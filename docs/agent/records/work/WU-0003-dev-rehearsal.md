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

## Log

## Review

## Audit
