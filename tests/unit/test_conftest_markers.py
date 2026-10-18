"""Tests of the tier markers and the CPU-only guard in ``tests/conftest.py``.

``tests/conftest.py`` sorts every test into a tier (unit, integration, slow or
gpu) by its folder and stops tests outside ``tests/gpu`` from using a GPU. These
rules keep quick checks from touching the shared GPU, so they protect every
other test of the study (WU-0010.1). The independent reference for every test
here is the written rule, not the conftest's own output: the folder-to-tier table
of DEVELOPMENT_WORKFLOW.md section 4.1 (``tests/unit`` is unit,
``tests/integration`` is integration, ``tests/slow`` is slow, ``tests/gpu`` is
gpu) and the section 4.5 rule that tests outside ``tests/gpu/`` never request a
GPU. Each test builds a small throwaway ``tests/`` tree with the ``pytester``
tool (a pytest feature that runs pytest inside a temporary folder), copies in the
real ``tests/conftest.py`` and ``pytest.ini``, and checks what pytest does with
it. The results are exact (a marker is present or not), so no numerical
tolerance is involved.
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
    """Build the throwaway tree: copy the real conftest and pytest.ini into it.

    Returns the new ``tests`` folder, ready for the test to add tier folders.
    """
    tests = pytester.path / "tests"
    tests.mkdir()
    shutil.copy(REAL_TESTS / "conftest.py", tests / "conftest.py")
    shutil.copy(REAL_TESTS.parent / "pytest.ini", pytester.path / "pytest.ini")
    return tests


def test_directory_sets_exactly_one_tier_marker(
    pytester: pytest.Pytester,
) -> None:
    """A test in ``tests/<tier>/`` gets that tier's marker and no other."""
    tests = _tree(pytester)
    for tier in TIERS:
        (tests / tier).mkdir()
        (tests / tier / f"test_{tier}_probe.py").write_text(PROBE)
    items = pytester.inline_genitems()[0]
    assert len(items) == len(TIERS)
    for item in items:
        expected = item.path.parent.name
        assert {m.name for m in item.iter_markers()} & set(TIERS) == {expected}


def test_test_outside_a_tier_directory_fails_collection(
    pytester: pytest.Pytester,
) -> None:
    """A test in ``tests/misc/`` stops collection and names the placement rule.

    ``misc`` is not a tier folder, so pytest must refuse to collect the file.
    """
    tests = _tree(pytester)
    (tests / "misc").mkdir()
    (tests / "misc" / "test_x.py").write_text(PROBE)
    result = pytester.runpytest_subprocess("--collect-only", "-q")
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    result.stderr.fnmatch_lines(
        ["*Tests outside a tier directory*tests/misc/test_x.py*"]
    )


def test_gpu_request_outside_gpu_tier_fails_with_clear_message(
    pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``jax.devices("gpu")`` in ``tests/unit`` fails with the guard's message.

    ``JAX_PLATFORMS`` is unset here on purpose: the guard acts before JAX does,
    so the GPU driver is never started and the guard does not rely on that
    setting.
    """
    tests = _tree(pytester)
    (tests / "unit").mkdir()
    (tests / "unit" / "test_gpu_call.py").write_text(GPU_CALL)
    monkeypatch.delenv("JAX_PLATFORMS", raising=False)
    # Hide the devices so a regressed guard cannot initialize CUDA or ROCm outside the lock.
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "")
    monkeypatch.setenv("ROCR_VISIBLE_DEVICES", "")
    result = pytester.runpytest_subprocess()
    assert result.ret == pytest.ExitCode.TESTS_FAILED
    result.stdout.fnmatch_lines(["*GPU device requested outside tests/gpu/*"])


def test_gpu_tier_is_not_guarded(
    pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The same call in ``tests/gpu`` is not stopped by the guard.

    With ``JAX_PLATFORMS=cpu`` JAX itself refuses the request (no GPU is present
    or touched), and the message must come from JAX, not from the guard.
    """
    tests = _tree(pytester)
    (tests / "gpu").mkdir()
    (tests / "gpu" / "test_gpu_call.py").write_text(GPU_CALL)
    monkeypatch.setenv("JAX_PLATFORMS", "cpu")
    result = pytester.runpytest_subprocess()
    assert result.ret == pytest.ExitCode.TESTS_FAILED
    output = result.stdout.str() + result.stderr.str()
    assert "GPU device requested outside tests/gpu/" not in output
    assert "Unknown backend: 'gpu'" in output


def test_tier_marker_that_differs_from_directory_fails_collection(
    pytester: pytest.Pytester,
) -> None:
    """A ``@pytest.mark.gpu`` test in ``tests/unit/`` stops collection.

    A marker that disagrees with the folder is refused, so a marker can neither
    lift the guard nor give a test two tiers.
    """
    tests = _tree(pytester)
    (tests / "unit").mkdir()
    (tests / "unit" / "test_marked.py").write_text(
        "import pytest\n\n\n@pytest.mark.gpu\ndef test_marked() -> None:\n    pass\n"
    )
    result = pytester.runpytest_subprocess("--collect-only", "-q")
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    result.stderr.fnmatch_lines(
        [
            "*Tier marker differs from the directory tier*test_marked*directory tier 'unit'*gpu*"
        ]
    )
