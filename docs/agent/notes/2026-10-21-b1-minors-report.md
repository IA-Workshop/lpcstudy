# Report: audit B1, the M4 proposal and minors m1 to m8 (2026-10-21)

- **Author:** claude-sonnet-5-5 (developer). Branch `wu/b1-minors` from develop `cfe9608`, not merged.
- **Source:** `docs/agent/notes/2026-10-21-audit-pre-promotion-conf1.md`.
- **Constraints kept:** no change under `lpcstudy/`; v3 not edited; no ledger entry; no seed, no sealing script, no sealed-run flag named in any command; no preset run; no tolerance grew.

## Commits (branch `wu/b1-minors`)

| Commit | Content |
|---|---|
| `a6debea` | m6: compare_runs banner text and the test line that pinned it |
| `80ad369` | m2, m4, m5 and the DEF-0022 proposed bullet: template, constants, rebuilt findings document, trace and sources |
| `8762648` | B1: unit files WU-0015, WU-0016, WU-0017, WU-0018; queue block of 2026-10-21 |
| `43a47c7` | M4: `docs/agent/notes/2026-10-21-def0022-proposal.md` |
| (this commit) | the WU-0020 log entry and this report |

## Per item

### B1 (records and WU-0017)

- (1) Unit files written from existing evidence only: `docs/agent/records/work/WU-0015-confirmatory-run.md` and `WU-0016-regeneration.md`, with per-sub-task status, ledger seqs (13, 14, 15, 20, 21, 22, 23), manifest rows, sha256 hashes, commit df8928f, run durations (15555 s CPU, 2696 s GPU, 7884 s run-2), the T0 comparison (20766 of 20766 equal, 0 different). Honest notes: the CPU authorization was entered retroactively (seq 15, no authorizing words); the pre-run checklist (pip freeze, lock, no other run) is not recorded; the regeneration was by the owner on the same host (DEC-0035); the GPU cross-check is information only; run-2 took about half the wall-clock of run-1 with equal leaves (no cause recorded).
- (2) **WU-0017.1 NOT executed.** The two `--report-only` runs are CPU-only post-processing, run from the freeze worktree `lpcstudy-wt/run/regen-freeze-1` (clean at df8928f; `git status` empty before and after) on scratch copies of the sealed `results.json` (copy hash `ae4b0fe5...cebe` verified) so that nothing is written to the worktree or the sealed run directory (`--report-only` rewrites `results.json`, `RESULTS.md` and figures in its output directory, so it must never target the sealed directory). The command contains `--preset full` and the PreToolUse hook `.claude/hooks/test_gate.py` refused it ("pilot/full runs must hold the GPU lock"). With `flock -n /tmp/lpcstudy-gpu.lock env JAX_PLATFORMS=cpu ...` the lock was held by the extension runs (two `--preset full ... --seed-id DEV-3` processes in `lpcstudy-wt/run/ext-run-392a069`); exit 1, nothing written. I did not circumvent the hook. The exact command block for the owner is in `WU-0017-v3-report.md`. Two open points recorded there: (a) the command without the sealed-run flag uses the default development seed id, so the output is expected equal to the stored `RESULTS.md` (header printed from stored provenance) but only the run shows it; if it differs, the repeat needs the sealed-run flag and the owner's environment; (b) whether the hook should exempt `--report-only`.
  - Pre-sample (not the acceptance evidence): ten narrative numbers of the stored `RESULTS.md` against the stored `results.json` leaves, 10 of 10 match (table in the WU-0017 file).
- (3) WU-0017.3 recorded as "Pending; owner and student read". WU-0018.1 recorded as "pending: audit by 2026-10-21 reused, see audit note" in `WU-0018-promotion.md` and the queue. Neither claimed done.
- (4) `docs/agent/records/work/queue.md`: one appended block (existing rows untouched) with status for WU-0015 to WU-0018.

### M4 proposal

`docs/agent/notes/2026-10-21-def0022-proposal.md`: (i) wording for the promoted report and section 10, (ii) a draft defects status line (not applied; `defects.md` is append-only, the line goes at the end of the file after the DEF-0022 status lines), (iii) options (accept as a limitation, recommended, already pre-registered at v3 line 363; accept plus a per-part report line; keep open), (iv) the owner action (a `ruling` entry and a DEC line). Applied as a marked paragraph in the findings document: limitation bullet "PROPOSED for owner review, not ruled (DEF-0022) ..." in section 10, from the new constant `def0022_proposed`, with no digit of its own. The build supports it: `check passed: 1262 traced values, 0 problems`.

### Minors

