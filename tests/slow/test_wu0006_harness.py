"""Smoke and self-checks of the WU-0006 harness (WU-0006.1).

Slow tier (a few seconds each, about two minutes in all, mostly worker start-up and the 10^7-draw
truth checks): the checks of the harness itself that must hold before its numbers are read.

* **H1** the AR(1) generator has the lag-1 autocorrelation and variance it claims (10^6 draws);
* **H3** the truths the coverage cases rely on (C2, C4, C5, C6, C7) are realized by the generators
  (10^7 draws), and the log-rank and delta-R2 generators have the designed marginals;
* **H2** a replication's result does not depend on the number of workers or on how the replications
  are split into tasks (1 worker, 2 workers, in process);
* the integer bounds follow from the formulas z = 3, SE = sqrt(p (1 - p) / R) of the plan;
* the independent verdict rule agrees with ``criterion_verdict`` at the band edges, including ties
  (which a continuous simulation never produces, so A4 alone cannot check the open and closed edges);
* the evaluation functions apply the registered bounds and ranges exactly (boundary counts), and the
  Option C/K switch ``ASSERT_ROADMAP_BOUNDS`` works in both modes;
* every design runs end to end on the pool at a tiny R, and the exact checks (identity with the
  production function, A4, A5, the C7 zero column, L3, the bitwise refit) hold there.

Tolerances. Each H1 and H3 check is a 3-standard-error z-test with the standard error stated at the
assertion; on fixed seeds the outcome is deterministic. There are 31 such z-tests (AR(1) 6, bivariate 12,
truths 5, log-rank 4, delta-R2 4). About 25 have a false-alarm probability of 0.27% for a correct
generator and 6 (the phi = 0.3 bivariate lag-1 checks, whose estimator's bias is 0.46 SE) 0.58%, so the
chance that at least one of the 31 fails for a correct generator is about 10%. A failure would be a finding about the
generator, not a reason to move a seed or a bound.
"""

from __future__ import annotations

import json
import math
import os
import warnings

import numpy as np
import pytest
from lpcstudy.analysis import quadratic_controls
from lpcstudy.config import FULL
from lpcstudy.data import make_rng
from lpcstudy.statistics import criterion_verdict, partial_correlation, spearman

import wu0006_harness as wu
import wu0006_reference as ref


def rng_for(*labels: object) -> np.random.Generator:
    """Self-check stream: ``make_rng(6006, "wu0006", "selfcheck", ...)``."""
    return make_rng(wu.WU0006_SEED, "wu0006", "selfcheck", *labels)


@pytest.fixture(scope="module")
def pool():
    """One spawned pool of single-thread workers for the tiny end-to-end runs."""
    with wu.worker_pool() as shared:
        yield shared


# ------------------------------------------------------------------------------ bounds, tables
def test_integer_bounds_follow_the_plan_formulas() -> None:
    """The registered integer bounds are the counts of nominal -/+ 3 sqrt(p (1 - p) / R).

    Reference: the plan's formulas evaluated here (z = 3), taking the stricter of formula and ROADMAP
    rounding (applied-mathematician M1): A1 0.929324 (ROADMAP 0.929), A2 0.971188 (0.971),
    A3 0.039811 and 0.016957, L 0.016675 (0.0167), N1 and N3 0.920760 (0.921), N2 0.045946.
    The ROADMAP's rounded values give counts no stricter than the formula's (929, 971, 33, 461).
    """
    def lower(p: float, total: int) -> int:
        return math.ceil(round(total * (p - 3 * math.sqrt(p * (1 - p) / total)), 9))

    def upper(p: float, total: int) -> int:
        return math.floor(round(total * (p + 3 * math.sqrt(p * (1 - p) / total)), 9))

    def rounded_up(rate: float, total: int) -> int:  # the ROADMAP's rounded lower bound as a count
        return math.ceil(round(total * rate, 9))

    alpha = 0.05 / 3
    assert wu.A1_MIN == lower(0.95, 1000) >= rounded_up(0.929, 1000)
    assert wu.A2_MIN == lower(1 - alpha, 1000) >= rounded_up(0.971, 1000)
    assert wu.A3_MAX["95"] == upper(0.025, 1000)
    assert wu.A3_MAX["98.3"] == upper(alpha / 2, 1000)
    assert wu.L_MAX == upper(0.01, 2000) <= math.floor(round(2000 * 0.0167, 9))
    assert wu.N1_MIN == wu.N3_MIN == lower(0.95, 500) >= rounded_up(0.921, 500)
    assert wu.N2_MAX == upper(0.025, 500)
    assert (wu.R_COVERAGE, wu.R_LOGRANK, wu.R_DELTA) == (1000, 2000, 500)


def test_reference_tables_hold_the_70_ranges() -> None:
    """36 coverage + 28 A3 + 6 log-rank ranges, each containing its own reference rate."""
    n_ranges = 0
    for (case, phi), levels in ref.COVERAGE_REFERENCE.items():
        for name, (rate, _, _, (low, high)) in levels.items():
            assert low <= rate * 1000 <= high, (case, phi, name)
            n_ranges += 1
    for (case, phi), kinds in ref.A3_REFERENCE.items():
        assert case in ref.A3_LEVEL
        for kind, (rate, _, (low, high)) in kinds.items():
            assert low <= rate * 1000 <= high, (case, phi, kind)
            n_ranges += 1
    for (row, phi), entry in ref.LOGRANK_REFERENCE.items():
        for key in ("fwer", "pass"):
            if entry[key] is not None:
                rate, (low, high) = entry[key]
                assert low <= rate * 2000 <= high, (row, phi, key)
                n_ranges += 1
    assert n_ranges == 70


def test_design_is_the_study_procedure() -> None:
    """B = 2000, block 5, levels 95% and 1 - 0.05/3, delta-R2 sizes 3000 / 1000 (from FULL)."""
    wu.assert_design()
    assert (FULL.bootstrap_resamples, FULL.bootstrap_block) == (2000, 5)
    assert wu.WU0006_SEED == 6006


# --------------------------------------------------------------------------------- generators
@pytest.mark.parametrize("phi", [0.0, 0.3])
def test_ar1_has_the_stated_lag1_and_variance(phi: float) -> None:
    """H1: 10^6 draws; lag-1 autocorrelation within 3 sqrt((1 - phi^2)/N) of phi, variance within
    3 sqrt(2 (1 + phi^2) / ((1 - phi^2) N)) of 1, mean within 3 sqrt((1 + phi)/((1 - phi) N)) of 0.

    References: Bartlett's variance of the sample lag-1 autocorrelation of an AR(1) (checked by the
    review: empirical 0.00944 vs 0.00954 at phi = 0.3, N = 1e4) and the variance of the sample
    variance, 2 sum_k phi^(2|k|) / N.
    """
    n = 10**6
    x = wu.ar1(rng_for("ar1", f"{phi:g}"), n, phi)
    centred = x - x.mean()
    lag1 = float(np.sum(centred[1:] * centred[:-1]) / np.sum(centred**2))
    assert abs(lag1 - phi) < 3 * math.sqrt((1 - phi**2) / n)
    assert abs(float(centred.var()) - 1.0) < 3 * math.sqrt(2 * (1 + phi**2) / ((1 - phi**2) * n))
    assert abs(float(x.mean())) < 3 * math.sqrt((1 + phi) / ((1 - phi) * n))


@pytest.mark.parametrize(("phi", "cross"), [(0.3, 0.8), (0.3, wu.C6_CORR), (0.0, 0.1), (0.3, 0.1)])
def test_bivariate_ar1_has_the_stated_correlations(phi: float, cross: float) -> None:
    """H1: lag-0 cross-correlation ``cross`` and lag-1 autocorrelation ``phi`` in both columns.

    200 independent paths of 5000 states; the mean of the per-path estimates is compared with the
    target at 3 standard errors, the standard error being the sample SD / sqrt(200) (about 9.5e-4 for the
    lag-1). The lag-1 estimator's O(1/N) bias (about 4e-4) is 0.46 SE, which shifts the z-test and
    roughly doubles its false-alarm rate to 0.0058 (from 0.0027); 3 SE is kept.
    """
    paths = 200
    rng = rng_for("ar1-bivariate", f"{phi:g}", f"{cross:g}")
    stats = []
    for _ in range(paths):
        x = wu.ar1(rng, 5000, phi, 2, cross)
        c = x - x.mean(0)
        stats.append([np.corrcoef(x.T)[0, 1],
                      np.sum(c[1:, 0] * c[:-1, 0]) / np.sum(c[:, 0] ** 2),
                      np.sum(c[1:, 1] * c[:-1, 1]) / np.sum(c[:, 1] ** 2)])
    stats_array = np.array(stats)
    se = stats_array.std(axis=0, ddof=1) / math.sqrt(paths)
    for value, target, error in zip(stats_array.mean(0), (cross, phi, phi), se, strict=True):
        assert abs(value - target) < 3 * error


def _chunks(spec: wu.CaseSpec, name: str, n_chunks: int, size: int, statistic) -> np.ndarray:
    """Per-chunk statistic of ``n_chunks`` independent i.i.d. samples of ``size`` states (phi = 0)."""
    rng = rng_for("truth", name)
    return np.array([statistic(wu.generate(spec, 0.0, rng, n=size)) for _ in range(n_chunks)])


def _within_three_se(values: np.ndarray, target: float) -> bool:
    return abs(values.mean() - target) < 3 * values.std(ddof=1) / math.sqrt(len(values))


def test_truths_of_the_log_normal_cases() -> None:
    """H3: E[a - b] = 0 (C2), E[a]/E[b] = 1.05 (C4) and 1.10 (C5), over 10^7 draws each.

    Reference: analytic (a = exp(mu + sigma u), b = exp(sigma v) with u, v standard normal, so
    E[a]/E[b] = exp(mu)). 100 chunks of 10^5 draws; the standard error is the SD of the chunk values
    / sqrt(100); the ratio estimator's O(1/n) bias is about 1e-5 against a standard error of 3.3e-4 to 5.2e-4.
    """
    assert _within_three_se(
        _chunks(wu.CaseSpec("C2"), "C2", 100, 10**5, lambda d: np.mean(d["a"] - d["b"])), 0.0)
    assert _within_three_se(
        _chunks(wu.CaseSpec("C4"), "C4", 100, 10**5, lambda d: d["a"].mean() / d["b"].mean()),
        1.05)
    assert _within_three_se(
        _chunks(wu.CaseSpec("C5"), "C5", 100, 10**5, lambda d: d["a"].mean() / d["b"].mean() - 1),
        0.10)


