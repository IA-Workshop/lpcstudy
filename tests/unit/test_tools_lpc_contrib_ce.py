"""Tests of ``tools/lpc_contrib_ce.py``, the phase J C/E tool (WU-0049).

* Refusals before anything is written (exit 64): a confirmatory request, a
  held-out seed without ``--replication``, an A/D record of another seed or
  run.
* Figures regenerate byte for byte: the same record drawn twice gives
  identical PNG files (Agg, no metadata), and ``--figures-from`` on a written
  record reproduces them.
* Every table of the cross-seed view has the DEVELOPMENT label before it.

References: hand-written fixtures. Tolerance: none (bytes, exit codes).
The end-to-end run on a smoke dump is in
``tests/integration/test_contribution_dump.py``.
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
TOOL = REPO / "tools" / "lpc_contrib_ce.py"
_SPEC = importlib.util.spec_from_file_location("lpc_contrib_ce", TOOL)
assert _SPEC is not None and _SPEC.loader is not None
tool = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(tool)

LABEL = "DEVELOPMENT (DEV-0): exploratory, not a hypothesis test"


def call(*argv: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-I", str(TOOL), *argv],
        capture_output=True,
        timeout=60,
    )


def fake_run(path: Path, seed_id: str) -> Path:
    path.mkdir(parents=True)
    (path / "results.json").write_text(
        json.dumps(
            {
                "provenance": {
                    "seed_id": seed_id,
                    "seed_kind": "development",
                    "complete": True,
                },
                "config": {"seed": 1},
                "systems": {"lorenz63": {}},
            }
        )
    )
    return path


def test_refusals_exit_64_and_write_nothing(tmp_path: Path) -> None:
    """Confirmatory word, held-out seed: exit 64, no output folder."""
    run = fake_run(tmp_path / "run", "DEV-1")
    done = call(str(run), "--out", str(tmp_path / "confirmatory"))
    assert done.returncode == 64 and not (tmp_path / "confirmatory").exists()
    held = fake_run(tmp_path / "held", "DEV-8")
    done = call(str(held), "--out", str(tmp_path / "out"))
    assert done.returncode == 64 and b"held-out" in done.stderr
    assert not (tmp_path / "out").exists()


def test_sealed_flag_refusals_write_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """WU-0054: ``--sealed`` with ``--replication``, without ``--abd``, or
    with an A/D record not written with ``--sealed``: exit 64, nothing
    written. The last case passes the seed check with a synthetic seed and
    a throwaway ledger (in-process; no sealed seed is read).

    Reference: the plan (WU-0054 (b)) and the hand-written label.
    Tolerance: none (exit codes).
    """
    monkeypatch.delenv("LPC_CONF_SEED", raising=False)
    monkeypatch.delenv("LPC_CONF_SALT", raising=False)
    run = tmp_path / "run"
    run.mkdir()
    (run / "results.json").write_text(
        json.dumps(
            {
                "provenance": {
                    "seed_id": "CONF-5",
                    "seed_kind": "confirmatory",
                    "complete": True,
                },
                "config": {"seed": None},
                "systems": {"lorenz63": {}},
            }
        )
    )
    (run / "cache").mkdir()
    pinned = REPO / "docs" / "study" / "preregistration_phase_j"
    (run / "cache" / "lyapunov.json").write_bytes(
        (pinned / "lyapunov.json").read_bytes()
    )
    abd = tmp_path / "contrib.json"
    abd.write_text(
        json.dumps(
            {
                "label": "DEVELOPMENT (CONF-5): exploratory, not a "
                "hypothesis test",
                "run": {"seed_id": "CONF-5", "dir": str(run)},
            }
        )
    )
    out = tmp_path / "out"
    for argv in (
        ["--sealed", "--replication", "--abd", str(abd)],
        ["--sealed"],
    ):
        assert tool.main([str(run), "--out", str(out), *argv]) == 64
        assert not out.exists()
    seed, salt = 123456789012345, "0f" * 16
    digest = hashlib.sha256(f"{seed}:{salt}".encode()).hexdigest()
    ledger = tmp_path / "l.jsonl"
    ledger.write_text(
        json.dumps(
            {
                "seq": 1,
                "prev_sha256": "0" * 64,
                "utc": "2026-01-01T00:00:00+00:00",
                "type": "commitment",
                "actor": "test",
                "role": "test",
                "authority": "",
                "summary": "synthetic",
                "files": {},
                "data": {"seed_id": "CONF-5", "sha256": digest},
            },
            sort_keys=True,
        )
        + "\n"
    )
    monkeypatch.setattr(tool.base, "LEDGER_PATH", ledger)
    monkeypatch.setenv("LPC_CONF_SEED", str(seed))
    monkeypatch.setenv("LPC_CONF_SALT", salt)
    assert tool.main([str(run), "--out", str(out), "--sealed", "--abd",
                      str(abd)]) == 64
    assert not out.exists()


def test_abd_record_of_another_seed_or_run_is_refused(tmp_path: Path) -> None:
    """``check_abd`` refuses a foreign A/D record."""
    run = tmp_path / "run"
    record = {"run": {"seed_id": "DEV-1", "dir": str(run)}}
    tool.check_abd(record, run, "DEV-1")
    with pytest.raises(tool.Refusal):
        tool.check_abd(record, run, "DEV-3")
    with pytest.raises(tool.Refusal):
        tool.check_abd(record, tmp_path / "other", "DEV-1")


def synthetic_record() -> dict:
    """A record with the fields the figures read (``None`` gaps included)."""
    rng = np.random.default_rng(4921)
    h = list(range(1, 241))
    curve = [[float(v) for v in rng.standard_normal(240)] for _ in range(3)]
    curve[2][100:110] = [None] * 10
    edges = np.linspace(-1, 1, 41).tolist()
    hist = {
        x: {
            "edges": edges,
            "counts": rng.integers(0, 50, 40).tolist(),
            "top_states": rng.uniform(-1, 1, 10).tolist(),
        }
        for x in "ROIN"
    }
    point = {"estimate": 0.1, "ci": [0.08, 0.12]}
    return {
        "label": LABEL,
        "systems": {
            "lorenz63": {
                "E_H2a": {
                    "steps_per_lt": 30,
                    "figure": {
                        "H": h,
                        "median_m": curve,
                        "median_drift": curve,
                        "median_corr": curve,
                    },
                },
                "E_H2e": {
                    "library_ends": [1000, 100000],
                    "levels": {
                        "0.01": {
                            "reading": "not determined",
                            "figure": {
                                "delta_R": rng.standard_normal(50).tolist(),
                                "delta_corr": rng.standard_normal(50).tolist(),
                                "zero_at_smallest": (
                                    rng.uniform(size=50) < 0.3
                                ).tolist(),
                            },
                        }
                    },
                },
                "E_H3c": {
                    "figure": {
                        "cumulative_share": np.linspace(
                            0.05, 0.6, 100
                        ).tolist(),
                        "n_states": 1000,
                        "histograms": hist,
                    }
                },
                "C3": {
                    "policies": {
                        "A2 + constant": {
                            "false_trust_realized": point,
                            "mean_trusted_lt": {
                                "estimate": 2.0,
                                "ci": [1.9, 2.1],
                            },
                        },
                        "g(F-hat) + h(F-hat)": {
                            "false_trust_realized": point,
                            "mean_trusted_lt": {
                                "estimate": 2.2,
                                "ci": [None, 2.3],
                            },
                        },
                    }
                },
            }
        },
    }


def test_figures_regenerate_byte_for_byte(tmp_path: Path) -> None:
    """The same record drawn twice, and via ``--figures-from``: equal bytes."""
    record = synthetic_record()
    first = tool.write_figures(record, tmp_path / "a")
    second = tool.write_figures(json.loads(json.dumps(record)), tmp_path / "b")
    assert first == second and len(first) == 4
    for name in first:
        a = (tmp_path / "a" / "figures" / name).read_bytes()
        assert a == (tmp_path / "b" / "figures" / name).read_bytes()
        assert b"Software" not in a  # no software tag in the PNG
    path = tmp_path / "ce.json"
    path.write_text(json.dumps(record))
    done = call("--figures-from", str(path), "--out", str(tmp_path / "c"))
    assert done.returncode == 0, done.stderr.decode()[-1000:]
    assert json.loads(done.stdout) == first


def test_crossseed_tables_carry_the_label() -> None:
    """Every table block of the cross-seed view follows a label paragraph."""
    records = [
        {
            "run": {"seed_id": s},
            "systems": {},
            "E_H3c_reading": {"reading": "x"},
        }
        for s in ("DEV-1", "DEV-3")
    ]
    text = tool.crossseed(records)
    label = "DEVELOPMENT (DEV-1, DEV-3): exploratory, not a hypothesis test"
    blocks = text.split("\n\n")
    tables = [i for i, b in enumerate(blocks) if b.lstrip().startswith("|")]
    assert tables
    for i in tables:
        assert label in blocks[i - 1]
