"""Tests for lpcstudy.analysis: per-state Spearman trend."""

from __future__ import annotations

import numpy as np


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
