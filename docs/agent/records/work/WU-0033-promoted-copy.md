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

- 2026-10-22 fix round 1 (review R1 to R6; developer claude-sonnet-5-5). 4.9 checklist: (1) change set `tools/findings_build.py`, `tests/unit/test_tools_findings_build.py`, `docs/agent/notes/2026-10-22-promotion-proposal.md`, this file; (2) radius `tests/unit/test_tools_findings_build.py`, once; (3) already run on this code: no (the code changed); (4) CPU; (5) no ledger, no sealed file touched.
  - **Plan amendment (dated note, nothing loosened):** exit codes follow the tool's docstring: 0 success, 1 the machine check failed, 2 usage or input error. The refusals of the header, an unmatched rule, a residual label and an existing or identical `--out` are input errors and exit 2 (the plan's "fails (exit 1 ...)" is read as: fails with nothing written). A failed machine check exits 1 and deletes the output.
  - R1 fixed: `verify_label_diff` no longer calls the substitution. It aligns the lines with `difflib`, accepts only the header deletion, equal lines and equal-length replaced runs whose new lines equal the old lines under a separate table `ALLOWED_EDITS`, and rejects any remaining label outside the kept provenance row. `promote()` writes with mode `x`, reads the bytes back, checks them, and deletes the output (exit 1) on any problem. New test: the substitution is monkeypatched to change a digit; the command exits 1 and no file is left.
  - R2 and R6 fixed in proposal section 8 (`promote` is the live command; `RESULTS.md` copy: delete lines 3 and 4 with `sed -i '3,4d'` and check that `diff` prints `3,4d2` and only the stored provenance cells `label` and `promoted false` remain; `find ... | xargs sha256sum` hashes figures too). R3: new proposal section 9 with the three options, the recommendation (a, as a follow-up unit; fallback c), the kept provenance row and the appendix C sentence that `promote` leaves unchanged (not in the allowed-edit table).
  - R4 fixed: tests at command level for the missing header, a residual label and an unmatched rule (exit 2, nothing written). R5 fixed: `--out` opened with mode `x`; a dangling symlink is refused and its target not created (test).
  - Result: `82 passed in 8.17s` (79 before plus 3 new test functions; the existing tests are unchanged); real document again: exit 0, same summary (553 to 550 lines, R-TITLE 1, R-RULE 1, R-WORD 4, R-RUN 2, 1 residual kept).

- 2026-10-22 4.9 checklist: (1) change set `tools/findings_build.py`, `tests/unit/test_tools_findings_build.py`, this file, `docs/agent/notes/2026-10-22-promotion-proposal.md`. (2) Radius `tests/unit/test_tools_findings_build.py` (rule: tool to its test file), once. (3) Already run on this code: no. (4) CPU. (5) The ledger and the sealed files were not touched; the real document was promoted into a scratch directory only.
- Tests (written before the code): 12 new (hand-written reference and expected copy; seven kinds of extra change each fail the check; unknown residual label refused; missing header refused; the command leaves the input bytes unchanged and refuses an existing or identical `--out`; the summary lines). Result: `79 passed in 7.94s` (67 existing plus 12 new); no test failed on the first run.
- Real document at this commit, `promote` into a scratch directory: exit 0; preliminary 553 lines, promoted 550; header lines deleted 3; R-TITLE 1, R-RULE 1, R-WORD 4, R-RUN 2 lines; one residual label kept (the provenance label row); `diff` shows 15 changed lines, all of them the rules above (checked by eye once). The preliminary document, trace and sources are unchanged (`git status`). Acceptance criteria 1 to 6 met.
- `black` is not installed in the project venv; the code was written in the file's style (not run through black).
- `ledger.py append --files` question (answered on a temporary copy of the tool and of the ledger): see the proposal note section 7; it accepts any existing file and records name and sha256; no entry is written for a missing file; the real ledger was not run.

## Review

- **Reviewer:** `reviewer`, claude-opus-5-5, fresh context, 2026-10-22, commits 032e543 and abdf0b5 against develop 8eb3995.
- **Checks run.**
  - Radius: `tools/run_tests.sh unit tests/unit/test_tools_findings_build.py`, run once with `.venv/bin` on PATH: `79 passed in 8.76s`.
  - Real document: `python3 -I tools/findings_build.py promote` into the session scratch directory. It exited 0 with the same summary as the Log (553 to 550 lines; R-TITLE 1, R-RULE 1, R-WORD 4, R-RUN 2; 1 residual).
  - Hand `diff`: header lines 1 to 3 deleted, and 6 changed lines (6, 98, 108, 111, 121, 126), all of them exactly the rules.
  - The input's sha256 was the same before and after. `git status` of the worktree is clean.
  - `ledger.py append --files` was tested on a scratch copy of the tool and of the first 3 ledger lines. The real ledger was not touched.
- **Label list (item 1): complete for this document.**
  - I searched the document for `prelim|unpromot|promot|internal to|provisional|draft|development|appendix|PROPOSED|status`. Besides the five rules, the only hits are file names (`prelim-findings-conf1.*`, `promotion-figure-map.md`), the PROVISIONAL gate wording (not a status label), the `## A. Development context [DEVELOPMENT]` appendix label (it must stay, owner ruling D4), and the kept provenance row.
  - The template (`preliminary.template.md` lines 2, 6, 30), `format_value` (`"supported (preliminary, unpromoted)"`) and the constant `wording.supported` (`in this preliminary, unpromoted run`) are the only sources of labels, and each is covered.
  - Keeping `| Label | CONFIRMATORY: UNPROMOTED |` is consistent with ROADMAP WU-0018.3 ("header label removed from the promoted copy only") and with the proposal's treatment of the `RESULTS.md` provenance cells. The exemption is an exact line match, so it is tight. The owner should still know that the promoted report's §2 table will read "Label: CONFIRMATORY: UNPROMOTED" (see R3).
