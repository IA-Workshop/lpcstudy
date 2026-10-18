# WU-0004d: H3a events and censored states per regime in results.json and RESULTS.md (DEF-0018)

| Field | Value |
| --- | --- |
| Status | in progress |
| Class | CSQ3 development (DEV-0 only; no confirmatory seed, no sealed flag) |
| Agent(s) | claude-sonnet-5-5 (developer), branch `wu/0004d-h3a-events` from develop `dfd656f` |
| Estimate | small: one function, one report section, one tool rule, tests, two smoke runs (~1 min each, CPU) |

Needs owner review before freeze (statistics code: `h3a_logrank`; the printed limitation sentence).

## Plan (written before execution)

**Source.** Owner ruling B6b (`docs/agent/notes/2026-10-11-amendments-for-owner.md` section 35): DEF-0018 "keep as is; report event counts per regime; state the exposure as a limitation". The gap is noted in section 38 and in the owner packet `docs/agent/notes/2026-10-18-owner-review-packet.md`. DEF-0018 (`docs/agent/records/defects.md`): one event against 99 censored states gives p = 2.5e-23; DEC-0011 O1 waived the per-regime 50-state minimum on purpose. The ruling keeps that. Today `analysis.h3a_logrank` stores the states per regime (`n_per_regime`) but not the events, so a regime with one event and 99 censored states cannot be seen beside the p-value.

**Scope (in).**

