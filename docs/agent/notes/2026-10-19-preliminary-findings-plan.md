# Preliminary findings and data presentation: plan (WU-0020)

Planner claude-opus-5-5, 2026-10-19, from `develop` 044dae2. Owner's instruction, verbatim: "Once the CPU and GPU initial confirmatory runs are complete, we need to coalesce around a preliminary findings document and present the data. Plan out how to do this." The unit file is `docs/agent/records/work/WU-0020-preliminary-findings.md`; it holds the acceptance criteria (fixed, VV.3). This note gives the detail an executor needs. No sealed output was read for this plan; the stand-in is DEV-2 (R6 CPU, R5 GPU).

## 0. Where this sits

- **WU-0020 is the narrative layer and its tooling.** It comes before WU-0017, which is the v3 report after regeneration. WU-0017.1 still produces `RESULTS.md` by `--report-only`. WU-0020 adds a short document that a human can read, three figures with intervals, and a build that traces every number. WU-0017 and WU-0018 then reuse the same build on the promoted run.
- **Nothing in `lpcstudy/` changes.** The frozen package (`freeze-1`) is untouched. All new code is in `tools/findings_build.py`, which reads `results.json` and the `compare_runs` text. It computes no statistic and no verdict, so it is not a change to the frozen configuration (LPC.PC.8).
- **Governance limit, stated up front.** QA.11 says: "A result SHALL NOT be reported before promotion … Reporting an unpromoted result, or relying on one beyond its author, is a blocking defect." Until WU-0018.3, the preliminary document is internal: the owner and the student only (WU-0017.3). Showing sealed numbers to judges before promotion needs promotion first, or an owner ruling (decision D5).

## 1. Readers and deliverables

| Reader | Needs | Gets |
| --- | --- | --- |
| Owner (Brian, PI) | Every verdict and gate outcome, what is still open before promotion, and the decisions to take | The full preliminary document and the owner-decision list (section 7) |
| Student (Deem, author) | What came out, stated plainly enough to interpret in their own words (v3 §9 roles: the student does the interpretation and the presentation) | The same document; the section "what it means" is a prompt sheet with no agent prose |
| Judges (after promotion only) | The question, the method, one honest picture of the result, and its limits | The poster (or slides) and the one-page summary |
| Later paper | Traceable numbers, provenance and limitations | The trace file and the build script, reused by WU-0017 |

The deliverables are sized for the deadline:

| # | Deliverable | Home | Size | Built by |
| --- | --- | --- | --- | --- |
| P1 | Preliminary findings document | `docs/study/preliminary_findings_conf1.md`, written by the main session (agents do not write `docs/study/`) | About 6 pages of prose plus generated tables | Script for tables, numbers and verdict sentences; hand for the frame; the student for the interpretation |
| P2 | Trace file | `docs/study/preliminary_findings_conf1.trace.csv` | One row per quoted number | Script |
| P3 | Figures | `docs/study/figures/conf1/` | The 4 existing PNGs plus F1 to F3 below | Script |
| P4 | One-page summary | `docs/study/preliminary_summary_conf1.md` | One page | Script plus hand (number-free frame) |
| P5 | Poster outline, with the slide variant | `docs/agent/notes/2026-10-xx-prelim-poster-outline.md` | 1 to 2 pages | Hand: student and planner; number-free until promotion |

**Figures.** `lpcstudy.report.make_figures` already produces four. Their captions say "no confidence interval is shown", which is correct for what they are: context, not verdicts.

| Figure | v3 identifier | Status |
| --- | --- | --- |
| `separation_weight_vs_horizon.png` | E4, H2a context | exists |
| `kaplan_meier_by_rule.png` | E4/E5, H2c and H3a context | exists |
| `regret_vs_regimes.png` | E5, H3c context | exists |
| `knob_response_library.png` | E2, H2b(ii) context | exists |
| **F1** Primary forest plot: 18 parts (H2a(i), H2a(ii) zero, H2a(ii) interior, H2b(i), H2b(ii), H3c × 3 systems); estimate and the 98.33% interval against the shaded band; verdict shown by marker shape and a text label | E1, E2, E4, E5; H2a, H2b, H3c | **missing** (the main figure) |
| **F2** Secondary forest plot: H1a to H1d, H2c to H2e, H3b, with 95% intervals; Q-N against its reading table | E2 to E5 | **missing** |
| **F3** GPU cross-check: z_away per primary part, with the 3.4 line, titled "information only" | none (v3 §9 item 3, DEC-0031) | **missing** |
| F4 Schematic of CP, PLP, the four conditions and w\* | none | hand-drawn by the student; no data |

