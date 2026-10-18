# WU-0004d: independent review, round 1

| Field | Value |
| --- | --- |
| Reviewer | `reviewer`, claude-opus-5-5 (fresh context, not the author) |
| Date | 2026-10-18 |
| Branch | `wu/0004d-h3a-events`, tip `3384725` (code and tests `d41fe03`), from develop `dfd656f` |
| Unit | `docs/agent/records/work/WU-0004d-h3a-events.md` |
| Basis | owner ruling B6b (`docs/agent/notes/2026-10-11-amendments-for-owner.md`, line 312); DEF-0018 (`docs/agent/records/defects.md`); DEC-0011 O1 |
| Tests run | none (as instructed). Offline only, on the saved smoke outputs: `tools/compare_runs.py` and `tools/leafdiff.py` (niced, CPU) |
| Verdict | **approve with fixes** (1 medium, 2 low) |
| Owner checkpoint | **needs owner review before freeze**: statistics code (`analysis.h3a_logrank` output), the printed limitation sentence, and the rule table of `tools/compare_pilot.py` |

## What was checked and holds

1. **Verdict path unchanged (read from the diff).** `analysis.py` gains exactly lines 1913-1916 (two list comprehensions) and two dict entries at line 1961. No later line reads `events_per_regime` or `censored_per_regime`. `counts`, `iqr`, `order`, `pairs`, `raw`, `adjusted`, `decided`, `verdict` and `reason` come from the same lines and inputs as at `dfd656f`. Nothing mutates `events` or `first_regime`: boolean masks are copies.
2. **Count correctness.** `events` is the boolean `event` of `oracle.characteristic_horizon` (`a5.events[:, 0]`), so `np.count_nonzero` counts events exactly. Censored is `counts - events` on the same mask `first_regime == k`, so the invariant holds by construction. Edge cases:
   - An empty regime gives 0/0/0.
   - All-censored data gives events 0 and censored equal to `n`.
   - All-events data gives censored 0.
   - A single regime gives one entry each.
   - Ordering: all three lists are indexed by regime index `k = 0..K_real-1`, as `n_per_regime` and `iqr_lt` are. The KM-median ordering only permutes `pairs`, and pairs carry regime indices. So the RESULTS.md column "Regime" (`enumerate` index, report.py line 822) is the index used in `H3a.pairs`. No regime is dropped: an empty regime keeps its slot.
3. **Hand case A1, checked by hand.**
   - Setup: regime 0 has durations 1..100 with one event at t = 37; regime 1 has 1..100 with all events. The medians [30, 10] give argsort [1, 0], so the pairs are [[1, 0]].
   - Counts: [100, 100], events [1, 100], censored [99, 0]. Correct.
   - Log-rank by hand: at every t both groups have 101 - t at risk.
     - With d_t = 1 (2 at t = 37): E_0 is about 50.5 and V is about 25.2 (0.25 per time).
     - Z is about (1 - 50.5)/5.02, which is -9.9, so the two-sided p is of order 1e-23.
     - This is consistent with DEF-0018's 2.5e-23, so the premise `p < 1e-10` holds with a wide margin.
   - The scipy oracle with `rel=1e-10` reuses the tolerance of an existing test, with its stated justification. That is legitimate.
4. **A2 reference** is a pure-Python loop that is independent of the NumPy masking. Its cases cover a forced-empty regime, all-censored, all-events and K = 1. Exact.
5. **Regression guard.** `test_regression_h3a_new_keys_change_no_pre_existing_number` is labelled as a regression guard and not correctness evidence (LPC.PC.21). The 14-key set matches the `dfd656f` docstring and the P1 reference file. I checked the reference's `systems/lorenz63/H3a` keys: exactly those 14.
6. **The edited existing assertion** (`test_h3_regimes_wiring_keys_and_arguments`) is still a set equality with two keys added. Nothing is loosened, and no tolerance changed anywhere in the diff.
7. **Test-before-code.** The developer's statement that the tests were never seen red is honest, and it is acceptable here: the new tests cannot pass vacuously.
   - The A1, A2, A3 and report tests index the new keys or the new heading. Without the code they raise `KeyError` or fail `lines.index`.
   - The compare_pilot test needs the new rule; without it `matches` returns 0 rules.
   - The one exception is `test_wu0004d_h3a_count_lists_need_no_tag_...` in `test_tools_compare_runs.py`. It pins behaviour that existed before this unit, so it would have passed before the change. It is a characterization, and is acceptable as such. It is not evidence for the change.
