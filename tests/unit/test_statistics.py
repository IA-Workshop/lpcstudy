"""Tests for lpcstudy.statistics: Kaplan-Meier, log-rank, Holm, partial correlation,
the moving-block bootstrap with counted failures, and the interval verdicts."""

from __future__ import annotations

import itertools
import math
import warnings
from collections.abc import Callable
from fractions import Fraction

import numpy as np
import pytest
from scipy import stats as sps

from lpcstudy.statistics import MIN_STATES, V3_SYSTEMS, BootstrapInterval, block_bootstrap, \
    block_bootstrap_counted, block_bootstrap_dropped, block_resample_indices, bootstrap_values, \
    combine_verdicts, criterion_verdict, holm_adjust, interval_verdict, kaplan_meier, \
    logrank_parts, logrank_test, overall_verdict, partial_correlation, percentile_interval


def test_kaplan_meier_matches_geometric_survival() -> None:
    """KM recovers the survival of censored geometric times.

    Reference: exact distribution. T is Geometric(0.1) on 1, 2, ..., so
    S(H) = Pr(T > H) = 0.9^H. Independent censoring C is uniform on 1..40 and the
    horizon is capped at H_max = 40; an event at T = C counts as an event (the
    convention of the at-risk set ``dur >= H``). n = 50 000 subjects.
    Tolerance: sup over H = 1..40 of |S_KM(H) - 0.9^H| < 0.01, unchanged. Greenwood's
    approximation, Var S(H) = S(H)^2 sum_{h <= H} d_h / (n_h (n_h - d_h)) evaluated at
    the expected counts, gives a pointwise standard error that peaks at 2.3e-3 (H = 8)
    and is 1.7e-3 at H = 40, where about 20 subjects remain at risk. So 0.01 is 4.3
    standard errors at the worst point, for a supremum over 40 correlated points.
    """
    rng = np.random.default_rng(3)
    times = rng.geometric(0.1, 50_000)
    censor = rng.integers(1, 41, 50_000)
    dur = np.minimum(np.minimum(times, censor), 40)
    ev = (times <= censor) & (times <= 40)
    curve = kaplan_meier(dur, ev, 40)
    assert np.max(np.abs(curve.survival - 0.9 ** curve.times)) < 0.01


def test_logrank_detects_difference_and_not_null() -> None:
    """Log-rank: small p for different hazards, large-ish p for equal hazards.

    Reference: property under known truth. Group A is Geometric(0.1), B is
    Geometric(0.2), n = 400 per group, no censoring; C is a second Geometric(0.1)
    sample. The value of the p-value is checked against independent references in
    ``test_logrank_hand_worked_ties_and_censoring`` and ``test_logrank_matches_scipy``.
    Thresholds, unchanged. (i) p < 1e-6 for A against B: the hazard ratio is
    ln 0.8 / ln 0.9 = 2.12 and d = 800 events, so the expected chi-square is about
    d (ln HR)^2 / 4 = 113 and p is about 1e-26, 20 orders of magnitude below the
    threshold. (ii) p > 1e-3 for A against C: under the null p is uniform on (0, 1),
    so the false-failure probability of this single fixed-seed draw is 1e-3.
    """
    rng = np.random.default_rng(4)
    a, b = rng.geometric(0.1, 400), rng.geometric(0.2, 400)
    ones = np.ones(400, dtype=bool)
    assert logrank_test(a, ones, b, ones) < 1e-6
    c = rng.geometric(0.1, 400)
    assert logrank_test(a, ones, c, ones) > 1e-3


def test_logrank_hand_worked_ties_and_censoring() -> None:
    """Log-rank p-value on a small data set with tied times and a censored subject.

    Reference: hand computation of the Mantel-Haenszel log-rank statistic with
    the tie-corrected hypergeometric variance, V = d (n_A/n)(1 - n_A/n)(n - d)/(n - 1),
    and p = erfc(sqrt(chi2/2)) from ``math.erfc`` (exact for one degree of freedom;
    independent of ``scipy.stats.chi2``).
    Group A: durations (1, 2, 2, 3), events (1, 1, 1, 0). Group B: (2, 3, 3, 4), all
    events. Event times, n at risk, n_A at risk, d events, d_A, and the terms:
      t=1: n=8, n_A=4, d=1, d_A=1: O-E = 1 - 1/2 = 1/2;       V = 1/4.
      t=2: n=7, n_A=3, d=3, d_A=2: O-E = 2 - 9/7 = 5/7;       V = 3 (3/7)(4/7)(4/6) = 24/49.
      t=3: n=4, n_A=1, d=2, d_A=0: O-E = 0 - 1/2 = -1/2;      V = 2 (1/4)(3/4)(2/3) = 1/4.
      t=4: n=1, n_A=0, d=1, d_A=0: O-E = 0;                    V = 0 (n = 1 is skipped).
    Sum O-E = 5/7; sum V = 1/2 + 24/49 = 97/98; chi2 = (25/49)/(97/98) = 50/97, so
    p = erfc(sqrt(25/97)) = 0.4728. Dropping the tie factor (n - d)/(n - 1), ignoring
    the censoring, or including the n = 1 term changes p visibly.
    Tolerance ``rel=1e-12``: a few dozen float64 operations on O(1) numbers (error below
    1e-14) and one tail-function evaluation (error about 1e-15 relative at p = 0.47).
    """
    dur_a, ev_a = np.array([1, 2, 2, 3]), np.array([True, True, True, False])
    dur_b, ev_b = np.array([2, 3, 3, 4]), np.array([True, True, True, True])
    expected = math.erfc(math.sqrt(25.0 / 97.0))
    assert logrank_test(dur_a, ev_a, dur_b, ev_b) == pytest.approx(expected, rel=1e-12)


