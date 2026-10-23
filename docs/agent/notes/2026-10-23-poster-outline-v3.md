# Poster outline v3, 10-slide variant, appendix handout and checklists (final draft for the owner and the student to edit)

Draft by claude-sonnet-5-5 (WU-0025.4), 2026-10-23, from `2026-10-23-poster-outline-v2.md`, `2026-10-19-prelim-poster-outline.md` ("v1") and DEC-0045, for the internal proposal due 2026-10-28. The student (Deem Albaty) writes all poster and slide prose and the interpretation (D8). This file gives structure, sources and rules. **It contains no number from any run.** Result words come from section 4 of the promoted report only (`promoted/CONF-1/report.md`, lines 91 to 125, checked on develop at cc27d31); numbers reach the poster only through the figures and tables built from the promoted copy, and the development numbers only through the standalone appendix A.

Sections and panels not listed here are unchanged from v1 (panels 1, 2 and 11 except where stated below, the glossary of v1 §7).

## What changed from v2

| Where | v2 | v3 | Why |
| --- | --- | --- | --- |
| Promotion label | "[OWNER: label; proposed ...]" | fixed: "Confirmatory result, seed CONF-1, promoted by the owner on 2026-10-23". The stored row "Label: CONFIRMATORY: UNPROMOTED" in §2 of the promoted report is never copied | DEC-0045 item 2 |
| Appendix A | `...appendix-a-development.md`, "not yet present" | the standalone document `docs/agent/notes/2026-10-23-appendix-a-standalone.md` (built by `tools/findings_build.py appendix`; 1073 traced values) holds A.1 (ensemble) and A.2 (six extension systems, S1 to S6) | DEC-0045 item 1 |
| PROVISIONAL | "No system is PROVISIONAL" | said of the three studied systems only. In appendix A.2, S2 to S6 are PROVISIONAL (stored gate V7 false); only S1 (`rossler_hyper`) passes. v2 had no sentence that counted two; the wording is made exact | DEC-0045 item 2; appendix A.2 |
| Panel 12 | placement open; open question 2 | on a handout or the back of the board, apart from panels 6, 7 and 10, text and tables only, no figure | DEC-0045 item 2 |
| Panel 12 code status | open question 4 | panel 12 states: the extension's verdict-reporting code is development-only and not owner-reviewed | DEC-0045 item 3 |
| Appendix and the sealed values | open question 3 | appendix A reprints no sealed value; the pointer to "section 5 of the promoted report" is in panel 12's own text (the built appendix contains no such pointer and no sealed value) | DEC-0045 item 2; grep of appendix A for the sealed primary estimates: 0 hits |
| Panels 3, 4, 5 | v1 text | panel 3: four one-line definitions (F1 resolved); panel 4: reason for the three systems (F2 resolved); panel 5: "sealed" described by what the records show (F5 resolved) | v3 §3 to §5; DEC-0001 |
| Panel 8 | prompt only | adds the recommended wording of what a pass does not show (F9 resolved) | v3 §8 |
| Panel 12 (D3) | Dysts one-liner | incorporates the Dysts tables note, the benchmark mapping and the Chua attribution; V3 always quoted with theta = 0.4 sigma_x and against the noisy verifying observation | `2026-10-23-researcher-dysts-tables.md`; `2026-10-23-math-benchmark-mapping.md` §1, F1, F4; `2026-10-23-math-chua-attribution.md` §5 |
| "later study", "v4" | "a later study" | "a subsequent pre-registered study" | DEC-0045 item 2 |

## 0. Status and release rule (replaces v1 §0 and v2 §0)

- **The CONF-1 result is promoted** (ledger entry 40, 2026-10-23; manifest line of the same date). Sealed results may appear on the poster and slides.
- **Source of every sealed item: `promoted/CONF-1/` only** (on develop): `report.md`, `report.figures/` (F1 to F3 with the promoted title), `figures/` (the four RESULTS.md figures, R1 to R4), `RESULTS.md`, `results.json`. Never the figures in `docs/agent/notes/2026-10-20-prelim-findings-conf1.figures/`: they carry the unpromoted title.
- **Header on every result panel and slide:** **Confirmatory result, seed CONF-1, promoted by the owner on 2026-10-23.**
- **Development material** (the ensemble DEV-1, DEV-3, DEV-4; the six extension systems; the Dysts descriptive table) appears only in panel 12 and appendix slides A1 to A4, titled `Development context: not a hypothesis test`, never on or beside F1, F2 or F3, and only after review WU-0025.6. Its numbers come only from appendix A (standalone) and the reviewed Dysts table.

