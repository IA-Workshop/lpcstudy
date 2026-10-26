"""Tests of experiment E of phase J (WU-0049, ``lpcstudy/mechanisms.py``).

* ``m(H)`` on a hand-built case with an analytic answer, and the
  ``0.5 sigma_x`` restriction of the mathematics specification;
* Spearman's rho against ``scipy.stats.spearmanr`` (an independent code),
  with failed resamples counted;
* the descriptive statistics of E-H3c (tail share, autocorrelation, the
  variance split, the bimodality coefficient) against hand or population
  values;
* the three reading rules, fixed in advance, on hand-built records.

Random inputs come from fixed ``np.random.default_rng(<int>)``.
"""

from __future__ import annotations

import math

import numpy as np
import pytest
from scipy.stats import spearmanr

from lpcstudy import contribution as cb
from lpcstudy import mechanisms as me


# ------------------------------------------------------------------- m(H)
def test_amplification_mismatch_is_exact_on_exponential_growth() -> None:
    """``E_C = a e^{2 lc H}``, ``E_P = b e^{2 lp H}`` give ``m = 2 (lc - lp)(H - H0)``.

    Reference: that closed form. The restriction keeps an entry where both
    r.m.s. errors are at most 0.5 at ``H`` and at ``H_0``; a state above 0.5
    at ``H_0`` is excluded at every horizon. Tolerance: 1e-12 absolute (two
    logs of ratios of numbers of order 1e-4 to 1, round-off near 1e-15).
    """
    h = np.arange(1, 121, dtype=float)
    a = np.array([1e-4, 4e-4, 0.3])
    b = np.array([2e-4, 1e-4, 0.3])
    lc = np.array([0.04, 0.01, 0.001])
    lp = np.array([0.02, 0.025, 0.001])
    e_c = a[:, None] * np.exp(2 * lc[:, None] * h)
    e_p = b[:, None] * np.exp(2 * lp[:, None] * h)
    ref = 29
    m, kept = me.amplification_mismatch(e_c, e_p, ref)
    exact = 2 * (lc - lp)[:, None] * (h - h[ref])
    np.testing.assert_allclose(m, exact, rtol=0, atol=1e-12)
    small = (np.sqrt(e_c) <= 0.5) & (np.sqrt(e_p) <= 0.5)
    np.testing.assert_array_equal(kept[:2], small[:2])
    assert not kept[2].any()  # sqrt(0.3 e^{0.06}) > 0.5 at H_0
    assert kept[0, :30].all() and not kept[0, -1]


def test_error_correlation_is_the_uncentered_ratio() -> None:
    """``C / sqrt(E_C E_P)``: 1 for equal errors, NaN for a zero moment."""
    e = np.array([[0.04, 0.0]])
    out = me.error_correlation(
        e, np.array([[0.04, 0.1]]), np.array([[0.04, 0.0]])
    )
    assert out[0, 0] == pytest.approx(1.0, rel=1e-15) and np.isnan(out[0, 1])


# ----------------------------------------------------------- statistics
def test_spearman_matches_scipy_with_ties_and_counts_failures() -> None:
    """Spearman's rho against ``scipy.stats.spearmanr`` (average ranks).

    Tolerance: 1e-12 absolute (sums of 300 products of ranks). A mask that
    leaves fewer than three states in a resample makes it failed (counted).
    """
    rng = np.random.default_rng(4911)
    x = rng.integers(0, 20, 300).astype(float)
    y = x + rng.standard_normal(300) * 5
    assert abs(me.spearman(x, y) - spearmanr(x, y).statistic) <= 1e-12
    index = cb.resample_indices(300, 40, 5, rng)
    row = me.spearman_row(x, y, index)
    assert abs(row["estimate"] - spearmanr(x, y).statistic) <= 1e-12
    assert row["n_failed_resamples"] == 0
    mask = np.zeros(300, bool)
    mask[0] = True  # one state: every resample is constant or too small
    sparse = me.spearman_row(x, y, index, mask)
    assert sparse["estimate"] is None and sparse["n_failed_resamples"] == 40


