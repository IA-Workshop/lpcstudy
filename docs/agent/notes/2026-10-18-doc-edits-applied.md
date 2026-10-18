# DEF-0005 document edits: patched copies and patches for the owner

Prepared 2026-10-18 on branch `wu/def0005-doc-patches` (from `develop` bbccf56) by claude-sonnet-5-5. Source: `docs/agent/notes/2026-10-18-def0005-document-edits.md` (63 edits). The owner ordered the drafted edits applied (chat, 2026-10-18); an agent may not edit the governing documents (GOV.49), so this unit produces **patched copies** and **patches** and leaves the live documents untouched. Nothing under `ROADMAP.md`, `docs/study/`, `.claude/`, governance, the ledger, `decisions.md`, `defects.md`, `seeds/` or any code or test file was modified. No ledger entry, no sealed seed, no web access, no tests, no presets.

## 1. Result in one table

| Document | Draft items | Applied | Skipped | No change | Failed |
| --- | --- | --- | --- | --- | --- |
| Proposal and methods v3 | 25 | 23 (V21 partly: 6 of its 10 bullets) | 1 (V20), plus 4 U bullets of V21 | 1 (V8, U1 option A) | 0 |
| Methods v2 (and decision log) | 28 (1 body edit, 26 log rows, DL-1) | 28 | 0 | 0 | 0 |
| ROADMAP | 10 | 9 | 0 | 0 | 1 (P9, U1 option A) |
| **Total** | **63** | **60** | **1 (+4 bullets)** | **1** | **1** |

