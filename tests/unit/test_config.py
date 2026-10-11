"""Study configuration constants (WU-0001.1)."""

from __future__ import annotations

import dataclasses
import json

from lpcstudy.config import PRESETS, StudyConfig
from lpcstudy.seeds import REGISTRY_PATH


def test_every_preset_seed_pair_is_a_registry_entry() -> None:
    """Each preset's ``(seed_id, seed)`` equals the registry's entry for that id.

    Reference: the test parses ``seeds/development_seeds.json`` with ``json.load`` (not
    ``load_registry``). Exact integer and string equality; no tolerance.
    """
    with REGISTRY_PATH.open() as handle:
        registry = {e["id"]: e["value"] for e in json.load(handle)["seeds"]}
    assert set(PRESETS) == {"full", "pilot", "smoke"}
    for name, preset in PRESETS.items():
        assert preset.seed_id == "DEV-0", name
        assert registry[preset.seed_id] == preset.seed == 20261005, name


def test_seed_id_is_the_last_field() -> None:
    """``seed_id`` follows ``seed``: the key order of ``asdict`` keeps the v1 prefix.

    Reference: the plan fixes ``seed_id`` as the new last field. Exact.
    """
    keys = list(dataclasses.asdict(StudyConfig()))
    assert keys[-2:] == ["seed", "seed_id"]


def test_config_has_no_transfer_fields() -> None:
    """``StudyConfig`` has no ``transfer*`` field and no preset names Lorenz-96 (WU-0002.1).

    Reference: decision log D3 and the WU-0002.1 acceptance row (transfer and Lorenz-96 are not in
    v3), written out in the test. Tolerance: none; exact checks of field names and strings.
    """
    assert [f.name for f in dataclasses.fields(StudyConfig) if f.name.startswith("transfer")] == []
    for preset in PRESETS.values():
        assert "lorenz96" not in preset.core_systems


def test_k_rule_candidates_cover_eight() -> None:
    """The K-rule candidates are exactly {2, 3, 4, 5, 6, 8} for FULL and PILOT (v3 §5, M2 §M7).

    Reference: the candidate set written out from the proposal (D-13): K up to 8, with 12 and
    16 kept only for the abstraction curve; SMOKE keeps its short list {2, 3, 4}. Tolerance:
    none; exact comparison of integer lists.
    """
    for preset in (PRESETS["full"], PRESETS["pilot"]):
        assert [k for k in preset.regime_counts if k <= preset.regime_max_primary] \
            == [2, 3, 4, 5, 6, 8]
    smoke = PRESETS["smoke"]
    assert [k for k in smoke.regime_counts if k <= smoke.regime_max_primary] == [2, 3, 4]
