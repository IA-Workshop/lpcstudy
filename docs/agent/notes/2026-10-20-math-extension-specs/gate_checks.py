"""The code's own V1, V2 and V6 on real SystemContexts of S1, S2, S3 at the
smoke preset's sizes (DEVELOPMENT, one thread, no preset run, no test tier).
The candidate specs are registered in-process (``SYSTEMS[name] = spec``) so
that ``data.build_context`` can build them; the file ``lpcstudy/systems.py``
is not edited. Then the V7 mechanism: ``check_cramer_rao`` (Gauss-Newton from
the true window-start state, 3 iterations) at the study's noise levels on 40
test states x 50 draws; a median ratio outside [0.9, 1.1] at a noise level
means that even an optimally started estimator leaves the Cramer-Rao regime
there, so the pipeline's V7 (LM from the network guess) cannot pass it."""

import sys
import tempfile
import time
from pathlib import Path

import numpy as np

from lpcstudy import systems
from lpcstudy.config import SMOKE
from lpcstudy.data import build_context
from lpcstudy.validation import check_cramer_rao, check_integrator, check_jacobians

from ext_common import CANDIDATES



def lm_efficiency(ctx, noise, n_states, n_draws, iters=15):
    """Damped LM (accept on decrease, damping /3 or x4, the pipeline's rule)
    from the true window-start state; returns the per-state ratio
    E||s_hat - s||^2_whitened / (rho nu)^2 and failure counts."""
    import jax
    import jax.numpy as jnp
    from lpcstudy.dynamics import delay_map_forward, make_observability
    from lpcstudy.systems import make_flow_step

    step = make_flow_step(ctx.spec, ctx.spec.params, ctx.interval)
    fwd = delay_map_forward(step, ctx.spec.observed_index, ctx.obs_mean, ctx.obs_scale, ctx.delay, ctx.embed_dim)
    jac = jax.jit(jax.jacfwd(fwd)); fwd_j = jax.jit(fwd)
    advance = jax.jit(lambda s: jax.lax.fori_loop(0, ctx.history, lambda _, x: step(x), s))
    nu_fn = make_observability(step, ctx.spec.observed_index, ctx.obs_scale, ctx.whiten, ctx.delay, ctx.embed_dim)
    rng = np.random.default_rng(20261020)
    ratios, rho_nus, nonfinite, far = [], [], 0, 0
    for t in ctx.split_indices["test"][:n_states]:
        s_old, s_t = ctx.eval_states[t - ctx.history], ctx.eval_states[t]
        clean = np.asarray(fwd_j(jnp.asarray(s_old)))
        nu = float(nu_fn(jnp.asarray(s_old[None, :]))[0])
        errs = []
        for _ in range(n_draws):
            target = clean + noise * rng.standard_normal(len(clean))
            u = s_old.copy(); damping = 1e-3
            cost = float(np.sum((target - np.asarray(fwd_j(jnp.asarray(u)))) ** 2))
            for _ in range(iters):
                a = np.asarray(jac(jnp.asarray(u)))
                if not np.all(np.isfinite(a)):
                    nonfinite += 1; break
                normal = a.T @ a
                rhs = a.T @ (target - np.asarray(fwd_j(jnp.asarray(u))))
                scale = np.trace(normal) / len(u) + 1e-12
                delta = np.linalg.solve(normal + damping * scale * np.eye(len(u)), rhs)
                cand = u + delta
                c = float(np.sum((target - np.asarray(fwd_j(jnp.asarray(cand)))) ** 2))
                if np.isfinite(c) and c < cost:
                    u, cost, damping = cand, c, damping / 3
                else:
                    damping *= 4
            s_hat = np.asarray(advance(jnp.asarray(u)))
            e2 = float(np.sum((ctx.whiten @ (s_hat - s_t)) ** 2))
            far += e2 > 1.0
            errs.append(e2)
        ratios.append(np.mean(errs) / (noise * nu) ** 2); rho_nus.append(noise * nu)
    ratios = np.sqrt(np.array(ratios))  # delta/(rho nu), as V7 defines it (rms over draws)
    return {"median": float(np.median(ratios)), "p10": float(np.quantile(ratios, .1)), "p90": float(np.quantile(ratios, .9)),
            "below": int((ratios < 0.9).sum()), "above": int((ratios > 1.1).sum()), "nonfinite": nonfinite, "far": int(far),
            "rho_nu": float(np.median(rho_nus))}


cache = Path(tempfile.mkdtemp(prefix="ext-math-cache-"))
which = sys.argv[1:] or ["S1", "S2", "S3"]
for key in which:
    sp = CANDIDATES[key]()
    systems.SYSTEMS[sp.name] = sp  # in-process registration only
    t0 = time.time()
    ctx = build_context(sp.name, SMOKE, cache)
    print(f"[{key}] {sp.name}: context built in {time.time()-t0:.0f} s; lambda {ctx.lambda_max!r}, interval {ctx.interval:.6f}, "
          f"delay {ctx.delay} (ami {ctx.meta['ami_delay']}), acf {ctx.acf_time}, spacing {ctx.spacing}, sigma_x {ctx.obs_scale:.4f}, "
          f"orbit max|x| {ctx.meta['trajectory_max_abs']}, starts {ctx.meta['start_index']}")
    v1 = check_jacobians(ctx)
    v6 = check_integrator(ctx)
    v2 = check_cramer_rao(ctx)
    print(f"  V1 {v1}  -> {'pass' if v1['delay_jacobian_rel_err'] < 1e-4 and v1['gain_rel_err'] < 1e-4 else 'FAIL'}")
    print(f"  V6 integrator_max_dev_sigma {v6['integrator_max_dev_sigma']:.3e} -> {'pass' if v6['integrator_max_dev_sigma'] < 1e-3 else 'FAIL'}")
    print(f"  V2 {v2} -> {'pass' if 0.8 <= v2['crlb_ratio_median'] <= 1.2 else 'FAIL'}")
    for rho in (0.005, 0.01, 0.02, 0.05):
        r = lm_efficiency(ctx, rho, n_states=40, n_draws=50)
        print(f"  LM efficiency (15 damped iterations from the true window start) at rho {rho}: median delta/(rho nu) {r['median']:.3f} "
              f"(p10 {r['p10']:.3f}, p90 {r['p90']:.3f}); states with ratio < 0.9: {r['below']}, > 1.1: {r['above']}; non-finite Jacobians {r['nonfinite']}; "
              f"draws with whitened error > 1: {r['far']} of {40*50}; median rho*nu {r['rho_nu']:.3f} -> V7-band {'ok' if 0.9 <= r['median'] <= 1.1 else 'OUTSIDE'}")
    print(f"  [{time.time()-t0:.0f} s]")
