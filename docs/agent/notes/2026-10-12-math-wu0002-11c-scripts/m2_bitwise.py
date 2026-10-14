"""M2 (WU-0002.11c): does a running max / first-failure carry change the Benettin float path?

DEVELOPMENT, no seed involved (deterministic orbits from the registry start states).
Old loop: verbatim copy of systems.estimate_lyapunov at 529b90b.
New loops: (A) carry in the averaging scan only, final burn-in state checked;
(B) carry in the burn-in fori_loop as well (the tightening).
"""
import struct
import sys
import time

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[4]))
import jax
import jax.numpy as jnp

from lpcstudy.systems import SYSTEMS, make_flow_step

BOUNDS = {"lorenz63": 40.0, "rossler": 25.0, "chua": 3.0}


def old(spec, interval, n_steps, burn_in, init=None):
    step_fn = make_flow_step(spec, spec.params, interval)
    jac_fn = jax.jacfwd(step_fn)
    state = jnp.asarray(spec.initial_state if init is None else init, dtype=jnp.float64)
    state = jax.jit(lambda s: jax.lax.fori_loop(
        0, burn_in, lambda _, x: step_fn(x), s))(state)

    def body(carry, _):
        current, basis = carry
        propagated = jac_fn(current) @ basis
        q_mat, r_mat = jnp.linalg.qr(propagated)
        signs = jnp.sign(jnp.diag(r_mat))
        q_mat = q_mat * signs
        log_growth = jnp.log(jnp.abs(jnp.diag(r_mat)))
        return (step_fn(current), q_mat), log_growth[0]

    basis = jnp.eye(spec.dim)
    _, growth = jax.jit(lambda c: jax.lax.scan(body, c, None, length=n_steps))(
        (state, basis))
    return float(jnp.sum(growth) / (n_steps * interval))


def _update(state, k, mx, fail, bound):
    a = jnp.abs(state[0])
    bad = jnp.logical_not(jnp.all(jnp.isfinite(state)) & (a <= bound))
    fail = jnp.where((fail < 0) & bad, k, fail)
    return jnp.maximum(mx, a), fail


def new(spec, interval, n_steps, burn_in, bound, guard_burn, init=None):
    step_fn = make_flow_step(spec, spec.params, interval)
    jac_fn = jax.jacfwd(step_fn)
    state = jnp.asarray(spec.initial_state if init is None else init, dtype=jnp.float64)
    mx0 = jnp.asarray(0.0)
    f0 = jnp.asarray(-1, dtype=jnp.int64)
    if guard_burn:
        def bbody(k, c):
            s, mx, fail = c
            mx, fail = _update(s, k, mx, fail, bound)
            return (step_fn(s), mx, fail)
        state, mx, fail = jax.jit(lambda c: jax.lax.fori_loop(0, burn_in, bbody, c))(
            (state, mx0, f0))
    else:
        state = jax.jit(lambda s: jax.lax.fori_loop(
            0, burn_in, lambda _, x: step_fn(x), s))(state)
        mx, fail = mx0, f0

    def body(carry, _):
        current, basis, k, mx, fail = carry
        mx, fail = _update(current, k, mx, fail, bound)
        propagated = jac_fn(current) @ basis
        q_mat, r_mat = jnp.linalg.qr(propagated)
        signs = jnp.sign(jnp.diag(r_mat))
        q_mat = q_mat * signs
        log_growth = jnp.log(jnp.abs(jnp.diag(r_mat)))
        return (step_fn(current), q_mat, k + 1, mx, fail), log_growth[0]

    basis = jnp.eye(spec.dim)
    (last, _, _, mx, fail), growth = jax.jit(
        lambda c: jax.lax.scan(body, c, None, length=n_steps))(
        (state, basis, jnp.asarray(burn_in, dtype=jnp.int64), mx, fail))
    lam = float(jnp.sum(growth) / (n_steps * interval))
    return lam, float(mx), int(fail)


def bits(v):
    return struct.pack("<d", v).hex()


if __name__ == "__main__":
    configs = [(100_000, 5_000), (1_000, 50), (20_000, 1_000)]
    for name, spec in SYSTEMS.items():
        interval = 20 * spec.max_dt
        for n_steps, burn in configs:
            t0 = time.time()
            lo = old(spec, interval, n_steps, burn)
            la, ma, fa = new(spec, interval, n_steps, burn, BOUNDS[name], False)
            lb, mb, fb = new(spec, interval, n_steps, burn, BOUNDS[name], True)
            print(f"{name:9s} n={n_steps:6d} burn={burn:5d} old={lo!r} {bits(lo)} "
                  f"A_eq={bits(la) == bits(lo)} B_eq={bits(lb) == bits(lo)} "
                  f"maxA={ma:.4f} maxB={mb:.4f} failA={fa} failB={fb} "
                  f"({time.time() - t0:.1f}s)", flush=True)
