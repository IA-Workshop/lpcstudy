# WU-0041b: the mathematician's points M-1 to M-7, the revised §6.3 predictions, S1's λ_max and S3

**Every number here is DEVELOPMENT (DEV-1, DEV-2, DEV-3, DEV-4): not a hypothesis test.** No confirmatory seed was drawn, read or used. No CONF-1 number is read or quoted, and nothing here is placed beside the sealed CONF-1 result.

- **Author:** applied-mathematician (claude-opus-5-5), 2026-10-25. Unit WU-0041, ROADMAP.md §9 (phase I). Minimal formality (ledger seq 42).
- **Worktree:** `wu/0041b-math-points`, from `develop` at 7a327d9.
- **Scope.** This note answers §12.1 M-1 to M-7 of the pre-registration draft (`docs/agent/notes/2026-10-25-phase-i-preregistration-draft.md`). It also rewrites the §6.3 predictions and answers §13 item 9 and the S3 admission question. The draft itself is not edited: the main session folds the quoted sentences (the `>` blocks) in at P4.
- **Inputs read:**
  - the draft, in full;
  - v3 §2, §5 to §9;
  - the V7 diagnosis note;
  - the stage 1 ablation note;
  - the ensemble summary and its `extract.out.md`;
  - DEF-0020 to DEF-0022;
  - `tests/slow/test_statistics_coverage.py`;
  - `lpcstudy/{data,analysis,allocation,statistics,systems}.py`;
  - `tools/compare_runs.py`;
  - the stored DEV run folders under `lpcstudy-wt/run/`. Only development folders were read: no `confirmatory/` path was opened.
- **Computations.** All ran on the CPU, one thread, at `nice -n 19`, on stored outputs only, with no new run. The scripts and their outputs are in `docs/agent/notes/2026-10-25-preregistration-math-points/`:
  - `seed_rule.py` → `seed_rule.out.md`: M-1;
  - `censoring_r2.py` → `censoring_r2.out.md`: M-5 and M-6;
  - `a4_coefficients.py` → `a4_coefficients.out.md`: the stored A4 coefficients of all 15 DEV system-runs;
  - `refit_predict.py` → `refit_predict.out.md` and `.json`: a development preview of the refit mode, for §6.3.

## Summary of decisions

| Point | Decision |
|---|---|
| M-1 | The p³ bound is **confirmed, with three corrections**: (i) a false *fail* of a criterion with k parts has a per-seed bound of kα/2, not α/2; (ii) the primaries' undercoverage (0.9695 to 0.9732) gives p of about 0.015; (iii) the bound concerns each seed's own conditional estimand, and against the seed-averaged quantity p is larger. Development seeds show a between-seed variation of about 0.5 to 0.8 SE. Even then, a false promoted word has probability below 7·10⁻³ per word (1.5·10⁻² if the undercoverage is added). Across-system multiplicity can stay unadjusted. The power cost: about 20% more distance from the band edge is needed (in SE units), which is the same as running one seed with 1/1.45 of the states. On DEV, 22 of 36 words were stable, and 70% of the per-seed decisive words survived. |
| M-2 | Keep 1.05 (H3c's band and the K rule's margin), with the comparisons closed as in H3c. **Split the draft's last decisive row:** "substantial" now needs a lower bound > 1.05, and 1 < lower ≤ 1.05 with upper > 1.05 reads "needed, size not determined". **Add a boundary rule** that reads "not identifiable" before the table is applied. |
| M-3 | **Mixed levels, by one rule:** an estimate row uses the level of the v3 statistic whose reading table it uses. (b1) and (b2) use 95% (Q-N; the bitwise constraint). (a) and (b3) use 1 − 0.05/3 (H3c, whose band gives the 1.05 margin). |
| M-4 | **The existing v3 rule, unchanged.** `statistics.percentile_interval` already counts a failed resample as −∞ for the lower bound and +∞ for the upper bound. With 50 failures (95%) or 17 failures (1 − 0.05/3) out of 2000, both bounds are infinite and the row reads "undetermined". Widening never creates a reading's bound claim. |
| M-5 | **Keep R² on Y = ln min(T, 8 LT).** The censoring is administrative at a fixed cap, so Y is observed for every state. Name the estimand, store the censored count (a new leaf), and read a part with fewer than 50 uncensored states as undetermined. Above 25% censored, add the report-only label "censoring-affected". |
| M-6 | **Confirm** R²(∅) as the training-mean predictor. It is the regressor's own no-feature limit, it is ≤ 0, and its expected size is −0.001 to −0.005. It shifts each φ_X by +|R²(∅)|/4 ≤ 0.0013. Store it as a leaf. |
| M-7 | If a regeneration is not bitwise, the pair is judged at the tier `compare_runs` selects from the digests, with the tolerances of WU-0003 A6 unchanged. For a same-digest GPU pair this is **tightened to the T1 rules**. Every word must be identical in T0 to T3. TD uses z_away ≤ 3.4 per primary part. New float leaves must have chain tags before the freeze. |
| §6.3 | Rewritten (§8 below). Zero-a is A0 and zero-a′ is almost A1. **In refit mode, a's loss nearly disappears** (r 0.90 to 1.16). b is "not identifiable" in both modes. b′ is negligible, or not identifiable where it sits at the boundary. |
| §13 item 9 | A CONF run uses the λ_max that **its own invocation computes on the official GPU** in a fresh output directory. It never uses the CPU-cached 0.112205. For S1 the expected value is 0.11272865874045755, bitwise. |
| S3 | **I agree: not admitted.** Even the oracle-started, converged LM is at the band edge (0.905 at 5%). Every deployable start fails. A pass would be a coincidence of nonlinear effects, not efficiency. |

---

## 1. M-1: multiplicity across systems and the seed rule

### 1.1 The bound, step by step

**Setting.** Fix a system and a criterion. Seed s ∈ {CONF-2, CONF-3, CONF-4} yields an interval I_s for each part. Let θ_s be the quantity that I_s is an interval for (§1.3). A promoted word W needs W on all three seeds.

**Step 1: per-seed error.** This is **correct as stated for a pass, but needs a hypothesis for a fail.**