8. **Smoke neutrality (A6), re-derived by me from the saved outputs.**
   - Inputs:
     - Base: `/home/brianm/projects/physics/chaos/lpcstudy-wt/develop/runs/wu0004d-base/smoke/results.json`, provenance commit `dfd656f`, dirty False, DEV-0.
     - Candidate: `/home/brianm/projects/physics/chaos/lpcstudy-wt/wu/0004d-h3a-events/runs/wu0004d-smoke/smoke/results.json`, commit `d41fe03`, dirty True, DEV-0, argv `--seed-id DEV-0`.
   - `compare_runs` output:
     - Tier T0. Leaves: REF 4689, NEW 4695, common 4689, equal 4689, different 0, one-sided 6. Untagged 0 on both runs.
     - Exactly 6 FAIL rows, all `only_new` under `systems/lorenz63/H3a/n_{events,censored}_per_regime/[0..2]`, with values 17/16/47 and 0/0/0.
     - `RESULT: FAIL (exit 1)`.
   - `leafdiff` output: A 4794, B 4802, different 0, removed 0, added 8 (the 6 plus two `#len`).
   - `diff` of the two RESULTS.md files: only the provenance rows and the new section.
   - The `verdicts` leaves are among the 4689 equal ones. The 80 test states split as 17 + 16 + 47, which is `n_test`.
   - Exit 1 is the T0 rule for one-sided leaves and is the expected outcome here (see R3 for later comparisons).
   - Caveat: provenance records `dirty: true` without a file list, so "only queue.md was dirty" is the author's statement. `git diff d41fe03 3384725` touches only the unit file and queue.md, which is consistent with that statement. Because every pre-existing leaf is bitwise equal, the result does not depend on the caveat.
9. **Silent handling (PRIME.4).** The new code has no clip, fallback or swallowed exception. `ValueError` on inconsistent counts is loud and correct, because a corrupt result is not printed. The production invariant holds by construction, so the raise cannot trigger on results from this code. The `handling` walker does not pick up the new keys: leafdiff shows only the 8 H3a leaves added.
10. **Section placement.** The developer moved the section to after the Allocation rules instead of editing `test_budget` L1. That is the right call: L1 enforces a structural property of the report, and the developer's own `###` heading broke it. The deviation from the plan's "right after the hypothesis table" is recorded in the Log.
11. **Exposure sentence.** It is accurate and does not overclaim:
   - It does not quote 2.5e-23.
   - It says "can give", not "gives".
   - It cites DEC-0011 O1 and the 50-state full-sample minimum correctly (`MIN_STATES`).
   - It states that the verdict rule is unchanged.

   See R1 for the one sentence that points at numbers the report does not print.
12. **Scope.** Everything changed is within the plan: two additive keys, the report section, the compare_pilot `new` rule, and tests. There is no verdict, threshold, minimum or ordering change. `budget.py` and `RESULT_COUNT_KEYS` are untouched, as the plan says.
13. **Governance.**
    - Seeds: DEV-0 only, with no confirmatory or sealed flag.
    - History: two linear commits on `dfd656f` (ancestor check OK), with no amend or rebase.
    - Append-only records: `queue.md` gains one appended line, and the unit file is new.
    - Commit messages name WU-0004d and carry `Co-Authored-By: Claude Sonnet 5.5` and `Agent: claude-sonnet-5-5`.
    - No randomness was added to `lpcstudy/` (the test uses `np.random.default_rng(7)` for synthetic labels, as test fixtures do). Values are ints and float64 is untouched.

