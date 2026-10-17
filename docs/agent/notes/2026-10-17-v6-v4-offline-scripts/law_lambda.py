"""V6 law at a given Lyapunov cache (CPU or GPU lambda), on a deterministic orbit (no random number).

The orbit is the continuation of the production statistics orbit (registry initial state,
production burn-in, 200 000 statistics steps) for a further 10^6 + 600 steps; D(s) is the
per-state step-halving deviation exactly as check_integrator (vmapped, as perstate.py of the
2026-10-13 note). The 10^6 states are cut into 5 consecutive segments of 2e5 (the 'orbits' of the
block summaries). V6 law by sliding 20-state windows at the production spacing, as law.py.
DEVELOPMENT; no seed of any kind is used.

Usage: python -I law_lambda.py <code_root> <cache_dir> <system> <spacing> <out.npz>
"""
import sys
import time
from pathlib import Path

code_root, cache_dir, system, spacing, out = (sys.argv[1], Path(sys.argv[2]), sys.argv[3],
                                              int(sys.argv[4]), sys.argv[5])
sys.path.insert(0, code_root)
import numpy as np  # noqa: E402
import jax  # noqa: E402

jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp  # noqa: E402
from dataclasses import replace  # noqa: E402
from lpcstudy.config import PRESETS  # noqa: E402
from lpcstudy.data import lyapunov_record  # noqa: E402
from lpcstudy.systems import SYSTEMS, make_flow_step, simulate_trajectory  # noqa: E402

cfg = PRESETS["pilot"]
spec = SYSTEMS[system]
lam, _ = lyapunov_record(spec, cache_dir / "lyapunov.json")
interval = 1.0 / (cfg.steps_per_lyapunov * lam)
coarse = make_flow_step(spec, spec.params, interval)
fine = make_flow_step(replace(spec, max_dt=spec.max_dt / 2), spec.params, interval)
burn = int(cfg.burn_in_lyapunov * cfg.steps_per_lyapunov)
t0 = time.time()
stats = simulate_trajectory(coarse, jnp.asarray(spec.initial_state), burn + 200_000)[burn:]
sigma = float(stats[:, spec.observed_index].std())
n_states = 1_000_000
orb = simulate_trajectory(coarse, jnp.asarray(stats[-1]), n_states + 1)[1:]


def dev(s):
    def body(c, _):
        a, b = c
        a, b = coarse(a), fine(b)
        return (a, b), jnp.abs(a[spec.observed_index] - b[spec.observed_index])
    _, d = jax.lax.scan(body, (s, s), None, length=30)
    return jnp.max(d)


devv = jax.jit(jax.vmap(dev))
D = np.concatenate([np.asarray(devv(jnp.asarray(orb[i:i + 20000])))
                    for i in range(0, n_states, 20000)]) / sigma
D = D.reshape(5, n_states // 5)
span = 19 * spacing + 1
V = np.stack([np.lib.stride_tricks.sliding_window_view(D[o], span)[:, ::spacing].max(axis=1)
              for o in range(5)])
allV = V.ravel()
seg_p = np.array([np.mean(V[o] >= 1e-3) for o in range(5)])
print(f"{system} lambda {lam!r} interval {interval:.6f} sigma {sigma:.6f} "
      f"n_c {int(np.ceil(interval / spec.max_dt))} ({time.time() - t0:.0f}s)")
print(f"  per-state: median {np.median(D):.3e} 99.9% {np.quantile(D, .999):.3e} max {D.max():.3e} "
      f"mu(D>=1e-3) {np.mean(D >= 1e-3):.3e} ({int(np.sum(D >= 1e-3))} states)")
print("  V6 law: " + " ".join(f"{q:g}:{np.quantile(allV, q):.3e}" for q in (.5, .9, .95, .99, .999))
      + f"  P(V6>=1e-3) {allV.__ge__(1e-3).mean():.4e}  per-segment {np.round(seg_p, 4)} "
      f"(SD/sqrt5 {seg_p.std(ddof=1) / np.sqrt(5):.4f})")
np.savez(out, D=D, sigma=sigma, interval=interval, lam=lam)
