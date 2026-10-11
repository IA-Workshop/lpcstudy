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
CONTEXT = {"delay": 5, "lambda_max": 0.9056, "interval": 0.0333, "obs_scale": 2.0}
V7_LEVELS = {"0.01": 1.0, "0.02": 1.01}


def old_tree() -> dict:
    """A small v1-named tree: one system, one leaf of each group."""
    return {
        "config": {"name": "pilot", "regime_max_primary": 5},
        "systems": {"lorenz63": {
            "context": dict(CONTEXT),
            "validation": {"gate": dict(GATE)},
            "scores": {"A0": {"regret": {"1LT": 0.0354}, "mse": {"1LT": 0.25}},
                       "A*": {"regret": {"1LT": 0.01}}},
            "H1a": {"median_slope": 1.0, "efficiency_median_by_noise": dict(V7_LEVELS)},
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
            "V7": {"median_slope": 1.0, "efficiency_median_by_noise": dict(V7_LEVELS),
                   "n_nonfinite": 0},
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


def test_cli_unchanged_difference_in_a_network_independent_chain_exits_one(tmp_path) -> None:
    """Exit 1: A0's MSE is the CP chain; with the context equal (branch N) a last-bit difference
    there violates N1, whatever the 1e-6 allowance of the network chain."""
    new = new_tree()
    new["systems"]["lorenz63"]["scores"]["A0"]["mse"]["1LT"] = math.nextafter(0.25, 1.0)
    done, report, _ = run_cli(tmp_path, old_tree(), new)
    assert done.returncode == 1
    text = report.read_text()
    assert "- branch: N (" in text
    assert "| FAIL-differs | systems/lorenz63/scores/A0/mse/1LT | 0.25 | 0.25000000000000006 |" in text
    assert "N1: systems/lorenz63/scores/A0/mse/1LT (cp chain) differs" in text


def test_cli_network_chain_difference_within_1e6_passes(tmp_path) -> None:
    """Branch N passes when only a network-chain leaf differs, by less than 1e-6 relative."""
    old, new = old_tree(), new_tree()
    old["systems"]["lorenz63"]["scores"]["A3"] = {"mse": {"1LT": 0.25}}
    new["systems"]["lorenz63"]["scores"]["A3"] = {"mse": {"1LT": math.nextafter(0.25, 1.0)}}
    done, report, _ = run_cli(tmp_path, old, new)
    assert done.returncode == 0, done.stdout + done.stderr
    text = report.read_text()
    assert "- branch: N (" in text
    assert "| systems/lorenz63/scores/A3/mse/1LT | 0.25 | 0.25000000000000006 |" in text


def branch_d_trees(**context):
    """Old tree and a new tree whose context differs from the pilot's (branch D)."""
    new = new_tree()
    new["systems"]["lorenz63"]["context"].update(context or {"lambda_max": 0.9060})
    return old_tree(), new


def test_cli_branch_d_without_reference_exits_three(tmp_path) -> None:
    """Branch D needs the local v1 run (D1) or --no-reference (D3): exit 3, and the report says so."""
    old, new = branch_d_trees()
    done, report, _ = run_cli(tmp_path, old, new)
    assert done.returncode == 3
    assert "--reference" in done.stderr and "--no-reference" in done.stderr
    text = report.read_text()
    assert "- branch: D (" in text and "mode: missing" in text


def run_cli_with(tmp_path: Path, old: dict, new: dict, *flags: str, reference: dict | None = None):
    """``run_cli`` with extra flags; a reference tree is written and passed with --reference."""
    old_path, new_path = write_pair(tmp_path, old, new)
    extra = list(flags)
    if reference is not None:
        ref_path = tmp_path / "ref.json"
        ref_path.write_text(json.dumps(reference))
        extra += ["--reference", str(ref_path)]
    report, leaves = tmp_path / "report.md", tmp_path / "leaves.json"
    done = subprocess.run(
        [sys.executable, "-I", str(TOOL), str(new_path), "--old", str(old_path), "--report",
         str(report), "--leaves-json", str(leaves), "--run-dir", "RUN-DIR", *extra],
        capture_output=True, text=True, timeout=60, check=False)
    return done, report


def test_cli_branch_d3_inside_the_lambda_band_passes(tmp_path) -> None:
    """D3: lambda 0.0030 above the pilot's, k SE = 5 * 0.0012 = 0.0060 (closed band): pass."""
    old, new = branch_d_trees(lambda_max=0.9056 + 0.0030)
    done, report = run_cli_with(tmp_path, old, new, "--no-reference")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "mode: D3" in report.read_text()


def test_cli_branch_d3_outside_the_lambda_band_fails(tmp_path) -> None:
    """D3: lambda 0.0100 above the pilot's is beyond k SE = 0.0060."""
    old, new = branch_d_trees(lambda_max=0.9056 + 0.0100)
    done, report = run_cli_with(tmp_path, old, new, "--no-reference")
    assert done.returncode == 1
    assert "D2: lambda of lorenz63" in report.read_text()


def test_cli_branch_d1_with_a_reference_run(tmp_path) -> None:
    """D1: the new run equals the local v1 run in the context (so B or N applies against it), and
    the local run's lambda is inside the pilot's 5 SE band (D2)."""
    old, new = branch_d_trees(lambda_max=0.9056 + 0.0030)
    reference = old_tree()
    reference["systems"]["lorenz63"]["context"]["lambda_max"] = 0.9056 + 0.0030
    done, report = run_cli_with(tmp_path, old, new, reference=reference)
    assert done.returncode == 0, done.stdout + done.stderr
    text = report.read_text()
    assert "mode: D1" in text and "against the local v1 run is in branch B" in text
    assert (tmp_path / "leaves.d1.json").exists()


def test_cli_branch_d1_fails_if_the_reference_is_far_from_the_pilot(tmp_path) -> None:
    """D2 on the local run: lambda 0.0100 from the pilot's is beyond 5 SE, though B holds in D1."""
    old, new = branch_d_trees(lambda_max=0.9056 + 0.0100)
    reference = old_tree()
    reference["systems"]["lorenz63"]["context"]["lambda_max"] = 0.9056 + 0.0100
    done, report = run_cli_with(tmp_path, old, new, reference=reference)
    assert done.returncode == 1
    assert "D2: lambda of lorenz63: local" in report.read_text()


def test_cli_branch_d1_fails_if_the_reference_context_differs_from_the_new_run(tmp_path) -> None:
    """D1 needs B or N against the local run: a reference with another context is still D."""
    old, new = branch_d_trees(lambda_max=0.9056 + 0.0030)
    reference = old_tree()  # the pilot's own context, which differs from the new run's
    done, report = run_cli_with(tmp_path, old, new, reference=reference)
    assert done.returncode == 1
    assert "D1: the new run is still in branch D against the local v1 run" in report.read_text()


def test_cli_reference_and_no_reference_exclude_each_other(tmp_path) -> None:
    """Both flags together are a usage error (exit 2)."""
    old, new = branch_d_trees()
    done, _ = run_cli_with(tmp_path, old, new, "--no-reference", reference=old_tree())
    assert done.returncode == 2


def test_cli_cache_flag_yes_is_a_finding(tmp_path) -> None:
    """The launch record says lyapunov.json pre-existed: a finding (the run must be repeated)."""
    done, report = run_cli_with(tmp_path, old_tree(), new_tree(), "--cache-preexisted", "yes")
    assert done.returncode == 1
    assert "lyapunov.json: launch record: lyapunov.json pre-existed in the cache directory (FINDING)" \
        in report.read_text()


def test_cache_status_cases() -> None:
    """The cache statement: flag yes, a file older than the run's start, flag no, no information."""
    status = cp.cache_status
    assert status({"flag": "yes", "cache_mtime": None, "start": None})[1] is True
    assert status({"flag": None, "cache_mtime": 100.0, "start": 200.0})[1] is True    # older than start
    assert status({"flag": None, "cache_mtime": 300.0, "start": 200.0})[1] is False   # written in the run
    assert status({"flag": "no", "cache_mtime": 300.0, "start": 200.0})[1] is False
    assert status({"flag": None, "cache_mtime": None, "start": None})[1] is False


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


def test_r3_when_condition_also_skips_a_present_leaf() -> None:
    """R3: ``H2c/pass`` is always present; if the new best single is not A1 it is a different
    quantity (A4 - A2 with A4 - A0) and is skipped, not compared with v1's."""
    old = {"systems": {"lorenz63": {"H2c": {"best_single": "A1", "pass": True}}}}
    new = {"systems": {"lorenz63": {"H2c": {"best_single": "A0", "pass": False}}}}
    status = {cp.show(r.path): r.status for r in sides(old, new)[2]}
    assert status["systems/lorenz63/H2c/pass"] == "skipped"
    new["systems"]["lorenz63"]["H2c"]["best_single"] = "A1"
    status = {cp.show(r.path): r.status for r in sides(old, new)[2]}
    assert status["systems/lorenz63/H2c/pass"] == "FAIL-differs"


def test_r4_relative_has_no_interval_of_its_own() -> None:
    """R4: the ci of an H2c comparison brackets ``mean`` (MSE units), not ``relative``."""
    def rule(text: str):
        return cp.TABLE.classify(p(text))

    for other in ("A2", "A1"):
        assert rule(f"systems/lorenz63/H2c/A4_minus_{other}/mean").interval == "ci"
        assert rule(f"systems/lorenz63/H2c/A4_minus_{other}/relative").interval == ""


def test_timing_is_not_compared() -> None:
    """``seconds`` leaves are wall-clock: any two values, or one side only."""
    res = cp.compare_leaves({p("seconds"): 1.0, p("systems/lorenz63/seconds"): 5.0},
                            {p("seconds"): 99.0})
    assert [r.status for r in res] == ["timing", "timing"]


# ---------------------------------------------------------------------------------- T6 (DEC-0019)
def context_pair(**changes):
    """Old/new context trees for the branch selection; ``changes`` replace new values."""
    old = {"systems": {"lorenz63": {"context": dict(CONTEXT)}}}
    new = {"systems": {"lorenz63": {"context": {**CONTEXT, **changes}}}}
    old_l, new_l, res = sides(old, new)
    return res, old_l, new_l


def test_t6_identical_context_and_leaves_select_b() -> None:
    """T6: everything equal gives branch B."""
    assert cp.select_branch(*context_pair()) == ("B", [], False)


@pytest.mark.parametrize("change", [
    {"lambda_max": math.nextafter(0.9056, 1.0)},     # one ulp: lambda and interval are bitwise
    {"interval": math.nextafter(0.0333, 1.0)},
    {"obs_scale": 2.0 * (1.0 + 2e-12)},              # beyond 1e-12 relative
    {"delay": 6},                                     # an integer
])
def test_t6_any_other_context_difference_selects_d(change) -> None:
    """T6: the approved text: only obs_scale within 1e-12 relative may differ outside branch D."""
    branch, reasons, _ = cp.select_branch(*context_pair(**change))
    assert branch == "D" and len(reasons) == 1
    assert next(iter(change)) in reasons[0]


def test_t6_obs_scale_within_1e12_is_n_and_flagged() -> None:
    """T6: obs_scale at 5e-13 relative: not D; the unchanged leaf differs, so N, with the flag."""
    branch, reasons, obs_differs = cp.select_branch(*context_pair(obs_scale=2.0 * (1.0 + 5e-13)))
    assert (branch, obs_differs) == ("N", True)
    assert reasons == ["1 unchanged leaves differ from the pilot"]


def test_t6_missing_context_leaf_selects_d() -> None:
    """T6: a context leaf missing from the new run is a context difference."""
    old = {"systems": {"lorenz63": {"context": dict(CONTEXT)}}}
    new = {"systems": {"lorenz63": {"context": {k: v for k, v in CONTEXT.items() if k != "delay"}}}}
    old_l, new_l, res = sides(old, new)
    branch, reasons, _ = cp.select_branch(res, old_l, new_l)
    assert branch == "D" and "context/delay missing from the new run" in reasons[0]


def test_t6_context_equal_and_another_unchanged_leaf_differs_selects_n() -> None:
    """T6: the context equals the pilot's but a network-chain leaf differs: branch N."""
    old = {"systems": {"lorenz63": {"context": dict(CONTEXT), "scores": {"A3": {"mse_href": 0.25}}}}}
    new = {"systems": {"lorenz63": {"context": dict(CONTEXT),
                                    "scores": {"A3": {"mse_href": math.nextafter(0.25, 1.0)}}}}}
    old_l, new_l, res = sides(old, new)
    assert cp.select_branch(res, old_l, new_l)[0] == "N"


def test_approved_constants_are_the_text_of_dec_0019() -> None:
    """The constants are the approved ones: 1e-6, 0.2 SE_arm, z 1.960 and 2.394, k = 5, SE per system."""
    c = cp.FALLBACK_CONSTANTS
    assert c["dec"] == "DEC-0019"
    assert (c["n2_rel"], c["n3_fraction"], c["k"]) == (1e-6, 0.2, 5.0)
    assert c["z"] == {0.95: 1.960, PRIMARY: 2.394}
    assert c["se"] == {"lorenz63": 0.0012, "rossler": 0.00055, "chua": 0.0048}


# ---------------------------------------------------------------------------------- T7 (N1 to N5)
# Test constants with exactly representable arithmetic: the bound |delta| <= 0.25 |old| for N2,
# 0.25 SE_arm for N3, z = 2 at 95% so that SE_arm = arm / 2.
NC = {"dec": "TEST", "n2_rel": 0.25, "n3_fraction": 0.25, "z": {0.95: 2.0, PRIMARY: 4.0},
      "k": 5.0, "se": {"lorenz63": 0.5}}
NC3 = {**NC, "n2_rel": 0.01}   # small N2 bound so that the N3 leaves are beyond it
LAM = {"lambda_max": 1.0}


def n_report(old_extra: dict, new_extra: dict, constants: dict = NC, obs: bool = False):
    """Evaluate N1 to N5 on small trees of one system (the context is equal)."""
    old = {"systems": {"lorenz63": {"context": dict(LAM), **old_extra}}}
    new = {"systems": {"lorenz63": {"context": dict(LAM), **new_extra}}}
    old_l, new_l, res = sides(old, new)
    return cp.evaluate_n(res, old_l, new_l, cp.TABLE, constants, obs)


@pytest.mark.parametrize("new_value, row_outcome", [(4.5, "within"), (5.0, "within"),   # 0.125, 0.25 on
                                                    (5.5, None)])                       # 0.375 beyond
def test_t7_n2_bound_is_closed(new_value, row_outcome) -> None:
    """N2: |new - old| <= bound |old|, closed (old 4.0, bound 0.25: 5.0 is on it, 5.5 beyond)."""
    rep = n_report({"scores": {"A3": {"mse_href": 4.0}}}, {"scores": {"A3": {"mse_href": new_value}}})
    path = "systems/lorenz63/scores/A3/mse_href"
    if row_outcome:
        assert [r[4] for r in rep.n2 if r[0] == path] == ["within"] and rep.passed
    else:
        assert [r[4] for r in rep.n2 if r[0] == path] == ["NO EVENT"]
        assert "no chain-head event upstream in the network chain" in rep.findings[0]


def test_t7_n1_network_independent_chains_must_be_bitwise() -> None:
    """N1: a cp-chain leaf differing at all is a finding; with obs_scale differing it falls to N2."""
    old, new = {"scores": {"A0": {"mse_href": 4.0}}}, {"scores": {"A0": {"mse_href": 4.0000000000000009}}}
    rep = n_report(old, new)
    assert [r[0] for r in rep.n1] == ["systems/lorenz63/scores/A0/mse_href"] and not rep.passed
    rep = n_report(old, new, obs=True)
    assert rep.n1 == [] and rep.passed
    assert [r[4] for r in rep.n2] == ["within"]


@pytest.mark.parametrize("new_value, ok", [
    (1.0625, True),                      # delta +0.0625 = 0.25 * SE_arm (arm 0.5, z 2): on the bound
    (1.0625000000000002, False),
    (1.03125, True)])
def test_t7_n3_upper_arm(new_value, ok) -> None:
    """N3: SE_arm = (hi - est) / z on the side of delta; |delta| <= 0.25 SE_arm, closed.
    The licensing event is a per-system head: a ``fitted`` coefficient beyond the N2 bound.
    (Changed in fix round 1, R1: this test used a count in another result block, H1c n_states, as
    the licence of an H1b slope; N3 now scopes a count to its own block, so a system head is used.)"""
    old = {"H1c": {"PLP": {"slope": 1.0, "ci": [0.5, 1.5]}},
           "fitted": {"estimation_proxy": {"slope": 4.0}}}
    new = {"H1b": {"PLP": {"slope": new_value, "ci": [0.5, 1.5]}},
           "fitted": {"estimation_proxy": {"slope": 6.0}}}
    rep = n_report(old, new, NC3)
    (row,) = rep.n3
    assert row[0] == "systems/lorenz63/H1b/PLP/slope"
    assert row[4] == "systems/lorenz63/fitted/estimation_proxy/slope"      # the licensing event
    assert (row[5], row[6], row[7], row[8], row[9]) == (0.5, 1.5, 0.95, 0.25, 0.0625)
    assert row[10] is ok and rep.passed is ok
    assert [e[1] for e in rep.events] == ["fitted coefficient"]


def test_t7_n3_lower_arm_and_primary_level() -> None:
    """N3: delta < 0 uses the lower arm (est - lo); the primary level has its own z (4 here).
    Lower arm 1.0 - 0.25 = 0.75, SE_arm 0.1875, bound 0.046875, delta -0.09375: beyond."""
    old = {"H2b": {"noise": {"mean_state_spearman": 1.0, "ci": [0.25, 2.0]}},
           "fitted": {"estimation_proxy": {"slope": 4.0}}}
    new = {"H2b": {"noise": {"mean_state_spearman": 0.90625, "ci": [0.25, 2.0]}},
           "fitted": {"estimation_proxy": {"slope": 6.0}}}
    rep = n_report(old, new, NC3)
    (row,) = rep.n3
    assert (row[8], row[9], row[7]) == (0.1875, 0.046875, PRIMARY)
    assert row[10] is False and not rep.passed
    assert "N3: systems/lorenz63/H2b/noise/mean_state_spearman moves -0.09375" in rep.findings[0]


def test_r1_a_count_licenses_only_its_own_block() -> None:
    """R1: an integer count in another block of the system does not license a ``scores`` leaf; a
    count in the leaf's own block does; a ``val_loss_by_width`` head licenses the whole system."""
    scores_old, scores_new = {"scores": {"A3": {"mse_href": 4.0}}}, {"scores": {"A3": {"mse_href": 6.0}}}
    # H1c/PLP/n_states (v1 H1d) is a count of the H1c block, not of scores.
    rep = n_report({**scores_old, "H1d": {"PLP": {"n_states": 1}}},
                   {**scores_new, "H1c": {"PLP": {"n_states": 2}}})
    assert [e[6] for e in rep.events] == ["systems/lorenz63/H1c"] and not rep.passed
    assert "no chain-head event upstream" in rep.findings[0]
    # The same count licenses a leaf of its own block (the PLP median ratio, no interval here).
    rep = n_report({"H1d": {"PLP": {"n_states": 1, "median_ratio": 4.0}}},
                   {"H1c": {"PLP": {"n_states": 2, "median_ratio": 6.0}}})
    assert rep.passed and rep.n3[0][4] == "systems/lorenz63/H1c/PLP/n_states"
    # A val_loss_by_width leaf beyond the bound is a system head (key of the estimators block).
    key = "('lorenz63', 7, 5, 0.01)"
    old_l, new_l, res = sides(
        {"systems": {"lorenz63": {"context": dict(LAM), **scores_old}},
         "estimators": {key: {"val_loss_by_width": {"64": 2.0}}}},
        {"systems": {"lorenz63": {"context": dict(LAM), **scores_new}},
         "estimators": {key: {"val_loss_by_width": {"64": 3.0}}}})
    rep = cp.evaluate_n(res, old_l, new_l, cp.TABLE, NC)
    assert [(e[1], e[6]) for e in rep.events] == [("val_loss beyond bound", "system")] and rep.passed


def test_t7_event_kinds_and_scope() -> None:
    """Events: integer counts, discrete leaves (chosen_width) and fitted coefficients beyond the bound
    license excess only in the same system and chain."""
    old = {"scores": {"A3": {"mse_href": 4.0}}, "fitted": {"estimation_proxy": {"slope": 4.0}}}
    new = {"scores": {"A3": {"mse_href": 6.0}}, "fitted": {"estimation_proxy": {"slope": 6.0}}}
    rep = n_report(old, new)
    assert [(e[1], e[4], e[5]) for e in rep.events] == [("fitted coefficient", "lorenz63", "network")]
    assert rep.passed                                    # the fitted slope is itself the head
    # An event in another system does not license the leaf.
    both_old = {"systems": {"lorenz63": {"context": dict(LAM), "scores": {"A3": {"mse_href": 4.0}}},
                            "rossler": {"context": dict(LAM), "H1d": {"PLP": {"n_states": 1}}}}}
    both_new = {"systems": {"lorenz63": {"context": dict(LAM), "scores": {"A3": {"mse_href": 6.0}}},
                            "rossler": {"context": dict(LAM), "H1c": {"PLP": {"n_states": 2}}}}}
    old_l, new_l, res = sides(both_old, both_new)
    rep = cp.evaluate_n(res, old_l, new_l, cp.TABLE, NC)
    assert [e[4] for e in rep.events] == ["rossler"] and not rep.passed
    # chosen_width of the estimators block is a discrete event of its system.
    key = "('lorenz63', 7, 5, 0.01)"
    old3 = {"scores": {"A3": {"mse_href": 4.0}}}
    new3 = {"scores": {"A3": {"mse_href": 6.0}}}
    old_l, new_l, res = sides(
        {"systems": {"lorenz63": {"context": dict(LAM), **old3}},
         "estimators": {key: {"chosen_width": 64}}},
        {"systems": {"lorenz63": {"context": dict(LAM), **new3}},
         "estimators": {key: {"chosen_width": 128}}})
    rep = cp.evaluate_n(res, old_l, new_l, cp.TABLE, NC)
    assert [(e[1], e[4], e[6]) for e in rep.events] == [("chosen width", "lorenz63", "system")]
    assert rep.passed


def test_t7_n5_regret_allowance_and_the_sentinel() -> None:
    """N5: regret(v3) >= regret(v1) (1 - 1e-6) (R3 allows 1e-12); A* exactly 0.0; a violation in a
    system whose curvature_floor is not 0 is attributed to that sentinel."""
    def run(a_new: float, star_new: float = 0.0, floor: int | None = None):
        old = {"systems": {"lorenz63": {"context": dict(LAM), "scores": {
            "A0": {"regret": {"1LT": 1.0}}, "A*": {"regret": {"1LT": 0.5}}}}}}
        new = {"systems": {"lorenz63": {"context": dict(LAM), "scores": {
            "A0": {"regret": {"1LT": a_new}}, "A*": {"regret": {"1LT": star_new}}}}}}
        if floor is not None:   # the core cell's counter (R6), not the system total
            new["systems"]["lorenz63"]["handling"] = {"cells": {
                "base|rho=0.01|n_lib=10000|core": {"counts": {"curvature_floor": floor}}}}
        old_l, new_l, res = sides(old, new)
        return cp.evaluate_n(res, old_l, new_l, cp.TABLE, cp.FALLBACK_CONSTANTS), res
    rep, res = run(1.0 * (1 - 5e-7))
    assert rep.passed and len(rep.n5) == 2
    assert [r.direction_ok for r in res if r.rule.direction == "new>=old"] == [False]   # R3, 1e-12
    rep, _ = run(1.0 * (1 - 2e-6))
    assert not rep.passed and "N5: systems/lorenz63/scores/A0/regret/1LT" in rep.findings[0]
    rep, _ = run(1.0 * (1 - 2e-6), floor=3)
    assert rep.passed and [r[4] for r in rep.n5 if r[3] is False] == [True]
    assert [r[5] for r in rep.n5 if r[3] is False] == [
        "systems/lorenz63/handling/cells/base|rho=0.01|n_lib=10000|core/counts/curvature_floor"]
    rep, _ = run(1.0 * (1 - 2e-6), floor=0)     # a zero core-cell counter excuses nothing
    assert not rep.passed
    # R6: a counter elsewhere (system total, a sweep cell) does not excuse a violation.
    old = {"systems": {"lorenz63": {"context": dict(LAM), "scores": {"A0": {"regret": {"1LT": 1.0}}}}}}
    new = {"systems": {"lorenz63": {"context": dict(LAM), "scores": {"A0": {"regret": {"1LT": 0.5}}},
                                    "handling": {"cells": {"base|rho=0.02|n_lib=10000|sweep": {
                                        "counts": {"curvature_floor": 7}}}}}},
           "handling": {"by_system": {"lorenz63": {"curvature_floor": 7}}}}
    old_l, new_l, res = sides(old, new)
    assert not cp.evaluate_n(res, old_l, new_l, cp.TABLE, cp.FALLBACK_CONSTANTS).passed
    rep, _ = run(1.5, star_new=1e-300)
    assert not rep.passed


def test_t7_locus_table_marks_the_first_differing_chain() -> None:
    """The divergence locus: chains in the order fixture, dynamics, cp, oracle, network; the first
    one with a differing unchanged leaf is marked FIRST, per system."""
    old = {"scores": {"A0": {"mse_href": 4.0}, "A3": {"mse_href": 4.0, "rmst_lyapunov": 1.0}}}
    new = {"scores": {"A0": {"mse_href": 4.0000000000000009}, "A3": {"mse_href": 4.5,
                                                                      "rmst_lyapunov": 1.0}}}
    rep = n_report(old, new)
    rows = {(r[0], r[1]): r for r in rep.locus}
    assert rows[("lorenz63", "cp")][2:4] == (1, 1) and rows[("lorenz63", "cp")][5] is True
    assert rows[("lorenz63", "network")][2:4] == (2, 1) and rows[("lorenz63", "network")][5] is False
    assert rows[("lorenz63", "dynamics")][2:4] == (1, 0)
    assert rows[("lorenz63", "network")][4] == pytest.approx(0.125, rel=1e-12)   # 0.5 / 4.0, exact


# ---------------------------------------------------------------------------------- D2, D3
def test_t7_d2_lambda_band_is_closed() -> None:
    """D2: |lambda_subject - lambda_pilot| <= k SE (here 5 * 0.5 = 2.5), closed. The pilot's lambda
    is 0.0 so that the difference is computed without rounding."""
    constants = {**NC, "se": {"lorenz63": 0.5}}
    path = p("systems/lorenz63/context/lambda_max")
    for subject, ok in [(2.5, True), (math.nextafter(2.5, 3.0), False), (-2.5, True),
                        (math.nextafter(-2.5, -3.0), False)]:
        (row,) = cp.d2_rows({path: 0.0}, {path: subject}, constants)
        assert row == ("lorenz63", 0.0, subject, abs(subject), 2.5, ok)
    with pytest.raises(cp.ToolError, match="no SE for lorenz63"):
        cp.d2_rows({path: 0.0}, {path: 0.0}, {**NC, "se": {}})
    (row,) = cp.d2_rows({path: 0.0}, {}, constants)           # lambda missing from the subject
    assert row[5] is False


def test_t7_d2_lists_integer_context_differences() -> None:
    """D2 lists the integer context leaves that differ (no pass/fail)."""
    old = {p("systems/lorenz63/context/delay"): 5, p("systems/lorenz63/context/spacing"): 9,
           p("systems/lorenz63/context/lambda_max"): 1.0}
    other = {p("systems/lorenz63/context/delay"): 6, p("systems/lorenz63/context/spacing"): 9,
             p("systems/lorenz63/context/lambda_max"): 1.5}
    assert cp.context_ints_differ(old, other) == [("systems/lorenz63/context/delay", 5, 6)]


def d3_for(pairs: dict[str, tuple[float, list, float, list]], constants: dict = NC):
    """d3_rows on H1b slopes: ``{key: (old_est, old_ci, new_est, new_ci)}`` for PLP and CP."""
    old = {"H1c": {k: {"slope": a, "ci": ca} for k, (a, ca, _, _) in pairs.items()}}
    new = {"H1b": {k: {"slope": b, "ci": cb} for k, (_, _, b, cb) in pairs.items()}}
    old_l, new_l, res = sides({"systems": {"lorenz63": old}}, {"systems": {"lorenz63": new}})
    return cp.d3_rows(res, old_l, new_l, cp.TABLE, constants)


def test_t7_d3_band_with_one_statistic() -> None:
    """D3, m = 1: z_B = Phi^-1(1 - 0.05/2) = 1.959964; SE from the arm on the side of delta over
    z(level). Reference by hand: old arm 0.5 / 1.96 = 0.255102, new arm 0.3 / 1.96 = 0.153061,
    hypot 0.297498, bound 1.959964 * 0.297498 = 0.583087 (6 digits typed; rel 1e-5)."""
    consts = {**NC, "z": {0.95: 1.96, PRIMARY: 2.394}}
    rows, reported, z_b = d3_for({"PLP": (1.0, [0.5, 1.5], 1.2, [0.9, 1.5])}, consts)
    assert z_b == pytest.approx(1.959964, rel=1e-5)
    (row,) = rows
    assert row[3] == pytest.approx(0.2, rel=1e-12)
    assert row[4] == pytest.approx(0.255102, rel=1e-5) and row[5] == pytest.approx(0.153061, rel=1e-5)
    assert row[6] == pytest.approx(0.583087, rel=1e-5) and row[7] is True
    assert reported == []


def test_t7_d3_bonferroni_over_m_statistics_and_failure() -> None:
    """D3, m = 2: z_B = Phi^-1(1 - 0.05/4) = Phi^-1(0.9875) = 2.241403 (table value). A shift of
    1.0 -> 2.5 against arms 0.5 and 0.1 (z 1.96) is far outside the band."""
    consts = {**NC, "z": {0.95: 1.96, PRIMARY: 2.394}}
    rows, _, z_b = d3_for({"PLP": (1.0, [0.5, 1.5], 2.5, [2.4, 2.6]),
                           "CP": (1.0, [0.5, 1.5], 1.0, [0.5, 1.5])}, consts)
    assert z_b == pytest.approx(2.241403, rel=1e-5)
    assert sorted((r[0].rsplit("/", 2)[1], r[7]) for r in rows) == [("CP", True), ("PLP", False)]


def test_t7_d3_reports_leaves_without_intervals_and_discrete_flips() -> None:
    """D3 reports (no pass/fail) the differing unchanged leaves that have no interval in both runs."""
    old = {"systems": {"lorenz63": {"scores": {"A3": {"mse_href": 4.0}}}}}
    new = {"systems": {"lorenz63": {"scores": {"A3": {"mse_href": 5.0}}}}}
    old_l, new_l, res = sides(old, new)
    rows, reported, z_b = cp.d3_rows(res, old_l, new_l, cp.TABLE, NC)
    assert rows == [] and z_b is None
    assert reported == [("systems/lorenz63/scores/A3/mse_href", 4.0, 5.0, 0.25)]


# ---------------------------------------------------------------------------------- gate, P2(c)
def test_gate_rows_flag_each_false_or_missing_value() -> None:
    """R4 and R5: gate flags must be True; P2(c) counters must be integer 0; absent is not ok."""
    new = {p("systems/lorenz63/validation/gate/V1"): True,
           p("systems/lorenz63/validation/gate/V7"): False,
           p("systems/lorenz63/verification/P2c/n_violations"): 1,
           p("systems/lorenz63/verification/P2c/n_chain_violations/p2a"): 0,
           p("systems/lorenz63/verification/P2c/n_chain_violations/triangle"): 0.0}
    new[p("systems/lorenz63/V7/n_nonfinite")] = 0
    new[p("systems/lorenz63/V7/median_slope")] = 1.1
    new[p("systems/lorenz63/V7/efficiency_median_by_noise/0.01")] = 0.9
    new[p("systems/lorenz63/V7/efficiency_median_by_noise/0.05")] = math.nextafter(1.1, 2.0)
    ok = {(c, path.rsplit("/", 1)[1]): good for c, path, _, good in cp.gate_rows(new)}
    assert ok[("R4", "n_nonfinite")] is True
    assert ok[("R4", "median_slope")] is True            # 1.1 is inside the closed band
    assert ok[("R4", "0.01")] is True                    # 0.9 is inside the closed band
    assert ok[("R4", "0.05")] is False                   # one ulp above 1.1
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


def test_r7_a_missing_regret_or_oracle_leaf_is_a_finding() -> None:
    """R7: R3 and N5 are "at every horizon": a regret or A* leaf absent on one side is a structure
    finding (changed rules without a direction stay informational)."""
    old = {"systems": {"lorenz63": {"scores": {"A0": {"regret": {"1LT": 1.0, "2LT": 2.0}},
                                               "A*": {"regret": {"1LT": 0.5}}}}}}
    new = {"systems": {"lorenz63": {"scores": {"A0": {"regret": {"1LT": 1.5}},
                                               "A*": {"regret": {"1LT": 0.0, "2LT": 0.0}}}}}}
    status = {cp.show(r.path): r for r in sides(old, new)[2]}
    assert status["systems/lorenz63/scores/A0/regret/2LT"].status == "FAIL-direction-missing"
    assert status["systems/lorenz63/scores/A*/regret/2LT"].status == "FAIL-direction-missing"
    assert all(r.is_finding for k, r in status.items() if r.status == "FAIL-direction-missing")
    assert status["systems/lorenz63/scores/A0/regret/1LT"].status == "changed"


def test_r8_d1_report_prints_the_reference_path_and_sha256(tmp_path) -> None:
    """R8: the D1 section names the reference file and its SHA-256 (hashlib, not the tool)."""
    old, new = branch_d_trees(lambda_max=0.9056 + 0.0030)
    reference = old_tree()
    reference["systems"]["lorenz63"]["context"]["lambda_max"] = 0.9056 + 0.0030
    done, report = run_cli_with(tmp_path, old, new, reference=reference)
    assert done.returncode == 0, done.stdout + done.stderr
    ref = tmp_path / "ref.json"
    text = report.read_text()
    assert f"D1 reference run (the v1 code run locally): {ref}" in text
    assert f"- sha256: {hashlib.sha256(ref.read_bytes()).hexdigest()}" in text


def test_r10_a_delay_change_between_runs_keeps_the_core_estimators_comparable() -> None:
    """R10 (branch D): the core estimators of the two sides are compared under a role name, whatever
    the system's own delay and embedding dimension are on each side. Old own delay 3, new own delay
    2 (the Rossler case of R9); the old run also has the removed delay/2 variant key (7, 2)."""
    old_tree = {"systems": {"rossler": {"context": {"delay": 3, "embed_dim": 7}}},
                "estimators": {"('rossler', 7, 3, 0.01)": {"chosen_width": 64, "seconds": 1.0},
                               "('rossler', 7, 2, 0.01)": {"chosen_width": 32, "seconds": 1.0},
                               "('rossler', 5, 3, 0.01)": {"chosen_width": 64, "seconds": 1.0}}}
    new_tree = {"systems": {"rossler": {"context": {"delay": 2, "embed_dim": 7}}},
                "estimators": {"('rossler', 7, 2, 0.01)": {"chosen_width": 64, "seconds": 2.0},
                               "('rossler', 5, 3, 0.01)": {"chosen_width": 64, "seconds": 2.0}}}
    old, new, _ = cp.load_sides(old_tree, new_tree)
    status = {cp.show(r.path): r.status for r in cp.compare_leaves(old, new)
              if r.path[0] == "estimators"}
    assert status == {
        "estimators/('rossler', core, core, 0.01)/chosen_width": "equal",
        "estimators/('rossler', core, core, 0.01)/seconds": "timing",
        "estimators/delay2-variant:('rossler', 7, 2, 0.01)/chosen_width": "removed",
        "estimators/delay2-variant:('rossler', 7, 2, 0.01)/seconds": "removed",
        "estimators/('rossler', 5, 3, 0.01)/chosen_width": "equal",
        "estimators/('rossler', 5, 3, 0.01)/seconds": "timing"}
    assert not any(s.startswith("FAIL") for s in status.values())


@pytest.mark.parametrize("single", ["A1", "A0"])
def test_h2c_verdict_keys_of_the_part_are_new_for_any_best_single(single) -> None:
    """The pilot's best single is A1 (the smoke's is A0): the part's verdict keys are new in v3 for
    whichever single was chosen (the A1 pilot output failed with these three keys unclassified)."""
    for key in ("n_failed_resamples", "reason", "verdict"):
        rule = cp.TABLE.classify(p(f"systems/chua/H2c/A4_minus_{single}/{key}"))
        assert (rule.cls, rule.sub) == ("new", "WU-0002.8, .9, .11"), (single, key)
    # the v1 statistics of the A1 part stay unchanged (conditional), the A0 part is new throughout
    mean = cp.TABLE.classify(p(f"systems/chua/H2c/A4_minus_{single}/mean"))
    assert mean.cls == ("unchanged" if single == "A1" else "new")
    assert cp.TABLE.classify(p("systems/chua/H2c/A4_minus_A3/verdict")).cls == "new"   # generic


def test_r9_a_system_delay_of_two_is_not_the_removed_variant() -> None:
    """R9: an estimator key with delay 2 is the removed ``delay/2`` variant only if the system's own
    context delay is not 2 (Rossler's AMI delay is 3 in the pilot but may become 2 in regime D)."""
    key = "('rossler', 7, 2, 0.01)"

    def classes(own_delay: int) -> dict:
        tree = {"systems": {"rossler": {"context": {"delay": own_delay, "embed_dim": 7}}},
                "estimators": {key: {"chosen_width": 64, "seconds": 1.0}}}
        old, new, _ = cp.load_sides(tree, tree)
        return {cp.show(r.path): (r.rule.cls, r.status) for r in cp.compare_leaves(old, new)}

    own3 = classes(3)      # delay 2 is not the system's own: the removed variant (also on the new side)
    assert own3["estimators/delay2-variant:('rossler', 7, 2, 0.01)/chosen_width"] == (
        "removed", "FAIL-removed-rule-new-present")
    own2 = classes(2)      # delay 2 is the system's own: a core estimator, unchanged
    assert own2["estimators/('rossler', core, core, 0.01)/chosen_width"] == ("unchanged", "equal")
    assert own2["estimators/('rossler', core, core, 0.01)/seconds"] == ("timing", "timing")
    old_only, _, _ = cp.load_sides({"systems": {"rossler": {"context": {"delay": 3}}},
                                    "estimators": {key: {"chosen_width": 64}}}, {})
    res = cp.compare_leaves(old_only, {})
    assert [r.status for r in res if r.path[0] == "estimators"] == ["removed"]


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
    # R2: the plan calls the analog proxy a CP-chain leaf, but it is fitted on the estimated nu
    # (allocation.py:123), so it follows the network chain.
    assert chain("systems/lorenz63/fitted/analog_proxy/slope") == "network"
    assert chain("systems/lorenz63/H1c/CP/slope") == "cp"                 # R5
    assert chain("systems/lorenz63/H1d/CP/median_ratio") == "cp"
    assert chain("systems/lorenz63/H1d/CP/n_states") == "cp"
    assert chain("systems/lorenz63/H1c/PLP/slope") == "network"
    assert chain("robustness/lorenz63/base/H1c/CP/ci/[0]") == "cp"
    assert chain("robustness/lorenz63/Lambda_fin(eps=1rho)/corr_fin_vs_linear") == "oracle"
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


# ---------------------------------------------------------------------------------- A10 (WU-0001.6)
DIGEST_KEYS = ("state_mean_digest", "cov_digest", "whiten_digest", "unwhiten_digest")


def digest_context(**changes) -> dict:
    """The fixture context plus the four digests of ``context_record`` (strings, hand-typed)."""
    digests = {key: hashlib.sha256(key.encode()).hexdigest() for key in DIGEST_KEYS}
    return {**CONTEXT, **digests, **changes}


def platform_block(model: str = "Test CPU", cores: tuple[str | None, ...] = ("Haswell", "Haswell"),
                   coretype: str | None = None) -> dict:
    """A hand-built provenance block with the keys of ``provenance.collect`` that the tool reads."""
    libs = [{"library": f"lib{i}.so", "corename": name, "config": "c", "error": None}
            for i, name in enumerate(cores)]
    return {"commit": "abc1234", "dirty": False,
            "env": {"LPC_THREADS": "8", "NPROC": "8", "OPENBLAS_CORETYPE": coretype},
            "cpu": {"model": model, "source": "/proc/cpuinfo", "isa": [], "error": None},
            "blas": {"libraries": libs, "error": None}}


def test_a10_the_four_digest_leaves_are_new_and_everything_classifies() -> None:
    """A10: the fixture new tree plus the four context digests has no unclassified leaf.

    Reference: the plan (rule ``new``, sub-task WU-0001.6, item DEF-0024); statuses decided by
    hand: the four digest leaves are ``new`` (the old side never has them) and the other leaves'
    statuses are those of the same trees without the digests. Exact.
    """
    new = new_tree()
    new["systems"]["lorenz63"]["context"] = digest_context()
    _, _, results = sides(old_tree(), new)
    found = by_path(results)
    for key in DIGEST_KEYS:
        row = found[f"systems/lorenz63/context/{key}"]
        assert row.status == "new" and row.rule.cls == "new"
        assert row.rule.sub == "WU-0001.6" and row.rule.item == "DEF-0024"
    plain = by_path(sides(old_tree(), new_tree())[2])
    assert {k: v.status for k, v in found.items() if not k.endswith(DIGEST_KEYS)} == \
        {k: v.status for k, v in plain.items()}


@pytest.mark.parametrize("changes, branch", [
    ({}, "B"),                                                     # identical context
    ({"obs_scale": 2.0 * (1.0 + 5e-13)}, "N"),                    # within 1e-12 relative
    ({"lambda_max": math.nextafter(0.9056, 1.0)}, "D"),           # one ulp
])
def test_a10_branch_selection_is_unchanged_by_the_digests(changes, branch) -> None:
    """A10: ``select_branch`` returns the same result with and without the digest leaves.

    Reference: the T6 fixtures for B, N and D (decided by hand in T6). The old side never has
    digests, and the rule reads the old side's context paths only (strings, never ``int``). Exact.
    """
    old = {"systems": {"lorenz63": {"context": dict(CONTEXT)}}}
    results = []
    for context in ({**CONTEXT, **changes}, digest_context(**changes)):
        new = {"systems": {"lorenz63": {"context": context}}}
        old_l, new_l, res = sides(old, new)
        results.append(cp.select_branch(res, old_l, new_l))
        assert type(new_l[p("systems/lorenz63/context/delay")]) is int
    assert results[0] == results[1] and results[0][0] == branch


def test_a10_platform_mismatch_needs_both_sides_and_a_difference() -> None:
    """A10: the information line appears when the model or a corename differs, else not.

    Reference: hand-built records (the text of the plan). Equal platforms, a missing side and
    a differing ``OPENBLAS_CORETYPE`` alone give ``None``. Exact string.
    """
    rec = cp.platform_record
    base = {"provenance": platform_block()}
    line = ("platform differs (DEF-0024): cross-host differences in the cp, oracle and fixture "
            "chains are expected")
    assert cp.platform_mismatch(rec(base), rec({"provenance": platform_block()})) is None
    assert cp.platform_mismatch(rec(base), rec({"provenance": platform_block(model="Other")})) == line
    assert cp.platform_mismatch(
        rec(base), rec({"provenance": platform_block(cores=("Haswell", "Sandybridge"))})) == line
    assert cp.platform_mismatch(
        rec(base), rec({"provenance": platform_block(coretype="Haswell")})) is None
    assert cp.platform_mismatch(rec(base), rec({"systems": {}})) is None
    assert cp.platform_mismatch(rec({"systems": {}}), rec({"systems": {}})) is None
    assert cp.platform_mismatch(rec(base), rec({"provenance": {"commit": "x"}})) is None


def test_a10_platform_section_shows_each_side_or_not_recorded(tmp_path) -> None:
    """A10: the report's Platform section has the new, old and reference rows.

    Reference: hand-built trees; the text of the plan. The new run is recorded, the old side has
    no provenance block (the v1 pilot), and the reference (a local v1 run) has none either. The
    mismatch line is absent because only one side is recorded. Exact strings.
    """
    new = new_tree()
    new["provenance"] = platform_block(model="Test CPU", cores=("Haswell", "Sandybridge"),
                                       coretype="Sandybridge")
    done, report = run_cli_with(tmp_path, old_tree(), new, reference=old_tree())
    assert done.returncode == 0, done.stdout + done.stderr
    lines = report.read_text().splitlines()
    start = lines.index("## Platform")
    section = lines[start:lines.index("## Branch")]
    assert "| new run | Test CPU | Haswell, Sandybridge | Sandybridge |" in section
    assert "| old (v1 pilot) | not recorded (no provenance block) |  |  |" in section
    assert "| reference (local v1 run) | not recorded (no provenance block) |  |  |" in section
    assert not any("platform differs" in x for x in section)


def test_a10_platform_section_without_a_reference_omits_that_row(tmp_path) -> None:
    """A10: no ``--reference`` gives the new and old rows only; a block without cpu/blas is flagged.

    Reference: hand-built trees (the fixture new tree has a provenance block without the platform
    keys). Exact.
    """
    done, report = run_cli_with(tmp_path, old_tree(), new_tree())
    assert done.returncode == 0
    text = report.read_text()
    assert "| new run | not recorded (no platform keys in the provenance block) |  |  |" in text
    assert "| old (v1 pilot) | not recorded (no provenance block) |  |  |" in text
    assert "reference (local v1 run)" not in text


def test_a10_a_recorded_old_side_with_another_platform_prints_the_line(tmp_path) -> None:
    """A10: when both sides are recorded and differ, the section carries the information line.

    Reference: hand-built trees passed through ``platform_record`` and ``platform_rows`` (the
    old side of the command line cannot carry a provenance block: ``load_sides`` rejects it, so
    the pair function is tested directly; ``compare_files`` is not called). Exact.
    """
    new = {"provenance": platform_block(model="A")}
    old = {"provenance": platform_block(model="B")}
    rows, notes = cp.platform_rows({"new": cp.platform_record(new), "old": cp.platform_record(old)})
    assert rows[0][:2] == ("new run", "A") and rows[1][:2] == ("old (v1 pilot)", "B")
    assert notes == ["new run against old (v1 pilot): platform differs (DEF-0024): cross-host "
                     "differences in the cp, oracle and fixture chains are expected"]


def test_a10_platform_provenance_changes_no_status_branch_or_exit_code(tmp_path) -> None:
    """A10: two runs that differ only in ``provenance.cpu``/``blas`` compare identically.

    Reference: two CLI runs on the same trees except the new side's provenance block (a Haswell
    host against a Sandybridge host). The per-leaf JSON files (path, group, status) are equal, the
    exit codes are equal, and the reports differ only in the Platform section. Exact.
    """
    outcomes = []
    for index, block in enumerate((platform_block(), platform_block(model="Other", cores=("A", "B")))):
        new = new_tree()
        new["provenance"] = block
        directory = tmp_path / str(index)
        directory.mkdir()
        done, report, leaves = run_cli(directory, old_tree(), new)
        rows = [{k: r[k] for k in ("path", "group", "status")} for r in json.loads(leaves.read_text())]
        branch = next(x for x in report.read_text().splitlines() if x.startswith("- branch:"))
        outcomes.append((done.returncode, rows, branch))
    assert outcomes[0] == outcomes[1]
    texts = []
    for index in (0, 1):
        lines = (tmp_path / str(index) / "report.md").read_text().splitlines()
        start, end = lines.index("## Platform"), lines.index("## Branch")
        # The sha256 of new.json differs because the file differs; nothing else may.
        kept = [x for x in lines[:start] + lines[end:] if not x.startswith("- sha256 new:")]
        texts.append(kept)
        assert lines[start:end] != []
    assert texts[0] == texts[1]


def test_r1_two_unknown_platforms_are_not_the_same_platform() -> None:
    """R1: a recorded but not determinate side gets "platform not determinable", not silence.

    Reference: hand-written expected strings. Two sides with model "unknown", corenames
    ``["unknown", "unknown"]`` or no libraries compare equal as values; the rule must not call
    them the same platform. A failed BLAS probe, an unknown model with a read error, an empty
    library list and a library without corename each make a record indeterminate. A side that is
    not recorded does not (it has its own row). No status, branch or exit code is involved. Exact.
    """
    def unknown(**changes) -> dict:
        block = platform_block(model="unknown", cores=(None, None))
        block["cpu"].update(source="none", error="FileNotFoundError: gone")
        block.update(changes)
        return {"provenance": block}

    first, second = cp.platform_record(unknown()), cp.platform_record(unknown())
    assert first["recorded"] and first["determinate"] is False
    assert first["why"] == "CPU model unknown (FileNotFoundError: gone); lib0.so corename unknown; " \
        "lib1.so corename unknown"
    line = cp.platform_mismatch(first, second, ("new run", "old"))
    assert line == ("platform not determinable (new run: CPU model unknown (FileNotFoundError: gone); "
                    "lib0.so corename unknown; lib1.so corename unknown; old: CPU model unknown "
                    "(FileNotFoundError: gone); lib0.so corename unknown; lib1.so corename unknown)")
    good = cp.platform_record({"provenance": platform_block()})
    assert good["determinate"] is True and good["why"] == ""
    # one indeterminate side is enough; the other side may be determinate or not recorded
    assert cp.platform_mismatch(good, first, ("a", "b")).startswith("platform not determinable (b: ")
    assert cp.platform_mismatch(cp.platform_record({}), first, ("a", "b")).startswith(
        "platform not determinable (b: ")
    failed = cp.platform_record(unknown(blas={"libraries": [], "error": "OSError: no maps"}))
    assert "BLAS probe failed (OSError: no maps)" in failed["why"]
    empty = cp.platform_record({"provenance": {**platform_block(), "blas": {"libraries": [], "error": None}}})
    assert empty["determinate"] is False and empty["why"] == "no OpenBLAS library mapped"


def test_r1_the_not_determinable_line_reaches_the_report_and_changes_nothing(tmp_path) -> None:
    """R1: an indeterminate new side prints the line under the Platform section only.

    Reference: two CLI runs on the same trees, the new provenance block determinate against
    indeterminate (model "unknown"). Same exit code, per-leaf statuses and branch; the
    indeterminate report has the line, the other does not. Exact.
    """
    outcomes = []
    for index, block in enumerate((platform_block(), platform_block(model="unknown"))):
        new = new_tree()
        new["provenance"] = block
        directory = tmp_path / str(index)
        directory.mkdir()
        done, report, leaves = run_cli(directory, old_tree(), new)
        statuses = [(r["path"], r["status"]) for r in json.loads(leaves.read_text())]
        outcomes.append((done.returncode, statuses, report.read_text()))
    assert outcomes[0][:2] == outcomes[1][:2]
    assert "platform not determinable" not in outcomes[0][2]
    assert ("- new run against old (v1 pilot): platform not determinable (new run: CPU model unknown)"
            in outcomes[1][2].splitlines())


def test_r5_a_failed_probe_is_not_a_value_in_the_platform_row() -> None:
    """R5: the table cells of a recorded side show the failure, not "none mapped" or a bare unknown.

    Reference: hand-written expected rows. A failed BLAS probe gives ``probe failed (<error>)``; a
    library with an error gives ``unknown (<error>)``; an unknown model shows the read error (or
    the source when there is none); a working probe with no library says ``none mapped``. The
    comparison fields (``model``, ``corenames``) are unchanged. Exact.
    """
    block = platform_block(model="unknown", cores=("Haswell", None))
    block["cpu"].update(source="none", error="FileNotFoundError: gone")
    block["blas"]["libraries"][1]["error"] = "AttributeError: no symbol"
    rows, _ = cp.platform_rows({"new": cp.platform_record({"provenance": block})})
    assert rows == [("new run", "unknown (FileNotFoundError: gone)",
                     "Haswell, unknown (AttributeError: no symbol)", "unset")]
    block["blas"] = {"libraries": [], "error": "OSError: no maps"}
    rows, _ = cp.platform_rows({"new": cp.platform_record({"provenance": block})})
    assert rows[0][2] == "probe failed (OSError: no maps)"
    block["blas"] = {"libraries": [], "error": None}
    block["cpu"].update(error=None)
    rows, _ = cp.platform_rows({"new": cp.platform_record({"provenance": block})})
    assert rows == [("new run", "unknown (source none)", "none mapped", "unset")]
