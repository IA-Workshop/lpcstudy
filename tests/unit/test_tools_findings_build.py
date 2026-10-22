"""Tests of ``tools/findings_build.py``, the builder of the preliminary
findings document (WU-0020.2, fix round 1).

The tool must do three things for the study: copy stored numbers and verdict
words into a short document without changing them, prove that the document
says nothing else, and refuse to mix the sources that its sections keep apart.
A wrong copy would put a wrong number in front of the owner and the student,
so the tests check the tool against references that do not come from it:

* **Synthetic results with planted values.** ``make_results`` builds a small
  ``results.json`` whose quoted leaves hold values chosen by hand (the
  estimate of part ``i`` is ``0.1 + 0.01 i`` with an interval of plus or minus
  0.05). The document, the trace and the figure arrays must show those values.
  Nothing is computed, so every comparison is exact string or float equality.
* **The stored comparison record.** ``docs/agent/records/work/
  WU-0003-9c-compare-R5R6.txt`` is a ``compare_runs`` output written long
  before this tool; its 18 z values, maximum 2.26, sum of squares 15.77 and
  zero failing parts must come out of ``parse_td`` unchanged (A10).
* **The code's and the proposal's own tables.** The identifier list and the
  primary part paths are compared with ``lpcstudy.identifiers`` and
  ``tools/compare_runs.py``. The secondary leaf paths are typed below from the
  real DEV-2 ``results.json`` (not built from the constants, so the check is
  not circular), and every band and bar is compared with the text of
  ``docs/study/proposal_and_methods_v3.md``.
* **A list of perturbations.** ``test_check_fails_on_every_perturbation``
  changes a built document in the ways a reviewer found that an earlier
  version missed (a swapped sentence, a blanked mark, a hidden number, a
  swapped figure, an edited source) and requires ``check`` to fail on each.

Tolerances. Every check is exact: formatting a float with a fixed format is
deterministic, so a tolerance would only hide a defect. Tests that need no
real figure stub the two drawing functions with a blank figure, which keeps
each test to a second or two; the figure tests and the determinism test draw
the real figures.
"""

from __future__ import annotations

import contextlib
import copy
import csv
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from argparse import Namespace
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import pytest

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools" / "findings_build.py"
_SPEC = importlib.util.spec_from_file_location("findings_build", TOOL)
fb = importlib.util.module_from_spec(_SPEC)
sys.modules["findings_build"] = fb
_SPEC.loader.exec_module(fb)

CONSTANTS = json.loads(fb.CONSTANTS_PATH.read_text())
SYSTEMS = ["lorenz63", "rossler", "chua"]
RECORD = ROOT / "docs/agent/records/work/WU-0003-9c-compare-R5R6.txt"
V3 = ROOT / "docs/study/proposal_and_methods_v3.md"
DEV_BANNER = "**DEVELOPMENT (DEV-9): not a hypothesis test** · **UNPROMOTED**"
ALL_PARTS = (
    CONSTANTS["primary_parts"]
    + CONSTANTS["secondary_parts"]
    + CONSTANTS["qn_parts"]
)


def set_path(tree: dict, path: str, value: object) -> None:
    """Create the nested dict entries of ``path`` and set the leaf."""
    keys = path.split("/")
    for key in keys[:-1]:
        tree = tree.setdefault(key, {})
    tree[keys[-1]] = value


def make_results(
    kind: str = "development",
    gate: dict | None = None,
    backend: str = "cpu",
) -> dict:
    """Build a small results file whose every quoted leaf is planted."""
    confirmatory = kind == "confirmatory"
    out = {
        "config": {"core_systems": list(SYSTEMS)},
        "provenance": {
            "seed_id": "CONF-1" if confirmatory else "DEV-9",
            "seed_kind": kind,
            "label": (
                "CONFIRMATORY: UNPROMOTED"
                if confirmatory
                else "DEVELOPMENT (DEV-9): not a hypothesis test"
            ),
            "preset": "full",
            "commit": "c" * 40,
            "dirty": False,
            "complete": True,
            "wall_seconds": 12345.6,
            "start_utc": "2026-01-02T03:04:05+00:00",
            "end_utc": "2026-01-02T06:07:08+00:00",
            "device": {"backend": backend},
            "env": {"LPC_THREADS": "8"},
        },
        "systems": {},
        "verdicts": {},
        "handling": {
            "totals": {"error_clips": 0, "nu_cap_clips": 7},
            "by_system": {
                s: {"error_clips": 0, "nu_cap_clips": 2} for s in SYSTEMS
            },
            "failed_variants": 0,
            "skipped_variants": 0,
        },
    }
    words = ["pass", "fail", "inconclusive"]
    for n, s in enumerate(SYSTEMS):
        block = out["systems"][s] = {}
        for i, part in enumerate(ALL_PARTS):
            est = 0.1 + 0.01 * i + 0.001 * n
            set_path(block, part["estimate"], est)
            set_path(block, part["interval"], [est - 0.05, est + 0.05])
            if part["verdict"].endswith("/reading"):
                word = "reduces"
            elif part["verdict"].endswith("/role"):
                word = "reported"
            else:
                word = words[(i + n) % 3]
            set_path(block, part["verdict"], word)
            if part["level"]:
                set_path(block, part["level"], 1 - 0.05 / 3)
        flags = {f"V{k}": True for k in (1, 2, 4, 5, 6, 7)}
        flags["gate_pass"] = gate is None or gate.get(s, True)
        block.setdefault("validation", {})["gate"] = flags
        for gate_row in CONSTANTS["gate_rows"]:
            for _, leaf, _ in gate_row["stats"]:
                set_path(block, leaf, 0.5)
        block["H3a"] = {
            "chosen_K": 2,
            "n_per_regime": [10, 20],
            "n_events_per_regime": [4, 5],
            "n_censored_per_regime": [6, 15],
            "pairs": [[1, 0]],
            "logrank_p_raw": [0.004],
            "logrank_p_holm": [0.008],
        }
        block["gain_bound"] = {
            "fraction_within_bound": 0.9,
            "n_states": 90,
            "n_total_states": 100,
            "median_gain_lyapunov": 0.0,
            "max_gain_lyapunov": 2.0,
        }
        for k, item in enumerate(CONSTANTS["result_counts"]):
            set_path(block, item["leaf"], 100 * n + k)
        planted = {item["leaf"] for item in CONSTANTS["result_counts"]}
        for k, item in enumerate(CONSTANTS["reported_quantities"]):
            if item["leaf"] in planted:
                continue  # the same leaf is also a result count (planted above)
            if item["fmt"] == "d":
                set_path(block, item["leaf"], 7 * n + k)
            else:
                set_path(block, item["leaf"], 0.25 + 0.01 * k + 0.001 * n)
            if "ci" in item:
                set_path(block, item["ci"], [0.125, 0.375 + 0.01 * k])
        set_path(block, "H2c/best_single", "A1")
    for item in CONSTANTS["identifiers"]:
        out["verdicts"][item["key"]] = {
            "by_system": {s: "pass" for s in SYSTEMS},
            "verdict": "supported",
        }
    return out


def make_markdown(results: dict) -> str:
    """Build a RESULTS.md with the three parts the tool copies."""
    banner = fb.banner_rule(results["provenance"])
    lines = [
        "# Results",
        "",
        banner,
        "",
        "| ID | Hypothesis | a | Verdict | clip |",
        "|---|---|---|---|---|",
    ]
    for item in CONSTANTS["identifiers"]:
        key = "(reported)" if item["key"] == "gain_bound" else item["key"]
        lines.append(f"| {key} | text 2 | PASS | supported | none 1.5 \\| x |")
    lines += ["", "Interval labels, one per row (procedure):", ""]
    for item in CONSTANTS["identifiers"]:
        key = (
            "(reported)"
            if item["key"] == "gain_bound"
            else f"{item['key']} ({item['role']})"
        )
        lines.append(f"- {key} — procedure: blocks of 5; level: 95%")
    return "\n".join(lines + ["", "## Next"]) + "\n"


def make_td(
    differing: str | None = "2", tier: str | None = "TD", result: str = "PASS"
) -> str:
    """Build a compare_runs text with hand-typed z values.

    ``REFDIR`` and ``NEWDIR`` stand for the two run directories; ``render_args``
    replaces them. The one listed leaf has the same stored value in both runs.
    """
    lines = [f"tier: {tier} (x)"] if tier else ["mode: --td-only"]
    lines += ["REF: REFDIR", "NEW: NEWDIR"]
    if differing is not None:
        lines.append(
            f"TD: {differing} verdict-type leaves differ (reported, no failure):"
        )
        lines.append(
            "      systems/lorenz63/H2a/part_i_verdict: 'pass' -> 'pass'"
        )
    lines.append("  system    part   d z_sym z_away  hw1/hw0  status")
    for n, s in enumerate(SYSTEMS):
        for k, p in enumerate(CONSTANTS["primary_parts"]):
            za = f"{0.5 + 0.1 * k + 0.01 * n:.2f}"
            lines.append(
                f"  {s:<9} {p['name']:<20} 0.0100 {za:>12} {za:>12} 1.000  ok"
            )
    lines.append(
        "  parts computed 18 of 18 expected (cannot be computed: 0); sum z^2 "
        "away 9.99, symmetric (information) 8.88; max z away 1.23, symmetric "
        "(information) 1.11; failing parts (z_away > 3.4) 0"
    )
    lines.append(f"RESULT: {result} (exit 0)")
    return "\n".join(lines) + "\n"


def write_run(directory: Path, results: dict) -> Path:
    """Write results.json and RESULTS.md into a run directory."""
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "results.json").write_text(json.dumps(results))
    (directory / "RESULTS.md").write_text(make_markdown(results))
    return directory


def render_args(tmp: Path, **extra) -> Namespace:
    """Arguments of ``render`` over synthetic runs written under ``tmp``."""
    write_run(tmp / "official", extra.pop("official", None) or make_results())
    write_run(
        tmp / "cross", extra.pop("cross", None) or make_results(backend="gpu")
    )
    text = extra.pop("td", None) or make_td()
    text = text.replace("REFDIR", str(tmp / "official"))
    (tmp / "td.txt").write_text(text.replace("NEWDIR", str(tmp / "cross")))
    base = {
        "official": str(tmp / "official"),
        "crosscheck": str(tmp / "cross"),
        "td": str(tmp / "td.txt"),
        "development": None,
        "out": str(tmp / "out"),
        "stem": "doc",
        "release_ref": None,
        "manifest_official": None,
        "manifest_official_md": None,
        "manifest_crosscheck": None,
    }
    base.update(extra)
    return Namespace(**base)


@contextlib.contextmanager
def stub_figures():
    """Replace the two drawing functions by a blank figure (fast, exact)."""
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            fb, "draw_panels", lambda *a, **k: plt.figure(figsize=(1, 1))
        )
        mp.setattr(
            fb, "draw_crosscheck", lambda *a, **k: plt.figure(figsize=(1, 1))
        )
        yield


def fast_build(tmp: Path, **extra) -> Path:
    """Render with stub figures and return the output directory."""
    args = render_args(tmp, **extra)
    with stub_figures():
        assert fb.render(args) == 0
    return Path(args.out)


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    """One full render with real figures and a development appendix."""
    tmp = tmp_path_factory.mktemp("build")
    args = render_args(tmp)
    write_run(tmp / "dev", make_results())
    args.development = str(tmp / "dev")
    assert fb.render(args) == 0
    return tmp, Path(args.out)


@pytest.fixture(scope="module")
def fast(tmp_path_factory):
    """A clean build with stub figures and a development appendix."""
    tmp = tmp_path_factory.mktemp("fast")
    write_run(tmp / "dev", make_results())
    return fast_build(tmp, development=str(tmp / "dev"))


@pytest.fixture(scope="module")
def bad(tmp_path_factory):
    """A build where chua failed both gates and two verdicts are not pass."""
    tmp = tmp_path_factory.mktemp("bad")
    official = make_results(gate={"chua": False})
    official["verdicts"]["H2a"].update(verdict="not supported")
    official["verdicts"]["H2b"].update(verdict="inconclusive")
    return fast_build(
        tmp,
        official=official,
        cross=make_results(gate={"chua": False}, backend="gpu"),
    )


def doc_of(out: Path) -> str:
    return (out / "doc.md").read_text()


def trace_of(out: Path) -> list[dict]:
    with (out / "doc.trace.csv").open(newline="") as handle:
        return list(csv.DictReader(handle))


