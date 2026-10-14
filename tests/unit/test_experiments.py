"""Tests for lpcstudy.experiments: the sweep-cell restriction (WU-0002.7)."""

from __future__ import annotations

import dataclasses
import hashlib
import struct

from types import SimpleNamespace

import numpy as np
import pytest

from lpcstudy.config import SMOKE
from lpcstudy.ensemble import EvaluationDraws
from lpcstudy.experiments import _sweep_subset, context_record, fitted_record
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


def test_context_record_adds_the_four_digests_and_leaves_meta_alone() -> None:
    """``context_record`` is ``ctx.meta`` plus four digests of the stored arrays (A2, WU-0001.6).

    Reference: ``hashlib.sha256(struct.pack("<...d", ...))`` over the row-major values, written
    in the test (not numpy ``tobytes``). The fake context is a ``SimpleNamespace`` with a
    non-symmetric ``whiten`` so that a transposed read would change the digest. ``ctx.meta`` is
    the same object afterwards with the same content (it is logged and shared by the cached
    context). Exact (a digest is a deterministic function of the bytes; no tolerance).
    """
    def ref(array: np.ndarray) -> str:
        values = array.ravel().tolist()
        return hashlib.sha256(struct.pack("<%dd" % len(values), *values)).hexdigest()

    meta = {"lambda_max": 0.9, "delay": 4}
    ctx = SimpleNamespace(
        meta=meta, state_mean=np.array([0.1, -2.5, 1.0 / 3.0]),
        state_cov=np.array([[2.0, 0.5, 0.0], [0.5, 3.0, 1e-300], [0.0, 1e-300, 4.0]]),
        whiten=np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.5]]),
        unwhiten=np.array([[0.5, 0.25, 0.125], [0.0, 1.0, -0.0], [5e-324, 2.0, 3.0]]))
    before = dict(meta)
    record = context_record(ctx)
    assert list(record) == ["lambda_max", "delay", "state_mean_digest", "cov_digest",
                            "whiten_digest", "unwhiten_digest"]
    assert record["state_mean_digest"] == ref(ctx.state_mean)
    assert record["cov_digest"] == ref(ctx.state_cov)
    assert record["whiten_digest"] == ref(ctx.whiten)
    assert record["unwhiten_digest"] == ref(ctx.unwhiten)
    assert record["whiten_digest"] != ref(ctx.whiten.T)
    assert ctx.meta is meta and meta == before and record is not meta


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


# ------------------------------------------------ DEF-0025: the robustness dimension filter

def _robustness_study(monkeypatch, tmp_path, **changes):
    """A real ``Study`` with stubs: dimension 3, summaries constant, ``run_cell`` recorded."""
    from lpcstudy import experiments
    from lpcstudy.pipeline import Study

    config = dataclasses.replace(SMOKE, misspec_levels=(), analog_counts=(1,),
                                 perturbation_scales=(), **changes)
    study = Study(config, tmp_path)
    study.core_cells["lorenz63"], study.fitted["lorenz63"] = object(), object()
    calls: list[str] = []
    monkeypatch.setattr(study, "context",
                        lambda system: SimpleNamespace(spec=SimpleNamespace(dim=3)))
    monkeypatch.setattr(experiments, "_variant_summary", lambda cell, rules, cfg: {"ok": True})
    monkeypatch.setattr(experiments, "fit_rules", lambda cells, cfg: object())
    monkeypatch.setattr(study, "record_rules", lambda system, cell, rules: None)

    def run_cell(system, noise, library, core, with_evals, label, **kwargs):
        calls.append(label)
        return object()

    monkeypatch.setattr(study, "run_cell", run_cell)
    return study, calls


def test_robustness_skips_and_reports_a_dimension_equal_to_the_state_dimension_def_0025(
        monkeypatch, tmp_path, caplog) -> None:
    """D1: ``D=3`` (equal to ``spec.dim``, zero chi-square degrees of freedom) is skipped, counted, reported.

    Reference: a hand-written config, ``robustness_dims = (3, 5, 7)`` with the smoke base
    ``embedding_dim = 7`` and a system of dimension 3. Expected by the DEF-0025 rule ``d >
    spec.dim`` and ``d != embedding_dim``: 7 is the base cell (not a variant, not a skip), 5 is
    run, 3 is skipped. Variants run: ``["D=5"]``; ``skipped_variants == {"lorenz63": ["D=3"]}``;
    exactly one WARNING from the ``lpcstudy`` logger naming the system and ``D=3``; the result
    has the keys ``base`` and ``D=5`` only. Exact.
    """
    import logging

    from lpcstudy import experiments

    study, calls = _robustness_study(monkeypatch, tmp_path, robustness_dims=(3, 5, 7))
    with caplog.at_level(logging.WARNING, logger="lpcstudy"):
        out = experiments.run_robustness(study, "lorenz63")
    assert calls == ["D=5"]
    assert list(out) == ["base", "D=5"]
    assert study.skipped_variants == {"lorenz63": ["D=3"]}
    warned = [r.getMessage() for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warned) == 1 and "lorenz63" in warned[0] and "D=3" in warned[0]


