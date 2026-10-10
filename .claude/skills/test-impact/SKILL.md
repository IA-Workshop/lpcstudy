---
name: test-impact
description: "Computes the blast-radius test set for the current change (DEVELOPMENT_WORKFLOW.md §4.2) and runs it once with the project's test discipline. Use before EVERY test run instead of running the suite."
argument-hint: "[base branch, default main]"
---

## Change set

!`git diff --name-only main...HEAD 2>/dev/null; git status --porcelain 2>/dev/null || echo "not a git repository"`

## Tool output

!`python3 tools/test_impact.py --base main --explain 2>/dev/null || echo "tools/test_impact.py not available yet (WU-0011): derive the set by hand from DEVELOPMENT_WORKFLOW.md §4.2"`

## Running processes

!`pgrep -fa "lpcstudy --preset" || echo "no preset running"`

## Instructions

1. **Derive the set.** Apply §4.2 to the change set above:
   - own tests plus the tests of direct dependents;
   - for a core module, the tests of all transitive dependents plus integration;
   - nothing for docs, `.claude` or governance;
   - for an unknown mapping, the default rule.

   While `tests/test_core.py` is the only test file, that file is the radius for any `lpcstudy/` change. Add the smoke preset only if `pipeline`, `experiments`, `report` or `__main__` changed.
2. **Log it.** Write the set, the rule used, and the §4.9 checklist answers into the active unit's `## Log`.
3. **Check it hasn't already run.** If this exact set already ran on this exact code, stop: there is no rerun without a change.
4. **Run it once** with `tools/run_tests.sh <tier> <files>`. Until that wrapper exists, use `python -m pytest -q --tb=short -rfE <files>`; the settings environment already sets the CPU device and the thread caps.
5. **Record** the summary line and any failures. On a failure, fix the code, then run `--lf` on the failing test only.

Never run the whole suite here. Gates belong to the main session (§4.3).
