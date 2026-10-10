---
title: "Methods and Experimental Procedures (v2)"
subtitle: "State-dependent allocation between an analog and a physics-based forecaster via four local predictability conditions"
date: "10 October 2026"
---

# M0. Scope and status

This document replaces §6 of the proposal and supersedes Methods v1 (5 October). It specifies the experiments, quantities, theorems used, and pre-registered criteria for the confirmatory run.

**Changes from v1.** v2 applies the decisions of 10 October (decision log D1–D6), which followed an adversarial audit of v1:

- three core systems (Lorenz-96 and transfer dropped);
- four local predictability conditions kept, with the fourth *estimated*, not pass/fail tested;
- the exact model only;
- two theorems for the student to prove by hand (P1, P2), with a third (P3) optional;
- a reduced, feasible hypothesis set.

Every change is listed in §M14.

**Relation to code.** The pilot ran with code v1. The changes code v2 needs to match this document are listed in §M15; none are needed for the 30 October submission.

**Structure.** §M1–§M12 are the methods proper. §M13–§M16 (limitations, amendment log, code changes, future work) are appendices for reviewers.

**What is run when.** The confirmatory run is the `full` preset on fresh random seeds, after 30 October and after this document is frozen. The pilot (`pilot` preset, 5–6 October) was exploratory. Pilot numbers quoted here are for design and precision only.

# M1. Notation

Symbols are defined here and on first use.

| Symbol | Meaning |
|---|---|
| s, ŝ | latent state (whitened), its estimate |
| x_t, X_t | scalar observation at step t; delay vector in ℝ^D |
| h̃ | normalized observable, (h − mean)/σ_x |
| ρ | observation-noise standard deviation, as a fraction of σ_x |
| D, τ_d | embedding dimension; delay in steps |
| G, J | delay map s ↦ noise-free delay vector; its Jacobian (D × m) |
| ν | observability factor, ν² = tr[(JᵀJ)⁻¹] (whitened) |
| Φ^H, g_H | flow over H steps; amplification ‖∇h̃ DΦ^H‖ |
| Λ̄, Λ̃ | growth exponent (slope of ln g_H per step over 1 LT); Λ̃ = 30 Λ̄, the exponent in units of λ_max |
| λ_max, LT | largest Lyapunov exponent; Lyapunov time 1/λ_max (= 30 steps) |
| R | delay-space distance from the query to its nearest library analog |
| Δ | nearest-neighbor margin r₂ − r₁ |
| ε_s, δ | analog seed and estimation seed (r.m.s. state error of CP's analog and of PLP's estimate) |
| N | **noise sensitivity of analog retrieval** (fourth LPC; §M5) |
| r₁, r₂ | nearest and second-nearest library distances from the clean query (P2); r₁ = R up to noise |
| N_lib | **library size** (number of admissible analogs). Written N in Mathematical Framework v2 (FW) |
| e_C, e_P | CP and PLP forecast errors against the noise-free truth |
| E_C, E_P, C | E[e_C²], E[e_P²], E[e_C e_P] over noise draws at a state |
| V(w) | hybrid MSE as a function of the weight (P1, P3); not to be confused with checks V1–V7 |
| w, w* | weight on CP in the hybrid; its MSE-optimal value |
| c | curvature E[(e_C − e_P)²] |
| θ, T | error tolerance (fraction of σ_x); predictability horizon (first passage) |
| H_ref | reference horizon, 1 LT |
| k | number of analogs averaged (1 unless stated) |
| CP, PLP | context parroting (analog forecaster); physics-based latent-state propagation |
| LPC | local predictability condition |

The four LPCs are:

- recurrence (through R and ε_s);
- observability (ν, δ);
- instability (Λ̄);
- noise sensitivity (N).

# M2. Systems and data generation

| System | m | Parameters | Observable | λ_max |
|---|---|---|---|---|
| Lorenz-63 | 3 | σ = 10, r = 28, b = 8/3 | x | 0.905 |
| Rössler | 3 | a = b = 0.2, c = 5.7 | x | 0.0719 |
| Chua (piecewise-linear diode) | 3 | α = 15.6, β = 28, m₀ = −1.143, m₁ = −0.714 | x | 0.431 |

Here m is the state dimension.

**Lyapunov exponent.** λ_max is computed by Benettin's method with QR re-orthonormalization.

**Time step and integration.**

- The observation interval is set so that 1 LT = 30 steps.
- The flow is fixed-step RK4. Internal steps:
  - Lorenz-63: ≤ 0.01;
  - Rössler: ≤ 0.04;
  - Chua: ≤ 0.005. Halving the step must change the observable by < 10⁻³ σ_x over 1 LT (check V6).
- Truth and the PLP model use the same integrator. This is the exact-model design (D2).

**Trajectories.** Each discards a 100-LT burn-in. Three trajectories are generated per system:

- **statistics:** 2×10⁵ steps, giving normalization, the invariant mean and covariance C_μ, τ_d and the autocorrelation time;
- **main:** library and evaluation segments;
- **separate:** from a perturbed start; used only to train the learned initial guess of the state estimator.

**Coordinates.** Latent quantities are whitened, s̄ = C_μ^(−1/2)(s − μ). Seeds, ν, g_H and the profile are therefore dimensionless and comparable across systems.

# M3. Observation, embedding, sampling

**Noise.** x_t = h̃(s_t) + η_t, with η_t ~ N(0, ρ²) i.i.d. and ρ ∈ {0.5, 1, 2, 5}%.

The same standard-normal draws are scaled by each ρ and reused across N_lib (common random numbers). This makes level differences reflect the intervention, not resampling.

**Embedding.** X_t = (x_t, x_{t−τ_d}, …, x_{t−(D−1)τ_d}), with D = 7.

- τ_d is the first minimum of the three-point-smoothed average mutual information, capped so that (D−1)τ_d ≤ 1 LT.
- Resulting τ_d: Lorenz-63 5, Rössler 3, Chua 5 steps.

**Thinning.**

- Evaluation states are 5·min(τ_ac, 1 LT) apart, where τ_ac is the ACF-envelope 1/e time.
- They are also at least one Theiler window (1 LT) apart.

# M4. Forecasters and the hybrid

**CP (context parroting).**

- **Library.** A contiguous noisy segment holding N_lib admissible analogs. An analog is admissible if it has full delay history and at least H_max future values. Libraries are nested across N_lib.
- **Search.** Exact Euclidean k-d tree search.
- **Forecast.** x̂ᶜᵖ_{t+H} = x_{i*+H}, the noisy future of the nearest analog i*.
- **Recurrence distance.** R_t = ‖X_t − X_{i*}‖.

**PLP (physics-based latent-state propagation).** ŝ_t = ψ(X_t) and x̂ᴾᴸᴾ_{t+H} = h̃(Φ^H(ŝ_t)). The estimator ψ has two stages:

1. **Learned initial guess.** An MLP (2 hidden layers, width chosen from {64, 128} by a capacity rule) maps X_t to the whitened window-start state.
   - It is trained on 10⁵ pairs from the separate trajectory.
   - Fresh noise at the cell's ρ is drawn for every minibatch.
2. **Model-based refinement.** Fifteen Levenberg–Marquardt iterations minimize ‖X_t − G′(u)‖² over the window-start state u.
   - G′ integrates the known model forward from u.
   - Steps are accepted only if the cost decreases.

Stage 2 is the Gaussian maximum-likelihood estimate, so it attains the Cramér–Rao floor ρν to first order (validation V7).

Wrong-basin convergence (about 2% of draws on Lorenz-63 at ρ = 1% in the pilot) is a real property of nonlinear estimation. Such estimates are kept, not filtered.

**Hybrid and error clipping.**

- The hybrid forecast is x̂ = w x̂ᶜᵖ + (1 − w) x̂ᴾᴸᴾ, with w ∈ [0, 1].
- Errors are measured against the noise-free truth and clipped at 10 σ_x.
- True states are used only to train stage 1 and for oracle quantities. They are never forecaster inputs.

# M5. Per-state quantities

## Oracle quantities (privileged; for mechanism and references)

For each state, M = 200 independent query-noise draws are made. Each draw gives an analog, an estimate and errors at every horizon.

| Quantity | Definition |
|---|---|
| ε_s, δ | ε_s² = mean_r ‖ā^(r) − s̄‖² and δ² = mean_r ‖ŝ̄^(r) − s̄‖², over draws r |
| ν | ν² = tr[C^(−1/2) Q (AᵀA)⁻¹ Qᵀ C^(−1/2)], with A = ∂X/∂s_old and Q = DΦ^((D−1)τ_d)(s_old) at the window-start state s_old. This equals tr[(JᵀJ)⁻¹] without inverting Q. |
| g_H, Λ̄ | g_H = ‖∇h̃ DΦ^H(s) C^(1/2)‖, H = 1…30. Λ̄ = least-squares slope of ln g_H on H. |
| **N (fourth LPC)** | N = (ρ√D)⁻¹ · [mean_r ‖Y_r − mean_r Y_r‖²]^(1/2), where Y_r is the delay vector of the analog retrieved under draw r: the r.m.s. displacement of the retrieved analog caused by noise, per coordinate, in noise units. Theorem P2 bounds it in terms of the margin Δ and the nearest distance, in noise units. |
| E_C, E_P, C | sample second moments at every horizon (raw, not centered) |
| w* | Unclipped u = (E_P − C)/c with c = E_C + E_P − 2C; w* = clip₀¹(u) (Theorem P1). |
| Characteristic horizon | First H at which √(E e² + ρ²) > θ, censored at H_max |
| Local dimension d | Levina–Bickel MLE (k = 20) on 2×10⁴ library states |

## Deployable proxies (observations, the model and ρ only)

| Proxy | Definition | Fitted |
|---|---|---|
| ν̂ | ν(ŝ), winsorized at its 99th construction percentile | cap |
| ε̂ | ε̂² = a_ε(R ν̂)² + b_ε(ρ ν̂)² (FW Lemma 1 and eq. 3.1) | a_ε, b_ε |
| δ̂ | δ̂² = a_δ(ρ ν̂)² + b_δ ρ² | a_δ, b_δ |
| Λ̂ | slope of ln g_H(ŝ) over 1 LT under the model | — |
| N̂ | Spread of the retrieved analogs' delay vectors under 16 synthetic perturbations X + ρz of the *observed* query, in units of ρ√D | — |