Optional, only if time allows: a noise-knob panel for H2b(i) from `H2b.noise.median_w_by_noise` (medians, labelled "no interval").

**Out of scope:**
- any new statistic, criterion, threshold, post hoc subgroup or "trend";
- recomputing a verdict;
- any change in `lpcstudy/`;
- a new run on any seed (no DEV ensemble; see D4);
- figures for removed experiments (shift, transfer, Lorenz-96, A4f);
- the paper itself;
- the promotion (WU-0018) and the regeneration (WU-0016), which are only sequenced here.

## 2. Honesty and status rules (the build enforces them)

1. **Banner.** Line 1 is the label the code prints, `**CONFIRMATORY: UNPROMOTED**`, copied from `provenance.label` and not typed by hand. Line 2 reads `PRELIMINARY: internal to the owner and the student until promotion (QA.11, LPC.PC.13).` The dry run prints `**DEVELOPMENT (DEV-2): not a hypothesis test** · **UNPROMOTED**` instead.
2. **Five source tags, one per section.** The build binds each placeholder to one named source and refuses a mismatch. For example, a `[PRE-REGISTERED]` section cannot quote the GPU file or a DEV file.

   | Tag | Source | May contain |
   | --- | --- | --- |
   | `[PRE-REGISTERED]` | the official CPU `results.json` (CONF-1) | verdicts, intervals and gates, read from the file |
   | `[CROSS-CHECK: information only]` | the GPU `results.json` and the `compare_runs` TD text | z per part, the GPU gate, the count of differing verdict-type leaves; the sentence "changes no verdict (DEC-0031)" |
   | `[DEVELOPMENT]` | the DEV rehearsal report and DEV-0 LM study | precision and reproducibility context only, in an appendix |
   | `[DIAGNOSTIC]` | handling counters, LM diagnostics, P2(c), λ_max | counts and readings, no verdict |
   | `[STUDENT]` | none | interpretation; no new numbers |
3. **Verdict statements.**
   - **Overall rule**, quoted from v3 §7: supported iff pass on all three systems; not supported if any system fails; inconclusive otherwise, including a system with no result. Then the intersection–union sentence, and the sentence that the error of "not supported" is not controlled this way (about 7.3%, about 14% for H2c).
   - **Each of the 14 rows** (H1a to H3c, Q-N and the reported gain bound) is shown with:
     - the per-system verdict (`verdicts.<id>.by_system`) and the overall verdict;
     - the estimate and interval, at the level stored in the leaf;
     - the band, with its strict or closed form;
     - the interval label (procedure, level, dependence, multiplicity; copied from `RESULTS.md`);
     - the `clip` column.
   - **Each of the 18 primary parts** additionally shows:
     - the LM row "not estimated", with a pointer to `lm_doubling_dev0_report_v3.md` (DEC-0024 A3);
     - the block-sensitive label status (see D6).
   - **Special rows:**
     - Q-N is a reading from the §7 table, never pass/fail;
     - H3a "cannot fail", and shows events and censored states per regime (DEF-0018);
     - the gain bound is "reported, v1 statistic, v3 screen pending" (DEC-0033 M3).
4. **Gate V1 to V7 per system,** with each statistic (V6 `integrator_max_dev_sigma`, V4 half-width). A failing system's rows carry `PROVISIONAL` in every table and figure (v3 §6 E0).
5. **Handling counters (PRIME.4).** Run totals, nonzero per-system counters and `failed_variants`, from `handling`. Zeros are stated as 0, never omitted.
6. **Limitations section (mandatory items).** Each v3 §8 item, plus:
   - DEF-0020: block-5 undercoverage, 0.923 to 0.947;
   - DEF-0026: per-seed V6/V4 gate risk;
   - DEF-0018: small H3a regimes;
   - DEF-0027: LM flag on 5 of 18 parts, development evidence;
   - DEC-0033 M2: bitwise agreement at full size is extrapolated;
   - DEC-0033 M3: the gain bound is reported only;
   - one realization per system;
   - the block-sensitive label not computable for the sealed run (D6).
