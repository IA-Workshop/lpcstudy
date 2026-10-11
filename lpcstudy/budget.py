"""Report text for the uncertainty budget and interval labels (WU-0008).

Pure functions of the results and the configuration: no randomness, no statistic, and no number
of ``results.json`` changes. This module holds what is longer than a call site, so that
``report.py`` takes only small delimited hunks.

WU-0008.3 (this part): the four-element label of every interval (procedure, level, dependence,
multiplicity; NVVUQ.16), the figure captions, and the same caption written into each PNG.
WU-0008.4: the declaration table of the quantities of interest (NVVUQ.3, NVVUQ.22), built from
``identifiers.HYPOTHESIS_TABLE`` and ``identifiers.QOI_DECLARATIONS``.
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass

from .config import StudyConfig
from .identifiers import HYPOTHESIS_TABLE, QOI_DECLARATIONS, Hypothesis

PRIMARY_LEVEL = 1.0 - 0.05 / 3.0
"""Level of the primary intervals H2a, H2b, H3c (v3 section 7: Bonferroni over the three). A
literal copy of ``analysis.PRIMARY_LEVEL`` (this module does not import ``analysis``); a test pins
the equality."""
SECONDARY_LEVEL = 0.95
"""Level of every other interval (v3 section 7)."""
PRIMARY_KEYS = ("H2a", "H2b", "H3c")
LEVEL_TOLERANCE = 1e-12
"""A stored level is the same as the role's level if they differ by less than this (both are the
same float expression, so the difference is 0 in practice)."""
V4_RESAMPLES = 200
"""Bootstrap resamples of the V4 check, a literal of ``experiments.py`` (``(200, m_draws)``); a
test reads that source to pin the equality."""

STORED_LEVEL_PATHS: dict[str, tuple[str, ...]] = {
    "H1a": ("level",), "H1d": ("level",), "H2b": ("library_change", "level"),
    "H3b": ("weight_lambda", "level"), "H3c": ("level",)}
"""Where a result stores the level of its decision interval, by table key. The other results store
none; their label then uses the level of the row's role."""

NO_INTERVAL_KEYS = ("gain_bound", "H3a")
"""Rows that show no interval: the gain bound (a fraction) and H3a (adjusted p-values)."""


def role_level(row: Hypothesis) -> float:
    """The level of a row's intervals by its role (v3 section 7): primary or 95%."""
    return PRIMARY_LEVEL if row.key in PRIMARY_KEYS else SECONDARY_LEVEL


def level_text(level: float) -> str:
    """Report text of a level: ``1 − 0.05/3 (98.33%)`` for the primary level, else ``95%``."""
    if abs(level - PRIMARY_LEVEL) < LEVEL_TOLERANCE:
        return f"1 − 0.05/3 ({100 * level:.2f}%)"
    return f"{100 * level:g}%"


def stored_level(row: Hypothesis, result: dict) -> float | None:
    """The level stored in ``result`` for the decision interval of ``row``, or ``None`` if the
    result stores none (see ``STORED_LEVEL_PATHS``)."""
    node = result
    for part in STORED_LEVEL_PATHS.get(row.key, ()):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return None if node is result else float(node)


def row_level(row: Hypothesis, results: dict, systems: list[str]) -> float:
    """The level printed in the label of a row: the stored level, else the role's.

    Raises
    ------
    ValueError
        If a system stores a level that differs from the level of the row's role. That is a
        defect of the analysis, not something to relabel (WU-0008 L2).
    """
    nominal = role_level(row)
    for system in systems:
        found = stored_level(row, results["systems"][system][row.key])
        if found is not None and abs(found - nominal) >= LEVEL_TOLERANCE:
            raise ValueError(
                f"result {row.key} of system {system} stores level {found!r} but its role "
                f"({row.role}) has level {nominal!r}: a defect, not relabelled")
    return nominal


def _dependence(config: StudyConfig, what: str = "test states") -> str:
    return (f"resampled in blocks of {config.bootstrap_block} consecutive {what} in time order "
            f"(Künsch 1989), so dependence is kept within a block and none is assumed beyond it")


