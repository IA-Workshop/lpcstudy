"""Run provenance (LPC.PC.18, LPC.PC.13, LPC.PC.22): what a result came from.

"Provenance" means the record of where a result came from. Two runs that print
the same number are only comparable if we know the code version, the settings,
the seed id, the library versions and the machine behind each. This module
collects that record into one dictionary that ``__main__`` stores inside
``results.json``:

* ``collect`` builds the block at the start of a run, before any output is
  written;
* ``finish`` completes it (end time, wall time, peak memory) before the final
  save.

It also supplies SHA-256 "digests" (``array_digest``, ``index_digest``): short
fingerprints of an array that change if even one bit of any value changes.
``data`` and ``networks`` use them to prove that two runs followed the same
trajectory; ``allocation`` uses the integer version.

The block records the seed id and never the confirmatory seed value
(LPC.PC.7). Nothing here is silent: a git failure is recorded in
``git_error`` and an uninstalled package as ``null`` (the caller logs both).
"""

from __future__ import annotations

import ctypes
import dataclasses
import datetime as dt
import hashlib
import os
import platform
import re
import resource
import subprocess
import sys
import time
from importlib import metadata
from pathlib import Path

import jax
import numpy as np

# The next import is needed for its side effect: it maps scipy's OpenBLAS into
# the process, so ``blas_record`` sees it.
import scipy.linalg  # noqa: F401

from .config import StudyConfig

# Name of the block layout, the repository root, and the packages whose
# versions are recorded.
SCHEMA = "lpcstudy.provenance/2"
ROOT = Path(__file__).resolve().parents[1]
PACKAGES = (
    "jax",
    "jaxlib",
    "optax",
    "numpy",
    "scipy",
    "scikit-learn",
    "matplotlib",
)
# Environment variables whose values affect numerical results; their values are
# copied into the block.
ENV_NAMES = (
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
)
# Longest wait for one git call, and the git variables that could point git at
# a different repository (they are removed before git is called).
GIT_TIMEOUT_SECONDS = 30
GIT_REDIRECT_VARIABLES = (
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_COMMON_DIR",
    "GIT_NAMESPACE",
)
# Tags that ``git ls-files -v`` prints for skip-worktree / assume-unchanged
# files, which ``git status`` does not show.
HIDDEN_TAGS = ("S", "s", "h")
CPUINFO = Path("/proc/cpuinfo")
MAPS = Path("/proc/self/maps")
ISA_FLAGS = (
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
)
"""The ``/proc/cpuinfo`` flags that OpenBLAS, numpy and LLVM key on (M4).

OpenBLAS reads them through ``cpuid``, numpy for its dispatch.

Not the whole flags line: its kernel-synthesized and mitigation flags change
with the kernel version on the same hardware."""
# Names of the C functions that report the OpenBLAS kernel name and build
# configuration. Different OpenBLAS builds use different spellings, so several
# are tried in order.
CORENAME_SYMBOLS = (
    "scipy_openblas_get_corename64_",
    "scipy_openblas_get_corename",
    "openblas_get_corename64_",
    "openblas_get_corename",
)
CONFIG_SYMBOLS = (
    "scipy_openblas_get_config64_",
    "scipy_openblas_get_config",
    "openblas_get_config64_",
    "openblas_get_config",
)


class RunClock:
    """Stopwatch for one run.

    It remembers the high-resolution counter (``time.perf_counter``) and the
    UTC start time at the moment it is created.

    Attributes
    ----------
    start_utc : str
        The start time as an ISO 8601 string in UTC, to the second.
    """

    def __init__(self) -> None:
        self._start = time.perf_counter()
        self.start_utc = dt.datetime.now(dt.timezone.utc).isoformat(
            timespec="seconds"
        )

    def elapsed(self) -> float:
        """Return the seconds since the clock was created."""
        return time.perf_counter() - self._start


