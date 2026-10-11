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


@pytest.mark.parametrize("n_analogs", [1, 2, 5])
def test_kdtree_query_matches_brute_force(n_analogs: int) -> None:
    """``AnalogLibrary.query`` equals an exhaustive nearest-neighbour search.

    Reference: independent algorithm (brute force). For each query the squared
    distances to all 10^4 library vectors in R^7 are formed directly as
    ``((q - x)**2).sum(1)`` (no ``|q|^2 - 2 q.x`` expansion, which cancels), in
    chunks of 20 queries, and ordered with ``np.argsort(kind="stable")``. The
    reference never touches the k-d tree. Data: 10^4 standard-normal vectors from
    ``np.random.default_rng(50052)``; 200 queries (190 standard normal and 10 exact
    copies of library vectors, the zero-distance edge case). The library indices are
    ``arange(10_000) + 41`` so the position-to-time mapping is tested. ``n_analogs``
    in {1, 2, 5}: 5 is ``config.analog_counts``, and 2 checks the second-nearest.

    Premise (hard assert, not a skip): every gap between consecutive sorted squared
    distances, for the first 6 neighbours, exceeds 1e-9 of the larger one, so the
    index order is well defined and no tie can make the reference ambiguous. At this
    seed the smallest relative gap (gap over the larger squared distance) is 1.8e-4,
    measured by a scratch script after the first run (the premise threshold 1e-9 was fixed in
    the plan, before any run; the applied-mathematician measured a smallest
    relative gap of 1.2e-6 over 37 200 gaps across 31 seeds, so P(a gap < 1e-9 in one
    test) is about 3e-5 at a random seed).

    Tolerances. Indices: exact equality, because the premise rules out ties. Distances:
    ``rtol=1e-12, atol=0``. Each of the two computations rounds the difference (u), the
    square (2u + u) and 6 additions of non-negative terms (6u), 9u, plus 4.5u + u for the
    square root, so each is within 5.5u and their difference within 11u = 1.2e-15
    relative (u = 1.1e-16); 1e-12 leaves a factor of about 800. The measured difference
    is 0 because the summation order is the same. The 10 copies must give exactly 0.0.
    """
    from lpcstudy.ensemble import AnalogLibrary
    from scipy.spatial import cKDTree

    rng = np.random.default_rng(50052)
    n_lib, dim, offset = 10_000, 7, 41
    vectors = rng.standard_normal((n_lib, dim))
    copies = rng.choice(n_lib, size=10, replace=False)
    queries = np.vstack([rng.standard_normal((190, dim)), vectors[copies]])
    library = AnalogLibrary(indices=np.arange(n_lib) + offset,
                            noisy_series=np.zeros(n_lib + offset), tree=cKDTree(vectors))

    ref_idx = np.empty((len(queries), 6), dtype=np.int64)
    ref_sq = np.empty((len(queries), 6))
    for start in range(0, len(queries), 20):
        chunk = queries[start:start + 20]
        sq = ((chunk[:, None, :] - vectors[None, :, :]) ** 2).sum(axis=2)
        order = np.argsort(sq, axis=1, kind="stable")[:, :6]
        ref_idx[start:start + 20] = order
        ref_sq[start:start + 20] = np.take_along_axis(sq, order, axis=1)
    gaps = np.diff(ref_sq, axis=1)
    assert np.all(gaps > 1e-9 * ref_sq[:, 1:]), "premise: tie-free ordering"
    assert np.array_equal(ref_idx[190:, 0], copies)

    indices, distances = library.query(queries, n_analogs)
    assert indices.shape == distances.shape == (200, n_analogs)
    np.testing.assert_array_equal(indices, ref_idx[:, :n_analogs] + offset)
    np.testing.assert_allclose(distances, np.sqrt(ref_sq[:, :n_analogs]), rtol=1e-12, atol=0)
    assert np.all(distances[190:, 0] == 0.0)
    with pytest.raises(ValueError):
        library.query(queries[:, :6], n_analogs)


def test_draw_correlation_matches_corrcoef_and_sets_constant_states_to_zero() -> None:
    """``draw_correlation`` equals ``np.corrcoef`` per state; a constant error gives exactly 0.

    Reference: independent algorithm, ``np.corrcoef`` (LAPACK-free normalized covariance) applied
    to each (state, horizon) pair of the M = 50 draws. Data: n = 6 states, nH = 3 horizons,
    CP standard normal, PLP = 0.6 CP + 0.8 independent noise (true correlation 0.6), from
    ``np.random.default_rng(2026)``; state 3 carries an offset of 1e3 on both errors (mean/sd =
    1e3, where a moment formula loses 6 digits). Five (state, horizon) pairs are made constant
    with the non-dyadic value 0.3712345, so the mean of 50 copies is not exactly the value and
    the unmasked two-pass result is not 0.0 (a premise asserted below, so the override is
    exercised): CP only at (0, 0), PLP only at (1, 1), both at (2, 2); CP only at (4, 0) with the
    other horizons untouched. Expected masks written out by hand.
    Tolerance: 1e-13 absolute on the correlation (tightened from the planned 1e-12 on the
    applied-mathematician's measurement of at most 1.1e-15 over 1200 rows with mean/sd up to
    1e5; the two algorithms differ by round-off of order M eps = 1e-14 at most). Constant
    states: ``== 0.0`` exactly (the override), and the masks are exact booleans.
    """
    rng = np.random.default_rng(2026)
    n_states, n_draws, n_hor = 6, 50, 3
    cp = rng.standard_normal((n_states, n_draws, n_hor))
    plp = 0.6 * cp + 0.8 * rng.standard_normal(cp.shape)
    cp[3] += 1e3
    plp[3] += 1e3
    constant = 0.3712345
    cp[0, :, 0] = constant
    plp[1, :, 1] = constant
    cp[2, :, 2] = constant
    plp[2, :, 2] = constant
    cp[4, :, 0] = constant
    expect_cp = np.zeros((n_states, n_hor), dtype=bool)
    expect_plp = np.zeros((n_states, n_hor), dtype=bool)
    expect_cp[[0, 2, 4], [0, 2, 0]] = True
    expect_plp[[1, 2], [1, 2]] = True

    from lpcstudy.ensemble import draw_correlation

    corr, cp_constant, plp_constant = draw_correlation(cp, plp)
    assert corr.shape == cp_constant.shape == plp_constant.shape == (n_states, n_hor)
    np.testing.assert_array_equal(cp_constant, expect_cp)
    np.testing.assert_array_equal(plp_constant, expect_plp)
    flagged = expect_cp | expect_plp
    assert np.all(corr[flagged] == 0.0)
    for state in range(n_states):
        for hor in range(n_hor):
            if flagged[state, hor]:
                continue
            reference = np.corrcoef(cp[state, :, hor], plp[state, :, hor])[0, 1]
            assert abs(corr[state, hor] - reference) < 1e-13
    # Premise: without the override the constant CP row does not give 0.0 (it is garbage or NaN).
    centered = cp[0, :, 0] - cp[0, :, 0].mean()
    with np.errstate(all="ignore"):
        raw = np.sum(centered * (plp[0, :, 0] - plp[0, :, 0].mean())) / (
            np.sqrt(np.sum(centered**2)) * np.sqrt(np.sum((plp[0, :, 0] - plp[0, :, 0].mean())**2)))
    assert not raw == 0.0
    assert np.all(np.abs(corr[~flagged]) <= 1.0 + 1e-12)


def test_draw_correlation_rejects_bad_shapes() -> None:
    """Mismatched shapes, a non-3-D input or a single draw raise ``ValueError`` (PRIME.4).

    Reference: the documented contract (arrays ``(n, M >= 2, nH)`` of one shape). Exact.
    """
    from lpcstudy.ensemble import draw_correlation

    good = np.zeros((2, 5, 3))
    for bad_cp, bad_plp in ((good, np.zeros((2, 5, 4))), (np.zeros((2, 5)), np.zeros((2, 5))),
                            (np.zeros((2, 1, 3)), np.zeros((2, 1, 3)))):
        with pytest.raises(ValueError):
            draw_correlation(bad_cp, bad_plp)


def test_subset_carries_the_correlation_fields_and_keeps_none() -> None:
    """``EnsembleMoments.subset`` selects the rows of ``err_corr``, ``cp_constant`` and
    ``plp_constant`` and leaves absent fields as ``None``.

    Reference: hand-built moments with arrays whose entries are their own flat index (so the
    expected rows are read off by eye): rows [3, 1] of a (5, 4) array. Exact (indexing only).
    """
    import dataclasses

    from unit_helpers import _moments_from_draws

    rng = np.random.default_rng(5)
    base = _moments_from_draws(rng.standard_normal((5, 6, 4)), rng.standard_normal((5, 6, 4)))
    assert base.err_corr is None and base.subset(np.array([3, 1])).err_corr is None
    grid = np.arange(20.0).reshape(5, 4)
    full = dataclasses.replace(base, err_corr=grid, cp_constant=grid > 9, plp_constant=grid < 3)
    part = full.subset(np.array([3, 1]))
    np.testing.assert_array_equal(part.err_corr, [[12.0, 13.0, 14.0, 15.0], [4.0, 5.0, 6.0, 7.0]])
    np.testing.assert_array_equal(part.cp_constant, (grid > 9)[[3, 1]])
    np.testing.assert_array_equal(part.plp_constant, (grid < 3)[[3, 1]])
