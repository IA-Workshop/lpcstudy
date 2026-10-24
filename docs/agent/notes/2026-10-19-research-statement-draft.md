# Research statement (DRAFT for the student to edit): when should a forecaster trust the past, and when the physics?

Draft by claude-sonnet-5-5, 2026-10-19 (WU-0020.10), for the internal proposal due 2026-10-28. Derived only from `docs/study/proposal_and_methods_v3.md` ("v3"). **This draft contains no number from any run**, only design constants that v3 states. The student writes the interpretation and owns the final text (D8). Every `[STUDENT: ...]` marks words only the student can supply. Each factual sentence carries a tag `{S#}` that points to the trace table at the end (remove the tags in the final text). Sections 1 to 8 are the statement; the glossary follows; the drafting notes and the trace table are for the author and are not part of the submission.

## 1. The research question

Can four measurable local conditions of a chaotic system decide, state by state, how much to trust an analog forecaster (one that copies the past) versus a physics-based forecaster (one that runs known equations), and for how long? {S1} We test this with three pre-registered hypotheses on three simulated chaotic systems, using a sealed fresh random-number seed and rules fixed before the run. {S2}

## 2. Why it matters

A chaotic system is deterministic, but a tiny error in its starting state grows quickly, so every forecast of it eventually fails. {S3} Forecasting such systems matters from sensing to climate. {S4} Analog forecasters find the past situation most like the present and copy what followed; they improve with more data. Physics-based forecasters integrate known equations, but must first estimate the hidden current state from noisy measurements. {S5} Most hybrids combine the two in a fixed way, and we know of no earlier work that decides, state by state, which to trust. {S6} [STUDENT: one sentence, in your words, on why this matters to you or a reader.]

## 3. The two forecasters and the blend weight

Both see only one noisy measurement (the observable) of a three-dimensional chaotic system. {S7}

- **CP (context parroting, the analog forecaster)** takes a delay vector (a short window of recent measurements), finds the nearest one in a library of recorded past data, and copies what followed. {S8}
- **PLP (physics-based latent-state propagation)** estimates the hidden state from the delay vector (a neural-network first guess, then 15 fitting steps against the known equations) and integrates the equations forward. {S9}

The hybrid is w times CP plus (1 minus w) times PLP; the blend weight w, from 0 to 1, is the weight on CP. {S10} The best weight, w\*, gives the least mean squared error (the average squared forecast error). Theorem P1 gives w\* in closed form from the two forecasters' average errors and how they move together. {S11} It also shows blending can extend the forecast horizon (how far ahead a forecast stays accurate) by at most half an error-doubling time. {S12}

## 4. The four local predictability conditions

Each is a property of one state. v3 gives no one-line definitions, so these are assembled from its text (flag F1).

- **Recurrence:** how close the nearest matching past state is to the present one. {S13}
- **Observability:** how well the hidden state can be reconstructed from noisy measurements. {S14}
- **Instability:** how fast small errors grow along the forecast. {S15}
- **Noise sensitivity:** how much the chosen past match moves when noise is added. {S16} Theorem P2 shows the match is stable while the noise is smaller than half the gap between the nearest and second-nearest candidates. {S17}

Recurrence and observability set the two forecasters' starting errors; instability sets how fast both grow. {S18b}

## 5. The three test systems

Lorenz-63, Rössler, and Chua's circuit (an electronic circuit with a piecewise-linear diode) each have exactly known equations, so true hidden states and every condition can be computed. {S18} We observe one variable, x, and score forecasts against the noise-free truth. {S19} Time is counted in Lyapunov times (1 divided by the largest Lyapunov exponent, the long-run growth rate of small errors), set to 30 steps in every system. {S20} [STUDENT: why these three? v3 gives only "exact models"; flag F2.]

## 6. The design in plain words

- **Pre-registered hypotheses.** Hypotheses, statistics and decision rules were fixed before the confirmatory run. {S21} The three primary ones: (H2a) given the starting errors, the best weight does not depend on horizon or instability; (H2b) it rises with noise level and library size; (H3c) a few regimes (groups of similar states) lose almost nothing against the closed-form rule. {S22} Nine secondary hypotheses and one estimate are also pre-registered. {S23}
- **Sealed fresh seed.** The confirmatory run uses a sealed random-number seed: new noise, libraries and trajectories on the same three systems. {S24}
- **Intervals.** Each statistic has a confidence interval (a range of plausible values) from a moving-block bootstrap (resampling blocks of 5 neighboring test states, 2000 times). {S25} Primaries use level 1 − 0.05/3, stricter because there are three; the rest use 95%. {S26}
- **Verdict rule.** Per system, a hypothesis passes if its interval lies inside the pre-set band (acceptable range) or wholly on the predicted side of a bound, fails if wholly outside, and is otherwise inconclusive. {S27} The overall verdict is "supported" only if all three systems pass, "not supported" if at least one fails, and "inconclusive" otherwise (flag F3). {S28}
- **Validity gates.** Seven checks (V1 to V7) confirm the numerical tools first. A failure marks that system's results provisional, is reported to the owner, and is never repaired by retuning or rerunning. {S29}
- **Cross-checks.** The official run is on a CPU; a GPU run is an information-only cross-check, and another person regenerates the official run. {S30}
- **All outcomes are reported,** failures included. {S31}

