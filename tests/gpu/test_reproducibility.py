"""GPU reproducibility: the smoke preset twice on the GPU, same settings (WU-0004c, ruling B10).

Run only through ``tools/run_tests.sh gpu tests/gpu/test_reproducibility.py`` (it holds the GPU
lock ``/tmp/lpcstudy-gpu.lock`` and the 1800 s timeout of DEVELOPMENT_WORKFLOW.md 4.5). Never
rerun without a code change (4.4). The test refuses to start unless the parent has
``JAX_PLATFORMS=cuda,cpu`` (only the wrapper's ``gpu`` tier sets it), so a direct call cannot start
two GPU jobs outside the lock (WU-0004c review R6).
"""

from __future__ import annotations

import importlib.util
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
RUN_TIMEOUT_SECONDS = 780          # two runs plus the probe stay under the 1800 s tier timeout
NO_PLUGIN_EXIT = 3                 # RuntimeError from jax.devices('gpu') and no CUDA plugin installed
BACKEND_FAILED_EXIT = 4            # RuntimeError from jax.devices('gpu') with a CUDA plugin installed
NO_DEVICE_MARK = "CUDA_ERROR_NO_DEVICE"   # cuInit's own message when the driver sees no device
WRAPPER_PLATFORMS = "cuda,cpu"     # set by tools/run_tests.sh for the gpu tier only
MIN_LEAVES = 1000                  # floor against an empty tree; the default (one-system) smoke at bd8e168
                                   # has 4,695 leaves, of which 3,166 are floats
DECLARED_ABS = 0.0                 # tier T0 of the declared tolerance: bitwise (see the test docstring)
DECLARED_REL = 0.0
SAME_SETTINGS = ("seed_id", "seed_kind", "preset", "config", "commit", "dirty", "device", "env", "packages",
                 "python", "jax_x64", "jax_matmul_precision")
CUDA_PLUGINS = ("jax_plugins.xla_cuda12", "jax_cuda12_plugin")

PROBE = (
    "import importlib.util, sys\n"
    "import jax\n"
    "try:\n"
    "    devices = jax.devices('gpu')\n"
    "except RuntimeError as exc:\n"
    "    def installed(name):\n"
    "        try:\n"
    "            return importlib.util.find_spec(name) is not None\n"
    "        except ImportError:\n"
    "            return False\n"
    f"    plugin = any(installed(name) for name in {CUDA_PLUGINS!r})\n"
    "    print('NO_GPU: cuda plugin installed =', plugin, '|', str(exc)[-300:])\n"
    f"    sys.exit({BACKEND_FAILED_EXIT} if plugin else {NO_PLUGIN_EXIT})\n"
    "print('GPU', jax.default_backend(), len(devices), devices[0].device_kind)\n")


def classify_probe(returncode: int, text: str) -> str:
    """Return ``ok``, ``skip`` or ``fail`` for the probe's exit code and its combined output.

    ``skip`` only when there is no CUDA to start: no CUDA plugin installed (exit 3), or a plugin
    whose ``cuInit`` reports ``CUDA_ERROR_NO_DEVICE`` (exit 4 and that mark in the output, which jax
    logs to stderr). Every other failure, including a CUDA backend that is present but will not start,
    is ``fail`` (PRIME.4: a broken GPU stack must not look like a pass).
    """
    if returncode == 0:
        return "ok"
    if returncode == NO_PLUGIN_EXIT:
        return "skip"
    if returncode == BACKEND_FAILED_EXIT and NO_DEVICE_MARK in text:
        return "skip"
    return "fail"


@dataclass
class Difference:
    """Result of the bitwise comparison of two results trees."""

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
    """IEEE-754 binary64 bytes of ``value`` (equal bytes mean the same float, NaN included)."""
    return struct.pack("<d", value)


