"""Command-line entry point of the study (``python -m lpcstudy``).

This is the front door of the study. ``main`` does the following, in order:

1. It checks the request before anything is computed. The seed guard
   (``seeds``) refuses any raw integer seed and any confirmatory request whose
   seed does not match the ledger commitment, and the clean-tree guard refuses
   a confirmatory run on code that is not committed. A refusal prints one line
   and exits with code 64 before any output exists (LPC.PC.7).
2. It picks a preset (``config``), stamps the seed on it, and collects the
   provenance block (``provenance``): the code version, settings and machine
   behind the run.
3. It runs the experiments (``pipeline`` and ``experiments``) system by
   system, saves ``results.json`` after each one, then computes the verdicts
   and writes ``RESULTS.md`` and the figures (``report``).

With ``--report-only`` it skips the computing of step 3 and rebuilds the
report from an existing ``results.json``.
"""

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
from .seeds import (
    LEDGER_PATH,
    REGISTRY_PATH,
    SeedRefusal,
    confirmatory_seed,
    load_registry,
    resolve_dev_seed,
    with_seed,
)

# Exit code of a refused request, and the seed ids that stand for the
# development default and for the default sealed confirmatory run (WU-0038:
# the confirmatory flag takes ``--seed-id CONF-n``; without it, CONF-1).
REFUSAL_EXIT = 64
DEFAULT_SEED_ID = "DEV-0"
CONFIRMATORY_SEED_ID = "CONF-1"


def _refuse(reason: str) -> int:
    """Print the one-line refusal message and return the refusal exit code."""
    print(f"lpcstudy: refused (LPC.PC.7): {reason}", file=sys.stderr)
    return REFUSAL_EXIT


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser.

    Abbreviations are turned off (``allow_abbrev=False``) so that a mistyped
    or shortened flag can never be silently read as another one (LPC.PC.7).

    Returns
    -------
    argparse.ArgumentParser
        The parser; its flags are documented in their ``help`` texts.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Command-line entry point: "
            "``python -m lpcstudy --preset pilot --out results/``."
        ),
        allow_abbrev=False,
    )
    parser.add_argument(
        "--seed-id",
        default=None,
        metavar="DEV-n|CONF-n",
        help=f"Registered development seed (default {DEFAULT_SEED_ID}); with "
        "the confirmatory flag, the sealed id CONF-n whose ledger commitment "
        f"the seed and salt must match (default {CONFIRMATORY_SEED_ID}).",
    )
    parser.add_argument(
        "--confirmatory",
        action="store_true",
        help="Owner-only (LPC.AUTH.6): seed and salt from LPC_CONF_SEED and "
        "LPC_CONF_SALT, verified against the ledger commitment.",
    )
    parser.add_argument(
        "--seed",
        nargs="*",
        default=None,
        help=argparse.SUPPRESS,
    )
    parser.add_argument("--preset", default="pilot", choices=sorted(PRESETS))
    parser.add_argument("--out", default="results", type=Path)
    parser.add_argument(
        "--systems",
        nargs="*",
        default=None,
        help="Subset of core systems (default: all in the preset).",
    )
    parser.add_argument("--skip-robustness", action="store_true")
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Rebuild RESULTS.md and figures from an existing results.json.",
    )
    parser.add_argument(
        "--estimator-refine-steps",
        default=None,
        metavar="N",
        help="Levenberg-Marquardt iterations of the PLP estimator, an integer "
        "of from 1 to 999 (WU-0005.6: iteration-doubling study; default: the "
        "preset's value, 15). Not accepted with the confirmatory flag.",
    )
    parser.add_argument(
        "--states-dump",
        action="store_true",
        help="Also write the per-state arrays of each core system to "
        "<out>/<preset>/states/<system>.npz (WU-0003.7b; the schema is in "
        "the docstring of lpcstudy/dump.py). Not accepted with the "
        "confirmatory flag or --report-only. Results are bitwise the same "
        "except one provenance leaf.",
    )
    return parser


def choose_states_dump(args: argparse.Namespace) -> bool:
    """Say whether the state dump was requested, or refuse a bad request.

    The state dump writes the per-state arrays of each core system to disk.
    It is refused together with the confirmatory flag: whether a sealed run
    may carry a dump is an open owner decision (O6), and until then the
    sealed run writes none. It is also refused with ``--report-only``, which
    recomputes nothing the dump could hold (a silently ignored flag would let
    a caller believe a dump exists). This runs before the seed is chosen, so a
    refused request has not read the sealed seed. Needs owner review before
    freeze (LPC.PC.11): it sits beside the seed guard.

    Parameters
    ----------
    args : argparse.Namespace
        The parsed arguments.

    Returns
    -------
    bool
        True if a dump was requested and allowed.

    Raises
    ------
    SeedRefusal
        If the flag is given with the confirmatory flag or with
        ``--report-only``.
    """
    if not args.states_dump:
        return False
    if args.confirmatory:
        raise SeedRefusal(
            "--states-dump is not accepted with the confirmatory flag (the "
            "sealed "
            "run writes no state dump until the owner decides)"
        )
    if args.report_only:
        raise SeedRefusal(
            "--states-dump is not accepted with --report-only (nothing is "
            "recomputed, so there is no dump to write)"
        )
    return True


def choose_refine_steps(args: argparse.Namespace) -> int | None:
    """Read the requested Levenberg-Marquardt iteration budget.

    The value is a canonical decimal integer from 1 to 999 (no sign, no
    leading zero, no space; the study needs at most 240, and a longer string
    would hit Python's digit limit). Anything else is refused, and so is any
    use of the flag together with the confirmatory flag (the sealed run takes
    the preset's value, LPC.PC.7). The value is never echoed. This runs before
    the seed is chosen, so a refused request has not read the sealed seed.
    Needs owner review before freeze (LPC.PC.11): it sits beside the seed
    guard.

    Parameters
    ----------
    args : argparse.Namespace
        The parsed arguments.

    Returns
    -------
    int or None
        The budget, or ``None`` if the flag is absent.

    Raises
    ------
    SeedRefusal
        If the flag is given with the confirmatory flag, or its value is not
        an integer from 1 to 999.
    """
    text = args.estimator_refine_steps
    if text is None:
        return None
    if args.confirmatory:
        raise SeedRefusal(
            "--estimator-refine-steps is not accepted with the confirmatory "
            "flag "
            "(the sealed run uses the preset's value)"
        )
    if re.fullmatch(r"[1-9][0-9]{0,2}", text) is None:
        raise SeedRefusal(
            "--estimator-refine-steps needs an integer from 1 to 999"
        )
    return int(text)


def choose_clean_tree(args: argparse.Namespace) -> str | None:
    """Refuse a sealed run unless the tree is clean and the commit known (B8).

    A sealed (confirmatory) run must be reproducible from a named commit, so
    its code must be exactly that commit. This check acts only with the
    confirmatory flag; a development run is not checked and ``None`` is
    returned.

    The state is read with ``provenance.git_state(provenance.ROOT)``, the
    reader that fills ``commit`` and ``dirty`` in the provenance block. The
    block of an accepted run is built from a second read, taken after the
    sealed seed has been read. ``main`` compares that read with the commit
    returned here and refuses if it differs (``check_tree_unchanged``), so an
    accepted run's block records the state that was checked.

    ``dirty`` is defined, and its hiding routes are listed, in
    ``provenance.git_state``. Modified, staged or untracked files count (an
    untracked file counts whatever ``status.showUntrackedFiles``,
    ``core.excludesFile`` or the ``GIT_CONFIG*`` environment say), and so
    does a tracked file hidden by the skip-worktree or assume-unchanged bit.
    Not closed, and left to the WU-0015.1 pre-run checks (accepted
    limitations): a file excluded by a ``.gitignore`` in the tree and a line
    in ``.git/info/exclude``.

    Refused here: a commit that is not a full hexadecimal object name
    (``None``, empty, ``"unknown"``, abbreviated), an unknown ``dirty`` (git
    failed, so cleanliness cannot be told), and ``dirty`` true. Git's own
    error text is not echoed (it can hold newlines and paths); it stays in the
    provenance block of a development run. This runs before the seed is
    chosen, so a refused request has not read the sealed seed, and before
    ``provenance.collect``, so nothing has been written. Needs owner review
    before freeze (LPC.PC.11): it sits beside the seed guard. Owner ruling B8,
    2026-10-18.

    Parameters
    ----------
    args : argparse.Namespace
        The parsed arguments.

    Returns
    -------
    str or None
        The checked commit (a full object name) for a sealed request,
        ``None`` otherwise.

    Raises
    ------
    SeedRefusal
        If the confirmatory flag is given and the commit is unknown, git
        cannot say whether the tree is clean, or the tree is dirty.
    """
    if not args.confirmatory:
        return None
    commit, dirty, _git_error = provenance.git_state(provenance.ROOT)
    if (
        commit is None
        or re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", commit) is None
        or dirty is None
    ):
        raise SeedRefusal(
            "the confirmatory flag needs a known commit and a readable git "
            "state "
            "(commit unknown or git unavailable)"
        )
    if dirty:
        raise SeedRefusal(
            "the confirmatory flag needs a clean working tree (modified or "
            "untracked "
            "files, or a tracked file hidden by skip-worktree or "
            "assume-unchanged); "
            "commit or remove the changes first"
        )
    return commit


def check_tree_unchanged(
    checked: str | None,
    commit: str | None,
    dirty: bool | None,
) -> None:
    """Refuse a sealed run whose second git read differs from the first.

    The first read is the one ``choose_clean_tree`` passed. The sealed seed
    has been read by the time this runs (the one-time draw is not undone; this
    is why the first guard exists and runs before it). What this prevents is
    output from a run whose own provenance block would say ``dirty: true`` or
    name another commit. ``main`` calls it after ``provenance.collect`` (or a
    direct read for ``--report-only``) and before the output directory is
    made. A development run (``checked`` is ``None``) is not checked.

    Parameters
    ----------
    checked : str or None
        The commit returned by ``choose_clean_tree``.
    commit, dirty : str or None, bool or None
        The second git read.

    Raises
    ------
    SeedRefusal
        If ``checked`` is a commit and the second read has another commit, or
        is not clean (a ``dirty`` that is not exactly ``False``, including an
        unreadable state).
    """
    if checked is None:
        return
    if commit != checked or dirty is not False:
        raise SeedRefusal(
            "the git state changed after the check (the commit moved, the tree "
            "became dirty or git became unreadable); no sealed run on a "
            "changed tree"
        )


def choose_seed(
    args: argparse.Namespace,
    extras: list[str],
    registry_path: Path,
    ledger_path: Path = LEDGER_PATH,
) -> tuple[str, int]:
    """Choose the seed id and master seed, or refuse the request.

    Refused: a raw ``--seed``, an unrecognized option (including an
    abbreviation of a real one; the token is never echoed), a development
    seed id that is not in the registry, the confirmatory flag with a
    ``--seed-id`` that is not ``CONF-n``, and a confirmatory request without
    the environment variables or with a seed and salt that do not match the
    latest ledger commitment for the id. With the confirmatory flag and no
    ``--seed-id`` the id is ``CONF-1``: the id only names the commitment that
    the seed from the environment must match, so a pair sealed under another
    id is refused, never run under the wrong id (WU-0038). Values are never
    echoed.

    Parameters
    ----------
    args : argparse.Namespace
        The parsed arguments.
    extras : list[str]
        The tokens the parser did not recognize.
    registry_path, ledger_path : Path
        The seed registry and the ledger.

    Returns
    -------
    tuple[str, int]
        ``(seed_id, seed)``.

    Raises
    ------
    SeedRefusal
        For any of the refusals above.
    """
    if args.seed is not None:
        raise SeedRefusal(
            "a raw integer seed (--seed) is never accepted; use --seed-id DEV-n"
        )
    if extras:
        known = {
            name
            for action in build_parser()._actions
            for name in action.option_strings
        }
        names = sorted(
            {
                e.split("=", 1)[0] if e.split("=", 1)[0] in known else "<value>"
                for e in extras
                if e.startswith("-")
            }
        )
        what = (
            f"unrecognized option(s) {', '.join(names)} (abbreviations are "
            f"disabled)"
            if names
            else "unexpected positional argument(s)"
        )
        raise SeedRefusal(what)
    if args.confirmatory:
        sealed_id = (
            args.seed_id if args.seed_id is not None else CONFIRMATORY_SEED_ID
        )
        return sealed_id, confirmatory_seed(os.environ, ledger_path, sealed_id)
    seed_id = args.seed_id if args.seed_id is not None else DEFAULT_SEED_ID
    return seed_id, resolve_dev_seed(seed_id, load_registry(registry_path))


def main(
    argv: list[str] | None = None,
    *,
    ledger_path: Path = LEDGER_PATH,
    registry_path: Path = REGISTRY_PATH,
) -> int:
    """Run the study for a preset and write results, report and figures.

    Parameters
    ----------
    argv : list[str], optional
        The arguments (default ``sys.argv[1:]``).
    ledger_path, registry_path : Path
        The ledger and the seed registry. Python-only: no flag or environment
        variable can redirect them, so the commitment cannot be redirected
        from the command line.

    Returns
    -------
    int
        0 on success; 64 after a seed refusal (including a confirmatory
        request on a dirty tree or with an unknown commit), with exactly one
        stderr line ``lpcstudy: refused (LPC.PC.7): <reason>`` and before any
        output is created.
    """
    parser = build_parser()
    args, extras = parser.parse_known_args(argv)
    try:
        refine_steps = choose_refine_steps(
            args
        )  # before the seed: a sealed request stops here
        states_dump = choose_states_dump(
            args
        )  # the same: refused before the seed is read
        checked_commit = choose_clean_tree(
            args
        )  # B8: clean tree and known commit, before the seed
        seed_id, seed = choose_seed(args, extras, registry_path, ledger_path)
    except SeedRefusal as refusal:
        return _refuse(refusal.reason)

    config = with_seed(PRESETS[args.preset], seed_id, seed)
    if args.systems:
        config = dataclasses.replace(config, core_systems=tuple(args.systems))
    if (
        refine_steps is not None
    ):  # WU-0005.6: the only knob; the preset's value is the design (15)
        config = dataclasses.replace(
            config,
            estimator_refine_steps=refine_steps,
        )
    out_dir = args.out / config.name
    if not args.report_only:  # read once, before any output exists (LPC.PC.18)
        clock = provenance.RunClock()
        block = provenance.collect(
            config,
            seed_id,
            sys.argv[1:] if argv is None else argv,
            clock,
        )
        if (
            states_dump
        ):  # the one added leaf of a dump run (absent otherwise: 0 added)
            block["states_dump"] = True
    if (
        checked_commit is not None
    ):  # B8: the second read must equal the first, before any output
        now = (
            (block["commit"], block["dirty"])
            if not args.report_only
            else provenance.git_state(provenance.ROOT)[:2]
        )
        try:
            check_tree_unchanged(checked_commit, *now)
        except SeedRefusal as refusal:
            return _refuse(refusal.reason)
    out_dir.mkdir(parents=True, exist_ok=True)
    if args.report_only:
        results = json.loads((out_dir / "results.json").read_text())
        stored = results.get("config", {}).get("estimator_refine_steps")
        if (refine_steps is not None and stored != refine_steps) or (
            refine_steps is None
            and stored is not None
            and stored != config.estimator_refine_steps
        ):
            # The report prints the budget from ``config`` (iterative_label), so
            # a mismatch would label the results with the wrong number of
            # iterations (PRIME.4: refuse, say why).
            return _refuse(
                "--estimator-refine-steps does not match the budget stored in "
                "results.json (pass the stored value)"
            )
        try:
            results["verdicts"] = verdicts(
                results,
                config,
            )  # refuses a pre-v3 file, writes nothing
        except ValueError as stale:
            print(
                f"lpcstudy: refused (stale results schema): {stale}",
                file=sys.stderr,
            )
            return REFUSAL_EXIT
        save_json(results, out_dir / "results.json")
        write_markdown(results, config, out_dir / "RESULTS.md")
        make_figures(results, config, out_dir / "figures")
        return 0
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(out_dir / "run.log"),
            logging.StreamHandler(),
        ],
    )
    log = logging.getLogger("lpcstudy")
    if args.seed_id is None and not args.confirmatory:
        log.info("seed id defaulted to %s", DEFAULT_SEED_ID)
    log.info(
        "provenance: seed id %s, commit %s, dirty %s",
        block["seed_id"],
        block["commit"],
        block["dirty"],
    )
    if block["git_error"]:
        log.warning(
            "git state unavailable, recorded as null: %s",
            block["git_error"],
        )
    missing = [
        name for name, version in block["packages"].items() if version is None
    ]
    if missing:
        log.warning(
            "%d package(s) not installed, recorded as null: %s",
            len(missing),
            ", ".join(missing),
        )
    probe_issues = provenance.probe_errors(block)
    if probe_issues:
        log.warning(
            "%d platform probe failure(s) or fallback(s), recorded in the "
            "provenance "
            "block: %s",
            len(probe_issues),
            "; ".join(probe_issues),
        )
    start = time.time()
    study = Study(config, out_dir)
    if states_dump:
        study.dump = StateDump()
    results: dict = {
        "config": provenance.config_record(config),
        "systems": {},
        "provenance": block,
    }
    for system in config.core_systems:
        results["systems"][system] = run_system(study, system)
        save_json(results, out_dir / "results.json")
    if not args.skip_robustness:
        results["robustness"] = {
            s: run_robustness(study, s)
            for s in config.robustness_systems
            if s in study.core_cells
        }
    results["handling"] = run_handling(
        study,
        results,
    )  # DEF-0001: counts, never silent
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
