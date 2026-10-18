"""Tests for ``lpcstudy.ensemble``: forecast draws, counters and moments.

The module under test makes the CP and PLP forecasts under many noise draws,
clips the errors and counts every clip and replacement. Each test names an
independent reference (a brute-force search, a hand-planned world or a
manufactured answer) and gives the reason for its tolerance in plain words.
"""

from __future__ import annotations

import numpy as np
import pytest


def test_retrieval_spread() -> None:
    """Noise sensitivity is 0 for a fixed analog and about 1 for wander.

    What is checked: ``retrieval_spread`` returns 0 when the retrieved analog
    never changes, and about 1 when it wanders by one noise standard deviation.

    Reference: (a) a property: a fixed analog has zero spread. (b) an exact
    distribution: for independent N(0, rho^2) entries,
    N = sqrt(mean_r ||V_r - mean V||^2 / D) / rho is the sample standard
    deviation over R draws divided by rho. Its expectation is
    sqrt((R - 1)/R), about 1 - 2.5e-5 (a bias of -2.5e-5 at R = 20 000).

    Tolerances. (a) ``== 0.0`` exactly: the mean of 50 ones is exactly 1.0 in
    float64, so the centered values are exactly 0. (b) ``rel=0.02``, unchanged:
    the Monte Carlo relative standard error of N is 0.5 sqrt(2/(R D)) = 1.9e-3
    for R = 20 000 draws and D = 7 coordinates (the sample variance has
    relative standard deviation sqrt(2/n) with n = R D), so 0.02 is 10.6
    standard errors. The bias of -2.5e-5 is negligible.
    """
    from lpcstudy.ensemble import retrieval_spread

    fixed = np.ones((1, 50, 7))
    assert retrieval_spread(fixed, 0.1)[0] == 0.0
    wander = 0.1 * np.random.default_rng(8).standard_normal((1, 20_000, 7))
    assert retrieval_spread(wander, 0.1)[0] == pytest.approx(1.0, rel=0.02)


@pytest.mark.parametrize("n_analogs", [1, 2, 5])
def test_kdtree_query_matches_brute_force(n_analogs: int) -> None:
    """``AnalogLibrary.query`` equals an exhaustive nearest-neighbor search.

    What is checked: the fast k-d tree search returns the same neighbors and
    distances as comparing every query with every library vector.

    Reference: an independent algorithm (brute force). For each query the
    squared distances to all 10^4 library vectors in R^7 are formed directly
    as ``((q - x)**2).sum(1)`` (no ``|q|^2 - 2 q.x`` expansion, which suffers
    from cancellation), in chunks of 20 queries, and ordered with
    ``np.argsort(kind="stable")``. The reference never touches the k-d tree.

    Data: 10^4 standard-normal vectors from ``np.random.default_rng(50052)``
    and 200 queries (190 standard normal and 10 exact copies of library
    vectors, the zero-distance edge case). The library indices are
    ``arange(10_000) + 41`` so the position-to-time mapping is tested. The
    values of ``n_analogs`` are 1, 2 and 5: 5 is ``config.analog_counts``, and
    2 checks the second-nearest neighbor.

    Premise (a hard assert, not a skip): every gap between consecutive sorted
    squared distances, for the first 6 neighbors, exceeds 1e-9 of the larger
    one, so the index order is well defined and no tie can make the reference
    ambiguous. At this seed the smallest relative gap (the gap over the larger
    squared distance) is 1.8e-4, measured by a scratch script after the first
    run. The premise threshold 1e-9 was fixed in the plan, before any run. The
    applied mathematician measured a smallest relative gap of 1.2e-6 over
    37 200 gaps across 31 seeds, so the chance of a gap below 1e-9 in one test
    is about 3e-5 at a random seed.

    Tolerances. Indices: exact equality, because the premise rules out ties.
    Distances: ``rtol=1e-12, atol=0``. Each of the two computations rounds the
    difference (u), the square (2u + u) and 6 additions of non-negative terms
    (6u), which is 9u, plus 4.5u + u for the square root. So each is within
    5.5u and their difference within 11u = 1.2e-15 relative (u = 1.1e-16);
    1e-12 leaves a factor of about 800. The measured difference is 0 because
    the summation order is the same. The 10 copies must give exactly 0.0.
    """
    from lpcstudy.ensemble import AnalogLibrary
    from scipy.spatial import cKDTree

    rng = np.random.default_rng(50052)
    n_lib, dim, offset = 10_000, 7, 41
    vectors = rng.standard_normal((n_lib, dim))
    copies = rng.choice(n_lib, size=10, replace=False)
    queries = np.vstack([rng.standard_normal((190, dim)), vectors[copies]])
    library = AnalogLibrary(
        indices=np.arange(n_lib) + offset,
        noisy_series=np.zeros(n_lib + offset),
        tree=cKDTree(vectors),
    )

    ref_idx = np.empty((len(queries), 6), dtype=np.int64)
    ref_sq = np.empty((len(queries), 6))
    for start in range(0, len(queries), 20):
        chunk = queries[start : start + 20]
        sq = ((chunk[:, None, :] - vectors[None, :, :]) ** 2).sum(axis=2)
        order = np.argsort(sq, axis=1, kind="stable")[:, :6]
        ref_idx[start : start + 20] = order
        ref_sq[start : start + 20] = np.take_along_axis(sq, order, axis=1)
    gaps = np.diff(ref_sq, axis=1)
    assert np.all(gaps > 1e-9 * ref_sq[:, 1:]), "premise: tie-free ordering"
    assert np.array_equal(ref_idx[190:, 0], copies)

    indices, distances = library.query(queries, n_analogs)
    assert indices.shape == distances.shape == (200, n_analogs)
    np.testing.assert_array_equal(indices, ref_idx[:, :n_analogs] + offset)
    np.testing.assert_allclose(
        distances, np.sqrt(ref_sq[:, :n_analogs]), rtol=1e-12, atol=0
    )
    assert np.all(distances[190:, 0] == 0.0)
    with pytest.raises(ValueError):
        library.query(queries[:, :6], n_analogs)


