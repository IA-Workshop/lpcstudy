# Phase J: LPC contribution study, plan

**DEVELOPMENT plan, adopted 2026-10-26 (owner: "Proceed", ledger seq 47; DV-1 to DV-5 and DS-1 to DS-7 agreed; DV-3 "with the intention of promoting it when confirmed").** WU-0045. Main session (claude-opus-5-5), 2026-10-26. Source: the student's follow-up proposal and notes, relayed by the owner on 2026-10-26 as "now the development priority". This plan implements that proposal. Section 1 lists every place where it departs from the proposal or from the current plan (ROADMAP §9, phase I).

Every number this phase produces is a development number (DEV seeds). It never appears beside the sealed CONF-1 result, and it never changes CONF-1.

## 0. Summary

- **Question.** Which of R, O, I and N carry information that helps two decisions, allocation (CP–PLP weight) and the predictability horizon? Do they interact? Is a limitation in the conditions themselves or in their deployable estimates?
- **Approach.** One data pass, then offline analysis.
  - Extend the opt-in state dump (`--states-dump`) so that it holds the profiles, the full-horizon oracle moments and the raw delay vectors for all three splits (J1).
  - Run the three core systems at the full preset on the GPU on development seeds (J2).
  - Every experiment A to E is then an offline analysis of the dumps (J3 to J5), with no further forecasting runs.
- **Why offline works.** For any weight w, the hybrid MSE of a state is exactly the quadratic V(w) = w²E_C + (1−w)²E_P + 2w(1−w)C of its oracle moments, on every horizon. WU-0036 checked this substitution against the stored realized scores: it passed 12 of 12 gating tests, with the low-power caveat that note states. So any allocation function can be scored at every horizon without a new run. The horizon of any blended forecast also follows from the same moment curves (`allocation.characteristic_horizon`).
- **Seeds.** An exploration set (DEV-1, DEV-3, DEV-4) is used to build and debug the analysis. Then the analysis script is frozen by commit hash. A replication set of five new development seeds (DEV-5 to DEV-9) is analyzed once with that frozen script.
- **Compute.** 8 full-preset GPU runs of about 40 to 46 minutes each (WU-0026 walls: 2319 to 2777 s), about 6 GPU hours, run serially under the lock. The analysis runs on the CPU and takes minutes per seed.
- **Critical path.** J1 dump (code) → J2 exploration runs → J3 analysis library (A, B, D) → J4 (C, E) → J6 freeze the script → replication runs → J7 report. J0 (applied-mathematician) runs in parallel with J1. A quick look on the existing DEV-2 dumps (J3a) can start today.

## 1. Deviations and decisions

### 1.1 Deviations from the current plan (need the owner)

| # | Deviation | Recommendation |
|---|---|---|
| DV-1 | **Priority.** Phase I P3 to P6 (extension development runs WU-0040, pre-registration WU-0041, CONF-2 to CONF-4) are paused behind phase J. The ruled phase I plan sets no dates, so only the order changes. WU-0039b's code stays on develop and is reused here. | Pause P3 to P6. WU-0040's runs may use the GPU only when no phase J run needs it. |
| DV-2 | **The December empirical-baseline comparison is deferred.** Part of it is covered here: experiment D includes A3 (the learned allocator adapted from Heuer et al. 2026, which works on the raw delay vector X_t) and a gradient-boosted model on X_t as empirical benchmarks. | Defer it. Revisit after J7. |
| DV-3 | **Status: development, exploratory.** Phase J runs on DEV seeds and reports estimates with readings, no verdict words. A confirmatory round (pre-registration, sealed seeds) would be a separate owner decision after J7. | Accept. The student's §7 already asks for "follow-up investigations". |
| DV-4 | **Five new development seeds, DEV-5 to DEV-9,** drawn and registered in `seeds/development_seeds.json` before any exploration result is read. They are the held-out replication set. | Approve the draw. It is development only, and LPC.PC.7 is untouched. |
| DV-5 | **A code change to the dump** (`lpcstudy/dump.py`, `pipeline.py`, schema /3). It is flag-gated and additive. With the flag off, nothing runs. With it on, `results.json` differs only in `provenance.states_dump`, as today. | Proceed. The acceptance criterion in §5 makes it checkable. |

