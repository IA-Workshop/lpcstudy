# Poster outline, 10-slide variant, highlights and checklists (WU-0020.5)

Author claude-sonnet-5-5, 2026-10-19, for the student (Deem), from the WU-0020 plan note sections 1, 2, 6 and 7. Documents only. This file contains no number from any run. A bracket such as `[F1]` or `[verdict: from results.json]` is a slot to fill from the released file. The student writes all poster and slide prose and the interpretation (D8). This file gives the structure, the questions each panel must answer, and the terms to define.

## 0. Status and release rule (read first)

- **No sealed number goes on a poster, slide or handout before promotion (WU-0018.3)**, unless the owner records a ruling. QA.11: reporting an unpromoted result beyond its author is a blocking defect. Preliminary results stay internal to the owner and the student (owner ruling of 2026-10-19; D5).
- Until then the poster may show the question, the two forecasters, the four conditions, the three systems, the method, the pre-registration, the limits and next steps, and the figure panels marked "results under verification" with no data in them.
- **Development-ensemble or DEV numbers** (D4) appear only in a labeled appendix panel or appendix slide, titled "Development context: not a hypothesis test", as text, never on F1 or F2. There is no new DEV ensemble before the fair.
- Every statement of a result that is not yet promoted carries the header: `CONFIRMATORY: UNPROMOTED` and `PRELIMINARY: internal to the owner and the student until promotion`. After promotion the header is replaced by the promotion label the owner records.
- Open question for the fair (researcher, not answered here): date, rules on preliminary or unverified results, AI-use disclosure, poster size limits.

## 1. Figures (slots)

| Slot | Content | Source | Status |
| --- | --- | --- | --- |
| F1 | Primary forest plot: 18 parts (H2a(i), H2a(ii) zero, H2a(ii) interior, H2b(i), H2b(ii), H3c, each on Lorenz-63, Rössler, Chua), estimate with its interval at the level stored in the leaf, shaded pass band, verdict by marker shape and text | `tools/findings_build.py` (to be built, WU-0020.2) from the official CPU `results.json` | missing until .2 |
| F2 | Secondary forest plot: H1a to H1d, H2c, H2d, H2e, H3b with intervals; Q-N shown against its reading table, not as pass/fail | same tool | missing until .2 |
| F3 | CPU versus GPU cross-check: z per primary part with the tolerance line, titled "cross-check, information only", in grey | same tool, from `compare_runs` text and the GPU file | missing until .2 |
| F4 | The four existing report figures from `lpcstudy.report.make_figures`: `separation_weight_vs_horizon.png` (E4, H2a context: median and IQR of w\* against horizon), `kaplan_meier_by_rule.png` (E4/E5, H2c and H3a context: realized-horizon curves per rule), `regret_vs_regimes.png` (E5, H3c context: regret against number of regimes K, 5% line), `knob_response_library.png` (E2, H2b(ii) context: w\* against library size per noise level) | `lpcstudy.report.make_figures`; captions from `budget.FIGURE_CAPTIONS` | exist; they say "no confidence interval is shown", so they are context, never verdicts |
| S1 | Schematic of CP, PLP, the four conditions and w\* | hand-drawn by the student; no data | to draw |

Note: the plan note lists "F4" both as the schematic and (in this task) as the existing report figures. This file uses **F4 = the four existing report figures** and **S1 = the schematic**, so each slot has one meaning. Flag to the owner if the plan should be changed to match.

Figure rules: intervals always drawn, level written in the panel; one message per figure; Okabe-Ito palette plus marker shape and text for the verdict; each caption names the experiment (E1 to E6), the v3 identifier and the interval procedure; `PROVISIONAL` in the title of any system that failed the gate.

## 2. Tri-fold poster outline

Layout: three folds, left to right, reading order top to bottom within a fold. Panel titles are questions, in plain language for judges at the early-undergraduate level. Each panel lists what it must answer and its figure slot. The student writes the text.

### Left fold

**Panel 1. The question.** Slot: S1 (small) or a photo or sketch of a chaotic trajectory.
Must answer: What is predictability, and why does a chaotic system limit it? What exactly do we ask? (Can four measurable local conditions decide, state by state, how much to trust an analog forecaster against a physics-based one, and for how long?) Why does anyone care? What is new (v3 §1: no prior state-dependent blend under partial observation)?
Terms: chaos, Lyapunov time, forecast horizon.

**Panel 2. Two ways to forecast.** Slot: S1.
Must answer: What does CP do (copies the future of the nearest past pattern in a library)? What does PLP do (estimates the hidden state, then integrates the known equations)? Why can each one fail (CP: few or noisy neighbors; PLP: state error grows)? Both see only one noisy measurement of a three-dimensional system: say why that matters.
Terms: analog forecast, delay vector, library size, state estimate, noise level, observable.

