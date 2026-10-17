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
def test_acf_readings_and_the_e2_coverage_rule_by_hand() -> None:
    """The C9 reading (thresholds 0.15 for n <= 500 and 0.11, the case values) and the E2 coverage.

    Reference: amendment 5 E2 and B1 7.D1 applied by hand. H3c (case 0.16, table 0.9402/0.9772 at
    phi = 0 and 0.9265/0.9715 at phi = 0.3): acf1 0.10 and 0.13 are within the 0.15 threshold (phi = 0
    rows apply), 0.16 is realistic. The coverage is ``cov0 + (cov0.3 - cov0) l/l_c`` from l = 0: at
    l = 0.08 (half the case value) 0.9402 - 0.5 x 0.0137 = 0.93335 and 0.9772 - 0.5 x 0.0057 =
    0.97435; at l = 0 or below it is cov0 (clamped); at l = 0.16 it is cov0.3; above (0.20) it is
    "<= cov0.3 (beyond the tabulated stress)" with no extrapolation. H2a(ii) (case 0.09) at 0.10:
    both readings hold, phi = 0.3 governs, and 0.10 is beyond the case value. H1d is tabulated (case
    0.09, C6). Q-N and H1b: "coverage not tabulated", phi = 0 reading only. acf1 = -0.2 gets neither
    reading. The false-trigger rate is ``2 norm.sf(thr sqrt(n))`` (scipy's tail, independent of the
    tool's ``erfc``). Tolerance 1e-12.
    """
    assert rd.acf_reading("H3c", 0.10, 500)[0].startswith("phi = 0 rows apply")
    assert rd.acf_reading("H3c", 0.16, 500)[0].startswith("phi = 0.3 rows realistic")
    assert rd.acf_reading("H3c", 0.13, 500)[0].startswith("phi = 0 rows apply")
    text, cov = rd.acf_reading("H3c", 0.08, 500)
    assert cov["cov95"] == pytest.approx(0.9402 + (0.9265 - 0.9402) * 0.5, abs=1e-12)
    assert cov["cov983"] == pytest.approx(0.9772 + (0.9715 - 0.9772) * 0.5, abs=1e-12)
    assert "coverage 0.9334 (95%) / 0.9744 (98.3%)" in text and "interpolated from l = 0" in text
    assert rd.coverage_at("H3c", 0.0)["cov95"] == 0.9402
    assert rd.coverage_at("H3c", -0.3)["cov983"] == 0.9772 and not rd.coverage_at("H3c", -0.3)["beyond"]
    at_case = rd.coverage_at("H3c", 0.16)
    assert at_case["cov95"] == pytest.approx(0.9265, abs=1e-12) and not at_case["beyond"]
    text, cov = rd.acf_reading("H3c", 0.20, 500)
    assert cov["beyond"] and "coverage <= 0.9265 (95%) / 0.9715 (98.3%) (beyond the tabulated stress)" in text
    text, cov = rd.acf_reading("H2a(ii)", 0.10, 500)
    assert text.startswith("phi = 0.3 rows realistic") and "both readings hold" in text
    assert cov["beyond"] and cov["bound95"] == 0.9389
    assert rd.coverage_at("H1d", 0.045)["cov95"] == pytest.approx(0.9470 + (0.9439 - 0.9470) * 0.5)
    for name in ("Q-N", "H1b", "H1c"):
        text, cov = rd.acf_reading(name, 0.05, 500)
        assert cov is None and "coverage not tabulated" in text
    assert "no case value" in rd.acf_reading("Q-N", 0.05, 500)[0]
    assert rd.acf_reading("H2b(i)", -0.2, 500)[0].startswith("acf1 below")
    assert set(rd.COVERAGE) == {"H2a(i)", "H2a(ii)", "H2b(i)", "H2b(ii)", "H3c", "H2c", "H2d",
                                "H2e", "H1d"}
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
    """The E6 near-bound rule and the Richardson bias of a mean change decided by hand.

    Reference: five states with u = (0.05, 0.5, 0.97, 0.3, -0.2) and s = (0.02, 0.1, 0.02, 0.1, 0.05).
    Near a bound means min(|u|, |1 - u|) <= 2 s: state 0: min(0.05, 0.95) = 0.05 <= 0.04? no;
    state 1: 0.5 <= 0.2? no; state 2: min(0.97, 0.03) = 0.03 <= 0.04: yes; state 3: 0.3 <= 0.2? no;
    state 4: min(0.2, 1.2) = 0.2 <= 0.1? no (u far outside [0, 1]: its clipped weight does not move).
    So f_b = 1/5. The bias: mean paired changes of the halves 0.30 and 0.20 and of the 200 draws 0.20
    give Delta_sh = 0.25 - 0.20 = 0.05 and B = 0.05/(sqrt 2 - 1). Tolerance 1e-12.
    """
    u = np.array([0.05, 0.5, 0.97, 0.3, -0.2])
    s = np.array([0.02, 0.1, 0.02, 0.1, 0.05])
    near = rd.near_clip(u, s)
    assert near.tolist() == [False, False, True, False, False] and near.mean() == 0.2
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
    d["core/N"] = np.exp(rng.normal(-2, 0.7, N))
    # the deployable profile of E = 2 draws: strictly increasing transforms of noisy proxies of the
    # oracle quantities (log(x/rho), log(x/rho), x steps_per_lyapunov, log(x + c))
    proxy = [d["core/eps_s"], d["core/delta"], d["core/Lambda_bar"], d["core/N"]]
    prof = np.empty((N, 2, 4))
    for draw in range(2):
        noisy = [v * np.exp(rng.normal(0, 0.4, N)) for v in proxy]
        prof[:, draw, 0] = np.log(noisy[0] / 0.01)
        prof[:, draw, 1] = np.log(noisy[1] / 0.01)
        prof[:, draw, 2] = noisy[2] * LT
        prof[:, draw, 3] = np.log(noisy[3] + 1e-3)
    d["core/profile"] = prof
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
    sysd["H2b"] = {"noise": {"mean_state_spearman": float(np.mean(spear)),
                             "n_constant_states": int(sum(np.ptp(r) == 0 for r in rows_w))},
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
    with np.errstate(divide="ignore"):
        x = np.log(d["core/g_H_ref"] * d["core/delta"])
    y = 0.5 * np.log(np.maximum(e_p[:, REF], 1e-12))
    keep = np.isfinite(x) & np.isfinite(y)
    sysd["H1b"] = {"PLP": {"slope": float(np.polyfit(x[keep], y[keep], 1)[0]),
                           "n_excluded_nonfinite": int((~keep).sum()),
                           "n_floored": int((e_p[:, REF][keep] < 1e-12).sum())}}
    sysd["H1d"] = {"rows": {}}
    for name, col, oracle in rd.H1D_ROWS:
        proxy, truth = d["core/profile"][:, 0, col], d[f"core/{oracle}"]
        keep = np.isfinite(proxy) & np.isfinite(truth)
        sysd["H1d"]["rows"][name] = {
            "spearman": float(sps.spearmanr(proxy[keep], truth[keep]).statistic),
            "n_excluded_nonfinite": int((~keep).sum())}
    return {"config": dict(CFG),
            "provenance": {"seed_id": "DEV-1", "seed_kind": "development", "commit": "synthetic"},
            "systems": {"lorenz63": sysd}}


def write_run(tmp_path: Path, d: dict, res: dict) -> Path:
    """Write ``results.json`` and ``states/lorenz63.npz`` and return the run directory."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / "results.json").write_text(json.dumps(res))
    (tmp_path / "states").mkdir(exist_ok=True)
    np.savez(tmp_path / "states" / "lorenz63.npz", **d)
    return tmp_path


def test_a_full_run_on_a_consistent_world_reproduces_every_leaf_and_lists_h1a_h1c(
        tmp_path, capsys) -> None:
    """End to end: labelled DEVELOPMENT, every recomputed leaf is MATCH, H1a and H1c are the only
    "not computable" lines (their arrays are not in the schema), so the exit code is 2.

    Reference: the results tree of ``build_world``, computed in this file by independent routes. The
    run must print D1 to D6 for the system and the run-level D1/D2 lines, compute the primaries
    (H2a(i), H2a(ii) zero and interior (and one if triggered), H2b(i), H2b(ii), H3c) and H1d, and
    record the seed and options in the JSON and prominently in the text (R9).
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
                   "D5 finite-M bias", "D6 H2b(ii)", "Run level (all systems)"):
        assert header in out
    assert "MISMATCH" not in out and "INTERNAL ERROR" not in out, out
    nc = [line.strip() for line in out.splitlines() if line.strip().startswith("not computable:")
          and "items" not in line and "item(s)" not in line]
    assert [line.split(":")[1].strip() for line in nc] == [
        "H1a (all systems)", "H1c (all systems)",
        "lorenz63 D5 pilot-equivalent V4"]  # E5: the world has 12 V4 states, not 40
    assert out.count(": MATCH") >= 28  # 20 earlier leaves, H1d: 4 rho + 4 exclusion counts
    assert code == 2
    data = json.loads(json_path.read_text())
    names = set(data["lorenz63"]["D1"])
    assert {"H2a(i)", "H2a(ii) zero", "H2a(ii) interior", "H2b(i)", "H2b(ii)", "H3c",
            "H1d analog_seed", "H1d estimation_seed", "H1d growth", "H1d nhat"} <= names
    assert data["lorenz63"]["D1"]["H3c"]["primary"] is True
    assert data["lorenz63"]["D1"]["H1d growth"]["primary"] is False
    assert data["lorenz63"]["D1"]["H3c"]["domain"] == N and data["lorenz63"]["D1"]["H2b(i)"]["domain"] == NS
    assert 2 <= data["lorenz63"]["D1"]["H2a(i)"]["domain"] < N  # the eligible states
    assert data["lorenz63"]["D5"]["reading"] in ("below 10%", "not below 10%", "not determined")
    assert data["options"] == {"seed": rd.TOOL_SEED, "resamples": 100, "permutations": 50,
                               "default": False}
    assert "NON-DEFAULT OPTIONS" in out and "owner question" in out and "not allowed" in out
    assert data["run_level"]["n_series"] == len(data["lorenz63"]["D1"])
    summary = out[out.index("Summary"):]
    assert "not computable by name: H1a, H1c." in summary
    assert "H1a, H1c. Without them the rehearsal cannot say whether the phi = 0 or the phi = 0.3 " \
        "coverage applies to the H1a interval" in summary
    assert "NON-DEFAULT OPTION: seed 20261018, resamples 100, permutations 50" in summary


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
    assert "check H3c A5/A4 ratio: dump" in out and "(|diff| " in out
    assert out.count(": MISMATCH") == 1 and "MISMATCH: 1 item(s)" in out and code == 1


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
        assert captured.out == "" and "refused" in captured.err


