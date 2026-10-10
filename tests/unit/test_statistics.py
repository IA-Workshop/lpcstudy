"""Tests for lpcstudy.statistics: Kaplan-Meier, log-rank, Holm, partial correlation."""

from __future__ import annotations

import math

import numpy as np
import pytest
from scipy import stats as sps

from lpcstudy.statistics import holm_adjust, kaplan_meier, logrank_test, \
    partial_correlation


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
