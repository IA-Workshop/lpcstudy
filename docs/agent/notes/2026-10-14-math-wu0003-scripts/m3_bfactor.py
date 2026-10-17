"""M3: effect of B (500 -> 2000) on the expected percentile half-width, and on its noise.

hw_B = (Q(1-a) - Q(a)) / 2 with np.quantile (linear) of B draws of the bootstrap distribution,
here N(0,1) and a skewed law (log-normal sigma 0.5, standardized). Synthetic, seed 20261015.
"""
import numpy as np
rng = np.random.default_rng(20261015)
R = 20000
for law in ("normal", "lognormal0.5"):
    for level in (0.95, 1 - 0.05 / 3):
        a = (1 - level) / 2
        if law == "normal":
            from statistics import NormalDist
            true = NormalDist().inv_cdf(1 - a)
        else:
            from statistics import NormalDist
            z = NormalDist().inv_cdf
            true = (np.exp(0.5 * z(1 - a)) - np.exp(0.5 * z(a))) / 2
        out = []
        for B in (500, 2000):
            x = rng.standard_normal((R, B))
            if law != "normal":
                x = np.exp(0.5 * x)
            q = np.quantile(x, [a, 1 - a], axis=1)
            hw = (q[1] - q[0]) / 2
            out.append((B, hw.mean() / true, hw.std() / true))
        print(f"{law:13s} level {level:.4f}: " + "; ".join(f"B={B}: E hw/true {m:.4f}, sd {s:.4f}" for B, m, s in out)
              + f"; ratio E(2000)/E(500) = {out[1][1]/out[0][1]:.4f}")
