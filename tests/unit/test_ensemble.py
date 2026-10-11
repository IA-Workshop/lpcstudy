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


# ---------------------------------------------------------------- WU-0002.11a: counters (DEF-0001)
def _old_error_lines(cp: np.ndarray, plp: np.ndarray, truth: np.ndarray
                     ) -> tuple[np.ndarray, np.ndarray]:
    """The three error lines of ``forecast_draws`` before WU-0002.11a, verbatim (bitwise reference)."""
    clip = 10.0
    cp_err = np.clip(cp - truth, -clip, clip)
    plp_err = np.nan_to_num(plp - truth, nan=clip, posinf=clip, neginf=-clip)
    return cp_err, np.clip(plp_err, -clip, clip)


def test_clip_errors_a2_counts_and_boundary() -> None:
    """A2: ``clip_errors`` counts CP +20, PLP +inf, NaN and -15 exactly; 10.0 is not a clip.

    Reference: a hand array, truth 0. CP errors [20, 10.0, -3, 0, 0, 0, 0]: one clipped (20); 10.0
    equals the clip and is not counted. PLP errors [0, 0, +inf, NaN, -15, 10.0, -10.0]: +inf and
    NaN are non-finite (2), -15 is a finite clip (1); +-10.0 are not counted. Expected counts
    (cp 1, nonfinite 2, plp 1, total 4) are read off the construction. Values are compared
    bitwise (``tobytes``) with the three old lines (copied above).
    """
    from lpcstudy.ensemble import clip_errors

    cp = np.array([[[20.0, 10.0, -3.0, 0.0, 0.0, 0.0, 0.0]]])
    plp = np.array([[[0.0, 0.0, np.inf, np.nan, -15.0, 10.0, -10.0]]])
    truth = np.zeros((1, 1, 7))
    cp_err, plp_err, masks = clip_errors(cp, plp, truth)
    counts = masks.counts()
    assert counts == {"error_clips_cp": 1, "error_clips_plp": 1, "error_clips_nonfinite": 2,
                      "error_clips": 4}
    assert masks.cp[0, 0].tolist() == [True] + [False] * 6
    assert masks.nonfinite[0, 0].tolist() == [False, False, True, True, False, False, False]
    assert masks.plp[0, 0].tolist() == [False, False, False, False, True, False, False]
    ref_cp, ref_plp = _old_error_lines(cp, plp, truth)
    assert cp_err.tobytes() == ref_cp.tobytes() and plp_err.tobytes() == ref_plp.tobytes()
    assert plp_err[0, 0, 2] == 10.0 and plp_err[0, 0, 3] == 10.0 and plp_err[0, 0, 4] == -10.0


