# WU-0004f: Close the code residues of DEF-0001 (a), (c)

| Field | Value |
| --- | --- |
| Status | in progress |
| Class | CSQ3 development (DEV-0 only, CPU smoke). **Needs owner review before freeze** (LPC.PC.11): it touches counter and report code of `clip_sensitivity.py`, `experiments.py`, `report.py` (counters and statistics reporting) |
| Agent(s) | claude-sonnet-5-5 (developer), on the request of the main session |
| Estimate | S (three small additive changes, one radius run, one CPU smoke) |

## Plan (written before execution)

Branch `wu/0004f-def0001-residues` from `develop` at c89ebe5. Sources read: DEF-0001 and all its status lines (`defects.md` lines 159, 169, 211, 255, 266 and the freeze-checklist note at 277), the inventory `WU-0002.11-counters.md` (rows, conventions N/C/J/D, the plan's V4 grep), `lpcstudy/clip_sensitivity.py`, `lpcstudy/experiments.py` (`RESULT_COUNT_KEYS`, `collect_result_counts`, `run_handling`, `run_robustness`), `lpcstudy/pipeline.py` (`Study.skipped_variants`, `system_handling`), `lpcstudy/report.py` (`handling_lines`, `SENTINEL_*`), `tools/compare_pilot.py` (rule table, `LOOK_AT`), `tools/compare_runs.py`.

There is no `lpcstudy/handling.py`: the `lpcstudy.handling/2` block is assembled in `pipeline.py` (`Study.system_handling`, `HANDLING_SCHEMA`) and walked in `experiments.py`; RESULTS.md's `## Handling` is `report.handling_lines`.

### Scope

In (the residues (a) and (c) of the DEF-0001 status line of 2026-10-18, line 266):

1. **(a1) The H1b floor in `clip_sensitivity.h1b_part`** (`np.maximum(sq_plp, 1e-12)` and `np.maximum(sq_plp_2, 1e-12)`, lines 408-409). Count it, additively, following row N4 (`analysis.h1b_seed_amplifier`, `n_floored`):
   - `n_floored`: among the regression states of the original (`keep`), those with `sq_plp < 1e-12` (the floor binds). Same inputs and same expression as `H1b.PLP.n_floored`, so the two must be equal.
   - `n_floored_2L`: among the same states, those with `sq_plp_2 < 1e-12`.
   - Both are attached to **every** return of `h1b_part` (computed or `not_computed`), as new keys of the part entry. No existing key changes.
   - **Justification for the docstring (a proof exists).** Under P2, `sq_plp_2 = sq_plp + 3 L^2 q / M` with `q >= 0` an integer (the increment of the module docstring, `perturb_moments`), and a sum of a float and a non-negative float is not below the float (round-to-nearest is monotone), so `sq_plp_2 >= sq_plp` and the floor binding under P2 implies it binds in the original: `n_floored_2L <= n_floored`. A state with `q >= 1` has `sq_plp_2 >= 3 L^2 / M = 300 / M` which exceeds 1e-12 for every `M <= 3e14`, so under P2 the floor can bind only on states with no clipped draw. Where the original floor does not bind, `np.maximum` is the identity on that state (no value changes). That the floor does not bind at all is NOT proved (it is the sentinel `H1b/PLP/n_floored`, "should read 0"); it is counted.
   - Both paths are added to `report.SENTINEL_RESULT_PATHS` (they should read 0 for the same reason as the original) and both keys are made visible through `RESULT_COUNT_KEYS` so they are mirrored in `handling.result_counts` (the walker already copies `n_floored`; `n_floored_2L` is added to the set).
2. **(a2) The three broad `except Exception` clauses of `clip_sensitivity.py`** (lines 570, 579, 619). Evidence at the pre-change commit:
   - **570** (`clip_sensitivity_block`): the block becomes `status = "not_computed"`, `reason = "error: <repr>"`, every part `not_computed`, `LOG.exception`, and `log_flags` writes a `NOT COMPUTED` WARNING. Visible per system, but **not counted** in the block or in `handling`.
   - **619** (`_guarded`, one per criterion): the criterion's parts read `not_computed` with `reason = "error: <repr>"`, `LOG.exception`. Visible per part, **not counted**; `log_flags` writes nothing for a `not_computed` part, so only the traceback in `run.log` carries it.
   - **579** (`_failed`, the listing of the parts of a failed block): the exception is swallowed with **no log line, no count**; the block gets `by_hypothesis = {}` and the reason of the first failure; the second exception (the cause) is lost. This is a silent swallow.
   - Change: a block-level integer `n_caught_exceptions` (present in every `clip_sensitivity` block, 0 when nothing was caught) counting the swallowed exceptions: one per failed criterion (619), one for the block (570), one for a failed listing (579, which also gets a `LOG.exception`). The count is carried through the whole `_block` call so a later `_BaselineMismatch` (a designed refusal that already carries its reason, not counted) does not lose the criteria-level count. Mirrored in `handling.result_counts` (`clip_sensitivity/n_caught_exceptions`) via `RESULT_COUNT_KEYS`, and a sentinel (an exception in a report-only block is a defect).
3. **(c) `Study.skipped_variants`** (DEF-0025 follow-up, `experiments.py:496-499`): `run_handling` returns `skipped_variants` (int, the same unit as `failed_variants`: robustness variants not run, summed over systems) as a new leaf of `results["handling"]`. `report.handling_lines` prints it in `## Handling` next to `failed_variants`; for results without the key it says so on one line, never an exception. The WARNING line in the log stays.
4. **Inventory.** Append a dated block at the end of `WU-0002.11-counters.md` with the new rows (no existing row edited): the three clip-sensitivity sites, `skipped_variants`, and the repeat of the V4 grep over `lpcstudy/` (hits not in the inventory, each classified N, C or J).
5. **Tools.** `tools/compare_pilot.py`: the new leaves fall under the existing rules `systems/*/clip_sensitivity/**` and `handling/**` (class `new`); a test asserts it (exit 2 'no rule' cannot occur). A `LOOK_AT` row "Skipped robustness variants" is added next to "Failed robustness variants" (read-only listing, no criterion).

Out: (b) DEF-0019 owner confirmation; (d) the `## Audit` of WU-0002.11 and `/audit freeze`; (e) the owner's code review. No change to any verdict, interval, statistic, seed or pre-existing result leaf. No randomness is consumed. No GPU, no pilot, no confirmatory seed. `docs/study/`, `seeds/`, `.claude/` untouched. `defects.md` is not edited: a proposed status line is in the Log for the main session.

### Definition of done

1. A1 to A8 pass in one radius run (once).
2. The CPU smoke on DEV-0 compared with the current develop smoke (`runs/gate-smoke/smoke` in the develop worktree) by `tools/compare_runs.py`: tier T0, every common leaf identical (untagged float leaves 0 differing), no leaf removed, new leaves only at the paths listed under "New leaves".
3. The inventory block and the V4 repeat are appended; the Log has the proposed DEF-0001 status line.
4. Committed on the branch with trailers; not merged.

### New leaves (the only ones allowed; all additive)

- `systems.<s>.clip_sensitivity.n_caught_exceptions` (int, in every block, also a failed one).
- `systems.<s>.clip_sensitivity.by_hypothesis.H1b.parts.PLP.n_floored` and `.n_floored_2L` (ints; present whenever the H1b part is built, i.e. except when the criterion's builder raised or H1b is absent).
- `systems.<s>.handling.result_counts["clip_sensitivity/n_caught_exceptions"]`, `["clip_sensitivity/by_hypothesis/H1b/parts/PLP/n_floored"]`, `[".../n_floored_2L"]` (mirrors).
- `handling.skipped_variants` (int, run level).
- Totals in `handling.totals` do not change (the result counts are not summed there).

### Acceptance criteria (fixed now, VV.3; none may be loosened)

All counts are exact integer equality. Values are bitwise. The references are independent of the code under test (an explicit loop over states; the production `analysis.h1b_seed_amplifier` on the same inputs; the pre-change function copied into the test).

| # | Check | Reference | Tolerance |
| --- | --- | --- | --- |
| A1 | `h1b_part` counts: hand arrays with states at `sq_plp` = 0.0, 5e-13, exactly 1e-12, 2.0 and NaN, some with a clipped draw (`q >= 1`) | explicit Python loop: floor binds iff `sq < 1e-12` and the state is in `keep`; 1e-12 itself does not bind; the NaN state is out of `keep` | `n_floored` and `n_floored_2L` equal the loop count; `n_floored_2L <= n_floored`; a floored state with `q >= 1` is not floored under P2 (increment 15 at M = 20) |
| A2 | `n_floored` equals `H1b.PLP.n_floored` | `analysis.h1b_seed_amplifier` on a mini-world cell whose test `sq_plp` has floored states | equality; also with no floored state (both 0) |
| A3 | the values are unchanged | the pre-change `h1b_part` copied into the test (`test_regression_*`: a regression guard, not value evidence) | every pre-existing key of the returned entry bitwise equal, on a computed case and on the `not_computed` cases; value evidence is the smoke comparison |
| A4 | counts survive `not_computed` | a case where the finite regression set changes under P2 and a case with no regression state | counts present, ints, status `not_computed` |
| A5 | `n_caught_exceptions` | the mini-world block (`_world`): no injection gives 0; `_compute` raising gives 1; the "worse" malformed-results case gives 2 and logs a traceback for the listing; one criterion builder raising gives 1 and still computed; two builders raising gives 2; a criterion raising followed by a forced `_BaselineMismatch` (P-c) gives a not-computed block with count 1 | exact; the existing test `test_an_exception_inside_the_block_is_recorded_not_raised` passes unchanged |
| A6 | `skipped_variants` in `run_handling` | hand `Study` with `skipped_variants = {"lorenz63": ["D=3"], "rossler": ["D=2", "D=3"]}` and with `{}` | 3 and 0, type `int`; the other keys and the one WARNING are unchanged; `json.dumps` round-trips. The test `test_run_handling_warns_of_skipped_variants_and_keeps_its_keys_def_0025` asserted the key list without it (DEF-0025 D4, "no schema change"): that assertion is replaced, by this plan, by the key list with `skipped_variants` appended (a plan-listed edit, not a loosening: the set is exact) |
| A7 | report | `handling_lines` on a hand results dict with `skipped_variants` = 3 and without the key | the exact line "Robustness variants not run (`skipped_variants`): 3." and, without the key, one line saying it is not recorded; no exception; the two clip paths and `clip_sensitivity/n_caught_exceptions` are labelled `(sentinel)` when nonzero |
| A8 | result counts and rules | `collect_result_counts` on a hand `clip_sensitivity` block; `RESULT_COUNT_KEYS` contains every key of that block matching the guard regex of WU-0002.11 A13 plus the two new keys; `compare_pilot` table classification of the new leaf paths | exact paths and values; exactly one rule, class `new`, per new path |
| V1 | numbers unchanged | CPU smoke on DEV-0 at the branch tip vs `runs/gate-smoke/smoke` of develop (c89ebe5 or the tip of the develop worktree, its provenance recorded), `tools/compare_runs.py` | tier T0; no leaf removed; new leaves only those listed; no differing common leaf |
| V3 | warnings | smoke `run.log` of both | the same set of WARNING lines except none added (all new counters are 0 at smoke, which writes no line); any difference is mapped to a counter |
| V4 | grep | the inventory pattern over `lpcstudy/` after the change | every hit not in the inventory is classified in the appended block |

### Affected checks (DEVELOPMENT_WORKFLOW §4.2; `python3 tools/test_impact.py --base develop --explain` after the change, plus the hand additions)

Changed: `lpcstudy/clip_sensitivity.py`, `lpcstudy/experiments.py`, `lpcstudy/report.py`, `tools/compare_pilot.py`, and their tests. `clip_sensitivity` is not a core module; `experiments` and `report` are pipeline modules (rule: own and direct dependents' unit tests, plus integration). The integration tier is replaced by the CPU smoke by hand (§4.2: one of the two). Radius written in the Log before the run.

## Log

(entries below, in order)

### 2026-10-18 Developer log (claude-sonnet-5-5)

**Evidence read before coding (line numbers at c89ebe5).**
- `clip_sensitivity.py`: the two floors at 408-409; the broad `except Exception` at 570 (`clip_sensitivity_block`: recorded as `status`/`reason`, `LOG.exception`, `NOT COMPUTED` WARNING in `log_flags`; not counted), 579 (`_failed`: **no log, no count**; the cause is lost) and 619 (`_guarded`: parts `not_computed` with `error: <repr>`, `LOG.exception`; not counted, and `log_flags` writes nothing for a not-computed part).
- `experiments.py:496-499`: `skipped_variants` summed and logged, not returned; `pipeline.py:133-134, 275-280` the dicts and recorders; `report.handling_lines` prints only `failed_variants`.
- Rule table: `systems/*/clip_sensitivity/**` and `handling/**` are class `new`; no new rule is needed (A8 asserts it).
- A failing-first run of three of the new tests (A1, A6, A7) at the unchanged code: 3 failed (KeyError / missing line), the expected reasons.

**Test-run checklist (§4.9) for the first radius run.**
1. Change set: `git diff --name-only develop...HEAD` is empty (nothing committed yet); `git status --porcelain`: `lpcstudy/{clip_sensitivity,experiments,report}.py`, `tools/compare_pilot.py`, `tests/unit/test_{clip_sensitivity,experiments,report,tools_compare_pilot}.py`, this unit file.
2. Radius: `python3 tools/test_impact.py --base develop --explain` gives the unit set `test___main__, test_budget, test_clip_sensitivity, test_data, test_dump, test_experiments, test_identifiers, test_pipeline, test_report, test_rng_hygiene, test_tools_compare_pilot, test_tools_test_impact` plus the integration tier. Hand addition: `test_tools_compare_runs.py` (it imports `compare_pilot`). The integration tier is replaced by the CPU smoke by hand (§4.2: one of the two). Smaller than the whole suite; not at a gate.
3. Already run? No run of this set on this code (the earlier run was three test ids on the code before the change).
4. Device: `JAX_PLATFORMS=cpu` (set by `run_tests.sh`).
5. Threads/time: `LPC_THREADS` 4 (default); unit timeout 300 s.
6. Contention: no preset or GPU job started by me.
7. Output: `-q --tb=short -rfE` (the wrapper), summary and failures only.
8. Command: `LPC_PYTHON=/home/brianm/projects/physics/chaos/lpcstudy/.venv/bin/python tools/run_tests.sh unit <the 13 files>`.

**Radius run (once).** `LPC_PYTHON=.../lpcstudy/.venv/bin/python tools/run_tests.sh unit` on the 13 files of item 2 of the checklist: `1 failed, 825 passed in 38.21s`. The failure was in my new test `test_block_counts_caught_exceptions_a5`, a test-design error, not a code defect: `caplog` still held the records of the earlier injections and `"Traceback"` is counted once per chained exception (7, not 2). I replaced that assertion by an exact one on the records of the single call (exactly two ERROR records, in the order block then listing, each with `exc_info`); the count of `n_caught_exceptions` and every later assertion are as planned (the failure stopped the test at that line, so the later assertions ran for the first time in the `--lf` run). `run_tests.sh unit --lf tests/unit/test_clip_sensitivity.py`: `1 passed, 32 deselected in 0.73s`. No tolerance in any assert grew; no assertion was removed or loosened. One existing assertion was replaced as the plan lists (A6): the key list of `run_handling` in `test_run_handling_warns_of_skipped_variants_and_keeps_its_keys_def_0025` now ends with `skipped_variants` (the list is exact, the docstring says why). Committed as dbce486.

**Self-check of the diff.**
- Grep of the diff for `clip|nan_to_num|isfinite|where(|try:|except`: the sites are the floor of `h1b_part` (counted: `n_floored`, `n_floored_2L`), the three broad `except Exception` (counted: `n_caught_exceptions`; the one of `_failed` is now also logged), `except _BaselineMismatch` (a refusal with a reason, unchanged), and `np.isfinite` of the existing code. No new clip, replacement or fallback was introduced.
- Grep for `default_rng|random\.|PRNGKey` in `lpcstudy/` diff: none; no randomness is consumed (the counters are integer sums).
- No tolerance grew.
