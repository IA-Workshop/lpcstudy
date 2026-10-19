"""Tests of ``tools/findings_build.py``, the builder of the preliminary
findings document (WU-0020.2).

The tool must do three things for the study: copy stored numbers and verdict
words into a short document without changing them, prove that every number
came from a stored file, and refuse to mix the sources that the document's
sections keep apart. A wrong copy here would put a wrong number in front of
the owner and the student, so the tests check the tool against references that
do not come from the tool:

* **Synthetic results with planted values.** ``make_results`` builds a small
  ``results.json`` whose every quoted leaf holds a value chosen by hand (the
  estimate of part ``i`` is ``0.1 + 0.01 i`` with an interval of plus or minus
  0.05). The document, the trace and the figure arrays must show those values.
  Nothing is computed, so the comparison is exact string or float equality.
* **The stored comparison record.** ``docs/agent/records/work/
  WU-0003-9c-compare-R5R6.txt`` is a ``compare_runs`` output written long
  before this tool; its 18 z values, maximum 2.26, sum of squares 15.77 and
  zero failing parts must come out of ``parse_td`` unchanged (A10).
* **The code's own tables.** The identifier list and the part paths in
  ``design_constants.json`` are compared with ``lpcstudy.identifiers`` and
  ``tools/compare_runs.py``, which define them independently.

Tolerances. Every check is exact: formatting a float with a fixed format is
deterministic, so a tolerance would only hide a defect. Each test runs in
a few seconds on a CPU (the three figures take about a second each).
"""

from __future__ import annotations

import copy
import csv
import importlib.util
import json
import re
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
    label = (
        "CONFIRMATORY: UNPROMOTED"
        if kind == "confirmatory"
        else "DEVELOPMENT (DEV-9): not a hypothesis test"
    )
    out = {
        "config": {"core_systems": SYSTEMS},
        "provenance": {
            "seed_id": "CONF-1" if kind == "confirmatory" else "DEV-9",
            "seed_kind": kind,
            "label": label,
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
            reading = part["verdict"].endswith("/reading")
            word = "reduces" if reading else words[(i + n) % 3]
            set_path(block, part["verdict"], word)
        is_pass = gate is None or gate.get(s, True)
        flags = {f"V{k}": True for k in (1, 2, 4, 5, 6, 7)}
        flags["gate_pass"] = is_pass
        validation = block.setdefault("validation", {})
        validation["gate"] = flags
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
        key = item["key"]
        out["verdicts"][key] = {
            "by_system": {s: "pass" for s in SYSTEMS},
            "verdict": "supported",
        }
    return out


def make_markdown(results: dict) -> str:
    """Build a RESULTS.md with the three parts the tool copies."""
    prov = results["provenance"]
    label = prov["label"]
    banner = (
        f"**{label}**"
        if "UNPROMOTED" in label
        else f"**{label}** · **UNPROMOTED**"
    )
    lines = [
        "# Results",
        "",
        banner,
        "",
        "| ID | Hypothesis | a | Verdict | clip |",
    ]
    lines.append("|---|---|---|---|---|")
    for item in CONSTANTS["identifiers"]:
        key = "(reported)" if item["key"] == "gain_bound" else item["key"]
        lines.append(f"| {key} | text 2 | PASS | supported | none 1.5 \\| x |")
    lines += ["", "Interval labels, one per row (procedure):", ""]
    for item in CONSTANTS["identifiers"]:
        key = (
            "(reported)"
            if item["key"] == "gain_bound"
            else (f"{item['key']} ({item['role']})")
        )
        lines.append(f"- {key} — procedure: blocks of 5; level: 95%")
    lines += ["", "## Next"]
    return "\n".join(lines) + "\n"


TD_ROW = "  {s:<9} {p:<20} {d:>8} {zs:>22} {za:>16} {hw:>8}  ok"


def make_td(parts: list[str] | None = None, failing: str = "0") -> str:
    """Build a compare_runs text with hand-typed z values."""
    lines = [
        "tier: TD (x)",
        "TD: 2 verdict-type leaves differ (reported, no failure):",
        "TD statistic: z_level 2.3940, bound 3.4",
        "  system    part                      d z_sym (information) z_away (governs)  hw1/hw0  status",
    ]
    names = parts or [p["name"] for p in CONSTANTS["primary_parts"]]
    for n, s in enumerate(SYSTEMS):
        for k, p in enumerate(names):
            za = f"{0.5 + 0.1 * k + 0.01 * n:.2f}"
            lines.append(
                TD_ROW.format(s=s, p=p, d="0.0100", zs=za, za=za, hw="1.000")
            )
    lines.append(
        "  parts computed 18 of 18 expected (cannot be computed: 0); sum z^2 "
        "away 9.99, symmetric (information) 8.88; max z away 1.23, symmetric "
        f"(information) 1.11; failing parts (z_away > 3.4) {failing}"
    )
    lines.append("RESULT: PASS (exit 0)")
    return "\n".join(lines) + "\n"


def write_run(directory: Path, results: dict) -> Path:
    """Write results.json and RESULTS.md into a run directory."""
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "results.json").write_text(json.dumps(results))
    (directory / "RESULTS.md").write_text(make_markdown(results))
    return directory


def render_args(tmp: Path, **extra) -> Namespace:
    """Arguments of ``render`` over synthetic runs written under ``tmp``."""
    official = extra.pop("official", None) or make_results()
    write_run(tmp / "official", official)
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
        "manifest_crosscheck": None,
    }
    base.update(extra)
    return Namespace(**base)


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    """One full render (with figures and a development appendix)."""
    tmp = tmp_path_factory.mktemp("build")
    args = render_args(tmp)
    write_run(tmp / "dev", make_results())
    args.development = str(tmp / "dev")
    assert fb.render(args) == 0
    return tmp, Path(args.out)