def test_truth_of_the_spearman_case() -> None:
    """H3: the Spearman correlation of C6's Gaussian pair is 0.7, over 10^7 draws.

    Reference: Spearman = (6/pi) arcsin(c/2) = 0.7 exactly at c = 2 sin(0.7 pi/6). 100 chunks of
    10^5 draws; standard error from the chunk SD / sqrt(100) (about 2e-4); the finite-n bias
    3 (tau - rho_S)/(n + 1) = -6e-6 is negligible.
    """
    assert abs(6 / math.pi * math.asin(wu.C6_CORR / 2) - 0.7) < 1e-15
    values = _chunks(wu.CaseSpec("C6"), "C6", 100, 10**5, lambda d: spearman(d["x"], d["y"]))
    assert _within_three_se(values, 0.7)


def test_truth_of_the_partial_correlation_case() -> None:
    """H3: the partial correlation of C7's target and growth given [1, Q] is 0.1, over 10^7 draws.

    Reference: both conditional means lie in span[1, Q(s)], so the population partial correlation
    is corr(e1, e2) = 0.1 exactly (review M3 (d)). 100 chunks of 10^5 states; standard error of the mean
    from the chunk SD / sqrt(100): the per-chunk SD is about 3.1e-3, the standard error 3.1e-4.
    """
    def partial(d: dict) -> float:
        logit = np.log(d["weight"] / (1.0 - d["weight"]))
        return partial_correlation(logit, d["growth"], quadratic_controls(d["seeds"]))

    assert _within_three_se(_chunks(wu.CaseSpec("C7"), "C7", 100, 10**5, partial), 0.1)


def test_logrank_design_marginals() -> None:
    """The log-rank generator: terciles of exactly 200, censoring (1 - h)^240 = 0.0489 (L1) and
    (2 (1 - h)^240 + (1 - 2h)^240)/3 = 0.0334 (L2), also at phi = 0.3 (Gaussian copula, uniform
    marginal). 100 samples of 600 states each; standard error from the SD across samples."""
    h, hmax = wu.LOGRANK_HAZARD, wu.LOGRANK_HMAX
    for phi in wu.PHIS:
        for partial, expected in ((False, (1 - h) ** hmax),
                                  (True, (2 * (1 - h) ** hmax + (1 - 2 * h) ** hmax) / 3)):
            rng = rng_for("logrank", f"{phi:g}", partial)
            fractions = []
            for _ in range(100):
                labels, duration, event = wu.logrank_draw(rng, phi, partial)
                assert np.array_equal(np.bincount(labels), [200, 200, 200])
                assert duration.min() >= 1 and duration.max() <= hmax
                fractions.append(1.0 - event.mean())
            assert _within_three_se(np.array(fractions), expected), (phi, partial)


def test_delta_r2_design_marginals() -> None:
    """The delta-R2 generator: 15% exact zeros, x4 unit variance with corr(x4, x1) = 0.6, and a
    target noise that carries no information on x4 beyond x1 to x3 (corr of x4's innovation xi with
    the latent's residual is 0 by construction; here the correlation of x4 - 0.6 x1 with L - its
    x1..x3 part is checked to be 0). 10^6 i.i.d. draws; standard errors binomial 3.6e-4 for the zero
    fraction and 6.4e-4 for corr(x4, x1) ((1 - 0.36)/sqrt(n)), whose tolerance is 3 SE = 1.9e-3 (it was
    3e-3, 4.7 SE; tightened to the 3-SE rule of the other checks, a tightening of a self-check)."""
    n = 10**6
    profile, weight, _ = wu.delta_states(rng_for("delta"), n, 0.0, iid=True)
    se_zero = math.sqrt(0.15 * 0.85 / n)
    assert abs(float(np.mean(weight == 0.0)) - 0.15) < 3 * se_zero
    assert abs(float(profile[:, 3].var()) - 1.0) < 3 * math.sqrt(2 / n)
    assert abs(float(np.corrcoef(profile[:, 3], profile[:, 0])[0, 1]) - 0.6) < 1.9e-3
    interior = (weight > 0) & (weight < 1)
    latent = np.log(weight[interior] / (1 - weight[interior]))
    residual = latent - (profile[interior, 0] - 0.5 * profile[interior, 1] ** 2
                         + 0.5 * profile[interior, 1] * profile[interior, 2])
    extra = profile[interior, 3] - 0.6 * profile[interior, 0]
    assert abs(float(np.corrcoef(extra, residual)[0, 1])) < 3 / math.sqrt(interior.sum())


# ------------------------------------------------------------------------------- verdict rule
CASE_EDGES = {"C2": 0.0, "C4": 1.05, "C5": 0.10, "C6": 0.7, "C7": 0.1, "C8": 0.0, "C9": 0.0}


