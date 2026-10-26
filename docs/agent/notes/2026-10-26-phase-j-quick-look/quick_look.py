"""WU-0048a (phase J, J3a): quick look at LPC contributions to allocation.

PROTOTYPE, DEVELOPMENT (DEV-2), old code c9bb981: not a hypothesis test.

Offline analysis of the DEV-2 full-preset state dumps (schema /2, test split
only, 1000 states in time order, 5 evaluation horizons). Allocation side
only. Experiments A (all 16 subsets of {R, O, I, N}: drop-one ratios and
Shapley shares), B (additive model against additive plus one pair) and D
(constant A2, separation formula, {R, O} learned, full profile), on the
oracle profile ``qn/oracle/x_test`` and, as a secondary column, on the
deployable profile ``core/profile`` (``(n, E, 4)``).

Method
------
* Hybrid MSE of a state for weight ``w`` on CP: ``V(w) = w^2 E_C +
  (1 - w)^2 E_P + 2 w (1 - w) C``, exact from the oracle moments.
  ``V* = min over [0, 1]``. Excess loss ``L(g) = mean_i [V_i(g_i) - V*_i]``.
  For the deployable profile the per-state term is averaged over the E draws.
* Cross-fitting: the 1000 test states are cut into 5 contiguous blocks in
  time order; each block is predicted by models fitted on the other four.
* Learner: ``analysis.qn_regressor`` (Q-N hyperparameters), target
  ``u = (E_P - C) / kappa`` with sample weight ``kappa = E_C + E_P - 2 C``,
  which is weighted least squares on the decision loss itself
  (``V(w) - V(w*) = kappa (w - u)^2 - kappa (w* - u)^2``). Predictions are
  clipped to [0, 1]; every clip is counted. States with
  ``kappa <= KAPPA_REL_TINY * (E_C + E_P)`` are left out of the fit (counted)
  and kept in the score.
* A2: the best constant weight on the training folds, in closed form
  ``clip(sum(E_P - C) / sum(kappa), 0, 1)``. It is also the empty subset.
* Gain share ``G(g) = [V(A2) - V(g)] / [V(A2) - V*] = 1 - L(g) / L(A2)``.
* Intervals: moving-block bootstrap over the test states (block 5, 2000
  resamples, 95%), out-of-fold predictions held fixed, one index set per
  system shared by every model, horizon and profile. Ratio readings by
  ``ablation.ratio_reading_reason``; failed resamples counted.

Run (CPU, 4 threads)::

    JAX_PLATFORMS=cpu OMP_NUM_THREADS=4 nice -n 19 \\
        <repo>/.venv/bin/python -I quick_look.py --out <dir>
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from itertools import combinations
from math import factorial
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))

from lpcstudy.ablation import ratio_reading_reason  # noqa: E402
from lpcstudy.analysis import qn_regressor  # noqa: E402
from lpcstudy.data import make_rng  # noqa: E402
from lpcstudy.statistics import (  # noqa: E402
    block_resample_indices,
    percentile_interval,
)

LABEL = "PROTOTYPE, DEVELOPMENT (DEV-2), old code c9bb981: not a hypothesis test"
DATA = Path(
    "/home/brianm/projects/physics/chaos/lpcstudy-wt/run/r1-c9bb981/runs/"
    "r5-gpu-dev2/full"
)
SYSTEMS = ("lorenz63", "rossler", "chua")
CONDITIONS = ("R", "O", "I", "N")
N_FOLDS = 5
N_RESAMPLES = 2000
BLOCK = 5
LEVEL = 0.95
KAPPA_REL_TINY = 1e-10
"""``kappa / (E_C + E_P)`` at or below which a state is left out of the fit.

