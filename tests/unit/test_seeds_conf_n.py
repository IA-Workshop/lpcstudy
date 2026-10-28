"""Tests for the sealed ids ``CONF-n`` of the confirmatory path (WU-0038).

The follow-on study seals CONF-2, CONF-3 and CONF-4 beside CONF-1. The
confirmatory flag takes the id from ``--seed-id`` (default ``CONF-1``) and
checks the seed and salt of ``LPC_CONF_SEED`` and ``LPC_CONF_SALT`` against the
latest ledger ``commitment`` entry whose ``data.seed_id`` equals that id.

Reference: the commitment is computed here with
``hashlib.sha256(f"{seed}:{salt}".encode())`` and the ledger chain is built here
with ``hashlib``, both independent of ``tools.seal_confirmatory_seed`` and
``tools.ledger``. Every check is exact (strings, integers, exit codes), so no
numerical tolerance applies. The seeds and salts are synthetic, every ledger is
built under ``tmp_path``, and the real ledger is never read (LPC.PC.7).
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections.abc import Iterator, Mapping
from pathlib import Path

import pytest

import tools.ledger
from lpcstudy import __main__ as cli
from lpcstudy import provenance
from lpcstudy.__main__ import build_parser, choose_seed, main
from lpcstudy.seeds import REGISTRY_PATH, SeedRefusal, confirmatory_seed

PREFIX = "lpcstudy: refused (LPC.PC.7): "
FLAG = "--confirmatory"
GENESIS = "0" * 64
ROOT = Path(__file__).resolve().parents[2]

# Synthetic pairs: never a real confirmatory seed or salt.
SEED_1, SALT_1 = 123456789012345, "0f" * 16
SEED_2, SALT_2 = 314159265358979, "a5" * 16
SEED_3, SALT_3 = 271828182845904, "3c" * 16
SECRETS = tuple(
    str(v) for v in (SEED_1, SALT_1, SEED_2, SALT_2, SEED_3, SALT_3)
)


@pytest.fixture(autouse=True)
def _isolated(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Remove the seed variables, hide the real ledger, fake a clean tree.

    ``tools.ledger.LEDGER`` points at a missing file under ``tmp_path``, so a
    stray read of the default ledger fails. The clean-tree guard sees a clean
    tree at a known commit, as in ``test___main__.py``.
    """
    monkeypatch.delenv("LPC_CONF_SEED", raising=False)
    monkeypatch.delenv("LPC_CONF_SALT", raising=False)
    monkeypatch.setattr(tools.ledger, "LEDGER", tmp_path / "absent.jsonl")
    monkeypatch.setattr(
        provenance, "git_state", lambda root: ("a" * 40, False, None)
    )


def digest(seed: int, salt: str) -> str:
    """Compute the commitment with ``hashlib`` (independent of the tools)."""
    return hashlib.sha256(f"{seed}:{salt}".encode()).hexdigest()


def commitment(seed_id: str, seed: int, salt: str) -> dict:
    """Make a ledger ``commitment`` entry for ``seed_id``."""
    return {
        "type": "commitment",
        "data": {"seed_id": seed_id, "sha256": digest(seed, salt)},
    }


def build_ledger(path: Path, entries: list[dict]) -> Path:
    """Write a hash-chained ledger under ``tmp_path``, chained with
    ``hashlib``.
    """
    assert ROOT not in path.resolve().parents, "fixtures live under tmp_path"
    lines, previous = [], GENESIS
    for number, entry in enumerate(entries, start=1):
        record = {
            "seq": number,
            "prev_sha256": previous,
            "utc": "2026-01-01T00:00:00+00:00",
            "actor": "test",
            "role": "test",
            "authority": "",
            "summary": "synthetic",
            "files": {},
            **entry,
        }
        line = json.dumps(record, sort_keys=True)
        previous = hashlib.sha256(line.encode()).hexdigest()
        lines.append(line)
    path.write_text("\n".join(lines) + "\n")
    return path


def environment(seed: int, salt: str) -> dict[str, str]:
    """Make the two confirmatory variables."""
    return {"LPC_CONF_SEED": str(seed), "LPC_CONF_SALT": salt}


# Ledger with CONF-1, CONF-2 (superseded once) and CONF-3 entries; the CONF-2
# entry that counts is the latest one, for (SEED_2, SALT_2).
def three_ids(tmp_path: Path) -> Path:
    """Write the ledger of the comment above."""
    return build_ledger(
        tmp_path / "l.jsonl",
        [
            commitment("CONF-1", SEED_1, SALT_1),
            commitment("CONF-2", SEED_3, SALT_3),
            {"type": "note", "data": {}},
            commitment("CONF-2", SEED_2, SALT_2),
            commitment("CONF-3", SEED_3, SALT_3),
        ],
    )


def assert_safe_reason(reason: str) -> None:
    """A refusal is one line and holds no seed or salt."""
    assert "\n" not in reason
    for secret in SECRETS:
        assert secret not in reason


# seeds.confirmatory_seed


