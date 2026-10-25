"""WU-0036: A4 coefficient ablation, stage 1 (offline, existing per-state dumps).

DEVELOPMENT (DEV-1, DEV-2): not a hypothesis test.

Two stages, run in this order (the tolerance is fixed and recorded before the stored score is read):

``--stage tolerance``
    Reads only the deployable profile, R, the A4 weights and the oracle moments (full and halves).
    Reconstructs the A4 weight, runs the 1e-12 reconstruction checks, and computes the tolerance
    of the approximation check from the oracle half-draw moments. It never reads ``state_mse/``.

``--stage full``
    Repeats the above, then reads ``state_mse/<A4|A0|A1|A4o>`` at H_ref, runs the approximation
    check, and, only if every check passes, the four zero-coefficient variants with the paired
    moving-block bootstrap of the ratios against the unchanged A4.

Usage (CPU, one thread)::

    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 nice -n 19 \
        /path/to/.venv/bin/python3 -I a4_ablation.py --stage full

The A4 code is that of commit c9bb981 (identical in ``lpcstudy/`` to the run commits 01d9fc7 and
6f1a8c8): ``eps_hat^2 = a (R nu)^2 + b (rho nu)^2``, ``delta_hat^2 = a' (rho nu)^2 + b' rho^2``,
``nu = min(nu_hat, nu_cap)``, ``w = delta_hat^2 / max(eps_hat^2 + delta_hat^2, 1e-300)``.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np

REPO_ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from lpcstudy.data import make_rng  # noqa: E402
from lpcstudy.seeds import load_registry, resolve_dev_seed, REGISTRY_PATH  # noqa: E402
from lpcstudy.statistics import bootstrap_values, endpoint_mc_error, \
    percentile_interval  # noqa: E402

LABEL = "DEVELOPMENT (DEV-1, DEV-2): not a hypothesis test"
RUNS_ROOT = pathlib.Path("/home/brianm/projects/physics/chaos/lpcstudy-wt/run/r1-c9bb981/runs")
RUNS = {"DEV-1 pilot": RUNS_ROOT / "r1-gpu-dev1" / "pilot",
        "DEV-2 full": RUNS_ROOT / "r5-gpu-dev2" / "full"}
SYSTEMS = ("lorenz63", "rossler", "chua")
COEFS = ("a", "b", "a_prime", "b_prime")
RECON_TOL = 1e-12          # relative, fixed by the ROADMAP WU-0036 criterion
Z_TOL = 4.0                # approximation check: |mean D| <= Z_TOL * SE (fixed in the note, section 2)
BLOCK, RESAMPLES = 5, 2000
LEVEL = 1.0 - 0.05 / 3.0


def rel_err(x: np.ndarray, y: np.ndarray) -> float:
    """Max relative difference ``|x - y| / |y|`` (``y`` nonzero everywhere here)."""
    return float(np.max(np.abs(x - y) / np.abs(y)))


def a4_weight(R, nu, rho, a, b, ap, bp):
    """A4 weight by the package's code path (SeedProxy.predict then closed_form_weight)."""
    eps_hat = np.sqrt(a * (R * nu) ** 2 + b * np.square(rho * nu))
    delta_hat = np.sqrt(ap * (rho * nu) ** 2 + bp * np.square(np.full_like(nu, rho)))
    eps_sq, delta_sq = eps_hat ** 2, delta_hat ** 2
    return delta_sq / np.maximum(eps_sq + delta_sq, 1e-300)


def hand_weight(variant, R, nu, rho, a, b, ap, bp):
    """Simplified closed forms (rho^2 divided out; nu^2 cancelled where it cancels)."""
    x2 = (R / rho) ** 2
    n2 = nu ** 2
    if variant == "unchanged":
        return (ap * n2 + bp) / (n2 * (a * x2 + b) + ap * n2 + bp)
    if variant == "a":
        return (ap * n2 + bp) / (b * n2 + ap * n2 + bp)
    if variant == "b":
        return (ap * n2 + bp) / (a * x2 * n2 + ap * n2 + bp)
    if variant == "a_prime":
        return bp / (n2 * (a * x2 + b) + bp)
    if variant == "b_prime":
        return ap / (a * x2 + b + ap)
    raise ValueError(variant)