def test_constant_h2b_states_and_nonfinite_h1b_states_are_counted_against_the_results(
        tmp_path, capsys) -> None:
    """The tie-convention count of H2b(i) and the non-finite exclusion of H1b are recomputed and compared.

    Reference: by hand. Making state 0's weight the same at all four noise levels (so its rank
    denominator is 0) gives n_constant_states = 1 (the world has none otherwise); making state 1's
    PLP gain 0 gives log(0) = -inf, one excluded state. The results leaves written to match are
    MATCH; the same leaves left at 0 are a MISMATCH (exact integer comparison, tolerance 0).
    """
    d, res, _ = build_world(rng_for("world"))
    for r in RHOS:
        d[f"sweep/rho={r:g}|n_lib=10000/w_star_href"][0] = 0.25
    d["core/g_H_ref"][1] = 0.0
    sysd = build_results(d)["systems"]["lorenz63"]
    assert sysd["H2b"]["noise"]["n_constant_states"] == 1
    res["systems"]["lorenz63"]["H2b"]["noise"] = sysd["H2b"]["noise"]
    assert sysd["H1b"]["PLP"]["n_excluded_nonfinite"] == 1
    res["systems"]["lorenz63"]["H1b"]["PLP"] = sysd["H1b"]["PLP"]
    rd.main([str(write_run(tmp_path, d, res)), "--resamples", "50", "--permutations", "20"])
    out = capsys.readouterr().out
    assert "check H2b(i) constant states (scored 0 by the tie convention): dump 1 vs results 1" in out
    assert "check H1b PLP states excluded as non-finite: dump 1 vs results 1" in out
    res["systems"]["lorenz63"]["H2b"]["noise"]["n_constant_states"] = 0
    code = rd.main([str(write_run(tmp_path / "b", d, res)), "--resamples", "50",
                    "--permutations", "20"])
    assert "dump 1 vs results 0" in capsys.readouterr().out and code == 1


def test_a_dump_of_another_run_is_refused_or_a_mismatch(tmp_path, capsys) -> None:
    """A dump whose ``meta/seed_id`` differs from the run's is REFUSED (exit 2, stderr); a differing
    ``meta/preset`` is a MISMATCH (exit 1); a dump without ``meta/preset`` is "not computable".

    Reference: the contract of R8 (every recorded seed id agrees and is DEV-n) and of the dump's
    provenance check.
    """
    d, res, _ = build_world(rng_for("world"))
    d["meta/seed_id"] = np.array("DEV-2")
    code = rd.main([str(write_run(tmp_path, d, res)), "--resamples", "100", "--permutations", "50"])
    captured = capsys.readouterr()
    assert code == 2 and captured.out == ""
    assert "the dump of lorenz63 records seed id 'DEV-2' but the run records 'DEV-1'" in captured.err
    d, res, _ = build_world(rng_for("world"))
    del d["meta/seed_id"]
    assert rd.main([str(write_run(tmp_path / "n", d, res))]) == 2
    assert "records no seed id" in capsys.readouterr().err
    d, res, _ = build_world(rng_for("world"))
    d["meta/preset"] = np.array("full")
    code = rd.main([str(write_run(tmp_path / "p", d, res)), "--resamples", "100",
                    "--permutations", "50"])
    assert "MISMATCH: lorenz63: meta/preset is 'full' in the dump but 'pilot' in results.json" in \
        capsys.readouterr().out and code == 1
    d, res, _ = build_world(rng_for("world"))
    del d["meta/preset"]
    assert rd.main([str(write_run(tmp_path / "b", d, res)), "--resamples", "100",
                    "--permutations", "50"]) == 2
    assert "array 'meta/preset' is not in" in capsys.readouterr().out


