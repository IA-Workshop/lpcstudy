"""Smoke-preset plumbing check of the CLI (WU-0010.3)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TIMEOUT_SECONDS = 300


def test_smoke_preset_writes_outputs_and_gate_flag(tmp_path: Path) -> None:
    """``python -m lpcstudy --preset smoke`` writes the four outputs and a boolean gate flag.

    Reference: the output contract of ``lpcstudy/__main__.py`` (``<out>/smoke/results.json``,
    ``RESULTS.md``, ``run.log``, ``figures/*.png``) and the schema of the baseline
    ``runs/baseline/smoke/results.json`` (``systems.<s>.validation.gate.gate_pass``).
    This is a plumbing check, not correctness evidence: it does not assert that the
    gate passes. Its only bound is the 300 s timeout of the DEVELOPMENT_WORKFLOW.md
    section 4.1 budget (the baseline took 49 s). No seed argument is passed, so the run
    uses the default 20261005 (DEV-0).
    """
    env = {**os.environ, "JAX_PLATFORMS": "cpu", "XLA_PYTHON_CLIENT_PREALLOCATE": "false"}
    done = subprocess.run(
        [sys.executable, "-m", "lpcstudy", "--preset", "smoke", "--out", str(tmp_path)],
        cwd=REPO_ROOT, env=env, capture_output=True, timeout=TIMEOUT_SECONDS)
    stderr_tail = "\n".join(done.stderr.decode(errors="replace").splitlines()[-20:])
    assert done.returncode == 0, f"smoke preset exited {done.returncode}; stderr tail:\n{stderr_tail}"
    out_dir = tmp_path / "smoke"
    for name in ("results.json", "RESULTS.md", "run.log"):
        assert (out_dir / name).is_file(), f"{name} missing; stderr tail:\n{stderr_tail}"
    assert (out_dir / "figures").is_dir()
    assert list((out_dir / "figures").glob("*.png")), "figures/ has no .png file"
    systems = json.loads((out_dir / "results.json").read_text())["systems"]
    assert systems
    for name, result in systems.items():
        assert isinstance(result["validation"]["gate"]["gate_pass"], bool), name
