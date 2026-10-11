"""Tests for lpcstudy.analysis: per-state Spearman trend."""

from __future__ import annotations

import dataclasses
import json
import math

import numpy as np
import pytest
from scipy import stats as sps
from sklearn.tree import DecisionTreeRegressor

from lpcstudy.config import SMOKE
from lpcstudy.data import make_rng
from lpcstudy.ensemble import EnsembleMoments, EvaluationDraws
from lpcstudy.pipeline import Cell, RuleScores, SplitData
from lpcstudy.statistics import block_bootstrap, holm_adjust

LEVEL = 1.0 - 0.05 / 3.0  # the primary level of v3 section 7, written out again here
CONFIG = dataclasses.replace(SMOKE, bootstrap_resamples=200)  # 200 resamples, block 5


def _stub_cell(weights: np.ndarray, err_corr: np.ndarray | None = None,
               cp_constant: np.ndarray | None = None, plp_constant: np.ndarray | None = None
               ) -> Cell:
    """A cell whose test moments have ``w*(H_ref) = weights`` exactly (H_ref = 30, nH = 1).

    With ``E_P = w``, ``E_C = 1 - w`` and ``C = 0`` the curvature is 1 and ``w* = E_P / 1 = w``
    (exact for dyadic ``w``). ``err_corr`` and the masks, when given, are ``(n,)`` columns.
    """
    n = len(weights)
    zeros = np.zeros((n, 1))
    col = lambda a: None if a is None else np.asarray(a)[:, None]
    moments = EnsembleMoments(
        horizons=np.array([30]), mean_cp=zeros, mean_plp=zeros, sq_cp=(1.0 - weights)[:, None],
        sq_plp=weights[:, None], cross=zeros, analog_seed=np.ones(n), est_seed=np.ones(n),
        noise_sens=np.zeros(n), err_corr=col(err_corr), cp_constant=col(cp_constant),
        plp_constant=col(plp_constant))
    return Cell(system="lorenz63", noise=0.01, library_size=0, label="stub", setup=None,
                splits={"test": SplitData(moments, None)}, oracles={}, horizons=np.array([30]))


def _has_nan(obj: object) -> bool:
    """True if a NaN float occurs anywhere in a nested dict/list result."""
    if isinstance(obj, float):
        return math.isnan(obj)
    if isinstance(obj, dict):
        return any(_has_nan(v) for v in obj.values())
    if isinstance(obj, (list, tuple)):
        return any(_has_nan(v) for v in obj)
    return False


# Six states by the five library sizes (1000, 3162, 10000, 31623, 100000); every entry is a
# multiple of 1/8, so w* is exact in the stub cells and the means below are exact in binary.
SIZES = (1_000, 3_162, 10_000, 31_623, 100_000)
TABLE = np.array([[0.0, 0.125, 0.25, 0.375, 0.5],
                  [0.25, 0.25, 0.5, 0.5, 0.75],
                  [0.0, 0.0, 0.0, 0.125, 0.125],
                  [0.5, 0.625, 0.625, 0.75, 1.0],
                  [0.125, 0.25, 0.375, 0.375, 0.5],
                  [0.75, 0.75, 1.0, 1.0, 1.0]])


def _library_cells(table: np.ndarray, rhos: tuple[float, ...] = (0.01,)) -> dict:
    """Library sweep stub: the same weight table at every rho, one column per library size."""
    return {(rho, n): _stub_cell(table[:, j]) for rho in rhos for j, n in enumerate(SIZES)}


def test_per_state_spearman_handles_ties() -> None:
    """A state whose weight is clipped to 0 at every level has no trend (rho = 0).

    Reference: hand-derived values. A strictly increasing (decreasing) row has rank
    correlation +1 (-1) with the increasing levels. The all-tied row has an undefined
    correlation (zero rank variance); 0 is the documented convention of
    ``_per_state_spearman`` (analysis.py), not a mathematical value.
    Tolerance: ``np.allclose`` defaults (rtol 1e-5, atol 1e-8), unchanged. The
    expected values are exact and the computation is a few float64 operations on
    small integers and half-integers (round-off below 1e-15), so the defaults are
    far above round-off.
    """
    from lpcstudy.analysis import _per_state_spearman

    values = np.array([[0.0, 0.0, 0.0, 0.0], [0.1, 0.2, 0.3, 0.4], [0.4, 0.3, 0.2, 0.1]])
    rho = _per_state_spearman(np.array([1.0, 2.0, 3.0, 4.0]), values)
    assert np.allclose(rho, [0.0, 1.0, -1.0])


def test_per_state_spearman_partial_ties_and_non_monotone() -> None:
    """Average ranks for partial ties, and a non-monotone row.

    Reference: Spearman's rho as the Pearson correlation of ranks, worked by hand.
    Levels 1..4 have ranks 1..4, centered (-1.5, -0.5, 0.5, 1.5), sum of squares 5.
    Row [0, 0, 0.1, 0.2]: average ranks (1.5, 1.5, 3, 4), centered (-1, -1, 0.5, 1.5),
    sum of squares 4.5, cross sum 1.5 + 0.5 + 0.25 + 2.25 = 4.5, so
    rho = 4.5 / sqrt(4.5 * 5) = 3 / sqrt(10).
    Row [1, 3, 2, 4]: ranks (1, 3, 2, 4), centered (-1.5, 0.5, -0.5, 1.5), cross sum
    2.25 - 0.25 - 0.25 + 2.25 = 4, sum of squares 5, so rho = 4/5.
    Tolerance ``atol=1e-12``, ``rtol=0``: a handful of float64 operations on numbers
    of order 1 (error below 1e-15), so 1e-12 leaves three orders of magnitude.
    """
    from lpcstudy.analysis import _per_state_spearman

    values = np.array([[0.0, 0.0, 0.1, 0.2], [1.0, 3.0, 2.0, 4.0]])
    rho = _per_state_spearman(np.array([1.0, 2.0, 3.0, 4.0]), values)
    assert np.allclose(rho, [3.0 / np.sqrt(10.0), 0.8], rtol=0.0, atol=1e-12)