## Findings

**R1 (medium; report accuracy; plan requirement "beside the p-values").** File `lpcstudy/report.py`, line 771 (`H3A_EXPOSURE`: "Read each p-value beside the events and censored counts above"), together with the docstring at `lpcstudy/analysis.py` line 1900 ("reported beside the p-values").

- The problem: RESULTS.md does not print the per-pair p-values or the pairs. The H3a verdict cell (report.py lines 246-249) shows only the largest Holm p. The smoke RESULTS.md has no other H3a p-value (lines 150, 169, 190 and 213-221).
- Why it matters: a reader of RESULTS.md cannot do what the sentence tells them to do. They cannot tell which pair's p rests on a one-event regime. The point of B6b is to make that exposure visible where the verdict is read. In results.json the lists do sit beside `logrank_p_raw` and `logrank_p_holm`, so the docstring is true there; the printed sentence is not true of RESULTS.md.
- Required fix, one of the two:
  - (a) Preferred. Add one line or table per system to the section, listing each tested pair in test order (`pairs`) with its raw p and Holm p (or "not computed" for `None`). The counts of both regimes of each pair can then be read beside its p. Pin it with a hand-typed test row.
  - (b) Reword the sentence so it names where the per-pair p-values are: `results.json`, `systems/<s>/H3a/pairs`, `logrank_p_raw` and `logrank_p_holm`, with regime indices as in this table. Update the pinned `EXPOSURE_TEXT` in `tests/unit/test_report.py` to the new text, typed by hand.

  Either way, the owner sees the final sentence at the owner-review checkpoint.
- Optional, non-blocking: placing the section directly after the QoI declaration (before `## Allocation rules`) also satisfies L1, because the declaration table's label lines would still precede the next heading. It would put the counts nearer the verdict table.

**R2 (low; PRIME.4 message accuracy).** File `lpcstudy/report.py`, lines 813-815 and 828.

- The problem: a block that has exactly one of the two new keys is reported as "not recorded (results written before WU-0004d)". No results file written before WU-0004d can have one key without the other, so a half-present pair is a corrupt or hand-edited result, not an old one. The output is visible, but it states a false cause.
- Required fix: if exactly one of `n_events_per_regime` and `n_censored_per_regime` is present, raise `ValueError` naming the system, as the inconsistent-counts branch already does. Keep "not recorded" for the case where both are absent. Add a hand case to `test_h3a_section_refuses_inconsistent_counts`.

**R3 (low; record accuracy; routing of a later comparison).** File `docs/agent/records/work/WU-0004d-h3a-events.md`, line 68, item (1), and the Risks bullet at line 38.

- The problem: the note asks to "extend exception (i)" of R-a "before the next pilot comparison". R-a is the P1-against-P0 acceptance criterion of WU-0002.14. It was evaluated and accepted (`WU-0002.14-review-P1.md`, lines 220-223: "ACCEPT P1 as the new v3 DEV-0 reference"; "R-a holds"). It governs no later run.
  - The tool prints R-a only as fixed "NOT checked" text in `--redrawn-states` mode.
  - Editing R-a, in the docstring or in `REDRAWN_NOT_CHECKED`, would rewrite a frozen, already-evaluated criterion. It must stay unedited. The developer was right not to touch it.
- What actually changes for later work: the v3 DEV-0 reference `docs/study/pilot_results_v3_dev0_reference.json` lacks the two lists. I checked this. So any later run compared against it shows 2 x sum(K_real) one-sided leaves.
  - `tools/compare_runs.py` fails them at every tier. At T0 that is a structure FAIL. At T1 to T3 they are only "listed" if `chosen_K` differs (the K-scope); otherwise they are FAIL. Either way the result is exit 1.
  - `tools/compare_pilot.py` classifies them `new` (the rule this unit adds), so there is no exit 2.
  - `tools/leafdiff.py` lists them as added.
  - This appears to be the first post-reference additive leaf. `ci_mc_se`, `n_failed_resamples`, `clip_sensitivity` and `result_counts` are already in the reference.
