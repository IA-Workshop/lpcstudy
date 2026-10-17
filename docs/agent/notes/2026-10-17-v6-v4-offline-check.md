# Offline V6/V4 check on DEV-1 to DEV-4: a test of the 2026-10-13 gate-failure estimates (DEF-0026)

DEVELOPMENT (DEV-0 for the bitwise check; DEV-1, DEV-2, DEV-3, DEV-4 for the new V6 draws; R1 = DEV-1 for V4): not a hypothesis test.

Date: 2026-10-17. Agent: applied-mathematician (claude-opus-5-5). Code: develop at b58d38f, used read-only (`lpcstudy/` is identical to c9bb981 and to the R1 provenance commit 01d9fc7; the V6 path is unchanged since 4fd0ef7 apart from the context digests).

**Scope.** The owner chose the "offline V6/V4 check" for DEF-0026 (amendments note §26). This note tests the estimates of `2026-10-13-v6-margin-mathematics.md` (below: "the 10-13 note"). It changes no bar, criterion or code.

**What was run.**
- **V6 on DEV-1 to DEV-4** with the production code: `build_context` then `validation.check_integrator(ctx)`, at the pilot and full presets, on CPU, with the CPU Lyapunov cache (the one every CPU run has used). The seeds come from `seeds/development_seeds.json` via `load_registry` and `resolve_dev_seed`. All randomness inside is `make_rng(seed, ...)`. My scripts draw no random number.
- **The 10-13 law** is reused read-only from its `D_*.npz` arrays, and a second law is computed on a deterministic orbit (no seed of any kind) at the CPU λ and at the GPU λ of R1.
- **V4 and the gate flags** were read from the R1 run (read-only), and from its states dump.
- **Not run:** no preset, no test and no GPU. Nothing was written to any run directory. The confirmatory seed was not read, drawn or run.
- **Scripts and logs:** `2026-10-17-v6-v4-offline-scripts/`. The commands are in §6.

---

## 0. Determinations