def test_median_row_counts_empty_resamples() -> None:
    """A resample with no masked state is failed, never filled."""
    values = np.arange(10, dtype=float)
    index = np.array(
        [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [5, 5, 5, 5, 5, 6, 6, 6, 6, 6]]
    )
    mask = np.zeros(10, bool)
    mask[:3] = True
    row = me.median_row(values, index, mask, level=0.5)
    assert row["estimate"] == 1.0 and row["n_failed_resamples"] == 1


def test_tail_share_autocorrelation_and_variance_split() -> None:
    """Hand values: a tail of exactly one half; alternating signs; total variance.

    * 99 ones and one 99: the top 1% (one entry) holds 99/198 = 1/2.
    * ``(-1)^t`` (n even): lag-1 autocorrelation ``-(n - 1)/n``, lag-2
      ``(n - 2)/n``.
    * within + between = total (law of total variance), 1e-12 relative, and
      the between part equals a direct sum over the group means.
    """
    assert me.tail_share(np.r_[np.ones(99), 99.0]) == 0.5
    with pytest.raises(ValueError):
        me.tail_share(np.array([1.0, -1.0]))
    n = 100
    alt = (-1.0) ** np.arange(n)
    ac = me.autocorrelation(alt, 2)
    assert ac[0] == pytest.approx(-(n - 1) / n, rel=1e-14)
    assert ac[1] == pytest.approx((n - 2) / n, rel=1e-14)
    rng = np.random.default_rng(4912)
    groups = rng.integers(0, 5, 400)
    values = groups * 0.3 + rng.standard_normal(400)
    split = me.variance_split(values, groups)
    assert split["within"] + split["between"] == pytest.approx(
        split["total"], rel=1e-12
    )
    between = (
        sum(
            np.sum(groups == g)
            * (values[groups == g].mean() - values.mean()) ** 2
            for g in range(5)
        )
        / 400
    )
    assert split["between"] == pytest.approx(between, rel=1e-12)


def test_bimodality_coefficient_of_known_shapes() -> None:
    """Sarle's BC: about 1/3 for a normal sample, about 1 for two points.

    References: population values (normal: skewness 0, excess kurtosis 0, so
    BC -> 1/3; a symmetric two-point law: excess kurtosis -2, so BC -> 1).
    Tolerance: 0.01. For the normal sample (n = 200000) the standard errors
    of skewness and kurtosis are sqrt(6/n) = 0.0055 and sqrt(24/n) = 0.011,
    which move BC = 1/(3 + k) by about 0.0012; the two-point sample is exact
    up to O(1/n) = 1e-4 corrections.
    """
    rng = np.random.default_rng(4913)
    assert me.bimodality_coefficient(
        rng.standard_normal(200_000)
    ) == pytest.approx(1 / 3, abs=0.01)
    two = np.r_[np.full(5000, -1.0), np.full(5000, 1.0)]
    assert me.bimodality_coefficient(two) == pytest.approx(1.0, abs=0.01)
    assert me.bimodality_coefficient(two) > me.UNIMODAL_BC


def test_terciles_split_distinct_values_evenly() -> None:
    """Three equal groups for 300 distinct values; cut points are quantiles."""
    values = np.random.default_rng(4914).permutation(300).astype(float)
    groups, cuts = me.terciles(values)
    assert np.bincount(groups).tolist() == [100, 100, 100]
    assert cuts == pytest.approx(np.quantile(values, [1 / 3, 2 / 3]).tolist())


# ---------------------------------------------------------------- readings
def _h2a_row(ci, low, high, kept=200) -> dict:
    return {
        "n_kept": kept,
        "spearman_m_I": {"ci": ci},
        "median_abs_drift_by_tercile": [low, 0.0, high],
    }


