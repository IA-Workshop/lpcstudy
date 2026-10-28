# Phase I follow-on study: pre-registration (DRAFT)

**DRAFT · not adopted · nothing sealed.** WU-0041 (ROADMAP.md §9, P1 draft; final at P4). Planner, claude-opus-5-5, 2026-10-25. The adopted version is copied to `docs/study/` at P4 and frozen at WU-0042.

- **Authority.** LPC.PC.1 scoped exception; ledger seq 44 (phase I ruling), seq 45 (code-review waiver), seq 42 (minimal formality); DEC-0038 (per-system words only).
- **Governing design.** v3 (`docs/study/proposal_and_methods_v3.md`) applies unchanged except where §1 names a ruling that replaces it. The procedure follows `docs/study/procedure_conf1.md` unless stated otherwise.
- **Marker.** `PENDING (unit)` means the item is filled in later from development evidence or a ruling. No PENDING item may remain at the seal.

## 0. PENDING items (all closed before any seal)

| # | Item | Source |
|---|---|---|
| P-1 | Admitted set of systems | WU-0040 (gate table), after WU-0037 and WU-0039 |
| P-2 | V7 fixes per system (at most two, estimator-side, new systems only) | WU-0037, WU-0039 |
| P-3 | Refined ablation predictions (§6.3, §7.3) | WU-0036, WU-0040 |
| P-4 | Parameter-table check S1 to S6 | WU-0044 |
| P-5 | Frozen commit, tag `freeze-x`, configuration, lock | WU-0042 |
| P-6 | Owner rulings listed in §12.2 | owner |
| P-7 | Tolerances and levels flagged in §12.1 | applied-mathematician |

## 1. Scope, and departures from v3 with their authority

| Topic | v3 | This study | Authority |
|---|---|---|---|
| Systems | Lorenz-63, Rössler, Chua | admitted subset of S1 to S6 (§2); the frozen three are not run on CONF-2 to CONF-4 (proposed, §12.2 O-3) | LPC.PC.1 exception; ROADMAP §9 ("CONF-1 is not re-run") |
| State dimension m | 3 (§4) | 3 or 4 (§2). Wherever v3 uses m (√m in H1b, χ² dof D − m in the LM diagnostic), the system's m is used, as implemented | LPC.PC.1 exception |
| Overall verdict | §7, across three systems | none; per-system words only | DEC-0038; LPC.PC.1 exception |
| Seeds | one sealed seed | CONF-2, CONF-3, CONF-4; combination rule §4 | seq 44 item 6 |
| Device | CPU official, GPU cross-check (§9 items 2 to 4) | GPU official, GPU regeneration, CPU on trigger only (§5) | seq 44 item 4 |
| Estimates | Q-N | Q-N plus the two ablations (§6, §7), estimate rows with no verdict | LPC.PC.1 exception; seq 44 item 5 |
| E6 robustness | Lorenz-63 and Rössler only | not run (no admitted system is in `robustness_systems`) | v3 §6 E6, unchanged |

Unchanged and not repeated here: hypotheses, statistics, bands, levels, verdict rule, the 50-state rule, the K rule, the Q-N reading table, the pre-registered readings of failures, sample sizes, intervals (block 5, 2000 resamples, failed resamples at the unfavourable tail), clip at 10 σ_x with the 20 σ_x sensitivity flag, the horizon rules and the validation gate.

The exploratory reading rules of the specification notes (specs §5 items 2 to 9, specs-2 §5 items 10 to 12) are **not** pre-registered readings. Only v3 §7's readings apply. Adopting them is an owner decision (§12.2 O-6).

## 2. Candidate systems and admission

| ID | Code name | m | Observed | Definition (checked by WU-0044) | DEV-3 gate (development) | λ_max referent |
|---|---|---|---|---|---|---|
| S1 | `rossler_hyper` | 4 | x | hyperchaotic Rössler (Rössler 1979) | PASS | published 0.1121 |
| S2 | `lorenz63_r166` | 3 | x | Lorenz-63 at r = 166.1 | FAIL V7 (all ρ) | none |
| S3 | `rossler_z` | 3 | z (state permuted) | Rössler at v3's parameters | FAIL V7 (ρ = 2%, slope) | none stored (§9) |
| S4 | `hindmarsh_rose` | 3 | x | Dysts `HindmarshRose` | FAIL V7 (all ρ, slope) | none |
| S5 | `hyper_jha` | 4 | x | Dysts `HyperJha` (web-page provenance) | FAIL V7 (ρ = 5% only) | none |
| S6 | `lorenz96_4` | 4 | x | Lorenz-96, N = 4, F = 20 | FAIL V7 (ρ = 5% only) | none |

**Admission rule** (seq 44 item 2, as ruled):

1. A system is admitted only if V1, V2, V4, V5, V6 and V7 pass at their v3 §6 criteria on each of DEV-1, DEV-3 and DEV-4, at the code that is frozen. V3 is reported and has no bar.
2. A system that fails V7 may receive at most two estimator-side fixes. They act on that system only and leave the frozen-system path bitwise unchanged (WU-0039 leafdiff criterion). After the budget, the system is reported as **not admitted, with its reason**.
3. No band, criterion or level changes for admission.
4. A system whose WU-0044 check leaves a mismatch unresolved is not admitted (proposed: seq 45 conditions the waiver on that check).

**Admitted set: PENDING (WU-0040).** The table of admitted and not-admitted systems, with the gate values per seed and the fixes applied, is inserted here at P4. A not-admitted system is reported in the study's results with its reason. It is not run on a CONF seed.

## 3. Hypothesis rows per system

**Rows.** For each admitted system and each CONF seed, every v3 §2 row is computed and judged exactly as in v3 §7. This covers H1a to H1d, Q-N, H2a to H2e and H3a to H3c, plus the reported-only items: the gain-bound screen, the horizon gain against the P1 bound, V3, the clip-sensitivity flag and the block-sensitive label.

- **Levels.** The primaries H2a, H2b and H3c use 1 − 0.05/3. All other rows use 95%.
- **Parts.** Intersection–union across a criterion's parts within a system: a criterion passes only if every part passes, and fails if any part fails.
- **Words.** The stored overall word is `per-system only` (DEC-0038 option (a)). No sentence, table or figure combines systems into a verdict, a count or a rate presented as a finding.

**Multiplicity across systems: not adjusted.** The reasons:

1. No claim combines systems. Each per-system word is its own claim, with v3's error control at the per-system level.
2. Adjusting would change a level, which seq 44 item 2 and the scoped exception forbid.
3. The seed rule (§4) is an intersection over three independent realizations. For a fixed true value of a part, a false promoted pass (or fail) needs a false word on all three seeds. With one-sided per-seed error p ≤ α/2, the bound is p³:
   - primaries: p ≤ 0.0083, so p³ ≈ 5.8·10⁻⁷ per word, or about 1·10⁻⁵ over 6 systems × 3 primaries;
   - secondaries: p ≤ 0.025, so p³ ≈ 1.6·10⁻⁵ per word, or about 8·10⁻⁴ over 54 words.

   These are nominal values. Under the undercoverage of v3 §8 (95% intervals at 0.923 to 0.931), p is about 0.035 to 0.038 for the secondaries.
4. **Caveat.** The bound covers sampling error only. A bias common to all seeds (the estimator, the LM iteration error, the clip, the code) gives the same wrong word three times, and the seed rule does not protect against it.
5. **Flag (applied-mathematician).** Confirm the bound, its independence premise, and the power cost (§4).

## 4. Seeds and the combination rule

- **Sealing.** CONF-2, CONF-3 and CONF-4 are drawn and committed by the owner (`tools/seal_confirmatory_seed.py`, a ledger `commitment` per id, WU-0038) after the freeze and before any confirmatory run. Agents never see them.
- **Per-seed words.** Each (system, seed) pair gets its own words, by v3 §7. Seeds are never pooled. No mean, spread or range is taken across seeds as a statistic, and no interval is combined.
- **Combination**, per system and per row:

| Per-seed outcome on CONF-2, -3, -4 | Reported word |
|---|---|
| the same word on all three, gate PASS on all three | that word (promotable) |
| words differ | **seed-dependent**, with the three words listed |
| gate fails on any seed | that seed's words are PROVISIONAL (v3 E0). Proposed: the system's word is reported as **provisional (gate failed on CONF-n)** and is not promotable (§12.2 O-4) |
| no result on a seed (orbit refusal, non-finite stop) | that seed's words are **inconclusive (no result)**, with the reason, by v3 §7's cannot-compute rule. The combination rule then applies |

- **Estimate rows.** Q-N and the ablation readings follow the same rule. A reading given by all three seeds is reported as stable. Otherwise the reading is seed-dependent.
- **Power cost.** If one seed decides a part with probability π, all three seeds agree with probability about π³. For π = 0.8 that is 0.51. On the frozen systems, H3c and H2b(ii) changed word across DEV-1, DEV-3 and DEV-4 (ensemble summary §3.2). Many words should therefore be expected to read seed-dependent. A seed-dependent word is not evidence of no effect.

## 5. Device, regeneration, and the CPU trigger

- **Official device.** The RTX 4090 (`jax[cuda12]==0.11.2`), one GPU job at a time, through `tools/run_preset.sh` under the lock.
- **Run unit.** One invocation per (system, seed) (proposed). In a batched invocation, a refusal in system k ends the run, and the systems after it are never run (specs-2 §8(a)).
- **Regeneration.** A second GPU run of each (system, seed) on the same host, from the same commit and inputs, judged at tier T0: bitwise on every compared leaf (`tools/compare_runs.py`). If it is not bitwise, the difference is reported and trigger C-1 fires. No verdict depends on the regeneration.
- **Actor (§12.2 O-1).** v3 §9 item 4 requires another actor, while ROADMAP P5 has one owner command run both. Either another actor runs the regeneration, or the owner records a waiver as seq 31 did for CONF-1.
- **CPU triggers (proposed).** A CPU run (`LPC_THREADS=8`) of the affected (system, seed) happens only if:
  - **C-1:** the GPU regeneration is not bitwise;
  - **C-2:** V6 fails on the GPU official run;
  - **C-3:** V1 or V2 fails on the GPU official run;
  - **C-4:** an orbit refusal with a non-finite state occurs on the GPU.
- **What a CPU run does.** It informs only. It is compared by v3 §9 item 3's statistic on the primary parts (a part disagrees if z > 3.4) and reported. It never replaces, rescues or changes a GPU word or gate outcome.

## 6. Ablation (a): the A4 coefficients a, b, a′, b′

### 6.1 Rows

Rows are computed per admitted system and seed. There are eight: {a, b, a′, b′} × {zero, refit}.

- **zero:** the named coefficient is set to 0, and the other three keep their construction-fit values.
- **refit:** the term is removed, and the other three coefficients are refitted on the construction states by v3 §5's robust log-scale least squares.
- **Statistic:** r = MSE(A4 variant) / MSE(A4) at H_ref, on the test states, with errors defined as for H2c.
- **Interval:** paired moving-block bootstrap (block 5, 2000 resamples), level 1 − 0.05/3 (as ruled; §12.1 M-3).
- **Undefined weights.** A state with ε̂² + δ̂² = 0 has no weight. Such states are counted and reported, never dropped silently. Their handling is PENDING (WU-0039).
- **Verdict:** none.

### 6.2 Reading table

Modeled on Q-N. The margin 1.05 is H3c's band (§12.1 M-2). Rows are checked top to bottom, and the first match applies.

| Interval for r | Reading |
|---|---|
| upper bound < 1 | removing the term lowers the MSE |
| lower bound ≤ 1, upper bound < 1.05 | the term is negligible at this precision |
| lower bound > 1, upper bound < 1.05 | the term is needed, but its contribution is small |
| lower bound > 1, upper bound ≥ 1.05 | the term carries a substantial part of A4's accuracy |
| otherwise | undetermined |