def test_h2d_is_the_in_distribution_part_only() -> None:
    """H2d has no shift part: ``pass`` equals ``in_distribution_pass`` and no shift key remains.

    Reference: hand calculation. With A4 per-state squared error exactly 1.05 (1.2) times A3's,
    the excess ``mean(A4)/mean(A3) - 1`` is 0.05 (0.2), so the 10% criterion (v1 and v3 H2d part
    (i), unchanged) passes (fails). The set of keys is the four written out below (WU-0002.1
    removed part (ii) and its three ``shift_*`` keys; DL: "H2d, part (ii) dropped").
    Tolerance ``abs=1e-12`` on the excess: two means and a quotient of float64 numbers of
    order 1 (relative round-off a few 1e-16, times about 6 operations), 1e-12 is a margin of
    three orders. The booleans and the key set are exact.
    """
    import pytest

    from lpcstudy.analysis import h2d_empirical_comparison
    from lpcstudy.config import SMOKE
    from lpcstudy.pipeline import RuleScores

    base = np.random.default_rng(7).uniform(1.0, 2.0, 60)

    def scores(factor: float) -> dict[str, RuleScores]:
        make = lambda e: RuleScores(mse=np.zeros(1), state_mse_ref=e, regret=np.zeros(1),
                                    agreement=0.0, km_median=0.0, rmst=0.0)
        return {"A3": make(base), "A4": make(factor * base)}

    for factor, excess, ok in ((1.05, 0.05, True), (1.2, 0.2, False)):
        out = h2d_empirical_comparison(scores(factor), SMOKE)
        assert set(out) == {"in_distribution_excess", "ci", "in_distribution_pass", "pass"}
        assert out["in_distribution_excess"] == pytest.approx(excess, abs=1e-12)
        assert out["pass"] is ok and out["in_distribution_pass"] is ok


# ---------------------------------------------------------------- WU-0002.7: H2b and H2e
def test_h2b_library_change_is_the_paired_mean_with_the_primary_interval() -> None:
    """H2b(ii) is the mean over states of ``w*(10^4) - w*(10^3)`` at rho = 1%, level 1 - 0.05/3.

    Reference: the six-state table ``TABLE`` (values in [0, 1], multiples of 1/8). Hand differences
    (column 10^4 minus column 10^3): 0.25, 0.25, 0, 0.125, 0.25, 0.25, sum 1.125, mean 0.1875.
    The interval is compared with ``statistics.block_bootstrap`` (the pre-existing, separately
    tested function) at the same generator ``make_rng(seed, "h2b-library-change", "0.01")``, 200
    resamples, block 5, level 1 - 0.05/3, by exact equality (the counted helper is bitwise equal
    without failed resamples). Six states are below the 50-state minimum of DEC-0008 A3, so the
    verdict is inconclusive with that reason (pass False).
    Tolerance: mean ``abs=1e-12`` (the stub weights are exact, the mean is one division).
    """
    from lpcstudy.analysis import h2b_knob_response

    noise_cells = {0.01: _stub_cell(TABLE[:, 2]), 0.02: _stub_cell(np.minimum(TABLE[:, 2] + 0.125, 1.0))}
    out = h2b_knob_response(noise_cells, _library_cells(TABLE), CONFIG)
    change = out["library_change"]
    assert change["mean_change"] == pytest.approx(0.1875, abs=1e-12)
    assert change["level"] == LEVEL and change["n_states"] == 6 and change["rho"] == 0.01
    diff = TABLE[:, 2] - TABLE[:, 0]
    reference = block_bootstrap(lambda idx: float(np.mean(diff[idx])), 6, 200, 5,
                                make_rng(CONFIG.seed, "h2b-library-change", "0.01"), LEVEL)
    assert change["ci"] == [reference[1], reference[2]]
    assert change["pass"] is False and change["inconclusive_reason"] == "n_states < 50"
    assert change["n_failed_resamples"] == 0 and change["n_zero_difference"] == 1
    assert "fail" not in change and "fail" not in out
    assert out["pass"] is False and out["inconclusive_reason"] == "n_states < 50"


def test_regression_h2b_noise_part_keeps_salt_three() -> None:
    """The noise part of H2b is unchanged: salt 3, level 1 - 0.05/3 (a regression guard).

    Reference: ``statistics.block_bootstrap`` of the mean of the per-state Spearman correlation
    (hand values: states whose weight rises with rho have +1, a flat state 0) at seed
    ``config.seed + 3``. This is a regression guard on the pre-existing statistic, not new
    correctness evidence. Exact equality (same function, same seed).
    """
    from lpcstudy.analysis import h2b_knob_response

    low = np.array([0.0, 0.125, 0.25, 0.5, 0.5, 0.75])
    high = np.array([0.125, 0.25, 0.5, 0.625, 0.5, 0.875])
    out = h2b_knob_response({0.01: _stub_cell(low), 0.02: _stub_cell(high)},
                            _library_cells(TABLE), CONFIG)["noise"]
    per_state = np.array([1.0, 1.0, 1.0, 1.0, 0.0, 1.0])  # Spearman with two levels: sign of the change
    reference = block_bootstrap(lambda idx: float(np.mean(per_state[idx])), 6, 200, 5,
                                CONFIG.seed + 3, LEVEL)
    assert out["mean_state_spearman"] == pytest.approx(5.0 / 6.0, abs=1e-12)
    assert out["ci"] == [reference[1], reference[2]]


def test_h2b_library_change_passes_on_a_clear_rise_and_not_on_zero_or_missing() -> None:
    """With 60 states the strict lower bound > 0 decides; zero change and missing cells do not pass.

    Reference: hand-built outcomes. (a) The six-state table tiled ten times (60 states): every
    difference is >= 0, and any 5 consecutive differences of the period-6 pattern sum to at least
    1.125 - 0.25 = 0.875 (the total less the largest), so every block mean and hence every
    resample mean is at least 0.175 and the lower bound is above 0: pass True, reason None. (b) Identical columns for 10^3 and 10^4: every
    resample mean is exactly 0.0, the interval is [0, 0], which is not above 0 (strict;
    DEC-0008 A1) and lies entirely below the open band: pass False and, since this is a fail and
    not an inconclusive, ``inconclusive_reason`` is None. (c) The 10^3 cell missing at rho = 1%:
    ``mean_change`` None, ``ci`` None, pass False, the reason names the cell, and the result has no
    NaN. Exact comparisons of booleans, None and strings.
    """
    from lpcstudy.analysis import h2b_knob_response

    noise_cells = {0.01: _stub_cell(np.tile(TABLE[:, 2], 10)),
                   0.02: _stub_cell(np.tile(np.minimum(TABLE[:, 2] + 0.125, 1.0), 10))}
    tiled = np.tile(TABLE, (10, 1))
    out = h2b_knob_response(noise_cells, _library_cells(tiled), CONFIG)["library_change"]
    assert out["pass"] is True and out["inconclusive_reason"] is None and out["ci"][0] > 0.0
    assert out["mean_change"] == pytest.approx(0.1875, abs=1e-12)

    flat = tiled.copy()
    flat[:, 2] = flat[:, 0]
    out = h2b_knob_response(noise_cells, _library_cells(flat), CONFIG)["library_change"]
    assert out["mean_change"] == 0.0 and out["ci"] == [0.0, 0.0]
    assert out["pass"] is False and out["inconclusive_reason"] is None

    cells = _library_cells(tiled)
    del cells[(0.01, 1_000)]
    result = h2b_knob_response(noise_cells, cells, CONFIG)
    out = result["library_change"]
    assert out["mean_change"] is None and out["ci"] is None and out["pass"] is False
    assert "rho=0.01 n_lib=1000" in out["inconclusive_reason"]
    assert result["pass"] is False and not _has_nan(result)
    json.dumps(result, allow_nan=False)


