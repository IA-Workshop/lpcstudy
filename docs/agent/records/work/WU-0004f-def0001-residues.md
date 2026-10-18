# WU-0004f: Close the code residues of DEF-0001 (a), (c)

| Field | Value |
| --- | --- |
| Status | implemented, awaiting independent review (not merged) |
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

**Smoke (V1, V3), checklist.** (1) Change set: committed at dbce486, tree clean, `runs/` ignored by git. (2) Radius: the CPU smoke by hand replaces the integration tier (§4.2). (3) Not run before on this code. (4) `--device cpu`. (5) `LPC_THREADS` 4, 56 s wall. (6) No `lpcstudy --preset` process was running; no lock needed on CPU. (7) Only the summary lines were read. (8) `LPC_PYTHON=.../lpcstudy/.venv/bin/python tools/run_preset.sh smoke DEV-0 runs/wu0004f-smoke --device cpu` (exit 0; `run.meta.json`: wall_seconds 56, exit_code 0, seed_id DEV-0, lpc_threads 4).

**V1, numbers unchanged.** Baseline: the develop smoke `runs/gate-smoke/smoke` in the develop worktree, provenance commit ff26883 (the merge-gate run of 2026-10-18). Between ff26883 and the branch base c89ebe5 the only changes under `lpcstudy/`, `tools/`, `tests/`, `seeds/` are `seeds/development_seeds.json` (status notes of DEV-1 to DEV-4; DEV-0's value is unchanged) and `tests/unit/test_embedding.py`, so the baseline is the base code. `python3 -I tools/compare_runs.py <baseline> runs/wu0004f-smoke/smoke`:
- tier **T0**; leaves REF 4695, NEW 4702, common 4695, **equal 4695, different 0**, one-sided 7 (all in NEW); untagged float leaves 0 (REF and NEW); 10x rule: 0 leaves in every class.
- The tool exits 1 ("present on both runs (class structure)") because it fails any one-sided leaf; the seven are exactly the planned set: `handling/skipped_variants` (0), `systems/lorenz63/clip_sensitivity/n_caught_exceptions` (0), `.../clip_sensitivity/by_hypothesis/H1b/parts/PLP/n_floored` (0), `.../n_floored_2L` (0), and the three mirrors `systems/lorenz63/handling/result_counts/clip_sensitivity%2F{n_caught_exceptions, by_hypothesis%2FH1b%2Fparts%2FPLP%2Fn_floored, ...%2Fn_floored_2L}` (0). No leaf removed.
- `H1b.PLP.n_floored` of the verdict is 0, equal to the new `n_floored` (A2 at run level). The smoke has one system (`lorenz63`).
- `RESULTS.md`: identical except the provenance table (commit, argv, times, peak RSS) and the new line "Robustness variants not run (`skipped_variants`): 0." in `## Handling`.

**V3, warnings.** The WARNING/ERROR lines of both `run.log` (timestamps and durations stripped, sorted): 8 lines each, identical (`diff` empty). All new counters are 0 at smoke, which writes no line.

**Proposed DEF-0001 status line, for the main session to append to `defects.md` (not appended by me; it is a record owned by the main session).**

> - DEF-0001, status line (2026-10-18, claude-sonnet-5-5, developer, WU-0004f, branch wu/0004f-def0001-residues, <tip>; **not merged, awaiting independent review and the owner's code review**): residues (a) and (c) of the line of 2026-10-18 "fixed in code; open pending confirmation" are closed in code. (a) `clip_sensitivity.h1b_part`: the 1e-12 floor is counted (`n_floored`, `n_floored_2L`, in the H1b part entry, mirrored in `handling.result_counts`; `n_floored` equals `H1b.PLP.n_floored`; docstring proof: `sq_plp_2 >= sq_plp`, so `n_floored_2L <= n_floored`). The three broad `except Exception` clauses (lines 570, 579, 619): 570 and 619 were recorded and logged but not counted; **579 (`_failed`) swallowed its exception with no log and no count**; all three now add to `n_caught_exceptions`, present in every block (0 at smoke), the 579 one is logged. (c) `handling.skipped_variants` (int) is in `results.json` and printed in `## Handling`. Sentinel paths added to the report. Smoke DEV-0 on CPU against the develop smoke (ff26883): tier T0, 4695 common leaves identical, 0 removed, 7 added (all 0), WARNING lines identical. V4 repeated (appended block of `WU-0002.11-counters.md`): no hit outside a row; it is the developer's grep, not the audit. Remaining: (b) DEF-0019 (the owner confirmed it on develop in e52177f, per its commit message: check), (d) `## Audit` of WU-0002.11 and `/audit freeze`, (e) the owner's code review (this unit adds counter and report code: needs owner review before freeze).

**Left for the main session / reviewer.** Independent review (`/independent-review`); the integration test `test_smoke_pipeline.py` was not edited or run (the smoke by hand is the same evidence, §4.2): at the next merge gate it runs on the branch, and an assertion `results["handling"]["skipped_variants"] == 0` and `clip_sensitivity["n_caught_exceptions"] == 0` could be added there. `tools/compare_runs.py` has no flag to accept new one-sided leaves, so a comparison after a counter is added always exits 1 on exactly those leaves (read the list).

## Review

### Round 1 (2026-10-18; reviewer, claude-opus-5-5; fresh context; tip e55732e, base c89ebe5)

Scope: the diff c89ebe5..e55732e, this unit file, the verification note `docs/agent/notes/2026-10-18-def0001-v4-verification.md` (branch wu/def0001-audit-note), and governance. No test and no preset was run. One offline rerun of `python3 -I tools/compare_runs.py <develop>/runs/gate-smoke/smoke runs/wu0004f-smoke/smoke` reproduced the developer's result: `tier: T0`, `leaves: REF 4695, NEW 4702, union 4702, common 4695, equal 4695, different 0, one-sided 7`. The 7 one-sided leaves are all in NEW, all 0, and are exactly the planned set. Exit 1 comes only from the structure rule on those 7 leaves. No pre-existing leaf changed and none was removed.

**What was checked and holds:**
- **(a1) Same expression and inputs.** `h1b_part` computes `(sq_plp < 1e-12)[keep]`, with `keep` built from the same `x_all` and floored `y`. `analysis.h1b_seed_amplifier` (PLP, floor 0.0) computes `((sq - 0.0) < 1e-12)[keep]`. The inputs come from the same arrays: `m_test.sq_plp[:, wcol]`, `est_seed`, `gains[:, ref-1]` and `spec.dim`. So the two counts are equal by construction. Test A2 checks this against production code, including at 0.
- **(a1) The docstring proof.** It is correct. `perturb_moments` (`:146`) adds `3 L^2 q / M`, which is at least 0. Rounding to nearest is monotone, so `sq_plp_2 >= sq_plp` and `n_floored_2L <= n_floored`. In (ii), the bound at `M = 3e14` gives exactly 1e-12, not a value "above" it. The claim still holds because the floor test is a strict `<`.
- **Counts on every return path.** Every return of `h1b_part` carries the counts, and no existing key changed. Test A3 is labelled as a regression guard.
- **(a2) Every broad `except` is now counted.** The three sites are `_guarded` (one per criterion), `clip_sensitivity_block` and `_failed`. The `_failed` site now also calls `LOG.exception`. The `caught` list belongs to the outermost caller, so a later block failure or `_BaselineMismatch` keeps the count from the criteria.
- **(a2) `_BaselineMismatch` is rightly not counted.** It is a designed refusal and carries its own reason.
- **(a2) No swallow is left uncounted.** No other broad `except` exists in the module.
- **(c) `skipped_variants`.** It is an int at run level and is printed next to `failed_variants`. Older results get the line "not recorded".
- **The DEF-0025 test edit.** The replaced key-list assertion is just as exact, and its docstring says why. It is not a loosening (PRIME.2).
- **References and tolerances.** Every new test names an independent reference: a hand loop, production `h1b_seed_amplifier`, hand strings, or the table contract. All checks are exact integers or strings, and no tolerance was touched.
- **`compare_pilot`.** Each new path matches exactly one rule, of class `new`, and the `LOOK_AT` row is added.
- **Randomness.** None is consumed: the counters are integer sums.
- **Records are append-only.** The diff of `docs/` deletes no line.
- **Commits and seeds.** All three commits name the unit and carry `Agent:` and `Co-Authored-By:` trailers. No sealed seed is touched, and neither are `seeds/`, `docs/study/` or `.claude/`.

**Owner checkpoint.** This unit touches counter, report and verdict-adjacent code (`clip_sensitivity.py`, `experiments.py`, `report.py`, `compare_pilot.py`). It **needs owner review before freeze**, as the header already states.

**Findings**

- **R1 (record; must change before the DEF-0001 status line is appended).**
  - **Where:** this file, the proposed DEF-0001 status line (Log, "Remaining: ..."), and the appended inventory block in `WU-0002.11-counters.md`.
  - **What is wrong:** the line says residues (a) and (c) are closed and lists only (b), (d) and (e) as remaining. Observations O-1 and O-2 of the verification note are still open and appear in neither place:
    - **O-1.** The P2 recomputation drops its counts. For example, `h1b_part` (`clip_sensitivity.py:440-447`, the function this unit edited) never reports `boot.n_failed`. `:454` drops `n_constant_states`, and `:458` drops the `n_failed` of `percentile_interval`.
    - **O-2.** The `1e-300` weight floors on the perturbed moments are not counted, and their justification is not written in the code.
  - **Why it matters:** with the line as written, DEF-0001 could be confirmed at freeze while these report-only counts are still silent (PRIME.4, NVVUQ.11).
  - **Judgment:**
    - O-1 must be dispositioned before freeze. Either count failed resamples in the P2 part entries (as `n_failed_resamples`, mirrored), or have the owner record it as **J**. Failed resamples go to the A3 tail, so the interval is conservative, and no verdict depends on it.
    - O-2 needs the one docstring sentence the note proposes. It can be done in the freeze pass.
    - O-3 is resolved by this unit: A5 injects a failure into a single criterion builder, and the new counter is a sentinel in RESULTS.md. Its other part (no WARNING line from `log_flags`) is acceptable because the count, the ERROR traceback and the sentinel row carry it.
  - **Fix:** add "O-1 and O-2 of the 2026-10-18 verification note (open, report-only)" to the "Remaining" of the proposed line. Append a dated row for each to the inventory block, marked **D** with the owner's disposition pending. No code change is required in this unit.
- **R2 (evidence; small).**
  - **Where:** `tests/unit/test_clip_sensitivity.py`, docstring of `test_block_counts_caught_exceptions_a5`, last bullet.
  - **What is wrong:** the docstring says the forced P-c case keeps "the count 1", but the test asserts `forced["n_caught_exceptions"] == 2`. Two builders are patched to raise at that point. Plan A5 states 1.
  - **Why it matters:** the property (the count survives a `_BaselineMismatch`) is tested, and nothing was loosened. But the stated reference disagrees with the assertion (LPC.PC.21).
  - **Fix:** correct the docstring to 2, with the reason (h2d and h3c both raise). Optionally add a note in the Log that A5's "count 1" was tested as 2.

**Notes (no change required).**
- **The radius was not rerun after the test fix.** After the failing A5 assertion was fixed, only `--lf` was run (1 passed), not the radius (§4 says fix, `--lf`, then the radius once). The fix touched one test function and no production code, and the merge gate runs the whole suite, so no rerun is asked for.
- **Scratchpad overwrites are harmless for the evidence.** The developer overwrote `smoke.out`, `cmp.txt` and `radius1.log` in the shared scratchpad. No record cites a scratchpad path as evidence. The summary lines are in this Log, the smoke tree `runs/wu0004f-smoke` persists, and the compare reproduces offline. The only risk is clobbering a file another concurrent agent kept under the same name. Use unit-prefixed names from now on.

**Verdict: approve with fixes** (R1 and R2; 2 findings; both are record or docstring fixes, and no code change is required). **Needs owner review before freeze.**

### 2026-10-18 Fix round 1 (developer, claude-sonnet-5-5) — answers to R1, R2

Review text committed unchanged as 3ab8c73.

**Changes (before any run).** O-1: `clip_sensitivity._counted` adds `n_failed_resamples` (the bootstrap count each P2 recomputation already holds) to the part entries of H1b (`boot.n_failed`), H2a(ii) parts, H2b(i) (`n_failed` of `percentile_interval`, plus `n_constant_states` from `_per_state_spearman_counted`), H2b(ii), H2c (both parts), H2d, H3c. Nothing is recomputed or reordered: the values were already returned and dropped. Additive keys only; `n_failed_resamples` and `n_constant_states` are already in `RESULT_COUNT_KEYS`, so they reach `handling.result_counts` (not sentinels: failed resamples go to the A3 tail by design). O-2: one docstring paragraph in `perturb_moments` (c' - c >= L^2 q / M >= 0 with the CP sentinel at 0, so the 1e-300 floors under P2 bind only where they bind in the original and are counted there by `curvature_floor` and `pooled_curvature_floor`); not counted. R2: docstring of `test_block_counts_caught_exceptions_a5` corrected to 2 with the reason; plan A5 ("count 1") is not edited: the forced P-c case was tested as 2 because `h2d_part` and `h3c_part` are both still patched to raise there (the property under test, that the count survives a `_BaselineMismatch`, is the same). Tests: A3 expected new-key sets updated (exact: the three keys when computed), new test `test_p2_parts_report_the_counts_they_recompute_o1`.

**Test-run checklist (§4.9), unit radius.** (1) Change set: `lpcstudy/clip_sensitivity.py`, `tests/unit/test_clip_sensitivity.py`, this file, `WU-0002.11-counters.md`. (2) Radius: the same 13 files as round 0 (tool set plus `test_tools_compare_runs.py`), the change being in `clip_sensitivity.py` (the reached set is unchanged); not the whole suite, not a gate. (3) Not run on this code. (4) CPU (wrapper). (5) `LPC_THREADS` 4, unit timeout 300 s. (6) No preset or GPU job. (7) `-q --tb=short -rfE`. (8) `LPC_PYTHON=.../lpcstudy/.venv/bin/python tools/run_tests.sh unit <13 files>`.

**Fix-round results.**
- Radius (once, the 13 files, after the changes): `827 passed, 1 warning in 39.25s`. The one warning was the deliberate 0/0 slope of my new O-1 test (`statistics.py:710`); I wrapped it in `pytest.warns(RuntimeWarning, match="invalid value")` and ran that one test id once more: `1 passed in 0.82s` (test-only change; committed with the code as 9a1e960).
- Smoke 2 (checklist: committed tree clean, CPU, `LPC_THREADS` 4, no other preset running, 55 s; `tools/run_preset.sh smoke DEV-0 runs/wu0004f-smoke2 --device cpu`, exit 0) against `develop/runs/gate-smoke/smoke` (ff26883, same base code as before): `tools/compare_runs.py`: **tier T0, REF 4695, NEW 4724, common 4695, equal 4695, different 0, one-sided 29** (all in NEW, none removed), untagged float leaves 0. Exit 1 only from the structure rule on those 29. The WARNING/ERROR lines of the two `run.log` are identical.
- The 29 one-sided leaves: the 7 of round 0 (all 0) plus 22 from O-1, each under `systems/lorenz63/clip_sensitivity/by_hypothesis/<H>/parts/<part>/` or its `handling/result_counts` mirror: `n_failed_resamples` (0) of H1b/PLP, H2a/{zero,one,interior}, H2b/{noise,library_change}, H2c/{A4_minus_A0,A4_minus_A2}, H2d/A4_over_A3, H3c/A5_over_A4 (10 leaves + 10 mirrors) and `n_constant_states` of H2b/noise (**15, not 0**, 1 leaf + 1 mirror). 15 equals `H2b.noise.n_constant_states` of the verdict at smoke (states whose w* is tied at every noise level, the tie convention of the H2b(i) estimand), so P2 does not change it there. The earlier expectation "0 at smoke" held for all but this count.

**Proposed DEF-0001 status line, corrected (replaces the one in the round-0 Log; for the main session to append to `defects.md`).** Same text as before, with the closure of the observations of the verification note added and "Remaining" changed to: (b) DEF-0019 (owner confirmation on develop at e52177f: check), (d) `## Audit` of WU-0002.11 and `/audit freeze`, (e) the owner's code review. Added sentences: "O-1 (the counts the P2 recomputation dropped) is closed in code: every recomputed tier-A part entry carries `n_failed_resamples`, H2b(i) also `n_constant_states`, mirrored in `handling.result_counts` (smoke: all 0 except `n_constant_states` 15, equal to the verdict's). O-2 (the `1e-300` floors on the perturbed moments) is justified in the `perturb_moments` docstring (c' - c >= L^2 q / M >= 0 with the CP sentinel at 0), so the floors bind under P2 only where `curvature_floor` and `pooled_curvature_floor` already count them; not counted separately. O-3 is resolved by WU-0004f A5; O-5 (`dump.py`, a diagnostic artefact outside `results.json`) stays informational. Inventory rows appended to `WU-0002.11-counters.md`."
