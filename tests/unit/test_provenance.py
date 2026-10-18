"""Tests for ``lpcstudy.provenance``: the run provenance block (WU-0001.4).

The references are LPC.PC.18, LPC.PC.22 and LPC.PC.13. The provenance block
records what produced a result: the code commit, the settings, the library
versions, the machine and the timing. These tests check that every field is
present and correct, that git trouble is recorded and not hidden, and that the
confirmatory seed never appears.

The references are independent of ``lpcstudy/provenance.py``: the test's own
``git`` calls, the kernel's ``VmHWM`` counter, ``requirements.txt``,
``sys.version_info`` and a second clock. The confirmatory seed is never used;
the one below is synthetic (LPC.PC.7).
"""

from __future__ import annotations

import dataclasses
import datetime as dt
import hashlib
import json
import os
import platform
import re
import resource
import struct
import subprocess
import sys
import time
from importlib import metadata
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np
import pytest

import lpcstudy.systems  # noqa: F401  (enables x64 on import, as in a real run)
from lpcstudy import provenance
from lpcstudy.config import SMOKE
from lpcstudy.seeds import with_seed

ROOT = Path(__file__).resolve().parents[2]
SYNTHETIC_SEED = 987654321987654321
KEYS = (
    "schema",
    "seed_id",
    "seed_kind",
    "label",
    "promoted",
    "commit",
    "dirty",
    "git_error",
    "preset",
    "config",
    "argv",
    "python",
    "packages",
    "platform",
    "cpu",
    "blas",
    "numpy_simd",
    "device",
    "jax_x64",
    "jax_matmul_precision",
    "env",
    "start_utc",
    "end_utc",
    "wall_seconds",
    "peak_rss_bytes",
    "device_peak_bytes",
    "complete",
)
END_KEYS = (
    "end_utc",
    "wall_seconds",
    "peak_rss_bytes",
    "device_peak_bytes",
    "complete",
)


@pytest.fixture(autouse=True)
def _clean_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep each test away from a confirmatory seed or salt (LPC.PC.7)."""
    monkeypatch.delenv("LPC_CONF_SEED", raising=False)
    monkeypatch.delenv("LPC_CONF_SALT", raising=False)


def block_for(seed_id: str = "DEV-0", argv: list[str] | None = None) -> dict:
    """Collect a provenance block for the smoke preset."""
    seed = SYNTHETIC_SEED if seed_id.startswith("CONF-") else SMOKE.seed
    config = with_seed(SMOKE, seed_id, seed)
    return provenance.collect(
        config,
        seed_id,
        argv or ["--preset", "smoke"],
        provenance.RunClock(),
    )


def git(*args: str, cwd: Path = ROOT) -> str:
    """Run git in ``cwd`` (the test's own reference calls)."""
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def test_every_lpc_pc_18_field_is_present_in_order_and_typed() -> None:
    """The block has exactly the schema's keys, in order, with the schema's
    types.

    Reference: the field table of the plan (LPC.PC.18/.22/.13). Tolerance: none
    (exact key and type checks).
    """
    block = block_for()
    assert tuple(block) == KEYS
    assert (
        block["schema"] == "lpcstudy.provenance/2"
    )  # DEC-0023 (O1): the key set changed
    assert block["seed_id"] == "DEV-0" and block["seed_kind"] == "development"
    assert block["promoted"] is False and block["complete"] is False
    assert isinstance(block["commit"], str) and len(block["commit"]) == 40
    assert isinstance(block["dirty"], bool) and block["git_error"] is None
    assert block["preset"] == "smoke" and block["argv"] == ["--preset", "smoke"]
    assert isinstance(block["python"], str) and isinstance(
        block["platform"],
        str,
    )
    assert set(block["device"]) == {"backend", "kind", "count"}
    assert (
        isinstance(block["device"]["count"], int)
        and block["device"]["count"] >= 1
    )
    assert isinstance(block["jax_x64"], bool)
    assert block["jax_matmul_precision"] is None or isinstance(
        block["jax_matmul_precision"],
        str,
    )
    assert (
        block["end_utc"],
        block["wall_seconds"],
        block["peak_rss_bytes"],
        block["device_peak_bytes"],
    ) == (None, None, None, None)
    json.dumps(block)  # serializable without a default handler


def test_start_utc_is_iso_8601_utc_to_the_second() -> None:
    """``start_utc`` is an aware UTC time with no sub-second part, within the
    call span.

    Reference: ``datetime`` bounds taken around the call. The stamp is truncated
    to the second, so it lies in [before truncated to the second, after].
    """
    before = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    clock = provenance.RunClock()
    after = dt.datetime.now(dt.timezone.utc)
    start = dt.datetime.fromisoformat(clock.start_utc)
    assert start.utcoffset() == dt.timedelta(0) and start.microsecond == 0
    assert before <= start <= after


def test_commit_and_dirty_equal_the_tests_own_git_calls() -> None:
    """``commit`` is ``git rev-parse HEAD`` and ``dirty`` is ``bool(git status
    --porcelain)``.

    Reference: two ``git`` subprocesses run by the test at the same moment (the
    working tree does not change between them). Tolerance: none (exact string
    and boolean equality).
    """
    block = block_for()
    assert block["commit"] == git("rev-parse", "HEAD").strip()
    assert block["dirty"] == bool(git("status", "--porcelain").strip())


def test_git_failure_is_recorded_not_silent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Outside a repository, and with no ``git`` executable, the error is
    returned as text.

    Reference: the plan (``None, None, <error>``). ``tmp_path`` is not a
    repository (asserted with the test's own git call), and an empty ``PATH``
    removes the executable.
    """
    assert (
        subprocess.run(
            ["git", "-C", str(tmp_path), "rev-parse"],
            capture_output=True,
        ).returncode
        != 0
    )
    commit, dirty, error = provenance.git_state(tmp_path)
    assert (commit, dirty) == (None, None) and isinstance(error, str) and error
    monkeypatch.setenv("PATH", str(tmp_path))
    commit, dirty, error = provenance.git_state(ROOT)
    assert (commit, dirty) == (None, None) and "FileNotFoundError" in str(error)


def own_git_env() -> dict[str, str]:
    """Return the environment for the tests' own git calls.

    The variables that redirect git are removed. A suite started from a git hook
    has ``GIT_DIR`` or ``GIT_INDEX_FILE`` set; without this, the ``add`` and
    ``commit`` of a throwaway repository would act on the real repository. Only
    the redirecting variables are removed: a hazard test that needs
    ``GIT_CONFIG_*`` in the plain call inherits it.
    """
    return {
        k: v
        for k, v in os.environ.items()
        if k not in provenance.GIT_REDIRECT_VARIABLES
    }


def make_repository(path: Path, text: str = "one\n") -> Path:
    """Make a throwaway repository at ``path`` with one committed file
    ``tracked.txt``.

    It uses the test's own git calls.
    """
    path.mkdir()
    (path / "tracked.txt").write_text(text)
    for args in (
        ("init", "-q"),
        ("add", "tracked.txt"),
        (
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@example.org",
            "commit",
            "-q",
            "-m",
            "m",
        ),
    ):
        subprocess.run(
            ["git", "-C", str(path), *args],
            check=True,
            capture_output=True,
            env=own_git_env(),
        )
    return path


@pytest.fixture
def repository(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Provide a committed throwaway repository.

    ``GIT_CEILING_DIRECTORIES`` stops git from looking for a repository above
    it.
    """
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    return make_repository(tmp_path / "repo")


def plain_status(repo: Path, *extra: str) -> str:
    """Run ``git status --porcelain`` as a user would, plus ``extra`` (the
    test's own call).

    The environment keeps ``GIT_CONFIG*`` (a hazard test sets them) but not the
    redirect variables.
    """
    return subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain", *extra],
        check=True,
        capture_output=True,
        text=True,
        env=own_git_env(),
    ).stdout


def test_git_state_in_an_ordinary_repository_is_unchanged_by_the_hardening(
    repository: Path,
) -> None:
    """WU-0004a R2: clean is ``(HEAD, False)``; an untracked or edited tracked
    file is dirty.

    Reference: the repository is built by the test, so the state is known by
    construction, and ``commit`` is the test's own ``git rev-parse HEAD``.
    Tolerance: none (exact).
    """
    head = subprocess.run(
        ["git", "-C", str(repository), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
        env=own_git_env(),
    ).stdout.strip()
    assert provenance.git_state(repository) == (head, False, None)
    (repository / "new.txt").write_text("x\n")
    assert provenance.git_state(repository) == (head, True, None)
    (repository / "new.txt").unlink()
    (repository / "tracked.txt").write_text("two\n")
    assert provenance.git_state(repository) == (head, True, None)


def test_git_state_counts_untracked_files_whatever_the_git_configuration_says(
    repository: Path,
) -> None:
    """WU-0004a R2: ``status.showUntrackedFiles=no`` cannot hide an untracked
    file.

    Reference: the precondition is the test's own plain ``git status
    --porcelain``, which prints nothing under that setting while the file exists
    (so the hazard is real). The expected ``dirty`` is true by construction.
    """
    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "config",
            "status.showUntrackedFiles",
            "no",
        ],
        check=True,
        capture_output=True,
        env=own_git_env(),
    )
    (repository / "numpy.py").write_text("# would shadow the package\n")
    assert plain_status(repository) == ""
    assert provenance.git_state(repository)[1] is True


@pytest.mark.parametrize("bit", ["--skip-worktree", "--assume-unchanged"])
def test_git_state_counts_a_change_hidden_by_an_index_bit(
    repository: Path,
    bit: str,
) -> None:
    """WU-0004a R2: an edit hidden by skip-worktree or assume-unchanged still
    counts as dirty.

    Reference: the precondition is the test's own plain status, which prints
    nothing after the bit is set (the hazard is real). The file really differs
    from HEAD by construction (edited text).
    """
    subprocess.run(
        ["git", "-C", str(repository), "update-index", bit, "tracked.txt"],
        check=True,
        capture_output=True,
        env=own_git_env(),
    )
    (repository / "tracked.txt").write_text("hidden edit\n")
    assert plain_status(repository) == ""
    assert provenance.git_state(repository)[1] is True


def test_git_state_counts_a_file_hidden_by_excludes_file_in_config(
    repository: Path,
    tmp_path: Path,
) -> None:
    """WU-0004a R4: ``core.excludesFile`` naming the file cannot hide it.

    Reference: the precondition is the test's own status with the modes
    ``git_state`` names (``--untracked-files=normal``), which prints nothing
    while ``numpy.py`` exists, so the hazard is real. The expected ``dirty`` is
    true by construction.
    """
    ignore = tmp_path / "global_ignore"
    ignore.write_text("numpy.py\n")
    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "config",
            "core.excludesFile",
            str(ignore),
        ],
        check=True,
        capture_output=True,
        env=own_git_env(),
    )
    (repository / "numpy.py").write_text("# would shadow the package\n")
    assert plain_status(repository, "--untracked-files=normal") == ""
    assert provenance.git_state(repository)[1] is True


def test_git_state_counts_a_file_hidden_by_excludes_file_in_environment(
    repository: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """WU-0004a R4: the same setting given as
    ``GIT_CONFIG_COUNT``/``KEY_0``/``VALUE_0``.

    Reference: as above; the precondition status inherits the injected variables
    and prints nothing, so the hazard is real. ``GIT_CONFIG_*`` must be removed
    from git's environment.
    """
    ignore = tmp_path / "env_ignore"
    ignore.write_text("numpy.py\n")
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "core.excludesFile")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", str(ignore))
    (repository / "numpy.py").write_text("# would shadow the package\n")
    assert plain_status(repository, "--untracked-files=normal") == ""
    assert provenance.git_state(repository)[1] is True


def test_git_state_does_not_count_a_file_ignored_by_a_tracked_gitignore(
    repository: Path,
) -> None:
    """Accepted limitation, pinned: the project's own ``.gitignore`` is honored.

    Reference: construction. After committing a ``.gitignore`` that names
    ``runs/``, a file in ``runs/`` is not dirty (the repository's real ``runs/``
    output directory is ignored this way, so a development run next to its own
    output stays clean). An untracked file that the ``.gitignore`` does not name
    is dirty, and so is an untracked ``.gitignore`` itself.
    """
    (repository / ".gitignore").write_text("runs/\n")
    for args in (
        ("add", ".gitignore"),
        (
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@example.org",
            "commit",
            "-q",
            "-m",
            "g",
        ),
    ):
        subprocess.run(
            ["git", "-C", str(repository), *args],
            check=True,
            capture_output=True,
            env=own_git_env(),
        )
    (repository / "runs").mkdir()
    (repository / "runs" / "results.json").write_text("{}\n")
    assert provenance.git_state(repository)[1] is False
    (repository / "other.txt").write_text("x\n")
    assert provenance.git_state(repository)[1] is True
    (repository / "other.txt").unlink()
    (repository / "sub").mkdir()
    (repository / "sub" / ".gitignore").write_text("*.tmp\n")
    assert provenance.git_state(repository)[1] is True


def test_git_state_ignores_a_git_dir_that_points_elsewhere(
    repository: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """WU-0004a R2: ``GIT_DIR`` and ``GIT_INDEX_FILE`` in the environment do not
    redirect it.

    Reference: a second repository with other content (so another HEAD) is dirty
    by construction. The precondition is the test's own ``git -C <repository>
    rev-parse HEAD`` with the variable set, which returns the other repository's
    HEAD (the hazard is real). ``git_state`` must still return the queried
    repository's own HEAD and a clean state.
    """
    other = make_repository(tmp_path / "other", text="different\n")
    (other / "dirty.txt").write_text("x\n")
    own = subprocess.run(
        ["git", "-C", str(repository), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
        env=own_git_env(),
    ).stdout.strip()
    monkeypatch.setenv("GIT_DIR", str(other / ".git"))
    monkeypatch.setenv("GIT_INDEX_FILE", str(other / ".git" / "index"))
    redirected = subprocess.run(
        ["git", "-C", str(repository), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert redirected != own
    assert provenance.git_state(repository) == (own, False, None)


def test_peak_rss_is_positive_and_bracketed_by_the_kernel_counter() -> None:
    """``peak_rss_bytes`` is positive, whole pages, and (on Linux) bracketed by
    ``VmHWM``.

    ``VmHWM`` is the kernel's own high-water mark of memory use.

    Reference: ``VmHWM`` (kB, the kernel's high-water mark) from
    ``/proc/self/status`` read before and after the call; ``ru_maxrss`` is the
    same counter in KiB, so ``1024 VmHWM_before - 2T <= peak <= 1024 VmHWM_after
    + 2T``. The roadmap criterion is ``peak > 0``, asserted exactly.

    Tolerance (applied-mathematician, WU-0001 Log 2026-10-10; DEC-0006
    proposed). Since Linux 6.2 the RSS is three ``percpu_counter``s (file, anon,
    shmem). ``getrusage`` reads them approximately; each per-CPU delta is below
    the batch ``b = max(32, 2n)`` (n = online CPUs), so the read is within ``T =
    3 n (b - 1)`` pages of the exact sum (24.8 MB at n = 32; attained per
    counter in a probe, WU-0001 Log 2026-10-10). ``VmHWM`` is the exact sum
    (approximate before about 6.16) and ``mm->hiwater_rss`` is refreshed by an
    approximate read before RSS falls, so the bracket above holds.

    Assumptions: no CPU hotplug, ``clear_refs`` or reclaim between the two
    reads; the process was not exec'd (vfork, fork or exec-in-place) from a
    process whose peak exceeds the upper bound, because ``ru_maxrss`` includes
    the pre-exec image (``signal->maxrss``), which ``VmHWM`` does not. A failure
    on the upper side with a large launcher is that, not a code defect.

    Power: with ``1024 VmHWM >= 182 MB`` (after importing jax) and ``2T = 49.5
    MB``, the bracket rejects a missing x1024 (E/1024), x4096 (4E) and any
    factor-2 error. ``ru_maxrss`` is pages x PAGE_SIZE/1024 KiB, so ``peak %
    pagesize == 0`` holds exactly and also catches x1000 and sub-page offsets.
    Neither check resolves a one-page additive error (kernel noise is about 10^3
    pages). ``os.sysconf("SC_NPROCESSORS_ONLN")`` is used, not
    ``os.cpu_count()``, which ``PYTHON_CPU_COUNT`` can override.

    Limitation of the quantity (not of the test): a child process inherits its
    parent's peak in ``ru_maxrss``, so the recorded ``peak_rss_bytes`` can
    reflect the launcher's peak.
    """

    def hwm() -> int:
        for line in Path("/proc/self/status").read_text().splitlines():
            if line.startswith("VmHWM:"):
                return int(line.split()[1])
        raise AssertionError("VmHWM not found")

    assert provenance.peak_rss_bytes() > 0
    if not sys.platform.startswith("linux"):
        pytest.skip(
            "VmHWM exists on Linux only; the positivity check above ran"
        )
    page = resource.getpagesize()
    before = hwm()
    peak = provenance.peak_rss_bytes()
    after = hwm()
    online = os.sysconf("SC_NPROCESSORS_ONLN")
    counter_error = 3 * online * (max(32, 2 * online) - 1) * page
    assert (
        peak % page == 0
    ), f"peak {peak} B is not a whole number of {page} B pages"
    assert (
        1024 * before - 2 * counter_error
        <= peak
        <= 1024 * after + 2 * counter_error
    ), (
        f"peak {peak} B outside [{1024 * before}, {1024 * after}] B +- "
        f"{2 * counter_error} B"
    )


def test_wall_seconds_is_within_one_percent_of_own_clock() -> None:
    """``finish(block, clock)["wall_seconds"]`` over a 1 s sleep agrees with a
    second clock.

    Reference: ``t0 = perf_counter(); clock = RunClock(); block = collect(...);
    sleep(1.0); done = finish(block, clock); t1 = perf_counter()``; the
    reference span is ``t1 - t0``. Both clocks span the same collect and sleep.

    Tolerance: 1% of the span (about 10 ms), the criterion's own. The two spans
    differ only by the constructor, the end-time stamp and the memory queries
    (microseconds) plus one possible preemption, far below 10 ms. The span (1 s
    of sleep plus the git calls of ``collect``) is long enough that 1% is well
    above timer noise.
    """
    t0 = time.perf_counter()
    clock = provenance.RunClock()
    block = provenance.collect(
        with_seed(SMOKE, "DEV-0", SMOKE.seed),
        "DEV-0",
        [],
        clock,
    )
    time.sleep(1.0)
    done = provenance.finish(block, clock)
    t1 = time.perf_counter()
    assert abs(done["wall_seconds"] - (t1 - t0)) <= 0.01 * (t1 - t0)


def test_python_version_equals_sys_version_info() -> None:
    """``python`` is the interpreter's ``major.minor.micro``.

    Reference: ``sys.version_info``. Tolerance: none (exact).
    """
    assert block_for()["python"] == "%d.%d.%d" % sys.version_info[:3]


def test_package_versions_equal_the_requirements_pins() -> None:
    """Each recorded package version equals its pin in ``requirements.txt``.

    Reference: the pins parsed from ``requirements.txt`` by the test. A mismatch
    is an LPC.PC.17 finding about the environment, never a reason to change this
    test. Tolerance: none (exact).
    """
    pins = {}
    for line in (ROOT / "requirements.txt").read_text().splitlines():
        text = line.split("#")[0].strip()
        if "==" in text:
            name, version = text.split("==")
            pins[name.split("[")[0]] = version
    packages = block_for()["packages"]
    assert set(packages) == {
        "jax",
        "jaxlib",
        "optax",
        "numpy",
        "scipy",
        "scikit-learn",
        "matplotlib",
    }
    assert packages == {name: pins[name] for name in packages}


def test_uninstalled_package_is_recorded_as_null(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A package that is not installed is recorded as ``None``, the others
    unchanged.

    Reference: ``importlib.metadata.version`` patched to raise
    ``PackageNotFoundError`` for ``optax`` only (the caller counts and logs the
    nulls).
    """
    real = metadata.version

    def version(name: str) -> str:
        if name == "optax":
            raise metadata.PackageNotFoundError(name)
        return real(name)

    monkeypatch.setattr(provenance.metadata, "version", version)
    packages = block_for()["packages"]
    assert packages["optax"] is None
    assert all(v is not None for k, v in packages.items() if k != "optax")


def test_jax_x64_equals_the_default_float_dtype() -> None:
    """``jax_x64`` is true exactly when ``jnp.zeros(1)`` is float64 (after
    importing systems).

    Reference: the dtype of a fresh jax array. Tolerance: none (exact); and the
    study requires it to be true.
    """
    enabled = jnp.zeros(1).dtype == jnp.float64
    assert enabled is True or bool(enabled) is True
    assert block_for()["jax_x64"] is bool(enabled)


def test_device_is_the_cpu_backend_under_jax_platforms_cpu() -> None:
    """``device.backend`` is ``cpu`` with the project default
    ``JAX_PLATFORMS=cpu``.

    Reference: the environment (``settings.json`` default); ``jax.devices()``
    for the kind and count. Tolerance: none (exact).
    """
    assert (
        os.environ.get("JAX_PLATFORMS") == "cpu"
    ), "tests run under JAX_PLATFORMS=cpu"
    device = block_for()["device"]
    assert device["backend"] == "cpu" == jax.default_backend()
    assert (
        device["count"] == len(jax.devices())
        and device["kind"] == jax.devices()[0].device_kind
    )


def test_env_block_has_the_listed_names_and_never_the_confirmatory_variables(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``env`` records the eleven listed variables and never ``LPC_CONF_*``.

    Reference: the plan's list (the nine of WU-0001.4 and WU-0012.5, then the
    two of WU-0001.6). The confirmatory variables are set to a synthetic value
    that must not appear anywhere in the block. Tolerance: none (exact).
    """
    monkeypatch.setenv("LPC_CONF_SEED", "424242424242")
    monkeypatch.setenv("LPC_CONF_SALT", "ab" * 16)
    monkeypatch.setenv("OMP_NUM_THREADS", "3")
    block = block_for("CONF-1", ["--confirmatory"])
    assert set(block["env"]) == {
        "JAX_PLATFORMS",
        "XLA_FLAGS",
        "XLA_PYTHON_CLIENT_PREALLOCATE",
        "LPC_THREADS",
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "PJRT_NPROC",
        "NPROC",
        "OPENBLAS_CORETYPE",
        "NPY_DISABLE_CPU_FEATURES",
    }
    assert block["env"]["OMP_NUM_THREADS"] == "3"
    text = json.dumps(block)
    assert (
        "424242424242" not in text
        and "ab" * 16 not in text
        and "LPC_CONF" not in text
    )


def test_env_block_records_the_xla_thread_cap_variables(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``env`` records ``PJRT_NPROC`` and ``NPROC`` as set, and ``None`` when
    unset (LPC.PC.18).

    Reference: the values the test itself puts in the environment (a synthetic
    "7" and "5", distinct from each other and from the budget of 4, so a swapped
    or defaulted value fails). The names are appended after the earlier seven
    (and are followed by the two names of WU-0001.6). Tolerance: none (exact).
    """
    assert provenance.ENV_NAMES[7:9] == ("PJRT_NPROC", "NPROC")
    monkeypatch.setenv("PJRT_NPROC", "7")
    monkeypatch.setenv("NPROC", "5")
    assert block_for("DEV-0", [])["env"]["PJRT_NPROC"] == "7"
    assert block_for("DEV-0", [])["env"]["NPROC"] == "5"
    monkeypatch.delenv("PJRT_NPROC")
    monkeypatch.delenv("NPROC")
    env = block_for("DEV-0", [])["env"]
    assert env["PJRT_NPROC"] is None and env["NPROC"] is None


def test_confirmatory_block_nulls_the_seed_and_labels_it() -> None:
    """A ``CONF-1`` block holds the id and the label but not the seed value.

    Reference: the synthetic seed literal. The value appears nowhere in the
    serialized block; ``config.seed`` is ``None``; every other config field
    equals the preset's. Tolerance: none (exact).
    """
    block = block_for("CONF-1", ["--confirmatory"])
    assert block["seed_id"] == "CONF-1" and block["seed_kind"] == "confirmatory"
    assert (
        block["label"] == "CONFIRMATORY: UNPROMOTED"
        and block["promoted"] is False
    )
    assert str(SYNTHETIC_SEED) not in json.dumps(block)
    assert (
        block["config"]["seed"] is None
        and block["config"]["seed_id"] == "CONF-1"
    )
    expected = dataclasses.asdict(SMOKE) | {"seed": None, "seed_id": "CONF-1"}
    assert json.loads(json.dumps(block["config"])) == json.loads(
        json.dumps(expected)
    )


def test_development_block_keeps_the_full_config() -> None:
    """A ``DEV-0`` block's config equals ``dataclasses.asdict`` of the config
    exactly.
    """
    block = block_for()
    assert block["label"] == "DEVELOPMENT (DEV-0): not a hypothesis test"
    assert block["config"] == dataclasses.asdict(
        with_seed(SMOKE, "DEV-0", SMOKE.seed)
    )


def test_header_label_rejects_other_ids() -> None:
    """``header_label`` accepts only ``DEV-n`` and ``CONF-n``."""
    assert (
        provenance.header_label("DEV-3")
        == "DEVELOPMENT (DEV-3): not a hypothesis test"
    )
    for bad in ("", "dev-1", "5", "X-1"):
        with pytest.raises(ValueError):
            provenance.header_label(bad)


def test_finish_completes_a_copy_and_leaves_the_original() -> None:
    """``finish`` returns a completed copy; the original block is untouched.

    Reference: the field table (end fields filled, ``complete`` true).
    ``wall_seconds`` is bracketed by the test's own clock, ``end_utc`` is not
    before ``start_utc``, and on the CPU backend ``device_peak_bytes`` is
    ``None`` (no device statistics). Tolerance: none (exact, and ordering).
    """
    t0 = time.perf_counter()
    clock = provenance.RunClock()
    block = provenance.collect(
        with_seed(SMOKE, "DEV-0", SMOKE.seed),
        "DEV-0",
        [],
        clock,
    )
    done = provenance.finish(block, clock)
    t1 = time.perf_counter()
    assert block["complete"] is False and block["end_utc"] is None
    assert done["complete"] is True
    assert 0.0 <= done["wall_seconds"] <= t1 - t0
    assert dt.datetime.fromisoformat(
        done["end_utc"]
    ) >= dt.datetime.fromisoformat(block["start_utc"])
    assert (
        isinstance(done["peak_rss_bytes"], int) and done["peak_rss_bytes"] > 0
    )
    assert done["device_peak_bytes"] is None
    assert {k: v for k, v in done.items() if k not in END_KEYS} == {
        k: v for k, v in block.items() if k not in END_KEYS
    }


# WU-0001.6: the platform record (DEC-0022 item 4; DEF-0024).

FLAG_LIST = (
    "sse4_1",
    "sse4_2",
    "avx",
    "avx2",
    "fma",
    "f16c",
    "bmi1",
    "bmi2",
    "avx_vnni",
    "avx512f",
    "avx512dq",
    "avx512cd",
    "avx512bw",
    "avx512vl",
    "avx512_vnni",
    "avx512_bf16",
    "avx512_fp16",
    "amx_tile",
)  # the mathematician's list (M4, B)


def reference_digest(values: list[float]) -> str:
    """Return the SHA-256 of the values packed as little-endian binary64.

    The test's own byte writer (``struct``) does the packing.
    """
    return hashlib.sha256(
        struct.pack("<%dd" % len(values), *values)
    ).hexdigest()


def test_array_digest_equals_sha256_of_struct_packed_little_endian_bytes() -> (
    None
):
    """``array_digest`` is the SHA-256 of the row-major little-endian binary64
    bytes (A1).

    Reference: ``hashlib.sha256(struct.pack("<%dd", ...))``, written here with
    ``struct``, not with numpy ``tobytes``. Two matrices (one with 0.1, 1/3,
    1e-300, -2.5 and the smallest subnormal 5e-324). Tolerance: none (exact; a
    digest is a deterministic function of the bytes).
    """
    first = [[1.0, 2.0], [3.0, 4.0]]
    second = [
        [0.1, 1.0 / 3.0, 1e-300],
        [-2.5, 5e-324, 7.0],
        [0.0, 1e300, -1e-5],
    ]
    for matrix in (first, second):
        flat = [v for row in matrix for v in row]
        digest = provenance.array_digest(np.array(matrix, dtype=np.float64))
        assert digest == reference_digest(flat)
        assert re.fullmatch(r"[0-9a-f]{64}", digest)


def test_array_digest_ignores_layout_and_byte_order() -> None:
    """Memory layout and byte order do not change ``array_digest``, but element
    order does (A1).

    A Fortran-ordered copy and a ``>f8`` copy give the C-order ``<f8`` digest.

    Reference: the struct digest of the row-major values. The digest is of the
    *logical* row-major sequence, so the transpose (same values, other order)
    differs: W and U are not bitwise symmetric, so the order is load-bearing
    (M2). Signed zeros differ (bitwise identity).
    """
    matrix = np.array(
        [[0.1, 1.0 / 3.0, -2.5], [5e-324, 7.0, 1e300], [2.0, -0.5, 3.0]]
    )
    expected = reference_digest(matrix.ravel().tolist())
    assert provenance.array_digest(matrix) == expected
    assert provenance.array_digest(np.asfortranarray(matrix)) == expected
    assert provenance.array_digest(matrix.astype(">f8")) == expected
    assert provenance.array_digest(matrix.T) != expected
    assert provenance.array_digest(np.array([0.0])) != provenance.array_digest(
        np.array([-0.0])
    )
    assert provenance.array_digest(np.array([-0.0])) == reference_digest([-0.0])


def test_array_digest_rejects_every_non_binary64_dtype() -> None:
    """float16, float32, longdouble, int, complex and object raise ``TypeError``
    (M2, PRIME.4).

    Reference: the plan (a conversion would be silent). Tolerance: none (exact).
    """
    for dtype in (
        np.float16,
        np.float32,
        np.longdouble,
        np.int64,
        np.int32,
        np.complex128,
        np.bool_,
        object,
    ):
        with pytest.raises(TypeError):
            provenance.array_digest(np.zeros(3, dtype=dtype))


def test_provenance_env_names_append_the_two_kernel_choices() -> None:
    """``ENV_NAMES`` ends with ``OPENBLAS_CORETYPE`` and
    ``NPY_DISABLE_CPU_FEATURES`` (A5).

    Reference: the plan (the old tuple, then the two names). Tolerance: none
    (exact).
    """
    assert provenance.ENV_NAMES[-2:] == (
        "OPENBLAS_CORETYPE",
        "NPY_DISABLE_CPU_FEATURES",
    )
    assert (
        len(provenance.ENV_NAMES) == 11 and len(set(provenance.ENV_NAMES)) == 11
    )


def test_platform_keys_have_the_scope_types_and_serialize(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``cpu``, ``blas`` and ``numpy_simd`` have the planned keys and types
    (A5).

    Reference: the plan's Scope. ``OPENBLAS_CORETYPE`` and
    ``NPY_DISABLE_CPU_FEATURES`` are recorded as set and ``None`` when unset.
    Tolerance: none (exact).
    """
    monkeypatch.delenv("OPENBLAS_CORETYPE", raising=False)
    monkeypatch.delenv("NPY_DISABLE_CPU_FEATURES", raising=False)
    block = block_for()
    assert block["env"]["OPENBLAS_CORETYPE"] is None
    assert block["env"]["NPY_DISABLE_CPU_FEATURES"] is None
    assert set(block["cpu"]) == {"model", "source", "isa", "error"}
    assert isinstance(block["cpu"]["model"], str) and block["cpu"]["model"]
    assert block["cpu"]["source"] in (
        "/proc/cpuinfo",
        "platform.processor",
        "none",
    )
    assert isinstance(block["cpu"]["isa"], list)
    assert set(block["blas"]) == {"libraries", "error"}
    for entry in block["blas"]["libraries"]:
        assert set(entry) == {"library", "corename", "config", "error"}
    assert set(block["numpy_simd"]) == {"found", "error"}
    assert (
        isinstance(block["numpy_simd"]["found"], list)
        and block["numpy_simd"]["error"] is None
    )
    monkeypatch.setenv("OPENBLAS_CORETYPE", "Sandybridge")
    monkeypatch.setenv("NPY_DISABLE_CPU_FEATURES", "AVX2")
    env = block_for()["env"]
    assert env["OPENBLAS_CORETYPE"] == "Sandybridge"
    assert env["NPY_DISABLE_CPU_FEATURES"] == "AVX2"
    json.dumps(block)


def _own_cpuinfo() -> tuple[str, list[str]]:
    """Parse ``/proc/cpuinfo`` in the test itself.

    Returns the first ``model name`` and the ISA flag subset (sorted).
    """
    text = Path("/proc/cpuinfo").read_text()
    model = re.search(r"^model name\s*:\s*(.*)$", text, re.MULTILINE)
    flags = re.search(r"^flags\s*:\s*(.*)$", text, re.MULTILINE)
    assert (
        model and flags
    ), "this host must expose model name and flags (x86 Linux)"
    return model.group(1).strip(), sorted(
        set(flags.group(1).split()) & set(FLAG_LIST)
    )


def test_cpu_record_equals_the_tests_own_parse_of_proc_cpuinfo() -> None:
    """On this host ``cpu`` equals the test's own regex parse of
    ``/proc/cpuinfo`` (A6, B).

    Reference: ``re`` over the file text, written in the test, not shared with
    the code. The ISA is the sorted intersection of the first ``flags`` line
    with the fixed list. Tolerance: none (exact).
    """
    model, isa = _own_cpuinfo()
    record = provenance.cpu_record()
    assert record == {
        "model": model,
        "source": "/proc/cpuinfo",
        "isa": isa,
        "error": None,
    }
    assert all(flag in FLAG_LIST for flag in record["isa"])


class _Unreadable:
    """A stand-in for a path whose ``read_text`` raises ``exc`` (or returns
    ``text``).

    It replaces ``/proc/cpuinfo`` and ``/proc/self/maps`` in the tests.
    """

    def __init__(self, exc: Exception | None, text: str = "") -> None:
        self.exc, self.text = exc, text

    def read_text(self, *args: object, **kwargs: object) -> str:
        if self.exc is not None:
            raise self.exc
        return self.text


@pytest.mark.parametrize(
    "source",
    [
        _Unreadable(FileNotFoundError("gone")),
        _Unreadable(PermissionError("denied")),
        _Unreadable(UnicodeDecodeError("utf-8", b"\xff", 0, 1, "bad byte")),
        _Unreadable(None, "processor : 0\nvendor_id : Test\n"),
    ],
)
def test_cpu_record_never_raises_and_falls_back(
    source: _Unreadable,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unreadable or model-less ``/proc/cpuinfo`` gives the fallback record, no
    exception (A6).

    Reference: the plan. With ``platform.processor()`` empty the record is model
    "unknown", source "none"; with "test-cpu" it is that value with source
    "platform.processor"; the ISA is ``[]`` (no flags line) in both. The read
    error is recorded (``<Type>: <msg>``), never dropped; the model-less text
    records no error. Tolerance: none (exact).
    """
    monkeypatch.setattr(provenance, "CPUINFO", source)
    monkeypatch.setattr(platform, "processor", lambda: "")
    record = provenance.cpu_record()
    assert (
        record["model"] == "unknown"
        and record["source"] == "none"
        and record["isa"] == []
    )
    if source.exc is None:
        assert record["error"] is None
    else:
        assert str(record["error"]).startswith(type(source.exc).__name__ + ":")
    monkeypatch.setattr(platform, "processor", lambda: "test-cpu")
    record = provenance.cpu_record()
    assert (
        record["model"] == "test-cpu"
        and record["source"] == "platform.processor"
    )
    assert record["isa"] == []
    json.dumps(record)


def test_cpu_isa_is_sorted_and_restricted_to_the_fixed_list(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``isa`` is the sorted intersection of the *first* ``flags`` line with the
    fixed list (B).

    Reference: a hand-written cpuinfo text with two processors. The second line
    has a flag (``amx_tile``) that must not be read; the first has flags outside
    the list (``pti``, ``ibrs``; ``avx512f`` is inside) in scrambled order.
    Expected by hand. Tolerance: none (exact).
    """
    text = (
        "processor\t: 0\nmodel name\t: Test CPU @ 1GHz\n"
        "flags\t\t: fpu pti avx512f ibrs sse4_2 fma avx2 zzz sse4_1\n\n"
        "processor\t: 1\nmodel name\t: Other\nflags\t\t: amx_tile avx\n"
    )
    monkeypatch.setattr(provenance, "CPUINFO", _Unreadable(None, text))
    assert provenance.cpu_record() == {
        "model": "Test CPU @ 1GHz",
        "source": "/proc/cpuinfo",
        "isa": ["avx2", "avx512f", "fma", "sse4_1", "sse4_2"],
        "error": None,
    }


def test_regression_simd_record_equals_the_show_config_it_wraps() -> None:
    """Regression guard (not correctness evidence): ``simd_record`` repeats the
    numpy call it wraps.

    It compares the code with ``np.show_config(mode="dicts")``, the call under
    test, so it only guards the key path and the ``[]`` default. The independent
    truth is the test at the end of this file (R3).
    """
    config = np.show_config(mode="dicts")
    expected = list(config.get("SIMD Extensions", {}).get("found", []))
    assert provenance.simd_record() == {"found": expected, "error": None}


def test_blas_record_lists_numpy_and_scipy_openblas_with_a_corename() -> None:
    """There is one OpenBLAS entry under ``numpy.libs`` and one under
    ``scipy.libs``, each with a corename (A7).

    Reference: the wheels' layout (``numpy.libs/libscipy_openblas64_*.so`` and
    ``scipy.libs/libscipy_openblas*.so``); the corename is a non-empty string
    and ``error`` is ``None``. Tolerance: none (exact). Importing ``provenance``
    imports ``scipy.linalg``, so scipy's library is mapped.
    """
    record = provenance.blas_record()
    assert record["error"] is None
    libraries = [entry["library"] for entry in record["libraries"]]
    assert sum(name.startswith("numpy.libs/") for name in libraries) == 1
    assert sum(name.startswith("scipy.libs/") for name in libraries) == 1
    for entry in record["libraries"]:
        assert isinstance(entry["corename"], str) and entry["corename"]
        assert (
            entry["error"] is None
            and isinstance(entry["config"], str)
            and entry["config"]
        )
        assert "openblas" in entry["library"]


FORCED_PROBE = (
    "import json, sys; sys.path.insert(0, sys.argv[1]); from lpcstudy import "
    "provenance; "
    "print(json.dumps(provenance.blas_record()))"
)


@pytest.mark.parametrize("coretype", ["Sandybridge", "Haswell"])
def test_blas_record_follows_a_forced_kernel(coretype: str) -> None:
    """Forcing ``OPENBLAS_CORETYPE`` changes the recorded corename of both
    libraries (A7).

    Reference: known truth by construction. A fresh interpreter (``python -I``,
    so nothing but the forced variable differs) runs the probe with
    ``OPENBLAS_CORETYPE=<coretype>``; OpenBLAS on x86-64 honors the request when
    the CPU supports it (Sandybridge and Haswell are both supported on the
    reference platform, DEC-0022). Tolerance: none (exact string equality).
    """
    assert (
        platform.machine() == "x86_64"
    ), "the reference platform is x86-64 (DEC-0022)"
    env = dict(os.environ, OPENBLAS_CORETYPE=coretype)
    done = subprocess.run(
        [sys.executable, "-I", "-c", FORCED_PROBE, str(ROOT)],
        env=env,
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )
    record = json.loads(done.stdout)
    assert len(record["libraries"]) == 2
    assert [e["corename"] for e in record["libraries"]] == [coretype, coretype]


def test_blas_record_never_raises_when_the_library_cannot_be_opened(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``CDLL`` raising ``OSError`` gives entries with corename ``None`` and an
    ``OSError`` error.

    Reference: the plan (every probe records ``<Type>: <msg>``, never raises).
    Tolerance: none (exact).
    """

    def refuse(*args: object, **kwargs: object) -> None:
        raise OSError("refused")

    monkeypatch.setattr(provenance.ctypes, "CDLL", refuse)
    record = provenance.blas_record()
    assert len(record["libraries"]) == 2 and record["error"] is None
    for entry in record["libraries"]:
        assert entry["corename"] is None and entry["config"] is None
        assert entry["error"] == "OSError: refused"
    json.dumps(record)


def test_blas_record_never_raises_when_the_symbols_are_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A library object without any of the symbols gives an ``AttributeError``
    error (A7).

    Reference: an object with no attributes stands in for the ``CDLL`` handle.
    Tolerance: none (exact prefix of the recorded error).
    """

    class Empty:
        pass

    monkeypatch.setattr(provenance.ctypes, "CDLL", lambda *a, **k: Empty())
    record = provenance.blas_record()
    assert len(record["libraries"]) == 2
    for entry in record["libraries"]:
        assert entry["corename"] is None and entry["error"].startswith(
            "AttributeError"
        )
    json.dumps(record)


def test_blas_record_never_raises_when_proc_self_maps_is_unreadable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Failing to read ``/proc/self/maps`` gives ``libraries == []`` and a
    top-level error (A7).

    Reference: the plan. ``collect`` still returns a serializable block.
    Tolerance: none (exact).
    """
    monkeypatch.setattr(provenance, "MAPS", _Unreadable(OSError("no maps")))
    record = provenance.blas_record()
    assert record["libraries"] == [] and record["error"] == "OSError: no maps"
    assert json.loads(json.dumps(block_for()["blas"]))["libraries"] == []


def test_probe_errors_lists_each_failed_probe_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``probe_errors`` is empty for a healthy block and counts each recorded
    failure (A7).

    Reference: the plan (a failed probe is recorded, and the caller counts and
    logs it). The healthy host block gives ``[]``; a block with a failed ``cpu``
    read, an unreadable maps file and a failed library each add one text.
    Tolerance: none (exact).
    """
    assert provenance.probe_errors(block_for()) == []
    with monkeypatch.context() as patch:
        patch.setattr(provenance, "CPUINFO", _Unreadable(OSError("no cpuinfo")))
        patch.setattr(provenance, "MAPS", _Unreadable(OSError("no maps")))
        patch.setattr(platform, "processor", lambda: "")
        patch.setattr(platform, "machine", lambda: "x86_64")
        # the failed read, then the two silent fallbacks it causes (model
        # source, empty ISA)
        assert provenance.probe_errors(block_for()) == [
            "cpu: OSError: no cpuinfo",
            "cpu: model from none",
            "cpu: no ISA flags found on x86_64",
            "blas: OSError: no maps",
        ]

    def refuse(*args: object, **kwargs: object) -> None:
        raise OSError("refused")

    with monkeypatch.context() as patch:
        patch.setattr(provenance.ctypes, "CDLL", refuse)
        failed = provenance.probe_errors(block_for())
    assert len(failed) == 2 and all(
        text.endswith("OSError: refused") for text in failed
    )


def test_probe_errors_counts_each_silent_fallback_r2(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """R2: a fallback that raises nothing is still counted, one text per state.

    Reference: hand-written expected lists (the review's R2): the CPU model from
    ``platform.processor``; no ``flags`` line on x86-64 (and none to report
    elsewhere); and a probe of ``/proc/self/maps`` that works but maps no
    OpenBLAS. Tolerance: none (exact).
    """
    no_flags = "processor\t: 0\nmodel name\t: Test CPU\n"
    with monkeypatch.context() as patch:
        patch.setattr(provenance, "CPUINFO", _Unreadable(None, no_flags))
        patch.setattr(platform, "machine", lambda: "x86_64")
        assert provenance.probe_errors(block_for()) == [
            "cpu: no ISA flags found on x86_64"
        ]
        patch.setattr(platform, "machine", lambda: "aarch64")
        assert provenance.probe_errors(block_for()) == []
    with monkeypatch.context() as patch:
        patch.setattr(
            provenance,
            "CPUINFO",
            _Unreadable(None, "processor\t: 0\n"),
        )
        patch.setattr(platform, "processor", lambda: "test-cpu")
        patch.setattr(platform, "machine", lambda: "aarch64")
        assert provenance.probe_errors(block_for()) == [
            "cpu: model from platform.processor"
        ]
    with monkeypatch.context() as patch:
        patch.setattr(
            provenance,
            "MAPS",
            _Unreadable(None, "7f00-7f01 r-xp 0 00:00 0 /usr/lib/libc.so\n"),
        )
        block = block_for()
        assert block["blas"] == {"libraries": [], "error": None}
        assert provenance.probe_errors(block) == [
            "blas: no OpenBLAS library mapped"
        ]


SIMD_PROBE = (
    "import json, sys; sys.path.insert(0, sys.argv[1]); "
    "from lpcstudy import provenance; "
    "print(json.dumps(provenance.simd_record()))"
)


def test_simd_record_follows_a_disabled_dispatch_level_r3() -> None:
    """Disabling ``X86_V3`` removes it from ``found`` (known truth by
    construction, R3).

    Reference: numpy's documented ``NPY_DISABLE_CPU_FEATURES`` (planning table:
    ``found`` is ``["X86_V3"]`` here and the key is absent under the variable).
    A fresh ``python -I`` runs the probe with the variable set; the level must
    be absent. When this CPU has every feature of x86-64-v3 (own parse of the
    flags line), a second run without the variable must list it.
    """
    assert (
        platform.machine() == "x86_64"
    ), "the reference platform is x86-64 (DEC-0022)"
    flags = set(
        re.search(
            r"^flags\s*:\s*(.*)$",
            Path("/proc/cpuinfo").read_text(),
            re.MULTILINE,
        )
        .group(1)
        .split()
    )

    def found(**env: str) -> list[str]:
        base = {
            k: v
            for k, v in os.environ.items()
            if k != "NPY_DISABLE_CPU_FEATURES"
        }
        done = subprocess.run(
            [sys.executable, "-I", "-c", SIMD_PROBE, str(ROOT)],
            env=base | env,
            capture_output=True,
            text=True,
            check=True,
            timeout=60,
        )
        record = json.loads(done.stdout)
        assert record["error"] is None
        return record["found"]

    assert "X86_V3" not in found(NPY_DISABLE_CPU_FEATURES="X86_V3")
    v3 = {"avx2", "bmi1", "bmi2", "fma", "f16c", "movbe", "abm"}
    if not v3 <= flags:
        pytest.skip(
            f"host lacks x86-64-v3 features {sorted(v3 - flags)}: "
            "the positive arm "
            "(X86_V3 present by default) cannot be checked here (R6)"
        )
    assert "X86_V3" in found()


# WU-0003.7a: the integer-index digest (A5 leaf membership).


def test_index_digest_is_sha256_of_int64_bytes() -> None:
    """``index_digest`` is the SHA-256 of the row-major little-endian int64
    bytes (WU-0003.7a, a4).

    Reference: ``hashlib.sha256(struct.pack("<%dq", ...))``, written here with
    ``struct`` (not numpy ``tobytes``). Values include a negative, a value above
    2**32 and zero. A signed narrower integer widens losslessly to the same
    digest; a big-endian copy and a Fortran-ordered 2-D array give the digest of
    the logical C-order sequence; the transpose differs. A float, an unsigned or
    a boolean array raises ``TypeError`` (PRIME.4: nothing is converted
    silently).
    Tolerance: none (exact; a digest is a deterministic function of the bytes).
    """
    values = [0, 1, -1, 2**40 + 3, 7, 7]
    expected = hashlib.sha256(
        struct.pack("<%dq" % len(values), *values)
    ).hexdigest()
    flat = np.array(values, dtype=np.int64)
    assert provenance.index_digest(flat) == expected
    assert re.fullmatch(r"[0-9a-f]{64}", expected)
    assert provenance.index_digest(flat.astype(">i8")) == expected
    small = [0, 1, -1, 5, 7, 7]
    small_ref = hashlib.sha256(
        struct.pack("<%dq" % len(small), *small)
    ).hexdigest()
    assert provenance.index_digest(np.array(small, dtype=np.int32)) == small_ref
    matrix = flat.reshape(2, 3)
    assert provenance.index_digest(np.asfortranarray(matrix)) == expected
    assert provenance.index_digest(matrix.T) != expected
    for bad in (
        np.array([1.0]),
        np.array([1], dtype=np.uint64),
        np.array([True]),
    ):
        with pytest.raises(TypeError, match="index_digest"):
            provenance.index_digest(bad)
