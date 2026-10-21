"""Tests for ``lpcstudy.experiments``: the orchestration of the study.

The module under test runs the stages for one system and builds the
``handling`` block (the record of every clipped, replaced or skipped case).
The tests use small hand-built worlds: stub cells, stub studies and planned
numbers whose answers can be read off by eye. Each test names the independent
reference (a hand sum, a formula written out, or a generator rebuilt from
NumPy directly) and explains why its tolerance is what it is.
"""

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
    """Stand in for ``StateOracles``: ``_sweep_subset`` only uses ``subset``."""

    def subset(self, rows: np.ndarray) -> "_Oracles":
        return self


def test_sweep_subset_slices_the_correlation_fields_to_the_evaluation_horizons() -> (
    None
):
    """``_sweep_subset`` restricts the correlation fields like the other fields.

    What is checked: ``err_corr``, ``cp_constant`` and ``plp_constant`` keep
    only the first ``n_test_sweep`` states and only the evaluation horizons.

    Reference: direct indexing of the hand-built full-horizon arrays. The
    entries are their own flat index, so the expected block is
    ``full[:n_sweep][:, eval_horizons - 1]``. The evaluation horizons of
    ``SMOKE`` are (8, 15, 30, 60, 120) steps, and H_ref = 30 is the third
    column. After slicing, the column of H_ref equals the original column 29
    of the first ``n_test_sweep`` rows (the plan's E2 check). The mean fields
    must change the same way. A cell without the fields stays without them
    (``None``). The result is exact (it is only indexing), so there is no
    tolerance.
    """
    config = dataclasses.replace(SMOKE, n_test_sweep=4)
    n_states, n_draws, n_hor = 6, 3, 120
    rng = np.random.default_rng(9)
    moments = _moments_from_draws(
        rng.standard_normal((n_states, n_draws, n_hor)),
        rng.standard_normal((n_states, n_draws, n_hor)),
    )
    grid = np.arange(n_states * n_hor, dtype=float).reshape(n_states, n_hor)
    moments = dataclasses.replace(
        moments,
        err_corr=grid,
        cp_constant=grid % 7 == 0,
        plp_constant=grid % 5 == 0,
    )
    zeros = np.zeros((n_states, 2, n_hor))
    evals = EvaluationDraws(
        horizons=moments.horizons,
        cp_err=zeros,
        plp_err=zeros,
        verify_noise=zeros,
        distance=np.zeros((n_states, 2)),
        est_nu=np.zeros((n_states, 2)),
        growth_proxy=np.zeros((n_states, 2)),
        gain_proxy=zeros,
        inputs=np.zeros((n_states, 2, 1)),
        noise_sens=np.zeros((n_states, 2)),
    )

    def cell_of(mom) -> Cell:
        return Cell(
            system="lorenz63",
            noise=0.01,
            library_size=10_000,
            label="base",
            setup=None,
            splits={"test": SplitData(mom, evals)},
            oracles={"test": _Oracles()},
            horizons=np.arange(1, n_hor + 1),
        )

    out = _sweep_subset(cell_of(moments), config).splits["test"].moments
    cols = np.array(config.eval_horizons) - 1
    np.testing.assert_array_equal(out.horizons, config.eval_horizons)
    np.testing.assert_array_equal(out.err_corr, grid[:4][:, cols])
    np.testing.assert_array_equal(out.cp_constant, (grid % 7 == 0)[:4][:, cols])
    np.testing.assert_array_equal(
        out.plp_constant, (grid % 5 == 0)[:4][:, cols]
    )
    ref = out.at(config.reference_horizon)
    assert ref == 2
    np.testing.assert_array_equal(
        out.err_corr[:, ref], grid[:4, config.reference_horizon - 1]
    )
    np.testing.assert_array_equal(out.mean_cp, moments.mean_cp[:4][:, cols])

    plain = (
        _sweep_subset(
            cell_of(
                _moments_from_draws(
                    rng.standard_normal((n_states, n_draws, n_hor)),
                    rng.standard_normal((n_states, n_draws, n_hor)),
                )
            ),
            config,
        )
        .splits["test"]
        .moments
    )
    assert (
        plain.err_corr is None
        and plain.cp_constant is None
        and plain.plp_constant is None
    )


# ------------------------------------------- WU-0002.11a: counters (DEF-0001)
def test_collect_result_counts_walks_nested_dicts_and_lists_a13() -> None:
    """A13: the walker copies every integer below a counted key only.

    What is checked: ``collect_result_counts`` returns a map from ``/``-joined
    paths to integer counts, copies no other leaf, and does not change its
    input.

    Reference: a hand dict and the expected path map, written out. The
    counted keys met are:

    * a plain int (``n_failed_resamples``);
    * a dict of ints (``zero_variance_corr`` by rho and n_lib, with a nested
      float and a ``bool``, which are skipped);
    * a list of dicts, and an int under a list index;
    * a dict whose leaves are ints and ``None`` (``degenerate_fits``).

    Uncounted keys are not copied. This includes ``n_states``, also when it
    sits below a counted key such as ``zero_variance_corr``, because it is a
    size (fix R1 of WU-0002.11b). In contrast ``n_zero_difference`` is
    counted since WU-0002.11b. A key holding the dotted rho ``0.01`` keeps its
    dot in the path (``/`` separates the parts). The paths and values are
    exact.
    """
    import copy

    from lpcstudy.experiments import RESULT_COUNT_KEYS, collect_result_counts

    tree = {
        "H1b": {
            "PLP": {"n_failed_resamples": 3, "n_floored": 2},
            "n_states": 40,
            "CP": {"n_dropped_resamples": 5},
        },
        "H1a": {
            "by_noise": {
                "0.01": {
                    "n_exponent_at_bound": {"point": 1, "resamples": 7},
                    "n_covariance_warnings": {"point": 0, "resamples": 9},
                }
            }
        },
        "H1c": {"CP": {"n_ineligible_states": 11}},
        "H3a": {
            "n_empty_regimes": 1,
            "n_degenerate_pairs": 2,
            "n_screened_out": {"growth_nonpositive": 4},
        },
        "H2b": {"noise": {"n_constant_states": 6, "n_dropped_resamples": 0}},
        "H2e": {
            "zero_variance_corr": {
                "0.01": {
                    "1000": {
                        "cp_constant": 2,
                        "n_nonfinite": 0,
                        "n_states": 60,
                        "frac": 0.5,
                        "flag": True,
                    }
                }
            },
            "by_noise": [
                {"n_zero_difference": 9, "n_failed_resamples": 4},
                {"n_failed_resamples": 7},
            ],
        },
        "H3b": {
            "degenerate_fits": {"weight_tree": 1, "horizon_tree": None},
            "nan_resamples": 5,
        },
        "n_nonfinite": np.int64(8),
    }
    before = copy.deepcopy(tree)
    got = collect_result_counts(tree)
    assert got == {
        "H1b/PLP/n_failed_resamples": 3,
        "H1b/PLP/n_floored": 2,
        "H1b/CP/n_dropped_resamples": 5,
        "H1a/by_noise/0.01/n_exponent_at_bound/point": 1,
        "H1a/by_noise/0.01/n_exponent_at_bound/resamples": 7,
        "H1a/by_noise/0.01/n_covariance_warnings/point": 0,
        "H1a/by_noise/0.01/n_covariance_warnings/resamples": 9,
        "H1c/CP/n_ineligible_states": 11,
        "H3a/n_empty_regimes": 1,
        "H3a/n_degenerate_pairs": 2,
        "H3a/n_screened_out/growth_nonpositive": 4,
        "H2b/noise/n_constant_states": 6,
        "H2b/noise/n_dropped_resamples": 0,
        "H2e/by_noise/0/n_zero_difference": 9,
        "H2e/zero_variance_corr/0.01/1000/cp_constant": 2,
        "H2e/zero_variance_corr/0.01/1000/n_nonfinite": 0,
        "H2e/by_noise/0/n_failed_resamples": 4,
        "H2e/by_noise/1/n_failed_resamples": 7,
        "H3b/degenerate_fits/weight_tree": 1,
        "H3b/nan_resamples": 5,
        "n_nonfinite": 8,
    }
    assert all(type(v) is int for v in got.values())
    assert tree["H1b"] == before["H1b"] and tree["H2e"] == before["H2e"]
    # n_zero_difference joined the counted keys in WU-0002.11b (review R3 of
    # lane .11a: it is a product of the zero-variance convention); n_states and
    # n_noncontiguous_states stay out.
    assert {
        "n_zero_difference",
        "n_floored",
        "n_dropped_resamples",
        "n_exponent_at_bound",
        "n_covariance_warnings",
        "n_constant_states",
        "n_empty_regimes",
        "n_degenerate_pairs",
        "n_ineligible_states",
        "n_screened_out",
    } <= RESULT_COUNT_KEYS
    assert (
        "n_states" not in RESULT_COUNT_KEYS
        and "n_noncontiguous_states" not in RESULT_COUNT_KEYS
    )


def _handled_cell(handled: np.ndarray) -> Cell:
    """Build a cell whose test moments carry a planned ``handled`` array.

    It stands in for the cell that ``run_cell`` would return.
    """
    n = len(handled)
    moments = _moments_from_draws(np.zeros((n, 2, 120)), np.zeros((n, 2, 120)))
    moments = dataclasses.replace(moments, handled=handled)
    zeros = np.zeros((n, 2, 120))
    evals = EvaluationDraws(
        horizons=moments.horizons,
        cp_err=zeros,
        plp_err=zeros,
        verify_noise=zeros,
        distance=np.zeros((n, 2)),
        est_nu=np.zeros((n, 2)),
        growth_proxy=np.zeros((n, 2)),
        gain_proxy=zeros,
        inputs=np.zeros((n, 2, 1)),
        noise_sens=np.zeros((n, 2)),
    )
    return Cell(
        system="lorenz63",
        noise=0.01,
        library_size=10_000,
        label="base",
        setup=None,
        splits={"test": SplitData(moments, evals)},
        oracles={"test": _Oracles()},
        horizons=np.arange(1, 121),
    )


def test_v7_replacements_a14_hand_sum_and_view_invariance() -> None:
    """A14 and D1: the replacement counts of V7 are the hand sums.

    What is checked: ``V7.invariant_mean_replacements[rho]`` equals the hand
    sum of the planned column, also on a sweep view of a bigger cell.

    Reference: hand sums of a planned ``handled`` table (the entries are small
    distinct integers written out, so the column sum is read off by eye). Two
    noise cells: rho 0.01 with column 0 [2, 0, 1, 3, 0, 1] (sum 7), and
    rho 0.02 with [0, 0, 1, 0, 0, 0] (sum 1). The keys are ``f"{rho:g}"``.

    Cell 1 is the view that ``_sweep_subset`` makes of a full-horizon core
    cell with 6 states, keeping the first 4 rows (``n_test_sweep = 4``). So
    the sum on the view is 2 + 0 + 1 + 3 = 6, and EVERY ``handled`` column of
    the view equals the column sum of the first four planned rows (the columns
    are horizon-free or taken at H_ref: D1, option (b)). A cell without
    ``handled`` raises (PRIME.4). All results are exact.
    """
    from lpcstudy.ensemble import DRAW_COUNTERS
    from lpcstudy.experiments import v7_replacements

    table = np.zeros((6, len(DRAW_COUNTERS)), dtype=np.int64)
    table[:, 0] = [2, 0, 1, 3, 0, 1]
    table[:, 1] = [1, 1, 0, 0, 0, 2]
    table[:, 4] = [0, 2, 0, 0, 1, 0]
    config = dataclasses.replace(SMOKE, n_test_sweep=4)
    view = _sweep_subset(_handled_cell(table), config)
    np.testing.assert_array_equal(
        view.splits["test"].moments.handled, table[:4]
    )
    # Hand-built draws carry no counts.
    assert view.splits["test"].evals.handled is None
    other = _handled_cell(
        np.array(
            [
                [0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
            ]
        )
    )
    got = v7_replacements({0.01: view, 0.02: other})
    assert got == {"0.01": 6, "0.02": 1}
    assert view.splits["test"].moments.clip_entries is None
    bare = _handled_cell(table)
    bare.splits["test"].moments.handled = None
    with pytest.raises(ValueError, match="handled"):
        v7_replacements({0.01: bare})


def test_run_robustness_counts_a_failed_variant_a10(
    monkeypatch, tmp_path
) -> None:
    """A10: a failing robustness variant is counted once and keeps its error.

    What is checked: a variant that fails does not stop the run. It is counted
    in ``failed_variants`` and its result entry holds the error text.

    Reference: a hand construction. A real ``Study`` (nothing is computed at
    construction) has its ``context`` replaced by a stub of dimension 3, with
    ``core_cells`` and ``fitted`` stubbed and the summary functions replaced by
    constants. The function ``run_cell`` is replaced by one that raises
    ``RuntimeError("boom")`` for the label ``misspec=0.05``. The config asks
    for misspec level 0.05 only, with no embedding or analog variants and no
    perturbation scales, so there is exactly one variant.

    Expected: ``failed_variants`` is 1 for the system
    (``{"lorenz63": ["misspec=0.05"]}``),
    ``out["misspec=0.05"] == {"error": "RuntimeError('boom')"}``, and
    ``out["base"]`` is unchanged. All results are exact.
    """
    from lpcstudy import experiments
    from lpcstudy.pipeline import Study

    config = dataclasses.replace(
        SMOKE,
        misspec_levels=(0.05,),
        robustness_dims=(7,),
        analog_counts=(1,),
        perturbation_scales=(),
    )
    study = Study(config, tmp_path)
    study.core_cells["lorenz63"], study.fitted["lorenz63"] = object(), object()
    monkeypatch.setattr(
        study,
        "context",
        lambda system: SimpleNamespace(spec=SimpleNamespace(dim=3)),
    )
    monkeypatch.setattr(
        experiments, "_variant_summary", lambda cell, rules, cfg: {"ok": True}
    )

    def boom(system, *args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(study, "run_cell", boom)
    out = experiments.run_robustness(study, "lorenz63")
    assert out == {
        "base": {"ok": True},
        "misspec=0.05": {"error": "RuntimeError('boom')"},
    }
    assert study.failed_variants == {"lorenz63": ["misspec=0.05"]}
    assert sum(len(v) for v in study.failed_variants.values()) == 1


def test_log_handling_writes_one_warning_per_nonzero_counter_a12(
    caplog,
) -> None:
    """A12: each nonzero counter gives one WARNING line, plus one INFO summary.

    What is checked: ``log_handling`` writes exactly one WARNING per nonzero
    counter, nothing for a zero counter, and one INFO summary.

    Reference: a hand-built handling block with one cell whose counts are
    zero except ``error_clips_cp = 4`` and ``gain_floor = 2`` (denominators
    1200 error entries and 10 evaluation draws), and one oracle split with all
    zeros. Expected: WARNING records from the ``lpcstudy`` logger whose text
    names the system, the block, the counter, the count and the denominator
    (``handling lorenz63 base|rho=0.01|n_lib=10000|core: error_clips_cp = 4 of
    1200 error_entries``), and one INFO record with the number of lines and
    blocks. A V3 block marks its PLP counters, and the two LM counters, as
    inert (R3: V3 computes PLP but does not use it). The strings are compared
    exactly.
    """
    import logging

    from lpcstudy.experiments import log_handling
    from lpcstudy.pipeline import ALL_COUNTERS, CELL_COUNTERS, CELL_DENOMINATORS

    counts = dict.fromkeys(CELL_COUNTERS, 0)
    counts.update(error_clips_cp=4, gain_floor=2)
    dens = dict.fromkeys(CELL_DENOMINATORS, 0)
    dens.update(error_entries=1200, eval_draws=10)
    v3 = dict.fromkeys(CELL_COUNTERS, 0)
    # WU-0005.4 (R3).
    v3.update(error_clips_plp=1, lm_nonfinite_cost=2, lm_nonfinite_jacobian=3)
    dens["estimates"] = 7
    handling = {
        "cells": {
            "base|rho=0.01|n_lib=10000|core": {
                "counts": counts,
                "denominators": dens,
            },
            "V3-cp-horizon": {"counts": v3, "denominators": dens},
        },
        "oracles": {
            "test": {
                "counts": {"oracle_nonfinite": 0},
                "denominators": {"states": 5},
            }
        },
    }
    with caplog.at_level(logging.INFO, logger="lpcstudy"):
        log_handling("lorenz63", handling)
    warnings_ = [
        r.getMessage() for r in caplog.records if r.levelno == logging.WARNING
    ]
    infos = [
        r.getMessage() for r in caplog.records if r.levelno == logging.INFO
    ]
    assert warnings_ == [
        "handling lorenz63 base|rho=0.01|n_lib=10000|core: "
        "error_clips_cp = 4 of 1200 error_entries",
        "handling lorenz63 base|rho=0.01|n_lib=10000|core: "
        "gain_floor = 2 of 10 eval_draws",
        "handling lorenz63 V3-cp-horizon: "
        "error_clips_plp = 1 of 1200 error_entries [inert: V3 uses CP only]",
        "handling lorenz63 V3-cp-horizon: "
        "lm_nonfinite_cost = 2 of 7 estimates [inert: V3 uses CP only]",
        "handling lorenz63 V3-cp-horizon: "
        "lm_nonfinite_jacobian = 3 of 7 estimates [inert: V3 uses CP only]",
    ]
    assert infos == ["handling lorenz63: 5 nonzero counters in 3 blocks"]
    assert set(ALL_COUNTERS) >= {"error_clips_cp", "gain_floor"}


# ------------------------------------------------- WU-0005.5: P2(c) wiring
def _p2c_fixture():
    """Build a fake study, core cell and library for ``p2c_verification``.

    The toy world has one analog (k = 1), delay dimension D = 7 and 3 splits.
    """
    from scipy.spatial import cKDTree

    from lpcstudy.ensemble import AnalogLibrary, retrieval_spread

    rng = np.random.default_rng(50061)
    series = rng.standard_normal(400)
    delay, dim, rho, draws = 3, 7, 0.4, 10
    splits = {
        "construction": np.arange(20, 60),
        "calibration": np.arange(60, 90),
        "test": np.arange(90, 120),
    }
    vectors = rng.standard_normal((200, dim))
    library = AnalogLibrary(
        indices=np.arange(200), noisy_series=np.zeros(1), tree=cKDTree(vectors)
    )
    ctx = SimpleNamespace(
        eval_clean=series, split_indices=splits, delay=delay, embed_dim=dim
    )
    noises = {
        name: rng.standard_normal((len(t), draws, dim))
        for name, t in splits.items()
    }
    seen = []

    def unit_noise(context, split, purpose, n_draws, width):
        seen.append((split, purpose, n_draws, width))
        return noises[split]

    study = SimpleNamespace(
        config=SimpleNamespace(n_oracle_draws=draws), unit_noise=unit_noise
    )
    sens = {}
    for name, times in splits.items():
        # Independent reference: the delay vector written out, the retrieval by
        # exhaustive search.
        clean = np.stack(
            [series[times - j * delay] for j in range(dim)], axis=1
        )
        queries = clean[:, None, :] + rho * noises[name]
        nearest = np.argmin(
            np.linalg.norm(
                queries[:, :, None, :] - vectors[None, None], axis=-1
            ),
            axis=-1,
        )
        sens[name] = retrieval_spread(vectors[nearest], rho)
    core = SimpleNamespace(
        system="toy",
        noise=rho,
        library_size=200,
        ctx=ctx,
        setup=SimpleNamespace(n_analogs=1),
        splits={
            name: SimpleNamespace(
                moments=SimpleNamespace(noise_sens=sens[name])
            )
            for name in splits
        },
    )
    return study, core, library, sens, seen


def test_p2c_verification_uses_the_core_draws_and_logs_a_mismatch(
    caplog,
) -> None:
    """``p2c_verification`` uses the core draws of every split and logs defects.

    What is checked: the check takes the clean queries and the oracle noise of
    every split, finds no violation on a clean toy world, and logs a warning
    when one noise sensitivity differs by the smallest possible amount.

    Reference: the clean delay vectors written out by indexing
    (``series[t - j tau]``) and the core ``noise_sens`` computed by exhaustive
    nearest-neighbor search on a toy library (200 vectors in R^7, rho = 0.4,
    M = 10, 3 splits of 40, 30 and 30 states). The check must report
    ``same_draws_identical`` (bitwise), no violation, 100 states and the cell
    description, and must ask ``unit_noise`` for the ``"oracle"`` draws of each
    split. With one ``noise_sens`` entry moved by one ulp (the smallest step
    between floating-point numbers), it must report ``False`` and write one
    WARNING naming the defect (PRIME.4). The toy library is far from the
    exact-arithmetic limits, so any violation would be a defect. Using k = 2 is
    refused. All comparisons are exact.
    """
    import logging

    from lpcstudy.experiments import p2c_verification

    study, core, library, sens, seen = _p2c_fixture()
    with caplog.at_level(logging.INFO, logger="lpcstudy"):
        out = p2c_verification(study, core, library)
    assert out["same_draws_identical"] is True and out["n_violations"] == 0
    assert out["n_states"] == 100
    assert out["splits"] == {"construction": 40, "calibration": 30, "test": 30}
    assert out["cell"] == {
        "noise": 0.4,
        "n_lib": 200,
        "n_analogs": 1,
        "draws": 10,
        "splits": ["construction", "calibration", "test"],
    }
    assert seen == [
        (name, "oracle", 10, 7)
        for name in ("construction", "calibration", "test")
    ]
    assert not [r for r in caplog.records if r.levelno >= logging.WARNING]

    sens["test"] = sens["test"].copy()
    sens["test"][2] = np.nextafter(sens["test"][2], np.inf)
    core.splits["test"].moments.noise_sens = sens["test"]
    caplog.clear()
    with caplog.at_level(logging.INFO, logger="lpcstudy"):
        bad = p2c_verification(study, core, library)
    assert bad["same_draws_identical"] is False
    warnings_ = [
        r.getMessage() for r in caplog.records if r.levelno == logging.WARNING
    ]
    assert len(warnings_) == 1 and warnings_[0].startswith(
        "toy P2(c) verification FAILED"
    )

    core.setup.n_analogs = 2
    with pytest.raises(ValueError, match="single nearest analog"):
        p2c_verification(study, core, library)


def test_context_record_adds_the_four_digests_and_leaves_meta_alone() -> None:
    """``context_record`` is ``ctx.meta`` plus four digests of the arrays.

    (A2, WU-0001.6.) A digest is a short fingerprint of the exact bytes of an
    array.

    Reference: ``hashlib.sha256(struct.pack("<...d", ...))`` over the
    row-major values, written in the test (not numpy ``tobytes``). The fake
    context is a ``SimpleNamespace`` with a non-symmetric ``whiten`` so that a
    transposed read would change the digest. ``ctx.meta`` is the same object
    afterwards with the same content (it is logged and shared by the cached
    context). The check is exact: a digest is a deterministic function of the
    bytes, so there is no tolerance.
    """

    def ref(array: np.ndarray) -> str:
        values = array.ravel().tolist()
        return hashlib.sha256(
            struct.pack("<%dd" % len(values), *values)
        ).hexdigest()

    meta = {"lambda_max": 0.9, "delay": 4}
    ctx = SimpleNamespace(
        meta=meta,
        state_mean=np.array([0.1, -2.5, 1.0 / 3.0]),
        state_cov=np.array(
            [[2.0, 0.5, 0.0], [0.5, 3.0, 1e-300], [0.0, 1e-300, 4.0]]
        ),
        whiten=np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.5]]),
        unwhiten=np.array(
            [[0.5, 0.25, 0.125], [0.0, 1.0, -0.0], [5e-324, 2.0, 3.0]]
        ),
    )
    before = dict(meta)
    record = context_record(ctx)
    assert list(record) == [
        "lambda_max",
        "delay",
        "state_mean_digest",
        "cov_digest",
        "whiten_digest",
        "unwhiten_digest",
    ]
    assert record["state_mean_digest"] == ref(ctx.state_mean)
    assert record["cov_digest"] == ref(ctx.state_cov)
    assert record["whiten_digest"] == ref(ctx.whiten)
    assert record["unwhiten_digest"] == ref(ctx.unwhiten)
    assert record["whiten_digest"] != ref(ctx.whiten.T)
    assert ctx.meta is meta and meta == before and record is not meta