def test_h2b_curves_and_the_reported_change_at_two_percent() -> None:
    """The M2 curves hold the mean and median of w* per library size; the 2% change is reported.

    Reference: ``np.mean`` and ``np.median`` of each table column (independent of the code, which
    takes them inside the bootstrap statistic), ``abs=1e-12`` (one reduction of exact binary
    fractions). Every size has a 2-element interval at level 0.95 with ``lo <= hi``. The change at
    rho = 2% (same table) is the hand mean 0.1875 at level 0.95, role "reported", and equals
    ``block_bootstrap`` at ``make_rng(seed, "h2b-library-change", "0.02")`` exactly. The library
    Spearman keys of v1 and the saturation rule are gone.
    """
    from lpcstudy.analysis import h2b_knob_response

    noise_cells = {0.01: _stub_cell(TABLE[:, 2]), 0.02: _stub_cell(np.minimum(TABLE[:, 2] + 0.125, 1.0))}
    out = h2b_knob_response(noise_cells, _library_cells(TABLE, (0.01, 0.02)), CONFIG)
    assert set(out["library_curves"]) == {"0.01", "0.02"}
    for rho in ("0.01", "0.02"):
        curve = out["library_curves"][rho]
        assert list(curve) == [str(n) for n in SIZES]
        for j, n in enumerate(SIZES):
            entry = curve[str(n)]
            assert entry["mean"] == pytest.approx(np.mean(TABLE[:, j]), abs=1e-12)
            assert entry["median"] == pytest.approx(np.median(TABLE[:, j]), abs=1e-12)
            assert len(entry["mean_ci"]) == len(entry["median_ci"]) == 2
            assert entry["mean_ci"][0] <= entry["mean_ci"][1] and entry["level"] == 0.95
    reported = out["library_change_reported"]
    assert set(reported) == {"0.02"} and reported["0.02"]["role"] == "reported"
    assert reported["0.02"]["mean_change"] == pytest.approx(0.1875, abs=1e-12)
    diff = TABLE[:, 2] - TABLE[:, 0]
    reference = block_bootstrap(lambda idx: float(np.mean(diff[idx])), 6, 200, 5,
                                make_rng(CONFIG.seed, "h2b-library-change", "0.02"), 0.95)
    assert reported["0.02"]["ci"] == [reference[1], reference[2]] and reported["0.02"]["level"] == 0.95
    assert "pass" not in reported["0.02"]
    assert "library" not in out and "median_at_largest_n_lib" not in json.dumps(out)


def _h2e_cells(low: np.ndarray, high: np.ndarray, rhos=(0.01, 0.02), cp_low=None) -> dict:
    """Library cells for H2e: correlation ``low`` at 10^3, ``high`` at 10^5 (and 0.5 at 10^4)."""
    n = len(low)
    none = np.zeros(n, dtype=bool)
    cells = {}
    for rho in rhos:
        for size, corr, cp in ((1_000, low, cp_low if cp_low is not None else none),
                               (10_000, np.full(n, 0.5), none), (100_000, high, none)):
            cells[(rho, size)] = _stub_cell(np.full(n, 0.5), corr, cp, none)
    return cells


def test_h2e_median_change_with_a_cp_constant_state_and_the_counts() -> None:
    """H2e: the median of per-state correlation changes, with the zero-variance counts reported.

    Reference: a hand-built table of 50 states. Correlation at 10^3: ``i/100`` for state ``i``
    (0.00 to 0.49), except state 7, which is CP-constant and has correlation 0.0 exactly (as
    ``draw_correlation`` sets it). Change ``d_i = 0.25 + 0.01 (i mod 5)`` for every state, so
    ``high = low + d``; ten states each have 0.25, 0.26, 0.27, 0.28, 0.29, and the median of the 50
    values is the mean of the 25th and 26th sorted values, both 0.27. The CP-constant state keeps
    its change (its correlation at 10^5 is 0 + d_7). Expected: median change 0.27 (``abs=1e-12``:
    one subtraction of numbers of order 1 per state), pass True at both rho (every resample median
    is at least 0.25 > 0), ``zero_variance_corr`` shows exactly one CP-constant state at 10^3
    (rho = 1% and 2%) and none at 10^5, and the interval equals ``block_bootstrap`` of the median
    at ``make_rng(seed, "h2e", "0.01")``, level 0.95, exactly.
    """
    from lpcstudy.analysis import h2e_noise_matching

    n = 50
    idx = np.arange(n)
    low = idx / 100.0
    low[7] = 0.0
    delta = 0.25 + 0.01 * (idx % 5)
    cp_low = np.zeros(n, dtype=bool)
    cp_low[7] = True
    out = h2e_noise_matching(_h2e_cells(low, low + delta, cp_low=cp_low), CONFIG)
    for rho in ("0.01", "0.02"):
        entry = out["by_noise"][rho]
        assert entry["median_change"] == pytest.approx(0.27, abs=1e-12)
        assert entry["pass"] is True and entry["inconclusive_reason"] is None
        assert entry["level"] == 0.95 and entry["n_states"] == 50
        assert out["zero_variance_corr"][rho]["1000"] == {
            "cp_constant": 1, "plp_constant": 0, "both_constant": 0, "n_nonfinite": 0,
            "n_states": 50}
        assert out["zero_variance_corr"][rho]["100000"]["cp_constant"] == 0
        assert out["corr_curve"][rho]["1000"] == pytest.approx(np.median(low), abs=1e-12)
        assert out["corr_curve"][rho]["10000"] == 0.5
    diff = (low + delta) - low
    reference = block_bootstrap(lambda i: float(np.median(diff[i])), 50, 200, 5,
                                make_rng(CONFIG.seed, "h2e", "0.01"), 0.95)
    assert out["by_noise"]["0.01"]["ci"] == [reference[1], reference[2]]
    assert out["pass"] is True and out["inconclusive_reason"] is None and not _has_nan(out)