**Panel 3. Four conditions and a blend weight.** Slot: S1 (conditions around the weight).
Must answer: What are the four local conditions (recurrence, observability, instability, noise sensitivity), each in one everyday sentence? What is the blend weight w\* (weight on CP, between 0 and 1) and what is "optimal" (least mean squared error)? What was proved (P1: closed-form optimal weight; blending can extend the horizon by at most half an error-doubling time; P2: retrieval of the nearest analog is stable while noise is below half the neighbor margin)? Say which part is theorem and which is tested.
Terms: mean squared error, blend, theorem, w\*, noise sensitivity.

### Centre fold

**Panel 4. Three test systems.** Slot: a small picture of each attractor (hand-drawn or generated outside the sealed data).
Must answer: Why Lorenz-63, Rössler and Chua's circuit? What do they share and where do they differ? Why one realization per system (limit; v3 §8)?
Terms: attractor, dimension, Chua circuit.

**Panel 5. How the test works.** Slot: none, or a timeline strip.
Must answer: What does pre-registered mean and why does it protect against fooling ourselves? What is the sealed seed (random numbers whose results nobody looked at until the rules were fixed)? What are the three primary hypotheses in one line each (H2a: the weight depends on the error seeds, not on horizon or instability; H2b: noise level and library size move the weight the predicted way; H3c: a few regimes lose almost nothing against the closed form)? What does a verdict mean: **"supported" only if all three systems pass**; "not supported" if any system fails; "inconclusive" otherwise, including a system with no result. State that the error of "not supported" is not controlled the same way (v3 §7). What does an interval tell you, and what is the band?
Terms: pre-registration, hypothesis, seed (random number seed), confidence interval, bootstrap, band, verdict.

**Panel 6. What we found (primary).** Slot: **[F1]**. Header banner required. Before promotion: "results under verification", no data.
Must answer: For each of the three primaries and three systems, where is the interval relative to the band? Which verdict does the pre-registered rule give: [verdict: from results.json]? Is any system marked PROVISIONAL (gate failure)? Say it in the file's words, not new words. One message only.
Terms: forest plot, interval, PROVISIONAL, gate.

**Panel 7. Highlights (secondary).** Slot: **[F2]** and one of **[F4]** (see section 3 for the fixed list).
Must answer: What do the four pre-fixed highlights say, each read with its interval and its verdict or table reading? Remind the judge that these are secondary and not the main test.
Terms: secondary hypothesis, Kaplan-Meier curve, log-rank test, noise matching.

### Right fold

**Panel 8. What it means, and what it does not.** Slot: none (student text; the section 11 prompt sheet in the preliminary document).
Must answer (questions only): What does the verdict allow us to say about the four conditions? What does it not say (no claim beyond the three pre-registered systems, an exact physics model, one observable, one realization per system)? What would a "not supported" or "inconclusive" mean, and why is it not "no effect" or "disproved"? What surprised you, stated as your own reading and marked as interpretation?
Language: no "proves", "confirms", "significant", "shows that", "demonstrates", "breakthrough" in the result statements.

**Panel 9. Limits.** Slot: none. Short list from v3 §8 and the plan note §2.6: exact model, 3 systems, one realization each; proxies carry little of the exact information (deployable allocation is limited by proxies, not theory); block-bootstrap intervals undercover slightly; iterative error of PLP flagged for some parts; H3a cannot fail and small regimes; the gain bound is reported only; the block-sensitive label is not computable for the sealed run; bitwise CPU/GPU agreement at full size is extrapolated.
Must answer: Which of these would change a conclusion if it went the other way?
Terms: undercoverage, proxy, iterative error.

**Panel 10. Cross-check and checks.** Slot: **[F3]**, grey, "information only". Optional appendix box: "Development context: not a hypothesis test" (D4).
Must answer: Why run it on a second computer (GPU)? What does it show (z per part against the tolerance line) and what does it not (it changes no verdict, DEC-0031)? If any part disagrees, say so here only.
Terms: z score, cross-check, reproducibility.

**Panel 11. What next, and thanks.** Slot: none.
Must answer: What is future work (v3 §8: misspecified physics model, higher-dimensional system, independent trajectory replicates, deployable noise-sensitivity estimate, break-even library size, Lean-checked theorems)? Who helped? AI-use statement (v3 §9, updated by the student). Contact and QR to the repository, if allowed after promotion.

## 3. Poster highlights, fixed BEFORE release (D10)

These are chosen now, before any sealed output exists, so nobody picks results after seeing them. They are shown whatever they say, with intervals and verdicts, favourable or not.

