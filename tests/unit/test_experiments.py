"""Tests for lpcstudy.experiments: the sweep-cell restriction (WU-0002.7)."""

from __future__ import annotations

import dataclasses

from types import SimpleNamespace

import numpy as np
import pytest

from lpcstudy.config import SMOKE
from lpcstudy.ensemble import EvaluationDraws
from lpcstudy.experiments import _sweep_subset
from lpcstudy.pipeline import Cell, SplitData
from unit_helpers import _moments_from_draws


class _Oracles:
    """Stand-in for ``StateOracles``: only ``subset`` is used by ``_sweep_subset``."""

    def subset(self, rows: np.ndarray) -> "_Oracles":
        return self


def test_sweep_subset_slices_the_correlation_fields_to_the_evaluation_horizons() -> None:
    """``_sweep_subset`` restricts ``err_corr``, ``cp_constant`` and ``plp_constant`` like the rest.

    Reference: direct indexing of the hand-built full-horizon arrays (entries are their own
    flat index, so the expected block is ``full[:n_sweep][:, eval_horizons - 1]``). The
    evaluation horizons of ``SMOKE`` are (8, 15, 30, 60, 120) steps; H_ref = 30 is the third
    column, and after slicing the column of H_ref equals the original column 29 of the first
    ``n_test_sweep`` rows (the plan's E2 check). The unsliced mean fields must change the same
    way. A cell without the fields stays without them (``None``). Exact (indexing only).
    """
    config = dataclasses.replace(SMOKE, n_test_sweep=4)
    n_states, n_draws, n_hor = 6, 3, 120
    rng = np.random.default_rng(9)
    moments = _moments_from_draws(rng.standard_normal((n_states, n_draws, n_hor)),
                                  rng.standard_normal((n_states, n_draws, n_hor)))
    grid = np.arange(n_states * n_hor, dtype=float).reshape(n_states, n_hor)
    moments = dataclasses.replace(moments, err_corr=grid, cp_constant=grid % 7 == 0,
                                  plp_constant=grid % 5 == 0)
    zeros = np.zeros((n_states, 2, n_hor))
    evals = EvaluationDraws(
        horizons=moments.horizons, cp_err=zeros, plp_err=zeros, verify_noise=zeros,
        distance=np.zeros((n_states, 2)), est_nu=np.zeros((n_states, 2)),
        growth_proxy=np.zeros((n_states, 2)), gain_proxy=zeros,
        inputs=np.zeros((n_states, 2, 1)), noise_sens=np.zeros((n_states, 2)))

    def cell_of(mom) -> Cell:
        return Cell(system="lorenz63", noise=0.01, library_size=10_000, label="base", setup=None,
                    splits={"test": SplitData(mom, evals)}, oracles={"test": _Oracles()},
                    horizons=np.arange(1, n_hor + 1))

    out = _sweep_subset(cell_of(moments), config).splits["test"].moments
    cols = np.array(config.eval_horizons) - 1
    np.testing.assert_array_equal(out.horizons, config.eval_horizons)
    np.testing.assert_array_equal(out.err_corr, grid[:4][:, cols])
    np.testing.assert_array_equal(out.cp_constant, (grid % 7 == 0)[:4][:, cols])
    np.testing.assert_array_equal(out.plp_constant, (grid % 5 == 0)[:4][:, cols])
    ref = out.at(config.reference_horizon)
    assert ref == 2
    np.testing.assert_array_equal(out.err_corr[:, ref], grid[:4, config.reference_horizon - 1])
    np.testing.assert_array_equal(out.mean_cp, moments.mean_cp[:4][:, cols])

    plain = _sweep_subset(cell_of(_moments_from_draws(
        rng.standard_normal((n_states, n_draws, n_hor)),
        rng.standard_normal((n_states, n_draws, n_hor)))), config).splits["test"].moments
    assert plain.err_corr is None and plain.cp_constant is None and plain.plp_constant is None


# ---------------------------------------------------------------- WU-0002.11a: counters (DEF-0001)
def test_collect_result_counts_walks_nested_dicts_and_lists_a13() -> None:
    """A13: the walker copies every integer below a counted key, with ``/`` paths, and nothing else.

    Reference: a hand dict and the expected path map written out. Counted keys met: a plain int
    (``n_failed_resamples``), a dict of ints (``zero_variance_corr`` by rho and n_lib, with a
    nested float and a ``bool``, which are skipped), a list of dicts, an int under a list index,
    a dict whose leaves are ints and ``None`` (``degenerate_fits``). Uncounted keys
    (``n_states``) are not copied, while ``n_zero_difference`` is since WU-0002.11b; a key holding the dotted rho ``0.01`` keeps its dot
    in the path (``/`` separates). Exact paths and values; the input is not modified.
    """
    import copy

    from lpcstudy.experiments import RESULT_COUNT_KEYS, collect_result_counts

    tree = {"H1b": {"PLP": {"n_failed_resamples": 3, "n_floored": 2}, "n_states": 40,
                    "CP": {"n_dropped_resamples": 5}},
            "H1a": {"by_noise": {"0.01": {"n_exponent_at_bound": {"point": 1, "resamples": 7},
                                          "n_covariance_warnings": {"point": 0, "resamples": 9}}}},
            "H1c": {"CP": {"n_ineligible_states": 11}},
            "H3a": {"n_empty_regimes": 1, "n_degenerate_pairs": 2,
                    "n_screened_out": {"growth_nonpositive": 4}},
            "H2b": {"noise": {"n_constant_states": 6, "n_dropped_resamples": 0}},
            "H2e": {"zero_variance_corr": {"0.01": {"1000": {"cp_constant": 2, "n_nonfinite": 0,
                                                              "frac": 0.5, "flag": True}}},
                    "by_noise": [{"n_zero_difference": 9, "n_failed_resamples": 4},
                                 {"n_failed_resamples": 7}]},
            "H3b": {"degenerate_fits": {"weight_tree": 1, "horizon_tree": None},
                    "nan_resamples": 5},
            "n_nonfinite": np.int64(8)}
    before = copy.deepcopy(tree)
    got = collect_result_counts(tree)
    assert got == {"H1b/PLP/n_failed_resamples": 3, "H1b/PLP/n_floored": 2,
                   "H1b/CP/n_dropped_resamples": 5,
                   "H1a/by_noise/0.01/n_exponent_at_bound/point": 1,
                   "H1a/by_noise/0.01/n_exponent_at_bound/resamples": 7,
                   "H1a/by_noise/0.01/n_covariance_warnings/point": 0,
                   "H1a/by_noise/0.01/n_covariance_warnings/resamples": 9,
                   "H1c/CP/n_ineligible_states": 11, "H3a/n_empty_regimes": 1,
                   "H3a/n_degenerate_pairs": 2, "H3a/n_screened_out/growth_nonpositive": 4,
                   "H2b/noise/n_constant_states": 6, "H2b/noise/n_dropped_resamples": 0,
                   "H2e/by_noise/0/n_zero_difference": 9,
                   "H2e/zero_variance_corr/0.01/1000/cp_constant": 2,
                   "H2e/zero_variance_corr/0.01/1000/n_nonfinite": 0,
                   "H2e/by_noise/0/n_failed_resamples": 4, "H2e/by_noise/1/n_failed_resamples": 7,
                   "H3b/degenerate_fits/weight_tree": 1, "H3b/nan_resamples": 5,
                   "n_nonfinite": 8}
    assert all(type(v) is int for v in got.values())
    assert tree["H1b"] == before["H1b"] and tree["H2e"] == before["H2e"]
    # n_zero_difference joined the counted keys in WU-0002.11b (review R3 of lane .11a: it is a
    # product of the zero-variance convention); n_states and n_noncontiguous_states stay out.
    assert {"n_zero_difference", "n_floored", "n_dropped_resamples", "n_exponent_at_bound",
            "n_covariance_warnings", "n_constant_states", "n_empty_regimes", "n_degenerate_pairs",
            "n_ineligible_states", "n_screened_out"} <= RESULT_COUNT_KEYS
    assert "n_states" not in RESULT_COUNT_KEYS and "n_noncontiguous_states" not in \
        RESULT_COUNT_KEYS


