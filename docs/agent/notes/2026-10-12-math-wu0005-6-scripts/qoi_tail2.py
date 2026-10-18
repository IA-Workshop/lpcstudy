"""E3b: per-estimate credibility checks (plan D1) beside the QoI-level sequence, same data as E3."""
import numpy as np, jax.numpy as jnp
import lm_mirror as L

for rho, se in ((0.01, 0.02), (0.01, 0.2), (0.05, 0.2)):
    d = L.run(200, 16, rho, se, 99 + int(1000 * rho) + int(100 * se))
    sw, nu = {}, {}
    for k in (15, 30, 60, 120):
        u, c, _ = L.make_refine(k)(jnp.asarray(d["u0"]), jnp.asarray(d["targets"]))
        s_old = L.MEAN + np.asarray(u) * L.STD
        sw[k] = np.asarray(L.adv_b(jnp.asarray(s_old))) / L.STD
        nu[k] = np.asarray(L.nu_b(jnp.asarray(s_old)))
    a = np.linalg.norm(sw[15] - sw[30], axis=1) / (rho * nu[30])
    b = np.linalg.norm(sw[30] - sw[60], axis=1) / (rho * nu[30])
    c = np.linalg.norm(sw[60] - sw[120], axis=1) / (rho * nu[30])
    mov = a > 0.1  # 'moving estimates' read as those above the per-estimate tolerance
    print(f"rho={rho} start={se}: median over moving: 15-30 {np.median(a[mov]):.3g}, 30-60 {np.median(b[mov]):.3g}"
          f" (ratio {np.median(b[mov])/np.median(a[mov]):.3f}); fraction>0.1: {np.mean(a>0.1):.4f}, {np.mean(b>0.1):.4f},"
          f" {np.mean(c>0.1):.4f} (ratios {np.mean(b>0.1)/np.mean(a>0.1):.2f}, {np.mean(c>0.1)/max(np.mean(b>0.1),1e-300):.2f});"
          f" total movement ratios {b.sum()/a.sum():.2f}, {c.sum()/b.sum():.2f}")
