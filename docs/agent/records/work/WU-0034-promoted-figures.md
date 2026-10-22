# WU-0034: promoted figures and pointers for the promoted copy

| Field | Value |
| --- | --- |
| Status | in progress (plan written before code, 2026-10-22) |
| Class | CSQ3 (tool); its output is used at CSQ2 by the owner after the promotion entry |
| Agent(s) | claude-sonnet-5-5 (developer), branch `wu/promoted-figures` from `wu/promoted-copy` eeb7123 (WU-0033) |
| Depends on | WU-0033 (the `promote` mode and its allowed-edit check); both must be reviewed and merged before the owner uses the output |

## Plan (written before execution)

The owner chose option (a) (recorded as DEC-0043) of `docs/agent/notes/2026-10-22-promotion-proposal.md` section 9: re-render F1 to F3 with a promoted status title through a reviewed change, instead of copying them with a note or omitting them.

- **Scope.** `findings_build.py promote` also (1) re-renders F1, F2 and F3 from the same sources and the same code as the preliminary build, changing only the figure title, into a new figures directory next to `--out`; (2) points the promoted copy's three image links at that directory; (3) replaces the appendix C pointer sentence; (4) checks all of it and fails closed. Out: the preliminary document, trace, sources and figures (never written; hashes before and after are tested); `lpcstudy/`; the sealed files; the four `RESULTS.md` figures (they carry no status text); the ledger; the choice to promote.
- **Exact promoted title.** Two lines, the same font size (8) and number of lines as the original title, so the layout (`tight_layout`) is identical:
  - line 1: `FINDINGS FOR SEED <seed id>` (the seed id read from the official provenance, here CONF-1). Dated amendment 2026-10-22: it is in capitals because the original line 1 has no descender and matplotlib sizes a text line from its glyphs; the first draft `Findings for seed ...` (with a "g") made the title 0.56 px taller and moved every panel (measured), so the pixel criterion needs a line with the same glyph class;
  - line 2: `Result promoted by the owner (QA.11, LPC.PC.13)`.
  It contains none of the words "unpromoted", "preliminary" or "confirmatory" (case-insensitive). The original title is `<provenance label>` plus the PRELIMINARY line. Panel titles, the experiment and v3 identifier labels, level and interval-procedure texts, the F3 footer and all captions are unchanged.
- **Allowed edits added to the independent check** (a separate table from the substitution table, with dynamic parts built from the input and output file stems `S` and `D`):
  - E-FIG: `(S.figures/` becomes `(D.figures/` (the three image links; the figures are written to `D.figures` next to `--out`; if `S` equals `D` the edit is the identity and the directory is still a different path).
  - E-TRACE: the appendix C sentence "Every number quoted above is listed with its source and leaf path in `S.trace.csv`. Run the `check` command of `tools/findings_build.py` on this directory to verify the document against the sources." becomes (dated amendment 2026-10-22: "preliminary" replaced by "source", because the residual-label check refuses that word): "Every number quoted above is listed with its source and leaf path in the trace file of the source document (the version before promotion), which stays beside that document and not in this directory. The `check` command of `tools/findings_build.py` verifies the source document against the sources; it does not apply to this promoted copy, whose only differences from it are the removed labels, the three figure links and this sentence." (no digits).
  - After the edits no line may contain `S.figures/` or `S.trace.csv` (a pointer left behind is a problem).
