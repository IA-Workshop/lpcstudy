"""V6-type RK4 step check for S1, S2, S3 (DEVELOPMENT, one thread).

For each candidate max_dt: the flow map over Delta = 1/(30 lambda) with
ceil(Delta/max_dt) substeps against the same with max_dt/2, 20 attractor
states, 30 steps (1 LT); the QoI is max |x_coarse - x_fine| / sigma_x, the
code's V6 statistic (gate: < 1e-3). The observed order uses three levels
h, h/2, h/4 on the same states (convergence-study skill, step 4).
"""

import math
import sys
from dataclasses import replace

import jax.numpy as jnp
import numpy as np

from lpcstudy.systems import lyapunov_guarded, make_flow_step, simulate_trajectory

from ext_common import CANDIDATES

LT = 30
GRID = {"S1": [0.02, 0.01, 0.005, 0.0025], "S2": [0.008, 0.004, 0.002, 0.001], "S3": [0.08, 0.04, 0.02]}

which = sys.argv[1:] or list(CANDIDATES)
for key in which:
    sp = CANDIDATES[key]()
    lam, _ = lyapunov_guarded(sp, 20 * sp.max_dt, 100_000, 5_000)
    interval = 1.0 / (LT * lam)
    step = make_flow_step(sp, sp.params, interval)
    orbit = simulate_trajectory(step, jnp.asarray(sp.initial_state), 3000 + 20_000)[3000:]
    scale = float(orbit[:, sp.observed_index].std())
    states = orbit[::1000][:20]
    print(f"[{key}] {sp.name}: Delta {interval:.6f}, sigma_x {scale:.4f}, 20 states, 30 steps")

    def run(max_dt):
        f = make_flow_step(replace(sp, max_dt=max_dt), sp.params, interval)
        return np.stack([simulate_trajectory(f, jnp.asarray(s), LT + 1)[:, sp.observed_index] for s in states])

    levels = GRID[key] + [GRID[key][-1] / 2, GRID[key][-1] / 4]
    paths = {h: run(h) for h in levels}
    print(f"  {'max_dt':>8s} {'substeps':>8s} {'V6 stat (h vs h/2)/sigma_x':>28s} {'gate <1e-3':>10s}")
    for h in GRID[key]:
        dev = np.max(np.abs(paths[h] - paths[h / 2])) / scale
        print(f"  {h:8.4f} {math.ceil(interval/h):8d} {dev:28.3e} {'pass' if dev < 1e-3 else 'FAIL':>10s}")
    print("  observed order p from (h, h/2, h/4) on the max-abs deviation at 1 LT:")
    for h in GRID[key]:
        d1 = np.max(np.abs(paths[h] - paths[h / 2]))
        d2 = np.max(np.abs(paths[h / 2] - paths[h / 4]))
        p = math.log(d1 / d2) / math.log(2) if d2 > 0 else float("nan")
        print(f"    h {h:.4f}: |q_h - q_h/2| {d1/scale:.3e}, |q_h/2 - q_h/4| {d2/scale:.3e}, p {p:.2f}, Richardson error at h/2: {d2/scale/(2**p-1) if d2>0 else 0:.2e} sigma_x")
    print()
