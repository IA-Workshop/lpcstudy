"""Scratch: V1 delay-Jacobian check with its internals saved (h, f(s+e), f(s-e), auto)."""
import json, sys, tempfile
from pathlib import Path
import numpy as np, jax, jax.numpy as jnp
from lpcstudy.config import PRESETS
from lpcstudy.data import build_context
from lpcstudy.dynamics import delay_map_forward
from lpcstudy.systems import make_flow_step
system, out = sys.argv[1], sys.argv[2]
RUN = "/home/brianm/projects/physics/chaos/lpcstudy-wt/run/pilot-dev0/runs/dev/wu0002-12/pilot/results.json"
lam = json.load(open(RUN))["systems"][system]["context"]["lambda_max"]
cache = Path(tempfile.mkdtemp(dir=Path(out).parent)); (cache / "lyapunov.json").write_text(json.dumps({system: lam}))
ctx = build_context(system, PRESETS["pilot"], cache)
step = make_flow_step(ctx.spec, ctx.spec.params, ctx.interval)
fwd = delay_map_forward(step, ctx.spec.observed_index, ctx.obs_mean, ctx.obs_scale, ctx.delay, ctx.embed_dim)
olds = ctx.eval_states[ctx.split_indices["test"][:10] - ctx.history]
scale = np.sqrt(np.diag(ctx.unwhiten @ ctx.unwhiten.T))
rec = {"scale": scale, "auto": [], "fp": [], "fm": [], "h": []}
for s_old in olds:
    rec["auto"].append(np.asarray(jax.jacfwd(fwd)(jnp.asarray(s_old))))
    for j in range(3):
        h = 1e-6 * scale[j]; e = np.zeros(3); e[j] = h
        rec["h"].append(h); rec["fp"].append(np.asarray(fwd(jnp.asarray(s_old + e)))); rec["fm"].append(np.asarray(fwd(jnp.asarray(s_old - e))))
np.savez(out, **{k: np.asarray(v) for k, v in rec.items()})
