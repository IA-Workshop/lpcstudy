"""Scratch (WU-0001.6 M1-M5): build the statistics trajectory exactly as data.build_context
(lines 259-269) for each system with the pilot run's lambda (preset-independent), save it."""
import json, sys, hashlib
from pathlib import Path
import numpy as np, jax.numpy as jnp
from lpcstudy.config import PRESETS
from lpcstudy.systems import SYSTEMS, make_flow_step, simulate_trajectory
out = Path(sys.argv[1])
lam_all = {'lorenz63': 0.9054940534657817, 'rossler': 0.07193978510879935, 'chua': 0.43113260161336364}
cfg = PRESETS["smoke"]
for system, lam in lam_all.items():
    spec = SYSTEMS[system]
    interval = 1.0 / (cfg.steps_per_lyapunov * lam)
    step_fn = make_flow_step(spec, spec.params, interval)
    burn = int(cfg.burn_in_lyapunov * cfg.steps_per_lyapunov)
    stats_j = simulate_trajectory(step_fn, jnp.asarray(spec.initial_state), burn + 200_000)
    stats = stats_j[burn:]
    print(system, type(stats_j).__name__, stats.dtype, stats.shape, stats.flags['C_CONTIGUOUS'],
          stats.flags['OWNDATA'], stats.flags['WRITEABLE'], hashlib.sha256(stats.tobytes()).hexdigest()[:16])
    np.save(out / f"stats_{system}.npy", stats)