def git_state(root: Path) -> tuple[str | None, bool | None, str | None]:
    """Read the git commit and whether the working tree has changes.

    "Dirty" means the code on disk is not exactly the code of the commit, so
    the commit name alone would not reproduce the run. ``dirty`` is true when
    either of two reads shows a difference from ``HEAD``:

    * ``git status --porcelain`` is non-empty (modified, staged or untracked
      files);
    * ``git ls-files -v`` shows a tracked file hidden from status by the
      skip-worktree or assume-unchanged bit (tags ``S``, ``s``, ``h``).

    Ways of hiding changes that are closed (WU-0004a, R2 and R4):

    * the settings ``status.showUntrackedFiles`` and the submodule setting
      (the status call names ``--untracked-files=normal
      --ignore-submodules=none``);
    * ``core.excludesFile`` from any config file or from the environment (the
      status call sets it to ``/dev/null`` on the command line, and every
      ``GIT_CONFIG*`` variable is removed from git's environment, which also
      drops the user's global ignore file);
    * the skip-worktree and assume-unchanged bits;
    * the variables that redirect git to another repository (``GIT_DIR``,
      ``GIT_WORK_TREE``, ``GIT_INDEX_FILE`` and the object-store variables
      are removed).

    Ways of hiding changes that are **not** closed (accepted limitations,
    covered by the WU-0015.1 pre-run checks): a file excluded by a
    ``.gitignore`` in the tree (the project's own declared ignore list), and a
    line in ``.git/info/exclude``. The second could be closed by listing
    untracked files with only the in-tree ``.gitignore`` files applied. But a
    git worktree shares ``info/exclude`` with its main checkout, and the
    project's worktrees hold a ``.venv`` symlink that the ``.venv/`` pattern
    of ``.gitignore`` does not match and only ``info/exclude`` hides. That
    read would make every such worktree record ``dirty: true`` (a change to
    ordinary development runs). In an ordinary checkout the value of
    ``dirty`` is unchanged by the closed routes.

    Parameters
    ----------
    root : Path
        The repository directory.

    Returns
    -------
    tuple[str | None, bool | None, str | None]
        ``(commit, dirty, error)``. On any failure this is
        ``(None, None, <error text>)``; the error is recorded by the caller,
        never dropped.
    """
    environment = {
        name: value
        for name, value in os.environ.items()
        if name not in GIT_REDIRECT_VARIABLES
        and not name.startswith("GIT_CONFIG")
    }

    def run(*args: str) -> str:
        done = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            text=True,
            timeout=GIT_TIMEOUT_SECONDS,
            env=environment,
        )
        if done.returncode != 0:
            raise RuntimeError(
                f"git {' '.join(args)} exited {done.returncode}: "
                f"{done.stderr.strip()[:200]}"
            )
        return done.stdout

    try:
        commit = run("rev-parse", "HEAD").strip()
        status = run(
            "-c",
            "core.excludesFile=/dev/null",
            "status",
            "--porcelain",
            "--untracked-files=normal",
            "--ignore-submodules=none",
        )
        listing = run("ls-files", "-v")
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        return None, None, f"{type(exc).__name__}: {exc}"
    hidden = any(line[:1] in HIDDEN_TAGS for line in listing.splitlines())
    return commit, bool(status.strip()) or hidden, None


def peak_rss_bytes() -> int:
    """Return the peak memory this process has used, in bytes (``ru_maxrss``).

    "Resident set size" is the part of the process's memory that sits in RAM.
    ``ru_maxrss`` is in KiB on Linux and in bytes on Darwin (macOS).

    Limitation (LPC.PC.22): a child process inherits its parent's peak in
    ``ru_maxrss`` (the pre-exec image counts), so the recorded peak can
    reflect the launcher's peak, not only this run's. The kernel also reads
    the resident-set counters approximately, to within about 25 MB at 32 CPUs
    (see ``tests/unit/test_provenance.py``).
    """
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(peak if sys.platform == "darwin" else peak * 1024)


def device_peak_bytes() -> int | None:
    """Return the first JAX device's peak memory in bytes.

    Returns ``None`` when the device reports none (the CPU does not).
    """
    stats = jax.devices()[0].memory_stats()
    if not stats or "peak_bytes_in_use" not in stats:
        return None
    return int(stats["peak_bytes_in_use"])


