"""Tests of ``tools/lpc_contrib.py``, the phase J A/B/D tool (WU-0048).

The tool must refuse, before writing anything, a confirmatory request, a
non-development run, a held-out replication seed (DEV-5 to DEV-9) without
``--replication`` and a run whose ``run.meta.json`` has a non-zero exit code
(exit 64). Its helpers: the leaf comparison of test (g) and the JSON-safe copy
(no NaN or infinity in ``contrib.json``). References: hand-written fixtures.
Tolerance: none (exit codes, counts and exact values). The end-to-end run on a
smoke dump is in ``tests/integration/test_contribution_dump.py``.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "tools" / "lpc_contrib.py"
_SPEC = importlib.util.spec_from_file_location("lpc_contrib", TOOL)
assert _SPEC is not None and _SPEC.loader is not None
lpc_contrib = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(lpc_contrib)


def fake_run(
    path: Path,
    seed_id: str,
    kind: str = "development",
    exit_code: int | None = 0,
) -> Path:
    """A run folder with a minimal ``results.json`` (and ``run.meta.json``)."""
    path.mkdir(parents=True)
    (path / "results.json").write_text(
        json.dumps(
            {
                "provenance": {
                    "seed_id": seed_id,
                    "seed_kind": kind,
                    "complete": True,
                },
                "config": {
                    "seed": 1,
                    "bootstrap_resamples": 10,
                    "bootstrap_block": 5,
                },
                "systems": {"lorenz63": {}},
            }
        )
    )
    if exit_code is not None:
        (path / "run.meta.json").write_text(
            json.dumps({"exit_code": exit_code})
        )
    return path


def call(*argv: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-I", str(TOOL), *argv],
        capture_output=True,
        timeout=60,
    )


@pytest.mark.parametrize(
    ("seed_id", "kind", "exit_code"),
    [
        ("DEV-6", "development", 0),  # held out
        ("DEV-9", "development", 0),
        ("CONF-1", "confirmatory", 0),
        ("DEV-1", "confirmatory", 0),
        ("DEV-1", "development", 1),  # failed run
        ("DEV-1", "development", None),
    ],
)
def test_refusals_exit_64_and_write_nothing(
    tmp_path: Path, seed_id: str, kind: str, exit_code: int | None
) -> None:
    """Exit 64 and no output folder for every refused run."""
    # Without a meta file the run passes the checks and is refused for its
    # missing dump: still 64 and nothing written.
    run = fake_run(tmp_path / "run", seed_id, kind, exit_code)
    done = call(str(run), "--out", str(tmp_path / "out"))
    assert done.returncode == 64, done.stderr
    assert not (tmp_path / "out").exists()


def test_confirmatory_word_is_refused_anywhere_in_the_arguments(
    tmp_path: Path,
) -> None:
    """Any argument containing "confirmatory" (any case) is refused first."""
    run = fake_run(tmp_path / "run", "DEV-1")
    done = call(str(run), "--out", str(tmp_path / "Confirmatory-out"))
    assert done.returncode == 64
    assert b"confirmatory" in done.stderr
    assert not (tmp_path / "Confirmatory-out").exists()


def test_replication_flag_admits_a_held_out_seed_past_the_seed_check(
    tmp_path: Path,
) -> None:
    """With ``--replication`` the seed check passes (the run then fails on
    its missing dump, still with 64 and nothing written)."""
    run = fake_run(tmp_path / "run", "DEV-7")
    assert (
        lpc_contrib.check_run(run, replication=True)["provenance"]["seed_id"]
        == "DEV-7"
    )
    with pytest.raises(lpc_contrib.Refusal):
        lpc_contrib.check_run(run, replication=False)
    done = call(str(run), "--out", str(tmp_path / "out"), "--replication")
    assert done.returncode == 64 and b"lorenz63.npz" in done.stderr


def test_compare_leaves_counts_equal_and_different_numbers() -> None:
    """Shared keys only; numbers equal bitwise or NaN-NaN; strings equal."""
    mine = {
        "a": 1.0,
        "b": [1.0, 2.0],
        "c": {"d": "x", "e": float("nan")},
        "only": 3.0,
    }
    theirs = {"a": 1.0, "b": [1.0, 2.5], "c": {"d": "x", "e": float("nan")}}
    same, diff, worst = lpc_contrib.compare_leaves(mine, theirs)
    assert (same, diff, worst) == (4, 1, 0.5)


def test_json_copy_has_no_non_finite_numbers() -> None:
    """``inf`` and NaN become ``null``; NumPy scalars become Python ones."""
    value = {
        "a": np.float64(np.inf),
        "b": [np.nan, 1.5],
        "c": np.int64(3),
        "d": np.bool_(True),
        "e": (1, 2),
        "f": np.array([0.5, np.inf]),
    }
    text = json.dumps(lpc_contrib.to_json(value), allow_nan=False)
    assert json.loads(text) == {
        "a": None,
        "b": [None, 1.5],
        "c": 3,
        "d": True,
        "e": [1, 2],
        "f": [0.5, None],
    }
