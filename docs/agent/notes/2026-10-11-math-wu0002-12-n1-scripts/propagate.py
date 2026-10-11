"""Scratch: propagate the BLAS-kernel difference of the oracle gains into H1b/H1c-like
statistics with the code's own estimators (ols_slope, block bootstrap, B=500, block 5)."""
import sys
import numpy as np
from lpcstudy.statistics import block_bootstrap_dropped, block_bootstrap_counted, ols_slope
D = sys.argv[1]
ref = {k: np.load(f"{D}/h8/{k}.npy") for k in ("gains", "growth")}
for alt in ("h2", "sb", "pr"):
    g = {k: np.load(f"{D}/{alt}/{k}.npy") for k in ("gains", "growth")}
    rg = np.abs(g["gains"] / ref["gains"] - 1)
    rgr = np.abs(g["growth"] / ref["growth"] - 1)
    ulp = np.abs(g["gains"] - ref["gains"]) / np.spacing(ref["gains"])
    print(f"{alt}: gains rel max {rg.max():.2e} med {np.median(rg):.2e}; ulps med {np.median(ulp):.1f} "
          f"p99 {np.quantile(ulp,.99):.0f} max {ulp.max():.0f}; frac differing {np.mean(rg>0):.2f}; "
          f"growth rel max {rgr.max():.2e} med {np.median(rgr):.2e}; growth min |.| {np.abs(ref['growth']).min():.2e}")
rng = np.random.default_rng(1)
n = len(ref["growth"])
seed = np.exp(rng.normal(np.log(0.01), 0.5, n))
noise = rng.normal(0, 0.3, n)
b = np.abs(rng.normal(25, 8, n))  # synthetic T-vs-ln(theta) slopes per state
def h1b(gains):
    x = np.log(gains[:, 29] * seed / np.sqrt(3)); y = 1.2 * x + noise
    est, lo, hi, _ = block_bootstrap_dropped(lambda i: ols_slope(x[i], y[i]), n, 500, 5, 20261005, 0.95)
    return np.array([est, lo, hi])
def h1c(growth):
    r = growth * b; r = r[np.isfinite(r)]
    iv = block_bootstrap_counted(lambda i: float(np.median(r[i])), r.size, 500, 5, 20261005, 0.95)
    return np.array([iv.estimate, iv.lower, iv.upper])
a1, c1 = h1b(ref["gains"]), h1c(ref["growth"])
for alt in ("h2", "sb", "pr"):
    g = {k: np.load(f"{D}/{alt}/{k}.npy") for k in ("gains", "growth")}
    print(alt, "H1b-like rel diff (slope, lo, hi):", np.abs(h1b(g["gains"]) / a1 - 1),
          " H1c-like rel diff (median, lo, hi):", np.abs(h1c(g["growth"]) / c1 - 1))
