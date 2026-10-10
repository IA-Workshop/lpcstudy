---
name: start-session
description: "Orient at the start of a session. Shows governance adoption status, ledger chain integrity, git state and the work queue, then picks the next unit. Use when a session starts or after /clear."
---

## Current state

Ledger chain:
!`python3 tools/ledger.py verify || echo "LEDGER CHAIN BROKEN: report to the owner and take only free actions"`

Governance adoption:
!`python3 tools/ledger.py status`

Git:
!`git status --short --branch 2>/dev/null || echo "not a git repository: run git init and commit everything first (see .claude/CLAUDE.md)"`

GPU lock and running presets:
!`(flock -n /tmp/lpcstudy-gpu.lock true && echo "GPU lock free") || echo "GPU lock HELD"; pgrep -fa "lpcstudy --preset" || echo "no preset running"`

Work queue:
!`cat docs/agent/records/work/queue.md`

## Instructions

1. **Check governance.** If any governance file is `NOT ADOPTED` or `CHANGED since adoption`, tell the owner in one line. Until it is resolved, take only free actions (LPC.AI.1, LPC.AI.3).
2. **Pick a unit.** Choose by the lanes in `ROADMAP.md` and the status in `queue.md`: the highest unit whose dependencies are done and that needs no owner checkpoint first. Record your model id and the latest adoption ledger sequence number in its unit file.
3. **Report.** Say in at most five lines what you will do next. Then continue with `/work-unit <WU-id>`.