def test_robustness_counts_every_dimension_at_or_below_the_state_dimension_def_0025(
        monkeypatch, tmp_path, caplog) -> None:
    """D2: ``(2, 3, 5)`` skips ``D=2`` and ``D=3``; ``(5,)`` skips nothing and warns of nothing.

    Reference: the same hand rule as D1. Expected: skipped ``["D=2", "D=3"]`` in configured
    order, run ``["D=5"]`` in both configs, no skip record and no WARNING for ``(5,)``. Exact.
    """
    import logging

    from lpcstudy import experiments

    study, calls = _robustness_study(monkeypatch, tmp_path, robustness_dims=(2, 3, 5))
    experiments.run_robustness(study, "lorenz63")
    assert calls == ["D=5"] and study.skipped_variants == {"lorenz63": ["D=2", "D=3"]}
    caplog.clear()  # the first config's own warning is not part of the second check
    clean, calls = _robustness_study(monkeypatch, tmp_path, robustness_dims=(5,))
    with caplog.at_level(logging.WARNING, logger="lpcstudy"):
        experiments.run_robustness(clean, "lorenz63")
    assert calls == ["D=5"] and clean.skipped_variants == {}
    assert [r for r in caplog.records if r.levelno >= logging.WARNING] == []


def test_no_configured_preset_changes_its_robustness_dimensions_def_0025() -> None:
    """D3: for smoke, pilot and full and every registry system the kept list is the hand list.

    Reference: ``config.py`` read by hand (``embedding_dim = 7`` in every preset;
    ``robustness_dims = (5, 7, 10)`` in the full config, inherited unchanged by the pilot; smoke
    ``(7,)``) and ``systems.py`` (the dimension of Lorenz-63, Rossler and Chua is 3). The base
    dimension 7 is the base cell, so the variants are smoke ``[]`` and pilot, full ``[5, 10]``;
    nothing is skipped. These are the lists of the old filter ``d >= spec.dim`` as well, so no
    preset's robustness list changes. Exact.
    """
    from lpcstudy.config import PILOT, FULL
    from lpcstudy.experiments import robustness_dimensions
    from lpcstudy.systems import SYSTEMS

    expected = {"smoke": [], "pilot": [5, 10], "full": [5, 10]}
    assert set(SYSTEMS) == {"lorenz63", "rossler", "chua"}
    for config in (SMOKE, PILOT, FULL):
        assert config.embedding_dim == 7
        for name, spec in SYSTEMS.items():
            assert spec.dim == 3
            kept, skipped = robustness_dimensions(config, spec.dim)
            assert (kept, skipped) == (expected[config.name], []), (config.name, name)


def test_robustness_dimensions_boundaries_def_0025() -> None:
    """D3b: the filter on a hand-written grid: ``d > dim`` kept, ``d <= dim`` skipped, base ignored.

    Reference: DEF-0025 (chi-square degrees of freedom ``d - dim`` must be positive). With
    ``dim = 3`` and base 7: ``(1, 2, 3, 4, 5, 7, 10)`` keeps ``[4, 5, 10]`` and skips ``[1, 2, 3]``;
    the base 7 is neither. Exact.
    """
    from lpcstudy.experiments import robustness_dimensions

    config = dataclasses.replace(SMOKE, robustness_dims=(1, 2, 3, 4, 5, 7, 10))
    assert robustness_dimensions(config, 3) == ([4, 5, 10], [1, 2, 3])
    assert robustness_dimensions(config, 5) == ([10], [1, 2, 3, 4, 5])


def test_run_handling_warns_of_skipped_variants_and_keeps_its_keys_def_0025(
        tmp_path, caplog) -> None:
    """D4: one aggregate WARNING when variants were skipped; the handling block keeps its keys.

    Reference: the ``failed_variants`` precedent in ``run_handling`` (one WARNING, count in the
    block). Here only the log line is new: expected exactly one WARNING naming the count and the
    label, and the returned keys exactly ``schema, totals, by_system, robustness,
    failed_variants`` (no schema change). Exact.
    """
    import logging

    from lpcstudy.experiments import run_handling
    from lpcstudy.pipeline import Study

    study = Study(SMOKE, tmp_path)
    study.skipped_variants = {"lorenz63": ["D=3"]}
    with caplog.at_level(logging.WARNING, logger="lpcstudy"):
        run = run_handling(study, {"systems": {}})
    warned = [r.getMessage() for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warned) == 1 and "skipped_variants = 1" in warned[0] and "D=3" in warned[0]
    assert list(run) == ["schema", "totals", "by_system", "robustness", "failed_variants"]


