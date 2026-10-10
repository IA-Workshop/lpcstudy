"""Command-line seed handling of ``python -m lpcstudy`` (WU-0001.1, .3).

Everything is exact (exit codes, strings). The study is never run here: only refusals and
seed resolution are exercised, and the confirmatory seed is never used (LPC.PC.7).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lpcstudy.__main__ import build_parser, choose_seed, main
from lpcstudy.seeds import REGISTRY_PATH

PREFIX = "lpcstudy: refused (LPC.PC.7): "


@pytest.fixture(autouse=True)
def _clean_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """No test sees a confirmatory seed or salt (LPC.PC.7)."""
    monkeypatch.delenv("LPC_CONF_SEED", raising=False)
    monkeypatch.delenv("LPC_CONF_SALT", raising=False)


def resolve(argv: list[str]) -> tuple[str, int]:
    """Parse ``argv`` and resolve the seed against the real development registry."""
    args, extras = build_parser().parse_known_args(argv)
    return choose_seed(args, extras, REGISTRY_PATH)


def test_default_and_explicit_ids_resolve() -> None:
    """No flag gives DEV-0 (20261005); ``--seed-id DEV-1`` gives the registry value.

    Reference: the literal 20261005 and ``json.load`` of the registry. Exact.
    """
    with REGISTRY_PATH.open() as handle:
        expected = next(e["value"] for e in json.load(handle)["seeds"] if e["id"] == "DEV-1")
    assert resolve([]) == ("DEV-0", 20261005)
    assert resolve(["--seed-id", "DEV-0"]) == ("DEV-0", 20261005)
    assert resolve(["--seed-id=DEV-1"]) == ("DEV-1", expected)


def test_abbreviations_are_off() -> None:
    """``allow_abbrev`` is false, so ``--conf`` cannot stand for a longer flag.

    Reference: the plan (parser built with ``allow_abbrev=False``). Exact.
    """
    assert build_parser().allow_abbrev is False


@pytest.mark.parametrize("argv", [
    ["--seed", "5"],
    ["--seed", "20261005"],
    ["--seed=5"],
    ["--seed"],
    ["--seed-id", "5"],
    ["--seed-id=20261005"],
    ["--seed-id", "dev-1"],
    ["--seed-id", "DEV-99"],
    ["--seed-id", "CONF-1"],
    ["--conf"],
    ["--conf=123"],
    ["--seed-i", "DEV-0"],
    ["5"],
    ["--preset", "smoke", "--seed", "5", "--seed-id", "DEV-0"],
])
def test_refusal_is_one_line_exit_64_and_creates_nothing(
        argv: list[str], tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Each refused request returns 64 with one stderr line naming LPC.PC.7 and writes nothing.

    Reference: the refusal contract of the plan (exit 64; exactly one stderr line
    ``lpcstudy: refused (LPC.PC.7): <reason>``; nothing created before it). The seed
    values in ``argv`` (5, 20261005, 123) must not be echoed. Exact string and integer checks.
    """
    out = tmp_path / "out"
    code = main([*argv, "--out", str(out)])
    captured = capsys.readouterr()
    assert code == 64
    assert captured.out == ""
    lines = captured.err.splitlines()
    assert len(lines) == 1 and lines[0].startswith(PREFIX)
    assert not out.exists() and not list(tmp_path.rglob("results.json"))
    for value in ("20261005", "=5", " 5", "=123"):
        assert value not in lines[0]


def test_refusal_does_not_set_up_logging(tmp_path: Path) -> None:
    """A refusal adds no logging handler (refusals precede logging setup).

    Reference: the plan's order (refuse before ``out_dir.mkdir``, logging and ``Study``).
    """
    import logging
    before = list(logging.getLogger().handlers)
    assert main(["--seed", "5", "--out", str(tmp_path / "o")]) == 64
    assert list(logging.getLogger().handlers) == before


def test_registry_path_is_a_python_parameter_only() -> None:
    """No flag redirects the registry or the ledger (Q8).

    Reference: the parser's option strings. Exact.
    """
    options = {s for action in build_parser()._actions for s in action.option_strings}
    assert not {o for o in options if "ledger" in o or "registry" in o}


# ------------------------------------------------------------ WU-0001.3: the confirmatory flag
# In-process only, with a throwaway ledger in tmp_path and synthetic seeds (LPC.PC.7).

SEED = 123456789012345
SALT = "0f" * 16
FLAG = "--confirmatory"


def ledger_with(path: Path, seed: int) -> Path:
    """A one-entry hash-chained ledger holding the ``CONF-1`` commitment of ``seed``."""
    import hashlib
    digest = hashlib.sha256(f"{seed}:{SALT}".encode()).hexdigest()
    record = {"seq": 1, "prev_sha256": "0" * 64, "utc": "2026-01-01T00:00:00+00:00",
              "type": "commitment", "actor": "test", "role": "test", "authority": "",
              "summary": "synthetic", "files": {},
              "data": {"seed_id": "CONF-1", "sha256": digest}}
    path.write_text(json.dumps(record, sort_keys=True) + "\n")
    return path


