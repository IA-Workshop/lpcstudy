"""WU-0006.4 (C7 correction): reference distribution of the C7 verdict counts out of R_test = 1000.

The verdict of H2a(ii-b) for the open band (-0.1, 0.1) at level 1 - 0.05/3, as production codes it
(and as the harness's independent rule ``expected_verdict`` codes it):
    pass         <=> lo > -0.1 and hi < 0.1
    fail         <=> lo >= 0.1 or hi <= -0.1
    inconclusive  otherwise.
The original reference (``make_tables.py``) took P(pass) = P(truth 0.1 > hi), the one-sided miss,
which ignores the condition lo > -0.1; that is the error corrected here (DEF-0022).

Input: ``cov_C7_<phi>.npy`` (R_ref = 20 000, seed 20261011, ``m2_coverage.py``) and
``cov_C7_<phi>_ext.npy`` (``c7_extend.py``, seed 20261012), from the current directory.
Range rule: the same as for the other 70 ranges (``m2_ranges.rng_counts``): central 1 - 0.0005
interval of Bin(1000, p) mixed over p ~ N(p_ref, se_ref^2). A sensitivity column mixes over the
Jeffreys posterior Beta(k + 1/2, R_ref - k + 1/2) instead (better for small k).
Uses only the design and the reference replications; no test-run count enters.
"""
import numpy as np
from scipy.stats import binom, beta

from m2_ranges import rng_counts, TAIL, RT
from m2_pfail import p_fail_rate

EDGE = 0.1
A3_MAX = 16  # ROADMAP bound on a verdict count at the edge, 98.3% level


def verdicts(arr):
    lo, hi = arr[:, 2], arr[:, 3]  # the 1 - 0.05/3 column
    passes = (lo > -EDGE) & (hi < EDGE)
    fails = (lo >= EDGE) | (hi <= -EDGE)
    return passes, fails, ~passes & ~fails


def beta_range(k, R):
    gx, gw = np.polynomial.legendre.leggauss(400)
    a, b = k + 0.5, R - k + 0.5
    lo_q, hi_q = beta.ppf([1e-9, 1 - 1e-9], a, b)
    ps = 0.5 * (hi_q - lo_q) * gx + 0.5 * (hi_q + lo_q)
    ws = 0.5 * (hi_q - lo_q) * gw * beta.pdf(ps, a, b)
    ws = ws / ws.sum()
    ks = np.arange(RT + 1)
    pm = sum(w * binom.pmf(ks, RT, p) for p, w in zip(ps, ws))
    c = np.cumsum(pm)
    return int(np.searchsorted(c, TAIL)), int(np.searchsorted(c, 1 - TAIL))


def tail_masses(p, se, rng):
    gx, gw = np.polynomial.hermite_e.hermegauss(61)
    gw = gw / gw.sum()
    ps = np.clip(p + se * gx, 1e-9, 1 - 1e-9)
    below = float(np.sum(gw * binom.cdf(rng[0] - 1, RT, ps)))
    above = float(np.sum(gw * binom.sf(rng[1], RT, ps)))
    return below, above


def main():
    for phi in ("0", "0.3"):
        parts = {"orig": np.load(f"cov_C7_{phi}.npy"), "ext": np.load(f"cov_C7_{phi}_ext.npy")}
        for tag, arr in parts.items():
            p, f, i = verdicts(arr)
            print(f"phi={phi} {tag}: R={len(arr)} pass={p.sum()} fail={f.sum()} "
                  f"(lo>=0.1: {(arr[:, 2] >= EDGE).sum()}, hi<=-0.1: {(arr[:, 3] <= -EDGE).sum()}) "
                  f"inconclusive={i.sum()} mean width={np.mean(arr[:, 3] - arr[:, 2]):.4f}")
        a = np.vstack(list(parts.values()))
        R = len(a)
        for name, mask in zip(("pass", "fail", "inconclusive"), verdicts(a)):
            k = int(mask.sum())
            q = k / R
            se = np.sqrt(q * (1 - q) / R)
            rng = rng_counts(q, se)
            below, above = tail_masses(q, se, rng)
            pf = p_fail_rate(q, se, A3_MAX) if name != "inconclusive" else float("nan")
            print(f"phi={phi} pooled R_ref={R} {name}: k={k} rate={q:.5f} se={se:.5f} "
                  f"(count SE {1000 * se:.2f}) range={rng} beta-range={beta_range(k, R)} "
                  f"false-alarm below={below:.5f} above={above:.5f} P(ROADMAP A3 fails)={pf:.3f}")


if __name__ == "__main__":
    main()