### 1.2 Departures from the student's proposal (the plan says why)

| # | Proposal says | Plan does | Why |
|---|---|---|---|
| DS-1 | Experiment A: drop one condition at a time (5 models) | All 16 subsets per decision, profile and horizon. The five drop-one models are among them, and Shapley shares and the {R, O} baseline of D come at no extra cost | 16 refits of a 4-feature model take seconds |
| DS-2 | D rung 2: "initial error seeds only" | This rung is the {R, O} subset plus the zero-parameter separation formula w = 1/(1 + e^{2(R−O)}) (A4o on the oracle profile, A4 deployable) | R = ln ε/ρ and O = ln δ/ρ *are* the log initial-error seeds (v3 §5). "Beyond the seeds" therefore means "what I and N add to {R, O}" |
| DS-3 | B: "separate effects vs interaction" | Interaction is defined on a stated target scale: logit w\* for allocation, log T for the horizon. Tests use gradient boosting with `interaction_cst` (additive model vs additive plus one pair) | On the w scale, the separation formula makes R × O "interact" through the link alone. Trees are invariant to monotone transforms of each feature, so only the target scale matters (M-3) |
| DS-4 | Horizon "calibration, accounting for forecasts that do not exceed the threshold" | Predict horizon quantiles (10%, 50%, 90%) by quantile-loss boosting. Score with pinball loss, Harrell's C, and quantile coverage | Censoring is fixed at H_max = 8 LT. A predicted quantile below 8 LT is judged exactly even for censored states (a censored state is known to lie above it), so coverage needs no survival model (M-4) |
| DS-5 | E: explain H2a, H2e and H3c "of the existing experiments" | E explains the same phenomena in the DEV realizations. It first checks that they reproduce (e.g., a wide H3c interval for Lorenz-63). It links to CONF-1 only in words | The sealed run has no per-state dump, and it is not re-run or re-analyzed. DEV numbers are never set beside CONF-1 |
| DS-6 | §7: "multiple independent runs" | 3 exploration seeds and 5 replication seeds, one realization each, with a replication rule fixed before the replication runs (M-6) | Exploration seeds are seen while the analysis is built. Only the replication seeds are held out |
| DS-7 | The three systems "initially" | Lorenz-63, Rössler and Chua only. The extension systems S1 to S6 are out of scope for phase J | Five of the six fail V7 (provisional); see DV-1 |

### 1.3 A note on reading the existing result (for the student)

The student reads H2a's failure as support for "instability matters for allocation" and for a link between horizon and allocation. The CONF-1 rows are consistent with that reading but do not establish it:

- H2a(ii) interior failed on Lorenz-63 and Chua with a positive partial correlation of logit w\* with Λ̃ given the seeds.
- The H3b weight tree failed on Lorenz-63 (Λ̃ importance 0.606).
- Q-N read "substantial" for N on the w\* = 0 indicator on all three systems.

v3 §7's pre-registered reading of an H2a failure (anisotropic seeds) was not tested. Experiments A (I's drop-one value for allocation), B (R × I and O × I) and C (shared information) test the student's reading directly. A and C could also come out against it.

## 2. What already exists and is reused

| Item | Where | Use in phase J |
|---|---|---|
| Q-N procedure (gradient boosting, train construction + calibration, test, models fixed in resamples, block bootstrap) | `analysis.qn_profile_block`, `qn_regressor` | The default learner and resampling for every model, for comparability |
| WU-0039b rows (b1) ΔR²_X, (b2) Shapley, (b3) A5 without X, and the A4 coefficient rows | `lpcstudy/ablation.py`, in `results.json` | They come free with J2's runs, at H_ref, as a cross-check of J3's drop-one and Shapley numbers |
| MSE-ratio reading table (margin 1.05) | `ablation.ratio_reading` | Reading of every loss ratio in A to D |
| V(w) substitution for realized MSE | WU-0036 note §2 | Scoring any weight function at every horizon; re-checked on the new dumps (J3 gate) |
| A3 learned allocator from X_t | `allocation.py`, `networks.py`; `state_mse/A3` in the dump | Empirical benchmark in D |
| A5 regime trees and leaf ids | dump `core/a5_leaf` | E (H3c) |
| Sweep moments and analog seeds per library size | dump `sweep/`, `h1a/` | E (H2e) |
| Existing dumps: DEV-1 pilot, DEV-2 full (commit c9bb981, test split, 5 horizons) | `lpcstudy-wt/run/r1-c9bb981/runs/` | J3a quick look only |

## 3. Design common to all experiments

### 3.1 Data (per system and seed, core cell ρ = 1%, N_lib = 10⁴)

- **Splits.** Construction (2000), calibration (1000), test (1000) states. Models are fitted on construction + calibration and scored on test, as in Q-N.
- **Profiles.**
  - Oracle F = (ln ε_s/ρ, ln δ/ρ, Λ̃, ln(N + 0.01)) per state.
  - Deployable F̂ per state and evaluation draw (E = 4).
- **Moments.** E_C, E_P and C on horizons 1 to 240 steps for calibration and test. Construction keeps the grid it has (every LT plus the evaluation horizons). J1 adds the full grid for construction as a separate copy, without changing what A3 trains on.
- **Horizons scored.** 0.25, 0.5, 1, 2 and 4 LT (the v3 evaluation horizons). H_ref = 1 LT is the headline.
- **Horizon target.** The characteristic horizon T of a stated blending policy at θ = 0.2, from the moment curve, censored at 8 LT.

### 3.2 The two decisions and their losses

- **Allocation.** For a weight function g(·) at horizon H, the excess MSE is

  L_A(g, H) = mean over test states of [V_i(g(F_i)) − V_i(w\*_i)],

  computed exactly from the moments. For deployable profiles, it is averaged over the E draws, as in WU-0036. The reported quantities are:
  - the ratio r = MSE(g)/MSE(reference), read by the 1.05 table;
  - the gain share G(g) = [V(A2) − V(g)] / [V(A2) − V(w\*)], the fraction of the attainable gain over one global weight per horizon (A2) that g recovers.

  Note: V(w) − V(w\*) = κ(w − u)² − κ(w\* − u)², with curvature κ = E_C + E_P − 2C and unclipped minimizer u. Fitting u with sample weight κ is therefore fitting the decision loss itself (M-2 decides the fitting target).
- **Horizon.** For a fixed policy, predict the quantiles q_τ(F) of T for τ ∈ {0.1, 0.5, 0.9}. Report:
  - the pinball loss at τ = 0.5;
  - Harrell's C;
  - the coverage of each quantile, P(T ≤ q̂_τ), and of the 80% interval;
  - the share of censored states.

### 3.3 Feature sets (every model is refitted on its permitted inputs only)

- **Constant:** A2 for allocation; the training-set quantiles of T for the horizon.
- **Separation formula:** w = 1/(1 + e^{2(R−O)}), with no fit. The horizon has no zero-parameter analogue (M-5 may propose the Lyapunov form ln(θ/e₀)/Λ).
- **Each of the 15 non-empty subsets of {R, O, I, N}.**
- **Empirical:** X_t (the delay vector) alone, with the same learner; plus A3 for allocation.
- **X_t + F:** does the profile add to the raw state, and does the raw state add to the profile?
- Each set is fitted on the **oracle** and on the **deployable** profile (X_t is deployable by construction).

### 3.4 Uncertainty, multiplicity, replication

- **Within a run.** Moving-block bootstrap over test states in time order (blocks of 5, 2000 resamples), with models held fixed. Resample index sets are shared across models, so differences are paired. A failed resample is counted (M-7). A part with fewer than 50 states reads "undetermined".
- **Training variance** is not in that interval. It enters only through the replication seeds, and the report says so.
- **Families** (Holm at 5% within each, per system, decision, profile and horizon):
  - A: the 4 drop-one rows;
  - B: the 6 pairs, with R × I and O × I named primary in advance;
  - D: the rungs against the full profile.
