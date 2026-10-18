# WU-0004b: report-text changes in `lpcstudy/budget.py` (OF-4 and B7)

| Field | Value |
| --- | --- |
| Status | implemented; pending independent review |
| Class | CSQ3 development |
| Agent(s) | claude-sonnet-5-5 (developer) under the owner rulings of amendments note §33 (OF-4) and §35 (B7) |
| Estimate | small (text only; one source file, one test file) |

## Plan (written before execution)

Sources: `docs/agent/notes/2026-10-11-amendments-for-owner.md` §33 (OF-4), §35 (B7);
`docs/agent/notes/2026-10-18-owner-decision-drafts.md` §3.1 to §3.3 (draft addendum A3);
`docs/agent/notes/2026-10-18-freeze-blockers.md` B7, C3, C4; `docs/study/lm_doubling_dev0_report_v3.md`
(sections 3 and 5); `docs/agent/records/work/WU-0005.6-lm-doubling.md` line 359 (the projection factors).
Branch `wu/0004b-budget-text` from develop 7b6f6e6.

- **Scope in:**
  1. **OF-4.** `lpcstudy/budget.py`: the docstring of `oracle_range_bound` (the two "worst case" phrases)
     and the H2a(i) cell string in `_oracle_cell` change from "indicative worst case ≤ F1 = <v>
     (independent draw noise across k horizons; V4 at H_ref only)" to the wording of addendum A3 (cell
     line 315): "indicative F1 = <v> (bias of a zero-range state, independent draw noise across k
     horizons; not a bound on the median; V4 at H_ref only)". The value `<v>` and the function
     `oracle_range_bound` are untouched. The "F1 not computable: ..." branches are untouched.
  2. **B7.** One new constant `LM_DEVELOPMENT_NOTE`, printed once under each of the five budget tables,
     directly after `ITERATIVE_SENTENCE`. It points to `docs/study/lm_doubling_dev0_report_v3.md`, says
     that the DEV-0 flags are development evidence and not a sealed result, quotes the flag count
     (5 of 18 parts; classes N 5 / X 6 / U 7) and the projection factor sqrt(n_full/n_pilot) (1.41 for
     H2a(i), H2a(ii), H3c; 1.83 for H2b(i), H2b(ii)), and says that the row of this report stays
     "not estimated". The factors are quoted from the WU-0005.6 record, not computed.
  3. Tests: `tests/unit/test_budget.py` updated where it pins superseded wording, and new assertions
     for the new wording (below).
- **Scope out:** any number of `results.json`; `ITERATIVE_SENTENCE`, `iterative_label`, `LM_PRESENT`,
  `LM_ABSENT` and the "unverified" label of each primary (all kept as written and still exactly pinned
  by existing tests, so no existing assertion changes for B7); `report.py`; docs under `docs/study/`;
  the decisions ledger (the owner's entry); the DEV-0 smoke neutrality check (main session, C16).
- **Definition of done:**
  - The string "worst case" and "≤ F1" no longer occur in `lpcstudy/budget.py` (docstrings, comments and
    printed text), except in the cell's "not computable" wording where they never occurred.
  - The H2a(i) cell prints "indicative F1 = <v> (bias of a zero-range state, independent draw noise
    across <k> horizons; not a bound on the median; V4 at H_ref only)" for k = 2 and 3.
  - Each of the five budget tables carries the pointer note, with the projection factor of its QoI.
  - No numeric output changes: the value `<v>`, every other cell and the whole `results.json` are
    unchanged (the latter is checked by the main session, DEV-0 smoke, plan A2.6).
