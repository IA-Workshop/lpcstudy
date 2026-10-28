"""Presentation figures of the phase J confirmatory round (CONF-5 to CONF-9).

Plots values already stored in the round's records and computes no statistic:
no pooling across seeds, no new interval, no new reading. Each claim row is
found by the frozen lookup of ``tools/lpc_confirm.py`` (``find_row`` on
``lpc_replicate.seed_rows``), and the point, interval and level are read from
the node that holds the stored reading. Every plotted reading is checked
against ``confirm/confirm.json``; a mismatch refuses.

Usage::

    python tools/phasej_figures.py promoted/phase-J --out <dir>

Figures (PNG):

- ``F1_horizon_ablation``: drop-one ablation of the horizon forecast, all four
  conditions, both profiles, three systems (J-H1, J-H2, J-H3; R for context).
- ``F2_allocation_ablation``: drop-one ablation of the allocation at 1 LT
  (J-A1; the other rows for context).
- ``F3_horizon_claims``: J-H4, J-H5, J-H6.
- ``F4_allocation_claims``: J-A2, J-A3, J-A4, J-I1, J-C2.
- ``F5_reading_grid``: every claim row's stored reading on every seed, with
  its verdict.
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lpc_confirm as lc  # noqa: E402
import lpc_replicate as rep  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CLAIMS = ROOT / "docs/study/preregistration_phase_j/claims.json"
SEEDS = ("CONF-5", "CONF-6", "CONF-7", "CONF-8", "CONF-9")
SYSTEMS = ("lorenz63", "rossler", "chua")
NAMES = {"lorenz63": "Lorenz-63", "rossler": "Rössler", "chua": "Chua"}
PROFILES = ("oracle", "deployable")
CONDITIONS = ("R", "O", "I", "N")
CONDITION_NAMES = {
    "R": "recurrence",
    "O": "separation",
    "I": "instability",
    "N": "noise",
}
COLORS = ("#0072B2", "#E69F00", "#009E73", "#CC79A7", "#D55E00")
"""Okabe-Ito colors, one per seed."""
OFFSETS = (-0.24, -0.12, 0.0, 0.12, 0.24)
LABEL = (
    "PHASE J CONFIRMATORY (CONF-5 to CONF-9): stored pre-registered results; "
    "each seed shown separately, not pooled"
)
FOOTER = (
    "Presentation figure made after the freeze from the stored records "
    "(promoted/phase-J); it computes no statistic. Filled marker: the seed's "
    "stored reading implies the claim. Hollow: it does not (for context rows "
    "without a claim: the reading is undetermined). Bars: the row's stored "
    "interval at its stored level."
)
POINT_KEYS = ("ratio", "difference", "delta_r2", "estimate")
SOURCE_FILES = {"pipeline results.json": "results", "ce.json": "ce"}


class Refusal(Exception):
    """A stored record disagrees with what the figure would show."""


# ------------------------------------------------------------------ records
def load(folder: Path) -> tuple[list[dict], dict, dict]:
    """The five seeds' records, ``confirm.json`` and the claim table."""
    seeds = []
    for seed in SEEDS:
        d = folder / seed
        rec = {
            name: json.loads((d / f"{name}.json").read_text())
            for name in ("contrib", "ce", "results")
        }
        rec["rows"] = rep.seed_rows(rec["contrib"], rec["ce"])
        seeds.append(rec)
    confirm = json.loads((folder / "confirm/confirm.json").read_text())
    if [str(i["seed_id"]) for i in confirm["inputs"]] != list(SEEDS):
        raise Refusal("confirm.json: seeds differ from CONF-5 to CONF-9")
    return seeds, confirm, json.loads(CLAIMS.read_text())


def walk(node, path: str):
    for part in path.strip("/").split("/"):
        node = node[part]
    return node


def stored(seed: dict, spec: dict) -> dict:
    """Point, interval, level and reading of one claim row on one seed."""
    if "source" in spec:
        node = walk(seed[SOURCE_FILES[spec["source"]]], spec["path"])
        reading = node.get("reading")
    else:
        found = lc.find_row(seed["rows"], spec, "phasej_figures")
        source, path = found.path.split("/", 1)
        node = walk(seed[source], path.rsplit("/", 1)[0])
        reading = found.word
    return value(node, reading)


def value(node: dict, reading: str | None) -> dict:
    point = next((node[k] for k in POINT_KEYS if k in node), None)
    if point is None:
        raise Refusal(f"no point value among {sorted(node)}")
    return {
        "point": point,
        "ci": node["ci"],
        "level": node.get("level"),
        "reading": reading,
        "reason": node.get("reason"),
    }


def claim_rows(table: dict, confirm: dict, seeds: list[dict]) -> list[dict]:
    """Every claim row with its stored values, checked against confirm.json."""
    out = []
    by_key = {
        (r["claim_id"], r["system"], r["profile"], r["item"]): r
        for r in confirm["rows"]
    }
    for claim in table["claims"]:
        for spec in claim["rows"]:
            key = (claim["id"], spec["system"], spec["profile"], spec["item"])
            row = by_key[key]
            values = [stored(s, spec) for s in seeds]
            words = [v["reading"] for v in values]
            if "source" in spec:
                words = row["readings"]  # J-C2 is read from its interval
            if words != row["readings"]:
                raise Refusal(f"{key}: readings {words} != {row['readings']}")
            out.append(
                {
                    **row,
                    "statement": claim["statement"],
                    "values": values,
                }
            )
    return out


def find(rows: list[dict], claim_id: str, **match) -> list[dict]:
    return [
        r
        for r in rows
        if r["claim_id"] == claim_id
        and all(r[k] == v for k, v in match.items())
    ]


# ----------------------------------------------------------------- drawing
def seed_points(ax, x: float, values: list[dict], implying, faded=False):
    """Five seeds at ``x``, each with its interval; filled if implying."""
    for i, (v, imp) in enumerate(zip(values, implying)):
        lo, hi = v["ci"]
        xi = x + OFFSETS[i]
        alpha = 0.45 if faded else 1.0
        if lo is not None and hi is not None:
            ax.plot([xi, xi], [lo, hi], color=COLORS[i], lw=1.4, alpha=alpha)
        ax.plot(
            xi,
            v["point"],
            "o",
            ms=5.5,
            color=COLORS[i],
            mfc=COLORS[i] if imp else "white",
            mew=1.4,
            alpha=alpha,
        )


def reference(ax, y: float, style: str = "-", label: str | None = None):
    """A reference line, kept inside the plotted range."""
    ax.axhline(y, color="0.35", lw=0.9, ls=style, zorder=0)
    ax.plot([0], [y], alpha=0)  # include the line in autoscaling


def seed_legend(fig, y: float = 0.955):
    handles = [
        Line2D([], [], marker="o", ls="", color=c, mfc=c, label=s)
        for s, c in zip(SEEDS, COLORS)
    ]
    handles += [
        Line2D([], [], marker="o", ls="", color="0.3", mfc="0.3",
               label="implies the claim"),
        Line2D([], [], marker="o", ls="", color="0.3", mfc="white",
               label="does not"),
        Line2D([], [], color="0.35", lw=0.9, ls="-",
               label="no change (ratio 1, difference 0)"),
        Line2D([], [], color="0.35", lw=0.9, ls="--",
               label="5% margin or 10% target"),
    ]
    fig.legend(
        handles=handles, loc="upper center", ncol=9, fontsize=8,
        frameon=False, bbox_to_anchor=(0.5, y),
    )


def frame(fig, title: str, footer: str = FOOTER):
    fig.suptitle(f"{LABEL}\n{title}", fontsize=9.5, y=0.995)
    fig.text(0.5, 0.005, footer, ha="center", va="bottom", fontsize=7,
             color="0.3", wrap=True)


def verdict_text(row: dict) -> str:
    return f"{row['claim_id']} {row['verdict']}\n({row['n_implying']} of 5 seeds)"


def level_text(values: list[dict]) -> str:
    levels = {v["level"] for v in values}
    if len(levels) != 1 or None in levels:
        return "level as stored"
    return f"{100 * levels.pop():.4g}% intervals"


# ----------------------------------------------------------------- figures
def horizon_ablation(seeds, rows, out: Path) -> Path:
    """F1: drop-one ablation of the horizon forecast."""
    claimed = {"I": "J-H1", "O": "J-H2", "N": "J-H3"}
    fig, axes = plt.subplots(2, 3, figsize=(13, 7.6), sharey=True)
    for c, system in enumerate(SYSTEMS):
        for r, profile in enumerate(PROFILES):
            ax = axes[r, c]
            values, ticks = [], {}
            for j, cond in enumerate(CONDITIONS):
                if cond in claimed:
                    (row,) = find(rows, claimed[cond], system=system,
                                  profile=profile)
                    vals, imp, faded = row["values"], row["implying"], False
                    ticks[cond] = verdict_text(row)
                else:
                    path = (
                        f"systems/{system}/horizon/{profile}/drop_one/"
                        f"{cond}/pinball_ratio"
                    )
                    nodes = [walk(s["contrib"], path) for s in seeds]
                    vals = [value(n, n["reading"]) for n in nodes]
                    imp = [v["reading"] != "undetermined" for v in vals]
                    faded = True
                seed_points(ax, j, vals, imp, faded)
                values += vals
            reference(ax, 1.0, "-")
            reference(ax, 1.05, "--")
            ax.set_xticks(range(4))
            ax.set_xticklabels(
                [
                    f"drop {k}\n{CONDITION_NAMES[k]}\n"
                    + ticks.get(k, "(no claim)")
                    for k in CONDITIONS
                ],
                fontsize=7.5,
            )
            ax.set_xlim(-0.6, 3.6)
            ax.set_title(
                f"{NAMES[system]}, {profile} profile ({level_text(values)})",
                fontsize=9,
            )
            ax.grid(axis="y", color="0.9")
            if c == 0:
                ax.set_ylabel(
                    "horizon loss without the condition\n"
                    "÷ loss with all four (pinball)",
                    fontsize=8.5,
                )
    seed_legend(fig, 0.935)
    frame(
        fig,
        "Ablation of the horizon forecast: what happens to the loss of "
        "predicting the forecast horizon when one condition is removed "
        "(above 1: the condition helps)",
    )
    fig.tight_layout(rect=(0, 0.04, 1, 0.9))
    return save(fig, out, "F1_horizon_ablation")


def allocation_ablation(seeds, rows, out: Path) -> Path:
    """F2: drop-one ablation of the allocation at 1 LT."""
    fig, axes = plt.subplots(2, 3, figsize=(13, 7.6), sharey=True)
    for c, system in enumerate(SYSTEMS):
        for r, profile in enumerate(PROFILES):
            ax = axes[r, c]
            values, ticks = [], {}
            for j, cond in enumerate(CONDITIONS):
                row = None
                if (system, profile, cond) == ("rossler", "oracle", "R"):
                    (row,) = find(rows, "J-A1")
                if row:
                    vals, imp, faded = row["values"], row["implying"], False
                    ticks[cond] = verdict_text(row)
                else:
                    path = (
                        f"systems/{system}/allocation/30/{profile}/drop_one/"
                        f"{cond}/mse_ratio"
                    )
                    nodes = [walk(s["contrib"], path) for s in seeds]
                    vals = [value(n, n["reading"]) for n in nodes]
                    imp = [v["reading"] != "undetermined" for v in vals]
                    faded = True
                seed_points(ax, j, vals, imp, faded)
                values += vals
            reference(ax, 1.0, "-")
            reference(ax, 1.05, "--")
            ax.set_xticks(range(4))
            ax.set_xticklabels(
                [
                    f"drop {k}\n{CONDITION_NAMES[k]}\n"
                    + ticks.get(k, "(no claim)")
                    for k in CONDITIONS
                ],
                fontsize=7.5,
            )
            ax.set_xlim(-0.6, 3.6)
            ax.set_title(
                f"{NAMES[system]}, {profile} profile ({level_text(values)})",
                fontsize=9,
            )
            ax.grid(axis="y", color="0.9")
            if c == 0:
                ax.set_ylabel(
                    "blend MSE without the condition\n÷ MSE with all four",
                    fontsize=8.5,
                )
    seed_legend(fig, 0.935)
    frame(
        fig,
        "Ablation of the allocation at 1 Lyapunov time: what happens to the "
        "error of the CP-PLP blend when one condition is removed "
        "(above 1: the condition helps)\n"
        "Only Rössler oracle drop R is a claim (J-A1); faded points are "
        "context. Below 2 LT, Lorenz-63 and Chua are mostly unreadable "
        "(pre-registration §8 item 3)",
    )
    fig.tight_layout(rect=(0, 0.04, 1, 0.9))
    return save(fig, out, "F2_allocation_ablation")


def claim_panel(ax, group: list[dict], ylabel: str, lines: list[tuple]):
    """One claim's rows as groups of five seeds, with its reference lines."""
    values = []
    for j, row in enumerate(group):
        seed_points(ax, j, row["values"], row["implying"])
        values += row["values"]
    for y, style, label in lines:
        reference(ax, y, style, label)
    ax.set_xticks(range(len(group)))
    ax.set_xticklabels(
        [
            f"{NAMES[r['system']]}\n{r['profile']}\n{r['verdict']}\n"
            f"({r['n_implying']} of 5)"
            for r in group
        ],
        fontsize=7.3,
    )
    ax.set_xlim(-0.6, len(group) - 0.4)
    ax.set_ylabel(ylabel, fontsize=8)
    ax.grid(axis="y", color="0.9")
    return level_text(values)


def title(ax, row: dict, level: str):
    ax.set_title(
        f"{row['claim_id']} (claim {row['claim']}, {level})\n"
        + textwrap.fill(row["statement"], 52),
        fontsize=8.3,
    )


def horizon_claims(rows, out: Path) -> Path:
    """F3: J-H4, J-H5, J-H6."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.4))
    spec = (
        ("J-H4", "interaction Δ: loss of additive O, I\nminus loss of O×I",
         [(0.0, "-", "no gain")]),
        ("J-H5", "loss of the Lyapunov rank\n÷ loss of the profile",
         [(1.0, "-", "equal"), (1.05, "--", "+5%")]),
        ("J-H6", "loss of profile + delay vector\n÷ loss of the profile",
         [(1.0, "-", "equal")]),
    )
    for ax, (cid, ylabel, lines) in zip(axes, spec):
        group = find(rows, cid)
        group.sort(key=lambda r: (SYSTEMS.index(r["system"]),
                                  PROFILES.index(r["profile"])))
        title(ax, group[0], claim_panel(ax, group, ylabel, lines))
    seed_legend(fig, 0.9)
    frame(fig, "The other horizon claims, at the horizon T_c")
    fig.tight_layout(rect=(0, 0.05, 1, 0.86))
    return save(fig, out, "F3_horizon_claims")


def allocation_claims(rows, out: Path) -> Path:
    """F4: J-A2, J-A3, J-A4, J-I1, J-C2."""
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    spec = (
        ("J-A2", "blend MSE, fitted constant\n÷ MSE with the profile",
         [(1.0, "-", "equal"), (1.05, "--", "+5%")]),
        ("J-A3", "MSE of a fitted constant weight\n÷ MSE of the separation "
         "formula", [(1.0, "-", "equal")]),
        ("J-A4", "blend MSE, delay vector alone\n÷ MSE with the profile",
         [(1.0, "-", "equal")]),
        ("J-I1", "ΔR² of logit w* from adding I\n(given R, O, N)",
         [(0.0, "-", "no gain")]),
        ("J-C2", "realized false-trust rate\n(full deployable system)",
         [(0.10, "--", "10% target")]),
    )
    for ax, (cid, ylabel, lines) in zip(axes.flat, spec):
        group = find(rows, cid)
        group.sort(key=lambda r: (SYSTEMS.index(r["system"]),
                                  PROFILES.index(r["profile"])))
        level = claim_panel(ax, group, ylabel, lines)
        if cid == "J-I1":
            level = "95% intervals"  # ablation.PROFILE_LEVEL, not stored
        title(ax, group[0], level)
        if cid == "J-A4":
            notes = [
                f"{SEEDS[i]}: undetermined ({v['reason']})"
                for i, v in enumerate(group[0]["values"])
                if v["reading"] == "undetermined"
            ]
            ax.text(
                0.98, 0.03, "hollow:\n" + "\n".join(notes),
                transform=ax.transAxes, ha="right", va="bottom",
                fontsize=7, color="0.25",
            )
    axes.flat[-1].axis("off")
    axes.flat[-1].text(
        0.0, 0.5,
        "How to read these panels\n\n"
        "• Each group is one claim row; its five points are the five sealed\n"
        "  seeds, never averaged.\n"
        "• A row is confirmed when at least 4 of the 5 stored readings imply\n"
        "  the claim (filled markers) and no two seeds contradict.\n"
        "• J-A4 is not confirmed: 3 of 5. On CONF-5 and CONF-7 the\n"
        "  pre-registered guard (effective sample size under 50) makes the\n"
        "  reading undetermined, whatever the interval.\n"
        "• 'Not confirmed' does not mean no effect (pre-registration §9).",
        fontsize=8, va="center",
    )
    seed_legend(fig, 0.94)
    frame(fig, "The allocation and tier 3 claims")
    fig.tight_layout(rect=(0, 0.04, 1, 0.91))
    return save(fig, out, "F4_allocation_claims")


def reading_grid(rows, out: Path) -> Path:
    """F5: the stored reading of every claim row on every seed."""
    n = len(rows)
    fig, ax = plt.subplots(figsize=(13, 0.29 * n + 1.6))
    for i, row in enumerate(rows):
        y = n - 1 - i
        for j, (word, imp) in enumerate(zip(row["readings"], row["implying"])):
            ax.add_patch(plt.Rectangle(
                (j, y), 1, 1, facecolor="#cfe8d6" if imp else "#eeeeee",
                edgecolor="white", lw=1.5,
            ))
            ax.text(j + 0.5, y + 0.5, word, ha="center", va="center",
                    fontsize=6.3)
        ax.add_patch(plt.Rectangle(
            (5.1, y), 1.1, 1,
            facecolor="#7fbf90" if row["verdict"] == "confirmed" else "#f2c48d",
            edgecolor="white", lw=1.5,
        ))
        ax.text(5.65, y + 0.5, row["verdict"], ha="center", va="center",
                fontsize=6.6, weight="bold")
        label = (
            f"{row['claim_id']} · {NAMES[row['system']]} · {row['profile']}"
            + (f" · {row['horizon']}" if row["horizon"] else "")
        )
        ax.text(-0.08, y + 0.5, label, ha="right", va="center", fontsize=6.8)
    for j, seed in enumerate(SEEDS):
        ax.text(j + 0.5, n + 0.25, seed, ha="center", fontsize=8,
                weight="bold")
    ax.text(5.65, n + 0.25, "row verdict", ha="center", fontsize=8,
            weight="bold")
    ax.set_xlim(-3.2, 6.3)
    ax.set_ylim(-0.2, n + 0.9)
    ax.axis("off")
    frame(
        fig,
        "Stored reading of every claim row on every seed "
        "(green: implies the claim; gray: does not)",
        "Presentation figure made after the freeze from confirm/confirm.json; "
        "words exactly as stored. It computes no statistic.",
    )
    fig.tight_layout(rect=(0, 0.02, 1, 0.97))
    return save(fig, out, "F5_reading_grid")


def save(fig, out: Path, name: str) -> Path:
    path = out / f"{name}.png"
    fig.savefig(path, dpi=160, metadata={"Software": None})
    plt.close(fig)
    return path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("folder", type=Path, help="promoted/phase-J")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    try:
        seeds, confirm, table = load(args.folder)
        rows = claim_rows(table, confirm, seeds)
    except (Refusal, lc.Refusal, rep.Refusal) as exc:
        print(f"phasej_figures: refused: {exc}", file=sys.stderr)
        return 64
    args.out.mkdir(parents=True, exist_ok=True)
    paths = [
        horizon_ablation(seeds, rows, args.out),
        allocation_ablation(seeds, rows, args.out),
        horizon_claims(rows, args.out),
        allocation_claims(rows, args.out),
        reading_grid(rows, args.out),
    ]
    print(f"{len(rows)} claim rows checked against confirm.json")
    for p in paths:
        print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
