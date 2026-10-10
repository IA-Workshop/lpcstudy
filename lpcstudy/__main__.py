"""Command-line entry point: ``python -m lpcstudy --preset pilot --out results/``."""

from __future__ import annotations

import argparse
import dataclasses
import json
import logging
import sys
import time
from pathlib import Path

from .config import PRESETS
from .experiments import run_robustness, run_system, run_transfer, run_transfer_target
from .pipeline import Study
from .report import make_figures, save_json, verdicts, write_markdown
from .seeds import (LEDGER_PATH, REGISTRY_PATH, SeedRefusal, load_registry, resolve_dev_seed,
                    with_seed)

REFUSAL_EXIT = 64
DEFAULT_SEED_ID = "DEV-0"


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser; abbreviations are off so no flag can be guessed (LPC.PC.7)."""
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--seed-id", default=None, metavar="DEV-n",
                        help=f"Registered development seed (default {DEFAULT_SEED_ID}).")
    parser.add_argument("--seed", nargs="*", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--preset", default="pilot", choices=sorted(PRESETS))
    parser.add_argument("--out", default="results", type=Path)
    parser.add_argument("--systems", nargs="*", default=None,
                        help="Subset of core systems (default: all in the preset).")
    parser.add_argument("--skip-transfer", action="store_true")
    parser.add_argument("--skip-robustness", action="store_true")
    parser.add_argument("--report-only", action="store_true",
                        help="Rebuild RESULTS.md and figures from an existing results.json.")
    return parser


def choose_seed(args: argparse.Namespace, extras: list[str],
                registry_path: Path) -> tuple[str, int]:
    """Return ``(seed_id, seed)`` for the parsed arguments or raise ``SeedRefusal``.

    Refused: a raw ``--seed``, an unrecognized option (including an abbreviation of a real
    one), and a seed id that is not in the registry. Values are never echoed.
    """
    if args.seed is not None:
        raise SeedRefusal("a raw integer seed (--seed) is never accepted; use --seed-id DEV-n")
    if extras:
        options = sorted({e.split("=", 1)[0] for e in extras if e.startswith("-")})
        what = (f"unrecognized option(s) {', '.join(options)} (abbreviations are disabled)"
                if options else "unexpected positional argument(s)")
        raise SeedRefusal(what)
    seed_id = args.seed_id if args.seed_id is not None else DEFAULT_SEED_ID
    return seed_id, resolve_dev_seed(seed_id, load_registry(registry_path))


def main(argv: list[str] | None = None, *, ledger_path: Path = LEDGER_PATH,
         registry_path: Path = REGISTRY_PATH) -> int:
    """Run the study for a preset and write results, report and figures.

    Parameters
    ----------
    argv : list[str], optional
        Arguments (default ``sys.argv[1:]``).
    ledger_path, registry_path : Path
        Ledger and seed registry. Python-only: no flag or environment variable
        can redirect them, so the commitment cannot be redirected from the command line.

    Returns
    -------
    int
        0 on success; 64 after a seed refusal, with exactly one stderr line
        ``lpcstudy: refused (LPC.PC.7): <reason>`` and before any output is created.
    """
    parser = build_parser()
    args, extras = parser.parse_known_args(argv)
    try:
        seed_id, seed = choose_seed(args, extras, registry_path)
    except SeedRefusal as refusal:
        print(f"lpcstudy: refused (LPC.PC.7): {refusal.reason}", file=sys.stderr)
        return REFUSAL_EXIT

    config = with_seed(PRESETS[args.preset], seed_id, seed)
    if args.systems:
        config = dataclasses.replace(config, core_systems=tuple(args.systems))
    out_dir = args.out / config.name
    out_dir.mkdir(parents=True, exist_ok=True)
    if args.report_only:
        results = json.loads((out_dir / "results.json").read_text())
        results["verdicts"] = verdicts(results, config)
        save_json(results, out_dir / "results.json")
        write_markdown(results, config, out_dir / "RESULTS.md")
        make_figures(results, config, out_dir / "figures")
        return 0
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.FileHandler(out_dir / "run.log"),
                                  logging.StreamHandler()])
    if args.seed_id is None:
        logging.getLogger("lpcstudy").info("seed id defaulted to %s", DEFAULT_SEED_ID)
    start = time.time()
    study = Study(config, out_dir)
    results: dict = {"config": dataclasses.asdict(config), "systems": {}}
    for system in config.core_systems:
        results["systems"][system] = run_system(study, system)
        save_json(results, out_dir / "results.json")
    if not args.skip_transfer and config.transfer_targets:
        for target in config.transfer_targets:
            if target not in study.core_cells:
                run_transfer_target(study, target)
        results["transfer"] = run_transfer(study)
        save_json(results, out_dir / "results.json")
    if not args.skip_robustness:
        results["robustness"] = {s: run_robustness(study, s)
                                 for s in config.robustness_systems
                                 if s in study.core_cells}
    results["verdicts"] = verdicts(results, config)
    results["estimators"] = study.estimator_log
    results["seconds"] = time.time() - start
    save_json(results, out_dir / "results.json")
    write_markdown(results, config, out_dir / "RESULTS.md")
    make_figures(results, config, out_dir / "figures")
    logging.getLogger("lpcstudy").info("study finished in %.0fs", results["seconds"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
