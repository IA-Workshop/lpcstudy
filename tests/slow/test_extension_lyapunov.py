"""Test A6: the largest Lyapunov exponent of the extension systems (WU-0021).

The study's time unit is one Lyapunov time, ``1 / lambda_max``, with
``lambda_max`` from Benettin's method (``systems.lyapunov_guarded``, cached by
``data.lyapunov_record``). For each extension system (S1 ``rossler_hyper``,
S2 ``lorenz63_r166``, S3 ``rossler_z``) this test checks three things.

1. **Regression guard (not correctness evidence), host- and build-bound.**
   ``lyapunov_record`` on a fresh cache equals the value of the specification
   note section 0 (``docs/agent/notes/2026-10-20-math-extension-specs.md``) to
   a relative 1e-12, and its orbit maximum is below the spec's bound. The
   expected values were produced by the code's own ``lyapunov_guarded`` on
   the development host (Intel i9-14900K, CPU, jax and jaxlib 0.11.2), so this
   compares the code with its earlier output (LPC.PC.21). A chaotic Benettin
   run of 1e6 to 4e6 steps decorrelates under any change of rounding, so on
   another CPU or XLA build the value differs at the level of its standard
   error (0.2% to 1%), not at 1e-12: the test is then skipped with the
   reason stated, and only check 2 applies. The tolerance is 1e-12 relative
   (the observed difference on this host is 0 for S2 and S3 and 6.7e-16 for
   S1). The test name starts with ``test_regression_``.
2. **The code agrees with an independent Benettin/QR implementation.** The
   reference below is written in this file and imports nothing from
   ``lpcstudy.systems``: its own fields, its own hand-derived Jacobians, its
   own RK4 on the system together with the tangent matrix (the variational
   equations; RK4 on them is exactly the derivative of the RK4 flow map, so the
   discretization is the code's), its own QR re-orthonormalization. Both start
   from the spec's initial state and use the interval ``20 max_dt`` with 20
   substeps and 5 000 burn-in steps, as ``lyapunov_record`` does.
   The chaotic orbits separate after a few dozen steps (rounding differs), so
   the two numbers agree only statistically: ``|lambda_code - lambda_ref| <=
   3 sqrt(SE_code^2 + SE_ref^2)``, with the standard errors from 20 batch means
   of ``n / 20`` steps each. ``SE_ref`` uses the reference's own batch means.
   ``lyapunov_guarded`` returns only a total, so ``SE_code`` is the standard
   error of 20 calls of it, one from each batch start state of the reference
   orbit (``n / 20`` steps each, 5 000 burn-in steps). The 3 is the z of a
   two-sided test at about 0.3% for a normal difference. The batch SE of
   long-memory systems underestimates the true uncertainty (S2: about 2% true
   against 1% block, specification note section 1.2), which makes the test
   stricter, not looser; the specification note's own run agrees with the
   cached value within 1 SE. This is the correctness check, valid on any
   host; its tolerance is the 3 sigma above, not the 1e-12 of check 1.
3. **A literature value is reported, and asserted only where confirmed.** S1:
   0.1121 (Ramasubramanian and Sriram, arXiv:chao-dyn/9909029, Table 1,
   standard method; the researcher read it directly; their second method gives
   0.1128). Relative difference printed; asserted within 3% (the tolerance of
   ``report.LYAPUNOV_REFERENCES``; the specification note's own value is
   +0.4%). S2 and S3 have no confirmed published value, so nothing is
   asserted (the S3 value is compared with the registry Rossler's cached
   0.07193978510879935 in the printed output only).

Slow tier (``@pytest.mark.slow``): about 3.5 times ``lyapunov_steps`` Benettin
steps per system (the cached run, the reference, and the 20 batch runs of the
code), measured in the unit log; the specification note timed the cached run
alone at 7 s (S1), 23 s (S2) and 6 s (S3) on one thread. Run once, by the
developer of the unit, with the output in the unit log. DEVELOPMENT only: no
seed is involved (the orbits start from the spec's fixed initial state).

No tolerance is to be changed to pass (PRIME.2).
"""

from __future__ import annotations

import dataclasses
import json
import math
import struct
from functools import partial

import jax
import jax.numpy as jnp
import numpy as np
import pytest

from lpcstudy.data import lyapunov_record
from lpcstudy.systems import SYSTEMS, lyapunov_guarded

pytestmark = pytest.mark.slow

N_BATCHES = 20
BURN_IN = 5_000
SUBSTEPS = 20  # interval = 20 max_dt, so exactly 20 RK4 substeps of max_dt

# Specification note section 0: expected cached exponents (this host, bitwise).
EXPECTED = {
    "rossler_hyper": 0.11251662457254265,
    "lorenz63_r166": 0.6217010154674514,
    "rossler_z": 0.07133265490530956,
}


# --------------------------------------------- independent reference code


def _field_s1(s):
    x, y, z, w = s
    a, b, c, d = 0.25, 3.0, 0.5, 0.05
    return jnp.stack([-y - z, x + a * y + w, b + x * z, -c * z + d * w])


