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
from scipy import integrate, special
from scipy.spatial import cKDTree

from lpcstudy.analysis import v7_efficiency, v7_noise_scaling
from lpcstudy.config import SMOKE
from lpcstudy.ensemble import AnalogLibrary, retrieval_spread
from lpcstudy.validation import (P2C_KAPPA, UNIT_ROUNDOFF, check_p2_bound, chi_tail_moment,
                                 gate_status, p2_bound_population, p2_bound_summary,
                                 p2_bound_terms, pool_terms)

CONFIG = dataclasses.replace(SMOKE, bootstrap_resamples=40)
LEVELS = np.array([0.005, 0.01, 0.02, 0.05])
NU11 = 2.0 ** ((np.arange(11) - 5) / 2.0)  # distinct, geometric: median / mean = 0.582
TOL = 1e-12
SYSTEM = "lorenz63"  # the system label of the V7 bootstrap generators


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
    out = v7_efficiency(LEVELS, _exact(LEVELS, NU11), NU11, CONFIG, SYSTEM)
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

    low = v7_efficiency(LEVELS, _exact(LEVELS, NU11, 0.85), NU11, CONFIG, SYSTEM)
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
        out = v7_efficiency(levels, deltas, NU11, CONFIG, SYSTEM)
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
    out = v7_efficiency(LEVELS, deltas, NU11, CONFIG, SYSTEM)
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
    out = v7_efficiency(levels, deltas, nu, CONFIG, SYSTEM)
    assert out["efficiency_median_by_noise"]["0.01"] == pytest.approx(1.0, abs=TOL)
    assert out["efficiency_median_by_noise"]["0.02"] == pytest.approx(1.0, abs=TOL)
    assert out["pass"] is True

    exponents = np.array([-0.5, 0.0, 0.05, 0.1, 3.0])
    deltas = _exact(levels, nu) * (levels[None, :] / 0.01) ** exponents[:, None]
    out = v7_efficiency(levels, deltas, nu, CONFIG, SYSTEM)
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
        out = v7_efficiency(LEVELS, _exact(LEVELS, NU11, factor), NU11, CONFIG, SYSTEM)
        assert out["pass"] is expected, factor
        assert all(v is expected for v in out["efficiency_pass_by_noise"].values()), factor
        assert out["slope_pass"] is True


def test_v7_band_edges_are_inside_exactly() -> None:
    """An efficiency of exactly 1.1 or exactly 0.9 passes: the band [0.9, 1.1] is closed.

    Reference: v3 E0 and DEC-0008 A1 (closed band), written out. Levels (0.25, 0.5) and nu = 1:
    delta = c rho with c the float64 nearest to 1.1 (or 0.9). Multiplying by 0.25 or 0.5 is
    exact in binary (a power of two only shifts the exponent), and so is the division by
    rho nu back, so the ratio is bit-for-bit the double that the literal 1.1 (0.9) denotes in
    the comparison; the median of identical values is that double. A strict inequality would
    fail this test. Exact decisions, no tolerance. The slope is 1 up to about 1e-16, far from
    its edges.
    """
    levels = np.array([0.25, 0.5])
    nu = np.ones(5)
    for edge in (1.1, 0.9):
        deltas = edge * levels[None, :] * nu[:, None]
        assert np.all(deltas / (levels[None, :] * nu[:, None]) == edge)  # exact, by construction
        out = v7_efficiency(levels, deltas, nu, CONFIG, SYSTEM)
        assert list(out["efficiency_median_by_noise"].values()) == [edge, edge], edge
        assert all(out["efficiency_pass_by_noise"].values()), edge
        assert out["slope_pass"] is True and out["pass"] is True, edge


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
    out = v7_efficiency(LEVELS, deltas, NU11, CONFIG, SYSTEM)
    assert out["n_nonfinite"] == 1 and out["n_states"] == 11
    assert out["pass"] is False and out["slope_pass"] is False
    assert np.isnan(out["median_slope"])

    nu = NU11.copy()
    nu[5] = -1.0
    out = v7_efficiency(LEVELS, deltas, nu, CONFIG, SYSTEM)
    assert out["n_nonfinite"] == 2 and out["pass"] is False

    for bad in (0.0, np.nan, np.inf, -1.0):
        nu = NU11.copy()
        nu[4] = bad
        out = v7_efficiency(LEVELS, base, nu, CONFIG, SYSTEM)
        assert out["n_nonfinite"] == 1 and out["pass"] is False, bad
        assert not any(out["efficiency_pass_by_noise"].values()), bad

    both = base.copy()
    both[3, 0] = np.inf
    nu = NU11.copy()
    nu[3] = 0.0
    assert v7_efficiency(LEVELS, both, nu, CONFIG, SYSTEM)["n_nonfinite"] == 1

    zero = base.copy()
    zero[7, 2] = 0.0  # delta = 0 has no logarithm: counted too
    assert v7_efficiency(LEVELS, zero, NU11, CONFIG, SYSTEM)["n_nonfinite"] == 1


