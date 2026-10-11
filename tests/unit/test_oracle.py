"""Tests for lpcstudy.oracle: oracle weight, regret identity, characteristic horizon."""

from __future__ import annotations

import numpy as np
import pytest

from lpcstudy.oracle import characteristic_horizon, curvature, excess_mse, hybrid_mse, \
    oracle_weight
from unit_helpers import _moments_from_draws, moments_from_triples, realizable_triples


def _direct_v(weight: np.ndarray, e_c: np.ndarray, e_p: np.ndarray, cross: np.ndarray
              ) -> np.ndarray:
    """V(w) = w^2 E_C + (1 - w)^2 E_P + 2 w (1 - w) C evaluated directly (independent of code)."""
    return weight**2 * e_c + (1 - weight) ** 2 * e_p + 2 * weight * (1 - weight) * cross


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


def test_excess_mse_matches_grid_minimum() -> None:
    """``excess_mse`` equals V(w) minus the brute-force minimum of V over [0, 1] (P1(a)).

    Reference: brute force. V(w) = w^2 E_C + (1-w)^2 E_P + 2w(1-w) C is evaluated directly
    from the moment triple on ``np.linspace(0, 1, 10_000)`` (h = 1/9999; both end points
    exact), and the reference excess is V(w) - min over the grid. Inputs: 200 manufactured
    realizable triples (70 with u in (-5, 0), 60 in [0, 1], 70 in (1, 6); c log-uniform on
    [1e-3, 10]); the reference sees only (E_C, E_P, C). w is uniform on [0, 1] with
    |w - w*| >= 0.1 (rejection, fixed seed), plus w = 0 and w = 1 whenever |w - w*| >= 0.1
    (the endpoint is kept only under that guard) or w equals w* (then excess and reference
    are both exactly 0).
    Tolerance ``rtol=1e-6``, ``atol=0``: the grid minimum exceeds V(w*) by at most
    c (h/2)^2 = 2.5005e-9 c, and the excess is at least c (w - w*)^2 >= 0.01 c (also when u
    is clipped: (w - w*)(w + w* - 2u) >= (w - w*)^2), so the relative bias is at most
    2.5e-7, four times below 1e-6. Round-off is about 1e-12 relative (V <= 46 c on these
    ranges, over an excess of at least 0.01 c).
    """
    rng = np.random.default_rng(20261011)
    t = realizable_triples(rng, 70, 60, 70)
    e_c, e_p, cross = t["E_C"][:, None], t["E_P"][:, None], t["C"][:, None]
    moments = moments_from_triples(e_c, e_p, cross)
    w_star = oracle_weight(moments)[:, 0]
    assert np.allclose(w_star, np.clip(t["u"], 0.0, 1.0), rtol=1e-9, atol=1e-9)
    grid = np.linspace(0.0, 1.0, 10_000)
    v_grid = _direct_v(grid[None, :], e_c, e_p, cross)  # (200, 10000)
    v_min = v_grid.min(axis=1)

    weights = rng.uniform(0.0, 1.0, 200)
    for _ in range(100):
        bad = np.abs(weights - w_star) < 0.1
        if not bad.any():
            break
        weights[bad] = rng.uniform(0.0, 1.0, bad.sum())
    assert not (np.abs(weights - w_star) < 0.1).any()
    got = excess_mse(moments, weights[:, None])[:, 0]
    ref = _direct_v(weights, e_c[:, 0], e_p[:, 0], cross[:, 0]) - v_min
    np.testing.assert_allclose(got, ref, rtol=1e-6, atol=0.0)

    used = excluded = 0
    for end in (0.0, 1.0):
        d = np.abs(end - w_star)
        keep = d >= 0.1
        same = end == w_star
        used += int(keep.sum()) + int(same.sum())
        excluded += int((~keep & ~same).sum())
        w_end = np.full((200, 1), end)
        got_end = excess_mse(moments, w_end)[:, 0]
        ref_end = _direct_v(w_end[:, 0], e_c[:, 0], e_p[:, 0], cross[:, 0]) - v_min
        np.testing.assert_allclose(got_end[keep], ref_end[keep], rtol=1e-6, atol=0.0)
        assert same.sum() > 0
        assert np.all(got_end[same] == 0.0) and np.all(ref_end[same] == 0.0)
    assert used > 150 and excluded > 0  # guard exercised; counts: excluded end points