def test_convergence_check_resamples_come_from_the_v4_generator(monkeypatch, tmp_path) -> None:
    """WU-0002.14 (b): V4 draws its bootstrap from ``make_rng(seed, system, "V4-convergence")``.

    Reference: a hand re-computation from ``np.random.default_rng([seed, crc32(b"lorenz63|V4-
    convergence")])`` (NumPy directly): for each M in order, ``integers(0, M, (200, M))`` from
    ONE generator that advances over the loop, the weight formula written again from the
    definition (``w = clip(mean(p (p - c)) / mean((c - p)^2), 0, 1)``), the half-width as
    ``0.5 (P97.5 - P2.5)`` over the 200 rows, and its median. Exact (``==``): the same operations
    in the same order on the same arrays. The largest-M deviation from the reference is exactly 0.0
    (the reference is the largest-M weight itself; plan R-f) and ``used_M`` is ``n_oracle_draws``.
    """
    import zlib

    from lpcstudy import experiments
    from lpcstudy.ensemble import DRAW_COUNTERS, DrawBatch
    from lpcstudy.pipeline import Study

    config = SMOKE
    n_states, n_draws = config.convergence_states, max(config.convergence_draws)
    study = Study(config, tmp_path)
    study.unit_noise = lambda *args, **kwargs: np.zeros((n_states + 5, n_draws, 7))
    monkeypatch.setattr(experiments.AnalogLibrary, "build", classmethod(lambda cls, *a, **k: None))
    errors = np.random.default_rng(1411).standard_normal((n_states, n_draws, 1))

    def fake(setup, library, split, rows, unit_noise, horizons, reference_horizon=None):
        ones = np.ones((len(rows), n_draws))
        return DrawBatch(
            cp_err=errors[rows], plp_err=errors[rows] + 0.1, analog_seed_sq=None, est_seed_sq=None,
            distance=None, inputs=None, est_states=None, est_nu=None, analog_vecs=None,
            handled=np.ones((len(rows), len(DRAW_COUNTERS)), dtype=np.int64),
            clip_entries={"error_clips_cp": 0, "error_clips_plp": 0, "error_clips_nonfinite": 0},
            lm_residual=ones, lm_accepted=ones.astype(int), lm_late=ones.astype(int))

    monkeypatch.setattr(experiments, "forecast_draws", fake)
    cell = SimpleNamespace(system="lorenz63", label="base", noise=0.01, library_size=10_000,
                           ctx=SimpleNamespace(embed_dim=10, spec=SimpleNamespace(dim=3)), setup=None)
    out = experiments.convergence_check(study, cell)

    cp, plp = errors[:, :, 0], errors[:, :, 0] + 0.1

    def weight(c, p):
        return np.clip(np.mean(p * (p - c), axis=-1) / np.maximum(np.mean((c - p) ** 2, axis=-1),
                                                                   1e-300), 0, 1)

    hand = np.random.default_rng([config.seed, zlib.crc32(b"lorenz63|V4-convergence")])
    for m_draws in config.convergence_draws:
        boots = np.stack([weight(cp[:, idx], plp[:, idx])
                          for idx in hand.integers(0, m_draws, (200, m_draws))])
        half = 0.5 * (np.percentile(boots, 97.5, axis=0) - np.percentile(boots, 2.5, axis=0))
        assert out[str(m_draws)]["median_half_width"] == float(np.median(half))
    assert out[str(max(config.convergence_draws))]["mean_abs_dev_from_max"] == 0.0
    assert out["used_M"] == config.n_oracle_draws


