# Applied-mathematician's view on the WU-0014 referral rulings (items 1, 3, 4, 5; D-25)

Date: 2026-10-10. Agent: applied-mathematician (claude-opus-5-5). Branch `develop` at ca59cc3. No study preset, no test suite, no GPU was run.

**Status.** This note **proposes**; the owner rules (LPC.AI.12, PRIME.2). Each section lists candidates, with the code's current definition as one candidate among them. It does not change any criterion, code or document.

**Sources:**
- the referral, `docs/agent/records/work/WU-0014-v3-concordance.md` `## Referral`;
- the concordance, `docs/agent/notes/2026-10-10-v3-concordance.md`, rows D-14, D-18 and D-22 to D-28;
- v3, `docs/study/proposal_and_methods_v3.md`;
- M2, `docs/study/methods_experimental_procedures_v2.md`;
- the pilot results: `pilot_results_v1.json` (JSON paths given), `pilot_results_v1_1.md` and `pilot_library_recheck.json`;
- the code: `lpcstudy/analysis.py`, `allocation.py`, `oracle.py`, `statistics.py`, `pipeline.py` and `data.py`.

**Verification markers:**
- **[V]** I verified the claim by reading the source or by computing it here.
- **[S]** The number comes from a synthetic model, not from the study systems.
- **[NV]** Not verified. The reason is given in each case.

The pilot JSON holds summaries only. It has no per-state w\*, ε_s, δ or Λ̃ (ROADMAP WU-0002.12 notes this). So no per-state pilot statistic could be recomputed under a new definition, and all such effects are marked [NV].

**Scratch scripts.** These live in the session scratchpad and are not in the repository. Each is described in one line where it is used. CPU only, at most 2 threads.

---

## 1. Referral item 4(a): w\* = 0 (and w\* = 1) in the logit of H2a(ii) and Q-N

**Question.** v3:89 tests the "partial correlation of logit w\* with Λ̃ given both seeds", with "interval inside (−0.1, 0.1)". Q-N (v3:83, :345) uses ΔR² for logit w\*. However, w\* = clip₀¹(u) (v3:258), and logit is −∞ at w\* = 0.
- In the pilot, 22–36% of test states had w\* = 0 at 1 LT (v3:376). The zero fraction was 0.24–0.36 across all library sizes (`pilot_library_recheck.json`, `zero_fraction`) [V].
- The 25th percentile of w\* at H = 30 is 0.0 on all three systems (`pilot_results_v1.json` `systems/*/weight_profile/q25` at horizon 30) [V].
- The code maps both boundaries to the logit of 0.01 and 0.99, so every w\* = 0 state sits at logit = −4.595 (`analysis.py:372-373` for H2a, `:281` for Q-N) [V].

**Why logit at all.** Under separation (v3:142), w\* = δ²/(ε_s² + δ²). So logit w\* = 2 ln(δ/ρ) − 2 ln(ε_s/ρ), which is exactly linear in the two controls. A linear partial correlation is the natural test under that model. The model never produces w\* = 0. Under P1(b), w\* = 0 means u ≤ 0, that is C ≥ E_P: a noise-matched cross-moment (the H2f mechanism; M2:406). The point mass is therefore itself a channel through which the weight can depend on the state.

**Synthetic model** [S]. Script `h2a_clip.py`:
- controls x = (ln ε_s/ρ, ln δ/ρ), bivariate normal;
- Λ̃ linear in x plus independent noise z;
- interior logit L = 2(x₂ − x₁) + β·z + 1.2·e;
- 30% mass at 0 from a hurdle index (or, for Tobit, from L below its 30% quantile), plus 2% mass at 1.

Population values use n = 4×10⁵. The SD is over 300 replicates at n = 1000.

| Estimator | S0 null | S0n null, nonlinear E[Λ̃\|x] | S1 Λ̃ acts on interior only | S2 Λ̃ acts on the zero mass only | S3 Tobit | SD at n = 1000 |
|---|---|---|---|---|---|---|
| logit, clip 10⁻⁴ | −0.000 | −0.070 | **+0.077** | −0.277 | +0.256 | 0.027–0.034 |
| logit, clip 10⁻³ | −0.001 | −0.066 | +0.102 | −0.259 | +0.270 | 0.027–0.033 |
| **logit, clip 0.01 (code)** | −0.000 | −0.056 | **+0.133** | −0.223 | +0.285 | 0.028–0.034 |
| logit, clip 0.05 | +0.000 | −0.043 | +0.141 | −0.182 | +0.268 | 0.029–0.034 |
| rank of w\* (ties at mid-rank) | −0.000 | −0.070 | +0.104 | −0.277 | +0.300 | 0.027–0.033 |
| normal scores of rank | −0.000 | −0.067 | +0.106 | −0.269 | +0.292 | 0.027–0.033 |
| hurdle (a): 1{w\* = 0}, all states | −0.000 | +0.079 | +0.002 | **+0.319** | −0.209 | 0.028–0.033 |
| hurdle (b) = interior only: logit w\*, 0 < w\* < 1 | −0.001 | −0.000 | **+0.349** | −0.000 | +0.302 | 0.034–0.040 |
| latent L (not observable; reference) | −0.003 | +0.000 | +0.349 | +0.001 | +0.354 | 0.028–0.033 |

The same S0n model with quadratic seed controls (x, x², x₁x₂) brings every estimator to |r| ≤ 0.0012 [S] (script `qn_clip.py`, part a).

Q-N under the same mechanisms [S] (script `qn_clip.py`, part b). This is gradient boosting with the code's hyperparameters, 3000 training and 1000 test states, the mean of 4 replicates.
- When N acts on the interior only, ΔR² is 0.041, 0.069 and 0.078 at clip 10⁻³, 0.01 and 0.05, and 0.043 with normal scores.
- So the v3 §7 Q-N reading flips between "distinct but small" and "substantial" at the 0.05 edge, depending only on the clip constant.
- Under the null, every target gives |ΔR²| ≤ 0.008.

**Candidates:**

| Candidate | Statistic | Sampling | Interpretability | Keeps v3's "inside (−0.1, 0.1)" meaning? |
|---|---|---|---|---|
| A. Clip at c (code: c = 0.01) | Value set by an arbitrary constant. In S1 it moves from 0.077 to 0.141 as c goes from 10⁻⁴ to 0.05, across the 0.1 bound | Null centred at 0 when E[Λ̃\|x] is linear. SD ≈ 1/√n | The mass's leverage grows with \|logit c\|. The number mixes two channels with a weight chosen by c | **No.** The verdict can depend on c |
| B. Rank or normal scores of w\* (single number) | No arbitrary constant. The tie block takes a data-set value (Φ⁻¹(p₀/2) ≈ −1.04 at p₀ = 0.3) | As A | A copula-scale correlation. It drops "logit" (invariant to any monotone transform) and still dilutes an interior effect (S1: 0.104 against 0.349) | Partly: the scale is no longer logit w\* |
| C. Two-part (hurdle): (a) 1{w\* = 0}, (b) logit w\* on interior states; both inside (−0.1, 0.1) | No constant. Each channel is measured on its own scale | (b) is about 20% wider (SD 0.034–0.040 against 0.033), since n_interior ≈ 0.68n. Two parts at level 1 − 0.05/3 each: the false-fail bound under the null is ≤ 2 × 0.0083 one-sided (union) | (b) is exactly v3's quantity on the set where it is defined. (a) is the point-biserial partial correlation of the boundary event | **Yes, on its domain,** and (a) closes the gap |
| D. Interior only, count reported | As C(b) | As C(b) | Misses the boundary channel: in S2 it reads 0.000 while Λ̃ drives the zero mass. Truncation attenuates effects (S3: 0.302 against 0.354) | No. It is anti-conservative for an equivalence claim |

**Proposed ruling: C, the two-part treatment, for both H2a(ii) and Q-N.**

- **H2a(ii).** Two parts:
  - (ii-a) the partial correlation of 1{w\*(H_ref) = 0} with Λ̃ given the seeds, over all test states;
  - (ii-b) the partial correlation of logit w\*(H_ref) with Λ̃ given the seeds, over states with 0 < w\* < 1. The counts of w\* = 0 and w\* = 1 are reported.

  Both intervals must lie inside (−0.1, 0.1) to pass. H2a fails if either lies entirely outside (v3:335).
