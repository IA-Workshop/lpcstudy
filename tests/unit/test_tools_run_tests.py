"""Tests of ``tools/run_tests.sh``, the shell script that runs pytest for the
study.

Every test run in this project goes through this wrapper. It sets the safe
environment (CPU only, four threads, no GPU memory grab), picks a time limit for
each tier, takes the GPU lock for the ``gpu`` tier, and refuses unsafe requests
such as running the whole suite (WU-0012.1, DEVELOPMENT_WORKFLOW.md section
4.5). These tests check each of those promises.

Reference for every test: the contract of DEVELOPMENT_WORKFLOW.md sections 4.5
and 4.6 and the acceptance criterion of WU-0012.1, applied by hand. The wrapper
is run in a throwaway root folder in ``tmp_path`` (``wrapper_helpers.FakeRoot``)
with a fake Python interpreter and a fake ``timeout`` that record what they were
called with, so there is no real pytest run and no real GPU lock. The expected
values (``cpu``, ``4``, ``-q --tb=short -rfE``, the time limits
300/900/3600/1800 s, the exit codes 64/75/124) are written literally from the
document, not taken from the wrapper.

Tolerance: none. Every outcome is a string, a set of arguments or an exit code,
compared for exact equality. The one timing check is the 30 s bound of section
4.5 for the lock wait. The expected elapsed time is about 1 s
(``LPC_GPU_WAIT=1``) plus process start-up, far under the bound, which is the
one in the criterion.
"""

from __future__ import annotations

import fcntl
import os
import subprocess
import time
from pathlib import Path

import pytest
from wrapper_helpers import REPO, TIERS, FakeRoot, write_script

TIMEOUTS = {"unit": "300", "integration": "900", "slow": "3600", "gpu": "1800"}
FIXED_FLAGS = ["-q", "--tb=short", "-rfE"]


@pytest.fixture
def fake(tmp_path: Path) -> FakeRoot:
    """Return a throwaway root with ``run_tests.sh`` and the fake programs."""
    return FakeRoot(tmp_path)


def only_call(fake: FakeRoot) -> dict:
    """Return the one recorded call of the fake interpreter (fail if not exactly
    one).
    """
    calls = fake.calls()
    assert len(calls) == 1, calls
    return calls[0]


def test_wrapper_is_executable() -> None:
    """The script exists and is executable (definition of done; reference:
    ``os.access``).
    """
    assert os.access(REPO / "tools" / "run_tests.sh", os.X_OK)


def test_unit_tier_environment_and_arguments(fake: FakeRoot) -> None:
    """Unit tier: CPU only, 4 threads each, no preallocation, fixed pytest flags
    (a).

    Reference: the criterion text of WU-0012.1. The inherited
    ``JAX_PLATFORMS=cuda`` and ``OMP_NUM_THREADS=1`` must be overridden.
    ``LPC_THREADS`` is unset, so the default of 4 applies. The fixed flags are
    ``-q --tb=short -rfE`` (quiet output and short tracebacks).
    """
    env = fake.environment(
        JAX_PLATFORMS="cuda",
        OMP_NUM_THREADS="1",
        XLA_PYTHON_CLIENT_PREALLOCATE="true",
    )
    done = fake.run("run_tests.sh", "unit", "tests/unit/test_x.py", env=env)
    assert done.returncode == 0, done.stderr
    call = only_call(fake)
    got = call["env"]
    assert got["JAX_PLATFORMS"] == "cpu"
    assert (
        got["OMP_NUM_THREADS"],
        got["MKL_NUM_THREADS"],
        got["OPENBLAS_NUM_THREADS"],
    ) == ("4", "4", "4")
    assert got["XLA_PYTHON_CLIENT_PREALLOCATE"] == "false"
    argv = call["argv"]
    assert argv[:2] == ["-m", "pytest"]
    assert argv[2:5] == FIXED_FLAGS, argv
    assert argv[5:] == ["tests/unit/test_x.py"]