def quad(EC, EP, C, w):
    """V(w) = w^2 E_C + (1-w)^2 E_P + 2 w (1-w) C, moments (n,) broadcast over draws (n, E)."""
    EC, EP, C = EC[:, None], EP[:, None], C[:, None]
    return w ** 2 * EC + (1 - w) ** 2 * EP + 2 * w * (1 - w) * C


def excess(EC, EP, C, w):
    """V(w) - V(w*) in the form of oracle.excess_mse (c [(w-u)^2 - (w*-u)^2])."""
    curv = EC + EP - 2 * C
    u = (EP - C) / np.maximum(curv, 1e-300)
    opt = np.clip(u, 0.0, 1.0)
    return curv[:, None] * ((w - u[:, None]) ** 2 - (opt[:, None] - u[:, None]) ** 2)


def load(run_dir: pathlib.Path, system: str) -> dict:
    """Read a dump and its results.json; reconstruct nu and the A4 weight; run the 1e-12 checks."""
    z = np.load(run_dir / "states" / f"{system}.npz")
    res = json.loads((run_dir / "results.json").read_text())
    cfg = res["config"]
    fit = res["systems"][system]["fitted"]
    seed_id = str(z["meta/seed_id"])
    assert seed_id.startswith("DEV-") and seed_id == cfg["seed_id"] == res["provenance"]["seed_id"]
    seed = resolve_dev_seed(seed_id, load_registry(REGISTRY_PATH))
    assert seed == cfg["seed"]
    ref = int(z["core/ref_index"])
    assert int(z["core/horizons"][ref]) == int(z["meta/reference_horizon"]) == 30
    rho = float(cfg["core_noise"])
    a, b = fit["analog_proxy"]["slope"], fit["analog_proxy"]["floor"]
    ap, bp = fit["estimation_proxy"]["slope"], fit["estimation_proxy"]["floor"]
    cap = fit["nu_cap"]
    R = z["core/R"]
    prof = z["core/profile"]
    eps2 = rho ** 2 * np.exp(2 * prof[..., 0])
    del2 = rho ** 2 * np.exp(2 * prof[..., 1])
    nu2 = eps2 / (a * R ** 2 + b * rho ** 2)          # from the analog coordinate (no subtraction)
    nu = np.sqrt(nu2)
    checks = {}
    # independent consistency: the estimation coordinate from the same nu
    checks["delta_from_nu_rel"] = rel_err(ap * (rho * nu) ** 2 + bp * rho ** 2, del2)
    checks["nu_above_cap"] = int(np.sum(nu > cap * (1 + RECON_TOL)))
    checks["nu_at_cap"] = int(np.sum(np.abs(nu / cap - 1) <= 1e-9))
    w_stored = z["core/weight_href/A4"]
    w_code = a4_weight(R, nu, rho, a, b, ap, bp)
    checks["weight_vs_stored_rel"] = rel_err(w_code, w_stored)
    checks["weight_hand_vs_code_rel"] = rel_err(hand_weight("unchanged", R, nu, rho, a, b, ap, bp),
                                                w_code)
    checks["profile_weight_vs_stored_rel"] = rel_err(del2 / (eps2 + del2), w_stored)
    EC, EP, C = (z[f"core/{k}"][:, ref] for k in ("E_C", "E_P", "C"))
    curv = EC + EP - 2 * C
    wstar = np.clip((EP - C) / np.maximum(curv, 1e-300), 0, 1)
    checks["w_star_vs_stored_abs"] = float(np.max(np.abs(wstar - z["core/w_star"][:, ref])))
    for key in ("delta_from_nu_rel", "weight_vs_stored_rel", "weight_hand_vs_code_rel",
                "profile_weight_vs_stored_rel"):
        assert checks[key] <= RECON_TOL, (system, key, checks[key])
    assert checks["nu_above_cap"] == 0
    halves = {h: tuple(z[f"core/{k}_{h}"][:, ref] for k in ("E_C", "E_P", "C")) for h in "AB"}
    mA, mB = (int(x) for x in z["core/half_n_draws"])
    # columns 4, 5 of meta/draw_counters: error_clips_plp_href, error_clips_nonfinite_href
    assert list(z["meta/draw_counters"][4:6]) == ["error_clips_plp_href", "error_clips_nonfinite_href"]
    clips = z["handling/test/eval_handled"][:, [4, 5]].sum(axis=0).tolist()
    return dict(z=z, seed=seed, ref=ref, rho=rho, coef=dict(a=a, b=b, a_prime=ap, b_prime=bp),
                cap=cap, R=R, nu=nu, w0=w_code, w_stored=w_stored, EC=EC, EP=EP, C=C,
                halves=halves, mA=mA, mB=mB, M=int(z["meta/n_oracle_draws"]),
                E=int(z["meta/n_eval_draws"]), n=R.shape[0], checks=checks,
                eval_clips_href_plp_nonfinite=clips,
                oracle_clips_href_plp_nonfinite=z["handling/test/oracle_handled"][:, [4, 5]]
                .sum(axis=0).tolist())


CHECKS: tuple[tuple[str, str, str | None, bool], ...] = (
    # (name, rule, paired reference rule, gating)
    ("A4", "A4", None, True),
    ("A4-A1", "A4", "A1", True),       # paired: the common realized-noise part cancels (tightening)
    ("A0", "A0", None, False),
    ("A1", "A1", None, False),
    ("A4o", "A4o", None, False),
    ("A4o-A1", "A4o", "A1", False),
)


def check_quantity(moments: tuple, weights: dict, rule: str, ref_rule: str | None) -> np.ndarray:
    """Per (state, draw) quadratic of the check: V(w) or the paired V(w) - V(w_ref), ``(n, E)``."""
    q = quad(*moments, weights[rule])
    return q if ref_rule is None else q - quad(*moments, weights[ref_rule])


def tolerance(d: dict) -> dict:
    """SE of mean_i D_i, D_i = S_i - Q_i, from the half-draw moments only (never reads S).

    ``sigma_i^2(w)``, the variance of one draw's squared error (or paired difference), is
    estimated by ``(V_A - V_B)^2 / (1/M_A + 1/M_B)``; ``Var S_i = sum_j sigma^2(w_ij) / E^2``
    (independent evaluation draws); ``Var Q_i = (Q_A - Q_B)^2 / (1/M_A + 1/M_B) / M`` (the E
    weights share the oracle draws). States are independent given the states (fresh noise).
    """
    weights = control_weights(d)
    inv = 1.0 / d["mA"] + 1.0 / d["mB"]
    out = {}
    for name, rule, ref_rule, gating in CHECKS:
        qa = check_quantity(d["halves"]["A"], weights, rule, ref_rule)
        qb = check_quantity(d["halves"]["B"], weights, rule, ref_rule)
        sigma2 = (qa - qb) ** 2 / inv
        var_D = sigma2.sum(axis=1) / d["E"] ** 2 + \
            (qa.mean(axis=1) - qb.mean(axis=1)) ** 2 / inv / d["M"]
        Q = check_quantity((d["EC"], d["EP"], d["C"]), weights, rule, ref_rule).mean(axis=1)
        se = float(np.sqrt(var_D.sum()) / d["n"])
        scale = float(quad(d["EC"], d["EP"], d["C"], weights[rule]).mean())
        out[name] = dict(gating=gating, mean_Q=float(Q.mean()), scale_V=scale, se=se,
                         tol=Z_TOL * se,
                         rel_se=se / scale, rel_tol=Z_TOL * se / scale,
                         n_eff_var=float(var_D.sum() ** 2 / np.sum(var_D ** 2)))
    return out


def control_weights(d: dict) -> dict:
    """Weights of the gating rule (A4) and of the draw-independent controls A0, A1, A4o."""
    z = d["z"]
    shape = d["w0"].shape
    eo = z["core/eps_s"] ** 2
    do = z["core/delta"] ** 2
    w4o = do / np.maximum(eo + do, 1e-300)
    return {"A4": d["w0"], "A0": np.ones(shape), "A1": np.zeros(shape),
            "A4o": np.broadcast_to(w4o[:, None], shape).copy()}


def approx_check(d: dict, tols: dict, system: str) -> dict:
    """Stored state_mse at H_ref against mean_j V(w_ij); pass iff |mean D| <= Z_TOL * SE.

    ``rel_D`` is relative to the mean V of the rule (not of the paired difference). The block
    bootstrap SE of mean D (block 5, 2000 resamples) is a diagnostic only, not the criterion.
    """
    weights = control_weights(d)
    out = {}
    for name, rule, ref_rule, gating in CHECKS:
        S = d["z"][f"core/state_mse/{rule}"][:, d["ref"]]
        if ref_rule is not None:
            S = S - d["z"][f"core/state_mse/{ref_rule}"][:, d["ref"]]
        Q = check_quantity((d["EC"], d["EP"], d["C"]), weights, rule, ref_rule).mean(axis=1)
        D = S - Q
        t = tols[name]
        _, boot = bootstrap_values(lambda idx: float(D[idx].mean()), d["n"], RESAMPLES, BLOCK,
                                   make_rng(d["seed"], "wu0036", system, "check-se", name))
        out[name] = dict(gating=gating, mean_S=float(S.mean()), mean_Q=float(Q.mean()),
                         mean_D=float(D.mean()), rel_D=float(D.mean()) / t["scale_V"],
                         z=float(D.mean() / t["se"]), tol=t["tol"],
                         boot_se_diag=float(boot.std(ddof=1)),
                         passed=bool(abs(D.mean()) <= t["tol"]))
    return out


def ablation(d: dict, system: str) -> dict:
    """Four zero-coefficient variants, no refit; ratios against the unchanged A4 with intervals."""
    R, nu, rho, c = d["R"], d["nu"], d["rho"], d["coef"]
    EC, EP, C = d["EC"], d["EP"], d["C"]
    weights = {"unchanged": d["w0"]}
    hand_rel = {}
    for k in COEFS:
        cc = dict(c)
        cc[k] = 0.0
        w = a4_weight(R, nu, rho, cc["a"], cc["b"], cc["a_prime"], cc["b_prime"])
        hand = hand_weight(k, R, nu, rho, c["a"], c["b"], c["a_prime"], c["b_prime"])
        hand_rel[k] = rel_err(w, hand)
        assert hand_rel[k] <= RECON_TOL, (system, k, hand_rel[k])
        weights[k] = w
    V = {k: quad(EC, EP, C, w).mean(axis=1) for k, w in weights.items()}       # (n,)
    X = {k: excess(EC, EP, C, w).mean(axis=1) for k, w in weights.items()}     # (n,)
    vst = quad(EC, EP, C, np.clip((EP - C) / (EC + EP - 2 * C), 0, 1)[:, None])[:, 0]
    # oracle Monte Carlo error of the ratios from the halves (SE_full ~ |r_A - r_B| / 2)
    half_ratio = {}
    for h in "AB":
        ECh, EPh, Ch = d["halves"][h]
        Vh = {k: quad(ECh, EPh, Ch, w).mean() for k, w in weights.items()}
        Xh = {k: excess(ECh, EPh, Ch, w).mean() for k, w in weights.items()}
        half_ratio[h] = {k: (Vh[k] / Vh["unchanged"], Xh[k] / Xh["unchanged"]) for k in COEFS}
    stat_keys = [(k, q) for k in COEFS for q in ("V", "excess")]

    def statistic(idx: np.ndarray) -> np.ndarray:
        vals = []
        for k, q in stat_keys:
            src = V if q == "V" else X
            vals.append(src[k][idx].mean() / src["unchanged"][idx].mean())
        return np.array(vals)

    point, values = bootstrap_values(statistic, d["n"], RESAMPLES, BLOCK,
                                     make_rng(d["seed"], "wu0036", system, "ablation-ratio"))
    mean_w0 = d["w0"].mean(axis=1)
    out = {"unchanged": dict(mean_V=float(V["unchanged"].mean()),
                             mean_excess=float(X["unchanged"].mean()),
                             mean_V_star=float(vst.mean()),
                             mean_w=float(d["w0"].mean()),
                             share_w_gt_half=float(np.mean(mean_w0 > 0.5)))}
    for col, (k, q) in enumerate(stat_keys):
        lo, hi, nf = percentile_interval(values[:, col], LEVEL)
        mc = endpoint_mc_error(values[:, col], LEVEL)
        entry = out.setdefault(k, {})
        entry[f"ratio_{q}"] = float(point[col])
        entry[f"ci_{q}"] = [lo, hi]
        entry[f"ci_{q}_mc_se"] = list(mc)
        entry[f"n_failed_{q}"] = nf
        entry[f"oracle_mc_se_{q}"] = float(abs(half_ratio["A"][k][q == "excess"]
                                               - half_ratio["B"][k][q == "excess"]) / 2)
    for k in COEFS:
        mw = weights[k].mean(axis=1)
        out[k].update(mean_V=float(V[k].mean()), mean_excess=float(X[k].mean()),
                      mean_w=float(weights[k].mean()),
                      share_states_cross_half=float(np.mean((mw > 0.5) != (mean_w0 > 0.5))),
                      share_draws_cross_half=float(np.mean((weights[k] > 0.5) != (d["w0"] > 0.5))),
                      hand_formula_rel=hand_rel[k])
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--stage", choices=("tolerance", "full"), required=True)
    parser.add_argument("--out", type=pathlib.Path,
                        default=pathlib.Path(__file__).with_suffix(""))
    args = parser.parse_args()
    report = {"label": LABEL, "stage": args.stage, "z_tol": Z_TOL, "recon_tol": RECON_TOL,
              "block": BLOCK, "resamples": RESAMPLES, "level": LEVEL, "cells": {}}
    data = {}
    for run, run_dir in RUNS.items():
        for system in SYSTEMS:
            d = load(run_dir, system)
            data[(run, system)] = d
            tols = tolerance(d)
            report["cells"][f"{run} {system}"] = {
                "n_states": d["n"], "E": d["E"], "M": d["M"], "rho": d["rho"],
                "coefficients": d["coef"], "nu_cap": d["cap"], "checks": d["checks"],
                "test_eval_clips_href_plp_nonfinite": d["eval_clips_href_plp_nonfinite"],
                "test_oracle_clips_href_plp_nonfinite": d["oracle_clips_href_plp_nonfinite"],
                "tolerance": tols}
    if args.stage == "full":
        all_pass = True
        for (run, system), d in data.items():
            cell = report["cells"][f"{run} {system}"]
            cell["approx_check"] = approx_check(d, cell["tolerance"], system)
            all_pass &= all(v["passed"] for v in cell["approx_check"].values() if v["gating"])
        report["approx_check_all_pass"] = bool(all_pass)
        if all_pass:
            for (run, system), d in data.items():
                report["cells"][f"{run} {system}"]["ablation"] = ablation(d, system)
        else:
            report["ablation"] = "not computed: approximation check failed (ROADMAP WU-0036)"
    path = args.out.parent / f"{args.out.name}_{args.stage}.json"
    path.write_text(json.dumps(report, indent=1) + "\n")
    print(LABEL)
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