- **Replication rule (M-6, fixed at J6 before the replication runs).** Proposed: a reading is "replicated" if it holds on at least 4 of the 5 replication seeds. Otherwise it is "seed-dependent". There is no pooling across seeds.
- **Labels.** `DEVELOPMENT (DEV-n): exploratory, not a hypothesis test` on every table and figure. Readings are estimates; none is pass or fail. A Shapley share or an interaction is predictive, not causal.

## 4. Experiments

Predictions are written now, before any phase J data. Where the plan does not predict, it says so.

### A. Individual contribution and ablation

- **Compute.** For each decision, profile, horizon and subset: L(S). Report:
  - drop-one Δ_X = L(F∖X) − L(F), and the ratio L(F∖X)/L(F) with its paired interval, read by the 1.05 table;
  - the Shapley share φ_X over the 16 subsets, with Σφ_X = L(∅) − L(F) as an identity check;
  - for allocation, G by subset.
- **Cross-check.** At H_ref, oracle profile, the drop-one ΔR² on Q-N's targets reproduces WU-0039b's (b1) leaves of the same run.
- **Predictions (oracle profile).**
  - Allocation: R and O carry most of the value at 0.25 to 1 LT, and their sum dominates. I's drop-one loss grows with the horizon and is not negligible at 2 to 4 LT (from H2a(i), the spread of w\* across horizons). N matters mainly through the w\* = 0 states.
  - Horizon: I is the largest share. R and O add through the initial error.
  - Deployable: O and I lose most relative to the oracle (ν̂ cancels in A4, v3 §8). R loses least.

### B. Pairwise interactions

- **Compute.** For each pair (X, Y), compare two models:
  - M_add: four features, `interaction_cst = [[R], [O], [I], [N]]`;
  - M_XY: the same, with [X, Y] allowed to interact.

  Statistic: L(M_add) − L(M_XY), paired interval, Holm over the 6 pairs. Also report the total interaction value L(M_add) − L(M_full) as a ceiling, and Friedman's H² of the full model as a descriptive measure. The allocation scale is logit w\* (interior states, as Q-N) with the w\* = 0 indicator as its own part. The horizon scale is log T (median quantile model). M-3 confirms the scales.
- **Predictions.**
  - Allocation (logit scale): R × I and O × I are not negligible at 2 to 4 LT and small at 0.25 LT. This is the anisotropic-amplification mechanism behind an H2a(ii) failure: the seeds' effect on w\* depends on how unevenly the two errors grow. R × O is small, because separation is additive in R − O on this scale.
  - Horizon (log scale): all pairs are small. Lyapunov theory gives log T ≈ log ln(θ/e₀) − log Λ, which is additive in a seed term and an instability term. No prediction is made for pairs with N.

### C. One profile for both decisions

- **C1. Separate performance.** Allocation g(F) and horizon h(F) from the same profile. Full versus reduced profiles versus the separation formula versus empirical, from A and D.
- **C2. Shared information.**
  - Does the horizon model using only the allocation output ĝ(F) (all five horizons, five features) match the horizon model on F?
  - Conversely, does ĥ(F) predict the weight?
  - Is the ordering of the Shapley shares of the two tasks rank-correlated (descriptive, 4 items, no test)?

  A small loss in the one-way bottleneck supports "the same local information informs both decisions".
- **C3. The deployable chain, in the order the proposal asks for.**
  1. The horizon of a fixed policy that uses no LPC (A2 weights), predicted from F̂.
  2. The full system: allocation ĝ(F̂) gives the hybrid. Its horizon T_ĝ (from the moment curve with the ĝ weights) is predicted by ĥ(F̂), with ĥ trained on construction T_ĝ.

  Joint operating metrics for the full system:
  - hybrid MSE;
  - the **false-trust rate** P(T_ĝ < q̂_0.1), with target 10%;
  - the mean trusted horizon q̂_0.1.

  These are compared against A2 + constant horizon and against A4 + KM horizon (the A5-style leaf horizon).
- **Prediction.** C2: the bottleneck keeps most of the horizon skill at 2 to 4 LT and less at 0.25 LT. No prediction for C3.

### D. Incremental value beyond simpler predictors