def test_sweep_subset_slices_lm_arrays_by_rows_only() -> None:
    """WU-0005.4 (L6): ``_sweep_subset`` slices the LM arrays by rows only.

    What is checked: the Levenberg-Marquardt (LM) arrays keep the first
    ``n_test_sweep`` rows and nothing else changes.

    Reference: direct indexing of hand arrays (the entries are their own flat
    index). The arrays do not depend on the horizon, so no column slice
    applies: the ``lm_*`` arrays of the moments and of the draws equal
    ``full[:4]``, with shape ``(4, 2)``. The result is exact.
    """
    config = dataclasses.replace(SMOKE, n_test_sweep=4)
    table = np.zeros((6, 8), dtype=np.int64)
    cell = _handled_cell(table)
    residual = np.arange(12.0).reshape(6, 2)
    accepted = np.arange(12, dtype=np.int32).reshape(6, 2)
    late = (np.arange(12) % 2).astype(np.int32).reshape(6, 2)
    for holder in (cell.splits["test"].moments, cell.splits["test"].evals):
        holder.lm_residual, holder.lm_accepted, holder.lm_late = (
            residual,
            accepted,
            late,
        )
    view = _sweep_subset(cell, config)
    for holder in (view.splits["test"].moments, view.splits["test"].evals):
        assert holder.lm_residual.tobytes() == residual[:4].tobytes()
        assert np.array_equal(holder.lm_accepted, accepted[:4])
        assert np.array_equal(holder.lm_late, late[:4])
        assert holder.lm_residual.shape == (4, 2)