**Fitting.** Coefficients are fitted by robust (soft-ℓ₁) least squares on the log scale, against the oracle squared seeds of the construction states.

**Estimand of N̂.** N̂ estimates the retrieval sensitivity at the observed query, which is displaced from G(s) by one noise draw. It is not an unbiased estimate of N, and its fidelity is reported, not tested (§M10).

**Deployable profile.** F̂ = (ln(ε̂/ρ), ln(δ̂/ρ), 30 Λ̂, ln(N̂ + 0.01)): recurrence, observability, instability and noise sensitivity, in that order. The oracle profile F uses ε_s, δ, Λ̄ and N.

# M6. Horizons and censoring

**Realized horizon.** T = min{H ≥ 1 : |x̂_{t+H} − x_{t+H}|/σ_x > θ}, where x_{t+H} is the *noisy* verifying observation. T is right-censored at H_max = 8 LT = 240 steps.

**Tolerances.**

- θ ∈ {0.1, 0.2, 0.3, 0.5}, restricted to θ ≥ 3√2ρ (FW Prop. 4 validity). All four are used at ρ ≤ 2%; only {0.3, 0.5} at ρ = 5%.
- θ = 0.2 is primary.

**Summaries.**

- Kaplan–Meier median and restricted mean (RMST) in LT.
- Regimes are compared by the log-rank test, Holm-adjusted.
- Censored horizons are never averaged.

# M7. Allocation rules

All rules output a weight on CP per state, evaluation draw and horizon.

| ID | Rule | Inputs | Fitted on |
|---|---|---|---|
| A0 | CP alone (w = 1) | — | — |
| A1 | PLP alone (w = 0) | — | — |
| A2 | Global weight per horizon (pooled MSE minimizer) | — | construction |
| A3 | Error-predictor allocator (adapted from Heuer et al. 2026). An MLP maps X_t to log ê²_CP(H) and log ê²_PLP(H); w = ê²_PLP/(ê²_CP + ê²_PLP). | X_t | construction |
| A4 | Two-seed closed form (FW Cor. 1): w = δ̂²/(ε̂² + δ̂²) | R, ν(ŝ), ρ | 4 proxy coefficients |
| A5 | Regime map: a regression tree on the four-coordinate F̂ with K leaves. Regime weight: P3's optimal regime weight. Regime horizon: KM median. | F̂ | tree on construction; weights and horizons on calibration |
| A4o | A4 with oracle seeds (reference) | ε_s, δ | — |
| A* | State-optimal w*(s, H) (reference) | true state | — |

**Choosing K for A5.** K is the smallest value in {2, 3, 4, 5, 6, 8} whose calibration excess MSE is within 5% of the minimum over that set.

**Fairness.** A3, A4 and A5 see the same construction states and draws.

# M8. Data partition and leakage

The main trajectory is laid out as `[library][gap][construction][gap][calibration][gap][test]`. Each gap is ϑ + (D−1)τ_d + H_max steps, with ϑ the Theiler window (1 LT), so no delay or verification window crosses a segment boundary.

| Set | full preset |
|---|---|
| Construction (proxies, A2, A3, trees) | 2000 states |
| Calibration (K; regime weights and horizons) | 1000 |
| Test (final evaluation) | 1000 |
| Sweep cells (E1, E2) | 1000 (pilot 300; §M12) |
| Oracle draws M / evaluation draws E per state | 200 / 4 |

**Leakage rules.**

- Nothing in a test state's windows appears in another set.
- Forecast outcomes and oracle quantities are training targets only.
- K is chosen on calibration.
- Oracle and evaluation noise draws are independent.

# M9. Theory used by the study

The student proves P1 and P2 by hand; P3 is optional (D4). Everything else is cited as a standard result with its hypotheses stated.

## Theorem P1 (optimal weight and the horizon-gain bound)

At a fixed state and horizon, let V(w) = E[(w e_C + (1 − w)e_P)²], with E_C, E_P and C as in §M1.

- **(a)** V(w) = c(w − u)² + V(u), with c = E_C + E_P − 2C and u = (E_P − C)/c. If CP's error contains copied future noise ξ with E[ξ²] = ρ²/k, orthogonal to e_P and to e_C − ξ (E[ξ e_P] = E[ξ(e_C − ξ)] = 0; it suffices that ξ is independent of both, with E[ξ] = 0), then c ≥ ρ²/k > 0. So V is strictly convex, and its minimizer on [0, 1] is w* = clip₀¹(u).
- **(b)** w* = u, which lies in [0, 1], if and only if C ≤ min(E_C, E_P).
- **(c)** If C ≥ 0, then min over w ∈ [0, 1] of V(w) ≥ ½ min(E_C, E_P).
- **(d)** Suppose C ≥ 0 at every horizon, and the better single forecaster's r.m.s. error is r₀e^(ΛH), with Λ > 0. Then the optimal hybrid's characteristic horizon exceeds that forecaster's by at most ln 2/(2Λ).
- **(e)** (c) fails without C ≥ 0. Counterexample: E_C = E_P = 1, C = −1 gives min V = 0.

**Remark (separation; FW Cor. 1).** If the amplified seed covariances are proportional across horizons, u does not depend on H. With uncorrelated seeds it reduces to δ²/(ε_s² + δ²), the rule A4 approximates.

## Theorem P2 (retrieval stability; the fourth LPC)

Let X₁, …, X_n be library vectors and x a query. Let i₁ be the nearest, at distance r₁, with margin Δ = r₂ − r₁ > 0, where r₂ is the second-nearest distance. Let η be noise with E‖η‖² = Dρ².

- **(a)** If ‖η‖ < Δ/2, the nearest analog of x + η is still i₁.
- **(b)** Pr(retrieval changes) ≤ Pr(‖η‖ ≥ Δ/2) ≤ 4Dρ²/Δ².
- **(c)** N² ≤ (4/(ρ²D)) · E[(r₁ + ‖η‖)² 1{‖η‖ ≥ Δ/2}].

**Consequence for the study.** N is bounded by a function of the margin and the nearest distance in noise units, Δ/ρ and r₁/ρ. It is small when Δ ≫ ρ√D. The margin is a different order statistic of the library from r₁, which equals R. N can therefore carry state-level information that the other three coordinates do not. FW's remark that noise acts "only through ρ" holds for PLP (to first order its noise sensitivity is ρ g_H ν) and on average over library sampling, but not state by state on the CP side.

So the study *estimates* how much N adds (Q-N, §M11). It does not assume redundancy.

## Theorem P3 (abstraction regret and its floor)

For states i, let V_i(w) = c_i(w − u_i)² + V_i(u_i) as in P1(a).

- **(a) Regime weight.** For a regime S, Σ_{i∈S} V_i(w) on [0, 1] is minimized by w_S = clip₀¹(Σ c_i u_i / Σ c_i).
- **(b) Measurability floor.** Let F be a profile and f any rule that is a function of F, with values in [0, 1]. Then
  E[V(f(F))] ≥ E[V(clip₀¹ ū(F))], where ū(F) = E[c u | F]/E[c | F].

  The difference between the right-hand side and E[V(w*)] is a floor on the excess MSE of every F-measurable rule, including every regime map, for every K. The floor vanishes when u is a function of F, and is generally positive otherwise.

**Why P3 matters.** P3(b) explains the pilot's flat regret-versus-K curve without attributing it to any single cause. The floor is positive whenever w* is not determined by the profile, whether because of proxy noise, seed anisotropy or cross-covariance. A4o, which uses exact seeds, also shows excess MSE above A*.

## Cited results (not proved by the student)

| Result | Source | Used for |
|---|---|---|
| Error = seed × amplifier + quadratic remainder | Taylor's theorem; FW Prop. 1 | H1c |
| Linearized estimation error ρ²(JᵀJ)⁻¹; Gauss–Markov; Cramér–Rao | FW Prop. 2 | V2, V7 |
| Delay distance bounds latent mismatch | FW Lemma 1 | ε̂ proxy |
| Nearest-neighbor scaling ε_s² ≈ b²N_lib^(−2/d) + floor | FW eq. 3.1; nearest-neighbor asymptotics | H1b |
| Horizon law T ≈ Λ̄⁻¹ ln(θσ_x√m/e₀) | FW Prop. 4 | H1d |
| Long-horizon limit of w* (Oseledets) | FW Remark, §5.2 | reading of H2a |

**Assumption A6 (FW).** Seeds are small enough that first-order expansions hold up to the horizons used, and errors have not saturated. H2a's small-error regime (both r.m.s. errors ≤ 0.5 σ_x) is the operational form of A6.

## Cross-reference

| FW v2 | Theorem program (L) | Methods v2 |
|---|---|---|
| Prop. 3 | L5 | P1(a), (b) |
| Cor. 2 (hybrid gain) | L7 | P1(c)–(e) |
| Cor. 1; Remark §5.2 | L6, L6′ | P1 remark; cited |
| Prop. 5 | L10(i)–(iii) | P3(a) |
| — (new) | L10 floor | P3(b) |
| Remark §3.2 ("two seeds, one noise level") | L11(a) | qualified by P2 |
| — (new) | L11(b) | P2 |
| Props. 1, 2, 4; Lemma 1; eq. 3.1 | L1, L2–L3, L8, L4, L12 | cited |
| eq. 8.1 (K^(−2/p) rate) | L10′ | dropped (H3b) |

# M10. Experiments

**E0. Validation gate.** Run first for every system. A failure is flagged at the top of the report and marks that system's results provisional.

| Check | Pass criterion |
|---|---|
| V1. Jacobians A and g_H vs. central finite differences | relative error < 10⁻⁴ |
| V2. Gauss–Newton at ρ = 10⁻⁴ attains ρ²ν² | ratio in [0.8, 1.2] |
| V3. CP valid-prediction time at θ = 0.4 (reported) | — |
| V4. w*(H_ref) convergence, M ∈ {50, 200, 800} | median half-width at M = 200 ≤ 0.05 |
| V5. Kaplan–Meier vs. exact censored geometric survival | max deviation < 0.01 |
| V6. RK4 step-halving over 1 LT | < 10⁻³ σ_x |
| **V7. Estimator efficiency** (formerly H1a). Median δ/(ρν) at every ρ, and median per-state slope of ln δ on ln ρ | both in [0.9, 1.1] |

**E1. Noise sweep.** ρ ∈ {0.5, 1, 2, 5}% at N_lib = 10⁴, with ψ trained at each ρ. Feeds V7 and H2b(i).

**E2. Library sweep.** N_lib ∈ {10³, 10^3.5, 10⁴, 10^4.5, 10⁵} at ρ ∈ {1, 2}%, with nested libraries.

- Feeds H1b, H2b(ii) and H2f.
- Also reports the mean and median w* at each N_lib, and the change between the two largest libraries.

**E3. Mechanism at the core cell** (ρ = 1%, N_lib = 10⁴; horizons 1–240). Feeds H1c–H1e and Q-N.

- Seed × amplifier regression at H_ref.
- Characteristic horizons over θ.
- Proxy–oracle rank correlations.
- **Q-N.** Gradient-boosted regressors (300 iterations, learning rate 0.05, ≤ 15 leaves, ≥ 20 samples per leaf) are fitted on construction and calibration states with the three-coordinate and the four-coordinate oracle profile. Targets: logit w*(H_ref) and log characteristic horizon. Statistic: out-of-sample ΔR² on test states, with a block-bootstrap interval. The same is repeated on the deployable profile (secondary). The R² of N predicted from the other three is also reported.

**E4. Allocation and separation.** All rules of §M7 on the core test split. Feeds H2a, H2c, H2d and H2e.

- Measures:
  - realized MSE at H ∈ {0.25, 0.5, 1, 2, 4} LT;
  - excess MSE over A*;
  - Kaplan–Meier median and RMST at θ = 0.2;
  - w*(H) per state;
  - partial correlation with Λ̃;
  - hybrid horizon gain.
- **Excess MSE** is computed exactly as V(w) − V(w*) from the moments. This fixes v1, which used c(w − w*)² with clipped w* and so understated the excess for clipped states.

**E5. Interventional shift (reported, no criterion).**

- Rules are fitted at the core cell and applied without refitting at ρ ∈ {0.5, 2, 5}% and at N_lib ∈ {10³, 10⁵}.
- Reported: the excess-MSE ratio to A* for A3, A4 and A5.

**E6. Regimes.** A5 for K ∈ {2, 3, 4, 5, 6, 8, 12, 16}. Feeds H3a, H3c and H3d.

- Measures:
  - excess MSE versus K, with the A4o and A* references;
  - within-regime IQR of the characteristic horizon;
  - Holm-adjusted log-rank tests between regimes consecutive in calibration median horizon;
  - importances of a weight tree and a horizon tree on F̂.

**E7. Robustness (Lorenz-63 and Rössler; reported only).** Each variant reruns the core cell:

- D ∈ {5, 10};
- k = 5 analogs;
- PLP model parameters perturbed by ±5% and ±10%;
- finite-amplitude Λ_fin in place of Λ̄.

# M11. Pre-registered hypotheses and decision rules

**Intervals.** Moving-block bootstrap over test states in temporal order (blocks of 5 states, about 7–25 LT; 2000 resamples).

**Primary endpoints.** There are three: H2a, H2b and H3d. They use intervals at level 1 − 0.05/3. All other intervals are 95%, and the other hypotheses are secondary.

**Per-system verdict.** Each criterion is a band or a one-sided bound. A system gets:

- **pass** if the interval lies inside the band, or entirely on the predicted side of the bound;
- **fail** if the interval lies entirely outside;
- **inconclusive** otherwise.

**Multi-part criteria.** Where a criterion has several parts (H1e, H2a, H2b, H2c, H2f, H3c), a system passes only if every part passes, fails if any part fails, and is otherwise inconclusive.

**Overall verdict.**

- **supported:** pass on all three systems;
- **not supported:** fail on at least one system;
- **inconclusive:** otherwise.

"Supported" requires every system to pass. This is an intersection–union test, so it needs no further multiplicity correction. The v1 category "partially supported" is retired.