- **Ladder** (each rung against the full profile and against the rung below):
  1. constant;
  2. separation formula, then {R, O} learned;
  3. single conditions and subsets (from A);
  4. full F;
  5. empirical X_t, A3;
  6. X_t + F.
- **Theory gap and estimation gap.** Theory gap = L_A(oracle F), the excess over the state-optimal weight that remains even with exact conditions. Estimation gap = L_A(deployable F̂) − L_A(oracle F). For the horizon, the same decomposition is made with the pinball loss. Report them per condition by swapping one oracle coordinate at a time for its deployable estimate (4 hybrids). This answers whether the limitation is in the conditions or in their estimates.
- **Predictions.**
  - The full oracle profile beats {R, O} at 2 to 4 LT and roughly ties it at 0.25 LT.
  - The deployable estimation gap is concentrated in O and I.
  - X_t + F is not worse than X_t alone. No prediction for X_t against F̂.

### E. Mechanisms and cross-system differences (explanatory, no tests)

- **E-H2a: directional amplification.** For each state, the amplification mismatch m(H) = ln[E_C(H)/E_C(1)] − ln[E_P(H)/E_P(1)]. Separation implies m ≈ 0, and then w\* is constant in H. Analyze:
  - m(H) and the drift of w\*(H) by tercile of I;
  - the error correlation C/√(E_C E_P) against H by tercile;
  - whether R × I and O × I from B line up with m.
- **E-H2e: library size and correlation.** On the sweep states (the first n_test_sweep test states, the same states as the core profile):
  - the per-state change in CP–PLP error correlation from 10³ to 10⁵, stratified by terciles of R, O, I and N;
  - its association with the change in the analog seed (`h1a/` seed_sq).

  Candidate mechanism, stated before looking: a larger library shrinks the analog error until both errors are dominated by the shared observation noise, so the correlation rises most where R falls most.
