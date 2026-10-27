# Phase J report: the LPC contribution study on held-out seeds (WU-0052)

**DEVELOPMENT (DEV-5 to DEV-9): phase J replication on held-out development seeds, not a hypothesis test.** Main session (claude-opus-5-5), 2026-10-26. For the owner and the student.

- **Runs.** `phasej` preset (full, n_test 4000), GPU, from tag `phasej-freeze` (0929a9a). Manifest line of 2026-10-26.
- **Analysis.** Both analysis tools ran once per seed, then `tools/lpc_replicate.py` ran once in rule mode (M-6 with S1 to S4: at least 4 of 5 seeds and no contradiction). All at `phasej-freeze`, clean tree, on CPU.
- **Departure.** The C/E command in the freeze note passed a directory to `--abd`. The C/E tool stopped at argument loading on DEV-5 to DEV-8 before it computed anything. The corrected command then ran once per seed. No code changed. Details are in the freeze note.
- **Chua is provisional on DEV-7 and DEV-8.** Chua failed validation check V1 (delay-map Jacobian against finite differences) on those two seeds. With 5 seeds, any "4 of 5" Chua replication includes at least one of them. So every Chua replication below is provisional. Of the 392 replicated Chua rows, 327 also read the same on all three clean seeds (DEV-5, DEV-6, DEV-9). Every Chua reading this report names is among those 327.
- **No pooling.** Each seed is read on its own. The replication rule counts readings and computes no new statistic across seeds.
- **Kept apart from CONF-1.** Nothing here is placed beside the sealed CONF-1 result.

Sources:
- `2026-10-26-phase-j-replication/replication.md`: every row with its five readings.
- `lpcstudy-wt/run/phj-freeze/runs/dev/replication-phasej-freeze/replication.json`, and per seed `runs/dev/phj-DEV-n/contrib-freeze/{contrib,ce}.json`.
- The sha256 hashes are in the manifest.

## 1. Summary

| | Lorenz-63 | Rössler | Chua (provisional) |
|---|---|---|---|
| Horizon: which conditions matter | I, then O | I, then O | I, then O |
| Horizon: O × I interaction | replicated, substantial | replicated | replicated |
| Weight: which conditions matter | none readable below 2 LT. Drop-I on the logit weight is substantial (pipeline ablation, display only) | R (substantial at 1–2 LT, oracle). R × O in the decision | none readable below 2 LT. Drop-I on the logit weight is substantial (pipeline ablation, display only) |
| Deployable weight against a constant | better at 1 LT (substantial) | no gain at 1 LT | not readable at 1 LT |
| Raw delay vector added to the profile | improves the horizon and, at 1 LT, the weight | improves the horizon | improves the horizon |
| C2, both bottlenecks lose most | consistent (oracle, replicated) | contradicted | deployable: not consistent (replicated) |
| C3, full system false trust | 9.0–11.1% | 13.2–14.0% (above the 10% target) | 9.2–10.6% |

Family counts (C1 is display only and not counted):

| family | rows | replicated | contradicted | not replicated |
|---|---|---|---|---|
| A drop-one | 144 | 72 | 1 | 71 |
| A vs separation | 480 | 254 | 4 | 222 |
| B loss ratio | 624 | 388 | 8 | 228 |
| B pair | 624 | 101 | 7 | 516 |
| C2 (four families) | 186 | 97 | 14 | 75 |
| C3 ratio | 66 | 43 | 1 | 22 |
| D vs below | 372 | 192 | 10 | 170 |
| D vs full | 372 | 176 | 5 | 191 |
| E-H2a, E-H2e, E-H3c | 24 | 4, plus 3 replicated as point readings | 2 | 15 |
| check (f2) | 393 | 94 | 4 | 295 |

Contradicted rows by system: Lorenz-63 15, Rössler 33, Chua 8.

**Expected false replications.** A false replication is a null row that still reads the same on 4 of 5 seeds. These counts are upper bounds: they assume every row is null. They use r from the r-measurement note, with M-6's formula at z = 1.96.

| families | rows | replicated | expected false replications (r median / RMS / Q3) |
|---|---|---|---|
| A, B, D | 2616 | 1183 | 0.7 / 1.7 / 3.9 |
| C2 | 186 | 97 | 0.2 / 0.7 / 1.5 |

At the rows' own family levels, the A and B rates are about ten times smaller. r was not measured for C3, E or check (f2), so no count is given for them.

## 2. Horizon (A, B, D on the crossing time)

This is the clearest result and it repeats on every seed.