- **Acceptance criteria (fixed now, VV.3):**
  - A1. `tests/unit/test_budget.py::test_f1_uses_the_number_of_long_horizons_of_the_configuration`:
    the exact new cell tail for k = 3 and k = 2, with `<v>` computed independently as
    `k / sqrt(pi) * 0.01 / scipy.stats.norm.ppf(0.975)` at 3 significant digits (the test's existing
    reference; unchanged), and the strings "worst case" and "≤ F1" absent. The tolerance is the
    existing exact 3-digit text match; nothing is loosened.
  - A2. `test_f1_matches_the_independent_formula` (line ~586, `F1 = {f1:.3g}` substring): passes
    unchanged. The F1 formula test is not edited.
  - A3. New test `test_lm_development_note_under_every_table`: for the five tables, the note appears
    exactly once under each, after `ITERATIVE_SENTENCE`; it names `docs/study/lm_doubling_dev0_report_v3.md`;
    it says "development evidence" and "not a sealed result"; its factor is 1.41 under H2a(i), H2a(ii)
    and H3c and 1.83 under H2b(i) and H2b(ii), derived in the test from sqrt(1000/500) and
    sqrt(1000/300) (an independent arithmetic reference, to the printed 3 significant digits); and the LM row
    cell still starts with "not estimated" (existing test, unchanged). Exact text.
  - A4. Every existing assertion on `LM_PRESENT`, `LM_ABSENT`, the label ending
    "(DEC-0024)" and `text.count(budget.ITERATIVE_SENTENCE) == 5` passes unchanged.
  - A5. The only assertion edited is the one that pins the superseded F1 wording (the substring
    "F1 = <v> (independent draw noise across 3 horizons", two occurrences in A1's test): it is
    replaced by the new wording, not relaxed; the replacement is longer and stricter.
- **Affected checks (hand-derived radius, DEVELOPMENT_WORKFLOW.md §4.2; the file changed is
  `lpcstudy/budget.py`, a leaf-ish module):** the importers of `lpcstudy.budget` are `lpcstudy/report.py`
  (hence `tests/unit/test_report.py`, `tests/unit/test___main__.py` through `report`/`__main__`) and
  `tools/lm_doubling.py` (hence `tests/unit/test_tools_lm_doubling.py`, which also runs offline over
  `budget._parts_of` only). The direct test is `tests/unit/test_budget.py`. The integration smoke
  `tests/integration/test_smoke_pipeline.py` was read: it checks the LM-diagnostics rows and clip rows
  of RESULTS.md by regular expression and does not pin any budget text, so it is not in the radius
  (and the integration tier is not run in this unit). The set is cross-checked with
  `tools/test_impact.py` (selection only, no `--run`) before the run, and the difference, if any, is
  logged.
- **Compatibility note.** The existing test asserts the substring `F1 = <v> (independent draw noise
  across 3 horizons`; addendum A3's cell wording puts "bias of a zero-range state," between the value
  and "independent draw noise", so that substring is superseded by the owner's ruling and is updated
  (A5), not loosened.

## Log

(entries below)

### 2026-10-18, claude-sonnet-5-5 (developer): plan committed 64e59d6; tests first, then code

- Tests written before the code: `tests/unit/test_budget.py`: (a) the two F1 substring assertions in
  `test_f1_uses_the_number_of_long_horizons_of_the_configuration` replaced by the A3 wording (the
  superseded substring `F1 = <v> (independent draw noise across k horizons` no longer holds under the
  ruling; the new assertion is longer and also asserts "worst case" and "≤ F1" absent); (b) new
  `test_lm_development_note_under_every_table`. Then `lpcstudy/budget.py`: docstring of
  `oracle_range_bound`, the cell string in `_oracle_cell`, new `LM_DEVELOPMENT_NOTE` and
  `LM_PROJECTION`, one change in `_table` (the end of each table). No clip, replacement,
  fallback or randomness is added (grep of the diff below).
- No existing assertion was loosened: `LM_PRESENT`, `LM_ABSENT`, the label ending, the
  `ITERATIVE_SENTENCE` count and `test_oracle_cell_shows_f1_and_f2_with_three_digits` (substring
  `F1 = <v>`, still true since "indicative F1 = <v>" contains it) are untouched.

#### 4.9 checklist before the one invocation

1. Change set (`git diff --name-only develop...HEAD` plus `git status --porcelain`):
   `docs/agent/records/work/WU-0004b-budget-text.md` (committed), `lpcstudy/budget.py`,
   `tests/unit/test_budget.py` (modified, uncommitted).
2. Radius: `tools/test_impact.py --base develop --explain` gives, for `lpcstudy/budget.py`: own and direct
   dependents (`test_budget`, `test_report`), direct import (`test_analysis`), source scan
   (`test_data`, `test_identifiers`, `test_rng_hygiene`, `test_tools_test_impact`). By hand (§4.2),
   the importers of `lpcstudy.budget` are also `tools/lm_doubling.py` (`test_tools_lm_doubling`) and
   `__main__` through `report` (`test___main__`; it names `iterative_label`), which the tool does not
   select; both are added. The set is the union, 9 unit files, far smaller than the whole suite (no gate).
   `tests/integration/test_smoke_pipeline.py` was read: it matches LM-diagnostics and clip rows of RESULTS.md by
   regular expression only, pins no budget text, and is not run (the integration tier is not run in this
   unit; the main session runs the DEV-0 smoke neutrality check, C16).
3. Already run on this code? No (first run).
4. Device: `JAX_PLATFORMS=cpu` (settings default); no GPU.
5. Threads and time: `LPC_THREADS=4` (settings default); unit tier, timeout 600 s.
6. Contention: no preset run (`pgrep -fa "lpcstudy --preset"` checked below); no lock needed.
7. Output: `-q --tb=short -rfE`; summary line and failures only.
8. Command: `tools/run_tests.sh unit <the nine files>`.

#### Run and result (one invocation, then `--lf` on the one failure)

- Command: `LPC_PYTHON=<main .venv python> tools/run_tests.sh unit tests/unit/test_analysis.py
  tests/unit/test_budget.py tests/unit/test_data.py tests/unit/test_identifiers.py tests/unit/test_report.py
  tests/unit/test_rng_hygiene.py tests/unit/test_tools_test_impact.py tests/unit/test___main__.py
  tests/unit/test_tools_lm_doubling.py` (the worktree has no `.venv`; the main checkout's interpreter is used;
  the first attempt without it stopped with "No module named pytest" before any test ran, so it is not a run).
- Result: `1 failed, 446 passed in 41.84s`. The one failure was a defect of my new test, not of the code:
  it looked for the lower-case "development evidence", while the printed note starts with the capitalised
  "Development evidence". Fixed in the test (it now asserts `note.startswith("Development evidence")`; no
  tolerance involved). `--lf` on that test only: `1 passed, 35 deselected in 0.81s`. No rerun of the radius
  (the fix touched one assertion of one test; the other 446 results stand on the unchanged code).
- Self-check of the diff against the plan: OF-4 wording in the docstring and the cell, B7 note under every
  table, nothing else. Grep of the diff for `clip|nan_to_num|isfinite|where(|try:|except` finds no site;
  `default_rng|random.|PRNGKey` none; `approx|rel=|abs=` none added; no tolerance changed.

#### Old and new wording

- Cell (H2a(i), row 1), old: `...; indicative worst case ≤ F1 = <v> (independent draw noise across <k> horizons; V4 at H_ref only)`.
  New: `...; indicative F1 = <v> (bias of a zero-range state, independent draw noise across <k> horizons; not a bound on the median; V4 at H_ref only)`.
- Docstring of `oracle_range_bound`, old: "indicative worst-case upward bias ... Independent draw noise across the
  horizons is the worst case." New: "the indicative bias of a zero-range state ... F1 is an indicative value,
  **not a bound** on the bias of the median range (DEC-0024 addendum A3 ...)".
- New B7 note, printed under each of the five tables after the iterative-error sentence (`LM_DEVELOPMENT_NOTE`).

#### Not done here (by scope)

- DEV-0 smoke neutrality check (0 changed `results.json` leaves, plan A2.6, C16): main session.
- Ledger entry for addendum A3 (the owner's), edits of the WU-0008 record lines 216, 310, 313-315, 868
  (draft §3.2 "replacement wording"; a dated correction to the WU-0008 Log is not part of this code unit).

## Review

- **Reviewer:** (independent-review, fresh context)
- **Findings and resolution:**

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:

## Referral

None.
