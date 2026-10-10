#!/usr/bin/env python3
"""Weekly GPU-hour tally from ``run.meta.json`` files (WU-0012.3, LPC.AUTH.3, DEVELOPMENT_WORKFLOW 4.5).

Usage::

    python3 -I tools/gpu_hours.py [--root DIR]... [--now YYYY-MM-DDTHH:MM:SSZ] sum
    python3 -I tools/gpu_hours.py [--root DIR]... [--now ...] check --hours H

Roots. The default is ``<worktree>/runs`` for every worktree in ``git worktree list --porcelain``,
because all worktrees share one tally (section 3), plus ``<this repository>/runs``. If git fails,
it is ``<this repository>/runs`` alone, with a note on stderr. ``--root`` (repeatable) replaces
the default. Every ``**/run.meta.json`` is read (symlinks are not followed; ``*.tmp`` files are
ignored) and counted once by resolved path.

Week. The current ISO week in UTC, ``[Monday 00:00Z, next Monday 00:00Z)``. Only runs with
``device == "gpu"`` count.

Contribution. The integer-second overlap of ``[start, end)`` with the week. A run that crosses a
week boundary is split. A run with ``end_utc`` null or missing (running, killed or rebooted) is
counted with ``end = min(now, start + 12 h)``, the timeout bound (conservative). A directory that
cannot be listed, a file that is unreadable, has another schema, a malformed field or an end before
the start, and an open run that starts after ``now`` are counted as unreadable and named on stderr
(PRIME.4): ``sum`` reports them and ``check`` refuses with exit 65.

Output (stdout, one line): ``week=2026-W42 gpu_hours=23.5000 gpu_seconds=84600 runs=4 open=2
cpu_excluded=1 unreadable=0``. ``runs`` counts the GPU runs that overlap the week, ``open`` those
among them without an end, ``cpu_excluded`` the non-GPU runs that overlap the week.

``check --hours H`` (H from 0 to 12) exits 65 if ``used + H * 3600 s > 60 h`` (exactly 60 h passes),
64 on bad usage, else 0. H = 12 reserves a whole run, because the wrapper's ``timeout 12h`` bounds
a run, so the weekly cap cannot be passed (LPC.AUTH.3: refer before the cap).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

SCHEMA = "lpcstudy.run-meta/1"
META_NAME = "run.meta.json"
CAP_SECONDS = 60 * 3600
RUN_LIMIT_SECONDS = 12 * 3600
MAX_HOURS = Decimal(12)
FORMAT = "%Y-%m-%dT%H:%M:%SZ"
STAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
EXIT_USAGE = 64
EXIT_CAP = 65


class BadMeta(Exception):
    """A run.meta.json file that cannot be used; the message is the reason."""


@dataclass(frozen=True)
class Run:
    """One run from a meta file: epoch seconds, with ``end`` None while open."""

    path: Path
    device: str
    start: int
    end: int | None


@dataclass
class Tally:
    """The weekly tally and the counts reported with it."""

    week: str
    seconds: int
    runs: int
    open_runs: int
    cpu_excluded: int
    unreadable: list[tuple[Path, str]]

    def line(self) -> str:
        """Return the one-line report."""
        return (f"week={self.week} gpu_hours={self.seconds / 3600:.4f} gpu_seconds={self.seconds} "
                f"runs={self.runs} open={self.open_runs} cpu_excluded={self.cpu_excluded} "
                f"unreadable={len(self.unreadable)}")


class Parser(argparse.ArgumentParser):
    """An argument parser whose usage errors exit 64 (not argparse's 2)."""

    def error(self, message: str) -> None:  # type: ignore[override]
        """Print the error on one line and exit 64."""
        print(f"gpu_hours.py: {message}", file=sys.stderr)
        sys.exit(EXIT_USAGE)


def parse_stamp(text: object) -> int:
    """Return the epoch seconds of a ``YYYY-MM-DDTHH:MM:SSZ`` string.

    Raises
    ------
    BadMeta
        If ``text`` is not a string of exactly that form or is not a calendar time.
    """
    if not isinstance(text, str) or not STAMP.match(text):
        raise BadMeta(f"time {text!r} is not YYYY-MM-DDTHH:MM:SSZ")
    try:
        return int(dt.datetime.strptime(text, FORMAT).replace(tzinfo=dt.timezone.utc).timestamp())
    except ValueError as error:
        raise BadMeta(f"time {text!r} is not a calendar time") from error


def week_bounds(now: int) -> tuple[str, int, int]:
    """Return the ISO week id and the epoch bounds ``[Monday 00:00Z, next Monday 00:00Z)``.

    Parameters
    ----------
    now : int
        Epoch seconds.

    Returns
    -------
    tuple
        ``("2026-W42", start, end)``.
    """
    moment = dt.datetime.fromtimestamp(now, dt.timezone.utc)
    year, week, weekday = moment.isocalendar()
    monday = (moment - dt.timedelta(days=weekday - 1)).replace(hour=0, minute=0, second=0,
                                                              microsecond=0)
    start = int(monday.timestamp())
    return f"{year}-W{week:02d}", start, start + 7 * 86400


def load_run(path: Path) -> Run:
    """Read and validate one meta file.

    Raises
    ------
    BadMeta
        With the reason, if the file is a symlink, unreadable, not JSON, not an object of schema
        ``lpcstudy.run-meta/1``, has a device other than ``cpu``/``gpu``, a malformed time, or an
        end before the start.
    """
    if path.is_symlink():
        raise BadMeta("is a symlink (not followed)")
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError) as error:
        raise BadMeta(f"unreadable ({type(error).__name__})") from error
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        raise BadMeta(f"schema is not {SCHEMA}")
    device = data.get("device")
    if device not in ("cpu", "gpu"):
        raise BadMeta(f"device {device!r} is not cpu or gpu")
    start = parse_stamp(data.get("start_utc"))
    end = None if data.get("end_utc") is None else parse_stamp(data["end_utc"])
    if end is not None and end < start:
        raise BadMeta("end_utc is before start_utc")
    return Run(path, device, start, end)


