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

## Re-review of fix round 1 (2026-10-19)

- **Reviewer:** `reviewer`, claude-opus-5-5, fresh context. I read `wu/prelim-build` at tip a1af5f8 read-only; this review branch still sits on the old tip.
- **Verdict:** **one more fix round needed.** R3 to R15 are fixed. R1 and R2 are only partly fixed, because the two free slots still leak (R18). Two new gaps need closing before the tool touches sealed outputs: the cross-check text is not bound to the two results files (R17), and the A9 provenance conditions are shown but not enforced (R16). R19 holds three small notes.
- **Owner checkpoint:** yes, unchanged. These need owner review before sealed use:
  - the release guard (R5, R16);
  - the cross-check binding (R17);
  - the two limits the tool states and cannot close: it reads neither the ledger nor the manifest.

### Evidence

All runs used scratch copies, `nice -n 19`, `LPC_THREADS=1 OMP_NUM_THREADS=1 JAX_PLATFORMS=cpu`. I started no preset and used no GPU.

- **Tests.** I ran the radius once from the `wu/prelim-build` worktree: `LPC_PYTHON=…/.venv/bin/python tools/run_tests.sh unit tests/unit/test_tools_findings_build.py tests/unit/test_tools_test_impact.py` gave **`88 passed in 9.38s`**. Black 26.10.1 leaves all four files unchanged.
- **Committed dry run.** `check` on the committed document, with overrides pointing to my byte-identical scratch copies, gives `check passed: 979 traced values, 0 problems` (exit 0). A fresh render from the copies gives 979 traced values and 30 leaves not recorded. Its three PNGs are byte-identical to the committed ones (A12).
- **DEV-2 equality (A10).** The document still prints 18 of 18 parts computed, sum of z² (away) 15.77, largest z 2.26, 0 failing and 52 differing verdict-type leaves. All of these equal my independent recomputation from the first round, and the TD file has the same SHA-256 (df8fcaad…).
- **New rows read stored leaves.** I checked by hand against the JSON:
  - V7 `efficiency_median_by_noise` at 0.005, 0.01, 0.02 and 0.05 equals the leaves (for example lorenz63 1.0040, 1.0055, 1.0072, 1.0112).
  - H2c A4o − A2 equals `H2c/A4o_minus_A2/{mean, ci, level, role}`: lorenz63 −0.0255 [−0.03815, −0.01414], level 0.9500, role "reported"; rossler and chua likewise.
  - Both are plain `ref` and `fmt` calls. No comparison and no arithmetic is involved, so A3 still holds.
- **Old perturbation table.** I re-ran the first-round tables (P1 to P13, Q6a to Q9c, X1, X2, G1 to G5, H1 to H4, M, D) against the new tool: **every one now fails `check` (exit 1) or is refused at render (exit 2)**, except the expected cases:
  - M (chua absent from `systems`) now renders chua as "not recorded" and PROVISIONAL everywhere, counts 118 such cells and passes. That is the intended fail-closed behaviour.
  - M2 (chua also removed from `core_systems`) is refused.
  - D (TD text without the "differing" line) now prints "none listed (…)", never "0".
  - H1d (confirmatory, well-formed but unverifiable reference, typed hashes, commit equal to freeze-1) still renders. That is the inherent limit the docstring states (see weak point 2).

### Status of R1 to R15

