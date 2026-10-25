# WU-0037: why V7 fails on S2 to S6, and estimator-side fixes

**DEVELOPMENT (DEV-3): not a hypothesis test.** Every number in this note is a development number. It is either a stored leaf of the DEV-3 full-preset GPU runs or a CPU reproduction on DEV-3. No confirmatory seed was drawn, read or used.

- **Author:** applied-mathematician (claude-opus-5-5), 2026-10-25.
- **Worktree:** `wu/0037-v7-diagnosis`, from `develop` at 2a630bb.
- **Scope:** diagnosis and proposals only. `lpcstudy/` is unchanged. The V7 band [0.9, 1.1], the noise levels, M = 200 and every criterion stay as they are (PRIME.2).
- **Runs:** CPU scratch computations only, at nice 19, on one or two cores (§9). I made no GPU run and no preset run, so no `--states-dump` run was needed.

## 1. Result in one table

| System | Mechanism found | Key evidence (DEV-3) | Proposed fix | Expected V7 with fix (CPU, DEV-3) | Judgement |
|---|---|---|---|---|---|
| S2 lorenz63_r166 | LM ends in a **wrong local minimum** from the network start | 24–30% of draws far, against 0.1–0.5% on lorenz63; ≥ 99.7% of far draws cost more than the truth-started fit; more iterations do not help; truth start passes | **F1** two-start LM (network, nearest estimator pair), keep the lower cost; **F2** add the window-continuation start | F1: 1.014 / 1.028 / 1.018 / 1.038, slope 1.002 | fixable |
| S3 rossler_z | **noise outside the linear regime** (large ν), not wrong basins | far draws 0.13–0.35%, as on the frozen systems; the truth-started LM itself fails (slope 0.893; 0.817 at 5%); ratio 1.12 for ρν ∈ [0.1, 0.3) and 0.35 for ρν > 1 | none that acts on the mechanism (§5.2) | F1: slope 0.878, fail | **not fixable without a design change** |
| S4 hindmarsh_rose | wrong local minimum; the basin is narrow even for good starts | 42–49% of draws far, all wrong minima; the share far does not depend on the start error (51% for a start error < 0.05 whitened); truth start 0.97–0.98 | F1; F2 as for S2 | F1: 0.985 / 0.986 / 0.987 / 1.001, slope 1.005 | fixable (V1 risk separate, §5.3) |
| S5 hyper_jha | wrong local minimum; the affected share of states crosses one half only at ρ = 5% | 16–21% of draws far; states with ≥ 1 wrong-minimum draw 27 / 33 / 47 / **58%** | F1; F2 | F1: 1.002 / 1.003 / 1.004 / 1.016, slope 1.002 | fixable |
| S6 lorenz96_4 | as S5 | 17–19% of draws far; states affected 32 / 39 / 50 / **70%** | F1; F2 | F1: 1.003 / 1.005 / 1.011 / 1.024, slope 1.005 | fixable |

The medians are given at ρ = 0.5 / 1 / 2 / 5%, with "slope" the median slope. They come from the first 40 to 200 test-sweep states of a CPU realization (§3). Intervals are in §4.6.

**Prediction for WU-0040.** WU-0040 (GPU, 1000 states, DEV-1, DEV-3 and DEV-4) is the actual test of these predictions:

- **S2, S4, S5, S6:** with F1, V7 passes. The predicted margin to the band edge is at least 0.06 at every level. The smallest margin is S2 at 5% (upper 95% limit 1.07 on 100 states).
- **S3:** fails V7 with or without F1.

## 2. Why V7 is so sensitive to a few bad draws

V7 (`analysis.v7_efficiency`) uses δ_i, the root mean square over the M = 200 oracle draws of the whitened state error at time t (`ensemble.ensemble_moments`, `est_seed`). It divides δ_i by ρν_i, where ν_i is the noise-free **oracle** ν at the true window-start state (`v7_noise_scaling` reads `oracles["test"].nu`).

**Derivation.** Assume k of the M draws are far, with error E, and the other M − k are first-order efficient, with mean square (ρν)². Then

  (δ_i/ρν_i)² ≈ (M − k)/M + k E² / (M (ρν_i)²),

so δ_i/ρν_i ≤ 1.1 requires k E² ≤ (0.21 M + k)(ρν_i)². For k = 1 and M = 200, this needs E ≤ 6.5 ρν_i.

**Measured far errors.** The wrong-minimum errors are 0.9–3.2 whitened units, which is the attractor scale. That is **15 to 166 times ρν** (`out/far_size.out.txt`).

**Consequences:**

- A single far draw in 200 already puts a state far above the band.
- The median over states fails as soon as more than about half the states have at least one wrong-minimum draw. This is the mechanism the 2026-10-20 notes predicted: "δ tracks the attractor size, not ρν".
- E does not depend on ρ, so the ratio of an affected state falls roughly as 1/ρ. This explains the stored S2 and S4 medians, which decrease with ρ, and the S4 slope of 0.405 (δ is nearly constant in ρ).

**How "far" is counted.** A draw is *far* when its final cost satisfies c > χ²₀.₉₉₉(D − m) ρ². This is the code's own goodness-of-fit reading, `fraction_above_chi2`.

- **Chance level.** In the correct basin, 0.1% of draws exceed the threshold by chance, so 1 − 0.999²⁰⁰ = 18% of states have at least one such draw with no defect. The truth rows of §4.3 show this floor (17–22% of states).
- **Wrong local minimum.** A far draw is a *wrong local minimum* when the LM started at the true window-start state, on the same noisy vector, reaches a lower cost (by more than 10⁻⁹ relative).

## 3. Method

1. **Stored leaves** (`stored_lm.py` → `stored_lm.out.md`). These are read-only. For each extension run and for ens-DEV-3, the script takes:
   - the V7 medians and their intervals;
   - the per-cell LM summaries of the oracle draws: c/ρ² quantiles, the share above χ², accepted iterations and late progress;
   - the network validation loss per ρ.
2. **CPU reproduction** (`diag.py`). The package is imported read-only, and the context is built with `Study.context` at the full preset on DEV-3:
   - **Noise:** the run's own oracle unit noise (`Study.unit_noise`, labels `(seed, system, 7, "test", "oracle")`).
   - **Estimator:** trained by `Study.setup` at the design settings (40 epochs, 10⁵ pairs, widths 64/128).
   - **λ:** the stored GPU Lyapunov cache is copied in, so the interval Δ is the run's.
   - **Not bitwise.** CPU and GPU arithmetic differ (`main_digest` differs, as expected across devices, DEF-0023/24). The orbit is a different realization of the same attractor, and the network is a CPU-trained copy of the same recipe. Its validation losses are within about 10% of the stored ones, for example S6 at 5%: 0.137 against 0.138.
   - **States:** the first N test-sweep states, with N = 200 (S6), 150 (S3), 100 (S2, lorenz63), 60 (S4, S5) and 40 (S1). All M = 200 draws and all four ρ are used.
3. **Variants** (production LM arithmetic: damping 10⁻³, ÷3 on accept, ×4 on reject):

   | Variant | Start | Iterations | Deployable |
   |---|---|---|---|
   | `prod` | network | 15 | yes (production) |
   | `it30`, `it60` | `prod` result, refined further; damping restarted per segment | 30 and 60 in all | yes |
   | `truth` | true window-start state | 15 | no |
   | `pair_nn` | target of the nearest noise-free training input among the estimator's own 10⁵ pairs (`ctx.estimator_inputs` / `estimator_targets`) | 15 | yes |
   | `cont` | network; LM on the m + 1 oldest delay coordinates, adding one coordinate per stage (5 iterations each), then all 7 | 15 on all 7 | yes |
   | `analog` (S6 only) | CP's nearest library analog | 15 | rejected (below) |
   | `ms_pp` = **F1** | the lower final cost of `prod` and `pair_nn` | — | yes |
   | `ms2` | the lower final cost of `prod` and `cont` | — | yes |
   | `ms3` = **F2** | the lower final cost of `prod`, `cont` and `pair_nn` | — | yes |
   | `best_truth` | the lower final cost of `prod` and `truth` | — | no |

   - **`analog` rejected.** A library start would make PLP depend on the library, and H2b(ii) and H2e measure exactly that dependence.
   - **`best_truth`** is an upper bound on what any change of start can give.
4. **Equivalence check.** My LM against `StateEstimator.estimate_counted` on the same inputs (2000 draws per level; all draws on S6):
   - **Result:** the largest error difference is 2.5·10⁻⁸ whitened (S2 at 5%; S6 bitwise 0), and the largest cost difference is 1·10⁻¹⁰.
   - **Tolerance.** The smallest ρν_i in any sample is above 2·10⁻³, so the difference is below 10⁻⁵ relative. It is round-off through a chaotic 30-step map under a different batch shape, not an algorithmic difference.
   - **S1:** the comparison is NaN because some `prod` draws are non-finite (§4.6).
5. **Intervals.** I used a moving-block bootstrap (block 5, 2000 resamples), as V7 does, through `statistics.block_bootstrap_dropped`, with generators from `make_rng(DEV-3 seed, "WU-0037", system, variant, level)`.

## 4. Evidence by mechanism

### 4.1 Stored LM leaves (oracle draws of the noise-sweep cells, 200 000 per ρ; DEV-3)

| System | share c/ρ² > χ²₀.₉₉₉ at ρ = 0.5 / 1 / 2 / 5% | p95 c (normalized units) | late progress | net val loss |
|---|---|---|---|---|
| lorenz63, rossler, chua | 0.001–0.020 | 2.5·10⁻⁴ to 0.027 (scales as ρ²) | 0.001–0.036 | 0.0006–0.016 |
| S1 rossler_hyper (passes) | 0.016–0.019 | 2.1·10⁻⁴ to 0.022 | 0.02–0.06 | 0.11–0.24 |
| S2 | **0.248 / 0.271 / 0.299 / 0.322** | **5.7 / 6.7 / 6.6 / 7.8 (flat in ρ)** | 0.25–0.49 | 0.065–0.081 |
| S3 | 0.0022 / 0.0024 / 0.0023 / 0.0036 | 2.4·10⁻⁴ to 0.024 (∝ ρ²) | 0.08–0.29 | 0.026–0.18 |
| S4 | **0.41–0.42** | **14 / 13 / 14 / 16** | 0.46–0.56 | 0.011–0.035 |
| S5 | **0.21–0.23** | **3.6 / 3.5 / 3.5 / 4.3** | 0.23–0.29 | 0.16–0.24 |
| S6 | **0.15–0.17** | **1.06 / 1.05 / 1.14 / 1.28** | 0.18–0.29 | 0.075–0.14 |

A p95 cost that does not scale with ρ² is the signature of wrong-basin fits. The runs already stored it. S3 does not show it.

### 4.2 Reproduction fidelity (production estimator, CPU, against the stored GPU V7 on 1000 states)

| System | ρ = 0.5% | 1% | 2% | 5% | slope |
|---|---|---|---|---|---|
| S2 | 1.07 (1.111) | 23.97 (25.98) | 18.54 (16.42) | 10.43 (11.25) | 0.950 (0.927) |
| S3 | 1.030 (1.025) | 1.048 (1.070) | 1.068 (1.111) | 0.970 (0.938) | 0.841 (0.872) |
| S4 | 106 (67.9) | 51.8 (52.5) | 42.0 (32.5) | 17.5 (17.2) | 0.318 (0.405) |
| S5 | 1.015 (1.029) | 1.025 (1.041) | 1.114 (1.081) | 1.531 (3.376) | 1.002 (1.005) |
| S6 | 1.027 (1.023) | 1.040 (1.037) | 1.079 (1.094) | 2.456 (2.753) | 1.027 (1.011) |
| lorenz63 (control) | 0.995 (1.000) | 0.995 (1.002) | 0.995 (1.004) | 1.002 (1.009) | 1.001 (1.001) |

Stored values are in parentheses.

- **Medians.** Every stored median and slope lies inside the reproduction's 95% interval. I checked this at full precision for S3, S5, S6 and lorenz63, and from the printed intervals for S2 and S4 (`analyze.out.md`).
- **Flags.** The overall V7 outcome (fail on S2 to S6, pass on lorenz63) is reproduced. Per-level flags differ only where the stored median is within 0.03 of the band edge: S2 at 0.5%, S3 at 2%, and S5 at 2%.
- **Wide intervals.** The reproduction intervals are wide where the per-state ratios are bimodal. For example, S2 at 0.5% has [1.04, 44.1]: the median sits on the edge between unaffected and affected states.

