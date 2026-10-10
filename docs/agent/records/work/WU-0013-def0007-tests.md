# WU-0013: DEF-0007 audit of the 14 v1 tests, and fixes

| Field | Value |
| --- | --- |
| Status | in progress |
| Class | CSQ3 development |
| Agent(s) | claude-sonnet-5-5 (main session) under governance ledger entry 5 (authorizations 4, 6) |
| Estimate | WU-0013.1 M, .2 S (ROADMAP.md §2) |

## Plan (written before execution)

- **Scope:** ROADMAP.md §2 phase A, WU-0013.1 and .2. In: the 14 v1 tests (now in `tests/unit/test_{allocation,analysis,dynamics,embedding,ensemble,oracle,statistics}.py`; not the marker tests of WU-0010 or the tool tests of WU-0011). WU-0013.1 is an audit by the reviewer that touches no test; WU-0013.2 is the developer's fixes. Out: `lpcstudy/`, governance, and any change to a tolerance that makes a test easier to pass.
- **Definition of done and acceptance criteria** (verbatim from ROADMAP.md §2, fixed before execution, VV.3):

| Id | Definition of done | Acceptance criteria (checkable) |
| --- | --- | --- |
| WU-0013.1 | `docs/agent/records/audits/<date>-def-0007-tests.md` lists all 14 tests with reference, independence and tolerance status | Every test is classified `reference`, `regression guard` or `defective`; each `reference` row names the reference kind from LPC.PC.21a. Tests found self-referential are listed for WU-0013.2. The audit touches no test. |
| WU-0013.2 | Every test has a docstring naming its reference and tolerance justification (`.claude/rules/tests.md`) | All 14 tests pass; `git diff` shows no tolerance that grew (reviewer checks each numeric literal in an `assert` or `approx`); DEF-0007 gets a dated `resolved` line with the audit path. |

- **Affected checks:** WU-0013.1: none (no test or code is touched). WU-0013.2: the test files it edits, per §4.2, unit tier (the 14 tests live in 7 files; the radius is those files). The audit file is `docs/agent/records/audits/2026-10-10-def-0007-tests.md`.
- **Owner checkpoints (LPC.PC.11):** none (no verdict, statistics, seed, provenance or dependency code).
- **Order:** .1 (reviewer), then .2 (developer), then independent review of .2 by a reviewer other than the .1 auditor where possible.
- **Note for the audit:** a test marked `reference` must name an independent reference (closed form, brute force, a published value, a conservation law or a property check, LPC.PC.21a); a test that checks a function against itself or against a copy of the same formula is `defective`; a test that pins current behaviour is a `regression guard` and is renamed `test_regression_*` in .2 (renaming a test is not a change of its assertions).

## Log

<dated entries: what was done, commands, results, commits>