def test_clip_errors_values_bitwise_and_counts_by_loop_on_random_entries() -> None:
    """On 10^4 random entries with injections, values equal the old lines bitwise and the counts
    equal a plain Python loop.

    Reference: (values) the three old lines, copied; (counts) a loop over the entries applying the
    definition entry by entry (``math.isfinite`` and ``abs > 10``), independent of the vectorized
    masks. Data: ``np.random.default_rng(1101)``; CP and PLP forecasts are 6 sigma normal (about 10%
    of the entries beyond 10 when the truth is 5 sigma), with injected +inf (200), -inf (100), NaN
    (300) entries in PLP, and an exact +-10.0 error in 50 entries each of CP and PLP. Exact.
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
    assert cp_err.tobytes() == ref_cp.tobytes() and plp_err.tobytes() == ref_plp.tobytes()
    n_cp = n_plp = n_nonfinite = 0
    for c_val, p_val, t_val in zip(cp.reshape(-1), plp.reshape(-1), truth_full.reshape(-1)):
        n_cp += abs(float(c_val) - float(t_val)) > 10.0
        diff = float(p_val) - float(t_val)
        if not math.isfinite(diff):
            n_nonfinite += 1
        elif abs(diff) > 10.0:
            n_plp += 1
    counts = masks.counts()
    # The loop subtracts in Python floats, the code in numpy float64: the same IEEE operation.
    assert (counts["error_clips_cp"], counts["error_clips_plp"],
            counts["error_clips_nonfinite"]) == (n_cp, n_plp, n_nonfinite)
    assert counts["error_clips"] == n_cp + n_plp + n_nonfinite
    # Premises (my own miscount, fixed before any rerun): 600 non-finite entries were injected and
    # the 50 exact PLP entries may overwrite some of them, so at least 550 remain.
    assert n_nonfinite >= 550 and n_cp > 100 and n_plp > 100


def test_clip_errors_minus_inf_goes_to_minus_clip() -> None:
    """-inf becomes -10 and counts as non-finite (the NaN and +inf branches map to +10).

    Reference: the ``nan_to_num`` contract of the old line (``neginf=-clip``), hand array. Exact.
    """
    from lpcstudy.ensemble import clip_errors

    _, plp_err, masks = clip_errors(np.zeros((1, 1, 3)), np.array([[[-np.inf, np.inf, np.nan]]]),
                                    np.zeros((1, 1, 3)))
    assert plp_err[0, 0].tolist() == [-10.0, 10.0, 10.0]
    assert masks.counts()["error_clips_nonfinite"] == 3 and masks.counts()["error_clips_plp"] == 0


def _fake_world(plp_diff: np.ndarray, state_bad: np.ndarray, nu_bad: np.ndarray,
                horizons: np.ndarray, n_states: int, n_draws: int):
    """A miniature, deterministic world for ``forecast_draws`` with stubbed estimator and paths.

    The estimator returns the flags it is given; the PLP path is the truth plus ``plp_diff``
    (a hand-planned error, flat state-major ``(n_states * n_draws, nH)``). The library is a
    k-d tree over delay vectors of a random series; CP errors are small.
    """
    from types import SimpleNamespace

    from scipy.spatial import cKDTree

    from lpcstudy.embedding import delay_vectors
    from lpcstudy.ensemble import AnalogLibrary, ForecastSetup

    rng = np.random.default_rng(777)
    horizons = np.asarray(horizons)
    n_time, n_lib = 300, 200
    ctx = SimpleNamespace(
        eval_clean=rng.standard_normal(n_time), eval_states=rng.standard_normal((n_time, 2)),
        library_states=rng.standard_normal((n_lib, 2)), delay=1, embed_dim=3,
        split_indices={"test": np.arange(100, 100 + n_states)},
        whiten_states=lambda x: x)
    series = rng.standard_normal(n_lib)
    indices = np.arange(2, n_lib - 10)
    library = AnalogLibrary(indices=indices, noisy_series=series,
                            tree=cKDTree(delay_vectors(series, indices, 1, 3)))
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
            return (np.full((len(flat), 2), 0.1), np.ones(len(flat)), state_bad, nu_bad)

    setup = ForecastSetup(ctx=ctx, noise=0.01, estimator=Stub(), model_step=None)
    setup._paths[h_last] = paths
    noise = np.random.default_rng(778).standard_normal((n_states, n_draws, 3))
    return setup, library, noise, np.arange(n_states)


def test_forecast_draws_handled_columns_per_state() -> None:
    """``forecast_draws`` fills ``handled`` per state from the estimator flags and the clip masks.

    Reference: hand-planned counts (a miniature world, stubbed estimator and PLP path, see
    ``_fake_world``). 4 states x 3 draws, horizons (1, 2, 3), H_ref = 2. Flat rows are
    state-major (row = 3 state + draw). State flags: rows 0 and 1 (state 0) and row 7 (state 2)
    have a replaced state; rows 7 (state 2) and 10 (state 3) a replaced nu. PLP error plan: row 0
    col 1 = +inf (non-finite at H_ref, state 0); row 1 col 1 = -25 (finite clip at H_ref, state
    0); row 1 col 0 = NaN (non-finite, not at H_ref); row 5 col 2 = 12 (finite clip, not at
    H_ref); row 9 col 1 = -10.0 exactly (not counted); row 10 col 1 = 11 (finite clip at H_ref,
    state 3). Expected ``handled`` rows, written out by hand: state 0 [2,0,0,0,1,1], state 1
    zeros, state 2 [1,1,0,0,0,0], state 3 [0,1,0,0,1,0]. Entry totals: non-finite 2, finite 3,
    CP 0 (CP errors are differences of unit normals). Exact integers. The PLP truth + diff - truth
    round trip is not bitwise, so the clipped values are checked to 1e-12 (u * 10 << 1e-12).
    """
    from lpcstudy.ensemble import DRAW_COUNTERS, forecast_draws

    n_states, n_draws, horizons = 4, 3, np.array([1, 2, 3])
    diff = np.zeros((12, 3))
    diff[0, 1], diff[1, 1], diff[1, 0], diff[5, 2], diff[9, 1], diff[10, 1] = \
        np.inf, -25.0, np.nan, 12.0, -10.0, 11.0
    state_bad = np.zeros(12, dtype=bool)
    state_bad[[0, 1, 7]] = True
    nu_bad = np.zeros(12, dtype=bool)
    nu_bad[[7, 10]] = True
    setup, library, noise, rows = _fake_world(diff, state_bad, nu_bad, horizons, n_states, n_draws)
    batch = forecast_draws(setup, library, "test", rows, noise, horizons, reference_horizon=2)
    expected = np.array([[2, 0, 0, 0, 1, 1], [0] * 6, [1, 1, 0, 0, 0, 0], [0, 1, 0, 0, 1, 0]])
    assert DRAW_COUNTERS == ("invariant_mean_replacements", "nu_replacements", "gain_replacements",
                             "gain_floor", "error_clips_plp_href", "error_clips_nonfinite_href")
    assert batch.handled.dtype == np.int64 and batch.handled.shape == (4, 6)
    np.testing.assert_array_equal(batch.handled, expected)
    assert batch.clip_entries == {"error_clips_cp": 0, "error_clips_plp": 3,
                                  "error_clips_nonfinite": 2}
    plp = batch.plp_err.reshape(12, 3)
    assert plp[0, 1] == 10.0 and plp[1, 1] == -10.0 and plp[1, 0] == 10.0 and plp[5, 2] == 10.0
    assert abs(plp[9, 1] - (-10.0)) < 1e-12 and plp[10, 1] == 10.0
    # Without a reference horizon the two H_ref columns are 0 and the others are unchanged.
    plain = forecast_draws(setup, library, "test", rows, noise, horizons)
    assert np.all(plain.handled[:, 4:] == 0)
    np.testing.assert_array_equal(plain.handled[:, :4], expected[:, :4])
    with pytest.raises(ValueError):
        forecast_draws(setup, library, "test", rows, noise, horizons, reference_horizon=7)


def test_sanitize_gains_a8_evaluation_path() -> None:
    """A8 (evaluation path): NaN and +inf are replaced by 1e300 and counted per draw; 0.0 is a floor.

    Reference: a hand array, window 4, 5 columns, 6 draws. Row 0: NaN inside the window. Row 1:
    +inf outside the window (column 4, still replaced: the whole array is the unit). Row 2: 0.0
    inside the window. Row 3: NaN and 0.0 (a replaced and floored draw; the NaN becomes 1e300
    and does not floor). Row 4: 0.0 outside the window (not floored). Row 5: NaN and +inf in one
    row (counts once: D5). Expected: replaced rows {0, 1, 3, 5} (4), floored rows {2, 3} (2),
    read off the construction. The replaced values equal 1e300 bitwise and every other entry is
    unchanged bitwise (the old line is ``np.nan_to_num(gains, nan=1e300, posinf=1e300)``).
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
    assert clean.tobytes() == np.nan_to_num(gains, nan=1e300, posinf=1e300).tobytes()
    assert clean[0, 3] == 1e300 and clean[1, 4] == 1e300 and clean[5, 1] == 1e300
    assert clean[2, 1] == 0.0 and clean[3, 2] == 0.0


