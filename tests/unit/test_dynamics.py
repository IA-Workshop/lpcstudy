"""Tests for ``lpcstudy.dynamics``: the observability and the delay map.

The observability factor ``nu`` says how strongly observation noise is
magnified when a state is recovered from a delay vector. The delay map takes
the oldest state of a window and returns the stacked observations. These tests
check both against references that do not use the code under test: a
manufactured linear system with a known answer, a closed form for a scalar
map, and the independent ordering rule for delay vectors.
"""

from __future__ import annotations

import jax
import jax.numpy as jnp
import numpy as np
import pytest

from lpcstudy.dynamics import delay_map_forward, make_observability
from lpcstudy.embedding import delay_vectors
from lpcstudy.systems import SYSTEMS, make_flow_step, simulate_trajectory


def test_regression_observability_matches_ad_jacobians() -> None:
    """nu from the forward formula equals tr[W Q (A^T A)^{-1} Q^T W^T].

    Here A and Q are obtained by independent automatic differentiation (AD) of
    the forward delay map and of the flow over the window. Forming
    J = A Q^{-1} explicitly is avoided: cond(Q) is about 1e7, which makes
    J^T J numerically singular, and that is why the forward formula is used.

    REGRESSION GUARD, not correctness evidence (WU-0013.2, DEF-0007). The
    reference reuses the code's own formula for nu (``make_observability`` in
    dynamics.py) and takes A from ``delay_map_forward``, which is code under
    test and shares the delay-index expression with ``make_observability``.
    The test therefore checks only that two AD routes (a tangent recursion in
    a scan, and ``jax.jacfwd`` through a ``fori_loop``) agree, i.e. the
    tangent bookkeeping (the prepended row 0, the scan offset, ``obs_scale``).
    The correctness of nu is tested by
    ``test_observability_linear_system_matches_pinv`` and
    ``test_observability_scalar_geometric_closed_form``; the index convention
    by ``test_delay_map_forward_matches_delay_vectors``.

    Tolerance: ``rel=1e-8``, unchanged. cond(A^T A) at the three states is 21,
    28 and 30 (cond(Q) is 3e7 to 7e7), so conditioning limits the agreement to
    about 30 * 2.2e-16 = 7e-15. The value 1e-8 is not an accuracy statement
    but a loose bound on agreement between two AD routes for an identical
    formula.
    """
    spec = SYSTEMS["lorenz63"]
    step = make_flow_step(spec, spec.params, 0.0368)
    traj = simulate_trajectory(step, jnp.asarray(spec.initial_state), 3000)[
        2000:
    ]
    delay, dim = 5, 7
    whiten = np.eye(3) / traj.std(axis=0)
    nu_fn = make_observability(step, 0, 7.9, whiten, delay, dim)
    fwd = delay_map_forward(step, 0, 0.0, 7.9, delay, dim)
    span = (dim - 1) * delay
    advance = lambda s: jax.lax.fori_loop(0, span, lambda _, x: step(x), s)
    for s_old in traj[:3]:
        a_mat = np.asarray(jax.jacfwd(fwd)(jnp.asarray(s_old)))
        q_mat = np.asarray(jax.jacfwd(advance)(jnp.asarray(s_old)))
        cov = (
            whiten @ q_mat @ np.linalg.inv(a_mat.T @ a_mat) @ q_mat.T @ whiten.T
        )
        got = float(nu_fn(jnp.asarray(s_old[None, :]))[0])
        assert got == pytest.approx(np.sqrt(np.trace(cov)), rel=1e-8)


def test_observability_linear_system_matches_pinv() -> None:
    """nu for a linear map s -> M s equals ||W J_G^+||_F (J_G formed directly).

    Here J_G^+ is the pseudo-inverse (the generalized matrix inverse).

    Reference: a manufactured linear system with a known answer, computed by
    a different route. For ``s -> M s`` the tangent is M everywhere, so (as in
    the ``make_observability`` docstring) A has rows
    e_0^T M^{(D-1-k) tau} / sigma_x (k = 0..D-1), Q = M^{(D-1) tau}, and the
    delay-map Jacobian at s_t is J_G = A Q^{-1}. Then
    nu^2 = tr[W (J_G^T J_G)^{-1} W^T] = ||W J_G^+||_F^2, because
    J_G^+ J_G^{+T} = (J_G^T J_G)^{-1}. The reference uses
    ``np.linalg.matrix_power`` and ``np.linalg.pinv`` (an SVD); the code uses
    a scan of Jacobian products and the normal equations (A^T A)^{-1}. Here
    M = R diag(1.1, 0.9, 1.0), with R a rotation by 0.7 rad about the axis
    (1, 2, -1)/sqrt(6), so (e_0, M) is observable (rank A = 3). Also tau = 2,
    D = 4, sigma_x = 1.7, and W = diag(1/2, 1/1.5, 1/0.8).

    Tolerance: ``rel=1e-11``. Here cond(A) = 2.8, cond(A^T A) = 8.1,
    cond(J_G) = 1.6 and cond(Q) = 1.9, so the round-off error of either route
    is about n_ops * cond * eps = 100 * 8.1 * 2.2e-16 = 2e-13, a deliberately
    pessimistic estimate; 1e-11 leaves a factor of 50 over it. The tolerance
    was fixed from this analysis before the test was run.
    """
    angle = 0.7
    axis = np.array([1.0, 2.0, -1.0]) / np.sqrt(6.0)
    cross = np.array(
        [
            [0.0, -axis[2], axis[1]],
            [axis[2], 0.0, -axis[0]],
            [-axis[1], axis[0], 0.0],
        ]
    )
    rotation = (
        np.eye(3) + np.sin(angle) * cross + (1 - np.cos(angle)) * cross @ cross
    )
    mat = rotation @ np.diag([1.1, 0.9, 1.0])
    delay, dim, sigma = 2, 4, 1.7
    whiten = np.diag([1 / 2.0, 1 / 1.5, 1 / 0.8])

    obs_row = np.array([1.0, 0.0, 0.0])
    a_mat = (
        np.array(
            [
                obs_row @ np.linalg.matrix_power(mat, (dim - 1 - k) * delay)
                for k in range(dim)
            ]
        )
        / sigma
    )
    q_mat = np.linalg.matrix_power(mat, (dim - 1) * delay)
    jac_g = a_mat @ np.linalg.inv(q_mat)
    expected = np.linalg.norm(whiten @ np.linalg.pinv(jac_g))

    mat_jax = jnp.asarray(mat)
    nu_fn = make_observability(
        lambda s: mat_jax @ s, 0, sigma, whiten, delay, dim
    )
    got = np.asarray(nu_fn(jnp.asarray([[0.3, -1.0, 2.0], [5.0, 0.1, -0.7]])))
    assert got == pytest.approx(expected, rel=1e-11)


@pytest.mark.parametrize("dim", [2, 3, 5])
def test_observability_scalar_geometric_closed_form(dim: int) -> None:
    """nu for the scalar map s -> lam s has a closed form.

    Reference: a closed form derived by hand. With m = 1,
    X_t[k] = lam^{(D-1-k) tau} s_old / sigma, so
    A = (lam^{(D-1) tau}, ..., lam^tau, 1)^T / sigma,
    A^T A = sum_{k<D} lam^{2 k tau} / sigma^2 and Q = lam^{(D-1) tau}, hence
    nu = w sigma lam^{(D-1) tau} / sqrt(sum_{k<D} lam^{2 k tau}), where w is
    the (1 x 1) whitening.

    Tolerance: ``rel=1e-12``. It is a handful of float64 operations on a
    well-conditioned 1 x 1 problem (cond = 1), with error about
    10 * 1.1e-16 = 1e-15; 1e-12 leaves a factor of 1000.
    """
    lam, delay, sigma, weight = 1.2, 3, 2.5, 0.7
    expected = (
        weight
        * sigma
        * lam ** ((dim - 1) * delay)
        / np.sqrt(sum(lam ** (2 * k * delay) for k in range(dim)))
    )
    nu_fn = make_observability(
        lambda s: lam * s, 0, sigma, np.array([[weight]]), delay, dim
    )
    got = float(nu_fn(jnp.asarray([[0.7]]))[0])
    assert got == pytest.approx(expected, rel=1e-12)


def test_delay_map_forward_matches_delay_vectors() -> None:
    """``delay_map_forward(s_old)`` equals ``delay_vectors`` of the path.

    Reference: the delay-vector definition
    X_t = (x_t, x_{t-tau}, ..., x_{t-(D-1)tau}), tested independently in
    ``test_embedding.py::test_delay_vectors_order``. The path is built by
    ``simulate_trajectory`` from s_old over (D-1) tau + 1 states and
    normalized as (x - mean) / sigma_x with mean 1.3 and sigma_x 7.9;
    ``delay_vectors`` then reads the entry at t = (D-1) tau. This ties the
    row-selection expression of ``delay_map_forward`` (and, through the same
    expression, ``make_observability``) to the tested ordering. The system is
    Lorenz-63 with tau = 3, D = 4 and three states. The test also asserts its
    own premise: reversing the vector changes it by more than 1e-3, so a
    reversed index convention would be detected.

    Tolerance: ``atol=1e-12``. Both routes apply the same 9 RK4 steps in
    float64 and differ only by XLA fusion, a few ulp (1e-16) amplified by at
    most exp(lambda_max * 9 steps), about 1.3 (1 Lyapunov time = 30 steps), so
    the difference is below 1e-15; 1e-12 leaves three orders of magnitude.
    """
    spec = SYSTEMS["lorenz63"]
    step = make_flow_step(spec, spec.params, 0.0368)
    traj = simulate_trajectory(step, jnp.asarray(spec.initial_state), 3000)[
        2000:
    ]
    delay, dim, mean, scale = 3, 4, 1.3, 7.9
    span = (dim - 1) * delay
    fwd = delay_map_forward(step, 0, mean, scale, delay, dim)
    for s_old in traj[:3]:
        path = simulate_trajectory(step, jnp.asarray(s_old), span + 1)[:, 0]
        expected = delay_vectors(
            (path - mean) / scale, np.array([span]), delay, dim
        )[0]
        assert np.max(np.abs(expected - expected[::-1])) > 1e-3
        np.testing.assert_allclose(
            np.asarray(fwd(jnp.asarray(s_old))),
            expected,
            rtol=0.0,
            atol=1e-12,
        )
