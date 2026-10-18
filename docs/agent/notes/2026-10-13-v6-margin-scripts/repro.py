"""Reproduce V6 of P0/P1 (DEV-0) bitwise and dump per-state step-halving deviations.

Usage: python -I repro.py <code_root> <cache_dir> <out.npz>
Read-only use of the library at <code_root>. DEVELOPMENT (DEV-0).
"""
import sys, time
from pathlib import Path
code_root, cache_dir, out = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
sys.path.insert(0, code_root)
import numpy as np, jax
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
from dataclasses import replace
from lpcstudy.config import PRESETS
from lpcstudy.data import build_context
from lpcstudy.systems import make_flow_step, simulate_trajectory
from lpcstudy.validation import check_integrator, check_cramer_rao
cfg = PRESETS["pilot"]
res = {}
for system in ("lorenz63", "rossler", "chua"):
    t0 = time.time()
    ctx = build_context(system, cfg, cache_dir)
    v6 = check_integrator(ctx)["integrator_max_dev_sigma"]
    coarse = make_flow_step(ctx.spec, ctx.spec.params, ctx.interval)
    fine = make_flow_step(replace(ctx.spec, max_dt=ctx.spec.max_dt / 2), ctx.spec.params, ctx.interval)
    per, argt = [], []
    idx = ctx.split_indices["test"][:20]
    for t in idx:
        a = simulate_trajectory(coarse, jnp.asarray(ctx.eval_states[t]), 31)
        b = simulate_trajectory(fine, jnp.asarray(ctx.eval_states[t]), 31)
        d = np.abs(a[:, 0] - b[:, 0]) / ctx.obs_scale
        per.append(d.max()); argt.append(int(d.argmax()))
    res[system] = dict(v6=v6, per=np.array(per), argt=np.array(argt),
                       states=ctx.eval_states[idx], obs_scale=ctx.obs_scale,
                       interval=ctx.interval, spacing=ctx.spacing, test_idx=idx)
    print(system, repr(v6), "per-state max", repr(max(per) ), f"{time.time()-t0:.1f}s", flush=True)
    print("  sorted per-state:", np.array2string(np.sort(per)[::-1], precision=3))
    print("  argmax step:", argt)
np.savez(out, **{f"{s}_{k}": v for s, d in res.items() for k, v in d.items()})
