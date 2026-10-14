"""Tests of ``tools/rehearsal_diagnostics.py`` (WU-0003.8; plan B2 row .8, acceptance c1 to c7).

DEVELOPMENT: synthetic arrays in the dump schema ``lpcstudy.states/1``; no run output exists yet, so
no real-data check is made here (it waits for the rehearsal, R1). Needs owner review before freeze
(statistics). References, none of them the tool's own output:

* c1: the **numerical Gateaux derivative** of each smooth functional at the empirical measure,
  ``(T(w_eps) - T(w_0))/eps`` with ``w_eps = (1 - eps)/n + eps 1{j = i}``, ``eps = 1e-6``, the
  functional written in the test from its definition with weights (weighted least squares by
  scaling rows with ``sqrt(w)``, weighted R^2, weighted ratio). The fitted models (Q-N) are held
  fixed. Compared as ``max_i |psi_i - G_i| <= 1e-4 max_i |G_i|``: the one-sided difference has
  truncation ``eps T''/2`` (about ``1e-6 psi^2``, at most 1e-5 of ``max |G|`` at ``|psi|`` up to
  10) and round-off ``u/eps`` (about 1e-10), so 1e-4 is 10x the truncation. Sign types: hand values
  (tie-free: the exact rank score; ties: the mid-rank rule, which does not sum to 0 at an atom).
* c2: the autocorrelation of an alternating +-1 series (a closed form).
* c3: ``V*(b)`` against a naive loop over the blocks with ``math.fsum`` (relative 1e-12: about
  ``n`` unit round-offs, n <= 500, so 5e-14, with margin 20).
* c4, c5: ``beta_5`` at 0 and 0.3 (closed forms in the plan), a central difference of it, and the
  trigamma identity ``psi'(z) - psi'(z + 1) = 1/z^2``.
* c6: the model of ``m5_d5split.py`` (seed 20261017) re-implemented here, the order law
  ``m(M) = c (M^-p - 800^-p)``, and hand-built three-way readings (dyadic numbers, exact).
* c7: constructed sets where ``f_b`` and the split-half mean bias are decided by hand.

The synthetic world builds a dump and a results tree whose every compared statistic is computed in
this file by an independent route (``np.corrcoef`` of ``lstsq`` residuals, ``scipy.stats.spearmanr``
per row, loops for the ranges, ``np.polyfit`` for the slope), so a full run must give exit 0, and
a perturbed leaf exit 1. Each test is under 5 s (n = 80 states, 100 resamples, 50 permutations).
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy import stats as sps

from lpcstudy.data import make_rng

ROOT = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location("rehearsal_diagnostics",
                                               ROOT / "tools" / "rehearsal_diagnostics.py")
assert _SPEC is not None and _SPEC.loader is not None
rd = importlib.util.module_from_spec(_SPEC)
sys.modules["rehearsal_diagnostics"] = rd
_SPEC.loader.exec_module(rd)

SEED = 20261030


def rng_for(label: str) -> np.random.Generator:
    """A generator from ``make_rng`` (the project's only source of randomness)."""
    return make_rng(SEED, "test_rehearsal_diagnostics", label)


# ------------------------------------------------------------------------------------------ c1
EPS = 1e-6


def gateaux(functional, n: int) -> np.ndarray:
    """``(T(w_eps) - T(w_0))/eps`` at every point, ``T`` a function of a weight vector."""
    base = np.full(n, 1.0 / n)
    t0 = functional(base)
    out = np.empty(n)
    for i in range(n):
        w = (1.0 - EPS) * base
        w[i] += EPS
        out[i] = (functional(w) - t0) / EPS
    return out


def assert_gateaux(psi: np.ndarray, truth: np.ndarray) -> None:
    """The c1 comparison: ``max |psi - G| <= 1e-4 max |G|``, and psi sums to 0 (1e-12 of sum |psi|)."""
    assert np.max(np.abs(psi - truth)) <= 1e-4 * np.max(np.abs(truth))
    assert abs(psi.sum()) <= 1e-12 * np.abs(psi).sum()


def weighted_corr_residuals(w: np.ndarray, y: np.ndarray, x: np.ndarray, q: np.ndarray) -> float:
    """Weighted partial correlation by weighted least squares (rows scaled by ``sqrt(w)``)."""
    design = np.column_stack([np.ones(len(y)), q])
    root = np.sqrt(w)[:, None]
    res = []
    for target in (y, x):
        beta = np.linalg.lstsq(design * root, target * root[:, 0], rcond=None)[0]
        res.append(target - design @ beta)
    ey, ex = res
    return float(np.sum(w * ey * ex) / math.sqrt(np.sum(w * ey**2) * np.sum(w * ex**2)))


def test_c1_partial_correlation_influence_equals_gateaux_derivative() -> None:
    """psi of the partial correlation (H2a(ii)) equals the Gateaux derivative, n = 50, with a domain.

    Reference: the weighted partial correlation functional above, over the domain rows only (the
    states outside it carry no weight and psi 0). Tolerance: see the module docstring.
    """
    rng = rng_for("c1-partial")
    n = 50
    q = rng.standard_normal((n, 5))
    x = 0.6 * q[:, 0] + rng.standard_normal(n)
    y = 0.3 * x - 0.5 * q[:, 1] + rng.standard_normal(n)
    dom = rng.random(n) < 0.8
    psi, r = rd.psi_partial_corr(y, x, q, dom)
    assert np.all(psi[~dom] == 0.0)
    rows = np.flatnonzero(dom)
    truth = gateaux(lambda w: weighted_corr_residuals(w, y[rows], x[rows], q[rows]), len(rows))
    assert_gateaux(psi[rows], truth)
    assert r == pytest.approx(weighted_corr_residuals(np.full(len(rows), 1 / len(rows)),
                                                      y[rows], x[rows], q[rows]), abs=1e-12)


def test_c1_slope_ratio_difference_and_delta_r2_influences_equal_gateaux() -> None:
    """psi of the OLS slope (H1b), a ratio of means (H3c, H2d), a mean (H2c, H2b) and Delta R^2 (Q-N).

    Reference: the weighted functionals written from their definitions; the Q-N models are fixed
    arrays (``pred3``, ``pred4``), the domain a boolean mask.
    """
    rng = rng_for("c1-others")
    n = 50
    x = rng.standard_normal(n)
    y = 0.8 * x + 0.5 * rng.standard_normal(n)

    def slope(w: np.ndarray) -> float:
        xm, ym = np.sum(w * x), np.sum(w * y)
        return float(np.sum(w * (x - xm) * (y - ym)) / np.sum(w * (x - xm) ** 2))

    assert_gateaux(rd.psi_slope(x, y), gateaux(slope, n))
    a, b = np.exp(rng.standard_normal(n)), np.exp(0.5 * rng.standard_normal(n))
    assert_gateaux(rd.psi_ratio(a, b), gateaux(lambda w: float(np.sum(w * a) / np.sum(w * b)), n))
    assert_gateaux(rd.psi_mean(a), gateaux(lambda w: float(np.sum(w * a)), n))
    target = rng.standard_normal(n)
    f3, f4 = 0.4 * target + 0.3 * rng.standard_normal(n), 0.6 * target + 0.3 * rng.standard_normal(n)
    dom = rng.random(n) < 0.85
    rows = np.flatnonzero(dom)
    psi, delta = rd.psi_delta_r2(target, f3, f4, dom)
    assert np.all(psi[~dom] == 0.0)

    def gain(w: np.ndarray) -> float:
        yy = target[rows]
        ybar = np.sum(w * yy)
        total = np.sum(w * (yy - ybar) ** 2)
        return float((np.sum(w * (yy - f3[rows]) ** 2) - np.sum(w * (yy - f4[rows]) ** 2)) / total)

    assert_gateaux(psi[rows], gateaux(gain, len(rows)))
    assert delta == pytest.approx(gain(np.full(len(rows), 1 / len(rows))), abs=1e-12)


def test_c1_sign_type_is_the_exact_rank_score_and_the_mid_rank_rule_with_ties() -> None:
    """psi_sign by hand: tie-free odd and even samples, a sample with ties, a domain.

    Reference: the rule ``1{v < m} + 1/2 1{v = m} - 1/2`` evaluated by hand. [5,1,4,2,3] has median
    3: the two below score +1/2, the two above -1/2, the median itself 0. [1,2,3,4] has median 2.5.
    [0,0,0,1,2] has median 0 and an atom of three: the atom scores 1/2 - 1/2 = 0, the others -1/2
    (the sum is -1: at an atom the rule does not sum to 0, so the diagnostics centre the series).
    A domain mask leaves 0 outside. Exact.
    """
    assert rd.psi_sign(np.array([5.0, 1.0, 4.0, 2.0, 3.0])).tolist() == [-0.5, 0.5, -0.5, 0.5, 0.0]
    assert rd.psi_sign(np.array([1.0, 2.0, 3.0, 4.0])).tolist() == [0.5, 0.5, -0.5, -0.5]
    assert rd.psi_sign(np.array([0.0, 0.0, 0.0, 1.0, 2.0])).tolist() == [0.0, 0.0, 0.0, -0.5, -0.5]
    dom = np.array([True, False, True, True, False, True])
    out = rd.psi_sign(np.array([9.0, 100.0, 1.0, 5.0, -3.0, 7.0]), dom)
    assert out.tolist() == [-0.5, 0.0, 0.5, 0.5, 0.0, -0.5]  # domain values 9, 1, 5, 7: median 6
    with pytest.raises(rd.NotComputable, match="empty domain"):
        rd.psi_sign(np.array([1.0, 2.0]), np.array([False, False]))


# ------------------------------------------------------------------------------------------ c2, c3
def test_c2_acf_of_alternating_series_is_minus_n_minus_one_over_n() -> None:
    """acf(1) of +-1, +-1, ... with even n is -(n - 1)/n; acf(2) is +(n - 2)/n (closed forms).

    Reference: the sum ``sum x_t x_{t+k} = (-1)^k (n - k)`` over ``sum x_t^2 = n`` for a series of
    mean 0. Tolerance 1e-12 (a handful of exact additions of integers; the division rounds once).
    """
    for n in (20, 50, 500):
        x = np.where(np.arange(n) % 2 == 0, 1.0, -1.0)
        lags = rd.acf(x)
        assert lags[0] == pytest.approx(-(n - 1) / n, abs=1e-12)
        assert lags[1] == pytest.approx((n - 2) / n, abs=1e-12)


def test_acf_refuses_a_constant_or_short_series_and_nonfinite_values() -> None:
    """Bad input raises ``NotComputable`` (PRIME.4): constant, too short, NaN."""
    for bad, why in ((np.ones(30), "constant"), (np.arange(10.0), "not longer"),
                     (np.r_[np.ones(29), np.nan], "non-finite")):
        with pytest.raises(rd.NotComputable, match=why):
            rd.acf(bad)


def naive_block_variance(x: list[float], b: int) -> float:
    """``b`` times the population variance of the overlapping block means, by explicit loops."""
    means = [math.fsum(x[i:i + b]) / b for i in range(len(x) - b + 1)]
    centre = math.fsum(means) / len(means)
    return b * math.fsum((m - centre) ** 2 for m in means) / len(means)


def test_c3_block_variance_equals_a_naive_loop() -> None:
    """V*(b) (sliding windows) and the row-wise cumulative-sum form equal the loop to 1e-12 relative.

    Reference: ``naive_block_variance``. A series with a large offset checks that the centring in
    the tool is not what makes it agree: both forms are shift invariant.
    """
    rng = rng_for("c3")
    for n, b in ((60, 5), (101, 10), (500, 20), (7, 7)):
        x = rng.standard_normal(n) * 3.0 + 1000.0
        ref = naive_block_variance(x.tolist(), b)
        assert rd.block_variance(x, b) == pytest.approx(ref, rel=1e-12)
        assert rd.block_variances(x[None, :], b)[0] == pytest.approx(ref, rel=1e-12)
    with pytest.raises(rd.NotComputable, match="does not fit"):
        rd.block_variance(np.ones(4), 5)


# ------------------------------------------------------------------------------------------ c4, c5
def test_c4_beta_five_closed_values_slope_and_standard_error() -> None:
    """beta_5(0) = 1 exactly, beta_5(0.3) = 0.8685 +- 5e-5; the slope is -0.4 at 0 and matches a
    central difference; the delta-method SE at n = 500 is |slope| sqrt((1 - phi^2)/n).

    Reference: the plan's values (0.8685 from the polynomial 1 + 2(0.24 + 0.054 + 0.0108 + 0.00162)
    = 1.61284 times 0.7/1.3). The central difference with h = 1e-5 has truncation about h^2 f'''/6
    (1e-10) so 1e-7 is safe.
    """
    assert rd.beta_five(0.0) == 1.0
    assert rd.beta_five(0.3) == pytest.approx(0.8685, abs=5e-5)
    assert rd.beta_five_slope(0.0) == pytest.approx(-0.4, abs=1e-12)
    h = 1e-5
    for phi in (-0.2, 0.1, 0.3, 0.5):
        numeric = (rd.beta_five(phi + h) - rd.beta_five(phi - h)) / (2 * h)
        assert rd.beta_five_slope(phi) == pytest.approx(numeric, abs=1e-7)
    lags = 0.3 ** np.arange(1, 11)  # exactly geometric
    reading = rd.beta_reading(lags, 500)
    assert reading["se"] == pytest.approx(abs(rd.beta_five_slope(0.3)) * math.sqrt(0.91 / 500))
    assert reading["used"] and not reading["fires"]  # 0.8685 + 2 SE is above the stress value
    strong = rd.beta_reading(0.5 ** np.arange(1, 11), 1000)  # beta_5(0.5) well below 0.8685
    assert strong["used"] and strong["fires"]
    broken = rd.beta_reading(np.array([0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]), 1000)
    assert not broken["used"] and not broken["fires"]


def test_c5_trigamma_identity_and_the_e_to_four_projection() -> None:
    """psi'(1) - psi'(2) = 1 to 1e-12; psi'(z) - psi'(z + 1) = 1/z^2; the projection from E = 2.

    Reference: the identity (it follows from psi'(z) = sum_{k >= 0} 1/(z + k)^2). A log-SD of 1.5
    at E = 2 projects to sqrt(2.25 - 1) = 1.118034; at E = 4 the projection is the value itself;
    a value below 1 at E = 2 has no projection (None, never NaN).
    """
    assert rd.trigamma(1.0) - rd.trigamma(2.0) == pytest.approx(1.0, abs=1e-12)
    for z in (0.5, 1.0, 2.0, 7.5):
        assert rd.trigamma(z) - rd.trigamma(z + 1.0) == pytest.approx(1.0 / z**2, rel=1e-12)
    assert rd.logsd_at_draws(1.5, 2) == pytest.approx(math.sqrt(1.25), rel=1e-12)
    assert rd.logsd_at_draws(1.5, 4) == pytest.approx(1.5, rel=1e-12)
    assert rd.logsd_at_draws(0.9, 2) is None


# ------------------------------------------------------------------------------------------ readings
def test_acf_readings_by_hand() -> None:
    """The C9 reading: thresholds 0.15 (n <= 500) and 0.11, the case values, the weight between.

    Reference: the rule of amendment 2, B1 item 7.D1 applied by hand. H3c (case 0.16) at n = 500:
    0.10 and 0.13 are within the 0.15 threshold (phi = 0 rows apply); 0.16 is realistic; 0.155 lies
    between, with weight (0.155 - 0.15)/(0.16 - 0.15) = 0.5. At n = 1000 the threshold is 0.11, so
    0.13 is between (weight (0.13 - 0.11)/(0.16 - 0.11) = 0.4). H2a(ii) (case 0.09) at 0.10: both
    readings hold and phi = 0.3 governs. A series with no case value gets only the phi = 0 reading;
    acf1 = -0.2 gets neither. The false-trigger rate is ``2 norm.sf(thr sqrt(n))`` from scipy's
    normal tail (independent of the ``erfc`` form in the tool); tolerance 1e-12 (two evaluations of
    the same tail).
    """
    assert rd.acf_reading("H3c", 0.10, 500)[0].startswith("phi = 0 rows apply")
    assert rd.acf_reading("H3c", 0.16, 500)[0].startswith("phi = 0.3 rows realistic")
    assert rd.acf_reading("H3c", 0.13, 500)[0].startswith("phi = 0 rows apply")
    text, weight = rd.acf_reading("H3c", 0.155, 500)
    assert weight == pytest.approx(0.5, abs=1e-12) and text.startswith("between")
    assert rd.acf_reading("H3c", 0.13, 1000)[1] == pytest.approx(0.4, abs=1e-12)
    text, weight = rd.acf_reading("H2a(ii)", 0.10, 500)
    assert text.startswith("phi = 0.3 rows realistic") and "both readings hold" in text
    assert weight is None
    assert "no case value" in rd.acf_reading("Q-N", 0.05, 500)[0]
    assert rd.acf_reading("H2b(i)", -0.2, 500)[0].startswith("acf1 below")
    for n, thr in ((300, 0.15), (500, 0.15), (1000, 0.11)):
        assert rd.lag_zero_false_trigger(n) == pytest.approx(2 * sps.norm.sf(thr * math.sqrt(n)),
                                                             rel=1e-12)


def test_d2_variance_summary_and_the_a5_rule() -> None:
    """V*(b) ratios and the A5 trigger on hand series.

    Reference: ``naive_block_variance`` for V*(5), V*(10), V*(20) of an AR(1) series with phi = 0.7
    drawn from ``make_rng`` (E V*(10)/V*(5) = 1.43 there, so the rule fires at n = 500; the ratio
    has SD about 0.1). An alternating +-1 series has block means of +-0.2 at b = 5 (V*(5) = 0.2) and
    exactly 0 at b = 10 and 20, so both ratios are 0 and the rule is quiet. A zero series has no
    positive V*(5): ``NotComputable``. Tolerance 1e-12 relative.
    """
    rng = rng_for("d2-summary")
    n = 500
    e = rng.standard_normal(n)
    ar = np.zeros(n)
    for t in range(1, n):
        ar[t] = 0.7 * ar[t - 1] + e[t]
    out = rd.variance_summary(ar)
    ref = [naive_block_variance(ar.tolist(), b) for b in (5, 10, 20)]
    assert out["V5"] == pytest.approx(ref[0], rel=1e-12)
    assert out["ratio10"] == pytest.approx(ref[1] / ref[0], rel=1e-12)
    assert out["ratio20"] == pytest.approx(ref[2] / ref[0], rel=1e-12)
    assert out["fires"] is True
    quiet = rd.variance_summary(np.where(np.arange(60) % 2 == 0, 1.0, -1.0))
    assert quiet["fires"] is False
    with pytest.raises(rd.NotComputable, match="not positive"):
        rd.variance_summary(np.zeros(60))


def test_permutation_null_equals_a_naive_loop_with_the_induced_order() -> None:
    """The pooled null and the observed statistic equal explicit loops, series of two lengths.

    Reference: the contract is ``keys = rng.random((P, n_max))``; permutation ``p`` orders series
    ``i`` (first ``n_i`` states) by ``keys[p, :n_i]``. The test draws the same keys from an equal
    generator and computes every V* with ``naive_block_variance``. Tolerance 1e-12 relative on the
    log ratios (each V* is exact to 1e-12).
    """
    rng = rng_for("perm-data")
    s_long, s_short = rng.standard_normal(40), rng.standard_normal(25)
    n_perm = 12
    obs, null = rd.permutation_null([s_long, s_short], n_perm, rng_for("perm-keys"))
    keys = rng_for("perm-keys").random((n_perm, 40))

    def log_ratio(series: list[float]) -> float:
        return math.log(naive_block_variance(series, 10) / naive_block_variance(series, 5))

    ref_obs = (log_ratio(s_long.tolist()) + log_ratio(s_short.tolist())) / 2
    assert obs == pytest.approx(ref_obs, rel=1e-12)
    for p in range(n_perm):
        parts = []
        for s in (s_long, s_short):
            order = sorted(range(len(s)), key=lambda j: keys[p, j])
            parts.append(log_ratio([float(s[j]) for j in order]))
        assert null[p] == pytest.approx(sum(parts) / 2, rel=1e-12, abs=1e-14)
    with pytest.raises(rd.NotComputable, match="no primary series"):
        rd.permutation_null([], 5, rng_for("x"))


# ------------------------------------------------------------------------------------------ criteria
def test_leading_ranges_and_segment_ranges_by_hand() -> None:
    """H2a(i): the leading small-error segment, eligibility (at least two), the range.

    Reference: three states, three horizons, decided by hand. State 0: small at all three, w =
    (0.1, 0.5, 0.2): range 0.4, eligible. State 1: small only at the first: not eligible (NaN).
    State 2: small at the first two and not the third: range |0.3 - 0.6| = 0.3. A state whose small
    flags are (1, 0, 1) has a leading segment of length 1 (the late small horizon is not an initial
    segment). The fixed segments of the 200-draw moments then give the half-draw ranges.
    Exact (max minus min of the same floats).
    """
    w = np.array([[0.1, 0.5, 0.2], [0.2, 0.9, 0.9], [0.3, 0.6, 0.0], [0.4, 0.8, 0.1]])
    small = np.array([[1, 1, 1], [1, 0, 0], [1, 1, 0], [1, 0, 1]], dtype=bool)
    ranges, eligible, leading = rd.leading_ranges(w, small)
    assert eligible.tolist() == [True, False, True, False]
    assert ranges[0] == 0.5 - 0.1 and ranges[2] == 0.6 - 0.3
    assert np.isnan(ranges[1]) and np.isnan(ranges[3])
    assert leading.tolist() == [[True, True, True], [True, False, False],
                                [True, True, False], [True, False, False]]
    half = rd.segment_ranges(np.array([[0.0, 0.25, 1.0]] * 4), leading)
    assert half[0] == 1.0 and half[2] == 0.25 and half[1] == 0.0  # length 1: range 0


def test_per_state_spearman_ties_constants_and_levels() -> None:
    """H2b(i): per-state Spearman with average ranks, constant rows score 0 and are counted.

    Reference: ``scipy.stats.spearmanr`` per non-constant row; hand values for the rest: a
    nondecreasing row against increasing levels is +1; (1, 0, 0, 0) against 4 levels has average
    ranks (4, 2, 2, 2) so the correlation is the Pearson of (4,2,2,2) with (1,2,3,4) = -0.7746
    (hand: covariance -1.5, sd 0.866 and 1.118 give -0.7746); a constant row scores 0.
    """
    levels = np.array([0.005, 0.01, 0.02, 0.05])
    rows = np.array([[0.1, 0.2, 0.3, 0.9], [1.0, 0.0, 0.0, 0.0], [0.5, 0.5, 0.5, 0.5],
                     [0.0, 0.0, 0.0, 0.4], [0.9, 0.4, 0.2, 0.1]])
    out, n_constant = rd.per_state_spearman(levels, rows)
    assert n_constant == 1 and out[2] == 0.0
    assert out[0] == pytest.approx(1.0, abs=1e-15)
    assert out[1] == pytest.approx(-math.sqrt(0.6), abs=1e-12)
    for i in (0, 1, 3, 4):
        assert out[i] == pytest.approx(sps.spearmanr(levels, rows[i]).statistic, abs=1e-12)


def test_quadratic_controls_and_weight_helpers_by_hand() -> None:
    """Quadratic controls (centred columns) and the oracle weight / unclipped optimum formulas.

    Reference: hand arithmetic. Seeds (0,0), (2,4), (4,2) centre to (-2,-2), (0,2), (2,0): the five
    columns of the first row are -2, -2, 4, 4, 4. Moments (E_C, E_P, C) = (2, 1, 0.5): curvature
    2 + 1 - 1 = 2, u = (1 - 0.5)/2 = 0.25. (2, 1, 1.5): curvature 0, so u is undefined (NaN) and the
    weight uses the package's 1e-300 guard: (1 - 1.5)/1e-300 clips to 0. (2, 3, 0): curvature 5,
    u = 3/5 = 0.6. (1, 4, 0): curvature 5, u = 0.8. A negative curvature (1, 0, 1) also gives w = 0.
    Exact.
    """
    q = rd.quadratic_controls(np.array([[0.0, 0.0], [2.0, 4.0], [4.0, 2.0]]))
    assert q[0].tolist() == [-2.0, -2.0, 4.0, 4.0, 4.0]
    e_c, e_p, c = np.array([2.0, 2.0, 2.0, 1.0]), np.array([1.0, 1.0, 3.0, 4.0]), \
        np.array([0.5, 1.5, 0.0, 0.0])
    u, curv = rd.unclipped_optimum(e_c, e_p, c)
    assert curv.tolist() == [2.0, 0.0, 5.0, 5.0]
    assert u[0] == 0.25 and np.isnan(u[1]) and u[2] == 0.6 and u[3] == 0.8
    w = rd.weight_from_moments(e_c, e_p, c)
    assert w.tolist() == [0.25, 0.0, 0.6, 0.8]
    assert rd.weight_from_moments(np.array([1.0]), np.array([0.0]), np.array([1.0])).tolist() == [0.0]


# ------------------------------------------------------------------------------------------ D3
def test_d3_log_sd_hybrid_state_part_and_exclusions() -> None:
    """log-SD (ddof 1) against ``statistics``-style loops, non-positive values counted, V_i(w).

    Reference: hand arithmetic. ln of (1, e, e^2, e^3) is (0, 1, 2, 3), whose sample SD is
    sqrt(5/3); a zero entry is excluded and counted. V_i(w) = w^2 E_C + (1-w)^2 E_P + 2 w (1-w) C:
    at w = 0.25, E_C = 4, E_P = 8, C = 2: 0.0625 x 4 + 0.5625 x 8 + 2 x 0.1875 x 2 = 0.25 + 4.5 +
    0.75 = 5.5; at w = 0.75: 0.5625 x 4 + 0.0625 x 8 + 0.75 = 2.25 + 0.5 + 0.75 = 3.5, so two draws
    with w = (0.25, 0.75) give the mean 4.5. Exact (dyadic); the SD to 1e-12 relative.
    """
    sigma, bad = rd.log_sd(np.exp(np.arange(4.0)))
    assert sigma == pytest.approx(math.sqrt(5 / 3), rel=1e-12) and bad == 0
    sigma, bad = rd.log_sd(np.array([0.0, 1.0, math.e, math.e**2, math.e**3]))
    assert sigma == pytest.approx(math.sqrt(5 / 3), rel=1e-12) and bad == 1
    with pytest.raises(rd.NotComputable):
        rd.log_sd(np.array([0.0, 0.0, 1.0]))
    e_c, e_p, c = np.array([4.0]), np.array([8.0]), np.array([2.0])
    assert rd.hybrid_state_mse(np.array([0.25]), e_c, e_p, c).tolist() == [5.5]
    assert rd.hybrid_state_mse(np.array([[0.25, 0.75]]), e_c, e_p, c).tolist() == [4.5]


# ------------------------------------------------------------------------------------------ D4
def test_d4_interior_attenuation_on_a_hand_world() -> None:
    """A from the delta method on states with known v and var(y~); the not-delta-valid exclusion.

    Reference: controls are all 0 (the residual is the centred logit), so var(y~) is the population
    variance of ``log(w/(1 - w))`` over the valid states and A^2 = 1 - mean(v)/var(y~) with
    v = s^2/(w (1 - w))^2, s = |u_A - u_B|/2, written here from the definition. Ten interior
    states, of which the last has w = 0.05 and s = 0.03: w - 3 s < 0, so it is excluded (one of
    ten); two more states are at w = 0 and w = 1 (not interior). The all-interior variance
    differs from the valid one. Tolerance 1e-12 relative (a few operations).
    """
    w = np.r_[np.linspace(0.3, 0.7, 9), 0.05, 0.0, 1.0]
    s = np.r_[[0.01, 0.02, 0.015, 0.01, 0.02, 0.01, 0.02, 0.015, 0.01], 0.03, 0.0, 0.0]
    u_a, u_b = w - s, w + s
    q = np.zeros((12, 5))
    lam = np.arange(12.0)
    out = rd.interior_attenuation(u_a, u_b, w, q, lam)
    assert (out["n_interior"], out["n_domain"], out["n_valid"], out["n_excluded_delta"]) == (10, 10, 9, 1)
    ok = list(range(9))
    logit = np.log(w[:10] / (1 - w[:10]))
    centred = logit - logit.mean()  # residualization on the ten-state domain
    var_valid = np.mean((centred[ok] - centred[ok].mean()) ** 2)
    var_all = np.mean((centred - centred.mean()) ** 2)
    mean_v = np.mean(s[ok] ** 2 / (w[ok] * (1 - w[ok])) ** 2)
    assert out["A"] == pytest.approx(math.sqrt(1 - mean_v / var_valid), rel=1e-12)
    assert out["A_all"] == pytest.approx(math.sqrt(1 - mean_v / var_all), rel=1e-12)
    assert out["bias_at_edge"] == pytest.approx(0.1 * (1 - out["A"]), rel=1e-12)
    assert out["n_undefined_halves"] == 0 and out["spearman_brown"]["n_states"] == 10
    nan_halves = u_a.copy()
    nan_halves[2] = np.nan
    assert rd.interior_attenuation(nan_halves, u_b, w, q, lam)["n_undefined_halves"] == 1
    with pytest.raises(rd.NotComputable, match="too few"):
        rd.interior_attenuation(u_a[:5], u_b[:5], w[:5], q[:5], lam[:5])


def test_d4_spearman_brown_value_and_negative_reliability_gives_none() -> None:
    """The Spearman-Brown value 2 r/(1 + r) with r the correlation of the two half logits.

    Reference: ``np.corrcoef`` of the two half logits written in the test (with controls 0 the
    residual of each is its centred value, which a correlation ignores). A world whose half-draw noise
    exceeds the signal (s = 0.08 on w in (0.4, 0.6): mean v = 0.10, var y~ = 0.055) has negative
    reliability and A = None, never NaN. Tolerance 1e-12 relative.
    """
    rng = rng_for("d4-sb")
    n = 40
    w = rng.uniform(0.3, 0.7, n)
    u_a, u_b = w + 0.03 * rng.standard_normal(n), w + 0.03 * rng.standard_normal(n)
    out = rd.interior_attenuation(u_a, u_b, w, np.zeros((n, 5)), np.arange(float(n)))
    sb = out["spearman_brown"]
    r_ab = np.corrcoef(np.log(u_a / (1 - u_a)), np.log(u_b / (1 - u_b)))[0, 1]
    assert sb["r_ab"] == pytest.approx(r_ab, rel=1e-12)
    assert sb["reliability"] == pytest.approx(2 * r_ab / (1 + r_ab), rel=1e-12)
    assert sb["A"] == pytest.approx(math.sqrt(2 * r_ab / (1 + r_ab)), rel=1e-12)
    w = rng.uniform(0.4, 0.6, n)
    wide = rd.interior_attenuation(w + 0.08, w - 0.08, w, np.zeros((n, 5)), np.arange(float(n)))
    assert wide["A"] is None and wide["reliability"] < 0


def test_d4_zero_reliability_by_hand() -> None:
    """Indicator reliability from the split-half covariance, Spearman-Brown, Pearson form.

    Reference: counts by hand on 10 states. Zero in half A: states 0, 1, 2; in half B: 0, 1, 3; in
    the 200-draw weight: 0, 1. Cov = P(both) - P(A) P(B) = 0.2 - 0.09 = 0.11; Var(200) = 0.2 x 0.8 =
    0.16; r_100 = 0.6875; Spearman-Brown 2 r/(1 + r) = 1.375/1.6875 = 0.814815; the Pearson form
    r = 0.11/0.21 = 0.5238, reliability 1.0476/1.5238 = 0.6875. A constant 200-draw indicator is not
    computable. Tolerance 1e-12.
    """
    def weights(zeros: list[int]) -> np.ndarray:
        w = np.full(10, 0.5)
        w[zeros] = 0.0
        return w

    out = rd.zero_reliability(weights([0, 1, 2]), weights([0, 1, 3]), weights([0, 1]))
    assert out["r100"] == pytest.approx(0.6875, rel=1e-12)
    assert out["reliability"] == pytest.approx(1.375 / 1.6875, rel=1e-12)
    assert out["A"] == pytest.approx(math.sqrt(1.375 / 1.6875), rel=1e-12)
    assert out["pearson_r"] == pytest.approx(0.11 / 0.21, rel=1e-12)
    assert out["pearson_reliability"] == pytest.approx(2 * (0.11 / 0.21) / (1 + 0.11 / 0.21),
                                                       rel=1e-12)
    with pytest.raises(rd.NotComputable, match="constant"):
        rd.zero_reliability(weights([0]), weights([1]), weights([]))


# ------------------------------------------------------------------------------------------ D5, D6
def d5_script_model(seed: int, n: int, frac_sep: float, c: float):
    """The generator of ``m5_d5split.py`` re-implemented here (states and the three estimates)."""
    rng = make_rng(seed, "m5_d5split", frac_sep, c)
    base = rng.uniform(0.05, 0.6, n)
    base[rng.random(n) < 0.3] = 0.0
    spread = rng.exponential(0.15, (n, 3)) * rng.choice([-1, 1], (n, 3))
    spread[rng.random(n) < frac_sep] = 0.0
    w = np.clip(base[:, None] + spread, 0, 1)
    s = 0.017 * np.exp(0.5 * rng.standard_normal(n))
    chol = np.linalg.cholesky(np.full((3, 3), c) + (1 - c) * np.eye(3))
    e_a = rng.standard_normal((n, 3)) @ chol.T * s[:, None] * np.sqrt(2)
    e_b = rng.standard_normal((n, 3)) @ chol.T * s[:, None] * np.sqrt(2)
    f = lambda e: np.clip(w + e, 0, 1)  # noqa: E731
    return f(e_a), f(e_b), f((e_a + e_b) / 2)


def test_c6_d5_shift_and_richardson_match_the_script_model() -> None:
    """Delta_sh and B on the model of ``m5_d5split.py`` (seed 20261017) equal the script's formula.

    Reference: the script's expression ``(med rg(a) + med rg(b))/2 - med rg(m)`` on arrays drawn by
    the re-implemented generator (master seed 20261017 through ``make_rng``, so the arrays are this
    model's, not the script's own draws); ``rg`` is max minus min over the three horizons. Delta_sh matches to
    1e-12 relative (medians of identical floats: exact). B = Delta_sh/(sqrt 2 - 1) matches to 1e-12.
    The script prints the constant as the rounded 2.414, which differs from 1/(sqrt 2 - 1) = 2.41421356
    by 8.8e-5 relative; that rounding is what the second assertion bounds (1e-4), so the script's
    own B and the tool's agree to the rounding of its constant, not to 1e-12 (open question in the Log).
    """
    rg = lambda x: x.max(1) - x.min(1)  # noqa: E731
    for c, sep in ((0.0, 0.6), (0.5, 0.2), (0.9, 0.6)):
        a, b, m = d5_script_model(20261017, 650, sep, c)
        ref = 0.5 * (np.median(rg(a)) + np.median(rg(b))) - np.median(rg(m))
        shift = rd.split_half_shift(float(np.median(rg(a))), float(np.median(rg(b))),
                                    float(np.median(rg(m))))
        assert shift == pytest.approx(ref, rel=1e-12, abs=1e-15)
        assert rd.RICHARDSON * shift == pytest.approx(ref / (math.sqrt(2) - 1), rel=1e-12, abs=1e-15)
        assert rd.RICHARDSON * shift == pytest.approx(2.414 * ref, rel=1e-4, abs=1e-15)


def test_c6_v4_order_is_recovered_exactly_on_the_power_law() -> None:
    """p-hat = p on m(M) = c (M^-p - 800^-p) at M = 50 and 200; outside [0.3, 1.5] or a
    non-positive shift is "order not determined" (None), never a number.

    Reference: the algebra (M1^-p - M2^-p)/(M2^-p - M3^-p) = 4^p for M = 50, 200, 800. Tolerance
    1e-12 relative (a log of a ratio of differences of numbers of order 1).
    """
    for p in (0.31, 0.5, 0.8, 1.2, 1.49):
        m = lambda M: 0.7 * (M ** -p - 800.0 ** -p)  # noqa: E731
        got, note = rd.v4_order(m(50), m(200))
        assert got == pytest.approx(p, rel=1e-12) and note == "order determined"
    for p in (0.2, 1.6):
        m = lambda M: 0.7 * (M ** -p - 800.0 ** -p)  # noqa: E731
        assert rd.v4_order(m(50), m(200))[0] is None
    assert rd.v4_order(0.1, 0.0)[0] is None and rd.v4_order(0.1, 0.2)[0] is None


def test_c6_three_way_reading_is_exact_on_dyadic_inputs() -> None:
    """The three-way reading and its boundaries, on dyadic numbers so every sum is exact.

    Reference: the definition. limit = 0.5. (bias 0, se 0.125): 0.25 < 0.5, below. (0.25, 0.125):
    |b| + 2se = 0.5 is not < 0.5, and |b| - 2se = 0 < 0.5: not determined. (0.75, 0.125): |b| - 2se =
    0.5 >= 0.5: not below (the boundary belongs to "not below"). (-0.75, 0.125) the same (sign).
    (0.5, 0.5): not determined.
    """
    assert rd.three_way_reading(0.0, 0.125, 0.5) == "below 10%"
    assert rd.three_way_reading(0.25, 0.125, 0.5) == "not determined"
    assert rd.three_way_reading(0.75, 0.125, 0.5) == "not below 10%"
    assert rd.three_way_reading(-0.75, 0.125, 0.5) == "not below 10%"
    assert rd.three_way_reading(0.5, 0.5, 0.5) == "not determined"


def test_full_halfwidth_projection_and_observed() -> None:
    """hw_full: observed on a full run; else x sqrt(n_run/n_full) x 1.014 when B goes 500 to 2000.

    Reference: M3 (0.717 = sqrt(0.5) x 1.014 for the test states; sqrt(0.3) x 1.014 = 0.555 for the
    sweep). Another B gives the n factor only, and the note says so. Tolerance 1e-12.
    """
    cfg = {"name": "pilot", "n_test": 500, "n_test_sweep": 300, "bootstrap_resamples": 500}
    hw, how = rd.full_halfwidth(0.1, cfg, "n_test")
    assert hw == pytest.approx(0.1 * math.sqrt(0.5) * 1.014, rel=1e-12) and "x1.014" in how
    assert rd.full_halfwidth(0.1, cfg, "n_test_sweep")[0] == pytest.approx(
        0.1 * math.sqrt(0.3) * 1.014, rel=1e-12)
    hw, how = rd.full_halfwidth(0.1, {**cfg, "bootstrap_resamples": 300}, "n_test")
    assert hw == pytest.approx(0.1 * math.sqrt(0.5), rel=1e-12) and "B factor 1" in how
    assert rd.full_halfwidth(0.1, {**cfg, "name": "full"}, "n_test") == (0.1, "observed (full preset)")


def test_c7_near_clip_share_and_the_split_half_mean_bias_on_a_constructed_set() -> None:
    """f_b and the Richardson bias of a mean change decided by hand.

    Reference: five states with u = (0.05, 0.5, 0.97, 0.3, -0.2) and s = (0.02, 0.1, 0.02, 0.1, 0.05):
    within 2 s of a bound means u - 2 s <= 0 or u + 2 s >= 1: state 0: 0.05 - 0.04 = 0.01 > 0,
    0.09 < 1: no; state 1: 0.3, 0.7: no; state 2: 0.97 + 0.04 = 1.01 >= 1: yes; state 3: 0.1, 0.5: no;
    state 4: -0.2 - 0.1 <= 0: yes. So f_b = 2/5 = 0.4. The bias: mean paired changes of the halves
    0.30 and 0.20 and of the 200 draws 0.20 give Delta_sh = 0.25 - 0.20 = 0.05 and B =
    0.05/(sqrt 2 - 1) = 0.1207107 (dyadic apart from the constant). Tolerance 1e-12.
    """
    u = np.array([0.05, 0.5, 0.97, 0.3, -0.2])
    s = np.array([0.02, 0.1, 0.02, 0.1, 0.05])
    near = rd.near_clip(u, s)
    assert near.tolist() == [False, False, True, False, True] and near.mean() == 0.4
    shift = rd.split_half_shift(0.30, 0.20, 0.20)
    assert shift == pytest.approx(0.05, abs=1e-15)
    assert rd.RICHARDSON * shift == pytest.approx(0.05 / (math.sqrt(2) - 1), rel=1e-12)


# ------------------------------------------------------------------------------------------ the world
LT, N, NS, NV = 30, 80, 50, 12
HORIZONS = np.array([7, 15, 30, 60, 120])
REF = 2
RHOS = [0.005, 0.01, 0.02, 0.05]
LIB = [1000, 3162, 10000, 31623, 100000]
CFG = {"name": "pilot", "steps_per_lyapunov": LT, "core_noise": 0.01, "core_library": 10000,
       "noise_levels": RHOS, "library_sweep_noises": [0.01, 0.02], "linear_regime_rms": 0.5,
       "n_test": N, "n_test_sweep": NS, "bootstrap_resamples": 500, "bootstrap_block": 5,
       "seed_id": "DEV-1"}


def make_moments(rng: np.random.Generator, n: int, n_h: int):
    """Realizable-looking second moments (|C| < sqrt(E_C E_P), so the curvature is positive)."""
    scale = 0.02 * np.exp(rng.normal(0, 1, (n, 1)))
    grow = np.array([1.0, 3.0, 8.0, 30.0, 300.0])[:n_h]
    e_c = scale * grow * np.exp(rng.normal(0, 1.0, (n, n_h)))
    e_p = scale * grow * np.exp(rng.normal(0, 1.0, (n, n_h)))
    c = rng.uniform(-0.5, 0.9, (n, n_h)) * np.sqrt(e_c * e_p)
    return e_c, e_p, c


def make_halves(rng: np.random.Generator, full: np.ndarray):
    """Two halves that average to ``full`` (within 2%), so (A + B)/2 = full."""
    u = rng.uniform(-0.02, 0.02, full.shape)
    return full * (1.0 + u), full * (1.0 - u)


def oracle_w(e_c, e_p, c):
    """The oracle weight written in the test: (E_P - C)/(E_C + E_P - 2 C), clipped to [0, 1]."""
    return np.clip((e_p - c) / (e_c + e_p - 2.0 * c), 0.0, 1.0)


def make_group(rng: np.random.Generator, n: int) -> dict[str, np.ndarray]:
    """One sweep group: H_ref moments, their halves, the weight and the error correlation."""
    e_c, e_p, c = (a[:, 0] for a in make_moments(rng, n, 1))
    out = {"E_C": e_c, "E_P": e_p, "C": c, "w_star_href": oracle_w(e_c, e_p, c),
           "err_corr_href": rng.uniform(-1, 1, n), "abs_C": np.abs(c),
           "half_n_draws": np.array([100, 100])}
    for name, v in (("E_C", e_c), ("E_P", e_p), ("C", c)):
        out[f"{name}_A"], out[f"{name}_B"] = make_halves(rng, v)
    return out


def build_world(rng: np.random.Generator) -> tuple[dict, dict, dict]:
    """A dump (as a dict), the results tree that matches it, and the hand-computed extras.

    Every statistic placed in the results tree is computed here by a route independent of the tool:
    loops for the ranges, scipy's spearmanr per row, ``np.corrcoef`` of ``lstsq`` residuals for the
    partial correlations, ``np.polyfit`` for the slope.
    """
    d: dict[str, np.ndarray] = {}
    d["meta/schema"] = np.array("lpcstudy.states/1")
    d["meta/system"], d["meta/seed_id"], d["meta/preset"] = (np.array("lorenz63"),
                                                              np.array("DEV-1"), np.array("pilot"))
    for k, v in (("n_oracle_draws", 200), ("n_eval_draws", 2), ("steps_per_lyapunov", LT),
                 ("reference_horizon", 30)):
        d[f"meta/{k}"] = np.array(v)
    d["core/horizons"], d["core/ref_index"] = HORIZONS, np.array(REF)
    e_c, e_p, c = make_moments(rng, N, 5)
    for name, v in (("E_C", e_c), ("E_P", e_p), ("C", c)):
        d[f"core/{name}"] = v
        d[f"core/{name}_A"], d[f"core/{name}_B"] = make_halves(rng, v)
    d["core/w_star"] = oracle_w(e_c, e_p, c)
    d["core/w_star_A"] = oracle_w(d["core/E_C_A"], d["core/E_P_A"], d["core/C_A"])
    d["core/w_star_B"] = oracle_w(d["core/E_C_B"], d["core/E_P_B"], d["core/C_B"])
    d["core/Lambda_bar"] = rng.uniform(0.0, 0.05, N)
    d["core/eps_s"], d["core/delta"] = np.exp(rng.normal(-4, 0.3, N)), np.exp(rng.normal(-4, 0.3, N))
    d["core/g_H_ref"] = np.exp(rng.normal(1, 0.5, N))
    for rule in ("A0", "A1", "A2", "A3", "A4", "A5", "A4o", "A*"):
        d[f"core/state_mse/{rule}"] = np.exp(rng.normal(-3, 1.0, (N, 5)))
    for rule in ("A2", "A3", "A4", "A5"):
        d[f"core/weight_href/{rule}"] = rng.uniform(0, 1, (N, 2))
    groups = {(r, 10000) for r in RHOS} | {(r, n) for r in (0.01, 0.02) for n in LIB}
    for rho, n_lib in sorted(groups):
        for k, v in make_group(rng, NS).items():
            d[f"sweep/rho={rho:g}|n_lib={n_lib}/{k}"] = v
    d["v4/M"], d["v4/horizons"] = np.array([50, 200, 800]), np.array([30, 60, 120])
    w_ref = rng.uniform(0, 1, (NV, 3))
    w_hat = np.clip(w_ref[None] + rng.normal(0, 0.03, (3, NV, 3)) * np.array([2, 1, 0])[:, None, None],
                    0, 1)
    d["v4/w_hat"], d["v4/w_ref"], d["v4/signed_dev"] = w_hat, w_ref, w_hat - w_ref[None]
    d["v4/half_width"] = np.abs(rng.normal(0.02, 0.005, (3, NV, 3)))
    d["v4/extra_href_equal"], d["v4/extra_href_diff"] = np.array(True), np.array(0)
    for kind in ("oracle", "deployable"):
        for target in rd.QN_TARGETS:
            y = (rng.random(N) < 0.3).astype(float) if target == "w_zero_indicator" \
                else rng.normal(0, 1, N)
            dom = rng.random(N) < 0.85 if target == "logit_w_interior" else np.ones(N, bool)
            y = np.where(dom, y, 0.0)
            d[f"qn/{kind}/{target}/y"], d[f"qn/{kind}/{target}/domain"] = y, dom
            d[f"qn/{kind}/{target}/pred3"] = 0.4 * y + rng.normal(0, 0.5, N)
            d[f"qn/{kind}/{target}/pred4"] = 0.6 * y + rng.normal(0, 0.5, N)
    res = build_results(d)
    return d, res, {}


def r2(y, f):
    """R^2 written in the test: 1 - SS_res/SS_tot."""
    return 1.0 - np.sum((y - f) ** 2) / np.sum((y - y.mean()) ** 2)


def build_results(d: dict) -> dict:
    """The results leaves that the tool recomputes, by independent routes (see ``build_world``)."""
    sysd: dict = {}
    w, e_c, e_p = d["core/w_star"], d["core/E_C"], d["core/E_P"]
    cols = [2, 3, 4]
    ranges = []
    for i in range(N):
        seg = []
        for j in cols:
            if math.sqrt(e_c[i, j]) <= 0.5 and math.sqrt(e_p[i, j]) <= 0.5:
                seg.append(float(w[i, j]))
            else:
                break
        ranges.append(max(seg) - min(seg) if len(seg) >= 2 else None)
    elig = [r for r in ranges if r is not None]
    sysd["H2a"] = {"median_range": float(np.median(elig)), "range_ci": [0.05, 0.15],
                   "part_ii": {}}
    w_ref = w[:, REF]
    lam = d["core/Lambda_bar"] * LT
    x1, x2 = np.log(d["core/eps_s"] / 0.01), np.log(d["core/delta"] / 0.01)
    x1, x2 = x1 - x1.mean(), x2 - x2.mean()
    q = np.column_stack([x1, x2, x1**2, x2**2, x1 * x2])

    def partial(target, rows):
        design = np.column_stack([np.ones(rows.sum()), q[rows]])
        res = []
        for v in (target[rows], lam[rows]):
            res.append(v - design @ np.linalg.lstsq(design, v, rcond=None)[0])
        return float(np.corrcoef(res[0], res[1])[0, 1])

    zero, one = w_ref == 0.0, w_ref == 1.0
    interior = ~zero & ~one
    parts = {"zero": (zero.astype(float), np.ones(N, bool)),
             "interior": (np.log(np.where(interior, w_ref, 0.5) / (1 - np.where(interior, w_ref, 0.5))),
                          interior)}
    if 20 * one.sum() > N:
        parts["one"] = (one.astype(float), np.ones(N, bool))
    for name, (target, rows) in parts.items():
        sysd["H2a"]["part_ii"][name] = {"partial_corr": partial(target, rows)}
    levels = np.array(RHOS)
    rows_w = np.column_stack([d[f"sweep/rho={r:g}|n_lib=10000/w_star_href"] for r in RHOS])
    spear = []
    for row in rows_w:
        spear.append(0.0 if np.ptp(row) == 0 else sps.spearmanr(levels, row).statistic)
    sysd["H2b"] = {"noise": {"mean_state_spearman": float(np.mean(spear))},
                   "library_change": {
                       "mean_change": float(np.mean(d["sweep/rho=0.01|n_lib=10000/w_star_href"]
                                                    - d["sweep/rho=0.01|n_lib=1000/w_star_href"])),
                       "ci": [0.01, 0.05]}}
    mse = {r: d[f"core/state_mse/{r}"][:, REF] for r in ("A0", "A1", "A2", "A3", "A4", "A5")}
    sysd["H3c"] = {"A5_over_A4_mse": float(mse["A5"].mean() / mse["A4"].mean())}
    sysd["H2c"] = {"best_single": "A1",
                   "A4_minus_A2": {"mean": float(np.mean(mse["A4"] - mse["A2"]))},
                   "A4_minus_A1": {"mean": float(np.mean(mse["A4"] - mse["A1"]))}}
    sysd["H2d"] = {"in_distribution_excess": float(mse["A4"].mean() / mse["A3"].mean() - 1.0)}
    sysd["H2e"] = {"by_noise": {}}
    for rho in (0.01, 0.02):
        diff = (d[f"sweep/rho={rho:g}|n_lib=100000/err_corr_href"]
                - d[f"sweep/rho={rho:g}|n_lib=1000/err_corr_href"])
        sysd["H2e"]["by_noise"][f"{rho:g}"] = {"median_change": float(np.median(diff))}
    sysd["Q-N"] = {}
    for kind in ("oracle", "deployable"):
        sysd["Q-N"][kind] = {}
        for target in rd.QN_TARGETS:
            y, dom = d[f"qn/{kind}/{target}/y"], d[f"qn/{kind}/{target}/domain"]
            f3, f4 = d[f"qn/{kind}/{target}/pred3"], d[f"qn/{kind}/{target}/pred4"]
            sysd["Q-N"][kind][target] = {"delta_r2": float(r2(y[dom], f4[dom]) - r2(y[dom], f3[dom]))}
    x = np.log(d["core/g_H_ref"] * d["core/delta"])
    y = 0.5 * np.log(np.maximum(e_p[:, REF], 1e-12))
    sysd["H1b"] = {"PLP": {"slope": float(np.polyfit(x, y, 1)[0])}}
    return {"config": dict(CFG), "provenance": {"seed_id": "DEV-1", "commit": "synthetic"},
            "systems": {"lorenz63": sysd}}


def write_run(tmp_path: Path, d: dict, res: dict) -> Path:
    """Write ``results.json`` and ``states/lorenz63.npz`` and return the run directory."""
    (tmp_path / "results.json").write_text(json.dumps(res))
    (tmp_path / "states").mkdir(exist_ok=True)
    np.savez(tmp_path / "states" / "lorenz63.npz", **d)
    return tmp_path


def test_a_full_run_on_a_consistent_world_reproduces_every_leaf_and_exits_0(tmp_path, capsys) -> None:
    """End to end: the report is labelled DEVELOPMENT, every recomputed leaf is MATCH, exit 0.

    Reference: the results tree of ``build_world``, computed in this file by independent routes. The
    run must print D1 to D6 for the system, list H1a, H1c and H1d as outside the schema, and compute the
    18 + 7 series of the criteria (the primaries: H2a(i), H2a(ii) zero and interior (and one if
    triggered), H2b(i), H2b(ii), H3c). Exit 0.
    """
    d, res, _ = build_world(rng_for("world"))
    run_dir = write_run(tmp_path, d, res)
    json_path = tmp_path / "out.json"
    code = rd.main([str(run_dir), "--resamples", "100", "--permutations", "50", "--json",
                    str(json_path)])
    out = capsys.readouterr().out
    assert out.splitlines()[0].startswith("DEVELOPMENT (DEV-1): conditional on one realization")
    assert "needs owner review before freeze" in out
    for header in ("D1 influence series", "D2 block-length", "D3 log-SD", "D4 split-half",
                   "D5 finite-M bias", "D6 H2b(ii)", "outside schema lpcstudy.states/1"):
        assert header in out
    assert "MISMATCH" not in out and "not computable" not in out, out
    assert out.count(": MATCH") >= 16
    assert code == 0
    data = json.loads(json_path.read_text())
    names = set(data["lorenz63"]["D1"])
    assert {"H2a(i)", "H2a(ii) zero", "H2a(ii) interior", "H2b(i)", "H2b(ii)", "H3c"} <= names
    assert data["lorenz63"]["D1"]["H3c"]["primary"] is True
    assert data["lorenz63"]["D5"]["reading"] in ("below 10%", "not below 10%", "not determined")


def test_a_perturbed_results_leaf_is_a_mismatch_with_exit_1(tmp_path, capsys) -> None:
    """A results leaf that differs from the dump's recomputation by 1e-6 relative is a MISMATCH.

    Reference: the unperturbed run is MATCH (previous test); the H3c ratio is changed by 1e-6 of
    itself, 10^6 times the 1e-12 tolerance. Exit 1 takes precedence over a "not computable".
    """
    d, res, _ = build_world(rng_for("world"))
    res["systems"]["lorenz63"]["H3c"]["A5_over_A4_mse"] *= 1.000001
    del d["core/Lambda_bar"]  # also makes H2a(ii) not computable: 1 must still win over 2
    code = rd.main([str(write_run(tmp_path, d, res)), "--resamples", "100", "--permutations", "50"])
    out = capsys.readouterr().out
    assert "MISMATCH: lorenz63 H3c A5/A4 ratio" in out and code == 1


def test_a_missing_array_prints_not_computable_and_every_other_diagnostic_still_runs(
        tmp_path, capsys) -> None:
    """Removing ``core/E_C_A`` (read by D4) and ``core/w_star_B`` (read by D5 and the H2a(i) series)
    makes those diagnostics not computable, each listed with the array's name; the diagnostics that
    do not need them still print; exit 2.

    Reference: the schema dependencies in the tool's docstring. Nothing is skipped silently.
    """
    d, res, _ = build_world(rng_for("world"))
    del d["core/E_C_A"]
    del d["core/w_star_B"]
    code = rd.main([str(write_run(tmp_path, d, res)), "--resamples", "100", "--permutations", "50"])
    out = capsys.readouterr().out
    assert "not computable: lorenz63 D4 inputs: array 'core/E_C_A' is not in" in out
    assert "not computable: lorenz63 D5 inputs: array 'core/w_star_B' is not in" in out
    assert "D3 log-SD" in out and "H3c" in out and "MISMATCH" not in out
    assert code == 2


def test_a_system_without_a_dump_file_is_listed_and_a_non_dev_seed_is_refused(tmp_path, capsys) -> None:
    """No ``states/<system>.npz``: "not computable" for the system (exit 2). A seed id that is not
    ``DEV-n`` is refused before anything is read from the dump (exit 2, message on stderr).

    Reference: the contract of the module docstring.
    """
    d, res, _ = build_world(rng_for("world"))
    (tmp_path / "results.json").write_text(json.dumps(res))
    assert rd.main([str(tmp_path)]) == 2
    assert "lorenz63 (D1 to D6): " in capsys.readouterr().out
    for bad in ("CONF-1", "dev-1", "DEV-", None):
        tree = {**res, "provenance": {"seed_id": bad}, "config": {**res["config"], "seed_id": bad}}
        run_dir = write_run(tmp_path, d, tree)
        assert rd.main([str(run_dir)]) == 2
        captured = capsys.readouterr()
        assert captured.out == "" and ("refused" in captured.err or "no config" in captured.err)


def test_a_wrong_schema_is_not_computable(tmp_path, capsys) -> None:
    """A dump with another schema version is refused for that system (never read as 1)."""
    d, res, _ = build_world(rng_for("world"))
    d["meta/schema"] = np.array("lpcstudy.states/2")
    assert rd.main([str(write_run(tmp_path, d, res))]) == 2
    assert "schema 'lpcstudy.states/2' is not 'lpcstudy.states/1'" in capsys.readouterr().out


def test_check_matches_within_the_relative_tolerance_and_needs_equality_at_zero() -> None:
    """``check``: |dump - leaf| <= tol |leaf|; an exact 0 leaf needs equality; a missing leaf is
    "not computable".

    Reference: the definition. 1.0 against 1.0 + 5e-13 passes at 1e-12 and fails at 1e-13; 0 against
    1e-300 fails at any tol (no floor).
    """
    rep = rd.Report()
    ctx = rd.Context("s", rd.Dump({}, "mem"), {"a": {"b": 1.0}, "z": {"c": 0.0}}, {}, rep, 1, 2, 2)
    rd.check(ctx, "ok", 1.0 + 5e-13, ("a", "b"), 1e-12)
    rd.check(ctx, "tight", 1.0 + 5e-13, ("a", "b"), 1e-13)
    rd.check(ctx, "zero", 1e-300, ("z", "c"), 1e-6)
    rd.check(ctx, "absent", 1.0, ("a", "q"), 1e-6)
    assert len(rep.defects) == 2 and "tight" in rep.defects[0] and "zero" in rep.defects[1]
    assert len(rep.incomplete) == 1 and "results leaf a/q is absent" in rep.incomplete[0]
    assert rep.exit_code() == 1


def test_the_tool_draws_randomness_only_through_make_rng() -> None:
    """No ``default_rng``, ``random.`` or ``PRNGKey`` in the tool (a source scan); its generators come
    from ``make_rng(seed, system, label)``, and equal seeds give equal reports.

    Reference: the plan's rule (randomness only via ``lpcstudy.data.make_rng``); the scan is of the
    tool's source text. Determinism: two ``bootstrap_se`` calls from equal ``make_rng`` generators agree.
    """
    source = (ROOT / "tools" / "rehearsal_diagnostics.py").read_text()
    for forbidden in ("default_rng(", "random.seed", "np.random.rand", "PRNGKey", "import random"):
        assert forbidden not in source
    stat = lambda idx: float(np.mean(idx))  # noqa: E731
    first = rd.bootstrap_se(stat, 60, 20, 5, make_rng(1, "a"))
    assert first == rd.bootstrap_se(stat, 60, 20, 5, make_rng(1, "a"))
    assert first != rd.bootstrap_se(stat, 60, 20, 5, make_rng(2, "a"))
    with pytest.raises(rd.NotComputable):
        rd.bootstrap_se(lambda idx: float("nan"), 60, 20, 5, make_rng(1, "a"))


def test_d5_v4_levels_by_hand(tmp_path) -> None:
    """The V4 check on a constructed dump: ranges, shifts, order, 2 m(200), signed deviations.

    Reference, by hand: two eligible V4 states (all three horizons small), w_hat at M = 50, 200, 800
    for horizons (1, 2, 4 LT):
    M = 800: (0.2, 0.3, 0.5) and (0.4, 0.4, 0.4): ranges 0.3 and 0; median 0.15.
    M = 200: ranges 0.5 and 0.1 (rows (0.1, 0.4, 0.6), (0.4, 0.5, 0.4)): median 0.3.
    M = 50: ranges 0.9 and 0.5 (rows (0.0, 0.5, 0.9), (0.3, 0.8, 0.3)): median 0.7.
    So m(200) = 0.15, m(50) = 0.55; p = log_4((0.55 - 0.15)/0.15) = log_4(2.6667) = 0.7075, and
    2 m(200) = 0.30. The third state is not eligible (large E_C at 1 LT) and must not count.
    Tolerance 1e-12 relative (the log).
    """
    n_v4 = 3
    d: dict[str, np.ndarray] = {
        "core/horizons": HORIZONS, "core/E_C": np.full((n_v4, 5), 0.01),
        "core/E_P": np.full((n_v4, 5), 0.01), "v4/M": np.array([50, 200, 800]),
        "v4/horizons": np.array([30, 60, 120]), "v4/extra_href_equal": np.array(False),
        "v4/extra_href_diff": np.array(7)}
    d["core/E_C"][2, 2:] = 9.0  # state 2 is not small at 1 LT: no leading segment
    w_hat = np.zeros((3, n_v4, 3))
    w_hat[2] = [[0.2, 0.3, 0.5], [0.4, 0.4, 0.4], [0.5, 0.5, 0.5]]
    w_hat[1] = [[0.1, 0.4, 0.6], [0.4, 0.5, 0.4], [0.0, 1.0, 0.0]]
    w_hat[0] = [[0.0, 0.5, 0.9], [0.3, 0.8, 0.3], [0.0, 1.0, 0.0]]
    d["v4/w_hat"] = w_hat
    d["v4/signed_dev"] = w_hat - w_hat[2][None]
    d["v4/half_width"] = np.full((3, n_v4, 3), 0.02)
    rep = rd.Report()
    ctx = rd.Context("s", rd.Dump(d, "mem"), {}, {"linear_regime_rms": 0.5}, rep, 1, 10, 10)
    out = rd._d5_v4(ctx)
    assert out["n_eligible"] == 2
    assert out["shift_a"] == pytest.approx(0.55, rel=1e-12) and out["shift_b"] == pytest.approx(0.15, rel=1e-12)
    assert out["order"] == pytest.approx(math.log((0.55 - 0.15) / 0.15, 4), rel=1e-12)
    assert out["bias_v4"] == pytest.approx(0.30, rel=1e-12)
    text = "\n".join(rep.lines)
    assert "WARNING extra_href_equal FALSE (7 differing" in text
    assert out["signed_mean_dev_href"][800] == 0.0


def test_d6_on_a_constructed_pair_of_library_cells(tmp_path) -> None:
    """D6 end to end on two cells whose moments are decided by hand.

    Reference: with E_C = 2, E_P = 1, C = 0.5 (so c = 2, u = 0.25) for every state in the 10^3
    cell, and E_P = 2 (u = 0.75) in the 10^4 cell; the halves differ from the full moments by +-0.1 in
    C: C_A = 0.5 + 0.1, C_B = 0.5 - 0.1 for the 10^3 cell and the same for 10^4. Hand values:
    10^3: full u = 0.25; half A: (1 - 0.6)/(2 + 1 - 1.2) = 0.4/1.8; half B: (1 - 0.4)/(3 - 0.8) = 0.6/2.2.
    10^4 (E_C = 2, E_P = 2, C = 0.5, c = 3): u = 1.5/3 = 0.5; half A: (2 - 0.6)/(4 - 1.2) = 0.5; half B:
    (2 - 0.4)/(4 - 0.8) = 0.5. So change(200) = 0.25, change A = 0.5 - 0.4/1.8, change B = 0.5 - 0.6/2.2;
    Delta_sh = (A + B)/2 - 0.25 and B_hat = Delta_sh/(sqrt 2 - 1), the same for each state (SE 0).
    f_b: s = |u_A - u_B|/2 is 0.0 for the 10^4 cell (0.5 both) and |0.2222 - 0.2727|/2 = 0.02525 for
    the 10^3 cell, and no u is within 2 s of 0 or 1, so f_b = 0 in both. Tolerance 1e-12 relative.
    """
    n = 12
    d: dict[str, np.ndarray] = {}
    for n_lib, e_p in ((1000, 1.0), (10000, 2.0)):
        g = f"sweep/rho=0.01|n_lib={n_lib}"
        e_c, c = np.full(n, 2.0), np.full(n, 0.5)
        d[f"{g}/E_C"], d[f"{g}/E_P"], d[f"{g}/C"] = e_c, np.full(n, e_p), c
        for tag, dc in (("A", 0.1), ("B", -0.1)):
            d[f"{g}/E_C_{tag}"], d[f"{g}/E_P_{tag}"], d[f"{g}/C_{tag}"] = e_c, np.full(n, e_p), c + dc
        d[f"{g}/w_star_href"] = np.clip((e_p - c) / (2.0 + e_p - 2.0 * c), 0.0, 1.0)
    rep = rd.Report()
    cfg = {"core_noise": 0.01, "bootstrap_block": 5, "name": "pilot", "n_test_sweep": 300,
           "bootstrap_resamples": 500}
    res = {"H2b": {"library_change": {"mean_change": 0.25, "ci": [0.0, 0.1]}}}
    ctx = rd.Context("s", rd.Dump(d, "mem"), res, cfg, rep, 3, 20, 10)
    rd.section_d6(ctx)
    out = rep.data["s"]["D6"]
    a, b = 0.5 - 0.4 / 1.8, 0.5 - 0.6 / 2.2
    shift = 0.5 * (a + b) - 0.25
    assert out["delta_sh"] == pytest.approx(shift, rel=1e-12)
    assert out["bias_order_half"] == pytest.approx(shift / (math.sqrt(2) - 1), rel=1e-12)
    assert out["se"] == pytest.approx(0.0, abs=1e-15)
    assert out["f_b"][1000]["f_b"] == 0.0 and out["f_b"][10000]["f_b"] == 0.0
    assert out["reading"] in ("below 10%", "not below 10%", "not determined")
    assert not rep.defects, rep.defects


def test_dump_loads_an_npz_without_pickles_and_names_the_missing_array(tmp_path) -> None:
    """``Dump.load`` reads an ``.npz`` (string and numeric arrays) with ``allow_pickle=False``.

    Reference: the arrays that were saved. A missing key raises ``Missing`` naming the key and the file.
    """
    path = tmp_path / "x.npz"
    np.savez(path, **{"meta/schema": np.array("lpcstudy.states/1"), "core/x": np.arange(3.0)})
    dump = rd.Dump.load(path)
    assert dump.scalar("meta/schema") == "lpcstudy.states/1" and dump["core/x"].tolist() == [0.0, 1.0, 2.0]
    assert dump.has("core/x") and not dump.has("core/y")
    with pytest.raises(rd.Missing, match="array 'core/y' is not in"):
        dump["core/y"]