def write_trace(out: Path, rows: list[dict]) -> None:
    with (out / "doc.trace.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def rebuilt(out: Path) -> dict:
    record = json.loads((out / "doc.sources.json").read_text())
    paths = {n: Path(p) for n, p in record["files"].items()}
    return fb.read_sources(paths, CONSTANTS)


def check_copy(out: Path, tmp: Path, name: str, edit=None) -> int:
    """Copy a build, edit the document text, run ``check``; return its code."""
    copy_dir = tmp / name
    shutil.copytree(out, copy_dir)
    if edit is not None:
        path = copy_dir / "doc.md"
        text = path.read_text()
        new = edit(text)
        assert new != text, name
        path.write_text(new)
    with stub_figures():
        return fb.run_check(copy_dir, "doc", {})


# --- references independent of the tool ---------------------------------
def test_constants_match_code_tables() -> None:
    """The identifier list and primary part paths equal the code's tables.

    Reference: ``lpcstudy.identifiers.HYPOTHESIS_TABLE`` (keys and roles) and
    ``tools/compare_runs.TD_PARTS`` (the 6 primary parts and their leaf
    paths), both defined independently of this tool. Exact equality.
    """
    sys.path.insert(0, str(ROOT))
    from lpcstudy.identifiers import HYPOTHESIS_TABLE

    table = [(h.key, h.role) for h in HYPOTHESIS_TABLE]
    mine = [(i["key"], i["role"]) for i in CONSTANTS["identifiers"]]
    assert sorted(mine) == sorted(table)
    spec = importlib.util.spec_from_file_location(
        "compare_runs", ROOT / "tools" / "compare_runs.py"
    )
    cr = importlib.util.module_from_spec(spec)
    sys.modules["compare_runs"] = cr
    spec.loader.exec_module(cr)
    theirs = [(n, "/".join(p), "/".join(i)) for n, p, i in cr.TD_PARTS]
    ours = [
        (p["name"], p["estimate"], p["interval"])
        for p in CONSTANTS["primary_parts"]
    ]
    assert ours == theirs


# Typed by hand from the leaf names of the real DEV-2 results.json (the
# structure printed by walking it), not built from the constants.
REAL_LEAVES = {
    "H1a rho-1%": ("H1a/by_noise/0.01/ratio", "H1a/by_noise/0.01/ratio_ci", "H1a/by_noise/0.01/verdict"),
    "H1a rho-2%": ("H1a/by_noise/0.02/ratio", "H1a/by_noise/0.02/ratio_ci", "H1a/by_noise/0.02/verdict"),
    "H1b PLP": ("H1b/PLP/slope", "H1b/PLP/ci", "H1b/verdict"),
    "H1c PLP": ("H1c/PLP/median_ratio", "H1c/PLP/ci", "H1c/PLP/verdict"),
    "H1d analog seed": ("H1d/rows/analog_seed/spearman", "H1d/rows/analog_seed/interval", "H1d/rows/analog_seed/verdict"),
    "H1d estimation seed": ("H1d/rows/estimation_seed/spearman", "H1d/rows/estimation_seed/interval", "H1d/rows/estimation_seed/verdict"),
    "H1d growth": ("H1d/rows/growth/spearman", "H1d/rows/growth/interval", "H1d/rows/growth/verdict"),
    "H2c A4 - A2": ("H2c/A4_minus_A2/mean", "H2c/A4_minus_A2/ci", "H2c/A4_minus_A2/verdict"),
    "H2c A4 - A1": ("H2c/A4_minus_A1/mean", "H2c/A4_minus_A1/ci", "H2c/A4_minus_A1/verdict"),
    "H2c A4o - A2 (reported)": ("H2c/A4o_minus_A2/mean", "H2c/A4o_minus_A2/ci", "H2c/A4o_minus_A2/role"),
    "H2d": ("H2d/in_distribution_excess", "H2d/ci", "H2d/verdict"),
    "H2e rho-1%": ("H2e/by_noise/0.01/median_change", "H2e/by_noise/0.01/ci", "H2e/by_noise/0.01/verdict"),
    "H2e rho-2%": ("H2e/by_noise/0.02/median_change", "H2e/by_noise/0.02/ci", "H2e/by_noise/0.02/verdict"),
    "H3b weight tree": ("H3b/weight_lambda/importance", "H3b/weight_lambda/ci", "H3b/weight_lambda/verdict"),
    "H3b horizon tree D": ("H3b/D/value", "H3b/D/ci", "H3b/D/verdict"),
    "Q-N oracle logit w*": ("Q-N/oracle/logit_w_interior/delta_r2", "Q-N/oracle/logit_w_interior/ci", "Q-N/oracle/logit_w_interior/reading"),
    "Q-N oracle zero indicator": ("Q-N/oracle/w_zero_indicator/delta_r2", "Q-N/oracle/w_zero_indicator/ci", "Q-N/oracle/w_zero_indicator/reading"),
}  # fmt: skip


def test_secondary_leaf_paths_match_the_real_results_layout() -> None:
    """Secondary and Q-N leaf paths equal a list typed from the real file."""
    parts = CONSTANTS["secondary_parts"] + CONSTANTS["qn_parts"]
    mine = {
        p["name"]: (p["estimate"], p["interval"], p["verdict"]) for p in parts
    }
    assert mine == REAL_LEAVES


def v3_text() -> str:
    """The v3 text without Markdown escapes and emphasis marks."""
    return V3.read_text().replace("\\", "").replace("*", "")


# Bands and bars: (band, an exact phrase of v3 section 2, 6 or 7 that states it).
BANDS = {
    "H2a(i)": ([None, 0.1], "(i) interval below 0.1"),
    "H2a(ii) zero": ([-0.1, 0.1], "(ii) every part's interval inside (−0.1, 0.1)"),
    "H2a(ii) interior": ([-0.1, 0.1], "(ii) every part's interval inside (−0.1, 0.1)"),
    "H2b(i)": ([0.0, None], "both lower bounds > 0"),
    "H2b(ii)": ([0.0, None], "both lower bounds > 0"),
    "H3c": ([None, 1.05], "upper bound ≤ 1.05"),
    "H1a rho-1%": ([0.75, 1.25], "ratio interval inside [0.75, 1.25] (closed)"),
    "H1b PLP": ([0.8, 1.2], "in [0.8, 1.2]"),
    "H1c PLP": ([0.8, 1.25], "in [0.8, 1.25]"),
    "H1d growth": ([0.7, None], "each lower bound ≥ 0.7"),
    "H2c A4 - A2": ([None, 0.0], "both upper bounds < 0"),
    "H2d": ([None, 0.1], "upper bound ≤ 0.10"),
    "H2e rho-1%": ([0.0, None], "lower bound > 0 at ρ = 1% and 2%"),
    "H3b weight tree": ([0.0, 0.2], "inside [0, 0.2)"),
    "H3b horizon tree D": ([0.0, None], "lower bound of D > 0"),
}  # fmt: skip
BARS = {
    "v1_bar": "relative error < 10⁻⁴",
    "v2_bar": "ratio in [0.8, 1.2]",
    "v4_bar": "median bootstrap half-width ≤ 0.05",
    "v5_bar": "maximum deviation < 0.01",
    "v6_bar": "< 10⁻³ σ_x",
    "v7_bar": "both in [0.9, 1.1]",
}


def test_bands_and_bars_equal_the_proposal() -> None:
    """Every band, edge and bar is stated by the text of v3 (sections 2, 6, 7).

    Reference: the phrase typed in ``BANDS`` and ``BARS`` must be found in
    ``docs/study/proposal_and_methods_v3.md``, and the band in
    ``design_constants.json`` must equal the band typed beside it. The Q-N
    reading edges 0 and 0.05 are quoted from the section 7 reading table.
    """
    text = v3_text()
    parts = {p["name"]: p for p in ALL_PARTS}
    for name, (band, phrase) in BANDS.items():
        assert phrase in text, (name, phrase)
        assert parts[name]["band"] == band, name
    for name, phrase in BARS.items():
        assert phrase in text, (name, phrase)
    bar_text = {k: CONSTANTS["constants"][k]["text"] for k in BARS}
    assert "10⁻⁴" in bar_text["v1_bar"] and "[0.8, 1.2]" in bar_text["v2_bar"]
    assert "≤ 0.05" in bar_text["v4_bar"] and "< 0.01" in bar_text["v5_bar"]
    assert "10⁻³" in bar_text["v6_bar"] and "[0.9, 1.1]" in bar_text["v7_bar"]
    assert "upper bound < 0.05, lower bound ≤ 0" in text
    assert all(q["lines"] == [0.0, 0.05] for q in CONSTANTS["qn_parts"])
    assert "1 − 0.05/3" in text and "about 7.3%" in text
    assert "a part disagrees if z > 3.4" in text
    assert CONSTANTS["constants"]["td_bound"]["text"] == "3.4"


def test_coverage_limit_quotes_v3_section_8() -> None:
    """The coverage limitation is v3 section 8's sentence, word for word."""
    cited = CONSTANTS["constants"]["coverage_limit"]["text"]
    sentence = cited.split(" (v3 §8")[0]
    assert sentence in v3_text()
    assert "false-verdict probability under dependence" in sentence


def test_every_constant_is_used() -> None:
    """No constant is dead: each is named in the template or the tool."""
    template = fb.TEMPLATE_PATH.read_text()
    source = TOOL.read_text()
    gate_json = json.dumps(CONSTANTS["gate_rows"])
    for name in CONSTANTS["constants"]:
        used = (
            f"const:{name}" in template
            or f'"{name}"' in source
            or f"'{name}'" in source
            or name in gate_json
            or name.startswith("caption_")
        )
        assert used, name


def test_parse_td_reproduces_stored_record() -> None:
    """``parse_td`` returns the printed strings of the stored record (A10).

    Reference: the record ``WU-0003-9c-compare-R5R6.txt``: maximum z_away
    2.26 (rossler H2b(i)), sum of z^2 15.77, 0 failing parts, 18 parts, and
    the chua row ``H2a(i)`` with z_away 1.07. Exact string equality.
    """
    td = fb.parse_td(RECORD)
    parts = [r for s in td["parts"].values() for r in s.values()]
    assert len(parts) == 18
    assert td["parts"]["chua"]["H2a(i)"]["z_away"] == "1.07"
    assert td["parts"]["rossler"]["H2b(i)"]["z_away"] == "2.26"
    assert max(float(r["z_away"]) for r in parts) == 2.26
    assert td["total"]["max_away"] == "2.26"
    assert td["total"]["sum_away"] == "15.77"
    assert td["total"]["failing"] == "0"
    assert td["total"]["differing"] == "52"


def test_absent_differing_count_is_never_a_number(tmp_path) -> None:
    """An absent "verdict-type leaves differ" line is text, never "0" (R7).

    ``compare_runs`` prints the line only when the count is nonzero, so a TD
    report without it says "none listed", a non-TD text says "not
    available", and a text with no totals line is refused. A text that
    cannot support agreement must not select the agreement sentence.
    """
    cases = {
        "td_ok": (make_td(None), fb.NONE_LISTED),
        "td_other": (make_td(None, tier=None), fb.NOT_AVAILABLE),
    }
    for name, (text, expected) in cases.items():
        path = tmp_path / f"{name}.txt"
        path.write_text(text)
        assert fb.parse_td(path)["total"]["differing"] == expected
    broken = tmp_path / "broken.txt"
    broken.write_text("tier: TD\n")
    with pytest.raises(fb.ToolError, match="no TD totals"):
        fb.parse_td(broken)
    out = fast_build(tmp_path / "r", td=make_td(None, tier=None))
    text = doc_of(out)
    assert "differ between the two runs: not available" in text
    assert "differ between the two runs: 0" not in text
    # The count is unavailable, so no sentence may call it zero or agreement.
    assert (
        "differ between the two runs: not available (the compare_runs text"
        in text
    )


def test_fmt_is_deterministic_and_strict() -> None:
    """Formats write the leaf exactly and refuse a wrong type."""
    assert [
        fb.fmt(0.123456, ".4g"),
        fb.fmt([0.1, 0.2], "ci:.1f"),
        fb.fmt(True, "yn"),
        fb.fmt("supported", "verdict"),
        fb.fmt("not supported", "verdict"),
        fb.fmt(None, ".3g"),
        fb.fmt(7, "d"),
    ] == [
        "0.1235",
        "[0.1, 0.2]",
        "yes",
        "supported (preliminary, unpromoted)",
        "not supported",
        "not computed",
        "7",
    ]
    for value, spec in (("text", ".3g"), (1.5, "d"), (1.5, "")):
        with pytest.raises(fb.ToolError):
            fb.fmt(value, spec)


# --- numerals (R2) -------------------------------------------------------
LOOPHOLES = [
    "see `0.81` here",
    "item 3.5% of states",
    "a rate of .003",
    "[rate](0.42)",
    "the quantile p_0.99",
    "n=x1000",
    "shift W-0.5",
    "about 12 percent",
    "H2a is 5",
    "§7% of cases",
    "ABC-1234",
    "WU-0016.45",
    "V1.5",
    "freeze-12",
]
FINE = [
    "Lorenz-63 and Rössler: H2a(ii) at E4 with V1 to V7, DEC-0033 M2, §7 item 3",
    "WU-0016.4 and DEF-0018, P2(c) and A4o minus A2 (QA.11, LPC.PC.13), D6",
    "| lorenz63 | r0 | and rho-0.5% and rho-2% | SHA-256 | CONF-1 | DEV-2 |",
    "## 4. A heading",
]


def test_numeral_scan_catches_every_loophole() -> None:
    """A digit hidden behind any mask is still reported (R2).

    The patterns are typed here, not taken from the tool: backticks, a
    decimal after ``item``, a leading-dot decimal, a link target, a digit after
    an underscore, a letter or a hyphen, an identifier lookalike with extra
    digits, and a plain number. Identifier shapes of the study pass.
    """
    for text in LOOPHOLES:
        assert fb.untraced_numbers([text], []), text
    for text in FINE:
        assert not fb.untraced_numbers([text], []), text


def test_template_is_number_free() -> None:
    """The template has no digit outside placeholders and identifiers (A2).

    The identifier shapes here are written independently of the tool.
    """
    text = re.sub(r"\{\{.*?\}\}", " ", fb.TEMPLATE_PATH.read_text())
    own = [
        r"§\s*M?\d+",
        r"\b[A-Z]{2,4}-\d{4}(?:\.\d)?",
        r"\b(?:CONF|DEV)-\d",
        r"\b(?:QA|PRIME|NVVUQ)\.\d+",
        r"\bLPC\.PC\.\d+",
        r"\b[HVEPADMFvr]\d",
        r"\bLorenz-63",
        r"\bfreeze-1",
        r"\bitem \d+",
        r"^#+ \d+\.",
    ]
    for line in text.split("\n"):
        for pattern in own:
            line = re.sub(pattern, " ", line)
        assert not re.search(r"\d", line), line


# --- the rendered document ------------------------------------------------
def test_banner_lines_and_check_pass(built) -> None:
    """Line 1 is the label as ``header_lines`` writes it; check passes (A1, A2).

    Reference: the banner strings typed here from the rule of
    ``report.header_lines`` (bold label, plus "· **UNPROMOTED**" unless the
    label already says UNPROMOTED). The real figures are re-drawn by ``check``
    and equal the stored PNG files.
    """
    _, out = built
    lines = doc_of(out).split("\n")
    assert lines[0] == DEV_BANNER
    assert lines[1] == fb.PRELIMINARY_LINE
    assert fb.run_check(out, "doc", {}) == 0
    conf = make_results("confirmatory")["provenance"]
    assert fb.banner_rule(conf) == "**CONFIRMATORY: UNPROMOTED**"


def test_banner_rule_matches_report_module() -> None:
    """The banner rule equals ``report.header_lines`` on both labels (A1)."""
    sys.path.insert(0, str(ROOT))
    from lpcstudy.report import header_lines

    for kind in ("development", "confirmatory"):
        prov = {**make_results(kind)["provenance"], "config": {}}
        assert fb.banner_rule(prov) == header_lines(prov)[0]


def test_trace_quotes_every_leaf_exactly(fast) -> None:
    """Each trace row holds the planted leaf and its text (A2).

    Reference: the planted values of ``make_results``: the estimate of the
    first primary part on lorenz63 is ``0.1`` and prints as ``0.1``.
    """
    rows = trace_of(fast)
    first = CONSTANTS["primary_parts"][0]["estimate"]
    row = next(r for r in rows if r["path"] == f"systems/lorenz63/{first}")
    assert row["rendered"] == format(0.1, ".4g")
    assert row["raw"] == repr(0.1)
    assert all(r["source"] in fb.SOURCES for r in rows)


def test_completeness_and_content(fast) -> None:
    """14 identifiers, 18 primary parts, gate, V7, A4o and counters (A4, A5, R9).

    Reference: the 14 keys of ``lpcstudy.identifiers`` (via
    ``test_constants_match_code_tables``) and the planted leaves.
    """
    text = doc_of(fast)
    lines = text.split("\n")
    for item in CONSTANTS["identifiers"]:
        pattern = rf"^\| {re.escape(item['key'])} \| {item['role']} \|"
        assert re.search(pattern, text, re.M)
    assert len([x for x in lines if "LM iteration" in x]) == 18
    assert "| error_clips | 0 | 0 | 0 | 0 |" in text
    assert "| nu_cap_clips | 7 | 2 | 2 | 2 |" in text
    assert "Failed robustness variants: 0." in text
    assert "reported, v1 statistic, v3 screen pending" in text
    assert "Every system passed the validation gate" in text
    for check in ("V1", "V2", "V3", "V4", "V5", "V6", "V7"):
        assert f"| lorenz63 | {check} |" in text
    for rho in ("0.5%", "1%", "2%", "5%"):
        assert f"| lorenz63 | V7 | efficiency_median rho-{rho} |" in text
    assert [
        x for x in lines if "A4o - A2 (reported)" in x and "| reported |" in x
    ]
    labels = [x for x in lines if x.startswith("- ") and "procedure" in x]
    assert len(labels) == 14
    assert "rounded to four-digit precision" in text


def test_design_levels_are_marked_and_counted(fast) -> None:
    """A level that is a design value says so, and the cells are counted (R8)."""
    lines = doc_of(fast).split("\n")
    note = CONSTANTS["constants"]["level_design_note"]["text"]
    primary = [x for x in lines if "LM iteration" in x]
    flagged = [x for x in primary if note in x]
    # H2a(i), H2a(ii) zero, H2a(ii) interior and H2b(i) store no level.
    assert len(flagged) == 12
    assert all("H2b(ii)" not in x and "| H3c |" not in x for x in flagged)
    assert "Level cells that show a design value: 12." in lines


def test_language_rules(fast) -> None:
    """No banned phrase in a PRE-REGISTERED section; required text present (A8)."""
    text = doc_of(fast)
    tags = fb.section_tags(text)
    pre = "\n".join(
        x for x, t in zip(text.split("\n"), tags) if t == "PRE-REGISTERED"
    ).lower()
    for phrase in CONSTANTS["banned_phrases"]:
        assert phrase not in pre
    assert 'The error of "not supported" is not controlled this way' in text
    assert "supported (preliminary, unpromoted)" in text
    edited = text.replace(
        "## 5. The three", "We note that this proves it.\n\n## 5. The three", 1
    )
    problems = fb.check_text(edited.split("\n"), rebuilt(fast), trace_of(fast))
    assert any("banned phrase" in p for p in problems)


def test_student_section_has_no_numbers(fast) -> None:
    """The STUDENT section has no placeholders and no digit (A6)."""
    text = doc_of(fast)
    tags = fb.section_tags(text)
    assert not [r for r in trace_of(fast) if r["tag"] == "STUDENT"]
    student = [
        x for x, t in zip(text.split("\n"), tags) if t == "STUDENT" and x
    ]
    assert student and not fb.untraced_numbers(student, [])


def test_missing_leaf_is_counted(tmp_path) -> None:
    """A missing or null leaf reads so, and is counted in the body (R14)."""
    results = make_results()
    del results["systems"]["chua"]["H3a"]["n_events_per_regime"]
    first = CONSTANTS["primary_parts"][0]
    set_path(results["systems"]["rossler"], first["estimate"], None)
    out = fast_build(tmp_path, official=results)
    text = doc_of(out)
    assert 'Leaves not found in the sources, written "not recorded": 2.' in text
    assert 'Null leaves written "not computed": 1.' in text
    assert 'Cells written "not recorded" so far: 2.' in text
    assert "official:systems/chua/H3a/n_events_per_regime/0" in text
    assert "| not computed |" in text
    with stub_figures():
        assert fb.run_check(out, "doc", {}) == 0


def _write(path: Path, text: str) -> Path:
    path.write_text(text)
    return path


def test_missing_system_fails_closed(tmp_path) -> None:
    """A system absent from the results never shrinks a table (R3).

    chua is deleted from ``systems``. The document still has all 18 primary
    rows, a chua column, "not recorded" cells and PROVISIONAL on every chua
    row; and a ``core_systems`` that is not the three v3 systems is refused.
    """
    results = make_results()
    del results["systems"]["chua"]
    out = fast_build(tmp_path / "a", official=results)
    text = doc_of(out)
    assert len([x for x in text.split("\n") if "LM iteration" in x]) == 18
    chua = [x for x in text.split("\n") if x.startswith("| chua")]
    assert chua and all("PROVISIONAL" in x for x in chua)
    assert "not recorded" in text
    header = next(x for x in text.split("\n") if x.startswith("| ID | Role"))
    assert "chua" in header
    with stub_figures():
        assert fb.run_check(out, "doc", {}) == 0
    short = make_results()
    short["config"]["core_systems"] = ["lorenz63", "rossler"]
    run = write_run(tmp_path / "b", short)
    with pytest.raises(fb.ToolError, match="core_systems"):
        fb.read_sources(
            {
                "official": run / "results.json",
                "official_md": run / "RESULTS.md",
                "crosscheck": run / "results.json",
                "td": _write(tmp_path / "td.txt", make_td()),
            },
            CONSTANTS,
        )


def test_no_recomputation(tmp_path) -> None:
    """The tool imports no verdict function and shows a planted verdict (A3).

    The planted ``H3c`` verdict of lorenz63 is "fail" although its interval
    lies well inside the band (upper bound below 1.05): the document must
    show the stored word, not a recomputed one.
    """
    source = TOOL.read_text()
    for name in ("criterion_verdict", "combine_verdicts", "overall_verdict"):
        assert name not in source
    assert "import lpcstudy" not in source and "from lpcstudy" not in source
    results = make_results()
    leaf = CONSTANTS["primary_parts"][5]
    block = results["systems"]["lorenz63"]
    set_path(block, leaf["estimate"], 0.5)
    set_path(block, leaf["interval"], [0.4, 0.6])
    set_path(block, leaf["verdict"], "fail")
    results["verdicts"]["H3c"]["by_system"]["lorenz63"] = "fail"
    results["verdicts"]["H3c"]["verdict"] = "inconclusive"
    text = doc_of(fast_build(tmp_path, official=results))
    assert re.search(
        r"\| lorenz63 \| H3c \| 0.5 \| \[0.4, 0.6\] \| .* \| fail \|", text
    )
    assert re.search(
        r"^\| H3c \| primary \| fail \| pass \| pass \| inconclusive \|",
        text,
        re.M,
    )


def test_band_edge_rounding_is_disclosed(tmp_path) -> None:
    """A printed edge can equal a band edge the stored endpoint does not reach.

    Planted: the lower endpoint of the lorenz63 H1d growth row is 0.699996
    (band edge 0.7, closed) and the stored verdict is "inconclusive". The
    table prints 0.7 (four digits) beside the stored word, and the document
    says endpoints are rounded (R15).
    """
    results = make_results()
    leaf = next(
        p for p in CONSTANTS["secondary_parts"] if p["name"] == "H1d growth"
    )
    block = results["systems"]["lorenz63"]
    set_path(block, leaf["interval"], [0.699996, 0.9])
    set_path(block, leaf["verdict"], "inconclusive")
    text = doc_of(fast_build(tmp_path, official=results))
    row = next(
        x for x in text.split("\n") if x.startswith("| lorenz63 | H1d growth")
    )
    assert "[0.7, 0.9]" in row and "inconclusive" in row
    assert "unrounded endpoints" in text


# --- the release guard (R5, R6) ---------------------------------------------
def conf_args(tmp: Path) -> Namespace:
    return render_args(
        tmp,
        official=make_results("confirmatory"),
        cross=make_results("confirmatory", backend="gpu"),
    )


def test_guard_refuses_unsafe_inputs(tmp_path, monkeypatch) -> None:
    """The release guard fails closed (A9, R5).

    Refused: a confirmatory file without a release reference or with a
    reference that is not ``ledger-seq-<n>``; missing or wrong manifest
    hashes; a commit that is not freeze-1. Accepted only with everything,
    and then ``check`` verifies the recorded hashes again.
    """
    monkeypatch.setattr(fb, "git_freeze_commit", lambda root: "c" * 40)
    args = conf_args(tmp_path / "c")
    with pytest.raises(fb.ToolError, match="release-ref"):
        fb.render(args)
    for bad_ref in ("x", "ledger-seq-", "ledger-seq-1 ", "seq-4"):
        args.release_ref = bad_ref
        with pytest.raises(fb.ToolError, match="release-ref"):
            fb.render(args)
    args.release_ref = "ledger-seq-17"
    with pytest.raises(fb.ToolError, match="manifest hash"):
        fb.render(args)
    base = tmp_path / "c"
    sha = {
        "official": fb.sha256_of(base / "official" / "results.json"),
        "official_md": fb.sha256_of(base / "official" / "RESULTS.md"),
        "crosscheck": fb.sha256_of(base / "cross" / "results.json"),
    }
    args.manifest_official = sha["official"]
    args.manifest_official_md = "0" * 64
    args.manifest_crosscheck = sha["crosscheck"]
    with pytest.raises(fb.ToolError, match="differs from the manifest"):
        fb.render(args)
    args.manifest_official_md = "z" * 64
    with pytest.raises(fb.ToolError, match="64 hex"):
        fb.render(args)
    args.manifest_official_md = sha["official_md"]
    monkeypatch.setattr(fb, "git_freeze_commit", lambda root: "d" * 40)
    with pytest.raises(fb.ToolError, match="not freeze-1"):
        fb.render(args)
    monkeypatch.setattr(fb, "git_freeze_commit", lambda root: "c" * 40)
    with stub_figures():
        assert fb.render(args) == 0
    out = Path(args.out)
    assert doc_of(out).split("\n")[0] == "**CONFIRMATORY: UNPROMOTED**"
    assert "equals freeze-1" in doc_of(out)
    assert "ledger-seq-17" in doc_of(out)
    record = json.loads((out / "doc.sources.json").read_text())
    assert record["manifest"]["official_md"] == sha["official_md"]
    assert record["release_ref"] == "ledger-seq-17"
    with stub_figures():
        assert fb.run_check(out, "doc", {}) == 0
        record["manifest"]["official"] = "1" * 64
        (out / "doc.sources.json").write_text(json.dumps(record))
        with pytest.raises(fb.ToolError, match="differs from the manifest"):
            fb.run_check(out, "doc", {})


def test_guard_refuses_inconsistent_kind_and_development_file(tmp_path) -> None:
    """Seed id and kind must agree; ``--development`` must be development."""
    spoof = make_results("development")
    spoof["provenance"]["seed_id"] = "CONF-1"
    args = render_args(
        tmp_path / "a", official=spoof, cross=copy.deepcopy(spoof)
    )
    with pytest.raises(fb.ToolError, match="do not describe"):
        fb.render(args)
    labeled = make_results("development")
    labeled["provenance"]["label"] = "CONFIRMATORY: UNPROMOTED"
    args = render_args(
        tmp_path / "b", official=labeled, cross=copy.deepcopy(labeled)
    )
    with pytest.raises(fb.ToolError, match="do not describe"):
        fb.render(args)
    args = render_args(tmp_path / "c")
    write_run(tmp_path / "c" / "conf", make_results("confirmatory"))
    args.development = str(tmp_path / "c" / "conf")
    with pytest.raises(fb.ToolError, match="must be a development run"):
        fb.render(args)
    mixed = render_args(
        tmp_path / "d", cross=make_results("confirmatory", backend="gpu")
    )
    with pytest.raises(fb.ToolError, match="different kinds"):
        fb.render(mixed)


def test_results_md_is_hashed(fast, tmp_path) -> None:
    """RESULTS.md is hashed in sources.json and a later edit is refused (R6)."""
    record = json.loads((fast / "doc.sources.json").read_text())
    assert set(record["sha256"]) >= {
        "official",
        "official_md",
        "crosscheck",
        "td",
    }
    md = Path(record["files"]["official_md"])
    other = tmp_path / "RESULTS.md"
    other.write_text(md.read_text().replace("blocks of 5", "blocks of 9"))
    with stub_figures(), pytest.raises(fb.ToolError, match="changed since"):
        fb.run_check(fast, "doc", {"official_md": str(other)})


# --- check: free slots and the list of perturbations -----------------------
def test_free_slots_accept_only_their_content(fast, tmp_path) -> None:
    """Section 11 and dated section 9 lines may change; nothing else (R1).

    Accepted: new words in section 11; an appended ``- date: text`` line in
    section 9. Refused: a digit in either slot, an undated extra line in
    section 9, an edited rendered line of section 9.
    """
    student = "The student writes this section"
    appended = "- 2026-10-19: {}\n\n## 10. Limitations"
    cases = [
        ("s11 words", lambda t: t.replace(student, "In my words, " + student), 0),
        ("s11 digit", lambda t: t.replace(student, "I found 12 cases. " + student), 1),
        ("s9 dated", lambda t: t.replace("## 10. Limitations", appended.format("compared, no change.")), 0),
        ("s9 dated digit", lambda t: t.replace("## 10. Limitations", appended.format("agreed to 5 digits.")), 1),
        ("s9 undated", lambda t: t.replace("## 10. Limitations", "Regeneration agreed.\n\n## 10. Limitations"), 1),
        ("s9 edited", lambda t: t.replace("pending", "done"), 1),
    ]  # fmt: skip
    for name, edit, expected in cases:
        assert (
            check_copy(fast, tmp_path, name.replace(" ", "_"), edit) == expected
        ), name


def swap(old: str, new: str):
    return lambda text: text.replace(old, new, 1)


def test_check_fails_on_every_perturbation(fast, bad, tmp_path) -> None:
    """Each perturbation of a built document makes ``check`` fail (R1, R2, R4).

    The list comes from the independent review of WU-0020.1 to .3 (cases
    P7, P8, P11, Q6, Q9, G1 to G4 and others). On the clean build and on the
    build where chua failed the gate, every edit below must give exit 1.
    """
    wording = CONSTANTS["wording"]
    intro = "## 1. The question\n"
    clean = {
        "number edited": swap("| 0.1 |", "| 0.2 |"),
        "banner": swap(DEV_BANNER, "**CONFIRMATORY: UNPROMOTED**"),
        "preliminary line": swap(fb.PRELIMINARY_LINE + "\n", ""),
        "mode notice": swap(
            "**DEVELOPMENT DRY RUN (WU-0020.3).** Every number below comes "
            "from a development seed. It rehearses the build and is not a "
            "result of the study.",
            "Results of the study.",
        ),
        "decision rule": swap("fails on at least one system", "fails on all of three systems"),
        "limitation softened": swap("cannot be resolved at these sample sizes", "can be resolved at these sample sizes"),
        "H3a cannot fail": swap("H3a cannot fail", "H3a passed"),
        "supported wording": swap("Pass on all three systems", "Pass on two of three systems"),
        "chua rows dropped": lambda t: "\n".join(x for x in t.split("\n") if not x.startswith("| chua")),
        "section added": lambda t: t + "\n## 12. Extra\n\nText.\n",
        "hidden backtick number": swap(intro, intro + "\n`0.81`\n"),
        "hidden item number": swap(intro, intro + "\nitem 3.5%\n"),
        "hidden leading dot": swap(intro, intro + "\n.003\n"),
        "hidden link number": swap(intro, intro + "\n[rate](0.42)\n"),
        "hidden underscore": swap(intro, intro + "\np_0.99\n"),
        "hidden glued number": swap(intro, intro + "\nn=x1000\n"),
        "hidden hyphen number": swap(intro, intro + "\nW-0.5\n"),
        "figure link": swap("![F1](", "![F9]("),
    }  # fmt: skip
    for name, edit in clean.items():
        label = "c-" + name.replace(" ", "_")
        assert check_copy(fast, tmp_path, label, edit) == 1, name
    box = "> " + wording["gate_failure"]
    dropped = r"^(\| H2a \|.*?) PROVISIONAL"
    broken = {
        "gate box all-clear": swap(box, "> " + wording["gate_ok"]),
        "gpu gate sentence swapped": swap(wording["gpu_gate_failed"].format(systems="chua"), wording["gpu_gate_ok"]),
        "gpu bound sentence swapped": swap("No primary part exceeds the bound", "At least one primary part exceeds the bound"),
        "H2a sentence swapped": swap(wording["not supported"], wording["supported"]),
        "mark dropped on a chua row": swap("| chua PROVISIONAL | V1 |", "| chua | V1 |"),
        "verdict cell mark blanked": lambda t: re.sub(dropped, lambda m: m.group(1) + " " * 12, t, count=1, flags=re.M),
        "verdict cell mark deleted": lambda t: re.sub(dropped, r"\1", t, count=1, flags=re.M),
    }  # fmt: skip
    for name, edit in broken.items():
        label = "b-" + name.replace(" ", "_")
        assert check_copy(bad, tmp_path, label, edit) == 1, name


def test_check_fails_on_edited_inputs(fast, tmp_path) -> None:
    """An edited trace, source or malformed trace row makes ``check`` fail.

    A malformed trace row (unknown source, unknown constant path, a line that
    is not a number) gives a message and exit 1, not a traceback (R13).
    """
    out = tmp_path / "trace"
    shutil.copytree(fast, out)
    rows = trace_of(out)
    rows[10]["rendered"] = "999"
    write_trace(out, rows)
    with stub_figures():
        assert fb.run_check(out, "doc", {}) == 1
    out = tmp_path / "malformed"
    shutil.copytree(fast, out)
    rows = trace_of(out)
    rows[3]["source"] = "nowhere"
    rows[4].update(source="const", path="constants/not_there/text")
    rows[5]["line"] = "x"
    write_trace(out, rows)
    with stub_figures():
        assert fb.run_check(out, "doc", {}) == 1
    record = json.loads((fast / "doc.sources.json").read_text())
    changed = tmp_path / "results.json"
    original = Path(record["files"]["official"]).read_text()
    changed.write_text(original.replace("0.1", "0.2", 1))
    with stub_figures(), pytest.raises(fb.ToolError, match="changed since"):
        fb.run_check(fast, "doc", {"official": str(changed)})


def test_cross_tag_violation_is_refused(fast) -> None:
    """One planted wrong-source row per tag fails the row check (A6)."""
    rows = trace_of(fast)
    wrong = {
        "PRE-REGISTERED": "crosscheck",
        "CROSS-CHECK": "official",
        "DEVELOPMENT": "official",
        "DIAGNOSTIC": "crosscheck",
    }
    lines = doc_of(fast).split("\n")
    for tag, source in wrong.items():
        row = next(r for r in rows if r["tag"] == tag)
        changed = [dict(r) for r in rows]
        changed[int(row["id"])]["source"] = source
        problems = fb.check_rows(changed, lines, rebuilt(fast))
        assert any("not allowed" in p for p in problems), tag
    # ``official_words`` is the official file under a second name, allowed in
    # [CROSS-CHECK] only: every other tag refuses it (WU-0020.8, R2).
    for tag in ("PRE-REGISTERED", "DIAGNOSTIC", "DEVELOPMENT", ""):
        row = next(r for r in rows if r["tag"] == tag)
        changed = [dict(r) for r in rows]
        changed[int(row["id"])]["source"] = "official_words"
        problems = fb.check_rows(changed, lines, rebuilt(fast))
        assert any("not allowed" in p for p in problems), tag
    assert {r["tag"] for r in rows if r["source"] == "official_words"} == {
        "CROSS-CHECK"
    }
    assert {r["tag"] for r in rows if r["source"] == "dev"} == {"DEVELOPMENT"}
    assert {r["tag"] for r in rows if r["source"] in ("td", "crosscheck")} == {
        "CROSS-CHECK",
        "",
    }


def test_limitations_keywords_checked(fast) -> None:
    """A removed limitation fails the check (A7)."""
    text = doc_of(fast).replace("Doubled thinning", "Other")
    problems = fb.check_text(text.split("\n"), rebuilt(fast), trace_of(fast))
    assert any("Doubled thinning" in p for p in problems)


def test_gate_failure_marks_system_provisional(bad) -> None:
    """A failed gate puts PROVISIONAL on every row of that system (A5).

    Reference: the planted ``gate_pass`` False for chua only. Every table
    row that starts with "| chua" carries the mark, the verdict-table cells of
    chua carry it, rossler rows do not, and the gate box says so.
    """
    text = doc_of(bad)
    lines = text.split("\n")
    chua = [x for x in lines if x.startswith("| chua")]
    assert chua and all("PROVISIONAL" in x for x in chua)
    assert not [
        x for x in lines if x.startswith("| rossler") and "PROVISIONAL" in x
    ]
    row = next(x for x in lines if x.startswith("| H2a | primary"))
    assert row.count("PROVISIONAL") == 1
    assert "GATE FAILURE" in text
    assert "The GPU validation gate did not pass on chua" in text
    assert "H2a**: not supported" in text
    assert CONSTANTS["wording"]["reading:H2a"] in text


# --- figures --------------------------------------------------------------
def test_figure_arrays_equal_stored_leaves() -> None:
    """F1 draws exactly the stored estimates and endpoints (A11).

    Reference: the planted leaves of ``make_results``. Matplotlib stores
    float64 data unchanged, so equality is exact. Each panel draws, per
    system, one interval line then one marker line.
    """
    results = make_results()
    parts = CONSTANTS["primary_parts"]
    panels = fb.panel_data(results, parts, SYSTEMS, CONSTANTS)
    fig = fb.draw_panels(panels, 3, "label", {s: False for s in SYSTEMS})
    axes = [a for a in fig.axes if a.get_visible() and a.lines]
    assert len(axes) == 6
    for ax, part in zip(axes, parts):
        lines = ax.get_lines()
        for n, s in enumerate(SYSTEMS):
            block = results["systems"][s]
            est, ci = block, block
            for key in part["estimate"].split("/"):
                est = est[key]
            for key in part["interval"].split("/"):
                ci = ci[key]
            assert list(lines[2 * n].get_xdata()) == ci
            assert list(lines[2 * n + 1].get_xdata()) == [est]
    plt.close(fig)


def test_figure_marks_levels_status_and_reference_lines() -> None:
    """Figure rules of the plan note and the review (A11, R10).

    * A gate-failed system is named PROVISIONAL; verdicts differ by marker.
    * Every panel states its level; the status line is in the title.
    * Q-N panels draw dashed lines at the two reading edges and shade no band.
    * The three H2c rows are drawn one panel per system.
    """
    results = make_results()
    parts = CONSTANTS["primary_parts"][:1]
    panels = fb.panel_data(results, parts, SYSTEMS, CONSTANTS)
    marks = dict(zip(SYSTEMS, (False, False, True)))
    fig = fb.draw_panels(panels, 1, "LABEL", marks)
    ax = fig.axes[0]
    assert [t.get_text() for t in ax.get_yticklabels()] == [
        "lorenz63",
        "rossler",
        "chua PROVISIONAL",
    ]
    lines = [ln for ln in ax.get_lines() if ln.get_marker() != "None"]
    assert len({ln.get_marker() for ln in lines}) == 3
    assert "level 0.9833 (design value)" in ax.get_title()
    title = fig._suptitle.get_text()
    assert "LABEL" in title and fb.PRELIMINARY_LINE in title
    plt.close(fig)
    qn = fb.panel_data(results, CONSTANTS["qn_parts"], SYSTEMS, CONSTANTS)
    fig = fb.draw_panels(qn, 2, "L", {s: False for s in SYSTEMS})
    for ax in fig.axes:
        assert not ax.patches
        dashed = [
            ln.get_xdata()[0]
            for ln in ax.get_lines()
            if ln.get_linestyle() == "--"
        ]
        assert dashed == [0.0, 0.05]
    plt.close(fig)
    h2c = [p for p in CONSTANTS["secondary_parts"] if p["row"] == "H2c"]
    panels = fb.panel_data(results, h2c, SYSTEMS, CONSTANTS)
    assert len(panels) == 9 and all(len(p["systems"]) == 1 for p in panels)
    assert panels[0]["name"] == "H2c A4 - A2 lorenz63"


def test_null_and_missing_points_are_named() -> None:
    """A null or absent leaf is drawn as text, with the table's words (R14)."""
    results = make_results()
    part = CONSTANTS["primary_parts"][0]
    set_path(results["systems"]["rossler"], part["estimate"], None)
    del results["systems"]["chua"][part["estimate"].split("/")[0]]
    panel = fb.panel_data(results, [part], SYSTEMS, CONSTANTS)[0]
    assert isinstance(panel["points"][0], tuple)
    assert panel["points"][1:] == ["not computed", "not recorded"]


def test_crosscheck_figure() -> None:
    """F3 plots the TD tokens and names GPU gate failures and PROVISIONAL (R10)."""
    td = fb.parse_td(RECORD)
    points = fb.crosscheck_points(td, CONSTANTS)
    assert len(points) == 18
    assert {(s, p): z for s, p, z in points}[("rossler", "H2b(i)")] == 2.26
    fig = fb.draw_crosscheck(
        td,
        CONSTANTS,
        "label",
        {"lorenz63": False, "rossler": False, "chua": True},
        {"lorenz63": True, "rossler": True, "chua": False},
    )
    ax = fig.axes[0]
    assert list(ax.get_lines()[0].get_xdata()) == [z for _, _, z in points]
    assert ax.get_lines()[1].get_xdata()[0] == 3.4
    assert ax.get_title() == "Cross-check, information only"
    labels = [t.get_text() for t in ax.get_yticklabels()]
    chua = [x for x in labels if x.startswith("chua")]
    assert chua and all("PROVISIONAL [GPU gate not passed]" in x for x in chua)
    assert not any(
        x.startswith("lorenz63") and "PROVISIONAL" in x for x in labels
    )
    assert any("chua NOT passed" in t.get_text() for t in fig.texts)
    plt.close(fig)


def test_figure_swap_is_detected(built, tmp_path) -> None:
    """F2 copied over F1 (or any changed PNG) fails ``check`` (R4)."""
    _, out = built
    copy_dir = tmp_path / "swap"
    shutil.copytree(out, copy_dir)
    figures = copy_dir / "doc.figures"
    shutil.copy(figures / "F2_secondary.png", figures / "F1_primary.png")
    assert fb.run_check(copy_dir, "doc", {}) == 1


def test_captions_and_excluded_topics() -> None:
    """Captions name an experiment, a v3 id and the interval procedure (A11).

    Also: neither the tool, the template, the constants nor a caption
    mentions a removed experiment.
    """
    for name in ("F1", "F2", "F3"):
        text = CONSTANTS["constants"][f"caption_{name}"]["text"]
        assert re.search(r"\bE[1-6]\b", text)
        assert re.search(r"H[1-3][a-e]|v3 §9", text)
        assert "bootstrap" in text
    banned = ("shift", "transfer", "Lorenz-96", "A4f")
    for path in (TOOL, fb.TEMPLATE_PATH, fb.CONSTANTS_PATH):
        body = path.read_text()
        for word in banned:
            assert word not in body, (path.name, word)


def test_render_is_deterministic(built, tmp_path) -> None:
    """Two renders of the same inputs are byte-identical (A12).

    Reference: SHA-256 equality of the document, the trace and the three
    PNGs between the module fixture and a second render.
    """
    _, out = built
    args = render_args(tmp_path)
    write_run(tmp_path / "dev", make_results())
    args.development = str(tmp_path / "dev")
    assert fb.render(args) == 0
    second = Path(args.out)
    names = ["doc.md", "doc.trace.csv"] + [
        f"doc.figures/{n}.png"
        for n in ("F1_primary", "F2_secondary", "F3_crosscheck")
    ]
    for name in names:
        assert fb.sha256_of(out / name) == fb.sha256_of(second / name), name


# --- fix round 2: provenance (R16), the compare_runs text (R17), free slots ---
def conf_render(tmp: Path, monkeypatch, edit_official=None, edit_cross=None):
    """Render a confirmatory pair with all guards satisfied, after edits."""
    monkeypatch.setattr(fb, "git_freeze_commit", lambda root: "c" * 40)
    official = make_results("confirmatory")
    cross = make_results("confirmatory", backend="gpu")
    if edit_official:
        edit_official(official["provenance"])
    if edit_cross:
        edit_cross(cross["provenance"])
    args = render_args(tmp, official=official, cross=cross)
    args.release_ref = "ledger-seq-3"
    args.manifest_official = fb.sha256_of(tmp / "official" / "results.json")
    args.manifest_official_md = fb.sha256_of(tmp / "official" / "RESULTS.md")
    args.manifest_crosscheck = fb.sha256_of(tmp / "cross" / "results.json")
    with stub_figures():
        return args, fb.render(args)


def test_confirmatory_provenance_is_enforced(tmp_path, monkeypatch) -> None:
    """The official run must be a clean, complete, 8-thread CPU run (A9, R16).

    Each edit below makes a confirmatory render refuse with a message naming
    the field; the cross-check must be clean, complete and a GPU run, and not
    the official file. The unedited pair renders. The same edits do not stop a
    development build (DEV-2 recorded other values).
    """
    refused = {
        "dirty": (lambda p: p.update(dirty=True), None, "dirty"),
        "incomplete": (lambda p: p.update(complete=False), None, "complete"),
        "gpu official": (lambda p: p["device"].update(backend="gpu"), None, "backend"),
        "one thread": (lambda p: p["env"].update(LPC_THREADS="1"), None, "LPC_THREADS"),
        "no threads": (lambda p: p["env"].pop("LPC_THREADS"), None, "LPC_THREADS"),
        "cross dirty": (None, lambda p: p.update(dirty=True), "dirty"),
        "cross incomplete": (None, lambda p: p.update(complete=False), "complete"),
        "cross cpu": (None, lambda p: p["device"].update(backend="cpu"), "backend"),
    }  # fmt: skip
    for name, (edit_o, edit_c, word) in refused.items():
        with pytest.raises(fb.ToolError, match=word):
            conf_render(
                tmp_path / name.replace(" ", "_"), monkeypatch, edit_o, edit_c
            )
    args, code = conf_render(tmp_path / "ok", monkeypatch)
    assert code == 0
    text = doc_of(Path(args.out))
    assert "not verified against the ledger" in text
    assert "(format checked only" in text
    dev = make_results()
    dev["provenance"].update(dirty=True, complete=False)
    dev["provenance"]["env"]["LPC_THREADS"] = "1"
    fast_build(tmp_path / "dev", official=dev)


def test_same_file_cross_check_is_refused(tmp_path) -> None:
    """The official file passed as its own cross-check is refused (R16)."""
    args = render_args(tmp_path)
    args.crosscheck = args.official
    with pytest.raises(fb.ToolError, match="same file|is the official"):
        fb.render(args)
    twin = write_run(tmp_path / "twin", make_results())
    args = render_args(tmp_path / "x", cross=make_results())
    shutil.copy(
        twin / "results.json", tmp_path / "x" / "cross" / "results.json"
    )
    shutil.copy(
        twin / "results.json", tmp_path / "x" / "official" / "results.json"
    )
    with pytest.raises(fb.ToolError, match="same file"):
        fb.render(args)


def test_cross_check_commit_may_differ_but_is_shown(tmp_path) -> None:
    """A later commit of the cross-check is printed and counted, not refused."""
    other = make_results(backend="gpu")
    other["provenance"]["commit"] = "d" * 40
    text = doc_of(fast_build(tmp_path / "a", cross=other))
    assert f"| Cross-check commit | {'d' * 40} (same as official: no) |" in text
    assert (
        "Cross-check commits that differ from the official commit: 1 " in text
    )
    same = doc_of(fast_build(tmp_path / "b"))
    assert (
        f"| Cross-check commit | {'c' * 40} (same as official: yes) |" in same
    )
    assert (
        "Cross-check commits that differ from the official commit: 0 " in same
    )


def test_compare_runs_text_is_bound_to_the_two_files(tmp_path) -> None:
    """REF and NEW must be the official and cross-check runs; leaves must match.

    Refused: the other order (with a message saying so), paths of other runs,
    a listed leaf that does not exist in a results file, a listed leaf whose
    printed value differs from the stored one. Accepted: the same directories
    under another prefix (last two path components). The z values are not
    recomputed, so none of this detects an altered z; the docstring says so.
    """
    base = tmp_path / "base"
    render_args(base)
    paths = {
        "official": base / "official" / "results.json",
        "official_md": base / "official" / "RESULTS.md",
        "crosscheck": base / "cross" / "results.json",
        "td": base / "td.txt",
    }

    def load(text: str):
        paths["td"].write_text(
            text.replace("REFDIR", str(base / "official")).replace(
                "NEWDIR", str(base / "cross")
            )
        )
        return fb.read_sources(paths, CONSTANTS)

    assert "REF is the official run" in load(make_td())["td_binding"]
    swapped = make_td().replace("REFDIR", "TMPX").replace("NEWDIR", "REFDIR")
    with pytest.raises(fb.ToolError, match="other order"):
        load(swapped.replace("TMPX", "NEWDIR"))
    with pytest.raises(fb.ToolError, match="do not name"):
        load(make_td().replace("REFDIR", "/elsewhere/run/full"))
    with pytest.raises(fb.ToolError, match="which is not in the official"):
        load(make_td().replace("H2a/part_i_verdict", "H2a/no_such_leaf"))
    with pytest.raises(fb.ToolError, match="the results store"):
        load(make_td().replace("'pass' -> 'pass'", "'pass' -> 'fail'"))
    prefix = f"/other/prefix/{base.name}/"
    moved = make_td().replace("REFDIR", prefix + "official")
    moved = moved.replace("NEWDIR", prefix + "cross")
    assert "trailing two path components" in load(moved)["td_binding"]
    assert "(development mode only)" in load(moved)["td_binding"]
    with pytest.raises(fb.ToolError, match="no REF and NEW"):
        load(make_td().replace("REF: REFDIR\n", ""))


BOLD_PROMOTED = "".join(chr(0x1D400 + ord(c) - 65) for c in "PROMOTED")
# (text, what its problem message must name). None holds a digit, so only the
# rule named can refuse it. Typed from the verification's probe, with the
# invisible characters written as escapes.
HIDING = [
    ("The study is _PROMOTED_ now.", "promot"),
    ("__CONFIRMATORY__ All three are supported.", "confirm"),
    ("_PROVISIONAL_ is lifted and H2b is supported", "provision"),
    ("it is un_promoted", "promot"),
    ("the pre_registered verdicts hold", "regist"),
    ("The study is PRO*MOTED*.", "promot"),
    ("The study is PRO**MOTED**.", "promot"),
    ("The study is PRO<!-- -->MOTED.", "HTML tag"),
    ("The study is PRO<b></b>MOTED.", "HTML tag"),
    ("The study is PRO&shy;MOTED.", "HTML entity"),
    ("The study is PRO&ZeroWidthSpace;MOTED.", "HTML entity"),
    ("The study is PRO\u200bMOTED.", "format character"),
    ("The study is PRO\u00adMOTED.", "format character"),
    ("The study is PRO\u2060MOTED.", "format character"),
    ("The study is PR\u041eMOTED.", "Latin script"),
    (
        "The study is \uff30\uff32\uff2f\uff2d\uff2f\uff34\uff25\uff24.",
        "promot",
    ),
    (f"The study is {BOLD_PROMOTED}.", "promot"),
    ("> Verdicts: all supported\n> ========", "setext"),
    ("> ## Verdicts: all supported", "heading"),
    ("- ## Verdicts: all supported", "heading"),
    ("- Verdicts: all supported\n    ---", "setext"),
    ("Verdicts\n    ====", "setext"),
    ("\uff3bSEALED\uff3d the verdicts stand", "bracketed"),
    ("[`SEALED`] the verdicts stand", "bracketed"),
    ("[*S*EALED] the verdicts stand", "bracketed"),
    ("[\u200bSEALED] the verdicts stand", "format character"),
    ("&lbrack;SEALED&rbrack; the verdicts stand", "HTML entity"),
    ("[\uff33EALED] the verdicts stand", "bracketed"),
    ("about &half; of the parts", "HTML entity"),
    ("a heading\n-", "setext"),
    ("a task [X] is done", "bracketed"),
    ("see [Lorenz attractor](https://example.org/lorenz)", "bracketed"),
]
ATTACKS = [
    "§ 0.938 of the states",
    "r947 and QA.73 and PRIME.14 and LPC.PC.95",
    "DEF-0947 and WU-0938.1 and D14 and item 7",
    "# 42. percent",
    "CONF-9 and rho-5%",
    "⁹⁵ percent of them",
    "¾ of the parts",
    "٣ cases and １２ cases and Ⅻ",
    "**CONFIRMATORY: PROMOTED** All three are supported.",
    "### Verdicts [PRE-REGISTERED]",
    "so the study proves the theory",
    "PROVISIONAL is lifted and H2b is supported",
    "this was verified by hand",
    "the gate passed after all",
    "a [STUDENT] note",
    "Results are UNPROMOTED no more",
    # N4: inflected forms of refused words (stems), no digit anywhere.
    "the study proved it",
    "all of it was confirmed",
    "a significantly better blend",
    "two gates were passed",
    "the result is provisionally fine",
    "after the promotion we know",
    # N4: setext headings, and a bracketed capitalized token of any text.
    "Verdicts\n========",
    "Verdicts\n--------",
    "[CROSS CHECK] here",
    "[Note about the table] here",
    # V2 to V5 of the verification: Markdown and Unicode disguises.
    *[text for text, _ in HIDING],
]
DATED_ATTACKS = [
    "- 0938-09-47: agreed",
    "- 2026-02-30: agreed",
    "- 2025-01-01: agreed",
    "- 2026-10-19: GPU cross-check agreed; PROVISIONAL is lifted and H2b is supported.",
    "- 2026-10-19: see item 3",
    "- 2026-10-19: agreed to five digits and 3 more",
    "- 2026-10-19 agreed",
    "- 2099-12-31: agreed",  # N4: after the day check runs
    "- 2026-10-19: the study is _PROMOTED_",  # V2 in a dated line
    "- 2026-10-19: all PRO\u200bMOTED",  # V4 in a dated line
]


def test_free_slot_attacks_are_refused(fast, tmp_path) -> None:
    """Every free-slot attack of the second review fails ``check`` (R18, R19).

    The strings are typed here: identifier shapes carrying digits, numerals of
    other Unicode categories (superscript, vulgar fraction, Arabic-Indic,
    fullwidth, Roman), status claims, headings and tags, and bad dates. Each
    goes in section 11 or as a section 9 line and must fail; a digit problem
    names the document line. Plain student words with hypothesis names pass.
    """
    student = "The student writes this section"
    for k, text in enumerate(ATTACKS):
        assert (
            check_copy(
                fast,
                tmp_path,
                f"a{k}",
                lambda t: t.replace(student, text + "\n" + student),
            )
            == 1
        ), text
    for k, text in enumerate(DATED_ATTACKS):
        edit = lambda t: t.replace(
            "## 10. Limitations", text + "\n\n## 10. Limitations"
        )  # noqa: E731
        assert check_copy(fast, tmp_path, f"d{k}", edit) == 1, text
    fine = "H2a and H3c are inconclusive, so the picture is mixed."
    edit = lambda t: t.replace(student, fine + "\n" + student)  # noqa: E731
    assert check_copy(fast, tmp_path, "fine", edit) == 0
    # The message names the document line, not the line inside the slot.
    doc = doc_of(fast).split("\n")
    at = next(i for i, x in enumerate(doc) if x.startswith(student)) + 1
    free = [(at, "I saw ⁹⁵ percent", False)]
    problems = fb.check_free_slots(free, CONSTANTS, None)
    assert problems and problems[0].startswith(f"line {at}:")
    free = [(7, "- 2026-10-19: 3 cases", True)]
    assert fb.check_free_slots(free, CONSTANTS, None)[0].startswith("line 7:")


# (text, a word that its problem message must contain): each attack must fail
# for the intended reason, not by accident of another rule.
FREE_SLOT_REASONS = [
    ("the study proved it", "stem 'prove'"),
    ("all of it was confirmed", "stem 'confirm'"),
    ("a significantly better blend", "stem 'signific'"),
    ("two gates were passed", "stem 'gate'"),
    ("the result is provisionally fine", "stem 'provision'"),
    ("after the promotion we know", "stem 'promot'"),
    ("the unpromoted copy", "stem 'unpromot'"),
    ("it was proving the point", "stem 'provin'"),
    ("a [CROSS CHECK] here", "bracketed capitalized"),
    ("a [Note about the table] here", "bracketed capitalized"),
    ("a [ Open] here", "bracketed capitalized"),
]
FREE_SLOT_FINE = [
    "H2a and H3c are inconclusive, so the picture is mixed.",
    "These notes provide some context for the table.",
    "A [lowercase bracket] and a (parenthesis) are allowed.",
    "- a list item\n- another list item",
    "A line\n\nAnother line after a blank line",
    "Three words - separated by a dash - on one line",
    "I improved my plots and Approved is not a stem.",
    "R\u00f6ssler and Chua behave alike, and the \u0141ukasiewicz note is fine.",
    "- [x] read the table\n- [a lowercase bracket] stays",
    "the developer wrote it and it was done",
]


def test_free_slot_stems_and_brackets_name_their_reason() -> None:
    """Prefix stems and bracket tokens fail for the intended reason (N4).

    Reference: typed here by hand. Each text holds no digit, no heading and
    no whole-word refusal, so the only rule that can refuse it is the one
    named in the second column. The controls must pass every rule, which
    shows that the stems are not so broad that plain words are refused.
    """
    for text, reason in FREE_SLOT_REASONS + HIDING:
        lines = [(5 + k, t, False) for k, t in enumerate(text.split("\n"))]
        problems = fb.check_free_slots(lines, CONSTANTS, None)
        assert any(reason in p for p in problems), (text, problems)
    for text in FREE_SLOT_FINE:
        lines = [(5 + k, t, False) for k, t in enumerate(text.split("\n"))]
        assert fb.check_free_slots(lines, CONSTANTS, None) == [], text


def test_setext_heading_names_its_line() -> None:
    """A line followed by a line of only = or - is a heading and is refused (N4).

    Reference: CommonMark's definition of a setext heading, typed by hand.
    The message names the document line of the text, and the underline of a
    paragraph that is a list item or a blank line is not a heading.
    """
    for under in ("=", "=====", "---", "-", "  ===  "):
        free = [(8, "Verdicts", False), (9, under, False)]
        problems = fb.check_free_slots(free, CONSTANTS, None)
        assert problems and problems[0].startswith("line 8: setext"), under
    blank = [(8, "Verdicts", False), (9, "", False), (10, "---", False)]
    assert fb.check_free_slots(blank, CONSTANTS, None) == []


def test_dated_line_after_today_is_refused() -> None:
    """A dated line later than the day ``check`` runs is refused (N4).

    The day is passed in, so the test does not depend on the clock; the same
    line is accepted on its own day and refused the day before.
    """
    free = [(7, "- 2026-10-20: agreed", True)]
    on_day = fb.check_free_slots(
        free, CONSTANTS, None, today=date(2026, 10, 20)
    )
    assert on_day == []
    before = fb.check_free_slots(
        free, CONSTANTS, None, today=date(2026, 10, 19)
    )
    assert len(before) == 1 and "after today" in before[0]
    assert before[0].startswith("line 7:")
    # The default day is the real one: a date long in the future is refused.
    far = [(7, "- 2099-12-31: agreed", True)]
    assert any(
        "after today" in p for p in fb.check_free_slots(far, CONSTANTS, None)
    )
    # The old rule still holds: before the end of the official run.
    early = [(7, "- 2026-01-01: agreed", True)]
    problems = fb.check_free_slots(early, CONSTANTS, date(2026, 1, 2))
    assert any("before the run ended" in p for p in problems)


def test_docstring_states_the_limits() -> None:
    """The module docstring quotes the stems and states the residual limits.

    N1: the empty-listing residual and the rerun-and-diff step; N2: the git
    check and that nothing more is verified; N3: the absolute-path rule; N4:
    the stems and the limits of the free-slot rules.
    """
    doc = " ".join(fb.__doc__.split())
    for stem in CONSTANTS["free_slot_stems"]:
        assert stem in doc, stem
    for phrase in (
        "empty or deleted",
        "rerun ``compare_runs`` on the released directories and diff",
        "WU-0020.8",
        "git diff --name-only",
        "does not verify the commit difference",
        "absolute paths",
        "realpath only",
        "Number words",
        "reads every claim",
        "date.today()",
    ):
        assert phrase in doc, phrase


# --- the cross-check commit (N2) ---------------------------------------------
def conf_with_commits(tmp: Path, monkeypatch, changed):
    """Render a confirmatory pair whose cross-check commit differs.

    ``changed`` is the stubbed answer of ``git_changed_paths`` (a list), or an
    exception to raise; the stub records its calls.
    """
    calls = []

    def stub(root, old, new):
        calls.append((old, new))
        if isinstance(changed, Exception):
            raise changed
        return list(changed)

    monkeypatch.setattr(fb, "git_changed_paths", stub)
    out = conf_render(
        tmp, monkeypatch, None, lambda p: p.update(commit="d" * 40)
    )
    return out, calls


def test_later_cross_check_commit_must_change_only_records(
    tmp_path, monkeypatch
) -> None:
    """A differing cross-check commit is allowed only for records and the ledger (N2).

    The git call is stubbed (the answer is typed here). Accepted: a diff of
    records files and the ledger only (and an empty diff). Refused: a diff that
    touches ``lpcstudy/`` or any path that only looks like a record path
    (a sibling directory, a suffix of the ledger name), and a failing git.
    """
    (args, code), calls = conf_with_commits(
        tmp_path / "ok",
        monkeypatch,
        [
            "docs/agent/records/work/WU-0020.md",
            "docs/agent/governance/ledger.jsonl",
        ],
    )
    assert code == 0 and calls == [("c" * 40, "d" * 40)] * 2  # render, check
    text = doc_of(Path(args.out))
    assert "(same as official: no)" in text
    assert (
        "lists 2 path(s), all under docs/agent/records/ or the ledger" in text
    )
    (args, code), _ = conf_with_commits(tmp_path / "empty", monkeypatch, [])
    assert code == 0
    refused = [
        ["lpcstudy/data.py"],
        ["docs/agent/records/x.md", "lpcstudy/statistics.py"],
        ["docs/agent/records-extra/x.md"],
        ["docs/agent/governance/ledger.jsonl.bak"],
        ["docs/agent/governance/other.md"],
        ["tools/findings_build.py"],
        ["../docs/agent/records/x.md"],
    ]
    for k, paths in enumerate(refused):
        reason = "'..' component" if ".." in paths[0] else "outside"
        with pytest.raises(fb.ToolError, match=reason):
            conf_with_commits(tmp_path / f"r{k}", monkeypatch, paths)
    with pytest.raises(fb.ToolError, match="cannot list"):
        conf_with_commits(
            tmp_path / "fail", monkeypatch, fb.ToolError("cannot list: no git")
        )

    # The same commit needs no git call at all.
    def never(root, old, new):
        raise AssertionError("git must not be called for one commit")

    monkeypatch.setattr(fb, "git_changed_paths", never)
    args, code = conf_render(tmp_path / "same", monkeypatch)
    assert code == 0
    assert "not needed (the same commit)" in doc_of(Path(args.out))


def test_changed_paths_helper_refuses_when_git_cannot_answer(
    tmp_path, monkeypatch
) -> None:
    """The git helper turns every failure into ``ToolError`` (N2).

    Reference: real git on this repository. An empty diff of a commit with
    itself lists nothing; an unknown commit, a failing subprocess, a missing
    git program and a commit string that is not 40 hex digits (which could
    be read as an option) are all refused.
    """
    head = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert fb.git_changed_paths(ROOT, head, head) == []
    assert fb.check_later_commit(ROOT, head, head).startswith("git diff")
    with pytest.raises(fb.ToolError, match="cannot list"):
        fb.git_changed_paths(ROOT, "0" * 40, head)
    with pytest.raises(fb.ToolError, match="cannot list"):
        fb.git_changed_paths(tmp_path, head, head)  # not a repository
    for bad in ("--output=x", "main", "d" * 39, "D" * 40, None):
        with pytest.raises(fb.ToolError, match="40 hex"):
            fb.check_later_commit(ROOT, bad, head)
        with pytest.raises(fb.ToolError, match="40 hex"):
            fb.check_later_commit(ROOT, head, bad)

    def missing(*a, **k):
        raise FileNotFoundError("git")

    monkeypatch.setattr(fb.subprocess, "run", missing)
    with pytest.raises(fb.ToolError, match="cannot run git"):
        fb.git_changed_paths(ROOT, head, head)


# --- the working directory (N3) ----------------------------------------------
def test_check_does_not_depend_on_the_working_directory(
    tmp_path, monkeypatch
) -> None:
    """An unaltered document passes ``check`` from any directory (N3).

    The committed dry-run text prints its REF and NEW lines relative to the
    directory it was made in. Here the fixture does the same: it is built
    from inside ``tmp_path`` with relative REF and NEW paths, then checked from
    a different directory. The recorded ``cwd`` is what the relative paths are
    read against, so the answer is the same. Without the record the paths
    would be read against the new directory and fail to bind.
    """
    text = make_td().replace("REFDIR", "official").replace("NEWDIR", "cross")
    args = render_args(tmp_path, td=text)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(tmp_path)
    with stub_figures():
        assert fb.render(args) == 0
    out = Path(args.out)
    record = json.loads((out / "doc.sources.json").read_text())
    assert record["cwd"] == str(tmp_path.resolve())
    assert all(Path(p).is_absolute() for p in record["files"].values())
    assert "(by realpath and realpath)" in doc_of(out)
    monkeypatch.chdir(elsewhere)
    with stub_figures():
        assert fb.run_check(out, "doc", {}) == 0
        assert fb.main(["check", str(out), "--stem", "doc"]) == 0
        # A record that names another directory cannot bind the relative path.
        record["cwd"] = str(elsewhere)
        (out / "doc.sources.json").write_text(json.dumps(record))
        with pytest.raises(fb.ToolError, match="do not name"):
            fb.run_check(out, "doc", {})
        del record["cwd"]
        (out / "doc.sources.json").write_text(json.dumps(record))
        with pytest.raises(fb.ToolError, match="no cwd"):
            fb.run_check(out, "doc", {})


def test_confirmatory_build_needs_absolute_paths(tmp_path, monkeypatch) -> None:
    """A confirmatory build refuses relative paths and binds by realpath only (N3).

    Refused: a relative ``--official``, ``--crosscheck`` or ``--td``; REF and
    NEW lines that are relative; REF and NEW under another prefix with the
    same last two path components (the development fallback); a REF that is
    a symbolic link or has a ``..`` component (it must be its own realpath).
    Accepted: the real paths, and then ``check`` passes from other
    directories.
    """
    monkeypatch.setattr(fb, "git_freeze_commit", lambda root: "c" * 40)
    official = make_results("confirmatory")
    cross = make_results("confirmatory", backend="gpu")

    def args_for(name: str, td: str | None = None) -> Namespace:
        base = tmp_path / name
        args = render_args(base, official=official, cross=cross, td=td)
        args.release_ref = "ledger-seq-3"
        args.manifest_official = fb.sha256_of(
            base / "official" / "results.json"
        )
        args.manifest_official_md = fb.sha256_of(
            base / "official" / "RESULTS.md"
        )
        args.manifest_crosscheck = fb.sha256_of(base / "cross" / "results.json")
        return args

    for k, field in enumerate(("official", "crosscheck", "td")):
        args = args_for(f"rel{k}")
        monkeypatch.chdir(tmp_path / f"rel{k}")
        setattr(args, field, os.path.relpath(getattr(args, field)))
        assert not Path(getattr(args, field)).is_absolute()
        with pytest.raises(fb.ToolError, match=f"absolute path for {field}"):
            fb.render(args)
    relative = (
        make_td().replace("REFDIR", "official").replace("NEWDIR", "cross")
    )
    args = args_for("reltext", relative)
    monkeypatch.chdir(tmp_path / "reltext")
    with pytest.raises(fb.ToolError, match="absolute REF and NEW"):
        fb.render(args)
    args = args_for("prefix")
    # Same last two components as the real directories: development binds it.
    real = tmp_path / "prefix"
    moved = make_td().replace("REFDIR", f"/other/{real.name}/official")
    moved = moved.replace("NEWDIR", f"/other/{real.name}/cross")
    (real / "td.txt").write_text(moved)
    with pytest.raises(fb.ToolError, match="do not name"):
        fb.render(args)
    # Through a symbolic link: the realpath is the official directory.
    args = args_for("link")
    base = tmp_path / "link"
    (base / "alias").symlink_to(base / "official", target_is_directory=True)
    for odd in (str(base / "alias"), f"{base}/official/../official"):
        text = make_td().replace("REFDIR", odd)
        (base / "td.txt").write_text(
            text.replace("NEWDIR", str(base / "cross"))
        )
        with pytest.raises(fb.ToolError, match="own realpath"):
            fb.render(args)  # a printed link or '..' path does not bind
    text = make_td().replace("REFDIR", str(base / "official"))
    (base / "td.txt").write_text(text.replace("NEWDIR", str(base / "cross")))
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    with stub_figures():
        assert fb.render(args) == 0
        out = Path(args.out)
        record = json.loads((out / "doc.sources.json").read_text())
        assert all(Path(p).is_absolute() for p in record["files"].values())
        monkeypatch.chdir(tmp_path)
        assert fb.run_check(out, "doc", {}) == 0
        monkeypatch.chdir(base)
        assert fb.main(["check", str(out), "--stem", "doc"]) == 0
        # A relative override is refused in a confirmatory check.
        with pytest.raises(fb.ToolError, match="absolute path for td"):
            fb.run_check(out, "doc", {"td": "td.txt"})


# --- V1, V6, V7: the changed-path check against real git ------------------------
def git_repo(tmp: Path):
    """Make a throwaway repository; return a function that runs git in it."""
    tmp.mkdir(parents=True)

    def git(*args: str) -> str:
        return subprocess.run(
            [
                "git",
                "-c",
                "user.name=t",
                "-c",
                "user.email=t@example.org",
                "-c",
                "commit.gpgsign=false",
                *args,
            ],
            cwd=tmp,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

    git("init", "-q")
    return git


def commit_files(git, root: Path, files: dict[str, str], message: str) -> str:
    """Write files (a ``None`` content removes one), commit, return the hash."""
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    git("add", "-A")
    git("commit", "-q", "-m", message)
    return git("rev-parse", "HEAD")


def test_renames_out_of_code_are_refused_with_real_git(tmp_path) -> None:
    """A move into the records lists the old path too and is refused (V1).

    Reference: real git in a throwaway repository, with git's default rename
    detection on. ``git mv`` of a file out of ``lpcstudy/``, ``seeds/`` or
    ``tools/`` into ``docs/agent/records/`` is refused, with and without an
    edit of the content (a rename with a small edit is still detected as a
    rename), while a records edit, a ledger edit and a move inside the
    records pass.
    """
    root = tmp_path / "repo"
    git = git_repo(root)
    body = "".join(f"line {k} of a source file\n" for k in range(40))
    base = commit_files(
        git,
        root,
        {
            "lpcstudy/core.py": body,
            "lpcstudy/core2.py": body + "extra\n",
            "seeds/dev.txt": body + "seed\n",
            "tools/t.py": body + "tool\n",
            "docs/agent/records/a.md": "a\n" + body,
            "docs/agent/governance/ledger.jsonl": "{}\n",
        },
        "base",
    )
    moves = {
        "lpcstudy": "lpcstudy/core.py",
        "seeds": "seeds/dev.txt",
        "tools": "tools/t.py",
    }
    for edit in (False, True):
        for key, source in moves.items():
            git("checkout", "-q", "-B", f"b-{key}-{edit}", base)
            git("mv", source, f"docs/agent/records/{key}-moved.py")
            if edit:
                moved = root / f"docs/agent/records/{key}-moved.py"
                moved.write_text(moved.read_text() + "# edited\n")
            git("add", "-A")
            git("commit", "-q", "-m", "move")
            head = git("rev-parse", "HEAD")
            # git's own rename detection sees one rename ...
            assert git("diff", "--name-status", f"{base}..{head}").startswith(
                "R"
            )
            # ... and the tool still lists both paths and refuses.
            assert source in fb.git_changed_paths(root, base, head)
            with pytest.raises(fb.ToolError, match="outside"):
                fb.check_later_commit(root, base, head)
    ok = {
        "records edit": {"docs/agent/records/a.md": "changed\n"},
        "ledger edit": {"docs/agent/governance/ledger.jsonl": "{}\n{}\n"},
        "new record": {"docs/agent/records/new.md": "new\n"},
    }
    for name, files in ok.items():
        git("checkout", "-q", "-B", name.replace(" ", "-"), base)
        head = commit_files(git, root, files, name)
        assert fb.check_later_commit(root, base, head).startswith("git diff")
    git("checkout", "-q", "-B", "inner", base)
    git("mv", "docs/agent/records/a.md", "docs/agent/records/b.md")
    git("commit", "-q", "-m", "inner move")
    inner = git("rev-parse", "HEAD")
    assert sorted(fb.git_changed_paths(root, base, inner)) == [
        "docs/agent/records/a.md",
        "docs/agent/records/b.md",
    ]
    assert fb.check_later_commit(root, base, inner).startswith("git diff")


def test_path_that_is_not_utf8_is_a_reported_refusal(tmp_path) -> None:
    """A changed path of invalid UTF-8 gives ``ToolError``, not a traceback (V6).

    Reference: real git; the file name holds the byte 0xff, written through a
    bytes path.
    """
    root = tmp_path / "repo"
    git = git_repo(root)
    base = commit_files(git, root, {"docs/agent/records/a.md": "a\n"}, "base")
    folder = os.fsencode(root / "docs/agent/records")
    with open(folder + b"/bad\xff.md", "w") as handle:
        handle.write("x\n")
    git("add", "-A")
    git("commit", "-q", "-m", "bad name")
    head = git("rev-parse", "HEAD")
    with pytest.raises(fb.ToolError, match="not valid UTF-8"):
        fb.git_changed_paths(root, base, head)
    with pytest.raises(fb.ToolError, match="not valid UTF-8"):
        fb.check_later_commit(root, base, head)


def test_dotdot_paths_and_trailing_newline_commits_are_refused(
    monkeypatch,
) -> None:
    """A ``..`` component is refused and a commit needs a full match (V7).

    The helper is stubbed to print a path that real git never prints, so the
    guard is tested on its own.
    """
    monkeypatch.setattr(
        fb,
        "git_changed_paths",
        lambda root, old, new: ["docs/agent/records/../../lpcstudy/x.py"],
    )
    with pytest.raises(fb.ToolError, match=r"'\.\.' component"):
        fb.check_later_commit(ROOT, "a" * 40, "b" * 40)
    with pytest.raises(fb.ToolError, match="40 hex"):
        fb.check_later_commit(ROOT, "a" * 40 + "\n", "b" * 40)
    assert not fb.FULL_COMMIT.fullmatch("a" * 40 + "\n")


# --- WU-0020.8 fix round 1 (R1 to R10 of the review of the sealed document) --
DECISIONS = ROOT / "docs/agent/records/decisions.md"
DEFECTS = ROOT / "docs/agent/records/defects.md"
LM_REPORT = ROOT / "docs/study/lm_doubling_dev0_report_v3.md"


def line_of(text: str, start: str) -> str:
    """Return the first line of a document that starts with ``start``."""
    return next(x for x in text.split("\n") if x.startswith(start))


def test_q_n_row_shows_both_readings_and_labels_the_stored_word(
    tmp_path,
) -> None:
    """R1: the overall Q-N row has both stored readings per system.

    Planted (not computed): the logit reading is "reduces" on lorenz63 and
    "substantial" on rossler, and the indicator reading is "substantial" on
    lorenz63 and "reduces" on rossler; the stored per-system words of
    ``verdicts.Q-N`` are planted as "reduces". Reference: the planted leaves
    and the v3 text, which says Q-N is read separately for its two parts.
    """
    results = make_results()
    logit, indicator = CONSTANTS["qn_parts"][:2]
    assert logit["verdict"] == "Q-N/oracle/logit_w_interior/reading"
    assert indicator["verdict"] == "Q-N/oracle/w_zero_indicator/reading"
    block = results["systems"]
    set_path(block["lorenz63"], logit["verdict"], "reduces")
    set_path(block["lorenz63"], indicator["verdict"], "substantial")
    set_path(block["rossler"], logit["verdict"], "substantial")
    set_path(block["rossler"], indicator["verdict"], "reduces")
    results["verdicts"]["Q-N"] = {
        "by_system": {s: "reduces" for s in SYSTEMS},
        "verdict": "estimate (read, no pass/fail)",
    }
    out = fast_build(tmp_path, official=results)
    text = doc_of(out)
    row = line_of(text, "| Q-N | estimate |")
    cells = [c.strip() for c in row.split("|")[3:6]]
    assert cells[0] == "logit: reduces; indicator: substantial"
    assert cells[1] == "logit: substantial; indicator: reduces"
    assert "the stored per-system words are the logit part only" in row
    assert (
        "stored overall word `verdicts.Q-N` collapses them to the logit part"
        in text
    )
    assert (
        "its per-system words are lorenz63 reduces, rossler reduces, chua reduces"
        in text
    )
    assert (
        "separately for its two parts" in v3_text()
        or "read separately" in v3_text()
    )
    paths = {r["path"] for r in trace_of(out) if r["source"] == "official"}
    for s in SYSTEMS:
        assert f"systems/{s}/{logit['verdict']}" in paths
        assert f"systems/{s}/{indicator['verdict']}" in paths
        assert f"verdicts/Q-N/by_system/{s}" in paths


def test_is_word_key_equals_the_compare_runs_rule() -> None:
    """The verdict-word key rule is the one of ``tools/compare_runs.py``.

    Reference: ``compare_runs.is_verdict_str`` on keys typed here, both the
    ones that count and ones that look alike.
    """
    spec = importlib.util.spec_from_file_location(
        "compare_runs_ref", ROOT / "tools" / "compare_runs.py"
    )
    cr = importlib.util.module_from_spec(spec)
    sys.modules["compare_runs_ref"] = cr
    spec.loader.exec_module(cr)
    keys = [
        "verdict", "verdict_2L", "part_i_verdict", "part_ii_verdict",
        "reading", "status", "reason", "verdicts", "my_verdict_x", "pass",
        "role", "Verdict", "readings", "statuses", "",
    ]  # fmt: skip
    for key in keys:
        assert fb.is_word_key(key) == cr.is_verdict_str(key), key


def test_cross_check_lists_every_differing_verdict_word(tmp_path) -> None:
    """R2: a table of the stored words that differ, in the stated order.

    Planted: overall H2c, a primary by-system word (H2a rossler) and a
    secondary one (H1a chua) differ; lorenz63 has a primary part word (H3c),
    a clip-sensitivity word (generic key ``verdict_2L``) that differ;
    chua has a word that exists in the cross-check only and an H2d word.
    Expected order, typed by hand from the rule "overall first, primary
    hypotheses first; then each system, primary parts first, then the rest".
    Words equal in the two files must not be listed. The words are shown as
    stored (the intervals contradict some of them on purpose).
    """
    official, cross = make_results(), make_results(backend="gpu")
    h3c = CONSTANTS["primary_parts"][5]["verdict"]
    h2d = next(p for p in CONSTANTS["secondary_parts"] if p["name"] == "H2d")
    clip = "clip_sensitivity/by_hypothesis/H2a/parts/zero/verdict_2L"
    cross["verdicts"]["H2c"]["verdict"] = "not supported"
    cross["verdicts"]["H2a"]["by_system"]["rossler"] = "fail"
    cross["verdicts"]["H1a"]["by_system"]["chua"] = "inconclusive"
    set_path(official["systems"]["lorenz63"], h3c, "inconclusive")
    set_path(cross["systems"]["lorenz63"], h3c, "pass")
    for run, word in ((official, "pass"), (cross, "fail")):
        set_path(run["systems"]["lorenz63"], clip, word)
    set_path(cross["systems"]["chua"], "H2b/extra_verdict", "fail")
    set_path(official["systems"]["chua"], h2d["verdict"], "pass")
    set_path(cross["systems"]["chua"], h2d["verdict"], "fail")
    set_path(cross["systems"]["rossler"], "H3a/chosen_K", 3)
    overall, per_system = fb.differing_words(official, cross, CONSTANTS)
    assert ["/".join(p) for p in overall] == [
        "verdicts/H2a/by_system/rossler",
        "verdicts/H1a/by_system/chua",
        "verdicts/H2c/verdict",
    ]
    assert ["/".join(p) for p in per_system] == [
        "systems/lorenz63/H3c/verdict",
        f"systems/lorenz63/{clip}",
        "systems/chua/H2b/extra_verdict",
        "systems/chua/H2d/verdict",
    ]
    out = fast_build(tmp_path, official=official, cross=cross)
    text = doc_of(out)
    assert (
        "| H2c/verdict | supported (preliminary, unpromoted) | not supported |"
        in text
    )
    assert "| H2a/by_system/rossler | pass | fail |" in text
    assert "| lorenz63 | H3c/verdict | inconclusive | pass |" in text
    assert f"| lorenz63 | {clip} | pass | fail |" in text
    assert "| chua | H2b/extra_verdict | not recorded | fail |" in text
    assert "| chua | H2d/verdict | pass | fail |" in text
    assert "Overall rows: 3. Rows per system: 4." in text
    assert "| rossler | 2 | 3 |" in text
    assert "H2b/verdict" not in text.split("## 8.")[1].split("## 9.")[0]
    assert "(1 lines against 2 verdict-type leaves counted" in text
    assert CONSTANTS["constants"]["dec28_item4"]["text"] in text
    # Primary overall rows come before the others, in the document too.
    section = text.split("## 8.")[1]
    assert section.index("H2a/by_system/rossler") < section.index(
        "H1a/by_system/chua"
    )
    assert section.index("H3c/verdict") < section.index(clip)
    assert section.index(clip) < section.index("H2b/extra_verdict")
    rows = trace_of(out)
    words = [r for r in rows if r["source"] == "official_words"]
    assert words and {r["tag"] for r in words} == {"CROSS-CHECK"}


def test_no_differing_word_is_said_plainly(fast) -> None:
    """With identical words in both files the document says none differs."""
    text = doc_of(fast)
    assert "No overall stored verdict word differs." in text
    assert "No stored verdict word of a system differs." in text
    assert "Overall rows: 0. Rows per system: 0." in text


def test_decision_sentence_is_quoted_from_decisions_md() -> None:
    """The DEC-0028 item 4 sentence is the one in the decision record.

    Reference: ``docs/agent/records/decisions.md``, DEC-0028 item 4: "What a
    TD pass does not mean. It does not reproduce verdicts or the gate
    outcome."
    """
    record = DECISIONS.read_text()
    start = record.index("## DEC-0028")
    item = record[start : record.index("**Evidence", start)]
    assert "4. **What a TD pass does not mean.**" in item
    assert "It does not reproduce verdicts or the gate outcome." in item
    cited = CONSTANTS["constants"]["dec28_item4"]
    assert cited["text"] == (
        "What a TD pass does not mean: it does not reproduce verdicts or the "
        "gate outcome."
    )
    assert "DEC-0028 item 4" in cited["v3"]


def test_cross_check_sentences_follow_the_tokens(tmp_path) -> None:
    """R3: one sentence per condition, each as stored; no fixed disjunction.

    Conditions: (a) the failing-part token "0" or not, (b) the differing
    count (a number, "none listed" or "not available"), (c) the GPU gate of
    each system. Reference: the planted tokens of ``make_td`` and the planted
    ``gate_pass`` flags.
    """
    fast_text = doc_of(fast_build(tmp_path / "ok"))
    assert (
        "No primary part exceeds the bound: failing parts 0, largest z (away) "
        "1.23, bound 3.4." in fast_text
    )
    assert (
        "Verdict-type leaves that differ between the two runs: 2." in fast_text
    )
    assert "The GPU validation gate passed on every system." in fast_text
    assert "At least one primary part exceeds the bound" not in fast_text
    assert "a verdict-type leaf differs or a GPU gate failed" not in fast_text
    td = make_td(result="FAIL").replace(
        "failing parts (z_away > 3.4) 0", "failing parts (z_away > 3.4) 2"
    )
    cross = make_results(gate={"rossler": False, "chua": False}, backend="gpu")
    bad_text = doc_of(fast_build(tmp_path / "bad", td=td, cross=cross))
    assert (
        "At least one primary part exceeds the bound: failing parts 2"
        in bad_text
    )
    assert "No primary part exceeds the bound" not in bad_text
    assert "The GPU validation gate did not pass on rossler, chua" in bad_text
    assert (
        "GPU validation gate, stored gate_pass: lorenz63 yes, rossler no, chua no."
        in bad_text
    )
    assert "The GPU validation gate passed on every system." not in bad_text
    assert "compare_runs result: FAIL (exit 0)." in bad_text
    caption = CONSTANTS["constants"]["caption_F3"]["text"]
    assert "A row would name a failed GPU validation gate" in caption
    assert "Each row names" not in caption


def test_lm_limitation_states_the_corrected_count() -> None:
    """R4: the DEF-0027 limitation reads as RESULTS.md and the record do.

    Reference: the DEF-0027 correction of 2026-10-18 in ``defects.md`` and
    ``docs/study/lm_doubling_dev0_report_v3.md``: N 5 / X 6 / U 7; the LM-row
    flag (class N) is yes for 5 of 18 parts and no for 13.
    """
    defects, report = DEFECTS.read_text(), LM_REPORT.read_text()
    assert "total N 5 / X 6 / U 7" in defects
    assert "yes for 5 of 18 parts, no for 13" in report
    assert "N 5 / X 6 / U 7" in report
    cited = CONSTANTS["constants"]["lm_limitation"]
    text = cited["text"]
    assert "for 5 of the 18 primary parts (class N)" in text
    assert "did not show it below 10% for the other 13" in text
    assert "not negligible, 6" in text and "not certified, 7" in text
    assert "stated and not applied" in text
    assert "referred to the owner" in cited["v3"]
    assert (
        ROOT / CONSTANTS["constants"]["lm_report_pointer"]["text"]
    ).is_file()
    assert "flag was raised" not in json.dumps(CONSTANTS)


def test_lm_limitation_and_pointer_are_in_the_document(fast) -> None:
    """R4: the limitation and the pointer are in §10 and under the primary table."""
    text = doc_of(fast)
    pointer = CONSTANTS["constants"]["lm_report_pointer"]["text"]
    limits = text.split("## 10.")[1].split("## 11.")[0]
    assert pointer in limits and "not negligible, 6" in limits
    primary = text.split("## 5.")[1].split("## 6.")[0]
    assert pointer in primary
    assert len([x for x in text.split("\n") if "LM iteration" in x]) == 18


# Typed from the Handling section of the real RESULTS.md (table of result
# counts of one system), not built from the constants.
RESULT_COUNT_LEAVES = [
    "H1b/CP/n_floored",
    "H2a/n_excluded_states",
    "H1c/PLP/n_ineligible_states",
    "H1c/CP/n_ineligible_states",
    "H2b/noise/n_constant_states",
    "gain_bound/n_screened_out/growth_nonpositive",
    "gain_bound/n_screened_out/negative_covariance",
    "gain_bound/n_screened_out/censored_single_forecaster",
]


def test_handling_section_names_its_scope_and_lists_result_counts(fast) -> None:
    """R5: the heading sentence is not complete and the counts are traced.

    Planted values: ``100 * system_index + position`` (the first count is 0,
    100, 200, so a zero is printed). Reference: the typed leaf list above and
    the planted values.
    """
    assert [
        i["leaf"] for i in CONSTANTS["result_counts"]
    ] == RESULT_COUNT_LEAVES
    text = doc_of(fast)
    section = text.split("## 7.")[1].split("## 8.")[0]
    assert "Every clip, floor, replacement and fallback" not in text
    assert "handling counters of the main systems" in section
    assert "`handling.robustness`" in section
    assert "Handling section of RESULTS.md" in section
    assert "Robustness variants not run (skipped_variants): 0." in section
    for k, leaf in enumerate(RESULT_COUNT_LEAVES):
        row = f"| {leaf} | {k} | {100 + k} | {200 + k} |"
        assert row in section, row
    paths = {r["path"] for r in trace_of(fast) if r["source"] == "official"}
    assert "handling/skipped_variants" in paths
    assert "systems/chua/H1b/CP/n_floored" in paths


# Typed from the real results.json (leaf names printed by walking it).
REPORTED_LEAVES = [
    ("H2a/n_excluded_states", None),
    ("H2a/n_eligible_states", None),
    ("H2a/range_by_span/1-2/median", None),
    ("H2a/range_by_span/1-2/n_states", None),
    ("H2a/range_by_span/1-2-4/median", None),
    ("H2a/range_by_span/1-2-4/n_states", None),
    ("H2a/complete_case/median_range", "H2a/complete_case/range_ci"),
    ("H2a/complete_case/n_states", None),
    ("H2a/n_w_zero", None),
    ("H2a/n_w_one", None),
    ("H1a/by_noise/0.01/floor_rms", None),
    ("H1a/by_noise/0.02/floor_rms", None),
    ("H1c/CP/median_ratio", "H1c/CP/ci"),
    ("H1d/rows/nhat/spearman", "H1d/rows/nhat/interval"),
    ("H3b/stability", None),
]


def test_reported_quantities_table_and_h2c_label(fast) -> None:
    """R6: reported quantities with no verdict, traced; the H2c label explained.

    Reference: the typed leaf list above; planted values ``7 * system_index +
    position`` for counts that are not also result counts and ``0.25 + 0.01 * position`` for the others, with
    the interval [0.125, 0.375 + 0.01 * position].
    """
    mine = [(q["leaf"], q.get("ci")) for q in CONSTANTS["reported_quantities"]]
    assert mine == REPORTED_LEAVES
    text = doc_of(fast)
    row = line_of(text, "| lorenz63 | H2a: complete-case")
    assert row.endswith("| 0.31 | [0.125, 0.435] |")
    row = line_of(text, "| chua | H2a: test states excluded")
    assert row.endswith("| 201 |  |")  # also a result count: 100 * 2 + 1
    row = line_of(text, "| chua | H2a: test states with w* = 0")
    assert row.endswith("| 22 |  |")  # 7 * 2 + 8
    assert "| lorenz63 | H3b: stability fraction" in text
    assert (
        "The H2c part labelled A4 - A1 is A4 minus the better single forecaster"
        in text
    )
    assert (
        "The stored best_single is lorenz63 A1, rossler A1, chua A1; A1 is PLP alone (w = 0)."
        in text
    )
    assert "A1 | PLP alone" in v3_text()
    assert (
        "better single forecaster, chosen on the calibration split" in v3_text()
    )
    section = text.split("## 6.")[1].split("## 7.")[0]
    assert "Reported quantities that carry no verdict" in section


def test_h2a_bullet_names_failed_parts_and_the_precision_statement(
    tmp_path,
) -> None:
    """R7: which H2a parts failed per system; the v3 precision sentence.

    Planted words: lorenz63 fails only H2a(ii) interior, rossler only H2a(i),
    chua nothing. In a build where chua failed the gate the chua entry carries
    PROVISIONAL. Reference: the planted words and v3 section 7 (Precision).
    """
    official = make_results(gate={"chua": False})
    by_part = {
        "lorenz63": ("pass", "inconclusive", "fail"),
        "rossler": ("fail", "inconclusive", "inconclusive"),
        "chua": ("pass", "pass", "pass"),
    }
    for s, words in by_part.items():
        for part, word in zip(CONSTANTS["primary_parts"][:3], words):
            set_path(official["systems"][s], part["verdict"], word)
    official["verdicts"]["H2a"]["verdict"] = "not supported"
    text = doc_of(fast_build(tmp_path, official=official))
    bullet = line_of(text, "- **H2a**: not supported.")
    assert (
        "Parts whose stored word is fail: lorenz63: H2a(ii) interior (fail); "
        "rossler: H2a(i) (fail); chua PROVISIONAL: none." in bullet
    )
    assert (
        "v3 §7 pre-registered this reading and it is not tested here." in bullet
    )
    sentence = CONSTANTS["constants"]["precision_h2a"]
    assert sentence["text"] in v3_text()
    assert f"Precision (v3 §7, DEF-0022): {sentence['text']}" in bullet
    assert "DEF-0022" in sentence["v3"]


def test_secondary_rows_have_their_own_labelled_block(fast) -> None:
    """R8: H2c is labelled secondary and H2e has a bullet (and H3a)."""
    text = doc_of(fast)
    primary = text.split("Primary hypotheses, stored overall words:")[1]
    primary = primary.split("Secondary rows (v3 §2;")[0]
    assert "- **H2a**:" in primary and "- **H3c**:" in primary
    assert "H2c" not in primary
    block = text.split("Secondary rows (v3 §2;")[1].split("## 5.")[0]
    assert "level 95% with no multiplicity adjustment, v3 §7)" in block
    for key in ("H2c", "H2e", "H3a"):
        assert f"- **{key} (secondary)**:" in block, key
    assert (
        "- **H2e (secondary)**: supported (preliminary, unpromoted)." in block
    )


def test_figure_square_is_named_and_tick_labels_do_not_overlap() -> None:
    """R9: the caption names the square for both uses; no x labels collide.

    Reference: the rendered geometry. Two panels of the kind that overlapped
    in the sealed figure (a range of about 1e-2 and one of about 1e-3, bands
    at zero) are drawn at the real panel width; the bounding boxes of
    neighbouring x tick labels must not intersect. The values are planted
    here, of the same magnitude only.
    """
    caption = CONSTANTS["constants"]["caption_F2"]["text"]
    assert (
        "square a Q-N reading (both readings, the logit part and the indicator part)"
        in caption
    )
    assert "reported with no verdict" in caption
    panels = [
        {
            "name": "tiny one",
            "experiment": "E4",
            "band": [None, 0.0],
            "lines": [],
            "level": "0.95",
            "systems": ["lorenz63"],
            "points": [(0.0041, -0.0035, 0.0162, "inconclusive")],
        },
        {
            "name": "tiny two",
            "experiment": "E4",
            "band": [None, None],
            "lines": [],
            "level": "0.95",
            "systems": ["chua"],
            "points": [(-0.0007, -0.0019, -0.00004, "reported")],
        },
        {
            "name": "tiny three",
            "experiment": "E4",
            "band": [None, 0.0],
            "lines": [],
            "level": "0.95",
            "systems": ["rossler"],
            "points": [(2.1e-05, -2.8e-05, 6.3e-05, "inconclusive")],
        },
    ]
    fig = fb.draw_panels(panels, 5, "L", {s: False for s in SYSTEMS})
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for ax in fig.axes[:3]:
        boxes = sorted(
            (
                t.get_window_extent(renderer)
                for t in ax.get_xticklabels()
                if t.get_text()
            ),
            key=lambda b: b.x0,
        )
        assert len(boxes) >= 2
        for left, right in zip(boxes, boxes[1:]):
            assert left.x1 <= right.x0, ax.get_title()
    plt.close(fig)


def test_hw_ratio_column_is_explained() -> None:
    """R10: the hw ratio is GPU half-width over CPU half-width.

    Reference: ``tools/compare_runs.py``: ``hw0`` is the half-width of the
    reference (first) interval, ``hw1`` of the new one, and the printed
    column is ``hw1 / hw0``; the builder binds REF to the official run and
    NEW to the cross-check (``bind_td``).
    """
    source = " ".join((ROOT / "tools/compare_runs.py").read_text().split())
    assert (
        "hw0, hw1 = 0.5 * (ci0[1] - ci0[0]), 0.5 * (ci1[1] - ci1[0])" in source
    )
    assert 'ratio = p["hw1"] / p["hw0"]' in source
    note = CONSTANTS["constants"]["hw_ratio_note"]["text"]
    assert (
        "half-width of the cross-check (GPU) interval divided by the half-width of the official (CPU) interval"
        in note
    )
    assert "wider" in note


# --- WU-0033: promoted copy --------------------------------------------------
# Reference: a small preliminary document and its promoted copy, both typed by
# hand from the label list of the unit plan (docs/agent/records/work/
# WU-0033-promoted-copy.md); nothing is computed by the code under test.
# Tolerance: byte-exact string equality (no numbers are involved).
PRE_DOC = (
    "**CONFIRMATORY: UNPROMOTED**\n"
    "PRELIMINARY: internal to the owner and the student until promotion "
    "(QA.11, LPC.PC.13).\n"
    "\n"
    "Source: the official CPU run. Verdicts are read from the file.\n"
    "\n"
    "# Preliminary findings for seed CONF-1\n"
    "\n"
    "| Item | Value |\n"
    "|---|---|\n"
    "| Label | CONFIRMATORY: UNPROMOTED |\n"
    "\n"
    "Each cell is the stored word. A \"supported\" verdict is always written "
    "\"supported (preliminary, unpromoted)\". Next sentence.\n"
    "\n"
    "| H2b | primary | pass | supported (preliminary, unpromoted) |\n"
    "- **H2b**: supported (preliminary, unpromoted). Pass on all three "
    "systems in this preliminary, unpromoted run. The value is 0.2437.\n"
)
PROMOTED_DOC = (
    "Source: the official CPU run. Verdicts are read from the file.\n"
    "\n"
    "# Findings for seed CONF-1\n"
    "\n"
    "| Item | Value |\n"
    "|---|---|\n"
    "| Label | CONFIRMATORY: UNPROMOTED |\n"
    "\n"
    "Each cell is the stored word. Next sentence.\n"
    "\n"
    "| H2b | primary | pass | supported |\n"
    "- **H2b**: supported. Pass on all three "
    "systems in this run. The value is 0.2437.\n"
)


def test_promote_text_equals_the_hand_written_copy() -> None:
    """The promoted text is exactly the hand-written expected text."""
    assert fb.promote_text(PRE_DOC) == PROMOTED_DOC
    assert fb.verify_label_diff(PRE_DOC, PROMOTED_DOC) == []


@pytest.mark.parametrize(
    "edit",
    [
        lambda t: t.replace("0.2437", "0.2438"),
        lambda t: t.replace("| pass | supported |", "| pass | inconclusive |"),
        lambda t: t + "An inserted line.\n",
        lambda t: t.replace("Source: the official CPU run.", "Source: x."),
        lambda t: t.replace("\n\n# Findings", "\n# Findings"),
        lambda t: t.replace("# Findings for", "# Preliminary findings for"),
        lambda t: "**CONFIRMATORY: UNPROMOTED**\n" + t,
    ],
    ids=[
        "digit",
        "verdict word",
        "insert",
        "other text",
        "deleted blank line",
        "label restored",
        "banner restored",
    ],
)
def test_any_extra_change_fails_the_label_diff(edit) -> None:
    """A change outside the label rules is reported as a problem."""
    bad = edit(PROMOTED_DOC)
    assert bad != PROMOTED_DOC
    assert fb.verify_label_diff(PRE_DOC, bad) != []


def test_promote_refuses_an_unknown_residual_label() -> None:
    """A label the list does not know makes the promotion fail (no copy)."""
    text = PRE_DOC.replace("Next sentence.", "The run is unpromoted.")
    with pytest.raises(fb.ToolError, match="residual"):
        fb.promote_text(text)


def test_promote_refuses_a_document_without_the_header() -> None:
    """The three header lines must be there."""
    with pytest.raises(fb.ToolError, match="header"):
        fb.promote_text(PRE_DOC.split("\n", 3)[3])


def test_promote_command_leaves_the_input_unchanged(tmp_path: Path) -> None:
    """The command writes only the new path; the input bytes are unchanged."""
    src = tmp_path / "pre.md"
    src.write_text(PRE_DOC)
    before = src.read_bytes()
    out = tmp_path / "promoted.md"
    assert fb.main(["promote", "--document", str(src), "--out", str(out)]) == 0
    assert src.read_bytes() == before
    assert out.read_text() == PROMOTED_DOC
    assert sorted(p.name for p in tmp_path.iterdir()) == [
        "pre.md",
        "promoted.md",
    ]
    # an existing output and the input itself are refused, nothing is written
    assert fb.main(["promote", "--document", str(src), "--out", str(out)]) == 2
    assert fb.main(["promote", "--document", str(src), "--out", str(src)]) == 2
    assert src.read_bytes() == before and out.read_text() == PROMOTED_DOC


def test_promote_command_prints_the_diff_summary(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """The summary names the deleted header lines and the rule counts."""
    src = tmp_path / "pre.md"
    src.write_text(PRE_DOC)
    fb.main(["promote", "--document", str(src), "--out", str(tmp_path / "o.md")])
    said = capsys.readouterr().out
    assert "header lines deleted: 3" in said
    assert "R-WORD: 2 lines" in said and "R-TITLE: 1 lines" in said
    assert "R-RULE: 1 lines" in said and "R-RUN: 1 lines" in said
    assert "residual labels: 1 (kept: provenance label row)" in said
    assert "checked on the bytes read back" in said


def test_promote_command_fails_and_leaves_no_file_on_an_extra_change(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """R1: the command's own check catches a change the rules do not allow.

    The substitution is patched to change one digit as well; the check on the
    bytes read back must fail (exit 1) and the output must be deleted.
    """
    real = fb.promote_lines

    def tampered(text: str, *stems):
        lines, counts = real(text, *stems)
        return [ln.replace("0.2437", "0.2438") for ln in lines], counts

    monkeypatch.setattr(fb, "promote_lines", tampered)
    src = tmp_path / "pre.md"
    src.write_text(PRE_DOC)
    out = tmp_path / "o.md"
    assert fb.main(["promote", "--document", str(src), "--out", str(out)]) == 1
    assert not out.exists()
    assert src.read_text() == PRE_DOC


def _promote_refused(tmp_path: Path, text: str, code: int) -> None:
    src = tmp_path / "pre.md"
    src.write_text(text)
    out = tmp_path / "o.md"
    assert (
        fb.main(["promote", "--document", str(src), "--out", str(out)]) == code
    )
    assert not out.exists()  # nothing written
    assert src.read_text() == text


def test_promote_command_refusals_write_nothing(tmp_path: Path) -> None:
    """R4: header, unmatched-rule and residual-label refusals (exit 2)."""
    _promote_refused(tmp_path, PRE_DOC.split("\n", 3)[3], 2)  # no header
    _promote_refused(
        tmp_path,
        PRE_DOC.replace("Next sentence.", "The run is unpromoted."),
        2,
    )  # residual label
    _promote_refused(
        tmp_path, PRE_DOC.replace("# Preliminary findings", "# Findings"), 2
    )  # R-TITLE matches nowhere


def test_promote_refuses_a_dangling_symlink_output(tmp_path: Path) -> None:
    """R5: the output is opened exclusively; a link is never followed."""
    src = tmp_path / "pre.md"
    src.write_text(PRE_DOC)
    target = tmp_path / "elsewhere.md"
    link = tmp_path / "o.md"
    link.symlink_to(target)
    assert fb.main(["promote", "--document", str(src), "--out", str(link)]) == 2
    assert not target.exists()


# --- WU-0034: promoted figures and pointers ---------------------------------
# References: (1) the committed-style PNGs themselves: the figures of the
# preliminary build are the originals; (2) hand-typed expected texts for the
# two pointer edits; (3) a pixel comparison done here with numpy on arrays read
# by matplotlib's imread, with its own band rule (rows of the first two runs of
# ink rows = the two title lines). Tolerance for pixels: zero (exact equality).
FIG_PRE = (
    PRE_DOC
    + "\n![F1](doc.figures/F1_primary.png)\n\n"
    "Every number quoted above is listed with its source and leaf path in "
    "`doc.trace.csv`. Run the `check` command of `tools/findings_build.py` "
    "on this directory to verify the document against the sources.\n"
)
FIG_PROMOTED = (
    PROMOTED_DOC
    + "\n![F1](out.figures/F1_primary.png)\n\n"
    "Every number quoted above is listed with its source and leaf path in "
    "the trace file of the source document (the version before promotion), "
    "which stays beside that document and not in this directory. The "
    "`check` command of `tools/findings_build.py` verifies the source "
    "document against the sources; it does not apply to this promoted "
    "copy, whose only differences from it are the removed labels, the "
    "three figure links and this sentence.\n"
)


def test_pointer_edits_equal_the_hand_written_copy() -> None:
    """The figure link and the appendix C sentence are rewritten exactly."""
    assert fb.promote_text(FIG_PRE, "doc", "out") == FIG_PROMOTED
    assert fb.verify_label_diff(FIG_PRE, FIG_PROMOTED, "doc", "out") == []
    # an extra change, or a pointer left behind, is a problem
    assert fb.verify_label_diff(
        FIG_PRE, FIG_PROMOTED.replace("out.figures", "other.figures"), "doc", "out"
    )
    assert fb.verify_label_diff(
        FIG_PRE, FIG_PROMOTED.replace("out.figures", "doc.figures"), "doc", "out"
    )
    assert fb.verify_label_diff(
        FIG_PRE, FIG_PROMOTED.replace("three figure links", "two"), "doc", "out"
    )
    assert not re.search(r"\d", fb.TRACE_SENTENCE_NEW)


@pytest.fixture(scope="module")
def conf_built(tmp_path_factory):
    """A confirmatory build with the real figures (original title)."""
    tmp = tmp_path_factory.mktemp("confbuilt")
    mp = pytest.MonkeyPatch()
    mp.setattr(fb, "git_freeze_commit", lambda root: "c" * 40)
    args = conf_args(tmp)
    base = tmp
    args.manifest_official = fb.sha256_of(base / "official" / "results.json")
    args.manifest_official_md = fb.sha256_of(base / "official" / "RESULTS.md")
    args.manifest_crosscheck = fb.sha256_of(base / "cross" / "results.json")
    args.release_ref = "ledger-seq-17"
    assert fb.render(args) == 0
    yield Path(args.out)
    mp.undo()


def _hashes(out: Path) -> dict:
    files = [p for p in sorted(out.rglob("*")) if p.is_file()]
    return {str(p): fb.sha256_of(p) for p in files}


def _title_rows(image) -> int:
    """Own band rule: end row of the second run of rows that have ink."""
    import numpy as np

    ink = ~(image[..., :3] == 1.0).all(axis=-1).all(axis=-1)
    edges = np.flatnonzero(np.diff(np.concatenate(([0], ink.astype(int), [0]))))
    return int(edges[3])  # stop of the second run


def test_original_title_reproduces_the_committed_png_bytes(conf_built) -> None:
    """(i) Re-rendering with the original title gives the same PNG bytes.

    The committed figures were written by the build; ``load_sources`` and a
    Builder with no title override draw them again, and the bytes are equal,
    so the title is the only thing a promoted figure can change.
    """
    _, constants, sources = fb.load_sources(conf_built, "doc", {})
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(fb, "git_freeze_commit", lambda root: "c" * 40)
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            builder = fb.Builder(sources, constants, Path(tmp), "doc")
            for name in ("F1", "F2", "F3"):
                builder.figure(name)
            for stem in fb.FIGURE_FILES:
                new = (Path(tmp) / "doc.figures" / f"{stem}.png").read_bytes()
                old = (conf_built / "doc.figures" / f"{stem}.png").read_bytes()
                assert new == old, stem
    assert fb.run_check(conf_built, "doc", {}) == 0


def test_promote_figures_differ_only_in_the_title_band(
    conf_built, tmp_path
) -> None:
    """(ii), (iii), (v): pixels, words and untouched sources."""
    import numpy as np
    from matplotlib import image as mpimg
    from PIL import Image

    before = _hashes(conf_built)
    out = tmp_path / "report.md"
    assert fb.main(["promote", "--document", str(conf_built / "doc.md"), "--out", str(out)]) == 0
    assert _hashes(conf_built) == before  # (v) nothing of the build changed
    figures = tmp_path / "report.figures"
    assert sorted(p.name for p in figures.iterdir()) == [
        f"{s}.png" for s in fb.FIGURE_FILES
    ]
    text = out.read_text()
    assert "(report.figures/F1_primary.png)" in text
    assert "doc.figures" not in text and "doc.trace.csv" not in text
    for stem in fb.FIGURE_FILES:
        a = mpimg.imread(conf_built / "doc.figures" / f"{stem}.png")
        b = mpimg.imread(figures / f"{stem}.png")
        assert a.shape == b.shape
        band = _title_rows(a)
        assert 20 < band < 80  # the two title lines (measured 48, 66, 53)
        assert np.array_equal(a[band:], b[band:])  # tolerance zero
        assert not np.array_equal(a[:band], b[:band])  # the title changed
        info = Image.open(figures / f"{stem}.png").info
        assert not re.search(
            r"unpromoted|preliminary|confirmatory",
            " ".join(str(v) for v in info.values()),
            re.I,
        )


def test_promoted_figure_texts_hold_no_pre_promotion_word(conf_built) -> None:
    """(iii): every text object of the promoted figures, and the title."""
    banned = re.compile(r"unpromoted|preliminary|confirmatory", re.I)
    assert not banned.search(fb.promoted_title("CONF-1"))
    seen: list[str] = []
    real = fb.save_figure

    def spy(fig, path):
        from matplotlib.text import Text

        seen.extend(t.get_text() for t in fig.findobj(Text))
        real(fig, path)

    _, constants, sources = fb.load_sources(conf_built, "doc", {})
    import tempfile

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(fb, "git_freeze_commit", lambda root: "c" * 40)
        mp.setattr(fb, "save_figure", spy)
        with tempfile.TemporaryDirectory() as tmp:
            builder = fb.Builder(
                sources,
                constants,
                Path(tmp),
                "doc",
                title=fb.promoted_title("CONF-1"),
                figures_dir=Path(tmp) / "f",
            )
            for name in ("F1", "F2", "F3"):
                builder.figure(name)
    assert any("FINDINGS FOR SEED CONF-1" in t for t in seen)
    assert not [t for t in seen if banned.search(t)]


@pytest.mark.parametrize("how", ["raise", "banned word", "moved panel"])
def test_promote_fails_closed_on_a_figure_problem(
    conf_built, tmp_path, monkeypatch, how
) -> None:
    """(iv): no promoted file and no figures directory are left behind."""
    real = fb.draw_panels
    if how == "raise":

        def bad_draw(*a, **k):
            raise RuntimeError("render failure")

        monkeypatch.setattr(fb, "draw_panels", bad_draw)
    elif how == "banned word":
        monkeypatch.setattr(fb, "promoted_title", lambda seed: "UNPROMOTED\nx")
    else:

        def moved(*a, **k):
            fig = real(*a, **k)
            fig.axes[0].set_xlim(-5, 5)  # changes pixels outside the title
            return fig

        monkeypatch.setattr(fb, "draw_panels", moved)
    before = _hashes(conf_built)
    out = tmp_path / "report.md"
    argv = ["promote", "--document", str(conf_built / "doc.md"), "--out", str(out)]
    if how == "raise":
        with pytest.raises(RuntimeError):
            fb.main(argv)
    else:  # a banned word and a moved panel are failed checks (exit 1)
        assert fb.main(argv) == 1
    assert list(tmp_path.iterdir()) == []  # nothing left behind
    assert _hashes(conf_built) == before


def test_promote_leaves_nothing_when_the_final_move_fails(
    conf_built, tmp_path, monkeypatch
) -> None:
    """R2: a move that fails midway leaves no copy and no partial folder."""

    def half_move(src: str, dst: str) -> None:
        Path(dst).mkdir()
        (Path(dst) / "F1_primary.png").write_bytes(b"partial")
        raise OSError("disk full")

    import shutil

    monkeypatch.setattr(shutil, "move", half_move)
    out = tmp_path / "report.md"
    before = _hashes(conf_built)
    with pytest.raises(OSError):
        fb.main(["promote", "--document", str(conf_built / "doc.md"), "--out", str(out)])
    assert list(tmp_path.iterdir()) == []
    assert _hashes(conf_built) == before


def test_promote_reads_the_pointer_edits_from_its_own_table() -> None:
    """R4: the check table holds the two pointer sentences as literals."""
    old, new = fb.allowed_edits("doc", "out")[-1]
    assert old != fb.trace_sentence_old("zzz") and "doc.trace.csv" in old
    assert new == fb.TRACE_SENTENCE_NEW and not re.search(r"\d", new)


def test_promote_needs_the_sources_file_for_the_figures(tmp_path) -> None:
    """A document with image links and no sources file is refused (exit 2)."""
    src = tmp_path / "doc.md"
    src.write_text(FIG_PRE)
    out = tmp_path / "out.md"
    assert fb.main(["promote", "--document", str(src), "--out", str(out)]) == 2
    assert sorted(p.name for p in tmp_path.iterdir()) == ["doc.md"]
    assert fb.main(["promote", "--document", str(src), "--out", str(out), "--no-figures"]) == 0
    assert "(doc.figures/F1_primary.png)" in out.read_text()
