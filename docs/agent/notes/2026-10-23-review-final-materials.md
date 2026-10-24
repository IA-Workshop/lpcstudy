# WU-0025.6: independent review of the final 10/28 materials (statement v3, poster outline v3, standalone appendix A, Dysts and Chua notes)

## Review

- **Reviewer:** `reviewer`, claude-opus-5-5, fresh context, 2026-10-23.
- **Scope.** On `develop` at 11bfe74 (the merge of `wu/statement-v3`):
  - `2026-10-23-research-statement-v3.md` and `2026-10-23-poster-outline-v3.md`;
  - `2026-10-23-appendix-a-standalone.md`, with its trace and sources;
  - `2026-10-23-math-benchmark-mapping.md` and `2026-10-23-math-chua-attribution.md`;
  - `2026-10-23-researcher-dysts-tables.md` and `2026-10-23-researcher-dysts-lyapunov-script.md`;
  - `2026-10-23-extension-ensemble-summary.md`;
  - for item 8 only, `2026-10-20-researcher-dysts-extension.md` §C.3 and `2026-10-20-math-extension-specs.md` line 198.
- **Governing texts:**
  - DEC-0037, DEC-0038 (with addenda A1 and A2), DEC-0042, DEC-0044 and DEC-0045;
  - ROADMAP.md §8 and the WU-0025 unit file (criteria E1 to E8, the definition of done, owner checkpoint D5);
  - `promoted/CONF-1/report.md` §§2 to 5 and §10, and `runs/confirmatory/run-1/full/results.json`, both read-only;
  - `docs/study/proposal_and_methods_v3.md` §§2, 4, 6 and 8, and the theorem-program errata of 2026-10-21;
  - the ledger, read-only: seq 13, 15, 20, 36 and 40.
- **Nothing edited** except this file. The ledger, the sealed files and the promoted files were not touched.

### Log

- **Tests: none.** These are documents only: no file under `lpcstudy/` or `tools/` changed in the reviewed merge, so the blast radius is empty.
- **The one command run, once:** `python3 -I tools/findings_build.py check docs/agent/notes --stem 2026-10-23-appendix-a-standalone`, with the project venv on PATH. Result: `Check passed: 1073 traced values, 0 problems`, exit 0. Nothing was re-rendered, and `git status` stayed clean.
- **Read-only checks:**
  - The verdict words were compared three ways: statement and poster, report §4, and `results.json` `verdicts.<H>.verdict` and `by_system`. They are H2a not supported (fail, fail, fail), H2b supported (pass, pass, pass) and H3c inconclusive (inconclusive, pass, inconclusive). The secondary words H2c inconclusive, H2e supported, H3a inconclusive and Q-N "estimate" also match, and the gate passed on all three systems. **All of these match.**
  - None of the 18 sealed primary estimates (report §5) appears in the statement, the poster outline or the appendix (grep of ten of them, 0 hits).
  - The banned words were grepped over the bodies of the statement (lines 26 to 130) and the poster outline (lines 22 to 90). The only hits are the allowed negations and one "confirm" used of the checks (R7).
  - The V3 code was read: `experiments.py` line 428 passes θ = 0.4, and `validation.py` line 357 gives `err = cp_err - noise * verify_unit`, which is the error against the noisy verifying observation. v3 §6 "Horizons" (line 317) states that convention, so the statement's V3 sentence is correct in substance.
  - Ledger times:
    - seq 13, the CONF-1 commitment: 2026-10-19T08:32:50Z, before the run started at 08:38:31Z;
    - seq 20, the release to agents: 2026-10-20T08:43:08Z;
    - seq 40, the promotion.
  - The network log on `main` (415 entries up to 2026-10-23) was searched for the sealed V3 triple: 0 hits.
  - `git remote -v` is empty, so no remote is configured.

### What is right (no finding)

- **Verdict words and PROVISIONAL.**
  - Every verdict word in the statement and the outline matches the promoted report and `results.json`.
  - "All three studied systems passed the validity gate" is correct.
  - For the extension, both documents say exactly that only S1 `rossler_hyper` passed and that S2 to S6 failed V7 and are PROVISIONAL. This agrees with the appendix A.2 gate table and its "Marked in this part" line.
  - Neither document gives an overall verdict or a ranking for the extension systems.