def test_logrank_matches_scipy() -> None:
    """Log-rank p-values agree with ``scipy.stats.logrank`` (independent implementation).

    Reference: ``scipy.stats.logrank`` (SciPy 1.18.1, requirements.txt), an independent
    implementation of the same test whose documented statistic uses the tie-corrected
    variance V = E ((N - O)/N)((N - N_i)/(N - 1)), which equals the one in
    ``logrank_test``. (This tests the implementation, not the choice of variance; the
    hand-worked test fixes the numbers.) Two cases: (i) the geometric samples of
    ``test_logrank_detects_difference_and_not_null`` (n = 400 per group, almost all
    times tied, p about 1e-26) and (ii) Geometric(0.10) against Geometric(0.13),
    n = 300 per group, right-censored by Uniform{1..15}, with ties between events and
    censoring (an event at the censoring time counts as an event in both).
    Tolerance ``rtol=1e-10``: the two codes sum 40 per-time terms in different order, so
    the statistics agree to about 1e-14 relative; the p-value derivative is
    d ln p / d chi2 ~ 1/2, which at chi2 = 113 turns 5e-15 into 3e-13. 1e-10 leaves
    a factor of 300 in the worst case (i).
    """
    rng = np.random.default_rng(4)
    a, b = rng.geometric(0.1, 400), rng.geometric(0.2, 400)
    ones = np.ones(400, dtype=bool)
    expected = sps.logrank(a, b).pvalue
    assert logrank_test(a, ones, b, ones) == pytest.approx(expected, rel=1e-10)

    rng = np.random.default_rng(11)
    groups = []
    for hazard in (0.10, 0.13):
        times = rng.geometric(hazard, 300)
        censor = rng.integers(1, 16, 300)
        groups.append((np.minimum(times, censor), times <= censor))
    (dur_a, ev_a), (dur_b, ev_b) = groups
    assert 0 < ev_a.sum() < 300 and 0 < ev_b.sum() < 300  # premise: some censoring
    as_data = lambda dur, ev: sps.CensoredData(uncensored=dur[ev], right=dur[~ev])
    expected = sps.logrank(as_data(dur_a, ev_a), as_data(dur_b, ev_b)).pvalue
    assert logrank_test(dur_a, ev_a, dur_b, ev_b) == pytest.approx(expected, rel=1e-10)


def test_logrank_parts_hand_values_and_zero_variance_cases() -> None:
    """``logrank_parts`` returns the O - E sum and the variance of the hand-worked data set.

    Reference: the hand computation of ``test_logrank_hand_worked_ties_and_censoring``
    (O - E = 5/7 and V = 97/98, derived there term by term from the Mantel-Haenszel
    definition; independent of the code). The p-value is checked against
    ``math.erfc(sqrt(chi2/2))`` (exact for one degree of freedom, independent of
    ``scipy.stats.chi2``), with chi2 = (O - E)^2 / V from the parts, and equals
    ``logrank_test`` to 1e-15 (the same arithmetic). Zero-variance cases, in which
    ``logrank_test`` returns 1.0 (DEF-0001): no event at all (O - E = V = 0 exactly), and one
    empty group (every risk set has n_A = 0, so each term is exactly 0).
    Tolerance ``rel=1e-13`` on the parts: about 30 float64 operations on O(1) numbers, error
    below 1e-14; the zero cases are exact equalities.
    """
    dur_a, ev_a = np.array([1, 2, 2, 3]), np.array([True, True, True, False])
    dur_b, ev_b = np.array([2, 3, 3, 4]), np.array([True, True, True, True])
    obs_minus_exp, variance = logrank_parts(dur_a, ev_a, dur_b, ev_b)
    assert obs_minus_exp == pytest.approx(5.0 / 7.0, rel=1e-13)
    assert variance == pytest.approx(97.0 / 98.0, rel=1e-13)
    chi2 = obs_minus_exp**2 / variance
    assert logrank_test(dur_a, ev_a, dur_b, ev_b) == pytest.approx(
        math.erfc(math.sqrt(chi2 / 2.0)), rel=1e-12)
    assert logrank_test(dur_a, ev_a, dur_b, ev_b) == float(sps.chi2.sf(chi2, df=1))

    none = np.zeros(4, dtype=bool)
    assert logrank_parts(dur_a, none, dur_b, none) == (0.0, 0.0)
    assert logrank_test(dur_a, none, dur_b, none) == 1.0
    empty = np.array([], dtype=int)
    assert logrank_parts(dur_a, ev_a, empty, empty.astype(bool)) == (0.0, 0.0)


