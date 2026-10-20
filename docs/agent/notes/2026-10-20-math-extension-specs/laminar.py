"""S2 laminar-phase statistics (DEVELOPMENT): successive maxima of z on a
long orbit; a step of the return map with |z_max(n+1) - z_max(n)| below a
threshold is 'laminar' (the orbit shadows the ghost of the r < 166.07 limit
cycle, Manneville & Pomeau 1980). Reports the fraction of cycles that are
laminar, the mean cycle period, and the run-length distribution of laminar
phases in LT, for three thresholds."""

import sys

import jax.numpy as jnp
import numpy as np

from lpcstudy.systems import lyapunov_guarded, make_flow_step, simulate_trajectory

from ext_common import CANDIDATES

LT = 30
from dataclasses import replace
import os
sp = CANDIDATES["S2"]()
if os.environ.get("R166"):
    sp = replace(sp, params={"sigma": 10.0, "rho": float(os.environ["R166"]), "beta": 8.0 / 3.0})
print("r =", sp.params["rho"])
lam, _ = lyapunov_guarded(sp, 20 * sp.max_dt, 100_000, 5_000)
lam = max(lam, 0.62)  # the control at r = 166.0 has lambda 0; keep Delta of r = 166.1
interval = 1.0 / (LT * lam)
step = make_flow_step(sp, sp.params, interval)
orbit = simulate_trajectory(step, jnp.asarray(sp.initial_state), 3000 + 600_000)[3000:]
z = orbit[:, 2]
peaks = np.nonzero((z[1:-1] > z[:-2]) & (z[1:-1] >= z[2:]))[0] + 1
zmax = z[peaks]
period = np.diff(peaks).mean() * interval
print(f"S2: {len(orbit)} steps = {len(orbit)*interval:.0f} time units; {len(peaks)} z-maxima; mean cycle {period:.3f} time units = {period*lam:.2f} LT")
print(f"  z_max quantiles 1/50/99% {np.array2string(np.quantile(zmax, [.01,.5,.99]), precision=2)}")
lag = 2  # the cycle has two distinct z-maxima per period (control r = 166.0)
d = np.abs(zmax[lag:] - zmax[:-lag])
print(f"  lag {lag} differences of z_max; lag-1 median {np.median(np.abs(np.diff(zmax))):.2f}, lag-2 median {np.median(np.abs(zmax[2:]-zmax[:-2])):.2f}")
# a stretch of successive maxima, to see the pattern
print("  first 40 z_max:", np.array2string(zmax[:40], precision=1, max_line_width=200))
# count runs where lag-2 differences stay below thr

for thr in (0.25, 0.5, 1.0, 2.0):
    lam_flag = d < thr
    runs, cur = [], 0
    for f in lam_flag:
        if f:
            cur += 1
        else:
            if cur:
                runs.append(cur)
            cur = 0
    if cur:
        runs.append(cur)
    runs = np.array(runs)
    print(f"  threshold {thr}: laminar fraction of cycles {lam_flag.mean():.3f}; {len(runs)} laminar phases; length (cycles) median {np.median(runs):.0f}, "
          f"p90 {np.quantile(runs, .9):.0f}, max {runs.max()}; median length {np.median(runs)*period*lam:.1f} LT; mean {runs.mean()*period*lam:.1f} LT")
hist, edges = np.histogram(d, bins=[0, 0.1, 0.25, 0.5, 1, 2, 5, 10, 50, 300])
print("  |dz_max| histogram edges", edges.tolist(), "counts", hist.tolist())
