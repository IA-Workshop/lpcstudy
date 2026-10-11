"""Tests for lpcstudy.analysis: per-state Spearman trend; H1a, H1b and H1d (WU-0002.4 and .5)."""

from __future__ import annotations

import dataclasses
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
    leaves two orders). The CP entry has only ``slope`` and ``ci``; the PLP entry adds
    ``n_failed_resamples``; the top-level keys are the plan's. Exact verdicts.
    """
    from lpcstudy.analysis import h1b_seed_amplifier

    config = _config(100)
    ok = h1b_seed_amplifier(_fake_h1b_cell(np.random.default_rng(21001), 100, 1.6, 1.0), config)
    assert ok["CP"]["slope"] == pytest.approx(1.6, abs=1e-12, rel=0)
    assert ok["PLP"]["slope"] == pytest.approx(1.0, abs=1e-12, rel=0)
    assert ok["verdict"] == "pass" and ok["pass"] is True and ok["reason"] is None
    assert set(ok["CP"]) == {"slope", "ci"}
    assert set(ok["PLP"]) == {"slope", "ci", "n_failed_resamples"} and \
        ok["PLP"]["n_failed_resamples"] == 0
    assert set(ok) == {"CP", "PLP", "threshold", "n_states", "verdict", "reason", "pass"}
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
    NaN gain makes the PLP slope NaN, the verdict is "inconclusive" with reason "not computable"
    and the failed resamples are counted: exactly those whose indices include the NaN state
    (counted here by replaying the index draws of ``block_resample_indices`` with the same
    seed); 40 states give "n_states < 50".
    """
    from lpcstudy.analysis import h1b_seed_amplifier
    from lpcstudy.statistics import block_bootstrap, block_resample_indices, ols_slope

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

    broken = _fake_h1b_cell(np.random.default_rng(21004), 100, 1.0, 1.0)
    broken.oracles["test"].gains[3, :] = np.nan
    nan_out = h1b_seed_amplifier(broken, config)
    assert nan_out["verdict"] == "inconclusive" and nan_out["reason"] == "not computable"
    hit = sum(3 in idx for idx in block_resample_indices(
        100, config.bootstrap_resamples, config.bootstrap_block, config.seed))
    assert 0 < hit < config.bootstrap_resamples
    assert nan_out["PLP"]["n_failed_resamples"] == hit
    assert nan_out["pass"] is False

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
