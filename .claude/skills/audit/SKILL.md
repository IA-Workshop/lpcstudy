---
name: audit
description: "Adversarial audit by the critical-elite-auditor agent of a scope you name (a unit, the freeze package, a results file, or the whole repository)."
argument-hint: "[scope]"
context: fork
agent: critical-elite-auditor
disable-model-invocation: true
background: false
---

Audit the following scope: **$ARGUMENTS**.

Repository state:
!`git log --oneline -15 2>/dev/null || echo "no git history"`

Open defects:
!`grep -n "^\*\*DEF-" docs/agent/records/defects.md || echo "none"`

Governance adoption:
!`python3 tools/ledger.py status`

Follow your auditor instructions:

- Verify by re-running checks and recomputing numbers.
- Rank findings as blocker, major or minor, each with evidence, the provision it violates, and a fix.
- Write `docs/agent/records/audits/<today>-<scope>.md`.
- Return the verdict and the blockers.
