"""Hypothesis verdicts, markdown report and figures."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import matplotlib.ticker

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from .allocation import RULE_LABELS  # noqa: E402
from .config import StudyConfig  # noqa: E402
from .identifiers import HYPOTHESIS_TABLE, Hypothesis, check_keys  # noqa: E402

SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7",
          "#e34948"]
INK, INK_2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
PLOTTED_RULES = ["A0", "A1", "A2", "A3", "A4", "A5", "A*"]

def _hypothesis_text(row: Hypothesis, computed: bool = True) -> str:
    """Report text of a table row: role mark, v3 criterion, and the pending note if any.

    ``computed`` is false for a row with no result: its note then says "not computed" instead
    of "computed with the v1 statistic".
    """
    text = ("[primary] " if row.role == "primary" else "") + row.criterion
    if row.pending:
        until = ", ".join(row.pending)
        text += (f" [computed with the v1 statistic until {until}]" if computed
                 else f" [not computed until {until}]")
    return text


HYPOTHESES: dict[str, str] = {row.key: _hypothesis_text(row) for row in HYPOTHESIS_TABLE}


VALIDATION_CRITERIA = {
    "delay_jacobian_rel_err": ("V1 delay-map Jacobian vs finite differences", "< 1e-4",
                               lambda v: v < 1e-4),
    "gain_rel_err": ("V1 amplifier g_H vs finite differences", "< 1e-4", lambda v: v < 1e-4),
    "crlb_ratio_median": ("V2 least squares / Cramer-Rao", "[0.8, 1.2]",
                          lambda v: 0.8 <= v <= 1.2),
    "cp_median_vpt_lyapunov": ("V3 CP valid-prediction time (LT, theta=0.4)", "reported", None),
    "convergence": ("V4 w* bootstrap half-width at used M", "<= 0.05", lambda v: v <= 0.05),
    "km_max_abs_dev": ("V5 Kaplan-Meier vs exact", "< 0.01", lambda v: v < 0.01),
    "integrator_max_dev_sigma": ("V6 RK4 step halving (sigma_x)", "< 1e-3",
                                 lambda v: v < 1e-3),
}


def verdicts(results: dict, config: StudyConfig) -> dict:
    """Aggregate per-system pass flags into supported / partial / not supported.

    Parameters
    ----------
    results : dict
        Study results.
    config : StudyConfig
        Configuration (core systems).

    Returns
    -------
    dict
        Result key of each table row that has a result to per-system flags and verdict. A row
        with no result in any system is absent; a row with a result in some systems only raises
        ``KeyError``.

    Raises
    ------
    ValueError
        If a system's results carry a hypothesis-shaped key that is not in the identifier table
        (results written before WU-0002.2): nothing is relabelled.
    """
    out = {}
    systems = [s for s in config.core_systems if s in results["systems"]]
    for s in systems:  # before any flag is read: a pre-v3 results file must not be relabelled
        try:
            check_keys(results["systems"][s])
        except ValueError as stale:
            raise ValueError(f"results of system {s} use identifiers of a schema older than "
                             f"WU-0002.2 (v1 keys); regenerate them with a new run: {stale}"
                             ) from None
    for row in HYPOTHESIS_TABLE:
        if not any(row.key in results["systems"][s] for s in systems):
            continue  # no result yet (v3 H2e until WU-0002.7); write_markdown lists the row
        flags = {s: bool(results["systems"][s][row.key]["pass"]) for s in systems}
        n_pass = sum(flags.values())
        verdict = ("supported" if flags and n_pass == len(flags) else
                   "partially supported" if n_pass else "not supported")
        out[row.key] = {"by_system": flags, "verdict": verdict}
    return out


def _fmt(value: float, digits: int = 3) -> str:
    return "n/a" if value is None or (isinstance(value, float) and np.isnan(value)) \
        else f"{value:.{digits}g}"


def _key_number(key: str, res: dict) -> str:
    """One-line numeric summary of a result (by its table key) for one system."""
    r = res[key]
    match key:
        case "H1a":
            parts = [f"rho={k}: 1/d (n_lib fit)={_fmt(v['fitted_inverse_dim'])}, "
                     f"ratio {_fmt(v['ratio'])} [{_fmt(v['ratio_ci'][0])}, "
                     f"{_fmt(v['ratio_ci'][1])}] {v['verdict']}"
                     for k, v in r["by_noise"].items()]
            return "; ".join(parts) + f" (1/d_LB={_fmt(r['inverse_dim_reference'])})"
        case "H1b":
            return f"CP {_fmt(r['CP']['slope'])}, PLP {_fmt(r['PLP']['slope'])}"
        case "H1c":
            return f"PLP {_fmt(r['PLP'].get('median_ratio', float('nan')))}, " \
                   f"CP {_fmt(r['CP'].get('median_ratio', float('nan')))}"
        case "H1d":
            s = r["spearman"]
            return f"eps {_fmt(s['analog_seed'], 2)}, delta {_fmt(s['estimation_seed'], 2)}, " \
                   f"Lambda {_fmt(s['growth'], 2)}, N {_fmt(s['noise_sensitivity'], 2)}"
        case "Q-N":
            d = r["deployable"]
            return f"{d['verdict']}: dR2 w {_fmt(d['logit_w']['delta_r2'], 2)} " \
                   f"[{_fmt(d['logit_w']['ci'][0], 2)}, {_fmt(d['logit_w']['ci'][1], 2)}], " \
                   f"T {_fmt(d['log_horizon']['delta_r2'], 2)} " \
                   f"[{_fmt(d['log_horizon']['ci'][0], 2)}, {_fmt(d['log_horizon']['ci'][1], 2)}]; " \
                   f"oracle: {r['oracle']['verdict']}"
        case "H2a":
            return f"range {_fmt(r['median_range'])} (CI hi {_fmt(r['range_ci'][1])}); " \
                   f"partial r {_fmt(r['partial_corr'], 2)}"
        case "H2b":
            lib = "; ".join(f"n_lib@{k}: w*(n_lib max)={_fmt(v['median_at_largest_n_lib'], 2)}"
                            for k, v in r["library"].items())
            return f"rho rank corr {_fmt(r['noise']['mean_state_spearman'], 2)}; {lib}"
        case "H2c":
            return f"A4-A2 {_fmt(100 * r['A4_minus_A2']['relative'], 3)}%; " \
                   f"A4-{r['best_single']} " \
                   f"{_fmt(100 * r['A4_minus_' + r['best_single']]['relative'], 3)}%"
        case "H2d":
            return f"A4/A3-1 = {_fmt(100 * r['in_distribution_excess'], 3)}%"
        case "gain_bound":
            return f"within bound {_fmt(r['fraction_within_bound'], 3)} " \
                   f"(n={r['n_states']}, max gain {_fmt(r['max_gain_lyapunov'], 2)} LT)"
        case "H3a":
            return f"K={r['chosen_K']}: regret {_fmt(100 * r['regret_ratio'], 3)}%, " \
                   f"IQR {_fmt(r['mean_iqr_lyapunov'], 2)} LT"
        case "H3b":
            return f"Lambda imp: weight {_fmt(r['weight_tree_importance']['lambda_tilde'], 2)}, " \
                   f"horizon {_fmt(r['horizon_tree_importance']['lambda_tilde'], 2)}"
        case "H3c":
            return f"A5/A4 {_fmt(r['A5_over_A4_mse'], 4)}"
    return ""


def _cell(value: object) -> str:
    """Render one provenance value for a Markdown table cell."""
    if value is None:
        return "null"
    text = value if isinstance(value, str) else json.dumps(value)
    return text.replace("|", "\\|").replace("\n", " ")


def header_lines(provenance: dict | None) -> list[str]:
    """Return the Markdown lines of the RESULTS.md provenance header (LPC.PC.13, LPC.PC.18).

    Parameters
    ----------
    provenance : dict or None
        The ``results["provenance"]`` block, used as stored. ``None`` for output written
        before the block existed.

    Returns
    -------
    list[str]
        The label line, then a two-column table of every key except ``config``, then the
        full configuration as JSON in a ``<details>`` block.
    """
    if provenance is None:
        return ["**UNPROMOTED** · provenance absent (output written before WU-0001)"]
    label = provenance["label"]
    lines = [f"**{label}**" if "UNPROMOTED" in label else f"**{label}** · **UNPROMOTED**", "",
             "| Provenance | Value |", "|---|---|"]
    lines += [f"| {key} | {_cell(value)} |" for key, value in provenance.items()
              if key != "config"]
    lines += ["", "<details><summary>Full configuration</summary>", "", "```json",
              json.dumps(provenance["config"], indent=2), "```", "", "</details>"]
    return lines


def _v7_rows(results: dict, systems: list[str]) -> list[str]:
    """The two V7 rows of the validation table (WU-0002.10): efficiency at every rho, slope.

    The efficiency cell is the minimum to maximum over rho of the median ``delta / (rho nu)``,
    flagged PASS only if every level passes; the slope cell is the median slope of ``ln delta``
    on ``ln rho``. A system without a V7 result shows "n/a" (no flag).
    """
    eff_cells, slope_cells = [], []
    for s in systems:
        v7 = results["systems"][s].get("V7")
        if v7 is None:
            eff_cells.append("n/a")
            slope_cells.append("n/a")
            continue
        values = list(v7["efficiency_median_by_noise"].values())
        ok = all(v7["efficiency_pass_by_noise"].values())
        eff_cells.append(f"{_fmt(float(np.min(values)), 3)}–{_fmt(float(np.max(values)), 3)}"
                         + (" PASS" if ok else " FAIL"))
        slope_cells.append(_fmt(v7["median_slope"], 3) + (" PASS" if v7["slope_pass"] else " FAIL"))
    return ["| V7 median δ/(ρν), every ρ | [0.9, 1.1] | " + " | ".join(eff_cells) + " |",
            "| V7 median slope of ln δ on ln ρ | [0.9, 1.1] | " + " | ".join(slope_cells) + " |"]


def write_markdown(results: dict, config: StudyConfig, path: Path) -> None:
    """Write the human-readable results report.

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
    lines = [f"# Results — preset `{config.name}`", "",
             *header_lines(results.get("provenance")), "",
             "Generated by `python -m lpcstudy`. Pass/fail criteria are the pre-registered "
             "thresholds of the Methods document (§M9). A hypothesis is *supported* if it "
             "passes on every core system, *partially supported* if on at least one.", "",
             "## Hypothesis verdicts", "",
             "| ID | Hypothesis | " + " | ".join(systems) + " | Verdict |",
             "|---|---|" + "---|" * len(systems) + "---|"]
    gate = {s: results["systems"][s]["validation"].get("gate", {}).get("gate_pass")
            for s in systems}
    lines[lines.index("## Hypothesis verdicts") + 1:lines.index("## Hypothesis verdicts") + 1] = [
        "", "Validation gate: " + ", ".join(
            f"{s} {'PASS' if g else 'FAIL (results provisional)' if g is not None else 'n/a'}"
            for s, g in gate.items())]
    ver = results["verdicts"]
    for row in HYPOTHESIS_TABLE:
        if row.key not in ver:  # a table row without a result is listed, not dropped
            cells = ["n/a: no result" for _ in systems]
            lines.append(f"| {row.v3_id} | {_hypothesis_text(row, computed=False)} | "
                         + " | ".join(cells) + " | no result |")
            continue
        cells = []
        for s in systems:
            flag = "PASS" if ver[row.key]["by_system"][s] else "FAIL"
            cells.append(f"{flag}: {_key_number(row.key, results['systems'][s])}")
        lines.append(f"| {row.v3_id} | {HYPOTHESES[row.key]} | " + " | ".join(cells)
                     + f" | {ver[row.key]['verdict']} |")

    lines += ["", "## Allocation rules at the core cell (test split)", ""]
    for s in systems:
        sc = results["systems"][s]["scores"]
        horizons = list(next(iter(sc.values()))["mse"])
        lines += [f"### {s}", "", "| Rule | " + " | ".join(f"MSE {h}" for h in horizons) +
                  " | regret H_ref | agreement | KM median (LT) | RMST (LT) |",
                  "|---|" + "---|" * (len(horizons) + 4)]
        for rule, v in sc.items():
            lines.append(f"| {rule} {RULE_LABELS[rule]} | " +
                         " | ".join(_fmt(x, 3) for x in v["mse"].values()) +
                         f" | {_fmt(v['regret'][horizons[2]], 3)} | "
                         f"{_fmt(v['agreement_href'], 3)} | {_fmt(v['km_median_lyapunov'], 3)} | "
                         f"{_fmt(v['rmst_lyapunov'], 3)} |")
        rec = results["systems"][s]["oracle_recovery"]
        lines += ["", f"Oracle recovery: A4 recovers {_fmt(100 * rec['A4_vs_A4o'], 3)}% of the "
                  f"oracle-seed closed form's gain over A2; A5 recovers "
                  f"{_fmt(100 * rec['A5_vs_Astar'], 3)}% of A*'s.", ""]

    lines += ["## Validation gate", "", "| Check | Criterion | " + " | ".join(systems) + " |",
              "|---|---|" + "---|" * len(systems)]
    for key, (label, criterion, ok) in VALIDATION_CRITERIA.items():
        cells = []
        for s in systems:
            val = results["systems"][s]["validation"]
            value = val["convergence"][str(config.n_oracle_draws)]["median_half_width"] \
                if key == "convergence" else val[key]
            flag = "" if ok is None else (" PASS" if ok(value) else " FAIL")
            cells.append(_fmt(value, 3) + flag)
        lines.append(f"| {label} | {criterion} | " + " | ".join(cells) + " |")
    lines += _v7_rows(results, systems)

    if "robustness" in results:
        lines += ["", "## Robustness (core cell)", ""]
        for s, variants in results["robustness"].items():
            lines += [f"### {s}", "", "| Variant | H2a range | H2a partial r | A4 vs A2 | "
                      "A4/A3 | A5 regret | H1b CP | H1b PLP |", "|---|---|---|---|---|---|---|---|"]
            for label, v in variants.items():
                if "error" in v:
                    lines.append(f"| {label} | error: {v['error']} | | | | | | |")
                elif "H2a_partial_corr_fin" in v:
                    lines.append(f"| {label} | | {_fmt(v['H2a_partial_corr_fin'], 2)} | | | | | "
                                 f"corr(fin, lin) {_fmt(v['corr_fin_vs_linear'], 2)} |")
                else:
                    lines.append(
                        f"| {label} | {_fmt(v['H2a_median_range'], 3)} | "
                        f"{_fmt(v['H2a_partial_corr'], 2)} | "
                        f"{_fmt(100 * v['A4_vs_A2_relative'], 3)}% | {_fmt(v['A4_over_A3'], 3)} | "
                        f"{_fmt(100 * v['A5_regret_ratio'], 3)}% | "
                        f"{_fmt(v['H1b']['CP']['slope'], 3)} | {_fmt(v['H1b']['PLP']['slope'], 3)} |")
    path.write_text("\n".join(lines) + "\n")


def _style(ax: plt.Axes) -> None:
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


def make_figures(results: dict, config: StudyConfig, out_dir: Path) -> list[Path]:
    """Write the standard figures (PNG) for each core system.

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
    fig, axes = plt.subplots(1, len(systems), figsize=(4.2 * len(systems), 3.4), squeeze=False)
    for ax, s in zip(axes[0], systems):
        prof = results["systems"][s]["weight_profile"]
        h = np.array(prof["horizons"]) / lt
        ax.fill_between(h, prof["q25"], prof["q75"], color=SERIES[0], alpha=0.18, linewidth=0)
        ax.plot(h, prof["median"], color=SERIES[0], linewidth=2)
        ax.axvline(1.0, color=INK_2, linewidth=1, linestyle=":")
        ax.set(xlabel="Horizon (Lyapunov times)", ylabel="Oracle weight on CP, w*",
               title=f"{s}: median and IQR of w*(s, H)", ylim=(0, 1))
        _style(ax)
    fig.tight_layout()
    path = out_dir / "separation_weight_vs_horizon.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    written.append(path)

    fig, axes = plt.subplots(1, len(systems), figsize=(4.2 * len(systems), 3.4), squeeze=False)
    for ax, s in zip(axes[0], systems):
        curves = results["systems"][s]["km_curves"]
        for color, rule in zip(SERIES, PLOTTED_RULES):
            if rule in curves:
                ax.step(np.arange(1, len(curves[rule]) + 1) / lt, curves[rule], where="post",
                        color=color, linewidth=1.6, label=rule)
        ax.set(xlabel="Horizon (Lyapunov times)", ylabel="Pr(T > H)",
               title=f"{s}: realized horizons, theta={config.primary_threshold:g}")
        ax.legend(frameon=False, fontsize=7, ncol=2, labelcolor=INK_2)
        _style(ax)
    fig.tight_layout()
    path = out_dir / "kaplan_meier_by_rule.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    written.append(path)

    fig, axes = plt.subplots(1, len(systems), figsize=(4.2 * len(systems), 3.4), squeeze=False)
    for ax, s in zip(axes[0], systems):
        curve = results["systems"][s]["regime_curve"]["regret_ratio_by_K"]
        ks = np.array(sorted(map(int, curve)))
        ax.semilogx(ks, [100 * curve[str(k)] for k in ks], color=SERIES[0], linewidth=2,
                    marker="o", markersize=5)
        ax.axhline(5.0, color=INK_2, linewidth=1, linestyle=":")
        ax.set_xticks(ks)
        ax.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter("%d"))
        ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        ax.set_ylim(bottom=0)
        ax.set(xlabel="Number of regimes K", ylabel="Regret (% of best-single MSE)",
               title=f"{s}: abstraction regret (dotted: 5% criterion)")
        _style(ax)
    fig.tight_layout()
    path = out_dir / "regret_vs_regimes.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    written.append(path)

    fig, axes = plt.subplots(1, len(systems), figsize=(4.2 * len(systems), 3.4), squeeze=False)
    for ax, s in zip(axes[0], systems):
        lib = results["systems"][s]["H2b"]["library"]
        for color, (rho, v) in zip(SERIES, lib.items()):
            sizes = np.array(list(map(int, v["median_w_by_n_lib"])))
            ax.semilogx(sizes, list(v["median_w_by_n_lib"].values()), color=color, linewidth=2,
                        marker="o", markersize=5, label=f"rho = {float(rho) * 100:g}% sigma_x")
        ax.set(xlabel="Library size n_lib", ylabel="Median w*(H_ref)", ylim=(0, 1),
               title=f"{s}: weight vs library size")
        ax.legend(frameon=False, fontsize=7, labelcolor=INK_2)
        _style(ax)
    fig.tight_layout()
    path = out_dir / "knob_response_library.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    written.append(path)
    return written


def save_json(obj: dict, path: Path) -> None:
    """Write JSON, converting numpy scalars and non-finite values."""
    def default(value):
        if isinstance(value, (np.floating, np.integer)):
            return value.item()
        if isinstance(value, np.bool_):
            return bool(value)
        if isinstance(value, np.ndarray):
            return value.tolist()
        return str(value)
    path.write_text(json.dumps(obj, indent=2, default=default, allow_nan=True))
