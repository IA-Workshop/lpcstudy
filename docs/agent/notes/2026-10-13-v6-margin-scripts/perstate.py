"""Per-state V6 deviation D(s) on long attractor orbits (law of the V6 summand under mu).

D(s) = max_{j=0..30} |x_coarse_j(s) - x_fine_j(s)| / sigma_x, exactly as check_integrator,
vmapped. Orbits: n_orb independent orbits from registry start + 1e-3 N(0,I), 3000-step
burn-in, n_per states each. Literal seeds (scratch). DEVELOPMENT, no study seed.
Usage: python -I perstate.py <code_root> <cache_dir> <system> <n_orb> <n_per> <out.npz>
"""
import sys, time
from pathlib import Path
code_root, cache_dir, system, n_orb, n_per, out = sys.argv[1], Path(sys.argv[2]), sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
sys.path.insert(0, code_root)
import numpy as np, jax
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
from dataclasses import replace
from lpcstudy.config import PRESETS
from lpcstudy.data import lyapunov_record
from lpcstudy.systems import SYSTEMS, make_flow_step, simulate_trajectory
cfg = PRESETS["pilot"]
spec = SYSTEMS[system]
lam, _ = lyapunov_record(spec, cache_dir / "lyapunov.json")
interval = 1.0 / (cfg.steps_per_lyapunov * lam)
coarse = make_flow_step(spec, spec.params, interval)
fine = make_flow_step(replace(spec, max_dt=spec.max_dt / 2), spec.params, interval)
burn = 3000
stats = simulate_trajectory(coarse, jnp.asarray(spec.initial_state), burn + 200_000)[burn:]
sigma = float(stats[:, 0].std())
def dev(s):
    def body(c, _):
        a, b = c
        a, b = coarse(a), fine(b)
        return (a, b), jnp.abs(a[0] - b[0])
    _, d = jax.lax.scan(body, (s, s), None, length=30)
    return jnp.max(d)
devv = jax.jit(jax.vmap(dev))
rng = np.random.default_rng(14_0006)
D = []
t0 = time.time()
for o in range(n_orb):
    x0 = stats[rng.integers(0, len(stats))] + 1e-3 * rng.standard_normal(3)
    orb = simulate_trajectory(coarse, jnp.asarray(x0), burn + n_per)[burn:]
    d = np.concatenate([np.asarray(devv(jnp.asarray(orb[i:i + 20000]))) for i in range(0, n_per, 20000)])
    D.append(d / sigma)
    print(system, "orbit", o, f"max {d.max()/sigma:.3e}", f"{time.time()-t0:.0f}s", flush=True)
D = np.stack(D)
np.savez(out, D=D, sigma=sigma, interval=interval)
for c in (1e-4, 2e-4, 4.83e-4, 1e-3, 2e-3):
    print(f"  P(D>={c:g}) = {np.mean(D >= c):.3e}  count {np.sum(D >= c)}")
