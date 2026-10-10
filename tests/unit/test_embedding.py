"""Tests for lpcstudy.embedding: delay vectors, AMI delay and autocorrelation time."""

from __future__ import annotations

import jax.numpy as jnp
import numpy as np

from lpcstudy.embedding import autocorrelation_time, delay_vectors, select_delay
from lpcstudy.systems import SYSTEMS, make_flow_step, simulate_trajectory


def test_delay_vectors_order() -> None:
    """X_t = (x_t, x_{t-tau}, ...)."""
    series = np.arange(20.0)
    out = delay_vectors(series, np.array([10]), 3, 3)
    assert out.tolist() == [[10.0, 7.0, 4.0]]


def test_delay_and_acf() -> None:
    """AMI delay of Lorenz-63 x at 1 LT = 30 steps lies near 0.15-0.2 time units;
    a pure sine is phase-coherent and never decorrelates."""
    spec = SYSTEMS["lorenz63"]
    step = make_flow_step(spec, spec.params, 0.0368)
    x = simulate_trajectory(step, jnp.asarray(spec.initial_state), 60_000)[5_000:, 0]
    assert 3 <= select_delay((x - x.mean()) / x.std(), 60) <= 8
    t = np.arange(20_000)
    assert autocorrelation_time(np.sin(2 * np.pi * t / 40), 500) == 500
