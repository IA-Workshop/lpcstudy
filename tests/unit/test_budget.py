"""Interval labels, figure captions and the QoI declaration table (WU-0008.3, WU-0008.4).

The references are strings written out by hand from v3 section 7 (levels, block length, number
of resamples, multiplicity), from the plan's acceptance criteria L1 to L3 and Q1, and from
matplotlib's own text extents; none is produced by the code under test. All checks are exact
(strings, counts, an inequality of two bounding boxes), so there is no tolerance to justify.
"""

from __future__ import annotations

import dataclasses
import math
import re
from pathlib import Path

import matplotlib.figure
import matplotlib.pyplot as plt
import pytest
from test_report import fake_results, fake_system

from lpcstudy import budget, report
from lpcstudy.config import SMOKE
from lpcstudy.identifiers import HYPOTHESIS_TABLE
from lpcstudy.report import make_figures, verdicts, write_markdown

TAGS = ("procedure:", "level:", "dependence:", "multiplicity:")
NUMERIC_INTERVAL = re.compile(r"\[-?\d[\d.e+-]*, -?\d[\d.e+-]*\]")
ROOT = Path(__file__).resolve().parents[2]
PROPOSAL = ROOT / "docs" / "study" / "proposal_and_methods_v3.md"


def markdown(tmp_path: Path, mutate=None) -> list[str]:  # noqa: ANN001
    """RESULTS.md lines of the one-system fake results (``mutate`` edits the system first)."""
    results, config = fake_results("DEV-0")
    system = fake_system(config)
    if mutate is not None:
        mutate(system)
    results["systems"] = {"lorenz63": system}
    results["verdicts"] = verdicts(results, config)
    write_markdown(results, config, tmp_path / "RESULTS.md")
    return (tmp_path / "RESULTS.md").read_text().splitlines()


def test_constants_equal_their_sources() -> None:
    """The level literal equals ``analysis.PRIMARY_LEVEL``; V4's 200 is the literal in the source.

    Reference: v3 section 7 (level 1 - 0.05/3, written here as 0.05/3 from the Bonferroni split
    of 0.05 over three) and the text of ``experiments.py`` (``(200, m_draws)`` in the V4 bootstrap).
    """
    from lpcstudy import analysis
    assert budget.PRIMARY_LEVEL == analysis.PRIMARY_LEVEL == 1.0 - 0.05 / 3.0
    assert budget.SECONDARY_LEVEL == analysis.H1_LEVEL == 0.95
    source = (ROOT / "lpcstudy" / "experiments.py").read_text()
    assert f"({budget.V4_RESAMPLES}, m_draws)" in source and "(200, m_draws)" in source


def test_level_text_is_exact() -> None:
    """``level_text``: 1 - 0.05/3 is 98.33% (100 * 0.98333.. rounded to 2 decimals), else percent."""
    assert budget.level_text(1.0 - 0.05 / 3.0) == "1 − 0.05/3 (98.33%)"
    assert budget.level_text(0.95) == "95%"
    assert budget.level_text(0.9) == "90%"


def test_every_label_has_the_four_elements_and_reads_its_config() -> None:
    """Each row's label has procedure, level, dependence and multiplicity, from the config (L1).

    Reference: the plan's wording (v3 section 7). The configuration is changed to block 7 and
    B = 123: those numbers appear in the labels of the bootstrap rows and the preset values 5 and
    2000 do not (the label reads ``config``, not literals). Primary rows say 98.33% and
    Bonferroni; the others say 95%; H3a and the gain bound have their own wording.
    """
    config = dataclasses.replace(SMOKE, bootstrap_block=7, bootstrap_resamples=123)
    for row in HYPOTHESIS_TABLE:
        level = 0.9833333333333333 if row.role == "primary" else 0.95
        label = budget.interval_label(row, level, config)
        positions = [label.index(tag) for tag in TAGS]
        assert positions == sorted(positions), row.key
        if row.key in ("gain_bound", "H3a"):
            assert "blocks of" not in label
            continue
        assert "blocks of 7" in label and "B = 123" in label, row.key
        assert "blocks of 5" not in label and "2000" not in label, row.key
        if row.role == "primary":
            assert "98.33%" in label and "Bonferroni" in label, row.key
            # DEC-0024: every primary's label says the iterative error is unverified
            assert label.endswith("iterative error: the fixed 15-iteration Levenberg–Marquardt "
                                  "error of the PLP estimator is not estimated and is unverified "
                                  "(DEC-0024)"), row.key
        else:
            assert "level: 95%" in label and "Bonferroni" not in label, row.key
            assert "iterative error" not in label, row.key
    rows = {r.key: r for r in HYPOTHESIS_TABLE}
    assert "over construction states" in budget.interval_label(rows["H3b"], 0.95, config)
    h2a = budget.interval_label(rows["H2a"], 0.9833333333333333, config)
    # DEC-0008 A4(b): the bootstrap resamples all test states and re-evaluates the eligibility
    # of part (i) and the domain of part (ii) inside each resample; no eligible-only resampling
    assert "all of them, not only the eligible ones" in h2a and "re-evaluated inside each" in h2a
    assert "consecutive eligible" not in h2a and "small-error) test states" not in h2a
    h3b = budget.interval_label(rows["H3b"], 0.95, config)
    # DEC-0008 A4 and the analysis docstring of h3b: coverage of these intervals is not measured
    assert "coverage not measured" in h3b and "not guaranteed to cover" in h3b
    assert all("coverage not measured" not in budget.interval_label(r, 0.95, config)
               for r in HYPOTHESIS_TABLE if r.key != "H3b")
    h3a = budget.interval_label(rows["H3a"], 0.95, config)
    assert "Holm" in h3a and "p-values with no interval" in h3a


def test_markdown_labels_every_interval_table_before_the_next_heading(tmp_path: Path) -> None:
    """Every table with a numeric ``[x, y]`` is followed by a four-element label line (L1).

    Reference: the plan (L1): the tables are found from the generated RESULTS.md by their text,
    after the provenance header; the verdict table gets one label line per row, the validation
    table gets the V4 line. No table is excluded by name.
    """
    lines = markdown(tmp_path)
    first = next(i for i, ln in enumerate(lines) if ln.startswith("## "))
    tables, i = [], first
    while i < len(lines):
        if lines[i].startswith("|"):
            j = i
            while j < len(lines) and lines[j].startswith("|"):
                j += 1
            tables.append((i, j))
            i = j
        else:
            i += 1
    labelled = 0
    for start, end in tables:
        if not any(NUMERIC_INTERVAL.search(ln) for ln in lines[start:end]):
            continue
        nxt = next((k for k in range(end, len(lines)) if lines[k].startswith("#")), len(lines))
        found = [ln for ln in lines[end:nxt] if all(tag in ln for tag in TAGS)]
        assert found, lines[start]
        labelled += 1
    # the verdict table, the declaration table (its criteria name bands such as [0.8, 1.2]) and
    # the validation table
    assert labelled == 3
    verdict_lines = [ln for ln in lines if ln.startswith("- ") and "— procedure:" in ln]
    assert [ln.split(" ")[1] for ln in verdict_lines] == [r.v3_id for r in HYPOTHESIS_TABLE]
    assert any(ln.startswith("- (reported) — procedure: none, a fraction") for ln in lines)
    v4 = [ln for ln in lines if ln.startswith("V4 half-width — procedure:")]
    assert len(v4) == 1 and "ordinary percentile bootstrap" in v4[0] and "200 resamples" in v4[0]
    assert all(tag in v4[0] for tag in TAGS)