def test_h2e_no_change_is_not_a_pass_and_missing_cells_are_named() -> None:
    """A median change of exactly 0 is not a pass (strict); missing 10^5 or 2% cells are named.

    Reference: hand-built outcomes. (a) ``high == low`` at both rho: every resample median is 0,
    the interval is [0, 0], not above 0 and entirely below the open band: pass False, reason None
    (a fail, not an inconclusive), ``n_zero_difference`` = 50. (b) The ``SMOKE`` library sweep (no
    10^5, no rho = 2%): both rho are missing, ``median_change`` None, ``ci`` None, pass False, the
    reason names n_lib=100000 at rho=0.01 and rho=0.02, and the dict has no NaN. (c) Moments
    without ``err_corr`` raise ``ValueError``. Exact.
    """
    from lpcstudy.analysis import h2e_noise_matching

    low = np.linspace(0.0, 0.4, 50)
    out = h2e_noise_matching(_h2e_cells(low, low.copy()), CONFIG)
    assert out["pass"] is False and out["inconclusive_reason"] is None
    assert out["by_noise"]["0.01"]["ci"] == [0.0, 0.0]
    assert out["by_noise"]["0.01"]["n_zero_difference"] == 50

    smoke = {(0.01, 1_000): _stub_cell(np.full(50, 0.5), low, np.zeros(50, dtype=bool),
                                       np.zeros(50, dtype=bool)),
             (0.01, 10_000): _stub_cell(np.full(50, 0.5), low, np.zeros(50, dtype=bool),
                                        np.zeros(50, dtype=bool))}
    out = h2e_noise_matching(smoke, SMOKE)
    for rho in ("0.01", "0.02"):
        assert out["by_noise"][rho]["median_change"] is None and out["by_noise"][rho]["ci"] is None
        assert out["by_noise"][rho]["pass"] is False
    assert "rho=0.01 n_lib=100000" in out["by_noise"]["0.01"]["inconclusive_reason"]
    assert "rho=0.02 n_lib=1000" in out["by_noise"]["0.02"]["inconclusive_reason"]
    assert out["pass"] is False and "rho=0.02" in out["inconclusive_reason"] and not _has_nan(out)
    json.dumps(out, allow_nan=False)

    with pytest.raises(ValueError, match="err_corr"):
        h2e_noise_matching({(0.01, 1_000): _stub_cell(np.full(50, 0.5))}, SMOKE)


