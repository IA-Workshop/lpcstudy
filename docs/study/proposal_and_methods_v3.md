# LPC Study: Proposal and Methods (v3)

Oct 10, 2026

## Summary

We ask whether four measurable local conditions of a chaotic system can decide, state by state, how much to trust an analog forecaster versus a physics-based forecaster, and for how long. The four local predictability conditions (LPCs) are recurrence, observability, instability and noise sensitivity.

**The two forecasters.** Both see only a noisy scalar observable of a three-dimensional chaotic system:

- **Context parroting (CP)** copies the future of the nearest past delay vector.
- **Physics-based latent-state propagation (PLP)** estimates the hidden state, then integrates the known equations.

We blend them with a weight w on CP.

**What is proved**:

- **P1:** the mean-squared-error-optimal weight is a closed-form function of the two forecasters' error moments, and blending can extend the forecast horizon by at most half an error-doubling time.
- **P2:** gives the fourth condition, noise sensitivity, a precise meaning. Retrieval of the nearest analog is stable while the noise is smaller than half the nearest-neighbor margin.

**What is tested.** Three pre-registered primary hypotheses, on Lorenz-63, Rössler and Chua's circuit:

- the optimal weight depends on the error seeds, not on instability;
- noise level and library size move the weight in the predicted direction;
- a few regimes defined by the four conditions lose almost nothing against the closed-form rule.

## 1. Background and motivation

Chaotic systems are deterministic, but sensitive dependence on initial conditions makes every forecast deteriorate (Lorenz 1963; Boffetta et al. 2002; Strogatz 2014). Forecasting them matters in fields from sensing to climate (Chen, Sun & Hao 2026; Zhu et al. 2025).

**Two forecaster families with opposite weaknesses.**

- **Data-based analog forecasters** find the past state most like the present one and copy what followed it (Lorenz 1969). Context parroting is the simplest form, and it is a strong baseline for chaotic forecasting (Zhang & Gilpin 2026; Gilpin 2023). Its accuracy depends on how close the nearest past analog is, so it improves with more data.
- **Physics-based forecasters** integrate known equations. Under partial observation they must first estimate the hidden state from noisy measurements. Their accuracy depends on how well that state can be reconstructed (Judd 2003; Wang et al. 2024).

**Hybrids combine the two, but not state by state.**

- **Fixed combinations.** Most hybrids correct a knowledge-based model with machine learning, or merge them with a fixed readout (Pathak et al. 2018; Wikner et al. 2020; Arcomano et al. 2022).
- **Dynamic weighting.** Recent work weights components by estimated confidence:
  - Heuer et al. (2026) mix a machine-learned and a conventional climate parameterization, column by column, according to a predicted error;
  - Feng et al. (2026) adapt a physics–data hybrid with an unscented Kalman filter in an engineering setting.

**Local predictability is a separate literature.** It measures, state by state, how fast errors grow and how well the state can be seen:

- local Lyapunov exponents (Ding & Li 2007; Kennel, Abarbanel & Sidorowich 1994);
- recurrence and local dimension (Faranda, Messori & Yiou 2017; Platzer et al. 2021);
- observability (Letellier, Aguirre & Maquet 2005; Parlitz et al. 2014);
- sensitivity to observation noise (Sviridova & Nakamura 2016).

Recurrence and instability have been used inside single forecasters (Guégan & Leroux 2009; Pérez-Zanón et al. 2022). To our knowledge, none of these conditions has been used to decide allocation between forecasters.

**Regimes.** Weather studies group states into regimes with different predictability (Vannitsem 2001; Matsueda & Palmer 2018). Reinforcement learning formalizes such grouping as state abstraction (Abel, Hershkowitz & Littman 2016).

**Gap and contribution.** Nothing connects the local conditions to the choice between an analog and a physics forecaster. This study:

1. Derives that choice in closed form from the forecasters' error moments, and proves when blending can and cannot help (P1).
2. Defines a fourth condition, the noise sensitivity of analog retrieval, and proves what controls it (P2).
3. Tests the predictions as controlled interventions on noise level and library size, on three chaotic systems.
4. Compares the theory-derived allocator with a learned allocator adapted from Heuer et al. (2026), and with a few-regime lookup.

Analog methods have been combined with data assimilation (Lguensat et al. 2017) and used to post-process numerical models (Delle Monache et al. 2013). We know of no prior *state-dependent* allocation between a delay-coordinate analog forecaster and a physics-based state propagator under partial observation.

## 2. Research questions and hypotheses

The study asks three research questions (abbreviated RQ), with three primary hypotheses (abbreviated H), nine secondary ones and one pre-registered estimate. Symbols are defined in §3–§5:

- w\* is the optimal weight on CP;
- ε\_s and δ are the CP and PLP initial errors (seeds);
- Λ̃ is the local growth exponent;
- N is noise sensitivity;
- N\_lib is library size;
- LT is one Lyapunov time;
- H\_ref = 1 LT.

**RQ1 (mechanism).** Do the four conditions predict each forecaster's error with the functional forms the theory gives, and is noise sensitivity distinct from the other three?

| ID | Hypothesis | Statistic | Pass if |
| --- | --- | --- | --- |
| H1a | The analog seed shrinks with library size as nearest-neighbor theory predicts | Fit of the median ε\_s² to b² N\_lib^(−2/d) + f² | interval of 1/d within ±25% of the independently estimated 1/d |
| H1b | PLP error = seed × amplifier | Slope of log r.m.s. PLP error on log(g\_H δ/√m) at H\_ref | in \[0.8, 1.2\] |
| H1c | Horizon law: horizon grows with log tolerance at rate 1/Λ | Median of Λ̄ × dT/d ln θ (PLP) | in \[0.8, 1.25\] |
| H1d | Deployable estimates of recurrence, observability and instability track their exact values | Spearman correlation, each | ≥ 0.7 |
| Q-N (estimate) | How much does N add to the other three? | Out-of-sample gain in R² (ΔR²) for predicting logit w\*, with exact (oracle) values | read by the table in §7 |

**RQ2 (decision).** Does allocation derived from the conditions beat simple alternatives, and do the two interventions move the weight as predicted?

| ID | Hypothesis | Statistic | Pass if |
| --- | --- | --- | --- |
| **H2a** | Separation: once the seeds are fixed, w\* does not depend on horizon or instability | (i) median range of w\* over 1, 2, 4 LT in the small-error regime; (ii) partial correlation of logit w\* with Λ̃ given both seeds | (i) interval below 0.1 and (ii) interval inside (−0.1, 0.1) |
| **H2b** | w\* rises with noise level, and with library size below saturation | (i) mean per-state rank correlation of w\* with ρ; (ii) mean paired change in w\* from N\_lib = 10³ to 10⁴ at ρ = 1% | both lower bounds > 0 |
| H2c | The closed-form allocator beats a global weight and the better single forecaster | Paired MSE differences at H\_ref | both upper bounds < 0 |
| H2d | The closed form is within 10% of a learned allocator | MSE ratio minus 1 at H\_ref | upper bound ≤ 0.10 |
| H2e | Noise matching: CP and PLP errors become correlated as the library grows | Median per-state change in error correlation, N\_lib 10³ → 10⁵ | lower bound > 0 at ρ = 1% and 2% |

**RQ3 (compression).** Can a few regimes defined by the four conditions carry the weight and the horizon?

| ID | Hypothesis | Statistic | Pass if |
| --- | --- | --- | --- |
| H3a | Regimes separate forecast horizons | Holm-adjusted log-rank tests between consecutive regimes | all p < 0.01 |
| H3b | Instability sets the horizon, not the weight | Importances in a weight tree and a horizon tree | weight tree: Λ̃ < 0.2; horizon tree: Λ̃ highest |
| **H3c** | A few regimes cost almost nothing against the closed form | MSE ratio, regimes / closed form, at H\_ref | upper bound ≤ 1.05 |

The hybrid's horizon gain over the better forecaster is reported against the P1 bound, without a pass/fail bar.

H2e was added after the pilot showed the effect. It is tested here on fresh random seeds.

## 3. Mathematical framework and theorems

**Seeds and an amplifier.** To first order, each forecaster's error at horizon H is an initial error (its *seed*) multiplied by the same amplifier (Taylor's theorem):

- the CP seed is the latent mismatch of the chosen analog, with r.m.s. size ε\_s;
- the PLP seed is the state-estimation error, with r.m.s. size δ;
- the amplifier g\_H is the local sensitivity of the observable after H steps;
- its growth rate is Λ̄, and Λ̃ is Λ̄ in units of the largest Lyapunov exponent.

