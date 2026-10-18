"""Fixed report texts: interval labels, figure captions, uncertainty budget.

A statistic without its uncertainty is not a result. This module writes, as
plain text for ``RESULTS.md``, three things that tell a reader how far each
number can be trusted:

* the four-element label of every confidence interval (the procedure that made
  it, its level, how serial dependence was handled, and how multiple tests were
  adjusted; NVVUQ.16);
* the caption of each figure, which ``report.py`` also writes into the PNG file;
* the declaration table of the quantities of interest (NVVUQ.3, NVVUQ.22) and
  the uncertainty budget (NVVUQ.15): one table for each primary quantity, with
  nine rows that size every source of error (sampling, bootstrap Monte Carlo
  error, discretization, iteration, round-off, proxy error, model form and the
  coverage of the interval procedure).

The functions here are pure: they read the ``results`` dictionary and the
configuration and return lists of text lines. They use no randomness and change
no number in ``results.json``. ``report.py`` calls them; the long texts live
here so that ``report.py`` stays short. The budget follows the design M1 to M9
of the applied mathematician (DEC-0024). In short: the bias from finite oracle
draws M is stated and not sized (only the indicative formulas F1 and F2 are
given), discretization error is 0 by LPC.NV.1 (truth and model share the
discrete map), the iterative error is not estimated, round-off is taken as 1e-4
of the interval, the coverage rates of the WU-0006 simulation give the size of
the interval-procedure error, and a numerical row is flagged unless it is under
10% of the sampling half-width.

Read ``budget_lines`` first for the budget, and ``interval_label`` for the
labels.
"""

from __future__ import annotations

import math
import textwrap
from dataclasses import dataclass
from statistics import NormalDist

from .config import StudyConfig
from .identifiers import HYPOTHESIS_TABLE, QOI_DECLARATIONS, Hypothesis

# Level of the primary intervals H2a, H2b, H3c (v3 section 7: Bonferroni over
# the three). A literal copy of ``analysis.PRIMARY_LEVEL`` (this module does
# not import ``analysis``); a test pins the equality.
PRIMARY_LEVEL = 1.0 - 0.05 / 3.0
# Level of every other interval (v3 section 7).
SECONDARY_LEVEL = 0.95
PRIMARY_KEYS = ("H2a", "H2b", "H3c")
# A stored level is the same as the role's level if they differ by less than
# this (both are the same float expression, so the difference is 0 in
# practice).
LEVEL_TOLERANCE = 1e-12
# Bootstrap resamples of the V4 check, a literal of ``experiments.py``
# (``(200, m_draws)``); a test reads that source to pin the equality.
V4_RESAMPLES = 200

# Where a result stores the level of each of its decision intervals, by table
# key: a tuple of paths, in which ``*`` stands for every key of the dict at
# that point (H2e: each noise level). The other results store none; their
# label then uses the level of the row's role.
STORED_LEVEL_PATHS: dict[str, tuple[tuple[str, ...], ...]] = {
    "H1a": (("level",),),
    "H1d": (("level",),),
    "H2b": (("library_change", "level"),),
    "H2e": (("by_noise", "*", "level"),),
    "H3b": (("weight_lambda", "level"), ("D", "level")),
    "H3c": (("level",),),
}


def role_level(row: Hypothesis) -> float:
    """Return the confidence level of a row's intervals, set by its role.

    The three primary hypotheses (H2a, H2b, H3c) share the level 1 - 0.05/3;
    every other row uses 95% (v3 section 7).
    """
    return PRIMARY_LEVEL if row.key in PRIMARY_KEYS else SECONDARY_LEVEL


def level_text(level: float) -> str:
    """Return the report text of a confidence level.

    The primary level prints as ``1 − 0.05/3 (98.33%)``; any other level prints
    as a plain percentage such as ``95%``.
    """
    if abs(level - PRIMARY_LEVEL) < LEVEL_TOLERANCE:
        return f"1 − 0.05/3 ({100 * level:.2f}%)"
    return f"{100 * level:g}%"


def stored_levels(row: Hypothesis, result: dict) -> list[float]:
    """Return the levels that a result stored for the intervals of one row.

    ``STORED_LEVEL_PATHS`` says where to look (a path of keys into ``result``,
    where ``*`` matches every key at that point). The list is empty if the
    result stores no level.
    """
    found = []
    for path in STORED_LEVEL_PATHS.get(row.key, ()):
        nodes = [result]
        for part in path:
            nodes = [
                child
                for node in nodes
                if isinstance(node, dict)
                for name, child in node.items()
                if part in ("*", name)
            ]
        found += [float(node) for node in nodes if node is not None]
    return found


def row_level(row: Hypothesis, results: dict, systems: list[str]) -> float:
    """Return the level to print in the label of a row.

    This is the level stored in the results, which must equal the level of the
    row's role.

    Raises
    ------
    ValueError
        If a system stores a level that differs from the level of the row's
        role. That is a defect of the analysis, not something to relabel
        (WU-0008 L2).
    """
    nominal = role_level(row)
    for system in systems:
        for found in stored_levels(row, results["systems"][system][row.key]):
            if abs(found - nominal) >= LEVEL_TOLERANCE:
                raise ValueError(
                    f"result {row.key} of system {system} stores level "
                    f"{found!r} but its role ({row.role}) has level "
                    f"{nominal!r}: a defect, not relabeled"
                )
    return nominal


def _dependence(config: StudyConfig, what: str = "test states") -> str:
    """Return the label text on serial dependence for the block bootstrap.

    ``what`` names the resampled units (test states or construction states).
    """
    return (
        f"resampled in blocks of {config.bootstrap_block} consecutive {what} "
        "in time order (Künsch 1989), so dependence is kept within a block "
        "and none is assumed beyond it"
    )


def iterative_label(config: StudyConfig) -> str:
    """Return the statement that the PLP iterative error is unverified.

    This is DEC-0024.

    The PLP forecaster fits its starting state with a fixed number of
    Levenberg-Marquardt iterations. The number comes from
    ``config.estimator_refine_steps``, so the label stays true under a study
    with another budget.
    """
    return (
        f"iterative error: the fixed {config.estimator_refine_steps}-iteration "
        "Levenberg–Marquardt error of the PLP estimator is not estimated and "
        "is unverified (DEC-0024)"
    )


H3B_COVERAGE = (
    "coverage not measured: the interval conditions on the fitted proxies and "
    "is not guaranteed to cover, because the split variable can switch between "
    "resamples (the bootstrap of a non-smooth functional; the WU-0006 coverage "
    "study has no H3b case)"
)