Every old text was required to match exactly once in the copy. All did, except P9's anchor (section 5). One old text needed context to be unique (V18, below), and one draft old text elided its middle with `...` (P2, below). The Methods v2 amendment log is append-only here: the copy adds the header paragraph and 26 rows after the M14 table and changes one line in the body (M2, the draft's M-body). Nothing else in the three documents changed (`diff` of copy against live file shows only the draft's lines).

## 2. Files

All under `docs/agent/notes/doc-edits-applied/`:

| File | What |
| --- | --- |
| `ROADMAP.md.new`, `proposal_and_methods_v3.md.new`, `methods_experimental_procedures_v2.md.new`, `decision_log_lpc.md.new` | Patched copies (the decision log is included because the draft edits it, DL-1). |
| `roadmap.patch`, `v3.patch`, `methods_v2.patch`, `decision_log.patch` | Unified patches from the live file to the copy, with paths `a/ROADMAP.md`, `a/docs/study/...` so that `git apply` from the repository root applies them. |

## 3. To apply (owner, one command)

From the repository root, on the branch that carries the documents (the study documents are identical on `main` and `develop`):

```
git apply docs/agent/notes/doc-edits-applied/*.patch
```

This edits `ROADMAP.md`, `docs/study/proposal_and_methods_v3.md`, `docs/study/methods_experimental_procedures_v2.md` and `docs/study/decision_log_lpc.md`. Then, as the draft's status paragraph says: commit; record one ledger `amendment` entry per changed document (v3, Methods v2, decision log, ROADMAP); re-adopt the changed governed files; re-export v3 and record its SHA-256 at the freeze (LPC.PC.8).

Dry run done here: `git apply --check docs/agent/notes/doc-edits-applied/*.patch` passes in this worktree and in the main checkout (`/home/brianm/projects/physics/chaos/lpcstudy`). Applying the patches to a scratch copy of the four live files reproduced the four `.new` copies byte for byte (`cmp`).

**The Claude Doc must receive the same edits.** The v3 export is generated from the Claude Doc, not from the repository file. Apply each v3 edit (the old and new text of every APPLIED v3 row are in the draft note, and in `v3.patch`) in the Claude Doc, then re-export. The draft's finding 5 still holds: the Claude Doc cannot be inspected from here, so if it differs from the export, use the old text as the search string.

## 4. SHA-256

| | SHA-256 of `proposal_and_methods_v3.md` |
| --- | --- |
| Old (live export) | `6fb99e8eeaac437ba1e561e01bd88f26fc86f836173460c7f2a0f8899fabad2b` |
| After the patch (patched copy `proposal_and_methods_v3.md.new`) | `2a856a4595bead58fa7de168f602ae4f250098839347aa352245b941459d0a06` |

The new value is the SHA-256 the v3 export will have **only if the Claude Doc, after the same edits, exports byte-identical text**. I wrote the new v3 text with the export's escape convention (`\_`, `\*`, `\[`, `\]`, as in `ε\_s`, `w\*`, `\[0.8, 1.2\]`), so the patched copy should match a faithful re-export, but only the export itself decides. The freeze must record the SHA-256 of the real final export, not this value.

## 5. Failed, skipped and conditional items

**FAILED**

- **P9 (ROADMAP, U1 option A).** The draft inserts the new row "after WU-0002.14 in the Phase B task table" and after it in the definition-of-done table. The live ROADMAP has **no WU-0002.14 row** (the last WU-0002 rows are WU-0002.13, lines 97 and 121; WU-0002.14 exists only as a unit file). The old text `| WU-0002.14 |` occurs 0 times, so nothing was guessed and P9 is not in `roadmap.patch`. This is the one U edit the order asked for, so it is **not yet opened**. Marked, as ordered: *opened under the owner's step-1 order on the main session's recommendation; the owner may rule it out.* Methods v2 log row 26 (applied) already refers to WU-0002.15, so that reference dangles until the row is placed. The text to paste, after the WU-0002.13 row of each table (closest anchor) or wherever the owner places WU-0002.14, is:

Task table:

```
| WU-0002.15 | Gain-bound screen (concordance D-21(b), (c); DEC-0016 O2): add to `analysis.gain_horizon_bound` the subset of states with raw C = E[e_C e_P] ≥ 0 at every horizon (P1(c), (d)), its fraction within ln 2/(2Λ̄) + 1 step, and the per-screen counts (growth ≤ 0, censored, raw C < 0 at some horizon); keep the v1 screen's numbers; no bar; remove `GAIN_BOUND_PENDING` | applied-mathematician (horizon range of the screen), developer | WU-0002.9 | CSQ3 | §M11 row H2e; v3 §2 (after RQ3); DEF-0005 | `test_analysis`, `test_identifiers`, `test_report`; smoke | S |
```

Definition-of-done table:

```
| WU-0002.15 | Subset and counts in `results.json` and `RESULTS.md`; no pending marker | Unit, hand-built moments (independent reference: arrays written in the test): a state with raw C < 0 at exactly one horizon and centered covariance ≥ 0 is out of the subset and counted once; the subset fraction equals the hand count ratio exactly (dyadic case, e.g. 3/8); the bound equals ln 2/(2Λ̄) + 1 step computed by NumPy in the test to 1e-15 relative; no `pass`, `threshold` or `verdict` key; `identifiers.ROWS` has no `pending` entry and `test_identifiers` pins it. Integration: a DEV-0 smoke differs from the pre-change smoke only by added `gain_bound` leaves (leafdiff: 0 changed, 0 removed). Marked "needs owner review before freeze" (statistics code). |
```

**SKIPPED** (class U other than U1, as ordered)

- **V20** (v3 section 7 Precision, H2a second part): U5, DEF-0022's power finding is not accepted by any owner answer; the draft itself drafts no replacement until the owner adopts the report.
- **V21, validation-gate risk bullet**: U2, the owner chose only the offline check, not a risk-register entry.
- **V21, H2a's second part bullet**: U5 (depends on V20).
- **V21, H3a "supported" bullet**: U8, no ruling.
- **V21, gain-bound bullet**: only for V8 option B; option A (open the row) was taken, so it does not apply.

**NO CHANGE**

- **V8** (v3 sentence after the RQ3 table): under U1 option A the draft says no change. If the owner later rules the row out (option B), V8's new sentence and the gain-bound limitation bullet become needed. V23 ("not edited": 13x margin / M5(d), F1, N2/N3) is a statement, not an edit.

**Applied as drafted although they depend on an open point (R/U or dependent R)** (the owner may still change their wording): V14b (U3), V22 (U4, U7), Methods row 24 (U4), P1 (U6), P4 (U4), P6 (U4), P7 and P8 (U7: a CPU bitwise repeat at `LPC_THREADS=8` is not demonstrated), V10, V21 iterative-error bullet and Methods row 21 (U9: the "5 of 18" flag). U10 (Claude Doc matches the export) cannot be checked.

**Points the reader should know about the applied edits**

- **V18**: the old text `- **inconclusive:** otherwise.` occurs twice (verdict per system and overall verdict). It was anchored with the preceding bullet `- **not supported:** fail on at least one system;` to hit the overall-verdict one, as the draft intends.
- **V22**: the draft's new list has four items, replacing items 1 to 3. The existing item `4. Analyze the results, and write the paper and the fair materials.` follows and now also begins with `4.` (a Markdown renderer shows it as 5). The draft did not renumber it; I did not either.
- **P2**: the draft's old text for the WU-0003.4 definition-of-done row elides its middle with `...`. The old text replaced is the live row from the quoted start (`Differences table in the unit file; ...`) to the quoted end (`... it is not rerun to make it pass.`).
- **Methods v2 row 26**: the draft gives `[option A] / [option B]` alternatives; only the option A clause is in the row, and its reason column keeps the draft's "owner ruling (pending)".
- **V21**: the five required bullets and the "Doubled thinning" bullet are inserted in that order after the last "Known limitations" bullet; the draft gave no order between them.

## 6. Verification

A script re-read the copies and the live files and checked, for every APPLIED edit part, that the new text is present in the copy and that the old text is absent (for the insertions, whose anchor text stays, that the anchor is in the live file and the added text follows it). Counts: v3 29 parts in 24 edit items, all new text present, no old text left; Methods v2 2 parts (body edit and the table block) plus the 26 rows individually, all present; decision log 1 part; ROADMAP 14 parts in 9 edit items. 0 problems. Separately, every line of new text was compared with the draft note: all are verbatim in it except the lines that are composed from the draft's instructions (V18's anchored bullet, the Methods row 26 option A text, P1's radius and definition-of-done cells, P2's title cell with its unchanged owner and depends cells).

## 7. Edit table

Class as in the draft: R required, R/U required with open wording, N nice to have, U waits on an owner decision.

| Edit | Document | Class | Status | Remark |
| --- | --- | --- | --- | --- |
| V1 | v3 | R | APPLIED |  |
| V2 | v3 | N | APPLIED |  |
| V3 | v3 | N | APPLIED |  |
| V4 | v3 | R | APPLIED |  |
| V5 | v3 | R | APPLIED |  |
| V6 | v3 | R | APPLIED |  |
| V7 | v3 | R | APPLIED |  |
| V8 | v3 | U1 | NO CHANGE | U1 option A (row opened): the draft says 'no change' to the sentence 'The hybrid's horizon gain ... without a pass/fail bar.' |
| V9 | v3 | R | APPLIED |  |
| V10 | v3 | R | APPLIED |  |
| V11 | v3 | N | APPLIED |  |
| V12 | v3 | R | APPLIED |  |
| V13 | v3 | R | APPLIED |  |
| V14a | v3 | R | APPLIED |  |
| V14b | v3 | R/U | APPLIED | wording depends on open point U3 (applied as drafted) |
| V14c | v3 | N | APPLIED |  |
| V15 | v3 | N | APPLIED |  |
| V16 | v3 | R | APPLIED |  |
| V17 | v3 | R | APPLIED |  |
| V18 | v3 | R | APPLIED | first part anchored with the preceding bullet, because '- **inconclusive:** otherwise.' occurs twice (Verdict per system and Overall verdict) |
| V19a | v3 | R | APPLIED |  |
| V19b | v3 | N | APPLIED |  |
| V20 | v3 | U5 | SKIPPED | U5 open (DEF-0022 power finding not accepted by any owner answer); the draft itself says no replacement is drafted until the owner adopts the report |
| V21 (5 required bullets) | v3 | R | APPLIED | interval coverage, slow dependence, small regimes in H3a, iterative error of PLP, lambda_max for Chua; inserted after the last 'Known limitations' bullet. The '5 of the 18' count rests on U9 (applied as drafted) |
| V21 (N bullet) | v3 | N | APPLIED | Doubled thinning, placed after the five required bullets |
| V21 (4 U bullets) | v3 | U2, U5, U8, U1 | SKIPPED | validation-gate risk (U2: owner chose only the offline check), H2a's second part (U5: depends on V20), H3a 'supported' (U8: no ruling), gain bound (only with V8 option B, not chosen) |
| V22 | v3 | R/U | APPLIED | wording depends on open point U4 (applied as drafted). The draft's new list has four items; the existing item '4. Analyze the results, and write the paper and the fair materials.' follows and now also reads '4.' (a Markdown renderer numbers it 5). The draft did not renumber it and this was not changed |
| V23 | v3 | - | NO CHANGE | draft: 'Not edited' (13x margin / M5(d), F1, N2/N3 are not v3 text) |
| M-body (M2 trajectories) | Methods v2 | R | APPLIED |  |
| M14b row 1 | Methods v2 | R | APPLIED | log row appended |
| M14b row 2 | Methods v2 | R | APPLIED | log row appended |
| M14b row 3 | Methods v2 | R | APPLIED | log row appended |
| M14b row 4 | Methods v2 | R | APPLIED | log row appended |
| M14b row 5 | Methods v2 | R | APPLIED | log row appended |
| M14b row 6 | Methods v2 | R | APPLIED | log row appended |
| M14b row 7 | Methods v2 | R | APPLIED | log row appended |
| M14b row 8 | Methods v2 | N | APPLIED | log row appended |
| M14b row 9 | Methods v2 | R | APPLIED | log row appended |
| M14b row 10 | Methods v2 | R | APPLIED | log row appended |
| M14b row 11 | Methods v2 | R | APPLIED | log row appended |
| M14b row 12 | Methods v2 | R | APPLIED | log row appended |
| M14b row 13 | Methods v2 | R | APPLIED | log row appended |
| M14b row 14 | Methods v2 | N | APPLIED | log row appended |
| M14b row 15 | Methods v2 | R | APPLIED | log row appended |
| M14b row 16 | Methods v2 | R | APPLIED | log row appended |
| M14b row 17 | Methods v2 | R | APPLIED | log row appended |
| M14b row 18 | Methods v2 | N | APPLIED | log row appended |
| M14b row 19 | Methods v2 | N | APPLIED | log row appended |
| M14b row 20 | Methods v2 | N | APPLIED | log row appended |
| M14b row 21 | Methods v2 | R | APPLIED | log row appended |
| M14b row 22 | Methods v2 | N | APPLIED | log row appended |
| M14b row 23 | Methods v2 | N | APPLIED | log row appended |
| M14b row 24 | Methods v2 | R/U | APPLIED | log row appended; wording depends on U4 (applied as drafted) |
| M14b row 25 | Methods v2 | N | APPLIED | log row appended |
| M14b row 26 | Methods v2 | U1 | APPLIED | log row appended; Option A text only (U1). The 'owner ruling (pending)' wording of the draft is kept. Refers to WU-0002.15, which is not yet in the ROADMAP (see P9) |
| DL-1 | decision log | R | APPLIED | section appended at the end of docs/study/decision_log_lpc.md (D7, D8) |
| P1 | ROADMAP | R/U | APPLIED | wording depends on open point U6 (applied as drafted). Radius cell and the definition-of-done cell are the two further parts the draft describes in words |
| P2 | ROADMAP | R | APPLIED | the draft's old text for the definition-of-done row elides the middle with '...'; the old text applied is the live row from the quoted start to the quoted end (middle taken from the live file). Title/owner/depends cells edited as one part, Owner and Serves cells otherwise unchanged |
| P3 | ROADMAP | N | APPLIED |  |
| P4 | ROADMAP | R/U | APPLIED | wording depends on open point U4 (applied as drafted) |
| P5 | ROADMAP | R | APPLIED |  |
| P6 | ROADMAP | R/U | APPLIED | new row inserted directly after the WU-0015.2 row; order and mandatory status depend on open point U4 (Y7 a, b, d) (applied as drafted) |
| P7 | ROADMAP | R | APPLIED |  |
| P8 | ROADMAP | R | APPLIED |  |
| P9 | ROADMAP | U1 | FAILED | anchor not found: old text occurs 0 times: '| WU-0002.14 |'. Closest anchor: the WU-0002.13 rows (ROADMAP.md lines 97 and 121), the last WU-0002 rows in the live ROADMAP. U1 option A is therefore NOT in the patch; ready-to-paste rows are in section 5 |
| P10 | ROADMAP | R | APPLIED |  |
