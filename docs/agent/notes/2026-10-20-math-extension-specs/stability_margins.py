"""RK4 frozen-coefficient stability margins at the proposed max_dt for every
candidate (DEVELOPMENT): along a 200 000-step orbit at Delta, sampled every 5
steps, the eigenvalues of the Jacobian (jax.jacfwd of the field) and
max_i |R(h lambda_i)| with R the RK4 stability polynomial; the margin is
2.785 / (h max|Re lambda|) for the stiff (negative real) modes and the
minimum distance of h lambda to the stability-region boundary is reported as
|R| itself (|R| <= 1 for every decaying mode means stable; the growing
physical modes give |R| = 1 + O(h lambda))."""

import math
import sys

import jax
import jax.numpy as jnp
import numpy as np

from lpcstudy.systems import lyapunov_guarded, make_flow_step, simulate_trajectory

from ext_common import CANDIDATES

for key in (sys.argv[1:] or ["S1", "S2", "S3", "S4", "S5", "S6"]):
    sp = CANDIDATES[key]()
    lam, _ = lyapunov_guarded(sp, 20 * sp.max_dt, 100_000, 5_000)
    interval = 1.0 / (30 * lam)
    h = interval / math.ceil(interval / sp.max_dt)
    step = make_flow_step(sp, sp.params, interval)
    orbit = simulate_trajectory(step, jnp.asarray(sp.initial_state), 3000 + 200_000)[3000::5]
    jac = jax.jit(jax.vmap(jax.jacfwd(lambda s: sp.field_fn(s, sp.params))))
    J = np.asarray(jac(jnp.asarray(orbit)))
    ev = np.linalg.eigvals(J)  # (n, m)
    hl = h * ev
    R = 1 + hl + hl**2 / 2 + hl**3 / 6 + hl**4 / 24
    decaying = ev.real < 0
    re_max = np.max(np.abs(ev.real[decaying]))
    worst = np.max(np.abs(R[decaying]))
    print(f"[{key}] {sp.name}: max_dt {sp.max_dt}, h {h:.5f}; along 40 000 sampled states: max |Re lambda| (decaying) {re_max:.1f}, max |lambda| {np.max(np.abs(ev)):.1f}, "
          f"max |h lambda| {np.max(np.abs(hl)):.3f}; max |R(h lambda)| over decaying modes {worst:.4f} ({'stable' if worst <= 1 + 1e-9 else 'UNSTABLE'}); "
          f"real-axis margin 2.785/(h max|Re lambda|) = {2.785/(h*re_max):.1f}; the state coordinate driving it: max|x| {np.abs(orbit[:,0]).max():.1f}")
