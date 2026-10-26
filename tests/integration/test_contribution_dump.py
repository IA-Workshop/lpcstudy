"""Phase J contribution library on a smoke state dump (WU-0048 (f1), (g)).

One smoke preset with ``--states-dump`` runs on the development seed DEV-0 on
the CPU, in a fresh process (the pattern of ``test_states_dump.py``). Then:

* (f1) ``contribution.check_stored_scores``: ``core/state_mse/<rule>`` is
  recomputed by the library's realized score from the dumped per-draw errors
  and weights (A0 to A4 at every evaluation horizon, A5 at ``H_ref``) within
  1e-12 relative. Reference: the run's own scores (``pipeline.score_rules``,
  an independent code path). Round-off of the recomputation: a blend, a
  square and a mean of ``E`` terms, a few ulps.
* (g) ``contribution.qn_cross_check``: the WU-0039b rows (b1) leave-one-out
  and (b2) Shapley, rebuilt from the dump's split arrays (oracle profile,
  ``w*(H_ref)`` from the full-grid moments, ``ln T`` from ``split/T``), equal
  the run's ``ablation/profile_conditions/oracle`` leaves. Reference: the
  leaves of ``results.json``. Tolerance: bitwise (the same function, the same
  inputs, the same resamples), so drop-N reproduces Q-N's procedure exactly.
* The tool ``tools/lpc_contrib.py`` on the smoke run writes ``contrib.json``
  and ``contrib.md`` with the DEVELOPMENT label before every table (its
  refusals are unit-tested in ``tests/unit/test_tools_lpc_contrib.py``).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from lpcstudy import contribution as cb

REPO_ROOT = Path(__file__).resolve().parents[2]
TIMEOUT_SECONDS = 600
SYSTEM = "lorenz63"


@pytest.fixture(scope="module")
def smoke(tmp_path_factory):
    """Run the smoke preset with the dump once; return the run folder."""
    out = tmp_path_factory.mktemp("contrib") / "run"
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
            "--seed-id",
            "DEV-0",
            "--out",
            str(out),
            "--states-dump",
        ],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        timeout=TIMEOUT_SECONDS,
    )
    tail = "\n".join(done.stderr.decode(errors="replace").splitlines()[-15:])
    assert done.returncode == 0, tail
    run = out / "smoke"
    results = json.loads((run / "results.json").read_text())
    with np.load(run / "states" / f"{SYSTEM}.npz", allow_pickle=False) as z:
        arrays = {k: z[k] for k in z.files}
    return {"run": run, "results": results, "arrays": arrays}


def test_f1_stored_scores_are_recomputed_from_the_per_draw_errors(
    smoke,
) -> None:
    """(f1): every stored per-state MSE within 1e-12 relative."""
    data = cb.SystemData.from_arrays(smoke["arrays"])
    record = cb.check_stored_scores(data)
    assert record["within_1e-12"], record
    assert set(record["max_rel_diff"]) == {"A0", "A1", "A2", "A3", "A4", "A5"}


def test_g_wu0039b_profile_rows_are_reproduced_bitwise_from_the_dump(
    smoke,
) -> None:
    """(g): drop-one (b1) and Shapley (b2) rows equal the run's leaves."""
    cfg = smoke["results"]["config"]
    data = cb.SystemData.from_arrays(smoke["arrays"])
    mine = cb.qn_cross_check(
        data,
        int(cfg["seed"]),
        int(cfg["bootstrap_resamples"]),
        int(cfg["bootstrap_block"]),
    )
    leaves = smoke["results"]["systems"][SYSTEM]["ablation"][
        "profile_conditions"
    ]["oracle"]
    for target, entry in mine.items():
        theirs = leaves[target]
        for x, row in entry["leave_one_out"].items():
            got = theirs["leave_one_out"][x]
            assert row["delta_r2"] == got["delta_r2"], (target, x)
            assert list(row["ci"]) == list(got["ci"]), (target, x)
            assert row["reading"] == got["reading"], (target, x)
            assert row["n_failed_resamples"] == got["n_failed_resamples"]
        for x, row in entry["shapley"].items():
            assert row["share"] == theirs["shapley"][x]["share"], (target, x)
            assert list(row["ci"]) == list(theirs["shapley"][x]["ci"])
        assert entry["r2_by_subset"] == theirs["r2_by_subset"], target


def test_tool_writes_labeled_tables_on_the_smoke_run(smoke, tmp_path) -> None:
    """The CLI on the smoke run: (f1) and (g) pass, every table is labeled."""
    tool = REPO_ROOT / "tools" / "lpc_contrib.py"
    run = smoke["run"]
    env = {**os.environ, "JAX_PLATFORMS": "cpu"}
    out = tmp_path / "out"
    done = subprocess.run(
        [
            sys.executable,
            "-I",
            str(tool),
            str(run),
            "--out",
            str(out),
            "--jobs",
            "4",
        ],
        capture_output=True,
        env=env,
        timeout=TIMEOUT_SECONDS,
    )
    assert done.returncode == 0, done.stderr.decode()[-2000:]
    record = json.loads((out / "contrib.json").read_text())
    label = "DEVELOPMENT (DEV-0): exploratory, not a hypothesis test"
    assert record["label"] == label
    system = record["systems"][SYSTEM]
    assert system["checks"]["f1_state_mse"]["within_1e-12"]
    assert system["checks"]["g_wu0039b"]["all_rows_reproduced"]
    text = (out / "contrib.md").read_text()
    blocks = text.split("\n\n")
    tables = [b for b in blocks if b.lstrip().startswith("|")]
    assert tables
    for i, block in enumerate(blocks):
        if block.lstrip().startswith("| horizon") or block.lstrip().startswith(
            "| profile"
        ):
            assert label in blocks[i - 1] or label in blocks[i - 2], block[:80]
