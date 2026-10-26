"""Tests of ``tools/lpc_replicate.py``, the M-6 replication rule (WU-0051b).

* The contradiction table of every pair of reading words, per row type,
  against a hand-written truth table derived from each word's definition in
  the analysis code (``ablation.ratio_reading``, ``contribution.pair_rows``,
  ``joint_decisions.retained_reading``, ``retention_comparison``,
  ``c2_prediction``, ``mechanisms.h2a_reading``, ``h2e_part_reading``,
  ``h3c_reading``). For the ratio table a second, independent reference:
  each word written as a predicate of the true ratio, and two words
  compatible iff some ratio on a grid that straddles every threshold
  satisfies both.
* The 4-of-5 count with undetermined and absent seeds; claim-free words never
  count and never contradict.
* The claim-level fallback.
* The refusals (exit 64, nothing written) and the rule-mode run on five
  synthetic held-out records.

References: hand-written truth tables and fixtures. Tolerance: none (sets,
words, exit codes). The end-to-end run on three copies of a smoke output is
in ``tests/integration/test_contribution_dump.py``.
"""

from __future__ import annotations

import importlib.util
import itertools
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "tools" / "lpc_replicate.py"
_SPEC = importlib.util.spec_from_file_location("lpc_replicate", TOOL)
assert _SPEC is not None and _SPEC.loader is not None
tool = importlib.util.module_from_spec(_SPEC)
sys.modules["lpc_replicate"] = tool  # dataclasses resolve their module
_SPEC.loader.exec_module(tool)

NO_GAIN = "no interaction gain; the pair model fits worse"
NEEDED = "needed, size not determined"
HELD_OUT = ["DEV-5", "DEV-6", "DEV-7", "DEV-8", "DEV-9"]


def unordered(pairs) -> set[frozenset]:
    return {frozenset(p) for p in pairs}


def tool_table(claims: dict) -> set[frozenset]:
    """Pairs (unordered, distinct names) whose claims contradict."""
    return {
        frozenset((a, b))
        for a, b in itertools.combinations(claims, 2)
        if tool.contradict(claims[a], claims[b])
    }


def assert_self_compatible(claims: dict) -> None:
    for name, c in claims.items():
        assert not tool.contradict(c, c), name


# --------------------------------------------------------- claim algebra
def test_satisfiable_respects_open_and_closed_endpoints() -> None:
    """Hand cases: [1, 1] is a point; (1, 1] and [1, 1) are empty."""
    c = tool.Claim
    assert tool.satisfiable([c("x", ">=", 1.0), c("x", "<=", 1.0)])
    assert not tool.satisfiable([c("x", ">", 1.0), c("x", "<=", 1.0)])
    assert not tool.satisfiable([c("x", ">=", 1.0), c("x", "<", 1.0)])
    assert tool.satisfiable([c("x", ">", 1.0), c("y", "<", 0.0)])
    assert tool.implies([c("x", "<", 1.0)], c("x", "<=", 1.05))
    assert not tool.implies([c("x", "<=", 1.05)], c("x", "<", 1.0))
    assert not tool.implies([], c("x", ">", 0.0))


# ------------------------------------------------------------ ratio rows
RATIO_WORDS = (
    "lowers",
    "negligible",
    "small",
    "substantial",
    NEEDED,
    "undetermined",
    "not identifiable",
    NO_GAIN,
)
RATIO_CONTRADICTIONS = unordered(
    [
        ("lowers", "small"),
        ("lowers", "substantial"),
        ("lowers", NEEDED),
        ("negligible", "substantial"),
        ("small", "substantial"),
        (NO_GAIN, "small"),
        (NO_GAIN, "substantial"),
        (NO_GAIN, NEEDED),
    ]
)
"""Hand-written: lowers = ratio < 1, negligible = ratio <= 1.05, small = 1 <
ratio <= 1.05, substantial = ratio > 1.05, needed = ratio > 1, the fits-worse
words on a loss-ratio row = ratio < 1; undetermined and not identifiable
claim nothing."""
RATIO_PREDICATES = {
    "lowers": lambda t: t < 1.0,
    "negligible": lambda t: t <= 1.05,
    "small": lambda t: 1.0 < t <= 1.05,
    "substantial": lambda t: t > 1.05,
    NEEDED: lambda t: t > 1.0,
    "undetermined": lambda t: True,
    "not identifiable": lambda t: True,
    NO_GAIN: lambda t: t < 1.0,
}
GRID = (0.5, 1.0 - 1e-9, 1.0, 1.0 + 1e-9, 1.02, 1.05, 1.05 + 1e-9, 2.0)