## 1. Figures (changes to v1 §1)

| Slot | Source now | Notes |
| --- | --- | --- |
| F1, F2, F3 | `promoted/CONF-1/report.figures/` | title "FINDINGS FOR SEED CONF-1 / Result promoted by the owner"; otherwise pixel-equal to the checked figures (DEC-0043) |
| R1 to R4 | `promoted/CONF-1/figures/` | captions written from the figure map (`2026-10-21-promotion-figure-map.md`), naming experiment and identifier: R1 separation_weight_vs_horizon E4, H2a; R2 kaplan_meier_by_rule E4, the rules behind H2c, H2d, H3c, no verdict; R3 regret_vs_regimes E5, H3c; R4 knob_response_library E1 and E2, H2b. Each caption says "no interval shown; context, not a verdict". R3: the dotted line is "a reference line drawn by the code, not a pre-registered criterion" (report §10) |
| D1 | appendix A.1 | DEV ensemble, stored words and values side by side, text or table only |
| D2 | appendix A.2 | extension systems S1 to S6, per-system gate and stored per-system words, text or table only |
| D3 | `2026-10-23-math-benchmark-mapping.md` §3 after review (WU-0024.3, WU-0025.6) | Dysts descriptive table and caption; not part of the standalone appendix as built, so it goes to the handout as a separate table |

## 2. Panels that change (tri-fold)

**Panel 3. Four conditions and a blend weight.** Use these one-line definitions (F1 resolved, each from v3):
- Recurrence: how close the nearest matching past state is to the present one.
- Observability: how well the hidden state can be recovered from noisy measurements.
- Instability: how fast small errors grow along the forecast.
- Noise sensitivity: how much the chosen past match moves when the noise changes; defined on the analog side.
Add, for P1: "under the conditions stated in the theorem, blending can extend the horizon by at most half an error-doubling time" (theorem program errata of 2026-10-21).

**Panel 4. Three test systems.** Why these systems (exact equations: v3 §4; the other two points are description, not recorded intent): exact equations, so every hidden state and every condition is known; standard chaotic systems that forecasting benchmarks use; different in shape and in how fast errors grow, and Chua's has a piecewise-linear part. The student may add their own reason.