def test_draw_correlation_matches_corrcoef_and_sets_constant_states_to_zero() -> (
    None
):
    """``draw_correlation`` equals ``np.corrcoef``; a constant error gives 0.

    What is checked: for each state and horizon the correlation over the
    noise draws matches the textbook value, and a state whose error is
    constant over the draws gets exactly 0.0 and a flag.

    Reference: an independent algorithm, ``np.corrcoef`` (a normalized
    covariance that does not use LAPACK), applied to each (state, horizon)
    pair of the M = 50 draws. Data: n = 6 states and nH = 3 horizons, with CP
    standard normal and PLP = 0.6 CP + 0.8 independent noise (true correlation
    0.6), from ``np.random.default_rng(2026)``. State 3 carries an offset of
    1e3 on both errors (mean/sd = 1e3, where a one-pass moment formula loses 6
    digits).

    Five (state, horizon) pairs are made constant with the value 0.3712345,
    which has no exact binary form, so the mean of 50 copies is not exactly
    the value and the unmasked two-pass result is not 0.0 (a premise asserted
    below, so the override is really exercised). They are: CP only at (0, 0),
    PLP only at (1, 1), both at (2, 2), and CP only at (4, 0) with the other
    horizons untouched. The expected masks are written out by hand.

    Tolerance: 1e-13 absolute on the correlation (tightened from the planned
    1e-12 on the applied mathematician's measurement of at most 1.1e-15 over
    1200 rows with mean/sd up to 1e5; the two algorithms differ by round-off of
    order M eps = 1e-14 at most). Constant states: ``== 0.0`` exactly (the
    override), and the masks are exact booleans.
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
    assert (
        corr.shape
        == cp_constant.shape
        == plp_constant.shape
        == (n_states, n_hor)
    )
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
    # Premise: without the override the constant CP row does not give 0.0
    # (it is garbage or NaN).
    centered = cp[0, :, 0] - cp[0, :, 0].mean()
    plp_centered = plp[0, :, 0] - plp[0, :, 0].mean()
    with np.errstate(all="ignore"):
        raw = np.sum(centered * plp_centered) / (
            np.sqrt(np.sum(centered**2)) * np.sqrt(np.sum(plp_centered**2))
        )
    assert not raw == 0.0
    assert np.all(np.abs(corr[~flagged]) <= 1.0 + 1e-12)


def test_draw_correlation_rejects_bad_shapes() -> None:
    """Bad input raises ``ValueError`` (PRIME.4).

    Bad means mismatched shapes, an input that is not 3-D, or a single draw.

    Reference: the documented contract (two arrays of shape ``(n, M >= 2, nH)``
    with one shape). Only the exception type is checked, so there is no
    tolerance.
    """
    from lpcstudy.ensemble import draw_correlation

    good = np.zeros((2, 5, 3))
    for bad_cp, bad_plp in (
        (good, np.zeros((2, 5, 4))),
        (np.zeros((2, 5)), np.zeros((2, 5))),
        (np.zeros((2, 1, 3)), np.zeros((2, 1, 3))),
    ):
        with pytest.raises(ValueError):
            draw_correlation(bad_cp, bad_plp)


def test_subset_carries_the_correlation_fields_and_keeps_none() -> None:
    """``EnsembleMoments.subset`` selects rows of the correlation fields.

    What is checked: ``subset`` picks the right rows of ``err_corr``,
    ``cp_constant`` and ``plp_constant``, and leaves absent fields as ``None``.

    Reference: hand-built moments with arrays whose entries are their own flat
    index, so the expected rows can be read off by eye: rows [3, 1] of a
    (5, 4) array. The result is exact (it is only indexing), so there is no
    tolerance.
    """
    import dataclasses

    from unit_helpers import _moments_from_draws

    rng = np.random.default_rng(5)
    base = _moments_from_draws(
        rng.standard_normal((5, 6, 4)), rng.standard_normal((5, 6, 4))
    )
    assert (
        base.err_corr is None and base.subset(np.array([3, 1])).err_corr is None
    )
    grid = np.arange(20.0).reshape(5, 4)
    full = dataclasses.replace(
        base, err_corr=grid, cp_constant=grid > 9, plp_constant=grid < 3
    )
    part = full.subset(np.array([3, 1]))
    np.testing.assert_array_equal(
        part.err_corr, [[12.0, 13.0, 14.0, 15.0], [4.0, 5.0, 6.0, 7.0]]
    )
    np.testing.assert_array_equal(part.cp_constant, (grid > 9)[[3, 1]])
    np.testing.assert_array_equal(part.plp_constant, (grid < 3)[[3, 1]])


# ------------------------------------------- WU-0002.11a: counters (DEF-0001)
def _old_error_lines(
    cp: np.ndarray, plp: np.ndarray, truth: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Return the error lines of ``forecast_draws`` from before WU-0002.11a.

    These are copied word for word, and serve as a bitwise reference.
    """
    clip = 10.0
    cp_err = np.clip(cp - truth, -clip, clip)
    plp_err = np.nan_to_num(plp - truth, nan=clip, posinf=clip, neginf=-clip)
    return cp_err, np.clip(plp_err, -clip, clip)