Recurrence and observability set the seeds; instability sets the amplifier.

&#91;embedded content: framework · four conditions → seeds and amplifier → weight and horizon → regimes\]

Recurrence and observability set the two seeds, and instability sets the shared amplifier. Noise sensitivity enters through the error cross-moment. If separation holds, the amplifier cancels from the weight.

### Theorem P1 (optimal weight and the limit on blending)

Fix a state and a horizon. Let e\_C and e\_P be the CP and PLP errors over observation-noise draws, with second moments E\_C = E\[e\_C²\], E\_P = E\[e\_P²\] and C = E\[e\_C e\_P\]. The hybrid's mean squared error is a quadratic in the weight:

```latex
V(w) = \mathbb{E}\big[(w\,e_C + (1-w)\,e_P)^2\big] = c\,(w-u)^2 + V(u), \qquad c = E_C + E_P - 2C, \quad u = \frac{E_P - C}{c}
```

- **(a)** CP copies a noisy future value. Its error therefore contains a term ξ with E\[ξ²\] = ρ²/k (k = number of analogs averaged), orthogonal to e\_P and to e\_C − ξ. Then c ≥ ρ²/k > 0, V is strictly convex, and the best admissible weight is w\* = clip to \[0, 1\] of u.
- **(b)** u itself lies in \[0, 1\] exactly when C ≤ min(E\_C, E\_P).
- **(c)** If C ≥ 0, then no weight in \[0, 1\] does better than half the better single forecaster: min V ≥ ½ min(E\_C, E\_P).
- **(d)** Suppose (c) holds at every horizon and the better forecaster's r.m.s. error grows as r₀e^(ΛH). Then the optimal hybrid's characteristic horizon exceeds that forecaster's by at most ln 2/(2Λ): half an error-doubling time.
- **(e)** (c) fails without C ≥ 0. With E\_C = E\_P = 1 and C = −1, min V = 0.

*Proof sketch.*

- (a) and (b): expand the square and complete it in w.
- (c): take E\_C ≤ E\_P. If C ≥ E\_C, the best weight is 1 and V = E\_C. Otherwise V(u) = (E\_C E\_P − C²)/c, and 2V(u) ≥ E\_C reduces to E\_C(E\_P − E\_C) + 2C(E\_C − C) ≥ 0, a sum of nonnegative terms.
- (d): a factor ½ in variance is a factor 1/√2 in r.m.s. error. Exponential growth recovers it in ln 2/(2Λ).

**Separation, as a remark.** Suppose the seeds' covariances are proportional to one matrix, and the seeds are uncorrelated. Then the amplifier cancels from u, and w\* = δ²/(ε\_s² + δ²), independent of horizon and instability. The closed-form allocator approximates this. H2a tests whether real attractors are close enough to that assumption.

### Theorem P2 (stability of analog retrieval: the fourth condition)

Let X₁, …, X\_n be library delay vectors and x a clean query. Let r₁ < r₂ be the nearest and second-nearest distances, with margin Δ = r₂ − r₁. Add observation noise η with E‖η‖² = Dρ², where D is the embedding dimension.

- **(a)** If ‖η‖ < Δ/2, the nearest analog does not change.
- **(b)** Pr(retrieval changes) ≤ Pr(‖η‖ ≥ Δ/2) ≤ 4Dρ²/Δ².
- **(c)** Define N as the r.m.s. displacement of the retrieved analog's delay vector under noise, per coordinate, in noise units. Then:

```latex
N^2 \le \frac{4}{\rho^2 D}\,\mathbb{E}\Big[(r_1 + \lVert\eta\rVert)^2\,\mathbf{1}\{\lVert\eta\rVert \ge \Delta/2\}\Big]
```

*Proof sketch.*

- (a): noise moves every distance by at most ‖η‖ (triangle inequality).
- (b): (a) plus Markov's inequality on ‖η‖².
- (c): suppose retrieval switches from X₁ to X\_j. Both lie within r₁ + ‖η‖ of the noisy query, so ‖X\_j − X₁‖ ≤ 2(r₁ + ‖η‖). The spread about the mean is at most the spread about X₁.

**Why this matters.**