- **Findings and resolution:**
  - **R1 (major). The command's byte-for-byte check verifies the substitution with itself, and the planned independent check was not implemented.** `tools/findings_build.py:2601`, `:2630` to `:2632`.
    - `promote()` builds `promoted` from `promote_lines(pre)`. It then calls `verify_label_diff(pre, promoted)`, which recomputes `expected = promote_text(pre)`, that is, `promote_lines(pre)` again, and compares the two. The comparison is deterministic and always equal, so the `return 1` branch cannot be reached. The printed claim "verified: ... byte for byte" (`:2645`) therefore carries no evidence.
    - The plan (Machine check) specified something different. The check was to align the preliminary and promoted lines with `difflib` and accept only: the header deletion as the first hunk; `replace` hunks of equal line count; everything else equal.
    - The tests do pin the output to an independent hand-written reference (acceptance criterion 1). They also show that `verify_label_diff` rejects a tampered text (criterion 2). They do not cover the command's own check.
    - Why it matters: promotion is the owner's irreversible act, and the tool's stated purpose is a machine check that nothing but the labels differs.
    - Fix:
      - Implement the planned check without calling `promote_lines`/`promote_text`. Use `difflib.SequenceMatcher` opcodes on the line lists: exactly one `delete` of lines 0 to 2, then only `equal` and equal-length `replace` hunks.
      - For each replaced pair, require that the character-level difference consists only of (old, new) fragments from a separately written allowed-edit table. For example `("Preliminary f", "F")`, `(" (preliminary, unpromoted)", "")` and `("preliminary, unpromoted ", "")`, plus the R-RULE sentence.
      - Run it on the bytes read back from `--out` after writing (delete the file and exit 1 on any problem), or write to a temporary name and rename only after it passes.
      - Add one test in which the substitution is monkeypatched to make one extra change, and show that the command then exits non-zero with no file left at `--out`.
  - **R2 (major). In section 8 of the proposal, the label-bearing copy stays the executable line.** `docs/agent/notes/2026-10-22-promotion-proposal.md:126` to `:130`.
    - `cp docs/agent/notes/2026-10-20-prelim-findings-conf1.md promoted/CONF-1/report.md` is still an active command, and the `promote` command at `:128` is a comment.
    - Run as written, `report.md` is the copy that still carries the labels, and its hash goes into the append-only manifest line (`:130`). Running the commented `promote` afterwards is refused, because `--out` exists.
    - The `RESULTS.md` label removal "by hand" (`:129`) names neither the exact line(s) nor how the hand edit is checked.
    - Fix:
      - Delete the `cp` line of the report and make `promote` an uncommented command.
      - Add "WU-0033 merged to develop" to the step-0 preconditions.
      - For `RESULTS.md`, name the line(s) to delete (line 3, `**CONFIRMATORY: UNPROMOTED**`, and decide on the following blank line), then check with `diff` that these are the only differences.
  - **R3 (major, owner decision to be surfaced). The findings figures and the trace pointer in the promoted copy.**
    - What the promoted report would show:
      - The document embeds `2026-10-20-prelim-findings-conf1.figures/F1_primary.png`, `F2_secondary.png` and `F3_crosscheck.png` (document lines 158, 332, 480). Section 8 copies only `runs/confirmatory/run-1/full/figures` (the four `RESULTS.md` figures) into `promoted/CONF-1/`.
      - So `promoted/CONF-1/report.md` would have three broken image links.
      - If the `.figures/` folder is copied too, each of F1 to F3 carries the drawn suptitle "CONFIRMATORY: UNPROMOTED / PRELIMINARY: internal to the owner and the student until promotion (QA.11, LPC.PC.13)." I inspected F1, and `status_title` is used in `draw_panels` and in the F3 builder. A promoted report would then show three images that declare it internal and unpromoted.
      - The `RESULTS.md` figures carry no status text: I checked `regret_vs_regimes.png`, and `lpcstudy/` draws no label into titles. They can be copied as they are.
      - Line 550 of the copy also says that the trace file sits in "this directory" and that `check` verifies the document. Neither holds for the promoted copy, which `check` refuses (as the plan states).
    - Fix (developer):
      - State these facts in proposal section 6 item 4 and in section 8, with the options for the owner:
        - (a) re-render F1 to F3 with a promoted status title through a separate reviewed builder change: new PNG hashes, numbers unchanged;
        - (b) copy them as they are, with a dated note that the figure titles show the status before promotion;
        - (c) leave them out of the promoted set.
      - Add the matching `cp` of the `.figures/` folder (and of the trace, if wanted) to section 8.
      - Tell the owner that the promoted report keeps the provenance row `Label | CONFIRMATORY: UNPROMOTED`.
    - Plan scope note: the plan placed the figures out of scope, which is legitimate for the tool. But the proposal, which this commit edits, must not imply that the promoted set is label-free.
  - **R4 (minor). Plan deviations and untested safeguards.**
    - The plan says failures exit 1. Header, unmatched-rule and residual failures, and the `--out` refusals, exit 2 through the `ToolError` handler (`:2704`). The test asserts 2.
    - The "rule matched nowhere" refusal has no test.
    - The header and residual refusals are tested only on `promote_text`, not on the command with "nothing written".
    - Fix: either record the exit-code deviation in the Log, or align the code with the plan. Add the unmatched-rule test and one command-level failure test that asserts no file exists at `--out`.
  - **R5 (minor). The existence check and the write are separate steps.** `:2624`, `:2636`.
    - `dst.exists()` is False for a dangling symlink, and `write_text` then follows the link and writes to its target. That contradicts "never writes anywhere else". The two steps also leave a check-then-write race.
    - Fix: open the output with mode `"x"` (O_CREAT|O_EXCL, which does not follow a final symlink).
  - **R6 (minor, pre-existing line in the section this commit edits). `sha256sum promoted/CONF-1/*` does not hash the files inside `figures/`.** Proposal `:130`.
    - It prints "Is a directory", so the figure hashes are missing from the manifest line.
    - Fix: `find promoted/CONF-1 -type f | sort | xargs sha256sum`.
- **Items checked with no finding.**
  - The refusal of `--out` when it equals the input or already exists; that the input bytes stay unchanged; that the trace, sources and figures are not touched.
  - The 12 tests: an independent hand-written reference, byte-exact tolerance justified, and seven kinds of extra change (digit, verdict word, insert, other text, deleted line, restored title label, restored banner). Each of the seven fails `verify_label_diff`. No test compares the code with itself.
  - No criterion was loosened: the plan is unchanged between 032e543 and abdf0b5.
  - Commit trailers are present.
  - Proposal section 7 on `--files`. I checked it against `tools/ledger.py` lines 142 to 196 and on a scratch copy, and every claim is accurate:
    - any existing file is accepted, and an absolute path is stored as typed;
    - a missing file exits with "governed file not found" and no entry;
    - `verify` checks only the chain;
    - `status` lists proposal files as "NOT ADOPTED";
    - files of a `promotion` entry are not listed.
  - Owner checkpoint: the change does not touch verdict, statistics, seed or provenance code in `lpcstudy/`, nor dependencies. The owner reviews the tool's output at WU-0018.3.