def test_convergence_check_records_the_lm_block_of_its_forecasts(
    monkeypatch, tmp_path
) -> None:
    """WU-0005.4 (L6): V4 summarizes the LM arrays of its own forecasts.

    What is checked: the summary of the Levenberg-Marquardt (LM) diagnostics is
    stored under ``V4-convergence``, and equals the hand values.

    Reference: hand values. ``forecast_draws`` is replaced by a stub that
    returns, for global row i, the residual i + 0.5 and accepted count i on
    every one of the M = 30 draws (SMOKE has ``convergence_draws = (10, 30)``
    and ``convergence_states = 10``, so there are 10 states in two batches of
    5), late progress i mod 2, and a ``handled`` array of ones. Then n = 300.
    The residual values 0.5..9.5 each occur 30 times, so the median is 5.0 (the
    150th and 151st values are 4.5 and 5.5) and the 95th percentile is
    x_(285) = 9.5. The accepted counts 0..9 give median 4.5 and a fraction 0.1
    of zeros (30 of 300). The late fraction is 0.5. Every residual exceeds the
    7-degrees-of-freedom threshold 24.32 * 0.01^2 (the cell has embed_dim 10
    and state dimension 3), so that fraction is 1.0. Each ``handled`` column
    sums to 10. No array is kept in the record, and it survives a round trip
    through JSON. All results are exact.
    """
    import json

    from lpcstudy import experiments
    from lpcstudy.ensemble import DrawBatch, DRAW_COUNTERS
    from lpcstudy.pipeline import Study

    config = SMOKE
    n_states, n_draws = config.convergence_states, max(config.convergence_draws)
    assert (n_states, n_draws) == (10, 30)
    study = Study(config, tmp_path)
    study.unit_noise = lambda *args, **kwargs: np.zeros(
        (n_states + 5, n_draws, 7)
    )
    monkeypatch.setattr(
        experiments.AnalogLibrary,
        "build",
        classmethod(lambda cls, *a, **k: None),
    )
    rng = np.random.default_rng(3)
    errors = rng.standard_normal((n_states, n_draws, 1))

    def fake(
        setup,
        library,
        split,
        rows,
        unit_noise,
        horizons,
        reference_horizon=None,
    ):
        ones = np.ones((len(rows), n_draws))
        return DrawBatch(
            cp_err=errors[rows],
            plp_err=errors[rows] + 0.1,
            analog_seed_sq=None,
            est_seed_sq=None,
            distance=None,
            inputs=None,
            est_states=None,
            est_nu=None,
            analog_vecs=None,
            handled=np.ones((len(rows), len(DRAW_COUNTERS)), dtype=np.int64),
            clip_entries={
                "error_clips_cp": 0,
                "error_clips_plp": 0,
                "error_clips_nonfinite": 0,
            },
            lm_residual=(rows + 0.5)[:, None] * ones,
            lm_accepted=rows[:, None] * ones.astype(int),
            lm_late=(rows % 2)[:, None] * ones.astype(int),
        )

    monkeypatch.setattr(experiments, "forecast_draws", fake)
    cell = SimpleNamespace(
        system="lorenz63",
        label="base",
        noise=0.01,
        library_size=10_000,
        ctx=SimpleNamespace(embed_dim=10, spec=SimpleNamespace(dim=3)),
        setup=None,
    )
    experiments.convergence_check(study, cell)
    record = study._records[("lorenz63", "main")]["V4-convergence"]
    lm = record["lm"]
    assert (lm["n_estimates"], lm["median_residual"], lm["p95_residual"]) == (
        300,
        5.0,
        9.5,
    )
    assert (lm["median_iterations"], lm["fraction_no_decrease"]) == (4.5, 0.1)
    assert (lm["fraction_late_progress"], lm["fraction_above_chi2"]) == (
        0.5,
        1.0,
    )
    assert lm["by_kind"]["check"] == {
        k: v for k, v in lm.items() if k != "by_kind"
    }
    assert lm["by_kind"]["oracle"]["n_estimates"] == 0 and lm["noise"] == 0.01
    assert (
        lm["gof_dof"] == 7
    )  # D - m = 10 - 3 (R2): a robustness-sized embedding
    assert record["counts"]["lm_nonfinite_cost"] == n_states
    assert record["denominators"]["estimates"] == lm["n_estimates"]
    assert json.loads(json.dumps(record)) == record


def test_cp_horizon_check_records_the_lm_block_of_v3(
    monkeypatch, tmp_path
) -> None:
    """WU-0005.4 (L6): V3 records its LM summary and removes ``handling``.

    What is checked: the summary of the Levenberg-Marquardt (LM) diagnostics is
    stored under ``V3-cp-horizon``, and the returned dict keeps the V3 value
    but loses its ``handling`` entry.

    Reference: hand values. ``check_cp_horizon`` is replaced by a stub that
    returns the dict that ``validation.check_cp_horizon`` builds (checked by
    its own test), with 3 states and 1 draw: residuals [2, 4, 6], accepted
    counts [0, 3, 6], late flags [0, 1, 1] and noise 1.0 (the threshold is
    18.47, so none is above). Expected: median 4, 95th percentile
    x_(ceil(2.85)) = 6, median accepted 3, fraction with no decrease 1/3, late
    2/3, above the threshold 0. The results are exact up to the division by 3
    (1/3 and 2/3 are compared with ``==`` to the same expression).
    """
    from lpcstudy import experiments
    from lpcstudy.ensemble import DRAW_COUNTERS
    from lpcstudy.pipeline import Study

    study = Study(SMOKE, tmp_path)
    handling = {
        "handled": dict.fromkeys(DRAW_COUNTERS, 0),
        "clip_entries": {
            "error_clips_cp": 0,
            "error_clips_plp": 0,
            "error_clips_nonfinite": 0,
        },
        "n_states": 3,
        "n_draws": 1,
        "n_horizons": 120,
        "noise": 1.0,
        "dof": 4,
        "lm": (
            np.array([[2.0], [4.0], [6.0]]),
            np.array([[0], [3], [6]]),
            np.array([[0], [1], [1]]),
        ),
    }
    monkeypatch.setattr(
        experiments,
        "check_cp_horizon",
        lambda *args, **kwargs: {
            "cp_median_vpt_lyapunov": 1.5,
            "handling": dict(handling),
        },
    )
    core = SimpleNamespace(system="lorenz63", label="base", setup=None)
    out = experiments._cp_horizon_check(study, core, None, None, None)
    assert out == {"cp_median_vpt_lyapunov": 1.5}
    lm = study._records[("lorenz63", "main")]["V3-cp-horizon"]["lm"]
    assert (lm["n_estimates"], lm["median_residual"], lm["p95_residual"]) == (
        3,
        4.0,
        6.0,
    )
    assert (lm["median_iterations"], lm["fraction_no_decrease"]) == (3.0, 1 / 3)
    assert (lm["fraction_late_progress"], lm["fraction_above_chi2"]) == (
        2 / 3,
        0.0,
    )


# ------------------------------------ DEF-0025: the robustness dimension filter
def _robustness_study(monkeypatch, tmp_path, **changes):
    """Build a real ``Study`` with stubs.

    The system dimension is 3, the summaries are constants, and ``run_cell``
    only records the labels it is called with.
    """
    from lpcstudy import experiments
    from lpcstudy.pipeline import Study

    config = dataclasses.replace(
        SMOKE,
        misspec_levels=(),
        analog_counts=(1,),
        perturbation_scales=(),
        **changes,
    )
    study = Study(config, tmp_path)
    study.core_cells["lorenz63"], study.fitted["lorenz63"] = object(), object()
    calls: list[str] = []
    monkeypatch.setattr(
        study,
        "context",
        lambda system: SimpleNamespace(spec=SimpleNamespace(dim=3)),
    )
    monkeypatch.setattr(
        experiments, "_variant_summary", lambda cell, rules, cfg: {"ok": True}
    )
    monkeypatch.setattr(experiments, "fit_rules", lambda cells, cfg: object())
    monkeypatch.setattr(study, "record_rules", lambda system, cell, rules: None)

    def run_cell(system, noise, library, core, with_evals, label, **kwargs):
        calls.append(label)
        return object()

    monkeypatch.setattr(study, "run_cell", run_cell)
    return study, calls


def test_robustness_skips_and_reports_a_dimension_equal_to_the_state_dimension_def_0025(
    monkeypatch, tmp_path, caplog
) -> None:
    """D1: the dimension ``D=3`` is skipped, counted and reported.

    The dimension 3 equals ``spec.dim``, which leaves zero chi-square degrees
    of freedom, so that variant cannot be tested.

    Reference: a hand-written config with ``robustness_dims = (3, 5, 7)``, the
    smoke base ``embedding_dim = 7`` and a system of dimension 3. By the
    DEF-0025 rule (``d > spec.dim`` and ``d != embedding_dim``): 7 is the base
    cell (neither a variant nor a skip), 5 is run, and 3 is skipped. Expected:
    the variants run are ``["D=5"]``; ``skipped_variants`` is
    ``{"lorenz63": ["D=3"]}``; exactly one WARNING from the ``lpcstudy``
    logger names the system and ``D=3``; and the result has the keys ``base``
    and ``D=5`` only. All results are exact.
    """
    import logging

    from lpcstudy import experiments

    study, calls = _robustness_study(
        monkeypatch, tmp_path, robustness_dims=(3, 5, 7)
    )
    with caplog.at_level(logging.WARNING, logger="lpcstudy"):
        out = experiments.run_robustness(study, "lorenz63")
    assert calls == ["D=5"]
    assert list(out) == ["base", "D=5"]
    assert study.skipped_variants == {"lorenz63": ["D=3"]}
    warned = [
        r.getMessage() for r in caplog.records if r.levelno == logging.WARNING
    ]
    assert len(warned) == 1 and "lorenz63" in warned[0] and "D=3" in warned[0]


def test_robustness_counts_every_dimension_at_or_below_the_state_dimension_def_0025(
    monkeypatch, tmp_path, caplog
) -> None:
    """D2: every too-small dimension is skipped; a clean config skips nothing.

    The config ``(2, 3, 5)`` skips ``D=2`` and ``D=3``. The config ``(5,)``
    skips nothing and warns of nothing.

    Reference: the same hand rule as D1. Expected: skipped ``["D=2", "D=3"]``
    in configured order, ``["D=5"]`` run in both configs, and no skip record
    and no WARNING for ``(5,)``. All results are exact.
    """
    import logging

    from lpcstudy import experiments

    study, calls = _robustness_study(
        monkeypatch, tmp_path, robustness_dims=(2, 3, 5)
    )
    experiments.run_robustness(study, "lorenz63")
    assert calls == ["D=5"]
    assert study.skipped_variants == {"lorenz63": ["D=2", "D=3"]}
    # The first config's own warning is not part of the second check.
    caplog.clear()
    clean, calls = _robustness_study(
        monkeypatch, tmp_path, robustness_dims=(5,)
    )
    with caplog.at_level(logging.WARNING, logger="lpcstudy"):
        experiments.run_robustness(clean, "lorenz63")
    assert calls == ["D=5"] and clean.skipped_variants == {}
    assert [r for r in caplog.records if r.levelno >= logging.WARNING] == []


