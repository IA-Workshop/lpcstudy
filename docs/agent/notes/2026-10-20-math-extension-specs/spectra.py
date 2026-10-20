"""Lyapunov spectra, the code's cache value, Benettin SE, and per-coordinate
orbit maxima for S1, S2, S3 (DEVELOPMENT, one thread).

(a) Full spectrum by an independent Benettin/QR (jacfwd of the code's RK4
    flow map), long run, block SE over 50 blocks; Kaplan-Yorke dimension.
(b) The value the code's ``lyapunov_record`` would cache: ``lyapunov_guarded``
    at interval = 20 max_dt, n_steps = 100_000, burn_in = 5_000 from the
    candidate initial_state; its block SE from the same settings re-run by the
    independent routine (same arithmetic up to the guard).
(c) max |s_i| per coordinate over the long orbit (for the orbit bound), and
    for Lorenz the analytic trapping-ellipsoid bound on |x|.
"""

import math
import sys
import time

import jax
import jax.numpy as jnp
import numpy as np
from scipy.optimize import minimize

from lpcstudy.systems import lyapunov_guarded, make_flow_step

from ext_common import CANDIDATES


def spectrum(sp, interval, n_steps, burn_in, n_blocks=50):
    step = make_flow_step(sp, sp.params, interval)
    jac = jax.jacfwd(step)
    dim = sp.dim

    def burn(s):
        return jax.lax.fori_loop(0, burn_in, lambda _, x: step(x), s)

    def body(carry, _):
        s, q = carry
        prop = jac(s) @ q
        q_new, r = jnp.linalg.qr(prop)
        sg = jnp.sign(jnp.diag(r))
        return (step(s), q_new * sg), (jnp.log(jnp.abs(jnp.diag(r))), jnp.abs(s))

    s0 = jax.jit(burn)(jnp.asarray(sp.initial_state, dtype=jnp.float64))
    (_, _), (growth, amax) = jax.jit(
        lambda c: jax.lax.scan(body, c, None, length=n_steps)
    )((s0, jnp.eye(dim)))
    growth = np.asarray(growth)
    lam = growth.sum(axis=0) / (n_steps * interval)
    per = n_steps // n_blocks
    blocks = growth[: per * n_blocks].reshape(n_blocks, per, dim).sum(axis=1) / (
        per * interval
    )
    se = blocks.std(axis=0, ddof=1) / math.sqrt(n_blocks)
    return lam, se, np.asarray(jnp.max(amax, axis=0)), growth


def kaplan_yorke(lam):
    lam = np.sort(lam)[::-1]
    cum = np.cumsum(lam)
    j = int(np.max(np.nonzero(cum >= 0)[0]))
    if j + 1 >= len(lam):
        return float(len(lam))
    return j + 1 + cum[j] / abs(lam[j + 1])


def lorenz_trapping_bound(sigma, r, beta):
    """Max of |x| over the ball V <= max_E V, V = x^2 + y^2 + (z - sigma - r)^2,
    E the ellipsoid sigma x^2 + y^2 + beta (z - (sigma+r)/2)^2 <= beta (sigma+r)^2/4
    outside which dV/dt < 0 (derived in the note, section 1.2)."""
    c = sigma + r

    def neg_v(p):
        x, y, z = p
        return -(x * x + y * y + (z - c) ** 2)

    cons = {
        "type": "ineq",
        "fun": lambda p: beta * c * c / 4
        - (sigma * p[0] ** 2 + p[1] ** 2 + beta * (p[2] - c / 2) ** 2),
    }
    best = 0.0
    for start in [(0, 0, 0), (0, c / 2, 0), (10, 10, 0), (0, -c / 2, 0), (5, -100, 2)]:
        res = minimize(neg_v, np.array(start, float), constraints=[cons], method="SLSQP")
        best = max(best, -res.fun)
    return math.sqrt(best)


which = sys.argv[1:] or list(CANDIDATES)
long_steps = {"S1": 1_000_000, "S2": 4_000_000, "S3": 1_000_000}
for key in which:
    sp = CANDIDATES[key]()
    interval = 20 * sp.max_dt
    t0 = time.time()
    lam, se, amax, growth = spectrum(sp, interval, long_steps[key], 5_000)
    dky = kaplan_yorke(lam)
    print(f"[{key}] {sp.name} dim {sp.dim} params {sp.params} max_dt {sp.max_dt}")
    print(f"  long run: interval {interval:g}, {long_steps[key]} steps = {long_steps[key]*interval:.0f} time units")
    print("  spectrum:", ", ".join(f"{v:+.5f} (se {s:.5f})" for v, s in zip(lam, se)))
    print(f"  lambda_max {lam.max():.5f} +- {se[np.argmax(lam)]:.5f}; LT {1/lam.max():.4f}; d_KY {dky:.3f}; "
          f"Delta = 1/(30 lambda) = {1/(30*lam.max()):.5f}; substeps ceil(Delta/max_dt) = {math.ceil(1/(30*lam.max())/sp.max_dt)}")
    print(f"  max|s_i| per coordinate over the long orbit: {np.array2string(amax, precision=3)}")
    # the exponent as the code would cache it
    t1 = time.time()
    lam_code, largest = lyapunov_guarded(sp, interval, 100_000, 5_000)
    lam_c, se_c, _, _ = spectrum(sp, interval, 100_000, 5_000)
    print(f"  code cache value lyapunov_guarded(interval {interval:g}, 100000, 5000) = {lam_code!r}, max|x| {largest:.3f} "
          f"[{time.time()-t1:.0f} s]; independent routine at the same settings {lam_c.max():.5f} se {se_c[np.argmax(lam_c)]:.5f} "
          f"(relative se {se_c[np.argmax(lam_c)]/lam_c.max():.3%})")
    print(f"  steps for a 1% relative se at this interval: about {int((se_c[np.argmax(lam_c)]/lam_c.max()/0.01)**2*100_000):,}")
    if key == "S2":
        p = sp.params
        print(f"  analytic trapping bound on |x| (Lorenz, sigma {p['sigma']}, r {p['rho']}, beta {p['beta']:.4f}): "
              f"{lorenz_trapping_bound(p['sigma'], p['rho'], p['beta']):.2f}; for r = 28: {lorenz_trapping_bound(10.0, 28.0, 8/3):.2f}")
        # local growth over 1-LT windows: bimodality of the per-window exponent
        lt_steps = int(round(1 / lam.max() / interval))
        g1 = growth[:, 0]
        per_window = g1[: (len(g1) // lt_steps) * lt_steps].reshape(-1, lt_steps).sum(axis=1) / (lt_steps * interval)
        q = np.quantile(per_window, [0.05, 0.25, 0.5, 0.75, 0.95])
        print(f"  per-1LT-window largest-exponent estimate: quantiles 5/25/50/75/95 = {np.array2string(q, precision=3)}; "
              f"fraction of windows below 0.1: {np.mean(per_window < 0.1):.3f}; mean {per_window.mean():.4f}")
        hist, edges = np.histogram(per_window, bins=np.linspace(-1, 3, 17))
        print("  histogram of per-window exponents (bins of 0.25 from -1 to 3):", hist.tolist())
    print(f"  [{time.time()-t0:.0f} s]")
    print()