- **False pass.** If θ_s lies outside the pass region, a pass needs the interval to lie entirely on the wrong side of θ_s. That is a one-sided miss, with probability ≤ α/2.
- **False fail.** A fail word needs only one part to fail (intersection–union). If no part is truly in the fail region, a false fail is a union of k one-sided misses, so its probability is ≤ kα/2 (Bonferroni).
- **Parts per criterion.** H2a has 3 parts (4 if w\* = 1 exceeds 5%); H2b, H2c, H1a, H2e and H3b have 2; H1d has 3.
- **H3a** has no fail word, and its pass carries a Holm FWER ≤ 0.01. WU-0006 measured 19 to 26 of 2000 (L1).
- **Pass bound.** The draft's p ≤ α/2 holds for pass words only.

**Step 2: independence across seeds.** This is **correct under hypothesis (I)**: given the system, the frozen code and the device, the three runs' random inputs are independent.

I checked (I) in the code:

- **Seed-drawn inputs.** Each of the following is seed-drawn through `make_rng(seed, ...)` or `sklearn_seed(seed, ...)`, with no label shared across seeds:
  - the main and estimator trajectories: `draw_starts`, then a 100 LT burn-in, while the start perturbation saturates within about 14 LT;
  - the library noise;
  - the oracle and evaluation noise;
  - the network initializations;
  - the gradient-boosted regressors;
  - the bootstrap indices.
- **Shared inputs.** The inputs shared by all seeds are deterministic constants, not random draws:
  - the statistics orbit from the registry start, which fixes σ_x, C, τ_d and the spacing;
  - λ_max: `lyapunov_guarded` starts at `spec.initial_state`, with no seed;
  - the code;
  - the bands.

  They create no sampling dependence. Their error is a **common-mode bias** (§1.4).
- **Product.** Under (I), P(W on all three | the θ_s) = Π_s P(W on seed s | θ_s) ≤ p³.

**Step 3: undercoverage.** This is **correct for the secondaries and missing for the primaries.**

- **Measured coverage** (WU-0006 reference, `tests/slow/test_statistics_coverage.py`): 0.9451 and 0.9800 at lag-1 autocorrelation φ = 0, and 0.9257 to 0.9292 and 0.9695 to 0.9732 at φ = 0.3.
- **Equal tails.** With equal tails, p ≈ 0.035 to 0.037 for the secondaries (as the draft says) and **p ≈ 0.013 to 0.015 for the primaries**.
- **Worst case.** For skewed statistics (ratios, medians) the tails of a percentile interval need not be equal. Then p ≤ 1 − coverage: about 0.074 for the secondaries and 0.031 for the primaries.

**Numbers per word** (`seed_rule.out.md`, part 1):

| Case | p per seed | pass word p³ | two-part fail (2p)³ | three-part fail (3p)³ |
|---|---|---|---|---|
| primary, nominal | 0.0083 | 5.8·10⁻⁷ | 4.6·10⁻⁶ | 1.6·10⁻⁵ |
| primary, φ = 0.3 | 0.0152 | 3.6·10⁻⁶ | 2.8·10⁻⁵ | 9.6·10⁻⁵ |
| secondary, nominal | 0.025 | 1.6·10⁻⁵ | 1.3·10⁻⁴ | 4.2·10⁻⁴ |
| secondary, φ = 0.3 | 0.037 | 5.1·10⁻⁵ | 4.1·10⁻⁴ | 1.4·10⁻³ |

**Union over all words.** Summed over 6 systems × 12 criteria, with each fail word at its k-part bound and every part at its band edge at once (a gross worst case), the total is 6.1·10⁻³ nominal and 2.1·10⁻² at φ = 0.3. Pass words alone give 8.5·10⁻⁴ and 2.8·10⁻³. **The draft's "8·10⁻⁴ over 54 words" is the pass-word figure.**

### 1.2 Development check of the premise: is θ_s the same on every seed?

The per-seed intervals cover each seed's conditional quantity, with the fitted models held fixed (v3 §7 for Q-N, and the same for H2c, H2d and H3c). Between seeds, that quantity can move because the libraries, networks and fits change.

**Method.**

- **Statistic.** I took the project's own two-run statistic (v3 §9 item 3, `compare_runs.td_part`) over the 18 primary parts × 3 seed pairs of the frozen systems (DEV-1, DEV-3, DEV-4; `seed_rule.out.md`, part 3).
- **What it measures.** Under a fixed θ and correct standard errors, z_sym² has mean 1. A seed-dependent θ with standard deviation τ gives a mean of 1 + τ²/SE².
- **Not a spread statistic.** This is a check of an interval property. No spread across seeds of any QoI is reported (schedule O7).

**Results.**

- **Mean z_sym².** The mean z_sym² is **1.70** over 54 pairs. The pairs share seeds, so there are about 36 effective pairs, and the null standard deviation of the mean is about 0.24.
- **Tail counts.** z_away exceeded 1.96 in 10 of 54 pairs, against 2.7 expected. It exceeded 3.4 in 1 pair: rossler H2b(i), DEV-1 against DEV-4, z = 4.06.
- **What explains part of it.** At φ = 0.3, the block-5 undercoverage alone inflates z² by about 1.16 (long-run variance 1.857 against the 1.60 that block 5 captures). Removing the single largest pair leaves 1.43.
- **Reading.** τ ≈ 0.5 to 0.8 SE on the primary parts. The per-seed estimand is seed-dependent at a level comparable to the sampling error.

**Consequence.** Against the seed-averaged quantity θ̄, the per-seed false-pass rate is Φ(−z_α/√(1 + τ²/SE²)):

- **At τ = 0.8 SE:** 0.031 (primary) and 0.063 (secondary).
- **Per word:** p³ = 2.9·10⁻⁵ and 2.5·10⁻⁴. The worst multi-part fail word, a four-part H2a or a three-part H1d, stays below 7·10⁻³.

With the φ = 0.3 undercoverage added (p = 0.046 and 0.082), the worst case rises to 1.5·10⁻². So the rule still controls the error of a promoted word if the word is read as a statement about the procedure's typical value, not about one realization.

### 1.3 What a promoted word claims

The estimand of a per-seed word is that seed's quantity, conditional on its fitted models. A promoted word says the criterion held on three independent realizations of the frozen pipeline. That is what §1.1 bounds.

### 1.4 What the bound does not cover (the draft's caveat 4, made precise)

A bias common to all seeds does not break the product rule, but it raises p equally on every seed, up to p → 1. The list of sources:

- the estimator and the LM iteration error;
- the clip;
- λ_max (S1: SE 0.4%, the same value on all three seeds, §10);
- σ_x and C from the registry-start statistics orbit;
- the code and the bands.

**No multiplicity adjustment would touch this.**