def array_digest(values: np.ndarray) -> str:
    """Fingerprint a float64 array with SHA-256.

    The digest is of the IEEE-754 binary64 values, little-endian, row-major (C
    order). It is a bitwise fingerprint: it has no shape or dtype prefix, so
    ``sha256`` of ``ctx.whiten.tobytes()`` on a little-endian host is the same
    string, and a signed zero or a NaN payload changes it. The order is that
    of the logical array (a Fortran-ordered copy or a ``>f8`` copy gives the
    same digest, a transpose does not).

    Parameters
    ----------
    values : np.ndarray
        An array whose dtype is a 64-bit float (either byte order).

    Returns
    -------
    str
        64 lowercase hexadecimal characters.

    Raises
    ------
    TypeError
        If the dtype is not a 64-bit float. Nothing is converted silently
        (PRIME.4).
    """
    array = np.asarray(values)
    if array.dtype.kind != "f" or array.dtype.itemsize != 8:
        raise TypeError(
            f"array_digest needs a 64-bit float array, got {array.dtype}"
        )
    return hashlib.sha256(
        np.asarray(array, dtype="<f8").tobytes(order="C")
    ).hexdigest()


def index_digest(values: np.ndarray) -> str:
    """Fingerprint an integer array with SHA-256.

    The digest is of the integers as little-endian int64, row-major (C order).
    This is the integer counterpart of :func:`array_digest` (WU-0003.7a). It
    fingerprints an index array such as the leaf id of every (state, draw) in
    a regression tree. A signed integer dtype of any width is widened to
    int64 first (lossless, so the same values give the same digest); the
    digest has no shape or dtype prefix.

    Parameters
    ----------
    values : np.ndarray
        An array of signed integers (any byte order).

    Returns
    -------
    str
        64 lowercase hexadecimal characters.

    Raises
    ------
    TypeError
        If the dtype is not a signed integer (a float, an unsigned integer or
        a boolean). Nothing is converted silently (PRIME.4).
    """
    array = np.asarray(values)
    if array.dtype.kind != "i":
        raise TypeError(
            f"index_digest needs a signed integer array, got {array.dtype}"
        )
    return hashlib.sha256(
        np.asarray(array, dtype="<i8").tobytes(order="C")
    ).hexdigest()


def _error_text(exc: BaseException) -> str:
    """Format an exception as ``"<Type>: <message>"``, as ``git_error`` does."""
    return f"{type(exc).__name__}: {exc}"


def cpu_record() -> dict:
    """Describe the CPU of this host (DEF-0024); never raises.

    Numerical results can differ in the last bits between CPUs, because the
    linear-algebra libraries pick different instruction sets (ISA flags such
    as ``avx2``). Recording the CPU lets us explain such differences.

    The model is the first ``model name`` line of ``/proc/cpuinfo``, else a
    non-empty ``platform.processor()``, else ``"unknown"``. ``isa`` is the
    sorted intersection of the first ``flags`` line with ``ISA_FLAGS`` (``[]``
    when there is none).

    Returns
    -------
    dict
        ``model`` (str), ``source`` (``"/proc/cpuinfo"``,
        ``"platform.processor"`` or ``"none"``), ``isa`` (list of str) and
        ``error`` (the read failure as text, or ``None``).
    """
    text, error = "", None
    try:
        text = CPUINFO.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001  (recorded below, never dropped)
        error = _error_text(exc)
    model = re.search(r"^model name\s*:\s*(.*)$", text, re.MULTILINE)
    flags = re.search(r"^flags\s*:\s*(.*)$", text, re.MULTILINE)
    isa = sorted(set(flags.group(1).split()) & set(ISA_FLAGS)) if flags else []
    if model and model.group(1).strip():
        return {
            "model": model.group(1).strip(),
            "source": "/proc/cpuinfo",
            "isa": isa,
            "error": error,
        }
    processor = platform.processor().strip()
    if processor:
        return {
            "model": processor,
            "source": "platform.processor",
            "isa": isa,
            "error": error,
        }
    return {"model": "unknown", "source": "none", "isa": isa, "error": error}