def test_every_recorded_seed_id_must_be_present_agree_and_be_a_development_id(
        tmp_path, capsys) -> None:
    """R8: config.seed_id, provenance.seed_id and provenance.seed_kind are all required.

    Reference: the contract. A disagreeing pair (DEV-1 and DEV-2), a missing provenance id, a
    missing config id, ``seed_kind`` 'confirmatory' or absent are each refused (exit 2, nothing on
    stdout); the consistent tree is accepted.
    """
    d, res, _ = build_world(rng_for("world"))
    cases = {
        "disagree": {"config": {**res["config"], "seed_id": "DEV-2"}},
        "no provenance id": {"provenance": {"seed_kind": "development"}},
        "no config id": {"config": {k: v for k, v in res["config"].items() if k != "seed_id"}},
        "confirmatory kind": {"provenance": {**res["provenance"], "seed_kind": "confirmatory"}},
        "no kind": {"provenance": {"seed_id": "DEV-1", "commit": "x"}},
    }
    for name, change in cases.items():
        run_dir = write_run(tmp_path / name.replace(" ", "_"), d, {**res, **change})
        assert rd.main([str(run_dir)]) == 2, name
        captured = capsys.readouterr()
        assert captured.out == "" and "refused" in captured.err, name
    assert rd.run_seed_id(res) == "DEV-1"


def test_a_wrong_schema_is_not_computable(tmp_path, capsys) -> None:
    """A dump with another schema version is refused for that system (never read as 1)."""
    d, res, _ = build_world(rng_for("world"))
    d["meta/schema"] = np.array("lpcstudy.states/3")
    assert rd.main([str(write_run(tmp_path, d, res))]) == 2
    assert "schema 'lpcstudy.states/3' is not one of ('lpcstudy.states/1', 'lpcstudy.states/2')" \
        in capsys.readouterr().out
    d["meta/schema"] = np.array("lpcstudy.states/2")  # /2 keeps every /1 key: accepted
    assert rd.main([str(write_run(tmp_path / "b", d, res)), "--resamples", "50",
                    "--permutations", "20"]) == 2
    assert "is not one of" not in capsys.readouterr().out


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
    assert "[uses the 2 and 4 LT columns; EXTRA_HREF_EQUAL FALSE]" in text  # beside the reading
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


# ------------------------------------------------------------------------------------------ fix round 1
def weighted_spearman(w: np.ndarray, x: np.ndarray, y: np.ndarray) -> float:
    """Spearman at a weighted measure: Pearson of the weighted mid-distribution functions.

    ``F(x_j) = sum_i w_i (1{x_i < x_j} + 1{x_i = x_j}/2)``, likewise ``G``; the weighted Pearson
    correlation of ``(F, G)`` written with weighted means (it does not assume they are 1/2).
    """
    cx = (x[:, None] < x[None, :]) + 0.5 * (x[:, None] == x[None, :])
    cy = (y[:, None] < y[None, :]) + 0.5 * (y[:, None] == y[None, :])
    a, b = w @ cx, w @ cy
    ma, mb = w @ a, w @ b
    return float((w @ (a * b) - ma * mb) / np.sqrt((w @ (a * a) - ma**2) * (w @ (b * b) - mb**2)))


def test_r2_spearman_influence_equals_gateaux_derivative_with_and_without_ties() -> None:
    """psi of the Spearman correlation (H1d) equals the Gateaux derivative of the weighted-rank
    correlation, n = 50, on a tie-free sample and on a sample with many ties, and with a domain.

    Reference: ``weighted_spearman`` above (weighted mid-distribution functions; the ranks move with
    the weights, so the derivative includes the rank-change terms). The value equals
    ``scipy.stats.spearmanr`` to 1e-12; sum psi = 0 within 1e-12 of sum |psi| (c1 rules); the
    result is unchanged, exactly, by strictly increasing transforms of either variable (the
    transforms of ``core/profile``). Tolerance of the derivative as in c1.
    """
    rng = rng_for("r2-spearman")
    n = 50
    x = rng.standard_normal(n)
    y = 0.6 * x + 0.8 * rng.standard_normal(n)
    for xs, ys in ((x, y), (np.round(x, 1), np.round(y, 0))):  # the second has ties
        psi, rho = rd.psi_spearman(xs, ys)
        assert rho == pytest.approx(sps.spearmanr(xs, ys).statistic, abs=1e-12)
        assert_gateaux(psi, gateaux(lambda w: weighted_spearman(w, xs, ys), n))
    ties = np.round(x, 1)
    assert len(np.unique(ties)) < n
    dom = rng.random(n) < 0.8
    rows = np.flatnonzero(dom)
    psi, rho = rd.psi_spearman(x, y, dom)
    assert np.all(psi[~dom] == 0.0)
    assert_gateaux(psi[rows], gateaux(lambda w: weighted_spearman(w, x[rows], y[rows]), len(rows)))
    again, rho2 = rd.psi_spearman(np.exp(3 * x), np.log(y - y.min() + 1.0))
    base_psi, base_rho = rd.psi_spearman(x, y)
    assert rho2 == base_rho and np.array_equal(again, base_psi)
    with pytest.raises(rd.NotComputable, match="Spearman"):
        rd.psi_spearman(np.ones(10), np.arange(10.0))


def test_r1_a_non_finite_half_width_is_not_computable_and_never_reads_below_10(
        tmp_path, capsys) -> None:
    """An interval at (-inf, inf) (failed resamples) or NaN makes the D5 and D6 readings "not
    computable"; nothing reads "below 10%" and exit is 2.

    Reference: the finding's probe. ``three_way_reading(0.03, 0.004, 0.1 * inf)`` read "below 10%";
    now every non-finite input raises ``NotComputable``, as does ``full_halfwidth`` of an infinite
    or NaN half-width. End to end the world's H2a range interval is [-inf, inf] and its H2b(ii)
    interval [nan, nan]: both readings are "not computable: ... half-width not finite", the shifts
    and SEs are still printed, and "may be stated below 10%" never appears.
    """
    for bad in (math.inf, math.nan):
        with pytest.raises(rd.NotComputable, match="non-finite"):
            rd.three_way_reading(0.03, 0.004, 0.1 * bad)
        with pytest.raises(rd.NotComputable, match="non-finite"):
            rd.three_way_reading(bad, 0.004, 0.01)
        with pytest.raises(rd.NotComputable, match="half-width"):
            rd.full_halfwidth(bad, {"name": "pilot", "n_test": 500}, "n_test")
    d, res, _ = build_world(rng_for("world"))
    res["systems"]["lorenz63"]["H2a"]["range_ci"] = [-math.inf, math.inf]
    res["systems"]["lorenz63"]["H2b"]["library_change"]["ci"] = [math.nan, math.nan]
    code = rd.main([str(write_run(tmp_path, d, res)), "--resamples", "100", "--permutations", "50"])
    out = capsys.readouterr().out
    assert "D5 reading: half-width not finite: interval [-inf, inf]" in out
    assert "D6 reading: half-width not finite: interval [nan, nan]" in out
    assert "reading: below 10%" not in out and "may be stated below 10%" not in out
    assert "Delta_sh" in out and "SE " in out and code == 2


