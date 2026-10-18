"""Tests of ``tools/gpu_hours.py``, the weekly GPU-hour tally (WU-0012.3).

The study may use at most 60 GPU-hours per week (rule LPC.AUTH.3). The tool adds
up the GPU time recorded in ``run.meta.json`` files and refuses to start a run
that could pass the cap. ``tools/run_preset.sh`` calls it before every preset
run. These tests check the sums, the week boundaries, the cap boundary, the
handling of unreadable files, and the wrapper's use of the tool.

Reference for every test: a hand sum, in integer seconds, of a fixture tree of
``run.meta.json`` files, written literally in the docstring or comment of each
test. The calendar facts were checked by hand against
``datetime.date.isocalendar``: 2026-10-12 is a Monday of 2026-W42, 2026-12-28 is
the Monday of 2026-W53, and 2027-01-04 is the Monday of 2027-W01. None of the
expected values comes from the tool. The tool runs as a subprocess with
``python3 -I`` semantics (``sys.executable -I``), as the wrapper calls it.

Tolerance: none. All times have whole-second resolution, so the sums are exact
integers and the comparison is equality. The cap boundary is tested at exactly
60 h (passes) and at 60 h + 1 s (refuses). The wrapper tests (n) use the fake
root of ``wrapper_helpers.FakeRoot`` with a recording fake ``gpu_hours.py``, a
fake lock and a fake interpreter. The real tally is used only with
date-independent trees (empty, or one corrupt file), because the wrapper never
passes ``--now``.
"""

from __future__ import annotations

import fcntl
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from wrapper_helpers import REPO, FakeRoot

TOOL = REPO / "tools" / "gpu_hours.py"
NOW = "2026-10-14T12:00:00Z"  # Wednesday of 2026-W42 (Monday 2026-10-12 00:00Z)


def write_meta(
    path: Path,
    start: str,
    end: str | None,
    device: str = "gpu",
    **extra: object,
) -> Path:
    """Write a ``run.meta.json`` (schema ``lpcstudy.run-meta/1``) and return its
    path.

    ``end=None`` writes a null end time, which means the run is still open.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "schema": "lpcstudy.run-meta/1",
        "preset": "pilot",
        "seed_id": "DEV-1",
        "start_utc": start,
        "end_utc": end,
        "device": device,
        "wall_seconds": None,
        "exit_code": None,
        **extra,
    }
    path.write_text(json.dumps(data))
    return path


def gpu_hours(*args: str) -> subprocess.CompletedProcess[str]:
    """Run the real tool with ``python -I`` and return the completed process."""
    return subprocess.run(
        [sys.executable, "-I", str(TOOL), *args],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def fields(done: subprocess.CompletedProcess[str]) -> dict[str, str]:
    """Parse the one stdout line ``key=value ...`` into a dictionary.

    Also checks that the output is exactly one line.
    """
    lines = done.stdout.strip().splitlines()
    assert len(lines) == 1, done.stdout
    return dict(part.split("=", 1) for part in lines[0].split())


def test_tool_is_executable() -> None:
    """The script exists and has the executable bit (reference: ``os.stat``)."""
    assert os.access(TOOL, os.X_OK)


def test_weekly_sum_matches_a_hand_sum(tmp_path: Path) -> None:
    """Two roots, nested directories and a fixed "now" (a Wednesday of 2026-W42)
    (l).

    ``--now 2026-10-14T12:00:00Z`` is a Wednesday. The week is
    [2026-10-12T00:00Z, 2026-10-19T00:00Z). Hand sums in integer seconds:

    * A: gpu 10-12T08:00Z to 10:30Z, inside the week: 9000.
    * B: gpu 10-11T20:00Z to 10-12T04:00Z, crosses in on Sunday night: only
      00:00 to 04:00 counts, 14400.
    * C: gpu, open (end null), started 5 h before now (07:00Z): end = min(now,
      start + 12 h) = now, 18000.
    * D: gpu, open (no ``end_utc`` key), started 20 h before now (10-13T16:00Z):
      end = start + 12 h = 10-14T04:00Z (capped), 43200.
    * E: cpu, 10 h inside the week: 0, counted as cpu_excluded.
    * F: gpu on 10-05 (previous week): 0, not a run of this week.
    * G: ``run.meta.json.tmp``, gpu inside the week: ignored.

    Total 9000 + 14400 + 18000 + 43200 = 84600 s = 23.5 h; runs 4, open 2,
    cpu_excluded 1, unreadable 0. With a second ``--now`` in the next week
    (2026-10-19T03:00Z, 2026-W43) every run is in the previous week: all 0.
    """
    one, two = tmp_path / "one", tmp_path / "two"
    write_meta(
        one / "dev" / "DEV-1" / "pilot" / "run.meta.json",
        "2026-10-12T08:00:00Z",
        "2026-10-12T10:30:00Z",
    )
    write_meta(
        one / "a" / "b" / "run.meta.json",
        "2026-10-11T20:00:00Z",
        "2026-10-12T04:00:00Z",
    )
    write_meta(one / "c" / "run.meta.json", "2026-10-14T07:00:00Z", None)
    deep = two / "x" / "y" / "z"
    path = write_meta(deep / "run.meta.json", "2026-10-13T16:00:00Z", None)
    data = json.loads(path.read_text())
    del data["end_utc"]
    path.write_text(json.dumps(data))
    write_meta(
        two / "cpu" / "run.meta.json",
        "2026-10-13T00:00:00Z",
        "2026-10-13T10:00:00Z",
        device="cpu",
    )
    write_meta(
        two / "old" / "run.meta.json",
        "2026-10-05T10:00:00Z",
        "2026-10-05T20:00:00Z",
    )
    write_meta(
        two / "tmp" / "run.meta.json.tmp",
        "2026-10-13T00:00:00Z",
        "2026-10-13T20:00:00Z",
    )
    roots = ["--root", str(one), "--root", str(two)]

    done = gpu_hours(*roots, "--now", NOW, "sum")
    assert done.returncode == 0, done.stderr
    assert fields(done) == {
        "week": "2026-W42",
        "gpu_hours": "23.5000",
        "gpu_seconds": "84600",
        "runs": "4",
        "open": "2",
        "cpu_excluded": "1",
        "unreadable": "0",
    }
    later = gpu_hours(*roots, "--now", "2026-10-19T03:00:00Z", "sum")
    assert fields(later) == {
        "week": "2026-W43",
        "gpu_hours": "0.0000",
        "gpu_seconds": "0",
        "runs": "0",
        "open": "0",
        "cpu_excluded": "0",
        "unreadable": "0",
    }


def test_run_crossing_the_end_boundary_is_split(tmp_path: Path) -> None:
    """A run over a week boundary counts 2 h in each week.

    The run is from Sunday 2026-10-18T22:00Z to Monday 10-19T02:00Z. Hand sum:
    W42 gets [22:00, 24:00) = 7200 s, and W43 gets [00:00, 02:00) = 7200 s. The
    run is closed, so ``--now`` only selects the week.
    """
    write_meta(
        tmp_path / "r" / "run.meta.json",
        "2026-10-18T22:00:00Z",
        "2026-10-19T02:00:00Z",
    )
    first = fields(
        gpu_hours(
            "--root", str(tmp_path), "--now", "2026-10-18T23:00:00Z", "sum"
        )
    )
    second = fields(
        gpu_hours(
            "--root", str(tmp_path), "--now", "2026-10-19T03:00:00Z", "sum"
        )
    )
    assert (first["week"], first["gpu_seconds"]) == ("2026-W42", "7200")
    assert (second["week"], second["gpu_seconds"]) == ("2026-W43", "7200")


def test_iso_week_53_and_year_boundary(tmp_path: Path) -> None:
    """The ISO week 53 and the year boundary are handled (l).

    ``--now 2027-01-02T12:00:00Z`` is 2026-W53, which starts on Monday
    2026-12-28. Hand sums: X, gpu 2026-12-27T22:00Z to 12-28T03:00Z, counts
    03:00 only, 10800 s; Y, gpu 2027-01-01T00:00Z to 01:00Z (Friday of W53),
    3600 s; Z, gpu on 2026-12-20 (W51), 0. Total 14400. On Monday 2027-01-04
    (``--now 2027-01-04T12:00:00Z``, 2027-W01) only V, gpu 2027-01-04T01:00Z to
    02:00Z, counts: 3600.
    """
    write_meta(
        tmp_path / "x" / "run.meta.json",
        "2026-12-27T22:00:00Z",
        "2026-12-28T03:00:00Z",
    )
    write_meta(
        tmp_path / "y" / "run.meta.json",
        "2027-01-01T00:00:00Z",
        "2027-01-01T01:00:00Z",
    )
    write_meta(
        tmp_path / "z" / "run.meta.json",
        "2026-12-20T10:00:00Z",
        "2026-12-20T20:00:00Z",
    )
    write_meta(
        tmp_path / "v" / "run.meta.json",
        "2027-01-04T01:00:00Z",
        "2027-01-04T02:00:00Z",
    )
    old = fields(
        gpu_hours(
            "--root", str(tmp_path), "--now", "2027-01-02T12:00:00Z", "sum"
        )
    )
    new = fields(
        gpu_hours(
            "--root", str(tmp_path), "--now", "2027-01-04T12:00:00Z", "sum"
        )
    )
    assert (old["week"], old["gpu_seconds"], old["runs"]) == (
        "2026-W53",
        "14400",
        "2",
    )
    assert (new["week"], new["gpu_seconds"], new["runs"]) == (
        "2027-W01",
        "3600",
        "1",
    )


def test_monday_midnight_belongs_to_the_new_week(tmp_path: Path) -> None:
    """A run ending exactly at Monday 00:00Z adds 0 to the new week.

    A run starting there is counted. Hand sum: the interval is half-open,
    ``[start, end)``. So [10-11T23:00, 10-12T00:00) is last week (0), and
    [10-12T00:00, 10-12T01:00) is 3600 s.
    """
    write_meta(
        tmp_path / "a" / "run.meta.json",
        "2026-10-11T23:00:00Z",
        "2026-10-12T00:00:00Z",
    )
    write_meta(
        tmp_path / "b" / "run.meta.json",
        "2026-10-12T00:00:00Z",
        "2026-10-12T01:00:00Z",
    )
    done = fields(gpu_hours("--root", str(tmp_path), "--now", NOW, "sum"))
    assert (done["gpu_seconds"], done["runs"]) == ("3600", "1")


def test_overlapping_roots_count_each_file_once(tmp_path: Path) -> None:
    """The same root twice, and a root nested in another, count one run once.

    The run is 3600 s long.
    """
    write_meta(
        tmp_path / "r" / "n" / "run.meta.json",
        "2026-10-12T00:00:00Z",
        "2026-10-12T01:00:00Z",
    )
    done = fields(
        gpu_hours(
            "--root",
            str(tmp_path / "r"),
            "--root",
            str(tmp_path / "r"),
            "--root",
            str(tmp_path / "r" / "n"),
            "--now",
            NOW,
            "sum",
        )
    )
    assert (done["gpu_seconds"], done["runs"]) == ("3600", "1")


def exact_run(tmp_path: Path, seconds: int) -> list[str]:
    """Write one closed gpu run of ``seconds`` from Monday 2026-10-12T00:00Z.

    Returns the command-line options (root and "now") to use with it.
    """
    end = (
        datetime(2026, 10, 12, tzinfo=timezone.utc) + timedelta(seconds=seconds)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")
    write_meta(tmp_path / "r" / "run.meta.json", "2026-10-12T00:00:00Z", end)
    return ["--root", str(tmp_path), "--now", "2026-10-16T00:00:00Z"]


@pytest.mark.parametrize(
    ("used", "hours", "code"),
    [
        (60 * 3600, "0", 0),
        (60 * 3600 + 1, "0", 65),
        (48 * 3600, "12", 0),
        (48 * 3600 + 1, "12", 65),
        (49 * 3600, "12", 65),
        (59 * 3600, "1", 0),
        (59 * 3600 + 1, "1", 65),
        (0, "12", 0),
        (0, "0", 0),
    ],
)
def test_check_boundary_at_exactly_60_hours(
    tmp_path: Path, used: int, hours: str, code: int
) -> None:
    """Used time plus reserved time above 216000 s refuses (65); exactly 60 h
    passes (m).

    Reference: the arithmetic of LPC.AUTH.3 (60 h = 216000 s). One run of
    ``used`` seconds starts on Monday 2026-10-12T00:00Z. The cases bracket the
    boundary by 1 s on both sides. Exit 65 prints one stderr reason line.
    """
    options = (
        exact_run(tmp_path, used)
        if used
        else ["--root", str(tmp_path), "--now", NOW]
    )
    done = gpu_hours(*options, "check", "--hours", hours)
    assert done.returncode == code, (done.stdout, done.stderr)
    assert fields(done)["gpu_seconds"] == str(used)
    if code == 65:
        assert "refused" in done.stderr and "60 h" in done.stderr


@pytest.mark.parametrize(
    "hours", ["13", "12.0001", "-1", "abc", "nan", "inf", ""]
)
def test_check_rejects_hours_outside_0_to_12(
    tmp_path: Path, hours: str
) -> None:
    """The hours to reserve must be a number in [0, 12]; otherwise exit 64 (m).

    The tool prints one stderr line.
    """
    done = gpu_hours(
        "--root", str(tmp_path), "--now", NOW, "check", "--hours", hours
    )
    assert done.returncode == 64
    assert len(done.stderr.strip().splitlines()) == 1


@pytest.mark.parametrize(
    "args",
    [
        [],
        ["check"],
        ["frobnicate"],
        ["--now", "yesterday", "sum"],
        ["--now", "2026-13-40T00:00:00Z", "sum"],
        ["--root", "/nonexistent-dir-xyz", "sum"],
    ],
)
def test_usage_errors_exit_64(args: list[str]) -> None:
    """Bad usage exits 64.

    Bad usage means a missing subcommand or ``--hours``, an unknown subcommand,
    a bad ``--now`` or a missing root.
    """
    done = gpu_hours(*args)
    assert done.returncode == 64, done.stderr


def corrupt_cases() -> list[tuple[str, str]]:
    """Return the name and file text of each unusable meta file.

    They are built independently of the tool.
    """
    good = {
        "schema": "lpcstudy.run-meta/1",
        "device": "gpu",
        "start_utc": "2026-10-12T08:00:00Z",
        "end_utc": "2026-10-12T09:00:00Z",
    }
    return [
        ("invalid-json", "{not json"),
        ("not-an-object", "[]"),
        ("wrong-schema", json.dumps({**good, "schema": "lpcstudy.run-meta/2"})),
        (
            "no-schema",
            json.dumps({k: v for k, v in good.items() if k != "schema"}),
        ),
        ("bad-device", json.dumps({**good, "device": "tpu"})),
        (
            "missing-start",
            json.dumps({k: v for k, v in good.items() if k != "start_utc"}),
        ),
        (
            "bad-time-format",
            json.dumps({**good, "start_utc": "2026-10-12 08:00:00"}),
        ),
        (
            "not-a-calendar-time",
            json.dumps({**good, "start_utc": "2026-13-45T08:00:00Z"}),
        ),
        (
            "end-before-start",
            json.dumps({**good, "end_utc": "2026-10-12T07:59:59Z"}),
        ),
        (
            "open-run-in-the-future",
            json.dumps(
                {**good, "end_utc": None, "start_utc": "2026-10-14T12:00:01Z"}
            ),
        ),
    ]


@pytest.mark.parametrize(
    ("name", "text"), corrupt_cases(), ids=[n for n, _ in corrupt_cases()]
)
def test_unusable_file_is_counted_named_and_refuses_check(
    tmp_path: Path, name: str, text: str
) -> None:
    """An unusable file is counted and named by ``sum`` (exit 0), and ``check``
    refuses (65) (m).

    Reference: PRIME.4 and the plan: a file is never skipped silently. A valid
    3600 s run beside it still counts: the corrupt file does not hide it.
    """
    bad = tmp_path / name / "run.meta.json"
    bad.parent.mkdir()
    bad.write_text(text)
    write_meta(
        tmp_path / "ok" / "run.meta.json",
        "2026-10-12T08:00:00Z",
        "2026-10-12T09:00:00Z",
    )
    options = ["--root", str(tmp_path), "--now", NOW]
    summed = gpu_hours(*options, "sum")
    assert summed.returncode == 0
    assert (fields(summed)["unreadable"], fields(summed)["gpu_seconds"]) == (
        "1",
        "3600",
    )
    assert str(bad) in summed.stderr
    checked = gpu_hours(*options, "check", "--hours", "0")
    assert checked.returncode == 65
    assert str(bad) in checked.stderr


def test_symlinked_meta_is_not_followed_and_is_reported(tmp_path: Path) -> None:
    """A symlinked ``run.meta.json`` is not read; it counts as unreadable.

    It is not skipped silently.
    """
    real = write_meta(
        tmp_path / "real.json", "2026-10-12T08:00:00Z", "2026-10-12T09:00:00Z"
    )
    link = tmp_path / "d" / "run.meta.json"
    link.parent.mkdir()
    link.symlink_to(real)
    done = gpu_hours("--root", str(tmp_path), "--now", NOW, "sum")
    assert (fields(done)["unreadable"], fields(done)["gpu_seconds"]) == (
        "1",
        "0",
    )
    assert str(link) in done.stderr


@pytest.mark.skipif(
    os.geteuid() == 0,
    reason="root ignores directory permissions, so chmod 000 hides nothing",
)
def test_unreadable_directory_is_counted_named_and_refuses_check(
    tmp_path: Path,
) -> None:
    """A directory that cannot be listed is counted as unreadable (R2).

    ``check`` refuses it too.

    Reference: PRIME.4 and the tool's own contract (nothing is skipped
    silently). Hand sums: two gpu runs of 10 h (36000 s each) inside the week.
    With one directory at mode 000, only the other is visible: 36000 s, with
    unreadable=1. Before the fix the result was 36000 s and unreadable=0, exit 0
    on ``check --hours 12``, which was a silent under-count of 10 h. Permissions
    are restored afterwards.
    """
    write_meta(
        tmp_path / "seen" / "run.meta.json",
        "2026-10-12T00:00:00Z",
        "2026-10-12T10:00:00Z",
    )
    hidden = tmp_path / "hidden"
    write_meta(
        hidden / "run.meta.json", "2026-10-13T00:00:00Z", "2026-10-13T10:00:00Z"
    )
    options = ["--root", str(tmp_path), "--now", NOW]
    hidden.chmod(0)
    try:
        summed = gpu_hours(*options, "sum")
        checked = gpu_hours(*options, "check", "--hours", "12")
    finally:
        hidden.chmod(0o755)
    assert summed.returncode == 0
    assert (fields(summed)["gpu_seconds"], fields(summed)["unreadable"]) == (
        "36000",
        "1",
    )
    assert str(hidden) in summed.stderr
    assert checked.returncode == 65
    assert str(hidden) in checked.stderr


def run_git(cwd: Path, *args: str) -> None:
    """Run git offline with a fixed identity and no global configuration."""
    env = {
        **os.environ,
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@t",
    }
    subprocess.run(
        ["git", *args], cwd=cwd, env=env, check=True, capture_output=True
    )


def test_default_roots_are_the_runs_of_every_worktree(tmp_path: Path) -> None:
    """Without ``--root`` the tool counts ``runs/`` of every worktree.

    That means the main worktree and a linked one.

    Reference: the plan ("all worktrees share one tally"). Hand sum: 3600 s in
    the main worktree plus 7200 s in the linked one is 10800 s, in 2 runs. The
    tool is copied into the repository so that it finds its root from its own
    path.
    """
    repo, other = tmp_path / "repo", tmp_path / "other"
    (repo / "tools").mkdir(parents=True)
    (repo / "tools" / "gpu_hours.py").write_text(TOOL.read_text())
    run_git(repo, "init", "-q", "-b", "main")
    run_git(repo, "add", "tools")
    run_git(repo, "commit", "-q", "-m", "x")
    run_git(repo, "worktree", "add", "-q", "-b", "side", str(other))
    write_meta(
        repo / "runs" / "a" / "run.meta.json",
        "2026-10-12T00:00:00Z",
        "2026-10-12T01:00:00Z",
    )
    write_meta(
        other / "runs" / "b" / "run.meta.json",
        "2026-10-12T00:00:00Z",
        "2026-10-12T02:00:00Z",
    )
    done = subprocess.run(
        [
            sys.executable,
            "-I",
            str(repo / "tools" / "gpu_hours.py"),
            "--now",
            NOW,
            "sum",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert done.returncode == 0, done.stderr
    assert (fields(done)["gpu_seconds"], fields(done)["runs"]) == ("10800", "2")
    assert "note:" not in done.stderr


def test_without_git_only_the_own_runs_are_counted_with_a_note(
    tmp_path: Path,
) -> None:
    """Outside a git repository only ``<root>/runs`` is scanned, and a note says
    so.

    Reference: the plan (the fallback must not be silent).
    """
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "gpu_hours.py").write_text(TOOL.read_text())
    write_meta(
        tmp_path / "runs" / "a" / "run.meta.json",
        "2026-10-12T00:00:00Z",
        "2026-10-12T01:00:00Z",
    )
    done = subprocess.run(
        [
            sys.executable,
            "-I",
            str(tmp_path / "tools" / "gpu_hours.py"),
            "--now",
            NOW,
            "sum",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
        env={**os.environ, "GIT_CEILING_DIRECTORIES": str(tmp_path.parent)},
    )
    assert done.returncode == 0, done.stderr
    assert fields(done)["gpu_seconds"] == "3600"
    assert "git worktree list failed" in done.stderr


# --- (n) the wrapper calls the tally -----------------------------------------


def lock_is_free(fake: FakeRoot) -> bool:
    """Return True if a non-blocking lock attempt succeeds."""
    with open(fake.lock, "a") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return False
        return True


def wait_for_lock(fake: FakeRoot, seconds: float = 5.0) -> bool:
    """Poll until the lock is free (a bounded wait)."""
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if lock_is_free(fake):
            return True
        time.sleep(0.02)
    return lock_is_free(fake)


def cli_runs(fake: FakeRoot) -> list[dict]:
    """Return the fake interpreter calls that start the study (``--preset``)."""
    return [c for c in fake.calls() if "--preset" in c["argv"]]


def test_wrapper_calls_the_tally_before_pilot_and_stops_on_65(
    tmp_path: Path,
) -> None:
    """A fake tally exiting 65 makes ``pilot`` exit 65; the CLI never runs (n).

    Reference: the criterion text. The fake records its arguments: ``check
    --hours 12`` and no ``--now``. The lock is free afterwards, so the refusal
    did not leave a holder behind.
    """
    fake = FakeRoot(tmp_path)
    done = fake.run(
        "run_preset.sh",
        "pilot",
        "DEV-1",
        "runs/dev/DEV-1",
        env=fake.environment(FAKE_TALLY_EXIT="65"),
    )
    assert done.returncode == 65, (done.stdout, done.stderr)
    assert fake.tally_calls() == [["check", "--hours", "12"]]
    assert cli_runs(fake) == []
    assert not list(fake.root.rglob("run.meta.json*"))
    assert lock_is_free(fake)


def test_wrapper_propagates_64_from_the_tally(tmp_path: Path) -> None:
    """Exit 64 from the tally is returned as 64.

    A child exit code of 64 or 65 is propagated.
    """
    fake = FakeRoot(tmp_path)
    done = fake.run(
        "run_preset.sh",
        "full",
        "DEV-1",
        "runs/dev/DEV-1",
        env=fake.environment(FAKE_TALLY_EXIT="64"),
    )
    assert done.returncode == 64
    assert cli_runs(fake) == []


def test_wrapper_tally_hours_per_device_and_preset(tmp_path: Path) -> None:
    """The wrapper reserves hours per device and preset (n).

    ``pilot --device cpu`` calls the tally with ``--hours 0``; smoke on the CPU
    does not call it. The pilot's background fake ends by itself (no sentinel),
    and the test waits for the lock.
    """
    fake = FakeRoot(tmp_path)
    done = fake.run(
        "run_preset.sh", "pilot", "DEV-1", "runs/dev/DEV-1", "--device", "cpu"
    )
    assert done.returncode == 0, done.stderr
    assert fake.tally_calls() == [["check", "--hours", "0"]]
    assert wait_for_lock(fake)
    smoke = fake.run("run_preset.sh", "smoke", "DEV-1", "runs/dev/DEV-1")
    assert smoke.returncode == 0, smoke.stderr
    assert fake.tally_calls() == [["check", "--hours", "0"]]


def test_wrapper_with_the_real_tally_starts_on_an_empty_tree(
    tmp_path: Path,
) -> None:
    """With the real tool and no ``run.meta.json`` anywhere, ``pilot`` starts.

    It exits 0. The test does not depend on the date.
    """
    fake = FakeRoot(tmp_path, real_tally=True)
    done = fake.run("run_preset.sh", "pilot", "DEV-1", "runs/dev/DEV-1")
    assert done.returncode == 0, done.stderr
    assert wait_for_lock(fake)
    meta = json.loads(
        (
            fake.root / "runs" / "dev" / "DEV-1" / "pilot" / "run.meta.json"
        ).read_text()
    )
    assert meta["exit_code"] == 0


def test_wrapper_with_the_real_tally_refuses_on_a_corrupt_file(
    tmp_path: Path,
) -> None:
    """With the real tool and a corrupt file, ``pilot`` gives 65 (m, n).

    The file is named in the error output.
    """
    fake = FakeRoot(tmp_path, real_tally=True)
    bad = fake.root / "runs" / "old" / "run.meta.json"
    bad.parent.mkdir(parents=True)
    bad.write_text("{not json")
    done = fake.run("run_preset.sh", "pilot", "DEV-1", "runs/dev/DEV-1")
    assert done.returncode == 65, (done.stdout, done.stderr)
    assert str(bad) in done.stderr
    assert cli_runs(fake) == []
    assert lock_is_free(fake)
