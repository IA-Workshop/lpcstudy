"""Tests for ``lpcstudy.systems``: the system registry, RK4 and the orbit guard.

``systems.py`` defines the three chaotic systems of the study and turns each
into a flow map built from fixed-step RK4 (a fourth-order Runge-Kutta ODE
solver). These tests give code verification of that flow map against exact
solutions (WU-0005), check the registry of systems (WU-0002.1), and check the
orbit guard that refuses a run when an orbit blows up or leaves the attractor
bound (WU-0002.11c, DEF-0015).
"""

from __future__ import annotations

import dataclasses
import math
import struct
from fractions import Fraction

import jax.numpy as jnp
import numpy as np
import pytest
from scipy.linalg import expm

from lpcstudy import systems
from lpcstudy.systems import (
    SYSTEMS,
    SystemSpec,
    make_flow_step,
    simulate_trajectory,
)

# Linear test system x' = A x, A = S B S^-1 (A non-normal, |lambda|max ~ 2.0).
_B = np.array([[-0.1, -2.0, 0.0], [2.0, -0.1, 0.0], [0.0, 0.0, -0.5]])
_S = np.array([[1.0, 0.5, 0.0], [0.0, 1.0, 0.3], [0.2, 0.0, 1.0]])
_A = _S @ _B @ np.linalg.inv(_S)
_X0 = np.array([1.0, 0.5, -0.3])
# Dyadic steps: ceil(1 / h) is exactly 8, 16, 32 substeps.
_STEPS = (1 / 8, 1 / 16, 1 / 32)


def _spec(
    field_fn, dim: int, initial: tuple[float, ...], max_dt: float
) -> SystemSpec:
    """Build a ``SystemSpec`` in the test (no registered system is used)."""
    return SystemSpec(
        name="test",
        field_fn=field_fn,
        params={},
        dim=dim,
        observed_index=0,
        initial_state=initial,
        max_dt=max_dt,
    )


def _linear_error(max_dt: float) -> tuple[np.ndarray, np.ndarray]:
    """Return (output, exact - output) of the RK4 flow for x' = Ax, T = 1."""
    a_jax = jnp.asarray(_A)
    spec = _spec(lambda s, p: a_jax @ s, 3, tuple(_X0), max_dt)
    out = make_flow_step(spec, {}, 1.0)(jnp.asarray(_X0))
    assert out.dtype == jnp.float64
    out = np.asarray(out)
    return out, expm(_A) @ _X0 - out


def test_rk4_observed_order_is_four() -> None:
    """RK4 on x' = A x matches ``expm(A t) x0`` with observed order 4.

    The "observed order" is the slope of log(error) against log(step size).
    It should be 4 for a fourth-order method. The leading error constant is
    also checked.

    Reference: the exact solution ``scipy.linalg.expm(A T) @ x0``
    (independent of the integrator; it agrees with a 50-digit Taylor series to
    1.2e-15). Here A = S B S^-1 with B = [[-0.1, -2, 0], [2, -0.1, 0],
    [0, 0, -0.5]] and S = [[1, .5, 0], [0, 1, .3], [.2, 0, 1]]. The
    eigenvalues are -0.1 +- 2i and -0.5 (asserted), x0 = (1, 0.5, -0.3),
    T = 1, and ``max_dt`` = h in {1/8, 1/16, 1/32} through ``make_flow_step``
    on a ``SystemSpec`` built here.

    Premises (asserted): the eigenvalues are as stated; the error at h = 1/8 is
    below 1e-3 and at h = 1/32 above 1e-11 (round-off is about 1e-14, so the
    finest error is well above it); the output is float64.

    Tolerances (applied-mathematician, WU-0005 log, which tightens the
    roadmap's [3.8, 4.2]). (1) The observed order log2(e_h / e_{h/2}) is in
    [3.9, 4.1] for both pairs. The error is
    (T h^4 / 120) ||A^5 e^{AT} x0|| + O(h^5), so the observed order deviates
    from 4 by O(h). The measured values are 4.042 and 4.024 (deviations 0.042
    and 0.024, halving with h), inside the band by a factor of 2.4 or more;
    round-off moves it by about 1e-8. (2) The leading constant at h = 1/32:
    ||(x_ref - x_h) - L h^4||_2 <= 0.10 ||L h^4||_2 with
    L = (T / 120) A^5 expm(A T) x0. The measured value is 0.043, the O(h)
    relative size of the next term, and the vector form also checks the sign
    and direction. The measured errors are 6.94e-5, 4.21e-6 and 2.59e-7
    (about 0.27 h^4).

    Limitation: a linear field exercises only the stability polynomial, which
    is shared by all 4-stage order-4 methods; it cannot see the nonlinear
    order conditions. ``test_rk4_observed_order_nonlinear_scalar`` adds a
    partial check of them (see its docstring for what it does not cover).
    """
    assert np.allclose(
        np.sort_complex(np.linalg.eigvals(_A)),
        np.sort_complex(np.array([-0.5, -0.1 - 2j, -0.1 + 2j])),
    )
    outputs = [_linear_error(h) for h in _STEPS]
    errors = [float(np.linalg.norm(err)) for _, err in outputs]
    assert errors[0] < 1e-3
    assert errors[2] > 1e-11
    for coarse, fine in ((0, 1), (1, 2)):
        order = float(np.log2(errors[coarse] / errors[fine]))
        assert 3.9 <= order <= 4.1, (coarse, order)

    leading = (
        (1.0 / 120.0)
        * np.linalg.matrix_power(_A, 5)
        @ expm(_A)
        @ _X0
        * _STEPS[2] ** 4
    )
    residual = float(np.linalg.norm(outputs[2][1] - leading))
    assert residual <= 0.10 * float(np.linalg.norm(leading))