def build_d5_dump(n: int = 300):
    """A constructed dump for the whole D5 estimator: the model of ``m5_d5split.py`` as
    ``w_star``, ``w_star_A``, ``w_star_B`` at 1, 2 and 4 LT, with states that are ineligible
    (not small at 1 LT), non-contiguous (small only at 1 LT and 4 LT) or short (small at 1 and 2 LT)."""
    a, b, m = d5_script_model(20261017, n, 0.3, 0.5)
    e_c, e_p = np.full((n, 3), 0.01), np.full((n, 3), 0.01)
    idx = np.arange(n)
    e_c[idx % 7 == 0, 0] = 0.9
    e_c[idx % 11 == 1, 1] = 0.9
    e_p[idx % 13 == 2, 2] = 0.9
    d = {"core/horizons": np.array([30, 60, 120]), "core/ref_index": np.array(0),
         "meta/steps_per_lyapunov": np.array(30), "core/E_C": e_c, "core/E_P": e_p,
         "core/w_star": m, "core/w_star_A": a, "core/w_star_B": b}
    return d, (a, b, m, e_c, e_p)


def loop_d5(a, b, m, e_c, e_p) -> tuple[float, float, int, float]:
    """The D5 estimator by explicit loops: leading segment, eligibility, the three medians."""
    n = len(m)

    def segment(i: int) -> int:
        length = 0
        while length < 3 and math.sqrt(e_c[i, length]) <= 0.5 and math.sqrt(e_p[i, length]) <= 0.5:
            length += 1
        return length

    rows = [i for i in range(n) if segment(i) >= 2]

    def med(w) -> float:
        return float(np.median([max(w[i, :segment(i)]) - min(w[i, :segment(i)]) for i in rows]))

    shift = 0.5 * (med(a) + med(b)) - med(m)
    return shift, shift / (math.sqrt(2.0) - 1.0), len(rows), med(m)


def test_r3_the_whole_d5_estimator_equals_an_independent_loop_value() -> None:
    """Eligibility, the fixed segments, the half-draw ranges and the medians over the eligible states.

    Reference: ``loop_d5`` (explicit loops over states: the leading small-error segment from the
    200-draw moments, eligible iff at least two horizons, the range of each of the three weight sets
    over that fixed segment, medians over the eligible states, ``Delta_sh = (med A + med B)/2 - med
    200`` and ``B = Delta_sh/(sqrt 2 - 1)``), on the model of ``m5_d5split.py`` placed in a dump with
    ineligible, non-contiguous and short states (the generator is this file's ``make_rng``
    re-implementation, not the script's own stream: the plan's "match the script" cannot hold
    bitwise under the make_rng rule, a planner point). Tolerance 1e-12 relative (medians of the same
    floats; the Richardson factor is one division).
    """
    d, parts = build_d5_dump()
    shift, bias, n_eligible, med_full = loop_d5(*parts)
    assert 150 < n_eligible < 270  # the construction removes some states and keeps most
    rep = rd.Report()
    cfg = {"linear_regime_rms": 0.5, "bootstrap_block": 5, "name": "pilot", "n_test": 300,
           "bootstrap_resamples": 500}
    res = {"H2a": {"median_range": med_full, "range_ci": [0.1, 0.3]}}
    ctx = rd.Context("s", rd.Dump(d, "mem"), res, cfg, rep, 7, 100, 10)
    rd.section_d5(ctx)
    out = rep.data["s"]["D5"]
    assert out["n_eligible"] == n_eligible
    assert out["delta_sh"] == pytest.approx(shift, rel=1e-12, abs=1e-15)
    assert out["bias_order_half"] == pytest.approx(bias, rel=1e-12, abs=1e-15)
    assert out["reading"] in ("below 10%", "not below 10%", "not determined")
    assert not rep.defects  # the median range of the dump is the results leaf, exactly
    assert any("D5 V4 check" in line for line in rep.incomplete)  # the V4 arrays are absent here
    # an infinite interval: the shift is still computed and printed, the reading is not computable
    res["H2a"]["range_ci"] = [-math.inf, math.inf]
    rep2 = rd.Report()
    rd.section_d5(rd.Context("s", rd.Dump(d, "mem"), res, cfg, rep2, 7, 100, 10))
    out2 = rep2.data["s"]["D5"]
    assert out2["delta_sh"] == out["delta_sh"] and "reading" not in out2
    assert any("D5 reading: half-width not finite" in line for line in rep2.incomplete)
    assert any("D5 V4 check" in line for line in rep2.incomplete)  # the V4 check still ran


def test_r4_the_reproduction_floor_removes_false_mismatches_and_hides_no_real_one() -> None:
    """Delta R^2 near 0: the tool's ``mean(gain)/SST`` and production's ``R^2(F4) - R^2(F3)`` differ
    by round-off (about 1e-14 absolute); the check is ``tol max(|leaf|, scale)`` with ``scale =
    max(|R^2_3|, |R^2_4|)``.

    Reference: 200 probes (n = 500, |Delta R^2| about 1e-4, ``make_rng``): the old bound ``1e-12
    |leaf|`` is exceeded on some (so the probe is exercising the case), the new bound on none. Mutation
    test: a leaf off by a relative 1e-6 (7e-11 absolute at 7e-5, against an allowed 4e-13), by 1e-9
    absolute, or by 1% is a MISMATCH; off by 1e-14 absolute is a MATCH; the same for the class with
    tolerance 1e-9 and scale 1 (a partial correlation): 1e-6 mismatches, 1e-11 matches.
    """
    rng = rng_for("r4")
    old_fail = new_fail = 0
    for _ in range(200):
        y = rng.standard_normal(500)
        f3 = 0.5 * y + 0.5 * rng.standard_normal(500)
        f4 = f3 + 0.01 * rng.standard_normal(500)
        mine = rd.psi_delta_r2(y, f3, f4)[1]
        sst = np.sum((y - y.mean()) ** 2)
        r3, r4 = 1 - np.sum((y - f3) ** 2) / sst, 1 - np.sum((y - f4) ** 2) / sst
        leaf = r4 - r3
        old_fail += abs(mine - leaf) > 1e-12 * abs(leaf)
        new_fail += abs(mine - leaf) > 1e-12 * max(abs(leaf), abs(r3), abs(r4))
    assert old_fail >= 1 and new_fail == 0

    def verdict(mine: float, leaf: float, tol: float, scale: float) -> bool:
        rep = rd.Report()
        ctx = rd.Context("s", rd.Dump({}, "mem"), {"a": {"b": leaf}}, {}, rep, 1, 2, 2)
        rd.check(ctx, "x", mine, ("a", "b"), tol, scale=scale)
        return not rep.defects

    leaf = 7e-5
    assert verdict(leaf + 1e-14, leaf, 1e-12, 0.4)
    for off in (leaf * 1e-6, 1e-9, leaf * 0.01):
        assert not verdict(leaf + off, leaf, 1e-12, 0.4)
    assert verdict(0.3 + 1e-11, 0.3, 1e-9, 1.0) and not verdict(0.3 + 1e-6, 0.3, 1e-9, 1.0)
    assert verdict(1e-12, 0.0, 1e-9, 1.0) and not verdict(1e-6, 0.0, 1e-9, 1.0)


