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
