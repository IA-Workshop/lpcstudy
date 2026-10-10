"""Command-line entry point: ``python -m lpcstudy --preset pilot --out results/``."""

from __future__ import annotations

import argparse
import dataclasses
import json
import logging
import time
from pathlib import Path

from .config import PRESETS
from .experiments import run_robustness, run_system, run_transfer, run_transfer_target
from .pipeline import Study
from .report import make_figures, save_json, verdicts, write_markdown


def main() -> None:
    """Run the study for a preset and write results, report and figures."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", default="pilot", choices=sorted(PRESETS))
    parser.add_argument("--out", default="results", type=Path)
    parser.add_argument("--systems", nargs="*", default=None,
                        help="Subset of core systems (default: all in the preset).")
    parser.add_argument("--skip-transfer", action="store_true")
    parser.add_argument("--skip-robustness", action="store_true")
    parser.add_argument("--report-only", action="store_true",
                        help="Rebuild RESULTS.md and figures from an existing results.json.")
    args = parser.parse_args()

    config = PRESETS[args.preset]
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
        return
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.FileHandler(out_dir / "run.log"),
                                  logging.StreamHandler()])
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


if __name__ == "__main__":
    main()