**Panel 5. How the test works.** As v1, plus: the sealed seed was drawn by the owner and recorded only as a salted hash before the run, separate from every development seed, with the rules and code frozen first (F5 resolved from DEC-0001 and the run's freeze check); do not say "nobody ever saw it" unless the owner attests it. Add one line: the regeneration was by the same person on the same computer, which shows determinism, not an independent reproduction (report §10).

**Panel 6. What we found (primary).** Slot F1 (promoted). Header required.
Must answer, in the words of report §4: H2a not supported (fail on all three systems); H2b supported (pass on all three systems in this run); H3c inconclusive (pass on Rössler; not decidable at this precision on Lorenz-63 and Chua; no system failed). None of the three studied systems is PROVISIONAL (report §3). Read each interval before its word. Say once: "not supported" is not "disproved"; "inconclusive" is not "no effect"; the error of "not supported" is not controlled the same way (v3 §7).

**Panel 7. Highlights (secondary).** Slot F2 (promoted). The fixed list of v1 §3 with its §4 words: H2c inconclusive, H2e supported, H3a inconclusive (cannot fail by design), Q-N an estimate with two readings, never pass or fail. No substitution.

**Panel 8. What it means, and what it does not.** Student text. Prompts as v1, plus: "Which of the ruled limits (panel 9) matters most for H2a and H3c?" and the recommended wording of what a pass does not show (F9 resolved): "supported" means that on these three systems, with an exact physics model and one measured variable, the prediction held in this run; it does not show the same for a wrong or approximate physics model, for real measured data, for higher-dimensional systems, or for other seeds (v3 §8 scope and future work; report §10, one realization per system).

**Panel 9. Limits.** v1 list, plus the ruled items of report §10: H2a part (ii) has low power and essentially cannot pass (DEF-0022, accepted by the owner); same-host, same-person regeneration (determinism only); owner code review waived, results spot-checked by the owner, code covered by independent agent reviews; no numerical-error estimate or per-quantity status for the secondary rows, and the status wording of the secondaries does not say whether a secondary is confirmatory in this run (NVVUQ.22 gaps G1 to G3); the error of the fixed number of fitting steps in the physics-based forecaster is not estimated for the official run (DEF-0027, v3 §8); H2e was added after the pilot showed the effect; figure captions R1 to R4 carry no experiment, identifier or interval; a subsequent pre-registered study will need different intervals and sample sizes (owner, ledger seq 36).

**Panel 10. Cross-check and checks.** F3 (promoted), grey, "information only", "changes no verdict" (DEC-0031). The verdict words stored in the GPU file are not shown.

**Panel 11. What next, and thanks.** As v1; Future work wording: "a subsequent pre-registered study".

**Panel 12 (new, appendix handout). Development context: not a hypothesis test.** Placement (DEC-0045): a handout, or the back of the board, physically apart from panels 6, 7 and 10 and from F1 to F3. Text and tables only, no figure. Header on the sheet and on every table: `Development context: not a hypothesis test`; each table names its seed ids.
Fixed sentences:
- "These are development runs on development seeds, exploratory, not confirmatory. Nothing here changes or adds to the promoted result."
- "For the pre-registered result, read section 5 of the promoted report. This sheet does not reprint any value from it." (the pointer; the built appendix has none)
- "The code that reports the verdicts of the extension systems is development-only and has not been reviewed by the owner." (DEC-0045 item 3)
Fixed caption sentence for every table and slide A1, A2 and A3 that prints V3 (R4): "V3: the analog forecaster's valid-prediction time, the first step at which its error against the noisy verifying observation exceeds theta = 0.4 of the standard deviation of the observed variable, Kaplan-Meier median in Lyapunov times; reported, not a gate." Also under D2: "S1 to S3: exploratory readings pre-specified in WU-0021.2; S4 to S6: in WU-0023.2."
Must answer:
- (D1) What is a development seed, and why are these runs not tests? How much do the stored words and values move between development seeds on the three studied systems? Side by side, no mean, spread or range (appendix A.1).
- (D2) Which other systems did we try, and why? Six systems outside the v3 design (a higher-dimensional Rössler system, a Lorenz system in an intermittent regime, Rössler observed through a different variable, and three Dysts systems), in appendix A.2. Per system only: gate and stored per-system words; no overall verdict; one development seed (DEV-3) each; the readings were fixed before the runs. **Only S1 (`rossler_hyper`) passed the validity gate; S2 to S6 failed V7 and are PROVISIONAL**, so their words are shown as stored with the failure reported, never repaired. The extension table also says "systems outside the v3 design; exploratory readings pre-specified in WU-0021.2".
- (D3) How does Dysts relate? Same equations for the three studied systems, parameters equal up to rounding. One difference is reported: the Dysts stored maximum exponent for Chua is about three times ours (a number may be added if the owner chooses); our value is reproduced by an independent implementation; the stored value was probably produced by a simpler Dysts estimator without renormalisation (our inference from Dysts' code and an older results file, not stated by Dysts), and why it is larger is not shown; differences of equations, parameters, time unit, attractor and the settings of our own exponent method were excluded (attribution note §5; script note §§2 to 4). The benchmark uses a percentage error that depends on the signal size, its own time unit, noise defined in a way not known to match ours, averages over many systems, and has no forecaster with known equations in the texts we read; so it is descriptive, not directly comparable, not a ranking. Wherever V3 (the analog forecaster's valid-prediction time) is quoted, the caption states: threshold theta = 0.4 sigma_x, measured against the noisy verifying observation, reported and not gated.

## 3. Ten-slide variant, with appendix slides (replaces v1 §4 and v2 §3)

| # | Slide | Content | Figure |
| --- | --- | --- | --- |
| 1 to 5 | As v1 | panels 1 to 5; slide 3 carries the four definitions; slide 4 the reason for the three systems; slide 5 the determinism line and the sealed-seed wording | as v1 |
| 6 | Primary verdicts | panel 6; header | F1 (promoted) |
| 7 | Secondary highlights | panel 7; header | F2 (promoted), R2 if needed, captioned from the map |
| 8 | What it means, and does not mean | panel 8 (student) | none |
| 9 | Limits and the CPU/GPU cross-check | panels 9 and 10; "information only" | F3 (promoted) |
| 10 | What next, thanks | panel 11 | none |
| A1 | Development context: not a hypothesis test (ensemble) | D1, side by side | none |
| A2 | Development context: not a hypothesis test (extension) | D2, per system, S2 to S6 PROVISIONAL, code status sentence | none |
| A3 | Development context: not a hypothesis test (Dysts) | D3 | none |
| A4 | Context figures | R1 to R4 with map captions | R1 to R4 |

Presenting rules: one message per slide; interval before word; slides A1 to A3 are shown only after slide 10 and only if asked; speak the development header aloud on each.

## 4. Honesty checklist (replaces v1 §6 and v2 §4). Ticks are for this draft with evidence; re-tick after the student edits and before anything leaves the owner and the student.

- [x] Every sealed item comes from `promoted/CONF-1/`; none from the preliminary figures directory. Evidence: §0 and §1 of this file name only `promoted/CONF-1/` paths.
- [x] The label in §0 is the DEC-0045 wording; no "UNPROMOTED" or "preliminary" header remains on sealed items. Evidence: the words occur in this file only in the what-changed table, §0 (as retired) and §5.
- [ ] Every estimate is shown with its interval at the stored level; the band is drawn. (Applies to the built figures; checked at build, not in this outline.)
- [x] The only verdict words are the pre-registered ones, as in report §4; H3c is shown with its per-system words. Evidence: panel 6 compared with the H2a, H2b and H3c rows of the §4 table (fail/fail/fail; pass/pass/pass; inconclusive/pass/inconclusive for Lorenz-63/Rössler/Chua).
- [x] None of "proves", "confirms", "significant", "shows that", "demonstrates", "breakthrough" in result text. Evidence: grep over this file, hits only in §5 (the list itself).
- [x] "Inconclusive" never as "no effect"; "not supported" never as "disproved"; the v3 §7 sentence on the error of "not supported" is in panel 6.
- [x] H3a described as unable to fail; Q-N as a reading; the gain bound as "reported, v1 statistic, v3 screen pending" (v1 §3 rows, kept in panel 7).
- [x] The GPU cross-check only in F3 and panel 10, grey, "information only", "changes no verdict".
- [x] Panel 9 lists every v1 limit and every ruled limit.
- [x] R1 to R4 captions name experiment and identifier from the figure map, say "no interval", and do not call the R3 dotted line a criterion.
- [x] No claim of independent reproduction; no claim that the owner reviewed the code, including the extension's verdict-reporting code. Evidence: panels 5, 9, 11 and 12 wording.
- [ ] V3 caption present on every table and slide that prints V3 (uses the panel 12 caption sentence, not a tool change).
- [x] Appendix: every development table is headed "Development context: not a hypothesis test" and names its seed ids (rule in panel 12; the built appendix does this, appendix A section headers).
- [x] Appendix: the ensemble is shown side by side with no mean, standard deviation or range. Evidence: appendix A.1 text "nothing is combined across them".
- [x] Appendix: extension systems per system only; no overall verdict; no "supported" or "not supported" for them; one development seed each; S2 to S6 marked PROVISIONAL; code status sentence present. Evidence: panel 12 and A2.
- [x] Appendix: the Dysts table has none of "outperform", "beats", "better than", "worse than", "superior", "wins", "state of the art"; it says "descriptive, not directly comparable". Evidence: the mapping note section 7 grep, 0 hits (re-run on the final handout text).
- [x] Appendix: no development number on or beside F1, F2 or F3, nor in panels 1 to 11, the statement or the abstract. Evidence: this file has no number from any run; the one ratio (Chua, about 2.85) is in panel 12 only.
- [x] Appendix: no sealed value is reprinted in appendix A. Evidence: grep of the standalone appendix for the sealed H2a, H2b and H3c point estimates, 0 hits.
- [ ] Appendix: every number is from appendix A or the reviewed Dysts table, traced, and `check` exit 0. (Main session at the build; the `check` could not be run in this worktree, matplotlib is not installed here.)
- [x] The highlights are exactly the v1 §3 list, whatever they show.
- [ ] Interpretation is the student's and marked. (The student's act.)
- [ ] Figures readable in grey; Okabe-Ito palette; verdicts also by marker and text. (Checked on the built figures.)
- [x] V3 is never quoted without theta = 0.4 sigma_x and "against the noisy verifying observation"; and V3 is not quoted numerically in this file.

