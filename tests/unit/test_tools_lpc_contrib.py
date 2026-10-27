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

import hashlib
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


# ------------------------------------------------- WU-0054: --sealed mode
# Reference: the plan (WU-0054 (b)) and the pre-registration's pinned cache
# (docs/study/preregistration_phase_j/lyapunov.json, sha256 written below by
# hand). Synthetic seed and salt with a throwaway ledger only (the pattern of
# tests/unit/test___main__.py); no sealed seed is read. The end-to-end sealed
# run on a relabelled smoke copy is in
# tests/integration/test_contribution_dump.py. Tolerance: none (exact).
PINNED = REPO / "docs" / "study" / "preregistration_phase_j" / "lyapunov.json"
PINNED_SHA = "852ce1f67cdcc55275f388c72817348b1b83e2146b4751c8c8aedc7a85453417"
FAKE_SEED = 123456789012345
FAKE_SALT = "0f" * 16


def sealed_run(
    path: Path, seed_id: str = "CONF-5", cache: bytes | None = None
) -> Path:
    """A sealed run folder: no seed value, the pinned cache (or ``cache``)."""
    run = fake_run(path, seed_id, "confirmatory")
    results = json.loads((run / "results.json").read_text())
    results["config"]["seed"] = None
    (run / "results.json").write_text(json.dumps(results))
    (run / "cache").mkdir()
    (run / "cache" / "lyapunov.json").write_bytes(
        PINNED.read_bytes() if cache is None else cache
    )
    return run


def ledger_with(path: Path, seed: int, seed_id: str) -> Path:
    """A one-entry ledger holding the commitment of ``seed`` for
    ``seed_id``."""
    digest = hashlib.sha256(f"{seed}:{FAKE_SALT}".encode()).hexdigest()
    record = {
        "seq": 1,
        "prev_sha256": "0" * 64,
        "utc": "2026-01-01T00:00:00+00:00",
        "type": "commitment",
        "actor": "test",
        "role": "test",
        "authority": "",
        "summary": "synthetic",
        "files": {},
        "data": {"seed_id": seed_id, "sha256": digest},
    }
    path.write_text(json.dumps(record, sort_keys=True) + "\n")
    return path


def test_pinned_hash_is_the_pre_registered_file() -> None:
    """The constant is the hash of the pinned file (hand-copied above)."""
    assert lpc_contrib.PINNED_LYAPUNOV_SHA256 == PINNED_SHA
    assert hashlib.sha256(PINNED.read_bytes()).hexdigest() == PINNED_SHA


def test_sealed_mode_accepts_a_sealed_run_and_refuses_the_rest(
    tmp_path: Path,
) -> None:
    """``check_run(sealed=True)``: a sealed run with the pinned cache passes;
    a development run, a sealed run with another cache or none, and a
    sealed id of the wrong form are refused. Without ``sealed`` a sealed run
    is still refused (development behavior unchanged)."""
    run = sealed_run(tmp_path / "ok")
    checked = lpc_contrib.check_run(run, False, sealed=True)
    assert checked["provenance"]["seed_id"] == "CONF-5"
    with pytest.raises(lpc_contrib.Refusal):
        lpc_contrib.check_run(run, False)
    dev = fake_run(tmp_path / "dev", "DEV-1")
    (dev / "cache").mkdir()
    (dev / "cache" / "lyapunov.json").write_bytes(PINNED.read_bytes())
    with pytest.raises(lpc_contrib.Refusal, match="not a sealed run"):
        lpc_contrib.check_run(dev, False, sealed=True)
    other = sealed_run(tmp_path / "other", cache=PINNED.read_bytes() + b"\n")
    with pytest.raises(lpc_contrib.Refusal, match="pinned"):
        lpc_contrib.check_run(other, False, sealed=True)
    none = sealed_run(tmp_path / "none")
    (none / "cache" / "lyapunov.json").unlink()
    with pytest.raises(lpc_contrib.Refusal, match="lyapunov.json"):
        lpc_contrib.check_run(none, False, sealed=True)
    bad_id = sealed_run(tmp_path / "bad", seed_id="CONF-x")
    with pytest.raises(lpc_contrib.Refusal, match="not a sealed run"):
        lpc_contrib.check_run(bad_id, False, sealed=True)


