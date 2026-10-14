"""M5: synthetic check of the primary D5 estimator (split halves over all eligible test states).

Same model as m5_d5sim.py. Halves A, B have draw-noise SD s*sqrt(2) each (100 draws); the 200-draw
estimate has noise (e_A + e_B)/2 (first order: w* is a ratio of the pooled moments).
B_hat(200) = 2.414 * [ (med r_A + med r_B)/2 - med r_200 ]  (Richardson, order 1/2).
Truth: bias of the median range at M = 200 against M = infinity (2e5 states).
Also: the D2 union trigger P(V*(10)/V*(5) > 1.1 or V*(20)/V*(5) > 1.15) per series (M4).
Synthetic (seed 20261017): not a DEV or CONF seed.
"""
import numpy as np
rng = np.random.default_rng(20261017)

def states(n, frac_sep):
    base = rng.uniform(0.05, 0.6, n)
    base[rng.random(n) < 0.3] = 0.0
    spread = rng.exponential(0.15, (n, 3)) * rng.choice([-1, 1], (n, 3))
    spread[rng.random(n) < frac_sep] = 0.0
    return np.clip(base[:, None] + spread, 0, 1), 0.017 * np.exp(0.5 * rng.standard_normal(n))

def halves(w, s, c):
    n = w.shape[0]
    L = np.linalg.cholesky(np.full((3, 3), c) + (1 - c) * np.eye(3))
    eA = rng.standard_normal((n, 3)) @ L.T * s[:, None] * np.sqrt(2)
    eB = rng.standard_normal((n, 3)) @ L.T * s[:, None] * np.sqrt(2)
    f = lambda e: np.clip(w + e, 0, 1)
    return f(eA), f(eB), f((eA + eB) / 2)

rg = lambda x: x.max(1) - x.min(1)
for c in (0.0, 0.5, 0.9):
    for sep in (0.2, 0.6):
        wb, sb = states(200000, sep)
        _, _, w200 = halves(wb, sb, c)
        truth = np.median(rg(w200)) - np.median(rg(wb))
        line = f"c={c} sep={sep}: truth {truth:+.4f}"
        for n in (320, 650, 930):
            est = []
            for _ in range(2000):
                i = rng.integers(0, wb.shape[0], n)
                a, b, m = halves(wb[i], sb[i], c)
                est.append(2.414 * (0.5 * (np.median(rg(a)) + np.median(rg(b))) - np.median(rg(m))))
            est = np.array(est)
            line += f" | n={n}: mean {est.mean():+.4f} sd {est.std():.4f}"
        print(line)

# D2 union trigger per series (Gaussian AR(1) influence series)
def ar1(n, a, R):
    e = rng.standard_normal((R, n)); x = np.empty((R, n)); x[:, 0] = e[:, 0]
    for t in range(1, n):
        x[:, t] = a * x[:, t - 1] + np.sqrt(1 - a * a) * e[:, t]
    return x
def vstar(x, b):
    cs = np.cumsum(np.concatenate([np.zeros((x.shape[0], 1)), x], 1), 1)
    return b * ((cs[:, b:] - cs[:, :-b]) / b).var(1)
for n in (300, 500, 1000):
    for a in (0.0, 0.3):
        x = ar1(n, a, 4000)
        v5, v10, v20 = vstar(x, 5), vstar(x, 10), vstar(x, 20)
        u = np.mean((v10 / v5 > 1.1) | (v20 / v5 > 1.15))
        print(f"D2 union trigger n={n} phi={a}: {u:.3f}")
