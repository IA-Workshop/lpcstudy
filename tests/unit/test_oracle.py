"""Tests for ``lpcstudy.oracle``: the optimal blend weight and its helpers.

The oracle module computes the best weight ``w*`` for blending the analog
forecaster (CP) with the physics-based forecaster (PLP), the error of any
weight, the first time a forecast error exceeds a tolerance, and the local
dimension of the attractor. These tests check each piece against a reference
that does not use the code under test: brute-force searches on a grid, exact
algebra, hand-worked examples, and the exact probability law of the
local-dimension estimator.
"""

from __future__ import annotations

import numpy as np
import pytest
from unit_helpers import (
    _moments_from_draws,
    moments_from_triples,
    realizable_triples,
)

from lpcstudy.oracle import (
    characteristic_horizon,
    curvature,
    excess_mse,
    hybrid_mse,
    local_dimension_counted,
    oracle_weight,
)


def _direct_v(
    weight: np.ndarray,
    e_c: np.ndarray,
    e_p: np.ndarray,
    cross: np.ndarray,
) -> np.ndarray:
    """Evaluate V(w) = w^2 E_C + (1 - w)^2 E_P + 2 w (1 - w) C directly.

    This is written out here, so it is independent of the code under test.
    """
    return (
        weight**2 * e_c
        + (1 - weight) ** 2 * e_p
        + 2 * weight * (1 - weight) * cross
    )


def test_oracle_weight_minimizes_ensemble_mse() -> None:
    """The weight w* equals a brute-force minimizer of the ensemble MSE.

    Reference: brute force. The average of (w e_C + (1 - w) e_P)^2 over the
    raw draws is computed on a grid of 2001 points in [0, 1], and the best
    grid point is taken. This uses the draws directly, not ``hybrid_mse`` or
    the moments inside ``oracle_weight``. The moments passed to
    ``oracle_weight`` come from a test helper (plain sample means), not from
    ``lpcstudy.ensemble``. There are 5 states, 3 horizons and 400 draws each.

    Tolerance: ``atol=1e-3`` (plus the default rtol 1e-5). The mean square is
    a convex quadratic in w, so the best grid point is the one nearest the
    (clipped) exact minimizer, which is off by at most half the grid spacing,
    2.5e-4 (the spacing is 5e-4), plus round-off. The bound 1e-3 is 4 times
    that.
    """
    rng = np.random.default_rng(0)
    common = rng.standard_normal((5, 400, 3))
    cp = 0.5 * common + rng.standard_normal((5, 400, 3))
    plp = 0.3 * common + 0.7 * rng.standard_normal((5, 400, 3))
    moments = _moments_from_draws(cp, plp)
    grid = np.linspace(0, 1, 2001)
    brute = np.array(
        [
            [
                grid[
                    np.argmin(
                        [
                            np.mean(
                                (w * cp[i, :, h] + (1 - w) * plp[i, :, h]) ** 2
                            )
                            for w in grid
                        ]
                    )
                ]
                for h in range(3)
            ]
            for i in range(5)
        ]
    )
    assert np.allclose(oracle_weight(moments), brute, atol=1e-3)


def test_oracle_weight_clips_to_boundary() -> None:
    """When the best unconstrained weight is outside [0, 1], w* is 0 or 1.

    Reference: brute force on the raw draws over the grid of 2001 points in
    [0, 1], as in ``test_oracle_weight_minimizes_ensemble_mse``.

    Manufactured inputs: with e_P = 0.3 c and e_C = c + 0.3 u (c and u
    independent standard normal), w* = E[e_P (e_P - e_C)] / E[(e_C - e_P)^2]
    is about -0.21 / 0.58 = -0.36 < 0, so the constrained minimizer is 0.
    With the roles swapped, w* is about 1.36 > 1, so it is 1. The test first
    asserts this premise (the unclipped value is outside [0, 1]). The margin
    is wide: the standard error of the sample w* at 400 draws is about 0.008,
    a Monte Carlo estimate, against a distance of 0.36 to the boundary. It
    then asserts that ``oracle_weight`` equals the grid minimizer.

    Tolerance: exact equality. A convex quadratic whose vertex lies outside
    [0, 1] has its grid minimum at the end point 0.0 or 1.0 (both exactly
    representable and exact in ``np.linspace``), and ``np.clip`` returns those
    values exactly.
    """
    rng = np.random.default_rng(10)
    common = rng.standard_normal((4, 400, 3))
    noise = 0.3 * rng.standard_normal((4, 400, 3))
    grid = np.linspace(0, 1, 2001)

    def brute_force(cp: np.ndarray, plp: np.ndarray) -> np.ndarray:
        return np.array(
            [
                [
                    grid[
                        np.argmin(
                            [
                                np.mean(
                                    (w * cp[i, :, h] + (1 - w) * plp[i, :, h])
                                    ** 2
                                )
                                for w in grid
                            ]
                        )
                    ]
                    for h in range(3)
                ]
                for i in range(4)
            ]
        )

    for cp, plp, expected in (
        (common + noise, 0.3 * common, 0.0),
        (0.3 * common, common + noise, 1.0),
    ):
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
    """V(w) - V(w*) = c (w - w*)^2 when w* is not clipped (FW Prop. 5).

    Here V(w) is the expected squared error of weight w, and the difference
    is the "regret" of using w instead of the best weight.

    Reference: the exact quadratic identity of FW Prop. 5. All three operands
    (``hybrid_mse``, ``oracle_weight`` and ``curvature``) are code under test,
    so this checks only that they agree with each other: the quadratic in
    ``hybrid_mse`` must have its lowest point at ``oracle_weight`` and its
    curvature equal to ``curvature`` (a sign or factor error in any one
    fails). The next test, ``test_regret_identity_matches_draws``, ties the
    result to the raw draws.

    Tolerance: ``np.allclose`` defaults (rtol 1e-5, atol 1e-8). The identity
    is exact algebra on the sample moments, so the difference is round-off
    (about 1e-16 on values of order one, below 1e-14 after subtraction).
    """
    rng = np.random.default_rng(1)
    cp = rng.standard_normal((4, 300, 2))
    plp = 0.8 * rng.standard_normal((4, 300, 2))
    moments = _moments_from_draws(cp, plp)
    w_star = oracle_weight(moments, clip=False)
    w = np.full_like(w_star, 0.3)
    lhs = hybrid_mse(moments, w) - hybrid_mse(moments, w_star)
    assert np.allclose(lhs, curvature(moments) * (w - w_star) ** 2)


