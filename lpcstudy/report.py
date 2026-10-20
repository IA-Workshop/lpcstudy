"""Turn the study's numbers into verdicts, a Markdown report and figures.

The study asks whether four local predictability conditions decide how to
blend an analog forecaster (CP) with a physics-based forecaster (PLP), on
Lorenz-63, Rossler and Chua. Each condition is a hypothesis with a pass,
fail or inconclusive verdict per system; a hypothesis is "supported" only
if all three systems pass.

This module is the last stage of a run. It reads the ``results`` dictionary
that ``experiments.py`` and ``analysis.py`` fill in, and it does three jobs:

* ``verdicts`` combines the per-system verdicts into one verdict per row of
  the hypothesis table in ``identifiers.py`` (using ``statistics.py``);
* ``write_markdown`` writes ``RESULTS.md``: the verdict table, the
  allocation rules, the validation gate, the uncertainty budget and a
  "Handling" section that counts every clip, floor and fallback;
* ``make_figures`` and ``save_json`` write the four PNG figures and
  ``results.json``.

The long fixed texts (interval labels, figure captions, uncertainty budget)
live in ``budget.py``; the clip-sensitivity column is read from the block
that ``clip_sensitivity.py`` stores. Nothing here changes a number or a
verdict: the module only reads stored results and formats them. Read
``write_markdown`` first (it is the table of contents of the report), then
the helper that each section calls.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import matplotlib.ticker

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from .allocation import RULE_LABELS  # noqa: E402
from .budget import (  # noqa: E402
    budget_lines,
    caption_figure,
    figure_caption_lines,
    interval_label_lines,
    qoi_declaration_lines,
    v4_label_line,
)
from .clip_sensitivity import (  # noqa: E402
    INVARIANCE_NOT_GUARANTEED,
    part_state,
)
from .config import StudyConfig  # noqa: E402
from .identifiers import (  # noqa: E402
    HYPOTHESIS_TABLE,
    Hypothesis,
    check_keys,
)
from .statistics import overall_verdict  # noqa: E402
from .statistics import V3_SYSTEMS  # noqa: E402

# Figure colors (series colors, ink for text, light gray for the grid).
SERIES = [
    "#2a78d6",
    "#eb6834",
    "#1baf7a",
    "#eda100",
    "#e87ba4",
    "#008300",
    "#4a3aa7",
    "#e34948",
]
INK, INK_2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
PLOTTED_RULES = ["A0", "A1", "A2", "A3", "A4", "A5", "A*"]


def _hypothesis_text(row: Hypothesis, computed: bool = True) -> str:
    """Return the report text of one hypothesis-table row.

    The text is a role mark (for a primary hypothesis), the v3 criterion
    and, if the row is pending, a note saying so.

    Parameters
    ----------
    row : Hypothesis
        The row of ``identifiers.HYPOTHESIS_TABLE``.
    computed : bool, optional
        False for a row with no result: its note then says "not computed"
        instead of "computed with the v1 statistic".

    Returns
    -------
    str
        The text for the "Hypothesis" column.
    """
    text = ("[primary] " if row.role == "primary" else "") + row.criterion
    if row.pending:
        until = ", ".join(row.pending)
        text += (
            f" [computed with the v1 statistic until {until}]"
            if computed
            else f" [not computed until {until}]"
        )
    return text


HYPOTHESES: dict[str, str] = {
    row.key: _hypothesis_text(row) for row in HYPOTHESIS_TABLE
}

# Validation checks V1 to V6: (label, criterion text, pass test or None).
VALIDATION_CRITERIA = {
    "delay_jacobian_rel_err": (
        "V1 delay-map Jacobian vs finite differences",
        "< 1e-4",
        lambda v: v < 1e-4,
    ),
    "gain_rel_err": (
        "V1 amplifier g_H vs finite differences",
        "< 1e-4",
        lambda v: v < 1e-4,
    ),
    "crlb_ratio_median": (
        "V2 least squares / Cramer-Rao",
        "[0.8, 1.2]",
        lambda v: 0.8 <= v <= 1.2,
    ),
    "cp_median_vpt_lyapunov": (
        "V3 CP valid-prediction time (LT, theta=0.4)",
        "reported",
        None,
    ),
    "convergence": (
        "V4 w* bootstrap half-width at used M",
        "<= 0.05",
        lambda v: v <= 0.05,
    ),
    "km_max_abs_dev": (
        "V5 Kaplan-Meier vs exact",
        "< 0.01",
        lambda v: v < 0.01,
    ),
    "integrator_max_dev_sigma": (
        "V6 RK4 step halving (sigma_x)",
        "< 1e-3",
        lambda v: v < 1e-3,
    ),
}

# Flag of a per-system verdict in the report table.
FLAGS = {"pass": "PASS", "fail": "FAIL", "inconclusive": "INCONCLUSIVE"}
REPORTED_VERDICT = "reported (no pass/fail)"
# Extension systems (WU-0021, DEC-0037). A run that contains one of them reports
# per-system verdicts only: the overall word of the v3 decision rule
# (statistics.overall_verdict, an intersection-union test over the three v3
# systems) is not applied, because adding systems after the freeze would change
# its error rates (specification note 2026-10-20, section 5). The word below
# cannot be read as "supported" or "not supported".
EXTENSION_SYSTEMS: tuple[str, ...] = (
    "rossler_hyper",
    "lorenz63_r166",
    "rossler_z",
)
PER_SYSTEM_VERDICT = "per-system only"
EXTENSION_NOTE = (
    "Extension run (DEC-0037, DEVELOPMENT: not a hypothesis test): this run "
    "includes system(s) outside the three v3 systems, so it reports "
    "per-system verdicts only and no overall verdict. The sentence above on "
    "*supported* and *not supported* does not apply, and nothing here bears "
    "on the overall verdicts of the sealed study."
)
INTRO = (
    "Generated by `python -m lpcstudy`. Each criterion is decided per "
    "system by its interval against the pre-registered band of the "
    "proposal (v3 §2): pass, fail or inconclusive. A hypothesis is "
    "*supported* if it passes on all three systems, *not supported* if it "
    "fails on at least one, and *inconclusive* otherwise; a system that "
    "was not run counts as inconclusive (v3 §7). A validation-gate FAIL "
    "marks that system's results provisional (v3 §6 E0); it does not "
    "change the verdicts."
)
SMOKE_GATE_NOTE = (
    "Note: at the smoke preset a gate FAIL is expected. V7 is a plumbing "
    "check there, judged at pilot size and above (DEC-0015)."
)
# Label of the V7 rows at the smoke preset: V7 is a plumbing check there
# (DEC-0015).
V7_SMOKE_LABEL = (
    " (smoke: plumbing-size numbers, judged at pilot size; DEC-0015)"
)


def verdicts(results: dict, config: StudyConfig) -> dict:
    """Combine the per-system verdicts into one verdict per table row.

    A verdict for one system and one criterion is the string "pass",
    "fail" or "inconclusive" stored at ``results[s][key]["verdict"]``. It
    is never a boolean, so that an inconclusive result cannot be mistaken
    for a failure. The overall verdict comes from
    ``statistics.overall_verdict`` over the three v3 systems (DEC-0016
    O1): supported only if all three pass, not supported if any system
    fails, inconclusive otherwise, with the missing systems listed. A
    run of one system (the smoke preset) can therefore never read
    "supported".

    Verdicts do not depend on the validation gate: a gate failure only
    marks that system's results provisional (v3 section 6 E0), which the
    Markdown shows next to the gate line. The Q-N row is read, not
    decided, and the gain-bound row is reported with no pass/fail bar (v3
    section 2).

    Parameters
    ----------
    results : dict
        Study results.
    config : StudyConfig
        Configuration (it names the core systems).

    Returns
    -------
    dict
        For each table row that has a result: ``by_system`` (the verdict
        string of each system), ``verdict`` and, for a decided row,
        ``missing_systems``. A row with no result in any system is
        absent; a row with a result in some systems only raises
        ``KeyError``.

    Raises
    ------
    ValueError
        If a system's results carry a hypothesis-shaped key that is not
        in the identifier table (results written before WU-0002.2), or a
        decided row has no valid ``verdict`` (results written before
        WU-0002.9, which stored a boolean ``pass``). Nothing is relabeled
        in either case. Also raised if a system is not one of the three
        v3 systems.

    Notes
    -----
    A run that contains an extension system (``EXTENSION_SYSTEMS``, WU-0021)
    does not call ``overall_verdict``: each decided row stores ``by_system`` and
    the word ``PER_SYSTEM_VERDICT`` and no ``missing_systems``. A run of the
    v3 systems alone is unchanged.
    """
    out = {}
    systems = [s for s in config.core_systems if s in results["systems"]]
    # An extension run (a system of EXTENSION_SYSTEMS, every system registered
    # as a v3 or extension system) takes the per-system branch below. Any other
    # label still reaches ``overall_verdict``, which raises.
    extension_run = any(s in EXTENSION_SYSTEMS for s in systems) and all(
        s in V3_SYSTEMS or s in EXTENSION_SYSTEMS for s in systems
    )
    # Check the keys before any flag is read: a pre-v3 results file must
    # not be relabeled.
    for s in systems:
        try:
            check_keys(results["systems"][s])
        except ValueError as stale:
            raise ValueError(
                f"results of system {s} use identifiers of a schema older "
                f"than WU-0002.2 (v1 keys); regenerate them with a new "
                f"run: {stale}"
            ) from None
    for row in HYPOTHESIS_TABLE:
        if not any(row.key in results["systems"][s] for s in systems):
            continue  # no result in any system; write_markdown lists the row
        if row.role == "estimate":
            # Q-N: an estimate is read, not passed (v3 section 7).
            readings = {}
            for s in systems:
                res = results["systems"][s][row.key]
                readings[s] = res[res["primary"]]["logit_w_interior"]["reading"]
            out[row.key] = {
                "by_system": readings,
                "verdict": "estimate (read, no pass/fail)",
            }
            continue
        if row.role == "reported":
            # The gain bound has no bar (v3 section 2). Indexing each
            # system raises KeyError if the result is missing in one.
            for s in systems:
                results["systems"][s][row.key]
            out[row.key] = {
                "by_system": {s: "reported" for s in systems},
                "verdict": REPORTED_VERDICT,
            }
            continue
        found = {
            s: results["systems"][s][row.key].get("verdict") for s in systems
        }
        stale = [s for s, v in found.items() if v not in FLAGS]
        if stale:
            raise ValueError(
                f"result {row.key} of system(s) {stale} has no verdict "
                "(pass, fail or inconclusive): written before WU-0002.9; "
                "regenerate it with a new run"
            )
        if extension_run:
            out[row.key] = {"by_system": found, "verdict": PER_SYSTEM_VERDICT}
            continue
        overall, missing = overall_verdict(found)
        out[row.key] = {
            "by_system": found,
            "verdict": overall,
            "missing_systems": missing,
        }
    return out


def _fmt(value: float | None, digits: int = 3) -> str:
    """Format a number to ``digits`` significant digits ("n/a" if absent)."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "n/a"
    return f"{value:.{digits}g}"


def _interval(ci: list | None, digits: int = 3) -> str:
    """Format a stored interval as ``[lo, hi]`` ("n/a" if not computed)."""
    if ci is None:
        return "n/a"
    return f"[{_fmt(ci[0], digits)}, {_fmt(ci[1], digits)}]"


def _verdict_text(res: dict) -> str:
    """Return the verdict of a result, with its reason if inconclusive."""
    reason = f" ({res['reason']})" if res.get("reason") else ""
    return f"{res['verdict']}{reason}"


def _key_number(key: str, res: dict) -> str:
    """Return a one-line numeric summary of one result for one system.

    Each hypothesis (table key) reports different numbers, so this
    function has one branch per key. Every branch only formats numbers
    that the analysis already stored.

    Parameters
    ----------
    key : str
        The hypothesis-table key, for example ``"H1b"`` or ``"Q-N"``.
    res : dict
        One system's results (it holds the result stored under ``key``).

    Returns
    -------
    str
        The text for one cell of the verdict table ("" for an unknown
        key).
    """
    r = res[key]
    match key:
        case "H1a":
            parts = [
                f"rho={k}: 1/d (n_lib fit)={_fmt(v['fitted_inverse_dim'])}, "
                f"ratio {_fmt(v['ratio'])} [{_fmt(v['ratio_ci'][0])}, "
                f"{_fmt(v['ratio_ci'][1])}] {_verdict_text(v)}"
                for k, v in r["by_noise"].items()
            ]
            reference = _fmt(r["inverse_dim_reference"])
            return "; ".join(parts) + f" (1/d_LB={reference})"
        case "H1b":
            plp = r["PLP"]
            return (
                f"CP {_fmt(r['CP']['slope'])}, PLP {_fmt(plp['slope'])} "
                f"[{_fmt(plp['ci'][0])}, {_fmt(plp['ci'][1])}]: "
                f"{_verdict_text(r)}"
            )
        case "H1c":
            plp, cp = r["PLP"], r["CP"]
            return (
                f"PLP {_fmt(plp.get('median_ratio'))} "
                f"{_interval(plp.get('ci'))}: {_verdict_text(r)}; "
                f"CP {_fmt(cp.get('median_ratio'))} "
                f"{_interval(cp.get('ci'))} (reported, no verdict)"
            )
        case "H1d":
            s = {name: row["spearman"] for name, row in r["rows"].items()}
            return (
                f"eps {_fmt(s['analog_seed'], 2)}, "
                f"delta {_fmt(s['estimation_seed'], 2)}, "
                f"Lambda {_fmt(s['growth'], 2)}, N {_fmt(s['nhat'], 2)}: "
                f"{_verdict_text(r)}"
            )
        case "Q-N":

            def block(profile: str, target: str) -> str:
                d = r[profile][target]
                interval = f"[{_fmt(d['ci'][0], 2)}, {_fmt(d['ci'][1], 2)}]"
                delta = f"dR2 {_fmt(d['delta_r2'], 2)} {interval}"
                if "reading" in d:
                    return f"{d['reading']} ({delta})"
                return delta

            primary, deployable = r["primary"], r["deployable"]
            return (
                f"{primary}: interior {block(primary, 'logit_w_interior')}, "
                f"w*=0 {block(primary, 'w_zero_indicator')}, "
                f"log T {block(primary, 'log_horizon')}; "
                f"deployable interior "
                f"{deployable['logit_w_interior']['reading']}, "
                f"w*=0 {deployable['w_zero_indicator']['reading']} "
                f"(w*=0: {r['n_w_zero']}, w*=1: {r['n_w_one']})"
            )
        case "H2a":
            two = r["part_ii"]
            zero, interior = two["zero"], two["interior"]
            return (
                f"(i) {r['part_i_verdict']}: "
                f"range {_fmt(r['median_range'])} "
                f"(CI hi {_fmt(r['range_ci'][1])}, "
                f"n={r['n_eligible_states']}); "
                f"(ii) {r['part_ii_verdict']}: partial r zero "
                f"{_fmt(zero['partial_corr'], 2)} "
                f"[{_fmt(zero['ci'][0], 2)}, {_fmt(zero['ci'][1], 2)}], "
                f"interior {_fmt(interior['partial_corr'], 2)} "
                f"[{_fmt(interior['ci'][0], 2)}, "
                f"{_fmt(interior['ci'][1], 2)}] "
                f"(w*=0: {r['n_w_zero']}, w*=1: {r['n_w_one']})"
            )
        case "H2b":
            change = r["library_change"]
            return (
                f"rho rank corr {_fmt(r['noise']['mean_state_spearman'], 2)};"
                f" n_lib 10^3->10^4 change {_fmt(change['mean_change'], 2)} "
                f"{_interval(change['ci'], 2)}: {_verdict_text(r)}"
            )
        case "H2c":
            best = f"A4_minus_{r['best_single']}"

            def part(p: dict) -> str:
                return (
                    f"{_fmt(p['mean'], 3)} {_interval(p['ci'])} "
                    f"({_fmt(100 * p['relative'], 3)}%) {_verdict_text(p)}"
                )

            oracle_gain = _fmt(100 * r["A4o_minus_A2"]["relative"], 3)
            return (
                f"A4-A2 {part(r['A4_minus_A2'])}; "
                f"A4-{r['best_single']} {part(r[best])}; "
                f"A4o-A2 {oracle_gain}% (reported): {_verdict_text(r)}"
            )
        case "H2d":
            return (
                f"A4/A3-1 = {_fmt(100 * r['in_distribution_excess'], 3)}% "
                f"[{_fmt(100 * r['ci'][0], 3)}, "
                f"{_fmt(100 * r['ci'][1], 3)}]%: {_verdict_text(r)}"
            )
        case "gain_bound":
            # A result without the counts fails loudly (PRIME.4).
            out = r["n_screened_out"]
            screens = (
                f" of {r['n_total_states']}; screened out: "
                f"growth<=0 {out['growth_nonpositive']}, "
                f"censored {out['censored_single_forecaster']}, "
                f"covariance<0 {out['negative_covariance']}"
            )
            return (
                f"within bound {_fmt(r['fraction_within_bound'], 3)} "
                f"(n={r['n_states']}{screens}, "
                f"max gain {_fmt(r['max_gain_lyapunov'], 2)} LT)"
            )
        case "H2e":
            changes = "; ".join(
                f"rho={k}: median change {_fmt(v['median_change'], 2)} "
                f"{_interval(v['ci'], 2)}"
                for k, v in r["by_noise"].items()
            )
            return changes + f": {_verdict_text(r)}"
        case "H3a":
            holm = r["logrank_p_holm"]
            return (
                f"K={r['chosen_K']}: largest Holm p "
                f"{_fmt(max(holm) if holm else None, 3)}, "
                f"IQR {_fmt(r['iqr_lt_mean'], 2)} LT: {_verdict_text(r)}"
            )
        case "H3b":
            w, d = r["weight_lambda"], r["D"]
            return (
                f"Lambda imp: weight {_fmt(w['importance'], 2)} "
                f"{_interval(w['ci'], 2)}, "
                f"D {_fmt(d['value'], 2)} {_interval(d['ci'], 2)}, "
                f"stability {_fmt(r['stability'], 2)}: {_verdict_text(r)}"
            )
        case "H3c":
            return (
                f"A5/A4 {_fmt(r['A5_over_A4_mse'], 4)} "
                f"{_interval(r['ci'], 4)}: {_verdict_text(r)}"
            )
    return ""


def _cell(value: object) -> str:
    """Render one provenance value for a Markdown table cell."""
    if value is None:
        return "null"
    text = value if isinstance(value, str) else json.dumps(value)
    return text.replace("|", "\\|").replace("\n", " ")


def platform_line(provenance: dict) -> str:
    """Return the ``Platform:`` header line.

    The line names the CPU model and the kernel that each OpenBLAS
    library chose at run time (the kernel can change the last digits of
    a floating-point sum, so a reader comparing runs needs it).

    A failed probe is never shown as a value (PRIME.4). An unknown model
    carries its source and the read error. A failed BLAS probe prints
    ``BLAS probe failed (<error>)``, and a failed library prints
    ``<library> unknown (<error>)``.

    Parameters
    ----------
    provenance : dict
        The provenance block. A block with neither ``cpu`` nor ``blas``
        (schema ``/1``, written before WU-0001.6) gives ``Platform: not
        recorded``.

    Returns
    -------
    str
        ``Platform: CPU <model> · BLAS <library> <corename>, ...``. It
        reads ``BLAS none mapped`` when the probe worked and found no
        OpenBLAS.
    """
    if "cpu" not in provenance and "blas" not in provenance:
        return "Platform: not recorded"
    cpu, blas = provenance.get("cpu", {}), provenance.get("blas", {})
    model = cpu.get("model", "unknown")
    if model == "unknown" or cpu.get("error"):
        detail = ", ".join(
            str(x)
            for x in (f"source {cpu.get('source', 'none')}", cpu.get("error"))
            if x
        )
        model = f"{model} ({detail})"
    elif cpu.get("source", "/proc/cpuinfo") != "/proc/cpuinfo":
        model = f"{model} (source {cpu['source']})"
    if blas.get("error"):
        text = f"BLAS probe failed ({blas['error']})"
    else:
        parts = [
            (
                f"{entry['library']} unknown ({entry['error']})"
                if entry.get("error")
                else f"{entry['library']} {entry['corename'] or 'unknown'}"
            )
            for entry in blas.get("libraries", [])
        ]
        text = "BLAS " + (", ".join(parts) or "none mapped")
    return f"Platform: CPU {model} · {text}"


def header_lines(provenance: dict | None) -> list[str]:
    """Return the Markdown lines of the RESULTS.md provenance header.

    The header says which seed and code produced the file, so that no
    reader mistakes a development run for a confirmatory one (LPC.PC.13,
    LPC.PC.18).

    Parameters
    ----------
    provenance : dict or None
        The ``results["provenance"]`` block, used as stored. ``None`` for
        output written before the block existed.

    Returns
    -------
    list[str]
        The label line, the ``Platform:`` line (WU-0001.6), a two-column
        table of every key except ``config``, and the full configuration
        as JSON in a ``<details>`` block.
    """
    if provenance is None:
        return [
            "**UNPROMOTED** · provenance absent "
            "(output written before WU-0001)"
        ]
    label = provenance["label"]
    lines = [
        (
            f"**{label}**"
            if "UNPROMOTED" in label
            else f"**{label}** · **UNPROMOTED**"
        ),
        "",
        platform_line(provenance),
        "",
        "| Provenance | Value |",
        "|---|---|",
    ]
    lines += [
        f"| {key} | {_cell(value)} |"
        for key, value in provenance.items()
        if key != "config"
    ]
    lines += [
        "",
        "<details><summary>Full configuration</summary>",
        "",
        "```json",
        json.dumps(provenance["config"], indent=2),
        "```",
        "",
        "</details>",
    ]
    return lines


# Counters that should be 0 by a theorem hypothesis (P1(a), P3) or by
# construction (the applied-mathematician's table (3), WU-0002.11): a
# nonzero one is a finding. The Handling section labels them; it marks no
# result provisional (Q6 of DEC-0017 is the owner's ruling).
SENTINEL_COUNTERS: frozenset[str] = frozenset(
    {
        "error_clips_cp",
        "curvature_floor",
        "pooled_curvature_floor",
        "decisive_floor",
        "closed_form_floor_a4",
        "closed_form_floor_a4o",
        "local_dim_zero_distance",
        "oracle_nonfinite",
        "oracle_gain_floor",
    }
)

_CLIP_H1B = "clip_sensitivity/by_hypothesis/H1b/parts/PLP"

# Result-count paths that are sentinels. The PLP regression of H1b has
# floor 0, so its squared error floors only below 1e-12, which is
# unreachable for rho >= 0.005. The clip-sensitivity copies of that floor
# (WU-0004f) read 0 for the same reason. An exception swallowed by the
# report-only clip-sensitivity block is a defect.
SENTINEL_RESULT_PATHS: frozenset[str] = frozenset(
    {
        "H1b/PLP/n_floored",
        f"{_CLIP_H1B}/n_floored",
        f"{_CLIP_H1B}/n_floored_2L",
        "clip_sensitivity/n_caught_exceptions",
    }
)


def _handling_blocks(handling: dict) -> list[tuple[str, dict]]:
    """Return the ``(block id, record)`` pairs of a system's ``handling``.

    Only records that carry ``counts`` are listed: each cell, its
    ``evaluation`` and ``fitting`` sub-blocks, each oracle split and the
    fit.
    """
    blocks = []
    for block_id, record in handling.get("cells", {}).items():
        blocks.append((block_id, record))
        for suffix in ("evaluation", "fitting"):
            if record.get(suffix):
                blocks.append((f"{block_id}/{suffix}", record[suffix]))
    blocks += [
        (f"oracles/{split}", record)
        for split, record in handling.get("oracles", {}).items()
    ]
    if handling.get("fitting"):
        blocks.append(("fitting", handling["fitting"]))
    return blocks


def _counter_text(name: str, value: int) -> str:
    """Return ``name = value``, marked "(sentinel)" if it should be 0."""
    return f"{name} = {value}" + (
        " (sentinel)" if name in SENTINEL_COUNTERS else ""
    )


def handling_lines(results: dict, systems: list[str]) -> list[str]:
    """Return the ``## Handling`` section of RESULTS.md.

    The study counts every clip, floor, replacement and fallback instead
    of hiding it (DEF-0001, WU-0002.11b: "nothing silent"). This section
    lists the counters that are not zero, so a reader sees at once where
    the code had to intervene. The full block, zeros included, stays in
    ``results.json``.

    The function reads ``results["handling"]`` (the run totals and the
    robustness variants that raised or were not run) and each system's
    ``handling`` (cells with their ``evaluation`` and ``fitting``
    sub-blocks, oracle splits, the fit, and ``result_counts``). Counters
    in ``SENTINEL_COUNTERS`` (and the result paths in
    ``SENTINEL_RESULT_PATHS``) are labeled "sentinel". The section is a
    report only: it changes no verdict and marks no result provisional
    (Q6, DEC-0017). Results written before the ``handling`` block existed
    get one line saying so, never an exception.

    Parameters
    ----------
    results : dict
        Study results.
    systems : list[str]
        The systems to list, in report order.

    Returns
    -------
    list[str]
        The Markdown lines of the section.
    """
    head = ["## Handling (DEF-0001: nothing silent)", ""]
    run = results.get("handling")
    if run is None:
        return [
            *head,
            "No `handling` block in these results "
            "(written before WU-0002.11).",
        ]
    totals = [
        _counter_text(name, value)
        for name, value in run["totals"].items()
        if value
    ]
    if "skipped_variants" in run:
        skipped = f"{run['skipped_variants']}."
    else:
        skipped = "not recorded in these results (written before WU-0004f)."
    lines = [
        *head,
        f"Schema `{run['schema']}`. Counts only: no number in this report "
        "depends on them, and none marks a result provisional (rate "
        "counters are report-only; whether a nonzero sentinel, or a "
        "collapsed nu cap, should mark results provisional is the owner's "
        "ruling, DEC-0017 Q6). Only nonzero counters of the main systems "
        "are listed here; the full block, with the zeros and the "
        "denominators of every block, is `handling` in `results.json` (the "
        "counters of the robustness variants are there too, under "
        "`handling.robustness`, and are not listed here). `run.log` has "
        "one line per nonzero cell, oracle or fit counter; result counts "
        "have no log line. A counter marked *sentinel* should be 0 by a "
        "theorem hypothesis or by construction: a nonzero one is a "
        "finding.",
        "",
        "Run totals (main systems): "
        + ("; ".join(totals) + "." if totals else "no counter is nonzero."),
        "",
        "Robustness variants that raised (`failed_variants`): "
        f"{run['failed_variants']}.",
        "Robustness variants not run (`skipped_variants`): " + skipped,
    ]
    for system in systems:
        handling = results["systems"][system].get("handling")
        lines += ["", f"### {system}", ""]
        if handling is None:
            lines.append("No `handling` block for this system.")
            continue
        rows = []
        for block_id, record in _handling_blocks(handling):
            nonzero = [
                _counter_text(name, value)
                for name, value in record["counts"].items()
                if value
            ]
            if nonzero:
                denominators = "; ".join(
                    f"{name} {value}"
                    for name, value in record["denominators"].items()
                )
                rows.append(
                    f"| `{_cell(block_id)}` | {'; '.join(nonzero)} "
                    f"| {denominators} |"
                )
        if rows:
            lines += [
                "| Block | Nonzero counters | Denominators of the block |",
                "|---|---|---|",
                *rows,
            ]
        else:
            lines.append("No counter of any block is nonzero.")
        counts = [
            (path, value)
            for path, value in handling["result_counts"].items()
            if value
        ]
        lines.append("")
        if counts:
            lines += ["| Result count | Value |", "|---|---|"]
            for path, value in counts:
                sentinel = (
                    " (sentinel)" if path in SENTINEL_RESULT_PATHS else ""
                )
                lines.append(f"| `{_cell(path)}`{sentinel} | {value} |")
        else:
            lines.append("No result count is nonzero.")
    return lines