7. **Language.**
   - **Banned in `[PRE-REGISTERED]` sections:** "proves", "confirms", "significant", "shows that", "demonstrates", "breakthrough". The build greps for them, case-insensitive.
   - **Required forms:**
     - "inconclusive" is never written as "no effect";
     - "not supported" is never written as "disproved";
     - "supported" carries "(preliminary, unpromoted)".
8. **Branches** (number-free templates, written now; section 4 item W):
   - **Supported, not supported, inconclusive:** one template each, per row and overall.
   - **Not supported:** the pre-registered reading of the failure from v3 §7 is quoted where one exists (H2a, H2c with A4o, H3c).
   - **Gate failure (V4 or V6, or any V):** the document is still built. The system is marked PROVISIONAL and its verdicts are computed and shown (E0). A boxed line says the result is referred to the owner (DEC-0027, DEC-0031) and that nothing proceeds to promotion until the owner rules.
   - **GPU disagreement:** a failing TD part, a differing verdict leaf or a GPU gate failure is reported in the cross-check section only, with "changes no verdict".

## 3. Pipeline: from run directories to document

| Step | Input | Tool | Output | Script or hand |
| --- | --- | --- | --- | --- |
| a | Released CPU `runs/confirmatory/run-1/full/results.json`, read at the WU-0015.3 commit with `git show <c>:<path>` | `python -m lpcstudy --preset full --out <copy> --report-only` (already produced by the run) | `RESULTS.md` and the 4 figures | script (existing) |
| b | The CPU and GPU run directories | `python3 tools/compare_runs.py <cpu_run_dir> <gpu_run_dir>` (the official run is the reference, as in the stored record `WU-0003-9c-compare-R5R6.txt`, which took run directories) | `docs/study/conf1_cpu_vs_gpu_td.txt` (tier TD) | script (existing) |
| c | Step a, step b, and the template `tools/findings/preliminary.template.md` | `python3 tools/findings_build.py render --official <cpu> --crosscheck <gpu> --td <txt> --release-ref <ledger seq> --out <dir>` | P1, P2, F1 to F3 | script (new) |
| d | Output of step c | `python3 tools/findings_build.py check <dir>` | Exit 0 or the list of untraced or mismatched numbers | script (new) |
| e | Frame, wording templates, student's section | hand | template text | hand (number-free) |

**Placeholders and the check.** A number enters the text only through a placeholder `{{official:systems/chua/H3c/ci/1|.3g}}`, which names a source and a leaf path. `render` writes P2 with one row per placeholder: the section tag, the source, the leaf path, the raw value as `repr(float)`, and the rendered string. `check` fails on any of these:

- a placeholder that does not resolve;
- a rendered string that does not equal the formatter applied to the leaf (exact string match);
- a source not allowed by the section tag;
- a numeral in the text that comes neither from a placeholder nor from `tools/findings/design_constants.json`. The allowlist holds the v3 constants (0.1, 1.05, 0.7, 0.8, 1.2, 0.05/3, 3.4, 2.394 and so on), each with its v3 section;
- a banned phrase;
- a missing banner.

Verdict words come from `verdicts` and from the part `verdict` leaves. The tool imports no verdict function (`statistics.criterion_verdict`, `combine_verdicts`, `overall_verdict`) and never compares an interval with a band.

**Provenance section** (generated):
- commit, which must equal `git rev-parse freeze-1^{commit}` (U1);
- `seed_id` CONF-1 and `seed_kind`;
- `device.backend`, `env.LPC_THREADS`;
- `dirty`, `complete`, `wall_seconds`, `start_utc`/`end_utc`;
- the SHA-256 of each `results.json`, equal to the manifest row of WU-0015.3;
- the ledger sequence of the release.

The build refuses a `results.json` whose `seed_kind` is confirmatory unless `--release-ref` is given; the value is printed in P1.

## 4. Now, before any sealed output exists (the critical path)

The sealed runs use the CPU (about 4.7 h, R6 measured 17 031 s) and then the GPU (about 0.8 h). Work for this unit runs alongside them under these rules:

- unit tests and renders under `nice -n 19` with `LPC_THREADS=1`;
- no `python -m lpcstudy --preset …` while `pgrep -fa "lpcstudy --preset"` shows the sealed run (this keeps the WU-0015.1 condition "no other preset run" literally true). In the dry run, `findings_build.py` calls `report.write_markdown` and `report.make_figures` in-process on a scratch copy instead;
- nothing on the GPU.

| Sub-task | What | Owner | Effort | Depends on |
| --- | --- | --- | --- | --- |
| WU-0020.1 | Skeleton template (section list below), `design_constants.json` (each constant with its v3 section), wording templates W for the 3 branches plus the gate and GPU branches, number-free | planner drafts, owner and student review wording | 2 h | — |
| WU-0020.2 | `tools/findings_build.py` (`render`, `check`, F1 to F3) and `tests/unit/test_tools_findings_build.py` | developer | 4 to 5 h | .1 |
| WU-0020.3 | Dry run on DEV-2: R6 (CPU) as the "official" source and R5 (GPU) as the "cross-check" source, scratch copies under `runs/dev/prelim-dryrun/`; `compare_runs` R6 against R5; render and check; dry-run document committed as `docs/agent/notes/2026-10-xx-prelim-findings-dryrun-dev2.md`, labelled DEVELOPMENT | developer | 1 h (CPU seconds) | .2 |
| WU-0020.4 | Independent review of .2 and .3 (`/independent-review`) | reviewer | 1 h | .3 |
| WU-0020.5 | Poster outline and slide variant, number-free, with figure slots F1 to F4; figure and table checklist | student with planner | 2 h | .1 |
| WU-0020.6 | Merge to `develop` (merge gate, unit tier radius only) | main session | 0.5 h | .4 |

**Sections of P1:**

| § | Section | Tag |
| --- | --- | --- |
| 0 | Banner and status | — |
| 1 | The question (from the v3 Summary; no new claims) | — |
| 2 | What was run (provenance) | — |
| 3 | Validation gate | `[PRE-REGISTERED]` |
| 4 | Overall verdict table (14 rows) and the decision rule | `[PRE-REGISTERED]` |
| 5 | The three primaries: 18-part table and F1 | `[PRE-REGISTERED]` |
| 6 | Secondaries, Q-N reading, H3a counts and F2; gain bound reported | `[PRE-REGISTERED]` |
| 7 | Handling counters | `[DIAGNOSTIC]` |
| 8 | GPU cross-check and F3 | `[CROSS-CHECK]` |
| 9 | Reproducibility: regeneration (WU-0016) pending or done | — |
| 10 | Limitations | — |
| 11 | What it means and does not mean | `[STUDENT]` |
| A | Development context | `[DEVELOPMENT]` |
| B | Interval labels | — |
| C | Trace summary | — |

Total before release: about 10 to 11 agent hours. Sub-tasks .2, .3, .4 and .6 are the critical path; .5 runs in parallel.

## 5. After the sealed runs finish, in order

| # | Step | Who | Gate |
| --- | --- | --- | --- |
| 1 | CPU run (WU-0015.2), then GPU cross-check (WU-0015.2b) | owner, under the per-action authorizations | — |
| 2 | Owner looks first, at the header, the gate line and `complete`/exit only. No editing or filtering of outputs | owner | **Release decision (WU-0015.4)**, covering the CPU and GPU outputs together (DEC-0031 item 3) |
| 3 | Manifest row `unpromoted` (CONF-1, commit, configuration, environment, SHA-256); outputs committed under `runs/confirmatory/run-1/` and `run-1-gpu/` (WU-0015.3) | owner | before any agent reads them |
| 4 | Regeneration (WU-0016.2) starts on the CPU once the GPU run has finished; it runs about 4.7 h in parallel with steps 5 to 7 | another actor | WU-0016.1 authorization |
| 5 | Build P1 to P4 from the committed outputs (steps a to d); commit on `wu/0020-prelim-findings` | main session | `check` exit 0 |
| 6 | Independent review of P1 against `results.json`, in a fresh context. The reviewer re-reads 20 randomly chosen trace rows from the JSON by hand, reads every claim and confirms none goes beyond a pre-registered test, the tags or the limitations | reviewer | zero open findings, or at most 2 fix rounds, then `/refer` |
| 7 | Owner and student read (WU-0017.3). The student writes §11; student interpretations are notes, not criterion edits (LPC.PC.2) | owner, student | — |
| 8 | Regeneration compared (WU-0016.3/.4): one dated line appended to P1 §9 | main session | — |
| 9 | WU-0017 (v3 report, reusing the build), WU-0018 (audit and promotion) | as ROADMAP | **Promotion (WU-0018.3)**. Only after this may P3 to P5 carry sealed numbers outside owner and student |

