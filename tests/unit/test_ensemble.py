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
    seed the minimum gap is far above that (applied-mathematician, WU-0005 log: the
    smallest relative gap over 37 200 gaps was 1.2e-6; 2.2e-5 at this seed).

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