def _v7_rows(
    results: dict, systems: list[str], config: StudyConfig
) -> list[str]:
    """Return the two V7 rows of the validation table (WU-0002.10).

    V7 checks the noise-level estimate: the ratio ``delta / (rho nu)``
    should be near 1 at every noise level rho, and ``ln delta`` should
    have slope near 1 against ``ln rho``.

    The efficiency cell shows the minimum to maximum over rho of the
    median ratio, flagged PASS only if every level passes. The slope cell
    shows the median slope. A system without a V7 result shows "n/a" (no
    flag). At the smoke preset the row name carries ``V7_SMOKE_LABEL``,
    because V7 is a plumbing check there, judged at pilot size (DEC-0015).
    Numbers and flags are the same at every preset.
    """
    label = V7_SMOKE_LABEL if config.name == "smoke" else ""
    eff_cells, slope_cells = [], []
    for s in systems:
        v7 = results["systems"][s].get("V7")
        if v7 is None:
            eff_cells.append("n/a")
            slope_cells.append("n/a")
            continue
        values = list(v7["efficiency_median_by_noise"].values())
        ok = all(v7["efficiency_pass_by_noise"].values())
        low, high = _fmt(float(np.min(values)), 3), _fmt(
            float(np.max(values)), 3
        )
        eff_cells.append(f"{low}–{high}" + (" PASS" if ok else " FAIL"))
        slope_cells.append(
            _fmt(v7["median_slope"], 3)
            + (" PASS" if v7["slope_pass"] else " FAIL")
        )
    return [
        f"| V7 median δ/(ρν), every ρ{label} | [0.9, 1.1] | "
        + " | ".join(eff_cells)
        + " |",
        f"| V7 median slope of ln δ on ln ρ{label} | [0.9, 1.1] | "
        + " | ".join(slope_cells)
        + " |",
    ]


# Published largest Lyapunov exponents, per natural time unit, with the
# relative tolerance of the comparison (WU-0007; tolerances derived in
# tests/unit/test_data.py, not tuned). The study's own Chua parameters
# have no confirmed published value (known limitation, NVVUQ.13, DEC-0010).
LYAPUNOV_REFERENCES: dict[str, list[tuple[float, float, str]]] = {
    "lorenz63": [
        (
            0.90563,
            0.01,
            "Sprott, sprott.physics.wisc.edu/chaos/lespec.htm (confirmed)",
        )
    ],
    "rossler": [
        (
            0.0714,
            0.03,
            "Sprott as cited by Bogdanov and Bogdanova, arXiv:1412.2242 "
            "(secondary)",
        ),
        (
            0.07062,
            0.03,
            "Bogdanov and Bogdanova, arXiv:1412.2242, own estimate "
            "0.07062 ± 0.00066 (primary)",
        ),
    ],
    "chua": [],
    # Extension systems (WU-0021, DEC-0037, specification note 2026-10-20
    # sections 1.1 and 7 R11). S1: the largest exponent of the standard method
    # in Ramasubramanian and Sriram, arXiv:chao-dyn/9909029, Table 1 (read by
    # the researcher); their other method gives 0.1128 and the code's value is
    # 0.4% away, so the 3% of the Rossler secondary source is generous.
    "rossler_hyper": [
        (
            0.1121,
            0.03,
            "Ramasubramanian and Sriram, arXiv:chao-dyn/9909029, Table 1, "
            "standard method (primary)",
        )
    ],
    "lorenz63_r166": [],
    "rossler_z": [],
}
# A different Chua parameter set (alpha 9, beta 100/7, m0 -8/7, m1 -5/7):
# 0.23 per circuit time of the memo, divided by 0.7 (tau = 0.7 t, derived),
# tolerance 10%.
LYAPUNOV_MEMO = (
    0.23 / 0.7,
    0.10,
    "Matsumoto, Chua and Komuro, UCB/ERL M84/73 (1984), "
    "μ1 = 0.23 per circuit time ÷ 0.7 (derived); Martins (2016) states 0.33",
)
LYAPUNOV_MEMO_TEST = (
    "tests/unit/test_data.py::"
    "test_lyapunov_cached_matches_published_reference[chua_memo]"
)


def _lyapunov_lines(results: dict, systems: list[str]) -> list[str]:
    """Return the table comparing the code's λ_max with published values.

    λ_max is the largest Lyapunov exponent: the rate at which nearby
    states drift apart. It sets the study's time unit (one Lyapunov time),
    so a wrong value would mislabel every horizon (WU-0007.3).

    The code's value is read from ``systems.<s>.context.lambda_max``; the
    references and tolerances are the constants above. A system without
    that value shows "n/a", not a skip. The comparison is report only: it
    does not enter the validation gate or any verdict.
    """
    lines = [
        "| System | Code λ_max | Published | Source | Relative difference "
        "| Result |",
        "|---|---|---|---|---|---|",
    ]
    for s in systems:
        found = results["systems"][s].get("context", {}).get("lambda_max")
        code = "n/a" if found is None else _fmt(found, 6)
        # A system without an entry raises (PRIME.4).
        references = LYAPUNOV_REFERENCES[s]
        if s in EXTENSION_SYSTEMS and not references:
            # DEC-0010 (the Chua retrieval decision) does not cover these.
            lines.append(
                f"| {s} | {code} | none | no confirmed published value | "
                "n/a | not validated: no confirmed published value at these "
                "parameters (extension system, WU-0021) |"
            )
            continue
        if not references:
            lines.append(
                f"| {s} | {code} | none | no confirmed published value | "
                "n/a | not validated: no published reference at these "
                "parameters (known limitation, NVVUQ.13, DEC-0010) |"
            )
        for value, tolerance, source in references:
            if found is None:
                gap, verdict = "n/a", "n/a: no λ_max in the results"
            else:
                relative = found / value - 1.0
                gap = f"{100 * relative:+.2f}%"
                if abs(relative) <= tolerance:
                    verdict = f"PASS: within {100 * tolerance:g}%"
                else:
                    verdict = (
                        f"FAIL: outside {100 * tolerance:g}%; step size "
                        "suspected (LPC.NV.1), reported, not tuned"
                    )
            lines.append(
                f"| {s} | {code} | {_fmt(value, 4)} | {source} | {gap} "
                f"| {verdict} |"
            )
    value, tolerance, source = LYAPUNOV_MEMO
    lines.append(
        "| chua, memo parameter set (α=9, β=100/7, m0=−8/7, m1=−5/7) | "
        f"not computed in this run | {_fmt(value, 4)} | {source} | n/a | "
        f"within {100 * tolerance:g}% is asserted by "
        f"`{LYAPUNOV_MEMO_TEST}`; a different parameter set from the "
        "study's: validates the routine and the field form, not the "
        "study's Chua parameters |"
    )
    lines += [
        "",
        "Every quantity is defined for the fixed-step RK4 flow map at the "
        "configured observation interval, not for the continuous ODE "
        "(LPC.NV.1). λ_max is estimated on that map by Benettin's method "
        "and compared in natural time units with published values for the "
        "continuous systems.",
        "",
        "Chua at the study's own parameters (α=15.6, β=28, m0=−1.143, "
        "m1=−0.714) has no confirmed published value (known limitation, "
        "NVVUQ.13, DEC-0010): its λ_max is reported but not validated.",
        "",
        "Validation against a real-world referent does not apply: the "
        "three systems are mathematical models (NVVUQ.13).",
        "",
        "This comparison is report-only: it does not enter the validation "
        "gate or any verdict.",
    ]
    return lines


