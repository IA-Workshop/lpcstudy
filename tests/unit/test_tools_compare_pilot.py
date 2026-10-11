"""Tests of ``tools/compare_pilot.py``, the DEV-0 against v1 pilot comparison (WU-0002.12, step 1).

References (none of them is the tool's own output):

* T1: the correction table of ``docs/study/decision_log_lpc.md`` ("v1 / code" to "v3"), typed here,
  and ``lpcstudy.identifiers.V1_KEY_MAP`` (a consistency guard; the tool itself does not import it).
* T2: v3 paths written by hand for a hand-built v1 tree.
* T3 to T7: small synthetic trees whose outcomes are decided by hand (IEEE byte equality; the
  ROADMAP switch rule with 1e-12 relative; the closed bound of the proposed fallback criterion;
  the exit codes of the tool's own docstring).
* T8: ``git show v1-baseline:lpcstudy/analysis.py``: ``PRIMARY_LEVEL = 1 - 0.05/3`` at the
  ``_boot`` calls of lines 369/370 (H2a ``range_ci``), 378 (H2a ``partial_ci``), 435/436
  (H2b ``noise.ci``) and 448/449 (H2b ``library.<rho>.ci``; the plan's list omits this one), every
  other interval at the default 0.95; ``ex.block_bootstrap`` for ``Lambda_fin`` (0.95).
* T9: the file ``docs/study/pilot_results_v1.json`` (11 540 leaves, counted by the plan).
* T10: the AST of the tool.

Tolerance: none. The logic is discrete (paths, classes, byte equality, exit codes), so every
comparison is exact, except one relative difference printed by the report (justified where it is
used). Each test runs in well under 5 s; T9 classifies 11 540 leaves in about 0.6 s.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import math
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools" / "compare_pilot.py"
PILOT = ROOT / "docs" / "study" / "pilot_results_v1.json"

_SPEC = importlib.util.spec_from_file_location("compare_pilot", TOOL)
assert _SPEC is not None and _SPEC.loader is not None
cp = importlib.util.module_from_spec(_SPEC)
sys.modules["compare_pilot"] = cp
_SPEC.loader.exec_module(cp)

PRIMARY = 1.0 - 0.05 / 3.0


def p(text: str) -> tuple[str, ...]:
    """A path from its ``/``-joined text."""
    return tuple(text.split("/"))


def sides(old: dict, new: dict):
    """Flatten and compare two small trees with the real rule table."""
    old_leaves, new_leaves, _ = cp.load_sides(old, new)
    return old_leaves, new_leaves, cp.compare_leaves(old_leaves, new_leaves)


def by_path(results: list) -> dict:
    """Results keyed by the ``/``-joined path."""
    return {cp.show(r.path): r for r in results}


# ---------------------------------------------------------------------------------- T1
EXPECTED_V1_TO_V3 = {  # decision_log_lpc.md, "Correction (2026-10-10, later; Claude)", typed by hand
    "H1a": "V7", "H1b": "H1a", "H1c": "H1b", "H1d": "H1c", "H1e": "H1d", "H1f": "Q-N",
    "H2a": "H2a", "H2b": "H2b", "H2c": "H2c", "H2d": "H2d", "H2e": "gain_bound",
    "H3a": "H3a", "H3b": None, "H3c": "H3b", "H3d": "H3c", "T1": None,
}


def test_t1_correction_table_is_the_decision_log_table() -> None:
    """T1: ``V1_TO_V3`` is the hand-typed table, and equals ``identifiers.V1_KEY_MAP``."""
    assert cp.V1_TO_V3 == EXPECTED_V1_TO_V3
    from lpcstudy.identifiers import V1_KEY_MAP

    assert cp.V1_TO_V3 == V1_KEY_MAP


# ---------------------------------------------------------------------------------- T2
V1_TREE = {
    "systems": {"lorenz63": {
        "H1a": {"median_slope": 1.0},
        "H1b": {"by_noise": {"0.01": {"mean_seed_by_N": {"1000": 0.5}}}},
        "H1c": {"CP": {"slope": 1.0}},
        "H1d": {"pass": True},
        "H1e": {"spearman": {"noise_sensitivity": 0.8, "growth": 0.9,
                             "estimation_seed_vs_cramer_rao": 0.7}},
        "H1f": {"margin": 0.01},
        "H2e": {"max_gain_lyapunov": 2.0},
        "H3a": {"logrank_holm_p": [0.1], "mean_iqr_lyapunov": 1.0, "chosen_K": 5},
        "H3b": {"p_eff": 2.0, "realized_K": {"2": 2}, "regret_ratio_by_K": {"2": 1.5},
                "loglog_slope": 0.3},
        "H3c": {"pass": True},
        "H3d": {"A5_over_A4_mse": 0.2},
        "H2b": {"library": {"0.01": {"median_w_by_N": {"1000": 0.1},
                                     "median_at_largest_N": 0.9}}},
        "shift": {"core_ratio": {"A2": 1.0}},
        "scores": {"A4f": {"mse_href": 1.0}},
        "seconds": 3.0}},
    "robustness": {"lorenz63": {"base": {"H1c": {"CP": {"slope": 1.0}}, "mse_href": {"A4f": 1.0}},
                                "delay/2": {"chosen_K": 5}}},
    "verdicts": {"H1a": {"verdict": "x"}, "H3b": {"verdict": "y"}, "H3c": {"verdict": "z"},
                 "T1": {"verdict": "w"}},
    "transfer": {"pass": True},
    "estimators": {"('lorenz63', 7, 5, 0.01)": {"seconds": 1.0}},
    "seconds": 5.0,
}
# Every v1 leaf of V1_TREE, mapped by hand (decision-log table; WU-0002.2 renames; the moved leaves
# of the WU-0002.4/.5/.7/.8 smoke comparisons). Removed features keep their path; dropped v1 results
# get the prefix ``v1:``.
EXPECTED_V3_PATHS = {
    "systems/lorenz63/V7/median_slope",
    "systems/lorenz63/H1a/by_noise/0.01/mean_seed_by_n_lib/1000",
    "systems/lorenz63/H1b/CP/slope",
    "systems/lorenz63/H1c/pass",
    "systems/lorenz63/H1d/rows/nhat/spearman",
    "systems/lorenz63/H1d/rows/growth/spearman",
    "systems/lorenz63/H1d/estimation_seed_vs_cramer_rao",
    "systems/lorenz63/Q-N/margin",
    "systems/lorenz63/gain_bound/max_gain_lyapunov",
    "systems/lorenz63/H3a/logrank_p_holm/[0]",
    "systems/lorenz63/H3a/iqr_lt_mean",
    "systems/lorenz63/H3a/chosen_K",
    "systems/lorenz63/v1:H3b/p_eff",
    "systems/lorenz63/regime_curve/realized_K/2",
    "systems/lorenz63/regime_curve/regret_ratio_by_K/2",
    "systems/lorenz63/v1:H3b/loglog_slope",
    "systems/lorenz63/H3b/pass",
    "systems/lorenz63/H3c/A5_over_A4_mse",
    "systems/lorenz63/H2b/library/0.01/median_w_by_n_lib/1000",
    "systems/lorenz63/H2b/library/0.01/median_at_largest_n_lib",
    "systems/lorenz63/shift/core_ratio/A2",
    "systems/lorenz63/scores/A4f/mse_href",
    "systems/lorenz63/seconds",
    "robustness/lorenz63/base/H1b/CP/slope",
    "robustness/lorenz63/base/mse_href/A4f",
    "robustness/lorenz63/delay%2F2/chosen_K",
    "verdicts/V7/verdict",
    "verdicts/v1:H3b/verdict",
    "verdicts/H3b/verdict",
    "verdicts/v1:T1/verdict",
    "transfer/pass",
    "estimators/('lorenz63', 7, 5, 0.01)/seconds",
    "seconds",
}


def test_t2_path_transform_of_every_kind() -> None:
    """T2: one v1 leaf of every transform kind maps to the hand-typed v3 path."""
    leaves = cp.flatten(V1_TREE)
    assert len(leaves) == len(EXPECTED_V3_PATHS)
    moved = {"/".join(cp.transform_v1(path)) for path in leaves}
    assert moved == EXPECTED_V3_PATHS


def test_t2_key_with_slash_is_escaped_and_values_survive() -> None:
    """The v1 key ``delay/2`` is one segment ``delay%2F2``; the value moves with its leaf."""
    leaves = cp.flatten({"robustness": {"lorenz63": {"delay/2": {"chosen_K": 5}}}})
    assert leaves == {p("robustness/lorenz63/delay%2F2/chosen_K"): 5}
    assert cp.transform_v1(p("systems/rossler/H1e/spearman/noise_sensitivity")) == \
        p("systems/rossler/H1d/rows/nhat/spearman")


def test_flatten_makes_empty_containers_visible_leaves() -> None:
    """An empty list is the leaf ``x/[]`` and an empty dict the leaf ``x/<empty>``."""
    leaves = cp.flatten({"a": [], "b": {}, "c": [1, [2]], "d": {"e": None}})
    assert leaves == {p("a/[]"): [], p("b/<empty>"): {}, p("c/[0]"): 1, p("c/[1]/[0]"): 2,
                      p("d/e"): None}


# ---------------------------------------------------------------------------------- T3
def test_t3_unmatched_leaf_names_the_path() -> None:
    """T3: a leaf with no rule raises ``Unclassified`` naming its path."""
    old = {"systems": {"lorenz63": {"mystery": 1.0}}}
    with pytest.raises(cp.Unclassified) as info:
        sides(old, {})
    assert "no rule matches systems/lorenz63/mystery" in str(info.value)


def test_t3_two_matching_rules_are_an_error() -> None:
    """T3: a leaf under two rules is an error that names both rules."""
    table = cp.Table([cp.Rule("a/b", "new"), cp.Rule("a/*", "new")])
    assert sorted(r.pattern for r in table.matches(p("a/b"))) == ["a/*", "a/b"]
    with pytest.raises(cp.Unclassified) as info:
        cp.compare_leaves({}, {p("a/b"): 1}, table)
    assert "2 rules match a/b" in str(info.value)
    assert "a/*" in str(info.value) and "a/b" in str(info.value)


@pytest.mark.parametrize("rule, message", [
    (cp.Rule("x/y", "bogus"), "unknown class"),
    (cp.Rule("*/y", "new"), "first segment must be literal"),
    (cp.Rule("x/y", "unchanged", rel_tol=1e-12), "rel_tol"),
    (cp.Rule("x/y", "changed", reason="r"), "needs a sub-task"),
    (cp.Rule("x/y", "unchanged", direction="zero"), "bad direction"),
    (cp.Rule("x/y", "new", when=(("a",), 1)), "'when'"),
])
def test_t3_bad_rules_are_load_errors(rule, message) -> None:
    """A malformed rule raises ``ToolError`` when the table is built."""
    with pytest.raises(cp.ToolError, match=re.escape(message)):
        cp.Table([rule])


def test_t3_duplicate_pattern_is_a_load_error() -> None:
    """The same pattern twice is a load error."""
    with pytest.raises(cp.ToolError, match="listed twice"):
        cp.Table([cp.Rule("x/y", "new"), cp.Rule("x/y", "removed")])


def test_rel_tol_needs_a_cited_summation_order() -> None:
    """A positive ``rel_tol`` loads only with a citation, and compares within it (plan, Scope)."""
    table = cp.Table([cp.Rule("x/y", "unchanged", rel_tol=1e-12, rel_tol_ref="WU-0000 log")])
    res = cp.compare_leaves({p("x/y"): 1.0}, {p("x/y"): 1.0 + 5e-13}, table)
    assert res[0].status == "within_tol"


def test_glob_semantics() -> None:
    """Segments: literal, ``*``, escaped star, ``[]`` (a list index or empty list), ``re:``, ``**``."""
    table = cp.Table([
        cp.Rule("g/A\\*", "new"), cp.Rule("g/x*y", "new"), cp.Rule("l/[]", "new"),
        cp.Rule("r/re:(a|b)+", "new"), cp.Rule("t/**", "new")])
    ok = {"g/A*": 1, "g/xzzy": 1, "g/xy": 1, "l/[3]": 1, "l/[]": 1, "r/abba": 1, "t/u": 1,
          "t/u/v": 1}
    for text in ok:
        assert len(table.matches(p(text))) == 1, text
    for text in ("g/A0", "g/x", "l/3", "l/[x]", "r/abc", "t", "q/u"):
        assert table.matches(p(text)) == [], text


# ---------------------------------------------------------------------------------- T4
@pytest.mark.parametrize("old, new, rel_tol, outcome", [
    (0.0, -0.0, 0.0, "differs"),                       # IEEE bytes differ
    (math.nan, math.nan, 0.0, "equal_nan"),            # NaN equals NaN (counted)
    (1.0, math.nextafter(1.0, 2.0), 0.0, "differs"),   # one ulp, relative 2.2e-16
    (1.0, math.nextafter(1.0, 2.0), 1e-12, "within_tol"),
    (1.0, 1.0 + 5e-13, 1e-12, "within_tol"),
    (1.0, 1.0 + 2e-12, 1e-12, "differs"),
    (1, 1.0, 0.0, "type"),
    (True, 1, 0.0, "type"),
    (1.0, 1.0, 0.0, "equal"),
    (0.1 + 0.2, 0.30000000000000004, 0.0, "equal"),    # same bytes
    (math.inf, math.inf, 0.0, "equal"),
    (math.inf, -math.inf, 1e-12, "differs"),           # no tolerance for non-finite values
    (0.0, 1e-300, 1e-12, "differs"),                   # relative to the larger magnitude
    ("a", "a", 0.0, "equal"),
    ("a", "b", 0.0, "differs"),
    (None, None, 0.0, "equal"),
    (True, False, 0.0, "differs"),
    (5, 6, 0.0, "differs"),
])
def test_t4_values_equal(old, new, rel_tol, outcome) -> None:
    """T4: byte-exact float comparison, exact types, and the relative tolerance of a rule."""
    assert cp.values_equal(old, new, rel_tol) == outcome


def test_t4_statuses_of_equal_nan_and_timing() -> None:
    """NaN against NaN is a status of its own (``equal_nan``), so that the report can count it."""
    res = cp.compare_leaves({p("seconds"): 1.0, p("config/name"): "pilot"},
                            {p("seconds"): 2.0, p("config/name"): "pilot"})
    assert {r.status for r in res} == {"timing", "equal"}
    nan = cp.compare_leaves({p("systems/lorenz63/V7/median_slope"): math.nan},
                            {p("systems/lorenz63/V7/median_slope"): math.nan})
    assert [r.status for r in nan] == ["equal_nan"]


# ---------------------------------------------------------------------------------- fixtures
GATE = {"V1": True, "V2": True, "V4": True, "V5": True, "V6": True, "gate_pass": True}
CONTEXT = {"delay": 5, "lambda_max": 0.9056, "interval": 0.0333}


def old_tree() -> dict:
    """A small v1-named tree: one system, one leaf of each group."""
    return {
        "config": {"name": "pilot", "regime_max_primary": 5},
        "systems": {"lorenz63": {
            "context": dict(CONTEXT),
            "validation": {"gate": dict(GATE)},
            "scores": {"A0": {"regret": {"1LT": 0.0354}, "mse": {"1LT": 0.25}},
                       "A*": {"regret": {"1LT": 0.01}}},
            "H1c": {"CP": {"slope": 1.0, "ci": [0.5, 1.5], "pass": True}, "pass": True},
            "H3b": {"p_eff": 2.0, "realized_K": {"2": 2}},
            "shift": {"core_ratio": {"A2": 1.0, "A3": 2.0}},
            "seconds": 10.0}},
        "verdicts": {"T1": {"verdict": "x", "by_system": {"lorenz63": True}}},
        "seconds": 20.0}


def new_tree() -> dict:
    """The matching v3-named tree (a clean run: the gate passes, P2(c) has no violation)."""
    gate = {**GATE, "V7": True}
    return {
        "config": {"name": "pilot", "regime_max_primary": 8, "seed_id": "DEV-0"},
        "systems": {"lorenz63": {
            "context": dict(CONTEXT),
            "validation": {"gate": gate},
            "scores": {"A0": {"regret": {"1LT": 0.0364}, "mse": {"1LT": 0.25}},
                       "A*": {"regret": {"1LT": 0.0}}},
            "H1b": {"CP": {"slope": 1.0, "ci": [0.5, 1.5]}, "pass": False, "verdict": "fail"},
            "regime_curve": {"realized_K": {"2": 2}},
            "verification": {"P2c": {"n_violations": 0, "n_chain_violations": {
                "A_le_B": 0, "N_le_A": 0, "consistency": 0, "p2a": 0, "triangle": 0}}},
            "handling": {"schema": 1},
            "seconds": 25.0}},
        "provenance": {"commit": "abc1234", "dirty": False,
                       "env": {"LPC_THREADS": "8", "NPROC": "8"}},
        "seconds": 30.0}


def write_pair(tmp_path: Path, old: dict, new: dict) -> tuple[Path, Path]:
    """Write the two trees as JSON files."""
    old_path, new_path = tmp_path / "old.json", tmp_path / "new.json"
    old_path.write_text(json.dumps(old))
    new_path.write_text(json.dumps(new))
    return old_path, new_path


def run_cli(tmp_path: Path, old: dict, new: dict) -> tuple[subprocess.CompletedProcess, Path, Path]:
    """Run the tool as a subprocess (``python -I``); returns the process, report and leaves paths."""
    old_path, new_path = write_pair(tmp_path, old, new)
    report, leaves = tmp_path / "report.md", tmp_path / "leaves.json"
    done = subprocess.run(
        [sys.executable, "-I", str(TOOL), str(new_path), "--old", str(old_path), "--report",
         str(report), "--leaves-json", str(leaves), "--run-dir", "RUN-DIR", "--manifest-row",
         "Pilot v1 (test row)"],
        capture_output=True, text=True, timeout=60, check=False)
    return done, report, leaves


# ---------------------------------------------------------------------------------- exit codes
def test_cli_clean_run_exits_zero(tmp_path) -> None:
    """Exit 0: every leaf classified, the gate and P2(c) pass, the changes are by design."""
    done, report, leaves = run_cli(tmp_path, old_tree(), new_tree())
    assert done.returncode == 0, done.stderr + done.stdout
    assert report.read_text().splitlines()[0] == "DEVELOPMENT (DEV-0): not a hypothesis test"
    rows = json.loads(leaves.read_text())
    assert {r["status"] for r in rows} >= {"equal", "changed", "new", "removed", "timing"}


def test_cli_unclassified_leaf_exits_two_and_names_it(tmp_path) -> None:
    """T3 end to end: exit 2, the path on stderr, no report written."""
    new = new_tree()
    new["systems"]["lorenz63"]["mystery"] = 1.0
    done, report, _ = run_cli(tmp_path, old_tree(), new)
    assert done.returncode == 2
    assert "no rule matches systems/lorenz63/mystery" in done.stderr
    assert not report.exists()


def test_cli_unreadable_input_exits_two(tmp_path) -> None:
    """A missing input file is exit 2."""
    done = subprocess.run([sys.executable, "-I", str(TOOL), str(tmp_path / "nope.json")],
                          capture_output=True, text=True, timeout=60, check=False)
    assert done.returncode == 2
    assert "cannot read input" in done.stderr


def test_cli_unchanged_difference_exits_one(tmp_path) -> None:
    """Exit 1: an unchanged leaf that differs in the last bit is a finding under the bitwise branch."""
    new = new_tree()
    new["systems"]["lorenz63"]["scores"]["A0"]["mse"]["1LT"] = math.nextafter(0.25, 1.0)
    done, report, _ = run_cli(tmp_path, old_tree(), new)
    assert done.returncode == 1
    text = report.read_text()
    assert "| FAIL-differs | systems/lorenz63/scores/A0/mse/1LT | 0.25 | 0.25000000000000006 |" in text


def test_cli_fallback_without_constants_exits_three(tmp_path) -> None:
    """T7: the switch fires (a context float 2e-12 relative off) and no constants exist: exit 3."""
    new = new_tree()
    new["systems"]["lorenz63"]["context"]["lambda_max"] = 0.9056 * (1.0 + 2e-12)
    done, report, _ = run_cli(tmp_path, old_tree(), new)
    assert done.returncode == 3
    assert "DEC is missing" in done.stderr
    assert "REFUSED" in report.read_text()


def test_cli_gate_failure_exits_one(tmp_path) -> None:
    """R4: a gate flag that is false in the new run is a finding in both branches."""
    new = new_tree()
    new["systems"]["lorenz63"]["validation"]["gate"]["V7"] = False
    new["systems"]["lorenz63"]["validation"]["gate"]["gate_pass"] = False
    done, report, _ = run_cli(tmp_path, old_tree(), new)
    assert done.returncode == 1
    assert "| R4 | systems/lorenz63/validation/gate/V7 | False | NO |" in report.read_text()


def test_cli_alert_for_a_failed_variant(tmp_path) -> None:
    """A robustness variant that failed (``error`` leaf) is a finding."""
    new = new_tree()
    new["robustness"] = {"lorenz63": {"D=5": {"error": "RuntimeError('x')"}}}
    done, report, _ = run_cli(tmp_path, old_tree(), new)
    assert done.returncode == 1
    assert "| ALERT | robustness/lorenz63/D=5/error |" in report.read_text()


# ---------------------------------------------------------------------------------- T5
def test_t5_report_strings(tmp_path) -> None:
    """T5: label, a changed row, a removed group, new verdicts, provenance fields (exact strings)."""
    done, report, _ = run_cli(tmp_path, old_tree(), new_tree())
    assert done.returncode == 0
    lines = report.read_text().splitlines()
    assert lines[0] == "DEVELOPMENT (DEV-0): not a hypothesis test"
    # One changed row: old, new, sub-task (WU-0002.3 Log) and reason, with the direction check.
    row = next(x for x in lines if x.startswith("| systems/lorenz63/scores/A0/regret/1LT |"))
    cells = [c.strip() for c in row.strip("|").split(" | ")]
    assert cells[:4] == ["systems/lorenz63/scores/A0/regret/1LT", "0.0354", "0.0364", "WU-0002.3"]
    assert "excess" in cells[5] and cells[6] == "new>=old: ok"
    star = next(x for x in lines if x.startswith("| systems/lorenz63/scores/A*/regret/1LT |"))
    assert star.startswith("| systems/lorenz63/scores/A*/regret/1LT | 0.01 | 0.0 | WU-0002.3 |")
    assert star.endswith("| zero: ok |")
    # A removed group, counted: two leaves of the shift experiment, one rule.
    removed = next(x for x in lines if x.startswith("| systems/*/shift/** |"))
    assert removed.startswith("| systems/*/shift/** | 2 | WU-0002.1 | D-17 |")
    # Provenance: fields present; sha256 from hashlib, not from the tool.
    text = "\n".join(lines)
    assert "- commit: abc1234" in text
    assert "- run dir: RUN-DIR" in text
    assert f"- sha256 old: {hashlib.sha256((tmp_path / 'old.json').read_bytes()).hexdigest()}" in text
    assert f"- sha256 new: {hashlib.sha256((tmp_path / 'new.json').read_bytes()).hexdigest()}" in text
    assert "- manifest row: Pilot v1 (test row)" in text
    assert "- lpc threads: 8 (run); nproc 8 (run env)" in text
    assert "- provenance leaves excluded from the new run: 4" in text   # commit, dirty, 2 env


def test_t5_counts_table(tmp_path) -> None:
    """The group counts add up to the leaves of both sides and list their outcomes."""
    _, report, leaves = run_cli(tmp_path, old_tree(), new_tree())
    rows = json.loads(leaves.read_text())
    groups: dict[str, int] = {}
    for r in rows:
        groups[r["group"]] = groups.get(r["group"], 0) + 1
    text = report.read_text()
    for group, n in groups.items():
        assert any(line.startswith(f"| {group} | {n} |") for line in text.splitlines()), group
    assert len(rows) == sum(groups.values())


def test_bulk_changed_rows_are_summarized_and_look_at_lists_counters(tmp_path) -> None:
    """Arrays of a changed rule (``km_curves/A5``) get one summary row: leaves, equal, max |diff|,
    with non-finite pairs counted apart; the 'things to look at' section lists new counters."""
    old, new = old_tree(), new_tree()
    old["systems"]["lorenz63"]["km_curves"] = {"A5": [1.0, 0.5, 0.25]}
    new["systems"]["lorenz63"]["km_curves"] = {"A5": [1.0, 0.25, math.inf]}
    new["handling"] = {"by_system": {"lorenz63": {"nu_cap_clips": 11}}}
    done, report, _ = run_cli(tmp_path, old, new)
    assert done.returncode == 0, done.stderr
    lines = report.read_text().splitlines()
    assert ("| systems/*/km_curves/A5/[] | 3 | 1 | 0.25 (1 non-finite pairs not in the maximum) "
            "| WU-0002.3 | D-13 |") in lines
    assert "| handling/by_system/lorenz63/nu_cap_clips | 11 |" in lines


# ---------------------------------------------------------------------------------- judging
def test_presence_contradicting_the_class_is_a_finding() -> None:
    """A ``new`` rule with the leaf in v1, a ``removed`` rule with it in the new run, an
    ``unchanged`` leaf missing from one side: each is a finding, whatever the branch."""
    table = cp.Table([cp.Rule("n/x", "new"), cp.Rule("r/x", "removed"), cp.Rule("u/x", "unchanged"),
                      cp.Rule("c/x", "changed", "WU-0", "i", "why")])
    res = {cp.show(r.path): r.status for r in cp.compare_leaves(
        {p("n/x"): 1, p("r/x"): 1, p("u/x"): 1, p("c/x"): 1},
        {p("n/x"): 1, p("r/x"): 1}, table)}
    assert res == {"n/x": "FAIL-new-rule-old-present", "r/x": "FAIL-removed-rule-new-present",
                   "u/x": "FAIL-missing-new", "c/x": "changed-old-only"}
    only_new = {cp.show(r.path): r.status for r in cp.compare_leaves(
        {}, {p("u/x"): 1, p("c/x"): 2, p("n/x"): 3}, table)}
    assert only_new == {"u/x": "FAIL-new-only", "c/x": "changed-new-only", "n/x": "new"}


def test_changed_leaf_with_equal_value_is_marked() -> None:
    """A changed-by-design leaf may keep its value; the report says so."""
    old = {"systems": {"lorenz63": {"H1c": {"pass": True}}}}
    new = {"systems": {"lorenz63": {"H1b": {"pass": True}}}}
    _, _, res = sides(old, new)
    assert [(r.status, r.same) for r in res] == [("changed", True)]


def test_direction_of_regret_and_of_the_oracle() -> None:
    """R3: regret(new) >= regret(v1) up to 1e-12 relative; A* is exactly 0.0."""
    def check(a_old, a_new, star_old=0.5, star_new=0.0):
        old = {"systems": {"lorenz63": {"scores": {"A0": {"regret": {"1LT": a_old}},
                                                   "A*": {"regret": {"1LT": star_old}}}}}}
        new = {"systems": {"lorenz63": {"scores": {"A0": {"regret": {"1LT": a_new}},
                                                   "A*": {"regret": {"1LT": star_new}}}}}}
        return {cp.show(r.path): r.direction_ok for r in sides(old, new)[2]}

    ok = check(1.0, 1.5)
    assert set(ok.values()) == {True}
    assert set(check(1.0, 1.0).values()) == {True}                      # equal is allowed
    assert set(check(1.0, 1.0 * (1 - 5e-13)).values()) == {True}        # inside 1e-12 relative
    bad = check(1.0, 1.0 * (1 - 2e-12))                                  # outside
    assert bad["systems/lorenz63/scores/A0/regret/1LT"] is False
    assert check(1.0, 1.5, star_new=1e-300)["systems/lorenz63/scores/A*/regret/1LT"] is False
    assert check(1.0, 1.5, star_new=-0.0)["systems/lorenz63/scores/A*/regret/1LT"] is False


def test_direction_violation_is_a_value_finding() -> None:
    """A violated direction fails the bitwise branch only (R3 applies there)."""
    old = {"systems": {"lorenz63": {"scores": {"A0": {"regret": {"1LT": 1.0}}}}}}
    new = {"systems": {"lorenz63": {"scores": {"A0": {"regret": {"1LT": 0.5}}}}}}
    res = sides(old, new)[2][0]
    assert res.is_value_finding and not res.is_finding


def test_when_condition_of_the_calibration_choice() -> None:
    """R2: ``A4_minus_A1`` (the pilot's best single) is expected only if the new best single is A1."""
    old = {"systems": {"lorenz63": {"H2c": {"best_single": "A1", "A4_minus_A1": {"mean": 0.5}}}}}

    def status(new_best: str, with_leaf: bool) -> dict:
        h2c: dict = {"best_single": new_best}
        if with_leaf:
            h2c["A4_minus_A1"] = {"mean": 0.5}
        return {cp.show(r.path): r.status
                for r in sides(old, {"systems": {"lorenz63": {"H2c": h2c}}})[2]}

    assert status("A0", False) == {"systems/lorenz63/H2c/best_single": "changed",
                                   "systems/lorenz63/H2c/A4_minus_A1/mean": "skipped"}
    assert status("A1", False)["systems/lorenz63/H2c/A4_minus_A1/mean"] == "FAIL-missing-new"
    assert status("A1", True)["systems/lorenz63/H2c/A4_minus_A1/mean"] == "equal"


def test_timing_is_not_compared() -> None:
    """``seconds`` leaves are wall-clock: any two values, or one side only."""
    res = cp.compare_leaves({p("seconds"): 1.0, p("systems/lorenz63/seconds"): 5.0},
                            {p("seconds"): 99.0})
    assert [r.status for r in res] == ["timing", "timing"]


# ---------------------------------------------------------------------------------- T6
def context_pair(**changes):
    """Old/new context dicts for the switch rule; ``changes`` replace new values."""
    old = {"systems": {"lorenz63": {"context": dict(CONTEXT)}}}
    new = {"systems": {"lorenz63": {"context": {**CONTEXT, **changes}}}}
    return cp.load_sides(old, new)[:2]


def test_t6_identical_context_selects_bitwise() -> None:
    """T6: identical context leaves give the bitwise branch."""
    assert cp.context_switch(*context_pair()) == ("bitwise", [])


def test_t6_float_beyond_1e12_selects_fallback() -> None:
    """T6: one float at 2e-12 relative fires the switch; 5e-13 does not."""
    branch, reasons = cp.context_switch(*context_pair(interval=0.0333 * (1.0 + 2e-12)))
    assert branch == "fallback" and "systems/lorenz63/context/interval" in reasons[0]
    assert cp.context_switch(*context_pair(interval=0.0333 * (1.0 + 5e-13)))[0] == "bitwise"


def test_t6_integer_context_difference_fires_and_fails_f1() -> None:
    """T6: a differing integer fires the switch, and F1 lists it as failed."""
    old, new = context_pair(delay=6)
    assert cp.context_switch(old, new)[0] == "fallback"
    res = cp.compare_leaves(old, new)
    report = cp.evaluate_fallback(res, old, new, cp.TABLE,
                                  {"dec": "DEC-TEST", "k": 2.0, "se": {"lorenz63": 0.5}})
    assert report.f1 == [("systems/lorenz63/context/delay", 5, 6, False)]
    assert not report.passed


def test_t6_missing_context_leaf_fires() -> None:
    """A context leaf missing from the new run selects the fallback branch."""
    old = cp.load_sides({"systems": {"lorenz63": {"context": dict(CONTEXT)}}}, {})[0]
    assert cp.context_switch(old, {})[0] == "fallback"


# ---------------------------------------------------------------------------------- T7
CONSTANTS = {"dec": "DEC-TEST", "k": 2.0, "se": {"lorenz63": 0.5}}  # tolerance k SE = 1.0 exactly


def fallback_for(old_extra: dict, new_extra: dict, new_lambda: float = 0.9056):
    """Evaluate the fallback criterion on small trees (lambda, plus extra system blocks)."""
    old = {"systems": {"lorenz63": {"context": {"lambda_max": 0.9056}, **old_extra}}}
    new = {"systems": {"lorenz63": {"context": {"lambda_max": new_lambda}, **new_extra}}}
    old_l, new_l, res = sides(old, new)
    return cp.evaluate_fallback(res, old_l, new_l, cp.TABLE, CONSTANTS)


@pytest.mark.parametrize("new_lambda, ok", [(1.5, True), (2.0, True), (2.5, False)])
def test_t7_lambda_inside_on_outside(new_lambda, ok) -> None:
    """T7 (F2): |new - pilot| <= k SE with the bound closed. Here lambda_pilot = 1.0, k SE = 1.0."""
    old = {"systems": {"lorenz63": {"context": {"lambda_max": 1.0}}}}
    new = {"systems": {"lorenz63": {"context": {"lambda_max": new_lambda}}}}
    old_l, new_l, res = sides(old, new)
    report = cp.evaluate_fallback(res, old_l, new_l, cp.TABLE, CONSTANTS)
    assert report.f2 == [("lorenz63", 1.0, new_lambda, abs(new_lambda - 1.0), 1.0, ok)]


@pytest.mark.parametrize("new_value, inside", [
    (1.0, True), (0.5, True), (1.5, True),                   # inside and both closed bounds
    (math.nextafter(1.5, 2.0), False), (math.nextafter(0.5, 0.0), False)])
def test_t7_statistic_against_its_pilot_interval(new_value, inside) -> None:
    """T7 (F3): a v1 statistic with a ci lies in [lo, hi] (closed), at the level of the interval."""
    old = {"H1c": {"PLP": {"slope": 1.0, "ci": [0.5, 1.5]}}}      # v1 names: H1c is v3 H1b
    new = {"H1b": {"PLP": {"slope": new_value, "ci": [0.5, 1.5]}}}
    rep = fallback_for(old, new)
    rows = [r for r in rep.f3 if r[0].endswith("PLP/slope")]
    assert rows == [("systems/lorenz63/H1b/PLP/slope", 1.0, new_value, 0.5, 1.5, 0.95, inside)]


def test_t7_statistic_without_interval_is_reported() -> None:
    """T7 (F3): a differing statistic with no pilot interval is reported with its relative
    difference and carries no pass/fail (the value ``None``)."""
    rep = fallback_for({"scores": {"A0": {"mse": {"1LT": 0.25}}}},
                       {"scores": {"A0": {"mse": {"1LT": 0.26}}}})
    (row,) = [r for r in rep.f3 if r[0].endswith("A0/mse/1LT")]
    assert row[:6] == ("systems/lorenz63/scores/A0/mse/1LT", 0.25, 0.26, None, None, None)
    assert row[6] is None
    # |0.26 - 0.25| / 0.26 in floating point; subtraction error ~1e-17 / 1e-2 = 1e-15 << 1e-12.
    assert row[7] == pytest.approx(0.01 / 0.26, rel=1e-12)
    assert rep.passed is True  # reported rows carry no pass/fail; F2 holds (lambda equal)


def test_t7_discrete_flip_and_gate_enter_f5_and_f4() -> None:
    """F5 lists a discrete unchanged leaf that flipped; F4 reads the gate flags."""
    rep = fallback_for({"H3b": {"realized_K": {"2": 2}}},
                       {"regime_curve": {"realized_K": {"2": 3}},
                        "validation": {"gate": {"V1": True, "V7": False}}})
    assert rep.f5 == [("systems/lorenz63/regime_curve/realized_K/2", 2, 3)]
    assert rep.f4 == [("systems/lorenz63/validation/gate/V1", True, True),
                      ("systems/lorenz63/validation/gate/V7", False, False)]
    assert not rep.passed


def test_t7_missing_constants_raise() -> None:
    """T7: the fallback cannot be evaluated without constants (the CLI exits 3)."""
    with pytest.raises(cp.ToolError, match="not recorded"):
        cp.evaluate_fallback([], {}, {}, cp.TABLE, None)
    with pytest.raises(cp.ToolError, match="no SE for lorenz63"):
        old = {p("systems/lorenz63/context/lambda_max"): 1.0}
        cp.evaluate_fallback([], old, old, cp.TABLE, {"dec": "x", "k": 1.0, "se": {}})
    assert cp.FALLBACK_CONSTANTS is None  # until the owner's DEC records them (LPC.AI.12)


# ---------------------------------------------------------------------------------- gate, P2(c)
def test_gate_rows_flag_each_false_or_missing_value() -> None:
    """R4 and R5: gate flags must be True; P2(c) counters must be integer 0; absent is not ok."""
    new = {p("systems/lorenz63/validation/gate/V1"): True,
           p("systems/lorenz63/validation/gate/V7"): False,
           p("systems/lorenz63/verification/P2c/n_violations"): 1,
           p("systems/lorenz63/verification/P2c/n_chain_violations/p2a"): 0,
           p("systems/lorenz63/verification/P2c/n_chain_violations/triangle"): 0.0}
    ok = {(c, path.rsplit("/", 1)[1]): good for c, path, _, good in cp.gate_rows(new)}
    assert ok[("R4", "V1")] is True
    assert ok[("R4", "V7")] is False
    assert ok[("R4", "V2")] is False                 # absent
    assert ok[("R5", "n_violations")] is False       # 1
    assert ok[("R5", "p2a")] is True
    assert ok[("R5", "triangle")] is False           # 0.0 is a float, not the integer 0
    assert ok[("R5", "A_le_B")] is False             # absent


# ---------------------------------------------------------------------------------- robustness
def test_robustness_v3_keys_classify() -> None:
    """The v3 robustness block (keys read from ``experiments._variant_summary`` and
    ``_perturbation_scale_variant``, typed here) is classified, leaf by leaf."""
    variant = {"H1b": {"CP": {"slope": 1.0, "ci": [0.5, 1.5], "n_floored": 0},
                       "PLP": {"slope": 1.0, "ci": [0.5, 1.5], "n_floored": 0,
                               "n_failed_resamples": 0},
                       "pass": True, "threshold": [0.8, 1.2], "n_states": 10, "verdict": "pass",
                       "reason": None, "n_excluded_nonfinite": 0},
               "H2a_median_range": 0.1, "H2a_partial_corr_zero": 0.1,
               "H2a_partial_corr_interior": 0.1, "A4_vs_A2_relative": -0.5, "A4_over_A3": 0.9,
               "A5_regret_ratio": 1.1, "chosen_K": 4,
               "mse_href": {"A*": 0.1, "A0": 0.2, "A1": 0.3, "A2": 0.4, "A3": 0.5, "A4": 0.6,
                            "A4o": 0.7, "A5": 0.8}}
    fin = {"scale_times_rho": 1.0, "H2a_partial_corr_zero_fin": 0.1,
           "H2a_partial_corr_interior_fin": 0.2, "ci_zero": [0.0, 1.0], "ci_interior": [0.0, 1.0],
           "corr_fin_vs_linear": 0.99}
    new = {"robustness": {"lorenz63": {"base": variant, "D=5": variant, "k=5": variant,
                                       "misspec=0.05": variant, "misspec=0.1": variant,
                                       "Lambda_fin(eps=1rho)": fin, "D=10": {"error": "x"}}}}
    _, _, res = sides({}, new)
    status = {cp.show(r.path): r.status for r in res}
    assert status["robustness/lorenz63/base/H1b/CP/slope"] == "FAIL-new-only"  # v1 has it: unchanged
    assert status["robustness/lorenz63/D=10/error"] == "ALERT"
    assert status["robustness/lorenz63/Lambda_fin(eps=1rho)/ci_zero/[0]"] == "new"
    assert status["robustness/lorenz63/base/H2a_partial_corr_zero"] == "new"
    assert status["robustness/lorenz63/base/mse_href/A5"] == "changed-new-only"


# ---------------------------------------------------------------------------------- T8
V1_INTERVAL_PATHS = {  # v1 interval leaves of the pilot (one per kind) -> expected level
    "systems/lorenz63/H2a/range_ci/[0]": PRIMARY,                # analysis.py l. 369-370
    "systems/lorenz63/H2a/partial_ci/[1]": PRIMARY,              # l. 378
    "systems/lorenz63/H2b/noise/ci/[0]": PRIMARY,                # l. 435-436
    "systems/lorenz63/H2b/library/0.01/ci/[1]": PRIMARY,         # l. 448-449 (not in the plan's list)
    "systems/lorenz63/H1a/ci/[0]": 0.95,                         # l. 57 (V7)
    "systems/lorenz63/H1b/by_noise/0.01/ci_inverse_dim/[1]": 0.95,   # l. 109
    "systems/lorenz63/H1c/CP/ci/[0]": 0.95,                      # l. 152
    "systems/lorenz63/H1c/PLP/ci/[1]": 0.95,
    "systems/lorenz63/H1d/CP/ci/[0]": 0.95,                      # l. 193
    "systems/lorenz63/H1f/deployable/logit_w/ci/[0]": 0.95,      # l. 317
    "systems/lorenz63/H1f/oracle/log_horizon/ci/[1]": 0.95,
    "systems/lorenz63/H2c/A4_minus_A1/ci/[0]": 0.95,             # l. 485
    "systems/lorenz63/H2c/A4_minus_A2/ci/[1]": 0.95,
    "systems/lorenz63/H2d/ci/[0]": 0.95,                         # l. 513
    "robustness/lorenz63/base/H1c/CP/ci/[0]": 0.95,              # via h1c_seed_amplifier
    "robustness/rossler/Lambda_fin(eps=3rho)/ci/[1]": 0.95,      # experiments.py l. 299 (default)
}


def test_t8_interval_levels_of_the_v1_leaves() -> None:
    """T8: primary intervals carry 1 - 0.05/3, every other interval 0.95 (v1 code, typed)."""
    for text, level in V1_INTERVAL_PATHS.items():
        rule = cp.TABLE.classify(cp.transform_v1(p(text)))
        assert rule.level == level, text


def test_t8_every_interval_leaf_of_the_pilot_has_a_level_and_nothing_else_does() -> None:
    """T8 over the pilot file. A leaf is an interval leaf iff it is an item of a list under a key
    named ``ci``, ``range_ci``, ``partial_ci`` or ``ci_inverse_dim`` (the file's own naming,
    independent of the table). Its rule must carry a level, 1 - 0.05/3 for the H2a ``range_ci`` and
    ``partial_ci``, the H2b ``noise.ci`` and the H2b ``library.<rho>.ci`` (v1 code, typed), else
    0.95; no other leaf may carry a level. Excepted: intervals inside a wholly removed group (the
    shift experiment, transfer, Lorenz-96, the ``delay/2`` variant: rules ending in ``/**``), which
    are never compared, so that no level is needed."""
    interval_keys = {"ci", "range_ci", "partial_ci", "ci_inverse_dim"}
    primary_keys = {("H2a", "range_ci"), ("H2a", "partial_ci"), ("H2b", "noise", "ci")}
    n_interval = n_primary = 0
    for path in cp.flatten(json.loads(PILOT.read_text())):
        rule = cp.TABLE.classify(cp.transform_v1(path))
        is_interval = len(path) > 1 and path[-1].startswith("[") and path[-2] in interval_keys
        if rule.cls == "removed" and rule.pattern.endswith("/**"):
            assert rule.level is None
            continue
        if not is_interval:
            assert rule.level is None, cp.show(path)
            continue
        key = path[2:-1] if path[0] == "systems" else ()
        primary = key in primary_keys or (len(key) == 4 and key[:2] == ("H2b", "library")
                                          and key[3] == "ci")
        assert rule.level == (PRIMARY if primary else 0.95), cp.show(path)
        n_interval += 1
        n_primary += primary
    # 3 systems x (2 + 2 + 2 + 2 x 2 library rho) primary leaves; the rest at 0.95.
    assert n_primary == 3 * (2 + 2 + 2 + 4)
    assert n_interval > n_primary


# ---------------------------------------------------------------------------------- T9
def test_t9_every_pilot_leaf_matches_exactly_one_rule() -> None:
    """T9: ``pilot_results_v1.json`` loads, transforms (no two leaves collide), and each of its
    11 540 leaves is matched by exactly one rule."""
    tree = json.loads(PILOT.read_text())
    leaves = cp.flatten(tree)
    assert len(leaves) == 11540            # counted by the plan (and by a separate walk)
    moved = {}
    for path in leaves:
        target = cp.transform_v1(path)
        assert target not in moved, cp.show(target)
        moved[target] = path
    assert len(moved) == 11540
    for path in moved:
        assert len(cp.TABLE.matches(path)) == 1, cp.show(path)
    old, new, n_prov = cp.load_sides(tree, {})
    assert len(old) == 11540 and new == {} and n_prov == 0


def test_t9_spot_classifications_from_the_sub_task_logs() -> None:
    """Hand-picked v1 leaves, classified as the sub-task Logs and the plan table say."""
    expect = {  # v1 path (a ``/`` inside a key is written %2F) -> (group, sub-task)
        "systems/lorenz63/context/lambda_max": ("unchanged", ""),
        "systems/chua/scores/A0/mse/1LT": ("unchanged", ""),
        "systems/chua/scores/A0/regret/1LT": ("changed", "WU-0002.3"),
        "systems/chua/scores/A*/regret/4LT": ("changed", "WU-0002.3"),
        "systems/chua/km_curves/A5/[3]": ("changed", "WU-0002.3"),
        "systems/chua/km_curves/A4f/[3]": ("removed", "WU-0002.1"),
        "systems/rossler/shift/core_ratio/A2": ("removed", "WU-0002.1"),
        "systems/rossler/H1c/PLP/slope": ("unchanged", ""),
        "systems/rossler/H1b/by_noise/0.01/fitted_inverse_dim": ("changed", "WU-0002.4"),
        "systems/rossler/H1e/spearman/noise_sensitivity": ("unchanged", ""),
        "systems/rossler/H1f/oracle/logit_w/delta_r2": ("removed", "WU-0002.6"),
        "systems/rossler/H1f/oracle/log_horizon/delta_r2": ("unchanged", ""),
        "systems/rossler/H2a/median_range_unrestricted": ("unchanged", ""),
        "systems/rossler/H2a/median_range": ("changed", "WU-0002.6"),
        "systems/rossler/H2b/noise/mean_state_spearman": ("unchanged", ""),
        "systems/rossler/H2b/library/0.01/pass": ("removed", "WU-0002.7"),
        "systems/rossler/H2c/best_single": ("changed", "WU-0002.8"),
        "systems/rossler/H2e/max_gain_lyapunov": ("unchanged", ""),
        "systems/rossler/H3c/horizon_tree_importance/lambda_tilde": ("changed", "WU-0002.8"),
        "systems/rossler/H3b/p_eff": ("removed", "WU-0002.8"),
        "systems/rossler/H3b/realized_K/5": ("unchanged", ""),
        "systems/rossler/H3b/regret_ratio_by_K/5": ("changed", "WU-0002.3"),
        "systems/rossler/validation/gate/gate_pass": ("changed", "WU-0002.10"),
        "config/regime_max_primary": ("changed", "WU-0002.3"),
        "config/transfer_targets/[0]": ("removed", "WU-0002.1"),
        "transfer/lorenz96/pass": ("removed", "WU-0002.1"),
        "verdicts/H3b/verdict": ("removed", "WU-0002.2, .9"),
        "verdicts/H3c/verdict": ("changed", "WU-0002.9"),
        "estimators/('lorenz96', 7, 5, 0.01)/chosen_width": ("removed", "WU-0002.1"),
        "estimators/('lorenz63', 7, 2, 0.01)/chosen_width": ("removed", "WU-0002.1"),
        "estimators/('lorenz63', 7, 5, 0.01)/chosen_width": ("unchanged", ""),
        "estimators/('lorenz63', 7, 5, 0.01)/seconds": ("timing", ""),
        "robustness/lorenz63/delay%2F2/chosen_K": ("removed", "WU-0002.1"),
        "robustness/lorenz63/D=5/H1c/PLP/slope": ("unchanged", ""),
        "robustness/lorenz63/D=5/A5_regret_ratio": ("changed", "WU-0002.3"),
        "seconds": ("timing", ""),
    }
    for text, (group, sub) in expect.items():
        rule = cp.TABLE.classify(cp.transform_v1(p(text)))
        assert (rule.cls, rule.sub) == (group, sub), text


def test_chain_tags_follow_the_plan_paragraph_on_bitwise_chains() -> None:
    """The plan ("Expected bitwise") names the chains: context is dynamics; V1, V2, V5, V6 are
    fixtures; A0 scores and km_curves, V3 and the analog proxy are the CP chain; A1 to A5, V7,
    H2*, H3* and the weight profile follow the network chain (psi, A3, LM)."""
    def chain(text: str) -> str:
        return cp.TABLE.classify(cp.transform_v1(p(text))).chain

    assert chain("systems/lorenz63/context/delay") == "dynamics"
    assert chain("systems/lorenz63/context/lambda_max") == "dynamics"
    assert chain("systems/lorenz63/validation/km_max_abs_dev") == "fixture"
    assert chain("systems/lorenz63/validation/cp_median_vpt_lyapunov") == "cp"
    assert chain("systems/lorenz63/scores/A0/mse/1LT") == "cp"
    assert chain("systems/lorenz63/km_curves/A0/[7]") == "cp"
    assert chain("systems/lorenz63/fitted/analog_proxy/slope") == "cp"
    assert chain("systems/lorenz63/scores/A3/mse/1LT") == "network"
    assert chain("systems/lorenz63/scores/A0/agreement_href") == "network"  # needs the PLP errors
    assert chain("systems/lorenz63/weight_profile/median/[0]") == "network"
    assert chain("systems/lorenz63/H1a/median_slope") == "network"          # V7
    assert chain("estimators/('lorenz63', 7, 5, 0.01)/chosen_width") == "network"


# ---------------------------------------------------------------------------------- T10
def test_t10_tool_imports_only_the_standard_library() -> None:
    """T10: every import of the tool is in ``sys.stdlib_module_names``; no ``lpcstudy`` import."""
    tree = ast.parse(TOOL.read_text())
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0, "relative import"
            modules.add((node.module or "").split(".")[0])
    assert modules, "no imports found"
    assert modules <= set(sys.stdlib_module_names), sorted(modules - set(sys.stdlib_module_names))
    assert "lpcstudy" not in modules


def test_tool_is_executable_and_has_no_randomness() -> None:
    """The script has the executable bit and uses no random source (it only reads)."""
    import os

    assert os.access(TOOL, os.X_OK)
    source = TOOL.read_text()
    assert not re.search(r"default_rng|random\.|PRNGKey|make_rng", source)