def test_master_seed_of_a_sealed_run_comes_from_the_verified_variables(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Development: ``config.seed``. Sealed: the synthetic seed, verified
    against the throwaway ledger's commitment for the run's id; refused
    without the variables, with a commitment for another id only, or when
    the sealed ``results.json`` holds a seed value."""
    monkeypatch.delenv("LPC_CONF_SEED", raising=False)
    monkeypatch.delenv("LPC_CONF_SALT", raising=False)
    dev_run = fake_run(tmp_path / "dev", "DEV-1")
    dev = json.loads((dev_run / "results.json").read_text())
    assert lpc_contrib.master_seed(dev, sealed=False) == 1
    sealed = json.loads(
        (sealed_run(tmp_path / "s") / "results.json").read_text()
    )
    monkeypatch.setattr(
        lpc_contrib,
        "LEDGER_PATH",
        ledger_with(tmp_path / "l.jsonl", FAKE_SEED, "CONF-5"),
    )
    with pytest.raises(lpc_contrib.Refusal, match="LPC_CONF_SEED"):
        lpc_contrib.master_seed(sealed, sealed=True)
    monkeypatch.setenv("LPC_CONF_SEED", str(FAKE_SEED))
    monkeypatch.setenv("LPC_CONF_SALT", FAKE_SALT)
    assert lpc_contrib.master_seed(sealed, sealed=True) == FAKE_SEED
    monkeypatch.setattr(
        lpc_contrib,
        "LEDGER_PATH",
        ledger_with(tmp_path / "m.jsonl", FAKE_SEED, "CONF-6"),
    )
    with pytest.raises(lpc_contrib.Refusal) as err:
        lpc_contrib.master_seed(sealed, sealed=True)
    assert str(FAKE_SEED) not in str(err.value)
    leaked = {**sealed, "config": {**sealed["config"], "seed": 7}}
    with pytest.raises(lpc_contrib.Refusal, match="seed value"):
        lpc_contrib.master_seed(leaked, sealed=True)


def test_relabel_replaces_every_development_label() -> None:
    """Every string equal to the old label, at any depth, becomes the new
    one; other strings are kept; the input is not modified."""
    old = "DEVELOPMENT (CONF-5): exploratory, not a hypothesis test"
    new = lpc_contrib.SEALED_LABEL.format(seed_id="CONF-5")
    record = {
        "label": old,
        "systems": {"a": {"label": old, "x": [old, "y"]}},
        "n": 1,
    }
    out = lpc_contrib.relabel(record, old, new)
    assert out == {
        "label": new,
        "systems": {"a": {"label": new, "x": [new, "y"]}},
        "n": 1,
    }
    assert record["label"] == old
    assert new == (
        "PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED"
    )


def test_sealed_flag_refusals_write_nothing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """``--sealed`` on a development run, with ``--replication``, or without
    the seed variables: 64, nothing written. With the synthetic seed and
    ledger the seed check passes and the run stops at its missing dump
    (still 64, nothing written)."""
    monkeypatch.delenv("LPC_CONF_SEED", raising=False)
    monkeypatch.delenv("LPC_CONF_SALT", raising=False)
    out = tmp_path / "out"
    dev = fake_run(tmp_path / "dev", "DEV-1")
    run = sealed_run(tmp_path / "run")
    for argv in (
        [str(dev), "--sealed"],
        [str(run), "--sealed", "--replication"],
        [str(run), "--sealed"],
    ):
        assert lpc_contrib.main([*argv, "--out", str(out)]) == 64
        assert not out.exists()
    err = capsys.readouterr().err
    assert "LPC_CONF_SEED" in err and str(FAKE_SEED) not in err
    monkeypatch.setattr(
        lpc_contrib,
        "LEDGER_PATH",
        ledger_with(tmp_path / "l.jsonl", FAKE_SEED, "CONF-5"),
    )
    monkeypatch.setenv("LPC_CONF_SEED", str(FAKE_SEED))
    monkeypatch.setenv("LPC_CONF_SALT", FAKE_SALT)
    assert lpc_contrib.main([str(run), "--sealed", "--out", str(out)]) == 64
    err = capsys.readouterr().err
    assert "lorenz63.npz" in err and str(FAKE_SEED) not in err
    assert not out.exists()
