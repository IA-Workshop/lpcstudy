"""Self-consistency check of the S4 field as integrated (DEVELOPMENT): the
time average of the divergence -1 + (2 b x - 3 a x^2)/tx - 1/tz along a long
orbit must equal the sum of the Lyapunov spectrum (0.21635 + 0.00002 - 6.36303
= -6.1467 from spectra_s456.log)."""

import jax.numpy as jnp
import numpy as np

from lpcstudy.systems import make_flow_step, simulate_trajectory

from ext_common import CANDIDATES

sp = CANDIDATES["S4"]()
p = sp.params
step = make_flow_step(sp, sp.params, 0.1)
orbit = simulate_trajectory(step, jnp.asarray(sp.initial_state), 5000 + 1_000_000)[5000:]
x = orbit[:, 0]
div = -1 + (2 * p["b"] * x - 3 * p["a"] * x**2) / p["tx"] - 1 / p["tz"]
blocks = div.reshape(50, -1).mean(axis=1)
print(f"S4 orbit-average divergence {div.mean():.4f} +- {blocks.std(ddof=1)/np.sqrt(50):.4f} (10^5 time units); spectrum sum -6.1467 +- 0.011")
print(f"   orbit mean/std of (x, y, z): {np.round(orbit.mean(axis=0), 4).tolist()} / {np.round(orbit.std(axis=0), 4).tolist()}; Dysts entry mean (0.0030, -0.1060, 0.0289), std (0.3265, 0.1481, 0.1180)")
