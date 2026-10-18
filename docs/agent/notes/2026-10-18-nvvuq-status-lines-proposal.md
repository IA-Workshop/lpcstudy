# Proposed status lines for `NVVUQ-instantiation-LPC.md` (WU-0005.6 in the ROADMAP's sense; freeze blocker C6)

Prepared 2026-10-18 by the planner (claude-opus-5-5). This is a read-only analysis of `develop` at e10f65e. I ran no code, tests or presets, used no web access and did not touch any seed. **This is a draft for the owner.** `NVVUQ-instantiation-LPC.md`, the ledger `proposal` entry and the ROADMAP are the owner's to edit (GOV.49, LPC.PC.11). Nothing here is a hypothesis-test result. Every run number cited comes from DEV-0, DEV-1 or DEV-2.

**Two meanings of "WU-0005.6".** In ROADMAP §2, WU-0005.6 is a review plus the proposal of status lines. In the queue and in `WU-0005.6-lm-doubling.md`, the same id names the LM iteration-doubling study, which is done. This note is the planner half of the ROADMAP sub-task. It is not the doubling study (owner item B1). The ROADMAP acceptance also asks for "`## Review` filled": a reviewer pass over WU-0005.1 to .5 as a set is still owed. The per-sub-task reviews cited below do not replace it.

**Method.**
- Each row text is quoted from `docs/agent/governance/NVVUQ-instantiation-LPC.md`, and its criterion from the "gap →" cell and ROADMAP §2.
- Every test node named here was checked to exist with grep on `develop`. Pass counts come from the unit Logs. None was rerun.
- The `runs/` tree is not committed. The durable evidence is the unit Log tables and the committed `WU-0003-*` record files.
- The file's own definition is "met: evidence exists in the code or the pilot". I propose `met` only where the stated criterion is fully supported.

---

## Part 1: the five WU-0005 rows

### W1. NVVUQ.5, "RK4: V6 step halving checks magnitude, not order". Gap: "observed-order test on a linear ODE with an exact solution"

- **ROADMAP criterion (WU-0005.1).** Reference `expm(A t) x0` for a 3×3 A with complex eigenvalues. Steps h, h/2, h/4. Observed order in [3.8, 4.2]. Under 5 s.
- **Tests.**
  - `tests/unit/test_systems.py::test_rk4_observed_order_is_four`. The band is tightened to [3.9, 4.1] (AM, Q1). There is an added vector leading-term check, residual ≤ 0.10.
  - `::test_rk4_observed_order_nonlinear_scalar` (y′ = y², accepted by plan amendment R2).
  - `::test_flow_step_respects_max_dt`.
- **Results (Log of `WU-0005-verification.md`).**
  - `3 passed in 0.69s`.
  - After the docstring-only fixes R1 to R3 (fbe2cc7): `19 passed in 3.04s`.
  - Observed orders 4.042 and 4.024. The nonlinear test gives 3.975 and 3.993.
- **Review.** `WU-0005-verification.md` `## Review` (reviewer claude-opus-5-5, approve with fixes). The reviewer recomputed the orders independently and ran mutation probes: substeps + 1, floor/ceil and a wrong k4 are all caught.
- **Meets the criterion?** Yes, with a tighter band than the ROADMAP's.
- **Residue (outside the criterion).** A linear field tests only the stability polynomial. For y′ = y², f‴ ≡ 0, so the order-4 condition Σbᵢcᵢ³ = 1/4 never enters the error (review R1).
- **Proposed line:** `met: observed order 4.04 and 4.02 (band [3.9, 4.1]) against expm on a non-normal linear ODE, plus a y' = y^2 order check and the max_dt step cap (tests/unit/test_systems.py::test_rk4_observed_order_is_four, ::test_rk4_observed_order_nonlinear_scalar, ::test_flow_step_respects_max_dt; WU-0005.1). Not exercised: the order condition sum b c^3 = 1/4.`

### W2. NVVUQ.5, "Analog search". Gap: "k-d tree against brute-force nearest neighbor"

- **ROADMAP criterion (WU-0005.2).**
  - 10⁴ library vectors in ℝ⁷ and 200 queries.
  - Nearest index identical to an exhaustive argmin.
  - Distance within 10⁻¹² relative.
  - Second-nearest also checked.
- **Test.** `tests/unit/test_ensemble.py::test_kdtree_query_matches_brute_force[1|2|5]`.
  - It checks exact indices, including the +41 position-to-time offset, with `rtol=1e-12, atol=0`.
  - Ten exact copies give 0.0.
  - The tie-free premise is a hard assertion.
- **Results.** `4 passed in 0.84s`, later included in the `19 passed` run. The measured distance difference is 0.0.
- **Review.** `WU-0005-verification.md` `## Review`. The mutants "skip the nearest" and "index + 1" are caught for k = 1, 2 and 5.
- **Meets the criterion?** Yes. The k = 2 case is the second-nearest check. The P2 margin path, which calls `library.tree.query(..., k=2)` directly in `validation.py:432`, is covered separately by `tests/unit/test_validation.py::test_p2_terms_match_brute_force`.
- **Residue.** None against the criterion. The review's thread-use observation (`workers=-1`) is now `workers=worker_count()` in `ensemble.py:223`.
- **Proposed line:** `met: AnalogLibrary.query equals exhaustive search exactly in index and to rtol 1e-12 in distance for k = 1, 2, 5 (tests/unit/test_ensemble.py::test_kdtree_query_matches_brute_force; WU-0005.2); the P2 second-neighbour path: tests/unit/test_validation.py::test_p2_terms_match_brute_force.`

### W3. NVVUQ.5, "Levina–Bickel dimension". Gap: "test on sets of known dimension"

- **ROADMAP criterion (WU-0005.3).**
  - A segment, a square and a cube in ℝ⁷.
  - 2×10⁴ points, k = 20.
  - Within ±10% of m.
  - The applied-mathematician (AM) may tighten the band.
- **Tests.**
  - `tests/unit/test_oracle.py::test_local_dimension_known_sets[1|2|3]`. The AM tightened the band to `abs(mean/m − 1) ≤ 0.03` (Q2). The test asserts `local_dimension.__defaults__ == (20,)`.
  - `::test_local_dimension_median_poisson_value[1|2|3]` (median against the exact Gamma(19) law; plan amendment R2).
- **Results.** `12 passed in 1.03s`. The mean/m − 1 values were −0.0043, −0.0026 and +0.0067. The k − 1 normalization would give +5.1 to +6.3% and would be caught.
- **Review.** `WU-0005-verification.md` `## Review`. The mutants "numerator k − 1", "skip nearest" and "k − 1 neighbours" are caught.
- **Meets the criterion?** Yes, at 3%, which is tighter than the ROADMAP's 10%.
- **Residue (by design).**
  - Queries are interior only, so the truncated-ball bias at the boundary is a property of the estimator and is not tested.
  - H1b aggregates per-state estimates with a median. The test pins only the per-query median law, not the callers' aggregation.
  - The `1e-300` floor is now counted (`oracle.py:80`).
- **Proposed line:** `met: mean estimate within 3% of m = 1, 2, 3 on uniform sets in R^7 at n = 2e4, k = 20 (tests/unit/test_oracle.py::test_local_dimension_known_sets, ::test_local_dimension_median_poisson_value; WU-0005.3). Interior queries only (boundary bias is an estimator property, not tested).`

### W4. NVVUQ.9, "Levenberg–Marquardt iterative error: about 2% of draws land in a wrong basin and are kept by design; the residual is not reported per estimate". Gap: "report the achieved residual and the iteration count"

- **ROADMAP criterion (WU-0005.4).**
  - Residual and accepted-iteration count per estimate.
  - Summary keys in `results.json`: `median_residual`, `p95_residual`, `median_iterations`, `fraction_no_decrease`.
  - Starting from truth, the cost is non-increasing, the residual is ≤ 10⁻¹²·D (tightened by DEC-0025) and the count is exact.
  - Smoke shows the summary per cell.