def test_r4_a_near_zero_delta_r2_in_the_world_is_a_match_and_a_one_percent_error_is_not(
        tmp_path, capsys) -> None:
    """End to end with a Q-N target whose gain is about 1e-5, the leaf computed by the test's route.

    Reference: ``r2(F4) - r2(F3)`` (this file). The run reports MATCH for it, and the same run with
    the leaf off by 1% of itself reports MISMATCH (exit 1).
    """
    d, res, _ = build_world(rng_for("world"))
    y = d["qn/oracle/log_horizon/y"]
    rng = rng_for("r4-world")
    d["qn/oracle/log_horizon/pred3"] = 0.5 * y + 0.5 * rng.standard_normal(N)
    d["qn/oracle/log_horizon/pred4"] = d["qn/oracle/log_horizon/pred3"] + 0.002 * rng.standard_normal(N)
    res = build_results(d)
    leaf = res["systems"]["lorenz63"]["Q-N"]["oracle"]["log_horizon"]["delta_r2"]
    assert 0 < abs(leaf) < 1e-3
    rd.main([str(write_run(tmp_path, d, res)), "--resamples", "50", "--permutations", "20"])
    assert "MISMATCH" not in capsys.readouterr().out
    res["systems"]["lorenz63"]["Q-N"]["oracle"]["log_horizon"]["delta_r2"] = leaf * 1.01
    code = rd.main([str(write_run(tmp_path / "b", d, res)), "--resamples", "50",
                    "--permutations", "20"])
    assert "check Q-N oracle log_horizon delta R^2" in capsys.readouterr().out and code == 1


def test_r2_h1d_leaf_mutation_is_a_mismatch(tmp_path, capsys) -> None:
    """H1d's reproduction check reads ``H1d/rows/<name>/spearman``: a leaf off by 1e-6 is a MISMATCH.

    Reference: the unperturbed leaf is the test's ``scipy.stats.spearmanr`` of the proxy with the
    oracle (MATCH in the full-run test); perturbing it by 1e-6 is 10^6 times the 1e-12 bound.
    """
    d, res, _ = build_world(rng_for("world"))
    res["systems"]["lorenz63"]["H1d"]["rows"]["growth"]["spearman"] += 1e-6
    code = rd.main([str(write_run(tmp_path, d, res)), "--resamples", "50", "--permutations", "20"])
    out = capsys.readouterr().out
    assert "check H1d growth Spearman" in out and out.count(": MISMATCH") == 1 and code == 1


def test_r5_a_failure_inside_a_section_names_what_is_skipped_and_continues(capsys) -> None:
    """D3: a missing weight array loses only that rule's state part (named), the rule's own log-SD
    and the other rules still print, and the non-positive count of the state part is reported. D6:
    a missing ``bootstrap_block`` is named, the shifts and f_b still print, no reading is made.

    Reference: the contract (every skipped item is named "not computable" with its reason).
    """
    n = 40
    rng = rng_for("r5")
    d = {"meta/n_eval_draws": np.array(2), "core/ref_index": np.array(0),
         "core/E_C": 1.0 + rng.random((n, 1)), "core/E_P": 1.0 + rng.random((n, 1)),
         "core/C": 0.2 * rng.random((n, 1))}
    for rule in ("A1", "A2", "A3", "A4", "A5"):
        d[f"core/state_mse/{rule}"] = np.exp(rng.normal(-3, 1, (n, 1)))
    for rule in ("A2", "A4", "A5"):  # A3's weights are absent
        d[f"core/weight_href/{rule}"] = rng.random((n, 2))
    rep = rd.Report()
    rd.section_d3(rd.Context("s", rd.Dump(d, "mem"), {}, {}, rep, 1, 2, 2))
    text = "\n".join(rep.lines)
    assert "not computable: s D3 A3 state part: array 'core/weight_href/A3' is not in" in text
    for rule in ("A1", "A2", "A3", "A4", "A5"):
        assert f"  {rule}: log-SD" in text
    assert set(rep.data["s"]["D3"]["rules"]) == {"A1", "A2", "A3", "A4", "A5"}
    # a zero state part is counted, not dropped: A1 with E_P = 0 on one state
    d["core/E_P"][3, 0] = 0.0
    rep = rd.Report()
    rd.section_d3(rd.Context("s", rd.Dump(d, "mem"), {}, {}, rep, 1, 2, 2))
    assert rep.data["s"]["D3"]["rules"]["A1"]["state_part_n_nonpositive"] == 1
    assert "1 non-positive state-part values excluded" in "\n".join(rep.lines)
    world, res, _ = build_world(rng_for("world"))
    cfg = {k: v for k, v in CFG.items() if k != "bootstrap_block"}
    rep = rd.Report()
    rd.section_d6(rd.Context("lorenz63", rd.Dump(world, "mem"), res["systems"]["lorenz63"], cfg,
                             rep, 1, 50, 10))
    text = "\n".join(rep.lines)
    assert "D6 block length: results leaf bootstrap_block is absent" in text.replace("lorenz63 ", "")
    assert "Delta_sh" in text and "n_lib 1000: f_b" in text
    assert "point reading" not in text and "0.1 hw_full" not in text


def test_r6_unexpected_exceptions_exit_2_with_the_partial_report(tmp_path, capsys,
                                                                 monkeypatch) -> None:
    """A corrupt archive and an unexpected exception exit 2 (not the MISMATCH code), print what was
    computed so far and an INTERNAL ERROR line naming the place.

    Reference: the finding. A garbage ``.npz`` raises inside ``np.load``; a patched
    ``run_level_lines`` raises ``RuntimeError`` after the systems were done: the header, the system
    block and the exception line are all printed.
    """
    d, res, _ = build_world(rng_for("world"))
    run_dir = write_run(tmp_path, d, res)
    (run_dir / "states" / "lorenz63.npz").write_bytes(b"this is not a zip archive")
    code = rd.main([str(run_dir)])
    out = capsys.readouterr().out
    assert code == 2 and out.startswith("DEVELOPMENT (DEV-1)")
    assert "INTERNAL ERROR: lorenz63 (D1 to D6):" in out and "MISMATCH" not in out
    run_dir = write_run(tmp_path / "b", d, res)

    def boom(rep):
        raise RuntimeError("simulated defect")

    monkeypatch.setattr(rd, "run_level_lines", boom)
    code = rd.main([str(run_dir), "--resamples", "50", "--permutations", "20"])
    out = capsys.readouterr().out
    assert code == 2 and "=== lorenz63 ===" in out and "D6 H2b(ii)" in out
    assert "INTERNAL ERROR: run: RuntimeError: simulated defect" in out
    assert "the report above is partial" in out


