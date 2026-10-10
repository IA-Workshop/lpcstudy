"""Tests for lpcstudy.systems: code verification of the fixed-step RK4 flow map."""

from __future__ import annotations

import jax.numpy as jnp
import numpy as np
import pytest
from scipy.linalg import expm

from lpcstudy.systems import SystemSpec, make_flow_step

# Linear test system x' = A x, A = S B S^-1 (A non-normal, |lambda|max ~ 2.0).
_B = np.array([[-0.1, -2.0, 0.0], [2.0, -0.1, 0.0], [0.0, 0.0, -0.5]])
_S = np.array([[1.0, 0.5, 0.0], [0.0, 1.0, 0.3], [0.2, 0.0, 1.0]])
_A = _S @ _B @ np.linalg.inv(_S)
_X0 = np.array([1.0, 0.5, -0.3])
_STEPS = (1 / 8, 1 / 16, 1 / 32)  # dyadic: ceil(1 / h) is exactly 8, 16, 32 substeps


def _spec(field_fn, dim: int, initial: tuple[float, ...], max_dt: float) -> SystemSpec:
    """A ``SystemSpec`` built in the test (no registered system is used)."""
    return SystemSpec(name="test", field_fn=field_fn, params={}, dim=dim, observed_index=0,
                      initial_state=initial, max_dt=max_dt)


def _linear_error(max_dt: float) -> tuple[np.ndarray, np.ndarray]:
    """Return (output, exact - output) of the RK4 flow over T = 1 for x' = A x."""
    a_jax = jnp.asarray(_A)
    spec = _spec(lambda s, p: a_jax @ s, 3, tuple(_X0), max_dt)
    out = make_flow_step(spec, {}, 1.0)(jnp.asarray(_X0))
    assert out.dtype == jnp.float64
    out = np.asarray(out)
    return out, expm(_A) @ _X0 - out


def test_rk4_observed_order_is_four() -> None:
    """RK4 on x' = A x matches ``expm(A t) x0`` with observed order 4 and the right constant.

    Reference: exact solution ``scipy.linalg.expm(A T) @ x0`` (independent of the
    integrator; it agrees with a 50-digit Taylor series to 1.2e-15). A = S B S^-1 with
    B = [[-0.1, -2, 0], [2, -0.1, 0], [0, 0, -0.5]], S = [[1, .5, 0], [0, 1, .3], [.2, 0, 1]],
    eigenvalues -0.1 +- 2i and -0.5 (asserted), x0 = (1, 0.5, -0.3), T = 1, ``max_dt`` = h in
    {1/8, 1/16, 1/32} through ``make_flow_step`` on a ``SystemSpec`` built here.

    Premises (asserted): eigenvalues as stated; error at h = 1/8 below 1e-3 and at
    h = 1/32 above 1e-11 (round-off is about 1e-14, so the finest error is well above it);
    float64 output.

    Tolerances (applied-mathematician, WU-0005 log, which tightens the roadmap's
    [3.8, 4.2]). (1) Observed order log2(e_h / e_{h/2}) in [3.9, 4.1] for both pairs. The
    error is (T h^4 / 120) ||A^5 e^{AT} x0|| + O(h^5), so the observed order deviates from 4
    by O(h): measured 4.042 and 4.024 (deviation 0.042 and 0.024, halving with h), inside
    the band by a factor of 2.4 or more; round-off moves it by about 1e-8. (2) Leading
    constant at h = 1/32: ||(x_ref - x_h) - L h^4||_2 <= 0.10 ||L h^4||_2 with
    L = (T / 120) A^5 expm(A T) x0; the measured value is 0.043, the O(h) relative size
    of the next term, and the vector form also checks the sign and direction. Measured
    errors 6.94e-5, 4.21e-6, 2.59e-7 (about 0.27 h^4).

    Limitation: a linear field exercises only the stability polynomial, which is shared by
    all 4-stage order-4 methods; the nonlinear order conditions are covered by
    ``test_rk4_observed_order_nonlinear_scalar``.
    """
    assert np.allclose(np.sort_complex(np.linalg.eigvals(_A)),
                       np.sort_complex(np.array([-0.5, -0.1 - 2j, -0.1 + 2j])))
    outputs = [_linear_error(h) for h in _STEPS]
    errors = [float(np.linalg.norm(err)) for _, err in outputs]
    assert errors[0] < 1e-3
    assert errors[2] > 1e-11
    for coarse, fine in ((0, 1), (1, 2)):
        order = float(np.log2(errors[coarse] / errors[fine]))
        assert 3.9 <= order <= 4.1, (coarse, order)

    leading = (1.0 / 120.0) * np.linalg.matrix_power(_A, 5) @ expm(_A) @ _X0 * _STEPS[2] ** 4
    residual = float(np.linalg.norm(outputs[2][1] - leading))
    assert residual <= 0.10 * float(np.linalg.norm(leading))


def test_rk4_observed_order_nonlinear_scalar() -> None:
    """RK4 on y' = y^2, y(0) = 0.5 has observed order 4 (exact y(1) = 1).

    Reference: the closed form y(t) = y0 / (1 - y0 t), so y(1) = 0.5 / 0.5 = 1 exactly.
    The scalar autonomous ODE has the same order conditions as a system up to order 4,
    so the nonlinear conditions are all exercised (the linear test cannot see them).
    ``make_flow_step`` takes the field through ``SystemSpec.field_fn``, so the spec is built
    here with dim = 1, T = 1 and h in {1/8, 1/16, 1/32}.

    Tolerance: observed order in [3.9, 4.1] for both pairs, the band used for the linear
    test. The applied-mathematician measured errors 2.90e-6, 1.84e-7, 1.16e-8 and orders
    3.975 and 3.993 (WU-0005 log); the deviation from 4 is O(h), so the margin to 3.9 is
    at least 0.075. The errors are far above round-off (1e-16) and below 1e-5.
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
    """``max_dt`` caps the step: 0.3 and 0.25 both give 4 substeps of 0.25 over T = 1.

    Reference: construction. ``substeps = ceil(T / max_dt)`` is ceil(3.33) = 4 for 0.3 and
    exactly 4 for 0.25, so dt = 0.25 in both and the arithmetic is identical; the step is
    never larger than ``max_dt`` (0.25 <= 0.3). Contrast: ``max_dt`` = 0.5 gives 2 substeps
    of 0.5, whose result differs from the 0.25 result by the truncation error (order
    0.27 h^4 = 1.7e-2 by extrapolating the measured errors; asserted only above 1e-6),
    many orders above the tolerance.
    Tolerance ``atol=1e-15``, set before the run: identical operations, so the results
    should be bitwise equal; 1e-15 allows an ulp of XLA reordering on a state of norm ~1.
    """
    a_jax = jnp.asarray(_A)
    spec = lambda max_dt: _spec(lambda s, p: a_jax @ s, 3, tuple(_X0), max_dt)  # noqa: E731
    x0 = jnp.asarray(_X0)
    capped = np.asarray(make_flow_step(spec(0.3), {}, 1.0)(x0))
    exact_quarter = np.asarray(make_flow_step(spec(0.25), {}, 1.0)(x0))
    np.testing.assert_allclose(capped, exact_quarter, rtol=0, atol=1e-15)
    coarse = np.asarray(make_flow_step(spec(0.5), {}, 1.0)(x0))
    assert np.linalg.norm(coarse - exact_quarter) > 1e-6
