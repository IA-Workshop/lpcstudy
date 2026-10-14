# WU-0003: Development rehearsal and precision report

| Field | Value |
| --- | --- |
| Status | planned |
| Class | CSQ3 development. Its precision estimates inform the owner's sample-size decision (LPC.PC.5). |
| Agent(s) | — |

## Plan

**Scope.**

1. **Rehearsal.** Run the v2 code at the pilot preset on `DEV-1`, on the owner's GPU, under LPC.AUTH.3.
2. **Optional full-preset run.** If time allows, run the full preset on `DEV-2`, within the 12-hour per-run limit of LPC.AUTH.3.
3. **Precision report** at `docs/study/dev_rehearsal_report.md`, labeled `DEVELOPMENT: not a hypothesis test`. For every v3 criterion it gives:
   - the interval half-width at the rehearsal size;
   - the half-width projected to the full preset;
   - which verdicts are reachable.

   It covers the H3c interval in particular, since the pilot had none.
4. **Reproducibility tolerance.** Run one core cell twice on GPU, and once on CPU with the same seed. Record the largest absolute and relative differences in w*, the seeds and the verdict statistics. Propose the tolerance that LPC.PC.18 declares, at about ten times the observed GPU-to-GPU variation.

**Out of scope:** looking at any confirmatory data; changing any criterion. A finding that a criterion is undecidable is reported to the owner, not fixed.

**Definition of done.** The report exists, the tolerance is proposed, and the owner has the information for the sample-size and freeze decisions.

**Acceptance criteria.**

- The run completes with the validation gate passing on all three systems, or the failure is reported.
- The report's numbers are regenerated from the run's `results.json` by a script committed with the unit (REPRO.10).
- Every number in the report states its seed id.

### Plan amendment 1 (2026-10-12, planner claude-opus-5-5; direction DEC-0026 item 10)

Everything above stays in force. This section adds to it and is fixed before any rehearsal output exists (VV.3). Basis: ROADMAP WU-0003.1 to .6, WU-0004 and WU-0016.3; DEC-0006, DEC-0018 O4, DEC-0019, DEC-0020, DEC-0022, DEC-0023 F1, DEC-0024 (M3, M5, follow-ups), DEC-0025 (M7, D2, D3), DEC-0026; DEF-0017, DEF-0023, DEF-0024; WU-0002.11e §5 and §8; WU-0005.5 M8 and M9.

**A1. Measured resources (this replaces the dev-run skill's "70 min on 2 cores").**
- The v3 pilot on DEV-0 took 1980 s on CPU at `LPC_THREADS=8`, with a peak RSS of 3.25 GB. Per system: Lorenz-63 248 s, Rössler 296 s, Chua 763 s, robustness about 660 s. The 5493 s figure is the v1 local re-baseline, whose code also runs transfer, Lorenz-96 and the shift experiments.
- Full against pilot: states 1400 → 4000 per system (×2.86), sweep 300 → 1000 (×3.3), estimator pairs × epochs ×4, B ×4, eval draws ×2. M = 200 is unchanged.
- Estimate for the full preset on CPU: about 1.7 to 2.2 h, with a planning upper bound of 4 h and a peak RSS of 10 GB or less. The full preset therefore does **not** need the GPU or days of CPU.
- The GPU speed is unmeasured. Part of the work, the k-d tree and the numpy code, stays on the CPU. WU-0003.1 measures it.

**A2. Preconditions: merged to `develop` and gated, in this order.** The rehearsal commit `C_R` is a `develop` commit that has passed a merge gate.
1. DEF-0025 (`d > spec.dim`) and the WU-0011.5 tooling fixes. Numbers unchanged.
2. WU-0002.11e implementation (clip-sensitivity leaves; bitwise-neutral, V1 of its §6). The rehearsal gives its first counts above smoke size.
3. WU-0002.11c, the diverging-orbit guard (DEF-0015).
4. The start-state unit (DEF-0017) together with WU-0002.11d (the `default_rng` conversions, DEF-0011). This is the one step that changes numbers. It ends with a regenerated DEV-0 pilot on CPU, which becomes the reference, and its comparison with the 2026-10-11 local baseline (DEC-0019/0020). v3 §8 ("fresh … trajectories") requires this step.
5. WU-0005.6, the LM 15-against-30 study (DEC-0025 D2), reported on the post-seed code. If the owner changes the iteration count, which is a v3 change, it lands before `C_R`.
6. New sub-tasks WU-0003.7 to .9 (below) merged. Every change merged after step 4 must show 0 changed leaves on the DEV-0 smoke.
7. A merge gate on `develop` at `C_R` (DEC-0026 (c)).

WU-0005.4, .5 (P2(c)), WU-0008.3 and DEF-0010 (`sklearn_seed`) are already on `develop`. The Option C switch (DEC-0026 item 2) is needed for the freeze, not for the runs.

**A3. New sub-tasks** (the owner appends them to the ROADMAP).

| Id | What | Owner | Bitwise-neutral? |
| --- | --- | --- | --- |
| WU-0003.7 | Per-state dump (opt-in, `states/<system>.npz`, outside `results.json`), as listed below; split-half moments (draws 1–100 and 101–200); V4 at 1, 2 and 4 LT with a signed mean deviation; SHA-256 digests of the trained estimator and allocator weights as new leaves | developer; mathematician M4 | yes: existing leaves unchanged, new leaves only |
| WU-0003.8 | `tools/rehearsal_diagnostics.py`: D1 to D6 below, computed from the dump | developer | tool only |
| WU-0003.9 | `tools/compare_runs.py` (WU-0016.3 pulled forward): tier selection by digests and the tier tolerances of A6 | developer; mathematician M1 and M2 | tool only |

What the dump holds, per system:
- **Core-cell test split, in time order:** w\*, E_C, E_P and C at {0.25, 0.5, 1, 2, 4} LT and at H_ref; split-half w\*; per-rule MSE; ε_s, δ, ν, Λ̄, N, R, d; the deployable profile; per-state counts of clipped draws and LM residuals.
- **Sweep cells:** per-state w\*(H_ref) and corr(e_C, e_P).
- **V4 states:** ŵ_M for M ∈ {50, 200, 800} at 1, 2 and 4 LT.

**A4. Procedure.** Every run is launched by the main session through `tools/run_preset.sh`, in the background and under the GPU lock. The run worktree is a clean, detached worktree at `C_R`; no agent writes to it. Every run starts with an empty cache. Runs go one at a time, and the log is polled with `tail -n 5`.

| Run | Sub-task | Preset, seed, device | Purpose |
| --- | --- | --- | --- |
| R0 | .1 | smoke on DEV-1, GPU and CPU; smoke on DEV-0 on CPU | GPU check (ROADMAP .1 criteria); first use of a 62-bit seed. The device probe: which context digests differ between GPU and CPU, which predicts the tier of R1 against R3. DEV-0 against the step-4 reference: 0 changed. |
| R1 | .2 | pilot on DEV-1, GPU, dump on | the rehearsal |
| R2 | .4 | pilot on DEV-1, GPU, `--skip-robustness` | GPU against GPU (R1) |
| R3 | .4 | pilot on DEV-1, CPU, `LPC_THREADS=8`, `--skip-robustness` | GPU against CPU, on every primary (DEC-0024 follow-up) |
| R4 (optional, O2) | .4 | as R3 with `OPENBLAS_CORETYPE=Sandybridge` | emulates another host's W and U, so that the F1 rule is tested before WU-0016 |
| R5 (O2) | .5 | full on DEV-2, GPU, dump on | full-size precision, budget and counts |
| R6 (optional, O2) | .5 | full on DEV-2, CPU, `LPC_THREADS=8` | input to the choice of confirmatory device (O4) |

- **DEV-1** is used for R0 to R4. **DEV-2** is used only at full size (R5, R6). The registry status of each changes to `used`, by the developer, with `test_seeds` in the radius.
- **Who runs it.** The main session, or a developer it dispatches, under the standing LPC.AUTH.3 (ledger seq 4 and 6; LPC.AUTH.5 extends it to subagents). That covers development seeds only, one run at a time, under 12 h each and at most 60 GPU-hours per week, so R0 to R4 need no per-action authorization.
- **R5 and R6** need the owner's go-ahead, because ROADMAP WU-0003.5 and §4 Phase D reserve the authorization of the optional full run to the owner. The agent records it in this file and in a ledger `note` that quotes the owner's words.
- No run uses `--confirmatory`.

**A5. Acceptance criteria and measurements (fixed now).**

| # | Item | Criterion or report |
| --- | --- | --- |
| C1 | Run integrity | Exit 0; wall-clock under 12 h; provenance shows `seed_id`, `dirty False`, the device, `jax_x64 True` and the DEV label. A gate failure (V1–V7) is reported, never fixed. |
| C2 | P2(c), all three splits | `n_violations == 0` and every chain counter 0, per system: 1400 states (pilot) and 4000 (full). Premise: at least 100 switching states. A nonzero count is a DEF plus `/refer`, never a tolerance. |
| C3 | Clips | Report, per system, the states with a clipped H_ref oracle draw (construction, calibration, test), the clipped evaluation draws, `held_fixed_entries` and the 11e flags. Consistency with the DEV-0 bound of 2.1e-3 per state: a count above 8 of 1400 or above 16 of 4000 (the Poisson 0.99 quantiles) is reported to the owner as "bound not transferred". This is a finding, not a failure. |
| C4 | LM | Report the median of c/ρ² (χ²₄ median 3.357), the fraction above 18.47 (D3: diagnostic only), `fraction_no_decrease` and `fraction_late_progress`, per cell. Predicted bands are set by M6. |
| C5 | Counters | Every `handling` counter is present (zero allowed); the ν-cap clips and replacements are listed per cell. Nothing is silent. |
| C6 | Wall-clock and memory | `wall_seconds`, `peak_rss_bytes` and `device_peak_bytes`, plus `nvidia-smi` sampled at 30 s. R5 does not start if R1's GPU time × the measured full/pilot factor exceeds 10 h; that case is referred. On DEC-0006: the launcher is bash with `timeout`, so the inherited `ru_maxrss` is negligible. |
| C7 | Precision report (.3) | ROADMAP .3 criteria. Projection per criterion with its own n (test 500 → 1000, sweep 300 → 1000). The v3 §7 statements are compared: Q-N ±0.04, H2b(ii) 0.03, H2e 0.04, and H2a(ii) needing \|pc\| ≲ 0.01. A projected half-width outside [0.67, 1.5] times the v3 value is reported as "v3 precision not reproduced". The R5 observed half-width against the R1 projection uses the same band. M3 may tighten either band. |
| C8 | Diagnostics (.8) | D1: acf at lags 1–10 of each criterion's influence series. D2: V\*(b = 10)/V\*(b = 5) and V\*(20)/V\*(5). D3: log-SD of per-state MSE. D4: split-half reliability of logit w\* and the H2a(ii) attenuation. D5: V4 by horizon, with the signed finite-M bias of the H2a(i) range estimated directly against ŵ_800. D6: the fraction f_b of states within 2s of a clip bound (the H2b(ii) bias). |
| C9 | Reading rules for C8 | These are inputs to the owner, not pass/fail: \|acf(1)\| ≤ 0.15 everywhere means the WU-0006 rows at φ = 0 apply; ≥ 0.3 means the φ = 0.3 rows are realistic. V\*(10)/V\*(5) > 1.1 or V\*(20)/V\*(5) > 1.15 on a primary means block length 5 is a design question for the owner. A log-SD > 1.5 means the C2h/C4h rows apply. A finite-M bias at full size above 0.1·hw means "budget row 1 not below 10%". M4 and M5 confirm or tighten these thresholds. |

**A6. Reproducibility tiers (WU-0003.4, and fixed for WU-0016.3).** The tier is selected mechanically from the digests (the F1 rule of DEC-0023, O5). A difference in a W or U digest is a `platform` locus; it does not select branch D.

| Tier | Selected when | Tolerances |
| --- | --- | --- |
| T0 | same host, CPU, same `LPC_THREADS`, all digests equal | every leaf bitwise, except timing and provenance |
| T1 | context and weight digests equal, device differs | cp and oracle chains \|Δ\| ≤ 1e-12·\|ref\|; V1 \|Δe\| ≤ 1e-12 absolute; V2 ≤ 1e-10 relative (WU-0002.12 AM); LM per estimate ≤ 1e-8 relative outside D1-flagged estimates, `fraction_no_decrease` exact, `median_iterations` ±1 (M7(i)); QoIs and interval endpoints \|Δ\| ≤ 1e-4·max(\|lo\|, \|hi\|) (WU-0008 M5) |
| T2 | W or U digest differs, `state_mean_digest` equal | cp, oracle and fixture as T1; LM by the 99% order-statistic bands, \|Δ fraction_no_decrease\| ≤ 3√(2p̄(1−p̄)/n) + 1/n, and `median_iterations` ±1 (M7(ii)); QoIs as T1 |
| T3 | weight digest differs, context equal | network chain as T2; other chains as T1 |
| TD | `state_mean_digest` or λ_max differs (the trajectory differs) | No per-leaf tolerance. Per primary and system, \|Δ\| ≤ 3.4·√(se₁² + se₂²), with se = hw/z_level (Bonferroni over 15 at a family level of 1%). Verdicts are reported. TD between GPU and CPU triggers O4. |

- **In every tier from T1 to T3:**
  - A leaf in a result block where a discrete count differs (K, best single, `n_states`, clip, ν-cap or replacement counts) is allowed \|Δ\| ≤ 0.1·hw instead of the tolerance above.
  - Every verdict must be identical. A verdict difference is a DEF (as WU-0016).
- **The ROADMAP rule** sets the GPU tolerance from R1 against R2: 10× the largest relative difference, rounded up to a power of 10. M2 sets the scale floors. If the GPU-to-GPU difference is 0, the declared tolerance is "bitwise on the same device type". If the rule gives more than 1e-4, that is a finding (O3); it is not adopted silently.
- **`tests/gpu/test_reproducibility.py`** runs the smoke preset twice on the GPU against the declared tolerance, at the freeze gate. It is written after WU-0003.6.

**A7. What the rehearsal feeds into the freeze.**
- The v3 values M = 200, B = 2000, blocks of 5, and sizes 2000/1000/1000/1000 with the five-point n_lib grid are design values. Only the owner changes them, as a v3 amendment before the freeze, on precision evidence (half-widths, Monte Carlo errors, bias bounds), never on the direction of DEV verdicts.
- **M.** The finite-M bias does not shrink with n. At full size, the worst case F1 is 0.6 to 1.2 of the half-width, against 0.43 to 0.86 at the pilot. D5 decides whether the shared draws make it small.
- **M ≥ 400** would break H-M1 and H-M2 (L²/M > 0.25; WU-0002.11e §5).
- **B.** The B = 2000 endpoint Monte Carlo error must be below 10% of hw (WU-0008.2).
- **Sample size.** C7 reachability.
- **Tolerance.** A6.

**A8. Risks.**
- **GPU speed.** Unmeasured (C6, R0); the wrapper kills a run at 12 h.
- **Lock contention.** The step-4 DEV-0 pilot and WU-0005.6 also take the lock. They are sequenced before R1, and no agent waits on the lock.
- **Trajectory divergence between GPU and CPU.** A jitted scan over 165 000 steps on another device is likely to differ by an ulp, and then by O(1) after about 40 LT. R0 shows whether this happens.
- **GPU reductions** are not deterministic: autotuning and atomics; `XLA_FLAGS` is never set.
- **First pilot-size use of a 62-bit seed.**
- **Memory.** At most 10 GB of host memory at full size; GPU 24 GB, with preallocation off.
- **CPU sharing** with other lanes: 8 threads here plus 4 per lane, on 32 CPUs.

**A9. Affected checks.**
- **WU-0003.7:** `python3 tools/test_impact.py --base develop`. By hand, add:
  - `test_experiments`, `test_pipeline`, `test_validation`, `test_oracle` and its transitive dependents, and `test___main__`;
  - `test_identifiers` (DEF-0016 source scan) and `test_tools_test_impact` (graph fixture);
  - `test_tools_compare_pilot` (the new leaves need a `new` rule; the tool exits 2 otherwise);
  - `tests/integration` (the pipeline is touched);
  - plus one DEV-0 smoke against the base.
- **WU-0003.8, .9 and .3:** only their own `tests/unit/test_tools_<t>.py`.
- **The runs:** no tests.

**A10. Owner checkpoints (LPC.PC.11).** WU-0003.7 (weight digests, which are provenance, and V4, a validation statistic) and WU-0003.9 (CSQ2 use in WU-0016) are marked "needs owner review before freeze". The registry status change touches seed records. No dependency changes.

**A11. Applied-mathematician items (before execution; they may tighten, never loosen).**
- **M1:** confirm the A6 tiers. In particular, the T1 network-chain QoI tolerance (flow amplification over 8 LT is about e⁸ on LM-level differences), and the TD statistic.
- **M2:** the scale floors for "relative difference", per leaf class, for the 10× rule.
- **M3:** projection factors per criterion (K-dependent and ratio criteria); the [0.67, 1.5] bands of C7.
- **M4:** the influence series per criterion; the C9 thresholds, with the SE of the variance ratios at n = 500 and 1000; split-half on logit w\* when w\* = 0 or 1 (22–36% of states).
- **M5:** the estimator of the direct finite-M bias from D5; F1 at M = 200, 300 and 399.
- **M6:** predicted bands for C4.
- **M7:** whether the P2(c) slack κ = 1e-13 suffices at 4000 states.
- **M8:** whether R0's digest pattern can select T1 for R1 against R3 before R3 exists.

**A12. Owner questions.**
- **O1.** The order in A2 (the seed step before the rehearsal; WU-0005.6 before `C_R`). Recommended.
- **O2.** Authorize R5. Choose whether to run R4 and R6. Recommended: all three.
- **O3.** Whether to set `XLA_FLAGS=--xla_gpu_deterministic_ops=true` for GPU runs. This changes WU-0012's rule; the researcher first confirms what the flag does in JAX 0.11.2.
- **O4.** If GPU against CPU is TD, choose one:
  - (a) pin the trajectory and context to the CPU, a code change;
  - (b) run the confirmatory run and the regeneration on the same device type;
  - (c) accept statistical agreement.

  Recommended: (b). If R6 confirms about 2 h, consider CPU for the confirmatory run, which allows a bitwise regeneration (T0).
- **O5.** The F1 rule of A6. Recommended: yes.
- **O6.** Dump opt-in (recommended) or always on, including the confirmatory run.
- **O7.** The weight digests. Recommended: yes.
- **O8.** WU-0003.4 widened from one core cell to the pilot without robustness, so that it covers the primaries. Recommended: yes.
- **Open, not needed here:** DEC-0006 VmHWM.

**Open questions for the researcher:** whether XLA GPU in JAX 0.11.2 is run-to-run deterministic for dense matmuls (autotuning), reductions and scatter, and what `--xla_gpu_deterministic_ops` covers.

### Plan amendment 2 (2026-10-14, planner claude-opus-5-5; basis: mathematics check `docs/agent/notes/2026-10-14-math-wu0003.md`, e8a39ed, §11 draft and §12 flags)

The plan and amendment 1 stay in force except where an item below says it replaces or refines them. This section is fixed before any rehearsal output exists (VV.3): no R0 to R6 output exists at this commit (branch merged with `develop` b982806). **Strictness rule.** Where the mathematician's draft would be looser than amendment 1 for some input, the working rule below is the stricter of the two, and the point goes to the owner as a planner flag (PF-n, B4). No threshold here is looser than in amendment 1.

**B1. Amended items** (numbering as the note's §11).

| # | Amended criterion or definition | Relation to amendment 1 | Strictness |
| --- | --- | --- | --- |
| 1 | **Tier selection.** TD is selected when any of these differs, for any system: `state_mean_digest`, λ_max, `interval`, `start_state` (main or estimator), `main_digest`, `estimator_digest`. The last two are new `context` leaves (.7a): SHA-256 of the post-burn-in main and estimator trajectories (float64, C order). T1 to T3 require all six equal. A pair in which either run lacks a selecting leaf is "tier undetermined": no T0 to T3 tolerance is applied, and the tool exits 2. When TD is selected only by `main_digest` or `estimator_digest`, the per-leaf differences are also listed (report only). | Replaces A6's TD "Selected when" cell; adds premises to T1 to T3. It implements A6's own condition, "the trajectory differs". | Tolerances unchanged; T1 to T3 premises stricter. Watch item: PF-1. |
| 2 | **T1, LM per estimate.** For estimates with `lm_late_progress` = 0 in both runs: \|Δc\| ≤ 1e-8·\|c_ref\| (A6). If also c/ρ² ≤ 18.47 in both runs: \|Δc\| ≤ min(1e-8·\|c_ref\|, η(2√c_ref + η)), with η = 1e-12·max(1, ‖X‖_∞) (WU-0005.4 M2). Late-flagged estimates are counted and listed, with no tolerance (as A6). | Refines A6 T1 LM. | At least as strict for every estimate. The draft's form alone is looser in two places: PF-2. |
| 3 | **Discrete counts.** .7a records these as new bitwise-neutral leaves: `nfev` and `status` of the `fitted/analog_proxy` and `fitted/estimation_proxy` fits, and a SHA-256 digest of the A5 leaf index of the calibration and test states. The A5 leaf index per state goes in the dump (.7b). The A6 exception list (K, best single, `n_states`, clip, ν-cap and replacement counts) is unchanged. A difference in a new integer is printed beside the H2c, H2d, H3c and `oracle_recovery` A4 differences. Until OF-1 is decided, it does **not** license the 0.1·hw exception. | Refines A6's first bullet. | As A6. The draft ("every integer leaf of the upstream chain") widens the exception: OF-1. |
| 4 | **Relative differences and the 10× rule.** rel = \|Δ\|/s, with s by class (note §M2): (a) interval statistics, s = max(\|lo\|, \|hi\|) of the reference interval, and Δ = 0 is required if both are 0; (b) weight-scale leaves, max(\|ref\|, 0.01); (c) fractions and probabilities, max(\|ref\|, 1/n); (d) correlations without an interval, max(\|ref\|, 1/√n); (e) p-values, max(\|ref\|, 1e-3); (f) R²-type leaves, max(\|ref\|, 0.01); (g) positive scales, \|ref\|, with an exact zero requiring Δ = 0. Excluded from the maximum, each under its own rule (h): integer leaves, digests and strings, V1, V2, `fitted/*/floor` and other chain heads (reported), blocks with a differing discrete count (0.1·hw), timing and provenance. The tolerance is declared per class: (a), and (b) to (g) together. **The O3 trigger (> 1e-4 is a finding) applies to both classes.** In T1 to T3, leaves of (b) to (g) without an interval are listed with rel and the class tolerance; an exceedance is a listed finding. "Bitwise on the same device type" stays if R1 = R2. | Fills A6's "M2 sets the scale floors". | Defines what A6 delegated. The draft limits O3 to class (a): PF-3. |
| 5 | **TD statistic.** Per primary part (18 parts: H2a(ii) counts two), z is computed twice: with the symmetric se = hw/z_level (A6), and with the arms facing away from the other estimate (DEC-0027). The part fails if max(\|z_sym\|, \|z_away\|) > 3.4. Family level ≤ 1.2% for each form. Both are printed. | Refines A6's TD row. | At least as strict. The away form alone gives a lower z on 7 of the 18 P0/P1 parts (Chua H3c: 1.02 against 1.34): OF-5. |
| 6 | **C7 projection.** hw_full = hw_pilot × f, with the factors of note §M3: √(n_p/n_f) for each criterion's own n; × 1.014 for B at 1 − 0.05/3 (× 1.007 at 95%); × κ_E for H2c, H2d and H3c, as a point estimate from the dump (V_s, V_d; the range [0.707, 1] only if not estimable); × [0.61, 1] (logit, log-horizon) or [0.74, 1] (indicator) for Q-N training. Ratios are projected as hw/R̂. H3c and H3a are conditional on K_pilot. **Two readings, both reported:** (i) A5's, against √(n_p/n_f) alone, band [0.67, 1.5]; (ii) the factor reading, outside if below 0.67·(lower projection) or above 1.5·(upper projection). "v3 precision not reproduced" is reported if either reading says outside, naming which. The predicted false-trigger rate is printed per part (about 0.4%; H3c about 7%). Pre-registered predictions from P0/P1: H2e narrower than v3 (0.44–0.76 of 0.04), H2b(ii) near the lower edge (0.68–0.85), Q-N undetermined. | Refines A5 C7; bands unchanged. | Reading (ii) alone is wider on the low side: PF-4. |
| 7 | **C8/C9 diagnostics.** | Refines A5 C8 and C9. | See each line. |
| 7.D1 | Influence series per criterion as in note §M4.1, over all states of the criterion's split in time order, with 0 outside the domain. "The φ = 0 rows apply" if every \|acf(1)\| ≤ 0.15 (n ≤ 500) or ≤ 0.11 (n = 1000). "The φ = 0.3 rows are realistic" if acf(1) ≥ the case value: 0.30 for H2b(i), H2b(ii) and H2c; 0.19 for H2a(i) and H2e; 0.16 for H3c and H2d; 0.09 for H2a(ii). Between the two, the coverage is interpolated linearly in the lag-1 of the influence series. If both readings hold (H2a(ii), 0.09 ≤ acf(1) ≤ 0.15), the φ = 0.3 reading governs. | Replaces "≥ 0.3"; adds 0.11 at n = 1000. | Tightening. |
| 7.D2 | V\*(b) in closed form: b × the variance of the n − b + 1 overlapping block means (the exact MBB variance, no B). The A5 rule (V\*(10)/V\*(5) > 1.1 or V\*(20)/V\*(5) > 1.15 on a primary) is computed and reported, with its predicted trigger rate under no dependence printed beside it: per series 0.21, 0.16 and 0.09 at n = 300, 500 and 1000; at least one of 18 series 0.97 (pilot) and 0.83 (full); power about 0.4 at φ = 0.3. Two readings are added: β̂₅ from acf(1) ("design question" if β̂₅ + 2 SE < 0.8685, used when acf(2..10) lies within 2.5/√n of φ̂^k), and the pooled per-system log V\*(10)/V\*(5) against a permutation null (1000 permutations, one permutation per system applied to all its series, trigger at the 0.99 quantile). Any of the three firing goes to the owner as "block length 5 is a design question". | Keeps A5's rule; adds two readings. | At least as strict. Which reading governs: OF-3. |
| 7.D3 | Per-state eval MSE of A4 and A5 (H3c) and of A1, A2 and A4 (H2c) at H_ref. The log-SD reading (> 1.5) uses the run's own σ̂ at the run's own E. Also printed: σ̂_E4 = √(σ̂² − 1.000) and the oracle state-part log-SD of V_i(w). | Defines A5's D3. | Threshold unchanged. |
| 7.D4 | Split-half on the unclipped optimum u = (E_P − C)/c of each half. Interior part: the delta-method attenuation A on delta-valid interior states, with the excluded count, and the Spearman–Brown value beside it, both labelled "overstates reliability". Zero part: indicator reliability from the split-half covariance, then Spearman–Brown to 200 draws. Spearman(v, Λ̃ \| Q) is printed. | Defines A5's D4. | Definition. |
| 7.D5 | B̂(200) = 2.414·Δ_sh, where Δ_sh = ½[med(r_A) + med(r_B)] − med(r_200) over all eligible test states (production eligibility, production median). The order-1 value Δ_sh is printed. SE from the production block bootstrap (blocks of 5, B = 2000). The V4 check gives p̂ = log₄[(m(50) − m(200))/m(200)] ("order not determined" outside [0.3, 1.5]), B̂_V4 = 2·m(200), and the signed mean of ŵ_M − ŵ_800 at H_ref. Readings: "below 10%" iff \|B̂\| + 2 SE < 0.1·hw_full; "not below 10%" iff \|B̂\| − 2 SE ≥ 0.1·hw_full; otherwise "not determined". Budget row 1 is stated below 10% only on "below 10%". A5's point reading (\|B̂\| > 0.1·hw_full) is also printed. | Replaces A5 C8 D5 ("against ŵ_800" understates by half) and the last C9 sentence. | Stricter. Treatment of "not determined": PF-5. |
| 7.D6 | The H2b(ii) bias by split-half Richardson on the mean paired change of the two library cells; f_b with s_i = \|u_A − u_B\|/2, pooled by w bins. | Defines A5's D6. | Definition. |
| 8 | **Dump additions** (.7b, bitwise-neutral): per-state rule weights at H_ref (A2, A3, A4, A5) and the A5 leaf index; split-half moments for the H2b cells (ρ = 1% with N_lib 10³ and 10⁴; the four noise cells); per-state V4 half-widths (M = 50, 200, 800) and signed deviations; per-estimate c, accepted and late flags (core test split); Q-N per-state predictions of both models; g_H at H_ref. `main_digest` and `estimator_digest` are results leaves (.7a). | Adds to A3's dump list. | Definition. |
| 9 | **C4 bands** as in note §M6 (pilot, oracle kind; eval kind with a 99% Poisson interval; full upper ends as pilot, lower ends at the χ² floor, `median_iterations` ≤ pilot + 1). Relation check: \|median c/ρ² − Q_χ²₄(0.5/(1 − (f_above − 0.001)))\| ≤ 4·SE_iid (0.025 core oracle, 0.05 sweep, 0.24 core eval). Exact check: the LM summaries of the library-sweep cells at fixed ρ are bitwise equal across N_lib, and a difference is a defect (DEF and `/refer`). A value outside a band is a finding. | Fills A5 C4's "set by M6". | New checks only. |
| 10 | **C2:** κ = 1e-13 confirmed at 4000 states (M7). No change. The optional margin leaf is not added. | None. | Unchanged. |
| 11 | **R0:** DEV-1 smoke with `--systems lorenz63 rossler chua` on GPU and on CPU. The DEV-0 smoke on CPU against the step-4 reference keeps the default systems (0 changed). The R0 record lists, per system, which context, trajectory and weight digests and which V1 leaves differ between devices. Its tier prediction is informational; the tier comes from R1's and R3's own digests. If any V1 leaf differs by more than 1e-12 between devices, refer before R3 (OF-2). | Refines A4 R0. | Tightening (P-1, B4). |
| 12 | **C1 predictions** (proposed pre-registration, P-2): P(at least one V6 failure over DEV-1 and DEV-2) ≈ 8.8% (12.9% if R3 is TD); P(at least one V4 failure) ≈ 50% (plug-in) to 71% (predictive) (DEF-0026). A failure is reported, never fixed (DEC-0027). R5's V4 (100 states) is not pooled with the pilot V4; a pilot-equivalent V4 (median of the first 40 states) is formed from the dump. | Adds to A5 C1. | C1 unchanged. |

**B2. Sub-tasks .7 to .9** (these replace A3's rows; .7 is split into .7a and .7b). Every sub-task runs the radius from `python3 tools/test_impact.py --base develop --explain`, plus the hand additions below, and writes the set into `## Log` first (§4.2, §4.9).

| Id | What | Acceptance (reference; tolerance) | Radius | Owner |
| --- | --- | --- | --- | --- |
| .7a | New results leaves: `main_digest`, `estimator_digest`; proxy-fit `nfev` and `status`; A5 leaf digest; the estimator and allocator weight digests (A3, O7). | a1: DEV-0 smoke at the tip against the base (`compare_pilot`): 0 changed, 0 removed; the added leaves are exactly this set, counted in the Log. a2: each digest equals `hashlib.sha256` of the array's float64 C-order bytes, recomputed independently in the test; exact. a3: `nfev` and `status` equal scipy's `OptimizeResult` on a synthetic `least_squares` problem with known solution; exact. a4: the A5 digest equals SHA-256 of `tree.apply(...)` as int64, recomputed in the test, and changes when one state's leaf changes; exact. a5: `compare_pilot` gets a `new` rule for these leaves (exit 0 on base against tip). a6: no new RNG draws (`test_rng_hygiene`, a1). | If `data.py` is touched (core): `test_data` plus every transitive dependent's unit test plus `tests/integration`. Otherwise: `test_allocation`, `test_experiments`, `test_pipeline` and their direct dependents (`test_analysis`, `test_report`, `test___main__`), plus `tests/integration` (the pipeline is touched). Always add `test_identifiers`, `test_rng_hygiene` and `test_tools_compare_pilot`; add `test_tools_test_impact` if imports change. The hand smokes of a1 replace `test_smoke_pipeline` (§4.2: one of them, not both). | needs owner review before freeze (provenance digests; verdict-chain leaves) |
| .7b | Opt-in dump `states/<system>.npz` (A3 list plus B1 item 8), with a schema version key and the schema in the docstring. | b1: dump off, results bitwise equal to the .7a tip (DEV-0 smoke; 0 added). b2: dump on against off, results bitwise equal except the flag's provenance leaf. b3: the production summary function applied to each dumped array reproduces its results leaf (median w\*, per-rule MSE, V4 median, LM summaries, Q-N ΔR² via `analysis.delta_r2`, H1b slope, `n_states`, clip counts). Bitwise where the function and order are the same; otherwise ≤ γ_n = nu/(1 − nu) relative, stated per array. b4: (m_A + m_B)/2 = m_200 for E_C, E_P and C in every split cell, \|Δ\| ≤ 1e-13·mean\|terms\| (γ₂₀₀ ≈ 2.2e-14, margin 4.5). b5: the median of the first `convergence_states` per-state V4 half-widths equals the V4 leaf, bitwise. b6: with `--confirmatory`, the dump is refused until O6 is decided. b7: the dump size at smoke, and the estimate at pilot and full, are in the Log. | As .7a for the modules touched. If `oracle.py` is touched: `test_oracle` plus its transitive dependents plus `tests/integration`. `__main__.py`: `test___main__` plus `tests/integration`. Add `test_identifiers` and `test_rng_hygiene`. | needs owner review before freeze (V4 and LM data; CLI guard) |
| .8 | `tools/rehearsal_diagnostics.py`: D1 to D6 per B1 item 7, from `results.json` and the dump. The output is labelled DEVELOPMENT. Every series is listed with its readings and predicted rates; a missing array prints "not computable" and is never skipped. | c1: for each smooth criterion, ψ_i equals the numerical Gateaux derivative at ε = 1e-6 (fitted models held fixed; n = 50 synthetic), relative ≤ 1e-4 (O(ε) truncation plus u/ε). Σψ_i = 0 within 1e-12·Σ\|ψ_i\|. Sign types: exact on a tie-free sample, and the mid-rank rule on a sample with ties. c2: acf(1) of an alternating ±1 series of even n is −(n − 1)/n, to 1e-12. c3: V\*(b) equals a naive loop to 1e-12 relative. c4: β₅(0) = 1 exactly; β₅(0.3) = 0.8685 ± 5e-5. c5: ψ′(1) − ψ′(2) = 1 to 1e-12 (the identity ψ′(z) − ψ′(z + 1) = 1/z²). c6: the D5 Δ_sh and B̂ on the `m5_d5split.py` model (seed 20261017) match the script to 1e-12 relative; p̂ = p exactly on m(M) = c(M^−p − 800^−p); the three-way reading is exact on hand-built inputs. c7: f_b and the split-half mean bias are exact on constructed sets. Slow (Monte Carlo, fixed seeds, MC error stated): E V\*(10)/V\*(5) at φ = 0, n = 500, R = 2000 is 0.987 ± 4·0.083/√2000 (`m4_ratios.log`); the permutation-null trigger rate on iid data, R = 500, is ≤ 0.01 + 3√(0.0099/500); D4's attenuation on synthetic data with known A₀ is within 4 MC SE. | `tests/unit/test_tools_rehearsal_diagnostics.py`. `tests/slow/test_rehearsal_diagnostics_mc.py`, run once by the .8 developer, who owns the statistic. No `lpcstudy` tests unless a module is changed. | needs owner review before freeze (statistics feeding the block-length and M decisions) |
| .9 | `tools/compare_runs.py` (WU-0016.3 pulled forward): tiers T0 to T3 and TD per A6 and B1 items 1 to 5; classes and the 10× rule per class; exit 0 (pass), 1 (a tolerance or verdict failure; a verdict difference prints a DEF line), 2 (undetermined or usage). | d1: a truth table on fixtures built from the WU-0002.14 S3 smoke pair (164 KB each, copied to `tests/unit/fixtures/`), with single leaves edited: each of the six TD triggers alone gives TD; W or U alone gives T2; a weight digest alone gives T3; all equal on another device gives T1; same host, CPU and threads gives T0; a missing selecting leaf gives exit 2. Exact. d2: every A6 and B1 rule passes at 0.5× its tolerance and fails at 2×. d3: on the unedited kernel pair, the per-class declaration is 1e-5 for (a) and 1e-4 for (b) to (g), with largest rel 3.97e-7 (H1a `ratio_ci`) and 4.99e-6 (`weight_profile` q25 at 165 steps), as in `m2_floors.log` to its printed digits; O3 is not triggered. d4: on the 18 P0/P1 primary parts (extracted fixture), Σz² = 12.65 (symmetric) and 11.99 (away) and max\|z\| = 1.69, as in `m1_td_p0p1.log` (± 0.005); no part fails. d5: the compared leaves number the union of both runs' leaves; one-sided leaves are listed; every difference is listed with its class, rel, tolerance and outcome; timing and provenance are listed as excluded. | `tests/unit/test_tools_compare_runs.py`; add `test_tools_compare_pilot` or `test_tools_leafdiff` only if those tools are changed. | needs owner review before freeze (tolerance and verdict-comparison code; CSQ2 use in WU-0016) |

**B3. Order of implementation.**
1. .7a first. It fixes the leaf names that .9 selects on and that R0 records.
2. .9 next, against the .7a leaf names. It may start in parallel with .7a once the names are final.
3. .7b, the dump.
4. .8, which reads the dump format.

A2 step 6 is unchanged: all four merge before `C_R`, each showing 0 changed leaves on the DEV-0 smoke, then the step-7 gate. The A9 radius for .7 is superseded by B2.

**B4. Owner questions** (none is decided here; each working default is the stricter reading and holds until the owner rules). Amendment 1's O1 to O8 remain open.

| Id | Question (mathematician's text, note §12, or planner) | Working default |
| --- | --- | --- |
| OF-1 | The T1–T3 QoI rule (1e-4·max(\|lo\|, \|hi\|)) has no licence for the tolerance-stopped proxy fit (ftol 1e-8, up to √ftol ≈ 1e-4 relative per flip) or for the A5 tree, both upstream of H2c, H2d and H3c. The cross-host DEV-0 comparison reached 6e-5 there (1.7× margin). Item 3 records the flips as integers. Does a `fitted/*` coefficient change > 1e-6, or a new-integer difference, also license the 0.1·hw exception (DEC-0019 N3 precedent, scoped causally)? | No licence. A failure with a differing integer is a DEF and `/refer`, with the integer attached. |
| OF-2 | V1's \|Δe\| ≤ 1e-12 under a device change holds only if the FD evaluations are bitwise equal across devices. If R0 shows otherwise, the rule fails on correct code. The principled replacement, about 1e-9 absolute, is wider. | Keep 1e-12. If R0 shows a V1 difference > 1e-12, refer, and do not run R3 until the owner rules. |
| OF-3 | C9's variance-ratio thresholds fire in about 97% (pilot) and 83% (full) of runs with no dependence, and catch the φ = 0.3 stress only about 40% of the time per series. Which calibrated reading (β̂₅, pooled permutation) informs the block-length question? | All three computed and reported; any firing goes to the owner as a design question. |
| OF-4 | F1 (WU-0008 M3, DEC-0024 point 2) is not a worst case for the median: a synthetic case reaches 1.38·F1. Its wording should be "indicative (the bias of a zero-range state); not a bound on the median". No admissible M (≤ 399) brings F1 below 0.1·hw. | The rehearsal report uses the corrected wording. WU-0008 and DEC-0024 stay untouched until the owner appends a ruling. |
| OF-5 | The TD se form: the away arms (DEC-0027) instead of the symmetric hw/z; 3.4 kept over 18 parts. | Both computed; a part fails on the larger \|z\| (B1 item 5). |
| OF-6 | Pre-register the predicted gate failures under C1 (V6 ≈ 9–13%, V4 ≈ 50–71% over the DEV-1 and DEV-2 realizations), so that a failure is read under DEF-0026 and DEC-0027. | Proposed text in B1 item 12. It must be confirmed or struck **before R1**, since pre-registration after R1 is void. |
| PF-1 | Item 1 routes pairs whose main or estimator trajectory diverged to TD (statistical agreement), where A6's literal digest test would have applied T1 to T3 per leaf and raised a DEF on correct code. | Adopted as A6's stated intent; per-leaf differences are still listed. The owner may instead require such pairs to be referred. |
| PF-2 | The draft's LM rule drops the 1e-8 bound for non-late estimates with c/ρ² > 18.47. For c < 4e-8·max(1, ‖X‖_∞)², its bound η(2√c + η) also exceeds 1e-8·c: at ρ = 0.5% and ‖X‖_∞ ≈ 3, about 3e-5 of estimates (P(χ²₄ < x) ≈ x²/8). | The min of both (B1 item 2). |
| PF-3 | The draft applies the O3 trigger to class (a) only. | Both classes. |
| PF-4 | The C7 factor-range reading alone widens A5's band on the low side. | Both readings; either triggers the report. |
| PF-5 | D5's "not determined" against A5's point reading. | "Not determined" is treated as "not below 10%" for budget row 1; the point reading is also printed. |
| P-1 | Pre-register R0 on all three systems on both devices (item 11). | Adopted (a tightening). The owner confirms. |
| P-2 | Pre-register the C1 gate-failure probabilities (item 12; OF-6). | As OF-6. |

**B5. Affected checks of this amendment:** documentation only, so no tests (§4.2). **Owner checkpoints (LPC.PC.11):** .7a (provenance), .7b (validation and LM data, CLI guard), .8 (statistics) and .9 (tolerance and verdict comparison) all need owner review before freeze. No seed code and no dependency changes. The registry status change of A4 is unchanged.

## Log

### WU-0003.7a (developer claude-sonnet-5-5, 2026-10-14; branch `wu/0003-rehearsal`, from `dcc4ff2`)

Needs owner review before freeze (provenance digests and verdict-chain leaves; B2 row .7a, plan A10). Bitwise-neutral: new `results.json` leaves only, no new random draw, no existing leaf changed. Development seeds only (DEV-0 for the pending smoke); the sealed seed and the owner-only run path are not touched. The dump is not touched (that is .7b).

**Design (leaf names, fixed here because .9 and R0 select on them).**

| Leaf (per system unless noted) | Where it is computed | What it is |
| --- | --- | --- |
| `systems/<s>/context/main_digest` | `data.build_context` (meta; `context_record` passes it on) | SHA-256 of the post-burn-in main trajectory (`ctx.eval_states`), float64, C order (`provenance.array_digest`) |
| `systems/<s>/context/estimator_digest` | `data.build_context` | the same for the post-burn-in estimator trajectory (not kept in the context, so it is hashed where it exists) |
| `systems/<s>/fitted/analog_proxy/{nfev,status}`, `.../estimation_proxy/{nfev,status}` | `allocation.SeedProxy.fit` (two new fields, default `None` for a hand-built proxy), read by `vars()` as before | `OptimizeResult.nfev` and `.status` of the soft-L1 `least_squares` call |
| `systems/<s>/fitted/a5_leaf_digest` | `experiments.fitted_record` via `RegimeMap.leaf_digest` and `provenance.index_digest` | SHA-256 of the int64 `tree.apply` leaf id of every (state, draw) of the calibration profiles, then the test profiles, of the chosen-K A5 tree, C order (one digest) |
| `systems/<s>/fitted/allocator_digest` | `experiments.fitted_record` via `TrainedNetwork.weights_digest` | SHA-256 of the A3 allocator network's W1, b1, W2, b2, ... (float64, C order; the standardization arrays are not included) |
| `estimators/<key>/weights_digest` and `systems/<s>/validation/estimators/<key>/weights_digest` | `pipeline.Study.setup` (`estimator_log`) | the same digest for each trained estimator network (one per system, D, delay and noise level) |

Nothing is clipped, replaced or skipped by any of these. `TrainedNetwork.weights_digest` raises `TypeError` on a non-float64 parameter and `index_digest` on a non-signed-integer array (PRIME.4). The profiles of `a5_leaf_digest` are recomputed by `deployable_profile` (a pure function, the call `clip_sensitivity` already makes) from the same evaluation draws and proxies as production.

**§4.9 checklist (before the first invocation; the code and tests are written, nothing has run).**
1. Change set (`git diff --name-only develop...HEAD` plus `git status --porcelain`; the branch differs from `develop` in docs only so far): `lpcstudy/allocation.py`, `lpcstudy/data.py`, `lpcstudy/experiments.py`, `lpcstudy/networks.py`, `lpcstudy/pipeline.py`, `lpcstudy/provenance.py`, `tools/compare_pilot.py`, `tests/unit/test_allocation.py`, `test_data.py`, `test_estimation.py`, `test_experiments.py`, `test_pipeline.py`, `test_provenance.py`, `test_tools_compare_pilot.py`, `tests/integration/test_smoke_pipeline.py`, this file.
2. Radius, `python3 tools/test_impact.py --base develop --explain`: `data.py` is a core module (own + transitive dependents + integration); `allocation.py`, `networks.py`, `provenance.py` are modules (own + direct dependents + source scans); `experiments.py` and `pipeline.py` are pipeline modules (own + direct dependents + integration); `tools/compare_pilot.py` its test file. Unit set (19 files): `test___main__`, `test_allocation`, `test_analysis`, `test_clip_sensitivity`, `test_data`, `test_ensemble`, `test_estimation`, `test_experiments`, `test_identifiers`, `test_oracle`, `test_pipeline`, `test_provenance`, `test_report`, `test_rng_hygiene`, `test_statistics`, `test_tools_compare_pilot`, `test_tools_lm_doubling`, `test_tools_test_impact`, `test_validation`. Integration set: `tests/integration` (5 files). The tool's warning "no test file for lpcstudy/networks.py" is answered by the new test in `test_estimation.py`. **B2 hand additions:** the data.py core row (test_data, every transitive dependent, integration), `test_allocation`, `test_experiments`, `test_pipeline` and their dependents (`test_analysis`, `test_report`, `test___main__`), `test_identifiers`, `test_rng_hygiene`, `test_tools_compare_pilot`, and `test_tools_test_impact` (imports changed: `data`, `networks` and `allocation` now import `provenance`). All are in the tool's set already, so the radius is the tool's set: 19 unit files, smaller than the whole suite (no gate). **The a1 hand smokes replace `test_smoke_pipeline`** (B2, 4.2: one of them, not both).
3. Already run: no. This set has not run on this code.
4. Device: `JAX_PLATFORMS=cpu` (set by `tools/run_tests.sh`).
5. Threads and time: `LPC_THREADS` 4 (default); wrapper timeout 300 s for unit (the whole unit tier took 119 s at the last gate).
6. Contention: a pilot arm of another lane is running (PID 1947011: `-m lpcstudy --preset pilot --out .../lm-post/runs/dev/wu0005-6/k15 --seed-id DEV-0 --estimator-refine-steps 15`). The unit tier starts no preset and no GPU job, so it runs. Every file of `tests/integration` that matters here starts a smoke preset (`test_smoke_pipeline`, `test_clip_failure` twice, `test_preset_wrapper`; `test_cli_seeds` and `test_lm_doubling_probe` run the CLI driver or small estimators): the integration tier and the a1 smokes wait for the slot (see "Pending").
7. Output: `-q --tb=short -rfE` (the wrapper's).
8. Command: `tools/run_tests.sh unit <the 19 files above>` (the tool's last line).

**Results.**
- Unit radius, run once: `2 failed, 886 passed in 76.92s`. The two failures were `test_tools_test_impact.py::test_graph_equals_hand_derived_fixture` and `::test_function_level_import_is_an_edge`: the hand-derived import graph fixture lacked the three new edges `data`, `networks` and `allocation` to `provenance` (the digest imports). Fix: the three rows of `tests/unit/fixtures/lpcstudy_graph.json` and its description edited by hand from the imports (as that file's rule requires, never from tool output). Then `tools/run_tests.sh unit --lf tests/unit/test_tools_test_impact.py`: `2 passed, 48 deselected in 0.36s`.
- a6 (`test_rng_hygiene`) passed inside the radius: no new `default_rng`, `random.` or `PRNGKey` in the diff (grepped, none); the diff has no `clip`, `nan_to_num`, `isfinite`, `where(`, `try:` or `except` either, so nothing is counted because nothing is handled.
- Existing tests edited, each because the contract it pins changed by design, none loosened: `test_data.py` key set of `ctx.meta` (+ `main_digest`, `estimator_digest`); `test_pipeline.py` stub network gains the one method `Study.setup` now reads; the graph fixture above. No tolerance in an `assert` or `approx` grew; the two `approx` values added in `test_allocation.py` copy the existing recovery test (rel 0.02 and 0.05, 34 and 29 standard errors).
- New tests and their references (all independent of the code under test): a2 `test_data` (`hashlib` over the trajectories that `simulate_trajectory` returned, recorded by the existing spy, cut at the burn-in; `struct` bytes) and `test_experiments`, `test_pipeline`, `test_estimation` (weights packed with `struct`); a3 `test_allocation` (scipy's `OptimizeResult` for the same manufactured problem, noisy and exact data); a4 `test_allocation` and `test_experiments` (leaf ids decided by hand from a manufactured stump with the split at 0.5, packed with `struct`; one state moved across the split changes the digest to the new hand value, one moved within its leaf does not); `test_provenance` (`index_digest` against `struct`, dtype refusals); a5 `test_tools_compare_pilot` (each of the ten leaf kinds has exactly one rule, class `new`; a tree with the leaves against the same tree without them changes no other status; the CLI exits 0).

**Pending (not run, slot rule).** The a1 smoke and the integration tier are presets, and a pilot arm of another lane (PID 1947011, DEV-0 pilot, `lm-post/runs/dev/wu0005-6/k15`) was running when the unit radius finished. Nothing was started. To run when the main session says the slot is free, one preset at a time, `pgrep -fa '[l]pcstudy --preset'` empty before each:
1. Base: a detached worktree at `dcc4ff2` (this branch before the first .7a commit; its `lpcstudy/` equals `develop`'s), `tools/run_preset.sh smoke DEV-0 runs/wu0003-7a-base` (CPU, `LPC_THREADS=4`).
2. Tip: this branch at the .7a tip, `tools/run_preset.sh smoke DEV-0 runs/wu0003-7a-tip`.
3. `python3 -I tools/leafdiff.py <base>/smoke/results.json <tip>/smoke/results.json --group-depth 4`: expected 0 different, 0 removed, and the added leaves exactly these, counted (default smoke systems = `lorenz63`): 2 (`context`) + 4 (`fitted/<proxy>/{nfev,status}`) + 2 (`fitted/{a5_leaf_digest,allocator_digest}`) + 2 per trained estimator entry (one in `estimators`, one in `systems/lorenz63/validation/estimators`; the entries are the (system, D, delay, noise) networks the smoke trains, counted from the run) = 8 + 2 x (number of `estimators` entries) added leaves.
4. `python3 -I tools/compare_pilot.py <tip>/smoke/results.json --old <base>/smoke/results.json --no-reference ...`: exit 0 (a5, on a real pair; the unit test covers the rule, the smoke covers a real tree).
5. The integration tier, once: `tools/run_tests.sh integration tests/integration` (it contains `test_smoke_pipeline`, whose new `assert_wu0003_7a_leaves` checks the schema of the new leaves). B2 says the hand smokes of a1 replace `test_smoke_pipeline`; the other four files of the directory start presets as well and are in the radius.

### WU-0003.9 (developer claude-sonnet-5-5, 2026-10-14; branch `wu/0003-9-compare-runs`, from `9039bf5`, the .7a tip, whose leaf names are final)

Needs owner review before freeze (the tool decides tolerances and compares verdicts; CSQ2 use in WU-0016; plan A10, B2 row .9). Tool only: no `lpcstudy/` file is touched, no preset is run, no RNG draw is added, development seeds only (the evidence runs read DEV-0 results already on disk; the sealed seed is not touched). The tool is read-only on run directories and writes nothing but its report to standard output.

**Design.** `tools/compare_runs.py REF NEW`: tier selection from the digests and the provenance (A6 with B1 item 1), the tolerances of T0 to T3 (A6, B1 items 2 to 5), scale classes (a) to (g) and the 10x rule per class (B1 item 4, note M2), the TD statistic in both forms with failure if either |z| exceeds 3.4 (B1 item 5, DEC-0027), leaf accounting (union, one-sided, excluded timing and provenance), and the exit codes 0 pass, 1 failure (a `DEF` line for a verdict), 2 undetermined or usage. It imports `tools/compare_pilot.py` for the flattening and for the chain tags (`cp`, `oracle`, `dynamics`, `fixture`, `network`) of its rule table, which are the only leaf-to-chain map in the repository (the A6 text names the chains without naming leaves). A new tag would be silently treated as network, so a test pins the tag set. Plain-language list of the places where the plan is silent and the strict reading was applied is in the tool's docstring ("Readings that the plan leaves open") and in the hand-back.

**§4.9 checklist (before the first invocation; the tool and the tests are written, nothing has run).**
1. Change set (`git diff --name-only 9039bf5...HEAD` plus `git status --porcelain`): `tools/compare_runs.py`, `tests/unit/test_tools_compare_runs.py`, `tests/unit/fixtures/td_p0p1_parts.json` (new, 5 KB: the 18 primary parts of the DEV-0 pilots P0 and P1), and this file. No `lpcstudy/` file, no change to `tools/compare_pilot.py` or `tools/leafdiff.py`.
2. Radius, `python3 tools/test_impact.py --base 9039bf5 --explain` (the branch point; the tool run against `develop` would also list the radius of .7a, which is already tested at its own tip): rule "`tools/<t>.py` -> `tests/unit/test_tools_<t>.py`"; the fixture is selected through the test that names it. Unit set: `tests/unit/test_tools_compare_runs.py` (one file). By hand, B2 row .9: `tests/unit/test_tools_compare_runs.py`, plus `test_tools_compare_pilot` or `test_tools_leafdiff` only if those tools change; they do not (the tool imports `compare_pilot`, it does not edit it). Smaller than the whole suite; no gate.
3. Already run: no. This set has not run on this code.
4. Device: `JAX_PLATFORMS=cpu` (set by `tools/run_tests.sh`; the tests import no JAX).
5. Threads and time: `LPC_THREADS` 4 (default); wrapper timeout 300 s for unit; the file is pure Python on small dicts and should take a few seconds.
6. Contention: a pilot arm of another lane is running (PID 1947011, `lm-post/runs/dev/wu0005-6/k15`). The unit tier starts no preset and no GPU job, so it runs. No preset is needed for this unit and none is started.
7. Output: `-q --tb=short -rfE` (the wrapper's).
8. Command: `tools/run_tests.sh unit tests/unit/test_tools_compare_runs.py`.

**Evidence runs of the tool (not tests; read-only on DEV-0 results on disk, before the unit run).**
- `python3 -I tools/compare_runs.py --td-only <P0> <P1>` (P0 = `run/p0-1b20db9/.../results.json`, P1 = `run/p1-5b3fd8f/.../results.json`, DEV-0): 18 parts, sum z^2 symmetric 12.65, away 11.99, max |z| 1.69 symmetric and away, no failing part; per-part values equal the printed values of `m1_td_p0p1.log` (e.g. Chua H3c 1.34 and 1.02). Exit 0.
- The WU-0002.14 S3 smoke pair (759d47b, default OpenBLAS kernel against forced Sandybridge; `run/wu0002-14-smokeB/runs/{b,bsandy}/smoke/results.json`) has none of the .7a selecting leaves (`main_digest`, `estimator_digest`, weight digests): `compare_runs.py` exits 2, "tier undetermined", as B1 item 1 requires. To get the per-class declaration, a scratch copy of each file (in the session scratchpad, never in the run directories) got `main_digest` and `estimator_digest` equal on both sides and different `allocator_digest` and estimator `weights_digest` (as a Sandybridge pair would have). Result: tier T2 (`cov_digest`, `whiten_digest`, `unwhiten_digest` differ), 950 differing leaves of 4682, **declared tolerance 1e-5 for class (a)** (largest rel 2.94e-7 at `H1a/by_noise/0.01/ratio_ci/[0]`) **and 1e-4 for (b) to (g)** (largest rel 4.99e-6 at `weight_profile/q25/[165]`, class b); O3 not triggered; `median_iterations` 8 -> 9 passes (within 1); V1 1.7e-16 absolute and V2 9e-16 pass; the discrete count `gain_bound/n_states` 52 -> 54 is listed. **Four failures, all on the T2 premise of A6 "cp chain 1e-12"**: `H1a/by_noise/0.01/{ci_inverse_dim/[0],ci_inverse_dim/[1],fitted_inverse_dim,floor_rms}` are tagged `cp` in `compare_pilot`'s table and differ by 7e-9 to 2.9e-7 relative. They are the H1a median fit of the inverse dimension, a fit on whitened distances, so the W/U ulp change is amplified. The same pair passes them as class (a) QoIs (1e-4). This is a finding about the A6 T2/T3 rule or the chain tag, not a defect of the tool (see the hand-back, Q1).
- Difference with B2 d3's text: the largest class-(a) rel under the stated scale s = max(|lo|, |hi|) is 2.94e-7, not 3.97e-7. 3.97e-7 is |d| / |ref leaf| (no scale) of the same leaf (3.83e-7 / 0.964); `m2_floors.log` itself prints 2.94e-07 for "interval endpoint" and 3.97e-07 only in the "no floor" column. The declarations (1e-5, 1e-4) agree; the test pins 2.94e-7 (hand case at `rel` 3e-7) and the note here records the difference (hand-back, Q2).

**Results.**
- Radius, run once: `tools/run_tests.sh unit tests/unit/test_tools_compare_runs.py`: `166 passed in 0.97s`. No failure, so no `--lf` was needed.
- After that run, two tests of the same file were tightened (no tolerance grew; no assertion was relaxed): `test_lm_estimate_check_hand_cases` now puts each bound at 0.5x and 2x exactly (B2 d2) instead of 0.8x and 1.2x, and `test_t2_t3_fraction_no_decrease_uses_the_two_proportion_bound` moves 0.48x the bound instead of 0.33x. Re-run of those two tests only (a code change had been made): `3 passed in 0.39s` (one test is parametrized over T2 and T3). The rest of the file was not re-run.
- Self-check of the diff. `clip|nan_to_num|isfinite|where(|try:|except`: no clip, `nan_to_num` or `where(` in the tool; the `math.isfinite` sites turn a non-finite difference into an infinite rel (a failure), a non-finite TD input into a "NOT COMPUTABLE" part (exit 2), or a bad `--tol-other` into a usage error; the two `try`/`except` sites report an unreadable input (exit 2) and count a leaf that `compare_pilot`'s table does not tag ("leaves without a chain rule", printed). Nothing is replaced silently. `default_rng|random.|PRNGKey`: none; a test scans the source (also for numpy, scipy, jax and `lpcstudy` imports and for files opened for writing). No tolerance in an assert or `approx` of an existing test changed (the new file only).
- Acceptance (B2 row .9):
  - **d1 truth table:** met on synthetic dicts (instruction of the main session; not on the 164 KB S3 pair): each of the six TD triggers alone gives TD (start_state main and estimator each), W or U alone T2 (three digests), a weight digest alone T3 (three places), all equal on another device T1 (each of six host and device facts), same host, device and threads T0, a missing selecting leaf on either side exit 2 (12 leaves x 2 sides), precedence TD > T2 > T3 > T1. Exact.
  - **d2 half and double:** met for 18 rules (cp, oracle, fixture and dynamics chains, V1 x2, V2, class a x4, classes b to g) x T1, T2, T3, the LM summaries (T1 exact, +-1, 1e-8; T2/T3 two-proportion bound), the 0.1 hw exception (5 count kinds, causal scope) and the two pure LM functions at exactly 0.5x and 2x (`lm_estimate_check`, B1 item 2; the order-statistic band is tested by its hand ranks). **The T1 per-estimate check and the T2/T3 order-statistic bands are not wired into the command line**: they need the per-estimate arrays of the .7b dump, whose schema does not exist at this commit. The tool reports them NOT COMPUTED and exits 2 unless `--allow-not-computed` (Q4).
  - **d3 kernel pair:** met in declarations (1e-5 for (a), 1e-4 for (b) to (g), O3 not triggered), by the evidence run above on the real pair (scratch copies with injected digests) and by a synthetic hand case in the test; the quoted 3.97e-7 is not the class-(a) rel (Q2).
  - **d4 P0/P1:** met on the extracted fixture: sum z^2 12.65 and 11.99, max |z| 1.69 (abs 0.005 against the log), no part fails; the same numbers come out of the evidence run on the two real files.
  - **d5 accounting:** met: union and one-sided counts, every difference with class, rel, tolerance and outcome (`--all`; by default every failure and the first `--show` of a passing group), timing and provenance listed as excluded with counts.

#### WU-0003.9 fix round 1 (developer claude-sonnet-5-5, 2026-10-14; review `WU-0003.9-review.md`, commit 7a46e2f; findings R1 to R4, R7 to R11, R13; R5, R6, R12 and Q1 are not in this round)

Needs owner review before freeze. Tool and tests only; no `lpcstudy/` file, no preset, no RNG, no tolerance loosened. No number of A6 or B1 changed; the changes make the tool stricter or fix its handling of the real schema.

Record of the d1 change (R10): B2 d1 fixes truth-table fixtures "built from the WU-0002.14 S3 smoke pair (164 KB each)". The first implementation used synthetic dicts on the instruction of the main session (task message of 2026-10-14, which also said not to copy large results into tests). That instruction is not a dated plan amendment; the planner or owner should record it as one, or require the 164 KB fixtures (open question Q6 in the hand-back). To close the schema gap that let R1, R3 and R9 escape, the synthetic tree now embeds a 10 KB extract of the real S3 results (`tests/unit/fixtures/real_schema_extract.json`): the `handling` subtree of lorenz63 with its LM kinds, the top-level `handling` block, the `clip_sensitivity` block.

Changes by finding (details under each finding in the review file): R1 `licensing_kind` and `count_scope` rebuilt to A6's list and per-system causal scope; R2 `td_statistic` uses the union of systems and counts a missing system's parts as not computable; R3 `lm_rules` (T3: T2 rules for the `eval` kind, T1 rules otherwise); R4 `--tol-other` above 1e-4 is refused (exit 2); R7 per-leaf-group selecting check on both runs, top-level estimator digests required; R8 a `cov_digest` difference alone is undetermined; R9 `is_verdict_str` (`verdict*`, `*_verdict`, `reading`, `status`) and `best_single*` as discrete; R10 above; R11 the three cases made 0.5x and 2x; R13 the docstring now says the untagged-as-network choice is the looser one and an owner reading.

**§4.9 checklist (before the first invocation of this round; code and tests are written, nothing has run on them).**
1. Change set (`git diff --name-only 9039bf5...HEAD` plus `git status --porcelain`): `tools/compare_runs.py`, `tests/unit/test_tools_compare_runs.py`, `tests/unit/fixtures/td_p0p1_parts.json`, `tests/unit/fixtures/real_schema_extract.json` (new, 10 KB), this file and `WU-0003.9-review.md`. Untracked files of other agents (`docs/agent/notes/2026-10-14-math-wu0003-9-*`) are not touched.
2. Radius, `python3 tools/test_impact.py --base 9039bf5 --explain`: rule "`tools/<t>.py` -> `tests/unit/test_tools_<t>.py`"; the fixtures are selected through the test that names them. Unit set: `tests/unit/test_tools_compare_runs.py` (one file). Smaller than the whole suite; no gate; the file is run once after this code change.
3. Already run: not on this code (the round-0 run, `166 passed`, was on the previous code).
4. Device: `JAX_PLATFORMS=cpu` (wrapper); no JAX import.
5. Threads and time: `LPC_THREADS` 4; wrapper timeout 300 s; the file took 1 s before.
6. Contention: a pilot arm of another lane is running (PID 1972909, `k30`); this unit tier starts no preset and no GPU job.
7. Output: `-q --tb=short -rfE`.
8. Command: `tools/run_tests.sh unit tests/unit/test_tools_compare_runs.py`.

**Results of fix round 1.**
- Radius, run once on the new code: `tools/run_tests.sh unit tests/unit/test_tools_compare_runs.py`: `2 failed, 211 passed in 1.82s`. Both failures were one test, `test_t2_rules_fraction_no_decrease_uses_the_two_proportion_bound[T2, T3]`, whose typed sanity values (0.0777, 0.4363) were my wrong estimates of the fixed points; the tool's solved moves 0.07843 and 0.41081 were checked by hand (pbar 0.13922, bound 0.15687 = 2 x 0.07843; pbar 0.30541, bound 0.20541 = 0.41081 / 2). The literals were corrected to those hand values (abs 1e-5; no tolerance of the tool or of the criterion changed). Then `tools/run_tests.sh unit --lf tests/unit/test_tools_compare_runs.py`: `2 passed, 211 deselected in 0.30s`.
- Self-check of the diff. `clip|nan_to_num|isfinite|where(|try:|except` sites: unchanged in kind (see the round-0 line above); the new refusal of `--tol-other` raises `ToolError` (exit 2) and is counted nowhere because nothing is replaced. `default_rng|random.|PRNGKey`: none (the hygiene test scans the source). No tolerance in an `assert` or `approx` of the file grew; the only literal changed is the one above, to the hand value.
- Evidence run again on the scratch copy of the S3 pair (T2, injected digests): declared tolerance still 1e-5 for (a) and 1e-4 for (b) to (g); the four H1a `cp` failures remain (Q1, not in this round). New: 2 integer leaves now FAIL, `gain_bound/n_screened_out/negative_covariance` 25 -> 23 and its `handling/result_counts` mirror, because `n_screened_out` is not on A6's list (`n_states` is, and `gain_bound/n_states` 52 -> 54 stays listed). This follows the strict reading the main session asked for; whether `n_screened_out` is a state count that should license 0.1 hw is an owner question (Q7).

#### WU-0003.9 fix round 2 (developer claude-sonnet-5-5, 2026-10-14; basis: mathematician's note `2026-10-14-math-wu0003-9-q1.md`, c2e1374)

Needs owner review before freeze. Only stricter or informational changes; no tolerance loosened; the re-tagging OF-7 (H1a fit outputs to the QoI rule) is **not adopted** (a loosening, with the owner). Tool and tests only; no preset, no RNG.

1. The cp 1e-12 rule stays on the four H1a fit leaves; a pointer to the note (OF-7, working default cp 1e-12) is printed beside any failure under `H1a/by_noise` (rows and one report line); the exit code is unchanged.
2. The cp 1e-12 rule now applies to `H1a/inverse_dim_reference` and `H1a/by_noise/*/median_seed_by_n_lib/*` (untagged in `compare_pilot`'s table).
3. Census: the report prints the number of differing untagged float leaves that fall through to the network (looser) class and the untagged float leaves of the reference run by block (information, never a failure). The count by block is not pinned in a test on the real-schema extract (it holds only `handling` and `clip_sensitivity`, where the count is not meaningful); it is tested on a hand-known tree.
4. The 3.97e-7 slip: it is not in the tool docstring. In this Log (round 0, "Difference with B2 d3's text") it is stated correctly: 3.97e-7 is |d| / |ref leaf| with no scale, 2.94e-7 is the class-(a) rel under s = max(|lo|, |hi|). The test table lists 3.97e-7 only as one input of the 10x rounding (both give 1e-5). No change needed.

**§4.9 checklist (before the first invocation of this round; code and tests are written, nothing has run on them).**
1. Change set (`git diff --name-only f381a48...HEAD` plus `git status --porcelain`): `tools/compare_runs.py`, `tests/unit/test_tools_compare_runs.py`, this file. The mathematician's note (c2e1374) is already committed and is not edited.
2. Radius, `python3 tools/test_impact.py --base 9039bf5 --explain`: rule "`tools/<t>.py` -> `tests/unit/test_tools_<t>.py`". Unit set: `tests/unit/test_tools_compare_runs.py`, once after this code change. Smaller than the whole suite; no gate.
3. Already run: not on this code (round 1: `2 failed, 211 passed`, then `2 passed` with `--lf`, on the previous code).
4. Device: `JAX_PLATFORMS=cpu` (wrapper), no JAX import.
5. Threads and time: `LPC_THREADS` 4; wrapper timeout 300 s; the file took 2 s.
6. Contention: no preset or GPU job is started here; another lane's pilot may be running.
7. Output: `-q --tb=short -rfE`.
8. Command: `tools/run_tests.sh unit tests/unit/test_tools_compare_runs.py`.

**Results of fix round 2.** Radius, run once: `tools/run_tests.sh unit tests/unit/test_tools_compare_runs.py`: `224 passed in 3.10s` (211 + 2 of round 1, plus 11 new cases: 9 for the untagged H1a leaves x T1, T2, T3, one for the pointer, one for the census). Self-check: no clip, `nan_to_num` or `where(`; no new `try`/`except`; no RNG; no tolerance changed. Evidence run on the scratch copy of the S3 pair (T2): `median_seed_by_n_lib/*` (3 leaves, max 8.2e-15) pass the cp rule, the four H1a fit leaves still fail (1e-12 kept) with the pointer printed once, exit 1 as before; census line: 84 differing untagged float leaves fall through to the class rules, 533 untagged float leaves in the reference run (H1a 9, H1b 2, H1c 6, H1d 10, H2a 16, H2b 19, ...).

## Review

## Audit