## 7. What is claimed and what is not

"Supported" would mean: on these three systems, with an exact physics model and one measured variable, the pre-registered predictions held. It would not show the same for real data, a wrong physics model, or higher-dimensional systems, which v3 lists as future work (flag F9). {S32} "Not supported" means at least one system failed a pre-set test. It is not "disproved": its error is not controlled the same way and, with 95% intervals, can reach about 7.3% over three systems. {S33} "Inconclusive" is not "no effect". Limits v3 states in advance:

- Three low-dimensional systems, one observable, one main trajectory per system. {S34}
- Same systems with fresh random numbers: more precision, not new systems. {S35}
- In the pilot, PLP usually won after one Lyapunov time with an exact model, and practical (non-exact) features carried little of the needed information, so allocation results are limited by them, not by theory. {S36}
- H2e (correlated errors as the library grows) was added after the pilot showed the effect. {S37}
- H3a cannot fail, and H2a's second part can be refuted but essentially cannot pass. {S38}
- The intervals cover slightly less often than their nominal level. {S39}

[STUDENT: your reading of what this means and what surprised you, marked as interpretation.]

## 8. Status and timeline

The plan: freeze the pre-registration, run the full study once on the sealed seed, regenerate it on another machine, then analyze and write up. {S40} [RESULTS: from the preliminary findings document, after promotion] [STUDENT: current status and the dates you commit to; flag F4.] Deem leads the questions, proofs of P1 and P2, interpretation and presentation; Brian reviews and runs the computation; an AI assistant (Claude) helped with drafting, reference checks and code, and the author reviewed it. {S41} [STUDENT: confirm roles and the AI-use statement.]

## Glossary

| Term | Plain meaning (v3 section) |
| --- | --- |
| Chaotic system | A deterministic system whose forecasts get worse fast because tiny starting errors grow (§1). |
| Lyapunov exponent, Lyapunov time | The long-run growth rate of small errors; its inverse, 1 Lyapunov time, is our unit of time, 30 steps (§4). |
| Observable | The one measured quantity we get to see, here the variable x with noise added (§4). |
| Delay vector | A short window of recent measurements stacked into one point (§4). |
| Analog forecast (CP) | Find the most similar past delay vector and copy what followed (§1, §4). |
| PLP | Estimate the hidden state, then integrate the known equations forward (§4). |
| Mean squared error | The average of the squared forecast errors (§3). |
| Blend weight w\* | The weight on CP, between 0 and 1, that gives the least mean squared error at a state (§3, §5). |
| Forecast horizon | How far ahead a forecast stays within a chosen error (§6). |
| Theorem (P1, P2) | A statement proved from assumptions; P1 gives w\* and the limit on blending, P2 explains noise sensitivity (§3). |
| Pre-registration | Writing the hypotheses and decision rules down before the data are produced (§7, §9). |
| Random-number seed vs. "seed" of an error | The sealed seed fixes the computer's random numbers (§9). In v3 the "seeds" of the forecasters are their starting errors (§3). |
| Confidence interval, moving-block bootstrap | A range of plausible values, found by resampling blocks of neighboring test states (§7). |
| Band, verdict | The pre-set pass range; the result "supported", "not supported" or "inconclusive" (§7). |
| Validation gate | Seven numerical checks that must pass before a system's results are trusted (§6). |
| Cross-check | An information-only repeat on a GPU to see whether it agrees (§9). |

## Drafting notes for the student (not part of the statement)

### Places that need your own words

1. §2: why the question matters to you.
2. §5: why these three systems (v3 gives no reason beyond "exact models").
3. §7: your interpretation and what surprised you, marked as interpretation.
4. §8: current status and the dates you commit to.
5. §8: the confirmed roles and the AI-use statement in your words.
6. §8: `[RESULTS: from the preliminary findings document, after promotion]`. Nothing goes here until the owner records the promotion (QA.11).
7. Whole text: read every sentence aloud and rewrite it in your voice; check the length (one to two pages).

### Points where v3 is ambiguous or silent (quoted, not resolved)

