"""GPU reproducibility test: run the smoke preset twice on the GPU and compare.

The study's results must be repeatable: the same code, seed and machine must give
the same numbers, bit for bit. This module checks that claim on the GPU (WU-0004c,
ruling B10). It starts the small "smoke" version of the study twice as child
processes with the development seed DEV-0, then compares the two ``results.json``
files leaf by leaf. A "leaf" is one value at the end of the nested results
dictionary. Before it can run, a small probe decides whether a usable CUDA GPU
(NVIDIA's computing platform) exists. The decision rules, ``classify_probe`` and
``cuda_plugin_installed``, are tested without a GPU in
``tests/unit/test_gpu_reproducibility_probe.py``. The comparison is this file's
own code and does not reuse ``tools/compare_runs.py`` for the main check, so the
two readings of the files are independent.

Run it only through ``tools/run_tests.sh gpu tests/gpu/test_reproducibility.py``.
That script holds the GPU lock ``/tmp/lpcstudy-gpu.lock`` and applies the
1800-second timeout of DEVELOPMENT_WORKFLOW.md section 4.5. Never rerun it
without a code change (section 4.4). The test refuses to start unless the parent
process has ``JAX_PLATFORMS=cuda,cpu`` (only the wrapper's ``gpu`` tier sets
it), so a direct call cannot start two GPU jobs outside the lock (WU-0004c
review R6).
"""

from __future__ import annotations

import importlib.util
import inspect
import json
import math
import os
import struct
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
GPU_BACKENDS = frozenset({"gpu", "cuda", "rocm"})
SEED_ID = "DEV-0"
PROBE_TIMEOUT_SECONDS = 120
RUN_TIMEOUT_SECONDS = (
    780  # two runs plus the probe stay under the 1800 s tier timeout
)
NO_PLUGIN_EXIT = (
    3  # RuntimeError from jax.devices('gpu') and no CUDA plugin installed
)
BACKEND_FAILED_EXIT = (
    4  # RuntimeError from jax.devices('gpu') with a CUDA plugin installed
)
NO_DEVICE_MARK = "CUDA_ERROR_NO_DEVICE"  # cuInit's own message when the driver sees no device
WRAPPER_PLATFORMS = (
    "cuda,cpu"  # set by tools/run_tests.sh for the gpu tier only
)
# Floor against an empty tree; the default (one-system) smoke at bd8e168 has 4,695
# leaves, of which 3,166 are floats.
MIN_LEAVES = 1000
DECLARED_ABS = (
    0.0  # tier T0 of the declared tolerance: bitwise (see the test docstring)
)
DECLARED_REL = 0.0
SAME_SETTINGS = (
    "seed_id",
    "seed_kind",
    "preset",
    "config",
    "commit",
    "dirty",
    "device",
    "env",
    "packages",
    "python",
    "jax_x64",
    "jax_matmul_precision",
)
# A module of the jax_plugins namespace: xla_cuda12, xla_cuda13, ...
PLUGIN_MODULE_PREFIX = "xla_cuda"
# A distribution name: jax-cuda12-plugin, jax-cuda13-pjrt, ...
PLUGIN_DIST_PATTERN = r"jax[-_.]cuda\d*[-_.](plugin|pjrt)"
HIDDEN_VARIABLE = "CUDA_VISIBLE_DEVICES"


def cuda_plugin_installed(search_path: list[str] | None = None) -> bool:
    """Tell whether a JAX CUDA plugin is installed on ``search_path``.

    JAX needs a "plugin" package to talk to an NVIDIA GPU. This function looks
    for one by name pattern, so it finds a plugin for any CUDA major version.
    The default search path is ``sys.path``. It returns True for a module
    ``jax_plugins.xla_cuda*`` or for a distribution whose name matches
    ``PLUGIN_DIST_PATTERN`` (review R8 a: a move to CUDA 13 must not turn every
    start failure into "no plugin", which would be a skip). Nothing is
    imported, so a broken plugin is still found. The source text of this
    function is embedded in the probe subprocess (see ``PROBE``).
    """
    import importlib.metadata as metadata
    import pkgutil
    import re

    paths = [
        str(entry)
        for entry in (sys.path if search_path is None else search_path)
    ]
    for entry in paths:
        if any(
            m.name.startswith(PLUGIN_MODULE_PREFIX)
            for m in pkgutil.iter_modules([os.path.join(entry, "jax_plugins")])
        ):
            return True
    return any(
        re.fullmatch(PLUGIN_DIST_PATTERN, dist.metadata["Name"] or "", re.I)
        for dist in metadata.distributions(path=paths)
    )