def doc_of(out: Path) -> str:
    return (out / "doc.md").read_text()


def trace_of(out: Path) -> list[dict]:
    with (out / "doc.trace.csv").open(newline="") as handle:
        return list(csv.DictReader(handle))


def fast_render(monkeypatch, tmp: Path, **extra) -> Path:
    """Render with stub figures (for variants that do not test figures)."""
    monkeypatch.setattr(
        fb, "draw_panels", lambda *a, **k: plt.figure(figsize=(1, 1))
    )
    monkeypatch.setattr(
        fb, "draw_crosscheck", lambda *a, **k: plt.figure(figsize=(1, 1))
    )
    args = render_args(tmp, **extra)
    fb.render(args)
    return Path(args.out)


def recheck(out: Path) -> int:
    return fb.run_check(out, "doc", {})


# --- references independent of the tool ---------------------------------
def test_constants_match_code_tables() -> None:
    """The identifier list and part paths equal the code's own tables.

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


def test_fmt_is_deterministic_and_strict() -> None:
    """Formats write the leaf exactly and refuse a wrong type."""
    assert fmt_all() == [
        "0.1235",
        "[0.1, 0.2]",
        "yes",
        "supported (preliminary, unpromoted)",
        "not supported",
        "not computed",
        "7",
    ]
    with pytest.raises(fb.ToolError):
        fb.fmt("text", ".3g")
    with pytest.raises(fb.ToolError):
        fb.fmt(1.5, "d")
    with pytest.raises(fb.ToolError):
        fb.fmt(1.5, "")


def fmt_all() -> list[str]:
    return [
        fb.fmt(0.123456, ".4g"),
        fb.fmt([0.1, 0.2], "ci:.1f"),
        fb.fmt(True, "yn"),
        fb.fmt("supported", "verdict"),
        fb.fmt("not supported", "verdict"),
        fb.fmt(None, ".3g"),
        fb.fmt(7, "d"),
    ]


def test_template_is_number_free() -> None:
    """The template has no numeral outside placeholders and structure (A2)."""
    text = fb.TEMPLATE_PATH.read_text()
    text = fb.PLACEHOLDER.sub(" ", text)
    for line in text.splitlines():
        clean = fb.STRUCTURE.sub(" ", line)
        assert not fb.NUMERAL.search(clean), line


# --- the rendered document -------------------------------------------------
def test_banner_lines_and_check_pass(built) -> None:
    """Line 1 is the label as ``header_lines`` writes it; check passes (A1, A2).

    Reference: the banner strings typed here from the rule of
    ``report.header_lines`` (bold label, plus "· **UNPROMOTED**" unless the
    label already says UNPROMOTED).
    """
    _, out = built
    lines = doc_of(out).split("\n")
    assert lines[0] == DEV_BANNER
    assert lines[1] == fb.PRELIMINARY_LINE
    assert recheck(out) == 0
    conf = make_results("confirmatory")["provenance"]
    assert fb.banner_rule(conf) == "**CONFIRMATORY: UNPROMOTED**"


def test_banner_rule_matches_report_module() -> None:
    """The banner rule equals ``report.header_lines`` on both labels (A1)."""
    sys.path.insert(0, str(ROOT))
    from lpcstudy.report import header_lines

    for kind in ("development", "confirmatory"):
        prov = {**make_results(kind)["provenance"], "config": {}}
        assert fb.banner_rule(prov) == header_lines(prov)[0]


def test_trace_quotes_every_leaf_exactly(built) -> None:
    """Each trace row re-resolves to the planted leaf and its text (A2).

    Reference: the planted values of ``make_results`` (est = 0.1 + 0.01 i
    with i the part index): the rendered estimate of the first primary part
    on lorenz63 is ``format(0.1, ".4g")``.
    """
    _, out = built
    rows = trace_of(out)
    first = CONSTANTS["primary_parts"][0]["estimate"]
    row = next(r for r in rows if r["path"] == f"systems/lorenz63/{first}")
    assert row["rendered"] == format(0.1, ".4g")
    assert row["raw"] == repr(0.1)
    assert all(r["source"] in fb.SOURCES for r in rows)


def test_check_catches_edits(built, tmp_path) -> None:
    """A changed number, a new number or a changed source fails (A2)."""
    _, out = built
    text = doc_of(out)
    first = CONSTANTS["primary_parts"][0]["estimate"]
    row = next(
        r for r in trace_of(out) if r["path"] == f"systems/lorenz63/{first}"
    )
    for k, change in enumerate(
        (
            lambda t: t.replace("| 0.1 |", "| 0.2 |", 1),
            lambda t: t.replace(
                "## 1. The question",
                "## 1. The question\n\nAbout 42 states.",
                1,
            ),
        )
    ):
        bad = tmp_path / f"bad{k}"
        bad.mkdir()
        for f in out.iterdir():
            if f.is_file():
                (bad / f.name).write_text(f.read_text())
        shutil_copy_tree(out / "doc.figures", bad / "doc.figures")
        (bad / "doc.md").write_text(change(text))
        assert row["rendered"] == "0.1"
        assert recheck(bad) == 1


def shutil_copy_tree(src: Path, dst: Path) -> None:
    dst.mkdir(exist_ok=True)
    for f in src.iterdir():
        (dst / f.name).write_bytes(f.read_bytes())


def test_changed_source_is_refused(built, tmp_path) -> None:
    """A results.json edited after the build fails the hash check."""
    tmp, out = built
    record = json.loads((out / "doc.sources.json").read_text())
    path = Path(record["files"]["official"])
    changed = tmp_path / "results.json"
    changed.write_text(path.read_text().replace("0.1", "0.2", 1))
    with pytest.raises(fb.ToolError, match="changed since the build"):
        fb.run_check(out, "doc", {"official": str(changed)})


def test_cross_tag_violation_is_refused(built) -> None:
    """One planted wrong-source row per tag fails the check (A6)."""
    _, out = built
    rows = trace_of(out)
    wrong = {
        "PRE-REGISTERED": "crosscheck",
        "CROSS-CHECK": "official",
        "DEVELOPMENT": "official",
        "DIAGNOSTIC": "crosscheck",
    }
    for tag, source in wrong.items():
        row = next(r for r in rows if r["tag"] == tag)
        changed = [dict(r) for r in rows]
        changed[int(row["id"])]["source"] = source
        problems = fb.check_rows(changed, doc_of(out).split("\n"), rebuilt(out))
        assert any("not allowed" in p for p in problems), tag
    # Development source rows exist only under the DEVELOPMENT tag.
    assert {r["tag"] for r in rows if r["source"] == "dev"} == {"DEVELOPMENT"}
    assert {r["tag"] for r in rows if r["source"] in ("td", "crosscheck")} == {
        "CROSS-CHECK",
        "",
    }


def rebuilt(out: Path) -> dict:
    record = json.loads((out / "doc.sources.json").read_text())
    return fb.rebuild_sources(record, CONSTANTS, {})


def test_student_section_has_no_numbers(built) -> None:
    """The STUDENT section has no placeholders and no numerals (A6)."""
    _, out = built
    text = doc_of(out)
    tags = fb.section_tags(text)
    assert not [r for r in trace_of(out) if r["tag"] == "STUDENT"]
    student = [
        ln for ln, t in zip(text.split("\n"), tags) if t == "STUDENT" and ln
    ]
    assert student and not any(
        fb.NUMERAL.search(fb.STRUCTURE.sub(" ", s)) for s in student
    )


def test_completeness(built) -> None:
    """14 identifiers, 18 primary parts, gate and counters appear (A4, A5).

    Reference: the 14 keys of ``lpcstudy.identifiers`` (via
    ``test_constants_match_code_tables``) and the planted leaves.
    """
    _, out = built
    text = doc_of(out)
    for item in CONSTANTS["identifiers"]:
        assert re.search(
            rf"^\| {re.escape(item['key'])} \| {item['role']} \|", text, re.M
        )
    primary = [
        ln
        for ln in text.split("\n")
        if ln.startswith("| ") and "LM iteration" in ln
    ]
    assert len(primary) == 18
    assert "| error_clips | 0 | 0 | 0 | 0 |" in text
    assert "| nu_cap_clips | 7 | 2 | 2 | 2 |" in text
    assert "Failed robustness variants: 0." in text
    assert "reported, v1 statistic, v3 screen pending" in text
    assert "Every system passed the validation gate" in text
    for check in ("V1", "V2", "V3", "V4", "V5", "V6", "V7"):
        assert f"| lorenz63 | {check} |" in text
    labels = [
        ln
        for ln in text.split("\n")
        if ln.startswith("- ") and "procedure" in ln
    ]
    assert len(labels) == 14


def test_language_rules(built) -> None:
    """No banned phrase in a PRE-REGISTERED section; required text present (A8)."""
    _, out = built
    text = doc_of(out)
    tags = fb.section_tags(text)
    pre = "\n".join(
        ln for ln, t in zip(text.split("\n"), tags) if t == "PRE-REGISTERED"
    ).lower()
    for phrase in CONSTANTS["banned_phrases"]:
        assert phrase not in pre
    assert 'The error of "not supported" is not controlled this way' in text
    assert "supported (preliminary, unpromoted)" in text
    bad = text.replace(
        "## 5. The three", "We note that this proves it.\n\n## 5. The three", 1
    )
    assert any(
        "banned phrase" in p
        for p in fb.check_text(bad.split("\n"), rebuilt(out), trace_of(out))
    )


def test_limitations_keywords_checked(built) -> None:
    """A removed limitation fails the check (A7)."""
    _, out = built
    text = doc_of(out).replace("Doubled thinning", "Other")
    problems = fb.check_text(text.split("\n"), rebuilt(out), trace_of(out))
    assert any("Doubled thinning" in p for p in problems)


def test_missing_leaf_is_counted(monkeypatch, tmp_path) -> None:
    """A missing leaf reads "not recorded" and is counted and listed (PRIME.4)."""
    results = make_results()
    del results["systems"]["chua"]["H3a"]["n_events_per_regime"]
    out = fast_render(monkeypatch, tmp_path, official=results)
    text = doc_of(out)
    assert "not recorded" in text
    assert 'written "not recorded": 2.' in text
    assert "`official:systems/chua/H3a/n_events_per_regime/0`" in text
    assert recheck(out) == 0


def test_no_recomputation(monkeypatch, tmp_path) -> None:
    """The tool imports no verdict function and shows a planted verdict (A3).

    The planted ``H3c`` verdict of lorenz63 is "fail" although its interval
    lies well inside the band (upper bound below 1.05): the document must
    show the stored word, not a recomputed one.
    """
    source = TOOL.read_text()
    for name in ("criterion_verdict", "combine_verdicts", "overall_verdict"):
        assert name not in source
    assert "import lpcstudy" not in source
    assert "from lpcstudy" not in source
    results = make_results()
    leaf = CONSTANTS["primary_parts"][5]
    set_path(results["systems"]["lorenz63"], leaf["estimate"], 0.5)
    set_path(results["systems"]["lorenz63"], leaf["interval"], [0.4, 0.6])
    set_path(results["systems"]["lorenz63"], leaf["verdict"], "fail")
    results["verdicts"]["H3c"]["by_system"]["lorenz63"] = "fail"
    results["verdicts"]["H3c"]["verdict"] = "inconclusive"
    out = fast_render(monkeypatch, tmp_path, official=results)
    text = doc_of(out)
    assert re.search(
        r"\| lorenz63 \| H3c \| 0.5 \| \[0.4, 0.6\] \| .* \| fail \|", text
    )
    assert re.search(
        r"^\| H3c \| primary \| fail \| pass \| pass \| inconclusive \|",
        text,
        re.M,
    )


def test_gate_failure_marks_system_provisional(monkeypatch, tmp_path) -> None:
    """A failed gate puts PROVISIONAL on every row of that system (A5).

    Reference: the planted ``gate_pass`` False for chua only. Every table
    row that starts with "| chua" carries the mark, the verdict table cells
    of chua carry it, rossler rows do not, and the gate box says so.
    """
    out = fast_render(
        monkeypatch, tmp_path, official=make_results(gate={"chua": False})
    )
    text = doc_of(out)
    chua = [ln for ln in text.split("\n") if ln.startswith("| chua")]
    assert chua and all("PROVISIONAL" in ln for ln in chua)
    assert not [
        ln
        for ln in text.split("\n")
        if ln.startswith("| rossler") and "PROVISIONAL" in ln
    ]
    row = next(
        ln for ln in text.split("\n") if ln.startswith("| H2a | primary")
    )
    assert row.count("PROVISIONAL") == 1
    assert "GATE FAILURE" in text
    assert recheck(out) == 0
    stripped = text.replace("| chua PROVISIONAL | H2a(i)", "| chua | H2a(i)")
    problems = fb.check_text(stripped.split("\n"), rebuilt(out), trace_of(out))
    assert any("lacks PROVISIONAL" in p for p in problems)


def test_confirmatory_needs_release_and_hashes(monkeypatch, tmp_path) -> None:
    """A confirmatory results.json is refused without its release record (A9)."""
    monkeypatch.setattr(fb, "git_freeze_commit", lambda root: "c" * 40)
    results = make_results("confirmatory")
    cross = make_results("confirmatory")
    args = render_args(tmp_path, official=results, cross=cross)
    with pytest.raises(fb.ToolError, match="release-ref"):
        fb.render(args)
    args.release_ref = "ledger-seq-1"
    with pytest.raises(fb.ToolError, match="manifest hash"):
        fb.render(args)
    args.manifest_official = "0" * 64
    args.manifest_crosscheck = "0" * 64
    with pytest.raises(fb.ToolError, match="differs from the manifest"):
        fb.render(args)
    official = fb.sha256_of(tmp_path / "official" / "results.json")
    cross_sha = fb.sha256_of(tmp_path / "cross" / "results.json")
    args.manifest_official, args.manifest_crosscheck = official, cross_sha
    monkeypatch.setattr(fb, "git_freeze_commit", lambda root: "d" * 40)
    with pytest.raises(fb.ToolError, match="not freeze-1"):
        fb.render(args)
    monkeypatch.setattr(fb, "git_freeze_commit", lambda root: "c" * 40)
    monkeypatch.setattr(
        fb, "draw_panels", lambda *a, **k: plt.figure(figsize=(1, 1))
    )
    monkeypatch.setattr(
        fb, "draw_crosscheck", lambda *a, **k: plt.figure(figsize=(1, 1))
    )
    assert fb.render(args) == 0
    text = doc_of(Path(args.out))
    assert text.split("\n")[0] == "**CONFIRMATORY: UNPROMOTED**"
    assert "equals freeze-1" in text and "ledger-seq-1" in text


def test_different_seeds_refused(tmp_path) -> None:
    """Official and cross-check runs of different seeds are refused."""
    cross = make_results()
    cross["provenance"]["seed_id"] = "DEV-8"
    with pytest.raises(fb.ToolError, match="different seeds"):
        fb.load_sources(render_args(tmp_path, cross=cross), ROOT)


# --- figures ------------------------------------------------------------
def test_figure_arrays_equal_stored_leaves() -> None:
    """F1 and F2 draw exactly the stored estimates and endpoints (A11).

    Reference: the planted leaves of ``make_results``. Matplotlib stores
    float64 data unchanged, so equality is exact. Each panel draws, per
    system, one interval line then one marker line; missing points draw
    only a text.
    """
    results = make_results()
    parts = CONSTANTS["primary_parts"]
    panels = fb.panel_data(results, parts, SYSTEMS)
    fig = fb.draw_panels(panels, 3, "label", {s: False for s in SYSTEMS})
    axes = [a for a in fig.axes if a.get_visible() and a.lines]
    assert len(axes) == 6
    for ax, part in zip(axes, parts):
        lines = ax.get_lines()
        for n, s in enumerate(SYSTEMS):
            block = results["systems"][s]
            est = block
            for key in part["estimate"].split("/"):
                est = est[key]
            ci = block
            for key in part["interval"].split("/"):
                ci = ci[key]
            assert list(lines[2 * n].get_xdata()) == ci
            assert list(lines[2 * n + 1].get_xdata()) == [est]
    plt.close(fig)


def test_figure_marks_provisional_and_shapes() -> None:
    """A gate-failed system is named PROVISIONAL; verdicts differ by marker."""
    results = make_results()
    panels = fb.panel_data(results, CONSTANTS["primary_parts"][:1], SYSTEMS)
    fig = fb.draw_panels(
        panels, 1, "label", dict(zip(SYSTEMS, (False, False, True)))
    )
    ax = fig.axes[0]
    labels = [t.get_text() for t in ax.get_yticklabels()]
    assert labels == ["lorenz63", "rossler", "chua PROVISIONAL"]
    markers = {
        ln.get_marker() for ln in ax.get_lines() if ln.get_marker() != "None"
    }
    assert len(markers) == 3
    plt.close(fig)


def test_crosscheck_figure_uses_td_tokens() -> None:
    """F3 plots the z_away strings of the compare_runs text as floats."""
    td = fb.parse_td(RECORD)
    points = fb.crosscheck_points(td, CONSTANTS)
    assert len(points) == 18
    assert dict(points)["rossler H2b(i)"] == 2.26
    fig = fb.draw_crosscheck(td, CONSTANTS, "label")
    ax = fig.axes[0]
    assert list(ax.get_lines()[0].get_xdata()) == [z for _, z in points]
    assert ax.get_lines()[1].get_xdata()[0] == 3.4
    assert ax.get_title() == "Cross-check, information only"
    plt.close(fig)


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
    tmp, out = built
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
