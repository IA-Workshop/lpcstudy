---
title: "Pilot Results (v1.1, corrected)"
subtitle: "Pilot of 6 October 2026 (code v1, preset `pilot`), with corrections from the audit of 10 October and a recheck of the library sweep"
date: "10 October 2026"
---

# Read this first

**What this is.** This is the exploratory pilot.

- **Systems.** Lorenz-63, Rössler and Chua, plus transfer and robustness runs.
- **Sample sizes.** 600/300/500 construction/calibration/test states, M = 200 oracle draws and E = 2 evaluation draws.
- **Validation.** Every validation check (V1–V6) passed on every system.

**What changed from v1 of this report.**

- **Interpretation.** It is corrected where it overstated or misattributed a result (§Corrections).
- **Verdicts.** These are restated under the decision rules of Methods v2: pass / fail / inconclusive per system, and "supported" only if all three pass.
- **New pilot evidence.** A recheck of the library sweep (same seeds) adds bootstrap intervals for the median weights and finds the noise-matching effect that motivates H2f.

**Scope.** Lorenz-96 and the transfer test T1 are no longer part of the study (decision D3). Their numbers stay in the appended table for the record only.

The appended auto-generated tables use the v1 criteria and labels. Where they disagree with this header, this header governs.

# Findings, restated

1. **The estimator is efficient: δ/(ρν) = 1.00–1.01 at every noise level.**
   - Under this design (common random numbers and a maximum-likelihood refinement), this is close to guaranteed.
   - It is now validation check V7, not a finding.
2. **The analog seed is predicted by R·ν̂ with a constant of 0.26 on all three systems.**
   - With the fitted constants, ν̂ cancels in the deployable closed form A4. A4 ≈ 1/(1 + 0.26(R/ρ)²) on Lorenz-63 and Rössler; on Chua a fitted floor keeps a small ν̂ dependence.
   - The deployable closed form is therefore, in effect, a recurrence-in-noise-units rule.
3. **The fourth LPC (noise sensitivity N) is a distinct quantity.**
   - A flexible regressor cannot predict N from the other three coordinates: out-of-sample R² is −0.18 to 0.10 with oracle values. A negative R² signals an overfit regressor, not proof of distinctness.
   - Under the Methods v2 Q-N reading (95% intervals), the oracle ΔR² for logit w* gives:

     | System | ΔR² [95% CI] | Reading |
     |---|---|---|
     | Rössler | 0.089 [0.042, 0.150] | carries substantial additional information |
     | Chua | 0.072 [0.017, 0.126] | carries substantial additional information |
     | Lorenz-63 | 0.023 [−0.014, 0.061] | undetermined |

   - Deployable ΔR²: undetermined on Lorenz-63 and Rössler; on Chua −0.014 [−0.071, 0.046] reads "reduces to the other three". The deployable profile barely predicts w* (three-coordinate R² −0.02 to 0.05).
4. **With an exact model, PLP dominates by 1 LT.**
   - Median w*(1 LT) is 0.05–0.09.
   - 22–36% of test states sit exactly at w* = 0, at every library size. "Most states", as v1 said, overstated this.
5. **Separation is not supported (H2a).**
   - In the small-error regime, w*(H) moves by a median of 0.12 / 0.28 / 0.17 (Lorenz-63 / Rössler / Chua). The interval lies entirely above 0.1 on Rössler and Chua: fail.
   - The partial correlation with instability is 0.06–0.13.
6. **The knobs move the weight, but not monotonically in library size (H2b, recheck of 10 October).**
   - **Noise.** w* rises with ρ: per-state rank correlation 0.16–0.25, with intervals above 0.
   - **Library size.** The mean w* rises from N_lib = 10³ to 10⁴ at ρ = 1%: +0.054, +0.079 and +0.055, with all 98.3% intervals above 0. It then falls.
   - **The falling branch.** The mean drops between the two largest libraries by 0.01–0.03, with intervals excluding 0 in 3 of 6 cells. The median dip that v1 flagged lies within noise in all six cells.
   - **The peak moves with noise.** It sits at about 10⁴–10^4.5 at ρ = 1% and about 10^3.5 at ρ = 2%.
   - **Why per-state rank correlations failed.** They were diluted by ties at w* = 0, not by an absent trend.
