#!/usr/bin/env python3
"""WU-0041b: development preview of the refit-mode A4 ablation, for the
predictions of the pre-registration section 6.3.

DEVELOPMENT (DEV-1, DEV-2): not a hypothesis test. A prediction aid, not a
stage-2 result: stage 2 (WU-0039) refits on the construction states, which
the dumps do not hold. Here every one-coefficient refit is made on the TEST
states of the dump (a stand-in with the same law), with the package's fit
recipe (``allocation.SeedProxy.fit``: per-state median over draws of the
squared feature and floor, scale by the median seed, NNLS start, soft_l1 on
the log scale). For a one-term proxy that recipe reduces to a robust location
of ln(seed^2 / term^2). Scored as in stage 1: the oracle quadratic V(w) at
H_ref averaged over the evaluation draws, ratio of means against the
unchanged A4, paired moving-block bootstrap (block 5, 2000 resamples), at
both levels 0.95 and 1 - 0.05/3, generator ``make_rng(seed, "wu0041b",
system, "refit-ratio")``.

Variants (refit mode): the named term is removed and the remaining
coefficient(s) of the SAME proxy refitted (the other proxy is unchanged, as
its fit does not involve the removed term):

* ``a``: eps_hat^2 = b (rho nu)^2, b refitted;
* ``b``: eps_hat^2 = a (R nu)^2, a refitted;
* ``a'``: delta_hat^2 = b' rho^2, b' refitted;
* ``b'``: delta_hat^2 = a' (rho nu)^2, a' refitted.

Also reported: MSE(A2)/MSE(A4) by the same V and resamples (A2's stored
weight), because refit-a gives a constant weight.

Run (CPU, one thread)::

    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 nice -n 19 \
        <.venv>/bin/python -I refit_predict.py
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import numpy as np
from scipy.optimize import least_squares, nnls

HERE = pathlib.Path(__file__).resolve().parent
STAGE1 = HERE.parent / "2026-10-25-a4-coefficient-ablation-stage1" / "a4_ablation.py"
spec = importlib.util.spec_from_file_location("a4_ablation", STAGE1)
s1 = importlib.util.module_from_spec(spec)
sys.modules["a4_ablation"] = s1
spec.loader.exec_module(s1)

from lpcstudy.data import make_rng  # noqa: E402  (path set by stage 1)
from lpcstudy.statistics import bootstrap_values, percentile_interval  # noqa: E402

LEVELS = (0.95, 1 - 0.05 / 3)


def fit_two(feature_sq, floor_sq, seed_sq):
    """The package's two-coefficient fit (copy of SeedProxy.fit)."""
    scale = np.median(seed_sq)
    design = np.column_stack([feature_sq, floor_sq]) / scale
    coef, _ = nnls(design, seed_sq / scale)
    start = np.log(np.maximum(coef, 1e-6))
    log_seed = np.log(seed_sq / scale)
    sol = least_squares(
        lambda lc: np.log(design @ np.exp(lc) + 1e-300) - log_seed,
        start, loss="soft_l1")
    return np.exp(sol.x)


def fit_one(term_sq, seed_sq):
    """The same recipe with one column."""
    scale = np.median(seed_sq)
    design = term_sq[:, None] / scale
    coef, _ = nnls(design, seed_sq / scale)
    start = np.log(np.maximum(coef, 1e-6))
    log_seed = np.log(seed_sq / scale)
    sol = least_squares(
        lambda lc: np.log(design @ np.exp(lc) + 1e-300) - log_seed,
        start, loss="soft_l1")
    return float(np.exp(sol.x[0]))


def main() -> None:
    out = {"label": "DEVELOPMENT (DEV-1, DEV-2): not a hypothesis test",
           "cells": {}}
    print(out["label"])
    for run, run_dir in s1.RUNS.items():
        for system in s1.SYSTEMS:
            d = s1.load(run_dir, system)
            R, nu, rho, c = d["R"], d["nu"], d["rho"], d["coef"]
            z = d["z"]
            eps2 = z["core/eps_s"] ** 2
            del2 = z["core/delta"] ** 2
            f_an = np.median((R * nu) ** 2, axis=1)
            g_an = np.median((rho * nu) ** 2, axis=1)
            f_es = np.median((rho * nu) ** 2, axis=1)
            g_es = np.full_like(f_es, rho ** 2)
            # sanity: the two-term fit on test states, against the stored fit
            a_t, b_t = fit_two(f_an, g_an, eps2)
            ap_t, bp_t = fit_two(f_es, g_es, del2)
            refit = {
                "a": dict(c, a=0.0, b=fit_one(g_an, eps2)),
                "b": dict(c, b=0.0, a=fit_one(f_an, eps2)),
                "a_prime": dict(c, a_prime=0.0, b_prime=fit_one(g_es, del2)),
                "b_prime": dict(c, b_prime=0.0, a_prime=fit_one(f_es, del2)),
            }
            weights = {"unchanged": d["w0"],
                       "A2": z["core/weight_href/A2"]}
            for k, cc in refit.items():
                weights[k] = s1.a4_weight(R, nu, rho, cc["a"], cc["b"],
                                          cc["a_prime"], cc["b_prime"])
            V = {k: s1.quad(d["EC"], d["EP"], d["C"], w).mean(axis=1)
                 for k, w in weights.items()}
            keys = ["a", "b", "a_prime", "b_prime", "A2"]

            def stat(idx):
                return np.array([V[k][idx].mean() / V["unchanged"][idx].mean()
                                 for k in keys])

            point, values = bootstrap_values(
                stat, d["n"], s1.RESAMPLES, s1.BLOCK,
                make_rng(d["seed"], "wu0041b", system, "refit-ratio"))
            cell = {"stored_fit": c,
                    "test_state_two_term_fit": dict(a=a_t, b=b_t,
                                                    a_prime=ap_t, b_prime=bp_t),
                    "refit_coefficients": {k: refit[k] for k in refit},
                    "rows": {}}
            print(f"\n{run} {system}: stored a={c['a']:.4f} b={c['b']:.1e} "
                  f"a'={c['a_prime']:.4f} b'={c['b_prime']:.2e}; test-state "
                  f"fit a={a_t:.4f} b={b_t:.1e} a'={ap_t:.4f} b'={bp_t:.2e}")
            for col, k in enumerate(keys):
                row = {"ratio": float(point[col]),
                       "mean_w": float(weights[k].mean())}
                for lev in LEVELS:
                    lo, hi, nf = percentile_interval(values[:, col], lev)
                    row[f"ci_{lev:.4f}"] = [lo, hi]
                    row[f"n_failed_{lev:.4f}"] = nf
                if k in refit:
                    rc = refit[k]
                    row["refit"] = {kk: rc[kk] for kk in ("a", "b", "a_prime",
                                                          "b_prime")}
                cell["rows"][k] = row
                ci95, ci98 = row["ci_0.9500"], row[f"ci_{LEVELS[1]:.4f}"]
                print(f"  {k:8s} r={row['ratio']:.4f}  95% [{ci95[0]:.4f}, "
                      f"{ci95[1]:.4f}]  98.3% [{ci98[0]:.4f}, {ci98[1]:.4f}]"
                      f"  mean w {row['mean_w']:.4f}"
                      + (f"  refit {row['refit']}" if k in refit else ""))
            out["cells"][f"{run} {system}"] = cell
    (HERE / "refit_predict.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