def test_lpc_threads_is_copied_to_the_thread_variables(fake: FakeRoot) -> None:
    """``LPC_THREADS=3`` sets all three thread variables to 3 (a).

    Larger values inherited from the caller (8) must be overridden.
    """
    env = fake.environment(
        LPC_THREADS="3", OMP_NUM_THREADS="8", MKL_NUM_THREADS="8"
    )
    done = fake.run("run_tests.sh", "unit", "tests/unit/test_x.py", env=env)
    assert done.returncode == 0, done.stderr
    got = only_call(fake)["env"]
    assert (
        got["OMP_NUM_THREADS"],
        got["MKL_NUM_THREADS"],
        got["OPENBLAS_NUM_THREADS"],
    ) == ("3", "3", "3")


@pytest.mark.parametrize("tier", ["unit", "gpu"])
@pytest.mark.parametrize(
    ("threads", "expected"), [(None, "4"), ("2", "2"), ("17", "17")]
)
def test_xla_thread_cap_is_exported_from_lpc_threads(
    fake: FakeRoot, tier: str, threads: str | None, expected: str
) -> None:
    """``PJRT_NPROC`` and ``NPROC`` equal the checked ``LPC_THREADS`` (default
    4).

    These two environment variables cap the threads that XLA (the compiler
    behind JAX) starts (WU-0012.4, 1). Reference: the criterion text of
    WU-0012.4 and the research note ``2026-10-11-research-xla-threads.md``
    (XLA's ``DefaultThreadPoolSize()`` reads these two plain variables). The
    expected strings are written literally (4, 2, 17), not taken from the
    wrapper. Larger values inherited from the caller (``9``) must be overridden,
    as for OMP. Tolerance: none, exact string equality.
    """
    extra = {"PJRT_NPROC": "9", "NPROC": "9"}
    if threads is not None:
        extra["LPC_THREADS"] = threads
    done = fake.run(
        "run_tests.sh",
        tier,
        f"tests/{tier}/test_x.py",
        env=fake.environment(**extra),
    )
    assert done.returncode == 0, done.stderr
    got = only_call(fake)["env"]
    assert (got["PJRT_NPROC"], got["NPROC"]) == (expected, expected)
    assert got["OMP_NUM_THREADS"] == expected


@pytest.mark.parametrize("threads", ["0", "100", "four", "-1", "2.5"])
def test_invalid_lpc_threads_still_refused_and_no_cap_is_set(
    fake: FakeRoot, threads: str
) -> None:
    """An invalid ``LPC_THREADS`` gives exit 64 and one message line (WU-0012.4,
    1).

    The refusal comes before any child process starts.
    """
    done = fake.run(
        "run_tests.sh",
        "unit",
        "tests/unit/test_x.py",
        env=fake.environment(LPC_THREADS=threads),
    )
    assert done.returncode == 64, (done.stdout, done.stderr)
    assert len(done.stderr.strip().splitlines()) == 1, done.stderr
    assert fake.calls() == [] and fake.timeout_calls() == []


@pytest.mark.parametrize("tier", ["unit", "gpu"])
def test_xla_flags_is_passed_through_unchanged_and_never_added(
    fake: FakeRoot, tier: str
) -> None:
    """The wrapper neither sets nor alters ``XLA_FLAGS`` (WU-0012.4, 1; research
    note, claims 1, 2).

    An unknown ``XLA_FLAGS`` token aborts XLA, so the thread cap must not travel
    through it. Reference: the behavior before WU-0012.4 (an inherited value
    passes unchanged, an absent one stays absent) and a literal scan of the
    script: no code line (comments excluded) names ``XLA_FLAGS``. Tolerance:
    none.
    """
    absent = fake.run("run_tests.sh", tier, f"tests/{tier}/test_x.py")
    assert absent.returncode == 0, absent.stderr
    assert "XLA_FLAGS" not in only_call(fake)["env"]
    supplied = "--xla_cpu_multi_thread_eigen=false"
    done = fake.run(
        "run_tests.sh",
        tier,
        f"tests/{tier}/test_x.py",
        env=fake.environment(XLA_FLAGS=supplied),
    )
    assert done.returncode == 0, done.stderr
    assert fake.calls()[-1]["env"]["XLA_FLAGS"] == supplied
    code = [
        line
        for line in (REPO / "tools" / "run_tests.sh").read_text().splitlines()
        if not line.lstrip().startswith("#")
    ]
    assert not [line for line in code if "XLA_FLAGS" in line]


@pytest.mark.parametrize("tier", ["integration", "slow"])
def test_other_cpu_tiers_force_cpu(fake: FakeRoot, tier: str) -> None:
    """The integration and slow tiers also run with ``JAX_PLATFORMS=cpu``
    (section 4.5).
    """
    env = fake.environment(JAX_PLATFORMS="cuda")
    done = fake.run("run_tests.sh", tier, f"tests/{tier}/test_x.py", env=env)
    assert done.returncode == 0, done.stderr
    assert only_call(fake)["env"]["JAX_PLATFORMS"] == "cpu"


def test_gpu_tier_disables_preallocation(fake: FakeRoot) -> None:
    """GPU tier: memory preallocation stays off even if ``true`` is inherited
    (b).

    The fake lock is free, so the child runs. ``JAX_PLATFORMS`` is ``cuda,cpu``
    (plan, section 4.5).
    """
    env = fake.environment(XLA_PYTHON_CLIENT_PREALLOCATE="true")
    done = fake.run("run_tests.sh", "gpu", "tests/gpu/test_x.py", env=env)
    assert done.returncode == 0, done.stderr
    got = only_call(fake)["env"]
    assert got["XLA_PYTHON_CLIENT_PREALLOCATE"] == "false"
    assert got["JAX_PLATFORMS"] == "cuda,cpu"


def test_gpu_tier_exits_75_within_30_s_when_the_lock_is_held(
    fake: FakeRoot,
) -> None:
    """A competing lock holder gives exit 75 in under 30 s, and nothing runs
    (c).

    Reference: ``fcntl.flock`` in the test process, which is the same advisory
    lock (a lock programs agree to respect) as the ``flock`` command on Linux.
    ``LPC_GPU_WAIT=1`` shortens the wait (about 1 s expected); the bound is the
    30 s of the criterion.
    """
    with open(fake.lock, "w") as holder:
        fcntl.flock(holder, fcntl.LOCK_EX | fcntl.LOCK_NB)
        start = time.monotonic()
        done = fake.run(
            "run_tests.sh",
            "gpu",
            "tests/gpu/test_x.py",
            env=fake.environment(LPC_GPU_WAIT="1"),
        )
        elapsed = time.monotonic() - start
    assert done.returncode == 75, done.stderr
    assert elapsed < 30.0
    assert fake.calls() == []
    assert len(done.stderr.strip().splitlines()) == 1


def test_gpu_tier_default_wait_is_30_s(fake: FakeRoot) -> None:
    """With a fake ``flock`` on the path, the wrapper calls ``flock -w 30 9``
    (c).
    """
    write_script(
        fake.bin / "flock",
        "#!/usr/bin/env bash\n" 'echo "$*" >>"$FAKE_DIR/flock.log"\nexit 0\n',
    )
    done = fake.run("run_tests.sh", "gpu", "tests/gpu/test_x.py")
    assert done.returncode == 0, done.stderr
    assert (fake.fake_dir / "flock.log").read_text().splitlines() == ["-w 30 9"]


def test_cpu_tiers_take_no_lock(fake: FakeRoot) -> None:
    """A held lock does not block the unit tier (section 4.5: only the gpu tier
    is locked).
    """
    with open(fake.lock, "w") as holder:
        fcntl.flock(holder, fcntl.LOCK_EX | fcntl.LOCK_NB)
        done = fake.run("run_tests.sh", "unit", "tests/unit/test_x.py")
    assert done.returncode == 0, done.stderr


@pytest.mark.parametrize("tier", TIERS)
def test_timeout_per_tier(fake: FakeRoot, tier: str) -> None:
    """The ``timeout`` command gets 300, 900, 3600 or 1800 s and a 30 s kill
    delay (d).

    Reference: DEVELOPMENT_WORKFLOW.md section 4.5, "Timeouts".
    """
    done = fake.run("run_tests.sh", tier, f"tests/{tier}/test_x.py")
    assert done.returncode == 0, done.stderr
    calls = fake.timeout_calls()
    assert len(calls) == 1
    assert calls[0][:2] == ["--kill-after=30", TIMEOUTS[tier]], calls[0]


def test_timeout_exit_124_is_reported(fake: FakeRoot) -> None:
    """A child that exits 124 (what ``timeout`` returns) gives 124 and a TIMEOUT
    line (d).
    """
    done = fake.run(
        "run_tests.sh",
        "unit",
        "tests/unit/test_x.py",
        env=fake.environment(FAKE_EXIT="124"),
    )
    assert done.returncode == 124
    assert "TIMEOUT after 300 s" in done.stderr
    assert "do not raise" in done.stderr


def test_timeout_kill_exit_137_is_reported(fake: FakeRoot) -> None:
    """A child that exits 137 (what ``timeout`` returns after a forced kill) is
    reported (R4).

    Reference: the ``timeout`` command, which exits 137 when it had to send
    SIGKILL after ``--kill-after``. The fake interpreter exits 137; the wrapper
    returns 137 and prints a TIMEOUT line that names the tier's limit (300 s)
    and the code.
    """
    done = fake.run(
        "run_tests.sh",
        "unit",
        "tests/unit/test_x.py",
        env=fake.environment(FAKE_EXIT="137"),
    )
    assert done.returncode == 137
    assert (
        "TIMEOUT" in done.stderr
        and "137" in done.stderr
        and "300 s" in done.stderr
    )


def test_pytest_exit_code_is_returned(fake: FakeRoot) -> None:
    """pytest's own failure code (1) is passed on, so ``tools/test_impact.py
    --run`` sees it.
    """
    done = fake.run(
        "run_tests.sh",
        "unit",
        "tests/unit/test_x.py",
        env=fake.environment(FAKE_EXIT="1"),
    )
    assert done.returncode == 1
    assert "TIMEOUT" not in done.stderr


def test_allowed_extras_node_ids_and_directories(fake: FakeRoot) -> None:
    """``--lf``, ``--tb=long``, ``--durations=N``, a ``::`` test id and the tier
    folder pass.

    The extras follow the fixed flags and come before the paths, in the order
    given. The test id keeps its suffix. The tier folder is allowed because a
    gate runs one call per tier.
    """
    done = fake.run(
        "run_tests.sh",
        "unit",
        "--lf",
        "--tb=long",
        "--durations=5",
        "tests/unit/test_x.py::test_a[1 2]",
        "tests/unit",
    )
    assert done.returncode == 0, done.stderr
    assert only_call(fake)["argv"][2:] == FIXED_FLAGS + [
        "--lf",
        "--tb=long",
        "--durations=5",
        "tests/unit/test_x.py::test_a[1 2]",
        "tests/unit",
    ]


def test_relative_path_from_another_directory(fake: FakeRoot) -> None:
    """A path is read from the caller's folder and passed on relative to the
    root.
    """
    done = subprocess.run(
        [str(fake.root / "tools" / "run_tests.sh"), "unit", "test_x.py"],
        cwd=fake.root / "tests" / "unit",
        env=fake.environment(),
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    assert done.returncode == 0, done.stderr
    assert only_call(fake)["argv"][-1] == "tests/unit/test_x.py"


@pytest.mark.parametrize(
    ("args", "env"),
    [
        (["unit", "tests"], {}),
        (["unit", "tests/"], {}),
        (["unit", "."], {}),
        (["unit"], {}),
        (["unit", "tests/integration/test_x.py"], {}),
        (["unit", "tests/unit/../integration/test_x.py"], {}),
        (["unit", "tests/unit/test_missing.py"], {}),
        (["unit", "-n", "2", "tests/unit/test_x.py"], {}),
        (["unit", "-s", "tests/unit/test_x.py"], {}),
        (["unit", "-v", "tests/unit/test_x.py"], {}),
        (["unit", "--durations=abc", "tests/unit/test_x.py"], {}),
        (["unit", "--durations", "tests/unit/test_x.py"], {}),
        (["unit", "", "tests/unit/test_x.py"], {}),
        (["integration", "tests/unit/test_x.py"], {}),
        (["nosuchtier", "tests/unit/test_x.py"], {}),
        ([], {}),
        (["unit", "tests/unit/test_x.py"], {"LPC_THREADS": "0"}),
        (["unit", "tests/unit/test_x.py"], {"LPC_THREADS": "100"}),
        (["unit", "tests/unit/test_x.py"], {"LPC_THREADS": "four"}),
        (["gpu", "tests/gpu/test_x.py"], {"LPC_GPU_WAIT": "31"}),
        (["gpu", "tests/gpu/test_x.py"], {"LPC_GPU_WAIT": "-1"}),
        (["gpu", "tests/gpu/test_x.py"], {"LPC_GPU_WAIT": "abc"}),
        (["unit", "tests/unit/test_x.py"], {"PYTEST_ADDOPTS": "-n 2"}),
        (["unit", "tests/unit/test_x.py"], {"PYTEST_ADDOPTS": "-s"}),
        (["unit", "tests/unit/test_x.py"], {"PYTEST_PLUGINS": "xdist.plugin"}),
    ],
)
def test_refusals_exit_64_with_one_line(
    fake: FakeRoot, args: list[str], env: dict[str, str]
) -> None:
    """Whole-suite, wrong-tier, missing and flagged requests and bad limits give
    64 (e).

    Each refusal prints exactly one line on stderr and starts nothing (no fake
    call).
    """
    done = fake.run("run_tests.sh", *args, env=fake.environment(**env))
    assert done.returncode == 64, (done.stdout, done.stderr)
    assert len(done.stderr.strip().splitlines()) == 1, done.stderr
    assert fake.calls() == []
    assert fake.timeout_calls() == []


def test_background_logs_and_records_the_exit_code(fake: FakeRoot) -> None:
    """``--background`` prints ``pid=... log=...``, exits 0, and records the
    child's exit code.

    The code goes to ``<log>.exit``. Reference: the plan of WU-0012.1
    (``runs/tests/<tier>-<stamp>.log`` and ``<log>.exit``). The fake interpreter
    exits 3, so the exit file must hold ``3``. The test waits at most 5 s.
    """
    done = fake.run(
        "run_tests.sh",
        "slow",
        "--background",
        "tests/slow/test_x.py",
        env=fake.environment(FAKE_EXIT="3"),
    )
    assert done.returncode == 0, done.stderr
    fields = dict(part.split("=", 1) for part in done.stdout.split())
    log = Path(fields["log"])
    assert log.parent == fake.root / "runs" / "tests"
    assert log.name.startswith("slow-")
    exit_file = Path(str(log) + ".exit")
    deadline = time.monotonic() + 5.0
    while not exit_file.exists() and time.monotonic() < deadline:
        time.sleep(0.02)
    assert exit_file.read_text().strip() == "3"
    call = only_call(fake)
    assert call["argv"][2:5] == FIXED_FLAGS
    assert "--background" not in call["argv"]
    assert fake.timeout_calls()[0][:2] == ["--kill-after=30", "3600"]


def test_unopenable_lock_file_is_refused(fake: FakeRoot) -> None:
    """A lock path that cannot be opened gives exit 64 and one line.

    The wrapper must not quietly run without the lock.
    """
    done = fake.run(
        "run_tests.sh",
        "gpu",
        "tests/gpu/test_x.py",
        env=fake.environment(LPC_GPU_LOCK=str(fake.base / "missing" / "lock")),
    )
    assert done.returncode == 64
    assert len(done.stderr.strip().splitlines()) == 1, done.stderr
    assert fake.calls() == []