7. **Noise matching (new; this motivates H2f).** On every system and at both noise levels:
   - the median correlation between CP and PLP errors at 1 LT rises steadily with library size, from 0.00–0.15 at N_lib = 10³ to 0.39–0.46 at 10⁵;
   - the paired change is 0.21–0.36, with intervals well above 0;
   - meanwhile the analog seed keeps shrinking.

   Interpretation: with more analogs, the margin between nearest neighbors shrinks, and retrieval follows the query noise (Theorem P2). CP then makes the same mistake PLP makes, and the positive cross-moment lowers w* (Theorem P1). This links the fourth LPC to the weight.
8. **The closed form with exact seeds helps; the deployable version does not (H2c).** MSE at 1 LT relative to the global weight A2:

   | Rule | Lorenz-63 | Rössler | Chua |
   |---|---|---|---|
   | A4o (closed form, oracle seeds) | −44% | −10% | −3% |
   | A4 (closed form, deployable seeds) | +19% | +7% | +1% |
   | A5 (four-coordinate regimes) | −14% | +2% | −8% |
   | A3 (empirical allocator) | −21% | +8% | −2% |
   | A* (oracle) | −54% | −25% | −29% |

   On Lorenz-63, both H2c intervals include 0 (undecided). v1 listed this as decided.