def test_regret_identity_matches_draws() -> None:
    """The regret identity holds when V is computed directly from the draws.

    Reference: V(w) is the mean over the 300 draws of (w e_C + (1 - w) e_P)^2,
    computed from the raw draws with no use of ``hybrid_mse`` or the moments
    (FW Prop. 5). This ties ``hybrid_mse`` to data. (i) ``hybrid_mse(w)``
    equals V(w) from the draws at w = 0.3 and at the unclipped w*. (ii)
    V(0.3) - V(w*) equals c (0.3 - w*)^2, with c the ``curvature``.

    Tolerance: ``atol=1e-12``, ``rtol=0``. V is a mean of 300 products of
    numbers of order one, so each side has a worst-case round-off of about
    300 * 1.1e-16 * 2 = 7e-14 (observed errors are far smaller). The
    differences cancel terms of order one, and 1e-12 leaves a factor of 15
    over the worst case.
    """
    rng = np.random.default_rng(1)
    cp = rng.standard_normal((4, 300, 2))
    plp = 0.8 * rng.standard_normal((4, 300, 2))
    moments = _moments_from_draws(cp, plp)
    w_star = oracle_weight(moments, clip=False)
    w = np.full_like(w_star, 0.3)

    def from_draws(weight: np.ndarray) -> np.ndarray:
        blend = weight[:, None, :] * cp + (1 - weight[:, None, :]) * plp
        return np.mean(blend**2, axis=1)

    np.testing.assert_allclose(
        hybrid_mse(moments, w), from_draws(w), rtol=0.0, atol=1e-12
    )
    np.testing.assert_allclose(
        hybrid_mse(moments, w_star), from_draws(w_star), rtol=0.0, atol=1e-12
    )
    np.testing.assert_allclose(
        from_draws(w) - from_draws(w_star),
        curvature(moments) * (w - w_star) ** 2,
        rtol=0.0,
        atol=1e-12,
    )