PROBE = (
    "import os, sys\n"
    f"PLUGIN_MODULE_PREFIX = {PLUGIN_MODULE_PREFIX!r}\n"
    f"PLUGIN_DIST_PATTERN = {PLUGIN_DIST_PATTERN!r}\n"
    + inspect.getsource(cuda_plugin_installed)
    + "import jax\n"
    "try:\n"
    "    devices = jax.devices('gpu')\n"
    "except RuntimeError as exc:\n"
    "    plugin = cuda_plugin_installed()\n"
    "    print('NO_GPU: cuda plugin installed =', plugin, '|', str(exc)[-300:])\n"
    f"    sys.exit({BACKEND_FAILED_EXIT} if plugin else {NO_PLUGIN_EXIT})\n"
    "print('GPU', jax.default_backend(), len(devices), devices[0].device_kind)\n"
)


def classify_probe(returncode: int, text: str, devices_hidden: bool) -> str:
    """Decide what the GPU probe's result means: ``ok``, ``skip`` or ``fail``.

    The inputs are the probe's exit code, its combined output text and whether
    the parent process hides GPUs (``devices_hidden``). The answer is ``skip``
    only when there is no CUDA to start and nothing was set up to hide it: either
    no CUDA plugin is installed (exit 3), or a plugin is installed and ``cuInit``
    (the driver's start-up call) reports ``CUDA_ERROR_NO_DEVICE`` (exit 4 and
    that mark in the output, which JAX logs to stderr) while
    ``CUDA_VISIBLE_DEVICES`` is **unset** in the parent. With the variable set,
    a no-device report is a configuration fault of the GPU workstation (an
    inherited ``CUDA_VISIBLE_DEVICES=-1`` would hide the card), so the answer is
    ``fail`` (review R8 b). Every other failure, including a CUDA backend that is
    present but will not start, is also ``fail`` (PRIME.4: a broken GPU stack
    must not look like a pass).
    """
    if returncode == 0:
        return "ok"
    if returncode == NO_PLUGIN_EXIT:
        return "skip"
    if (
        returncode == BACKEND_FAILED_EXIT
        and NO_DEVICE_MARK in text
        and not devices_hidden
    ):
        return "skip"
    return "fail"


@dataclass
class Difference:
    """Counts and worst cases from comparing two results trees leaf by leaf.

    Attributes
    ----------
    n_leaves, n_floats : int
        Number of leaves compared, and how many of them are floats.
    n_different, n_one_sided : int
        Leaves whose values differ, and leaves present in only one tree.
    max_abs, max_rel : float
        Largest absolute and relative difference among float leaves.
    where_abs, where_rel : str
        Leaf path at which each maximum occurs.
    examples : list of str
        Up to ten human-readable descriptions of differences.
    """

    n_leaves: int = 0
    n_floats: int = 0
    n_different: int = 0
    n_one_sided: int = 0
    max_abs: float = 0.0
    max_rel: float = 0.0
    where_abs: str = ""
    where_rel: str = ""
    examples: list[str] = field(default_factory=list)


def float_bits(value: float) -> bytes:
    """Return the 8 bytes that store ``value`` as an IEEE-754 binary64 float.

    Equal bytes mean the same float, "not a number" (NaN) values included, so
    comparing bytes is a strict bitwise test.
    """
    return struct.pack("<d", value)


def leaves(tree: object, path: tuple = ()) -> dict[tuple, object]:
    """Flatten a nested JSON tree into ``{path: leaf}``.

    Dictionary keys named ``seconds`` and the top-level ``provenance`` block are
    skipped: timing and provenance (who ran what, where) are the two things the
    declared tolerance allows to differ. This is the test's own walk, independent
    of ``tools/compare_runs.py`` and ``tools/compare_pilot.py``.
    """
    if isinstance(tree, dict):
        out: dict[tuple, object] = {}
        if not tree:
            out[(*path, "{}")] = "empty dict"
        for key, value in tree.items():
            if key == "seconds" or (not path and key == "provenance"):
                continue
            out.update(leaves(value, (*path, key)))
        return out
    if isinstance(tree, list):
        out = {}
        for index, value in enumerate(tree):
            out.update(leaves(value, (*path, f"[{index}]")))
        if not tree:
            out[(*path, "[]")] = "empty list"
        return out
    return {path: tree}