def interval_label(row: Hypothesis, level: float, config: StudyConfig) -> str:
    """The four-element label of the interval of one table row (NVVUQ.16).

    The block length and the number of resamples come from ``config``, not literals. H3a
    (adjusted p-values), H3b (bootstrap over construction states) and the gain bound (no
    interval) have their own wording.

    Parameters
    ----------
    row : Hypothesis
        The table row.
    level : float
        The level of the interval.
    config : StudyConfig
        Source of ``bootstrap_block`` and ``bootstrap_resamples``.

    Returns
    -------
    str
        ``procedure: ...; level: ...; dependence: ...; multiplicity: ...``
    """
    block, resamples = config.bootstrap_block, config.bootstrap_resamples
    if row.key == "gain_bound":
        return ("procedure: none, a fraction of states within the P1 bound is reported with no "
                "interval; level: not applicable; dependence: not applicable; multiplicity: none "
                "(reported with no pass/fail bar)")
    if row.key == "H3a":
        return ("procedure: Holm-adjusted log-rank tests between consecutive regimes, p-values "
                "with no interval; level: each adjusted p must be below 0.01; dependence: the "
                "log-rank test treats states as independent, serial dependence between "
                "neighbouring states is not modelled; multiplicity: Holm over the consecutive "
                "comparisons within a system, intersection–union across systems")
    if row.key == "H3b":
        procedure = (f"moving-block bootstrap percentile interval over construction states, "
                     f"blocks of {block} consecutive states in time order, B = {resamples}")
        dependence = _dependence(config, "construction states")
    else:
        what = "eligible (small-error) test states" if row.key == "H2a" else "test states"
        procedure = (f"moving-block bootstrap percentile interval, blocks of {block} "
                     f"consecutive {what} in time order, B = {resamples}")
        dependence = _dependence(config, what)
    if row.key in PRIMARY_KEYS:
        multiplicity = ("Bonferroni over the three primaries (H2a, H2b, H3c), intersection–union "
                        "across systems, every part of the criterion must pass")
    elif row.role == "estimate":
        multiplicity = "none (an estimate, read by the table of v3 section 7, not decided)"
    else:
        multiplicity = ("none (secondary, unadjusted), intersection–union across systems, "
                        "every part of the criterion must pass")
    return (f"procedure: {procedure}; level: {level_text(level)}; dependence: {dependence}; "
            f"multiplicity: {multiplicity}")


def interval_label_lines(results: dict, systems: list[str], config: StudyConfig) -> list[str]:
    """Label lines to follow the verdict table: one line per row that has a result (WU-0008.3).

    A table row without a verdict (no result) has no line. Each line starts with the row id and
    ends the paragraph; the block is preceded by a blank line, so it follows the table.
    """
    lines = ["", "Interval labels, one per row (procedure, level, dependence and multiplicity; "
             "NVVUQ.16):", ""]
    for row in HYPOTHESIS_TABLE:
        if row.key not in results["verdicts"]:
            continue
        label = interval_label(row, row_level(row, results, systems), config)
        role = "" if row.v3_id == f"({row.role})" else f" ({row.role})"  # gain bound: "(reported)"
        lines.append(f"- {row.v3_id}{role} — {label}")
    return lines


def v4_label_line(config: StudyConfig) -> str:
    """The label of the V4 row of the validation table: its half-width is a bootstrap interval.

    V4 resamples the M noise draws of each state independently (``experiments.py``), not the
    block bootstrap of the verdicts: the draws are independent by construction.
    """
    return (f"V4 half-width — procedure: ordinary percentile bootstrap over the "
            f"M = {config.n_oracle_draws} noise draws of each state, {V4_RESAMPLES} resamples (not "
            f"the moving-block bootstrap of the verdicts), half-width of the 2.5% to 97.5% range, "
            f"median over states; level: 95%; dependence: the noise draws are independent by "
            f"construction, so no blocking; multiplicity: none (a validation check with bar "
            f"0.05).")


# ------------------------------------------------------------------------------ figure captions


@dataclass(frozen=True)
class FigureCaption:
    """The caption of one figure file.

    Attributes
    ----------
    text : str
        What is plotted and what any band is.
    interval_level : float or None
        The level of a confidence interval drawn in the figure; ``None`` if no interval is drawn
        (every current figure: the caption then says so).
    """

    text: str
    interval_level: float | None = None


FIGURE_CAPTIONS: dict[str, FigureCaption] = {
    "separation_weight_vs_horizon.png": FigureCaption(
        "Median of the oracle weight w* on CP against the horizon, per system; the shaded band is "
        "the inter-quartile range of w* across test states, not a confidence interval. The "
        "dotted line is 1 Lyapunov time (30 steps). No confidence interval is shown."),
    "kaplan_meier_by_rule.png": FigureCaption(
        "Kaplan–Meier curves of Pr(T > H), the realized horizon at the primary tolerance, for "
        "each allocation rule A0 to A5 and A*, per system. Point curves only; no interval is "
        "shown."),
    "regret_vs_regimes.png": FigureCaption(
        "Abstraction regret (percent of the best-single MSE) against the number of regimes K, "
        "per system; the dotted line is the 5% criterion. Point values only; no interval is "
        "shown."),
    "knob_response_library.png": FigureCaption(
        "Median oracle weight w* at the reference horizon against the library size n_lib, one "
        "curve per noise level ρ (percent of σ_x), per system. Medians only; the stored "
        "intervals of the medians are in results.json and are not drawn. No interval is shown."),
}
"""One caption per file written by ``report.make_figures``, keyed by file name (WU-0008.3)."""