- **Tests (`tests/unit/test_estimation.py`).**
  - `::test_l1_true_start_no_noise_exact_model`
  - `::test_l2_perturbed_start_cost_matches_independent_recomputation`
  - `::test_l3_nonfinite_target_row_is_counted_per_estimate`
  - `::test_l3_nan_model_counts_every_estimate_in_both_counters`
  - `::test_l4_no_number_changes_bitwise_against_the_pre_change_function`
  - `::test_l5_lm_summary_quantiles_with_infinities`
  - `::test_l5_lm_summary_other_keys_and_empty_and_errors`
  - `::test_late_progress_counts_a_first_accept_from_a_nonfinite_start`
  - `::test_gof_threshold_is_the_chi2_999_quantile_for_any_dof`
  - `::test_lm_summary_threshold_follows_the_degrees_of_freedom`
  - `::test_zero_refine_steps_defines_the_diagnostics`
- **Other tests.**
  - `tests/unit/test_report.py::test_lm_lines_exact_rows_note_and_missing_block`
  - `tests/unit/test_report.py::test_write_markdown_places_the_lm_subsection_after_p2c_and_before_handling`
  - `tests/integration/test_smoke_pipeline.py` (`assert_lm_rows`, schema `/2`)
- **Results (Log of `WU-0005.4-lm-diagnostics.md`).**
  - Run 3: `345 passed`.
  - Run 4, after R7: `92 passed`.
  - Integration: `11 passed in 198.86s`.
  - V1 smoke before/after: exit 0, 4285 leaves identical, 0 changed, 246 new, all under `handling/**/lm`.
  - V2: 6 LM rows.
  - L1 residual maximum: 2.9e-31.
- **Reviews.** `WU-0005.4-lm-diagnostics.md` `## Review`: round 1 (R1 to R6) and re-review (R7). R7 was fixed in 15edf09. The reviewer said no further round was needed once the run was logged, and it is logged.
- **Meets the criterion?** Yes for the criterion as stated: reporting the residual and the iteration count.
- **Residue.**
  - (a) The iterative error of the QoIs is not part of this criterion. DEF-0027 shows it is not negligible. In the DEV-0 doubling study (`docs/study/lm_doubling_dev0_report_v3.md`, reviewed in `WU-0005.6-report-check.md` and `WU-0005.6-rule-r-order-review.md`), the flag "below 10% of half-width" is yes on only 5 of 18 primary parts (classes N 5 / X 6 / U 7).
    - The owner ruled "report and flag only" (amendments note §29). That ruling is not yet a `DEC` entry.
    - The budget prints the LM row as "not estimated" with a development-evidence pointer.
    - O4 and O6 are open.
  - (b) The "about 2% wrong basin" in the row's means cell is unmeasured. `fraction_above_chi2` is a diagnostic that also counts unconverged estimates and model error (O3 and D3 of WU-0005.4).
  - (c) The R2 confirmation that dof = D − m is not recorded as an explicit applied-mathematician line in the unit file. It appears only through the fix-round-2 citation of "the mathematician's notes".
  - (d) The unit header is stale ("awaiting re-review").
- **Proposed line:** `met (reporting): residual, accepted-step count, non-finite counters and late-progress flag per estimate, summarized per cell in handling.cells.*.lm (schema lpcstudy.handling/2) and printed in RESULTS.md (tests/unit/test_estimation.py::test_l1_true_start_no_noise_exact_model and L2-L5; tests/integration/test_smoke_pipeline.py; WU-0005.4). The iterative error of the QoIs is a declared limitation: DEF-0027, flag yes on 5 of 18 primary parts at DEV-0, owner ruling 'report and flag only'; the budget row reads 'not estimated'.`
- **Also proposed:** reword the means cell. Drop "about 2% ... wrong basin" as an unmeasured figure, or label it "v3 §4, not measured".

