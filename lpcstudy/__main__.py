"""Command-line entry point: ``python -m lpcstudy --preset pilot --out results/``."""

from __future__ import annotations

import argparse
import dataclasses
import json
import logging
import os
import re
import sys
import time
from pathlib import Path

from . import provenance
from .config import PRESETS
from .dump import StateDump
from .experiments import run_handling, run_robustness, run_system
from .pipeline import Study
from .report import make_figures, save_json, verdicts, write_markdown
from .seeds import (LEDGER_PATH, REGISTRY_PATH, SeedRefusal, confirmatory_seed, load_registry,
                    resolve_dev_seed, with_seed)

REFUSAL_EXIT = 64
DEFAULT_SEED_ID = "DEV-0"
CONFIRMATORY_SEED_ID = "CONF-1"


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser; abbreviations are off so no flag can be guessed (LPC.PC.7)."""
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--seed-id", default=None, metavar="DEV-n",
                        help=f"Registered development seed (default {DEFAULT_SEED_ID}).")
    parser.add_argument("--confirmatory", action="store_true",
                        help="Owner-only (LPC.AUTH.6): seed and salt from LPC_CONF_SEED and "
                             "LPC_CONF_SALT, verified against the ledger commitment.")
    parser.add_argument("--seed", nargs="*", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--preset", default="pilot", choices=sorted(PRESETS))
    parser.add_argument("--out", default="results", type=Path)
    parser.add_argument("--systems", nargs="*", default=None,
                        help="Subset of core systems (default: all in the preset).")
    parser.add_argument("--skip-robustness", action="store_true")
    parser.add_argument("--report-only", action="store_true",
                        help="Rebuild RESULTS.md and figures from an existing results.json.")
    parser.add_argument("--estimator-refine-steps", default=None, metavar="N",
                        help="Levenberg-Marquardt iterations of the PLP estimator, an integer of "
                             "from 1 to 999 (WU-0005.6: iteration-doubling study; default: the "
                             "preset's value, 15). Not accepted with the confirmatory flag.")
    parser.add_argument("--states-dump", action="store_true",
                        help="Also write the per-state arrays of each core system to "
                             "<out>/<preset>/states/<system>.npz (WU-0003.7b; the schema is in "
                             "the docstring of lpcstudy/dump.py). Not accepted with the "
                             "confirmatory flag or --report-only. Results are bitwise the same "
                             "except one provenance leaf.")
    return parser


def choose_states_dump(args: argparse.Namespace) -> bool:
    """Return whether the state dump was requested, or raise if the request is not allowed.

    Refused together with the confirmatory flag: whether a sealed run may carry a dump is an open
    owner decision (O6), and until then the sealed run writes none. Refused with ``--report-only``,
    which recomputes nothing the dump could hold (a silently ignored flag would let a caller believe
    a dump exists). This runs before the seed is chosen, so a refused request has not read the
    sealed seed. Needs owner review before freeze (LPC.PC.11): it sits beside the seed guard.

    Raises
    ------
    SeedRefusal
        If the flag is given with the confirmatory flag or with ``--report-only``.
    """
    if not args.states_dump:
        return False
    if args.confirmatory:
        raise SeedRefusal("--states-dump is not accepted with the confirmatory flag (the sealed "
                          "run writes no state dump until the owner decides)")
    if args.report_only:
        raise SeedRefusal("--states-dump is not accepted with --report-only (nothing is "
                          "recomputed, so there is no dump to write)")
    return True


def choose_refine_steps(args: argparse.Namespace) -> int | None:
    """Return the requested Levenberg-Marquardt budget, or ``None`` if the flag is absent.

    The value is a canonical decimal integer from 1 to 999 (no sign, no leading zero, no space; the
    study needs at most 240, and a longer string would hit Python's digit limit). Anything else is
    refused, and so is any use of the flag together with the confirmatory flag
    (the sealed run takes the preset's value, LPC.PC.7). The value is never echoed. This runs
    before the seed is chosen, so a refused request has not read the sealed seed. Needs owner
    review before freeze (LPC.PC.11): it sits beside the seed guard.

    Raises
    ------
    SeedRefusal
        If the flag is given with the confirmatory flag, or its value is not an integer from 1
        to 999.
    """
    text = args.estimator_refine_steps
    if text is None:
        return None
    if args.confirmatory:
        raise SeedRefusal("--estimator-refine-steps is not accepted with the confirmatory flag "
                          "(the sealed run uses the preset's value)")
    if re.fullmatch(r"[1-9][0-9]{0,2}", text) is None:
        raise SeedRefusal("--estimator-refine-steps needs an integer from 1 to 999")
    return int(text)


def choose_clean_tree(args: argparse.Namespace) -> None:
    """Refuse a sealed run unless the working tree is clean and the commit is known (B8).

    Acts only with the confirmatory flag; a development run is not checked. The state is read
    with ``provenance.git_state(provenance.ROOT)``, the reader that fills ``commit`` and ``dirty``
    in the provenance block, so the block of an accepted run records exactly what was checked
    (``dirty`` is ``bool(git status --porcelain)``: untracked files count). Refused: a commit that
    is not a full hexadecimal object name (``None``, empty, ``"unknown"``, abbreviated) or an
    unknown ``dirty`` (git failed, so cleanliness cannot be told), and ``dirty`` true. Git's own
    error text is not echoed (it can hold newlines and paths); it stays in the provenance block of
    a development run. This runs before the seed is chosen, so a refused request has not read the
    sealed seed, and before ``provenance.collect``, so nothing has been written. Needs owner review
    before freeze (LPC.PC.11): it sits beside the seed guard. Owner ruling B8, 2026-10-18.

    Raises
    ------
    SeedRefusal
        If the confirmatory flag is given and the commit is unknown, git cannot say whether the
        tree is clean, or the tree is dirty.
    """
    if not args.confirmatory:
        return
    commit, dirty, _git_error = provenance.git_state(provenance.ROOT)
    if (commit is None or re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", commit) is None
            or dirty is None):
        raise SeedRefusal("the confirmatory flag needs a known commit and a readable git state "
                          "(commit unknown or git unavailable)")
    if dirty:
        raise SeedRefusal("the confirmatory flag needs a clean working tree (git status "
                          "--porcelain is not empty); commit or remove the changes first")


def choose_seed(args: argparse.Namespace, extras: list[str], registry_path: Path,
                ledger_path: Path = LEDGER_PATH) -> tuple[str, int]:
    """Return ``(seed_id, seed)`` for the parsed arguments or raise ``SeedRefusal``.

    Refused: a raw ``--seed``, an unrecognized option (including an abbreviation of a real
    one; the token is never echoed), the confirmatory flag together with ``--seed-id``, a seed id that is not in the
    registry, and a confirmatory request without the environment variables or with a seed
    and salt that do not match the ledger commitment. Values are never echoed.
    """
    if args.seed is not None:
        raise SeedRefusal("a raw integer seed (--seed) is never accepted; use --seed-id DEV-n")
    if extras:
        known = {name for action in build_parser()._actions for name in action.option_strings}
        names = sorted({e.split("=", 1)[0] if e.split("=", 1)[0] in known else "<value>"
                        for e in extras if e.startswith("-")})
        what = (f"unrecognized option(s) {', '.join(names)} (abbreviations are disabled)"
                if names else "unexpected positional argument(s)")
        raise SeedRefusal(what)
    if args.confirmatory:
        if args.seed_id is not None:
            raise SeedRefusal("the confirmatory flag and --seed-id are mutually exclusive")
        return CONFIRMATORY_SEED_ID, confirmatory_seed(os.environ, ledger_path)
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
        0 on success; 64 after a seed refusal (including a confirmatory request on a dirty tree
        or with an unknown commit), with exactly one stderr line
        ``lpcstudy: refused (LPC.PC.7): <reason>`` and before any output is created.
    """
    parser = build_parser()
    args, extras = parser.parse_known_args(argv)
    try:
        refine_steps = choose_refine_steps(args)  # before the seed: a sealed request stops here
        states_dump = choose_states_dump(args)  # the same: refused before the seed is read
        choose_clean_tree(args)  # B8: a sealed run needs a clean tree and a known commit, first
        seed_id, seed = choose_seed(args, extras, registry_path, ledger_path)
    except SeedRefusal as refusal:
        print(f"lpcstudy: refused (LPC.PC.7): {refusal.reason}", file=sys.stderr)
        return REFUSAL_EXIT

    config = with_seed(PRESETS[args.preset], seed_id, seed)
    if args.systems:
        config = dataclasses.replace(config, core_systems=tuple(args.systems))
    if refine_steps is not None:  # WU-0005.6: the only knob; the preset's value is the design (15)
        config = dataclasses.replace(config, estimator_refine_steps=refine_steps)
    out_dir = args.out / config.name
    if not args.report_only:  # read once, before any output exists (LPC.PC.18)
        clock = provenance.RunClock()
        block = provenance.collect(config, seed_id, sys.argv[1:] if argv is None else argv,
                                   clock)
        if states_dump:  # the one added leaf of a dump run (absent otherwise: 0 added)
            block["states_dump"] = True
    out_dir.mkdir(parents=True, exist_ok=True)
    if args.report_only:
        results = json.loads((out_dir / "results.json").read_text())
        stored = results.get("config", {}).get("estimator_refine_steps")
        if (refine_steps is not None and stored != refine_steps) or (
                refine_steps is None and stored is not None
                and stored != config.estimator_refine_steps):
            # The report prints the budget from ``config`` (iterative_label), so a mismatch would
            # label the results with the wrong number of iterations (PRIME.4: refuse, say why).
            print("lpcstudy: refused (LPC.PC.7): --estimator-refine-steps does not match the "
                  "budget stored in results.json (pass the stored value)", file=sys.stderr)
            return REFUSAL_EXIT
        try:
            results["verdicts"] = verdicts(results, config)  # refuses a pre-v3 file, writes nothing
        except ValueError as stale:
            print(f"lpcstudy: refused (stale results schema): {stale}", file=sys.stderr)
            return REFUSAL_EXIT
        save_json(results, out_dir / "results.json")
        write_markdown(results, config, out_dir / "RESULTS.md")
        make_figures(results, config, out_dir / "figures")
        return 0
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.FileHandler(out_dir / "run.log"),
                                  logging.StreamHandler()])
    log = logging.getLogger("lpcstudy")
    if args.seed_id is None and not args.confirmatory:
        log.info("seed id defaulted to %s", DEFAULT_SEED_ID)
    log.info("provenance: seed id %s, commit %s, dirty %s", block["seed_id"], block["commit"],
             block["dirty"])
    if block["git_error"]:
        log.warning("git state unavailable, recorded as null: %s", block["git_error"])
    missing = [name for name, version in block["packages"].items() if version is None]
    if missing:
        log.warning("%d package(s) not installed, recorded as null: %s", len(missing),
                    ", ".join(missing))
    probe_issues = provenance.probe_errors(block)
    if probe_issues:
        log.warning("%d platform probe failure(s) or fallback(s), recorded in the provenance "
                    "block: %s", len(probe_issues), "; ".join(probe_issues))
    start = time.time()
    study = Study(config, out_dir)
    if states_dump:
        study.dump = StateDump()
    results: dict = {"config": provenance.config_record(config), "systems": {},
                     "provenance": block}
    for system in config.core_systems:
        results["systems"][system] = run_system(study, system)
        save_json(results, out_dir / "results.json")
    if not args.skip_robustness:
        results["robustness"] = {s: run_robustness(study, s)
                                 for s in config.robustness_systems
                                 if s in study.core_cells}
    results["handling"] = run_handling(study, results)  # DEF-0001: counts, never silent
    results["verdicts"] = verdicts(results, config)
    results["estimators"] = study.estimator_log
    results["seconds"] = time.time() - start
    results["provenance"] = provenance.finish(block, clock)
    save_json(results, out_dir / "results.json")
    write_markdown(results, config, out_dir / "RESULTS.md")
    make_figures(results, config, out_dir / "figures")
    log.info("study finished in %.0fs", results["seconds"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
