"""WU-0037: per-draw V7 diagnosis of the PLP state estimator on one system.

DEVELOPMENT (DEV-3): not a hypothesis test.

CPU reproduction of the V7 quantity ``delta_i / (rho nu_i)`` on the first
``--states`` test-sweep states of a DEV-3 full-preset context, with the
run's own oracle unit noise (labels ``(seed, system, D, "test", "oracle")``,
so these are the same random numbers as the stored run), and the estimator
trained by the package's own ``Study.setup`` at the full preset (40 epochs,
1e5 pairs, widths 64/128). The package is imported read-only; nothing in
``lpcstudy/`` is changed. CPU training is not bitwise the GPU training, so the
reproduction is checked against the stored V7 medians, not assumed.

Estimator variants (all with the production LM arithmetic: damping 1e-3,
x1/3 on accept, x4 on reject, scale tr(A^T A)/m + 1e-12):

* ``prod``: network start, 15 iterations; checked against
  ``StateEstimator.estimate_counted`` on the same inputs.
* ``it30`` and ``it60``: the ``prod`` result refined by 15, and then 30, more
  iterations (damping restarted at 1e-3 at each segment), 30 and 60 in all
  (iteration-count study at 15, 30, 60, ratio 2). The first run, on
  ``lorenz96_4``, ran 60 iterations straight from the network start instead,
  and the equivalence check on all draws.
* ``truth``: start at the true window-start state, 15 iterations (not
  deployable: it isolates the start from the objective).
* ``cont``: network start, window continuation: LM on the ``m+1`` oldest
  delay coordinates, then one more coordinate per stage (5 iterations per
  intermediate stage, damping reset), then 15 iterations on all ``D``
  coordinates. The final objective is the production objective.
* ``analog`` (only with ``--analog``; on by default in the first run, on
  ``lorenz96_4``): start at the window-start state of CP's nearest analog (library
  at the core size 1e4, same noise level), 15 iterations.
* ``pair_nn``: start at the training target (whitened window-start state) of
  the nearest noise-free training input of the estimator's own pairs
  (``ctx.estimator_inputs``; PLP's own data, no library dependence), 15
  iterations.
* ``ms2``: the lowest final cost among ``prod`` and ``cont`` (deployable).
* ``ms3``: the lowest final cost among ``prod``, ``cont`` and ``pair_nn``
  (deployable three-start; ``analog`` is not used in it because a library
  start would make PLP depend on the library, which H2b and H2e measure).
* ``best_truth``: the lowest final cost among ``prod`` and ``truth`` (not
  deployable; an upper bound on what any start change can achieve if the
  global minimum is the one nearest the truth).

Per draw it stores the whitened error at time t (after the window advance)
and the final cost c, for every variant, and the start error of the network.
Output: ``<out>/<system>.npz`` and a JSON summary on stdout.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import shutil
import time
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np

from lpcstudy.config import PRESETS
from lpcstudy.dynamics import delay_map_forward, make_observability
from lpcstudy.embedding import delay_vectors
from lpcstudy.ensemble import AnalogLibrary
from lpcstudy.estimation import StateEstimator, gof_threshold
from lpcstudy.pipeline import Study
from lpcstudy.seeds import load_registry, resolve_dev_seed, with_seed
from lpcstudy.systems import make_flow_step

WT = Path("/home/brianm/projects/physics/chaos/lpcstudy-wt")
REPO = WT / "wu/0037-v7-diagnosis"
RUNS = {
    "lorenz63_r166": WT / "run/ext-run-974519a/runs/dev/ext-lorenz63_r166-gpu/full",
    "rossler_z": WT / "run/ext-run-974519a/runs/dev/ext-rossler_z-gpu/full",
    "rossler_hyper": WT / "run/ext-run-974519a/runs/dev/ext-rossler_hyper-gpu/full",
    "hindmarsh_rose": WT / "run/ext-run-392a069/runs/dev/ext-hindmarsh_rose-gpu/full",
    "hyper_jha": WT / "run/ext-run-392a069/runs/dev/ext-hyper_jha-gpu/full",
    "lorenz96_4": WT / "run/ext-run-392a069/runs/dev/ext-lorenz96_4-gpu/full",
    "lorenz63": WT / "run/ens-3dec086/runs/dev/ens-DEV-3/full",
}
SEED_ID = "DEV-3"


def make_lm(generate, dim: int, n_coords: int):
    """Production LM step with a 0/1 mask on the residual coordinates."""
    jac = jax.jacfwd(generate)

    def cost(u, target, mask):
        resid = (target - generate(u)) * mask
        value = jnp.sum(resid**2)
        return jnp.where(jnp.isfinite(value), value, jnp.inf)

    def run(u0, target, mask, n_iter):
        def body(carry, _):
            u, c_u, damping = carry
            a_mat = jac(u) * mask[:, None]
            a_mat = jnp.where(jnp.isfinite(a_mat), a_mat, 0.0)
            normal = a_mat.T @ a_mat
            rhs = a_mat.T @ ((target - generate(u)) * mask)
            scale = jnp.trace(normal) / dim + 1e-12
            delta = jnp.linalg.solve(normal + damping * scale * jnp.eye(dim), rhs)
            cand = u + delta
            c_cand = cost(cand, target, mask)
            accept = c_cand < c_u
            return (
                jnp.where(accept, cand, u),
                jnp.where(accept, c_cand, c_u),
                jnp.where(accept, damping / 3.0, damping * 4.0),
            ), None

        carry, _ = jax.lax.scan(body, (u0, cost(u0, target, mask), 1e-3), None, length=n_iter)
        return carry[0], carry[1]

    return cost, run


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("system")
    ap.add_argument("--states", type=int, default=100)
    ap.add_argument("--levels", default="0.005,0.01,0.02,0.05")
    ap.add_argument("--out", required=True)
    ap.add_argument("--analog", action="store_true", help="also run the library-analog start")
    args = ap.parse_args()
    system = args.system
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    work = out / f"work-{system}"
    (work / "cache").mkdir(parents=True, exist_ok=True)
    shutil.copy(RUNS[system] / "cache/lyapunov.json", work / "cache/lyapunov.json")

    seed = resolve_dev_seed(SEED_ID, load_registry(REPO / "seeds/development_seeds.json"))
    cfg = with_seed(dataclasses.replace(PRESETS["full"], core_systems=(system,)), SEED_ID, seed)
    stored = json.loads((RUNS[system] / "results.json").read_text())
    assert stored["config"]["seed"] == cfg.seed, "seed mismatch with the stored run"
    study = Study(cfg, work)
    t0 = time.time()
    ctx = study.context(system)
    meta_cmp = {
        k: ctx.meta.get(k) == stored["systems"][system]["context"].get(k)
        for k in ("main_digest", "estimator_digest", "whiten_digest", "interval", "delay")
    }
    print(json.dumps({"context_s": time.time() - t0, "context_matches_stored": meta_cmp}), flush=True)

    n = args.states
    times = ctx.split_indices["test"][:n]
    m = ctx.spec.dim
    big_d = ctx.embed_dim
    hist = ctx.history
    step = make_flow_step(ctx.spec, ctx.spec.params, ctx.interval)
    nu_fn = make_observability(step, ctx.spec.observed_index, ctx.obs_scale, ctx.whiten, ctx.delay, big_d)
    s_old = ctx.eval_states[times - hist]
    nu = np.asarray(nu_fn(jnp.asarray(s_old)))
    s_true_w = ctx.whiten_states(ctx.eval_states[times])
    u_true = ctx.whiten_states(s_old)
    clean = delay_vectors(ctx.eval_clean, times, ctx.delay, big_d)
    unit = study.unit_noise(ctx, "test", "oracle", cfg.n_oracle_draws, big_d)[:n]
    n_draws = unit.shape[1]

    root = jnp.asarray(ctx.unwhiten)
    mean = jnp.asarray(ctx.state_mean)
    fwd = delay_map_forward(step, ctx.spec.observed_index, ctx.obs_mean, ctx.obs_scale, ctx.delay, big_d)

    def generate(u):
        return fwd(mean + root @ u)

    cost, lm_run = make_lm(generate, m, big_d)

    def advance(s):
        return jax.lax.fori_loop(0, hist, lambda _, x: step(x), s)

    @jax.jit
    def finish(u):
        return jax.vmap(lambda v: advance(mean + root @ v))(u)

    full_mask = jnp.ones(big_d)
    # X_t[k] observes Phi^{(D-1-k) tau}(s_old): the oldest coordinate is k = D-1.
    stages = [np.r_[np.zeros(big_d - j), np.ones(j)] for j in range(m + 1, big_d)]

    def batched(n_iter):
        return jax.jit(jax.vmap(lambda u0, x, mk: lm_run(u0, x, mk, n_iter), in_axes=(0, 0, None)))

    lm15, lm30, lm5 = batched(15), batched(30), batched(5)
    from scipy.spatial import cKDTree
    pair_tree = cKDTree(ctx.estimator_inputs)
    results = {"system": system, "n_states": n, "n_draws": n_draws, "nu": nu, "times": times}
    summary = {"system": system, "label": "DEVELOPMENT (DEV-3): not a hypothesis test",
               "n_states": n, "n_draws": n_draws, "levels": {}}
    dof = big_d - m
    chi = gof_threshold(dof)
    for rho in [float(r) for r in args.levels.split(",")]:
        t1 = time.time()
        setup = study.setup(ctx, rho)
        est: StateEstimator = setup.estimator
        flat = (clean[:, None, :] + rho * unit).reshape(-1, big_d)
        xs = jnp.asarray(flat)
        u0 = jnp.asarray(est.network.predict(xs))
        # production path on the first n_check draws, for the equivalence check
        n_check = min(len(flat), 2000)
        prod_states, _, _, _, prod_lm = est.estimate_counted(flat[:n_check])
        prod_w = ctx.whiten_states(prod_states)
        if args.analog:
            library = AnalogLibrary.build(ctx, rho, cfg.core_library, cfg.horizon_max)
            lib_idx, _ = library.query(flat, 1)
            u_analog = jnp.asarray(ctx.whiten_states(ctx.library_states[lib_idx[:, 0] - hist]))
        u_tr = jnp.asarray(np.repeat(u_true, n_draws, axis=0))
        _, pair_idx = pair_tree.query(flat, k=1)
        u_pair = jnp.asarray(ctx.estimator_targets[pair_idx])

        variants = {}
        u, c = lm15(u0, xs, full_mask)
        variants["prod"] = (u, c)
        # 15 and then 30 more iterations from the production result (damping
        # restarted at 1e-3 at each segment): 30 and 60 iterations in all
        variants["it30"] = lm15(u, xs, full_mask)
        variants["it60"] = lm30(variants["it30"][0], xs, full_mask)
        variants["truth"] = lm15(u_tr, xs, full_mask)
        if args.analog:
            variants["analog"] = lm15(u_analog, xs, full_mask)
        variants["pair_nn"] = lm15(u_pair, xs, full_mask)
        uc = u0
        for mk in stages:
            uc, _ = lm5(uc, xs, jnp.asarray(mk))
        variants["cont"] = lm15(uc, xs, full_mask)

        arrays = {}
        truth_rep = np.repeat(s_true_w, n_draws, axis=0)
        for name, (uu, cc) in variants.items():
            s_t = np.asarray(finish(uu))
            err = np.linalg.norm(ctx.whiten_states(s_t) - truth_rep, axis=1)
            arrays[name] = (err, np.asarray(cc))
        prod_err_pkg = np.linalg.norm(prod_w - truth_rep[:n_check], axis=1)
        equiv = float(np.max(np.abs(prod_err_pkg - arrays["prod"][0][:n_check])))
        equiv_c = float(np.max(np.abs(np.asarray(prod_lm.residual) - arrays["prod"][1][:n_check])))

        def pick(names):
            cs = np.stack([arrays[k][1] for k in names])
            es = np.stack([arrays[k][0] for k in names])
            j = np.argmin(cs, axis=0)
            return es[j, np.arange(es.shape[1])], cs[j, np.arange(es.shape[1])]

        arrays["ms2"] = pick(["prod", "cont"])
        arrays["ms3"] = pick(["prod", "cont", "pair_nn"])
        arrays["best_truth"] = pick(["prod", "truth"])
        start_err = np.linalg.norm(np.asarray(u0) - np.asarray(u_tr), axis=1)
        lev = {"seconds": None, "equiv_max_abs_err_diff": equiv, "equiv_max_abs_cost_diff": equiv_c,
               "variants": {}}
        for name, (err, cc) in arrays.items():
            e2 = err.reshape(n, n_draws) ** 2
            delta = np.sqrt(e2.mean(axis=1))
            ratio = delta / (rho * nu)
            far = (cc > chi * rho**2).reshape(n, n_draws)
            lev["variants"][name] = {
                "median_ratio": float(np.median(ratio)),
                "q10_q90_ratio": [float(np.quantile(ratio, 0.1)), float(np.quantile(ratio, 0.9))],
                "frac_states_ratio_gt_1.1": float(np.mean(ratio > 1.1)),
                "frac_draws_above_chi2": float(far.mean()),
                "frac_states_with_far_draw": float(far.any(axis=1).mean()),
                "median_ratio_states_without_far": (float(np.median(ratio[~far.any(axis=1)]))
                                                     if (~far.any(axis=1)).any() else None),
            }
            results[f"{rho:g}/{name}/err"] = err
            results[f"{rho:g}/{name}/cost"] = cc
        results[f"{rho:g}/start_err"] = start_err
        lev["start_err_median"] = float(np.median(start_err))
        lev["val_loss"] = study.estimator_log[str((system, big_d, ctx.delay, rho))]["val_loss_by_width"]
        lev["seconds"] = time.time() - t1
        summary["levels"][f"{rho:g}"] = lev
        print(json.dumps({f"{rho:g}": lev}), flush=True)
    np.savez(out / f"{system}.npz", **{k: np.asarray(v) for k, v in results.items()})
    (out / f"{system}.summary.json").write_text(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