- **Fail closed.** Figures are rendered into a temporary directory and checked first; the promoted text is written with mode `x` and checked on the bytes read back; only then is the figures directory moved into place. On any failure (render error, banned word in a figure text, band check, text check) the promoted file and the new figures directory are removed and nothing else exists; exit 1 for a failed check (including a banned word found in a figure text), 2 for an input error (for example the sources file next to the document is missing while the document has image links; `--no-figures` skips figures and leaves the links, for hand-written texts).
- **Acceptance criteria (fixed now; tolerance zero where stated).**
  1. **Determinism (title is the only change).** Rendering the figures with the ORIGINAL title through the same code reproduces the committed F1 to F3 PNG files byte for byte. Method: `findings_build.py check` already re-renders the three PNGs in a temporary directory and compares the bytes with the committed ones; the test repeats this directly on the committed document and prints the three equalities; documented command `findings_build.py check docs/agent/notes --stem 2026-10-20-prelim-findings-conf1`.
  2. **Pixel difference.** For each of F1, F2 and F3, read the committed PNG and the promoted PNG as arrays (matplotlib `imread`, independent of the renderer). Same shape. Band: from row 0 down to the first all-white row after the first non-white row of the committed (original) image, that is, the rows of the original title text. Outside the band the arrays are equal, tolerance 0 (exact equality of every channel value). Inside the band they differ (the title changed).
  - **Dated amendment to criterion 2 (2026-10-22, after the first measurement; review R1).** The literal first rule ("the first all-white row after the first non-white row") stopped between the two title lines, which contradicts the criterion's own wording "the rows of the original title text". The rule used is: the band ends at the end of the **second run of ink rows** (rows with a non-white pixel) of the ORIGINAL image, that is the two title lines, and nothing below it. Tolerance stays zero outside the band. Rejected alternative: a run of 12 white rows as the end of the title; it works on F1 and F3 but on F2 the gap between the title and the first panel title is only 8 rows, so that band would have reached into the panels and hidden differences there (a loosening). Measured bands (rows from the top): F1 48, F2 66, F3 53; the white margin between the band and the first panel content is 26, 8 and 23 rows (reviewer's measurement).
  3. **No banned words in figure text.** Every text object of the promoted figures (found with `figure.findobj(Text)`) and the PNG metadata contain none of "unpromoted", "preliminary", "confirmatory" (case-insensitive); the title strings are checked at their source.
  4. **Fail closed.** With the figure renderer made to raise, to emit a changed panel, or with a banned word planted in the title, `promote` exits non-zero and no promoted file and no figures directory exist.
  5. **Untouched.** The sha256 of the preliminary document, its trace, sources and the three PNGs are equal before and after `promote` (test).
  6. **Text check.** The promoted text equals the preliminary one with the WU-0033 label edits, E-FIG and E-TRACE only (independent check; hand-written reference for the two new edits; an extra change fails).
  7. The existing tests still pass.
- **Affected checks.** `tools/findings_build.py` maps to `tests/unit/test_tools_findings_build.py`, run once through `tools/test_impact.py`'s radius.
- **Proposal update.** Section 8 and 9 of the promotion proposal are updated to option (a), with the exact commands, and a note that WU-0033 and WU-0034 must be reviewed and merged first.

## Log

- 2026-10-22 4.9 checklist: (1) change set `tools/findings_build.py`, `tests/unit/test_tools_findings_build.py`, this file, `docs/agent/notes/2026-10-22-promotion-proposal.md`. (2) Radius `tests/unit/test_tools_findings_build.py` (rule: tool to its test file), once. (3) Already run on this code: no. (4) CPU. (5) The ledger and sealed files untouched; the real document was promoted into a scratch directory only.
- Findings while coding (kept as measured): (a) with the title `Findings for seed ...` every panel moved: the title was 27.79 px high against 27.23 px, because matplotlib sizes a text line from its glyphs and the lower-case "g" is a descender the original line 1 lacks; line 1 is now in capitals (plan amended above). (b) The first band rule (first white row after the title) ended between the two title lines; the second (a run of 12 white rows) fails on F2, where the gap from the title to the first panel title is 8 rows; the final rule is the end of the second run of ink rows (the two title lines), measured 48, 66 and 53 rows for F1, F2, F3. (c) The new appendix C sentence first said "preliminary document" and the residual-label check refused it; "source document" is used (plan amended above).
- Real document, `promote` into a scratch directory: exit 0; 553 to 550 lines; R-TITLE 1, R-RULE 1, R-WORD 4, R-RUN 2, E-FIG 3, E-TRACE 1; figures written to `report.figures/`; sha256 of the preliminary document, trace, sources and the three PNGs equal before and after.
- Byte reproduction (criterion 1): `findings_build.py check docs/agent/notes --stem 2026-10-20-prelim-findings-conf1` re-renders F1 to F3 in a temporary directory and compares bytes; the test `test_original_title_reproduces_the_committed_png_bytes` does the same on a confirmatory fixture build (all three equal, and `run_check` returns 0). Result for the committed document: `check passed: 1266 traced values, 0 problems` (figures equal a fresh render).
- Tests: 6 new test functions (8 cases with the parametrized ones) added to the 82; result `90 passed in 13.25s`. All first-run passes; fail-closed cases (renderer raises, planted banned word, moved panel) each leave the directory empty and the preliminary files byte-equal.
- 2026-10-22 fix round 1 (review R1 to R5; developer claude-sonnet-5-5). 4.9 checklist: (1) change set `tools/findings_build.py`, `tests/unit/test_tools_findings_build.py`, this file, the promotion proposal; (2) radius `tests/unit/test_tools_findings_build.py`, once; (3) already run on this code: no; (4) CPU; (5) ledger and sealed files untouched.
  - R1: dated amendment added under criterion 2 (rule, reason, rejected alternative, measured bands 48, 66, 53 and margins 26, 8, 23). R2: the temporary directory is created beside `--out` (`TemporaryDirectory(dir=dst.parent)`), the figures folder is registered for cleanup before the move, and the move failing midway (test: a patched `shutil.move` that leaves a partial folder and raises) leaves no copy and no folder; `--out` in a missing folder is refused. R3: a banned word in a figure text is a failed check (`FigureLabelError`, counted, exit 1, as the plan says); the test now expects 1. R4: the two pointer edits of the check table are written as their own literals in `allowed_edits`; proposal section 9 now says the command checks the figure texts and that the PNG metadata is checked in the tests only. R5: DEC-0043 cited in the plan and in proposal section 9.
  - Result: `92 passed in 13.91s` (90 plus 2 new tests).

