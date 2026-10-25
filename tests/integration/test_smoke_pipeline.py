"""End-to-end plumbing check: run the smoke preset and inspect its output files.

The "smoke" preset is a small, fast version of the whole study (about a minute).
It exercises every stage: simulate the chaotic systems, train the networks, run
both forecasters, count every clip or replacement, compute the statistics and
write the report. This module runs it once with ``python -m lpcstudy`` and
checks that the output files exist and that the structure of ``results.json``
has the promised pieces: the validation gate flag, the P2(c) bound check (a
numerical bound that must hold), the Levenberg-Marquardt (LM) state-estimator
summaries, the clip-sensitivity block, the new digests of WU-0003.7a, and the
``handling`` block that counts everything the code clipped, replaced or dropped
(PRIME.4). It checks the plumbing and the schema, not the scientific answer
(WU-0010.3). The helper functions ``assert_*`` hold the checks of each part.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

from lpcstudy.config import SMOKE
from lpcstudy.experiments import RESULT_COUNT_KEYS
from lpcstudy.pipeline import ALL_COUNTERS, cell_id

REPO_ROOT = Path(__file__).resolve().parents[2]
TIMEOUT_SECONDS = 300


def test_smoke_preset_writes_outputs_and_gate_flag(tmp_path: Path) -> None:
    """``python -m lpcstudy --preset smoke`` writes its outputs and a
    true-or-false gate flag.

    Reference: the output rules of ``lpcstudy/__main__.py``
    (``<out>/smoke/results.json``, ``RESULTS.md``, ``run.log`` and
    ``figures/*.png``) and the schema of the baseline
    ``runs/baseline/smoke/results.json``
    (``systems.<s>.validation.gate.gate_pass``). This is a plumbing check, not
    correctness evidence: it does not assert that the gate passes. Its only
    bound is the 300 s timeout of the DEVELOPMENT_WORKFLOW.md section 4.1 budget
    (the baseline took 49 s). No seed argument is passed, so the run uses the
    default 20261005 (DEV-0).
    """
    env = {
        **os.environ,
        "JAX_PLATFORMS": "cpu",
        "XLA_PYTHON_CLIENT_PREALLOCATE": "false",
    }
    done = subprocess.run(
        [
            sys.executable,
            "-m",
            "lpcstudy",
            "--preset",
            "smoke",
            "--out",
            str(tmp_path),
        ],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        timeout=TIMEOUT_SECONDS,
    )
    stderr_tail = "\n".join(
        done.stderr.decode(errors="replace").splitlines()[-20:]
    )
    assert (
        done.returncode == 0
    ), f"smoke preset exited {done.returncode}; stderr tail:\n{stderr_tail}"
    out_dir = tmp_path / "smoke"
    for name in ("results.json", "RESULTS.md", "run.log"):
        assert (
            out_dir / name
        ).is_file(), f"{name} missing; stderr tail:\n{stderr_tail}"
    assert (out_dir / "figures").is_dir()
    assert list(
        (out_dir / "figures").glob("*.png")
    ), "figures/ has no .png file"
    systems = json.loads((out_dir / "results.json").read_text())["systems"]
    assert systems
    for name, result in systems.items():
        assert isinstance(result["validation"]["gate"]["gate_pass"], bool), name
        # WU-0005.5 (P1): the P2(c) check runs on the core cell's own draws and
        # finds no violation.
        p2c = result["verification"]["P2c"]
        assert (
            p2c["n_violations"] == 0 and p2c["same_draws_identical"] is True
        ), name
    results = json.loads((out_dir / "results.json").read_text())
    assert_handling(results)
    assert_lm_rows(results, (out_dir / "RESULTS.md").read_text().splitlines())
    assert_clip_sensitivity(
        results, (out_dir / "RESULTS.md").read_text().splitlines()
    )
    assert_wu0003_7a_leaves(results)
    assert_ablation(results, (out_dir / "RESULTS.md").read_text().splitlines())


def assert_ablation(results: dict, report_lines: list[str]) -> None:
    """Check the ``ablation`` block of each system (WU-0039b, ROADMAP WU-0039).

    On the real pipeline: the unchanged A4 proxies, rescored, reproduce the
    stored A4 per-state MSE bitwise (``reproduces_A4``); the four-column A5
    refit reproduces A5 (``reproduces_A5``); the drop-N leave-one-out row
    equals the stored Q-N leaves bitwise for both profiles and all three
    targets (float hex); the Shapley shares sum to
    ``R^2(F) - R^2(empty)`` within 1e-12 (round-off of eight weighted
    differences of O(1) values); and the report has the section heading.
    """
    for name, system in results["systems"].items():
        block = system["ablation"]
        a4 = block["A4_coefficients"]
        assert a4["full"]["reproduces_A4"] is True, name
        assert block["A5_without_condition"]["full"]["reproduces_A5"] is True
        for kind in ("oracle", "deployable"):
            for target, entry in block["profile_conditions"][kind].items():
                qn = system["Q-N"][kind][target]
                drop_n = entry["leave_one_out"]["N"]
                for got, want in (
                    (drop_n["delta_r2"], qn["delta_r2"]),
                    (drop_n["r2_without"], qn["r2_three"]),
                    (entry["r2_by_subset"]["ROIN"], qn["r2_four"]),
                    *zip(drop_n["ci"], qn["ci"]),
                ):
                    assert got.hex() == want.hex(), (name, kind, target)
                assert drop_n["n_failed_resamples"] == qn["n_failed_resamples"]
                gap = entry["shapley_sum"] - entry["r2_full_minus_empty"]
                assert abs(gap) <= 1e-12, (name, kind, target, gap)
    assert "## Ablations (estimates, no verdict)" in report_lines


def assert_wu0003_7a_leaves(results: dict) -> None:
    """WU-0003.7a on the smoke run: the new leaves are present, typed and
    JSON-clean.

    These leaves are "bitwise neutral": adding them changed no other number.
    Reference: the plan (B2 row .7a). Per system: ``context.main_digest`` and
    ``estimator_digest``; ``fitted.<proxy>.nfev`` and ``status`` of both proxy
    fits; ``fitted.a5_leaf_digest`` and ``fitted.allocator_digest``. Also
    ``weights_digest`` in every entry of ``estimators`` (top level and
    ``validation.estimators``). A digest is a fingerprint of 64 lowercase
    hexadecimal characters. ``nfev`` (number of function evaluations) is a
    positive int and ``status`` is one of the documented ``least_squares``
    statuses (-1 to 4). The values are checked against independent
    recomputations in the unit tests, so only the schema is asserted here, plus
    that the four per-system digests are pairwise different (a constant would
    pass the schema). The checks are exact.

    The two estimator blocks do not hold the same keys:
    ``systems.<s>.validation.estimators`` is a snapshot taken in ``run_system``
    after the core cell and before the noise sweep, so an estimator trained
    later (the 0.02 noise level at smoke) is only in the top-level
    ``estimators``. Where a key is in both, the entries are the same object, so
    the digests agree (WU-0003.7a review R1).
    """
    digest = re.compile(r"[0-9a-f]{64}")
    for name, system in results["systems"].items():
        seen: set[str] = set()
        for leaf in ("main_digest", "estimator_digest"):
            seen.add(system["context"][leaf])
            assert digest.fullmatch(system["context"][leaf]), (name, leaf)
        for proxy in ("analog_proxy", "estimation_proxy"):
            fit = system["fitted"][proxy]
            assert type(fit["nfev"]) is int and fit["nfev"] >= 1, (name, proxy)
            assert type(fit["status"]) is int and fit["status"] in range(
                -1, 5
            ), (name, proxy)
        for leaf in ("a5_leaf_digest", "allocator_digest"):
            seen.add(system["fitted"][leaf])
            assert digest.fullmatch(system["fitted"][leaf]), (name, leaf)
        logs = [results["estimators"], system["validation"]["estimators"]]
        for log in logs:
            assert log, name
            for key, entry in log.items():
                assert digest.fullmatch(entry["weights_digest"]), (name, key)
        assert len(seen) == 4, name


def assert_clip_sensitivity(results: dict, report_lines: list[str]) -> None:
    """WU-0002.11e (T6 on the smoke run): the clip-sensitivity block is computed
    and well formed.

    Where no clipped entry feeds a part, that part must have a change (delta) of
    exactly 0.0, no flag and the same verdict.

    Reference: the definition of the perturbation. The study clips some values
    at 10 sigma_x (ten standard deviations of x) and the block recomputes with
    the clip at 20 sigma_x. A part with no clipped input is the same computation
    on the same arrays, so its change is 0.0 bitwise. A flag that is False
    implies that the verdict at 20 sigma_x equals the verdict. A part that
    cannot be computed says why and has no flag (never False). The block sits
    outside ``handling`` and every hypothesis key, and RESULTS.md has the
    ``clip`` column. The checks are exact.
    """
    for name, system in results["systems"].items():
        block = system["clip_sensitivity"]
        assert block["status"] == "computed", (name, block["reason"])
        assert (block["clip_level"], block["perturbed_level"]) == (
            10.0,
            20.0,
        ), name
        assert "clip_sensitivity" not in system["handling"], name
        parts = [
            (h, n, part)
            for h, entry in block["by_hypothesis"].items()
            for n, part in entry["parts"].items()
        ]
        assert parts, name
        for hypothesis, part_name, part in parts:
            where = (name, hypothesis, part_name)
            if part["status"] != "computed":
                assert part["reason"] and part["flag"] is None, where
            elif part["n_clipped_inputs"] == 0:
                assert part.get("delta", part.get("delta_bound")) == 0.0, where
                assert part["flag"] is False, where
    header = next(
        line for line in report_lines if line.startswith("| ID | Hypothesis |")
    )
    assert header.endswith("| Verdict | clip |")


LM_KEYS = (
    "median_residual",
    "p95_residual",
    "median_iterations",
    "fraction_no_decrease",
)
"""The four keys the ROADMAP row of WU-0005.4 names."""


def assert_lm_rows(results: dict, report_lines: list[str]) -> None:
    """WU-0005.4 (V2 and V3): every handling cell has an ``lm`` block, and
    RESULTS.md shows it.

    Every cell of every system has ``lm`` with the four ROADMAP keys. The count
    of estimates per kind equals the ``estimates`` denominator of the same kind.
    The report has exactly one row per (system, cell, kind) with at least one
    estimate. The core cell has the oracle and eval kinds; the two checks (V3,
    V4) have the check kind only.
    """
    row = re.compile(
        r"^\| \w+ \| `.+` \| (oracle|eval|check) \| \d+ \|"
    )  # ids hold escaped pipes
    rows = [line for line in report_lines if row.match(line)]
    expected = 0
    for name, system in results["systems"].items():
        for block_id, record in system["handling"]["cells"].items():
            lm = record["lm"]
            assert set(LM_KEYS) <= set(lm), (name, block_id)
            assert set(lm["by_kind"]) == {"oracle", "eval", "check"}, (
                name,
                block_id,
            )
            for kind, part in lm["by_kind"].items():
                assert set(LM_KEYS) <= set(part), (name, block_id, kind)
                assert (
                    part["n_estimates"]
                    == record["by_kind"][kind]["denominators"]["estimates"]
                ), (name, block_id, kind)
                expected += part["n_estimates"] > 0
            assert lm["n_estimates"] == record["denominators"]["estimates"], (
                name,
                block_id,
            )
    assert len(rows) == expected > 0, (len(rows), expected)


COUNT_KEY_PATTERN = re.compile(
    r"n_(failed|excluded|nonfinite|dropped|km_not_reached|degenerate|"
    r"floored|constant|empty|exponent|covariance|ineligible|screened|"
    r"zero_difference)|nan_resamples|degenerate_fits|"
    r"zero_variance_corr"
)


def expected_cell_ids(config=SMOKE) -> set[str]:
    """Return the cell ids ``run_system`` should record, derived from the
    configuration (WU-0002.11 V2).

    A "cell" is one setting of the study (noise level and library size). The ids
    are: the core cell; every noise level of the sweep other than the core's;
    every (noise, size) of the library sweep other than the core cell and the
    noise-sweep cells (they are the same cells, recorded once); and the two
    checks that draw their own forecasts.
    """
    ids = {
        cell_id("base", config.core_noise, config.core_library, True),
        "V3-cp-horizon",
        "V4-convergence",
    }
    ids |= {
        cell_id("base", rho, config.core_library, False)
        for rho in config.noise_levels
        if rho != config.core_noise
    }
    ids |= {
        cell_id("base", rho, size, False)
        for rho in config.library_sweep_noises
        for size in config.library_sizes
        if not (rho == config.core_noise and size == config.core_library)
    }
    return ids


def assert_handling(results: dict) -> None:
    """Check the ``handling`` block of a smoke run (WU-0002.11 V2 and A13).

    The block is where the study counts every value it clipped, replaced or
    dropped, so nothing is handled silently (PRIME.4). Every system has the full
    block with the planned cell ids and every counter as an ``int``. The system
    totals are the sum over its cells, their sub-blocks, the oracle blocks and
    the fit. The run totals are the sum over systems. Every key of the results
    that looks like a count (the pattern of A13) is in ``RESULT_COUNT_KEYS`` or
    is named here as not a handling count.
    """
    assert (
        results["handling"]["schema"] == "lpcstudy.handling/2"
    )  # WU-0005.4 (O1)
    run_total = dict.fromkeys(ALL_COUNTERS, 0)
    for name, system in results["systems"].items():
        block = system["handling"]
        assert set(block) == {
            "schema",
            "cells",
            "oracles",
            "fitting",
            "result_counts",
            "totals",
        }
        assert set(block["cells"]) == expected_cell_ids(), name
        assert set(block["oracles"]) == {
            "construction",
            "calibration",
            "test",
        }, name
        assert set(block["totals"]) == set(ALL_COUNTERS)
        parts = [
            *block["cells"].values(),
            *block["oracles"].values(),
            block["fitting"],
        ]
        parts += [
            c[k]
            for c in block["cells"].values()
            for k in ("evaluation",)
            if k in c
        ]
        for counter in ALL_COUNTERS:
            assert type(block["totals"][counter]) is int, counter
            assert block["totals"][counter] == sum(
                int(p["counts"].get(counter, 0)) for p in parts
            ), (name, counter)
            run_total[counter] += block["totals"][counter]
        assert all(type(v) is int for v in block["result_counts"].values())
        assert "invariant_mean_replacements" in system["V7"]
    assert results["handling"]["totals"] == run_total
    assert results["handling"]["failed_variants"] == 0

    # A13 guard: every count-like key of the results is copied by the walker.
    not_handling = {
        "n_noncontiguous_states"
    }  # a property of a statistic (does not match anyway)

    def keys(node: object):
        if isinstance(node, dict):
            for key, value in node.items():
                yield str(key)
                yield from keys(value)
        elif isinstance(node, list):
            for value in node:
                yield from keys(value)

    hypotheses = {
        name: {k: v for k, v in system.items() if k != "handling"}
        for name, system in results["systems"].items()
    }
    found = {
        k for k in keys(hypotheses) if COUNT_KEY_PATTERN.search(k)
    } - not_handling
    missing = {k for k in found if k not in RESULT_COUNT_KEYS}
    assert (
        not missing
    ), f"count-like result keys not in RESULT_COUNT_KEYS: {sorted(missing)}"
