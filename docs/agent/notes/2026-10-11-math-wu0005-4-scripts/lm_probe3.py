"""Probe 3: frequency of non-convergence at the 15-iteration budget and a cheap late-progress screen (DEVELOPMENT)."""
import sys
import numpy as np
import jax, jax.numpy as jnp
jax.config.update("jax_enable_x64", True)
root = sys.argv[1]
sys.argv = [sys.argv[0], root, "5", "7.9"]
import importlib.util
s_ = importlib.util.spec_from_file_location("p1", sys.argv[0].replace("lm_probe3", "lm_probe"))
p1 = importlib.util.module_from_spec(s_); s_.loader.exec_module(p1)

p1.N_ITER = 30
trace30 = jax.jit(jax.vmap(p1.refine_trace))
# 256 states: reuse trajectory, new indices
rng = np.random.default_rng(41)
idx = rng.choice(4000, size=256, replace=False)
targets = np.stack([p1.clean_target(i) for i in idx]); truth = p1.traj[idx]
for rho in [0.02, 0.05]:
    for pert in [0.05, 0.5]:
        r = np.random.default_rng(43)
        noisy = targets + rho * r.standard_normal(targets.shape)
        start = truth + pert * r.standard_normal(truth.shape)
        _, _, c0, (us, cs, acc, cc) = trace30(jnp.asarray(start), jnp.asarray(noisy))
        us, cs, acc, c0 = map(np.asarray, (us, cs, acc, c0))
        d = np.linalg.norm(us[:, 14] - us[:, 29], axis=1)
        err = np.linalg.norm(us[:, 29] - truth, axis=1)
        z = cs[:, 29] / rho**2
        wrong = z > 18.47  # chi2_4 0.999 quantile
        uncon = d > 0.1 * err
        cprev = np.concatenate([c0[:, None], cs[:, :-1]], 1)
        rel = (cprev - cs) / cprev
        late = ((rel[:, 12:15] > 1e-6) & acc[:, 12:15]).any(1)
        acc15 = acc[:, :15].sum(1)
        print(f"rho={rho} pert={pert}: unconverged@15 (|u15-u30|>0.1 err) {uncon.sum()}/256; late-progress flag {late.sum()}/256,"
              f" both {(late & uncon).sum()}; c30/rho^2>chi2_4(.999) {wrong.sum()}/256; accepted@15 median {np.median(acc15)},"
              f" material accepts@15 median {np.median(((rel[:, :15] > 1e-6) & acc[:, :15]).sum(1))}; accepted==0 {np.sum(acc15==0)}")
