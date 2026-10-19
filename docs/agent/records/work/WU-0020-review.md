# WU-0020.4: independent review of WU-0020.1 to .3 (preliminary findings build)

## Review

- **Reviewer:** `reviewer`, claude-opus-5-5, fresh context, 2026-10-19. Branch `wu/prelim-review` from `wu/prelim-build` 8e08d3f.
- **Scope reviewed:** `tools/findings_build.py`, `tools/findings/preliminary.template.md`, `tools/findings/design_constants.json`, `tests/unit/test_tools_findings_build.py`, the DEV-2 dry run under `docs/agent/notes/` (document, trace, sources, F1 to F3, both compare_runs texts), against the plan (A1 to A13), the plan note, and v3 §2, §6, §7, §8 and §9.
- **Verdict:** **changes required.** There are 3 blocking findings, 9 should-fix findings and 3 notes.
- **Owner checkpoint:** yes. The tool reads released sealed outputs through the release guard (R5). It needs owner review before it is used on sealed outputs. No verdict, statistics, seed or provenance code changed. No dependency changed.

### What I ran (read-only on originals; scratch copies only)

All work ran under `nice -n 19` with `LPC_THREADS=1 OMP_NUM_THREADS=1 JAX_PLATFORMS=cpu`, on scratch copies in the session scratchpad. I edited no committed file and no original under `lpcstudy-wt/run/`. I did not rerun the unit test file, since I changed no code. I started no `python -m lpcstudy` process, used no GPU, and read nothing under `runs/confirmatory/`.

- **Inputs.** The scratch copies are byte-identical to the originals. The SHA-256 of the copies equals that of `run/r3r6-c9bb981/runs/r6-cpu-dev2/full/results.json` (official, 5e2eaf68…) and `run/r1-c9bb981/runs/r5-gpu-dev2/full/results.json` (cross-check, f0649d75…). The two `RESULTS.md` files are also equal.
- **Fresh render** from the scratch copies: `rendered d: 876 traced values, 30 leaves not recorded`, then `check passed: 876 traced values, 0 problems`. F1, F2 and F3 are byte-identical to the committed PNGs, from a different process and stem (A12 holds).
- **A10, recomputed independently.** My script reads the 18 primary leaves of both files and does not import `compare_runs`. It uses z_level = Φ⁻¹(1 − 0.05/6) = 2.3940 and the away arms. All 18 z_away and z_sym values equal the document. Totals: max z_away 2.26 (rossler H2b(i)), sum of z² away 15.77, max z_sym 2.32, sum of z² sym 16.45, 0 failing. A separate walk of the two trees with the verdict-type predicate of `compare_runs.is_verdict_str`, excluding provenance, finds 52 differing verdict-type leaves. The TD block of the R5-vs-R6 text is identical to the one in `WU-0003-9c-compare-R5R6.txt`.
- **Trace re-read by hand.** I re-read 24 random trace rows (seed 20261019) against the JSON leaves and the document position. All 24 agree: value, format, line and column. They cover the official, const, official_md, td and meta sources and the PRE-REGISTERED, DIAGNOSTIC and plain tags.
- **Constants against v3.** I checked these by hand against v3: all 6 primary bands, 14 secondary bands and 2 Q-N bands, and their strict or closed form (§2, §7). I also checked the gate bars V1 to V7 (§6), the levels 1 − 0.05/3 and 95% (§7), the bound 3.4 and z 2.394 (§9 item 3), "about 7.3%" and "about 14%" (§7), and the decision-rule wording (§7). All match. The only exception is the V7 statistic, which is incomplete (R9).
- **A3 (no recomputation).** I read the whole tool. Verdict cells are `fmt(leaf, "verdict")`, a copy of the stored word plus the required suffix. `wording_primary` is a dictionary lookup on the stored overall word. `wording_gpu` reads the TD tokens and the stored GPU `gate_pass`. `panel_data` plots stored floats. No interval is compared with a band, no verdict function is imported, and nothing is rounded before a decision. The only number not read from a source is the defaulted `differing` "0" (R7). **A3 holds.**
- **Perturbations.** I made about 40 edits to scratch copies of the document, the trace, the sources and the inputs. The tables below list the ones `check` misses.
- **Commits.** All three commits name the unit and carry `Agent: claude-sonnet-5-5` and a Co-Authored-By trailer. Black 26.10.1 at 80 columns reports both files unchanged. Nothing under `runs/confirmatory` or `docs/study/preliminary_findings_conf1.md` is in the branch (A13).

Edits that `check` catches correctly (exit 1, or exit 2 for input errors), each with a clear message:

- a changed quoted z value or verdict word;
- a wrong-source row for the PRE-REGISTERED, CROSS-CHECK, DIAGNOSTIC and plain tags;
- an edited results.json, which is refused with "changed since the build";
- a missing or altered PRELIMINARY line;
- a deleted PROVISIONAL mark on a `| chua …` row;
- a deleted PROVISIONAL mark in the verdict table, caught only through the column shift;
- a confirmatory file without `--release-ref`;
- a missing `seed_kind`;
- an official commit that is not freeze-1. This used the real tag: `git rev-parse freeze-1^{commit}` gives df8928f, and the DEV-2 commit 059dc84 is refused.

Edits that `check` misses, or inputs that `render` accepts (exit 0):

| Case | Edit or input | Finding |
| --- | --- | --- |
| P7 | GPU sentence swapped to `gpu_agree` while the data show the chua GPU gate failed and 52 verdict leaves differ | R1 |
| P8 | H2a sentence "Fail on at least one system" replaced by the "supported" sentence | R1 |
| Q9 | Decision rule edited ("fails on at least one" → "fails on all of three"), same length | R1 |
| Q9b, Q9c | A limitation softened to "resolved"; "H3a cannot fail" replaced by "H3a passed" | R1 |
| G4 | Gate box swapped to the all-clear text after a planted chua gate failure | R1 |
| P11 | DEVELOPMENT DRY RUN notice replaced by "Results of the study." | R1 |
| Q6a, c, d, f, g, j | Numbers hidden as `` `0.81` ``, "item 3.5%", ".003", "[rate](0.42)", "p_0.99", "n=x1000", "W-0.5" (the control "About 42 states." is caught) | R2 |
| M | chua removed from `systems` (still in `core_systems`): every chua column, row and TD row vanishes, 12 primary parts instead of 18, check passes | R3 |
| G2 | PROVISIONAL in the verdict-table cell blanked to spaces (same length) | R4 |
| G5, P12 | F1 replaced by a non-PROVISIONAL F1, or by F2 | R4 |
| H2 | `seed_id` CONF-1 with `seed_kind` development: rendered with no guard, under a CONFIRMATORY banner and a "DEVELOPMENT DRY RUN" notice | R5 |
| H3 | Confirmatory-labeled file passed as `--development`: its verdict words are printed in Appendix A as "Development seed numbers" | R5 |
| H1d | Confirmatory with `--release-ref x` and hashes typed from the files themselves: accepted | R5 |
| D | TD text without the "verdict-type leaves differ" line: the document says "0" | R7 |

### Findings

**Blocking**

- **R1. `check` does not verify the untraced frame, so a sentence that contradicts the stored data passes.**
  - **Where:** `tools/findings_build.py:1274-1294` (`run_check`), `:632-685` (`wording_primary`, `wording_gpu`, `gate_box`), `:775` (`mode_notice`).
  - **What happens:** the verdict sentences, the GPU agree or disagree sentence, the gate box, the mode notice, the decision rule and the limitations are inserted untraced. `check` only checks:
    - traced spans;
    - numerals;
    - the banner lines;
    - three required phrases;
    - limitation keywords.
  - **Failure scenario:** P1 is hand-edited after the build (the main session writes the frame, the student writes §11). Then "The cross-check changes no verdict… GPU gate passed on every system" can sit beside data showing a GPU gate failure, with `check` at exit 0 (P7, G4). The same holds for "Pass on all three systems" under a "not supported" word (P8), and for a weakened decision rule or limitation (Q9 to Q9c). The DoD evidence "check exit 0" would then certify a wrong statement.
  - **Fix:** in `check`, re-render from the template and the hashed sources. Rendering is deterministic (A12). Require byte equality of everything outside the body of the `[STUDENT]` section and an explicit append-only §9 slot. This closes the gap by construction, makes R4's G2 and G4 cases moot, and makes R2 matter only inside the free-text slots.
  - **Minimum alternative:** trace every wording, gate-box and mode-notice block as a row whose key is the stored token it was chosen by, and re-derive the choice in `check`.
  - **Test:** add a unit test with one swapped sentence per branch.
- **R2. The numeral scan has loopholes, so a number can hide behind a mask.**
  - **Where:** `tools/findings_build.py:66-69` (`NUMERAL`, `STRUCTURE`) and `:1196-1208`.
  - **What passes:** `` `0.81` `` (any backtick span without spaces), "item 3.5%" (`item \d+` masks "item 3", leaving ".5", which the lookbehind then ignores), ".003" (no numeral may follow "."), "[rate](0.42)" (any link target), and numbers glued to a word or a hyphen ("p_0.99", "x1000", "W-0.5"). Number words ("Forty-two percent") are also not caught; that one only needs saying in the docstring.
  - **Why it matters:** A2 says "every number in P1 … is either a placeholder … or a constant", and §0 of the document tells the reader so. Mechanically, that is not true.
  - **Fix:**
    - Exempt only identifier shapes: `H\d[a-z]`, `V\d`, `E\d`, `[A-Z]+-\d{4}`, `WU-\d{4}(\.\d+)?`, `r\d+` in the H3a regime column. Then let NUMERAL match a leading-dot decimal and a digit after `_` or `-` everywhere else.
    - Limit the backtick mask to spans containing a `/` or a letter, and the link mask to the `![F…](…)` figure lines the tool writes.
    - Change the `item` mask to `\bitem \d+\b(?![.\d])`.
    - Allow a § mask only on `§\s*\d+(\.\d+)?(?![\d%])`.
  - **Tests:** one test per loophole. `test_template_is_number_free` (`tests/unit/test_tools_findings_build.py:347-353`) uses the tool's own regexes and so cannot catch any of this. Give it an independent, deliberately stricter pattern.
- **R3. A system missing from the results is silently dropped, and the A4 completeness check is defeated.**
  - **Where:** `tools/findings_build.py:321-325` (`Builder.systems` keeps only the systems present in `systems`), `:1242-1246` (`check_text` uses the same filtered list).
  - **Failure scenario (case M):** chua is removed from `systems`. The verdict table has columns for lorenz63 and rossler only, the primary table has 12 rows, and the chua TD rows disappear from §8. Nothing reads "not recorded", nothing is counted, and `check` passes. v3 §7 names "a system has no result" as a case to report (overall inconclusive), and A4 requires 18 parts (3 × 6).
  - **Fix:**
    - Take the system list from a constant (the three v3 systems, cited to §4) and require `config/core_systems` to equal it.
    - Render every absent system's cells as "not recorded", counted through `ref`.
    - In `check`, require 3 × 6 primary estimate rows and 14 × 3 `by_system` rows.

**Should fix**

- **R4. PROVISIONAL is enforced only on lines that start with `| <system>`, and figures are not verified.**
  - **Where:** `tools/findings_build.py:1258-1264` and `:1285-1287`.
  - **Gaps:**
    - G2: a verdict-table mark blanked to spaces passes.
    - G5, P12: any PNG passes, including F2 copied over F1, or an F1 without the PROVISIONAL label. `check` only tests that the file exists.
  - **Fix:**
    - In `check`, require " PROVISIONAL" right after every `verdicts/*/by_system/<s>` span of a failed system.
    - Record the SHA-256 of each PNG in `sources.json` and verify it, or re-draw and compare (A12 makes this exact).
- **R5. The release guard is fail-open and partly self-referential.** This is an owner checkpoint.
  - **Where:** `tools/findings_build.py:1004-1031`, `:985-995`, `:1045`, `:1070-1073`.
  - **What I found:**
    - (a) The guard keys on `seed_kind` alone. `seed_id` CONF-1 with `seed_kind` development renders with no guard, a CONFIRMATORY banner and a "DEVELOPMENT DRY RUN" notice (H2).
    - (b) `--development` is never checked. A confirmatory file is accepted and printed in Appendix A as "Development seed numbers" (H3), which breaks D4.
    - (c) The manifest hashes are typed on the command line, not read from the WU-0015.3 manifest. An operator who pastes `sha256sum` of whatever file is at hand passes (H1d). The hash itself is not recorded; `sources.json` and the document carry only the words "equals the manifest row", and `check` takes those from `sources.json` without verifying them.
    - (d) `--release-ref` accepts any string ("x"), with no lookup in the ledger.
    - (e) The freeze-1 equality is now confirmed against the real tag: the DEV-2 commit is refused. The unit test still uses a stub.
  - **What is fine:** the tool never needs the sealed seed or the sealed-run flag. It reads only `results.json`, `RESULTS.md` and the TD text.
  - **Fix:**
    - Fail closed: accept a development run only if `seed_kind` is development, `seed_id` starts with "DEV-" and the label does not contain CONFIRMATORY. Otherwise take the confirmatory path.
    - Refuse a `--development` file that is not development.
    - Read the manifest row from the committed manifest file.
    - Check the release reference against the ledger (`tools/ledger.py`).
    - Store both the hash and the reference in `sources.json`, and re-verify them in `check`.
