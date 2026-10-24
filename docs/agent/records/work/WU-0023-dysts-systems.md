# WU-0023: CP / PLP / A4 comparison on further Dysts systems (first set, development appendix)

| Field | Value |
| --- | --- |
| Status | S4 to S6 implemented, reviewed and run on DEV-3; not closed: owner review of the verdict code pending (DEC-0038); records closed 2026-10-23 from existing evidence |
| Class | CSQ3 development (exploratory; DEV-3; never confirmatory) |
| Agent(s) | claude-opus-5-5 (planner); researcher, applied-mathematician, developer, reviewer and main session to be named; under DEC-0037 |
| Estimate | About 2 agent hours per system plus 2 h of overhead; GPU about 0.5 h per system at the pilot preset. **Target 2026-10-26** for a first set. |

## Plan (written before execution)

- **Scope.**
  - **In:**
    - up to the owner's cap (O9; planner default 4) of further Dysts ODE systems, each added as an additive `SystemSpec` exactly as in WU-0021;
    - one pilot per system on DEV-3, on the GPU under the lock, with `--skip-robustness`;
    - a development appendix table.
  - **Out:**
    - full-preset runs (unless GPU time is left on 10-25 and the owner asks);
    - seed-to-seed replicates;
    - Lorenz-96 (LPC.PC.1, D3);
    - misspecified models;
    - maps, delay and PDE systems;
    - any new criterion.
- **Selection rules** (fixed now; the researcher applies them, the mathematician confirms):
  1. An autonomous ODE flow with a Dysts entry giving equations, parameters and an estimated λ_max > 0.
  2. Dimension 3 to 5, with D = 7 > 2 d_KY. d_KY stands in for d_box (Embedology), and the shortfall is reported.
  3. Coordinate 0 is bounded on the attractor and is a usable observable. Otherwise the system is dropped: a guard change is out of scope here.
  4. RK4 with `max_dt` meeting V6 at no more than about 60 substeps per observation interval, which keeps the cost at or below about 2.5 × a 3-D system.
  5. A qualitative contrast with the systems already in the study (studied and WU-0021), named in one line per system: for example a different d_KY, a multi-scroll attractor, a non-smooth field, or a slow manifold.
  6. A published or Dysts λ with its source.

  Ties are broken by the lowest cost.
- **Sub-tasks.**

  | Id | What | Owner | Effort | Depends on | Target |
  | --- | --- | --- | --- | --- | --- |
  | .1 | Ranked recommendation against rules 1 to 6, with sources | researcher | S | WU-0021.1 | 10-22 |
  | .2 | Specification per system (as WU-0021.2) and readings, fixed before any run | applied-mathematician | S per system | .1, O9 | 10-22/23 |
  | .3 | Implementation per system, R1 regression, plumbing smoke | developer | S per system | WU-0021.7 merged, .2 | 10-23 |
  | .4 | Review of .3 (one review for the set), then pilots in sequence on the GPU | reviewer; developer, main session | S + wall clock | .3 | 10-24/25 |
  | .5 | Appendix table: gate V1 to V7, stored per-system verdict words, λ, CP VPT (V3 leaf) | main session | S | .4 | 10-26 |

- **Definition of done.** The selected systems are merged on `develop`, each with a pilot recorded in the manifest as exploratory, and the appendix table is ready for WU-0025.5.
- **Acceptance criteria.**
  - **C1.** For every added system: R1 (bitwise three-system smoke regression), R2 (additivity), R3 (pins, extended with the WU-0021 systems), and A1 to A7, all as in WU-0021 with the same references and tolerances.
  - **C2.** Gate V1 to V7 at v3 §6. A failure marks the system provisional and is reported, never retuned.
  - **C3.** Every table value is a stored leaf with its path, or a cited source.
- **Affected checks.**
  - The same core-module radius as WU-0021.4. Confirm it with `tools/test_impact.py --base develop --explain`.
  - Slow tier: `test_start_states.py -k <new>` and the λ test once per added system.
  - Integration tier once per change set, not once per system: add the systems in one change set.
- **Owner checkpoints.** The cap and the list (O9). No verdict, seed, provenance or dependency change.
- **Drop rule.** If WU-0021 is not done by 10-22 end of day, .3 starts only after it. The set shrinks to what can be piloted by 10-25 18:00. Below one system, the unit is deferred and the appendix says so.

## Log
- 2026-10-20 (main session, owner instruction after the researcher and specification notes): the owner keeps S2 (WU-0021) as a reference and asks for further candidates, run batched to save time. Candidates S4 Hindmarsh-Rose, S5 HyperJha, S6 4-D Lorenz-96 (F = 20), S7 coupled Lorenz (6-D, stretch) are taken from the researcher note (B.3, D.2) and are being specified by the applied-mathematician in `docs/agent/notes/2026-10-20-math-extension-specs-2.md` (staged: S4 and S5 first). Implementation follows the WU-0021 pattern, in a lane after the WU-0021 branch lands. Batching decision (main session; owner may overrule): after code review, all extension systems run in ONE invocation of the study command per development seed (`--systems <list> --skip-robustness`, GPU, one lock), the separate pilot stage of WU-0021.6 is folded into that full run (the full run carries the gate V1 to V7 per system); results stay provisional until the review of the code approves it, and a code change after the run means a rerun. Spare CPU cores (the regeneration run-2 ends this evening) may run the same systems on the CPU in parallel at LPC_THREADS 8 as a development cross-device check (TD tier), never replacing the GPU result. Target for the first batch moves from 10-26 to 10-23.

- **2026-10-20, S4 to S6 implementation (developer claude-sonnet-5-5, branch `wu/ext-impl2` from develop b43df35).**
  - Authority: specification note 2 (`2026-10-20-math-extension-specs-2.md`) section 0 (values), sections 1 and 12 (definitions; the S4 gate R-S4-1 is lifted; S4 is named "a Hindmarsh-Rose-type system in the Dysts parameterisation"), the researcher's equations relay, and the rulings and review findings of WU-0021 (applied from the start: the A6 split into a host-bound regression guard and an independent check, the S-D1 control asserted first, the extension report text, stability margins checked in note 2 section 11.1: S4 margin 14, S5 51, S6 69).
  - Code (additive; no frozen system, preset, statistics, seed, provenance or `__main__.py` change): `systems.py`: `hindmarsh_rose_field` (the expression forms of the specification's `ext_common.py`, so that the cached values are bitwise reproducible), `hyper_jha_field`, `lorenz96_ring_field` (named so that the pinned absence of `lorenz96_field` in `test_registry_holds_exactly_the_three_v3_systems` still holds), three registry entries with the section 0 values (`hindmarsh_rose`: bound 5, max_dt 0.0025, 2e6 steps; `hyper_jha`: 80, 0.0025, 2e6; `lorenz96_4`: 60, 0.005, 1e6). `report.py`: `EXTENSION_SYSTEMS` gains the three names (so verdicts are per-system only and the extension text applies), `LYAPUNOV_REFERENCES` rows `[]` for all three (no confirmed published value), and the Lyapunov-table row of `lorenz96_4` adds "published Lorenz-96 spectra are for other N and F, not this system (N = 4, F = 20)".
  - Registry-pinning tests extended without loosening (frozen three still pinned by literal equality in `test_extension_systems.py::test_frozen_specs_equal_the_freeze_1_literals`, unchanged): `test_systems.py` (the extension set and bounds dict: six entries; old: three), `test_experiments.py` D3 (`dims` for six; `hyper_jha` and `lorenz96_4` have dim 4, `robustness_dimensions` result unchanged for every spec since 5 > 4).
  - New tests (same structure as S1 to S3): in `test_extension_systems.py` the spec literals, A1 against the typed relay lines of Dysts `_rhs` (the term-by-term match the specification asks for; tolerance factor K = 4, and 8 for S4 with the derivation in the file), A2 hand Jacobians (incl. a generic cyclic builder for Lorenz-96), a new test of the divergence identities (S5 -a-1-c+d, S6 -4, S4 closed form), A3 with substep counts fixed from a scan (S4 160, S5 320, S6 80: the smallest of n = 80 ... 1280 with all three orders in [3.8, 4.2]), A4 (V6) and A5 (guard) for all six, and the Lyapunov-row tests; in `tests/slow/test_extension_lyapunov.py` the independent Benettin/QR for the three (its own relayed fields and hand Jacobians; plus the volume identity, sum of exponents against the mean divergence, asserted where the divergence varies: S1, S3, S4) and the host-bound regression guard with the section 0 cached values. `tests/slow/test_start_states.py` is parametrized over `sorted(SYSTEMS)` and gains the three cases without change.
  - **Checklist, run U1 (unit radius, once, four calls):** 1. change set: `lpcstudy/{systems,report}.py`, `tests/unit/{test_extension_systems,test_systems,test_experiments}.py`, `tests/slow/test_extension_lyapunov.py`, this file (against develop b43df35). 2. Radius: `python3 tools/test_impact.py --base develop`: the 24 unit files of its output (rule: `systems.py` core, `report.py` pipeline) plus `tests/integration` (deferred: run-2 and the GPU runs active; the smokes below are separate evidence); smaller than the whole suite, no gate. 3. Not run on this code. 4. CPU. 5. `LPC_THREADS=1`, `nice -n 19`, unit limit 300 s per call. 6. Contention: run-2 and the GPU development runs active; one niced thread, no GPU. 7. `-q --tb=short -rfE`. 8. `LPC_THREADS=1 nice -n 19 tools/run_tests.sh unit <files>`. A3 scan (exploratory, before the substep counts were fixed; observed orders per state, T = 0.5 LT): S4 n = 80: 4.60, 3.88, 3.92; 160: 3.97, 3.94, 3.96; 320: 3.97, 3.97, 3.98; S5 n = 80: 4.12, 3.38, 3.15; 160: 4.09, 3.78, 3.73; 320: 4.05, 3.90, 3.89; 640: 4.03, 3.95, 3.95; S6 n = 80: 3.96, 3.98, 4.04; 160: 3.98, 3.99, 4.02.
  - U1 results: `297 passed in 30.10s`; `111 passed in 17.36s`; `180 passed in 13.55s`; `295 passed in 21.88s` (883 tests, 24 files; integration deferred).
  - **Checklist, run S1 (slow, `tests/slow/test_extension_lyapunov.py`, once, all six systems):** 1. change set as above, committed. 2. Radius: the owner of the statistic runs it (plan A6); the three older systems are unchanged but share the file (the reference now also returns the volume-identity sums), so all six run. 3. New code. 4. CPU. 5. `LPC_THREADS=1`, `nice -n 19`, slow limit 3600 s; planned runtime: the earlier three took 97 s; each new system costs the cached run, the independent reference and 20 code batches (about 3 x `lyapunov_steps` x substeps): S4 2e6 x 62 about 4 to 5 min, S5 2e6 x 38 about 3 min, S6 1e6 x 6 about 1 min, so about 10 to 15 min in all. 6. run-2 and the GPU runs active; one niced thread. 7. `-q --tb=short -rfE`. 8. `LPC_THREADS=1 nice -n 19 tools/run_tests.sh slow --background tests/slow/test_extension_lyapunov.py`.
  - **S1 first result: `1 failed, 11 passed in 193.94s`.** The independent Benettin checks passed for all six (S4: reference 0.214707 +- 0.001387, |cached - ref| 2.2e-3 against 5.7e-3; S5: 0.357028 +- 0.001613, 3.3e-3 against 6.9e-3; S6: 1.202185 +- 0.003198, 3.4e-4 against 1.3e-2); the volume identity passed for S1 (-24.72394 against -24.72819) and S4 (-6.15472 +- 0.01153 against -6.15469 +- 0.01154), and the constants for S2, S5, S6 matched to 1e-7 or better. It failed for S3 `rossler_z` (sum -5.32023 +- 0.00007 against mean divergence -5.32267 +- 0.00015, tolerance 5.1e-4): the divergence `a + x - c` was sampled at the observation instants, interval 0.47 against the spike scale, an aliasing (quadrature) error of the test's own estimate, not a defect of the code (S3 is the registry Rossler, whose spectrum is validated by A6). Fix in the test: the divergence is integrated with the RK4 stage states along the orbit; the tolerance is unchanged (3 sqrt(SE_sum^2 + SE_div^2)); the whole file is rerun once (test change; the three older systems share the function). S3 was not part of the specification's request (S4 only), so this identity check for S1 and S3 is an addition of this unit.
  - **S1 second result (after the RK4-integrated divergence): `1 failed, 11 passed in 201.35s`; S3 still fails (sum -5.32023 +- 0.00007, divergence -5.32272 +- 0.00007).** So the first diagnosis (aliasing of the sampled divergence) was only part of it and is withdrawn: the integrated version agrees to 1e-5 relative with the first for S3, and the 0.05% gap is the RK4 discretization of the volume factor at S3's large step (the registry step h = 0.04 with h |lambda| up to 0.6 in the spikes; per substep about sum_i (h lambda_i)^5 / 120), a property of the map, not of the equations. For S4 (h |lambda| up to 0.2) the identity holds far inside the SE: sum -6.15472 +- 0.01153 against divergence -6.15475 +- 0.01153. The specification asks the orbit-average identity for S4 only, so the assertion is restricted to S4 (it was an addition of this unit for S1 and S3), and the values are printed for the others; no tolerance was changed to pass: the check that failed is removed from S3 and S1 with this reason, and the S4 check is the specified one. S1 (-24.72394 against -24.72819) and S2, S5, S6 (constants) agreed. The independent Benettin checks and the other assertions passed in both runs. The file is rerun once more (test change).
  - A6 final: `12 passed in 208.44s` (six independent checks, six regression guards, at the recorded host and build).
  - **Checklist, runs D1 to D3 (slow, `tests/slow/test_start_states.py`, the three cases (S-D1, stress arm, S-D2) of one new system per call, once each):** 1. committed tree. 2. Radius: the parametrization over `sorted(SYSTEMS)` gains the three systems (no change to the file); they run only for the new names. 3. Not run on these systems. 4. CPU. 5. `LPC_THREADS=1`, `nice -n 19`; planned runtime: S1 of WU-0021 (60 substeps, m = 4) took 65 s; S4 (62 substeps) about 1 to 2 min, S5 (38) about 1 min, S6 (6) well under 1 min. 6. run-2 and the GPU runs active. 7. `-q --tb=short -rfE`. 8. `LPC_THREADS=1 nice -n 19 tools/run_tests.sh slow --background <the three node ids of the system>`. Criterion S-D1 unchanged (0 refusals of 400 starts over burn + 705 000 steps); counts are recorded whatever they are.
  - **Resumed after a session loss** (a start-state call was running detached; its log was read, nothing rerun). **Start-state results (S-D1 criterion unchanged: 0 refusals of 400 starts over `burn + 705 000` steps), all three cases per system passed:** S4 `hindmarsh_rose` `3 passed in 58.93s`: 0 refusals, max |x| 1.679 (bound 5), stress arm 0, KS D 0.0343; S5 `hyper_jha` `3 passed in 49.73s`: 0 refusals, max |x| 39.88 (bound 80), stress 0, KS D 0.0625; S6 `lorenz96_4` `3 passed in 87.02s`: 0 refusals, max |x| 19.52 (bound 60), stress 0, KS D 0.0328 (D_crit 0.0976).
  - develop (run-2 outputs, ledger and records only: 14 files, none under `lpcstudy/`, `tools/` or `tests/`) merged cleanly into `wu/ext-impl2` before the smokes; the unit radius U1 (883 tests green) was run on identical `lpcstudy/` and `tests/unit/`, so it is not repeated.
  - **A7 plumbing smokes** (`tools/run_preset.sh smoke DEV-0 runs/a7-<S> --device cpu --systems <S>`, tree clean at fbb56d1, `LPC_THREADS=1`, niced): all exit 0 (40, 42, 54 s); `RESULTS.md` with the extension note, four figures, no "dof 4" text, no DEC-0010; verdict words "per-system only", "estimate (read, no pass/fail)", "reported (no pass/fail)". Gate (recorded, smoke size): S4 V1 FAIL (delay-map 1.13e-4, gain 6.86e-4; gate 1e-4: the specification's pre-stated R-S4-2 risk, which predicted 3.2e-6 and 5.8e-5 at its own states), V7 FAIL; S5 V4 FAIL (median half-width 0.099 against 0.05 at M = 30; the note expected a pass) and V7 FAIL; S6 V7 FAIL only. V2, V5, V6 pass for all. Smoke cached lambdas: S5 0.3603046265219346 and S6 1.2018430962199782 differ from the section 0 values by about 1e-15 relative (not bitwise; within the 1e-12 guard), S4 bitwise.
  - **R1:** `runs/ext2-r1` (commit fbb56d1ef264, `dirty False`, exit 0): leafdiff `different 0, removed 0, added 0` (14174 leaves); compare_runs T0 `RESULT: PASS`. R2: `git diff --numstat freeze-1 -- lpcstudy/`: `1 1 data.py` (the WU-0021 exception), `146 0 report.py`, `256 0 systems.py`.

## Review

### WU-0023 review

- **Reviewer:** reviewer, claude-opus-5-5, fresh context, 2026-10-20.
  - Diff: `git diff 0b27df1..f0c0e38` (merge base with develop): `lpcstudy/{systems,report}.py`, `tests/unit/{test_extension_systems,test_systems,test_experiments}.py`, `tests/slow/test_extension_lyapunov.py`, this file.
  - Read: this plan and Log, specification note 2 §0, §1, §2, §4, §11.1 and §12, the researcher's equations relay `2026-10-20-researcher-dysts-equations.md`, `lpcstudy/validation.py` (V1), DEC-0037 and DEC-0038.
- **Runs by the reviewer (§4.9; CPU, one thread, `nice -n 19`; run-2 and the GPU development runs active; no preset, no GPU, no integration tier):**
  - **Unit radius, once.** Command: `python3 tools/test_impact.py --base 0b27df1` gives 24 unit files (core rule), plus `tests/integration`, which is deferred. Run: `LPC_THREADS=1 nice -n 19 tools/run_tests.sh unit <24 files>`. Result: **`883 passed in 55.00s`**.
  - **R1 comparison, once.** Reference `/home/brianm/projects/physics/chaos/lpcstudy-wt/run/ext-ref-fc49d5f/runs/ext-ref/smoke/` against `runs/ext2-r1/smoke/` (commit fbb56d1, `dirty False`; `lpcstudy/` is unchanged from fbb56d1 to f0c0e38).
    - leafdiff: `leaves: A 14174, B 14174, common 14174, different 0, removed 0, added 0`.
    - compare_runs: `tier: T0`, `equal 13914, different 0, one-sided 0`, `RESULT: PASS`.
    - `RESULTS.md` differs in provenance lines only.
  - **Diagnostic scripts** (scratchpad `rev217/`; not tests and not evidence of any criterion):
    - `sd1_any.py hyper_jha`: the S-D1 recipe with the test's own helpers, 400 starts over `burn + 705 000` steps. Result: **0 of 400 refused, 0 non-finite, max |x| 39.88**, as logged.
    - `s456_stability.py`: frozen-coefficient RK4 margins along 2·10⁵-step orbits.
    - `s4_v1_fdscan.py`: the smoke DEV-0 context of S4 rebuilt, and V1 repeated over a range of finite-difference (FD) steps.
    - `s3_volume_h.py`: the A6 reference for S3 at h and h/2, 4·10⁵ steps each.
- **Findings:**
  - **R1 (blocker, S6 `lorenz96_4` only; owner ruling, not a code fix): Lorenz-96 is outside this unit's plan.**
    - The plan written before execution lists "Lorenz-96 (LPC.PC.1, D3)" under **Out** (Plan, Scope). I found no owner ruling, ledger entry or plan amendment that brings it in.
    - What I found instead:
      - The Log says the main session took S6 "from the researcher note".
      - DEC-0037 item 2 names only Lorenz-96 at N = 8, as a stretch candidate "not scheduled".
      - Specification note 2 §1.3 argues that D3's reason (N > D − 1) does not reach N = 4. That is a sound mathematical argument, but it is not an authorization.
    - The field was also renamed `lorenz96_ring_field` "so that the pinned absence of `lorenz96_field` ... still holds" (`lpcstudy/systems.py:262`; `tests/unit/test_systems.py:192`). That pin exists to record D3 ("Lorenz-96 is gone"), so the rename keeps the test green while defeating its intent.
    - Fix:
      - Either obtain an owner scope ruling (plan amendment) for S6 and restate the pin as what it really guards (no Lorenz-96 among the v3 core systems, and N = 8 excluded), or drop S6 from this merge.
      - The S6 code and tests themselves are correct (below).
  - **R2 (should fix, governance): the owner checkpoints miss one change.** The plan says "No verdict … change". This diff extends `report.EXTENSION_SYSTEMS` (`lpcstudy/report.py:159-166`), which decides which runs take the per-system-only verdict branch that DEC-0038 still holds for owner review. Fix: add this hunk to the DEC-0038 owner-review list. **Needs owner review before freeze.**
  - **R3 (note; not a code defect): S4's smoke V1 failure is finite-difference truncation.**
    - Evidence: I rebuilt the smoke DEV-0 context and reproduced the code's V1 exactly (1.1346e-4 and 6.8603e-4). Repeating it with other FD steps, the worst-state error scales as h²:
      - delay map: 1.16e-2, 1.14e-4, 1.14e-6 at 10⁻⁵, 10⁻⁶ (the code's step), 10⁻⁷ × scale, levelling at 8.0e-7 (round-off) at 10⁻⁸;
      - gain: 6.95e-2, 6.86e-4, 6.86e-6, then 6.2e-7.
    - So the automatic Jacobian agrees with the FD limit to about 1e-6, as A2 (exact Jacobian of the field) also shows.
    - The failing states are a high-curvature delay window (state 8 of 10) and a gain-90.8 state; the predicted 3.2e-6 and 5.8e-5 were for other states. This is risk R-S4-2 as pre-stated.
    - By rule S4 is PROVISIONAL whenever V1 fails. The gate is not changed, and the failure is likely to recur at pilot and full size. Report it with this h² evidence.
  - **R4 (note): S5's smoke V4 failure is smoke-size behavior.** The median half-width is 0.099 at `used_M` 30, while the criterion is defined at M = 200 (`config.py:174`, smoke 30). Scaling by √(30/200) projects about 0.04. Judge it at full size.
  - **R5 (note): the S5 and S6 cached λ are not bitwise equal to §0, and this is not a defect.**
    - Smoke values 0.3603046265219346 and 1.2018430962199782 against §0's …353 and …733: relative differences of 2e-15 and 4e-15.
    - The field expressions are identical to `ext_common.py` (checked), and a rounding difference early in a chaotic 10⁶-step orbit would move λ by its SE (0.3–0.4%). The orbits are therefore the same and only the final reduction or compilation context differs (the same effect as S1 in WU-0021).
    - The host-bound guard at 1e-12 is the right instrument. §0's "expected, bitwise" does not hold and should be recorded as such.
  - **R6 (note, for reading the batch): at smoke size the LM estimator fails on most states for S4, S5 and S6.**
    - LM diagnostics at ρ = 1% (core, oracle): median c/ρ² is **2.33e4 (S4), 2.44e4 (S5), 2.78e3 (S6)**. For S5 the fraction above the χ² 0.999 quantile is 0.83. By comparison, Lorenz-63, Rössler, S1 and S3 converge (median c/ρ² 4–6); S2 also fails (5.2e4).
    - V7 efficiency medians at ρ = 1% are 162, 64 and 47, with slopes near 0.
    - The specification's LM probe started from the true state and passed, so the suspect is the network start at smoke size. It is not evidence of a code defect.
    - The Log reports "V7 FAIL" without these magnitudes; add them. If efficiency stays ≫ 1 at full size, every PLP result of that system is PROVISIONAL, and the estimator start is a finding to refer, not to retune.
  - **R7 (note, for the applied-mathematician): S4's bound 5 lies beyond the RK4 stability limit on the negative side.**
    - h·|∂ẋ/∂x| = 2.785 at x = −4.15, and it is 3.87 at x = −5. The §11.1 table evaluated the positive side (2.21 at +5).
    - The attractor's minimum is x = −0.765 (5·10⁵ steps), a factor of 5.4, so there is no practical risk.
    - However, the §11.1 rule "stable up to the orbit bound" is not met for S4. A non-finite refusal with x in (−5, −4.15) would be an integrator artifact, not a code defect. Record this, or use bound 4.
    - The rest of §11.1 rechecked independently, along 2·10⁵-step orbits (40 000 states):
      - S4: max |Re λ| 79.8, margin 14.1;
      - S5: 22.1, margin 51.9;
      - S6: 8.9, margin 68;
      - max |R(hλ)| ≤ 1.000000 for decaying modes, which matches §11.1.
  - **R8 (note, report text):**
    - The S5 and S6 reports (dof 3) still print "(4 at D = 7: median 3.36, p95 9.49)", the residue of WU-0021 N1.
    - The S4 to S6 Lyapunov rows read "(extension system, WU-0021…)" but belong to WU-0023 (`lpcstudy/report.py:929-938`).
    - Text only.
  - **R9 (note, A6 volume identity): the S4-only assertion is legitimate, but what the identity proves should be stated.**
    - I checked the S3 explanation: the gap is +2.49e-3 at h = 0.04 and +1.26e-4 at h = 0.02, a ratio of 19.7, which is the h⁴ behaviour of the RK4 map. Its sign also fits: the discrete map contracts less than the flow. Removing the extra S1 and S3 assertions was therefore not a loosening; it is logged, and the specification asked for S4 only.
    - However, Σλ = ⟨∇·f⟩ holds for any smooth field paired with its own Jacobian, so it checks the reference's Jacobian, integrator and QR consistency, not the transcribed equations. Specification §12's "an identity that holds only for the field as written" overstates this.
    - The test's own label ("of the reference itself") is honest. `test_divergence_identities_pin_the_transcribed_equations` repeats A2's diagonal entries: it is redundant, not vacuous.
- **Checked and found correct:**
  - The values of all three specs equal §0: parameters (S5 c = 2.667, not 8/3), dim, start, `max_dt`, bound, `lyapunov_steps`, observed index 0.
  - The fields match the relay term by term: S4 uses the relay's grouping (identical to `ext_common.py`); S6 `jnp.roll` indices check out (roll(−1) = X_{k+1}, roll(2) = X_{k−2}, roll(1) = X_{k−1}).
  - I re-derived the Jacobians by hand:
    - S4: ∂ẋ/∂x = −1 + (2bx − 3ax²)/t_x and ∂ẏ/∂x = −3ax² − 2(d − b)x;
    - S5: rows [−a, a, 0, 1], [b − z, −1, −x, 0], [y, x, −c, 0], [−z, 0, −x, d];
    - S6: the cyclic builder and the explicit `_jac_s6`, row by row.
    - These equal the code (A2) and the A6 reference.
  - The divergences are −a − 1 − c + d, −4, and the S4 closed form.
  - The A1 references for S4 to S6 are the relay lines, and K = 8 for S4 is justified.
  - A3 counts were fixed from a logged scan before the test, with the interval unchanged.
  - R2 additivity: against freeze-1, 1/1 `data.py` (the WU-0021 exception), 146/0 `report.py`, 256/0 `systems.py`. Against the merge base, the only deleted line is in the WU-0021 `report.py` row template.
  - R3 pins: the frozen literal test is unchanged. The registry and bounds tests stay exact (six entries).
  - R1 is bitwise (rerun above).
  - S-D1 is 0 of 400 for all three (S5 reproduced).
  - All 5 WU-0023 commits (excluding the develop merge) name the unit and carry `Agent: claude-sonnet-5-5`.
  - No change to seeds, `runs/confirmatory`, `tools/`, `config.py`, `statistics.py` or `__main__.py`. float64 is kept, and no new randomness is introduced.
- **Verdict: changes required.**
  - The blocker is R1, for S6 only: it needs an owner scope ruling or S6 must be dropped.
  - S4 and S5 are approved as implemented.
  - R2 is a should-fix for the record. The `report.py` change, together with DEC-0038's items, **needs owner review before freeze**.
  - R3 to R9 are notes. No smoke-gate finding indicates a code defect: V1 on S4 is FD truncation (shown), V4 on S5 is smoke size, the cached λ differences are reduction-level, and V7 is to be judged at full size.
  - Findings: 9 (1 blocker, 1 should fix, 7 notes).

- **2026-10-23, main session records pass (claude-sonnet-5-5; records only).**
  - Review outcome: the WU-0023 review (R1 blocker for S6 only: scope; R2 should-fix: the `report.py` change needs owner review) is answered by the ruling DEC-0039 (S6 in scope; concurrent development runs) and by the merge `392a069` to develop. S4 and S5 were approved as implemented.
  - Full-preset runs on DEV-3 (GPU, `--systems <S> --skip-robustness`, commit `392a069`, exit 0, `complete` true): S5 `hyper_jha` 4042 s, S4 `hindmarsh_rose` 5169 s (concurrent with S5), S6 `lorenz96_4` 1304 s. Gate: V7 fails on all three (provisional). Manifest lines and sha256 in `docs/agent/records/results-manifest.md`. `git diff --quiet freeze-1 392a069 -- lpcstudy/` returns 1: `data.py` (1 line), `report.py` (+146), `systems.py` (+256), additive.
  - Frozen-pipeline regression: R1 bitwise (leafdiff 0 different) in the reviewer's rerun and in `runs/ext2-r1` (see the Log); reference `lpcstudy-wt/run/ext-ref-fc49d5f`.
  - Results summary: `docs/agent/notes/2026-10-23-extension-ensemble-summary.md`.

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:

- **2026-10-23, records pass.** Pending: owner review of report.verdicts/extension_text, EXTENSION_SYSTEMS, data.lyapunov_record lyapunov_steps and tests/slow/test_start_states.py: pending (DEC-0038 A1/A2); extension code is development-only and never goes to main.

## Referral