- **m1** (presentation edits after the sealed results were seen): no code change. The audit already assessed them (DEC-0036 ruled R1 and R4). The promoted report must not say the frame was untouched after the result (audit wording).
- **m2** fixed: the template sentence "Regeneration ... pending" is now "Regeneration of the official run (WU-0016, v3 §9 item 4): each dated line below is appended after the event it reports." The document was rebuilt.
- **m3** (A6 plan amendment `official_words` unconfirmed): no change; owner item below.
- **m4** fixed: the H3b weight-tree band label "(strict)" is now "(closed at 0, open at 0.2)" (three rows of section 6), and a note `h3b_edge_note` follows the secondary table (a lower bound of exactly 0 is inside the band; the verdict words are the stored ones). No number changed; the Rossler row still reads 0 and [0, 0.1301], pass.
- **m5** done: a dated line of 2026-10-21 in section 9 (the free slot) says the rebuild ran on the branch that carries the extension code, that the builder imports nothing from the study code, and that no result number changed. It is worded without digits and without the banned stems (it passed `check`). The WU-0020 log carries the same statement.
- **m6** fixed: `tools/compare_runs.py` `REVIEW` text is now "tolerance and verdict-comparison code, rules ratified by the owner (DEC-0030 OF-5 and OF-7, DEC-0032 B9); CSQ2 use in WU-0016". One test asserted the old text (`tests/unit/test_tools_compare_runs.py`, the end-to-end banner test): it now asserts the new phrase and the absence of "needs owner review". Committed texts `run-1-compare.txt`, `run-2-compare.txt` and the notes copy keep the old banner (records are not rewritten); the WU-0016 file says so.
- **m7** checked, no change needed: the document already carries the Q-N two-readings sentence (section 4, "Q-N is read by the table of v3 §7, separately for each of its two parts ... the stored overall word `verdicts.Q-N` collapses them to the logit part: its per-system words are lorenz63 reduces, rossler reduces, chua reduces"), and the Q-N table row shows both parts.
- **m8**: no change; owner item below.

## Commands run and results

| Command | Result |
|---|---|
| `python -m lpcstudy --preset full --report-only --out <scratch>/ro1` (freeze worktree) | refused by the hook (GPU lock) |
| `flock -n /tmp/lpcstudy-gpu.lock env JAX_PLATFORMS=cpu .venv/bin/python -m lpcstudy --preset full --report-only --out <scratch>/ro1` and `ro2` | exit 1 and 1 (lock held); nothing written |
| `tools/findings_build.py render ... --release-ref ledger-seq-20 ...` into a scratch directory | `rendered ...: 1262 traced values, 0 leaves not recorded, 0 null leaves`; `check passed: 1262 traced values, 0 problems` |
| `tools/findings_build.py check docs/agent/notes --stem 2026-10-20-prelim-findings-conf1` (after the dated lines) | `check passed: 1262 traced values, 0 problems` |
| `tools/test_impact.py --base cfe9608 --explain` | `tests/unit/test_tools_compare_runs.py`, `tests/unit/test_tools_findings_build.py` |
| `tools/run_tests.sh unit tests/unit/test_tools_compare_runs.py tests/unit/test_tools_findings_build.py` (once) | `351 passed in 17.02s` |

Note on `test_impact.py` with the default base `main`: the base differs from develop in `lpcstudy/`, so that default gives the whole unit tier; the base `cfe9608` (develop) is the change set of this branch.

Findings-document changes (diff vs HEAD before the rebuild): three band labels, one note paragraph, the section 9 sentence, one dated line, one limitation bullet. `grep -ci "confirmed|proved|significant"` on the document gives 0. The trace file changes by row renumbering and the two new constants (1262 rows against 1260); `sources.json` changes only in `cwd`; the three figures are byte-identical.

## What remains for the owner

1. **Run WU-0017.1** (command in `WU-0017-v3-report.md`) when the GPU lock is free, or rule that `--report-only` is exempt from the hook; then hash-compare. If the output differs from `2a4c1d06...4577`, the repeat needs the sealed-run flag in the owner's environment.
2. **WU-0017.3** (owner and student read) and **WU-0017.2** (figures) are open; WU-0018.1 re-audits the v3 report after them.
3. **M1:** a ledger `note` that records the owner's review of the verdict, statistics, seed and provenance code (WU-0004.5), or waives it; DEF-0001 closing line.
4. **M2:** a `ruling` entry that the official run was launched by the owner under the owner's own authority, accepting seq 15 as its record (and saying whether any agent assisted).
5. **M3:** the promoted report's reproducibility wording ("regenerated bitwise by the producer on the same host (DEC-0035); no independent-actor or second-host regeneration"); optional agent-session regeneration.
6. **M4:** the DEF-0022 ruling (`2026-10-21-def0022-proposal.md`); then rebuild the findings document with the ruled wording.
7. **Owner items from the minors:**
   - **m3:** the plan amendment of 2026-10-20 (A6: the source name `official_words` may be quoted inside `[CROSS-CHECK]`; WU-0020 log and `WU-0020-review.md`) is "to be confirmed by the owner" and is unconfirmed. One owner line.
   - **m8:** v3 section 9 has two items numbered "4." (lines 416-417, frozen text). Cosmetic; cite "item 4 (regeneration)" in every document. v3 is not edited.
8. Merge of `wu/b1-minors` into develop (not done by me).
