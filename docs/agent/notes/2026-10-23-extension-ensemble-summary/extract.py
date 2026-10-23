"""Read-only extraction of stored leaves from the development ensemble and extension runs.

DEVELOPMENT seeds only (DEV-1, DEV-3, DEV-4). Computes no statistic and no verdict:
every value printed is a stored leaf of results.json or run.meta.json, printed with its
leaf path. The only derived items are (a) string comparisons of stored verdict words
across seeds and (b) set membership of an extension system's stored word among the words
stored for the frozen systems in the ensemble. Run with ``python3 -I extract.py``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RUN_ROOT = Path("/home/brianm/projects/physics/chaos/lpcstudy-wt/run")
ENSEMBLE = {
    seed: RUN_ROOT / f"ens-3dec086/runs/dev/ens-{seed}/full" for seed in ("DEV-1", "DEV-3", "DEV-4")
}
EXTENSION = {
    "rossler_hyper": RUN_ROOT / "ext-run-974519a/runs/dev/ext-rossler_hyper-gpu/full",
    "lorenz63_r166": RUN_ROOT / "ext-run-974519a/runs/dev/ext-lorenz63_r166-gpu/full",
    "rossler_z": RUN_ROOT / "ext-run-974519a/runs/dev/ext-rossler_z-gpu/full",
    "hindmarsh_rose": RUN_ROOT / "ext-run-392a069/runs/dev/ext-hindmarsh_rose-gpu/full",
    "hyper_jha": RUN_ROOT / "ext-run-392a069/runs/dev/ext-hyper_jha-gpu/full",
    "lorenz96_4": RUN_ROOT / "ext-run-392a069/runs/dev/ext-lorenz96_4-gpu/full",
}
PRIMARIES = ("H2a", "H2b", "H3c")
SECONDARIES = ("H1a", "H1b", "H1c", "H1d", "H2c", "H2d", "H2e", "H3a", "H3b", "Q-N", "gain_bound")
DESIGN_LEVEL = "0.9833 (design value, not stored)"


def load(folder: Path) -> tuple[dict, dict]:
    """Return (results, meta) of one run folder."""
    return (
        json.loads((folder / "results.json").read_text()),
        json.loads((folder / "run.meta.json").read_text()),
    )


def fmt(value: object) -> str:
    """Print a stored number to four significant digits, or the stored value as is."""
    if isinstance(value, float):
        return f"{value:.4g}"
    if isinstance(value, list):
        return "[" + ", ".join(fmt(v) for v in value) + "]"
    return str(value)


def run_row(name: str, res: dict, meta: dict) -> str:
    """One provenance and completeness row."""
    prov = res["provenance"]
    skip = "--skip-robustness" in prov["argv"]
    return (
        f"| {name} | {meta['seed_id']} | {meta['device']} ({prov['device']['kind']}) | "
        f"{meta['wall_seconds']} | {meta['exit_code']} | {prov['commit'][:7]} | {prov['dirty']} | "
        f"{prov['complete']} | {prov['promoted']} | {res['handling']['failed_variants']} | "
        f"{res['handling']['skipped_variants']} | {'skipped' if skip else 'run'} | {prov['label']} |"
    )


def gate_rows(name: str, res: dict) -> list[str]:
    """Gate V1-V7 per system, with the stored V7 numbers."""
    rows = []
    for system, block in res["systems"].items():
        gate = block["validation"]["gate"]
        v7 = block["V7"]
        effs = v7["efficiency_median_by_noise"]
        eff_txt = ", ".join(f"{k}: {fmt(v)}" for k, v in effs.items())
        status = "PASS" if gate["gate_pass"] else "FAIL -> PROVISIONAL"
        rows.append(
            f"| {name} | {system} | "
            + " | ".join("pass" if gate[k] else "FAIL" for k in ("V1", "V2", "V4", "V5", "V6", "V7"))
            + f" | {fmt(block['validation']['cp_median_vpt_lyapunov'])} | {status} | "
            f"slope {fmt(v7['median_slope'])} {fmt(v7['ci'])} (pass {v7['slope_pass']}); "
            f"median δ/(ρν) {eff_txt}; n_nonfinite {v7['n_nonfinite']} |"
        )
    return rows


def word_of(res: dict, hyp: str, system: str) -> str:
    """Stored per-system word at verdicts/<hyp>/by_system/<system>."""
    return res["verdicts"][hyp]["by_system"][system]


def primary_rows(name: str, res: dict) -> list[str]:
    """Primary parts: stored estimate, interval, level, word, reason, leaf path."""
    rows = []
    for system, block in res["systems"].items():
        h2a = block["H2a"]
        root = f"systems/{system}/H2a"
        rows.append(
            f"| {name} | {system} | H2a(i) | {fmt(h2a['median_range'])} | {fmt(h2a['range_ci'])} | "
            f"{DESIGN_LEVEL} | {h2a['part_i_verdict']} | {h2a['part_i_reason']} | "
            f"n_eligible {h2a['n_eligible_states']}, n_excluded {h2a['n_excluded_states']} | "
            f"{root}/median_range, range_ci, part_i_verdict |"
        )
        for part in ("zero", "interior"):
            leaf = h2a["part_ii"][part]
            rows.append(
                f"| {name} | {system} | H2a(ii) {part} | {fmt(leaf['partial_corr'])} | {fmt(leaf['ci'])} | "
                f"{leaf.get('level', DESIGN_LEVEL)} | {leaf['verdict']} | {leaf['reason']} | "
                f"n {leaf['n_states']} | {root}/part_ii/{part}/{{partial_corr,ci,verdict}} |"
            )
        noise = block["H2b"]["noise"]
        rows.append(
            f"| {name} | {system} | H2b(i) noise | {fmt(noise['mean_state_spearman'])} | {fmt(noise['ci'])} | "
            f"{noise.get('level', DESIGN_LEVEL)} | {noise['verdict']} | {noise['reason']} | "
            f"n_constant {noise['n_constant_states']} | systems/{system}/H2b/noise/{{mean_state_spearman,ci,verdict}} |"
        )
        lib = block["H2b"]["library_change"]
        rows.append(
            f"| {name} | {system} | H2b(ii) library | {fmt(lib['mean_change'])} | {fmt(lib['ci'])} | "
            f"{fmt(lib['level'])} | {lib['verdict']} | {lib['reason']} | "
            f"n {lib['n_states']}, zero-diff {lib['n_zero_difference']} | "
            f"systems/{system}/H2b/library_change/{{mean_change,ci,level,verdict}} |"
        )
        h3c = block["H3c"]
        rows.append(
            f"| {name} | {system} | H3c | {fmt(h3c['A5_over_A4_mse'])} | {fmt(h3c['ci'])} | {fmt(h3c['level'])} | "
            f"{h3c['verdict']} | {h3c['reason']} | n {h3c['n_states']} | "
            f"systems/{system}/H3c/{{A5_over_A4_mse,ci,level,verdict}} |"
        )
    return rows


def words_table(runs: dict[str, dict]) -> list[str]:
    """Per-system stored words for every hypothesis (verdicts/<H>/by_system/<s>)."""
    cols = [(name, s) for name, res in runs.items() for s in res["systems"]]
    head = "| Hypothesis | " + " | ".join(f"{n}:{s}" for n, s in cols) + " |"
    rows = [head, "|" + "---|" * (len(cols) + 1)]
    for hyp in PRIMARIES + SECONDARIES:
        rows.append(
            f"| {hyp} | " + " | ".join(word_of(runs[n], hyp, s) for n, s in cols) + " |"
        )
    return rows


def reasons(runs: dict[str, dict]) -> list[str]:
    """Stored reason strings of every secondary that is inconclusive (systems/<s>/<H>/reason)."""
    out = []
    for name, res in runs.items():
        for system, block in res["systems"].items():
            for hyp in PRIMARIES + SECONDARIES:
                leaf = block.get(hyp, {})
                reason = leaf.get("reason") if isinstance(leaf, dict) else None
                if reason:
                    out.append(f"- {name}:{system} {hyp}: `{reason}` (systems/{system}/{hyp}/reason)")
    return out


def censoring(name: str, res: dict) -> list[str]:
    """Exclusion, censoring and clip-sensitivity counts that limit reading."""
    out = []
    for system, block in res["systems"].items():
        h3a = block["H3a"]
        qn = block["Q-N"]
        gb = block["gain_bound"]
        h1c = block["H1c"]["PLP"]
        clip = block["clip_sensitivity"]
        flags = [h for h, v in clip.get("by_hypothesis", {}).items() if v.get("flag")]
        out.append(
            f"| {name} | {system} | {block['H2a']['n_eligible_states']}/{block['H2a']['n_excluded_states']} | "
            f"{block['H2a']['n_noncontiguous_states']} | {h3a['n_censored_per_regime']} | {h3a['n_km_not_reached']} | "
            f"{h3a['n_empty_regimes']} | {qn['n_w_zero']}/{qn['n_w_one']} | "
            f"{h1c['n_states']}/{h1c.get('n_ineligible_states', 'n/a')} | "
            f"{gb['n_states']}/{gb['n_total_states']} | {clip['status']} | {', '.join(flags) or 'none'} |"
        )
    return out


def lyapunov(res: dict) -> list[str]:
    """Stored λ_max of each system (systems/<s>/context/lambda_max)."""
    return [f"- {s}: {fmt(b['context']['lambda_max'])}" for s, b in res["systems"].items()]


def ensemble_flips(ens: dict[str, dict]) -> list[str]:
    """Overall words per seed and every per-system and part-level word that differs across seeds."""
    out = ["| Hypothesis | DEV-1 | DEV-3 | DEV-4 | agree |", "|---|---|---|---|---|"]
    for hyp in PRIMARIES + SECONDARIES:
        words = [ens[s]["verdicts"][hyp]["verdict"] for s in ens]
        out.append(f"| {hyp} | " + " | ".join(words) + f" | {'yes' if len(set(words)) == 1 else 'NO'} |")
    out.append("")
    out.append("Per-system words that differ across seeds (verdicts/<H>/by_system/<s>):")
    systems = list(next(iter(ens.values()))["systems"])
    for hyp in PRIMARIES + SECONDARIES:
        for system in systems:
            words = [word_of(ens[s], hyp, system) for s in ens]
            if len(set(words)) > 1:
                out.append(f"- {hyp}/{system}: " + ", ".join(f"{s} {w}" for s, w in zip(ens, words)))
    out.append("")
    out.append("Primary part-level words that differ across seeds:")
    for system in systems:
        for label, path in (
            ("H2a(i)", ("H2a", "part_i_verdict")),
            ("H2a(ii) zero", ("H2a", "part_ii", "zero", "verdict")),
            ("H2a(ii) interior", ("H2a", "part_ii", "interior", "verdict")),
            ("H2b(i)", ("H2b", "noise", "verdict")),
            ("H2b(ii)", ("H2b", "library_change", "verdict")),
            ("H3c", ("H3c", "verdict")),
        ):
            words = []
            for s in ens:
                leaf = ens[s]["systems"][system]
                for key in path:
                    leaf = leaf[key]
                words.append(leaf)
            out.append(
                f"- {system} {label}: " + ", ".join(f"{s} {w}" for s, w in zip(ens, words))
                + ("" if len(set(words)) == 1 else "  <- differs")
            )
    return out


def contrast(ens: dict[str, dict], ext: dict[str, dict]) -> list[str]:
    """Is each extension word among the words stored for the frozen systems on DEV-1/3/4?"""
    out = ["| Hypothesis | words on frozen systems (9 system-seed cells) | " + " | ".join(ext) + " |",
           "|---|---|" + "---|" * len(ext)]
    for hyp in PRIMARIES + SECONDARIES:
        frozen = sorted({word_of(r, hyp, s) for r in ens.values() for s in r["systems"]})
        cells = []
        for name, res in ext.items():
            word = word_of(res, hyp, name)
            cells.append(word if word in frozen else f"**{word}** (not seen on frozen)")
        out.append(f"| {hyp} | {', '.join(frozen)} | " + " | ".join(cells) + " |")
    return out


def main() -> int:
    """Print every table in Markdown."""
    ens = {s: load(p) for s, p in ENSEMBLE.items()}
    ext = {s: load(p) for s, p in EXTENSION.items()}
    ens_res = {s: r for s, (r, _) in ens.items()}
    ext_res = {s: r for s, (r, _) in ext.items()}
    print("## Runs\n")
    print("| run | seed | device | wall s | exit | commit | dirty | complete | promoted | failed var. | skipped var. | robustness | label |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for name, (res, meta) in {**{f"ens-{k}": v for k, v in ens.items()}, **{f"ext-{k}": v for k, v in ext.items()}}.items():
        print(run_row(name, res, meta))
    print("\n## Gate\n")
    print("| run | system | V1 | V2 | V4 | V5 | V6 | V7 | V3 (LT, reported) | gate | V7 stored numbers |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for name, res in {**{f"ens-{k}": v for k, v in ens_res.items()}, **ext_res}.items():
        for row in gate_rows(name, res):
            print(row)
    print("\n## lambda_max (stored)\n")
    for name, res in {**ens_res, **ext_res}.items():
        print(name, *lyapunov(res), sep="\n")
    print("\n## Words: ensemble\n")
    print("\n".join(words_table({f"ens-{k}": v for k, v in ens_res.items()})))
    print("\n## Words: extension\n")
    print("\n".join(words_table(ext_res)))
    print("\n## Primary intervals\n")
    print("| run | system | part | estimate | interval | level | word | reason | counts | leaf |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for name, res in {**{f"ens-{k}": v for k, v in ens_res.items()}, **ext_res}.items():
        for row in primary_rows(name, res):
            print(row)
    print("\n## Ensemble agreement\n")
    print("\n".join(ensemble_flips(ens_res)))
    print("\n## Extension words against frozen-system words (string membership only)\n")
    print("\n".join(contrast(ens_res, ext_res)))
    print("\n## Exclusion, censoring and clip flags\n")
    print("| run | system | H2a eligible/excluded | H2a noncontiguous | H3a censored per regime | H3a KM not reached | H3a empty regimes | Q-N n w*=0 / w*=1 | H1c PLP states/ineligible | gain bound states/total | clip status | clip-sensitive hypotheses |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for name, res in {**{f"ens-{k}": v for k, v in ens_res.items()}, **ext_res}.items():
        for row in censoring(name, res):
            print(row)
    print("\n## Stored reasons\n")
    print("\n".join(reasons({**{f"ens-{k}": v for k, v in ens_res.items()}, **ext_res})))
    return 0


if __name__ == "__main__":
    sys.exit(main())
