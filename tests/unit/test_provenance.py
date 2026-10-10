"""Run provenance block (WU-0001.4; LPC.PC.18, LPC.PC.22, LPC.PC.13).

References are independent of ``lpcstudy/provenance.py``: the test's own ``git`` calls, the
kernel's ``VmHWM`` counter, ``requirements.txt``, ``sys.version_info`` and a second clock.
The confirmatory seed is never used; the one below is synthetic (LPC.PC.7).
"""

from __future__ import annotations

import dataclasses
import datetime as dt
import json
import os
import resource
import subprocess
import sys
import time
from importlib import metadata
from pathlib import Path

import jax
import jax.numpy as jnp
import pytest

import lpcstudy.systems  # noqa: F401  (enables x64 on import, as in a real run)
from lpcstudy import provenance
from lpcstudy.config import SMOKE
from lpcstudy.seeds import with_seed

ROOT = Path(__file__).resolve().parents[2]
SYNTHETIC_SEED = 987654321987654321
KEYS = ("schema", "seed_id", "seed_kind", "label", "promoted", "commit", "dirty", "git_error",
        "preset", "config", "argv", "python", "packages", "platform", "device", "jax_x64",
        "jax_matmul_precision", "env", "start_utc", "end_utc", "wall_seconds",
        "peak_rss_bytes", "device_peak_bytes", "complete")
END_KEYS = ("end_utc", "wall_seconds", "peak_rss_bytes", "device_peak_bytes", "complete")


@pytest.fixture(autouse=True)
def _clean_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """No test sees a confirmatory seed or salt (LPC.PC.7)."""
    monkeypatch.delenv("LPC_CONF_SEED", raising=False)
    monkeypatch.delenv("LPC_CONF_SALT", raising=False)


def block_for(seed_id: str = "DEV-0", argv: list[str] | None = None) -> dict:
    """Collect a block for the smoke preset."""
    seed = SYNTHETIC_SEED if seed_id.startswith("CONF-") else SMOKE.seed
    config = with_seed(SMOKE, seed_id, seed)
    return provenance.collect(config, seed_id, argv or ["--preset", "smoke"],
                              provenance.RunClock())


def git(*args: str, cwd: Path = ROOT) -> str:
    """Run git in ``cwd`` (the test's own reference calls)."""
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                          check=True).stdout


def test_every_lpc_pc_18_field_is_present_in_order_and_typed() -> None:
    """The block has exactly the schema's keys, in order, with the schema's types.

    Reference: the field table of the plan (LPC.PC.18/.22/.13). Exact key and type checks.
    """
    block = block_for()
    assert tuple(block) == KEYS
    assert block["schema"] == "lpcstudy.provenance/1"
    assert block["seed_id"] == "DEV-0" and block["seed_kind"] == "development"
    assert block["promoted"] is False and block["complete"] is False
    assert isinstance(block["commit"], str) and len(block["commit"]) == 40
    assert isinstance(block["dirty"], bool) and block["git_error"] is None
    assert block["preset"] == "smoke" and block["argv"] == ["--preset", "smoke"]
    assert isinstance(block["python"], str) and isinstance(block["platform"], str)
    assert set(block["device"]) == {"backend", "kind", "count"}
    assert isinstance(block["device"]["count"], int) and block["device"]["count"] >= 1
    assert isinstance(block["jax_x64"], bool)
    assert block["jax_matmul_precision"] is None or isinstance(block["jax_matmul_precision"], str)
    assert (block["end_utc"], block["wall_seconds"], block["peak_rss_bytes"],
            block["device_peak_bytes"]) == (None, None, None, None)
    json.dumps(block)  # serializable without a default handler


def test_start_utc_is_iso_8601_utc_to_the_second() -> None:
    """``start_utc`` parses as an aware UTC time with no sub-second part, within the call span.

    Reference: ``datetime`` bounds taken around the call; the stamp is truncated to the
    second, so it lies in [before truncated to the second, after].
    """
    before = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    clock = provenance.RunClock()
    after = dt.datetime.now(dt.timezone.utc)
    start = dt.datetime.fromisoformat(clock.start_utc)
    assert start.utcoffset() == dt.timedelta(0) and start.microsecond == 0
    assert before <= start <= after


