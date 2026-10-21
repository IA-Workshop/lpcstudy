"""V1 of S4 on the code's real context, with the implementation's own code
(PYTHONPATH = the wu/ext-impl2 worktree; DEVELOPMENT, one thread): the code's
check_jacobians, then per test state the AD gain g_H (H = 30), the FD gain at
steps h = 1e-4 ... 1e-7 (whitened), and the delay-map Jacobian FD error for
step factors 1e-4 ... 1e-8. A V-shape in h (truncation at large h, round-off at
small h) with a minimum below 1e-4 means the AD Jacobian is right and the gate
statistic is a finite-difference resolution effect at the code's fixed step;
a flat error means a Jacobian discrepancy. Also: my field against the code's
field at 1000 orbit states (max abs difference)."""

import sys
import tempfile
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np

from lpcstudy.config import SMOKE
from lpcstudy.data import build_context
from lpcstudy.dynamics import delay_map_forward, make_amplification
from lpcstudy.systems import SYSTEMS, make_flow_step, simulate_trajectory
from lpcstudy.validation import check_jacobians

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ext_common import hindmarsh_rose_field  # noqa: E402

spec = SYSTEMS["hindmarsh_rose"]
print("code spec:", spec.params, spec.max_dt, spec.orbit_bound, getattr(spec, "lyapunov_steps", None))
ctx = build_context("hindmarsh_rose", SMOKE, Path(tempfile.mkdtemp(prefix="v1s4-")))
print(f"context: lambda {ctx.lambda_max!r}, Delta {ctx.interval:.6f}, delay {ctx.delay}, sigma_x {ctx.obs_scale:.4f}")
v1 = check_jacobians(ctx)
print("code check_jacobians:", v1)

# field comparison
orbit = ctx.eval_states[:1000]
mine = np.asarray(jax.vmap(lambda s: hindmarsh_rose_field(s, spec.params))(jnp.asarray(orbit)))
code = np.asarray(jax.vmap(lambda s: spec.field_fn(s, spec.params))(jnp.asarray(orbit)))
print(f"field: max |mine - code| = {np.max(np.abs(mine - code)):.3e} (max |field| {np.max(np.abs(code)):.3e}); bitwise equal rows {int(np.all(mine == code, axis=1).sum())} of 1000")

step = make_flow_step(spec, spec.params, ctx.interval)
times = ctx.split_indices["test"][:10]
amp = make_amplification(step, 0, ctx.obs_scale, ctx.unwhiten, 30)
states = ctx.eval_states[times]
gains = np.asarray(amp(jnp.asarray(states)))[:, -1]


def obs_after(s):
    return float(simulate_trajectory(step, jnp.asarray(s), 31)[-1, 0]) / ctx.obs_scale


hs = [1e-4, 3e-5, 1e-5, 3e-6, 1e-6, 3e-7, 1e-7]
print("gain FD relative error per state (rows: states with g_H; columns h):", hs)
worst = {h: 0.0 for h in hs}
for state, gain in zip(states, gains):
    errs = []
    for h in hs:
        row = np.zeros(3)
        for j in range(3):
            d = ctx.unwhiten[:, j]
            row[j] = (obs_after(state + h * d) - obs_after(state - h * d)) / (2 * h)
        e = abs(np.linalg.norm(row) - gain) / gain
        errs.append(e)
        worst[h] = max(worst[h], e)
    print(f"   g_H {gain:9.2f} x {state[0]:+.3f}: " + " ".join(f"{e:.1e}" for e in errs))
print("   worst over states:", " ".join(f"{worst[h]:.1e}" for h in hs), "(code uses h = 1e-6)")

fwd = delay_map_forward(step, 0, ctx.obs_mean, ctx.obs_scale, ctx.delay, ctx.embed_dim)
scale = np.sqrt(np.diag(ctx.unwhiten @ ctx.unwhiten.T))
olds = ctx.eval_states[times - ctx.history]
facs = [1e-4, 1e-5, 1e-6, 1e-7, 1e-8]
print("delay-map Jacobian FD relative error, worst over 10 states; columns step factor:", facs)
w = {f: 0.0 for f in facs}
for s_old in olds:
    auto = np.asarray(jax.jacfwd(fwd)(jnp.asarray(s_old)))
    for f in facs:
        fd = np.zeros_like(auto)
        for j in range(3):
            h = f * scale[j]
            e = np.zeros_like(s_old); e[j] = h
            fd[:, j] = (np.asarray(fwd(jnp.asarray(s_old + e))) - np.asarray(fwd(jnp.asarray(s_old - e)))) / (2 * h)
        w[f] = max(w[f], float(np.max(np.abs(auto - fd)) / np.max(np.abs(auto))))
print("   ", " ".join(f"{w[f]:.1e}" for f in facs), "(code uses factor 1e-6)")
