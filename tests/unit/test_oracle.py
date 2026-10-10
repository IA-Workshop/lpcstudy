"""Tests for lpcstudy.oracle: oracle weight, regret identity, characteristic horizon."""

from __future__ import annotations

import numpy as np
import pytest

from lpcstudy.oracle import characteristic_horizon, curvature, hybrid_mse, oracle_weight
from unit_helpers import _moments_from_draws


def test_oracle_weight_minimizes_ensemble_mse() -> None:
    """w* equals the brute-force minimizer of the ensemble MSE over [0, 1].

    Reference: brute force. The empirical mean of (w e_C + (1 - w) e_P)^2 over the raw
    draws is evaluated on a grid of 2001 points in [0, 1] and the argmin is taken. It
    uses the draws directly, not ``hybrid_mse`` or the moments of ``oracle_weight``;
    the moments passed to ``oracle_weight`` come from the test helper (plain sample
    means), not from ``lpcstudy.ensemble``. 5 states x 3 horizons, 400 draws each.
    Tolerance ``atol=1e-3`` (plus the default rtol 1e-5), unchanged: the mean square is
    a convex quadratic in w, so the grid argmin is the grid point nearest to the
    (clipped) exact minimizer, an error of at most half the spacing, 2.5e-4 (spacing
    5e-4), plus round-off; 1e-3 is 4 times that bound.
    """
    rng = np.random.default_rng(0)
    common = rng.standard_normal((5, 400, 3))
    cp = 0.5 * common + rng.standard_normal((5, 400, 3))
    plp = 0.3 * common + 0.7 * rng.standard_normal((5, 400, 3))
    moments = _moments_from_draws(cp, plp)
    grid = np.linspace(0, 1, 2001)
    brute = np.array([[grid[np.argmin([np.mean((w * cp[i, :, h] + (1 - w) * plp[i, :, h]) ** 2)
                                       for w in grid])] for h in range(3)] for i in range(5)])
    assert np.allclose(oracle_weight(moments), brute, atol=1e-3)


def test_oracle_weight_clips_to_boundary() -> None:
    """When the unconstrained minimizer is outside [0, 1], the weight clips to 0 or 1.

    Reference: brute force on the raw draws over the grid of 2001 points in [0, 1], as
    in ``test_oracle_weight_minimizes_ensemble_mse``. Manufactured inputs: with
    e_P = 0.3 c and e_C = c + 0.3 u (c, u independent N(0, 1)),
    w* = E[e_P (e_P - e_C)] / E[(e_C - e_P)^2] ~ -0.21 / 0.58 = -0.36 < 0, so the
    constrained minimizer is 0; with the roles swapped w* ~ 1.36 > 1, so it is 1.
    The test asserts that the unclipped value is outside [0, 1] (the premise, true by a
    wide margin: the standard error of the sample w* at 400 draws is about 0.008, a
    Monte Carlo estimate, against a distance of 0.36 to the boundary) and then that ``oracle_weight`` equals the grid argmin.
    Tolerance: exact equality. A convex quadratic whose vertex lies outside [0, 1] has
    its grid minimum at the end point 0.0 or 1.0 (both exactly representable and
    exact in ``np.linspace``), and ``np.clip`` returns those values exactly.
    """
    rng = np.random.default_rng(10)
    common = rng.standard_normal((4, 400, 3))
    noise = 0.3 * rng.standard_normal((4, 400, 3))
    grid = np.linspace(0, 1, 2001)

    def brute_force(cp: np.ndarray, plp: np.ndarray) -> np.ndarray:
        return np.array([[grid[np.argmin([np.mean((w * cp[i, :, h] + (1 - w) * plp[i, :, h])
                                                   ** 2) for w in grid])]
                          for h in range(3)] for i in range(4)])

    for cp, plp, expected in ((common + noise, 0.3 * common, 0.0),
                              (0.3 * common, common + noise, 1.0)):
        moments = _moments_from_draws(cp, plp)
        raw = oracle_weight(moments, clip=False)
        if expected == 0.0:
            assert np.all(raw < 0.0)
        else:
            assert np.all(raw > 1.0)
        got = oracle_weight(moments)
        assert np.array_equal(got, brute_force(cp, plp))
        assert np.array_equal(got, np.full_like(got, expected))


