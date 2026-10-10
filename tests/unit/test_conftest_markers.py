"""Tier markers and the CPU-only guard of ``tests/conftest.py`` (WU-0010.1).

Reference for every test here: the directory-to-tier table of DEVELOPMENT_WORKFLOW.md
section 4.1 (``tests/unit`` -> unit, ``tests/integration`` -> integration, ``tests/slow``
-> slow, ``tests/gpu`` -> gpu) and the section 4.5 rule that tests outside ``tests/gpu/``
never request a GPU. Each test builds a synthetic ``tests/`` tree in a ``pytester``
directory that holds copies of the real ``tests/conftest.py`` and ``pytest.ini``. The
oracle is the table, not the conftest's own output. There is no numerical tolerance.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

REAL_TESTS = Path(__file__).resolve().parents[1]
PROBE = "def test_probe() -> None:\n    pass\n"
GPU_CALL = 'import jax\n\n\ndef test_call() -> None:\n    jax.devices("gpu")\n'
TIERS = ("unit", "integration", "slow", "gpu")


def _tree(pytester: pytest.Pytester) -> Path:
    """Copy the real conftest and pytest.ini into the synthetic tree; return its tests dir."""
    tests = pytester.path / "tests"
    tests.mkdir()
    shutil.copy(REAL_TESTS / "conftest.py", tests / "conftest.py")
    shutil.copy(REAL_TESTS.parent / "pytest.ini", pytester.path / "pytest.ini")
    return tests


def test_directory_sets_exactly_one_tier_marker(pytester: pytest.Pytester) -> None:
    """A test under tests/<tier>/ carries that tier marker and no other tier marker."""
    tests = _tree(pytester)
    for tier in TIERS:
        (tests / tier).mkdir()
        (tests / tier / f"test_{tier}_probe.py").write_text(PROBE)
    items = pytester.inline_genitems()[0]
    assert len(items) == len(TIERS)
    for item in items:
        expected = item.path.parent.name
        assert {m.name for m in item.iter_markers()} & set(TIERS) == {expected}


def test_test_outside_a_tier_directory_fails_collection(pytester: pytest.Pytester) -> None:
    """A test under tests/misc/ makes collection fail and names the placement rule."""
    tests = _tree(pytester)
    (tests / "misc").mkdir()
    (tests / "misc" / "test_x.py").write_text(PROBE)
    result = pytester.runpytest_subprocess("--collect-only", "-q")
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    result.stderr.fnmatch_lines(["*Tests outside a tier directory*tests/misc/test_x.py*"])


def test_gpu_request_outside_gpu_tier_fails_with_clear_message(
        pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch) -> None:
    """jax.devices("gpu") in tests/unit fails with the guard's message when
    JAX_PLATFORMS is unset (the guard acts before jax, so CUDA is never initialized)."""
    tests = _tree(pytester)
    (tests / "unit").mkdir()
    (tests / "unit" / "test_gpu_call.py").write_text(GPU_CALL)
    monkeypatch.delenv("JAX_PLATFORMS", raising=False)
    result = pytester.runpytest_subprocess()
    assert result.ret == pytest.ExitCode.TESTS_FAILED
    result.stdout.fnmatch_lines(["*GPU device requested outside tests/gpu/*"])


def test_gpu_tier_is_not_guarded(pytester: pytest.Pytester,
                                 monkeypatch: pytest.MonkeyPatch) -> None:
    """The same call under tests/gpu with JAX_PLATFORMS=cpu is refused by jax itself
    (no GPU present or touched), not by the guard."""
    tests = _tree(pytester)
    (tests / "gpu").mkdir()
    (tests / "gpu" / "test_gpu_call.py").write_text(GPU_CALL)
    monkeypatch.setenv("JAX_PLATFORMS", "cpu")
    result = pytester.runpytest_subprocess()
    assert result.ret == pytest.ExitCode.TESTS_FAILED
    output = result.stdout.str() + result.stderr.str()
    assert "GPU device requested outside tests/gpu/" not in output
    assert "Unknown backend: 'gpu'" in output