- Required fix (record only, no code):
  - Append a correction line to the unit Log. It should say that R-a is closed and is not to be amended. It should also say that the plan of the next unit that compares a run against the v3 DEV-0 reference must pre-register these leaves as predicted additions, by path pattern and count 2 x K_real per system, before that run. That means the WU-0016 comparison, the next pilot regeneration, or any rehearsal leg against the reference.
  - Add a queue line or a `/refer` item so that this reaches the planner of that unit.
- Who acts:
  - The planner writes the predicted-addition list into that unit's criteria.
  - If that unit's criterion text is already frozen or owner-approved, adding the exception is a criterion amendment, and the owner must approve it (PRIME.2: a predicted, named exception fixed in advance is not a loosening after the fact).
  - Alternatively, the owner may choose to regenerate the reference. That is an owner decision.
  - Whether `compare_runs` should accept a declared list of expected one-sided leaves is a tool-design question for a separate unit. It is not for this one.

## Views on the developer's questions

- **Should the exposure sentence also appear in budget.py's H3a uncertainty row? Not needed for B6b, and better not in this unit.**
  - That row is the four-element interval label (procedure; level; dependence; multiplicity, NVVUQ.16). The pinned tests fix its format and wording, and WU-0004b is changing `budget.py` in parallel, so there is a conflict risk.
  - The ruling asks for the counts to be reported and the exposure to be stated as a limitation. The RESULTS.md section does that, and the limitations list of the decision drafts already carries B6b (amendments note, line 336).
  - If the owner wants a cross-reference, a short pointer appended to the "dependence" element is the minimal form, for example "few-event regimes: see the H3a events/censored section, DEF-0018". It would go in a follow-up unit with owner sign-off on the text.
- **Should the lists be in `handling.result_counts`? No.**
  - `RESULT_COUNT_KEYS` counts excluded, failed, replaced, dropped or constant cases (DEF-0001).
  - Censored states are not handled cases. They enter the log-rank test as right-censored observations, which is the method working as designed. They are sizes, like `n_per_regime` and `n_states`, which are deliberately left out.
  - Adding them would put routinely nonzero numbers into `handling`. That would mislead the handling sentinels (R-h style "nonzero in P1 and zero in P0" checks) and the `## Handling` section.
- **Other notes:**
  - Integration tier not run: as instructed. The DEV-0 smoke is the end-to-end check, and it passed A6.
  - The smoke has 0 censored states, so the nonzero-censored path is exercised only by A1 and A2. Those tests are adequate.

## Verdict

**approve with fixes.** Findings: 3 (R1 medium; R2 and R3 low). The verdict path, the p-values and every pre-existing leaf are unchanged: I read this from the diff and confirmed it bitwise on the DEV-0 smoke. The counts are correct for every edge case. R1 and R2 are small report fixes, with a radius rerun of `test_report` and its importers once after the fix. R3 is a record correction plus routing. None needs a new A6 neutrality smoke: R1 and R2 change RESULTS.md text only, and option (a) prints numbers that are already in results.json.

Needs owner review before freeze: statistics code (`h3a_logrank` output), the limitation sentence as finally worded, and the `compare_pilot` rule table.

# Round 2 (re-review of fix round 1)

