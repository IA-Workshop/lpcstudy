"""Seed refusals of ``python -m lpcstudy`` as a subprocess (WU-0001.3, LPC.PC.7).

Every case runs the real entry point ``main`` in a fresh interpreter with a throwaway
ledger in ``tmp_path`` and synthetic seeds. The real ledger and any real seed never
appear, ``LPC_CONF_*`` are removed from the child environment unless a case sets synthetic
values, and the study is never run (each case is refused before any output).
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TIMEOUT_SECONDS = 120   # one jax import (~3 s) per case on a shared CPU; far below this bound
PREFIX = "lpcstudy: refused (LPC.PC.7):"
SEED = 123456789012345          # synthetic; never a real confirmatory seed
SALT = "0f" * 16
CONFIRMATORY = "--confirmatory"   # only ever with a tmp_path ledger and synthetic values
# The driver pins the repository state to a clean tree at a known commit (WU-0004a): the sealed
# flag is refused on a dirty tree before the commitment is looked at, and these cases test the
# commitment and variable refusals, which must not depend on whether the checkout is clean. The
# tree guard itself is tested in tests/unit/test___main__.py.
DRIVER = ("import sys; from pathlib import Path; from lpcstudy import provenance; "
          "from lpcstudy.__main__ import main; "
          "provenance.git_state = lambda root: ('a' * 40, False, None); "
          "sys.exit(main(sys.argv[2:], ledger_path=Path(sys.argv[1])))")


def write_ledger(path: Path, entries: list[dict]) -> Path:
    """Write a hash-chained ledger (chain computed here with hashlib)."""
    lines, previous = [], "0" * 64
    for number, entry in enumerate(entries, start=1):
        record = {"seq": number, "prev_sha256": previous, "utc": "2026-01-01T00:00:00+00:00",
                  "actor": "test", "role": "test", "authority": "", "summary": "synthetic",
                  "files": {}, **entry}
        line = json.dumps(record, sort_keys=True)
        previous = hashlib.sha256(line.encode()).hexdigest()
        lines.append(line)
    path.write_text("\n".join(lines) + "\n")
    return path


def commitment(seed: int) -> dict:
    """A ``CONF-1`` commitment entry for ``seed`` and the synthetic salt."""
    digest = hashlib.sha256(f"{seed}:{SALT}".encode()).hexdigest()
    return {"type": "commitment", "data": {"seed_id": "CONF-1", "sha256": digest}}


CASES = {
    "unknown-id": (["--seed-id", "DEV-99"], [commitment(SEED)], {}),
    "no-commitment": ([CONFIRMATORY], [{"type": "note", "data": {}}],
                      {"LPC_CONF_SEED": str(SEED), "LPC_CONF_SALT": SALT}),
    "mismatched-commitment": ([CONFIRMATORY], [commitment(SEED + 1)],
                              {"LPC_CONF_SEED": str(SEED), "LPC_CONF_SALT": SALT}),
    "no-variables": ([CONFIRMATORY], [commitment(SEED)], {}),
    "seed-variable-only": ([CONFIRMATORY], [commitment(SEED)], {"LPC_CONF_SEED": str(SEED)}),
    "salt-variable-only": ([CONFIRMATORY], [commitment(SEED)], {"LPC_CONF_SALT": SALT}),
    "raw-seed-flag": (["--seed", "5"], [commitment(SEED)], {}),
    "raw-seed-id": (["--seed-id", "5"], [commitment(SEED)], {}),
}


@pytest.mark.parametrize("case", sorted(CASES))
def test_refusal_exits_64_with_one_line_and_writes_nothing(case: str, tmp_path: Path) -> None:
    """Each refusal exits 64, gives one stderr line and creates no output (WU-0001.3).

    Reference: the refusal contract of the plan. The assertions are exact: return code 64;
    the stderr text is exactly one line and starts with ``lpcstudy: refused (LPC.PC.7):``;
    the out directory does not exist and no ``results.json`` exists under ``tmp_path``.
    The cases are the four refusals (unknown id; no or mismatched commitment; missing
    variables; raw integer seed). No synthetic seed or salt appears on stderr.
    """
    args, entries, extra_env = CASES[case]
    ledger = write_ledger(tmp_path / "ledger.jsonl", entries)
    assert ledger.parent == tmp_path and REPO_ROOT not in ledger.resolve().parents
    out = tmp_path / "out"
    env = {k: v for k, v in os.environ.items() if not k.startswith("LPC_CONF_")}
    env.update({"JAX_PLATFORMS": "cpu", "XLA_PYTHON_CLIENT_PREALLOCATE": "false", **extra_env})
    done = subprocess.run([sys.executable, "-c", DRIVER, str(ledger), *args, "--out", str(out)],
                          cwd=REPO_ROOT, env=env, capture_output=True, timeout=TIMEOUT_SECONDS)
    stderr = done.stderr.decode(errors="replace")
    assert done.returncode == 64, stderr[-500:]
    lines = stderr.splitlines()
    assert len(lines) == 1 and lines[0].startswith(PREFIX), stderr[-500:]
    assert done.stdout == b""
    assert not out.exists() and not list(tmp_path.rglob("results.json"))
    for secret in (str(SEED), str(SEED + 1), SALT):
        assert secret not in stderr
