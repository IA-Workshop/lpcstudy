"""WU-0037: does a converged LM change V7? Iteration study from two starts.

DEVELOPMENT (DEV-3): not a hypothesis test.

Same context, states, unit noise and trained estimator recipe as ``diag.py``
(CPU, DEV-3, full preset). For the starts ``truth`` (true window-start state)
and ``pair_nn`` (nearest estimator training pair), runs the production LM for
15 iterations, then 15 and 30 more (damping restarted at 1e-3 at each
segment): 15, 30 and 60 in all. Reports per level the V7 medians and the
median slope, and the median relative cost change between 30 and 60
iterations (a convergence measure of the objective). Used for S3, where the
question is whether the departure from rho nu is a property of the converged
estimate (the objective) or of the iteration budget.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import shutil
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np
from scipy.spatial import cKDTree

from lpcstudy.config import PRESETS
from lpcstudy.dynamics import delay_map_forward, make_observability
from lpcstudy.embedding import delay_vectors
from lpcstudy.pipeline import Study
from lpcstudy.seeds import load_registry, resolve_dev_seed, with_seed
from lpcstudy.systems import make_flow_step

import diag  # same folder: RUNS, REPO, SEED_ID, make_lm


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("system")
    ap.add_argument("--states", type=int, default=150)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    system, out = args.system, Path(args.out)
    work = out / f"work-conv-{system}"
    (work / "cache").mkdir(parents=True, exist_ok=True)
    shutil.copy(diag.RUNS[system] / "cache/lyapunov.json", work / "cache/lyapunov.json")
    seed = resolve_dev_seed(diag.SEED_ID, load_registry(diag.REPO / "seeds/development_seeds.json"))
    cfg = with_seed(dataclasses.replace(PRESETS["full"], core_systems=(system,)), diag.SEED_ID, seed)
    study = Study(cfg, work)
    ctx = study.context(system)
    n, big_d, m, hist = args.states, ctx.embed_dim, ctx.spec.dim, ctx.history
    times = ctx.split_indices["test"][:n]
    step = make_flow_step(ctx.spec, ctx.spec.params, ctx.interval)
    nu = np.asarray(make_observability(step, ctx.spec.observed_index, ctx.obs_scale, ctx.whiten,
                                       ctx.delay, big_d)(jnp.asarray(ctx.eval_states[times - hist])))
    s_true_w = ctx.whiten_states(ctx.eval_states[times])
    u_true = ctx.whiten_states(ctx.eval_states[times - hist])
    clean = delay_vectors(ctx.eval_clean, times, ctx.delay, big_d)
    unit = study.unit_noise(ctx, "test", "oracle", cfg.n_oracle_draws, big_d)[:n]
    n_draws = unit.shape[1]
    root, mean = jnp.asarray(ctx.unwhiten), jnp.asarray(ctx.state_mean)
    fwd = delay_map_forward(step, ctx.spec.observed_index, ctx.obs_mean, ctx.obs_scale, ctx.delay, big_d)
    _, lm_run = diag.make_lm(lambda u: fwd(mean + root @ u), m, big_d)
    mask = jnp.ones(big_d)
    lm15 = jax.jit(jax.vmap(lambda u0, x: lm_run(u0, x, mask, 15)))
    lm30 = jax.jit(jax.vmap(lambda u0, x: lm_run(u0, x, mask, 30)))
    finish = jax.jit(jax.vmap(lambda v: jax.lax.fori_loop(0, hist, lambda _, x: step(x), mean + root @ v)))
    tree = cKDTree(ctx.estimator_inputs)
    truth_rep = np.repeat(s_true_w, n_draws, axis=0)
    levels = cfg.noise_levels
    deltas = {}
    conv = {}
    for rho in levels:
        flat = (clean[:, None, :] + rho * unit).reshape(-1, big_d)
        xs = jnp.asarray(flat)
        starts = {"truth": jnp.asarray(np.repeat(u_true, n_draws, axis=0)),
                  "pair_nn": jnp.asarray(ctx.estimator_targets[tree.query(flat, k=1)[1]])}
        for name, u0 in starts.items():
            u15, c15 = lm15(u0, xs)
            u30, c30 = lm15(u15, xs)
            u60, c60 = lm30(u30, xs)
            for it, uu in ((15, u15), (30, u30), (60, u60)):
                err = np.linalg.norm(ctx.whiten_states(np.asarray(finish(uu))) - truth_rep, axis=1)
                deltas[(name, it, rho)] = np.sqrt((err.reshape(n, n_draws) ** 2).mean(axis=1))
            c30, c60 = np.asarray(c30), np.asarray(c60)
            conv[(name, rho)] = float(np.median((c30 - c60) / np.maximum(c30, 1e-300)))
    lv = np.array(levels)
    cen = np.log(lv) - np.log(lv).mean()
    res = {"system": system, "label": "DEVELOPMENT (DEV-3): not a hypothesis test", "n_states": n, "rows": []}
    for name in ("truth", "pair_nn"):
        for it in (15, 30, 60):
            d = np.column_stack([deltas[(name, it, r)] for r in levels])
            ratio = d / (lv[None, :] * nu[:, None])
            slope = (np.log(d) - np.log(d).mean(axis=1, keepdims=True)) @ cen / np.sum(cen**2)
            res["rows"].append({
                "start": name, "iterations": it,
                "median_ratio": {f"{r:g}": float(np.median(ratio[:, i])) for i, r in enumerate(levels)},
                "median_slope": float(np.median(slope)),
                "median_rel_cost_change_30_to_60": {f"{r:g}": conv[(name, r)] for r in levels},
            })
    (out / f"{system}.converged.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
