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
import re
import shutil
import sys
from argparse import Namespace
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


def make_results(kind: str = "development", gate: dict | None = None) -> dict:
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
            "device": {"backend": "cpu"},
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
    """Build a compare_runs text with hand-typed z values."""
    lines = [f"tier: {tier} (x)"] if tier else ["mode: --td-only"]
    if differing is not None:
        lines.append(
            f"TD: {differing} verdict-type leaves differ (reported, no failure):"
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
    write_run(tmp / "cross", extra.pop("cross", None) or make_results())
    (tmp / "td.txt").write_text(extra.pop("td", None) or make_td())
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
        tmp, official=official, cross=make_results(gate={"chua": False})
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
    assert CONSTANTS["wording"]["gpu_disagree"] in text
    assert CONSTANTS["wording"]["gpu_agree"] not in text
    assert "differ between the two runs: 0" not in text


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
        cross=make_results("confirmatory"),
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
    mixed = render_args(tmp_path / "d", cross=make_results("confirmatory"))
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
        "gpu agree swapped": swap(wording["gpu_disagree"], wording["gpu_agree"]),
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
    assert CONSTANTS["wording"]["gpu_disagree"] in text
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