| Finding | Status | Evidence |
| --- | --- | --- |
| R1 frame not verified | **partly** | `check` re-renders and compares byte for byte (`tools/findings_build.py:1593-1661`). P7, P8, P9, Q9 to Q9c, G4 and P11 now fail. The two free slots can still carry status claims; see R18. |
| R2 numeral loopholes | **partly** | Outside traced spans the frame is byte-compared, so the scan now matters only in the free slots. All old loopholes Q6a to Q6j are caught, and `test_numeral_scan_catches_every_loophole` uses typed patterns. The `IDENTIFIER` list and non-ASCII digits still let numbers into the free slots; see R18. |
| R3 missing system | fixed | The three systems are a constant. `core_systems` must equal them (M2 refused), an absent system is "not recorded" and PROVISIONAL and is counted (M), and `check` requires 14 × 3 verdict rows and 6 × 3 primary rows. |
| R4 PROVISIONAL and figures | fixed | G2 is caught: "verdict cell … lacks PROVISIONAL". G5 and P12 are caught: figures are re-drawn and compared byte for byte. |
| R5 release guard | partly, by design | Fixed: (a) `classify` refuses a mixed kind (H2, H4); (b) `--development` must be development (H3); manifest hashes are stored in `sources.json` and re-verified; the freeze check is re-run by `check`. Inherent: (c) the hashes are typed, not read from the manifest; (d) the reference is checked for format only. New gaps: R16, R17. |
| R6 RESULTS.md hash | fixed | It is hashed, stored, re-verified, and has a manifest hash for CONF-1. |
| R7 TD default "0" | fixed | The absent count is "none listed" or "not available", never a number. A text with no totals line is refused. `test_absent_differing_count_is_never_a_number` covers it. |
| R8 design level | fixed | Cells read "0.9833 (design value, not stored)", with a count under each table (12, 15, 6). |
| R9 V7 and A4o − A2 | fixed | The rows are read from stored leaves, verified above. |
| R10 figures | fixed | I viewed the PNGs. Q-N has dashed edges at 0 and 0.05 and no band. Every panel title states its level ("(design value)" where not stored). F3 names "[GPU gate not passed]" per row, has a footer, and marks PROVISIONAL. H2c has one axis per system. Every suptitle carries the PRELIMINARY line. |
| R11 test-impact | fixed | `select()` on the template and constants alone now gives `['tests/unit/test_tools_findings_build.py']`. The `TOOL_DATA_TESTS` entry has its test. The Log correction is recorded. |
| R12 tests | fixed | There is an independent `REAL_LEAVES` table. Bands and bars are pinned to quoted v3 phrases (`test_bands_and_bars_equal_the_proposal`), the loophole list is typed, and tests cover the guard, the free slots and figure swaps. The tests are exact and none is vacuous. |
| R13 dead code and crash | fixed | `test_every_constant_is_used`. A malformed trace row now gives a message (X1 "unknown source", X2 "leaf gives …"). |
| R14 counts | fixed | Counts of "not recorded" and "not computed" appear in the body after §5, the H3a table and F2. Nulls are counted. Figure text uses the table's words. |
| R15 wording | fixed | The rounding sentence is above both parts tables. The coverage limitation is v3 §8 word for word (`test_coverage_limit_quotes_v3_section_8`). |

### New findings

- **R16 (should fix, owner checkpoint).** A9's provenance conditions are shown but not enforced, and the cross-check run's commit is never checked.
  - **Where:** `tools/findings_build.py:1239-1248`.
  - **Scenario (case N4):** a confirmatory official file with `dirty` true, `complete` false, backend gpu and `LPC_THREADS` 1, and a cross-check at commit `000…0`, renders with exit 0. The document then says "Source: the official CPU run of the sealed confirmatory seed" above "Backend | gpu", "Dirty | yes", "Complete | no".
  - **Fix (needs no ledger):** for confirmatory mode, refuse unless:
    - the official file has `complete` true, `dirty` false, `device.backend` cpu and `env.LPC_THREADS` "8" (v3 §9 item 2 and 3; A9);
    - the cross-check file has `complete` true, `dirty` false and a commit equal to the official commit (the same freeze, DEC-0031);
    - the two results files have different SHA-256 values. Case N3 shows the official file passed as its own cross-check is accepted today.

  The mode notice should also stop asserting "CPU"; let the backend row speak for it.
- **R17 (should fix, before sealed use).** The `compare_runs` text is not bound to the two results files.
  - **Where:** `tools/findings_build.py:297-343`, `:1161-1185`.
  - **Scenario:** any text with a TD totals line is accepted and its z values are copied verbatim:
    - N1: the swapped-order text renders and passes;
    - N2: a text in which I set every z to 9.99 renders and passes, printing `| lorenz63 | H2a(i) | 0.0179 | 9.99 | 9.99 | …` beside these files.

    For CONF-1, a stale or wrong TD file (for example the DEV-2 one) would put another run pair's cross-check numbers into §8 and F3 under the CONF-1 banner. `check` passes, because the TD file is hashed only against itself.
  - **Fix (no recomputation needed):**
    - require the `REF:` and `NEW:` lines of the text to resolve to the `--official` and `--crosscheck` directories (run `compare_runs` with absolute paths, as step b of the plan note implies);
    - and/or verify that every listed `TD: … differ` leaf (`path: 'ref' -> 'new'`) equals the stored strings in the two files;
    - refuse on mismatch.
