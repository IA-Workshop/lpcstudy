"""PreToolUse hook: only the researcher agent may use WebFetch and WebSearch.

Enforces LPC.AUTH.2(b) and LPC.AI.14. Claude Code passes the hook input as
JSON on stdin; ``agent_type`` is present when the call comes from a subagent
(or a session started with ``--agent``). Calls from any other agent, or from
the main session, are blocked with exit code 2 and a reason on stderr.
Allowed calls are appended to ``docs/agent/records/network-log.jsonl``
(GUARD.13, REPRO.11) and then go through the normal permission flow.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
from pathlib import Path

ALLOWED_AGENT = "researcher"


def log_call(payload: dict, project_dir: Path) -> None:
    """Append one record of an allowed web call to the network log.

    Parameters
    ----------
    payload : dict
        Hook input from Claude Code.
    project_dir : Path
        Project root.
    """
    tool_input = payload.get("tool_input", {})
    record = {
        "utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "session_id": payload.get("session_id"),
        "agent_type": payload.get("agent_type"),
        "agent_id": payload.get("agent_id"),
        "tool": payload.get("tool_name"),
        "target": tool_input.get("url") or tool_input.get("query"),
    }
    log_path = project_dir / "docs" / "agent" / "records" / "network-log.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    """Read the hook input, block non-researcher web calls, log allowed ones."""
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(f"web_gate: unreadable hook input ({exc}); blocking web call", file=sys.stderr)
        sys.exit(2)
    agent = payload.get("agent_type")
    if agent != ALLOWED_AGENT:
        who = agent or "main session"
        print(f"Web access is reserved to the 'researcher' agent (LPC.AUTH.2, LPC.AI.14); "
              f"{who} may not use {payload.get('tool_name')}. Ask the main session to "
              f"dispatch the researcher agent, e.g. /verify-citation.", file=sys.stderr)
        sys.exit(2)
    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", payload.get("cwd", ".")))
    log_call(payload, project_dir)
    sys.exit(0)


if __name__ == "__main__":
    main()