def test_ratio_contradiction_table_matches_hand_and_brute_force() -> None:
    """Every pair of the 1.05 table's words (and the B fits-worse alias)."""
    claims = {w: tool.ratio_claims(w, "p") for w in RATIO_WORDS}
    brute = {
        frozenset((a, b))
        for a, b in itertools.combinations(RATIO_WORDS, 2)
        if not any(
            RATIO_PREDICATES[a](t) and RATIO_PREDICATES[b](t) for t in GRID
        )
    }
    assert brute == RATIO_CONTRADICTIONS
    assert tool_table(claims) == RATIO_CONTRADICTIONS
    assert_self_compatible(claims)
    assert claims["undetermined"] == claims["not identifiable"] == ()
    with pytest.raises(tool.Refusal):
        tool.ratio_claims("pass", "p")


def test_pair_retained_and_difference_tables() -> None:
    """B pair, C2 retained, C2 oracle-vs-deployable: one clash each."""
    pair = dict(tool.PAIR)
    assert tool_table(pair) == unordered(
        [("interaction gain detected", NO_GAIN)]
    )
    assert pair["no interaction gain detected"] == ()
    retained_words = (
        "keeps most",
        "loses most",
        "not determined (interval spans 0.5)",
        "not determined (n_eff < 50)",
        "not determined (full-profile skill not established)",
        "not determined (failed resamples)",
    )
    retained = {
        w: tool.table_claims(tool.RETAINED, w, "p") for w in retained_words
    }
    assert tool_table(retained) == unordered([("keeps most", "loses most")])
    assert all(retained[w] == () for w in retained_words[2:])
    difference_words = (
        "deployable retains less",
        "deployable retains more",
        "no difference detected",
        "not determined (n_eff < 50)",
        "not determined (full-profile skill not established)",
    )
    difference = {
        w: tool.table_claims(tool.RETAINED_DIFFERENCE, w, "p")
        for w in difference_words
    }
    assert tool_table(difference) == unordered(
        [("deployable retains less", "deployable retains more")]
    )
    for table in (pair, retained, difference):
        assert_self_compatible(table)
    with pytest.raises(tool.Refusal):
        tool.table_claims(tool.RETAINED, "keeps some", "p")


def test_dependence_bias_words_take_their_sign_from_the_interval() -> None:
    """(f2): only detectable-above against detectable-below clash."""
    detected = "dependence bias detectable (interval excludes 0)"
    rows = {
        "above": {"reading": detected, "dependence": {"ci": [0.1, 0.2]}},
        "below": {"reading": detected, "dependence": {"ci": [-0.2, -0.1]}},
        "none": {"reading": "no detectable dependence bias"},
        "outlier": {
            "reading": "realized-noise outlier, no detectable dependence bias"
        },
    }
    claims = {k: tool.bias_claims(r, "p") for k, r in rows.items()}
    assert tool_table(claims) == unordered([("above", "below")])
    with pytest.raises(tool.Refusal):
        tool.bias_claims(
            {"reading": detected, "dependence": {"ci": [-0.1, 0.1]}}, "p"
        )


def h2e_part(word: str, median: list, spearman: list) -> dict:
    return {
        "reading": word,
        "median_delta_corr": {"ci": median},
        "spearman_delta_corr_delta_R": {"ci": spearman},
    }


