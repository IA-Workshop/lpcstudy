# Results guide: what the LPC study found, and how to read it

This guide covers the study's two confirmatory results:
- **CONF-1**, the test of the v3 hypotheses, promoted on 2026-10-23 (ledger entry 40);
- **phase J**, the follow-on study of which conditions carry information, on seeds CONF-5 to CONF-9, promoted on 2026-10-28 (ledger entry 69).

It explains what each result says, what it allows you to say, and where it is easy to over-read. It is a reading aid written after both results were frozen and promoted. It computes no statistic and changes no verdict. The verdict words are copied exactly as stored. The student's own interpretation is in the student's sections of the reports and the research statement.

- **Sources.**
  - CONF-1: `promoted/CONF-1/report.md` (§4 verdicts, §5 estimates, §10 limitations).
  - Phase J: `promoted/phase-J/report.md` and `promoted/phase-J/confirm/confirm.md`, with each seed's records.
  - Figures: `promoted/CONF-1/report.figures/` and `docs/agent/notes/2026-10-28-phase-j-figures/`.
- **Numbers.**
  - Part 2 (CONF-1) gives words only. Its estimates and intervals are in the CONF-1 report §5.
  - Part 3 (phase J) quotes stored per-seed values, printed from the promoted records by `docs/agent/notes/2026-10-29-phase-j-interpretation-guide.values.py`.
  - "Between a and b on every seed" means the lowest and the highest of the five stored values. Nothing is averaged across seeds.
- **Kept apart.** The two results answer different questions on different seeds. Their numbers are never set side by side or compared (phase J pre-registration §9), and phase J changes nothing in CONF-1. No development-seed number appears here.

## Part 1. The study in one page

**The question.** Two forecasters predict a chaotic system from one noisy measured variable:
- **CP** (context parroting, the analog forecaster) finds the most similar moment in a library of past data and copies what happened next;
- **PLP** (physics-based latent-state propagation) estimates the hidden state and runs the known equations forward.

Their forecasts are blended with a weight w on CP. The study asks whether four measurable **local predictability conditions** can decide, state by state, how much to trust each forecaster (the **blend**), and for how long the forecast stays good (the **horizon**).

**The systems.** Lorenz-63, Rössler and Chua's circuit: three standard three-dimensional chaotic systems with exact equations.

**How the results were made.**
1. The design and code were written down and frozen first: tag `freeze-1` for CONF-1, tag `freeze-j` and the phase J pre-registration for phase J.
2. The owner then drew sealed random-number seeds, recorded only as a hash in the ledger, and ran the frozen code once on them.
3. The pre-registered rules turned the outputs into verdict words.
4. Each result was regenerated, audited and promoted by the owner.

| Term | Meaning |
|---|---|
| R, recurrence | How close the nearest past match is: CP's log starting error in noise units, ln ε/ρ |
| O, observability | PLP's log starting error in noise units, ln δ/ρ. v3 calls it **observability**. The phase J claims label the same coordinate **separation**. It is one quantity under two names |
| I, instability | The local growth rate of errors, Λ̃ |
| N, noise sensitivity | How much the analog retrieval moves when the noise changes |
| Profile | The four conditions together, (R, O, I, N) |
| Oracle profile | The conditions computed exactly from the true state. Not available in practice: it shows what the conditions could do if known |
| Deployable profile | The conditions estimated from the noisy observations. This is what a real forecaster could use |
| w\* | The best possible weight on CP for a given state and horizon (Theorem P1). 0 means trust PLP fully, 1 means trust CP fully |
| Separation | The v3 idea behind H2a: once both starting errors are known, the growth rate cancels from w\*. It gives the zero-parameter **separation formula** for the weight from R and O |
| Horizon | The time at which a forecast's error first crosses the tolerance. 1 Lyapunov time (LT) = 30 steps |
| Interval | A bootstrap confidence interval at a stated level. The verdicts depend on where the interval lies, not on the point estimate |

## Part 2. CONF-1: the test of the v3 hypotheses

**What was tested.** v3 (`docs/study/proposal_and_methods_v3.md` §2) pre-registered:
- three primary hypotheses;
- nine secondary hypotheses;
- one estimate, Q-N.

They ran on one sealed seed, CONF-1, as the official CPU run.

**How the words work** (v3 §7):
- **Pass, fail and inconclusive.** Each part of a hypothesis gets **pass** if its interval lies inside the pass band, **fail** if it lies entirely outside, and **inconclusive** otherwise. A hypothesis passes on a system only if every part passes.
- **Overall words.** **supported** means pass on all three systems; **not supported** means fail on at least one; **inconclusive** covers everything else.
- **Levels.** Primary parts use 98.33% intervals, the rest 95%.
- **Meaning:**
  - "Not supported" is not "disproved".
  - "Inconclusive" means the data could not decide at this precision, not that the effect is absent.
  - "Supported" means the prediction held on these three systems in this run.

### The primary hypotheses

| Hypothesis | What it predicted | Lorenz-63 | Rössler | Chua | Overall |
|---|---|---|---|---|---|
| H2a | Separation: once the seeds are fixed, w\* does not depend on the horizon or on instability | fail | fail | fail | **not supported** |
| H2b | w\* rises with the noise level, and with library size below saturation | pass | pass | pass | **supported** |
| H3c | A few regimes defined by the conditions cost almost nothing against the closed-form rule | inconclusive | pass | inconclusive | **inconclusive** |

**H2a, not supported.**
- **What failed:** w\* still depends on instability or the horizon once the seeds are fixed, on all three systems. The failing parts were:
  - Lorenz-63: the interior part;
  - Rössler: part (i);
  - Chua: part (i) and the interior part.
- **The pre-registered reading of a failure (v3 §7):** instability enters the weight through uneven seeds, and the size of the departure measures how far real attractors are from the separation assumption. That reading was stated in advance and is not itself tested.
- **Power:** the second part of H2a has low power. It can be refuted but essentially cannot pass (DEF-0022, accepted by the owner).

**H2b, supported.** The two interventions moved the weight in the predicted direction on every system:
- adding noise moves trust toward CP;
- a larger library moves trust toward CP.

**H3c, inconclusive.**
- Rössler passed.
- On Lorenz-63 and Chua the interval was too wide to decide.
- No system failed.

### The secondary hypotheses (95% level, no multiplicity adjustment)

| ID | What it predicted | Lorenz-63 | Rössler | Chua | Overall |
|---|---|---|---|---|---|
| H1a | The analog seed shrinks with library size as nearest-neighbor theory predicts | pass | pass | inconclusive | inconclusive |
| H1b | PLP error = seed × amplifier | inconclusive | fail | pass | not supported |
| H1c | The horizon grows with log tolerance at rate 1/Λ | fail | pass | inconclusive | not supported |
| H1d | Deployable estimates of R, O and I track their exact values | pass | pass | inconclusive | inconclusive |
| H2c | The closed-form allocator beats a global weight and the better single forecaster | inconclusive | inconclusive | pass | inconclusive |
| H2d | The closed form is within 10% of a learned allocator | inconclusive | pass | pass | inconclusive |
| H2e | CP and PLP errors become correlated as the library grows | pass | pass | pass | supported |
| H3a | Regimes separate forecast horizons | inconclusive | inconclusive | inconclusive | inconclusive |
| H3b | Instability sets the horizon, not the weight | fail | pass | inconclusive | not supported |

**Q-N** (how much N adds to the other three) is an estimate with readings, not a pass or fail:
- on every system the stored reading is "logit: reduces; indicator: substantial";
- the stored overall word keeps only the logit part.

**The gain bound** (the hybrid's horizon gain against Theorem P1's bound) is reported with no pass or fail.

### CONF-1 figures

| Figure | Shows |
|---|---|
| `promoted/CONF-1/report.figures/F1_primary.png` | Each primary part: estimate, interval and pass band, with the stored verdict as the marker shape |
| `promoted/CONF-1/report.figures/F2_secondary.png` | The same for the secondary rows and Q-N |
| `promoted/CONF-1/report.figures/F3_crosscheck.png` | The GPU cross-check of the same seed. Information only |
| `promoted/CONF-1/figures/*.png` | The four built-in plots of the run, which show point values only and no intervals. CONF-1 report §10 maps them to their experiments: w\* against horizon (H2a); Kaplan–Meier survival by rule; regret against the number of regimes (H3c); w\* against library size (H2b). The dotted 5% line on the regret plot is a reference line, not a pre-registered criterion |

### CONF-1 limitations, as ruled (CONF-1 report §10)

- One sealed seed: one realization per system, so no seed-to-seed variation is estimated.
- Three low-dimensional systems, one measured variable and an exact physics model.
- The block-bootstrap intervals slightly undercover (DEF-0020).
- The regeneration was by the same person on the same computer. It shows determinism, not independent reproduction.
- The owner's code review was waived. The code was covered by independent agent reviews.
- The secondary rows carry no numerical-error estimate.

## Part 3. Phase J: which conditions carry information

**What was tested.** CONF-1 tested the theory's predictions. The follow-on phase J asked a different, more direct question: which of R, O, I and N carry information for the blend and for the horizon?
1. **Development.** Phase J was developed on development seeds, and the readings that replicated there were written down as 12 claims, 48 rows in all (`docs/study/preregistration_phase_j/claims.json`).
2. **The test.** The claims were tested once, on five fresh sealed seeds (CONF-5 to CONF-9), with the code frozen at `freeze-j`.
3. **The rule.**
   - A row is **confirmed** if at least 4 of the 5 seeds' readings imply the claim and no two seeds contradict each other.
   - A claim is confirmed on a system if all its rows there are.
   - The other verdicts are **not confirmed**, **contradicted** and **not confirmable**. None was contradicted or not confirmable.

Phase J does not test, confirm or revise any v3 hypothesis or the CONF-1 result. The pre-registration says so (§1, §9).

**Reading words.** Each seed's interval for a ratio (a model's loss without something, divided by its loss with everything) earns a word:

| Word | Interval |
|---|---|
| **substantial** | lower bound above 1.05 |
| **needed, size not determined** | lower bound above 1, upper bound above 1.05 |
| **small** | lower bound above 1, upper bound at most 1.05 |
| **negligible** | lower bound at or below 1, upper bound between 1 and 1.05 |
| **lowers** | upper bound below 1 |
| **undetermined** | none of the above, or fewer than 50 effective states |

The **pinball loss** scores how well a model predicts each state's (median, log) horizon; lower is better. The **allocation MSE** is the blended forecast's mean squared error when a model sets the weight.

### Verdicts

| Claim | Statement (as stored) | Systems | Verdict |
|---|---|---|---|
| J-H1 | Dropping instability (I) raises the horizon loss by more than 5% | all three | **confirmed** on each |
| J-H2 | Dropping separation (O) raises the horizon loss | all three | **confirmed** on each |
| J-H3 | Dropping noise (N) changes the horizon loss by at most 5% | all three | **confirmed** on each |
| J-H4 | O and I interact in the horizon | all three | **confirmed** on each |
| J-H5 | The four-condition profile predicts the horizon better than the Lyapunov rank by more than 5% | all three | **confirmed** on each |
| J-H6 | Adding the raw delay vector to the profile lowers the horizon loss | all three | **confirmed** on each |
| J-A1 | Rossler, oracle, 1 LT: dropping R raises the allocation MSE by more than 5% | Rössler | **confirmed** |
| J-A2 | Rossler, deployable, 1 LT: the profile improves the allocation MSE over a fitted constant by at most 5% | Rössler | **confirmed** |
| J-A3 | 4 LT: a fitted constant weight has a lower MSE than the separation formula | all three | **confirmed** on each |
| J-A4 | Lorenz-63, deployable, 1 LT: the raw delay vector alone has a lower allocation MSE than the profile | Lorenz-63 | **not confirmed** |
| J-I1 | Instability adds information about the logit weight given R, O and N (deployable profile) | Lorenz-63, Chua | **confirmed** on each |
| J-C2 | Rossler: the full deployable system's realized false-trust rate is above the 10% target | Rössler | **confirmed** |

### The horizon: how long a forecast can be trusted

**J-H1, instability.**
- **Stored values:** removing I raised the horizon loss by 21 to 29% (ratios 1.209 to 1.287) on every seed, system and profile.
- **Readings:** every lower bound is at least 1.172, so every seed reads substantial.

**J-H2, O.**
- **Stored values:** removing O raised the loss by 5 to 13% (ratios 1.050 to 1.130).
- **Readings:** on Chua with the oracle profile, four seeds read "needed, size not determined". The claim needs only a ratio above 1, so they count.
- **I against O:** on every seed, the drop-I ratio is larger than the drop-O ratio. The lowest drop-I value, 1.209, is above the highest drop-O value, 1.130.

**J-H3, noise.**
- **Stored values:** removing N changed the loss by between −0.8% and +1.4% (ratios 0.992 to 1.014). Every upper bound is at most 1.024.
- **What it means:** given R, O and I, N adds almost nothing to predicting the horizon. That is a statement about prediction, not a claim that noise does not matter to the forecast.

**J-H4, O and I interact.**
- **What Δ measures:** the loss of a model forced to treat O and I separately, minus the loss of a model allowed to combine them. A Δ above zero means the effect of O on the horizon depends on the level of I.
- **Stored values:** the Holm-adjusted test detected the gain on every seed, system and profile, with Δ between 0.0052 and 0.0185.
- **Size:** Δ is in units of the loss, not a percentage. Read its sign, not its size.

**J-H5, the profile against the Lyapunov rank.**
- **What it compares:** the classical estimate (the Lyapunov time from the local growth rate, scaled by constants fitted on training data) against the four-condition model. The ratio is the classical estimate's loss over the profile's.
- **Stored values:**
  - Lorenz-63: 1.86 to 2.06;
  - Rössler: 1.36 to 1.47;
  - Chua: 1.56 to 1.65.
- **What it means:** the conditions predict the horizon much better than growth rate alone.

**J-H6, the raw state adds more.**
- **Stored values:** adding the raw delay vector to the four conditions lowered the loss by 9 to 25% (ratios 0.754 to 0.910). Every seed reads lowers.
- **What it means:** the four conditions do not hold all the horizon information in the state. Say this alongside J-H1 to J-H5.

**Oracle and deployable.** For J-H1 to J-H6, the deployable rows reached the same verdict as the oracle rows on every system. For the horizon, estimating the conditions from noisy data did not change a verdict.

### The blend: how much to trust each forecaster

**J-A1, recurrence on Rössler (oracle, 1 LT).**
- **Stored values:** removing R raised the allocation MSE by 9 to 13% (ratios 1.086 to 1.126). Every lower bound is above 1.05.
- **What it means:** with exact conditions, R is what sets the blend on Rössler.

**J-A2, the estimated profile on Rössler (deployable, 1 LT).**
- **Stored values:** the constant weight's MSE over the profile model's was between 0.992 and 1.014, all negligible. The estimated profile set the weight no better than one constant weight, within 5%.
- **With J-A1:** the exact conditions help the blend on Rössler, and the estimated ones do not beat a constant. This fits a limit in the estimates rather than in the conditions, but the round did not test that explanation directly.

**J-A3, a constant beats the separation formula at 4 LT.**
- **Stored values:** the constant weight's MSE over the formula's MSE was 0.923 to 0.987, so the constant's error was about 1 to 8% lower.
- **Readings:** two rows read negligible on one seed each, and every row had at least 4 of 5 seeds reading lowers.
- **Scope:** this holds at 4 LT. The claim says nothing about shorter horizons.

**J-A4, not confirmed.** It claimed that on Lorenz-63 at 1 LT, a weight set from the raw delay vector alone beats one set from the estimated profile.

| seed | ratio (raw / profile) | interval (level 0.99615) | reading |
|---|---|---|---|
| CONF-5 | 0.894 | 0.699 to 1.106 | undetermined (effective size under 50) |
| CONF-6 | 0.886 | 0.780 to 0.983 | lowers |
| CONF-7 | 0.742 | 0.570 to 0.909 | undetermined (effective size under 50) |
| CONF-8 | 0.778 | 0.642 to 0.905 | lowers |
| CONF-9 | 0.836 | 0.724 to 0.975 | lowers |

- **Why it failed:** three seeds read lowers, and four were needed.
- **CONF-7:** its interval lies entirely below 1. A guard fixed in advance still makes it "undetermined", because a few states carry most of the error, so the effective sample is under 50.
- **What may not be said:** "not confirmed" does not mean that the raw state fails to beat the profile.

**J-I1, instability and the weight (deployable).**
- **What it measures:** the gain in explained variance (ΔR²) of the logit of w\* when I is added to R, O and N.
- **Stored values:**
  - Lorenz-63: 0.009 to 0.051;
  - Chua: 0.046 to 0.076.
- **Readings:** on Lorenz-63, one seed reads "reduces", with an interval that includes zero. That word is compatible with the claim but does not imply it, so the row is confirmed on 4 of 5.
- **Size:** I explains a few hundredths of the variance of the weight. The effect is real on these two systems, but small.
- **Rössler:** no claim was made for Rössler.

**J-C2, over-trust on Rössler.**
- **What it measures:** the full deployable system sets the weight and predicts, for each state, a horizon the forecast should survive 90% of the time. The false-trust rate is the share of states whose forecast failed before that horizon. A calibrated system gives 10%.
- **Stored values:** 13.4% to 14.3% on Rössler, with every seed's lower bound at least 12.7%.
- **What it means:** on Rössler the system trusts its forecasts for too long. The round does not say why.

### How much to trust the phase J verdicts

- **The rule is strict.**
  - A confirmed row needs 4 of 5 seeds, each with an interval at its pre-registered level. For Tiers 1 and 2 that level is corrected for the number of rows.
  - The pre-registration (§4) puts the chance that a false Tier 1 or 2 row reads confirmed at about 1.5 in 1000 per row.
  - The two Tier 3 claims, J-I1 and J-C2, have no measured rate.
- **No contradictions.** No row had two seeds pulling in opposite directions.
- **Repeated runs agree.** Each seed was run twice. The second runs gave the same reading on every seed of every row. The GPU produced numerical differences on four seeds (DEF-0033, DEF-0035), and none changed a reading.
- **Rows close to their line:**
  - J-H2 on Chua (oracle);
  - two J-A3 oracle rows;
  - J-I1 on Lorenz-63;
  - J-A4.

  Most other rows are far from it.

### The v3 words in the phase J report

The sealed phase J runs also produced v3's verdict words as a side output (phase J report §5). They are a **secondary description, not a test**: the settings differ from v3's (a larger test split, the GPU, no robustness sweep). They do not confirm, revise or replace CONF-1.

### Phase J figures (`docs/agent/notes/2026-10-28-phase-j-figures/`)

| Figure | Shows |
|---|---|
| `F1_horizon_ablation.png` | J-H1 to J-H3: what removing each condition does to the horizon loss, by system and profile |
| `F2_allocation_ablation.png` | J-A1, with the other allocation rows faded as context |
| `F3_horizon_claims.png` | J-H4 to J-H6 |
| `F4_allocation_claims.png` | J-A2, J-A3, J-A4, J-I1, J-C2 |
| `F5_reading_grid.png` | Every row's reading on every seed, and its verdict |

Each seed is a separate colored point with its own interval. A filled point means that seed's reading implies the claim, and a hollow point means it does not.

### Phase J limitations (phase J report §6)

- The claims were chosen after development seeds were seen. That is why they were tested on fresh sealed seeds. They were expected to confirm, so confirmation checks stability. It is not a discovery.
- Five seeds, each one realization per system. Nothing is pooled.
- Below 2 LT, the blend on Lorenz-63 and Chua is mostly unreadable (the effective-size guard). No claim was made there, and J-A4 met the same guard.
- Three systems only.
- The second runs repeated the first on the same machine, which is a repetition, not an independent reproduction.
- The phase J code was built and tested by agents and not reviewed by the owner.

## Part 4. Reading the two results together

The two results ask related questions with different instruments. The table maps the questions only. It does not set their results side by side, and neither result changes the other.

| Question | CONF-1 (v3) | Phase J |
|---|---|---|
| Does instability cancel from the weight once the starting errors are known? | H2a, H3b (weight-tree part) | J-I1 (a different instrument: the gain in explained variance of logit w\*) |
| Does the separation formula set a good weight? | H2c (closed form against a global weight) | J-A3 (at 4 LT only) |
| Does instability set the horizon? | H3b (horizon-tree part), H1c | J-H1, J-H5 |
| Does noise sensitivity add to the other three? | Q-N (for the weight) | J-H3 (for the horizon) |
| Can the conditions be estimated well enough to use? | H1d | Oracle against deployable rows; J-A2 |

**Common misreadings:**

| Tempting sentence | Why not | Instead |
|---|---|---|
| "Phase J confirms (or overturns) H2a." | Phase J tests no v3 hypothesis and changes nothing in CONF-1 | "Phase J asked a related question (J-I1) with a different instrument." |
| "47 of 48 rows were confirmed, so the theory is right." | No overall verdict or count of claims may be presented as a finding (phase J §9), and phase J's claims are not the v3 hypotheses | Give each claim's verdict on each system |
| "Instability causes forecasts to fail sooner." | Both studies test prediction, not cause | "Removing instability from the model made its horizon predictions worse on every seed." |
| "Across the seeds, the drop-I ratio was 1.25." | That pools seeds | "Between 1.21 and 1.29 on every seed, system and profile." |
| "H3c is false" or "J-A4 shows no effect." | Inconclusive and not confirmed are not "no effect" | "The data could not decide it at this precision." |
| "The conditions explain the horizon completely." | J-H6: the raw state still lowers the loss by 9 to 25% | "The conditions carry much of the horizon information, but not all of it." |
| "The conditions decide the blend." | Among phase J's claims, the estimated conditions show a gain for the blend only in J-I1, and it is small. On Rössler the estimated profile does no better than a constant (J-A2) | State each blend claim with its system and profile |
| "This holds for chaotic systems in general." | Three low-dimensional systems with exact models | Name the three systems |

## Part 5. Where everything is

| Path | Contents |
|---|---|
| `promoted/CONF-1/` | The promoted CONF-1 result: report, `RESULTS.md`, `results.json`, figures (hashes in `promoted/CONF-1.sha256`) |
| `promoted/phase-J/` | The promoted phase J result: report, verdicts, each seed's records (hashes in `promoted/phase-J.sha256`) |
| `docs/study/proposal_and_methods_v3.md` | The v3 design that CONF-1 tested |
| `docs/study/preregistration_phase_j.md`, `docs/study/preregistration_phase_j/claims.json` | The phase J pre-registration and its claims |
| `docs/agent/notes/2026-10-28-phase-j-figures/` | The phase J presentation figures, made after the freeze from the promoted records |
| `docs/agent/notes/2026-10-29-phase-j-interpretation-guide.md` | The longer phase J reading guide, with its values script and output |
| `docs/agent/governance/ledger.jsonl` | The hash-chained record of every decision (`python3 tools/ledger.py verify`) |