- **Drop-one.** The pinball-loss ratio is the loss without the condition over the loss with all four conditions. Every seed reads substantial for I and for O, on all three systems and both profiles. Ranges over the five seeds:

  | | drop I | drop O | drop R |
  |---|---|---|---|
  | Lorenz-63 | 1.20–1.29 | 1.07–1.13 | 1.00–1.04 |
  | Rössler | 1.21–1.27 | 1.10–1.14 | 1.00–1.04 |
  | Chua | 1.22–1.28 | 1.06–1.09 | 1.00–1.03 |

  N reads negligible everywhere. R reads negligible on Lorenz-63 and "small" on oracle Rössler. On Chua no single reading for R reaches 4 of 5 seeds, but every seed puts its ratio at or below 1.05.
- **O × I interaction.** Replicated on every system and both profiles. Its loss ratio is substantial on Lorenz-63 (both profiles) and on deployable Rössler, and "needed, size not determined" elsewhere. Two other horizon pairs replicate: R × I (deployable, Lorenz-63 and Rössler) and R × O and R × N (oracle Rössler). Their loss ratios are small or not replicated.
- **D ladder.** Every single condition, the pair {R, O}, the constant and the Lyapunov rank read substantial against the full profile (at least 4 of 5 seeds, every system and profile). The full profile's Harrell's C is 0.68–0.73, against 0.60–0.67 for the Lyapunov rank. **Adding the raw delay vector lowers the pinball loss on every system, profile and seed.** The four conditions do not carry all of the horizon information in the state.
- **Deployable against oracle.** The C index and drop-one ratios agree to within about 0.03. For the horizon, estimating the conditions is not the limit.

## 3. Allocation (A, B, D on the weight)

- **Lorenz-63 and Chua below 2 LT.** Allocation is still undetermined at 0.27, 0.5 and 1 LT on most seeds, even with n_test 4000: the n_eff guard is not met. The larger test split did not fix this.
- **Rössler.**
  - R is the condition that matters: drop-R reads substantial at 1 LT on 5 of 5 seeds and at 2 LT on 4 of 5 (oracle).
  - O is small at 1 and 2 LT.
  - The R × O interaction in the decision loss is substantial at 0.5 and 1 LT (oracle).
  - On the deployable profile, every drop-one at 1 LT is negligible, and so is the gap to a constant weight. **On Rössler the oracle conditions help the weight, but the estimated ones add nothing over a constant at 1 LT.** This repeats the exploration result: the limit is estimation.
- **Lorenz-63, deployable, 1 LT.**
  - The constant weight and the separation formula read substantial against the full profile on 4 of 5 seeds; the fifth is undetermined.
  - The raw delay vector, alone or added to the profile, gives a lower MSE than the profile on 5 of 5.
  - So the deployable profile beats a constant, and the raw state beats the profile.
- **4 LT.**
  - Every drop-one reads negligible or small.
  - The separation formula reads "needed" or substantial against the full profile on every system and profile.
  - The raw delay vector added to the profile is negligible against the profile, or lowers its MSE on some seeds.
  - The fitted constant (subset none) gives a lower MSE than the separation formula on every system and profile, 4 or 5 of 5 seeds.
  - At shorter horizons the comparison differs by system. On oracle Rössler at 1 and 2 LT the fitted constant is substantially worse than the formula, while on the deployable rows of Lorenz-63 and Rössler it is better.
- **The instability test (H2a, display only).** This row is drop-I on the logit weight given R, O and N, at 1 LT with the Q-N learner. It comes from each run's own ablation (`results.json`, `ablation/profile_conditions`), which is not a family of the replication rule. Per-seed readings:

  | | oracle | deployable |
  |---|---|---|
  | Lorenz-63 | substantial on 3, distinct but small on 2 | substantial on 5 |
  | Chua | substantial on 5 | substantial on 5 |
  | Rössler | reduces on 2, distinct but small on 3 | reduces on 4, distinct but small on 1 |

  The ΔR² is 0.03–0.09. This matches the exploration direction: instability adds information about the weight on Lorenz-63 and Chua, not on Rössler. The effect is small in size, and the MSE-ratio rows above cannot read it below 2 LT.

## 4. Interactions in the weight (B)

- **The student's priorities.**
  - **R × I:** the gain on the logit weight replicates in one cell each on Lorenz-63 and Rössler. In both cells the loss ratio is negligible or does not replicate. In this study R × I is not a material interaction in the weight.
  - **O × I:** a small, replicated gain on the logit weight on Chua (oracle and deployable, at 1 and 2 LT) and on oracle Lorenz-63 at 4 LT. The loss ratio is below 1.05 in every cell.
- **R × O** is the largest weight interaction: substantial in Rössler's decision loss, and small on the logit weight on Rössler (7 of 10 cells) and Chua.
- **The w* = 0 classifier** shows many small replicated pair gains, mainly R × O and R × N, all with loss ratios ≤ 1.05.

Every replicated weight interaction is small except Rössler's R × O.

## 5. One profile for both decisions (C)

- **C2 retained share.**
  - Forward with one weight: loses most on every system, profile and horizon (4 or 5 of 5), except Rössler at 4 LT, where it is contradicted.
  - Reverse to the weight (the L_w rows): loses most in 24 of 30 cells. The other six do not replicate: four are at 4 LT, and two are deployable Chua at 1 and 2 LT.
  - Reverse to the MSE: mostly not determined.
- **C2, "both lose most."**
  - Lorenz-63 oracle: consistent (5 of 5).
  - Chua deployable: not consistent (5 of 5). The forward share keeps most (4 of 5).
  - Rössler (both profiles) and Chua oracle: contradicted, with seeds on both sides.
  - The prediction holds on Lorenz-63 only, as in exploration.
- **C3 joint system.**
  - The combined deployable system, with weights from F̂ and the horizon from the predicted 10% quantile, gives a lower MSE than the constant weight on Lorenz-63 at 0.5 to 4 LT and on Chua at 2 and 4 LT. On Rössler it is negligible against the constant at 0.27 and 1 LT, lower at 4 LT, and contradicted at 2 LT.
  - Its trusted horizon is the longest of the four policies on every system and seed: Lorenz-63 1.11–1.13 LT, Rössler 2.24–2.27, Chua 1.39–1.50.
  - False trust is above the constant policy on every system. The constant policy's rates are 7.0–8.1% on Lorenz-63, 9.0–10.0% on Rössler and 7.0–8.0% on Chua.
  - **On Rössler, false trust is 13.2–14.0% on every seed, and every interval lies above the 10% target.** A constant weight with the horizon model (12.7–13.6%) does about the same. The cause is the horizon model, not the weight.

## 6. Mechanisms (E)

- **E-H3c:** not consistent on all five seeds. These are point readings, so they never contradict. As in exploration, Lorenz-63's heavy states have low I, not high I.
- **E-H2a:** Rössler not consistent (replicated). Lorenz-63 and Chua not determined.
- **E-H2e:** the final reading does not replicate on any system. Three parts replicate "not consistent": the "all states" part on Lorenz-63 and on Rössler at ρ = 0.01, and Rössler's "both defined" part at ρ = 0.02. Two rows are contradicted: Chua's "all states" part and Lorenz-63's "both defined" part, at ρ = 0.02.

## 7. Predictions written before the data

| Prediction (plan §4, math spec "Refined predictions") | Held-out seeds |
|---|---|
| Horizon: I largest, then O; R's direct effect small | **replicated** on every system and profile |
| Horizon pairs: R × O the only first-order pair; I pairs only through departures | **departs.** O × I replicates everywhere and R × O replicates only on oracle Rössler |
| Allocation: R and O carry most value at short horizons | **Rössler: R yes, O small.** Lorenz-63 and Chua: not readable (n_eff) |
| Allocation: I's value grows with the horizon | **not seen.** Drop-I is negligible or small at 4 LT everywhere. On Lorenz-63 and Chua it is substantial at 1 LT on the logit target (display only, R² scale) |
| Separation formula worse than A2 at 4 LT | **replicated.** The fitted constant beats the formula at 4 LT on every system and profile, and the full profile beats it too |
| B: R × I and O × I U-shaped in the horizon | **not determinable.** R × I is absent in the weight; O × I is small |
| C2: both bottlenecks lose most | **Lorenz-63 only** |
| D: deployable estimation gap concentrated in O and I | **departs.** The horizon has no estimation gap. On Rössler the gap covers the whole profile |
| E-H3c: Lorenz-63 tail in high-I states | **not consistent**: the tail is in low-I states |
| E-H2e: correlation rises most where R falls most | not supported where readable |

## 8. What this means for the student's questions

1. **Do the four conditions explain predictability?** For the horizon, yes, in a stable way. I, then O, decides how long the hybrid stays trustworthy, and O × I matters. This holds on every system and seed. The raw state still adds a little beyond the profile.
2. **Do they decide the blend?** Only partly.
   - On Rössler, R decides the blend if R is known exactly. The estimated profile loses that gain.
   - On Lorenz-63, the estimated profile beats a constant at 1 LT, but the raw state does better still.
   - On Chua the short-horizon blend cannot be read, and instability adds information about the weight only on the R² scale.
3. **One profile for both decisions?** The two decisions share part of their information. Lorenz-63 matches the "both lose most" prediction; the other systems do not replicate it. The combined deployable system trusts longer than the simple policies, but over-trusts on Rössler.
4. **Promotion.** These are development readings under a rule fixed in advance. Promoting any of them needs the owner's confirmatory round, which is not part of this unit.

## 9. Open items for the owner

- Whether to run a confirmatory round, and on which claims. The horizon claims (I, O, O × I, and X+F lowering the loss) are the strongest candidates.
- Chua V1 on DEV-7 and DEV-8: an optional diagnosis, exploratory, that changes no reading.
- The `allocation.pooled_floor_count` docstring finding, still open.
