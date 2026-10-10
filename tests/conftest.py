"""Tier markers from the directory and the CPU-only guard (DEVELOPMENT_WORKFLOW.md 4.1, 4.5)."""

from __future__ import annotations

from pathlib import Path

import pytest

TIERS = ("unit", "integration", "slow", "gpu")
GPU_BACKENDS = frozenset({"gpu", "cuda", "rocm"})


def tier_of(path: str | Path, tests_root: str | Path) -> str | None:
    """Return the tier of a test file from its place under ``tests/``.

    Parameters
    ----------
    path : str or Path
        Path of the test file.
    tests_root : str or Path
        The ``tests/`` directory.

    Returns
    -------
    str or None
        The first path component under ``tests_root`` if it is in ``TIERS`` and
        the file lies inside that directory; otherwise ``None``.
    """
    try:
        parts = Path(path).resolve().relative_to(Path(tests_root).resolve()).parts
    except ValueError:
        return None
    return parts[0] if len(parts) > 1 and parts[0] in TIERS else None


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Mark every item with its tier, and refuse items outside a tier directory."""
    root = Path(__file__).parent
    misplaced = []
    for item in items:
        tier = tier_of(item.path, root)
        if tier is None:
            misplaced.append(item.nodeid)
        else:
            item.add_marker(getattr(pytest.mark, tier))
    if misplaced:
        raise pytest.UsageError(
            "Tests outside a tier directory (tests/unit, tests/integration, tests/slow, "
            "tests/gpu): place a test by cost and device (.claude/rules/tests.md): "
            + ", ".join(misplaced))


@pytest.fixture(autouse=True)
def _refuse_gpu(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    """Fail any test outside ``tests/gpu/`` that asks jax for a GPU device (4.5).

    The check runs before jax is called, so CUDA is never initialized, and does
    not depend on ``JAX_PLATFORMS``. ``Failed`` is a ``BaseException``, so a test's
    own ``except Exception`` does not swallow it.
    """
    if request.node.get_closest_marker("gpu") is not None:
        return
    import jax

    tier = next((t for t in TIERS if request.node.get_closest_marker(t)), None)

    def guard(backend: object) -> None:
        if isinstance(backend, str) and backend.lower() in GPU_BACKENDS:
            pytest.fail(
                f"GPU device requested outside tests/gpu/ (tier '{tier}', "
                f"{request.node.nodeid}): CPU-only tiers never touch the GPU "
                "(DEVELOPMENT_WORKFLOW.md 4.5); move the test to tests/gpu/.", pytrace=False)

    real_devices, real_local = jax.devices, jax.local_devices

    def devices(backend: object = None) -> list:
        guard(backend)
        return real_devices(backend)

    def local_devices(process_index: object = None, backend: object = None,
                      host_id: object = None) -> list:
        guard(backend)
        return real_local(process_index, backend, host_id)

    monkeypatch.setattr(jax, "devices", devices)
    monkeypatch.setattr(jax, "local_devices", local_devices)