## Review

- **Reviewer:** `reviewer`, claude-opus-5-5, fresh context, 2026-10-22, commits ef38a8f and 79442d4 (diff eeb7123..79442d4).
- **Checks run** (worktree clean before and after; ledger and main untouched).
  - **(i) Byte reproduction.** `findings_build.py check docs/agent/notes --stem 2026-10-20-prelim-findings-conf1` with the project venv printed `check passed: 1266 traced values, 0 problems` (exit 0). It re-renders F1 to F3 with the original title and compares their bytes. The committed document was not rebuilt.
  - **(v) Untouched.** I took the sha256 of the preliminary `.md`, `.trace.csv`, `.sources.json`, `.compare.txt` and the three PNGs, then ran `promote --out <scratch>/out/report.md`. It exited 0 with E-FIG 3 and E-TRACE 1 and wrote `report.figures/`. Afterwards all 7 hashes were `OK`.
  - **(ii) Independent pixel check.** My own script reads both PNG sets with PIL as uint8 arrays, not with matplotlib's `imread`.
    - For each of F1, F2 and F3 the shapes are equal.
    - The rows that differ are exactly 16–47, 34–65 and 21–52 (26 rows each). These are the two title ink runs of the original: (16,27)+(33,48), (34,45)+(51,66) and (21,32)+(38,53).
    - The next ink run (panel titles) starts at row 74, 74 and 76, so the band ends 26, 8 and 23 white rows above any panel content.
    - The promoted images have the same ink-run structure, so the layout did not move.
    - The PNG metadata of both sets holds only `dpi`.
  - **Visual check.** I viewed all three promoted PNGs. Each title reads "FINDINGS FOR SEED CONF-1 / Result promoted by the owner (QA.11, LPC.PC.13)". Panels, markers, verdict words, levels, the F3 bound line and the F3 gate footer look the same as the committed F1.
  - **(vi) Tests.** `tools/run_tests.sh unit tests/unit/test_tools_findings_build.py`, run once: `90 passed in 13.04s`.
- **Judgments asked for.**
  - **Capitalized title line (plan amendment): legitimate.**
    - It changes the product (the title string), not the criterion. Tolerance stays 0 outside the band.
    - The cause is recorded with the measurement (27.79 against 27.23 px).
    - My pixel check confirms that layout and ink rows are identical.
    - The owner should know that line 1 is in capitals for this reason.
  - **Band rule: legitimate in substance, but not recorded in the criterion (R1).**
    - Criterion 2 defined the band as "the rows of the original title text". Its literal rule (first white row after the first ink) stopped between the two title lines, so the rule contradicted its own stated intent.
    - The final rule (end of the second ink run) is taken from the original image only. It covers exactly the two title lines and no panel content (verified above).
    - The developer rejected a rule that would have loosened the check: the 12-white-row run, which on F2 would have reached into the panels.
    - It is not a loosening. It is a mis-specified criterion corrected to its own intent, and it should be written as such.
  - **(iii) Banned words.**
    - `banned_figure_text` runs inside `Builder.figure`, so on its own it is not independent of the render code.
    - Independence comes from two other checks: the zero-tolerance pixel comparison (everything outside the title is identical to the committed figures, which carry no banned word outside the title), and `promoted_title` checked at its source.
    - PNG metadata is checked independently with PIL, in the test only.
    - Acceptable. See R4 on how the proposal words this.
  - **(iv) New Appendix C wording.** It has no digits and none of the words "preliminary", "unpromoted" or "confirmatory".
    - "Source document (the version before promotion)" is accurate.
    - "Only differences from it are the removed labels, the three figure links and this sentence" is accurate for the text: the title rename and the R-RULE sentence count as label removals.
    - It does not mention that the linked images carry a different title, and it does not say where the source document is. These are wording choices for the owner, not inaccuracies.