### 4.3 Wrong-basin test (production estimator)

| System | share of draws far | of which wrong local minimum | states with ≥ 1 wrong-minimum draw (ρ = 0.5 / 1 / 2 / 5%) | far draws, truth start | far draws, F1 (`ms_pp`) | far draws, F2 (`ms3`) |
|---|---|---|---|---|---|---|
| S2 | 0.24–0.30 | ≥ 99.7% | 0.46 / 0.60 / 0.66 / 0.82 | 0.0008–0.0009 | 0.020–0.069 | 0.018–0.050 |
| S3 | 0.0013–0.0035 | 57–80% (near chance level) | 0.13 / 0.11 / 0.14 / 0.17 | 0.0010–0.0011 | — | 0.0009–0.0010 |
| S4 | 0.43–0.49 | ≥ 99.9% | 0.70 / 0.72 / 0.73 / 0.80 | 0.0009–0.0016 | 0.001–0.054 | 0.001–0.038 |
| S5 | 0.16–0.21 | ≥ 99.5% | 0.27 / 0.33 / 0.47 / **0.58** | 0.0014 | 0.005–0.074 | 0.005–0.029 |
| S6 | 0.17–0.19 | ≥ 99.5% | 0.32 / 0.39 / **0.50** / **0.70** | 0.0009 | 0.001–0.027 | 0.001–0.016 |
| S1 (passes) | 0.003–0.030 | ≥ 77% | 0.08 / 0.10 / 0.13 / 0.25 | 0.0006–0.0008 | — | 0.0006 |
| lorenz63 (control) | 0.001–0.005 | 0–80% | 0.00 / 0.02 / 0.05 / 0.10 | 0.0011 | — | 0.0011 |

Under F1 the residual far draws are largest at the smallest ρ, where they matter most. They now fall on fewer states, so the medians pass (§4.6). F1 selects the pair start in 61–81% of draws, but most of these selections are round-off-level cost differences between two fits of the same minimum (see §6, item 4).

**S5 and S6 fail only at 5%.** On these systems the median crosses 1.1 exactly where the share of affected states passes one half. The share grows with ρ because the network's start error grows with ρ: on S6 the median start error is 0.15 / 0.15 / 0.18 / 0.24 for the draws that converge and 0.30 / 0.28 / 0.34 / 0.37 for the far ones. The states without a far draw sit at 1.004–1.05 on every system.

**Start error and basin size** (share of draws ending far, by bin of the network start error in whitened units, pooled over ρ; `analyze.out.md`):

- **S6:** 0.013 below 0.05, 0.10 in [0.1, 0.2), 0.39 in [0.4, 0.8).
- **S5:** 0.002, 0.15, 0.45 in the same bins.
- **S2:** 0.10 already below 0.05, and 0.51 in [0.1, 0.2).
- **S4:** 0.51 below 0.05, about 0.4 in every bin. The S4 basin in whitened state distance is narrower than any start the network can give. A start a few hundredths of a whitened unit off shifts the spike timing inside the 1-LT window (g_H at 1 LT has a 95th percentile of 1 720, note specs-2 §1.1), and the Gauss–Newton step from there lands in another minimum.

**Why the estimator-pair start works.** It is a real attractor point whose noise-free delay vector is the nearest one to the observation. Its residual is therefore already of the order of the noise plus the neighbour distance, and it lies on the same branch of the delay map (same spike phase, same lobe). This is an explanation consistent with the numbers, not a proof.

### 4.4 Iteration study (convergence-study skill; parameter: LM iterations 15, 30, 60, ratio 2; the same draws)

| System, ρ | median ratio, 15 / 30 / 60 iterations | far share, 15 / 60 |
|---|---|---|
| S2, 1% | 23.97 / 25.09 / 24.71 | 0.283 / 0.269 |
| S4, 1% | 51.8 / 49.7 / 45.7 | 0.458 / 0.370 |
| S5, 5% | 1.531 / 1.461 / 1.479 | 0.161 / 0.155 |
| S6, 5% | 2.456 / — / 2.265 (60 from the start) | 0.178 / 0.158 |
| S3, 2% | 1.068 / 1.091 / 1.119 | 0.0013 / 0.0012 |