- **F1. The four conditions have no one-line definitions in v3.** The Summary only names them: "recurrence, observability, instability and noise sensitivity". The sentences in section 4 are assembled from: §3 "Recurrence and observability set the seeds; instability sets the amplifier", §4 "The recurrence distance R is the distance to that analog", §1 "[Physics-based forecasters'] accuracy depends on how well that state can be reconstructed", §5 (ν², Λ̃, N) and P2(c). The pairing of recurrence with the analog starting error and observability with the physics starting error is read from §3's sentence and the order of the profile in §5 ("recurrence, observability, instability and noise sensitivity", F̂ = (ln ε̂/ρ, ln δ̂/ρ, Λ̃̂, ln(N̂ + 0.01))). The owner or student should confirm these four sentences.
- **F2. Why these three systems.** v3 §4: "All experiments are simulations of three chaotic systems with exact models, so true states and every condition are known." No further reason (for example dimension, shape, or time scale) is given, so none is written. §8 calls the choice "deliberately narrow".
- **F3. What the "Overall verdict" covers.** v3 §7: "**supported:** pass on all three systems; **not supported:** fail on at least one system; **inconclusive:** otherwise, including when a system has no result." It sits after "A criterion with several parts passes only if every part passes", and v3 never says whether the overall verdict is per hypothesis (H2a, H2b and H3c each get one) or one verdict for the study. The draft says only "the overall verdict" and does not say which. The user's wording ("supported only if all three systems pass") matches v3. The owner should say which reading is intended before the final text.
- **F4. Status and dates.** v3 §9: "The proposal and methods are due on Oct 30, 2026", and the steps freeze, run, regenerate, analyze are listed "**After 30 October** (dates to be set)". The internal proposal is due 2026-10-28 (WU-0020 amendment), and the repository history already records freeze entries, so v3's timeline is behind the facts. The draft states only the v3 sequence and leaves the current status to the student. Also, v3 §9 numbers two items "4." (the regeneration and the analysis), so "§9 item 4", which §8 cites for the regeneration, could be read as either.
- **F5. "Never seen" data.** The task asks to say the confirmatory data were never seen. v3 says the run uses "a sealed fresh seed" (§9 item 3) and that the rules "are fixed before the confirmatory run" (§7), but does not state in those words that nobody viewed the data. The draft uses only the v3 wording. The student may add the plain-language claim if the owner confirms it from the governance records.
- **F6. "18 primary parts".** v3 §8 and §9 say 18 primary parts but §2 never lists them. Counting gives six parts (H2a(i), H2a(ii) with the indicator of w\* = 0, H2a(ii) with logit w\*, H2b(i), H2b(ii), H3c) times three systems; v3 adds a third H2a(ii) part only "if w\* = 1 exceeds 5% of states". The draft does not use the number 18 in the text for this reason.
- **F7. Terminology clash.** v3 uses "seed" for the sealed random-number seed (§9) and for each forecaster's starting error (§3). The draft says "starting error" and glosses "seed" in the glossary.
- **F8. Pilot figures left out.** Section 7 of this draft restates pilot-based limitations from v3 §8 in words only. v3 gives numbers for them; they are left out on purpose (no development-run values).
- **F9. What a pass would not show.** v3 does not state what a "supported" verdict would not show. The sentence in section 7 is an inference from §8 ("three low-dimensional systems, an exact physics model, one observable") and §8's future-work list. The owner should confirm it.

## Trace table: statement -> v3 section

Kind: Q = near-quote of v3; P = paraphrase; A = assembled from several places or an inference (see the flag).

