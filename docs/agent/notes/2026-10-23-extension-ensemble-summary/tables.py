"""Compact per-system tables for the development summary note (stored leaves only).

DEVELOPMENT seeds only. Prints one Markdown table per extension system and one per frozen
system of the development ensemble (DEV-1, DEV-3, DEV-4 side by side; no mean, spread or
range is computed, schedule O7). Run with ``python3 -I tables.py``.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from extract import ENSEMBLE, EXTENSION, SECONDARIES, fmt, load  # noqa: E402

PARTS = (
    ("H2a(i) median range of w*", ("H2a",), "median_range", "range_ci", "part_i_verdict", "upper < 0.1"),
    ("H2a(ii) zero, partial corr.", ("H2a", "part_ii", "zero"), "partial_corr", "ci", "verdict", "inside (-0.1, 0.1)"),
    ("H2a(ii) interior, partial corr.", ("H2a", "part_ii", "interior"), "partial_corr", "ci", "verdict", "inside (-0.1, 0.1)"),
    ("H2b(i) Spearman w* with rho", ("H2b", "noise"), "mean_state_spearman", "ci", "verdict", "lower > 0"),
    ("H2b(ii) library change of w*", ("H2b", "library_change"), "mean_change", "ci", "verdict", "lower > 0"),
    ("H3c MSE ratio A5/A4", ("H3c",), "A5_over_A4_mse", "ci", "verdict", "upper <= 1.05"),
)


def leaf_at(block: dict, path: tuple[str, ...]) -> dict:
    """Walk a key path."""
    for key in path:
        block = block[key]
    return block


def gate_text(block: dict) -> str:
    """Gate status with the failing checks named."""
    gate = block["validation"]["gate"]
    failed = [k for k in ("V1", "V2", "V4", "V5", "V6", "V7") if not gate[k]]
    if not failed:
        return "PASS (V1, V2, V4, V5, V6, V7)"
    v7 = block["V7"]
    eff = ", ".join(
        f"{k}: {fmt(v)}" for k, v in v7["efficiency_median_by_noise"].items()
    )
    return (
        f"FAIL {', '.join(failed)} -> PROVISIONAL. Stored V7: median δ/(ρν) by ρ {eff} "
        f"(band [0.9, 1.1]); median slope {fmt(v7['median_slope'])} (slope_pass {v7['slope_pass']})"
    )


def system_table(label: str, res: dict, system: str) -> list[str]:
    """One compact table for one system of one run."""
    block = res["systems"][system]
    verdicts = res["verdicts"]
    out = [
        f"**{label}** ({res['provenance']['label']}; commit {res['provenance']['commit'][:7]})",
        "",
        f"Gate: {gate_text(block)}.",
        "",
        "| Part | Estimate | Interval (level 0.9833) | Pass band | Stored part word |",
        "|---|---|---|---|---|",
    ]
    for name, path, est, ci, word, band in PARTS:
        leaf = leaf_at(block, path)
        out.append(f"| {name} | {fmt(leaf[est])} | {fmt(leaf[ci])} | {band} | {leaf[word]} |")
    out.append("")
    out.append(
        "Per-system words (verdicts/<H>/by_system/" + system + "): "
        + "; ".join(f"{h} {verdicts[h]['by_system'][system]}" for h in ("H2a", "H2b", "H3c"))
        + " (primaries); "
        + "; ".join(f"{h} {verdicts[h]['by_system'][system]}" for h in SECONDARIES if h != "gain_bound")
        + " (secondaries)."
    )
    h2a = block["H2a"]
    out.append(
        f"Counts: H2a eligible {h2a['n_eligible_states']} / excluded {h2a['n_excluded_states']} of 1000; "
        f"w* = 0: {h2a['n_w_zero']}, w* = 1: {h2a['n_w_one']}; "
        f"H3a censored per regime {block['H3a']['n_censored_per_regime']}; "
        f"V3 CP valid-prediction time {fmt(block['validation']['cp_median_vpt_lyapunov'])} LT (reported)."
    )
    out.append("")
    return out


def main() -> int:
    """Print the tables."""
    print("### Extension systems (DEV-3, one run each)\n")
    for system, folder in EXTENSION.items():
        print("\n".join(system_table(f"{system}", load(folder)[0], system)))
    print("### Frozen systems in the development ensemble\n")
    runs = {seed: load(folder)[0] for seed, folder in ENSEMBLE.items()}
    for system in ("lorenz63", "rossler", "chua"):
        print(f"**{system}** (DEV-1 | DEV-3 | DEV-4; gate PASS on all three seeds)\n")
        print("| Part | DEV-1 estimate [interval] word | DEV-3 | DEV-4 |")
        print("|---|---|---|---|")
        for name, path, est, ci, word, _band in PARTS:
            cells = []
            for seed in runs:
                leaf = leaf_at(runs[seed]["systems"][system], path)
                cells.append(f"{fmt(leaf[est])} {fmt(leaf[ci])} {leaf[word]}")
            print(f"| {name} | " + " | ".join(cells) + " |")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
