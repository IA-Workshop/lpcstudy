# WU-0045 (phase J, J0): mathematics specification, M-1 to M-8

**Every number in this note is DEVELOPMENT (DEV-2): exploratory, not a hypothesis test; prototype, old code c9bb981.** It comes from the R5 DEV-2 full dumps (test split only). No confirmatory seed was drawn, read or used. No CONF-1 number is read or quoted, and nothing here is placed beside CONF-1. These numbers are not carried into the phase J report.

- **Author:** applied-mathematician (claude-opus-5-5), 2026-10-26. Unit WU-0045, plan `docs/agent/notes/2026-10-26-phase-j-lpc-contribution-plan.md` (ledger seq 47). Minimal formality.
- **Inputs read:**
  - the plan;
  - v3 §2, §3, §5 to §8;
  - the WU-0036 note and its script;
  - the WU-0041b note (phase I M-4, M-5, M-6);
  - `analysis.qn_regressor`, `qn_targets`, `qn_profile_block`;
  - `ablation.py`;
  - `allocation.global_weight`, `state_horizon_target`;
  - `oracle.characteristic_horizon`;
  - `statistics.percentile_interval`;
  - `pipeline.score_rules`;
  - `ensemble.EvaluationDraws`, `draw_correlation`.
- **Script and output:** `docs/agent/notes/2026-10-26-phase-j-math-spec/phase_j_checks.py` produces `phase_j_checks.out.md`. It runs on the CPU, one thread, `nice -n 19`, with the project `.venv` and `python -I`, in about 3 minutes.

## Summary of decisions

| Point | Decision |
|---|---|
| M-1 | **Per horizon only, with a separate fit per horizon and H_ref as the headline.** No horizon-averaged MSE: median κ grows 190- to 1400-fold from 0.25 to 4 LT, so 4 LT would dominate any average. A geometric mean of the five per-horizon ratios may be shown as a descriptive summary, with no reading. |
| M-2 | **Fit u with sample weight κ/mean_train(κ),** squared loss, the Q-N hyperparameters, then clip to [0, 1] and count the clips. This is Fisher-consistent for L_A (P3), and κ near 0 or large \|u\| cannot blow it up, because κu² ≤ E_P. **The weights must be normalized**: with `l2_regularization = 1`, raw κ (median 5·10⁻⁴ to 1) shrinks the fit. The real hazard is the heavy tail of κ: n_eff is 7 to 11 at 0.25 LT on Lorenz-63 and Chua. Two consequences: (i) an L_A ratio reading whose reference rule has per-state-excess n_eff < 50 reads "undetermined (n_eff < 50)"; (ii) a second loss L_w (κ ≡ 1, fitted with unit weights) is reported beside L_A. |
| M-3 | **Confirmed: logit u on interior states, and log T.** Two additions. First, the w\* = 0 indicator, and the w\* = 1 indicator wherever w\* = 1 exceeds 5% of test states (DEV-2: 4 LT on all three systems, and 2 LT on Chua), are fitted on the log-odds scale (`HistGradientBoostingClassifier`, log loss). Second, the horizon uses the interpolated crossing time T_c. **Do not report the plain w scale.** Report instead the decision scale (κ-weighted u, L_A) as the secondary row, where R × O is expected to be non-zero because of the link. |
| M-4 | **Quantile boosting on Y = ln min(T_c, H_max)**, with T_c the log-linear interpolated crossing time (⌈T_c⌉ = T). Coverage is exact for every state with q̂ < H_max. A prediction at the cap is undetermined only for a censored state: report it separately, with a bracket. **Harrell's C rule:** event-event tied times are excluded, tied predictions count ½, and an event at H_max against a censored state at H_max is comparable. Under fixed censoring, Harrell's C equals Uno's C truncated at H_max, so it has no censoring bias. |
| M-5 | **The Lyapunov form is well posed as a ranking score only.** T₀ = (30/Λ̃) ln(θ√m/(ρe^{s})), with s the policy's log initial-error seed. On DEV-2, 5% to 17% of states have Λ̃ ≤ 0, and T₀ overpredicts the horizon (median ln(T/T₀) between −0.57 and −0.10). The rung is therefore Harrell's C of T₀ (zero parameters). Its quantile version uses T₀ times training residual quantiles: 6 constants and no fitted function. |
| M-6 | **Keep "at least 4 of 5", and add a rule:** no seed may have a reading that contradicts it. Contradiction means the two readings' bound claims cannot both hold. Three outcomes: replicated, contradicted, not replicated (imprecision is not seed dependence). The false-replication rate is 1.9·10⁻⁶ under independence. If the between-seed SD that the interval omits is 2 times the within-seed SE, the rate is 5.6·10⁻³ (at least 3 of 5 would give 5·10⁻²). The power is 0.74 at a per-seed probability of 0.8. **J5 measures the ratio r of between-seed SD to within-seed SE** on the three exploration seeds before the freeze. |
| M-7 | **Phase I M-4, unchanged.** A failed resample counts as −∞ for the lower bound and +∞ for the upper bound. Both bounds are infinite at F ≥ 50 failures (95%), 17 (1 − 0.05/3), 13 (1 − 0.05/4) or 9 (1 − 0.05/6), with B = 2000. In bootstrap p-values (Holm, family B), a failed resample counts as unfavourable. |
| M-8 | **WU-0036's validation does not carry over.** The bias is 2 Cov_j(w, h) + Cov_j(d², Δ²) over a state's draws. Learned rules on F̂ can track the draw's own window: N̂ is 69% to 78% draw noise and Î 14% to 26%. For a draw-adaptive rule the bias is negative, so the substitution overstates the estimation gap. **Fix:** J1 dumps the per-draw evaluation errors e_C and e_P, and deployable rows use the realized score. Test (f) becomes an exact reconstruction (1e-12) plus a reported bias diagnostic. |

## 0. Theorem and identity checks the plan relies on

| Claim | Status |
|---|---|
| V(w) − V(w\*) = κ[(w − u)² − (w\* − u)²], κ = E_C + E_P − 2C | **correct**: complete the square, V(w) = κ(w − u)² + V(u) |
| For g ∈ [0, 1], fitting u with weight κ is fitting the decision loss | **correct**: Σκ_i(g_i − u_i)² = Σ[V_i(g_i) − V_i(u_i)], and the second sum does not depend on g. Outside [0, 1] the two losses differ, so only the population minimizer coincides (M-2) |
| P3: no rule of F beats clip(E[κu \| F]/E[κ \| F]) | **correct; its hypotheses always hold here.** It needs E[κ \| F] > 0, which holds because κ > 0 almost surely. It needs E[κu²] < ∞, which holds because κu² ≤ E_P (Cauchy–Schwarz: \|E_P − C\| = \|E[e_P(e_P − e_C)]\| ≤ √(E_P κ)), and E_P is bounded since errors are clipped at 10 σ_x |
| P1(a) per state: κ ≥ ρ²/k | **needs a hypothesis: the expectation must include the library noise.** The oracle moments are taken over query-noise draws with the library fixed (`ensemble.draw_correlation` documents CP-constant states). So the copied noise ξ is a fixed realization per state, not a variance ρ². DEV-2 min κ/ρ² = 0.012 (Chua, H_ref). No code depends on it, because the 1e-300 floor is a counted guard. But the docstring of `allocation.pooled_floor_count` ("Under P1(a) every c_i ≥ ρ²/k") is false per state. I flag it for the main session; I do not edit `lpcstudy/` |
| Gain share G = [V(A2) − V(g)]/[V(A2) − V(w\*)] | **identity: G = 1 − L_A(g)/L_A(A2).** It carries no information beyond the ratio to A2. Report it as that ratio's transform, with the same interval and no separate reading |
| Σ_X φ_X = L(∅) − L(F) | **correct**, with value function v(S) = −L(S) (efficiency of the Shapley value) |
| Separation formula: logit w = 2(O − R) | **correct**: w = δ²/(ε² + δ²), with R = ln ε/ρ and O = ln δ/ρ |
| Trees are invariant to monotone transforms of each feature | **correct for HGB**: bins are feature quantiles, so I and ln I give the same fit |
| HGB's constant model is A2 | **correct, with a caveat about the data.** With squared loss and sample weight κ, the initial prediction is Σκu/Σκ, which is A2's unclipped pooled weight on the training rows. The stored A2 pools construction only, and phase J trains on construction + calibration. So the constant rung is "A2 refit on the training rows" |

## M-1. Aggregation across horizons

**Decision: report each horizon separately, with a separate fit per horizon and per profile. H_ref is the headline. Do not average MSE or excess over horizons.**

- **Scale.** The excess scales with κ. Median κ/ρ² (DEV-2) rises from 10.4 to 9551 (Lorenz-63), 5.3 to 1030 (Rössler) and 4.9 to 6989 (Chua) between 0.25 and 4 LT. By median κ, the 4 LT term is 90% to 95% of an arithmetic mean over the five horizons, which would hide everything at 0.25 to 1 LT.
- **Optional summary.** The geometric mean of the five per-horizon ratios, with an interval from the shared resamples. It is scale-free and gives each horizon equal weight. It has no reading.
- **Multiplicity.** No adjustment across horizons: these are estimates. Holm families stay per system, decision, profile and horizon, as the plan says.

## M-2. The allocation fitting target

**Decision.** For A, C and D, the primary target is u with sample weight κ_i / mean_train(κ), under squared loss, with `qn_regressor`'s hyperparameters unchanged. Predictions are clipped to [0, 1], and `n_pred_clipped` is counted per row.

**Why κ-weighted u is sound**

- **Consistency.** For each F, the population minimizer of E[κ(g − u)² | F] is m(F) = E[κu | F]/E[κ | F]. Clipped, it is the P3 optimum, which is the minimizer of L_A among rules of F. The fit is therefore Fisher-consistent for L_A.
- **No other target is.**
  - Q-N's two-part logit composition ignores κ and drops the w\* = 1 states, so it estimates a different functional.
  - A custom logistic-link model has no sklearn HGB loss hook, and it is not needed.
  - Neither is used for A, C or D. The logit scale is kept for B (M-3).

**κ near 0.** It occurs (DEV-2 min κ/ρ² = 0.012; see §0, P1(a)), and it is harmless.

- **Bounded terms.** κu = E_P − C and κu² ≤ E_P. So a state's loss term κ(g − u)² ≤ 2κ + 2E_P and its gradient κ(g − u) are bounded by its moments, however small κ is.
- **Little weight.** A state with small κ contributes little, which is correct: its V is flat in w.
- **No handling needed.** Nothing needs a floor or an exclusion, beyond the existing counted 1e-300 guard.

**Very large |u|.** It cannot occur together with a non-negligible κ.

- **The bound.** \|u\| ≤ √(E_P/κ) and \|1 − u\| ≤ √(E_C/κ). So a large \|u\| needs κ ≪ E_P: the two errors must be nearly equal draw by draw.
- **On DEV-2.** max \|u\| = 1.91 over all 15 system-horizon cells.
- **The only cost is efficiency.** 15% to 30% of states have u < 0, and up to 12% have u > 1 at 4 LT. There the regression spends capacity on values that clipping makes equivalent. This costs efficiency, not consistency.

**Weight normalization is required, not cosmetic.**

- **Mechanism.** HGB's leaf value is −Σg/(Σh + λ), where h is the sample weight under squared loss, and `l2_regularization = 1.0`.
- **Effect on a synthetic fit.** Uniform weights of 1, 10⁻², 10⁻³ and 10⁻⁴ give in-sample R² of 0.980, 0.977, 0.968 and 0.828.
- **Consequence.** Raw κ (median 5·10⁻⁴ to 1 in these units) would make the shrinkage depend on the system and the horizon. Dividing by the training mean makes λ = 1 mean "one average state", as in Q-N.

**The real hazard is the heavy tail of κ.**

- **How heavy** (DEV-2):
  - n_eff(κ) = (Σκ)²/Σκ² on 1000 test states is 11.0 (Lorenz-63) and 7.1 (Chua) at 0.25 LT, and 51 and 48 at H_ref;
  - the top 1% of states hold 65% and 81% of Σκ at 0.25 LT;
  - the n_eff of the per-state excess of the constant rule is 7.4 and 7.7 at 0.25 LT, and 33.5 and 11.8 at H_ref;
  - Rössler is 73 to 206 throughout.