def test_conf_2_matching_pair_is_accepted(tmp_path: Path) -> None:
    """The CONF-2 pair is accepted against the latest CONF-2 entry.

    Reference: the digests are computed in the test. The earlier CONF-2 entry
    (for the CONF-3 pair) is superseded, so that pair is refused for CONF-2.
    """
    ledger = three_ids(tmp_path)
    assert (
        confirmatory_seed(environment(SEED_2, SALT_2), ledger, "CONF-2")
        == SEED_2
    )
    assert (
        confirmatory_seed(environment(SEED_3, SALT_3), ledger, "CONF-3")
        == SEED_3
    )
    with pytest.raises(SeedRefusal):
        confirmatory_seed(environment(SEED_3, SALT_3), ledger, "CONF-2")


@pytest.mark.parametrize(
    "env, entries, seed_id, words",
    [
        (
            environment(SEED_2 + 1, SALT_2),
            None,
            "CONF-2",
            "do not match the ledger commitment for CONF-2",
        ),  # wrong seed
        (
            environment(SEED_2, "a4" * 16),
            None,
            "CONF-2",
            "do not match the ledger commitment for CONF-2",
        ),  # wrong salt
        (
            environment(SEED_2, SALT_2),
            [commitment("CONF-1", SEED_2, SALT_2)],
            "CONF-2",
            "no commitment entry for CONF-2",
        ),  # the pair is committed, but only under CONF-1
        (
            environment(SEED_2, SALT_2),
            None,
            "CONF-9",
            "no commitment entry for CONF-9",
        ),  # unknown id
    ],
    ids=["wrong-seed", "wrong-salt", "conf-1-entry-only", "unknown-id"],
)
def test_conf_n_refusals(
    tmp_path: Path,
    env: dict[str, str],
    entries: list[dict] | None,
    seed_id: str,
    words: str,
) -> None:
    """Wrong seed, wrong salt, a CONF-1-only ledger and an unknown id refuse.

    Reference: the digests of the committed pairs, from ``hashlib``; any other
    pair differs. The reason is one line naming the id, without secrets.
    """
    ledger = (
        three_ids(tmp_path)
        if entries is None
        else build_ledger(tmp_path / "l.jsonl", entries)
    )
    with pytest.raises(SeedRefusal, match=r"LPC\.PC\.7") as caught:
        confirmatory_seed(env, ledger, seed_id)
    assert words in caught.value.reason
    assert_safe_reason(str(caught.value))
    for value in env.values():
        assert value not in str(caught.value)


class _Untouchable(Mapping[str, str]):
    """An environment that fails the test if it is read at all."""

    def __getitem__(self, key: str) -> str:
        raise AssertionError("the environment was read")

    def __iter__(self) -> Iterator[str]:
        raise AssertionError("the environment was read")

    def __len__(self) -> int:
        raise AssertionError("the environment was read")


@pytest.mark.parametrize(
    "seed_id",
    [
        "DEV-0",
        "DEV-1",
        "CONF-0",
        "CONF-01",
        "conf-2",
        "CONF-2 ",
        "CONF-",
        "CONF-2\n",
        "",
        str(SEED_2),
    ],
)
def test_malformed_id_is_refused_before_the_environment_is_read(
    tmp_path: Path,
    seed_id: str,
) -> None:
    """An id that is not ``CONF-n`` (n >= 1, no leading zero) is refused first.

    Reference: the id form ``CONF-[1-9][0-9]*``. The environment is a mapping
    that fails on any read, so the refusal comes before the secrets are read.
    A raw integer is not echoed.
    """
    ledger = three_ids(tmp_path)
    with pytest.raises(SeedRefusal, match="CONF-n") as caught:
        confirmatory_seed(_Untouchable(), ledger, seed_id)
    assert_safe_reason(str(caught.value))


def test_default_id_is_conf_1(tmp_path: Path) -> None:
    """Without an id the pair is checked against CONF-1, never another id.

    Reference: the ledger of ``three_ids``. The CONF-1 pair is accepted; the
    CONF-2 pair, valid for CONF-2, is refused with a reason naming CONF-1, so
    an omitted id cannot select another sealed seed silently.
    """
    ledger = three_ids(tmp_path)
    assert confirmatory_seed(environment(SEED_1, SALT_1), ledger) == SEED_1
    with pytest.raises(SeedRefusal, match="commitment for CONF-1"):
        confirmatory_seed(environment(SEED_2, SALT_2), ledger)


# The command line (in process)


def parse_and_choose(argv: list[str], ledger: Path) -> tuple[str, int]:
    """Parse ``argv`` and choose the seed against ``ledger``."""
    args, extras = build_parser().parse_known_args(argv)
    return choose_seed(args, extras, REGISTRY_PATH, ledger)


def test_flag_with_conf_2_resolves_to_conf_2(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``--seed-id CONF-2`` with the flag gives ``("CONF-2", seed)``; no id
    still gives CONF-1 for the CONF-1 pair.
    """
    ledger = three_ids(tmp_path)
    monkeypatch.setenv("LPC_CONF_SEED", str(SEED_2))
    monkeypatch.setenv("LPC_CONF_SALT", SALT_2)
    assert parse_and_choose([FLAG, "--seed-id", "CONF-2"], ledger) == (
        "CONF-2",
        SEED_2,
    )
    assert parse_and_choose([FLAG, "--seed-id=CONF-2"], ledger) == (
        "CONF-2",
        SEED_2,
    )
    monkeypatch.setenv("LPC_CONF_SEED", str(SEED_1))
    monkeypatch.setenv("LPC_CONF_SALT", SALT_1)
    assert parse_and_choose([FLAG], ledger) == ("CONF-1", SEED_1)


def test_conf_id_without_the_flag_is_refused(tmp_path: Path) -> None:
    """``--seed-id CONF-2`` without the flag is refused (a development id is
    ``DEV-n``), even with a matching pair in a matching ledger.
    """
    with pytest.raises(SeedRefusal, match="DEV-n"):
        parse_and_choose(["--seed-id", "CONF-2"], three_ids(tmp_path))


def fake_study(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    """Replace the study by fakes; return the list of seeds the study saw."""
    seen: list[int] = []

    class FakeStudy:
        core_cells: dict = {}
        estimator_log: list = []

        def __init__(self, config: object, out_dir: Path) -> None:
            seen.append(config.seed)
            self.config = config

    monkeypatch.setattr(cli, "Study", FakeStudy)
    monkeypatch.setattr(cli, "run_system", lambda study, system: {})
    monkeypatch.setattr(cli, "run_handling", lambda study, results: {})
    monkeypatch.setattr(cli, "verdicts", lambda results, config: {})
    monkeypatch.setattr(cli, "write_markdown", lambda *a: None)
    monkeypatch.setattr(cli, "make_figures", lambda *a: None)
    return seen


def test_faked_conf_2_run_records_only_the_id(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A faked CONF-2 run uses the CONF-2 seed and records only the id.

    Reference: the synthetic literals. The study saw ``SEED_2``; the saved
    ``results.json`` holds ``seed_id`` CONF-2, a null seed, the confirmatory
    label, and neither the seed nor the salt; nor do the log and the console.
    """
    seen = fake_study(monkeypatch)
    monkeypatch.setenv("LPC_CONF_SEED", str(SEED_2))
    monkeypatch.setenv("LPC_CONF_SALT", SALT_2)
    out = tmp_path / "out"
    caplog.set_level(logging.INFO, logger="lpcstudy")
    code = main(
        [
            "--preset",
            "smoke",
            FLAG,
            "--seed-id",
            "CONF-2",
            "--out",
            str(out),
            "--skip-robustness",
        ],
        ledger_path=three_ids(tmp_path),
    )
    assert code == 0 and seen == [SEED_2]
    text = (out / "smoke" / "results.json").read_text()
    saved = json.loads(text)
    assert saved["config"]["seed_id"] == "CONF-2"
    assert saved["config"]["seed"] is None
    assert saved["provenance"]["seed_id"] == "CONF-2"
    assert saved["provenance"]["label"] == "CONFIRMATORY: UNPROMOTED"
    captured = capsys.readouterr()
    logged = "\n".join(r.getMessage() for r in caplog.records)
    for secret in SECRETS:
        assert secret not in text and secret not in logged
        assert secret not in captured.out and secret not in captured.err


@pytest.mark.parametrize(
    "seed_id, env, entries",
    [
        ("CONF-2", environment(SEED_2 + 1, SALT_2), None),
        ("CONF-2", environment(SEED_2, "a4" * 16), None),
        (
            "CONF-2",
            environment(SEED_2, SALT_2),
            [commitment("CONF-1", SEED_2, SALT_2)],
        ),
        ("CONF-9", environment(SEED_2, SALT_2), None),
        ("DEV-1", environment(SEED_2, SALT_2), None),
    ],
    ids=[
        "wrong-seed",
        "wrong-salt",
        "conf-1-entry-only",
        "unknown-id",
        "dev-id-with-flag",
    ],
)
def test_cli_refusals_compute_and_write_nothing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    seed_id: str,
    env: dict[str, str],
    entries: list[dict] | None,
) -> None:
    """Each refusal exits 64 with one stderr line, before any computation.

    Reference: the refusal contract of ``main``. The study and the provenance
    collection are replaced by functions that fail the test if called; the
    output directory (so ``results.json``) never exists; no secret is echoed.
    """

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("computation or provenance began")

    monkeypatch.setattr(cli, "Study", forbidden)
    monkeypatch.setattr(provenance, "collect", forbidden)
    for name, value in env.items():
        monkeypatch.setenv(name, value)
    ledger = (
        three_ids(tmp_path)
        if entries is None
        else build_ledger(tmp_path / "l.jsonl", entries)
    )
    out = tmp_path / "out"
    code = main(
        ["--preset", "smoke", FLAG, "--seed-id", seed_id, "--out", str(out)],
        ledger_path=ledger,
    )
    captured = capsys.readouterr()
    assert code == 64
    assert len(captured.err.splitlines()) == 1
    assert captured.err.startswith(PREFIX)
    assert not out.exists()
    for secret in (*SECRETS, *env.values()):
        assert secret not in captured.err and secret not in captured.out
