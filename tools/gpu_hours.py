#!/usr/bin/env python3
"""Weekly GPU-hour tally from ``run.meta.json`` files (WU-0012.3, LPC.AUTH.3).

The study may use at most 60 hours of GPU time per week (rule LPC.AUTH.3).
Every study run writes a small file called ``run.meta.json`` that records its
device, start time and end time. This tool adds up the GPU time in those files
for the current week and refuses to start a new run that could pass the cap.
``tools/run_preset.sh`` calls it before every preset run; nothing in
``lpcstudy/`` imports it.

Usage::

    python3 -I tools/gpu_hours.py [--root DIR]...
        [--now YYYY-MM-DDTHH:MM:SSZ] sum
    python3 -I tools/gpu_hours.py [--root DIR]... [--now ...] check --hours H

Where it looks (roots). By default it scans ``<worktree>/runs`` for every
worktree in ``git worktree list --porcelain`` (a worktree is one checked-out
copy of the repository; all of them share one tally), plus
``<this repository>/runs``. If git fails, it scans ``<this repository>/runs``
alone and prints a note on stderr. ``--root`` (repeatable) replaces the
default. Every ``**/run.meta.json`` is read once (counted once by resolved
path); symlinks are not followed and ``*.tmp`` files are ignored.

Which week. The current ISO week in UTC, from Monday 00:00Z up to, but not
including, the next Monday 00:00Z. Only runs with ``device == "gpu"`` count.

What a run contributes. The whole seconds of overlap between its
``[start, end)`` interval and the week, so a run that crosses a week boundary
is split. A run whose ``end_utc`` is null or missing (still running, killed or
rebooted) is counted with ``end = min(now, start + 12 h)``, the wrapper's
timeout, which is the conservative choice. These cases are counted as
unreadable and named on stderr (PRIME.4: never skip silently): a directory
that cannot be listed, a file that cannot be read or has another schema or a
malformed field, a run that ends before it starts, and an open run that starts
after ``now``. ``sum`` reports them; ``check`` refuses with exit 65.

Output (stdout, one line)::

    week=2026-W42 gpu_hours=23.5000 gpu_seconds=84600 runs=4 open=2
    cpu_excluded=1 unreadable=0

``runs`` counts the GPU runs that overlap the week, ``open`` counts those among
them without an end, and ``cpu_excluded`` counts the non-GPU runs that overlap
the week.

``check --hours H`` (H from 0 to 12) exits 65 if ``used + H * 3600 s > 60 h``
(exactly 60 h passes), 64 on bad usage, and otherwise 0. H = 12 reserves a
whole run: the wrapper's ``timeout 12h`` bounds every run, so the weekly cap
cannot be passed (LPC.AUTH.3: refer to the owner before the cap).
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
    """A ``run.meta.json`` file (or time string) that cannot be used.

    The message is the reason, and it is printed next to the file name.
    """


@dataclass(frozen=True)
class Run:
    """One run from a meta file.

    Times are epoch seconds (seconds since 1970-01-01 00:00 UTC). ``end`` is
    None while the run is still open.
    """

    device: str
    start: int
    end: int | None


@dataclass
class Tally:
    """The weekly tally and the counts that are reported with it.

    ``unreadable`` holds one ``(path, reason)`` pair for each file or
    directory that could not be used, so none is skipped silently.
    """

    week: str
    seconds: int
    runs: int
    open_runs: int
    cpu_excluded: int
    unreadable: list[tuple[Path, str]]

    def line(self) -> str:
        """Return the one-line report that ``sum`` and ``check`` print."""
        return (
            f"week={self.week} gpu_hours={self.seconds / 3600:.4f} "
            f"gpu_seconds={self.seconds} runs={self.runs} "
            f"open={self.open_runs} cpu_excluded={self.cpu_excluded} "
            f"unreadable={len(self.unreadable)}"
        )


class Parser(argparse.ArgumentParser):
    """An argument parser whose usage errors exit 64 (not argparse's 2).

    Exit 64 is this tool's own code for "bad usage". It lets the wrapper tell
    a bad command line from a refused start (exit 65).
    """

    def error(self, message: str) -> None:  # type: ignore[override]
        """Print the error on one line and exit with status 64."""
        print(f"gpu_hours.py: {message}", file=sys.stderr)
        sys.exit(EXIT_USAGE)


def parse_stamp(text: object) -> int:
    """Return the epoch seconds of a ``YYYY-MM-DDTHH:MM:SSZ`` string.

    Raises
    ------
    BadMeta
        If ``text`` is not a string of exactly that form, or is not a real
        calendar time (for example month 13).
    """
    if not isinstance(text, str) or not STAMP.match(text):
        raise BadMeta(f"time {text!r} is not YYYY-MM-DDTHH:MM:SSZ")
    try:
        return int(
            dt.datetime.strptime(text, FORMAT)
            .replace(tzinfo=dt.timezone.utc)
            .timestamp()
        )
    except ValueError as error:
        raise BadMeta(f"time {text!r} is not a calendar time") from error


def week_bounds(now: int) -> tuple[str, int, int]:
    """Return the ISO week id and its epoch bounds.

    The week runs from Monday 00:00Z up to, but not including, the next
    Monday 00:00Z.

    Parameters
    ----------
    now : int
        Epoch seconds of a moment inside the week.

    Returns
    -------
    tuple
        ``("2026-W42", start, end)``.
    """
    moment = dt.datetime.fromtimestamp(now, dt.timezone.utc)
    year, week, weekday = moment.isocalendar()
    monday = (moment - dt.timedelta(days=weekday - 1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    start = int(monday.timestamp())
    return f"{year}-W{week:02d}", start, start + 7 * 86400


def load_run(path: Path) -> Run:
    """Read one meta file and check that it is usable.

    Raises
    ------
    BadMeta
        With the reason, if the file is a symlink, cannot be read, is not
        JSON, is not an object of schema ``lpcstudy.run-meta/1``, has a device
        other than ``cpu`` or ``gpu``, has a malformed time, or ends before it
        starts.
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
    return Run(device, start, end)


def find_meta_files(
    roots: list[Path],
) -> tuple[list[Path], list[tuple[Path, str]]]:
    """Return every ``run.meta.json`` under the roots, once each.

    Symlinked directories are not followed.

    Returns
    -------
    tuple
        The meta files, and the directories that could not be listed as
        ``(path, reason)`` pairs. The caller counts those as unreadable; they
        are never skipped silently (PRIME.4).
    """
    seen: dict[Path, Path] = {}
    errors: dict[Path, str] = {}

    def on_error(error: OSError) -> None:
        errors.setdefault(
            Path(error.filename or "?"),
            f"directory not readable ({type(error).__name__})",
        )

    for root in roots:
        for directory, _, names in os.walk(
            root, followlinks=False, onerror=on_error
        ):
            if META_NAME in names:
                path = Path(directory) / META_NAME
                seen.setdefault(path.resolve(), path)
    return sorted(seen.values()), sorted(errors.items())


def tally_week(
    files: list[Path], now: int, walk_errors: list[tuple[Path, str]]
) -> Tally:
    """Sum the GPU seconds of the ISO week of ``now`` over the meta files.

    Parameters
    ----------
    files : list of Path
        Meta files, each counted once.
    now : int
        Epoch seconds; it picks the week and bounds the open runs.
    walk_errors : list
        Directories that could not be listed; they start the ``unreadable``
        list.
    """
    week, week_start, week_end = week_bounds(now)
    total = runs = open_runs = cpu_excluded = 0
    unreadable: list[tuple[Path, str]] = list(walk_errors)
    for path in files:
        try:
            run = load_run(path)
            if run.end is None and run.start > now:
                raise BadMeta("open run starts after now")
        except BadMeta as error:
            unreadable.append((path, str(error)))
            continue
        end = (
            run.end
            if run.end is not None
            else min(now, run.start + RUN_LIMIT_SECONDS)
        )
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

    If git fails, return only ``<repo>/runs`` and print a note on stderr.
    """
    roots = [repo / "runs"]
    try:
        done = subprocess.run(
            ["git", "-C", str(repo), "worktree", "list", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        done = None
    if done is None or done.returncode != 0:
        print(
            f"note: git worktree list failed; scanning only {repo / 'runs'}",
            file=sys.stderr,
        )
        return roots
    for line in done.stdout.splitlines():
        if line.startswith("worktree "):
            roots.append(Path(line[len("worktree ") :]) / "runs")
    return roots


def existing_roots(roots: list[Path]) -> list[Path]:
    """Keep the roots that are directories.

    A missing ``runs/`` (a worktree that has not run anything yet) holds no
    meta file, so nothing is lost by leaving it out. An explicit ``--root``
    that is missing is refused in ``main``. A root listed twice is harmless,
    because ``find_meta_files`` counts each file once.
    """
    return [root for root in roots if root.is_dir()]


def parse_hours(text: str) -> Decimal:
    """Return the hours to reserve as an exact decimal in [0, 12].

    Decimal (rather than float) keeps the cap comparison exact.

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
    parser = Parser(
        description=(
            "Weekly GPU-hour tally from ``run.meta.json`` files "
            "(WU-0012.3, LPC.AUTH.3, DEVELOPMENT_WORKFLOW 4.5)."
        )
    )
    parser.add_argument(
        "--root",
        action="append",
        default=None,
        type=Path,
        metavar="DIR",
        help="directory to scan (repeatable); default: runs/ of every worktree",
    )
    parser.add_argument(
        "--now",
        default=None,
        metavar="ISO",
        help=(
            "current time YYYY-MM-DDTHH:MM:SSZ "
            "(tests only; the wrapper never passes it)"
        ),
    )
    sub = parser.add_subparsers(
        dest="command", required=True, parser_class=Parser
    )
    sub.add_parser("sum", help="report this week's GPU hours")
    check = sub.add_parser(
        "check", help="exit 65 if a start of H hours would pass 60 h"
    )
    check.add_argument(
        "--hours", required=True, help="hours to reserve, 0 to 12"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the tool and return the exit code.

    The codes are 0 (fine), 64 (bad usage) and 65 (the cap would be passed,
    or some file could not be read so the tally is not trustworthy).
    """
    args = build_parser().parse_args(argv)
    try:
        now = (
            int(dt.datetime.now(dt.timezone.utc).timestamp())
            if args.now is None
            else parse_stamp(args.now)
        )
        hours = (
            parse_hours(args.hours) if args.command == "check" else Decimal(0)
        )
    except (BadMeta, ValueError) as error:
        print(f"gpu_hours.py: {error}", file=sys.stderr)
        return EXIT_USAGE
    if args.root:
        missing = [str(r) for r in args.root if not r.is_dir()]
        if missing:
            print(
                "gpu_hours.py: --root is not a directory: "
                f"{', '.join(missing)}",
                file=sys.stderr,
            )
            return EXIT_USAGE
        roots = existing_roots(args.root)
    else:
        repo = Path(__file__).resolve().parents[1]
        roots = existing_roots(default_roots(repo))
    files, walk_errors = find_meta_files(roots)
    result = tally_week(files, now, walk_errors)
    print(result.line())
    for path, reason in result.unreadable:
        print(f"unreadable: {path}: {reason}", file=sys.stderr)
    if args.command == "sum":
        return 0
    if result.unreadable:
        print(
            f"refused: {len(result.unreadable)} unreadable file(s) or "
            "directory(ies), named above: "
            "the tally is not trustworthy (fail closed)",
            file=sys.stderr,
        )
        return EXIT_CAP
    needed = Decimal(result.seconds) + hours * 3600
    if needed > CAP_SECONDS:
        print(
            f"refused: {result.seconds / 3600:.2f} h used this week "
            f"({result.week}) + {hours} h "
            "reserved > 60 h weekly GPU cap (LPC.AUTH.3): refer before the cap",
            file=sys.stderr,
        )
        return EXIT_CAP
    return 0


if __name__ == "__main__":
    sys.exit(main())