### 1.5 Power of the all-three rule

**Model.** If one seed decides a part with probability π, the part is promoted with probability π³. The probability that all three seeds give the same word is π_pass³ + π_inc³ + π_fail³.

**Distance needed for 80% power** (normal approximation, distance from the band edge in SE units, `seed_rule.out.md`, part 4):

| Level | one seed | all three | ratio | same as one seed with n / … |
|---|---|---|---|---|
| 1 − 0.05/3 | 3.24 | 3.86 | 1.19 | 1.42 |
| 95% | 2.80 | 3.42 | 1.22 | 1.49 |

**Development evidence** (frozen systems, DEV-1, DEV-3, DEV-4, `seed_rule.out.md`, part 2):

- **Stability.** 22 of the 36 per-system words were the same on all three seeds: 17 decisive and 5 inconclusive.
- **Retention.** Each seed gave 27, 24 and 22 decisive words (mean 24.3), so 17 of 24.3 (70%) survived promotion.
- **Primary parts.** 12 of the 18 primary parts were stable.
- **No reversals.** No word moved between pass and fail.

The seed-dependent estimand of §1.2 lowers agreement further. That is one reason why the observed 61% is below what the intervals alone suggest.

### 1.6 Across-system multiplicity

**It can stay unadjusted.**

1. No claim combines systems.
2. The seed rule already makes the family-wise rate of a false promoted word small. At most 2.1·10⁻² over all 72 words under the worst-case union, and 2.8·10⁻³ for pass words, even with the measured undercoverage.
3. An adjustment would change a level, which seq 44 forbids.
4. It would do nothing against the common-mode biases of §1.4, which are the real residual risk.

### 1.7 Sentences for the pre-registration (§3 item 3 and §4 "Power cost")

> **Multiplicity across systems: not adjusted.** Each per-system word is its own claim, and no claim combines systems. A word is promoted only if all three CONF seeds give it. The three runs share no random input: trajectories, libraries, noise, networks, regressors and resamples are drawn from each seed, and the shared inputs (the statistics orbit from the registry start, λ_max, the code, the bands) are deterministic. So the probability that a false word is promoted is the product of the three per-seed probabilities. Per seed, that probability is at most α/2 for a false pass, and at most kα/2 for a false fail of a criterion with k parts. Nominally, this gives at most 5.8·10⁻⁷ for a primary pass word and 4.2·10⁻⁴ for a three-part secondary fail word. Under the undercoverage measured in WU-0006 at lag-1 autocorrelation 0.3 (coverage 0.926 at 95% and 0.970 at 1 − 0.05/3), the same bounds are 3.6·10⁻⁶ and 1.4·10⁻³. The estimand of a per-seed word is that seed's quantity, conditional on its fitted models. On development seeds this quantity varied between seeds by about 0.5 to 0.8 of its standard error. Judged against the seed-averaged quantity, a promoted word is still false with probability below 7·10⁻³, or 1.5·10⁻² with the measured undercoverage. These bounds cover sampling error only. A bias shared by all seeds (the estimator, the LM iteration error, the clip, λ_max, the code) acts on every seed alike, and neither the seed rule nor a multiplicity adjustment reduces it.

> **Power cost.** If one seed decides a part with probability π, it is promoted with probability π³ (0.51 at π = 0.8). For 80% power on all three seeds, a part's value must lie about 3.9 standard errors from its band edge (primaries) or 3.4 (secondaries), against 3.2 and 2.8 for one seed. That is about 20% farther, the same as running one seed with about 1/1.45 of the states. On the frozen systems (DEV-1, DEV-3, DEV-4), 22 of the 36 per-system words were the same on all three seeds, 17 of a mean of 24 decisive words per seed would have been promoted, and no word moved between pass and fail. Many words should be expected to read "seed-dependent", and a seed-dependent word is not evidence of no effect.

---

## 2. M-2: the 1.05 margin of the MSE-ratio reading table

**Answer: keep 1.05.** Its basis is not a loss function. It is the study's own definition of "costs almost nothing" for an MSE ratio at H_ref: H3c's band (upper ≤ 1.05) and the K rule. An MSE ratio of 1.05 is an RMS forecast error ratio of 1.025.

**Three refinements.**

1. **Closed comparisons, as in H3c.** Use "≤ 1.05" for the small and negligible rows and "> 1.05" for substantial. The draft's "< 1.05" and "≥ 1.05" copied Q-N's strictness. Equality has probability zero in practice, but the text must fix one convention, and the margin's source is H3c.
2. **Split the draft's last decisive row.** The draft reads "lower > 1, upper ≥ 1.05" as "substantial". On the development data, that would call DEV-1 lorenz63 zero-a′, 1.054 [1.014, 1.121], "substantial", although the interval allows a 1.4% loss. "Substantial" should mean the interval excludes "small": lower > 1.05. The remaining case, 1 < lower ≤ 1.05 with upper > 1.05, reads "needed; size not determined". Q-N's table is not changed, because it is pre-registered in v3 and governs (b1) and (b2).
3. **A boundary rule, applied before the table** (ablation (a) only). A coefficient fitted at the boundary of its domain (stage 1 §3.3) gives r = 1 to round-off, for example a b row at 1 + 10⁻⁹. Such a row could read "needed, but small" from round-off alone. The rule:
   - **Rule.** Zero the coefficient in the full A4, and let Δw be the largest absolute weight change over the test (state, evaluation draw) pairs. If max |Δw| ≤ 10⁻⁶, both of the coefficient's rows (zero and refit) read **"not identifiable (fitted at the boundary)"**.
   - **Why 10⁻⁶.** Development values are at most 8.4·10⁻⁸ for every boundary case (b in all six stage-1 cells, b′ on Rössler), and 2.4·10⁻³ to 1.3·10⁻² for the non-boundary b′ (Lorenz-63, Chua). The threshold sits one decade above the first group and more than three decades below the second.
   - **Effect on r.** A weight change of 10⁻⁶ moves r by at most about 10⁻⁵, far below every threshold of the table.
   - **The refit preview shows the need.** Refit-b′ on Rössler gives 1.0004 [1.0003, 1.0006], which the table would read "needed, small". That is an artefact of the test-state refit (§8.2), and the rule reads it "not identifiable".

**Precision.**

- **Half-widths at n = 1000.** Development half-widths of the ratio rows:
  - the a′ rows at 1 − 0.05/3: 0.04 to 0.09 (stage 1);
  - the refit-a rows at 95%: 0.04 to 0.15 (preview).