- **R6. `RESULTS.md` is quoted but not hashed.**
  - **Where:** `tools/findings_build.py:1121-1130` and `:1154-1157`.
  - **What happens:** the interval labels (Appendix B, which carry numbers such as "98.33%" and "B = 2000"), the clip column and the banner come from `RESULTS.md`. Only the banner is checked against `results.json`, and `sources.json` records no hash for this file. A `RESULTS.md` from another run placed beside `results.json` would be quoted, and a later consistent edit of `RESULTS.md` and the document passes `check`.
  - **Fix:** record and verify its SHA-256. For CONF-1, require it in the manifest.
- **R7. The TD count "differing" defaults to "0".**
  - **Where:** `tools/findings_build.py:260`, with `TD_DIFFERS` at `:100`.
  - **Why the default is unsafe:** `compare_runs` prints the line only when the count is nonzero (`tools/compare_runs.py:2788-2791`). The line is also absent from an UNDETERMINED report, which returns early, and from a non-TD tier, where verdict differences are printed as DEF lines instead.
  - **Failure scenario (case D):** the document states "Verdict-type leaves that differ between the two runs: 0", traced to a file that never printed it. If the result token were PASS and the gates passed, this would select `gpu_agree`. This is the one fabricated number in the tool (PRIME.4).
  - **Fix:** require a `tier: TD` line and the TD statistic block, or refuse. Write the absent count as "none listed (compare_runs prints this line only when nonzero; tier TD)", not as a bare traced "0".
- **R8. The Level column substitutes the design constant without marking it.**
  - **Where:** `tools/findings_build.py:463-467`.
  - **What happens:** for H2a(i), H2a(ii) zero, H2a(ii) interior and H2b(i) (4 of the 6 primary parts), the cell shows `primary_level` "0.9833". It is formatted exactly like a stored leaf (H2b(ii), H3c: "0.9833"), so the reader cannot tell which is which. H1b, H1c, H2c, H2d and Q-N show "0.95" next to stored "0.9500". The template sentence at `tools/findings/preliminary.template.md:40` discloses the substitution only in general terms. A4 asks for "the level stored in the leaf", and the results store none for these parts.
  - **Fix:** write "0.9833 (design value, not stored)" in those cells and count them. Alternatively, have the planner record that A4 is unattainable for these parts.
- **R9. Pre-registered or reported content is missing.**
  - (a) V7 shows only `median_slope` (`tools/findings/design_constants.json:92`). v3 §6 V7 also requires "median δ/(ρν) at every ρ" in [0.9, 1.1]. It is stored as `V7/efficiency_median_by_noise` and `V7/efficiency_pass_by_noise` but not shown, so A5 ("with their statistic") is unmet for V7.
  - (b) v3 §2 H2c says "A4o − A2 reported with its interval", and the leaf `H2c/A4o_minus_A2` exists with a level. The tool omits it, yet the H2c failure reading in §4 (`design_constants.json:99`) tells the reader to apply it "from the reported A4o − A2 interval", which the document does not contain.
  - **Fix:** add a V7 efficiency row per ρ and an H2c A4o − A2 row, marked "reported, no verdict".
- **R10. Figures: what could mislead a reader.** The estimates and intervals are drawn exactly as stored, and marker shape, text and Okabe–Ito colour are all used. The problems:
  - (a) **F2, Q-N panels.** These shade [0, 0.05] like a pass band. For a four-way reading this looks like pass or fail: the "substantial" zero-indicator intervals sit outside the shade and read as failures. Draw reference lines at 0 and 0.05 labelled with the §7 readings, and no shaded band.
  - (b) **Level.** It is not written in any panel, against the figure rule of plan note §6; only the caption has it.
  - (c) **F3.** It shows no GPU gate status. In this dry run the chua GPU gate failed, which F3 does not show. It also has no PROVISIONAL mark (A5: "every … figure panel of that system").
  - (d) **F2, H2c panels.** These share one axis across systems whose scales differ by 10³ (rossler about 10⁻⁵, lorenz63 about 10⁻²). Rossler's interval is invisible and its "fail" marker appears to sit on the band edge.
  - (e) **Status line.** The suptitle carries only the provenance label. A PNG lifted for the poster (P3) loses the PRELIMINARY, internal-only status. Add it to the suptitle.