- **Verdict: changes required** (R1 to R3 major; R4 to R6 minor; 6 findings).
- **Re-review, fix round 1** (`reviewer`, claude-opus-5-5, 2026-10-22, diff 1b5e41a..eeb7123; covers R1 to R6 only).
  - **Checks run.**
    - Radius: `tools/run_tests.sh unit tests/unit/test_tools_findings_build.py`, run once: `82 passed in 8.31s`.
    - Real document: `promote` into the session scratch directory. It exited 0 with the same summary as before.
    - The output is byte-identical (`cmp`) to the round-0 output. The input's sha256 was the same before and after, and the worktree is clean.
  - **R1 fixed.**
    - `verify_label_diff` (`tools/findings_build.py:2605` ff.) no longer calls `promote_lines`/`promote_text`. It aligns the lines with `difflib.SequenceMatcher` (`autojunk=False`) after it has checked and removed the header. It accepts only `equal` hunks and equal-length `replace` hunks whose new lines equal the old lines under the separate `ALLOWED_EDITS` table, then scans for residual labels.
    - `promote()` writes with mode `"x"`, checks the text read back from `--out`, and on a problem unlinks the file and exits 1.
    - The new monkeypatch test shows the command's own check catching an extra digit: exit 1, no file left.
    - Note, not a finding: the read-back goes through `read_text` (decoded, universal newlines), not raw bytes. A carriage return in the source would be normalized on both sides and not reported. The real document contains none (`grep -c $'\r'` gives 0), so this is immaterial here.
  - **R2 fixed.**
    - Proposal §8: `promote` is now the live command, and its precondition (WU-0033 merged) is stated.
    - `sed -i '3,4d'` is correct for the official `RESULTS.md`, whose line 3 is `**CONFIRMATORY: UNPROMOTED**` and line 4 is blank. I checked on a scratch copy:
      - `diff` prints exactly `3,4d2` and the two deleted lines;
      - the `grep` then shows only the stored cells `| label | CONFIRMATORY: UNPROMOTED |` and `| promoted | false |`.
  - **R3 fixed.**
    - The facts in §9 are accurate:
      - F1 to F3 are embedded at lines 158, 332 and 480;
      - `status_title` is the suptitle of every findings figure (`:1501`, `:1550`);
      - the `RESULTS.md` figures carry no status text;
      - the links break under the step-3 copies;
      - the provenance row and the stored cells are kept;
      - the sentence is in Appendix C (heading at line 548, sentence at line 550, line 547 of the copy).
    - The options and the recommendation, (a) with (c) as fallback, are stated fairly as the owner's decision.
    - One constraint the follow-up unit must honour: `check` re-renders the figures and compares their bytes (`:2514`). So option (a) has to add a promoted title as a separate path; it cannot change the default `status_title`, or the preliminary document stops passing `check`. §9 states the requirement ("the preliminary document must still pass `check`").
  - **R4 fixed.**
    - The exit-code change is recorded in the Log as a dated note. I judge it acceptable, not a post-hoc loosening, for three reasons:
      - the exit code appears in the Safeguards text, not in acceptance criteria 1 to 6;
      - every refusal still exits non-zero with nothing written;
      - the new split (1 = the check failed, 2 = input or usage error) gives more information.
    - Command-level tests now cover the missing header, a residual label and an unmatched rule, each asserting that no file is written. Each of the three cases reaches only its intended refusal.
  - **R5 fixed.** `dst.is_symlink()` refuses a dangling link before the open, and `open("x")` uses O_EXCL. The test confirms that the link's target is not created.
  - **R6 fixed.** `find promoted/CONF-1 -type f | sort | xargs sha256sum` hashes the files inside `figures/`.
  - **Re-review verdict: approve** (R1 to R6 fixed; no new findings).

## Audit

- Is the definition of done met?
- Defects recorded:
- Notes for successors:
