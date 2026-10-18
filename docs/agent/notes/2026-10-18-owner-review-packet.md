# Owner review packet: WU-0004.5, with the checkpoints WU-0006.4 and WU-0008.5 (freeze blockers B2, C14)

Prepared 2026-10-18 by claude-opus-5-5 (drafting only) on branch `wu/0004-owner-packet`, from develop `7b6f6e6`. This is a reading list, not a review. Nothing was run except read-only inspection: `git log`, `git diff --shortstat`, `git blame` counts, `wc` and a Python AST listing of function line ranges.

Sources:
- `docs/agent/records/work/queue.md` and every unit and review file under `docs/agent/records/work/`;
- `docs/agent/notes/2026-10-18-freeze-blockers.md` (B2, B9, C14);
- the amendments note §§16-36;
- `decisions.md`;
- `ROADMAP.md` rows WU-0004.5, WU-0006.4, WU-0008.5.

**What the owner must record.** The ROADMAP sets two requirements:
- WU-0004.5 acceptance: "the owner's review is recorded in each unit's `## Review` under their name";
- LPC.PC.11: verdict, statistics and acceptance code; the seed and provenance machinery; dependency additions.

A line per unit is enough, for example:

```
- <date>, <owner name> (human owner): reviewed <files and functions read> at <commit>; readings confirmed: <list>; not reviewed: <list, with waiver ledger entry n>.
```

Many agent reviews live in separate `WU-*-review*.md` files. Whether the owner's line goes into the unit file or the review file is not settled (freeze blockers E6). The unit file is the literal reading.

**What the owner has not decided.** The owner has not chosen among B2's options: full review, tiered review with waivers for tools, or waiver per unit. The tiers below allow any of them. Under option 2, Tiers 1 and 4 are reviewed and every Tier 3 file not reviewed gets a `waiver` (ledger batch draft, L23).

---

## 0. Effort, honestly

The rate is an assumption, not a measurement: focused reading of dense numerical Python against its specification, its tests and the review record, at 150 to 250 lines per hour. "Focus lines" counts only the functions listed in the tables, measured from the AST. Expect re-reading and questions to add time.

| Tier | Scope | Full lines | Focus lines | Hours at 250 / 150 lines per hour |
| --- | --- | --- | --- | --- |
| 1A | Seed, provenance, CLI guards, presets (`lpcstudy/`) | 1,953 | 1,233 | 5 to 8 |
| 1B | Verdict, statistics, criteria, budget and report (`lpcstudy/`) | 6,855 | 4,945 | 20 to 33 |
| 1C | WU-0006 study code (`tests/slow/`; checkpoint WU-0006.4) | 2,537 | about 670, plus spot reading | 4 to 8 |
| 2 | Numerics feeding the statistics (`lpcstudy/`) | 4,927 | 2,219 | 9 to 15 |
| 3 | Tools whose output feeds CSQ2 decisions | 11,802 | 3,239 | 13 to 22 |
| 4 | Dependency pins | 30 | 30, plus the lock (C17) | about 1 |
| **Total** | | **about 28,100** | **about 12,300** | **about 50 to 82** |

Three ways to scope the review, with their consequences:
- **(i) Decision-point read**, about 1,500 lines, 6 to 10 h. Read only the constants, the verdict and interval functions in **bold** below, and the seed guard. The owner's `## Review` lines must then say that the review sampled the code and relied on the independent reviews for the rest (PRIME.2: claim no more than was read).
- **(ii) Tiers 1 and 4 in full focus**, about 27 to 46 h. This is B2 option 2, with waivers for Tier 3 (6,880 focus lines).
- **(iii) Everything in focus**, about 50 to 82 h.

---

## 1. Tier 1A: seed, provenance, CLI guards and presets

| File (lines) | What it decides | Functions that matter (line ranges) | Tests | Independent reviews already done |
| --- | --- | --- | --- | --- |
| `lpcstudy/seeds.py` (206; all new since v1) | Which master seed a run may use; refusal of raw, unknown and confirmatory seeds; the commitment check against the ledger | **`resolve_dev_seed` 86-113**, **`check_commitment` 116-167**, **`confirmatory_seed` 170-201**, `load_registry` 39-83 | `tests/unit/test_seeds.py` (24); `tests/integration/test_cli_seeds.py` | `WU-0001-seed-provenance.md` `## Review` (line 441+; mathematician R1 at line 330) |
| `lpcstudy/__main__.py` (241; 54 v1 lines) | The CLI guard order: seed, sealed flag, `--states-dump` refused with the sealed flag, `--estimator-refine-steps` refused with the sealed flag; exit codes | **`choose_seed` 110-133**, **`choose_refine_steps` 83-107**, **`choose_states_dump` 58-80**, `main` 136-237, `REFUSAL_EXIT` | `tests/unit/test___main__.py` (27); `test_cli_seeds.py`; `tests/integration/test_states_dump.py` | WU-0001 (as above); `WU-0003.7b-review.md`, `WU-0003.7b-review-round2.md`; `WU-0005.6-lm-doubling.md` re-review (line 676); `WU-0005.6-review-round2.md` (names `choose_refine_steps` for the owner) |
| `lpcstudy/provenance.py` (412; new) | What every run records: commit, `dirty`, environment, packages, platform (CPU, BLAS, SIMD), digests | **`git_state` 70-90** (records `dirty`, refuses nothing; B8 adds the refusal), **`collect` 351-402**, `array_digest` 115-141, `index_digest` 144-171, `ENV_NAMES`, `finish` 405-412 | `tests/unit/test_provenance.py` (35) | WU-0001; `WU-0001.6-platform-record.md` `## Review` (line 405+, three rounds); `WU-0012.5-provenance-env.md` (line 27+); `WU-0003.7a-review.md` |
| `lpcstudy/data.py` (476; 255 v1 lines) | The randomness root (`make_rng`), the seed-dependent start states, the scikit-learn seed (DEF-0010), the context build and the Lyapunov cache | **`make_rng` 39-55**, **`draw_starts` 84-121**, **`sklearn_seed` 128-163**, `build_context` 371-476, `lyapunov_cached` 353-368 | `tests/unit/test_data.py` (21), `tests/unit/test_rng_hygiene.py` (7), `tests/slow/test_start_states.py` (3) | `WU-0002.6-qn-h2a.md` step (a) review (DEF-0010, line 246+); `WU-0002.11c-orbit-guard.md` (line 321+); `WU-0002.14-seeded-states.md` `## Review` (line 763+) and `WU-0002.14-review-P1.md`; mathematician M1-M7 in the .14 unit file |
| `lpcstudy/systems.py` (398; 236 v1 lines) | The orbit guard that refuses a diverging Lyapunov or context orbit; this sets the time unit (DEC-0017 Q1) | **`guard_orbit` 261-299**, **`lyapunov_guarded` 302-373**, `checked_bound` 233-250; the vector fields 28-101 are v1 | `tests/unit/test_systems.py` (11) | `WU-0002.11c-orbit-guard.md` `## Review`; WU-0007 λ validation (`WU-0007-lyapunov-validation.md`, line 354+) |
| `lpcstudy/config.py` (220; **209 v1 lines**) | The presets: FULL is the confirmatory sample size (DEC-0029) | `StudyConfig` 14-193; **`FULL` 196, `PILOT` 198, `SMOKE` 207** | `tests/unit/test_config.py` (5); `tests/slow/test_wu0006_harness.py` (`assert_design` pins FULL's B, block, levels and sizes) | Only the diffs of WU-0001.1 and WU-0002.1-.3 and .10 were reviewed; the FULL values are v1 lines |

**Not in Tier 1A on purpose:**
- `lpcstudy/dump.py` (429 lines). The dump is off in the sealed run (B11), and `__main__` refuses it with the sealed flag before the seed is read. Its content is in Tier 3 priority. Reviews: `WU-0003.7b-review.md`, `-round2.md`, `WU-0003.7c-review.md`.
- The seed-sealing script. See §9.

## 2. Tier 1B: verdict, statistics, acceptance criteria, budget and report

| File (lines) | What it decides | Functions that matter (line ranges) | Tests | Independent reviews already done |
| --- | --- | --- | --- | --- |
| `lpcstudy/statistics.py` (739; 174 v1 lines) | The shared interval and verdict contract (DEC-0012), the A1/A3 rules, failed resamples, the overall verdict (DEC-0016), log-rank and Holm, the endpoint Monte Carlo error | **`percentile_interval` 272-329**, **`interval_verdict` 469-511**, **`criterion_verdict` 591-627**, **`overall_verdict` 543-588**, `combine_verdicts` 514-540, `block_resample_indices` 183-219, `block_bootstrap_counted` 358-392, `holm_adjust` 160-180, `logrank_test` 130-157, `endpoint_mc_error` 395-466, `partial_correlation` 713-734 | `tests/unit/test_statistics.py` (32); slow `test_statistics_coverage.py` | `WU-0002.4-5-h1.md` (contract, line 131+); `WU-0002.7-8-h2-h3.md` (line 347+); `WU-0002.9-verdicts.md` (line 331+); `WU-0002.11-counters.md` (.11b); `WU-0008-report-budget.md` (.2a reviews, lines 780, 913, 1022) |
| `lpcstudy/analysis.py` (2,243; 394 v1 lines) | Every hypothesis statistic and its band | **constants 45-73** (bands, levels, `H3A_ALPHA`); **`h1a_library_scaling` 309-431**; `h1b_seed_amplifier` 434-511; `h1c_horizon_law` 567-629; `h1d_correlations` 636-710; **`qn_reading` 820-848**, `qn_profile_block` 863-986; **`h2a_initial_segments` 1120-1203**, **`h2a_part_ii` 1206-1296**; **`h2b_knob_response` 1472-1592**; `h2e_noise_matching` 1595-1667; **`h2c_state_dependence` 1670-1755**; `h2d_empirical_comparison` 1758-1794; `gain_horizon_bound` 1797-1848; **`h3a_logrank` 1857-1958**; `h3b_importances` 1978-2101; **`h3c_ratio` 2104-2144** | `tests/unit/test_analysis.py` (84); slow `test_analysis_coverage.py`, `test_analysis_logrank_size.py`, `test_analysis_null_delta_r2.py` | `WU-0002-methods-v2-changes.md` (line 444+); `WU-0002.4-5-h1.md`; `WU-0002.6-qn-h2a.md` (line 244+); `WU-0002.7-8-h2-h3.md`; `WU-0002.9-verdicts.md`; `WU-0002.9b-h2b-counted.md` (line 35+); `WU-0002.10-v7.md` (line 145+); `WU-0003.7c-review.md`; WU-0008 .2a reviews |
| `lpcstudy/validation.py` (598; 237 v1 lines) | The validity gate V1-V7 (`gate_pass`, provisional marking) and the P2(c) bound | **`gate_status` 255-282**, `check_jacobians` 18-72, `check_cramer_rao` 75-133, `check_integrator` 171-200, `check_cp_horizon` 203-252, `check_p2_bound` 565-598 | `tests/unit/test_validation.py` (22); slow `test_p2_bound.py` | `WU-0002.10-v7.md`; `WU-0005.5-p2c-bound.md` (line 496+); `WU-0005.4-lm-diagnostics.md` (line 460+); WU-0002.11a |
| `lpcstudy/identifiers.py` (323; new) | The v3 identifier map and the required result keys | `Hypothesis` 26-52, `check_keys` 108-131 | `tests/unit/test_identifiers.py` (11) | `WU-0002-methods-v2-changes.md`; WU-0008.3/.4 reviews |
| `lpcstudy/report.py` (1,028; 249 v1 lines) | The verdict rows, the "FAIL (results provisional)" rule (DEC-0016 O4) and the RESULTS.md text | **`verdicts` 87-154**, `_key_number` 173-258, `write_markdown` 766-897, `_v7_rows` 440-464, `_lm_lines` 590-654, `clip_lines` 730-762 | `tests/unit/test_report.py` (30); `tests/integration/test_smoke_pipeline.py` | `WU-0002.9-verdicts.md`; `WU-0007-lyapunov-validation.md` (.3); `WU-0008-report-budget.md`; `WU-0005.4-lm-diagnostics.md` |
| `lpcstudy/budget.py` (997; new) | The uncertainty budget, the interval labels and the 10% rule (checkpoint WU-0008.5) | **`oracle_range_bound` 564-574** and **`_oracle_cell` 685-729** (the OF-4 text, lines 565, 570, 702), `interval_label` 122-179, `below_tenth` 541-551, `_lm_cell` 770-776 (B7), `_coverage_cell` 836-848, `budget_lines` 962-997; constants `COVERAGE_PROVENANCE`, `DEF0020_TEXT` | `tests/unit/test_budget.py` (35) | `WU-0008-report-budget.md` `## Review` (lines 613-1098: .3/.4 two rounds; .2a and .1/.2b three rounds; last verdict approve); `WU-0006.5-option-c.md` (line 73+) |
| `lpcstudy/clip_sensitivity.py` (927; new) | The clip-sensitivity flag next to MSE- and weight-based verdicts (OD1-OD7) | **`flag_rule` 184-211**, `median_bound` 258-299, `_compute` 624-759, `invariance` 762-814 | `tests/unit/test_clip_sensitivity.py` (27); `tests/integration/test_clip_failure.py` | `WU-0002.11e-clip-sensitivity.md` `## Review` (line 430+, re-review line 494) |

## 3. Tier 1C and the two checkpoints

**WU-0006.4 (statistical-procedure verification).**

Code:
- `tests/slow/wu0006_reference.py` (171 lines);
- `tests/slow/wu0006_harness.py` (1,080 lines);
- `tests/slow/test_wu0006_harness.py` (790 lines);
- the four studies: `tests/slow/test_statistics_coverage.py`, `test_analysis_coverage.py`, `test_analysis_logrank_size.py` and `test_analysis_null_delta_r2.py` (496 lines together).

Reviews:
- `WU-0006-simstudies.md` `## Review` (line 520+): round 1 with 7 findings; re-review closed R1-R7, with R3a as a one-line residual;
- `WU-0006.5-option-c.md` `## Review` (R1-R3);
- mathematician `docs/agent/notes/2026-10-11-math-wu0006.md`.

Points for the owner:
- (a) The N2/N3 reading was ruled in §36: N1, N2 and N3 are computed and reported, none asserted.
- (b) The 12 delta-R2 consistency ranges (A9) were fixed after run 2 had shown the counts. DEC-0018's update (3) calls their pass "a regression guard, not independent confirmation".
- (c) **The slow tier has not run as one tier since Option C.** DEC-0024 A2's prediction (no ROADMAP-bound node fails; consistency ranges and exact checks pass) is unconfirmed (C15).
- (d) The unit's `## Audit` is empty.

**WU-0008.5 (budget and labels).**

Code: `budget.py` (above); `statistics.endpoint_mc_error`; the budget lines in `report.py`.

Points for the owner:
- (a) OF-4. Until the WU-0004b text change lands, every RESULTS.md prints "indicative worst case ≤ F1". That includes a sealed run's. Draft addendum A3 is in the ledger batch draft, D5.
- (b) B7. The LM row prints "not estimated" plus a pointer. The text change is planned on `wu/0004b-budget-text` (plan commit `64e59d6` only).
- (c) The WU-0006 coverage numbers are constants with provenance (`COVERAGE_PROVENANCE`; DEC-0021 O3), checked by a test that parses the WU-0006 Log table.
- (d) The unit's `## Audit` is empty.

## 4. Tier 2: numerics that feed the statistics

These do not decide a verdict, but every statistic is computed from them. They are changed in many reviewed diffs, and about half of their lines (2,481 of 4,927) are v1 lines.

| File (lines; v1 lines) | What it decides | Functions that matter | Tests | Reviews |
| --- | --- | --- | --- | --- |
| `lpcstudy/pipeline.py` (1,091; 450) | The K rule and the allocator scores | **`choose_regime_count` 860-898**, `rule_weights` 966-1007, `score_rules` 1042-1091, `fit_rules` 456-507 | `test_pipeline.py` (18) | `WU-0002.3-excess-mse.md` (line 340+); WU-0002.11a, .11e, .14; WU-0003.7a/7b; WU-0005.4 |
| `lpcstudy/allocation.py` (607; 385) | Regime calibration and the closed-form weight | **`calibrate_regimes` 517-572**, `regime_weight` 477-514, `closed_form_weight` 204-206, `fit_regime_tree` 445-474 | `test_allocation.py` (12) | WU-0002.3, .6, .11a, .14 |
| `lpcstudy/oracle.py` (383; 204) | The oracle weight w*, excess MSE, local dimension (Levina-Bickel) | **`excess_mse` 272-324**, `oracle_weight` 222-244, `local_dimension_counted` 55-83, `inverse_dimension` 107-139 | `test_oracle.py` (22) | WU-0002.3, .4, .11a, .14; WU-0012.6; WU-0005 verification (`WU-0005-verification.md`, line 207+) |
| `lpcstudy/experiments.py` (810; 221) | The per-system run, the convergence check, P2(c), V7 replacements, the context and fit records | `run_system` 574-686, `convergence_check` 62-169, `p2c_verification` 261-309, `context_record` 504-529, `fitted_record` 532-571 | `test_experiments.py` (23) | many: WU-0002.x, WU-0003.7a-c, WU-0005.4, WU-0005.5b, WU-0011.5 |
| `lpcstudy/estimation.py` (434; 108) | PLP's fixed 15-iteration Levenberg-Marquardt and its diagnostics | `StateEstimator` 130-348, `lm_summary` 351-434, `gof_threshold` 47-74 | `test_estimation.py` (18) | `WU-0005.4-lm-diagnostics.md` (line 460+, re-review line 557) |
| `lpcstudy/ensemble.py` (899; 470) | The CP draws, error clips, moments, evaluation draws, worker count | `clip_errors` 110-144, `ensemble_moments` 607-723, `evaluation_draws` 819-899, `sanitize_gains` 791-816 | `test_ensemble.py` (19) | WU-0002.11a, .11e; WU-0005.4; `WU-0012.6-def0012-workers.md` (line 30+) |
| `networks.py` (293; 242), `dynamics.py` (291; 282), `embedding.py` (119; **all v1**) | Network training; flow maps; delay selection | (mostly v1) | `test_dynamics.py` (4), `test_embedding.py` (3); WU-0005 RK4 order and k-d tree tests | WU-0002.14 and WU-0003.7a diffs only; WU-0013 audited the v1 tests |

## 5. Tier 3: tools

Ordered by how directly each tool's output enters a CSQ2 decision.

| File (lines) | What it decides | Functions that matter | Tests | Reviews |
| --- | --- | --- | --- | --- |
| `tools/compare_runs.py` (1,624) | The reproducibility tier and pass/fail of a run pair: DEC-0028, the GPU cross-check of DEC-0031, WU-0016 | **`select_tier` 388-453**, **`decide` 1073-1196**, **`td_part` 1256-1291**, **`td_statistic` 1303-1342**, `_build_tags` 707-837, **`_build_retags` 887-907 (RETAGS)**, `count_scope` 545-569, `in_scope` 580-595, `classify_float` 481-508; constants 185-231 (`TD_BOUND`, `TOL_*`) | `tests/unit/test_tools_compare_runs.py` (99) | `WU-0003.9-review.md`, `-round2.md`, `-round3.md` (approve); `WU-0003.9b-review.md`; `WU-0003.9c-review.md` (approve after R1-R3) |
| `tools/run_preset.sh` (312) | The LPC.AUTH.3 wrapper: lock, thread cap (`PJRT_NPROC`), sealed-flag scan, GPU-hours tally, run meta | the whole file | `tests/unit/test_tools_run_preset.py` (36); `tests/integration/test_preset_wrapper.py` | `WU-0012-wrappers.md` (line 275+, three rounds); `WU-0012.4-xla-threads.md`; `WU-0003.11-review.md`; `WU-0005.6-review-round2.md` |
| `tools/lm_doubling.py` (1,896) | The LM-row flag (classes N/X/U) quoted in the report (B7) | **`classify` 264-383**, **`tail_ratio` 386-400**, `pairing_problems` 1435-1453, `probe_problems` 1484-1527 | `tests/unit/test_tools_lm_doubling.py` (70); `tests/integration/test_lm_doubling_probe.py` | `WU-0005.6-lm-doubling.md` (re-review line 676); `WU-0005.6-review-round2.md`; `WU-0005.6-report-check.md`; `WU-0005.6-rule-r-order-review.md` |
| `tools/compare_pilot.py` (2,356) | The DEV-0 regression branch and D3 (the WU-0004.3 evidence) | **`select_branch` 1164-1200**, `evaluate_n` 1313-1408, `evaluate_d` 1605-1650, `d3_rows` 1504-1540, `se_pair` 1228-1247; rule table `_build_rules` 480-940 | `tests/unit/test_tools_compare_pilot.py` (102) | `WU-0002.12-pilot-regression.md` (line 593+); WU-0002.14 reviews; WU-0001.6b; WU-0002.11c, .11e |
| `tools/rehearsal_report.py` (1,235) | The precision report behind the sample-size decision (DEC-0029); its exit code | `project_row` 826-928, `h3a_projection` 393-423, `kappa_range` 239-243, `outside_margin` 385-390, `run` 1089-1202 | `test_tools_rehearsal_report.py` (59); slow `test_rehearsal_report_mc.py` | `WU-0003.3a-review.md`, `-round2.md` to `-round4.md` (accept pending OF-H1 and OF-R2, since ruled) |
| `tools/rehearsal_diagnostics.py` (2,829) | D1-D6, the block-length reading (OF-3) and the block-sensitive label | `section_d1_d2` 1601-1720, `_permutation_reading` 1723-1741, **`block_sensitivity` 1775-1822**, `widen_interval` 1770-1772, `section_d5` 1976-1991, `run` 2679-2784; `TOOL_SEED` 160 (OQ-R9) | `test_tools_rehearsal_diagnostics.py` (102); slow `test_rehearsal_diagnostics_mc.py` | `WU-0003.8-review.md`, `-round2.md` to `-round4.md`; `WU-0003.8d-review.md` (approve) |
| `tools/rehearsal_common.py` (232) | Shared numerics of the two rehearsal tools | whole file | `test_tools_rehearsal_common.py` (14); the goldens | **No independent review record found** (§9) |
| `tools/leafdiff.py` (149), `tools/gpu_hours.py` (325), `tools/run_tests.sh` (137), `tools/test_impact.py` (547) | Leaf diffs; GPU-hours tally against the 60 h cap; test runner; blast radius | `tally_week`, `select` | their `test_tools_*.py` files | WU-0002.14; `WU-0012-wrappers.md`; `WU-0011-test-impact.md`, `WU-0011.5-tooling-def0025.md` |
| `tools/ledger.py` (160; v1 baseline) | The hash chain, adoption drift and the freeze record (GOV.36, GOV.38) | `verify_chain` 54-80, `append_entry` 83-109, `show_status` 112-131 | indirectly through `seeds.check_commitment` (`test_seeds.py`) | **None found** (§9) |

## 6. Tier 4: dependencies (LPC.PC.17)

Files: `requirements.txt` (8 pins) and `docs/agent/records/dependencies.md`.

What the owner should know:
- The pins were "last reviewed on 2026-10-10 (initial)", by Claude, as "the versions the v1 pilot ran with". No dependency has been added since.
- No lock of transitive dependencies exists. `requirements.lock` is a WU-0004.7 output, and C17 prepares it from `pip freeze`.
- The GPU wheel `jax[cuda12]==0.11.2` appears only as a comment. It now matters for the GPU cross-check of DEC-0031.
- The XLA thread cap uses the undocumented `PJRT_NPROC` (§7). It must be re-checked on any jax pin change.

## 7. Units marked "needs owner review before freeze"

Sources: the `queue.md` log lines, unit files and review files.

- **Seed and provenance:**
  - WU-0001 (guard, registry, provenance block);
  - WU-0001.6 (platform record);
  - WU-0012, .4, .5 (wrappers, thread cap, provenance env);
  - WU-0002.14 (start states, `make_rng` conversions, `compare_pilot --redrawn-states`);
  - WU-0003.7a (provenance digests);
  - WU-0003.7b (dump, CLI guard);
  - WU-0003.11 (`run_preset.sh --states-dump`);
  - WU-0005.6 (`choose_refine_steps`, the wrapper).
- **Verdict and statistics:**
  - WU-0002.3 to .9, .9b, .10, .11 (a, b), .11c (orbit guard), .11e (clip sensitivity);
  - WU-0002.12 (regression criterion, DEC-0019 and DEC-0020);
  - WU-0005.4 (LM diagnostics);
  - WU-0006 and WU-0006.5 (Option C);
  - WU-0008 (budget, .2a);
  - WU-0003.7c (verdict-chain data in `h1a_library_scaling` and `h1c_horizon_law`).
- **Tools feeding CSQ2 decisions:**
  - WU-0003.3a (`rehearsal_report`);
  - WU-0003.8, .8b, .8c, .8d (`rehearsal_diagnostics`; seed code OQ-R9);
  - WU-0003.9, .9b, .9c (`compare_runs`: tolerance classes, RETAGS, OF-5);
  - WU-0003.10 (part);
  - WU-0005.6 and DEF-0028 (`classify`, `tail_ratio`, `pairing_problems`, `probe_problems`).
- **Decision records** marked the same way: DEC-0011, 0012, 0013, 0014, 0016, 0017, 0018, 0019, 0020, 0021, 0022 (item 4), 0023, 0024, 0025, 0026, 0027.
- **Coming:** the B8 dirty-tree refusal, the B6b event counts, and the WU-0004b text all change Tier 1 code. Each will add its own "needs owner review before freeze" before the freeze commit.

## 8. Readings the reviewers asked the owner to confirm

Status as the records show it on 2026-10-18.

| # | Reading | Where it is decided in code | Asked in | Status |
| --- | --- | --- | --- | --- |
| 1 | DEF-0028: a half-width ≤ 0, NaN, or an infinite point with finite bounds is **not** a structural switch (stays U, or X if verdicts differ) | `tools/lm_doubling.py` `classify` 264-383 | §30; `WU-0005.6-rule-r-order-review.md` "Owner checkpoint (unchanged)" | **Open** |
| 2 | DEF-0028: an infinite lower or upper bound at any arm **is** a switch (U) | same | same | **Open** |
| 3 | RETAGS: does OF-7 also cover `ratio` and `ratio_ci`? The text ruled on said they "already" were at 1e-4 s, which stopped being true at `da22cdd` on 2026-10-17. Under the literal reading, every T2 pair (WU-0016 cross-host) fails on 18 H1a leaves with correct code | `tools/compare_runs.py` `_build_retags` 887-907 | `WU-0003.9c-review.md` R3 and "Owner checkpoint" item 1; `WU-0003-dev-rehearsal.md` "Open for the owner" (1) | **Open** |
| 4 | RETAGS: `floor_rms` is class (g), a FINDING with exit 1 and `--tol-other` ≤ 1e-4, while the ruling text says "class a"; its basis is a flip ≤ 6.3e-7 relative with safety factor ≥ 70 | same | same, item (2) | **Open** |
| 5 | RETAGS: the chain stays cp, so the whole-system clip scope does not reach these leaves, while block-local H1a counts still license 0.1 hw per A6 | same; `count_scope`, `in_scope` | `WU-0003.9c-review.md` item 1 | **Open** (information) |
| 6 | OF-5 text: the A6 and B1 item 5 plan text still says `max(z_sym, z_away)`, and the tool fails on `z_away` alone. A planner amendment and the owner's decision entry are needed | `td_statistic` 1303-1342 | `WU-0003.9c-review.md` item 2 | Ruled (§33); **records owed** (DEC-0028, a plan amendment) |
| 7 | 8d judgement call (b): block-sensitive label rows, including "not computable" rows and invariant violations, never set exit 2 | `tools/rehearsal_diagnostics.py` `_block_sensitivity_lines` 1825-1865 | `WU-0003.8d-review.md` R1 and "Owner checkpoint"; `WU-0003-dev-rehearsal.md` 8d entry (b) | **Open** |
| 8 | 8d judgement call (d): the label is per primary **part**, not per combined hypothesis verdict | `block_sensitivity` 1775-1822 | same, (d) | **Open** |
| 9 | `follows_k` (the K-block listing) is a looser reading, labelled in the docstring | `tools/compare_runs.py` `follows_k` 598-601 | `WU-0003.9-review-round3.md` (R17, verdict line) | **Open**: not named in §33 or §36 |
| 10 | `n_states` of a network-independent block licenses 0.1 hw on its cp leaves (A6 as written; reading 9 and Q7) | `count_scope` | `WU-0003.9-review-round3.md` "Information for the owner" | Probably covered by §33 "handling-count licence kept as written"; **confirm** |
| 11 | OF-H1 (range-governed kappa_E rows count as computed for the `rehearsal_report` exit code) | `tools/rehearsal_report.py` `run` | `WU-0003.3a-review-round4.md` | Ruled §36 (B9) |
| 12 | OF-I1 (min anchor; H1d at 98.3% prints 0.9794) and OF-I2 (C7 for the H2a(ii) "one" part) | `rehearsal_diagnostics` `coverage_at` 536-552 | amendment 9 | Ruled §36 |
| 13 | OQ-R9 (tool seed and options) | `TOOL_SEED` 160 | `WU-0003.8-review.md` R9 | Ruled §26 |
| 14 | Q6, K2: d3 was shown on scratch copies, not on the unedited S3 pair | tests only | §34 point 8; drafts §4 | **Ambiguous**: §33 "keep as built" names d1; §36's en bloc may cover it |
| 15 | N2/N3 under Option C | `tests/slow/` switch | `WU-0006.5-option-c.md` R1 | Ruled §36 (code reading kept) |
| 16 | WU-0003.7c F4 additions (four H1a keys, H1c masks, stronger b3) | `lpcstudy/dump.py`, `analysis.py` | `WU-0003.7c-review.md` | Ruled §33 (keep) |
| 17 | DEC-0013: the K rule is evaluated at H_ref; v3 §5 should state the horizon | `pipeline.choose_regime_count` | DEC-0013 | Ratified (DEC-0026); **v3 edit owed** (B1) |
| 18 | DEC-0015: what "superseded" means for V7 | — | DEC-0015 | **Open** (non-blocking) |
| 19 | WU-0003.10: `block_variance` and the influence builders remain duplicated in the two tools (they differ in substance; G4 part unmet) | `rehearsal_diagnostics` 279-289; `rehearsal_report` 289-300 | merge `2d99ac4` message | **Open** (planner and owner; tool only) |
| 20 | `rehearsal_diagnostics` exit 1 on R1 and R5 only for the three H1d nhat Spearman tie entries (a documented artefact); exit 2 on R6 by design | `check_spearman_ties` 1144-1174 | freeze blockers D | Information; confirm the exit-code reading |

## 9. What no independent review covers

1. **v1 baseline code that no unit changed.** Each agent review I sampled is scoped to a diff, for example "`git diff 789f5a1..6adf6cc`". `git blame` attributes **4,289 of 14,164 lines in `lpcstudy/` (30%)** to the baseline commit `f01360d`. No review on record read those lines as code.
   - In Tier 1:
     - `config.py`: 209 of 220 lines, including the FULL sample sizes;
     - `analysis.py`: 394;
     - `data.py`: 255;
     - `report.py`: 249;
     - `validation.py`: 237;
     - `systems.py`: 236 (the vector fields);
     - `statistics.py`: 174;
     - `__main__.py`: 54.
   - In Tier 2:
     - `ensemble.py`: 470;
     - `pipeline.py`: 450;
     - `allocation.py`: 385;
     - `dynamics.py`: 282;
     - `networks.py`: 242;
     - `experiments.py`: 221;
     - `oracle.py`: 204;
     - `embedding.py`: 119 (the whole file);
     - `estimation.py`: 108.
   - They are partly covered by other evidence:
     - WU-0013's audit of the 14 v1 tests;
     - WU-0005's code-verification tests (RK4 order, k-d tree against brute force, Levina-Bickel on sets of known dimension, LM residuals, the P2 bound);
     - WU-0007's λ validation (the Chua value at the study's parameters is a known limitation);
     - WU-0014's concordance, which maps hypotheses to functions; the main session spot-checked 2 of its 28 discrepancy rows;
     - the DEV-0 regressions, which are regression guards: they show v3 reproduces v1, not that v1 is right.
