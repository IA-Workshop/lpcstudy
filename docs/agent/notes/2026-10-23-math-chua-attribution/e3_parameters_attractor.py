"""E3: candidate (i) parameters and the attractor type.

Scan alpha at beta = 28 (m0, m1 OURS), beta at alpha = 15.6, the inner/outer
slopes exchanged, and the classical double-scroll set alpha = 9,
beta = 100/7. 4 starts each ((0.7,0,0); (0.01,0,0) near the origin; (1.51,0,-1.5) near
the outer equilibrium P+ = (1.5, 0, -1.5); (-0.5,-0.2,1); no two are mirror images), burn 2000 intervals,
T = 1000 (10 000 intervals of 0.1), h = 0.005. Records lambda_1, divergence,
the fraction of time with x > 0 and the number of scroll switches
(|x| > 1 on one side to |x| > 1 on the other). Diverged starts are counted.
"""
import json, numpy as np
from chua_np import *
starts = np.array([[0.7, 0.0, 0.0], [0.01, 0.0, 0.0], [1.51, 0.0, -1.5], [-0.5, -0.2, 1.0]])
cases = [(f"alpha={a}", {**OURS, "alpha": a}) for a in [8.0, 8.5, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 15.6, 16.0, 17.0, 18.0, 18.5, 19.0, 19.5, 20.0]]
cases += [(f"beta={b}", {**OURS, "beta": b}) for b in [20.0, 24.0, 26.0, 30.0, 32.0, 35.0]]
cases += [("slopes_swapped", {**OURS, "m0": OURS["m1"], "m1": OURS["m0"]}),
          ("classic_9_100/7", {"alpha": 9.0, "beta": 100 / 7, "m0": -8 / 7, "m1": -5 / 7})]
out = {}
for tag, p in cases:
    with np.errstate(all="ignore"):
        r = benettin_qr(starts, p, burn=2000, n_int=10000, bound=50.0)
    ok = ~r["diverged"]
    lam1 = r["lam"][ok, 0]
    out[tag] = {"params": p, "n_diverged": int((~ok).sum()), "lam1": lam1.tolist(),
                "pos_frac": r["pos_frac"][ok].tolist(), "switches": r["switches"][ok].tolist(),
                "maxabs_x": r["maxabs_x"][ok].tolist()}
    s = f"{tag:18s} diverged {int((~ok).sum())}/4"
    if ok.any():
        s += f"  lam1 {np.round(lam1, 4)}  pos_frac {np.round(r['pos_frac'][ok], 2)}  switches {r['switches'][ok]}  max|x| {np.round(r['maxabs_x'][ok], 2)}"
    print(s, flush=True)
json.dump(out, open("e3_parameters_attractor.json", "w"), indent=1)
