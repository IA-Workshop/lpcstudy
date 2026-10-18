"""Median statistic (H2a(i)-like): discreteness of the bootstrap distribution, ties at q +- d, calibration."""
import numpy as np, time
n, block, B, R = 500, 5, 2000, 100
levels = (0.95, 1 - 0.05/3)
rng = np.random.default_rng(4242)
def stat_factory(spread, eligible):
    def stat(idx):
        rows = idx[eligible[idx]]
        return np.median(spread[rows])
    return stat
def boots(stat, rng):
    starts = rng.integers(0, n-block+1, (B, n//block))
    idx = (starts[:, :, None] + np.arange(block)).reshape(B, n)
    return np.array([stat(i) for i in idx])
for atom in (0.0, 0.2, 0.45):
    ties = np.zeros(4); lmed = []; ndist = []
    for k in range(10):
        eligible = rng.random(n) < 0.68
        spread = np.where(rng.random(n) < atom, 0.0, np.exp(rng.normal(np.log(0.15), 0.8, n)))
        stat = stat_factory(spread, eligible)
        res = []
        for r in range(R):
            v = boots(stat, rng); ndist.append(len(np.unique(v)))
            row = []
            for L in levels:
                a = (1-L)/2
                for q in (a, 1-a):
                    d = np.sqrt(q*(1-q)/B)
                    lo_, hi_ = np.quantile(v, q-d), np.quantile(v, q+d)
                    row.append((np.quantile(v, q), (hi_-lo_)/2))
            res.append(row)
        res = np.array(res)
        ties += (res[:, :, 1] == 0).mean(0)/10
        ref = res[:, :, 0].std(0, ddof=1)
        lmed.append(np.log(np.median(res[:, :, 1], 0)/ref))
    lmed = np.array(lmed)
    print(f"atom {atom}: distinct bootstrap values per B=2000: median {np.median(ndist):.0f}; P(SE=0) per endpoint {ties.round(4)}; median ratio over data sets {np.exp(lmed).mean(0).round(3)} min {np.exp(lmed.min(0)).round(3)} max {np.exp(lmed.max(0)).round(3)}")