## 6. Presenting the data

**Story arc** (poster panels, or about 10 slides):
1. The question.
2. The two forecasters (CP copies an analog; PLP estimates the state and integrates).
3. The four local conditions and the blend weight w\* (P1: closed form, and at most half a doubling time of gain).
4. The three systems.
5. Pre-registration and the sealed seed: why the rules were fixed first.
6. The three primary verdicts (F1).
7. Secondary highlights (F2, a selection fixed in .5 before release, not chosen after seeing the results).
8. What it means and does not mean (student).
9. Limits.
10. What next (v3 §8 future work).

**Figure rules:**
- Intervals are always drawn. The band is shaded and the level is written in the panel.
- One message per figure.
- Okabe–Ito palette, with the verdict also encoded by marker shape and a text label.
- Every caption names the experiment (E1 to E6), the v3 identifier and the interval procedure (WU-0017.2).
- PROVISIONAL in the panel title for a system that failed the gate.
- No point estimate without its interval on any verdict figure.

**Cross-check and DEV material:**
- The GPU cross-check appears only in F3 and §8, in grey, titled "cross-check, information only".
- DEV numbers appear only in Appendix A, as text, never on F1 or F2.

## 7. Risks and owner decisions (answer in one line each; default in bold)

1. **D1 Home and name.** **`docs/study/preliminary_findings_conf1.md` plus `.trace.csv`, written by the main session.**
2. **D2 Release.** The owner checks the header, gate and completion only, then releases the CPU and GPU outputs together, **as soon as both finish**.
3. **D3 Wait for regeneration?** **No.** Build in parallel. §9 says "regeneration pending" and gets a dated line after WU-0016.4.
4. **D4 DEV numbers beside the sealed result.** **No.** Appendix A only (precision and reproducibility context, labelled). **No new DEV ensemble before the fair** (post hoc and contends for compute).
5. **D5 Science fair before promotion.** QA.11 makes showing unpromoted results to judges a blocking defect. **Promote first** (WU-0016 → WU-0017 → WU-0018). If the fair comes first, show the design, the theorems and the method with "results under verification" and no sealed numbers, or record an explicit owner ruling. The fair's date and rules are needed (researcher question).
6. **D6 Block-sensitive label.** v3 §8 promises it, but `tools/rehearsal_diagnostics.py` needs a states dump, and the sealed run writes none (the CLI refuses `--states-dump` with the confirmatory flag). **Report "not computable for the sealed run" as a limitation; no extra sealed-seed run.**
7. **D7 Gate failure in the sealed run.** **Build the document anyway, with the system marked PROVISIONAL and its verdicts shown (E0). Promotion halts until the owner rules (DEC-0027, DEC-0031).**
8. **D8 Authorship.** **Agents generate tables, figures and number-free templates. The student writes §11 and the poster prose. The AI-use statement (v3 §9) is updated by the student.**
9. **D9 Format.** **Tri-fold poster, with a 10-slide variant from the same figures.**
10. **D10 Secondary highlights on the poster.** **Fixed in WU-0020.5 before release: H2c, H2e, H3a, Q-N.**

**Risks:**
- R5/R6 predate the freeze code. The dry run must therefore expect "not recorded" for the H3a event lists and the leaves added after c9bb981; this is a known difference, not a bug.
- The `compare_runs` output may differ in leaf counts from the stored `WU-0003-9c-compare-R5R6.txt` (REF R5, NEW R6). The z values must not differ: z_away is symmetric when the two runs are swapped (d changes sign and the facing arms swap), and the 18 part leaves are the same inputs.

**Open questions for the researcher:** the fair's date, its rules on preliminary or unverified results, its AI-use disclosure rules, and the poster size limits.
