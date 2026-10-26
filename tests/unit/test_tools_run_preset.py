"""Tests of ``tools/run_preset.sh``, the shell script that starts a study run.

Study runs (the "presets": ``smoke``, ``pilot``, ``full`` and ``phasej``) are
started through this wrapper. It accepts only registered development seeds, refuses
anything that names the sealed run, takes the GPU lock for GPU work, tallies GPU
hours, can run a long job in the background, and writes a ``run.meta.json`` file
that says who ran what and when (WU-0012.2, LPC.AUTH.3, LPC.PC.7). A mistake
here could waste GPU time or touch data that must stay sealed, so each promise
is tested.

Reference for every test: the acceptance criterion of WU-0012.2 and
DEVELOPMENT_WORKFLOW.md section 4.5, applied by hand: refusal exit code 64,
lock-busy exit code 75, timeout ``12h``, the seven required ``run.meta.json``
keys, ``JAX_PLATFORMS`` set to cpu or cuda, and
``XLA_PYTHON_CLIENT_PREALLOCATE=false``. The wrapper runs in a throwaway root
folder in ``tmp_path`` (``wrapper_helpers.FakeRoot``) with a fake interpreter, a
fake ``timeout``, a fake ``gpu_hours.py`` and a fake lock file
(``LPC_GPU_LOCK``). The real ``runs/`` folder and the real GPU lock are never
touched, and no real preset starts. The competing lock holder is ``fcntl.flock``
in the test process, which is the same advisory lock (a lock programs agree to
respect) as the ``flock`` command on Linux.

Tolerance: none. Every outcome is a string, an integer or an exit code, compared
for exact equality. The timing bounds are: the lock-busy exit within 3 s (about
0.3 s of process start-up, with a 10x margin for 4 shared cores), and at most 5
s for a background fake to end. A fake child waits at most 10 s for its sentinel
file, so no test leaves a process behind.
"""

from __future__ import annotations

import fcntl
import json
import os
import re
import signal
import subprocess
import time
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

import pytest
from wrapper_helpers import REPO, FakeRoot

ISO = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
META_KEYS = {
    "preset",
    "seed_id",
    "start_utc",
    "end_utc",
    "device",
    "wall_seconds",
    "exit_code",
}


@pytest.fixture
def fake(tmp_path: Path) -> FakeRoot:
    """Return a throwaway root with ``run_preset.sh``, a fake tally and the
    other fakes.
    """
    return FakeRoot(tmp_path)


def wait_until(predicate: Callable[[], bool], seconds: float = 5.0) -> bool:
    """Check a condition repeatedly for at most ``seconds``; return whether it
    held.

    This is a bounded wait for a background process, not a retry of a test.
    """
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.02)
    return predicate()


def alive(pid: int) -> bool:
    """Return True if the process exists and is not a zombie (finished but
    unreaped).

    A process that exits between the open and the read of ``/proc/<pid>/stat``
    makes the read raise ``ProcessLookupError`` (ESRCH), not
    ``FileNotFoundError``. Both mean "not alive" (WU-0004g).
    """
    try:
        state = (
            Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
        )
    except (FileNotFoundError, ProcessLookupError):
        return False
    return state != "Z"


def lock_is_free(fake: FakeRoot) -> bool:
    """Return True if a non-blocking attempt to take the fake lock succeeds."""
    with open(fake.lock, "a") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return False
        return True


def cli_calls(fake: FakeRoot) -> list[dict]:
    """Return the fake interpreter calls that run the study (``--preset``), not
    the ``--help`` probe.
    """
    return [c for c in fake.calls() if "--preset" in c["argv"]]


def meta_path(fake: FakeRoot, preset: str, name: str = "DEV-1") -> Path:
    """Return the path of the ``run.meta.json`` of a run into
    ``runs/dev/<name>``.
    """
    return fake.root / "runs" / "dev" / name / preset / "run.meta.json"


def start_pilot(
    fake: FakeRoot,
    *extra: str,
    name: str = "DEV-1",
    preset: str = "pilot",
    **env: str,
) -> tuple[subprocess.CompletedProcess[str], int]:
    """Start a background run (a pilot by default) through the wrapper; return
    the result and the background process id.
    """
    done = fake.run(
        "run_preset.sh",
        preset,
        name,
        f"runs/dev/{name}",
        *extra,
        env=fake.environment(**env),
    )
    assert done.returncode == 0, done.stderr
    match = re.search(
        r"started pid=(\d+) console=(\S+) run_log=(\S+) meta=(\S+)", done.stdout
    )
    assert match, done.stdout
    return done, int(match.group(1))


def test_wrapper_is_executable() -> None:
    """The script exists and is executable (definition of done; reference:
    ``os.access``).
    """
    assert os.access(REPO / "tools" / "run_preset.sh", os.X_OK)