- N is controlled by the margin and the nearest distance in noise units, Δ/ρ and r₁/ρ.
- The margin is a different order statistic of the library from the recurrence distance r₁, so N can carry state-level information the other three conditions do not.
- For PLP, the noise effect is already contained in observability, so the fourth condition is defined on the analog side.
- The study does not assume N is redundant: it estimates how much N adds (Q-N).

### Theorem P3 (optional: the cost of regimes)

In a regime, the total error Σᵢ Vᵢ(w) is minimized by the curvature-weighted mean of the unclipped optima, clipped to \[0, 1\].

A rule that sees only a profile F cannot beat the rule clip(E\[c u | F\] / E\[c | F\]). This sets a floor on the excess error of every regime map, for every number of regimes. The floor vanishes when the optimum is a function of F, and is generally positive otherwise.

**Cited, not proved here:**

- the first-order error decomposition;
- the state-estimation error ρ²(JᵀJ)⁻¹ and its Cramér–Rao optimality;
- the delay-distance bound on the analog seed;
- nearest-neighbor scaling of the analog seed;
- the horizon law T ≈ Λ̄⁻¹ ln(θσ\_x√m/e₀);
- the optimal combination of forecasts (Bates & Granger 1969).

## 4. Methods: systems, data and forecasters

All experiments are simulations of three chaotic systems with exact models, so true states and every condition are known.

| System | Parameters | Observable | λ\_max (per time unit) | RK4 step |
| --- | --- | --- | --- | --- |
| Lorenz-63 | σ = 10, r = 28, b = 8/3 | x | 0.905 | ≤ 0.01 |
| Rössler | a = b = 0.2, c = 5.7 | x | 0.0719 | ≤ 0.04 |
| Chua (piecewise-linear diode) | α = 15.6, β = 28, m₀ = −1.143, m₁ = −0.714 | x | 0.431 | ≤ 0.005 |

**Integration and time scale.**

- λ\_max is computed with Benettin's method (Benettin et al. 1980).
- The observation interval is set so that one Lyapunov time (LT = 1/λ\_max) is 30 steps.
- Truth and the physics model use the same fourth-order Runge–Kutta integrator. Halving the step must change the observable by less than 10⁻³ σ\_x over 1 LT.

**Trajectories.** Each system gets three trajectories, after a 100-LT burn-in:

- **statistics:** normalization, mean and covariance;
- **main:** library and evaluation states;
- **separate:** used only to train the state estimator's first stage.

Hidden states are whitened by the attractor's covariance, so all errors are dimensionless and comparable across systems.

**Observation and embedding.**

- The observable is normalized to unit variance.
- Observations are x\_t = h(s\_t) + η\_t, with η\_t independent Gaussian noise of standard deviation ρ ∈ {0.5, 1, 2, 5}% of σ\_x.
- The same random draws are rescaled across noise levels and library sizes (common random numbers), so differences reflect the intervention.
- Delay vectors are X\_t = (x\_t, x\_{t−τ}, …, x\_{t−6τ}), with D = 7 and τ at the first minimum of the average mutual information (Fraser & Swinney 1986). τ is capped so the window spans at most 1 LT; the result is τ = 5, 3, 5 steps.

**CP (context parroting).**

- The library is a noisy trajectory segment of N\_lib admissible delay vectors, each with full history and 8 LT of future.
- CP finds the nearest library vector by exact Euclidean search and copies its noisy future.
- The recurrence distance R is the distance to that analog.

**PLP (physics-based latent-state propagation).** The estimator ψ maps X\_t to the hidden state in two stages:

1. A small neural network (two hidden layers) gives an initial guess. It is trained on the separate trajectory with fresh noise at the cell's ρ.
2. Fifteen Levenberg–Marquardt iterations then fit the known model to the delay window. This is the maximum-likelihood estimate, so it reaches the Cramér–Rao floor ρν to first order. Here ν² = tr\[(JᵀJ)⁻¹\], with J the delay-map Jacobian.

The model is then integrated forward. About 2% of estimates (Lorenz-63, ρ = 1%) converge to a wrong basin. They are kept, because this is a real property of nonlinear estimation (Judd 2003).

**Hybrid.** x̂ = w · x̂\_CP + (1 − w) · x̂\_PLP, with w ∈ \[0, 1\]. Errors are measured against the noise-free truth and clipped at 10 σ\_x. True states are never forecaster inputs.

**Data partition.** The main trajectory is laid out as library | construction | calibration | test. The segments are separated by gaps longer than one Theiler window (1 LT; Theiler 1986), plus the delay and forecast windows, so no window crosses a boundary.

| Set | Use | States |
| --- | --- | --- |
| Construction | fit proxies, the global weight, the learned allocator, the regime trees | 2000 |
| Calibration | choose the number of regimes; regime weights and horizons | 1000 |
| Test | all reported results | 1000 |
| Sweep cells | noise and library sweeps | 1000 |

Evaluation states are at least 1 LT apart. Each state gets M = 200 noise draws for exact (oracle) moments and 4 draws for deployable evaluation.

## 5. Per-state quantities, the four-condition profile, and allocation rules

Each condition is measured twice:

- **exactly (oracle)**, using the true state, to test the mechanism;
- **deployably**, from observations, the model and ρ only, to test allocation fairly.

**Oracle quantities** use M independent noise draws per state.

| Quantity | Definition |
| --- | --- |
| Analog seed ε\_s | r.m.s. latent mismatch of the analogs retrieved across draws |
| Estimation seed δ | r.m.s. error of ψ across draws |
| Observability ν | ν² = tr\[(JᵀJ)⁻¹\], computed by a forward formula that avoids inverting an ill-conditioned matrix |
| Amplifier g\_H, growth Λ̄ | g\_H = sensitivity of the observable after H steps; Λ̄ = slope of ln g\_H over 1 LT; Λ̃ = 30Λ̄ |
| Noise sensitivity N | r.m.s. displacement of the retrieved analog's delay vector across draws, per coordinate, in units of ρ (P2) |
| Moments E\_C, E\_P, C | second moments of the two errors at each horizon |
| Optimal weight w\* | clip to \[0, 1\] of (E\_P − C)/(E\_C + E\_P − 2C) (P1) |
| Characteristic horizon | first H at which the r.m.s. error, including verification noise, exceeds θ σ\_x |
| Local dimension d | Levina–Bickel estimator (Levina & Bickel 2005) on library states |

**Deployable proxies.**

| Proxy | Definition |
| --- | --- |
| ν̂ | ν at the estimate ŝ, capped at its 99th percentile |
| ε̂ | ε̂² = a(R ν̂)² + b(ρ ν̂)²: the recurrence distance mapped into state space through local observability |
| δ̂ | δ̂² = a′(ρ ν̂)² + b′ρ² |
| Λ̂ | growth rate of the model started at ŝ |
| N̂ | spread of retrieved analogs under 16 synthetic perturbations of the observed query |

The coefficients a, b, a′, b′ are fitted on construction states by robust least squares on a log scale.

**The profile.** F̂ = (ln ε̂/ρ, ln δ̂/ρ, Λ̃̂, ln(N̂ + 0.01)): recurrence, observability, instability and noise sensitivity, all dimensionless. The oracle profile uses the exact values.

**Allocation rules.** Each rule outputs a weight per state and horizon.

| Rule | Weight | Inputs | Fitted on |
| --- | --- | --- | --- |
| A0 | CP alone, w = 1 | — | — |
| A1 | PLP alone, w = 0 | — | — |
| A2 | One global weight per horizon | — | construction |
| A3 | Learned allocator, adapted from Heuer et al. (2026): a network predicts both forecasters' errors from X\_t; w = ê²\_PLP / (ê²\_CP + ê²\_PLP) | X\_t | construction |
| A4 | Closed form: w = δ̂² / (ε̂² + δ̂²) | R, ν̂, ρ | construction (4 coefficients) |
| A5 | Regime lookup: a regression tree on F̂ with K leaves; each leaf gets the P3 regime weight and a Kaplan–Meier horizon | F̂ | tree: construction; weights: calibration |
| A4o | A4 with exact seeds (reference) | ε\_s, δ | — |
| A\* | State-optimal w\* (reference) | true state | — |

K is the smallest value in {2, 3, 4, 5, 6, 8} whose calibration error is within 5% of the best value in that set. Excess error is computed exactly from the moments, as V(w) − V(w\*).

## 6. Experiments

Seven experiments, all run on each of the three systems. Each experiment either tests a numerical prerequisite or feeds named hypotheses.

| # | Experiment | Design | Feeds |
| --- | --- | --- | --- |
| E0 | Validation gate | Checks V1–V7 below; a failure marks that system's results provisional | all |
| E1 | Noise sweep | ρ ∈ {0.5, 1, 2, 5}% at N\_lib = 10⁴; ψ retrained at each ρ | V7, H2b(i) |
| E2 | Library sweep | N\_lib ∈ {10³, 10^3.5, 10⁴, 10^4.5, 10⁵} at ρ ∈ {1, 2}%; nested libraries | H1a, H2b(ii), H2e |
| E3 | Mechanism at the core cell | ρ = 1%, N\_lib = 10⁴, horizons 1–240 steps; seed × amplifier fit; horizons over θ; proxy fidelity; Q-N with gradient-boosted regressors | H1b–H1d, Q-N |
| E4 | Allocation and separation | All rules on the core test split; MSE at 0.25, 0.5, 1, 2, 4 LT; w\*(H) per state; horizon gain | H2a, H2c, H2d |
| E5 | Regimes | A5 for K ∈ {2, 3, 4, 5, 6, 8, 12, 16}; excess error against K; log-rank tests; tree importances | H3a–H3c |
| E6 | Robustness (reported only; Lorenz-63 and Rössler) | D ∈ {5, 10}; 5 averaged analogs; model parameters perturbed ±5% and ±10%; finite-amplitude growth in place of Λ̄ | — |

**Validation checks (****R****u****n**** ****a****t**** ****E0).**

- **V1.** Jacobians and amplifiers agree with finite differences: relative error < 10⁻⁴.
- **V2.** At ρ = 10⁻⁴, least squares attains the Cramér–Rao value ρ²ν²: ratio in \[0.8, 1.2\].
- **V3.** CP's valid prediction time is reported, for comparison with Zhang & Gilpin (2026).
- **V4.** w\* is converged at M = 200 noise draws: median bootstrap half-width ≤ 0.05 (checked at M = 50, 200, 800).
- **V5.** Kaplan–Meier matches exact censored survival: maximum deviation < 0.01.
- **V6.** Halving the RK4 step changes the observable by < 10⁻³ σ\_x over 1 LT.
- **V7.** The estimator is efficient: median δ/(ρν), and the median slope of ln δ on ln ρ, both in \[0.9, 1.1\].

**Horizons.** The realized horizon is the first step at which the error against the *noisy* verifying observation exceeds θ σ\_x. It is right-censored at 8 LT.

- θ ∈ {0.1, 0.2, 0.3, 0.5}, keeping only θ ≥ 3√2ρ so that noise alone cannot cross it; θ = 0.2 is primary.
- Censored horizons are summarized by the Kaplan–Meier median and restricted mean (Kaplan & Meier 1958), never by plain averages.

## 7. Analysis plan and decision rules

Every criterion in §2 is decided by an interval, and the rules below are fixed before the confirmatory run.

**Intervals.**

- Moving-block bootstrap over test states in time order (Künsch 1989): blocks of 5 states, 2000 resamples.
- The three primary hypotheses (H2a, H2b, H3c) use level 1 − 0.05/3 (Bonferroni). Everything else uses 95%.

**Verdict per system.**

- **pass:** the interval lies inside the band, or entirely on the predicted side of the bound;
- **fail:** the interval lies entirely outside;
- **inconclusive:** otherwise.

A criterion with several parts passes only if every part passes, and fails if any part fails.

**Overall verdict.**

- **supported:** pass on all three systems;
- **not supported:** fail on at least one system;
- **inconclusive:** otherwise.

Requiring every system to pass is an intersection–union test, so it needs no further multiplicity correction.

**Reading Q-N** (oracle ΔR² for logit w\* at 1 LT; the deployable version is secondary):

| Interval for ΔR² | Reading |
| --- | --- |
| upper bound < 0.05, lower bound ≤ 0 | N reduces to the other three, at this precision |
| lower bound > 0, upper bound < 0.05 | N is distinct but small |
| lower bound > 0, upper bound ≥ 0.05 | N carries substantial additional information |
| otherwise | undetermined |

**Pre-registered readings of failures.**

