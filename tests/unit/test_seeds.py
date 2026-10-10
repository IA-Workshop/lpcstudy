"""Seed registry and guard (WU-0001.1, .2; LPC.PC.7, NVVUQ.18).

Every check is exact (integers, strings, identical decisions); no numerical tolerance
applies. The confirmatory seed is never used: the seeds below are synthetic and every
ledger is built in ``tmp_path`` (LPC.PC.7).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lpcstudy.config import SMOKE
from lpcstudy.seeds import (REGISTRY_PATH, REGISTRY_SCHEMA, SeedRefusal, load_registry,
                            resolve_dev_seed, with_seed)

DEV_0_LITERAL = 20261005  # v1 config.py default and the pilot record (docs/study)


@pytest.fixture(autouse=True)
def _clean_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """No test sees a confirmatory seed or salt (LPC.PC.7)."""
    monkeypatch.delenv("LPC_CONF_SEED", raising=False)
    monkeypatch.delenv("LPC_CONF_SALT", raising=False)


def write_registry(path: Path, seeds: list[dict], schema: str = REGISTRY_SCHEMA) -> Path:
    """Write a synthetic registry file."""
    path.write_text(json.dumps({"schema": schema, "seeds": seeds}))
    return path


def test_dev_0_resolves_to_the_pilot_seed() -> None:
    """``DEV-0`` resolves to 20261005.

    Reference: the literal 20261005 of the v1 ``config.py`` and the pilot record. Exact.
    """
    assert resolve_dev_seed("DEV-0", load_registry(REGISTRY_PATH)) == DEV_0_LITERAL


def test_dev_1_resolves_to_the_registry_value() -> None:
    """``DEV-1`` resolves to the value that ``json.load`` finds in the registry file.

    Reference: the test parses the file itself (independent of ``load_registry``). Exact
    integer equality; the value exceeds 2**32, so this also checks that no narrowing occurs.
    """
    with REGISTRY_PATH.open() as handle:
        entries = json.load(handle)["seeds"]
    expected = next(e["value"] for e in entries if e["id"] == "DEV-1")
    assert expected > 2 ** 32
    assert resolve_dev_seed("DEV-1", load_registry(REGISTRY_PATH)) == expected


def test_real_registry_matches_its_json_exactly() -> None:
    """The loaded registry equals the file's id/value pairs.

    Reference: ``json.load`` of the file. Exact equality of a mapping.
    """
    with REGISTRY_PATH.open() as handle:
        entries = json.load(handle)["seeds"]
    assert load_registry(REGISTRY_PATH) == {e["id"]: e["value"] for e in entries}


def test_loader_rejects_a_different_schema(tmp_path: Path) -> None:
    """A registry whose ``schema`` differs from ``lpcstudy.seed-registry/1`` is refused.

    Reference: the roadmap criterion (WU-0001.1). Exact.
    """
    path = write_registry(tmp_path / "r.json", [{"id": "DEV-0", "value": 1}],
                          schema="lpcstudy.seed-registry/2")
    with pytest.raises(SeedRefusal, match=r"LPC\.PC\.7"):
        load_registry(path)


@pytest.mark.parametrize("seeds", [
    [{"id": "DEV-0", "value": 1}, {"id": "DEV-0", "value": 2}],       # duplicate id
    [{"id": "DEV-0", "value": 7}, {"id": "DEV-1", "value": 7}],       # duplicate value
    [{"id": "DEV-0", "value": True}],                                  # bool is not an int
    [{"id": "DEV-0", "value": 1.0}],                                   # float
    [{"id": "DEV-0", "value": "5"}],                                   # string
    [{"id": "DEV-0", "value": -1}],                                    # below range
    [{"id": "DEV-0", "value": 2 ** 64}],                               # above range
    [{"id": "CONF-1", "value": 5}],                                    # not a DEV id
    [{"id": "DEV-01", "value": 5}],                                    # leading zero
    [{"id": "dev-1", "value": 5}],                                     # case
    [{"value": 5}],                                                    # no id
    ["DEV-0"],                                                         # entry not a mapping
])
def test_loader_rejects_a_bad_entry(tmp_path: Path, seeds: list) -> None:
    """Each malformed registry entry is refused with a message naming LPC.PC.7.

    Reference: the rules of the plan (WU-0001.1): ids match ``^DEV-(0|[1-9][0-9]*)$``,
    ids and values are unique, a value is an ``int`` (not ``bool``) in [0, 2**64).
    """
    with pytest.raises(SeedRefusal, match=r"LPC\.PC\.7"):
        load_registry(write_registry(tmp_path / "r.json", seeds))


def test_loader_accepts_the_range_ends(tmp_path: Path) -> None:
    """0 and 2**64 - 1 are valid values (the interval is [0, 2**64))."""
    path = write_registry(tmp_path / "r.json", [{"id": "DEV-0", "value": 0},
                                                {"id": "DEV-7", "value": 2 ** 64 - 1}])
    assert load_registry(path) == {"DEV-0": 0, "DEV-7": 2 ** 64 - 1}


@pytest.mark.parametrize("content", ["", "not json", "[]", '{"schema": "lpcstudy.seed-registry/1"}'])
def test_loader_rejects_unparsable_or_empty_documents(tmp_path: Path, content: str) -> None:
    """Invalid JSON, a non-object and a missing ``seeds`` list are refused, not crashed on."""
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

    Reference: the rule that messages never contain a seed value (plan interface).
    """
    path = write_registry(tmp_path / "r.json", [{"id": "DEV-0", "value": 424242424242},
                                                {"id": "DEV-1", "value": 424242424242}])
    with pytest.raises(SeedRefusal) as caught:
        load_registry(path)
    assert "424242424242" not in str(caught.value)
    assert "DEV-0" in str(caught.value) and "DEV-1" in str(caught.value)


@pytest.mark.parametrize("seed_id", ["DEV-99", "5", "dev-1", "DEV-01", "CONF-1", "", "DEV-1 ",
                                     "20261005"])
def test_resolve_refuses_unknown_and_malformed_ids(seed_id: str) -> None:
    """Unknown ids, raw integers, wrong case, leading zeros and CONF ids are refused.

    Reference: the plan: only registered ``DEV-n`` ids resolve. A raw integer such as
    20261005 is refused without being echoed.
    """
    with pytest.raises(SeedRefusal, match=r"LPC\.PC\.7") as caught:
        resolve_dev_seed(seed_id, load_registry(REGISTRY_PATH))
    if seed_id.isdigit():
        assert seed_id not in str(caught.value)


def test_with_seed_replaces_exactly_the_id_and_the_seed() -> None:
    """``with_seed`` changes ``seed_id`` and ``seed`` and nothing else.

    Reference: ``dataclasses.fields`` compared field by field. Exact.
    """
    other = with_seed(SMOKE, "DEV-1", 12345)
    assert (other.seed_id, other.seed) == ("DEV-1", 12345)
    for name in SMOKE.__dataclass_fields__:
        if name not in ("seed", "seed_id"):
            assert getattr(other, name) == getattr(SMOKE, name), name
