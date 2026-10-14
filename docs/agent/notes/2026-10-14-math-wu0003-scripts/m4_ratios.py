"""M4: sampling law of the C8/C9 diagnostics on an influence series of length n.

D1: lag-1 sample autocorrelation; D2: exact (B-free) moving-block bootstrap variance of the mean,
V*(b) = b * var(means of the n-b+1 overlapping blocks of length b), and the ratios V*(10)/V*(5),
V*(20)/V*(5). Series: AR(1) with lag-1 a (Gaussian innovations) and, as a heavy-tailed case, the
log-normal transform exp(2 g) - E of a Gaussian AR(1) g (its own lag-1 is smaller than a).
Also E V*(5) / long-run variance (the first-order coverage driver).
Synthetic (scratch seed 20261014): not a DEV or CONF seed.
"""
import numpy as np
rng = np.random.default_rng(20261014)
R = 4000

def ar1(n, a, R):
    e = rng.standard_normal((R, n))
    x = np.empty((R, n)); x[:, 0] = e[:, 0]
    s = np.sqrt(1 - a * a)
    for t in range(1, n):
        x[:, t] = a * x[:, t - 1] + s * e[:, t]
    return x

def vstar(x, b):
    c = np.cumsum(np.concatenate([np.zeros((x.shape[0], 1)), x], axis=1), axis=1)
    bm = (c[:, b:] - c[:, :-b]) / b
    return b * bm.var(axis=1)

def acf1(x):
    xc = x - x.mean(axis=1, keepdims=True)
    return (xc[:, 1:] * xc[:, :-1]).sum(1) / (xc * xc).sum(1)

def lrv_ar1(a):
    return (1 + a) / (1 - a)

print("case        n     a   acf1 mean (sd)     P|acf1|>.15  R10 mean (sd)   P(R10>1.1)  R20 mean (sd)   P(R20>1.15)  E V5/LRV")
for kind in ("gauss", "lognorm"):
    for n in (300, 500, 1000):
        for a in (0.0, 0.15, 0.3):
            g = ar1(n, a, R)
            x = g if kind == "gauss" else np.exp(2 * g)
            r1 = acf1(x)
            v5, v10, v20 = vstar(x, 5), vstar(x, 10), vstar(x, 20)
            R10, R20 = v10 / v5, v20 / v5
            if kind == "gauss":
                lrv = lrv_ar1(a)
            else:
                # long-run variance of exp(2g): sum of autocovariances e^{4}(e^{4 a^k}-1)
                k = np.arange(1, 400)
                gam0 = np.exp(4) * (np.exp(4) - 1)
                lrv = gam0 + 2 * (np.exp(4) * (np.exp(4 * a ** k) - 1)).sum()
            ev5 = v5.mean() / lrv
            print(f"{kind:8s} {n:5d} {a:5.2f}  {r1.mean():+.3f} ({r1.std():.3f})   {np.mean(abs(r1)>.15):.3f}      "
                  f"{R10.mean():.3f} ({R10.std():.3f})  {np.mean(R10>1.1):.3f}       {R20.mean():.3f} ({R20.std():.3f})  "
                  f"{np.mean(R20>1.15):.3f}       {ev5:.3f}")