2. **`tools/ledger.py`** (160 lines, baseline, governance harness). No review record was found. From reading it:
   - `verify` checks only `prev_sha256` and `seq`;
   - deleting the last entries leaves a valid chain;
   - placeholder actors pass;
   - `status` treats an `amendment` with files as a re-adoption.

   Recording the hash of the last ledger line outside the repository at the freeze would close the truncation gap. That is a suggestion, not a requirement.
3. **The seed-sealing script** (`tools/` script named in ROADMAP WU-0004.6).
   - A hook bars agents from it, so I did not read it.
   - The WU-0001 developer read its `make_commitment` function with the Read tool (`WU-0001-seed-provenance.md` line 228), and `seeds.check_commitment`, which was reviewed and tested, uses that function.
   - No record shows a review of the script's drawing and appending path. The owner's review is the only one possible.
4. **WU-0003.10** (`tools/rehearsal_common.py`, 232 lines). It was merged at `2d99ac4` on the evidence of byte-identical golden outputs and the line gate (`GATE-2026-10-17-wu0003-line.md`). No `## Review` or review file was found.
5. **WU-0003.8 fix round 5** (the H1d tie-break rule, `53483c4`, merged at `1ed9e2d`). No review of that round was found. The WU-0003.8d review started at `2c73b5a`, and it found that the golden test had been red since that merge (§32). The later gate (`GATE-2026-10-18-develop.md`) covers tests only.
6. **Tests that have not run, though they are not reviews.**
   - The slow tier has never run as one tier on the current code (C15).
   - `tests/gpu/` does not exist, so the gpu tier passes vacuously (B10).
7. **`.claude/hooks/test_gate.py` and `web_gate.py`.** The owner adopted them as governance (entry 5). No code review is on record. They enforce LPC.PC.7 refusals in the agent environment only, not in the pipeline; the pipeline guard is `seeds.py` and `__main__.py` (Tier 1A).
8. **Dependency pins.** They have not been reviewed since the initial list (§6).