- **R11. test-impact: an entry is needed, not a note.**
  - **Where:** `tools/test_impact.py:524`.
  - **What happens:** I called `select()` on a change set holding only `tools/findings/design_constants.json` and `preliminary.template.md`. The result is `default: own test + direct dependents -> nothing` for both. The default rule looks for `tests/unit/test_design_constants.py`, which does not exist, so a band or wording edit alone would run no test. The Log's statement that the default rule "select[s] the same test file" is incorrect: the file was selected only because `findings_build.py` changed too.
  - **Fix:** add a mapping `tools/findings/*` → `tests/unit/test_tools_findings_build.py` in `tools/test_impact.py`, with its test (WU-0011 or the owner). Until then, record the radius by hand in each Log.
- **R12. Test gaps.** All tests are exact and justified, and none can pass vacuously. Black is clean and the docstrings are plain. The gaps:
  - No test covers a mask loophole (R2), and `test_template_is_number_free` uses the tool's own regexes.
  - No `check`-level test covers the verdict-table PROVISIONAL mark, the gate box or the wording blocks (R1, R4).
  - No test covers `--development` or a mismatched `seed_id`/`seed_kind` (R5), the missing-system case (R3) or the TD default (R7).
  - The secondary, Q-N and gate leaf paths are checked only through `make_results`, which is built from the same constants, so that check is circular. The DEV-2 dry run is the only independent evidence that they resolve. Say so in the module docstring, or pin them against `RESULTS.md` or the code.
  - The bands and bars have no test against v3. I verified them by hand; a fixed table copied from v3 §2, §6 and §7, with section citations, would pin them.
  - `test_check_catches_edits` repeats an irrelevant assert inside its loop (`:424`).

**Notes**

- **R13. Dead code and a crash path.**
  - Dead code: in `missing_note` (`tools/findings_build.py:743-749`), `count` is a non-empty string, so `if count` is always true. The constants `min_states`, `td_level_z`, `reading_q_lo`, `reading_q_hi` and `primary_level_pct` are unused. This goes against the complexity rule: remove them or use them.
  - Crash path: `check` crashes with a traceback (exit 1, no message) on a trace row naming an absent source (`:1172`, KeyError) or an unknown const path (`:1191`, uncaught `Missing`).
- **R14. Counting of absent values.**
  - The 30 "not recorded" H3a leaves are visible as cells in §6, but their count appears only in Appendix C. Add the count line under the H3a table.
  - A null leaf renders "not computed" (`:175-176`) and is not counted.
  - `panel_data` (`:848`) turns a null estimate or interval (TypeError) into "not recorded" on the figure, uncounted, and with a different word from the table. These are minor PRIME.4 gaps.
- **R15. Wording precision.**
  - The 4-digit (`.4g`) endpoints can print a band edge that the unrounded endpoint does not reach (for example 0.699996 → "0.7" against "≥ 0.7 (closed)"), while the stored verdict correctly says inconclusive. Add one line above each parts table: "endpoints rounded to 4 significant digits; verdicts use the unrounded endpoints (v3 §7)".
  - The coverage limitation (template line 94) drops "at nominal 95%" and v3 §8's "about 1 to 2 percentage points of false-verdict probability under dependence". Quote v3 more closely.

### Honesty of the document (item 6)

- The banner (A1) is exact, and line 2 carries the internal-only status (D5).
- The decision rule and the uncontrolled-error sentence quote v3 §7.
- "supported" always carries "(preliminary, unpromoted)".
- No banned phrase appears, and no claim goes beyond a pre-registered test.
- All 14 items of v3 §8 are present, plus the DEF and DEC items and D6.
- Development numbers appear only in this labelled dry-run note. Appendix A is empty in this build (D4).
- The open points are R9(b) (a reading that points to an absent interval), R14 (the count of absent values sits only in the appendix) and R15 (two paraphrases weaker than v3).

### Could not check

- **Sealed outputs:** behaviour on real sealed outputs and the real manifest and ledger. They do not exist yet, and I must not read them.
- **A10 at full precision:** compare_runs prints two decimals, so A10 equality is confirmed only at that precision.
- **Infinite or null bounds:** whether the frozen code ever stores an infinite bound as `null`. If it does, `fmt` raises and `render` aborts (loud, not wrong).
- **P4 and P5:** not built in .1 to .3, so not reviewed.

Reviewer scripts, all throwaway and outside the repository, are in the session scratchpad: `z_recompute.py`, `vcount.py`, `sample.py`, `perturb.py`, `perturb2.py`, `perturb3.py` and `variants.py`.