def test_e_h2e_and_e_h2a_tables() -> None:
    """E-H2e words clash; E-H2a's consistent and not consistent do not.

    E-H2a "consistent" claims a non-zero Spearman(m, I) at a supporting
    horizon, "not consistent" claims |Spearman| < 0.1 at every usable one:
    both hold for a Spearman in (0, 0.1), so they cannot contradict.
    """
    parts = {
        "consistent": h2e_part("consistent", [0.1, 0.3], [-0.3, -0.1]),
        "nc spearman": h2e_part("not consistent", [-0.1, 0.3], [0.1, 0.3]),
        "nc median": h2e_part("not consistent", [-0.3, -0.1], [-0.1, 0.1]),
        "nd": h2e_part("not determined", [-0.1, 0.3], [-0.3, 0.1]),
    }
    claims = {k: tool.h2e_part_claims(p, "p") for k, p in parts.items()}
    assert tool_table(claims) == unordered(
        [("consistent", "nc spearman"), ("consistent", "nc median")]
    )

    def h2a(word: str, ci60: list, supporting: list) -> dict:
        return {
            "reading": {
                "reading": word,
                "horizons_used": ["60", "120"],
                "horizons_supporting": supporting,
            },
            "by_horizon": {
                "60": {"spearman_m_I": {"ci": ci60}},
                "120": {"spearman_m_I": {"ci": [-0.05, 0.05]}},
            },
        }

    blocks = {
        "consistent +": h2a("consistent", [0.02, 0.3], ["60"]),
        "consistent -": h2a("consistent", [-0.3, -0.02], ["60"]),
        "not consistent": h2a("not consistent", [-0.05, 0.08], []),
        "nd": h2a("not determined (fewer than 50 kept states)", [0, 0], []),
    }
    claims = {k: tool.h2a_claims(b, "p") for k, b in blocks.items()}
    assert tool_table(claims) == unordered([("consistent +", "consistent -")])


def h3c(word: str, lorenz: str, rossler: str, share: float, pct: float,
        bc: dict) -> dict:
    return {
        "reading": word,
        "lorenz63_part": lorenz,
        "rossler_part": rossler,
        "lorenz63_tail_share": share,
        "lorenz63_top_median_I_percentile": pct,
        "rossler_bimodality": bc,
    }


def test_e_h3c_and_c2_prediction_tables() -> None:
    """E-H3c consistent clashes with either not-consistent part; the C2
    prediction clashes only where the two seeds read the same component."""
    low = {"R": 0.4, "O": 0.4, "I": 0.4, "N": 0.4}
    high = {"R": 0.7, "O": 0.7, "I": 0.4, "N": 0.4}
    recs = {
        "consistent": h3c("consistent", "consistent", "consistent", 0.2, 0.8,
                          low),
        "nc lorenz": h3c("not consistent", "not consistent", "consistent",
                         0.02, 0.8, low),
        "nc rossler": h3c("not consistent", "not determined",
                          "not consistent", 0.07, 0.6, high),
        "nd": h3c("not determined (pattern not reproduced)", "consistent",
                  "consistent", 0.2, 0.8, low),
    }
    claims = {k: tool.h3c_claims(r) for k, r in recs.items()}
    assert tool_table(claims) == unordered(
        [("consistent", "nc lorenz"), ("consistent", "nc rossler")]
    )

    def c2(word: str, forward: str, reverse: dict) -> dict:
        return {
            "prediction_check": {"reading": word},
            "forward": {"retained": {"reading": forward}},
            "reverse": {
                h: {"retained": {"reading": w}} for h, w in reverse.items()
            },
        }

    nd = "not determined (interval spans 0.5)"
    blocks = {
        "consistent": c2("consistent", "loses most",
                         {"8": "loses most", "30": nd}),
        "nc reverse 30": c2("not consistent", "loses most",
                            {"8": nd, "30": "keeps most"}),
        "nc forward": c2("not consistent", "keeps most", {"8": nd, "30": nd}),
        "nd": c2("not determined", nd, {"8": nd, "30": nd}),
    }
    claims = {k: tool.prediction_claims(b, "p") for k, b in blocks.items()}
    assert tool_table(claims) == unordered([("consistent", "nc forward")])


# ------------------------------------------------------------- counting
def reading(word: str, table: dict | None = None) -> object:
    claims = (table or tool.RATIO)[word]
    return tool.Reading(word, claims, "p")


def classify(words: list, minimum: int = 4) -> dict:
    return tool.classify(
        [None if w is None else reading(w) for w in words], minimum
    )


def test_four_of_five_with_undetermined_and_absent_seeds() -> None:
    """Hand cases of M-6: claim-free words never count toward the 4."""
    u = "undetermined"
    out = classify(["small"] * 4 + [u])
    assert out["class"] == "replicated" and out["replicated_reading"] == "small"
    assert out["n_claim_free"] == 1
    out = classify(["small"] * 3 + [u, u])
    assert out["class"] == "not replicated" and out["replicated_claims"] == []
    out = classify([u] * 4 + ["small"])
    assert out["class"] == "not replicated"
    assert out["modal_claim_word"] == "small" and out["modal_count"] == 1
    out = classify([u] * 5)
    assert out["class"] == "not replicated" and out["n_claim_free"] == 5
    assert out["modal_claim_word"] is None
    out = classify(["small"] * 4 + [None])
    assert out["class"] == "replicated" and out["n_absent"] == 1
    out = classify(["small"] * 3 + [None, u])
    assert out["class"] == "not replicated" and out["n_absent"] == 1
    out = classify(["small"] * 4 + [NEEDED])
    assert out["class"] == "replicated"
    out = classify(["negligible"] * 4 + ["substantial"])
    assert out["class"] == "contradicted"
    assert out["contradicting_pairs"] == [
        [i, "negligible", 4, "substantial"] for i in range(4)
    ]
    out = classify(["lowers"] * 4 + [u])
    assert out["class"] == "replicated"
    none = "no interaction gain detected"
    out = tool.classify([reading(none, tool.PAIR)] * 5, 4)
    assert out["class"] == "not replicated" and out["n_claim_free"] == 5


def test_claim_level_fallback() -> None:
    """Weaker claims implied on at least 4 seeds and contradicted by none."""
    out = classify(["small", "small", "small", NEEDED, "undetermined"])
    assert out["class"] == "not replicated"
    assert out["replicated_claims"] == ["ratio > 1"]
    out = classify(["substantial"] * 3 + [NEEDED] * 2)
    assert out["class"] == "not replicated"
    assert out["replicated_claims"] == ["ratio > 1"]
    out = classify(["small", "small", "negligible", "negligible", "lowers"])
    assert out["class"] == "contradicted"
    assert out["replicated_claims"] == ["ratio <= 1.05"]
    out = classify(["substantial", "substantial", NEEDED, NEEDED, "small"])
    assert out["class"] == "contradicted"
    assert out["replicated_claims"] == ["ratio > 1"]
    # Two passing claims on one quantity: the stronger one is reported.
    out = classify(["lowers", "lowers", NO_GAIN, NO_GAIN, "negligible"])
    assert out["class"] == "not replicated"
    assert out["replicated_claims"] == ["ratio < 1"]
    out = classify(["negligible", "negligible", "small", NEEDED, NEEDED])
    assert out["class"] == "not replicated"
    assert out["replicated_claims"] == []


# ------------------------------------------------------------- refusals
def contrib_system(word: str) -> dict:
    return {
        "allocation": {
            "30": {
                "oracle": {
                    "horizon": "H=30 (1.00 LT)",
                    "drop_one": {"I": {"mse_ratio": {"reading": word}}},
                    "subsets": {},
                    "ladder": {"vs_full": {}, "vs_below": {}},
                }
            }
        },
        "interactions": {},
        "horizon": {},
    }


def write_seed(
    path: Path,
    seed: str,
    word: str = "small",
    commit: str = "abc123",
    dirty: bool = False,
    ce_commit: str | None = None,
) -> Path:
    path.mkdir(parents=True)
    run = {"seed_id": seed, "dir": f"/runs/{seed}", "commit": "r1",
           "preset": "phasej"}
    contrib = {
        "label": "DEVELOPMENT",
        "run": run,
        "analysis": {"commit": commit, "dirty": dirty},
        "systems": {"lorenz63": contrib_system(word)},
    }
    ce = {
        "run": dict(run),
        "analysis": {"commit": ce_commit or commit, "dirty": dirty},
        "abd": {"path": "contrib.json", "commit": commit},
        "systems": {},
    }
    (path / "contrib.json").write_text(json.dumps(contrib))
    (path / "ce.json").write_text(json.dumps(ce))
    return path


def five(tmp_path: Path, words=("small",) * 5, **kw) -> list[str]:
    return [
        str(write_seed(tmp_path / s, s, w, **kw))
        for s, w in zip(HELD_OUT, words)
    ]