def test_commit_and_dirty_equal_the_tests_own_git_calls() -> None:
    """``commit`` is ``git rev-parse HEAD`` and ``dirty`` is ``bool(git status --porcelain)``.

    Reference: two ``git`` subprocesses run by the test at the same moment (the working tree
    does not change between them). Exact string and boolean equality.
    """
    block = block_for()
    assert block["commit"] == git("rev-parse", "HEAD").strip()
    assert block["dirty"] == bool(git("status", "--porcelain").strip())


def test_git_failure_is_recorded_not_silent(tmp_path: Path,
                                            monkeypatch: pytest.MonkeyPatch) -> None:
    """Outside a repository, and with no ``git`` executable, the error is returned as text.

    Reference: the plan (``None, None, <error>``). ``tmp_path`` is not a repository
    (asserted with the test's own git call), and an empty ``PATH`` removes the executable.
    """
    assert subprocess.run(["git", "-C", str(tmp_path), "rev-parse"],
                          capture_output=True).returncode != 0
    commit, dirty, error = provenance.git_state(tmp_path)
    assert (commit, dirty) == (None, None) and isinstance(error, str) and error
    monkeypatch.setenv("PATH", str(tmp_path))
    commit, dirty, error = provenance.git_state(ROOT)
    assert (commit, dirty) == (None, None) and "FileNotFoundError" in str(error)


def test_peak_rss_is_positive_and_bracketed_by_the_kernel_counter() -> None:
    """``peak_rss_bytes`` is positive, a whole number of pages and, on Linux, bracketed by ``VmHWM``.

    Reference: ``VmHWM`` (kB, the kernel's high-water mark) from ``/proc/self/status`` read
    before and after the call; ``ru_maxrss`` is the same counter in KiB, so
    ``1024 VmHWM_before - 2T <= peak <= 1024 VmHWM_after + 2T``. The roadmap criterion is
    ``peak > 0``, asserted exactly.

    Tolerance (applied-mathematician, WU-0001 Log 2026-10-10; DEC-0006 proposed). Since Linux
    6.2 the RSS is three ``percpu_counter``s (file, anon, shmem). ``getrusage`` reads them
    approximately; each per-CPU delta is below the batch ``b = max(32, 2n)`` (n = online
    CPUs), so the read is within ``T = 3 n (b - 1)`` pages of the exact sum (24.8 MB at
    n = 32; attained per counter in a probe, WU-0001 Log 2026-10-10). ``VmHWM`` is the exact
    sum (approximate before about 6.16) and ``mm->hiwater_rss`` is refreshed by an
    approximate read before RSS falls, so the bracket above holds. Assumptions: no CPU
    hotplug, ``clear_refs`` or reclaim between the two reads; the process was not exec'd
    (vfork, fork or exec-in-place) from a process whose peak exceeds the upper bound, because
    ``ru_maxrss`` includes the pre-exec image (``signal->maxrss``), which ``VmHWM`` does not;
    a failure on the upper side with a large launcher is that, not a code defect. Power: with
    ``1024 VmHWM >= 182 MB`` (after importing jax) and ``2T = 49.5 MB``, the bracket rejects
    a missing x1024 (E/1024), x4096 (4E) and any factor-2 error. ``ru_maxrss`` is
    pages x PAGE_SIZE/1024 KiB, so ``peak % pagesize == 0`` holds exactly and also catches
    x1000 and sub-page offsets. Neither check resolves a one-page additive error (kernel
    noise is about 10^3 pages). ``os.sysconf("SC_NPROCESSORS_ONLN")`` is used, not
    ``os.cpu_count()``, which ``PYTHON_CPU_COUNT`` can override.

    Limitation of the quantity (not of the test): a child process inherits its parent's peak
    in ``ru_maxrss``, so the recorded ``peak_rss_bytes`` can reflect the launcher's peak.
    """
    def hwm() -> int:
        for line in Path("/proc/self/status").read_text().splitlines():
            if line.startswith("VmHWM:"):
                return int(line.split()[1])
        raise AssertionError("VmHWM not found")

    assert provenance.peak_rss_bytes() > 0
    if not sys.platform.startswith("linux"):
        pytest.skip("VmHWM exists on Linux only; the positivity check above ran")
    page = resource.getpagesize()
    before = hwm()
    peak = provenance.peak_rss_bytes()
    after = hwm()
    online = os.sysconf("SC_NPROCESSORS_ONLN")
    counter_error = 3 * online * (max(32, 2 * online) - 1) * page
    assert peak % page == 0, f"peak {peak} B is not a whole number of {page} B pages"
    assert 1024 * before - 2 * counter_error <= peak <= 1024 * after + 2 * counter_error, (
        f"peak {peak} B outside [{1024 * before}, {1024 * after}] B +- {2 * counter_error} B")


def test_recorded_wall_seconds_is_within_one_percent_of_the_tests_own_clock() -> None:
    """``finish(block, clock)["wall_seconds"]`` over a 1 s sleep agrees with a second clock.

    Reference: ``t0 = perf_counter(); clock = RunClock(); block = collect(...); sleep(1.0);
    done = finish(block, clock); t1 = perf_counter()``; the reference span is ``t1 - t0``.
    Both clocks span the same collect and sleep. Tolerance 1% of the span (about 10 ms),
    the criterion's own: the two spans differ only by the constructor, the end-time stamp
    and the memory queries (microseconds) plus one possible preemption, far below 10 ms.
    The span (1 s of sleep plus the git calls of ``collect``) is long enough that 1% is well
    above timer noise.
    """
    t0 = time.perf_counter()
    clock = provenance.RunClock()
    block = provenance.collect(with_seed(SMOKE, "DEV-0", SMOKE.seed), "DEV-0", [], clock)
    time.sleep(1.0)
    done = provenance.finish(block, clock)
    t1 = time.perf_counter()
    assert abs(done["wall_seconds"] - (t1 - t0)) <= 0.01 * (t1 - t0)


def test_python_version_equals_sys_version_info() -> None:
    """``python`` is the interpreter's ``major.minor.micro``.

    Reference: ``sys.version_info``. Exact.
    """
    assert block_for()["python"] == "%d.%d.%d" % sys.version_info[:3]


def test_package_versions_equal_the_requirements_pins() -> None:
    """Each recorded package version equals its pin in ``requirements.txt``.

    Reference: the pins parsed from ``requirements.txt`` by the test. A mismatch is an
    LPC.PC.17 finding about the environment, never a reason to change this test. Exact.
    """
    pins = {}
    for line in (ROOT / "requirements.txt").read_text().splitlines():
        text = line.split("#")[0].strip()
        if "==" in text:
            name, version = text.split("==")
            pins[name.split("[")[0]] = version
    packages = block_for()["packages"]
    assert set(packages) == {"jax", "jaxlib", "optax", "numpy", "scipy", "scikit-learn",
                             "matplotlib"}
    assert packages == {name: pins[name] for name in packages}


def test_uninstalled_package_is_recorded_as_null(monkeypatch: pytest.MonkeyPatch) -> None:
    """A package that is not installed is recorded as ``None``, the others unchanged.

    Reference: ``importlib.metadata.version`` patched to raise ``PackageNotFoundError`` for
    ``optax`` only (the caller counts and logs the nulls).
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
    """``jax_x64`` is true exactly when ``jnp.zeros(1)`` is float64 (after importing systems).

    Reference: the dtype of a fresh jax array. Exact; and the study requires it to be true.
    """
    enabled = jnp.zeros(1).dtype == jnp.float64
    assert enabled is True or bool(enabled) is True
    assert block_for()["jax_x64"] is bool(enabled)


def test_device_is_the_cpu_backend_under_jax_platforms_cpu() -> None:
    """``device.backend`` is ``cpu`` with the project default ``JAX_PLATFORMS=cpu``.

    Reference: the environment (``settings.json`` default); ``jax.devices()`` for the kind
    and count. Exact.
    """
    assert os.environ.get("JAX_PLATFORMS") == "cpu", "tests run under JAX_PLATFORMS=cpu"
    device = block_for()["device"]
    assert device["backend"] == "cpu" == jax.default_backend()
    assert device["count"] == len(jax.devices()) and device["kind"] == jax.devices()[0].device_kind


def test_env_block_has_the_listed_names_and_never_the_confirmatory_variables(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """``env`` records the seven listed variables and never ``LPC_CONF_*``.

    Reference: the plan's list; the variables below are set to a synthetic value that must
    not appear anywhere in the block. Exact.
    """
    monkeypatch.setenv("LPC_CONF_SEED", "424242424242")
    monkeypatch.setenv("LPC_CONF_SALT", "ab" * 16)
    monkeypatch.setenv("OMP_NUM_THREADS", "3")
    block = block_for("CONF-1", ["--confirmatory"])
    assert set(block["env"]) == {"JAX_PLATFORMS", "XLA_FLAGS", "XLA_PYTHON_CLIENT_PREALLOCATE",
                                 "LPC_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
                                 "OPENBLAS_NUM_THREADS"}
    assert block["env"]["OMP_NUM_THREADS"] == "3"
    text = json.dumps(block)
    assert "424242424242" not in text and "ab" * 16 not in text and "LPC_CONF" not in text


def test_confirmatory_block_nulls_the_seed_and_labels_it() -> None:
    """A ``CONF-1`` block holds the id and the label but not the seed value.

    Reference: the synthetic seed literal. The value appears nowhere in the serialized
    block; ``config.seed`` is ``None``; every other config field equals the preset's. Exact.
    """
    block = block_for("CONF-1", ["--confirmatory"])
    assert block["seed_id"] == "CONF-1" and block["seed_kind"] == "confirmatory"
    assert block["label"] == "CONFIRMATORY: UNPROMOTED" and block["promoted"] is False
    assert str(SYNTHETIC_SEED) not in json.dumps(block)
    assert block["config"]["seed"] is None and block["config"]["seed_id"] == "CONF-1"
    expected = dataclasses.asdict(SMOKE) | {"seed": None, "seed_id": "CONF-1"}
    assert json.loads(json.dumps(block["config"])) == json.loads(json.dumps(expected))


def test_development_block_keeps_the_full_config() -> None:
    """A ``DEV-0`` block's config equals ``dataclasses.asdict`` of the config exactly."""
    block = block_for()
    assert block["label"] == "DEVELOPMENT (DEV-0): not a hypothesis test"
    assert block["config"] == dataclasses.asdict(with_seed(SMOKE, "DEV-0", SMOKE.seed))


def test_header_label_rejects_other_ids() -> None:
    """``header_label`` accepts only ``DEV-n`` and ``CONF-n``."""
    assert provenance.header_label("DEV-3") == "DEVELOPMENT (DEV-3): not a hypothesis test"
    for bad in ("", "dev-1", "5", "X-1"):
        with pytest.raises(ValueError):
            provenance.header_label(bad)


def test_finish_completes_a_copy_and_leaves_the_original() -> None:
    """``finish`` returns a completed copy; the original block is untouched.

    Reference: the field table (end fields filled, ``complete`` true). ``wall_seconds`` is
    bracketed by the test's own clock, ``end_utc`` is not before ``start_utc``, and on the
    CPU backend ``device_peak_bytes`` is ``None`` (no device statistics). Exact/ordering.
    """
    t0 = time.perf_counter()
    clock = provenance.RunClock()
    block = provenance.collect(with_seed(SMOKE, "DEV-0", SMOKE.seed), "DEV-0", [], clock)
    done = provenance.finish(block, clock)
    t1 = time.perf_counter()
    assert block["complete"] is False and block["end_utc"] is None
    assert done["complete"] is True
    assert 0.0 <= done["wall_seconds"] <= t1 - t0
    assert dt.datetime.fromisoformat(done["end_utc"]) >= dt.datetime.fromisoformat(
        block["start_utc"])
    assert isinstance(done["peak_rss_bytes"], int) and done["peak_rss_bytes"] > 0
    assert done["device_peak_bytes"] is None
    assert {k: v for k, v in done.items() if k not in END_KEYS} == \
        {k: v for k, v in block.items() if k not in END_KEYS}