- **Meaning.** At short horizons, Lorenz-63's and Chua's mean excess MSE is a property of about ten states (large-PLP-error states, consistent with wrong-basin estimates).
- **Prototype cross-fit.** The κ-weighted fit was worse than the constant in Chua at H_ref (ratio 1.29) and on all three systems at 4 LT (1.11 to 1.27). This used 5 contiguous folds of the test split and 800 training states, a quarter of J3's size.

**Rules.** Both tighten; neither loosens.

1. **Effective-size guard.** Each L_A row reports n_eff of the per-state excess of its reference rule (the ratio's denominator). A ratio reading with n_eff < 50 reads "undetermined (n_eff < 50)". This is the analogue of the v3 50-state rule. A block bootstrap of a mean carried by fewer than about 50 effective states undercovers, and about 37% of resamples miss any given block.
2. **A second loss.** L_w = mean_i[(g_i − u_i)² − (w\*_i − u_i)²] is the excess in weight units, with every state counting once. It is fitted with unit weights on u, which is consistent for L_w by the same argument with κ ≡ 1. It is reported beside L_A, with the same subsets, ratios and resamples. L_A answers "how much MSE", and L_w answers "how accurate is the weight on a typical state".
3. **The theory gap is an upper bound.** L_A(oracle F) is the P3 floor *plus* the learner's estimation error. The plan's "theory gap" should be worded as an upper bound. A learned row worse than the constant reads "the learner does not beat the constant at this training size". It is not evidence that a condition carries no information.

## M-3. Scales for the interaction tests

**Decision: confirmed, with three additions.**

1. **Allocation, primary.** The target is logit u on interior test states (0 < w\* < 1), fitted by the Q-N regressor with `interaction_cst`.
   - **Indicator parts.** The w\* = 0 indicator, and the w\* = 1 indicator wherever w\* = 1 exceeds 5% of test states (the H2a(ii) rule), are fitted by `HistGradientBoostingClassifier` (log loss, the Q-N hyperparameters otherwise) and scored by test log loss. An additive model is then additive on the log-odds scale. Squared loss on a 0/1 target would be additive on the probability scale, and would create link interactions there.
   - **DEV-2 shares.** w\* = 1 is 12.1%, 7.6% and 10.3% at 4 LT, and 5.3% for Chua at 2 LT. So the third part is needed.
2. **Why logit.** Under separation, logit w = 2(O − R). This is exactly additive, so the mixed partial in (R, O) is 0. On the w scale, ∂²w/∂R∂O = −4w(1 − w)(1 − 2w). At w = 0.1 this is −0.29, against a main-effect slope ∂w/∂O = 0.18: the link alone makes R × O look large.
3. **Do not report the plain w scale.** Unweighted squared error on w is neither the theory's additive scale nor the decision loss, so a row on it has no interpretation. **Report instead the decision scale** as the secondary row: κ-weighted u, scored by L_A, with the same `interaction_cst` comparison. It answers "does the interaction matter for the MSE". Its R × O row is expected to be positive through the link, and it is not evidence against separation.
4. **Horizon.** The target is ln T_c (M-4), with a median (τ = 0.5) quantile model with `interaction_cst`, scored by pinball loss on the log scale. Censoring is at most 0.4% of states on DEV-2.

**Statistic and multiplicity for B.** Δ_XY = L(M_add) − L(M_XY) on the test states, with the models fixed.

- **p-value.** p = (1 + #{b : Δ\*_b ≤ 0 or failed})/(B + 1).
- **Holm.** At 5% over the 6 pairs; R × I and O × I are named primary in advance.
- **Size.** The ratio L(M_add)/L(M_XY) is read by the 1.05 table at level 1 − 0.05/6.
- **Null behaviour.** Under an additive truth, the fixed-model gain is ≤ 0 in expectation, because the pair model can only overfit. So the test is conservative, like Q-N's ΔR².

## M-4. Horizon quantiles under fixed censoring at H_max = 240

**Target.** Define the crossing time by log-linear interpolation of the r.m.s. curve e_H = √(mse_H + ρ²) between the last step below θ and the first above:

T_c = T − 1 + (ln θ − ln e_{T−1})/(ln e_T − ln e_{T−1}), so ⌈T_c⌉ = T.

- **Edge cases.** T = 1 gives T_c = 1 (counted). e_{T−1} = θ exactly gives T_c = T − 1 (counted). Censored states keep T_c > H_max.
- **Why.** T is an integer with 154 to 181 distinct values and a largest atom of 1.7% to 2.6% (DEV-2). With an integer target, a calibrated quantile's coverage can deviate from τ by up to the conditional atom mass, which is a few points. T_c removes the atoms. The WU-0039b cross-check keeps integer T.
- **Fit and score.**
  - Fit HGB with `loss="quantile"` on Y = ln min(T_c, H_max), one model per τ ∈ {0.1, 0.5, 0.9}.
  - The pinball loss on Y is a proper score for the quantiles of min(T, H_max), which equal min(q_τ(T), H_max). It is exactly computable for every state.
  - Rearrange the three predictions monotonically per state (sort), and count the crossings.
  - Cap predictions at ln H_max, and count the caps.

**Coverage.**

- **Exact below the cap.** For q̂ < H_max, 1{T ≤ q̂} is known for every state: an event has T observed, and a censored state has T > H_max > q̂, so its indicator is 0. **This confirms the plan's DS-4.**
- **At the cap,** the indicator is 1 for an event, and unknown for a censored state.
- **Report:**
  - coverage over the states with q̂ < H_max. This is a legitimate conditional coverage, because q̂ is a function of F;
  - the number of states at the cap;
  - the all-state bracket, with unknowns set to 0 and to 1. On DEV-2 its width is at most 0.4% for the oracle-hybrid target.
- **80% interval:** P(q̂₀.₁ < T ≤ q̂₀.₉).
- **False trust in C3:** P(T ≤ q̂₀.₁), written "≤" to match coverage. With continuous T_c, "<" and "≤" agree almost surely.

**Harrell's C.** The score is q̂₀.₅ (higher means a longer horizon).

- **Comparable pairs:**
  - i an event and T_i < T_j;
  - or T_i = T_j = H_max with i an event and j censored (a censored state lies beyond H_max).
- **Excluded:** event-event pairs with tied times (counted), and censored-censored pairs.
- **Tied predictions** count ½.
- **No censoring bias.** With administrative censoring at one fixed time, the censoring survival is G ≡ 1 on [0, H_max). So Harrell's C equals Uno's C truncated at H_max. It estimates P(q̂_i < q̂_j | T_i < T_j, T_i ≤ H_max).
- **Checked.** The script's vectorized form equals a brute-force double loop to 1e-12. That is test (e)'s reference.

## M-5. A zero-parameter horizon baseline

**The form.**

- **Formula.** T₀ = (30/Λ̃) ln(θ√m/e₀): v3's cited horizon law, with m = 3 and e₀ = ρe^{s}.
- **The seed term.** s_w = ½ ln(w²e^{2R} + (1 − w)²e^{2O}) for a policy with CP weight w at H_ref, assuming uncorrelated seeds. For the oracle hybrid, w is the separation weight p = δ²/(ε² + δ²), and s = −½ ln(e^{−2R} + e^{−2O}), the soft-minimum of R and O.

**Well posed as a ranking score only** (DEV-2):

- **Undefined for many states.** Λ̃ ≤ 0 for 148, 50 and 169 of 1000 states (Lorenz-63, Rössler, Chua), where the form is undefined.
- **Biased.** Median ln(T/T₀) is −0.57, −0.10 and −0.24, with IQR 1.06, 0.58 and 1.04. This is consistent with the local 1-LT rate understating the growth over the horizon, whose median T is 2.4 to 3.4 LT (the DEV-2 H1c PLP medians are 0.58, 0.97 and 0.74).
- **Harrell's C:**
  - T₀: 0.61, 0.66, 0.69;
  - 1/Λ̃ alone: 0.61, 0.64, 0.68;
  - the seed term −s alone: 0.49, 0.58, 0.61.

**Decision: two rungs.**

- **(i) "Lyapunov rank":** Harrell's C of T₀, with Λ̃ ≤ 0 ranked as +∞ (ties ½). It has zero parameters.
- **(ii) "Lyapunov quantile":** q_τ = T₀·exp(Q_τ^train[ln T_c − ln T₀]) on Λ̃ > 0, and the training quantiles of T_c on Λ̃ ≤ 0. That is 6 constants and no fitted function of F. It is the horizon analogue of the separation formula.

## M-6. The replication rule over 5 held-out seeds

**Rule (fixed at J6).** A reading is **replicated** if two conditions hold:

- the same reading occurs on at least 4 of the 5 replication seeds;
- no seed's reading contradicts it, where two readings contradict iff their bound claims are jointly unsatisfiable. For example, "lowers" (upper < 1) contradicts any reading with lower > 1, and "negligible" (upper ≤ 1.05) contradicts "substantial" (lower > 1.05).

The other outcomes:

- **Contradicted:** at least one pair of seeds has contradicting readings. This is the plan's "seed-dependent".
- **Not replicated:** otherwise, typically through imprecision.
- **Claim-level fallback.** If a reading is not replicated, report any weaker bound claim (for example "lower > 1") that holds on at least 4 of 5 seeds with no contradiction, as "replicated claim".

**Error rates under independence.** Given the system and the frozen script, the seeds' inputs are independent and identically distributed (WU-0041b M-1, hypothesis (I)). P(at least 4 of 5) = 5p⁴(1 − p) + p⁵.

| per-seed p | 0.025 | 0.063 | 0.1 | 0.2 | 0.5 | 0.8 | 0.9 | 0.95 |
|---|---|---|---|---|---|---|---|---|
| at least 4 of 5 | 1.9e-6 | 7.5e-5 | 4.6e-4 | 6.7e-3 | 0.19 | 0.74 | 0.92 | 0.98 |
| at least 3 of 5 | 1.5e-4 | 2.3e-3 | 8.6e-3 | 0.058 | 0.50 | 0.94 | 0.99 | 1.00 |

- **False replication.** A one-sided miss of a 95% interval has p = 0.025, which gives 1.9·10⁻⁶. But the interval holds the fitted models fixed, so it omits training variance and between-seed variation.
- **With omitted variation.** If that variation has SD r times the within-seed SE, the per-seed false-claim probability is p = Φ(−1.96/√(1 + r²)):

  | r | 0.8 | 1 | 1.5 | 2 |
  |---|---|---|---|---|
  | p | 0.063 | 0.083 | 0.14 | 0.19 |
  | P(at least 4 of 5) | 7.5·10⁻⁵ | 2.2·10⁻⁴ | 1.6·10⁻³ | 5.6·10⁻³ |
  | P(at least 3 of 5) | 2.3·10⁻³ | 5·10⁻³ | 2.1·10⁻² | 5.1·10⁻² |

  "At least 4 of 5" is robust to r ≤ 2; "at least 3 of 5" is not.
- **Power.** 0.74 for a reading with per-seed probability 0.8, and 0.92 at 0.9.
- **Multiplicity.** With N null rows, the expected number of false replications is N times the rate. At r = 2 and N = 1000, that is about 6. **So J5 measures r**: the SD of each headline row's point estimate over DEV-1, DEV-3 and DEV-4, divided by its mean bootstrap SE (2 degrees of freedom, crude). J6 states the median r beside the rule. If r > 2, the J7 report gives the expected false-replication count, and the rule itself is not changed.

## M-7. Failed resamples in estimate rows

**Decision: phase I M-4 (WU-0041b §4), unchanged.**

- **The rule.** `statistics.percentile_interval` treats a failed value as −∞ for the lower bound and +∞ for the upper. Both bounds become infinite at F ≥ ⌊(B − 1)a⌋ + 1 failures. With B = 2000, that is **50 at 95%, 17 at 1 − 0.05/3, 13 at 1 − 0.05/4 and 9 at 1 − 0.05/6**. The row then reads "undetermined (failed resamples ≥ threshold)", and the count is in every row.
- **Why it suits estimate rows.** Widening can only remove a bound claim, never create one, so this is the unfavourable direction for every reading, even with no pass or fail.
- **Bootstrap p-values (B).** A failed resample counts in the numerator, as if Δ\* ≤ 0.
- **Sources of failure, each counted per row:**
  - an empty interior set or a constant indicator in a resample;
  - a non-positive denominator in a ratio. The moment-form L_A is > 0 almost surely, but the realized-score excess of a deployable row (M-8) is a difference S − V(w\*), so a resample mean ≤ 0 is possible: it is a failed resample;
  - no comparable pair in Harrell's C.

## M-8. The deployable V(w) substitution for learned weights

**WU-0036 does not carry over automatically.**

**The bias, per state.** Write the weight on draw j as w_j = w̄ + d_j, with Δ = e_C − e_P and the per-draw half-gradient h_j = (e_P + w̄Δ)Δ. Expanding q(w, e) = (e_P + wΔ)² about w̄ gives

E[S_i] − E[Q_i] = 2 Cov_j(d_j, h_j) + Cov_j(d_j², Δ_j²),

so \|bias_i\| ≤ 2 SD_j(w)·SD_j(h) + SD_j(d²)·SD_j(Δ²).

- **Size.** It scales with how much the rule's weight moves across a state's own draws, and how well that movement tracks the draw's own loss gradient.
- **What WU-0036 covered.** WU-0036 validated A4: its weight depends on the draw through R̂ only, with draw-SD 0.03 to 0.05 (DEV-2). Its power was low: paired relative tolerances were 9% to 26%.
- **Why learned rules on F̂ are different.** They can lean on coordinates that are mostly draw noise. The within-state share of total SD (DEV-2) is:
  - N̂: 0.69 to 0.78;
  - R̂: 0.25 to 0.38;
  - Î: 0.14 to 0.26;
  - Ô: 0.02 to 0.13.

  Λ̂ and ν̂ are evaluated at the draw's own estimate ŝ, so a wrong-basin draw moves them.
- **Sign.** For a rule that uses this well (less CP weight on draws where CP is worse), Cov(d, h) < 0, so the realized MSE is *below* the substituted one. The substitution therefore **overstates the estimation gap** and understates deployable rules, by a different amount for each rule.
- **Stored rules on DEV-2,** WU-0036 construction at H_ref (`phase_j_checks.out.md`, M-8):
  - A3's weight barely moves across draws (SD 0.004 to 0.007), and A5's moves 0.010 to 0.061;
  - every \|z\| ≤ 1.97 in the paired form;
  - paired relative D is −0.11 and −0.13 for Lorenz-63 A3 and A5, on the predicted side but not significant (relative tolerances 0.29 and 0.36).

  So a stored learned rule passes, but at a power that cannot see a bias of the size of the 1.05 margin.

**Decision: a tighter check, which removes the substitution where it is uncertain.**

1. **WU-0046 (J1) dumps the per-draw evaluation errors** `cp_err` and `plp_err`, against the noise-free truth, for the test and calibration splits, at the five evaluation horizons. That is shape (n, E, 5) per split; the full grid is optional. They exist in memory in `pipeline.score_rules` (`ev.cp_err`, `ev.plp_err`, shape (n, E, nH)).
2. **Deployable-profile rows use the realized score** S_i(g) = (1/E) Σ_j (g_ij e_C,ij + (1 − g_ij) e_P,ij)². This is the deployment estimand, with no dependence bias.
   - The excess is S_i(g) − V_i(w\*_i), which is unbiased for the deployment excess. A single state's value can be negative; a resample whose mean excess is ≤ 0 in a ratio's denominator is failed and counted (M-7).
   - Comparisons between deployable rules share the draws, so the realized noise largely cancels (WU-0036's paired finding).
   - The V-substituted value is reported beside it as a lower-variance secondary.
3. **Oracle-profile rows keep the moment form.** There the weight does not depend on any draw, so (H2) holds exactly, and the only error is the oracle Monte Carlo error (§U).
4. **Test (f) is rewritten:**
   - **(f1) Exact.** Recompute `state_mse/<rule>` for A0, A1, A2, A3 and A4 at all five evaluation horizons, and A5 at H_ref, from the dumped per-draw errors and weights. Each must match to 1e-12 relative.
   - **(f2) Reported, not gating.** For every deployable rule in the report, give the dependence bias mean_i(S_i − Q_i), direct and paired with A1. Use WU-0036's half-draw SE and z at every scored horizon, and its relative size against the 1.05 margin.

   If J1 cannot add the errors, the fallback is the substitution with (f2) computed for the stored rules only. Every deployable row is then labelled "substitution, dependence bias not bounded". In that case, the plan's (f) as written ("the full-profile ĝ passes") cannot be executed, because no realized score exists for ĝ.

## Refined predictions (§4)

Theory-derived. Where a DEV-2 diagnostic was seen before writing, it is named. The plan's own predictions stand unless changed here.

**A, allocation.**

- **A correction to §1.3 and §4.B.** First-order anisotropic amplification gives logit u = 2(O − R) + m(H; seed directions). If m depends on the state through Λ̃, this is an **additive main effect of I**, not an R × I or O × I interaction. The direct test of the student's H2a reading is therefore **A's drop-I (and φ_I) on the logit target given {R, O}**, the nonparametric analogue of H2a(ii). B's pairs test a second-order claim.
- **Few-state-dominated rows.** At 0.25 to 0.5 LT on Lorenz-63 and Chua, expect most L_A rows to read "undetermined (n_eff < 50)" (DEV-2 n_eff 7 to 26). The informative rows there are L_w.
- **The separation formula against A2.** The formula ignores the horizon. In saturation, E_C/E_P → 1 and the error correlation rises. On DEV-2, the ratio of median E_C to median E_P is 4.6 to 10 at 0.25 to 2 LT and 0.63 to 1.34 at 4 LT, and the median of C/√(E_C E_P) rises from 0.12–0.21 at ≤ 1 LT to 0.30–0.33 at 4 LT. So **the formula's ratio to A2 rises with the horizon and exceeds 1 at 4 LT.** I saw this in the DEV-2 prototype cross-fit (1.16 to 1.30) before writing it.

**A, horizon.** In the Lyapunov form, ∂ln T/∂R = −p/L′, ∂ln T/∂O = −(1 − p)/L′ and ∂ln T/∂ln Λ̃ = −1, with L′ = ln(θ√m/e₀) and p the CP weight. On DEV-2, median L′ is 2.7 to 3.5, and median p is 0.09 to 0.15 (IQR 0.04 to 0.29).

- **Prediction:** I is largest. O is second. **R's direct effect is p/(1 − p) of O's: median 0.10 to 0.17, IQR 0.04 to 0.41.** It can still have a non-zero Shapley share through its correlation with O and I.
- **This sharpens the plan's** "R and O add through the initial error". The DEV-2 C of the seed term alone (0.49 to 0.61) was seen.

**B, allocation (logit scale).**

- **R × O** is zero to first order at every horizon, and small at 0.25 to 2 LT. It may appear at 4 LT, where the correlation C enters both ln(E_P − C) and ln(E_C − C).
- **R × I and O × I** are zero to first order. There are two second-order sources:
  - (i) the CP noise floor (the fixed copied noise ξ, of order ρ²) at 0.25 to 0.5 LT, which gives R × I mainly for low-R states;
  - (ii) error saturation at 4 LT, which gives both pairs.

  **Expect a U shape in the horizon, smallest near 1 to 2 LT.** This replaces the plan's "small at 0.25 LT" for R × I.
- **A detection at 1 to 2 LT** would be evidence that seed direction and seed magnitude are coupled through the state (for example, O × I through the observability geometry), beyond first-order theory.

**B, horizon (log scale).**

- **R × O:** small, but the only pair that is non-zero in the Lyapunov form. Its mixed partial is −p(1 − p)(2L′ + 1)/L′², about −0.08 at the DEV-2 medians, from the soft-minimum's curvature. The O main effect is −(1 − p)/L′ ≈ −0.28.
- **R × I and O × I:** zero in the Lyapunov form on Λ̃ > 0. Departures are expected from two sources:
  - (i) the states with Λ̃ ≤ 0 (5% to 17% on DEV-2), where the form breaks;
  - (ii) finite-time averaging of the growth rate, since Λ̃ covers 1 LT while the median T is 2.4 to 3.4 LT. The expected sign: the effect of Λ̃ weakens for long-T (small-seed) states.

  So the plan's "all pairs small" should read: "**no pair is zero by construction; the I-pairs are zero only in the first-order form**".

**C2, shared information: the plan's prediction is replaced.**

- **Under separation.** Every ĝ(F) output is a function of R − O, while ln T depends on (s ≈ O, Λ̃). The forward bottleneck therefore loses I and most of O, and keeps only what R − O carries through its correlation with them. The reverse bottleneck ĥ(F) ≈ f(O, I) loses R, so it cannot rebuild R − O.
- **Prediction:** both bottlenecks lose most of their skill. The forward one keeps more at 4 LT, where saturation makes w\*(4 LT) depend on Λ̃.
- **Interpretation.** Retained horizon skill in the forward bottleneck *measures how much I enters w\*(H)*, so C2 is a second view of the H2a departure.

**D.** "Theory gap" becomes an upper bound (M-2 rule 3). With realized scores (M-8), the estimation gap no longer carries the substitution's upward bias.

**E-H2a.** m(H) = ln[E_C(H)/E_C(H₀)] − ln[E_P(H)/E_P(H₀)] is non-zero under isotropic separation for two reasons:

- the CP floor ξ² does not amplify, so m < 0 at short horizons;
- saturation drives E_C/E_P → 1 at long horizons.

Use H₀ = 1 LT, not 1 step: at 0.25 LT the median E_C is only 5 to 10 ρ². Restrict to horizons where both r.m.s. errors are ≤ 0.5 σ_x, as in H2a(i).

## Changes to acceptance criteria

All of these tighten or add; none loosens.

- **WU-0046 (J1), add (vi).** Dump per-draw `cp_err` and `plp_err` (test, calibration; five evaluation horizons). Recomputing `state_mse/<rule>` from them and the dumped weights reproduces the stored values to 1e-12 relative (A0 to A4 at all evaluation horizons, A5 at H_ref).
- **WU-0046 (J1), optional.** Add half-draw (A/B) full-grid moments for the test split. Without them, the oracle Monte Carlo error of T_c is "not estimated" in the budget.
- **WU-0048 (a):** unchanged.
- **WU-0048, new (a′).** Weighted HGB with weights κ/mean(κ) has as its initial prediction the κ-weighted mean of u, equal to 1e-12 relative to Σκu/Σκ.
- **WU-0048 (c):** "within the bootstrap null band" means that for every pair the Holm-adjusted p > 0.05 and the upper bound of Δ is ≥ 0. A planted X × Y term is detected (Holm p ≤ 0.05) and no other pair is. The synthetic sizes and seeds are fixed in the test.
- **WU-0048 (d).** Plug in the *true* conditional quantiles of a synthetic T with fixed censoring. Each τ's coverage is within 4√(τ(1 − τ)/n) of τ. A planted state set with q ≥ H_max exercises the cap rule and the bracket.
- **WU-0048 (e):** equality with a brute-force count, to 1e-12, under the rule of M-4, including tied times, tied predictions and event-at-H_max against censored pairs.
- **WU-0048 (f):** replaced by (f1) and (f2) of M-8.
- **WU-0049, add.** T − 1 ≤ T_c ≤ T, and ⌈T_c⌉ equals `characteristic_horizon` exactly on hand-built and dumped curves. T_c = T − 1 only where e_{T−1} = θ exactly, which is counted.

## U. Uncertainty budget (QoI: an L_A ratio at H_ref, per system and seed)

| Source | Type | How estimated | Size (DEV-2) | In the interval? |
|---|---|---|---|---|
| Sampling of test states | aleatory | paired moving-block bootstrap (block 5, 2000) | the row's half-width | yes |
| Effective size of the mean | estimator | n_eff of the reference rule's per-state excess | 7 to 467 | no; n_eff < 50 reads "undetermined" (M-2) |
| Oracle Monte Carlo (M = 200): w\* estimated from the same moments | numerical | κ(w\*_A − w\*_B)²/4 per state, from the halves | 0.2% to 2.1% of the constant rule's excess; it pulls ratios towards 1 | no; reported per row, and flagged when it exceeds a tenth of the half-width |
| Dependence bias of the V substitution (deployable rows) | estimator | (f2), M-8 | not significant for the stored rules; power is low | removed by the realized score (M-8) |
| Training variance of the fitted models | aleatory | between-seed spread (J5, ratio r) | not estimated yet | no; enters only through replication (M-6) |
| Bootstrap Monte Carlo error | numerical | `endpoint_mc_error` | per row | no; must be below a tenth of the half-width, or flagged |
| Discretization (RK4), Levenberg–Marquardt | numerical | inherited from V6 and the LM summaries | not re-estimated | no |
| Model form: three systems, ρ = 1% core cell, scalar observable | epistemic | not estimated | — | no |

The interval level is per family (M-3, M-7), and the dependence assumption is block stationarity with blocks of 5. Seed: DEV-2 for every number here. For the horizon QoIs (pinball loss, C, coverage), the same rows apply, with the oracle Monte Carlo error of T_c "not estimated" unless J1 dumps the full-grid halves.

## Addendum (WU-0045b, 2026-10-26): rulings on three WU-0048 points

**DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.** The inputs are the phase J DEV-1 full run (run commit f701a47, schema /3) and the WU-0048 analysis code at 108d7d5. The diagnostics are `2026-10-26-phase-j-math-spec/rulings_0045b.py`, with output in `rulings_0045b.out.md` (CPU, one thread). This addendum supersedes the text above where they differ.

### R1. Test (c), the additive null: the criterion I gave was mis-specified

- **The fault.** I wrote that under an additive truth the fixed-model gain Δ = L(M_add) − L(M_XY) is ≤ 0 in expectation, because the pair model can only overfit. I then asked, as part of the null criterion, for every upper bound of Δ to be ≥ 0. These two statements contradict each other. The overfitting penalty is a real, non-zero quantity. With 1000 test states and the models held fixed, the interval can exclude 0 from above. That is what happened for R × O: Δ = −0.0110 [−0.0212, −0.0016].
- **The upper-bound condition controls no error rate.** It fails more often the larger the pair model's overfit, and that is not a defect of the statistic.
- **Corrected criterion (c), null.** For each of the 6 pairs, the Holm-adjusted p is > 0.05. Equivalently, no pair is detected, and no claim "gain > 0" is made.
  - **Error rate.** The null hypothesis is the one-sided, composite E[Δ] ≤ 0. Holm on the one-sided bootstrap p-values keeps the family-wise false-detection rate ≤ 0.05, approximately, since bootstrap p-values are approximate. It is conservative when E[Δ] < 0.
  - **For the test.** This is one fixed-seed check, so its probability of a spurious failure is ≤ 0.05. The observed smallest Holm p is 0.144.
  - **The planted part is unchanged.**
- **A significantly negative Δ is not a defect, and needs no fix.**
  - **No stricter inner CV.** The inner cross-validation chose each model's setting by its own decision loss, as designed. A stricter grid for the pair model only would be a different rule for one model.
  - **No training variance in the interval.** The intervals hold the models fixed by design (plan §3.4). Training variance enters through replication.
  - **The cost is power, not error.** A true interaction is detected only if its gain exceeds the pair model's overfitting penalty. The J5 report should state this.
- **Reading of a B row with upper bound < 0** (MSE-ratio upper bound < 1): "no interaction gain; the pair model fits worse". It is not a claim of a negative interaction. For M-6, it does not contradict "no interaction".

### R2. The n_eff guard for deployable rows: use the substituted excess

- **The fault.** For realized scores, x_i = S_i − V_i(w\*_i) = E[x_i] + η_i, where η_i is draw noise with mean zero that is independent across states. So (Σx)²/Σx² estimates n·mean²/(mean² + var(η)), a signal-to-noise ratio, not concentration. On DEV-1 its value was 0.6 to 75 for A4 and 27 for the learned rules at Rössler 0.27 LT, where Kish(κ) is 269.
- **What the guard is for.** It targets the concentration of the estimand's per-state contributions E[x_i]. Draw noise is resampled by the bootstrap, and its heavy tail lies on the large-κ states that Kish(κ) already covers.
- **Ruling.** For deployable rows, n_eff = min(Kish(κ), Kish(x̃)), where x̃_i = (1/E) Σ_j V_i(g_ij) − V_i(w\*_i) ≥ 0 is the substituted (moment-form) excess of the row's reference rule. This is the oracle-row definition applied to the deployable weights. x̃_i estimates E[x_i] up to the dependence bias, which (f2) reports.
  - The same quantity replaces `n_eff_constant_excess` in the deployable blocks.
  - The reading is still made on the realized MSE ratio (M-8). Only the guard changes.
- **Rejected alternatives.**
  - **\|x\|** measures noise magnitude. On DEV-1 its Kish size exceeds the substituted one by up to 2× (Rössler 0.27 LT: 306 against 143), and it falls below it elsewhere (Chua 1 LT: 13.7 against 26.4).
  - **Kish(κ) alone** ignores the rule. A rule's excess can concentrate where κ does not: Chua 0.27 LT A4 gives 5.1 against Kish(κ) 19.4.
- **Effect on DEV-1.** At Rössler 0.27 LT, Kish(x̃) is 52 to 57 for the learned RON and ROIN rules and 143 for A4. Those rows become readable. Chua 0.27 LT stays undetermined (4.0 to 5.1), correctly, because one state there has κ 269 times the median.

### R3. (f2) on DEV-1, Chua 0.27 LT, RON at z = 6.4: noise in one state, not a dependence bias

- **Exact decomposition.** With w = w̄ + d over a state's draws, Δ = e_C − e_P, a = e_P Δ − (C − E_P) and b = Δ² − κ, the paired D_i − D_i(A1) = T0 + T1 + T2:
  - T0 = mean_j(2w̄a + w̄²b), the realized noise at the draw-mean weight, approximately mean zero;
  - T1 = mean_j 2d(a + w̄b), the 2 Cov(d, h) term;
  - T2 = mean_j d²b, the Cov(d², Δ²) term.

  This is an algebraic identity, checked per state to 1e-9.
- **Size of each term for RON,** in units of the rule's mean V:
  - total +0.080: T0 +0.064, T1 +0.016, T2 +0.0006;
  - one state (index 4) carries +0.052 of the total. Its RON weight does not vary across draws (draw-SD 0), so it has no dependence term at all: its contribution is pure realized-draw noise on a state with κ 269 times the median;
  - five states carry 81% of the total.
- **Why z is 6.4.** The half-draw SE has one degree of freedom per state, and Kish(κ) is 19. It therefore underestimates the SE when one state dominates. This is the WU-0036 §2.5 caveat, here larger.
- **The dependence part, T1 + T2 = +0.017 of V, is consistent with the derivation.**
  - T2 is negligible.
  - T1 is positive, meaning that RON shifts weight towards CP on draws where that hurts. The derivation leaves this sign open. My M-8 statement that the bias is negative held only "for a rule that uses this well": a rule whose draw-level weight changes track the draw's own loss gradient. The learned rules are trained on state-level targets u_i with per-draw inputs, so nothing makes them track the draw's own errors.
  - **Correction to M-8 and the summary table:** delete "the substitution overstates the estimation gap" as a general claim. The sign of the dependence bias is not determined a priori, and (f2) measures it.
  - A4 shows the same sign (T1 +0.015).
- **What changes.**
  1. M-8's decision is reinforced. Deployable rows already use realized scores, so no reading depends on the substitution.
  2. (f2) adds the decomposition. It reports mean(T1 + T2) as the dependence-bias estimate, with a paired moving-block bootstrap interval over test states (block 5), beside WU-0036's z.
     - The WU-0036 z, on the half-draw SE, is kept as a secondary column. A row with \|z\| > 4 whose T1 + T2 interval contains 0 reads "realized-noise outlier, no detectable dependence bias".
     - (f2) remains reported, not gating.

## Addendum (WU-0045c, 2026-10-26): M-6 tool semantics (before the freeze)

These rulings are on the semantics of `tools/lpc_replicate.py` (WU-0051b) and of `lpcstudy.mechanisms`. They are made before any held-out seed (DEV-5 to DEV-9) has been read, and no number is used. They govern the tool and the E readings from the freeze on.

### S1. Non-detections can never be replicated

**Confirmed.**

- **Why.** A non-detection ("no interaction gain detected", "no difference detected", "no detectable dependence bias", and every "not determined") is the absence of a bound claim. Low power produces it on every seed with probability near 1. Counting it toward "at least 4 of 5" would turn imprecision into a replicated null.
- **What a replicable null needs.** An equivalence claim: an interval inside a margin fixed in advance. The vocabulary has three:
  - the ratio rows' "negligible" (ratio ≤ 1.05), which covers A, the B loss ratio, D and the horizon ratios;
  - E-H2a "not consistent" (−0.1 < Spearman < 0.1 at every usable H; S2);
  - C2 "loses most" (retained < the retain level).
- **No new margins.** None is added for C2's oracle-against-deployable difference or for (f2). Their nulls stay non-replicable, and J7 says so in one line.
- **Claim-set change:** none.

### S2. E-H2a: "consistent" and "not consistent" should contradict

- **The fault.** The two words are not mutually exclusive in truth. A true Spearman in (0, 0.1) satisfies both, so a seed split between them is not evidence of seed dependence. The fault is in the reading, not in the tool. "Consistent" only asked the interval to exclude 0, while "not consistent" uses the margin 0.1. An association smaller than the margin the null reading calls negligible should not count as supporting the mechanism.
- **Corrected reading** (`mechanisms.h2a_reading`). A horizon *supports* the mechanism iff two conditions hold:
  - its Spearman(m, I) interval lies beyond the margin on one side: lower > NEAR_ZERO, or upper < −NEAR_ZERO;
  - the drift condition holds as now.

  The "not consistent" rule is unchanged, and so is the "not determined" rule (otherwise). This tightens "consistent"; nothing is loosened. The exploration readings must be regenerated before the freeze.
- **Corrected claim sets:**
  - **consistent:** at each supporting H, either `Spearman(m, I)@H > 0.1` (interval) or `Spearman(m, I)@H < -0.1` (interval), whichever side established it, plus `drift high - low I@H > 0` (point);
  - **not consistent:** at each usable H, `Spearman(m, I)@H > -0.1` and `Spearman(m, I)@H < 0.1` (interval). Unchanged.
- **Effect.** The two now contradict whenever a supporting H of one seed is a usable H of the other. The claims are keyed by H, so `satisfiable` already handles horizons that differ between seeds. The drift claim is a point claim (S3), so it never establishes a contradiction.

### S3. Point-threshold claims (E-H3c, and E-H2a's drift) never establish a contradiction

- **The fault.** M-6's contradiction is a statement about the *true* quantity: two seeds' intervals cannot both cover it. A point estimate on one side of a threshold makes no claim about the true value. So two seeds whose point estimates fall on either side of a threshold show sampling variation, not seed dependence. Calling that "contradicted" mislabels noise, which is exactly what the plan's DS-6 and M-6 set out to avoid.
- **The rule.** Claims with `basis == "point"` do two things only:
  - they count toward the minimum by word: a row is replicated if the same word appears on at least 4 of 5 seeds;
  - they are ignored by `contradict` and by the claim-level fallback.

  A row whose claim-bearing words are all point-based therefore reads:
  - **"replicated (point readings)"**, if the same word is on at least 4 of 5 seeds;
  - **"not replicated"**, otherwise.

  It never reads "contradicted". The label "(point readings)" must appear in `replication.md` and `replication.json`, so these rows are never mistaken for interval-based replications. Error rates for point readings are not controlled, as for any explanatory reading (plan §4.E).
- **E-H3c.** This applies to all three parts:
  - the Lorenz-63 tail share and percentile;
  - the Rössler BC;
  - the width ordering.

  The gaps between the thresholds (0.05 to 0.10 for the share, 1/2 to 2/3 for the percentile) already act as a "not determined" buffer. No interval is added before the freeze.
- **E-H2a.** Mixed rows check contradiction on the interval claims only (S2). The drift claims count only through the word.
- **Claim-set change:** none to the sets themselves. `contradict(first, second)` and the fallback filter out claims with `basis == "point"`, and the row classifier gains the "(point readings)" outcome.

### S4. The main session's two bookkeeping decisions

- **C1 rows excluded from the family counts and shown for display: agreed, with one guard.** They are duplicates only if their ratio, interval and word equal those of the matching D vs-full row on every seed. The tool must assert this and refuse otherwise. Without the check, "duplicate" is an assumption.
- **The claim-level fallback for contradicted rows: agreed, with two guards.**
  - The row's headline stays "contradicted".
  - A fallback claim is listed beneath it as "replicated claim within a contradicted row". It still needs to be implied by at least 4 seeds and contradicted by none.

  Example: four seeds read "small" and one reads "lowers". The row is contradicted on `ratio > 1`, but `ratio <= 1.05` is a legitimate replicated claim, and it must not lift the row's label.

### Note on r for C2

C2's upper-quartile r of 2.2 gives p = 0.21 and a P(at least 4 of 5) of 8·10⁻³ per null row. This is above M-6's robustness bound r ≤ 2. M-6 already rules that the rule is not changed: J7 states the expected count for the C2 rows. Nothing more is needed.