def test_rule_mode_on_five_held_out_records(tmp_path: Path) -> None:
    """Exit 0; the rule's label, before every table; the row replicated."""
    dirs = five(tmp_path, ("small",) * 4 + ("undetermined",))
    out = tmp_path / "out"
    assert tool.main([*dirs, "--out", str(out)]) == 0
    record = json.loads((out / "replication.json").read_text())
    assert record["label"] == tool.LABEL
    assert record["mode"] == "rule" and record["minimum"] == 4
    (row,) = record["rows"]
    assert row["class"] == "replicated" and row["replicated_reading"] == "small"
    assert row["family"] == "A drop-one" and row["system"] == "lorenz63"
    blocks = (out / "replication.md").read_text().split("\n\n")
    tables = [i for i, b in enumerate(blocks) if b.lstrip().startswith("|")]
    assert tables
    for i in tables:
        assert tool.LABEL in blocks[i - 1], blocks[i][:80]


@pytest.mark.parametrize(
    "case",
    [
        "n4",
        "not held out",
        "commits differ",
        "ce commit differs",
        "dirty",
        "forbidden text",
        "unknown word",
        "uncovered leaf",
        "foreign ce",
    ],
)
def test_refusals_write_nothing(tmp_path: Path, case: str) -> None:
    """Each refusal: exit 64 and no output folder."""
    if case == "n4":
        dirs = five(tmp_path)[:4]
    elif case == "not held out":
        dirs = [str(write_seed(tmp_path / s, s)) for s in
                ("DEV-1", "DEV-3", "DEV-4", "DEV-5", "DEV-6")]
    elif case == "commits differ":
        dirs = five(tmp_path)
        write_seed(tmp_path / "x", "DEV-9", commit="def456")
        dirs[-1] = str(tmp_path / "x")
    elif case == "ce commit differs":
        dirs = five(tmp_path, ce_commit="def456")
    elif case == "dirty":
        dirs = five(tmp_path, dirty=True)
    else:
        dirs = five(tmp_path)
        last = Path(dirs[-1])
        contrib = json.loads((last / "contrib.json").read_text())
        ce = json.loads((last / "ce.json").read_text())
        if case == "forbidden text":
            contrib["label"] = "CONF-1 beside it"
        elif case == "unknown word":
            contrib["systems"]["lorenz63"] = contrib_system("pass")
        elif case == "uncovered leaf":
            contrib["systems"]["lorenz63"]["extra"] = {"reading": "small"}
        elif case == "foreign ce":
            ce["run"]["seed_id"] = "DEV-5"
        (last / "contrib.json").write_text(json.dumps(contrib))
        (last / "ce.json").write_text(json.dumps(ce))
    out = tmp_path / "out"
    assert tool.main([*dirs, "--out", str(out)]) == 64
    assert not out.exists()


def test_exploratory_admits_other_n_and_labels_it(tmp_path: Path) -> None:
    """N = 3 with repeats runs only with --exploratory; minimum ceil(12/5)."""
    one = write_seed(tmp_path / "a", "DEV-1", dirty=True)
    dirs = [str(one)] * 3
    out = tmp_path / "out"
    assert tool.main([*dirs, "--out", str(out)]) == 64
    assert tool.main([*dirs, "--out", str(out), "--exploratory"]) == 0
    record = json.loads((out / "replication.json").read_text())
    assert record["mode"] == "exploratory" and record["minimum"] == 3
    assert record["n_repeated_seeds"] == 2
    assert "not the M-6 rule" in record["label"]
    assert record["label"] != tool.LABEL


def test_cli_refuses_forbidden_words_in_arguments(tmp_path: Path) -> None:
    """Either word anywhere in the arguments: exit 64.

    The test's name avoids both words: ``tmp_path`` contains it.
    """
    assert not tool.FORBIDDEN.search(str(tmp_path))
    for bad in ("confirmatory", "CONF-1"):
        done = subprocess.run(
            [sys.executable, "-I", str(TOOL), str(tmp_path), "--out",
             str(tmp_path / bad)],
            capture_output=True,
            timeout=60,
        )
        assert done.returncode == 64, done.stderr
        assert not (tmp_path / bad).exists()