REFUSALS = [
    pytest.param(["smoke", "DEV-99", "runs/d"], id="unregistered-id"),
    pytest.param(
        ["smoke", "20261005", "runs/d"], id="raw-integer-registered-value"
    ),
    pytest.param(["smoke", "7", "runs/d"], id="raw-integer"),
    pytest.param(["smoke", "CONF-1", "runs/d"], id="conf-id"),
    pytest.param(["smoke", "dev-1", "runs/d"], id="lowercase-id"),
    pytest.param(["smoke", "DEV-1;ls", "runs/d"], id="shell-metacharacters"),
    pytest.param(["smoke", "confirmatory", "runs/d"], id="seed-lowercase"),
    pytest.param(["smoke", "CONFIRMATORY", "runs/d"], id="seed-uppercase"),
    pytest.param(
        ["smoke", "DEV-1", "runs/confirmatory"], id="outdir-lowercase"
    ),
    pytest.param(
        ["smoke", "DEV-1", "runs/CONFIRMATORY"], id="outdir-uppercase"
    ),
    pytest.param(
        ["smoke", "DEV-1", "runs/d", "--systems", "confirmatory"],
        id="passthrough-value",
    ),
    pytest.param(
        ["smoke", "DEV-1", "runs/d", "--skip-Confirmatory"],
        id="passthrough-flag",
    ),
    pytest.param(
        ["smoke", "DEV-1", "runs/d", "--confirmatory"], id="confirmatory-flag"
    ),
    pytest.param(
        ["smoke", "DEV-1", "runs/d", "--device", "gpu", "--confirmatory"],
        id="flag-last",
    ),
    pytest.param(["smoke", "DEV-1", "OUTSIDE"], id="outdir-outside-runs"),
    pytest.param(["smoke", "DEV-1", "runs"], id="outdir-is-runs"),
    pytest.param(["smoke", "DEV-1", "runs/../elsewhere"], id="outdir-dotdot"),
    pytest.param(["huge", "DEV-1", "runs/d"], id="unknown-preset"),
    pytest.param(["PHASEJ", "DEV-1", "runs/d"], id="unknown-preset-case"),
    pytest.param(["phasej", "DEV-99", "runs/d"], id="phasej-unregistered-id"),
    pytest.param(["phasej", "20261005", "runs/d"], id="phasej-raw-integer"),
    pytest.param(
        ["phasej", "DEV-1", "runs/d", "--confirmatory"],
        id="phasej-confirmatory-flag",
    ),
    pytest.param(["phasej", "DEV-1", "OUTSIDE"], id="phasej-outdir-outside"),
    pytest.param(
        ["phasej", "DEV-1", "runs/d", "--foo"], id="phasej-unknown-argument"
    ),
    pytest.param(["smoke", "DEV-1", "runs/d", "--foo"], id="unknown-argument"),
    pytest.param(["smoke", "DEV-1", "runs/d", "extra"], id="extra-positional"),
    pytest.param(
        ["smoke", "DEV-1", "runs/d", "--device", "tpu"], id="bad-device"
    ),
    pytest.param(
        ["smoke", "DEV-1", "runs/d", "--device"], id="device-without-value"
    ),
    pytest.param(
        ["smoke", "DEV-1", "runs/d", "--systems"], id="systems-without-value"
    ),
    pytest.param(
        ["smoke", "DEV-1", "runs/d", "--systems", "a;b"], id="bad-system-name"
    ),
    pytest.param(["smoke", "DEV-1"], id="too-few-arguments"),
    pytest.param([], id="no-arguments"),
]


@pytest.mark.parametrize("args", REFUSALS)
def test_refusals_exit_64_with_one_line_and_start_nothing(
    fake: FakeRoot, args: list[str]
) -> None:
    """Every refusal gives 64, one stderr line, no meta file and no call of any
    fake (f).

    Reference: the criterion text of WU-0012.2 and LPC.PC.7 (development seeds
    only; any argument naming the sealed-run path is refused, whatever its
    position or letter case). The output folder outside ``runs/`` is resolved
    against the root, so the check does not depend on the current folder.
    """
    done = fake.run("run_preset.sh", *args)
    assert done.returncode == 64, (done.stdout, done.stderr)
    assert len(done.stderr.strip().splitlines()) == 1, done.stderr
    assert not list(fake.root.rglob("run.meta.json*"))
    assert (
        fake.calls() == []
        and fake.timeout_calls() == []
        and fake.tally_calls() == []
    )
    assert not (fake.root / "runs").exists()


def test_existing_meta_is_never_overwritten(fake: FakeRoot) -> None:
    """An existing ``run.meta.json`` gives 64 and is left byte for byte (f).

    Overwriting it would erase the record of GPU hours.
    """
    path = meta_path(fake, "smoke")
    path.parent.mkdir(parents=True)
    path.write_text('{"keep": "me"}')
    done = fake.run("run_preset.sh", "smoke", "DEV-1", "runs/dev/DEV-1")
    assert done.returncode == 64
    assert len(done.stderr.strip().splitlines()) == 1
    assert path.read_text() == '{"keep": "me"}'
    assert fake.calls() == []


@pytest.mark.parametrize(
    "registry",
    [
        '{"schema": "lpcstudy.seed-registry/2", "seeds": [{"id": "DEV-1"}]}',
        '{"seeds": [{"id": "DEV-1"}]}',
        "not json",
        "[]",
    ],
)
def test_registry_with_another_schema_or_unreadable_is_refused(
    fake: FakeRoot, registry: str
) -> None:
    """A seed registry of another schema, or an unreadable one, refuses even a
    listed id (f).

    The accepted schema is ``lpcstudy.seed-registry/1``.
    """
    (fake.root / "seeds" / "development_seeds.json").write_text(registry)
    done = fake.run("run_preset.sh", "smoke", "DEV-1", "runs/dev/DEV-1")
    assert done.returncode == 64
    assert len(done.stderr.strip().splitlines()) == 1
    assert fake.calls() == []


def test_missing_registry_is_refused(fake: FakeRoot) -> None:
    """With no registry file the answer is 64, not an unchecked run."""
    (fake.root / "seeds" / "development_seeds.json").unlink()
    done = fake.run("run_preset.sh", "smoke", "DEV-1", "runs/dev/DEV-1")
    assert done.returncode == 64
    assert fake.calls() == []


@pytest.mark.parametrize(
    "args",
    [
        ["pilot", "DEV-1", "runs/dev/DEV-1"],
        ["full", "DEV-1", "runs/dev/DEV-1"],
        ["phasej", "DEV-1", "runs/dev/DEV-1"],
        ["smoke", "DEV-1", "runs/dev/DEV-1", "--device", "gpu"],
        ["pilot", "DEV-1", "runs/dev/DEV-1", "--device", "cpu"],
    ],
)
def test_lock_held_exits_75_at_once(fake: FakeRoot, args: list[str]) -> None:
    """With the lock held, pilot, full, phasej, a GPU smoke and a CPU pilot exit
    75 in under 3 s (g).

    The fake never runs (no call at all: the lock comes before the tally and the
    probe), no meta file is written, and the message is one line. Bound: about
    0.3 s of start-up with a 10x margin for shared cores.
    """
    with open(fake.lock, "w") as holder:
        fcntl.flock(holder, fcntl.LOCK_EX | fcntl.LOCK_NB)
        start = time.monotonic()
        done = fake.run("run_preset.sh", *args)
        elapsed = time.monotonic() - start
    assert done.returncode == 75, (done.stdout, done.stderr)
    assert elapsed < 3.0
    assert len(done.stderr.strip().splitlines()) == 1
    assert (
        cli_calls(fake) == []
        and fake.calls() == []
        and fake.tally_calls() == []
    )
    assert not list(fake.root.rglob("run.meta.json*"))