- **Findings and resolution:**
  - **R1 (minor). The band rule in acceptance criterion 2 differs from the rule implemented, and the plan text was not amended.** The plan's criterion 2 still states the first-white-row rule. The rule actually used (`title_band_end`, `tools/findings_build.py:2798`) appears only in Log (b).
    - Why it matters: a criterion changed after measuring must be visible where the criterion is stated (PRIME.2), and the judgment above depends on it.
    - Fix: add a dated amendment under criterion 2 that states:
      - the rule used (end of the second ink run of the original image);
      - the reason (the literal rule cut through the title, contrary to "the rows of the original title text");
      - the rejected alternative;
      - the measured bands (48, 66, 53) and the white margin to the panels.
  - **R2 (minor). There is a fail-closed gap on a move across filesystems.** `:2917`, `:2936`–`:2937`.
    - The figures are rendered in `tempfile.TemporaryDirectory()`, which defaults to `/tmp`, and are then moved with `shutil.move` to `report.figures/` in the repository.
    - Across filesystems this is a copy followed by a delete. If the copy fails partway, `figures_dst` is not yet in `created`, so a partial directory is left behind next to the copy whose text has already been written. That contradicts "nothing is left behind".
    - Fix: either create the temporary directory in `dst.parent` (`tempfile.TemporaryDirectory(dir=dst.parent)`, so the move is an atomic rename), or append `figures_dst` to `created` before the move. Add a test that makes the move raise.
  - **R3 (minor). The exit code for a banned word differs from the plan.** The plan's Fail-closed paragraph lists "banned word in a figure text" among the failures that exit 1. The code raises `ToolError` (`:1279`), so the command exits 2, and the test asserts 2.
    - Fix: either make it a counted check problem (exit 1), or record the deviation as a dated plan note, as was done for WU-0033.
  - **R4 (minor). The pointer edits share constants with the substitution, and the proposal overstates what the command checks.**
    - `allowed_edits` (`:2730`) builds E-FIG and E-TRACE from the same `trace_sentence_old` and `TRACE_SENTENCE_NEW` that `promote_rules` uses. Unlike the label edits of `ALLOWED_EDITS`, these two edits are not an independently written table. The hand-typed `FIG_PROMOTED` test reference does pin both sentences, which limits the risk.
    - Fix: write the old and new Appendix C sentences, and the link form, as their own literals in the check table.
    - Separately, proposal §9 line 150 lists "no figure text or PNG metadata holds ..." among the things the command checks. The command checks figure texts (in the renderer) but not the PNG metadata, which only the test checks.
    - Fix: say "(metadata: tested)", or add a metadata read-back in `verify_title_only`.
  - **R5 (minor, for the main session). The owner's choice of option (a) is not on record.**
    - Proposal §9 is headed "decided 2026-10-22: option (a)", and the plan opens with "The owner chose option (a)". I found no entry for this choice in `docs/agent/records/decisions.md` or in the ledger.
    - Why it matters: the content of the promoted report is an owner judgment (GOV.50), and the agent text should cite the owner's words.
    - Fix: the main session records the owner's words in the decision log, and §9 cites that entry.