@pytest.mark.parametrize("case", sorted(CASE_EDGES))
def test_independent_rule_agrees_with_criterion_verdict_at_the_edges(case: str) -> None:
    """The band rule of ``expected_verdict`` equals ``criterion_verdict`` at every tie.

    A continuous simulation never has a bound equal to the edge, so A4 cannot tell an open from a
    closed edge; this deterministic table does (edge, just inside, just outside, straddle). The
    reference is the rule written in the harness from the criterion's wording (v3 section 2, DEC-0008
    A1): H2c upper edge 0 open; H2d 0.10 and H3c 1.05 closed; H1d lower edge 0.7 closed; H2b and
    H2e lower edge 0 open; H2a(ii) band (-0.1, 0.1) open.
    """
    edge = CASE_EDGES[case]
    band, closed = wu._BANDS[case]
    gap = 0.01
    points = [edge - 2 * gap, edge - gap, edge, edge + gap, edge + 2 * gap]
    if case == "C7":
        points += [-edge - 2 * gap, -edge - gap, -edge, -edge + gap]
    seen = set()
    for low in points:
        for high in points:
            if low > high:
                continue
            got = wu.expected_verdict(case, low, high)
            assert got == criterion_verdict((low + high) / 2, low, high, band, closed,
                                            n_states=500)[0], (case, low, high)
            seen.add(got)
    assert seen == {"pass", "fail", "inconclusive"}
    # the ties, stated explicitly
    ties = {"C2": [(-1, 0.0, "inconclusive"), (0.0, 1, "fail")],
            "C4": [(1, 1.05, "pass"), (1.05, 2, "inconclusive")],
            "C5": [(0, 0.10, "pass"), (0.10, 1, "inconclusive")],
            "C6": [(0.7, 0.9, "pass"), (0.5, 0.7, "inconclusive")],
            "C7": [(-0.1, 0.05, "inconclusive"), (0.1, 0.2, "fail"), (-0.2, -0.1, "fail")],
            "C8": [(0.0, 1, "inconclusive"), (-1, 0.0, "fail")],
            "C9": [(0.0, 1, "inconclusive"), (-1, 0.0, "fail")]}
    for low, high, expected in ties[case]:
        assert wu.expected_verdict(case, low, high) == expected, (case, low, high)


# ------------------------------------------------------------------ evaluation and the switch
def fake_run(case: str, phi: float, covered: tuple[int, int], fail_misses: int, *,
             failed: int = 0, mismatch: bool = False, identity_bad: bool = False
             ) -> wu.CoverageRun:
    """R = 1000 replications of the upper-sided case C4 with the stated counts.

    Level 0 and level 1 cover in the first ``covered[j]`` replications; at level 1 ``fail_misses``
    of the others have the truth below the lower bound (verdict fail), the rest above the upper bound
    (verdict pass).
    """
    spec, total = wu.CaseSpec(case), wu.R_COVERAGE
    truth = spec.truth
    lower = np.zeros((total, 2))
    upper = np.zeros((total, 2))
    for j in (0, 1):
        lower[:, j], upper[:, j] = truth - 0.05, truth + 0.05
        misses = np.arange(covered[j], total)
        lower[misses, j], upper[misses, j] = truth - 0.2, truth - 0.1      # truth above
    low_side = np.arange(covered[1], covered[1] + fail_misses)
    lower[low_side, 1], upper[low_side, 1] = truth + 0.1, truth + 0.2      # truth below
    verdict = np.array([wu.expected_verdict(case, lo, hi) for lo, hi in zip(lower[:, 1],
                                                                              upper[:, 1])])
    expected = verdict.copy()
    if mismatch:
        verdict[0] = "pass" if verdict[0] != "pass" else "fail"
    identity = np.full(total, -1)
    identity[:10] = 1
    if identity_bad:
        identity[3] = 0
    return wu.CoverageRun(
        spec=spec, phi=phi, R=total, estimate=np.zeros(total), lower=lower, upper=upper,
        failed=np.zeros((total, 2), int) + (np.arange(total)[:, None] < failed),
        verdict=verdict, expected=expected, identity=identity, zero_ok=np.full(total, -1))