def test_excess_mse_matches_grid_minimum() -> None:
    """``excess_mse`` equals V(w) minus the brute-force minimum of V on [0, 1].

    This is Theorem P1(a). The "excess" is how much worse a weight is than
    the best weight in [0, 1].

    Reference: brute force. V(w) = w^2 E_C + (1-w)^2 E_P + 2w(1-w) C is
    evaluated directly from the moment triple on ``np.linspace(0, 1, 10_000)``
    (spacing h = 1/9999; both end points are exact), and the reference excess
    is V(w) minus the minimum over the grid.

    Inputs: 200 manufactured realizable triples (70 with u in (-5, 0), 60 in
    [0, 1], 70 in (1, 6); c log-uniform on [1e-3, 10]); the reference sees
    only (E_C, E_P, C). The weight w is uniform on [0, 1] with
    |w - w*| >= 0.1 (by rejection, fixed seed). The end points w = 0 and
    w = 1 are also tested whenever |w - w*| >= 0.1 (the end point is kept only
    under that guard) or w equals w* (then the excess and the reference are
    both exactly 0).

    Tolerance: ``rtol=1e-6``, ``atol=0``. The grid minimum exceeds V(w*) by
    at most c (h/2)^2 = 2.5005e-9 c, and the excess is at least
    c (w - w*)^2 >= 0.01 c (also when u is clipped, because
    (w - w*)(w + w* - 2u) >= (w - w*)^2). So the relative bias is at most
    2.5e-7, four times below 1e-6. Round-off is about 1e-12 relative (V is at
    most 46 c on these ranges, over an excess of at least 0.01 c).
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
        ref_end = (
            _direct_v(w_end[:, 0], e_c[:, 0], e_p[:, 0], cross[:, 0]) - v_min
        )
        np.testing.assert_allclose(
            got_end[keep], ref_end[keep], rtol=1e-6, atol=0.0
        )
        assert same.sum() > 0
        assert np.all(got_end[same] == 0.0) and np.all(ref_end[same] == 0.0)
    # The guard was exercised: some end points were excluded.
    assert used > 150 and excluded > 0


def test_excess_mse_is_nonnegative_and_zero_at_optimum() -> None:
    """The excess is never negative and is exactly 0.0 at w*.

    It is also not negative at one to five floating-point steps (ulps) from
    w*, where a different algebraic form of the formula would fail.

    Reference: exact algebra (P1(a)). V(w) - V(w*) = c [(w - u)^2 - (w* - u)^2]
    is at least 0, with equality at w = w*. In floating-point arithmetic the
    form used is at least 0 exactly (rounding is monotone and
    |w - u| >= |w* - u|), and exactly 0.0 at w* computed from the same u. The
    factored form fails the sign within 5 ulps of w* (measured by the
    mathematician).

    Inputs: the 200 triples of ``test_excess_mse_matches_grid_minimum`` (same
    seed), w on a 21-point grid of [0, 1], at w*, and at ``np.nextafter`` of
    w* in both directions up to 5 steps (clipped to [0, 1]).

    Tolerance: none (exact comparisons).
    """
    rng = np.random.default_rng(20261011)
    t = realizable_triples(rng, 70, 60, 70)
    moments = moments_from_triples(
        t["E_C"][:, None], t["E_P"][:, None], t["C"][:, None]
    )
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
    """When u > 1, c (w - w*)^2 underestimates the excess; ``excess_mse`` not.

    This is the case behind DEF-0002.

    Reference: direct evaluation of the quadratic. E_C = 1, E_P = 4 and
    C = 1.5 (realizable, because E_C E_P - C^2 = 1.75 >= 0) give c = 2,
    b = E_P - C = 2.5, u = 1.25 and w* = 1. With w = 0.5, V(0.5) =
    0.25 + 1 + 0.75 = 2.0 and V(1) = 1.0, so the excess is 1.0, against
    c (w - w*)^2 = 0.5.

    Tolerance: exact ``==``. Every operand and intermediate value is dyadic
    (0.5625, 0.0625, 2.0), so no rounding occurs.
    """
    moments = moments_from_triples(
        np.array([[1.0]]), np.array([[4.0]]), np.array([[1.5]])
    )
    w = np.array([[0.5]])
    assert oracle_weight(moments, clip=False)[0, 0] == 1.25
    assert oracle_weight(moments)[0, 0] == 1.0
    got = excess_mse(moments, w)[0, 0]
    direct = _direct_v(0.5, 1.0, 4.0, 1.5) - _direct_v(1.0, 1.0, 4.0, 1.5)
    assert direct == 1.0
    assert got == 1.0
    assert curvature(moments)[0, 0] * (0.5 - 1.0) ** 2 == 0.5 < got


def test_excess_mse_unclipped_equals_curvature_form_and_broadcasts() -> None:
    """For u in [0, 1] the excess is c (w - u)^2, and 3-D weights broadcast.

    Reference: the FW Prop. 5 identity (the unclipped case of
    ``test_regret_identity``) with the curvature and u written out from the
    triple by hand: c = E_C + E_P - 2C and u = (E_P - C) / c. Also,
    ``excess_mse`` of a ``(n, E, nH)`` weight equals the 2-D result for each
    draw, exactly (the same elementwise operations), and a weight of the wrong
    shape raises.

    Tolerance: ``rtol=1e-12``. A few operations at about 1e-16 each, over an
    excess of at least 1e-3 c (w is at least 0.05 from u by construction).
    """
    rng = np.random.default_rng(5)
    t = realizable_triples(rng, 0, 30, 0, inside=(0.2, 0.8))
    e_c, e_p, cross = t["E_C"][:, None], t["E_P"][:, None], t["C"][:, None]
    moments = moments_from_triples(e_c, e_p, cross)
    c = e_c + e_p - 2 * cross
    u = (e_p - cross) / c
    w = np.where(u > 0.5, u - 0.1, u + 0.1)
    np.testing.assert_allclose(
        excess_mse(moments, w), c * (w - u) ** 2, rtol=1e-12, atol=0.0
    )
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
    """The horizon is the first crossing above theta; censored rows get H_max.

    The test uses sqrt(mse + rho^2) with rho = 0. A row that never crosses is
    "censored": we only know its horizon is at least H_max.

    Reference: hand computation. With rho = 0 and theta = 0.2, row 1 has
    sqrt(mse) = 0, 0.1, 0.224, 0.447, so the first value above 0.2 is at
    H = 3 (an event). Row 2 is identically 0, never crosses, and is censored
    at H_max = 4 (no event).

    Tolerance: none; exact equality of integers and booleans. The strict
    inequality is not at a boundary: 0.224 and 0.1 are away from theta = 0.2
    by 0.024 and 0.1.
    """
    mse = np.array([[0.0, 0.01, 0.05, 0.2], [0.0, 0.0, 0.0, 0.0]])
    horizon, event = characteristic_horizon(mse, np.arange(1, 5), 0.0, 0.2)
    assert horizon.tolist() == [3, 4] and event.tolist() == [True, False]


def test_characteristic_horizon_noise_in_quadrature() -> None:
    """Horizons use the noisy observation: rho adds in quadrature.

    Reference: hand computation on the same mse as the noise-free test, with
    rho = 0.19 and theta = 0.2. Row 1: sqrt(0 + 0.0361) = 0.19 <= 0.2, then
    sqrt(0.01 + 0.0361) = sqrt(0.0461) = 0.2147 > 0.2, so H = 2 (an event).
    Row 2 stays at 0.19 for every horizon and is censored at H_max = 4. The
    expected result is ([2, 4], [True, False]). Also, horizons that are not
    contiguous from 1 raise ``ValueError`` (PRIME.4).

    Tolerance: none; exact equality. The crossing is not at a boundary (0.19
    and 0.2147 are 0.01 and 0.015 from theta, far above round-off).
    """
    mse = np.array([[0.0, 0.01, 0.05, 0.2], [0.0, 0.0, 0.0, 0.0]])
    horizon, event = characteristic_horizon(mse, np.arange(1, 5), 0.19, 0.2)
    assert horizon.tolist() == [2, 4] and event.tolist() == [True, False]
    with pytest.raises(ValueError, match="horizons 1..H_max"):
        characteristic_horizon(mse, np.arange(2, 6), 0.0, 0.2)


def _uniform_known_dimension(
    m: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build a reference set, interior queries and a map for the cube [0, 1]^m.

    The set is ``c + U u`` with ``u`` uniform on ``[0, 1]^m``, ``U`` (7 x m)
    with orthonormal columns (the first factor of ``qr`` of a standard-normal
    matrix) and a fixed offset ``c`` in R^7. The map is an isometry (it
    preserves distances), so Euclidean neighbor distances in R^7 equal those
    in ``u``-space. The queries are 2000 fresh points uniform in the interior
    box ``[0.2, 0.8]^m``. The fixed seed 50053 is for test data only, not a
    study stream.
    """
    rng = np.random.default_rng(50053)
    basis = np.linalg.qr(rng.standard_normal((7, m)))[0]
    offset = rng.standard_normal(7)
    reference = offset + rng.uniform(size=(20_000, m)) @ basis.T
    queries = offset + rng.uniform(0.2, 0.8, size=(2_000, m)) @ basis.T
    assert np.allclose(basis.T @ basis, np.eye(m), atol=1e-14)
    return reference, queries, basis