### W5. NVVUQ.5, "Noise sensitivity N against the Theorem P2 bound, state by state" (and NVVUQ.14, "P2 is checked numerically (WU-0005)")

- **ROADMAP criterion (WU-0005.5).**
  - The AM fixes the exact form (done in .5a: B_M on the same draws, which is deterministic).
  - Unit: on a synthetic library the bound holds for every state, and ‖η‖ < Δ/2 gives N = 0.
  - Slow: on a development cell, the violation fraction is in `results.json` and equals 0.
  - The per-state check is reported for each system's core cell in the rehearsal.
- **Unit tests (`tests/unit/test_validation.py`).**
  - `::test_p2_stable_case_is_exact_on_dyadic_library`
  - `::test_p2_stable_case_generic_coordinates_is_zero_up_to_centring_round_off`
  - `::test_p2_chain_holds_on_switching_states_against_closed_forms`
  - `::test_p2_bound_is_tight_enough_to_catch_a_factor_two`
  - `::test_p2_check_detects_an_indexing_defect`
  - `::test_p2_chain_items_fire_on_planted_defects`
  - `::test_p2_terms_match_brute_force`
  - `::test_p2_population_bound_matches_quadrature`
  - `::test_p2_population_variance_matches_quadrature_and_simulation`
  - `::test_p2_check_reports_same_draws_and_refuses_bad_input`
- **Other tests.**
  - `tests/unit/test_experiments.py::test_p2c_verification_uses_the_core_draws_and_logs_a_mismatch`
  - `tests/unit/test_report.py::test_markdown_p2c_section_is_labelled_report_only_and_shows_defects`
  - `tests/slow/test_p2_bound.py::test_p2c_holds_at_the_core_cell` and `::test_p2c_holds_at_the_stress_cell`
  - `tests/integration/test_smoke_pipeline.py:47-48`
- **Results.**
  - S1: `6 passed in 5.17s`, then rerun on the seed-drawn states in WU-0002.14: `6 passed in 8.88s`. All violation and chain counts are 0, with 1047 to 1257 switching states.
  - Rehearsal (committed):
    - `docs/agent/records/work/WU-0003-R1R2-gate-and-counts.txt`: 1400 states per system, `n_viol 0`, `same_draws_identical True`.
    - `WU-0003-R1R2-R5-gate-and-counts.txt` (R5): 4000 states per system, 0 violations.
    - `WU-0003-R3R6-gates-clips-R3.txt`, `-R6.txt` and `WU-0003-R3R6.md:76,93`: 0 violations in R3 and R6.
- **Reviews.** `WU-0005.5-p2c-bound.md` `## Review`: round 1 (R1 to R3) and re-review (R4, approve with fixes). R4 was fixed in fix round 2 (`23 passed in 2.18s`). There is no re-review of the R4 fix on record.
- **Meets the criterion?** Yes, on all four legs: unit, slow, smoke and the rehearsal on all three systems.
- **Residue.**
  - The check is the same-draws (Markov) form. The population form B_∞ is reported only, consistent with axiom LPC.NV.2, which the owner has not yet declared.
  - The R4 fix is not independently re-reviewed (a one-line test assertion).
  - The unit header still reads "planned".
- **Proposed line (NVVUQ.5):** `met: N_M^2 <= B_M checked state by state on the pipeline's own draws, with chain items; 0 violations in unit, slow (DEV-0, 3 systems x 2 cells) and rehearsal runs R1, R3, R5, R6 (1400/4000 states per system) (tests/unit/test_validation.py::test_p2_*; tests/slow/test_p2_bound.py; WU-0005.5; WU-0003-R1R2-gate-and-counts.txt). Report-only, outside the validation gate.`
- **Proposed line (NVVUQ.14, the P2 clause):** `P2 → met (WU-0005.5, as above)`.

---

## Part 2: the WU-0006, WU-0007 and WU-0008 gap rows

### G6. NVVUQ.7, "Statistical procedures". Gap: "WU-0006 (at pilot sample sizes, with the simulation's own Monte Carlo error)"

- **Row means.**
  - Coverage of the moving-block bootstrap intervals for six statistics.
  - Size of the Holm-adjusted log-rank tests.
  - The ΔR² interval under a null.
  - The verdict-rule branches.
- **ROADMAP criteria (WU-0006.2 and .3).**
  - Coverage ≥ nominal − 3 SE (0.929 and 0.971) at R = 1000.
  - Log-rank FWER ≤ 0.0167 at R = 2000.
  - Null ΔR² interval contains 0 in ≥ 0.921 of 500 replications.
- **Tests.**
  - `tests/slow/test_statistics_coverage.py::{test_exact_checks, test_counts_are_consistent_with_the_reference, test_roadmap_coverage_bounds, test_c1s_dependence_curve_is_reported}`
  - `tests/slow/test_analysis_coverage.py::{test_exact_checks, test_counts_are_consistent_with_the_reference, test_roadmap_coverage_and_verdict_bounds, test_heavy_tail_rows_are_reported}`
  - `tests/slow/test_analysis_logrank_size.py::{test_no_pair_is_left_uncomputed, test_counts_are_consistent_with_the_reference, test_roadmap_size_bound}`
  - `tests/slow/test_analysis_null_delta_r2.py::{test_refit_reproduces_the_returned_gain_bitwise, test_count_is_consistent_with_the_reference, test_roadmap_false_distinct_rate_and_conditional_coverage, test_roadmap_interval_contains_zero}`
  - Harness: `tests/slow/test_wu0006_harness.py`
  - `ASSERT_ROADMAP_BOUNDS = False` (Option C, DEC-0026 item 2, WU-0006.5)
- **Results (`WU-0006-simstudies.md` Log, run 2 table and run 7).**
  - Log-rank L1 and L2 pass at both φ (FWER 19 and 26 of 2000, bound 33).
  - Identity with production (bitwise), A4 verdict equality and 0 failed resamples hold everywhere.
  - All consistency ranges pass, after the post-result C7 correction (F3/DEF-0022, disclosed).
  - **16 ROADMAP-bound coverage and edge rows fail.**
    - 14 are at φ = 0.3, from block-5 undercoverage, which was predicted.
    - 2 are at φ = 0: C4 and C5 at 98.3%, 971 against 972.
    - These are DEF-0020.
  - **N1 fails in 2 of 4 rows** (460 and 457 against 461). This is an estimand mismatch, DEF-0021. N2 and N3 pass.
  - After the WU-0002.14 stream conversions, the exact-check and consistency nodes were rerun once: `102 passed, 5 warnings in 1099.20 s` (`WU-0002.14-seeded-states.md`).
- **Reviews.**
  - `WU-0006-simstudies.md` `## Review`: round 1 (R1 to R7) and re-review (approve). The reviewer found no code defect and nothing loosened.
  - `WU-0006.5-option-c.md` `## Review`: approve with fixes; R1 resolved by the DEC-0024 A2 clarification.
- **Meets the criterion?** Partly.
  - The procedures are verified as implemented: identity, verdict rule, log-rank size, conditional ΔR² (N3) and zero failures.
  - The ROADMAP coverage criterion is **not** met at φ = 0.3, and narrowly not met at φ = 0 for two cases.
  - Under Option C these are recorded characterization rows, not assertions.
- **Residue.**
  - (1) DEF-0020: block-5 undercoverage at lag-1 dependence 0.3.
    - The DEV-1/DEV-2 block-length note (`docs/agent/notes/2026-10-17-math-block-length.md`) finds block 5 adequate on the evidence available. That evidence is conditional and comes from two realizations.
    - Whether to widen the intervals is an open owner and AM question (DEC-0024 A2).
  - (2) DEF-0021: the N1 row of the ROADMAP needs the owner's amendment to N2/N3.
  - (3) DEF-0022: H2a(ii-b) power is low, as v3 §7 pre-registers.
  - (4) H3b coverage is not measured; its label says so.
  - (5) The `test_roadmap_*` nodes have not run since Option C, and the slow tier has never run as one tier on the current code (C15).
    - Later `analysis.py` changes (WU-0003.7b/c, WU-0004d) are additive outputs and were not rerun under the slow rule.
    - The DEC-0024 A2 prediction is unconfirmed.
  - (6) The WU-0006.4 owner checkpoint is not recorded.
  - (7) The run-2 counts survive in the Log table and in `budget.COVERAGE_WU0006`. The `runs/tests/*` logs are untracked.
- **Proposed line:** `partially met: procedures verified as implemented (bitwise identity with production, verdict-rule equality, 0 failed resamples, log-rank FWER within 0.0167 at phi 0 and 0.3, conditional delta-R2 coverage N3 >= 461/500) (tests/slow/test_statistics_coverage.py, test_analysis_coverage.py, test_analysis_logrank_size.py, test_analysis_null_delta_r2.py; WU-0006). Not met: nominal coverage of the block-5 intervals at lag-1 dependence 0.3 (DEF-0020) and the ROADMAP's N1 row (DEF-0021); under Option C (DEC-0026 item 2) these are characterization rows. H3b coverage not measured. Needs owner review (WU-0006.4) and one slow-tier run at the freeze candidate.`

### G7. NVVUQ.13, "Validation ... (a) λ_max of each discrete map against published values, confirmed under VV.2 → WU-0007". Status: "gap → WU-0007; (b) met by design"

- **ROADMAP criterion (WU-0007.2 and .3).**
  - Agreement within 3% relative per system, or a DEF.
  - The report states the comparison and the LPC.NV.1 convention.
  - The report states that no real-world referent applies.
- **Tests.**
  - `tests/unit/test_data.py::test_lyapunov_cached_matches_published_reference[lorenz63|rossler|chua|chua_memo]`. Lorenz is tightened to 1%. Rössler is 3% against two references. Chua has no λ assertion, only finiteness and a bounded orbit. The `chua_memo` case is at 10%.
  - `tests/unit/test_report.py::test_markdown_lyapunov_section_has_comparisons_convention_and_referent`.
- **Results.**
  - `13 passed in 5.18s`. Lorenz −0.015%. Rössler +0.76% and +1.87%. Memo −1.53%.
  - Report radius `54 passed`, integration `10 passed`.
  - Research note: `docs/agent/notes/2026-10-10-research-lyapunov.md`.
- **Review.** `WU-0007-lyapunov-validation.md` `## Review` round 1 (approve with fixes).
  - R1 and R4 were fixed in fix round 1, with the runs logged.
  - R2: a DEC-0010 line was appended at `decisions.md:239`.
  - R3 was closed by the DEC-0026 item 1 ratification of DEC-0010.
  - There is no re-review of the fix round on record.
- **Meets the criterion?** Yes for Lorenz-63 and Rössler. For Chua, no confirmed published value exists at the study's parameters. The ROADMAP's alternative ("a DEF records the discrepancy") is replaced by a recorded limitation (DEC-0010, ratified).
- **Residue.**
  - Chua's λ_max at the study's parameters is not validated. The memo case validates the routine and the field form at a different parameter set only.
  - The Lorenz and Rössler tolerances were derived while the code's pilot values were visible (VV.3). This is disclosed in the docstring.
- **Proposed line:** `(a) met for Lorenz-63 (within 1%) and Rossler (within 3% of two references); Chua: declared limitation, no published lambda_max at the study's parameters (DEC-0010); the routine and field form are checked on Chua's memo parameters within 10% (tests/unit/test_data.py::test_lyapunov_cached_matches_published_reference; tests/unit/test_report.py::test_markdown_lyapunov_section_has_comparisons_convention_and_referent; WU-0007). (b) met by design.`

### G8. The WU-0008 rows (NVVUQ.3, .9, .10, .15, .16 and the WU-0008 half of .22)

- **Common evidence.**
  - `WU-0008-report-budget.md` covers the plan, the AM design M1 to M9 (DEC-0024 with addendum A1) and the reviews:
    - .3/.4: approve after re-review;
    - .2a and .1/.2b: approve with fixes, twice;
    - R17 to R21: **approve**.
  - The work was merged through a gate (a74d6b0).
  - The OF-4 F1 wording is corrected by WU-0004b (614d889, 182ef6f; `WU-0004b-review.md` round 2, approve).
  - The owner checkpoint (WU-0008.5) is not recorded.

| Row | Criterion | Tests (exist on develop) | Meets? | Proposed line |
| --- | --- | --- | --- | --- |
| **NVVUQ.3**, "restate in the report → WU-0008" | QoI table in `RESULTS.md`, one row per identifier-table row | `tests/unit/test_budget.py::test_declaration_table_has_a_complete_row_per_table_row`, `::test_a_table_row_without_a_declaration_raises`, `::test_declaration_texts_state_the_statistics_of_the_decision_log`, `::test_markdown_has_the_declaration_section_between_labels_and_allocation`; `tests/unit/test_identifiers.py::test_declarations_cover_the_table_keys_with_nonempty_fields` | Yes. There are 14 rows, gain bound included (DEC-0021 O1, ratified); the ROADMAP row says 13 plus Q-N. | `met: QoI declaration table restated in RESULTS.md (WU-0008.4; test_budget.py::test_declaration_*)` |
| **NVVUQ.9**, "size of each error per QoI ... in the report's budget → WU-0008" | Numerical rows with a size or "not estimated: reason", and the 10% flag | `test_budget.py::test_table_cells_for_each_numerical_row`, `::test_the_ten_percent_flag_is_strict`, `::test_lm_row_is_not_estimated_with_and_without_the_summary`, `::test_not_estimated_reasons_are_true_in_each_reachable_case`, `::test_lm_development_note_under_every_table` | **Partly.** V6, round-off and oracle MC are sized. The iterative (LM) row is "not estimated" by design (DEF-0027, O4/O6 open). V6 failed once on Chua: R5, GPU, 2.4e-3 against 1e-3 (DEF-0026). | `partially met: discretization (V6, LPC.NV.1), round-off and oracle Monte Carlo rows sized per primary QoI (WU-0008.2); iterative LM row 'not estimated' with DEV-0 development evidence (DEF-0027); V6 on Chua device-dependent (DEF-0026)` |
| **NVVUQ.10**, "Monte Carlo error of the interval endpoints → WU-0008" | Endpoint binomial error; nested check within a factor of 2 | `tests/unit/test_statistics.py::test_endpoint_mc_error_on_the_deterministic_normal_grid_within_2_percent`, `::test_endpoint_mc_error_median_over_100_bootstraps_matches_the_endpoint_sd` (factor 1.4, tighter than 2; AM, DEC-0024), `::test_endpoint_mc_error_is_none_when_failures_reach_the_window_or_the_window_leaves_0_1`; `tests/unit/test_analysis.py::test_ci_mc_se_is_persisted_at_the_five_primary_sites_and_only_there` | Yes. A1 smoke: 0 changed leaves; 14 new `ci_mc_se` leaves. | `met: endpoint Monte Carlo error per primary interval (ci_mc_se), checked against a repeated bootstrap within a factor 1.4 (WU-0008.2a)` |
| **NVVUQ.15**, "Uncertainty budget → WU-0008" | One table per primary QoI, every row sized or "not estimated: reason" | `test_budget.py::test_every_table_has_nine_rows_in_order_and_no_cell_is_empty_or_unparsable`, `::test_old_schema_and_a_missing_result_give_the_same_rows_and_not_estimated_cells`, `::test_markdown_has_the_budget_section_between_validation_and_robustness`, `::test_coverage_constants_equal_the_wu0006_documents`, `::test_oracle_row_formulas_equal_the_hand_expressions` | **Partly.** The five primaries are done. NVVUQ.15 says "per primary QoI", but the profile asks for every reported QoI: secondaries and Q-N were deferred (DEC-0021 O5). The LM and some proxy rows read "not estimated". The interval-procedure row uses synthetic coverage (DEF-0020). | `partially met: budget tables for the five primary QoIs (nine rows each; WU-0008.1); secondaries and Q-N not tabulated (DEC-0021 O5); LM row not estimated (DEF-0027)` |
| **NVVUQ.16**, "figure labels → WU-0008" | Procedure, level, dependence and multiplicity next to every interval table; captions | `test_budget.py::test_every_label_has_the_four_elements_and_reads_its_config`, `::test_markdown_labels_every_interval_table_before_the_next_heading`, `::test_label_level_equals_the_stored_level_and_a_mismatch_raises`, `::test_every_figure_file_has_one_caption_in_the_markdown_and_the_png`, `::test_an_interval_caption_states_level_and_procedure` | Yes. No figure draws an interval today (DEC-0021 O4), so the interval caption is exercised on a synthetic entry. | `met: four-element label after every interval table and a caption per figure (WU-0008.3)` |
| **NVVUQ.22**, "gap → WU-0001, WU-0008" | Header labels and provenance (WU-0001); per-QoI budget table (WU-0008) | WU-0008 part: as for NVVUQ.15. WU-0001 part: `tests/unit/test_report.py::test_header_labels_are_exact_in_the_markdown_file`, `::test_header_has_the_platform_line_under_the_label_a8` (not assessed in depth here) | WU-0008 part: as NVVUQ.15. | `WU-0008 part: as NVVUQ.15; WU-0001 part: not assessed in this note` |

---

## Summary

| Row | Proposed status | Residue |
| --- | --- | --- |
| NVVUQ.5 RK4 | met | Σbc³ = 1/4 not exercised (f‴ ≡ 0) |
| NVVUQ.5 Analog search | met | none |
| NVVUQ.5 Levina–Bickel | met (3%, tightened) | interior queries only, by design |
| NVVUQ.9 LM | met (reporting), plus a declared limitation | QoI iterative error shown negligible on only 5 of 18 DEV-0 parts (X 6 not negligible, U 7 undetermined; DEF-0027, "report and flag only", not yet a DEC); "about 2% wrong basin" unmeasured; dof = D − m confirmation not explicit |
| NVVUQ.5 N vs P2 (and NVVUQ.14 P2) | met | Markov/same-draws form only (axiom LPC.NV.2 undeclared); R4 fix not re-reviewed |
| NVVUQ.7 statistical procedures | partially met | DEF-0020 undercoverage (φ = 0.3; 2 marginal at φ = 0), DEF-0021 N1, DEF-0022 power, H3b not measured, slow tier not rerun since Option C, owner checkpoint |
| NVVUQ.13 validation (a) | met for 2 of 3 systems; Chua declared | Chua λ_max unvalidated at the study's parameters (DEC-0010) |
| NVVUQ.3 restate | met | none |
| NVVUQ.9 size per QoI | partially met | LM row not estimated; V6 Chua device-dependent (DEF-0026) |
| NVVUQ.10 endpoint MC error | met | none |
| NVVUQ.15 budget | partially met | secondaries and Q-N deferred; LM row not estimated |
| NVVUQ.16 labels | met | no figure draws an interval |
| NVVUQ.22 (WU-0008 part) | as NVVUQ.15 | WU-0001 part not assessed |

**Records to tidy (not status questions).** These are stale unit headers:
- `WU-0005-verification.md`
- `WU-0005.4-lm-diagnostics.md`
- `WU-0005.5-p2c-bound.md`
- `WU-0006-simstudies.md`
- `WU-0007-lyapunov-validation.md`
- `WU-0008-report-budget.md`

In each of these, `## Audit` is empty.
