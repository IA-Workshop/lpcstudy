"""Shared pytest rules for the whole test suite: test tiers and the CPU-only guard.

The study's tests are sorted into four folders by cost and by the device they
need: ``tests/unit`` (fast, CPU), ``tests/integration`` (small end-to-end runs,
CPU), ``tests/slow`` (long simulation studies, CPU) and ``tests/gpu`` (graphics
processor, run only under the project lock). This file does two jobs for every
test. First, it marks each test with the tier of the folder it sits in, so the
folder is the only place a tier is decided. Second, it stops any test outside
``tests/gpu`` from asking for a GPU, so a quick check on a shared workstation
can never grab the one GPU that a long study run may be using. The helper
script ``tools/run_tests.sh`` and the tier tests in
``tests/unit/test_conftest_markers.py`` rely on these rules (see
DEVELOPMENT_WORKFLOW.md sections 4.1 and 4.5). Read the two ``pytest`` hooks
at the bottom first; ``tier_of`` is the small helper both of them use.
"""

from __future__ import annotations

from pathlib import Path

import pytest

TIERS = ("unit", "integration", "slow", "gpu")
GPU_BACKENDS = frozenset({"gpu", "cuda", "rocm"})


def tier_of(path: str | Path, tests_root: str | Path) -> str | None:
    """Return the tier of a test file, read from the folder it sits in.

    A "tier" is one of the four test groups in ``TIERS``. The tier is simply
    the first folder name below ``tests/``.

    Parameters
    ----------
    path : str or Path
        Path of the test file.
    tests_root : str or Path
        The ``tests/`` directory.

    Returns
    -------
    str or None
        The first folder name below ``tests_root`` if it is in ``TIERS`` and
        the file lies inside a folder (not directly in ``tests/``); otherwise
        ``None``.
    """
    try:
        parts = (
            Path(path).resolve().relative_to(Path(tests_root).resolve()).parts
        )
    except ValueError:
        return None
    return parts[0] if len(parts) > 1 and parts[0] in TIERS else None


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Mark every test with its tier; refuse tests that are misplaced.

    ``pytest`` calls this hook once, after it has collected all tests. A test
    outside the tier folders, or one that carries a tier marker different from
    its folder's tier (for example ``@pytest.mark.gpu`` under ``tests/unit/``),
    raises a ``UsageError`` and the run stops. The folder is the only source of
    the tier (section 4.1 of DEVELOPMENT_WORKFLOW.md).
    """
    root = Path(__file__).parent
    misplaced, mismatched = [], []
    for item in items:
        tier = tier_of(item.path, root)
        if tier is None:
            misplaced.append(item.nodeid)
            continue
        own = sorted({m.name for m in item.iter_markers()} & set(TIERS))
        if own and own != [tier]:
            mismatched.append(
                f"{item.nodeid} (directory tier '{tier}', markers {own})"
            )
        item.add_marker(getattr(pytest.mark, tier))
    if misplaced:
        raise pytest.UsageError(
            "Tests outside a tier directory (tests/unit, tests/integration, tests/slow, "
            "tests/gpu): place a test by cost and device (.claude/rules/tests.md): "
            + ", ".join(misplaced)
        )
    if mismatched:
        raise pytest.UsageError(
            "Tier marker differs from the directory tier: move the test to the directory of "
            "its tier instead of marking it (.claude/rules/tests.md): "
            + ", ".join(mismatched)
        )


@pytest.fixture(autouse=True)
def _refuse_gpu(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Fail any test outside ``tests/gpu/`` that asks JAX for a GPU device.

    JAX is the numerical library the study uses. This fixture (a setup step
    that pytest runs automatically before each test) wraps ``jax.devices`` and
    ``jax.local_devices`` so that a request for ``"gpu"``, ``"cuda"`` or
    ``"rocm"`` fails with a clear message. The check runs before JAX is called,
    so the GPU driver is never started, and it does not depend on the
    ``JAX_PLATFORMS`` setting. ``Failed`` is a ``BaseException``, so a test's
    own ``except Exception`` cannot swallow it. The tier comes from the
    folder (``tier_of``), not from a marker, so a ``gpu`` marker on a test
    elsewhere does not lift the guard (collection rejects it anyway).

    Limits: this guard is a backstop. The primary control is setting
    ``JAX_PLATFORMS=cpu`` (in the project settings and in
    ``tools/run_tests.sh``). The guard does not catch implicit default-device
    use (JAX array operations when ``JAX_PLATFORMS`` is unset on a GPU
    machine), a name bound at import time before the fixture runs (``from jax
    import devices``), or a backend given as a non-string object (a client
    instance).
    """
    tier = tier_of(request.node.path, Path(__file__).parent)
    if tier == "gpu":
        return
    import jax

    def guard(backend: object) -> None:
        if isinstance(backend, str) and backend.lower() in GPU_BACKENDS:
            pytest.fail(
                f"GPU device requested outside tests/gpu/ (tier '{tier}', "
                f"{request.node.nodeid}): CPU-only tiers never touch the GPU "
                "(DEVELOPMENT_WORKFLOW.md 4.5); move the test to tests/gpu/.",
                pytrace=False,
            )

    real_devices, real_local = jax.devices, jax.local_devices

    def devices(backend: object = None) -> list:
        guard(backend)
        return real_devices(backend)

    def local_devices(
        process_index: object = None,
        backend: object = None,
        host_id: object = None,
    ) -> list:
        guard(backend)
        return real_local(process_index, backend, host_id)

    monkeypatch.setattr(jax, "devices", devices)
    monkeypatch.setattr(jax, "local_devices", local_devices)