def test_regret_identity() -> None:
    """V(w) - V(w*) = c (w - w*)^2 for the unclipped optimum (FW Prop. 5).

    Reference: the exact quadratic identity of FW Prop. 5. All three operands
    (``hybrid_mse``, ``oracle_weight``, ``curvature``) are code under test, so this
    checks their mutual consistency only: the quadratic in ``hybrid_mse`` must have its
    vertex at ``oracle_weight`` and curvature ``curvature`` (a sign or factor error in
    any one fails). It is anchored to the raw draws by the next test,
    ``test_regret_identity_matches_draws``.
    Tolerance: ``np.allclose`` defaults (rtol 1e-5, atol 1e-8), unchanged. The
    identity is exact algebra on the sample moments, so the difference is round-off
    (about 1e-16 on O(1) values, below 1e-14 after subtraction).
    """
    rng = np.random.default_rng(1)
    cp, plp = rng.standard_normal((4, 300, 2)), 0.8 * rng.standard_normal((4, 300, 2))
    moments = _moments_from_draws(cp, plp)
    w_star = oracle_weight(moments, clip=False)
    w = np.full_like(w_star, 0.3)
    lhs = hybrid_mse(moments, w) - hybrid_mse(moments, w_star)
    assert np.allclose(lhs, curvature(moments) * (w - w_star) ** 2)


def test_regret_identity_matches_draws() -> None:
    """The regret identity holds with V computed directly from the draws.

    Reference: V(w) = mean over the 300 draws of (w e_C + (1 - w) e_P)^2, computed from
    the raw draws with no use of ``hybrid_mse`` or the moments (FW Prop. 5). This
    anchors ``hybrid_mse`` to data. (i) ``hybrid_mse(w)`` equals V(w) from the draws at
    w = 0.3 and at the unclipped w*. (ii) V(0.3) - V(w*) equals c (0.3 - w*)^2, with c
    the ``curvature``.
    Tolerance ``atol=1e-12``, ``rtol=0``: V is a mean of 300 products of O(1) numbers,
    each side has a worst-case round-off bound of about 300 * 1.1e-16 * 2 = 7e-14
    (observed errors are far smaller), and the differences cancel O(1) terms; 1e-12
    leaves a factor of 15 over the worst-case bound.
    """
    rng = np.random.default_rng(1)
    cp, plp = rng.standard_normal((4, 300, 2)), 0.8 * rng.standard_normal((4, 300, 2))
    moments = _moments_from_draws(cp, plp)
    w_star = oracle_weight(moments, clip=False)
    w = np.full_like(w_star, 0.3)

    def from_draws(weight: np.ndarray) -> np.ndarray:
        return np.mean((weight[:, None, :] * cp + (1 - weight[:, None, :]) * plp) ** 2, axis=1)

    np.testing.assert_allclose(hybrid_mse(moments, w), from_draws(w), rtol=0.0, atol=1e-12)
    np.testing.assert_allclose(hybrid_mse(moments, w_star), from_draws(w_star),
                               rtol=0.0, atol=1e-12)
    np.testing.assert_allclose(from_draws(w) - from_draws(w_star),
                               curvature(moments) * (w - w_star) ** 2, rtol=0.0, atol=1e-12)


def test_characteristic_horizon_and_censoring() -> None:
    """First crossing of sqrt(mse + rho^2) above theta; censored rows return H_max.

    Reference: hand computation. With rho = 0, theta = 0.2, row 1 has
    sqrt(mse) = 0, 0.1, 0.224, 0.447, so the first value above 0.2 is at H = 3 (event);
    row 2 is identically 0, never crosses, and is censored at H_max = 4 (no event).
    Tolerance: none, exact equality of integers and booleans. The strict inequality
    is not at a boundary: 0.224 and 0.1 are away from theta = 0.2 by 0.024 and 0.1.
    """
    mse = np.array([[0.0, 0.01, 0.05, 0.2], [0.0, 0.0, 0.0, 0.0]])
    horizon, event = characteristic_horizon(mse, np.arange(1, 5), 0.0, 0.2)
    assert horizon.tolist() == [3, 4] and event.tolist() == [True, False]


def test_characteristic_horizon_noise_in_quadrature() -> None:
    """Horizons are measured against the noisy observation: rho adds in quadrature.

    Reference: hand computation on the same mse as the noise-free test, with
    rho = 0.19 and theta = 0.2. Row 1: sqrt(0 + 0.0361) = 0.19 <= 0.2, then
    sqrt(0.01 + 0.0361) = sqrt(0.0461) = 0.2147 > 0.2, so H = 2 (event). Row 2 stays at
    0.19 for every horizon and is censored at H_max = 4. Expected ([2, 4],
    [True, False]). Also, non-contiguous horizons raise ``ValueError`` (PRIME.4).
    Tolerance: none, exact equality; the crossing is not at a boundary (0.19 and
    0.2147 are 0.01 and 0.015 from theta, far above round-off).
    """
    mse = np.array([[0.0, 0.01, 0.05, 0.2], [0.0, 0.0, 0.0, 0.0]])
    horizon, event = characteristic_horizon(mse, np.arange(1, 5), 0.19, 0.2)
    assert horizon.tolist() == [2, 4] and event.tolist() == [True, False]
    with pytest.raises(ValueError, match="horizons 1..H_max"):
        characteristic_horizon(mse, np.arange(2, 6), 0.0, 0.2)
