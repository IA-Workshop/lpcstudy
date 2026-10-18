"""Tests for ``lpcstudy.seeds``: the seed registry and the guard (WU-0001.1,
.2).

The references are LPC.PC.7 and NVVUQ.18. ``seeds`` decides which master seed a
run may use. A development run names a registered id (``DEV-n``); a confirmatory
run must present a seed and salt whose SHA-256 hash matches the commitment in
the ledger. Every check here is exact (integers, strings, identical decisions),
so no numerical tolerance applies. The real confirmatory seed is never used: the
seeds below are synthetic, and every ledger is built in ``tmp_path`` (LPC.PC.7).
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

import tools.ledger
from lpcstudy.config import SMOKE
from lpcstudy.seeds import (
    LEDGER_PATH,
    REGISTRY_PATH,
    REGISTRY_SCHEMA,
    SeedRefusal,
    check_commitment,
    confirmatory_seed,
    load_registry,
    resolve_dev_seed,
    with_seed,
)

# The v1 config.py default and the pilot record (docs/study).
DEV_0_LITERAL = 20261005

# A synthetic seed: never a real confirmatory seed.
SYNTHETIC_SEED = 123456789012345
SYNTHETIC_SALT = "0f" * 16
OTHER_SEED = 222222222222222
GENESIS = "0" * 64
ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _clean_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Keep each test away from a confirmatory seed, salt or the real ledger
    (LPC.PC.7).

    The two environment variables are removed. ``tools.ledger.LEDGER`` points at
    a nonexistent file under ``tmp_path``, so a stray read of the default ledger
    fails loudly instead of reading the real one.
    """
    monkeypatch.delenv("LPC_CONF_SEED", raising=False)
    monkeypatch.delenv("LPC_CONF_SALT", raising=False)
    monkeypatch.setattr(
        tools.ledger,
        "LEDGER",
        tmp_path / "no-such-default-ledger.jsonl",
    )


def digest(seed: int, salt: str) -> str:
    """Compute the commitment with ``hashlib`` (independent of
    ``make_commitment``).
    """
    return hashlib.sha256(f"{seed}:{salt}".encode()).hexdigest()


def build_ledger(path: Path, entries: list[dict]) -> Path:
    """Write a hash-chained ledger line by line, chaining with ``hashlib``.

    The chain is independent of the production code. Each entry is a dict of
    ``type`` and ``data``; ``seq`` and ``prev_sha256`` are set here.
    """
    assert (
        tmp_root(path) is not None
    ), "fixture ledgers live under tmp_path (LPC.PC.7)"
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


def tmp_root(path: Path) -> Path | None:
    """Return ``path`` if it is outside the repository (so it is a temporary
    file).
    """
    return None if ROOT in path.resolve().parents else path


def commitment(
    seed_id: str,
    seed: int,
    salt: str,
    kind: str = "commitment",
) -> dict:
    """Make a ledger entry holding the commitment of ``seed`` and ``salt``."""
    return {
        "type": kind,
        "data": {"seed_id": seed_id, "sha256": digest(seed, salt)},
    }


def write_registry(
    path: Path,
    seeds: list[dict],
    schema: str = REGISTRY_SCHEMA,
) -> Path:
    """Write a synthetic registry file and return its path."""
    path.write_text(json.dumps({"schema": schema, "seeds": seeds}))
    return path


def test_dev_0_resolves_to_the_pilot_seed() -> None:
    """``DEV-0`` resolves to 20261005, the seed of the pilot record.

    Reference: the literal 20261005 of the v1 ``config.py`` and the pilot
    record.
    Tolerance: none (exact).
    """
    assert (
        resolve_dev_seed("DEV-0", load_registry(REGISTRY_PATH)) == DEV_0_LITERAL
    )


def test_dev_1_resolves_to_the_registry_value() -> None:
    """``DEV-1`` resolves to the value that ``json.load`` finds in the registry
    file.

    Reference: the test parses the file itself (independent of
    ``load_registry``). Tolerance: none (exact integer equality). The value
    exceeds 2**32, so this also checks that no narrowing occurs.
    """
    with REGISTRY_PATH.open() as handle:
        entries = json.load(handle)["seeds"]
    expected = next(e["value"] for e in entries if e["id"] == "DEV-1")
    assert expected > 2**32
    assert resolve_dev_seed("DEV-1", load_registry(REGISTRY_PATH)) == expected


