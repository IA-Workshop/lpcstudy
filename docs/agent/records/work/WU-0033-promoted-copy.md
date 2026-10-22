# WU-0033: promoted-copy mode of `tools/findings_build.py`

| Field | Value |
| --- | --- |
| Status | in progress (plan written before code, 2026-10-22) |
| Class | CSQ3 (tool); its output is used at CSQ2 by the owner after the promotion entry |
| Agent(s) | claude-sonnet-5-5 (developer), branch `wu/promoted-copy` from develop `8eb3995` |
| Estimate | small |

## Plan (written before execution)

- **Scope.** A new command `findings_build.py promote --document <preliminary .md> --out <new .md>` that writes a copy of the findings document with only the pre-promotion labels removed, and checks by machine that the difference between the two documents is exactly that list. In: the copy, the check, the diff summary, tests. Out: removing labels from anything automatically at promotion time (the mode only produces a copy for the owner to place after the promotion entry); the trace, `sources.json`, `compare.txt` and the figures (not touched; the PNG figures carry the status line drawn in their titles and are not re-rendered); the ledger; `lpcstudy/`; the sealed files; `check` (it keeps refusing an edited document, so the promoted copy is not a `check` input; its source, the preliminary document, still passes `check`).
- **The exact label list** (from the template `tools/findings/preliminary.template.md`, the builder's `PRELIMINARY_LINE` and verdict format, ROADMAP WU-0018.3 "header label removed from the promoted copy only", QA.11, and the promotion proposal section 6 item 4). Nothing else is changed. Each rule is an exact string:
  1. **H-DEL** Delete the first three lines: the banner `**CONFIRMATORY: UNPROMOTED**`, the `PRELIMINARY_LINE` ("PRELIMINARY: internal to the owner and the student until promotion (QA.11, LPC.PC.13)."), and the one blank line after them.
  2. **R-TITLE** `# Preliminary findings for seed ` becomes `# Findings for seed `.
  3. **R-RULE** The sentence ` A "supported" verdict is always written "supported (preliminary, unpromoted)".` (with its leading space) is removed (it explains a status wording that no longer applies).
  4. **R-WORD** `supported (preliminary, unpromoted)` becomes `supported` (verdict cells and bullets), applied after R-RULE.
  5. **R-RUN** ` in this preliminary, unpromoted run` becomes ` in this run`.
  - **Kept on purpose:** the provenance row `| Label | CONFIRMATORY: UNPROMOTED |` quotes the label stored in the sealed `results.json`, which is not edited (ROADMAP: only the header label is removed on the copy). It is the only line allowed to contain "UNPROMOTED" or "preliminary" after the substitution; any other residue makes the command fail (a label this list does not know about must be added to the list by a reviewed change, not removed silently). The dated free-slot lines, the limitation bullets (including "PROPOSED" wording, which a ruling already replaced) and the trace are untouched.
- **Safeguards.** The command refuses `--out` equal to `--document` (real paths), refuses an existing `--out`, and never writes anywhere else; the input is read only and its bytes are unchanged (tested). It fails (exit 1, nothing written) if the document does not start with the three header lines, if a rule matches nowhere, or if a residual label remains.
- **Machine check.** `verify_label_diff(preliminary, promoted)` compares the two texts line by line with `difflib` and accepts only: the header deletion as the first hunk; `replace` hunks of equal line count in which every new line equals the old line with the rules applied; everything else equal. Any insert, any other delete, any changed line not explained by a rule is a problem. It prints a summary: lines in and out, the deleted header lines, and per rule the number of lines changed. Verdict words, numbers and traced values are covered because every line outside the rule substitutions is byte-equal.
- **Definition of done.** The command and check exist; tests pass; the plan list above is the implemented list; run on the real document (output in a scratch directory, not committed) it exits 0 with a summary; the real preliminary document, trace and sources are byte-unchanged (`git status` clean for them).
- **Acceptance criteria (fixed now).**
  1. Reference independent of the code: a small hand-written preliminary text (30 lines or fewer) and a hand-written expected promoted text; the output equals the expected text byte for byte (tolerance: exact, strings).
  2. Any extra change in a promoted text (a changed digit, a changed verdict word, an inserted or deleted line, a restored label in another place) makes `verify_label_diff` report a problem, one test per kind.
  3. The input file's bytes are identical before and after `promote`; `--out` equal to the input, or an existing `--out`, is refused with nothing written.
  4. A document with a residual unknown label (for example "Preliminary" in another sentence) is refused.
  5. The real document at this commit promotes with exit 0 and the diff summary shows exactly the rules above (checked by hand once and recorded in the log).
  6. The existing 67 tests of `tests/unit/test_tools_findings_build.py` still pass.
- **Affected checks (blast radius).** `tools/findings_build.py` maps to `tests/unit/test_tools_findings_build.py` (rule: tool to its test file), run once.

## Log

- 2026-10-22 4.9 checklist: (1) change set `tools/findings_build.py`, `tests/unit/test_tools_findings_build.py`, this file, `docs/agent/notes/2026-10-22-promotion-proposal.md`. (2) Radius `tests/unit/test_tools_findings_build.py` (rule: tool to its test file), once. (3) Already run on this code: no. (4) CPU. (5) The ledger and the sealed files were not touched; the real document was promoted into a scratch directory only.
- Tests (written before the code): 12 new (hand-written reference and expected copy; seven kinds of extra change each fail the check; unknown residual label refused; missing header refused; the command leaves the input bytes unchanged and refuses an existing or identical `--out`; the summary lines). Result: `79 passed in 7.94s` (67 existing plus 12 new); no test failed on the first run.
- Real document at this commit, `promote` into a scratch directory: exit 0; preliminary 553 lines, promoted 550; header lines deleted 3; R-TITLE 1, R-RULE 1, R-WORD 4, R-RUN 2 lines; one residual label kept (the provenance label row); `diff` shows 15 changed lines, all of them the rules above (checked by eye once). The preliminary document, trace and sources are unchanged (`git status`). Acceptance criteria 1 to 6 met.
- `black` is not installed in the project venv; the code was written in the file's style (not run through black).
- `ledger.py append --files` question (answered on a temporary copy of the tool and of the ledger): see the proposal note section 7; it accepts any existing file and records name and sha256; no entry is written for a missing file; the real ledger was not run.

## Review

- **Reviewer:**
- **Findings and resolution:**

## Audit

- Is the definition of done met?
- Defects recorded:
- Notes for successors:
