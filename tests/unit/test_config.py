"""Tests for ``lpcstudy.config``: study constants and presets (WU-0001.1).

``config`` holds every design constant in one frozen object. These tests pin the
facts that other documents fix (seed registry, field order, section sizes of the
Methods document), so a stray edit to a constant is caught.
"""

from __future__ import annotations

import dataclasses
import json

from lpcstudy.config import PRESETS, StudyConfig
from lpcstudy.seeds import REGISTRY_PATH


def test_every_preset_seed_pair_is_a_registry_entry() -> None:
    """Each preset's seed pair is the registry's entry for its id.

    ``(seed_id, seed)`` must equal the entry of
    ``seeds/development_seeds.json``.

    Reference: the test reads ``seeds/development_seeds.json`` with
    ``json.load`` (not with ``load_registry``), so the check does not depend on
    the code under test. Tolerance: none (exact integer and string equality).
    """
    with REGISTRY_PATH.open() as handle:
        registry = {e["id"]: e["value"] for e in json.load(handle)["seeds"]}
    assert set(PRESETS) == {"full", "pilot", "smoke"}
    for name, preset in PRESETS.items():
        assert preset.seed_id == "DEV-0", name
        assert registry[preset.seed_id] == preset.seed == 20261005, name


def test_seed_id_is_the_last_field() -> None:
    """``seed_id`` follows ``seed`` as the last field of the configuration.

    This keeps the key order of ``asdict`` (and so of ``results.json``) the same
    as before ``seed_id`` was added. Reference: the plan fixes ``seed_id`` as
    the new last field. Tolerance: none (exact).
    """
    keys = list(dataclasses.asdict(StudyConfig()))
    assert keys[-2:] == ["seed", "seed_id"]


def test_config_has_no_transfer_fields() -> None:
    """No ``transfer*`` field and no Lorenz-96 preset remain (WU-0002.1).

    ``StudyConfig`` must have no ``transfer*`` field, and no preset names
    Lorenz-96.

    Reference: decision log D3 and the WU-0002.1 acceptance row (the transfer
    test and Lorenz-96 are not in v3), written out in the test. Tolerance: none
    (exact checks of field names and strings).
    """
    assert [
        f.name
        for f in dataclasses.fields(StudyConfig)
        if f.name.startswith("transfer")
    ] == []
    for preset in PRESETS.values():
        assert "lorenz96" not in preset.core_systems


def test_test_sweep_sizes_follow_the_methods_document() -> None:
    """The test-sweep sizes follow the Methods document (WU-0002.10).

    ``n_test_sweep`` is 1000 (full) and 300 (pilot), and never exceeds
    ``n_test``.

    Reference: v3 section 4 and Methods v2 M2 section M8 (D-15), written out
    here. The full sweep uses 1000 test states and the pilot 300. The sweep
    takes the first ``n_test`` rows, so it cannot be larger than ``n_test`` for
    any preset. The smoke value 60 is the unchanged plan value. Tolerance: none
    (exact integer equality and ordering).
    """
    assert PRESETS["full"].n_test_sweep == 1000
    assert PRESETS["pilot"].n_test_sweep == 300
    assert PRESETS["smoke"].n_test_sweep == 60
    for name, preset in PRESETS.items():
        assert preset.n_test_sweep <= preset.n_test, name


def test_k_rule_candidates_cover_eight() -> None:
    """The candidate numbers of regimes are {2, 3, 4, 5, 6, 8} (v3 section 5).

    These are the candidates ``K`` of the rule in M2 section M7.

    This holds for the full and pilot presets; the smoke preset keeps its short
    list {2, 3, 4}. Reference: the candidate set written out from the proposal
    (D-13): ``K`` up to 8, with 12 and 16 kept only for the abstraction curve.
    Tolerance: none (exact comparison of integer lists).
    """
    for preset in (PRESETS["full"], PRESETS["pilot"]):
        assert [
            k for k in preset.regime_counts if k <= preset.regime_max_primary
        ] == [2, 3, 4, 5, 6, 8]
    smoke = PRESETS["smoke"]
    assert [
        k for k in smoke.regime_counts if k <= smoke.regime_max_primary
    ] == [2, 3, 4]