- **Consequence.** The 0.05 margin is about one half-width. "Negligible" is therefore reachable only when the point estimate is within about 0.02 of 1, and small effects should be expected to read "undetermined".
- **Bootstrap error.** The bootstrap endpoint Monte Carlo error of these rows reached 0.32 in one stage 1 row (DEV-1 lorenz63 zero-a). Report it with each row (`endpoint_mc_error`, as in the ensemble summary §7), so that an endpoint within two Monte Carlo errors of 1 or 1.05 can be seen.

> **Reading table for an MSE ratio r (ablation (a) and row (b3)).** Endpoints are compared unrounded, and the rows are checked from the top. First, a row with fewer than 50 test states, or with an infinite bound (failed resamples, §M-4), reads "undetermined" with its reason. In ablation (a), if zeroing the coefficient in the full A4 changes no test weight by more than 10⁻⁶ (the coefficient is fitted at the boundary), both rows of that coefficient read "not identifiable (fitted at the boundary)". Otherwise: upper bound < 1, "removing the term lowers the MSE"; lower bound ≤ 1 and upper bound ≤ 1.05, "the term is negligible at this precision"; lower bound > 1 and upper bound ≤ 1.05, "the term is needed, but its contribution is small"; lower bound > 1.05, "the term carries a substantial part of A4's accuracy"; lower bound > 1 and upper bound > 1.05, "the term is needed; its size is not determined"; otherwise, "undetermined". The margin 1.05 is H3c's band, the study's definition of an MSE ratio that costs almost nothing. With the development half-widths (0.04 to 0.15), small effects are expected to read "undetermined". Each row reports the bootstrap Monte Carlo error of its endpoints.

---

## 3. M-3: levels of the estimate rows

**Answer: mixed, by one rule.** An estimate row uses the level of the v3 statistic whose reading table it uses.

- **(b1) and (b2): 95%.** These rows are read by the Q-N table, and that table's thresholds (0.05, and the slightly negative null gain of v3 §7) are calibrated at Q-N's 95% (v3 §7 projects ±0.04). The drop-N row must also reproduce Q-N's leaves bitwise, which fixes the level. The Shapley rows share the resamples and the table, so they share the level.
- **(a) and (b3): 1 − 0.05/3.** These rows are read by the MSE-ratio table, whose margin is H3c's band, and H3c is judged at 1 − 0.05/3. At the same level, "upper ≤ 1.05" means exactly that the variant would meet H3c's criterion against the full rule.
- **No error rate to control.** Neither level controls an error rate, because the rows carry no verdict. The 0.05/3 here is a convention inherited with the table, not a Bonferroni family of the ablations. The development numbers were computed at both levels (`refit_predict.out.md`), so the predictions do not depend on this choice.

**Why not one level.** A single 95% everywhere would also be coherent, and I would accept it. Then "negligible" in (a) and (b3) would no longer coincide with H3c's pass. A single 1 − 0.05/3 is impossible, because of the bitwise constraint on drop-N.

> **Levels of the estimate rows.** Each estimate row uses the level of the v3 statistic whose reading table it uses. The profile rows (b1) and (b2) are read by the Q-N table and use Q-N's 95%, so the drop-N row reproduces Q-N's leaves bitwise. The MSE-ratio rows (a) and (b3) are read by the table of §6.2, whose margin is H3c's band, and use H3c's level 1 − 0.05/3. No estimate row carries a verdict, so neither level controls an error rate.

---

## 4. M-4: failed resamples in estimate rows

**Answer: the v3 rule as implemented, unchanged.** v3 places a failed resample "at the unfavourable tail". The code already reads that rule symmetrically for both directions (`statistics.percentile_interval`, DEC-0008 A3):

- **Bounds.** A failed value counts as −∞ for the lower bound and +∞ for the upper bound, so it can only widen the interval.
- **Threshold.** With F ≥ ⌊(B − 1)a⌋ + 1 failures (a = (1 − level)/2), both bounds are infinite. For B = 2000 that is **50 at 95% and 17 at 1 − 0.05/3**.
- **Q-N already does this.** Q-N uses this path (`_interval_block`), so (b1) reproduces Q-N bitwise including its failure handling. `_qn_reading_reason` gives the reason "failed resamples ≥ threshold".

**Why this is the unfavourable direction for every reading.**

- **Bound claims.** Every reading is a conjunction of bound claims ("lower > c", "upper ≤ c") and their negations. Widening can only remove a bound claim; it can never create one.
- **Example.** A widened [1.01, 1.04] can move from "needed, small" to "negligible". It loses the claim "lower > 1" and keeps "upper ≤ 1.05", which was already established.
- **Undefined statistics.** For estimate rows, a failure comes from an undefined statistic in a resample:
  - a constant target, where SS_tot = 0, for example the w\* = 0 indicator with no zero state;
  - an empty interior set;
  - a zero or non-finite MSE.

  Each is counted per row.

> **Failed resamples in estimate rows** are counted and handled as in v3 §7, through the same code (`statistics.percentile_interval`). A failed value counts as −∞ for the lower bound and +∞ for the upper bound, so it only widens the interval and can never create a reading's bound claim. With 50 or more failures of 2000 at 95%, or 17 or more at 1 − 0.05/3, both bounds are infinite and the row reads "undetermined (failed resamples ≥ threshold)". The count is reported in every row.

---

## 5. M-5: R² on the horizon target censored at 8 LT

**What the target is** (`allocation.state_horizon_target`).

- **Definition.** The characteristic horizon of the oracle hybrid at θ = 0.2, computed from the M = 200 oracle moments. It is set to H_max = 240 steps (8 LT) when the tolerance is never exceeded. Q-N stores Y = ln of it.
- **Censoring.** This is administrative (type I) censoring at one fixed cap. Y is observed for every state, so R² of Y is well defined without a censoring model. The censoring is not informative missingness: nothing is unobserved except where T lies beyond 8 LT.

**What R² of Y measures.**

- **Estimand.** It measures predictive information about the censored horizon min(T, 8 LT). It is not information about T itself.
- **Blind spot.** A condition that only separates states whose horizons all exceed 8 LT gets no credit.
- **Implementation.** The squared-loss regressor estimates E[Y | X], which is the correct predictor for this estimand.

**Size of the effect** (`censoring_r2.out.md`, part A).

- **Model.** Z = b₁X₁ + b₂X₂ + sε, with Y = min(Z, c) censored at the (1 − p_c) quantile. The conditional means are analytic (Tobit), and the Monte Carlo is over X only (4·10⁵ draws).
- **Attenuation.** ΔR² of a condition on Y, relative to its value on Z:
  - 0.98 to 1.00 for the weaker condition at every p_c up to 0.5;
  - 0.94 to 0.99 for the stronger condition at p_c ≤ 0.25;
  - 0.86 to 0.98 at p_c = 0.5.
- **Reading.** At the censoring seen so far, the attenuation is small against the Q-N interval of about ±0.04.

**Development counts.**

- **Frozen systems.** DEV-2 has 0, 2 and 4 censored states of 1000 (lorenz63, rossler, chua; `censoring_r2.out.md`, part B).
- **S2.** The draft's "125 censored states on S2 (DEV-3)" is H3a's count for the *realized* horizon of the first evaluation draw, judged against the noisy verifying observation. It is not the Q-N target. The Q-N block stores no censored count (checked in the S1 and S2 DEV-3 `results.json`), so the count of the target itself is unknown.

**Rules to add.**

- **A censored-count leaf.** An added leaf, so the leafdiff "0 changed, 0 removed" holds.
- **An uncensored-state minimum.** The information in Y is carried by the uncensored states, so the analogue of the 50-state rule is 50 uncensored test states.
- **A report-only label.** Above 25% censored, where the simulated attenuation of the stronger condition passes 5%, the reading carries the label "censoring-affected".