def _jac_s1(s):
    x, y, z, w = s
    a, c, d = 0.25, 0.5, 0.05
    return jnp.array(
        [
            [0.0, -1.0, -1.0, 0.0],
            [1.0, a, 0.0, 1.0],
            [z, 0.0, x, 0.0],
            [0.0, 0.0, -c, d],
        ]
    )


def _field_s2(s):
    x, y, z = s
    sg, rho, bt = 10.0, 166.1, 8.0 / 3.0
    return jnp.stack([sg * (y - x), x * (rho - z) - y, x * y - bt * z])


def _jac_s2(s):
    x, y, z = s
    sg, rho, bt = 10.0, 166.1, 8.0 / 3.0
    return jnp.array(
        [[-sg, sg, 0.0], [rho - z, -1.0, -x], [y, x, -bt]]
    )


def _field_s3(s):
    z, x, y = s
    a, b, c = 0.2, 0.2, 5.7
    return jnp.stack([b + z * (x - c), -y - z, x + a * y])


def _jac_s3(s):
    z, x, y = s
    a, c = 0.2, 5.7
    return jnp.array(
        [[x - c, z, 0.0], [-1.0, 0.0, -1.0], [0.0, 1.0, a]]
    )


# name -> (field, Jacobian, initial state, max_dt), typed from the note
# section 0 (not read from the registry).
REFERENCE = {
    "rossler_hyper": (_field_s1, _jac_s1, (-10.0, -6.0, 0.0, 10.0), 0.01),
    "lorenz63_r166": (_field_s2, _jac_s2, (1.0, 1.0, 1.0), 0.002),
    "rossler_z": (_field_s3, _jac_s3, (0.0, 1.0, 1.0), 0.04),
}


def _rk4_pair(field, jac, dt, s, q):
    """One RK4 step of the state and of the tangent matrix ``q`` together."""

    def deriv(state, tangent):
        return field(state), jac(state) @ tangent

    k1s, k1q = deriv(s, q)
    k2s, k2q = deriv(s + 0.5 * dt * k1s, q + 0.5 * dt * k1q)
    k3s, k3q = deriv(s + 0.5 * dt * k2s, q + 0.5 * dt * k2q)
    k4s, k4q = deriv(s + dt * k3s, q + dt * k3q)
    s_next = s + dt / 6.0 * (k1s + 2.0 * k2s + 2.0 * k3s + k4s)
    q_next = q + dt / 6.0 * (k1q + 2.0 * k2q + 2.0 * k3q + k4q)
    return s_next, q_next


def _flow(name, s, q):
    """One observation interval (``SUBSTEPS`` RK4 substeps) of state and tangent."""
    field, jac, _, dt = REFERENCE[name]

    def body(_, carry):
        return _rk4_pair(field, jac, dt, *carry)

    return jax.lax.fori_loop(0, SUBSTEPS, body, (s, q))


@partial(jax.jit, static_argnames=("name",))
def _post_burn_state(name, state):
    """Return the state after ``BURN_IN`` steps and the largest |x| seen."""
    identity = jnp.eye(state.shape[0])

    def step(carry, _):
        s, big = carry
        return (_flow(name, s, identity)[0], jnp.maximum(big, jnp.abs(s[0]))), None

    return jax.lax.scan(
        step, (state, jnp.asarray(0.0)), None, length=BURN_IN
    )[0]


@partial(jax.jit, static_argnames=("name", "n_steps"))
def _benettin_batch(name, state, n_steps):
    """Average the log growth of the first QR direction over ``n_steps`` steps.

    Returns ``(sum of log |R_00|, final state, max |x| over the steps)``.
    """
    identity = jnp.eye(state.shape[0])

    def body(carry, _):
        s, q, big = carry
        s_next, tangent = _flow(name, s, q)
        q_next, r = jnp.linalg.qr(tangent)
        # The sign convention of QR does not matter for log |R_00|.
        return (s_next, q_next, jnp.maximum(big, jnp.abs(s[0]))), jnp.log(
            jnp.abs(r[0, 0])
        )

    (state, _, big), growth = jax.lax.scan(
        body, (state, identity, jnp.asarray(0.0)), None, length=n_steps
    )
    return jnp.sum(growth), state, big


def reference_benettin(name: str, n_steps: int):
    """Return the reference exponent, its batch SE, the batch start states.

    The orbit runs from the spec's initial state through ``BURN_IN`` steps and
    then ``N_BATCHES`` batches of ``n_steps / N_BATCHES`` steps. The exponent
    is per natural time unit (interval ``20 max_dt``).
    """
    _, _, initial, max_dt = REFERENCE[name]
    interval = SUBSTEPS * max_dt
    per_batch = n_steps // N_BATCHES
    state, biggest = _post_burn_state(name, jnp.asarray(initial, dtype=jnp.float64))
    biggest = float(biggest)
    sums, starts = [], []
    for _ in range(N_BATCHES):
        starts.append(np.asarray(state))
        total, state, big = _benettin_batch(name, state, per_batch)
        sums.append(float(total))
        biggest = max(biggest, float(big))
    batch_lambda = np.asarray(sums) / (per_batch * interval)
    lam = float(np.mean(batch_lambda))
    se = float(np.std(batch_lambda, ddof=1) / math.sqrt(N_BATCHES))
    return lam, se, starts, biggest