def test_clip_errors_a2_counts_and_boundary() -> None:
    """A2: ``clip_errors`` counts each kind of clip; exactly 10.0 is not a clip.

    What is checked: a CP error of +20, a PLP error of +inf, NaN or -15 are
    counted exactly once each, and an error equal to the clip level is not.

    Reference: a hand array with truth 0. The CP errors are
    [20, 10.0, -3, 0, 0, 0, 0]: one is clipped (20), and 10.0 equals the clip
    and is not counted. The PLP errors are [0, 0, +inf, NaN, -15, 10.0, -10.0]:
    +inf and NaN are non-finite (2), -15 is a finite clip (1), and +-10.0 are
    not counted. The expected counts (cp 1, nonfinite 2, plp 1, total 4) are
    read off the construction. The values are compared bit for bit
    (``tobytes``) with the old lines (copied above). Everything is exact, so
    there is no tolerance.
    """
    from lpcstudy.ensemble import clip_errors

    cp = np.array([[[20.0, 10.0, -3.0, 0.0, 0.0, 0.0, 0.0]]])
    plp = np.array([[[0.0, 0.0, np.inf, np.nan, -15.0, 10.0, -10.0]]])
    truth = np.zeros((1, 1, 7))
    cp_err, plp_err, masks = clip_errors(cp, plp, truth)
    counts = masks.counts()
    assert counts == {
        "error_clips_cp": 1,
        "error_clips_plp": 1,
        "error_clips_nonfinite": 2,
        "error_clips": 4,
    }
    assert masks.cp[0, 0].tolist() == [True] + [False] * 6
    assert masks.nonfinite[0, 0].tolist() == [
        False,
        False,
        True,
        True,
        False,
        False,
        False,
    ]
    assert masks.plp[0, 0].tolist() == [
        False,
        False,
        False,
        False,
        True,
        False,
        False,
    ]
    ref_cp, ref_plp = _old_error_lines(cp, plp, truth)
    assert cp_err.tobytes() == ref_cp.tobytes()
    assert plp_err.tobytes() == ref_plp.tobytes()
    assert plp_err[0, 0, 2] == 10.0
    assert plp_err[0, 0, 3] == 10.0
    assert plp_err[0, 0, 4] == -10.0


def test_clip_errors_values_bitwise_and_counts_by_loop_on_random_entries() -> (
    None
):
    """On random entries, values equal the old lines and counts equal a loop.

    What is checked: on 10^4 random entries with injected bad values, the
    clipped values equal the old lines bit for bit, and the counts equal a
    plain Python loop.

    Reference: for the values, the old lines (copied). For the counts, a loop
    over the entries that applies the definition entry by entry
    (``math.isfinite`` and ``abs > 10``), independent of the vectorized masks.
    Data: ``np.random.default_rng(1101)``. The CP and PLP forecasts are normal
    with standard deviation 6 (about 10% of the entries are beyond 10 when the
    truth has standard deviation 5). The PLP forecasts get injected +inf (200),
    -inf (100) and NaN (300) entries, and 50 entries each of CP and PLP get an
    error of exactly +-10.0. Everything is exact, so there is no tolerance.
    """
    import math

    from lpcstudy.ensemble import clip_errors

    rng = np.random.default_rng(1101)
    shape = (50, 20, 10)
    cp = 6.0 * rng.standard_normal(shape)
    plp = 6.0 * rng.standard_normal(shape)
    truth = 5.0 * rng.standard_normal((50, 1, 10))
    flat_plp = plp.reshape(-1)
    where = rng.choice(flat_plp.size, size=650, replace=False)
    flat_plp[where[:200]] = np.inf
    flat_plp[where[200:300]] = -np.inf
    flat_plp[where[300:600]] = np.nan
    exact = rng.choice(flat_plp.size, size=100, replace=False)
    truth_full = np.broadcast_to(truth, shape)
    flat_cp = cp.reshape(-1)
    flat_cp[exact[:50]] = truth_full.reshape(-1)[exact[:50]] + 10.0
    plp_view = flat_plp.copy()
    plp_view[exact[50:]] = truth_full.reshape(-1)[exact[50:]] - 10.0
    plp = plp_view.reshape(shape)
    cp = flat_cp.reshape(shape)
    cp_err, plp_err, masks = clip_errors(cp, plp, truth)
    ref_cp, ref_plp = _old_error_lines(cp, plp, truth)
    assert cp_err.tobytes() == ref_cp.tobytes()
    assert plp_err.tobytes() == ref_plp.tobytes()
    n_cp = n_plp = n_nonfinite = 0
    for c_val, p_val, t_val in zip(
        cp.reshape(-1), plp.reshape(-1), truth_full.reshape(-1)
    ):
        n_cp += abs(float(c_val) - float(t_val)) > 10.0
        diff = float(p_val) - float(t_val)
        if not math.isfinite(diff):
            n_nonfinite += 1
        elif abs(diff) > 10.0:
            n_plp += 1
    counts = masks.counts()
    # The loop subtracts in Python floats, the code in numpy float64: the same
    # IEEE operation.
    assert (
        counts["error_clips_cp"],
        counts["error_clips_plp"],
        counts["error_clips_nonfinite"],
    ) == (n_cp, n_plp, n_nonfinite)
    assert counts["error_clips"] == n_cp + n_plp + n_nonfinite
    # Premises (my own miscount, fixed before any rerun): 600 non-finite
    # entries were injected and the 50 exact PLP entries may overwrite some of
    # them, so at least 550 remain.
    assert n_nonfinite >= 550 and n_cp > 100 and n_plp > 100


def test_clip_errors_minus_inf_goes_to_minus_clip() -> None:
    """-inf becomes -10 and counts as non-finite; NaN and +inf become +10.

    Reference: the ``nan_to_num`` contract of the old line (``neginf=-clip``),
    on a hand array. The result is exact, so there is no tolerance.
    """
    from lpcstudy.ensemble import clip_errors

    _, plp_err, masks = clip_errors(
        np.zeros((1, 1, 3)),
        np.array([[[-np.inf, np.inf, np.nan]]]),
        np.zeros((1, 1, 3)),
    )
    assert plp_err[0, 0].tolist() == [-10.0, 10.0, 10.0]
    assert masks.counts()["error_clips_nonfinite"] == 3
    assert masks.counts()["error_clips_plp"] == 0


def _planned_lm(n_flat: int):
    """Return planned Levenberg-Marquardt diagnostics of ``n_flat`` flat rows.

    The rows are state-major with 3 draws per state. For flat row ``r`` the
    residual is ``r + 0.5``, the accepted count is ``2 r`` and the late
    progress flag is ``r mod 2``. The flag ``nonfinite_cost`` is set on rows 4,
    10 and 11 and ``nonfinite_jacobian`` on rows 5 and 9 (when they exist), so
    the per-state counts can be written out in the tests that use them.
    """
    from lpcstudy.estimation import LMDiagnostics

    rows = np.arange(n_flat)
    return LMDiagnostics(
        residual=rows + 0.5,
        accepted=(2 * rows).astype(np.int32),
        nonfinite_cost=np.isin(rows, [4, 10, 11]),
        nonfinite_jacobian=np.isin(rows, [5, 9]),
        late_progress=(rows % 2).astype(np.int32),
    )


