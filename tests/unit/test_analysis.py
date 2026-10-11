"""Tests for lpcstudy.analysis: per-state Spearman trend; H1a, H1b and H1d (WU-0002.4 and .5);
H2a and Q-N (WU-0002.6)."""

from __future__ import annotations

import dataclasses
import warnings
from types import SimpleNamespace

import numpy as np
import pytest

from lpcstudy.config import StudyConfig
from lpcstudy.data import make_rng
from lpcstudy.statistics import block_bootstrap_counted


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


# ------------------------------------------------------------------ H2a (WU-0002.6(b))
# Tests for H2a(i) initial segments and H2a(ii) with quadratic seed controls (DEC-0008 A1, A3,
# A4(a), A4(a2), A4(b)). Plan checks T4 to T9 of WU-0002.6, with the applied-mathematician's
# tightenings of docs/agent/notes/2026-10-11-math-wu0002-6.md (T9 at n = 2000, exact targets).

PRIMARY = 1.0 - 0.05 / 3.0


def _hand_controls(x: np.ndarray) -> np.ndarray:
    """Q = [x1, x2, x1^2, x2^2, x1 x2] of a centred (n, 2) array, written out by hand."""
    c = x - x.mean(axis=0)
    return np.column_stack([c[:, 0], c[:, 1], c[:, 0] * c[:, 0], c[:, 1] * c[:, 1],
                            c[:, 0] * c[:, 1]])


def _qr_partial_corr(target: np.ndarray, variable: np.ndarray, controls: np.ndarray) -> float:
    """Partial correlation by explicit QR residuals and a hand Pearson (independent reference)."""
    design = np.column_stack([np.ones(len(target)), controls])
    q_mat, _ = np.linalg.qr(design)
    res_t = target - q_mat @ (q_mat.T @ target)
    res_v = variable - q_mat @ (q_mat.T @ variable)
    res_t, res_v = res_t - res_t.mean(), res_v - res_v.mean()
    return float(np.sum(res_t * res_v) / np.sqrt(np.sum(res_t**2) * np.sum(res_v**2)))


def test_quadratic_controls_columns_and_contract() -> None:
    """``quadratic_controls`` returns [x1, x2, x1^2, x2^2, x1 x2] of the centred seeds.

    Reference: the five columns written out by hand from the centred input. Tolerance: exact
    (``==``): the same float operations. Bad shapes and non-finite input raise (PRIME.4).
    """
    import pytest

    from lpcstudy.analysis import quadratic_controls

    x = np.random.default_rng(3).normal(size=(40, 2)) + 5.0
    assert np.array_equal(quadratic_controls(x), _hand_controls(x))
    with pytest.raises(ValueError):
        quadratic_controls(x[:, :1])
    with pytest.raises(ValueError):
        quadratic_controls(np.where(np.arange(80).reshape(40, 2) == 7, np.nan, x))


def test_partial_correlation_with_quadratic_controls_constructed_case() -> None:
    """T4(a): target q + u and variable p + u + v give exactly 1/sqrt(2).

    Reference: closed form. q, p are in span[1, Q]; u, v are orthonormal and orthogonal to
    every column of [1, Q] (from the QR of [1, Q, a, b] at n = 200), so after partialling out
    the controls the correlation of u and u + v is u.(u + v) / (|u| |u + v|) = 1 / sqrt(2).
    Tolerance 1e-12: cond([1, Q]) is about 10 after centring, so round-off is about
    cond * eps = 1e-14, two orders below.
    """
    from lpcstudy.statistics import partial_correlation

    rng = np.random.default_rng(11)
    x = rng.multivariate_normal([0.0, 0.0], [[1.0, 0.5], [0.5, 1.0]], size=200)
    controls = _hand_controls(x)
    design = np.column_stack([np.ones(200), controls])
    q_mat, _ = np.linalg.qr(np.column_stack([design, rng.normal(size=200),
                                              rng.normal(size=200)]))
    u, v = q_mat[:, 6], q_mat[:, 7]
    target = design @ np.array([0.3, 1.0, -2.0, 0.5, 0.2, 0.7]) + u
    variable = design @ np.array([-1.0, 0.4, 0.1, 0.9, -0.5, 0.3]) + u + v
    assert abs(partial_correlation(target, variable, controls) - 1 / np.sqrt(2)) < 1e-12


def test_partial_correlation_with_quadratic_controls_matches_qr_reference() -> None:
    """T4(b): on random data (n = 200) the code equals explicit QR residuals and a hand Pearson.

    Reference: ``np.linalg.qr`` projection and a hand-written Pearson formula (independent of
    ``lstsq`` and ``np.corrcoef``). Tolerance 1e-12 (round-off about cond * eps = 1e-14).
    The same agreement holds for the centring chosen on a resample: T4(c) re-centred controls
    give the same value, because span[1, Q] does not change under translation.
    """
    from lpcstudy.analysis import quadratic_controls
    from lpcstudy.statistics import partial_correlation

    rng = np.random.default_rng(12)
    x = rng.normal(size=(200, 2)) @ np.array([[1.0, 0.4], [0.0, 0.9]]) + 3.0
    target, variable = rng.normal(size=200), rng.normal(size=200) + 0.3 * x[:, 0] ** 2
    controls = quadratic_controls(x)
    ours = partial_correlation(target, variable, controls)
    assert abs(ours - _qr_partial_corr(target, variable, _hand_controls(x))) < 1e-12
    idx = rng.integers(0, 200, 200)  # a resample with repeats
    resampled = partial_correlation(target[idx], variable[idx], controls[idx])
    recentred = partial_correlation(target[idx], variable[idx], _hand_controls(x[idx]))
    assert abs(resampled - recentred) < 1e-12


def _synthetic(model: str, n: int, rng: np.random.Generator, tail: float = 0.02) -> dict:
    """Synthetic H2a models S0, S1, S2, S0n (math note Q-A8); returns the arrays and params.

    x ~ N(0, [[1, .5], [.5, 1]]); z, e, eta, g iid N(0, 1). With bump = a (x1^2 - 1):
    Lam = .5 x1 - .3 x2 + z + bump; L = 2 (x2 - x1) + bI z + 1.2 e + bump;
    h = .8 x1 - .4 x2 + bZ z + eta + bump; w* = 0 iff h > c0 = Phi^-1(.7) sqrt(Var h), with
    Var h = .48 + bZ^2 + 1 + 2 a^2 (population); else w* = 1 iff g > Phi^-1(1 - tail); else
    sigmoid(L). S0: bI = bZ = a = 0; S1: bI = .447; S2: bZ = .5; S0n: a = .6.
    """
    from scipy.stats import norm

    b_i, b_z, a = {"S0": (0.0, 0.0, 0.0), "S1": (0.447, 0.0, 0.0), "S2": (0.0, 0.5, 0.0),
                   "S0n": (0.0, 0.0, 0.6)}[model]
    x = rng.multivariate_normal([0.0, 0.0], [[1.0, 0.5], [0.5, 1.0]], size=n)
    z, e, eta, g = (rng.normal(size=n) for _ in range(4))
    bump = a * (x[:, 0] ** 2 - 1.0)
    lam = 0.5 * x[:, 0] - 0.3 * x[:, 1] + z + bump
    logit_w = 2.0 * (x[:, 1] - x[:, 0]) + b_i * z + 1.2 * e + bump
    hurdle = 0.8 * x[:, 0] - 0.4 * x[:, 1] + b_z * z + eta + bump
    c_zero = norm.ppf(0.7) * np.sqrt(0.48 + b_z**2 + 1.0 + 2.0 * a**2)
    weight = 1.0 / (1.0 + np.exp(-logit_w))
    weight = np.where(g > norm.ppf(1.0 - tail), 1.0, weight)
    weight = np.where(hurdle > c_zero, 0.0, weight)
    return {"x": x, "lam": lam, "w": weight}


def _run_part_ii(data: dict, seed: int = 2) -> dict:
    from lpcstudy.analysis import h2a_part_ii

    return h2a_part_ii(data["w"], data["lam"], data["x"], n_resamples=2000, block=5,
                       seed=seed, level=PRIMARY)


def _assert_recovery(result: dict, targets: dict[str, float]) -> None:
    """Point estimates within 4/sqrt(n_part) of the exact population values."""
    for name, truth in targets.items():
        part = result["part_ii"][name]
        assert abs(part["partial_corr"] - truth) < 4.0 / np.sqrt(part["n_states"]), name


def test_recovery_under_the_null_models_no_part_fails() -> None:
    """T9, S0 and S0n: every population value is exactly 0; no part fails; points recovered.

    Reference: exact population values (math note Q-A8): with quadratic controls the residual
    of Lambda_tilde is z (S0) or z (S0n: the bump lies in span[1, Q]), independent of every
    target and filter, so each part has population value 0. Tolerance: 4/sqrt(n_part) on the
    point (the SD of r-hat is at most 1.02/sqrt(n_part); 4 SD gives a false-failure probability
    of about 1e-4 per check). Verdict: no part may fail; the no-fail margins of (ii-b) at
    n = 2000, R = 2000 (reviewer's measurement, 40 replicates, S0) are 5.3 SD on the upper
    bound, (E[hi] + 0.1)/SD(hi), and 5.8 SD on the lower bound, (0.1 - E[lo])/SD(lo). Seeds
    fixed in the test.
    """
    for model, seed in (("S0", 101), ("S0n", 102)):
        data = _synthetic(model, 2000, np.random.default_rng(seed))
        result = _run_part_ii(data)
        _assert_recovery(result, {"zero": 0.0, "interior": 0.0})
        assert all(p["verdict"] != "fail" for p in result["part_ii"].values()), model
        assert result["part_ii_verdict"] != "fail"
        assert "one" not in result["part_ii"]  # 1.4% of states: below the 5% trigger


def test_recovery_with_three_parts_under_the_null() -> None:
    """T9, S0 with about 8% at w* = 1: part (ii-c) is added; all targets are 0; none fails.

    Reference: exact value 0 for each part (the indicator 1{w* = 1} depends on g only, which is
    independent of Lambda_tilde given the seeds). Tolerance as in the other null checks.
    """
    from scipy.stats import norm

    tail = 0.115  # P(g > t) among the 70% non-zero states: about 8% of all states at w* = 1
    data = _synthetic("S0", 2000, np.random.default_rng(103), tail=tail)
    assert 0.05 < np.mean(data["w"] == 1.0) < 0.11 and norm.ppf(1.0 - tail) > 0
    result = _run_part_ii(data)
    assert set(result["part_ii"]) == {"zero", "interior", "one"}
    _assert_recovery(result, {"zero": 0.0, "interior": 0.0, "one": 0.0})
    assert result["part_ii_verdict"] != "fail"
    assert result["n_w_one"] == int(np.sum(data["w"] == 1.0))


def test_recovery_s1_interior_part_fails_and_zero_part_does_not() -> None:
    """T9, S1: (ii-b) population value 0.447 / sqrt(0.447^2 + 1.44) = 0.3490686853 fails.

    Reference: closed form (the partial correlation of z + L's residual): the residual of the
    logit given the controls is bI z + 1.2 e, so r = bI / sqrt(bI^2 + 1.44), and (ii-a) is 0
    because the hurdle does not depend on z. Tolerance 4/sqrt(n_part). Fail margin at n = 2000,
    R = 2000, blocks of 5 (reviewer's measurement, 40 replicates): 6.9 SD of the lower bound,
    that is (E[lo] - 0.1)/SD(lo) with E[lo] = 0.291 and SD(lo) = 0.0275. The no-fail margin on
    (ii-a) is the math note's 7.0 SD (15 bootstraps; not re-measured by the reviewer).
    """
    result = _run_part_ii(_synthetic("S1", 2000, np.random.default_rng(104)))
    _assert_recovery(result, {"zero": 0.0, "interior": 0.3490686853})
    assert result["part_ii"]["interior"]["verdict"] == "fail"
    assert result["part_ii"]["zero"]["verdict"] != "fail"
    assert result["part_ii_verdict"] == "fail"


def test_recovery_s2_zero_part_fails_and_interior_part_does_not() -> None:
    """T9, S2: (ii-a) population value 0.3157925466 fails; (ii-b) is 0; (ii-c) -0.0225107081.

    Reference: (ii-a) by 2-D Gauss-Hermite quadrature of Cov(1{h > c0}, z) (stable to 10 digits
    from 40 to 160 nodes; math note Q-A8); (ii-b): the logit residual 1.2 e is independent of
    the selection; (ii-c) is not triggered at 1.4% of states and is not asserted here.
    Tolerance 4/sqrt(n_part); fail margin at least 9.1 SD, no-fail margin on (ii-b) at least
    5.75 SD.
    """
    result = _run_part_ii(_synthetic("S2", 2000, np.random.default_rng(105)))
    _assert_recovery(result, {"zero": 0.3157925466, "interior": 0.0})
    assert result["part_ii"]["zero"]["verdict"] == "fail"
    assert result["part_ii"]["interior"]["verdict"] != "fail"
    assert result["part_ii_verdict"] == "fail"


def test_quadratic_controls_remove_the_nonlinear_confound_that_linear_ones_miss() -> None:
    """T9, S0n: with linear controls (ii-a) is about 0.306 (>= 0.05); with quadratic it is <= 0.0065.

    Reference: independent QR partial correlation (not the code under test) on n = 4e5 states;
    exact population values 0.306 (Monte Carlo, SE 0.002) with linear controls and 0 with
    quadratic ones. Tolerance: the quadratic value must be below 0.0065, which is 4 SE of
    sqrt(1/n) = 0.0016; the linear value must be at least 0.05, about 150 SE below its value.
    """
    data = _synthetic("S0n", 400_000, np.random.default_rng(106))
    zero = (data["w"] == 0.0).astype(float)
    linear = abs(_qr_partial_corr(zero, data["lam"], data["x"]))
    quadratic = abs(_qr_partial_corr(zero, data["lam"], _hand_controls(data["x"])))
    assert linear >= 0.05
    assert quadratic <= 0.0065


def test_parts_share_the_resamples_and_refit_inside_each_one() -> None:
    """The parts use the same index sets, domain filters are applied inside, fits are redone.

    Reference: an independent loop over ``block_resample_indices`` (same integer seed) that
    filters the interior states inside each resample and calls ``_qr_partial_corr`` (QR, not
    lstsq) with controls centred on the full sample; the intervals of the code equal those of
    ``percentile_interval`` on the reference values. Tolerance 1e-10: the reference differs
    from the code only by round-off (QR against lstsq, about 1e-14 per value, quantiles
    interpolate two of them).
    """
    from lpcstudy.analysis import h2a_part_ii
    from lpcstudy.statistics import block_resample_indices, percentile_interval

    data = _synthetic("S1", 300, np.random.default_rng(107))
    controls = _hand_controls(data["x"])
    zero = (data["w"] == 0.0).astype(float)
    interior = (data["w"] > 0.0) & (data["w"] < 1.0)
    inner = np.where(interior, data["w"], 0.5)  # placeholder outside the interior, never read
    logit = np.log(inner / (1.0 - inner))
    ref = {"zero": [], "interior": []}
    for idx in block_resample_indices(300, 100, 5, 9):
        ref["zero"].append(_qr_partial_corr(zero[idx], data["lam"][idx], controls[idx]))
        sel = idx[interior[idx]]
        ref["interior"].append(_qr_partial_corr(logit[sel], data["lam"][sel], controls[sel]))
    result = h2a_part_ii(data["w"], data["lam"], data["x"], n_resamples=100, block=5, seed=9,
                         level=PRIMARY)
    for name in ("zero", "interior"):
        lo, hi, n_failed = percentile_interval(np.array(ref[name]), PRIMARY)
        assert result["part_ii"][name]["n_failed_resamples"] == n_failed == 0
        assert np.allclose(result["part_ii"][name]["ci"], [lo, hi], atol=1e-10, rtol=0)
    assert result["part_ii"]["interior"]["n_states"] == int(interior.sum())
    assert result["part_ii"]["zero"]["n_states"] == 300


def test_constant_indicator_resamples_are_counted_as_failed() -> None:
    """A resample whose indicator is constant is a failed resample, counted, not dropped (A3).

    Reference: the count of resamples (from ``block_resample_indices``, same integer seed) in
    which the 1{w* = 0} indicator is constant, computed here by hand. With 3 zeros among 100
    states, many resamples hold none. Tolerance: exact integer. The failures reach the
    threshold floor((B - 1) a) + 1, so both bounds are infinite and the part is inconclusive
    with the reason of ``criterion_verdict`` (never a pass or fail from the finite part).
    """
    from lpcstudy.analysis import h2a_part_ii
    from lpcstudy.statistics import block_resample_indices

    rng = np.random.default_rng(108)
    n = 100
    weight = rng.uniform(0.1, 0.9, n)
    weight[[10, 11, 60]] = 0.0
    seeds, lam = rng.normal(size=(n, 2)), rng.normal(size=n)
    expected = sum(1 for idx in block_resample_indices(n, 200, 5, 4)
                   if np.ptp((weight[idx] == 0.0).astype(float)) == 0.0)
    assert 20 < expected < 200
    part = h2a_part_ii(weight, lam, seeds, n_resamples=200, block=5, seed=4,
                       level=PRIMARY)["part_ii"]["zero"]
    assert part["n_failed_resamples"] == expected
    assert part["ci"] == [-np.inf, np.inf]
    assert part["verdict"] == "inconclusive" and part["reason"] == "failed resamples >= threshold"


def test_third_part_triggers_at_six_of_one_hundred_and_not_at_five() -> None:
    """T5: the indicator is ``w == 0.0``, the interior is ``0 < w < 1``, (ii-c) needs > 5%.

    Reference: hand counts on constructed weights (n = 100): 6 states at w* = 1 give
    20 * 6 > 100 so the third part exists; 5 give 20 * 5 = 100, not strictly more, so it does
    not. ``np.clip`` returns exact 0.0 and 1.0, so equality tests are exact. Tolerance: exact.
    """
    from lpcstudy.analysis import h2a_part_ii

    rng = np.random.default_rng(109)
    seeds, lam = rng.normal(size=(100, 2)), rng.normal(size=100)
    for n_one, expected in ((6, True), (5, False)):
        weight = rng.uniform(0.2, 0.8, 100)
        weight[:20] = 0.0
        weight[20:20 + n_one] = 1.0
        result = h2a_part_ii(weight, lam, seeds, n_resamples=20, block=5, seed=1, level=PRIMARY)
        assert ("one" in result["part_ii"]) is expected
        assert result["n_w_zero"] == 20 and result["n_w_one"] == n_one
        assert result["part_ii"]["interior"]["n_states"] == 80 - n_one
        assert result["part_ii"]["zero"]["n_states"] == 100


def test_part_ii_verdicts_use_the_open_band_and_the_multi_part_rule(monkeypatch) -> None:
    """T7: band (-0.1, 0.1) open; (ii) fails iff any part fails, passes iff all pass; n = 49/50.

    Reference: hand-enumerated cases on crafted bootstrap values: the patched ``bootstrap_values``
    returns columns that are half ``lo`` and half ``hi``, so the percentile interval is exactly
    ``(lo, hi)`` (quantiles at 0.0083 and 0.9917 of a two-valued column). Cases: (-0.0999,
    0.0999) passes; (-0.1, 0.05) is inconclusive (open edge); (0.1, 0.3) fails; (-0.3, -0.1)
    fails. Combination enumerated over the 3^2 and 3^3 verdict triples. Tolerance: exact.
    """
    import itertools

    import lpcstudy.analysis as an

    cases = {"pass": (-0.0999, 0.0999), "inconclusive": (-0.1, 0.05), "fail": (0.1, 0.3)}
    assert an.combine_verdicts(["fail", "pass"]) == "fail"
    rng = np.random.default_rng(110)

    def run(bounds: list[tuple[float, float]], n: int, n_one: int) -> dict:
        weight = rng.uniform(0.2, 0.8, n)
        weight[: n // 3] = 0.0
        weight[n // 3: n // 3 + n_one] = 1.0
        seeds, lam = rng.normal(size=(n, 2)), rng.normal(size=n)
        values = np.column_stack([np.repeat([lo, hi], 100) for lo, hi in bounds])
        monkeypatch.setattr(an, "bootstrap_values", lambda *a, **k: (np.full(len(bounds), 0.0),
                                                                     values))
        return an.h2a_part_ii(weight, lam, seeds, n_resamples=200, block=5, seed=0,
                              level=PRIMARY)

    for triple in itertools.product(cases, repeat=2):
        out = run([cases[t] for t in triple], 100, 0)
        assert [out["part_ii"][k]["verdict"] for k in ("zero", "interior")] == list(triple)
        want = "fail" if "fail" in triple else "pass" if set(triple) == {"pass"} else "inconclusive"
        assert out["part_ii_verdict"] == want
    for triple in itertools.product(cases, repeat=3):
        out = run([cases[t] for t in triple], 100, 10)
        assert [out["part_ii"][k]["verdict"] for k in ("zero", "interior", "one")] == list(triple)
        want = "fail" if "fail" in triple else "pass" if set(triple) == {"pass"} else "inconclusive"
        assert out["part_ii_verdict"] == want
    # (-0.3, -0.1) fails at the other edge; n = 49 is inconclusive, n = 50 is computed (A3).
    assert run([(-0.3, -0.1), (0.0, 0.05)], 100, 0)["part_ii"]["zero"]["verdict"] == "fail"
    small = run([(-0.05, 0.05), (-0.05, 0.05)], 49, 0)["part_ii"]["zero"]
    assert small["verdict"] == "inconclusive" and small["reason"] == "n_states < 50"
    assert run([(-0.05, 0.05), (-0.05, 0.05)], 50, 0)["part_ii"]["zero"]["verdict"] == "pass"


def test_part_ii_rejects_bad_input() -> None:
    """Bad input raises (PRIME.4): length mismatch, weights outside [0, 1], non-finite weights.

    Reference: the contract of ``h2a_part_ii``. Tolerance: none.
    """
    import pytest

    from lpcstudy.analysis import h2a_part_ii

    rng = np.random.default_rng(111)
    w, lam, x = rng.uniform(0.2, 0.8, 60), rng.normal(size=60), rng.normal(size=(60, 2))
    kwargs = {"n_resamples": 5, "block": 5, "seed": 0}
    with pytest.raises(ValueError):
        h2a_part_ii(w, lam[:-1], x, **kwargs)
    with pytest.raises(ValueError):
        h2a_part_ii(w + 0.5, lam, x, **kwargs)
    with pytest.raises(ValueError):
        h2a_part_ii(np.where(np.arange(60) == 3, np.nan, w), lam, x, **kwargs)


# H2a(i) on the hand-built table of T8: horizons 1, 2, 4 LT.
T8_SMALL = np.array([[1, 1, 1], [1, 1, 0], [1, 0, 0], [1, 0, 1], [0, 1, 1], [0, 0, 0]], bool)
T8_WEIGHT = np.array([[0.10, 0.50, 0.30], [0.20, 0.60, 0.90], [0.40, 0.70, 0.80],
                      [0.05, 0.45, 0.95], [0.30, 0.10, 0.90], [0.50, 0.50, 0.50]])
# Ranges by hand: state 0 over horizons 1, 2, 4: 0.50 - 0.10; state 1 over 1, 2: 0.60 - 0.20.
T8_RANGE_0, T8_RANGE_1 = 0.50 - 0.10, 0.60 - 0.20


def _t8(**kw):
    from lpcstudy.analysis import h2a_initial_segments

    return h2a_initial_segments(T8_WEIGHT, T8_SMALL, ["1", "2", "4"], n_resamples=10, block=2,
                                seed=3, level=PRIMARY, **kw)


def test_initial_segments_on_a_hand_built_table() -> None:
    """T8: L = 3, 2, 1, 1, 0, 0; ranges by hand; non-contiguous states counted; complete case.

    Reference: hand enumeration. Small sets {1,2,4}, {1,2}, {1}, {1,4}, {2,4}, {} give L = 3, 2,
    1, 1, 0, 0, so states 0 and 1 are eligible (ranges 0.50 - 0.10 over three horizons, and
    0.60 - 0.20 over the first two; state 1's third horizon is ignored although w* = 0.90 would
    widen the range). The v1 rule (at least two small horizons) admitted states 0, 1, 3, 4; of
    these 3 ({1,4}) and 4 ({2,4}) are not initial segments, so 2 are non-contiguous. The
    complete-case median equals the median of the {1,2,4} span. Tolerance: exact (``==``); the
    reference uses the same float subtraction.
    """
    out = _t8()
    assert out["n_eligible_states"] == 2 and out["n_excluded_states"] == 4
    assert out["n_noncontiguous_states"] == 2
    assert out["median_range"] == np.median([T8_RANGE_0, T8_RANGE_1])
    assert out["range_by_span"]["1-2"] == {"median": T8_RANGE_1, "n_states": 1}
    assert out["range_by_span"]["1-2-4"] == {"median": T8_RANGE_0, "n_states": 1}
    assert out["complete_case"]["median_range"] == out["range_by_span"]["1-2-4"]["median"]
    assert out["complete_case"]["n_states"] == 1
    assert out["part_i_verdict"] == "inconclusive" and out["part_i_reason"] == "n_states < 50"


def test_initial_segments_resampled_statistic_on_an_index_array_with_repeats(monkeypatch) -> None:
    """T8: the resampled statistic on a hand index array with repeats gives the hand median.

    Reference: hand medians. The index array [0, 0, 1, 2, 5, 1] holds eligible states 0, 0, 1, 1
    (median of [r0, r0, r1, r1] = (r0 + r1) / 2 with r0 = 0.4, r1 = 0.4 at the same float
    values), and complete cases 0, 0 (median r0). With [2, 3, 4, 5] (no eligible state) the
    statistic is NaN, which the bootstrap counts as failed. Tolerance: exact. The statistic is
    captured by patching ``bootstrap_values`` in the module under test.
    """
    import lpcstudy.analysis as an

    captured = {}
    real = an.bootstrap_values

    def spy(statistic, *args, **kwargs):
        captured["stat"] = statistic
        return real(statistic, *args, **kwargs)

    monkeypatch.setattr(an, "bootstrap_values", spy)
    _t8()
    stat = captured["stat"]
    assert np.array_equal(stat(np.array([0, 0, 1, 2, 5, 1])),
                          [np.median([T8_RANGE_0, T8_RANGE_0, T8_RANGE_1, T8_RANGE_1]),
                           T8_RANGE_0])
    assert np.all(np.isnan(stat(np.array([2, 3, 4, 5]))))


def test_initial_segments_pass_when_every_range_is_small() -> None:
    """60 identical eligible states with range 0.02 give interval (0.02, 0.02) and a pass.

    Reference: hand values. Each state has small set {1,2} and weights (0.30, 0.32, 0.9); its
    range is taken over the first two horizons only (0.32 - 0.30), not over the third (0.9
    would give 0.6). The interval is degenerate because every resample holds the same value;
    the upper bound is below 0.1, so ``criterion_verdict`` gives "pass"; the {1,2,4} span is
    empty (median NaN, count 0). Tolerance: exact (the same float subtraction).
    """
    from lpcstudy.analysis import h2a_initial_segments

    weight = np.tile([0.30, 0.32, 0.9], (60, 1))
    small = np.tile([True, True, False], (60, 1))
    out = h2a_initial_segments(weight, small, ["1", "2", "4"], n_resamples=50, block=5, seed=1,
                               level=PRIMARY)
    assert out["median_range"] == 0.32 - 0.30 and out["range_ci"] == [out["median_range"]] * 2
    assert out["n_eligible_states"] == 60 and out["part_i_verdict"] == "pass"
    assert out["range_by_span"]["1-2"]["n_states"] == 60
    assert out["range_by_span"]["1-2-4"]["n_states"] == 0
    assert np.isnan(out["range_by_span"]["1-2-4"]["median"])


def test_initial_segments_band_is_open_at_the_upper_edge() -> None:
    """H2a(i): pass iff the upper bound is below 0.1; fail iff the lower bound is at least 0.1.

    Reference: hand cases on 60 states: all weights equal give range 0 (upper bound 0 < 0.1:
    pass); weights (0.125, 0.25, 0.125) give range 0.25 - 0.125 = 0.125 exactly (lower bound
    0.125 >= 0.1: fail). The edge itself (lower bound exactly 0.1 fails, upper bound exactly 0.1
    does not pass) is the job of ``criterion_verdict`` and is tested with it in test_statistics.
    Tolerance: exact.
    """
    from lpcstudy.analysis import h2a_initial_segments

    small = np.ones((60, 3), bool)
    flat = np.zeros((60, 3))
    wide = np.tile([0.125, 0.25, 0.125], (60, 1))
    kw = {"n_resamples": 30, "block": 5, "seed": 2, "level": PRIMARY}
    assert h2a_initial_segments(flat, small, ["1", "2", "4"], **kw)["part_i_verdict"] == "pass"
    assert h2a_initial_segments(wide, small, ["1", "2", "4"], **kw)["part_i_verdict"] == "fail"


# ------------------------------------------------------------------ Q-N (WU-0002.6(c))
# Plan checks T1 to T3 of WU-0002.6 (DEC-0008 A4(a), A4(c); v3 section 7 table).


def test_qn_reading_returns_each_reading_at_the_table_boundaries() -> None:
    """T1: ``qn_reading`` follows the v3 section 7 table, exactly, on unrounded float64 bounds.

    Reference: the table, enumerated by hand: upper < 0.05 and lower <= 0: "reduces"; lower > 0
    and upper < 0.05: "distinct but small"; lower > 0 and upper >= 0.05: "substantial";
    otherwise "undetermined". Cases: (0, 0.04) reduces; (0, 0.05) undetermined (an upper bound
    of exactly 0.05 is "not < 0.05" and a lower bound of exactly 0 is "not > 0");
    (nextafter(0, 1), nextafter(0.05, 0)) distinct but small; (0.01, 0.05) substantial;
    (-0.01, 0.06) undetermined; a NaN bound is undetermined. Tolerance: exact strings.
    """
    from lpcstudy.analysis import qn_reading

    assert qn_reading(0.0, 0.04) == "reduces"
    assert qn_reading(-0.2, 0.0499) == "reduces"
    assert qn_reading(0.0, 0.05) == "undetermined"
    assert qn_reading(np.nextafter(0.0, 1.0), np.nextafter(0.05, 0.0)) == "distinct but small"
    assert qn_reading(0.01, 0.05) == "substantial"
    assert qn_reading(0.2, 0.9) == "substantial"
    assert qn_reading(-0.01, 0.06) == "undetermined"
    assert qn_reading(float("nan"), 0.01) == "undetermined"
    assert qn_reading(0.01, float("nan")) == "undetermined"
    assert qn_reading(-np.inf, np.inf) == "undetermined"


def test_qn_regressor_parameters_and_seed() -> None:
    """T2: the regressor has the Methods v2 E3 / DEC-0008 A4(c) parameters and routes the seed.

    Reference: the literal parameter values of Methods v2 section M10 E3 (max_iter 300,
    learning_rate 0.05, max_leaf_nodes 15, min_samples_leaf 20) and A4(c) (l2_regularization
    1.0), early_stopping False. The seed is ``sklearn_seed(seed, "qn-regressor")``: the raw
    seed for DEV-0 and a 32-bit value for a 62-bit seed, so a fit does not raise (DEF-0010; the
    DEV-1 value is read from the registry by ``json.load``). Tolerance: exact.
    """
    import json

    from lpcstudy.analysis import qn_regressor
    from lpcstudy.data import sklearn_seed
    from lpcstudy.seeds import REGISTRY_PATH

    params = qn_regressor(20261005).get_params()
    expected = {"max_iter": 300, "learning_rate": 0.05, "max_leaf_nodes": 15,
                "min_samples_leaf": 20, "l2_regularization": 1.0, "early_stopping": False,
                "random_state": 20261005}
    assert {k: params[k] for k in expected} == expected
    with REGISTRY_PATH.open() as handle:
        dev1 = next(e["value"] for e in json.load(handle)["seeds"] if e["id"] == "DEV-1")
    model = qn_regressor(dev1)
    assert model.get_params()["random_state"] == sklearn_seed(dev1, "qn-regressor") < 2**32
    rng = np.random.default_rng(21)
    model.fit(rng.normal(size=(60, 3)), rng.normal(size=60))  # would raise for a raw 62-bit seed


def test_delta_r2_equals_sklearn_r2_score_difference() -> None:
    """T3: ``delta_r2`` equals ``r2_score(y, p4) - r2_score(y, p3)`` and handles resampled rows.

    Reference: ``sklearn.metrics.r2_score`` on a fixed synthetic case (n = 200, ``make_rng``),
    for a continuous target and a 0/1 target, on all rows and on a resample with repeats
    (``r2_score(y[idx], p[idx])``). Tolerance 1e-12: both compute 1 - SS_res/SS_tot in float64
    with different summation orders; the error is about n eps = 5e-14. A constant target or an
    empty row set gives NaN (a failed resample).
    """
    from sklearn.metrics import r2_score

    from lpcstudy.analysis import delta_r2
    from lpcstudy.data import make_rng

    rng = make_rng(7, "delta-r2")
    for y in (rng.normal(size=200), (rng.uniform(size=200) < 0.3).astype(float)):
        p3 = y + rng.normal(scale=0.8, size=200)
        p4 = y + rng.normal(scale=0.5, size=200)
        full = np.arange(200)
        assert abs(delta_r2(y, p3, p4, full) - (r2_score(y, p4) - r2_score(y, p3))) < 1e-12
        idx = rng.integers(0, 200, 200)
        ref = r2_score(y[idx], p4[idx]) - r2_score(y[idx], p3[idx])
        assert abs(delta_r2(y, p3, p4, idx) - ref) < 1e-12
    constant = np.zeros(200)
    assert np.isnan(delta_r2(constant, p3, p4, np.arange(200)))
    assert np.isnan(delta_r2(y, p3, p4, np.array([], dtype=int)))


def _qn_synthetic(n_train: int, n_test: int, seed: int) -> dict:
    """Profiles with a known dependence: w* depends on the first coordinates and a little on N."""
    rng = np.random.default_rng(seed)

    def draw(n: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        x = rng.normal(size=(n, 4))
        score = 1.2 * x[:, 0] - 0.8 * x[:, 1] + 0.6 * x[:, 3] + 0.5 * rng.normal(size=n)
        weight = 1.0 / (1.0 + np.exp(-score))
        weight = np.where(score < -1.5, 0.0, np.where(score > 2.2, 1.0, weight))
        return x, weight, x[:, 0] + 0.3 * x[:, 3] + 0.3 * rng.normal(size=n)

    x_tr, w_tr, t_tr = draw(n_train)
    x_te, w_te, t_te = draw(n_test)
    return {"x_train": x_tr, "w_train": w_tr, "log_t_train": t_tr,
            "x_test": x_te, "w_test": w_te, "log_t_test": t_te}


def test_qn_profile_block_matches_an_independent_fit_and_scores() -> None:
    """The Q-N block: targets, training sets, point values, counts and readings are as specified.

    Reference: built independently in the test from the definition (DEC-0008 A4(a)): the logit is
    fitted on the interior (0 < w* < 1) training states only and scored on the interior test
    states; the indicator 1{w* = 0} by a squared-loss regressor on all states; the log horizon on
    all; all with ``HistGradientBoostingRegressor`` built from the literal parameters of T2
    (not ``qn_regressor``) and ``sklearn.metrics.r2_score``. Tolerance 1e-12 on R^2 and
    Delta R^2 (same data, same deterministic fits; only the summation order of the R^2
    differs, about n eps). Counts are exact. The out-of-[0,1] predictions of the indicator are
    counted, not clipped. Also checks ``reading == qn_reading(*ci)`` for both profiles' interior
    and indicator targets (T1), and that log_horizon has no reading (D-04).
    """
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.metrics import r2_score

    from lpcstudy.analysis import qn_profile_block, qn_reading

    d = _qn_synthetic(500, 200, 31)

    def fit_predict(cols, rows, y, x_test):
        model = HistGradientBoostingRegressor(
            max_iter=300, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=20,
            l2_regularization=1.0, early_stopping=False, random_state=5)
        return model.fit(d["x_train"][rows][:, cols], y[rows]).predict(x_test[:, cols])

    int_tr = (d["w_train"] > 0) & (d["w_train"] < 1)
    int_te = (d["w_test"] > 0) & (d["w_test"] < 1)
    logit_tr = np.log(np.where(int_tr, d["w_train"], 0.5) / (1 - np.where(int_tr, d["w_train"], 0.5)))
    logit_te = np.log(np.where(int_te, d["w_test"], 0.5) / (1 - np.where(int_te, d["w_test"], 0.5)))
    everyone = np.ones(500, bool)
    ref = {}
    for name, rows, y_tr, y_te, keep in (
            ("logit_w_interior", int_tr, logit_tr, logit_te, int_te),
            ("w_zero_indicator", everyone, (d["w_train"] == 0).astype(float),
             (d["w_test"] == 0).astype(float), np.ones(200, bool)),
            ("log_horizon", everyone, d["log_t_train"], d["log_t_test"], np.ones(200, bool))):
        p3 = fit_predict([0, 1, 2], rows, y_tr, d["x_test"])
        p4 = fit_predict([0, 1, 2, 3], rows, y_tr, d["x_test"])
        ref[name] = (r2_score(y_te[keep], p3[keep]), r2_score(y_te[keep], p4[keep]),
                     int(rows.sum()), int(keep.sum()), p3, p4)
    out = qn_profile_block(d["x_train"], d["x_test"], d["w_train"], d["w_test"],
                           d["log_t_train"], d["log_t_test"], seed=5, n_resamples=100, block=5,
                           boot_seed=11)
    for name, (r2_3, r2_4, n_train, n_test, p3, p4) in ref.items():
        got = out[name]
        assert abs(got["r2_three"] - r2_3) < 1e-12 and abs(got["r2_four"] - r2_4) < 1e-12
        assert abs(got["delta_r2"] - (r2_4 - r2_3)) < 1e-12
        assert got["n_train"] == n_train and got["n_test"] == n_test
        assert got["ci"][0] <= got["delta_r2"] or got["n_failed_resamples"] > 0
        assert ("reading" in got) == (name != "log_horizon")
        if "reading" in got:
            assert got["reading"] == qn_reading(*got["ci"]) and got["reason"] is None
    outside = out["w_zero_indicator"]["n_pred_outside_unit"]
    p3z, p4z = ref["w_zero_indicator"][4], ref["w_zero_indicator"][5]
    assert outside["three"] == int(np.sum((p3z < 0) | (p3z > 1)))
    assert outside["four"] == int(np.sum((p4z < 0) | (p4z > 1)))
    n_model = HistGradientBoostingRegressor(
        max_iter=300, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=20,
        l2_regularization=1.0, early_stopping=False, random_state=5)
    n_pred = n_model.fit(d["x_train"][:, :3], d["x_train"][:, 3]).predict(d["x_test"][:, :3])
    assert abs(out["noise_sens_r2_from_three"] - r2_score(d["x_test"][:, 3], n_pred)) < 1e-12


def test_qn_block_intervals_share_resamples_across_targets_and_profiles() -> None:
    """The three intervals of one block come from the same index sets as an independent loop.

    Reference: an independent loop over ``block_resample_indices`` (same integer seed) that
    evaluates ``sklearn.metrics.r2_score`` differences on the resampled rows, with the interior
    filter applied inside each resample, using predictions refitted in the test; the intervals
    equal ``percentile_interval`` of those values. Tolerance 1e-10 (r2_score against the code's
    sums; quantile interpolation of two values each about 1e-14 apart).
    """
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.metrics import r2_score

    from lpcstudy.analysis import qn_profile_block
    from lpcstudy.statistics import block_resample_indices, percentile_interval

    d = _qn_synthetic(400, 150, 32)

    def predict(cols, rows, y):
        model = HistGradientBoostingRegressor(
            max_iter=300, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=20,
            l2_regularization=1.0, early_stopping=False, random_state=5)
        return model.fit(d["x_train"][rows][:, cols], y[rows]).predict(d["x_test"][:, cols])

    int_tr = (d["w_train"] > 0) & (d["w_train"] < 1)
    int_te = (d["w_test"] > 0) & (d["w_test"] < 1)
    safe = lambda w, m: np.log(np.where(m, w, 0.5) / (1 - np.where(m, w, 0.5)))  # noqa: E731
    y_logit_te = safe(d["w_test"], int_te)
    p3 = predict([0, 1, 2], int_tr, safe(d["w_train"], int_tr))
    p4 = predict([0, 1, 2, 3], int_tr, safe(d["w_train"], int_tr))
    p3h = predict([0, 1, 2], np.ones(400, bool), d["log_t_train"])
    p4h = predict([0, 1, 2, 3], np.ones(400, bool), d["log_t_train"])
    ref_logit, ref_hor = [], []
    for idx in block_resample_indices(150, 80, 5, 11):
        sel = idx[int_te[idx]]
        ref_logit.append(r2_score(y_logit_te[sel], p4[sel]) - r2_score(y_logit_te[sel], p3[sel]))
        ref_hor.append(r2_score(d["log_t_test"][idx], p4h[idx])
                       - r2_score(d["log_t_test"][idx], p3h[idx]))
    out = qn_profile_block(d["x_train"], d["x_test"], d["w_train"], d["w_test"],
                           d["log_t_train"], d["log_t_test"], seed=5, n_resamples=80, block=5,
                           boot_seed=11)
    for name, values in (("logit_w_interior", ref_logit), ("log_horizon", ref_hor)):
        lo, hi, n_failed = percentile_interval(np.array(values), 0.95)
        assert out[name]["n_failed_resamples"] == n_failed == 0
        assert np.allclose(out[name]["ci"], [lo, hi], atol=1e-10, rtol=0)


def test_qn_block_reading_needs_fifty_test_states_and_rejects_bad_input() -> None:
    """With fewer than 50 test states in a domain the reading is "undetermined" with a reason (A3).

    Reference: DEC-0008 A3 (a subset statistic needs at least 50 states) applied to the Q-N
    reading, and the contract of the function. Tolerance: exact strings. Bad input raises.
    """
    import pytest

    from lpcstudy.analysis import qn_profile_block

    d = _qn_synthetic(300, 40, 33)
    out = qn_profile_block(d["x_train"], d["x_test"], d["w_train"], d["w_test"],
                           d["log_t_train"], d["log_t_test"], seed=5, n_resamples=20, block=5,
                           boot_seed=1)
    for name in ("logit_w_interior", "w_zero_indicator"):
        assert out[name]["reading"] == "undetermined" and out[name]["reason"] == "n_states < 50"
    kw = {"seed": 5, "n_resamples": 5, "block": 5, "boot_seed": 1}
    with pytest.raises(ValueError):
        qn_profile_block(d["x_train"][:, :3], d["x_test"], d["w_train"], d["w_test"],
                         d["log_t_train"], d["log_t_test"], **kw)
    with pytest.raises(ValueError):
        qn_profile_block(d["x_train"], d["x_test"], d["w_train"] + 0.5, d["w_test"],
                         d["log_t_train"], d["log_t_test"], **kw)
    with pytest.raises(ValueError):
        qn_profile_block(d["x_train"], d["x_test"], d["w_train"][:-1], d["w_test"],
                         d["log_t_train"], d["log_t_test"], **kw)


# ----------------------------------------------------------------------------------- H1a
SIZES = np.array(StudyConfig().library_sizes, dtype=float)
D_TRUE = 2.2


def _seed_sq(rng: np.random.Generator, n_states: int, floor_index: int, sigma: float = 0.05
             ) -> np.ndarray:
    """Per-state squared analog seed error ``(b^2 n^(-2/d) + f^2) LN(0, sigma)`` with heavy tail.

    ``b^2 = 1``, ``d = 2.2`` and ``f^2 = SIZES[floor_index]^(-2/d)`` (the floor equals the power
    term at that library size). The log-normal noise and the inflation by 100 of 5% of the
    entries are drawn independently per (state, n_lib), so the inflation does not cancel as a
    common factor of a state.
    """
    mean = SIZES ** (-2.0 / D_TRUE) + SIZES[floor_index] ** (-2.0 / D_TRUE)
    noise = rng.lognormal(0.0, sigma, size=(n_states, len(SIZES)))
    inflate = np.where(rng.random((n_states, len(SIZES))) < 0.05, 100.0, 1.0)
    return mean * noise * inflate


def _gamma_local_dim(rng: np.random.Generator, n_states: int, dim: float) -> np.ndarray:
    """Levina-Bickel local dimensions ``(k - 2) / S`` under the exact Gamma law, k = 20.

    ``S dim ~ Gamma(k - 1, 1)`` (applied-mathematician, WU-0002.4-5 log, Job 1 item 2), so
    ``S / (k - 1)`` has mean ``1 / dim`` exactly and relative sd ``1 / sqrt(19) = 0.229``.
    """
    return 18.0 * dim / rng.gamma(19.0, size=n_states)


def _fake_cells(sq_by_rho: dict[float, np.ndarray], local_dim: np.ndarray,
                system: str = "lorenz63") -> dict:
    """Library cells keyed ``(rho, n_lib)``: only what ``h1a_library_scaling`` reads."""
    cells = {}
    for rho, sq in sq_by_rho.items():
        for j, size in enumerate(SIZES):
            cells[(rho, int(size))] = SimpleNamespace(
                system=system, noise=rho, library_size=int(size),
                splits={"test": SimpleNamespace(moments=SimpleNamespace(
                    analog_seed=np.sqrt(sq[:, j])))},
                oracles={"test": SimpleNamespace(local_dim=local_dim)})
    return cells


def _config(resamples: int = 200) -> StudyConfig:
    """Full-study settings (block 5, seed) with fewer resamples to keep the unit tests fast."""
    return dataclasses.replace(StudyConfig(), bootstrap_resamples=resamples)


def _hand_ratio(seed_sq: np.ndarray, inverse_dim: np.ndarray, rows: np.ndarray) -> float:
    """Median fit over mean reference on ``rows``, medians and mean formed by hand."""
    from lpcstudy.analysis import _fit_seed_law

    medians = []
    for j in range(seed_sq.shape[1]):
        v = np.sort(seed_sq[rows, j])
        m = len(v)
        medians.append(v[m // 2] if m % 2 else 0.5 * (v[m // 2 - 1] + v[m // 2]))
    return 0.5 * _fit_seed_law(SIZES, np.array(medians))[0] / (inverse_dim[rows].sum() / len(rows))


def test_h1a_median_fit_recovers_inverse_dimension_with_heavy_tail() -> None:
    """The median fit recovers 1/d = 1/2.2 within 5% on log-normal data with a heavy tail (T1).

    Reference: the known d of the synthetic law. 300 states at the five ``library_sizes`` of
    ``StudyConfig``; ``eps^2 = (b^2 n^(-2/d) + f^2) LN(0, 0.05)`` with b^2 = 1, d = 2.2,
    ``f^2 = 3162^(-2/2.2)`` (the floor equals the power term at the second size), and 5% of the
    entries inflated by 100, noise and inflation independent per (state, n_lib). Fixed
    ``default_rng(11002)``, chosen before any output was seen.

    Tolerance: ``abs(fitted * d - 1) <= 0.05`` (the ROADMAP). Over 2000 seeds of this design the
    median fit has relative error with bias +0.0001 and sd 0.0088 (applied-mathematician,
    WU-0002.4-5 log, Job 1 item 3), so 5% is 5.7 sd and no seed in 2000 left the bound. (The
    free floor triples the standard error of the plain median-of-log estimate, which is why
    sigma is 0.05, not 0.5.) The mean fit would miss +-5% with probability 0.92 on this design
    (a mutation probe, not asserted: one seed would be flaky at power 0.92). The fitted value
    also equals ``0.5 * _fit_seed_law(sizes, np.median(sq, 0))[0]`` bitwise, which pins the
    statistic as the fit of the column medians.
    """
    from lpcstudy.analysis import _fit_seed_law, h1a_library_scaling

    rng = np.random.default_rng(11002)
    sq = _seed_sq(rng, 300, floor_index=1)
    cells = _fake_cells({0.01: sq}, _gamma_local_dim(rng, 300, D_TRUE))
    out = h1a_library_scaling(cells, _config())
    fitted = out["by_noise"]["0.01"]["fitted_inverse_dim"]
    sq_cells = np.column_stack([cells[(0.01, int(n))].splits["test"].moments.analog_seed ** 2
                                for n in SIZES])
    assert fitted == 0.5 * _fit_seed_law(SIZES, np.median(sq_cells, axis=0))[0]
    assert abs(fitted * D_TRUE - 1.0) <= 0.05


def test_h1a_ratio_is_the_hand_value_and_the_interval_is_the_joint_bootstrap() -> None:
    """``h1a_ratio`` is median fit over mean reference on the same rows; the CI is one joint draw.

    Reference: hand computation. (i) On 80 arbitrary rows with repeats of 60 states the ratio
    equals ``0.5 * fit(medians) / mean(inverse_dim)`` with the medians formed by sorting and the
    mean by a sum, relative 1e-12 (a median is an order statistic or the mean of two, exact;
    the fit is the same deterministic function; one division and one sum, a few ulp).
    (ii) End to end, ``ratio_ci`` equals bitwise the percentile interval that
    ``block_bootstrap_counted`` gives for the closure ``idx -> h1a_ratio(sq, inv, sizes, idx)``
    seeded with ``make_rng(config.seed, system, "bootstrap", "H1a", "0.01")``: one index draw
    feeds the numerator and the denominator (a mutant with separate draws, or another label,
    changes the interval), and ``ci_inverse_dim`` equals the interval of the half fit alone with
    the same seed (same indices). ``n_failed_resamples`` equals the counted failures. Exact.
    """
    from lpcstudy.analysis import _fit_seed_law, h1a_library_scaling, h1a_ratio
    from lpcstudy.oracle import inverse_dimension

    rng = np.random.default_rng(11003)
    small = _seed_sq(rng, 60, floor_index=1, sigma=0.3)
    inv_small = 1.0 / _gamma_local_dim(rng, 60, D_TRUE) * 18.0 / 19.0
    rows = rng.integers(0, 60, size=80)
    assert len(np.unique(rows)) < 80
    assert h1a_ratio(small, inv_small, SIZES, rows) == pytest.approx(
        _hand_ratio(small, inv_small, rows), rel=1e-12, abs=0.0)

    sq = _seed_sq(rng, 300, floor_index=1)
    local_dim = _gamma_local_dim(rng, 300, D_TRUE)
    config = _config()
    out = h1a_library_scaling(_fake_cells({0.01: sq}, local_dim), config)["by_noise"]["0.01"]
    sq_cells = np.column_stack(
        [np.sqrt(sq[:, j]) ** 2 for j in range(len(SIZES))])  # what the cells hold, squared again
    inverse = inverse_dimension(local_dim)
    label = (config.seed, "lorenz63", "bootstrap", "H1a", "0.01")
    joint = block_bootstrap_counted(lambda idx: h1a_ratio(sq_cells, inverse, SIZES, idx), 300,
                                    config.bootstrap_resamples, config.bootstrap_block,
                                    make_rng(*label), 0.95)
    assert out["ratio_ci"] == [joint.lower, joint.upper]
    assert out["n_failed_resamples"] == joint.n_failed and out["ratio"] == joint.estimate
    marginal = block_bootstrap_counted(
        lambda idx: 0.5 * _fit_seed_law(SIZES, np.median(sq_cells[idx], axis=0))[0], 300,
        config.bootstrap_resamples, config.bootstrap_block, make_rng(*label), 0.95)
    assert out["ci_inverse_dim"] == [marginal.lower, marginal.upper]


def test_h1a_ratio_is_nan_when_a_median_is_not_positive_or_the_fit_raises(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """A resample that cannot be fitted is NaN (a counted failure), never an exception (A3).

    Reference: the contract of the applied-mathematician (WU-0002.4-5 log, Job 1 item 5 (iv)).
    A column median that is zero, negative or non-finite gives NaN before the fit is tried (the
    fit is replaced by one that fails the test if called); a fit that raises ``ValueError``
    (``curve_fit`` does for non-finite residuals; ``_fit_seed_law`` catches only
    ``RuntimeError``) also gives NaN; a fit that returns NaN gives NaN. Exact.
    """
    from lpcstudy import analysis

    rng = np.random.default_rng(11004)
    sq = _seed_sq(rng, 40, floor_index=1)
    inv = np.full(40, 0.5)
    rows = np.arange(40)

    def must_not_run(sizes: np.ndarray, medians: np.ndarray) -> tuple[float, float]:
        raise AssertionError("the fit must not be tried on a non-positive median")

    monkeypatch.setattr(analysis, "_fit_seed_law", must_not_run)
    for bad in (0.0, -1.0, np.nan, np.inf):
        broken = sq.copy()
        broken[:, 2] = bad
        assert np.isnan(analysis.h1a_ratio(broken, inv, SIZES, rows))

    def raises(sizes: np.ndarray, medians: np.ndarray) -> tuple[float, float]:
        raise ValueError("Residuals are not finite in the initial point.")

    monkeypatch.setattr(analysis, "_fit_seed_law", raises)
    assert np.isnan(analysis.h1a_ratio(sq, inv, SIZES, rows))
    monkeypatch.setattr(analysis, "_fit_seed_law", lambda sizes, medians: (np.nan, np.nan))
    assert np.isnan(analysis.h1a_ratio(sq, inv, SIZES, rows))
    monkeypatch.undo()
    assert np.isfinite(analysis.h1a_ratio(sq, inv, SIZES, rows))
    assert np.isnan(analysis.h1a_ratio(sq, np.zeros(40), SIZES, rows))  # reference 0: no ratio


def test_h1a_verdicts_on_known_truth_at_both_noise_levels() -> None:
    """Pass when the ratio is about 1, fail when the reference is wrong, at both rho (T6, D-19).

    Reference: known truth. Fake cells follow the T1 design (d = 2.2, 300 states) at rho = 0.01
    and 0.02; the reference ``S / (k - 1)`` is drawn from the exact Gamma law, with dimension
    2.2 (true ratio 1) or 1.2 (true ratio 0.545). Fixed ``default_rng(11005)``.

    * Ratio 1: both rho pass, overall pass. In the applied-mathematician's simulation (B = 500,
      40 replications) the interval is 0.971 +- 0.016 to 1.031 +- 0.018, i.e. 12 sd inside
      [0.75, 1.25] on both sides; B = 200 here widens the endpoint noise slightly, not the
      margin.
    * Reference at d = 1.2: the upper bound is 0.562 +- 0.010, 19 sd below 0.75: both fail,
      overall fail.
    * Floors *decreasing* in rho (power term at the third size for rho = 0.02, at the second
      for 0.01), ratio 1: still pass. The v1 criterion "floor increasing in rho" is removed
      (D-19); the floors are reported only.
    Exact verdicts, band [0.75, 1.25], level 0.95.
    """
    from lpcstudy.analysis import h1a_library_scaling

    rng = np.random.default_rng(11005)
    config = _config()
    same = {0.01: _seed_sq(rng, 300, 1), 0.02: _seed_sq(rng, 300, 1)}
    good = h1a_library_scaling(_fake_cells(same, _gamma_local_dim(rng, 300, D_TRUE)), config)
    assert [good["by_noise"][k]["verdict"] for k in ("0.01", "0.02")] == ["pass", "pass"]
    assert good["verdict"] == "pass" and good["pass"] is True and good["reason"] is None
    assert good["band"] == [0.75, 1.25] and good["level"] == 0.95

    bad = h1a_library_scaling(_fake_cells(same, _gamma_local_dim(rng, 300, 1.2)), config)
    assert [bad["by_noise"][k]["verdict"] for k in ("0.01", "0.02")] == ["fail", "fail"]
    assert bad["verdict"] == "fail" and bad["pass"] is False

    decreasing = {0.01: _seed_sq(rng, 300, 1), 0.02: _seed_sq(rng, 300, 2)}
    out = h1a_library_scaling(_fake_cells(decreasing, _gamma_local_dim(rng, 300, D_TRUE)), config)
    assert out["by_noise"]["0.02"]["floor_rms"] < out["by_noise"]["0.01"]["floor_rms"]
    assert out["verdict"] == "pass" and out["pass"] is True
    assert not {"floor_increases", "threshold", "local_dimension_median",
                "relative_error_vs_local_dim"} & set(out)


def test_h1a_minimum_states_and_uncomputable_fit_are_inconclusive_with_reasons(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """Fewer than 50 states, or a fit that cannot be computed, give inconclusive (A3, T6).

    Reference: DEC-0008 A3 and the guard order of ``criterion_verdict``. (i) 49 states: both
    rho and the whole are inconclusive with the exact reason "n_states < 50"; with 50 states the
    reason is not that (the verdict itself is not asserted: 50 states give a wide interval).
    (ii) ``_fit_seed_law`` replaced by a function returning NaN: the point estimate is not
    computable, every one of the B resamples fails and is counted in ``n_failed_resamples``,
    and the reason is "not computable" (the guard before the interval). Exact.
    """
    from lpcstudy import analysis

    rng = np.random.default_rng(11006)
    config = _config(100)
    for n_states, short in ((49, True), (50, False)):
        cells = _fake_cells({0.01: _seed_sq(rng, n_states, 1), 0.02: _seed_sq(rng, n_states, 1)},
                            _gamma_local_dim(rng, n_states, D_TRUE))
        out = analysis.h1a_library_scaling(cells, config)
        assert out["n_states"] == n_states and out["n_excluded_nonfinite"] == 0
        reasons = [out["by_noise"][k]["reason"] for k in ("0.01", "0.02")]
        if short:
            assert reasons == ["n_states < 50"] * 2 and out["verdict"] == "inconclusive"
            assert out["reason"] == "rho=0.01: n_states < 50; rho=0.02: n_states < 50"
            assert out["pass"] is False
        else:
            assert "n_states < 50" not in reasons

    cells = _fake_cells({0.01: _seed_sq(rng, 300, 1)}, _gamma_local_dim(rng, 300, D_TRUE))
    monkeypatch.setattr(analysis, "_fit_seed_law", lambda sizes, medians: (np.nan, np.nan))
    out = analysis.h1a_library_scaling(cells, config)
    part = out["by_noise"]["0.01"]
    assert part["verdict"] == "inconclusive" and part["reason"] == "not computable"
    assert part["n_failed_resamples"] == config.bootstrap_resamples
    assert np.isnan(part["fitted_inverse_dim"]) and np.isnan(part["ratio"])
    assert out["verdict"] == "inconclusive" and out["pass"] is False


def test_h1a_excludes_and_counts_states_with_nonfinite_inputs_once_for_both_rho() -> None:
    """A state with a non-finite seed or reference is excluded from every rho and counted (A3).

    Reference: the applied-mathematician's conditions (WU-0002.4-5 log, Job 1 item 5 (i)).
    State 7 has a NaN seed error at rho = 0.02 only, state 11 a NaN local dimension in every
    cell. Both are removed from the numerator and the denominator at both rho (one state set),
    in time order; ``n_states`` is 298 and ``n_excluded_nonfinite`` is 2. The ``ratio_ci`` at
    rho = 0.01 (where state 7 is finite) equals bitwise the interval of the ``h1a_ratio`` closure
    over the arrays with those two rows deleted, which fails if state 7 is kept at rho = 0.01,
    and ``inverse_dim_reference`` equals the mean of the kept ``S / (k - 1)``. Exact.
    """
    from lpcstudy.analysis import h1a_library_scaling, h1a_ratio
    from lpcstudy.oracle import inverse_dimension

    rng = np.random.default_rng(11007)
    sq = {0.01: _seed_sq(rng, 300, 1), 0.02: _seed_sq(rng, 300, 1)}
    local_dim = _gamma_local_dim(rng, 300, D_TRUE)
    local_dim[11] = np.nan
    sq[0.02][7, 3] = np.nan
    config = _config()
    out = h1a_library_scaling(_fake_cells(sq, local_dim), config)
    assert out["n_states"] == 298 and out["n_excluded_nonfinite"] == 2
    keep = np.delete(np.arange(300), [7, 11])
    inverse = inverse_dimension(local_dim)[keep]
    assert out["inverse_dim_reference"] == inverse.mean()
    kept_sq = np.column_stack([np.sqrt(sq[0.01][keep, j]) ** 2 for j in range(len(SIZES))])
    joint = block_bootstrap_counted(
        lambda idx: h1a_ratio(kept_sq, inverse, SIZES, idx), 298, config.bootstrap_resamples,
        config.bootstrap_block, make_rng(config.seed, "lorenz63", "bootstrap", "H1a", "0.01"),
        0.95)
    assert out["by_noise"]["0.01"]["ratio_ci"] == [joint.lower, joint.upper]


def test_h1a_rejects_cells_that_do_not_share_the_states_and_has_the_documented_keys() -> None:
    """Misaligned ``local_dim`` raises; the result has exactly the documented keys (T6, plan).

    Reference: the plan's result-key list (WU-0002.4-5). One cell with a different local
    dimension (a different state set) raises ``ValueError`` rather than pairing the numerator
    and the denominator of the ratio across states. The key sets of the whole and of a rho are
    compared exactly with the plan's; ``reference_estimator`` is text; ``pass`` equals
    ``verdict == "pass"``.
    """
    from lpcstudy.analysis import h1a_library_scaling

    rng = np.random.default_rng(11008)
    local_dim = _gamma_local_dim(rng, 80, D_TRUE)
    cells = _fake_cells({0.01: _seed_sq(rng, 80, 1)}, local_dim)
    out = h1a_library_scaling(cells, _config(50))
    assert set(out) == {"inverse_dim_reference", "reference_estimator", "n_states",
                        "n_excluded_nonfinite", "band", "level", "verdict", "reason", "pass",
                        "by_noise"}
    assert set(out["by_noise"]["0.01"]) == {
        "fitted_inverse_dim", "ci_inverse_dim", "ratio", "ratio_ci", "n_failed_resamples",
        "verdict", "reason", "floor_rms", "median_seed_by_n_lib"}
    assert isinstance(out["reference_estimator"], str) and out["pass"] == (out["verdict"] == "pass")
    assert list(out["by_noise"]["0.01"]["median_seed_by_n_lib"]) == [str(int(n)) for n in SIZES]
    cells[(0.01, 3162)].oracles["test"].local_dim = local_dim[::-1].copy()
    with pytest.raises(ValueError, match="local_dim"):
        h1a_library_scaling(cells, _config(50))


# ----------------------------------------------------------------------------------- H1b
def _fake_h1b_cell(rng: np.random.Generator, n_states: int, slope_cp: float, slope_plp: float,
                   log_noise: float = 0.0) -> SimpleNamespace:
    """A core cell whose H1b regressions have the stated slopes (power laws, optional noise).

    The CP regression is ``0.5 ln(sq_cp - noise^2/n_analogs)`` on ``ln(g seed_cp / sqrt(m))``
    and the PLP one is ``0.5 ln(sq_plp)`` on ``ln(g seed_plp / sqrt(m))``, exactly the
    construction of ``h1b_seed_amplifier``; the squared errors are built from the stated slope
    and intercept 0.3 with additive Gaussian noise ``log_noise`` on the log scale (0 gives exact
    power laws, hence exact slopes).
    """
    dim, noise, n_analogs, horizon = 3, 0.01, 20, 30
    gain = np.exp(rng.normal(0.0, 0.5, n_states))
    seed_cp = np.exp(rng.normal(-2.0, 0.4, n_states))
    seed_plp = np.exp(rng.normal(-2.0, 0.4, n_states))
    copied = noise**2 / n_analogs

    def squared(slope: float, seed: np.ndarray) -> np.ndarray:
        x = np.log(gain * seed / np.sqrt(dim))
        return np.exp(2.0 * (slope * x + 0.3 + rng.normal(0.0, log_noise, n_states)))

    gains = np.tile(gain[:, None], (1, horizon))
    moments = SimpleNamespace(
        analog_seed=seed_cp, est_seed=seed_plp, at=lambda h: 0,
        sq_cp=(copied + squared(slope_cp, seed_cp))[:, None],
        sq_plp=squared(slope_plp, seed_plp)[:, None])
    return SimpleNamespace(
        noise=noise, setup=SimpleNamespace(n_analogs=n_analogs),
        ctx=SimpleNamespace(spec=SimpleNamespace(dim=dim)),
        splits={"test": SimpleNamespace(moments=moments)},
        oracles={"test": SimpleNamespace(gains=gains)})


def test_h1b_verdict_uses_the_plp_slope_only() -> None:
    """CP slope 1.6 with PLP slope 1.0 passes; swapped fails; CP has no verdict (T8).

    Reference: the ROADMAP row of WU-0002.4 and DEC-0008 A1. The cells are noise-free power
    laws, so every resample of the regression has the exact slope (the 100 distinct x values
    never make a block resample constant), the interval is a point, and the PLP interval lies
    inside [0.8, 1.2] (pass) or entirely above it (fail). The CP and PLP slopes agree with 1.6
    and 1.0 to 1e-12 (OLS on 100 values of order 10 after a ``log(sq - floor)`` round trip:
    relative error a few 1e-16 times the condition number of the design, below 1e-14; 1e-12
    leaves two orders). The CP entry has only ``slope``, ``ci`` and the exclusion count; the
    PLP entry adds ``n_failed_resamples``; the top-level keys are the plan's plus the
    exclusion count (fix R2). Exact verdicts.
    """
    from lpcstudy.analysis import h1b_seed_amplifier

    config = _config(100)
    ok = h1b_seed_amplifier(_fake_h1b_cell(np.random.default_rng(21001), 100, 1.6, 1.0), config)
    assert ok["CP"]["slope"] == pytest.approx(1.6, abs=1e-12, rel=0)
    assert ok["PLP"]["slope"] == pytest.approx(1.0, abs=1e-12, rel=0)
    assert ok["verdict"] == "pass" and ok["pass"] is True and ok["reason"] is None
    assert set(ok["CP"]) == {"slope", "ci", "n_excluded_nonfinite"}
    assert set(ok["PLP"]) == {"slope", "ci", "n_failed_resamples", "n_excluded_nonfinite"} and \
        ok["PLP"]["n_failed_resamples"] == 0
    assert set(ok) == {"CP", "PLP", "threshold", "n_states", "n_excluded_nonfinite", "verdict",
                       "reason", "pass"}
    assert ok["n_excluded_nonfinite"] == 0
    assert ok["threshold"] == [0.8, 1.2] and ok["n_states"] == 100

    swapped = h1b_seed_amplifier(_fake_h1b_cell(np.random.default_rng(21002), 100, 1.0, 1.6),
                                 config)
    assert swapped["PLP"]["slope"] == pytest.approx(1.6, abs=1e-12, rel=0)
    assert swapped["verdict"] == "fail" and swapped["pass"] is False


def test_regression_h1b_intervals_equal_the_old_block_bootstrap_and_edge_cases() -> None:
    """Regression guard: slopes and intervals of both forecasters are those of ``block_bootstrap``.

    This compares with the old function at the seed ``config.seed`` (the pre-existing
    ``_boot(..., salt=0)`` integer seed, DEC-0012 keeps it), so it is a guard against moving the
    bootstrap, not evidence of correctness (T8 above is). On noisy data (log-scale noise 0.1) the
    CP interval equals ``block_bootstrap`` and the PLP interval equals it too, because no
    resample fails and ``block_bootstrap_counted`` is bitwise equal then. Edge cases (exact): a
    NaN gain state is excluded and counted (fix R2): the PLP slope and interval equal
    ``block_bootstrap`` on the arrays with that state deleted; 50 remaining states are enough
    and 49 give "n_states < 50"; a constant regressor gives a 0/0 slope, "not computable", and
    every resample counted failed; 40 states give "n_states < 50".
    """
    from lpcstudy.analysis import h1b_seed_amplifier
    from lpcstudy.statistics import block_bootstrap, ols_slope

    config = _config(100)
    cell = _fake_h1b_cell(np.random.default_rng(21003), 100, 1.1, 0.9, log_noise=0.1)
    out = h1b_seed_amplifier(cell, config)
    m, gain = cell.splits["test"].moments, cell.oracles["test"].gains[:, 29]
    copied = cell.noise**2 / cell.setup.n_analogs
    for name, seed, sq, floor in (("CP", m.analog_seed, m.sq_cp[:, 0], copied),
                                  ("PLP", m.est_seed, m.sq_plp[:, 0], 0.0)):
        x = np.log(gain * seed / np.sqrt(cell.ctx.spec.dim))
        y = 0.5 * np.log(np.maximum(sq - floor, 1e-12))
        old = block_bootstrap(lambda idx: ols_slope(x[idx], y[idx]), 100,
                              config.bootstrap_resamples, config.bootstrap_block, config.seed)
        assert (out[name]["slope"], *out[name]["ci"]) == old
    assert out["PLP"]["n_failed_resamples"] == 0

    # A non-finite gain removes that state from both regressions and counts it (R2, plan (g)).
    broken = _fake_h1b_cell(np.random.default_rng(21004), 100, 1.0, 1.0, log_noise=0.1)
    clean = _fake_h1b_cell(np.random.default_rng(21004), 100, 1.0, 1.0, log_noise=0.1)
    broken.oracles["test"].gains[3, :] = np.nan
    nan_out = h1b_seed_amplifier(broken, config)
    assert nan_out["n_excluded_nonfinite"] == 1 and nan_out["n_states"] == 99
    assert nan_out["CP"]["n_excluded_nonfinite"] == 1
    mp, gain_p = clean.splits["test"].moments, clean.oracles["test"].gains[:, 29]
    keep = np.delete(np.arange(100), 3)
    xp = np.log(gain_p * mp.est_seed / np.sqrt(3))[keep]
    yp = 0.5 * np.log(mp.sq_plp[:, 0])[keep]
    kept = block_bootstrap(lambda idx: ols_slope(xp[idx], yp[idx]), 99,
                           config.bootstrap_resamples, config.bootstrap_block, config.seed)
    assert (nan_out["PLP"]["slope"], *nan_out["PLP"]["ci"]) == kept
    assert nan_out["PLP"]["n_failed_resamples"] == 0 and nan_out["reason"] != "not computable"

    # Fifty remaining states are enough, 49 are not (MIN_STATES applies after exclusion).
    for n_bad, reason in ((50, None), (51, "n_states < 50")):
        few = _fake_h1b_cell(np.random.default_rng(21006), 100, 1.0, 1.0)
        few.oracles["test"].gains[:n_bad, :] = np.nan
        out = h1b_seed_amplifier(few, config)
        assert out["n_states"] == 100 - n_bad and out["n_excluded_nonfinite"] == n_bad
        assert (out["reason"] == "n_states < 50") == (reason is not None)

    # Constant regressor (x = 0 exactly): the slope is 0/0, not computable; every resample
    # fails and is counted.
    flat = _fake_h1b_cell(np.random.default_rng(21007), 100, 1.0, 1.0)
    flat.splits["test"].moments.est_seed = np.full(100, np.sqrt(3.0))  # x = ln(1) = 0 exactly
    flat.oracles["test"].gains[:, :] = 1.0
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        flat_out = h1b_seed_amplifier(flat, config)
    assert flat_out["verdict"] == "inconclusive" and flat_out["reason"] == "not computable"
    assert flat_out["PLP"]["n_failed_resamples"] == config.bootstrap_resamples
    assert flat_out["pass"] is False

    short = h1b_seed_amplifier(_fake_h1b_cell(np.random.default_rng(21005), 40, 1.0, 1.0), config)
    assert short["verdict"] == "inconclusive" and short["reason"] == "n_states < 50"


# ----------------------------------------------------------------------------------- H1d
TESTED_ROWS = ("analog_seed", "estimation_seed", "growth")


def _pair(rng: np.random.Generator, n: int, spearman_target: float
          ) -> tuple[np.ndarray, np.ndarray]:
    """Bivariate normal pair with Spearman correlation about ``spearman_target``.

    For a bivariate normal with Pearson ``r``, ``rho_s = (6 / pi) arcsin(r / 2)``, so
    ``r = 2 sin(pi rho_s / 6)`` (0.9545 for 0.95, 0.2091 for 0.2, 0.8 for ``rho_s = 0.7861``).
    """
    r = 2.0 * np.sin(np.pi * spearman_target / 6.0)
    z = rng.standard_normal((n, 2))
    return z[:, 0], r * z[:, 0] + np.sqrt(1.0 - r**2) * z[:, 1]


def _pairs(rng: np.random.Generator, n: int, targets: tuple[float, float, float, float]) -> dict:
    """The four H1d pairs (three tested rows and ``nhat``) with the given Spearman targets."""
    return {name: _pair(rng, n, t) for name, t in zip((*TESTED_ROWS, "nhat"), targets)}


def test_h1d_spearman_equals_scipy_and_the_closed_form_on_500_points() -> None:
    """Each row's Spearman is ``scipy.stats.spearmanr`` and ``1 - 6 sum d^2 / (n (n^2 - 1))`` (T9).

    Reference: scipy for the point estimate (ROADMAP: 10^-12 on 500 bivariate-normal points,
    rho = 0.8, fixed seed), plus the closed form on the integer ranks of tie-free data (the code's
    ``spearman`` *is* scipy's, so the closed form is the independent check; applied-mathematician,
    WU-0002.4-5 log, Job 1 item 6). 500 draws, ``default_rng(21011)``, four independent pairs.

    Tolerance: absolute 1e-12. The closed form is an exact integer sum (Sum d^2 < 5e7, exact in
    float64) and three operations; scipy's value is the Pearson correlation of the ranks,
    a few hundred operations on numbers of order 10^2 to 10^5 with relative error a few 1e-16
    times 500; 1e-12 leaves about three orders.
    """
    from scipy.stats import rankdata, spearmanr

    from lpcstudy.analysis import h1d_correlations

    pairs = _pairs(np.random.default_rng(21011), 500, (0.7861,) * 4)
    out = h1d_correlations(pairs, "lorenz63", _config(50))
    for name, (a, b) in pairs.items():
        got = out["rows"][name]["spearman"]
        d = rankdata(a) - rankdata(b)
        closed_form = 1.0 - 6.0 * np.sum(d**2) / (500 * (500**2 - 1))
        assert got == pytest.approx(spearmanr(a, b).statistic, abs=1e-12, rel=0)
        assert got == pytest.approx(closed_form, abs=1e-12, rel=0)


def test_h1d_interval_is_the_seeded_block_bootstrap_at_the_study_settings() -> None:
    """The interval contains the point and equals ``block_bootstrap_counted`` with the label (T10).

    Reference: ``StudyConfig()`` has 2000 resamples and blocks of 5 (v3 section 7), and the
    interval of each row equals bitwise the percentile interval of
    ``block_bootstrap_counted(idx -> spearman(a[idx], b[idx]))`` with
    ``make_rng(config.seed, system, "bootstrap", "H1d", name)`` at level 0.95. That pins the
    seed label, the resample count and the block; a different label or count changes the
    interval. 100 states (the cost is 2 x 4 x 2000 rank correlations), ``default_rng(21012)``.
    The interval contains the point estimate (the percentile interval of a smooth statistic
    does, with the observed margin far from the edge). Exact.
    """
    from lpcstudy.analysis import h1d_correlations
    from lpcstudy.statistics import spearman

    config = StudyConfig()
    assert config.bootstrap_resamples == 2000 and config.bootstrap_block == 5
    pairs = _pairs(np.random.default_rng(21012), 100, (0.8, 0.8, 0.8, 0.5))
    out = h1d_correlations(pairs, "rossler", config)
    assert out["level"] == 0.95 and out["threshold"] == 0.7
    for name, (a, b) in pairs.items():
        ref = block_bootstrap_counted(
            lambda idx: spearman(a[idx], b[idx]), 100, 2000, 5,
            make_rng(config.seed, "rossler", "bootstrap", "H1d", name), 0.95)
        row = out["rows"][name]
        assert row["interval"] == [ref.lower, ref.upper] and row["spearman"] == ref.estimate
        assert row["n_failed_resamples"] == ref.n_failed == 0
        assert row["interval"][0] <= row["spearman"] <= row["interval"][1]


def test_h1d_nhat_has_no_verdict_and_does_not_move_the_overall_verdict() -> None:
    """``nhat`` is reported (Spearman and interval) without a verdict; the three rows decide (T11).

    Reference: v3 sections 2 and 8 and M2 H1e: N-hat is reported, not tested. Synthetic pairs
    with n = 500 and Spearman targets 0.95 (three tested rows) or 0.2: on the Fisher-z scale
    (SE = sqrt((1 + rho^2/2) / (n - 3)), applied-mathematician) the lower bound for 0.95 is
    16 sd above 0.7 and the upper bound for 0.2 is 15 sd below it, so verdicts are pass and fail
    with a margin that no bootstrap noise at 200 resamples can cross. Flipping the N-hat pair's
    correlation from +0.9 to -0.9 leaves the verdict, ``pass`` and the three tested rows
    unchanged (identical dicts), while ``nhat`` has ``spearman`` and ``interval`` and neither
    ``pass`` nor ``verdict``. One tested row at 0.2 gives fail overall.
    """
    from lpcstudy.analysis import h1d_correlations

    config = _config(200)
    rng = np.random.default_rng(21013)
    pairs = _pairs(rng, 500, (0.95, 0.95, 0.95, 0.9))
    flipped = dict(pairs, nhat=(pairs["nhat"][0], -pairs["nhat"][1]))
    out, out_flipped = (h1d_correlations(p, "chua", config) for p in (pairs, flipped))
    assert out["verdict"] == out_flipped["verdict"] == "pass"
    assert out["pass"] is out_flipped["pass"] is True and out["reason"] is None
    assert [out["rows"][name]["verdict"] for name in TESTED_ROWS] == ["pass"] * 3
    assert {name: out["rows"][name] for name in TESTED_ROWS} == \
        {name: out_flipped["rows"][name] for name in TESTED_ROWS}
    nhat, nhat_flipped = out["rows"]["nhat"], out_flipped["rows"]["nhat"]
    assert {"spearman", "interval"} <= set(nhat) and not {"pass", "verdict"} & set(nhat)
    assert nhat["spearman"] > 0.8 and nhat_flipped["spearman"] < -0.8

    low = h1d_correlations(_pairs(rng, 500, (0.95, 0.95, 0.2, 0.95)), "chua", config)
    assert low["rows"]["growth"]["verdict"] == "fail"
    assert low["rows"]["analog_seed"]["verdict"] == "pass"
    assert low["verdict"] == "fail" and low["pass"] is False


def test_h1d_exclusions_minimum_states_and_uncomputable_rows() -> None:
    """Non-finite pairs are excluded per row and counted; short or constant rows are inconclusive.

    Reference: DEC-0008 A3 and the applied-mathematician's condition (ii) (WU-0002.4-5 log, Job 1
    item 5): exclusion is per row, so a reported-only ``nhat`` with NaNs does not shrink the
    tested rows. Exact counts and reasons: (i) two NaN in ``nhat`` only: the tested rows keep all
    120 states, ``nhat`` has 118 and 2 excluded, top-level ``n_states`` 120 and
    ``n_excluded_nonfinite`` 0; (ii) one NaN in a tested row: that row has 119 states, the
    top level reports the smallest (119) and the largest exclusion (1); (iii) 49 states give
    "n_states < 50" for every tested row and the whole; (iv) a constant proxy makes the
    correlation undefined: the row is "inconclusive" with reason "not computable" and
    every resample is counted failed. (The scipy constant-input warning is expected.)
    """
    import warnings

    from lpcstudy.analysis import h1d_correlations

    config = _config(100)
    rng = np.random.default_rng(21014)
    pairs = _pairs(rng, 120, (0.9, 0.9, 0.9, 0.9))
    pairs["nhat"][0][[3, 4]] = np.nan
    out = h1d_correlations(pairs, "lorenz63", config)
    assert out["rows"]["nhat"]["n_states"] == 118
    assert out["rows"]["nhat"]["n_excluded_nonfinite"] == 2
    assert out["rows"]["analog_seed"]["n_states"] == 120
    assert out["n_states"] == 120 and out["n_excluded_nonfinite"] == 0

    pairs["growth"][1][9] = np.inf
    out = h1d_correlations(pairs, "lorenz63", config)
    assert out["rows"]["growth"]["n_states"] == 119 and out["n_states"] == 119
    assert out["n_excluded_nonfinite"] == 1 and out["rows"]["growth"]["n_excluded_nonfinite"] == 1

    short = h1d_correlations(_pairs(rng, 49, (0.95,) * 4), "lorenz63", config)
    assert [short["rows"][n]["reason"] for n in TESTED_ROWS] == ["n_states < 50"] * 3
    assert short["verdict"] == "inconclusive" and short["pass"] is False
    assert short["reason"] == ("analog_seed: n_states < 50; estimation_seed: n_states < 50; "
                               "growth: n_states < 50")

    flat = _pairs(rng, 120, (0.9,) * 4)
    flat["estimation_seed"] = (np.ones(120), flat["estimation_seed"][1])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        out = h1d_correlations(flat, "lorenz63", config)
    row = out["rows"]["estimation_seed"]
    assert row["verdict"] == "inconclusive" and row["reason"] == "not computable"
    assert row["n_failed_resamples"] == config.bootstrap_resamples
    assert out["verdict"] == "inconclusive" and out["reason"] == "estimation_seed: not computable"


def test_h1d_proxies_pairs_each_proxy_with_its_oracle_on_the_first_draw() -> None:
    """``h1d_proxies`` maps the cell onto the four pairs and keeps the Cramer-Rao comparison.

    Reference: the definitions of v3 H1d (and the pre-existing code): (eps-hat, eps_s),
    (delta-hat, delta), (Lambda-hat, Lambda-bar), (N-hat, N), all on the first evaluation draw
    (column 0; column 1 is deliberately different noise), and the reported Spearman of the
    estimation seed with ``rho nu``. Each value is compared with ``scipy.stats.spearmanr`` of
    the pair built in the test, at 1e-12 absolute (ranks of 80 distinct values; round-off
    below 1e-14). Different Spearman targets per pair (0.9, 0.7, 0.5, 0.3, 0.1) make a swapped
    pair visible. The result carries ``estimation_seed_vs_cramer_rao`` with no interval.
    """
    from scipy.stats import spearmanr

    from lpcstudy.analysis import h1d_proxies

    rng = np.random.default_rng(21015)
    n, noise = 80, 0.02
    eps_hat, analog = _pair(rng, n, 0.9)
    delta_hat, est = _pair(rng, n, 0.7)
    growth_hat, growth = _pair(rng, n, 0.5)
    nhat, noise_sens = _pair(rng, n, 0.3)
    _, nu_scaled = _pair(rng, n, 0.1)
    nu = np.exp(nu_scaled) / noise
    other = rng.standard_normal((n, 1))  # draw 1: must not be used
    ev = SimpleNamespace(growth_proxy=np.column_stack([growth_hat, other]),
                         noise_sens=np.column_stack([nhat, other]))
    rules = SimpleNamespace(proxies=SimpleNamespace(
        seeds=lambda e, rho: (np.column_stack([eps_hat, other]),
                              np.column_stack([delta_hat, other]))))
    cell = SimpleNamespace(
        system="lorenz63", noise=noise,
        splits={"test": SimpleNamespace(evals=ev, moments=SimpleNamespace(
            analog_seed=analog, est_seed=est, noise_sens=noise_sens))},
        oracles={"test": SimpleNamespace(growth=growth, nu=nu)})
    out = h1d_proxies(cell, rules, _config(50))
    expected = {"analog_seed": (eps_hat, analog), "estimation_seed": (delta_hat, est),
                "growth": (growth_hat, growth), "nhat": (nhat, noise_sens)}
    for name, (a, b) in expected.items():
        assert out["rows"][name]["spearman"] == pytest.approx(spearmanr(a, b).statistic,
                                                              abs=1e-12, rel=0)
    assert out["estimation_seed_vs_cramer_rao"] == pytest.approx(
        spearmanr(est, noise * nu).statistic, abs=1e-12, rel=0)
    assert set(out) == {"rows", "estimation_seed_vs_cramer_rao", "threshold", "level",
                        "n_states", "n_excluded_nonfinite", "verdict", "reason", "pass"}
    assert set(out["rows"]["growth"]) == {"spearman", "interval", "n_failed_resamples",
                                          "n_states", "n_excluded_nonfinite", "verdict", "reason"}
