"""Scratch: conditioning of nu (V2 denominator) and of the V2 error at the five V2 states;
response of nu^2 to 1-ulp perturbations of the delay-map Jacobian rows (numpy reference)."""
import json, sys, tempfile
from pathlib import Path
import numpy as np, jax, jax.numpy as jnp
from lpcstudy.config import PRESETS
from lpcstudy.data import build_context
from lpcstudy.dynamics import delay_map_forward
from lpcstudy.systems import make_flow_step
system = sys.argv[1]
RUN = "/home/brianm/projects/physics/chaos/lpcstudy-wt/run/pilot-dev0/runs/dev/wu0002-12/pilot/results.json"
lam = json.load(open(RUN))["systems"][system]["context"]["lambda_max"]
cache = Path(tempfile.mkdtemp(dir=sys.argv[2])); (cache / "lyapunov.json").write_text(json.dumps({system: lam}))
ctx = build_context(system, PRESETS["pilot"], cache)
step = make_flow_step(ctx.spec, ctx.spec.params, ctx.interval)
fwd = delay_map_forward(step, ctx.spec.observed_index, ctx.obs_mean, ctx.obs_scale, ctx.delay, ctx.embed_dim)
jac = jax.jit(jax.jacfwd(fwd))
adv = jax.jit(jax.jacfwd(lambda s: jax.lax.fori_loop(0, ctx.history, lambda _, x: step(x), s)))
rng = np.random.default_rng(0)
for t in ctx.split_indices["test"][:5]:
    s_old = ctx.eval_states[t - ctx.history]
    A = np.asarray(jac(jnp.asarray(s_old))); Q = np.asarray(adv(jnp.asarray(s_old)))
    W = ctx.whiten
    nu2 = lambda A: np.trace(W @ Q @ np.linalg.inv(A.T @ A) @ Q.T @ W.T)
    base = nu2(A)
    d = [abs(nu2(A * (1 + rng.choice([-1, 1], A.shape) * 2.2e-16)) / base - 1) for _ in range(200)]
    print(f"{system} t={t}: kappa(A)={np.linalg.cond(A):.1e} kappa(AtA)={np.linalg.cond(A.T@A):.1e} "
          f"nu={np.sqrt(base):.3g}  |d nu^2/nu^2| from 1-ulp A: median {np.median(d):.1e} max {np.max(d):.1e}")
