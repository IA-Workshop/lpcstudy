"""PreToolUse hook on Bash: enforce the test and compute discipline.

Implements DEVELOPMENT_WORKFLOW.md §4.3 and §4.5 and backs up the deny rules
for the confirmatory path (LPC.PC.7). It blocks, with exit code 2 and a reason:

1. any command that uses the confirmatory path or the seal script;
2. a ``pilot``, ``full`` or ``phasej`` preset run that does not hold the GPU lock (``flock``)
   and is not started through ``tools/run_preset.sh`` (``--report-only`` runs are
   exempt: they recompute nothing);
3. a whole-suite pytest run (no test path, or the bare ``tests`` directory)
   unless the command sets ``LPC_GATE=<gate>``, which only the main session
   uses at a gate of §4.3.

Everything else passes to the normal permission flow (exit 0, no output).
"""
from __future__ import annotations

import json
import re
import shlex
import sys

SEPARATORS = {";", "&&", "||", "|", "&"}
VALUE_OPTIONS = {"-k", "-m", "-c", "-p", "-o", "--rootdir", "--deselect", "--ignore",
                 "--timeout", "--maxfail", "--tb", "-r", "--durations", "--basetemp"}
WHOLE_SUITE_PATHS = {"tests", "tests/", ".", "./"}


def block(reason: str) -> None:
    """Print the reason for Claude and block the tool call."""
    print(reason, file=sys.stderr)
    sys.exit(2)


def heavy_run_unlocked(segment: str) -> bool:
    """Say whether one command segment starts a pilot, full or phasej run without the lock.

    A ``--report-only`` run recomputes nothing (it rewrites the report from a
    stored ``results.json``), so it needs no GPU lock even with ``--preset full``.

    Parameters
    ----------
    segment : str
        One simple command of the shell command line.

    Returns
    -------
    bool
        True when the segment must be blocked.
    """
    if not re.search(r"--preset\s+(pilot|full|phasej)\b", segment):
        return False
    if "--report-only" in segment:
        return False
    return not ("flock" in segment or "run_preset.sh" in segment)


def pytest_targets(tokens: list[str]) -> list[list[str]]:
    """Return the positional arguments of each pytest invocation in a command.

    Parameters
    ----------
    tokens : list[str]
        Shell tokens of the command.

    Returns
    -------
    list[list[str]]
        One list of positional (path) arguments per pytest invocation.
    """
    invocations, index = [], 0
    while index < len(tokens):
        token = tokens[index]
        is_pytest = token.endswith("pytest") or (
            token == "-m" and index + 1 < len(tokens) and tokens[index + 1] == "pytest")
        if not is_pytest:
            index += 1
            continue
        index += 2 if token == "-m" else 1
        positional, skip_next = [], False
        while index < len(tokens) and tokens[index] not in SEPARATORS:
            arg = tokens[index]
            if skip_next:
                skip_next = False
            elif arg in VALUE_OPTIONS:
                skip_next = True
            elif not arg.startswith("-"):
                positional.append(arg)
            index += 1
        invocations.append(positional)
    return invocations


def main() -> None:
    """Read the hook input and apply the three checks."""
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)
    command = payload.get("tool_input", {}).get("command", "") or ""
    if re.search(r"--confirmatory|seal_confirmatory_seed", command):
        block("The confirmatory path and the seal script are owner-only (LPC.PC.7, LPC.AUTH.6).")
    if any(heavy_run_unlocked(segment) for segment in re.split(r"[;&|]+", command)):
        block("pilot/full runs must hold the GPU lock: use tools/run_preset.sh, or until it "
              "exists `flock -n ${LPC_GPU_LOCK:-/tmp/lpcstudy-gpu.lock} env JAX_PLATFORMS=cuda "
              "python -m lpcstudy --preset ...` in the background (DEVELOPMENT_WORKFLOW.md §4.5).")
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        sys.exit(0)
    for targets in pytest_targets(tokens):
        whole_suite = not targets or any(t in WHOLE_SUITE_PATHS for t in targets)
        if whole_suite and "LPC_GATE=" not in command:
            block("Whole-suite test runs are allowed only at a gate (DEVELOPMENT_WORKFLOW.md §4.3), "
                  "by the main session, with LPC_GATE=<gate> set. Compute the blast radius "
                  "(/test-impact, §4.2) and run only those test files.")
    sys.exit(0)


if __name__ == "__main__":
    main()
