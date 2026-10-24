# Poster outline v2, 10-slide variant, appendix and checklists (DRAFT for the owner and the student to edit)

Draft by claude-opus-5-5 (planner), 2026-10-23, for WU-0025.4 and the update after promotion of the WU-0020.5 outline (`2026-10-19-prelim-poster-outline.md`, "v1"). The student (Deem Albaty) writes all poster and slide prose and the interpretation (D8). This file gives structure, sources and rules. **It contains no number from any run.** Result words come from findings §4 only; numbers reach the poster only through the figures and tables built by the tool, from the promoted copy.

Sections and panels not listed here are unchanged from v1 (panels 1 to 5 and 11, the glossary of v1 §7).

## 0. Status and release rule (replaces v1 §0)

- **The CONF-1 result is promoted** (ledger entry 40, 2026-10-23; manifest line of the same date). Sealed results may now appear on the poster and slides, subject to the fair's own rules (open question 1).
- **Source of every sealed item: `promoted/CONF-1/` only** (on develop): `report.md`, `report.figures/` (F1 to F3 with the promoted title), `figures/` (the four RESULTS.md figures, R1 to R4), `RESULTS.md`, `results.json`. Never the figures in `docs/agent/notes/2026-10-20-prelim-findings-conf1.figures/`: they carry the unpromoted title.
- **Header on every result panel and slide:** `[OWNER: label; proposed "Confirmatory result, seed CONF-1, promoted by the owner on 2026-10-23"]`. The headers `CONFIRMATORY: UNPROMOTED` and "(preliminary, unpromoted)" are retired. Note: §2 of the promoted report still shows the row "Label: CONFIRMATORY: UNPROMOTED"; it quotes the stored label of the sealed file and is not a status. Do not copy it.
- **v1 line "There is no new DEV ensemble before the fair" is replaced (DEC-0037):** development material (the DEV ensemble of WU-0026, the extension systems of WU-0021 and WU-0023, the Dysts table of WU-0024) appears only in the appendix panel and appendix slides of §4 below, titled `Development context: not a hypothesis test`, never on or beside F1, F2 or F3, and only after review WU-0025.6. Its numbers come only from appendix A (`docs/agent/notes/2026-10-23-appendix-a-development.md`, not yet present) and the WU-0024 note.

## 1. Figures (changes to v1 §1)

| Slot | Source now | Notes |
| --- | --- | --- |
| F1, F2, F3 | `promoted/CONF-1/report.figures/` | title "FINDINGS FOR SEED CONF-1 / Result promoted by the owner"; otherwise pixel-equal to the checked figures (DEC-0043) |
| R1 to R4 | `promoted/CONF-1/figures/` | captions must be written from the figure map (`2026-10-21-promotion-figure-map.md`), naming experiment and identifier: R1 separation_weight_vs_horizon E4, H2a; R2 kaplan_meier_by_rule E4, the rules behind H2c, H2d, H3c, no verdict; R3 regret_vs_regimes E5, H3c; R4 knob_response_library E1 and E2, H2b. Each caption says "no interval shown; context, not a verdict". R3: the dotted line is "a reference line drawn by the code, not a pre-registered criterion" (findings §10) |
| D1 (new) | appendix A.1 | DEV ensemble, stored words and values side by side, text or table only |
| D2 (new) | appendix A.2 | extension systems, per-system gate and stored per-system words, text or table only |
| D3 (new) | WU-0024 note | Dysts descriptive table and its caption, as reviewed |

## 2. Panels that change (tri-fold)

**Panel 5. How the test works.** As v1, plus one line: the regeneration was by the same person on the same computer, which shows determinism, not an independent reproduction (findings §10).

**Panel 6. What we found (primary).** Slot F1 (promoted). Header required.
Must answer, in the words of findings §4: H2a not supported (fail on all three systems); H2b supported (pass on all three systems in this run); H3c inconclusive (pass on Rössler; not decidable at this precision on Lorenz-63 and Chua; no system failed). No system is PROVISIONAL (findings §3). Read each interval before its word. Say once: "not supported" is not "disproved"; "inconclusive" is not "no effect"; the error of "not supported" is not controlled the same way (v3 §7).

**Panel 7. Highlights (secondary).** Slot F2 (promoted). The fixed list of v1 §3, with its §4 words: H2c inconclusive, H2e supported, H3a inconclusive (cannot fail by design), Q-N an estimate with two readings, never pass or fail. No substitution.

**Panel 8. What it means, and what it does not.** Student text, prompts as v1. Add the prompt: "Which of the ruled limits (panel 9) matters most for H2a and H3c?"

**Panel 9. Limits.** v1 list, plus the ruled items of findings §10: H2a part (ii) has low power and essentially cannot pass (DEF-0022, accepted by the owner); same-host, same-person regeneration (determinism only); owner code review waived, results spot-checked by the owner, code covered by independent agent reviews; no numerical-error estimate or per-quantity status for the secondary rows (NVVUQ.22 gaps); figure captions (R1 to R4) carry no experiment, identifier or interval; a later study will need different intervals and sample sizes (owner, ledger seq 36).

**Panel 10. Cross-check and checks.** F3 (promoted), grey, "information only", "changes no verdict" (DEC-0031). The verdict words stored in the GPU file are not shown.

**Panel 12 (new, appendix box). Development context: not a hypothesis test.** Text and tables only, no figure. Placement: physically apart from panels 6, 7 and 10 (owner to choose: bottom of the right fold with a rule line, the back of the board, or a separate handout; open question 2).
Must answer: What is a development seed, and why are these runs not tests? (D1) How much do the stored words and values move between development seeds on the three studied systems? Side by side, no mean, spread or range (O7). (D2) Which other systems did we try, and why (higher dimension, intermittent bursts, a different observed variable, Dysts systems)? Per system only: gate and stored per-system words; no overall verdict; one development seed each; the readings were fixed before the runs; nothing here changes the promoted result. (D3) How does Dysts relate? Same equations for the three studied systems; different units and metrics; no physics-based forecaster; descriptive, not a ranking.
Each table names its seed ids. The extension table also says "systems outside the v3 design; exploratory readings pre-specified in WU-0021.2".

## 3. Ten-slide variant, with appendix slides (replaces v1 §4)

| # | Slide | Content | Figure |
| --- | --- | --- | --- |
| 1 to 5 | As v1 | panels 1 to 5; slide 5 adds the determinism line | as v1 |
| 6 | Primary verdicts | panel 6; header | F1 (promoted) |
| 7 | Secondary highlights | panel 7; header | F2 (promoted), R2 if needed, captioned from the map |
| 8 | What it means, and does not mean | panel 8 (student) | none |
| 9 | Limits and the CPU/GPU cross-check | panels 9 and 10; "information only" | F3 (promoted) |
| 10 | What next, thanks, AI-use statement | panel 11; the AI-use statement says agents also reviewed the code | none |
| A1 | Development context: not a hypothesis test (ensemble) | D1, side by side | none |
| A2 | Development context: not a hypothesis test (extension) | D2, per system | none |
| A3 | Development context: not a hypothesis test (Dysts) | D3 | none |
| A4 | Context figures | R1 to R4 with map captions | R1 to R4 |

Presenting rules: one message per slide; interval before word; slides A1 to A3 are shown only after slide 10 and only if asked; speak the development header aloud on each.

## 4. Honesty checklist (replaces v1 §6; tick every item before anything leaves the owner and the student)

- [ ] Every sealed item comes from `promoted/CONF-1/`; none from the preliminary figures directory.
- [ ] Every result panel and slide carries the owner's promotion label; no "UNPROMOTED" or "preliminary" header remains on sealed items.
- [ ] Every estimate is shown with its interval at the stored level; the band is drawn.
- [ ] The only verdict words are the pre-registered ones, as in findings §4; H3c is shown with its per-system words.
- [ ] None of "proves", "confirms", "significant", "shows that", "demonstrates", "breakthrough" in result text.
- [ ] "Inconclusive" never as "no effect"; "not supported" never as "disproved"; the v3 §7 sentence on the error of "not supported" is present.
- [ ] H3a described as unable to fail; Q-N as a reading; the gain bound as "reported, v1 statistic, v3 screen pending".
- [ ] The GPU cross-check only in F3 and panel 10, grey, "information only", "changes no verdict".
- [ ] Panel 9 lists every v1 limit and every ruled limit of §2 above.
- [ ] R1 to R4 captions name experiment and identifier from the figure map, say "no interval", and do not call the R3 dotted line a criterion.
- [ ] No claim of independent reproduction; no claim that the owner reviewed the code.
- [ ] Appendix: every development table is headed "Development context: not a hypothesis test" and names its seed ids.
- [ ] Appendix: the ensemble is shown side by side, with no mean, standard deviation or range.
- [ ] Appendix: extension systems per system only; no overall verdict; no "supported" or "not supported" for them; one development seed each is stated.
- [ ] Appendix: the Dysts table has none of "outperform", "beats", "better than", "worse than", "superior", "wins", "state of the art"; it says "descriptive, not directly comparable".
- [ ] Appendix: no development number on or beside F1, F2 or F3, nor in panels 1 to 11, the statement or the abstract.
- [ ] Appendix: every number is from appendix A or the WU-0024 note after review WU-0025.6, traced and `check` exit 0.
- [ ] The highlights are exactly the v1 §3 list, whatever they show.
- [ ] Interpretation is the student's and marked; the AI-use statement is updated.
- [ ] Figures readable in grey; Okabe-Ito palette; verdicts also by marker and text.

## 5. Must NOT be said (poster, slides, talk)

- An overall verdict for any extension system, or that the extension supports, confirms or generalizes the promoted result.
- Any ranking of systems, forecasters or methods, including against the Dysts benchmark.
- "Proved", "confirmed", "significant" for a result (theorems P1 and P2 may be "proved").
- "Inconclusive" as "no effect"; "not supported" as "disproved".
- Any development number in the main panels or slides 1 to 10; any average or spread across development seeds.
- "Independently reproduced", "verified by a second person", "the owner reviewed the code".

## 6. Still to be supplied

1. Student: all panel and slide prose, the interpretation (panels 8 and 12 motivation), the F4 schematic, the attractor pictures, the AI-use statement.
2. Owner: the promotion label wording; the placement of panel 12; the systems in appendix A at the cutoff (2026-10-26 18:00).
3. Main session: appendix A (WU-0025.5) and its review (WU-0025.6); the WU-0024 table and caption after its review.
4. Researcher: the fair's rules (date, unverified or exploratory results, AI-use disclosure, poster size): still open from v1.

## 7. Open questions (to the owner)

1. Does the fair allow exploratory development results on the board at all, or only on slides or a handout?
2. Is panel 12 on the board, on the back, or a handout only?
3. Reading 4 of `2026-10-20-math-extension-specs.md` §5 compares the S1 H2a(ii) interval with the sealed values. Under D4 ("never beside the sealed result"), proposal: appendix A states the S1 reading and refers to "§5 of the promoted report" without reprinting any sealed value. Agree?
4. The extension's verdict-reporting code is still awaiting the owner's review (DEC-0038 addendum A1, A2). Should panel 12 say so?
