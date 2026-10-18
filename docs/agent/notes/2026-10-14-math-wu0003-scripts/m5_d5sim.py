"""M5: synthetic check of the D5 direct finite-M bias estimator of the H2a(i) median range.

Model (indicative, not fitted): per state, true weights w(h) at h = 1, 2, 4 LT; draw-noise SD at
M draws s * sqrt(200/M), s log-normal with median 0.017 (V4: s_med = h/1.96 ~ 0.016-0.021), noise
correlation c across horizons (common draws), nested draws M = 50 < 200 < 800 (prefixes: the
increments are independent); w_hat clipped to [0, 1]. True ranges: a mix of exact separation
(range 0) and spread ranges (exponential, mean 0.15); 30% of states have w near 0.
Estimators on n_V4 states: D(200) = mean(r_200 - r_800); median shift; Richardson with the
observed order from 50/200/800; conservative 2 D(200) (order 1/2).
Truth: bias of the median range over a large state sample at M = 200 against M = infinity.
Synthetic (seed 20261016): not a DEV or CONF seed.
"""
import numpy as np
rng = np.random.default_rng(20261016)

def states(n, frac_sep):
    base = rng.uniform(0.05, 0.6, n)
    base[rng.random(n) < 0.3] = 0.0
    spread = rng.exponential(0.15, (n, 3)) * rng.choice([-1, 1], (n, 3))
    sep = rng.random(n) < frac_sep
    spread[sep] = 0.0
    w = np.clip(base[:, None] + spread, 0, 1)
    s = 0.017 * np.exp(0.5 * rng.standard_normal(n))
    return w, s

def noisy(w, s, c, Ms=(50, 200, 800)):
    n = w.shape[0]
    cov = np.full((3, 3), c) + (1 - c) * np.eye(3)
    L = np.linalg.cholesky(cov)
    # nested: sum of independent increments; mean of first M draws ~ prefix sums
    incr_sizes = np.diff((0,) + Ms)
    sums = np.zeros((n, 3)); out = {}; tot = 0
    for M, k in zip(Ms, incr_sizes):
        z = rng.standard_normal((n, 3)) @ L.T * np.sqrt(k)
        sums += z; tot += k
        e = sums / tot * np.sqrt(200.0) * s[:, None]   # SD s*sqrt(200/M)
        out[M] = np.clip(w + e, 0, 1)
    return out

def rng_(x):
    return x.max(1) - x.min(1)

for c in (0.0, 0.5, 0.9):
    for frac_sep in (0.2, 0.6):
        wb, sb = states(200000, frac_sep)
        nb = noisy(wb, sb, c)
        truth_med = np.median(rng_(nb[200])) - np.median(rng_(wb))
        truth_mean = np.mean(rng_(nb[200]) - rng_(wb))
        res = {}
        for nv in (40, 100):
            est = {"D200": [], "med": [], "rich": [], "cons": []}
            for _ in range(2000):
                idx = rng.integers(0, wb.shape[0], nv)
                w, s = wb[idx], sb[idx]
                d = noisy(w, s, c)
                r = {M: rng_(d[M]) for M in d}
                D200 = np.mean(r[200] - r[800]); D50 = np.mean(r[50] - r[800])
                est["D200"].append(D200)
                est["med"].append(np.median(r[200]) - np.median(r[800]))
                ratio = (D50 - D200) / D200 if D200 > 0 else np.nan
                p = np.log(ratio) / np.log(4) if ratio > 0 else np.nan
                est["rich"].append(D200 / (1 - 4.0 ** (-p)) if p == p and 0.3 <= p <= 1.5 else np.nan)
                est["cons"].append(2 * D200)
            res[nv] = {k: (np.nanmean(v), np.nanstd(v), np.mean(np.isnan(v))) for k, v in est.items()}
        print(f"c={c} sep={frac_sep}: true bias of median range at M=200: {truth_med:.4f} (mean per-state {truth_mean:.4f}); "
              f"F1-type bound 0.8636*h = {0.8636*1.96*np.median(sb):.4f}")
        for nv in (40, 100):
            print(f"   n_V4={nv}: " + "; ".join(f"{k} mean {m:.4f} sd {sd:.4f}" + (f" (undetermined {u:.2f})" if u else "")
                                          for k, (m, sd, u) in res[nv].items()))