def test_excess_mse_is_nonnegative_and_zero_at_optimum() -> None:
    """The excess is >= 0 everywhere, exactly 0.0 at w*, and >= 0 one to five ulps from w*.

    Reference: exact algebra (P1(a)): V(w) - V(w*) = c [(w - u)^2 - (w* - u)^2] >= 0 with
    equality at w = w*. In IEEE arithmetic the form used is >= 0 exactly (rounding is
    monotone and |w - u| >= |w* - u|), and exactly 0.0 at w* computed from the same u; the
    factored form fails the sign within 5 ulps of w* (measured by the mathematician).
    Inputs: the 200 triples of ``test_excess_mse_matches_grid_minimum`` (same seed), w on
    a 21-point grid of [0, 1], at w*, and at ``np.nextafter`` of w* in both directions up
    to 5 steps (clipped to [0, 1]). Tolerance: none (exact comparisons).
    """
    rng = np.random.default_rng(20261011)
    t = realizable_triples(rng, 70, 60, 70)
    moments = moments_from_triples(t["E_C"][:, None], t["E_P"][:, None], t["C"][:, None])
    w_star = oracle_weight(moments)
    assert np.all(excess_mse(moments, w_star) == 0.0)
    for w in np.linspace(0.0, 1.0, 21):
        assert np.all(excess_mse(moments, np.full_like(w_star, w)) >= 0.0)
    near_up, near_down = w_star, w_star
    for _ in range(5):
        near_up = np.nextafter(near_up, np.inf)
        near_down = np.nextafter(near_down, -np.inf)
        for near in (near_up, near_down):
            assert np.all(excess_mse(moments, np.clip(near, 0.0, 1.0)) >= 0.0)


def test_excess_mse_clipped_case() -> None:
    """When u > 1, c (w - w*)^2 underestimates V(w) - V(w*); ``excess_mse`` is exact (DEF-0002).

    Reference: direct evaluation of the quadratic. E_C = 1, E_P = 4, C = 1.5 (realizable:
    E_C E_P - C^2 = 1.75 >= 0) give c = 2, b = E_P - C = 2.5, u = 1.25, w* = 1. With
    w = 0.5: V(0.5) = 0.25 + 1 + 0.75 = 2.0 and V(1) = 1.0, so the excess is 1.0, against
    c (w - w*)^2 = 0.5. Tolerance: exact ``==``; every operand and intermediate is dyadic
    (0.5625, 0.0625, 2.0), so no rounding occurs.
    """
    moments = moments_from_triples(np.array([[1.0]]), np.array([[4.0]]), np.array([[1.5]]))
    w = np.array([[0.5]])
    assert oracle_weight(moments, clip=False)[0, 0] == 1.25
    assert oracle_weight(moments)[0, 0] == 1.0
    got = excess_mse(moments, w)[0, 0]
    direct = _direct_v(0.5, 1.0, 4.0, 1.5) - _direct_v(1.0, 1.0, 4.0, 1.5)
    assert direct == 1.0
    assert got == 1.0
    assert curvature(moments)[0, 0] * (0.5 - 1.0) ** 2 == 0.5 < got


def test_excess_mse_unclipped_equals_curvature_form_and_broadcasts() -> None:
    """For u in [0, 1] the excess is c (w - u)^2, and 3-D weights broadcast the moments.

    Reference: the FW Prop. 5 identity (the unclipped case of ``test_regret_identity``)
    with the curvature and u written out from the triple by hand: c = E_C + E_P - 2C,
    u = (E_P - C) / c. Also: ``excess_mse`` of a ``(n, E, nH)`` weight equals the 2-D
    result per draw, exactly (same elementwise operations), and a wrong shape raises.
    Tolerance ``rtol=1e-12``: a few operations at ~1e-16 each over an excess >= 1e-3 c
    (w is at least 0.05 from u by construction).
    """
    rng = np.random.default_rng(5)
    t = realizable_triples(rng, 0, 30, 0, inside=(0.2, 0.8))
    e_c, e_p, cross = t["E_C"][:, None], t["E_P"][:, None], t["C"][:, None]
    moments = moments_from_triples(e_c, e_p, cross)
    c = e_c + e_p - 2 * cross
    u = (e_p - cross) / c
    w = np.where(u > 0.5, u - 0.1, u + 0.1)
    np.testing.assert_allclose(excess_mse(moments, w), c * (w - u) ** 2, rtol=1e-12, atol=0.0)
    three = np.stack([w, np.clip(w + 0.05, 0.0, 1.0)], axis=1)  # (n, 2, 1)
    got = excess_mse(moments, three)
    assert got.shape == three.shape
    assert np.array_equal(got[:, 0, :], excess_mse(moments, three[:, 0, :]))
    assert np.array_equal(got[:, 1, :], excess_mse(moments, three[:, 1, :]))
    with pytest.raises(ValueError, match="weight shape"):
        excess_mse(moments, np.zeros((30, 2)))
    with pytest.raises(ValueError, match="weight shape"):
        excess_mse(moments, np.zeros(30))


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
    aggregator (Levina and Bickel 2005, NIPS 17, eq. 9). The median of the per-query estimates
    is not the published aggregator; its value is pinned against the Gamma law in
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

    The test computes ``np.median`` itself and pins the median of the distribution of the
    per-query estimates against the exact Gamma law; it does not exercise any caller's
    aggregation. The published aggregator is the arithmetic mean (Levina and Bickel 2005,
    NIPS 17, eq. 9; no median appears there). The per-query estimate (k - 2) / S has
    S ~ Gamma(19, rate m), so its median is 18 m / median(Gamma(19, 1)) = 0.9642 m, below the
    mean m because the distribution is skewed.

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