def test_holm() -> None:
    """Holm adjustment on a hand-worked example.

    Reference: Holm's step-down definition, worked by hand. Sort the p-values
    (0.01, 0.03, 0.04) and take the running maximum of (m - rank) p, capped at 1:
    3 * 0.01 = 0.03; 2 * 0.03 = 0.06; max(1 * 0.04, 0.06) = 0.06. In the input order
    (0.01, 0.04, 0.03) the result is (0.03, 0.06, 0.06). (No external source is cited
    for the example; it is derived from the definition.)
    Tolerance: ``np.allclose`` defaults (rtol 1e-5, atol 1e-8), unchanged. The inputs
    are decimal literals and the products have relative round-off below 1e-15.
    """
    assert np.allclose(holm_adjust([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])


def test_holm_clip_at_one_and_ties() -> None:
    """Holm adjusted p-values are capped at 1 and tied p-values are handled.

    Reference: Holm's definition by hand. (i) (0.4, 0.8, 0.9): 3 * 0.4 = 1.2 caps at 1,
    and the running maximum keeps 1 for the rest: (1, 1, 1). (ii) (0.02, 0.3, 0.6):
    3 * 0.02 = 0.06; 2 * 0.3 = 0.6; max(0.6, 1 * 0.6) = 0.6: (0.06, 0.6, 0.6).
    (iii) a tie (0.01, 0.01, 0.2): 3 * 0.01 = 0.03, then max(0.03, 2 * 0.01) = 0.03,
    then max(0.03, 0.2) = 0.2: (0.03, 0.03, 0.2), whichever tied element comes first.
    Tolerance ``atol=1e-15``, ``rtol=0``: each value is one product of a small integer and
    a decimal literal, with relative round-off below 2.2e-16 on values below 1, so
    below 1.5e-16 absolute; the capped values are exactly 1.0.
    """
    got = holm_adjust([0.4, 0.8, 0.9])
    assert got == [1.0, 1.0, 1.0]
    np.testing.assert_allclose(holm_adjust([0.02, 0.3, 0.6]), [0.06, 0.6, 0.6],
                               rtol=0.0, atol=1e-15)
    np.testing.assert_allclose(holm_adjust([0.01, 0.01, 0.2]), [0.03, 0.03, 0.2],
                               rtol=0.0, atol=1e-15)


def test_partial_correlation_removes_confounder() -> None:
    """A variable related to the target only through a control has ~zero partial r.

    Reference: exact distribution. y = z + 0.1 e_y and x = z + 0.1 e_x with independent
    standard normal z, e_y, e_x: given z, y and x are independent, so the population
    partial correlation is 0 (while the plain correlation is 0.99). The sample
    correlation of residuals, n = 5000, has standard error about
    1/sqrt(n - 3) = 0.0141.
    Tolerance: |r| < 0.05, unchanged, which is 3.5 standard errors (two-sided
    false-failure probability 5e-4 for this fixed seed). A function returning a constant
    0 would pass this test; the next test checks a nonzero value.
    """
    rng = np.random.default_rng(6)
    z = rng.standard_normal(5000)
    x = z + 0.1 * rng.standard_normal(5000)
    y = z + 0.1 * rng.standard_normal(5000)
    assert abs(partial_correlation(y, x, z[:, None])) < 0.05


def test_partial_correlation_nonzero_closed_form() -> None:
    """The partial correlation recovers a known nonzero value, with its sign.

    Reference: closed form for a manufactured model. With z, u, v independent standard
    normal, y = z + u and x = z + u + v, regressing out z leaves u and u + v, whose
    correlation is cov(u, u + v)/sqrt(var u var(u + v)) = 1/sqrt(2) = 0.7071. With
    y' = z - u the residuals are -u and u + v, so the value is -1/sqrt(2). The plain
    correlation of y and x is 2/sqrt(2 * 3) = 0.816 and of y' and x is 0, so the
    answer differs from the unconditional one (a function that ignored z would fail).
    Tolerance ``abs=0.03``: the standard error of a sample correlation with n = 5000 and
    rho = 0.707 is (1 - rho^2)/sqrt(n - 3) = 0.5/70.7 = 7.1e-3, so 0.03 is 4.2 standard
    errors (false-failure probability about 3e-5 per assertion, fixed seed).
    """
    rng = np.random.default_rng(12)
    z, u, v = rng.standard_normal((3, 5000))
    x = z + u + v
    assert partial_correlation(z + u, x, z[:, None]) == pytest.approx(1 / np.sqrt(2), abs=0.03)
    assert partial_correlation(z - u, x, z[:, None]) == pytest.approx(-1 / np.sqrt(2), abs=0.03)


# ---------------------------------------------------------------------------------------
# Moving-block bootstrap, failed resamples and verdicts (WU-0002.4-.5 phase 1, DEC-0012).
# ---------------------------------------------------------------------------------------


def _pre_refactor_block_bootstrap(statistic: Callable[[np.ndarray], float], n_items: int,
                                  n_resamples: int, block: int, seed: int,
                                  level: float = 0.95) -> tuple[float, float, float]:
    """Verbatim copy of ``block_bootstrap`` at commit 5a485d0, before the refactor."""
    rng = np.random.default_rng(seed)
    base = np.arange(n_items)
    n_blocks = int(np.ceil(n_items / block))
    starts_max = max(1, n_items - block + 1)
    values = np.empty(n_resamples)
    for r in range(n_resamples):
        starts = rng.integers(0, starts_max, n_blocks)
        idx = (starts[:, None] + np.arange(block)[None, :]).ravel()[:n_items]
        values[r] = statistic(base[np.minimum(idx, n_items - 1)])
    alpha = (1.0 - level) / 2.0
    return (float(statistic(base)), float(np.nanquantile(values, alpha)),
            float(np.nanquantile(values, 1.0 - alpha)))


def _reference_bound(values: np.ndarray, quantile: float, lower: bool) -> float:
    """Linear-interpolation quantile with failed values at -inf (lower) or +inf (upper).

    Independent of ``percentile_interval``: an explicit order-statistic formula
    ``s[i] (1 - w) + s[i + 1] w`` with ``h = (B - 1) q``, ``i = floor(h)``, ``w = h - i``,
    in which an infinite order statistic that carries positive weight makes the
    result infinite (no infinite arithmetic is performed).
    """
    fill = -math.inf if lower else math.inf
    order = sorted(fill if not math.isfinite(v) else float(v) for v in values)
    height = (len(order) - 1) * quantile
    i = math.floor(height)
    weight = height - i
    if weight == 0.0:
        return order[i]
    for neighbour in (order[i], order[i + 1]):
        if math.isinf(neighbour):
            return neighbour
    return order[i] * (1.0 - weight) + order[i + 1] * weight


def _exact_edge(n_resamples: int, level: float) -> int:
    """Failures needed to make a bound infinite: the smallest F with weight on a failure."""
    alpha = (1.0 - level) / 2.0
    return math.floor((n_resamples - 1) * alpha) + 1


def _mean_of(x_values: np.ndarray) -> Callable[[np.ndarray], float]:
    """Statistic: mean of the selected items."""
    return lambda idx: float(np.mean(x_values[idx]))


@pytest.mark.parametrize("n_items,block,n_resamples,seed", [
    (23, 5, 50, 0), (300, 5, 40, 1), (4, 5, 30, 2), (5, 5, 30, 3), (1, 3, 10, 4), (50, 1, 30, 5)])
def test_regression_block_bootstrap_bitwise_equals_pre_refactor(
        n_items: int, block: int, n_resamples: int, seed: int) -> None:
    """Regression guard: the refactored ``block_bootstrap`` equals the old code bitwise.

    Reference: a verbatim copy of the pre-refactor function (commit 5a485d0), kept in this
    test. Cases cover n a multiple of the block, a partial last block, n < block, n = block,
    n = 1 and block 1, and a nonlinear statistic as well as a mean. Tolerance: none; the same
    draws and the same expressions give identical float64 values (``==`` on the tuples).
    """
    x_values = np.random.default_rng(99).standard_normal(max(n_items, 1)) ** 3
    for level in (0.95, 0.9):
        for statistic in (_mean_of(x_values), lambda idx: float(np.std(x_values[idx]) ** 0.5)):
            new = block_bootstrap(statistic, n_items, n_resamples, block, seed, level)
            old = _pre_refactor_block_bootstrap(statistic, n_items, n_resamples, block, seed,
                                                level)
            assert new == old


def test_regression_block_bootstrap_drops_nan_as_before() -> None:
    """Regression guard: ``block_bootstrap`` still drops NaN resamples (nanquantile).

    Reference: the verbatim pre-refactor copy. The refactor must not change the
    behaviour that A3 will replace later (WU-0002.9/.11). Tolerance: bitwise.
    """
    x_values = np.random.default_rng(7).standard_normal(60)

    def with_nans(idx: np.ndarray) -> float:
        resampled = not np.array_equal(idx, np.arange(60))
        return float("nan") if resampled and idx[0] % 7 == 0 else float(np.mean(x_values[idx]))

    assert block_bootstrap(with_nans, 60, 80, 5, 3) == \
        _pre_refactor_block_bootstrap(with_nans, 60, 80, 5, 3)


@pytest.mark.parametrize("n_items,n_resamples", [(23, 50), (300, 50)])
def test_block_resample_indices_equal_those_recorded_inside_old_function(
        n_items: int, n_resamples: int) -> None:
    """The yielded indices are exactly the arrays the old function passed to its statistic.

    Reference: the verbatim pre-refactor copy with a recording statistic (its last call
    is the point estimate on ``arange(n)``). Tolerance: none (integer arrays).
    Also checks properties that hold by construction of a moving-block draw, independent
    of the code: length n, values in [0, n-1], consecutive runs inside a block, block
    starts at most n - block.
    """
    recorded: list[np.ndarray] = []

    def record(idx: np.ndarray) -> float:
        recorded.append(idx.copy())
        return 0.0

    _pre_refactor_block_bootstrap(record, n_items, n_resamples, 5, 11)
    drawn = list(block_resample_indices(n_items, n_resamples, 5, 11))
    assert len(drawn) == n_resamples and len(recorded) == n_resamples + 1
    for mine, theirs in zip(drawn, recorded[:-1]):
        np.testing.assert_array_equal(mine, theirs)
        assert mine.shape == (n_items,) and mine.min() >= 0 and mine.max() <= n_items - 1
        within = np.arange(1, n_items) % 5 != 0
        assert np.all(np.diff(mine)[within] == 1)
        assert np.all(mine[::5] <= n_items - 5)


def test_block_resample_indices_seed_forms_and_validation() -> None:
    """An int seed equals ``default_rng(seed)``; a Generator is consumed; bad input raises.

    Reference: NumPy's documented seeding (``default_rng(int)`` is deterministic) and the
    streaming property: two consecutive draws of B from one generator equal one draw of 2B
    from the same seed. Tolerance: none. Bad sizes raise at the call, not on first iteration.
    """
    from_int = list(block_resample_indices(40, 20, 5, 17))
    from_gen = list(block_resample_indices(40, 20, 5, np.random.default_rng(17)))
    for a, b in zip(from_int, from_gen):
        np.testing.assert_array_equal(a, b)
    gen = np.random.default_rng(17)
    first = list(block_resample_indices(40, 10, 5, gen))
    second = list(block_resample_indices(40, 10, 5, gen))
    for a, b in zip(first + second, from_int):
        np.testing.assert_array_equal(a, b)
    stat = _mean_of(np.arange(40.0))
    assert block_bootstrap(stat, 40, 30, 5, np.random.default_rng(3)) == \
        block_bootstrap(stat, 40, 30, 5, 3)
    for bad in ((0, 5, 5), (10, 5, 0), (10, -1, 5)):
        with pytest.raises(ValueError):
            block_resample_indices(bad[0], bad[1], bad[2], 0)


def test_bootstrap_values_scalar_vector_and_call_order() -> None:
    """``bootstrap_values`` returns recorded values, the point last, and shares resamples.

    Reference: a recording statistic. (i) Scalar: values equal the recorded outputs of the
    first B calls in order; the point is the statistic on ``arange(n)`` and is evaluated
    after the resamples. (ii) Vector (mean of x, median of y): column j equals the scalar
    bootstrap of component j at the same seed, bitwise (same resamples, one pass).
    (iii) A statistic that changes shape, returns a 2-D array, or raises is not hidden.
    Tolerance: bitwise.
    """
    x_values = np.random.default_rng(1).standard_normal(33)
    y_values = np.random.default_rng(2).standard_normal(33)
    seen: list[np.ndarray] = []

    def record(idx: np.ndarray) -> float:
        seen.append(idx.copy())
        return float(np.mean(x_values[idx]))

    point, values = bootstrap_values(record, 33, 25, 5, 8)
    assert values.shape == (25,) and len(seen) == 26
    np.testing.assert_array_equal(seen[-1], np.arange(33))
    expected = [np.mean(x_values[i]) for i in seen[:-1]]
    np.testing.assert_array_equal(values, expected)
    assert point == record(np.arange(33)) and isinstance(point, float)

    def both(idx: np.ndarray) -> np.ndarray:
        return np.array([np.mean(x_values[idx]), np.median(y_values[idx])])

    point_vec, values_vec = bootstrap_values(both, 33, 25, 5, 8)
    assert values_vec.shape == (25, 2) and point_vec.shape == (2,)
    _, only_x = bootstrap_values(lambda i: float(np.mean(x_values[i])), 33, 25, 5, 8)
    _, only_y = bootstrap_values(lambda i: float(np.median(y_values[i])), 33, 25, 5, 8)
    np.testing.assert_array_equal(values_vec[:, 0], only_x)
    np.testing.assert_array_equal(values_vec[:, 1], only_y)

    calls = itertools.count()
    with pytest.raises(ValueError):  # shape changes between calls
        bootstrap_values(lambda i: np.zeros(1 + next(calls) % 2), 33, 5, 5, 0)
    with pytest.raises(ValueError):  # 2-D output
        bootstrap_values(lambda i: np.zeros((2, 2)), 33, 5, 5, 0)

    def boom(idx: np.ndarray) -> float:
        raise RuntimeError("statistic failed")

    with pytest.raises(RuntimeError):  # exceptions are not caught
        bootstrap_values(boom, 33, 5, 5, 0)


def test_percentile_interval_no_failure_is_np_quantile_bitwise() -> None:
    """With F = 0 the interval is ``np.quantile`` and equals the old ``nanquantile`` form.

    Reference: ``np.quantile`` at alpha and 1 - alpha, and the bounds returned by the
    pre-refactor ``block_bootstrap``. Tolerance: bitwise (same linear method on the same data).
    No RuntimeWarning (an inf-inf lerp) may be raised.
    """
    values = np.random.default_rng(5).standard_normal(500)
    for level in (0.95, 0.9, 0.99):
        alpha = (1.0 - level) / 2.0
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            lo, hi, n_failed = percentile_interval(values, level)
        assert (lo, hi, n_failed) == (float(np.quantile(values, alpha)),
                                      float(np.quantile(values, 1.0 - alpha)), 0)
    x_values = np.random.default_rng(6).standard_normal(40)
    stat = _mean_of(x_values)
    _, old_lo, old_hi = _pre_refactor_block_bootstrap(stat, 40, 300, 5, 4)
    _, boot_values = bootstrap_values(stat, 40, 300, 5, 4)
    assert percentile_interval(boot_values, 0.95) == (old_lo, old_hi, 0)


@pytest.mark.parametrize("n_resamples,level,edge", [
    (20, 0.8, 2), (2000, 0.95, 50), (2000, 1.0 - 0.05 / 3.0, 17), (500, 0.95, 13)])
def test_percentile_interval_failure_edge_matches_exact_index_rule(
        n_resamples: int, level: float, edge: int) -> None:
    """Failed resamples sit at -inf (lower) and +inf (upper); both bounds go infinite at F*.

    Reference: ``_reference_bound``, the explicit order-statistic formula in this test with
    failures filled by -inf / +inf, for F = 0, 1, ..., F* + 1 failures of mixed kind (NaN,
    +inf, -inf) at random positions of N(0, 1) values (seed 12; the positions are irrelevant
    to the result). F* is stated by hand: B = 20, level 0.8: 2; B = 2000, 95%: 50;
    B = 2000, 1 - 0.05/3: 17 (the Holm-type level of three criteria); B = 500, 95%: 13
    [floor((B-1) a) + 1 with a = (1 - level)/2]. Tolerance: finite bounds rel 1e-13 (a convex
    combination of two order statistics: a few ulp); infinite bounds exactly; ``n_failed``
    exact. The edge cases F* - 1 (finite) and F* (infinite) are asserted explicitly.
    """
    assert _exact_edge(n_resamples, level) == edge
    rng = np.random.default_rng(12)
    base = rng.standard_normal(n_resamples)
    kinds = [math.nan, math.inf, -math.inf]
    alpha = (1.0 - level) / 2.0
    for n_failed in range(edge + 2):
        values = base.copy()
        values[rng.choice(n_resamples, n_failed, replace=False)] = \
            [kinds[k % 3] for k in range(n_failed)]
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            lo, hi, got = percentile_interval(values, level)
        assert got == n_failed
        want_lo = _reference_bound(values, alpha, lower=True)
        want_hi = _reference_bound(values, 1.0 - alpha, lower=False)
        for have, want in ((lo, want_lo), (hi, want_hi)):
            if math.isinf(want):
                assert have == want
            else:
                assert math.isfinite(have) and have == pytest.approx(want, rel=1e-13)
        assert (n_failed >= edge) == (lo == -math.inf and hi == math.inf)
    assert percentile_interval(np.full(n_resamples, math.nan), level) == \
        (-math.inf, math.inf, n_resamples)


def test_percentile_interval_float_threshold_is_conservative_at_b21() -> None:
    """Pin the documented float convention of the failure threshold (review R2).

    Reference: exact arithmetic gives (B - 1) a = 20 * 0.1 = 2 for B = 21 and level 0.8,
    so F* = 3 and F = 2 would leave a finite lower bound (the third order statistic);
    the float a = 0.09999999999999998 gives 1.9999999999999996, so the code's F* is 2 and
    F = 2 returns (-inf, inf). This is the documented conservative result (more
    inconclusive, one step), recorded here so that a later change to exact arithmetic is
    a visible decision. F = 1 stays finite; the same threshold applies to the upper bound.
    Tolerance: exact.
    """
    values = np.random.default_rng(0).standard_normal(21)
    for n_failed, infinite in ((1, False), (2, True), (3, True)):
        failing = values.copy()
        failing[:n_failed] = np.nan
        lo, hi, got = percentile_interval(failing, 0.8)
        assert got == n_failed
        assert (lo == -math.inf and hi == math.inf) == infinite


def test_percentile_interval_rejects_bad_input() -> None:
    """Empty, 2-D values and a level outside (0, 1) raise (PRIME.4).

    Reference: the documented contract. Tolerance: none.
    """
    for bad_values in (np.array([]), np.zeros((3, 2))):
        with pytest.raises(ValueError):
            percentile_interval(bad_values, 0.95)
    for bad_level in (0.0, 1.0, -0.1, 1.5):
        with pytest.raises(ValueError):
            percentile_interval(np.arange(10.0), bad_level)


def test_block_bootstrap_counted_equals_block_bootstrap_without_failures() -> None:
    """T7(i): with no failed resample the counted interval equals ``block_bootstrap``.

    Reference: the verbatim pre-refactor function at the same integer seed. Tolerance:
    bitwise. ``n_failed`` is 0, ``n_resamples`` and ``level`` are echoed, and a vector
    statistic is refused (the interval of one scalar only).
    """
    x_values = np.random.default_rng(21).standard_normal(120)
    stat = _mean_of(x_values)
    for level in (0.95, 0.8):
        got = block_bootstrap_counted(stat, 120, 400, 5, 9, level)
        old = _pre_refactor_block_bootstrap(stat, 120, 400, 5, 9, level)
        assert (got.estimate, got.lower, got.upper) == old
        assert (got.n_failed, got.n_resamples, got.level) == (0, 400, level)
    assert isinstance(got, BootstrapInterval)
    with pytest.raises(ValueError):
        block_bootstrap_counted(lambda idx: np.zeros(2), 120, 10, 5, 9)
    with pytest.raises(AttributeError):  # frozen dataclass
        got.lower = 0.0  # type: ignore[misc]


@pytest.mark.parametrize("n_failed", [4, 5, 6])
def test_block_bootstrap_counted_injected_failures_follow_exact_rule(n_failed: int) -> None:
    """T7(ii)-(iii): injected failures are counted and placed at the unfavourable tails.

    Reference: a recorder of the statistic's values, the hand count of injected failures,
    and ``_reference_bound`` (the exact index rule; the planned +-1e300 reference is wrong
    because at B = 200 and 95% the failed order statistic carries weight 0.025, giving
    -2.5e298 under ``np.quantile``). B = 200, level 0.95: F* = floor(199 * 0.025) + 1 = 5.
    F = 4: both bounds finite; F = 5, 6: both infinite. The failures are NaN or +inf at
    calls 3, 17, 40, 41, 100, 150 (first ``n_failed`` of them); the point call is finite.
    Tolerance: finite bounds rel 1e-13; counts exact.
    """
    x_values = np.random.default_rng(31).standard_normal(80)
    bad_calls = {3: math.nan, 17: math.inf, 40: math.nan, 41: -math.inf, 100: math.nan,
                 150: math.inf}
    bad = dict(list(bad_calls.items())[:n_failed])
    recorder: list[float] = []

    def injected(idx: np.ndarray) -> float:
        value = bad.get(len(recorder), float(np.mean(x_values[idx])))
        recorder.append(value)
        return value

    got = block_bootstrap_counted(injected, 80, 200, 5, 13, 0.95)
    resampled = np.array(recorder[:200])
    assert got.n_failed == n_failed == int(np.sum(~np.isfinite(resampled)))
    assert got.n_resamples == 200 and math.isfinite(got.estimate)
    alpha = (1.0 - 0.95) / 2.0
    want_lo = _reference_bound(resampled, alpha, lower=True)
    want_hi = _reference_bound(resampled, 1.0 - alpha, lower=False)
    if n_failed >= 5:
        assert (got.lower, got.upper) == (-math.inf, math.inf)
    else:
        assert got.lower == pytest.approx(want_lo, rel=1e-13)
        assert got.upper == pytest.approx(want_hi, rel=1e-13)
        assert math.isfinite(got.lower) and math.isfinite(got.upper)


VERDICT_CASES = [
    # (band, closed, lower, upper, expected); hand-classified from A1: pass iff inside, fail iff
    # disjoint, else inconclusive; a closed edge belongs to the band, an open one does not.
    # H1a closed band [0.75, 1.25]
    ((0.75, 1.25), (True, True), 0.8, 1.2, "pass"),
    ((0.75, 1.25), (True, True), 0.75, 1.25, "pass"),
    ((0.75, 1.25), (True, True), 0.9, 0.9, "pass"),
    ((0.75, 1.25), (True, True), 1.3, 1.5, "fail"),
    ((0.75, 1.25), (True, True), 0.2, 0.7, "fail"),
    ((0.75, 1.25), (True, True), 0.7, 1.0, "inconclusive"),
    ((0.75, 1.25), (True, True), 1.0, 1.3, "inconclusive"),
    ((0.75, 1.25), (True, True), 1.25, 1.4, "inconclusive"),
    ((0.75, 1.25), (True, True), 0.6, 0.75, "inconclusive"),
    ((0.75, 1.25), (True, True), float(np.nextafter(1.25, np.inf)), 1.4, "fail"),
    ((0.75, 1.25), (True, True), 0.5, float(np.nextafter(0.75, -np.inf)), "fail"),
    ((0.75, 1.25), (True, True), -math.inf, math.inf, "inconclusive"),
    ((0.75, 1.25), (True, True), math.nan, 1.0, "inconclusive"),
    ((0.75, 1.25), (True, True), 1.0, math.nan, "inconclusive"),
    # A bound that cannot be computed never reads as a fail (A3), even when the other bound
    # is disjoint from the band on its own side.
    ((0.75, 1.25), (True, True), math.nan, 0.5, "inconclusive"),
    ((0.75, 1.25), (True, True), 1.3, math.nan, "inconclusive"),
    ((0.75, 1.25), (True, True), math.nan, math.nan, "inconclusive"),
    ((0.0, math.inf), (False, True), math.nan, -1.0, "inconclusive"),
    # H2a(ii) open band (-0.1, 0.1)
    ((-0.1, 0.1), (False, False), -0.05, 0.05, "pass"),
    ((-0.1, 0.1), (False, False), -0.1, 0.05, "inconclusive"),
    ((-0.1, 0.1), (False, False), -0.1, 0.1, "inconclusive"),
    ((-0.1, 0.1), (False, False), 0.1, 0.2, "fail"),
    ((-0.1, 0.1), (False, False), -0.2, -0.1, "fail"),
    ((-0.1, 0.1), (False, False), 0.05, 0.2, "inconclusive"),
    # H2b, H2e, H3b D: (0, inf), lower edge open
    ((0.0, math.inf), (False, True), 0.1, 5.0, "pass"),
    ((0.0, math.inf), (False, True), 0.1, math.inf, "pass"),
    ((0.0, math.inf), (False, True), 0.0, 5.0, "inconclusive"),
    ((0.0, math.inf), (False, True), -1.0, 0.0, "fail"),
    ((0.0, math.inf), (False, True), -1.0, 1.0, "inconclusive"),
    ((0.0, math.inf), (False, True), -math.inf, math.inf, "inconclusive"),
    # H1d: [0.7, inf), lower edge closed
    ((0.7, math.inf), (True, False), 0.7, 0.9, "pass"),
    ((0.7, math.inf), (True, False), 0.6, 0.9, "inconclusive"),
    ((0.7, math.inf), (True, False), 0.1, 0.69, "fail"),
    ((0.7, math.inf), (True, False), 0.7, math.inf, "pass"),
    ((0.7, math.inf), (True, False), -math.inf, 0.69, "fail"),
    # H2a(i): (-inf, 0.1), upper edge open
    ((-math.inf, 0.1), (True, False), -1.0, 0.05, "pass"),
    ((-math.inf, 0.1), (True, False), -1.0, 0.1, "inconclusive"),
    ((-math.inf, 0.1), (True, False), 0.1, 0.5, "fail"),
    ((-math.inf, 0.1), (True, False), 0.05, 0.5, "inconclusive"),
    ((-math.inf, 0.1), (False, False), -math.inf, 0.05, "pass"),
    ((-math.inf, 0.1), (True, False), -math.inf, math.inf, "inconclusive"),
    # H2d, H3c: (-inf, 0.10], upper edge closed
    ((-math.inf, 0.1), (True, True), -1.0, 0.1, "pass"),
    ((-math.inf, 0.1), (True, True), 0.1, 0.5, "inconclusive"),
    ((-math.inf, 0.1), (True, True), float(np.nextafter(0.1, np.inf)), 0.5, "fail"),
    # H3b weight: [0, 0.2), lower edge closed, upper open
    ((0.0, 0.2), (True, False), 0.0, 0.1, "pass"),
    ((0.0, 0.2), (True, False), 0.0, 0.2, "inconclusive"),
    ((0.0, 0.2), (True, False), 0.2, 0.3, "fail"),
    ((0.0, 0.2), (True, False), -0.1, 0.0, "inconclusive"),
    ((0.0, 0.2), (True, False), -0.2, -0.1, "fail"),
]


@pytest.mark.parametrize("band,closed,lower,upper,expected", VERDICT_CASES)
def test_interval_verdict_hand_classified_cases(
        band: tuple[float, float], closed: tuple[bool, bool], lower: float, upper: float,
        expected: str) -> None:
    """T5 and the open-band cases: ``interval_verdict`` against a hand-classified table.

    Reference: the A1 definition applied by hand to each (band, closed, interval): pass iff
    the interval lies in the band, fail iff it is disjoint from it, else inconclusive, with
    a closed edge in the band and an open edge out of it (v3 bands of the contract). The
    nextafter cases show that unrounded float64 values are compared. Tolerance: exact.
    """
    assert interval_verdict(lower, upper, band, closed) == expected


def test_interval_verdict_infinite_edge_ignores_closed_flag_and_bad_input_raises() -> None:
    """An infinite band edge is always satisfied whatever ``closed`` says; bad input raises.

    Reference: the contract (item 5): ``closed`` applies to finite edges only. A band with
    a >= b and an interval with lower > upper raise ValueError. Tolerance: exact.
    """
    for closed in itertools.product((True, False), repeat=2):
        assert interval_verdict(-5.0, 0.0, (-math.inf, 0.1), closed) == "pass"
        assert interval_verdict(0.2, 5.0, (0.1, math.inf), closed) == "pass"
    for bad_band in ((1.0, 1.0), (2.0, 1.0), (math.nan, 1.0)):
        with pytest.raises(ValueError):
            interval_verdict(0.0, 1.0, bad_band)
    with pytest.raises(ValueError):
        interval_verdict(1.0, 0.0, (0.0, 2.0))


def test_combine_verdicts_all_two_and_three_part_cases() -> None:
    """``combine_verdicts``: fail dominates, then pass needs all parts, else inconclusive.

    Reference: v3 section 7 ("fail if any part fails; pass if all pass; otherwise
    inconclusive") enumerated as a hand table over 3^2 = 9 and 3^3 = 27 combinations,
    classified here by counting the labels (not by calling the function). A single part,
    an iterator input, an empty input and an unknown string are also checked. Exact.
    """
    labels = ("pass", "fail", "inconclusive")
    for size, count in ((2, 9), (3, 27)):
        combos = list(itertools.product(labels, repeat=size))
        assert len(combos) == count
        for combo in combos:
            n_fail, n_pass = combo.count("fail"), combo.count("pass")
            want = "fail" if n_fail else ("pass" if n_pass == size else "inconclusive")
            assert combine_verdicts(combo) == want, combo
    assert combine_verdicts(["pass", "inconclusive"]) == "inconclusive"
    assert combine_verdicts(["inconclusive", "fail", "pass"]) == "fail"
    assert combine_verdicts(iter(["pass", "pass", "pass"])) == "pass"
    for label in labels:
        assert combine_verdicts([label]) == label
    with pytest.raises(ValueError):
        combine_verdicts([])
    with pytest.raises(ValueError):
        combine_verdicts(["pass", "Pass"])


def test_overall_verdict_all_27_cases_over_the_three_systems() -> None:
    """``overall_verdict``: supported only for (pass, pass, pass); fail on any system fails it.

    Reference: v3 section 7 ("supported: pass on all three systems; not supported: fail on at
    least one system; inconclusive: otherwise"; DEC-0016 O1), enumerated as a hand table over
    3^3 = 27 combinations and classified by counting the labels (not by calling the function).
    Nothing is missing, so the missing list is empty. Exact.
    """
    labels = ("pass", "fail", "inconclusive")
    combos = list(itertools.product(labels, repeat=3))
    assert len(combos) == 27 and V3_SYSTEMS == ("lorenz63", "rossler", "chua")
    n_supported = 0
    for combo in combos:
        want = ("not supported" if combo.count("fail") else
                "supported" if combo.count("pass") == 3 else "inconclusive")
        n_supported += want == "supported"
        assert overall_verdict(dict(zip(V3_SYSTEMS, combo))) == (want, []), combo
    assert n_supported == 1


def test_overall_verdict_with_absent_systems_the_63_cases() -> None:
    """A system that is absent can never be a pass; a fail on a present one still fails it.

    Reference: the same rule by counting, over {pass, fail, inconclusive, absent}^3 minus the
    all-absent case (4^3 - 1 = 63): any fail gives "not supported" whatever is absent; else all
    present and all pass gives "supported"; else "inconclusive". ``missing`` is the absent
    names in the order of ``required``. The all-absent input, a system outside ``required``
    (also when it fails: it must not decide "not supported"), and an unknown verdict string
    raise (PRIME.4). A custom ``required`` is honoured. Exact.
    """
    labels = ("pass", "fail", "inconclusive", "absent")
    combos = [c for c in itertools.product(labels, repeat=3) if c != ("absent",) * 3]
    assert len(combos) == 63
    for combo in combos:
        present = {name: v for name, v in zip(V3_SYSTEMS, combo) if v != "absent"}
        absent = [name for name, v in zip(V3_SYSTEMS, combo) if v == "absent"]
        want = ("not supported" if combo.count("fail") else
                "supported" if combo.count("pass") == 3 else "inconclusive")
        assert overall_verdict(present) == (want, absent), combo
    with pytest.raises(ValueError, match="at least one"):
        overall_verdict({})
    with pytest.raises(ValueError, match="lorenz96"):
        overall_verdict({"lorenz63": "pass", "lorenz96": "fail"})
    with pytest.raises(ValueError, match="verdict"):
        overall_verdict({"lorenz63": "Pass"})
    with pytest.raises(ValueError, match="verdict"):
        overall_verdict({"lorenz63": True})
    assert overall_verdict({"a": "pass", "b": "pass"}, required=("a", "b")) == ("supported", [])
    assert overall_verdict({"a": "pass"}, required=("a", "b")) == ("inconclusive", ["b"])


def test_criterion_verdict_guard_order_and_reasons() -> None:
    """``criterion_verdict`` applies A3 in order: n_states, then computability, then the band.

    Reference: DEC-0008 A3 and the contract (item 7) by hand. ``MIN_STATES`` is 50 (10 blocks
    of 5). (i) 49 states beats everything, including a non-finite estimate and a perfect
    interval; 50 states does not. (ii) A non-finite estimate (NaN or inf) or NaN bound
    gives "not computable" even if the interval would pass. (iii) Infinite bounds that
    cannot pass give "failed resamples >= threshold"; a bound on the band edge gives
    "interval meets band edge"; pass and fail have reason None. (iv) A one-sided band
    can pass with an infinite far bound (reason None). Exact.
    """
    band = (0.75, 1.25)
    assert MIN_STATES == 50
    inside = dict(estimate=1.0, lower=0.9, upper=1.1)
    assert criterion_verdict(**inside, band=band, n_states=49) == ("inconclusive", "n_states < 50")
    assert criterion_verdict(math.nan, 0.9, 1.1, band, n_states=49) == \
        ("inconclusive", "n_states < 50")
    assert criterion_verdict(**inside, band=band, n_states=50) == ("pass", None)
    assert criterion_verdict(math.nan, 0.9, 1.1, band, n_states=50) == \
        ("inconclusive", "not computable")
    assert criterion_verdict(math.inf, 0.9, 1.1, band, n_states=50) == \
        ("inconclusive", "not computable")
    assert criterion_verdict(1.0, math.nan, 1.1, band, n_states=50) == \
        ("inconclusive", "not computable")
    assert criterion_verdict(1.0, -math.inf, math.inf, band, n_states=50) == \
        ("inconclusive", "failed resamples >= threshold")
    assert criterion_verdict(1.0, 1.25, 1.4, band, n_states=50) == \
        ("inconclusive", "interval meets band edge")
    assert criterion_verdict(1.4, 1.3, 1.5, band, n_states=50) == ("fail", None)
    # One infinite bound is enough for the failed-resample reason (not both required).
    reason = "failed resamples >= threshold"
    assert criterion_verdict(1.0, -math.inf, 1.1, band, n_states=50) == ("inconclusive", reason)
    assert criterion_verdict(1.0, 0.9, math.inf, band, n_states=50) == ("inconclusive", reason)
    assert criterion_verdict(1.0, -math.inf, math.inf, band, n_states=50) == \
        ("inconclusive", reason)
    assert criterion_verdict(0.9, 0.8, 0.95, (0.7, math.inf), (True, False), n_states=50) == \
        ("pass", None)
    assert criterion_verdict(0.9, 0.8, math.inf, (0.7, math.inf), (True, False), n_states=50) == \
        ("pass", None)


# ---------------------------------------------------------------------------------------
# WU-0002.11b: the dropped resamples of block_bootstrap are counted; the Kaplan-Meier
# hazard-0 branch (inventory row T1) is justified.
# ---------------------------------------------------------------------------------------


def _nan_on_calls(x_values: np.ndarray, nan_calls: set[int]) -> Callable[[np.ndarray], float]:
    """Statistic: the mean of the selected items, NaN on the listed call numbers (0-based).

    ``block_bootstrap`` and ``block_bootstrap_dropped`` call the statistic once per resample in
    order (calls 0..B-1) and then once on all items (call B), so a fresh closure injects the
    same failures into any function that follows that order.
    """
    calls = itertools.count()
    return lambda idx: float("nan") if next(calls) in nan_calls else float(np.mean(x_values[idx]))


def test_block_bootstrap_dropped_counts_nan_resamples_and_keeps_the_numbers() -> None:
    """B1: ``n_dropped`` is the number of NaN resamples; (est, lo, hi) are the old values bitwise.

    Reference: NaN is injected into exactly 3 of B = 40 resamples (calls 4, 11, 25), so the
    count is known by construction. The interval is compared with ``block_bootstrap`` and with
    the verbatim pre-refactor copy of this file, both run with their own fresh closure that
    injects the same calls. Tolerance: none, ``==`` on the tuples (same draws, same
    expressions). Also: all resamples NaN gives ``n_dropped == B`` and NaN bounds (the
    All-NaN slice, whose RuntimeWarning is expected and checked); a +inf resample is not
    dropped by ``np.nanquantile`` (it can turn a bound into inf or NaN) and so not counted; no
    failure counts 0.
    """
    x_values = np.random.default_rng(5).standard_normal(60)
    inject = {4, 11, 25}
    est, lo, hi, n_dropped = block_bootstrap_dropped(_nan_on_calls(x_values, inject), 60, 40, 5, 3)
    assert n_dropped == 3
    assert (est, lo, hi) == block_bootstrap(_nan_on_calls(x_values, inject), 60, 40, 5, 3)
    assert (est, lo, hi) == _pre_refactor_block_bootstrap(_nan_on_calls(x_values, inject), 60,
                                                          40, 5, 3)
    assert math.isfinite(est) and math.isfinite(lo) and math.isfinite(hi)

    *_, none_dropped = block_bootstrap_dropped(_mean_of(x_values), 60, 40, 5, 3)
    assert none_dropped == 0

    with pytest.warns(RuntimeWarning, match="All-NaN"):
        est_all, lo_all, hi_all, n_all = block_bootstrap_dropped(
            lambda idx: float("nan"), 60, 40, 5, 3)
    assert n_all == 40 and math.isnan(lo_all) and math.isnan(hi_all) and math.isnan(est_all)

    def with_inf() -> Callable[[np.ndarray], float]:
        calls = itertools.count()
        return lambda idx: float("inf") if next(calls) in (2, 9) \
            else float(np.mean(x_values[idx]))

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)  # inf - inf inside np.quantile's lerp
        *rest, inf_dropped = block_bootstrap_dropped(with_inf(), 60, 40, 5, 3)
        old_inf = block_bootstrap(with_inf(), 60, 40, 5, 3)
    assert inf_dropped == 0  # an infinite resample is not NaN: nanquantile keeps it, not counted
    assert np.array_equal(rest, old_inf, equal_nan=True)