def _fake_world(
    plp_diff: np.ndarray,
    state_bad: np.ndarray,
    nu_bad: np.ndarray,
    horizons: np.ndarray,
    n_states: int,
    n_draws: int,
):
    """Build a miniature, deterministic world for ``forecast_draws``.

    The estimator and the PLP paths are stubs. The estimator returns the flags
    it is given, and the PLP path is the truth plus ``plp_diff`` (a
    hand-planned error, flat and state-major, with shape
    ``(n_states * n_draws, nH)``). The library is a k-d tree over delay vectors
    of a random series, and the CP errors are small.
    """
    from types import SimpleNamespace

    from scipy.spatial import cKDTree

    from lpcstudy.embedding import delay_vectors
    from lpcstudy.ensemble import AnalogLibrary, ForecastSetup

    rng = np.random.default_rng(777)
    horizons = np.asarray(horizons)
    n_time, n_lib = 300, 200
    ctx = SimpleNamespace(
        eval_clean=rng.standard_normal(n_time),
        eval_states=rng.standard_normal((n_time, 2)),
        library_states=rng.standard_normal((n_lib, 2)),
        delay=1,
        embed_dim=3,
        split_indices={"test": np.arange(100, 100 + n_states)},
        whiten_states=lambda x: x,
    )
    series = rng.standard_normal(n_lib)
    indices = np.arange(2, n_lib - 10)
    library = AnalogLibrary(
        indices=indices,
        noisy_series=series,
        tree=cKDTree(delay_vectors(series, indices, 1, 3)),
    )
    times = ctx.split_indices["test"]
    truth = ctx.eval_clean[times[:, None] + horizons[None, :]]
    truth_flat = np.repeat(truth, n_draws, axis=0)
    h_last = int(horizons[-1])

    def paths(states):
        out = np.zeros((len(states), h_last))
        out[:, horizons - 1] = truth_flat + plp_diff
        return out

    class Stub:
        def estimate_counted(self, flat):
            return (
                np.full((len(flat), 2), 0.1),
                np.ones(len(flat)),
                state_bad,
                nu_bad,
                _planned_lm(len(flat)),
            )

    setup = ForecastSetup(
        ctx=ctx, noise=0.01, estimator=Stub(), model_step=None
    )
    setup._paths[h_last] = paths
    noise = np.random.default_rng(778).standard_normal((n_states, n_draws, 3))
    return setup, library, noise, np.arange(n_states)


def test_forecast_draws_handled_columns_per_state() -> None:
    """``forecast_draws`` fills ``handled`` per state from flags and clip masks.

    What is checked: the per-state counts of replaced estimates and clipped
    errors, including those at the reference horizon ``H_ref``.

    Reference: hand-planned counts in a miniature world with a stubbed
    estimator and PLP path (see ``_fake_world``). There are 4 states with 3
    draws each, horizons (1, 2, 3) and H_ref = 2. Flat rows are state-major
    (row = 3 state + draw).

    State flags: rows 0 and 1 (state 0) and row 7 (state 2) have a replaced
    state, and rows 7 (state 2) and 10 (state 3) have a replaced nu. PLP error
    plan:

    * row 0, column 1 is +inf (non-finite at H_ref, state 0);
    * row 1, column 1 is -25 (finite clip at H_ref, state 0);
    * row 1, column 0 is NaN (non-finite, not at H_ref);
    * row 5, column 2 is 12 (finite clip, not at H_ref);
    * row 9, column 1 is exactly -10.0 (not counted);
    * row 10, column 1 is 11 (finite clip at H_ref, state 3).

    The expected ``handled`` rows, written out by hand, are state 0
    [2,0,0,0,1,1], state 1 zeros, state 2 [1,1,0,0,0,0] and state 3
    [0,1,0,0,1,0]. The entry totals are non-finite 2, finite 3 and CP 0 (the
    CP errors are differences of unit normals). All counts are exact integers.
    The round trip "PLP truth + diff - truth" is not bitwise exact, so the
    clipped values are checked to 1e-12 (the round-off, about 10 u, is far
    below 1e-12).
    """
    from lpcstudy.ensemble import DRAW_COUNTERS, forecast_draws

    n_states, n_draws, horizons = 4, 3, np.array([1, 2, 3])
    diff = np.zeros((12, 3))
    diff[0, 1], diff[1, 1], diff[1, 0] = np.inf, -25.0, np.nan
    diff[5, 2], diff[9, 1], diff[10, 1] = 12.0, -10.0, 11.0
    state_bad = np.zeros(12, dtype=bool)
    state_bad[[0, 1, 7]] = True
    nu_bad = np.zeros(12, dtype=bool)
    nu_bad[[7, 10]] = True
    setup, library, noise, rows = _fake_world(
        diff, state_bad, nu_bad, horizons, n_states, n_draws
    )
    batch = forecast_draws(
        setup, library, "test", rows, noise, horizons, reference_horizon=2
    )
    # Columns 6 and 7 (WU-0005.4): the planned LM flags, ``_planned_lm``:
    # nonfinite_cost on flat rows 4, 10, 11 (states 1, 3, 3) -> [0, 1, 0, 2];
    # nonfinite_jacobian on rows 5, 9 (states 1, 3) -> [0, 1, 0, 1].
    expected = np.array(
        [
            [2, 0, 0, 0, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 1, 0, 2, 1],
        ]
    )
    assert DRAW_COUNTERS == (
        "invariant_mean_replacements",
        "nu_replacements",
        "gain_replacements",
        "gain_floor",
        "error_clips_plp_href",
        "error_clips_nonfinite_href",
        "lm_nonfinite_cost",
        "lm_nonfinite_jacobian",
    )
    assert batch.handled.dtype == np.int64 and batch.handled.shape == (4, 8)
    np.testing.assert_array_equal(batch.handled, expected)
    planned = _planned_lm(12)
    assert (
        batch.lm_residual.tobytes() == planned.residual.reshape(4, 3).tobytes()
    )
    assert np.array_equal(batch.lm_accepted, planned.accepted.reshape(4, 3))
    assert np.array_equal(batch.lm_late, planned.late_progress.reshape(4, 3))
    assert batch.clip_entries == {
        "error_clips_cp": 0,
        "error_clips_plp": 3,
        "error_clips_nonfinite": 2,
    }
    plp = batch.plp_err.reshape(12, 3)
    assert plp[0, 1] == 10.0 and plp[1, 1] == -10.0
    assert plp[1, 0] == 10.0 and plp[5, 2] == 10.0
    assert abs(plp[9, 1] - (-10.0)) < 1e-12 and plp[10, 1] == 10.0
    # Without a reference horizon the two H_ref columns are 0 and the others
    # are unchanged.
    plain = forecast_draws(setup, library, "test", rows, noise, horizons)
    assert np.all(plain.handled[:, 4:6] == 0)  # the two H_ref columns
    np.testing.assert_array_equal(plain.handled[:, :4], expected[:, :4])
    np.testing.assert_array_equal(plain.handled[:, 6:], expected[:, 6:])
    with pytest.raises(ValueError):
        forecast_draws(
            setup, library, "test", rows, noise, horizons, reference_horizon=7
        )


