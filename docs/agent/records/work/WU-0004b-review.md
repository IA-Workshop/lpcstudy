# WU-0004b: independent review (round 1)

Reviewer: `reviewer`, claude-opus-5-5, 2026-10-18, fresh context. Companion to `WU-0004b-budget-text.md`.

**Scope.** `git diff 7b6f6e6..614d889` (plan 64e59d6, code 614d889): `lpcstudy/budget.py`, `tests/unit/test_budget.py`,
the unit file and `queue.md`. Sources read: amendments note §33 (OF-4) and §35 (B7); owner-decision drafts §3 (addendum A3);
math note `2026-10-14-math-wu0003.md` M5.1 and M5.2; `docs/study/lm_doubling_dev0_report_v3.md`; WU-0005.6 record line 359;
`lpcstudy/config.py` presets.

**Tests.** I ran none (read-only review, per the dispatch). The developer's record stands: radius of 9 unit files
`1 failed, 446 passed`, the failure an own-test defect (case of "Development evidence"), `--lf` `1 passed, 35 deselected`.
The fix changed one assertion of the new test only and no code, so not rerunning the other 446 is consistent with
DEVELOPMENT_WORKFLOW.md §4.4 (precedent: WU-0003.7c review). The first attempt without pytest ran no test.

**Offline check (no test, no preset).** I imported `budget.budget_lines` at 7b6f6e6 and at 614d889 over
`runs/baseline/smoke/results.json` (CPU, niced) and diffed the line lists: 127 lines old, 137 new; exactly one changed
line (the H2a(i) oracle cell, F1 = 0.0368 in both, only the wording around it differs) and five added note blocks (blank
line plus `LM_DEVELOPMENT_NOTE`), one per table. No number changes.

## Checks that hold

1. **OF-4 wording matches A3 and is true per M5.** The cell now reads "indicative F1 = <v> (bias of a zero-range state,
   independent draw noise across <k> horizons; not a bound on the median; V4 at H_ref only)", which is A3's line-315
   wording with k filled in. "Bias of a zero-range state" and "not a bound on the median" are M5.2's corrections; the
   direction "upward (toward fail)" is kept, as M5.2 says it stands. The docstring's mechanism (more than half of the
   eligible states exactly separated, median near an upper quantile of the noise-only range, above its mean) and 1.38 F1
   (60% separated, c = 0, M = 200) match M5.2's table. The figures quoted for A3 match M5.1: F1/hw_full at M = 200 is
   0.54 to 1.20 (P1 Lorenz 0.54, P0 Lorenz 1.20); M for F1 < 0.1 hw_full is 5,700 to 28,900 (A3 rounds to 29,000). These
   two ranges are not printed by the code, only by the A3 draft text. The F1 value and `oracle_range_bound` body are unchanged.
2. **B7 facts that are correct.** 18 parts; classes N 5 / X 6 / U 7 (report §3); the flag "yes" iff N, 5 of 18 (report §0,
   §3). The projection factors equal the WU-0005.6 record line 359. The sizes match the presets: PILOT n_test 500,
   n_test_sweep 300; FULL 1000 and 1000 (`config.py` 132-133, 200); sqrt(2) = 1.414, sqrt(10/3) = 1.826. The note opens
   "Development evidence ..., not a sealed result" and ends "The iterative row of this report stays not estimated."
   It does not claim that the iterative error is small. The direction of the 5 is printed unambiguously ("below 10% ...
   for 5 of 18"). For the 13, see R1.
3. **Tests.** The one edited assertion (`test_f1_uses_the_number_of_long_horizons_of_the_configuration`) is replaced by a
   strict superset of the old substring's information (same independent reference k/sqrt(pi)·0.01/z, same 3-digit match,
   plus the absence of "worst case" and "≤ F1"). Nothing is loosened (PRIME.2). `test_f1_matches_the_independent_formula`
   and the existing LM, label and `ITERATIVE_SENTENCE` assertions are untouched. The new test's factors come from
   arithmetic, not from the code (the code quotes strings).
4. **Radius and stale pins.** `grep` of tests/, tools/, lpcstudy/ for "worst case", "worst-case", "≤ F1" and
   "independent draw noise" finds only unrelated docstrings (test_states_dump, test_rehearsal_report_mc, test_statistics,
   test_validation, test_oracle) and the new assertions. No golden fixture holds budget text (the golden_rehearsal
   `budget` hits are rehearsal_diagnostics' D5 reading, which does not import `budget`). The only importers of
   `lpcstudy.budget` are `report.py` and `tools/lm_doubling.py`, both covered by the 9 files. The integration readers of
   RESULTS.md (`test_smoke_pipeline.assert_lm_rows` regex `^\| \w+ \| ...`, `test_clip_failure` substrings) cannot
   match the new note. The radius is adequate for the unit tier.
5. **Silent handling and reproducibility.** No clip, fallback, exception handling, randomness or dtype change was added.
6. **Governance.** Both commits name the unit and carry `Co-Authored-By` and `Agent: claude-sonnet-5-5`. The history is
   linear (614d889 → 64e59d6 → 7b6f6e6). `queue.md` is append-only (one added line). The unit file changes only its Status
   field and appended sections. No seed, provenance or dependency file was touched, and no confirmatory seed was used.

## Findings

**R1 (medium; correctness of a printed claim): "not below it for 13" states a finding the study does not make.**
`lpcstudy/budget.py:408-410` prints "finds the iterative change below 10% of the sampling half-width for 5 of 18 parts
... and not below it for 13 (classes N 5, X 6, U 7)". The report defines U as "not certified" (§2) and summarises the 13 as
"not shown negligible (class X or U)" (§7). Several U parts are measured well under 10%, for example rossler H2b(i)
(d1 = d2 = 0, U only because r_A = 0.571), rossler H3c (S = 1.1e-4), rossler H2a(i) (S = 0.026) and lorenz63 H2a(ii)
interior (S = 0.061). "Finds ... not below it" asserts a size the study did not find for 7 of the 13 parts, in text that a
sealed RESULTS.md will carry. **Fix:** word it as the report does, for example "... below 10% of the sampling half-width
for 5 of 18 parts (class N, size under H-geo) and does not show it below for the other 13 (X, not negligible, 6; U, not
certified, 7)". Then pin the exact sentence in the test (see R5).

**R2 (medium-low; correctness on non-full presets): "from the pilot to this run" is false unless this run is the full preset.**
`lpcstudy/budget.py:411-412` with `LM_PROJECTION` (`budget.py:415-419`) prints "grows from the pilot to this run by about
√(n_full/n_pilot), ×1.41 ... (500 → 1000 test states)" in every RESULTS.md. In my offline smoke render (n_test = 80) it
prints exactly this, and on a pilot run (n_test = 500) "this run" is the pilot itself. The sealed run is the full preset
(amendments §33, sample size kept), so the sealed text is true, but DEV smoke and pilot RESULTS.md now carry a false
statement. Nothing ties the quoted sizes to `config.PILOT` or `config.FULL`, so a preset change would go stale silently.
**Fix:** say "from the pilot preset to the full preset" instead of "this run" (keeping the quoted-not-computed design),
or print the note's projection clause only when `config.n_test` and `config.n_test_sweep` equal FULL's. In the test,
assert that the quoted sizes equal `PILOT.n_test`, `FULL.n_test`, `PILOT.n_test_sweep` and `FULL.n_test_sweep`, as an
independent cross-check of the quoted text.

**R3 (low; correctness against the source): what would remove the projection.**
`lpcstudy/budget.py:413-414`: "only a 30-iteration run at the full size would remove it". The projected quantity is
S = d1 + 2 d2, which needs the 60-iteration arm as well. The report (§5) and the WU-0005.6 record (line 372) both say
"a full-run 30/60 twin". **Fix:** "a 30- and 60-iteration twin of the full-size run (O4) would remove it". Also drop
"only", or keep it if the owner confirms that it holds.

**R4 (low; readability of scope): a study-wide count is printed under each QoI table.**
The same "5 of 18 parts" sentence is printed under H2a(i), where 0 of 3 parts are N, and under H2b(ii), where 2 of 3 are N.
The phrase "(system and QoI part)" does not say that the 18 span all five QoIs. A reader of one table can take 5 of 18 as
that QoI's share. **Fix:** say "5 of the 18 parts of the five QoIs and three systems". Optionally add the QoI's own count
(from report §3: H2a(i) 0 of 3, H2a(ii) 3 of 6, H2b(i) 0 of 3, H2b(ii) 2 of 3, H3c 0 of 3), quoted, not computed.

**R5 (low; evidence): the new test does not pin the direction of the counts.**
`tests/unit/test_budget.py:794` asserts only that "5 of 18" and "classes N 5, X 6, U 7" are substrings. A reversed
or garbled sentence (for example "not below it for 5 of 18") would pass. This is the hazard noted at dispatch, where the
LM-row flag is described loosely as "flags 5 of 18". The docstring has the same ambiguity ("5 of 18 parts with the LM-row
flag"). **Fix:** assert the exact count sentence after R1, and say in the docstring "flag yes (below 10%) for 5 of 18".

**R6 (low; traceability, owner dependency): the docstring cites an addendum that is not yet in the ledger.**
`lpcstudy/budget.py:589` cites "DEC-0024 addendum A3", but `docs/agent/records/decisions.md` has only A1 and A2. A3 is a
draft (owner-decision drafts §3.2), and the ledger entry is the owner's. **Fix:** none needed in code if the owner enters
A3 under that label before the freeze. Otherwise, cite the draft path. Record it as a freeze-checklist dependency.

## Owner checkpoint

**Needs owner review before freeze.** This change sets text that every RESULTS.md prints, including the sealed report:
the H2a(i) F1 cell (OF-4/A3) and the B7 development-evidence note. The change touches no verdict, statistics, seed,
provenance or dependency code, and no number. The owner's review should read the final note text after R1 to R4, and
confirm that the A3 ledger entry exists (R6).

## Verdict

**approve with fixes.** 6 findings: R1 and R2 must be fixed (printed claims that are false in part or in context), and
R3 to R5 should be fixed in the same round. R6 is an owner dependency. After the fixes, run the radius once
(`test_budget.py` at least; the same 9 files is simplest), and include the main session's C16 DEV-0 smoke neutrality check.

## Round 2 (re-review of fix round 1)

Reviewer: `reviewer`, claude-opus-5-5, 2026-10-18, fresh context. Scope: R1 to R6 only, `git diff 9d7dd53..182ef6f`
(`lpcstudy/budget.py`, `tests/unit/test_budget.py`, the unit file, `queue.md`). Source checked:
`docs/study/lm_doubling_dev0_report_v3.md` on this branch (§2 class definitions, §3 table, §5 line 134, §7 line 149).

**Tests.** I ran none, per the dispatch. The developer ran the same 9-file unit radius once: `447 passed` (446 + 1 as in
round 1, so the same tests). The change to the code is text only, so the radius is unchanged.

**Offline render (no test, no preset).** I extracted `lpcstudy/` at 7b6f6e6 and 182ef6f with `git archive` into the
scratchpad and imported `budget.budget_lines` over `runs/baseline/smoke/results.json` with `config.SMOKE` (CPU, niced).
Old: 127 lines; new: 137. With the five note blocks removed, exactly one line differs: the H2a(i) oracle row (OF-4 wording
of round 1). Its only number, F1 = 0.0368, is the same in both. Every other line, and so every number, is byte-identical.

| Finding | Status | Check |
| --- | --- | --- |
| R1 | **resolved** | The note now reads "... below 10% of the sampling half-width (class N) for 5 of the 18 parts ... and does not show it below 10% for the other 13 (X, not negligible, 6; U, not certified, 7)". This matches report §2 (X "not negligible", U "not certified"), §3 (flag yes for 5, no for 13; N 5 / X 6 / U 7) and §7 ("not shown negligible (class X or U) for 13 of 18"). It no longer claims the U parts are above 10%. |
| R2 | **resolved** | The note says "from the pilot preset to the full preset ... (<a> → <b> test/sweep states in the two presets)", which is true on any preset. The test takes sizes and factors from `config.PILOT` and `config.FULL` (n_test 500/1000, n_test_sweep 300/1000; `config.py` 132-133, 196-200). It asserts the exact projection sentence, and it keeps the literal `["1.41", "1.41", "1.83", "1.83", "1.41"]` pin, the WU-0005.6 reference, so a preset change would fail the test. |
| R3 | **resolved** | "a 30/60-iteration twin of the full-size run would remove it", as in report §5 ("a full-run 30/60 twin would remove the projection"). "only" dropped. |
| R4 | **resolved** | "5 of the 18 parts of the five QoIs and three systems (this QoI: class N in k of m parts)". I recounted from the §3 table: H2a(i) X, X, U → 0 of 3; H2a(ii) chua U, U, lorenz63 U, N, rossler N, N → 3 of 6; H2b(i) X, X, U → 0 of 3; H2b(ii) chua N, lorenz63 X, rossler N → 2 of 3; H3c U, X, U → 0 of 3. Sum 5, total 18. The rendered notes carry these counts under the right tables, in the order H2a(i), H2a(ii), H2b(i), H2b(ii), H3c. |
| R5 | **resolved** | The test asserts the exact count sentence with its direction (flag yes = class N for 5; "does not show it below 10%" for 13) and that "not below it" is absent. The docstring states the flag direction and that the 13 must not be described as found above 10%. |
| R6 | **resolved (safe option)** | The `oracle_range_bound` docstring cites the draft addendum A3, `docs/agent/notes/2026-10-18-owner-decision-drafts.md` §3.2 (present, heading at line 94), and says it is not yet in the ledger (`decisions.md` has DEC-0024 A1 and A2 only). The owner's A3 ledger entry stays a freeze-checklist dependency. |

**No assertion loosened (PRIME.2).** Only `test_lm_development_note_under_every_table` changed, which is the developer's own
new test from round 1. Each old check has a stricter successor:
- `index(ITERATIVE) < index(note)` is implied by the kept `== index + 2`;
- `startswith("Development evidence")` and "not a sealed result" became the exact opening clause;
- the "5 of 18" and class-count substrings became the exact sentence;
- the `×factor` substring became the exact projection sentence;
- "stays not estimated" became `endswith` the full sentence.

The absence check for the other factor and the H3c "not estimated" cell assertions are kept. No other test, tolerance or
criterion was touched. The diff adds no clip, fallback, exception handling, randomness or dtype change.

**Governance.** 182ef6f names the unit and carries `Co-Authored-By` and `Agent: claude-sonnet-5-5`. Its parent is 9d7dd53,
so the history is linear. `queue.md` gains one appended line. The unit file changes only its Status field and appends a
section. Observation, not a finding: the unit-file Log says "commit given below once made", but no hash follows. This
review records it as 182ef6f.

**New findings (round 2):** none.

**Owner checkpoint (unchanged).** Needs owner review before freeze. The owner should read the final note text, rendered
above, and enter the A3 ledger entry (R6). C16, the DEV-0 smoke neutrality check, is still the main session's.

**Verdict (round 2): approve.** All 6 round-1 findings are resolved, with 0 new findings.
