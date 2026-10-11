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
    (``n_states``, also when it sits below a counted key such as ``zero_variance_corr``: it is a
    size, fix R1 of WU-0002.11b) are not copied, while ``n_zero_difference`` is since WU-0002.11b; a key holding the dotted rho ``0.01`` keeps its dot
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
                                                              "n_states": 60,
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
    and blocks. A V3 block marks its PLP counters inert, and the two LM counters too (R3: V3 computes
    PLP and does not use it). Exact strings.
    """
    import logging

    from lpcstudy.experiments import log_handling
    from lpcstudy.pipeline import ALL_COUNTERS, CELL_COUNTERS, CELL_DENOMINATORS

    counts = dict.fromkeys(CELL_COUNTERS, 0)
    counts.update(error_clips_cp=4, gain_floor=2)
    dens = dict.fromkeys(CELL_DENOMINATORS, 0)
    dens.update(error_entries=1200, eval_draws=10)
    v3 = dict.fromkeys(CELL_COUNTERS, 0)
    v3.update(error_clips_plp=1, lm_nonfinite_cost=2, lm_nonfinite_jacobian=3)  # WU-0005.4 (R3)
    dens["estimates"] = 7
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
        "[inert: V3 uses CP only]",
        "handling lorenz63 V3-cp-horizon: lm_nonfinite_cost = 2 of 7 estimates "
        "[inert: V3 uses CP only]",
        "handling lorenz63 V3-cp-horizon: lm_nonfinite_jacobian = 3 of 7 estimates "
        "[inert: V3 uses CP only]"]
    assert infos == ["handling lorenz63: 5 nonzero counters in 3 blocks"]
    assert set(ALL_COUNTERS) >= {"error_clips_cp", "gain_floor"}


# ----------------------------------------------------------- WU-0005.5: P2(c) wiring
def _p2c_fixture():
    """A fake study, core cell and library for ``p2c_verification`` (k = 1, D = 7, 3 splits)."""
    from scipy.spatial import cKDTree

    from lpcstudy.ensemble import AnalogLibrary, retrieval_spread

    rng = np.random.default_rng(50061)
    series = rng.standard_normal(400)
    delay, dim, rho, draws = 3, 7, 0.4, 10
    splits = {"construction": np.arange(20, 60), "calibration": np.arange(60, 90),
              "test": np.arange(90, 120)}
    vectors = rng.standard_normal((200, dim))
    library = AnalogLibrary(indices=np.arange(200), noisy_series=np.zeros(1),
                            tree=cKDTree(vectors))
    ctx = SimpleNamespace(eval_clean=series, split_indices=splits, delay=delay, embed_dim=dim)
    noises = {name: rng.standard_normal((len(t), draws, dim)) for name, t in splits.items()}
    seen = []

    def unit_noise(context, split, purpose, n_draws, width):
        seen.append((split, purpose, n_draws, width))
        return noises[split]

    study = SimpleNamespace(config=SimpleNamespace(n_oracle_draws=draws), unit_noise=unit_noise)
    sens = {}
    for name, times in splits.items():
        # Independent reference: the delay vector written out, the retrieval by exhaustive search.
        clean = np.stack([series[times - j * delay] for j in range(dim)], axis=1)
        queries = clean[:, None, :] + rho * noises[name]
        nearest = np.argmin(np.linalg.norm(queries[:, :, None, :] - vectors[None, None], axis=-1),
                            axis=-1)
        sens[name] = retrieval_spread(vectors[nearest], rho)
    core = SimpleNamespace(
        system="toy", noise=rho, library_size=200, ctx=ctx, setup=SimpleNamespace(n_analogs=1),
        splits={name: SimpleNamespace(moments=SimpleNamespace(noise_sens=sens[name]))
                for name in splits})
    return study, core, library, sens, seen


def test_p2c_verification_uses_the_core_draws_and_logs_a_mismatch(caplog) -> None:
    """``p2c_verification`` takes the clean queries and oracle noise of every split and logs defects.

    Reference: the clean delay vectors written out by indexing (``series[t - j tau]``) and the
    core ``noise_sens`` computed by exhaustive nearest-neighbor search on a toy library
    (200 vectors in R^7, rho = 0.4, M = 10, 3 splits of 40, 30 and 30 states): the check must
    report ``same_draws_identical`` (bitwise), no violation, 100 states, the cell description,
    and ask ``unit_noise`` for the ``"oracle"`` draws of each split. With one ``noise_sens`` entry
    moved by an ulp it must report ``False`` and write one WARNING naming the defect (PRIME.4).
    The toy library is far from the exact-arithmetic limits, so any violation would be a defect.
    k = 2 is refused. Exact comparisons.
    """
    import logging

    from lpcstudy.experiments import p2c_verification

    study, core, library, sens, seen = _p2c_fixture()
    with caplog.at_level(logging.INFO, logger="lpcstudy"):
        out = p2c_verification(study, core, library)
    assert out["same_draws_identical"] is True and out["n_violations"] == 0
    assert out["n_states"] == 100 and out["splits"] == {"construction": 40, "calibration": 30,
                                                        "test": 30}
    assert out["cell"] == {"noise": 0.4, "n_lib": 200, "n_analogs": 1, "draws": 10,
                           "splits": ["construction", "calibration", "test"]}
    assert seen == [(name, "oracle", 10, 7) for name in ("construction", "calibration", "test")]
    assert not [r for r in caplog.records if r.levelno >= logging.WARNING]

    sens["test"] = sens["test"].copy()
    sens["test"][2] = np.nextafter(sens["test"][2], np.inf)
    core.splits["test"].moments.noise_sens = sens["test"]
    caplog.clear()
    with caplog.at_level(logging.INFO, logger="lpcstudy"):
        bad = p2c_verification(study, core, library)
    assert bad["same_draws_identical"] is False
    warnings_ = [r.getMessage() for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warnings_) == 1 and warnings_[0].startswith("toy P2(c) verification FAILED")

    core.setup.n_analogs = 2
    with pytest.raises(ValueError, match="single nearest analog"):
        p2c_verification(study, core, library)


def test_sweep_subset_slices_lm_arrays_by_rows_only() -> None:
    """WU-0005.4 (L6): ``_sweep_subset`` keeps the first ``n_test_sweep`` rows of the LM arrays.

    Reference: direct indexing of hand arrays (entries are their own flat index). The arrays are
    horizon-free, so no column slice applies: the moments' and the draws' ``lm_*`` equal
    ``full[:4]``, shape ``(4, 2)``. Exact.
    """
    config = dataclasses.replace(SMOKE, n_test_sweep=4)
    table = np.zeros((6, 8), dtype=np.int64)
    cell = _handled_cell(table)
    residual = np.arange(12.0).reshape(6, 2)
    accepted = np.arange(12, dtype=np.int32).reshape(6, 2)
    late = (np.arange(12) % 2).astype(np.int32).reshape(6, 2)
    for holder in (cell.splits["test"].moments, cell.splits["test"].evals):
        holder.lm_residual, holder.lm_accepted, holder.lm_late = residual, accepted, late
    view = _sweep_subset(cell, config)
    for holder in (view.splits["test"].moments, view.splits["test"].evals):
        assert holder.lm_residual.tobytes() == residual[:4].tobytes()
        assert np.array_equal(holder.lm_accepted, accepted[:4])
        assert np.array_equal(holder.lm_late, late[:4]) and holder.lm_residual.shape == (4, 2)


def test_convergence_check_records_the_lm_block_of_its_forecasts(monkeypatch, tmp_path) -> None:
    """WU-0005.4 (L6): V4 summarizes the LM arrays of its own forecasts under ``V4-convergence``.

    Reference: hand values. ``forecast_draws`` is replaced by a stub returning, for global row i,
    the residual i + 0.5 and accepted i on every one of the M = 30 draws (SMOKE:
    ``convergence_draws = (10, 30)``, ``convergence_states = 10`` so 10 states, two batches of 5),
    late progress i mod 2, and ``handled`` ones. Then n = 300; the residual values 0.5..9.5 each
    occur 30 times, so the median is 5.0 (the 150th and 151st values are 4.5 and 5.5) and the p95
    is x_(285) = 9.5; accepted 0..9 gives median 4.5 and 30 zeros (0.1); late 0.5; every residual
    exceeds the dof-7 threshold 24.32 * 0.01^2 (the cell has embed_dim 10 and state dimension 3),
    so 1.0. Each ``handled`` column sums to 10. No array is kept in the
    record, and it round-trips JSON. Exact.
    """
    import json

    from lpcstudy import experiments
    from lpcstudy.ensemble import DrawBatch, DRAW_COUNTERS
    from lpcstudy.pipeline import Study

    config = SMOKE
    n_states, n_draws = config.convergence_states, max(config.convergence_draws)
    assert (n_states, n_draws) == (10, 30)
    study = Study(config, tmp_path)
    study.unit_noise = lambda *args, **kwargs: np.zeros((n_states + 5, n_draws, 7))
    monkeypatch.setattr(experiments.AnalogLibrary, "build", classmethod(lambda cls, *a, **k: None))
    rng = np.random.default_rng(3)
    errors = rng.standard_normal((n_states, n_draws, 1))

    def fake(setup, library, split, rows, unit_noise, horizons, reference_horizon=None):
        ones = np.ones((len(rows), n_draws))
        return DrawBatch(
            cp_err=errors[rows], plp_err=errors[rows] + 0.1, analog_seed_sq=None, est_seed_sq=None,
            distance=None, inputs=None, est_states=None, est_nu=None, analog_vecs=None,
            handled=np.ones((len(rows), len(DRAW_COUNTERS)), dtype=np.int64),
            clip_entries={"error_clips_cp": 0, "error_clips_plp": 0, "error_clips_nonfinite": 0},
            lm_residual=(rows + 0.5)[:, None] * ones, lm_accepted=rows[:, None] * ones.astype(int),
            lm_late=(rows % 2)[:, None] * ones.astype(int))

    monkeypatch.setattr(experiments, "forecast_draws", fake)
    cell = SimpleNamespace(system="lorenz63", label="base", noise=0.01, library_size=10_000,
                           ctx=SimpleNamespace(embed_dim=10, spec=SimpleNamespace(dim=3)), setup=None)
    experiments.convergence_check(study, cell)
    record = study._records[("lorenz63", "main")]["V4-convergence"]
    lm = record["lm"]
    assert (lm["n_estimates"], lm["median_residual"], lm["p95_residual"]) == (300, 5.0, 9.5)
    assert (lm["median_iterations"], lm["fraction_no_decrease"]) == (4.5, 0.1)
    assert (lm["fraction_late_progress"], lm["fraction_above_chi2"]) == (0.5, 1.0)
    assert lm["by_kind"]["check"] == {k: v for k, v in lm.items() if k != "by_kind"}
    assert lm["by_kind"]["oracle"]["n_estimates"] == 0 and lm["noise"] == 0.01
    assert lm["gof_dof"] == 7  # D - m = 10 - 3 (R2): a robustness-sized embedding
    assert record["counts"]["lm_nonfinite_cost"] == n_states
    assert record["denominators"]["estimates"] == lm["n_estimates"]
    assert json.loads(json.dumps(record)) == record


def test_cp_horizon_check_records_the_lm_block_of_v3(monkeypatch, tmp_path) -> None:
    """WU-0005.4 (L6): V3 records its LM summary under ``V3-cp-horizon`` and pops ``handling``.

    Reference: hand values. ``check_cp_horizon`` is replaced by a stub returning the dict that
    ``validation.check_cp_horizon`` builds (checked by its own test), with 3 states x 1 draw:
    residuals [2, 4, 6], accepted [0, 3, 6], late [0, 1, 1], noise 1.0 (threshold 18.47: none above).
    Expected: median 4, p95 x_(ceil(2.85)) = 6, median accepted 3, no decrease 1/3, late 2/3,
    above 0; the returned dict keeps the V3 value and loses ``handling``. Exact up to the
    division by 3 (1/3 and 2/3 are compared with ``==`` to the same expression).
    """
    from lpcstudy import experiments
    from lpcstudy.ensemble import DRAW_COUNTERS
    from lpcstudy.pipeline import Study

    study = Study(SMOKE, tmp_path)
    handling = {"handled": dict.fromkeys(DRAW_COUNTERS, 0),
                "clip_entries": {"error_clips_cp": 0, "error_clips_plp": 0,
                                 "error_clips_nonfinite": 0},
                "n_states": 3, "n_draws": 1, "n_horizons": 120, "noise": 1.0, "dof": 4,
                "lm": (np.array([[2.0], [4.0], [6.0]]), np.array([[0], [3], [6]]),
                       np.array([[0], [1], [1]]))}
    monkeypatch.setattr(experiments, "check_cp_horizon",
                        lambda *args, **kwargs: {"cp_median_vpt_lyapunov": 1.5,
                                                 "handling": dict(handling)})
    core = SimpleNamespace(system="lorenz63", label="base", setup=None)
    out = experiments._cp_horizon_check(study, core, None, None, None)
    assert out == {"cp_median_vpt_lyapunov": 1.5}
    lm = study._records[("lorenz63", "main")]["V3-cp-horizon"]["lm"]
    assert (lm["n_estimates"], lm["median_residual"], lm["p95_residual"]) == (3, 4.0, 6.0)
    assert (lm["median_iterations"], lm["fraction_no_decrease"]) == (3.0, 1 / 3)
    assert (lm["fraction_late_progress"], lm["fraction_above_chi2"]) == (2 / 3, 0.0)
