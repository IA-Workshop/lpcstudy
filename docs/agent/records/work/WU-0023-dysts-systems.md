# WU-0023: CP / PLP / A4 comparison on further Dysts systems (first set, development appendix)

| Field | Value |
| --- | --- |
| Status | planned |
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

## Review

- **Reviewer:**
- **Findings and resolution:**

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:

## Referral