## 5. Must NOT be said (poster, slides, talk)

- An overall verdict for any extension system, or that the extension supports, confirms or generalizes the promoted result. The gate words PASS and PROVISIONAL are allowed per system.
- Any ranking of systems, forecasters or methods, including against the Dysts benchmark; none of "outperform", "beats", "better than", "worse than", "superior", "wins", "state of the art".
- "Proved", "confirmed", "significant" for a result (theorems P1 and P2 may be "proved").
- "Inconclusive" as "no effect"; "not supported" as "disproved".
- Any development number in the main panels or slides 1 to 10; any average or spread across development seeds.
- "Independently reproduced", "verified by a second person", "the owner reviewed the code" (also for the extension's verdict-reporting code).
- "v4"; write "a subsequent pre-registered study".
- The stored label "CONFIRMATORY: UNPROMOTED" or "preliminary" on a sealed item.
- Any V3 value without theta = 0.4 sigma_x and the noisy verifying observation; any V3 value of the promoted run (report §3) beside a development V3 value; the values 1.97, 3.43 and 2.8 from the development notes (they equal the promoted run's V3 values; see open item O6).
- That Dysts' stored Chua exponent is wrong or that ours is "validated" by Dysts: the cause is not determined and no published Chua reference exists.
- "Nobody ever saw the data" unless the owner attests it (panel 5 wording is the records-based one).

## 6. Trace table (every sentence with a number or a verdict word)

| Row | Statement | Source | Kind |
| --- | --- | --- | --- |
| PO1 | Promotion of CONF-1 by the owner on 2026-10-23; label wording | ledger entry 40; manifest line of 2026-10-23; DEC-0045 item 2; promoted copies in `promoted/CONF-1/` | Q |
| PO2 | H2a not supported (fail on all three); H2b supported (pass on all three); H3c inconclusive (pass on Rössler; inconclusive on Lorenz-63 and Chua; none failed); not-supported and inconclusive caveats; H2a failure reading pre-registered and not tested | promoted report §4 (decision rule paragraph; table rows H2a, H2b, H3c; "Primary hypotheses" list) | Q |
| PO3 | None of the three studied systems PROVISIONAL | promoted report §3, closing line | Q |
| PO4 | Secondary words H2c inconclusive, H2e supported, H3a inconclusive (cannot fail), Q-N an estimate with two readings; gain bound "reported, v1 statistic, v3 screen pending" | promoted report §4 (table; "Secondary rows"; Q-N paragraph); v1 poster outline §3 (fixed list); DEC-0033 M3 | Q |
| PO5 | Regeneration by same actor and host: determinism, not independent reproduction; thread count and BLAS dependence | promoted report §10, §9; DEC-0035; ledger seq 31, 34 | P |
| PO6 | Owner code review waived; results spot-checked; independent agent reviews; DEF-0001 open | promoted report §10; ledger seq 33 | Q |
| PO7 | H2a(ii) low power, accepted | promoted report §10 (DEF-0022); DEC-0041; ledger seq 32 | P |
| PO8 | NVVUQ.22 gaps for secondary rows; figure captions; R3 dotted line is a reference line | promoted report §10; figure map; ledger seq 36 | P |
| PO9 | A subsequent pre-registered study needs different intervals and sample sizes | ledger seq 36; DEC-0042 item 4; DEC-0045 item 2 | P |
| PO10 | GPU cross-check information only, changes no verdict | promoted report §8; DEC-0031 | Q |
| PO11 | Four one-line definitions of the conditions | v3 §3, §4 (CP), §5 table; statement v3 trace rows U2 to U5 | P |
| PO12 | Reason for the three systems | v3 §4, §8; mapping note M1; unconfirmed intent (open item O3) | A |
| PO13 | P1 horizon bound under stated conditions | theorem program errata addendum 2026-10-21 (L7(ii), P1(d)); DEC-0040 | Q |
| PO14 | Seed drawn by the owner, sealed by salted hash, supplied only at run time; rules and code frozen first | DEC-0001; promoted report §2 (Seed kind, Freeze check) | Q |
| PO15 | What a pass does not show | v3 §8 scope and future work; report §10 (one realization per system) | A |
| PO16 | Appendix A holds A.1 (ensemble DEV-1, DEV-3, DEV-4; side by side) and A.2 (six extension systems, DEV-3); 1073 traced values | `2026-10-23-appendix-a-standalone.md` sections A.1, A.2, B; `...standalone.trace.csv` (1074 lines with header) | Q |
| PO17 | Only S1 `rossler_hyper` passed the gate; S2 to S6 failed V7 and are PROVISIONAL | appendix A.2 gate table and "Marked in this part" line; `2026-10-23-extension-ensemble-summary.md` gate table | Q |
| PO18 | Extension code development-only, not owner-reviewed; owner's review pending | DEC-0045 item 3; DEC-0038 addendum A1, A2 | Q |
| PO19 | One development seed (DEV-3) per extension system; readings fixed before runs; no overall verdict | appendix A.2 intro and table headers; extension schedule note O3; `2026-10-20-math-extension-specs.md` §5 | Q |
| PO20 | Dysts: same equations, parameters equal up to rounding | `2026-10-23-researcher-dysts-tables.md` A.1; mapping M1 | Q |
| PO21 | Chua: Dysts stored maximum differs by a factor of about 2.85; our value reproduced by an independent estimator; cause not determined | `2026-10-23-math-chua-attribution.md` §0, §2, §5; Dysts value 1.2301 from tables note A.2 divided by v3 §4 table value 0.431 | Q |
| PO22 | Benchmark differences: percentage error, own time unit, averages over many systems, no known-equation forecaster | mapping note M5, M9, M15, §5 paragraph | P |
| PO23 | V3 threshold 0.4 sigma_x, noisy verifying observation, reported and not gated | mapping note §1 (V3 definition; documentation points (i), (ii)), F1, F4; v3 §6 | Q |

## 7. Open items for the owner and the student (only they can supply these)

Owner:
- **O1.** Whether the poster may carry panel 12 on the back of the board or only on a handout, (DEC-0045 chooses "a handout or the back of the board").
- **O3.** Whether the reasons given in panel 4 are the reasons you chose the three systems.
- **O4.** Whether you can attest, from your own knowledge, that nobody looked at the confirmatory data before the run; if so, add it in your name (panel 5).
- **O5.** The final cutoff: appendix A is built from the files of 2026-10-26 18:00; confirm the systems listed in panel 12 then.
- **O6.** For information: the numbers 1.97, 3.43 and 2.8 recur in development notes (`2026-10-20-researcher-dysts-extension.md` C.3 and `2026-10-20-math-extension-specs.md` line 198) as CP values at "error above 0.2". They equal the V3 values stored in the sealed run (promoted report §3), written before promotion. How they reached those notes is for the main session and the owner to establish. Nothing in this outline uses them.
- **O7.** Recording theta = 0.4 sigma_x in a v3 amendment (mapping note F1) is the owner's decision.
- **O8.** The extension code review (DEC-0038 A1, A2) is the owner's pending act; panel 12 says it is not done.

Student:
- **ST1.** All panel and slide prose; the interpretation (panel 8) and the motivation in panel 12; the F4 schematic; the attractor pictures; .
- **ST2.** Personal text and entries (name, school, category).