def test_h2a_reading_rule() -> None:
    """Consistent / not consistent / not determined (addendum S2).

    A horizon supports only if its interval lies beyond the margin 0.1 on
    one side (strict), with the drift condition. Manufactured intervals on
    both sides of +0.1 and of -0.1.
    """
    rows = {
        "30": _h2a_row([None, None], 0, 0),
        "60": _h2a_row([0.12, 0.3], 0.1, 0.2),
    }
    assert me.h2a_reading(rows, 30)["reading"] == "consistent"
    rows["60"] = _h2a_row([-0.3, -0.12], 0.1, 0.2)
    assert me.h2a_reading(rows, 30)["reading"] == "consistent"
    for inside in ([0.05, 0.3], [0.1, 0.3], [-0.3, -0.05], [-0.3, -0.1]):
        # excludes 0 but not beyond the margin: no longer supports
        rows["60"] = _h2a_row(inside, 0.1, 0.2)
        assert me.h2a_reading(rows, 30)["reading"] == "not determined", inside
    rows["60"] = _h2a_row([0.12, 0.3], 0.3, 0.2)  # drift not larger in high-I
    assert me.h2a_reading(rows, 30)["reading"] == "not determined"
    rows["60"] = _h2a_row([-0.05, 0.08], 0.1, 0.2)
    rows["120"] = _h2a_row([-0.09, 0.02], 0.1, 0.2)
    assert me.h2a_reading(rows, 30)["reading"] == "not consistent"
    rows["120"] = _h2a_row([-0.2, 0.02], 0.1, 0.2)
    assert me.h2a_reading(rows, 30)["reading"] == "not determined"
    few = {"60": _h2a_row([0.1, 0.3], 0.1, 0.2, kept=49)}
    assert me.h2a_reading(few, 30)["reading"].startswith(
        "not determined (fewer"
    )


def test_h2e_reading_rule() -> None:
    """Rise with a negative association reads consistent; the rest as fixed."""

    def part(m_ci, s_ci) -> dict:
        return {
            "median_delta_corr": {"ci": m_ci},
            "spearman_delta_corr_delta_R": {"ci": s_ci},
        }

    assert me.h2e_part_reading(part([0.1, 0.2], [-0.3, -0.1])) == "consistent"
    assert me.h2e_part_reading(part([0.1, 0.2], [0.1, 0.3])) == "not consistent"
    assert (
        me.h2e_part_reading(part([-0.2, -0.1], [-0.3, -0.1]))
        == "not consistent"
    )
    assert (
        me.h2e_part_reading(part([0.1, 0.2], [-0.3, 0.1])) == "not determined"
    )
    assert (
        me.h2e_part_reading(part([None, 0.2], [-0.3, -0.1])) == "not determined"
    )


def _h3c(
    width: float, share: float = 0.2, pct: float = 0.8, bc: float = 0.4
) -> dict:
    return {
        "H3c": {"width": width},
        "tail_share": {"abs_difference": share},
        "top_abs_difference": {"median_I_percentile": pct},
        "marginals_deployable": {
            x: {"bimodality_coefficient": bc} for x in "ROIN"
        },
    }


def test_h3c_reading_rule() -> None:
    """The pattern check first, then the two parts (rules fixed in advance)."""
    blocks = {"lorenz63": _h3c(0.4), "rossler": _h3c(0.05), "chua": _h3c(0.2)}
    assert me.h3c_reading(blocks)["reading"] == "consistent"
    blocks["chua"] = _h3c(0.5)
    out = me.h3c_reading(blocks)
    assert out["reading"] == "not determined (pattern not reproduced)"
    assert out["lorenz63_part"] == "consistent"
    blocks = {
        "lorenz63": _h3c(0.4, share=0.04),
        "rossler": _h3c(0.05),
        "chua": _h3c(0.2),
    }
    assert me.h3c_reading(blocks)["reading"] == "not consistent"
    blocks = {
        "lorenz63": _h3c(0.4),
        "rossler": _h3c(0.05, bc=0.6),
        "chua": _h3c(0.2),
    }
    assert me.h3c_reading(blocks)["rossler_part"] == "not consistent"
    blocks = {
        "lorenz63": _h3c(0.4, share=0.07),
        "rossler": _h3c(0.05),
        "chua": _h3c(0.2),
    }
    assert me.h3c_reading(blocks)["reading"] == "not determined"
    assert math.isclose(me.UNIMODAL_BC, 5 / 9)
