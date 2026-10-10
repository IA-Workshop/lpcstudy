# Audit of the LPC Study Decision Plan (v1, 2026-10-10)

Adversarial review of the 2026-10-06 decision plan, the methods document (v1), the suggested proposal edits, the theorem program and the pilot results, against the 2026-10-30 deadline for the proposal and methods description.

## Spot checks against `pilot_results.json`

- **F6 confirmed.** The analog proxy slope is 0.261/0.262/0.263 with a floor near 0 on all three systems. The estimation proxy slope is 1.00–1.06.
  - On Lorenz-63 and Rössler, ν̂ therefore cancels in A4.
  - On Chua the fitted estimation floor is 0.062, so ν̂ cancels only partially there. This is a small correction to F6.
- **F3 confirmed.** Regret is computed as A4o regret over A1 regret, scaled by A1's ratio. A4o's regret ratio at 1 LT is about 0.19 on Lorenz-63, so the 5% bar cannot be met even with oracle seeds.
- **F8 (H1d) confirmed.** PLP median ratio, with the criterion that the interval exclude 0.8:

  | System | Median ratio | Interval |
  |---|---|---|
  | Lorenz-63 | 0.746 | [0.617, 0.850] |
  | Chua | 0.654 | [0.574, 0.754] |

- **F5: not verified.** I did not check the claim about ISEF's AI-disclosure rules. Check the current ISEF rules directly.
- **F2: disagreement.** The auditor recommends demoting the fourth LPC. That conflicts with the PI's standing decision to keep four coordinates and let the data show whether N reduces to three. The recommended alternative is in the final section.

---

## 1. Verdict

The plan is not on scope for 10/30. It answers "what is needed to decide every question" and then treats that answer as the work plan. That conflates two deadlines:

- **the fair** (next spring) needs results;
- **10/30** needs a proposal and a methods description a student can defend.

Nothing in the plan's "what's needed" column is required for 10/30:

- the full preset;
- replicates;
- the thinning check;
- the Lorenz-96 fix;
- the misspecification arm;
- Lean staging (5–8 agent-days).

Several of these would also add material the student must then own.

The scientific problems are:

- **The fourth LPC.** The documents are inconsistent on it, and the theorem program admits that H1f cannot discriminate between the two outcomes.
- **H3a.** The regret criterion is infeasible even with oracle seeds.
- **The status table.** It mislabels at least five hypotheses relative to `pilot_results.json`.
- **A4.** As fitted, the deployable closed-form rule is essentially a function of R/ρ alone.

The pilot is a good exploratory study. The honest path to 10/30 is a sharply reduced, pre-registered design with two or three hand-proved propositions, not a larger run.

## 2. Findings (most severe first)

### Blockers

**F1 — scope — the decision plan as a whole.**

The plan lists only work that comes after 10/30, yet claims about one day to deliver all of it. None of its five rows is needed to write a proposal and methods.

The one-day claim covers:

- freezing the pre-registration;
- five trajectory replicates, which needs a pipeline refactor and multiplies core-cell compute by five;
- the thinning-doubling check;
- a Lorenz-96 PLP fix with three untested alternatives. That is a research task, not a fix.

Meanwhile the student must absorb:

- four systems;
- 16 hypotheses plus T1, which is 48 or more system-level tests;
- nine rules;
- four LPCs, each with an oracle and a deployable estimator;
- the statistical machinery: gradient boosting, CART, Kaplan–Meier, log-rank, Holm, block bootstrap;
- the estimation machinery: LM refinement, Levina–Bickel, AMI;
- twelve or more theorems.

An ISEF Mathematics judge interviews the student. Breadth the student cannot explain is penalized.

*Fix:* write two separate plans, one for the 10/30 proposal and methods and one for the runs after 10/30. Drop the one-day framing.

**F2 — inconsistency — H1f's direction contradicts its own theory.**

- The edits document (E4.1) says the theory predicts N is reducible to the other three.
- The theorem program (L11) says N is not reducible pointwise, and that either result is consistent with L11.
- The methods document (M9 H1f) calls redundancy "the theory's prediction for the PLP side", but N is defined on the CP side.
- The decision plan says L11 is tested by H1e and H1f.

The recommended 0.05 margin also flips the pilot's only clear oracle-level results to inconclusive:

- Rössler: 0.089 [0.042, 0.150];
- Chua: 0.072 [0.017, 0.126].

At margin 0.01 these read as "adds information"; at 0.05 they are inconclusive.

*Auditor's fix:* demote N to an exploratory, oracle-level coordinate. The 10/5 review's B1 recommended this, and the same-day edit E1.13 reversed it without a recorded reason.

**F3 — validity — H3a's 5% regret criterion is unattainable by design.**

`regime_regret` divides by the mean over states of min(E e_C², E e_P²). The pilot's regret ratios at 1 LT:

| Rule | Lorenz-63 | Rössler | Chua |
|---|---|---|---|
| A4o | 0.189 | 0.090 | 0.455 |
| A3 | 0.42 | 0.24 | 0.51 |
| A1 | 1.05 | 0.24 | 0.50 |

