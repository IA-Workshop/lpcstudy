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

## Re-review of fix round 2 (2026-10-19)

- **Reviewer:** `reviewer`, claude-opus-5-5. I read `wu/prelim-build` at tip bf20192 read-only. Scope: R16 to R19, and anything the new code could have broken in R1 to R15.
- **Verdict:** **approve with notes.**
  - R16, R17, R18 and R19 are fixed, within the residual limits the tool states.
  - R1 to R15 still hold.
  - Every attack from my earlier tables now fails `check` or is refused at render. The one exception is the residual the tool states and documents: a `compare_runs` text that is altered but carries the right paths and leaves (B2, B4 below).
  - The notes N1 to N4 below are cheap improvements, not conditions for merging.
- **Owner checkpoint:** yes, for the release guard. The items are listed at the end.

### Evidence

All runs used scratch copies, `nice -n 19`, `LPC_THREADS=1 OMP_NUM_THREADS=1 JAX_PLATFORMS=cpu`, with no preset and no GPU.

- **Tests and style.** One run of the findings test file: **`42 passed in 7.93s`**. Black 26.10.1 reports both files unchanged.
- **Committed dry run.** `check` on the committed DEV-2 document passes, using overrides to my byte-identical copies and running from a working directory where the text's relative REF and NEW paths resolve: `check passed: 983 traced values, 0 problems`. A fresh render gives 983 traced values and three PNGs byte-identical to the committed ones (A12). The TD numbers are unchanged and equal my independent recomputation: 18 of 18 parts, sum of z² 15.77, max 2.26, 0 failing, 52 differing.
- **New provenance rows.** "compare_runs text | … (by realpath and realpath)", "Cross-check commit … (same as official: no)" with its count, and "Release reference | none (development dry run)".
- **Earlier table, re-run.** P1 to P13, Q6a to Q9c, X1 and X2 all exit 1. The only exit-0 entry is the unedited control row of P12.

R16, confirmatory guard (variants4, all on synthetic relabels of DEV-2 copies; no sealed data):

| Case | Result |
| --- | --- |
| C0, a clean confirmatory pair (CPU official at freeze-1 with 8 threads, GPU cross-check, `ledger-seq-1`, hashes given) | renders (exit 0); control |
| C1 to C7: official dirty, incomplete, GPU, `LPC_THREADS` "1", integer 8, " 8", commit not freeze-1 | all refused (exit 2), each with a clear message |
| C8 to C10: cross-check dirty, incomplete, CPU | all refused |
| C11: cross-check commit differs | renders, and prints "(same as official: no)" with the count 1 |
| C12: same path; C13: a copy with the same SHA-256 at another path | both refused (C13 by the leaf binding, which runs before the SHA comparison) |
| DEV-2 development pair | still renders |

R17, `compare_runs` binding:

| Case | Result |
| --- | --- |
| B1: swapped REF and NEW | refused, with "made in the other order" |
| B3: one listed leaf value altered | refused |
| B5: the stored R5-vs-R6 record with its paths rewritten to bind | refused by the leaf check, since the listed values are reversed |
| B6: no REF or NEW lines | refused |
| B2: REF and NEW under another prefix with the same last two components, and every z set to 9.99 | **renders and passes** |
| B4: the "TD: … differ" line and its leaf listing deleted from an otherwise correct text | **renders and passes**, and prints "none listed" although 52 leaves differ |

Both B2 and B4 are edits of the text itself, so they fall inside the stated residual ("an altered z in a text with the right paths is not detected"). B4 widens that residual: deleting the listing switches the leaf check off, because that check has nothing to test. The docstring should name this case too (note N1).

R18, free slots (body of §11 and dated §9 lines):

- **Refused, all with the document line number:**
  - every round-2 attack: § decimals, r947, QA.73, DEF-0947 and D14, "# 42.", superscripts, ¾, Ⅶ, 十, fullwidth digits, "**CONFIRMATORY: PROMOTED**", "proves", identifiers such as V7, a `[TAG]`, `###` headings, "## " headings;
  - in §9: a date that does not exist (0938-09-47), a date before the run ended, an undated line, digits in dated text, an edit of a rendered line.
- **Still accepted, all without digits:**
  - inflections of refused or banned words: "proved", "confirmed", "significantly", "gates", "provisionally", "promotion";
  - a setext heading ("Verdicts" underlined with `===`);
  - "[CROSS CHECK]" with a space;
  - a blockquote status sentence worded without refused words;
  - a claim that contradicts the stored verdict ("H3c passes on every system and H2a is supported");
  - "H1a H2a H3a";
  - number words;
  - a far-future dated line (2099-12-31);
  - the date itself as a small number channel (a real date such as 2026-11-23).

  The module docstring states these limits: "Number words and claims phrased in other words cannot be detected."

R19: the free-slot messages name the document line. I checked by hand that line 379 and line 351 hold the planted text. The Release reference row reads "ledger-seq-1 (format checked only; not verified against the ledger by this tool)".