def interval_label(row: Hypothesis, level: float, config: StudyConfig) -> str:
    """Return the four-element label of one row's interval (NVVUQ.16).

    The four elements are the procedure, the level, the handling of dependence
    and the multiplicity adjustment. The block length and the number of
    resamples come from ``config``, not from literals. H3a (adjusted p-values),
    H3b (bootstrap over construction states) and the gain bound (no interval)
    have their own wording.

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
        return (
            "procedure: none, a fraction of states within the P1 bound is "
            "reported with no interval; level: not applicable; dependence: not "
            "applicable; multiplicity: none (reported with no pass/fail bar)"
        )
    if row.key == "H3a":
        return (
            "procedure: Holm-adjusted log-rank tests between consecutive "
            "regimes, p-values with no interval; level: each adjusted p must "
            "be below 0.01; dependence: the log-rank test treats states as "
            "independent, serial dependence between neighboring states is not "
            "modeled; multiplicity: Holm over the consecutive comparisons "
            "within a system, intersection–union across systems"
        )
    if row.key == "H3b":
        procedure = (
            "moving-block bootstrap percentile interval over construction "
            f"states, blocks of {block} consecutive states in time order, B = "
            f"{resamples}"
        )
        dependence = _dependence(config, "construction states")
    else:
        procedure = (
            f"moving-block bootstrap percentile interval, blocks of {block} "
            f"consecutive test states in time order, B = {resamples}"
        )
        if (
            row.key == "H2a"
        ):  # DEC-0008 A4(b): all states resampled, domains re-evaluated
            procedure = procedure.replace(
                "test states",
                "test states (all of them, not only the eligible ones)",
            ) + (
                ", with the eligibility of part (i) and the domain of part "
                "(ii) re-evaluated inside each resample (DEC-0008 A4)"
            )
        dependence = _dependence(config)
    if row.key in PRIMARY_KEYS:
        multiplicity = (
            "Bonferroni over the three primaries (H2a, H2b, H3c), "
            "intersection–union across systems, every part of the criterion "
            "must pass"
        )
    elif row.role == "estimate":
        multiplicity = (
            "none (an estimate, read by the table of v3 section 7, not decided)"
        )
    else:
        multiplicity = (
            "none (secondary, unadjusted), intersection–union across systems, "
            "every part of the criterion must pass"
        )
    label = (
        f"procedure: {procedure}; level: {level_text(level)}; dependence: "
        f"{dependence}; multiplicity: {multiplicity}"
    )
    if row.key == "H3b":
        return f"{label}; {H3B_COVERAGE}"
    return (
        f"{label}; {iterative_label(config)}"
        if row.key in PRIMARY_KEYS
        else label
    )


def interval_label_lines(
    results: dict, systems: list[str], config: StudyConfig
) -> list[str]:
    """Return the label lines that follow the verdict table (WU-0008.3).

    There is one line per row that has a result. A table row without a verdict
    has no line. Each line starts with the row id and ends its paragraph; the
    block starts with a blank line, so it follows the table.
    """
    lines = [
        "",
        "Interval labels, one per row (procedure, level, dependence and "
        "multiplicity; NVVUQ.16):",
        "",
    ]
    for row in HYPOTHESIS_TABLE:
        if row.key not in results["verdicts"]:
            continue
        label = interval_label(row, row_level(row, results, systems), config)
        role = (
            "" if row.v3_id == f"({row.role})" else f" ({row.role})"
        )  # gain bound: "(reported)"
        lines.append(f"- {row.v3_id}{role} — {label}")
    return lines


def v4_label_line(config: StudyConfig) -> str:
    """Return the label of the V4 row of the validation table.

    V4 checks that enough oracle draws M were used. Its half-width is an
    ordinary bootstrap over the M noise draws of each state (see
    ``experiments.py``), not the block bootstrap of the verdicts, because the
    draws are independent by construction.
    """
    return (
        "V4 half-width — procedure: ordinary percentile bootstrap over the M "
        f"= {config.n_oracle_draws} noise draws of each state, {V4_RESAMPLES} "
        "resamples (not the moving-block bootstrap of the verdicts), "
        "half-width of the 2.5% to 97.5% range, median over states; level: "
        "95%; dependence: the noise draws are independent by construction, so "
        "no blocking; multiplicity: none (a validation check with bar 0.05)."
    )


# --- Figure captions ---


@dataclass(frozen=True)
class FigureCaption:
    """The caption of one figure file.

    Attributes
    ----------
    text : str
        What is plotted and what any band is.
    interval_level : float or None
        The level of a confidence interval drawn in the figure, or ``None``
        if no interval is drawn (true of every current figure; the caption
        then says so).
    """

    text: str
    interval_level: float | None = None


# One caption per file written by ``report.make_figures``, keyed by file name
# (WU-0008.3).
FIGURE_CAPTIONS: dict[str, FigureCaption] = {
    "separation_weight_vs_horizon.png": FigureCaption(
        "Median of the oracle weight w* on CP against the horizon, per system; "
        "the shaded band is the inter-quartile range of w* across test states, "
        "not a confidence interval. The dotted line is 1 Lyapunov time (30 "
        "steps). No confidence interval is shown."
    ),
    "kaplan_meier_by_rule.png": FigureCaption(
        "Kaplan–Meier curves of Pr(T > H), the realized horizon at the primary "
        "tolerance, for each allocation rule A0 to A5 and A*, per system. "
        "Point curves only; no interval is shown."
    ),
    "regret_vs_regimes.png": FigureCaption(
        "Abstraction regret (percent of the best-single MSE) against the "
        "number of regimes K, per system; the dotted line is the 5% criterion. "
        "Point values only; no interval is shown."
    ),
    "knob_response_library.png": FigureCaption(
        "Median oracle weight w* at the reference horizon against the library "
        "size n_lib, one curve per noise level ρ (percent of σ_x), per system. "
        "Medians only; the stored intervals of the medians are in results.json "
        "and are not drawn. No interval is shown."
    ),
}


def figure_caption(
    name: str,
    config: StudyConfig,
    captions: dict[str, FigureCaption] | None = None,
) -> str:
    """Return the caption text of a figure file.

    If the figure draws an interval, the caption adds the statement of how the
    interval was made.

    Parameters
    ----------
    name : str
        File name, a key of ``captions``.
    config : StudyConfig
        Source of the block length and the number of resamples of a drawn
        interval.
    captions : dict[str, FigureCaption], optional
        Caption table; ``FIGURE_CAPTIONS`` by default (a test passes a
        synthetic one).

    Raises
    ------
    KeyError
        If the file has no caption: every figure file has one.
    """
    entry = (FIGURE_CAPTIONS if captions is None else captions)[name]
    if entry.interval_level is None:
        return entry.text
    return (
        f"{entry.text} Intervals: moving-block bootstrap, blocks of "
        f"{config.bootstrap_block} consecutive test states in time order, B = "
        f"{config.bootstrap_resamples}, level "
        f"{level_text(entry.interval_level)}."
    )


def figure_caption_lines(config: StudyConfig) -> list[str]:
    """Return the ``## Figures`` section of RESULTS.md.

    It holds one caption for each file that ``make_figures`` writes.
    """
    lines = [
        "## Figures",
        "",
        "Written to `figures/` next to this file; each PNG carries the same "
        "caption.",
        "",
    ]
    lines += [
        f"- `{name}`: {figure_caption(name, config)}"
        for name in FIGURE_CAPTIONS
    ]
    return lines


def caption_figure(
    fig,
    name: str,
    config: StudyConfig,
    captions: dict[str, FigureCaption] | None = None,
) -> None:
    """Write the caption of ``name`` at the bottom of ``fig``.

    The figure grows taller by the height of the wrapped caption, and the layout
    is redone with the caption's strip reserved, so the caption never overlaps
    an axis. Call this after ``fig.tight_layout()`` and before ``fig.savefig``.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure to caption.
    name : str
        File name the figure will be saved under (a key of ``captions``).
    config : StudyConfig
        Configuration (for a caption that names an interval).
    captions : dict[str, FigureCaption], optional
        Caption table; ``FIGURE_CAPTIONS`` by default.
    """
    size = 6.5  # points
    width, height = fig.get_size_inches()
    per_line = max(20, int(width * 72 / (0.55 * size)))
    wrapped = textwrap.fill(
        figure_caption(name, config, captions), width=per_line
    )
    extra = (wrapped.count("\n") + 1) * size * 1.4 / 72 + 0.12
    fig.set_size_inches(width, height + extra)
    fig.tight_layout(rect=(0, extra / (height + extra), 1, 1))
    fig.text(
        0.01,
        0.01,
        wrapped,
        ha="left",
        va="bottom",
        fontsize=size,
        color="#52514e",
    )


# --- Declaration table of the quantities of interest (QoIs) ---

# Columns of the declaration table: the five items of NVVUQ.3 and the status
# of NVVUQ.22.
QOI_COLUMNS = (
    "ID",
    "Definition",
    "Units and conventions",
    "Criterion",
    "Decision-relevant error",
    "Decision informed",
    "Confirmatory or exploratory",
)


def general_label(config: StudyConfig) -> str:
    """Return one label for the intervals quoted in the criteria column.

    The rule is in v3 section 7.

    The quantity-of-interest table names intervals in its criteria. This label
    says, once, how all of them were built.
    """
    block, resamples = config.bootstrap_block, config.bootstrap_resamples
    return (
        "Intervals named in the criteria column — procedure: moving-block "
        f"bootstrap percentile interval, blocks of {block} consecutive states "
        f"in time order, B = {resamples}; level: {level_text(PRIMARY_LEVEL)} "
        f"for H2a, H2b and H3c, {level_text(SECONDARY_LEVEL)} for every other "
        f"row; dependence: kept within a block of {block}, none assumed beyond "
        "it; multiplicity: Bonferroni over the three primaries, "
        "intersection–union across systems, Holm within H3a, none for the "
        "secondaries. The labels of each row are under the verdict table."
    )


def _escape(text: str) -> str:
    """Escape pipes and newlines so that text fits in one table cell."""
    return text.replace("|", "\\|").replace("\n", " ")


def qoi_declaration_lines(config: StudyConfig) -> list[str]:
    """Return the ``## Quantities of interest`` section (WU-0008.4).

    There is one row per row of the hypothesis table. The criterion column is
    ``row.criterion`` word for word; the other cells come from
    ``identifiers.QOI_DECLARATIONS[row.key]``. A table row without a declaration
    raises ``KeyError``, because a quantity of interest is never reported
    undeclared.

    Parameters
    ----------
    config : StudyConfig
        Source of the block length and the number of resamples named in the
        closing label.

    Returns
    -------
    list[str]
        The Markdown lines: heading, one introductory sentence, the table,
        and the label of the intervals its criteria name.
    """
    lines = [
        "## Quantities of interest (NVVUQ.3)",
        "",
        "Every row of the identifier table is declared with its definition, "
        "units, criterion, the error that would change the decision, and the "
        "decision it informs (NVVUQ.3), and with its status (NVVUQ.22). Time "
        "is in observation steps (1 Lyapunov time = 30 steps), noise ρ is a "
        "fraction of σ_x, latent states are whitened, and errors are measured "
        "against the noise-free truth.",
        "",
        "| " + " | ".join(QOI_COLUMNS) + " |",
        "|" + "---|" * len(QOI_COLUMNS),
    ]
    for row in HYPOTHESIS_TABLE:
        declared = QOI_DECLARATIONS[row.key]
        cells = [
            row.v3_id,
            declared["definition"],
            declared["units"],
            row.criterion,
            declared["decision_error"],
            declared["decision"],
            declared["status"],
        ]
        lines.append("| " + " | ".join(_escape(cell) for cell in cells) + " |")
    lines += ["", general_label(config)]
    return lines


# --- Uncertainty budget (WU-0008.1, .2b) ---
# One table per primary QoI, nine rows each (the eight rows of the
# ``uq-budget`` skill and the interval procedure, DEC-0021 O2). Every size
# cell is a number, ``0 (...)``, or ``not estimated: <reason>``; a missing key
# never raises and never prints a blank (PRIME.4). Row decisions: the
# applied-mathematician's design M1 to M9, accepted in DEC-0024.

# Round-off size as a fraction of max(|lo|, |hi|): the empirical
# cross-platform perturbation of the QoI-type statistics, at most 6.0e-5
# relative (DEV-0 against the v1 pilot, M5), rounded up.
ROUNDOFF_RELATIVE = 1e-4
# A numerical row is small against the sampling half-width iff its size is
# strictly below this fraction of it (M9; the skill's "at least 10 times
# smaller" differs only at equality).
FLAG_FRACTION = 0.1
LM_ABSENT = (
    "not estimated: no Levenberg–Marquardt summary (handling.cells[*].lm with "
    "estimates) in these results"
)
LM_PRESENT = (
    "not estimated: the residual bounds the error in the observation metric "
    "only (cond(JᵀJ) ≈ 1e7), so it does not convert to the QoI scale; needs a "
    "{steps} → {doubled} iteration refinement of the QoI; the residual "
    "diagnostics are in the report's 'Levenberg–Marquardt diagnostics' "
    "subsection (a diagnostic, not an estimate of this error)"
)
COVERAGE_SEEDS_TEXT = (
    "reference rates from scratch seed 20261011 (m2_coverage.py), run-2 counts "
    'from seed 6006 (make_rng(6006, "wu0006", ...)); neither is a '
    "registered seed"
)
CONDITIONAL_SENTENCE = (
    "Conditional on one realization per system of the trajectory, the library "
    "noise and the trained networks. Between-realization variability is not "
    "estimated (v3 section 8, future work)."
)
H3C_SENTENCE = (
    "Conditional on the fitted A4 and A5. Fit-stage variability is outside the "
    "interval and not estimated."
)
ITERATIVE_SENTENCE = (
    "The iterative (Levenberg–Marquardt) error is not estimated, so the "
    "numerical error of this QoI is partly unverified (PRIME.3, NVVUQ.9; "
    "DEC-0024)."
)
LM_DEVELOPMENT_NOTE = (
    "Development evidence on the iterative error, not a sealed result: the "
    "Levenberg–Marquardt doubling study on the development seed DEV-0 (15, 30 "
    "and 60 iterations; docs/study/lm_doubling_dev0_report_v3.md) finds the "
    "iterative change below 10% of the sampling half-width (class N) for 5 of "
    "the 18 parts of the five QoIs and three systems (this QoI: {own}), and "
    "does not show it below 10% for the other 13 (X, not negligible, 6; U, not "
    "certified, 7). A systematic iterative change does not shrink with n while "
    "the half-width does, so its size against the half-width grows from the "
    "pilot preset to the full preset by about √(n_full/n_pilot), ×{factor} for "
    "this QoI ({sizes} in the two presets). The projection is stated, not "
    "applied: a 30/60-iteration twin of the full-size run would remove it. The "
    "iterative row of this report stays not estimated."
)
# Per primary QoI: the projection factor sqrt(n_full/n_pilot), the sizes it
# rests on (pilot and full presets), and the QoI's own count of class N parts,
# all quoted as text, never computed here (B7, owner ruling of 2026-10-18).
# Factors and sizes: ``docs/agent/records/work/WU-0005.6-lm-doubling.md`` (the
# full-n projection); counts: the table of section 3 of
# ``docs/study/lm_doubling_dev0_report_v3.md``.
LM_PROJECTION = {
    "H2a(i)": ("1.41", "500 → 1000 test states", "class N in 0 of 3 parts"),
    "H2a(ii)": ("1.41", "500 → 1000 test states", "class N in 3 of 6 parts"),
    "H2b(i)": ("1.83", "300 → 1000 sweep states", "class N in 0 of 3 parts"),
    "H2b(ii)": ("1.83", "300 → 1000 sweep states", "class N in 2 of 3 parts"),
    "H3c": ("1.41", "500 → 1000 test states", "class N in 0 of 3 parts"),
}
WIDENING_SENTENCE = (
    "A numerical row at or above 10% of the sampling half-width is flagged, "
    "not widened: the rule of the uq-budget skill is to widen the interval or "
    "refine, and which of the two is the owner's choice; this report does not "
    "widen."
)
# The texts of ORACLE_INCLUDED, WIDENING_SENTENCE and the R_ref of
# COVERAGE_WU0006 are those of DEC-0024 addendum A1
# (docs/agent/records/decisions.md), which amends M1 (a) and M7. DEF0020_TEXT
# is the row-9 text of addendum A2 of the same file, which replaces the A1
# sentence after the owner ratified Option C (DEC-0026 item 2, 2026-10-12).
DEF0020_TEXT = (
    "DEF-0020: Option C in force (owner-ratified 2026-10-12, DEC-0026; "
    "ASSERT_ROADMAP_BOUNDS = False): the WU-0006 ROADMAP-bound coverage rows "
    "are recorded characterization rows (outcome reported, not asserted) and "
    "the consistency ranges are the defect test; no bound, level or R is "
    "changed. Whether the study widens its intervals or uses another procedure "
    "(longer block, studentized, BCa) is a separate, undecided design question "
    "for the owner and the applied-mathematician"
)


@dataclass(frozen=True)
class CoverageCase:
    """One WU-0006 coverage case at the primary level 1 - 0.05/3.

    WU-0006 was a simulation that measured how often the block-5 percentile
    interval covers the true value.

    Attributes
    ----------
    rate : float
        Reference coverage of the block-5 percentile interval (independent
        implementation, scratch seed 20261011, R_ref 2*10^4 to 4*10^4 for
        the cases used here, SE below 0.0013; the range 10^4 to 4*10^4 of
        the math note includes C6, which no quantity of interest uses).
    rate_se : float
        Monte Carlo standard error of ``rate``.
    r_ref : int
        Replications of the reference run (hand transcription from the math
        note and its scripts: 40000 for C1, C4, C8; 20000 for C3, C7, C4h;
        the C7 pooled 60000 applies to its verdict counts only, not to the
        coverage rate).
    count : int
        Run-2 coverage count out of 1000 (the production check, beside the
        reference).
    n_states : int
        States of the synthetic series.
    design : str
        What was simulated.
    """

    rate: float
    rate_se: float
    r_ref: int
    count: int
    n_states: int
    design: str


COVERAGE_PROVENANCE = (
    "WU-0006 run 2, log `runs/tests/slow-20261011T165447Z.log`, Log table at "
    "b73bbed; reference rates (scratch seed 20261011, m2_coverage.py) from "
    "docs/agent/notes/2026-10-11-math-wu0006.md and, for C4h, "
    "docs/agent/notes/2026-10-11-math-wu0008-scripts/m7b.log, which only "
    "transcribes them"
)
# WU-0006 coverage at level 1 - 0.05/3, by (case, phi): the reference rate
# with its SE as the size, the run-2 count beside it (O3 of DEC-0021:
# constants with provenance; tests parse the WU-0006 Log table and the math
# note as the independent reference).
COVERAGE_WU0006: dict[tuple[str, float], CoverageCase] = {
    ("C1", 0.0): CoverageCase(
        0.9800, 0.0007, 40000, 983, 500, "mean, Gaussian AR(1)"
    ),
    ("C1", 0.3): CoverageCase(
        0.9695, 0.0009, 40000, 969, 500, "mean, Gaussian AR(1)"
    ),
    ("C3", 0.0): CoverageCase(
        0.9807, 0.0010, 20000, 984, 500, "median, Gaussian AR(1)"
    ),
    ("C3", 0.3): CoverageCase(
        0.9732, 0.0011, 20000, 973, 500, "median, Gaussian AR(1)"
    ),
    ("C4", 0.0): CoverageCase(
        0.9772,
        0.0007,
        40000,
        971,
        500,
        "ratio of means, log-normal pair, sigma 1",
    ),
    ("C4", 0.3): CoverageCase(
        0.9715,
        0.0008,
        40000,
        961,
        500,
        "ratio of means, log-normal pair, sigma 1",
    ),
    ("C7", 0.0): CoverageCase(
        0.9794, 0.0010, 20000, 972, 500, "partial correlation, interior part"
    ),
    ("C7", 0.3): CoverageCase(
        0.9762, 0.0011, 20000, 977, 500, "partial correlation, interior part"
    ),
    ("C8", 0.0): CoverageCase(
        0.9806, 0.0007, 40000, 987, 300, "paired mean, Gaussian AR(1)"
    ),
    ("C8", 0.3): CoverageCase(
        0.9682, 0.0009, 40000, 972, 300, "paired mean, Gaussian AR(1)"
    ),
    ("C4h1.5", 0.0): CoverageCase(
        0.9744, 0.0011, 20000, 965, 500, "ratio of means, log-normal, sigma 1.5"
    ),
    ("C4h2", 0.0): CoverageCase(
        0.9669, 0.0013, 20000, 984, 500, "ratio of means, log-normal, sigma 2"
    ),
}

QOI_IDS = ("H2a(i)", "H2a(ii)", "H2b(i)", "H2b(ii)", "H3c")
QOI_TITLES = {
    "H2a(i)": "H2a(i): median range of w* over the initial segments of the "
    "horizons 1, 2, 4 LT",
    "H2a(ii)": "H2a(ii): partial correlation of w* (indicator or logit) with "
    "Λ̃ given the seeds",
    "H2b(i)": "H2b(i): mean per-state rank correlation of w* with ρ",
    "H2b(ii)": "H2b(ii): mean paired change in w* from N_lib = 10³ to 10⁴ at ρ "
    "= 1%",
    "H3c": "H3c: MSE ratio, regimes (A5) over closed form (A4), at H_ref",
}
QOI_KEYS = {
    "H2a(i)": "H2a",
    "H2a(ii)": "H2a",
    "H2b(i)": "H2b",
    "H2b(ii)": "H2b",
    "H3c": "H3c",
}
# WU-0006 cases mapped to each QoI and part (M7): H2a(i) is a proxy (C3); the
# zero and the w* = 1 parts of H2a(ii) have no case; H2b(i) is C8 (one
# per-state series at the sweep size). The C1 constants are kept as data (M7
# allows citing C1 beside H2b(i)) but the cell does not print them.
QOI_COVERAGE: dict[str, dict[str, tuple[tuple[str, float], ...]]] = {
    "H2a(i)": {"": (("C3", 0.0), ("C3", 0.3))},
    "H2a(ii)": {"interior": (("C7", 0.0), ("C7", 0.3))},
    "H2b(i)": {"": (("C8", 0.0), ("C8", 0.3))},
    "H2b(ii)": {"": (("C8", 0.0), ("C8", 0.3))},
    "H3c": {"": (("C4", 0.0), ("C4", 0.3), ("C4h1.5", 0.0), ("C4h2", 0.0))},
}

ROW_NAMES = (
    ("Oracle Monte Carlo (M draws per state)", "aleatory"),
    ("Sampling of test states", "aleatory"),
    ("Bootstrap Monte Carlo error", "numerical"),
    ("Discretization (RK4)", "numerical"),
    ("Iterative (Levenberg–Marquardt)", "numerical"),
    ("Round-off", "numerical"),
    ("Proxy error (deployable against oracle)", "estimator"),
    ("Model form: exact model, three systems, scalar observable", "epistemic"),
    (
        "Interval procedure (coverage of the block-5 percentile interval)",
        "statistical method",
    ),
)
# The "included in the reported interval?" cell of each row; row 0 is per QoI
# (``ORACLE_INCLUDED``).
INCLUDED = (
    "",
    "yes",
    "no",
    "no",
    "no",
    "no",
    "reported separately",
    "no",
    "no",
)
# Row 1 of the Included column by QoI (the applied-mathematician's wording,
# DEC-0024 addendum A1; it amends M1 (a) and M7: the M-draw variance is inside
# the interval of H2a and H2b, and not in H3c's).
ORACLE_INCLUDED = {
    "H2a(i)": "variance: yes (states resampled with their M-draw w*; "
    "eligibility redone in each resample; asymptotic for a median); finite-M "
    "bias: no",
    "H2a(ii)": "variance: yes in every part (target, domain and seed controls "
    "resampled with the states; asymptotic); finite-M bias: no",
    "H2b(i)": "variance: yes (mean of per-state Spearman values, each from "
    "that state's own draws); finite-M bias: no",
    "H2b(ii)": "variance: yes (mean of per-state paired changes; same unit "
    "draws at both N_lib); finite-M clip-boundary bias: no",
    "H3c": "no: test-state M draws do not enter the QoI; fit-stage M-draw "
    "noise (A4 proxies; A5 tree, leaf weights, K) is conditioned on",
}
H2A_ONE_NOTE = (
    "Whether the w* = 1 part is added at all is decided once on the full "
    "sample and is not resampled."
)
BUDGET_HEADING = "## Uncertainty budget (NVVUQ.15)"

NOT_ESTIMATED = "not estimated: "
INTERVAL_UNBOUNDED = "not estimated: interval unbounded"


@dataclass(frozen=True)
class _Part:
    """The interval of one part of a QoI in one system, as stored."""

    label: str
    ci: list | None
    se: list | None
    n_failed: int | None
    n_states: int | None = None


def below_tenth(size: float | None, half_width: float | None) -> str:
    """Flag a numerical row: "yes" if ``size < 0.1 * half_width``.

    The comparison is strict (M9). The result is "not estimated" if the size is
    missing, and "not estimated: interval unbounded" if the half-width is
    missing or not finite.
    """
    if size is None:
        return "not estimated"
    if half_width is None or not math.isfinite(half_width):
        return INTERVAL_UNBOUNDED
    return "yes" if size < FLAG_FRACTION * half_width else "no"


def _num(value: float) -> str:
    """Format a number with three significant digits."""
    return f"{value:.3g}"


def _half_width(ci: list | None) -> float | None:
    """Return half the width of a stored interval, or ``None``."""
    if not isinstance(ci, (list, tuple)) or len(ci) != 2 or None in ci:
        return None
    return (float(ci[1]) - float(ci[0])) / 2.0


def oracle_range_bound(v4_half_width: float, horizons: int = 3) -> float:
    """Return F1 of M3: the indicative bias of the H2a(i) median range.

    F1 is the bias of a zero-range state caused by a finite number of oracle
    draws.

    The bias comes from using a finite number M of oracle draws. The expected
    range of k independent N(0, s^2) values is ``2 s / sqrt(pi)`` for k = 2 and
    ``3 s / sqrt(pi)`` for k = 3. Here ``s`` is the standard deviation of the
    per-state weight at H_ref, ``s = v4_half_width / z_0.975``, because the V4
    median half-width is a 95% half-width. The draw noise is taken as
    independent across the horizons.

    F1 is an indicative value, **not a bound** on the bias of the median range
    (owner ruling OF-4; the wording is that of the draft addendum A3 to DEC-0024
    in ``docs/agent/notes/2026-10-18-owner-decision-drafts.md``, section 3.2,
    not yet entered in the ledger). When more than half of the eligible states
    have exact separation, the median of the noisy ranges lies near an upper
    quantile of the noise-only range, which is above its mean. A synthetic case
    reaches 1.38 F1 (``docs/agent/notes/2026-10-14-math-wu0003.md``, M5).

    Raises
    ------
    ValueError
        If ``horizons`` is not 2 or 3 (the expected range is tabulated only
        for those).
    """
    if horizons not in (2, 3):
        raise ValueError(
            "the expected range is tabulated for 2 or 3 horizons; got "
            f"{horizons}"
        )
    return (
        horizons
        / math.sqrt(math.pi)
        * v4_half_width
        / NormalDist().inv_cdf(0.975)
    )


def oracle_change_share(
    mean_abs_dev: float,
    used_draws: int,
    max_draws: int,
    n_states: int,
    level: float,
) -> float:
    """Return F2 of M3: the oracle-draw share of the H2b(ii) half-width.

    The share is a variance share, and the result is an upper bound.

    The result is an upper bound. V4 gives the mean absolute deviation ``a`` of
    the weight at ``M`` draws from the largest-``M`` reference. For nested
    draws, ``Var(w_M - w_Mmax) = (1 - M/M_max) s^2``, and a Gaussian has ``E|X|
    = sqrt(2/pi) sigma``, so ``s_mean = a / (sqrt(2/pi) sqrt(1 - M/M_max))``.
    Then ``F2 = z_L sqrt(2) s_mean / sqrt(n)``, where ``z_L`` is the normal
    quantile of the level. The formula assumes zero correlation of the draw
    noise across the two library sizes, and that V4's standard deviation at 10^4
    equals the one at 10^3.

    Raises
    ------
    ValueError
        If ``used_draws >= max_draws`` (V4 has no larger reference to
        compare with) or ``n_states < 1``.
    """
    if used_draws >= max_draws or n_states < 1:
        raise ValueError(
            "F2 needs V4 at a larger M than the one used, and at least one "
            "state"
        )
    s_mean = mean_abs_dev / (
        math.sqrt(2.0 / math.pi) * math.sqrt(1.0 - used_draws / max_draws)
    )
    z_level = NormalDist().inv_cdf((1.0 + level) / 2.0)
    return z_level * math.sqrt(2.0) * s_mean / math.sqrt(n_states)


def coverage_shortfall(
    rate: float, rate_se: float, level: float
) -> tuple[float, float]:
    """Return the half-width shortfall ``f = z_nom / z_obs - 1``.

    The interval covers the true value at the measured ``rate`` instead of the
    nominal ``level``. If the interval behaves like ``est +- k z_nom SE``, then
    ``rate = 2 Phi(k z_nom) - 1`` and ``k = z_obs / z_nom``, with ``z_obs =
    Phi^-1((1 + rate)/2)``. The half-width needed for the nominal coverage is
    the reported one divided by ``k``, so ``f`` is the shortfall as a fraction
    of the reported half-width (negative when the coverage is above nominal).
    The Monte Carlo standard error of ``f`` is ``z_nom / z_obs^2 * rate_se / (2
    phi(z_obs))`` (delta method).

    Returns
    -------
    tuple[float, float]
        ``f`` and its standard error.
    """
    normal = NormalDist()
    z_nom = normal.inv_cdf((1.0 + level) / 2.0)
    z_obs = normal.inv_cdf((1.0 + rate) / 2.0)
    shortfall = z_nom / z_obs - 1.0
    return shortfall, z_nom / z_obs**2 * rate_se / (2.0 * normal.pdf(z_obs))


def mc_error_reason(
    ci: list | None, n_failed: int | None, n_resamples: int, level: float
) -> str:
    """Explain why ``statistics.endpoint_mc_error`` returned None (M2).

    The reason is found from the interval and the counts. The rules are the
    helper's, in its order: (1) a bound is infinite (the A3 rule), (3) the
    binomial window leaves (0, 1) at this number of resamples B, (2) failed
    resamples reach the window.
    """
    if ci is not None and any(not math.isfinite(float(bound)) for bound in ci):
        return "bound infinite (A3)"
    alpha = (1.0 - level) / 2.0
    spread = math.sqrt(alpha * (1.0 - alpha) / n_resamples)
    if alpha - spread <= 0.0 or (1.0 - alpha) + spread >= 1.0:
        return f"B = {n_resamples} too small for the binomial window"
    if n_failed:
        return (
            f"failed resamples (F = {n_failed}) within one binomial SE of the "
            "endpoint"
        )
    return "the endpoint error is undefined for these inputs"


def _parts_of(qoi: str, system: dict) -> list[_Part] | None:
    """Return the stored interval parts of a QoI, or ``None`` if absent.

    The input is one system's results; the parts are the pieces of the criterion
    that each have an interval.
    """
    result = system.get(QOI_KEYS[qoi])
    if not isinstance(result, dict):
        return None
    if qoi == "H2a(i)":
        return [
            _Part(
                "",
                result.get("range_ci"),
                result.get("ci_mc_se"),
                result.get("range_n_failed_resamples"),
                result.get("n_eligible_states"),
            )
        ]
    if qoi == "H2a(ii)":
        parts = result.get("part_ii")
        if not isinstance(parts, dict):
            return None
        return [
            _Part(
                name,
                p.get("ci"),
                p.get("ci_mc_se"),
                p.get("n_failed_resamples"),
                p.get("n_states"),
            )
            for name, p in parts.items()
        ]
    block = {
        "H2b(i)": result.get("noise"),
        "H2b(ii)": result.get("library_change"),
        "H3c": result,
    }[qoi]
    if not isinstance(block, dict):
        return None
    return [
        _Part(
            "",
            block.get("ci"),
            block.get("ci_mc_se"),
            block.get("n_failed_resamples"),
            block.get("n_states"),
        )
    ]


def _v4(system: dict) -> tuple[tuple[float, float, int, int] | None, str]:
    """Return what the budget needs from check V4, with a reason if absent.

    The values are the median half-width, the mean absolute deviation, the M
    used and the largest M. The return value is ``(values, "")`` or ``(None,
    reason)``; the reasons tell apart V4 absent, V4 present without ``used_M``,
    and V4 present without the entry (or ``median_half_width``) of the used M.
    """
    conv = system.get("validation", {}).get("convergence")
    if not isinstance(conv, dict):
        return None, "V4 absent from these results"
    if "used_M" not in conv:
        return None, "V4 present but used_M missing"
    used = int(conv["used_M"])
    entry = conv.get(str(used))
    if not isinstance(entry, dict) or "median_half_width" not in entry:
        return (
            None,
            f"V4 present but its entry for the used M = {used} (or its "
            "median_half_width) is missing",
        )
    largest = max(int(k) for k in conv if str(k).isdigit())
    return (
        float(entry["median_half_width"]),
        float(entry.get("mean_abs_dev_from_max", math.nan)),
        used,
        largest,
    ), ""


def _long_horizons(config: StudyConfig) -> int:
    """Return the number of horizons of at least 1 Lyapunov time (LT).

    H2a(i) takes its initial segments over those horizons.
    """
    return sum(1 for h in config.eval_horizons_lyapunov if h >= 1.0)


def _oracle_cell(
    qoi: str, part: _Part, system: dict, config: StudyConfig, level: float
) -> tuple[str, str]:
    """Return row 1 of the budget: the finite-M bias statement of M3.

    The text includes F1 or F2 where a formula exists. Each "not computable"
    reason names its own cause (V4 absent, V4 without ``used_M``, V4 without the
    entry of the used M, no larger M, a missing number of states, a non-finite
    deviation).
    """
    flag = "not estimated"
    if qoi == "H2a(i)":
        v4, why = _v4(system)
        k = _long_horizons(config)
        if v4 is None:
            bound = f"; F1 not computable: {why}"
        elif k not in (2, 3):
            bound = (
                "; F1 not computable: tabulated for 2 or 3 horizons, this "
                f"configuration has {k}"
            )
        else:
            bound = (
                f"; indicative F1 = {_num(oracle_range_bound(v4[0], k))} (bias "
                f"of a zero-range state, independent draw noise across {k} "
                "horizons; not a bound on the median; V4 at H_ref only)"
            )
        return (
            NOT_ESTIMATED + "finite-M bias upward (toward fail)" + bound,
            flag,
        )
    if qoi == "H2a(ii)":
        return (
            NOT_ESTIMATED
            + "per-state draw variance on the logit scale not stored; the "
            "classical part attenuates toward 0 (favors a pass; a fail is "
            "robust)",
            flag,
        )
    if qoi == "H2b(i)":
        return (
            NOT_ESTIMATED + "draw noise flips ranks across the "
            f"{len(config.noise_levels)} ρ cells and attenuates the mean "
            "toward 0 (against a pass; a fail is not certified against it); "
            "V4 exists only at ρ = 1%",
            flag,
        )
    if qoi == "H2b(ii)":
        v4, why = _v4(system)
        if v4 is None:
            reason = f"share not computable: {why}"
        elif not part.n_states or part.n_states < 1:
            reason = (
                "share not computable: the number of states of the change is "
                "missing"
            )
        elif not math.isfinite(v4[1]):
            reason = (
                "share not computable: V4's mean_abs_dev_from_max is missing "
                "or not finite"
            )
        elif v4[2] >= v4[3]:
            reason = (
                "share not computable: V4 has no larger M than the one used "
                f"(M = {v4[2]})"
            )
        else:
            share = oracle_change_share(
                v4[1], v4[2], v4[3], part.n_states, level
            )
            reason = f"share ≈ F2 = {_num(share)}"
        return (
            NOT_ESTIMATED
            + "finite-M clip-boundary bias (≤ 0.40 s per state near a clip "
            "bound, partly canceling in the pair); variance inside the "
            "interval, " + reason,
            flag,
        )
    return (
        NOT_ESTIMATED
        + "M-draw noise enters only through the fitted A4 and A5 inputs "
        "(the interval is conditional on them)",
        flag,
    )


def _bootstrap_cell(
    part: _Part, half_width: float | None, config: StudyConfig, level: float
) -> tuple[str, str]:
    """Return row 3: the larger endpoint standard error.

    When the error is None, the cell gives the reason.
    """
    if part.ci is None:
        return NOT_ESTIMATED + "no interval in these results", "not estimated"
    if part.se is None:
        return (
            NOT_ESTIMATED
            + "no ci_mc_se in these results (written before WU-0008.2a)",
            "not estimated",
        )
    if len(part.se) != 2 or None in part.se:
        return (
            NOT_ESTIMATED
            + mc_error_reason(
                part.ci, part.n_failed, config.bootstrap_resamples, level
            ),
            "not estimated",
        )
    size = max(float(part.se[0]), float(part.se[1]))
    text = f"{_num(size)} (lower {_num(part.se[0])}, upper {_num(part.se[1])})"
    if size == 0.0:
        text = "0 (tie at the endpoint)"
    return text, below_tenth(size, half_width)


def lm_summary_present(system: dict) -> bool:
    """Return whether the results carry a Levenberg-Marquardt summary.

    The summary must hold at least one estimate.

    The summary (WU-0005.4) is ``handling.cells[<cell id>].lm`` (cell ids depend
    on the configuration). Its ``by_kind`` parts each have an ``n_estimates``.
    The summary is present if some cell has an ``lm`` block with at least one
    part with ``n_estimates > 0``, which are the rows the report's subsection
    prints.
    """
    handling = system.get("handling")
    cells = handling.get("cells") if isinstance(handling, dict) else None
    if not isinstance(cells, dict):
        return False
    for record in cells.values():
        block = record.get("lm") if isinstance(record, dict) else None
        parts = block.get("by_kind") if isinstance(block, dict) else None
        if isinstance(parts, dict) and any(
            isinstance(p, dict) and p.get("n_estimates") for p in parts.values()
        ):
            return True
    return False


def _lm_cell(system: dict, config: StudyConfig) -> tuple[str, str]:
    """Return row 5: the iterative error is always "not estimated" (M4).

    The text says why, and points to the report's diagnostics subsection when
    the summary is present. No number of the summary is printed as an estimate.
    """
    if not lm_summary_present(system):
        return LM_ABSENT, "not estimated"
    steps = config.estimator_refine_steps
    return LM_PRESENT.format(steps=steps, doubled=2 * steps), "not estimated"


def _proxy_cell(qoi: str, system: dict) -> tuple[str, str]:
    """Return row 7: the proxy error.

    It is 0 by construction for the oracle-defined quantities. H3c reports the
    fidelity of the deployable rules instead (M8).
    """
    if qoi != "H3c":
        return (
            "0: by construction (oracle w*, oracle seeds, oracle Λ̃; no "
            "deployable proxy enters)",
            "—",
        )
    recovery = system.get("oracle_recovery")
    rows = (
        system.get("H1d", {}).get("rows")
        if isinstance(system.get("H1d"), dict)
        else None
    )

    def share(key: str, reference: str) -> str:
        if not isinstance(recovery, dict) or key not in recovery:
            return f"not available (no {key} in these results)"
        value = recovery[key]
        if value is None or not math.isfinite(float(value)):
            # The denominator is not positive (M8).
            return f"not computable (A2 ≤ {reference})"
        return f"{_num(100 * float(value))}% of {reference}"

    def rho(name: str) -> str:
        value = (
            rows.get(name, {}).get("spearman")
            if isinstance(rows, dict)
            else None
        )
        return "n/a" if value is None else _num(float(value))

    return (
        NOT_ESTIMATED
        + "the QoI compares two deployable rules, so proxy error is not an "
        "error of this QoI; reported separately: A4 recovers "
        f"{share('A4_vs_A4o', 'A4o')} gain over A2, A5 recovers "
        f"{share('A5_vs_Astar', 'A*')} gain; H1d Spearman, proxy against "
        f"oracle: analog seed {rho('analog_seed')}, estimation seed "
        f"{rho('estimation_seed')}, growth {rho('growth')} (N̂ {rho('nhat')}, "
        "reported only)",
        "—",
    )


def _coverage_f(qoi: str, label: str, level: float) -> float | None:
    """Return the largest shortfall over the WU-0006 cases of a QoI part.

    This is M7.

    The result is ``None`` if no case is mapped.
    """
    cases = QOI_COVERAGE[qoi].get(label)
    if cases is None:
        return None
    return max(
        coverage_shortfall(
            COVERAGE_WU0006[c].rate, COVERAGE_WU0006[c].rate_se, level
        )[0]
        for c in cases
    )


def coverage_how(qoi: str, level: float) -> str:
    """Return the "how estimated" text of the interval-procedure row (M7).

    The text lists the cases, their coverage rates and their shortfalls.
    """
    pieces = []
    for label, cases in QOI_COVERAGE[qoi].items():
        for case in cases:
            c = COVERAGE_WU0006[case]
            f, f_se = coverage_shortfall(c.rate, c.rate_se, level)
            name = case[0] + (f" φ = {case[1]:g}")
            pieces.append(
                f"{(label + ': ') if label else ''}{name} (n = {c.n_states}, "
                f"{c.design}): reference coverage {c.rate:.4f} (SE "
                f"{c.rate_se:.4f}, R_ref {c.r_ref}), shortfall {f:+.3f} ± "
                f"{f_se:.3f} of the half-width, run 2: {c.count}/1000"
            )
    tail = (
        "; zero and w* = 1 parts: no WU-0006 case has a binary target"
        if qoi == "H2a(ii)"
        else ""
    )
    return (
        "shortfall f = z_nom/z_obs − 1 of the reference coverage (WU-0006, the "
        "block-5 percentile interval at level 1 − 0.05/3); "
        + "; ".join(pieces)
        + tail
        + "; "
        f"{COVERAGE_SEEDS_TEXT}; the study's residual lag-1 is unmeasured "
        f"(DEC-0018 O4); {DEF0020_TEXT}; source: {COVERAGE_PROVENANCE}"
    )


def _coverage_cell(
    qoi: str, part: _Part, half_width: float | None, level: float
) -> tuple[str, str]:
    """Return row 9: the shortfall of the interval procedure, with its flag.

    The size is in the units of the quantity of interest.
    """
    f_max = _coverage_f(qoi, part.label, level)
    if f_max is None:
        return (
            NOT_ESTIMATED
            + "no WU-0006 case has a binary target (C7's zero column is "
            "constant)",
            "not estimated",
        )
    if half_width is None or not math.isfinite(half_width):
        return INTERVAL_UNBOUNDED, "not estimated"
    if f_max <= 0.0:
        return "0 (coverage ≥ nominal)", "yes"
    size = f_max * half_width
    return _num(size), below_tenth(size, half_width)


def _cells(
    qoi: str,
    row: int,
    part: _Part,
    system: dict,
    config: StudyConfig,
    level: float,
) -> tuple[str, str]:
    """Return the size text and flag of one row for one part and system."""
    half_width = _half_width(part.ci)
    finite = half_width is not None and math.isfinite(half_width)
    if row == 0:
        return _oracle_cell(qoi, part, system, config, level)
    if row == 1:
        if half_width is None:
            return NOT_ESTIMATED + "no interval in these results", "—"
        if not finite:
            return (
                NOT_ESTIMATED
                + "interval unbounded (failed resamples at the A3 threshold)",
                "—",
            )
        return _num(half_width), "—"
    if row == 2:
        return _bootstrap_cell(part, half_width, config, level)
    if row == 3:
        v6 = system.get("validation", {}).get("integrator_max_dev_sigma")
        shown = (
            "V6 not in these results"
            if v6 is None
            else f"V6 = {_num(float(v6))} σ_x"
        )
        return (
            f"0 (LPC.NV.1: truth and model share the discrete map); {shown} "
            "(map against half step over 1 LT; not added)",
            "yes",
        )
    if row == 4:
        return _lm_cell(system, config)
    if row == 5:
        if half_width is None:
            return (
                NOT_ESTIMATED + "no interval in these results",
                "not estimated",
            )
        if not finite:
            return INTERVAL_UNBOUNDED, "not estimated"
        size = ROUNDOFF_RELATIVE * max(
            abs(float(part.ci[0])), abs(float(part.ci[1]))
        )
        return _num(size), below_tenth(size, half_width)
    if row == 6:
        return _proxy_cell(qoi, system)
    if row == 7:
        return (
            NOT_ESTIMATED
            + "v3 section 8 (exact model, three systems, scalar observable)",
            "—",
        )
    return _coverage_cell(qoi, part, half_width, level)


def _how(qoi: str, row: int, config: StudyConfig, level: float) -> str:
    """Return the "how estimated" text of one row of the budget table."""
    resamples = config.bootstrap_resamples
    return (
        "V4 convergence check (core cell, ρ = 1%, N_lib = 10⁴, H_ref only); "
        "the finite-M bias is stated, not sized; F1 and F2 are indicative "
        "formulas (WU-0008 M3); whether the M-draw variance is inside the "
        "interval is in the 'Included in the reported interval?' column",
        "moving-block bootstrap percentile interval (label below); size = "
        "half-width (hi − lo)/2",
        "binomial error of the percentile index, converted to the statistic's "
        "scale: SE = (Q(q + d) − Q(q − d))/2, d = √(q(1 − q)/B), B = "
        f"{resamples} (statistics.endpoint_mc_error); the larger endpoint is "
        "compared",
        "step halving (V6); the QoI is defined on the discrete map (LPC.NV.1)",
        "WU-0005.4 residual and iteration summary: does not convert to the QoI "
        "scale (M4)",
        f"empirical cross-platform perturbation, {ROUNDOFF_RELATIVE:g} × "
        "max(|lo|, |hi|) (DEVELOPMENT (DEV-0) against the v1 pilot, M5); "
        "excludes a discrete flip (one state's share in a median or a K "
        "choice)",
        (
            "not applicable to the oracle-defined QoI: no deployable proxy "
            "enters"
            if qoi != "H3c"
            else "A4 against A4o and A5 against A*, and the H1d proxy-oracle "
            "correlations (M8)"
        ),
        "not estimated; stated as a limitation (v3 section 8)",
        coverage_how(qoi, level),
    )[row]


def seed_text(results: dict) -> str:
    """Return ``DEVELOPMENT (DEV-n)`` or ``CONFIRMATORY (CONF-n)``.

    The seed id comes from the provenance block, and the text says which kind of
    seed produced the results.

    The text says which kind of seed produced the results.
    """
    block = results.get("provenance")
    seed_id = block.get("seed_id") if isinstance(block, dict) else None
    if not isinstance(seed_id, str):
        return "seed not recorded (no provenance block)"
    kind = "DEVELOPMENT" if seed_id.startswith("DEV-") else "CONFIRMATORY"
    return f"{kind} ({seed_id})"


def _join_parts(items: list[tuple[str, str]]) -> str:
    """Return one cell from the per-part texts.

    The cell is labeled by part when there is more than one part.
    """
    if len(items) == 1 and not items[0][0]:
        return items[0][1]
    return "; ".join(f"{label or 'all'}: {text}" for label, text in items)


def _table(
    qoi: str,
    results: dict,
    systems: list[str],
    config: StudyConfig,
    level: float,
    label: str,
) -> list[str]:
    """Return the budget table of one QoI, with the notes under it."""
    lines = [
        f"### {QOI_TITLES[qoi]}",
        "",
        "| Source | Type | How estimated | "
        + " | ".join(f"Size: {s}" for s in systems)
        + " | Included in the reported interval? | "
        "Below 10% of the sampling half-width? |",
        "|" + "---|" * (3 + len(systems) + 2),
    ]
    for row, (name, kind) in enumerate(ROW_NAMES):
        sizes, flags = [], []
        for system_name in systems:
            system = results["systems"][system_name]
            parts = _parts_of(qoi, system)
            if parts is None:
                text = (
                    NOT_ESTIMATED
                    + f"no {QOI_KEYS[qoi]} result in these results"
                )
                sizes.append(text)
                flags.append("not estimated")
                continue
            pairs = [
                (part.label, *_cells(qoi, row, part, system, config, level))
                for part in parts
            ]
            sizes.append(
                _join_parts([(label, text) for label, text, _ in pairs])
            )
            flags.append(
                _join_parts([(label, flag) for label, _, flag in pairs])
            )
        flag_cell = (
            flags[0]
            if len(set(flags)) == 1
            else "; ".join(f"{s}: {flag}" for s, flag in zip(systems, flags))
        )
        cells = [name, kind, _how(qoi, row, config, level).replace("|", "\\|")]
        cells += [text.replace("|", "\\|") for text in sizes]
        cells += [
            ORACLE_INCLUDED[qoi] if row == 0 else INCLUDED[row],
            flag_cell,
        ]
        lines.append("| " + " | ".join(cells) + " |")
    lines += [
        "",
        f"Interval label — {label}",
        "",
        f"Seed: {seed_text(results)}; the interval-procedure row: "
        f"{COVERAGE_SEEDS_TEXT}.",
        "",
        WIDENING_SENTENCE,
        "",
        CONDITIONAL_SENTENCE,
        "",
    ]
    if qoi == "H2a(ii)":
        lines += [H2A_ONE_NOTE, ""]
    if qoi == "H3c":
        lines += [H3C_SENTENCE, ""]
    factor, sizes, own = LM_PROJECTION[qoi]
    lines += [
        ITERATIVE_SENTENCE,
        "",
        LM_DEVELOPMENT_NOTE.format(factor=factor, sizes=sizes, own=own),
    ]
    return lines


def budget_lines(
    results: dict, systems: list[str], config: StudyConfig
) -> list[str]:
    """Return the ``## Uncertainty budget`` section (WU-0008).

    There is one table per primary quantity of interest, with nine rows each:
    the eight rows of the ``uq-budget`` skill and the interval procedure. Every
    size cell is a number, ``0 (...)`` or ``not estimated: <reason>``. Results
    written before ``ci_mc_se``, before the LM summary, or without a system's
    quantity never raise. Under each table come the interval label of
    ``interval_label``, the seed line, the 10% rule sentence, and the sentences
    of M1 (conditional on one realization; for H3c also conditional on the
    fitted A4 and A5) and the iterative-error statement.

    Parameters
    ----------
    results : dict
        Study results (``systems``, ``provenance``).
    systems : list[str]
        Systems in report order.
    config : StudyConfig
        Source of the bootstrap resamples, block and ``core_noise``.

    Returns
    -------
    list[str]
        Markdown lines.
    """
    lines = [
        BUDGET_HEADING,
        "",
        "One table per primary quantity of interest (H2a, H2b and H3c; the "
        "secondaries have no table yet). Each size is in the units of the QoI. "
        "Sampling is the half-width of the reported interval; the numerical "
        "rows are flagged against it.",
    ]
    for key in ("H2a", "H2b", "H3c"):
        row = next(r for r in HYPOTHESIS_TABLE if r.key == key)
        present = [s for s in systems if key in results["systems"][s]]
        level = row_level(row, results, present) if present else role_level(row)
        label = interval_label(row, level, config)
        for qoi in (q for q in QOI_IDS if QOI_KEYS[q] == key):
            lines += ["", *_table(qoi, results, systems, config, level, label)]
    return lines