def _assert_interior(reference: np.ndarray, queries: np.ndarray) -> None:
    """Check the premise: each query's 20-neighbor ball lies inside the cube.

    That is, the radius is below 0.2, the distance from the query box to the
    edge of the cube.
    """
    from scipy.spatial import cKDTree

    radius = cKDTree(reference).query(queries, k=20)[0][:, -1]
    assert radius.max() < 0.2


@pytest.mark.parametrize("m", [1, 2, 3])
def test_local_dimension_known_sets(m: int) -> None:
    """The Levina-Bickel estimate is unbiased on uniform sets of dimension m.

    The sets are a segment, a unit square and a unit cube (dimension 1, 2, 3)
    embedded in R^7.

    Reference: the exact law of the estimator, independent of the code. Each
    set has n = 2e4 points, k = 20 neighbors (the study's setting;
    ``local_dimension_counted.__defaults__ == (20,)`` is asserted) and 2000
    queries uniform in the interior box [0.2, 0.8]^m, not in the reference.
    Given T_k (the distance to the k-th neighbor), the k - 1 inner neighbors
    are independent and uniform in the ball, and every ball lies inside the
    set (asserted: T_20 < 0.2; its maximum is about 0.078 for the cube). So
    S = sum_j log(T_k / T_j) follows Gamma(k - 1, rate m) exactly for any n.
    The per-query estimate (k - 2) / S is the "divide by k - 2" variant of
    Levina and Bickel (2005), NIPS 17, Sec. 3.1, with mean m and standard
    deviation m / sqrt(k - 3) = 0.2425 m.

    The statistic is the arithmetic mean of the per-query estimates, which is
    the published aggregator (Levina and Bickel 2005, eq. 9). The median is
    not the published aggregator; its value is pinned against the Gamma law
    in ``test_local_dimension_median_poisson_value``.

    Boundary queries are excluded on purpose. Their balls are cut off by the
    edge of the set, which biases the estimator down (for the cube, 32% of
    points have T_20 reaching the edge; the bias is -2.2% on the mean and
    -5.6% on the median at m = 3). That is a property of the estimator, not a
    check of the code, and its reference value would have to come from
    simulation, not from an independent law.

    Tolerance: ``abs(mean / m - 1) <= 0.03``, tightened from the roadmap's
    10% (applied-mathematician, WU-0005 log). The mean of 2000 estimates with
    standard deviation 0.2425 m has standard deviation 0.0054 m if they are
    independent. In 200 simulated seeds the standard deviation of mean / m was
    0.0054, 0.0057 and 0.0057 for m = 1, 2, 3 (neighbors shared between
    queries inflate it by at most 1.06), and the average of mean / m was
    0.9997, 0.9999 and 1.0007 (no bias). A bound of 3% is 5.3 standard
    deviations, so a false alarm over the three values of m has probability
    about 1e-6. A tolerance of 10% would not detect a wrong normalization:
    dividing by k - 1 instead of k - 2 multiplies every estimate by 19/18
    (+5.56%), which is 2.56% beyond the 3% bound (4.5 standard deviations),
    so a miss has probability below 1e-5.
    """
    assert local_dimension_counted.__defaults__ == (20,)
    reference, queries, _ = _uniform_known_dimension(m)
    _assert_interior(reference, queries)
    estimates = local_dimension_counted(reference, queries)[0]
    assert estimates.shape == (2_000,)
    assert abs(estimates.mean() / m - 1) <= 0.03