def test_sanitize_gains_a8_evaluation_path() -> None:
    """A8 (evaluation path): bad gains become 1e300 and are counted per draw.

    What is checked: NaN and +inf gains are replaced by 1e300 and counted once
    per draw, and a gain of 0.0 inside the growth window counts as a "floor".

    Reference: a hand array with window 4, 5 columns and 6 draws.

    * Row 0: NaN inside the window.
    * Row 1: +inf outside the window (column 4; it is still replaced, because
      the whole array is the unit).
    * Row 2: 0.0 inside the window.
    * Row 3: NaN and 0.0 (a replaced and floored draw; the NaN becomes 1e300
      and does not floor).
    * Row 4: 0.0 outside the window (not floored).
    * Row 5: NaN and +inf in one row (counts once: D5).

    Expected, read off the construction: replaced rows {0, 1, 3, 5} (4) and
    floored rows {2, 3} (2). The replaced values equal 1e300 bit for bit and
    every other entry is unchanged bit for bit (the old line is
    ``np.nan_to_num(gains, nan=1e300, posinf=1e300)``).
    """
    from lpcstudy.ensemble import sanitize_gains

    gains = np.full((6, 5), 2.0)
    gains[0, 3] = np.nan
    gains[1, 4] = np.inf
    gains[2, 1] = 0.0
    gains[3, 0], gains[3, 2] = np.nan, 0.0
    gains[4, 4] = 0.0
    gains[5, 1], gains[5, 3] = np.nan, np.inf
    clean, replaced, floored = sanitize_gains(gains, 4)
    assert replaced.tolist() == [True, True, False, True, False, True]
    assert floored.tolist() == [False, False, True, True, False, False]
    assert int(replaced.sum()) == 4 and int(floored.sum()) == 2
    expected = np.nan_to_num(gains, nan=1e300, posinf=1e300)
    assert clean.tobytes() == expected.tobytes()
    assert clean[0, 3] == 1e300 and clean[1, 4] == 1e300
    assert clean[5, 1] == 1e300
    assert clean[2, 1] == 0.0 and clean[3, 2] == 0.0


class _StubLibrary:
    """Stand in for ``AnalogLibrary`` where only the answer shapes matter."""

    def __init__(self, dim: int) -> None:
        self.dim = dim

    def query(self, vectors: np.ndarray, n_analogs: int):
        return (
            np.zeros((len(vectors), n_analogs), dtype=np.int64),
            np.zeros((len(vectors), n_analogs)),
        )

    def analog_vectors(self, lib_idx: np.ndarray) -> np.ndarray:
        return np.zeros((len(lib_idx), self.dim))


def _stubbed_forecasts(
    monkeypatch,
    handled_table: np.ndarray,
    entry_table: np.ndarray,
    n_draws: int,
    n_hor: int,
    dim: int,
):
    """Replace ``forecast_draws`` by a stub with planned results.

    The stub returns planned errors, ``handled`` rows and entry totals. The
    estimated state of flat row ``r`` (global, state-major) is ``[r, 0]``, so a
    stubbed amplification function can look the planned gains up by row.
    """
    from lpcstudy import ensemble

    n_states = len(handled_table)
    rng = np.random.default_rng(31)
    cp = rng.standard_normal((n_states, n_draws, n_hor))
    plp = rng.standard_normal((n_states, n_draws, n_hor))
    flat_id = np.arange(n_states * n_draws, dtype=float).reshape(
        n_states, n_draws
    )
    est_states = np.stack([flat_id, np.zeros_like(flat_id)], axis=-1)

    def fake(
        setup,
        library,
        split,
        rows,
        unit_noise,
        horizons,
        reference_horizon=None,
    ):
        residual, accepted, late = planned_lm(n_states, n_draws)
        return ensemble.DrawBatch(
            cp_err=cp[rows],
            plp_err=plp[rows],
            analog_seed_sq=np.ones((len(rows), n_draws)),
            est_seed_sq=np.ones((len(rows), n_draws)),
            distance=np.ones((len(rows), n_draws)),
            inputs=unit_noise,
            est_states=est_states[rows],
            est_nu=np.ones((len(rows), n_draws)),
            analog_vecs=np.zeros((len(rows), n_draws, dim)),
            handled=handled_table[rows].copy(),
            clip_entries={
                name: int(entry_table[rows, i].sum())
                for i, name in enumerate(ensemble.ENTRY_COUNTERS)
            },
            lm_residual=residual[rows],
            lm_accepted=accepted[rows],
            lm_late=late[rows],
        )

    monkeypatch.setattr(ensemble, "forecast_draws", fake)
    return cp, plp