| Group | Items | Why fixed |
| --- | --- | --- |
| Primary (all shown, F1) | all 18 parts: H2a(i), H2a(ii) zero, H2a(ii) interior, H2b(i), H2b(ii), H3c, on each system | pre-registered primaries; none omitted |
| Secondary highlights (D10) | **H2c** (closed-form allocator against a global weight and the better single forecaster), **H2e** (noise matching: error correlation as the library grows), **H3a** (regimes separate horizons; with events and censored states per regime), **Q-N** (what noise sensitivity adds; shown as its reading from the v3 §7 table, never pass/fail) | one from each research question except RQ1, whose reading is Q-N; fixed in D10 |
| Other secondaries | H1a to H1d, H2d, H3b, gain bound | appear in F2 and the preliminary document; not highlighted; the gain bound only as "reported, v1 statistic, v3 screen pending" |

Rules: no substitution after release; if a highlight is inconclusive or not supported, it is shown with that word. Any additional highlight needs an owner ruling recorded before release.

## 4. Ten-slide variant (same figures)

| # | Slide | Content slot | Figure |
| --- | --- | --- | --- |
| 1 | The question | panel 1 questions; title, names, banner | S1 (small) |
| 2 | The two forecasters | CP and PLP, panel 2 questions | S1 |
| 3 | The four conditions and w\* | panel 3 questions; what is proved | S1 |
| 4 | The three systems | panel 4 questions | attractor pictures |
| 5 | Pre-registration, sealed seed, verdict rule | panel 5 questions; "supported" only if all three systems pass | timeline strip (optional) |
| 6 | Primary verdicts | panel 6; [verdict: from results.json]; PROVISIONAL if any | **[F1]** |
| 7 | Secondary highlights (H2c, H2e, H3a, Q-N) | panel 7 | **[F2]**, plus one of [F4] if needed |
| 8 | What it means, and does not mean | panel 8 (student) | none |
| 9 | Limits and the CPU/GPU cross-check | panel 9 and 10; "information only" | **[F3]** |
| 10 | What next, thanks, AI-use statement | panel 11 | none |
| Appendix (hidden unless asked) | Context figures; development context (labeled, D4) | existing four report figures | **[F4]** |

Presenting rules: one message per slide; read the interval before the verdict; do not say "significant"; speak the header on any results slide until promotion.

## 5. Figure and table checklist, with sources

Sources are leaves of the official CPU `results.json` (CONF-1) unless stated. Leaf paths are written as the `{{source:path}}` placeholders of the plan note section 3; the tool column is the producer. "TBD" means the tool is not built yet (WU-0020.2).

| Item | Shows | Source (results.json leaf or file) | Tool | Used in |
| --- | --- | --- | --- | --- |
| F1 | 18 primary parts: estimate, interval at the stored level (1 − 0.05/3), band, verdict | `systems/<s>/<H2a,H2b,H3c>/...` parts as listed in `compare_runs.TD_PARTS` (point and interval leaves); `verdict` leaf of each part | `findings_build.py` (TBD) | panel 6, slide 6 |
| F2 | Secondary parts with 95% intervals; Q-N reading | `systems/<s>/<H1a..H1d, H2c, H2d, H2e, H3b>` leaves; `systems/<s>/Q-N` | `findings_build.py` (TBD) | panel 7, slide 7 |
| F3 | z_away per primary part, tolerance line, "information only" | GPU `results.json` and `compare_runs` TD text (`docs/study/conf1_cpu_vs_gpu_td.txt`) | `tools/compare_runs.py`, `findings_build.py` (TBD) | panel 10, slide 9 |
| F4a | w\* median and IQR against horizon | `systems/<s>/weight_profile` | `lpcstudy.report.make_figures` | appendix, panel 7 option |
| F4b | Kaplan-Meier curves per rule | `systems/<s>/km_curves` | `make_figures` | panel 7 (H2c, H3a context) |
| F4c | Regret ratio against K | `systems/<s>/regime_curve/regret_ratio_by_K` | `make_figures` | appendix (H3c context) |
| F4d | w\* against library size per noise level | `systems/<s>/` knob-response leaves (see `make_figures`) | `make_figures` | appendix (H2b(ii) context) |
| S1 | Schematic | none | student, by hand | panels 2, 3 |
| T1 | Overall verdict table, 14 rows (H1a to H3c, Q-N, gain bound) | `verdicts.<id>.by_system`, `verdicts.<id>.verdict`; interval labels from `RESULTS.md` | `findings_build.py` (TBD); `report.write_markdown` | preliminary document section 4; poster verdict box |
| T2 | 18-part table (estimate, interval, level, band, verdict) | part leaves as in F1 | `findings_build.py` (TBD) | document section 5 |
| T3 | Validation gate V1, V2, V4 to V7 per system with statistic | `gate` leaves, `gate_pass` per system | `findings_build.py` (TBD) | document section 3; PROVISIONAL flag on F1 |
| T4 | H3a events and censored states per regime | H3a leaves ("not recorded" if absent) | `findings_build.py` (TBD) | panel 7 |
| T5 | Handling counters and `failed_variants` (zeros printed as 0) | `handling.totals`, `handling` per system | `findings_build.py` (TBD) | document section 7 |
| T6 | Provenance: commit, seed_id, backend, threads, dirty, complete, SHA-256 of each results file, release ledger sequence | `provenance` leaves, git, WU-0015.3 manifest | `findings_build.py` (TBD) | document section 2 |
| T7 | Cross-check summary: z per part, count of differing verdict-type leaves, GPU gate | `compare_runs` text, GPU file | `tools/compare_runs.py` | panel 10 |
| T8 | Limitations list (v3 §8 items plus DEF-0018, DEF-0020, DEF-0026, DEF-0027, DEC-0033 M2 and M3, one realization per system, block-sensitive label status) | design constants and v3 §8 | hand, checked by the tool keyword list | panel 9 |

