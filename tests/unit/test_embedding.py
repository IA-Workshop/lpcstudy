"""Tests for ``lpcstudy.embedding``: delay vectors, AMI delay, ACF time.

The embedding module turns one measured signal into delay vectors and picks the
delay and the spacing of sampled states (see its module docstring). Each test
below compares the code with an independent reference: a hand calculation, a
published value, or a closed-form property of a sine wave.
"""

from __future__ import annotations

import jax.numpy as jnp
import numpy as np

from lpcstudy.embedding import autocorrelation_time, delay_vectors, select_delay
from lpcstudy.systems import SYSTEMS, make_flow_step, simulate_trajectory


def test_delay_vectors_order() -> None:
    """Delay vectors list the present value first, then older values.

    What is checked: ``X_t = (x_t, x_{t-tau}, ...)``.
    Reference: the definition, worked by hand on the series ``x_i = i``. With
    ``t = 10``, ``tau = 3`` and ``D = 3`` the vector is ``(x_10, x_7, x_4) =
    (10, 7, 4)``.
    Tolerance: none (exact equality). The integers 0..19 are exact in float64
    and the function only picks entries, so there is no round-off.
    """
    series = np.arange(20.0)
    out = delay_vectors(series, np.array([10]), 3, 3)
    assert out.tolist() == [[10.0, 7.0, 4.0]]


def test_regression_ami_delay_lorenz_band() -> None:
    """The delay chosen for Lorenz-63 stays near the published value.

    At 1 LT = 30 steps the first AMI minimum lies near 0.15 to 0.2 time units.

    This is a REGRESSION GUARD (WU-0013.2, DEF-0007 audit item 2), not evidence
    of correctness: it only keeps the code from drifting far from a published
    order of magnitude.

    Source (LPC.PC.21a; verified by the ``researcher``, note
    ``docs/agent/notes/2026-10-11-research-ami-delay.md``, retrieved
    2026-10-11): Deshmukh, Bradley, Garland and Meiss, "Using Curvature to
    Select the Time Lag for Delay Reconstruction", arXiv:2003.06509v1 (7 Mar
    2020), Sec. IV.B "Classic Lorenz Attractor", Fig. 5 (PDF p. 8). For x(t) of
    Lorenz-63 (sigma = 10, beta = 8/3, rho = 28; RK4 with a time step of 0.01;
    90,000 points; AMI by TISEAN ``mutual``, bin count not stated) "the first
    minima of both curves fall near tau = 18", that is about 0.18 time units,
    which is 4.9 steps at Delta t = 0.0368. The researcher reads that minimum in
    Fig. 5 as a shallow shoulder (AMI about 0.65 at tau = 18 against 0.7 near
    30; a reading of the figure, not a quotation). The paper also says that,
    from this AMI profile, a practitioner would quite likely choose tau_I = 60
    (0.60 time units, 16.3 steps).

    The citation fixes only the order of magnitude of the first minimum, not a
    pinned value, so the test stays a regression guard. The estimator here
    differs (32 equiprobable bins, 3-point smoothing), and the location of a
    first minimum depends on the estimator. The test does not pin the current
    value: ``select_delay`` currently returns 5 steps = 0.184 time units at
    Delta t = 0.0368, but any value from 3 to 8 passes.

    Tolerance: the integer band [3, 8] steps (0.110 to 0.294 time units),
    unchanged. The cited 0.18 time units (4.9 steps) lies inside it, and so does
    the current value. The band is kept, neither widened nor tightened: the
    researcher's assessment is that the evidence does not justify a tighter band
    without a stated estimator-matching tolerance (a band of about [4, 6] steps
    would be weakly supported by this source and by an informal course page,
    0.16 time units, which is not peer reviewed). The estimator is the default
    32-equiprobable-bin histogram AMI with the first local minimum of a 3-point
    smoothed curve, on 55 000 normalized samples (60 000 steps, 5 000 burn-in).
    """
    spec = SYSTEMS["lorenz63"]
    step = make_flow_step(spec, spec.params, 0.0368)
    x = simulate_trajectory(step, jnp.asarray(spec.initial_state), 60_000)[
        5_000:,
        0,
    ]
    assert 3 <= select_delay((x - x.mean()) / x.std(), 60) <= 8


def test_autocorrelation_time_sine_is_censored() -> None:
    """A pure sine wave never decorrelates, so the result is ``max_lag``.

    The function returns the censoring value because a sine never forgets
    itself.

    Reference: a property of the biased FFT autocorrelation estimator for a pure
    sinusoid of period 40 over N = 20 000 samples: ``ACF(k) ~ (1 - k/N) cos(2 pi
    k / 40)``. At ``k = max_lag = 500``, ``cos(2 pi 500/40) = cos(25 pi) = -1``,
    so ``|ACF(500)| ~ 0.975``. The envelope at every lag ``k <= 500`` is
    ``max_{500 >= j >= k} |ACF(j)|``, which is at least ``|ACF(500)|`` ~ 0.975,
    above ``1/e = 0.368``. So it never falls below ``1/e`` and the function
    returns the censoring value ``max_lag = 500``.
    Tolerance: none (exact integer equality). The margin 0.975 against 0.368 is
    a factor of 2.6, far above the ``1/N`` corrections of the approximation.
    """
    t = np.arange(20_000)
    assert autocorrelation_time(np.sin(2 * np.pi * t / 40), 500) == 500