### 6.3 Predictions (written now; refinement PENDING (WU-0036, WU-0040))

The pilot form A4 ≈ 1/(1 + 0.26(R/ρ)²) (v3 §8) implies b′ ≈ 0 and that ν̂ cancels.

| Coefficient | Prediction | Why |
|---|---|---|
| a | large loss: "substantial", the largest r | zeroing a removes R, so w becomes the constant a′/(a′ + b) |
| b | small: "negligible" or "small" | b(ρν̂)² is small next to a(Rν̂)² |
| a′ | moderate: "substantial", r below a's | zeroing a′ gives δ̂² = b′ρ² ≈ 0, so w ≈ 0 and A4 behaves like A1 |
| b′ | about zero: "negligible" | b′ ≈ 0 |

The predicted ordering of point estimates is r(a) > r(a′) > r(b) ≥ r(b′) ≈ 1, in both modes. The refit mode minimizes the proxy fit, not the MSE, so the refit loss is not guaranteed to be smaller than the zero-mode loss.

## 7. Ablation (b): the profile conditions R, O, I, N

### 7.1 Coordinates and procedure

- **Coordinates** (v3 §5): R = ln ε/ρ, O = ln δ/ρ, I = Λ̃, N = ln(N + 0.01).
- **Profiles.** The oracle profile is primary and the deployable profile is secondary, as in Q-N.
- **Procedure.** The Q-N procedure throughout (`analysis.qn_profile_block`):
  - the same gradient-boosted regressors and hyperparameters;
  - training on construction plus calibration, scoring on test;
  - models held fixed in the resamples;
  - resamples shared across targets and rows;
  - level 95%.
- **Targets**, as stored by Q-N:
  - the weight: logit w\* on 0 < w\* < 1, and 1{w\* = 0};
  - the horizon: the log characteristic horizon of the oracle hybrid at θ = 0.2, censored at 8 LT (`state_horizon_target`).

### 7.2 Rows

| Row | Statistic | Read by |
|---|---|---|
| (b1) leave-one-out | ΔR²_X = R²(F) − R²(F without X), for X ∈ {R, O, I, N}, per target and profile. The X = N row is Q-N and reproduces its leaves bitwise (WU-0039) | the v3 §7 Q-N table. A part with fewer than 50 states is undetermined. Reading the horizon target is new (Q-N reported it without a reading, D-04) |
| (b2) Shapley | φ_X = Σ over S ⊆ F without X of \|S\|!(3 − \|S\|)!/4! · [R²(S ∪ {X}) − R²(S)], over the 16 subsets; Σ φ_X = R²(F) − R²(∅), where ∅ is the training-mean predictor | the Q-N table applied to φ_X |
| (b3) A5 without X | A5 refitted on the three remaining deployable coordinates (K by the v3 rule, weights on calibration); r = MSE(A5 without X)/MSE(A5) at H_ref; paired block bootstrap, level 1 − 0.05/3 (§12.1 M-3) | the table in §6.2 |

### 7.3 Predictions (oracle profile; refinement PENDING (WU-0036, WU-0040); deployable predictions PENDING (WU-0040))

| X | Weight targets (b1, b2) | Horizon target (b1, b2) | A5 without X (b3) |
|---|---|---|---|
| R | large ("substantial") | no prediction | large, PENDING (WU-0040) |
| O | large ("substantial") | no prediction | PENDING (WU-0040) |
| I | near zero ("reduces") | large ("substantial") | negligible |
| N | as Q-N reads it on that system and seed | no prediction | PENDING (WU-0040) |

Shapley shares and ΔR² describe predictive information under fitted models with training held fixed. They are not causal attributions.

## 8. Start-state refusal (S1, and every admitted system)

