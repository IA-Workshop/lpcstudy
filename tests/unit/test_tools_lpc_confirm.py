"""Tests of ``tools/lpc_confirm.py``, the phase J verdict tool (WU-0054).

Synthetic seed sets only: every record, ``results.json`` and cache file is
written here, with fake seed ids and no seed value. The reading rows are
built by ``lpc_replicate.seed_rows`` (tested in
``test_tools_lpc_replicate.py``); the row used is A drop-one, oracle,
H=30, ``drop I: MSE ratio``, whose words carry the 1.05 table's claims.

Reference: verdicts computed by hand from the rule of the claim table
(``docs/study/preregistration_phase_j/claims.json``) and the words'
definitions (``substantial`` = ratio > 1.05, ``negligible`` = ratio <= 1.05,
``small`` = 1 < ratio <= 1.05, ``undetermined`` = no claim). For the claim
``ratio > 1.05``: ``substantial`` implies it, ``small`` and ``negligible``
do not, and ``negligible`` contradicts ``substantial``. Tolerance: none
(words, counts, exit codes).
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
TOOLS = REPO / "tools"
sys.path.insert(0, str(TOOLS))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, TOOLS / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclasses resolve their module
    spec.loader.exec_module(module)
    return module


tool = _load("lpc_confirm")
base = sys.modules["lpc_contrib"]
rep = sys.modules["lpc_replicate"]

PINNED = REPO / "docs" / "study" / "preregistration_phase_j" / "lyapunov.json"
SEALED = [f"CONF-{k}" for k in range(5, 10)]
DEV = [f"DEV-{k}" for k in range(5, 10)]
SYSTEMS = ("lorenz63", "rossler")
ITEM = "drop I: MSE ratio"
HORIZON = "H=30 (1.00 LT)"
DEV_LABEL = "DEVELOPMENT ({seed_id}): exploratory, not a hypothesis test"


def table(claim: str = "ratio > 1.05", systems=SYSTEMS) -> dict:
    return {
        "schema": tool.SCHEMA,
        "rule": "the rule (synthetic)",
        "minimum": 4,
        "n_seeds": 5,
        "seed_ids": SEALED,
        "claims": [
            {
                "id": "J-T1",
                "tier": 1,
                "statement": "synthetic",
                "claim": claim,
                "rows": [
                    {
                        "family": "A drop-one",
                        "system": s,
                        "profile": "oracle",
                        "horizon": HORIZON,
                        "item": ITEM,
                    }
                    for s in systems
                ],
            }
        ],
    }


def contrib_system(words: dict[str, str]) -> dict:
    """A/D rows of one system: ``drop X: MSE ratio`` with the given words."""
    return {
        "allocation": {
            "30": {
                "oracle": {
                    "horizon": HORIZON,
                    "drop_one": {
                        x: {"mse_ratio": {"reading": w}}
                        for x, w in words.items()
                    },
                    "subsets": {},
                    "ladder": {"vs_full": {}, "vs_below": {}},
                }
            }
        },
        "interactions": {},
        "horizon": {},
    }


def write_seed(
    root: Path,
    seed: str,
    words: dict[str, str],
    gate: dict[str, bool] | None = None,
    sealed: bool = True,
    cache: bytes | None = None,
    commit: str = "abc123",
    extra: dict[str, str] | None = None,
) -> Path:
    """``<root>/<seed>/phasej/`` (run) and ``<root>/<seed>/contrib-x/``.

    ``words`` maps a system to its ``drop I`` word; ``extra`` adds a
    ``drop R`` word per system (a row outside the claim table).
    """
    run = root / seed / "phasej"
    (run / "cache").mkdir(parents=True)
    (run / "cache" / "lyapunov.json").write_bytes(
        PINNED.read_bytes() if cache is None else cache
    )
    gate = gate or {}
    (run / "results.json").write_text(
        json.dumps(
            {
                "provenance": {
                    "seed_id": seed,
                    "seed_kind": "confirmatory" if sealed else "development",
                    "commit": "r1",
                    "complete": True,
                },
                "config": {"seed": None if sealed else 1},
                "systems": {
                    s: {"validation": {"gate": {"gate_pass": gate.get(s, True)}}}
                    for s in words
                },
            }
        )
    )
    label = (base.SEALED_LABEL if sealed else DEV_LABEL).format(seed_id=seed)
    record_run = {
        "dir": f"runs/{seed}/phasej",
        "seed_id": seed,
        "commit": "r1",
        "preset": "phasej",
    }
    contrib = {
        "label": label,
        "run": record_run,
        "analysis": {"commit": commit, "dirty": False},
        "systems": {
            s: contrib_system({"I": w, **({"R": extra[s]} if extra else {})})
            for s, w in words.items()
        },
    }
    ce = {
        "label": label,
        "run": dict(record_run),
        "analysis": {"commit": commit, "dirty": False},
        "abd": {"path": "contrib.json", "commit": commit},
        "systems": {},
    }
    folder = root / seed / "contrib-x"
    folder.mkdir()
    (folder / "contrib.json").write_text(json.dumps(contrib))
    (folder / "ce.json").write_text(json.dumps(ce))
    return folder


def seed_set(
    root: Path,
    words: list[str],
    gates: list[bool] | None = None,
    sealed: bool = True,
    **kw,
) -> list[str]:
    """Five seeds; seed k reads ``words[k]`` on both systems, and its
    lorenz63 gate is ``gates[k]`` (rossler always passes)."""
    ids = SEALED if sealed else DEV
    gates = gates or [True] * len(words)
    return [
        str(
            write_seed(
                root,
                s,
                {x: w for x in SYSTEMS},
                gate={"lorenz63": g},
                sealed=sealed,
                **kw,
            )
        )
        for s, w, g in zip(ids, words, gates)
    ]


def run(tmp_path: Path, dirs: list[str], *flags: str, claims=None) -> tuple:
    path = tmp_path / "claims.json"
    path.write_text(json.dumps(claims or table()))
    out = tmp_path / "out"
    code = tool.main(
        [*dirs, "--claims", str(path), "--pinned", str(PINNED), "--out",
         str(out), *flags]
    )
    record = (
        json.loads((out / "confirm.json").read_text()) if code == 0 else None
    )
    return code, record, out


def verdict_of(record: dict, system: str = "lorenz63") -> tuple[str, str]:
    (row,) = [r for r in record["rows"] if r["system"] == system]
    (claim,) = [v for v in record["verdicts"] if v["system"] == system]
    return row["verdict"], claim["verdict"]


S, U, N = "substantial", "undetermined", "negligible"


# ------------------------------------------------------------- the rule
@pytest.mark.parametrize(
    ("words", "gates", "expected", "n_implying", "n_present"),
    [
        pytest.param([S] * 5, None, "confirmed", 5, 5, id="5-of-5"),
        pytest.param([S] * 4 + [U], None, "confirmed", 4, 5,
                     id="4-of-5-one-claim-free"),
        pytest.param([S] * 3 + [U] * 2, None, "not confirmed", 3, 5,
                     id="3-of-5"),
        pytest.param([S] * 4 + [N], None, "contradicted", 4, 5,
                     id="one-contradicting-seed"),
        pytest.param([S] * 5, [True] * 4 + [False], "confirmed", 4, 4,
                     id="one-absent-4-implying"),
        pytest.param([S] * 5, [True] * 3 + [False] * 2, "not confirmable",
                     3, 3, id="two-absent"),
        # "needed, size not determined" = ratio > 1: compatible with
        # substantial, does not imply ratio > 1.05.
        pytest.param([S] * 3 + ["needed, size not determined"] * 2, None,
                     "not confirmed", 3, 5, id="3-implying-2-compatible"),
    ],
)
def test_row_and_system_verdicts_on_five_sealed_seeds(
    tmp_path: Path, words, gates, expected, n_implying, n_present
) -> None:
    """Hand-computed verdicts for lorenz63; rossler (gates pass) as a check.

    The system verdict equals the row verdict (one row per system). Absent
    seeds (failed lorenz63 gate) are not counted present on lorenz63 but are
    present on rossler, so rossler reads every seed.
    """
    code, record, out = run(tmp_path, seed_set(tmp_path, words, gates))
    assert code == 0
    assert verdict_of(record) == (expected, expected)
    (row,) = [r for r in record["rows"] if r["system"] == "lorenz63"]
    assert (row["n_implying"], row["n_present"]) == (n_implying, n_present)
    assert row["absent"] == [not g for g in (gates or [True] * 5)]
    rossler = sum(w == S for w in words)
    hand = (
        "contradicted" if N in words
        else "confirmed" if rossler >= 4 else "not confirmed"
    )
    assert verdict_of(record, "rossler") == (hand, hand)
    assert record["label"].startswith("PHASE J CONFIRMATORY (CONF-5")
    assert record["mode"] == "sealed"


def test_contradicting_pair_is_listed_and_beats_not_confirmable(
    tmp_path: Path,
) -> None:
    """Three absent seeds and a contradicting pair among the two present:
    "contradicted" (the rule's order: contradicted before not confirmable).
    """
    code, record, _ = run(
        tmp_path,
        seed_set(tmp_path, [S, N, S, S, S], [True, True, False, False, False]),
    )
    assert code == 0
    (row,) = [r for r in record["rows"] if r["system"] == "lorenz63"]
    assert row["verdict"] == "contradicted" and row["n_present"] == 2
    assert row["contradicting_pairs"] == [[0, S, 1, N]]


def test_claim_by_system_combines_rows() -> None:
    """Hand table of the per-system rule."""
    c, x, nc, n = (tool.CONFIRMED, tool.CONTRADICTED, tool.NOT_CONFIRMABLE,
                   tool.NOT_CONFIRMED)
    assert tool.system_verdict([c, c]) == c
    assert tool.system_verdict([c, x, nc]) == x
    assert tool.system_verdict([c, nc, n]) == nc
    assert tool.system_verdict([c, n]) == n


def test_point_claims_never_contradict() -> None:
    """Readings with point claims only: opposite sides of 1.05, no
    contradiction; four imply ``ratio > 1.05`` (through the word, S3), so
    the row is confirmed."""
    above = rep.Reading("p", (rep.Claim("ratio", ">", 1.05, "point"),), "p")
    below = rep.Reading("q", (rep.Claim("ratio", "<", 1.0, "point"),), "p")
    claim = rep.Claim("ratio", ">", 1.05)
    out = tool.row_verdict([above] * 4 + [below], claim, 4)
    assert out["contradicting_pairs"] == []
    assert out["verdict"] == "confirmed" and out["n_implying"] == 4
    out = tool.row_verdict([above] * 3 + [below] * 2, claim, 4)
    assert out["verdict"] == "not confirmed"


def test_only_table_rows_are_reported(tmp_path: Path) -> None:
    """A ``drop R`` row on every seed is outside the table: not in the
    output (JSON rows or markdown)."""
    dirs = [
        str(write_seed(tmp_path, s, {x: S for x in SYSTEMS},
                       extra={x: "lowers" for x in SYSTEMS}))
        for s in SEALED
    ]
    code, record, out = run(tmp_path, dirs)
    assert code == 0
    assert {r["item"] for r in record["rows"]} == {ITEM}
    assert len(record["rows"]) == 2
    assert "drop R" not in (out / "confirm.md").read_text()


def test_markdown_labels_every_table(tmp_path: Path) -> None:
    """The label paragraph comes before every table of ``confirm.md``."""
    code, record, out = run(tmp_path, seed_set(tmp_path, [S] * 5))
    assert code == 0
    blocks = (out / "confirm.md").read_text().split("\n\n")
    tables = [i for i, b in enumerate(blocks) if b.lstrip().startswith("|")]
    assert len(tables) == 3  # inputs, verdicts, one claim
    for i in tables:
        assert record["label"] in blocks[i - 1]


# ------------------------------------------------------------- refusals
def test_missing_pre_registered_row_is_an_error(tmp_path: Path) -> None:
    """A present seed without the row: exit 64, nothing written."""
    dirs = seed_set(tmp_path, [S] * 5)
    claims = table()
    claims["claims"][0]["rows"][0]["item"] = "drop O: MSE ratio"
    code, _, out = run(tmp_path, dirs, claims=claims)
    assert code == 64 and not out.exists()


def test_missing_row_on_an_absent_seed_is_not_an_error(tmp_path: Path) -> None:
    """A seed whose lorenz63 gate failed and that has no lorenz63 rows is
    absent there, not an error."""
    dirs = seed_set(tmp_path, [S] * 4)
    last = write_seed(tmp_path, "CONF-9", {"rossler": S, "lorenz63": S},
                      gate={"lorenz63": False})
    contrib = json.loads((last / "contrib.json").read_text())
    del contrib["systems"]["lorenz63"]
    (last / "contrib.json").write_text(json.dumps(contrib))
    code, record, _ = run(tmp_path, [*dirs, str(last)])
    assert code == 0 and verdict_of(record) == ("confirmed", "confirmed")


@pytest.mark.parametrize(
    "case",
    [
        "cache mismatch",
        "development run without rehearsal",
        "sealed run with rehearsal",
        "ignore gate when sealed",
        "seed repeated",
        "commits differ",
        "seed set not pre-registered",
        "claim on a wrong quantity",
        "unparsable claim",
        "record label",
    ],
)
def test_refusals_write_nothing(tmp_path: Path, case: str) -> None:
    """Each refusal: exit 64 and no output folder."""
    flags: list[str] = []
    claims = None
    if case == "cache mismatch":
        dirs = seed_set(tmp_path, [S] * 5)
        cache = Path(dirs[2]).parent / "phasej" / "cache" / "lyapunov.json"
        cache.write_bytes(cache.read_bytes() + b" ")
    elif case == "development run without rehearsal":
        dirs = seed_set(tmp_path, [S] * 5, sealed=False)
    elif case == "sealed run with rehearsal":
        dirs = seed_set(tmp_path, [S] * 5)
        flags = ["--rehearsal"]
    elif case == "ignore gate when sealed":
        dirs = seed_set(tmp_path, [S] * 5)
        flags = ["--ignore-gate"]
    elif case == "seed repeated":
        dirs = seed_set(tmp_path, [S] * 5)
        dirs[-1] = dirs[0]
    elif case == "commits differ":
        dirs = seed_set(tmp_path, [S] * 4)
        dirs.append(str(write_seed(tmp_path, "CONF-9", {x: S for x in SYSTEMS},
                                   commit="def456")))
    elif case == "seed set not pre-registered":
        dirs = seed_set(tmp_path, [S] * 4)
    elif case == "claim on a wrong quantity":
        dirs = seed_set(tmp_path, [S] * 5)
        claims = table("delta > 0")
    elif case == "unparsable claim":
        dirs = seed_set(tmp_path, [S] * 5)
        claims = table("ratio >> 1")
    elif case == "record label":
        dirs = seed_set(tmp_path, [S] * 5)
        contrib_path = Path(dirs[1]) / "contrib.json"
        contrib = json.loads(contrib_path.read_text())
        contrib["label"] = DEV_LABEL.format(seed_id="CONF-6")
        contrib_path.write_text(json.dumps(contrib))
    code, _, out = run(tmp_path, dirs, *flags, claims=claims)
    assert code == 64 and not out.exists()


# ------------------------------------------------------------ rehearsal
def test_rehearsal_reports_a_cache_mismatch_and_labels_development(
    tmp_path: Path,
) -> None:
    """Development seeds with ``--rehearsal``: exit 0, the cache mismatch of
    one seed reported (not refused), the rehearsal label, and the gate
    honored unless ``--ignore-gate``."""
    dirs = seed_set(tmp_path, [S] * 5, [True] * 3 + [False] * 2,
                    sealed=False)
    cache = Path(dirs[2]).parent / "phasej" / "cache" / "lyapunov.json"
    cache.write_bytes(b"{}")
    code, record, out = run(tmp_path, dirs, "--rehearsal")
    assert code == 0
    assert record["label"] == tool.REHEARSAL_LABEL
    assert [i["lyapunov_matches_pinned"] for i in record["inputs"]] == [
        True, True, False, True, True
    ]
    assert verdict_of(record)[0] == "not confirmable"
    code, record, _ = run(tmp_path, dirs, "--rehearsal", "--ignore-gate")
    assert code == 0 and verdict_of(record)[0] == "confirmed"
    assert record["ignore_gate"] is True


def test_rehearsal_on_two_seeds_runs(tmp_path: Path) -> None:
    """N = 2 (the dress rehearsal): exit 0, every row not confirmable."""
    dirs = seed_set(tmp_path, [S] * 2, sealed=False)
    code, record, _ = run(tmp_path, dirs, "--rehearsal")
    assert code == 0
    assert {r["verdict"] for r in record["rows"]} == {"not confirmable"}


# ---------------------------------------- source rows J-I1, J-C2 (seq 53)
# Reference: the reading tables of claims.json (ledger seq 53), copied below
# by hand. J-I1: substantial -> delta_r2 > 0; distinct but small -> 0 <
# delta_r2 < 0.05; reduces -> delta_r2 < 0.05; undetermined -> none. J-C2:
# above target (ci[0] > 0.10) -> false_trust > 0.10; below target (ci[1] <
# 0.10) -> false_trust < 0.10; not determined -> none.
I1_PATH = (
    "systems/{s}/ablation/profile_conditions/deployable/logit_w_interior/"
    "leave_one_out/I"
)
C2_PATH = "systems/rossler/C3/policies/g(F-hat) + h(F-hat)/false_trust_realized"
READING_TABLES = {
    "J-I1": {
        "words": {
            "substantial": ["delta_r2 > 0"],
            "distinct but small": ["delta_r2 > 0", "delta_r2 < 0.05"],
            "reduces": ["delta_r2 < 0.05"],
            "undetermined": [],
        }
    },
    "J-C2": {
        "words": {
            "above target": ["false_trust > 0.10"],
            "below target": ["false_trust < 0.10"],
            "not determined": [],
        }
    },
}


def test_source_claims_imply_and_contradict_by_hand() -> None:
    """The threshold claims of the two reading tables, pair by pair.

    By hand: "reduces" (delta_r2 < 0.05) is compatible with "substantial"
    (delta_r2 > 0) and does not imply delta_r2 > 0, so J-I1 is never
    contradicted; "distinct but small" implies delta_r2 > 0. "above target"
    and "below target" are disjoint; "not determined" claims nothing.
    """
    table = {"reading_tables": READING_TABLES}
    i1 = tool.word_claims(table, "J-I1")
    c2 = tool.word_claims(table, "J-C2")
    target = tool.parse_text("delta_r2 > 0")
    assert rep.implies(i1["substantial"], target)
    assert rep.implies(i1["distinct but small"], target)
    assert not rep.implies(i1["reduces"], target)
    assert not rep.implies(i1["undetermined"], target)
    for a in i1:
        for b in i1:
            assert not rep.contradict(i1[a], i1[b]), (a, b)
    above = tool.parse_text("false_trust > 0.10")
    assert rep.implies(c2["above target"], above)
    assert not rep.implies(c2["below target"], above)
    assert rep.contradict(c2["above target"], c2["below target"])
    assert not rep.contradict(c2["above target"], c2["not determined"])
    assert not rep.contradict(c2["below target"], c2["not determined"])


@pytest.mark.parametrize(
    ("ci", "word"),
    [
        ([0.11, 0.2], "above target"),
        ([0.05, 0.09], "below target"),
        ([0.09, 0.12], "not determined"),
        ([0.10, 0.2], "not determined"),  # strict: ci[0] > 0.10
        ([0.0, 0.10], "not determined"),  # strict: ci[1] < 0.10
        ([None, 0.2], "not determined"),
        ([None, 0.05], "below target"),
    ],
)
def test_j_c2_word_from_the_interval(ci: list, word: str) -> None:
    """Above if ci[0] > 0.10, below if ci[1] < 0.10, else not determined
    (``None``: a non-finite bound, never beyond the target)."""
    words = tool.word_claims({"reading_tables": READING_TABLES}, "J-C2")
    assert tool.read_ci_threshold({"ci": ci}, words) == word


def source_table() -> dict:
    out = table(systems=("lorenz63",))
    out["claims"] += [
        {
            "id": "J-I1",
            "tier": 3,
            "statement": "synthetic",
            "claim": "delta_r2 > 0",
            "rows": [
                {
                    "source": "pipeline results.json",
                    "system": "lorenz63",
                    "profile": "deployable",
                    "path": I1_PATH.format(s="lorenz63"),
                    "item": "drop I: Delta R^2",
                }
            ],
        },
        {
            "id": "J-C2",
            "tier": 3,
            "statement": "synthetic",
            "claim": "false_trust > 0.10",
            "rows": [
                {
                    "source": "ce.json",
                    "system": "rossler",
                    "profile": "deployable",
                    "path": C2_PATH,
                    "item": "C3 false trust",
                }
            ],
        },
    ]
    out["reading_tables"] = json.loads(json.dumps(READING_TABLES))
    return out


def source_seeds(
    root: Path, i1_words: list, c2_cis: list, gates: list | None = None
) -> list[str]:
    """Five sealed seeds with a J-I1 word (results.json) and a J-C2
    interval (ce.json); lorenz63's gate per seed from ``gates``."""
    dirs = seed_set(root, [S] * 5, gates)
    for d, word, ci in zip(dirs, i1_words, c2_cis):
        folder = Path(d)
        results_path = folder.parent / "phasej" / "results.json"
        results = json.loads(results_path.read_text())
        loo = {"leave_one_out": {"I": {"reading": word, "ci": [0.0, 0.1]}}}
        results["systems"]["lorenz63"]["ablation"] = {
            "profile_conditions": {"deployable": {"logit_w_interior": loo}}
        }
        results_path.write_text(json.dumps(results))
        ce = json.loads((folder / "ce.json").read_text())
        ce["systems"]["rossler"] = {
            "C2": {},
            "C3": {
                "policies": {
                    "g(F-hat) + h(F-hat)": {
                        "mse": {},
                        "false_trust_realized": {"estimate": 0.1, "ci": ci},
                    }
                },
                "horizon_models": {},
            },
            "E_H2a": {"reading": {"reading": "not determined (synthetic)"}},
            "E_H2e": {"levels": {}},
        }
        (folder / "ce.json").write_text(json.dumps(ce))
    return dirs


def by_claim(record: dict, claim_id: str) -> tuple[str, dict]:
    (row,) = [r for r in record["rows"] if r["claim_id"] == claim_id]
    (v,) = [v for v in record["verdicts"] if v["claim_id"] == claim_id]
    assert v["verdict"] == row["verdict"]
    return row["verdict"], row


ABOVE, BELOW, ND = [0.12, 0.14], [0.05, 0.08], [0.09, 0.12]


@pytest.mark.parametrize(
    ("i1_words", "c2_cis", "gates", "i1", "c2"),
    [
        pytest.param(["substantial"] * 5, [ABOVE] * 5, None,
                     "confirmed", "confirmed", id="all-imply"),
        pytest.param(["substantial"] * 4 + ["reduces"], [ABOVE] * 4 + [BELOW],
                     None, "confirmed", "contradicted",
                     id="reduces-never-contradicts-below-does"),
        pytest.param(["substantial"] * 3 + ["reduces"] * 2,
                     [ABOVE] * 3 + [ND] * 2, None,
                     "not confirmed", "not confirmed", id="3-of-5"),
        pytest.param(["distinct but small"] * 4 + ["undetermined"],
                     [ABOVE] * 5, [True] * 4 + [False],
                     "confirmed", "confirmed", id="absent-lorenz63-seed"),
        pytest.param(["substantial"] * 5, [ABOVE] * 5,
                     [True] * 3 + [False] * 2,
                     "not confirmable", "confirmed", id="two-absent"),
    ],
)
def test_source_rows_follow_the_rule(
    tmp_path: Path, i1_words, c2_cis, gates, i1, c2
) -> None:
    """Hand-computed verdicts of the J-I1 and J-C2 rows under the rule; the
    lorenz63 gate does not touch the rossler row."""
    dirs = source_seeds(tmp_path, i1_words, c2_cis, gates)
    code, record, out = run(tmp_path, dirs, claims=source_table())
    assert code == 0
    assert by_claim(record, "J-I1")[0] == i1
    verdict, row = by_claim(record, "J-C2")
    assert verdict == c2
    assert row["source"] == "ce.json" and row["path"] == C2_PATH
    assert "J-C2" in (out / "confirm.md").read_text()


def test_source_row_with_a_missing_path_is_an_error(tmp_path: Path) -> None:
    """A present seed without the J-I1 leaf: exit 64, nothing written."""
    dirs = source_seeds(tmp_path, ["substantial"] * 5, [ABOVE] * 5)
    results_path = Path(dirs[3]).parent / "phasej" / "results.json"
    results = json.loads(results_path.read_text())
    del results["systems"]["lorenz63"]["ablation"]
    results_path.write_text(json.dumps(results))
    code, _, out = run(tmp_path, dirs, claims=source_table())
    assert code == 64 and not out.exists()


def test_source_table_refusals(tmp_path: Path) -> None:
    """An unknown word, a table quantity unlike the claim's, a claim with no
    reader: exit 64, nothing written."""
    dirs = source_seeds(
        tmp_path / "a", ["substantial"] * 4 + ["large"], [ABOVE] * 5
    )
    code, _, out = run(tmp_path, dirs, claims=source_table())
    assert code == 64 and not out.exists()
    good = source_seeds(tmp_path / "b", ["substantial"] * 5, [ABOVE] * 5)
    bad = source_table()
    bad["reading_tables"]["J-C2"]["words"]["above target"] = ["x > 0.10"]
    assert run(tmp_path, good, claims=bad)[0] == 64
    bad = source_table()
    bad["claims"][1]["id"] = "J-Z9"
    bad["reading_tables"]["J-Z9"] = bad["reading_tables"]["J-I1"]
    assert run(tmp_path, good, claims=bad)[0] == 64
    assert not out.exists()


# ------------------------------------------- secondary v3 description (7a)
def test_v3_description_lists_words_per_seed_and_counts(
    tmp_path: Path,
) -> None:
    """A synthetic ``verdicts`` block: the word per seed and system, "gate
    failed" where lorenz63's gate failed, "(missing)" counted, the counts
    per word; no seed-level verdict, no combined word; the section 7a label
    (sealed) or the rehearsal label.

    Reference: the hand-written block and expected rows below.
    """
    dirs = seed_set(tmp_path, [S] * 5, [True, True, False, True, True])
    words = [
        ("pass", "fail"),
        ("pass", "pass"),
        ("pass", "pass"),
        ("inconclusive", "pass"),
        ("pass", None),
    ]
    for d, (lorenz, rossler) in zip(dirs, words):
        path = Path(d).parent / "phasej" / "results.json"
        results = json.loads(path.read_text())
        by_system = {"lorenz63": lorenz}
        if rossler is not None:
            by_system["rossler"] = rossler
        results["verdicts"] = {
            "H1a": {
                "by_system": by_system,
                "verdict": "supported",
                "missing_systems": [],
            }
        }
        path.write_text(json.dumps(results))
    code, _, out = run(tmp_path, dirs)
    assert code == 0
    v3 = json.loads((out / "v3.json").read_text())
    assert v3["label"] == tool.V3_LABEL == (
        "SECONDARY DESCRIPTION: v3 words of the sealed runs under the phase J "
        "configuration; not the v3 test; does not change, confirm or replace "
        "CONF-1"
    )
    assert v3["rows"] == [
        {
            "row": "H1a",
            "system": "lorenz63",
            "words": ["pass", "pass", "gate failed", "inconclusive", "pass"],
            "count": {"pass": 3, "gate failed": 1, "inconclusive": 1},
        },
        {
            "row": "H1a",
            "system": "rossler",
            "words": ["fail", "pass", "pass", "pass", "(missing)"],
            "count": {"fail": 1, "pass": 3, "(missing)": 1},
        },
    ]
    assert v3["n_missing"] == 1
    text = (out / "v3.md").read_text()
    assert "supported" not in text  # the seed-level verdict is not listed
    blocks = text.split("\n\n")
    tables = [i for i, b in enumerate(blocks) if b.lstrip().startswith("|")]
    assert tables and all(v3["label"] in blocks[i - 1] for i in tables)
    rehearsal = seed_set(tmp_path / "dev", [S] * 2, sealed=False)
    code, _, out = run(tmp_path / "dev", rehearsal, "--rehearsal")
    assert code == 0
    v3 = json.loads((out / "v3.json").read_text())
    assert v3["label"] == tool.REHEARSAL_LABEL and v3["rows"] == []