def test_no_configured_preset_changes_its_robustness_dimensions_def_0025() -> (
    None
):
    """D3: no preset changes its robustness dimensions (DEF-0025).

    What is checked: for the smoke, pilot and full presets and every system in
    the registry, the kept list equals the hand list and nothing is skipped.

    Reference: ``config.py`` read by hand (``embedding_dim = 7`` in every
    preset; ``robustness_dims = (5, 7, 10)`` in the full config, inherited
    unchanged by the pilot; ``(7,)`` for smoke) and ``systems.py`` (the
    dimension of Lorenz-63, Rossler and Chua is 3). The base dimension 7 is the
    base cell, so the variants are ``[]`` for smoke and ``[5, 10]`` for pilot
    and full, and nothing is skipped. These are also the lists of the old
    filter ``d >= spec.dim``, so no preset's robustness list changes. All
    results are exact.
    """
    from lpcstudy.config import PILOT, FULL
    from lpcstudy.experiments import robustness_dimensions
    from lpcstudy.systems import SYSTEMS

    expected = {"smoke": [], "pilot": [5, 10], "full": [5, 10]}
    # Changed by design in WU-0021 (DEC-0037): this asserted
    # ``set(SYSTEMS) == {"lorenz63", "rossler", "chua"}`` and ``spec.dim == 3``
    # for every spec. The frozen three keep dim 3; the extension entries are
    # listed separately (the hyperchaotic Rossler has dim 4, and 5 > 4 keeps
    # the same lists).
    frozen = {"lorenz63", "rossler", "chua"}
    dims = {
        "rossler_hyper": 4,
        "lorenz63_r166": 3,
        "rossler_z": 3,
        "hindmarsh_rose": 3,
        "hyper_jha": 4,
        "lorenz96_4": 4,
    }
    assert set(SYSTEMS) == frozen | set(dims)
    for config in (SMOKE, PILOT, FULL):
        assert config.embedding_dim == 7
        for name, spec in SYSTEMS.items():
            assert spec.dim == (3 if name in frozen else dims[name])
            kept, skipped = robustness_dimensions(config, spec.dim)
            assert (kept, skipped) == (expected[config.name], []), (
                config.name,
                name,
            )


def test_robustness_dimensions_boundaries_def_0025() -> None:
    """D3b: the filter keeps ``d > dim``, skips ``d <= dim``, ignores the base.

    Reference: DEF-0025 (the chi-square degrees of freedom ``d - dim`` must be
    positive), applied to a hand-written grid. With ``dim = 3`` and base 7, the
    list ``(1, 2, 3, 4, 5, 7, 10)`` keeps ``[4, 5, 10]`` and skips
    ``[1, 2, 3]``; the base 7 is neither. The results are exact.
    """
    from lpcstudy.experiments import robustness_dimensions

    config = dataclasses.replace(SMOKE, robustness_dims=(1, 2, 3, 4, 5, 7, 10))
    assert robustness_dimensions(config, 3) == ([4, 5, 10], [1, 2, 3])
    assert robustness_dimensions(config, 5) == ([10], [1, 2, 3, 4, 5])


def test_run_handling_warns_of_skipped_variants_and_keeps_its_keys_def_0025(
    tmp_path, caplog
) -> None:
    """D4: skipped variants give one summary WARNING; the block keeps its keys.

    Reference: the precedent of ``failed_variants`` in ``run_handling`` (one
    WARNING, the count in the block). Expected: exactly one WARNING naming the
    count and the label, and the returned keys exactly ``schema, totals,
    by_system, robustness, failed_variants, skipped_variants``. WU-0004f
    appended ``skipped_variants`` (the count, as for ``failed_variants``) to
    the block. The key list below used to end with ``failed_variants`` (D4 of
    WU-0011.5, "no schema change"), and the new list is equally exact, so no
    assertion was loosened. The results are exact.
    """
    import logging

    from lpcstudy.experiments import run_handling
    from lpcstudy.pipeline import Study

    study = Study(SMOKE, tmp_path)
    study.skipped_variants = {"lorenz63": ["D=3"]}
    with caplog.at_level(logging.WARNING, logger="lpcstudy"):
        run = run_handling(study, {"systems": {}})
    warned = [
        r.getMessage() for r in caplog.records if r.levelno == logging.WARNING
    ]
    assert len(warned) == 1 and "skipped_variants = 1" in warned[0]
    assert "D=3" in warned[0]
    assert list(run) == [
        "schema",
        "totals",
        "by_system",
        "robustness",
        "failed_variants",
        "skipped_variants",
    ]
    assert run["skipped_variants"] == 1 and type(run["skipped_variants"]) is int


def test_convergence_check_resamples_come_from_the_v4_generator(
    monkeypatch, tmp_path
) -> None:
    """WU-0002.14 (b): V4 draws its bootstrap from one named random stream.

    The stream is ``make_rng(seed, system, "V4-convergence")``.

    Reference: a hand re-computation from
    ``np.random.default_rng([seed, crc32(b"lorenz63|V4-convergence")])``
    (NumPy directly). For each M in order it draws ``integers(0, M, (200, M))``
    from ONE generator that advances over the loop. The weight formula is
    written again from the definition
    (``w = clip(mean(p (p - c)) / mean((c - p)^2), 0, 1)``), the half-width is
    ``0.5 (P97.5 - P2.5)`` over the 200 rows, and the result is its median.
    The comparison is exact (``==``) because the operations are the same, in
    the same order, on the same arrays. The deviation of the largest M from the
    reference is exactly 0.0 (the reference is the largest-M weight itself;
    plan R-f), and ``used_M`` is ``n_oracle_draws``.
    """
    import zlib

    from lpcstudy import experiments
    from lpcstudy.ensemble import DRAW_COUNTERS, DrawBatch
    from lpcstudy.pipeline import Study

    config = SMOKE
    n_states, n_draws = config.convergence_states, max(config.convergence_draws)
    study = Study(config, tmp_path)
    study.unit_noise = lambda *args, **kwargs: np.zeros(
        (n_states + 5, n_draws, 7)
    )
    monkeypatch.setattr(
        experiments.AnalogLibrary,
        "build",
        classmethod(lambda cls, *a, **k: None),
    )
    errors = np.random.default_rng(1411).standard_normal((n_states, n_draws, 1))

    def fake(
        setup,
        library,
        split,
        rows,
        unit_noise,
        horizons,
        reference_horizon=None,
    ):
        ones = np.ones((len(rows), n_draws))
        return DrawBatch(
            cp_err=errors[rows],
            plp_err=errors[rows] + 0.1,
            analog_seed_sq=None,
            est_seed_sq=None,
            distance=None,
            inputs=None,
            est_states=None,
            est_nu=None,
            analog_vecs=None,
            handled=np.ones((len(rows), len(DRAW_COUNTERS)), dtype=np.int64),
            clip_entries={
                "error_clips_cp": 0,
                "error_clips_plp": 0,
                "error_clips_nonfinite": 0,
            },
            lm_residual=ones,
            lm_accepted=ones.astype(int),
            lm_late=ones.astype(int),
        )

    monkeypatch.setattr(experiments, "forecast_draws", fake)
    cell = SimpleNamespace(
        system="lorenz63",
        label="base",
        noise=0.01,
        library_size=10_000,
        ctx=SimpleNamespace(embed_dim=10, spec=SimpleNamespace(dim=3)),
        setup=None,
    )
    out = experiments.convergence_check(study, cell)

    cp, plp = errors[:, :, 0], errors[:, :, 0] + 0.1

    def weight(c, p):
        return np.clip(
            np.mean(p * (p - c), axis=-1)
            / np.maximum(np.mean((c - p) ** 2, axis=-1), 1e-300),
            0,
            1,
        )

    hand = np.random.default_rng(
        [config.seed, zlib.crc32(b"lorenz63|V4-convergence")]
    )
    for m_draws in config.convergence_draws:
        boots = np.stack(
            [
                weight(cp[:, idx], plp[:, idx])
                for idx in hand.integers(0, m_draws, (200, m_draws))
            ]
        )
        half = 0.5 * (
            np.percentile(boots, 97.5, axis=0)
            - np.percentile(boots, 2.5, axis=0)
        )
        assert out[str(m_draws)]["median_half_width"] == float(np.median(half))
    assert (
        out[str(max(config.convergence_draws))]["mean_abs_dev_from_max"] == 0.0
    )
    assert out["used_M"] == config.n_oracle_draws


def _variant_cell(rng: np.random.Generator, n: int = 80):
    """Build a stub cell for the Lambda_fin variant and H2a.

    The best weights include zeros, interior values and ones.
    """
    from unit_helpers import moments_from_triples, realizable_triples

    tri = realizable_triples(
        rng, n_below=n // 4, n_inside=n // 2, n_above=n - n // 4 - n // 2
    )
    shuffle = rng.permutation(n)
    scale = (
        1e-3  # r.m.s. errors below 0.5 (the small-error regime), w* unchanged
    )
    cols = lambda a: np.tile((scale * a[shuffle])[:, None], (1, 2))
    moments = moments_from_triples(
        cols(tri["E_C"]), cols(tri["E_P"]), cols(tri["C"])
    )
    moments.horizons = np.array([30, 60])
    moments.analog_seed = np.exp(rng.normal(0.0, 0.3, n)) * 0.01
    moments.est_seed = np.exp(rng.normal(0.0, 0.3, n)) * 0.01
    growth = np.exp(rng.normal(-3.0, 0.3, n))
    ctx = SimpleNamespace(
        spec=SimpleNamespace(name="lorenz63", observed_index=0),
        obs_scale=1.0,
        unwhiten=np.eye(3),
        split_indices={"test": np.arange(n)},
        eval_states=np.zeros((n, 3)),
    )
    return (
        SimpleNamespace(
            system="lorenz63",
            noise=0.01,
            ctx=ctx,
            setup=SimpleNamespace(model_step=None),
            splits={"test": SimpleNamespace(moments=moments)},
            oracles={"test": SimpleNamespace(growth=growth)},
        ),
        growth,
    )


def test_lambda_fin_variant_shares_the_h2a_two_part_generator_and_the_directions_across_scales(
    monkeypatch,
) -> None:
    """P9: the Lambda_fin variant matches H2a(ii) when set to Lambda_tilde.

    The match is bit for bit, at any perturbation scale.

    Reference (M4 of the mathematics check).

    (a) The finite-growth function is stubbed to return the cell's own
    ``Lambda_tilde`` per window step. Then the variant's statistic is the same
    two-part statistic on the same index sets, so its partial correlations and
    both intervals equal the ones that ``analysis.h2a_separation`` reports,
    bit for bit (``==``; there is no tolerance, because the operations are
    identical, on identical arrays, from identical generators).

    (b) The generator handed to ``make_finite_growth`` has the state of a fresh
    ``make_rng(seed, system, "finite-growth")`` at both scales 1 and 3 (a fresh
    one per call, with no scale in the label, so the same directions are used
    at every scale). That state differs from a generator on another system's
    label.
    """
    from lpcstudy import analysis as an
    from lpcstudy import experiments
    from lpcstudy.data import make_rng

    config = dataclasses.replace(
        SMOKE,
        bootstrap_resamples=60,
        eval_horizons_lyapunov=(1.0, 2.0),
        perturbation_scales=(1.0, 3.0),
    )
    cell, growth = _variant_cell(np.random.default_rng(14009))
    received: list[dict] = []

    def stub(
        step_fn, observed_index, obs_scale, unwhiten, n_steps, n_dirs, rng
    ):
        received.append(rng.bit_generator.state)
        return lambda states, eps: np.asarray(growth)[: len(states)]

    monkeypatch.setattr(experiments, "make_finite_growth", stub)
    study = SimpleNamespace(config=config)
    h2a = an.h2a_separation(cell, config)["part_ii"]
    assert not np.isnan(h2a["zero"]["partial_corr"])
    assert not np.isnan(h2a["interior"]["partial_corr"])
    for scale in (1.0, 3.0):
        out = experiments._perturbation_scale_variant(study, cell, None, scale)
        assert out["H2a_partial_corr_zero_fin"] == h2a["zero"]["partial_corr"]
        assert (
            out["H2a_partial_corr_interior_fin"]
            == h2a["interior"]["partial_corr"]
        )
        assert out["ci_zero"] == h2a["zero"]["ci"]
        assert out["ci_interior"] == h2a["interior"]["ci"]
    fresh = make_rng(
        config.seed, "lorenz63", "finite-growth"
    ).bit_generator.state
    assert received == [fresh, fresh]
    assert (
        make_rng(config.seed, "rossler", "finite-growth").bit_generator.state
        != fresh
    )