def find_meta_files(roots: list[Path]) -> tuple[list[Path], list[tuple[Path, str]]]:
    """Return every ``run.meta.json`` under the roots (symlinked directories not followed), once each.

    Returns
    -------
    tuple
        The meta files, and the directories that could not be listed as ``(path, reason)``: those
        are counted as unreadable by the caller, never skipped silently (PRIME.4).
    """
    seen: dict[Path, Path] = {}
    errors: dict[Path, str] = {}

    def on_error(error: OSError) -> None:
        errors.setdefault(Path(error.filename or "?"), f"directory not readable ({type(error).__name__})")

    for root in roots:
        for directory, _, names in os.walk(root, followlinks=False, onerror=on_error):
            if META_NAME in names:
                path = Path(directory) / META_NAME
                seen.setdefault(path.resolve(), path)
    return sorted(seen.values()), sorted(errors.items())


def tally_week(files: list[Path], now: int,
               walk_errors: list[tuple[Path, str]] | None = None) -> Tally:
    """Sum the GPU seconds of the ISO week of ``now`` over the given meta files.

    Parameters
    ----------
    files : list of Path
        Meta files, each counted once.
    now : int
        Epoch seconds; bounds the week and the open runs.
    walk_errors : list, optional
        Directories that could not be listed; they start the ``unreadable`` list.
    """
    week, week_start, week_end = week_bounds(now)
    total = runs = open_runs = cpu_excluded = 0
    unreadable: list[tuple[Path, str]] = list(walk_errors or [])
    for path in files:
        try:
            run = load_run(path)
            if run.end is None and run.start > now:
                raise BadMeta("open run starts after now")
        except BadMeta as error:
            unreadable.append((path, str(error)))
            continue
        end = run.end if run.end is not None else min(now, run.start + RUN_LIMIT_SECONDS)
        overlap = max(0, min(end, week_end) - max(run.start, week_start))
        if run.device != "gpu":
            cpu_excluded += overlap > 0
            continue
        if overlap > 0:
            runs += 1
            open_runs += run.end is None
            total += overlap
    return Tally(week, total, runs, open_runs, cpu_excluded, unreadable)


def default_roots(repo: Path) -> list[Path]:
    """Return ``<worktree>/runs`` for every git worktree, plus ``<repo>/runs``.

    If git fails, only ``<repo>/runs``, with a note on stderr.
    """
    roots = [repo / "runs"]
    try:
        done = subprocess.run(["git", "-C", str(repo), "worktree", "list", "--porcelain"],
                              capture_output=True, text=True, timeout=30, check=False)
    except (OSError, subprocess.TimeoutExpired):
        done = None
    if done is None or done.returncode != 0:
        print(f"note: git worktree list failed; scanning only {repo / 'runs'}", file=sys.stderr)
        return roots
    for line in done.stdout.splitlines():
        if line.startswith("worktree "):
            roots.append(Path(line[len("worktree "):]) / "runs")
    return roots


def existing_roots(roots: list[Path]) -> list[Path]:
    """Keep the roots that are directories, once each by resolved path.

    A missing ``runs/`` (a worktree that has not run anything yet) holds no meta file, so nothing
    is dropped by leaving it out. An explicit ``--root`` that is missing is refused in ``main``.
    """
    kept: dict[Path, Path] = {}
    for root in roots:
        if root.is_dir():
            kept.setdefault(root.resolve(), root)
    return list(kept.values())


def parse_hours(text: str) -> Decimal:
    """Return H as a decimal in [0, 12].

    Raises
    ------
    ValueError
        If ``text`` is not a finite number in that range.
    """
    try:
        value = Decimal(text)
    except InvalidOperation as error:
        raise ValueError(f"--hours {text!r} is not a number") from error
    if not value.is_finite() or value < 0 or value > MAX_HOURS:
        raise ValueError(f"--hours {text!r} must be in [0, 12]")
    return value


def build_parser() -> argparse.ArgumentParser:
    """Return the command-line parser."""
    parser = Parser(description=__doc__.split("\n")[0])
    parser.add_argument("--root", action="append", default=None, type=Path, metavar="DIR",
                        help="directory to scan (repeatable); default: runs/ of every worktree")
    parser.add_argument("--now", default=None, metavar="ISO",
                        help="current time YYYY-MM-DDTHH:MM:SSZ (tests only; the wrapper never passes it)")
    sub = parser.add_subparsers(dest="command", required=True, parser_class=Parser)
    sub.add_parser("sum", help="report this week's GPU hours")
    check = sub.add_parser("check", help="exit 65 if a start of H hours would pass 60 h")
    check.add_argument("--hours", required=True, help="hours to reserve, 0 to 12")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the tool; return the exit code (0, 64 usage, 65 cap or unreadable file)."""
    args = build_parser().parse_args(argv)
    try:
        now = int(dt.datetime.now(dt.timezone.utc).timestamp()) if args.now is None \
            else parse_stamp(args.now)
        hours = parse_hours(args.hours) if args.command == "check" else Decimal(0)
    except (BadMeta, ValueError) as error:
        print(f"gpu_hours.py: {error}", file=sys.stderr)
        return EXIT_USAGE
    if args.root:
        missing = [str(r) for r in args.root if not r.is_dir()]
        if missing:
            print(f"gpu_hours.py: --root is not a directory: {', '.join(missing)}", file=sys.stderr)
            return EXIT_USAGE
        roots = existing_roots(args.root)
    else:
        roots = existing_roots(default_roots(Path(__file__).resolve().parents[1]))
    files, walk_errors = find_meta_files(roots)
    result = tally_week(files, now, walk_errors)
    print(result.line())
    for path, reason in result.unreadable:
        print(f"unreadable: {path}: {reason}", file=sys.stderr)
    if args.command == "sum":
        return 0
    if result.unreadable:
        print(f"refused: {len(result.unreadable)} unreadable file(s) or directory(ies), named above: "
              "the tally is not trustworthy (fail closed)", file=sys.stderr)
        return EXIT_CAP
    needed = Decimal(result.seconds) + hours * 3600
    if needed > CAP_SECONDS:
        print(f"refused: {result.seconds / 3600:.2f} h used this week ({result.week}) + {hours} h "
              f"reserved > 60 h weekly GPU cap (LPC.AUTH.3): refer before the cap", file=sys.stderr)
        return EXIT_CAP
    return 0


if __name__ == "__main__":
    sys.exit(main())