- **E-H3c: why A5 against A4 varies by system.** First confirm that the DEV realizations reproduce the pattern (H3c ratio and interval per system and seed from J2's `results.json`). Then, per system:
  - the tail share of the per-state loss (share of the top 1% of states), and the block autocorrelation of per-state differences;
  - the K chosen and the leaf occupancy;
  - within-leaf versus between-leaf variance of w\*;
  - LPC marginal distributions and pairwise dependence (from A and B);
  - where the large-loss states sit in the profile (and, for Lorenz-63, near the lobe switch).

  Candidate explanation, stated now: Lorenz-63's wide interval comes from a heavy-tailed per-state loss in high-I states, which a few regimes average badly. Rössler's narrow interval comes from a near-unimodal profile.
- **Output.** Figures and tables with the DEVELOPMENT label. Each mechanism reads "consistent", "not consistent" or "not determined". No causal claim.

## 5. Units, order, acceptance criteria

Minimal formality (standing owner rule): one agent per unit, no review rounds, no unit logs beyond a short status line in `queue.md`. Numerical code gets tests with an independent reference (skill `numerical-test`). Test runs are blast radius only.

| Unit | Who | Depends on | Content | Accepted when |
|---|---|---|---|---|
| WU-0045 (J0) | applied-mathematician | this plan | Fix M-1 to M-8 (§6) in a short note; refine the predictions where the math says so | Every M item answered, or marked as an open limitation |
| WU-0046 (J1) | developer | — | Dump schema /3 for all three splits: oracle profile, deployable profile, delay vectors X_t, full-grid E_C, E_P, C (construction as a separate full-grid copy), the A3 per-draw weights at the evaluation horizons, oracle T at θ = 0.2 | (i) Smoke DEV-0, flag off: leafdiff against develop 0 changed and 0 removed. (ii) Flag on: `results.json` equal except `provenance.states_dump`. (iii) Schema /2 keys unchanged in name and meaning. (iv) The dumped construction moments at the allocator grid equal the moments A3 trained on, bitwise. (v) No new `make_rng` draw |
| WU-0047 (J2) | main session (GPU, under the lock) | WU-0046; owner DV-4 | Register DEV-5 to DEV-9 (do not read them yet). Run DEV-1, DEV-3, DEV-4: full preset, three core systems, `--skip-robustness --states-dump`, GPU | Manifest line per run (commit, seed id, device, wall, sha256). Gate V1 to V7 per system and seed |
| WU-0048 (J3) | developer | WU-0046 (the schema); J3a can start now | `lpcstudy/contribution.py` (pure functions on dump arrays) and `tools/lpc_contrib.py` (reads the dumps, writes JSON + markdown). Common machinery, then A, B, D | Tests: (a) the κ-form excess loss equals V(w) − V(w\*) within 1e-12 relative. (b) Σφ_X = L(∅) − L(F) within 1e-12. (c) On a synthetic additive target, every pair's interaction gain is within the bootstrap null band. On a target with a planted X × Y term, that pair is detected and the others are not. (d) Quantile coverage on synthetic data with known quantiles and fixed censoring. (e) Harrell's C equals a brute-force count on a small case. (f) The WU-0036 V(w) substitution check, re-run on the new dumps for the full-profile ĝ: passes at its stated rule. (g) Drop-N at H_ref reproduces WU-0039b (b1) |
| WU-0048a (J3a) | developer | none | Quick look: A, B, D for allocation, oracle profile, 5 horizons, on the existing DEV-2 full dumps (test split only; cross-fitted by contiguous blocks) | Prototype numbers for the student, labeled "prototype, old code c9bb981". Not carried into the report |
| WU-0049 (J4) | developer | WU-0048 | C (C1 to C3) and E (E-H2a, E-H2e, E-H3c) | Tests for the horizon-of-a-policy computation against `characteristic_horizon` on hand-built curves. E figures regenerate byte-identically from the script |
| WU-0050 (J5) | main session | WU-0047, WU-0049 | Exploration report on DEV-1, DEV-3, DEV-4; predictions compared; any analysis change made now | Every number traced to a dump or `results.json` leaf |
| WU-0051 (J6) | main session + applied-mathematician | WU-0050 | Freeze: record the analysis commit hash and the replication rule (M-6). Then run DEV-5 to DEV-9 (GPU, ~4 h) | The script is unchanged between the freeze commit and the replication analysis (`git diff --quiet`) |
| WU-0052 (J7) | main session | WU-0051 | Replication analysis, run once; the final phase J report for the owner and student | Readings per system: replicated or seed-dependent. Departures from the predictions stated plainly |

Parallel start, today: WU-0045 (math), WU-0046 (dump code) and WU-0048a (quick look) are independent.

## 6. Open points for the applied-mathematician (WU-0045)

- **M-1. Loss aggregation across horizons.** Report per horizon only, or also a horizon-averaged loss? Proposed: per horizon, with H_ref as the headline.
- **M-2. The allocation fitting target.** Options:
  - u with weight κ (the exact decision loss; predictions clipped to [0, 1]);
  - Q-N's two-part logit target, composed;
  - a custom logistic-link additive model.

  Proposed: u with κ for A, C and D, and the logit scale for B.
- **M-3. Scales for interactions.** Confirm logit w\* and log T. Say whether to also report the w scale as a sensitivity.
- **M-4. Horizon calibration under fixed censoring at 8 LT.** Confirm quantile-loss boosting and exact coverage when q̂ < 8 LT. Decide the handling when q̂ ≥ 8 LT, and the C-index tie rule.
- **M-5.** A zero-parameter horizon baseline (Lyapunov form), if one is well posed.
- **M-6. The replication rule over 5 seeds,** with its error rates under independence.
- **M-7. Failed resamples in estimate rows** (no unfavourable tail): same answer as phase I M-4.
- **M-8. The deployable V(w) substitution.** WU-0036 validated it for A4 weights. Is that enough for learned weights with stronger dependence on the draw's own window, or does J3 test (f) need a tighter rule?

## 7. Out of scope

- Any change to CONF-1, its files or its words.
- The confirmatory seed and `--confirmatory`.
- The extension systems S1 to S6 in phase J (DV-1, DS-7).
- New forecasters, new systems, or new LPC definitions. The four conditions are used as v3 §5 defines them.
- A confirmatory version of phase J (possible later, as an owner decision; DV-3).