- **R18 (should fix; the remainder of R1 and R2).** The free slots (the body of §11 and the dated §9 lines) are fenced off from the frame, but they still leak.
  - **Where:** `tools/findings_build.py:93-117`, `:1389-1428`, `:1493-1517`.
  - **What the free text cannot do:** change any rendered verdict, number or status line. Those are byte-compared. Adding a `## ` heading is caught (S5), editing a rendered §9 line is caught (S4), and an undated extra line is caught (S3).
  - **What it can do:**
    - **(a) Numbers through identifier shapes.** All of these pass: "§ 0.938", "r947", "QA.73", "PRIME.14", "LPC.PC.95", "DEF-0947", "WU-0938.1", "D14", "item 7", "# 42. percent", and the shapes "CONF-9", "rho-5%" (cases F1 to F5, F10, F11). `IDENTIFIER` is the trust boundary, and in free text almost every shape takes free digits. Fix: in the free slots, use a separate, strict mask that allows only `H\d[a-e]`, `V[1-7]`, `E[0-6]`, `v3` and `§\d+` with no decimal.
    - **(b) Non-ASCII numerals.** "⁹⁵ percent" and "¾ of the parts" pass (F6). Python's `\d` matches only category Nd, as the fullwidth control F7 shows. Fix: reject any character with `unicodedata.numeric(ch, None) is not None` in the free slots.
    - **(c) Status and verdict claims in words.** These pass:
      - F8: "**CONFIRMATORY: PROMOTED** All three primary hypotheses are supported and the study proves the theory." (the banned phrases are not applied there);
      - S6: "### Verdicts [PRE-REGISTERED]" inside §11;
      - S1: "- 2026-10-20: GPU cross-check agreed after all; PROVISIONAL is lifted and H2b is supported."

      Fix: in both slots, refuse the banned phrases, the status tokens (CONFIRMATORY, DEVELOPMENT, PROMOTED, UNPROMOTED, PROVISIONAL, PRELIMINARY, GATE, any `[TAG]`) and headings. The student's interpretation can still use verdict words.
    - **(d) The date channel.** "- 0938-09-47: …" passes (S2). Fix: validate the date with `date.fromisoformat` and require it not to be earlier than the build.
  - **Tests:** add a test per case, with the patterns typed independently.
- **R19 (notes).**
  - (a) A digit found in a free slot is reported as "line 4", which is its index in the slot, not its line in the document (F7). Report the document line.
  - (b) The "Release reference" row should say "(format checked only; not verified against the ledger by this tool)". The "Manifest hashes" row already says its limit plainly.
  - (c) N3 (identical official and cross-check files) is covered by the R16 fix.

### The developer's three weak points

1. **`IDENTIFIER` as the trust boundary.** It is safe for the frame, which is byte-compared, so a smuggled identifier there fails as a diff. It is not safe for the free slots: R18 (a) shows eleven shapes that carry arbitrary digits, and R18 (b) shows non-Nd numerals. A narrower mask for the free slots is the fix.
2. **Release guard limits.**
   - The module docstring (`tools/findings_build.py:34-46`) says plainly what the tool cannot verify: it reads neither the ledger nor the manifest, typed hashes from the wrong file pass, and the owner or main session must compare both. I judge that plain enough for the owner. The document's "Manifest hashes" row repeats the limit; the "Release reference" row does not (R19 b).
   - Without reading the ledger, the guard can still be tightened as in R16 (complete, dirty, backend, threads, cross-check commit, distinct files) and R17 (binding the TD text to the files). Reading the committed manifest row read-only would remove the typed-hash weakness. That is a design choice for the owner.
3. **`merge_free_slots`.** Text in a free slot cannot change a verdict, a number or a status line that the tool renders. It can add competing numbers and status claims beside them; see R18. The merge logic itself is sound: equal headings are required, §9 must keep the rendered lines as a prefix, and the fresh text is put back before the positional checks.

### Could not check

- Anything on real sealed outputs, or on the real manifest and ledger.
- A10 beyond the two decimals that `compare_runs` prints.

Reviewer scripts are in the session scratchpad: `perturb.py`, `perturb2.py`, `perturb3.py`, `variants2.py` and `variants3.py`.
