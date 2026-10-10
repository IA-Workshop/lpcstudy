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


def _uniform_known_dimension(m: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Reference set, interior queries and orthonormal map for the unit cube ``[0, 1]^m``.

    The set is ``c + U u`` with ``u`` uniform on ``[0, 1]^m``, ``U`` (7 x m) with orthonormal
    columns (first factor of ``qr`` of a standard-normal matrix) and a fixed offset ``c`` in
    R^7. The map is an isometry, so Euclidean neighbor distances in R^7 equal those in
    ``u``-space. Queries are 2000 fresh points uniform in the interior box ``[0.2, 0.8]^m``.
    Fixed seed 50053 (test data only, not a study stream).
    """
    rng = np.random.default_rng(50053)
    basis = np.linalg.qr(rng.standard_normal((7, m)))[0]
    offset = rng.standard_normal(7)
    reference = offset + rng.uniform(size=(20_000, m)) @ basis.T
    queries = offset + rng.uniform(0.2, 0.8, size=(2_000, m)) @ basis.T
    assert np.allclose(basis.T @ basis, np.eye(m), atol=1e-14)
    return reference, queries, basis


def _assert_interior(reference: np.ndarray, queries: np.ndarray) -> None:
    """Premise: the 20-neighbor ball of every query lies inside the unit cube (radius < 0.2)."""
    from scipy.spatial import cKDTree

    radius = cKDTree(reference).query(queries, k=20)[0][:, -1]
    assert radius.max() < 0.2


@pytest.mark.parametrize("m", [1, 2, 3])
def test_local_dimension_known_sets(m: int) -> None:
    """Levina-Bickel estimate is unbiased on uniform sets of known dimension 1, 2, 3 in R^7.

    Reference: the exact law of the estimator, independent of the code. Sets: a segment,
    a unit square and a unit cube, each embedded in R^7 by a fixed orthonormal map, with
    n = 2e4 points, k = 20 (the study's setting; ``local_dimension.__defaults__ == (20,)`` is
    asserted) and 2000 queries uniform in the interior box [0.2, 0.8]^m, not in the reference.
    Given T_k (the distance to the k-th neighbor) the k - 1 inner neighbors are iid uniform in
    the ball, and every ball lies inside the set (asserted: T_20 < 0.2; its maximum is about
    0.078 for the cube), so S = sum_j log(T_k / T_j) ~ Gamma(k - 1, rate m) exactly for any n.
    The code's per-query estimate (k - 2) / S is the "divide by k - 2" variant of Levina and
    Bickel (2005), NIPS 17, Sec. 3.1: mean m, sd m / sqrt(k - 3) = 0.2425 m.

    The statistic is the arithmetic mean of the per-query estimates. That is the published
    aggregator (Levina and Bickel 2005, NIPS 17, eq. 9). The code's callers aggregate with the
    median over states, which is not the published aggregator; its departure is pinned in
    ``test_local_dimension_median_poisson_value``.

    Boundary queries are excluded on purpose. Their balls are truncated by the edge of the
    set, which biases the estimator down (for the cube, 32% of points have T_20 reaching the
    edge; bias -2.2% on the mean, -5.6% on the median at m = 3). That is a property of the
    estimator, not a check of the code, and its reference value would have to come from
    simulation, not from an independent law.

    Tolerance: ``abs(mean / m - 1) <= 0.03``, tightened from the roadmap's 10%
    (applied-mathematician, WU-0005 log). The mean of 2000 estimates with sd 0.2425 m has
    sd 0.0054 m if independent; 200 simulated seeds gave sd of mean / m of 0.0054, 0.0057,
    0.0057 for m = 1, 2, 3 (inflation by shared neighbors at most 1.06), and the mean of
    mean / m was 0.9997, 0.9999, 1.0007 (bias nil). 3% is 5.3 standard deviations, so a false
    alarm over the three m has probability about 1e-6. A tolerance of 10% would not detect
    the normalization: dividing by k - 1 instead of k - 2 multiplies every estimate by
    19/18, +5.56%, which is 2.56% beyond the 3% bound (4.5 sd), so a miss has probability
    below 1e-5.
    """
    from lpcstudy.oracle import local_dimension

    assert local_dimension.__defaults__ == (20,)
    reference, queries, _ = _uniform_known_dimension(m)
    _assert_interior(reference, queries)
    estimates = local_dimension(reference, queries)
    assert estimates.shape == (2_000,)
    assert abs(estimates.mean() / m - 1) <= 0.03


@pytest.mark.parametrize("m", [1, 2, 3])
def test_local_dimension_median_poisson_value(m: int) -> None:
    """The median of the per-query estimates sits at 0.964 m, 3.6% below the mean.

    This is a characterization of the aggregator the code's callers use (the median over
    states, as H1b does), not a check of the published one: Levina and Bickel (2005), NIPS 17,
    eq. 9, average the per-point estimates arithmetically, and no median appears there. The
    per-query estimate (k - 2) / S has S ~ Gamma(19, rate m), so its median is
    18 m / median(Gamma(19, 1)) = 0.9642 m, below the mean m because the distribution is
    skewed. The test documents that departure; it does not endorse it.

    Reference: the exact Gamma law, with the constant computed as
    ``18 / scipy.stats.gamma(19).median()`` (independent of the code); same data, queries
    and premises as ``test_local_dimension_known_sets``.

    Tolerance: ``abs(median / (c m) - 1) <= 0.03`` with c = 0.9642. Over 200 simulated seeds
    the median / m averaged 0.9641, 0.9643, 0.9653 for m = 1, 2, 3, with sd 0.006 to 0.0066
    (applied-mathematician, WU-0005 log), i.e. a relative sd of at most 0.0068 about c m;
    3% is 4.4 sd (false alarm about 1e-5 per m). This test alone does not separate the median
    from the mean: an estimate centered at m would be +3.7% from c m, only 1 sd beyond the
    bound. It pins the value of the median (and so a gross change of the per-query law),
    while the mean test, with its 3% bound about m, fixes the normalization.
    """
    from scipy.stats import gamma

    from lpcstudy.oracle import local_dimension

    reference, queries, _ = _uniform_known_dimension(m)
    _assert_interior(reference, queries)
    constant = 18.0 / gamma(19).median()
    assert constant == pytest.approx(0.9642, abs=5e-5)
    median = float(np.median(local_dimension(reference, queries)))
    assert abs(median / (constant * m) - 1) <= 0.03