| ID | Question | Statistic | Pass if |
|---|---|---|---|
| H1b | Analog seed scales with library size | Fit of **median** ε_s² over states to b²N_lib^(−2/d) + f², per ρ (E2) | interval of 1/d_fit within ±25% of 1/d_LB at both ρ; floor f reported |
| H1c | PLP error is seed × amplifier | OLS slope of ln √(E e_P²) on ln(g_H δ/√m) at H_ref. The CP slope is reported (it assumes isotropic seeds; §M13). | slope in [0.8, 1.2] |
| H1d | Horizon law | Median over eligible states of Λ̄ × slope of characteristic T(θ) on ln θ (PLP) | in [0.8, 1.25] |
| H1e | Deployable proxies track the oracles | Spearman ρ_S of (ε̂, ε_s), (δ̂, δ), (Λ̂, Λ̄). (N̂, N) is reported, not tested. | each ≥ 0.7 |
| Q-N | How much does N add? *(estimate, no pass/fail)* | Oracle ΔR² (four vs. three coordinates) for logit w*(H_ref) and log horizon, with interval; deployable ΔR² secondary | Read by the table below |
| **H2a** | Separation: once seeds are fixed, w* does not depend on H or Λ̃ | (i) Median range of w*(H) over {1, 2, 4} LT in the small-error regime; unrestricted range reported. (ii) Partial correlation of logit w*(H_ref) with Λ̃ given ln(ε_s/ρ), ln(δ/ρ). | (i) interval < 0.1 **and** (ii) interval within (−0.1, 0.1) |
| **H2b** | The knobs move the weight as theory predicts | (i) Mean per-state Spearman correlation of w*(H_ref) with ρ (E1). (ii) Mean paired change in w*(H_ref) from N_lib = 10³ to 10⁴ at ρ = 1% (E2). The full mean-w* curve at ρ = 1% and 2% is reported. | both lower bounds > 0 |
| H2c | State-dependent allocation beats a global weight | Mean paired MSE difference at H_ref: A4 − A2, and A4 − better of (A0, A1). A4o − A2 reported. | both upper bounds < 0 |
| H2d | Closed form vs. empirical allocator | MSE_A4/MSE_A3 − 1 at H_ref | upper bound ≤ 0.10 |
| H2f *(new, from the pilot)* | Noise matching: the CP and PLP errors become correlated as the library grows | Median per-state change in corr(e_C, e_P) at H_ref from N_lib = 10³ to 10⁵, at ρ = 1% and 2% (E2). The correlation is set to 0 where CP's error does not vary across draws. | lower bound > 0 at both ρ |
| H2e | Gain bound (P1(d)) *(reported)* | Fraction of eligible states with gain ≤ ln 2/(2Λ̄) + 1 step. Also reported for the subset satisfying P1's hypotheses at every horizon. | — |
| H3a | Regimes separate horizons | Holm-adjusted log-rank p between consecutive regimes at the chosen K; IQR reported | all p < 0.01 |
| H3c | Instability sets the horizon, not the weight | Impurity importances: weight tree (target w*, curvature weights) and horizon tree, on F̂ | weight-tree Λ̃ < 0.2; horizon-tree Λ̃ > each other coordinate |
| **H3d** | A few regimes cost nothing vs. the closed form | MSE_A5/MSE_A4 at H_ref | upper bound ≤ 1.05 |

**Reading Q-N (decision D1).** The primary target is logit w*(H_ref).

| Oracle ΔR² interval | Reading |
|---|---|
| upper bound < 0.05 and lower bound ≤ 0 | N **reduces to the other three** at this study's precision |
| lower bound > 0 and upper bound < 0.05 | N is **distinct but small** |
| lower bound > 0 and upper bound ≥ 0.05 | N **carries substantial additional information** |
| otherwise | **undetermined** |

**Why H2f was added.** In a recheck of the pilot library sweep (10 October), mean w* rose with N_lib and then fell, on every system and at both noise levels:

- the peak was at N_lib ≈ 10⁴–10^4.5 at ρ = 1%, and ≈ 10^3.5 at ρ = 2%;
- the analog seed kept shrinking;
- the median CP–PLP error correlation rose steadily, from 0.00–0.15 at 10³ to 0.39–0.46 at 10⁵.

**Proposed mechanism (noise matching).** As the library grows, the margin Δ shrinks. P2 then says retrieval becomes sensitive to the query noise, so the analog fits the same noise realization the estimator fits. The resulting positive C lowers w* through P1(a). The peak should then move to smaller N_lib as ρ grows, which is what the pilot shows.

This links the fourth LPC to the weight through the cross-moment C. H2f tests the mechanism on fresh seeds. H2b(ii) tests only the rising branch, at the core noise level, where the pilot puts the peak at or above 10⁴.

**Pre-registered readings.**

- **H2a fails.** Instability enters the weight through seed anisotropy (FW long-horizon remark). The measured departure quantifies how far real attractors are from proportional seed covariances.
- **H2c fails but A4o beats A2.** The closed form is right, and the deployable seeds limit it.
- **H3d holds while excess MSE is flat in K.** This is consistent with the P3 floor.

All outcomes are reported, including failures.

# M12. Precision of the confirmatory run

**How the table was built.**

- Half-widths are the largest over the three systems in the pilot.
- They are projected to the full preset by √(n_pilot/n_full):
  - ×0.71 for test-split statistics (500 → 1000 states);
  - ×0.55 for sweep statistics (300 → 1000).
- Primary endpoints are at level 1 − 0.05/3. All others are at 95%.
- The pilot estimates are exploratory, and the confirmatory run uses fresh seeds.

