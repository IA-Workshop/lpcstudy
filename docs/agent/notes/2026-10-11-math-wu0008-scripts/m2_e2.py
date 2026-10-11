"""WU-0008 M2/E2 design: helper SE against the SD of the endpoints over R repeated bootstraps on the same data.

Mean of a Gaussian AR(1) (phi = 0.3, n = 500), moving blocks of 5, B = 2000, levels 0.95 and 1 - 0.05/3.
Own vectorized block bootstrap (same law as statistics._draw_indices; not bitwise). For n_data independent data sets:
the probability that the single first-bootstrap ratio leaves [0.5, 2] (the planned E2), and the distribution of
median_R(SE)/SD_R(endpoint) (the proposed E2). Usage: python m2_e2.py [R=100] [n_data=1000]. CPU; about 2 min.
"""
import sys, time
import numpy as np
n, block, B, phi = 500, 5, 2000, 0.3
LEVELS = (0.95, 1 - 0.05 / 3)

def ar1(rng):
    e = rng.standard_normal(n)
    x = np.empty(n); x[0] = e[0]
    for t in range(1, n):
        x[t] = phi * x[t - 1] + np.sqrt(1 - phi**2) * e[t]
    return x

def boot_means(x, rng):
    sums = np.convolve(x, np.ones(block), "valid")
    starts = rng.integers(0, n - block + 1, (B, n // block))
    return sums[starts].sum(axis=1) / n

def endpoints_and_se(v):
    out = []
    for level in LEVELS:
        a = (1 - level) / 2
        for q in (a, 1 - a):
            d = np.sqrt(q * (1 - q) / B)
            out.append((np.quantile(v, q), (np.quantile(v, q + d) - np.quantile(v, q - d)) / 2))
    return np.array(out)

if __name__ == "__main__":
    R = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    n_data = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    master = np.random.default_rng(777)
    t0 = time.time()
    lmed, first, allr = [], [], []
    for _ in range(n_data):
        x = ar1(master)
        res = np.stack([endpoints_and_se(boot_means(x, master)) for _ in range(R)])
        ratio = res[:, :, 1] / res[:, :, 0].std(axis=0, ddof=1)
        lmed.append(np.log(np.median(ratio, axis=0))); first.append(ratio[0]); allr.append(ratio)
    lmed, first, allr = np.array(lmed), np.array(first), np.concatenate(allr)
    print(f"{n_data} data sets x {R} bootstraps, {time.time() - t0:.0f} s; endpoints: 95 lo, 95 hi, 98.3 lo, 98.3 hi")
    print("single ratio: relative SD", (allr.std(0) / allr.mean(0)).round(3),
          "quantiles 1/5/50/95/99%:", [np.percentile(allr[:, j], [1, 5, 50, 95, 99]).round(3).tolist() for j in range(4)])
    for lo, hi in ((0.5, 2.0), (1 / 3, 3.0)):
        out = (first < lo) | (first > hi)
        print(f"planned E2, first bootstrap in [{lo:.3f}, {hi}]: P(endpoint out) {out.mean(0)}, P(any of 4) {out.any(1).mean():.4f}")
    print("log(median ratio): mean", lmed.mean(0).round(4), "sd", lmed.std(0).round(4))
    for f in (1.25, 1.3, 1.35, 1.4, 1.5):
        out = np.abs(lmed) > np.log(f)
        print(f"proposed E2, median within factor {f}: P(endpoint out) {out.mean(0)}, P(any of 4) {out.any(1).mean():.4f}")
    print("extremes of the median ratio:", np.exp(lmed.min(0)).round(3), np.exp(lmed.max(0)).round(3))