def _site_relative(path: Path) -> str:
    """Shorten ``path`` to be relative to numpy's or scipy's site-packages.

    The absolute path is returned if it is under neither, so the record does
    not depend on where the virtual environment lives.
    """
    for module in (np, scipy):
        try:
            return path.relative_to(
                Path(module.__file__).resolve().parents[1]
            ).as_posix()
        except ValueError:
            continue
    return str(path)


def _mapped_openblas() -> list[Path]:
    """List the OpenBLAS shared libraries loaded in this process, by path."""
    paths: set[Path] = set()
    for line in MAPS.read_text(encoding="utf-8").splitlines():
        fields = line.split(maxsplit=5)
        if (
            len(fields) == 6
            and fields[5].startswith("/")
            and "openblas" in fields[5].lower()
        ):
            paths.add(Path(fields[5].removesuffix(" (deleted)")))
    return sorted(paths)


def _call_string(handle: object, names: tuple[str, ...]) -> str:
    """Call the first C function in ``names`` that ``handle`` defines.

    Raises ``AttributeError`` if it defines none of them. Returns the text the
    function gives back.
    """
    for name in names:
        try:
            function = getattr(handle, name)
        except AttributeError:
            continue
        function.restype = ctypes.c_char_p
        return function().decode("ascii", errors="replace")
    raise AttributeError(f"none of {', '.join(names)} is defined")


def _probe_library(path: Path) -> dict:
    """Ask one loaded OpenBLAS library for its corename and configuration.

    Any failure is stored in the ``error`` field of the entry, not raised.
    """
    entry: dict = {
        "library": _site_relative(path),
        "corename": None,
        "config": None,
        "error": None,
    }
    try:
        handle = ctypes.CDLL(str(path), mode=os.RTLD_NOLOAD | os.RTLD_LAZY)
        entry["corename"] = _call_string(handle, CORENAME_SYMBOLS)
        entry["config"] = _call_string(handle, CONFIG_SYMBOLS)
    except (
        Exception
    ) as exc:  # noqa: BLE001  (recorded in the entry, never dropped)
        entry["error"] = _error_text(exc)
    return entry


def blas_record() -> dict:
    """Record which OpenBLAS kernel (corename) is running; never raises.

    OpenBLAS is the library that does the matrix arithmetic under numpy and
    scipy. It picks a "kernel" (a set of routines tuned for the CPU) when it
    starts. Each library found in ``/proc/self/maps`` is opened with
    ``RTLD_NOLOAD`` (nothing new is loaded) and asked for its corename and
    configuration string. The corename is what actually runs, which is not
    always what ``OPENBLAS_CORETYPE`` requested (``np.show_config`` shows only
    the build-time string).

    Returns
    -------
    dict
        ``libraries``: a list of ``{"library", "corename", "config",
        "error"}`` sorted by path (``library`` is relative to site-packages);
        ``error``: why the list could not be built, else ``None``.
    """
    try:
        paths = _mapped_openblas()
    except Exception as exc:  # noqa: BLE001  (recorded, never dropped)
        return {"libraries": [], "error": _error_text(exc)}
    return {
        "libraries": [_probe_library(path) for path in paths],
        "error": None,
    }


def simd_record() -> dict:
    """Record numpy's runtime SIMD dispatch; never raises.

    SIMD ("single instruction, multiple data") instructions let the CPU
    process several numbers at once. This reads the ``found`` list of
    ``np.show_config``, the instruction sets numpy found on this machine.

    Returns
    -------
    dict
        ``found`` (list of str, ``[]`` when numpy reports none) and ``error``
        (text or ``None``).
    """
    try:
        found = (
            np.show_config(mode="dicts")
            .get("SIMD Extensions", {})
            .get("found", [])
        )
        return {"found": [str(name) for name in found], "error": None}
    except Exception as exc:  # noqa: BLE001  (recorded, never dropped)
        return {"found": [], "error": _error_text(exc)}


