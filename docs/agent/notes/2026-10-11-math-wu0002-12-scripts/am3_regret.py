"""AM3: regret(v3) >= regret(v1) in IEEE arithmetic; v1 = c (w - w*)^2, v3 = c[(w-u)^2 - (w*-u)^2]."""
import numpy as np
rng = np.random.default_rng(20261011)
def both(sq_cp, sq_plp, cross, w):
    c = sq_cp + sq_plp - 2.0 * cross
    u = (sq_plp - cross) / np.maximum(c, 1e-300)
    ws = np.clip(u, 0.0, 1.0)
    old = np.mean(c[:, None, :] * (w - ws[:, None, :]) ** 2, axis=(0, 1))
    new = np.mean(c[:, None, :] * ((w - u[:, None, :]) ** 2 - (ws[:, None, :] - u[:, None, :]) ** 2), axis=(0, 1))
    ent_old = c[:, None, :] * (w - ws[:, None, :]) ** 2
    ent_new = c[:, None, :] * ((w - u[:, None, :]) ** 2 - (ws[:, None, :] - u[:, None, :]) ** 2)
    inside = (u >= 0) & (u <= 1)
    eq_inside = np.all((ent_new == ent_old)[np.broadcast_to(inside[:, None, :], ent_new.shape)])
    return old, new, int(np.sum(ent_new < ent_old)), eq_inside, float(np.mean(~inside))
n, E, nH, M = 500, 2, 5, 200
worst = 0.0; n_ent_viol = 0; n_agg_viol = 0; all_eq = True; trials = 300
for t in range(trials):
    # correlated CP/PLP errors per state and horizon, with scale growth and occasional near-equality
    scale_c = np.exp(rng.normal(0, 1.5, (n, 1, nH)))
    scale_p = np.exp(rng.normal(0, 1.5, (n, 1, nH)) + np.linspace(-3, 2, nH))
    rho = rng.uniform(-0.999, 0.999, (n, 1, nH)) if t % 3 else rng.uniform(0.99, 0.9999999, (n, 1, nH))
    z1, z2 = rng.standard_normal((2, n, M, nH))
    ec = scale_c * z1; ep = scale_p * (rho * z1 + np.sqrt(1 - rho**2) * z2) + rng.normal(0, 0.3, (n, 1, nH)) * scale_p
    sq_cp, sq_plp, cross = (ec**2).mean(1), (ep**2).mean(1), (ec*ep).mean(1)
    logits = rng.normal(0, 30, (n, E, nH))
    rules = {"A0": np.ones((n, E, nH)), "A1": np.zeros((n, E, nH)),
             "A2": np.broadcast_to(rng.uniform(0, 1, nH), (n, E, nH)),
             "A3": 1.0 / (1.0 + np.exp(np.clip(logits, -50, 50))),
             "A4": np.broadcast_to(rng.uniform(0, 1, (n, 1, 1)) ** rng.choice([1, 40]), (n, E, nH))}
    for w in rules.values():
        old, new, nv, eq, frac = both(sq_cp, sq_plp, cross, w)
        n_ent_viol += nv; all_eq &= eq
        short = np.max((old - new) / old)
        worst = max(worst, short); n_agg_viol += int(np.any(new < old))
print(f"trials={trials} x 5 rules; entries with new<old: {n_ent_viol}; horizons-with-aggregate new<old: {n_agg_viol}; "
      f"max aggregate relative shortfall {worst:.3e}; u in [0,1] entries bitwise equal: {all_eq}")
# adversarial: u << 0 with tiny positive w (sigmoid tail), entry level
u = -np.logspace(-3, 8, 2000); c = 1.0
w = np.logspace(-30, -1, 2000)[:, None]
o = c * (w - 0.0) ** 2; nn = c * ((w - u) ** 2 - (0.0 - u) ** 2)
bad = nn < o
print(f"adversarial grid: {bad.sum()} of {bad.size} entries new<old; all have w < 4 eps |u|: "
      f"{np.all((w * np.ones_like(u))[bad] < 4 * 2.22e-16 * np.abs(u * np.ones_like(w))[bad])}; "
      f"max shortfall / (c u^2) = {np.max(np.where(bad, (o - nn) / (u**2), 0)):.2e}")