def figure_caption(name: str, config: StudyConfig,
                   captions: dict[str, FigureCaption] | None = None) -> str:
    """The caption text of a figure file, with the interval statement if it draws an interval.

    Parameters
    ----------
    name : str
        File name, a key of ``captions``.
    config : StudyConfig
        Source of the block length and the number of resamples of a drawn interval.
    captions : dict[str, FigureCaption], optional
        Caption table; ``FIGURE_CAPTIONS`` by default (a test passes a synthetic one).

    Raises
    ------
    KeyError
        If the file has no caption: every figure file has one.
    """
    entry = (FIGURE_CAPTIONS if captions is None else captions)[name]
    if entry.interval_level is None:
        return entry.text
    return (f"{entry.text} Intervals: moving-block bootstrap, blocks of {config.bootstrap_block} "
            f"consecutive test states in time order, B = {config.bootstrap_resamples}, level "
            f"{level_text(entry.interval_level)}.")


def figure_caption_lines(config: StudyConfig) -> list[str]:
    """The ``## Figures`` section of RESULTS.md: one caption per file of ``make_figures``."""
    lines = ["## Figures", "",
             "Written to `figures/` next to this file; each PNG carries the same caption.", ""]
    lines += [f"- `{name}`: {figure_caption(name, config)}" for name in FIGURE_CAPTIONS]
    return lines


def caption_figure(fig, name: str, config: StudyConfig,
                   captions: dict[str, FigureCaption] | None = None) -> None:
    """Write the caption of ``name`` at the bottom of ``fig``, leaving the axes their room.

    The figure grows taller by the height of the wrapped caption and the layout is redone with
    the caption's strip reserved, so the caption never overlaps an axis. Call after
    ``fig.tight_layout()`` and before ``fig.savefig``.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure to caption.
    name : str
        File name the figure will be saved under (a key of ``captions``).
    config : StudyConfig
        Configuration (for an interval-bearing caption).
    captions : dict[str, FigureCaption], optional
        Caption table; ``FIGURE_CAPTIONS`` by default.
    """
    size = 6.5  # points
    width, height = fig.get_size_inches()
    per_line = max(20, int(width * 72 / (0.55 * size)))
    wrapped = textwrap.fill(figure_caption(name, config, captions), width=per_line)
    extra = (wrapped.count("\n") + 1) * size * 1.4 / 72 + 0.12
    fig.set_size_inches(width, height + extra)
    fig.tight_layout(rect=(0, extra / (height + extra), 1, 1))
    fig.text(0.01, 0.01, wrapped, ha="left", va="bottom", fontsize=size, color="#52514e")


# ------------------------------------------------------------------ quantity-of-interest table

QOI_COLUMNS = ("ID", "Definition", "Units and conventions", "Criterion",
               "Decision-relevant error", "Decision informed", "Confirmatory or exploratory")
"""Columns of the declaration table: the five items of NVVUQ.3 and the status of NVVUQ.22."""


def general_label(config: StudyConfig) -> str:
    """One label for the intervals quoted in the criteria of the declaration table (v3 section 7)."""
    block, resamples = config.bootstrap_block, config.bootstrap_resamples
    return (f"Intervals named in the criteria column — procedure: moving-block bootstrap "
            f"percentile interval, blocks of {block} consecutive states in time order, "
            f"B = {resamples}; level: {level_text(PRIMARY_LEVEL)} for H2a, H2b and H3c, "
            f"{level_text(SECONDARY_LEVEL)} for every other row; dependence: kept within a block "
            f"of {block}, none assumed beyond it; multiplicity: Bonferroni over the three "
            f"primaries, intersection–union across systems, Holm within H3a, none for the "
            f"secondaries. The labels of each row are under the verdict table.")


def _escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def qoi_declaration_lines(config: StudyConfig) -> list[str]:
    """The ``## Quantities of interest (NVVUQ.3)`` section: one row per table row (WU-0008.4).

    The criterion column is ``row.criterion`` verbatim; the other cells are
    ``identifiers.QOI_DECLARATIONS[row.key]``. A table row without a declaration raises
    ``KeyError`` (a QoI is never reported undeclared).

    Parameters
    ----------
    config : StudyConfig
        Source of the block length and the number of resamples named in the closing label.

    Returns
    -------
    list[str]
        The Markdown lines: heading, one introductory sentence, the table, and the label of the
        intervals its criteria name.
    """
    lines = ["## Quantities of interest (NVVUQ.3)", "",
             "Every row of the identifier table is declared with its definition, units, "
             "criterion, the error that would change the decision, and the decision it informs "
             "(NVVUQ.3), and with its status (NVVUQ.22). Time is in observation steps "
             "(1 Lyapunov time = 30 steps), noise ρ is a fraction of σ_x, latent states are "
             "whitened, and errors are measured against the noise-free truth.", "",
             "| " + " | ".join(QOI_COLUMNS) + " |", "|" + "---|" * len(QOI_COLUMNS)]
    for row in HYPOTHESIS_TABLE:
        declared = QOI_DECLARATIONS[row.key]
        cells = [row.v3_id, declared["definition"], declared["units"], row.criterion,
                 declared["decision_error"], declared["decision"], declared["status"]]
        lines.append("| " + " | ".join(_escape(cell) for cell in cells) + " |")
    lines += ["", general_label(config)]
    return lines

