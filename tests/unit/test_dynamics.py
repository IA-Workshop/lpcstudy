"""Tests for lpcstudy.dynamics: the observability against independent Jacobians."""

from __future__ import annotations

import jax
import jax.numpy as jnp
import numpy as np
import pytest

from lpcstudy.dynamics import delay_map_forward, make_observability
from lpcstudy.systems import SYSTEMS, make_flow_step, simulate_trajectory


def test_observability_matches_independent_jacobians() -> None:
    """nu from the scan-based forward formula equals tr[W Q (A^T A)^{-1} Q^T W^T]
    with A and Q obtained by independent automatic differentiation of the forward
    delay map and of the flow over the window. (Forming J = A Q^{-1} explicitly is
    avoided: cond(Q) ~ 1e7 makes J^T J numerically singular, which is why the
    forward formula is used.)"""
    spec = SYSTEMS["lorenz63"]
    step = make_flow_step(spec, spec.params, 0.0368)
    traj = simulate_trajectory(step, jnp.asarray(spec.initial_state), 3000)[2000:]
    delay, dim = 5, 7
    whiten = np.eye(3) / traj.std(axis=0)
    nu_fn = make_observability(step, 0, 7.9, whiten, delay, dim)
    fwd = delay_map_forward(step, 0, 0.0, 7.9, delay, dim)
    span = (dim - 1) * delay
    advance = lambda s: jax.lax.fori_loop(0, span, lambda _, x: step(x), s)
    for s_old in traj[:3]:
        a_mat = np.asarray(jax.jacfwd(fwd)(jnp.asarray(s_old)))
        q_mat = np.asarray(jax.jacfwd(advance)(jnp.asarray(s_old)))
        cov = whiten @ q_mat @ np.linalg.inv(a_mat.T @ a_mat) @ q_mat.T @ whiten.T
        got = float(nu_fn(jnp.asarray(s_old[None, :]))[0])
        assert got == pytest.approx(np.sqrt(np.trace(cov)), rel=1e-8)