def test_smoke_on_cpu_takes_no_lock(fake: FakeRoot) -> None:
    """A smoke run on the CPU runs while the lock is held (section 4.5) and
    skips the tally.
    """
    with open(fake.lock, "w") as holder:
        fcntl.flock(holder, fcntl.LOCK_EX | fcntl.LOCK_NB)
        done = fake.run("run_preset.sh", "smoke", "DEV-1", "runs/dev/DEV-1")
    assert done.returncode == 0, done.stderr
    assert len(cli_calls(fake)) == 1
    assert fake.tally_calls() == []


def test_smoke_foreground_command_environment_and_meta(fake: FakeRoot) -> None:
    """Smoke runs in the foreground, returns the CLI exit code, and records meta
    and command (i).

    The fake exits 3, so the wrapper exits 3 and ``exit_code`` is 3. Expected
    arguments, from the plan: ``-m lpcstudy --preset smoke --out
    <root>/runs/dev/DEV-1 --seed-id DEV-1``, under ``timeout --kill-after=300
    12h``. Environment: ``JAX_PLATFORMS=cpu``, preallocation off, 4 threads.
    """
    env = fake.environment(
        FAKE_EXIT="3",
        JAX_PLATFORMS="cuda",
        XLA_PYTHON_CLIENT_PREALLOCATE="true",
        OMP_NUM_THREADS="1",
    )
    done = fake.run(
        "run_preset.sh", "smoke", "DEV-1", "runs/dev/DEV-1", env=env
    )
    assert done.returncode == 3, done.stderr
    out = fake.root / "runs" / "dev" / "DEV-1"
    (call,) = cli_calls(fake)
    assert call["argv"] == [
        "-m",
        "lpcstudy",
        "--preset",
        "smoke",
        "--out",
        str(out),
        "--seed-id",
        "DEV-1",
    ]
    assert call["env"]["JAX_PLATFORMS"] == "cpu"
    assert call["env"]["XLA_PYTHON_CLIENT_PREALLOCATE"] == "false"
    assert (
        call["env"]["OMP_NUM_THREADS"],
        call["env"]["MKL_NUM_THREADS"],
        call["env"]["OPENBLAS_NUM_THREADS"],
    ) == ("4", "4", "4")
    timeout_calls = fake.timeout_calls()
    assert ["--kill-after=300", "12h", str(fake.python)] == timeout_calls[-1][
        :3
    ]
    meta = json.loads(meta_path(fake, "smoke").read_text())
    assert meta["exit_code"] == 3 and meta["device"] == "cpu"
    assert meta["seed_flag"] == "--seed-id DEV-1" and meta["lpc_threads"] == 4
    assert meta["command"].endswith("--seed-id DEV-1")
    assert (out / "smoke" / "results.json").is_file()


@pytest.mark.parametrize(
    ("threads", "expected"), [(None, "4"), ("2", "2"), ("17", "17")]
)
def test_xla_thread_cap_is_exported_from_lpc_threads(
    fake: FakeRoot, threads: str | None, expected: str
) -> None:
    """``PJRT_NPROC`` and ``NPROC`` equal the checked ``LPC_THREADS`` (default
    4) in every child.

    These two variables cap the threads that XLA (the compiler behind JAX)
    starts (WU-0012.4, 1). Reference: the criterion text of WU-0012.4 and the
    research note ``2026-10-11-research-xla-threads.md`` (XLA's
    ``DefaultThreadPoolSize()`` reads these two plain variables). The expected
    strings are written literally (4, 2, 17). Larger values inherited from the
    caller (``9``) must be overridden. Both the ``--help`` probe and the study
    call are children, and both must carry the cap. Tolerance: none, exact
    string equality.
    """
    extra = {"PJRT_NPROC": "9", "NPROC": "9"}
    if threads is not None:
        extra["LPC_THREADS"] = threads
    done = fake.run(
        "run_preset.sh",
        "smoke",
        "DEV-1",
        "runs/dev/DEV-1",
        env=fake.environment(**extra),
    )
    assert done.returncode == 0, done.stderr
    calls = fake.calls()
    assert (
        len(calls) == 2
        and "--help" in calls[0]["argv"]
        and "--preset" in calls[1]["argv"]
    )
    for call in calls:
        assert (call["env"]["PJRT_NPROC"], call["env"]["NPROC"]) == (
            expected,
            expected,
        )
        assert call["env"]["OMP_NUM_THREADS"] == expected
        assert call["env"]["LPC_THREADS"] == expected
    assert json.loads(meta_path(fake, "smoke").read_text())[
        "lpc_threads"
    ] == int(expected)


def test_background_pilot_child_carries_the_xla_thread_cap(
    fake: FakeRoot,
) -> None:
    """The background child (pilot, CPU device) gets ``PJRT_NPROC`` and
    ``NPROC`` equal to ``LPC_THREADS``.
    """
    _, pid = start_pilot(fake, "--device", "cpu", LPC_THREADS="3", NPROC="9")
    assert wait_until(lambda: not alive(pid))
    (call,) = cli_calls(fake)
    assert (call["env"]["PJRT_NPROC"], call["env"]["NPROC"]) == ("3", "3")


@pytest.mark.parametrize("threads", ["0", "100", "four", "-1", "2.5"])
def test_invalid_lpc_threads_still_refused_and_starts_nothing(
    fake: FakeRoot, threads: str
) -> None:
    """An invalid ``LPC_THREADS`` gives 64 and one line, with no meta file and
    no child (WU-0012.4, 1).
    """
    done = fake.run(
        "run_preset.sh",
        "smoke",
        "DEV-1",
        "runs/dev/DEV-1",
        env=fake.environment(LPC_THREADS=threads),
    )
    assert done.returncode == 64, (done.stdout, done.stderr)
    assert len(done.stderr.strip().splitlines()) == 1, done.stderr
    assert not list(fake.root.rglob("run.meta.json*"))
    assert (
        fake.calls() == []
        and fake.timeout_calls() == []
        and fake.tally_calls() == []
    )


def test_xla_flags_is_passed_through_unchanged_and_never_added(
    fake: FakeRoot,
) -> None:
    """The wrapper neither sets nor alters ``XLA_FLAGS`` (WU-0012.4, 1; research
    note, claims 1, 2).

    Reference: the behavior before WU-0012.4 (an inherited value passes
    unchanged, an absent one stays absent) and a literal scan of the script: no
    code line (comments excluded) names ``XLA_FLAGS``. Tolerance: none.
    """
    absent = fake.run("run_preset.sh", "smoke", "DEV-1", "runs/dev/DEV-1")
    assert absent.returncode == 0, absent.stderr
    assert all("XLA_FLAGS" not in call["env"] for call in fake.calls())
    supplied = "--xla_cpu_multi_thread_eigen=false"
    done = fake.run(
        "run_preset.sh",
        "smoke",
        "DEV-2",
        "runs/dev/DEV-2",
        env=fake.environment(XLA_FLAGS=supplied),
    )
    assert done.returncode == 0, done.stderr
    assert all(
        call["env"]["XLA_FLAGS"] == supplied for call in fake.calls()[-2:]
    )
    code = [
        line
        for line in (REPO / "tools" / "run_preset.sh").read_text().splitlines()
        if not line.lstrip().startswith("#")
    ]
    assert not [line for line in code if "XLA_FLAGS" in line]


def test_pass_through_arguments_follow_the_seed(fake: FakeRoot) -> None:
    """``--systems a b --skip-robustness`` reach the study command unchanged."""
    done = fake.run(
        "run_preset.sh",
        "smoke",
        "DEV-2",
        "runs/dev/DEV-2",
        "--systems",
        "lorenz63",
        "rossler",
        "--skip-robustness",
    )
    assert done.returncode == 0, done.stderr
    (call,) = cli_calls(fake)
    assert call["argv"][call["argv"].index("--seed-id") + 1] == "DEV-2"
    tail = call["argv"][call["argv"].index("--systems") :]
    assert tail == ["--systems", "lorenz63", "rossler", "--skip-robustness"]


def test_removed_skip_transfer_option_is_refused(fake: FakeRoot) -> None:
    """``--skip-transfer`` no longer exists: exit 64, one line, nothing started
    (WU-0002.1).

    Reference: the wrapper's refusal rule (an unknown argument gives exit 64 and
    one stderr line naming it; no fake is called and no meta file is written),
    as in the refusal table. Tolerance: none; exit code and counts are compared
    for equality.
    """
    done = fake.run(
        "run_preset.sh", "smoke", "DEV-1", "runs/d", "--skip-transfer"
    )
    assert done.returncode == 64, (done.stdout, done.stderr)
    assert (
        len(done.stderr.strip().splitlines()) == 1
        and "--skip-transfer" in done.stderr
    )
    assert not list(fake.root.rglob("run.meta.json*"))
    assert (
        fake.calls() == []
        and fake.timeout_calls() == []
        and fake.tally_calls() == []
    )


def test_seed_flag_is_passed_when_the_help_lists_it(fake: FakeRoot) -> None:
    """When the help text lists ``--seed-id``, the command gets ``--seed-id
    DEV-1`` (j).
    """
    done = fake.run("run_preset.sh", "smoke", "DEV-1", "runs/dev/DEV-1")
    assert done.returncode == 0, done.stderr
    (call,) = cli_calls(fake)
    assert (
        "--seed-id" in call["argv"]
        and call["argv"][call["argv"].index("--seed-id") + 1] == "DEV-1"
    )


def test_dev0_runs_without_the_flag_when_the_cli_lacks_it(
    fake: FakeRoot,
) -> None:
    """When the help text lacks ``--seed-id``, DEV-0 runs with no flag and a
    printed note (j).

    The command-line default 20261005 is the registry's DEV-0 value
    (``seeds/development_seeds.json``).
    """
    registry = json.loads(
        (fake.root / "seeds" / "development_seeds.json").read_text()
    )
    assert [s["value"] for s in registry["seeds"] if s["id"] == "DEV-0"] == [
        20261005
    ]
    done = fake.run(
        "run_preset.sh",
        "smoke",
        "DEV-0",
        "runs/dev/DEV-0",
        env=fake.environment(FAKE_HELP_SEED="0"),
    )
    assert done.returncode == 0, done.stderr
    (call,) = cli_calls(fake)
    assert "--seed-id" not in call["argv"]
    assert "note:" in done.stdout and "20261005" in done.stdout
    assert (
        json.loads(meta_path(fake, "smoke", "DEV-0").read_text())["seed_flag"]
        is None
    )


def test_other_ids_are_refused_when_the_cli_lacks_the_flag(
    fake: FakeRoot,
) -> None:
    """When the help text lacks ``--seed-id``, DEV-1 gives 64 and the study
    never starts (j).
    """
    done = fake.run(
        "run_preset.sh",
        "smoke",
        "DEV-1",
        "runs/dev/DEV-1",
        env=fake.environment(FAKE_HELP_SEED="0"),
    )
    assert done.returncode == 64
    assert len(done.stderr.strip().splitlines()) == 1
    assert cli_calls(fake) == []
    assert not list(fake.root.rglob("run.meta.json*"))


def test_failed_probe_is_refused(fake: FakeRoot) -> None:
    """A command line whose ``--help`` fails gives 64 ("fail closed"), not a
    guess about the flag.
    """
    done = fake.run(
        "run_preset.sh",
        "smoke",
        "DEV-0",
        "runs/dev/DEV-0",
        env=fake.environment(FAKE_HELP_EXIT="1"),
    )
    assert done.returncode == 64
    assert cli_calls(fake) == []


@pytest.mark.parametrize(
    ("extra", "platform", "hours"),
    [
        ([], "cuda", "12"),
        (["--device", "cpu"], "cpu", "0"),
    ],
)
def test_pilot_background_environment_and_tally(
    fake: FakeRoot, extra: list[str], platform: str, hours: str
) -> None:
    """Pilot: 12h timeout, CUDA (or CPU with ``--device cpu``), preallocation
    off (i).

    The tally is called once with ``check --hours 12`` (GPU) or ``--hours 0``
    (CPU) before the start. The criterion of WU-0012.3 is tested in
    ``test_tools_gpu_hours.py``.
    """
    _, pid = start_pilot(fake, *extra, XLA_PYTHON_CLIENT_PREALLOCATE="true")
    assert wait_until(lambda: not alive(pid))
    (call,) = cli_calls(fake)
    assert call["env"]["JAX_PLATFORMS"] == platform
    assert call["env"]["XLA_PYTHON_CLIENT_PREALLOCATE"] == "false"
    assert any("12h" in c for c in fake.timeout_calls())
    assert fake.tally_calls() == [["check", "--hours", hours]]
    assert json.loads(meta_path(fake, "pilot").read_text())["device"] == (
        "gpu" if hours == "12" else "cpu"
    )


@pytest.mark.parametrize("preset", ["full", "phasej"])
def test_phasej_starts_like_full_in_the_background_on_the_gpu(
    fake: FakeRoot, preset: str
) -> None:
    """``phasej`` is accepted and handled exactly as ``full`` (WU-0051a).

    Both default to the GPU (``JAX_PLATFORMS=cuda``), start in the background,
    call the tally once with ``check --hours 12`` (the hours of ``full``), pass
    ``--preset <name>`` to the study command unchanged, and write
    ``<out>/<name>/run.meta.json`` with device ``gpu``. Reference: the WU-0051a
    plan (phasej is treated like full) and the expected argv written out here.
    """
    done, pid = start_pilot(fake, preset=preset)
    assert wait_until(lambda: not alive(pid))
    out = fake.root / "runs" / "dev" / "DEV-1"
    (call,) = cli_calls(fake)
    assert call["argv"] == [
        "-m",
        "lpcstudy",
        "--preset",
        preset,
        "--out",
        str(out),
        "--seed-id",
        "DEV-1",
    ]
    assert call["env"]["JAX_PLATFORMS"] == "cuda"
    assert any("12h" in c for c in fake.timeout_calls())
    assert fake.tally_calls() == [["check", "--hours", "12"]]
    meta = json.loads(meta_path(fake, preset).read_text())
    assert (meta["preset"], meta["device"], meta["exit_code"]) == (
        preset,
        "gpu",
        0,
    )
    assert f"console={out / preset / 'console.log'}" in done.stdout
    assert lock_is_free(fake)


def test_existing_phasej_meta_is_never_overwritten(fake: FakeRoot) -> None:
    """An existing ``phasej/run.meta.json`` gives 64 and is left byte for byte,
    as for ``full``.
    """
    path = meta_path(fake, "phasej")
    path.parent.mkdir(parents=True)
    path.write_text('{"keep": "me"}')
    done = fake.run("run_preset.sh", "phasej", "DEV-1", "runs/dev/DEV-1")
    assert done.returncode == 64
    assert len(done.stderr.strip().splitlines()) == 1
    assert path.read_text() == '{"keep": "me"}'
    assert fake.calls() == [] and fake.tally_calls() == []


def test_unknown_preset_message_lists_phasej(fake: FakeRoot) -> None:
    """The refusals of an unknown preset and of too few arguments name the four
    accepted presets.
    """
    done = fake.run("run_preset.sh", "huge", "DEV-1", "runs/d")
    assert done.returncode == 64
    assert "(smoke, pilot, full or phasej)" in done.stderr
    usage = fake.run("run_preset.sh")
    assert usage.returncode == 64
    assert "<smoke|pilot|full|phasej>" in usage.stderr


@pytest.mark.parametrize("fake_exit", [0, 3])
def test_background_holds_the_lock_survives_sighup_and_records_the_end(
    fake: FakeRoot, fake_exit: int
) -> None:
    """A pilot starts in the background, holds the lock, survives SIGHUP and
    records its end (h).

    SIGHUP is the "hang-up" signal sent when a terminal closes. Reference: the
    criterion text. While the fake waits for its sentinel file: the wrapper has
    already exited 0, ``end_utc`` is null, a non-blocking lock attempt fails,
    and SIGHUP does not kill the child. After the sentinel appears: the process
    ends within 5 s, the meta file has the 7 keys with their types,
    ``wall_seconds == end - start`` and ``exit_code == FAKE_EXIT``, and the lock
    is free.
    """
    done, pid = start_pilot(fake, FAKE_WAIT="1", FAKE_EXIT=str(fake_exit))
    path = meta_path(fake, "pilot")
    try:
        assert wait_until(lambda: bool(cli_calls(fake)))
        running = json.loads(path.read_text())
        assert running["end_utc"] is None and running["exit_code"] is None
        assert running["wall_seconds"] is None
        assert not lock_is_free(fake)
        os.kill(pid, signal.SIGHUP)
        time.sleep(0.3)
        assert alive(pid)
        assert not lock_is_free(fake)
    finally:
        (fake.fake_dir / "go").write_text("")
    assert wait_until(lambda: not alive(pid))
    meta = json.loads(path.read_text())
    assert META_KEYS <= set(meta)
    assert (
        meta["preset"] == "pilot"
        and meta["seed_id"] == "DEV-1"
        and meta["device"] == "gpu"
    )
    assert ISO.match(meta["start_utc"]) and ISO.match(meta["end_utc"])
    parse = lambda text: datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc
    )
    assert type(meta["wall_seconds"]) is int
    assert meta["wall_seconds"] == int(
        (parse(meta["end_utc"]) - parse(meta["start_utc"])).total_seconds()
    )
    assert type(meta["exit_code"]) is int and meta["exit_code"] == fake_exit
    assert meta["pid"] == pid
    assert lock_is_free(fake)
    assert (
        "started" in done.stdout
        and "console.log" in done.stdout
        and "run.log" in done.stdout
    )


def test_background_sigterm_is_recorded_as_143(fake: FakeRoot) -> None:
    """SIGTERM (the "please stop" signal) to the background recorder stops the
    child.

    The recorded exit code is ``128 + 15 = 143``.
    """
    _, pid = start_pilot(fake, FAKE_WAIT="1")
    path = meta_path(fake, "pilot")
    try:
        assert wait_until(lambda: bool(cli_calls(fake)))
        os.kill(pid, signal.SIGTERM)
        assert wait_until(lambda: not alive(pid))
    finally:
        (fake.fake_dir / "go").write_text("")
    meta = json.loads(path.read_text())
    assert meta["exit_code"] == 143 and ISO.match(meta["end_utc"])
    assert lock_is_free(fake)


HIDDEN_MODES = [
    "__record",
    "record",
    "--record",
    "__run",
    "__internal",
    "--internal",
    "-c",
]


@pytest.mark.parametrize("mode", HIDDEN_MODES)
def test_no_hidden_mode_runs_a_command(fake: FakeRoot, mode: str) -> None:
    """Any hidden mode name is refused with 64 and runs nothing (R1a; reference:
    the plan).

    The wrapper has one entry point: ``<preset> <seed-id> <out-dir> [options]``.
    ``__record`` was an internal re-entry in the first version; it is gone. The
    test passes the reviewer's probe shape, ``<mode> <file> -- sh -c 'touch
    MARK'``, with the lock file open on file descriptor 9 as the reviewer did,
    and checks that the marker file is never created and no fake is called.
    """
    marker = fake.base / "marker"
    meta = fake.base / "plain.txt"
    meta.write_text("")
    for extra in (
        [str(meta), "--", "sh", "-c", f"touch {marker}"],
        [str(meta), "x"],
        [],
    ):
        done = subprocess.run(
            [
                "bash",
                "-c",
                'exec "$@" 9>>"$LPC_GPU_LOCK"',
                "x",
                str(fake.root / "tools" / "run_preset.sh"),
                mode,
                *extra,
            ],
            cwd=fake.root,
            env=fake.environment(),
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        assert done.returncode == 64, (extra, done.stdout, done.stderr)
        assert len(done.stderr.strip().splitlines()) == 1
    assert not marker.exists()
    assert (
        fake.calls() == []
        and fake.timeout_calls() == []
        and fake.tally_calls() == []
    )


def test_script_has_no_second_entry_point() -> None:
    """The script text has no ``__record`` mode and no ``nohup`` re-entry (R1;
    reference: a text search).

    A structural guard: the background run is a subshell of the checked front
    end, so no argument can reach the recorder without passing the lock, seed,
    registry and tally checks.
    """
    text = (REPO / "tools" / "run_preset.sh").read_text()
    assert "__record" not in text
    assert "nohup" not in text.replace("like nohup", "")


def test_background_run_has_the_checks_of_the_front_end(fake: FakeRoot) -> None:
    """The background child exists only after the lock, tally and registry
    checks (R1c).

    With a busy lock nothing starts at all (see
    ``test_lock_held_exits_75_at_once``). With an unregistered seed nothing
    starts. With the lock free a pilot starts, and the only child is the checked
    command (``timeout ... 12h``), run under the recorder with the process id in
    the meta file equal to the printed one.
    """
    refused = fake.run("run_preset.sh", "pilot", "DEV-99", "runs/dev/DEV-99")
    assert refused.returncode == 64
    assert fake.calls() == []
    done, pid = start_pilot(fake)
    assert wait_until(lambda: not alive(pid))
    assert len(cli_calls(fake)) == 1
    assert json.loads(meta_path(fake, "pilot").read_text())["pid"] == pid


@pytest.mark.parametrize("tally_exit", [None, 7])
def test_tally_failure_other_than_64_65_fails_closed(
    fake: FakeRoot, tally_exit: int | None
) -> None:
    """A missing tally tool, or one that fails with another code, gives 65 and
    no start.

    "Fail closed" means that when the check cannot be made, the run is refused.
    """
    if tally_exit is None:
        (fake.root / "tools" / "gpu_hours.py").unlink()
        env = fake.environment()
    else:
        env = fake.environment(FAKE_TALLY_EXIT=str(tally_exit))
    done = fake.run(
        "run_preset.sh", "pilot", "DEV-1", "runs/dev/DEV-1", env=env
    )
    assert done.returncode == 65, done.stderr
    assert cli_calls(fake) == []
    assert not list(fake.root.rglob("run.meta.json*"))
    assert lock_is_free(fake)


# ------------------------------------ WU-0005.6a: --estimator-refine-steps (K2)
# Reference: the plan (the wrapper passes the flag to the study command
# unchanged and refuses a bad value before the lock, the tally and any child)
# and the argument rules of ``test_pass_through_*``. Tolerance: none; argument
# lists, exit codes and counts are compared for equality.
@pytest.mark.parametrize(
    "args",
    [
        pytest.param(["--estimator-refine-steps", "0"], id="zero"),
        pytest.param(["--estimator-refine-steps", "-1"], id="negative"),
        pytest.param(["--estimator-refine-steps", "1.5"], id="fraction"),
        pytest.param(["--estimator-refine-steps", "x"], id="letter"),
        pytest.param(["--estimator-refine-steps", ""], id="empty"),
        pytest.param(["--estimator-refine-steps", "015"], id="leading-zero"),
        pytest.param(["--estimator-refine-steps", "+3"], id="plus"),
        pytest.param(["--estimator-refine-steps", "3\nx"], id="newline"),
        pytest.param(["--estimator-refine-steps", "1000"], id="above-the-cap"),
        pytest.param(
            ["--estimator-refine-steps", "9" * 5000], id="over-the-digit-limit"
        ),
        pytest.param(["--estimator-refine-steps"], id="no-value"),
        pytest.param(
            [
                "--estimator-refine-steps",
                "15",
                "--estimator-refine-steps",
                "30",
            ],
            id="twice",
        ),
    ],
)
def test_k2_bad_refine_value_is_refused_before_the_lock(
    fake: FakeRoot, args: list[str]
) -> None:
    """K2: a bad value, no value or a repeat gives 64 with one line, even with
    the lock held.

    A pilot would exit 75 with the lock held if the check came after the lock;
    64 shows it comes first. No fake is called, and no meta file or runs folder
    is created.
    """
    with open(fake.lock, "w") as holder:
        fcntl.flock(holder, fcntl.LOCK_EX | fcntl.LOCK_NB)
        done = fake.run(
            "run_preset.sh", "pilot", "DEV-1", "runs/dev/DEV-1", *args
        )
    assert done.returncode == 64, (done.stdout, done.stderr)
    assert (
        len(done.stderr.strip().splitlines()) == 1
        and "--estimator-refine-steps" in done.stderr
    )
    assert (
        fake.calls() == []
        and fake.timeout_calls() == []
        and fake.tally_calls() == []
    )
    assert (
        not list(fake.root.rglob("run.meta.json*"))
        and not (fake.root / "runs").exists()
    )


def test_k2_flag_reaches_the_cli_and_the_meta(fake: FakeRoot) -> None:
    """K2: the flag and its value reach the study command in order, and the meta
    ``command`` shows it.

    ``--systems`` keeps its place before the other pass-through arguments, which
    keep their given order (the wrapper builds ``--systems S...`` and then the
    pass-through list).
    """
    done = fake.run(
        "run_preset.sh",
        "smoke",
        "DEV-2",
        "runs/dev/DEV-2",
        "--estimator-refine-steps",
        "30",
        "--systems",
        "lorenz63",
        "--skip-robustness",
    )
    assert done.returncode == 0, done.stderr
    (call,) = cli_calls(fake)
    tail = call["argv"][call["argv"].index("--systems") :]
    assert tail == [
        "--systems",
        "lorenz63",
        "--estimator-refine-steps",
        "30",
        "--skip-robustness",
    ]
    assert (
        "--seed-id" in call["argv"]
        and call["argv"][call["argv"].index("--seed-id") + 1] == "DEV-2"
    )
    meta = json.loads(meta_path(fake, "smoke", "DEV-2").read_text())
    assert "--estimator-refine-steps 30" in meta["command"]


def test_k2_absent_flag_leaves_the_argv_as_before(fake: FakeRoot) -> None:
    """K2: without the flag the study command never mentions it (the normal path
    is unchanged).
    """
    done = fake.run("run_preset.sh", "smoke", "DEV-2", "runs/dev/DEV-2")
    assert done.returncode == 0, done.stderr
    (call,) = cli_calls(fake)
    assert "--estimator-refine-steps" not in call["argv"]


def test_k2_background_pilot_carries_the_flag_and_the_tally(
    fake: FakeRoot,
) -> None:
    """K2: a CPU pilot with the flag passes it to the child, after the lock and
    the tally.
    """
    _, pid = start_pilot(
        fake, "--device", "cpu", "--estimator-refine-steps", "60"
    )
    assert wait_until(lambda: not alive(pid))
    (call,) = cli_calls(fake)
    assert call["argv"][-2:] == ["--estimator-refine-steps", "60"]
    assert fake.tally_calls() == [["check", "--hours", "0"]]


# ---------------------------------------- WU-0003.11: --states-dump (bare flag)
# Reference: the plan of WU-0003.11 and the command-line rules of
# ``lpcstudy/__main__.py`` (a ``store_true`` flag, that is, a switch that takes
# no value): the wrapper passes the bare flag once, unchanged, and refuses a
# repeat or an argument before the lock. The expected argument lists are
# written by hand from the wrapper's documented order (``--systems S...``
# first, then the pass-through arguments as given). Tolerance: none; argument
# lists, exit codes and counts are compared for equality.
@pytest.mark.parametrize(
    "args",
    [
        pytest.param(["--states-dump", "--states-dump"], id="twice"),
        pytest.param(
            ["--states-dump", "--skip-robustness", "--states-dump"],
            id="twice-apart",
        ),
        pytest.param(["--states-dump", "1"], id="digit-argument"),
        pytest.param(["--states-dump", "x"], id="word-argument"),
        pytest.param(["--states-dump", "true"], id="boolean-argument"),
        pytest.param(["--states-dump", ""], id="empty-argument"),
        pytest.param(["--states-dump", "-1"], id="dash-argument"),
        pytest.param(["--states-dump=1"], id="equals-argument"),
        pytest.param(
            ["--states-dump=", "--skip-robustness"], id="equals-empty"
        ),
        pytest.param(
            ["--systems", "lorenz63", "--states-dump", "lorenz63"],
            id="system-name-after",
        ),
    ],
)
def test_dump_repeat_or_argument_is_refused_before_the_lock(
    fake: FakeRoot, args: list[str]
) -> None:
    """A repeated flag or a flag with an argument gives 64 with one line, even
    with the lock held.

    A pilot would exit 75 with the lock held if the check came after the lock;
    64 shows it comes first. No fake is called, and no meta file or runs folder
    is created.
    """
    with open(fake.lock, "w") as holder:
        fcntl.flock(holder, fcntl.LOCK_EX | fcntl.LOCK_NB)
        done = fake.run(
            "run_preset.sh", "pilot", "DEV-1", "runs/dev/DEV-1", *args
        )
    assert done.returncode == 64, (done.stdout, done.stderr)
    assert (
        len(done.stderr.strip().splitlines()) == 1
        and "--states-dump" in done.stderr
    )
    assert (
        fake.calls() == []
        and fake.timeout_calls() == []
        and fake.tally_calls() == []
    )
    assert (
        not list(fake.root.rglob("run.meta.json*"))
        and not (fake.root / "runs").exists()
    )


def test_dump_flag_reaches_the_cli_and_the_meta(fake: FakeRoot) -> None:
    """The bare flag reaches the study command once, in its given place, and the
    meta ``command`` shows it.
    """
    done = fake.run(
        "run_preset.sh",
        "smoke",
        "DEV-2",
        "runs/dev/DEV-2",
        "--states-dump",
        "--estimator-refine-steps",
        "30",
        "--systems",
        "lorenz63",
        "--skip-robustness",
    )
    assert done.returncode == 0, done.stderr
    (call,) = cli_calls(fake)
    expected = [
        "--systems",
        "lorenz63",
        "--states-dump",
        "--estimator-refine-steps",
        "30",
        "--skip-robustness",
    ]
    assert call["argv"][call["argv"].index("--systems") :] == expected
    assert call["argv"].count("--states-dump") == 1
    meta = json.loads(meta_path(fake, "smoke", "DEV-2").read_text())
    words = meta["command"].split()
    assert (
        words.count("--states-dump") == 1
        and words[-len(expected) :] == expected
    )


def test_dump_flag_as_the_last_argument_and_before_another_option(
    fake: FakeRoot,
) -> None:
    """The flag stays bare at the end of the line and before ``--device``;
    neither takes it as a value.
    """
    last = fake.run(
        "run_preset.sh", "smoke", "DEV-2", "runs/dev/a", "--states-dump"
    )
    assert last.returncode == 0, last.stderr
    before = fake.run(
        "run_preset.sh",
        "smoke",
        "DEV-2",
        "runs/dev/b",
        "--states-dump",
        "--device",
        "cpu",
    )
    assert before.returncode == 0, before.stderr
    first, second = cli_calls(fake)
    assert (
        first["argv"][-1] == "--states-dump"
        and second["argv"][-1] == "--states-dump"
    )
    assert (
        first["argv"].count("--states-dump")
        == second["argv"].count("--states-dump")
        == 1
    )


def test_dump_absent_flag_leaves_the_argv_as_before(fake: FakeRoot) -> None:
    """Without the flag, neither the study command nor the meta ``command``
    mentions it.
    """
    done = fake.run("run_preset.sh", "smoke", "DEV-2", "runs/dev/DEV-2")
    assert done.returncode == 0, done.stderr
    (call,) = cli_calls(fake)
    assert "--states-dump" not in call["argv"]
    assert (
        "--states-dump"
        not in json.loads(meta_path(fake, "smoke", "DEV-2").read_text())[
            "command"
        ]
    )


def test_dump_flag_changes_only_the_argv_by_the_flag(fake: FakeRoot) -> None:
    """With and without the flag the two runs differ by the flag alone (no other
    behavior change).

    The output folder is the one expected difference (two runs cannot share a
    meta file) and is masked. The environment variables that the wrapper sets
    and the ``timeout`` call are compared whole.
    """
    plain = fake.run(
        "run_preset.sh", "smoke", "DEV-2", "runs/dev/plain", "--skip-robustness"
    )
    dumped = fake.run(
        "run_preset.sh",
        "smoke",
        "DEV-2",
        "runs/dev/dumped",
        "--skip-robustness",
        "--states-dump",
    )
    assert plain.returncode == dumped.returncode == 0, (
        plain.stderr,
        dumped.stderr,
    )
    first, second = cli_calls(fake)

    def masked(call: dict, name: str) -> list[str]:
        return [
            word.replace(name, "OUT")
            for word in call["argv"]
            if word != "--states-dump"
        ]

    assert masked(second, "dumped") == masked(first, "plain")
    keys = (
        "JAX_PLATFORMS",
        "XLA_PYTHON_CLIENT_PREALLOCATE",
        "OMP_NUM_THREADS",
        "PJRT_NPROC",
    )
    assert {k: first["env"].get(k) for k in keys} == {
        k: second["env"].get(k) for k in keys
    }
    one, two = [
        c for c in fake.timeout_calls() if "--preset" in c
    ]  # not the ``--help`` probe
    assert [w.replace("plain", "OUT") for w in one] == [
        w.replace("dumped", "OUT") for w in two if w != "--states-dump"
    ]


def test_dump_flag_with_the_confirmatory_flag_is_still_refused(
    fake: FakeRoot,
) -> None:
    """The sealed-run scan still refuses it first: 64, its own message, one
    line, nothing started.

    The message check ("owner-only", the text of the scan in the wrapper) is
    what tells the scan apart from the catch-all "unexpected argument" refusal,
    which also gives 64 and one line (LPC.PC.7).
    """
    done = fake.run(
        "run_preset.sh",
        "smoke",
        "DEV-1",
        "runs/dev/DEV-1",
        "--states-dump",
        "--confirmatory",
    )
    assert done.returncode == 64, (done.stdout, done.stderr)
    assert (
        "owner-only" in done.stderr and "unexpected argument" not in done.stderr
    )
    assert len(done.stderr.strip().splitlines()) == 1
    assert fake.calls() == [] and not list(fake.root.rglob("run.meta.json*"))


def test_dump_background_pilot_carries_the_flag_and_the_tally(
    fake: FakeRoot,
) -> None:
    """A CPU pilot with the flag passes it to the child, after the lock and the
    tally.
    """
    _, pid = start_pilot(fake, "--device", "cpu", "--states-dump")
    assert wait_until(lambda: not alive(pid))
    (call,) = cli_calls(fake)
    assert (
        call["argv"][-1] == "--states-dump"
        and call["argv"].count("--states-dump") == 1
    )
    assert fake.tally_calls() == [["check", "--hours", "0"]]
    assert (
        "--states-dump"
        in json.loads(meta_path(fake, "pilot").read_text())["command"].split()
    )


def test_alive_is_false_for_a_pid_that_does_not_exist_and_true_for_this_process() -> (
    None
):
    """The helper ``alive`` reports liveness correctly (WU-0004g).

    A process id that does not exist is not alive, and this process is.
    Reference: the operating system. A process id above ``pid_max`` cannot exist
    (the limit is read from ``/proc/sys/kernel/pid_max``), and ``os.getpid()``
    is alive. The ESRCH race itself (the process vanishing between open and
    read) cannot be forced reliably; the helper maps its exception to False,
    which this test covers through the ``FileNotFoundError`` branch of the same
    ``except``. The answers are exact booleans.
    """
    beyond = int(Path("/proc/sys/kernel/pid_max").read_text()) + 1
    assert alive(beyond) is False
    assert alive(os.getpid()) is True
