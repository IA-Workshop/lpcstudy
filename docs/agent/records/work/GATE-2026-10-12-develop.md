# Merge gate on `develop`, 2026-10-12 (main session, claude-sonnet-5-5)

Gate: merge (DEVELOPMENT_WORKFLOW.md 4.3), run by the main session with `LPC_GATE=merge`, one call per tier, once.

## Contents under test

`develop` tip `1b20db9` (merge of WU-0002.11e). Merged since the second gate of 2026-10-11 (`a74d6b0`: unit 902, integration 11): WU-0006.5 (Option C), WU-0011.5 (test-impact rules, whole-token stale-id test, DEF-0025), WU-0002.11c (orbit guard), WU-0002.11e (clip sensitivity), the WU-0002.14 plan, and records (DEC-0026, DEF-0015, DEF-0016 and DEF-0020/21/25 status lines). Every lane was reviewed independently and each ran its own blast-radius set once. This is the first whole-suite run of the combined tree.

## Checklist (4.9), answered before the invocation

1. **Change set:** `git diff --name-only main...HEAD` in the `develop` worktree: the lanes above; `git status --porcelain` is empty (checked before the run); no conflict markers in `lpcstudy`, `tests`, `tools`, `docs`.
2. **Radius:** the whole suite of the unit and integration tiers (the merge gate; named role: the main session; allowed by 4.3). The slow tier is not part of this gate.
3. **Already run?** No: the combined tree `1b20db9` has never been run as a whole.
4. **Device:** `JAX_PLATFORMS=cpu` (set by `tools/run_tests.sh`); no GPU tier.
5. **Threads and time:** `LPC_THREADS` at the default 4; timeouts: unit 300 s, integration 900 s (the wrapper's).
6. **Contention:** no `pilot` or `full` run active (`pgrep -fa "lpcstudy --preset"` shows none at launch); lane agents (WU-0005.6 developer, WU-0002.14 reviewer) may start single smokes; the integration tier is slower under contention but results do not depend on it.
7. **Output:** wrapper default (`-q --tb=short -rfE`); only summary lines and failures are recorded.
8. **Command:** `LPC_GATE=merge tools/run_tests.sh unit tests/unit`, then `LPC_GATE=merge tools/run_tests.sh integration tests/integration`.

## Results

(appended below after the runs)

- `LPC_GATE=merge tools/run_tests.sh unit tests/unit`: `975 passed in 78.84s`.
- `LPC_GATE=merge tools/run_tests.sh integration tests/integration`: `12 passed in 290.42s (0:04:50)` (a WU-0005.6 smoke from another lane ran during it; no effect on results).
- No failure, no rerun. The tree was clean for both runs.
- **Gate result: pass** for `develop` tip `1b20db9` (this log commit follows it).

## Items the gate does not settle (owner checkpoints, needs owner review before freeze)

As in `GATE-2026-10-11-develop-2.md`, plus: the orbit guard (WU-0002.11c; sets the time unit), the clip-sensitivity flag (WU-0002.11e; D1 layout awaiting the owner), Option C (WU-0006.5), the test-impact rules (WU-0011.5). The slow tier is not part of this gate. Not green for `main`: see DEC-0026's list of open items; no request for `main` is made.