| Item | Determination |
| --- | --- |
| Reproduction | The script reproduces the P1 V6 values (DEV-0) **bitwise** on all three systems (`dev0_check.log`). An independent NumPy RK4 reproduces the library's D to 1e-11 relative at the three states checked (`verify_state.log`). |
| **V6, pilot preset, DEV-1 to DEV-4** | **All pass.** Lorenz-63 2.6e-5 to 4.6e-5, Rössler 3.1e-5 to 3.9e-5, Chua 7.9e-5 to 1.35e-4. Ranks in the 10-13 law: 0.09 to 0.64. |
| **V6, full preset, DEV-1 to DEV-4** | **One failure: Chua on DEV-1, V6 = 1.53e-3** (rank 0.979). It is a real deviation of the map from the flow (e_h = 1.32e-3 against DOP853), at a window with 3 diode-breakpoint crossings. All other values pass. **No run is planned at full size on DEV-1.** The full DEV-2 values (R5/R6's seed) pass: 2.2e-5, 3.1e-5 and 3.3e-4. |
| Law against the draws | Consistent. KS test of rank uniformity on the 30 CPU draws: p = 0.14 (per system 0.45, 0.066 and 0.73). Upper-tail Fisher test: p = 0.80, so no sign of a heavier tail than predicted. Chua: 1 failure in 10 draws, against P(K ≥ 1) = 0.37 under the law. |
| **P(V6 fails) per seed, updated** | Chua **4.6%** at the CPU λ (95% CI 4.3 to 5.0%, 2·10⁶ states) and **4.3%** at the GPU λ (3.7 to 4.9%). Lorenz-63 0.13% (0.09 to 0.17%) on CPU and 0.15% on GPU. Rössler 0. **Any system: 4.8% (CPU), 4.4% (GPU).** The development draws test the law but barely move it. Their direct estimate for Chua is 1/10 (Clopper–Pearson 0.25 to 44.5%). |
| R1 (DEV-1 pilot, GPU) | All gate flags pass: V1, V2, V4, V5, V6, V7. V6: 3.8e-5, 4.3e-5 and 3.4e-5. Ranked in the GPU-λ law they sit at 0.50, 0.79 and **0.0025** (Chua is a 1-in-400 low draw). |
| **V4, R1** | Pass on all systems. used_M = 200. Median half-width 0.0349 / **0.0439** / 0.0272 (margins ×1.43 / **×1.14** / ×1.83). Mean \|w₂₀₀ − w₈₀₀\| 0.013 / 0.018 / 0.021. |
| **P(V4 fails) per seed, updated** | Now 3 realizations per system (P0, P1, R1). Pooled between-seed log-SD 0.27 on 6 df, CI [0.17, 0.59] (was 0.31 on 3 df, CI [0.18, 1.17]). Plug-in / predictive: **Lorenz 2% / 6%, Rössler 16% / 21%, Chua 6% / 11%; any system 23% / 34%** (range 7 to 58% over the CI). Rössler is now the main V4 risk. Still not well determined. **At the full size** (V4 is a median of 100 states, not 40), any system: 6.7% plug-in, 22% predictive. That rests on the state-sampling scaling of §2.3 and is untested until R5. |
| New V4 evidence | R1's states dump gives per-state half-widths. The **state-sampling log-SE of the median of 40 is 0.21 to 0.40**, which matches the between-seed SD (ratio 0.89, p = 0.58). So there is no detectable seed-level component: the V4 spread is explained by which 40 states are drawn. Most of that comes from the share of states whose weight sits at the clip (half-width 0: 8, 6 and 11 of 40). |
| V2, V5, V7 | R1: V2 medians 1.039 / 0.964 / 0.979 (per-state min 0.861); V5 0.0058; V7 slopes 1.0016 / 1.0000 / 1.0006. The distribution-free V2 bound tightens to ≤ 0.27% per system (45 per-state values, all in the band). |
| R2 and R3–R6 | R2 (DEV-1 GPU repeat) was still running. Its interim `results.json` (08:37) equals R1 on every V4, V6 and gate value, as a repeat should. It is not a new draw. R3 to R6 had no outputs yet. The CPU values here **predict R3 and R6** (§4). |

---

## 1. V6 on the development seeds

### 1.1 Method and reproduction

The quantity is `check_integrator(ctx)["integrator_max_dev_sigma"]`: the largest of 20 per-state step-halving deviations D(s_i) at the first 20 test states. It is evaluated on the context that `build_context` produces for (preset, DEV id, system), so it is the production gate value for a CPU run with that seed.

- **Bitwise check.** DEV-0 at the pilot preset gives 0.0004832547134836568, 4.253412949499829e-05 and 0.00029249004360848153. These are P1's values, bitwise.
- **Code identity.** The R1 provenance commit 01d9fc7 and develop have identical `lpcstudy/` and `seeds/`.
- **Device.** The GPU and CPU contexts differ (tier TD, amendments note §25). λ differs by 2e-4, 3e-3 and 2.2e-2 relative, so the GPU trajectory differs from the CPU one. **These CPU values are not R1's values. They are what a CPU run (R3, R6) computes.** R1's GPU values are separate draws from the GPU-λ law (§1.4).
- **Independence of the draws.**
  - Pilot and full test blocks of one seed lie on the same main orbit but are 93 645 steps apart (Lorenz-63, 3100 LT) and 312 150 steps apart (Rössler, Chua). They are independent for practical purposes.
  - Different seeds have different post-burn-in starts (M1).

### 1.2 Values

Rank F is the fraction of the 10-13 law below the value. The ± is the SD over its 5 orbits / √5.

| Draw | Lorenz-63 V6 (rank) | Rössler V6 (rank) | Chua V6 (rank) |
| --- | --- | --- | --- |
| P0 (DEV-0) | 3.93e-5 (0.531) | 3.31e-5 (0.149) | 7.54e-5 (0.075) |
| P1 (DEV-0) | 4.83e-4 (0.994) | 4.25e-5 (0.787) | 2.92e-4 (0.699) |
| DEV-1 pilot | 2.60e-5 (0.197) | 3.07e-5 (0.085) | 1.09e-4 (0.196) |
| DEV-2 pilot | 4.64e-5 (0.643) | 3.38e-5 (0.182) | 7.91e-5 (0.087) |
| DEV-3 pilot | 2.96e-5 (0.296) | 3.85e-5 (0.549) | 1.35e-4 (0.296) |
| DEV-4 pilot | 2.83e-5 (0.260) | 3.43e-5 (0.207) | 1.18e-4 (0.231) |
| DEV-1 full | 4.45e-5 (0.618) | 3.70e-5 (0.488) | **1.53e-3 (0.979), FAIL** |
| DEV-2 full | 2.18e-5 (0.063) | 3.06e-5 (0.081) | 3.34e-4 (0.755) |
| DEV-3 full | 3.09e-5 (0.333) | 2.76e-5 (0.022) | 2.95e-4 (0.703) |
| DEV-4 full | 3.29e-5 (0.386) | 4.37e-5 (0.920) | 1.69e-4 (0.422) |
| R1, DEV-1 pilot, GPU (ranked in the GPU-λ law) | 3.77e-5 (0.496) | 4.31e-5 (0.789) | 3.36e-5 (0.0025) |

- **Rank precision.** Rank errors are ≤ 0.007.
- **Agreement with the independent law.** The deterministic CPU law (§1.4) gives the same ranks within 0.01.
- **The predicted distribution, for reference (10-13 note).** Median, 95th percentile:
  - Lorenz-63: 3.8e-5 and 1.6e-4;
  - Rössler: 3.7e-5 and 4.4e-5;
  - Chua: 2.0e-4 and 9.5e-4.

### 1.3 The failing draw (full, DEV-1, Chua), verified independently

From `verify_state.log`:

- **Location.** The largest D is at test state k = 7 (index 552491). The second largest is 1.0e-4.
- **Independent reproduction.** A NumPy RK4 with the field written out independently gives 1.529522e-3, against the library's 1.529522e-3 (relative difference 1.7e-11).
- **Against a DOP853 reference** (rtol 1e-13, restarted at the breakpoints |x| = 1):
  - the true 1-LT error of the production map is **e_h = 1.32e-3 σ_x**, so D/e_h = 1.16;
  - the window crosses a breakpoint 3 times;
  - the 1-LT stretching is ln σ₁ = 4.99;
  - the observed orders at n_c, 2n_c, 4n_c, 8n_c are 8.7, −4.3 and 5.9 (erratic, not in the order-4 regime).
- **Reading.** This is exactly the mechanism of the 10-13 note §1.2(b): crossings times stretching. **V6 here measures a real deviation of the map from the flow of 1.3e-3 σ_x, not an artefact of the halving.**
- **Reference accuracy.** At these states it is ≤ 5e-6 σ_x (10-13 note, `refcheck.log`), which is 260 times smaller than e_h.
- **The other two top states checked:**
  - full DEV-2 Chua (3.3e-4): 2 crossings, D/e_h 1.11;
  - pilot DEV-3 Chua (1.35e-4): 3 crossings, D/e_h 0.80.

### 1.4 The law at the CPU and GPU λ, recomputed without any seed

`law_lambda.py` runs on a deterministic orbit: the continuation of the production statistics orbit, 10⁶ states. It recomputes the V6 law at each λ. `law_pool.py` pools it with the 10-13 law.

The SE uses segments of 10⁴ window starts, SD/√n with a normal approximation, in place of the 10-13 block bootstrap, so that no random number is drawn.

| System | P(V6 ≥ 1e-3), 10-13 law (CPU λ) | Deterministic orbit, CPU λ | **Pooled, CPU λ (2·10⁶ states)** | **Deterministic orbit, GPU λ** |
| --- | --- | --- | --- | --- |
| Lorenz-63 | 1.09e-3 ± 0.25e-3 | 1.52e-3 ± 0.30e-3 | **1.30e-3 [0.92, 1.69]e-3** | **1.49e-3 [0.89, 2.10]e-3** |
| Rössler | 0 (max D 4.45e-5) | 0 (max D 4.45e-5) | **0** | **0** (max D 4.51e-5) |
| Chua | 4.43e-2 ± 0.26e-2 | 4.84e-2 ± 0.26e-2 | **4.64e-2 [4.27, 5.00]e-2** | **4.29e-2 [3.68, 4.90]e-2** |

- **The two CPU laws agree** within their errors. Chua differs by 0.41 points against an SE of the difference of 0.37; Lorenz by 0.44e-3 against 0.39e-3. This is an independent replication of the 10-13 law, on a different orbit and with no random perturbation.
- **The GPU λ** (smaller Δ by 2.2% for Chua, with the same n_c = 16) lowers Chua's median V6 from 1.91e-4 to 1.76e-4 and P(fail) by about 0.4 points. That is within the CIs.

### 1.5 Tests of the law (`v6_ranks.log`)

| Test | Result |
| --- | --- |
| KS test of rank uniformity, 30 CPU draws | D = 0.204, p = 0.14 |
| KS per system: Lorenz-63 / Rössler / Chua | p = 0.45 / 0.066 / 0.73 |
| Upper-tail Fisher test (tail heavier than the law?) | p = 0.80 |
| Lower-tail Fisher test (draws lower than the law?) | p = 0.094 |
| Chua failures: 0/6 pilot-type draws; 1/10 with full; 1/11 with R1 | P(K=0) = 0.76; P(K ≥ 1) = 0.37; P(K ≥ 1) = 0.40 |
| Lorenz-63 failures 0/10, Rössler 0/10 | P(K=0) = 0.99 and 1 |

- **No evidence against the law.** The draws lean slightly low: the mean rank is 0.41 against 0.50 ± 0.05, and R1 Chua sits at 0.0025. This is not significant. If it were real it would make the law's failure probability conservative, not optimistic.
- **The check has little power.** With 10 draws per system, a true Chua rate of 20% would still give K ≤ 1 with probability 0.38, and a rate of 1% would give K ≥ 1 with probability 0.10. The draws rule out only gross errors in the law, for example "Chua P(fail) ≈ 0" in the sense of M5(d): one failure has now been observed.

### 1.6 Updated per-seed V6 failure probability, with its uncertainty budget (skill `uq-budget`)

**Estimate.** P(V6 fails on some system, per fresh seed) = **4.8% at the CPU λ** and **4.4% at the GPU λ**. Chua carries 97% of it.

**How the draws enter.** The law has an effective sample size of about p(1 − p)/SE² ≈ 1.4·10⁴ draws. Adding 11 direct draws with 1 failure moves it by < 1e-4. So the development draws are used as a test of the law, not pooled into it.

| Source | Type | How estimated | Size (points of P(fail), Chua) | In the reported interval? |
| --- | --- | --- | --- | --- |
| Finite attractor sample (2·10⁶ states on CPU; 10⁶ on GPU) | aleatory (MC) | segment SE (10⁴-start blocks) | ±0.37 (CPU), ±0.61 (GPU) half-width | yes |
| Device (λ of GPU vs CPU) | epistemic, identified | both laws computed | 0.35 between the point estimates | reported as two numbers |
| Block start ~ μ (A1 of the 10-13 note) | epistemic | M1(a) KS; 30 development ranks KS p = 0.14 | not detectable at this resolution | no |
| Code identity with the sealed run | epistemic | bitwise P1 reproduction; `lpcstudy/` diff empty | 0 while `systems.py`, `data.py` and `validation.py` are unchanged | no |
| Round-off | numerical | float64; NumPy against library 1e-11 relative at D ≈ 1e-3 | < 1e-8 relative | no |
| Reference accuracy (mechanism only) | numerical | DOP853, 10-13 `refcheck` | ≤ 5e-6 σ_x | not used in P(fail) |

The intervals are 95%, under dependence handled by blocks of 10⁴ consecutive window starts. Seeds: no seed for the deterministic laws; the 10-13 laws used that note's literal scratch seeds (read-only reuse of its arrays, no new draw).

---

## 2. V4 and the other gate flags

### 2.1 Values (read-only, `v4_update.log`)

| Run (seed, commit, device) | System | V4 at M = 50 / 200 / 800 | Mean \|w_M − w₈₀₀\| at M = 50 / 200 | used_M | V4 flag | Margin (0.05 / V4₂₀₀) |
| --- | --- | --- | --- | --- | --- | --- |
| P0 (DEV-0, 1b20db9, CPU) | L / R / C | 0.0726 / 0.0370 / 0.0206; 0.0731 / 0.0390 / 0.0214; 0.0549 / 0.0308 / 0.0145 | 0.051 / 0.030; 0.037 / 0.017; 0.048 / 0.016 | 200 | pass | ×1.35 / ×1.28 / ×1.62 |
| P1 (DEV-0, 5b3fd8f, CPU) | L / R / C | 0.0308 / 0.0187 / 0.0114; 0.0546 / 0.0334 / 0.0211; 0.0632 / 0.0420 / 0.0196 | 0.038 / 0.020; 0.029 / 0.018; 0.033 / 0.027 | 200 | pass | ×2.68 / ×1.50 / ×1.19 |
| **R1 (DEV-1, 01d9fc7, GPU)** | L / R / C | 0.0659 / **0.0349** / 0.0157; 0.0616 / **0.0439** / 0.0228; 0.0516 / **0.0272** / 0.0136 | 0.028 / 0.013; 0.032 / 0.018; 0.036 / 0.021 | 200 | pass | ×1.43 / **×1.14** / ×1.83 |

**R1 gate flags.** V1, V2, V4, V5, V6 and V7 are all true on all three systems, so `gate_pass` is true.

| R1 check | Lorenz-63 | Rössler | Chua |
| --- | --- | --- | --- |
| V2 median (per-state min, max) | 1.039 (0.861, 1.066) | 0.964 (0.923, 0.985) | 0.979 (0.939, 1.035) |
| V5 | 0.0058 | 0.0058 | 0.0058 |
| V6 | 3.77e-5 | 4.31e-5 | 3.36e-5 |
| V7 slope | 1.0016 | 1.0000 | 1.0006 |

V1: ≤ 3.8e-9.

**What is pending.**
- **R2** (DEV-1, GPU, repeat) was still running. Its interim `results.json` (08:37) equals R1 on every V4, V6 and gate value, as a repeat on one device should. It adds no draw.
- **R3 to R6** had no output under `run/r3r6-c9bb981/` (no `runs/` directory yet).

### 2.2 What the R1 states dump adds

The dump holds the 40 per-state half-widths at M = 200. Their median equals the gated V4 bitwise on all three systems.

| | Lorenz-63 | Rössler | Chua |
| --- | --- | --- | --- |
| Quartiles of the per-state half-width | 0.005 / 0.047 | 0.018 / 0.064 | 0.000 / 0.056 |
| States with half-width 0 (w at the clip) | 8 | 6 | 11 |
| States above 0.05 | 7 | 17 | 13 |
| Distribution-free 96.2% CI of the population median [x₍₁₄₎, x₍₂₇₎] | [0.0144, 0.0433] | [0.0230, 0.0546] | [0.0089, 0.0458] |
| State-sampling log-SE of the median (order statistics; Maritz–Jarrett) | 0.27; 0.21 | 0.21; 0.19 | 0.40; 0.32 |
| P(median of 40 resampled states > 0.05), exact binomial bounds | ≈ 0 | 0.13 to 0.21 | 0.007 to 0.016 |

**Reading.** V4 is a median of 40 draws from a mixture with an atom at 0, the states whose weight sits at the clip. It moves when that share moves.

The state-sampling SE (RMS 0.30) is the size the between-seed log-SD would have if only the states changed, with ψ, the library and the code held fixed. **The observed between-seed SD (0.27, 6 df) is fully consistent with it**: ratio 0.89, F-type p = 0.58. So there is no evidence of an extra seed-level or code-version component.

This also bears on the 10-13 note's open question about the Lorenz pair (factor 2): it is within state sampling.

### 2.3 Updated per-seed V4 failure probabilities

The model is the 10-13 note's: log V4 ~ N(μ_s, σ²) with a common σ. Bartlett's test of a common σ gives p = 0.45, but with 2 df per system it has low power.

| System | Values P0, P1, R1 | Geometric mean (margin) | Plug-in | Predictive (t₆) | Over the σ CI [0.17, 0.59] | State-sampling σ only (0.30) | 10-13 note (plug-in / predictive) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Lorenz-63 | 0.0370, 0.0187, 0.0349 | 0.0289 (×1.73) | 0.020 | 0.062 | 0.001 to 0.175 | 0.034 | 0.020 / 0.096 |
| Rössler | 0.0390, 0.0334, 0.0439 | 0.0385 (×1.30) | **0.164** | **0.214** | 0.064 to 0.328 | 0.193 | 0.149 / 0.229 |
| Chua | 0.0308, 0.0420, 0.0272 | 0.0328 (×1.53) | 0.056 | 0.109 | 0.007 to 0.236 | 0.080 | 0.146 / 0.227 |
| Any system | | | **0.23** | **0.34** | 0.07 to 0.58 | 0.28 | 0.29 / 0.46 |

**What can be concluded.**
- σ is now known within a factor of 3.4 (it was 6.6). An independent within-seed estimate agrees with it.
- Rössler is the V4 risk: about 16 to 21% per seed. R1's ×1.14 is the smallest V4 margin seen so far.
- Chua's V4 risk is lower than the 10-13 central estimate, about 6 to 11%, because R1's Chua value was low.
- Lorenz-63 is about 2 to 6%.

**What cannot be concluded.**
- Log-normality is untested, and with an atom at 0 in the per-state law it is only an approximation for the median.
- The R1 values come from a different code version (01d9fc7 against 5b3fd8f) and device (GPU). The agreement of the within-seed and between-seed spreads is the only check that this did not shift μ_s.
- Each further seed adds 1 df per system. R3 (CPU, DEV-1) would add a CPU realization on another trajectory.

**The full preset (the confirmatory size) differs.** `convergence_states` is 100 at full and 40 at the pilot (`config.py`), so the gated V4 is a median of 100 states.

If the between-seed spread is state sampling, as §2.2 indicates, σ scales by √(40/100) = 0.63, to 0.17. With the pilot locations carried over, the per-seed P(V4 fails) at full is (`v4_update.log`, last block):

| System | Plug-in | Predictive | Over the CI |
| --- | --- | --- | --- |
| Lorenz-63 | 0.1% | 2.7% | 0 to 7% |
| Rössler | 6.1% | 14.8% | 0.8 to 24% |
| Chua | 0.6% | 5.7% | 0 to 13% |
| **Any system** | **6.7%** | **22%** | **0.8 to 38%** |

- **The location may move at full.** The estimator is trained on 100 000 pairs at full (40 000 at the pilot), so the PLP errors, and with them the per-state law of the half-width, can change.
- **R5 (DEV-2, full) gives the first full-size V4 value.** It tests both the location and the √(40/100) scaling.

### 2.4 V2

R1 adds 15 per-state ratios, all inside [0.8, 1.2]. That makes 45 of 45 inside, so q ≤ 1 − 0.05^{1/45} = 0.064 (95%), and P(median of 5 out of band) ≤ C(5,3)·q³ = **0.27% per system**, distribution-free. It was 0.9%. The gated medians are 0.95 to 1.04.

---

## 3. Gate risk per fresh seed, updated (development evidence only)

| Check | Per-seed P(fail), any system | Determination |
| --- | --- | --- |
| V6 | 4.8% (CPU λ) / 4.4% (GPU λ); CI about ±0.5 points | well determined; the law is consistent with the 30 new draws and replicated on an independent orbit |
| V4, pilot size (40 states) | 23% plug-in, 34% predictive (range 7 to 58%) | better than on 10-13 but still not determined; Rössler dominates |
| V4, full size (100 states) | 6.7% plug-in, 22% predictive (range 0.8 to 38%) | assumes the state-sampling scaling and an unchanged location (§2.3); untested until R5 |
| V1, V2, V5, V7 | ≈ 0 (V2 ≤ 0.27% per system) | unchanged |
| **V4 or V6 (N4), pilot size** | **about 26% plug-in, 38% predictive** | assumes V4 and V6 are independent; they share the first 20 test states but measure unrelated things (RK4 truncation against the bootstrap spread of w*). Untested |
| **V4 or V6 (N4), full size** | **about 11% plug-in, 25% predictive** | same assumptions, plus those of the full-size V4 row |

**Neutral consequence for the owner.** The 10-13 note's conclusion stands. A gate failure at a fresh seed, including the confirmatory one, is a plausible outcome of correct code, mostly from V4 (Rössler) and V6 (Chua):
- about 1 in 4 to 1 in 3 at the pilot size;
- about 1 in 10 to 1 in 4 at the full size, where the sealed run is made. This note concretely exhibits one such failure: full preset, DEV-1, Chua V6 = 1.53e-3. I make no recommendation on bars or options; the 10-13 note §5 lists them. This note does not change any bar or criterion.

---

## 4. Predictions for the pending runs (falsifiable checks)

- **R3** (pilot, DEV-1, CPU, `LPC_THREADS=8`). Predicted V6, bitwise: 2.603053882868152e-05, 3.073216545287898e-05 and 0.00010887766530342213, so pass on all systems. Predicted `main_digest`: 7d05d85f…7580, d5af1019…7c43 and 9d8eba8e…c98e (full strings in `v6_dev14_cpu.log` via the npz; listed in §6). Conditions:
  - R3's CPU λ equals the CPU cache used here. Every CPU run so far has the same λ.
  - The orbit does not depend on the thread count. This is expected for a serial `lax.scan` of a 3-vector, but not verified here.
- **R6** (full, DEV-2, CPU). Predicted V6, bitwise: 2.1802591911046492e-05, 3.0603832151101185e-05 and 0.00033398382382766916, so pass (Chua margin ×2.99). The conditions are the same.
- **R5** (full, DEV-2, GPU). No value can be predicted, because GPU contexts differ (TD). Under the GPU-λ law: P(V6 fail) is 4.3% for Chua and 0.15% for Lorenz-63.
- **A CPU full run on DEV-1** would fail V6 on Chua (1.53e-3). None is planned. This is recorded so that it is not a surprise if one is made.

A mismatch in R3 or R6 under the stated conditions would mean that the offline path and the production path differ. It would be a defect candidate, not a statistical event.

**Seed use, for the registry keeper.**
- **DEV-3 and DEV-4** were used here, for the first time, for this V6 check (contexts only).
- **DEV-2** was also evaluated at the pilot preset. The WU-0003 plan reserves DEV-2 for full-size runs, while the owner's DEF-0026 answer names DEV-1 to DEV-4.
- Only V6, an outcome-free integrator check, was computed. No forecast, oracle or hypothesis statistic was computed on any seed.

---

## 5. Hypotheses (NVVUQ.14) and where they are checked

| Hypothesis | Check |
| --- | --- |
| The production V6 equals the offline evaluation | bitwise on DEV-0 (P1); `lpcstudy/` diff empty between the R1 commit and develop |
| The test-block start is μ-distributed, and pilot, full and the seeds are independent draws | M1(a); KS of the 30 ranks p = 0.14; blocks ≥ 3100 LT apart |
| The law is not an artefact of one orbit set | replicated on a deterministic continuation orbit with no random perturbation (§1.4) |
| V4 is log-normal with a common σ | Bartlett p = 0.45 (low power); not otherwise tested; the per-state law has an atom at 0 |
| V4's between-seed spread is state sampling | R1 dump: within-seed log-SE 0.30 against between-seed 0.27 (p = 0.58) |

---

## 6. Reproduction (REPRO.10)

Set `PY=.venv/bin/python -I` (the develop venv) and `W=` the develop worktree.
- `C_CPU=` a copy of `run/r0-e3b2645/runs/r0-cpu-dev1/smoke/cache/` (CPU λ, bitwise equal to P1's).
- `C_GPU=` a copy of R1's `cache/`.
- `D10=` the directory holding the 10-13 `D_*.npz` (regenerated by that note's `perstate.py`).

All commands run on CPU with `LPC_THREADS=4`.

```
$PY v6_dev.py $W $C_CPU dev0_pilot.npz pilot DEV-0                       # bitwise P1 check -> dev0_check.log
$PY v6_dev.py $W $C_CPU dev14_cpu.npz pilot,full DEV-1,DEV-2,DEV-3,DEV-4  # -> v6_dev14_cpu.log (about 2 min)
$PY verify_state.py $W $C_CPU full DEV-1 chua                            # also full DEV-2 chua, pilot DEV-3 chua -> verify_state.log
$PY law_lambda.py $W $C_CPU <system> <spacing> L_<system>_cpu.npz        # and $C_GPU -> law_lambda_*.log
$PY v6_ranks.py $D10 dev14_cpu.npz <R1 pilot dir>/results.json           # -> v6_ranks.log
$PY law_pool.py $D10 dev14_cpu.npz <R1 pilot dir>/results.json           # -> law_pool.log (run where L_*.npz are)
$PY v4_update.py <R1 pilot dir> [<R2 pilot dir>]                         # -> v4_update.log
```

Spacing: Lorenz-63 45, Rössler 150, Chua 150. The npz outputs are not committed; they regenerate in minutes.

Full predicted digests (§4):

| Run | System | Digest |
| --- | --- | --- |
| R3 (pilot, DEV-1, CPU) | Lorenz-63 | 7d05d85f25b9b96d0dcabea44d6fe26f23a869858bf36140243aed379ab47580 |
| R3 | Rössler | d5af1019e4d9c4a44ca594b3620cc4fbaf08c35fd9c2ad2fddeb098d7fb27c43 |
| R3 | Chua | 9d8eba8e4f35a7c2348fdc7d167949bcff3c7ece6b8ef6bd3a899510bc70c98e |
| R6 (full, DEV-2, CPU) | Lorenz-63 | 46c29722e2cc410e992e6462231b988f0ea9c4612bb42971e6e0c1686cbcb9ed |
| R6 | Rössler | c44156c19da6c432d1170725698b2783e3519e30c61ef87827b03f02365a2c35 |
| R6 | Chua | bd50bc75d8ceb169d7b430f9211226a00ddf1f6fd4ca10878683c4a97d08c8f0 |
