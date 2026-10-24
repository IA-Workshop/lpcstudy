# WU-0027: independent verification of `theorem_proofs_detailed.md` (Parts A and B) and its checks

**DEVELOPMENT: not a hypothesis test.** No seed was drawn or run; the confirmatory seed, flag and `runs/confirmatory` were not read. Study numbers quoted here come only from `docs/study/pilot_results_v3_dev0_reference.json` (DEV-0, DEVELOPMENT) and from the released preliminary-findings note `docs/agent/notes/2026-10-20-prelim-findings-conf1.md` (CONF-1, PRELIMINARY, UNPROMOTED). Everything I computed is synthetic, single-threaded at `nice -n 19`, CPU only (`verify_wu0027.py` and its log in `2026-10-21-math-theory-verification/`, run with `uv run --no-project --with sympy --with numpy python -I`: SymPy is an ephemeral tool, not a project dependency).

- **Date:** 2026-10-21. **Agent:** applied-mathematician (claude-fable-5-1). **Branch:** `wu/theory-verify` from develop 49b3154.
- **Read in full:** `theorem_proofs_detailed.md` (1,093 lines), `theorem_checks.py`, `proposed_checks.py`, both run logs and JSONs (owner run and main-session run), my note of 2026-10-19, `theorem_program_lpc_v1.md`, v3 §2, §3, §7, §8, Methods v2 §M13; `lpcstudy/oracle.py` (`oracle_weight`, `curvature`, `excess_mse`, `characteristic_horizon`), `ensemble.py` (`AnalogLibrary.build`, `forecast_draws`), `pipeline.unit_noise`, `dynamics.make_observability` (docstring), `analysis.gain_horizon_bound`, `analysis.h1c_*`, `experiments.py` sweep block.
- **Not changed:** nothing under `lpcstudy/`, `tools/`, `docs/study/`, `seeds/`, `ROADMAP.md`, the ledger or any record. New files only: this note, its folder, and the two drafts beside it.

## 0. Summary