def planned_lm(n_states: int, n_draws: int):
    """Return planned per-estimate LM arrays of shape ``(n_states, n_draws)``.

    For state ``s`` and draw ``d`` the residual is 10 s + d + 0.25, the
    accepted count is s + d and the late flag is (s + d) mod 2. The tests read
    the expected values off by hand.
    """
    s, d = np.meshgrid(np.arange(n_states), np.arange(n_draws), indexing="ij")
    return (
        10.0 * s + d + 0.25,
        (s + d).astype(np.int32),
        ((s + d) % 2).astype(np.int32),
    )


def _planned_tables(n_states: int, n_draws: int):
    """Return planned ``handled`` and entry-count tables (random integers)."""
    from lpcstudy.ensemble import DRAW_COUNTERS

    rng = np.random.default_rng(91)
    handled = rng.integers(
        0, n_draws + 1, size=(n_states, len(DRAW_COUNTERS))
    ).astype(np.int64)
    handled[:, 2:4] = 0  # Gain columns are filled by evaluation_draws only.
    entries = rng.integers(0, 50, size=(n_states, 3)).astype(np.int64)
    return handled, entries


@pytest.mark.parametrize("chunk_traj", [4, 10**6])
def test_ensemble_moments_accumulates_handled_exactly_for_any_chunking(
    monkeypatch, chunk_traj: int
) -> None:
    """A3 (oracle kind): counts equal the planned sums for any chunking.

    What is checked: ``handled`` and ``clip_entries`` of the oracle moments do
    not depend on how the states are split into chunks.

    Reference: hand sums. ``forecast_draws`` is replaced by a stub that
    returns a planned per-state ``handled`` table and planned entry counts per
    state (random integers from ``np.random.default_rng(91)``). The expected
    result is the table itself (per state) and its column sums (totals). The
    setting ``chunk_traj = 4`` with M = 4 draws gives one state per chunk, and
    ``10**6`` puts all 7 states in one chunk. The check is exact integer
    equality in both cases.
    """
    from types import SimpleNamespace

    from lpcstudy.ensemble import ENTRY_COUNTERS, ensemble_moments

    n_states, n_draws, n_hor, dim = 7, 4, 3, 2
    handled, entries = _planned_tables(n_states, n_draws)
    _stubbed_forecasts(monkeypatch, handled, entries, n_draws, n_hor, dim)
    setup = SimpleNamespace(noise=0.01)
    noise = np.zeros((n_states, n_draws, dim))
    moments = ensemble_moments(
        setup,
        None,
        "test",
        noise,
        np.arange(1, n_hor + 1),
        chunk_traj=chunk_traj,
        reference_horizon=2,
    )
    np.testing.assert_array_equal(moments.handled, handled)
    assert moments.handled.dtype == np.int64
    assert moments.clip_entries == {
        name: int(entries[:, i].sum()) for i, name in enumerate(ENTRY_COUNTERS)
    }
    part = moments.subset(np.array([5, 2]))
    np.testing.assert_array_equal(part.handled, handled[[5, 2]])
    assert part.clip_entries is None  # A view has no valid entry totals.
    # WU-0005.4: the per-estimate LM arrays equal the planned ones for any
    # chunking (rows in order), and a row subset slices them like ``handled``.
    residual, accepted, late = planned_lm(n_states, n_draws)
    assert moments.lm_residual.tobytes() == residual.tobytes()
    assert np.array_equal(moments.lm_accepted, accepted)
    assert np.array_equal(moments.lm_late, late)
    assert part.lm_residual.tobytes() == residual[[5, 2]].tobytes()
    assert np.array_equal(part.lm_accepted, accepted[[5, 2]])


@pytest.mark.parametrize("chunk_traj", [4, 10**6])
def test_evaluation_draws_accumulates_handled_and_gain_columns(
    monkeypatch, chunk_traj: int
) -> None:
    """A3 and A8 (evaluation kind): gain columns are counted per state.

    What is checked: ``evaluation_draws`` fills the gain columns of
    ``handled`` per state, passes the other columns through unchanged, and
    keeps the values it computes.

    Reference: hand sums. There are 6 states with 4 draws, horizons (1, 3, 5)
    and window 4 (5 gain columns). ``forecast_draws`` is replaced by a stub
    (planned ``handled`` rows and entry counts, random integers from
    ``np.random.default_rng(91)``). The stubbed amplification returns a
    planned gain table with:

    * flat row 2 (state 0): NaN in the window;
    * row 5 (state 1): +inf outside the window;
    * row 9 (state 2): 0.0 in the window;
    * row 10 (state 2): NaN and 0.0;
    * row 13 (state 3): 0.0 outside the window;
    * row 14 (state 3): NaN and +inf in one row.

    Expected ``gain_replacements`` per state [1, 1, 1, 1, 0, 0] and
    ``gain_floor`` [0, 0, 2, 0, 0, 0], read off the construction (D5: the row
    with both NaN and +inf counts once). The other columns equal the planned
    table. ``growth_proxy`` and ``gain_proxy`` equal the old expression
    (``nan_to_num`` then ``growth_exponent``) applied to the planned gains,
    bit for bit. Everything is exact, so there is no tolerance.
    """
    from types import SimpleNamespace

    from lpcstudy.dynamics import growth_exponent
    from lpcstudy.ensemble import ENTRY_COUNTERS, evaluation_draws

    n_states, n_draws, dim, window = 6, 4, 2, 4
    horizons = np.array([1, 3, 5])
    handled, entries = _planned_tables(n_states, n_draws)
    _stubbed_forecasts(
        monkeypatch, handled, entries, n_draws, len(horizons), dim
    )
    gains = np.random.default_rng(5).uniform(
        0.5, 3.0, size=(n_states * n_draws, 5)
    )
    gains[2, 3] = np.nan
    gains[5, 4] = np.inf
    gains[9, 1] = 0.0
    gains[10, 0], gains[10, 2] = np.nan, 0.0
    gains[13, 4] = 0.0
    gains[14, 1], gains[14, 3] = np.nan, np.inf

    def amplification(amp_steps):
        return lambda states: gains[np.asarray(states)[:, 0].astype(int)]

    setup = SimpleNamespace(
        noise=0.01, n_analogs=1, amplification=amplification
    )
    noise = np.zeros((n_states, n_draws, dim))
    verify = np.zeros((n_states, n_draws, 5))
    synth = np.zeros((n_states, n_draws, 3, dim))
    out = evaluation_draws(
        setup,
        _StubLibrary(dim),
        "test",
        noise,
        verify,
        horizons,
        window,
        synth,
        chunk_traj=chunk_traj,
        reference_horizon=3,
    )
    expected = handled.copy()
    expected[:, 2] = [1, 1, 1, 1, 0, 0]
    expected[:, 3] = [0, 0, 2, 0, 0, 0]
    np.testing.assert_array_equal(out.handled, expected)
    assert out.clip_entries == {
        name: int(entries[:, i].sum()) for i, name in enumerate(ENTRY_COUNTERS)
    }
    old = np.nan_to_num(gains, nan=1e300, posinf=1e300)
    assert (
        out.growth_proxy.tobytes()
        == growth_exponent(old, window).reshape(n_states, n_draws).tobytes()
    )
    assert (
        out.gain_proxy.tobytes()
        == old[:, horizons - 1].reshape(n_states, n_draws, -1).tobytes()
    )
    sub = out.subset(np.array([4, 0]))
    np.testing.assert_array_equal(sub.handled, expected[[4, 0]])
    assert sub.clip_entries is None
    # WU-0005.4: the LM arrays of the evaluation draws are the planned ones, in
    # row order.
    residual, accepted, late = planned_lm(n_states, n_draws)
    assert out.lm_residual.tobytes() == residual.tobytes()
    assert np.array_equal(out.lm_accepted, accepted)
    assert np.array_equal(out.lm_late, late)
    assert sub.lm_residual.tobytes() == residual[[4, 0]].tobytes()


