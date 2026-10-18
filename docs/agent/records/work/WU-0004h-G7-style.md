# WU-0004h-G7: style pass on the run-comparison tools (compare_pilot, compare_runs, rehearsal_common, leafdiff)

| Field | Value |
| --- | --- |
| Status | in progress |
| Class | CSQ3 development |
| Agent(s) | claude-sonnet-5-5 (no ledger entry of its own; owner's order of 2026-10-18) |
| Estimate | one session |

## Plan (written before execution)

- **Scope:** the owner's code-review order of 2026-10-18 applied to group G7: `tools/compare_pilot.py`, `tools/compare_runs.py`, `tools/rehearsal_common.py`, `tools/leafdiff.py`, and their tests `tests/unit/test_tools_compare_pilot.py`, `test_tools_compare_runs.py`, `test_tools_rehearsal_common.py`, `test_tools_leafdiff.py`. The golden fixtures under `tests/unit/fixtures/` are data and are not touched. Out of scope: every other file.
- **Definition of done:** (1) black 26.10.1, 80 columns, idempotent; (2) every module, class, function and test docstring is NumPy style, plain early-undergraduate language, with the reason and the link to the study; (3) American spelling in comments, docstrings and names; (4) dead code, duplicated helpers and forwarding wrappers removed, with grep evidence; (5) no behavior change: no number, no report line, no CLI behavior.
- **Acceptance criteria (fixed now):** the syntax tree (AST, docstrings ignored) of every file equals the base tree, except the changes listed in the Log; the unit tests of the four test files pass with no changed assertion and no changed tolerance; the saved comparisons `WU-0003-9c-compare-R1R3.txt` and `-R5R6.txt` are reproduced byte for byte by `python -I tools/compare_runs.py` on the stored run pairs.
- **Affected checks:** `tools/test_impact.py --base develop --explain` selects exactly `tests/unit/test_tools_compare_pilot.py`, `test_tools_compare_runs.py`, `test_tools_leafdiff.py`, `test_tools_rehearsal_common.py`. The tools are not imported by `lpcstudy`, so the smoke comparison (d) of the common brief is optional; in its place: the unit tests, the AST checks and the saved comparisons.

## 4.9 test-run checklist (before the run)

1. Change set: the eight files above plus this record (`git diff --name-only develop...HEAD`).
2. Radius: the four test files above (unit tier), as computed by `tools/test_impact.py --base develop`. Smaller than the whole suite; no gate.
3. Already run on this code? No.
4. Device: `JAX_PLATFORMS=cpu` (set by `tools/run_tests.sh`).
5. Threads and time: `LPC_THREADS` default 4; unit timeout 300 s.
6. Contention: no pilot or full run is started by this unit.
7. Output: wrapper output; summary line and failures only.
8. Command: `LPC_PYTHON=/home/brianm/projects/physics/chaos/lpcstudy/.venv/bin/python tools/run_tests.sh unit tests/unit/test_tools_compare_pilot.py tests/unit/test_tools_compare_runs.py tests/unit/test_tools_leafdiff.py tests/unit/test_tools_rehearsal_common.py`.

## Log

2026-10-18, branch `wu/style-g7` from `develop` at 6ddf9cb.

Commits: 69abbd9 (the four tools), then the four test files and this record.

### Lines before and after (`wc -l`, base 6ddf9cb)

| File | before | after |
| --- | --- | --- |
| tools/compare_pilot.py | 2361 | 5028 |
| tools/compare_runs.py | 1624 | 2975 |
| tools/rehearsal_common.py | 232 | 327 |
| tools/leafdiff.py | 149 | 281 |
| tests/unit/test_tools_compare_pilot.py | 2123 | 3516 |
| tests/unit/test_tools_compare_runs.py | 2117 | 3610 |
| tests/unit/test_tools_rehearsal_common.py | 331 | 503 |
| tests/unit/test_tools_leafdiff.py | 143 | 240 |
| **Total** | **9080** | **16480** |

The growth is the owner's own rules: black puts one argument per line (the 340-row rule table of `compare_pilot.py` alone grew by about 2000 lines) and every docstring now explains itself.

### Code changes (b), each with its reason; every other line of code is unchanged

AST check: each file is compared with the base file (`git show develop:<path>`) with `ast_compare.py`. For files with a code change below, the base file was first given exactly the same edit by script and then compared ("expected" copy).

- `tools/leafdiff.py`, `tools/rehearsal_common.py`, the four test files: **no code change**; `AST equal (docstrings ignored)` against the base (except renames of tests, below, applied to the base copy first).
- `tools/compare_runs.py`:
  - `RANK` removed (dead: defined once, never read; `grep -rnw RANK` over `*.py *.md *.sh`).
  - `TAG_CHAINS` removed (dead: defined once, never read; the test uses `cp.NETWORK_INDEPENDENT`).
  - `tag_of` and `retag_of` shared a copy of the same lookup. They now call one helper `_one_row(table, path, what)`; the two `ToolError` messages are unchanged ("N override rows match ..." and "N re-tag rows match ...").
  - twelve copies of `row.outcome = "pass" if row.metric <= row.tol else "FAIL"` (nine) or `"FINDING"` (three) replaced by one helper `_pass_or(row, failure)`.
  - `select_tier`: the second assignment of `tier.cpu_device` (same expression on the same facts; the early return above it covers the missing-fact case) removed.
  - `labelled` to `labeled` (docstring); the two comment-trailing remarks on dataclass fields moved into the class docstrings.
- `tools/compare_pilot.py`:
  - `RULES` removed (used only to build `TABLE`; `grep -rnw RULES` finds nothing else in code or tests): `TABLE = Table(_build_rules())`.
  - `DReport.passed` removed (no caller anywhere: `grep -rn "\.passed"` finds only `NReport.passed`, which tests use, and no test or tool calls it on a `DReport`).
  - three bare string statements after assignments (`REDRAWN_NOT_CHECKED`, `REDRAWN_D3_ARMS`, `V5_FIXTURE_DEVIATION`: no-op expressions used as "attribute docstrings") turned into comments.
  - a `SyntaxWarning` (invalid escape `\*` in a docstring) removed by writing it `\\*`.
  - the four files compile with `-W error::SyntaxWarning`.
- Long string literals were split into adjacent literals (same value) so that no line exceeds 80 columns; `ast.dump` is equal, which is how this was proved. A few lone strings were wrapped in parentheses (`x = ("a" "b")`) for the same reason; also equal.

### Tests renamed (to keep `def` lines within 80 columns); none removed, none loosened

Renamed (same body, same assertions, same tolerances). Only append-only records mention the old names.

- compare_runs (27): `test_missing_provenance_fact_is_undetermined_only_when_it_decides_t0_against_t1` -> `test_missing_provenance_fact_matters_only_for_t0_against_t1`; `test_t0_same_non_cpu_device_measures_float_differences_and_keeps_the_rest_exact` -> `test_t0_same_gpu_measures_float_differences_keeps_rest_exact`; `test_class_b_to_g_exceedance_is_a_finding_and_a_or_chain_exceedance_a_failure` -> `test_class_b_to_g_exceedance_is_a_finding_others_fail`; `test_class_a_endpoint_uses_the_reference_interval_scale_and_zero_interval_needs_exact_equality` -> `test_class_a_endpoint_uses_interval_scale_zero_interval_exact`; `test_t1_lm_summaries_exact_fraction_iterations_within_one_other_relative_1e_8` -> `test_t1_lm_summaries_follow_their_rules`; `test_t3_keeps_the_t1_lm_rules_for_the_oracle_and_check_kinds_and_the_pooled_summary` -> `test_t3_keeps_t1_lm_rules_for_oracle_check_and_pooled`; `test_lm_checks_that_need_the_dump_are_not_computed_and_exit_2_unless_allowed` -> `test_dump_dependent_lm_checks_are_not_computed_exit_2`; `test_a_clip_count_licenses_its_own_system_only_and_a_total_licenses_nothing` -> `test_a_clip_count_licenses_its_own_system_only`; `test_state_denominator_and_top_level_counts_are_listed_without_a_scope` -> `test_state_denominator_and_top_level_counts_open_no_scope`; `test_a_verdict_difference_is_a_def_in_t1_to_t3_and_only_reported_in_td` -> `test_verdict_difference_is_def_in_t1_to_t3_reported_in_td`; `test_one_sided_leaves_fail_unless_a_count_of_their_block_explains_the_shape` -> `test_one_sided_leaves_fail_unless_a_count_explains_the_shape`; `test_failures_of_the_h1a_ratio_keep_the_cp_rule_and_print_the_of7_pointer_with_an_unchanged_exit` -> `test_h1a_ratio_failures_keep_cp_rule_and_print_of7_pointer`; `test_untagged_census_counts_hand_known_leaves_and_the_report_prints_it` -> `test_untagged_census_counts_hand_known_leaves`; `test_every_difference_is_listed_with_class_rel_tolerance_and_outcome_with_all` -> `test_all_option_lists_every_difference`; `test_regression_every_previously_tagged_leaf_keeps_its_chain_but_the_documented_tightening` -> `test_regression_previously_tagged_leaves_keep_their_chain`; `test_the_nhat_spearman_is_tightened_to_cp_and_meets_the_chain_tolerance` -> `test_nhat_spearman_is_tightened_to_cp`; `test_every_override_matches_a_leaf_of_the_fixtures_and_names_no_index_or_system` -> `test_every_override_matches_a_fixture_leaf_with_wildcards`; `test_every_override_has_a_known_chain_a_reason_that_cites_its_source_and_a_known_tolerance` -> `test_every_override_has_a_known_chain_and_a_cited_reason`; `test_an_untagged_float_leaf_is_not_computable_in_every_tier_even_when_equal` -> `test_untagged_float_leaf_is_not_computable_in_every_tier`; `test_wu0004d_h3a_count_lists_need_no_tag_and_are_one_sided_against_an_older_run` -> `test_wu0004d_h3a_count_lists_need_no_tag_and_are_one_sided`; `test_the_h1a_ratio_is_cp_and_meets_the_strict_chain_tolerance_with_the_of7_pointer` -> `test_h1a_ratio_is_cp_and_meets_strict_tolerance_with_pointer`; `test_the_whole_pilot_schema_runs_through_the_tolerance_rules_with_no_untagged_leaf` -> `test_whole_pilot_schema_runs_with_no_untagged_leaf`; `test_the_report_prints_the_tag_summary_and_the_reason_of_each_override_in_use` -> `test_report_prints_tag_summary_and_override_reasons`; `test_of7_retag_table_is_pinned_to_the_four_named_leaves_and_leaves_the_rest_alone` -> `test_of7_retag_table_is_pinned_to_the_four_named_leaves`; `test_of7_floor_rms_follows_the_tol_other_option_like_every_class_g_leaf` -> `test_of7_floor_rms_follows_tol_other`; `test_of7_effect_on_a_pair_the_four_pass_the_ratio_leaves_still_fail_and_nothing_else_moves` -> `test_of7_effect_the_four_pass_ratio_leaves_still_fail`; `test_td_report_says_which_form_governs_and_prints_the_other_as_information` -> `test_td_report_names_the_governing_form`.
- compare_pilot (5): `test_r10_a_delay_change_between_runs_keeps_the_core_estimators_comparable` -> `test_r10_delay_change_keeps_core_estimators_comparable`; `test_t8_every_interval_leaf_of_the_pilot_has_a_level_and_nothing_else_does` -> `test_t8_every_pilot_interval_leaf_has_a_level_and_only_those`; `test_wu0003_7a_leaves_are_new_and_change_no_other_status_and_the_tool_exits_zero` -> `test_wu0003_7a_leaves_are_new_and_the_tool_exits_zero`; `test_the_eighteen_ci_mc_se_leaves_of_the_pilot_have_exactly_one_new_rule` -> `test_the_eighteen_ci_mc_se_leaves_have_exactly_one_new_rule`; `test_a_tree_with_the_ci_mc_se_leaves_compares_without_an_unclassified_leaf` -> `test_ci_mc_se_leaves_compare_without_an_unclassified_leaf`.
- rehearsal_common (3): `test_attempt_returns_the_value_records_not_computable_and_internal_errors_and_lets_refused_pass` -> `test_attempt_records_failures_and_lets_refused_pass`; `test_run_seed_id_accepts_only_agreeing_development_ids_of_kind_development` -> `test_run_seed_id_accepts_only_agreeing_development_ids`; `test_json_ready_converts_numpy_and_nonfinite_values_so_strict_json_accepts_them` -> `test_json_ready_makes_numpy_and_nonfinite_values_json_safe`.
- Removed tests: none. A module-level bare string (a no-op "docstring" of a constant) in `test_tools_compare_pilot.py` became a comment.

### Flagged runtime strings (British spelling; not changed)

- `tools/compare_runs.py:1984` and `:2005`: `row.note = "OF-1: no licence for 0.1 hw"` (appears in the report text of a differing `nfev`/`status`/`a5_leaf_digest`; not in the stored R1/R3 or R5/R6 outputs; not pinned by a test). "licence" should be "license" in American English. For the main session to decide.

### Verification

- black 26.10.1: `uvx black==26.10.1 <the eight files>` then `--check`: `8 files would be left unchanged`. Lines over 80 columns: 0 (counted with awk).
- Tests, once, after all edits: `LPC_PYTHON=.../.venv/bin/python tools/run_tests.sh unit tests/unit/test_tools_compare_pilot.py tests/unit/test_tools_compare_runs.py tests/unit/test_tools_leafdiff.py tests/unit/test_tools_rehearsal_common.py` -> **`498 passed in 18.26s`**. (For comparison, `449 passed` for the first two files plus the leafdiff and rehearsal tests at the base.) The rehearsal golden outputs (inside `test_tools_rehearsal_common.py`) are byte-identical; no golden was regenerated.
- Saved comparisons, re-run with the final code (`python -I tools/compare_runs.py REF NEW`, CPU, niced; stored run directories exist under `lpcstudy-wt/run/r1-c9bb981/runs/{r1-gpu-dev1/pilot,r5-gpu-dev2/full}` and `lpcstudy-wt/run/r3r6-c9bb981/runs/{r3-cpu-dev1/pilot,r6-cpu-dev2/full}`): R1 against R3 and R5 against R6 are **byte-identical** to `WU-0003-9c-compare-R1R3.txt` and `-R5R6.txt`, exit 0 both.
- Extra equivalence runs, old tool (develop) against the new tool on the same stored runs: `compare_runs` with seven option sets (`--tags --all`, `--show 3`, `--td-only`, `--tol-other 1e-6 --allow-not-computed`, `--tol-other 1` (exit 2), the R1 run against itself) and `--help`: identical stdout and exit codes. `compare_pilot` on four stored `results.json` files against `docs/study/pilot_results_v1.json` with five flag sets each (default, `--no-reference`, `--redrawn-states`, `--redrawn-states --d3-arms half-width`, `--reference`): 20 cases, Markdown report, leaves JSON, stdout, stderr and exit code identical. `leafdiff` on R1 against R3 and `--help`: identical.
- Smoke check (d): not run. These tools are not imported by `lpcstudy`.

## Review

- **Reviewer:** <actor, not the author>
- **Findings and resolution:**

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:
