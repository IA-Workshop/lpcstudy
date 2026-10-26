#!/usr/bin/env python3
"""Phase J experiments A, B and D on one run directory (WU-0048).

DEVELOPMENT, exploratory: every table carries "DEVELOPMENT (DEV-n):
exploratory, not a hypothesis test". The tool reads one run's state dumps
(``states/<system>.npz``, schema /3 with the ``split/`` group) and its
``results.json``, runs ``lpcstudy.contribution.analyze_system`` per system on
the CPU, recomputes the WU-0039b rows (b1), (b2) from the dump (test (g)), and
writes ``contrib.json`` and ``contrib.md`` to the output directory.

Usage::

    python tools/lpc_contrib.py <run-dir> --out <dir> [--jobs 4]
        [--systems lorenz63 ...] [--replication]

Refusals (exit 64, nothing written): an argument containing "confirmatory"
(any case); a run whose ``provenance.seed_kind`` is not ``development`` or
whose seed id is not ``DEV-n``; a held-out replication seed (DEV-5 to DEV-9)
without ``--replication`` (phase J, DV-4: those are analyzed once, by the
frozen script); a ``run.meta.json`` whose ``exit_code`` is not 0; a dump of
another seed; a dump without schema /3.

The model fits run in ``--jobs`` worker processes with one thread each
(``OMP``, ``MKL`` and ``OPENBLAS`` threads = 1), so ``--jobs 4`` uses four
cores, the project's limit.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lpcstudy import contribution as cb  # noqa: E402
from lpcstudy.ablation import CONDITIONS  # noqa: E402

HELD_OUT = {f"DEV-{k}" for k in range(5, 10)}
"""The replication seeds of phase J (plan DV-4), held out until the freeze."""
THREAD_VARS = ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS")


class Refusal(Exception):
    """A reason to stop before anything is written (exit 64)."""


# ------------------------------------------------------------------ reading
def check_run(run: Path, replication: bool) -> dict:
    """Read and check ``results.json`` (and ``run.meta.json`` if present)."""
    meta_path = run / "run.meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        if meta.get("exit_code") != 0:
            raise Refusal(f"run.meta.json exit_code is {meta.get('exit_code')}")
    results = json.loads((run / "results.json").read_text())
    prov = results.get("provenance", {})
    seed_id = str(prov.get("seed_id", ""))
    if prov.get("seed_kind") != "development" or not re.fullmatch(
        r"DEV-\d+", seed_id
    ):
        raise Refusal(
            f"not a development run: seed_kind={prov.get('seed_kind')!r}, "
            f"seed_id={seed_id!r}"
        )
    if seed_id in HELD_OUT and not replication:
        raise Refusal(f"{seed_id} is a held-out replication seed")
    if prov.get("complete") is False:
        raise Refusal("the run is not complete")
    return results


def load_dump(path: Path, seed_id: str) -> dict[str, np.ndarray]:
    """Load one dump and check that it belongs to the run's seed."""
    with np.load(path, allow_pickle=False) as loaded:
        arrays = {k: loaded[k] for k in loaded.files}
    if str(arrays.get("meta/seed_id")) != seed_id:
        raise Refusal(f"{path.name}: seed {arrays.get('meta/seed_id')}")
    return arrays


def git_state() -> dict:
    """Commit and dirty flag of the analysis code (the freeze needs them)."""

    def run(*args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(ROOT), *args], capture_output=True, text=True
        ).stdout.strip()

    return {
        "commit": run("rev-parse", "HEAD"),
        "dirty": bool(run("status", "--porcelain", "--", "lpcstudy", "tools")),
    }


# --------------------------------------------------------- the (g) check
def compare_leaves(mine, theirs, path: str = "") -> tuple[int, int, float]:
    """Count equal and different numeric leaves; largest absolute difference.

    Only the keys present in both are compared; strings must be equal.
    """
    if isinstance(mine, dict) and isinstance(theirs, dict):
        same = diff = 0
        worst = 0.0
        for key in mine.keys() & theirs.keys():
            s, d, w = compare_leaves(mine[key], theirs[key], f"{path}/{key}")
            same, diff, worst = same + s, diff + d, max(worst, w)
        return same, diff, worst
    if isinstance(mine, (list, tuple)) and isinstance(theirs, (list, tuple)):
        same = diff = 0
        worst = 0.0
        for a, b in zip(mine, theirs):
            s, d, w = compare_leaves(a, b, path)
            same, diff, worst = same + s, diff + d, max(worst, w)
        return same, diff, worst
    if isinstance(mine, (int, float)) and isinstance(theirs, (int, float)):
        a, b = float(mine), float(theirs)
        if a == b or (np.isnan(a) and np.isnan(b)):
            return 1, 0, 0.0
        return 0, 1, abs(a - b)
    return (1, 0, 0.0) if mine == theirs else (0, 1, float("inf"))


def cross_check(data, seed: int, config: dict, leaves: dict) -> dict:
    """Test (g): rows (b1), (b2) from the dump against the run's leaves."""
    mine = cb.qn_cross_check(
        data, seed, config["bootstrap_resamples"], config["bootstrap_block"]
    )
    out = {}
    for target, entry in mine.items():
        same, diff, worst = compare_leaves(
            {k: entry[k] for k in ("leave_one_out", "shapley", "r2_by_subset")},
            leaves[target],
        )
        out[target] = {"equal": same, "different": diff, "max_abs_diff": worst}
    out["drop_N_reproduced"] = all(
        compare_leaves(
            mine[t]["leave_one_out"]["N"], leaves[t]["leave_one_out"]["N"]
        )[1]
        == 0
        for t in mine
    )
    out["all_rows_reproduced"] = all(
        v["different"] == 0 for k, v in out.items() if isinstance(v, dict)
    )
    return out


# ---------------------------------------------------------------- writing
def to_json(value):
    """JSON-safe copy: non-finite floats become None, arrays lists."""
    if isinstance(value, dict):
        return {str(k): to_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_json(v) for v in value]
    if isinstance(value, np.ndarray):
        return to_json(value.tolist())
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        return float(value) if np.isfinite(value) else None
    return value


def fmt(value, digits: int = 3) -> str:
    """A number for a table (``-`` if missing)."""
    if value is None or (isinstance(value, float) and not np.isfinite(value)):
        return "-"
    if isinstance(value, (int, np.integer)):
        return str(value)
    return f"{value:.{digits}g}"


def ci(row: dict) -> str:
    lo, hi = row.get("ci", [None, None])
    return f"[{fmt(lo)}, {fmt(hi)}]"


def reading(row: dict) -> str:
    text = row.get("reading", "")
    return f"{text} ({row['reason']})" if row.get("reason") else text


def markdown(record: dict) -> str:
    """The headline tables of every system (A, B, D), all horizons."""
    lines = [f"# Phase J contribution study: {record['run']['seed_id']}", ""]
    label = record["label"]
    lines += [
        f"**{label}.** Run `{record['run']['dir']}`; analysis commit "
        f"`{record['analysis']['commit']}` (dirty: "
        f"{record['analysis']['dirty']}). Every reading is an estimate; "
        "Shapley shares and interactions are predictive, not causal. "
        "Training variance is not in the intervals.",
        "",
    ]
    for system, res in record["systems"].items():
        lines += [f"## {system}", "", f"**{label}.**", ""]
        lines += _checks_table(res)
        lines += _allocation_tables(res, label)
        lines += _horizon_tables(res, label)
    return label_tables("\n".join(lines) + "\n", label)


def label_tables(text: str, label: str) -> str:
    """Put a label paragraph before every table that lacks one."""
    blocks = text.split("\n\n")
    out: list[str] = []
    for block in blocks:
        if block.lstrip().startswith("|") and (not out or label not in out[-1]):
            out.append(f"{label}.")
        out.append(block)
    return "\n\n".join(out)


def _checks_table(res: dict) -> list[str]:
    chk = res["checks"]
    f1 = chk["f1_state_mse"]
    g = chk.get("g_wu0039b", {})
    return [
        "| check | result |",
        "|---|---|",
        "| (f1) state_mse from per-draw errors, max rel diff | "
        + ", ".join(f"{k} {v:.1e}" for k, v in f1["max_rel_diff"].items())
        + f" (within 1e-12: {f1['within_1e-12']}) |",
        f"| (g) WU-0039b (b1), (b2) rows reproduced | drop-N: "
        f"{g.get('drop_N_reproduced')}, all rows: "
        f"{g.get('all_rows_reproduced')} |",
        f"| separation formula on F-hat vs stored A4 at H_ref, max abs | "
        f"{fmt(chk.get('separation_vs_stored_A4_max_abs'))} |",
        f"| T_c: T = 1 / e_(T-1) = theta (train, test) | "
        f"{chk['crossing_time']['train']['n_first_step']}/"
        f"{chk['crossing_time']['train']['n_exact_theta']}, "
        f"{chk['crossing_time']['test']['n_first_step']}/"
        f"{chk['crossing_time']['test']['n_exact_theta']} |",
        f"| (f2) dependence bias, deployable rows (reported, not gating) | "
        f"{_f2_summary(res)} |",
        "",
    ]


def _f2_summary(res: dict) -> str:
    """Count the (f2) readings; name the rows that are not "no detectable"."""
    rows, flagged = 0, []
    for hkey, blocks in res["allocation"].items():
        for rule, d in (
            blocks.get("deployable", {}).get("dependence_bias", {}).items()
        ):
            rows += 1
            if d["reading"] != "no detectable dependence bias":
                part = d["dependence"]
                flagged.append(
                    f"H={hkey} {rule}: {d['reading']}, t1+t2 / V "
                    f"{fmt(part['rel'])}, z {fmt(d['paired']['z'])}"
                )
    shown = "; ".join(flagged[:12]) + (" ..." if len(flagged) > 12 else "")
    return f"{rows} rows; {len(flagged)} flagged" + (
        f": {shown}" if flagged else ""
    )


def _allocation_tables(res: dict, label: str) -> list[str]:
    out = [
        "### A. Allocation: drop-one and Shapley",
        "",
        f"{label}. MSE ratio MSE(F without X)/MSE(F) at level 1 - 0.05/4 "
        "(reading by the 1.05 table, with the n_eff guard); excess ratio "
        "L_A(F without X)/L_A(F) and Holm p (Delta MSE > 0) are estimates. "
        "phi = Shapley share of L_A (95%). Oracle rows: moment form; "
        "deployable rows: realized per draw.",
        "",
        "| horizon | profile | X | MSE ratio [CI] | reading | excess ratio | "
        "Holm p | phi_X [95% CI] | share |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for hkey, blocks in res["allocation"].items():
        for kind, b in blocks.items():
            for x in CONDITIONS:
                row = b["drop_one"][x]
                sh = b["shapley_L_A"]["rows"][x]
                out.append(
                    f"| {b['horizon']} | {kind} | {x} | "
                    f"{fmt(row['mse_ratio']['ratio'])} {ci(row['mse_ratio'])} | "
                    f"{reading(row['mse_ratio'])} | "
                    f"{fmt(row['excess_ratio']['ratio'])} | "
                    f"{fmt(row['p_holm'])} | {fmt(sh['phi'])} {ci(sh)} | "
                    f"{fmt(sh['share'])} |"
                )
    out += [
        "",
        "### A. Allocation: summary per horizon",
        "",
        f"{label}. n_eff = Kish size of kappa on the test states; G = 1 - "
        "L_A(rule)/L_A(constant), estimate (95%).",
        "",
        "| horizon | profile | n_eff(kappa) | G(F) [CI] | G(separation) | "
        "MSE(F)/MSE(sep) [CI] | reading | settings (A) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for hkey, blocks in res["allocation"].items():
        for kind, b in blocks.items():
            full = b["subsets"]["ROIN"]
            g_sep = None
            if "separation" in b["ladder"]["L_A"]:
                g_sep = (
                    1
                    - b["ladder"]["L_A"]["separation"]
                    / b["ladder"]["L_A"]["none"]
                )
            chosen = [
                v["fit"]["A"]["setting"]
                for v in b["subsets"].values()
                if isinstance(v["fit"].get("A"), dict)
            ]
            settings = f"F: {full['fit']['A']['setting']}; " + ", ".join(
                f"{s} {chosen.count(s)}" for s in ("qn", "mid", "low")
            )
            out.append(
                f"| {b['horizon']} | {kind} | {fmt(b['n_eff_kappa'])} | "
                f"{fmt(full['G']['ratio'])} {ci(full['G'])} | {fmt(g_sep)} | "
                f"{fmt(full['mse_vs_separation']['ratio'])} "
                f"{ci(full['mse_vs_separation'])} | "
                f"{reading(full['mse_vs_separation'])} | {settings} |"
            )
    out += [
        "",
        "### B. Allocation: pairwise interactions (logit u, interior states)",
        "",
        f"{label}. Delta = L(additive) - L(additive + pair) on the test "
        "states, models fixed; level 1 - 0.05/6; Holm over the six pairs. "
        "R x I and O x I are primary.",
        "",
        "| horizon | profile | pair | Delta [CI] | Holm p | reading | "
        "loss ratio reading |",
        "|---|---|---|---|---|---|---|",
    ]
    for hkey, kinds in res["interactions"].items():
        for kind, parts in kinds.items():
            part = parts.get("logit", {})
            if "pairs" not in part:
                out.append(f"| {hkey} | {kind} | - | {reading(part)} | | | |")
                continue
            horizon = res["allocation"][hkey][kind]["horizon"]
            for name in ("RI", "OI", "RO", "RN", "ON", "IN"):
                row = part["pairs"][name]
                star = " (primary)" if row["primary"] else ""
                out.append(
                    f"| {horizon} | {kind} | {name}{star} | "
                    f"{fmt(row['difference'])} {ci(row)} | "
                    f"{fmt(row['p_holm'])} | {row['reading']} | "
                    f"{reading(row['loss_ratio'])} |"
                )
    out += [
        "",
        "### D. Allocation ladder (rung against the full profile)",
        "",
        f"{label}. MSE ratio MSE(rung)/MSE(F) at level 1 - 0.05/m (m rungs); "
        "Holm p for Delta MSE > 0. Theory gap L_A(oracle F) is an upper "
        "bound; estimation gap = L_A(deployable F) - L_A(oracle F) (95%).",
        "",
        "| horizon | profile | rung | MSE | MSE ratio vs F [CI] | reading | "
        "Holm p |",
        "|---|---|---|---|---|---|---|",
    ]
    for hkey, blocks in res["allocation"].items():
        for kind, b in blocks.items():
            lad = b["ladder"]
            for rung in lad["rungs"]:
                if rung == "ROIN":
                    out.append(
                        f"| {b['horizon']} | {kind} | F (ROIN) | "
                        f"{fmt(lad['mse'][rung])} | 1 | | |"
                    )
                    continue
                row = lad["vs_full"][rung]
                out.append(
                    f"| {b['horizon']} | {kind} | {rung} | "
                    f"{fmt(lad['mse'][rung])} | "
                    f"{fmt(row['mse_ratio']['ratio'])} {ci(row['mse_ratio'])}"
                    f" | {reading(row['mse_ratio'])} | {fmt(row['p_holm'])} |"
                )
    out += [
        "",
        "| horizon | theory gap (upper bound) [CI] | estimation gap [CI] | "
        + " | ".join(f"gap with {x} estimated" for x in CONDITIONS)
        + " |",
        "|---|---|---|" + "---|" * len(CONDITIONS),
    ]
    for hkey, gap in res.get("gaps", {}).items():
        horizon = res["allocation"][hkey]["oracle"]["horizon"]
        th, est = gap["theory_gap_upper_bound"], gap["estimation_gap"]
        cells = [
            f"{fmt(gap['by_condition'][x]['estimate'])} "
            f"{ci(gap['by_condition'][x])}"
            for x in CONDITIONS
        ]
        out.append(
            f"| {horizon} | {fmt(th['estimate'])} {ci(th)} | "
            f"{fmt(est['estimate'])} {ci(est)} | " + " | ".join(cells) + " |"
        )
    out.append("")
    return out


def _horizon_tables(res: dict, label: str) -> list[str]:
    out = [
        "### Horizon decision (Y = ln min(T_c, H_max))",
        "",
        f"{label}. Pinball loss at tau = 0.5; drop-one ratio at level 1 - "
        "0.05/4; ladder ratio vs F at 1 - 0.05/m; C = Harrell's C (95%); "
        "coverage of q_0.1, q_0.5, q_0.9 and the 80% interval below the cap.",
        "",
        "| profile | X | pinball ratio [CI] | reading | Holm p | phi [CI] |",
        "|---|---|---|---|---|---|",
    ]
    for kind, b in res["horizon"].items():
        for x in CONDITIONS:
            row = b["drop_one"][x]
            sh = b["shapley_pinball"]["rows"][x]
            out.append(
                f"| {kind} | {x} | {fmt(row['pinball_ratio']['ratio'])} "
                f"{ci(row['pinball_ratio'])} | {reading(row['pinball_ratio'])}"
                f" | {fmt(row['p_holm'])} | {fmt(sh['phi'])} {ci(sh)} |"
            )
    out += [
        "",
        "| profile | rung | pinball | ratio vs F [CI] | reading | C [CI] | "
        "cov 0.1 / 0.5 / 0.9 / 80% |",
        "|---|---|---|---|---|---|---|",
    ]
    for kind, b in res["horizon"].items():
        for rung in b["ladder"]["rungs"]:
            r = b["rows"][rung]
            cov = (
                " / ".join(
                    fmt(r["coverage"][t]["coverage_below_cap"])
                    for t in ("0.1", "0.5", "0.9")
                )
                + " / "
                + fmt(r["coverage_80"]["coverage_below_cap"])
            )
            if rung == "ROIN":
                ratio, read = "1", ""
            else:
                row = b["ladder"]["vs_full"][rung]["pinball_ratio"]
                ratio, read = f"{fmt(row['ratio'])} {ci(row)}", reading(row)
            out.append(
                f"| {kind} | {rung} | {fmt(r['pinball_0.5'])} | {ratio} | "
                f"{read} | {fmt(r['c_index']['c_index'])} "
                f"{ci(r['c_index'])} | {cov} |"
            )
        lr = b["lyapunov_rank"]
        out.append(
            f"| {kind} | Lyapunov rank (C only) | | | | "
            f"{fmt(lr['c_index'])} {ci(lr)} | |"
        )
    out += [
        "",
        "| profile | pair | Delta [CI] | Holm p | detected |",
        "|---|---|---|---|---|",
    ]
    for kind, b in res["horizon"].items():
        for name, row in b["interactions"]["pairs"].items():
            star = " (primary)" if row["primary"] else ""
            out.append(
                f"| {kind} | {name}{star} | {fmt(row['difference'])} "
                f"{ci(row)} | {fmt(row['p_holm'])} | {row['detected']} |"
            )
    out.append("")
    return out


# ------------------------------------------------------------------- main
def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if any("confirmatory" in a.lower() for a in argv):
        print("lpc_contrib: refused: confirmatory", file=sys.stderr)
        return 64
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("run", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--systems", nargs="*")
    parser.add_argument("--replication", action="store_true")
    args = parser.parse_args(argv)
    try:
        results = check_run(args.run, args.replication)
        seed_id = results["provenance"]["seed_id"]
        config = results["config"]
        systems = args.systems or list(results["systems"])
        dumps = {
            s: load_dump(args.run / "states" / f"{s}.npz", seed_id)
            for s in systems
        }
        datas = {s: cb.SystemData.from_arrays(a) for s, a in dumps.items()}
    except (Refusal, ValueError, FileNotFoundError) as err:
        print(f"lpc_contrib: refused: {err}", file=sys.stderr)
        return 64
    for name in THREAD_VARS:
        os.environ[name] = "1"
    record = {
        "label": cb.LABEL.format(seed_id=seed_id),
        "run": {
            "dir": str(args.run),
            "seed_id": seed_id,
            "commit": results["provenance"].get("commit"),
            "preset": results["provenance"].get("preset"),
        },
        "analysis": git_state(),
        "systems": {},
    }
    context = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(args.jobs, mp_context=context) as pool:

        def mapper(func, items):
            return pool.map(func, items, chunksize=2)

        for system, data in datas.items():
            start = time.time()
            res = cb.analyze_system(
                data,
                int(config["seed"]),
                n_resamples=int(config["bootstrap_resamples"]),
                block=int(config["bootstrap_block"]),
                mapper=mapper,
            )
            leaves = results["systems"][system]["ablation"][
                "profile_conditions"
            ]["oracle"]
            res["checks"]["g_wu0039b"] = cross_check(
                data, int(config["seed"]), config, leaves
            )
            res["seconds"] = time.time() - start
            record["systems"][system] = res
            print(f"{system}: {res['seconds']:.0f} s", file=sys.stderr)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "contrib.json").write_text(
        json.dumps(to_json(record), indent=1, allow_nan=False) + "\n"
    )
    (args.out / "contrib.md").write_text(markdown(record))
    print(f"wrote {args.out / 'contrib.json'} and contrib.md", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