Every algebraic step of Parts A and B that I re-derived (SymPy, exact rationals, or randomized numerics: 30 of 30 items in `verify_wu0027.log`) agrees with the document. **No theorem in Part A or Part B is wrong as a mathematical statement under its own stated hypotheses.** What I found are (i) one hypothesis missing from P1(d′) that matters for the study ("every allocation rule" fails for draw-dependent weights, V1); (ii) one historical claim that is wrong (the v1 program's L10(i) is not false in its own notation, V2); (iii) one data statement that contradicts the code (the "C < 0 at some horizon" percentages are the centered covariance at one horizon, V4); (iv) three places where a theorem is said to give a study result more than it does (N2's chain, N8 and H2b(i), N7's "no bias", V5, V7, V9); and (v) five checks that cannot fail or test a weaker claim than they name (§3). None changes a pre-registered verdict; all are post-freeze findings for the document, the drafts and later development work.

## 1. Verdict table

Grades: **correct** (statement and proof hold as written); **correct with a stated fix** (the fix is given, no verdict changes); **wrong** (a counterexample or a contradiction with the repository is given). "Hyp." names a hypothesis that must be added to the statement.

| Item | Grade | Finding(s) | Independent check |
| --- | --- | --- | --- |
| F1–F14 toolbox | correct | F8 needs φ twice differentiable on (0,1) and continuous on [0,1]; F11 needs B positive definite: both as used | — |
| A1.2 P1(a) algebra, clip | correct | — | SymPy identity; A1.3 identities |
| A1.3 P1(b), restatement | correct | needs c > 0 (stated) | SymPy |
| A1.4 P1(c), tightness | correct | step 8 is where C ≥ 0 enters; c > 0 is automatic in Case 2 | SymPy step 6–7 |
| A1.5 P1(e) | correct | — | SymPy |
| A1.6 conditioning caveat | correct | agrees with my 2026-10-19 note §B.1; "cite N1" is the right action | code: `forecast_draws` varies only the query draw; library noise fixed at `AnalogLibrary.build` |
| A1.7 P1(d), L7(iii) | correct | fine print on the envelope is right; see V3(a) for the code's "better" | SymPy (L7(iii)) |
| **A1.8 P1(d′)** | **correct with a stated fix** | V1 (Hyp.: weight independent of the draw), V12 (θ′ form), V3 (how the code's screen differs) | 2,676 random non-exponential cases with C ≥ 0 at H₁ only and a switching envelope: 0 violations; lower bound 0 violations; draw-dependent counterexample |
| A2.1–A2.3 L6, transient | correct | the transient keeps the copied-noise term "uncorrelated with everything else", which A1.6 says is a model assumption: consistent because flagged (V16) | SymPy derivative and shortfall 1 − n/c |
| A2.4 | correct | CONF-1 words verified (§4) | — |
| A3.2 P2(a), tightness | correct | — | my 2026-10-19 note §B.2 |
| A3.3 P2(b) | correct | — | — |
| A3.4 P2(c) | correct | the "exact for the empirical law" remark is right; DEV-0 numbers verified (§4) | — |
| A3.5 L11(a) | correct | — | — |
| **A4.1 regret identity; "v1 form is false"** | identity **correct**; the historical claim is **wrong** | V2 | v1 L5 defines w* as the unconstrained minimizer; `theorem_checks.py` "L10(iii)" passes v1's form with u_i outside [0,1] |
| A4.2 P3(a) | correct | needs Σc_i > 0 (stated implicitly) | — |
| A4.3 P3(b) | correct | "vanishes when u is a function of F" is sufficient, not necessary (V13) | — |
| A4.4 lemma, corrected L10(iii), L10(iv) | correct | the lemma is new and useful; the parenthetical on v1 is V2 | 20,000 exact-rational cases, 0 violations |
| A5.1 L8, A5.2 bracket | correct | discrete "+1 step" argument right | — |
| A5.3 L8′ Grönwall and numbers | correct | L_K = 50.0, certified 0.0542 LT, linearized 3.00 LT, ratio 55 (V14: orbit-sampled box, not a proven enclosure) | recomputed from a 280-time-unit orbit |
| A5.4 L9 | correct | — | — |
| A6.1 L1 | correct | CONF-1 words verified | — |
| A6.2 L2 | correct | — | — |
| A6.3 L3 strengthened, erratum note | correct | V15: the code computes the trace form, so affine invariance applies to the study's ν | numeric: invariance 3e-9, whitener-independent |
| A6.4 L4 | correct | — | — |
| N1 | correct | trivial (F3); fine as the replacement for the ρ²/k argument | — |
| N2(a) | correct | — | SymPy |
| **N2(b)** | correct with a stated fix | V6: "impossible" holds for the population m = 0; the study's m is the 200-draw sample mean | SymPy: |m|(|μ|−|m|) ≤ μ²/4 |
| N2(c) and "the chain" | (c) correct; chain wording **overstated** | V5 | — |
| N3(a) | correct | needs Σ_s ≻ 0, Γ ≠ 0 | my numerics |
| **N3(b)** | correct with a stated fix | V8: copied noise omitted from E_C | pencil and range: 8e-14 |
| N4(a) | correct | hypothesis C ≤ min(E_C, E_P) ⇔ ϱ ≤ √r; D = (1−ϱs)² + s²(1−ϱ²) > 0 | SymPy: f, f′ factorization, denominator |
| N4(b) and "what it tightens" | (b) correct; data sentence **contradicts the code** | V4, V10 | — |
| N5 | correct | needs Λ_loc(T) ≠ 0 and a continuous crossing; H1c's statistic is a 3-to-4-point OLS secant, not the derivative (note) | — |
| N6 | correct | R_c² is defined to make the identity hold; the content is the Pythagoras identity (also V17 for the check) | independent R_c²: 4e-17 |
| N7 | correct | V9: "no bias" overstated; "293 of 300" is 294 in both stored runs | p_j vs 4×10⁵ draws; dimension-free bound |
| **N8** | correct under its stated conditions; "turns H2b(i) into a theorem" **overstated** | V7 | SymPy at m̄ = 0; CRN form with m̄ ≠ 0; sign search |

## 2. Findings

Severity: **major** = changes what the document claims or what a draft must say; **minor** = wording or a missing qualifier; **note** = for the record.

**V1 (major; A1.8 statement, "for every allocation rule"; also N4(b)).** The displayed chain 0 ≤ T_h(θ) − T_m(θ) ≤ T_m(√2θ) − T_m(θ) holds for the optimal hybrid. The upper bound extends to every weight that is a function of the state and the horizon only. It does **not** extend to a weight that depends on the draw: for such a rule the realized MSE E[(w_r e_C + (1 − w_r) e_P)²] can be below min_w V(w). Counterexample: e_C = ±1 and e_P = ±2 independent and symmetric; E_C = 1, E_P = 4, C = 0, min_w V = 4/5; the rule w_r = 2/3 when the signs differ (error 0) and w_r = 1 otherwise (error 1) has realized MSE 1/2. With θ² = 0.6 the optimal hybrid has crossed at this step and the rule has not, so T_rule > H₁. The study's deployable rules A3–A5 use per-draw weights (their profile is read at the noisy query; my 2026-10-19 note §B.3), so the sentence "applies to every allocation rule" needs the hypothesis "whose weight is independent of the draw". The oracle hybrid used by `gain_horizon_bound` (`oracle_weight(m)` per horizon) satisfies it, so the screen itself is unaffected. Fix: add the hypothesis in A1.8 and N4(b); say "every draw-independent weight".

**V2 (major; A4.1 "The v1 form is false", the A4.4 parenthetical, C1.2 bullet 2).** The program's L5 reads "its unique minimizer is w* = (V_s − V_K)/c, and the constrained minimizer is clip₀¹(w*)": in v1, w* **is** the unclipped minimizer. With that notation L10(i) V_i(w) − V_i(w_i*) = c_i(w − w_i*)², L10(ii) and L10(iii) are true as written (L10(iii) is then the one-line bound mean c_i ε_i² ≤ ε_w² max c_i), and `theorem_checks.py` "L10(iii)" in fact tests exactly v1's form, with u_i drawn from N(0.5, 0.8) (many outside [0,1]), and passes. What used the clipped w* was the pilot **code** (Methods v2 §M13 item 7, DEF-0002, DEF-0003), which v2 corrected. The counterexample "u = 1.4, w = 0 gives 1.80 against 1.00" is correct arithmetic for the clipped reading but refutes a statement the program does not make. The A4.4 parenthetical "(The program's v1 form, with the clipped w_S in the hypothesis and regret measured against the unclipped u_i, fails ...)" attributes a mixed form to v1 that v1 does not state. What **is** new and useful is the A4.4 lemma and the corrected L10(iii), which bound the admissible excess V_i(clip ū_S) − V_i(clip u_i) from a hypothesis on the **unclipped** ū_S; v1's form only bounds the excess against the unconstrained optimum (a looser quantity, since V_i(u_i) ≤ V_i(clip u_i)). Fix: in A4.1 and C1.2 replace "the v1 form is false" by "v1's w* is the unconstrained minimizer; the clipped reading was the pilot code's error (DEF-0002); the program text should disambiguate w* from clip(w*) and add the clipping lemma". The draft `2026-10-21-draft-theorem-program-amendments.md` does this.

**V3 (major for C1.3; A1.8 "Why it matters for the data", N4 tests, `analysis.gain_horizon_bound`).** Three differences between the document's reading of the screen and the code, none of which changes a verdict (the row is reported only, DEC-0016 O2, DEC-0033 M3): (a) the code's "better" is `max(t_cp, t_plp)`, the later of the two single-forecaster first passages, not the envelope's first passage T_m of min(E_C, E_P). For monotone curves they coincide; for a non-monotone curve (CP's r.m.s. error on an oscillatory system can dip below θ after crossing) T_m ≥ max(T_C, T_P), and the code's gain exceeds T_h − T_m by T_m − max(T_C, T_P), exactly the fine print of A1.7. (b) The code's covariance condition is **centered** (`m.cross − m.mean_cp·m.mean_plp`) at one horizon; P1(c) needs the **raw** C ≥ 0. (c) The horizon at which P1(d′) needs C ≥ 0 is T_m(√2θ′), not the crossing of θ′. The ROADMAP's WU-0002.15 plans "raw C ≥ 0 at every horizon" (P1(d)'s hypothesis), which is a third option. The decision draft states all three precisely.