def _variant_cell(rng: np.random.Generator, n: int = 80):
    """A stub cell for the Lambda_fin variant and H2a: weights with zeros, interior and ones."""
    from unit_helpers import moments_from_triples, realizable_triples

    tri = realizable_triples(rng, n_below=n // 4, n_inside=n // 2, n_above=n - n // 4 - n // 2)
    shuffle = rng.permutation(n)
    scale = 1e-3  # r.m.s. errors below 0.5 (the small-error regime), w* unchanged
    cols = lambda a: np.tile((scale * a[shuffle])[:, None], (1, 2))
    moments = moments_from_triples(cols(tri["E_C"]), cols(tri["E_P"]), cols(tri["C"]))
    moments.horizons = np.array([30, 60])
    moments.analog_seed = np.exp(rng.normal(0.0, 0.3, n)) * 0.01
    moments.est_seed = np.exp(rng.normal(0.0, 0.3, n)) * 0.01
    growth = np.exp(rng.normal(-3.0, 0.3, n))
    ctx = SimpleNamespace(spec=SimpleNamespace(name="lorenz63", observed_index=0), obs_scale=1.0,
                          unwhiten=np.eye(3), split_indices={"test": np.arange(n)},
                          eval_states=np.zeros((n, 3)))
    return SimpleNamespace(system="lorenz63", noise=0.01, ctx=ctx,
                           setup=SimpleNamespace(model_step=None),
                           splits={"test": SimpleNamespace(moments=moments)},
                           oracles={"test": SimpleNamespace(growth=growth)}), growth


def test_lambda_fin_variant_shares_the_h2a_two_part_generator_and_the_directions_across_scales(
        monkeypatch) -> None:
    """P9: the Lambda_fin variant is H2a(ii) bitwise when Lambda_fin := Lambda_tilde, at any scale.

    Reference (M4 of the mathematics check). (a) With the finite-growth function stubbed to return
    the cell's own ``Lambda_tilde`` per window step, the variant's statistic is the same two-part
    statistic on the same index sets, so its partial correlations and both intervals equal the
    ones ``analysis.h2a_separation`` reports, bitwise (``==``; no tolerance: identical operations
    on identical arrays from identical generators). (b) The generator handed to
    ``make_finite_growth`` has the state of a fresh ``make_rng(seed, system, "finite-growth")``
    at both scales 1 and 3 (a fresh one per call, no scale in the label, so the same directions at
    every scale), which differs from a generator on another system's label.
    """
    from lpcstudy import analysis as an
    from lpcstudy import experiments
    from lpcstudy.data import make_rng

    config = dataclasses.replace(SMOKE, bootstrap_resamples=60, eval_horizons_lyapunov=(1.0, 2.0),
                                 perturbation_scales=(1.0, 3.0))
    cell, growth = _variant_cell(np.random.default_rng(14009))
    received: list[dict] = []

    def stub(step_fn, observed_index, obs_scale, unwhiten, n_steps, n_dirs, rng):
        received.append(rng.bit_generator.state)
        return lambda states, eps: np.asarray(growth)[: len(states)]

    monkeypatch.setattr(experiments, "make_finite_growth", stub)
    study = SimpleNamespace(config=config)
    h2a = an.h2a_separation(cell, config)["part_ii"]
    assert not np.isnan(h2a["zero"]["partial_corr"]) and not np.isnan(h2a["interior"]["partial_corr"])
    for scale in (1.0, 3.0):
        out = experiments._perturbation_scale_variant(study, cell, None, scale)
        assert out["H2a_partial_corr_zero_fin"] == h2a["zero"]["partial_corr"]
        assert out["H2a_partial_corr_interior_fin"] == h2a["interior"]["partial_corr"]
        assert out["ci_zero"] == h2a["zero"]["ci"] and out["ci_interior"] == h2a["interior"]["ci"]
    fresh = make_rng(config.seed, "lorenz63", "finite-growth").bit_generator.state
    assert received == [fresh, fresh]
    assert make_rng(config.seed, "rossler", "finite-growth").bit_generator.state != fresh


def test_fitted_record_keeps_the_existing_leaves_and_adds_the_integer_and_digest_leaves() -> None:
    """WU-0003.7a (a2, a3, a4): ``fitted_record`` is the old ``fitted`` block plus ``nfev`` and
    ``status`` of both proxies, ``a5_leaf_digest`` and ``allocator_digest``, in that order.

    Reference: a hand-built world. (i) The A5 tree is a manufactured stump on the profile
    coordinate ``Lambda_hat / lambda_max`` (= ``growth_proxy * steps_per_lyapunov``): fitted on
    the two points 0 and 1 with the other three coordinates constant, its one split is 0.5, so by
    hand a coordinate <= 0.5 is node 1 and a coordinate above is node 2. The growth values are
    0.0, 0.01 (0.3), 0.02 (0.6) and 0.04 (1.2), far from the split, and the leaf of every
    (state, draw) is decided by hand; the digest is ``hashlib.sha256`` of those leaves packed as
    little-endian int64 with ``struct``, calibration first and test second, C order. (ii) The
    allocator digest is ``hashlib.sha256`` of the allocator network's weight and bias values
    (binary64, row-major) packed with ``struct``. (iii) The integer leaves are the typed values
    11, 2, 5, 1. (iv) The existing leaves are the hand values of the fields they read. Moving one
    calibration state across the split changes ``a5_leaf_digest`` and nothing else. Exact.
    """
    from lpcstudy.allocation import ProfileProxies, RegimeMap, SeedProxy
    from lpcstudy.networks import TrainedNetwork
    from sklearn.tree import DecisionTreeRegressor

    cfg, lt = SMOKE, SMOKE.steps_per_lyapunov
    assert lt == 30 and cfg.reference_horizon == 30

    def draws(growth: np.ndarray) -> EvaluationDraws:
        n, e = growth.shape
        zeros = np.zeros((n, e, 3))
        return EvaluationDraws(
            horizons=np.arange(1, 4), cp_err=zeros, plp_err=zeros, verify_noise=zeros,
            distance=np.full((n, e), 0.02), est_nu=np.ones((n, e)), growth_proxy=growth,
            gain_proxy=zeros, inputs=np.zeros((n, e, 1)), noise_sens=np.zeros((n, e)))

    cal_growth = np.array([[0.0, 0.01], [0.02, 0.04], [0.01, 0.01]])
    test_growth = np.array([[0.04, 0.0], [0.02, 0.01]])
    core = SimpleNamespace(noise=0.01, splits={
        "calibration": SimpleNamespace(evals=draws(cal_growth)),
        "test": SimpleNamespace(evals=draws(test_growth))})
    fit = np.zeros((2, 4))
    fit[:, 2] = [0.0, 1.0]
    tree = DecisionTreeRegressor(max_leaf_nodes=2, random_state=0).fit(fit, [0.0, 1.0])
    leaf_ids = np.nonzero(tree.tree_.children_left == -1)[0]
    assert tree.tree_.feature[0] == 2 and tree.tree_.threshold[0] == 0.5
    regime_map = RegimeMap(tree=tree, leaf_ids=leaf_ids, weights=np.full((2, 30), 0.25),
                           horizons_km=np.array([60.0, 90.0]))
    params = [(np.array([[0.1, 0.2], [0.3, 0.4]]), np.array([0.5, -0.5])),
              (np.array([[1.0], [2.0]]), np.array([1e-7]))]
    network = TrainedNetwork(params=params, in_mean=np.zeros(2), in_scale=np.ones(2),
                             out_mean=np.zeros(1), out_scale=np.ones(1), val_loss=0.0, width=2)
    rules = SimpleNamespace(
        proxies=ProfileProxies(SeedProxy(1.0, 2.0, nfev=11, status=2),
                               SeedProxy(0.5, 0.25, nfev=5, status=1), nu_cap=7.5),
        predictor=SimpleNamespace(network=network), regimes={2: regime_map}, chosen_regimes=2)

    def hand_leaves(*growths: np.ndarray) -> str:
        leaves = [1 if g * lt <= 0.5 else 2 for growth in growths for g in growth.ravel()]
        return hashlib.sha256(struct.pack("<%dq" % len(leaves), *leaves)).hexdigest()

    values = [v for w, b in params for a in (w, b) for v in a.ravel().tolist()]
    record = fitted_record(core, rules, cfg)
    assert list(record) == ["analog_proxy", "estimation_proxy", "nu_cap", "chosen_K",
                            "regime_weights_href", "regime_horizons_km_lyapunov",
                            "a5_leaf_digest", "allocator_digest"]
    assert record["analog_proxy"] == {"slope": 1.0, "floor": 2.0, "nfev": 11, "status": 2}
    assert record["estimation_proxy"] == {"slope": 0.5, "floor": 0.25, "nfev": 5, "status": 1}
    assert record["nu_cap"] == 7.5 and record["chosen_K"] == 2
    assert record["regime_weights_href"] == {"2": [0.25, 0.25]}
    assert record["regime_horizons_km_lyapunov"] == {"2": [2.0, 3.0]}
    assert record["a5_leaf_digest"] == hand_leaves(cal_growth, test_growth)
    assert record["allocator_digest"] == hashlib.sha256(
        struct.pack("<%dd" % len(values), *values)).hexdigest()
    moved = cal_growth.copy()
    moved[2, 0] = 0.04  # was 0.01: node 1 becomes node 2
    core.splits["calibration"].evals = draws(moved)
    again = fitted_record(core, rules, cfg)
    assert again["a5_leaf_digest"] == hand_leaves(moved, test_growth) != record["a5_leaf_digest"]
    assert {k: v for k, v in again.items() if k != "a5_leaf_digest"} == \
        {k: v for k, v in record.items() if k != "a5_leaf_digest"}