def leaves(tree: object, path: tuple = ()) -> dict[tuple, object]:
    """Flatten a JSON tree to ``{path: leaf}``; dict keys ``seconds`` and the top-level ``provenance`` are skipped.

    This is the test's own walk (independent of ``tools/compare_runs.py`` and ``compare_pilot``):
    timing and the provenance block are the two exclusions of the declared tolerance.
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
    """Compare two results trees leaf by leaf: floats by IEEE bytes, everything else by type and value."""
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
                abs_diff = rel_diff = math.inf          # a NaN or infinity that differs is counted as infinite
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
    """Import ``tools/compare_runs.py`` (not a package) by path."""
    spec = importlib.util.spec_from_file_location("compare_runs_for_gpu_test", REPO_ROOT / "tools" / "compare_runs.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def gpu_environment() -> dict[str, str]:
    """The environment of a GPU child: CUDA only (no silent CPU fallback), no preallocation (4.5).

    The persistent compilation cache is pinned off (``JAX_ENABLE_COMPILATION_CACHE=false`` and no
    ``JAX_COMPILATION_CACHE_DIR``), so run 2 cannot load run 1's compiled executables or autotuning
    choices (review R4).
    """
    env = {**os.environ, "JAX_PLATFORMS": "cuda", "XLA_PYTHON_CLIENT_PREALLOCATE": "false",
           "JAX_ENABLE_COMPILATION_CACHE": "false"}
    env.pop("JAX_COMPILATION_CACHE_DIR", None)
    return env


def require_gpu(capsys: pytest.CaptureFixture[str]) -> str:
    """Skip when there is no CUDA to start; fail when CUDA is present but broken. Returns the probe line.

    The skip reason is printed with capture disabled, because ``-rfE`` does not report skips (R1).
    """
    probe_env = {**gpu_environment(), "JAX_PLATFORMS": WRAPPER_PLATFORMS}
    done = subprocess.run([sys.executable, "-c", PROBE], cwd=REPO_ROOT, env=probe_env, capture_output=True,
                          timeout=PROBE_TIMEOUT_SECONDS)
    out = done.stdout.decode(errors="replace").strip()
    err = done.stderr.decode(errors="replace")
    verdict = classify_probe(done.returncode, out + "\n" + err)
    if verdict == "skip":
        message = f"SKIPPED: no CUDA backend or device available to jax, so the GPU reproducibility test did not run: {out}"
        with capsys.disabled():
            print("\n" + message)
        pytest.skip(message)
    assert verdict == "ok", (
        f"the jax GPU probe failed (exit {done.returncode}) although a CUDA backend is present or the cause is "
        f"not 'no device': this is a broken GPU stack, not a skip. stdout: {out}\nstderr tail:\n"
        + "\n".join(err.splitlines()[-15:]))
    return out


def run_smoke(out_dir: Path) -> tuple[dict, float]:
    """Run ``python -m lpcstudy --preset smoke --seed-id DEV-0`` on the GPU; return the results tree and the seconds."""
    start = time.monotonic()
    done = subprocess.run(
        [sys.executable, "-m", "lpcstudy", "--preset", "smoke", "--seed-id", SEED_ID, "--out", str(out_dir)],
        cwd=REPO_ROOT, env=gpu_environment(), capture_output=True, timeout=RUN_TIMEOUT_SECONDS)
    seconds = time.monotonic() - start
    tail = "\n".join(done.stderr.decode(errors="replace").splitlines()[-20:])
    assert done.returncode == 0, f"smoke preset on the GPU exited {done.returncode}; stderr tail:\n{tail}"
    return json.loads((out_dir / "smoke" / "results.json").read_text()), seconds


def test_smoke_twice_on_gpu_is_bitwise_reproducible(tmp_path: Path, capsys: pytest.CaptureFixture[str],
                                                    record_property) -> None:
    """Two GPU runs of the smoke preset (DEV-0, identical settings) agree bitwise; tier T0.

    Reference (independent): the first run against the second run. The pair is its own reference,
    because the claim is that two executions of the same code on the same device agree, not that
    either equals a value. The comparison is this file's own walk of the two ``results.json``
    trees, with floats compared as IEEE-754 bytes. It does not use ``tools/compare_runs.py``;
    that tool is imported afterwards only to classify the pair (tier T0, exit 0), as a second,
    independent reading of the same files. Nothing is compared between the GPU and the CPU: across
    devices the contexts differ and the rule is the TD statistic, not a per-leaf tolerance.

    Declared tolerance: **bitwise**. Maximum absolute difference 0.0 and maximum relative
    difference 0.0 over every leaf except timing (keys ``seconds``) and the top-level
    ``provenance`` block; no leaf on one side only; no integer, boolean, string or null leaf
    different. Source: the declared reproducibility tolerance of WU-0003.6, item 1 (same context,
    same device type, host, code, seed and environment: tier T0, bitwise; draft decision in
    ``docs/agent/notes/2026-10-18-owner-decision-drafts.md`` section 1), for which the measured
    fact is R1 against R2 (DEV-1 pilot on this host's GPU, 20,533 of 20,533 leaves equal). The
    tolerance was fixed before this test ran and is not loosened on failure (PRIME.2): a
    difference is a nondeterminism finding to be recorded as a DEF, not a reason to widen it.
    No Monte Carlo error applies: nothing is estimated, and the test draws no random number
    (the seed is the registered DEV-0, passed to the preset).

    Scope of the property (review R3). Bitwise repeatability of a GPU run is a **measured
    property of this card, driver and jaxlib (RTX 4090, jaxlib 0.11.2), without
    ``--xla_gpu_deterministic_ops``** (plan item O3, still open), not a guarantee of XLA or CUDA.
    The tolerance cited is the ruled but not yet entered decision of WU-0003.6 (no DEC id exists
    yet; the draft is the file above). A failure after a driver, jaxlib or host change is a
    finding about that change, to be recorded as a DEF, and not a reason to widen the tolerance.

    Settings check: the two ``provenance`` blocks must agree on seed, preset, config, commit,
    dirty flag, device, environment, package versions, python, ``jax_x64`` and matmul precision,
    so "identical settings" is verified; ``jax_x64`` must be true (float64). The children run
    with the persistent compilation cache off, so run 2 cannot reuse run 1's compiled code.
    The parent must have ``JAX_PLATFORMS=cuda,cpu`` (the wrapper's ``gpu`` tier): otherwise the
    test fails at once rather than start GPU jobs outside the lock.
    The test is skipped, not failed, only when there is no CUDA to start: no CUDA plugin
    installed, or the driver reports ``CUDA_ERROR_NO_DEVICE``; the reason is printed with capture
    disabled, because ``-rfE`` does not report skips. A CUDA backend that is present but will not
    start fails the test. The measured maximum differences are printed (capture disabled) and
    recorded with ``record_property``.
    Cost: two smoke runs on the GPU, each about 4 times slower than on the CPU, inside the
    1800 s tier timeout.
    """
    assert os.environ.get("JAX_PLATFORMS") == WRAPPER_PLATFORMS, (
        f"run this test only through tools/run_tests.sh gpu (it holds the GPU lock and sets JAX_PLATFORMS="
        f"{WRAPPER_PLATFORMS}); found JAX_PLATFORMS={os.environ.get('JAX_PLATFORMS')!r}. A direct call would "
        "start two GPU jobs outside the lock (LPC.AUTH.3, 4.5).")
    probe = require_gpu(capsys)
    first, seconds_first = run_smoke(tmp_path / "run1")
    second, seconds_second = run_smoke(tmp_path / "run2")

    one, two = first["provenance"], second["provenance"]
    assert one["device"]["backend"] in GPU_BACKENDS and two["device"]["backend"] in GPU_BACKENDS, (
        one["device"], two["device"])
    assert one["seed_id"] == SEED_ID and one["seed_kind"] == "development", (one["seed_id"], one["seed_kind"])
    assert one["jax_x64"] is True and two["jax_x64"] is True, (one["jax_x64"], two["jax_x64"])   # float64 convention
    for key in SAME_SETTINGS:
        assert one[key] == two[key], f"provenance {key!r} differs between the two runs: {one[key]!r} vs {two[key]!r}"

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
        f"{len(cmp.rows)} differing and {len(cmp.one_sided)} one-sided leaves")
    for name, value in (("leaves", diff.n_leaves), ("different", diff.n_different), ("max_abs", diff.max_abs),
                        ("max_rel", diff.max_rel), ("seconds_run1", seconds_first), ("seconds_run2", seconds_second),
                        ("compare_runs_tier", cmp.tier.name), ("compare_runs_exit", cmp.exit_code)):
        record_property(name, value)
    with capsys.disabled():
        print("\n" + summary)

    assert diff.n_leaves > MIN_LEAVES and diff.n_floats > MIN_LEAVES, summary
    assert diff.n_one_sided == 0, summary + "\n" + "\n".join(diff.examples)
    assert diff.max_abs <= DECLARED_ABS and diff.max_rel <= DECLARED_REL, summary + "\n" + "\n".join(diff.examples)
    assert diff.n_different == 0, summary + "\n" + "\n".join(diff.examples)
    assert cmp.tier.name == "T0" and not cmp.rows and not cmp.one_sided and cmp.exit_code == 0, (
        summary + "\n" + "\n".join(tool.render(cmp, "run1", "run2", show=5)[:40]))
