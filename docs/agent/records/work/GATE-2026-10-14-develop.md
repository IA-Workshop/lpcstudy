# Merge gate on `develop`, 2026-10-14 (main session, claude-sonnet-5-5)

Gate: merge (DEVELOPMENT_WORKFLOW.md 4.3), run by the main session with `LPC_GATE=merge`, one call per tier, once.

## Contents under test

`develop` tip `083f594` (merge of WU-0005.6). Merged since the gate of 2026-10-12 (`1b20db9`: unit 975, integration 12): WU-0002.14 (seed-dependent start states, RNG conversions, `tools/leafdiff.py`, `compare_pilot` rules; merge 4aa16a5), WU-0005.6 (LM knob, `tools/lm_doubling.py`; merge 083f594), DEF-0026 and the records. Each lane was reviewed independently; WU-0002.14 ran its own radius, the integration tier (12 passed) and the P0/P1 pilots on its branch; WU-0005.6 ran its radius, the integration pair (10 passed) and smokes on its branch. This is the first whole-suite run of the combined tree and it also carries out R9 of the WU-0005.6 re-review (post-merge radius: `test_tools_lm_doubling`, `test_lm_doubling_probe`, `test___main__`, `test_tools_run_preset`, `test_cli_seeds`, `test_preset_wrapper` are all inside the whole suite).

## Checklist (4.9), answered before the invocation

1. **Change set:** `git diff --name-only main...HEAD` in the `develop` worktree: the lanes above; `git status --porcelain` empty (checked before the run); no conflict markers in `lpcstudy`, `tests`, `tools`, `docs`.
2. **Radius:** the whole suite of the unit and integration tiers (the merge gate; named role: the main session; allowed by 4.3). The slow tier is not part of this gate.
3. **Already run?** No: the combined tree `083f594` has never been run as a whole.
4. **Device:** `JAX_PLATFORMS=cpu` (set by `tools/run_tests.sh`); no GPU tier.
5. **Threads and time:** `LPC_THREADS` at the default 4; timeouts: unit 300 s, integration 900 s (the wrapper's).
6. **Contention:** no `pilot` or `full` run active (`pgrep -fa "lpcstudy --preset"` shows none at launch); no lane agent has a slot.
7. **Output:** wrapper default (`-q --tb=short -rfE`); only summary lines and failures are recorded.
8. **Command:** `LPC_GATE=merge tools/run_tests.sh unit tests/unit`, then `LPC_GATE=merge tools/run_tests.sh integration tests/integration`.

## Results

(appended below after the runs)