@pytest.mark.parametrize("m", [1, 2, 3])
def test_local_dimension_median_poisson_value(m: int) -> None:
    """The median of the per-query estimates sits at 0.964 m, below the mean.

    The test computes ``np.median`` itself and compares the median of the
    per-query estimates with the exact Gamma law; it does not exercise any
    caller's aggregation. The published aggregator is the arithmetic mean
    (Levina and Bickel 2005, eq. 9; no median appears there). The per-query
    estimate (k - 2) / S has S ~ Gamma(19, rate m), so its median is
    18 m / median(Gamma(19, 1)) = 0.9642 m. That is 3.6% below the mean m,
    because the distribution is skewed.

    Reference: the exact Gamma law, with the constant computed as
    ``18 / scipy.stats.gamma(19).median()`` (independent of the code). The
    data, queries and premises are those of
    ``test_local_dimension_known_sets``.

    Tolerance: ``abs(median / (c m) - 1) <= 0.03`` with c = 0.9642. Over 200
    simulated seeds the median / m averaged 0.9641, 0.9643 and 0.9653 for
    m = 1, 2, 3, with standard deviation 0.006 to 0.0066
    (applied-mathematician, WU-0005 log). That is a relative standard
    deviation of at most 0.0068 about c m, and 3% is 4.4 standard deviations
    (a false alarm of about 1e-5 per m). This test alone does not separate the
    median from the mean: an estimate centered at m would be +3.7% from c m,
    only 1 standard deviation beyond the bound. It pins the value of the
    median (and so a gross change of the per-query law), while the mean test,
    with its 3% bound about m, fixes the normalization.
    """
    from scipy.stats import gamma

    reference, queries, _ = _uniform_known_dimension(m)
    _assert_interior(reference, queries)
    constant = 18.0 / gamma(19).median()
    assert constant == pytest.approx(0.9642, abs=5e-5)
    median = float(np.median(local_dimension_counted(reference, queries)[0]))
    assert abs(median / (constant * m) - 1) <= 0.03


@pytest.mark.parametrize("m", [1, 2, 3])
def test_inverse_dimension_is_unbiased_on_known_sets(m: int) -> None:
    """The reference S / (k - 1) has mean 1 / m on sets of dimension m.

    Reference: the exact Gamma law, independent of the code
    (applied-mathematician, WU-0002.4-5 log, Job 1 item 2). The sets, queries
    and premises are those of ``test_local_dimension_known_sets`` (segment,
    square, cube in R^7; k = 20; interior queries with T_20 < 0.2, asserted).
    The k - 1 inner neighbors of a query are independent and uniform in the
    ball given T_k, so S = sum_j ln(T_k / T_j) satisfies S m ~ Gamma(k - 1, 1)
    exactly, and E[S / (k - 1)] = 1 / m exactly. Inverting the k - 2 estimate
    of ``local_dimension_counted`` without the correction
    (1 / local_dim = S / (k - 2)) would be too high by
    (k - 1) / (k - 2) - 1 = +5.56%.

    Tolerance: ``abs(mean * m - 1) <= 0.03`` (the tolerance of the
    local-dimension mean test). The per-query relative standard deviation is
    1 / sqrt(k - 1) = 0.229, so the mean of 2000 queries has standard
    deviation 0.0054 (neighbors shared between queries inflate it by at most
    1.06 in 900 simulated cases, applied-mathematician). A bound of 3% is 5.5
    standard deviations (a false alarm over the three m has probability about
    1e-7). The k - 2 slip sits at +5.56%, 4.7 standard deviations beyond the
    bound, so it is caught.
    """
    from lpcstudy.oracle import inverse_dimension

    reference, queries, _ = _uniform_known_dimension(m)
    _assert_interior(reference, queries)
    estimates = inverse_dimension(
        local_dimension_counted(reference, queries)[0]
    )
    assert estimates.shape == (2_000,)
    assert abs(estimates.mean() * m - 1) <= 0.03