def compare_bitwise(first: dict, second: dict) -> Difference:
    """Compare two results trees leaf by leaf and return a ``Difference``.

    Floats are compared by their IEEE bytes, everything else by type and value.
    """
    one, two = leaves(first), leaves(second)
    diff = Difference(n_leaves=len(set(one) | set(two)))
    for path in sorted(set(one) ^ set(two), key=str):
        diff.n_one_sided += 1
        if len(diff.examples) < 10:
            diff.examples.append(f"one-sided {'/'.join(map(str, path))}")
    for path in sorted(set(one) & set(two), key=str):
        a, b = one[path], two[path]
        name = "/".join(map(str, path))
        if isinstance(a, float) and isinstance(b, float):
            diff.n_floats += 1
            if float_bits(a) == float_bits(b):
                continue
            diff.n_different += 1
            if math.isfinite(a) and math.isfinite(b):
                abs_diff = abs(a - b)
                rel_diff = abs_diff / max(abs(a), abs(b))
            else:
                # A NaN or infinity that differs is counted as infinite.
                abs_diff = rel_diff = math.inf
            if abs_diff > diff.max_abs:
                diff.max_abs, diff.where_abs = abs_diff, name
            if rel_diff > diff.max_rel:
                diff.max_rel, diff.where_rel = rel_diff, name
            if len(diff.examples) < 10:
                diff.examples.append(f"float {name}: {a!r} -> {b!r}")
        elif type(a) is not type(b) or a != b:
            diff.n_different += 1
            if len(diff.examples) < 10:
                diff.examples.append(f"{name}: {a!r} -> {b!r}")
    return diff