**V4 (major as a data statement; N4 "What it tightens", N2 "Tests").** "DEV-0: 22–32% of states have C < 0 at some horizon" matches `gain_bound.n_screened_out.negative_covariance` (109, 162, 122 of 500 = 21.8%, 32.4%, 24.4%), but that counter is the **centered** covariance at the **single** horizon max(T_C, T_P) (V3(b)), not raw C at some horizon. Neither the raw C nor an "at some horizon" count exists in the DEV-0 reference file. Fix: "22–32% of test states have a negative centered error covariance at the better forecaster's crossing (DEV-0 gain-bound screen)". The N4 statement about negative correlation stays true; only its evidence is misdescribed.

**V5 (minor; N2 "What it explains", "The chain for noise matching").** N2(c) shows switching is **necessary** for C ≠ μm. It gives |C − μm| a bound, not a sign. "Cross-moment beyond μm ⟶ lower weight" needs C to rise, which no result in the document implies; H2e stays empirical. Also H2e's statistic is the centered per-state Pearson correlation (`H2e.corr_curve`, with `zero_variance_corr` counting the constant-CP states), while N2 is in raw C; the two agree that no switching ⟹ no correlation (centered covariance is exactly 0 when e_C is constant), but the sentence should name the statistic. Fix: "each arrow is a theorem except the direction of the cross-moment, which H2e measures".