def test_a_row_without_a_result_has_no_label_line(tmp_path: Path) -> None:
    """A table row with no result (no verdict) is listed in the table but has no label line."""
    results, config = fake_results("DEV-0")
    results["systems"] = {"lorenz63": fake_system(config, skip=("H2d",))}
    results["verdicts"] = verdicts(results, config)
    write_markdown(results, config, tmp_path / "RESULTS.md")
    ids = [ln.split(" ")[1] for ln in (tmp_path / "RESULTS.md").read_text().splitlines()
           if ln.startswith("- ") and "— procedure:" in ln]
    assert ids == [r.v3_id for r in HYPOTHESIS_TABLE if r.key != "H2d"]


def test_label_level_equals_the_stored_level_and_a_mismatch_raises(tmp_path: Path) -> None:
    """The level in a label is the stored one; a stored level off the role's raises (L2).

    Reference: hand values. H3c and H2b(ii) are primary: stored 1 - 0.05/3 gives "98.33%"; H1a is
    secondary: stored 0.95 gives "95%". A primary row that stores 0.95, or a secondary that
    stores the primary level, is a defect and ``ValueError`` names the key (nothing relabelled).
    """
    def store(system: dict) -> None:
        system["H3b"]["D"]["level"] = 0.95
        system["H2e"]["by_noise"]["0.01"]["level"] = 0.95
        system["H2e"]["by_noise"]["0.02"]["level"] = 0.95
        system["H3c"]["level"] = 1.0 - 0.05 / 3.0
        system["H2b"]["library_change"]["level"] = 1.0 - 0.05 / 3.0
        system["H1a"]["level"] = 0.95
    lines = markdown(tmp_path, mutate=store)
    by_id = {ln.split(" ")[1]: ln for ln in lines if ln.startswith("- ") and "— procedure:" in ln}
    assert "level: 1 − 0.05/3 (98.33%);" in by_id["H3c"]
    assert "level: 1 − 0.05/3 (98.33%);" in by_id["H2b"]
    assert "level: 95%;" in by_id["H1a"]
    assert "level: 95%;" in by_id["H3b"] and "level: 95%;" in by_id["H2e"]
    for key, wrong, path in (("H3c", 0.95, ("level",)),
                             ("H1a", 1.0 - 0.05 / 3.0, ("level",)),
                             ("H2b", 0.95, ("library_change", "level")),
                             ("H3b", 1.0 - 0.05 / 3.0, ("D", "level")),
                             ("H3b", 0.9, ("weight_lambda", "level")),
                             ("H2e", 1.0 - 0.05 / 3.0, ("by_noise", "0.01", "level")),
                             ("H2e", 0.9, ("by_noise", "0.02", "level"))):
        results, config = fake_results("DEV-0")
        system = fake_system(config)
        node = system[key]
        for part in path[:-1]:
            node = node[part]
        node[path[-1]] = wrong
        results["systems"] = {"lorenz63": system}
        results["verdicts"] = verdicts(results, config)
        with pytest.raises(ValueError, match=f"result {key} .*defect, not relabelled"):
            write_markdown(results, config, tmp_path / "bad.md")


def test_results_without_stored_levels_use_the_role_level() -> None:
    """Results that predate stored levels (old schema) get the role's level, no exception."""
    results, config = fake_results("DEV-0")
    system = fake_system(config)
    results["systems"] = {"lorenz63": system}
    row = next(r for r in HYPOTHESIS_TABLE if r.key == "H3c")
    assert budget.stored_levels(row, system["H3c"]) == []
    assert budget.row_level(row, results, ["lorenz63"]) == 1.0 - 0.05 / 3.0
    assert budget.row_level(HYPOTHESIS_TABLE[0], results, ["lorenz63"]) == 0.95


@pytest.fixture
def saved_texts(monkeypatch: pytest.MonkeyPatch) -> dict[str, matplotlib.figure.Figure]:
    """Capture each figure at ``savefig`` time by file name; nothing is written or closed."""
    saved: dict[str, matplotlib.figure.Figure] = {}

    def stub(self: matplotlib.figure.Figure, fname, **kwargs) -> None:  # noqa: ANN001
        saved[Path(fname).name] = self

    monkeypatch.setattr(matplotlib.figure.Figure, "savefig", stub)
    monkeypatch.setattr(report.plt, "close", lambda fig=None: None)
    return saved


def test_every_figure_file_has_one_caption_in_the_markdown_and_the_png(
        tmp_path: Path, saved_texts: dict) -> None:
    """One caption per file written by ``make_figures``, in RESULTS.md and in the PNG (L3).

    Reference: the file list of ``make_figures`` (the four names, written out here) and the plan.
    The PNG text, with line breaks undone, is the caption; the ``## Figures`` section has the
    same caption for the same file; no current figure draws an interval, so each caption says
    "no interval" or "not a confidence interval".
    """
    try:
        results, config = fake_results("DEV-0")
        results["systems"] = {"lorenz63": fake_system(config)}
        written = make_figures(results, config, tmp_path)
        (tmp_path / "md").mkdir()
        lines = markdown(tmp_path / "md")
    finally:
        plt.close("all")
    names = ["separation_weight_vs_horizon.png", "kaplan_meier_by_rule.png",
             "regret_vs_regimes.png", "knob_response_library.png"]
    assert [p.name for p in written] == names == list(budget.FIGURE_CAPTIONS)
    start = lines.index("## Figures")
    section = lines[start:next(k for k in range(start + 1, len(lines)) if lines[k].startswith("#"))]
    for name in names:
        caption = budget.figure_caption(name, config)
        texts = [t.get_text() for t in saved_texts[name].texts]
        assert [" ".join(t.split()) for t in texts] == [caption]
        assert f"- `{name}`: {caption}" in section
        assert "no interval" in caption.lower() or "not a confidence interval" in caption
    assert sum(ln.startswith("- `") for ln in section) == 4


def test_caption_does_not_overlap_the_axes(tmp_path: Path, saved_texts: dict) -> None:
    """The caption's box lies below every axis' tight box, and the figure grew to hold it.

    Reference: matplotlib's own extents (``Text.get_window_extent`` and
    ``Axes.get_tightbbox``) on the figure saved by the knob-response plot, with a renderer from
    the Agg canvas. Exact comparison of two pixel coordinates.
    """
    try:
        results, config = fake_results("DEV-0")
        results["systems"] = {"lorenz63": fake_system(config)}
        make_figures(results, config, tmp_path)
        for name in budget.FIGURE_CAPTIONS:
            fig = saved_texts[name]
            fig.canvas.draw()
            renderer = fig.canvas.get_renderer()
            caption_top = fig.texts[0].get_window_extent(renderer).y1
            axes_bottom = min(ax.get_tightbbox(renderer).y0 for ax in fig.axes)
            assert caption_top <= axes_bottom + 1e-6, name
            assert fig.get_size_inches()[1] > 3.4, name  # grew beyond the original 3.4 in
    finally:
        plt.close("all")


