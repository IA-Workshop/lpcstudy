# Research statement v2 (DRAFT for the owner and the student to edit): when should a forecaster trust the past, and when the physics?

Draft by claude-opus-5-5 (planner), 2026-10-23, for WU-0025.3 and the update after promotion of the WU-0020.10 draft (`2026-10-19-research-statement-draft.md`, "v1"). For the internal proposal due 2026-10-28. The student (Deem Albaty) writes the interpretation and owns the final text (D8). `[STUDENT: ...]` and `[OWNER: ...]` mark words only they can supply.

**Number rule for this file.** It contains no number from any run. Result words are copied from section 4 of the findings document only (promoted copy `promoted/CONF-1/report.md` §4, lines 91 to 125; source document `docs/agent/notes/2026-10-20-prelim-findings-conf1.md` §4, lines 94 to 128). If the student wants an estimate or interval in the text, it is copied from §5 of the promoted copy with its interval and level, and cited by section and row. Development numbers (the ensemble, the extension systems, the Dysts table) never appear in this statement (O5); they appear only in appendix A (`docs/agent/notes/2026-10-23-appendix-a-development.md`, built in parallel, not yet present at the time of writing). The digits left in the text are design constants of v3 (with their v3 section in the v1 trace table), dates, and system names.

Tags: `{S#}` are the v1 trace rows (unchanged, see the v1 trace table); `{T#}` are new rows, in the trace table at the end. Remove the tags in the final text.

## What changed from v1

| Where | v1 | v2 | Why |
| --- | --- | --- | --- |
| Status words | "unpromoted", "(preliminary, unpromoted)" | "promoted by the owner on 2026-10-23" (label to confirm) | ledger entry 40, manifest line of 2026-10-23 {T1} |
| §6 Cross-checks | "another person regenerates the official run" | same person, same computer: shows determinism, not independent reproduction | DEC-0035, ledger seq 31 and 34 {T5} |
| §6 Verdict rule, flag F3 | "the overall verdict" (scope unclear) | one overall word per hypothesis | findings §4 gives one per hypothesis {T2} |
| §7 (new) | `[RESULTS: after promotion]` | the three primary words, per system | findings §4 only {T2} |
| §8 Limits | v3 §8 items | plus the ruled items: DEF-0022 power, same-host regeneration, waived code review, NVVUQ.22 gaps, figure captions, later runs need different intervals and sample sizes | findings §10 {T6 to T10} |
| §9 (new) | none | number-free paragraphs: extension, development ensemble, Dysts context | DEC-0037, DEC-0039, WU-0025.3 {T12 to T17} |
| §10 Status | v3 sequence only (flag F4) | dated facts to promotion | manifest, ledger {T18} |

## 1. The research question

Can four measurable local conditions of a chaotic system decide, state by state, how much to trust an analog forecaster (one that copies the past) versus a physics-based forecaster (one that runs known equations), and for how long? {S1} We tested this with three pre-registered hypotheses on three simulated chaotic systems, using a sealed fresh random-number seed and rules fixed before the run. {S2}

## 2. Why it matters

(Unchanged from v1 §2.) A chaotic system is deterministic, but a tiny error in its starting state grows quickly, so every forecast of it eventually fails. {S3} Forecasting such systems matters from sensing to climate. {S4} Analog forecasters find the past situation most like the present and copy what followed; they improve with more data. Physics-based forecasters integrate known equations, but must first estimate the hidden current state from noisy measurements. {S5} Most hybrids combine the two in a fixed way, and we know of no earlier work that decides, state by state, which to trust. {S6} [STUDENT: one sentence, in your words, on why this matters to you or a reader.]

## 3 to 5. Forecasters, conditions, systems

Unchanged from v1 §3, §4 and §5 (tags S7 to S20, flags F1 and F2 still open). Copy them here when assembling the final text.

## 6. The design in plain words

As v1 §6 (tags S21 to S29, S31), with two bullets replaced:

- **Verdict rule.** Per system, a hypothesis passes if its interval lies inside the pre-set band or wholly on the predicted side of a bound, fails if wholly outside, and is otherwise inconclusive. {S27} Each hypothesis then gets one overall word: "supported" only if all three systems pass, "not supported" if at least one fails, and "inconclusive" otherwise. {S28, T2}
- **Cross-checks.** The official run was on a CPU. A GPU run of the same seed is an information-only cross-check and changes no verdict. {S30, T11} The design asked another person to regenerate the official run. With only one person on the team able to run it, the owner regenerated it on the same computer: every compared value was equal, which shows the run is deterministic, not that it reproduces on another computer. {T5}

## 7. What we found

Header for this section and every copy of it: `[OWNER: label, proposed "Confirmatory result, seed CONF-1, promoted by the owner on 2026-10-23"]` {T1}

All three systems passed the validity gate (checks V1 to V7; V3 is only reported), so no result is marked provisional. {T4}

- **H2a: not supported.** It failed on all three systems. "Not supported" is not "disproved", and it says nothing about systems beyond the three studied. v3 fixed in advance how a failure would be read (instability enters the weight through uneven starting errors); that reading was not itself tested. {T2} The second part of H2a can be refuted but essentially cannot pass at these sample sizes, as v3 anticipated. {S38, T7}
- **H2b: supported.** It passed on all three systems in this run. {T2}
- **H3c: inconclusive.** It passed on Rössler; on Lorenz-63 and Chua it could not be decided at this precision; no system failed. Inconclusive does not mean the effect is absent. {T2}
- [OPTIONAL, one line, the pre-fixed secondary highlights in their §4 words: H2c inconclusive, H2e supported, H3a inconclusive, Q-N an estimate read from the v3 table, not pass or fail. {T3}]

[STUDENT: if you quote an estimate, copy it with its interval and level from §5 of the promoted report and cite the row. Otherwise leave numbers to the poster figure F1.]

[STUDENT: your reading of what these three words mean, and what surprised you, marked as interpretation.]

## 8. What is claimed and what is not

"Supported" means: on these three systems, with an exact physics model and one measured variable, the pre-registered prediction held in this run. It does not show the same for real data, a wrong physics model or higher-dimensional systems (flag F9). {S32} "Not supported" means at least one system failed a pre-set test; its error is not controlled the same way and, with 95% intervals, can reach about 7.3% over three systems. {S33} "Inconclusive" is not "no effect".

Limits stated in advance by v3 (v1 §7 list, tags S34 to S39), plus the limits the owner ruled on before promotion (findings §10):

- Three low-dimensional systems, one observable, one sealed seed, so one realization per system. {S34}
- Same systems with fresh random numbers: more precision, not new systems. {S35}
- Practical (non-exact) features carry little of the information in the exact ones, so allocation results are limited by them, not by theory. {S36}
- H3a cannot fail; the second part of H2a has low power: it can be refuted but essentially cannot pass. The owner accepted this as a known limitation. {S38, T7}
- The intervals cover slightly less often than their nominal level. {S39}
- The regeneration was by the same person on the same computer: it shows determinism, not an independent reproduction. Results depend on the thread count and the computer's linear-algebra library, so another computer may differ. {T5}
- The owner did not review the code; the owner spot-checked the results, and the code was covered by independent AI-agent reviews. {T6}
- For the secondary and reported rows the official results file gives no numerical-error estimate and no per-quantity verification status. {T8}
- The four built-in report figures name no experiment or hypothesis and show no interval; a dotted line in the regret figure is a reference line, not a pre-registered criterion. {T9}
- A later study will need different intervals and sample sizes; this changes nothing in the present analysis. {T10}

## 9. Beyond the pre-registered study (development, exploratory)

Header for this section and every copy of it: `DEVELOPMENT CONTEXT: not a hypothesis test`. (Drafting rule, criterion E8 of WU-0025: the paragraphs below contain no digit except in system names; the tags and slots are removed in the final text.)

**Extension.** After the pre-registered run, and on development seeds only, we asked whether the same patterns appear in chaotic systems that differ from the three studied in a qualitative way: a higher-dimensional system with two directions of error growth, a Lorenz system in a regime with intermittent bursts, a Rössler system observed through a different variable, and further systems from the Dysts collection. [OWNER: confirm the system names that are in appendix A at the appendix cutoff.] The forecasters, the tests and the decision thresholds were the same as in the pre-registered study, and the readings were written down before any extension run. Each extension system is read on its own: there is no overall verdict, no ranking of systems, and nothing here changes or adds to the pre-registered result. Each system was run on one development seed only, so seed-to-seed variation is not known for them. A confirmatory claim about any of these systems would need its own sealed seed and freeze. {T12, T13, T19}

**Development ensemble.** We also repeated the full study on several development seeds for the three studied systems, to see how much the readings move from seed to seed. Those runs are shown side by side in the development appendix, without any average or range, and are not a test. {T14}

**Dysts context.** Dysts is a public collection of chaotic systems with published forecasting benchmarks, which our design document cites. {T15} Its entries for Lorenz-63, Rössler and Chua use the same equations as ours, with parameters equal up to rounding. Its stored exponent estimates do not all agree with each other or with ours, and the cause could not be found from the published texts; for Chua at our parameters no published reference value exists. {T16} The benchmark measures error, time and noise in different units, and it has no forecaster with known equations like PLP, so its values are context only and cannot be compared directly with ours; a descriptive table is in the development appendix. {T17}

[STUDENT: one sentence, marked as interpretation if it is one, on why you wanted to look beyond the three systems.]

## 10. Status and timeline

The design was frozen before the confirmatory run. The official run used the sealed seed on 2026-10-19 (CPU); the GPU cross-check and the regeneration followed on 2026-10-20; two audits followed; the owner promoted the result on 2026-10-23. {T18} [STUDENT: next steps and the dates you commit to.] Deem leads the questions, proofs of P1 and P2, interpretation and presentation; Brian reviews and runs the computation; an AI assistant (Claude) helped with drafting, reference checks, code and code review, and the author reviewed it. {S41} [STUDENT: confirm roles and the AI-use statement; it should now say that AI agents also reviewed the code, because the owner's code review was waived {T6}.]

## Glossary additions (to v1)

| Term | Plain meaning |
| --- | --- |
| Promotion | The owner's recorded decision that a checked result may be reported as the study's result. |
| Development seed | Random numbers used for building and exploring, never for the pre-registered test. |
| Exploratory | Looked at to learn, not to test a prediction fixed in advance. |
| Determinism vs. reproduction | Same inputs on the same computer give the same output; reproduction means another person or computer gets it too. |
| Hyperchaos | Chaos with more than one direction in which small errors grow. |
| Intermittency | Long calm stretches broken by irregular bursts. |
| Dysts | A public database of chaotic systems with forecasting benchmarks. |

## For the author (not part of the statement)

### A. Still to be supplied

1. Student: every `[STUDENT]` slot (§2, §7 interpretation, §9 motivation, §10 dates, roles and AI-use statement); the whole text in your own voice, one to two pages.
2. Owner: the promotion label of §7 and its exact wording on all materials.
3. Owner: the list of extension systems actually in appendix A at the cutoff (§9).
4. Owner or student: v1 flags still open: F1 (the four one-line definitions), F2 (why these three systems), F5 ("never seen"), F9 (what a pass would not show). F3 is settled by findings §4 (one word per hypothesis). F4 is replaced by §10. F8 stands.
5. Applied mathematician (WU-0022.2, not yet written): the wording on the Chua exponent difference, if it changes the §9 sentence.

### B. Must NOT be said

- No overall verdict for any extension system, and no "supported" or "not supported" for them; per-system words only, and only in appendix A.
- No ranking of systems, forecasters or methods; none of "outperform", "beats", "better than", "worse than", "superior", "wins", "state of the art" (WU-0024 D3).
- No "proved", "proves", "confirmed", "confirms", "significant", "shows that", "demonstrates", "breakthrough" for a result (a theorem may be "proved").
- "Inconclusive" never as "no effect"; "not supported" never as "disproved" or "false".
- No development number (ensemble, extension, Dysts) in the statement or beside the sealed result; only in the labeled appendix.
- Not that the result was independently reproduced, nor that the owner reviewed the code.
- Not that the extension confirms, extends or generalizes the pre-registered result.
- No number not copied from the promoted report with its section.

### C. Honesty checklist for this statement (tick before it leaves the owner and the student)

- [ ] The promotion label is on §7 and matches the owner's wording.
- [ ] The three primary words are exactly those of findings §4; H3c carries its per-system words.
- [ ] Every result number, if any, is copied from the promoted report §5 with interval and level, and cited.
- [ ] §9 has no digit except in system names (E8), carries the development header, and says "no overall verdict" and "not a hypothesis test".
- [ ] §8 has every ruled limit: DEF-0022 power, same-host regeneration, waived code review with spot-checked results, NVVUQ.22 gaps, figure captions, later runs need different intervals and sample sizes.
- [ ] The cross-check sentence says "information only" and "changes no verdict".
- [ ] Nothing in section B appears.
- [ ] Interpretation is the student's and is marked as such; the AI-use statement is updated.

### D. Trace table for the new tags

| Tag | Statement | Source | Kind |
| --- | --- | --- | --- |
| T1 | Promotion of CONF-1 run-1 by the owner on 2026-10-23 | ledger entry 40 (`promotion`, 2026-10-23T09:37:12Z), proposal entry 39; `docs/agent/records/results-manifest.md` line of 2026-10-23; promoted copies in `promoted/CONF-1/` | Q |
| T2 | Decision rule; one overall word per hypothesis; H2a not supported (fail on all three), H2b supported (pass on all three), H3c inconclusive (pass on Rössler, inconclusive on Lorenz-63 and Chua); not-supported and inconclusive caveats; H2a failure reading pre-registered and not tested | promoted report §4 (rule paragraph; table rows H2a, H2b, H3c; "Primary hypotheses" list) | Q |
| T3 | Secondary highlight words H2c, H2e, H3a; Q-N an estimate with two readings | promoted report §4 (table; "Secondary rows"; Q-N paragraph); highlight list D10 in `2026-10-19-prelim-poster-outline.md` §3 | Q |
| T4 | Every system passed the gate; nothing provisional | promoted report §3, closing line | Q |
| T5 | Same actor, host and environment; determinism, not independent reproduction; thread count and BLAS dependence | promoted report §10 (regeneration item), §9; DEC-0035; ledger seq 31 (waiver), 34 (ruling); DEF-0023, DEF-0024 | P |
| T6 | Owner code review waived; results spot-checked by the owner; independent agent reviews; DEF-0001 open | promoted report §10 (V&V item); ledger seq 33; DEC-0042 item 1 | Q |
| T7 | H2a(ii) low power, accepted as a known limitation | promoted report §10 (DEF-0022 item), §4 (H2a precision note); DEC-0041; ledger seq 32 | P |
| T8 | NVVUQ.22 gaps G1 to G3 for the secondary and reported rows | promoted report §10 (reporting-gaps item); ledger seq 36 | P |
| T9 | Captions of the four RESULTS.md figures; dotted line a reference line, not a criterion | promoted report §10 (figures item); `2026-10-21-promotion-figure-map.md` | P |
| T10 | Subsequent runs need different intervals and sample sizes; no change to the sealed analysis | ledger seq 36 quote "different intervals/dataset size will be needed in subsequent runs"; DEC-0042 item 4; DEC-0041 item 2 (proposals, WU-0032) | P |
| T11 | GPU cross-check information only, changes no verdict | promoted report §8; DEC-0031 | Q |
| T12 | Extension program: development seeds, exploratory, never beside the sealed result; confirmatory claim needs its own sealed seed and freeze; system characters | DEC-0037 items 1 to 3; DEC-0039 item 1; `2026-10-20-math-extension-specs.md` §1, §5; `2026-10-20-math-extension-specs-2.md` §1, §5 | P |
| T13 | Same estimands, rules, levels and thresholds; readings fixed before the runs; per-system only, no overall verdict | `2026-10-20-math-extension-specs.md` §5; DEC-0038 and addendum A1 (per-system-only branch) | P |
| T14 | Development ensemble on several development seeds; side by side, no aggregates; not a test | DEC-0037 item 4; WU-0026; schedule note O7 | P |
| T15 | Dysts is a public collection with forecasting benchmarks cited by v3 | v3 §1 and references (Gilpin 2023; Zhang & Gilpin 2026); `2026-10-20-researcher-dysts-extension.md` §0, §C.1 | P |
| T16 | Same equations, parameters equal up to rounding; exponent fields disagree, cause not found; no published Chua reference | researcher note §A.1, §A.3, §A.5, §F; promoted report §10 (lambda_max item) | P |
| T17 | Different units and metrics, no physics-based counterpart; not directly comparable; descriptive table in the appendix | researcher note §C.3; WU-0024 plan | P |
| T18 | Run dates, cross-check and regeneration, audits, promotion | manifest lines of 2026-10-20 and 2026-10-23; promoted report §2, §9; audits `2026-10-21-audit-pre-promotion-conf1.md`, `2026-10-22-audit-promotion-conf1.md` | Q |
| T19 | One development seed per extension system, no replicate | schedule note O3 | P |
