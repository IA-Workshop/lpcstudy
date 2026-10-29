# Phase J confirmatory round: a guide to reading the results

**PHASE J CONFIRMATORY (CONF-5 to CONF-9): a reading guide to the stored, pre-registered results. Written after the freeze; it computes no statistic and changes no verdict.** Main session (claude-opus-5-5), 2026-10-29, for the owner and the student. The student writes the interpretation (D8). This guide explains what each result says, what it allows you to say, and where it is easy to over-read.

- **Sources.** The promoted records in `promoted/phase-J/`: the report (`report.md`), the verdicts (`confirm/confirm.md`) and each seed's `contrib.json`, `ce.json` and `results.json`. The figures are in `docs/agent/notes/2026-10-28-phase-j-figures/`.
- **Numbers.** Every number below is a stored per-seed value. `2026-10-29-phase-j-interpretation-guide.values.py` prints them from the promoted records, after checking each row's readings against `confirm.json`; its output is `…values.txt`. "Between a and b on every seed" means the lowest and the highest of the five stored values. No average or pooled value is taken.
- **Kept apart.** No development number and no CONF-1 number appears here.

## 1. What this round tested

Phase J asked which of the four local conditions carry information for two decisions:
- **the blend**, how much weight to give the analog forecaster (CP) against the physics forecaster (PLP);
- **the horizon**, how long the blended forecast stays within tolerance.

The development seeds suggested answers. This round wrote 12 of them down as claims, 48 rows in all (`claims.json`), and tested them on five fresh sealed seeds with a rule fixed in advance. A row is **confirmed** if at least 4 of the 5 seeds' readings imply the claim and no two seeds contradict each other. A claim is confirmed on a system if all of its rows there are.

Terms you need:

| Term | Meaning |
|---|---|
| R, recurrence | How close the nearest past match is: the analog forecaster's log starting error in noise units, ln ε/ρ |
| O | The physics forecaster's log starting error in noise units, ln δ/ρ. The phase J claims call it **separation**. v3 calls the same coordinate **observability** (v3 §5, the profile). It is one quantity under two names |
| I, instability | The local growth rate of errors, Λ̃ |
| N, noise | Noise sensitivity of analog retrieval |
| Profile | The four conditions together, (R, O, I, N) |
| Oracle profile | The conditions computed exactly from the true state. Not available in practice: it shows what the conditions could do if known |
| Deployable profile | The conditions estimated from the noisy observations. This is what a real forecaster could use |
| Horizon | The time at which the blended forecast's error first crosses the tolerance (T_c, interpolated between steps). 1 Lyapunov time (LT) = 30 steps |
| Pinball loss | The error score of the model that predicts each state's (median, log) horizon. Lower is better |
| Loss ratio | A model's loss divided by the loss of the model with all four conditions. Above 1: the model predicts worse without what was removed |
| Allocation MSE | The mean squared error of the blended forecast when a model sets the weight from the conditions |
| Constant weight | A single blend weight for every state, fitted on training data. The simplest alternative |
| Separation formula | v3's zero-parameter weight from R and O, w = 1/(1 + e^{2(R−O)}) |
| Reading | The word a seed's interval earns under the frozen 1.05 table: **substantial** (lower bound above 1.05), **needed, size not determined** (lower bound above 1, upper above 1.05), **small** (between 1 and 1.05), **negligible** (lower bound at or below 1, upper bound between 1 and 1.05), **lowers** (upper bound below 1), **undetermined** |

## 2. The results, claim by claim

### The horizon (how long a forecast can be trusted)

**J-H1. Instability.** Confirmed on Lorenz-63, Rössler and Chua.
- **Stored values:** removing I raised the horizon loss by 21 to 29% (ratios 1.209 to 1.287) on every seed, system and profile.
- **Readings:** every lower bound is at least 1.172, well above the 1.05 claim line, so every seed reads substantial.
- **Plain reading:** I carries more information than O or N about how long a forecast stays good.

**J-H2. O (separation).** Confirmed on all three systems.
- **Stored values:** removing O raised the loss by 5 to 13% (ratios 1.050 to 1.130).
- **Readings:** on Chua with the oracle profile, four seeds read "needed, size not determined". Their lower bounds are above 1 but below 1.05. The claim only needs a ratio above 1, so they count.
- **Ordering of I and O:** on every seed the drop-I ratio is larger than the drop-O ratio. The lowest drop-I value, 1.209, is above the highest drop-O value, 1.130.

**J-H3. Noise.** Confirmed on all three systems.
- **Stored values:** removing N changed the loss by between −0.8% and +1.4% (ratios 0.992 to 1.014), and every upper bound is at most 1.024.
- **Readings:** mostly negligible. Four read small (just above 1 but below 1.05) and two read lowers. All three words imply "at most 5%".
- **Plain reading:** given R, O and I, N adds almost nothing about the horizon. That is a claim about prediction. It does not mean noise does not matter to the forecast.

**J-H4. O and I interact.** Confirmed on all three systems.
- **What Δ measures:** the loss of a model forced to treat O and I separately, minus the loss of a model allowed to combine them. A Δ above zero means the effect of O on the horizon depends on the level of I.
- **Stored values:** the Holm-adjusted test detected the gain on every seed, system and profile. Δ is between 0.0052 and 0.0185.
- **Size:** Δ is in units of the loss, not a percentage. This guide does not read its size, only its sign.

**J-H5. The profile against the Lyapunov rank.** Confirmed on all three systems.
- **What it compares:** the classical estimate, the Lyapunov time from the local growth rate scaled by constants fitted on training data, against the four-condition model. The ratio is the Lyapunov estimate's loss over the profile's.
- **Stored values:**
  - Lorenz-63: 1.86 to 2.06;
  - Rössler: 1.36 to 1.47;
  - Chua: 1.56 to 1.65.
- **Plain reading:** the four conditions predict the horizon much better than growth rate alone. On Lorenz-63 the Lyapunov estimate's loss is about twice the profile's.

**J-H6. The raw state adds more.** Confirmed on all three systems.
- **Stored values:** adding the raw delay vector to the four conditions lowered the loss by 9 to 25% (ratios 0.754 to 0.910). Every seed reads lowers.
- **Plain reading:** the four conditions do not hold all the information about the horizon that the state contains. This limits J-H1 to J-H5, and is worth saying alongside them.

**Oracle and deployable.** For J-H1 to J-H6, the deployable rows reached the same verdict as the oracle rows on every system. For the horizon, estimating the conditions from noisy data did not change any verdict.

### The blend (how much to trust each forecaster)

**J-A1. Recurrence on Rössler (oracle, 1 LT).** Confirmed.
- **Stored values:** removing R raised the allocation MSE by 9 to 13% (ratios 1.086 to 1.126), and every lower bound is above 1.05.
- **Plain reading:** with the exact conditions, R is what sets the blend on Rössler.

**J-A2. The estimated profile on Rössler (deployable, 1 LT).** Confirmed.
- **What it compares:** the constant weight's MSE over the profile model's MSE.
- **Stored values:** between 0.992 and 1.014, all negligible. The estimated profile set the weight no better than one constant weight, within 5%.
- **Read with J-A1:** the exact conditions help the blend on Rössler, and the estimated ones do not beat a constant. This fits a limit in the estimates rather than in the conditions. This round did not test that explanation directly.

**J-A3. A constant beats the separation formula at 4 LT.** Confirmed on all three systems.
- **Stored values:** the constant weight's MSE over the formula's MSE was 0.923 to 0.987. The constant's error was about 1 to 8% lower.
- **Readings:** two rows read negligible on one seed each, Chua oracle on CONF-6 and Rössler oracle on CONF-8. Each row still had 4 of 5 seeds reading lowers.
- **Plain reading:** at long horizons, v3's zero-parameter formula sets the weight worse than doing nothing state-specific. Say that it holds at 4 LT. This claim says nothing about shorter horizons.

**J-A4. The raw state against the profile on Lorenz-63 (deployable, 1 LT).** Not confirmed. See §3.

**J-I1. Instability and the weight (deployable).** Confirmed on Lorenz-63 and Chua.
- **What it measures:** the gain in explained variance (ΔR²) of the logit of the best weight when I is added to R, O and N.
- **Stored values:**
  - Lorenz-63: 0.009 to 0.051;
  - Chua: 0.046 to 0.076.
- **Readings:**
  - On Lorenz-63, CONF-5 reads "reduces": its interval, −0.015 to 0.032, includes zero. CONF-6 reads distinct but small. The other three read substantial.
  - "Reduces" is compatible with the claim but does not imply it. So the row is confirmed on 4 of 5.
- **Size:** I explains a few hundredths of the variance of the weight. That is real on these two systems, but small.
- **The H2a question:** this is the question behind v3's H2a, whether instability cancels from the weight. It is asked here with a different instrument. It is **not a test of H2a** and it changes nothing in CONF-1.
- **Rössler:** no claim was made for it, so this round says nothing about Rössler here.

**J-C2. Over-trust on Rössler.** Confirmed.
- **What it measures:** the full deployable system sets the weight and predicts, for each state, a horizon that the forecast should survive 90% of the time. The **false-trust rate** is the share of states whose forecast actually failed before that horizon. A calibrated system gives 10%.
- **Stored values:** 13.4% to 14.3% on Rössler, and every seed's lower bound is at least 12.7%.
- **Plain reading:** on Rössler, the full system trusts its forecasts for too long.
- **Cause:** this round does not say why. The development report (2026-10-26, §5) points to the horizon model rather than the weight. That is development evidence and was not tested here.

## 3. The one claim not confirmed: J-A4

J-A4 claimed that on Lorenz-63, at 1 LT, a blend set from the raw delay vector alone has a lower MSE than one set from the estimated profile.

| seed | ratio (raw / profile) | interval (level 0.99615) | reading |
|---|---|---|---|
| CONF-5 | 0.894 | 0.699 to 1.106 | undetermined (effective size under 50) |
| CONF-6 | 0.886 | 0.780 to 0.983 | lowers |
| CONF-7 | 0.742 | 0.570 to 0.909 | undetermined (effective size under 50) |
| CONF-8 | 0.778 | 0.642 to 0.905 | lowers |
| CONF-9 | 0.836 | 0.724 to 0.975 | lowers |

- **Why it failed:**
  - three seeds read lowers, and the rule needs four;
  - CONF-7's interval lies entirely below 1, but a guard fixed in advance makes any row with an effective sample under 50 "undetermined" whatever its interval. At 1 LT on Lorenz-63, a few states account for most of the excess error, so the effective sample is small;
  - the guard was applied exactly as frozen.
- **What you may say:** "J-A4 was not confirmed under the pre-registered rule; three of five seeds read lowers, and two were undetermined by the sample-size guard."
- **What you may not say:** that the raw state does not beat the profile, or that there is no effect. "Not confirmed" means the round could not establish it.

## 4. How much to trust the verdicts

- **The rule is strict.** A confirmed row needs 4 of 5 independent seeds, each with an interval at its pre-registered level (corrected for multiple rows in Tiers 1 and 2; the figure titles list the levels). The pre-registration (§4) put the chance that a false Tier 1 or 2 row still reads confirmed at about 1.5 in 1000 per row. The two Tier 3 claims, J-I1 and J-C2, have no measured rate.
- **No contradictions.** No row had two seeds pulling in opposite directions.
- **Repeated runs agree.** Each seed was run twice. The second runs gave the same reading on every seed of every row, and the same verdicts (report §3). On four seeds the GPU produced numerical differences between the two runs (DEF-0033, DEF-0035), and none changed a reading.
- **Most rows are far from their line.** For example, every drop-I lower bound is above 1.17 against the 1.05 line. The rows close to their line are:
  - J-H2 on Chua (oracle);
  - J-A3's two oracle rows;
  - J-I1 on Lorenz-63;
  - J-A4.

  The figures show this most clearly.

## 5. Common misreadings

| Tempting sentence | Why not | Instead |
|---|---|---|
| "47 of 48 rows were confirmed, so the theory is right." | The pre-registration (§9) forbids an overall verdict or a count of claims as a finding. Claims differ in importance | Give each claim's verdict on each system |
| "Instability causes forecasts to fail sooner." | The round tests prediction, not cause (§9) | "Removing instability from the model made its horizon predictions worse on every seed." |
| "Across the seeds, the drop-I ratio was 1.25." | That pools seeds (§9) | "Between 1.21 and 1.29 on every seed, system and profile." |
| "The raw state is no better than the profile on Lorenz-63." | "Not confirmed" is not "no effect" (§9) | See §3 |
| "Phase J confirms (or overturns) H2a / CONF-1." | Phase J does not test v3 hypotheses and changes nothing in CONF-1 (§9) | "Phase J asked a related question, J-I1, with a different instrument." |
| "Noise doesn't matter." | J-H3 is about the horizon prediction given R, O and I | "Given R, O and I, noise sensitivity adds almost nothing to the horizon prediction." |
| "The conditions explain the horizon completely." | J-H6: the raw state still lowers the loss by 9 to 25% | "The conditions carry most of the information we tested for, but not all of it." |
| "The conditions decide the blend." | Among the claims, the estimated conditions show a gain for the blend only in J-I1 (Lorenz-63 and Chua), and it is small. On Rössler the estimated profile does no better than a constant (J-A2) | State the blend claims one at a time, with the profile (oracle or deployable) named |

## 6. The v3 words in the report (§5 there)

The sealed runs also produced v3's verdict words (H1a to H3c) as a side output.
- **Status:** they are a **secondary description**, not a test. The settings differ from v3's: a larger test split, the GPU and a skipped robustness sweep.
- **What they may not be used for:** they do not confirm, revise or replace CONF-1.
- **The CONF-1 column:** the report shows CONF-1's words as a reference column only. A different word on a phase J seed describes how v3's words vary with the seed and the settings. Don't present it as a new result for any H.

## 7. Limitations to keep in view

All of report §6 applies. These matter most for interpretation:
1. The claims were chosen after seeing development seeds. That is why they were tested on fresh sealed seeds. They were expected to confirm, so confirmation is a check of stability, not a discovery.
2. Each seed is one realization per system, and five seeds is a small sample. Nothing is pooled.
3. Below 2 LT, the blend on Lorenz-63 and Chua is mostly unreadable (the sample-size guard). No claim was made there, and J-A4 met the same guard.
4. Only three systems were tested. Nothing here extends to other systems.
5. The second runs repeated the first on the same machine. That is a repetition, not an independent reproduction.
6. The phase J code was built and tested by agents and not reviewed by the owner.

## 8. Which figure shows what

| Claim | Figure |
|---|---|
| J-H1, J-H2, J-H3 | `F1_horizon_ablation.png`: drop-one ratios, by system and profile |
| J-A1, with the allocation context rows | `F2_allocation_ablation.png` |
| J-H4, J-H5, J-H6 | `F3_horizon_claims.png` |
| J-A2, J-A3, J-A4, J-I1, J-C2 | `F4_allocation_claims.png` |
| Every row's readings and verdict | `F5_reading_grid.png` |

In every figure, each seed is a separate colored point with its own interval. A filled point means that seed's reading implies the claim, and a hollow one means it does not.

## 9. Prompts for the student's interpretation

- Which of the two decisions do the conditions inform better, the horizon or the blend? Which claims support your answer, and with which profile?
- What does J-H6 tell you about what the four conditions leave out?
- On Rössler, J-A1 and J-A2 together suggest the conditions help the blend only when known exactly. What would you test next to find out where the estimate loses that value?
- How would you explain J-A4's "not confirmed" to a judge without saying "no effect"?
- What would you change about the full system, given J-C2?