class _StubLibrary:
    """Stands in for ``AnalogLibrary`` where only the shapes of the answers matter."""

    def __init__(self, dim: int) -> None:
        self.dim = dim

    def query(self, vectors: np.ndarray, n_analogs: int):
        return np.zeros((len(vectors), n_analogs), dtype=np.int64), np.zeros((len(vectors),
                                                                              n_analogs))

    def analog_vectors(self, lib_idx: np.ndarray) -> np.ndarray:
        return np.zeros((len(lib_idx), self.dim))


def _stubbed_forecasts(monkeypatch, handled_table: np.ndarray, entry_table: np.ndarray,
                       n_draws: int, n_hor: int, dim: int):
    """Monkeypatch ``forecast_draws`` to return planned errors, ``handled`` rows and entry totals.

    The estimated state of flat row ``r`` (global, state-major) is ``[r, 0]``, so a stubbed
    amplification function can look the planned gains up by row.
    """
    from lpcstudy import ensemble

    n_states = len(handled_table)
    rng = np.random.default_rng(31)
    cp = rng.standard_normal((n_states, n_draws, n_hor))
    plp = rng.standard_normal((n_states, n_draws, n_hor))
    flat_id = np.arange(n_states * n_draws, dtype=float).reshape(n_states, n_draws)
    est_states = np.stack([flat_id, np.zeros_like(flat_id)], axis=-1)

    def fake(setup, library, split, rows, unit_noise, horizons, reference_horizon=None):
        return ensemble.DrawBatch(
            cp_err=cp[rows], plp_err=plp[rows], analog_seed_sq=np.ones((len(rows), n_draws)),
            est_seed_sq=np.ones((len(rows), n_draws)), distance=np.ones((len(rows), n_draws)),
            inputs=unit_noise, est_states=est_states[rows], est_nu=np.ones((len(rows), n_draws)),
            analog_vecs=np.zeros((len(rows), n_draws, dim)), handled=handled_table[rows].copy(),
            clip_entries={name: int(entry_table[rows, i].sum())
                          for i, name in enumerate(ensemble.ENTRY_COUNTERS)})

    monkeypatch.setattr(ensemble, "forecast_draws", fake)
    return cp, plp