| Hypothesis | Pilot estimate (L63 / Rössler / Chua) | Pilot half-width | Projected half-width | Outlook at full size |
|---|---|---|---|---|
| H1b 1/d_fit (ρ = 1%) | 0.50 / 0.37 / 0.37 (1/d_LB 0.51 / 0.55 / 0.51); from v1's mean-ε² fit | 0.13 | 0.07 | Band ±25% is about ±0.13, so this is decidable. Rössler and Chua lie below the band's lower edge (0.41, 0.38). |
| H1c PLP slope | 0.82 / 0.67 / 1.01 | 0.05 | 0.04 | Decidable. Lorenz-63 sits at the band edge. |
| H1d PLP ratio | 0.75 / 0.98 / 0.65 | 0.12 | 0.08 | Chua (likely fail) and Rössler (likely pass) are decidable. Lorenz-63 sits near the 0.8 edge. |
| H1e ε̂, δ̂, Λ̂ | ε̂ 0.68–0.77; δ̂ 0.82–0.96; Λ̂ 0.97–0.99 | ≤ 0.05* | ≤ 0.04* | ε̂ on Rössler (0.74) and Chua (0.68) is borderline. δ̂ and Λ̂ are decidable. |
| Q-N oracle ΔR² | 0.02 / 0.09 / 0.07 | 0.05 | 0.04 | All four readings are reachable. |
| **H2a(i)** median range | 0.12 / 0.28 / 0.17 | 0.06 | 0.04 | Decidable. Rössler and Chua already exceed 0.1. |
| **H2a(ii)** partial r | 0.06 / 0.13 / 0.13 | 0.14 | 0.10 | **Can refute, cannot pass.** Passing needs \|r\| ≲ 0.01. Passing at \|r\| = 0.05 would need about 2300 eligible states. |
| **H2b(i)** ρ Spearman | 0.24 / 0.16 / 0.25 | 0.10 | 0.05 | Decidable (pass). |
| **H2b(ii)** mean rise, 10³ → 10⁴ (ρ = 1%) | 0.054 / 0.079 / 0.055 | 0.05 | 0.03 | Decidable (pass). At ρ = 2% the rise is 0.01–0.02 with intervals including 0 (reported only). |
| H2f correlation rise, 10³ → 10⁵ | 0.28–0.29 / 0.27–0.36 / 0.21–0.29 (paired median change; E2 recheck) | 0.08 | 0.04 | Decidable (pass). |
| H2c A4 − A2 (relative MSE) | +19% / +7% / +1% | 23% | 17% | Lorenz-63 is decidable. Rössler and Chua are likely inconclusive. |
| H2d MSE_A4/MSE_A3 − 1 | 0.51 / −0.01 / 0.03 | 0.45 | 0.32 | Lorenz-63 likely fails; Rössler already passes (upper bound 0.08); Chua likely inconclusive. |
| **H3d** MSE_A5/MSE_A4 | 0.72 / 0.96 / 0.91 | not computed in v1 | — | Point estimates are 9–31% below 1.05. |

\* H1e uses the Fisher-z approximation; v1 computed no bootstrap interval for it.

**Reading.**

- The confirmatory run can decide most hypotheses in at least one direction.
- **H2a can only be refuted.** Its equivalence clause (ii) cannot pass at any practical sample size unless the partial correlation is essentially zero. This is stated now so a "not supported" verdict is not read as a power failure.
- **Q-N** is reported with its interval whatever the reading.

# M13. Known limitations from the pilot

These come from pilot data and are stated before the confirmatory run so that its results are read correctly.

1. **The deployable closed form A4 depends, in effect, on R/ρ alone.**
   - The fitted proxies are ε̂² ≈ 0.26(Rν̂)², with the same constant 0.26 on all three systems and a floor near 0, and δ̂² ≈ (ρν̂)².
   - So ν̂ cancels: A4 ≈ 1/(1 + 0.26(R/ρ)²) on Lorenz-63 and Rössler. On Chua the fitted floor b_δ = 0.062 leaves a small ν̂ dependence.
   - A4 is therefore, in effect, a recurrence-in-noise-units rule. Observability enters the deployable allocation only through A5 and A3.
   - This also explains why A4 transferred to Chua at almost no cost in the pilot: the constant 0.26 is the same on every system.
2. **With an exact model and an efficient estimator, PLP dominates by 1 LT.**
   - Median w*(1 LT) is 0.05–0.09, and 22–36% of states sit at w* = 0.
   - CP's value lies at short horizons and in wrong-basin estimation events.
   - The allocation questions (RQ2, RQ3) are therefore asked in a regime where the stakes are modest. The misspecified-model arm that would raise them is future work (§M16).
3. **The deployable profile carries little information about w\*.** Out-of-sample R² for logit w* with the three-coordinate profile:
   - deployable: −0.02 to 0.05;
   - oracle: 0.25–0.49.

   Deployable-level conclusions about allocation are limited by the proxies, not by the theory.
4. **N̂ does not estimate N without bias** (§M5).
5. **The H1c statistic assumes isotropic seeds.** Analog seeds lie along the attractor and are anisotropic. CP's superlinear slope (1.2–1.6) may reflect this as much as a breakdown of the linear regime, so H1c is tested for PLP only.
6. **Estimator efficiency is near-tautological under this design** (common random numbers with a maximum-likelihood refinement). It is a validation check (V7), not a finding.
7. **v1's regret was a lower bound.** It used c(w − w*)² with clipped w*, which understates the excess MSE of clipped states. v1 regime weights were the curvature-weighted mean of *clipped* w*, which is not the optimum in P3(a). Both are corrected in v2 (§M15). The pilot's conclusion (excess flat in K, far above 5%) is unchanged in direction.
8. **Same attractors, fresh seeds.** The confirmatory run draws new noise, libraries and trajectories on the same three attractors. It gives higher precision and protection against tuning to the pilot's noise, not independent systems.

# M14. Changes from v1 and from the proposal

Dated amendment log (all 10 October 2026 unless noted). Changes marked † were made after seeing pilot data; their reasons are given.