def test_confirmatory_flag_returns_the_verified_seed_under_conf_1(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """With matching synthetic variables the flag resolves to ``("CONF-1", seed)``.

    Reference: the synthetic seed literal; the ledger is built in the test with hashlib.
    Exact. The study is not run.
    """
    monkeypatch.setenv("LPC_CONF_SEED", str(SEED))
    monkeypatch.setenv("LPC_CONF_SALT", SALT)
    args, extras = build_parser().parse_known_args([FLAG])
    assert choose_seed(args, extras, REGISTRY_PATH,
                       ledger_with(tmp_path / "l.jsonl", SEED)) == ("CONF-1", SEED)


@pytest.mark.parametrize("argv, set_env", [
    ([FLAG, "--seed-id", "DEV-0"], True),     # mutually exclusive, even with valid variables
    ([FLAG], False),                          # no variables
    ([FLAG, "--seed", "5"], True),            # raw integer beside the flag
])
def test_confirmatory_refusals_in_process(argv: list[str], set_env: bool, tmp_path: Path,
                                          monkeypatch: pytest.MonkeyPatch,
                                          capsys: pytest.CaptureFixture[str]) -> None:
    """The flag with ``--seed-id`` or a raw seed, or without variables, is refused (64).

    Reference: the refusal contract. One stderr line, nothing created, no seed or salt echoed.
    """
    if set_env:
        monkeypatch.setenv("LPC_CONF_SEED", str(SEED))
        monkeypatch.setenv("LPC_CONF_SALT", SALT)
    out = tmp_path / "out"
    code = main([*argv, "--out", str(out)], ledger_path=ledger_with(tmp_path / "l.jsonl", SEED))
    err = capsys.readouterr().err
    assert code == 64 and len(err.splitlines()) == 1 and err.startswith(PREFIX)
    assert not out.exists()
    assert str(SEED) not in err and SALT not in err


class _FakeStudy:
    """Stands in for ``Study``: no computation."""

    core_cells: dict = {}
    estimator_log: list = []

    def __init__(self, config: object, out_dir: Path) -> None:
        self.config = config


def run_with_fakes(argv: list[str], tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                   **kwargs: Path) -> list[dict]:
    """Run ``main`` with the study replaced by fakes; return a deep copy of every save."""
    import copy
    import lpcstudy.__main__ as cli
    saves: list[dict] = []
    monkeypatch.setattr(cli, "Study", _FakeStudy)
    monkeypatch.setattr(cli, "run_system", lambda study, system: {"seed_seen": study.config.seed})
    monkeypatch.setattr(cli, "verdicts", lambda results, config: {})
    monkeypatch.setattr(cli, "save_json", lambda obj, path: saves.append(copy.deepcopy(obj))
                        or path.write_text(json.dumps(obj)))
    monkeypatch.setattr(cli, "write_markdown", lambda *a: None)
    monkeypatch.setattr(cli, "make_figures", lambda *a: None)
    assert main([*argv, "--out", str(tmp_path / "out"), "--skip-transfer", "--skip-robustness"],
                **kwargs) == 0
    return saves


def test_provenance_is_saved_incomplete_first_and_complete_last(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The first incremental save holds the block with ``complete`` false, the last true.

    Reference: the plan (written from the first incremental ``save_json``, finished before the
    final save). The study is faked; the seed the study saw is the DEV-0 literal 20261005.
    """
    saves = run_with_fakes(["--preset", "smoke"], tmp_path, monkeypatch)
    first, last = saves[0]["provenance"], saves[-1]["provenance"]
    assert first["complete"] is False and first["end_utc"] is None
    assert last["complete"] is True and last["wall_seconds"] > 0 and last["peak_rss_bytes"] > 0
    assert last["seed_id"] == "DEV-0" and saves[-1]["config"]["seed_id"] == "DEV-0"
    assert saves[-1]["systems"]["lorenz63"]["seed_seen"] == 20261005 == saves[-1]["config"]["seed"]
    assert last["argv"][:2] == ["--preset", "smoke"]


def test_confirmatory_run_writes_no_seed_value(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A faked confirmatory run uses the synthetic seed but saves it nowhere.

    Reference: the synthetic literal; the fake study records the seed it received (so the
    run did use it), while ``results.json`` text and every save omit it. Exact.
    """
    monkeypatch.setenv("LPC_CONF_SEED", str(SEED))
    monkeypatch.setenv("LPC_CONF_SALT", SALT)
    saves = run_with_fakes(["--preset", "smoke", FLAG], tmp_path, monkeypatch,
                           ledger_path=ledger_with(tmp_path / "l.jsonl", SEED))
    assert saves[-1]["config"]["seed"] is None and saves[-1]["config"]["seed_id"] == "CONF-1"
    assert saves[-1]["provenance"]["label"] == "CONFIRMATORY: UNPROMOTED"
    assert saves[-1]["systems"]["lorenz63"]["seed_seen"] == SEED   # the fake received it
    text = (tmp_path / "out" / "smoke" / "results.json").read_text()
    assert text.count(str(SEED)) == 1       # only the fake's own 'seed_seen' echo
    del saves[-1]["systems"]
    assert str(SEED) not in json.dumps(saves[-1]) and SALT not in text


def test_mismatched_commitment_in_process(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                          capsys: pytest.CaptureFixture[str]) -> None:
    """A seed that differs from the committed one is refused (64) with one line."""
    monkeypatch.setenv("LPC_CONF_SEED", str(SEED + 1))
    monkeypatch.setenv("LPC_CONF_SALT", SALT)
    out = tmp_path / "out"
    code = main([FLAG, "--out", str(out)], ledger_path=ledger_with(tmp_path / "l.jsonl", SEED))
    err = capsys.readouterr().err
    assert code == 64 and len(err.splitlines()) == 1 and err.startswith(PREFIX)
    assert not out.exists() and str(SEED + 1) not in err and SALT not in err
