"""Tests for lpcstudy.ensemble: retrieval spread."""

from __future__ import annotations

import numpy as np
import pytest


def test_retrieval_spread() -> None:
    """Noise sensitivity is 0 for a fixed analog and ~1 for unit-noise wander.

    Reference: (a) property: a fixed analog has zero spread. (b) exact distribution:
    for iid N(0, rho^2) entries N = sqrt(mean_r ||V_r - mean V||^2 / D) / rho is the
    sample standard deviation over R draws divided by rho, with expectation
    sqrt((R - 1)/R) ~ 1 - 2.5e-5 (bias -2.5e-5 at R = 20 000).
    Tolerances. (a) ``== 0.0`` exactly: the mean of 50 ones is exactly 1.0 in
    float64, so the centered values are exactly 0. (b) ``rel=0.02``, unchanged: the
    Monte Carlo relative standard error of N is 0.5 sqrt(2/(R D)) = 1.9e-3 for
    R = 20 000 draws and D = 7 coordinates (the sample variance has relative standard
    deviation sqrt(2/n) with n = R D), so 0.02 is 10.6 standard errors; the bias
    -2.5e-5 is negligible.
    """
    from lpcstudy.ensemble import retrieval_spread

    fixed = np.ones((1, 50, 7))
    assert retrieval_spread(fixed, 0.1)[0] == 0.0
    wander = 0.1 * np.random.default_rng(8).standard_normal((1, 20_000, 7))
    assert retrieval_spread(wander, 0.1)[0] == pytest.approx(1.0, rel=0.02)