1. `lpcstudy/analysis.py::h3a_logrank`: two new additive result keys, `n_events_per_regime` and `n_censored_per_regime`, each a list of K_real ints in regime-index order (the order of `n_per_regime`), counted on the same first-draw states and the same `events` array the log-rank test reads. `events[i]` true is an event (the A5 horizon was realized); false is censored. Invariant: `n_events_per_regime[k] + n_censored_per_regime[k] == n_per_regime[k]`. Nothing else in the function changes: the ordering, the pairs, the raw and Holm p-values, the verdict, the reason and every pre-existing key are computed by the same lines on the same inputs.
2. `lpcstudy/report.py`: a new subsection of `RESULTS.md` right after the hypothesis table (and the clip lines), "H3a: events and censored states per regime", with one row per (system, regime): states, events, censored; then the exposure sentence (small regimes can give extreme log-rank p-values; DEF-0018; the ruling; a limitation; the verdict rule is unchanged). A results file without the new keys (written before this unit) prints "not recorded" for that system, visibly (PRIME.4), instead of failing or omitting the row; a length mismatch between the lists raises.
3. `tools/compare_pilot.py`: one `new` rule for the two new list leaves (without it `compare_pilot` exits 2 with "no rule" on any run that has them: "A leaf that matches no rule is an error"), with a test that each leaf matches exactly one rule of class `new`. `tools/compare_runs.py`: **no TAGS rows**: TAGS tags float leaves only (`untagged_leaves` takes `is_float`), and the new leaves are ints; a test pins that a run carrying the new leaves has no untagged float leaf, and that against an older reference the new leaves are one-sided (at T0 a one-sided leaf is a structure FAIL by the tool's rule; at T1 to T3 it is "listed" only inside a K-scope). Not changed: the DEV-0 comparison in criterion 5 reads exactly that.

**Scope (out).** Any verdict, criterion, p-value, threshold, minimum or ordering of H3a (the ruling says keep as is; if the design needed any of these: STOP and hand back). `budget.py` (the H3a uncertainty row is unchanged; the limitation sentence is printed in RESULTS.md and the hand-back asks whether the owner also wants it in the budget row). `handling.result_counts` (`RESULT_COUNT_KEYS` is for excluded, failed, replaced or dropped cases; `n_per_regime` is not in it; the new keys are sizes of the same kind and are not added). Any docstring of the frozen R-a criterion in `compare_pilot.py` (see Risks).

**Definition of done.** (a) The two keys exist in `h3a_logrank` output with the invariant above and the docstring says what they are. (b) RESULTS.md prints them with the exposure sentence. (c) `compare_pilot` classifies the two new leaves as `new`. (d) Tests (below) pass in the unit radius, run once. (e) A DEV-0 smoke on CPU at the unit tip, compared with a DEV-0 smoke at the develop tip by `tools/compare_runs.py` (tier T0), shows 0 differing leaves, 0 removed leaves and exactly the new leaves added (2 x K per system), the new leaves being the only FAIL rows, and the `verdicts` identical. (f) Unit file Log, queue.md line, commits with trailers.

**Acceptance criteria (fixed now; none may be loosened).**

- **A1 (hand case, one event among 100 censored states).** Regime labels `[0]*100 + [1]*100`, regime 0 durations 1..100 with exactly one event (the state with duration 37), regime 1 durations 1..100 all events. Expected by hand: `n_per_regime == [100, 100]`, `n_events_per_regime == [1, 100]`, `n_censored_per_regime == [99, 0]`. Exact (integers).
- **A2 (reference independent of the code under test).** For a random labelled sample with several regimes (fixed `np.random.default_rng(<int>)`), the counts equal a pure-Python loop over the states (`sum(1 for l, e in zip(labels, flags) if l == k and e)`), and `events + censored == n_per_regime` for every regime; an empty regime gives 0, 0, 0; all-censored data gives events 0 and censored equal to the size. Exact.
- **A3 (no number changes, mutation-style).** On the same inputs, every pre-existing key of the output (`pairs`, `logrank_p_raw`, `logrank_p_holm`, `n_per_regime`, `n_km_not_reached`, `n_empty_regimes`, `n_degenerate_pairs`, `iqr_lt`, `iqr_lt_mean`, `threshold`, `verdict`, `reason`, `pass`, `chosen_K`) is bitwise equal to the value of the reference implementation. The reference is the output frozen by hand in the existing tests plus a new test that runs the case of A1 and checks `logrank_p_raw` against `scipy.stats.logrank` (the existing independent oracle; `rel=1e-10` as in `test_h3a_logrank_...`, the two codes sum in a different order) and that deleting the two new keys leaves exactly the pre-existing key set `{chosen_K, pairs, logrank_p_raw, logrank_p_holm, n_per_regime, n_km_not_reached, n_empty_regimes, n_degenerate_pairs, iqr_lt, iqr_lt_mean, threshold, verdict, reason, pass}`. Existing assertions stay as they are.
- **A4 (report).** For a results tree with H3a counts `n_per_regime [100, 100]`, events `[1, 100]`, censored `[99, 0]`, RESULTS.md contains the heading, a table row with the three numbers per regime, and the exposure sentence (exact text pinned: it contains "DEF-0018", "events", "censored", "extreme" and "limitation"). For a results tree without the new keys it contains "not recorded" for that system and no exception. A list-length mismatch raises `ValueError`.
- **A5 (tool).** `compare_pilot.TABLE.matches` returns exactly one rule, class `new`, for `systems/lorenz63/H3a/n_events_per_regime/[0]` and `.../n_censored_per_regime/[2]`; `compare_runs.untagged_leaves` of a flat run with these leaves is empty (ints are not tagged).
- **A6 (end-to-end neutrality, DEV-0 smoke on CPU).** Baseline = develop tip `dfd656f`, candidate = unit tip, same command, same seed DEV-0, `tools/compare_runs.py <base> <new>` (tier T0 expected: same code path, same host and device): 0 different, 0 removed, added = 2 x (sum of the K of the three systems), every added path under `H3a/n_events_per_regime/` or `H3a/n_censored_per_regime/`; with `tools/leafdiff.py` as a second reader. Any other difference means the change is not neutral and the unit stops.

**Risks and stop conditions.**

- Verdict code beyond additive counts: STOP and hand back (none planned).
- R-a of `compare_pilot` (the frozen P1 criterion: "the leaf set equals P0's plus exactly the 24 start leaves, except the K-shaped H3a lists ...") will count the 2K new H3a leaves of any later pilot run as findings unless the owner extends the exception. This is a text of a frozen criterion; the unit does not edit it. It is reported in the hand-back as a question.
- Old `results.json` files (pilot P0/P1, `docs/study/`) lack the keys: the report prints "not recorded"; `compare_pilot` of a new run against them lists the new leaves as `new` (fine).

**Affected checks (radius, derived by hand from DEVELOPMENT_WORKFLOW.md §4.2).** Changed files: `lpcstudy/analysis.py`, `lpcstudy/report.py`, `tools/compare_pilot.py`, `tests/unit/test_analysis.py`, `tests/unit/test_report.py`, `tests/unit/test_tools_compare_pilot.py`, `tests/unit/test_tools_compare_runs.py`, this file and `queue.md`. Importers of `analysis`: `test_analysis`, `test_experiments` (calls `analysis`?), `test_budget` and `test_report` (call `write_markdown`), `test___main__` (monkeypatches `write_markdown`), `test_clip_sensitivity`, `test_dump`; importers of `tools/compare_pilot`: `test_tools_compare_pilot`, `test_tools_compare_runs` (its Table), others that import it (`test_tools_leafdiff`? to be grepped). The exact list is written in the Log before the run.

## Log

- 2026-10-18, claude-sonnet-5-5 (developer). Branch `wu/0004d-h3a-events` created from develop `dfd656f` (`git worktree add /home/brianm/projects/physics/chaos/lpcstudy-wt/wu/0004d-h3a-events -b wu/0004d-h3a-events develop`). Read: DEF-0018, DEC-0011 O1, `analysis.h3a_logrank` and `h3_regimes`, `report._key_number` (the H3a cell prints K, the largest Holm p, the mean IQR and the verdict; no per-regime count), `budget.py` (the H3a row has no counts), `experiments.RESULT_COUNT_KEYS` (`n_per_regime` is not in it), `compare_runs` (TAGS tags float leaves only: `untagged_leaves` takes `is_float`; a one-sided leaf at T0 is a structure FAIL), `compare_pilot` (a leaf with no rule is exit 2).
- **Leaf names** (new, under `systems/<system>/H3a/`): `n_events_per_regime/[k]` and `n_censored_per_regime/[k]`, ints, one entry per regime (K_real), same order as `n_per_regime`. Pattern: the existing `n_per_regime` list.
- **Baseline smoke** (started before the edits, develop worktree, clean, tip `dfd656f`): `LPC_PYTHON=/home/brianm/projects/physics/chaos/lpcstudy/.venv/bin/python tools/run_preset.sh smoke DEV-0 runs/wu0004d-base --device cpu` in `/home/brianm/projects/physics/chaos/lpcstudy-wt/develop`: exit 0, 61 s, provenance `commit dfd656f..., dirty False`.
- Tests written first (analysis, report, compare_pilot, compare_runs), then the code; the failing-first run was not made (blast-radius rule: one run per code state), so the tests have not been seen red. The existing assertion `set(out["H3a"]) == {...}` of `test_h3_regimes_wiring_keys_and_arguments` is an equality on the key set; it now lists the two new keys (still an equality: nothing loosened).
- Self-check grep of the added lines for `clip|nan_to_num|isfinite|where(|try:|except|default_rng|random.|PRNGKey`: no hit in `lpcstudy/` or `tools/` (no handling site, no randomness).

**§4.9 checklist, run 1 (unit radius, after the implementation, before any commit).**
1. Change set: `lpcstudy/analysis.py`, `lpcstudy/report.py`, `tools/compare_pilot.py`, `tests/unit/test_analysis.py`, `tests/unit/test_report.py`, `tests/unit/test_tools_compare_pilot.py`, `tests/unit/test_tools_compare_runs.py`, this unit file.
2. Radius: `python3 tools/test_impact.py --base develop --explain` gives 16 unit files (`test___main__`, `test_analysis`, `test_budget`, `test_clip_sensitivity`, `test_data`, `test_experiments`, `test_identifiers`, `test_pipeline`, `test_report`, `test_rng_hygiene`, `test_tools_compare_pilot`, `test_tools_compare_runs`, `test_tools_rehearsal_diagnostics`, `test_tools_rehearsal_report`, `test_tools_test_impact`, `test_validation`), by the rules module + direct dependents + source scan; it is smaller than the whole suite. The integration tier (`tests/integration`) is listed by the tool and not run, as instructed (the smoke runs below are the end-to-end check). Slow tests excluded.
3. Already run: no.
4. Device: `run_tests.sh` sets `JAX_PLATFORMS=cpu`.
5. Threads and time: `LPC_THREADS` default 4; unit timeout 300 s.
6. Contention: no `pilot` or `full` run (the baseline smoke has finished).
7. Output: the wrapper's `-q --tb=short -rfE`; summary and failures only.
8. Command: `LPC_PYTHON=/home/brianm/projects/physics/chaos/lpcstudy/.venv/bin/python tools/run_tests.sh unit <the 16 files>` (below).

**Result run 1:** `1 failed, 1072 passed in 66.51s`. The failure: `tests/unit/test_budget.py::test_markdown_labels_every_interval_table_before_the_next_heading` (L1: the interval label lines of the verdict table must come before the next heading; my `###` heading sat between the table and its label lines). My defect, not a test to change: the section moves after the Allocation rules as a `##` section (before Validation gate). Then `--lf` on that test: `1 passed, 35 deselected in 0.79s`. Then the radius once more, same 16 files and command (checklist items 1 to 8 re-answered: change set plus the report.py move; not run on this code; CPU; 4 threads; no preset running): **`1073 passed in 50.54s`**.

## Review

- **Reviewer:** <actor, not the author>
- **Findings and resolution:**

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:
