"""The exponent the code would cache with a per-system Benettin run length
(the additive field ``lyapunov_steps`` that WU-0021.4 anticipates), computed by
the code's own ``lyapunov_guarded`` at interval 20 max_dt, burn-in 5 000, and
the block SE of the independent routine at the same settings (DEVELOPMENT)."""

import math
import time

import jax
import jax.numpy as jnp
import numpy as np

from lpcstudy.systems import lyapunov_guarded, make_flow_step

from ext_common import CANDIDATES


def block_se(sp, interval, n_steps, burn_in, n_blocks=50):
    step = make_flow_step(sp, sp.params, interval)
    jac = jax.jacfwd(step)

    def body(carry, _):
        s, q = carry
        qn, r = jnp.linalg.qr(jac(s) @ q)
        return (step(s), qn * jnp.sign(jnp.diag(r))), jnp.log(jnp.abs(r[0, 0]))

    s0 = jax.jit(lambda s: jax.lax.fori_loop(0, burn_in, lambda _, x: step(x), s))(jnp.asarray(sp.initial_state, dtype=jnp.float64))
    _, g = jax.jit(lambda c: jax.lax.scan(body, c, None, length=n_steps))((s0, jnp.eye(sp.dim)))
    g = np.asarray(g)
    per = n_steps // n_blocks
    blocks = g[: per * n_blocks].reshape(n_blocks, per).sum(axis=1) / (per * interval)
    return g.sum() / (n_steps * interval), blocks.std(ddof=1) / math.sqrt(n_blocks)


import sys
STEPS = {"S1": 1_000_000, "S2": 4_000_000, "S3": 1_000_000, "S4": 2_000_000, "S5": 2_000_000, "S6": 1_000_000}
for key in (sys.argv[1:] or ["S1", "S2", "S3"]):
    n = STEPS[key]
    sp = CANDIDATES[key]()
    interval = 20 * sp.max_dt
    t0 = time.time()
    lam, mx = lyapunov_guarded(sp, interval, n, 5_000)
    lam_i, se = block_se(sp, interval, n, 5_000)
    print(f"[{key}] {sp.name}: lyapunov_guarded(interval {interval:g}, n_steps {n}, burn_in 5000) = {lam!r}; max|x| {mx:.3f}; "
          f"{n*interval:.0f} time units; independent {lam_i:.6f} +- {se:.6f} (relative {se/lam_i:.2%}); Delta = {1/(30*lam):.6f}; "
          f"substeps {math.ceil(1/(30*lam)/sp.max_dt)}  [{time.time()-t0:.0f} s]")