def load_compare_runs():
    """Import ``tools/compare_runs.py`` by file path (``tools`` is not a package)."""
    spec = importlib.util.spec_from_file_location(
        "compare_runs_for_gpu_test", REPO_ROOT / "tools" / "compare_runs.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def gpu_environment() -> dict[str, str]:
    """Return the environment variables for a child process that uses the GPU.

    CUDA only (no silent fallback to the CPU) and no memory preallocation (section
    4.5). The persistent compilation cache is turned off
    (``JAX_ENABLE_COMPILATION_CACHE=false`` and no ``JAX_COMPILATION_CACHE_DIR``),
    so run 2 cannot load run 1's compiled programs or autotuning choices
    (review R4).
    """
    env = {
        **os.environ,
        "JAX_PLATFORMS": "cuda",
        "XLA_PYTHON_CLIENT_PREALLOCATE": "false",
        "JAX_ENABLE_COMPILATION_CACHE": "false",
    }
    env.pop("JAX_COMPILATION_CACHE_DIR", None)
    return env


def require_gpu(capsys: pytest.CaptureFixture[str]) -> str:
    """Probe for a GPU: skip if there is none, fail if it is broken or hidden.

    Returns the probe's one-line description of the GPU. The reason is printed
    with output capture turned off in both cases, because ``-rfE`` does not
    report skips (R1).
    """
    probe_env = {**gpu_environment(), "JAX_PLATFORMS": WRAPPER_PLATFORMS}
    done = subprocess.run(
        [sys.executable, "-c", PROBE],
        cwd=REPO_ROOT,
        env=probe_env,
        capture_output=True,
        timeout=PROBE_TIMEOUT_SECONDS,
    )
    out = done.stdout.decode(errors="replace").strip()
    err = done.stderr.decode(errors="replace")
    hidden = HIDDEN_VARIABLE in os.environ
    verdict = classify_probe(done.returncode, out + "\n" + err, hidden)
    if verdict == "skip":
        message = f"SKIPPED: no CUDA backend or device available to jax, so the GPU reproducibility test did not run: {out}"
        with capsys.disabled():
            print("\n" + message)
        pytest.skip(message)
    if verdict == "fail":
        if hidden and NO_DEVICE_MARK in out + err:
            reason = (
                f"FAILED: the driver reports no CUDA device while {HIDDEN_VARIABLE}={os.environ[HIDDEN_VARIABLE]!r} "
                "is set in the environment: on the GPU workstation a hidden device is a configuration fault, "
                "not a skip. Unset the variable, or run on a host without CUDA."
            )
        else:
            reason = (
                f"FAILED: the jax GPU probe exited {done.returncode} although a CUDA backend is present or the "
                "cause is not 'no device': a broken GPU stack, not a skip."
            )
        message = (
            reason
            + f" stdout: {out}\nstderr tail:\n"
            + "\n".join(err.splitlines()[-15:])
        )
        with capsys.disabled():
            print("\n" + message)
        pytest.fail(message, pytrace=False)
    return out


def run_smoke(out_dir: Path) -> tuple[dict, float]:
    """Run the smoke preset (seed DEV-0) on the GPU in a child process.

    Returns the parsed ``results.json`` tree and the wall-clock seconds.
    """
    start = time.monotonic()
    done = subprocess.run(
        [
            sys.executable,
            "-m",
            "lpcstudy",
            "--preset",
            "smoke",
            "--seed-id",
            SEED_ID,
            "--out",
            str(out_dir),
        ],
        cwd=REPO_ROOT,
        env=gpu_environment(),
        capture_output=True,
        timeout=RUN_TIMEOUT_SECONDS,
    )
    seconds = time.monotonic() - start
    tail = "\n".join(done.stderr.decode(errors="replace").splitlines()[-20:])
    assert (
        done.returncode == 0
    ), f"smoke preset on the GPU exited {done.returncode}; stderr tail:\n{tail}"
    return json.loads((out_dir / "smoke" / "results.json").read_text()), seconds


def test_smoke_twice_on_gpu_is_bitwise_reproducible(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], record_property
) -> None:
    """Two GPU runs of the smoke preset (DEV-0, same settings) agree bit for bit.

    This is reproducibility tier T0: "bitwise", the strictest tier.

    Reference (independent): the first run against the second run. The pair is its
    own reference, because the claim is that two executions of the same code on the
    same device agree, not that either equals a known value. The comparison is this
    file's own walk of the two ``results.json`` trees, with floats compared as
    IEEE-754 bytes. It does not use ``tools/compare_runs.py``; that tool is
    imported afterwards only to classify the pair (tier T0, exit 0), as a second,
    independent reading of the same files. Nothing is compared between the GPU and
    the CPU: across devices the contexts differ and the rule is the TD statistic,
    not a per-leaf tolerance.

    Declared tolerance: **bitwise**. The maximum absolute difference is 0.0 and the
    maximum relative difference is 0.0 over every leaf except timing (keys
    ``seconds``) and the top-level ``provenance`` block. No leaf may exist on one
    side only, and no integer, boolean, string or null leaf may differ. Source: the
    declared reproducibility tolerance of WU-0003.6, item 1 (same context, device
    type, host, code, seed and environment: tier T0, bitwise; draft decision in
    ``docs/agent/notes/2026-10-18-owner-decision-drafts.md`` section 1). The
    measured fact behind it is R1 against R2 (DEV-1 pilot on this host's GPU,
    20,533 of 20,533 leaves equal). The tolerance was fixed before this test ran
    and is not loosened on failure (PRIME.2): a difference is a nondeterminism
    finding to be recorded as a DEF (defect), not a reason to widen it. No Monte
    Carlo error applies: nothing is estimated, and the test draws no random number
    (the seed is the registered DEV-0, passed to the preset).

    Scope of the property (review R3). Bitwise repeatability of a GPU run is a
    **measured property of this card, driver and jaxlib (RTX 4090, jaxlib 0.11.2),
    without ``--xla_gpu_deterministic_ops``** (plan item O3, still open), not a
    guarantee of XLA or CUDA. The tolerance cited is the ruled but not yet entered
    decision of WU-0003.6 (no DEC id exists yet; the draft is the file above). A
    failure after a driver, jaxlib or host change is a finding about that change,
    to be recorded as a DEF, and not a reason to widen the tolerance.

    Settings check: the two ``provenance`` blocks must agree on seed, preset,
    config, commit, dirty flag, device, environment, package versions, Python,
    ``jax_x64`` and matmul precision, so "identical settings" is verified.
    ``jax_x64`` must be true (float64). The children run with the persistent
    compilation cache off, so run 2 cannot reuse run 1's compiled code. The parent
    must have ``JAX_PLATFORMS=cuda,cpu`` (the wrapper's ``gpu`` tier): otherwise
    the test fails at once rather than start GPU jobs outside the lock.

    The test is skipped, not failed, only when there is no CUDA to start: no CUDA
    plugin installed (detected by pattern, any CUDA major version), or the driver
    reports ``CUDA_ERROR_NO_DEVICE`` while ``CUDA_VISIBLE_DEVICES`` is unset. The
    reason is printed with capture disabled, because ``-rfE`` does not report
    skips. A CUDA backend that is present but will not start fails the test, and
    so does a no-device report with ``CUDA_VISIBLE_DEVICES`` set (a hidden device
    is a configuration fault on the GPU workstation). The measured maximum
    differences are printed (capture disabled) and recorded with
    ``record_property``. Cost: two smoke runs on the GPU, each about 4 times slower
    than on the CPU, inside the 1800 s tier timeout.
    """
    assert os.environ.get("JAX_PLATFORMS") == WRAPPER_PLATFORMS, (
        f"run this test only through tools/run_tests.sh gpu (it holds the GPU lock and sets JAX_PLATFORMS="
        f"{WRAPPER_PLATFORMS}); found JAX_PLATFORMS={os.environ.get('JAX_PLATFORMS')!r}. A direct call would "
        "start two GPU jobs outside the lock (LPC.AUTH.3, 4.5)."
    )
    probe = require_gpu(capsys)
    first, seconds_first = run_smoke(tmp_path / "run1")
    second, seconds_second = run_smoke(tmp_path / "run2")

    one, two = first["provenance"], second["provenance"]
    assert (
        one["device"]["backend"] in GPU_BACKENDS
        and two["device"]["backend"] in GPU_BACKENDS
    ), (one["device"], two["device"])
    assert one["seed_id"] == SEED_ID and one["seed_kind"] == "development", (
        one["seed_id"],
        one["seed_kind"],
    )
    assert one["jax_x64"] is True and two["jax_x64"] is True, (
        one["jax_x64"],
        two["jax_x64"],
    )  # float64 convention
    for key in SAME_SETTINGS:
        assert (
            one[key] == two[key]
        ), f"provenance {key!r} differs between the two runs: {one[key]!r} vs {two[key]!r}"

    diff = compare_bitwise(first, second)
    tool = load_compare_runs()
    cmp = tool.compare_trees(first, second)
    summary = (
        f"GPU reproducibility, smoke {SEED_ID}, run 1 {seconds_first:.0f} s, run 2 {seconds_second:.0f} s ({probe}): "
        f"{diff.n_leaves} leaves compared ({diff.n_floats} floats), {diff.n_different} different, "
        f"{diff.n_one_sided} one-sided; max abs difference {diff.max_abs!r}"
        f"{' at ' + diff.where_abs if diff.where_abs else ''}; max rel difference {diff.max_rel!r}"
        f"{' at ' + diff.where_rel if diff.where_rel else ''}; declared tolerance bitwise "
        f"(abs {DECLARED_ABS}, rel {DECLARED_REL}); compare_runs tier {cmp.tier.name}, exit {cmp.exit_code}, "
        f"{len(cmp.rows)} differing and {len(cmp.one_sided)} one-sided leaves"
    )
    for name, value in (
        ("leaves", diff.n_leaves),
        ("different", diff.n_different),
        ("max_abs", diff.max_abs),
        ("max_rel", diff.max_rel),
        ("seconds_run1", seconds_first),
        ("seconds_run2", seconds_second),
        ("compare_runs_tier", cmp.tier.name),
        ("compare_runs_exit", cmp.exit_code),
    ):
        record_property(name, value)
    with capsys.disabled():
        print("\n" + summary)

    assert diff.n_leaves > MIN_LEAVES and diff.n_floats > MIN_LEAVES, summary
    assert diff.n_one_sided == 0, summary + "\n" + "\n".join(diff.examples)
    assert diff.max_abs <= DECLARED_ABS and diff.max_rel <= DECLARED_REL, (
        summary + "\n" + "\n".join(diff.examples)
    )
    assert diff.n_different == 0, summary + "\n" + "\n".join(diff.examples)
    assert (
        cmp.tier.name == "T0"
        and not cmp.rows
        and not cmp.one_sided
        and cmp.exit_code == 0
    ), (
        summary
        + "\n"
        + "\n".join(tool.render(cmp, "run1", "run2", show=5)[:40])
    )
