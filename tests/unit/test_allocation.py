"""Tests for lpcstudy.allocation: closed-form weight and the seed proxy."""

from __future__ import annotations

import numpy as np
import pytest

from lpcstudy.allocation import SeedProxy, closed_form_weight
from lpcstudy.oracle import oracle_weight
from unit_helpers import _moments_from_draws


def test_closed_form_matches_uncorrelated_isotropic_case() -> None:
    """With independent seeds of variances eps^2 and delta^2, w* -> delta^2/(eps^2+delta^2).

    Reference: the analytic value delta^2/(eps^2+delta^2) = 0.81/0.97 = 0.8351
    (FW Cor. 1), written out in the test (not taken from ``closed_form_weight``).
    The tested quantity is ``oracle_weight`` of plain sample moments of 200 000
    independent draws (moments from the test helper, not from ``lpcstudy.ensemble``).

    Tolerance ``abs=5e-3``: Monte Carlo error, kept unchanged. The delta-method
    standard error of the sample weight w = (b - c)/(a + b - 2c), with a, b the
    sample second moments and c the sample cross moment, at N = 200 000 is
    sqrt([(b/D^2)^2 2 a^2 + (a/D^2)^2 2 b^2 + ((b-a)/D^2)^2 a b]/N) = 8.3e-4
    (a = eps^2, b = delta^2, D = a + b), so 5e-3 is 6.0 standard errors.
    """
    rng = np.random.default_rng(2)
    eps, delta = 0.4, 0.9
    cp = eps * rng.standard_normal((1, 200_000, 1))
    plp = delta * rng.standard_normal((1, 200_000, 1))
    w_star = oracle_weight(_moments_from_draws(cp, plp))[0, 0]
    analytic = delta**2 / (eps**2 + delta**2)
    assert w_star == pytest.approx(analytic, abs=5e-3)


def test_closed_form_weight_exact_values() -> None:
    """``closed_form_weight`` equals delta^2/(eps^2+delta^2) written out by hand.

    Reference: the formula evaluated on exact rationals (FW Cor. 1): 0.16, 0.81 give
    81/97; eps^2 = 0 gives 1 (all weight on the physics forecaster); delta^2 = 0 gives 0;
    equal seeds give 1/2.
    Tolerance ``rel=1e-14``: one addition and one division in float64, a relative
    error of at most about 3 * 1.1e-16 = 3.3e-16, so 1e-14 leaves a factor of 30.
    """
    got = closed_form_weight(np.array([0.16, 0.0, 0.5, 0.3]), np.array([0.81, 2.0, 0.0, 0.3]))
    assert got == pytest.approx([81 / 97, 1.0, 0.0, 0.5], rel=1e-14, abs=0.0)


def test_seed_proxy_recovers_parameters() -> None:
    """Log-scale least squares recovers slope and floor of seed^2 = a f^2 + b g^2.

    Reference: manufactured solution. The data are generated with the known
    (a, b) = (2, 3) and multiplicative log-normal noise of sd 0.01, n = 500.
    Tolerances ``rel=0.02`` (slope) and ``rel=0.05`` (floor), kept unchanged: the
    linearized standard errors of log a and log b are the square roots of the
    diagonal of sigma^2 (J^T J)^-1, with J the Jacobian of log(seed^2) with
    respect to (log a, log b) on the test's own 500 states and sigma = 0.01: 5.8e-4
    and 1.7e-3 (relative errors of a and b). The tolerances are therefore about
    34 and 29 standard errors: loose, and they leave room for the soft-L1 loss
    (for residuals near 0.01 it differs from a quadratic by a relative z/4 = 2.5e-5,
    with z the squared residual) and the nonlinearity.
    """
    rng = np.random.default_rng(5)
    rho = 0.02
    feature = rng.uniform(0.01, 0.2, 500)
    floor = rho * rng.uniform(0.5, 2.0, 500)
    seed_sq = (2.0 * feature**2 + 3.0 * floor**2) * np.exp(0.01 * rng.standard_normal(500))
    proxy = SeedProxy.fit(feature**2, floor**2, seed_sq)
    assert proxy.slope == pytest.approx(2.0, rel=0.02)
    assert proxy.floor == pytest.approx(3.0, rel=0.05)
