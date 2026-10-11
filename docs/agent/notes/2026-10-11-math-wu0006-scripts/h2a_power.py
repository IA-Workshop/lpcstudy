"""WU-0006.4 (DEF-0022 power finding): width and P(pass) of the H2a(ii-b) interval against n and rho.

Design: the C7 generator of the note's M3 (a) with corr(e1, e2) = rho (the true partial correlation,
exact because both conditional means lie in span[1, Q]); the procedure is the study's (moving-block
bootstrap, blocks of 5, B = 2000, np.quantile bounds at 1 - 0.05/3). Verdict "pass" iff the interval
lies inside the open band (-0.1, 0.1). n is the number of states in the part's domain (for the
interior part, the test states with 0 < w* < 1).

Two estimates of P(pass | rho):
  * shift: from replications at rho = 0, P(lo0 + rho > -0.1 and hi0 + rho < 0.1) (the distribution
    of the interval about the truth is nearly shift-invariant for |rho| <= 0.1: its SD scales by
    1 - rho^2 >= 0.99);
  * direct: replications at rho itself (validation points).
Scratch seed literal 20261013 (not a DEV or CONF seed); 4 spawned single-thread workers.
Writes ``h2a_power_<n>_<phi>_<rho>.npy`` (estimate, lo, hi per replication) to the current directory.

Usage: python h2a_power.py
"""
import os
import sys
import time

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
from multiprocessing import get_context

import numpy as np
from scipy.stats import norm

from simcore import ar1, starts, idx_from, mult, partial_w, quad

B = 2000
LEVEL = 1 - 0.05 / 3
Z = norm.ppf(1 - (1 - LEVEL) / 2)
EDGE = 0.1


def one(n, phi, rho, rng):
    st = starts(rng, B, n)
    s = ar1(rng, n, phi, 2, 0.0)
    e = ar1(rng, n, phi, 2, rho)
    t = 0.5 * s[:, 0] - 0.3 * s[:, 1] ** 2 + e[:, 0]
    v = 0.4 * s[:, 1] + 0.2 * s[:, 0] * s[:, 1] + e[:, 1]
    Q = quad(s)
    m = mult(idx_from(st, n), n)
    vals = partial_w(m, t, v, Q)
    est = partial_w(np.ones((1, n), dtype=np.int64), t, v, Q)[0]
    a = (1 - LEVEL) / 2
    return est, np.quantile(vals, a), np.quantile(vals, 1 - a)


def work(args):
    n, phi, rho, seed, reps = args
    rng = np.random.default_rng(seed)
    return [one(n, phi, rho, rng) for _ in range(reps)]


def run(n, phi, rho, R, pool, chunks=40):
    ss = np.random.SeedSequence([20261013, n, int(round(phi * 1000)), int(round(rho * 1000))])
    seeds = [int(c.generate_state(1)[0]) for c in ss.spawn(chunks)]
    per = [R // chunks + (i < R % chunks) for i in range(chunks)]
    res = pool.map(work, [(n, phi, rho, s, r) for s, r in zip(seeds, per)])
    return np.array([row for part in res for row in part])


def p_pass(arr, shift=0.0):
    lo, hi = arr[:, 1] + shift, arr[:, 2] + shift
    return float(np.mean((lo > -EDGE) & (hi < EDGE)))


def main():
    grid = [(n, phi, 0.0, 2000) for phi in (0.0, 0.3) for n in (250, 500, 1000, 2000)]
    grid += [(500, 0.0, 0.05, 1000), (1000, 0.0, 0.05, 1000), (2000, 0.3, 0.05, 1000)]
    data = {}
    with get_context("spawn").Pool(4) as pool:
        for n, phi, rho, R in grid:
            t0 = time.time()
            arr = run(n, phi, rho, R, pool)
            np.save(f"h2a_power_{n}_{phi:g}_{rho:g}.npy", arr)
            data[(n, phi, rho)] = arr
            print(f"run n={n} phi={phi:g} rho={rho:g} R={R} t={time.time() - t0:.0f}s", flush=True)
    print("\nWidth of the 1 - 0.05/3 interval (rho = 0); observed exponent p from W(n)/W(2n) = 2^p")
    print("| phi | n | mean width (MC SE) | SD of estimate | mean half-width / (z SD) | p | "
          "P(pass, rho=0) (SE) |")
    for phi in (0.0, 0.3):
        prev = None
        for n in (250, 500, 1000, 2000):
            a = data[(n, phi, 0.0)]
            w = a[:, 2] - a[:, 1]
            sd = a[:, 0].std(ddof=1)
            kappa = w.mean() / 2 / (Z * sd)
            p = "" if prev is None else f"{np.log(prev / w.mean()) / np.log(2):.3f}"
            pp = p_pass(a)
            print(f"| {phi:g} | {n} | {w.mean():.4f} ({w.std(ddof=1) / np.sqrt(len(w)):.4f}) | "
                  f"{sd:.4f} | {kappa:.3f} | {p} | {pp:.3f} ({np.sqrt(pp * (1 - pp) / len(w)):.3f}) |")
            prev = w.mean()
    print("\nP(pass | rho) by the shift estimate (rho = 0 replications)")
    rhos = np.round(np.arange(0.0, 0.1001, 0.01), 3)
    print("| phi | n | " + " | ".join(f"rho={r:g}" for r in rhos) + " | largest |rho| with P >= 0.8 |")
    for phi in (0.0, 0.3):
        for n in (250, 500, 1000, 2000):
            a = data[(n, phi, 0.0)]
            ps = [p_pass(a, r) for r in rhos]
            fine = np.round(np.arange(0.0, 0.1001, 0.001), 4)
            ok = [r for r in fine if p_pass(a, r) >= 0.8]
            print(f"| {phi:g} | {n} | " + " | ".join(f"{p:.3f}" for p in ps)
                  + f" | {max(ok) if ok else 'none'} |")
    print("\nValidation of the shift estimate by direct replications at rho")
    for (n, phi, rho), a in data.items():
        if rho == 0.0:
            continue
        direct = p_pass(a)
        shifted = p_pass(data[(n, phi, 0.0)], rho)
        se = np.sqrt(direct * (1 - direct) / len(a) + shifted * (1 - shifted) / len(data[(n, phi, 0.0)]))
        print(f"n={n} phi={phi:g} rho={rho:g}: direct {direct:.3f}, shift {shifted:.3f}, "
              f"z {(direct - shifted) / se:.2f}")
    print("\nNormal-theory n for P(pass | rho) >= 0.8, half-width h = kappa z s, s = c / sqrt(n)")
    for phi in (0.0, 0.3):
        a = data[(1000, phi, 0.0)]
        c = a[:, 0].std(ddof=1) * np.sqrt(1000)
        kappa = (a[:, 2] - a[:, 1]).mean() / 2 / (Z * a[:, 0].std(ddof=1))
        for rho in (0.0, 0.02, 0.05):
            for n in range(500, 20001, 10):
                s = c / np.sqrt(n)
                h = kappa * Z * s
                prob = norm.cdf((EDGE - rho - h) / s) - norm.cdf((-EDGE - rho + h) / s)
                if prob >= 0.8:
                    print(f"phi={phi:g} rho={rho:g}: n >= {n} (c = {c:.3f}, kappa = {kappa:.3f})")
                    break


if __name__ == "__main__":
    sys.exit(main())
