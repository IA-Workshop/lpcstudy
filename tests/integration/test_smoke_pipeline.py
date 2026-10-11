"""Smoke-preset plumbing check of the CLI (WU-0010.3)."""

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
    """``python -m lpcstudy --preset smoke`` writes the four outputs and a boolean gate flag.

    Reference: the output contract of ``lpcstudy/__main__.py`` (``<out>/smoke/results.json``,
    ``RESULTS.md``, ``run.log``, ``figures/*.png``) and the schema of the baseline
    ``runs/baseline/smoke/results.json`` (``systems.<s>.validation.gate.gate_pass``).
    This is a plumbing check, not correctness evidence: it does not assert that the
    gate passes. Its only bound is the 300 s timeout of the DEVELOPMENT_WORKFLOW.md
    section 4.1 budget (the baseline took 49 s). No seed argument is passed, so the run
    uses the default 20261005 (DEV-0).
    """
    env = {**os.environ, "JAX_PLATFORMS": "cpu", "XLA_PYTHON_CLIENT_PREALLOCATE": "false"}
    done = subprocess.run(
        [sys.executable, "-m", "lpcstudy", "--preset", "smoke", "--out", str(tmp_path)],
        cwd=REPO_ROOT, env=env, capture_output=True, timeout=TIMEOUT_SECONDS)
    stderr_tail = "\n".join(done.stderr.decode(errors="replace").splitlines()[-20:])
    assert done.returncode == 0, f"smoke preset exited {done.returncode}; stderr tail:\n{stderr_tail}"
    out_dir = tmp_path / "smoke"
    for name in ("results.json", "RESULTS.md", "run.log"):
        assert (out_dir / name).is_file(), f"{name} missing; stderr tail:\n{stderr_tail}"
    assert (out_dir / "figures").is_dir()
    assert list((out_dir / "figures").glob("*.png")), "figures/ has no .png file"
    systems = json.loads((out_dir / "results.json").read_text())["systems"]
    assert systems
    for name, result in systems.items():
        assert isinstance(result["validation"]["gate"]["gate_pass"], bool), name
        # WU-0005.5 (P1): the P2(c) check runs on the core cell's own draws and finds no violation.
        p2c = result["verification"]["P2c"]
        assert p2c["n_violations"] == 0 and p2c["same_draws_identical"] is True, name
    assert_handling(json.loads((out_dir / "results.json").read_text()))


COUNT_KEY_PATTERN = re.compile(r"n_(failed|excluded|nonfinite|dropped|km_not_reached|degenerate|"
                               r"floored|constant|empty)|nan_resamples|degenerate_fits|"
                               r"zero_variance_corr")


def expected_cell_ids(config=SMOKE) -> set[str]:
    """Cell ids ``run_system`` records, derived from the configuration (WU-0002.11 V2).

    The core cell, every noise level of the sweep other than the core's, every (noise, size) of
    the library sweep other than the core cell and the noise-sweep cells (they are the same
    cells, recorded once), and the two checks that draw their own forecasts.
    """
    ids = {cell_id("base", config.core_noise, config.core_library, True), "V3-cp-horizon",
           "V4-convergence"}
    ids |= {cell_id("base", rho, config.core_library, False) for rho in config.noise_levels
            if rho != config.core_noise}
    ids |= {cell_id("base", rho, size, False) for rho in config.library_sweep_noises
            for size in config.library_sizes
            if not (rho == config.core_noise and size == config.core_library)}
    return ids


def assert_handling(results: dict) -> None:
    """The ``handling`` block of a smoke run (WU-0002.11 V2 and A13).

    Every system has the full block with the planned cell ids and every counter as an ``int``;
    the system totals are the sum over its cells, their sub-blocks, the oracle blocks and the
    fit; the run totals are the sum over systems; and every key of the results that looks like a
    count (the pattern of A13) is in ``RESULT_COUNT_KEYS`` or is named here as not a handling count.
    """
    assert results["handling"]["schema"] == "lpcstudy.handling/1"
    run_total = dict.fromkeys(ALL_COUNTERS, 0)
    for name, system in results["systems"].items():
        block = system["handling"]
        assert set(block) == {"schema", "cells", "oracles", "fitting", "result_counts", "totals"}
        assert set(block["cells"]) == expected_cell_ids(), name
        assert set(block["oracles"]) == {"construction", "calibration", "test"}, name
        assert set(block["totals"]) == set(ALL_COUNTERS)
        parts = [*block["cells"].values(), *block["oracles"].values(), block["fitting"]]
        parts += [c[k] for c in block["cells"].values() for k in ("evaluation",) if k in c]
        for counter in ALL_COUNTERS:
            assert type(block["totals"][counter]) is int, counter
            assert block["totals"][counter] == sum(int(p["counts"].get(counter, 0)) for p in parts), \
                (name, counter)
            run_total[counter] += block["totals"][counter]
        assert all(type(v) is int for v in block["result_counts"].values())
        assert "invariant_mean_replacements" in system["V7"]
    assert results["handling"]["totals"] == run_total
    assert results["handling"]["failed_variants"] == 0

    # A13 guard: every count-like key of the results is copied by the walker.
    not_handling = {"n_zero_difference", "n_noncontiguous_states"}  # properties of a statistic

    def keys(node: object):
        if isinstance(node, dict):
            for key, value in node.items():
                yield str(key)
                yield from keys(value)
        elif isinstance(node, list):
            for value in node:
                yield from keys(value)

    hypotheses = {name: {k: v for k, v in system.items() if k != "handling"}
                  for name, system in results["systems"].items()}
    found = {k for k in keys(hypotheses) if COUNT_KEY_PATTERN.search(k)} - not_handling
    missing = {k for k in found if k not in RESULT_COUNT_KEYS}
    assert not missing, f"count-like result keys not in RESULT_COUNT_KEYS: {sorted(missing)}"