def test_an_interval_caption_states_level_and_procedure() -> None:
    """A caption entry with ``interval_level`` states the level and the bootstrap (L3).

    Reference: the plan: a synthetic entry (no current figure draws an interval) at the primary
    level reads "moving-block bootstrap, blocks of 5" and "98.33%" at smoke (block 5, B = 50).
    A file with no caption raises ``KeyError`` (every figure has one).
    """
    captions = {"x.png": budget.FigureCaption("Medians with bands.", 1.0 - 0.05 / 3.0)}
    text = budget.figure_caption("x.png", SMOKE, captions)
    assert text == ("Medians with bands. Intervals: moving-block bootstrap, blocks of 5 "
                    "consecutive test states in time order, B = 50, level 1 − 0.05/3 (98.33%).")
    with pytest.raises(KeyError):
        budget.figure_caption("missing.png", SMOKE, captions)


def proposal_ids() -> list[str]:
    """Hypothesis ids of the three tables of v3 section 2, in order, then the gain bound.

    Reference: the proposal file, parsed by a regular expression on the table rows (``| H1a |``,
    ``| **H2a** |``, ``| Q-N (estimate) |``); the gain bound is the sentence after the RQ3 table
    ("The hybrid's horizon gain over the better forecaster is reported against the P1 bound"),
    which the decision log maps to the id ``(reported)``.
    """
    text = PROPOSAL.read_text(encoding="utf-8")
    section = text[text.index("## 2. Research questions"):text.index("## 3. Mathematical")]
    ids = re.findall(r"^\| (?:\*\*)?(H\d[a-e]|Q-N)(?:\*\*)?(?: \(estimate\))? \|", section, re.M)
    assert "reported against the P1 bound" in section
    return ids[:10] + ["(reported)"] + ids[10:]


def test_declaration_table_has_a_complete_row_per_table_row() -> None:
    """The declaration section has 14 rows, none with an empty cell, criterion verbatim (Q1).

    Reference: the ids parsed from v3 section 2 (13 hypotheses and the estimate, plus the
    reported gain bound: 14) and ``HYPOTHESIS_TABLE`` for the verbatim criterion. The heading and
    the seven columns are the plan's. The closing label has the four elements.
    """
    lines = budget.qoi_declaration_lines(SMOKE)
    assert lines[0] == "## Quantities of interest (NVVUQ.3)"
    header = next(i for i, ln in enumerate(lines) if ln.startswith("| ID |"))
    rows = [ln for ln in lines[header + 2:] if ln.startswith("|")]
    assert lines[header + 1] == "|" + "---|" * 7
    assert [c.strip() for c in lines[header].strip("|").split(" | ")] == [
        "ID", "Definition", "Units and conventions", "Criterion", "Decision-relevant error",
        "Decision informed", "Confirmatory or exploratory"]
    assert len(rows) == len(HYPOTHESIS_TABLE) == 14
    cells = [ln[2:-2].split(" | ") for ln in rows]
    assert all(len(row) == 7 and all(c.strip() for c in row) for row in cells)
    assert [row[0] for row in cells] == proposal_ids()
    assert [row[3] for row in cells] == [h.criterion.replace("|", "\\|") for h in HYPOTHESIS_TABLE]
    assert all(tag in lines[-1] for tag in TAGS) and "B = 50" in lines[-1]
    assert "blocks of 5" in lines[-1] and "98.33%" in lines[-1]


def test_a_table_row_without_a_declaration_raises() -> None:
    """A QoI is never reported undeclared: a missing declaration is a ``KeyError``."""
    declared = dict(budget.QOI_DECLARATIONS)
    del declared["H3c"]
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(budget, "QOI_DECLARATIONS", declared)
        with pytest.raises(KeyError, match="H3c"):
            budget.qoi_declaration_lines(SMOKE)


def test_markdown_has_the_declaration_section_between_labels_and_allocation(
        tmp_path: Path) -> None:
    """RESULTS.md has the section once, after the verdict labels and before the allocation rules."""
    lines = markdown(tmp_path)
    heads = [ln for ln in lines if ln.startswith("## ")]
    assert heads.count("## Quantities of interest (NVVUQ.3)") == 1
    i = heads.index("## Quantities of interest (NVVUQ.3)")
    assert heads[i - 1] == "## Hypothesis verdicts"
    assert heads[i + 1] == "## Allocation rules at the core cell (test split)"


def test_declaration_texts_state_the_statistics_of_the_decision_log() -> None:
    """The H2a, H3a, H3b and H3c declarations say what DEC-0008 A3, A4 and v3 section 7 say.

    Reference: hand-written phrases from DEC-0008 A4(a), A4(a2), A4(b) (H2a), A3 (H3a cannot fail;
    H3b decided by the lower bound of D, the stability index reported) and the sentence of v3
    section 7 "H3c holds while excess error is flat in K. This is the P3 floor." (read from the
    proposal file). Exact substring checks.
    """
    declared = budget.QOI_DECLARATIONS
    h2a = declared["H2a"]
    assert "indicator 1{w* = 0}" in h2a["definition"] and "1{w* = 1}" in h2a["definition"]
    assert "quadratic controls" in h2a["definition"] and "initial segment" in h2a["definition"]
    assert "at most 0.5" in h2a["definition"] and "below 0.5" not in h2a["definition"]
    assert "the edge is the bound 0.1" in h2a["decision_error"]
    assert "cannot fail" in declared["H3a"]["decision_error"]
    h3b = declared["H3b"]
    assert "lower bound of D" in h3b["decision_error"]
    assert "reported, not decided" in h3b["decision_error"] and "reported only" in h3b["definition"]
    text = PROPOSAL.read_text(encoding="utf-8")
    assert "H3c holds while excess error is flat in K" in text and "This is the P3 floor" in text
    assert 'reads "H3c holds while excess error is flat in K" as "the P3 floor"' in \
        declared["H3c"]["decision_error"]
    assert "not as a failure" not in declared["H3c"]["decision_error"]


# ------------------------------------------------------------ WU-0008.1 and .2b: the budget tables

NOTE_WU0006 = ROOT / "docs" / "agent" / "notes" / "2026-10-11-math-wu0006.md"
NOTE_WU0008_M7B = (ROOT / "docs" / "agent" / "notes" / "2026-10-11-math-wu0008-scripts"
                   / "m7b.log")
WU0006_UNIT = ROOT / "docs" / "agent" / "records" / "work" / "WU-0006-simstudies.md"
SOURCES = [name for name, _ in budget.ROW_NAMES]
PART_LABEL = re.compile(r"(?:^|; )(zero|interior|one|all): ")