# ------------------------------------------------------------------ test


def _build_matches_the_recorded_one() -> str | None:
    """Return why this is not the recorded host and build, or ``None`` if it is."""
    cpu = ""
    try:
        with open("/proc/cpuinfo") as handle:
            for line in handle:
                if line.startswith("model name"):
                    cpu = line.split(":", 1)[1].strip()
                    break
    except OSError:
        pass
    if "i9-14900K" not in cpu:
        return f"CPU {cpu!r} is not the recorded Intel i9-14900K"
    if jax.default_backend() != "cpu":
        return f"backend {jax.default_backend()!r} is not cpu"
    if jax.__version__ != "0.11.2":
        return f"jax {jax.__version__} is not the recorded 0.11.2"
    return None


@pytest.fixture(scope="module", params=sorted(EXPECTED))
def cached(request, tmp_path_factory) -> tuple[str, float, float]:
    """Compute ``lyapunov_record`` once per system: (name, value, orbit max)."""
    name = request.param
    spec = SYSTEMS[name]
    path = tmp_path_factory.mktemp(name) / "lyapunov.json"
    value, orbit_max = lyapunov_record(spec, path)
    assert json.loads(path.read_text())[name]["lambda_max"] == value
    return name, value, orbit_max


def test_regression_cached_lambda_equals_the_recorded_value(cached) -> None:
    """Regression guard, host- and build-bound: cached lambda equals the note's.

    This compares the code with its own earlier output (specification note
    section 0, produced by ``lyapunov_guarded`` on the Intel i9-14900K, CPU,
    jax 0.11.2), so it is not correctness evidence; the independent Benettin
    test below is. Tolerance: relative 1e-12 (the observed differences are 0 for
    S2 and S3 and 6.7e-16 for S1 on the recorded host). Skipped, with the
    reason, on another CPU or XLA build, where the Benettin value differs at
    the level of its standard error. The orbit maximum must be below the bound.
    """
    name, value, orbit_max = cached
    spec = SYSTEMS[name]
    assert orbit_max < spec.orbit_bound
    reason = _build_matches_the_recorded_one()
    if reason is not None:
        pytest.skip(f"host-bound regression guard not applicable: {reason}")
    bitwise = struct.pack("<d", value) == struct.pack("<d", EXPECTED[name])
    print(f"[A6 {name}] cached {value!r}, bitwise as recorded: {bitwise}")
    assert abs(value / EXPECTED[name] - 1.0) <= 1e-12, (value, EXPECTED[name])


def test_extension_lyapunov_matches_an_independent_benettin_run(
    cached, capsys
) -> None:
    """A6 (correctness): cached lambda against an independent Benettin/QR run.

    Valid on any host. See the module docstring for the reference, the
    tolerance ``3 sqrt(SE_code^2 + SE_ref^2)`` (20 batch means each) and its
    justification; the 1e-12 of the regression guard does not apply here.
    """
    name, cached_value, orbit_max = cached
    spec = SYSTEMS[name]
    n_steps = spec.lyapunov_steps
    interval = 20 * spec.max_dt

    lam_ref, se_ref, starts, ref_max = reference_benettin(name, n_steps)
    assert ref_max < spec.orbit_bound

    per_batch = n_steps // N_BATCHES
    batch_code = []
    for state in starts:
        shifted = dataclasses.replace(spec, initial_state=tuple(state))
        lam_k, _ = lyapunov_guarded(shifted, interval, per_batch, BURN_IN)
        batch_code.append(lam_k)
    se_code = float(np.std(batch_code, ddof=1) / math.sqrt(N_BATCHES))
    lam_batches = float(np.mean(batch_code))

    tolerance = 3.0 * math.sqrt(se_code**2 + se_ref**2)
    with capsys.disabled():
        print(
            f"\n[A6 {name}] reference {lam_ref:.6f} +- {se_ref:.6f}; code "
            f"batches {lam_batches:.6f} +- {se_code:.6f}; |cached - ref| = "
            f"{abs(cached_value - lam_ref):.3e}, tolerance {tolerance:.3e}; "
            f"relative SE of the cached value (code batches) "
            f"{100 * se_code / cached_value:.2f}%; orbit max code "
            f"{orbit_max:.4g}, reference {ref_max:.4g}, bound "
            f"{spec.orbit_bound:g}"
        )
        if name == "rossler_hyper":
            print(
                f"[A6 {name}] published 0.1121 (Ramasubramanian and Sriram): "
                f"relative difference {100 * (cached_value / 0.1121 - 1):+.2f}%"
            )
        if name == "rossler_z":
            reg = 0.07193978510879935
            print(
                f"[A6 {name}] registry Rossler cached {reg}: relative "
                f"difference {100 * (cached_value / reg - 1):+.2f}%"
            )
    assert abs(cached_value - lam_ref) <= tolerance
    if name == "rossler_hyper":
        assert abs(cached_value / 0.1121 - 1.0) <= 0.03
