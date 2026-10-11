"""Scratch probe for WU-0005.4 M-items (DEVELOPMENT, literal default_rng seeds, CPU, 1 thread)."""
import sys
from types import SimpleNamespace
import numpy as np
import jax, jax.numpy as jnp
jax.config.update("jax_enable_x64", True)
sys.path.insert(0, sys.argv[1])
from lpcstudy.systems import SYSTEMS, make_flow_step, simulate_trajectory
from lpcstudy.dynamics import delay_map_forward
from lpcstudy.estimation import StateEstimator
from scipy import stats

D, M_DIM, N_ITER = 7, 3, 15
spec = SYSTEMS["lorenz63"]
interval = 1.0 / (30 * 0.9056)
step = make_flow_step(spec, spec.params, interval)
OBS_SCALE = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
TAU = int(sys.argv[2])
span = (D - 1) * TAU

burn = simulate_trajectory(step, jnp.asarray(spec.initial_state), 3000)
traj = simulate_trajectory(step, jnp.asarray(burn[-1]), 4000 + span + 1)
rng = np.random.default_rng(20261011)
starts = rng.choice(4000, size=64, replace=False)


def clean_target(i):
    obs = traj[i:i + span + 1, 0] / OBS_SCALE
    return obs[(D - 1 - np.arange(D)) * TAU]  # newest first


fwd = delay_map_forward(step, 0, 0.0, OBS_SCALE, TAU, D)


def generate(u):
    return fwd(u)


jac = jax.jacfwd(generate)


def cost(u, target):
    resid = target - generate(u)
    value = jnp.sum(resid ** 2)
    return jnp.where(jnp.isfinite(value), value, jnp.inf)


def refine_trace(u0, target):
    dim = u0.shape[0]

    def body(carry, _):
        u, c_u, damping = carry
        a_mat = jac(u)
        a_mat = jnp.where(jnp.isfinite(a_mat), a_mat, 0.0)
        normal = a_mat.T @ a_mat
        rhs = a_mat.T @ (target - generate(u))
        scale = jnp.trace(normal) / dim + 1e-12
        delta = jnp.linalg.solve(normal + damping * scale * jnp.eye(dim), rhs)
        cand = u + delta
        c_cand = cost(cand, target)
        accept = c_cand < c_u
        u_new = jnp.where(accept, cand, u)
        c_new = jnp.where(accept, c_cand, c_u)
        return (u_new, c_new, jnp.where(accept, damping / 3.0, damping * 4.0)), (u_new, c_new, accept, c_cand)

    c0 = cost(u0, target)
    (uf, cf, _), ys = jax.lax.scan(body, (u0, c0, 1e-3), None, length=N_ITER)
    return uf, cf, c0, ys


trace_fn = jax.jit(jax.vmap(refine_trace))
eager_cost = jax.jit(jax.vmap(cost))  # independent compile, outside the loop

targets = np.stack([clean_target(i) for i in starts])
truth = traj[starts]


def run(u0, tg, label):
    uf, cf, c0, (us, cs, acc, ccand) = trace_fn(jnp.asarray(u0), jnp.asarray(tg))
    us, cs, acc, ccand = map(np.asarray, (us, cs, acc, ccand))
    # independent recomputation J(u_k), one compile, per iteration
    J = np.stack([np.asarray(eager_cost(jnp.asarray(us[:, k]), jnp.asarray(tg))) for k in range(N_ITER)], 1)
    J0 = np.asarray(eager_cost(jnp.asarray(u0), jnp.asarray(tg)))
    dc = np.abs(cs - J)
    print(f"--- {label}: c0 med {np.median(c0):.3e}, J0-c0 max {np.max(np.abs(J0-np.asarray(c0))):.2e}")
    print(f"   final c: median {np.median(cf):.3e} max {np.max(cf):.3e}; accepted median {np.median(acc.sum(1))}, min {acc.sum(1).min()} max {acc.sum(1).max()}")
    print(f"   max|c_k-J(u_k)| {dc.max():.3e}; max rel {np.max(dc/np.maximum(J,1e-300)):.3e}")
    # monotone of J along accepted iterates
    Jprev = np.concatenate([J0[:, None], J[:, :-1]], 1)
    viol = (J > Jprev * (1 + 1e-12)) & acc
    print(f"   J(u_k)>J(u_k-1)(1+1e-12) on accepted: {viol.sum()} of {acc.sum()}")
    # accepts that are 'null' (relative decrease < 1e-10)
    cprev = np.concatenate([np.asarray(c0)[:, None], cs[:, :-1]], 1)
    reldec = (cprev - cs) / np.maximum(cprev, 1e-300)
    print(f"   accepts with rel. decrease < 1e-8: {((reldec < 1e-8) & acc).sum()} of {acc.sum()}")
    return np.asarray(cf), acc, us, cs, np.asarray(c0)


if __name__ == "__main__":
    print(f"tau={TAU}, obs_scale={OBS_SCALE}, interval={interval:.5f}")
    cf, acc, *_ = run(truth, targets, "true start, no noise")
    print("   per-state accepted at truth:", acc.sum(1)[:20])
    for d in [1e-3, 1e-2, 1e-1, 0.5, 1.0]:
        r2 = np.random.default_rng(7)
        dirs = r2.standard_normal(truth.shape)
        dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
        run(truth + d * dirs, targets, f"perturbed |delta|={d}")
    # noisy rho=0.01 and 0.05 in normalized units relative to sigma_x
    sig = np.std(traj[:, 0]) / OBS_SCALE
    for rho in [0.01, 0.05]:
        r3 = np.random.default_rng(11)
        noisy = targets + rho * sig * r3.standard_normal(targets.shape)
        cf, acc, us, cs, c0 = run(truth, noisy, f"noisy rho={rho} (noise sd {rho*sig:.3e})")
        z = cf / (rho * sig) ** 2
        print(f"   c/(rho sigma)^2: median {np.median(z):.2f} (chi2_4 {stats.chi2.median(4):.2f}), p95 {np.quantile(z,0.95):.2f} (chi2_4 {stats.chi2.ppf(.95,4):.2f}); KS p {stats.kstest(z, stats.chi2(4).cdf).pvalue:.3f}")
        # iteration at which c within 1e-10 rel of final
        conv_it = np.argmax(np.abs(cs - cf[:, None]) <= 1e-10 * cf[:, None], axis=1) + 1
        print(f"   iteration of convergence (rel 1e-10): median {np.median(conv_it)}, max {conv_it.max()}; accepts after: median {np.median([acc[i, conv_it[i]:].sum() for i in range(len(cf))])}")