def full_system(config=SMOKE) -> dict:  # noqa: ANN001
    """``fake_system`` plus the keys of WU-0008.2a (``ci_mc_se``) and V4's used M and larger M."""
    system = fake_system(config)
    system["H2a"]["ci_mc_se"] = [0.001, 0.002]
    system["H2a"]["range_n_failed_resamples"] = 0
    for part in system["H2a"]["part_ii"].values():
        part["ci_mc_se"] = [0.003, 0.004]
        part["n_failed_resamples"] = 0
    system["H2b"]["noise"].update(ci=[0.1, 0.3], ci_mc_se=[0.002, 0.002], n_failed_resamples=0,
                                  n_states=300)
    system["H2b"]["library_change"].update(ci_mc_se=[0.001, 0.002], n_states=300,
                                           n_failed_resamples=0)
    system["H3c"]["ci_mc_se"] = [0.0005, 0.0006]
    system["H3c"]["n_failed_resamples"] = 0
    system["H1d"]["rows"]["analog_seed"]["spearman"] = 0.8
    convergence = system["validation"]["convergence"]
    convergence["used_M"] = config.n_oracle_draws
    convergence[str(config.n_oracle_draws)]["mean_abs_dev_from_max"] = 0.02
    convergence[str(4 * config.n_oracle_draws)] = {"median_half_width": 0.005,
                                                   "mean_abs_dev_from_max": 0.0}
    return system


def budget_results(*systems: dict, names=("lorenz63", "rossler", "chua")) -> tuple[dict, list]:
    """Results with the given systems (in ``names`` order) and the matching system list."""
    results, _ = fake_results("DEV-0")
    results["systems"] = dict(zip(names, systems))
    return results, list(results["systems"])


def tables_of(lines: list[str]) -> dict[str, list[list[str]]]:
    """Heading to the cells of each table row (header and separator dropped), from the lines."""
    out: dict[str, list[list[str]]] = {}
    heading = ""
    for ln in lines:
        if ln.startswith("### "):
            heading = ln[4:]
            out[heading] = []
        elif ln.startswith("| ") and not ln.startswith("| Source") and heading:
            out[heading].append(ln[2:-2].split(" | "))
    return out


def part_values(cell: str) -> list[str]:
    """The values of a size or flag cell: one per part when the cell is part-labelled."""
    marks = list(PART_LABEL.finditer(cell))
    if not marks:
        return [cell]
    return [cell[m.end():(marks[i + 1].start() if i + 1 < len(marks) else len(cell))]
            for i, m in enumerate(marks)]


def test_every_table_has_nine_rows_in_order_and_no_cell_is_empty_or_unparsable() -> None:
    """B1: five tables, nine rows in the skill's order, every size a number or "not estimated: why".

    Reference: the skill ``uq-budget`` (the eight rows) and DEC-0021 O2 (the ninth), written out in
    ``ROW_NAMES`` order here by hand; ``fake_system`` results with the full keys. A size cell, or
    each part of a part-labelled cell, starts with a digit (a number, ``0 (...)``, ``0: ...``) or
    with "not estimated: " followed by a non-empty reason. No cell is blank. Exact.
    """
    results, systems = budget_results(full_system(), full_system())
    lines = budget.budget_lines(results, systems, SMOKE)
    tables = tables_of(lines)
    assert list(tables) == list(budget.QOI_TITLES.values())
    skill_rows = ["Oracle Monte Carlo (M draws per state)", "Sampling of test states",
                  "Bootstrap Monte Carlo error", "Discretization (RK4)",
                  "Iterative (Levenberg–Marquardt)", "Round-off",
                  "Proxy error (deployable against oracle)",
                  "Model form: exact model, three systems, scalar observable",
                  "Interval procedure (coverage of the block-5 percentile interval)"]
    for title, rows in tables.items():
        assert [r[0] for r in rows] == skill_rows, title
        for cells in rows:
            assert len(cells) == 3 + 2 + 2, (title, cells[0])  # 2 systems
            assert all(c.strip() for c in cells), (title, cells[0])
            for cell in cells[3:5]:
                for value in part_values(cell):
                    assert re.match(r"\d", value) or (
                        value.startswith("not estimated: ") and value[15:].strip()), \
                        (title, cells[0], value)
    assert [ln for ln in lines if ln.startswith("### ")] == [
        f"### {t}" for t in budget.QOI_TITLES.values()]


def test_old_schema_and_a_missing_result_give_the_same_rows_and_not_estimated_cells() -> None:
    """B2: results without ``ci_mc_se``, the LM keys or V4's used M, and a system without H3c.

    Reference: the plan: the same nine rows, no exception, the affected cells "not estimated: why".
    The old system is ``fake_system`` as it stood before WU-0008 (no ``ci_mc_se``, no ``used_M``);
    the second system lacks the H3c result and V4. Exact string checks.
    """
    old = fake_system(SMOKE)
    short = full_system()
    del short["H3c"], short["validation"]
    results, systems = budget_results(old, short, names=("lorenz63", "rossler"))
    tables = tables_of(budget.budget_lines(results, systems, SMOKE))
    assert all(len(rows) == 9 for rows in tables.values())
    h3c = tables[budget.QOI_TITLES["H3c"]]
    assert all(r[4].startswith("not estimated: no H3c result") for r in h3c)
    bootstrap = tables[budget.QOI_TITLES["H2b(ii)"]][2]
    assert bootstrap[3].startswith("not estimated: no ci_mc_se in these results")
    assert bootstrap[4] == "0.002 (lower 0.001, upper 0.002)"  # the second system has the keys
    assert tables[budget.QOI_TITLES["H2a(i)"]][4][3] == budget.LM_NOT_READ
    # the old fake V4 has convergence entries but no used_M: R12(c), a distinct reason
    assert tables[budget.QOI_TITLES["H2a(i)"]][0][3].endswith(
        "F1 not computable: V4 present but used_M missing")
    discretization = tables[budget.QOI_TITLES["H2a(i)"]][3][4]
    assert discretization.startswith("0 (LPC.NV.1") and "V6 not in these results" in discretization


def test_the_ten_percent_flag_is_strict() -> None:
    """B3: sizes 0.09, 0.10 and 0.11 of a half-width of 1 read yes, no, no (M9).

    Reference: the plan (strict "<"): 0.1 * 1.0 == 0.1 exactly in float64, so a size of 0.1 is not
    below it. An unbounded half-width and a missing size are "not estimated". Exact.
    """
    assert [budget.below_tenth(s, 1.0) for s in (0.09, 0.10, 0.11)] == ["yes", "no", "no"]
    assert budget.below_tenth(0.0, 1.0) == "yes"
    assert budget.below_tenth(0.5, float("inf")) == "not estimated: interval unbounded"
    assert budget.below_tenth(0.5, None) == "not estimated: interval unbounded"
    assert budget.below_tenth(None, 1.0) == "not estimated"