- `_choose_regimes` fell through to the K=5 fallback on every system, and RESULTS.md doesn't say so.
- The pilot report attributes the regret floor to proxy noise. But A4o has no proxy noise and still sits at 9–45%, so the floor is mostly closed-form mismatch.
- H3b presupposes a Lipschitz hypothesis that the deployable R² (−0.02 to 0.07) already refutes.

*Fix:* replace H3a with a feasible relative criterion, or use H3d. Drop H3b. Correct the attribution in the pilot report.

**F4 — inconsistency — N is both library size and the fourth LPC.**

The collision appears in methods M2–M3, M5, M9, the theorem program (notation table vs. L12) and the decision plan.

*Fix:* rename library size to N_lib everywhere, including the code's labels.

**F5 — scope/compliance — authorship and AI use.**

- The Lean proofs are by an agent, on the PI's pre-existing library.
- The student must be able to reproduce the proofs at the board.

*Fix:* the student proves two or three propositions by hand. Lean becomes future work. Add an AI-use and mentor-contribution statement. *(Check the current ISEF rules.)*

### Major

**F6 — A4 is a function of R/ρ.**

The fitted proxies are ε̂² ≈ 0.26(Rν̂)² and δ̂² ≈ (ρν̂)², so A4 = 1/(1 + 0.26(R/ρ)²) and ν̂ cancels. On Chua, the 0.062 estimation floor keeps a small ν̂ dependence.

- Observability therefore plays essentially no role in the deployable allocator.
- This explains why A4 transfers to Chua: the constant 0.26 is the same on every system.

*Fix:* disclose it. Either accept A4 as a recurrence-only rule, or redesign δ̂.

**F7 — the deployable profile carries almost no information about w\*.**

Out-of-sample R² for logit w*:

| Profile | Lorenz-63 | Rössler | Chua |
|---|---|---|---|
| Deployable | about −0.02 to 0.0 | 0.04–0.07 | 0.04–0.05 |
| Oracle | 0.49 | 0.34 | 0.25 |

The misspecification arm is new scope, not a fix. Under model error, the seed × amplifier law for PLP collapses, so the arm needs its own theory and its own proxy.

*Fix:* keep the exact model as the primary design and state the limitation honestly.

**F8 — the decision plan's status table disagrees with the JSON.**

- **H1c is missing.** It is decided against: the CP slopes are 1.22–1.63 with intervals above 1.
- **H1d is decided against on Lorenz-63 and Chua,** not "near threshold".
- **H3c:** on Lorenz-63, Λ has weight-tree importance 0.89. That is not near threshold.
- **H2c is undecided on Lorenz-63:** both intervals include 0.
- **H1e:** Chua's ε̂ also fails (0.679), so "fails on N alone" is false.
- **H2b's library trend is diluted, not absent.**
  - Chua at ρ = 1% passes.
  - Medians rise 3–5× from N_lib = 10³ to 3×10⁴ on every system.

**F9 — the H2b amendment hides a systematic dip.**

From N_lib = 31623 to 10⁵, median w* falls in all six (system, ρ) cells. No interval on the medians was ever computed, so "within sampling noise" is unverified.

*Fix:* report the monotone-median check with bootstrap intervals, and investigate the dip.

**F10 — several "laws" are near-tautological.**

- **H1a.** With common random numbers and a Gauss–Newton estimator, the slope is 1 by construction: [1.0007, 1.0028]. Reclassify H1a as a validation check.
- **H2b's "< 0.95" clause** is vacuous.
- **H2e.** The gain is ≥ 0 by construction under the per-horizon w*, and the 0.9 bar is arbitrary.

**F11 — the theorem ↔ hypothesis mappings are overstated.**

- **L3** is a matrix identity certified by a unit test. No experiment tests it.
- **L5** is used to compute w*, so it is not tested either. No theorem predicts w* rising with ρ or with N_lib.
- **L9 is not computed, and L8′ is vacuous on Lorenz-63.**
- **H1c's statistic assumes an isotropic seed covariance.** Analog seeds are anisotropic, so the CP superlinearity may come from anisotropy rather than from leaving the linear region.
- **L10's K^(−2/p) rate predicts decreasing regret,** not flat regret.
- **L3's title "affine invariance" is wrong.** The statement proves orthogonal invariance.

**F12 — post-hoc amendments and the "confirmatory" label.**

Rules changed after the pilot:

- H2a was restricted;
- H2b's monotone check was dropped;
- H1f was added;
- the analog proxy R → R·ν̂ was chosen on the H1e metric.

The record also says "M = 100 misses ±0.05", but M = 100 was never run.

On multiplicity:

- only the three primaries are Bonferroni-adjusted;
- the "partially supported" verdict carries about 14% type-I error under a global null;
- there is no TOST framing for the equivalence tests;
- there is no precision table.

*Fix:* label the full run a "pre-registered replication with amendments", and add a dated amendment log and a precision table.

**F13 — the methods document borrows definitions from an absent document.**

It cites "FW" propositions, A6 and §8.3, none of which are defined in the materials.