> **Horizon target.** The horizon rows use Y = ln min(T, 8 LT), the log characteristic horizon of the oracle hybrid at θ = 0.2, censored administratively at H_max = 240 steps. Y is observed for every state, so R² and ΔR² need no censoring model. They measure predictive information about the censored horizon, not about horizons beyond 8 LT. The number of censored test states is stored and reported beside every horizon row. A horizon part with fewer than 50 uncensored test states is undetermined. Where more than 25% of the test states are censored, the horizon reading carries the report-only label "censoring-affected" (in a Gaussian model, censoring up to 25% reduces a condition's ΔR² by at most 6%).

---

## 6. M-6: R²(∅) as the training-mean predictor

**Answer: confirmed.**

**Definition.** The empty model predicts ȳ_train, the mean of the target over the training states (construction plus calibration; for the interior-logit target, the interior training states). It is scored like every other subset: on the test states, with SS_tot about the test or resample mean (`analysis._r2`). This gives

  R²(∅) = −(ȳ_test − ȳ_train)² / s²_test ≤ 0,

with expected value about −(1/n_train + 1/n_test)·κ, where κ is the long-run variance factor. At n_train = 3000 and n_test = 1000 this is **−0.0013κ**: −0.001 to −0.005 for κ from 1 to 4 (`censoring_r2.out.md`, part C).

**Why this definition.**

- **Same treatment for all 16 subsets.** Every subset is fitted on the training states and scored on the test states.
- **The regressor's own limit.** The training mean is what `qn_regressor` returns when it has no usable feature. Fitted on a constant feature, every tree is a single leaf with value −Σg/(Σh + λ) = 0, because the gradients sum to zero after the mean start. Its prediction is ȳ_train to round-off.
- **For the indicator target** this is the Brier skill reference (the training base rate).
- **The alternative leaks.** "R²(∅) = 0" would use the test mean as a predictor, which leaks the test targets.

**Effect on the Shapley values.**

- **Shift.** R²(∅) enters each φ_X only through the S = ∅ term, which has weight 0!·3!/4! = 1/4. So every φ_X is raised by |R²(∅)|/4 ≤ 0.0013. That is 3% of the 0.05 threshold.
- **Sum.** Σφ_X exceeds R²(F) by |R²(∅)|.
- **Null value.** Under the null, ΔR² and φ_X remain slightly negative (the overfitting penalty), so the Q-N table's "reduces" row keeps its meaning.

> **Empty set.** R²(∅) is the out-of-sample R² of the constant predictor equal to the target's mean over the training states (construction plus calibration; for the interior-logit target, the interior training states). It is scored on the test states like every other subset. It equals −(ȳ_test − ȳ_train)²/s²_test ≤ 0, and at the full sizes it is expected to lie between −0.001 and −0.005. It raises every Shapley share by |R²(∅)|/4. It is stored per target and profile, and the identity Σ_X φ_X = R²(F) − R²(∅) is checked to 10⁻¹².

---

## 7. M-7: fall-back tolerances if the GPU regeneration is not bitwise

**What can differ, and how `tools/compare_runs.py` classifies it** (tier selection is mechanical, from the recorded digests and platform facts):

1. **Equal data, whitening and network digests, same host and device.** The tool labels the pair T0. On a GPU it then measures the float differences with the 10x rule: per class group, a declared tolerance 10^⌈log₁₀(10·max rel)⌉, where a declaration above 10⁻⁴ is the O3 finding, exit 1. Integers, strings and words stay exact.
   - **The gap.** That rule alone would allow a network-independent leaf (`cp`, `oracle`, `dynamics`, `fixture`) to move by up to 10⁻⁴. A cross-device T1 pair must keep those leaves within 10⁻¹².
   - **Tightening.** A same-device rerun should not be held to less than a cross-device one, so I **tighten** the fall-back for this case to the full A6 T1 rules: chain leaves within 10⁻¹² relative, V1 within 10⁻¹² absolute, V2 within 10⁻¹⁰ relative, QoIs and interval endpoints within 10⁻⁴·max(|lo|, |hi|), and the LM summaries as in T1, together with the declaration ≤ 10⁻⁴.
   - **Applying it.** The tool's report lists every differing leaf with its relative difference and chain tag, so the T1 check is a reading of that list. A tool flag is optional.
2. **A differing network weight digest: T3. A differing whitening digest: T2.** The tool's rules apply, and every word must be identical.
3. **A differing data digest** (the trajectory, λ_max or the start state): TD. These are different realizations, as when a nondeterministic reduction reaches a chaotic trajectory. Each of the system's 6 primary parts must have z_away ≤ 3.4 (OF-5), and the words are reported only.

**Why these tolerances are enough.**

- **Ratified.** The rules are the WU-0003 A6 rules as ratified (DEC-0030 OF-5 and OF-7, DEC-0032 B9). None is chosen or loosened here.
- **Endpoint movement.** A QoI tolerance of 10⁻⁴·max(|lo|, |hi|) moves an interval endpoint by much less than its bootstrap Monte Carlo error (ensemble §7: s.e./half-width ≤ 0.10). A word can therefore change only if an endpoint sits within 10⁻⁴ of a band edge, and "every word identical" catches that case.
- **The TD bound.** z_away ≤ 3.4 has a per-part two-sided rate of 6.7·10⁻⁴ under equal distributions: about 0.4% per (system, seed) over 6 parts.

**A precondition, not a tolerance.** `compare_runs` reads an untagged float leaf as NOT COMPUTABLE (exit 2) in every tier, even when the leaf is bitwise equal. WU-0039 adds leaves: the ablation rows, the new LM start counters, R²(∅) and the censored count. They must carry chain tags before the freeze, or the T0 comparison itself cannot pass. WU-0042 should check this on a development pair of an extension-system run.

> **If the GPU regeneration is not bitwise.** It is reported as "not bitwise (determinism not shown)" and trigger C-1 fires. The pair is then judged, without change, at the tier that `tools/compare_runs.py` at the frozen commit selects from the recorded digests. With equal data, whitening and network digests on the same host and device, every non-float leaf and every word must be identical, and every float must meet the A6 T1 tolerances (network-independent chain leaves within 10⁻¹² relative; V1 within 10⁻¹² absolute; V2 within 10⁻¹⁰ relative; QoIs and interval endpoints within 10⁻⁴ of the larger absolute endpoint of the reference interval; LM summaries as in T1), with no class-wise declared tolerance above 10⁻⁴. With a differing network weight or whitening digest, the T3 or T2 rules apply and every word must be identical. With a differing data digest, the runs are different realizations: each primary part must have z_away ≤ 3.4, and the words are reported only. None of these outcomes changes a word, and no tolerance is set or loosened after a result. Before the freeze, every float leaf of an extension-system run, including the ablation rows, carries a chain tag in `compare_runs`.

---

## 8. §6.3 rewritten: predictions for ablation (a), using stage 1

### 8.1 Evidence used (all development)

1. **Stage 1** (WU-0036; DEV-1 pilot and DEV-2 full; zero mode only, at 1 − 0.05/3).
2. **The stored fitted coefficients** of all 15 DEV system-runs (`a4_coefficients.out.md`).

   | Runs | b | b′ | a/a′ |
   |---|---|---|---|
   | 9 frozen cells (DEV-1, DEV-3, DEV-4) | ≤ 3.9·10⁻⁹ in all 9 | ≤ 2·10⁻⁶ in 5 (Rössler 3 of 3, Lorenz-63 2 of 3); 8.2·10⁻³ to 5.4·10⁻² elsewhere | 0.252 to 0.281 |
   | S1 (DEV-3, gate PASS) | 8.8·10⁻⁹ | 4.6·10⁻⁸ | 0.209 |

   S2 to S6 (DEV-3) ran with the unfixed estimator. Their a′ (1.27 to 496) and b′ (up to 1040) describe the wrong-basin LM, not an admitted configuration. S3 also has b = 1.5.
3. **A development preview of the refit mode** (`refit_predict.out.md`).
   - **Method.** Each one-coefficient refit uses the package's fit recipe, but on the dump's *test* states, because the construction states are not in the dump. It is scored as in stage 1.
   - **Fit noise.** The test-state stand-in gives a refit-b and refit-b′ of 0.997 to 1.008 where the construction fit would give 1 exactly. That is the scale of the fit-sample noise, and it is why the boundary rule of M-2 is needed.

### 8.2 What the variants are, algebraically

Notation: x = R/ρ, n = ν̂² (stage 1 §3.5).

- **zero-a:** w = 1 − O(b/a′). This is A0, so **r = MSE(A0)/MSE(A4)** within about 10⁻⁵ relative wherever b ≤ 10⁻⁶.
- **refit-a:** b is refitted to ε_s² ≈ b(ρν̂)², which gives b ≈ 5 to 12. Then w = (a′n + b′)/(bn + a′n + b′) ≈ a′/(a′ + b): **a constant weight close to A4's mean weight** (0.09 to 0.17).
- **zero-b and refit-b:** b is at the boundary, so r = 1 by construction.
- **zero-a′:** w = b′/(n(ax² + b) + b′). This is nearly A1, and exactly A1 where b′ is at the boundary.
- **refit-a′:** δ̂² = b′ρ² with b′ refitted (≈ 1.4 to 6.4). Then w = b′/(b′ + n(ax² + b)), so the weight **regains a dependence on ν̂**.
- **zero-b′:** w = 1/(1 + (a/a′)x²), the ν̂-free form of v3 §8.
- **refit-b′:** the same form, with a′ refitted (a change of at most 2%).

### 8.3 Revised prediction table

The original predictions stay visible. **A prediction holds** on a (system, seed) if the reading falls among the predicted readings and the point estimate falls in the predicted range.

| Row | Original prediction (draft of 2026-10-25, unchanged) | Revised prediction | Development evidence | What changed, and why |
|---|---|---|---|---|
| a, zero | large loss: "substantial", the largest r | r equals MSE(A0)/MSE(A4). Where A1 is the better single forecaster on calibration: lower bound > 1, reading "substantial" (lower > 1.05) or "needed; size not determined". Where A0 is the better single forecaster: no direction predicted. Not new evidence about R: the row restates A0 against A4. | Stage 1: 3.06 to 10.4, every interval excluding 1 at the full size (lower ≥ 1.94); DEV-1 pilot lorenz63 1.31 [0.60, 3.77]. Stored A0/A4: 2.3 to 10.1 over the 9 frozen cells; S1 1.40 | The mechanism changed: the weight becomes 1 (A0), not a′/(a′ + b), because b is at the boundary. The prediction is now conditional on the H2c comparator, because A0 was the better single forecaster on calibration on S2, S3 and S4 (DEV-3, unfixed estimator), and there A0/A4 was only 1.01 to 1.40 (S4 1.01). |
| a, refit | (same as zero; no separate prediction) | Constant weight. \|r − 1\| ≤ 0.25; no direction and no reading predicted ("lowers the MSE", "undetermined" and "substantial" all occur in development); r(a, refit) < r(a, zero) | Preview: 0.90 to 1.16 over 6 cells; for example lorenz63 DEV-1 0.90 [0.87, 0.95] (95%), rossler DEV-2 1.09 [1.06, 1.13] | **"Large" withdrawn for the refit mode.** The zero-mode loss comes from the parametrization (w → 1), not from R's information. A constant weight near the mean is about as good as A4 (A2/A4 0.62 to 0.99). |
| b, both | small: "negligible" or "small" | **"not identifiable (fitted at the boundary)"** on every admitted system where b is at the boundary (the M-2 rule). If b is not at the boundary on an admitted system, no prediction is made | b ≤ 3.9·10⁻⁹ in 9 of 9 frozen cells, 8.8·10⁻⁹ on S1; max \|Δw\| ≤ 8.4·10⁻⁸; stage 1 r = 1 within 3·10⁻⁹ | "Small" becomes "not identifiable". A boundary fit gives r = 1 by construction, so the row cannot measure the analog floor. |
| a′, zero | moderate: "substantial", r below a's | Nearly A1: r ≈ MSE(A1)/MSE(A4), \|r − 1\| ≤ 0.15, r(a′) < r(a, zero). Lower bound > 1 is expected where H2c's A4-versus-A1 part passes, with the reading "needed" (small, or size not determined); elsewhere "negligible" or "undetermined" | Stage 1: 1.00 to 1.09 (3 of 6 intervals excluding 1); stored A1/A4 0.95 to 1.14 frozen, 1.036 on S1 (H2c A4−A1 passed on S1, DEV-3) | "Substantial" becomes small and system-dependent. A4 already puts 82 to 89% of its weight on PLP. |
| a′, refit | (same as zero) | \|r − 1\| ≤ 0.1; reading "negligible" or "undetermined"; no direction | Preview: 0.996 to 1.026, every 95% interval containing 1 (half-widths 0.02 to 0.05) | New row-specific prediction: the refitted constant δ̂ brings ν̂ back into the weight, with no detectable effect. |
| b′, zero | about zero: "negligible" | \|r − 1\| ≤ 0.005. "Not identifiable" where b′ is at the boundary (frozen Rössler, S1 on DEV-3); otherwise "negligible", or "removing the term lowers the MSE" by less than 0.5% | Stage 1 \|r − 1\| ≤ 8·10⁻⁴; DEV-2 chua 0.9992 [0.9980, 0.99994] | The boundary case is added, and so is the possible tiny improvement, both seen in development. |
| b′, refit | (same as zero) | As zero-b′: \|r − 1\| ≤ 0.005, the same readings | Preview within 10⁻³ of 1 (excluding the stand-in artefact on Rössler, which the boundary rule covers) | As above. |

**Fitted coefficients (descriptive predictions, not rows).** On each admitted system: b at the boundary; b′ ≤ 0.1; a/a′ in [0.15, 0.30] (frozen 0.25 to 0.28, S1 0.21). For S2, S4, S5 and S6, these predictions are conditional on the V7 fix (F1 or F2): with an efficient estimator, a′ is expected near 1 and b′ near 0.

**Ordering of the point estimates.**

- **Zero mode:** r(a) > r(a′) ≥ r(b′) ≈ r(b) = 1, where A1 is the better single forecaster.
- **Refit mode:** no ordering between a and a′; both within 0.25 of 1; r(b) and r(b′) ≈ 1.
- **Original:** "r(a) > r(a′) > r(b) ≥ r(b′) ≈ 1, in both modes". **Withdrawn for the refit mode.**

> **Predictions, and why they were revised.** These predictions replace those of the draft of 2026-10-25, which are kept beside them and are also compared with the results. They were revised before any CONF seed was drawn, on development evidence only: WU-0036 stage 1 (DEV-1, DEV-2), the stored coefficients of the DEV-1, DEV-3 and DEV-4 runs, and a refit preview on DEV-1 and DEV-2 test states. This is permitted because the CONF seeds are fresh and are sealed after the predictions are frozen. The development data are not reused as confirmatory evidence. Zeroing a turns A4 into A0, and zeroing a′ turns it nearly into A1, so those two zero-mode rows restate comparisons the study already makes (A0 and A1 against A4). They are not new evidence about the conditions. In the refit mode, removing a leaves a constant weight near A4's mean weight, and the loss is predicted to be small and of either sign. The coefficient b, and b′ where it is fitted at the boundary, is predicted to be "not identifiable" rather than "small".

---

## 9. §13 item 9: which S1 λ_max a CONF run uses

**The mechanism** (`data.lyapunov_record`, `pipeline.Study`):

- **Cache location.** The cache is `<out>/cache/lyapunov.json`, keyed by system name only (WU-0021 review R8).
- **Fresh directory.** In a fresh output directory, the invocation computes λ_max with `lyapunov_guarded`, from the registry initial state with no seed, on the run's own device. It then writes the cache.
- **Pre-existing entry.** A new-form entry that already exists is read without recomputation.

**The two values.** Both are at the current specification (`max_dt` 0.005, 2·10⁶ steps; 974519a contains the re-specification decf0bd).

| Value | Source | Orbit max \|x\| |
|---|---|---|
| 0.11272865874045755 | the DEV-3 GPU run's own cache, written at 08:55 local, after the run started | 149.6 |
| 0.11220508610149857 | the WU-0021 CPU value | 166.35 |

**Why they differ.**

- **Different orbits.** The differing orbit maxima show that the two orbits decorrelated: a 2·10⁶-step chaotic Benettin run on two devices.
- **Size of the difference.** The difference, 0.47%, is about 1.2 single-run standard errors (0.39 to 0.47%) and 0.85 of the standard error of the difference. It is the estimator's statistical error, not a bias.
- **Validation.** Both values validate against 0.1121 within 3% (+0.56% and +0.09%).

**Answer.** A CONF run uses the value its own invocation computes on the official GPU at the frozen commit, in a fresh output directory. The reasons:

1. λ_max is a system constant defined by the frozen code on the official device. The GPU is official for this study (seq 44).
2. The value does not depend on the seed, so all three CONF seeds and the regeneration should reproduce it bitwise. That makes it a determinism check: a differing λ is a TD trigger in `compare_runs`.
3. Copying the CPU cache into a GPU run would make the official run depend on an artefact of another device, and the regeneration could no longer be judged "from the same inputs".
4. Choosing the value nearer the published 0.1121 would be selection on the referent.

**Effect on the results.** The 0.47% changes the time unit Δ by 0.47%, a shift of 0.14 steps at H_ref = 30 steps. All criteria are defined in steps, so no criterion depends on it beyond the statement of the LT unit.

> **λ_max in CONF runs.** Each CONF run and each regeneration writes to a fresh output directory with no `cache/lyapunov.json`. λ_max is computed by that invocation, on the official GPU at the frozen commit, from the registry initial state (it does not depend on the seed). The value expected for each admitted system is the one stored by the WU-0040 GPU runs at the frozen code. For S1 it is 0.11272865874045755 (DEV-3, +0.56% against the published 0.1121, standard error about 0.4%). It is recorded in the freeze record. A CONF value that differs in any bit is reported as a device or build change and changes no word. The CPU value 0.11220508610149857 (WU-0021) belongs to the CPU and is not used.

---

## 10. S3 (`rossler_z`): not admitted. I agree

The evidence is in the WU-0037 note, §4.6, §5.2 and the iteration study (DEV-3, CPU reproduction, 150 states):

1. **Wrong basin is ruled out.**
   - The far share is 0.13 to 0.35%, against a chance level of 0.1% and 0.1 to 0.5% on Lorenz-63.
   - The p95 cost scales as ρ². That is the signature of correct-basin fits (§4.1).
2. **The first-order premise of V7 fails at S3's ν.**
   - V7 compares δ with ρν, the first-order (Cramér–Rao) error. The median state has ν = 14.6 (p90 64.5), so ρν = 0.07, 0.15, 0.29 and 0.73 whitened units at the four noise levels.
   - The truth-started ratio is 0.997 for ρν < 0.03, then 1.12 in [0.1, 0.3), 0.89 in [0.3, 1) and 0.35 above 1. This is the progression expected when the error leaves the linear regime: second-order excess first, then saturation at the attractor scale.
3. **The best conceivable estimator-side fix is at the edge.**
   - The non-deployable truth start, converged to 60 iterations, gives slope 0.921 and a 5% median of 0.905, against the bar of 0.9. A 0.005 margin is below the seed-to-seed movement of a V7 median: the reproduction intervals are about ±0.05 at 150 states.
   - Every deployable start fails: F1 (slope 0.878) and F2 (1.24 at 2%). The pair start, converged, gives 1.116 at 2%.
   - Two converged starts disagree at 2% (1.008 against 1.116), so the objective has several minima in the poorly observed directions.
4. **A pass would not mean what V7 claims.**
   - The pair start passes only at 15 iterations, through cancellation between second-order excess and saturation.
   - Tuning iterations or starts until the median crosses 0.9 would be the kind of fit to the criterion that PRIME.2 rules out.
   - The theory that V7 protects (δ ≈ ρν in P1's seeds and in H1b) does not hold at these ρν either.

**Conclusion.** I agree with "not admitted". The reason is a property of the estimation problem (the z observable of Rössler is poorly observable at ρ ≥ 1%), not of the estimator. Restricting V7 to ρν < 0.1, or changing the observable or the noise levels, would be a design or criterion change, which the admission rule forbids. One remark on §13 item 8: S3 stores λ = 0.07165 against the frozen Rössler's 0.07172 (0.1% apart), so the Rössler referent does apply. It no longer matters for admission.

> **S3 (`rossler_z`) is not admitted.** The reason is that its estimation error is outside the first-order regime: the median ν is 14.6, so ρν reaches 0.15 to 0.73 attractor units at ρ ≥ 1% (WU-0037). The V7 check compares the error with its first-order prediction ρν. Even an estimator started at the true state and fully converged only reaches the band edge (median 0.905 at ρ = 5%, slope 0.921), and every deployable start fails. No estimator-side fix acts on this mechanism, and a pass reached by tuning would not show efficiency.

---

## 11. Uncertainty budget of the development numbers used here

The QoIs are the refit-preview ratios (§8) and the τ/SE estimate (§1.2).

| Source | Type | How estimated | Size | In the reported interval? |
|---|---|---|---|---|
| Test-state sampling | aleatory | paired moving-block bootstrap (block 5, 2000 resamples), both levels | half-widths 0.04 to 0.15 (refit-a, 95%) | yes |
| Refit on the test states instead of the construction states | estimator | the refit-b and refit-b′ rows, which would be exactly 1 on construction | 0.1% to 0.8% of r | no; below a tenth of the refit-a half-width; the boundary rule removes the artefact from the b and b′ rows |
| Oracle Monte Carlo (M = 200) | aleatory | inherited from stage 1 (§5): a rows 6·10⁻³ to 0.14, a′ rows ≤ 3.9·10⁻³ | as stated | no (state level) |
| Realized score against the oracle V | estimator | stage 1 approximation check (paired \|rel D\| ≤ 4.4%) | ≤ 4.4% of V(A4), not significant | no |
| τ/SE from 54 shared-seed pairs | aleatory | null SD of the mean z² about 0.24 (36 effective pairs); sensitivity without the largest pair | τ/SE 0.5 to 0.8 | no (a premise check, not a result) |
| Undercoverage of the per-seed intervals | numerical / method | WU-0006 reference coverage | about 1.16 in z² at φ = 0.3 | no; it is the reason the τ range is given as a range |
| Model form: frozen systems for the predictions about new systems | epistemic | not estimated; the predictions are conditional where the evidence is | — | no |

The intervals are percentile intervals at the stated level. Dependence is handled by moving blocks of 5 consecutive test states. Seeds: DEV-1 (pilot, commit 01d9fc7), DEV-2 (full, 6f1a8c8), and DEV-1, DEV-3 and DEV-4 (ensemble, 3dec086; extension 974519a and 392a069).

---

## 12. Items for the main session at P4 (not decided here)

1. **Implementation needs for WU-0039 and WU-0042** (all added leaves, so the leafdiff holds):
   - the boundary rule and its max |Δw|;
   - the censored count and the uncensored-50 rule for the horizon rows;
   - R²(∅) as a leaf;
   - endpoint Monte Carlo errors on the ratio rows;
   - chain tags in `compare_runs` for every new float leaf.
2. **Words to change in the draft's §3 item 3.** "p³ ≈ 1.6·10⁻⁵ per word, or about 8·10⁻⁴ over 54 words" is the pass-word figure. The fail-word and seed-averaged figures above should replace it, or stand beside it.
3. **§7.3 (profile predictions).** I did not revise it. The draft keeps it PENDING (WU-0040), and stage 1 has no profile evidence.
4. **O-3.** If the frozen three are not run on CONF seeds, the §8 predictions apply to new systems only, and the strongest evidence behind them (the frozen systems) stays development. S1 is the only new system with clean evidence (b and b′ at the boundary, a/a′ 0.21, A0/A4 1.40, A1/A4 1.036).