def _planned_tables(n_states: int, n_draws: int):
    rng = np.random.default_rng(91)
    handled = rng.integers(0, n_draws + 1, size=(n_states, 6)).astype(np.int64)
    handled[:, 2:4] = 0  # gain columns are filled by evaluation_draws only
    entries = rng.integers(0, 50, size=(n_states, 3)).astype(np.int64)
    return handled, entries


@pytest.mark.parametrize("chunk_traj", [4, 10**6])
def test_ensemble_moments_accumulates_handled_exactly_for_any_chunking(monkeypatch,
                                                                       chunk_traj: int) -> None:
    """A3 (oracle kind): ``handled`` and ``clip_entries`` equal the planned sums for any chunking.

    Reference: hand sums. ``forecast_draws`` is monkeypatched to return a planned per-state
    ``handled`` table and planned entry counts per state (random integers from
    ``np.random.default_rng(91)``); the expected result is the table itself (per state) and its
    column sums (totals). ``chunk_traj = 4`` with M = 4 draws gives one state per chunk,
    ``10**6`` puts all 7 states in one chunk. Exact integer equality in both cases.
    """
    from types import SimpleNamespace

    from lpcstudy.ensemble import ENTRY_COUNTERS, ensemble_moments

    n_states, n_draws, n_hor, dim = 7, 4, 3, 2
    handled, entries = _planned_tables(n_states, n_draws)
    _stubbed_forecasts(monkeypatch, handled, entries, n_draws, n_hor, dim)
    setup = SimpleNamespace(noise=0.01)
    noise = np.zeros((n_states, n_draws, dim))
    moments = ensemble_moments(setup, None, "test", noise, np.arange(1, n_hor + 1),
                               chunk_traj=chunk_traj, reference_horizon=2)
    np.testing.assert_array_equal(moments.handled, handled)
    assert moments.handled.dtype == np.int64
    assert moments.clip_entries == {name: int(entries[:, i].sum())
                                    for i, name in enumerate(ENTRY_COUNTERS)}
    part = moments.subset(np.array([5, 2]))
    np.testing.assert_array_equal(part.handled, handled[[5, 2]])
    assert part.clip_entries is None  # a view has no valid entry totals


