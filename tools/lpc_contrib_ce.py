#!/usr/bin/env python3
"""Phase J experiments C and E on one run directory (WU-0049).

DEVELOPMENT, exploratory: every table and figure carries "DEVELOPMENT
(DEV-n): exploratory, not a hypothesis test". No causal claim; nothing is set
beside CONF-1. The tool reads one run's state dumps (schema /3), its
``results.json`` and, for C1 and the Shapley rank correlation of C2, the A/D
record ``contrib.json`` that ``tools/lpc_contrib.py`` wrote for the same run.
It runs ``lpcstudy.joint_decisions.analyze_joint`` (C2, C3) and the
``lpcstudy.mechanisms`` blocks (E-H2a, E-H2e, E-H3c) per system on the CPU and
writes ``ce.json``, ``ce.md`` and ``figures/*.png`` to the output directory.

Usage::

    python tools/lpc_contrib_ce.py <run-dir> --out <dir> --abd <contrib.json>
        [--jobs 4] [--systems lorenz63 ...] [--replication]
    python tools/lpc_contrib_ce.py --figures-from <ce.json> --out <dir>
    python tools/lpc_contrib_ce.py --crossseed <ce.json> ... --out <file.md>

Figures are drawn from the written ``ce.json`` (read back), with the Agg
backend and no metadata, so ``--figures-from`` regenerates them byte for
byte. Refusals (exit 64, nothing written) are those of
``tools/lpc_contrib.py`` (confirmatory, non-development run, held-out seed
without ``--replication``, failed run, foreign dump), plus an A/D record of
another seed or run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import lpc_contrib as base  # noqa: E402
from lpcstudy import contribution as cb  # noqa: E402
from lpcstudy import joint_decisions as jd  # noqa: E402
from lpcstudy import mechanisms as me  # noqa: E402
from lpcstudy.ablation import CONDITIONS  # noqa: E402

fmt, ci, Refusal = base.fmt, base.ci, base.Refusal
SYSTEMS = ("lorenz63", "rossler", "chua")
TERCILES = ("low", "mid", "high")
FIGURE_DPI = 110


# ------------------------------------------------------------------ compute
def check_abd(abd: dict, run: Path, seed_id: str) -> None:
    """The A/D record must belong to the same run and seed."""
    if abd["run"]["seed_id"] != seed_id:
        raise Refusal(f"A/D record of {abd['run']['seed_id']}, run {seed_id}")
    if Path(abd["run"]["dir"]).resolve() != run.resolve():
        raise Refusal(f"A/D record of another run: {abd['run']['dir']}")


def b_link(abd_system: dict) -> dict:
    """E-H2a beside B and A: R x I, O x I (oracle, logit) and drop-I."""
    out = {}
    for hkey, kinds in abd_system["interactions"].items():
        pairs = kinds["oracle"].get("logit", {}).get("pairs", {})
        drop = abd_system["allocation"][hkey]["oracle"]["drop_one"]["I"]
        out[hkey] = {
            "RI": pairs.get("RI", {}).get("reading"),
            "OI": pairs.get("OI", {}).get("reading"),
            "drop_I_mse": drop["mse_ratio"].get("reading"),
            "drop_I_mse_reason": drop["mse_ratio"].get("reason"),
            "drop_I_L_w_ratio": drop["L_w_ratio"].get("ratio"),
        }
    return out


def g_reproduction(joint: dict, abd_system: dict) -> dict:
    """Largest |value here - value of the A/D record| per profile.

    ``MSE`` of the refit ``A/ROIN`` and ``L_w`` of the refit ``W/ROIN``
    (the same jobs and seed as WU-0048, so 0 is expected).
    """
    out = {}
    for kind, by_h in joint["checks"]["g_mse"].items():
        out[kind] = max(
            abs(v - abd_system["allocation"][h][kind]["subsets"]["ROIN"]["mse"])
            for h, v in by_h.items()
        )
    for kind, by_h in joint["checks"]["gw_L_w"].items():
        out[f"{kind}_L_w"] = max(
            abs(v - abd_system["allocation"][h][kind]["subsets"]["ROIN"]["L_w"])
            for h, v in by_h.items()
        )
    return out


def analyze(args, results: dict, datas: dict, dumps: dict, abd) -> dict:
    """Every block of every system; the seed-level E-H3c reading."""
    seed_id = results["provenance"]["seed_id"]
    config = results["config"]
    seed = int(config["seed"])
    n_resamples = int(config["bootstrap_resamples"])
    block = int(config["bootstrap_block"])
    record = {
        "label": cb.LABEL.format(seed_id=seed_id),
        "run": {
            "dir": str(args.run),
            "seed_id": seed_id,
            "commit": results["provenance"].get("commit"),
            "preset": results["provenance"].get("preset"),
        },
        "analysis": base.git_state(),
        "abd": (
            {"path": str(args.abd), "commit": abd["analysis"]["commit"]}
            if abd
            else None
        ),
        "systems": {},
    }
    for name in base.THREAD_VARS:
        os.environ[name] = "1"
    context = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(args.jobs, mp_context=context) as pool:

        def mapper(func, items):
            return pool.map(func, items, chunksize=2)

        for system, data in datas.items():
            start = time.time()
            arrays = dumps[system]
            index = cb.resample_indices(
                len(data.test["T"]),
                n_resamples,
                block,
                cb.bootstrap_generator(seed, data.system),
            )
            joint = jd.analyze_joint(
                data, arrays, cb.Learner(seed=seed), index, mapper=mapper
            )
            res = {
                "label": joint["label"],
                "checks": joint["checks"],
                "C2": joint["C2"],
                "C3": joint["C3"],
                "E_H2a": me.h2a_block(data, index),
                "E_H2e": me.h2e_block(data, arrays, seed, n_resamples, block),
                "E_H3c": me.h3c_block(
                    data, arrays, results["systems"][system], block
                ),
            }
            if abd is not None:
                abd_system = abd["systems"][system]
                res["C1"] = jd.c1_rows(abd_system)
                res["C2"]["shapley_rank"] = jd.shapley_rank_rows(abd_system)
                res["E_H2a"]["b_link"] = b_link(abd_system)
                res["checks"]["g_reproduces_abd_max_abs"] = g_reproduction(
                    joint, abd_system
                )
            res["seconds"] = time.time() - start
            record["systems"][system] = res
            print(f"{system}: {res['seconds']:.0f} s", file=sys.stderr)
    if set(SYSTEMS) <= set(record["systems"]):
        record["E_H3c_reading"] = me.h3c_reading(
            {s: record["systems"][s]["E_H3c"] for s in SYSTEMS}
        )
    return record


# ------------------------------------------------------------------ figures
def save_figure(fig, path: Path) -> None:
    """PNG with no software tag or timestamp (byte-identical reruns)."""
    fig.savefig(path, dpi=FIGURE_DPI, metadata={"Software": None})
    plt.close(fig)


def _series(values: list) -> np.ndarray:
    return np.array([np.nan if v is None else v for v in values], dtype=float)


def figure_h2a(system: str, block: dict, label: str):
    """Median m(H), w* drift and error correlation by I tercile."""
    fig_data = block["figure"]
    lt = block["steps_per_lt"]
    h = np.array(fig_data["H"], dtype=float) / lt
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.4))
    panels = (
        ("median_m", "m(H) (kept entries)"),
        ("median_drift", "w*(H) - w*(1 LT) (kept entries)"),
        ("median_corr", "C / sqrt(E_C E_P) (all states)"),
    )
    for ax, (key, title) in zip(axes, panels):
        for g, name in enumerate(TERCILES):
            ax.plot(h, _series(fig_data[key][g]), label=f"I {name}")
        ax.axvline(1.0, color="0.6", lw=0.8)
        ax.set_xscale("log")
        ax.set_xlabel("H (Lyapunov times)")
        ax.set_title(title, fontsize=8)
    axes[0].legend(fontsize=7)
    fig.suptitle(
        f"{label}\nE-H2a, {system}: median by tercile of I", fontsize=8
    )
    fig.tight_layout()
    return fig


def figure_h2e(system: str, block: dict, label: str):
    """Delta corr against Delta R per noise level (zero-variance marked)."""
    levels = block["levels"]
    fig, axes = plt.subplots(1, len(levels), figsize=(4.2 * len(levels), 3.4))
    axes = np.atleast_1d(axes)
    for ax, (rho, lev) in zip(axes, levels.items()):
        f = lev["figure"]
        dr, dc = np.array(f["delta_R"]), np.array(f["delta_corr"])
        zero = np.array(f["zero_at_smallest"], dtype=bool)
        lo, hi = block["library_ends"]
        ax.scatter(dr[~zero], dc[~zero], s=4, label=f"corr defined at {lo}")
        ax.scatter(dr[zero], dc[zero], s=4, label=f"corr = 0 at {lo} (conv.)")
        ax.axhline(0.0, color="0.6", lw=0.8)
        ax.set_xlabel(f"Delta R (N_lib {lo} -> {hi})")
        ax.set_ylabel(f"Delta corr (N_lib {lo} -> {hi})")
        ax.set_title(f"rho = {rho}: {lev['reading']}", fontsize=8)
    axes[0].legend(fontsize=7)
    fig.suptitle(f"{label}\nE-H2e, {system}", fontsize=8)
    fig.tight_layout()
    return fig


def figure_h3c(system: str, block: dict, label: str):
    """Cumulative share of |A5 - A4|; deployable marginals with top states."""
    f = block["figure"]
    fig, axes = plt.subplots(1, 5, figsize=(15, 3.2))
    share = np.array(f["cumulative_share"])
    frac = np.arange(1, len(share) + 1) / f["n_states"]
    axes[0].plot(frac, share)
    axes[0].axvline(me.TOP_SHARE, color="0.6", lw=0.8)
    axes[0].set_xscale("log")
    axes[0].set_xlabel("top fraction of states")
    axes[0].set_title("share of sum |A5 - A4| at H_ref", fontsize=8)
    for ax, name in zip(axes[1:], CONDITIONS):
        hist = f["histograms"][name]
        edges = np.array(hist["edges"])
        ax.stairs(np.array(hist["counts"]), edges, fill=True, alpha=0.6)
        top = np.array(hist["top_states"])
        ax.plot(top, np.zeros_like(top), "|", color="C3", ms=12)
        ax.set_title(
            f"{name} (deployable; top-1% |d| oracle in red)", fontsize=7
        )
    fig.suptitle(f"{label}\nE-H3c, {system}", fontsize=8)
    fig.tight_layout()
    return fig


def figure_c3(record: dict, label: str):
    """Mean trusted horizon against the false-trust rate, per policy."""
    systems = list(record["systems"])
    fig, axes = plt.subplots(1, len(systems), figsize=(4.4 * len(systems), 3.6))
    axes = np.atleast_1d(axes)
    for ax, system in zip(axes, systems):
        pol = record["systems"][system]["C3"]["policies"]
        for k, (name, row) in enumerate(pol.items()):
            x, y = row["false_trust_realized"], row["mean_trusted_lt"]
            xl, xh = (v if v is not None else np.nan for v in x["ci"])
            yl, yh = (v if v is not None else np.nan for v in y["ci"])
            ax.errorbar(
                x["estimate"],
                y["estimate"],
                xerr=[[x["estimate"] - xl], [xh - x["estimate"]]],
                yerr=[[y["estimate"] - yl], [yh - y["estimate"]]],
                fmt="o",
                color=f"C{k}",
                label=name,
            )
        ax.axvline(jd.TRUST_LEVEL, color="0.6", lw=0.8)
        ax.set_xlabel("false-trust rate P(T_realized <= q_0.1)")
        ax.set_ylabel("mean trusted horizon q_0.1 (LT)")
        ax.set_title(system, fontsize=8)
    axes[0].legend(fontsize=7)
    fig.suptitle(f"{label}\nC3, deployable chain (95% intervals)", fontsize=8)
    fig.tight_layout()
    return fig


def write_figures(record: dict, out: Path) -> dict[str, str]:
    """Draw every figure from a (JSON-loaded) record; return sha256 by name."""
    folder = out / "figures"
    folder.mkdir(parents=True, exist_ok=True)
    label = record["label"]
    made = {}
    for system, res in record["systems"].items():
        for name, fig in (
            (f"e_h2a_{system}.png", figure_h2a(system, res["E_H2a"], label)),
            (f"e_h2e_{system}.png", figure_h2e(system, res["E_H2e"], label)),
            (f"e_h3c_{system}.png", figure_h3c(system, res["E_H3c"], label)),
        ):
            save_figure(fig, folder / name)
            made[name] = None
    save_figure(figure_c3(record, label), folder / "c3_chain.png")
    made["c3_chain.png"] = None
    return {
        name: hashlib.sha256((folder / name).read_bytes()).hexdigest()
        for name in sorted(made)
    }


# ----------------------------------------------------------------- markdown
def rd(row: dict) -> str:
    """Estimate (or ratio) with its interval."""
    value = row.get("estimate", row.get("ratio", row.get("difference")))
    return f"{fmt(value)} {ci(row)}"


def reading(row: dict) -> str:
    return base.reading(row)


def markdown(record: dict) -> str:
    """The condensed tables of C and E for every system."""
    label = record["label"]
    lines = [
        f"# Phase J experiments C and E: {record['run']['seed_id']}",
        "",
        f"**{label}.** Run `{record['run']['dir']}`; analysis commit "
        f"`{record['analysis']['commit']}` (dirty: "
        f"{record['analysis']['dirty']}); A/D record "
        f"`{(record.get('abd') or {}).get('path')}`. Estimates with 95% "
        "intervals from the shared moving-block index sets (models fixed; "
        "training variance not included). Readings are descriptive; no "
        "causal claim; nothing here is set beside CONF-1.",
        "",
    ]
    for system, res in record["systems"].items():
        lines += [f"## {system}", ""]
        lines += _checks(res)
        if "C1" in res:
            lines += _c1(res)
        lines += _c2(res)
        lines += _c3(res)
        lines += _h2a(res)
        lines += _h2e(res)
        lines += _h3c(res)
    if "E_H3c_reading" in record:
        r = record["E_H3c_reading"]
        lines += [
            "## E-H3c reading (this seed)",
            "",
            "| item | value |",
            "|---|---|",
            f"| H3c interval widths | "
            + ", ".join(f"{s} {fmt(w)}" for s, w in r["widths"].items())
            + " |",
            f"| pattern (Lorenz-63 widest, Rössler narrowest) reproduced | "
            f"{r.get('pattern_reproduced')} |",
            f"| Lorenz-63 part (top-1% share of sum abs(d) "
            f"{fmt(r.get('lorenz63_tail_share'))}, median I percentile "
            f"{fmt(r.get('lorenz63_top_median_I_percentile'))}) | "
            f"{r.get('lorenz63_part')} |",
            f"| Rössler part (BC deployable: "
            + ", ".join(
                f"{k} {fmt(v)}"
                for k, v in r.get("rossler_bimodality", {}).items()
            )
            + f") | {r.get('rossler_part')} |",
            f"| **reading** | **{r['reading']}** |",
            "",
        ]
    return base.label_tables("\n".join(lines) + "\n", label)


def _checks(res: dict) -> list[str]:
    chk = res["checks"]
    cc = chk["crossing_counts"]
    return [
        "| check | result |",
        "|---|---|",
        "| A2 rebuilt on 1..H_max equals the dumped A2 (bitwise); A4 "
        f"horizon-free | {chk['a2_full_grid_equals_dump']}, "
        f"{chk['a4_horizon_free']} |",
        "| refit reproduces WU-0048 (max abs: A/ROIN MSE oracle, deployable;"
        " W/ROIN L_w oracle, deployable) | "
        + " / ".join(
            fmt(v, 2) for v in chk.get("g_reproduces_abd_max_abs", {}).values()
        )
        + " |",
        "| T_c counts T = 1 / e_(T-1) = theta (A2 train, g train, A2 test, "
        "g test, A4 calibration) | "
        + ", ".join(f"{a}/{b}" for a, b in cc.values())
        + " |",
        "| A2 on 1..H_max: pooled curvature floor / columns at 0 or 1 | "
        f"{chk['a2_full_grid_counts']['pooled_curvature_floor']} / "
        f"{chk['a2_full_grid_counts']['columns_at_0_or_1']} |",
        "| weights clipped to [0, 1] | "
        + ", ".join(f"{k} {v}" for k, v in chk["n_pred_clipped"].items())
        + " |",
        "",
    ]


def _c1(res: dict) -> list[str]:
    c1 = res["C1"]
    out = [
        "### C1. Separate performance (from the A/D record, no refit)",
        "",
        "Allocation: MSE per rule (oracle: moment form; deployable: realized); "
        "reading of the rung against F (MSE ratio, 1.05 table, n_eff guard). "
        "G(F) = 1 - L_A(F)/L_A(constant).",
        "",
        "| horizon | profile | constant | separation | RO | F (ROIN) | X | "
        "X+F | G(F) | sep vs F | RO vs F | X+F vs F |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for hkey, kinds in c1["allocation"].items():
        for kind, b in kinds.items():
            m, r = b["mse"], b["reading_vs_F"]
            out.append(
                f"| {b['horizon']} | {kind} | {fmt(m.get('none'))} | "
                f"{fmt(m.get('separation'))} | {fmt(m.get('RO'))} | "
                f"{fmt(m.get('ROIN'))} | {fmt(m.get('X'))} | "
                f"{fmt(m.get('X+F'))} | {fmt(b['G_F'])} | "
                f"{r.get('separation')} | {r.get('RO')} | {r.get('X+F')} |"
            )
    out += [
        "",
        "Horizon (Y = ln min(T_c, H_max)): pinball at 0.5 / Harrell's C / "
        "coverage of q_0.1 below the cap; reading against F.",
        "",
        "| profile | rung | pinball | C | cov q_0.1 | reading vs F |",
        "|---|---|---|---|---|---|",
    ]
    for kind, rows in c1["horizon"].items():
        for rung, r in rows.items():
            if rung == "lyapunov_rank_c":
                out.append(f"| {kind} | Lyapunov rank | | {fmt(r)} | | |")
                continue
            out.append(
                f"| {kind} | {rung} | {fmt(r['pinball'])} | "
                f"{fmt(r['c_index'])} | {fmt(r['coverage_0.1'])} | "
                f"{r['reading_vs_F'] or ''} |"
            )
    out.append("")
    return out


def _c2(res: dict) -> list[str]:
    c2 = res["C2"]
    out = [
        "### C2. Shared information (oracle and deployable profiles)",
        "",
        "Skill retained = [L(constant) - L(bottleneck)] / [L(constant) - "
        "L(F)]; reading: keeps most (CI > 0.5), loses most (CI < 0.5), else "
        "not determined. Forward: horizon from g (five clipped weights; g_w: "
        "the L_w fits); reverse: weight from h (three quantiles), scored by "
        "L_A (MSE; deployable: realized per draw, R2 guard) and by L_w "
        "(weight units, unit-weight fits). Training inputs cross-fitted.",
        "",
        "| profile | direction | horizon | full skill [CI] | retained L_A / "
        "pinball [CI] | reading | retained L_w [CI] | reading L_w |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for kind in ("oracle", "deployable"):
        fwd = c2[kind]["forward"]
        out.append(
            f"| {kind} | forward (g; g_w) | all five | {rd(fwd['full_skill'])} | "
            f"{rd(fwd['retained'])} | {fwd['retained']['reading']} | "
            f"{rd(fwd['retained_w'])} | {fwd['retained_w']['reading']} |"
        )
        for r in fwd["single_horizon"].values():
            out.append(
                f"| {kind} | forward, one weight | {r['horizon']} | | "
                f"{rd(r['retained'])} | {r['retained']['reading']} | | |"
            )
        for r in c2[kind]["reverse"].values():
            out.append(
                f"| {kind} | reverse | {r['horizon']} | {rd(r['full_skill'])} | "
                f"{rd(r['retained'])} | {r['retained']['reading']} | "
                f"{rd(r['retained_w'])} | {r['retained_w']['reading']} |"
            )
    out += [
        "",
        "| profile | forward C-index F / g / g_w | reverse MSE(h)/MSE(F) per "
        "horizon | math-spec prediction (both lose most) | largest "
        "single-weight retention at H |",
        "|---|---|---|---|---|",
    ]
    for kind in ("oracle", "deployable"):
        fwd, rev = c2[kind]["forward"], c2[kind]["reverse"]
        ci_text = " / ".join(fmt(fwd["c_index"][k]) for k in ("F", "g", "g_w"))
        ratios = "; ".join(
            f"{r['horizon']} {rd(r['mse_ratio_bottleneck_over_F'])} "
            f"{reading(r['mse_ratio_bottleneck_over_F'])}"
            for r in rev.values()
        )
        pc = c2[kind]["prediction_check"]
        out.append(
            f"| {kind} | {ci_text} | {ratios} | **{pc['reading']}** | "
            f"{pc['forward_single_largest_at']} |"
        )
    out += [
        "",
        "Oracle against deployable: retained (deployable) minus retained "
        "(oracle), paired 95% interval.",
        "",
        "| row | oracle | deployable | difference [CI] | reading |",
        "|---|---|---|---|---|",
    ]
    for key, r in c2["oracle_vs_deployable"].items():
        out.append(
            f"| {key} | {fmt(r['oracle'])} | {fmt(r['deployable'])} | "
            f"{fmt(r['difference'])} {ci(r)} | {r['reading']} |"
        )
    out.append("")
    if "shapley_rank" in c2:
        out += [
            "| horizon | Spearman(phi allocation, phi horizon) (4 items, "
            "descriptive) | phi_alloc R/O/I/N | phi_horizon R/O/I/N |",
            "|---|---|---|---|",
        ]
        for r in c2["shapley_rank"].values():
            pa = "/".join(fmt(v, 2) for v in r["phi_allocation"].values())
            ph = "/".join(fmt(v, 2) for v in r["phi_horizon"].values())
            out.append(
                f"| {r['horizon']} | {fmt(r['spearman'])} | {pa} | {ph} |"
            )
        out.append("")
    return out


def _c3(res: dict) -> list[str]:
    c3 = res["C3"]
    pol = c3["policies"]
    names = list(pol)
    hkeys = list(next(iter(pol.values()))["mse"])
    out = [
        "### C3. The deployable chain",
        "",
        "False trust = P(T <= q_0.1) per (state, draw), target 0.1; T "
        "realized (the run's first passage against the noisy truth) or "
        "characteristic (moments). Trusted horizon = mean q_0.1 (LT). "
        "A4 + KM leaf uses the calibration A4 hybrid's characteristic horizon "
        "(no per-draw calibration errors on the full grid).",
        "",
        "| policy | false trust realized [CI] | false trust characteristic "
        "[CI] | mean trusted (LT) [CI] | q at cap |",
        "|---|---|---|---|---|",
    ]
    for name in names:
        r = pol[name]
        out.append(
            f"| {name} | {rd(r['false_trust_realized'])} | "
            f"{rd(r['false_trust_characteristic'])} | "
            f"{rd(r['mean_trusted_lt'])} | {r['n_q_at_cap']} |"
        )
    out += [
        "",
        "Hybrid MSE ratio to A2 (realized per draw; 1.05 table, R2 guard).",
        "",
        "| policy | "
        + " | ".join(pol[names[0]]["mse"][h]["horizon"] for h in hkeys)
        + " |",
        "|---|" + "---|" * len(hkeys),
    ]
    for name in ("A4 + KM leaf", "g(F-hat) + h(F-hat)"):
        cells = []
        for h in hkeys:
            row = pol[name]["mse"][h]["ratio_to_A2"]
            cells.append(f"{rd(row)} {reading(row)}")
        out.append(f"| {name} | " + " | ".join(cells) + " |")
    out += [
        "",
        "| full system minus | false trust realized [CI] | false trust "
        "characteristic [CI] | trusted LT [CI] |",
        "|---|---|---|---|",
    ]
    for name, r in c3["full_minus_comparator"].items():
        out.append(
            f"| {name} | {rd(r['false_trust_realized'])} | "
            f"{rd(r['false_trust_characteristic'])} | {rd(r['trusted_lt'])} |"
        )
    out += [
        "",
        "| horizon model (own characteristic target) | pinball / constant's |"
        " constant/model ratio [CI] reading | cov 0.1 / 0.5 / 0.9 | C |",
        "|---|---|---|---|---|",
    ]
    for name, r in c3["horizon_models"].items():
        row = r["pinball_ratio_constant_over_model"]
        cov = " / ".join(
            fmt(r["coverage"][t]["coverage_below_cap"])
            for t in ("0.1", "0.5", "0.9")
        )
        out.append(
            f"| {name} | {fmt(r['pinball'])} / {fmt(r['pinball_constant'])} | "
            f"{rd(row)} {reading(row)} | {cov} | {fmt(r.get('c_index'))} |"
        )
    out.append("")
    return out


def _h2a(res: dict) -> list[str]:
    b = res["E_H2a"]
    link = b.get("b_link", {})
    out = [
        "### E-H2a. Amplification mismatch m(H) (H_0 = 1 LT; both r.m.s. <= "
        "0.5 sigma_x)",
        "",
        "Medians by tercile of I (low / mid / high). Spearman(m, I) on the kept "
        "states [95%]. B and A columns from the A/D record (oracle).",
        "",
        "| horizon | kept | m | abs drift w* | corr C/sqrt(E_C E_P) | "
        "Spearman(m, I) | B RI / OI | A drop-I (MSE) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for h, r in b["by_horizon"].items():
        trio = lambda v: " / ".join(fmt(x, 2) for x in v)  # noqa: E731
        sp = rd(r["spearman_m_I"]) if "spearman_m_I" in r else "(H_0)"
        lk = link.get(h, {})
        out.append(
            f"| {r['horizon']} | {r['n_kept']} | {trio(r['median_m_by_tercile'])}"
            f" | {trio(r['median_abs_drift_by_tercile'])} | "
            f"{trio(r['median_corr_by_tercile'])} | {sp} | "
            f"{lk.get('RI')} / {lk.get('OI')} | {lk.get('drop_I_mse')}"
            + (
                f" ({lk['drop_I_mse_reason']})"
                if lk.get("drop_I_mse_reason")
                else ""
            )
            + " |"
        )
    out += [
        "",
        f"**Reading: {b['reading']['reading']}** ({_detail(b['reading'])}).",
        "",
    ]
    return out


def _detail(reading_record: dict) -> str:
    return ", ".join(
        f"{k}: {v}" for k, v in reading_record.items() if k != "reading"
    )


def _h2e(res: dict) -> list[str]:
    b = res["E_H2e"]
    out = [
        "### E-H2e. Library size and error correlation (sweep states)",
        "",
        f"{b['n_sweep_states']} sweep states. Delta = value at N_lib "
        f"{b['library_ends'][1]} minus {b['library_ends'][0]}. corr = the H2e "
        "correlation (0 by convention where an error is "
        "constant over the draws).",
        "",
        "| rho | valid | corr 0 small / large lib | median corr small -> large"
        " | set | "
        "median Delta corr [CI] | Spearman(Delta corr, Delta R) [CI] | "
        "reading |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for rho, lev in b["levels"].items():
        for part, p in lev["parts"].items():
            out.append(
                f"| {rho} | {lev['n_valid']} | {lev['n_corr_zero_smallest']} / "
                f"{lev['n_corr_zero_largest']} | {fmt(lev['median_corr']['smallest'])}"
                f" -> {fmt(lev['median_corr']['largest'])} | {part} "
                f"({p['median_delta_corr']['n_states']}) | "
                f"{rd(p['median_delta_corr'])} | "
                f"{rd(p['spearman_delta_corr_delta_R'])} | {p['reading']} |"
            )
    out += [
        "",
        "| rho | stratifier | median Delta corr low / mid / high | median "
        "Delta R low / mid / high |",
        "|---|---|---|---|",
    ]
    for rho, lev in b["levels"].items():
        for name, s in lev["by_tercile"].items():
            out.append(
                f"| {rho} | {name} | "
                + " / ".join(fmt(v, 2) for v in s["median_delta_corr"])
                + " | "
                + " / ".join(fmt(v, 2) for v in s["median_delta_R"])
                + " |"
            )
    out += [
        "",
        "**Reading** (final, after the convention check): "
        + "; ".join(
            f"rho {rho}: {lev['reading']}" for rho, lev in b["levels"].items()
        )
        + ".",
        "",
    ]
    return out


def _h3c(res: dict) -> list[str]:
    b = res["E_H3c"]
    h = b["H3c"]
    top = b["top_abs_difference"]
    bc_o = {
        k: v["bimodality_coefficient"] for k, v in b["marginals_oracle"].items()
    }
    bc_d = {
        k: v["bimodality_coefficient"]
        for k, v in b["marginals_deployable"].items()
    }
    out = [
        "### E-H3c. A5 against A4",
        "",
        "| item | value |",
        "|---|---|",
        f"| H3c ratio MSE(A5)/MSE(A4) [CI at level {fmt(h['level'])}] (run) | "
        f"{fmt(h['ratio'])} [{fmt(h['ci'][0])}, {fmt(h['ci'][1])}], width "
        f"{fmt(h['width'])} |",
        f"| top-1% share: A5 loss / A4 loss / abs(A5 - A4) | "
        f"{fmt(b['tail_share']['A5'])} / {fmt(b['tail_share']['A4'])} / "
        f"{fmt(b['tail_share']['abs_difference'])} |",
        f"| autocorrelation of d = A5 - A4, lags 1..5 | "
        + ", ".join(fmt(v, 2) for v in b["autocorrelation_difference"])
        + " |",
        f"| block-{b['block_means']['block']} means: lag-1 autocorrelation, "
        f"variance ratio | {fmt(b['block_means']['lag1_autocorrelation'])}, "
        f"{fmt(b['block_means']['variance_ratio'])} |",
        f"| K chosen; leaves used test / calibration; largest leaf share test |"
        f" {b['chosen_K']}; {b['occupancy_test']['n_leaves_used']} / "
        f"{b['occupancy_calibration']['n_leaves_used']}; "
        f"{fmt(b['occupancy_test']['largest_share'])} |",
        f"| w*(H_ref) within-leaf share of variance | "
        f"{fmt(b['w_star_variance_by_leaf']['within_share'])} |",
        "| bimodality coefficient R/O/I/N, oracle; deployable | "
        + "/".join(fmt(v, 2) for v in bc_o.values())
        + "; "
        + "/".join(fmt(v, 2) for v in bc_d.values())
        + " |",
        "| Spearman pairs (oracle) | "
        + ", ".join(f"{k} {fmt(v, 2)}" for k, v in b["spearman_oracle"].items())
        + " |",
        f"| top-1% abs(d) states: mean percentile R/O/I/N | "
        + "/".join(fmt(v, 2) for v in top["mean_percentile"].values())
        + " |",
        f"| top-1% abs(d) states: median I pct; share high-I; median abs(x) "
        f"pct; share sign change in window; share of sum d | "
        f"{fmt(top['median_I_percentile'])}; "
        f"{fmt(top['share_high_I_tercile'])}; "
        f"{fmt(top['median_abs_x_percentile'])}; "
        f"{fmt(top['share_sign_change_in_window'])}; "
        f"{fmt(top['share_of_signed_difference'])} |",
        "",
    ]
    return out


# ---------------------------------------------------------------- crossseed
def crossseed(records: list[dict]) -> str:
    """Readings and headline numbers side by side, one column per seed."""
    seeds = [r["run"]["seed_id"] for r in records]
    label = (
        "DEVELOPMENT ("
        + ", ".join(seeds)
        + "): exploratory, not a hypothesis test"
    )
    head = "| system | item | " + " | ".join(seeds) + " |"
    rule = "|---|---|" + "---|" * len(seeds)
    lines = [
        f"# Phase J experiments C and E: {', '.join(seeds)} side by side",
        "",
        f"**{label}.** One column per seed; no pooling and no new statistic. "
        "Every cell is copied from that seed's ce.json.",
        "",
        head,
        rule,
    ]

    def row(system: str, item: str, get) -> None:
        cells = []
        for r in records:
            try:
                cells.append(get(r["systems"][system]))
            except (KeyError, TypeError, IndexError):
                cells.append("-")
        lines.append(f"| {system} | {item} | " + " | ".join(cells) + " |")

    for system in SYSTEMS:
        row(
            system,
            "C1 G(F) oracle, 1 LT",
            lambda s: fmt(s["C1"]["allocation"]["30"]["oracle"]["G_F"]),
        )
        row(
            system,
            "C1 F pinball / C, oracle",
            lambda s: f"{fmt(s['C1']['horizon']['oracle']['ROIN']['pinball'])} / {fmt(s['C1']['horizon']['oracle']['ROIN']['c_index'])}",
        )
        for kind in ("oracle", "deployable"):
            k = kind[:3]
            row(
                system,
                f"C2 {k} forward retained",
                lambda s, k=kind: f"{rd(s['C2'][k]['forward']['retained'])} {s['C2'][k]['forward']['retained']['reading']}",
            )
            row(
                system,
                f"C2 {k} forward retained L_w (g_w)",
                lambda s, k=kind: f"{rd(s['C2'][k]['forward']['retained_w'])} {s['C2'][k]['forward']['retained_w']['reading']}",
            )
            for h in ("8", "30", "120"):
                row(
                    system,
                    f"C2 {k} reverse retained L_A, H={h}",
                    lambda s, h=h, k=kind: f"{rd(s['C2'][k]['reverse'][h]['retained'])} {s['C2'][k]['reverse'][h]['retained']['reading']}",
                )
                row(
                    system,
                    f"C2 {k} reverse retained L_w, H={h}",
                    lambda s, h=h, k=kind: f"{rd(s['C2'][k]['reverse'][h]['retained_w'])} {s['C2'][k]['reverse'][h]['retained_w']['reading']}",
                )
            row(
                system,
                f"C2 {k} prediction (both lose most)",
                lambda s, k=kind: s["C2"][k]["prediction_check"]["reading"],
            )
        for key in ("forward", "forward_w", "reverse/30", "reverse_w/30"):
            row(
                system,
                f"C2 dep - ora retained, {key}",
                lambda s, key=key: f"{fmt(s['C2']['oracle_vs_deployable'][key]['difference'])} {ci(s['C2']['oracle_vs_deployable'][key])} {s['C2']['oracle_vs_deployable'][key]['reading']}",
            )
        row(
            system,
            "C2 Spearman(phi), 1 LT",
            lambda s: fmt(s["C2"]["shapley_rank"]["30"]["spearman"]),
        )
        for name in (
            "A2 + constant",
            "A2 + h(F-hat)",
            "A4 + KM leaf",
            "g(F-hat) + h(F-hat)",
        ):
            row(
                system,
                f"C3 false trust realized: {name}",
                lambda s, n=name: rd(
                    s["C3"]["policies"][n]["false_trust_realized"]
                ),
            )
            row(
                system,
                f"C3 trusted LT: {name}",
                lambda s, n=name: rd(s["C3"]["policies"][n]["mean_trusted_lt"]),
            )
        row(
            system,
            "C3 MSE g / A2 at 1 LT",
            lambda s: f"{rd(s['C3']['policies']['g(F-hat) + h(F-hat)']['mse']['30']['ratio_to_A2'])} {reading(s['C3']['policies']['g(F-hat) + h(F-hat)']['mse']['30']['ratio_to_A2'])}",
        )
        row(system, "E-H2a reading", lambda s: s["E_H2a"]["reading"]["reading"])
        row(
            system,
            "E-H2a Spearman(m, I) at 2 LT",
            lambda s: rd(s["E_H2a"]["by_horizon"]["60"]["spearman_m_I"]),
        )
        for rho in ("0.01", "0.02"):
            row(
                system,
                f"E-H2e reading rho {rho}",
                lambda s, r=rho: s["E_H2e"]["levels"][r]["reading"],
            )
            row(
                system,
                f"E-H2e Spearman all, rho {rho}",
                lambda s, r=rho: rd(
                    s["E_H2e"]["levels"][r]["parts"]["all"][
                        "spearman_delta_corr_delta_R"
                    ]
                ),
            )
        row(
            system,
            "E-H3c ratio [CI]",
            lambda s: f"{fmt(s['E_H3c']['H3c']['ratio'])} [{fmt(s['E_H3c']['H3c']['ci'][0])}, {fmt(s['E_H3c']['H3c']['ci'][1])}]",
        )
        row(
            system,
            "E-H3c top-1% share abs(d)",
            lambda s: fmt(s["E_H3c"]["tail_share"]["abs_difference"]),
        )
    lines += ["", head, rule]
    cells = [r.get("E_H3c_reading", {}).get("reading", "-") for r in records]
    lines.append("| all | E-H3c reading | " + " | ".join(cells) + " |")
    lines.append("")
    return base.label_tables("\n".join(lines) + "\n", label)


# ------------------------------------------------------------------- main
def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if any("confirmatory" in a.lower() for a in argv):
        print("lpc_contrib_ce: refused: confirmatory", file=sys.stderr)
        return 64
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("run", type=Path, nargs="?")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--abd", type=Path)
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--systems", nargs="*")
    parser.add_argument("--replication", action="store_true")
    parser.add_argument("--figures-from", type=Path)
    parser.add_argument("--crossseed", type=Path, nargs="+")
    args = parser.parse_args(argv)
    if args.figures_from is not None:
        record = json.loads(args.figures_from.read_text())
        digests = write_figures(record, args.out)
        print(json.dumps(digests, indent=1))
        return 0
    if args.crossseed is not None:
        records = [json.loads(p.read_text()) for p in args.crossseed]
        args.out.write_text(crossseed(records))
        return 0
    if args.run is None:
        parser.error("a run directory is required")
    try:
        results = base.check_run(args.run, args.replication)
        seed_id = results["provenance"]["seed_id"]
        systems = args.systems or list(results["systems"])
        dumps = {
            s: base.load_dump(args.run / "states" / f"{s}.npz", seed_id)
            for s in systems
        }
        datas = {s: cb.SystemData.from_arrays(a) for s, a in dumps.items()}
        abd = None
        if args.abd is not None:
            abd = json.loads(args.abd.read_text())
            check_abd(abd, args.run, seed_id)
    except (Refusal, ValueError, FileNotFoundError) as err:
        print(f"lpc_contrib_ce: refused: {err}", file=sys.stderr)
        return 64
    record = analyze(args, results, datas, dumps, abd)
    args.out.mkdir(parents=True, exist_ok=True)
    text = json.dumps(base.to_json(record), indent=1, allow_nan=False) + "\n"
    (args.out / "ce.json").write_text(text)
    loaded = json.loads(text)
    (args.out / "ce.md").write_text(markdown(loaded))
    digests = write_figures(loaded, args.out)
    (args.out / "figures.sha256.json").write_text(
        json.dumps(digests, indent=1) + "\n"
    )
    print(f"wrote {args.out}/ce.json, ce.md, figures/", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