def test_fitted_record_keeps_the_existing_leaves_and_adds_the_integer_and_digest_leaves() -> (
    None
):
    """WU-0003.7a (a2, a3, a4): ``fitted_record`` adds leaves to the old ones.

    The record is the old ``fitted`` block plus ``nfev`` and ``status`` of both
    proxies, ``a5_leaf_digest`` and ``allocator_digest``, in that order.

    Reference: a hand-built world.

    1. The A5 tree is a manufactured stump on the profile coordinate
       ``Lambda_hat / lambda_max`` (= ``growth_proxy * steps_per_lyapunov``).
       It is fitted on the two points 0 and 1 with the other three coordinates
       constant, so its one split is 0.5: by hand, a coordinate <= 0.5 is node
       1 and a coordinate above is node 2. The growth values are 0.0, 0.01
       (0.3), 0.02 (0.6) and 0.04 (1.2), far from the split, and the leaf of
       every (state, draw) is decided by hand. The digest is
       ``hashlib.sha256`` of those leaves packed as little-endian int64 with
       ``struct``, calibration first and test second, in C order.
    2. The allocator digest is ``hashlib.sha256`` of the allocator network's
       weight and bias values (binary64, row-major) packed with ``struct``.
    3. The integer leaves are the typed values 11, 2, 5, 1.
    4. The existing leaves are the hand values of the fields they read.

    A decoy map under a second K, split at 0.1, must not be hashed while K = 2
    is chosen, and is hashed when K = 3 is chosen. Moving one calibration state
    across the split changes ``a5_leaf_digest`` and nothing else. All results
    are exact.
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
            horizons=np.arange(1, 4),
            cp_err=zeros,
            plp_err=zeros,
            verify_noise=zeros,
            distance=np.full((n, e), 0.02),
            est_nu=np.ones((n, e)),
            growth_proxy=growth,
            gain_proxy=zeros,
            inputs=np.zeros((n, e, 1)),
            noise_sens=np.zeros((n, e)),
        )

    cal_growth = np.array([[0.0, 0.01], [0.02, 0.04], [0.01, 0.01]])
    test_growth = np.array([[0.04, 0.0], [0.02, 0.01]])
    core = SimpleNamespace(
        noise=0.01,
        splits={
            "calibration": SimpleNamespace(evals=draws(cal_growth)),
            "test": SimpleNamespace(evals=draws(test_growth)),
        },
    )
    fit = np.zeros((2, 4))
    fit[:, 2] = [0.0, 1.0]
    tree = DecisionTreeRegressor(max_leaf_nodes=2, random_state=0).fit(
        fit, [0.0, 1.0]
    )
    leaf_ids = np.nonzero(tree.tree_.children_left == -1)[0]
    assert tree.tree_.feature[0] == 2 and tree.tree_.threshold[0] == 0.5
    regime_map = RegimeMap(
        tree=tree,
        leaf_ids=leaf_ids,
        weights=np.full((2, 30), 0.25),
        horizons_km=np.array([60.0, 90.0]),
    )
    # R2 of the review: a decoy map under another K, split at 0.1 instead of
    # 0.5 (fitted on 0 and 0.2), so that hashing any other K than
    # ``chosen_regimes`` gives a different digest.
    fit_decoy = np.zeros((2, 4))
    fit_decoy[:, 2] = [0.0, 0.2]
    decoy_tree = DecisionTreeRegressor(max_leaf_nodes=2, random_state=0).fit(
        fit_decoy, [0.0, 1.0]
    )
    assert decoy_tree.tree_.feature[0] == 2
    assert decoy_tree.tree_.threshold[0] == pytest.approx(0.1)
    decoy_map = RegimeMap(
        tree=decoy_tree,
        leaf_ids=np.nonzero(decoy_tree.tree_.children_left == -1)[0],
        weights=np.full((2, 30), 0.75),
        horizons_km=np.array([30.0, 30.0]),
    )
    params = [
        (np.array([[0.1, 0.2], [0.3, 0.4]]), np.array([0.5, -0.5])),
        (np.array([[1.0], [2.0]]), np.array([1e-7])),
    ]
    network = TrainedNetwork(
        params=params,
        in_mean=np.zeros(2),
        in_scale=np.ones(2),
        out_mean=np.zeros(1),
        out_scale=np.ones(1),
        val_loss=0.0,
        width=2,
    )
    rules = SimpleNamespace(
        proxies=ProfileProxies(
            SeedProxy(1.0, 2.0, nfev=11, status=2),
            SeedProxy(0.5, 0.25, nfev=5, status=1),
            nu_cap=7.5,
        ),
        predictor=SimpleNamespace(network=network),
        regimes={2: regime_map, 3: decoy_map},
        chosen_regimes=2,
    )

    def hand_leaves(*growths: np.ndarray, split: float = 0.5) -> str:
        leaves = [
            1 if g * lt <= split else 2
            for growth in growths
            for g in growth.ravel()
        ]
        return hashlib.sha256(
            struct.pack("<%dq" % len(leaves), *leaves)
        ).hexdigest()

    values = [v for w, b in params for a in (w, b) for v in a.ravel().tolist()]
    record = fitted_record(core, rules, cfg)
    assert list(record) == [
        "analog_proxy",
        "estimation_proxy",
        "nu_cap",
        "chosen_K",
        "regime_weights_href",
        "regime_horizons_km_lyapunov",
        "a5_leaf_digest",
        "allocator_digest",
    ]
    assert record["analog_proxy"] == {
        "slope": 1.0,
        "floor": 2.0,
        "nfev": 11,
        "status": 2,
    }
    assert record["estimation_proxy"] == {
        "slope": 0.5,
        "floor": 0.25,
        "nfev": 5,
        "status": 1,
    }
    assert record["nu_cap"] == 7.5 and record["chosen_K"] == 2
    assert record["regime_weights_href"] == {
        "2": [0.25, 0.25],
        "3": [0.75, 0.75],
    }
    assert record["regime_horizons_km_lyapunov"] == {
        "2": [2.0, 3.0],
        "3": [1.0, 1.0],
    }
    assert record["a5_leaf_digest"] == hand_leaves(cal_growth, test_growth)
    assert (
        record["allocator_digest"]
        == hashlib.sha256(
            struct.pack("<%dd" % len(values), *values)
        ).hexdigest()
    )
    moved = cal_growth.copy()
    moved[2, 0] = 0.04  # was 0.01: node 1 becomes node 2
    core.splits["calibration"].evals = draws(moved)
    again = fitted_record(core, rules, cfg)
    assert (
        again["a5_leaf_digest"]
        == hand_leaves(moved, test_growth)
        != record["a5_leaf_digest"]
    )
    assert {k: v for k, v in again.items() if k != "a5_leaf_digest"} == {
        k: v for k, v in record.items() if k != "a5_leaf_digest"
    }
    # The digest follows the chosen K: the decoy's digest is different, and
    # choosing K = 3 gives it.
    assert (
        hand_leaves(cal_growth, test_growth, split=0.1)
        != record["a5_leaf_digest"]
    )
    rules.chosen_regimes = 3
    assert fitted_record(core, rules, cfg)["a5_leaf_digest"] == hand_leaves(
        moved, test_growth, split=0.1
    )


# ------------------------------- V4 arrays for the state dump (WU-0003.7b)
def _v4_world(
    monkeypatch,
    tmp_path,
    perturb=None,
    clips=None,
    nan=False,
    signed_zero=False,
):
    """Build two real ``Study`` objects (dump off and on) with one stub.

    Both studies use the same stubbed ``forecast_draws``. The planned errors at
    horizon ``h`` for global row i and draw j are ``cp0[i, j] (1 + h / 100)``
    (CP) and ``plp0[i, j] + 0.1 h / 30`` (PLP), so a column's value does not
    depend on which other horizons were requested. The option ``perturb`` (a
    number) may be added to the PLP error of the first column when three
    horizons are requested (a broken second call), and ``clips`` may set the
    entry counts of that call.
    """
    from lpcstudy import experiments
    from lpcstudy.dump import StateDump
    from lpcstudy.ensemble import DRAW_COUNTERS, DrawBatch
    from lpcstudy.pipeline import Study

    n_states, n_draws = SMOKE.convergence_states, max(SMOKE.convergence_draws)
    rng = np.random.default_rng(4107)
    cp0 = rng.standard_normal((n_states, n_draws))
    plp0 = rng.standard_normal((n_states, n_draws))
    if nan:  # An unclipped NaN PLP error in both calls (the same entry).
        plp0[0, 0] = np.nan
    calls: list[list[int]] = []

    def errors(rows, horizons):
        h = np.asarray(horizons, dtype=float)
        cp = cp0[rows][:, :, None] * (1.0 + h / 100.0)
        plp = plp0[rows][:, :, None] + 0.1 * h / 30.0
        if perturb is not None and len(h) == 3:
            plp[:, :, 0] += perturb
        if signed_zero and rows[0] == 0:
            # Global state 0, draw 0: zero with the other sign in the
            # three-horizon call.
            plp[0, 0, 0] = -0.0 if len(h) == 3 else 0.0
        return cp, plp

    def fake(
        setup,
        library,
        split,
        rows,
        unit_noise,
        horizons,
        reference_horizon=None,
    ):
        calls.append([int(h) for h in horizons])
        cp, plp = errors(rows, horizons)
        entries = {
            "error_clips_cp": 0,
            "error_clips_plp": 0,
            "error_clips_nonfinite": 0,
        }
        if clips is not None and len(horizons) == 3:
            entries.update(clips)
        ones = np.ones((len(rows), n_draws))
        return DrawBatch(
            cp_err=cp,
            plp_err=plp,
            analog_seed_sq=None,
            est_seed_sq=None,
            distance=None,
            inputs=None,
            est_states=None,
            est_nu=None,
            analog_vecs=None,
            handled=np.ones((len(rows), len(DRAW_COUNTERS)), dtype=np.int64),
            clip_entries=entries,
            lm_residual=ones,
            lm_accepted=ones.astype(int),
            lm_late=ones.astype(int),
        )

    monkeypatch.setattr(experiments, "forecast_draws", fake)
    monkeypatch.setattr(
        experiments.AnalogLibrary,
        "build",
        classmethod(lambda cls, *a, **k: None),
    )
    studies = []
    for name in ("off", "on"):
        study = Study(SMOKE, tmp_path / name)
        study.unit_noise = lambda *a, **k: np.zeros((n_states + 5, n_draws, 7))
        studies.append(study)
    studies[1].dump = StateDump()
    cell = SimpleNamespace(
        system="lorenz63",
        label="base",
        noise=0.01,
        library_size=10_000,
        ctx=SimpleNamespace(embed_dim=7, spec=SimpleNamespace(dim=3)),
        setup=None,
    )
    return studies, cell, calls, errors


def _ref_weight(c: np.ndarray, p: np.ndarray) -> np.ndarray:
    """Return the V4 weight written from its definition.

    That is ``clip(E[p (p - c)] / E[(c - p)^2], 0, 1)``.
    """
    return np.clip(
        np.mean(p * (p - c), axis=-1)
        / np.maximum(np.mean((c - p) ** 2, axis=-1), 1e-300),
        0,
        1,
    )


def test_convergence_check_with_the_dump_gives_the_same_leaves_and_the_v4_arrays(
    monkeypatch, tmp_path
) -> None:
    """With the dump on, V4 gives the same results and the dump holds V4 values.

    What is checked: the V4 result and its handling record equal those of the
    dump-off run bit for bit, and the arrays written for the dump equal the V4
    values recomputed by hand.

    Reference: formulas written in the test. The planned errors (see
    ``_v4_world``) give the weight ``clip(E[p (p - c)] / E[(c - p)^2], 0, 1)``
    from the first ``M`` draws, per state and horizon (1, 2, 4 LT = 30, 60, 120
    steps). The signed deviation is that weight minus the weight from all
    draws. The half-width is half the distance between the 97.5 and 2.5
    percentiles of 200 bootstrap weights, whose index sets the test draws
    again from an independent ``np.random.default_rng([seed, crc32(label)])``
    in the production order (one ``integers(0, M, (200, M))`` per ``M``).

    Tolerances:

    * the leaves and the record are compared bit for bit (the dump changes
      nothing, because the production code path is the same);
    * ``w_hat``, ``signed_dev`` and ``half_width`` are compared to
      ``rtol = 1e-13`` (each is a mean of at most 30 products, with
      gamma_30 = 3.3e-15, or a percentile of such values: a factor of 30 of
      margin);
    * the b5 pair (the median of the ``H_ref`` half-widths and the mean
      absolute deviation, against the leaves) is compared bit for bit, since
      the leaves are computed from the same arrays.

    Also: the production call asked for ``H_ref`` only, and the dump's second
    call for 30, 60 and 120 (only with the dump on). The flag
    ``extra_href_equal`` is True. No random number is drawn that the dump-off
    run does not draw (the leaves are equal).
    """
    import zlib

    from lpcstudy import experiments

    (off, on), cell, calls, errors = _v4_world(monkeypatch, tmp_path)
    out_off = experiments.convergence_check(off, cell)
    n_off = len(calls)
    assert all(c == [30] for c in calls)
    out_on = experiments.convergence_check(on, cell)
    assert out_on == out_off and off._records == on._records
    assert {tuple(c) for c in calls[n_off:]} == {(30,), (30, 60, 120)}
    v4 = on.dump._v4["lorenz63"]
    n_states, n_draws = SMOKE.convergence_states, max(SMOKE.convergence_draws)
    assert v4["M"].tolist() == list(SMOKE.convergence_draws)
    assert v4["horizons"].tolist() == [30, 60, 120]
    assert bool(v4["extra_href_equal"])
    cp, plp = errors(np.arange(n_states), [30, 60, 120])
    ref = np.stack(
        [_ref_weight(cp[:, :, j], plp[:, :, j]) for j in range(3)], axis=1
    )
    assert v4["w_ref"].shape == (n_states, 3)
    np.testing.assert_allclose(v4["w_ref"], ref, rtol=1e-13, atol=0.0)
    label = b"lorenz63|V4-convergence"
    rng = np.random.default_rng([SMOKE.seed, zlib.crc32(label)])
    for mi, m in enumerate(SMOKE.convergence_draws):
        base = np.stack(
            [_ref_weight(cp[:, :m, j], plp[:, :m, j]) for j in range(3)], axis=1
        )
        idx = rng.integers(0, m, (200, m))
        for j in range(3):
            boots = np.stack(
                [_ref_weight(cp[:, i, j], plp[:, i, j]) for i in idx]
            )
            half = 0.5 * (
                np.percentile(boots, 97.5, axis=0)
                - np.percentile(boots, 2.5, axis=0)
            )
            np.testing.assert_allclose(
                v4["half_width"][mi, :, j], half, rtol=1e-13, atol=0.0
            )
        np.testing.assert_allclose(v4["w_hat"][mi], base, rtol=1e-13, atol=0.0)
        np.testing.assert_allclose(
            v4["signed_dev"][mi], base - ref, rtol=0.0, atol=1e-13
        )
        leaf = out_on[str(m)]
        assert (
            float(np.median(v4["half_width"][mi, :, 0]))
            == leaf["median_half_width"]
        )
        assert (
            float(np.mean(np.abs(v4["signed_dev"][mi, :, 0])))
            == leaf["mean_abs_dev_from_max"]
        )
    assert v4["extra_handled"].shape == (n_states, 8)
    assert v4["extra_clip_entries"].tolist() == [0, 0, 0]
    assert v4["extra_clip_entry_names"].tolist() == [
        "error_clips_cp",
        "error_clips_plp",
        "error_clips_nonfinite",
    ]


def test_convergence_check_dump_flags_a_second_call_whose_href_column_differs(
    monkeypatch, tmp_path, caplog
) -> None:
    """A broken second forecast is not silent.

    What is checked: ``extra_href_equal`` is False, one WARNING is written, and
    the production leaves are unchanged.

    Reference: the stub adds 1e-9 to the ``H_ref`` PLP column of the
    three-horizon call only. The bitwise comparison with the production column
    must then be False (a defect of the dump would show as a difference, never
    as a pass). The V4 leaves still equal the dump-off ones, and one WARNING
    line names the number of differing entries: all 10 x 30 PLP entries (R5 of
    the review).
    """
    import logging

    from lpcstudy import experiments

    (off, on), cell, _, _ = _v4_world(monkeypatch, tmp_path, perturb=1e-9)
    with caplog.at_level(logging.WARNING, logger="lpcstudy"):
        out_on = experiments.convergence_check(on, cell)
    assert out_on == experiments.convergence_check(off, cell)
    v4 = on.dump._v4["lorenz63"]
    assert (
        bool(v4["extra_href_equal"]) is False
        and int(v4["extra_href_diff"]) == 300
    )
    lines = [
        r.getMessage()
        for r in caplog.records
        if "H_ref errors of the second" in r.getMessage()
    ]
    assert len(lines) == 1 and "300 of 600 entries" in lines[0]


def test_convergence_check_dump_treats_an_identical_nan_as_unequal(
    monkeypatch, tmp_path, caplog
) -> None:
    """Strict comparison (amendment 4, D3): a NaN differs from another NaN.

    Reference: the plan text of D3 ("a NaN counts as unequal"). The stub puts
    the same NaN PLP entry in the production and the second forecast. Then
    ``extra_href_equal`` is False, ``extra_href_diff`` is 1 (one entry of the
    600) and one WARNING says so. (Round 1 had adopted the looser reading, NaN
    equal to NaN; round 2 withdrew it, R9 of the re-review.) The results are
    exact.
    """
    import logging

    from lpcstudy import experiments

    (_, on), cell, _, _ = _v4_world(monkeypatch, tmp_path, nan=True)
    with caplog.at_level(logging.WARNING, logger="lpcstudy"):
        experiments.convergence_check(on, cell)
    v4 = on.dump._v4["lorenz63"]
    assert (
        bool(v4["extra_href_equal"]) is False
        and int(v4["extra_href_diff"]) == 1
    )
    lines = [
        r.getMessage()
        for r in caplog.records
        if "H_ref errors of the second" in r.getMessage()
    ]
    assert len(lines) == 1 and "1 of 600 entries" in lines[0]
    assert "NaN counts as different" in lines[0]


def test_convergence_check_dump_compares_bit_patterns_so_signed_zeros_differ(
    monkeypatch, tmp_path, caplog
) -> None:
    """The values +0.0 and -0.0 count as a mismatch (the comparison is bitwise).

    Reference: the plan text of D3 ("bitwise") and IEEE 754: the two zeros are
    ``==`` but have different bit patterns. The stub gives one PLP entry the
    value 0 with the sign + in the production call and the sign - in the
    three-horizon call. Expected: one differing entry and one WARNING. The
    results are exact.
    """
    import logging

    from lpcstudy import experiments

    (_, on), cell, _, _ = _v4_world(monkeypatch, tmp_path, signed_zero=True)
    with caplog.at_level(logging.WARNING, logger="lpcstudy"):
        experiments.convergence_check(on, cell)
    v4 = on.dump._v4["lorenz63"]
    assert (
        bool(v4["extra_href_equal"]) is False
        and int(v4["extra_href_diff"]) == 1
    )
    matching = [
        r
        for r in caplog.records
        if "H_ref errors of the second" in r.getMessage()
    ]
    assert len(matching) == 1


def test_convergence_check_dump_counts_and_logs_the_clips_of_its_second_forecast(
    monkeypatch, tmp_path, caplog
) -> None:
    """The dump-only forecasts count their clips in the dump and log them once.

    The ``handling`` record is unchanged, because the run does not use these
    forecasts.

    Reference: the stub reports 3 CP clips and 2 non-finite entries per batch
    of the three-horizon call (two batches of five states), so the totals are
    [6, 0, 4]. One WARNING line from the ``lpcstudy`` logger names V4 and
    ``states/lorenz63.npz``. The handling record of the dump-on study equals
    the dump-off one. The results are exact.
    """
    import logging

    from lpcstudy import experiments

    (off, on), cell, _, _ = _v4_world(
        monkeypatch,
        tmp_path,
        clips={"error_clips_cp": 3, "error_clips_nonfinite": 2},
    )
    experiments.convergence_check(off, cell)
    with caplog.at_level(logging.WARNING, logger="lpcstudy"):
        experiments.convergence_check(on, cell)
    assert on.dump._v4["lorenz63"]["extra_clip_entries"].tolist() == [6, 0, 4]
    lines = [
        r.getMessage()
        for r in caplog.records
        if "V4 dump forecasts" in r.getMessage()
    ]
    assert len(lines) == 1 and "states/lorenz63.npz" in lines[0]
    # R4: the line says what it counts: all three horizons (H_ref, 2 and 4 LT)
    # of 10 x 30 draws.
    assert "H_ref, 2 and 4 LT" in lines[0] and " of 900;" in lines[0]
    assert off._records == on._records


# ------------------------------------ WU-0004f: skipped_variants in results
def test_run_handling_writes_the_skipped_variants_count_a6(
    tmp_path, caplog
) -> None:
    """A6 (WU-0004f): ``handling.skipped_variants`` counts labels, all systems.

    Reference: hand counts. Two systems with 1 and 2 skipped labels give 3. No
    skipped label gives 0 (the key is present, it is an ``int``, and no WARNING
    is written). The other keys are the same as without skips,
    ``failed_variants`` is independent, and the block survives
    ``json.dumps``. The results are exact.
    """
    import json
    import logging

    from lpcstudy.experiments import run_handling
    from lpcstudy.pipeline import Study

    study = Study(SMOKE, tmp_path)
    study.skipped_variants = {"lorenz63": ["D=3"], "rossler": ["D=2", "D=3"]}
    study.failed_variants = {"chua": ["misspec=0.05"]}
    run = run_handling(study, {"systems": {}})
    assert run["skipped_variants"] == 3 and run["failed_variants"] == 1
    assert type(run["skipped_variants"]) is int
    assert json.loads(json.dumps(run)) == run
    clean = Study(SMOKE, tmp_path)
    caplog.clear()
    with caplog.at_level(logging.WARNING, logger="lpcstudy"):
        none = run_handling(clean, {"systems": {}})
    assert (
        none["skipped_variants"] == 0 and type(none["skipped_variants"]) is int
    )
    assert not [r for r in caplog.records if r.levelno >= logging.WARNING]
    assert list(none) == list(run)


def test_result_count_keys_include_the_clip_sensitivity_counters_a8() -> None:
    """A8 (WU-0004f): the walker mirrors the new clip-sensitivity counters.

    Reference: a hand ``clip_sensitivity`` block and the expected path map,
    written out. The mirrored ints are ``n_caught_exceptions`` (block level)
    and ``n_floored`` and ``n_floored_2L`` of the H1b part. The count
    ``n_clipped_inputs`` and the other ints (sizes of the clipped sets) are not
    copied. The test also keeps the guard of WU-0002.11 A13 for these names:
    each name is in the set of counted keys.
    """
    from lpcstudy.experiments import RESULT_COUNT_KEYS, collect_result_counts

    block = {
        "clip_sensitivity": {
            "status": "computed",
            "n_caught_exceptions": 2,
            "href_clipped_draws": {"test_eval": 5},
            "by_hypothesis": {
                "H1b": {
                    "parts": {
                        "PLP": {
                            "status": "computed",
                            "n_clipped_inputs": 9,
                            "n_floored": 4,
                            "n_floored_2L": 1,
                        }
                    },
                    "flag": False,
                }
            },
        }
    }
    assert collect_result_counts(block) == {
        "clip_sensitivity/n_caught_exceptions": 2,
        "clip_sensitivity/by_hypothesis/H1b/parts/PLP/n_floored": 4,
        "clip_sensitivity/by_hypothesis/H1b/parts/PLP/n_floored_2L": 1,
    }
    assert {
        "n_caught_exceptions",
        "n_floored",
        "n_floored_2L",
    } <= RESULT_COUNT_KEYS