def test_rk4_observed_order_nonlinear_scalar() -> None:
    """RK4 on y' = y^2, y(0) = 0.5 has observed order 4 (exact y(1) = 1).

    Reference: the closed form y(t) = y0 / (1 - y0 t), so
    y(1) = 0.5 / 0.5 = 1 exactly.

    What it checks: through the nonlinearity (f' and f'' are not zero), the
    order-1 to order-3 conditions (including sum b c^2 = 1/3), plus one
    weighted sum of the three non-tall order-4 conditions (for f = y^2 their
    elementary differentials are all proportional to y^5, so a single scalar
    ODE sees only one combination of their defects).

    What it does not check: sum b c^3 = 1/4, because f''' = 0 for y' = y^2, so
    that term never enters the error; and it cannot tell the individual
    order-4 conditions apart. It is a partial check of the nonlinear order
    conditions, not a proof of all of them. The linear test cannot see them
    at all. ``make_flow_step`` takes the field through
    ``SystemSpec.field_fn``, so the spec is built here with dim = 1, T = 1
    and h in {1/8, 1/16, 1/32}.

    Tolerance: the observed order is in [3.9, 4.1] for both pairs, the band
    used for the linear test. The applied-mathematician measured errors
    2.90e-6, 1.84e-7 and 1.16e-8 and orders 3.975 and 3.993 (WU-0005 log).
    The deviation from 4 is O(h), so the margin to 3.9 is at least 0.075. The
    errors are far above round-off (1e-16) and below 1e-5.
    """
    errors = []
    for h in _STEPS:
        spec = _spec(lambda s, p: s * s, 1, (0.5,), h)
        out = make_flow_step(spec, {}, 1.0)(jnp.asarray([0.5]))
        assert out.dtype == jnp.float64
        errors.append(abs(1.0 - float(out[0])))
    assert errors[0] < 1e-5 and errors[2] > 1e-12
    for coarse, fine in ((0, 1), (1, 2)):
        order = float(np.log2(errors[coarse] / errors[fine]))
        assert 3.9 <= order <= 4.1, (coarse, order)


def test_flow_step_respects_max_dt() -> None:
    """``max_dt`` caps the step: 0.3 and 0.25 both give 4 substeps of 0.25.

    Over T = 1, the substep count is ``ceil(T / max_dt)``.

    Reference: construction. ``substeps = ceil(T / max_dt)`` is
    ceil(3.33) = 4 for 0.3 and exactly 4 for 0.25, so dt = 0.25 in both and
    the arithmetic is identical. The step is never larger than ``max_dt``
    (0.25 <= 0.3). Contrast: ``max_dt`` = 0.5 gives 2 substeps of 0.5, whose
    result differs from the 0.25 result by the truncation error (about
    0.27 h^4 = 1.7e-2 by extrapolating the measured errors; asserted only
    above 1e-6), many orders above the tolerance.

    Tolerance: ``atol=1e-15``, set before the run. The operations are
    identical, so the results should be bitwise equal; 1e-15 allows one ulp of
    XLA reordering on a state of norm about 1.
    """
    a_jax = jnp.asarray(_A)
    spec = lambda max_dt: _spec(  # noqa: E731
        lambda s, p: a_jax @ s, 3, tuple(_X0), max_dt
    )
    x0 = jnp.asarray(_X0)
    capped = np.asarray(make_flow_step(spec(0.3), {}, 1.0)(x0))
    exact_quarter = np.asarray(make_flow_step(spec(0.25), {}, 1.0)(x0))
    np.testing.assert_allclose(capped, exact_quarter, rtol=0, atol=1e-15)
    coarse = np.asarray(make_flow_step(spec(0.5), {}, 1.0)(x0))
    assert np.linalg.norm(coarse - exact_quarter) > 1e-6


def test_registry_holds_exactly_the_three_v3_systems() -> None:
    """The frozen registry entries are Lorenz-63, Rossler and Chua (Lorenz-96 is gone).

    Reference: decision log D3 and proposal and methods v3 section 4 (three
    systems), written out in the test, not read from the code. The extension
    systems of WU-0021 (DEC-0037) are additional registry entries and are
    listed separately, so the registry is the frozen three plus the extension
    three. This test changed by design in WU-0021: it asserted
    ``set(SYSTEMS) == {"lorenz63", "rossler", "chua"}``.

    Tolerance: none; the check is equality of sets of strings.
    """
    frozen = {"lorenz63", "rossler", "chua"}
    extension = {"rossler_hyper", "lorenz63_r166", "rossler_z"}
    assert frozen <= set(SYSTEMS)
    assert set(SYSTEMS) - frozen == extension
    assert not hasattr(systems, "lorenz96_field")


# ------------------------------------ orbit guard (WU-0002.11c, DEF-0015)
#
# Needs owner review before freeze: the guard sets the study's time unit.
# Reference for the constants: the "Mathematics check" of
# docs/agent/records/work/WU-0002.11c-orbit-guard.md (applied-mathematician,
# fixed before the code, VV.3). Every number below is from there or from a
# hand or exact-rational computation in this file; none is read from the code
# under test.

BOUND = 3.0
"""Bound of the linear test specs (the plan's B for G1 to G3)."""


def _linear_spec(
    rates: tuple[float, float, float],
    bound: float | None = BOUND,
    observed: int = 0,
) -> SystemSpec:
    """Build the linear system ``f(s) = diag(rates) s`` (G2/G3 constants).

    The constants are max_dt 0.03 and start (1, 1, 1).
    """
    rate = jnp.asarray(rates)
    return SystemSpec(
        name="linear",
        field_fn=lambda s, p: rate * s,
        params={},
        dim=3,
        observed_index=observed,
        initial_state=(1.0, 1.0, 1.0),
        max_dt=0.03,
        orbit_bound=bound,
    )


def _rk4_factor(z: Fraction) -> Fraction:
    """Return the RK4 amplification R(z) = 1 + z + z^2/2 + z^3/6 + z^4/24.

    The value is an exact rational number.
    """
    return 1 + z + z**2 / 2 + z**3 / 6 + z**4 / 24


def test_guard_on_hand_arrays() -> None:
    """G1: the closed bound, one ulp above it, NaN and inf in other coordinates.

    Reference: hand arrays (B = 3). Tolerance: none; the results are exact. B
    and -B are accepted and the returned maximum is exactly 3.
    ``nextafter(B, inf)`` is refused at its own row. A NaN in y only and an
    inf in z only are refused as "non-finite" at their rows. Large finite y
    and z are accepted (the guard reads x only: z exceeds B on the Lorenz and
    Chua attractors, M4).
    """
    spec = _linear_spec((0.0, 0.0, 0.0))
    ok = np.array([[0.0, 0.0, 0.0], [BOUND, 0.0, 0.0], [-BOUND, 1e3, -1e3]])
    assert systems.guard_orbit(spec, "main", ok) == BOUND
    above = math.nextafter(BOUND, math.inf)
    for sign, row in ((1.0, 1), (-1.0, 2)):
        states = np.zeros((4, 3))
        states[row, 0] = sign * above
        with pytest.raises(
            systems.OrbitDivergence,
            match=rf"'main' of 'linear'.*first failing step {row},",
        ) as raised:
            systems.guard_orbit(spec, "main", states)
        assert "non-finite" not in str(raised.value)
        assert f"{above:.17g}" in str(raised.value)
    for column, value in (
        (1, math.nan),
        (2, math.inf),
        (2, -math.inf),
        (0, math.nan),
    ):
        states = np.zeros((5, 3))
        states[3, column] = value
        with pytest.raises(
            systems.OrbitDivergence,
            match=r"first failing step 3, max\|x\| non-finite",
        ):
            systems.guard_orbit(spec, "statistics", states)