**Reading.** Quadrupling the budget changes no median by more than 12%, and the far share by at most a fifth. The far draws are stationary points, not unconverged iterates. The high stored late-progress fractions (§4.1) mark iterates that are still moving inside a wrong basin.

**Ruled out as a fix:** more iterations. An observed order is not meaningful here: the differences do not shrink geometrically, and the fixed point is the wrong one.

### 4.5 Is ν mis-scaled? (Jacobian conditioning, 99th-percentile cap)

- **The cap does not enter V7.** V7 uses the oracle ν at the true state. The 99th-percentile cap (`allocation.ProfileProxies.features`, `nu_cap_clips`) acts only on the deployable ν̂ features. This is ruled out from the code, not tested.
- **Conditioning: ν is right.** The truth-started LM gives median ratios inside [0.97, 1.02] at every ρ on S2, S4, S5 and S6 (§4.6). By ρν bin, it gives 0.976–1.021 wherever ρν < 0.1 on all six systems. A mis-scaled ν (an ill-conditioned AᵀA) would shift these ratios. V2 (stored 0.967–1.02) agrees on 5 states per system.

### 4.6 Nonlinear regime at large ρ, and the candidate fixes

Per variant, the median ratio at ρ = 0.5 / 1 / 2 / 5% and the median slope, with 95% block-bootstrap intervals in `analyze.out.md`:

| System | `truth` (not deployable) | F1 `ms_pp` | F2 `ms3` | `pair_nn` alone | `cont` alone |
|---|---|---|---|---|---|
| S2 | 1.004 / 1.010 / 1.014 / 0.993; 0.999 ✓ | 1.014 / 1.028 / 1.018 / 1.038 [0.991, 1.07]; 1.002 ✓ | 1.008 / 1.029 / 1.026 / 1.049 [0.997, 1.09]; 1.002 ✓ | ✓ | 3.02 at 5% ✗ |
| S3 | 1.005 / 1.009 / 1.002 / **0.817**; **0.893** ✗ | 1.030 / 1.048 / 1.070 / 1.046; **0.878** ✗ | 1.042 / 1.058 / **1.24** / **1.22**; **0.885** ✗ | 1.021 / 1.035 / 1.077 / 1.048; 0.906 [0.80, 1.06] (marginal) | ✗ |
| S4 | 0.983 / 0.983 / 0.978 / 0.972; 1.003 ✓ | 0.985 / 0.986 / 0.987 / 1.001; 1.005 ✓ | 0.989 / 0.987 / 0.989 / 1.012; 1.005 ✓ | ✓ | ✗ (6–11 at ρ ≥ 1%) |
| S5 | 1.000 / 1.002 / 1.000 / 1.005; 1.002 ✓ | 1.002 / 1.003 / 1.004 / 1.016; 1.002 ✓ | 1.002 / 1.004 / 1.004 / 1.016; 1.003 ✓ | ✓ | 1.10 at 5% (edge) |
| S6 | 1.001 / 1.003 / 1.007 / 1.018; 1.004 ✓ | 1.003 / 1.005 / 1.011 / 1.024; 1.005 ✓ | 1.003 / 1.004 / 1.011 / 1.026; 1.005 ✓ | ✓ | 1.21 at 5% ✗ |
| S1 (passes stored) | ✓ | 0.999 / 0.992 / 0.987 / 0.996; 1.000 ✓ | ✓ | ✓ | (non-finite draws) |
| lorenz63 (control) | ✓ | 0.995 / 0.995 / 0.994 / 1.000; 1.001 ✓ | identical to F1 | ✓ | ✓ |

**S1 non-finite draws.** On S1, `prod` and the variants started from it have 9 / 26 / 44 / 132 non-finite draws out of 8000 per ρ. The package replaces these with the invariant mean and counts them; my script leaves them NaN, so those medians are NaN. The `pair_nn` and `truth` starts have none.

**The S3 linear-regime test** (truth start, by ρν bins):

| ρν (whitened) | median ratio | p90 |
|---|---|---|
| < 0.03 | 0.997 | 1.03–1.05 |
| [0.03, 0.1) | 1.021 | 1.16 |
| [0.1, 0.3) | **1.117** | 1.61 |
| [0.3, 1) | **0.890** | 1.35 |
| ≥ 1 | **0.345** | 0.72 |

