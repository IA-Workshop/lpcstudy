"""Tests for lpcstudy.embedding: delay vectors, AMI delay and autocorrelation time."""

from __future__ import annotations

import jax.numpy as jnp
import numpy as np

from lpcstudy.embedding import autocorrelation_time, delay_vectors, select_delay
from lpcstudy.systems import SYSTEMS, make_flow_step, simulate_trajectory


def test_delay_vectors_order() -> None:
    """X_t = (x_t, x_{t-tau}, ...).

    Reference: the definition evaluated by hand on series x_i = i. With t = 10,
    tau = 3, D = 3: X_t = (x_10, x_7, x_4) = (10, 7, 4).
    Tolerance: none, exact equality. The integers 0..19 are exact in float64 and the
    function only indexes, so there is no round-off.
    """
    series = np.arange(20.0)
    out = delay_vectors(series, np.array([10]), 3, 3)
    assert out.tolist() == [[10.0, 7.0, 4.0]]


def test_regression_ami_delay_lorenz_band() -> None:
    """AMI delay of Lorenz-63 x at 1 LT = 30 steps lies near 0.15-0.2 time units.

    REGRESSION GUARD (WU-0013.2, DEF-0007 audit item 2), not correctness evidence. The
    band's source ("0.15-0.2 time units") is uncited, so LPC.PC.21a is not met for
    it: a published value must be cited in the code, and no source has been verified
    (needs ``/verify-citation`` or the ``researcher``). Until it is, the test is a
    deliberately loose guard that the selected delay stays within [3, 8] steps. It
    does not pin the current value: ``select_delay`` currently returns 5 steps =
    0.184 time units at Delta t = 0.0368, but any value from 3 to 8 passes.

    Tolerance: integer band [3, 8] steps (0.110-0.294 time units), unchanged. The band
    is uncited and wider than the docstring's own 0.15-0.2 time-unit claim
    (4.08-5.43 steps). It is kept, neither widened nor tightened: the audit does not
    allow tightening without a source. A cited reference, to be retrieved by the
    ``researcher``, would let the band be tightened and the test renamed back
    (dropping ``regression``). The estimator is the default 32-equiprobable-bin
    histogram AMI with the first local minimum of a 3-point smoothed curve, on
    55 000 normalized samples (60 000 steps, 5 000 burn-in).
    """
    spec = SYSTEMS["lorenz63"]
    step = make_flow_step(spec, spec.params, 0.0368)
    x = simulate_trajectory(step, jnp.asarray(spec.initial_state), 60_000)[5_000:, 0]
    assert 3 <= select_delay((x - x.mean()) / x.std(), 60) <= 8


def test_autocorrelation_time_sine_is_censored() -> None:
    """A pure sine is phase-coherent and never decorrelates.

    Reference: property of the biased FFT autocorrelation estimator for a pure
    sinusoid of period 40 over N = 20 000 samples: ACF(k) ~ (1 - k/N) cos(2 pi k / 40).
    At k = max_lag = 500, cos(2 pi 500/40) = cos(25 pi) = -1, so |ACF(500)| ~ 0.975.
    The envelope at every lag k <= 500 is max_{500 >= j >= k} |ACF(j)| >= |ACF(500)|
    ~ 0.975 > 1/e = 0.368, so it never falls below 1/e and the function returns the
    censoring value max_lag = 500.
    Tolerance: none, exact integer equality; the margin 0.975 against 0.368 is a factor
    of 2.6, far above the (1/N) corrections of the approximation.
    """
    t = np.arange(20_000)
    assert autocorrelation_time(np.sin(2 * np.pi * t / 40), 500) == 500