| Field | Value |
| --- | --- |
| Reviewer | `reviewer`, claude-opus-5-5 (fresh context, not the author) |
| Date | 2026-10-18 |
| Scope | R1 to R3 only, fix round 1 = `git diff 0ce6bf2..931df8f` (tip `931df8f`) |
| Tests run | none (as instructed; the developer's radius run 2 gave `1075 passed`). Offline only: `report.h3a_regime_lines` on the saved candidate smoke `runs/wu0004d-smoke/smoke/results.json` (provenance commit `d41fe03`), CPU, niced |
| Verdict | **approve with fixes** (2 new low findings, R4 and R5; R1 to R3 resolved) |
| Owner checkpoint | unchanged: **needs owner review before freeze** (statistics output, the limitation sentence as now worded, the `compare_pilot` rule table) |

## R1 to R3

**R1: resolved.** `lpcstudy/report.py` lines 833-849 add the table "Tested pairs, in test order".

- There is one row per entry of `pairs`, and the events/censored of both regimes of the pair are printed beside it. The raw p and the Holm p are read from `logrank_p_raw` and `logrank_p_holm` as stored and formatted by `_fmt(..., 3)` (`%.3g`). A raw p of `None` prints `not computed`. Nothing is recomputed.
- `h3a_logrank` (`analysis.py` line 1946) never stores a `None` Holm p: a `None` raw p enters the family as 1.0. The single return at line 1959 always carries `pairs`, so the report cannot hit a `KeyError` on results from this code.
- `ValueError` is raised for each of these cases:
  - the pair list and the p lists differ in length;
  - a pair names a regime index outside `0..len(n_per_regime)-1`. This includes a negative index, which matters because Python would otherwise index from the end of the list without any error.
- The exposure sentence now says "Read each p-value of the pair table beside the events and censored counts of its two regimes". That matches what is printed whenever counts exist; for the exception, see R4.
- The pinned strings were checked by hand:
  - The A4 test layout (`head + 7` to `head + 11` for the pair table, `head + 13` for the sentence) matches the paragraph builder at lines 852-854.
  - The row `| lorenz63 | 1, 0 | 100/0 | 1/99 | 0.002 | 0.004 |` is right for pair (1, 0) with events [1, 100] and censored [99, 0].
  - The `not computed` case is right: `_fmt(1.0)` gives "1", and `_fmt(0.0123456)` gives "0.0123".
  - `EXPOSURE_TEXT` is identical to `H3A_EXPOSURE`, typed separately.
- I checked the smoke section offline by running `h3a_regime_lines` on the saved candidate `results.json`:
  - The regime rows are 17/17/0, 16/16/0 and 47/47/0.
  - The pair rows are `| lorenz63 | 0, 1 | 17/0 | 16/0 | 0.644 | 0.958 |` and `| lorenz63 | 1, 2 | 16/0 | 47/0 | 0.479 | 0.958 |`.
  - The stored raw values are 0.64384... and 0.47890..., and the stored Holm values are both 0.95781.... By hand, Holm gives 2 x 0.4789 = 0.9578, then max(0.9578, 1 x 0.6438) = 0.9578.
  - The largest Holm p, 0.958, equals the verdict cell, which reads "largest Holm p 0.958" (RESULTS.md line 150 and `_key_number`).
  - This matches the developer's Log exactly.

**R2: resolved.** Lines 818-824 handle the two lists as follows:

- Exactly one of the two lists present raises `ValueError("<system>: H3a block has only one of ...")`.
- Both absent still prints "not recorded".
- The test covers each list alone, and the message names the system.

**R3: resolved.** The Log correction is appended and no earlier line is edited: the diff removes no line from the unit file or from `queue.md`.

- It states that R-a is closed and not to be amended.
- It names the reference file. I confirmed again that `docs/study/pilot_results_v3_dev0_reference.json` has neither list in any of the three H3a blocks (the key sets are the 14 old keys).
- It gives the path pattern and the count of 2 x K_real per system, and the consequences for `compare_runs`, `compare_pilot` and `leafdiff`. It also says who acts: the planner, or the owner if the criterion is frozen or the reference is regenerated.
- The queue line carries the routing note.
- Non-blocking wording note: the queue line says "compare_runs exit 1 at T0 and at T1 to T3 unless chosen_K differs". Read on its own, that could suggest exit 0 when `chosen_K` differs. In fact the leaves are only "listed" in that case, and the exit is 1 either way (round 1, R3). The unit Log wording ("listed only if `chosen_K` differs") is correct, and the planner reads both. If the developer touches the records again, an appended clarification is enough.

**Neutrality of this round.** The diff touches only:

- `lpcstudy/report.py`: the sentence constant, the docstring, and `h3a_regime_lines`, which reads `results` and builds strings;
- `tests/unit/test_report.py`;
- the unit file and `queue.md`.

`analysis.py`, `pipeline.py`, `tools/` and `save_json` are untouched, and `h3a_regime_lines` mutates nothing. So no `results.json` number can have changed, and no new smoke is needed.

**PRIME.2.** No assertion is loosened:

- The sentence assertion moved from `head + 7` to `head + 13`, and it is still an exact equality.
- The "not recorded" absence check now spans 14 lines instead of 8, which is stricter.
- The verdict-cell assertion is unchanged. The fixture now sets `logrank_p_holm=[0.004]` instead of `[0.004, 0.001]`, so the largest value is the same 0.004.
- `EXPOSURE_TEXT` changed only because R1 required new text, and it was retyped by hand.
- No tolerance changed.

**Commit `931df8f`** names WU-0004d and carries `Co-Authored-By` and `Agent: claude-sonnet-5-5`. It is linear on `0ce6bf2`.

## New findings

**R4 (low; report accuracy, same class as R1).** File `lpcstudy/report.py`, lines 843-854 together with `H3A_EXPOSURE` (lines 771-772).

- The problem: when no shown system has the two lists, `rows` is empty, so neither table is printed. The section then holds only the "not recorded" lines and the sentence "Read each p-value of the pair table beside the events and censored counts of its two regimes", which points at a table and counts that are not there. The test `test_h3a_section_says_not_recorded_for_results_without_the_counts` asserts this output, with the sentence present and no pair table.
- Why it matters: the path is real. `python -m lpcstudy` has a report-only branch (`__main__.py` lines 188-194) that rewrites RESULTS.md from a saved `results.json`. Run on the v3 DEV-0 reference, or on any file written before WU-0004d, it prints this section with all three systems "not recorded". The same flaw existed in round 1 ("counts above" with no counts above); I missed it then. It is in scope now because the fix was to make the sentence match what is printed.
- Required fix, one of the two:
  - (a) When `rows` is empty, print the pair table anyway from the stored `pairs`, `logrank_p_raw` and `logrank_p_holm`, which old files have, with `not recorded` in the two count columns.
  - (b) When `rows` is empty, print a variant sentence without the "Read each p-value of the pair table ..." clause, stating that the counts are not recorded, so the exposure cannot be read from this file.

  In either case, pin the output with a hand-typed expectation in the not-recorded test. The owner sees the final wording at the checkpoint.

**R5 (low; evidence, LPC.PC.21; record accuracy).** File `tests/unit/test_report.py`, lines 1239-1255, against `lpcstudy/report.py` line 835 and the unit Log, fix round 1, R2 bullet.

- The problem: the new guard "a pair names a regime that has no count" (`not 0 <= k < len(states)`) has no test. The R2 test only covers a length mismatch (`logrank_p_holm: []`). The Log nevertheless says "A pair list whose length differs from the p lists, or that names a regime with no count, also raises. Hand cases added."
- Why it matters: the guard is what stops a negative or out-of-range index from silently printing another regime's counts beside a p-value (Python negative indexing). An untested guard is not evidence, and the Log overstates what was tested.
- Required fix:
  - Add hand cases to the R2 test, for example `n_per_regime [100, 100]` with `pairs [[0, 2]]`, and with `pairs [[-1, 0]]`, each expected to raise `ValueError` matching "pairs are inconsistent".
  - Then run the `test_report` radius once.
  - Append to the Log the cases actually added. Do not edit the earlier line.

## Verdict (round 2)

**approve with fixes.** Findings this round: 2 new, both low (R4 and R5). R1, R2 and R3 are resolved.

R4 and R5 are report text and test additions only. They need no smoke and no change to any `results.json` number, and a radius run of `test_report` and its importers once after the fix is enough. This is the last fix round allowed (DEVELOPMENT_WORKFLOW.md §2.3). If R4 or R5 is disputed rather than fixed, the main session refers the unit.

Needs owner review before freeze: unchanged, as listed above.