def test_real_registry_matches_its_json_exactly() -> None:
    """The loaded registry equals the id/value pairs of the file.

    Reference: ``json.load`` of the file. Tolerance: none (exact equality of a
    mapping).
    """
    with REGISTRY_PATH.open() as handle:
        entries = json.load(handle)["seeds"]
    assert load_registry(REGISTRY_PATH) == {
        e["id"]: e["value"] for e in entries
    }


def test_loader_rejects_a_different_schema(tmp_path: Path) -> None:
    """A registry whose ``schema`` differs from ``lpcstudy.seed-registry/1`` is
    refused.

    Reference: the roadmap criterion (WU-0001.1). Tolerance: none.
    """
    path = write_registry(
        tmp_path / "r.json",
        [{"id": "DEV-0", "value": 1}],
        schema="lpcstudy.seed-registry/2",
    )
    with pytest.raises(SeedRefusal, match=r"LPC\.PC\.7"):
        load_registry(path)


@pytest.mark.parametrize(
    "seeds",
    [
        [
            {"id": "DEV-0", "value": 1},
            {"id": "DEV-0", "value": 2},
        ],  # duplicate id
        [
            {"id": "DEV-0", "value": 7},
            {"id": "DEV-1", "value": 7},
        ],  # duplicate value
        [{"id": "DEV-0", "value": True}],  # bool is not an int
        [{"id": "DEV-0", "value": 1.0}],  # float
        [{"id": "DEV-0", "value": "5"}],  # string
        [{"id": "DEV-0", "value": -1}],  # below range
        [{"id": "DEV-0", "value": 2**64}],  # above range
        [{"id": "CONF-1", "value": 5}],  # not a DEV id
        [{"id": "DEV-01", "value": 5}],  # leading zero
        [{"id": "dev-1", "value": 5}],  # case
        [{"value": 5}],  # no id
        ["DEV-0"],  # entry not a mapping
    ],
)
def test_loader_rejects_a_bad_entry(tmp_path: Path, seeds: list) -> None:
    """Each malformed registry entry is refused with a message naming LPC.PC.7.

    The cases cover a repeated id or value, a value that is a bool, float,
    string or out of range, an id that is not ``DEV-n``, and an entry that is
    not a mapping.

    Reference: the rules of the plan (WU-0001.1): ids match
    ``^DEV-(0|[1-9][0-9]*)$``, ids and values are unique, a value is an ``int``
    (not ``bool``) in [0, 2**64).
    """
    with pytest.raises(SeedRefusal, match=r"LPC\.PC\.7"):
        load_registry(write_registry(tmp_path / "r.json", seeds))


def test_loader_accepts_the_range_ends(tmp_path: Path) -> None:
    """The values 0 and 2**64 - 1 are valid (the interval is [0, 2**64))."""
    path = write_registry(
        tmp_path / "r.json",
        [{"id": "DEV-0", "value": 0}, {"id": "DEV-7", "value": 2**64 - 1}],
    )
    assert load_registry(path) == {"DEV-0": 0, "DEV-7": 2**64 - 1}


@pytest.mark.parametrize(
    "content",
    ["", "not json", "[]", '{"schema": "lpcstudy.seed-registry/1"}'],
)
def test_loader_rejects_unparsable_or_empty_documents(
    tmp_path: Path,
    content: str,
) -> None:
    """Invalid JSON, a non-object and a missing ``seeds`` list are refused.

    The loader must refuse them with a clear message, not crash on them.
    """
    path = tmp_path / "r.json"
    path.write_text(content)
    with pytest.raises(SeedRefusal, match=r"LPC\.PC\.7"):
        load_registry(path)


def test_loader_rejects_a_missing_file(tmp_path: Path) -> None:
    """A missing registry file is a refusal."""
    with pytest.raises(SeedRefusal, match=r"LPC\.PC\.7"):
        load_registry(tmp_path / "absent.json")