- **Items checked with no finding.**
  - **(vii) Proposal §8 is runnable in order** once WU-0033 and WU-0034 are merged: mkdir, three `cp` commands, `promote` (writes `report.md` and `report.figures/`; it refuses if either exists), `sed`, `diff`, `grep`, then `find | xargs sha256sum`, which hashes `figures/` and `report.figures/`.
  - **Fail-closed.** The command refuses an existing `--out` or an existing figures directory, a symlink, an input used as output, and a missing `sources.json` (exit 2). It renders and checks before it writes. On a failed check it removes the copy. A pointer left behind is a problem.
  - **The tests.**
    - They use hand-typed pointer texts.
    - The band is computed by the tests' own code, with a sanity range.
    - PIL checks the metadata.
    - The fail-closed cases are: the renderer raises, a banned word is planted, a panel is moved.
    - The build directory is hash-checked.
    - No test compares the code with itself.
  - **Reproducibility and scope.** float64 is untouched, and no randomness is involved. Commit trailers are present. Changes are confined to `tools/`, `tests/` and the notes. `lpcstudy/`, the ledger and the sealed files are untouched.
  - **Owner checkpoint.** No verdict, statistics, seed or provenance code and no dependencies are touched. The owner inspects the promoted figures at WU-0018.3.
- **Verdict: approve with fixes** (R1 to R5 minor; 5 findings).
- **Re-review, fix round 1** (`reviewer`, claude-opus-5-5, 2026-10-22, diff 19ad101..2432a3c; covers R1 to R5 only).
  - **Checks run.**
    - Radius: `tools/run_tests.sh unit tests/unit/test_tools_findings_build.py`, run once: `92 passed in 14.04s`.
    - Real document: `promote` into a new scratch folder. It exited 0 with the same counts as before.
    - All 4 output files (`report.md` and the three PNGs) are sha256-identical to the round-0 output.
    - No temporary folder is left beside `--out`.
    - The 7 preliminary files (document, trace, sources, compare, F1 to F3) have unchanged hashes, and the worktree is clean.
  - **R1 fixed.** The dated amendment under criterion 2 states the rule, the reason, the rejected alternative and the measured values, and all of them are accurate:
    - **rule:** the end of the second ink run of the original image;
    - **reason:** the literal rule cut between the title lines, contrary to "the rows of the original title text";
    - **rejected alternative:** 12 white rows. It holds on F1 and F3. On F2 the title-to-panel gap is 8 rows, so that band would reach into the panels.
    - **bands:** 48, 66 and 53 rows;
    - **margins:** 26, 8 and 23 rows. I checked these against my own PIL ink-run measurement: the first panel ink starts at rows 74, 74 and 76, so 74−48=26, 74−66=8 and 76−53=23.
  - **R2 fixed.**
    - `TemporaryDirectory(dir=dst.parent)` makes the final move a same-filesystem rename.
    - `figures_dst` is registered for cleanup before `shutil.move`.
    - A missing output folder is refused (exit 2).
    - The new test patches `shutil.move` to leave a partial folder and raise. It shows that neither the copy nor the folder is left behind and that the build's hashes are unchanged.
  - **R3 fixed.**
    - `FigureLabelError` is caught around the render and counted as a problem, so nothing is written and the command exits 1.
    - The plan's Fail-closed text now says this, and the test expects 1.
  - **R4 fixed.**
    - `allowed_edits` writes the old and new Appendix C sentences as their own literals.
    - Proposal §9 now says the command checks the figure text objects, while PNG metadata (resolution only) is checked in the tests.
    - Note, not a finding: `test_promote_reads_the_pointer_edits_from_its_own_table` asserts `new == fb.TRACE_SENTENCE_NEW`, which compares two copies in the code with each other. It is a consistency guard, not evidence. The independent reference remains the hand-typed `FIG_PROMOTED`. Labelling the docstring "regression guard" would make that explicit.
  - **R5 fixed.**
    - DEC-0043 exists on develop at 52a6f2e, with the owner's verbatim words "option a".
    - It is cited in the plan's first line and in the heading of proposal §9.
    - Its reading matches §9:
      - F1 to F3 are re-rendered with a promoted title into a separate folder, and the preliminary figures are untouched;
      - the checks are byte reproduction and zero tolerance outside the title band;
      - the `RESULTS.md` figures are copied as they are;
      - the provenance row keeps the stored label.
    - The DEC-0043 text itself is on develop, not on this branch; it arrives with the merge.
  - **Re-review verdict: approve** (R1 to R5 fixed; no new findings).

## Audit

- Is the definition of done met?
- Defects recorded:
- Notes for successors:
