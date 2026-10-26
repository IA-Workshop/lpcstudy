# Phase J exploration report (WU-0050)

**DEVELOPMENT (DEV-1, DEV-3, DEV-4): exploratory, not a hypothesis test.** Main session (claude-opus-5-5), 2026-10-26. For the owner and the student.

- **Runs.** Full preset, GPU, commit f701a47. The validation gate passed on all three systems and seeds (manifest, 2026-10-26).
- **Analysis.** A, B, D at ea0bd77; C, E at 5889351.
- **Status.** These seeds were seen while the analysis was built, so they show directions, not results. The results come from the held-out seeds DEV-5 to DEV-9 under the frozen analysis and the M-6 replication rule.
- **No pooling.** Readings are set side by side, with no pooling and no new statistic across seeds.
- **Kept apart from CONF-1.** Nothing here is placed beside the sealed CONF-1 result.

Sources:
- tables: `2026-10-26-phase-j-exploration/` (`crossseed-DEV-1-3-4.md`, `condensed2-DEV-n.md`, `ce/`);
- full outputs: `lpcstudy-wt/run/phj-f701a47/runs/dev/phj-DEV-n/contrib-*/`;
- the drop-I rows on the weight targets: each run's `results.json`, `systems/<s>/ablation/profile_conditions/<profile>/<target>/leave_one_out/I`.

## 1. What the three seeds show

### Horizon: the clearest and most repeatable signal

On every system, profile and seed:
- dropping I costs most: the pinball-loss ratio is 1.19 to 1.29, read "substantial";
- O comes second, read "substantial" or "needed";
- R and N are negligible;
- the O × I interaction is detected (18 of 18 cells).

Other observations:
- The deployable profile predicts the horizon about as well as the oracle profile (Harrell's C 0.67 to 0.73 for both). For the horizon, estimating the conditions is not the limitation.
- The zero-parameter Lyapunov rank does worse (C 0.59 to 0.69).
- The raw delay vector together with the profile does better (C 0.71 to 0.78).

### Allocation: informative only where the loss is spread over enough states

- **Lorenz-63 and Chua at 0.27 and 1 LT.** Almost every row is "undetermined": a few states carry the loss, with n_eff 6 to 63 of 1000. This motivated the `phasej` preset (n_test 4000) for the replication runs (ledger seq 49).
- **Rössler.** R is the main condition, read "substantial" at 1 LT on all three seeds, and O is "needed". The full oracle profile beats a constant weight by about 15% at 1 LT on all seeds. The deployable profile loses most of that gain. For Rössler allocation, the limitation is estimation, not the conditions.
- **4 LT, all systems.**
  - Every drop-one row is negligible or small.
  - The no-fit separation formula is "needed" or "substantial" against the full profile, on every system and both profiles.
  - So at long horizons the weight is not set by the initial errors alone, but no single condition stands out by its absence.

### The direct test of the student's H2a reading

This is drop-I on the logit-weight target given R, O and N (WU-0039b rows, Q-N learner, 1 LT, oracle profile):

| System | DEV-1 | DEV-3 | DEV-4 |
|---|---|---|---|
| Lorenz-63 | undetermined | substantial | undetermined |
| Chua | substantial | substantial | undetermined |
| Rössler | reduces | reduces | reduces |

Instability adds information about the weight beyond the seeds on Lorenz-63 and Chua, and does not on Rössler. That is a direction for the replication runs to confirm or not.

### Interactions in the weight (B)

- No pair repeats across seeds.
- O × I is detected on single seeds, for example Lorenz-63 at 4 LT on DEV-1 and DEV-3, and Chua on one seed each at 0.27 and 1 LT.
- R × I is detected in four cells, each on a single seed (three on Lorenz-63, one on Rössler). Two of those intervals reach 0.
- So far there is no repeatable interaction in the weight. That fits the math spec: uneven error growth is a main effect of I, not an interaction.

### One profile for both decisions (C)

**C2, forward: horizon predicted from the allocation outputs only.**
- Lorenz-63 loses most of the skill on every seed (0.10 to 0.21 retained, both profiles).
- Rössler and Chua retain about half (0.37 to 0.69): mostly "not determined", with some "keeps most" on Rössler.

**C2, reverse: weight predicted from the horizon outputs only.** It loses most wherever it can be read: the L_w rows at 0.27 and 1 LT on all three systems.

So the two decisions share part of their information, not all of it. The math spec predicted that both directions lose most. Lorenz-63 matches that prediction. On Rössler and Chua the forward direction keeps more, which the spec reads as I entering the weight.

**C3, the full deployable system.** Weights come from F̂ and the trust horizon is the predicted 10% quantile.

| | Lorenz-63 | Rössler | Chua |
|---|---|---|---|
| Trusted horizon (LT) | 1.0 to 1.15 | about 2.25 | about 1.45 |
| False trust | 9.0 to 10.6% | 13 to 15% | 9 to 11% |

- The trusted horizon is the longest of the four policies on every system.
- False trust is higher than for a constant weight with a constant horizon (6 to 8% on Lorenz-63).
- On Rössler, false trust is above the 10% target. The horizon models also over-trust slightly on their own (10% quantile coverage 0.11 to 0.14).

### Mechanisms (E)

- **E-H3c.**
  - The pattern repeats: Lorenz-63 has the widest H3c interval and Rössler the narrowest.
  - On Lorenz-63 the top 1% of states carry 59 to 68% of the A5–A4 difference. Those states are low-instability states (median I percentile about 0.2), not high-instability ones.
  - The explanation stated in advance is therefore "not consistent" on all three seeds. Lorenz-63's uncertainty comes from a few heavy states, but not the ones expected.
- **E-H2e.** The candidate mechanism (correlation rises most where recurrence improves most) is not supported where it can be read. On Rössler the association has the opposite sign. Elsewhere it is mostly not determined, because many states have zero error correlation at the smallest library.
- **E-H2a.** Mostly not determined. There is one "consistent" reading, on Lorenz-63 at DEV-4, at 4 LT only.

## 2. Predictions written before the data, against these seeds

| Prediction (plan §4, math spec "Refined predictions") | Exploration seeds |
|---|---|
| Horizon: I largest, then O; R's direct effect small | matches on every system, profile and seed |
| Horizon pairs: R × O the only first-order pair; the I pairs appear only through departures | O × I is detected everywhere, beyond the first-order form. R × O appears on some seeds |
| Allocation: R and O carry most value at short horizons | Rössler: yes, mainly R. Lorenz-63 and Chua: not determined (n_eff) |
| Allocation: I's value grows with the horizon | not seen at 4 LT, where every drop-one is negligible. Drop-I on the logit target at 1 LT is substantial on Lorenz-63 and Chua on some seeds |
| Separation formula worse than A2 at 4 LT | it is worse than the full profile at 4 LT on every system |
| B: R × I and O × I U-shaped in the horizon | no repeatable pair, so not determinable |
| C2: both bottlenecks lose most | Lorenz-63 yes. Rössler and Chua forward keep about half |
| D: deployable estimation gap concentrated in O and I | not yet read per condition. Rössler's deployable profile loses most of the oracle gain |
| E-H3c: Lorenz-63 tail in high-I states | not consistent: the tail sits in low-I states |
| E-H2e: correlation rises most where R falls most | not supported where readable |

## 3. Changes made during exploration, all before the freeze

All are recorded in plan §8 to §10 and the math spec addendum:
- realized per-draw scores for deployable rows;
- inner cross-validation for model complexity;
- readings on the MSE ratio;
- the n_eff guard, with its deployable definition (R2);
- the restated additive-null test (R1);
- the dependence-bias decomposition (R3);
- C2 on the deployable profile with L_w rows;
- the `phasej` preset for the replication runs.

None of these was made after seeing a held-out seed.