def test_coverage_constants_equal_the_wu0006_documents() -> None:
    """B4: every run-2 count, reference rate and SE equals the documents they come from.

    Reference (parsed from the files, shared nothing with the module): the Log table of
    ``WU-0006-simstudies.md`` ("| C1, 0 | 945 (918-969) | 983 (963-994) | ..."), whose third column
    is the count out of 1000 at level 1 - 0.05/3; the reference table of the math note of WU-0006
    ("| C8 | 300 | 0.3 | 0 | 0.9444 (0.0011) | ... | 0.9806 (0.0007) | ...") for the rate and SE at
    98.3%; and ``m7b.log`` for the C4h rows. Exact (the documents hold the same four-digit
    decimals); the n_states of each case equals the note's n.
    """
    counts = {}
    for ln in WU0006_UNIT.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| (C\d), (0|0\.3) \| \**(\d+)\**.*? \| \**(\d+)\**", ln)
        if m:
            counts[(m.group(1), float(m.group(2)))] = int(m.group(4))
    reference = {}
    for ln in NOTE_WU0006.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| (C\d) \| (\d+) \| [<=\d.]+ \| (0|0\.3) \| [\d.]+ \([\d.]+\) \| [\d.]+ "
                     r"\| \[[\d, ]+\] \| ([\d.]+) \(([\d.]+)\) \|", ln)
        if m:
            reference[(m.group(1), float(m.group(3)))] = (
                float(m.group(4)), float(m.group(5)), int(m.group(2)))
    log = {}
    for ln in NOTE_WU0008_M7B.read_text(encoding="utf-8").splitlines():
        m = re.match(r"C4h s(1\.5|2) phi0\s+p_ref ([\d.]+) \(([\d.]+)\)", ln)
        if m:
            log[("C4h" + m.group(1), 0.0)] = (float(m.group(2)), float(m.group(3)))
    c4h = re.search(r"C4h sigma 1\.5: \d+ / (\d+).*?sigma 2: \d+ / (\d+)",
                    WU0006_UNIT.read_text(encoding="utf-8"))
    assert len(counts) >= 16 and len(reference) == 18 and len(log) == 2 and c4h
    for key, case in budget.COVERAGE_WU0006.items():
        if key[0].startswith("C4h"):
            assert (case.rate, case.rate_se) == log[key], key
            assert case.count == int(c4h.group(1 if key[0] == "C4h1.5" else 2)), key
            continue
        assert case.count == counts[key], key
        assert (case.rate, case.rate_se, case.n_states) == reference[key], key


def test_oracle_row_formulas_equal_the_hand_expressions() -> None:
    """B5: F1 and F2 of M3 against one float expression each (1e-15 relative).

    Reference: F1 = (3/sqrt(pi)) h / z_0.975 with z_0.975 from ``scipy.stats.norm.ppf`` (a
    different quantile implementation from the module's ``statistics.NormalDist``), F2 =
    z_L sqrt(2) s / sqrt(n) with s = a / (sqrt(2/pi) sqrt(1 - M/M_max)), z_L = ppf((1 + level)/2),
    on hand values h = 0.02, a = 0.03, M = 200, M_max = 800, n = 300, level 1 - 0.05/3. Tolerance:
    one expression of about ten operations plus two quantile evaluations that agree to a few ulp:
    1e-15 relative was fixed by the plan.
    """
    from scipy.stats import norm

    level = 1.0 - 0.05 / 3.0
    f1 = 3.0 / math.sqrt(math.pi) * 0.02 / norm.ppf(0.975)
    assert budget.oracle_range_bound(0.02) == pytest.approx(f1, rel=1e-15)
    s_mean = 0.03 / (math.sqrt(2.0 / math.pi) * math.sqrt(1.0 - 200 / 800))
    f2 = norm.ppf((1.0 + level) / 2.0) * math.sqrt(2.0) * s_mean / math.sqrt(300)
    assert budget.oracle_change_share(0.03, 200, 800, 300, level) == pytest.approx(f2, rel=1e-15)
    assert budget.oracle_range_bound(0.02, horizons=2) == pytest.approx(
        2.0 / math.sqrt(math.pi) * 0.02 / norm.ppf(0.975), rel=1e-15)
    with pytest.raises(ValueError):
        budget.oracle_change_share(0.03, 800, 800, 300, level)
    with pytest.raises(ValueError):
        budget.oracle_range_bound(0.02, horizons=4)


def test_oracle_cell_shows_f1_and_f2_with_three_digits() -> None:
    """The oracle row prints F1 (H2a(i)) and F2 (H2b(ii)) from the stored V4, 3 significant digits.

    Reference: the functions of B5 (hand-checked) formatted with ``f"{x:.3g}"``; V4 of the full
    fake system: half-width 0.01, mean deviation 0.02 at M = 30, larger M = 120; H2b(ii) n = 300.
    """
    results, systems = budget_results(full_system(), names=("lorenz63",))
    tables = tables_of(budget.budget_lines(results, systems, SMOKE))
    level = 1.0 - 0.05 / 3.0
    f1 = budget.oracle_range_bound(0.01)
    f2 = budget.oracle_change_share(0.02, 30, 120, 300, level)
    assert f"F1 = {f1:.3g}" in tables[budget.QOI_TITLES["H2a(i)"]][0][3]
    assert f"F2 = {f2:.3g}" in tables[budget.QOI_TITLES["H2b(ii)"]][0][3]
    assert tables[budget.QOI_TITLES["H2b(ii)"]][0][5] == "not estimated"


def test_coverage_shortfall_matches_the_applied_mathematician_table() -> None:
    """f = z_nom/z_obs - 1 and its SE reproduce the M7 table; f = 10% at p = 0.9705.

    Reference: the M7 table of the unit file (WU-0008 design): C8 at phi 0.3, reference 0.9682
    (SE 0.0009), f +0.115 +- 0.006 (four-digit rates and three-digit results: the table rounds the
    inputs, so abs 2e-3 on f and 1e-3 on its SE); C3 at phi 0 gives +0.023 +- 0.009; and the
    statement "f = 10% <=> p = 0.9705" (abs 2e-3: the rate is given to four digits, df/dp is about
    7). The flag of the whole table (M7 'Flag'): H2a(i) yes, H2a(ii) interior yes, H2b no, H3c no.
    """
    level = 1.0 - 0.05 / 3.0
    f, se = budget.coverage_shortfall(0.9682, 0.0009, level)
    assert f == pytest.approx(0.115, abs=2e-3) and se == pytest.approx(0.006, abs=1e-3)
    f, se = budget.coverage_shortfall(0.9807, 0.0010, level)
    assert f == pytest.approx(0.023, abs=2e-3) and se == pytest.approx(0.009, abs=1e-3)
    assert budget.coverage_shortfall(0.9705, 0.001, level)[0] == pytest.approx(0.10, abs=2e-3)
    assert budget.coverage_shortfall(0.99, 0.001, level)[0] < 0.0  # above nominal: no shortfall
    flags = {q: budget._coverage_f(q, label, level) for q, label in
             (("H2a(i)", ""), ("H2a(ii)", "interior"), ("H2b(i)", ""), ("H2b(ii)", ""),
              ("H3c", ""))}
    assert [f < 0.1 for f in flags.values()] == [True, True, False, False, False]
    assert budget._coverage_f("H2a(ii)", "zero", level) is None


def test_table_cells_for_each_numerical_row() -> None:
    """Bootstrap error, round-off, discretization, coverage and the flags, by hand values.

    Reference: the full fake system: H3c interval [0.99, 1.04] (half-width 0.025), ``ci_mc_se``
    [0.0005, 0.0006]; round-off 1e-4 * max(|0.99|, |1.04|) = 1.04e-4; the bootstrap size is the
    larger endpoint, 0.0006, against 10% of 0.025 = 0.0025: yes; round-off 1.04e-4 < 0.0025: yes;
    the coverage size is f_max * 0.025 with f_max = 0.1235 (C4h sigma 2, M7, computed in the test
    from scipy's quantiles): 0.0031 > 0.0025: no.
    V6 of the fake system 1e-5 is printed with the zero discretization size. Exact strings, 3
    significant digits.
    """
    results, systems = budget_results(full_system(), names=("lorenz63",))
    rows = tables_of(budget.budget_lines(results, systems, SMOKE))[budget.QOI_TITLES["H3c"]]
    assert rows[1][3] == "0.025" and rows[1][5] == "—"
    assert rows[2][3] == "0.0006 (lower 0.0005, upper 0.0006)" and rows[2][5] == "yes"
    assert rows[3][3].startswith("0 (LPC.NV.1: truth and model share the discrete map); "
                                 "V6 = 1e-05 σ_x") and rows[3][5] == "yes"
    assert rows[5][3] == "0.000104" and rows[5][5] == "yes"
    from scipy.stats import norm

    level = 1.0 - 0.05 / 3.0  # f of C4h sigma 2 (reference rate 0.9669) by scipy's quantiles
    f_c4h2 = norm.ppf((1.0 + level) / 2.0) / norm.ppf((1.0 + 0.9669) / 2.0) - 1.0
    assert rows[8][3] == f"{f_c4h2 * 0.025:.3g}" and rows[8][5] == "no"
    assert rows[7][3].startswith("not estimated: v3 section 8") and rows[7][5] == "—"
    assert rows[6][3].startswith("not estimated: the QoI compares two deployable rules")
    assert "H1d Spearman" in rows[6][3] and "analog seed 0.8" in rows[6][3]


def test_failed_resamples_tie_and_unbounded_interval_cells() -> None:
    """None endpoint errors get the reason of M2; a tie reads 0; an unbounded interval says so.

    Reference: hand cases at B = 50 (smoke) and level 1 - 0.05/3: the window leaves (0, 1) ->
    "B = 50 too small for the binomial window"; an infinite bound -> "bound infinite (A3)"; a
    finite interval with failures -> "failed resamples (F = 3) within one binomial SE of the
    endpoint". At B = 2000 with 13 failed resamples and a finite interval the same last text.
    A tie (``ci_mc_se`` [0, 0]) reads "0 (tie at the endpoint)" and flag yes; an interval
    [-inf, inf] gives a half-width cell "not estimated: interval unbounded ...", flag "not
    estimated" and round-off/coverage cells "not estimated: interval unbounded".
    """
    level = 1.0 - 0.05 / 3.0
    assert budget.mc_error_reason([0.0, 1.0], 0, 50, level) == \
        "B = 50 too small for the binomial window"
    assert budget.mc_error_reason([-math.inf, 1.0], 20, 2000, level) == "bound infinite (A3)"
    assert budget.mc_error_reason([0.0, 1.0], 13, 2000, level) == \
        "failed resamples (F = 13) within one binomial SE of the endpoint"
    system = full_system()
    system["H3c"]["ci_mc_se"] = [None, None]
    system["H3c"]["ci"] = [0.9, 1.1]
    system["H3c"]["n_failed_resamples"] = 3
    system["H2b"]["library_change"]["ci_mc_se"] = [0.0, 0.0]
    system["H2a"]["range_ci"] = [-math.inf, math.inf]
    system["H2a"]["ci_mc_se"] = [None, None]
    results, systems = budget_results(system, names=("lorenz63",))
    tables = tables_of(budget.budget_lines(results, systems, SMOKE))
    h3c = tables[budget.QOI_TITLES["H3c"]][2]
    assert h3c[3] == "not estimated: B = 50 too small for the binomial window"
    assert h3c[5] == "not estimated"
    tie = tables[budget.QOI_TITLES["H2b(ii)"]][2]
    assert tie[3] == "0 (tie at the endpoint)" and tie[5] == "yes"
    unbounded = tables[budget.QOI_TITLES["H2a(i)"]]
    assert unbounded[1][3].startswith("not estimated: interval unbounded")
    assert unbounded[2][3] == "not estimated: bound infinite (A3)"
    assert unbounded[5][3] == "not estimated: interval unbounded" and unbounded[8][3] == \
        "not estimated: interval unbounded"
    assert unbounded[8][5] == "not estimated"


def test_h2a_ii_cells_are_labelled_by_part_and_the_zero_part_has_no_coverage_case() -> None:
    """H2a(ii) shows each part in each cell; the zero part's coverage cell is "not estimated".

    Reference: M1/M7: the parts are zero and interior (and "one" when stored); C7 maps to the
    interior part only, so the zero part reads "not estimated: no WU-0006 case has a binary
    target" and the interior part has a size and the flag "yes" (f_max 0.059 < 0.1). Exact.
    """
    system = full_system()
    system["H2a"]["part_ii"]["one"] = dict(system["H2a"]["part_ii"]["zero"])
    results, systems = budget_results(system, names=("lorenz63",))
    rows = tables_of(budget.budget_lines(results, systems, SMOKE))[budget.QOI_TITLES["H2a(ii)"]]
    assert [m.group(1) for m in PART_LABEL.finditer(rows[1][3])] == ["zero", "interior", "one"]
    values = part_values(rows[8][3])
    assert values[0].startswith("not estimated: no WU-0006 case has a binary target")
    assert re.match(r"[\d.e-]+$", values[1])
    assert part_values(rows[8][5]) == ["not estimated", "yes", "not estimated"]


def test_lm_row_reads_the_summary_when_a_path_is_set(monkeypatch: pytest.MonkeyPatch) -> None:
    """With ``LM_SUMMARY_PATH`` set and the keys present the row is "not estimated" plus the diagnostic.

    Reference: M4's text: median residual/(3.36 rho^2) with rho = 0.01 (smoke core noise):
    a median residual of 6.72e-4 gives 2 (6.72e-4 / (3.36 * 1e-4) = 2, by hand), the fraction
    of no decrease 0.25. The flag stays "not estimated" (the residual does not convert to the QoI
    scale). Absent keys give ``LM_ABSENT``. Exact.
    """
    monkeypatch.setattr(budget, "LM_SUMMARY_PATH", ("estimators", "summary"))
    system = full_system()
    system["estimators"] = {"summary": {"median_residual": 6.72e-4, "fraction_no_decrease": 0.25}}
    results, systems = budget_results(system, full_system(), names=("lorenz63", "rossler"))
    row = tables_of(budget.budget_lines(results, systems, SMOKE))[
        budget.QOI_TITLES["H3c"]][4]
    assert row[3].startswith("not estimated: residual and iteration summary do not convert")
    assert "median residual/(3.36ρ²) = 2, fraction no decrease = 0.25" in row[3]
    assert row[4] == budget.LM_ABSENT and row[6] == "not estimated"
    assert budget.LM_ABSENT == "not estimated: WU-0005.4 summary absent from results"