def test_inverse_dimension_equals_brute_force_log_ratio_mean() -> None:
    """The inverse dimension is (1/(k-1)) sum_{j<k} ln(T_k/T_j).

    Reference: an independent algorithm. The neighbor distances come from
    ``scipy.spatial``'s ``cdist`` (all pairs) and a full sort, not from the
    k-d tree used by ``local_dimension_counted``; the mean of the k - 1 log
    ratios is formed directly. There are 500 reference points and 50 queries,
    both standard normal in R^3 (fixed ``default_rng(30013)``), in general
    position (no ties, queries not in the reference), with k = 20. Also
    asserted: ``inverse_dimension.__defaults__`` equals
    ``local_dimension_counted.__defaults__`` (both ``(20,)``), so the two
    functions use the same k.

    Tolerance: relative 1e-12. The code takes 19 logs, a sum, a division by
    the local dimension (k - 2) / S and the reverse
    (k - 2) / ((k - 1) local_dim); each step is a few ulp (2.2e-16), about 40
    operations in all. The worst deviation between the k-d tree and the
    brute-force distances is 3.3e-16 relative (applied-mathematician, 50
    cases), so 1e-12 is about 3000 times the round-off.
    """
    from scipy.spatial.distance import cdist

    from lpcstudy.oracle import inverse_dimension

    assert (
        inverse_dimension.__defaults__
        == local_dimension_counted.__defaults__
        == (20,)
    )
    rng = np.random.default_rng(30013)
    reference = rng.standard_normal((500, 3))
    queries = rng.standard_normal((50, 3))
    k = 20
    sorted_dist = np.sort(cdist(queries, reference), axis=1)[:, :k]
    expected = np.mean(
        np.log(sorted_dist[:, k - 1 : k] / sorted_dist[:, : k - 1]), axis=1
    )
    got = inverse_dimension(local_dimension_counted(reference, queries)[0])
    assert got.shape == expected.shape
    assert np.allclose(got, expected, rtol=1e-12, atol=0.0)


def test_inverse_dimension_rejects_too_few_neighbors_and_keeps_nonfinite() -> (
    None
):
    """k < 3 raises; a non-finite local dimension stays non-finite.

    Nothing is replaced silently.

    Reference: the formula (k - 2) / ((k - 1) d). With k = 2 the estimator
    (k - 2) / S is identically zero (no information), and k < 2 has no log
    ratio, so both raise (PRIME.4). For d = (nan, inf, 2) at k = 20 the values
    are nan, 0 (the limit, an infinite dimension) and 18 / (19 * 2); the
    caller (H1a) decides what to exclude.

    Tolerance: relative 1e-15 on the one finite nonzero value (a division and
    a product).
    """
    from lpcstudy.oracle import inverse_dimension

    with pytest.raises(ValueError, match="n_neighbors"):
        inverse_dimension(np.array([2.0]), n_neighbors=2)
    out = inverse_dimension(np.array([np.nan, np.inf, 2.0]))
    assert np.isnan(out[0]) and out[1] == 0.0
    assert out[2] == pytest.approx(18.0 / (19.0 * 2.0), rel=1e-15, abs=0.0)


# ------------------------------- WU-0002.11a: counters (DEF-0001)
def _old_local_dimension(
    reference: np.ndarray, queries: np.ndarray, k: int = 20
) -> np.ndarray:
    """Return the local dimension as computed before WU-0002.11a, verbatim.

    This is the bitwise reference for the counted version.
    """
    from scipy.spatial import cKDTree

    dist, _ = cKDTree(reference).query(queries, k=k, workers=-1)
    dist = np.maximum(dist, 1e-300)
    logs = np.log(dist[:, -1:] / dist[:, :-1])
    return (k - 2) / np.sum(logs, axis=1)


def test_local_dimension_counts_zero_distance_a7() -> None:
    """A7: a query equal to a reference point is counted once.

    The dimensions are unchanged by the counting.

    Reference: a hand construction. There are 300 standard-normal reference
    points in R^3 from ``np.random.default_rng(1107)``. The queries are 5 fresh
    normal points (no duplicate: the nearest distance of a continuous draw is
    positive) and query 5, equal to reference point 17 (distance 0, below the
    1e-300 floor). The expected ``local_dim_zero_distance`` flags are set only
    for query 5 (sum 1). The dimensions equal those of the pre-change
    function (copied above) bitwise, because the floor of 1e-300 is applied
    identically.
    """
    rng = np.random.default_rng(1107)
    reference = rng.standard_normal((300, 3))
    queries = np.vstack([rng.standard_normal((5, 3)), reference[17:18]])
    dims, floored = local_dimension_counted(reference, queries)
    assert floored.tolist() == [False] * 5 + [True] and int(floored.sum()) == 1
    ref = _old_local_dimension(reference, queries)
    assert dims.tobytes() == ref.tobytes()
    # The floored state has a tiny dimension.
    assert np.isfinite(dims[5]) and dims[5] < dims[:5].min()