### Findings R16 to R19

- **R16: fixed.** All the A9 conditions requested are enforced in confirmatory mode, and the files must differ by both path and SHA-256. The cross-check commit is printed with "same as official". One open point: the document says "a ledger-only later commit is allowed", but the tool does not check that the difference is ledger-only (N2).
- **R17: fixed, with the stated residual.** Judging that residual:
  - The tool recomputes no z, as instructed. A wrong-run text is caught when its paths differ in the last two components, or when it lists a differing leaf whose values disagree with the files. The listing includes the first 20 verdict-type leaves, and a different realization almost surely differs in at least one of them.
  - A text whose last two path components match but comes from another tree is caught only through that listing. For the sealed pair the components will be roughly `run-1/full` and `run-1-gpu/full`, which a run under another prefix could share. If the listing is empty or deleted (B4), nothing ties the text to the files.
  - I judge the residual acceptable for an information-only section that changes no verdict, on two conditions:
    - in confirmatory mode, require binding by realpath (N3);
    - make it a step of the WU-0020.8 review to rerun `compare_runs` on the released directories and diff the result with the committed text. Its SHA-256 is already in `sources.json`.
  - The docstring states the z residual plainly. It should add the empty-listing case (N1).
- **R18: fixed for numbers, status tags and headings, with stated residuals for wording.**
  - **The hypothesis-name allowance.** Removing the 12 names `H1a` to `H3c` would only push the student towards "H-two-a", with no gain. The allowance carries no number: "H2a1" is refused, and the names are fixed strings. A claim such as "H3c passes" can be phrased without the name just as easily. I would keep it. (The allowance actually covers 12 names, not 14: Q-N and the gain bound have no digit and need none.)
  - **The real gap is the banned list.** The free-slot rule uses whole-word matching, so inflections pass ("proved", "confirmed", "significantly", "gates", "provisionally"). The PRE-REGISTERED rule matches substrings and catches those. N4 gives the fix.
- **R19: fixed.**

### Notes (not merge conditions)

- **N1.** Add to the docstring and to the "compare_runs text" row that an empty or deleted leaf listing leaves only the path binding. Better still: in confirmatory mode, refuse a TD text that has no "TD: … differ" line while its tier is TD and any listed verdict leaf of the two files differs. That would be a string comparison of stored verdict words, which A3 allows.
- **N2.** `git diff --name-only <official>..<cross-check>` is read-only git, which the tool already calls for freeze-1. In confirmatory mode, refuse when the cross-check commit differs and the changed paths fall outside `docs/agent/records/`. Without that, the words "a ledger-only later commit is allowed" describe a rule nobody checks.
- **N3.**
  - `check` depends on the working directory. Relative REF and NEW paths resolve against the current directory, so the binding sentence changes from "realpath" to "trailing two path components". An unaltered document then fails `check` with "meta values differ" ("trace file differs"; reproduced from the scratchpad root).
  - This fails safe, but it is confusing.
  - Fix: in confirmatory mode, require `compare_runs` to be run with absolute paths and bind only by realpath. Otherwise, record the render's working directory in `sources.json` and resolve against it.
- **N4.**
  - In the free slots, match the banned and refused words as prefixes (`\bprov(e|es|ed|en|ing)\b`, `\bconfirm\w*`, `\bsignifican\w*`, `\bgate\w*`, `\bprovisional\w*`, `\bpromot\w*`), as the PRE-REGISTERED rule already does by substring.
  - Refuse setext underlines (`^=+$`, `^-+$` after text) and any `[…]` in capitals.
  - Refuse a dated line later than the day `check` runs.

### Residual risks the owner must know (stated in the module docstring)

1. The tool reads neither the manifest nor the ledger. Hashes typed from the wrong file, and a release reference that does not exist, both pass. The owner compares the three hashes with the WU-0015.3 manifest row, and `ledger-seq-<n>` with the ledger.
2. A `compare_runs` text with altered z values, or with its leaf listing deleted, passes if its paths bind. Remedy: rerun `compare_runs` on the released directories and diff (N1, N3).
3. The cross-check commit may differ from freeze-1. Only "same as official: no" is shown, so the owner checks that the difference is ledger-only (N2).
4. In §11 and the dated §9 lines, claims in words are not detected: a verdict contradicted in prose, inflected banned words (N4) or number words. The WU-0020.8 reviewer reads every claim.

### Owner-checkpoint items for the release guard

These need owner review before sealed use:

- the `classify` kinds;
- the confirmatory conditions (official: complete, clean, CPU, `LPC_THREADS` "8", commit equal to freeze-1; cross-check: complete, clean, GPU, a different file);
- the `ledger-seq-<n>` format;
- that manifest hashes are typed, not read;
- the cross-check commit rule (N2);
- the REF and NEW binding rule (N3).

Reviewer scripts are in the session scratchpad: `variants4.py`, `freeslot.py` and the earlier `perturb*.py`.