@pytest.mark.parametrize("chunk_traj", [4, 10**6])
def test_evaluation_draws_accumulates_handled_and_gain_columns(monkeypatch,
                                                               chunk_traj: int) -> None:
    """A3 and A8 (evaluation kind): gain columns per state, other columns passed through, values kept.

    Reference: hand sums. 6 states x 4 draws, horizons (1, 3, 5), window 4 (5 gain columns).
    ``forecast_draws`` is monkeypatched (planned ``handled`` rows and entry counts, random
    integers from ``np.random.default_rng(91)``); the stubbed amplification returns a planned
    gain table with: flat row 2 (state 0) NaN in the window; row 5 (state 1) +inf outside the
    window; row 9 (state 2) 0.0 in the window; row 10 (state 2) NaN and 0.0; row 13 (state 3)
    0.0 outside the window; row 14 (state 3) NaN and +inf in one row. Expected
    ``gain_replacements`` per state [1, 1, 1, 1, 0, 0] and ``gain_floor`` [0, 0, 2, 0, 0, 0],
    read off the construction (D5: the row with both NaN and +inf counts once). Other columns
    equal the planned table. ``growth_proxy`` and ``gain_proxy`` equal the old expression
    (``nan_to_num`` then ``growth_exponent``) applied to the planned gains, bitwise. Exact.
    """
    from types import SimpleNamespace

    from lpcstudy.dynamics import growth_exponent
    from lpcstudy.ensemble import ENTRY_COUNTERS, evaluation_draws

    n_states, n_draws, dim, window = 6, 4, 2, 4
    horizons = np.array([1, 3, 5])
    handled, entries = _planned_tables(n_states, n_draws)
    _stubbed_forecasts(monkeypatch, handled, entries, n_draws, len(horizons), dim)
    gains = np.random.default_rng(5).uniform(0.5, 3.0, size=(n_states * n_draws, 5))
    gains[2, 3] = np.nan
    gains[5, 4] = np.inf
    gains[9, 1] = 0.0
    gains[10, 0], gains[10, 2] = np.nan, 0.0
    gains[13, 4] = 0.0
    gains[14, 1], gains[14, 3] = np.nan, np.inf
    amplification = lambda amp_steps: (lambda states: gains[np.asarray(states)[:, 0].astype(int)])
    setup = SimpleNamespace(noise=0.01, n_analogs=1, amplification=amplification)
    noise = np.zeros((n_states, n_draws, dim))
    verify = np.zeros((n_states, n_draws, 5))
    synth = np.zeros((n_states, n_draws, 3, dim))
    out = evaluation_draws(setup, _StubLibrary(dim), "test", noise, verify, horizons, window,
                           synth, chunk_traj=chunk_traj, reference_horizon=3)
    expected = handled.copy()
    expected[:, 2] = [1, 1, 1, 1, 0, 0]
    expected[:, 3] = [0, 0, 2, 0, 0, 0]
    np.testing.assert_array_equal(out.handled, expected)
    assert out.clip_entries == {name: int(entries[:, i].sum())
                                for i, name in enumerate(ENTRY_COUNTERS)}
    old = np.nan_to_num(gains, nan=1e300, posinf=1e300)
    assert out.growth_proxy.tobytes() == growth_exponent(old, window).reshape(
        n_states, n_draws).tobytes()
    assert out.gain_proxy.tobytes() == old[:, horizons - 1].reshape(n_states, n_draws, -1).tobytes()
    sub = out.subset(np.array([4, 0]))
    np.testing.assert_array_equal(sub.handled, expected[[4, 0]])
    assert sub.clip_entries is None


class _SpyTree:
    """A real ``cKDTree`` behind a recorder of the keyword arguments of ``query``."""

    def __init__(self, tree) -> None:
        self.tree = tree
        self.calls: list[dict] = []

    def query(self, *args, **kwargs):
        self.calls.append(dict(kwargs))
        return self.tree.query(*args, **kwargs)