- **Promotion and dates.** The promotion label follows DEC-0045. "UNPROMOTED" and "v4" appear only in the change tables, the must-not-say lists and the checklists. The dates in §10 match the provenance (run-1 2026-10-19; GPU cross-check and run-2 2026-10-20).
- **Ruled limitations that are present and not weakened:**
  - DEF-0022;
  - the same-host regeneration, worded as determinism and not an independent reproduction;
  - the code review: waived, results spot-checked, code covered by agent reviews;
  - the figure captions and the R3 reference line;
  - "a subsequent pre-registered study … different intervals and sample sizes", against seq 36's "different intervals/dataset size". The gaps are in R3.
- **F5.** The text claims only what the records show: seed commitment seq 13 came before the run, the freeze check passed, and DEC-0001 holds. It does not say "never seen".
- **P1 bound.** "At most half an error-doubling time under the stated conditions" agrees with the errata L7(ii) and P1(d) (ln 2/(2Λ̄)).
- **Standalone appendix.**
  - Every table is headed with the development label and its seed ids.
  - A.2 says "per-system only, no overall verdict".
  - No sealed value appears.
  - `check` passes as above.

### Findings

**R1 (major): criterion E8 is not met and was redefined in the draft.**
- **Where:**
  - `2026-10-23-research-statement-v3.md` line 108 contains "2.85" and "0.4". Line 102 says the section has "no digit except in system names and the one ratio of tag U9".
  - Line 5 calls the remaining digits "design constants of v3".
  - Checklist line 162 is ticked with the same carve-out.
- **Why it matters:**
  - WU-0025 criterion E8, fixed in advance, reads "No digit in the new statement paragraph, except system names such as 'Lorenz-63'." The draft adds two exceptions of its own and ticks the item. That is a criterion loosened after the fact (PRIME.2, LPC.PC.21).
  - Line 5 is also wrong about 0.4. 0.4 is not a v3 design constant: v3 §6 does not state θ for V3, and 0.4 is outside the v3 set θ ∈ {0.1, 0.2, 0.3, 0.5} (mapping note F1).
- **Fix:**
  - (a) Make the Chua sentence number-free, using the attribution note's own wordings (§5 number-free variant, or the DEC-0010 wording "about three times larger"). This also settles open item 3 and avoids the snapshot dependence of the ratio (R2).
  - (b) The statement quotes no V3 value. So move the V3 definition sentence (tag U17) to the panel 12 and handout caption, where V3 values do appear (R4). The other route is to keep it in words and obtain a recorded owner exception to E8 (a decision entry). The draft must not grant the exception itself.
  - (c) Correct line 5 and checklist line 162 to match.

**R2 (major): the Chua and Dysts sentences are stale against the researcher's script note, and one exclusion is too broad.**
- **Where:**
  - statement line 108 (the two U9 sentences) and trace row U9 (line 186);
  - poster outline line 73 (D3) and trace row PO21.
- **Why it matters:**
  - **Stale provenance.** Both drafts say `2026-10-23-researcher-dysts-lyapunov-script.md` "is not on develop (checked at cc27d31), so nothing more is said". The note has been on develop since a35d0aa, before the merge of these drafts (11bfe74), so U9 and PO21 now state a false provenance.
  - **The note's finding is missing.** The stored `maximum_lyapunov_estimated` field most probably comes from Dysts' naive estimator: a single pair of trajectories, the slope of log-separation, no renormalisation. That is an inference from an older Dysts results file (Chua 1.189) and a commit that updated both files together. No Dysts text states it (script note §4, unconfirmed item 1). Why that estimator gives a larger value is not shown (§4, item 4).
  - **The exclusion is too broad.** "We tested and excluded differences of … integration settings" goes further than the attribution note. That note excluded the settings of our own Benettin/QR method and a replica of Dysts' spectrum recipe (§3, rows 4a to 4e and §5: "Benettin setting"). It did not test the integration or fit settings of the estimator now thought to have written the field (Radau, fit window, no renormalisation). Its §5 says explicitly that "whether it comes from a different estimator … is open".
  - **The factor depends on the snapshot.** The stored field changed over time: the 2023 naive value 1.189 gives a ratio of about 2.76, and today's JSON 1.230 gives about 2.85 (script note §3).
