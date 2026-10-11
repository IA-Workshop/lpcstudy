"""Interval labels, figure captions and the QoI declaration table (WU-0008.3, WU-0008.4).

The references are strings written out by hand from v3 section 7 (levels, block length, number
of resamples, multiplicity), from the plan's acceptance criteria L1 to L3 and Q1, and from
matplotlib's own text extents; none is produced by the code under test. All checks are exact
(strings, counts, an inequality of two bounding boxes), so there is no tolerance to justify.
"""

from __future__ import annotations

import dataclasses
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
        else:
            assert "level: 95%" in label and "Bonferroni" not in label, row.key
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
