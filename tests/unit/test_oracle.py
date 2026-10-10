"""Tests for lpcstudy.oracle: oracle weight, regret identity, characteristic horizon."""

from __future__ import annotations

import numpy as np

from lpcstudy.oracle import characteristic_horizon, curvature, hybrid_mse, oracle_weight
from unit_helpers import _moments_from_draws


def test_oracle_weight_minimizes_ensemble_mse() -> None:
    """w* equals the brute-force minimizer of the ensemble MSE over [0, 1]."""
    rng = np.random.default_rng(0)
    common = rng.standard_normal((5, 400, 3))
    cp = 0.5 * common + rng.standard_normal((5, 400, 3))
    plp = 0.3 * common + 0.7 * rng.standard_normal((5, 400, 3))
    moments = _moments_from_draws(cp, plp)
    grid = np.linspace(0, 1, 2001)
    brute = np.array([[grid[np.argmin([np.mean((w * cp[i, :, h] + (1 - w) * plp[i, :, h]) ** 2)
                                       for w in grid])] for h in range(3)] for i in range(5)])
    assert np.allclose(oracle_weight(moments), brute, atol=1e-3)


def test_regret_identity() -> None:
    """V(w) - V(w*) = c (w - w*)^2 for the unclipped optimum (FW Prop. 5)."""
    rng = np.random.default_rng(1)
    cp, plp = rng.standard_normal((4, 300, 2)), 0.8 * rng.standard_normal((4, 300, 2))
    moments = _moments_from_draws(cp, plp)
    w_star = oracle_weight(moments, clip=False)
    w = np.full_like(w_star, 0.3)
    lhs = hybrid_mse(moments, w) - hybrid_mse(moments, w_star)
    assert np.allclose(lhs, curvature(moments) * (w - w_star) ** 2)


def test_characteristic_horizon_and_censoring() -> None:
    """First crossing of sqrt(mse + rho^2) above theta; censored rows return H_max."""
    mse = np.array([[0.0, 0.01, 0.05, 0.2], [0.0, 0.0, 0.0, 0.0]])
    horizon, event = characteristic_horizon(mse, np.arange(1, 5), 0.0, 0.2)
    assert horizon.tolist() == [3, 4] and event.tolist() == [True, False]