class _SpyTree:
    """Wrap a real ``cKDTree`` and record the keyword arguments of ``query``."""

    def __init__(self, tree) -> None:
        self.tree = tree
        self.calls: list[dict] = []

    def query(self, *args, **kwargs):
        self.calls.append(dict(kwargs))
        return self.tree.query(*args, **kwargs)


def _synthetic_library():
    """Return a fixed 3000-vector library in R^5 (seed 50120) and 40 queries."""
    from lpcstudy.ensemble import AnalogLibrary
    from scipy.spatial import cKDTree

    rng = np.random.default_rng(50120)
    vectors = rng.standard_normal((3000, 5))
    queries = rng.standard_normal((40, 5))
    tree = cKDTree(vectors)
    library = AnalogLibrary(
        indices=np.arange(3000) + 7, noisy_series=np.zeros(3007), tree=tree
    )
    return library, tree, queries


@pytest.mark.parametrize(
    "value, expected",
    [(None, 4), ("", 4), ("1", 1), ("2", 2), ("8", 8), ("99", 99)],
)
def test_worker_count_reads_lpc_threads(
    monkeypatch, value, expected: int
) -> None:
    """``worker_count`` is ``LPC_THREADS`` as an integer, 4 if unset or empty.

    (DEF-0012.) Reference: the rule of ``tools/run_tests.sh``
    (``${LPC_THREADS:-4}``, an integer from 1 to 99), stated here as the table
    of expected values. The comparison is between exact integers, so there is
    no tolerance.
    """
    from lpcstudy.ensemble import worker_count

    if value is None:
        monkeypatch.delenv("LPC_THREADS", raising=False)
    else:
        monkeypatch.setenv("LPC_THREADS", value)
    assert worker_count() == expected


@pytest.mark.parametrize("value", ["0", "-1", "abc", "100", "07", "2.5", " 4"])
def test_worker_count_rejects_invalid_values(monkeypatch, value: str) -> None:
    """Values outside the integers 1 to 99 raise a ``ValueError`` (PRIME.4).

    The error message names ``LPC_THREADS``. Reference: the validation of
    ``tools/run_tests.sh`` (``^[1-9][0-9]?$``). There is no silent fallback
    to 4.
    """
    from lpcstudy.ensemble import worker_count

    monkeypatch.setenv("LPC_THREADS", value)
    with pytest.raises(ValueError, match="LPC_THREADS"):
        worker_count()


@pytest.mark.parametrize("value, expected", [(None, 4), ("2", 2), ("8", 8)])
def test_analog_query_passes_lpc_threads_as_workers(
    monkeypatch, value, expected: int
) -> None:
    """``AnalogLibrary.query`` calls the tree with ``workers == LPC_THREADS``.

    (DEF-0012.) Reference: the expected integer is the environment value set
    by the test (4 when unset). The spy forwards to a real ``cKDTree``, so the
    call is also valid. The comparison is exact.
    """
    library, tree, queries = _synthetic_library()
    spy = _SpyTree(tree)
    library.tree = spy
    if value is None:
        monkeypatch.delenv("LPC_THREADS", raising=False)
    else:
        monkeypatch.setenv("LPC_THREADS", value)
    library.query(queries, 3)
    assert len(spy.calls) == 1 and spy.calls[0]["workers"] == expected


@pytest.mark.parametrize("value", ["0", "-1", "abc"])
def test_analog_query_rejects_invalid_lpc_threads(
    monkeypatch, value: str
) -> None:
    """An invalid ``LPC_THREADS`` makes ``AnalogLibrary.query`` raise.

    It raises ``ValueError`` and does not query the tree (there is no silent
    fallback, PRIME.4).
    """
    library, tree, queries = _synthetic_library()
    spy = _SpyTree(tree)
    library.tree = spy
    monkeypatch.setenv("LPC_THREADS", value)
    with pytest.raises(ValueError, match="LPC_THREADS"):
        library.query(queries, 3)
    assert spy.calls == []