def test_refusal_messages_hold_no_seed_value(tmp_path: Path) -> None:
    """A duplicate-value refusal names the two ids and never the value.

    Reference: the rule that messages never contain a seed value (plan
    interface).
    """
    path = write_registry(
        tmp_path / "r.json",
        [
            {"id": "DEV-0", "value": 424242424242},
            {"id": "DEV-1", "value": 424242424242},
        ],
    )
    with pytest.raises(SeedRefusal) as caught:
        load_registry(path)
    assert "424242424242" not in str(caught.value)
    assert "DEV-0" in str(caught.value) and "DEV-1" in str(caught.value)


@pytest.mark.parametrize(
    "seed_id",
    ["DEV-99", "5", "dev-1", "DEV-01", "CONF-1", "", "DEV-1 ", "20261005"],
)
def test_resolve_refuses_unknown_and_malformed_ids(seed_id: str) -> None:
    """Unknown ids, raw integers, wrong case, leading zeros and CONF ids are
    refused.

    Reference: the plan: only registered ``DEV-n`` ids resolve. A raw integer
    such as 20261005 is refused without being echoed.
    """
    with pytest.raises(SeedRefusal, match=r"LPC\.PC\.7") as caught:
        resolve_dev_seed(seed_id, load_registry(REGISTRY_PATH))
    if seed_id.isdigit():
        assert seed_id not in str(caught.value)


def test_with_seed_replaces_exactly_the_id_and_the_seed() -> None:
    """``with_seed`` changes ``seed_id`` and ``seed`` and nothing else.

    Reference: ``dataclasses.fields`` compared field by field. Tolerance: none
    (exact).
    """
    other = with_seed(SMOKE, "DEV-1", 12345)
    assert (other.seed_id, other.seed) == ("DEV-1", 12345)
    for name in SMOKE.__dataclass_fields__:
        if name not in ("seed", "seed_id"):
            assert getattr(other, name) == getattr(SMOKE, name), name


# WU-0001.2: commitment check


def test_fixture_ledger_is_outside_the_repository(tmp_path: Path) -> None:
    """The fixture ledger lives under ``tmp_path``, never in the repository
    (LPC.PC.7).

    Reference: the roadmap criterion asserts the fixture path is under
    ``tmp_path``. Tolerance: none (exact).
    """
    path = build_ledger(
        tmp_path / "ledger.jsonl",
        [commitment("CONF-1", SYNTHETIC_SEED, SYNTHETIC_SALT)],
    )
    assert path.parent == tmp_path and ROOT not in path.resolve().parents
    assert path != LEDGER_PATH


def test_fixture_chain_is_a_valid_chain(tmp_path: Path) -> None:
    """The fixture builder makes a chain that ``tools.ledger.verify_chain``
    accepts.

    Reference: the chain is built with ``hashlib`` in the test; ``verify_chain``
    is the production verifier, so this checks the fixture, not the guard.
    Tolerance: none (the result must be an empty list).
    """
    path = build_ledger(
        tmp_path / "l.jsonl",
        [{"type": "note", "data": {}}, commitment("CONF-1", 1, "aa")],
    )
    assert tools.ledger.verify_chain(path.read_text().splitlines()) == []


def test_matching_pair_is_accepted(tmp_path: Path) -> None:
    """A seed and salt whose digest equals the ledger entry are accepted.

    Reference: ``hashlib.sha256(f"{seed}:{salt}")`` computed in the test.
    Tolerance: none (exact).
    """
    ledger = build_ledger(
        tmp_path / "l.jsonl",
        [commitment("CONF-1", SYNTHETIC_SEED, SYNTHETIC_SALT)],
    )
    assert check_commitment(SYNTHETIC_SEED, SYNTHETIC_SALT, ledger) is None