@pytest.mark.parametrize("m", [1, 2, 3])
def test_inverse_dimension_is_unbiased_on_known_sets(m: int) -> None:
    """The per-state reference ``S / (k - 1)`` has mean ``1 / m`` on uniform sets of dimension m.

    Reference: the exact Gamma law, independent of the code (applied-mathematician, WU-0002.4-5
    log, Job 1 item 2). On the sets, queries and premises of ``test_local_dimension_known_sets``
    (segment, square, cube in R^7; k = 20; interior queries with T_20 < 0.2, asserted), the
    k - 1 inner neighbors of a query are iid uniform in the ball given T_k, so
    ``S = sum_j ln(T_k / T_j)`` satisfies ``S m ~ Gamma(k - 1, 1)`` exactly and
    ``E[S / (k - 1)] = 1 / m`` exactly. Inverting the k - 2 estimate of ``local_dimension``
    without the correction (``1 / local_dim = S / (k - 2)``) would be too high by
    ``(k - 1) / (k - 2) - 1 = +5.56%``.

    Tolerance: ``abs(mean * m - 1) <= 0.03`` (the tolerance of the ``local_dimension`` mean
    test). The per-query relative sd is ``1 / sqrt(k - 1) = 0.229``, so the mean of 2000
    queries has sd 0.0054 (inflation by shared neighbors at most 1.06 in 900 simulated cases,
    applied-mathematician), and 3% is 5.5 sd (a false alarm over the three m has probability
    about 1e-7). The k - 2 slip sits at +5.56%, 4.7 sd beyond the bound, so it is caught.
    """
    from lpcstudy.oracle import inverse_dimension, local_dimension

    reference, queries, _ = _uniform_known_dimension(m)
    _assert_interior(reference, queries)
    estimates = inverse_dimension(local_dimension(reference, queries))
    assert estimates.shape == (2_000,)
    assert abs(estimates.mean() * m - 1) <= 0.03


def test_inverse_dimension_equals_brute_force_log_ratio_mean() -> None:
    """``inverse_dimension(local_dimension(...))`` is ``(1/(k-1)) sum_{j<k} ln(T_k/T_j)``.

    Reference: an independent algorithm. The neighbor distances come from ``scipy.spatial``'s
    ``cdist`` (all pairs) and a full sort, not from the k-d tree of ``local_dimension``; the
    mean of the k - 1 log ratios is formed directly. 500 reference points and 50 queries, both
    standard normal in R^3 (fixed ``default_rng(30013)``), in general position (no ties, queries
    not in the reference), k = 20. Also asserted: ``inverse_dimension.__defaults__`` equals
    ``local_dimension.__defaults__`` (both ``(20,)``), so the two functions use the same k.

    Tolerance: relative 1e-12. The code takes 19 logs, a sum, a division by the local dimension
    ``(k - 2) / S`` and the reverse ``(k - 2) / ((k - 1) local_dim)``; each step is a few ulp
    (2.2e-16), about 40 operations in all. The worst deviation between the k-d tree and the
    brute-force distances is 3.3e-16 relative (applied-mathematician, 50 cases), so 1e-12 is
    about 3000 times the round-off.
    """
    from scipy.spatial.distance import cdist

    from lpcstudy.oracle import inverse_dimension, local_dimension

    assert inverse_dimension.__defaults__ == local_dimension.__defaults__ == (20,)
    rng = np.random.default_rng(30013)
    reference = rng.standard_normal((500, 3))
    queries = rng.standard_normal((50, 3))
    k = 20
    sorted_dist = np.sort(cdist(queries, reference), axis=1)[:, :k]
    expected = np.mean(np.log(sorted_dist[:, k - 1:k] / sorted_dist[:, :k - 1]), axis=1)
    got = inverse_dimension(local_dimension(reference, queries))
    assert got.shape == expected.shape
    assert np.allclose(got, expected, rtol=1e-12, atol=0.0)


