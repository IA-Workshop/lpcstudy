"""Tests for V7 (estimator efficiency) and the validation gate (WU-0002.10).

Every V7 input is built as an exact product, ``delta = c * rho * nu * (power law)``, so the
references are hand-computed or come from an expression independent of the code under test
(``np.polyfit``, ``np.median``, ``1.1 ** 0.2``). Common value tolerance ``abs 1e-12``: the
ratios and the OLS on at most 4 levels, with values of magnitude at most 6, lose at most about
1e-14; every decision margin below is at least 1e-4 (measured by the applied mathematician at
2e-16 for 4 levels and 8e-15 for the two close levels). The bootstrap interval is reported
only; it enters no assertion except where every state is identical (interval of zero width).
"""

from __future__ import annotations

import dataclasses
from types import SimpleNamespace

import numpy as np
import pytest

from lpcstudy.analysis import v7_efficiency, v7_noise_scaling
from lpcstudy.config import SMOKE
from lpcstudy.validation import gate_status

CONFIG = dataclasses.replace(SMOKE, bootstrap_resamples=40)
LEVELS = np.array([0.005, 0.01, 0.02, 0.05])
NU11 = 2.0 ** ((np.arange(11) - 5) / 2.0)  # distinct, geometric: median / mean = 0.582
TOL = 1e-12


def _exact(levels: np.ndarray, nu: np.ndarray, factor: float = 1.0) -> np.ndarray:
    """``delta_i(rho) = factor * rho * nu_i``, shape (n_states, n_levels)."""
    return factor * levels[None, :] * nu[:, None]


def test_v7_passes_at_unit_efficiency_and_fails_at_085() -> None:
    """V7 passes when delta/(rho nu) = 1 and fails at 0.85 with the slope still 1.

    Reference: ROADMAP acceptance (D-28), exact products. With delta = c rho nu_i, every
    efficiency is c and ln delta has slope 1 exactly. The mean-nu variant (divide by
    mean(nu)) would give median(nu)/mean(nu) = 0.5824 here (hand value, also computed below),
    outside the band, so the test is not vacuous: only the per-state oracle nu gives 1.
    Tolerance: abs 1e-12 (module note); decision margins 0.05 and 0.15.
    """
    out = v7_efficiency(LEVELS, _exact(LEVELS, NU11), NU11, CONFIG)
    assert out["pass"] is True and out["slope_pass"] is True
    assert out["n_states"] == 11 and out["n_nonfinite"] == 0
    assert out["median_slope"] == pytest.approx(1.0, abs=TOL)
    assert out["ci"] == pytest.approx([1.0, 1.0], abs=TOL)  # identical slopes: zero width
    assert set(out["efficiency_median_by_noise"]) == {"0.005", "0.01", "0.02", "0.05"}
    for key, value in out["efficiency_median_by_noise"].items():
        assert value == pytest.approx(1.0, abs=TOL), key
        assert out["efficiency_pass_by_noise"][key] is True
        assert out["efficiency_ci_by_noise"][key] == pytest.approx([1.0, 1.0], abs=TOL)

    mean_variant = np.median(NU11) / np.mean(NU11)
    assert mean_variant == pytest.approx(0.5824, abs=1e-4) and not 0.9 <= mean_variant <= 1.1

    low = v7_efficiency(LEVELS, _exact(LEVELS, NU11, 0.85), NU11, CONFIG)
    assert low["median_slope"] == pytest.approx(1.0, abs=TOL) and low["slope_pass"] is True
    for value in low["efficiency_median_by_noise"].values():
        assert value == pytest.approx(0.85, abs=TOL)
    assert not any(low["efficiency_pass_by_noise"].values())
    assert low["pass"] is False


def test_v7_slope_band_is_part_of_pass() -> None:
    """A median slope outside [0.9, 1.1] fails V7 even when every efficiency passes (A2).

    Reference: two close levels (0.01, 0.011) and delta = nu_i rho (rho/0.01)^b, so
    ln delta = ln nu + ln rho + b (ln rho - ln 0.01) has slope 1 + b exactly, and the
    efficiencies are 1 (at 0.01) and 1.1^b (at 0.011). b = 0.2: slope 1.2 (outside), efficiency
    1.1^0.2 = 1.019245 (inside). b = 0.05: slope 1.05 (inside), efficiency 1.004777.
    Tolerance: abs 1e-12 against the independent expression 1.1 ** b; abs 1e-6 against the
    6-digit hand value.
    """
    levels = np.array([0.01, 0.011])
    for b, slope_ok in ((0.2, False), (0.05, True)):
        deltas = _exact(levels, NU11) * (levels[None, :] / 0.01) ** b
        out = v7_efficiency(levels, deltas, NU11, CONFIG)
        assert out["median_slope"] == pytest.approx(1.0 + b, abs=TOL)
        assert out["slope_pass"] is slope_ok
        assert out["efficiency_median_by_noise"]["0.011"] == pytest.approx(1.1**b, abs=TOL)
        assert all(out["efficiency_pass_by_noise"].values())
        assert out["pass"] is slope_ok
    hand = {0.2: 1.019245, 0.05: 1.004777}
    for b, value in hand.items():
        assert 1.1**b == pytest.approx(value, abs=1e-6)


def test_v7_holds_at_every_noise_level() -> None:
    """One bad level fails V7 although the slope and the pooled median pass ("at every rho").

    Reference: delta = rho nu_i except x1.15 at rho = 0.05. The efficiency at 0.05 is 1.15
    (fails); the other three are 1. The slope, by hand: with x = ln rho, d = x - mean(x),
    sum d^2 = 2.903624, d_4 = 1.207078, the slope is 1 + ln(1.15) d_4 / sum d^2 =
    1 + 0.139762 * 1.207078 / 2.903624 = 1.0581011, inside the band; np.polyfit is the
    independent OLS. The pooled median over all (state, rho) is 1 (3/4 of the entries are 1).
    Tolerance: abs 1e-12 against polyfit; abs 1e-7 against the 8-digit hand slope.
    """
    deltas = _exact(LEVELS, NU11)
    deltas[:, 3] *= 1.15
    out = v7_efficiency(LEVELS, deltas, NU11, CONFIG)
    eff = out["efficiency_median_by_noise"]
    assert eff["0.05"] == pytest.approx(1.15, abs=TOL)
    for key in ("0.005", "0.01", "0.02"):
        assert eff[key] == pytest.approx(1.0, abs=TOL)
    assert out["efficiency_pass_by_noise"] == {"0.005": True, "0.01": True, "0.02": True,
                                               "0.05": False}
    polyfit = np.polyfit(np.log(LEVELS), np.log(deltas[0]), 1)[0]
    assert out["median_slope"] == pytest.approx(polyfit, abs=TOL)
    assert out["median_slope"] == pytest.approx(1.0581011, abs=1e-7)
    assert out["slope_pass"] is True
    pooled = np.median(deltas / (LEVELS[None, :] * NU11[:, None]))
    assert pooled == pytest.approx(1.0, abs=TOL) and 0.9 <= pooled <= 1.1
    assert out["pass"] is False


def test_v7_uses_medians_over_states_not_means_or_ratios_of_medians() -> None:
    """Efficiency is the median of per-state ratios; the slope is the median of OLS slopes.

    Reference: 5 states with efficiencies (0.80, 0.95, 1.0, 1.05, 2.0) and nu = (2, 4, 0.5, 1,
    8) at both levels. Median of ratios 1.0 (passes); mean of ratios 1.16 (fails); ratio of
    medians: median(delta) = 1.6 rho (delta_i = 1.6, 3.8, 0.5, 1.05, 16 times rho), median(nu)
    = 2, so 0.80 (fails). Slope part: levels (0.01, 0.02), delta = nu rho (rho/0.01)^b_i with
    b = (-0.5, 0, 0.05, 0.1, 3): per-state slopes 1 + b = (0.5, 1, 1.05, 1.1, 4), median 1.05
    (passes), mean 1.53 (fails). The efficiencies at 0.02 are 2^b = (0.7071, 1, 1.0353, 1.0718,
    8), median 2^0.05 = 1.0353. Tolerance: abs 1e-12; margins >= 0.05.
    """
    nu = np.array([2.0, 4.0, 0.5, 1.0, 8.0])
    eff = np.array([0.80, 0.95, 1.0, 1.05, 2.0])
    levels = np.array([0.01, 0.02])
    deltas = eff[:, None] * _exact(levels, nu)
    assert np.mean(eff) == pytest.approx(1.16, abs=TOL)
    assert np.median(deltas[:, 0] / levels[0]) / np.median(nu) == pytest.approx(0.80, abs=TOL)
    out = v7_efficiency(levels, deltas, nu, CONFIG)
    assert out["efficiency_median_by_noise"]["0.01"] == pytest.approx(1.0, abs=TOL)
    assert out["efficiency_median_by_noise"]["0.02"] == pytest.approx(1.0, abs=TOL)
    assert out["pass"] is True

    exponents = np.array([-0.5, 0.0, 0.05, 0.1, 3.0])
    deltas = _exact(levels, nu) * (levels[None, :] / 0.01) ** exponents[:, None]
    out = v7_efficiency(levels, deltas, nu, CONFIG)
    assert out["median_slope"] == pytest.approx(1.05, abs=TOL)
    assert np.mean(1.0 + exponents) == pytest.approx(1.53, abs=TOL)
    assert out["efficiency_median_by_noise"]["0.02"] == pytest.approx(2.0**0.05, abs=TOL)
    assert out["pass"] is True


def test_v7_band_is_closed_and_edges_are_sharp() -> None:
    """0.9001 and 1.0999 pass; 0.8999 and 1.1001 fail, at every level.

    Reference: delta = c rho nu_i with c set to the edge +- 1e-4 (the slope is 1). The
    margin 1e-4 is eight orders above the rounding of the ratio (about 1e-16). Exact decisions.
    """
    for factor, expected in ((1.0999, True), (0.9001, True), (1.1001, False), (0.8999, False)):
        out = v7_efficiency(LEVELS, _exact(LEVELS, NU11, factor), NU11, CONFIG)
        assert out["pass"] is expected, factor
        assert all(v is expected for v in out["efficiency_pass_by_noise"].values()), factor
        assert out["slope_pass"] is True


def test_v7_counts_non_finite_input_and_fails() -> None:
    """A NaN delta, or a non-finite or non-positive nu, is counted and fails V7 (PRIME.4).

    Reference: hand counts. One NaN delta in state 2 gives n_nonfinite 1; with nu_5 = -1 as
    well, 2 (two distinct states); nu = 0, nu = NaN and nu = +inf each count one state. A state
    with both a NaN delta and a bad nu counts once. The state is not dropped: n_states stays 11,
    and the NaN propagates to the median so the point statistics are NaN and fail the band.
    Exact counts and flags.
    """
    base = _exact(LEVELS, NU11)

    deltas = base.copy()
    deltas[2, 1] = np.nan
    out = v7_efficiency(LEVELS, deltas, NU11, CONFIG)
    assert out["n_nonfinite"] == 1 and out["n_states"] == 11
    assert out["pass"] is False and out["slope_pass"] is False
    assert np.isnan(out["median_slope"])

    nu = NU11.copy()
    nu[5] = -1.0
    out = v7_efficiency(LEVELS, deltas, nu, CONFIG)
    assert out["n_nonfinite"] == 2 and out["pass"] is False

    for bad in (0.0, np.nan, np.inf, -1.0):
        nu = NU11.copy()
        nu[4] = bad
        out = v7_efficiency(LEVELS, base, nu, CONFIG)
        assert out["n_nonfinite"] == 1 and out["pass"] is False, bad
        assert not any(out["efficiency_pass_by_noise"].values()), bad

    both = base.copy()
    both[3, 0] = np.inf
    nu = NU11.copy()
    nu[3] = 0.0
    assert v7_efficiency(LEVELS, both, nu, CONFIG)["n_nonfinite"] == 1

    zero = base.copy()
    zero[7, 2] = 0.0  # delta = 0 has no logarithm: counted too
    assert v7_efficiency(LEVELS, zero, NU11, CONFIG)["n_nonfinite"] == 1


