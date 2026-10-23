# Research statement v3 (final draft for the owner and the student to edit): when should a forecaster trust the past, and when the physics?

Draft by claude-sonnet-5-5 (WU-0025.3), 2026-10-23, from `2026-10-23-research-statement-v2.md` and DEC-0045, for the internal proposal due 2026-10-28. The student (Deem Albaty) writes the interpretation and owns the final text (D8). `[STUDENT: ...]` marks words only the student can supply, `[OWNER: ...]` words only the owner can supply. Sections 1 to 10 and the glossary are the statement. Everything after "For the author" is not part of the submission.

**Number rule.** The statement body has no number from any run. Result words are copied from section 4 of the promoted report (`promoted/CONF-1/report.md` §4, lines 91 to 125; checked against the file on develop at cc27d31). Where the student wants an estimate, it is copied from §5 of the promoted report with its interval and level, and cited by section and row; none is quoted here. Development numbers (ensemble, extension systems, Dysts tables) never appear in the body; they are in the standalone development appendix A (`docs/agent/notes/2026-10-23-appendix-a-standalone.md`, 1073 traced values) and are reached only by pointer. The digits left in the body are design constants of v3, dates, system names, and one ratio of two published or v3-stated values (Chua exponent, §9, tag U9).

Tags: `{S#}` are the v1 trace rows (v1 file `2026-10-19-research-statement-draft.md`), `{T#}` the v2 rows, `{U#}` new rows; all three are in the trace table at the end. Remove the tags in the final text.

## What changed from v2

| Where | v2 | v3 | Why |
| --- | --- | --- | --- |
| Promotion label | "[OWNER: label, proposed ...]" | fixed: "Confirmatory result, seed CONF-1, promoted by the owner on 2026-10-23"; the stored provenance row "CONFIRMATORY: UNPROMOTED" is never copied | DEC-0045 item 2; promotion closeout note |
| §1 and F5 "never seen" | open flag | resolved with records-based wording (seed drawn and sealed by hash before the run; rules and code frozen first) and a stated limit on what is not claimed | DEC-0001; report §2 (freeze check); {U1} |
| §4 and F1 | v1 sentences "assembled" from v3, flag open | four one-line definitions, each tied to a v3 sentence or table row | v3 §3, §4, §5, P2; {U2 to U5} |
| §5 and F2 | no reason given | a recommended reason drawn from v3 §4 and §8 and from the benchmark literature, with what v3 does and does not say | {U6} |
| §3 theorems | v1 wording | P1 horizon bound stated with its conditions (errata addendum of 2026-10-21) | theorem program errata; DEC-0040; {U7} |
| §8 and F9 | "would not show" inferred, flag open | concrete wording from v3 §8 scope and future work, plus what the extension does not change | v3 §8; {U8} |
| §8 later study | "A later study" | "a subsequent pre-registered study" (never "v4") | DEC-0045 item 2 |
| §9 Extension | "[OWNER: confirm names]", gate not mentioned | names fixed by appendix A.2 (six systems); all but one failed gate check V7 and are marked PROVISIONAL; verdict-reporting code is development-only and not owner-reviewed | DEC-0045 items 2 and 3; appendix A.2; ensemble summary |
| §9 Dysts context | Chua difference "could not be found" | the Chua sentence of the mathematician's attribution note; V3 stated with its threshold and its target; Dysts tables and benchmark mapping incorporated without any development value | `2026-10-23-math-chua-attribution.md` §5; `2026-10-23-math-benchmark-mapping.md` §1 and F1, F4; `2026-10-23-researcher-dysts-tables.md` |
| §9 appendix pointer | "descriptive table in the development appendix" | appendix A holds the ensemble and the extension; the Dysts descriptive table is separate (WU-0024.3, not in the standalone appendix as built) | appendix A section list |
| §10 | status to promotion | same dates; AI-use statement now says agents reviewed the code | {T6} |
| Counting of PROVISIONAL | v2 §7 says no result is provisional (true for the three studied systems) | v3 says "the three studied systems" explicitly, so it cannot be read as covering the extension, where five of six systems are PROVISIONAL (appendix A.2) | DEC-0045 item 2. v2 has no sentence saying "two PROVISIONAL"; the wording is made exact so none can be read in |

## 1. The research question

Can four measurable local conditions of a chaotic system decide, state by state, how much to trust an analog forecaster (one that copies the past) versus a physics-based forecaster (one that runs known equations), and for how long? {S1} We tested this with three pre-registered hypotheses on three simulated chaotic systems. {S2} The rules and the code were frozen before the official run, and the official run used a fresh random-number seed that the owner drew and sealed (it was recorded only as a salted hash) before the run, separate from every development seed. {U1}

## 2. Why it matters

A chaotic system is deterministic, but a tiny error in its starting state grows quickly, so every forecast of it eventually fails. {S3} Forecasting such systems matters from sensing to climate. {S4} Analog forecasters find the past situation most like the present and copy what followed; they improve with more data. Physics-based forecasters integrate known equations, but must first estimate the hidden current state from noisy measurements. {S5} Most hybrids combine the two in a fixed way, and we know of no earlier work that decides, state by state, which to trust. {S6} [STUDENT: one sentence, in your words, on why this matters to you or a reader.]

## 3. The two forecasters and the blend weight

Both see only one noisy measurement (the observable) of a three-dimensional chaotic system. {S7}

- **CP (context parroting, the analog forecaster)** takes a delay vector (a short window of recent measurements), finds the nearest one in a library of recorded past data, and copies what followed. {S8}
- **PLP (physics-based latent-state propagation)** estimates the hidden state from the delay vector (a neural-network first guess, then 15 fitting steps against the known equations) and integrates the equations forward. {S9}

The hybrid is w times CP plus (1 minus w) times PLP; the blend weight w, from 0 to 1, is the weight on CP. {S10} The best weight, w\*, gives the least mean squared error (the average squared forecast error). Theorem P1 gives w\* in closed form from the two forecasters' average errors and how they move together. {S11} Under the conditions stated in the theorem, blending can extend the forecast horizon (how far ahead a forecast stays accurate) by at most half an error-doubling time. {S12, U7}

## 4. The four local predictability conditions

Each is a property of one state, and each has a precise definition in v3.

- **Recurrence:** how close the nearest matching past state is to the present one (the distance to the best analog in the library). {U2}
- **Observability:** how well the hidden state can be recovered from noisy measurements (large when the measurements pin the state down poorly). {U3}
- **Instability:** how fast small errors grow along the forecast (the amplifier that makes both forecasters' errors grow). {U4}
- **Noise sensitivity:** how much the chosen past match moves when the noise changes; it is defined on the analog side only. {U5} Theorem P2 shows the match is stable while the noise is smaller than half the gap between the nearest and second-nearest candidates. {S17}

Recurrence and observability set the two forecasters' starting errors; instability sets how fast both grow. {S18b}

## 5. The three test systems

Lorenz-63, Rössler, and Chua's circuit (an electronic circuit with a piecewise-linear diode) each have exactly known equations, so true hidden states and every condition can be computed. {S18} We chose them because their equations are exact, they are standard chaotic systems that other forecasting benchmarks also use, and they differ in shape and in how fast errors grow; Chua's has a piecewise-linear part where the other two are smooth. {U6} We observe one variable, x, and score forecasts against the noise-free truth. {S19} Time is counted in Lyapunov times (1 divided by the largest Lyapunov exponent, the long-run growth rate of small errors), set to 30 steps in every system. {S20} [STUDENT: if your own reason for these three differs from the one above, replace it; v3 itself gives only "exact models".]

## 6. The design in plain words

- **Pre-registered hypotheses.** Hypotheses, statistics and decision rules were fixed before the confirmatory run. {S21} The three primary ones: (H2a) given the starting errors, the best weight does not depend on horizon or instability; (H2b) it rises with noise level and library size; (H3c) a few regimes (groups of similar states) lose almost nothing against the closed-form rule. {S22} Nine secondary hypotheses and one estimate are also pre-registered. {S23}
- **Sealed fresh seed.** The confirmatory run used a sealed random-number seed: new noise, libraries and trajectories on the same three systems. {S24}
- **Intervals.** Each statistic has a confidence interval (a range of plausible values) from a moving-block bootstrap (resampling blocks of 5 neighboring test states, 2000 times). {S25} Primaries use level 1 − 0.05/3, stricter because there are three; the rest use 95%. {S26}
- **Verdict rule.** Per system, a hypothesis passes if its interval lies inside the pre-set band (acceptable range) or wholly on the predicted side of a bound, fails if wholly outside, and is otherwise inconclusive. {S27} Each hypothesis then gets one overall word: "supported" only if all three systems pass, "not supported" if at least one fails, and "inconclusive" otherwise. {S28, T2}
- **Validity gates.** Seven checks (V1 to V7) confirm the numerical tools first. A failure marks that system's results provisional, is reported to the owner, and is never repaired by retuning or rerunning. {S29}
- **Cross-checks.** The official run was on a CPU. A GPU run of the same seed is an information-only cross-check and changes no verdict. {S30, T11} The design asked another person to regenerate the official run. With only one person on the team able to run it, the owner regenerated it on the same computer: every compared value was equal, which shows the run is deterministic, not that it reproduces on another computer. {T5}
- **All outcomes are reported,** failures included. {S31}

## 7. What we found

Header for this section and every copy of it: **Confirmatory result, seed CONF-1, promoted by the owner on 2026-10-23.** {T1, U10}

All three studied systems passed the validity gate (checks V1 to V7; V3 is only reported), so no result of the pre-registered study is marked provisional. {T4}

- **H2a: not supported.** It failed on all three systems. "Not supported" is not "disproved", and it says nothing about systems beyond the three studied. v3 fixed in advance how a failure would be read (instability enters the weight through uneven starting errors); that reading was not itself tested. {T2} The second part of H2a can be refuted but essentially cannot pass at these sample sizes, as v3 anticipated. {S38, T7}
- **H2b: supported.** It passed on all three systems in this run. {T2}
- **H3c: inconclusive.** It passed on Rössler; on Lorenz-63 and Chua it could not be decided at this precision; no system failed. Inconclusive does not mean the effect is absent. {T2}
- [OPTIONAL, one line, the pre-fixed secondary highlights in their §4 words: H2c inconclusive, H2e supported, H3a inconclusive (it cannot fail by design), Q-N an estimate read from the v3 table, not pass or fail. {T3}]

[STUDENT: if you quote an estimate, copy it with its interval and level from §5 of the promoted report and cite the row. Otherwise leave numbers to the poster figure F1.]

[STUDENT: your reading of what these three words mean, and what surprised you, marked as interpretation.]

## 8. What is claimed and what is not

"Supported" means: on these three systems, with an exact physics model and one measured variable, the pre-registered prediction held in this run. {S32} It does not show the same for a physics model that is wrong or only approximate (the model here is exact), for real measured data (every series here is simulated), or for higher-dimensional systems (all three studied have three dimensions); v3 lists these as future work. It also does not show that the same pattern holds for other seeds, because one sealed seed gives one realization per system. {U8, S34} "Not supported" means at least one system failed a pre-set test; its error is not controlled the same way and, with 95% intervals, can reach about 7.3% over three systems. {S33} "Inconclusive" is not "no effect".

Limits stated in advance by v3 (tags S34 to S39), plus the limits the owner ruled on before promotion:

- Three low-dimensional systems, one observable, one sealed seed, so one realization per system. {S34}
- Same systems with fresh random numbers: more precision, not new systems. {S35}
- Practical (non-exact) features carry little of the information in the exact ones, so allocation results are limited by them, not by theory. {S36}
- H3a cannot fail; the second part of H2a has low power: it can be refuted but essentially cannot pass. The owner accepted this as a known limitation. {S38, T7}
- The intervals cover slightly less often than their nominal level. {S39}
- The regeneration was by the same person on the same computer: it shows determinism, not an independent reproduction. Results depend on the thread count and the computer's linear-algebra library, so another computer may differ. {T5}
- The owner did not review the code; the owner spot-checked the results, and the code was covered by independent AI-agent reviews. {T6}
- For the secondary and reported rows the official results file gives no numerical-error estimate and no per-quantity verification status. {T8}
- The four built-in report figures name no experiment or hypothesis and show no interval; a dotted line in the regret figure is a reference line, not a pre-registered criterion. {T9}
- A subsequent pre-registered study will need different intervals and sample sizes; this changes nothing in the present analysis. {T10, U11}

## 9. Beyond the pre-registered study (development, exploratory)

Header for this section and every copy of it: **DEVELOPMENT CONTEXT: not a hypothesis test.** (Drafting rule, criterion E8 of WU-0025: the paragraphs below contain no digit except in system names and the one ratio of tag U9; the tags are removed in the final text.)

**Extension.** After the pre-registered run, and on development seeds only, we asked whether the same patterns appear in chaotic systems that differ from the three studied in a qualitative way. Six systems were run: a higher-dimensional Rössler system with two directions of error growth; a Lorenz system in a regime with intermittent bursts; Rössler observed through a different variable; and three further systems from the Dysts collection (a Hindmarsh-Rose neuron model, a hyperchaotic Lorenz-family system called HyperJha, and a four-variable Lorenz-96 system). {T12, U12} The forecasters, the tests and the decision thresholds were the same as in the pre-registered study, and the readings were written down before any extension run. {T13} Only the higher-dimensional Rössler system passed the validity gate; the other systems failed check V7 (the check that the state estimator reaches its theoretical accuracy floor) and are marked PROVISIONAL, with their words shown as stored and the failure reported, not repaired. {U13} Each extension system is read on its own: there is no overall verdict, no ranking of systems, and nothing here changes or adds to the pre-registered result. Each system was run on one development seed only, so seed-to-seed variation is not known for them. A confirmatory claim about any of these systems would need its own sealed seed and freeze. {T12, T13, T19} The code that reports the extension's verdicts is development-only and has not been reviewed by the owner. {U14}

**Development ensemble.** We also repeated the full study on several development seeds for the three studied systems, to see how much the readings move from seed to seed. Those runs are shown side by side in development appendix A, without any average or range, and are not a test. {T14}

**Dysts context.** Dysts is a public collection of chaotic systems with published forecasting benchmarks, which our design document cites. {T15} Its entries for Lorenz-63, Rössler and Chua use the same equations as ours, with parameters equal up to rounding. {U15} The Dysts database's stored maximum Lyapunov exponent for Chua differs from ours by a factor of about 2.85; our value is reproduced by an independent estimator; the cause of the Dysts value is not determined. {U9} We tested and excluded differences of equations, parameters, time unit, attractor and integration settings, and Dysts' own Lyapunov spectrum entry for the same system is near our value; no published reference value for Chua at our parameters exists, so neither Dysts number validates ours. {U9} The benchmark measures error, time and noise in different units, scores forecasts with a percentage error that depends on the size of the signal, reports averages over many systems, and has no forecaster with known equations like PLP, so its values are context only and cannot be compared directly with ours. {T17, U16} Where we quote our analog forecaster's valid-prediction time (check V3), it counts a forecast as valid until its error first exceeds 0.4 of the standard deviation of the observed variable, and the error is measured against the noisy verifying observation, not the noise-free truth; it is reported for context and is not a gate. {U17} All values, and the separate descriptive table of the Dysts definitions, are in the development appendix and its companion table, not here. {U18}

[STUDENT: one sentence, marked as interpretation if it is one, on why you wanted to look beyond the three systems.]

## 10. Status and timeline

The design was frozen before the confirmatory run. The official run used the sealed seed on 2026-10-19 (CPU); the GPU cross-check and the regeneration followed on 2026-10-20; two audits followed; the owner promoted the result on 2026-10-23. {T18} [STUDENT: next steps and the dates you commit to.] Deem leads the questions, proofs of P1 and P2, interpretation and presentation; Brian reviews and runs the computation; an AI assistant (Claude) helped with drafting, reference checks, code and code review, and the author reviewed it. {S41} [STUDENT: confirm roles and the AI-use statement in your words; it must say that AI agents also reviewed the code, because the owner's code review was waived. {T6}]

## Glossary (v1 glossary plus additions)

The v1 glossary (chaotic system, Lyapunov exponent and time, observable, delay vector, CP, PLP, mean squared error, w\*, forecast horizon, theorems P1 and P2, pre-registration, seed, confidence interval and moving-block bootstrap, band and verdict, validation gate, cross-check) is unchanged. Additions:

| Term | Plain meaning |
| --- | --- |
| Promotion | The owner's recorded decision that a checked result may be reported as the study's result. |
| Development seed | Random numbers used for building and exploring, never for the pre-registered test. |
| Exploratory | Looked at to learn, not to test a prediction fixed in advance. |
| Determinism vs. reproduction | Same inputs on the same computer give the same output; reproduction means another person or computer gets it too. |
| Hyperchaos | Chaos with more than one direction in which small errors grow. |
| Intermittency | Long calm stretches broken by irregular bursts. |
| Dysts | A public database of chaotic systems with forecasting benchmarks. |
| PROVISIONAL | A system's results shown with a mark because a validity check failed; the failure is reported and nothing is retuned. |

---

## For the author (not part of the statement)

### A. Recommended wording for the four v1 flags (now in the text; the evidence)

- **F1, four definitions (§4).** Recurrence: v3 §4 (CP) "The recurrence distance R is the distance to that analog". Observability: v3 §5 table, ν² = tr[(JᵀJ)⁻¹], and §1 "accuracy depends on how well that state can be reconstructed". Instability: v3 §3 "instability sets the amplifier" and §5 (Λ̄). Noise sensitivity: v3 §5 table, "r.m.s. displacement of the retrieved analog's delay vector across draws, per coordinate, in units of ρ (P2)", and §3 "the fourth condition is defined on the analog side". The pairing of recurrence and observability with the starting errors and of instability with the amplifier is v3 §3's own sentence. The parenthetical "large when the measurements pin the state down poorly" in the observability bullet is a plain-language gloss of ν as a noise amplification factor (ν² is a trace of an inverse information matrix); the student should confirm it reads right.
- **F2, why these three (§5).** v3 §4 gives only "exact models"; v3 §8 calls the choice "deliberately narrow". The added reasons are (a) standard, widely used systems (Gilpin 2023 names "the Lorenz, Rössler, and Chua attractors" as well-known systems; mapping note M1), and (b) they differ in shape and in error growth (v3 §4 table: three different exponents; the Chua field is piecewise linear). Reason (b) is a description of the table, not a design intention recorded by v3. The sentence says "we chose them because", which is a claim about intent that only the owner or the student can confirm.
- **F5, "never seen" (§1).** Records support: the confirmatory seed is drawn by the owner at the freeze, committed by salted SHA-256 in the ledger and supplied only at run time (DEC-0001); the run's commit equals freeze-1 (report §2, "Freeze check"); the pilot seed was rejected for reuse because its results had been seen (DEC-0001). Records do not state in these words that no person or agent viewed the data before the run, so the text does not say "never seen" and says "sealed" and "separate from every development seed". If the owner can attest that nobody looked, that sentence is theirs to add.
- **F9, what a pass would not show (§8).** From v3 §8: "three low-dimensional systems, an exact physics model, one observable" and its future-work list (a misspecified physics model, transfer to a higher-dimensional system, independent trajectory replicates). "Real measured data" is added because every series in v3 §4 is a simulation; it is implied by §4's "All experiments are simulations".

### B. Must NOT be said

- No overall verdict for any extension system, and no "supported" or "not supported" for them; per-system words only, and only in appendix A. The gate words "PASS" and "PROVISIONAL" are allowed for them; "extension supports the result" is not.
- No ranking of systems, forecasters or methods; none of "outperform", "beats", "better than", "worse than", "superior", "wins", "state of the art" (WU-0024 D3).
- No "proved", "proves", "confirmed", "confirms", "significant", "shows that", "demonstrates", "breakthrough" for a result (a theorem may be "proved").
- "Inconclusive" never as "no effect"; "not supported" never as "disproved" or "false".
- No development number (ensemble, extension, Dysts table) in the statement or beside the sealed result; only in the labeled appendix. The one allowed ratio is the Chua sentence of §9 (U9).
- Not that the result was independently reproduced, nor that the owner reviewed the code, nor that the extension's verdict-reporting code was reviewed by the owner.
- Not that the extension confirms, extends or generalizes the pre-registered result.
- Not "v4"; write "a subsequent pre-registered study".
- Not the stored provenance row "CONFIRMATORY: UNPROMOTED" or the headers "(preliminary, unpromoted)".
- Not the values "1.97, 3.43, 2.8" (or any V3 value) in any form. They are the stored V3 values of the sealed run (report §3) and also appear in a development note labelled "error above 0.2" (see open item 9 for the owner). V3 is not quoted numerically anywhere in this statement.
- Not "2.79" or any ensemble value of the Chua ratio; the ratio in §9 is the DEV-0 and v3-table one used by the attribution note.
- No number not copied from the promoted report with its section.

### C. Honesty checklist (tick when the final text leaves the owner and the student). Ticks below are for this draft, with evidence; re-tick after the student edits.

- [x] The promotion label is on §7 and is the DEC-0045 wording. Evidence: §7 header; "UNPROMOTED" and "v4" occur in this file only in the what-changed table, the must-not-say list and this checklist, never in the body (grep run on the body, 0 hits).
- [x] The three primary words are exactly those of report §4 (H2a not supported; H2b supported; H3c inconclusive); H3c carries its per-system words. Evidence: compared with the H2a, H2b and H3c rows of the §4 table in `promoted/CONF-1/report.md` on develop (H2a fail/fail/fail; H2b pass/pass/pass; H3c inconclusive/pass/inconclusive for Lorenz-63/Rössler/Chua).
- [x] No result number is quoted. Evidence: §7 quotes none; the student slot says to copy from §5 with interval and level.
- [x] §9 has no digit except in system names and tag U9's ratio, and the 0.4 of V3 (a code constant, tag U17); it carries the development header, "no overall verdict" and "not a hypothesis test". Evidence: grep of §9 (the digits found are 2.85 and 0.4 and none else, apart from system names "Lorenz-63", "Lorenz-96", "V3", "V7", "Chua" tags).
- [x] §8 has every ruled limit: DEF-0022 power, same-host regeneration, waived code review with spot-checked results, NVVUQ.22 gaps, figure captions, a subsequent pre-registered study needs different intervals and sample sizes.
- [x] The cross-check sentence says "information-only" and "changes no verdict" (§6).
- [x] Nothing of section B appears in the body. Evidence: case-insensitive grep for the banned words over the body (lines before "For the author") returns only the sentence "'Not supported' is not 'disproved'" and 'Inconclusive does not mean...' which are the allowed negations.
- [x] PROVISIONAL counts are right: body says "the three studied systems" passed all gates; "only the higher-dimensional Rössler" passed among the extension systems; the others failed V7. Evidence: appendix A.2 gate table (rossler_hyper yes; the other five V7 no).
- [x] "Subsequent pre-registered study", not "v4". Evidence: grep "v4" returns no hit in the body.
- [x] Dysts and Chua sentences match their sources (attribution note §5 sentence; tables note A.1 and A.2).
- [ ] Interpretation is the student's and is marked as such; the AI-use statement is updated. (The student's act; slots in §2, §5, §7, §9, §10.)
- [ ] Owner confirms the §5 and §1 intent wording (items 1 and 2 below).

### D. Trace table. Every sentence with a number or a verdict word maps to a source. Kind: Q near-quote, P paraphrase, A assembled.

v1 rows S1 to S41 are in `2026-10-19-research-statement-draft.md` (trace table at its end) and are unchanged except S2 (the "sealed fresh random-number seed" clause now also rests on U1) and S12 (conditions added, U7). v2 rows T1 to T19 are in `2026-10-23-research-statement-v2.md` §D and are unchanged, except T10 (wording "a subsequent pre-registered study", U11) and T12 (system list now fixed, U12). New rows:

| Tag | Statement | Source | Kind |
| --- | --- | --- | --- |
| U1 | Seed drawn by the owner at the freeze, committed by salted SHA-256 in the ledger, supplied only at run time; rules and code frozen before the run (run commit equals freeze-1); the sealed seed is separate from DEV seeds | DEC-0001 (decision text); promoted report §2 rows "Seed id", "Seed kind", "Commit", "Freeze check" | Q |
| U2 | Recurrence = distance to the best past analog | v3 §4 (CP): "The recurrence distance R is the distance to that analog"; §3 | Q |
| U3 | Observability = how well the hidden state can be recovered from noisy measurements | v3 §1 (physics-based bullet); §5 table (ν²) | P |
| U4 | Instability = how fast small errors grow; the amplifier shared by both forecasters | v3 §3 (amplifier sentence); §5 (Λ̄, Λ̃) | P |
| U5 | Noise sensitivity = movement of the retrieved analog under noise; defined on the analog side | v3 §5 table (N row); §3 (the analog-side sentence); P2 | P |
| U6 | Why these three systems: exact equations, standard systems used by the benchmark literature, differing shape and error-growth rates | v3 §4 (intro and table); v3 §8 ("deliberately narrow"); mapping note `2026-10-23-math-benchmark-mapping.md` M1 (Gilpin 2023, p.2) | A (intent unconfirmed) |
| U7 | The horizon bound of P1 holds under stated conditions | `docs/study/theorem_program_lpc_v1.md` errata addendum (2026-10-21), L7(ii), P1(d); DEC-0040 | Q |
| U8 | What a "supported" does not show: wrong or approximate physics model, real data, higher-dimensional systems, other seeds | v3 §8 (intro; Future work: misspecified physics model, higher-dimensional system, independent trajectory replicates); v3 §4 ("All experiments are simulations"); report §10 ("One realization per system") | A |
| U9 | Chua: Dysts stored maximum exponent differs by a factor of about 2.85 (1.2301 divided by the v3 §4 table value 0.431); our value reproduced by an independent estimator; cause not determined; equations, parameters, time unit, attractor, integration settings excluded; Dysts' spectrum entry near our value; no published Chua reference | `2026-10-23-math-chua-attribution.md` §0, §2, §5 ("Sentence for the research statement"), §6; `2026-10-23-researcher-dysts-tables.md` A.2, A.3; v3 §8 (λ_max for Chua has no published value); report §10 (same item). `2026-10-23-researcher-dysts-lyapunov-script.md` is not on develop (checked at cc27d31), so the cause remains undetermined | Q |
| U10 | Promotion label wording | DEC-0045 item 2; ledger entry 40; results-manifest line of 2026-10-23 | Q |
| U11 | A subsequent pre-registered study | DEC-0045 item 2; ledger seq 36 quote of T10 | P |
| U12 | Six extension systems and their characters | appendix A.2 (system list); `2026-10-23-extension-ensemble-summary.md` (S1 to S6 names); `2026-10-20-math-extension-specs.md` §1 | Q |
| U13 | Only the higher-dimensional Rössler passed the gate; the other five failed V7 and are PROVISIONAL, words shown as stored | appendix A.2 (gate table and "Marked in this part" line); ensemble summary gate table; v3 §6 E0 | Q |
| U14 | The extension's verdict-reporting code is development-only and not owner-reviewed | DEC-0045 item 3; DEC-0038 addendum A1, A2 | Q |
| U15 | Same equations, parameters equal up to rounding (Lorenz-63, Rössler, Chua) | researcher tables note A.1; mapping note M1 | Q |
| U16 | Percentage error depending on signal size; averages over many systems; different time units; no known-equation forecaster | mapping note M5, M9, M15, §5 paragraph; L3 | P |
| U17 | V3 counts validity up to the first error above 0.4 σ_x, against the noisy verifying observation; reported, not gated | mapping note §1 (V3 definition; documentation points (i) and (ii)), F1, F4; v3 §6 ("Horizons", V3 reported) | Q |
| U18 | Appendix A contains the ensemble and extension; the Dysts descriptive table is separate | appendix A section list (A.1, A.2, B); WU-0024.3 | P |

### E. Open items for the owner and the student (only they can supply these)

Owner:

1. Whether the "we chose them because ..." sentence in §5 matches your intent when you chose the systems, or should be recast as a description ("these systems are ...") or replaced by your own reason.
2. Whether you can attest, from your own knowledge, that nobody looked at the confirmatory data before the run; if so, add that sentence to §1 in your name. The records show only the sealed seed and the freeze.
3. Whether the Chua ratio may be quoted as "about 2.85" (value of the DEV-0 and v3 table) or as a number-free "about three times", given that the ensemble value gives a slightly different ratio.
4. Recording the V3 threshold 0.4 in a v3 amendment (mapping note F1) is the owner's decision; until then the text states it as a code constant.
5. Placement of panel 12 (see the poster outline): the fair's rules decide.
6. The final promotion label, if you want other than the DEC-0045 wording.
7. Any statement of owner code review: none is made; the extension code review is still the owner's pending act (DEC-0045 item 3).
8. Names of the roles in §10 as the proposal wants them.
9. For information: the three values 1.97, 3.43 and 2.8 recur in a development note (`2026-10-20-researcher-dysts-extension.md` C.3, `2026-10-20-math-extension-specs.md` line 198) labelled as CP values at "error above 0.2". They equal the sealed run's stored V3 values (report §3, written 2026-10-19 and not promoted until 2026-10-23). The mapping note (F2) says they must not be used but does not notice the match. How the values reached a development note on 2026-10-20 is a question for the main session and the owner (D5: sealed numbers stay with the owner and the student until promotion). Nothing in this statement uses them.

Student:

1. Every `[STUDENT]` slot: §2 why it matters; §5 your reason if different; §7 interpretation and any quoted estimate; §9 why look beyond three systems; §10 next steps, dates, roles and AI-use statement.
2. The whole text in your own voice, one to two pages; read each sentence aloud and rewrite it.
3. Whether the observability gloss in §4 reads right to you.
4. Personal text for the fair submission (name, school, category) if the form asks.
5. The fair's own format and length rules, which only the fair supplies (still open from v1).
