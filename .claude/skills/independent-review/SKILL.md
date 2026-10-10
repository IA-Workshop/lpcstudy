---
name: independent-review
description: "Independent review of the current branch's changes for a unit, run by the reviewer agent in a fresh context (QA.7, LPC.PC.11)."
argument-hint: "[WU-id]"
context: fork
agent: reviewer
background: false
---

Review the change for unit **$ARGUMENTS**.

Unit file:
!`cat docs/agent/records/work/$ARGUMENTS-*.md 2>/dev/null || echo "unit file not found"`

Changed files against main:
!`git diff --stat main...HEAD 2>/dev/null || git diff --stat HEAD`

Diff:
!`git diff main...HEAD 2>/dev/null || git diff HEAD`

Blast radius:
!`python3 tools/test_impact.py --base main --explain 2>/dev/null || echo "derive the radius by hand from DEVELOPMENT_WORKFLOW.md §4.2"`

Follow your reviewer instructions:

1. Run the blast-radius set once and paste the summary line. Never run the whole suite.
2. Check correctness, evidence, silent handling, scope, reproducibility and owner checkpoints.
3. Write `## Review` in the unit file, with findings numbered R1…Rn and a verdict.
4. Return the verdict and the findings to the caller.
5. If this is a re-review, address only the findings marked `fixed` or `disputed`.

Report only findings that affect correctness, the plan or governance.