def test_oracle_handling_a8_oracle_path_replaces_nothing() -> None:
    """A8 (oracle path): NaN, +inf and 0.0 are counted, never replaced.

    Reference: hand arrays with window 4 and 6 states. State 0 has a NaN
    gain. State 1 has a +inf gain. State 2 has a 0.0 gain in the window (a
    floor). State 3 is all finite. For the first three rows alone,
    ``oracle_nonfinite == 2`` and ``oracle_gain_floor == 1`` (the plan's A8).
    State 4 (D5) has NaN and +inf in one row, which counts once, making
    ``oracle_nonfinite == 3``. State 5 has ``nu`` = NaN with finite gains
    (this counts in ``oracle_nonfinite``). ``growth_exponent`` (unchanged
    code) keeps the NaN: the oracle gains are not replaced, so ``growth``
    equals the old expression bitwise. The zero-distance flags are passed
    through to column 0. All comparisons are exact.
    """
    from lpcstudy.dynamics import growth_exponent
    from lpcstudy.oracle import ORACLE_COUNTERS, oracle_handling

    assert ORACLE_COUNTERS == (
        "local_dim_zero_distance",
        "oracle_gain_floor",
        "oracle_nonfinite",
    )
    gains = np.full((6, 4), 3.0)
    gains[0, 1] = np.nan
    gains[1, 2] = np.inf
    gains[2, 0] = 0.0
    gains[4, 0], gains[4, 3] = np.nan, np.inf
    nu = np.ones(6)
    nu[5] = np.nan
    zero_distance = np.array([False, False, False, True, False, False])
    first = oracle_handling(nu[:3], gains[:3], 4, zero_distance[:3])
    assert (
        first[:, 2].sum() == 2
        and first[:, 1].sum() == 1
        and first[:, 0].sum() == 0
    )
    flags = oracle_handling(nu, gains, 4, zero_distance)
    assert flags.dtype == np.int64 and flags.shape == (6, 3)
    assert flags[:, 0].tolist() == [0, 0, 0, 1, 0, 0]
    assert flags[:, 1].tolist() == [0, 0, 1, 0, 0, 0]
    assert flags[:, 2].tolist() == [1, 1, 0, 0, 1, 1] and flags[:, 2].sum() == 4
    # The inf - inf of the unreplaced row is the point of the test.
    with np.errstate(invalid="ignore"):
        old = growth_exponent(gains, 4)
    # Nothing was replaced, so NaN propagates.
    assert np.isnan(old[0]) and np.isnan(old[4])