- **2026-10-10, WU-0013.1 audit** (`reviewer`, claude-opus-5-5, fresh context, worktree `wu/0013-def0007-audit` at `0da91a7`).
  - **What was audited.** All 14 v1 tests in `tests/unit/test_{allocation,analysis,dynamics,embedding,ensemble,oracle,statistics}.py`, plus `tests/unit/unit_helpers.py`, together with every `lpcstudy` function they call. The audit is in `docs/agent/records/audits/2026-10-10-def-0007-tests.md`.
  - **Result.** 13 `reference`, 0 `regression guard`, 1 `defective`.
    - **Defective:** `test_dynamics.py::test_observability_matches_independent_jacobians` copies the ν formula of dynamics.py:220–222 at test L32. It also shares the delay-index expression through `delay_map_forward`.
    - **Weak or uncited `reference` tests, listed for WU-0013.2:** `test_delay_and_acf` (the AMI band is uncited and wider than its own docstring) and `test_logrank_detects_difference_and_not_null` (no check of the p-value's value).
  - **Docstrings.** None of the 14 docstrings states both a reference and a tolerance justification. All 14 are listed for WU-0013.2, with fixes that loosen no tolerance.
  - **What was not run or changed.** No test was run (WU-0013.1 needs none). No test or `lpcstudy/` file was touched. The Monte Carlo error figures in the audit are scratch NumPy arithmetic, run without importing `lpcstudy`.

- **2026-10-10, WU-0013.2 developer, pre-run checklist (DEVELOPMENT_WORKFLOW.md 4.9), run 1** (claude-sonnet-5-5).
  1. **Change set:** `git status --porcelain` shows `M tests/unit/test_{allocation,analysis,dynamics,embedding,ensemble,oracle,statistics}.py`; `git diff --name-only main...HEAD` shows only the two WU-0013 records. No `lpcstudy/` file, no `unit_helpers.py`.
  2. **Radius:** `tools/test_impact.py --explain`: rule "test file: that file only" for each of the 7 edited files, tier `unit`; no module changed, so no importing test files are added. Smaller than the whole suite.
  3. **Already run?** No: first invocation of this code.
  4. **Device:** `JAX_PLATFORMS=cpu`, `XLA_PYTHON_CLIENT_PREALLOCATE=false`.
  5. **Threads and time:** `LPC_THREADS=4` (OMP/MKL/OPENBLAS=4); unit timeout 300 s.
  6. **Contention:** no GPU, preset or slow run involved.
  7. **Output:** `-q --tb=short -rfE`; only the summary and failures recorded.
  8. **Command:** `JAX_PLATFORMS=cpu XLA_PYTHON_CLIENT_PREALLOCATE=false OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 timeout 300 .venv/bin/python -m pytest -q --tb=short -rfE <the 7 files>`.

- **2026-10-10, WU-0013.2 developer** (claude-sonnet-5-5), worktree `wu/0013-def0007-audit`, on top of `cbb0a35`.
  - **Files changed (tests only; no `lpcstudy/`, no `unit_helpers.py`):** `tests/unit/test_{allocation,analysis,dynamics,embedding,ensemble,oracle,statistics}.py`.
  - **Command and result (run 1, the only run):** the command of the checklist above gave `29 passed in 4.18s`. No failure, no rerun. The 14 original assertions are kept (see the table); 15 tests were added or split off, so 29 tests run.
  - **Scratch checks (plain NumPy, not pytest, no tolerance chosen from a test result):** I recomputed the audit's error figures before writing the docstrings: delta-method SE for #1 8.3e-4; linearized SE for #2 5.8e-4 and 1.7e-3 on the test's own 500 states; #7 relative SE 1.89e-3 and bias -2.5e-5; #11 Greenwood SE at expected counts, max 2.34e-3 at H = 8 and 1.74e-3 at H = 40 (20.5 at risk); #12 expected chi-square 113; #14 SE 0.0141. All agree with the audit. For #4 I computed cond(A^T A) = 21.3, 28.3, 30.3 at the three Lorenz states (cond(Q) = 6.6e7, 4.6e7, 3.0e7), and for the new linear system cond(A) = 2.8, cond(A^T A) = 8.1, cond(J_G) = 1.6, cond(Q) = 1.9, rank(A) = 3. The tolerances of the new tests were set from these before running. `select_delay` currently returns 5 steps (0.184 time units); `tools/test_impact.py` selected the radius.
  - **Tightening not applied.** The audit offers tighter values for #1 (2.5e-3), #2 (3e-3, 7e-3), #7 (6e-3), #8 (3e-4) and #14 (0.043). It marks all current values sound (S: yes), only undocumented (J: no). I kept every current tolerance and documented it, so no tolerance changed. #6a is not tightened either (see below).
  - **Per test.**
    - #1 `test_closed_form_matches_uncorrelated_isotropic_case`: expected value is now the inline `delta**2 / (eps**2 + delta**2)`; docstring gives the delta-method SE; `abs=5e-3` unchanged. New `test_closed_form_weight_exact_values` checks `closed_form_weight` against 81/97 and three edge values (rel 1e-14).
    - #2 `test_seed_proxy_recovers_parameters`: docstring only (reference: manufactured (2, 3); tolerances 34 and 29 SE).
    - #3 `test_per_state_spearman_handles_ties`: docstring only (hand values; 0 is the documented convention for an undefined correlation). New `test_per_state_spearman_partial_ties_and_non_monotone`: 3/sqrt(10) and 4/5 by hand.
    - #4 renamed `test_regression_observability_matches_ad_jacobians`; body and `rel=1e-8` unchanged; docstring says regression guard and gives cond(A^T A). New independent tests: `test_observability_linear_system_matches_pinv` (linear map, reference by `matrix_power` and `pinv`, rel 1e-11), `test_observability_scalar_geometric_closed_form` (hand closed form for D = 2, 3, 5, rel 1e-12), `test_delay_map_forward_matches_delay_vectors` (ties the delay-index expression to `delay_vectors`, atol 1e-12, with its own non-symmetry premise).
    - #5 `test_delay_vectors_order`: docstring only.
    - #6 split into `test_regression_ami_delay_lorenz_band` (assertion `3 <= delay <= 8` unchanged, relabelled a regression guard because the "0.15-0.2 time units" source is uncited and no source is verifiable without web access) and `test_autocorrelation_time_sine_is_censored` (`== 500` unchanged, envelope bound 0.975 > 1/e documented). The band is neither tightened nor widened. **Open:** `/verify-citation` (or the `researcher`) for the AMI first-minimum delay of Lorenz-63 x, with estimator and bin count; with a citation the band can be tightened and the name changed back.
    - #7 `test_retrieval_spread`: docstring only (SE 1.9e-3, bias -2.5e-5, 10.6 SE).
    - #8 `test_oracle_weight_minimizes_ensemble_mse`: docstring only (grid bound 2.5e-4; atol 1e-3 kept). New `test_oracle_weight_clips_to_boundary`: exercises both clip branches, checks the premise (raw w* < 0 and > 1), exact equality with the grid argmin.
    - #9 `test_regret_identity`: classified as the audit says (reference, partly independent), docstring only. New `test_regret_identity_matches_draws`: V computed from the raw draws, anchors `hybrid_mse` to data (atol 1e-12).
    - #10 `test_characteristic_horizon_and_censoring`: docstring only. New `test_characteristic_horizon_noise_in_quadrature` (noise 0.19, expected [2, 4] and [True, False]) and the `ValueError` branch.
    - #11 `test_kaplan_meier_matches_geometric_survival`: docstring only (4.3 SE).
    - #12 `test_logrank_detects_difference_and_not_null`: docstring only (chi-square 113, 1e-3 false-failure probability). New `test_logrank_hand_worked_ties_and_censoring` (hand sums O-E = 5/7, V = 97/98, p = erfc(sqrt(25/97)), rel 1e-12) and `test_logrank_matches_scipy` (`scipy.stats.logrank` exists in SciPy 1.18.1 and uses the same tie-corrected variance; two data sets, one censored with ties; rel 1e-10).
    - #13 `test_holm`: docstring only; "textbook" dropped because no source is cited (derived from the definition). New `test_holm_clip_at_one_and_ties`.
    - #14 `test_partial_correlation_removes_confounder`: docstring only (SE 0.0141; 0.05 is 3.5 SE). New `test_partial_correlation_nonzero_closed_form`: 1/sqrt(2) and -1/sqrt(2), abs 0.03 (4.2 SE).
  - **Disagreements with `lpcstudy/` code:** none. The hand-worked log-rank case, `scipy.stats.logrank` (both data sets), the pinv and closed-form observability references, and the draws-based regret identity all agree with the code inside the stated tolerances. No `lpcstudy/` file was changed.
  - **Self-check.** Grep of the diff for `clip|nan_to_num|isfinite|where(|try:|except` finds only words in docstrings and `oracle_weight(..., clip=False)` calls; there is no handling in test code to count. `default_rng` appears only as `np.random.default_rng(<int>)` with fixed integers (DEVELOPMENT_WORKFLOW.md 4.7). Sensitivity of the hand log-rank case: without the tie factor the same data give p = 0.540 against 0.473.
  - **Numeric literals in `assert` or `approx`, old -> new (no value grew).**

| Test | Old literal | New literal |
| --- | --- | --- |
| #1 closed_form_matches | `abs=5e-3` | `abs=5e-3` (expected value now inline) |
| #2 seed_proxy | `2.0, rel=0.02`; `3.0, rel=0.05` | same |
| #3 spearman ties | `[0.0, 1.0, -1.0]`, allclose defaults | same |
| #4 observability (regression) | `rel=1e-8` | `rel=1e-8` |
| #5 delay_vectors_order | `[[10.0, 7.0, 4.0]]` | same |
| #6a AMI band | `3 <= d <= 8` | same |
| #6b ACF sine | `== 500` | same |
| #7 retrieval_spread | `== 0.0`; `1.0, rel=0.02` | same |
| #8 oracle_weight | `atol=1e-3` | `atol=1e-3` |
| #9 regret identity | allclose defaults | same |
| #10 characteristic horizon | `[3, 4]`, `[True, False]` | same |
| #11 Kaplan-Meier | `< 0.01` | `< 0.01` |
| #12 logrank | `< 1e-6`; `> 1e-3` | same |
| #13 holm | `[0.03, 0.06, 0.06]`, allclose defaults | same |
| #14 partial correlation | `< 0.05` | `< 0.05` |
| new tests | none | `rel=1e-14`; `atol=1e-12` (Spearman, regret, delay map); `rel=1e-11`, `rel=1e-12` (observability); `rtol=0` with `atol=1e-15` (Holm); `rel=1e-12`, `rel=1e-10` (log-rank); `abs=0.03` (partial correlation); exact equality (clip, horizon) |

## Review

- **Reviewer:** <actor, not the author>
- **Findings and resolution:**

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:

## Referral

<only if halted; use the form in agent-instructions.md, LPC.AI.13>