**V6 (minor; N2(b) "w* = 0 is impossible").** In the study m is the sample mean over M = 200 draws, never exactly 0. The exact condition (same signs and σ² ≤ |m|(|μ| − |m|)) with |m| ≈ σ/√M gives |μ| ≳ √M σ ≈ 14σ. So the usable statement is quantitative: "under stable retrieval, zero weight needs CP's error to exceed PLP's draw spread by a factor of order √M unless PLP is biased". The dichotomy "switching or biased PLP" stands with "biased" read as the sample mean.

**V7 (minor; N8 setting and "What it tightens").** (a) The setting **is** consistent with the oracle: library noise is `noise * ctx.library_unit_noise` with one fixed unit draw (`ensemble.py` line 241), the query unit noise is keyed by (seed, system, D, split, purpose) without ρ (`pipeline.unit_noise`), so both scale with ρ under common random numbers, and A = Γ_H d depends on ρ only through the analog index. (b) Under CRN the PLP sample mean is m = ρ m̄ with m̄ = Γ_H J⁺ z̄ = O(M^{-1/2}) ≠ 0. The exact form is then u = (q − y m̄)/(y² + q) with y = A/ρ + z − m̄ (verified symbolically), so the stated derivative is exact only at m̄ = 0. A search over 2×10⁵ random parameter sets with 0.02 < w* < 0.98 found **no** case where the sign of dw*/dρ differs from the document's criterion A(A + ρz) > 0; the disagreement regions are w* ≈ 1 and w* ≈ m̄²/(2q). The sign claim is robust; the formula is first order in M^{-1/2}. (c) "Stable retrieval" across the four ρ levels is stronger than stable retrieval across draws at one ρ, because the library vectors move with ρ too. (d) "N8 turns H2b(i) into a theorem" (table row and the first sentence of "What it tightens") is an overstatement: H2b(i) is a mean rank correlation over **all** states, of which 75–90% switch within 200 draws at ρ = 1% (DEV-0 `P2c.n_switching_states`), and the subset stable across all four ρ is smaller; N8 gives the mechanism in a regime. The grade "Theorem, under stated conditions" and C5's "consistent with" rule are the right wording; the table's "Gives H2b(i) ... a theorem" is not.