*Fix:* add one cross-reference table (FW ↔ L ↔ statement).

**F14 — the deployable N̂ does not estimate the defined N.**

- **Center and noise level.** The bootstrap perturbs the *noisy* observation, so it samples at √2·ρ about a displaced center.
- **Zero inflation.** With only 16 draws, many states return exactly 0.

More draws reduce the variance, not this bias.

**F15 — Lorenz-96 and T1.**

- The proposed fix is untested research.
- Chua is both a core system and a transfer target, which makes E7 partly circular.

*Fix:* drop Lorenz-96 and T1 from the 10/30 proposal.

### Minor

- **Pilot report.**
  - "Most states at w* = 0" overstates it: q25 is 0, so the share is 25–50%.
  - The "N not predictable" R² values are oracle values, and a negative out-of-sample R² indicates an overfit GBM.
  - RESULTS.md's rounding hides H1a's degenerate interval.
- **Hypothesis numbering and criteria drift.**
  - The 10/5 review uses different hypothesis numbers.
  - E4.1 (H2a, H3c) and M9 state the criteria differently.
- **H1b.** It is fit on the mean, which heavy-tailed wrong-lobe analogs dominate, and Rössler's floor test passes trivially.
- **Redundant rule.** A4f is identical to A4. Drop it.
- **Statistics.**
  - The H1f bootstrap ignores GBM training variability.
  - H2d(ii) is a sign test with n = 5.
  - The choice of block size 5 is not justified.
- **Compute.** The estimate of several hours excludes the replicates.

## 3. Cut list

**Drop:**

- H3b;
- the 5% regret bar in H3a;
- H1f as a pass/fail test;
- A4f;
- Lorenz-96 and T1;
- the "partially supported" verdict;
- the H2b "< 0.95" clause;
- the one-day bundle on the 10/30 critical path.

**Defer to future work:**

- Lean;
- the misspecified-PLP arm;
- replicates and the thinning check;
- E7 and most of E8;
- theorems L2, L3, L4, L8′, L9, L10′ and L12. Cite these as standard results, not contributions.

**Keep:**

- **Systems:** Lorenz-63 and Rössler; Chua optional.
- **Rules:** A0, A1, A2, A4, A5, A4o and A*.
- **About 10 hypotheses.** H1a becomes validation check V7.
- **Propositions the student proves by hand:**
  - P1 = L5 + L7 (optimal weight and the horizon-gain bound);
  - P2 = L11(b) (retrieval stability and the spread bound);
  - optionally P3 = L10 (regret identity and floor).

## 4. Minimum viable plan to 10/30

| Dates | Owner | Task |
|---|---|---|
| 10/10–10/12 | PI | Make the decisions in §5; check the current ISEF AI-use and Research Plan rules. |
| 10/12–10/14 | Claude | Methods v2, at most 8 pages: apply the cut list; rename N_lib; add the notation table, the cross-reference table, statements of P1–P3, the precision table and the amendment log; add a "Known limitations" box covering F6 and F7. |
| 10/14–10/21 | Student, about 1 h/day | Rewrite proposal §1–§5 in their own words; replace the RQ block; attempt P1 and P2 on paper with the PI; reproduce one pilot figure. |
| 10/21–10/24 | PI, then Claude | PI reads for ownership; Claude does a consistency-only redline. |
| 10/24–10/28 | Student | Final edits and ISEF forms. |
| 10/29 | — | Buffer. |
| 10/30 | Student | Submit. |

**Experiments to specify, not run, by 10/30:**

- **E0:** the validation gate, V1–V6 plus V7.
- **E1:** the noise sweep.
- **E2:** the library sweep.
- **E3:** the mechanism study.
- **E4:** allocation.
- **E6:** regimes.
- **E5:** secondary.

## 5. Decisions the PI must make (auditor's recommendations)

1. **Fourth LPC:** demote to exploratory, oracle-level only. *(See my alternative below.)*
2. **Model:** exact model only for the primary design; misspecification becomes future work.
3. **Systems:** Lorenz-63 and Rössler as core, Chua optional; drop Lorenz-96 and T1.
4. **Proofs:** the student proves P1 and P2 by hand; Lean is deferred; add the AI-use and mentor statement.
5. **Amendments:**
   - report H2a both restricted and unrestricted;
   - check the H2b medians with intervals;
   - replace H3a's bar with H3d;
   - drop H3b and "partially supported";
   - correct the status table and the pilot report before the student reads them.

## Alternative to decision 1: keep four coordinates

This keeps four coordinates and still resolves F2, F4 and F14.

- Keep N as the fourth coordinate in the profile, in A5 and in H3c.
- Replace H1f's pass/fail redundancy test with a pre-registered *estimation* question. Report the oracle-level ΔR² for adding N, with its interval, and state the expected direction from L11(b): pointwise information, average reducibility.
  - If the interval is near 0, the study shows that N rolls into three.
  - Otherwise it shows that N is distinct.
- Report the deployable test as secondary. State honestly that N̂'s estimand differs from N (F14).
- Rename library size to N_lib.