def test_v7_rejects_malformed_arrays() -> None:
    """Shapes, level count and level sign are checked where the data enter (DSGN.2).

    Reference: the contract of ``v7_efficiency``: ``deltas`` is (n_states, n_levels), ``nu``
    is (n_states,), at least two distinct positive levels. Exact: each case raises ValueError.
    """
    good = _exact(LEVELS, NU11)
    with pytest.raises(ValueError):
        v7_efficiency(LEVELS, good[:, :3], NU11, CONFIG)
    with pytest.raises(ValueError):
        v7_efficiency(LEVELS, good, NU11[:5], CONFIG)
    with pytest.raises(ValueError):
        v7_efficiency(LEVELS[:1], good[:, :1], NU11, CONFIG)
    with pytest.raises(ValueError):
        v7_efficiency(np.array([0.01, 0.01]), good[:, :2], NU11, CONFIG)
    with pytest.raises(ValueError):
        v7_efficiency(np.array([-0.01, 0.02]), good[:, :2], NU11, CONFIG)


def _stub_cell(est_seed: np.ndarray, nu: np.ndarray) -> SimpleNamespace:
    moments = SimpleNamespace(est_seed=est_seed)
    return SimpleNamespace(splits={"test": SimpleNamespace(moments=moments)},
                           oracles={"test": SimpleNamespace(nu=nu)})


def test_v7_wrapper_sorts_the_levels_and_only_extracts_arrays() -> None:
    """``v7_noise_scaling`` on unsorted stub cells equals ``v7_efficiency`` on sorted arrays.

    Reference: the plan (item 2, test ix): the wrapper does nothing but extract the arrays.
    The deltas are exact products times a seeded (default_rng(7)) lognormal factor of sd 0.02,
    so the output has distinct, non-trivial values. The comparison is a dict equality: same
    float64 operations in the same order, no tolerance. This is a refactoring guard, not a
    correctness test of the statistic (those are above).
    """
    rng = np.random.default_rng(7)
    deltas = _exact(LEVELS, NU11) * np.exp(0.02 * rng.standard_normal((11, 4)))
    order = [2, 0, 3, 1]  # unsorted insertion order
    cells = {float(LEVELS[i]): _stub_cell(deltas[:, i], NU11) for i in order}
    assert list(cells) != sorted(cells)
    out = v7_noise_scaling(cells, CONFIG)
    assert out == v7_efficiency(LEVELS, deltas, NU11, CONFIG)
    assert out["n_states"] == 11


def _passing_validation() -> dict:
    return {"delay_jacobian_rel_err": 1e-6, "gain_rel_err": 1e-6, "crlb_ratio_median": 1.0,
            "km_max_abs_dev": 1e-3, "integrator_max_dev_sigma": 1e-5,
            "convergence": {"pass": True}}


def test_gate_status_requires_and_reports_v7() -> None:
    """``gate_status(validation, v7)``: flags V1, V2, V4, V5, V6, V7 and gate_pass = all.

    Reference: the plan (item 3): V7 = v7["pass"], gate_pass requires it (precedent V4 with
    ``convergence["pass"]``). Hand cases: all pass gives exactly seven keys, all true; V7
    failing flips V7 and gate_pass only; one of V1-V6 failing flips its flag and gate_pass but
    not V7; the call without ``v7`` raises TypeError. Exact booleans; no tolerance.
    """
    good = gate_status(_passing_validation(), {"pass": True})
    assert set(good) == {"V1", "V2", "V4", "V5", "V6", "V7", "gate_pass"}
    assert all(v is True for v in good.values())

    bad = gate_status(_passing_validation(), {"pass": False})
    assert bad["V7"] is False and bad["gate_pass"] is False
    assert all(bad[k] is True for k in ("V1", "V2", "V4", "V5", "V6"))

    failing = dict(_passing_validation(), km_max_abs_dev=0.5)
    other = gate_status(failing, {"pass": True})
    assert other["V5"] is False and other["V7"] is True and other["gate_pass"] is False

    with pytest.raises(TypeError):
        gate_status(_passing_validation())  # type: ignore[call-arg]