- **History.** At `max_dt` 0.01 and bound 300, S-D1 refused 10 of 400 starts, 7 of them non-finite (WU-0021). The cause was RK4 instability in the attractor's tail (review R1), not an escape. The main session's hazard ruling was withdrawn (DEC-0038 item 4).
- **Current specification.** At `max_dt` 0.005 and bound 460, S-D1 passes: 0 of 400 refused, max |x| 303.30 (WU-0021).
  - 95% upper bound on the per-orbit probability of exceeding 304: about 0.65% (specs-2 §11).
  - Each run has a main and a separate trajectory, so the bound is about 1.3% per (S1, seed). Regeneration repeats the same orbits and adds no risk.
- **Rule** (Ruling 2, carried by specs-2 §11):
  - A refusal is reported as a result. The bound and S-D1 are not changed.
  - The mechanism is read from the recorded maximum. A finite state at the bound is a new excursion, a finding. A non-finite state is a defect: it fires trigger C-4 and is referred.
- **Proposed for the confirmatory study:**
  - no sealed seed is re-drawn after a refusal, because a re-draw would condition the sample on the outcome (§12.2 O-2);
  - the affected (system, seed) reads "inconclusive (no result)" by §4;
  - the other systems are unaffected (§5, run unit).

## 9. Validation status of the instruments

- **λ_max**, which sets the time unit 1 LT = 30 steps:
  - **S1** is validated against a published value (0.1121, Ramasubramanian & Sriram 1999), within 3%. The DEV-3 run stored +0.56%, and the WU-0021 cached value is +0.09% (§13 item 9).
  - **S2 to S6** are stored "not validated". Their time unit rests on the code's Benettin value, with an independent Benettin check (A6, within 3 block SEs). That check is verification, not validation.
  - S2's λ SE (about 1 to 2%) is reported beside every LT statement.
- **Specifications and verdict code.** S1 to S6 equations and parameters are checked against Dysts and the literature, with quotes (WU-0044). The extension verdict-reporting code is covered by agent review plus that check, with owner review waived (seq 45). Its risk statement is carried into the report verbatim.
- **Estimator.** V7 is the efficiency check. On an admitted system with fixes, the PLP arm rests on an estimator modified for that system only.

## 10. Known limitations, stated before the run

1. **H2a(i) describes only small-error states.** Exclusions on DEV-3: S1 420, S3 375, S2 605, S6 687, S4 868 and S5 899 of 1000 (frozen systems 76 to 338). On S4 and S5, H2a(i) covers about 10 to 13% of the test states. Refreshed counts are PENDING (WU-0040).
2. **H2c's comparator differs by system and may differ by seed.** The better single forecaster on calibration was A0 on S2, S3 and S4 and A1 elsewhere (DEV-3). The comparator is reported beside every H2c word.
3. **Clip sensitivity on S1.** On DEV-3, 0.34% of core-cell error entries were clipped as non-finite. H1b, H2c and H2e were flagged clip-sensitive. The flag is reported and never changes a word.
4. **Determinism, not independent reproduction.** The regeneration runs on the same host and device, and possibly by the same actor (§12.2 O-1).
5. **The extension verdict code is not owner-reviewed** (seq 45, risk accepted as recorded).
6. **λ_max is externally validated for S1 only** (§9).
7. **One realization per (system, seed).** Three seeds give three realizations, which are neither pooled nor used to estimate between-seed variance.
8. **The admission evidence and any V7 fixes come from development seeds whose results were seen** (DEV-1, DEV-3, DEV-4). The CONF seeds are fresh.
9. **v3 §8 limitations carried unchanged:** interval undercoverage; LM iterative error not estimated for S1 to S6; the gain-bound screen reported only; slow dependence.
   - The block-sensitive label needs a per-state dump, and whether the confirmatory run writes one is PENDING (WU-0039, WU-0042).
10. **S5's provenance is weak** (Dysts web page; "Dysts `HyperJha`" in every table).
11. **The seed rule's power is low** (§4). Expect seed-dependent words.

## 11. What the result may and may not be called

**May be said**, with §10 attached:

- For each admitted system, the pre-registered v3 analysis of sealed seeds CONF-2 to CONF-4 returned the listed per-system words, and each word is either promoted (all three seeds agree) or "seed-dependent".
- The not-admitted systems are listed with their reasons.
- The regeneration reproduced every compared leaf bitwise on the same host (determinism).
- The ablations are estimates with readings, compared against the predictions written in §6.3 and §7.3.

**May not be said:**

- an overall verdict, or a count of systems presented as a finding ("H2b holds on k of 6 systems");
- any pooling across seeds, or a reading of one seed's word as the result;
- independent reproduction, or owner-reviewed extension code;
- that a word holds or fails because of a system property (dimension, hyperchaos, spiking);
- that "inconclusive" or "seed-dependent" means no effect;
- that an ablation share is causal;
- that the CPU or the regeneration confirms a verdict;
- any comparison that sets these numbers beside CONF-1's, or any change to the CONF-1 result.

Every development number (DEV seeds, WU-0026, WU-0036, WU-0040) stays labelled development.

## 12. Open points

### 12.1 For the applied-mathematician (before the seal)

- **M-1. Multiplicity.** Confirm across systems (§3: not adjusted, the p³ bound and its independence premise) and across seeds (the intersection rule's error and power).
- **M-2.** The 1.05 margin of the MSE-ratio reading table (§6.2).
- **M-3. Levels.** Ablation (a) and row (b3) run at 1 − 0.05/3, while (b1) and (b2) must run at 95% so that the drop-N row reproduces Q-N bitwise. Confirm, or set one level for all estimate rows.
- **M-4.** Where failed resamples go for estimate rows, which have no unfavourable tail.
- **M-5.** R² on a horizon target censored at 8 LT (S2 had 125 censored states on DEV-3).
- **M-6.** R²(∅) as the out-of-sample training-mean predictor, which is slightly negative.
- **M-7.** The fall-back tolerances if the GPU regeneration is not bitwise.

### 12.2 For the owner

- **O-1.** Another actor for the regeneration, or a waiver (v3 §9 item 4).
- **O-2.** No re-draw of a sealed seed after a refusal.
- **O-3.** The frozen three are not run on CONF-2 to CONF-4. Their ablation numbers stay development, unless the ablations should also run confirmatorily on them.
- **O-4.** A gate failure on one CONF seed makes the system's word "provisional", not promotable.
- **O-5.** The CPU trigger list C-1 to C-4, and one invocation per (system, seed).
- **O-6.** Whether the specification notes' reading rules become pre-registered readings (proposed: no).

## 13. Conflicts found with v3 or the rulings

1. **S1's 10 of 400 refusals are superseded.** They were measured at the old step. At the current specification S-D1 passes (0 of 400). Ruling 2's handling rule survives (§8), and its hazard premise was withdrawn (DEC-0038 item 4).
2. **Official device.** v3 §9 items 2 and 3 make the CPU official. Seq 44 makes the GPU official for this study. This is a recorded departure (§1).
3. **Regeneration actor.** v3 §9 item 4 (another actor) conflicts with ROADMAP P5 (one owner command). Needs O-1.
4. **State dimension.** v3 §4 assumes three-dimensional systems. S1, S5 and S6 have m = 4. The scoped exception covers them, and m is used as implemented.
5. **Overall verdict.** v3 §7's overall verdict and its error analysis of "not supported" do not apply (DEC-0038).
6. **Ablation levels.** The levels are inconsistent within the ablations (M-3).
7. **Horizon reading.** Q-N's horizon target had no reading in CONF-1 (D-04). §7 reads it.
8. **S3's λ_max.** S3 is Rössler at v3's parameters, yet it is stored "not validated". The Rössler referent may apply, as a check for the researcher.
9. **S1's λ_max values.** The stored DEV-3 value (0.112729, +0.56%) differs from the WU-0021 cached value (0.112205, +0.09%) by about one SE. Which value a CONF run uses should be confirmed (WU-0042).
