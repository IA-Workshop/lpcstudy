"""Probe 4: probe 3 in whitened coordinates (mean, C^{1/2} from the trajectory), as production (DEVELOPMENT)."""
import sys
import numpy as np
import jax, jax.numpy as jnp
jax.config.update("jax_enable_x64", True)
root = sys.argv[1]
sys.argv = [sys.argv[0], root, "5", "7.9"]
import importlib.util
s_ = importlib.util.spec_from_file_location("p1", sys.argv[0].replace("lm_probe4", "lm_probe"))
p1 = importlib.util.module_from_spec(s_); s_.loader.exec_module(p1)
mean = p1.traj.mean(0); C = np.cov(p1.traj.T)
w, V = np.linalg.eigh(C); U = V @ np.diag(np.sqrt(w)) @ V.T; W = V @ np.diag(1/np.sqrt(w)) @ V.T
Uj, mj = jnp.asarray(U), jnp.asarray(mean)
p1.generate = lambda u: p1.fwd(mj + Uj @ u)
p1.jac = jax.jacfwd(p1.generate)
p1.N_ITER = 30
trace30 = jax.jit(jax.vmap(p1.refine_trace))
rng = np.random.default_rng(41)
idx = rng.choice(4000, size=256, replace=False)
targets = np.stack([p1.clean_target(i) for i in idx]); truth = (p1.traj[idx] - mean) @ W.T
for rho in [0.01, 0.05]:
    for pert in [0.02, 0.2]:
        r = np.random.default_rng(43)
        noisy = targets + rho * r.standard_normal(targets.shape)
        start = truth + pert * r.standard_normal(truth.shape)
        _, _, c0, (us, cs, acc, cc) = trace30(jnp.asarray(start), jnp.asarray(noisy))
        us, cs, acc, c0 = map(np.asarray, (us, cs, acc, c0))
        d = np.linalg.norm(us[:, 14] - us[:, 29], axis=1)
        err = np.linalg.norm(us[:, 29] - truth, axis=1)
        uncon = d > 0.1 * err
        cprev = np.concatenate([c0[:, None], cs[:, :-1]], 1)
        rel = (cprev - cs) / cprev
        late = ((rel[:, 12:15] > 1e-6) & acc[:, 12:15]).any(1)
        acc15 = acc[:, :15].sum(1)
        print(f"WHITENED rho={rho} pert={pert}: unconverged@15 {uncon.sum()}/256; late flag {late.sum()}/256, both {(late & uncon).sum()};"
              f" c30/rho^2>18.47 {(cs[:,29]/rho**2>18.47).sum()}/256; accepted@15 median {np.median(acc15)}, material median {np.median(((rel[:, :15] > 1e-6) & acc[:, :15]).sum(1))}; acc==0 {np.sum(acc15==0)}")
