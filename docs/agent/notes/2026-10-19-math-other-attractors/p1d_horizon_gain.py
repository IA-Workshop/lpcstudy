"""Numerical check of Theorem P1(d), the half-doubling-time bound on the gain.

Model: per horizon H = 1..240 (8 LT), the better single forecaster's r.m.s.
error is r0 exp(Lambda H) exactly (the hypothesis of (d)); the other
forecaster's error and the cross moment are random but with C >= 0 at every
horizon (the hypothesis of (c)). The hybrid uses the clipped optimum. The
characteristic horizon is the code's: first H with sqrt(mse + rho^2) > theta
(verification noise in quadrature, ``oracle.characteristic_horizon``), on
integer steps, censored at 240.

Claim checked: T_hybrid - T_best <= ln 2 / (2 Lambda) + 1 step (the +1 is the
integer first passage). Then the same with C < 0 allowed, to show the bound
fails (P1(e)).

DEVELOPMENT, scratch seed 20261019, numpy only.
"""

import numpy as np

rng = np.random.default_rng(20261019)
H = np.arange(1, 241)
rho, theta = 0.01, 0.2
worst_gain, n_viol, n_cases = -np.inf, 0, 0
for _ in range(2000):
    Lam = rng.uniform(0.5, 1.5) / 30  # per step, 0.5 to 1.5 Lyapunov units
    r0 = rng.uniform(0.001, 0.02)
    best = (r0 * np.exp(Lam * H)) ** 2
    other = best * rng.lognormal(0.5, 0.7, len(H))  # worse at every H
    corr = rng.uniform(0.0, 0.99, len(H))  # C >= 0
    C = corr * np.sqrt(best * other)
    # which one is CP does not matter; call best = E_P, other = E_C
    ec, ep = other, best
    curv = ec + ep - 2 * C
    u = (ep - C) / curv
    w = np.clip(u, 0, 1)
    hyb = w**2 * ec + (1 - w) ** 2 * ep + 2 * w * (1 - w) * C
    assert (hyb <= best + 1e-15).all()
    assert (2 * hyb >= np.minimum(ec, ep) * (1 - 1e-12)).all()  # P1(c) numerically
    t_best = np.argmax(np.sqrt(best + rho**2) > theta) + 1 if (np.sqrt(best + rho**2) > theta).any() else 240
    t_hyb = np.argmax(np.sqrt(hyb + rho**2) > theta) + 1 if (np.sqrt(hyb + rho**2) > theta).any() else 240
    if t_best == 240:
        continue
    n_cases += 1
    gain = t_hyb - t_best
    bound = np.log(2) / (2 * Lam) + 1
    worst_gain = max(worst_gain, gain - bound)
    n_viol += gain > bound
print(f"P1(d) with C >= 0 at every horizon: {n_cases} cases, violations of gain <= ln2/(2Lambda) + 1 step: {n_viol}; "
      f"worst (gain - bound) = {worst_gain:.2f} steps (negative means never reached)")

# Counterexample: negative C
n_viol = 0
for _ in range(500):
    Lam = 1 / 30
    r0 = 0.005
    best = (r0 * np.exp(Lam * H)) ** 2
    other = best * 1.2
    C = -0.9 * np.sqrt(best * other)  # strongly anticorrelated errors
    ec, ep = other, best
    curv = ec + ep - 2 * C
    w = np.clip((ep - C) / curv, 0, 1)
    hyb = w**2 * ec + (1 - w) ** 2 * ep + 2 * w * (1 - w) * C
    t_best = np.argmax(np.sqrt(best + rho**2) > theta) + 1
    exceed = np.sqrt(hyb + rho**2) > theta
    t_hyb = np.argmax(exceed) + 1 if exceed.any() else 240
    n_viol += (t_hyb - t_best) > np.log(2) / (2 * Lam) + 1
print(f"With C = -0.9 sqrt(E_C E_P): bound violated in {n_viol} of 500 cases "
      f"(example gain {t_hyb - t_best} steps against bound {np.log(2)/(2*Lam)+1:.1f}): P1(e) as expected")
