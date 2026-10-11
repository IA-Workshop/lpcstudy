# Merge gate on `develop`, 2026-10-11, second gate (main session, claude-sonnet-5-5)

Gate: merge (DEVELOPMENT_WORKFLOW.md 4.3), run by the main session with `LPC_GATE=merge`, one call per tier, once.

## Contents under test

`develop` tip `a74d6b0` (merge of WU-0008). Merged since the first gate of today (`f039310`, unit 589, integration 11): WU-0002.9, WU-0002.9b, WU-0002.11 (.11a, .11b), WU-0006 (simulation studies, slow tier), WU-0005.5, WU-0002.12 (the comparison tool and the pilot regression), WU-0001.6 (platform record), WU-0005.4 (LM diagnostics), WU-0008 (uncertainty budget), with their records (DEC-0014 to DEC-0025, DEF-0016 to DEF-0025). Every lane was reviewed independently, its fixes re-reviewed, and each lane ran its own blast-radius set once; WU-0001.6, WU-0005.4 and WU-0008 each ran smoke before/after comparisons (neutral outside their new leaves) and the integration tier on their own branch. This is the first whole-suite run of the combined tree after those merges (the `develop` tree was found red once undetected, DEF-0016).

## Checklist (4.9), answered before the invocation

1. **Change set:** `git diff --name-only main...HEAD` in the `develop` worktree: the lanes above; `git status --porcelain` is empty (checked before the run); no conflict markers in `lpcstudy`, `tests`, `tools`, `docs`.
2. **Radius:** the whole suite of the unit and integration tiers (the merge gate, named role: the main session, allowed by 4.3). The slow tier is not part of the merge gate (it is run by the owner of the statistic; the WU-0006 files and the WU-0008 exact checks were run on their branches).
3. **Already run?** The combined tree `a74d6b0` has never been run as a whole. The lane runs were on lane tips; the first gate covered only `f039310`.
4. **Device:** `JAX_PLATFORMS=cpu` (set by `tools/run_tests.sh`); no GPU tier.
5. **Threads and time:** `LPC_THREADS` at the default 4; timeouts: unit 300 s, integration 900 s (the wrapper's).
6. **Contention:** no `pilot` or `full` run active (`pgrep -fa "lpcstudy --preset"` shows none); no lane agent is running a preset; the mathematician of WU-0002.11e works read-only on another worktree.
7. **Output:** wrapper default (`-q --tb=short -rfE`); only summary lines and failures are recorded.
8. **Command:** `LPC_GATE=merge tools/run_tests.sh unit tests/unit`, then `LPC_GATE=merge tools/run_tests.sh integration tests/integration`.

## Results

(appended below after the runs)

- `LPC_GATE=merge tools/run_tests.sh unit tests/unit`: `902 passed in 88.83s`.
- `LPC_GATE=merge tools/run_tests.sh integration tests/integration`: `11 passed in 205.04s (0:03:25)`.
- No failure, no rerun. The tree was clean for both runs (`git status --porcelain` empty before each).
- **Gate result: pass** for `develop` tip `a74d6b0` (this log commit follows it).

## Items the gate does not settle (owner checkpoints, needs owner review before freeze)

- Verdict and statistics code (WU-0002.4 to .10, WU-0008.2a `endpoint_mc_error`; DEC-0011 to DEC-0014, DEC-0021, DEC-0024 proposed), seed and provenance code (WU-0012.5, WU-0001.6), the LM estimator diagnostics (WU-0005.4; `estimation.py` values bitwise unchanged; handling schema `/2`; DEC-0025 proposed) and the Chua memo row (DEC-0010 proposed).
- The slow tier is not part of this gate (WU-0006 and the WU-0008 exact checks C4/C7/C8 were run on their branches).
- Open, so not "fully green" for `main` (the owner's reservation): DEF-0017 (seed-independent start states; blocks WU-0002.11c), DEF-0018, DEF-0019 confirmation, DEF-0020 (Option C or K), DEF-0025, WU-0002.11c, .11d (owner ruling), .11e (owner decisions OD1 to OD8), the WU-0003 rehearsal, the WU-0004 freeze items, the owner's ledger entries and the confirmation of the proposed DECs. No request for `main` is made.