def test_state_oracles_attaches_handled_and_keeps_values(monkeypatch) -> None:
    """``state_oracles`` returns ``handled`` and leaves the other values alone.

    The values that must not change are ``nu``, ``gains`` and ``growth``.

    Reference: hand-planned stubs. The flow map, observability and
    amplification functions are replaced by stubs that return planned arrays
    (``nu`` with one NaN, gains with one 0.0 in the window). The library of 50
    random states contains state 7 exactly, and the evaluation state at time
    12 is that state (a zero neighbor distance). The expected flags (columns
    local_dim_zero_distance, oracle_gain_floor, oracle_nonfinite) for the 3
    states at times (10, 12, 14) are: zero distance only for time 12, gain
    floor for the state at time 14, and non-finite for the state at time 10.
    ``growth`` equals ``growth_exponent`` of the planned gains bitwise, and
    ``subset`` carries the rows. All comparisons are exact.
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
    ctx = SimpleNamespace(
        spec=SimpleNamespace(name="lorenz63", params={}, observed_index=0),
        interval=0.1,
        obs_scale=1.0,
        whiten=np.eye(2),
        unwhiten=np.eye(2),
        delay=1,
        embed_dim=3,
        history=2,
        library_states=library,
        eval_states=eval_states,
        split_indices={"test": np.array([10, 12, 14])},
        whiten_states=lambda x: x,
    )
    monkeypatch.setattr(systems, "make_flow_step", lambda *a, **k: None)
    monkeypatch.setattr(
        oracle, "make_observability", lambda *a, **k: (lambda s: nu)
    )
    monkeypatch.setattr(
        oracle, "make_amplification", lambda *a, **k: (lambda s: gains)
    )
    out = oracle.state_oracles(ctx, "test", 4, 20261005)
    np.testing.assert_array_equal(
        out.handled, [[0, 0, 1], [1, 0, 0], [0, 1, 0]]
    )
    assert out.growth.tobytes() == growth_exponent(gains, 4).tobytes()
    assert (
        out.gains.tobytes() == gains.tobytes()
        and out.nu.tobytes() == nu.tobytes()
    )
    np.testing.assert_array_equal(
        out.subset(np.array([2, 0])).handled, [[0, 1, 0], [0, 0, 1]]
    )


class _SpyTree:
    """A real ``cKDTree`` that records the keyword arguments of ``query``."""

    def __init__(self, tree, calls: list) -> None:
        self.tree = tree
        self.calls = calls

    def query(self, *args, **kwargs):
        self.calls.append(dict(kwargs))
        return self.tree.query(*args, **kwargs)


def _spy_factory(calls: list):
    """Return a replacement for ``cKDTree`` that records its query calls."""
    from scipy.spatial import cKDTree

    return lambda reference: _SpyTree(cKDTree(reference), calls)


def _reference_and_queries() -> tuple[np.ndarray, np.ndarray]:
    """Return a fixed Gaussian reference (2000, 4) and 50 queries."""
    rng = np.random.default_rng(50121)
    return rng.standard_normal((2000, 4)), rng.standard_normal((50, 4))


@pytest.mark.parametrize("value, expected", [(None, 4), ("2", 2), ("8", 8)])
def test_local_dimension_passes_lpc_threads_as_workers(
    monkeypatch, value, expected: int
) -> None:
    """``local_dimension_counted`` queries with ``workers == LPC_THREADS``.

    This is DEF-0012. The ``workers`` setting is the number of threads the
    nearest-neighbor search may use.

    Reference: the expected integer is the environment value set by the test
    (4 when unset). The spy forwards to a real ``cKDTree``. The comparison is
    exact.
    """
    from lpcstudy import oracle

    calls: list = []
    monkeypatch.setattr(oracle, "cKDTree", _spy_factory(calls))
    if value is None:
        monkeypatch.delenv("LPC_THREADS", raising=False)
    else:
        monkeypatch.setenv("LPC_THREADS", value)
    reference, queries = _reference_and_queries()
    oracle.local_dimension_counted(reference, queries)
    assert len(calls) == 1 and calls[0]["workers"] == expected


@pytest.mark.parametrize("value", ["0", "-1", "abc"])
def test_local_dimension_rejects_invalid_lpc_threads(
    monkeypatch, value: str
) -> None:
    """An invalid ``LPC_THREADS`` raises ``ValueError`` and no query is made.

    This follows PRIME.4: bad input must fail loudly, not run with a guess.
    """
    from lpcstudy import oracle

    calls: list = []
    monkeypatch.setattr(oracle, "cKDTree", _spy_factory(calls))
    monkeypatch.setenv("LPC_THREADS", value)
    reference, queries = _reference_and_queries()
    with pytest.raises(ValueError, match="LPC_THREADS"):
        oracle.local_dimension_counted(reference, queries)
    assert calls == []


@pytest.mark.parametrize("threads", ["1", "4"])
def test_local_dimension_is_bitwise_independent_of_workers(
    monkeypatch, threads: str
) -> None:
    """The estimates and flags are bitwise those of a ``workers=1`` query.

    Reference: the Levina-Bickel formula written out here from
    ``cKDTree.query(workers=1)`` (the formula with k = 20 neighbors and floor
    1e-300), not the code under test. The exact comparison is justified as in
    ``test_analog_query_is_bitwise_independent_of_workers``: the worker count
    splits the query points among threads and changes no arithmetic.
    """
    from scipy.spatial import cKDTree

    monkeypatch.setenv("LPC_THREADS", threads)
    reference, queries = _reference_and_queries()
    dims, floored = local_dimension_counted(reference, queries)
    dist = cKDTree(reference).query(queries, k=20, workers=1)[0]
    ref_dims = 18 / np.sum(
        np.log(
            np.maximum(dist, 1e-300)[:, -1:] / np.maximum(dist, 1e-300)[:, :-1]
        ),
        axis=1,
    )
    assert dims.tobytes() == ref_dims.tobytes()
    assert not floored.any()


def test_oracle_pool_is_the_seeded_labeled_draw_shared_by_the_splits(
    monkeypatch,
) -> None:
    """P9 and DEC-0008 B: the 1/d pool is a fresh seeded draw per call.

    The pool is ``make_rng(seed, system, "oracle-pool")``.

    Reference: a hand re-draw from
    ``np.random.default_rng([seed, crc32(b"<system>|oracle-pool")])`` (NumPy
    used directly): ``choice(len(library), size, replace=False)``. The pool
    that ``state_oracles`` hands to ``local_dimension_counted`` is recorded.
    Every split of a system (two calls with different ``split``) gets the same
    pool. Another seed or another system gives a different one. The old
    literal ``default_rng(0)`` pool is not used. Tolerance: none (the stubbed
    pipeline passes the rows through unchanged).
    """
    import zlib
    from types import SimpleNamespace

    from lpcstudy import oracle, systems

    library = np.random.default_rng(1409).standard_normal((300, 2))
    eval_states = np.random.default_rng(1410).standard_normal((60, 2))
    gains = np.full((3, 4), 2.0)
    pools: list[np.ndarray] = []

    def spy(pool, queries):
        pools.append(np.array(pool))
        return np.ones(len(queries)), np.zeros(len(queries), dtype=bool)

    monkeypatch.setattr(systems, "make_flow_step", lambda *a, **k: None)
    monkeypatch.setattr(
        oracle, "make_observability", lambda *a, **k: (lambda s: np.ones(3))
    )
    monkeypatch.setattr(
        oracle, "make_amplification", lambda *a, **k: (lambda s: gains)
    )
    monkeypatch.setattr(oracle, "local_dimension_counted", spy)

    def ctx(name: str) -> SimpleNamespace:
        return SimpleNamespace(
            spec=SimpleNamespace(name=name, params={}, observed_index=0),
            interval=0.1,
            obs_scale=1.0,
            whiten=np.eye(2),
            unwhiten=np.eye(2),
            delay=1,
            embed_dim=3,
            history=2,
            library_states=library,
            eval_states=eval_states,
            split_indices={
                "test": np.array([10, 12, 14]),
                "calibration": np.array([20, 22, 24]),
            },
            whiten_states=lambda x: x,
        )

    seed = 20261005
    oracle.state_oracles(ctx("rossler"), "test", 4, seed)
    oracle.state_oracles(ctx("rossler"), "calibration", 4, seed)
    oracle.state_oracles(ctx("rossler"), "test", 4, seed + 1)
    oracle.state_oracles(ctx("chua"), "test", 4, seed)
    hand = np.random.default_rng([seed, zlib.crc32(b"rossler|oracle-pool")])
    expected = library[
        hand.choice(len(library), size=len(library), replace=False)
    ]
    assert np.array_equal(pools[0], expected)
    assert np.array_equal(pools[1], expected)
    assert not np.array_equal(pools[2], expected)
    assert not np.array_equal(pools[3], expected)
    legacy = library[
        np.random.default_rng(0).choice(
            len(library), size=len(library), replace=False
        )
    ]
    assert not np.array_equal(pools[0], legacy)