def test_guard_rejects_bad_input() -> None:
    """A spec without a usable bound, a bad observed index or array raises.

    The error is ``ValueError`` in each case.

    Reference: the plan (a missing bound is refused, never silently
    unguarded, PRIME.4) and M4 (the guard reads coordinate 0 only; B was
    derived for x). Tolerance: none.
    """
    states = np.zeros((3, 3))
    for bad in (None, math.nan, math.inf, 0.0, -1.0):
        with pytest.raises(ValueError, match="orbit_bound"):
            systems.guard_orbit(
                _linear_spec((0.0,) * 3, bound=bad), "main", states
            )
        with pytest.raises(ValueError, match="orbit_bound"):
            systems.lyapunov_guarded(
                _linear_spec((-0.1,) * 3, bound=bad), 0.1, 10, 2
            )
    with pytest.raises(ValueError, match="observed_index"):
        systems.guard_orbit(
            _linear_spec((0.0,) * 3, observed=1), "main", states
        )
    with pytest.raises(ValueError, match="observed_index"):
        systems.lyapunov_guarded(
            _linear_spec((-0.1,) * 3, observed=1), 0.1, 10, 2
        )
    spec = _linear_spec((0.0,) * 3)
    for shape in ((0, 3), (3, 2), (3,)):
        with pytest.raises(ValueError, match="shape"):
            systems.guard_orbit(spec, "main", np.zeros(shape))


def test_registry_bounds_are_the_ratified_ones() -> None:
    """The registry bounds are Lorenz-63 40, Rossler 25 and Chua 3 (frozen).

    These are the ratified values (DEC-0017 Q1, DEC-0026 item 3). The extension
    systems of WU-0021 have their own bounds (specification note section 0:
    S1 300, S2 185, S3 50). This test changed by design in WU-0021: it asserted
    the dict of all registry bounds equal to the three frozen ones.

    Reference: the ratified numbers, typed here. Tolerance: none.
    """
    bounds = {name: spec.orbit_bound for name, spec in SYSTEMS.items()}
    assert {n: bounds[n] for n in ("lorenz63", "rossler", "chua")} == {
        "lorenz63": 40.0,
        "rossler": 25.0,
        "chua": 3.0,
    }
    assert {
        n: bounds[n] for n in set(bounds) - {"lorenz63", "rossler", "chua"}
    } == {"rossler_hyper": 300.0, "lorenz63_r166": 185.0, "rossler_z": 50.0}


def test_first_failing_step_on_an_analytic_orbit() -> None:
    """G2: the first failing step of ``x' = 0.5 x`` is 22 on every path (B = 3).

    Reference: exact rational arithmetic (``fractions``) on the RK4
    amplification ``R(z)``, ``x_k = R(a dt)^(substeps k)`` with interval 0.1,
    max_dt 0.03 (4 substeps, dt = 0.025, a dt = 1/80), and start x = 1. The
    smallest ``k`` with ``x_k > 3`` is found by a loop in the test. The float
    step is 0.1/4 rather than 1/40 (a relative difference of 1e-16), which
    moves x_22 by about 1e-14, far inside the margin.

    Tolerance: exact integer. The premise is asserted on both sides:
    ``x_21 < B (1 - 1e-6)`` and ``x_22 > B (1 + 1e-6)`` (the relative margins
    are 4.7e-2 and 1.4e-3 and the rounding of x_22 is about 4e-14), so
    rounding cannot move the index. The ``lyapunov_guarded`` cases place the
    crossing inside the burn-in (burn 50, where a burn-in-blind guard would
    report 50) and inside the averaging scan (burn 10). Both must report 22
    (the state counted from the start as 0, M2).
    """
    factor = _rk4_factor(Fraction(1, 2) * Fraction(1, 40)) ** 4
    k = 0
    while Fraction(factor**k) <= BOUND:
        k += 1
    assert k == 22
    assert float(factor ** (k - 1)) < BOUND * (1 - 1e-6)
    assert float(factor**k) > BOUND * (1 + 1e-6)

    spec = _linear_spec((0.5, -1.0, -2.0))
    orbit = simulate_trajectory(
        make_flow_step(spec, spec.params, 0.1),
        np.asarray(spec.initial_state),
        40,
    )
    with pytest.raises(
        systems.OrbitDivergence, match=r"first failing step 22,"
    ):
        systems.guard_orbit(spec, "main", orbit)
    for burn_in in (50, 10):
        with pytest.raises(
            systems.OrbitDivergence,
            match=r"'lyapunov' of 'linear'.*first failing step 22,",
        ):
            systems.lyapunov_guarded(spec, 0.1, 100, burn_in)