# ---------------------------------------------------------------- WU-0002.8: H3a
def _regime_data(hazards: tuple[float, ...], n_each: int, seed: int
                 ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """First-draw regime labels, geometric durations (all events) and a linear horizon target."""
    rng = np.random.default_rng(seed)
    regime = np.repeat(np.arange(len(hazards)), n_each)
    durations = np.concatenate([rng.geometric(h, n_each) for h in hazards])
    target = np.concatenate([np.arange(n_each) * (k + 1.0) for k in range(len(hazards))])
    return regime, durations, target


def test_h3a_holm_and_raw_p_match_independent_references() -> None:
    """H3a on three separated regimes: scipy raw p, hand Holm, pass, stable order, IQR.

    Reference: three regimes of 60 states with geometric hazards 0.05, 0.45, 0.15 (labels 0, 1,
    2; no censoring), from ``np.random.default_rng(3)``. The Kaplan-Meier medians given to the
    function are 14, 2, 5 steps, so the test order is regime 1, 2, 0 and the pairs are (1, 2)
    and (2, 0). Raw p: ``scipy.stats.logrank`` on each pair, ``rel=1e-10`` (the tolerance of
    ``test_logrank_matches_scipy``: the two codes sum per-time terms in a different order, p
    about 1e-4 to 1e-15 here). Holm for two p-values by hand: adjusted ``min(1, 2 p_small)`` and
    ``max(that, p_large)``, ``atol=1e-15`` (one multiplication and a comparison); and equal to
    ``holm_adjust`` exactly. ``pass`` is True because both adjusted p are below 0.01 (asserted
    from the scipy p as a premise). The horizon target of regime ``k`` is ``arange(60) (k+1)``
    steps, whose interquartile range is 29.5 (k+1) steps (linear interpolation: 44.25 - 14.75),
    so ``iqr_lt`` is 29.5 (k+1)/30 (``abs=1e-12``, a few operations on numbers of order 1) and
    ``iqr_lt_mean`` their size-weighted mean (equal sizes: the plain mean). There is no key with
    "regret" or "fail" in it, and no ``iqr_pass`` (D-08, DEC-0008 A3).
    """
    from lpcstudy.analysis import h3a_logrank

    regime, durations, target = _regime_data((0.05, 0.45, 0.15), 60, 3)
    events = np.ones(len(durations), dtype=bool)
    out = h3a_logrank(regime, durations, events, np.array([14.0, 2.0, 5.0]), target, 30, 3)
    assert out["pairs"] == [[1, 2], [2, 0]] and out["chosen_K"] == 3
    raw = [sps.logrank(durations[regime == a], durations[regime == b]).pvalue
           for a, b in ((1, 2), (2, 0))]
    assert all(p < 0.005 for p in raw)  # premise: both pairs clearly separated
    assert out["logrank_p_raw"] == pytest.approx(raw, rel=1e-10)
    small, large = sorted(out["logrank_p_raw"])
    first = min(1.0, 2 * small)
    hand = {small: first, large: max(first, large)}
    assert out["logrank_p_holm"] == pytest.approx([hand[p] for p in out["logrank_p_raw"]],
                                                  rel=0, abs=1e-15)
    assert out["logrank_p_holm"] == holm_adjust(out["logrank_p_raw"])
    assert out["pass"] is True and out["inconclusive_reason"] is None
    assert out["n_per_regime"] == [60, 60, 60]
    assert out["iqr_lt"] == pytest.approx([29.5 * (k + 1) / 30 for k in range(3)], abs=1e-12)
    assert out["iqr_lt_mean"] == pytest.approx(29.5 * 2 / 30, abs=1e-12)
    assert not any("regret" in key or "fail" in key or key == "iqr_pass" for key in out)


def test_h3a_inconclusive_paths_and_small_regimes() -> None:
    """H3a is inconclusive, never a fail, when a pair is not separated, empty or degenerate.

    Reference: hand-built situations. (a) Two regimes with the same hazard (0.1; 60 states each,
    seed 5): the raw p is the scipy p (large; premise p > 0.01), the Holm p equals it, and the
    result is pass False with a reason naming the largest Holm p. (b) Regime 1 has no state (labels
    0 and 2 only, K = 3): the pair containing it has raw p None, enters Holm at 1, pass False
    with reason "empty regime". (c) Two regimes in which no event occurs (all censored): the
    log-rank variance is 0, raw p None (not 1.0), reason "zero log-rank variance". (d) DEC-0011
    O1: regimes of 20 states each, hazards 0.5 and 0.05, are not rejected for size: pass True when
    scipy's p is below 0.01 (premise). (e) One regime: no pair, inconclusive. All results have the
    keys ``pass`` and ``inconclusive_reason`` and no ``fail`` key. Exact comparisons.
    """
    from lpcstudy.analysis import h3a_logrank

    regime, durations, target = _regime_data((0.1, 0.1), 60, 5)
    ones = np.ones(len(durations), dtype=bool)
    p_same = sps.logrank(durations[regime == 0], durations[regime == 1]).pvalue
    assert p_same > 0.01  # premise
    out = h3a_logrank(regime, durations, ones, np.array([7.0, 8.0]), target, 30, 2)
    assert out["pass"] is False and "largest Holm-adjusted p" in out["inconclusive_reason"]
    assert out["logrank_p_holm"] == pytest.approx([p_same], rel=1e-10)

    regime3 = np.where(regime == 1, 2, 0)
    out = h3a_logrank(regime3, durations, ones, np.array([5.0, 6.0, 7.0]), target, 30, 3)
    assert out["pairs"] == [[0, 1], [1, 2]] and out["logrank_p_raw"] == [None, None]
    assert out["logrank_p_holm"] == [1.0, 1.0] and out["pass"] is False
    assert "empty regime" in out["inconclusive_reason"]
    assert out["n_per_regime"] == [60, 0, 60] and out["iqr_lt"][1] is None

    out = h3a_logrank(regime, durations, np.zeros(len(durations), dtype=bool),
                      np.array([7.0, 8.0]), target, 30, 2)
    assert out["logrank_p_raw"] == [None] and out["logrank_p_holm"] == [1.0]
    assert out["pass"] is False and "zero log-rank variance" in out["inconclusive_reason"]

    small_regime, small_dur, small_target = _regime_data((0.5, 0.05), 20, 8)
    small = h3a_logrank(small_regime, small_dur, np.ones(40, dtype=bool), np.array([2.0, 14.0]),
                        small_target, 30, 2)
    assert sps.logrank(small_dur[:20], small_dur[20:]).pvalue < 0.01  # premise
    assert small["pass"] is True and small["n_per_regime"] == [20, 20]

    one = h3a_logrank(np.zeros(10, dtype=int), durations[:10], ones[:10], np.array([5.0]),
                      target[:10], 30, 1)
    assert one["pass"] is False and "fewer than two regimes" in one["inconclusive_reason"]
    assert one["pairs"] == [] and one["logrank_p_holm"] == []
    for result in (out, small, one):
        assert "fail" not in result and {"pass", "inconclusive_reason"} <= set(result)


def test_h3a_orders_tied_and_missing_horizons_by_regime_index() -> None:
    """Regimes with equal (or missing) Kaplan-Meier medians are ordered by regime index (DEF-0013).

    Reference: the documented rule (``np.argsort(kind="stable")`` with NaN mapped to infinity, ties
    by index), written out by hand: medians [7, 7, 3, 7, nan, 7, nan] give the order 2, 0, 1, 3, 5,
    4, 6, hence the consecutive pairs below. NumPy's default sort is not stable on tied arrays on
    some CPUs (the defect), so the expected pairs are fixed by hand, not computed. The data are
    7 regimes of 5 states with identical durations (the p-values are irrelevant; only the pairs are
    checked). Exact.
    """
    from lpcstudy.analysis import h3a_logrank

    regime = np.repeat(np.arange(7), 5)
    out = h3a_logrank(regime, np.arange(1, 36), np.ones(35, dtype=bool),
                      np.array([7.0, 7.0, 3.0, 7.0, np.nan, 7.0, np.nan]), np.ones(35), 30, 7)
    assert out["pairs"] == [[2, 0], [0, 1], [1, 3], [3, 5], [5, 4], [4, 6]]
    assert out["n_km_not_reached"] == 2  # the two NaN medians are counted, not hidden


# ---------------------------------------------------------------- WU-0002.8: H3b
def _h3b_data(seed: int, n: int = 600):
    """Profile ``(n, 2, 4)`` with ``x`` drawn per state and repeated over the 2 draws, and weights.

    The curvature weights are integers 1..4 and the profile is uniform on [0, 1]^4, from
    ``np.random.default_rng(seed)``. Column 2 is ``lambda_tilde``.
    """
    rng = np.random.default_rng(seed)
    x = rng.uniform(size=(n, 4))
    curvature = rng.integers(1, 5, n).astype(float)
    return x, np.repeat(x[:, None, :], 2, axis=1), curvature


def test_h3b_known_ordering_lambda_irrelevant_for_the_weight_and_first_for_the_horizon() -> None:
    """H3b passes where ``Lambda_tilde`` is irrelevant to the weight and dominates the horizon.

    Reference: manufactured truth, 600 states x 2 draws, ``x ~ U[0, 1]^4`` drawn per state and
    repeated over its draws (the targets are per state). Column 2 is Lambda_tilde. Weight
    ``w* = 0.5 1{x0 > 0.5} + 0.25 1{x1 > 0.3}`` (dyadic, depends on x0 and x1 only), curvature
    weights integers 1..4, ``ln T = 3 x2 + 0.5 x0``. After the splits on x0 and x1 every leaf of
    the weight tree is pure with an exactly zero impurity (dyadic values and integer weights make
    the leaf mean and squared mean exact), so no split on x2 can improve it: the importance of
    Lambda_tilde is exactly 0.0 in the full fit and in every resample, and the interval is
    [0.0, 0.0], inside the band [0, 0.2). In the horizon tree the first three splits are on x2
    (impurity decrease 0.703 of 0.771 of the total, a 9-fold margin over any x0 split, which
    gains at most 0.0039), so ``D`` is about 0.96 and positive in every resample: stability is
    exactly 1.0 and the lower bound of D is at least 0.9 (the plan's bound; the applied-
    mathematician observed at least 0.982 over 8 seeds). The tolerances are exact equalities for
    the zeros and ``>= 0.9`` for D, fixed before the run.
    """
    from lpcstudy.analysis import h3b_importances

    x, profile, curvature = _h3b_data(31)
    w_star = 0.5 * (x[:, 0] > 0.5) + 0.25 * (x[:, 1] > 0.3)
    log_t = 3.0 * x[:, 2] + 0.5 * x[:, 0]
    out = h3b_importances(profile, w_star, curvature, log_t, CONFIG)
    weight = out["weight_lambda"]
    assert weight["importance"] == 0.0 and weight["ci"] == [0.0, 0.0]
    assert weight["pass"] is True and weight["n_failed_resamples"] == 0
    assert out["stability"] == 1.0 and out["D"]["ci"][0] >= 0.9 and out["D"]["value"] >= 0.9
    assert out["D"]["pass"] is True and out["pass"] is True and out["inconclusive_reason"] is None
    assert out["degenerate_fits"] == {"weight_tree": 0, "horizon_tree": 0,
                                      "full_data": {"weight_tree": False, "horizon_tree": False}}
    assert out["nan_resamples"] == 0 and out["max_leaf_nodes"] == 8 and out["n_resamples"] == 200


def test_h3b_reversed_ordering_fails_both_parts() -> None:
    """With Lambda_tilde carrying the weight and not the horizon, both parts fail.

    Reference: manufactured truth on the data of the previous test with the roles reversed:
    ``w* = 0.5 1{x2 > 0.5}`` (so the weight tree's only split is on Lambda_tilde = x2) and
    ``ln T = 3 x0 + 0.5 x2`` (x0 dominates the horizon tree). The weight importance of x2 is then
    exactly 1.0 in every resample (a single feature carries all the impurity decrease, 1.0 / 1.0),
    so the interval is [1.0, 1.0] (the plan asked for >= 0.2; tightened by the applied-
    mathematician, who verified it), which misses the band [0, 0.2): ``pass`` False and, as a fail,
    no inconclusive reason. D is about -0.95, so its upper bound is at most -0.9 (observed at most
    -0.978 over 8 seeds), stability is exactly 0.0, and the combined result is not a pass.
    """
    from lpcstudy.analysis import h3b_importances

    x, profile, curvature = _h3b_data(31)
    out = h3b_importances(profile, 0.5 * (x[:, 2] > 0.5), curvature,
                          3.0 * x[:, 0] + 0.5 * x[:, 2], CONFIG)
    assert out["weight_lambda"]["importance"] == 1.0 and out["weight_lambda"]["ci"] == [1.0, 1.0]
    assert out["weight_lambda"]["pass"] is False
    assert out["D"]["ci"][1] <= -0.9 and out["stability"] == 0.0 and out["D"]["pass"] is False
    assert out["pass"] is False and out["inconclusive_reason"] is None


def test_h3b_construction_leaf_count_row_expansion_and_point_fit() -> None:
    """The trees have 8 leaves, a state's draws stay together, and the point fit is the plain fit.

    Reference: (a) the estimator parameters, read from ``DecisionTreeRegressor.max_leaf_nodes``.
    (b) The state-to-row expansion of the states [2, 0] at 3 draws each is rows
    [6, 7, 8, 0, 1, 2] (state i owns rows 3i..3i+2), worked by hand. (c) The reported full-data
    importances equal those of a ``DecisionTreeRegressor(max_leaf_nodes=8, random_state=seed)``
    fitted in the test on the flattened rows, with the curvature as sample weight for the weight
    tree (scikit-learn is the independent implementation), by exact equality: both fits run
    the same deterministic algorithm on identical inputs (the seed 20261005 is below 2**32, so
    ``sklearn_seed`` is the identity).
    """
    from lpcstudy.analysis import PROFILE_NAMES, _h3b_trees, _state_rows, h3b_importances

    tree_w, tree_t = _h3b_trees(CONFIG.seed)
    assert tree_w.max_leaf_nodes == tree_t.max_leaf_nodes == 8
    assert _state_rows(np.array([2, 0]), 3).tolist() == [6, 7, 8, 0, 1, 2]

    x, profile, curvature = _h3b_data(32, n=200)
    w_star = 0.5 * (x[:, 0] > 0.5) + 0.25 * (x[:, 1] > 0.3) + 0.0625 * (x[:, 3] > 0.9)
    log_t = 3.0 * x[:, 2] + 0.5 * x[:, 0] + 0.1 * x[:, 1]
    out = h3b_importances(profile, w_star, curvature, log_t, CONFIG)
    flat = profile.reshape(-1, 4)
    ref_w = DecisionTreeRegressor(max_leaf_nodes=8, random_state=CONFIG.seed).fit(
        flat, np.repeat(w_star, 2), sample_weight=np.repeat(curvature, 2))
    ref_t = DecisionTreeRegressor(max_leaf_nodes=8, random_state=CONFIG.seed).fit(
        flat, np.repeat(log_t, 2))
    assert [out["weight_tree_importance"][n] for n in PROFILE_NAMES] == \
        ref_w.feature_importances_.tolist()
    assert [out["horizon_tree_importance"][n] for n in PROFILE_NAMES] == \
        ref_t.feature_importances_.tolist()
    assert ref_t.get_n_leaves() == 8


def test_h3b_degenerate_fits_are_counted_failed_resamples_and_not_zeros() -> None:
    """A single-leaf tree has no importance: NaN in a resample (counted), inconclusive if full-data.

    Reference: (a) a constant ``w*``: the full-data weight tree has one leaf (checked with the
    independent scikit-learn fit's ``get_n_leaves() == 1`` as a premise), so the weight part is
    "not computable" (importance None, pass False, reason naming the degenerate full-data fit),
    ``degenerate_fits.weight_tree`` equals the number of resamples (200: every resample is
    constant too), ``nan_resamples`` is 200, and the whole result is not a pass. (b) A weight
    target that is non-zero only on states 20..24 (60 states): a resample whose blocks miss all
    five states has a constant target and a single-leaf tree. The expected number of such
    resamples is replayed with ``block_resample_indices`` on the same generator (an independent
    use of the tested helper), and must equal ``degenerate_fits.weight_tree`` and the weight
    interval's ``n_failed_resamples``. (c) A constant ``ln T`` makes D not computable and
    stability 0.0. Exact comparisons.
    """
    from lpcstudy.analysis import h3b_importances
    from lpcstudy.statistics import block_resample_indices

    x, profile, curvature = _h3b_data(33, n=60)
    log_t = 3.0 * x[:, 2] + 0.5 * x[:, 0]
    constant = np.full(60, 0.5)
    assert DecisionTreeRegressor(max_leaf_nodes=8).fit(
        profile.reshape(-1, 4), np.repeat(constant, 2)).get_n_leaves() == 1  # premise
    out = h3b_importances(profile, constant, curvature, log_t, CONFIG)
    weight = out["weight_lambda"]
    assert weight["importance"] is None and weight["pass"] is False
    assert "degenerate full-data fit" in weight["inconclusive_reason"]
    assert out["degenerate_fits"]["weight_tree"] == 200 and out["nan_resamples"] == 200
    assert out["degenerate_fits"]["full_data"] == {"weight_tree": True, "horizon_tree": False}
    assert out["weight_tree_importance"]["lambda_tilde"] is None
    assert out["pass"] is False and not _has_nan(out)

    sparse = np.zeros(60)
    sparse[20:25] = 0.5
    out = h3b_importances(profile, sparse, curvature, log_t, CONFIG)
    expected = sum(not np.isin(idx, np.arange(20, 25)).any() for idx in block_resample_indices(
        60, 200, 5, make_rng(CONFIG.seed, "h3b-bootstrap")))
    assert expected > 0  # premise: the replay finds resamples that miss all five states
    assert out["degenerate_fits"]["weight_tree"] == expected
    assert out["weight_lambda"]["n_failed_resamples"] == expected
    assert out["degenerate_fits"]["full_data"]["weight_tree"] is False

    out = h3b_importances(profile, 0.5 * (x[:, 0] > 0.5), curvature, constant, CONFIG)
    assert out["D"]["value"] is None and out["D"]["pass"] is False
    assert "degenerate full-data fit" in out["D"]["inconclusive_reason"]
    assert out["stability"] == 0.0 and out["degenerate_fits"]["horizon_tree"] == 200


# ---------------------------------------------------------------- WU-0002.8: H3c, H2c, wiring
def test_h3c_ratio_of_means_paired_resampling_and_closed_bound() -> None:
    """H3c is ``mean(A5) / mean(A4)`` with one index array, level 1 - 0.05/3, pass iff hi <= 1.05.

    Reference: (a) hand ratios: A5 = A4 gives exactly 1 in every resample (x / x = 1 in IEEE),
    so ``ci == [1, 1]`` and pass; A5 = 1.2 A4 gives 1.2 in every resample to within a few
    ulp, ``ci == [1.2, 1.2]`` to 1e-12 and no pass (the bound 1.2 exceeds 1.05). (b) A random
    pair (60 states, ``default_rng(21)``, A4 uniform on [1, 2], A5 = A4 (1 + 0.1 u) with u
    uniform): the point ratio equals ``np.mean(a5) / np.mean(a4)`` (abs 1e-12) and the
    interval equals ``statistics.block_bootstrap`` of the ratio at
    ``make_rng(seed, "h3c-ratio")``, level 1 - 0.05/3, exactly (the same index array in the
    numerator and the denominator). (c) The closed bound: a ratio interval whose upper
    bound is exactly 1.05 passes; this is tested through the verdict helper
    ``criterion_verdict``, which has its own tests, by the resample-constant case A5 = 1.05 A4 only up to
    round-off, so it is not asserted exactly. (d) Fewer than 50 states: pass False with the
    reason "n_states < 50".
    """
    from lpcstudy.analysis import h3c_ratio

    rng = np.random.default_rng(21)
    a4 = rng.uniform(1.0, 2.0, 60)
    same = h3c_ratio(a4, a4, CONFIG)
    assert same["ci"] == [1.0, 1.0] and same["A5_over_A4_mse"] == 1.0
    assert same["pass"] is True and same["inconclusive_reason"] is None
    assert same["level"] == LEVEL and same["n_states"] == 60 and same["n_failed_resamples"] == 0
    worse = h3c_ratio(1.2 * a4, a4, CONFIG)
    assert worse["ci"] == pytest.approx([1.2, 1.2], abs=1e-12)
    assert worse["pass"] is False and worse["inconclusive_reason"] is None
    assert "fail" not in worse

    a5 = a4 * (1.0 + 0.1 * rng.uniform(size=60))
    out = h3c_ratio(a5, a4, CONFIG)
    assert out["A5_over_A4_mse"] == pytest.approx(np.mean(a5) / np.mean(a4), abs=1e-12)
    reference = block_bootstrap(lambda idx: float(a5[idx].mean() / a4[idx].mean()), 60, 200, 5,
                                make_rng(CONFIG.seed, "h3c-ratio"), LEVEL)
    assert out["ci"] == [reference[1], reference[2]]

    short = h3c_ratio(a4[:30], a4[:30], CONFIG)
    assert short["pass"] is False and short["inconclusive_reason"] == "n_states < 50"
    with pytest.raises(ValueError):
        h3c_ratio(a4[:30], a4[:20], CONFIG)


def _scores(**state_mse: np.ndarray) -> dict[str, RuleScores]:
    """Rule scores that carry only ``state_mse_ref`` (the field H2c and H3c read)."""
    return {name: RuleScores(mse=np.zeros(1), state_mse_ref=mse, regret=np.zeros(1),
                             agreement=0.0, km_median=0.0, rmst=0.0)
            for name, mse in state_mse.items()}


def _calibration(cp_sq: float, plp_sq: float, n: int = 6, draws: int = 2) -> SplitData:
    """A calibration split whose errors at H_ref (second of horizons 8, 30) have fixed squares."""
    cp = np.zeros((n, draws, 2))
    plp = np.zeros((n, draws, 2))
    cp[:, :, 1] = np.sqrt(cp_sq) * np.where(np.arange(draws) % 2 == 0, 1.0, -1.0)
    plp[:, :, 1] = np.sqrt(plp_sq)
    cp[:, :, 0], plp[:, :, 0] = 100.0, 100.0  # the other horizon must not be read
    zeros = np.zeros((n, draws, 2))
    evals = EvaluationDraws(
        horizons=np.array([8, 30]), cp_err=cp, plp_err=plp, verify_noise=zeros,
        distance=np.zeros((n, draws)), est_nu=np.zeros((n, draws)),
        growth_proxy=np.zeros((n, draws)), gain_proxy=zeros, inputs=np.zeros((n, draws, 1)),
        noise_sens=np.zeros((n, draws)))
    return SplitData(moments=None, evals=evals)


def test_h2c_chooses_the_better_single_forecaster_on_calibration_and_reports_a4o() -> None:
    """The better single forecaster comes from the calibration split; A4o - A2 is reported only.

    Reference: hand-built data. Calibration squared errors at H_ref are 0.25 for CP (A0) and 4.0
    for PLP (A1), so the realized calibration MSEs are 0.25 and 4.0 and the choice is A0, although
    on the test scores A1 has the smaller per-state MSE (0.1 against 0.2), which the old rule would
    have picked. A tie (equal squares) goes to A0. ``A4o_minus_A2.mean`` is the hand mean of
    ``a4o - a2`` (``abs=1e-12``: one reduction of 6 numbers); its interval is at level 0.95, it
    carries ``role == "reported"`` and no ``pass``. The value at the other horizon (100) must not
    be read: the column is located by the horizon value, not by position. The entry
    ``A4_minus_A0`` exists and ``A4_minus_A1`` does not.
    """
    from lpcstudy.analysis import h2c_state_dependence

    a2 = np.array([1.0, 1.5, 2.0, 2.5, 3.0, 3.5])
    a4 = a2 - 0.5
    a4o = a2 - np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
    scores = _scores(A2=a2, A4=a4, A4o=a4o, A0=np.full(6, 0.2), A1=np.full(6, 0.1))
    out = h2c_state_dependence(scores, _calibration(0.25, 4.0), CONFIG)
    assert out["best_single"] == "A0"
    assert out["calibration_mse"] == {"A0": 0.25, "A1": 4.0}
    assert "A4_minus_A0" in out and "A4_minus_A1" not in out
    assert out["A4_minus_A0"]["mean"] == pytest.approx(np.mean(a4 - 0.2), abs=1e-12)
    reported = out["A4o_minus_A2"]
    assert reported["mean"] == pytest.approx(-0.35, abs=1e-12)  # mean of -0.1 .. -0.6
    assert reported["level"] == 0.95 and reported["role"] == "reported" and "pass" not in reported
    assert reported["relative"] == pytest.approx(-0.35 / np.mean(a2), abs=1e-12)
    assert out["A4_minus_A2"]["pass"] is True  # a4 - a2 = -0.5 in every resample
    assert out["A4_minus_A0"]["pass"] is False and out["pass"] is False  # a4 - 0.2 > 0 everywhere
    tie = h2c_state_dependence(scores, _calibration(1.0, 1.0), CONFIG)
    assert tie["best_single"] == "A0"
    flipped = h2c_state_dependence(scores, _calibration(4.0, 0.25), CONFIG)
    assert flipped["best_single"] == "A1" and "A4_minus_A1" in flipped
    with pytest.raises(ValueError):
        h2c_state_dependence(scores, SplitData(moments=None, evals=None), CONFIG)


def test_h3_regimes_wiring_keys_and_arguments(monkeypatch: pytest.MonkeyPatch) -> None:
    """``h3_regimes`` returns exactly H3a, H3b, H3c and regime_curve, calling the three helpers.

    Reference: the key sets of the plan (D4), written out below; no ``p_eff`` key anywhere. The
    helpers are checked against direct calls on the same arrays: H3c equals ``h3c_ratio`` of the
    scores, H3b equals ``h3b_importances`` of the construction arrays, and H3a uses the first
    evaluation draw (its ``n_per_regime`` counts the states of ``regime[:, 0]``). The profile
    function is replaced by a lookup of fixed arrays (the unit under test is the wiring, not the
    proxies), and the regime map is a real tree. Exact equality of dicts (same deterministic code
    on the same inputs: a wiring check, not independent evidence of the statistics, which the
    tests above check).
    """
    from lpcstudy import analysis
    from lpcstudy.allocation import RegimeMap, state_horizon_target
    from lpcstudy.oracle import curvature, oracle_weight
    from lpcstudy.pipeline import FittedRules
    from unit_helpers import realizable_triples

    rng = np.random.default_rng(55)
    n_test, n_con, n_hor, n_draws = 60, 80, 30, 2

    def moments_of(n: int) -> EnsembleMoments:
        t = realizable_triples(rng, n // 3, n // 3, n - 2 * (n // 3), inside=(0.1, 0.9))
        e_c, e_p, cross = (np.repeat(t[k][:, None], n_hor, axis=1) for k in ("E_C", "E_P", "C"))
        zeros = np.zeros_like(e_c)
        return EnsembleMoments(horizons=np.arange(1, n_hor + 1), mean_cp=zeros, mean_plp=zeros,
                               sq_cp=e_c, sq_plp=e_p, cross=cross, analog_seed=np.ones(n),
                               est_seed=np.ones(n), noise_sens=np.zeros(n))

    test_m, con_m = moments_of(n_test), moments_of(n_con)
    profiles = {"test": rng.normal(size=(n_test, n_draws, 4)),
                "construction": rng.normal(size=(n_con, n_draws, 4))}
    monkeypatch.setattr(analysis, "deployable_profile", lambda ev, proxies, noise, lt: profiles[ev])
    tree = DecisionTreeRegressor(max_leaf_nodes=3, random_state=1).fit(
        profiles["test"].reshape(-1, 4), rng.normal(size=(n_test * n_draws, 2)))
    leaf_ids = np.unique(tree.apply(profiles["test"].reshape(-1, 4)))
    rmap = RegimeMap(tree=tree, leaf_ids=leaf_ids, weights=np.full((len(leaf_ids), n_hor), 0.5),
                     horizons_km=np.array([20.0, 10.0, 30.0]))
    rules = FittedRules(proxies=None, global_weights=None, predictor=None,
                        regimes={3: rmap}, chosen_regimes=3)
    cell = Cell(system="lorenz63", noise=0.01, library_size=0, label="stub", setup=None,
                splits={"test": SplitData(test_m, "test"), "construction": SplitData(con_m, "construction")},
                oracles={}, horizons=np.arange(1, n_hor + 1))
    durations = rng.integers(1, 30, (n_test, n_draws))
    a5 = RuleScores(mse=np.zeros(1), state_mse_ref=rng.uniform(1, 2, n_test), regret=np.zeros(1),
                    agreement=0.0, km_median=0.0, rmst=0.0, durations=durations,
                    events=np.ones((n_test, n_draws), dtype=bool))
    a4 = RuleScores(mse=np.zeros(1), state_mse_ref=rng.uniform(1, 2, n_test), regret=np.zeros(1),
                    agreement=0.0, km_median=0.0, rmst=0.0)
    out = analysis.h3_regimes(cell, rules, {"A5": a5, "A4": a4}, CONFIG)

    assert set(out) == {"H3a", "H3b", "H3c", "regime_curve"} and "p_eff" not in json.dumps(out)
    assert set(out["H3a"]) == {"chosen_K", "pairs", "logrank_p_raw", "logrank_p_holm",
                               "n_per_regime", "n_km_not_reached", "iqr_lt", "iqr_lt_mean",
                               "threshold", "pass", "inconclusive_reason"}
    assert set(out["H3b"]) == {"weight_lambda", "D", "stability", "weight_tree_importance",
                               "horizon_tree_importance", "degenerate_fits", "nan_resamples",
                               "n_states", "n_resamples", "max_leaf_nodes", "threshold", "pass",
                               "inconclusive_reason"}
    assert set(out["H3c"]) == {"A5_over_A4_mse", "ci", "level", "n_states", "n_failed_resamples",
                               "threshold", "pass", "inconclusive_reason"}
    assert out["H3c"] == analysis.h3c_ratio(a5.state_mse_ref, a4.state_mse_ref, CONFIG)
    col = CONFIG.reference_horizon - 1
    assert out["H3b"] == analysis.h3b_importances(
        profiles["construction"], oracle_weight(con_m)[:, col], curvature(con_m)[:, col],
        np.log(state_horizon_target(con_m, 0.01, CONFIG.primary_threshold)), CONFIG)
    first = rmap.assign(profiles["test"])[:, 0]
    assert out["H3a"]["n_per_regime"] == [int(np.sum(first == k)) for k in range(3)]
    assert out["H3a"]["chosen_K"] == 3 and set(out["regime_curve"]) == {"regret_ratio_by_K",
                                                                       "realized_K"}