## WU-0020.8 review of the sealed-run document (reviewer, 2026-10-20)

- **Reviewer:** `reviewer`, claude-opus-5-5. Fresh context; I did not write the document, the tool or the template.
- **Subject:** develop at 0e55df8, `docs/agent/notes/2026-10-20-prelim-findings-conf1.{md,trace.csv,sources.json,compare.txt,figures/}`.
- **Sources read under the release:** `python3 tools/ledger.py verify` reported "ledger chain intact". Entry seq 20 is an `authorization` by the owner: audience Brian McDermott and Deem Albaty; paths `runs/confirmatory/run-1/full`, `run-1-gpu/full` and `run-1-compare.txt`; `promoted: false`. I read only those paths, plus the governing and record files. I did not read the sealed seed, the seal script, `run-2` or anything else under `runs/confirmatory/`.
- **Tests:** none run. `python3 tools/test_impact.py --base f8bfe74` prints "no tests", because the change set holds no code. I did not run `findings_build.py check`; the main session reported "check passed: 961 traced values, 0 problems". Every check below is my own read-only Python (`.venv/bin/python -I`) or a read by hand.
- **Verdict:** **changes required**. 11 findings: 3 blockers (R1, R2, R4), 3 should fix (R3, R5, R6), 5 notes (R7 to R11).

### What I checked and found correct

- **Provenance (§2).**
  - The SHA-256 of `run-1/full/results.json` (ae4b0fe5…), `RESULTS.md` (2a4c1d06…) and `run-1-gpu/full/results.json` (b768cb03…) equal the files on disk, the owner's `.sha256` files and the WU-0015.3 row of `results-manifest.md`.
  - `git rev-parse freeze-1^{commit}` is df8928f…, which equals the official commit.
  - `git diff --name-only df8928f..78f7f2f` lists only `docs/agent/governance/ledger.jsonl` (commit "Ledger: authorization for the GPU cross-check of CONF-1"), so the "1 path, all under … the ledger" row is true.
  - Start 08:38:31Z plus 15555 s gives 12:57:46Z, the stored end time, and agrees with the manifest's "04:38 (local), 15555s".
  - `LPC_THREADS` 8, cpu, dirty no, complete yes: all equal their leaves.
  - Release reference: ledger seq 20 exists and covers these paths.
- **Every trace row (961).** An independent resolver (`chk_trace.py` in my scratchpad) resolved each `official` and `crosscheck` path in its JSON:
  - 0 raw-value mismatches;
  - 0 rendered strings off their raw value by more than half a unit in the last printed digit;
  - 0 rows whose rendered string is not found at its recorded document line and column.
- **Semantic mapping.** I printed every cell of the gate, primary, secondary, Q-N, H3a and gain tables beside its leaf path, and each cell reads the right statistic for its row label:
  - H2a(i) reads `median_range`/`range_ci`;
  - H2b(i) reads `noise/mean_state_spearman`;
  - H2b(ii) reads `library_change`;
  - H3c reads `A5_over_A4_mse`;
  - H1c reads `PLP/median_ratio`;
  - H2c reads `A4_minus_A1`. The stored `best_single` is "A1" on all three systems.
  - H2a(ii) correctly has no third part: `n_w_one` is 22, 5 and 16 of 1000, all under 5%.
- **Verdicts (step 3).**
  - All 14 rows of §4 equal `verdicts.<id>` in `results.json`.
  - Each overall word follows v3 §7 from its three per-system words. Each per-system word follows the "every part passes / any part fails" rule from its part words.
  - Applying the v3 §2 bands, strict or closed as v3 §7 lists them, to the 60 stored primary and secondary endpoint pairs reproduces every stored part verdict (0 mismatches).
  - Q-N readings follow the v3 §7 table from their stored endpoints. H3a is inconclusive on all three systems because Holm p ≥ 0.01 somewhere on each.
  - No sentence uses "confirmed", "proves", "significant", "shows" or "no effect". "Inconclusive" is glossed as "does not say the effect is absent", and "supported" carries "(preliminary, unpromoted)".
- **20 random trace rows re-read by hand.** I drew them with `random.Random(20261020).sample(range(961), 20)`, which gave ids 32, 63, 67, 83, 151, 208, 217, 321, 330, 470, 492, 507, 520, 666, 667, 763, 792, 814, 837 and 879.
  - Each was re-read by a direct key access in `results.json`, in `design_constants.json` with its v3 citation, or in compare-text line 377 (id 879).
  - All 20 equal the document cell. For example: id 32 is 0.8383301964405617, shown as 0.838; id 666 is `rossler/H3a/pairs[2]` = [1, 0], shown as "1, 0"; id 879 is 0.0271.
  - The constants match v3: V1 bar §6; v3_bar "reported"; the H1a band [0.75, 1.25] closed (§2).
- **Clip column and Appendix B.** Each of the 14 clip cells equals the last cell of its row in the `RESULTS.md` verdict table. Each of the 14 interval labels (lines 389 to 402) occurs verbatim in `RESULTS.md`.
- **Cross-check numbers (§8).**
  - The 18 rows equal compare-text lines 363 to 380 field by field.
  - The totals line equals line 381; 53 and PASS equal lines 340 and 382.
  - The GPU gate leaves are all true.
  - `compare.txt` differs from the owner's released `run-1-compare.txt` only in the REF and NEW path prefixes (`diff` after stripping the prefix: empty).
- **Handling (§7).** Every total and per-system cell equals `handling.totals` and `handling.by_system`, and `failed_variants` is 0. All nine `SENTINEL_COUNTERS` of `report.py`, and the sentinel result paths, are 0 everywhere in `handling` and `systems`.
- **Figures.**
  - **F1.** Every marker and bar matches its §5 row. The bands are drawn as written: below 0.1; (−0.1, 0.1); > 0; ≤ 1.05. Levels read "(design value)" exactly where the table says so. Shape and text encode the verdict.
  - **F2.** Every panel matches §6, including chua H1a ρ-2% inconclusive, rossler H3b weight 0 [0, 0.13] pass, and the Q-N dashed edges at 0 and 0.05 with no band.
  - **F3.** The 18 z_away values equal §8, the dashed line is at 3.4, and the gate footer reads "passed" for all three systems.
- **Limitations (§10).** It covers all 14 items of v3 §8 plus DEF-0018, DEF-0020, DEF-0026, DEF-0027, DEC-0033 M2 and M3, one realization per system, and the D6 block-sensitive status. The coverage sentence is v3 §8's text. The content of the DEF-0027 line is wrong (R4).
- **Labeling.**
  - Line 1 is `**CONFIRMATORY: UNPROMOTED**`, equal to `provenance.label`; line 2 is the note §2.1 sentence.
  - Section tags match the note's section table: §3 to §6 `[PRE-REGISTERED]`, §7 `[DIAGNOSTIC]`, §8 `[CROSS-CHECK: information only]`, §11 `[STUDENT]`, A `[DEVELOPMENT]`, the rest untagged.
  - Appendix A holds no development numbers. §11 is still the prompt, and §9 has no dated line, so there is no free-slot text to read.
- **Untraced numerals.** I masked the trace spans and identifier shapes and scanned the document for digits. Only section numbers, "SHA-256", ρ row labels (`rho-1%`), counter names (`closed_form_floor_a4`) and "v2 §M16" remain.

### Findings

- **R1 (blocker): the Q-N row of the overall table reports only one of the two pre-registered parts.**
  - **Location:** document line 106 (§4), trace ids 131 to 133 (`verdicts/Q-N/by_system/{lorenz63,rossler,chua}`), together with line 117.
  - **What is wrong:** the row reads "reduces | reduces | reduces". v3 §2 and §7 read Q-N "separately for its two parts". The stored indicator part reads **substantial** on all three systems: `systems/<s>/Q-N/oracle/w_zero_indicator/reading`, with ΔR² 0.2266 [0.1673, 0.2839], 0.2002 [0.1462, 0.2538] and 0.1438 [0.09589, 0.1902]; §6 lines 216, 218 and 220 show this.
  - **Cause:** the stored word is faithful to the file, but the file's `verdicts.Q-N.by_system` is built from the logit part alone (`lpcstudy/report.py`, the `row.role == "estimate"` branch: `readings[s] = res[res["primary"]]["logit_w_interior"]["reading"]`). `RESULTS.md` shows both parts in its cell ("reduces: oracle: interior reduces (…), w*=0 substantial (…)"). The document drops the second.
  - **Why it matters:** Q-N is a D10 poster highlight. A reader of the headline table would conclude that "N reduces to the other three", which the indicator part contradicts.
  - **Fix:** in the §4 row, show both stored readings per system (logit / indicator), traced to the two `reading` leaves, or label the cell "logit part only" with the indicator readings beside it. Do not change frozen code. Refer the collapse in `report.py` to the owner as a reporting observation (verdict and report code: needs owner review).
- **R2 (blocker): the cross-check section does not report the differing verdicts, and its framing implies agreement.**
  - **Location:** §8, lines 317 to 344 (trace ids 938 and 939), and F3.
  - **What is wrong:** v3 §9 item 3 ("a differing verdict … is reported") and DEC-0031 item 2 require the differing verdicts to be reported. DEC-0028 item 4 says a TD pass "does not reproduce verdicts or the gate outcome". The document gives only the count (53) next to "compare_runs result: PASS (exit 0)" and 18 "ok" rows, and none of the differences.
  - **Evidence:** read from the two `results.json`, CPU → GPU:
    - **Overall words:** H2c inconclusive → **not supported**; H2d inconclusive → **not supported**.
    - **Primary per system:** lorenz63 H2a fail → inconclusive (H2a(ii) interior fail → inconclusive); lorenz63 H3c inconclusive → **pass**; rossler and chua H2a(ii) zero inconclusive → pass.
    - **Q-N:** rossler reads reduces → **substantial**.
    - **Other per-system words:** lorenz63 H1a pass → inconclusive; chua H1c inconclusive → fail; rossler H3b pass → inconclusive; lorenz63 H2c and H2d inconclusive → fail; chua H2c pass → inconclusive.
    - **H3a regimes:** lorenz63 has 6 regimes on the CPU and 4 on the GPU (compare text lines 324 to 339, one-sided leaves).
    - The compare text lists only the first 20 of the 53 leaves (lines 341 to 360).
  - **Why it matters:** "PASS" and "ok" read as agreement. The owner and student would not see that two secondary overall verdicts and three primary per-system words flip across devices.
  - **Fix:** add a `[CROSS-CHECK]` table of stored verdict words that differ, overall and per system (primary parts first), read from the two files as a string comparison (A3 allows this). Add DEC-0028 item 4's sentence.
  - **Plan note:** the note §2 item 2 limits `[CROSS-CHECK]` to "the count of differing verdict-type leaves". That is narrower than v3 §9 item 3, so the plan needs a planner or owner amendment for the fix.
- **R3 (should fix): the closing sentence of §8 is a fixed disjunction that is misleading for this data.**
  - **Location:** line 344; `tools/findings_build.py` `wording_gpu` (lines 850 to 867); `design_constants.json` `wording.gpu_disagree`.
  - **What is wrong:** "At least one primary part exceeds the bound, a verdict-type leaf differs or a GPU gate failed" is true here only through the second clause. No part exceeds 3.4 (largest 2.21) and every GPU gate passed. A reader takes it as a TD failure.
  - **Second instance:** the F3 caption (line 348) says "Each row names a failed GPU validation gate and a PROVISIONAL official system", which reads as an assertion although neither occurs.
  - **Fix:** emit one sentence per condition from the tokens: "no primary part exceeds the bound"; "53 verdict-type leaves differ"; "the GPU gate passed on all three systems". Make the F3 sentence conditional ("a row would name …").
- **R4 (blocker): the DEF-0027 limitation reverses the meaning of "5 of 18".**
  - **Location:** line 367, trace id 943 (`constants/lm_flag_count` = "5 of 18", cited to v3 §8); the per-row note "LM iteration error: not estimated" (lines 130 to 147).
  - **What is wrong:** the document says "the Levenberg–Marquardt flag was raised on 5 of 18 primary parts", as if 5 parts were affected. In the source records the LM-row flag is "yes iff class N", meaning negligible (`docs/study/lm_doubling_dev0_report_v3.md`, lines 24 and 66). The official `RESULTS.md` says (line 429 and the four parallel lines) that the change is below 10% of the half-width "for 5 of the 18 parts … and does not show it below 10% for the other 13 (X, not negligible, 6; U, not certified, 7)". The DEF-0027 correction of 2026-10-18 gives N 5 / X 6 / U 7 (Lorenz-63 X 4, Chua X 2, Rössler X 0).
  - **Root:** v3 §8's own sentence ("not negligible … for 5 of the 18 primary parts") disagrees with the corrected record. The document copies v3 and so contradicts the official run's own report.
  - **Plan gap:** the plan (note §2 item 3) also requires a pointer to `lm_doubling_dev0_report_v3.md` on the primary rows, and it is absent.
  - **Why it matters:** this understates the main unestimated error on the primary parts, which the student will repeat.
  - **Fix:** state the limitation as `RESULTS.md` and DEF-0027 do (development evidence: shown negligible for only 5 of 18 parts; not negligible for 6; not certified for 7; the projection is stated, not applied), add the pointer, and refer the v3 §8 inconsistency to the owner.
- **R5 (should fix): §7 claims completeness it does not have.**
  - **Location:** line 279, "Every clip, floor, replacement and fallback counted by the run (PRIME.4)".
  - **What is wrong:** the table holds only the main-system counters of `handling`. It omits:
    - `skipped_variants` (0);
    - the counters under `handling.robustness` (lorenz63, rossler);
    - the result counts of `RESULTS.md` §Handling, among them floors and exclusions: `H1b/CP/n_floored` 79 / 92 / 114; `H2a/n_excluded_states` 312 / 72 / 361; `H1c/*/n_ineligible_states`; `H2b/noise/n_constant_states` 62 / 76 / 61; the gain-bound screen-outs (lorenz63: growth ≤ 0 136, covariance < 0 252).
  - **Sentinels:** the table also does not mark the sentinel counters. All are 0, which I checked.
  - **Fix:** reword to "the run's handling counters of the main systems", add `skipped_variants`, and either add the result counts (traced) or point to the `RESULTS.md` section and `handling.robustness` by name.
- **R6 (should fix): quantities that v3 §2 says are "reported" are missing, although §1 says the document "reports what the pre-registered analysis returned" (line 12).**
  - **H2a:** the excluded-state counts (312, 72, 361 of 1000), the per-span medians and counts (lorenz63 1-2: 0.0650 on 533 states; 1-2-4: 0.479 on 155), the complete-case {1, 2, 4} sensitivity (lorenz63 0.479 [0.390, 0.576]; rossler 0.377 [0.336, 0.411]; chua 0.407 [0.344, 0.493]) and the counts of w* = 0 and w* = 1 (285/22, 305/5, 284/16). The complete-case values sit far above the 0.1 bar while lorenz63 H2a(i) reads inconclusive at 0.113, so a reader needs them.
  - **Others:** the H1a floor f; H1c's CP value; H1d's N̂ (Spearman 0.66, 0.61, 0.63 in `RESULTS.md`); the H3b stability fraction (0.91, 1.0, 1.0); the gain-bound screen-out counts.
  - **H2c label:** the label "A4 − A1" is not explained. The stored `best_single` is A1 (PLP), chosen on the calibration split, on all three systems.
  - **Fix:** add a traced "reported quantities (no verdict)" table, or state plainly which reported quantities are left to `RESULTS.md`.
- **R7 (note): H2a reading and power.**
  - **Location:** line 119.
  - The v3 §7 reading of an H2a failure ("instability enters the weight through anisotropic seeds") is about part (ii). Rössler fails H2a through part (i) alone, the horizon range 0.2754 [0.2426, 0.3107]; both of its part (ii) words are inconclusive.
  - **Suggestion:** write "v3 §7 pre-registered this interpretation; it is not tested here", and say which parts failed per system.
  - **Suggestion:** add v3 §7's precision statement (DEF-0022): H2a's second part "can be refuted but essentially cannot pass". "Supported" was nearly unreachable by design, which matters for how the student reads "not supported".
- **R8 (note): bullets after the overall table.**
  - **Location:** lines 119 to 122.
  - The H2c bullet sits among the primary bullets without a "secondary" label. H2e, the other supported row and a D10 highlight, has no bullet.
  - **Suggestion:** label the bullet "H2c (secondary)", or add a short secondary block.
- **R9 (note): F2 marker legend and tick labels.**
  - The A4o − A2 "reported" panels use the square marker, which the caption reserves for "a Q-N reading" (line 273).
  - The x tick labels overlap and cannot be read in the panels "H2c A4 − A2 chua" and "H2c A4o − A2 (reported)" lorenz63 and rossler. The markers do match the table.
  - **Suggestion:** name the square for "reported" in the caption, and use fewer ticks or scientific offsets on those panels.
- **R10 (note): the §8 "hw ratio" column is not explained.**
  - It is hw1/hw0, GPU half-width over CPU half-width (compare text line 362).
  - chua H3c reads 3.036: the GPU interval is three times wider. One sentence would prevent a misreading.
- **R11 (note, governance and plan; owner to see).**
  - **(a) Commit trailer.** The 0e55df8 message has no `Agent: <model id>` trailer (CLAUDE.md, Commits).
  - **(b) Log placement.** The WU-0020.7 Log entry sits under `## Referral` instead of `## Log` in the unit file.
  - **(c) Deliverable paths.** P1 and P2 are under `docs/agent/notes/`, while the plan and the D1 default name `docs/study/`. P3 lacks the 4 existing report figures, and P4 (the one-page summary) is not built, although WU-0020.7 says "build P1 to P4". This bears on the definition of done.
  - **(d) A13 as written.** The first commit touching `runs/confirmatory/` (e754601, 08:41:12Z) precedes the release entry (seq 20, 08:43:08Z). It is the owner's own commit, not an agent's, but the mechanical check of A13 as written is not met.
  - **(e) §9 and "another actor".** §9 says the regeneration is "by another actor" (v3 §9 item 4). Ledger seq 21 records the regeneration as run by the owner, who also ran run-1 (manifest). Whether that satisfies "another actor" is the owner's call before the dated §9 line is written.

### Owner checkpoint

- No code, seed or dependency changed in WU-0020.7.
- R1 concerns verdict and report code (`report.py`, frozen): needs owner review before any change.
- R2 needs a plan amendment (scope of `[CROSS-CHECK]`).
- R4 needs an owner ruling on the v3 §8 wording.

## WU-0020.8 re-review after fix round 1 (reviewer, 2026-10-20)

- **Reviewer:** `reviewer`, claude-opus-5-5, fresh context.
- **Subject:** develop at ed6e4e1 (merge 1c86daf of `wu/prelim-fix1` 67a49c5).
- **Scope:** R1 to R10 only. R11 is left to the owner and the main session (DEC-0035).
- **Inputs:** `python3 tools/ledger.py verify` reports "ledger chain intact". The release is ledger seq 20, unchanged. `compare.txt` and F3 are unchanged since 0e55df8 (empty `git diff`). I read only the released paths, `RESULTS.md`, the records, the tool and its constants.
- **Test radius:** `python3 tools/test_impact.py --base 0e55df8` selects `unit: tests/unit/test_tools_findings_build.py`, by the rules tools/<x>.py → its test and `TOOL_DATA_TESTS` for the template and JSON. `lpcstudy/` is unchanged, so there is no integration tier.
- **Checklist before the run:**
  - change set: the tool, template, constants and test file;
  - not run before on this code by me;
  - `JAX_PLATFORMS=cpu`, one thread, `nice -n 19`;
  - the owner's run-2 is active, so I started no preset;
  - quiet output.
