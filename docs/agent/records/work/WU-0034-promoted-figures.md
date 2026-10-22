# WU-0034: promoted figures and pointers for the promoted copy

| Field | Value |
| --- | --- |
| Status | in progress (plan written before code, 2026-10-22) |
| Class | CSQ3 (tool); its output is used at CSQ2 by the owner after the promotion entry |
| Agent(s) | claude-sonnet-5-5 (developer), branch `wu/promoted-figures` from `wu/promoted-copy` eeb7123 (WU-0033) |
| Depends on | WU-0033 (the `promote` mode and its allowed-edit check); both must be reviewed and merged before the owner uses the output |

## Plan (written before execution)

The owner chose option (a) of `docs/agent/notes/2026-10-22-promotion-proposal.md` section 9: re-render F1 to F3 with a promoted status title through a reviewed change, instead of copying them with a note or omitting them.

- **Scope.** `findings_build.py promote` also (1) re-renders F1, F2 and F3 from the same sources and the same code as the preliminary build, changing only the figure title, into a new figures directory next to `--out`; (2) points the promoted copy's three image links at that directory; (3) replaces the appendix C pointer sentence; (4) checks all of it and fails closed. Out: the preliminary document, trace, sources and figures (never written; hashes before and after are tested); `lpcstudy/`; the sealed files; the four `RESULTS.md` figures (they carry no status text); the ledger; the choice to promote.
- **Exact promoted title.** Two lines, the same font size (8) and number of lines as the original title, so the layout (`tight_layout`) is identical:
  - line 1: `FINDINGS FOR SEED <seed id>` (the seed id read from the official provenance, here CONF-1). Dated amendment 2026-10-22: it is in capitals because the original line 1 has no descender and matplotlib sizes a text line from its glyphs; the first draft `Findings for seed ...` (with a "g") made the title 0.56 px taller and moved every panel (measured), so the pixel criterion needs a line with the same glyph class;
  - line 2: `Result promoted by the owner (QA.11, LPC.PC.13)`.
  It contains none of the words "unpromoted", "preliminary" or "confirmatory" (case-insensitive). The original title is `<provenance label>` plus the PRELIMINARY line. Panel titles, the experiment and v3 identifier labels, level and interval-procedure texts, the F3 footer and all captions are unchanged.
- **Allowed edits added to the independent check** (a separate table from the substitution table, with dynamic parts built from the input and output file stems `S` and `D`):
  - E-FIG: `(S.figures/` becomes `(D.figures/` (the three image links; the figures are written to `D.figures` next to `--out`; if `S` equals `D` the edit is the identity and the directory is still a different path).
  - E-TRACE: the appendix C sentence "Every number quoted above is listed with its source and leaf path in `S.trace.csv`. Run the `check` command of `tools/findings_build.py` on this directory to verify the document against the sources." becomes (dated amendment 2026-10-22: "preliminary" replaced by "source", because the residual-label check refuses that word): "Every number quoted above is listed with its source and leaf path in the trace file of the source document (the version before promotion), which stays beside that document and not in this directory. The `check` command of `tools/findings_build.py` verifies the source document against the sources; it does not apply to this promoted copy, whose only differences from it are the removed labels, the three figure links and this sentence." (no digits).
  - After the edits no line may contain `S.figures/` or `S.trace.csv` (a pointer left behind is a problem).
- **Fail closed.** Figures are rendered into a temporary directory and checked first; the promoted text is written with mode `x` and checked on the bytes read back; only then is the figures directory moved into place. On any failure (render error, banned word in a figure text, band check, text check) the promoted file and the new figures directory are removed and nothing else exists; exit 1 for a failed check, 2 for an input error (for example the sources file next to the document is missing while the document has image links; `--no-figures` skips figures and leaves the links, for hand-written texts).
- **Acceptance criteria (fixed now; tolerance zero where stated).**
  1. **Determinism (title is the only change).** Rendering the figures with the ORIGINAL title through the same code reproduces the committed F1 to F3 PNG files byte for byte. Method: `findings_build.py check` already re-renders the three PNGs in a temporary directory and compares the bytes with the committed ones; the test repeats this directly on the committed document and prints the three equalities; documented command `findings_build.py check docs/agent/notes --stem 2026-10-20-prelim-findings-conf1`.
  2. **Pixel difference.** For each of F1, F2 and F3, read the committed PNG and the promoted PNG as arrays (matplotlib `imread`, independent of the renderer). Same shape. Band: from row 0 down to the first all-white row after the first non-white row of the committed (original) image, that is, the rows of the original title text. Outside the band the arrays are equal, tolerance 0 (exact equality of every channel value). Inside the band they differ (the title changed).
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

## Review

- **Reviewer:**
- **Findings and resolution:**

## Audit

- Is the definition of done met?
- Defects recorded:
- Notes for successors:
