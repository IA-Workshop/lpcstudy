"""Run provenance (LPC.PC.18, LPC.PC.13, LPC.PC.22): what a result was produced by.

``collect`` builds the block at the start of a run, before any output is written, and
``finish`` completes it before the final save. The block records the seed id and never the
confirmatory seed value (LPC.PC.7). Nothing here is silent: a git failure is recorded in
``git_error`` and an uninstalled package as ``null`` (the caller logs both).
"""

from __future__ import annotations

import dataclasses
import datetime as dt
import os
import platform
import resource
import subprocess
import sys
import time
from importlib import metadata
from pathlib import Path

import jax

from .config import StudyConfig

SCHEMA = "lpcstudy.provenance/1"
ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ("jax", "jaxlib", "optax", "numpy", "scipy", "scikit-learn", "matplotlib")
ENV_NAMES = ("JAX_PLATFORMS", "XLA_FLAGS", "XLA_PYTHON_CLIENT_PREALLOCATE", "LPC_THREADS",
             "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS")
GIT_TIMEOUT_SECONDS = 30


class RunClock:
    """Wall clock of a run: ``perf_counter`` at construction and the UTC start time.

    Attributes
    ----------
    start_utc : str
        ISO 8601 UTC time at construction, to the second.
    """

    def __init__(self) -> None:
        self._start = time.perf_counter()
        self.start_utc = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

    def elapsed(self) -> float:
        """Return the seconds since construction."""
        return time.perf_counter() - self._start


def git_state(root: Path) -> tuple[str | None, bool | None, str | None]:
    """Return ``(commit, dirty, error)`` of the repository at ``root``.

    ``dirty`` is ``bool(git status --porcelain)``, so untracked files count. On any
    failure the result is ``(None, None, <error text>)``; the error is recorded by the
    caller, never dropped.
    """
    def run(*args: str) -> str:
        done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
                              timeout=GIT_TIMEOUT_SECONDS)
        if done.returncode != 0:
            raise RuntimeError(f"git {' '.join(args)} exited {done.returncode}: "
                               f"{done.stderr.strip()[:200]}")
        return done.stdout

    try:
        commit = run("rev-parse", "HEAD").strip()
        dirty = bool(run("status", "--porcelain").strip())
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        return None, None, f"{type(exc).__name__}: {exc}"
    return commit, dirty, None


def peak_rss_bytes() -> int:
    """Return the peak resident set size of this process in bytes (``ru_maxrss``).

    ``ru_maxrss`` is in KiB on Linux and in bytes on Darwin.
    """
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(peak if sys.platform == "darwin" else peak * 1024)


def device_peak_bytes() -> int | None:
    """Return the first device's peak memory in bytes, or ``None`` when it reports none (CPU)."""
    stats = jax.devices()[0].memory_stats()
    if not stats or "peak_bytes_in_use" not in stats:
        return None
    return int(stats["peak_bytes_in_use"])


def header_label(seed_id: str) -> str:
    """Return the output label for a seed id (LPC.PC.13).

    Raises
    ------
    ValueError
        If ``seed_id`` is neither ``DEV-n`` nor ``CONF-n``.
    """
    if seed_id.startswith("DEV-"):
        return f"DEVELOPMENT ({seed_id}): not a hypothesis test"
    if seed_id.startswith("CONF-"):
        return "CONFIRMATORY: UNPROMOTED"
    raise ValueError(f"seed id {seed_id!r} is neither DEV-n nor CONF-n")


def config_record(config: StudyConfig) -> dict:
    """Return the configuration as a dict, with the seed nulled for a confirmatory id."""
    record = dataclasses.asdict(config)
    if config.seed_id.startswith("CONF-"):
        record["seed"] = None
    return record


def _package_versions() -> dict[str, str | None]:
    versions: dict[str, str | None] = {}
    for name in PACKAGES:
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            versions[name] = None
    return versions


def collect(config: StudyConfig, seed_id: str, argv: list[str], clock: RunClock) -> dict:
    """Build the provenance block at the start of a run.

    Parameters
    ----------
    config : StudyConfig
        The run's configuration (its seed is nulled in the record when confirmatory).
    seed_id : str
        ``DEV-n`` or ``CONF-n``; the seed value is never recorded for ``CONF-n``.
    argv : list[str]
        Command-line arguments, to regenerate the run.
    clock : RunClock
        The run clock (supplies ``start_utc``).

    Returns
    -------
    dict
        The block with ``complete`` false and the end-of-run fields null.
    """
    commit, dirty, git_error = git_state(ROOT)
    devices = jax.devices()
    precision = jax.config.jax_default_matmul_precision
    return {
        "schema": SCHEMA,
        "seed_id": seed_id,
        "seed_kind": "confirmatory" if seed_id.startswith("CONF-") else "development",
        "label": header_label(seed_id),
        "promoted": False,
        "commit": commit,
        "dirty": dirty,
        "git_error": git_error,
        "preset": config.name,
        "config": config_record(config),
        "argv": list(argv),
        "python": platform.python_version(),
        "packages": _package_versions(),
        "platform": platform.platform(),
        "device": {"backend": jax.default_backend(), "kind": devices[0].device_kind,
                   "count": len(devices)},
        "jax_x64": bool(jax.config.jax_enable_x64),
        "jax_matmul_precision": None if precision is None else str(precision),
        "env": {name: os.environ.get(name) for name in ENV_NAMES},
        "start_utc": clock.start_utc,
        "end_utc": None,
        "wall_seconds": None,
        "peak_rss_bytes": None,
        "device_peak_bytes": None,
        "complete": False,
    }


def finish(block: dict, clock: RunClock) -> dict:
    """Return a copy of ``block`` completed with the end time, wall time and peak memory."""
    return {**block,
            "end_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "wall_seconds": clock.elapsed(),
            "peak_rss_bytes": peak_rss_bytes(),
            "device_peak_bytes": device_peak_bytes(),
            "complete": True}