def test_lyapunov_guarded_on_a_bounded_linear_orbit() -> None:
    """G3: lambda and the maximum of ``x' = diag(-0.1, -0.5, -1) x`` are exact.

    Reference: e_1 is the dominant eigendirection and QR of a diagonal matrix
    leaves Q = I, so each step contributes ``ln R(-0.1 dt)`` with
    ``dt = 0.1/4``, and ``lambda = 4 log1p(w) / 0.1`` with
    ``w = z (1 + z/2 + z^2/6 + z^3/24)``, ``z = -0.0025`` (``R = 1 + w``;
    equal to a 30-term rational series to the last digit, M4).

    Tolerance: relative 1e-12 (n_steps = 1000, burn-in 10). The bound comes
    from the budget: Jacobian rounding at most 4.4e-14 relative to
    ``|ln J_11| = 0.01``, plus 1000 u = 1.1e-13 for the sum, about 1.6e-13 in
    total, so 1e-12 keeps a margin of 6; the observed error is 4e-15.
    ``orbit_max_abs`` is exactly ``|x_0| = 1`` (the orbit decays and state 0 is
    checked, burn-in included; the plan's burn-in-blind formula is replaced,
    M2). The bitwise equality with ``estimate_lyapunov`` holds by delegation
    and is not evidence (G4 carries it).
    """
    spec = _linear_spec((-0.1, -0.5, -1.0))
    z = -0.0025
    w = z * (1 + z / 2 + z**2 / 6 + z**3 / 24)
    reference = 4 * math.log1p(w) / 0.1
    lam, largest = systems.lyapunov_guarded(spec, 0.1, 1000, 10)
    assert abs(lam / reference - 1.0) <= 1e-12
    assert largest == 1.0 and type(largest) is float and type(lam) is float
    assert systems.estimate_lyapunov(spec, 0.1, 1000, 10) == lam


def _verbatim_benettin(
    spec: SystemSpec, interval: float, n_steps: int, burn_in: int
) -> float:
    """Return the Benettin loop of ``estimate_lyapunov`` at 529b90b, verbatim.

    The code is copied unchanged. It has no guard. It is the pre-change code
    and so a REGRESSION reference, not correctness evidence (skill
    numerical-test).
    """
    import jax

    step_fn = make_flow_step(spec, spec.params, interval)
    jac_fn = jax.jacfwd(step_fn)
    state = jnp.asarray(spec.initial_state, dtype=jnp.float64)
    state = jax.jit(
        lambda s: jax.lax.fori_loop(0, burn_in, lambda _, x: step_fn(x), s)
    )(state)

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
        (state, basis)
    )
    return float(jnp.sum(growth) / (n_steps * interval))


G4_BANDS = {
    "lorenz63": (18.0, 20.0),
    "rossler": (11.40, 11.45),
    "chua": (2.25, 2.27),
}
"""Band of ``orbit_max_abs`` at production settings.

The bands come from block maxima of 3.2e6 independent states
(applied-mathematician, M4): Lorenz 18.87 to 19.61, Rossler 11.4314 to
11.4332, Chua 2.2628 to 2.2631. The upper limits catch a wrong-coordinate
maximum (Rossler z reaches 22.85 <= B).
"""