- **States at w\* = 1.** These are excluded from (ii-b) and counted. If they exceed 5% of states, the owner should add a third part, 1{w\* = 1} [NV: the pilot does not record the mass at 1; its q75 at 1 LT is 0.24–0.33, so the mass is below 25%].
- **Q-N.** Report ΔR² for interior logit w\* and ΔR² for the indicator (the R² of a 0/1 target is the Brier skill score). The §7 reading table applies to each.

Reasoning:
1. **The constant decides the verdict.** Under candidate A, the clip constant changes the verdict-relevant value by up to a factor of 1.8 [S]. No physical or statistical argument fixes c.
2. **C keeps v3's meaning.** C keeps v3's exact quantity, logit w\* given the seeds, wherever it exists. It adds the boundary event, which the noise-matching mechanism (H2f) acts on.
3. **The cost is acceptable.** C leaves the null centred at 0, adds about 20% to the width of (ii-b), and doubles the fail-side α. H2a(ii) "essentially cannot pass" anyway (v3:363), so its role is refutation, and C refutes in S1, S2 and S3 where A at c = 10⁻⁴ does not in S1.

**Second ruling, needed under any candidate: the control set.** "Given both seeds" is linear in the code (`statistics.py:189-191`). If both E[target|x] and E[Λ̃|x] are nonlinear, a linear partial correlation is biased under the null: −0.04 to −0.07 for A and B, and +0.08 for C(a), in S0n [S]. That is the size of the band. Residualizing on (x, x², x₁x₂) removes this bias [S]. I propose quadratic seed controls, fixed before the freeze. [NV: whether E[Λ̃|x] is nonlinear on the real systems; the pilot has no per-state data.]

**Effect on pilot-comparable numbers (WU-0002.12)** [NV]:
- The keys `H2a.partial_corr` / `partial_ci` (pilot 0.061 [−0.055, 0.168], 0.133 [0.026, 0.221], 0.126 [−0.012, 0.263]; `pilot_results_v1.json` `systems/*/H2a`) are replaced by two parts.
- The Q-N `logit_w` ΔR² values (deployable and oracle; `systems/*/H1f`) change.
- `H2a.unconditional_spearman_w_lambda` is unchanged.
- The pilot H2a verdict does not depend on (ii): Rössler and Chua fail on (i), whose intervals are above 0.1 (`range_ci` [0.219, 0.328] and [0.122, 0.234]).

---

## 2. Referral item 4(b): the H2a(i) small-error regime and eligibility

**Question.** v3:89 tests the "median range of w\* over 1, 2, 4 LT in the small-error regime". The code (`analysis.py:359-370`) works as follows:
- it masks each (state, H) with both r.m.s. errors ≤ 0.5 σ_x (M2:277, assumption A6);
- it requires at least 2 masked horizons;
- it takes the range over the masked horizons only;
- it bootstraps the median over the eligible states only.

In the pilot, 348, 492 and 331 of 500 states were eligible (`systems/*/H2a/n_eligible_states`) [V].

**Selection effects** [V, by argument]:
1. **Mixed spans.** The range is monotone in the horizon set, so a state contributes a range over {1, 2} LT (span 1 LT) or over {1, 2, 4} LT (span 3 LT). The mix depends on Λ̃, because fast-growing states leave the regime first. That is the variable H2a is about. Under the alternative, high-Λ̃ states get shorter spans, which pushes the median toward a pass.
2. **Non-contiguous sets.** A set such as {1, 4} with 2 LT excluded is admitted. A6 reads "up to the horizons used" (M2:277), which implies an initial segment.
3. **The bootstrap fixes the eligible count.** Blocks are formed over consecutive *eligible* states (`:366`, `:369`), not over test states in time order (v3:326).
4. **States pinned at w\* = 0.** These have range 0 and pull the median down. This is legitimate, since the admissible optimum does not move, but it is not reported.

