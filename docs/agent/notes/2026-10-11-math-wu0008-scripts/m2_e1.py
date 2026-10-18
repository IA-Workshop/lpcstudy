"""WU-0008 M2/E1: endpoint SE on the deterministic grid Phi^-1((i - 1/2)/B) against sqrt(q(1-q)/B)/phi(z_q).

Prints the relative deviation of SE = (Q(q+d) - Q(q-d))/2, d = sqrt(q(1-q)/B), Q = np.quantile (linear), and the
pure curvature part (continuous quantile function, no grid). CPU, deterministic, < 1 s.
"""
import numpy as np
from statistics import NormalDist
N = NormalDist()
for B in (2000, 500, 50):
    v = np.array([N.inv_cdf((i - 0.5) / B) for i in range(1, B + 1)])
    for level in (0.95, 1 - 0.05 / 3):
        a = (1 - level) / 2
        for q in (a, 1 - a):
            d = np.sqrt(q * (1 - q) / B)
            ref = d / N.pdf(N.inv_cdf(q))
            if q - d <= 0 or q + d >= 1:
                print(f"B={B} level={level:.5f} q={q:.5f} d*B={d*B:.2f}: q +- d leaves (0, 1) -> None")
                continue
            se = (np.quantile(v, q + d) - np.quantile(v, q - d)) / 2
            curv = (N.inv_cdf(q + d) - N.inv_cdf(q - d)) / 2 / ref - 1
            print(f"B={B} level={level:.5f} q={q:.5f} d*B={d*B:.2f} se={se:.6g} ref={ref:.6g} "
                  f"rel={se/ref-1:+.4%} (curvature only {curv:+.4%})")
