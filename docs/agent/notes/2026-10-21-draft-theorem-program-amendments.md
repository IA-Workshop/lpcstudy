# Draft for the owner: proposed amendments to `theorem_program_lpc_v1.md` (C1.2)

**Status: draft, not applied.** Nothing in `docs/study/` is edited. The program file is a reference document (its own Status section says so); it is not pre-registered v3 text, but PRIME.5 still applies: the proposal is to **append** dated errata, never to rewrite the 6 October text. No pre-registered hypothesis, band, level, decision rule or v3 sentence is touched by any item below. Source: WU-0027 verification, `2026-10-21-math-theory-verification.md` (findings V1, V2, V12, V13, V15).

Each item says what changes, where, and why; "text" is the proposed erratum wording.

## 1. L3: narrow the existing erratum; add the affine-invariant trace form

- **Where:** Status → Errata, first bullet ("L3 proves orthogonal (not affine) invariance of the whitened ν").
- **What changes:** keep the bullet (it is correct for the literal statement) and append one sentence.
- **Why:** the literal statement transforms W ↦ UW, which is not how a whitener transforms under s′ = Us (W′ = WU⁻¹ up to a left orthogonal factor); hence the orthogonal restriction. The quantity the code computes is ν² = tr[(JᵀJ)⁻¹C⁻¹] (`dynamics.make_observability`), which is unchanged by every invertible affine change s ↦ As + b (J ↦ JA⁻¹, C ↦ ACAᵀ; trace cyclicity) and by the choice of whitener (verified symbolically and numerically, V15).
- **Text:** "Addendum (2026-10-21): the restriction to orthogonal U concerns the literal form tr[W(JᵀJ)⁻¹Wᵀ] with W ↦ UW. In whitened coordinates ν² = tr[(JᵀJ)⁻¹C⁻¹] with C the attractor covariance, and this is invariant under every invertible affine change of state coordinates and under the choice of whitening matrix. This is the quantity the code computes."

## 2. L5 and L10: disambiguate w* from clip(w*); add the clipping lemma and the corrected L10(iii)

- **Where:** Status → Errata, new bullet; L10 statement.
- **What changes:** a notation note and two added statements. **Not** a retraction: L10(i)–(iv) are true as written in v1's notation.
- **Why:** v1's L5 defines w* = (V_s − V_K)/c as the unconstrained minimizer and clip₀¹(w*) as the constrained one, so L10(i) V_i(w) − V_i(w_i*) = c_i(w − w_i*)² is correct, and L10(iii)–(iv) bound the regret against the **unconstrained** optimum. The study's "excess MSE" is against the admissible optimum clip(u_i) (Methods v2 §M13 item 7, DEF-0002); the pilot code had used c(w − clip u)², which understates it (u = 1.4, w = 0: 1.80 against 1.00). The document under review calls the v1 form "false"; it is not (V2). What is new is a lemma that bounds the admissible excess from a hypothesis on the unclipped regime mean.
- **Text:** "Notation (2026-10-21): in L5 and L10, w* denotes the unconstrained minimizer u = (V_s − V_K)/c; the admissible optimum is clip₀¹(u). L10(i)–(iv) hold with w* = u, and they bound the regret against V_i(u_i), which is at least the excess against the admissible optimum. **Clipping lemma.** For any real v, V(clip v) − V(clip u) ≤ c(v − u)². **L10(iii′).** If |ū_S − u_i| ≤ ε_w for all i in the regime, with ū_S = Σc_iu_i/Σc_i unclipped, then the mean excess of the regime weight clip(ū_S) over the state-optimal admissible weights is ≤ ε_w² max_i c_i. L10(iv) then holds for the admissible excess with the same constant. (The code computes the excess exactly, `oracle.excess_mse`, and the regime weight as clip of the mean of unclipped u_i, DEF-0003.)"

## 3. L5 / P1(a): the curvature floor and the study's estimand

- **Where:** L5 statement ("If the copied noise ξ is orthogonal in L² to e_C − e_P, then ... c ≥ ρ²/k").
- **What changes:** add the hypothesis under which the floor holds and the replacement that the code needs.
- **Why:** the orthogonality holds for an expectation that includes the library's noise (up to a selection effect of about 0.1ρ² at H ≤ 5 steps; my 2026-10-19 note §B.1 (C)). The study's oracle moments condition on the realized library (`forecast_draws` varies only the query draw), so ξ is a fixed number per analog and the floor is not guaranteed (toy ratio 0.41). The code needs only c > 0, and N1 gives it: c = E[(e_C − e_P)²] ≥ Var(e_C − e_P), which is Var(e_P) under stable retrieval.
- **Text:** "Addendum (2026-10-21): the floor c ≥ ρ²/k needs the expectation to include the noise of the copied value, independent of the retrieval and of e_P. The study's moments average over query noise at a fixed library, where this is not guaranteed. For them, c ≥ Var(e_C − e_P) > 0 whenever the two errors do not move in lockstep across draws (N1), and this is the hypothesis the code relies on (`excess_mse` cites ρ²/k in its docstring; a later code unit should cite c > 0)."

## 4. L7(ii) / P1(d): the envelope, and the growth-free form P1(d′)

- **Where:** L7 statement (ii).
- **What changes:** name the comparator as the per-horizon envelope; add L7(ii′) with its hypotheses.
- **Why:** the proof uses min(E_C, E_P) at each horizon; if the better forecaster switches identity, the envelope's first passage is later than either single forecaster's and the gain over the longer-horizon forecaster can exceed the bound by that lead (A1.7 fine print; the code's `better = max(t_cp, t_plp)` coincides with the envelope only for monotone curves, V3(a)). The growth-free form needs no fit and C ≥ 0 at one step, but its "every rule" clause needs the weight to be independent of the draw (V1), and in the study's units the √2 loosening applies to θ′ (V12).
- **Text:** "Addendum (2026-10-21): in (ii) 'the better forecaster' is the per-horizon envelope m(H) = min(E_C, E_P)^{1/2}, and the hypotheses are V_K ≥ 0 at every horizon and m(H) = r₀e^{ΛH} exactly; on integer horizons add one step. **(ii′)** For any error curves, with T(θ) the first integer H at which the r.m.s. error exceeds θ: if the raw cross-moment C ≥ 0 at the single step H₁ = T_m(√2θ), then T_h(θ) ≤ H₁ for the optimal hybrid and for every weight that is a function of the state and horizon only (not of the draw), and T_h(θ) ≥ T_m(θ) for the optimal hybrid; the bound is exact in discrete steps. With verification noise added in quadrature, replace θ by θ′ = √(θ² − ρ²) on both sides."

## 5. Optional, from the 2026-10-19 note (owner's choice)

- **P3(b) / L10's floor:** "vanishes when u is a function of F" is sufficient; the floor is zero iff clip ū(F) = clip u almost surely on {c > 0} (V13).
- **L6 remark in v3 §3** omits the copied-noise term (u = (δ² − κ)q_H/((ε² + δ² − 2κ)q_H + ρ²/k)); the program's L6 already states it correctly, so no program change; this is for a later v3 erratum list only, never for the sealed text.

## Caution

- These are errata to a reference document, to be appended with a date, not edits of the 6 October text (PRIME.5).
- No v3 sentence, hypothesis, band, level or decision rule changes; the sealed run and its outputs are untouched.
- Items 3 and 4 mention a future code docstring change and a possible screen change; those go through their own work units (the second is the subject of `2026-10-21-draft-gain-screen-decision.md`).
