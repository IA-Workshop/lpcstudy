"""Tail of |x| (coordinate 0) on long orbits of S1, S2, S3 at the study's
Delta, for the orbit bound (DEVELOPMENT). Block maxima over blocks of
100 000 steps, the overall maximum, and the number of steps with |x| above
fractions of the proposed bound."""

import sys
import time

import jax
import jax.numpy as jnp
import numpy as np

from lpcstudy.systems import lyapunov_guarded, make_flow_step

from ext_common import CANDIDATES

LT = 30
STEPS = {"S1": 4_000_000, "S2": 2_000_000, "S3": 2_000_000}
which = sys.argv[1:] or list(CANDIDATES)
for key in which:
    sp = CANDIDATES[key]()
    t0 = time.time()
    lam, _ = lyapunov_guarded(sp, 20 * sp.max_dt, 100_000, 5_000)
    interval = 1.0 / (LT * lam)
    step = make_flow_step(sp, sp.params, interval)
    n_blocks, per = STEPS[key] // 100_000, 100_000

    def block(s, _):
        def body(c, _):
            nxt = step(c)
            return nxt, jnp.abs(nxt[0])
        s_end, absx = jax.lax.scan(body, s, None, length=per)
        return s_end, (jnp.max(absx), jnp.sum(absx > 0.5 * sp.orbit_bound), jnp.sum(absx > 0.75 * sp.orbit_bound))
    s0 = jnp.asarray(sp.initial_state, dtype=jnp.float64)
    s0 = jax.jit(lambda s: jax.lax.fori_loop(0, 3000, lambda _, x: step(x), s))(s0)
    _, (bmax, n_half, n_three) = jax.jit(lambda s: jax.lax.scan(block, s, None, length=n_blocks))(s0)
    bmax = np.asarray(bmax)
    print(f"[{key}] {sp.name}: {STEPS[key]} steps x Delta {interval:.5f} = {STEPS[key]*interval:.0f} time units = {STEPS[key]/LT:.0f} LT; bound {sp.orbit_bound}")
    print(f"  max |x| {bmax.max():.3f}; block maxima (100k steps each) quantiles 10/50/90% {np.array2string(np.quantile(bmax, [.1,.5,.9]), precision=2)}; "
          f"steps with |x| > 0.5 B: {int(np.sum(np.asarray(n_half)))}, > 0.75 B: {int(np.sum(np.asarray(n_three)))}; ratio B / max {sp.orbit_bound/bmax.max():.2f}  [{time.time()-t0:.0f} s]")
