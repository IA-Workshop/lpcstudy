# Merge gate on `develop`, 2026-10-11 (main session, claude-sonnet-5-5)

Gate: merge (DEVELOPMENT_WORKFLOW.md 4.3), run by the main session with `LPC_GATE=merge`, one call per tier, once.

## Contents under test

`develop` tip `f039310` (merge of WU-0002.7/.8). Merged since the last gate (`main` at `95ef937`): WU-0012.4, WU-0012.5, WU-0002.3, WU-0002.4/.5 (phases 1 and 2), WU-0002.6, WU-0002.7/.8, WU-0002.10, DEF-0010 (`sklearn_seed`), WU-0007.2/.3, with their records. Every lane was reviewed independently and its fixes re-reviewed; each lane ran its own blast-radius set once. This is the first whole-suite run of the combined tree.

## Checklist (4.9), answered before the invocation

1. **Change set:** `git diff --name-only main...HEAD` in the `develop` worktree: the lanes above; `git status --porcelain` is empty (checked before the run).
2. **Radius:** the whole suite of the unit and integration tiers. This is larger than any blast radius because this is the merge gate, the named role is the main session, and the gate is allowed by 4.3.
3. **Already run?** No: the combined tree `f039310` has never been run as a whole. The lane runs were on lane tips (before the later merges).
4. **Device:** `JAX_PLATFORMS=cpu` (set by `tools/run_tests.sh`); no GPU tier.
5. **Threads and time:** `LPC_THREADS` at the default 4 (and `PJRT_NPROC`/`NPROC` 4 from the wrapper); timeouts: unit 300 s, integration 900 s.
6. **Contention:** no `pilot` or `full` run active (`pgrep -fa "lpcstudy --preset"` shows none); no agent is running (all lane agents have reported); the develop worktree has no concurrent writer.
7. **Output:** wrapper default (`-q --tb=short -rfE`); only summary lines and failures are recorded.
8. **Command:** `LPC_GATE=merge tools/run_tests.sh unit tests/unit`, then `LPC_GATE=merge tools/run_tests.sh integration tests/integration`.

## Results

(appended below after the runs)