**V8 (minor; N3(b)).** Under stable retrieval the CP error is Γ_H d + ξ with the copied noise ξ fixed (N2's μ, N8's A + ρz), so E_C = (Γ_H d + ξ)², not (Γ_H d)². N3(b)'s formula follows A2.1's "ignoring ξ"; at 1 LT this is a small correction, at short H it is not. Fix: state "copied noise negligible" or carry (Γd + ξ)². The conclusion "separation cannot hold exactly for CP" is right as a statement about L6's proportional-covariance hypothesis (rank one against positive definite).

**V9 (minor; N7 "A better deployable N̂").** The p_j computed from the observed query carry the same estimand bias as N̂ (DEF-0008: the margin at the noisy query is not the margin at the clean one); only the Monte Carlo noise of the 16 perturbations is removed. "No bias" should read "no Monte Carlo error". Also "smaller in 293 of 300 random states": both stored runs (`proposed_checks.json`, the main session's log) say 294.

**V10 (minor; N4 "Noise matching erodes the horizon gain").** ϱ is the raw-moment correlation C/√(E_C E_P); H2e measures the centered correlation; and r = min/max changes with N_lib too. The prediction "gain falls with N_lib" is a heuristic consequence, correctly listed under tests; the sentence "f rises toward 1" should not cite H2e as if it measured ϱ.

**V11 (note; A1.8 "Why it matters for the data").** The DEV-0 percentages (4.5%, 9.7%, 7.7% exceed; largest gains 1.7, 3.8, 2.1 LT) are verified from `gain_bound` (fractions 0.9552, 0.9033, 0.9233; max gains 1.733, 3.767, 2.067 LT). They are the v1 screen (bound + 1 step, centered covariance), as the file and the CONF-1 note both label it.

**V12 (note; A1.7 definitions, A1.8).** `characteristic_horizon` crosses when √(MSE + ρ²) > θ (quadrature, strict), so the document's "with θ′ = √(θ² − ρ²) in place of θ" is right, and P1(d′) in the study's units reads T_h(θ) ≤ T_m^clean(√2θ′), equivalently the noisy criterion at the level √(2θ² − ρ²), **not** √2θ. The difference is at most 2.8% in θ under θ ≥ 3√2ρ (`threshold_noise_factor`); in 2,757 random monotone cases the naive √2θ form was never violated, but the exact statement is the θ′ one, and the decision draft uses it.

**V13 (note; A4.3 P3(b) "It vanishes when u is a function of F").** Sufficient, not necessary: the floor is 0 iff clip ū(F) = clip u a.s. on {c > 0} (my 2026-10-19 note §B.3). N6's no-clipping assumption is where the "iff" becomes the stated identity.

**V14 (note; A5.3).** Recomputed: L_K = 50.0 from the Frobenius norm at the corners of the orbit box [−20.7, 19.8] × [−27.4, 25.8] × [1.8, 48.0] plus margin 2 (the Frobenius norm is convex in each coordinate, so the corner maximum is valid); certified horizon ln 20 / 50 = 0.0599 time units = 0.0542 LT; linearized ln 20 / 0.905 = 3.00 LT; ratio 55. The box is sampled from one orbit, not a proven invariant set: fine for the illustration, not a certificate.

**V15 (note; A6.3).** The v1 literal form transforms W ↦ UW, which is not how a whitener transforms under s′ = Us (W′ = WU⁻¹ up to a left orthogonal factor); that is why the v1 erratum had to restrict to orthogonal U. The code computes ν² = tr[C^{-1/2} Q (AᵀA)^{-1} Qᵀ C^{-1/2}] (docstring of `dynamics.make_observability`), the trace form of A6.3(b), which is invariant under every invertible affine change and under the choice of whitener (numeric: 3×10⁻⁹). The C1.2 bullet is right.

**V16 (note; A1.6 against A2.3).** A2.3 models the copied noise as uncorrelated with everything else, which A1.6 says the design does not guarantee; the document cross-references A1.6, so this is consistent. The formula is a model statement, and H2a's horizons (≥ 1 LT) are where the term is negligible (my 2026-10-19 note §B.4).

**V17 (minor; checks).** See §3: five checks cannot fail or test a weaker claim than named; four skip censored cases without reporting the evaluated count.

**V18 (note; data).** "22–36% of states have w* = 0" (N6) is v3 §8's pilot figure. DEV-0 reference: 155, 137, 137 of 500 (31%, 27%, 27%); CONF-1 (PRELIMINARY): 285, 305, 284 of 1000. The source should be named.

**V19 (note; §0.1 and the appendix).** "Both scripts ... run in under a minute each on two CPU cores" cannot be verified: neither log records a time, and the main session's run was one niced thread. Harmless.

## 3. Audit of the checks

For each check: does it test the named claim, is the tolerance at least as tight as the claim needs, and can it pass vacuously. "OK" means yes, yes, no.

| Check | Verdict | Detail |
| --- | --- | --- |
| L1 (a) generic F | OK | Hessian bound ‖a‖² + ‖b‖² is valid; abs tol 1e-10 |
| L1 (b) Lorenz slope | OK | slope 1.998 within 0.15 of 2; finite-difference derivative at 1e-6 is adequate for sizes ≥ 1e-4 |
| L2(a)–(c) | OK | PSD by the smallest eigenvalue of the symmetrized gap |
| L2(d) | OK, loose | tol 0.02 is 10× the Monte Carlo relative error (≈0.002 at 4×10⁵ draws); a wrong formula would err by O(1) |
| L3, L3 (strengthened), L3 (literal form) | OK | the literal-form construction demonstrates V15 |
| L4 | OK | the Hessian bound of the vector-valued quadratic map is valid; Taylor is exact for it |
| P1(a) symbolic | OK | — |
| P1(a) property, "c ≥ ρ²/k" part | **cannot fail** | c − copied = the (a, e_P) Gram quadratic form, ≥ 0 by construction; it restates the orthogonality model and says nothing about the study's estimand (A1.6 says so). The clip-against-grid part is a real test |
| P1(b) | OK | 1e-14 at the boundary |
| P1(c) proof step, P1(c)/L7(i), tightness, P1(e) | OK | min slack 4.7e-9 is an absolute number from a tiny-E_C case; a relative slack would read better |
| L7(iii) | OK, weak | value at r = 1 and one derivative sign at r = ½ |
| P1(d)/L7(ii) | OK | grid 1e-4, tol 1e-3; **censored cases are skipped without a count** |
| P1(d′) new | tests a **stronger hypothesis** than named | C ≥ 0 is imposed at every step and the envelope never changes identity; censored cases skipped without a count. My re-test with C ≥ 0 at H₁ only, C ∈ [−0.95, 0.95] elsewhere and a switching envelope: 0 violations in 2,676 |
| P1(d) vs P1(d′) | equality part **tautological** | with equal uncorrelated errors the hybrid is e²/2, so T_h(θ) = T_m(√2θ) identically; the content is the second clause (86 against 6.93 + 1), which I reproduced |
| L6, L6 transient | OK | — |
| L6 (hypothesis) | OK | the proportional branch is constant by construction; the anisotropic median range 0.64 is the content |
| L8 | OK, trivial | — |
| L8 bracket | OK | the `exp` overflow warning is harmless (finite indices precede `inf`) |
| L8′ | numbers OK; inequality **cannot realistically fail** | with L_K = 50 the bound is 100× the actual growth at t = 0.1; it is an illustration, and the reported numbers are the content (V14) |
| L9 | OK | — |
| L10(i) corrected | **vacuous** | checks (c(w−u)² + V₀) − (0 + V₀) − c(w−u)² ≡ 0, the definition against itself; the real identity is the P1(a) symbolic check |
| L10(i) as in v1 | arithmetic OK; attribution V2 | — |
| P3(a)/L10(ii) | OK | — |
| L10(iii) | tests **v1's form** (unclipped regret), a tautology that the document calls failing (V2) | the corrected L10(iii) is covered by the A4.4 lemma check |
| L10(iv) | OK | gradient bound 0.5·lip is right; no clipping occurs (target in [0,1]) |
| P3(b) | OK, weak competitors | 20 random tables per case; a per-cell grid search is decisive (done in my 2026-10-19 note) |
| P2(a), P2(a) tightness | OK | — |
| P2(b) | OK, mostly vacuous | the Markov bound is ≥ 1 at most states (Δ < 0.26 at ρ = 0.05, D = 7); the count of vacuous states is not reported; the 0.01 allowance is below one binomial s.e. (0.016) but the bound is loose |
| P2(c) | OK | 2.6e-26 excess is rounding of the sample mean |
| L11(a) | OK | — |
| A4.4 lemma | OK, strong | 4×10⁵ random triples |
| N1 | **cannot fail** | the F3 identity with `np.var` (ddof 0): c − Var = (mean)² ≥ 0 |
| N2(a) | OK | — |
| N2(b) | OK | 26,660 w* = 0 cases, non-vacuous |
| N2(c) | **cannot fail** | Cauchy–Schwarz on arbitrary arrays; the identity C = μm + E[(e_C − μ)e_P 1_S] holds by construction of e_C |
| N3(a), N3(b) | OK | attainment via the Cholesky pencil is valid (similar matrices) |
| N4(a) | OK | sign on [−1, √r] is not checked, only the factorization (the sign argument is two lines) |
| N4(b) | tests a **weaker claim** | f₀ = min of f from T_m(θ) onward, a stronger hypothesis than "f ≥ f₀ at the single step"; censored t_wide skipped without a count. Fix: f at H₁ |
| N5, N5 noise factor | OK | special case ln E quadratic in H; nonvacuous |
| N6 | first clause **tautological** | R² is defined from the floor, then the definition is verified; the Pythagoras clause is a real test. Fix: R_c² = E[c(ū(F) − ū)²]/E[c(u − ū)²] computed independently (my script: 4e-17) |
| N7 | OK | one-sided 4-s.e. allowance; 294 states tighter than Markov |
| N8 | OK at m̄ = 0 | the finite-M mean is not tested (V7(b)) |

Tolerances: none hides an error at the size a wrong formula would produce; the only tolerance below its Monte Carlo error (P2(b)) passes because the bound is loose. I did not loosen any.

## 4. Statements about the study's data and conventions

Verified against the repository (file, leaf):

| Statement in the document | Source | Result |
| --- | --- | --- |
| oracle moments average M = 200 query-noise draws, library fixed (§0.1, A1.6) | `config.n_oracle_draws` 200; `forecast_draws` varies `unit_noise` only; `AnalogLibrary.build` fixes `library_unit_noise` | verified |
| common random numbers across ρ (N8) | `pipeline.unit_noise` keyed without ρ; `experiments.py` sweep comment | verified |
| crossing adds verification noise in quadrature (A1.7) | `characteristic_horizon`: `sqrt(mse + noise²) > theta` | verified |
| θ ≥ 3√2ρ rule (A5.1) | `config.threshold_noise_factor` 4.2426; `admissible_thresholds` | verified |
| ν computed as the trace form (A6.3) | `make_observability` docstring | verified |
| `curvature_floor` counts c < 1e-300 (A1.6) | `excess_mse` docstring; DEV-0 and CONF-1 counters 0 | verified |
| DEV-0 4.5%, 9.7%, 7.7% exceed; max gains 1.7, 3.8, 2.1 LT (A1.8) | `gain_bound` | verified (v1 screen) |
| DEV-0 P2(c): 0 violations in 1,400 states; median N/√B 0.18–0.23; loose by ≈5 (A3.4) | `verification.P2c` | verified (0.182, 0.223, 0.228) |
| DEV-0 75–90% of states switch (N2) | `P2c.n_switching_states` 1047, 1257, 1203 of 1400 | verified (74.8–89.8%) |
| DEV-0 H1c Lorenz-63 0.60 (N5) | `H1c.PLP.median_ratio` 0.601 | verified |
| DEV-0 proxy constant ≈ 0.27 (A6.4) | `fitted.analog_proxy.slope` 0.273, 0.271, 0.268 | verified |
| CONF-1 H2a not supported; (i) fail Rössler, Chua; (ii) interior fail Lorenz-63, Chua (A2.4) | prelim note §4–§5 | verified |
| CONF-1 H1b pass Chua, inconclusive Lorenz-63, fail Rössler (A6.1) | §4 | verified |
| CONF-1 H1c fail Lorenz-63 (N5) | §4 | verified |
| CONF-1 H2e pass all three; H2b(i) pass all three (N4, N8) | §4–§6 | verified |
| CONF-1 Q-N "substantial" (indicator) all three; "reduces" (logit) (N2, A4.4) | §6 | verified |
| V7 and the gate pass on all three (A6.2) | §3 | verified for CONF-1 (unlabelled in the document) |
| labels PRELIMINARY / UNPROMOTED / DEVELOPMENT | header and each use | present at every quoted number I found; the V7 sentence lacks a label |

Cannot be verified from the repository: "293 of 300" (stored: 294, V9); "under a minute on two CPU cores" (no timing, V19); "22–36% w* = 0" is v3 §8's pilot figure, not a DEV-0 reference number (V18).

Contradicts the repository: "22–32% of states have C < 0 at some horizon" (V4); "the v1 form is false" (V2); "no bias" for the p_j-based N̂ (V9, against DEF-0008's definition of the bias).

## 5. Where the theorems' hypotheses are checked numerically (NVVUQ.14)

| Hypothesis | Where checked | Status |
| --- | --- | --- |
| c > 0 (P1(a), P3) | `curvature_floor` counter (c < 1e-300) per cell | 0 in DEV-0 and CONF-1 |
| c ≥ ρ²/k | nowhere (silent) | report-only counter proposed in my 2026-10-19 note; N1 makes it unnecessary for the code |
| raw C ≥ 0 at every horizon (P1(c),(d)) | planned, WU-0002.15 (not built); the present screen is the centered covariance at max(T_C, T_P) | pending |
| raw C ≥ 0 at T_m(√2θ′) (P1(d′)) | nowhere | the decision draft proposes it |
| exponential envelope (P1(d), L8) | H1c (PLP), `growth_nonpositive` screen | H1c: CONF-1 not supported |
| weights independent of the draw (P1(d′) upper bound, P3 plug-in) | not checked; A3–A5 are draw-dependent | my 2026-10-19 note §B.3 |
| P2(a)–(c) | `verification.P2c` | 0 violations (DEV-0) |
| Σc_i > 0 per regime (P3(a)) | `pooled_curvature_floor`, `regime_target_constant` | 0 |
| E[c \| F] > 0 (P3(b)) | not separately; implied by the counters | — |
| L1 remainder small | H1b | CONF-1 not supported |
| L2 Gauss–Markov, Gaussian noise | V2 (CRLB ratio), V7 | pass |
| L3 | unit test (v1 erratum) | — |
| L4 radius | H1d analog seed with Rν̂ | — |
| L8′, L9 | not computed (v1 erratum) | — |
| N1–N8 | none yet | Part C tasks, DEV seeds |

## 6. Files

- This note: `docs/agent/notes/2026-10-21-math-theory-verification.md`.
- Script and log: `docs/agent/notes/2026-10-21-math-theory-verification/verify_wu0027.py`, `verify_wu0027.log` (30/31 items agree; the one "FAIL" is my own search for an N8 sign disagreement, which found none: V7(b)).
- Drafts for the owner, not applied anywhere: `docs/agent/notes/2026-10-21-draft-theorem-program-amendments.md` (C1.2) and `docs/agent/notes/2026-10-21-draft-gain-screen-decision.md` (C1.3).
