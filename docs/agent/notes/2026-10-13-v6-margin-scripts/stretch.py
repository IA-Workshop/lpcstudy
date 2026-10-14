"""Rank correlation of log D with the 1-LT stretching ln sigma_1 on 4000 random states + the top-1% states. DEVELOPMENT."""
import sys
from pathlib import Path
code_root, cache_dir, system = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
sys.path.insert(0, code_root)
import numpy as np, jax
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
from scipy import stats as st
from lpcstudy.data import lyapunov_record
from lpcstudy.systems import SYSTEMS, make_flow_step, simulate_trajectory
spec = SYSTEMS[system]
lam, _ = lyapunov_record(spec, cache_dir / "lyapunov.json")
coarse = make_flow_step(spec, spec.params, 1.0 / (30 * lam))
stats = simulate_trajectory(coarse, jnp.asarray(spec.initial_state), 203_000)[3000:]
rng = np.random.default_rng(14_0006)
x0 = stats[rng.integers(0, len(stats))] + 1e-3 * rng.standard_normal(3)
orb = simulate_trajectory(coarse, jnp.asarray(x0), 203_000)[3000:]
D = np.load(f"D_{system}.npz")["D"][0]
jac = jax.jit(jax.vmap(jax.jacfwd(lambda s: jax.lax.fori_loop(0, 30, lambda _, x: coarse(x), s))))
idx = np.random.default_rng(7).integers(0, len(D), 4000)
ls = np.log(np.linalg.svd(np.asarray(jac(jnp.asarray(orb[idx]))), compute_uv=False)[:, 0])
r = st.spearmanr(np.log(D[idx]), ls)
q = np.quantile(ls, [.5, .99]); top = np.argsort(D)[::-1][:2000]
lt = np.log(np.linalg.svd(np.asarray(jac(jnp.asarray(orb[top]))), compute_uv=False)[:, 0])
print(f"{system}: spearman(log D, ln s1) = {r.statistic:.2f}; ln s1 random median {q[0]:.2f}, 99% {q[1]:.2f}; top-0.1% D states: ln s1 median {np.median(lt):.2f}, min {lt.min():.2f}")