| Candidate | Effect on the statistic | Sampling | Interpretability |
|---|---|---|---|
| A. Code: per-(state, H) mask, at least 2 horizons, any subset | Mixed spans and Λ̃-dependent eligibility | Eligible n treated as fixed | Reads as the operational form of A6, but the span is not uniform |
| B. Complete case: all three horizons small | Uniform span (3 LT). Strongest selection toward slow, small-seed states | Smaller n [NV: likely small on Lorenz-63, where A1's MSE at 4 LT is 1.01, so the r.m.s. is about 1.0 σ_x; `pilot_results_v1_1.md:166`] | Cleanest estimand, but on a selected subpopulation |
| C. Code rule restricted to initial segments ({1, 2} or {1, 2, 4}), with the median reported per span and the counts | Removes non-contiguous sets. The mix becomes visible | Bootstrap over all test states in time order, with eligibility re-evaluated inside each resample | A6 as written |
| D. Unrestricted range (no regime) | Pilot 0.40 / 0.34 / 0.39 (`median_range_unrestricted`) | Full n | Outside the theory's validity (the decision log, line 20, keeps it reported only) |

**Proposed ruling: C, with B reported as a sensitivity.** It changes the code's reading only where A6 is violated (non-contiguous sets) and where the bootstrap departs from v3:326. It makes the selection visible without discarding the regime that the theory needs.

**What the owner should fix in the text (v3:89 or M2:381).** "For each state, the range of w\*(H) over the horizons in {1, 2, 4} LT up to the last at which both r.m.s. errors are ≤ 0.5 σ_x (A6); states with fewer than two such horizons are excluded and counted; the median is over eligible states; medians per span are reported."

**Effect on pilot-comparable numbers** [NV]:
- `median_range` and `range_ci` (0.118 [0.085, 0.159], 0.280 [0.219, 0.328], 0.174 [0.122, 0.234]) change slightly through the contiguity rule and the bootstrap index set.
- `n_eligible_states` can only fall.

---

## 3. Referral item 3: pass / fail / inconclusive for H3a, H3b and statistics that cannot be computed

**Question.** v3:322 says that every criterion is decided by an interval. H3a is a p-value rule: Holm-adjusted log-rank tests between consecutive regimes, all p < 0.01 (v3:99). H3b compares importances (v3:100). The code turns an empty or failed computation into `pass False` or NaN (D-18; `analysis.py:190-191`, `:367-368`, `:656`). Separately, `block_bootstrap` drops NaN resamples silently through `np.nanquantile` (`statistics.py:161`) [V].

| Item | Candidate | Cost | View |
|---|---|---|---|
| Statistic not computable | U1: verdict "inconclusive (not computable)", with the reason and the count recorded (PRIME.4) | None | **Propose.** A missing statistic is neither evidence for nor evidence against |
| | U2: a pre-registered minimum count for any statistic on a subset: n ≥ 50 states (10 blocks of 5). Below it, U1 applies | None. It is stricter than the code's 10 for H1c (`:190`) | **Propose** (the owner fixes the number). Fewer than about 10 blocks makes the moving-block bootstrap distribution too discrete |
| | U3: NaN bootstrap resamples placed at the unfavourable tail. If the NaN fraction is at least α/2, the bound on that side is infinite | None | **Propose.** It is conservative and counts the NaN resamples instead of conditioning on them |
| H3a | A3-1: v3 as written. Pass if all Holm-adjusted p < 0.01; "fail" otherwise | None | Reject. It reads "not significant" as "fail", so the false-fail rate depends on power |
| | **A3-2: pass as in v3; otherwise inconclusive. "Fail" exists only if the owner sets an equivalence margin m_H for the RMST difference of consecutive regimes, and some pair's interval then lies inside (−m_H, m_H)** | None, or K − 1 block-bootstrap RMST intervals for the fail side | **Propose.** It is the minimal change consistent with v3:331-333 |
| | A3-3: replace the tests with Bonferroni block-bootstrap intervals on the RMST differences | K − 1 intervals | Optional. It handles serial dependence, which the log-rank test ignores, and it is stricter than Holm |
| H3b | **B-1: block bootstrap (blocks of 5, 2000 resamples, 95%) over construction states, refitting both trees, for imp_w(Λ̃) and for D = imp_t(Λ̃) − max of the other coordinates' imp_t.** Weight part: band [0, 0.2). Horizon part: bound (0, ∞) | About 4000 fits of trees with at most 8 leaves per system, CPU seconds | **Propose.** Report alongside it the fraction of resamples in which Λ̃ ranks first (stability) |
| | B-2: stability fraction only, with pass at ≥ 0.95 | Same | A probability, not an interval. Not v3 §7 |
| | B-3: permutation importance on test, with an interval | More | A different estimand from M2's "impurity importances" (M2:388) |

**Caveats** [V, by argument]:
- **Holm is stricter than needed.** "All pairs separate" is an intersection–union claim, so unadjusted p < 0.01 per pair already controls the pass error. Holm is therefore conservative. I keep it, because it is v3's rule and loosening it is not for an agent to propose.
- **Bootstrapping importances.** Tree importances and the max in D are non-smooth functionals, so percentile coverage is not guaranteed near ties. That is why the stability fraction is reported.

**Effect on the pilot:**
- **H3a.** "fail" on all three systems (`pilot_results_v1_1.md:112`) becomes "inconclusive" under A3-2. The statistic does not change; the Holm p-values are in `systems/*/H3a/logrank_holm_p`.
- **H3b.** The point values do not change (Lorenz-63 weight-tree Λ̃ importance 0.89; `systems/lorenz63/H3c`). The intervals are new [NV: they need refitting].

---

## 4. Referral item 1, open points: band edges, the fail side and the K-rule "5%"

**Question.** Is H1a's "within ±25%" band (v3:79) open or closed? Is the endpoint on the fail side inside or outside? How is a tie at "within 5%" resolved? And does the K rule mean "calibration error" (v3:289) or "excess MSE" (M2:203)?

| Point | Candidates | Proposed ruling | Effect |
|---|---|---|---|
| Verdict geometry, all criteria | Per-criterion conventions, or one set rule | **One set rule: pass iff CI ⊆ B; fail iff CI ∩ B = ∅; otherwise inconclusive, with B exactly as v3:79-101 writes it (strict or closed).** The fail side follows automatically: for a closed B, an endpoint on the edge is not "entirely outside" | Pilot: none [V, below] |
| H1a band | Open or closed | **Closed:** B = [0.75, 1.25] / d_LB, matching v3's other bands (H1b, H1c) | None. See the next paragraph |
| Comparisons | Rounded or float64 | **Unrounded float64 values from `results.json`.** Rounding to the report's 2–3 digits is the only realistic source of ties | Avoids spurious ties |
| K rule, quantity | (a) excess V(w) − V(w\*) within 5% of the minimum excess (M2, ROADMAP WU-0002.3); (b) total calibration MSE within 5% of the minimum (a literal reading of v3:289); (c) code: excess / best-single ≤ 0.05, else K = 5 (`pipeline.py:341-346`) | **(a).** v3:289's next sentence defines the error as the excess. The excess is what the regime map controls (P3), while V(w\*) is common to every K | See below |
| K rule, tie | ≤ or < | **≤** (WU-0002.3 already treats a tie as inside) | None (measure zero) |

**Why the open/closed choice is immaterial** [V, computed]:
- The endpoints are interpolated bootstrap quantiles of continuous statistics, so an exact tie has probability about 0.
- The Monte Carlo SD of a percentile endpoint at 2000 resamples is 0.060 bootstrap SD at 95% and 0.088 at 1 − 0.05/3, where only 16.7 resamples fall in each tail. (Simulated with 4000 repetitions; this agrees with the formula √(α/2(1 − α/2)/B)/φ(z).)
- This Monte Carlo noise dwarfs any edge convention. What matters is that the bootstrap seeds are fixed before the run (`config.seed + salt`, `analysis.py:31`).

**Why the K-rule reading matters** [V for arithmetic; the inputs are test-split pilot values, because the calibration curves are not saved]:
- Reading (b) tolerates an excess larger than the minimum by 5% of (V\* + excess_min), against 5% of excess_min for reading (a). That is a factor 1 + V\*/excess_min looser.
- With pilot A\* MSE at 1 LT and the minimum regret ratio times the better single MSE, the factor is 1.6 / 4.9 / 2.8 (Lorenz-63 / Rössler / Chua).
- On the test-split pilot curves (`systems/*/H3b/regret_ratio_by_K`), reading (a) picks K = 4 / 3 / 4, reading (b) picks K = 4 / 2 / 2, and the code fell back to 5 on all three (`pilot_results_v1_1.md:75`).
- These curves use clipped w\* (DEF-0002) and are illustrative only.

**H1a "at both ρ"** (M2:376; v3 does not say). Requiring both is an intersection, so it is stricter. The ρ = 2% part is less well identified because the floor f grows with ρ: the pilot interval width is 0.43 at 2% against 0.26 at 1% on Lorenz-63 (`systems/lorenz63/H1b/by_noise`). I lean to "both ρ" (E2 feeds H1a at both ρ, v3:299), but the choice is the owner's.

---

## 5. Referral item 5 and D-26: state spacing and block length

**Question.** v3:239 says "at least 1 LT apart". M2:109-110 says 5·min(τ_ac, 1 LT) and at least one Theiler window (1 LT). The code uses max(⌈5·min(τ_ac, 1 LT)⌉, 1 LT) (`data.py:240-245`) [V]. Which rule gives approximately independent states, and what does a block of 5 assume?

Pilot spacing [V]:
- τ_ac is 9 / 1500 / 76 steps, and the spacing is 45 / 150 / 150 steps, that is 1.5 / 5 / 5 LT (`systems/*/context`).
- The M2 rule falls below 1 LT only when τ_ac < 6 steps (0.2 LT), so the max with 1 LT never bound in the pilot.

**Dependence check** [S on the real equations, with a proxy statistic].
- **Script.** `spacing_acf.py` integrates each system with numpy RK4 at the pilot's sampling interval and the v3 step bound. It computes the 1-LT growth exponent of the observable's sensitivity (a proxy for Λ̄) at 1000 states, then the autocorrelation function (ACF) and the ratio of the moving-block bootstrap (MBB) variance of the mean to the iid variance.
- **Precision.** The SE of each ACF value is about 0.03, and of the integrated autocorrelation time τ_int about 0.2.

| System | Spacing | ACF at lags 1–3 | τ_int = 1 + 2Σ_{1..10} ACF | MBB / iid variance at block 1 / 5 / 20 |
|---|---|---|---|---|
| Lorenz-63 | 1 LT | −0.14, +0.02, −0.05 | 0.76 | 0.99 / 0.78 / 0.76 |
| Lorenz-63 | 1.5 LT (coded) | −0.05, −0.04, −0.02 | 0.99 | 0.98 / 0.85 / 0.94 |
| Rössler | 1 LT | +0.05, −0.21, −0.11 | 0.41 | 1.01 / 0.77 / 0.57 |
| Rössler | 5 LT (coded) | +0.03, −0.08, −0.05 | 0.86 | 0.97 / 0.95 / 0.79 |
| Chua | 1 LT | −0.09, −0.02, −0.03 | 0.63 | 1.01 / 0.82 / 0.74 |
| Chua | 5 LT (coded) | +0.03, −0.06, −0.04 | 0.96 | 1.07 / 0.99 / 0.91 |

**Reading:**
1. **The x-ACF is the wrong clock.** Rössler's τ_ac of 50 LT reflects phase coherence, while per-state quantities decorrelate within one spacing. The code's cap of τ_ac at 1 LT is justified.
2. **The coded spacing is close to independent.** At the coded spacing, |ACF| ≤ 0.08 and τ_int ≈ 1, so states are approximately independent for this statistic.
3. **At 1 LT the dependence is negative.** States are anti-correlated (τ_int < 1), so iid and MBB intervals are conservative, not anti-conservative.
4. **Block 5 is adequate.** It assumes that dependence is negligible beyond about 4 spacings (6–20 LT). That holds here, and at the coded spacing block 5 reproduces the iid variance within 15%.
5. **Not covered.** This was not checked for w\*, ε_s or δ [NV]: they also depend on the noise draws and on the shared library. The shared library and trajectory are a common random effect, not serial dependence. The bootstrap over states does not capture it, which v3 §8 states as a scope limit ("independent trajectory replicates", future work).

**Proposed ruling.** Spacing = max(5·min(τ_ac, 1 LT), 1 LT), stated in v3 §4. This satisfies both documents and is what the code does. Keep block 5, and record the dependence check above, repeated on per-state w\* at DEV seeds, as its justification (NVVUQ.16).

**Effect on the pilot.** None: the spacing is unchanged (WU-0002.12 requires an identical `context.spacing`).

---

## 6. D-25 (c)–(i): one line each

| Item | View | Reason |
|---|---|---|
| (c) Q-N `l2_regularization = 1.0` (`analysis.py:294`) | **Document** in M2 E3, fixed before the freeze | A pre-data choice of estimator. It shrinks both nested models. Under the null, ΔR² ≈ 0 with it [S, §1] |
| (d) A5 tree: two-output CART on standardized (w\*(H_ref), log T), `min_samples_leaf = max(10, nE/50)` (`allocation.py:353-359`) | **Document**, and flag | The split criterion is not P3's curvature-weighted regret. The weight tree for H3b is curvature-weighted (`analysis.py:679`) but A5 is not. The owner may want curvature weights on the w\* output |
| (e) H3b trees `max_leaf_nodes = max(K, 4)` (`analysis.py:678`) | **Change** to a fixed leaf count (for example 8), set before the run | Impurity importances depend on tree size. Tying them to the data-chosen K makes the H3b estimand depend on the K rule. With 3 splits, a single Λ̃ split easily exceeds 0.2 |
| (f) H3a log-rank on the first evaluation draw (`analysis.py:646`) | **Keep**, and document | One observation per state keeps the test valid. Using all E draws would need a clustered test. The cost is a loss of power |
| (g) E6 perturbation: one random sign per parameter | **Keep**, and document the sign vector and seed | Reported only. A single direction is one draw of the model-error direction; it should be named as such |
| (h) 1/d reference: point median of Levina–Bickel over test-sweep states (`analysis.py:101-102`, `oracle.py:43-64`) | **Change:** estimate 1/d as the mean over states of (1/(k−1))Σ ln(T_k/T_j). Carry its uncertainty with a joint block bootstrap of the ratio (1/d_fit)/(1/d_LB) over the same resampled states, and pass if the ratio's interval ⊆ [0.75, 1.25] | See the next paragraph |
| (i) H2c better single forecaster chosen on test means (`analysis.py:480-481`) | **Change** to a choice on the calibration split, or recompute min(A0, A1) inside each resample | Selecting the smaller mean on the same data biases the comparison against A4, which is conservative but not pre-specified. No pilot effect: A1 wins at 1 LT by 2–14× on every system (`pilot_results_v1_1.md:165-197`) |

**Detail for (h)** [V, computed]:
- Under the Poisson idealization, the per-state estimator (k − 2)/S with S ~ Gamma(k − 1, d) is unbiased for d, with SD = d/√(k − 3) = 0.243d at k = 20.
- Its *median* is 0.964d (exact: 18/median Γ(19) = 0.9642). So 1/median is biased up by 3.7%, which uses up 15% of the ±25% band.
- The SD of the reference is 0.9% (n = 1000) or 1.7% (n = 300) of 1/d. That is negligible in quadrature against the 1/d_fit half-width of about 14%.
- So the reference's main defect is a bias, not missing variance. The proposed mean estimator removes the bias (simulation: relative bias −0.0001).
- Pilot effect: scaling 1/d_LB by 0.964 leaves all three pilot H1a intervals straddling an edge. The verdict stays inconclusive (computed from `systems/*/H1b`).
- [NV] Curvature and finite-N bias of Levina–Bickel on the real attractors, which is epistemic and not in any interval.

---

## Reproducibility

The scratch scripts below are in the session scratchpad, which is not persistent. The parameters stated above are enough to regenerate them. If the owner adopts §1 or §5, the scripts should move to the unit's folder (REPRO.10).

- `h2a_clip.py`: synthetic w\* with masses at 0 and 1, and nine estimators (seed 12345).
- `qn_clip.py`: quadratic controls; Q-N ΔR² with gradient boosting (seed 777).
- `spacing_acf.py`: RK4, the Λ̄ proxy, ACF and MBB variance ratio (seed 1).
- The endpoint Monte Carlo error and the Levina–Bickel median bias were computed inline (seeds 5 and 3).