- **Where the S3 states sit.** The median S3 state has ν = 14.6 (p90 64.5), so its ρν is 0.07 / 0.15 / 0.29 / 0.73 at the four levels. From ρ = 1% on, half the states are outside the first-order regime: δ first exceeds ρν (second-order terms), then saturates at the attractor scale and falls below it.
- **Converged iterations do not rescue it** (`diag_converged.py`, `out/rossler_z.converged.json`). From the truth start, 15 → 30 → 60 iterations move the slope 0.893 → 0.919 → 0.921 and the 5% median 0.817 → 0.878 → 0.905. From the pair start, the 2% median moves 1.077 → 1.090 → **1.116** and the slope 0.906 → 0.923 → 0.930.
- **Multiple minima.** The two converged starts disagree at 2% (1.008 against 1.116), so the objective has several minima in the poorly observed directions.
- **Even the oracle start sits at the band edge.** Even with the truth start and 60 iterations, V7 is at the edge (0.905 at 5%).

## 5. Diagnosis and proposals per system

### 5.1 S2 lorenz63_r166

**Mechanism tested.** Wrong basin: **confirmed**.

- 24–30% of draws end in local minima of higher cost than the truth's, with errors of 1.5–1.9 whitened units (22–166 ρν).
- More iterations do not help.
- The truth start passes.

**Nonlinear regime:** tested and **not the cause**. The truth-start ratio is 0.99–1.01; only 17 of 400 state-levels have ρν ≥ 0.1.

**F1 (two-start LM).** Run the production LM from the network start and from the nearest estimator training pair, and keep the estimate with the strictly lower final cost (ties go to the network result).

- Expected V7: 1.014 / 1.028 / 1.018 / 1.038, slope 1.002.
- Far share falls from 0.24–0.30 to 0.02–0.07; it is largest at 0.5%.

**F2 (three-start).** F1 plus the window-continuation start (`ms3`); this is the fallback if F1 misses on DEV-1 or DEV-4. Expected V7: 1.008 / 1.029 / 1.026 / 1.049.

### 5.2 S3 rossler_z

**Wrong basin:** tested and **ruled out**. The far share is 0.13–0.35%, against a chance level of 0.1% and 0.1–0.5% on lorenz63.

**Nonlinear regime:** tested and **confirmed as the cause**.

- The truth-started LM fails V7 itself: slope 0.893 at 15 iterations and 0.921 at 60, with the 5% median 0.817–0.905.
- The ratio depends on ρν exactly as a leave-the-linear-regime effect would (§4.6).
- The first-order prediction ρν does not describe the error of any estimator of this objective at ν ≈ 15 and ρ ≥ 1%.

**Judgement: not fixable without a design change.**

- **Starts.** Every deployable start I tested fails, or passes only marginally. F1 fails (slope 0.878), and F2 fails (1.24 at 2%).
- **`pair_nn` alone.** It is inside the band at 150 states (slope 0.906 [0.80, 1.06]; 1.077 [1.02, 1.15] at 2%), but with 60 iterations it leaves it (1.116 at 2%). That pass comes from two nonlinear effects that cancel, not from efficiency. I do not propose it, because a V7 pass reached that way would not mean what V7 claims.
- **No proposal.** I propose no fix and recommend reporting S3 as not admitted, with the reason "estimation error outside the first-order regime (median ν = 14.6)". This is the outcome the 2026-10-20 note pre-stated for S3 as "itself the finding".
- **Outside this unit's authority.** Restricting V7 to ρν < 0.1, or changing the noise levels or the observable, would be a criterion or design change, and none of those is proposed here.

### 5.3 S4 hindmarsh_rose

**Mechanism tested.** Wrong basin: **confirmed**, and it is the strongest case.

- 42–49% of draws end far, with ≥ 99.9% of them wrong minima.
- The share is about 0.4–0.5 whatever the start error, so the basin is narrower than the network's accuracy (§4.3).
- More iterations remove a fifth of the far draws and leave the medians at 15–105.

**Nonlinear regime:** tested and **not the cause**. The truth start gives 0.972–0.983 at every ρ, with slope 1.003.

