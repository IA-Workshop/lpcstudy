"""Probe 2: L3 stub Jacobians, production vs trace bitwise, 15 vs 30 iterations (DEVELOPMENT)."""
import sys
from types import SimpleNamespace
import numpy as np
import jax, jax.numpy as jnp
jax.config.update("jax_enable_x64", True)
sys.path.insert(0, sys.argv[1])
sys.argv = [sys.argv[0], sys.argv[1], "5", "7.9"]
import importlib.util
spec_ = importlib.util.spec_from_file_location("p1", sys.argv[0].replace("lm_probe2", "lm_probe"))
p1 = importlib.util.module_from_spec(spec_); spec_.loader.exec_module(p1)
from lpcstudy.estimation import StateEstimator
from lpcstudy.dynamics import delay_map_forward

D, TAU = 7, 5
# --- L3(ii): which NaN stub gives a non-finite Jacobian?
for name, bad in [("full_like nan", lambda s: jnp.full_like(s, jnp.nan)),
                  ("s + nan", lambda s: s + jnp.nan), ("s * nan", lambda s: s * jnp.nan)]:
    f = delay_map_forward(bad, 0, 0.0, 7.9, TAU, D)
    J = np.asarray(jax.jacfwd(f)(jnp.ones(3)))
    print(f"L3 stub {name}: G finite rows {np.isfinite(np.asarray(f(jnp.ones(3)))).sum()}/7, Jacobian nonfinite entries {(~np.isfinite(J)).sum()}/21")

# --- production (pre-change) vs trace variant, bitwise
ctx = SimpleNamespace(unwhiten=np.eye(3), whiten=np.eye(3), state_mean=np.zeros(3),
                      spec=SimpleNamespace(observed_index=0), obs_mean=0.0, obs_scale=7.9,
                      delay=TAU, embed_dim=D, history=(D - 1) * TAU)
r = np.random.default_rng(23)
noisy = p1.targets + 0.01 * r.standard_normal(p1.targets.shape)
u0 = p1.truth + 0.01 * r.standard_normal(p1.truth.shape)
net = SimpleNamespace(predict=lambda x: jnp.asarray(u0), width=0)
est = StateEstimator(ctx=ctx, network=net, model_step=p1.step, refine_steps=15)
fn = est._build()
# production returns s_t and nu; recover s_old by comparing with trace's u_final advanced
uf, cf, c0, (us, cs, acc, cc) = p1.trace_fn(jnp.asarray(u0), jnp.asarray(noisy))
st_prod, _ = fn(noisy)
st_trace = np.asarray(jax.vmap(lambda s: jax.lax.fori_loop(0, ctx.history, lambda _, x: p1.step(x), s))(uf))
print("production s_t == trace-advanced s_t bitwise:", np.array_equal(st_prod, st_trace),
      "max abs diff", np.max(np.abs(st_prod - st_trace)))

# --- iteration-count study: 15 vs 30 (common inputs)
p1.N_ITER = 30
trace30 = jax.jit(jax.vmap(p1.refine_trace))
for rho in [0.01, 0.05]:
    r = np.random.default_rng(31)
    noisy = p1.targets + rho * r.standard_normal(p1.targets.shape)
    start = p1.truth + 0.05 * r.standard_normal(p1.truth.shape)
    _, _, _, (us, cs, acc, cc) = trace30(jnp.asarray(start), jnp.asarray(noisy))
    us, cs, acc = map(np.asarray, (us, cs, acc))
    d15_30 = np.linalg.norm(us[:, 14] - us[:, 29], axis=1)
    err30 = np.linalg.norm(us[:, 29] - p1.truth, axis=1)
    last = (cs[:, 13] - cs[:, 14]) / cs[:, 14]
    print(f"rho={rho}: |u15-u30| median {np.median(d15_30):.2e} max {np.max(d15_30):.2e}; |u30-truth| median {np.median(err30):.2e};"
          f" ratio max {np.max(d15_30/err30):.2e}; last-iter rel decrease>1e-6: {(last>1e-6).sum()}/64, >1e-10: {(last>1e-10).sum()}/64;"
          f" c15/c30-1 max {np.max(cs[:,14]/cs[:,29]-1):.2e}; accepts 16..30 median {np.median(acc[:,15:].sum(1))}")

# --- inspect the worst rho=0.05 case
i = int(np.argmax(d15_30))
np.set_printoptions(precision=4, linewidth=200)
print("worst state", i, "c_k/c30:", cs[i] / cs[i, 29])
print("accept:", acc[i].astype(int))
