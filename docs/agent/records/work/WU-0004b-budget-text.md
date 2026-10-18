# WU-0004b: report-text changes in `lpcstudy/budget.py` (OF-4 and B7)

| Field | Value |
| --- | --- |
| Status | in progress |
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

## Review

- **Reviewer:** (independent-review, fresh context)
- **Findings and resolution:**

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:

## Referral

None.