def test_v7_rejects_malformed_arrays() -> None:
    """Shapes, level count and level sign are checked where the data enter (DSGN.2).

    Reference: the contract of ``v7_efficiency``: ``deltas`` is (n_states, n_levels), ``nu``
    is (n_states,), at least two distinct positive levels. Exact: each case raises ValueError.
    """
    good = _exact(LEVELS, NU11)
    with pytest.raises(ValueError):
        v7_efficiency(LEVELS, good[:, :3], NU11, CONFIG, SYSTEM)
    with pytest.raises(ValueError):
        v7_efficiency(LEVELS, good, NU11[:5], CONFIG, SYSTEM)
    with pytest.raises(ValueError):
        v7_efficiency(LEVELS[:1], good[:, :1], NU11, CONFIG, SYSTEM)
    with pytest.raises(ValueError):
        v7_efficiency(np.array([0.01, 0.01]), good[:, :2], NU11, CONFIG, SYSTEM)
    with pytest.raises(ValueError):
        v7_efficiency(np.array([-0.01, 0.02]), good[:, :2], NU11, CONFIG, SYSTEM)


def _stub_cell(est_seed: np.ndarray, nu: np.ndarray) -> SimpleNamespace:
    moments = SimpleNamespace(est_seed=est_seed)
    return SimpleNamespace(system=SYSTEM, splits={"test": SimpleNamespace(moments=moments)},
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
    assert out == v7_efficiency(LEVELS, deltas, NU11, CONFIG, SYSTEM)
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


def test_check_cp_horizon_returns_counts_under_one_key_and_keeps_the_value(monkeypatch) -> None:
    """``check_cp_horizon`` keeps its value and returns its counts under the one key ``handling``.

    Reference: the old function body, copied (``realized_horizon`` then ``kaplan_meier`` on the CP
    error minus the verification noise), evaluated on hand-planned CP errors; and the planned
    counts. ``forecast_draws`` is monkeypatched to return 4 states x 1 draw x 6 horizons with CP
    errors 0.5 (beyond theta = 0.4 from horizon 1, so every duration is 1 and the KM median is 1
    step = 1/30 Lyapunov time), a planned ``handled`` table and entry totals. Expected: value
    equal bitwise to the old expression; ``handling`` carries the column sums of the table by
    name, the totals, and the sizes (4, 1, 6). The only extra key is ``handling`` (the caller pops
    it, so no validation leaf is added). Exact.
    """
    from lpcstudy import ensemble
    from lpcstudy.oracle import realized_horizon
    from lpcstudy.statistics import kaplan_meier
    from lpcstudy.validation import check_cp_horizon

    n_states, horizon_max = 4, 6
    handled = np.arange(32, dtype=np.int64).reshape(4, 8)  # one column per DRAW_COUNTERS name
    lm_planned = (np.arange(4.0).reshape(4, 1) + 0.5, np.arange(4).reshape(4, 1),
                  np.ones((4, 1), dtype=np.int32))
    entries = {"error_clips_cp": 2, "error_clips_plp": 3, "error_clips_nonfinite": 5}

    def fake(setup, library, split, rows, unit_noise, horizons, reference_horizon=None):
        assert reference_horizon == 3
        return ensemble.DrawBatch(
            cp_err=np.full((len(rows), 1, len(horizons)), 0.5), plp_err=np.zeros((len(rows), 1, 6)),
            analog_seed_sq=None, est_seed_sq=None, distance=None, inputs=None, est_states=None,
            est_nu=None, analog_vecs=None, handled=handled, clip_entries=dict(entries),
            lm_residual=lm_planned[0], lm_accepted=lm_planned[1], lm_late=lm_planned[2])

    monkeypatch.setattr(ensemble, "forecast_draws", fake)
    setup = SimpleNamespace(noise=0.01, ctx=SimpleNamespace(embed_dim=7, spec=SimpleNamespace(dim=3)))
    verify = np.zeros((n_states, 1, horizon_max))
    out = check_cp_horizon(setup, None, np.zeros((n_states, 1, 2)), verify, horizon_max, 0.4, 30, 3)
    horizons = np.arange(1, horizon_max + 1)
    dur, ev = realized_horizon(np.full((n_states, horizon_max), 0.5) - 0.01 * verify[:, 0],
                               horizons, 0.4)
    old = kaplan_meier(dur, ev, horizon_max).median() / 30
    assert set(out) == {"cp_median_vpt_lyapunov", "handling"}
    assert np.float64(out["cp_median_vpt_lyapunov"]).tobytes() == np.float64(old).tobytes()
    info = out["handling"]
    assert info["handled"] == dict(zip(ensemble.DRAW_COUNTERS, handled.sum(axis=0).tolist()))
    assert info["clip_entries"] == entries
    assert (info["n_states"], info["n_draws"], info["n_horizons"]) == (4, 1, 6)
    # WU-0005.4: the noise level and the batch's LM arrays travel in the same dict (popped by the caller)
    assert info["noise"] == 0.01 and info["dof"] == 4  # D - m = 7 - 3
    assert all(got is planned for got, planned in zip(info["lm"], lm_planned))


# ------------------------------------------------------------------------------------------
# Theorem P2(c) verification (WU-0005.5b). Design numbers: the WU-0005.5a block of the unit file.
# ------------------------------------------------------------------------------------------
DIM = 7
KAPPA = P2C_KAPPA


def _library(vectors: np.ndarray, offset: bool = False, cls: type | None = None
             ) -> AnalogLibrary:
    """An ``AnalogLibrary`` over ``vectors`` (time index = row), optionally a mutant class."""
    cls = cls or (_OffsetLibrary if offset else AnalogLibrary)
    return cls(indices=np.arange(len(vectors)), noisy_series=np.zeros(1), tree=cKDTree(vectors))


class _OffsetLibrary(AnalogLibrary):
    """Mutant: ``analog_vectors`` returns the vector next to the retrieved one (an indexing bug)."""

    def analog_vectors(self, lib_idx: np.ndarray) -> np.ndarray:
        last = len(self.tree.data) - 1
        return self.tree.data[np.minimum(lib_idx - self.indices[0] + 1, last)].mean(axis=1)


def _chi_integral(power: int, offset: float, lower: float) -> float:
    """``int_lower^inf (offset + x)^power f_D(x) dx`` by ``quad`` (the chi density, log form)."""
    def integrand(x: float) -> float:
        if x <= 0:
            return 0.0
        log_density = ((DIM - 1) * np.log(x) - x * x / 2 - (DIM / 2 - 1) * np.log(2)
                       - special.gammaln(DIM / 2))
        return (offset + x) ** power * np.exp(log_density)

    cuts = sorted({lower, max(lower, np.sqrt(DIM - 1)), max(lower, 12.0), max(lower, 40.0)})
    total = sum(integrate.quad(integrand, a, b, epsabs=0, epsrel=1e-13, limit=200)[0]
                for a, b in zip(cuts[:-1], cuts[1:]))
    return total + integrate.quad(integrand, cuts[-1], np.inf, epsabs=0, epsrel=1e-13,
                                  limit=200)[0]


@pytest.mark.parametrize("rho", [1.0, 0.02])
def test_p2_population_bound_matches_quadrature(rho: float) -> None:
    """U1: B_inf in closed form equals the quadrature of the chi density (v3 Theorem P2(c)).

    Reference: ``scipy.integrate.quad`` of ``(r1/rho + x)^2 f_D(x)`` on ``[Delta/(2 rho), inf)``
    with ``D = 7``, ``epsrel = 1e-13`` (its own error estimate is at most 8e-14), so
    ``B_inf = 4 / D * integral``. Grid ``(r1/rho, Delta/rho)`` in {0, 1, 10} x {0, 0.5, 2, 8,
    16}; 16 puts the far tail (Q about 1e-10) in. Tolerance: relative 1e-12 (WU-0005.5a, A2: the
    gamma-function ratio and ``gammaincc`` have about 1e-15 relative error; observed worst 2.5e-15).
    """
    for a in (0.0, 1.0, 10.0):
        for d in (0.0, 0.5, 2.0, 8.0, 16.0):
            got, _ = p2_bound_population(np.array([a * rho]), np.array([d * rho]), rho, DIM)
            want = 4.0 / DIM * _chi_integral(2, a, d / 2)
            assert got[0] == pytest.approx(want, rel=1e-12, abs=0), (a, d)


def test_p2_population_variance_matches_quadrature_and_simulation() -> None:
    """U1b: the variance of one per-draw term, by quadrature and by simulation (M2).

    Reference 1: ``Var(b) = (4/D)^2 (I4 - I2^2)`` with ``I_p = int (a + x)^p f_D`` by ``quad``, on
    ``Delta/rho`` in {0, 0.5, 2}. Tolerance: relative 1e-10 (the difference loses about a factor
    ``I4 / Var <= 80`` of the 1e-13 quadrature accuracy).
    Reference 2: 20000 replicates of ``B_M`` at ``M = 50`` (rho = 0.1, r1 = 0.5, Delta/rho = 2,
    ``default_rng(50059)``), ``B_M = 4 mean (r1 + ||eta||)^2 1{||eta|| >= Delta/2} / (rho^2 D)``.
    The mean of ``B_M`` is ``B_inf`` with standard error ``sqrt(Var(b) / (M R))`` (tolerance 4 SE);
    the sd of ``B_M`` is ``sqrt(Var(b) / M)`` with relative error about 1% (tolerance 5%).
    """
    for a in (0.0, 1.0, 10.0):
        for d in (0.0, 0.5, 2.0):
            _, var = p2_bound_population(np.array([a]), np.array([d]), 1.0, DIM)
            want = (4.0 / DIM) ** 2 * (_chi_integral(4, a, d / 2) - _chi_integral(2, a, d / 2) ** 2)
            assert var[0] == pytest.approx(want, rel=1e-10, abs=0), (a, d)

    rho, r1, delta, m, reps = 0.1, 0.5, 0.2, 50, 20_000
    b_inf, var = p2_bound_population(np.array([r1]), np.array([delta]), rho, DIM)
    eta = np.linalg.norm(np.random.default_rng(50059).standard_normal((reps, m, DIM)) * rho,
                         axis=-1)
    b_m = 4 / (rho**2 * DIM) * np.mean((r1 + eta) ** 2 * (eta >= delta / 2), axis=1)
    assert abs(b_m.mean() - b_inf[0]) <= 4 * np.sqrt(var[0] / (m * reps))
    assert b_m.std() / np.sqrt(var[0] / m) == pytest.approx(1.0, abs=0.05)


def test_chi_tail_moments_at_zero_threshold() -> None:
    """U1c: with no threshold the tail moments are 1 and D (the chi_D moments), Delta = 0 (ties).

    Reference: ``E chi^0 = 1`` and ``E chi^2 = D``. Tolerance 1e-14 (observed exactly 0).
    """
    assert chi_tail_moment(0, 0.0, DIM) == pytest.approx(1.0, abs=1e-14)
    assert chi_tail_moment(2, 0.0, DIM) == pytest.approx(float(DIM), abs=1e-14)


def _stable_library(rng: np.random.Generator, dyadic: bool) -> np.ndarray:
    """x = 0 in R^7; X_1 = 0.5 e_1; 40 other vectors at distance >= 1.5 (Delta >= 1)."""
    nearest = np.zeros(DIM)
    nearest[0] = 0.5
    others: list[np.ndarray] = []
    while len(others) < 40:
        v = np.round(rng.uniform(-4, 4, DIM) * 16) / 16  # multiples of 2**-4
        if np.linalg.norm(v) >= 1.5:
            others.append(v)
    lib = np.vstack([nearest, *others])
    if dyadic:
        return lib
    generic = rng.standard_normal(lib.shape)
    generic *= np.linalg.norm(lib, axis=1, keepdims=True) \
        / np.linalg.norm(generic, axis=1, keepdims=True)  # the same distances, generic coordinates
    return generic


def test_p2_stable_case_is_exact_on_dyadic_library() -> None:
    """U2: when no draw can switch the retrieval, A = B = N = 0 exactly (ROADMAP, P2(a)).

    Reference: P2(a), by construction. x = 0, X_1 at r1 = 0.5, every other vector at distance
    >= 1.5, so Delta >= 1; rho = 0.02, M = 200, ``default_rng(50055)``; the premise
    ``max ||eta|| < Delta / 2`` is asserted. Coordinates are multiples of 2**-4, so the sum of 200
    equal copies and its division by 200 are exact: the centred values are exactly 0 and
    ``N == 0.0`` with no tolerance. ``A == B == 0.0`` because every ``Y_r`` is bitwise ``X_1``.
    """
    rho, m = 0.02, 200
    lib = _stable_library(np.random.default_rng(50054), dyadic=True)
    noise = np.random.default_rng(50055).standard_normal((1, m, DIM))
    t = p2_bound_terms(_library(lib), np.zeros((1, DIM)), noise, rho)
    assert np.linalg.norm(rho * noise, axis=-1).max() < t["delta"][0] / 2  # the premise
    assert t["n_switch"][0] == 0
    assert (t["a_m"][0], t["b_m"][0], t["b_sw"][0], t["n_m"][0]) == (0.0, 0.0, 0.0, 0.0)
    assert not t["violation"][0]
    assert t["n_p2a"][0] == t["n_triangle"][0] == t["n_consistency"][0] == 0


def test_p2_stable_case_generic_coordinates_is_zero_up_to_centring_round_off() -> None:
    """U3: the same design with generic coordinates: A = B = 0 exactly, N <= tau_N (added check).

    Reference: P2(a) as in U2 (premise ``max eta < Delta/2 - max s`` asserted), the library
    rescaled to the same distances. ``A == B == 0.0`` still (``Y_r`` is bitwise ``X_1``), but
    ``N`` is the round-off of the mean of 200 equal vectors, which is not 0. Tolerance
    ``tau_N = M u max|Y| / rho`` per state: the first-order bound on the centring error of the
    sequential mean (WU-0005.5a, M4); observed 1.5e-14 against 5e-13. This is an added check;
    U2 keeps the exact zero.
    """
    rho, m = 0.02, 200
    lib = _stable_library(np.random.default_rng(50054), dyadic=False)
    noise = np.random.default_rng(50055).standard_normal((1, m, DIM))
    t = p2_bound_terms(_library(lib), np.zeros((1, DIM)), noise, rho)
    eta = np.linalg.norm(rho * noise, axis=-1)
    assert eta.max() < t["delta"][0] / 2 - KAPPA * (t["r2"][0] + eta.max())  # the slack-safe premise
    assert t["n_switch"][0] == 0
    assert (t["a_m"][0], t["b_m"][0]) == (0.0, 0.0)
    assert t["tau"][0] == pytest.approx(m * UNIT_ROUNDOFF * np.abs(lib[0]).max() / rho, rel=1e-12)
    assert t["n_m"][0] <= t["tau"][0]
    assert not t["violation"][0]


def _collinear_states(r1_over_rho: float, seed: int, rho: float = 0.1, m: int = 200,
                      cls: type | None = None) -> list[tuple[float, dict[str, np.ndarray], np.ndarray]]:
    """300 collinear states: X_1 = r1 e_1, X_2 = -(r1 + Delta) e_1, 20 distractors far away.

    Delta / rho in {0.5, 1, 2, 4, 8, 16}, 50 states each. The query is x = 0, so X_2 is retrieved
    exactly when ``q_1 < -Delta / 2`` (the worst case of P2(a)); distractors lie at distance
    ``r1 + Delta + 20 rho``, more than twice ``max ||eta||`` away. Returns ``(Delta/rho, terms,
    unit noise)`` per state.
    """
    rng = np.random.default_rng(seed)
    out = []
    for grid in (0.5, 1, 2, 4, 8, 16):
        for _ in range(50):
            r1, delta = r1_over_rho * rho, grid * rho
            first, second = np.zeros(DIM), np.zeros(DIM)
            first[0], second[0] = r1, -(r1 + delta)
            dirs = rng.standard_normal((20, DIM))
            dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
            lib = np.vstack([first, second, dirs * (r1 + delta + 20 * rho)])
            noise = rng.standard_normal((1, m, DIM))
            out.append((grid, p2_bound_terms(_library(lib, cls=cls), np.zeros((1, DIM)), noise, rho),
                        noise))
    return out


def test_p2_chain_holds_on_switching_states_against_closed_forms() -> None:
    """U4: 300 collinear switching states: the chain holds and N, A match closed forms.

    Reference (independent of the code): with two retrievable vectors at distance
    ``L = 2 r1 + Delta`` and ``K`` = the draws with ``rho z_1 < -Delta/2`` (X_2 is closer iff
    ``q_1 < -Delta/2``, derived from the squared distances), ``p = K/M``:
    ``N^2 = L^2 p (1 - p) / (rho^2 D)``, ``A = L^2 p / (rho^2 D)``, ``||Ybar - X_1||^2 /
    (rho^2 D) = L^2 p^2 / (rho^2 D)`` (Huygens: ``N^2 = A - centre``). Design: rho = 0.1,
    r1 = 5 rho, ``default_rng(50056)`` (WU-0005.5a, M7). Tolerances (M4/M7): ``|N - N_ref| <=
    tau_N + kappa N_ref``, ``|A - A_ref| <= kappa A_ref``, ``|N^2 - (A - centre)| <= tau_N^2 + 2
    kappa A``; the centre term is also compared with ``L^2 p^2 / (rho^2 D)`` at relative 1e-9 (absolute
    1e-24 for p = 0, where it is the square of a centring round-off of at most 1e-16). Justification of
    the 1e-9: the centring error of the mean is at most M u max|Y| = 200 * 1.1e-16 * 1.1 = 2.4e-14
    per coordinate, against ``p L >= 0.005`` for ``p >= 1/200`` (L >= 1.05), so the relative error
    of the squared centre term is about 1e-11 and 1e-9 leaves a margin of about 100
    (observed errors are at most 0.004 of the other tolerances). Premises asserted: at least 100
    switching states, 40 states with B > 0 and A == 0, 40 with B == 0, and no distractor retrieved
    (``n_switch == K`` exactly). Violations: 0.
    """
    rho, m = 0.1, 200
    states = _collinear_states(5.0, 50056, rho, m)
    n_switching = n_b_only = n_zero = 0
    for grid, t, noise in states:
        delta = grid * rho
        length = 2 * 5.0 * rho + delta
        k = int(np.sum(rho * noise[0, :, 0] < -delta / 2))
        p = k / m
        assert t["n_switch"][0] == k  # no distractor retrieved, the switch count is the closed one
        assert not t["violation"][0]
        assert t["n_p2a"][0] == t["n_triangle"][0] == t["n_consistency"][0] == 0
        n_ref = np.sqrt(length**2 * p * (1 - p) / (rho**2 * DIM))
        a_ref = length**2 * p / (rho**2 * DIM)
        assert abs(t["n_m"][0] - n_ref) <= t["tau"][0] + KAPPA * n_ref
        assert abs(t["a_m"][0] - a_ref) <= KAPPA * a_ref
        assert abs(t["n_m"][0] ** 2 - (t["a_m"][0] - t["centre"][0])) \
            <= t["tau"][0] ** 2 + 2 * KAPPA * t["a_m"][0]
        # rel 1e-9: about 100 times the round-off of the centred mean (see the docstring)
        assert t["centre"][0] == pytest.approx(length**2 * p**2 / (rho**2 * DIM),
                                               rel=1e-9, abs=1e-24)
        n_switching += k > 0
        n_b_only += (t["b_m"][0] > 0) and (t["a_m"][0] == 0.0)
        n_zero += t["b_m"][0] == 0.0
    assert n_switching >= 100 and n_b_only >= 40 and n_zero >= 40
    assert len(states) == 300


def test_p2_bound_is_tight_enough_to_catch_a_factor_two() -> None:
    """U5: power. With r1 = 50 rho the per-draw and per-state bounds are nearly attained.

    Reference: the same collinear design as U4 with r1 = 50 rho (``default_rng(50057)``). Premises
    (WU-0005.5a, A5), fixed before the result: the largest per-draw ratio ``||Y_r - X_1|| /
    (2 (r1 + eta_r))`` is at least 0.9, so a triangle bound with constant 1 instead of 2 (a
    factor 4 in B) would fail (1.8 > 1); and the largest state-level ``A_M / B_M`` is at least 0.3,
    which exceeds 1/4, so a bound ``B/4`` would fail. The chain holds (0 violations).
    """
    states = _collinear_states(50.0, 50057)
    assert not any(t["violation"][0] for _, t, _ in states)
    assert max(t["max_ratio"][0] for _, t, _ in states) >= 0.9
    assert max(t["a_m"][0] / t["b_m"][0] for _, t, _ in states if t["b_m"][0] > 0) >= 0.3


def test_p2_check_detects_an_indexing_defect() -> None:
    """The chain catches an off-by-one in ``analog_vectors`` (mutation test, WU-0005.5a M3).

    Reference: the U4 design (Delta/rho = 2) with a library whose ``analog_vectors`` returns the
    next vector. The retrieved vectors are then not the nearest ones: the consistency check
    (``||q - Y||`` against the tree distance) fails on every draw, and the state is a violation.
    The honest library on the same data has none.
    """
    rho, m = 0.1, 200
    rng = np.random.default_rng(50060)
    delta, r1 = 2 * rho, 5 * rho
    first, second = np.zeros(DIM), np.zeros(DIM)
    first[0], second[0] = r1, -(r1 + delta)
    dirs = rng.standard_normal((20, DIM))
    dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
    lib = np.vstack([first, second, dirs * (r1 + delta + 20 * rho)])
    noise = rng.standard_normal((1, m, DIM))
    good = p2_bound_terms(_library(lib), np.zeros((1, DIM)), noise, rho)
    bad = p2_bound_terms(_library(lib, offset=True), np.zeros((1, DIM)), noise, rho)
    assert not good["violation"][0]
    assert bad["violation"][0] and bad["n_consistency"][0] == m


class _SecondNearestLibrary(AnalogLibrary):
    """Mutant: ``query`` returns the second nearest vector, with its own true distance."""

    def query(self, vectors: np.ndarray, n_analogs: int) -> tuple[np.ndarray, np.ndarray]:
        dist, pos = self.tree.query(vectors, k=2)
        return self.indices[pos[:, 1:2]], dist[:, 1:2]


def test_p2_chain_items_fire_on_planted_defects(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mutation test (review R1): p2a, triangle, A_le_B, N_le_A and the headline each fire.

    Reference: closed forms of the collinear design (x = 0, X_1 = r1 e_1, X_2 = -(r1 + Delta) e_1,
    distractors far away). The unmutated run on each design must report 0 violations (so the
    test is not vacuous); the integer counts below are exact, with no tolerance.

    (a) U4 design (``default_rng(50056)``, r1 = 5 rho), a library whose ``query`` returns the
    second nearest vector with its true distance: ``consistency`` passes (0), while on every draw
    with ``eta < Delta/2`` the nearest is X_1, the retrieved vector is X_2 and ``||X_2 - X_1|| =
    2 r1 + Delta > 2 (r1 + eta)``: ``n_p2a`` and ``n_triangle`` both equal the count of draws with
    ``rho ||z|| < Delta/2`` (such a draw has ``rho z_1 > -Delta/2``, so X_1 is the nearest). On the
    50 states with Delta/rho = 16, B = 0 < A, so ``A_le_B`` fires in all 50.

    (b) U5 design (``default_rng(50057)``, r1 = 50 rho), N multiplied by f = 2 and by f = 3 through
    patching ``retrieval_spread``. With p = K/M the switching fraction, ``N^2 = L^2 p (1-p) /
    (rho^2 D)`` and ``A = L^2 p / (rho^2 D)``, so ``f^2 N^2 > A`` exactly when ``K > 0`` and
    ``f^2 (M - K) > M`` (integers): ``N_le_A`` fires in exactly those states (f = 2: ``0 < K <
    150``). The headline ``f^2 N^2 > B`` fires in exactly the states where the closed form says so
    (B written out from ``rho ||z||``). On this design the largest ``N^2 / B`` is 0.228 (the
    0.46 of U5 is the largest ``A / B``), below 1/4, so f = 2 is seen by ``N_le_A`` only
    (the headline count is exactly 0), and f = 3 (9 * 0.228 > 1) by the headline too.
    """
    rho, m = 0.1, 200
    honest = _collinear_states(5.0, 50056, rho, m)
    assert not any(t["violation"][0] for _, t, _ in honest)
    mutant = _collinear_states(5.0, 50056, rho, m, cls=_SecondNearestLibrary)
    n_p2a = n_triangle = n_a_le_b = 0
    for grid, t, noise in mutant:
        delta = grid * rho
        expected = int(np.sum(rho * np.linalg.norm(noise[0], axis=-1) < delta / 2))
        assert t["n_p2a"][0] == t["n_triangle"][0] == expected
        assert t["n_consistency"][0] == 0
        # the reported flag is the OR of the checks: dropping a term from it is caught here
        assert bool(t["violation"][0]) == (expected > 0 or bool(t["fail_a_le_b"][0])
                                           or bool(t["fail_n_le_a"][0])
                                           or bool(t["fail_headline"][0]))
        if grid == 16:
            assert t["fail_a_le_b"][0] and t["violation"][0]
            n_a_le_b += 1
        n_p2a += expected
    assert n_a_le_b == 50 and n_p2a > 0

    honest5 = _collinear_states(50.0, 50057, rho, m)
    assert not any(t["violation"][0] for _, t, _ in honest5)
    from lpcstudy import validation
    original = validation.retrieval_spread
    heads = {}
    for factor in (2, 3):
        monkeypatch.setattr(validation, "retrieval_spread",
                            lambda y, noise, f=factor: f * original(y, noise))
        scaled = _collinear_states(50.0, 50057, rho, m)
        want_a = want_head = got_a = got_head = 0
        for grid, t, noise in scaled:
            delta, length = grid * rho, 2 * 50.0 * rho + grid * rho
            k = int(np.sum(rho * noise[0, :, 0] < -delta / 2))
            eta = rho * np.linalg.norm(noise[0], axis=-1)
            b_ref = 4 / (rho**2 * DIM) * np.mean((50.0 * rho + eta) ** 2 * (eta >= delta / 2))
            n_sq = factor**2 * length**2 * (k / m) * (1 - k / m) / (rho**2 * DIM)  # (f N_ref)^2
            fires_a = k > 0 and factor**2 * (m - k) > m  # f^2 N^2 > A  <=>  f^2 (1 - p) > 1
            assert bool(t["fail_n_le_a"][0]) == fires_a
            assert bool(t["fail_headline"][0]) == (n_sq > b_ref)
            # only N is mutated, so the violation flag is true exactly when a check fires
            assert bool(t["violation"][0]) == (fires_a or bool(n_sq > b_ref))
            want_a += fires_a
            want_head += n_sq > b_ref
            got_a += bool(t["fail_n_le_a"][0])
            got_head += bool(t["fail_headline"][0])
        assert (got_a, got_head) == (want_a, want_head) and want_a > 0
        heads[factor] = want_head
    # The largest N^2/B on this design is 0.228 < 1/4 (the reviewer's 0.46 is the largest A/B), so
    # a factor 2 is seen by N_le_A only; a factor 3 (9 * 0.228 > 1) is seen by the headline too.
    assert heads[2] == 0 and heads[3] > 0


def _random_case():
    """A random library, 25 clean queries and M = 20 draws at rho = 0.3 (switching is common)."""
    rng = np.random.default_rng(50058)
    lib = rng.standard_normal((60, DIM)) * 1.3
    clean = rng.standard_normal((25, DIM)) * 1.3
    return lib, clean, rng.standard_normal((25, 20, DIM)), 0.3


def test_p2_terms_match_brute_force() -> None:
    """The terms equal an exhaustive-search computation (independent algorithm).

    Reference: ``np.argmin`` over all pairwise distances for the retrieval, ``np.sort`` for r1 and
    r2, ``eta = rho ||z||`` (not ``q - x``) and the formulas of Theorem P2(c) written out. Premises
    asserted so the references are unambiguous: every draw's best and second-best distances
    differ by more than 1e-9 and no draw lies within 1e-9 of the threshold ``Delta/2``.
    Tolerance: indices exact; real quantities relative 1e-12 (sums of at most 20 positive terms
    of distances with relative round-off about 6u = 7e-16, squared).
    """
    lib, clean, z, rho = _random_case()
    n, m, _ = z.shape
    t = p2_bound_terms(_library(lib), clean, z, rho)

    d_clean = np.sort(np.linalg.norm(clean[:, None, :] - lib[None], axis=-1), axis=1)
    r1, r2 = d_clean[:, 0], d_clean[:, 1]
    nearest = np.argmin(np.linalg.norm(clean[:, None, :] - lib[None], axis=-1), axis=1)
    q = clean[:, None, :] + rho * z
    d_q = np.linalg.norm(q[:, :, None, :] - lib[None, None], axis=-1)
    gaps = np.diff(np.sort(d_q, axis=-1)[..., :2], axis=-1)
    assert gaps.min() > 1e-9
    chosen = np.argmin(d_q, axis=-1)
    y = lib[chosen]
    eta = rho * np.linalg.norm(z, axis=-1)
    assert np.abs(eta - (r2 - r1)[:, None] / 2).min() > 1e-9

    c = 1 / (rho**2 * DIM)
    sw = chosen != nearest[:, None]
    n_ref = np.sqrt(np.mean(np.sum((y - y.mean(axis=1, keepdims=True)) ** 2, axis=-1), axis=-1)
                    / DIM) / rho
    a_ref = c * np.mean(np.sum((y - lib[nearest][:, None, :]) ** 2, axis=-1), axis=-1)
    sq = (r1[:, None] + eta) ** 2
    b_ref = 4 * c * np.mean(sq * (eta >= (r2 - r1)[:, None] / 2), axis=-1)
    bsw_ref = 4 * c * np.mean(sq * sw, axis=-1)
    assert sw.sum() > 100  # switching is common here
    np.testing.assert_array_equal(t["n_switch"], sw.sum(axis=1))
    for key, ref in (("r1", r1), ("r2", r2), ("n_m", n_ref), ("a_m", a_ref), ("b_m", b_ref),
                     ("b_sw", bsw_ref), ("b_plus", b_ref)):
        np.testing.assert_allclose(t[key], ref, rtol=1e-12, atol=0, err_msg=key)
    assert not t["violation"].any() and t["n_band"].sum() == 0

    out = p2_bound_summary(pool_terms([t]), rho, m, DIM)
    positive = b_ref > 0
    assert out["n_states"] == n and out["n_violations"] == 0
    assert out["n_switching_states"] == int(sw.any(axis=1).sum())
    assert out["n_zero_bound_states"] == int((~positive).sum())
    assert out["tightness"]["N_over_sqrt_B"]["median"] == pytest.approx(
        np.median(n_ref[positive] / np.sqrt(b_ref[positive])), rel=1e-12)
    assert out["tightness"]["N_over_sqrt_B"]["max"] == pytest.approx(
        np.max(n_ref[positive] / np.sqrt(b_ref[positive])), rel=1e-12)
    assert out["noise_second_moment"]["value"] == pytest.approx(
        np.mean(np.sum(z**2, axis=-1)) / DIM, rel=1e-12)
    assert out["noise_second_moment"]["se"] == pytest.approx(np.sqrt(2 / (n * m * DIM)), rel=1e-12)


def test_p2_check_reports_same_draws_and_refuses_bad_input() -> None:
    """``check_p2_bound`` compares N bitwise with the cell's ``noise_sens`` (P1) and checks input.

    Reference: the bitwise-equal array is accepted, the same array with one entry moved by one ulp
    is not (exact comparison, no tolerance; PRIME.2). A missing comparison is ``None`` (not
    compared), not ``True``. Bad input raises (PRIME.4): a non-positive noise, a one-vector
    library, mismatched shapes.
    """
    lib, clean, z, rho = _random_case()
    library = _library(lib)
    n_m = p2_bound_terms(library, clean, z, rho)["n_m"]
    same = check_p2_bound(library, {"test": clean}, {"test": z}, rho, {"test": n_m.copy()})
    assert same["same_draws_identical"] is True and same["splits"] == {"test": 25}
    moved = n_m.copy()
    moved[3] = np.nextafter(moved[3], np.inf)
    assert check_p2_bound(library, {"test": clean}, {"test": z}, rho,
                          {"test": moved})["same_draws_identical"] is False
    assert check_p2_bound(library, {"test": clean}, {"test": z}, rho)["same_draws_identical"] is None
    with pytest.raises(ValueError, match="positive"):
        p2_bound_terms(library, clean, z, 0.0)
    with pytest.raises(ValueError, match="two vectors"):
        p2_bound_terms(_library(lib[:1]), clean, z, rho)
    with pytest.raises(ValueError, match="shapes"):
        p2_bound_terms(library, clean[:, :5], z, rho)
