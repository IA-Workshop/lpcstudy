"""End-to-end check: a failure in the clip-sensitivity block must not cost a run
its results.

The study clips some values to a valid range, and the clip-sensitivity block
asks how much the conclusions depend on that clipping. The block is report-only
(OD6, an owner decision): it never changes a verdict. So if it breaks, the
failure must be recorded and shown, and the run must go on (WU-0002.11e, R3).

The test makes two smoke runs (the small version of the study) on the
development seed DEV-0, each in a fresh Python process. One is normal. In the
other, ``lpcstudy.clip_sensitivity._compute`` is replaced by a function that
raises an error. The second run must exit 0 and leave every leaf outside the
``clip_sensitivity`` subtree and its mirrors bitwise equal to the first run, so
every verdict is intact. (A "leaf" is one value at the end of the nested results
dictionary.) It must also show the failure in four places:

* ``status = not_computed`` with the error text in the block;
* the RESULTS.md table and note;
* a WARNING line in the run log;
* a count: the mirror of ``clip_sensitivity.n_caught_exceptions`` in
  ``handling.result_counts`` is at least 1 in the failed run (0 in the normal
  one).

Since WU-0004f the counters of the clip subtree are mirrored in
``handling.result_counts`` under keys that start with ``clip_sensitivity/``.
They are the subtree's own leaves, so they are dropped from the comparison
together with it (WU-0004g).
"""

from __future__ import annotations

import json
import os
import struct
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TIMEOUT_SECONDS = 300
DRIVER = (
    "import sys\n"
    "import lpcstudy.clip_sensitivity as c\n"
    "if sys.argv[1] == 'fail':\n"
    "    def boom(*args, **kwargs):\n"
    "        raise RuntimeError('injected')\n"
    "    c._compute = boom\n"
    "from lpcstudy.__main__ import main\n"
    "sys.exit(main(['--preset', 'smoke', '--out', sys.argv[2]]))\n"
)


def run_smoke(mode: str, out: Path) -> Path:
    """Run the smoke preset in a fresh process; ``mode`` is ``normal`` or
    ``fail``.

    In ``fail`` mode the clip computation is replaced by one that raises.
    Returns the folder that holds the run's output.
    """
    env = {
        **os.environ,
        "JAX_PLATFORMS": "cpu",
        "XLA_PYTHON_CLIENT_PREALLOCATE": "false",
    }
    done = subprocess.run(
        [sys.executable, "-c", DRIVER, mode, str(out)],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        timeout=TIMEOUT_SECONDS,
    )
    tail = "\n".join(done.stderr.decode(errors="replace").splitlines()[-15:])
    assert (
        done.returncode == 0
    ), f"{mode} smoke exited {done.returncode}:\n{tail}"
    return out / "smoke"


def leaves(node: object, prefix: tuple = ()):
    """Yield ``(path, value)`` for every leaf of a nested results tree.

    Floats are replaced by their IEEE-754 bytes (as hex text), so comparing two
    leaves compares them bit for bit.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            yield from leaves(value, (*prefix, str(key)))
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from leaves(value, (*prefix, f"[{i}]"))
    else:
        yield prefix, (
            struct.pack("<d", node).hex() if isinstance(node, float) else node
        )


def comparable(results: dict) -> dict:
    """Return the leaves that two runs must share exactly.

    Left out: the provenance block (who ran what, where), every timing value,
    the ``clip_sensitivity`` subtrees and their mirrors (the
    ``clip_sensitivity/...`` keys of ``handling.result_counts``).
    """
    return {
        path: value
        for path, value in leaves(results)
        if path[0] != "provenance"
        and path[-1] not in ("seconds", "wall_seconds")
        and not (path[0] == "systems" and path[2:3] == ("clip_sensitivity",))
        and not (
            path[0] == "systems"
            and path[2:4] == ("handling", "result_counts")
            and path[4].startswith("clip_sensitivity/")
        )
    }


def test_a_failure_in_the_clip_block_is_visible_and_costs_no_verdict(
    tmp_path: Path,
) -> None:
    """The smoke run with ``_compute`` raising exits 0, keeps every other leaf
    bitwise, and says so.

    Reference: the normal smoke run in the same test. It is independent of the
    code under test, because the second run differs from it only by the injected
    exception. The comparison is exact (IEEE bytes and strings), so there is no
    tolerance.
    """
    normal = run_smoke("normal", tmp_path / "normal")
    failed = run_smoke("fail", tmp_path / "failed")
    ok = json.loads((normal / "results.json").read_text())
    bad = json.loads((failed / "results.json").read_text())
    assert comparable(ok) == comparable(bad)
    assert ok["verdicts"] == bad["verdicts"] and ok["verdicts"]
    reason = "error: RuntimeError('injected')"
    for name, system in bad["systems"].items():
        block = system["clip_sensitivity"]
        assert (
            block["status"] == "not_computed" and block["reason"] == reason
        ), name
        assert all(
            p["status"] == "not_computed" and p["flag"] is None
            for e in block["by_hypothesis"].values()
            for p in e["parts"].values()
        ), name
        assert (
            ok["systems"][name]["clip_sensitivity"]["status"] == "computed"
        ), name
        # The failure is counted, not only shown.
        mirror = "clip_sensitivity/n_caught_exceptions"
        assert (
            bad["systems"][name]["handling"]["result_counts"][mirror] >= 1
        ), name
        assert (
            ok["systems"][name]["handling"]["result_counts"][mirror] == 0
        ), name
    report = (failed / "RESULTS.md").read_text()
    assert f"clip sensitivity not computed: {reason}." in report
    assert f"not computed ({reason})" in report
    log = (failed / "run.log").read_text()
    assert f"WARNING clip sensitivity lorenz63: NOT COMPUTED: {reason}" in log
    assert "Traceback" in log and "injected" in log