@pytest.mark.parametrize("name", ["lorenz63", "rossler", "chua"])
def test_regression_guarded_lambda_is_bitwise_unchanged(name: str) -> None:
    """G4: production-setting exponents keep their pre-change value bit for bit.

    This is a REGRESSION GUARD against the verbatim 529b90b loop
    (``_verbatim_benettin``), not correctness evidence. The guard carries a
    running maximum and a first-failure index in the burn-in loop and the
    scan, and must not move the XLA float path of lambda (DEF-0015, V4).

    Production settings: interval ``20 max_dt``, 10^5 steps, burn-in 5000.
    Tolerance: bitwise (IEEE bytes). The evidence is for this CPU and XLA
    build only; a GPU may contract differently. ``orbit_max_abs`` lies in
    ``G4_BANDS`` (independent block maxima, see there) and is at most B.
    """
    spec = SYSTEMS[name]
    interval = 20 * spec.max_dt
    expected = _verbatim_benettin(spec, interval, 100_000, 5_000)
    lam, largest = systems.lyapunov_guarded(spec, interval, 100_000, 5_000)
    assert struct.pack("<d", lam) == struct.pack("<d", expected), (
        lam,
        expected,
    )
    low, high = G4_BANDS[name]
    assert low <= largest <= high and largest <= spec.orbit_bound, largest
    assert systems.estimate_lyapunov(spec, interval, 100_000, 5_000) == lam


def _chua_rk4_numpy(
    start: tuple[float, float, float], steps: int
) -> np.ndarray:
    """Integrate the Chua map at interval 0.1 in NumPy, from the equations.

    The integration uses 20 RK4 substeps of 0.005. It is independent of
    ``lpcstudy``: the three-segment diode is written out piecewise.
    """
    alpha, beta, m0, m1 = 15.6, 28.0, -1.143, -0.714

    def field(s: np.ndarray) -> np.ndarray:
        x, y, z = s
        if x > 1.0:
            g = m1 * x + (m0 - m1)
        elif x < -1.0:
            g = m1 * x - (m0 - m1)
        else:
            g = m0 * x
        return np.array([alpha * (y - x - g), x - y + z, -beta * y])

    state, dt, out = np.array(start), 0.005, [np.array(start)]
    for _ in range(steps):
        for _ in range(20):
            k1 = field(state)
            k2 = field(state + 0.5 * dt * k1)
            k3 = field(state + 0.5 * dt * k2)
            k4 = field(state + dt * k3)
            state = state + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        out.append(state)
    return np.array(out)


def test_diverging_chua_start_refuses_the_run() -> None:
    """G5: the DEF-0015 case: a Chua start with |x_0| <= 3 that diverges raises.

    The start (0.6, -0.3, 1.0) has |x_0| inside the bound but leaves the
    basin of the attractor.

    Reference: registry parameters, interval 0.1, a NumPy RK4 written from
    the equations in this file (``_chua_rk4_numpy``), and the
    applied-mathematician's SciPy DOP853 values (M3): |x_80| = 2.679006 (RK4)
    and 2.680819 (DOP853), |x_81| = 3.126980 and 3.128149, so the first
    failing step is 81 (state 0 is the start). The margins are 0.134 below B
    and 0.127 above it, and the two integrators differ by at most 2e-3 there.

    Tolerance: printed digits, so 5e-7 absolute on the two RK4 values; the
    index is an exact integer.

    The old loop returns a finite positive exponent (0.3055) for this orbit.
    The guarded one raises, naming the system, the orbit and step 81, with
    the maximum "non-finite" at production length (the orbit has overflowed by
    step 5000 + 10^5). A burn-in-blind guard would report step 5000, so the
    case also pins the placement. The registry start passes (G4).
    """
    start = (0.6, -0.3, 1.0)
    orbit = _chua_rk4_numpy(start, 81)
    assert abs(abs(orbit[80, 0]) - 2.679006) <= 5e-7
    assert abs(abs(orbit[81, 0]) - 3.126980) <= 5e-7
    assert np.abs(orbit[:81, 0]).max() < 3.0 < abs(orbit[81, 0])
    spec = dataclasses.replace(SYSTEMS["chua"], initial_state=start)
    with pytest.raises(
        systems.OrbitDivergence,
        match=(
            r"'lyapunov' of 'chua'.*first failing step 81, "
            r"max\|x\| non-finite"
        ),
    ):
        systems.lyapunov_guarded(spec, 0.1, 100_000, 5_000)
    with pytest.raises(systems.OrbitDivergence, match="first failing step 81,"):
        systems.estimate_lyapunov(spec, 0.1, 1000, 200)