| Tag | Statement | v3 section | Kind |
| --- | --- | --- | --- |
| S1 | The question: can four local conditions decide, state by state, how much to trust an analog versus a physics-based forecaster, and for how long | Summary | Q |
| S2 | Three pre-registered primary hypotheses on three systems; sealed fresh seed; rules fixed before the run | Summary; §7 (intro); §9 item 3 | P (F5) |
| S3 | Chaotic systems are deterministic; sensitive dependence makes every forecast deteriorate | §1 | Q |
| S4 | Forecasting matters from sensing to climate | §1 | Q |
| S5 | Analog and physics-based forecasters have opposite weaknesses; their accuracy depends on the nearest analog and on state reconstruction | §1 (two bullets) | P |
| S6 | Hybrids are mostly fixed combinations; no known prior state-dependent allocation | §1 ("Hybrids", "Gap and contribution", last paragraph) | P |
| S7 | Both see only a noisy scalar observable of a three-dimensional chaotic system | Summary; §4 | Q |
| S8 | CP: delay vector, nearest library vector by exact search, copies its noisy future | Summary; §4 (CP) | P |
| S9 | PLP: network first guess, 15 Levenberg-Marquardt iterations, integrate known model forward | Summary; §4 (PLP) | P |
| S10 | Hybrid = w CP + (1 - w) PLP, w in [0, 1], w is the weight on CP | Summary; §4 (Hybrid) | Q |
| S11 | w\* is the mean-squared-error-optimal weight, a closed form of the error moments (P1) | Summary; §3 P1; §5 (oracle table) | P |
| S12 | Blending can extend the horizon by at most half an error-doubling time | Summary; §3 P1(d) | Q |
| S13 | Recurrence: closeness of the nearest past analog (recurrence distance R) | §3; §4 (CP); §5 (proxies, profile) | A (F1) |
| S14 | Observability: how well the hidden state can be reconstructed | §1; §5 (ν) | A (F1) |
| S15 | Instability: growth of errors through the amplifier, rate Λ̄ | §3; §5 (g_H, Λ̄, Λ̃) | A (F1) |
| S16 | Noise sensitivity N: displacement of the retrieved analog under noise | §3 P2(c); §5 | A (F1) |
| S17 | P2: nearest analog does not change if noise is below half the margin | Summary; §3 P2(a) | Q |
| S18 | Three systems with exact models, so true states and every condition are known; Lorenz-63, Rössler, Chua (piecewise-linear diode) | §4 (intro and table) | Q |
| S18b | Recurrence and observability set the seeds; instability sets the amplifier | §3 | Q |
| S19 | Observable x in each; errors measured against the noise-free truth | §4 (table; Hybrid) | P |
| S20 | LT = 1/λ_max, set to 30 steps for each system | §4 (Integration and time scale) | Q |
| S21 | Rules are fixed before the confirmatory run | §7 (intro) | Q |
| S22 | Primary hypotheses H2a, H2b, H3c in one line each | Summary; §2 (RQ2 and RQ3 tables) | P |
| S23 | Nine secondary hypotheses and one pre-registered estimate (Q-N) | §2 (intro) | Q |
| S24 | New noise, libraries and trajectories on the same three systems | §8 (Same attractors, fresh seeds); §9 item 3 | P |
| S25 | Moving-block bootstrap percentile intervals; blocks of 5; 2000 resamples | §7 (Intervals) | Q |
| S26 | Primaries at level 1 - 0.05/3 (Bonferroni); everything else 95% | §7 (Intervals) | Q |
| S27 | Pass if interval inside the band or entirely on the predicted side; fail if entirely outside; inconclusive otherwise | §7 (Verdict per system) | Q |
| S28 | Overall: supported if pass on all three systems; not supported if fail on at least one; inconclusive otherwise | §7 (Overall verdict) | Q (F3) |
| S29 | E0 gate with V1 to V7; failure marks results provisional, is reported, referred to the owner, never repaired by retuning or rerunning; examples V1 and V7 | §6 (E0, V1, V7) | P |
| S30 | CPU official run; GPU cross-check only; another actor regenerates | §9 items 3 and 4 | P (F4) |
| S31 | All outcomes are reported, including failures | §7 (last line) | Q |
| S32 | Narrow scope: three low-dimensional systems, exact model, one observable; future work lists misspecified model, higher-dimensional system | §8 (intro; Future work) | A (F9) |
| S33 | Error of "not supported" is not controlled; with 95% intervals it can reach about 7.3% over three systems | §7 (Overall verdict) | Q |
| S34 | Three low-dimensional systems, one observable, one main trajectory per system (statistics, main and separate trajectories are drawn per system); independent trajectory replicates listed as future work | §8 (intro; Future work); §4 (Trajectories) | P |
| S35 | Same attractors, fresh seeds: adds precision, not new systems | §8 (Same attractors, fresh seeds) | Q |
| S36 | Pilot: with an exact model PLP usually wins after 1 LT; deployable features carry little of the exact information; limited by the proxies, not the theory (numbers omitted on purpose) | §8 (first three limitations) | P (F8) |
| S37 | H2e added after the pilot showed the effect; tested on fresh seeds | §2 (last paragraph) | Q |
| S38 | H3a cannot fail; H2a's second part can be refuted but essentially cannot pass | §2 (H3a row); §7 (Precision) | Q |
| S39 | Block-5 intervals undercover slightly; PLP iterative error flagged for some parts | §8 (Interval coverage; Iterative error of PLP) | P |
| S40 | Planned sequence: freeze, one full run on the sealed seed, CPU regeneration, analysis and write-up; design date Oct 10, 2026 | §9 items 2 to 4; title block | P (F4) |
| S41 | Roles (Deem, Brian, AI assistant) and the AI-use statement, "to be confirmed" | §9 (Roles; AI-use statement) | P |
| G1 | Glossary entries: chaotic system, Lyapunov time, observable, delay vector, CP, PLP, MSE, w\*, horizon, theorems, pre-registration, seed, interval and bootstrap, band and verdict, gate, cross-check | §1, §3, §4, §5, §6, §7, §9 as cited in each row | P |
