"""Tests of ``tools/run_tests.sh``, the pytest wrapper (WU-0012.1, DEVELOPMENT_WORKFLOW.md 4.5).

Reference for every test: the contract of DEVELOPMENT_WORKFLOW.md 4.5 and 4.6 and the acceptance
criterion of WU-0012.1, applied by hand. The wrapper is run in a synthetic root in ``tmp_path``
(``wrapper_helpers.FakeRoot``) with a fake interpreter and a fake ``timeout`` that record what
they were called with; no real pytest, no real GPU lock. The expected values (``cpu``, ``4``,
``-q --tb=short -rfE``, the durations 300/900/3600/1800 s, the exit codes 64/75/124) are written
literally from the document, not taken from the wrapper.

Tolerance: none. Every outcome is a string, a set of arguments or an exit code, compared for
exact equality. The one timing check is the 30 s bound of 4.5 for the lock wait; the expected
elapsed time is about 1 s (``LPC_GPU_WAIT=1``) plus process start, and the bound is the one
in the criterion.
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
    """A synthetic root with run_tests.sh and the fakes."""
    return FakeRoot(tmp_path)


def only_call(fake: FakeRoot) -> dict:
    """Return the single recorded fake-interpreter call."""
    calls = fake.calls()
    assert len(calls) == 1, calls
    return calls[0]


def test_wrapper_is_executable() -> None:
    """The script exists and has the executable bit (definition of done; reference: os.stat)."""
    assert os.access(REPO / "tools" / "run_tests.sh", os.X_OK)


def test_unit_tier_environment_and_arguments(fake: FakeRoot) -> None:
    """Unit tier: cpu, 4/4/4 threads, preallocation off, argv has ``-q --tb=short -rfE`` (a).

    Reference: criterion text of WU-0012.1. The inherited JAX_PLATFORMS=cuda and
    OMP_NUM_THREADS=1 must be overridden; LPC_THREADS is unset, so the default 4 applies.
    """
    env = fake.environment(JAX_PLATFORMS="cuda", OMP_NUM_THREADS="1",
                           XLA_PYTHON_CLIENT_PREALLOCATE="true")
    done = fake.run("run_tests.sh", "unit", "tests/unit/test_x.py", env=env)
    assert done.returncode == 0, done.stderr
    call = only_call(fake)
    got = call["env"]
    assert got["JAX_PLATFORMS"] == "cpu"
    assert (got["OMP_NUM_THREADS"], got["MKL_NUM_THREADS"], got["OPENBLAS_NUM_THREADS"]) == \
        ("4", "4", "4")
    assert got["XLA_PYTHON_CLIENT_PREALLOCATE"] == "false"
    argv = call["argv"]
    assert argv[:2] == ["-m", "pytest"]
    assert argv[2:5] == FIXED_FLAGS, argv
    assert argv[5:] == ["tests/unit/test_x.py"]


def test_lpc_threads_is_copied_to_the_thread_variables(fake: FakeRoot) -> None:
    """``LPC_THREADS=3`` gives 3, 3, 3 (a); inherited larger values are overridden."""
    env = fake.environment(LPC_THREADS="3", OMP_NUM_THREADS="8", MKL_NUM_THREADS="8")
    done = fake.run("run_tests.sh", "unit", "tests/unit/test_x.py", env=env)
    assert done.returncode == 0, done.stderr
    got = only_call(fake)["env"]
    assert (got["OMP_NUM_THREADS"], got["MKL_NUM_THREADS"], got["OPENBLAS_NUM_THREADS"]) == \
        ("3", "3", "3")


@pytest.mark.parametrize("tier", ["integration", "slow"])
def test_other_cpu_tiers_force_cpu(fake: FakeRoot, tier: str) -> None:
    """The integration and slow tiers also run with JAX_PLATFORMS=cpu (4.5: CPU-only tiers)."""
    env = fake.environment(JAX_PLATFORMS="cuda")
    done = fake.run("run_tests.sh", tier, f"tests/{tier}/test_x.py", env=env)
    assert done.returncode == 0, done.stderr
    assert only_call(fake)["env"]["JAX_PLATFORMS"] == "cpu"


def test_gpu_tier_disables_preallocation(fake: FakeRoot) -> None:
    """Gpu tier: ``XLA_PYTHON_CLIENT_PREALLOCATE=false`` even if ``true`` is inherited (b).

    The fake lock is free, so the child runs. JAX_PLATFORMS is ``cuda,cpu`` (plan, 4.5).
    """
    env = fake.environment(XLA_PYTHON_CLIENT_PREALLOCATE="true")
    done = fake.run("run_tests.sh", "gpu", "tests/gpu/test_x.py", env=env)
    assert done.returncode == 0, done.stderr
    got = only_call(fake)["env"]
    assert got["XLA_PYTHON_CLIENT_PREALLOCATE"] == "false"
    assert got["JAX_PLATFORMS"] == "cuda,cpu"


def test_gpu_tier_exits_75_within_30_s_when_the_lock_is_held(fake: FakeRoot) -> None:
    """A competing lock holder gives exit 75 in under 30 s and the interpreter never runs (c).

    Reference: fcntl.flock in the test process, which is the same advisory lock as flock(1)
    on Linux. ``LPC_GPU_WAIT=1`` shortens the wait (about 1 s expected); the bound is the 30 s
    of the criterion.
    """
    with open(fake.lock, "w") as holder:
        fcntl.flock(holder, fcntl.LOCK_EX | fcntl.LOCK_NB)
        start = time.monotonic()
        done = fake.run("run_tests.sh", "gpu", "tests/gpu/test_x.py",
                        env=fake.environment(LPC_GPU_WAIT="1"))
        elapsed = time.monotonic() - start
    assert done.returncode == 75, done.stderr
    assert elapsed < 30.0
    assert fake.calls() == []
    assert len(done.stderr.strip().splitlines()) == 1


def test_gpu_tier_default_wait_is_30_s(fake: FakeRoot) -> None:
    """With a fake ``flock`` on the PATH, the call is ``flock -w 30 9`` (c)."""
    write_script(fake.bin / "flock", "#!/usr/bin/env bash\n"
                 'echo "$*" >>"$FAKE_DIR/flock.log"\nexit 0\n')
    done = fake.run("run_tests.sh", "gpu", "tests/gpu/test_x.py")
    assert done.returncode == 0, done.stderr
    assert (fake.fake_dir / "flock.log").read_text().splitlines() == ["-w 30 9"]


def test_cpu_tiers_take_no_lock(fake: FakeRoot) -> None:
    """A held lock does not block the unit tier (4.5: only the gpu tier is under the lock)."""
    with open(fake.lock, "w") as holder:
        fcntl.flock(holder, fcntl.LOCK_EX | fcntl.LOCK_NB)
        done = fake.run("run_tests.sh", "unit", "tests/unit/test_x.py")
    assert done.returncode == 0, done.stderr


@pytest.mark.parametrize("tier", TIERS)
def test_timeout_per_tier(fake: FakeRoot, tier: str) -> None:
    """The coreutils timeout is 300, 900, 3600 or 1800 s with a 30 s kill-after (d).

    Reference: DEVELOPMENT_WORKFLOW.md 4.5, "Timeouts".
    """
    done = fake.run("run_tests.sh", tier, f"tests/{tier}/test_x.py")
    assert done.returncode == 0, done.stderr
    calls = fake.timeout_calls()
    assert len(calls) == 1
    assert calls[0][:2] == ["--kill-after=30", TIMEOUTS[tier]], calls[0]


def test_timeout_exit_124_is_reported(fake: FakeRoot) -> None:
    """A child that exits 124 (what coreutils timeout returns) gives 124 and the TIMEOUT line (d)."""
    done = fake.run("run_tests.sh", "unit", "tests/unit/test_x.py",
                    env=fake.environment(FAKE_EXIT="124"))
    assert done.returncode == 124
    assert "TIMEOUT after 300 s" in done.stderr
    assert "do not raise" in done.stderr


def test_timeout_kill_exit_137_is_reported(fake: FakeRoot) -> None:
    """A child that exits 137 (what timeout returns after its kill grace) is reported (R4).

    Reference: coreutils timeout, which exits 137 when it had to SIGKILL after ``--kill-after``.
    The fake interpreter exits 137; the wrapper returns 137 and prints a TIMEOUT line that names
    the tier's limit (300 s) and the code.
    """
    done = fake.run("run_tests.sh", "unit", "tests/unit/test_x.py",
                    env=fake.environment(FAKE_EXIT="137"))
    assert done.returncode == 137
    assert "TIMEOUT" in done.stderr and "137" in done.stderr and "300 s" in done.stderr


def test_pytest_exit_code_is_returned(fake: FakeRoot) -> None:
    """pytest's own failure code (1) is returned, so ``tools/test_impact.py --run`` sees it."""
    done = fake.run("run_tests.sh", "unit", "tests/unit/test_x.py",
                    env=fake.environment(FAKE_EXIT="1"))
    assert done.returncode == 1
    assert "TIMEOUT" not in done.stderr


def test_allowed_extras_node_ids_and_directories(fake: FakeRoot) -> None:
    """``--lf``, ``--tb=long``, ``--durations=N``, a ``::`` node id and the tier directory pass.

    The extras follow the fixed flags and precede the paths, in the order given; the node id
    keeps its suffix; the tier directory (a gate runs one call per tier) is allowed.
    """
    done = fake.run("run_tests.sh", "unit", "--lf", "--tb=long", "--durations=5",
                    "tests/unit/test_x.py::test_a[1 2]", "tests/unit")
    assert done.returncode == 0, done.stderr
    assert only_call(fake)["argv"][2:] == FIXED_FLAGS + [
        "--lf", "--tb=long", "--durations=5", "tests/unit/test_x.py::test_a[1 2]", "tests/unit"]


def test_relative_path_from_another_directory(fake: FakeRoot) -> None:
    """A path is taken from the caller's directory and passed relative to the root."""
    done = subprocess.run(
        [str(fake.root / "tools" / "run_tests.sh"), "unit", "test_x.py"],
        cwd=fake.root / "tests" / "unit", env=fake.environment(), capture_output=True,
        text=True, timeout=20, check=False)
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
def test_refusals_exit_64_with_one_line(fake: FakeRoot, args: list[str],
                                        env: dict[str, str]) -> None:
    """Whole-suite, wrong-tier, missing and flagged invocations and bad limits give 64 (e).

    Each refusal prints exactly one line on stderr and starts nothing (no fake call).
    """
    done = fake.run("run_tests.sh", *args, env=fake.environment(**env))
    assert done.returncode == 64, (done.stdout, done.stderr)
    assert len(done.stderr.strip().splitlines()) == 1, done.stderr
    assert fake.calls() == []
    assert fake.timeout_calls() == []


def test_background_logs_and_records_the_exit_code(fake: FakeRoot) -> None:
    """``--background`` prints ``pid=… log=…``, exits 0, and writes the child's code to ``<log>.exit``.

    Reference: the plan of WU-0012.1 (runs/tests/<tier>-<stamp>.log and <log>.exit). The fake
    interpreter exits 3, so the exit file must hold ``3``. The test waits at most 5 s.
    """
    done = fake.run("run_tests.sh", "slow", "--background", "tests/slow/test_x.py",
                    env=fake.environment(FAKE_EXIT="3"))
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
    """A lock path that cannot be opened gives 64 and one line, not a silent run without the lock."""
    done = fake.run("run_tests.sh", "gpu", "tests/gpu/test_x.py",
                    env=fake.environment(LPC_GPU_LOCK=str(fake.base / "missing" / "lock")))
    assert done.returncode == 64
    assert len(done.stderr.strip().splitlines()) == 1, done.stderr
    assert fake.calls() == []