- **H2a fails.** Instability enters the weight through anisotropic seeds. The size of the departure measures how far real attractors are from the separation assumption.
- **H2c fails but A4o beats A2.** The theory is right, and the deployable seed estimates limit it.
- **H3c holds while excess error is flat in K.** This is the P3 floor.

**Precision** (projected from the pilot to the full sample sizes):

- Most criteria can be decided in at least one direction.
- H2a's second part can be refuted but essentially cannot pass: that would need a partial correlation within about 0.01 of zero.
- The Q-N interval is about ±0.04, so all four readings are reachable.
- H2b(ii) and H2e are expected to be decided (pilot estimates 0.05–0.08 and 0.21–0.36, projected half-widths 0.03 and 0.04).

All outcomes are reported, including failures.

## 8. Scope, limitations and future work

The study is deliberately narrow: three low-dimensional systems, an exact physics model, one observable, and two proved theorems.

**Known limitations, stated before the confirmatory run.**

- **The deployable closed form A4 depends almost only on recurrence distance in noise units.** In the pilot the fitted proxies made ν̂ cancel (A4 ≈ 1/(1 + 0.26(R/ρ)²)). Observability reaches deployable allocation mainly through A5 and A3.
- **With an exact model, PLP usually wins after 1 LT.** In the pilot, median w\* at 1 LT was 0.05–0.09, and 22–36% of states had w\* = 0. CP's value lies at short horizons and in wrong-basin estimation events.
- **Deployable features carry little of the information in the exact ones.** Out-of-sample R² for logit w\* was −0.02 to 0.05 (deployable) against 0.25–0.49 (exact). Deployable allocation results are limited by the proxies, not the theory.
- **N̂ measures retrieval sensitivity at the observed (noisy) query, not at the true one.** It is therefore reported, not tested.
- **The seed × amplifier test (H1b) assumes isotropic seeds,** so it is applied to PLP only. Analog seeds lie along the attractor.
- **Same attractors, fresh seeds.** The confirmatory run uses new noise, libraries and trajectories on the same three systems. That adds precision and guards against tuning to the pilot; it is not new systems.

**Future work (not in this study):**

- a misspecified physics model, which needs its own error theory and proxy;
- transfer to a higher-dimensional system;
- independent trajectory replicates;
- a deployable N̂ that estimates N without bias;
- the break-even library size and the regret-versus-K scaling law;
- machine-checked (Lean) versions of P1 and P2, with the student taking part.

## 9. Timeline, roles and AI use

The proposal and methods are due on Oct 30, 2026.

&#91;embedded content: plan to 30 October · 5 phases, 1 deadline\]

**After 30 October** (dates to be set):

1. Update the code to match this document (about one day).
2. Freeze the pre-registration: a dated copy of this document, the code commit and the configuration.
3. Run the full study on fresh seeds on the mentor's GPU workstation.
4. Analyze the results, and write the paper and the fair materials.

**Roles** (to be confirmed by the student and mentor):

| Who | Responsible for |
| --- | --- |
| Deem (primary author) | Research questions, proposal text, proofs of P1 and P2 by hand, interpretation of results, presentation |
| Brian | Review of design and proofs; running the full computational study; pre-existing project tools |
| AI assistant (Claude) | Drafting help, literature and reference checks, the v1 research code, design audits |

**AI-use statement**: An AI assistant (Claude, Anthropic) was used to:

- check references;
- draft and audit parts of the methods;
- implement and test the simulation code.

The author chose the research questions, wrote the proposal in their own words, and proved the theorems presented. Every AI-generated component was reviewed by the author.

## References

The list is trimmed to the works this document cites. Metadata follows the project's reference audit (5 October 2026). Entries marked \[U\] were not independently verified; for entries without a title, take the title and full author list from the proposal's original reference list.

- Abel, D., Hershkowitz, D. E., & Littman, M. L. (2016). Near optimal behavior via approximate state abstraction. *ICML 2016*.
- Arcomano, T. et al. (2022). *J. Adv. Model. Earth Syst.* 14.
- Bates, J. M., & Granger, C. W. J. (1969). The combination of forecasts. *Oper. Res. Q.* 20(4), 451–468. doi:10.1057/jors.1969.103
- Benettin, G., Galgani, L., Giorgilli, A., & Strelcyn, J.-M. (1980). Lyapunov characteristic exponents for smooth dynamical systems and for Hamiltonian systems; a method for computing all of them. Parts 1 and 2. *Meccanica* 15, 9–20 and 21–30.
- Boffetta, G., Cencini, M., Falcioni, M., & Vulpiani, A. (2002). Predictability: a way to characterize complexity. *Phys. Rep.* 356, 367–474. doi:10.1016/S0370-1573(01)00025-4
- Chen, Sun & Hao (2026). *IEEE Sens. J.* 26(10).
- Delle Monache, L. et al. (2013). Probabilistic weather prediction with an analog ensemble. *Mon. Weather Rev.* 141, 3498–3516. doi:10.1175/MWR-D-12-00281.1
- Ding, R., & Li, J. (2007). *Phys. Lett. A* 364.
- Faranda, D., Messori, G., & Yiou, P. (2017). *Sci. Rep.* 7.
- Feng et al. (2026). *Adv. Eng. Inform.* 72.
- Fraser, A. M., & Swinney, H. L. (1986). Independent coordinates for strange attractors from mutual information. *Phys. Rev. A* 33, 1134–1140. doi:10.1103/PhysRevA.33.1134
- Gilpin, W. (2023). *Phys. Rev. Res.* 5, 043252.
- Guégan, D., & Leroux, J. (2009). *Chaos Solitons Fractals* 41(5).
- Heuer et al. (2026). Beyond the training data: confidence-guided mixing of parameterizations in a hybrid AI-climate model. *J. Adv. Model. Earth Syst.* 18(5). arXiv:2510.08107
- Judd, K. (2003). *Physica D* 183.
- Kaplan, E. L., & Meier, P. (1958). Nonparametric estimation from incomplete observations. *J. Am. Stat. Assoc.* 53, 457–481. \[U\]
- Kennel, M. B., Abarbanel, H. D. I., & Sidorowich, J. J. (1994). Prediction errors and local Lyapunov exponents. arXiv:chao-dyn/9403001 (preprint; not a *Phys. Rev. Lett.* article).
- Künsch, H. R. (1989). The jackknife and the bootstrap for general stationary observations. *Ann. Stat.* 17(3), 1217–1241. \[U\]
- Letellier, C., Aguirre, L. A., & Maquet, J. (2005). *Phys. Rev. E* 71.
- Levina, E., & Bickel, P. J. (2005). Maximum likelihood estimation of intrinsic dimension. *NeurIPS 17*. \[U\]
- Lguensat, R. et al. (2017). *Mon. Weather Rev.* 145.
- Lorenz, E. N. (1963). Deterministic nonperiodic flow. *J. Atmos. Sci.* 20, 130–141. \[U\]
- Lorenz, E. N. (1969). Atmospheric predictability as revealed by naturally occurring analogues. *J. Atmos. Sci.* 26, 636–646.
- Matsueda, M., & Palmer, T. N. (2018). *Q. J. R. Meteorol. Soc.* 144.
- Parlitz, U. et al. (2014). *Chaos* 24.
- Pathak, J. et al. (2018). Hybrid forecasting of chaotic processes: using machine learning in conjunction with a knowledge-based model. *Chaos* 28.
- Pérez-Zanón, N. et al. (2022). *Geosci. Model Dev.* 15.
- Platzer, P. et al. (2021). *J. Atmos. Sci.* 78(7).
- Strogatz, S. H. (2014). *Nonlinear Dynamics and Chaos*, 2nd ed. Westview Press.
- Sviridova, N., & Nakamura, K. (2016). *Chaos* 26.
- Theiler, J. (1986). Spurious dimension from correlation algorithms applied to limited time-series data. *Phys. Rev. A* 34, 2427–2432. doi:10.1103/PhysRevA.34.2427
- Vannitsem, S. (2001). *Tellus A* 53(1). doi:10.3402/tellusa.v53i1.12180
- Wang et al. (2024). *Chaos Solitons Fractals* 186.
- Wikner, A. et al. (2020). *Chaos* 30.
- Zhang, Y., & Gilpin, W. (2026). Context parroting: a simple but tough-to-beat baseline for foundation models in scientific machine learning. *ICLR 2026*. arXiv:2505.11349
- Zhu et al. (2025). *Nat. Commun.* 16, 7736.