def test_inverse_dimension_rejects_too_few_neighbors_and_keeps_nonfinite() -> None:
    """``k < 3`` raises; a non-finite local dimension stays non-finite (never replaced).

    Reference: the formula ``(k - 2) / ((k - 1) d)``. With k = 2 the estimator ``(k - 2) / S``
    is identically zero (no information), and ``k < 2`` has no log ratio, so both raise
    (PRIME.4). For ``d = (nan, inf, 2)`` at k = 20 the values are ``nan``, ``0`` (the
    limit, an infinite dimension) and ``18 / (19 * 2)``; the caller (H1a) decides what to
    exclude. Tolerance: relative 1e-15 on the one finite nonzero value (a division and a product).
    """
    from lpcstudy.oracle import inverse_dimension

    with pytest.raises(ValueError, match="n_neighbors"):
        inverse_dimension(np.array([2.0]), n_neighbors=2)
    out = inverse_dimension(np.array([np.nan, np.inf, 2.0]))
    assert np.isnan(out[0]) and out[1] == 0.0
    assert out[2] == pytest.approx(18.0 / (19.0 * 2.0), rel=1e-15, abs=0.0)


# ---------------------------------------------------------------- WU-0002.11a: counters (DEF-0001)
def _old_local_dimension(reference: np.ndarray, queries: np.ndarray, k: int = 20) -> np.ndarray:
    """``local_dimension`` before WU-0002.11a, verbatim (bitwise reference)."""
    from scipy.spatial import cKDTree

    dist, _ = cKDTree(reference).query(queries, k=k, workers=-1)
    dist = np.maximum(dist, 1e-300)
    logs = np.log(dist[:, -1:] / dist[:, :-1])
    return (k - 2) / np.sum(logs, axis=1)


def test_local_dimension_counts_zero_distance_a7() -> None:
    """A7: a query that duplicates a reference point is counted once; the dimensions are unchanged.

    Reference: a hand construction. 300 standard-normal reference points in R^3 from
    ``np.random.default_rng(1107)``; queries: 5 fresh normal points (no duplicate: the nearest
    distance of a continuous draw is positive) and query 5 equal to reference point 17 (distance 0,
    below the 1e-300 floor). Expected ``local_dim_zero_distance`` flags: only query 5 (sum 1).
    The dimensions equal the pre-change function (copied above) bitwise, for both entry points:
    the floor of 1e-300 is applied identically.
    """
    from lpcstudy.oracle import local_dimension, local_dimension_counted

    rng = np.random.default_rng(1107)
    reference = rng.standard_normal((300, 3))
    queries = np.vstack([rng.standard_normal((5, 3)), reference[17:18]])
    dims, floored = local_dimension_counted(reference, queries)
    assert floored.tolist() == [False] * 5 + [True] and int(floored.sum()) == 1
    ref = _old_local_dimension(reference, queries)
    assert dims.tobytes() == ref.tobytes()
    assert local_dimension(reference, queries).tobytes() == ref.tobytes()
    assert np.isfinite(dims[5]) and dims[5] < dims[:5].min()  # the floored state: tiny dimension