**Proposals:**

- **F1:** expected 0.985 / 0.986 / 0.987 / 1.001, slope 1.005.
- **F2:** expected 0.989 / 0.987 / 0.989 / 1.012.

**Separate admission risk (not V7).** The specs-2 note §13(1) expects V1 to fail on S4 in about two seeds of three, from the fixed finite-difference step on spike edges. DEV-3 stored a pass, 4.3·10⁻⁶. An estimator fix cannot change this.

### 5.4 S5 hyper_jha

**Mechanism tested.** Wrong basin: **confirmed**. 16–21% of draws are far, all wrong minima.

**Why only 5% fails.** The share of states affected crosses one half only at 5% (0.27 → 0.58), because the network start error grows with ρ. Below 5% the median state is unaffected, which explains the stored pattern: 1.03 / 1.04 / 1.08 / 3.38 with slope 1.005.

**Nonlinear regime:** tested and **not the cause**. The truth start gives 1.000–1.005.

**Proposals:**

- **F1:** expected 1.002 / 1.003 / 1.004 / 1.016.
- **F2:** expected 1.002 / 1.004 / 1.004 / 1.016.
- **Small-sample caution.** S5 has only 60 states here, so these intervals are the widest of the four fixable systems (F1 at 5%: [0.999, 1.04]).

### 5.5 S6 lorenz96_4

**Mechanism tested.** Wrong basin: **confirmed**. The affected share of states is 0.32 → 0.70, and the median passes 1.1 between 2% (exactly 0.50; 1.079) and 5%.

**Nonlinear regime:** tested and **not the cause**. The truth start gives 1.001–1.018.

**Other variants:**

- 60 iterations: 2.27 at 5%, no fix.
- The library-analog start passes (1.031 at 5%) but is rejected (§3, item 3).

**Proposals:**

- **F1:** expected 1.003 / 1.005 / 1.011 / 1.024, slope 1.005.
- **F2:** expected 1.003 / 1.004 / 1.011 / 1.026.

## 6. Implementation brief for WU-0039 (F1, and F2 as the fallback)

1. **Per-system switch.** Add a field to `SystemSpec`, for example `estimator_starts: tuple[str, ...] = ("network",)`.
   - Set it to `("network", "pair")` for S2, S4, S5 and S6 (F1), or to `("network", "pair", "continuation")` (F2).
   - Leave the default on lorenz63, rossler and chua, and on S1 (it passes; no change is needed there) and S3 (no fix).
   - **Bitwise guarantee.** The branch is taken in Python before tracing. The frozen systems then compile the identical function and draw no new random number, so they stay bitwise unchanged. The WU-0039 leafdiff criterion (0 changed, 0 removed) checks this.
2. **Pair start.** Build a `scipy.spatial.cKDTree` once per context on `ctx.estimator_inputs` (noise-free, normalized). For a noisy delay vector X_t, the start is `ctx.estimator_targets[nn(X_t)]`, which is already a whitened window-start state.
   - The query is deterministic and host-side, with no randomness and no library dependence.
   - It uses PLP's own training data only, so H2b and H2e keep their design separation.
3. **Selection.** Run the unchanged LM loop (`refinement().refine`, 15 iterations) from each start. Keep the result with the strictly lowest final cost; ties go to the network start. `LMDiagnostics` reports the selected run.
4. **Counts (PRIME.4).** Add per-cell counts, report-only, beside the LM block:
   - estimates where a non-network start was selected (`lm_start_switched`);
   - the same with the cost lower by more than 10⁻⁶ relative (`lm_start_switched_material`).

   Two counts are needed because in this diagnosis the pair start was selected in 61–81% of draws, mostly by round-off between two fits of the same minimum. Only the material count says how often the start changed the basin.
5. **Cost.**
   - The LM work of the four systems doubles under F1 and roughly quadruples under F2. The continuation stages cost (D − m − 1) × 5 iterations.
   - The kd-tree query on 10⁵ points is negligible.
   - The forecasts after the estimate are unchanged.
6. **Not changed.** V7 and V2 code, ν, the cap, M, the noise levels and the band are all unchanged.
7. **What WU-0040 must show.** For F1 to be accepted, V7 must pass at 1000 states on DEV-1, DEV-3 and DEV-4 on the GPU. If one seed misses, F2 is the second and last fix allowed for that system (ROADMAP §9 decision 2).

## 7. Uncertainty budget of the diagnosis numbers (QoI: median δ/(ρν) per level under F1; uq-budget skill)

| Source | Type | How estimated | Size | In the reported interval? |
|---|---|---|---|---|
| Sampling of test states (40–200 of 1000) | aleatory | moving-block bootstrap, block 5, 2000 resamples | half-widths 0.01–0.04 (F1) | yes |
| Oracle Monte Carlo (M = 200 per state) | aleatory | M is fixed by design; the sensitivity of δ to one far draw is derived in §2 | enters through the far share; the same draws in every variant | no (state level) |
| CPU realization against the GPU run (orbit, network weights) | numerical / epistemic | §4.2: every stored median inside the reproduction interval; val losses within about 10% | S5 at 5%: 1.53 against 3.38 (60 states), the largest gap; inside the interval | no; resolved by WU-0040 on the GPU |
| LM iterations | numerical | 15 / 30 / 60 study (§4.4) | ≤ 12% on the failing medians; it does not change a verdict | no |
| My LM against the package | numerical | equivalence check | ≤ 2.5·10⁻⁸ whitened, below 10⁻⁵ relative | no |
| Seed | epistemic | DEV-3 only | not estimated | no; WU-0040 runs DEV-1, DEV-3, DEV-4 |
| Round-off | numerical | float64 | negligible | no |

The intervals are 95% intervals, with dependence handled by the moving block of 5 consecutive test states, as in V7. Every numerical row with evidence is at least 10 times smaller than the sampling half-width, with one exception, the CPU/GPU realization row. That row is why every number here is a prediction for WU-0040, not a verdict.

## 8. What I did not test or could not verify

- **States and seeds.** I used fewer than 1000 states per system and one seed (DEV-3). The S4 and S5 fixes rest on 60 states.
- **Selection rule.** I did not test whether F1 still picks the right basin when the pair start lands in a wrong minimum of lower cost than the network's. The `ms_pp` rows include that case as it occurred: the cost selection is the MLE rule.
- **GPU check.** I made no GPU run, so I did not check that the network-pair kd-tree path reproduces on the GPU. It is host-side and should be device-independent.
- **Effect on other hypotheses.** F1 improves PLP on four systems and so changes their H-results. That is intended for systems not yet admitted, but it is a change WU-0041 must state.
- **Literature.** The window-continuation idea resembles quasi-static variational assimilation (Pires, Vautard and Talagrand, Tellus A, 1996). I quote this from memory, unverified; ask the researcher before citing it. F1 does not depend on it.

## 9. Reproduction

Everything is in `docs/agent/notes/2026-10-25-v7-diagnosis/`. The CPU runs used the project venv, `JAX_PLATFORMS=cpu`, `nice -n 19`, and `taskset` on cores 2–3.

- **`stored_lm.py`** → `stored_lm.out.md`: stored leaves; standard library only (`python3 -I`).
- **`diag.py`**: per-draw reproduction and variants. It writes `<out>/<system>.npz` (not committed: 5–24 MB each, kept in the session scratch) plus the logs and summaries in `out/`.
  - **S6** ran first, on two threads, with an earlier version of `diag.py`: `it60` was 60 iterations straight from the network start, there was no `it30`, the `analog` start was on, and the equivalence check covered all draws. The docstring records this.
  - **Other systems** ran with `run_chain.sh`, one core and one thread each: core 2 ran S4 (60 states) then S5 (60); core 3 ran S2 (100), S3 (150), lorenz63 (100) and S1 (40). The chains were started by `out/launch.sh`.
- **`diag_converged.py`** → `out/rossler_z.converged.json`: the S3 iteration study.
- **`analyze.py`** → `analyze.out.md`: all V7, far-draw, basin and ρν tables, including F1 (`ms_pp`).
- **`far_size.py`** → `out/far_size.out.txt`: wrong-minimum error sizes.
- **Wall clock** (sum of the per-level times in the logs): S2 14 min, S3 7 min, S4 18 min, S5 18 min, S1 14 min and lorenz63 4 min, each on one core; S6 54 min on two cores, with the heavier first version.