def _handled_cell(handled: np.ndarray) -> Cell:
    """A cell whose test moments carry a planned ``handled`` array (a stand-in for run_cell's)."""
    n = len(handled)
    moments = _moments_from_draws(np.zeros((n, 2, 120)), np.zeros((n, 2, 120)))
    moments = dataclasses.replace(moments, handled=handled)
    zeros = np.zeros((n, 2, 120))
    evals = EvaluationDraws(
        horizons=moments.horizons, cp_err=zeros, plp_err=zeros, verify_noise=zeros,
        distance=np.zeros((n, 2)), est_nu=np.zeros((n, 2)), growth_proxy=np.zeros((n, 2)),
        gain_proxy=zeros, inputs=np.zeros((n, 2, 1)), noise_sens=np.zeros((n, 2)))
    return Cell(system="lorenz63", noise=0.01, library_size=10_000, label="base", setup=None,
                splits={"test": SplitData(moments, evals)}, oracles={"test": _Oracles()},
                horizons=np.arange(1, 121))


def test_v7_replacements_a14_hand_sum_and_view_invariance() -> None:
    """A14 and D1: ``V7.invariant_mean_replacements[rho]`` is the hand sum, also on a sweep view.

    Reference: hand sums of a planned ``handled`` table (entries are small distinct integers
    written out, so the column sum is read off by eye). Two noise cells: rho 0.01 with column 0
    [2, 0, 1, 3, 0, 1] (sum 7), rho 0.02 with [0, 0, 1, 0, 0, 0] (sum 1); the keys are
    ``f"{rho:g}"``. Cell 1 is the view ``_sweep_subset`` makes of a full-horizon core cell with 6
    states and the first 4 rows kept (``n_test_sweep = 4``): the rows are the first four, so the
    sum on the view is 2 + 0 + 1 + 3 = 6, and EVERY ``handled`` column of the view equals the
    column sum of the first four planned rows (the columns are horizon-free or at H_ref: D1,
    option (b)). A cell without ``handled`` raises (PRIME.4). Exact.
    """
    from lpcstudy.ensemble import DRAW_COUNTERS
    from lpcstudy.experiments import v7_replacements

    table = np.zeros((6, len(DRAW_COUNTERS)), dtype=np.int64)
    table[:, 0] = [2, 0, 1, 3, 0, 1]
    table[:, 1] = [1, 1, 0, 0, 0, 2]
    table[:, 4] = [0, 2, 0, 0, 1, 0]
    config = dataclasses.replace(SMOKE, n_test_sweep=4)
    view = _sweep_subset(_handled_cell(table), config)
    np.testing.assert_array_equal(view.splits["test"].moments.handled, table[:4])
    assert view.splits["test"].evals.handled is None  # hand-built draws carry none
    other = _handled_cell(np.array([[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 0, 0, 0]]))
    got = v7_replacements({0.01: view, 0.02: other})
    assert got == {"0.01": 6, "0.02": 1}
    assert view.splits["test"].moments.clip_entries is None
    bare = _handled_cell(table)
    bare.splits["test"].moments.handled = None
    with pytest.raises(ValueError, match="handled"):
        v7_replacements({0.01: bare})