def test_text_under_every_table() -> None:
    """Under each table: the interval label, the seed line, the 10% rule, and the M1 sentences.

    Reference: the plan and M1: the label contains the four elements; "DEVELOPMENT (DEV-0)" from
    the provenance block; the H3c table has the extra "Conditional on the fitted A4 and A5"
    sentence and no other table has it; the iterative-error statement is under all five; a
    results dict without provenance says the seed is not recorded.
    """
    results, systems = budget_results(full_system(), names=("lorenz63",))
    text = "\n".join(budget.budget_lines(results, systems, SMOKE))
    assert text.count("Interval label — procedure:") == 5
    assert text.count("Seed: DEVELOPMENT (DEV-0); the interval-procedure row: reference rates "
                      "from scratch seed 20261011 (m2_coverage.py), run-2 counts from seed 6006 "
                      "(make_rng(6006, \"wu0006\", ...)); neither is a registered seed.") == 5
    assert text.count(budget.WIDENING_SENTENCE) == 5 == text.count(budget.CONDITIONAL_SENTENCE)
    assert text.count(budget.H3C_SENTENCE) == 1 == text.count("Conditional on the fitted A4")
    assert text.count(budget.ITERATIVE_SENTENCE) == 5
    del results["provenance"]
    assert "seed not recorded" in "\n".join(budget.budget_lines(results, systems, SMOKE))
    assert all(tag in ln for ln in text.splitlines() if ln.startswith("Interval label — ")
               for tag in TAGS)


def test_markdown_has_the_budget_section_between_validation_and_robustness(
        tmp_path: Path) -> None:
    """RESULTS.md holds the budget section once, after the validation gate and before Handling."""
    lines = markdown(tmp_path)
    heads = [ln for ln in lines if ln.startswith("## ")]
    assert heads.count(budget.BUDGET_HEADING) == 1
    i = heads.index(budget.BUDGET_HEADING)
    assert heads[i - 1] == "## Validation gate" and heads[i + 1] == "## Figures"


def test_coverage_r_ref_is_the_hand_transcription_of_the_math_note() -> None:
    """R_ref of each case: 40000 for C1, C4, C8; 20000 for C3, C7 and C4h (hand transcription).

    Reference: the applied-mathematician's statement (fix round 1) from the math note and its
    scripts: the C7 pooled 60000 applies to its verdict counts only. The note gives the range
    "10^4 to 4*10^4" generically, so this is a transcription, not a parse. Exact.
    """
    expected = {"C1": 40000, "C4": 40000, "C8": 40000, "C3": 20000, "C7": 20000,
                "C4h1.5": 20000, "C4h2": 20000}
    assert {k: v.r_ref for k, v in budget.COVERAGE_WU0006.items()} == {
        (case, phi): r for case, r in expected.items() for phi in (0.0, 0.3)
        if (case, phi) in budget.COVERAGE_WU0006}


def test_interval_procedure_cell_names_both_seed_sources_and_def0020_correctly() -> None:
    """R9 and R13: reference seed 20261011 with R_ref and run-2 seed 6006; DEF-0020 stated truly.

    Reference: the review's wording (the reference rates come from the scratch seed 20261011, the
    run-2 counts from make_rng(6006, ...)); DEF-0020's Resolution (Option C or K only decides
    whether the WU-0006 ROADMAP-bound rows stay asserted; widening or another procedure is a
    separate design question). The widening sentence cites the uq-budget rule, not DEF-0020 or
    DEC-0018. Exact substring checks.
    """
    results, systems = budget_results(full_system(), names=("lorenz63",))
    tables = tables_of(budget.budget_lines(results, systems, SMOKE))
    h2b = tables[budget.QOI_TITLES["H2b(ii)"]][8][2]
    assert "R_ref 40000" in h2b and "scratch seed 20261011" in h2b and "seed 6006" in h2b
    assert "R_ref 20000" in tables[budget.QOI_TITLES["H3c"]][8][2]
    assert "decides only whether the WU-0006 ROADMAP-bound coverage rows stay asserted (K) or " \
        "become recorded characterization rows" in h2b
    assert "separate, undecided design question for the owner and the applied-mathematician" in h2b
    assert "widening or another procedure (Option C or K)" not in h2b
    assert "registered seed" in h2b and "synthetic, seed 6006" not in h2b
    assert "DEF-0020" not in budget.WIDENING_SENTENCE and "DEC-0018" not in budget.WIDENING_SENTENCE
    assert "uq-budget skill is to widen the interval or refine" in budget.WIDENING_SENTENCE


def test_included_cell_of_the_oracle_row_is_per_qoi() -> None:
    """R10: the Included cell of row 1 is the applied-mathematician's wording for each QoI.

    Reference: the wording supplied in fix round 1, written out here; each at most 140 characters;
    H3c says the test-state M draws do not enter and the fit-stage noise is conditioned on; no
    table says the variance is inside "every" primary interval; the H2a(ii) table carries the note
    that the w* = 1 part is decided once on the full sample. Exact.
    """
    results, systems = budget_results(full_system(), names=("lorenz63",))
    lines = budget.budget_lines(results, systems, SMOKE)
    tables = tables_of(lines)
    expected = {
        "H2a(i)": "variance: yes (states resampled with their M-draw w*; eligibility redone in "
                  "each resample; asymptotic for a median); finite-M bias: no",
        "H2a(ii)": "variance: yes in every part (target, domain and seed controls resampled with "
                   "the states; asymptotic); finite-M bias: no",
        "H2b(i)": "variance: yes (mean of per-state Spearman values, each from that state's own "
                  "draws); finite-M bias: no",
        "H2b(ii)": "variance: yes (mean of per-state paired changes; same unit draws at both "
                   "N_lib); finite-M clip-boundary bias: no",
        "H3c": "no: test-state M draws do not enter the QoI; fit-stage M-draw noise (A4 proxies; "
               "A5 tree, leaf weights, K) is conditioned on"}
    for qoi, text in expected.items():
        cell = tables[budget.QOI_TITLES[qoi]][0][4]
        assert cell == text and len(cell) <= 140, qoi
    text = "\n".join(lines)
    assert "inside every primary" not in text and "propagates through the state resampling" not in text
    assert text.count(budget.H2A_ONE_NOTE) == 1
    assert budget.H2A_ONE_NOTE == ("Whether the w* = 1 part is added at all is decided once on "
                                   "the full sample and is not resampled.")