@pytest.mark.parametrize(
    "seed, salt",
    [
        (SYNTHETIC_SEED + 1, SYNTHETIC_SALT),
        (SYNTHETIC_SEED, "0e" * 16),
        (SYNTHETIC_SEED, SYNTHETIC_SALT.upper()),
    ],
)
def test_wrong_seed_or_salt_is_refused(
    tmp_path: Path,
    seed: int,
    salt: str,
) -> None:
    """A wrong seed, a wrong salt and a salt in another case are each refused.

    Reference: the digest of the committed pair, from ``hashlib``; any other
    pair differs (SHA-256 collisions are not a concern). The messages hold
    neither the seed nor the salt.
    """
    ledger = build_ledger(
        tmp_path / "l.jsonl",
        [commitment("CONF-1", SYNTHETIC_SEED, SYNTHETIC_SALT)],
    )
    with pytest.raises(SeedRefusal, match=r"LPC\.PC\.7") as caught:
        check_commitment(seed, salt, ledger)
    for secret in (str(seed), str(SYNTHETIC_SEED), salt, SYNTHETIC_SALT):
        assert secret not in str(caught.value)


@pytest.mark.parametrize(
    "entries",
    [
        [],  # empty ledger
        [{"type": "note", "data": {}}],  # no commitment
        [
            commitment("OTHER-1", SYNTHETIC_SEED, SYNTHETIC_SALT)
        ],  # other seed id
        [
            commitment("CONF-1", SYNTHETIC_SEED, SYNTHETIC_SALT, kind="note")
        ],  # wrong type
        [{"type": "commitment", "data": {"seed_id": "CONF-1"}}],  # no digest
        [
            {"type": "commitment", "data": {"seed_id": "CONF-1", "sha256": 5}}
        ],  # digest not text
        [{"type": "commitment", "data": "CONF-1"}],  # data not a dict
    ],
)
def test_ledger_without_a_conf_1_commitment_is_refused(
    tmp_path: Path,
    entries: list[dict],
) -> None:
    """A ledger with no usable ``CONF-1`` commitment refuses even a pair that
    would match.

    Reference: the roadmap criterion (no ``CONF-1`` entry is refused); the
    variants are each an entry that must not count. Tolerance: none (exact).
    """
    ledger = build_ledger(tmp_path / "l.jsonl", entries)
    with pytest.raises(SeedRefusal, match=r"LPC\.PC\.7"):
        check_commitment(SYNTHETIC_SEED, SYNTHETIC_SALT, ledger)


def test_only_the_latest_commitment_counts(tmp_path: Path) -> None:
    """With two ``CONF-1`` entries only the later one is used.

    Reference: the plan (latest ``commitment`` entry). The earlier pair is
    refused and the later accepted. Tolerance: none (exact).
    """
    ledger = build_ledger(
        tmp_path / "l.jsonl",
        [
            commitment("CONF-1", SYNTHETIC_SEED, SYNTHETIC_SALT),
            {"type": "note", "data": {}},
            commitment("CONF-1", OTHER_SEED, SYNTHETIC_SALT),
        ],
    )
    check_commitment(OTHER_SEED, SYNTHETIC_SALT, ledger)
    with pytest.raises(SeedRefusal):
        check_commitment(SYNTHETIC_SEED, SYNTHETIC_SALT, ledger)


def test_other_seed_id_entries_do_not_shadow_conf_1(tmp_path: Path) -> None:
    """A later commitment for another id does not replace the ``CONF-1`` one."""
    ledger = build_ledger(
        tmp_path / "l.jsonl",
        [
            commitment("CONF-1", SYNTHETIC_SEED, SYNTHETIC_SALT),
            commitment("CONF-2", OTHER_SEED, SYNTHETIC_SALT),
        ],
    )
    check_commitment(SYNTHETIC_SEED, SYNTHETIC_SALT, ledger)
    check_commitment(OTHER_SEED, SYNTHETIC_SALT, ledger, seed_id="CONF-2")


def test_broken_chain_is_refused(tmp_path: Path) -> None:
    """A ledger whose chain is broken is refused although its commitment
    matches.

    Reference: the chain is built with ``hashlib``; the first line is then
    edited, so the second entry's ``prev_sha256`` no longer equals the hash of
    line 1.
    Tolerance: none (exact).
    """
    ledger = build_ledger(
        tmp_path / "l.jsonl",
        [
            {"type": "note", "data": {}},
            commitment("CONF-1", SYNTHETIC_SEED, SYNTHETIC_SALT),
        ],
    )
    lines = ledger.read_text().splitlines()
    lines[0] = lines[0].replace("synthetic", "tampered")
    ledger.write_text("\n".join(lines) + "\n")
    with pytest.raises(SeedRefusal, match="chain"):
        check_commitment(SYNTHETIC_SEED, SYNTHETIC_SALT, ledger)