@pytest.mark.parametrize("threads", ["1", "4"])
def test_analog_query_is_bitwise_independent_of_workers(
    monkeypatch, threads: str
) -> None:
    """Indices and distances are bit for bit those of a 1-worker query.

    Reference: ``cKDTree.query(..., workers=1)`` on the same tree, with the
    library's position-to-time map applied by hand. Why the comparison is
    exact: a k-d tree query is a deterministic search per query point. The
    worker count only splits the query points among threads and does not
    change any arithmetic, so the bytes are identical (a failure would mean a
    data race or a different code path, not round-off).
    """
    library, tree, queries = _synthetic_library()
    monkeypatch.setenv("LPC_THREADS", threads)
    indices, distances = library.query(queries, 5)
    ref_dist, ref_pos = tree.query(queries, k=5, workers=1)
    assert distances.tobytes() == ref_dist.tobytes()
    assert indices.tobytes() == (np.arange(3000) + 7)[ref_pos].tobytes()


# ----------------------- half-draw moments for the state dump (WU-0003.7b)
@pytest.mark.parametrize("n_draws, sizes", [(6, [3, 3]), (7, [3, 4])])
@pytest.mark.parametrize("chunk_traj", [6, 10**6])
def test_ensemble_moments_half_out_holds_the_half_draw_moments_and_changes_nothing(
    monkeypatch, n_draws: int, sizes: list[int], chunk_traj: int
) -> None:
    """``half_out`` gets the second moments of each half of the draws.

    The two halves are the draws ``[0, M // 2)`` and ``[M // 2, M)``, and the
    returned moments are unchanged by asking for them.

    Reference: brute force on the planned errors that the stubbed
    ``forecast_draws`` returns: ``mean(cp[:, :h]**2)`` and the other five by
    direct slicing, written in the test.

    1. The moments returned with ``half_out`` equal those returned without it,
       bit for bit (the dump is read-only).
    2. The half arrays equal the brute force to ``rtol = 1e-14``. Each is a
       mean of at most 4 products, so the round-off is below
       gamma_4 = 4.4e-16 relative to the sum of absolute terms, and the brute
       force sums the same terms in the same order (a factor of 20 of margin).
    3. For even M the average of the halves is the full moment to ``1e-13``
       times the mean absolute term (b4 of the plan: gamma_M is about M u, here
       M = 6; the plan's value 1e-13 at M = 200 has margin 4.5).
    4. ``n_draws`` holds the two sizes (the floor of M / 2 and the rest).
    5. ``abs_cross`` is ``mean |cp * plp|`` over all the draws, the exact scale
       that the dump hands to b4 (R3 of the review).
    """
    from types import SimpleNamespace

    from lpcstudy.ensemble import ensemble_moments

    n_states, n_hor, dim = 7, 3, 2
    handled, entries = _planned_tables(n_states, n_draws)
    cp, plp = _stubbed_forecasts(
        monkeypatch, handled, entries, n_draws, n_hor, dim
    )
    setup = SimpleNamespace(noise=0.01)
    noise = np.zeros((n_states, n_draws, dim))
    kwargs = dict(chunk_traj=chunk_traj, reference_horizon=2)
    plain = ensemble_moments(
        setup, None, "test", noise, np.arange(1, n_hor + 1), **kwargs
    )
    half: dict = {}
    with_half = ensemble_moments(
        setup,
        None,
        "test",
        noise,
        np.arange(1, n_hor + 1),
        half_out=half,
        **kwargs,
    )
    for name in (
        "mean_cp",
        "mean_plp",
        "sq_cp",
        "sq_plp",
        "cross",
        "analog_seed",
        "est_seed",
        "noise_sens",
        "err_corr",
        "handled",
        "lm_residual",
    ):
        same = (
            getattr(with_half, name).tobytes() == getattr(plain, name).tobytes()
        )
        assert same, name
    h = n_draws // 2
    assert (
        half["n_draws"].tolist() == sizes and half["n_draws"].dtype == np.int64
    )
    for tag, part in (("A", slice(0, h)), ("B", slice(h, None))):
        for stem, brute in (
            ("sq_cp", cp[:, part] ** 2),
            ("sq_plp", plp[:, part] ** 2),
            ("cross", cp[:, part] * plp[:, part]),
        ):
            np.testing.assert_allclose(
                half[f"{stem}_{tag}"], brute.mean(axis=1), rtol=1e-14, atol=0.0
            )
    np.testing.assert_allclose(
        half["abs_cross"], np.abs(cp * plp).mean(axis=1), rtol=1e-14, atol=0.0
    )
    if n_draws % 2 == 0:
        for stem, brute in (
            ("sq_cp", cp**2),
            ("sq_plp", plp**2),
            ("cross", cp * plp),
        ):
            # The exact mean absolute term (R3: also dumped).
            scale = np.abs(brute).mean(axis=1)
            diff = np.abs(
                0.5 * (half[f"{stem}_A"] + half[f"{stem}_B"])
                - getattr(plain, stem)
            )
            assert np.all(diff <= 1e-13 * scale)


def test_ensemble_moments_half_out_needs_two_draws(monkeypatch) -> None:
    """One oracle draw cannot be split, so ``half_out`` raises ``ValueError``.

    Nothing is invented to fill the missing half. Reference: the documented
    contract; only the exception and its message are checked.
    """
    from types import SimpleNamespace

    from lpcstudy.ensemble import ensemble_moments

    handled, entries = _planned_tables(3, 1)
    _stubbed_forecasts(monkeypatch, handled, entries, 1, 2, 2)
    with pytest.raises(ValueError, match="at least two oracle draws"):
        ensemble_moments(
            SimpleNamespace(noise=0.01),
            None,
            "test",
            np.zeros((3, 1, 2)),
            np.arange(1, 3),
            half_out={},
        )


def test_ensemble_moments_rejects_a_missing_reference_horizon() -> None:
    """A reference horizon that is not among the horizons raises ``ValueError``.

    This is the same check that ``forecast_draws`` makes, now made once
    before any forecast starts (both functions share one helper). Reference:
    the documented contract; only the exception and its message are checked.
    """
    from types import SimpleNamespace

    from lpcstudy.ensemble import ensemble_moments

    with pytest.raises(ValueError, match="reference_horizon 7 is not in"):
        ensemble_moments(
            SimpleNamespace(noise=0.01),
            None,
            "test",
            np.zeros((3, 2, 2)),
            np.arange(1, 3),
            reference_horizon=7,
        )