def test_evaluate_coverage_applies_the_registered_bounds_exactly() -> None:
    """Boundary counts of A1 (930), A2 (972), A3 (39 / 16), the C4 ranges and the exact checks.

    Reference: the registered integers and the C4 phi = 0 ranges of the review: coverage 95%
    (912, 965), 98.3% (959, 992), A3 P(pass) and P(fail) (2, 25) (level 98.3%, bound 16).
    """
    ok = wu.evaluate_coverage(fake_run("C4", 0.0, (930, 972), 12))
    assert (ok.exact, ok.consistency, ok.roadmap) == ([], [], [])
    assert ok.row["roadmap_outcome"] == "pass" and ok.row["asserted"] is True
    assert wu.evaluate_coverage(fake_run("C4", 0.0, (929, 972), 12)).roadmap[0].count("A1") == 1
    assert "A2" in wu.evaluate_coverage(fake_run("C4", 0.0, (930, 971), 12)).roadmap[0]
    # misses = 1000 - 972 = 28 = 12 fail + 16 pass; 11 fail + 17 pass breaks the A3 pass bound only
    assert "A3 P(pass)" in wu.evaluate_coverage(fake_run("C4", 0.0, (930, 972), 11)).roadmap[0]
    assert "A3 P(fail)" in wu.evaluate_coverage(fake_run("C4", 0.0, (930, 972), 17)).roadmap[0]
    # ranges (inclusive)
    assert wu.evaluate_coverage(fake_run("C4", 0.0, (912, 972), 12)).consistency == []
    assert wu.evaluate_coverage(fake_run("C4", 0.0, (965, 972), 12)).consistency == []
    assert len(wu.evaluate_coverage(fake_run("C4", 0.0, (911, 972), 12)).consistency) == 1
    assert len(wu.evaluate_coverage(fake_run("C4", 0.0, (966, 972), 12)).consistency) == 1
    assert len(wu.evaluate_coverage(fake_run("C4", 0.0, (930, 958), 12)).consistency) >= 1
    assert len(wu.evaluate_coverage(fake_run("C4", 0.0, (930, 993), 3)).consistency) >= 1
    # the range is the defect test: coverage that passes the ROADMAP bound but is too high is flagged
    assert wu.evaluate_coverage(fake_run("C4", 0.0, (970, 972), 12)).roadmap == []
    assert len(wu.evaluate_coverage(fake_run("C4", 0.0, (970, 972), 12)).consistency) == 1
    # exact checks
    assert "A5" in wu.evaluate_coverage(fake_run("C4", 0.0, (930, 972), 12, failed=1)).exact[0]
    assert "A4" in wu.evaluate_coverage(fake_run("C4", 0.0, (930, 972), 12, mismatch=True)).exact[0]
    assert "identity" in wu.evaluate_coverage(
        fake_run("C4", 0.0, (930, 972), 12, identity_bad=True)).exact[0]
    with pytest.raises(ValueError, match="R must be"):
        wu.evaluate_coverage(wu.CoverageRun(**{**fake_run("C4", 0.0, (930, 972), 12).__dict__,
                                               "R": 999}))


