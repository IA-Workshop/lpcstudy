"""Q1 step 1: reproduce the H1a point fit of the smoke kernel pair and identify the stop.

DEVELOPMENT (DEV-0): not a hypothesis test. Reads two results.json files read-only. The fit is a
verbatim copy of ``lpcstudy.analysis._floor_power_law`` and ``_fit_seed_law`` (worktree c80f908),
so no lpcstudy import (no JAX). The inputs are the squared ``median_seed_by_n_lib`` leaves (the
leaf stores sqrt(median), so the square may differ from the production median by ~1 ulp).
"""
import json, sys, warnings
import numpy as np
from scipy.optimize import curve_fit, least_squares, OptimizeWarning

BOUNDS = (0.01, 10.0)


def model(log_n, log_c2, exponent, log_f2):
    return np.log(np.exp(log_c2) * np.exp(log_n) ** (-exponent) + np.exp(log_f2))


def guess_of(sizes, mean_sq):
    log_n = np.log(sizes)
    return (np.log(mean_sq[0]) + 2 * 0.5 * log_n[0], 1.0, np.log(mean_sq[-1] * 0.5))


def fit_prod(sizes, mean_sq):
    log_n = np.log(sizes)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", OptimizeWarning)
        p, _ = curve_fit(model, log_n, np.log(mean_sq), p0=guess_of(sizes, mean_sq),
                         bounds=([-50, BOUNDS[0], -60], [50, BOUNDS[1], 10]), maxfev=20_000)
    return p


def fit_ls(sizes, mean_sq, tol=None):
    """The same problem through least_squares (what curve_fit calls with bounds), to read
    nfev, status and the last step; tol None means scipy's defaults (1e-8)."""
    log_n, y = np.log(sizes), np.log(mean_sq)
    kw = {} if tol is None else dict(ftol=tol, xtol=tol, gtol=tol)
    res = least_squares(lambda p: model(log_n, *p) - y, np.array(guess_of(sizes, mean_sq)),
                        method="trf", bounds=([-50, BOUNDS[0], -60], [50, BOUNDS[1], 10]),
                        max_nfev=20_000, **kw)
    return res


def h1a_medians(path, system="lorenz63", rho="0.01"):
    blk = json.load(open(path))["systems"][system]["H1a"]["by_noise"][rho]
    sizes = np.array(sorted(int(k) for k in blk["median_seed_by_n_lib"]), dtype=float)
    med = np.array([blk["median_seed_by_n_lib"][str(int(n))] for n in sizes]) ** 2
    return sizes, med, blk


if __name__ == "__main__":
    ref, new = sys.argv[1], sys.argv[2]
    out = {}
    for tag, path in (("ref", ref), ("new", new)):
        sizes, med, blk = h1a_medians(path)
        p = fit_prod(sizes, med)
        r = fit_ls(sizes, med)
        out[tag] = (p, r, blk, med)
        print(f"{tag}: sizes {sizes.astype(int).tolist()} medians^2 {med.tolist()}")
        print(f"  reproduced 1/d = {p[1]/2!r}  leaf = {blk['fitted_inverse_dim']!r}  "
              f"equal: {p[1]/2 == blk['fitted_inverse_dim']}")
        print(f"  reproduced floor_rms = {np.sqrt(np.exp(p[2]))!r}  leaf = {blk['floor_rms']!r}")
        print(f"  params {p.tolist()}")
        print(f"  least_squares: status {r.status} ({r.message}); nfev {r.nfev}; cost {r.cost:.3e}; "
              f"optimality {r.optimality:.3e}; x equal to curve_fit: {np.array_equal(r.x, p)}")
    pr, pn = out["ref"][0], out["new"][0]
    print("relative change of params (new vs ref):", (np.abs(pn - pr) / np.abs(pr)).tolist())
    print("relative change of inputs (medians^2):",
          (np.abs(out['new'][3] - out['ref'][3]) / out['ref'][3]).tolist())
    # Underdetermination: Jacobian at the solution (n_sizes x 3), singular values, null direction
    sizes = h1a_medians(ref)[0]
    log_n = np.log(sizes)
    def jac(p, h=1e-6):
        J = np.empty((len(log_n), 3))
        for k in range(3):
            e = np.zeros(3); e[k] = h
            J[:, k] = (model(log_n, *(p + e)) - model(log_n, *(p - e))) / (2 * h)
        return J
    J = jac(pr)
    U, S, Vt = np.linalg.svd(J)
    print("Jacobian singular values:", S.tolist(), " rows:", J.shape[0])
    print("null direction (log_c2, 2/d, log_f2):", Vt[-1].tolist())
    # the family of exact solutions: fix 2/d at other values and solve the 2 x 2 system
    for e2 in (pr[1] * 0.9, pr[1], pr[1] * 1.1):
        sol = least_squares(lambda q: model(log_n, q[0], e2, q[1]) - np.log(out["ref"][3]),
                            np.array([pr[0], pr[2]]), xtol=1e-15, ftol=1e-15, gtol=1e-15)
        print(f"  2/d fixed at {e2:.6f}: exact fit cost {sol.cost:.2e}, floor_rms {np.sqrt(np.exp(sol.x[1])):.6f}")