def _p2c_lines(results: dict, systems: list[str]) -> list[str]:
    """Return the table verifying Theorem P2(c) (WU-0005.5).

    Theorem P2(c) of the v3 proposal says that, on the same draws, every
    state must satisfy N² ≤ A ≤ B. This table counts the states where the
    code violates it. There is one row per system, read from
    ``systems.<s>.verification.P2c``; a system without the block shows
    "n/a", not a skip. The check is report only: it carries no verdict
    and is not part of the validation gate or of any verdict. A violation
    is shown as a defect, never as a flag on the results.
    """
    lines = [
        "| System | States | Violations | Chain violations (N≤A, A≤B, "
        "P2(a), triangle, consistency) | Switching states | States with "
        "B = 0 | N/√B (median, p90, max) | Same draws as N |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for s in systems:
        block = results["systems"][s].get("verification", {}).get("P2c")
        if block is None:
            lines.append(f"| {s} | n/a: no P2(c) result | | | | | | |")
            continue
        chain = block["n_chain_violations"]
        spread = block["tightness"]["N_over_sqrt_B"]
        if spread["median"] is None:
            tight = "n/a"
        else:
            tight = (
                f"{_fmt(spread['median'], 3)}, {_fmt(spread['p90'], 3)}, "
                f"{_fmt(spread['max'], 3)}"
            )
        found = block["n_violations"]
        same = block["same_draws_identical"]
        if same is None:
            same_text = "not compared"
        else:
            same_text = "yes" if same else "**NO: DEFECT**"
        lines.append(
            f"| {s} | {block['n_states']} | "
            + (f"{found}" if not found else f"**{found}: DEFECT**")
            + f" | {chain['N_le_A']}, {chain['A_le_B']}, {chain['p2a']}, "
            f"{chain['triangle']}, {chain['consistency']} | "
            f"{block['n_switching_states']} | "
            f"{block['n_zero_bound_states']} | {tight} | {same_text} |"
        )
    lines += [
        "",
        "Verification check (NVVUQ.14, v3 Theorem P2(c)); not a hypothesis "
        "test; no verdict; not in the validation gate. At the core cell "
        "(k = 1) and on the same oracle draws as N, every state must "
        "satisfy N² ≤ A ≤ B, where A = mean ‖Y_r − X₁‖² / (ρ²D) is the "
        "spread of the retrieved analogs Y_r about the clean-query analog "
        "X₁ and B = 4 mean (r₁ + ‖η_r‖)² 1{‖η_r‖ ≥ Δ/2} / (ρ²D) is the "
        "bound, both over the M draws, in the units of N². This holds "
        "exactly, so a violation is a code defect, not sampling noise; the "
        "slack is the round-off bound of the check (κ = 1e-13, τ_N), not a "
        "tolerance fitted to results. N/√B near 0 means the bound is loose "
        "for that state.",
    ]
    return lines


# The kinds of a cell's ``lm`` block, in report order (the keys of
# ``pipeline.KINDS``).
LM_KINDS: tuple[str, ...] = ("oracle", "eval", "check")


def _lm_lines(
    results: dict, systems: list[str], config: StudyConfig
) -> list[str]:
    """Return the table of Levenberg-Marquardt (LM) diagnostics.

    The PLP forecaster estimates its starting state with the LM method,
    an iterative least-squares fit. This table shows how well those fits
    ended (WU-0005.4, NVVUQ.10). There is one row per system, cell and
    kind with at least one estimate, read from
    ``systems.<s>.handling.cells.<id>.lm``. ``c`` is the final cost
    ``||X_t - G'(u_hat)||^2`` in normalized observation units, printed
    beside ``c / rho^2``.

    This is a report only: no verdict reads it, it is not in the
    validation gate, and the fraction of estimates with ``c / rho^2``
    above the chi-square 0.999 quantile is a diagnostic with no role in
    any decision (DEC-0025, D3). Results written before the block existed
    (handling schema ``/1``, or none) get one line, never an exception.
    Needs owner review before freeze.
    """

    def ratio(value: float | None, noise: float) -> str:
        return _fmt(None if value is None else value / noise**2)

    rows = []
    for system in systems:
        handling = results["systems"][system].get("handling")
        cells = {} if handling is None else handling.get("cells", {})
        for cell_id, record in cells.items():
            block = record.get("lm")
            if block is None:
                continue
            for kind in LM_KINDS:
                part = block["by_kind"][kind]
                if not part["n_estimates"]:
                    continue
                rho = part["noise"]
                rows.append(
                    f"| {system} | `{_cell(cell_id)}` | {kind} | "
                    f"{part['n_estimates']} | {part['gof_dof']} | "
                    f"{_fmt(part['median_residual'])} | "
                    f"{_fmt(part['p95_residual'])} | "
                    f"{ratio(part['median_residual'], rho)} | "
                    f"{ratio(part['p95_residual'], rho)} | "
                    f"{_fmt(part['median_iterations'])} | "
                    f"{_fmt(part['fraction_no_decrease'])} | "
                    f"{_fmt(part['fraction_late_progress'])} | "
                    f"{_fmt(part['fraction_above_chi2'])} | "
                    f"{part['nonfinite_residuals']} |"
                )
    if not rows:
        return [
            "No Levenberg-Marquardt estimates in these results (no cell "
            "has an `lm` block with n > 0: written before WU-0005.4, or "
            "built by hand)."
        ]
    steps = config.estimator_refine_steps
    return [
        "| System | Cell | Kind | n | dof (D − m) | median c | p95 c | "
        "median c/ρ² | p95 c/ρ² | "
        f"median accepted steps (of {steps}) | fraction no decrease | "
        "fraction late progress | "
        "fraction c/ρ² > χ²(dof) 0.999 quantile | non-finite residuals |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
        *rows,
        "",
        "Verification of the estimator's iterative stage (NVVUQ.10); not a "
        "hypothesis test; no verdict; not in the validation gate. The "
        f"stopping criterion is a fixed {steps} Levenberg–Marquardt "
        "iterations with no tolerance stop. c is the final cost "
        "‖X_t − G′(û)‖², the sum of D squared terms in the units of σ_x "
        "(the noise standard deviation is ρ). The first-order reference "
        "for an estimate that converged in the correct basin is c/ρ² ~ "
        "χ²(dof) with dof = D − m delay coordinates beyond the state (4 at "
        "D = 7: median 3.36, p95 9.49). 'Accepted steps' counts every "
        "iteration whose candidate cost was strictly lower, round-off "
        "accepts after convergence included, so it is an upper bound on "
        "the productive steps and not the number of iterations to "
        "convergence. A fraction with no decrease above 0 indicates a "
        "failure (non-finite cost, corrupted Jacobian, or a stationary "
        "start), not slow convergence. 'Late progress' is the fraction of "
        "estimates with an accepted step in the last 3 iterations that "
        "lowered the cost by more than 1e-6 relative (or left an infinite "
        "cost): a screen for an estimate still moving at the budget. The "
        "fraction with c/ρ² above the 0.999 quantile of χ²(dof) (18.47 for "
        "dof 4) is 0.001 under the reference (a converged estimate in the "
        "correct basin with an exact model); it also counts wrong-basin "
        "estimates, estimates still unconverged at the budget, and model "
        "error (a misspecified model gives a non-central χ²: in a probe at "
        "5% misspecification 100% exceeded at ρ = 0.01 and 23% at "
        "ρ = 0.05). Infinite residuals count in this fraction and also in "
        "the non-finite residuals column, so the two overlap. It is "
        "printed as a diagnostic, with no gate or verdict role. Neither "
        "column estimates the iterative error of any reported quantity "
        "(NVVUQ.9).",
    ]


# --- The clip column (WU-0002.11e; needs owner review before freeze) ---
# The clip: errors are capped at 10 sigma_x. The clip column reports how
# much each verdict would move if the cap were 20 sigma_x.
CLIP_NONE = "—"  # no clipped entry feeds the verdict at H_ref
CLIP_MARK = "CLIP-SENSITIVE"


def _invariance_text(label: str) -> str:
    """Return "invariant" for an exact invariance, else the label itself."""
    return "invariant" if label == "exact" else label


def _parts_text(entry: dict) -> str:
    """Return the ``clip`` text of one criterion from its parts.

    A part is one decided piece of a criterion (see
    ``clip_sensitivity.part_state``). Fired parts are listed with their
    ratio and the verdict at 20 sigma_x. Otherwise the text is ``—`` when
    no computed part has a clipped input, or ``ok (|Δ|/hw = x)`` with the
    largest ratio. Parts that could not be computed are listed with their
    reason and are never read as ok.
    """
    fired, other, ratios, not_done = [], [], [], []
    for name, part in entry["parts"].items():
        state = part_state(part)
        ratio = part["ratio"]
        label = "|Δ|max/hw" if "delta_bound" in part else "|Δ|/hw"
        if state == "fired":
            what = part.get("verdict_2L") or part["reason"] or "bound"
            fired.append(
                f"{name} ({label} = {_fmt(ratio, 2)}; at 20 σ_x: {what})"
            )
        elif state == "not_computed":
            not_done.append(f"{name}: {part['reason']}")
        else:
            other.append(state)
            if ratio is not None:
                ratios.append(ratio)
    text = []
    if fired:
        text.append(f"**{CLIP_MARK}** " + "; ".join(fired))
    elif entry["flag"]:
        # A criterion-level event: the parts of H2a(ii) change at 20 sigma_x.
        text.append(
            f"**{CLIP_MARK}** (the parts change at 20 σ_x: "
            f"{entry.get('parts_2L')})"
        )
    if not fired and other:
        if all(s == "none" for s in other):
            text.append(CLIP_NONE)
        else:
            largest = _fmt(max(ratios), 2) if ratios else "n/a"
            text.append(f"ok (|Δ|/hw = {largest})")
    if not_done:
        text.append("not computed (" + "; ".join(not_done) + ")")
    return "; ".join(text) if text else CLIP_NONE


def _clip_text(block: dict | None, key: str) -> str:
    """Return the ``clip`` text of table row ``key`` for one system.

    ``block`` is the system's ``clip_sensitivity`` block (or ``None``).
    """
    if block is None:
        return "n/a"
    if block["status"] != "computed":
        return f"not computed ({block['reason']})"
    if key in ("Q-N", "H3b"):
        n = block["affected_states"][key]
        if n == 0:
            return CLIP_NONE
        return f"{n} states with a clipped H_ref draw (count only)"
    if key in ("H1c", "H3a"):
        # For H3a the label is the cause string: source, total, H_ref count.
        return _invariance_text(block["invariance"][key])
    entry = block["by_hypothesis"].get(key)
    if entry is None:
        return "n/a"
    text = _parts_text(entry)
    if key == "H2a":
        inv = _invariance_text(block["invariance"]["H2a_i"])
        return f"(i) {inv}; (ii) {text}"
    return text


def clip_cells(results: dict, systems: list[str], key: str) -> str:
    """Return the ``clip`` cell of table row ``key``.

    The cell holds each system's text, with pipes escaped for the table.
    """
    text = "; ".join(
        f"{s}: "
        f"{_clip_text(results['systems'][s].get('clip_sensitivity'), key)}"
        for s in systems
    )
    return text.replace("|", "\\|")


def clip_lines(results: dict, systems: list[str]) -> list[str]:
    """Return the note under the verdict table about the ``clip`` column.

    The result is ``[]`` if no system has a ``clip_sensitivity`` block
    (results written before WU-0002.11e). Otherwise one line says what
    the column is and that it is report only (OD6: a fired flag marks
    nothing provisional). Then come one line per system for a block that
    was not computed, one for the clipped inputs that are held fixed (the
    regime tree, A3 and Kaplan-Meier inputs are not recomputed) and one
    for an H3a invariance that is not guaranteed.
    """
    blocks = {s: results["systems"][s].get("clip_sensitivity") for s in systems}
    if not any(blocks.values()):
        return []
    lines = [
        "",
        "Clip sensitivity (the `clip` column; WU-0002.11e, DEC-0017 Q6): "
        "each verdict is recomputed with every clipped PLP error at H_ref "
        "moved from 10 σ_x to 20 σ_x (the same states, draws, proxies, A3 "
        "network, regime tree and bootstrap resamples). "
        f"`{CLIP_MARK}` means 10 |Δ| exceeds the half-width of the "
        "verdict's own interval, or the verdict at 20 σ_x differs (Δ is "
        "the change of the estimate); `—` means no clipped H_ref entry "
        "feeds the verdict; a quantity that cannot be computed says so. It "
        "is reported next to the verdicts and changes none of them; it "
        "marks no result provisional (the clip is part of the estimand, v3 "
        "§4).",
    ]
    for s, block in blocks.items():
        if block is None:
            lines += [
                "",
                f"{s}: no `clip_sensitivity` block "
                "(results written before WU-0002.11e).",
            ]
            continue
        if block["status"] != "computed":
            lines += [
                "",
                f"{s}: clip sensitivity not computed: {block['reason']}.",
            ]
            continue
        if block["held_fixed_entries"]:
            lines += [
                "",
                f"{s}: tree, A3 and KM inputs contain "
                f"{block['held_fixed_entries']} clipped entries; not "
                "recomputed.",
            ]
        if block["invariance"]["H3a"].startswith(INVARIANCE_NOT_GUARANTEED):
            lines += ["", f"{s}: H3a invariance {block['invariance']['H3a']}."]
    return lines


# --- The H3a events and censored counts (WU-0004d, DEF-0018) ---
_H3A_EXPOSURE_HEAD = (
    "Exposure (DEF-0018; owner ruling B6b: keep as is, report the counts, "
    "state the exposure as a limitation): the H3a log-rank test sets no "
    "minimum number of states or events per regime (DEC-0011 O1; only the "
    "full sample needs 50 states), so a regime with few events can give an "
    "extreme log-rank p-value, for example one event among 99 censored "
    "states. "
)
_H3A_EXPOSURE_TAIL = (
    "This is a stated limitation of the H3a verdict; the verdict rule is "
    "unchanged."
)
# The limitation sentence of the H3a events/censored section (the exact
# text is pinned by a test). H3A_EXPOSURE_NO_COUNTS replaces it when no
# listed system carries the counts, so there is nothing to read the
# p-values beside (R4 of the WU-0004d review).
H3A_EXPOSURE = (
    _H3A_EXPOSURE_HEAD
    + "Read each p-value of the pair table beside the events and censored "
    "counts of its two regimes. " + _H3A_EXPOSURE_TAIL
)
H3A_EXPOSURE_NO_COUNTS = (
    _H3A_EXPOSURE_HEAD
    + "The events and censored counts are not recorded in this results "
    "file, so the exposure cannot be read from it. " + _H3A_EXPOSURE_TAIL
)


def h3a_regime_lines(results: dict, systems: list[str]) -> list[str]:
    """Return the ``H3a: events/censored per regime`` section, or ``[]``.

    H3a splits the states into regimes and compares their survival
    curves with log-rank tests. A "censored" state is one where the
    forecast had not yet failed when the horizon ended. A regime with
    very few events can give an extreme p-value, so the section shows the
    counts beside each p-value (WU-0004d, DEF-0018).

    The section has two tables and the exposure sentence
    (``H3A_EXPOSURE``). The first has one row per (system, regime), the
    regime index being the one used in ``H3a.pairs``: the states, events
    and censored states of the first evaluation draw, from
    ``n_per_regime``, ``n_events_per_regime`` and
    ``n_censored_per_regime``. The second has one row per tested pair, in
    test order, with the events and censored states of its two regimes
    beside its raw and Holm-adjusted p (``logrank_p_raw`` and
    ``logrank_p_holm`` as stored, "not computed" where the raw p is
    None). Nothing is recomputed.

    A system whose H3a block has neither new list (results written before
    WU-0004d) gets a line saying so, never a silent gap (PRIME.4). The
    section reads stored numbers only; it changes no verdict.

    Parameters
    ----------
    results : dict
        Study results.
    systems : list[str]
        The systems to show.

    Returns
    -------
    list[str]
        Markdown lines, from the ``##`` heading to the exposure sentence
        (no blank line before or after), or ``[]`` if no listed system
        has an H3a result.

    Raises
    ------
    ValueError
        If exactly one of the two new lists is present (a corrupt block,
        not an older file), if the lists differ in length, if events plus
        censored differ from the states of a regime, or if the pair lists
        differ in length or name a regime that has no count.
    """
    shown = [s for s in systems if "H3a" in results["systems"][s]]
    if not shown:
        return []
    rows: list[str] = []
    pair_rows: list[str] = []
    missing: list[str] = []
    for s in shown:
        block = results["systems"][s]["H3a"]
        has = (
            "n_events_per_regime" in block,
            "n_censored_per_regime" in block,
        )
        if has == (False, False):
            missing.append(s)
            continue
        if has != (True, True):
            raise ValueError(
                f"{s}: H3a block has only one of n_events_per_regime and "
                "n_censored_per_regime (a corrupt block, not an older "
                "results file)"
            )
        states = block["n_per_regime"]
        events = block["n_events_per_regime"]
        censored = block["n_censored_per_regime"]
        if not len(states) == len(events) == len(censored) or any(
            e + c != n for n, e, c in zip(states, events, censored)
        ):
            raise ValueError(
                f"{s}: H3a counts are inconsistent: n_per_regime {states}, "
                f"n_events_per_regime {events}, "
                f"n_censored_per_regime {censored}"
            )
        rows += [
            f"| {s} | {k} | {n} | {e} | {c} |"
            for k, (n, e, c) in enumerate(zip(states, events, censored))
        ]
        pairs = block["pairs"]
        raw, holm = block["logrank_p_raw"], block["logrank_p_holm"]
        if not len(pairs) == len(raw) == len(holm) or any(
            not 0 <= k < len(states) for pair in pairs for k in pair
        ):
            raise ValueError(
                f"{s}: H3a pairs are inconsistent: pairs {pairs}, "
                f"logrank_p_raw {raw}, logrank_p_holm {holm}"
            )
        for (a, b), p_raw, p_holm in zip(pairs, raw, holm):
            raw_text = "not computed" if p_raw is None else _fmt(p_raw, 3)
            pair_rows.append(
                f"| {s} | {a}, {b} | {events[a]}/{censored[a]} | "
                f"{events[b]}/{censored[b]} | {raw_text} | "
                f"{_fmt(p_holm, 3)} |"
            )
    # Each paragraph is preceded by a blank line.
    blocks: list[list[str]] = []
    if rows:
        blocks.append(
            [
                "| System | Regime | States | Events | Censored |",
                "|---|---|---|---|---|",
                *rows,
            ]
        )
        blocks.append(
            [
                "Tested pairs, in test order (regime indices as above; "
                "events/censored of each regime of the pair):",
                "",
                "| System | Pair (a, b) | Events/censored a | "
                "Events/censored b | Raw p | Holm p |",
                "|---|---|---|---|---|---|",
                *pair_rows,
            ]
        )
    blocks += [
        [
            f"{s}: events/censored per regime not recorded "
            "(results written before WU-0004d)."
        ]
        for s in missing
    ]
    lines = ["## H3a: events/censored per regime (DEF-0018)"]
    exposure = H3A_EXPOSURE if rows else H3A_EXPOSURE_NO_COUNTS
    for paragraph in [*blocks, [exposure]]:
        lines += ["", *paragraph]
    return lines


def _verdict_rows(
    results: dict, systems: list[str], with_clip: bool
) -> list[str]:
    """Return the rows of the verdict table, one per hypothesis-table row.

    A table row without a result is listed with "n/a: no result", never
    dropped.
    """
    rows = []
    ver = results["verdicts"]
    for row in HYPOTHESIS_TABLE:
        if row.key not in ver:
            cells = ["n/a: no result" for _ in systems]
            rows.append(
                f"| {row.v3_id} | {_hypothesis_text(row, computed=False)} | "
                + " | ".join(cells)
                + " | no result |"
                + (" n/a |" if with_clip else "")
            )
            continue
        cells = []
        for s in systems:
            numbers = _key_number(row.key, results["systems"][s])
            if row.role == "estimate":
                cells.append(f"{ver[row.key]['by_system'][s]}: {numbers}")
            elif row.role == "reported":  # no bar, so no flag
                cells.append(numbers)
            else:
                flag = FLAGS[ver[row.key]["by_system"][s]]
                cells.append(f"{flag}: {numbers}")
        missing = ver[row.key].get("missing_systems")
        overall = ver[row.key]["verdict"] + (
            f" (missing: {', '.join(missing)})" if missing else ""
        )
        rows.append(
            f"| {row.v3_id} | {HYPOTHESES[row.key]} | "
            + " | ".join(cells)
            + f" | {overall} |"
            + (
                f" {clip_cells(results, systems, row.key)} |"
                if with_clip
                else ""
            )
        )
    return rows


def _allocation_lines(results: dict, systems: list[str]) -> list[str]:
    """Return the allocation-rule tables, one per system.

    An allocation rule (A0 to A5, A*) decides the weight w on CP for a
    forecast. Each table shows each rule's mean squared error (MSE) at
    every horizon, its regret, and its survival summaries, then how much
    of the oracle's gain the deployable rules recover.
    """
    lines = ["", "## Allocation rules at the core cell (test split)", ""]
    for s in systems:
        sc = results["systems"][s]["scores"]
        horizons = list(next(iter(sc.values()))["mse"])
        lines += [
            f"### {s}",
            "",
            "| Rule | "
            + " | ".join(f"MSE {h}" for h in horizons)
            + " | regret H_ref | agreement | KM median (LT) | RMST (LT) |",
            "|---|" + "---|" * (len(horizons) + 4),
        ]
        for rule, v in sc.items():
            lines.append(
                f"| {rule} {RULE_LABELS[rule]} | "
                + " | ".join(_fmt(x, 3) for x in v["mse"].values())
                + f" | {_fmt(v['regret'][horizons[2]], 3)} | "
                f"{_fmt(v['agreement_href'], 3)} | "
                f"{_fmt(v['km_median_lyapunov'], 3)} | "
                f"{_fmt(v['rmst_lyapunov'], 3)} |"
            )
        rec = results["systems"][s]["oracle_recovery"]
        lines += [
            "",
            f"Oracle recovery: A4 recovers {_fmt(100 * rec['A4_vs_A4o'], 3)}% "
            "of the oracle-seed closed form's gain over A2; A5 recovers "
            f"{_fmt(100 * rec['A5_vs_Astar'], 3)}% of A*'s.",
            "",
        ]
    return lines


def _validation_lines(
    results: dict, systems: list[str], config: StudyConfig
) -> list[str]:
    """Return the validation-gate table (checks V1 to V7).

    The gate checks that the code's own building blocks (Jacobians,
    estimator, integrator, Kaplan-Meier estimate) behave as theory says,
    before anyone trusts a hypothesis result. A gate FAIL marks that
    system's results provisional.
    """
    lines = [
        "## Validation gate",
        "",
        "| Check | Criterion | " + " | ".join(systems) + " |",
        "|---|---|" + "---|" * len(systems),
    ]
    for key, (label, criterion, ok) in VALIDATION_CRITERIA.items():
        cells = []
        for s in systems:
            val = results["systems"][s]["validation"]
            if key == "convergence":
                used = str(config.n_oracle_draws)
                value = val["convergence"][used]["median_half_width"]
            else:
                value = val[key]
            flag = "" if ok is None else (" PASS" if ok(value) else " FAIL")
            cells.append(_fmt(value, 3) + flag)
        lines.append(f"| {label} | {criterion} | " + " | ".join(cells) + " |")
    return lines + _v7_rows(results, systems, config)


def _robustness_lines(results: dict) -> list[str]:
    """Return the robustness tables (core cell), one per system.

    Each row repeats the main numbers under a variant of the setup, so a
    reader can see whether the conclusions depend on one design choice.
    """
    lines = ["", "## Robustness (core cell)", ""]
    for s, variants in results["robustness"].items():
        lines += [
            f"### {s}",
            "",
            "| Variant | H2a range | H2a partial r (w*=0) | "
            "H2a partial r (interior) | A4 vs A2 | A4/A3 | A5 regret | "
            "H1b CP | H1b PLP |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
        for label, v in variants.items():
            if "error" in v:
                lines.append(f"| {label} | error: {v['error']} | | | | | | | |")
            elif "H2a_partial_corr_zero_fin" in v:
                lines.append(
                    f"| {label} | | "
                    f"{_fmt(v['H2a_partial_corr_zero_fin'], 2)} | "
                    f"{_fmt(v['H2a_partial_corr_interior_fin'], 2)} | | | | | "
                    f"corr(fin, lin) {_fmt(v['corr_fin_vs_linear'], 2)} |"
                )
            else:
                lines.append(
                    f"| {label} | {_fmt(v['H2a_median_range'], 3)} | "
                    f"{_fmt(v['H2a_partial_corr_zero'], 2)} | "
                    f"{_fmt(v['H2a_partial_corr_interior'], 2)} | "
                    f"{_fmt(100 * v['A4_vs_A2_relative'], 3)}% | "
                    f"{_fmt(v['A4_over_A3'], 3)} | "
                    f"{_fmt(100 * v['A5_regret_ratio'], 3)}% | "
                    f"{_fmt(v['H1b']['CP']['slope'], 3)} | "
                    f"{_fmt(v['H1b']['PLP']['slope'], 3)} |"
                )
    return lines


# Text of an extension run that is wrong or misleading for systems outside the
# three v3 systems (WU-0021 review R5): (old, new) pairs, each of which must
# occur in the generated report (a vanished pattern raises, never a silent
# no-op). Applied only to extension runs, so the report of a v3 run is unchanged.
EXTENSION_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    (
        "(18.47 for dof 4)",
        "(18.47 for dof 4, 16.27 for dof 3: the dof of a system is D − m, "
        "listed in the table)",
    ),
    (
        "the three systems are mathematical models",
        "the systems of this run are mathematical models",
    ),
    (
        "exact model, three systems, scalar observable",
        "exact model, the systems of this run, scalar observable",
    ),
    (
        "(DEVELOPMENT (DEV-0) against the v1 pilot, M5);",
        "(DEVELOPMENT (DEV-0) against the v1 pilot, M5; calibrated on the "
        "three v3 systems, not established for the extension systems);",
    ),
    (
        "and three systems (this QoI:",
        "and the three v3 systems, not the extension systems (this QoI, on "
        "the v3 systems:",
    ),
)
# Lines about Chua, dropped from an extension run that does not include Chua.
CHUA_ONLY_PREFIXES = (
    "Chua at the study's own parameters",
    "| chua, memo parameter set",
)


def extension_text(lines: list[str], systems: list[str]) -> list[str]:
    """Return the report lines of an extension run with the v3-only text fixed.

    Applies ``EXTENSION_REPLACEMENTS`` and, when Chua is not in the run, drops
    the Chua paragraph and the Chua memo row of the Lyapunov section. Raises
    ``ValueError`` if a pattern does not occur (the report text changed).
    """
    out = list(lines)
    for old, new in EXTENSION_REPLACEMENTS:
        hits = sum(line.count(old) for line in out)
        if hits == 0:
            raise ValueError(
                f"extension text pattern not found in the report: {old!r}"
            )
        out = [line.replace(old, new) for line in out]
    if "chua" not in systems:
        out = [ln for ln in out if not ln.startswith(CHUA_ONLY_PREFIXES)]
    return out


def extension_note_lines(results: dict) -> list[str]:
    """Return the note of an extension run (blank line and text), else ``[]``.

    The note is added when any stored verdict is ``PER_SYSTEM_VERDICT``, so the
    report of a run of the three v3 systems is unchanged.
    """
    stored = results.get("verdicts", {})
    if any(v.get("verdict") == PER_SYSTEM_VERDICT for v in stored.values()):
        return ["", EXTENSION_NOTE]
    return []


def write_markdown(results: dict, config: StudyConfig, path: Path) -> None:
    """Write the human-readable results report (``RESULTS.md``).

    The sections come in this order: provenance header, verdict table
    with its clip column and interval labels, quantities of interest,
    allocation rules, H3a counts, validation gate, verification
    subsections, uncertainty budget, robustness, figure captions and the
    Handling section.

    Parameters
    ----------
    results : dict
        Study results.
    config : StudyConfig
        Configuration.
    path : Path
        Output file.
    """
    systems = [s for s in config.core_systems if s in results["systems"]]
    # The clip column appears only if some system carries a
    # clip_sensitivity block (WU-0002.11e).
    with_clip = any(
        "clip_sensitivity" in results["systems"][s] for s in systems
    )
    gate = {
        s: results["systems"][s]["validation"].get("gate", {}).get("gate_pass")
        for s in systems
    }
    gate_words = {
        True: "PASS",
        False: "FAIL (results provisional)",
        None: "n/a",
    }
    gate_text = ", ".join(
        f"{s} {gate_words[None if g is None else bool(g)]}"
        for s, g in gate.items()
    )
    gate_lines = ["", "Validation gate: " + gate_text]
    if config.name == "smoke":
        gate_lines += ["", SMOKE_GATE_NOTE]
    lines = [
        f"# Results — preset `{config.name}`",
        "",
        *header_lines(results.get("provenance")),
        "",
        INTRO,
        *extension_note_lines(results),
        "",
        "## Hypothesis verdicts",
        *gate_lines,
        "",
        "| ID | Hypothesis | "
        + " | ".join(systems)
        + " | Verdict |"
        + (" clip |" if with_clip else ""),
        "|---|---|"
        + "---|" * len(systems)
        + "---|"
        + ("---|" if with_clip else ""),
        *_verdict_rows(results, systems, with_clip),
        *clip_lines(results, systems),
        *interval_label_lines(results, systems, config),
        "",
        *qoi_declaration_lines(config),
        *_allocation_lines(results, systems),
    ]
    # The H3a section comes after the allocation rules so that the interval
    # label lines of the verdict table still come before the next heading
    # (test_budget L1).
    h3a_section = h3a_regime_lines(results, systems)
    lines += [*h3a_section, ""] if h3a_section else []
    lines += _validation_lines(results, systems, config)
    lines += [
        "",
        v4_label_line(config),
        "",
        "### Largest Lyapunov exponent against published values",
        "",
        *_lyapunov_lines(results, systems),
        "",
        "### Theorem P2(c) bound (verification check, not a hypothesis)",
        "",
        *_p2c_lines(results, systems),
        "",
        "### Levenberg–Marquardt diagnostics "
        "(verification, NVVUQ.10; not a hypothesis)",
        "",
        *_lm_lines(results, systems, config),
        "",
        *budget_lines(results, systems, config),
    ]
    if "robustness" in results:
        lines += _robustness_lines(results)
    lines += [
        "",
        *figure_caption_lines(config),
        "",
        *handling_lines(results, systems),
    ]
    if extension_note_lines(results):
        lines = extension_text(lines, systems)
    path.write_text("\n".join(lines) + "\n")


def _style(ax: plt.Axes) -> None:
    """Give an axes the study's look: light grid, gray spines and text."""
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(INK_2)
    ax.tick_params(colors=INK_2, labelsize=8)
    ax.xaxis.label.set_color(INK)
    ax.yaxis.label.set_color(INK)
    ax.title.set_color(INK)


def _new_figure(count: int) -> tuple[plt.Figure, list[plt.Axes]]:
    """Return a figure with one axes per system, side by side."""
    fig, axes = plt.subplots(
        1, count, figsize=(4.2 * count, 3.4), squeeze=False
    )
    return fig, list(axes[0])


def _save_figure(
    fig: plt.Figure, name: str, config: StudyConfig, out_dir: Path
) -> Path:
    """Lay out, caption, save (150 dpi) and close a figure; return its path."""
    fig.tight_layout()
    caption_figure(fig, name, config)
    path = out_dir / name
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def make_figures(
    results: dict, config: StudyConfig, out_dir: Path
) -> list[Path]:
    """Write the four standard figures (PNG), one panel per core system.

    The figures are the oracle weight against the horizon, the
    Kaplan-Meier curves of each allocation rule, the regret against the
    number of regimes K, and the weight against the library size. Each
    PNG carries its caption from ``budget.FIGURE_CAPTIONS``.

    Parameters
    ----------
    results : dict
        Study results.
    config : StudyConfig
        Configuration.
    out_dir : Path
        Figure directory.

    Returns
    -------
    list[Path]
        Written files.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    lt = config.steps_per_lyapunov
    systems = [s for s in config.core_systems if s in results["systems"]]

    fig, axes = _new_figure(len(systems))
    for ax, s in zip(axes, systems):
        prof = results["systems"][s]["weight_profile"]
        h = np.array(prof["horizons"]) / lt
        ax.fill_between(
            h,
            prof["q25"],
            prof["q75"],
            color=SERIES[0],
            alpha=0.18,
            linewidth=0,
        )
        ax.plot(h, prof["median"], color=SERIES[0], linewidth=2)
        ax.axvline(1.0, color=INK_2, linewidth=1, linestyle=":")
        ax.set(
            xlabel="Horizon (Lyapunov times)",
            ylabel="Oracle weight on CP, w*",
            title=f"{s}: median and IQR of w*(s, H)",
            ylim=(0, 1),
        )
        _style(ax)
    written.append(
        _save_figure(fig, "separation_weight_vs_horizon.png", config, out_dir)
    )

    fig, axes = _new_figure(len(systems))
    for ax, s in zip(axes, systems):
        curves = results["systems"][s]["km_curves"]
        for color, rule in zip(SERIES, PLOTTED_RULES):
            if rule in curves:
                ax.step(
                    np.arange(1, len(curves[rule]) + 1) / lt,
                    curves[rule],
                    where="post",
                    color=color,
                    linewidth=1.6,
                    label=rule,
                )
        ax.set(
            xlabel="Horizon (Lyapunov times)",
            ylabel="Pr(T > H)",
            title=f"{s}: realized horizons, theta={config.primary_threshold:g}",
        )
        ax.legend(frameon=False, fontsize=7, ncol=2, labelcolor=INK_2)
        _style(ax)
    written.append(
        _save_figure(fig, "kaplan_meier_by_rule.png", config, out_dir)
    )

    fig, axes = _new_figure(len(systems))
    for ax, s in zip(axes, systems):
        curve = results["systems"][s]["regime_curve"]["regret_ratio_by_K"]
        ks = np.array(sorted(map(int, curve)))
        ax.semilogx(
            ks,
            [100 * curve[str(k)] for k in ks],
            color=SERIES[0],
            linewidth=2,
            marker="o",
            markersize=5,
        )
        ax.axhline(5.0, color=INK_2, linewidth=1, linestyle=":")
        ax.set_xticks(ks)
        ax.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter("%d"))
        ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        ax.set_ylim(bottom=0)
        ax.set(
            xlabel="Number of regimes K",
            ylabel="Regret (% of best-single MSE)",
            title=f"{s}: abstraction regret (dotted: 5% criterion)",
        )
        _style(ax)
    written.append(_save_figure(fig, "regret_vs_regimes.png", config, out_dir))

    fig, axes = _new_figure(len(systems))
    for ax, s in zip(axes, systems):
        lib = results["systems"][s]["H2b"]["library_curves"]
        for color, (rho, curve) in zip(SERIES, lib.items()):
            sizes = np.array([int(n) for n in curve])
            ax.semilogx(
                sizes,
                [v["median"] for v in curve.values()],
                color=color,
                linewidth=2,
                marker="o",
                markersize=5,
                label=f"rho = {float(rho) * 100:g}% sigma_x",
            )
        ax.set(
            xlabel="Library size n_lib",
            ylabel="Median w*(H_ref)",
            ylim=(0, 1),
            title=f"{s}: weight vs library size",
        )
        ax.legend(frameon=False, fontsize=7, labelcolor=INK_2)
        _style(ax)
    written.append(
        _save_figure(fig, "knob_response_library.png", config, out_dir)
    )
    return written


def save_json(obj: dict, path: Path) -> None:
    """Write ``obj`` as JSON, converting NumPy values and non-finite floats.

    NumPy scalars, booleans and arrays become plain Python values;
    anything else unknown is written as its string. NaN and infinity are
    written as the JSON extensions ``NaN`` and ``Infinity`` (``allow_nan``
    is true), never silently dropped.
    """

    def default(value):
        if isinstance(value, (np.floating, np.integer)):
            return value.item()
        if isinstance(value, np.bool_):
            return bool(value)
        if isinstance(value, np.ndarray):
            return value.tolist()
        return str(value)

    path.write_text(json.dumps(obj, indent=2, default=default, allow_nan=True))
