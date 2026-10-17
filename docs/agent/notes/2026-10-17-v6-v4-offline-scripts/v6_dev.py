"""V6 gate statistic on registered development seeds, exactly as the production gate (DEF-0026).

For each seed id (registry, DEV-n only), preset and system: build the production context with
``build_context`` (seed from ``seeds/development_seeds.json`` via ``load_registry`` and
``resolve_dev_seed``; every random stream inside comes from ``make_rng(seed, ...)``), evaluate
``validation.check_integrator(ctx)`` (the gated value), and dump the 20 per-state deviations
D(s_i) exactly as repro.py of the 2026-10-13 note. No other randomness. CPU only.

DEVELOPMENT (DEV-0 for the bitwise P1 check; DEV-1 to DEV-4 for the new draws). Never the
confirmatory seed (the script refuses any id that is not DEV-n through resolve_dev_seed).

Usage: python -I v6_dev.py <code_root> <cache_dir> <out.npz> <preset[,preset]> <DEV-a[,DEV-b]>
"""
import sys
import time
from pathlib import Path

code_root, cache_dir, out = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
presets, seed_ids = sys.argv[4].split(","), sys.argv[5].split(",")
sys.path.insert(0, code_root)
import numpy as np  # noqa: E402
import jax  # noqa: E402

jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp  # noqa: E402
from dataclasses import replace  # noqa: E402
from lpcstudy.config import PRESETS  # noqa: E402
from lpcstudy.data import build_context  # noqa: E402
from lpcstudy.seeds import REGISTRY_PATH, load_registry, resolve_dev_seed, with_seed  # noqa: E402
from lpcstudy.systems import make_flow_step, simulate_trajectory  # noqa: E402
from lpcstudy.validation import check_integrator  # noqa: E402

assert all(s.startswith("DEV-") for s in seed_ids), "development ids only (LPC.PC.7)"
registry = load_registry(REGISTRY_PATH)
print("registry", REGISTRY_PATH, "jax", jax.__version__, "devices", jax.devices(), flush=True)
res = {}
for preset in presets:
    for seed_id in seed_ids:
        cfg = with_seed(PRESETS[preset], seed_id, resolve_dev_seed(seed_id, registry))
        for system in ("lorenz63", "rossler", "chua"):
            t0 = time.time()
            ctx = build_context(system, cfg, cache_dir)
            v6 = check_integrator(ctx)["integrator_max_dev_sigma"]
            coarse = make_flow_step(ctx.spec, ctx.spec.params, ctx.interval)
            fine = make_flow_step(replace(ctx.spec, max_dt=ctx.spec.max_dt / 2),
                                  ctx.spec.params, ctx.interval)
            idx = ctx.split_indices["test"][:20]
            per, argt = [], []
            for t in idx:
                a = simulate_trajectory(coarse, jnp.asarray(ctx.eval_states[t]), 31)
                b = simulate_trajectory(fine, jnp.asarray(ctx.eval_states[t]), 31)
                d = np.abs(a[:, ctx.spec.observed_index] - b[:, ctx.spec.observed_index]) \
                    / ctx.obs_scale
                per.append(d.max())
                argt.append(int(d.argmax()))
            per = np.array(per)
            n_c = int(np.ceil(ctx.interval / ctx.spec.max_dt))
            n_f = int(np.ceil(ctx.interval / (ctx.spec.max_dt / 2)))
            key = f"{preset}|{seed_id}|{system}"
            res[key] = dict(v6=v6, per=per, argt=np.array(argt), test_idx=np.array(idx),
                            spacing=ctx.spacing, interval=ctx.interval, obs_scale=ctx.obs_scale,
                            n_c=n_c, n_f=n_f, main_digest=ctx.meta["main_digest"],
                            start_index=ctx.meta["start_index"]["main"])
            print(f"{key:28s} V6 {v6!r}  per-state max {per.max()!r}  equal {per.max() == v6}  "
                  f"test[0] {idx[0]} test[19] {idx[-1]} spacing {ctx.spacing} n_c/n_f {n_c}/{n_f}"
                  f"  main_digest {ctx.meta['main_digest'][:16]}  {time.time() - t0:.1f}s",
                  flush=True)
            print("    sorted per-state:", np.array2string(np.sort(per)[::-1][:5], precision=3),
                  " argmax step of the max:", argt[int(per.argmax())], flush=True)
np.savez(out, **{f"{k}#{f}": np.asarray(v) for k, d in res.items() for f, v in d.items()})
