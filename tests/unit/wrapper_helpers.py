"""Shared helper for the wrapper tests (WU-0012): a synthetic repository root with fake tools.

The wrappers ``tools/run_tests.sh`` and ``tools/run_preset.sh`` are copied into a root built in
``tmp_path`` together with the seed registry, so the real ``runs/`` and the real GPU lock are never
touched. Fakes stand in for the programs the wrappers start:

* ``fakepy`` (used through ``LPC_PYTHON``) records its argv and environment as one JSON line in
  ``$FAKE_DIR/python.jsonl``; answers ``--help`` with or without ``--seed-id`` (``FAKE_HELP_SEED``);
  for ``-m lpcstudy`` it writes ``<out>/<preset>/results.json``, waits for the sentinel file
  ``$FAKE_DIR/go`` (only if ``FAKE_WAIT=1``, capped at 10 s) and exits ``$FAKE_EXIT`` (default 0).
* ``tools/gpu_hours.py`` in the root is a fake that records its argv in ``$FAKE_DIR/tally.jsonl``
  and exits ``$FAKE_TALLY_EXIT`` (default 0), unless ``real_tally=True`` copies the real tool.
* ``bin/timeout`` records its argv in ``$FAKE_DIR/timeout.log`` and runs the command that follows
  the duration.
"""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TOOLS = ("run_tests.sh", "run_preset.sh", "gpu_hours.py")
TIERS = ("unit", "integration", "slow", "gpu")

FAKE_PYTHON = f"""#!{sys.executable}
import json, os, sys, time
from pathlib import Path

fake_dir = Path(os.environ["FAKE_DIR"])
argv = sys.argv[1:]
with open(fake_dir / "python.jsonl", "a") as handle:
    handle.write(json.dumps({{"argv": argv, "env": dict(os.environ), "pid": os.getpid()}}) + "\\n")
if "--help" in argv:
    print("usage: lpcstudy [--preset P] [--out OUT]"
          + (" [--seed-id SEED_ID]" if os.environ.get("FAKE_HELP_SEED", "1") == "1" else ""))
    sys.exit(int(os.environ.get("FAKE_HELP_EXIT", "0")))
if "lpcstudy" in argv:
    out = Path(argv[argv.index("--out") + 1]) / argv[argv.index("--preset") + 1]
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.json").write_text("{{}}")
    if os.environ.get("FAKE_WAIT") == "1":
        deadline = time.time() + 10
        while not (fake_dir / "go").exists() and time.time() < deadline:
            time.sleep(0.02)
sys.exit(int(os.environ.get("FAKE_EXIT", "0")))
"""

FAKE_TIMEOUT = """#!/usr/bin/env bash
echo "$*" >>"$FAKE_DIR/timeout.log"
while [[ "$1" == --* ]]; do shift; done
shift
exec "$@"
"""

FAKE_TALLY = """import json, os, sys

with open(os.path.join(os.environ["FAKE_DIR"], "tally.jsonl"), "a") as handle:
    handle.write(json.dumps(sys.argv[1:]) + "\\n")
sys.exit(int(os.environ.get("FAKE_TALLY_EXIT", "0")))
"""

FAKE_FLOCK = """#!/usr/bin/env bash
echo "$*" >>"$FAKE_DIR/flock.log"
exit 0
"""


def write_script(path: Path, text: str) -> Path:
    """Write an executable script."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


class FakeRoot:
    """A synthetic repository root with the wrappers, a seed registry and fake programs.

    Parameters
    ----------
    base : Path
        Empty directory (``tmp_path``) that holds ``root/``, ``fake/``, ``bin/`` and ``lock``.
    real_tally : bool
        Keep the real ``tools/gpu_hours.py`` (default: replace it with the recording fake).
    """

    def __init__(self, base: Path, real_tally: bool = False) -> None:
        self.base = base
        self.root = (base / "root").resolve()
        self.fake_dir = base / "fake"
        self.bin = base / "bin"
        self.lock = base / "lock"
        (self.root / "tools").mkdir(parents=True)
        (self.root / "seeds").mkdir()
        self.fake_dir.mkdir()
        for name in TOOLS:
            if (REPO / "tools" / name).is_file():
                shutil.copy2(REPO / "tools" / name, self.root / "tools" / name)
        if not real_tally:
            write_script(self.root / "tools" / "gpu_hours.py", FAKE_TALLY)
        shutil.copy2(REPO / "seeds" / "development_seeds.json", self.root / "seeds")
        for tier in TIERS:
            test_dir = self.root / "tests" / tier
            test_dir.mkdir(parents=True)
            (test_dir / "test_x.py").write_text("")
        self.python = write_script(base / "fakepy", FAKE_PYTHON)
        write_script(self.bin / "timeout", FAKE_TIMEOUT)

    def environment(self, **extra: str) -> dict[str, str]:
        """Return a clean environment: real PATH behind the fakes, no inherited LPC_*/JAX_* values."""
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(("LPC_", "FAKE_", "JAX_", "XLA_", "OMP_", "MKL_", "OPENBLAS_", "PYTEST_"))}
        env.update(PATH=f"{self.bin}:{env['PATH']}", FAKE_DIR=str(self.fake_dir),
                   LPC_PYTHON=str(self.python), LPC_GPU_LOCK=str(self.lock),
                   GIT_CEILING_DIRECTORIES=str(self.base.parent))
        env.update(extra)
        return env

    def run(self, tool: str, *args: str, env: dict[str, str] | None = None,
            timeout: float = 20.0) -> subprocess.CompletedProcess[str]:
        """Run ``<root>/tools/<tool>`` from the root with the clean environment."""
        return subprocess.run([str(self.root / "tools" / tool), *args], cwd=self.root,
                              env=self.environment() if env is None else env,
                              capture_output=True, text=True, timeout=timeout, check=False)

    def calls(self) -> list[dict]:
        """Return the JSON records of the fake python, in order (empty if it never ran)."""
        path = self.fake_dir / "python.jsonl"
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text().splitlines()]

    def tally_calls(self) -> list[list[str]]:
        """Return the argv of each call of the fake ``gpu_hours.py`` (empty if never called)."""
        path = self.fake_dir / "tally.jsonl"
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    def timeout_calls(self) -> list[list[str]]:
        """Return the argv of each fake ``timeout`` call (empty if never called)."""
        path = self.fake_dir / "timeout.log"
        return [line.split() for line in path.read_text().splitlines()] if path.exists() else []