- **Fix.** In the statement, replace the two U9 sentences with something like:

  > "The Dysts database's stored maximum Lyapunov exponent for Chua is about three times ours, and our value is reproduced by an independent implementation. The stored value was probably produced by a simpler Dysts estimator that follows the separation of two nearby trajectories without renormalising it; this is our inference from Dysts' published code and an older results file, not something Dysts states, and why that estimator gives a larger value is not shown. Differences of equations, parameters, time unit, attractor and the settings of our own exponent method were tested and excluded, and Dysts' own spectrum entry for the system is near our value; no published reference value exists for Chua at our parameters, so neither Dysts number validates ours."

  Then:
  - use "independent implementation" (the attribution note's term) rather than "estimator";
  - make the same change to poster D3, where the ratio may stay as a number only if the owner chooses;
  - update U9 and PO21 to cite the script note §§2 to 4 and drop the "not on develop" clause.

**R3 (major): limitations missing from statement §8, and G3 missing from poster panel 9.**
- **Where:**
  - statement lines 87 to 98, with the claims "tags S34 to S39" and checklist line 163 ("§8 has every ruled limit");
  - poster outline line 59 (panel 9).
- **Why it matters.** Three limits are missing. The promoted report §10, DEC-0044 ("ruled limitations carried by the promoted report") and v3 §8 all carry them:
  - (a) **NVVUQ.22 gap G3.** The status wording of the secondaries does not say whether a secondary is confirmatory in this run. The statement (line 96) and panel 9 give only G1 and G2, but the owner accepted G1 to G3 (seq 36, DEC-0042 item 4).
  - (b) **Iterative error of PLP (DEF-0027).** v3 §8 lists it among the limitations stated in advance, and the report §10 and DEC-0044 carry it: it is not estimated for the sealed run, and on DEV-0 it was not shown negligible for 13 of 18 primary parts. The statement omits it; v1 trace S39 had it, but v3 kept only the coverage half. Poster panel 9 covers it only through the v1 list.
  - (c) **H2e was added after the pilot showed the effect** (v3 §2, line 105; v1 tag S37). It is dropped from §8, while the optional §7 line still offers "H2e supported" as a highlight.

  The claims that the tags run from S34 to S39 and that every ruled limit is present are therefore not true.
- **Fix:**
  - Add three bullets to statement §8:
    - G3, in plain words;
    - "the error left by the fixed number of fitting steps in the physics-based forecaster was not estimated for the official run";
    - "H2e was added after the pilot showed the effect and is tested on fresh seeds".
  - Add G3 to panel 9.
  - Re-tick checklist line 163 with evidence.

**R4 (major): V3 is quoted in appendix A without θ = 0.4 σ_x or the noisy verifying target.**
- **Where:**
  - `2026-10-23-appendix-a-standalone.md`, lines 41 to 51 (A.1) and 186 to 193 (A.2). The column header is "CP median VPT (V3, reported, no bar)".
  - Poster outline: lines 71 and 72 (D1, D2) carry no such caption, and the rule sits only under D3 (line 73). Checklist line 115 is ticked.
- **Why it matters:**
  - Panel 12 and slides A1 and A2 take their tables from appendix A. These are the only places in the 10/28 materials where V3 values are printed, and there neither the threshold nor the target is stated.
  - The mapping note F1 and F4 require both wherever V3 is quoted, as does the brief for this review. The threshold matters because 0.4 is not in the v3 θ set; the target matters because V3 is the one quantity scored against the noisy observation, not the noise-free truth.
- **Fix:**
  - In poster panel 12, under D1 and D2 and on slides A1 and A2, add a fixed caption sentence: "V3: the analog forecaster's valid-prediction time, the first step at which its error against the noisy verifying observation exceeds θ = 0.4 σ_x, Kaplan–Meier median in Lyapunov times; reported, not gated."
  - Alternatively, add the sentence to the appendix template in `tools/findings_build.py`. That is a tool change: E1 regression and a re-review.
  - Re-tick checklist line 115 only after one of these.

**R5 (major): an intent claim ("we chose them because") with no record.**
- **Where:**
  - statement line 56 ({U6});
  - poster outline line 48, "Reason (F2 resolved)", and the what-changed rows that call F2 resolved.
- **Why it matters:**
  - The drafts' own analysis (statement §A, F2, and open item 1; poster O3) says that v3 records only "exact models". The second reason is a description of the v3 table, and "we chose them because" is a claim about intent that only the owner or the student can confirm.
  - DEC-0045 applied the listed recommended answers. Its list (item 2) does not include the intent behind the choice of systems, and the owner said no further answers would come ("no further bureaucracy is needed from me").
  - So the submission text must default to the wording the records support. Unrecorded intent stated as fact is an unsupported claim.
- **Fix:**
  - Statement: "The design uses them because their equations are exact (v3 §4). They are also standard chaotic systems that forecasting benchmarks use, and they differ in shape and in how fast errors grow; Chua's has a piecewise-linear part." Keep the student slot for their own reason.
  - Poster: label panel 4 "Why these systems (exact equations: v3; the other two: description)".
  - Mark F2 "resolved as description; intent unconfirmed".

**R6 (minor): §8 attributes "real measured data" to v3's future work.**
- **Where:** statement line 85, "…; v3 lists these as future work".
- **Why it matters.** v3 §8 "Future work" lists a misspecified physics model, transfer to a higher-dimensional system and independent trajectory replicates (lines 398 to 400). It does not list real data. The draft's own §A F9 says that item was added from v3 §4 "All experiments are simulations".
- **Fix:** "v3 lists the first and the third as future work; every series here is a simulation (v3 §4)."

**R7 (minor): four glosses that misstate the technical content.**
- **(a) Line 74.** The H2a pre-registered reading "instability enters the weight through uneven starting errors" stands for v3's "anisotropic seeds", which means direction-dependent, not of unequal size. Fix: "through starting errors that are larger in some directions than in others".
- **(b) Line 104.** V7 is called "the check that the state estimator reaches its theoretical accuracy floor". V7 tests that the realized estimation error matches its first-order prediction ρν: the median ratio and the median slope must lie in [0.9, 1.1] (v3 §6; ensemble summary §2). The accuracy floor is V2 (CRLB). Fix: "the check that the state estimator's error matches its theoretical prediction".
- **(c) Line 64.** "Seven checks (V1 to V7) confirm the numerical tools first": V3 has no bar, and "confirm" overstates what the checks do. Fix: "Checks V1 to V7 test the numerical tools first (V3 is only reported)."
- **(d) Line 48.** The observability bullet says "how well the hidden state can be recovered … (large when the measurements pin the state down poorly)". The size statement belongs to ν, a noise-amplification factor, and contradicts the phrase it qualifies. Fix: "how well the hidden state can be recovered from noisy measurements; it is measured by a noise-amplification factor that is large when the measurements pin the state down poorly".

**R8 (minor): two benchmark claims go beyond the mapping note.**
- **Where:**
  - statement line 108: "measures error, time and noise in different units" and "has no forecaster with known equations like PLP";
  - poster line 73: the second claim.
- **Why it matters:**
  - The mapping note rates noise as M13 "partly" for ZG26: level 10⁻² corresponds to ρ = 0.01 if two unconfirmed conditions hold. Gilpin 2023 has no noise. "Different units" is therefore not established.
  - M15 is limited to "the benchmark texts read".
- **Fix:** "measures error and time differently (noise is absent from the main benchmark and defined in a way not confirmed to match ours)" and "has no forecaster with known equations, in the texts we read".

**R9 (minor): the appendix A.2 label names WU-0021.2 for all six systems.**
- **Where:** `2026-10-23-appendix-a-standalone.md` lines 158 and 160 onward: "exploratory readings pre-specified in WU-0021.2". The wording is the fixed E7 sentence.
- **Why it matters.** It is true only of S1 to S3. The S4 to S6 readings were fixed in WU-0023.2 (`2026-10-20-math-extension-specs-2.md` §5, commit 8cbd373 at 2026-10-20 10:58Z), before the S4 to S6 runs (2026-10-21 08:00Z). The statement's "the readings were written down before any extension run" is therefore supported, but the table names the wrong unit for half its rows.
- **Fix.** Add one line to panel 12 D2: "S4 to S6: readings pre-specified in WU-0023.2." The other route is to correct the template, which is a tool change with E1 and a re-review. The E7 sentence itself is the owner's to amend.

**R10 (minor; records; for the owner to know about): the sealed V3 triple sits in two development notes.**
- **Where:**
  - `2026-10-20-researcher-dysts-extension.md` line 157 (§C.3);
  - `2026-10-20-math-extension-specs.md` line 198;
  - repeated in `2026-10-23-math-benchmark-mapping.md` F2 (line 221), which says the values "match no V3 leaf read here".
- **Facts:**
  - 1.97, 3.43 and 2.8 are the CONF-1 run-1 leaves `systems/<s>/validation/cp_median_vpt_lyapunov` (1.9667, 3.4333, 2.8), rounded exactly as RESULTS.md line 312 prints them. No development run or v1 pilot stores these values (DEV-0: 2.1, 3.2667, 2.9667; v1 pilot: 2.0333, 3.5333, 2.7).
  - The researcher note was committed at 0945504 (2026-10-20 09:49Z). That is after the release to agents, seq 20 at 08:43Z, and after the sealed outputs were committed (e754601, 08:41Z).
  - The researcher note itself says "I did not read `runs/confirmatory`", so the values reached it by another path, most likely the dispatch text or the preliminary findings. The path is not recorded.
  - The values carry a wrong definition: "error above 0.2 of the attractor scale". The code uses θ = 0.4 σ_x against the noisy observation.
  - The specs note (line 198) proposed quoting them "descriptively" in the benchmark comparison.
  - No remote is configured, and the network log shows no web query carrying them.
- **Ruling (reviewer's reading).** This is **not a breach of access**: seq 20 released the CONF-1 outputs to agents. Nor did the values leave the owner, the student and the agents before promotion, so **D5 was not breached**. It is a **deviation of purpose and labelling**:
  - Seq 20 released the outputs "for the UNPROMOTED preliminary findings".
  - Two development planning notes used the sealed values unlabelled, misdefined and without a source, contrary to the rule that sealed and development numbers are never set side by side or mixed (D4; DEC-0037 item 1).
  - Promotion (seq 40) now allows the values to be quoted under the promoted label, so no confidentiality harm remains.
  - The risk is reuse: the triple sits in development notes beside development V3 values (DEV 2.0 to 3.3).
- **What must be done (main session; append-only, PRIME.5):**
  - (i) Append a dated correction to each of the three notes. It should say that the triple is the sealed CONF-1 V3 (θ = 0.4 σ_x, noisy target, ρ = 1 %, N_lib = 10⁴; promoted report §3), not a development value; that the "0.2" label is wrong; and that it must not be reused or set beside development values.
  - (ii) Add a short entry in `docs/agent/records/incidents.md` recording the deviation of purpose and the unrecorded source path. The owner decides whether anything more is needed.
  - (iii) The 10/28 materials need no change beyond keeping the existing "must not say" items: neither draft uses the values.

### Notes (not findings)

- **Poster checklist line 111.** It can now be ticked for `check`: the command above passed with 1073 traced values and 0 problems.
- **D5.** It is satisfied for both drafts: they quote no sealed number, and the result words come from the promoted report.

### Verdict

**Changes required.** There are 10 findings: 5 major (R1 to R5) and 5 minor (R6 to R10), and no blockers.
- No verdict word or sealed number is wrong.
- The major findings concern a criterion loosened by the draft (R1), a stale and over-broad Chua sentence (R2), ruled limitations left out (R3), V3 printed without its definition on the handout (R4) and an unrecorded intent claim (R5).
- R1 and R4 can be fixed without any tool change: move the V3 definition to the panel 12 caption and make the Chua sentence number-free.
- R10 needs the main session's append-only record actions and owner awareness, not a change to the materials.
- **Owner checkpoint.** These are documents only, with no change to verdict, statistics, seed, provenance or dependency code, so no owner code review is triggered. Two items do need the owner: R1(b) if the owner prefers an exception to E8, and R10 for awareness.