Every item above is read from the released file by the tool or `make_figures`. Nobody retypes a number.

## 6. Honesty checklist (tick every item before anything leaves the owner and the student)

- [ ] Promotion (WU-0018.3) exists in the ledger, or the owner has recorded a ruling that allows the display. Otherwise no sealed number appears.
- [ ] Every result statement carries the header (`CONFIRMATORY: UNPROMOTED`, or the promotion label).
- [ ] Every estimate is shown with its interval, at the stored level; no point alone.
- [ ] The band is drawn and its strict or closed form is stated.
- [ ] The only verdict language is the pre-registered rule: "supported" only if all three systems pass; "not supported"; "inconclusive". "Supported" carries "(preliminary, unpromoted)" until promotion.
- [ ] No "proves", "confirms", "significant", "shows that", "demonstrates", "breakthrough" in result text.
- [ ] "Inconclusive" is never written as "no effect"; "not supported" is never written as "disproved".
- [ ] The sentence on the uncontrolled error of "not supported" (v3 §7) is present.
- [ ] H3a is described as unable to fail; Q-N as a reading; the gain bound as "reported, v1 statistic, v3 screen pending".
- [ ] Any system that failed the gate carries PROVISIONAL in every panel and table; a boxed line says the result was referred to the owner.
- [ ] The GPU cross-check is shown only in F3 and its panel, in grey, titled "information only", and says "changes no verdict".
- [ ] Any development ensemble or DEV number is only in the labeled appendix, as text, never on F1 or F2.
- [ ] The highlights are exactly the list in section 3, whatever they show.
- [ ] Handling counters are stated, zeros as 0.
- [ ] Limitations panel lists every item of section 2 above.
- [ ] Interpretation is the student's own and is marked as interpretation; the AI-use statement is updated.
- [ ] Figures use the Okabe-Ito palette and also distinguish verdicts by marker shape and text; text and markers are legible when printed in grey.
- [ ] No figure or caption mentions removed experiments (shift, transfer, Lorenz-96, A4f).
- [ ] Every caption names the experiment (E1 to E6), the v3 identifier and the interval procedure (moving-block bootstrap, blocks of 5, B = 2000, level).
- [ ] Every number on the poster has a row in the trace file (`.trace.csv`), and `findings_build.py check` exits 0 on the document it came from.

## 7. Glossary of terms for the student to define in plain words

chaos; Lyapunov time (1 Lyapunov time = 30 steps); forecast horizon; analog forecast (CP); delay vector; library size N_lib; physics-based forecast (PLP); state estimate; observable; noise level ρ (fraction of σ_x); recurrence, observability, instability, noise sensitivity; blend weight w\*; mean squared error; theorem; pre-registration; seed; sealed seed; hypothesis; primary and secondary; confidence interval; moving-block bootstrap; band (pass region); verdict; intersection-union rule; forest plot; Kaplan-Meier curve; log-rank test; regime; regret; gate (validation checks V1 to V7); PROVISIONAL; CPU/GPU cross-check and z score; promotion.

## 8. Open questions for the student and owner

1. The fair's date, its rules on unverified results, its AI-use disclosure and poster size limits (researcher); decides whether the poster waits for promotion (D5).
2. Naming: the plan note calls the schematic "F4"; this file uses F4 for the existing report figures and S1 for the schematic. Confirm.
3. Is Panel 4 allowed attractor pictures drawn from development data? (They carry no results, but owner to confirm.)
4. The panel count (11) fits a tri-fold with three or four per fold; merge panels 10 and 11 if space is short.
5. Do you want the optional noise-knob panel for H2b(i) (medians, labeled "no interval")?
