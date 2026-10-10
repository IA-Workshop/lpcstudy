---
title: "Theorem Program for the LPC Study"
subtitle: "What can be proved, traditionally and in Lean 4, and how it connects to the experiments"
date: "6 October 2026"
---

# Status (10 October 2026)

This document is kept as a reference. Under decision D4, Lean formalization is deferred until after the fair results exist. The student proves three results by hand; they are stated in Methods v2 §M9:

- **P1** = L5 + L7;
- **P2** = L11(b);
- **P3** = L10(i)–(iii) plus a measurability floor.

**Errata.**

- **L3** proves *orthogonal* (not affine) invariance of the whitened ν.
- **L10's flat-regret explanation.** The floor is from any failure of w* to be a function of the profile, not from proxy noise alone. A4o, with exact seeds, has excess 9–46%. The general statement is P3(b).
- **What L11 implies for H1f** is superseded by the Q-N estimate (Methods v2 §M11).
- **The theorem-to-experiment mapping in §4 is overstated.**
  - L3 is certified by a unit test, not an experiment.
  - L5 defines w* and is not tested.
  - L9 is not computed.
  - L8′ is vacuous on Lorenz-63.

  Use the mapping in Methods v2 §M9.
- **Notation.** In this document N is the noise sensitivity, and library size is written N_lib (L12's "N^(−1/d)" means N_lib).

# 0. Purpose and grading

A Mathematics judge will ask *what is proved*. This document sorts every mathematical claim in the study into three grades:

- **[T] Theorem.** Provable from stated hypotheses, with a traditional proof given or sketched. Each [T] item has a Lean plan.
- **[C] Conditional or asymptotic.** Provable traditionally only under idealized hypotheses (asymptotics, Oseledets theory, nearest-neighbor limits). It is not worth mechanizing at the current mathlib pin; it is stated as a theorem with the hypotheses explicit, and the experiments test whether those hypotheses hold.
- **[E] Empirical.** A property of the data-generating measure with no closed form (sufficiency, regime transfer, tree partitions). It is tested, never claimed as a theorem.

The experiments (H1a–H3d, T1) then become **tests of whether the hypotheses of the [T] and [C] results hold for real chaotic systems**. That is the right framing for a Mathematics entry: theorems with stated domains of validity, plus falsification experiments that map where the domains end.

## Lean context

The project already has a Lean 4 library, `Disquiet` (Lean 4.33.1, mathlib v4.33.1 pinned). It contains about 90 proved theorems with no `sorry`, standard axioms only, and CI gates on the §8.2 table.

Several of its results are directly reusable here:

| Existing artifact | Reused for |
|---|---|
| `wstar`, `combVar`, `bates_granger`, `weight_mem_unit_interval_iff`, `boundary_optimal_left/right` | optimal-weight algebra |
| `OptimalWeightL2`, `sq_diff_noisy` | curvature lower bound from copied noise |
| `wstar_antitone_library_noise` | copied-noise tilt toward PLP |
| `taylor_remainder_sq`, `linearization_remainder` | seed × amplifier with quadratic remainder |
| `latent_sep_of_noisy_mismatch` | delay-distance → latent-mismatch bound |
| `two_trajectory_bound` (Grönwall) | a rigorous lower bound on the horizon |

New work goes in a new namespace, `Disquiet/LPC/`, under the same constitution: statements are law, every narrowing is disclosed in §8.2, and no `sorry` is merged.

The Lean statements below are **uncompiled sketches** for the Lean agent's staging step. Mathlib lemma names must be checked against the v4.33.1 pin.

## Notation

| Symbol | Meaning |
|---|---|
| s | latent state |
| ξ | seed: a = analog state, ŝ = estimate |
| Γ_H | amplifier: the row vector ∇h(Φ^H s) DΦ^H(s) |
| g_H | ‖Γ_H‖ |
| J | delay-map Jacobian (D × m) |
| ν² | tr[(JᵀJ)⁻¹] |
| ρ | noise level |
| V_a, V_s, V_K | amplified seed variances and their cross term |
| c | curvature: V_a + ρ²/k + V_s − 2V_K |
| w* | optimal weight |
| N | analog-retrieval noise sensitivity (the fourth LPC) |
| Δ | nearest-neighbor margin d₂ − d₁ |

# 1. Inventory

| # | Result | Grade | Traditional proof | Lean status | Effort |
|---|---|---|---|---|---|
| L1 | Seed × amplifier decomposition with explicit quadratic remainder | T | Taylor | **reuse** `taylor_remainder_sq` + new wrapper | small |
| L2 | Noise amplification and Gauss–Markov optimality of the linearized estimator | T | linear algebra | new | medium |
| L3 | Forward observability formula and affine invariance of ν | T | matrix algebra | new | small |
| L4 | Delay-space distance bounds latent mismatch (FW Lemma 1) | T | Taylor + σ_min | **reuse** `latent_sep_of_noisy_mismatch` + local version | medium |
| L5 | Optimal weight, clipping, strict convexity from copied noise | T | quadratic | **reuse** `wstar`, `combVar`, `sq_diff_noisy` | small |
| L6 | Separation: scale invariance of w* under proportional covariances; limit as amplification grows | T | algebra / limits | new (easy) | small |
| L6′ | Long-horizon limit via Oseledets alignment | C | Oseledets | out of scope (no Oseledets theorem in mathlib) | — |
| L7 | Hybrid horizon-gain bound ½ min(V_a, V_s) and ln2/(2Λ) | T | inequality + log | new | small |
| L8 | Horizon law: exact form, robust bracket, monotonicity, discrete first passage | T | log/exp | new | small |
| L8′ | Rigorous (nonlinear) horizon lower bound from Grönwall | T | Grönwall | **reuse** `two_trajectory_bound` | small |
| L9 | Geometric ≤ arithmetic growth exponent (NLLE vs Λ), with equality case | T | Jensen / AM-GM | new | small–medium |
| L10 | Abstraction regret identity, optimal regime weight, error bound | T | quadratic | new | small |
| L10′ | Quantization rate K^(−2/p) for Lipschitz w* on a grid partition | T | covering | new | medium |
| L11 | **Fourth LPC: reducibility on the PLP side, margin control on the CP side** | T | new (§3) | new | medium |
| L12 | Analog seed ~ N^(−1/d) with a noise floor | C | nearest-neighbor asymptotics | out of scope | — |
| L13 | Kaplan–Meier, log-rank properties | cite | standard | not needed | — |
| E1 | Predictive sufficiency of the profile; transfer of regimes; tree partitions approaching L10′ | E | — | — (tested: H1f, H3, T1) | — |

**Priority for the entry.** L5–L8, L10 and L11 carry the paper's argument. L2 and L4 make the observability coordinate rigorous. L11 is the most original result: it gives the fourth LPC a precise mathematical meaning and says *when* it can and cannot be rolled into the other three.

# 2. Statements, proofs and Lean plans

## L1. Seed × amplifier decomposition [T]

**Statement.**

- Let F = h̃ ∘ Φ^H be twice differentiable on a convex set containing s and s + ξ, with ‖D²F‖ ≤ M₂.
- Then |F(s+ξ) − F(s) − Γ_H ξ| ≤ (M₂/2)‖ξ‖².
- Hence e_CP = Γ_H(a − s) + η_copied + r_a and e_PLP = Γ_H(ŝ − s) + r_ŝ, with |r| ≤ (M₂/2)‖seed‖².

**Proof.** Taylor's theorem with Lagrange remainder along the segment.

**Lean.** This is a direct instance of `taylor_remainder_sq` (already proved, with the sharp constant M₂/2). The wrapper names the two forecasters' errors.

**What the experiment adds.** H1c tests the slope against log(g_H·seed). The pilot shows that PLP sits near the linear regime (slopes 0.67–1.01). CP is superlinear (1.2–1.6): the analog seed is often outside the region where the remainder is small. That is the L1 hypothesis failing, not the theorem.

## L2. Noise amplification and Gauss–Markov optimality [T]

**Statement.** Let J ∈ ℝ^(D×m) have full column rank and J⁺ = (JᵀJ)⁻¹Jᵀ.

- (a) J⁺J = I.
- (b) J⁺J⁺ᵀ = (JᵀJ)⁻¹, and tr(J⁺J⁺ᵀ) = Σⱼ σⱼ⁻².
- (c) **Gauss–Markov.** For every left inverse L (LJ = I), LLᵀ ⪰ (JᵀJ)⁻¹, with equality iff L = J⁺.
- (d) If η has mean 0 and covariance ρ²I, then Cov(Lη) = ρ²LLᵀ. Hence the linearized least-squares estimator has error covariance ρ²(JᵀJ)⁻¹, and no linear unbiased estimator does better.

**Proof of (c).** Write L = J⁺ + Z. Then ZJ = 0, so ZJ⁺ᵀ = ZJ(JᵀJ)⁻¹ = 0. Therefore LLᵀ = J⁺J⁺ᵀ + ZZᵀ, and ZZᵀ ⪰ 0.

**Lean.**

- (a)–(c) are matrix algebra. The relevant mathlib pieces are `Matrix.nonsing_inv_mul`, `Matrix.transpose_nonsing_inv`, and `Matrix.posSemidef_self_mul_conjTranspose` for ZZᵀ ⪰ 0.
- The trace identity in (b) uses `Matrix.IsHermitian.eigenvalues` and the trace-equals-sum-of-eigenvalues lemma, applied to JᵀJ and its inverse (medium).
- (d) is stated with an abstract covariance matrix (a moments model, like `OptimalWeight.lean`). No measure theory is needed.

**Scope.** The full Cramér–Rao bound for *nonlinear, biased* estimators is out of scope, consistent with the existing exclusion of Theorem 5(ii). The study's estimator is biased (Bayesian initial guess plus refinement). The empirical efficiency δ/(ρν) = 1.00 ± 0.01 (H1a) is the evidence that it behaves like the linearized ML estimator of L2.

```lean
/-- L2(c), Gauss–Markov: every left inverse has covariance factor ⪰ (JᵀJ)⁻¹. -/
theorem gauss_markov_left_inverse {m D : ℕ}
    (J : Matrix (Fin D) (Fin m) ℝ) (L : Matrix (Fin m) (Fin D) ℝ)
    (hJ : IsUnit (Jᵀ * J).det) (hL : L * J = 1) :
    (L * Lᵀ - (Jᵀ * J)⁻¹).PosSemidef
-- proof: set Z := L - (Jᵀ*J)⁻¹ * Jᵀ; Z * J = 0; L*Lᵀ - (JᵀJ)⁻¹ = Z * Zᵀ;
--        Matrix.posSemidef_self_mul_conjTranspose (conjTranspose = transpose over ℝ).
```

## L3. Forward observability formula [T]

**Statement.**

- If J = AQ⁻¹ with Q invertible and AᵀA invertible, then (JᵀJ)⁻¹ = Q(AᵀA)⁻¹Qᵀ.
- For any invertible W, the whitened quantity tr[W(JᵀJ)⁻¹Wᵀ] is unchanged under J ↦ JU⁻¹, W ↦ UW with U orthogonal.

**Proof.** Inverse of a product, and invariance of the trace under orthogonal conjugation.

**Lean.** Small: `Matrix.mul_inv_rev` and trace cyclicity. This certifies the formula the code uses to compute ν without inverting the ill-conditioned Q, which is also covered by a unit test.

## L4. Delay-space distance bounds latent mismatch (FW Lemma 1) [T]

**Statement.**

- Hypotheses: ‖J(s)v‖ ≥ σ_m‖v‖ for all v; ‖D²G‖ ≤ L₂ on the segment from s to a; and ‖a − s‖ ≤ σ_m/L₂.
- Conclusion: ‖a − s‖ ≤ 2(R + ‖η_t − η_a‖)/σ_m.

**Proof.** Taylor expansion of G about s, then absorb the quadratic term.

**Lean.**

- The global bi-Lipschitz version is already proved: `latent_sep_of_noisy_mismatch`.
- The local σ_m version adds `taylor_remainder_sq` for G and an absorption step (medium).

**Why it matters for the study.** L4 is the theoretical reason the deployable analog-seed proxy uses R·ν̂ and not R alone. The pilot confirms it: the Spearman correlation rose from about 0.55 to about 0.75, with a fitted constant of 0.26 on all three systems.

## L5. Optimal weight [T]

**Statement.** V(w) = w²(V_a + ρ²/k) + (1 − w)²V_s + 2w(1 − w)V_K.

- If the copied noise ξ is orthogonal in L² to e_C − e_P, then the curvature satisfies c = ‖e_C − e_P‖² + ‖ξ‖² ≥ ρ²/k > 0. So V is strictly convex.
- Its unique minimizer is w* = (V_s − V_K)/c, and the constrained minimizer is clip₀¹(w*).
- w* lies in [0, 1] iff V_K ≤ min(V_a + ρ²/k, V_s).

**Lean.** Entirely reuse:

- `combVar`, `wstar`;
- `weight_mem_unit_interval_iff`;
- `boundary_optimal_left/right`;
- `sq_diff_noisy`, whose orthogonality hypothesis is exactly the copied-noise independence;
- `OptimalWeightL2` for a ≥ 0 via Cauchy–Schwarz.

The only new item is a one-line corollary c ≥ ρ²/k.

## L6. Separation [T] and its limit [T], with the Oseledets version [C]

**Statement (scale invariance).** For q ≠ 0, wstar(q·a, q·b, q·c) = wstar(a, b, c). Hence, if the amplified variances are V_a = ε²q_H, V_s = δ²q_H and V_K = κq_H with q_H = Γ_H S Γ_Hᵀ (proportional covariances), w* does not depend on H or Γ_H: w* = (δ² − κ)/(ε² + δ² − 2κ).

**Statement (copied-noise transient).** With the copied-noise term,

w*(H) = (δ²q_H − κq_H)/((ε² + δ² − 2κ)q_H + ρ²/k).

- w*(H) increases with q_H whenever δ² > κ.
- w*(H) converges to the closed form as q_H → ∞.

So the copied noise tilts the weight toward PLP at short horizons only (this generalizes `wstar_antitone_library_noise`).

**Lean.** Both are easy: `field_simp`/`ring` for invariance, and `Filter.Tendsto` of a rational function for the limit.

**[C] Long-horizon alignment.** If Γ_H/‖Γ_H‖ → v (adjoint Oseledets direction), then w*(H) → (vᵀΣ_s v − vᵀKv)/(vᵀΣ_a v + vᵀΣ_s v − 2vᵀKv).

- The *implication* (alignment ⟹ limit) is [T] by continuity and can be mechanized conditionally.
- The *alignment itself* is the Oseledets multiplicative ergodic theorem, which is not in mathlib. It is cited.

**What the experiment adds.** H2a tests whether the proportional-covariance hypothesis holds closely enough. The pilot says it does not: w* moves by 0.12–0.28 in the small-error regime, and instability keeps a partial correlation of 0.06–0.13.

**This is a theorem with a falsified hypothesis, not a false theorem.** The paper's statement becomes: "separation holds exactly under proportional seed covariances (L6); the measured departure quantifies the seed anisotropy of real attractors."

## L7. Hybrid horizon-gain bound [T]

**Statement.**

- (i) If V_K ≥ 0 and the copied-noise term is negligible, then min over w ∈ [0, 1] of V(w) ≥ ½ min(V_a, V_s).
- (ii) If the better forecaster's error grows exactly as e₀e^(ΛH), then the hybrid's crossing of any tolerance occurs at most ln2/(2Λ) later.
- (iii) With uncorrelated seeds, the gain equals (1/(2Λ)) ln(1 + r²), where r is the seed ratio.
- (iv) For V_K < 0 the bound fails. Explicit counterexample: (V_a, V_s, V_K) = (1, 1, −1) gives min V = 0.

**Proof.**

- (i) Case split on V_K ≥ V_a. Otherwise use the closed form of the minimum and the inequality V_a(V_s − V_a) + 2V_K(V_a − V_K) ≥ 0.
- (ii) Solve e₀e^(ΛH)/√2 = e₀e^(ΛH′) for H′ − H.

**Lean.** Small: `nlinarith` with the case split; `Real.log`/`Real.exp` algebra; `norm_num` for the counterexample.

## L8. Horizon law [T] and rigorous lower bound [T]

**Statement (law).** If g_H = e^(ΛH), then the characteristic horizon is T = Λ⁻¹ ln(θσ_x√m/e₀). Consequently:

- dT/d ln θ = 1/Λ;
- T is increasing in θ and decreasing in e₀.

**Statement (robust bracket).** If (Λ − ε)H ≤ ln g_H ≤ (Λ + ε)H on the window, then

ln(θ′/e₀)/(Λ + ε) ≤ T ≤ ln(θ′/e₀)/(Λ − ε).

This turns H1d's tolerance band into a theorem about how linear ln g_H must be.

**Statement (discrete first passage).** On integer horizons, T = ⌈Λ⁻¹ ln(θ′/e₀)⌉, with censoring at H_max.

**[T] Rigorous lower bound (L8′).**

- Hypotheses: the vector field is L_K-Lipschitz on a forward-invariant set K, and h is L_h-Lipschitz.
- Grönwall gives |e(t)| ≤ L_h‖ξ‖e^(L_K t).
- So the forecast is guaranteed within θ for all t < L_K⁻¹ ln(θ/(L_h‖ξ‖)).

This is a *certified* horizon: nonlinear and valid without linearization. The law above is its sharp linearized counterpart.

**Lean.**

- Law, bracket and discrete version: `Real.log_le_log`, `div_le_div`, `Nat.ceil` lemmas (small).
- L8′: reuse `two_trajectory_bound` plus log algebra (small).

## L9. Geometric versus arithmetic growth exponent [T]

**Statement.** For growth factors g₁, …, g_M > 0,

(1/2H)·mean(ln gᵢ²) ≤ (1/2H)·ln(mean gᵢ²),

with equality iff all gᵢ are equal. So the NLLE-type exponent never exceeds the mean-square exponent Λ used in the horizon law, and they agree iff growth is isotropic.

**Lean.** Use the weighted AM-GM `Real.geom_mean_le_arith_mean_weighted` and take logs. The equality case is via `Real.geom_mean_eq_arith_mean_weighted_iff`, if present at the pin; otherwise strict concavity of log (medium).

## L10. Abstraction regret [T] and quantization rate [T]

**Statement.**

- (i) Vᵢ(w) − Vᵢ(wᵢ*) = cᵢ(w − wᵢ*)².
- (ii) The minimizer of Σᵢ cᵢ(w − wᵢ*)² is the curvature-weighted mean.
- (iii) If |w_k − wᵢ*| ≤ ε_w on the regime, then the mean regret is ≤ ε_w² max cᵢ.
- (iv) If w* is L-Lipschitz on [0, 1]^p and the regimes are the n^p grid cells (K = n^p), then the mean regret is ≤ c_max L² p/n² = c_max L² p K^(−2/p).

**Lean.**

- (i)–(iii) are small (`Finset.sum`, `ring`, `nlinarith`).
- (iv) is medium: grid-cell diameter √p/n plus the Lipschitz bound.

**[E] What is not a theorem.** That a CART tree on the *estimated* profile attains this rate.

- The pilot shows it does not: regret is flat in K. The cause is proxy noise in F̂, which violates L10′'s hypothesis that w* is a function of the coordinates.
- That observation is itself a corollary worth stating: if w* is not measurable with respect to the coordinates up to noise of variance τ², regret ≥ c_min τ² for every K.
- This "irreducible-regret floor" is provable [T, small] and explains the flat curve.

## L11. The fourth LPC: noise sensitivity [T]

This is the new result. It gives the fourth coordinate a precise meaning, so the study's redundancy test (H1f) is testing a theorem's consequences rather than a hunch.

**Definition.** Retrieval noise sensitivity:

N(s) = (ρ√D)⁻¹ · (E_η ‖X_{i*(G(s)+η)} − E X_{i*}‖²)^(1/2),

the r.m.s. displacement of the retrieved analog's delay vector under observation noise, per coordinate, in noise units. The code computes it from oracle draws (oracle) and by parametric bootstrap around the observed X (deployable).

**Theorem L11(a): PLP-side reducibility.**

- To first order in ρ, the noise-induced change in PLP's forecast is Γ_H J⁺η.
- Its r.m.s. size satisfies ρ‖Γ_H J⁺‖_F ≤ ρ g_H ν.
- So the noise sensitivity of the *physics* forecaster is a function of observability (ν), amplification (g_H) and ρ alone. It carries no information beyond (ν, Λ).

*Proof:* L2(d) plus submultiplicativity of the operator and Frobenius norms. *Lean:* small, given L2.

**Theorem L11(b): CP-side margin control.**

- Setup: let d₁ < d₂ be the nearest and second-nearest library distances from the clean query G(s), and Δ = d₂ − d₁ the margin.
- (i) **Deterministic stability.** If ‖η‖ < Δ/2, the retrieved analog does not change.
  *Proof:* each distance moves by at most ‖η‖ (triangle inequality).
- (ii) **Probabilistic control.** Pr(retrieval changes) ≤ Pr(‖η‖ ≥ Δ/2).
  - By Chebyshev/Markov, this is ≤ 4Dρ²/Δ².
  - By Gaussian concentration of the norm (traditional), it is ≤ exp(−(Δ/(2ρ) − √D)²/2) for Δ > 2ρ√D.
- (iii) **Spread bound.** If retrieval changes from i₁ to j under η, then ‖X_j − X_{i₁}‖ ≤ 2(d₁ + ‖η‖), because j is at least as close to G(s) + η as i₁ is. The spread about the mean is at most the spread about X_{i₁}, so

  N(s)² ≤ (4/(ρ²D)) · E[(d₁ + ‖η‖)² · 1{‖η‖ ≥ Δ/2}].

  N is small when the margin is large compared with the noise, and grows like (d₁/ρ)·√Pr(‖η‖ ≥ Δ/2) otherwise.

**What L11 implies for H1f.**

- N is governed by the **margin in noise units**, Δ/ρ.
- The recurrence coordinate R = d₁ is a *different order statistic* of the same nearest-neighbor process. Per realization, Δ is not a function of d₁, so N is **not** reducible to (ε̃, ν̃, Λ̃) pointwise.
- In distribution over library sampling, both d₁ and Δ are functions of the local density c(s) and dimension d(s). For a locally Poisson library of intensity λ, the two are jointly determined by λ, by standard order-statistic results.
- So N is reducible **on average but not state by state**.

The theorem therefore predicts *how* H1f can come out:

- If allocation outcomes depend on the realized library geometry, N should add out-of-sample information (H1f: "adds information").
- If they depend only on local density, N is redundant given the three seeds ("redundant").

Either result is consistent with L11, which says which mechanism decided it.

**Lean.**

- (i) is small: finite-set argmin stability under perturbation, `Finset.exists_min_image` plus triangle inequalities.
- (ii)'s Markov version is medium: `MeasureTheory.meas_ge_le_lintegral_div` with E‖η‖² = Dρ², in the moments-model style of `NoiseL2.lean`.
- The Gaussian-concentration version is out of scope (no multivariate Gaussian norm-concentration lemma at the pin); state it traditionally.
- (iii) follows from (i)–(ii) (small).

```lean
/-- L11(b)(i): retrieval is stable under perturbations smaller than half the margin. -/
theorem retrieval_stable {V ι : Type*} [NormedAddCommGroup V] [Fintype ι]
    (lib : ι → V) (x η : V) (i₁ : ι) (Δ : ℝ)
    (hmargin : ∀ j ≠ i₁, ‖x - lib i₁‖ + Δ ≤ ‖x - lib j‖)
    (hη : 2 * ‖η‖ < Δ) :
    ∀ j ≠ i₁, ‖(x + η) - lib i₁‖ < ‖(x + η) - lib j‖
-- proof: norm_sub_le / abs_norm_sub_norm_le on both sides, then linarith.
```

## L12. Analog-seed scaling [C]

- E[d₁²] ~ c² N^(−2/d) for a measure with local dimension d at s, from nearest-neighbor asymptotics (e.g. Evans, Jones & Schmidt 2002; Penrose & Yukich).
- The noise floor follows from L11: once d₁ ≲ ρ√D, the margin is within noise and retrieval wanders.
- A theorem requires local-dimension regularity and is asymptotic. It is cited, not mechanized. H1b tests it: it passes on Lorenz-63, and the fitted 1/d is about 30% low on Rössler and Chua.

# 3. What cannot be a theorem, and why [E]

- **Predictive sufficiency of the four-coordinate profile.** This is a conditional-independence property of the joint law of (state, outcomes). It has no closed form for chaotic attractors; H1f and the nested test give evidence only.
- **Transfer of regimes across systems.** Non-dimensionalization makes quantities comparable but implies nothing about the invariant measures of different systems (T1).
- **Tree partitions reaching L10′'s rate.** These are algorithmic and data-dependent.
- **The deployable proxies' accuracy.** This depends on the estimator and library (H1e).

# 4. Recommended plan

| Order | Items | Lean effort | Paper |
|---|---|---|---|
| 1 | L5, L6, L7, L10(i–iii): the allocation core | about 1 day (mostly reuse) | Prop. + proof each |
| 2 | L8, L8′, L9: horizons | about 1 day | Prop. + proof each |
| 3 | L11(a), L11(b)(i), (b)(ii) Markov, (b)(iii): the fourth LPC | about 1–2 days | the headline new theorem |
| 4 | L2, L3: observability | about 1–2 days (eigenvalue trace is the hard step) | Prop. + proof |
| 5 | L4 local, L10′ | about 1–2 days | Prop. + proof |
| — | L6′, L12, the Gaussian version of L11(b)(ii) | none | cited, stated with hypotheses |

**Total.** About 5–8 Lean-agent days, at the pace of the earlier phases. Every row gets a §8.2 entry with disclosed narrowings: hypothesized singular values instead of an SVD, moments models instead of measures where the informal argument only uses moments, and the conditional form of L6′.

**How to present it at the fair.** One page of theorems (L5–L8, L10, L11) with machine-checked badges. One page of figures showing where each theorem's hypotheses hold and fail on Lorenz-63, Rössler and Chua: H1a/H1c/H1d for L1, L2 and L8; H2a for L6; H2e for L7; H3 for L10; H1f for L11.
