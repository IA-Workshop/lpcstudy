"""E3: QoI-level doubling ratios and the d1 + 2 d2 bound on the LM mirror (DEVELOPMENT, literal seeds).

Surrogate QoIs: mean and median over 200 states of the per-state log mean squared whitened
estimate error (16 draws per state); 240 iterations serve as the converged reference.
"""
import numpy as np, jax.numpy as jnp
import lm_mirror as L

for rho, se in ((0.01, 0.02), (0.01, 0.2), (0.05, 0.2)):
    d = L.run(200, 16, rho, se, 99 + int(1000 * rho) + int(100 * se))
    q = {}
    for k in (15, 30, 60, 120, 240):
        u, c, _ = L.make_refine(k)(jnp.asarray(d["u0"]), jnp.asarray(d["targets"]))
        s_old = L.MEAN + np.asarray(u) * L.STD
        sw = np.asarray(L.adv_b(jnp.asarray(s_old))) / L.STD
        e2 = np.sum((sw - d["s_t"] / L.STD) ** 2, 1).reshape(d["n_states"], -1)
        ps = np.log(e2.mean(1))                     # per-state log MSE of the estimate
        q[k] = dict(mean=ps.mean(), median=np.median(ps))
    for name in ("mean", "median"):
        v = [q[k][name] for k in (15, 30, 60, 120, 240)]
        d1, d2, d3, d4 = (abs(v[i + 1] - v[i]) for i in range(4))
        err15 = abs(v[0] - v[-1])
        print(f"rho={rho} start={se} {name:6s}: d(15-30)={d1:.4g} d(30-60)={d2:.4g} d(60-120)={d3:.4g}"
              f" d(120-240)={d4:.4g} ratios {d2/max(d1,1e-300):.3f} {d3/max(d2,1e-300):.3f} {d4/max(d3,1e-300):.3f};"
              f" |q15-q240|={err15:.4g} <= d1+2d2={d1+2*d2:.4g}: {err15 <= d1 + 2*d2}; <= 2 d1: {err15 <= 2*d1}")