def _exact_km(durations: list[int], events: list[bool], horizon_max: int) -> list[Fraction]:
    """Product-limit survival in exact rational arithmetic (the textbook definition)."""
    survival, out = Fraction(1), []
    for t in range(1, horizon_max + 1):
        at_risk = sum(d >= t for d in durations)
        deaths = sum(d == t and e for d, e in zip(durations, events))
        if at_risk > 0:
            survival *= 1 - Fraction(deaths, at_risk)
        out.append(survival)
    return out


def test_kaplan_meier_all_events_before_h_max_gives_exact_zero_after_the_last_event() -> None:
    """B4 (a), T1: with every subject having an event before H_max, S = 0 exactly from the last
    event on, and the curve equals the exact product-limit before it.

    Reference: the product-limit estimator in exact rational arithmetic (``_exact_km``,
    ``fractions.Fraction``), independent of the NumPy implementation. At the last event time
    ``t_L`` everyone still at risk has an event, so ``deaths / at_risk = d / d = 1`` in IEEE
    and ``1 - 1 = 0`` exactly: S(t_L) is exactly 0 and the cumulative product stays 0. Before
    that, tolerance ``rel = 1e-15``: at most 5 floating-point products of O(1) numbers (error
    below 5 * 1.1e-16). Hand values for the first case: S = (1, 3/4, 1/4, 1/4, 0, 0, 0, 0),
    median 3, restricted mean 1 + 2.25 = 3.25.
    """
    cases = [([2, 3, 3, 5], [True] * 4, 8),
             ([1, 1, 4, 4, 4, 6], [True] * 6, 10),
             ([7], [True], 9)]
    for durations, events, horizon_max in cases:
        curve = kaplan_meier(np.array(durations), np.array(events), horizon_max)
        last = max(durations)
        assert np.array_equal(curve.survival[last - 1:], np.zeros(horizon_max - last + 1))
        expected = _exact_km(durations, events, horizon_max)
        assert curve.survival == pytest.approx([float(v) for v in expected], rel=1e-15, abs=0)
    first = kaplan_meier(np.array([2, 3, 3, 5]), np.ones(4, dtype=bool), 8)
    assert first.survival == pytest.approx([1, 0.75, 0.25, 0.25, 0, 0, 0, 0], rel=1e-15, abs=0)
    assert first.median() == 3.0
    assert first.restricted_mean() == pytest.approx(3.25, rel=1e-15)


def test_kaplan_meier_empty_input_is_all_ones_with_nan_median() -> None:
    """B4 (b), T1 hypothesis (ii): n = 0 gives S = 1 at every horizon, a NaN median and a
    restricted mean of H_max.

    Reference: the product-limit definition with an empty risk set at every time (the hazard is
    0 by convention, so the product is empty and equals 1); the restricted mean is
    ``1 + sum_{H < H_max} 1 = H_max``. Exact equalities. The integer dtype of the empty
    ``durations`` is required (``np.bincount`` rejects floats), as the docstring says.
    """
    empty = np.array([], dtype=int)
    curve = kaplan_meier(empty, empty.astype(bool), 6)
    assert np.array_equal(curve.survival, np.ones(6))
    assert np.array_equal(curve.times, np.arange(1, 7))
    assert math.isnan(curve.median())
    assert curve.restricted_mean() == 6.0