def test_r7_run_level_lines_reproduce_the_plans_probabilities() -> None:
    """The run-level D2 line: P(at least one) = 1 - prod(1 - r_i) over the primary series, 0.97 for the
    pilot's 18 (12 at n = 500, 6 at n = 300) and 0.83 for the full preset's 18 at n = 1000.

    Reference: the plan's numbers (B1 7.D2) and the per-series rates 0.164, 0.210, 0.094, hand
    products. The D1 line counts every series, not only primaries.
    """
    def log_of(ns: list[int], fired: list[bool], within: list[bool]) -> rd.Report:
        rep = rd.Report()
        for k, (n, f, w) in enumerate(zip(ns, fired, within)):
            rep.series_log.append({"system": "s", "name": f"series {k}", "n": n, "primary": True,
                                   "acf1": 0.0 if w else 0.3, "within": w, "fires": f})
        rep.series_log.append({"system": "s", "name": "other", "n": 500, "primary": False,
                               "acf1": 0.5, "within": False, "fires": None})
        rd.run_level_lines(rep)
        return rep

    pilot = log_of([500] * 12 + [300] * 6, [False] * 17 + [True], [True] * 18)
    assert round(pilot.data["run_level"]["predicted_at_least_one"], 2) == 0.97
    assert pilot.data["run_level"]["predicted_at_least_one"] == pytest.approx(
        1 - 0.836**12 * 0.79**6, rel=1e-12)
    text = "\n".join(pilot.lines)
    assert "D2: the A5 rule fired on 1 of the 18 computed primary series (at least one fired: yes)" \
        in text
    assert "18 of 19 computed series" in text
    assert "NOT every computed series is within: s other (+0.500)" in text
    full = log_of([1000] * 18, [False] * 18, [True] * 18)
    assert round(full.data["run_level"]["predicted_at_least_one"], 2) == 0.83
    assert "at least one fired: no" in "\n".join(full.lines)
    odd = log_of([80] * 3, [False] * 3, [True] * 3)
    assert odd.data["run_level"]["predicted_at_least_one"] is None
    assert "not tabulated for these n" in "\n".join(odd.lines)
    empty = rd.Report()
    rd.run_level_lines(empty)
    assert empty.incomplete and "no series had an autocorrelation" in empty.incomplete[0]


def test_r13_run_level_lines_do_not_read_favourably_over_gaps() -> None:
    """With series not computed, the run-level D1 and D2 sentences are about the computed ones only,
    name the gaps, and never say "none fired" over an empty set.

    Reference: the finding's probe. One computed primary series within its threshold and not
    firing, plus an H2b(i) series and H1a not computed: D1 says "of the computed series only"
    style (the phi = 0 rows apply "to these computed series only") and names both gaps; D2 names
    the uncomputed primary. With no primary series computed, D2 is "not computable" ("0 of 0") and
    makes no statement.
    """
    rep = rd.Report()
    rep.series_log.append({"system": "s", "name": "H3c", "n": 500, "primary": True, "acf1": 0.0,
                           "within": True, "fires": False})
    rep.uncomputed += [("s H2b(i)", True), ("H1a (all systems)", False)]
    rd.run_level_lines(rep)
    text = "\n".join(rep.lines)
    assert "to these computed series only" in text and "every series is within" not in text
    assert "not computed, so not read here: s H2b(i), H1a (all systems)" in text
    assert "(at least one fired: no; primary series not computed: s H2b(i))" in text
    assert not rep.incomplete
    clean = rd.Report()
    clean.series_log.append({"system": "s", "name": "H3c", "n": 500, "primary": True, "acf1": 0.0,
                             "within": True, "fires": False})
    rd.run_level_lines(clean)
    assert "every one of the 1 computed series is within (the phi = 0 rows apply to these series " \
        "only)" in "\n".join(clean.lines)
    bare = rd.Report()
    bare.series_log.append({"system": "s", "name": "H2c A4-A2", "n": 500, "primary": False,
                            "acf1": 0.0, "within": True, "fires": None})
    bare.uncomputed.append(("s H3c", True))
    rd.run_level_lines(bare)
    assert any("run-level D2: 0 of 0 primary series were computed" in line for line in bare.incomplete)
    assert "no statement (no primary series computed)" in "\n".join(bare.lines)
    assert "none fired" not in "\n".join(bare.lines)


def test_r9_default_options_are_not_flagged_and_the_notice_is_always_printed(tmp_path, capsys) -> None:
    """With the default seed, resamples and permutations the report has no "NON-DEFAULT" flag and
    ``options.default`` is true; the NOTICE (seed, options, "not allowed", owner question) is printed
    either way.

    Reference: the finding R9 (the owner's decision; only the wording and the record are the tool's).
    """
    d, res, _ = build_world(rng_for("world"))
    json_path = tmp_path / "o.json"
    rd.main([str(write_run(tmp_path, d, res)), "--json", str(json_path)])
    out = capsys.readouterr().out
    assert "NOTICE: every reading below is computed with tool seed 20261018" in out
    assert "NON-DEFAULT" not in out and "is not allowed" in out and "owner question" in out
    assert json.loads(json_path.read_text())["options"] == {
        "seed": 20261018, "resamples": 2000, "permutations": 1000, "default": True}


def test_r10_e6_f_b_bins_pooled_s_and_the_wu0008_bound_by_hand() -> None:
    """E6: ``f_b`` per bin and per cell with ``s_i`` and with the pooled ``s_bin``, the larger
    governing, the near rule ``min(|u|, |1 - u|) <= 2 s``, and the WU-0008 bound, on ten states that
    hit every bin and every edge.

    Reference: by hand. (w, u, s): 0 (0.0, -0.3, 0.05): 0.3 <= 0.1? no; 1 (0.0, 0.0, 0): 0 <= 0
    yes; 2 (0.05, 0.05, 0.01): 0.05 <= 0.02 no; 3 (0.1, 0.1, 0.04): 0.1 <= 0.08 no (and in the
    closed bin [0.1, 0.9]); 4 (0.5, 0.5, 0.3): 0.5 <= 0.6 yes; 5 (0.9, 0.9, 0.04): min(0.9, 0.1) =
    0.1 <= 0.08 no (closed edge); 6 (0.95, 0.95, 0.03): 0.05 <= 0.06 yes; 7 (1.0, 1.2, 0.01):
    min(1.2, 0.2) = 0.2 <= 0.02 no; 8 (1.0, 1.0, 0): 0 <= 0 yes; 9 undefined (excluded, counted).
    With s_i: near = {1, 4, 6, 8}, f_b = 4/9. Pooled s_bin = sqrt(mean s^2): w = 0: sqrt(0.00125);
    (0, 0.1): 0.01; [0.1, 0.9] (states 3, 4, 5): sqrt(0.0932/3) = 0.17626; (0.9, 1): 0.03; w = 1:
    sqrt(0.00005). With s_bin the near states are {1, 3, 5, 6, 8}: f_b = 5/9, which governs. Bins
    (n, f with s_i, f with s_bin): w=0 (2, 1/2, 1/2); 0<w<0.1 (1, 0, 0); 0.1<=w<=0.9 (3, 1/3, 2/3);
    0.9<w<1 (1, 1, 1); w=1 (2, 1/2, 1/2). Bound 0.40 (1/9) sum_near s: with s_i (0 + 0.3 + 0.03 + 0)
    = 0.4 x 0.33/9; with s_bin (0.035355 + 0.17626 + 0.17626 + 0.03 + 0.0070711) = 0.4 x 0.42494/9; the
    larger is reported. Tolerance 1e-12 (a few operations).
    """
    w = np.array([0.0, 0.0, 0.05, 0.1, 0.5, 0.9, 0.95, 1.0, 1.0, 0.3])
    u = np.array([-0.3, 0.0, 0.05, 0.1, 0.5, 0.9, 0.95, 1.2, 1.0, np.nan])
    s = np.array([0.05, 0.0, 0.01, 0.04, 0.3, 0.04, 0.03, 0.01, 0.0, 0.0])
    out = rd.f_b_by_bin(w, u, u - s, u + s)
    assert out["n_undefined"] == 1 and out["n_defined"] == 9
    assert out["f_b_state"] == pytest.approx(4 / 9) and out["f_b_pooled"] == pytest.approx(5 / 9)
    assert out["f_b"] == pytest.approx(5 / 9) and out["governs"] == "s_bin"
    s_bin = {"w=0": math.sqrt(0.00125), "0<w<0.1": 0.01, "0.1<=w<=0.9": math.sqrt(0.0932 / 3),
             "0.9<w<1": 0.03, "w=1": math.sqrt(0.00005)}
    expect = {"w=0": (2, 1 / 2, 1 / 2), "0<w<0.1": (1, 0.0, 0.0), "0.1<=w<=0.9": (3, 1 / 3, 2 / 3),
              "0.9<w<1": (1, 1.0, 1.0), "w=1": (2, 1 / 2, 1 / 2)}
    for label, (n, f_state, f_pool) in expect.items():
        row = out["bins"][label]
        assert row["n"] == n and row["s_bin"] == pytest.approx(s_bin[label], rel=1e-12)
        assert row["f_b_state"] == pytest.approx(f_state) and row["f_b_pooled"] == pytest.approx(f_pool)
        assert row["f_b"] == pytest.approx(max(f_state, f_pool))
    bound_state = 0.40 * (0.0 + 0.3 + 0.03 + 0.0) / 9
    bound_pool = 0.40 * (s_bin["w=0"] + 2 * s_bin["0.1<=w<=0.9"] + 0.03 + s_bin["w=1"]) / 9
    assert out["bound_state"] == pytest.approx(bound_state, rel=1e-12)
    assert out["bound_pooled"] == pytest.approx(bound_pool, rel=1e-12)
    assert out["bound"] == pytest.approx(max(bound_state, bound_pool), rel=1e-12)
    with pytest.raises(rd.NotComputable, match="no state"):
        rd.f_b_by_bin(w[:1], np.array([np.nan]), np.array([0.0]), np.array([0.0]))


