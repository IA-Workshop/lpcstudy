"""WU-0045 (phase J, J0): numerical checks behind the M-1 to M-8 decisions.

DEVELOPMENT (DEV-2): exploratory, not a hypothesis test. Prototype numbers on
old code c9bb981 (the R5 DEV-2 full dumps, test split only). Nothing here is
compared with, or placed beside, CONF-1.

Parts (each prints a markdown table):

* ``m2``  curvature kappa and unclipped minimizer u per horizon; the effect of
  the sample-weight scale in HistGradientBoosting; a cross-fitted comparison
  of fitting targets (5 contiguous folds of the test split, oracle profile).
* ``m8``  the WU-0036 V(w) substitution check applied to the stored learned
  rules A3 and A5 at H_ref (direct and paired with A1), and the spread of each
  rule's weight over the evaluation draws.
* ``m45`` the horizon target T: censoring, ties, the zero-parameter Lyapunov
  baseline T0, and Harrell's C (vectorized, checked against a brute-force
  count).
* ``m6``  the binomial error rates of the replication rules, and the per-seed
  false-claim probability when between-seed variation is omitted from the interval.
* ``mc``  the oracle Monte Carlo bias of the excess, ``kappa (w*_A - w*_B)^2 / 4``, against
  the excess of the constant rule; the failed-resample thresholds at the planned levels.

Usage (CPU, one thread)::

    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 nice -n 19 \
        /path/to/.venv/bin/python -I phase_j_checks.py > phase_j_checks.out.md
"""

from __future__ import annotations

import pathlib
import sys
from math import comb

import numpy as np
from scipy.stats import norm
from sklearn.ensemble import HistGradientBoostingRegressor

REPO_ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from lpcstudy.data import make_rng  # noqa: E402
from lpcstudy.seeds import REGISTRY_PATH, load_registry, resolve_dev_seed  # noqa: E402
from lpcstudy.statistics import bootstrap_values  # noqa: E402

LABEL = "DEVELOPMENT (DEV-2): exploratory, not a hypothesis test; prototype, old code c9bb981"
RUN = pathlib.Path(
    "/home/brianm/projects/physics/chaos/lpcstudy-wt/run/r1-c9bb981/runs/r5-gpu-dev2/full"
)
SYSTEMS = ("lorenz63", "rossler", "chua")
RHO = 0.01
THETA = 0.2
H_MAX = 240
STEPS_PER_LT = 30
M_DIM = 3  # latent dimension of the three core systems (v3 horizon law, sqrt(m))
FOLDS = 5


def load(system: str) -> dict:
    """Read one DEV-2 dump (test split) and check it is a development seed."""
    z = np.load(RUN / "states" / f"{system}.npz")
    seed_id = str(z["meta/seed_id"])
    assert seed_id == "DEV-2", seed_id
    return {k: z[k] for k in z.files}


def regressor(seed: int, **extra) -> HistGradientBoostingRegressor:
    """The Q-N regressor's hyperparameters (analysis.qn_regressor), seed fixed per call."""
    return HistGradientBoostingRegressor(
        max_iter=300,
        learning_rate=0.05,
        max_leaf_nodes=15,
        min_samples_leaf=20,
        l2_regularization=1.0,
        early_stopping=False,
        random_state=seed % 2**31,
        **extra,
    )


def quad(EC, EP, C, w):
    """V(w) = w^2 E_C + (1-w)^2 E_P + 2 w (1-w) C (broadcasting)."""
    return w**2 * EC + (1 - w) ** 2 * EP + 2 * w * (1 - w) * C


# ----------------------------------------------------------------------- M-2
def part_m2(seed: int) -> None:
    print(f"## M-2: curvature, unclipped minimizer, fitting target\n\n{LABEL}\n")
    print("| system | H | min kappa/rho^2 | median kappa/rho^2 | n_eff(kappa) | "
          "top-1% share of sum kappa | share u<0 (w*=0) | share u>1 (w*=1) | "
          "max abs u | n_eff(A2 excess) | median E_C / median E_P | median C / sqrt(E_C E_P) |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for s in SYSTEMS:
        z = load(s)
        EC, EP, C = z["core/E_C"], z["core/E_P"], z["core/C"]
        for h, H in enumerate(z["core/horizons"]):
            k = EC[:, h] + EP[:, h] - 2 * C[:, h]
            u = (EP[:, h] - C[:, h]) / k
            top = np.sort(k)[::-1][: len(k) // 100].sum() / k.sum()
            wbar = np.clip(np.sum(k * u) / k.sum(), 0, 1)
            ex = k * ((wbar - u) ** 2 - (np.clip(u, 0, 1) - u) ** 2)
            print(f"| {s} | {H} | {k.min() / RHO**2:.3f} | {np.median(k) / RHO**2:.1f} | "
                  f"{k.sum() ** 2 / np.sum(k**2):.1f} | {top:.2f} | {np.mean(u < 0):.3f} | "
                  f"{np.mean(u > 1):.3f} | {np.abs(u).max():.2f} | "
                  f"{ex.sum() ** 2 / np.sum(ex**2):.1f} | "
                  f"{np.median(EC[:, h]) / np.median(EP[:, h]):.2f} | "
                  f"{np.median(C[:, h] / np.sqrt(EC[:, h] * EP[:, h])):.2f} |")
    print()

    # weight scale: HGB leaf value = -sum g / (sum h + l2), h = sample weight
    rng = make_rng(seed, "wu0045", "weight-scale")
    x = rng.normal(size=(3000, 2))
    y = np.sin(2 * x[:, 0]) + 0.1 * rng.normal(size=3000)
    print("Sample-weight scale with l2_regularization = 1 (synthetic, in-sample R^2):\n")
    print("| weight scale | R^2 |")
    print("|---|---|")
    for scale in (1.0, 1e-2, 1e-3, 1e-4):
        p = regressor(seed).fit(x, y, sample_weight=np.full(3000, scale)).predict(x)
        print(f"| {scale:g} | {1 - np.mean((p - y) ** 2) / np.var(y):.4f} |")
    print()

    print("Cross-fitted targets (5 contiguous folds of 200 test states; oracle profile; "
          "train 800 states). L_A = mean excess MSE V(g) - V(w*), as a ratio to the "
          "kappa-weighted constant; L_w = mean of (g-u)^2 - (w*-u)^2 (kappa = 1), as a ratio "
          "to the unweighted constant.\n")
    print("| system | H | rule | L_A ratio | L_w ratio |")
    print("|---|---|---|---|---|")
    for s in SYSTEMS:
        z = load(s)
        X = z["qn/oracle/x_test"]
        assert np.allclose(X[:, 2], STEPS_PER_LT * z["core/Lambda_bar"], rtol=1e-12, atol=0)
        n = len(X)
        folds = np.array_split(np.arange(n), FOLDS)
        for h in (0, 2, 4):
            EC, EP, C = (z[f"core/{q}"][:, h] for q in ("E_C", "E_P", "C"))
            k = EC + EP - 2 * C
            u = (EP - C) / k
            ws = np.clip(u, 0, 1)
            preds: dict[str, np.ndarray] = {r: np.empty(n) for r in (
                "const kappa", "const unit", "u, kappa/mean", "u, raw kappa", "u, unit",
                "w*, unit", "two-part logit", "separation formula")}
            for f, te in enumerate(folds):
                tr = np.setdiff1d(np.arange(n), te)
                kn = k[tr] / k[tr].mean()
                preds["const kappa"][te] = np.sum(k[tr] * u[tr]) / k[tr].sum()
                preds["const unit"][te] = u[tr].mean()
                preds["u, kappa/mean"][te] = regressor(seed + f).fit(
                    X[tr], u[tr], sample_weight=kn).predict(X[te])
                preds["u, raw kappa"][te] = regressor(seed + f).fit(
                    X[tr], u[tr], sample_weight=k[tr]).predict(X[te])
                preds["u, unit"][te] = regressor(seed + f).fit(X[tr], u[tr]).predict(X[te])
                preds["w*, unit"][te] = regressor(seed + f).fit(X[tr], ws[tr]).predict(X[te])
                inner = (ws[tr] > 0) & (ws[tr] < 1)
                lg = regressor(seed + f).fit(
                    X[tr][inner], np.log(ws[tr][inner] / (1 - ws[tr][inner]))).predict(X[te])
                p0 = np.clip(regressor(seed + f).fit(
                    X[tr], (ws[tr] == 0).astype(float)).predict(X[te]), 0, 1)
                preds["two-part logit"][te] = (1 - p0) / (1 + np.exp(-lg))
                preds["separation formula"][te] = 1 / (1 + np.exp(2 * (X[te, 0] - X[te, 1])))
            excess = {r: k * ((np.clip(g, 0, 1) - u) ** 2 - (ws - u) ** 2)
                      for r, g in preds.items()}
            wloss = {r: (np.clip(g, 0, 1) - u) ** 2 - (ws - u) ** 2 for r, g in preds.items()}
            for r in preds:
                print(f"| {s} | {z['core/horizons'][h]} | {r} | "
                      f"{excess[r].mean() / excess['const kappa'].mean():.3f} | "
                      f"{wloss[r].mean() / wloss['const unit'].mean():.3f} |")
    print()


# ----------------------------------------------------------------------- M-8
def part_m8(seed: int) -> None:
    print(f"## M-8: V(w) substitution for learned, draw-dependent weights at H_ref\n\n{LABEL}\n")
    print("WU-0036 construction: D_i = S_i - mean_j V_i(w_ij); SE from the half-draw moments; "
          "paired rows subtract A1 (w = 0). Rule of WU-0036: |z| <= 4.\n")
    print("| system | rule | mean draw-SD of w | mean w | rel D (direct) | z (direct) | "
          "rel D (paired) | z (paired) | rel tol (paired) |")
    print("|---|---|---|---|---|---|---|---|---|")
    for s in SYSTEMS:
        z = load(s)
        ref = int(z["core/ref_index"])
        EC, EP, C = (z[f"core/{q}"][:, ref][:, None] for q in ("E_C", "E_P", "C"))
        half = {hh: tuple(z[f"core/{q}_{hh}"][:, ref][:, None] for q in ("E_C", "E_P", "C"))
                for hh in "AB"}
        mA, mB = (int(v) for v in z["core/half_n_draws"])
        inv = 1 / mA + 1 / mB
        E, M = int(z["meta/n_eval_draws"]), int(z["meta/n_oracle_draws"])
        n = EC.shape[0]
        for rule in ("A4", "A3", "A5"):
            w = z[f"core/weight_href/{rule}"]
            zero = np.zeros_like(w)
            row = [f"| {s} | {rule} | {np.mean(w.std(axis=1, ddof=1)):.4f} | {w.mean():.3f}"]
            for paired in (False, True):
                def q(mom, ww=w):
                    out = quad(*mom, ww)
                    return out - quad(*mom, zero) if paired else out
                qa, qb = q(half["A"]), q(half["B"])
                var_d = ((qa - qb) ** 2 / inv).sum(axis=1) / E**2 + \
                    (qa.mean(axis=1) - qb.mean(axis=1)) ** 2 / inv / M
                se = np.sqrt(var_d.sum()) / n
                S = z[f"core/state_mse/{rule}"][:, ref]
                if paired:
                    S = S - z["core/state_mse/A1"][:, ref]
                D = S - q((EC, EP, C)).mean(axis=1)
                scale = quad(EC, EP, C, w).mean()
                row.append(f"{D.mean() / scale:+.3f} | {D.mean() / se:+.2f}")
                if paired:
                    row.append(f"{4 * se / scale:.3f}")
            print(" | ".join(row) + " |")
    print()
    print("Draw dependence of the deployable profile: within-state SD over the E draws divided by "
          "the total SD, per coordinate (0 = a function of the state only; 1 = all draw noise).\n")
    print("| system | R_hat | O_hat | I_hat | N_hat |")
    print("|---|---|---|---|---|")
    for s in SYSTEMS:
        prof = load(s)["core/profile"]
        within = np.sqrt(np.mean(prof.var(axis=1, ddof=1), axis=0))
        total = prof.reshape(-1, prof.shape[-1]).std(axis=0, ddof=1)
        print(f"| {s} | " + " | ".join(f"{v:.2f}" for v in within / total) + " |")
    print()


# ---------------------------------------------------------------------- M-4/5
def harrell_c(time: np.ndarray, event: np.ndarray, pred: np.ndarray) -> tuple[float, int]:
    """Harrell's C with a fixed censoring time: higher ``pred`` = longer horizon.

    A pair (i, j) is comparable iff time_i < time_j and event_i, or time_i == time_j with
    event_i and not event_j (censored at H_max lies beyond an event at H_max). Tied times of
    two events and pairs of censored states are not comparable. Tied predictions count 1/2.
    """
    ti, tj = time[:, None], time[None, :]
    ei, ej = event[:, None], event[None, :]
    comp = ei & ((ti < tj) | ((ti == tj) & ~ej))
    pi, pj = pred[:, None], pred[None, :]
    score = np.where(pi < pj, 1.0, np.where(pi == pj, 0.5, 0.0))
    return float(score[comp].sum() / comp.sum()), int(comp.sum())


def harrell_c_brute(time, event, pred) -> float:
    """Brute-force double loop of the same rule (reference for the vectorized form)."""
    num = den = 0.0
    for i in range(len(time)):
        for j in range(len(time)):
            if not event[i]:
                continue
            if time[i] < time[j] or (time[i] == time[j] and not event[j]):
                den += 1
                num += 1.0 if pred[i] < pred[j] else (0.5 if pred[i] == pred[j] else 0.0)
    return num / den


def softmin(r: np.ndarray, o: np.ndarray) -> np.ndarray:
    """ln(e0/rho) of the separation-optimal blend: -1/2 ln(e^{-2R} + e^{-2O})."""
    return -0.5 * np.logaddexp(-2 * r, -2 * o)


def part_m45() -> None:
    print(f"## M-4, M-5: horizon target, ties, Lyapunov baseline, Harrell's C\n\n{LABEL}\n")
    print("T = oracle-hybrid characteristic horizon at theta = 0.2 (steps), stored as log T; "
          "T = 240 is treated as censored (the dump has no event flag). T0 = (30 / I) ln(theta "
          "sqrt(3) / (rho e^s)), s = softmin(R, O); I <= 0 or T0 > 240 gives 240, T0 < 1 gives "
          "1 (counted).\n")
    print("| system | n censored | distinct T | largest atom | n I<=0 | n T0 clipped | "
          "median ln(T/T0) | IQR ln(T/T0) | C(T0) | C(1/I) | C(-s) | Spearman(T, T0) | "
          "H1c PLP median ratio |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for s in SYSTEMS:
        z = load(s)
        X = z["qn/oracle/x_test"]
        T = np.rint(np.exp(z["qn/oracle/log_t"])).astype(int)
        event = T < H_MAX
        _, counts = np.unique(T, return_counts=True)
        R, O, I = X[:, 0], X[:, 1], X[:, 2]
        lnratio = np.log(THETA * np.sqrt(M_DIM) / RHO) - softmin(R, O)
        with np.errstate(divide="ignore"):
            raw = np.where(I > 0, STEPS_PER_LT / np.where(I > 0, I, 1.0) * lnratio, np.inf)
        T0 = np.clip(raw, 1, H_MAX)
        n_clip = int(np.sum((raw < 1) | (raw > H_MAX)))
        lr = np.log(T / T0)[event]
        c0, _ = harrell_c(T, event, T0)
        c_i, _ = harrell_c(T, event, np.where(I > 0, 1 / np.where(I > 0, I, 1), np.inf))
        c_s, _ = harrell_c(T, event, -softmin(R, O))
        sub = slice(0, 150)
        assert abs(harrell_c(T[sub], event[sub], T0[sub])[0]
                   - harrell_c_brute(T[sub], event[sub], T0[sub])) < 1e-12
        rank = lambda v: np.argsort(np.argsort(v))  # noqa: E731
        sp = np.corrcoef(rank(T), rank(T0))[0, 1]
        h1c = z["h1c/PLP/ratio"][z["h1c/PLP/eligible"]]
        print(f"| {s} | {int((~event).sum())} | {len(counts)} | {counts.max() / len(T):.3f} | "
              f"{int(np.sum(I <= 0))} | {n_clip} | {np.median(lr):+.3f} | "
              f"{np.subtract(*np.percentile(lr, [75, 25])):.3f} | {c0:.3f} | {c_i:.3f} | "
              f"{c_s:.3f} | {sp:.3f} | {np.median(h1c):.3f} |")
    print("\nHarrell's C: vectorized form equals the brute-force count to 1e-12 on the first 150 "
          "states of each system (asserted).\n")
    print("Quartiles (25, 50, 75%) of T in LT, of L' = ln(theta sqrt(3) / (rho e^s)), and of the "
          "separation weight p = 1 / (1 + e^{2(R - O)}):\n")
    print("| system | T / LT | L' | p |")
    print("|---|---|---|---|")
    for s in SYSTEMS:
        z = load(s)
        X = z["qn/oracle/x_test"]
        T = np.exp(z["qn/oracle/log_t"]) / STEPS_PER_LT
        lp = np.log(THETA * np.sqrt(M_DIM) / RHO) - softmin(X[:, 0], X[:, 1])
        p = 1 / (1 + np.exp(2 * (X[:, 0] - X[:, 1])))
        q = [np.percentile(v, [25, 50, 75]) for v in (T, lp, p)]
        print(f"| {s} | " + " | ".join(", ".join(f"{x:.3g}" for x in v) for v in q) + " |")
    print()


# ----------------------------------------------------------------------- M-6
def part_m6() -> None:
    print("## M-6: replication rules, binomial error rates (5 independent seeds)\n")
    print("p = per-seed probability that a seed gives the reading. P(rule) = P(at least k of 5).\n")
    ps = (0.01, 0.025, 0.05, 0.063, 0.1, 0.2, 0.5, 0.7, 0.8, 0.9, 0.95)
    print("| p | " + " | ".join(f"{p:g}" for p in ps) + " |")
    print("|---|" + "---|" * len(ps))
    for k in (3, 4, 5):
        vals = [sum(comb(5, j) * p**j * (1 - p) ** (5 - j) for j in range(k, 6)) for p in ps]
        print(f"| >= {k} of 5 | " + " | ".join(f"{v:.2g}" for v in vals) + " |")
    print()
    print("Per-seed probability p of a false decisive bound claim at 95% when the interval omits "
          "a between-seed SD of r times the within-seed SE: p = Phi(-1.96 / sqrt(1 + r^2)).\n")
    print("| r | p | P(>= 3 of 5) | P(>= 4 of 5) |")
    print("|---|---|---|---|")
    for r in (0.0, 0.5, 0.8, 1.0, 1.5, 2.0):
        p = norm.sf(norm.isf(0.025) / np.sqrt(1 + r * r))
        tail = [sum(comb(5, j) * p**j * (1 - p) ** (5 - j) for j in range(k, 6)) for k in (3, 4)]
        print(f"| {r:g} | {p:.4f} | {tail[0]:.2g} | {tail[1]:.2g} |")
    print()


def part_mc() -> None:
    print(f"## Oracle Monte Carlo bias of the excess; failed-resample thresholds\n\n{LABEL}\n")
    print("bias_i = kappa_i (w*_A - w*_B)^2 / 4 (half-draw moments): the expected upward bias of "
          "every rule's estimated excess, because w* is estimated from the same moments.\n")
    print("| system | H | mean bias / mean excess of the constant rule | median half-width of w* |")
    print("|---|---|---|---|")
    for s in SYSTEMS:
        z = load(s)
        for h, H in enumerate(z["core/horizons"]):
            EC, EP, C = (z[f"core/{q}"][:, h] for q in ("E_C", "E_P", "C"))
            k = EC + EP - 2 * C
            u = (EP - C) / k
            const = np.clip(np.sum(k * u) / k.sum(), 0, 1)
            ex = k * ((const - u) ** 2 - (np.clip(u, 0, 1) - u) ** 2)
            dw = z["core/w_star_A"][:, h] - z["core/w_star_B"][:, h]
            print(f"| {s} | {H} | {np.mean(k * dw**2 / 4) / ex.mean():.4f} | "
                  f"{np.median(np.abs(dw)) / 2:.4f} |")
    print()
    print("| level | failures that make both bounds infinite (B = 2000) |")
    print("|---|---|")
    for level in (0.95, 1 - 0.05 / 3, 1 - 0.05 / 4, 1 - 0.05 / 6):
        print(f"| {level:.5f} | {int(np.floor(1999 * (1 - level) / 2)) + 1} |")
    print()


def main() -> None:
    seed = resolve_dev_seed("DEV-2", load_registry(REGISTRY_PATH))
    print(f"# WU-0045 checks\n\n{LABEL}\n")
    part_m2(seed)
    part_m8(seed)
    part_m45()
    part_m6()
    part_mc()


if __name__ == "__main__":
    main()