def test_run_robustness_counts_a_failed_variant_a10(monkeypatch, tmp_path) -> None:
    """A10: a robustness variant that raises is counted once and its result entry keeps the error.

    Reference: a hand construction. A real ``Study`` (no computation at construction), its
    ``context`` replaced by a stub of dimension 3, ``core_cells`` and ``fitted`` stubbed, the
    summary functions replaced by constants, and ``run_cell`` replaced by a function that raises
    ``RuntimeError("boom")`` for the label ``misspec=0.05`` and returns a stub cell otherwise. The
    config asks for misspec level 0.05 only, no embedding or analog variants and no perturbation
    scales, so there is exactly one variant. Expected: ``failed_variants`` == 1 for the system
    (``{"lorenz63": ["misspec=0.05"]}``), ``out["misspec=0.05"] == {"error": "RuntimeError('boom')"}``,
    and ``out["base"]`` unchanged. Exact.
    """
    from lpcstudy import experiments
    from lpcstudy.pipeline import Study

    config = dataclasses.replace(SMOKE, misspec_levels=(0.05,), robustness_dims=(7,),
                                 analog_counts=(1,), perturbation_scales=())
    study = Study(config, tmp_path)
    study.core_cells["lorenz63"], study.fitted["lorenz63"] = object(), object()
    monkeypatch.setattr(study, "context", lambda system: SimpleNamespace(spec=SimpleNamespace(dim=3)))
    monkeypatch.setattr(experiments, "_variant_summary", lambda cell, rules, cfg: {"ok": True})

    def boom(system, *args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(study, "run_cell", boom)
    out = experiments.run_robustness(study, "lorenz63")
    assert out == {"base": {"ok": True}, "misspec=0.05": {"error": "RuntimeError('boom')"}}
    assert study.failed_variants == {"lorenz63": ["misspec=0.05"]}
    assert sum(len(v) for v in study.failed_variants.values()) == 1


def test_log_handling_writes_one_warning_per_nonzero_counter_a12(caplog) -> None:
    """A12: two nonzero counters give exactly two WARNING lines plus one INFO summary.

    Reference: a hand-built handling block with one cell whose counts are zero except
    ``error_clips_cp = 4`` and ``gain_floor = 2`` (denominators 1200 error entries and 10 evaluation
    draws), and one oracle split with all zeros. Expected: two WARNING records from the
    ``lpcstudy`` logger whose text names the system, the block, the counter, the count and the
    denominator (``handling lorenz63 base|rho=0.01|n_lib=10000|core: error_clips_cp = 4 of 1200
    error_entries``), nothing for a zero counter, and one INFO record with the number of lines
    and blocks. A V3 block marks its PLP counters inert. Exact strings.
    """
    import logging

    from lpcstudy.experiments import log_handling
    from lpcstudy.pipeline import ALL_COUNTERS, CELL_COUNTERS, CELL_DENOMINATORS

    counts = dict.fromkeys(CELL_COUNTERS, 0)
    counts.update(error_clips_cp=4, gain_floor=2)
    dens = dict.fromkeys(CELL_DENOMINATORS, 0)
    dens.update(error_entries=1200, eval_draws=10)
    v3 = dict.fromkeys(CELL_COUNTERS, 0)
    v3.update(error_clips_plp=1)
    handling = {"cells": {"base|rho=0.01|n_lib=10000|core": {"counts": counts, "denominators": dens},
                          "V3-cp-horizon": {"counts": v3, "denominators": dens}},
                "oracles": {"test": {"counts": {"oracle_nonfinite": 0}, "denominators": {"states": 5}}}}
    with caplog.at_level(logging.INFO, logger="lpcstudy"):
        log_handling("lorenz63", handling)
    warnings_ = [r.getMessage() for r in caplog.records if r.levelno == logging.WARNING]
    infos = [r.getMessage() for r in caplog.records if r.levelno == logging.INFO]
    assert warnings_ == [
        "handling lorenz63 base|rho=0.01|n_lib=10000|core: error_clips_cp = 4 of 1200 error_entries",
        "handling lorenz63 base|rho=0.01|n_lib=10000|core: gain_floor = 2 of 10 eval_draws",
        "handling lorenz63 V3-cp-horizon: error_clips_plp = 1 of 1200 error_entries "
        "[inert: V3 uses CP only]"]
    assert infos == ["handling lorenz63: 3 nonzero counters in 3 blocks"]
    assert set(ALL_COUNTERS) >= {"error_clips_cp", "gain_floor"}