def test_e6_the_paired_bound_is_the_sum_of_the_two_cells_without_cancellation() -> None:
    """Section D6 prints the paired bound as the sum of the two cells' bounds.

    Reference: the two cells of the constructed D6 world of ``test_d6_...`` have f_b = 0 and bound 0
    (u = 0.25 and 0.5 are far from a bound relative to s), so the paired bound is 0 = 0 + 0; a cell
    with a near state adds its bound (hand: u = 0.01, s = 0.02: near, bound 0.40 x 0.02 / n).
    """
    n = 10
    d: dict[str, np.ndarray] = {}
    for n_lib, e_p in ((1000, 1.0), (10000, 1.0)):
        g = f"sweep/rho=0.01|n_lib={n_lib}"
        e_c, c = np.full(n, 2.0), np.full(n, 0.5)
        d[f"{g}/E_C"], d[f"{g}/E_P"], d[f"{g}/C"] = e_c, np.full(n, e_p), c
        for tag, dc in (("A", 0.1), ("B", -0.1)):
            d[f"{g}/E_C_{tag}"], d[f"{g}/E_P_{tag}"], d[f"{g}/C_{tag}"] = e_c, np.full(n, e_p), c + dc
        d[f"{g}/w_star_href"] = np.clip((e_p - c) / (2.0 + e_p - 2.0 * c), 0.0, 1.0)
    # a state of the 10^4 cell near the bound: C = E_P - 0.01 c-wise gives u = 0.01/c
    g = "sweep/rho=0.01|n_lib=10000"
    for tag in ("", "_A", "_B"):
        d[f"{g}/C{tag}"][0] = 0.99 + (0.01 if tag == "_A" else (-0.01 if tag == "_B" else 0.0))
    d[f"{g}/w_star_href"][0] = np.clip((1.0 - 0.99) / (2.0 + 1.0 - 2.0 * 0.99), 0.0, 1.0)
    rep = rd.Report()
    cfg = {"core_noise": 0.01, "bootstrap_block": 5, "name": "pilot", "n_test_sweep": 300,
           "bootstrap_resamples": 500}
    res = {"H2b": {"library_change": {"mean_change": 0.0, "ci": [0.0, 0.1]}}}
    rd.section_d6(rd.Context("s", rd.Dump(d, "mem"), res, cfg, rep, 3, 20, 10))
    fb = rep.data["s"]["D6"]["f_b"]
    assert fb[1000]["bound"] == 0.0
    # state 0: u = (1 - 0.99)/(2 + 1 - 1.98) = 0.01/1.02; halves C = 1.0 and 0.98: u_A = 0/..., 
    u_full = 0.01 / 1.02
    u_a = (1.0 - 1.0) / (3.0 - 2.0)
    u_b = (1.0 - 0.98) / (3.0 - 1.96)
    s0 = abs(u_a - u_b) / 2
    assert min(abs(u_full), abs(1 - u_full)) <= 2 * s0  # near, by hand
    assert fb[10000]["bound_state"] >= 0.40 * s0 / 10 * (1 - 1e-12)
    assert rep.data["s"]["D6"]["bound_paired"] == pytest.approx(fb[1000]["bound"] + fb[10000]["bound"],
                                                                rel=1e-12)


# ------------------------------------------------------------------------------------------ fix round 2
def v4_dump(n_v4: int) -> dict:
    """A V4 block of ``n_v4`` states (all eligible at 1, 2 and 4 LT) with known half-widths."""
    rng = rng_for(f"v4-{n_v4}")
    w_hat = rng.uniform(0.2, 0.8, (3, n_v4, 3))
    return {"core/horizons": HORIZONS, "core/E_C": np.full((n_v4, 5), 0.01),
            "core/E_P": np.full((n_v4, 5), 0.01), "v4/M": np.array([50, 200, 800]),
            "v4/horizons": np.array([30, 60, 120]), "v4/w_hat": w_hat,
            "v4/signed_dev": w_hat - w_hat[2][None], "v4/half_width": rng.uniform(0.01, 0.05, (3, n_v4, 3)),
            "v4/extra_href_equal": np.array(True), "v4/extra_href_diff": np.array(0)}


def test_e5_pilot_equivalent_v4_is_the_median_of_the_first_40_states_or_not_computable() -> None:
    """E5: with 45 V4 states the first-40 value equals ``np.median`` of the first 40 per-state
    half-widths exactly (and differs from the all-states value); with 39 it is "not computable" and
    the label says nothing about 40; the all-states value is always printed.

    Reference: ``np.median`` on the arrays the test put in (exact: the same floats).
    """
    for n_v4, has_40 in ((45, True), (39, False)):
        d = v4_dump(n_v4)
        rep = rd.Report()
        ctx = rd.Context("s", rd.Dump(d, "mem"), {}, {"linear_regime_rms": 0.5}, rep, 1, 10, 10)
        out = rd._d5_v4(ctx)
        text = "\n".join(rep.lines)
        for i, m in enumerate((50, 200, 800)):
            row = out["median_half_width"][m]
            assert row["all"] == float(np.median(d["v4/half_width"][i, :, 0]))
            if has_40:
                assert row["first_40"] == float(np.median(d["v4/half_width"][i, :40, 0]))
                assert row["first_40"] != row["all"]
            else:
                assert row["first_40"] is None
        assert ("pilot-equivalent V4 (median over the first 40 V4 states" in text) is has_40
        assert any("D5 pilot-equivalent V4: only 39 V4 states" in line for line in rep.incomplete) \
            is (not has_40)
        assert f"over all {n_v4} V4 states" in text and "first 40, the pilot" not in text