def test_oracle_handling_a8_oracle_path_replaces_nothing() -> None:
    """A8 (oracle path): NaN, +inf and 0.0 in the window are counted per state and never replaced.

    Reference: hand arrays, window 4, 6 states. State 0: a NaN gain. State 1: a +inf gain. State
    2: a 0.0 gain in the window (a floor). State 3: all finite. First three rows alone:
    ``oracle_nonfinite == 2`` and ``oracle_gain_floor == 1`` (the plan's A8). State 4 (D5): NaN and
    +inf in one row counts once, making ``oracle_nonfinite == 3``. State 5: ``nu`` = NaN with
    finite gains (counts in ``oracle_nonfinite``). ``growth_exponent`` (unchanged code) keeps the
    NaN: the oracle gains are not replaced, so ``growth`` equals the old expression bitwise.
    The zero-distance flags are passed through to column 0. Exact.
    """
    from lpcstudy.dynamics import growth_exponent
    from lpcstudy.oracle import ORACLE_COUNTERS, oracle_handling

    assert ORACLE_COUNTERS == ("local_dim_zero_distance", "oracle_gain_floor",
                               "oracle_nonfinite")
    gains = np.full((6, 4), 3.0)
    gains[0, 1] = np.nan
    gains[1, 2] = np.inf
    gains[2, 0] = 0.0
    gains[4, 0], gains[4, 3] = np.nan, np.inf
    nu = np.ones(6)
    nu[5] = np.nan
    zero_distance = np.array([False, False, False, True, False, False])
    first = oracle_handling(nu[:3], gains[:3], 4, zero_distance[:3])
    assert first[:, 2].sum() == 2 and first[:, 1].sum() == 1 and first[:, 0].sum() == 0
    flags = oracle_handling(nu, gains, 4, zero_distance)
    assert flags.dtype == np.int64 and flags.shape == (6, 3)
    assert flags[:, 0].tolist() == [0, 0, 0, 1, 0, 0]
    assert flags[:, 1].tolist() == [0, 0, 1, 0, 0, 0]
    assert flags[:, 2].tolist() == [1, 1, 0, 0, 1, 1] and flags[:, 2].sum() == 4
    with np.errstate(invalid="ignore"):  # the inf - inf of the unreplaced row is the point
        old = growth_exponent(gains, 4)
    assert np.isnan(old[0]) and np.isnan(old[4])  # nothing replaced: NaN propagates


def test_state_oracles_attaches_handled_and_keeps_values(monkeypatch) -> None:
    """``state_oracles`` returns ``handled`` per state and the same ``nu``, ``gains``, ``growth``.

    Reference: hand-planned stubs. The flow map, observability and amplification functions are
    replaced by stubs returning planned arrays (``nu`` with one NaN, gains with one 0.0 in the
    window); the library of 50 random states contains state 7 exactly, and the evaluation state at
    time 12 is that state (a zero neighbour distance). Expected flags (columns local_dim_zero_
    distance, oracle_gain_floor, oracle_nonfinite) for the 3 states at times (10, 12, 14): zero
    distance only for time 12, gain floor for the state at time 14, non-finite for the state at
    time 10. ``growth`` equals ``growth_exponent`` of the planned gains bitwise, and ``subset``
    carries the rows. Exact.
    """
    from types import SimpleNamespace

    from lpcstudy import oracle, systems
    from lpcstudy.dynamics import growth_exponent

    rng = np.random.default_rng(1108)
    library = rng.standard_normal((50, 2))
    eval_states = rng.standard_normal((30, 2))
    eval_states[12] = library[7]
    gains = np.full((3, 4), 2.0)
    gains[2, 1] = 0.0
    nu = np.array([np.nan, 1.0, 2.0])
    ctx = SimpleNamespace(spec=SimpleNamespace(params={}, observed_index=0), interval=0.1,
                          obs_scale=1.0, whiten=np.eye(2), unwhiten=np.eye(2), delay=1,
                          embed_dim=3, history=2, library_states=library, eval_states=eval_states,
                          split_indices={"test": np.array([10, 12, 14])},
                          whiten_states=lambda x: x)
    monkeypatch.setattr(systems, "make_flow_step", lambda *a, **k: None)
    monkeypatch.setattr(oracle, "make_observability", lambda *a, **k: (lambda s: nu))
    monkeypatch.setattr(oracle, "make_amplification", lambda *a, **k: (lambda s: gains))
    out = oracle.state_oracles(ctx, "test", 4)
    np.testing.assert_array_equal(out.handled, [[0, 0, 1], [1, 0, 0], [0, 1, 0]])
    assert out.growth.tobytes() == growth_exponent(gains, 4).tobytes()
    assert out.gains.tobytes() == gains.tobytes() and out.nu.tobytes() == nu.tobytes()
    np.testing.assert_array_equal(out.subset(np.array([2, 0])).handled, [[0, 1, 0], [0, 0, 1]])
