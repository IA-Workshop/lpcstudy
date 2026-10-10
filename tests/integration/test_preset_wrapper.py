"""The smoke preset through ``tools/run_preset.sh`` equals a direct run (WU-0012.2, criterion (k)).

Reference: a direct invocation of ``python -m lpcstudy --preset smoke`` with the same interpreter,
the same ``LPC_THREADS`` and the same environment, which is independent of the wrapper.
Both runs write into fresh directories under the worktree's ``runs/`` (the wrapper accepts only
out-dirs there, so that the GPU-hour tally sees every run); the test removes them afterwards.

Tolerance: none, floats are compared bitwise. The code, the CPU, the thread count and the seed
are the same (LPC.PC.18), so the two ``results.json`` must be identical except for the keys named
``seconds`` (wall-clock; at the top level, in ``systems.*`` and in ``estimators.*``; DEC-0005
Q1). The WU-0001.4 provenance timestamp, wall-clock and peak-memory fields do not exist yet; when
that unit merges they are added to ``WALL_CLOCK_KEYS`` and this docstring. Comparison is on the
canonical JSON text (sorted keys), so a NaN equals a NaN. The wrapper adds nothing to
``results.json``; it writes ``run.meta.json`` next to it, which is checked separately.

Cost: about 2 x 50 s on a free CPU (the baseline smoke run took 49 s), bounded by the 900 s
tier timeout of DEVELOPMENT_WORKFLOW.md 4.5; each of the two runs has a 400 s limit here.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
WALL_CLOCK_KEYS = frozenset({"seconds"})
RUN_LIMIT_SECONDS = 400


def strip_wall_clock(value: object) -> object:
    """Return ``value`` with every dict key in ``WALL_CLOCK_KEYS`` removed at any depth."""
    if isinstance(value, dict):
        return {k: strip_wall_clock(v) for k, v in value.items() if k not in WALL_CLOCK_KEYS}
    if isinstance(value, list):
        return [strip_wall_clock(v) for v in value]
    return value


def canonical(path: Path) -> str:
    """Canonical text of a results.json without its wall-clock keys."""
    return json.dumps(strip_wall_clock(json.loads(path.read_text())), sort_keys=True)


def test_strip_wall_clock_removes_seconds_at_any_depth() -> None:
    """Reference: a hand-built document with ``seconds`` at three depths and one ``second``."""
    document = {"seconds": 1.5, "a": {"seconds": 2, "b": [{"seconds": 3, "x": 1}], "second": 4}}
    assert strip_wall_clock(document) == {"a": {"b": [{"x": 1}], "second": 4}}


def test_smoke_through_the_wrapper_matches_a_direct_run() -> None:
    """The smoke preset on CPU through the wrapper gives the same results.json as a direct run.

    The wrapper must also return 0 and write a ``run.meta.json`` with exit code 0 and device
    ``cpu``. Seed: DEV-0 (the CLI default, 20261005); if the CLI already has ``--seed-id``, both
    invocations pass ``--seed-id DEV-0``.
    """
    suffix = uuid.uuid4().hex[:8]
    base = REPO / "runs" / f"test-preset-wrapper-{suffix}"
    direct_out, wrapped_out = base / "direct", base / "wrapped"
    env = {k: v for k, v in os.environ.items() if not k.startswith(("LPC_", "JAX_", "XLA_"))}
    env.update(LPC_THREADS="4", OMP_NUM_THREADS="4", MKL_NUM_THREADS="4", OPENBLAS_NUM_THREADS="4",
               JAX_PLATFORMS="cpu", XLA_PYTHON_CLIENT_PREALLOCATE="false",
               LPC_PYTHON=sys.executable)
    try:
        help_text = subprocess.run(
            [sys.executable, "-m", "lpcstudy", "--help"], cwd=REPO, env=env, capture_output=True,
            text=True, timeout=120, check=True).stdout
        seed_args = ["--seed-id", "DEV-0"] if "--seed-id" in help_text else []
        direct = subprocess.run(
            [sys.executable, "-m", "lpcstudy", "--preset", "smoke", "--out", str(direct_out),
             *seed_args], cwd=REPO, env=env, capture_output=True, text=True,
            timeout=RUN_LIMIT_SECONDS, check=False)
        assert direct.returncode == 0, direct.stderr[-2000:]
        wrapped = subprocess.run(
            [str(REPO / "tools" / "run_preset.sh"), "smoke", "DEV-0", str(wrapped_out)],
            cwd=REPO, env=env, capture_output=True, text=True, timeout=RUN_LIMIT_SECONDS,
            check=False)
        assert wrapped.returncode == 0, (wrapped.stdout[-1000:], wrapped.stderr[-2000:])
        direct_text = canonical(direct_out / "smoke" / "results.json")
        wrapped_text = canonical(wrapped_out / "smoke" / "results.json")
        assert wrapped_text == direct_text
        meta = json.loads((wrapped_out / "smoke" / "run.meta.json").read_text())
        assert meta["exit_code"] == 0 and meta["device"] == "cpu" and meta["preset"] == "smoke"
        assert meta["seed_id"] == "DEV-0" and meta["end_utc"] is not None
    finally:
        shutil.rmtree(base, ignore_errors=True)