By Cauchy-Schwarz ``|E_P - C| <= sqrt(E_P kappa)``, so for such a state V
varies over [0, 1] by at most about ``2 sqrt(E_P kappa)``: it carries no
information about the weight, and ``u`` is round-off. It stays in the score."""
SHAPLEY_TOL = 1e-12
IDENTITY_TOL = 1e-12

SUBSETS = tuple(
    s for size in range(5) for s in combinations(range(4), size)
)
PAIRS = tuple(combinations(range(4), 2))


def key(subset: tuple[int, ...]) -> str:
    """Letters of a subset, or ``none`` for the empty set."""
    return "".join(CONDITIONS[j] for j in subset) or "none"


def hybrid_v(w: np.ndarray, ec: np.ndarray, ep: np.ndarray, c: np.ndarray) -> np.ndarray:
    """Exact hybrid MSE ``w^2 E_C + (1 - w)^2 E_P + 2 w (1 - w) C``."""
    return w * w * ec + (1.0 - w) ** 2 * ep + 2.0 * w * (1.0 - w) * c


def optimal_v(ec: np.ndarray, ep: np.ndarray, c: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Minimum of V over [0, 1] and its argmin, per state.

    For ``kappa > 0`` V is convex and the minimizer is ``clip(u, 0, 1)``; the
    endpoints are compared as well, so the result is the minimum over [0, 1]
    for any sign of ``kappa``.
    """
    kappa = ec + ep - 2.0 * c
    pos = kappa > 0
    u = np.where(pos, (ep - c) / np.where(pos, kappa, 1.0), 0.0)
    cands = np.stack([np.zeros_like(u), np.ones_like(u), np.clip(u, 0.0, 1.0)])
    vals = hybrid_v(cands, ec, ep, c)
    vals[2, ~pos] = np.inf
    arg = np.argmin(vals, axis=0)
    return np.take_along_axis(vals, arg[None], 0)[0], np.take_along_axis(cands, arg[None], 0)[0]


def interaction_cst(pair: tuple[int, int] | None) -> list[list[int]]:
    """Singletons, with ``pair`` (if any) merged into one group."""
    if pair is None:
        return [[0], [1], [2], [3]]
    rest = [[j] for j in range(4) if j not in pair]
    return [list(pair), *rest]


class Learner:
    """Fits the Q-N regressor on u with weight kappa and counts clips."""

    def __init__(self, seed: int) -> None:
        self.seed = seed
        self.n_fits = 0
        self.seconds = 0.0

    def fit_predict(
        self,
        x_train: np.ndarray,
        u: np.ndarray,
        weight: np.ndarray,
        x_test: np.ndarray,
        cst: list[list[int]] | None,
    ) -> tuple[np.ndarray, int, int]:
        """Raw prediction clipped to [0, 1], with the counts below 0 and above 1."""
        t0 = time.perf_counter()
        model = qn_regressor(self.seed)
        if cst is not None:
            model.set_params(interaction_cst=cst)
        model.fit(x_train, u, sample_weight=weight)
        raw = model.predict(x_test)
        self.n_fits += 1
        self.seconds += time.perf_counter() - t0
        if not np.isfinite(raw).all():
            raise FloatingPointError("non-finite prediction")
        n_low, n_high = int((raw < 0).sum()), int((raw > 1).sum())
        return np.clip(raw, 0.0, 1.0), n_low, n_high


def load_system(system: str) -> dict:
    """Moments, profiles and checks of one system's dump."""
    z = np.load(DATA / "states" / f"{system}.npz")
    assert str(z["meta/seed_id"]) == "DEV-2", "only the DEV-2 dump is used"
    out = {
        "horizons": z["core/horizons"].astype(np.int64),
        "ec": z["core/E_C"].astype(np.float64),
        "ep": z["core/E_P"].astype(np.float64),
        "c": z["core/C"].astype(np.float64),
        "x_oracle": z["qn/oracle/x_test"].astype(np.float64),
        "x_deploy": z["core/profile"].astype(np.float64),
        "w_star_dump": z["core/w_star"].astype(np.float64),
        "steps_per_lt": int(z["meta/steps_per_lyapunov"]),
    }
    for name in ("ec", "ep", "c", "x_oracle", "x_deploy"):
        if not np.isfinite(out[name]).all():
            raise ValueError(f"{system}: non-finite entries in {name}")
    return out


def cross_fit(
    learner: Learner,
    x: np.ndarray,
    u: np.ndarray,
    kappa: np.ndarray,
    fit_ok: np.ndarray,
    folds: list[np.ndarray],
    cols: tuple[int, ...],
    cst: list[list[int]] | None,
) -> tuple[np.ndarray, int, int]:
    """Out-of-fold weights for a profile ``x`` of shape ``(n, 4)`` or ``(n, E, 4)``.

    Deployable rows are (state, draw) pairs; a state's u and kappa are
    repeated over its draws.
    """
    n = x.shape[0]
    draws = 1 if x.ndim == 2 else x.shape[1]
    xs = x.reshape(n, draws, 4)[:, :, list(cols)]
    w_hat = np.empty((n, draws))
    n_low = n_high = 0
    for test in folds:
        train = np.setdiff1d(np.arange(n), test)
        train = train[fit_ok[train]]
        x_tr = xs[train].reshape(-1, len(cols))
        u_tr = np.repeat(u[train], draws)
        k_tr = np.repeat(kappa[train], draws)
        pred, lo, hi = learner.fit_predict(
            x_tr, u_tr, k_tr, xs[test].reshape(-1, len(cols)), cst
        )
        w_hat[test] = pred.reshape(len(test), draws)
        n_low += lo
        n_high += hi
    return w_hat, n_low, n_high


def a2_weights(ec, ep, c, folds) -> tuple[np.ndarray, list[float]]:
    """Per-state A2 weight: the best constant on the training folds."""
    n = len(ec)
    w = np.empty(n)
    consts = []
    for test in folds:
        train = np.setdiff1d(np.arange(n), test)
        num = (ep[train] - c[train]).sum()
        den = (ec[train] + ep[train] - 2.0 * c[train]).sum()
        if not den > 0:
            raise ValueError("non-positive pooled curvature")
        const = float(np.clip(num / den, 0.0, 1.0))
        w[test] = const
        consts.append(const)
    return w, consts


def interval(values: np.ndarray, point: float) -> dict:
    """Percentile interval of one bootstrap column, with its failure count."""
    lower, upper, n_failed = percentile_interval(values, LEVEL)
    return {"est": float(point), "ci": [lower, upper], "n_failed": n_failed}


def ratio_row(num: np.ndarray, den: np.ndarray, idx: np.ndarray, n: int) -> dict:
    """``mean(num) / mean(den)``, paired interval and reading."""
    with np.errstate(divide="ignore", invalid="ignore"):
        boot = num[idx].mean(1) / den[idx].mean(1)
    row = interval(boot, num.mean() / den.mean())
    reading, reason = ratio_reading_reason(row["ci"][0], row["ci"][1], n)
    row["reading"] = reading
    row["reason"] = reason
    return row


def shapley(loss: dict) -> np.ndarray:
    """Shapley values phi_X of the loss reduction, X in R, O, I, N.

    ``phi_X = sum_{S not containing X} |S|! (3 - |S|)! / 4! [L(S) - L(S + X)]``,
    so that ``sum phi = L(none) - L(ROIN)``. The losses may be floats or
    arrays of bootstrap values (the result then has a leading axis of 4).
    """
    phi = []
    for j in range(4):
        total = 0.0
        for s in SUBSETS:
            if j in s:
                continue
            weight = factorial(len(s)) * factorial(3 - len(s)) / factorial(4)
            with_j = tuple(sorted((*s, j)))
            total = total + weight * (loss[key(s)] - loss[key(with_j)])
        phi.append(total)
    return np.array(phi)


def analyse_horizon(
    learner: Learner,
    d: dict,
    h: int,
    x: np.ndarray,
    folds: list[np.ndarray],
    idx: np.ndarray,
    with_pairs: bool,
) -> dict:
    """Experiments A, B and D at one horizon for one profile."""
    ec, ep, c = d["ec"][:, h], d["ep"][:, h], d["c"][:, h]
    n = len(ec)
    kappa = ec + ep - 2.0 * c
    fit_ok = kappa > KAPPA_REL_TINY * (ec + ep)
    u = np.where(fit_ok, (ep - c) / np.where(fit_ok, kappa, 1.0), 0.0)
    v_star, w_star = optimal_v(ec, ep, c)

    # Independent checks: w* against the run's own clipped oracle weight, and
    # the kappa form of the excess loss against V(w) - V(w*) directly.
    w_dump = d["w_star_dump"][:, h]
    checks = {
        "w_star_vs_dump_max_abs": float(np.abs(w_star - w_dump).max()),
    }
    w_test = np.linspace(0.0, 1.0, 11)[:, None]
    direct = hybrid_v(w_test, ec, ep, c) - v_star
    kform = kappa * (w_test - u) ** 2 - kappa * (w_star - u) ** 2
    scale = np.maximum(np.abs(direct), ec + ep)
    checks["kappa_form_max_rel"] = float((np.abs(direct - kform) / scale).max())
    if checks["kappa_form_max_rel"] > IDENTITY_TOL:
        raise AssertionError(f"kappa form: {checks['kappa_form_max_rel']}")

    def excess(w_hat: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        w2 = w_hat.reshape(n, -1)
        v = hybrid_v(w2, ec[:, None], ep[:, None], c[:, None]).mean(1)
        return v - v_star, v

    models: dict[str, dict] = {}
    clips: dict[str, list[int]] = {}

    w_a2, consts = a2_weights(ec, ep, c, folds)
    models["none"] = dict(zip(("loss", "mse"), excess(w_a2)))
    rr = x[..., 0] - x[..., 1]
    w_sep = 1.0 / (1.0 + np.exp(2.0 * rr))
    models["sep"] = dict(zip(("loss", "mse"), excess(w_sep)))
    for s in SUBSETS[1:]:
        w_hat, lo, hi = cross_fit(learner, x, u, kappa, fit_ok, folds, s, None)
        models[key(s)] = dict(zip(("loss", "mse"), excess(w_hat)))
        clips[key(s)] = [lo, hi]
    if with_pairs:
        for pair in (None, *PAIRS):
            name = "add" if pair is None else "add+" + key(pair)
            w_hat, lo, hi = cross_fit(
                learner, x, u, kappa, fit_ok, folds, (0, 1, 2, 3),
                interaction_cst(pair),
            )
            models[name] = dict(zip(("loss", "mse"), excess(w_hat)))
            clips[name] = [lo, hi]

    neg = {m: int((v["loss"] < 0).sum()) for m, v in models.items()}
    min_excess = min(float(v["loss"].min()) for v in models.values())
    loss_pt = {m: float(v["loss"].mean()) for m, v in models.items()}
    full = models["ROIN"]

    # A: drop-one ratios (excess and MSE) and Shapley shares.
    drop_one = {}
    for j, name in enumerate(CONDITIONS):
        rest = key(tuple(i for i in range(4) if i != j))
        drop_one[name] = {
            "subset": rest,
            "loss_ratio": ratio_row(models[rest]["loss"], full["loss"], idx, n),
            "mse_ratio": ratio_row(models[rest]["mse"], full["mse"], idx, n),
        }
    phi = shapley(loss_pt)
    total = loss_pt["none"] - loss_pt["ROIN"]
    residual = float(phi.sum() - total)
    if abs(residual) > SHAPLEY_TOL:
        raise AssertionError(f"Shapley identity residual {residual}")
    boot_loss = {m: v["loss"][idx].mean(1) for m, v in models.items()}
    boot_phi = shapley(boot_loss)  # linear in the losses: (4, B)
    boot_total = boot_loss["none"] - boot_loss["ROIN"]
    shap = {}
    for j, name in enumerate(CONDITIONS):
        with np.errstate(divide="ignore", invalid="ignore"):
            share_boot = boot_phi[j] / boot_total
            g_part_boot = boot_phi[j] / boot_loss["none"]
        # "share": phi / (L(none) - L(full)), meaningless when that total is
        # near 0 or negative. "gain_part": phi / L(A2), the Shapley part of
        # the gain share; the four parts sum to G(full).
        shap[name] = {
            "phi": interval(boot_phi[j], phi[j]),
            "share": interval(share_boot, phi[j] / total),
            "gain_part": interval(g_part_boot, phi[j] / loss_pt["none"]),
        }

    # Gain share of every model: G = 1 - L / L(A2).
    gain = {}
    for m in models:
        with np.errstate(divide="ignore", invalid="ignore"):
            g_boot = 1.0 - boot_loss[m] / boot_loss["none"]
        gain[m] = interval(g_boot, 1.0 - loss_pt[m] / loss_pt["none"])

    # B: additive vs additive + one pair.
    pairs = {}
    if with_pairs:
        add = models["add"]["loss"]
        for pair in PAIRS:
            name = "add+" + key(pair)
            diff = add - models[name]["loss"]
            pairs[key(pair)] = {
                "delta": interval(diff[idx].mean(1), diff.mean()),
                "ratio": ratio_row(add, models[name]["loss"], idx, n),
            }
        ceil = add - full["loss"]
        pairs["ceiling_add_minus_full"] = interval(ceil[idx].mean(1), ceil.mean())
        pairs["ratio_add_over_full"] = ratio_row(add, full["loss"], idx, n)

    # D: ladder A2 -> separation formula -> {R, O} learned -> full.
    ladder = {}
    rungs = ("none", "sep", "RO", "ROIN")
    for i, m in enumerate(rungs):
        ladder[m] = {
            "loss": loss_pt[m],
            "gain_share": gain[m],
            "ratio_vs_full": ratio_row(models[m]["loss"], full["loss"], idx, n),
        }
        if i > 0:
            prev = rungs[i - 1]
            ladder[m]["ratio_prev_over_this"] = ratio_row(
                models[prev]["loss"], models[m]["loss"], idx, n
            )

    return {
        "horizon_steps": int(d["horizons"][h]),
        "horizon_lt": float(d["horizons"][h] / d["steps_per_lt"]),
        "n_states": n,
        "n_fit_excluded_kappa": int((~fit_ok).sum()),
        "n_w_star_at_0": int((w_star == 0).sum()),
        "n_w_star_at_1": int((w_star == 1).sum()),
        "a2_constants": consts,
        "loss": loss_pt,
        "mse": {m: float(v["mse"].mean()) for m, v in models.items()},
        "v_star_mean": float(v_star.mean()),
        "clips_low_high": clips,
        "n_negative_excess": neg,
        "min_excess": min_excess,
        "checks": checks,
        "shapley_residual": residual,
        "drop_one": drop_one,
        "shapley": shap,
        "gain_share": gain,
        "pairs": pairs,
        "ladder": ladder,
    }


def lag1(a: np.ndarray) -> float:
    """Lag-1 autocorrelation in time order."""
    a = a - a.mean()
    return float((a[:-1] * a[1:]).sum() / (a * a).sum())


SHORT = {
    "lowers": "lowers",
    "negligible": "negl.",
    "small": "small",
    "substantial": "SUBST.",
    "needed, size not determined": "needed",
    "undetermined": "undet.",
}


def fmt_ratio(row: dict) -> str:
    """``1.23 [1.10, 1.40] SUBST.``"""
    lo, hi = row["ci"]
    fail = f" ({row['n_failed']} failed)" if row["n_failed"] else ""
    return (f"{row['est']:.3f} [{lo:.3f}, {hi:.3f}] "
            f"{SHORT.get(row['reading'], row['reading'])}{fail}")


def fmt_est(row: dict, digits: int = 2) -> str:
    """``0.42 [0.30, 0.55]``"""
    lo, hi = row["ci"]
    fail = f" ({row['n_failed']} failed)" if row["n_failed"] else ""
    return f"{row['est']:.{digits}f} [{lo:.{digits}f}, {hi:.{digits}f}]{fail}"


def render(out: dict, keep: tuple[str, ...] | None = None) -> str:
    """Markdown tables of every system and profile, at the horizon positions
    ``keep`` (default all)."""
    lines = [f"# WU-0048a quick-look tables\n\n**{out['label']}.**\n",
             f"Data: `{out['data']}` (run commit {out['run_commit']}). "
             f"{out['n_fits']} fits, {out['wall_seconds']:.0f} s.\n",
             "Ratios: estimate [95% moving-block interval] reading "
             "(`ablation.ratio_reading`, margin 1.05). Orientation: "
             "simpler / richer, so > 1 means the richer model is better.\n"]
    for system, s in out["systems"].items():
        lines.append(f"\n## {system}\n")
        lag = s["lag1_autocorr_href"]
        lines.append("Lag-1 autocorrelation at H_ref (time order): " + ", ".join(
            f"{k} {v:.3f}" for k, v in lag.items()) + ".\n")
        for prof in ("oracle", "deployable"):
            res = s[prof]
            if not res:
                continue
            hs = [h for h in res if keep is None or h in keep]
            head = "| | " + " | ".join(
                f"{res[h]['horizon_steps']} st. ({res[h]['horizon_lt']:.2f} LT)" for h in hs) + " |"
            sep = "|---" * (len(hs) + 1) + "|"
            lines.append(f"\n### {system}, {prof} profile\n")
            lines.append(f"*{out['label']}.*\n")

            def table(title, rows):
                lines.append(f"\n**{title}**\n\n{head}\n{sep}")
                for name, fn in rows:
                    lines.append(f"| {name} | " + " | ".join(
                        fn(res[h]) for h in hs) + " |")

            table("Basics", [
                ("L(A2)", lambda r: f"{r['loss']['none']:.3g}"),
                ("L(full)", lambda r: f"{r['loss']['ROIN']:.3g}"),
                ("mean V*", lambda r: f"{r['v_star_mean']:.3g}"),
                ("w* = 0 / w* = 1", lambda r:
                    f"{r['n_w_star_at_0']} / {r['n_w_star_at_1']}"),
                ("full: clipped low / high", lambda r:
                    "{} / {}".format(*r["clips_low_high"]["ROIN"])),
                ("kappa excluded from fit", lambda r:
                    str(r["n_fit_excluded_kappa"])),
                ("negative excess entries (all models)", lambda r:
                    str(sum(r["n_negative_excess"].values()))),
            ])
            table("A: drop-one, L(F minus X) / L(F) (excess loss)", [
                (c, lambda r, c=c: fmt_ratio(r["drop_one"][c]["loss_ratio"]))
                for c in CONDITIONS])
            table("A: drop-one, MSE(F minus X) / MSE(F)", [
                (c, lambda r, c=c: fmt_ratio(r["drop_one"][c]["mse_ratio"]))
                for c in CONDITIONS])
            table("A: Shapley part of G(F), phi_X / L(A2) (sums to G(F))", [
                *[(c, lambda r, c=c: fmt_est(r["shapley"][c]["gain_part"]))
                  for c in CONDITIONS],
                ("G(F)", lambda r: fmt_est(r["gain_share"]["ROIN"])),
                ("Shapley identity residual", lambda r:
                    f"{r['shapley_residual']:.1e}"),
            ])
            table("A: gain share G by subset", [
                (m, lambda r, m=m: fmt_est(r["gain_share"][m]))
                for m in (key(sb) for sb in SUBSETS[1:])])
            if res[hs[0]]["pairs"]:
                table("B: L(additive) / L(additive + pair)", [
                    *[(key(p), lambda r, p=p: fmt_ratio(
                        r["pairs"][key(p)]["ratio"])) for p in PAIRS],
                    ("ceiling L(add) / L(F)", lambda r: fmt_ratio(
                        r["pairs"]["ratio_add_over_full"])),
                    ("G(additive)", lambda r: fmt_est(r["gain_share"]["add"])),
                ])
            table("D: ladder, gain share G", [
                (m, lambda r, m=m: fmt_est(r["ladder"][m]["gain_share"]))
                for m in ("none", "sep", "RO", "ROIN")])
            table("D: ladder, L(rung) / L(F)", [
                (m, lambda r, m=m: fmt_ratio(r["ladder"][m]["ratio_vs_full"]))
                for m in ("none", "sep", "RO")])
            table("D: ladder, L(rung below) / L(rung)", [
                (m, lambda r, m=m: fmt_ratio(
                    r["ladder"][m]["ratio_prev_over_this"]))
                for m in ("sep", "RO", "ROIN")])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--render-only", action="store_true",
                        help="rewrite tables.md from an existing quick_look.json")
    parser.add_argument("--systems", nargs="+", default=list(SYSTEMS))
    parser.add_argument("--horizons", nargs="+", type=int, default=None,
                        help="horizon positions (default: all)")
    parser.add_argument("--no-deployable", action="store_true")
    parser.add_argument("--deployable-pairs", action="store_true",
                        help="also run experiment B on the deployable profile")
    args = parser.parse_args()
    if args.render_only:
        out = json.loads((args.out / "quick_look.json").read_text())
        (args.out / "tables.md").write_text(render(out))
        (args.out / "tables_key.md").write_text(render(out, ("0", "2", "4")))
        return

    results = json.loads((DATA / "results.json").read_text())
    seed = int(results["config"]["seed"])
    if results["config"]["seed_id"] != "DEV-2":
        raise ValueError("only the DEV-2 run is used")
    learner = Learner(seed)
    out: dict = {
        "label": LABEL,
        "data": str(DATA),
        "run_commit": results["provenance"]["commit"],
        "settings": {
            "n_folds": N_FOLDS, "n_resamples": N_RESAMPLES, "block": BLOCK,
            "level": LEVEL, "kappa_rel_tiny": KAPPA_REL_TINY,
            "learner": repr(qn_regressor(seed)),
        },
        "systems": {},
    }
    t_start = time.perf_counter()
    for system in args.systems:
        d = load_system(system)
        n = d["ec"].shape[0]
        folds = np.array_split(np.arange(n), N_FOLDS)
        idx = np.stack(list(block_resample_indices(
            n, N_RESAMPLES, BLOCK, make_rng(seed, "wu0048a-quick-look", system)
        )))
        h_list = args.horizons or list(range(len(d["horizons"])))
        ref = d["horizons"].tolist().index(d["steps_per_lt"])
        kappa_ref = d["ec"][:, ref] + d["ep"][:, ref] - 2 * d["c"][:, ref]
        u_ref = (d["ep"][:, ref] - d["c"][:, ref]) / kappa_ref
        sys_out = {
            "lag1_autocorr_href": {
                "u": lag1(u_ref),
                "w_star": lag1(d["w_star_dump"][:, ref]),
                **{c: lag1(d["x_oracle"][:, j]) for j, c in enumerate(CONDITIONS)},
            },
            "oracle": {}, "deployable": {},
        }
        for h in h_list:
            print(f"[{time.perf_counter() - t_start:7.1f}s] {system} h={h} oracle",
                  flush=True)
            sys_out["oracle"][str(h)] = analyse_horizon(
                learner, d, h, d["x_oracle"], folds, idx, True
            )
            if not args.no_deployable:
                print(f"[{time.perf_counter() - t_start:7.1f}s] {system} h={h} "
                      "deployable", flush=True)
                sys_out["deployable"][str(h)] = analyse_horizon(
                    learner, d, h, d["x_deploy"], folds, idx,
                    args.deployable_pairs,
                )
        out["systems"][system] = sys_out
    out["n_fits"] = learner.n_fits
    out["fit_seconds"] = learner.seconds
    out["wall_seconds"] = time.perf_counter() - t_start
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "quick_look.json").write_text(json.dumps(out, indent=1))
    (args.out / "tables.md").write_text(render(out))
    (args.out / "tables_key.md").write_text(render(out, ("0", "2", "4")))
    print(f"done: {learner.n_fits} fits, {out['wall_seconds']:.0f} s", flush=True)


if __name__ == "__main__":
    main()