- **Run once:** `LPC_THREADS=1 … nice -n 19 tools/run_tests.sh unit tests/unit/test_tools_findings_build.py` gave `67 passed in 8.78s`. `git status` was clean afterwards.
- **Verdict:** **approve**. R1 to R10 are all fixed. The re-review found 3 notes (N1 to N3), none blocking.

### Status of R1 to R10

- **R1: fixed.**
  - Line 106 shows "logit: reduces; indicator: substantial" for every system. The cells are traced to `systems/<s>/Q-N/oracle/{logit_w_interior,w_zero_indicator}/reading` (trace ids 132 to 137), and the values equal the leaves.
  - Line 117 quotes the stored `verdicts.Q-N.by_system` (ids 184 to 186, all "reduces") and says that the stored word collapses the two parts to the logit part. This matches `report.py`, which is left untouched.
  - The owner ruling on the collapse is still open.
- **R2: fixed.**
  - Lines 410 to 476 add two `[CROSS-CHECK]` tables of differing stored words: 11 overall rows and 33 per-system rows.
  - Completeness: an independent walk of both `results.json` files found every string leaf whose key contains "verdict" or is "reading", plus every string under `verdicts/`, that differs. That gives exactly 44 differences (11 under `verdicts/`, 33 under `systems/`), no one-sided leaves, and none under `robustness`. The set equals the document's 44 rows: 0 missing, 0 extra, every official and GPU word identical.
  - Row binding: each row's `official_words` path equals its `crosscheck` path, and each row label (a `meta` value) is the suffix of that path (0 mismatches).
  - Leaf count: 44 string words plus 9 differing `pass` booleans gives the 53 of the compare text, so the sentence at line 410 ("20 lines against 53 … which also include boolean flags") is correct.
  - H3a regimes: lines 466 to 468 read `H3a/chosen_K` (6/4, 4/4, 6/6), consistent with the lengths of `n_per_regime` in each file.
  - Line 476 carries the DEC-0028 item 4 sentence.
  - The plan amendment for `official_words` still awaits the owner.
- **R3: fixed.**
  - Line 470: "No primary part exceeds the bound: failing parts 0, largest z (away) 2.21, bound 3.4".
  - Line 472: the count of differing leaves.
  - Line 474: the per-system GPU gate, with the conclusion "passed on every system".
  - There is no disjunction left. The F3 caption (line 480) is conditional ("A row would name … if there were one").
- **R4: fixed.**
  - Line 499 states N 5 / X 6 / U 7 as `RESULTS.md` (line 429 and its parallels) and the DEF-0027 correction of 2026-10-18 do. It is labeled development evidence and points to `docs/study/lm_doubling_dev0_report_v3.md`.
  - Line 156 adds the pointer under the primary table.
  - The constant `lm_limitation` cites its sources and refers the v3 §8 wording to the owner. v3 is not edited, and that ruling is still open. See N1 for one wording slip.
- **R5: fixed.**
  - Line 338 now reads "handling counters of the main systems" and names `handling.robustness`.
  - Line 370 adds `skipped_variants` 0.
  - Lines 374 to 381 read eight result-count leaves of each system. The trace paths are correct, and every nonzero value equals the `RESULTS.md` Handling tables. For example: `H1b/CP/n_floored` 79/92/114; `H2a/n_excluded_states` 312/72/361; the gain-bound screen-outs 136/46/142, 252/316/250 and 0/1/2.
  - See N2 for one wording slip.
- **R6: fixed.**
  - Lines 278 to 326 hold a traced table of 15 reported quantities per system. I checked each leaf mapping against its label, and the definitions against `analysis.py`: `stability` is "the share of the B resamples with D > 0", and `n_excluded_states = n_states − n_eligible`.
  - The values equal the leaves and, where `RESULTS.md` prints them, its text: N̂ 0.656/0.6078/0.6295 against "N 0.66/0.61/0.63"; H1c CP 0.4947 [0.4664, 0.5374] against "CP 0.495 [0.466, 0.537]".
  - Line 328 explains A4 − A1 from the stored `best_single` (A1 on all three systems; ids 839 to 841).
- **R7: fixed.**
  - Line 120 says the reading is "pre-registered … not tested here" and lists the failing parts per system, traced (ids 188 to 191): lorenz63 (ii) interior; rossler (i); chua (i) and (ii) interior. These equal the stored part words.
  - The line quotes the v3 §7 precision sentence verbatim.
- **R8: fixed.** "H2c (secondary)" is labeled, and H2e and H3a have bullets under "Secondary rows", whose words equal `verdicts`.
- **R9: fixed.**
  - The F2 caption (line 332) names the square for both Q-N readings and for "reported".
  - In the rebuilt F2 every tick label is readable, with at most four ticks and a shared power-of-ten offset (×1e-2, ×1e-3, ×1e-4, ×1e-5). I re-read the markers against §6, for example "H2c A4o − A2 rossler" −0.925e-4 within [−2.04, −0.15]e-4, and "H2c A4 − A2 chua" −0.84e-3.
  - In the rebuilt F1, the H2b(ii) panel at ×1e-2 matches its table.
- **R10: fixed.** Line 385 explains the hw ratio. The direction is confirmed in `tools/compare_runs.py` (`hw1/hw0` with hw0 = REF = official), and recomputing from the two stored intervals for chua H3c gives 3.036.

### Regression checks

- **(a) Trace.**
  - The independent resolver, now also mapping `official_words` to the official file, resolved all 1260 rows: 0 raw-value mismatches, 0 rounding mismatches, 0 position mismatches.
  - There are 285 rows that are new or changed against the 0e55df8 trace, compared as (source, path, rendered, tag). I drew 20 with `random.Random(202610201).sample(...)`: ids 743, 762, 776, 788, 826, 835, 962, 968, 973, 981, 990, 1087, 1116, 1119, 1129, 1147, 1153, 1156, 1167 and 1205.
  - I re-read each by direct key access in the CPU or GPU `results.json` or `design_constants.json`, and all equal the document. For example: 788 is rossler `complete_case/n_states` 657; 835 is chua `nhat/interval` [0.5753, 0.681]; 1119 is `verdicts/H2d/verdict` "inconclusive" beside GPU "not supported"; 1205 is chua `H2c/A4_minus_A1/verdict` pass → inconclusive.
- **(b) Verdict-difference tables:** complete and exact, as stated under R2.
- **(c) Q-N row, LM limitation and new tables:** checked against the JSON and `RESULTS.md`, as stated under R1, R4, R5 and R6.
- **(d) `official_words`.**
  - `ALLOWED` in `tools/findings_build.py` permits it only under `CROSS-CHECK`. The untagged set and the PRE-REGISTERED, DIAGNOSTIC, DEVELOPMENT and STUDENT sets exclude it.
  - All 47 `official_words` rows in the trace are tagged CROSS-CHECK.
  - `test_cross_tag_violation_is_refused` plants it in the PRE-REGISTERED, DIAGNOSTIC, DEVELOPMENT and untagged sections and requires "not allowed" each time; the test passed in my run. `check` re-renders the document, so a hand edit cannot place it elsewhere.
  - No leak was found. See N3 for its breadth inside CROSS-CHECK.
- **(e) F2 tick labels and legend:** see R9.
- **(f) Labeling.**
  - Lines 1 and 2 and every `#` heading are identical to 0e55df8 (`diff` empty), so the tags are unchanged.
  - Appendix A still holds no development numbers. §11 is still the prompt, and §9 has no dated line.
  - A case-insensitive grep for confirm, prove, demonstrat, signific, "shows that" and breakthrough finds only "confirmatory" in the label and provenance rows.

### New findings

- **N1 (note): the projection wording in the LM limitation is too narrow.**
  - **Location:** line 499, constant `lm_limitation`.
  - **What is wrong:** it says the projection uses "the square root of the ratio of the numbers of test states". For H2b(i) and H2b(ii), `RESULTS.md` projects by sweep states (lines 483 and 509: "300 → 1000 sweep states", ×1.83). Test states (×1.41) apply only to H2a and H3c.
  - **Fix:** "of the numbers of test or sweep states", or quote √(n_full/n_pilot).
- **N2 (note): "All result counts" overstates what `RESULTS.md` lists.**
  - **Location:** line 338.
  - **What is wrong:** the sentence says "All result counts are listed in the Handling section of RESULTS.md". `RESULTS.md` lists only nonzero result counts. For example, lorenz63 `gain_bound/n_screened_out/censored_single_forecaster` (0, shown at line 381) is absent from its lorenz63 table.
  - **Fix:** "All nonzero result counts …".
- **N3 (note): `official_words` is not limited to verdict words.**
  - **Location:** `tools/findings_build.py`, `ALLOWED` and the comment at lines 222 to 225.
  - **What is wrong:** the source is restricted by tag only. Inside `[CROSS-CHECK]` it can quote any official leaf in any format, and it already quotes a number (`H3a/chosen_K`, line 466).
  - **Impact:** it cannot leak outside CROSS-CHECK, which (d) confirms.
  - **Suggestion:** for the owner's reading of the A6 amendment, either say in the comment and the plan amendment that it covers verdict words and the regime count, or limit its leaves to `verdict`/`reading`/`chosen_K`.

### Still open for the owner (not reviewer findings)

- The A6 amendment (`official_words`).
- The v3 §8 wording of the DEF-0027 count.
- The Q-N collapse in `report.py` (verdict and report code: needs owner review before any change).