def _synthetic_library():
    """A fixed 3000-vector library in R^5 (test seed 50120) and 40 query vectors."""
    from lpcstudy.ensemble import AnalogLibrary
    from scipy.spatial import cKDTree

    rng = np.random.default_rng(50120)
    vectors = rng.standard_normal((3000, 5))
    queries = rng.standard_normal((40, 5))
    tree = cKDTree(vectors)
    library = AnalogLibrary(indices=np.arange(3000) + 7, noisy_series=np.zeros(3007), tree=tree)
    return library, tree, queries


@pytest.mark.parametrize("value, expected", [(None, 4), ("", 4), ("1", 1), ("2", 2), ("8", 8),
                                             ("99", 99)])
def test_worker_count_reads_lpc_threads(monkeypatch, value, expected: int) -> None:
    """``worker_count`` is ``LPC_THREADS`` as an integer, 4 when unset or empty (DEF-0012).

    Reference: the rule of ``tools/run_tests.sh`` (``${LPC_THREADS:-4}``, integer 1 to 99),
    stated here as the table of expected values. Exact integer comparison: no tolerance.
    """
    from lpcstudy.ensemble import worker_count

    if value is None:
        monkeypatch.delenv("LPC_THREADS", raising=False)
    else:
        monkeypatch.setenv("LPC_THREADS", value)
    assert worker_count() == expected


@pytest.mark.parametrize("value", ["0", "-1", "abc", "100", "07", "2.5", " 4"])
def test_worker_count_rejects_invalid_values(monkeypatch, value: str) -> None:
    """Values outside the integers 1 to 99 raise ``ValueError`` naming ``LPC_THREADS`` (PRIME.4).

    Reference: the validation of ``tools/run_tests.sh`` (``^[1-9][0-9]?$``). There is no
    silent fallback to 4.
    """
    from lpcstudy.ensemble import worker_count

    monkeypatch.setenv("LPC_THREADS", value)
    with pytest.raises(ValueError, match="LPC_THREADS"):
        worker_count()


@pytest.mark.parametrize("value, expected", [(None, 4), ("2", 2), ("8", 8)])
def test_analog_query_passes_lpc_threads_as_workers(monkeypatch, value, expected: int) -> None:
    """``AnalogLibrary.query`` calls the tree with ``workers == LPC_THREADS`` (DEF-0012).

    Reference: the expected integer is the environment value set by the test (4 when unset).
    The spy forwards to a real ``cKDTree``, so the call is also valid. Exact comparison.
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
def test_analog_query_rejects_invalid_lpc_threads(monkeypatch, value: str) -> None:
    """``AnalogLibrary.query`` raises ``ValueError`` for an invalid ``LPC_THREADS`` and does
    not query the tree (no silent fallback, PRIME.4)."""
    library, tree, queries = _synthetic_library()
    spy = _SpyTree(tree)
    library.tree = spy
    monkeypatch.setenv("LPC_THREADS", value)
    with pytest.raises(ValueError, match="LPC_THREADS"):
        library.query(queries, 3)
    assert spy.calls == []


@pytest.mark.parametrize("threads", ["1", "4"])
def test_analog_query_is_bitwise_independent_of_workers(monkeypatch, threads: str) -> None:
    """Indices and distances are bitwise those of the same query with ``workers=1``.

    Reference: ``cKDTree.query(..., workers=1)`` on the same tree, with the library's
    position-to-time map applied by hand. Justification of the exact comparison: a k-d
    tree query is a deterministic search per query point; the worker count only splits
    the query points among threads and does not change any arithmetic, so the bytes are
    identical (a failure would mean a data race or a different code path, not round-off).
    """
    library, tree, queries = _synthetic_library()
    monkeypatch.setenv("LPC_THREADS", threads)
    indices, distances = library.query(queries, 5)
    ref_dist, ref_pos = tree.query(queries, k=5, workers=1)
    assert distances.tobytes() == ref_dist.tobytes()
    assert indices.tobytes() == (np.arange(3000) + 7)[ref_pos].tobytes()