def test_not_estimated_reasons_are_true_in_each_reachable_case() -> None:
    """R12 (a) to (e): each reason names its own cause; hand-written expected texts.

    Reference: the review's wording and the code paths: (a) an unavailable H2b(ii) (``ci`` None,
    no ``ci_mc_se``, as ``_unavailable`` writes it) reads "no interval in these results", not
    "written before WU-0008.2a"; (b) F2 with V4's used M equal to its largest M, with no states,
    with a non-finite deviation, each its own reason; (c) V4 absent, V4 without used_M, V4 without
    the entry of the used M; (d) smoke has two noise levels: "across the 2 ρ cells", and the
    pilot's four give "across the 4 ρ cells"; (e) A5_vs_Astar None reads "not computable (A2 ≤
    A*)", A4_vs_A4o "(A2 ≤ A4o)", a missing key "not available". Exact substring checks.
    """
    def table(system: dict, config=SMOKE) -> dict:  # noqa: ANN001
        results, systems = budget_results(system, names=("lorenz63",))
        return tables_of(budget.budget_lines(results, systems, config))

    unavailable = full_system()
    unavailable["H2b"]["library_change"] = {"mean_change": None, "ci": None, "level": 1.0 - 0.05 / 3.0,
                                            "n_states": None, "n_failed_resamples": None}
    rows = table(unavailable)[budget.QOI_TITLES["H2b(ii)"]]
    assert rows[2][3] == "not estimated: no interval in these results"
    assert "written before WU-0008.2a" not in rows[2][3]

    def f2_text(mutate) -> str:  # noqa: ANN001
        system = full_system()
        mutate(system)
        return table(system)[budget.QOI_TITLES["H2b(ii)"]][0][3]

    same_m = f2_text(lambda s: s["validation"]["convergence"].pop(str(4 * SMOKE.n_oracle_draws)))
    assert same_m.endswith("share not computable: V4 has no larger M than the one used (M = 30)")
    no_states = f2_text(lambda s: s["H2b"]["library_change"].update(n_states=0))
    assert no_states.endswith("share not computable: the number of states of the change is "
                              "missing")
    no_dev = f2_text(lambda s: s["validation"]["convergence"][str(SMOKE.n_oracle_draws)].pop(
        "mean_abs_dev_from_max"))
    assert no_dev.endswith("share not computable: V4's mean_abs_dev_from_max is missing or not "
                           "finite")
    absent = f2_text(lambda s: s["validation"].pop("convergence"))
    assert absent.endswith("share not computable: V4 absent from these results")
    no_used = f2_text(lambda s: s["validation"]["convergence"].pop("used_M"))
    assert no_used.endswith("share not computable: V4 present but used_M missing")
    no_entry = f2_text(lambda s: s["validation"]["convergence"].pop(str(SMOKE.n_oracle_draws)))
    assert no_entry.endswith("share not computable: V4 present but its entry for the used M = 30 "
                             "(or its median_half_width) is missing")
    f1_absent = table({**full_system(), "validation": {}})[budget.QOI_TITLES["H2a(i)"]][0][3]
    assert f1_absent.endswith("; F1 not computable: V4 absent from these results")

    assert "across the 2 ρ cells" in table(full_system())[budget.QOI_TITLES["H2b(i)"]][0][3]
    four = dataclasses.replace(SMOKE, noise_levels=(0.005, 0.01, 0.02, 0.05))
    assert "across the 4 ρ cells" in table(full_system(), four)[
        budget.QOI_TITLES["H2b(i)"]][0][3]

    proxy = full_system()
    proxy["oracle_recovery"] = {"A4_vs_A4o": None, "A5_vs_Astar": float("nan")}
    text = table(proxy)[budget.QOI_TITLES["H3c"]][6][3]
    assert "A4 recovers not computable (A2 ≤ A4o) gain over A2" in text
    assert "A5 recovers not computable (A2 ≤ A*) gain" in text
    proxy["oracle_recovery"] = {"A4_vs_A4o": 0.5}
    assert "A5 recovers not available (no A5_vs_Astar in these results) gain" in table(proxy)[
        budget.QOI_TITLES["H3c"]][6][3]


def test_f1_uses_the_number_of_long_horizons_of_the_configuration() -> None:
    """R16: F1's horizon count k comes from ``eval_horizons_lyapunov`` (those at least 1 LT).

    Reference: M3: F1 = (k/sqrt(pi)) h/z for k = 2 or 3, h = 0.01 here; the default configuration
    has 1, 2, 4 LT (k = 3); (0.5, 1, 2) has k = 2: F1 = 2/sqrt(pi) * 0.01 / 1.959963984540054;
    four long horizons are not tabulated: "F1 not computable: tabulated for 2 or 3 horizons, this
    configuration has 4". Exact text; the numbers are checked at 3 significant digits.
    """
    from scipy.stats import norm

    def cell(config) -> str:  # noqa: ANN001
        results, systems = budget_results(full_system(), names=("lorenz63",))
        return tables_of(budget.budget_lines(results, systems, config))[
            budget.QOI_TITLES["H2a(i)"]][0][3]

    z = norm.ppf(0.975)
    assert f"F1 = {3 / math.sqrt(math.pi) * 0.01 / z:.3g} (independent draw noise across 3 " \
        "horizons" in cell(SMOKE)
    two = dataclasses.replace(SMOKE, eval_horizons_lyapunov=(0.5, 1.0, 2.0))
    assert f"F1 = {2 / math.sqrt(math.pi) * 0.01 / z:.3g} (independent draw noise across 2 " \
        "horizons" in cell(two)
    four = dataclasses.replace(SMOKE, eval_horizons_lyapunov=(1.0, 2.0, 4.0, 8.0))
    assert cell(four).endswith("F1 not computable: tabulated for 2 or 3 horizons, this "
                               "configuration has 4")


def test_lm_row_text_is_true_whatever_the_merge_order(monkeypatch: pytest.MonkeyPatch) -> None:
    """R16: with ``LM_SUMMARY_PATH`` None the row says the path is not set, and reads nothing.

    Reference: the review: "not read: LM_SUMMARY_PATH not set until WU-0005.4 merges" must hold
    even if a summary is present in the results (a WU-0005.4 that merged first). Once the path is
    set and the summary missing the row says "absent from results"; with it present it reads it.
    """
    system = full_system()
    system["handling"] = {"lm": {"median_residual": 1.0, "fraction_no_decrease": 0.0}}
    results, systems = budget_results(system, names=("lorenz63",))

    def cell() -> str:
        return tables_of(budget.budget_lines(results, systems, SMOKE))[
            budget.QOI_TITLES["H3c"]][4][3]

    assert cell() == ("not estimated: LM_SUMMARY_PATH not set (the location of the WU-0005.4 "
                      "summary is not read until WU-0005.4 merges)")
    monkeypatch.setattr(budget, "LM_SUMMARY_PATH", ("handling", "missing"))
    assert cell() == "not estimated: WU-0005.4 summary absent from results"
    monkeypatch.setattr(budget, "LM_SUMMARY_PATH", ("handling", "lm"))
    assert "median residual/(3.36ρ²) = " in cell()