9. **Regime abstraction does not reach low excess error, and could not have under v1's 5% bar (H3).**
   - Even A4o, with exact seeds, has excess MSE equal to 19% / 9% / 45% of the mean per-state better-single-forecaster MSE (v1's denominator), so no profile-based rule could meet the bar.
   - K selection fell back to K = 5 on every system.
   - The flat excess-versus-K curve is the floor of Theorem P3(b). It is positive whenever w* is not a function of the profile, from any cause. v1 attributed it to proxy noise alone, which A4o rules out.
   - v1 computed regret with clipped w*, which understates the excess MSE, so these numbers are lower bounds.
   - The regime map's point estimates are below the closed form's: MSE_A5/MSE_A4 = 0.72 / 0.96 / 0.91 (H3d; v1 computed no interval).
10. **Instability dominates both trees on Lorenz-63 (H3c).** Weight-tree importance of Λ̃ is 0.89, against a criterion below 0.2. This is clearly opposite to separation, not partial support.
11. **Robustness.** Under ±5–10% model error, PLP's error stops following the seed law (PLP slope 0.53–0.65 on Lorenz-63, 0.21–0.27 on Rössler). The exact-model theory does not cover this case, which is why the misspecified arm is future work.

# Corrections to v1 of this report

| v1 statement | Correction |
|---|---|
| "The estimation-seed law holds exactly" | Close to guaranteed by design; now validation V7 |
| "H1e fails on N alone" | Under v1's point criterion, ε̂ on Chua (0.679) also fails |
| "R² of N from the other three is −0.18 to 0.10" | These are oracle values. The deployable values are −0.15 to −0.05. Negative values indicate overfitting. |
| "Most states keep w* at the clip floor of 0" | 22–36% of states |
| "Library-size trend absent except on Chua" | Diluted by ties. The mean rises from 10³ to 10⁴ at ρ = 1% on every system (recheck). |
| Flat regret is "the irreducible floor from proxy noise" | It is the P3(b) floor from any non-measurability; A4o, with no proxy noise, sits at 9–45% |
| Decision plan of 6 October: H1c omitted; H1d and H3c "near threshold"; H2c "decided" | H1c is decided against: CP slopes on Rössler (1.62) and Chua (1.63) have intervals above 1.2 (Lorenz-63 1.22 [1.01, 1.44] straddles it), and Rössler PLP at 0.67 has its interval below 0.8. H1d fails on Chua (interval below 0.8) and is inconclusive on Lorenz-63 [0.62, 0.85]. H3c fails clearly on Lorenz-63 (0.89) and passes on Rössler and Chua. H2c is undecided on Lorenz-63. |
| "Pilot showed M = 100 misses ±0.05" | M = 100 was not run. M = 50 gives half-width 0.055–0.073; M = 200 gives 0.031–0.039. |

# Verdicts under the Methods v2 rules

Pilot precision: 95% intervals, and 98.3% for the primaries, which are marked in bold. This table is indicative only; the confirmatory run decides.

| ID | Lorenz-63 | Rössler | Chua | Overall |
|---|---|---|---|---|
| V7 (was H1a) | pass | pass | pass | gate passes |
| H1b | inconclusive | inconclusive | inconclusive | inconclusive |
| H1c (PLP) | inconclusive | fail | pass | not supported |
| H1d | inconclusive | pass | fail | not supported |
| H1e (ε̂, δ̂, Λ̂) | pass | inconclusive (ε̂) | inconclusive (ε̂) | inconclusive |
| Q-N (oracle) | undetermined | substantial | substantial | (estimate) |
| **H2a** | inconclusive | fail | fail | not supported |
| **H2b** (i) ρ; (ii) 10³ → 10⁴ at ρ = 1% | pass | pass | pass | supported |
| H2c | inconclusive | inconclusive | inconclusive | inconclusive |
| H2d | fail | pass | inconclusive | not supported |
| H2f (new) | pass | pass | pass | supported |
| H3a (log-rank) | fail | fail | fail | not supported |
| H3c | fail | pass | pass | not supported |
| **H3d** | no interval in v1 | no interval in v1 | no interval in v1 | point estimates 0.72–0.96 |

Notes on individual rows:

- **H1b.** Judged from the mean-ε² fit (v2 uses the median). Every 1/d interval straddles an edge of the ±25% band.
- **H1e** uses the Fisher-z approximation. ε̂ is 0.74 on Rössler and 0.68 on Chua, and both intervals straddle 0.7.
- **H2c.** On every system at least one interval includes 0.
- **H2d.** Rössler [−0.09, 0.08] lies below the 0.10 bound.
- **H3a.** No system has all consecutive log-rank p < 0.01.
- **H2f.** Paired median change in error correlation, 10³ → 10⁵: 0.21–0.36, with every interval above 0 (from the recheck's saved per-state arrays).
- **H3c.** On Lorenz-63 the weight-tree importance of Λ̃ is 0.89. On Rössler and Chua it is 0.00 and 0.12, and Λ̃ leads the horizon tree.

---


*Appended below: the auto-generated tables of 6 October, unchanged. Their verdict labels use the v1 rules.*

# Results — preset `pilot`

Generated by `python -m lpcstudy`. Pass/fail criteria are the pre-registered thresholds of the Methods document (§M9). A hypothesis is *supported* if it passes on every core system, *partially supported* if on at least one.

## Hypothesis verdicts

Validation gate: lorenz63 PASS, rossler PASS, chua PASS

| ID | Hypothesis | lorenz63 | rossler | chua | Verdict |
|---|---|---|---|---|---|
| H1a | Estimation seed scales linearly with noise: median per-state slope of log delta on log rho in [0.9, 1.1] | PASS: slope 1 [1, 1] | PASS: slope 1 [1, 1] | PASS: slope 1 [1, 1] | supported |
| H1b | Analog seed follows eps^2 = c^2 N^(-2/d) + f^2: fitted 1/d within 25% of the local dimension, floor increasing with rho | PASS: rho=0.01: 1/d=0.497; rho=0.02: 1/d=0.494 (1/d_LB=0.508) | FAIL: rho=0.01: 1/d=0.366; rho=0.02: 1/d=0.273 (1/d_LB=0.549) | FAIL: rho=0.01: 1/d=0.374; rho=0.02: 1/d=0.311 (1/d_LB=0.506) | partially supported |
| H1c | Error = amplifier x seed: slope of log rms error on log(g_H seed) in [0.8, 1.2] for CP and PLP at H_ref | FAIL: CP 1.22, PLP 0.823 | FAIL: CP 1.62, PLP 0.672 | FAIL: CP 1.63, PLP 1.01 | not supported |
| H1d | Horizon law: median of Lambda_bar x dT/dln(theta) in [0.8, 1.25] (PLP) | FAIL: PLP 0.746, CP 0.519 | PASS: PLP 0.985, CP 1.02 | FAIL: PLP 0.654, CP 0.687 | partially supported |
| H1e | Deployable proxies of all four LPCs track their oracles: Spearman >= 0.7 each | FAIL: eps 0.77, delta 0.82, Lambda 0.98, N 0.68 | FAIL: eps 0.74, delta 0.96, Lambda 0.99, N 0.63 | FAIL: eps 0.68, delta 0.91, Lambda 0.97, N 0.69 | not supported |
| H1f | Fourth LPC (noise sensitivity) is reducible to the other three: Delta R^2 (4 vs 3 coordinates, out of sample) upper bound < 0.01 for logit w* and log T | FAIL: inconclusive: dR2 w 0.021 [-0.049, 0.089], T 0.0018 [-0.048, 0.051]; oracle: inconclusive | FAIL: inconclusive: dR2 w 0.031 [-0.023, 0.09], T 0.019 [-0.036, 0.08]; oracle: adds information | FAIL: inconclusive: dR2 w -0.014 [-0.071, 0.046], T -0.0071 [-0.043, 0.03]; oracle: adds information | not supported |
| H2a | [primary] Separation: for H >= 1 LT median range of w*(H) < 0.1 and |partial corr(logit w*, Lambda | seeds)| < 0.1 | FAIL: range 0.118 (CI hi 0.159); partial r 0.061 | FAIL: range 0.28 (CI hi 0.328); partial r 0.13 | FAIL: range 0.174 (CI hi 0.234); partial r 0.13 | not supported |
| H2b | [primary] Knob response: w* rises with N (per-state rank correlation > 0; median at N_max < 0.95) and with rho | FAIL: rho rank corr 0.24; N@0.01: w*(Nmax)=0.068; N@0.02: w*(Nmax)=0.081 | FAIL: rho rank corr 0.16; N@0.01: w*(Nmax)=0.07; N@0.02: w*(Nmax)=0.086 | FAIL: rho rank corr 0.25; N@0.01: w*(Nmax)=0.084; N@0.02: w*(Nmax)=0.076 | not supported |
| H2c | State dependence: A4 MSE < A2 and < best single forecaster at H_ref | FAIL: A4-A2 19.1%; A4-A1 -3.97% | FAIL: A4-A2 7.06%; A4-A1 7.83% | FAIL: A4-A2 1.13%; A4-A1 7.19% | not supported |
| H2d | Empirical comparison: A4 within 10% of A3 in-distribution; A4 degrades less than A3 in >= 4 of 5 shifted cells | FAIL: A4/A3-1 = 50.6%; shift wins 4/5 | FAIL: A4/A3-1 = -0.992%; shift wins 2/5 | FAIL: A4/A3-1 = 2.88%; shift wins 2/5 | not supported |
| H2e | Hybrid horizon gain <= ln2 / (2 Lambda_bar) for >= 90% of eligible states | PASS: within bound 0.952 (n=335, max gain 1.7 LT) | FAIL: within bound 0.889 (n=324, max gain 3.8 LT) | PASS: within bound 0.943 (n=318, max gain 3.6 LT) | partially supported |
| H3a | [primary] Some K <= 5: regret <= 5% of best-single variance, regime horizon IQR <= 0.5 LT, consecutive log-rank Holm p < 0.01 | FAIL: K=5: regret 61.6%, IQR 1.1 LT | FAIL: K=5: regret 19.7%, IQR 1.5 LT | FAIL: K=5: regret 41.3%, IQR 1.5 LT | not supported |
| H3b | Regret falls as K^(-2/p_eff) with p_eff < 1.5 | FAIL: p_eff 73.7 | FAIL: p_eff 35.8 | FAIL: p_eff inf | not supported |
| H3c | Structure: weight tree ignores instability (importance < 0.2); horizon tree uses instability more than any other coordinate | FAIL: Lambda imp: weight 0.89, horizon 0.49 | PASS: Lambda imp: weight 0, horizon 0.69 | PASS: Lambda imp: weight 0.12, horizon 0.84 | partially supported |
| H3d | Regime lookup costs <= 5% MSE relative to the closed form | PASS: A5/A4 0.7242 | PASS: A5/A4 0.9563 | PASS: A5/A4 0.915 | supported |

**T1 (transfer, secondary):** not supported — chua: gap A3 0.59, A4 0.00333, A5 0.74; lorenz96: gap A3 0.44, A4 0.475, A5 0.28

## Allocation rules at the core cell (test split)

### lorenz63

| Rule | MSE 0.25LT | MSE 0.5LT | MSE 1LT | MSE 2LT | MSE 4LT | regret H_ref | agreement | KM median (LT) | RMST (LT) |
|---|---|---|---|---|---|---|---|---|---|
| A0 CP alone | 0.0199 | 0.118 | 0.224 | 0.514 | 1.98 | 0.175 | 0.139 | 1.4 | 1.55 |
| A1 PLP alone | 0.0491 | 0.0592 | 0.1 | 0.133 | 1.01 | 0.0467 | 0.861 | 2.6 | 2.74 |
| A2 Global fixed weight | 0.0147 | 0.0479 | 0.0806 | 0.115 | 0.857 | 0.0348 | 0.861 | 2.17 | 2.14 |
| A3 Error-predictor allocator (Heuer-inspired) | 0.0291 | 0.035 | 0.0638 | 0.103 | 0.888 | 0.0185 | 0.879 | 2.47 | 2.51 |
| A4 LPC closed form (deployable) | 0.0466 | 0.0517 | 0.0961 | 0.12 | 0.896 | 0.0432 | 0.861 | 2.47 | 2.52 |
| A4f LPC full form with amplifier (deployable) | 0.0471 | 0.0558 | 0.0966 | 0.12 | 0.896 | 0.0434 | 0.861 | 2.47 | 2.52 |
| A5 LPC regimes (deployable) | 0.0135 | 0.0417 | 0.0696 | 0.11 | 0.856 | 0.0273 | 0.611 | 2.13 | 2.12 |
| A4o LPC closed form (oracle seeds) | 0.000743 | 0.00766 | 0.0455 | 0.0967 | 0.919 | 0.0084 | 0.902 | 2.47 | 2.55 |
| A* Oracle state-optimal weight | 0.000445 | 0.0057 | 0.0374 | 0.0498 | 0.581 | 0 | 1 | 2.6 | 2.61 |

Oracle recovery: A4 recovers -43.9% of the oracle-seed closed form's gain over A2; A5 recovers 25.6% of A*'s.

### rossler

| Rule | MSE 0.25LT | MSE 0.5LT | MSE 1LT | MSE 2LT | MSE 4LT | regret H_ref | agreement | KM median (LT) | RMST (LT) |
|---|---|---|---|---|---|---|---|---|---|
| A0 CP alone | 0.0013 | 0.00236 | 0.00879 | 0.0565 | 0.193 | 0.00693 | 0.131 | 2.6 | 2.81 |
| A1 PLP alone | 0.000117 | 0.000214 | 0.000619 | 0.0111 | 0.124 | 0.000159 | 0.869 | 3.67 | 3.89 |
| A2 Global fixed weight | 0.000118 | 0.000216 | 0.000624 | 0.011 | 0.105 | 0.00014 | 0.869 | 3.3 | 3.44 |
| A3 Error-predictor allocator (Heuer-inspired) | 0.000132 | 0.000234 | 0.000675 | 0.011 | 0.106 | 0.000158 | 0.869 | 3.43 | 3.54 |
| A4 LPC closed form (deployable) | 0.000126 | 0.000232 | 0.000668 | 0.0106 | 0.109 | 0.000129 | 0.869 | 3.6 | 3.75 |
| A4f LPC full form with amplifier (deployable) | 0.000123 | 0.000229 | 0.000665 | 0.0106 | 0.108 | 0.000127 | 0.869 | 3.6 | 3.75 |
| A5 LPC regimes (deployable) | 0.000144 | 0.000253 | 0.000639 | 0.0109 | 0.105 | 0.000131 | 0.869 | 3.33 | 3.48 |
| A4o LPC closed form (oracle seeds) | 0.000116 | 0.000208 | 0.000559 | 0.00958 | 0.108 | 5.97e-05 | 0.905 | 3.63 | 3.77 |
| A* Oracle state-optimal weight | 9.49e-05 | 0.000183 | 0.000466 | 0.00704 | 0.0778 | 0 | 1 | 3.7 | 3.83 |

Oracle recovery: A4 recovers -68% of the oracle-seed closed form's gain over A2; A5 recovers -9.42% of A*'s.

### chua

| Rule | MSE 0.25LT | MSE 0.5LT | MSE 1LT | MSE 2LT | MSE 4LT | regret H_ref | agreement | KM median (LT) | RMST (LT) |
|---|---|---|---|---|---|---|---|---|---|
| A0 CP alone | 0.00637 | 0.0314 | 0.134 | 0.508 | 1.19 | 0.111 | 0.145 | 2 | 2.24 |
| A1 PLP alone | 0.00539 | 0.00614 | 0.0215 | 0.212 | 0.648 | 0.00504 | 0.855 | 3.23 | 3.4 |
| A2 Global fixed weight | 0.0051 | 0.00572 | 0.0228 | 0.19 | 0.555 | 0.00543 | 0.855 | 2.6 | 2.79 |
| A3 Error-predictor allocator (Heuer-inspired) | 0.00531 | 0.00621 | 0.0224 | 0.197 | 0.563 | 0.00515 | 0.855 | 2.87 | 2.99 |
| A4 LPC closed form (deployable) | 0.0045 | 0.00541 | 0.023 | 0.195 | 0.584 | 0.00554 | 0.853 | 2.9 | 3.09 |
| A4f LPC full form with amplifier (deployable) | 0.00452 | 0.00545 | 0.023 | 0.194 | 0.584 | 0.00555 | 0.853 | 2.9 | 3.09 |
| A5 LPC regimes (deployable) | 0.00481 | 0.00593 | 0.0211 | 0.192 | 0.563 | 0.0042 | 0.855 | 2.6 | 2.8 |
| A4o LPC closed form (oracle seeds) | 0.000622 | 0.00135 | 0.0221 | 0.177 | 0.563 | 0.00462 | 0.872 | 2.93 | 3.17 |
| A* Oracle state-optimal weight | 0.000588 | 0.00111 | 0.0163 | 0.126 | 0.377 | 0 | 1 | 3.17 | 3.26 |

Oracle recovery: A4 recovers -39.5% of the oracle-seed closed form's gain over A2; A5 recovers 26.2% of A*'s.

## Validation gate

| Check | Criterion | lorenz63 | rossler | chua |
|---|---|---|---|---|
| V1 delay-map Jacobian vs finite differences | < 1e-4 | 1.49e-09 PASS | 1.35e-09 PASS | 4.46e-09 PASS |
| V1 amplifier g_H vs finite differences | < 1e-4 | 1.74e-07 PASS | 1.38e-09 PASS | 1.72e-09 PASS |
| V2 least squares / Cramer-Rao | [0.8, 1.2] | 0.954 PASS | 0.982 PASS | 0.95 PASS |
| V3 CP valid-prediction time (LT, theta=0.4) | reported | 2.03 | 3.53 | 2.7 |
| V4 w* bootstrap half-width at used M | <= 0.05 | 0.037 PASS | 0.039 PASS | 0.0308 PASS |
| V5 Kaplan-Meier vs exact | < 0.01 | 0.00583 PASS | 0.00583 PASS | 0.00583 PASS |
| V6 RK4 step halving (sigma_x) | < 1e-3 | 3.93e-05 PASS | 3.31e-05 PASS | 7.54e-05 PASS |

## Robustness (core cell)

### lorenz63

| Variant | H2a range | H2a partial r | A4 vs A2 | A4/A3 | A5 regret | H1c CP | H1c PLP |
|---|---|---|---|---|---|---|---|
| base | 0.118 | 0.061 | 19.1% | 1.51 | 61.6% | 1.22 | 0.823 |
| D=5 | 0.143 | -0.00082 | 7.25% | 1.28 | 86.9% | 1.5 | 0.909 |
| D=10 | 0.136 | 0.0049 | 16.8% | 1.73 | 324% | 1.44 | 0.86 |
| delay/2 | 0.182 | 0.26 | 9.19% | 1.05 | 42.6% | 1.51 | 0.971 |
| k=5 | 0.204 | 0.19 | 33.8% | 1.47 | 50.9% | 0.592 | 0.823 |
| misspec=0.05 | 0.244 | -0.045 | 13.2% | 0.994 | 109% | 1.22 | 0.654 |
| misspec=0.1 | 0.146 | -0.13 | 7.15% | 1.01 | 84% | 1.22 | 0.533 |
| Lambda_fin(eps=1rho) | | 0.056 | | | | | corr(fin, lin) 1 |
| Lambda_fin(eps=3rho) | | 0.026 | | | | | corr(fin, lin) 0.96 |
### rossler

| Variant | H2a range | H2a partial r | A4 vs A2 | A4/A3 | A5 regret | H1c CP | H1c PLP |
|---|---|---|---|---|---|---|---|
| base | 0.28 | 0.13 | 7.06% | 0.99 | 19.7% | 1.62 | 0.672 |
| D=5 | 0.281 | 0.086 | -2.43% | 0.992 | 19.6% | 1.31 | 0.697 |
| D=10 | 0.248 | 0.15 | 5.33% | 0.968 | 16.6% | 1.46 | 0.673 |
| delay/2 | 0.285 | 0.075 | 8.59% | 1.02 | 22% | 1.47 | 0.698 |
| k=5 | 0.383 | 0.15 | 21.5% | 1.19 | 18.5% | 0.897 | 0.672 |
| misspec=0.05 | 0.212 | -0.039 | 29% | 1.49 | 47% | 1.62 | 0.266 |
| misspec=0.1 | 0.15 | -0.16 | 19.3% | 1.25 | 44.2% | 1.62 | 0.212 |
| Lambda_fin(eps=1rho) | | 0.14 | | | | | corr(fin, lin) 0.99 |
| Lambda_fin(eps=3rho) | | 0.14 | | | | | corr(fin, lin) 0.98 |