| Change | Reason |
|---|---|
| Lorenz-96 and transfer hypothesis T1 dropped (D3) | Lorenz-96 PLP cannot be interpreted as designed (1 observable of 6); T1 rests on a single meaningful target |
| Misspecified-PLP arm deferred (D2) | It needs its own seed law and proxy; the theory here is for the exact model |
| H1f's redundancy test replaced by the Q-N estimate† (D1) | v1's prediction ("redundant") contradicted P2, which shows N carries pointwise information. The pilot's oracle ΔR² is 0.02–0.09. |
| Library size renamed N_lib | N meant both library size and the fourth LPC |
| H1a moved to validation (V7)† | Near-tautological under the design (§M13 item 6) |
| H1b fits the median ε_s² over states† | The mean is dominated by heavy-tailed wrong-lobe analogs |
| H1c tested for PLP only† | The statistic assumes isotropic seeds (§M13 item 5) |
| H1e: N̂ fidelity reported, not tested† | N̂'s estimand differs from N (§M5) |
| H2a: small-error restriction kept, unrestricted range reported (v1, 5 Oct)† | Separation is derived under A6; errors saturate by 4 LT |
| H2b(ii): mean paired change from N_lib = 10³ to 10⁴ at ρ = 1% replaces the per-state rank correlation across all five N_lib† | 22–36% of states sit at w* = 0 at every N_lib, so per-state rank correlations are dominated by ties. The mean w* rises and then falls (§M11, "Why H2f was added"), and its peak moves to smaller N_lib at ρ = 2%. The test targets the rising branch at the core noise level. ρ = 1% was chosen after seeing the ρ = 2% curve; the mechanism predicts the earlier peak there. |
| H2f added† | Pilot recheck of 10 October: CP–PLP error correlation rises with N_lib on every system (noise matching) |
| H2b: "median w*(N_lib = 10⁵) < 0.95" dropped | Vacuous (pilot medians 0.07–0.09) |
| H2d(ii) (n = 5 sign test) dropped; E5 reported only | Not informative with 5 cells |
| H2e reported without a pass/fail bar | The gain is ≥ 0 by construction; the 0.9 bar was arbitrary |
| H3a: 5% regret bar replaced by log-rank separation; H3b dropped; H3d becomes primary† | Even A4o (exact seeds) has excess equal to 9–45% of the mean per-state better-single-forecaster MSE, so the bar was unattainable for any profile-based rule (P3(b)). H3b's Lipschitz hypothesis is refuted by the deployable R². |
| K chosen within 5% of the minimum calibration excess | The v1 rule always fell through to K = 5 |
| Verdicts: pass / fail / inconclusive per system; "partially supported" retired | Its type-I rate under a global null was about 14% |
| Excess MSE and regime weights computed exactly (P1, P3) | Correctness (§M13 item 7) |
| A4f dropped | Identical to A4 to three digits on every system |
| Sweep states raised to 1000 in the full preset | Precision for H1b and H2b (§M12) |
| Robustness reduced to D, k, model perturbation and Λ_fin | Scope |
| M = 200 oracle draws (v1, 5 Oct)† | V4: at M = 50 the half-width was 0.055–0.073; at M = 200 it was 0.031–0.039 (criterion ≤ 0.05). *v1 wrongly said M = 100 had been tried.* |
| Analog proxy built from R·ν̂ (v1, 5 Oct)† | Chosen on pilot data: Spearman with ε_s rose from 0.50–0.64 to 0.71–0.73. The confirmatory run on fresh seeds tests it. |

Changes from the proposal's §6 that v1 introduced, and that remain (ψ refinement, deployable proxies, delay cap, Chua step, θ rule), are listed in Methods v1 §M12.

# M15. Code changes for v2 (after 30 October)

None of these changes the pilot's data path; they align outputs with this document.

1. Rename library size to `n_lib` in config labels and report text.
2. **Excess MSE and regime weights.**
   - Excess MSE becomes V(w) − V(w*) from the moments.
   - Regime weight becomes clip(Σcᵢuᵢ/Σcᵢ) with unclipped uᵢ.
   - K selection follows §M7.
3. **H1b and H1c.**
   - H1b: median instead of mean ε_s².
   - H1c: PLP-only verdict.
4. **H1e.** Bootstrap intervals for the Spearman correlations; N̂ reported only.
5. **Q-N.** Oracle-primary output with the reading table of §M11.
6. **H2b and H2f.**
   - H2b(ii) becomes the mean paired change from 10³ to 10⁴ at ρ = 1%.
   - Add H2f: the error correlation by N_lib and its 10³ → 10⁵ change.
   - Report the mean and median w* curves.
7. **H3 and H2d.**
   - H3a: log-rank only.
   - Remove H3b.
   - H3d: block-bootstrap interval on the MSE ratio.
   - H2d: remove part (ii).
8. **Verdict logic.** Pass / fail / inconclusive; remove "partially supported".
9. **Remove** A4f, Lorenz-96, transfer and the τ_d-halved variant.
10. **Validation and presets.**
    - V7: add to the gate.
    - Full preset: sweep states 1000.

Estimated effort: about one day, plus a smoke run and the unit tests.

# M16. Deferred to future work

- **Lean formalization** of P1–P3. It is optional and done after the fair results exist, with the student taking part.
- **A misspecified-model PLP arm.** It needs a model-error seed term (FW §10) and a proxy for it.
- **Robustness and transfer.**
  - Independent trajectory replicates at the core cell.
  - The check that bootstrap intervals are stable when thinning is doubled.
  - Cross-system transfer, including a higher-dimensional target.
- **Theory and estimators.**
  - A deployable N̂ with the correct estimand.
  - Break-even library size (FW eq. 5.1) and the K^(−2/p) regret rate (FW eq. 8.1).