def test_roadmap_switch_has_both_modes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Option K (``ASSERT_ROADMAP_BOUNDS = True``) raises on a failed bound, Option C reports it.

    The outcome is "fail" in both modes, so the results table always shows it. The constant is read
    at call time, so flipping the module attribute flips the behaviour of every test that calls
    ``enforce``.
    """
    assert wu.enforce([], asserting=True) == wu.enforce([], asserting=False) == "pass"
    with pytest.raises(AssertionError, match="finding"):
        wu.enforce(["C4: A1 929 < 930"], asserting=True)
    assert wu.enforce(["C4: A1 929 < 930"], asserting=False) == "fail"
    monkeypatch.setattr(wu, "ASSERT_ROADMAP_BOUNDS", True)
    with pytest.raises(AssertionError):
        wu.enforce(["x"])
    monkeypatch.setattr(wu, "ASSERT_ROADMAP_BOUNDS", False)
    assert wu.enforce(["x"]) == "fail"


def fake_logrank(row: str, phi: float, fwer: int, passed: int, uncomputed: int = 0
                 ) -> wu.LogrankRun:
    table = np.zeros((wu.R_LOGRANK, 10))
    table[:fwer, 0] = 1.0
    table[:passed, 1] = 1.0
    table[:, 2:4] = 0.5
    table[:uncomputed, 4] = 1.0
    table[:, 6:10] = [2, 0, 0, 1]
    return wu.LogrankRun(row=row, phi=phi, R=wu.R_LOGRANK, table=table)


def test_evaluate_logrank_applies_the_registered_bounds_exactly() -> None:
    """L ROADMAP bound 33 of 2000 and the L1 / L2 ranges, boundary counts (review M5).

    L1 phi = 0: FWER range (7, 39), pass range (0, 9); L2 phi = 0.3: pass range (9, 44).
    """
    assert wu.evaluate_logrank(fake_logrank("L1", 0.0, 20, 5)).roadmap == []
    assert len(wu.evaluate_logrank(fake_logrank("L1", 0.0, 34, 5)).roadmap) == 1
    assert wu.evaluate_logrank(fake_logrank("L1", 0.0, 33, 5)).roadmap == []
    assert len(wu.evaluate_logrank(fake_logrank("L1", 0.0, 6, 5)).consistency) == 1
    assert wu.evaluate_logrank(fake_logrank("L1", 0.0, 7, 9)).consistency == []
    assert len(wu.evaluate_logrank(fake_logrank("L1", 0.0, 7, 10)).consistency) == 1
    assert wu.evaluate_logrank(fake_logrank("L2", 0.3, 0, 9)).consistency == []
    assert len(wu.evaluate_logrank(fake_logrank("L2", 0.3, 0, 8)).consistency) == 1
    assert len(wu.evaluate_logrank(fake_logrank("L2", 0.3, 0, 34)).roadmap) == 1
    assert "L3" in wu.evaluate_logrank(fake_logrank("L1", 0.0, 20, 5, uncomputed=1)).exact[0]


def fake_delta(contains_zero: int, positive_lower: int, covers: int, refit_bad: int = 0,
               phi: float = 0.0) -> wu.DeltaRun:
    """R = 500 replications: ``contains_zero`` intervals around 0, ``positive_lower`` above 0, the
    rest below 0; the truth is inside the interval in the first ``covers`` replications."""
    total = wu.R_DELTA
    lo, hi = np.full(total, -0.3), np.full(total, -0.2)
    lo[:contains_zero], hi[:contains_zero] = -0.1, 0.1
    top = np.arange(contains_zero, contains_zero + positive_lower)
    lo[top], hi[top] = 0.05, 0.15
    truth = np.where(np.arange(total) < covers, (lo + hi) / 2, 5.0)
    refit = np.ones(total)
    refit[:refit_bad] = 0.0
    block = np.column_stack([np.zeros(total), lo, hi, truth, np.full(total, 0.001), refit,
                             np.zeros(total), np.full(total, 0.4), np.ones(total)])
    return wu.DeltaRun(phi=phi, R=total, table=np.hstack([block, block]))


def test_evaluate_delta_applies_the_registered_bounds_exactly() -> None:
    """N1 >= 461, N2 <= 22 and N3 >= 461 (all under the constant since addendum A9), the bitwise
    refit (exact). N1 alone can fail with no false 'distinct' when the missed intervals lie below 0.
    """
    assert wu.evaluate_delta(fake_delta(478, 22, 461)).roadmap == []
    only_n1 = wu.evaluate_delta(fake_delta(460, 0, 461))
    assert len(only_n1.roadmap) == 2 and "N1" in only_n1.roadmap[0]       # both targets
    assert wu.evaluate_delta(fake_delta(461, 0, 461)).roadmap == []
    n2 = wu.evaluate_delta(fake_delta(477, 23, 461))
    assert len(n2.roadmap) == 2 and "N2" in n2.roadmap[0]                  # 23 > 22
    n3 = wu.evaluate_delta(fake_delta(478, 22, 460))
    assert len(n3.roadmap) == 2 and "N3" in n3.roadmap[0]                  # 460 < 461
    assert wu.evaluate_delta(fake_delta(478, 22, 461, refit_bad=1)).exact[0].count("bitwise") == 1


def test_delta_roadmap_rows_follow_the_switch_in_both_modes() -> None:
    """A failed N1, N2 or N3 row raises under Option K and is only reported under Option C.

    Their consistency ranges are asserted in both modes: ``evaluate_delta`` fills ``consistency``
    independently of the switch (checked by the next test).
    """
    for counts in ((460, 0, 461), (477, 23, 461), (478, 22, 460)):
        failures = wu.evaluate_delta(fake_delta(*counts)).roadmap
        assert len(failures) == 2
        with pytest.raises(AssertionError, match="finding"):
            wu.enforce(failures, asserting=True)
        assert wu.enforce(failures, asserting=False) == "fail"
    assert wu.enforce(wu.evaluate_delta(fake_delta(478, 22, 461)).roadmap, asserting=True) == "pass"


def test_evaluate_delta_applies_the_a9_ranges_exactly() -> None:
    """The 12 pre-registered ranges (phi 0: N1 logit (431, 483), indicator (440, 487); N2 (0, 23) and
    (0, 25); N3 (446, 490) and (448, 491); phi 0.3: N1 (434, 484) and (436, 485), N2 (0, 16) and
    (0, 21), N3 (449, 491) and (448, 491)): inclusive ends, row by row, independent of the switch."""
    logit, indicator = "logit_w_interior", "w_zero_indicator"
    ok = wu.evaluate_delta(fake_delta(478, 22, 461))
    assert ok.consistency == [] and set(ok.consistency_rows.values()) == {None}
    assert len(ok.consistency_rows) == 6
    n1_high = wu.evaluate_delta(fake_delta(484, 0, 461))      # logit out (> 483), indicator in
    assert [k for k, v in n1_high.consistency_rows.items() if v] == [f"n1|{logit}"]
    n1_low = wu.evaluate_delta(fake_delta(439, 0, 461))       # indicator out (< 440), logit in
    assert [k for k, v in n1_low.consistency_rows.items() if v] == [f"n1|{indicator}"]
    n2_high = wu.evaluate_delta(fake_delta(470, 24, 461))     # logit out (> 23), indicator in (<= 25)
    assert [k for k, v in n2_high.consistency_rows.items() if v] == [f"n2|{logit}"]
    n3_low = wu.evaluate_delta(fake_delta(478, 22, 446))      # logit in (>= 446), indicator out (< 448)
    assert [k for k, v in n3_low.consistency_rows.items() if v] == [f"n3|{indicator}"]
    assert len(wu.evaluate_delta(fake_delta(478, 22, 445)).consistency) == 2
    # phi = 0.3 has its own ranges: N2 = 17 is out for the logit (<= 16), in for the indicator
    third = wu.evaluate_delta(fake_delta(478, 17, 461, phi=0.3))
    assert [k for k, v in third.consistency_rows.items() if v] == [f"n2|{logit}"]


def test_delta_reference_holds_12_ranges() -> None:
    """Addendum A9: 4 (phi, target) cells x 3 rows = 12 ranges, each containing its rate x 500; the
    rates are probabilities, the bound-failure chances lie in [0, 1], and N1 is the row that fails."""
    cells = ref.DELTA_R2_REFERENCE
    assert sorted(cells) == [("0", "logit_w_interior"), ("0", "w_zero_indicator"),
                             ("0.3", "logit_w_interior"), ("0.3", "w_zero_indicator")]
    n_ranges = 0
    for entry in cells.values():
        for key in ("n1", "n2", "n3"):
            rate, se, p_fail, (low, high) = entry[key]
            assert 0 < rate < 1 and se > 0 and 0 <= p_fail <= 1 and low <= rate * 500 <= high
            n_ranges += 1
        assert entry["n1"][2] > entry["n3"][2] >= entry["n2"][2]
    assert n_ranges == 12 and ref.DELTA_R2_REFERENCE_R == 1000


def test_result_table_round_trips_numpy_and_non_finite_values(tmp_path) -> None:
    """The results JSON holds numpy values and non-finite numbers as plain JSON, row by row."""
    table = wu.ResultTable("selfcheck", tmp_path)
    table.add("a", {"n": np.int64(3), "x": np.float64(0.5), "v": np.array([1, 2]),
                    "bad": float("inf"), "t": (1, 2)}, workers=3)
    table.add("b", {"ok": True}, workers=3)
    loaded = json.loads(table.path.read_text())
    assert loaded["_meta"]["workers"] == 3
    assert loaded["a"] == {"n": 3, "x": 0.5, "v": [1, 2], "bad": "inf", "t": [1, 2]}
    assert loaded["b"] == {"ok": True}
    assert loaded["_meta"]["bootstrap"] == [2000, 5]


# ------------------------------------------------------------------------------ pool, end to end
def test_pool_sets_single_thread_workers_and_restores_the_environment() -> None:
    """Workers see one thread everywhere; the parent environment is restored on exit (O1)."""
    names = ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "LPC_THREADS",
             "PJRT_NPROC", "NPROC", "JAX_PLATFORMS")
    before = {name: os.environ.get(name) for name in names}
    with wu.worker_pool(workers=1) as one:
        seen = [one.submit(os.getenv, name).result() for name in names]
        assert seen == ["1"] * 6 + ["cpu"]
    assert {name: os.environ.get(name) for name in names} == before
    assert wu.pool_size() == min(int(os.environ.get("LPC_THREADS", "4")), 4)


def test_worker_count_does_not_change_a_replication() -> None:
    """H2: the first 8 replications of C4 (phi 0.3) and L1 (phi 0) are bitwise equal with 1 worker,
    2 workers, and in process, however the replications are split into tasks.

    Reference: the same function called in process on one task of all 8 replications.
    """
    cov_tasks = [(wu.CaseSpec("C4"), 0.3, r, r + 1, 10) for r in range(8)]
    log_tasks = [("L1", 0.0, r, r + 1) for r in range(8)]
    in_process = (wu._coverage_task((wu.CaseSpec("C4"), 0.3, 0, 8, 10)),
                  wu._logrank_task(("L1", 0.0, 0, 8)))
    for workers in (1, 2):
        with wu.worker_pool(workers=workers) as small:
            cov = [row for part in wu.run_tasks(small, wu._coverage_task, cov_tasks)
                   for row in part]
            log = [row for part in wu.run_tasks(small, wu._logrank_task, log_tasks)
                   for row in part]
        assert cov == in_process[0], workers
        assert np.array_equal(np.array(log), np.array(in_process[1]), equal_nan=True), workers


def test_every_design_runs_end_to_end_and_passes_the_exact_checks(pool, tmp_path) -> None:
    """All nine coverage designs, the characterization rows, L1, L2 and the delta-R2 study run on
    the pool at a tiny R and satisfy the exact checks (identity with the production function, A4,
    A5, the C7 zero column, L3, the bitwise refit). The counts against the registered bounds are
    meaningless at this R and are ignored (``strict=False``); this checks the wiring only."""
    table = wu.ResultTable("selfcheck-e2e", tmp_path)
    specs = [wu.CaseSpec(f"C{k}") for k in range(1, 10)]
    specs += [wu.CaseSpec("C2", 1.5, "h1.5"), wu.CaseSpec("C4", 2.0, "h2"),
              wu.CaseSpec("C1", 1.0, "s")]
    for spec in specs:
        phi = 0.1 if spec.tag == "s" else 0.3
        run = wu.run_coverage(pool, spec, phi, R=4)
        ev = wu.evaluate_coverage(run, strict=False)
        assert ev.exact == [], ev.exact
        assert ev.row["failed_resamples"] == 0
        table.add(f"{spec.label}-{phi:g}", ev.row, workers=pool.wu_workers)
    for row in ("L1", "L2"):
        run = wu.run_logrank(pool, row, 0.3, R=20)
        ev = wu.evaluate_logrank(run, strict=False)
        assert ev.exact == [] and ev.row["uncomputed_pairs"] == 0
        table.add(row, ev.row, workers=pool.wu_workers)
    delta = wu.run_delta(pool, 0.3, R=2, chunk=1)
    ev = wu.evaluate_delta(delta, strict=False)
    assert ev.exact == [] and delta.table.shape == (2, 18)
    assert all(ev.row["targets"][name]["failed_resamples"] == 0 for name in wu.DELTA_TARGETS)
    table.add("delta", ev.row, workers=pool.wu_workers)
    saved = json.loads(table.path.read_text())
    assert len(saved) == len(specs) + 3 + 1
    assert saved["_meta"]["workers"] == pool._max_workers == wu.pool_size()


def test_c7_zero_column_rule_allows_a_failing_interior_part() -> None:
    """The combined verdict of H2a(ii) is "fail" when the interior part fails (``combine_verdicts``:
    one fail fails the whole), else "inconclusive" because the zero part is not computable.

    Added after run 2, in which the first form of the check demanded "inconclusive" and so rejected a
    correct replication whose interior part failed (a defect of the harness's expectation, found at
    phi = 0.3, replication with an interior "fail"; no bound moved)."""
    zero = {"n_failed_resamples": 2000, "reason": "not computable", "verdict": "inconclusive"}
    for interior, combined, ok in (("fail", "fail", True), ("inconclusive", "inconclusive", True),
                                   ("pass", "inconclusive", True), ("fail", "inconclusive", False),
                                   ("inconclusive", "fail", False)):
        extra = {"zero_part": zero, "combined": combined}
        assert wu._zero_column_ok(extra, interior, 2000) is ok, (interior, combined)
    assert not wu._zero_column_ok({"zero_part": {**zero, "n_failed_resamples": 1999},
                                   "combined": "inconclusive"}, "pass", 2000)


def test_result_files_are_stamped_and_never_overwritten(tmp_path) -> None:
    """Two tables of the same name get different files, each keeps its own rows (R2)."""
    first, second = wu.ResultTable("same", tmp_path), wu.ResultTable("same", tmp_path)
    assert first.path != second.path
    first.add("a", {"x": 1}, workers=4)
    second.add("b", {"x": 2}, workers=4)
    assert sorted(path.name[:10] for path in tmp_path.iterdir()) == ["wu0006_same"] * 2
    assert "a" in json.loads(first.path.read_text()) and "b" not in json.loads(first.path.read_text())
    assert first.path.name.startswith("wu0006_same_20") and first.path.name.endswith(".json")


def test_run_cache_records_the_pool_size_at_creation(pool, tmp_path) -> None:
    """R1: the results JSON written by ``RunCache`` says ``workers`` = the pool's size (4 here), not
    1, although the parent environment has ``LPC_THREADS=1`` while the pool lives. Runs C1 at phi 0
    (R = 1000, a few seconds), the cheapest study design, through the same code path as the study
    files, and checks the file and the exact checks."""
    assert os.environ["LPC_THREADS"] == "1"
    cache = wu.RunCache("smoke-cache", tmp_path)
    evaluation = cache.coverage(pool, wu.CaseSpec("C1"), 0.0)
    assert evaluation.exact == [] and evaluation.row["R"] == wu.R_COVERAGE
    meta = json.loads(cache.table.path.read_text())["_meta"]
    assert meta["workers"] == pool._max_workers == pool.wu_workers


def test_delta_roadmap_rows_are_keyed_not_matched_by_text() -> None:
    """R6: the N-row tests select failures by row key (``delta_rows``), never by message text.

    Every message of ``roadmap`` is in exactly one row list and names its row; an unknown row raises.
    A reworded message that dropped its row label would fail here, and a row that selected nothing
    would raise ``KeyError``."""
    ev = wu.evaluate_delta(fake_delta(460, 23, 460))      # N1, N2 and N3 all fail, both targets
    assert {row: len(msgs) for row, msgs in ev.roadmap_rows.items()} == {"n1": 2, "n2": 2, "n3": 2}
    assert sorted(ev.roadmap) == sorted(wu.delta_rows(ev, "n1", "n2", "n3"))
    for row in ("n1", "n2", "n3"):
        assert all(f" {row.upper()} " in message for message in wu.delta_rows(ev, row))
        assert not set(wu.delta_rows(ev, row)) & set(wu.delta_rows(
            ev, *({"n1", "n2", "n3"} - {row})))
    assert len(wu.delta_rows(ev, "n2", "n3")) == 4
    with pytest.raises(KeyError):
        wu.delta_rows(ev, "n4")
    ok = wu.evaluate_delta(fake_delta(478, 22, 461))
    assert wu.delta_rows(ok, "n1", "n2", "n3") == [] and ok.roadmap == []


def test_option_c_failure_warns_instead_of_passing_silently() -> None:
    """R6: under Option C a failed ROADMAP row gives a passing node plus a visible UserWarning."""
    with pytest.warns(UserWarning, match="Option C"):
        assert wu.enforce(["C4: A1 929 < 930"], asserting=False) == "fail"
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert wu.enforce([], asserting=False) == "pass"