def test_e8_non_default_options_are_flagged_beside_each_affected_reading(tmp_path, capsys) -> None:
    """E8: with a non-default seed, resamples or permutations the D2 permutation line, the D5 and D6
    SE and reading lines, and the summary say "non-default option"; the default report has none.

    Reference: the contract of amendment 5 E8 (the seed affects D2, D5 and D6; resamples D5 and D6;
    permutations D2). A changed permutations count alone flags D2 and not D5/D6.
    """
    d, res, _ = build_world(rng_for("world"))
    rd.main([str(write_run(tmp_path, d, res)), "--seed", "5", "--resamples", "100",
             "--permutations", "50"])
    out = capsys.readouterr().out
    lines = out.splitlines()

    def flagged(prefix: str) -> list[str]:
        return [ln for ln in lines if prefix in ln or ln.startswith(prefix)]

    for prefix in ("pooled mean log V*(10)/V*(5)", "  Delta_sh", "  reading: "):
        got = [ln for ln in lines if ln.startswith(prefix)] or flagged(prefix)
        assert got and all("[non-default option: seed 5" in ln for ln in got), prefix
    assert any("resamples 100" in ln for ln in flagged("  Delta_sh"))
    assert "NON-DEFAULT OPTION: seed 5, resamples 100, permutations 50" in out
    ctx = rd.Context("s", rd.Dump({}, "mem"), {}, {}, rd.Report(), rd.TOOL_SEED, 2000, 50)
    assert ctx.option_flag("d2") == " [non-default option: permutations 50]"
    assert ctx.option_flag("d5") == "" and ctx.option_flag("d6") == ""
    ctx = rd.Context("s", rd.Dump({}, "mem"), {}, {}, rd.Report(), rd.TOOL_SEED, 100, 1000)
    assert ctx.option_flag("d5") == " [non-default option: resamples 100]"
    assert ctx.option_flag("d2") == ""


def test_r14_a_failed_json_write_exits_2_with_a_message_and_keeps_the_mismatch_code(
        tmp_path, capsys) -> None:
    """R14: ``--json`` into a folder that does not exist prints one stderr line and does not crash
    (a traceback would exit 1, the MISMATCH code); the report is already on stdout; exit 2 for a run
    without mismatch, 1 if there is one.

    Reference: the finding's probe.
    """
    d, res, _ = build_world(rng_for("world"))
    bad = tmp_path / "missing" / "out.json"
    code = rd.main([str(write_run(tmp_path / "a", d, res)), "--resamples", "50",
                    "--permutations", "20", "--json", str(bad)])
    captured = capsys.readouterr()
    assert code == 2 and "cannot write" in captured.err and "FileNotFoundError" in captured.err
    assert "Run level (all systems)" in captured.out
    res["systems"]["lorenz63"]["H3c"]["A5_over_A4_mse"] *= 1.001
    code = rd.main([str(write_run(tmp_path / "b", d, res)), "--resamples", "50",
                    "--permutations", "20", "--json", str(bad)])
    assert code == 1 and "cannot write" in capsys.readouterr().err


def test_r15_the_q_n_scale_does_not_collapse_when_both_r2_are_near_zero() -> None:
    """A no-skill target (F3 = the mean of y plus small noise, R^2 about -3e-5): the old scale ``max(|R^2_3|,
    |R^2_4|)`` false-mismatches some correct cases, the tool's scale (``max`` of those and
    ``SS_3/SST``, ``SS_4/SST``, the sizes of the terms) none.

    Reference: 200 probes (n = 500, ``make_rng``): production's ``(1 - SS_4/SST) - (1 - SS_3/SST)``
    against the tool's ``psi_delta_r2`` value, bound ``1e-12 max(|leaf|, scale)``. The mutation test of
    ``test_r4_...`` (7e-11, 1e-9, 1%) still detects with this scale, since the floor stays about 1e-12
    absolute.
    """
    rng = rng_for("r15")
    old_fail = new_fail = 0
    for _ in range(200):
        y = rng.standard_normal(500)
        f3 = y.mean() + 0.005 * rng.standard_normal(500)
        f4 = f3 + 0.003 * rng.standard_normal(500)
        mine = rd.psi_delta_r2(y, f3, f4)[1]
        sst = np.sum((y - y.mean()) ** 2)
        ss3, ss4 = np.sum((y - f3) ** 2) / sst, np.sum((y - f4) ** 2) / sst
        leaf = (1 - ss4) - (1 - ss3)
        old = max(abs(1 - ss3), abs(1 - ss4))
        new = max(old, ss3, ss4)
        old_fail += abs(mine - leaf) > 1e-12 * max(abs(leaf), old)
        new_fail += abs(mine - leaf) > 1e-12 * max(abs(leaf), new)
    assert new_fail == 0 and old_fail >= 1


def test_r16_a_reading_needs_fewer_failed_resamples_than_the_production_threshold() -> None:
    """The D5/D6 reading is "not computable" once the failed resamples reach the count at which the
    production interval at 1 - 0.05/3 is infinite: 5 of 500, 17 of 2000.

    Reference: ``lpcstudy.statistics.percentile_interval`` itself (an independent implementation of
    the threshold): with F failures among B values its bounds are infinite iff F reaches the
    tool's ``failure_threshold(B)``; hand values 5 and 17. A reading with one fewer failure is made.
    """
    from lpcstudy.statistics import percentile_interval
    assert rd.failure_threshold(500) == 5 and rd.failure_threshold(2000) == 17
    for b in (500, 2000):
        thr = rd.failure_threshold(b)
        for failed, infinite in ((thr - 1, False), (thr, True)):
            values = np.arange(float(b))
            values[:failed] = np.nan
            lo, hi, n_failed = percentile_interval(values, rd.PRIMARY_LEVEL)
            assert n_failed == failed and (not math.isfinite(lo)) is infinite
    cfg = {"name": "pilot", "n_test": 500, "bootstrap_resamples": 500}
    res = {"H2a": {"range_ci": [0.1, 0.3]}}
    ctx = rd.Context("s", rd.Dump({}, "mem"), res, cfg, rd.Report(), rd.TOOL_SEED, 500, 10)
    got = rd.budget_reading(ctx, 0.01, 0.002, 4, ("H2a", "range_ci"), "n_test", "d5")
    assert got["reading"] in ("below 10%", "not below 10%", "not determined")
    with pytest.raises(rd.NotComputable, match="5 of 500 bootstrap resamples failed"):
        rd.budget_reading(ctx, 0.01, 0.002, 5, ("H2a", "range_ci"), "n_test", "d5")
    with pytest.raises(rd.NotComputable, match="not available"):
        rd.budget_reading(ctx, 0.01, 0.002, None, ("H2a", "range_ci"), "n_test", "d5")
