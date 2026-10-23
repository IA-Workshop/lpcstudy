"""E2: candidate (iv) Benettin settings, and the Jacobian form.

Parameters OURS. Starts: (0.7, 0, 0) + 1e-3 k (1, 1, 1)/sqrt(3), k = 0..N-1;
the perturbations decorrelate within about 20 time units (lambda 0.43), so
after the burn-in of 300 time units at the level's own step the members are
independent orbits on the attractor. (A first version used time-shifted
points of one orbit; at h = 0.005 their windows overlapped and the SE was
understated. That version's output was discarded.)

(a) RK4 step h in {0.01, 0.005, 0.0025, 0.00125}: N = 32 independent members,
    interval 0.1, T = 2000 each. Independent ensembles per level, so the SE
    of a level difference is sqrt(SE1^2 + SE2^2).
(b)-(e) at h = 0.005, N = 16, T = 2000, on the SAME orbits as the baseline
    (QR every 0.1), so they are paired comparisons: re-orthonormalisation
    interval 0.01 and 1.0; two-trajectory Benettin (no Jacobian), d0 = 1e-8;
    deliberately wrong Jacobians ("swapped" slopes, "nohalf").
(f) burn-in 0 against 5000 intervals at T = 100, and the spread of the
    finite-time exponent at T = 100 and T = 2000.
"""
import json
import numpy as np
from chua_np import OURS, benettin_pair, benettin_qr

def starts(n):
    k = np.arange(n)[:, None]
    return np.array([0.7, 0.0, 0.0]) + 1e-3 * k * np.ones(3) / np.sqrt(3.0)

out = {}
def rep(tag, vals, extra=None):
    vals = np.asarray(vals)
    m, se = float(vals.mean()), float(vals.std(ddof=1) / np.sqrt(vals.size))
    out[tag] = {"mean": m, "se": se, "sd": float(vals.std(ddof=1)), "values": vals.tolist(), **(extra or {})}
    print(f"{tag:30s} mean {m:+.5f}  SE {se:.5f}  sd {vals.std(ddof=1):.5f}  min {vals.min():+.5f} max {vals.max():+.5f}", flush=True)

# (a)
for h in [0.01, 0.005, 0.0025, 0.00125]:
    r = benettin_qr(starts(32), OURS, dt=h, interval=0.1, burn=3000, n_int=20000)
    print("   diverged:", int(r["diverged"].sum()))
    rep(f"a_h={h}", r["lam"][~r["diverged"], 0], {"div": float(r["mean_div"].mean())})
# (b)-(e), paired
base = benettin_qr(starts(16), OURS, dt=0.005, interval=0.1, burn=3000, n_int=20000)
b0 = base["lam"][:, 0]
rep("base_h=0.005_iv=0.1", b0)
for iv, n in [(0.01, 200000), (1.0, 2000)]:
    r = benettin_qr(starts(16), OURS, dt=0.005, interval=iv, burn=int(round(300 / iv)), n_int=n)
    rep(f"b_interval={iv}", r["lam"][:, 0])
    rep(f"b_interval={iv}_minus_base", r["lam"][:, 0] - b0)
r = benettin_pair(starts(16), OURS, dt=0.005, interval=0.1, burn=3000, n_int=20000)
rep("d_pair_d0=1e-8", r["lam"])
rep("d_pair_minus_base", r["lam"] - b0)
for mode in ["swapped", "nohalf"]:
    r = benettin_qr(starts(16), OURS, dt=0.005, interval=0.1, burn=3000, n_int=20000, jac_mode=mode)
    rep(f"e_jac={mode}", r["lam"][:, 0], {"spectrum": r["lam"].mean(axis=0).tolist()})
# (f)
for burn in [0, 5000]:
    r = benettin_qr(starts(16), OURS, dt=0.005, interval=0.1, burn=burn, n_int=1000)
    rep(f"f_burn={burn}_T=100", r["lam"][:, 0])
json.dump(out, open("e2_benettin_settings.json", "w"), indent=1)