def probe_errors(block: dict) -> list[str]:
    """List the platform probes that failed or fell back to a weaker source.

    The caller counts and logs the texts (a failure or fallback is recorded in
    the block and never silent, PRIME.4). A failure is a non-null ``error``. A
    fallback raises nothing but is not the primary source: the CPU model from
    ``platform.processor`` or unknown, no ISA flags on x86-64, or no OpenBLAS
    library mapped by a probe that did not fail.

    Parameters
    ----------
    block : dict
        A provenance block from ``collect``.

    Returns
    -------
    list[str]
        One text per failed probe or silent fallback (empty if none).
    """
    found = []
    cpu = block["cpu"]
    if cpu["error"]:
        found.append(f"cpu: {cpu['error']}")
    if cpu["source"] != "/proc/cpuinfo":
        found.append(f"cpu: model from {cpu['source']}")
    if not cpu["isa"] and platform.machine() == "x86_64":
        found.append("cpu: no ISA flags found on x86_64")
    for name in ("blas", "numpy_simd"):
        if block[name]["error"]:
            found.append(f"{name}: {block[name]['error']}")
    if not block["blas"]["libraries"] and not block["blas"]["error"]:
        found.append("blas: no OpenBLAS library mapped")
    for entry in block["blas"]["libraries"]:
        if entry["error"]:
            found.append(f"blas {entry['library']}: {entry['error']}")
    return found


def header_label(seed_id: str) -> str:
    """Return the label printed on every output for a seed id (LPC.PC.13).

    The label tells a reader at a glance whether a result is a development
    run ("not a hypothesis test") or an unpromoted confirmatory run.

    Parameters
    ----------
    seed_id : str
        ``DEV-n`` or ``CONF-n``.

    Returns
    -------
    str
        The label.

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
    """Return the configuration as a dict.

    For a confirmatory id the seed value is replaced by ``None``, so the
    sealed seed is never written to disk (LPC.PC.7).
    """
    record = dataclasses.asdict(config)
    if config.seed_id.startswith("CONF-"):
        record["seed"] = None
    return record


def _package_versions() -> dict[str, str | None]:
    """Return the installed version of each package in ``PACKAGES``.

    A package that is not installed maps to ``None`` (the caller logs it).
    """
    versions: dict[str, str | None] = {}
    for name in PACKAGES:
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            versions[name] = None
    return versions


def collect(
    config: StudyConfig,
    seed_id: str,
    argv: list[str],
    clock: RunClock,
) -> dict:
    """Build the provenance block at the start of a run.

    Parameters
    ----------
    config : StudyConfig
        The run's configuration (its seed is nulled in the record when the
        run is confirmatory).
    seed_id : str
        ``DEV-n`` or ``CONF-n``; the seed value is never recorded for
        ``CONF-n``.
    argv : list[str]
        The command-line arguments, so the run can be regenerated.
    clock : RunClock
        The run clock (supplies ``start_utc``).

    Returns
    -------
    dict
        The block, with ``complete`` false and the end-of-run fields null.
    """
    commit, dirty, git_error = git_state(ROOT)
    devices = jax.devices()
    precision = jax.config.jax_default_matmul_precision
    return {
        "schema": SCHEMA,
        "seed_id": seed_id,
        "seed_kind": (
            "confirmatory" if seed_id.startswith("CONF-") else "development"
        ),
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
        "cpu": cpu_record(),
        "blas": blas_record(),
        "numpy_simd": simd_record(),
        "device": {
            "backend": jax.default_backend(),
            "kind": devices[0].device_kind,
            "count": len(devices),
        },
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
    """Return a copy of ``block`` completed at the end of the run.

    Fills in the end time, the wall time (seconds, from ``clock``), the peak
    memory, and sets ``complete`` to true.
    """
    return {
        **block,
        "end_utc": dt.datetime.now(dt.timezone.utc).isoformat(
            timespec="seconds"
        ),
        "wall_seconds": clock.elapsed(),
        "peak_rss_bytes": peak_rss_bytes(),
        "device_peak_bytes": device_peak_bytes(),
        "complete": True,
    }