def test_missing_ledger_is_refused_not_read_from_the_default(
    tmp_path: Path,
) -> None:
    """A missing ledger path is refused; the default ledger is never consulted.

    Reference: ``tools.ledger.LEDGER`` is monkeypatched to a nonexistent file by
    the autouse fixture, so a stray default read would also fail here.
    """
    with pytest.raises(SeedRefusal, match=r"LPC\.PC\.7"):
        check_commitment(
            SYNTHETIC_SEED,
            SYNTHETIC_SALT,
            tmp_path / "absent.jsonl",
        )


def test_development_path_does_not_import_the_tools() -> None:
    """Resolving a DEV seed imports nothing from ``tools``.

    Importing ``lpcstudy.seeds`` and resolving a DEV seed must not import the
    commitment tools, which belong to the confirmatory path only.

    Reference: ``sys.modules`` of a fresh interpreter (the plan: lazy ``tools``
    imports).
    """
    code = (
        "import sys; from lpcstudy.seeds import *; "
        "resolve_dev_seed('DEV-0', load_registry(REGISTRY_PATH)); "
        "sys.exit(any(m == 'tools' or m.startswith('tools.') for m in "
        "sys.modules))"
    )
    done = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        capture_output=True,
    )
    assert done.returncode == 0, done.stderr.decode()[-500:]


# confirmatory_seed (reads the environment)


def environment(
    seed: str | None = str(SYNTHETIC_SEED),
    salt: str | None = SYNTHETIC_SALT,
) -> dict[str, str]:
    """Make a synthetic environment mapping with the seed and salt variables."""
    return {
        k: v
        for k, v in (("LPC_CONF_SEED", seed), ("LPC_CONF_SALT", salt))
        if v is not None
    }


def test_confirmatory_seed_returns_the_verified_seed(tmp_path: Path) -> None:
    """The environment pair that matches the ledger is returned as an ``int``.

    Reference: the synthetic seed literal. Tolerance: none (exact).
    """
    ledger = build_ledger(
        tmp_path / "l.jsonl",
        [commitment("CONF-1", SYNTHETIC_SEED, SYNTHETIC_SALT)],
    )
    assert confirmatory_seed(environment(), ledger) == SYNTHETIC_SEED


@pytest.mark.parametrize(
    "env",
    [
        environment(None, None),
        environment(None),
        environment(salt=None),
        environment(seed=""),
        environment(salt=""),
        environment(seed="12 34"),
        environment(seed="-5"),
        environment(seed="1e5"),
        environment(seed=str(2**64)),
        environment(seed="\u0661\u0662"),  # Arabic-Indic digits
        environment(salt="ABCDEF"),
        environment(salt="xyz"),
        environment(salt="0f\n"),
        environment(seed=str(SYNTHETIC_SEED + 1)),  # valid shape, no match
    ],
)
def test_confirmatory_seed_refuses_missing_malformed_and_mismatched(
    tmp_path: Path,
    env: dict[str, str],
) -> None:
    """Missing, empty or malformed variables and a mismatching pair are refused.

    Reference: the plan (both variables required; seed ``^[0-9]+$`` below 2**64;
    salt non-empty lowercase hex). The refusal never contains the seed or the
    salt.
    """
    ledger = build_ledger(
        tmp_path / "l.jsonl",
        [commitment("CONF-1", SYNTHETIC_SEED, SYNTHETIC_SALT)],
    )
    with pytest.raises(SeedRefusal, match=r"LPC\.PC\.7") as caught:
        confirmatory_seed(env, ledger)
    for value in env.values():
        if len(value) > 4:
            assert value not in str(caught.value)


def test_confirmatory_seed_accepts_the_range_top(tmp_path: Path) -> None:
    """The value 2**64 - 1 is a valid seed (the bound is exclusive at 2**64)."""
    top = 2**64 - 1
    ledger = build_ledger(
        tmp_path / "l.jsonl",
        [commitment("CONF-1", top, SYNTHETIC_SALT)],
    )
    assert confirmatory_seed(environment(seed=str(top)), ledger) == top
