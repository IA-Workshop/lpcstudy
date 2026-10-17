"""Q1 step 3: size of a stopping-test flip, and the mechanism of the ulp amplification.

DEVELOPMENT (DEV-0): not a hypothesis test. Same inputs as q1_pilot_sensitivity (P0, P1 H1a
medians, 5 sizes; plus resample-like jitter, scratch seed 20261019) and the smoke kernel pair
(2 sizes). Read-only.

(1) Flip size. Two correct runs whose inputs differ at the ulp level can stop at different
    iterations when the stopping test is marginal. The difference is then one solver step. It is
    bracketed by refitting with the stopping tolerance halved and doubled (the neighbouring stops):
    flip = max(|theta(tol/2) - theta(tol)|, |theta(2 tol) - theta(tol)|), on the stopping test that
    fired (ftol for the 5-size fits, gtol for the 2-size smoke fit).
(2) Mechanism. The ulp experiment of q1_pilot_sensitivity is repeated with an analytic Jacobian
    instead of scipy's 2-point finite differences (the production setting).
"""
import json, sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
sys.path.insert(0, str(Path(__file__).resolve().parent))
from q1_reproduce import model, guess_of, h1a_medians

LB, UB = [-50, 0.01, -60], [50, 10.0, 10]
rng = np.random.default_rng(20261019)


def fit(sizes, med, ftol=1e-8, xtol=1e-8, gtol=1e-8, analytic=False):
    log_n, y = np.log(sizes), np.log(med)
    def jac(p):
        a = np.exp(p[0] - p[1] * log_n); f = np.exp(p[2]); den = a + f
        return np.column_stack([a / den, -log_n * a / den, f / den])
    return least_squares(lambda p: model(log_n, *p) - y, np.array(guess_of(sizes, med)),
                         jac=jac if analytic else "2-point", method="trf", bounds=(LB, UB),
                         ftol=ftol, xtol=xtol, gtol=gtol, max_nfev=20_000)


def flip(sizes, med, s):
    r0 = fit(sizes, med)
    which = {1: "gtol", 2: "ftol", 3: "xtol", 4: "ftol"}.get(r0.status, "ftol")
    out = []
    for f in (0.5, 2.0):
        kw = {which: 1e-8 * f}
        r = fit(sizes, med, **kw)
        out.append((abs(r.x[1] - r0.x[1]) / 2 / s,
                    abs(np.exp(r.x[2] / 2) - np.exp(r0.x[2] / 2)) / np.exp(r0.x[2] / 2),
                    r.nfev != r0.nfev))
    return max(o[0] for o in out), max(o[1] for o in out), any(o[2] for o in out), which


def ulp_amp(sizes, med, s, analytic, n=100, gamma=3.2e-14):
    r0 = fit(sizes, med, analytic=analytic)
    d = [abs(fit(sizes, med * (1 + rng.uniform(-gamma, gamma, len(sizes))), analytic=analytic).x[1]
             - r0.x[1]) / 2 / s for _ in range(n)]
    return max(d)


if __name__ == "__main__":
    cells = []
    for path in sys.argv[1:3]:
        for system, blk in json.load(open(path))["systems"].items():
            for rho, b in blk["H1a"]["by_noise"].items():
                sizes = np.array(sorted(int(k) for k in b["median_seed_by_n_lib"]), dtype=float)
                med = np.array([b["median_seed_by_n_lib"][str(int(n))] for n in sizes]) ** 2
                cells.append((f"{Path(path).parts[-3]} {system} {rho}", sizes, med,
                              max(map(abs, b["ci_inverse_dim"]))))
    rows = []
    for name, sizes, med, s in cells:
        rows.append(("point",) + flip(sizes, med, s))
        for _ in range(40):
            rows.append(("resample",) + flip(sizes, med * np.exp(rng.normal(0, 0.05, len(sizes))), s))
    for kind in ("point", "resample"):
        rr = [r for r in rows if r[0] == kind]
        fi = np.array([r[1] for r in rr]); ff = np.array([r[2] for r in rr])
        print(f"5-size {kind:8s} n={len(rr):3d} stop on {sorted(set(r[4] for r in rr))}: flip 1/d / s "
              f"median {np.median(fi):.2e} p99 {np.quantile(fi, 0.99):.2e} max {fi.max():.2e}; "
              f"floor rel median {np.median(ff):.2e} max {ff.max():.2e}; nfev changed in "
              f"{sum(r[3] for r in rr)}")
    # smoke kernel pair (2 sizes): gtol stop, underdetermined
    sizes, med, b = h1a_medians(sys.argv[3])
    s = max(map(abs, b["ci_inverse_dim"]))
    fi, ff, ch, which = flip(sizes, med, s)
    print(f"2-size smoke point: stop on {which}; flip 1/d / s {fi:.2e}; floor rel {ff:.2e}; nfev changed {ch}")
    sm = [flip(sizes, med * np.exp(rng.normal(0, 0.05, 2)), s) for _ in range(200)]
    print(f"2-size smoke resample-like n=200: flip 1/d / s median {np.median([x[0] for x in sm]):.2e} "
          f"max {max(x[0] for x in sm):.2e}; floor rel max {max(x[1] for x in sm):.2e}")
    # mechanism
    for name, sizes, med, s in cells[:4]:
        print(f"ulp amplification {name}: 2-point jac {ulp_amp(sizes, med, s, False):.2e} s, "
              f"analytic jac {ulp_amp(sizes, med, s, True):.2e} s")
    print(f"ulp amplification smoke: 2-point jac {ulp_amp(sizes, med, s, False):.2e} s, "
          f"analytic jac {ulp_amp(sizes, med, s, True):.2e} s")
