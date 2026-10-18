"""Hand cases for the GPU probe of ``tests/gpu/test_reproducibility.py`` (WU-0004c, review R8).

The probe decides skip or fail for the ``gpu`` reproducibility test, so a wrong rule would turn a broken
GPU stack into a silent skip. These tests run on the CPU and start no GPU job; they import the gpu test
module by path (it only imports pytest and the standard library at module level).

References (none is the code under test):

* ``classify_probe``: the decision table of the plan, typed by hand. Exit 0 is ok; exit 3 (no CUDA
  plugin) skips; exit 4 (a plugin is installed and jax raised) skips only with cuInit's
  ``CUDA_ERROR_NO_DEVICE`` in the output and ``CUDA_VISIBLE_DEVICES`` unset in the parent; every other
  exit, and exit 4 without the mark or with the variable set, fails.
* ``cuda_plugin_installed``: synthetic site directories built here with a known content (a
  ``jax_plugins/xla_cuda13`` module, a ``jax_cuda13_plugin-1.0.dist-info`` metadata directory, and
  non-CUDA look-alikes), so the expected answer is known by construction. Exact (booleans).

No tolerance is involved: every assertion is an exact equality of strings or booleans.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

GPU_TEST = Path(__file__).resolve().parents[1] / "gpu" / "test_reproducibility.py"
MARK = "CUDA_ERROR_NO_DEVICE"


@pytest.fixture(scope="module")
def probe_module():
    """The gpu reproducibility test module, imported by path under a private name."""
    spec = importlib.util.spec_from_file_location("gpu_reproducibility_for_probe_tests", GPU_TEST)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(("code", "text", "hidden", "expected"), [
    (0, "", False, "ok"),
    (0, "", True, "ok"),
    (3, "", False, "skip"),                              # no CUDA plugin installed
    (3, "", True, "skip"),
    (4, f"cuInit(0) failed: {MARK}", False, "skip"),     # plugin, driver sees no device, variable unset
    (4, f"cuInit(0) failed: {MARK}", True, "fail"),      # same, but CUDA_VISIBLE_DEVICES is set: a configuration fault
    (4, "ValueError: XLA_PYTHON_CLIENT_ALLOCATOR env var must be one of", False, "fail"),   # present but will not start
    (4, "", False, "fail"),
    (1, "ImportError: No module named jax", False, "fail"),
    (1, f"{MARK}", False, "fail"),                       # the mark with an unexpected exit code is not a skip
    (2, "", False, "fail"),
    (-9, "", False, "fail"),
])
def test_classify_probe_decision_table(probe_module, code: int, text: str, hidden: bool, expected: str) -> None:
    """``classify_probe`` returns the table's answer for each hand case (exact)."""
    assert probe_module.classify_probe(code, text, hidden) == expected


def make_site(root: Path, modules: tuple[str, ...] = (), dists: tuple[str, ...] = ()) -> str:
    """A synthetic site directory with ``jax_plugins/<module>/__init__.py`` and ``<dist>-1.0.dist-info/METADATA``."""
    root.mkdir(parents=True, exist_ok=True)
    for module in modules:
        package = root / "jax_plugins" / module
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("")
    for dist in dists:
        info = root / f"{dist.replace('-', '_')}-1.0.dist-info"
        info.mkdir()
        (info / "METADATA").write_text(f"Metadata-Version: 2.1\nName: {dist}\nVersion: 1.0\n")
    return str(root)


@pytest.mark.parametrize(("modules", "dists", "expected"), [
    ((), (), False),                                     # empty site
    (("xla_cuda12",), (), True),                         # CUDA 12 module
    (("xla_cuda13",), (), True),                         # a later CUDA major version: found by pattern
    ((), ("jax-cuda12-plugin",), True),
    ((), ("jax_cuda13_plugin",), True),                  # a later CUDA major version, underscore spelling
    ((), ("jax-cuda13-pjrt",), True),
    (("xla_rocm",), ("jax-rocm60-plugin",), False),      # other accelerators are not CUDA
    ((), ("jax", "jaxlib", "numpy"), False),             # unrelated distributions
    ((), ("jax-cudaish-helper",), False),                # name that only starts like a plugin
])
def test_cuda_plugin_detection_by_pattern(probe_module, tmp_path: Path, modules, dists, expected: bool) -> None:
    """``cuda_plugin_installed`` finds a CUDA plugin of any major version on a synthetic site, and nothing else."""
    site = make_site(tmp_path / "site", modules, dists)
    assert probe_module.cuda_plugin_installed([site]) is expected


def test_probe_source_compiles_and_embeds_the_detector(probe_module) -> None:
    """The probe subprocess source is valid Python and carries the pattern constants and the detector."""
    compile(probe_module.PROBE, "probe", "exec")
    assert "def cuda_plugin_installed" in probe_module.PROBE
    assert probe_module.PLUGIN_MODULE_PREFIX in probe_module.PROBE
    assert probe_module.PLUGIN_DIST_PATTERN.replace("\\", "\\\\") in probe_module.PROBE
