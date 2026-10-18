# Ledger and decision entries the owner still owes: draft batch (freeze blockers B3, B11, C11)

Prepared 2026-10-18 by claude-opus-5-5 (drafting only) on branch `wu/0004-owner-packet`, cut from develop `7b6f6e6`. No ledger entry, `decisions.md` entry, governed file or study document was written or edited. `python3 tools/ledger.py verify` and `status` were the only ledger commands run; both are read-only.

Sources:
- `docs/agent/notes/2026-10-18-freeze-blockers.md`, all of it;
- `docs/agent/notes/2026-10-11-amendments-for-owner.md` §§1-36 (cited as "§n");
- `docs/agent/notes/2026-10-18-owner-decision-drafts.md` (cited as "drafts §n");
- `docs/agent/records/decisions.md`, DEC-0001 to DEC-0027;
- `tools/ledger.py`;
- `docs/agent/governance/` (GOV.36, GOV.41, GOV.50, PRIME.1, PRIME.5, LPC.PC.5, LPC.PC.8, LPC.PC.25, the LPC.AUTH list).

**Every entry below is for the owner to enter.** Agents may draft these acts but never perform them (PRIME.1, GOV.49, GOV.50). This note is a draft and carries no authority. No number in it is a hypothesis-test result: every run cited is DEV-0, DEV-1 or DEV-2.

---

## 0. Conventions and order of entry

- **Ledger state when drafted.**
  - `verify`: chain intact, 6 entries, all dated 2026-10-10.
  - `status` in the develop worktree: all 22 governed files "adopted, unchanged (entry 5)".
  - `status` in the main worktree: `.claude/settings.json: CHANGED since adoption (entry 5)`. This is the owner's uncommitted removal of `"Bash(git merge *)"` from the ask list.
- **Command form.** Every command below uses:
  - `--actor "<owner name>"`: write the same string the owner puts on line 11 of `project-constitution.md` (L1);
  - `--role "human owner"`;
  - `--data` with these keys:
    - `ruled_on`: the date the ruling was given;
    - `source`: the note section;
    - `evidence`: the paths.

  `tools/ledger.py` stamps `utc` with the time of the append, not the time of the ruling. That is why `ruled_on` is needed.
- **Use one worktree for every append.** `tools/ledger.py` takes `ROOT` from its own location. An append therefore hashes the files of, and writes the ledger of, the worktree it runs in. If two worktrees append independently, they produce two entries with the same `seq`. Each branch then verifies on its own, but the merge conflicts.
  - Suggested practice: commit the `settings.json` change, then do every append in develop, and commit after each group. `main` receives the entries at the B5 merge.
- **Amendments: edit, then append.** `--files` hashes each file at the moment of the append, and `status` treats an `amendment` with files like a re-adoption. The sequence is:
  1. edit the file;
  2. commit it;
  3. append the entry;
  4. run `status`, which must read "adopted, unchanged (entry n)".
- **After each append:** run `python3 tools/ledger.py verify`, then commit the ledger with the record it cites.
- **DEC numbers.** DEC-0028 to DEC-0032 below are proposed numbers, in order of entry. At entry time, take the next free number and update the cross-references.
- **Suggested order of entry.**
  1. L1 to L4: governance hygiene.
  2. The `decisions.md` entries D1 to D7 (commit them first, because the rulings cite them).
  3. Rulings L7 to L11: the rulings of 2026-10-11 to 2026-10-13.
  4. L12 to L22: the rulings of 2026-10-17 and 2026-10-18.
  5. L5 and L6: the document amendments, after the B1 edits.
  6. Waivers, if any (L23).
  7. At the freeze: L24 (commitment, from the sealing step), L25 (classification) and L26 (governance reread).

## 1. Observations (not entries)

1. **Placeholder actor.** Three ledger entries carry the actor `<you>`: entry 4 (`authorization`), entry 5 (`adoption`, the 22 governed files) and entry 6 (`authorization`).
   - Entries 4 and 6 have the same truncated summary: "LPC.AUTH.1 (environment setup), LPC.AUTH.3 (compute limits) ...".
   - Entry 6 has the same timestamp as entry 5 (2026-10-10T19:21:33Z). Entry 4 is 34 s earlier.
   - From the chain alone it cannot be told whether entry 6 repeats entry 4 or records another grant. Only the owner can say. L2 is drafted with that blank.
2. **No owner-typed entries yet.** The chain holds no `classification`, `ruling`, `waiver` or `amendment` entry. The CSQ2 classification appears only in two places:
   - the `data.owner_statement` of proposal entry 1;
   - the project constitution adopted by entry 5 (LPC.PC.5).

   The freeze `classification` entry (L25) would be the first entry of that type.
3. **Truncation is not detected.** `verify` checks `prev_sha256` and `seq` only. Removing the last k entries leaves a chain that still verifies, so the head is not protected. The checks also do not refuse a placeholder actor, which is how entries 4 to 6 pass. Suggestion, not a requirement: record the SHA-256 of the last ledger line outside the ledger at the freeze, for example in the tag message (see the review packet, §9).
4. **Rulings not yet in code.** These rulings are not yet implemented in code or files, so their entries should say "to be implemented", not "done":
   - **B6b.** `h3a_logrank` (`lpcstudy/analysis.py` lines 1857-1958) computes per-regime *state* counts, not per-regime *event* counts. "Report event counts per regime" is a small statistics or report change, and no C-item in the freeze-blocker list covers it. I read the code; I ran no test.
   - **B7 and the OF-4 text.** Branch `wu/0004b-budget-text` holds only a plan commit (`64e59d6`).
   - **B8.** Branch `wu/0004a-dirty-guard` has no commit. `provenance.git_state` records `dirty`, and nothing refuses a dirty tree.
   - **B10.** Branch `wu/0004c-gpu-test` has no commit, and `tests/gpu/` does not exist.
   - **DEV registry.** `seeds/development_seeds.json` still lists DEV-1 to DEV-4 as "unused".
5. **The drafts are stale in five places since the rulings of 2026-10-18.** Correct them before entry (D1, D2):
   - Drafts §1 item 2 says class (a) "includes the four H1a fit leaves re-tagged under OF-7". As merged (WU-0003.9c, `91c93f5`), `fitted_inverse_dim` and `ci_inverse_dim[0..1]` are class (a), and `floor_rms` is class (g).
   - Drafts §1 "Affects" says "Until that change lands the tool applies the stricter max-of-both rule". The OF-5 change has landed (`91c93f5`).
   - Drafts §1 item 4 and "Affects", and drafts §2 "Device" and "Affects", say the confirmatory device is "not decided here" or "stays open". It was decided on 2026-10-18 (§36, B4; D4 below).
   - Drafts §2 "Compute against LPC.PC.22" is still correct. It should add that the official run is on the CPU (about 4.7 h, not a clean figure).
6. **The scope of the en-bloc ratification in §36 (B9) is ambiguous.** The owner chose "ratify en bloc". The parenthesis in §36 names only some of the B9 items. The B9 items it does not name are:
   - DEC-0024 point 2 (now superseded in wording by addendum A3);
   - DEC-0020's open arm (the N3 licence scope; the D3 SE_new arm was closed by DEC-0027);
   - DEC-0023;
   - DEC-0024 A2 (its wording);
   - the Q6 clause K2 (d3 shown on scratch copies).

   The ruling entry (L22) should say "all B9 items" or list the exceptions.
7. **The en-bloc ratification includes plan amendment 1 O1 to O8.** Three of those recommendations were overtaken or not followed:
   - O2 recommended R4 as well. R4 was not run.
   - O3 recommended setting `XLA_FLAGS=--xla_gpu_deterministic_ops=true` for GPU runs. It was never set; R1 = R2 bitwise without it.
   - O4 recommended "the same device type". The owner ruled differently (B4: the CPU is official, the GPU is a cross-check).

   L22 and D7 should say that O2 (R4), O3 and O4 are overtaken, not ratified.
8. **B4 has a second question that §35 and §36 do not answer.** Do R1, R3 and R6 satisfy LPC.PC.6's "validation gate V1-V7 passes on all three systems in the rehearsal", with R5's Chua V6 failure recorded under DEF-0026? Or must the rehearsal pass at full size on the chosen device (R6 did, on the CPU)? D4 leaves a blank for it.
9. **Owner confirmations that no ruling covers yet** (detail in the review packet, §8):
   - the DEF-0028 readings (§30);
   - the RETAGS readings, including the R3 premise about `ratio` and `ratio_ci`;
   - the WU-0003.8d judgement calls (b), the exit code, and (d), the label per part;
   - `follows_k`.

   Blanks are left in D3 and L14 to L16 for them.

---

## 2. `decisions.md` entries (for the owner to enter; the main session may relay them as for DEC-0015 to DEC-0027 if the owner prefers)

### D1. DEC-0028: WU-0003.6 reproducibility tolerance

- **Type:** `decisions.md` entry.
- **Subject:** the declared reproducibility tolerance: bitwise at the same context; the A6 tiers at equal contexts; the TD statistic, away-arm form, bound 3.4, across devices.
- **Text:** paste drafts §1, the fenced block at lines 11-43 of `docs/agent/notes/2026-10-18-owner-decision-drafts.md`, with these substitutions:
  - `DEC-nnnn` becomes `DEC-0028`;
  - item 2: "(class a; this includes the four H1a fit leaves re-tagged under OF-7)" becomes "(class a; this includes `fitted_inverse_dim` and `ci_inverse_dim[0..1]`, re-tagged under OF-7; `floor_rms` is class (g), and `ratio` and `ratio_ci` stay in the cp chain at 1e-12, see DEC-0030 item 9)";
  - item 4, last sentence, becomes: "The choice of confirmatory device is DEC-0031.";
  - "Affects", first bullet, becomes: "`tools/compare_runs.py`: the TD failing rule is |z_away| > 3.4 (WU-0003.9c, merged 91c93f5, independent review `WU-0003.9c-review.md`); needs owner review before freeze.";
  - "Affects", last bullet, becomes: "Not decided here: O3 (`--xla_gpu_deterministic_ops`). O4 is DEC-0031."
- **Evidence:**
  - `docs/agent/records/work/WU-0003-R1R2.md`;
  - `WU-0003-R1R2-compare-r1-r2.txt`;
  - `WU-0003-R3R6-compare-R1-R3.txt`;
  - `WU-0003-R3R6-compare-R5-R6.txt`;
  - `WU-0003-9c-compare-R1R3.txt`;
  - `WU-0003-9c-compare-R5R6.txt`;
  - `docs/agent/notes/2026-10-14-math-wu0003.md` §M1, §M2;
  - `docs/agent/notes/2026-10-14-math-wu0003-9-q1.md`.
- **From:** §29 (proposal), §33 (ruling), §34 points 1-4; drafts §1; freeze blockers A1 (WU-0003.6), B3 item 4.

### D2. DEC-0029: WU-0003.6 confirmatory sample size

- **Type:** `decisions.md` entry.
- **Subject:** the confirmatory run keeps the full preset.
- **Text:** paste drafts §2, the fenced block at lines 49-75, with these substitutions:
  - `DEC-nnnn` becomes `DEC-0029`;
  - the "Device" bullet ends with: "The official sealed run is on the CPU (DEC-0031).";
  - in "Affects", "O4 (the confirmatory device, plan amendment 1 A12) stays open" becomes "the device is DEC-0031".

  Note: the FULL preset values the entry cites (`lpcstudy/config.py`) are almost all baseline (v1) lines: 209 of 220 lines of `config.py` are unchanged since `f01360d`.
- **Evidence:**
  - `WU-0003-R1R2-R5-rehearsal-report-r5.txt`;
  - `WU-0003-R1R2-R5-rehearsal-report-r1-observed-r5.txt`;
  - `WU-0003-R3R6-report-R6.txt`;
  - `WU-0003-R3R6.md`;
  - `docs/agent/notes/2026-10-14-math-wu0003.md` §M5.1.
- **From:** §29, §33; drafts §2.

### D3. DEC-0030: the owner's rulings of 2026-10-17 and 2026-10-18 on the rehearsal, the LM study and the comparison tools (C11 (i))

- **Type:** `decisions.md` entry. It consolidates §26 and §29 to §33, which the note says are "not ledger entries".
- **Subject:** one record of the 18 rulings given through the question tool, with their implementation state.
- **Text:**

```
## DEC-0030: Owner rulings of 2026-10-17 and 2026-10-18 on the WU-0003 rehearsal, the LM-doubling study and the comparison and diagnostics tools  (2026-10-18, human owner; answers given through the question tool and recorded by the main session in docs/agent/notes/2026-10-11-amendments-for-owner.md §§26, 29, 30, 31, 33; text drafted by claude-opus-5-5)

**Decision.** The note sections are the record of the wording; this entry restates them.
1. OF-2 (§26, 2026-10-17): "Equal contexts only". The V1 1e-12 rule of plan item 11 applies only to pairs whose context digests are equal (tiers T0 to T2); GPU-against-CPU pairs (TD) are judged by the TD statistic.
2. R5 and R6 (§26): authorized (full preset on DEV-2; GPU with the states dump; CPU at LPC_THREADS=8). Run on 2026-10-17.
3. DEF-0026 (§26): the offline V6/V4 check on DEV-1 to DEV-4 only. Not chosen: a pre-registered response to a sealed-run gate failure, evaluating the outcome-free gate checks first, a risk-register-only entry. A sealed-run gate failure stays a hard stop referred to the owner (DEC-0027).
4. OQ-R9 (§26): the diagnostics defaults (tool seed 20261018, 1000 permutations, 2000 resamples) are pre-registered; the first default-options report per run is the record; any other option is labelled non-default and is not the record.
5. O5, DEF-0027 (§29): report and flag only. The design value stays 15 LM iterations; the iteration-sensitivity flag is reported per part; no new reference run.
6. DEF-0028 (§29): amend tools/lm_doubling.py to the plan (structural switch, class U, before the X bullets). Done: merged f14c8fa after independent review (WU-0005.6-rule-r-order-review.md). Readings of §30: [owner: "confirmed" | "ruled otherwise: ..."]: (a) a half-width <= 0, a NaN value and an infinite point estimate with finite bounds are not structural switches; (b) an infinite lower or upper bound at any arm is.
7. OF-R2, OF-G6 (§29): keep the range. The pre-registered kappa_E range [0.7071, 1] governs; no dump change, no half-split estimator, no rerun.
8. Block length (§29, §31): keep block length 5 for all three systems (no v3 or Methods v2 amendment). OF-3: the pooled permutation reading governs the D2 verdict; the A5 rule and beta-hat-5 are printed as information. A report-only "block-sensitive" label marks a primary part whose verdict would change if the half-width were widened by sqrt(max(1, V*(10)/V*(5))); it changes no criterion. Implemented in WU-0003.8d (merged 1e3d726). Judgement calls of WU-0003.8d: [owner: (b) label rows, including "not computable" rows, never set exit 2 — "confirmed" | "count them for the exit code"]; [owner: (d) the label is per primary part, not per combined hypothesis verdict — "confirmed" | ...].
9. OF-7 (§33, 2026-10-18): re-tag the H1a fit leaves out of the cp chain under the A6 QoI rule; the 1e-12 rule stays elsewhere. As merged (WU-0003.9c, 91c93f5): fitted_inverse_dim and ci_inverse_dim[0..1] class (a), 1e-4 s; floor_rms class (g); ratio and ratio_ci stay cp 1e-12 with the OF-7 pointer. [owner: "ratio and ratio_ci are covered by OF-7 (class a)" | "they stay cp 1e-12"; note: the text ruled on said they "already" were at 1e-4 s, which stopped being true at da22cdd on 2026-10-17; under the literal reading every T2 pair fails on 18 H1a leaves with correct code.] [owner: floor_rms "class (g) as built" | "class (a) as the ruling text says".]
10. OF-1 (§33): keep strict. No licence for H2c, H2d or H3c under T1 to T3 for a fitted-coefficient change beyond 1e-6.
11. R5 of the WU-0003.9 review, O3 (§33): the declared-tolerance rule O3 is information only on T1 to T3 pairs.
12. Q7, Q8, Q9 and the handling-count scope (§33): keep the tool's strict readings; the handling-count licence is kept as written. [owner: follows_k (the K-block listing, labelled a looser reading in WU-0003.9 R17) — "confirmed" | ...]
13. OF-4 (§33): the F1 wording is corrected by DEC-0024 addendum A3.
14. OF-5 (§33): the away-arm TD form is the failing rule (|z_away| > 3.4 over 18 parts); the symmetric form is printed as information. Merged in WU-0003.9c (91c93f5). The plan text of A6 and B1 item 5 is left as written; the plan amendment for it is the planner's.
15. OF-F3 (§33): keep N = 24 diagnostic series as written (H1c not counted).
16. OF-G3 (§33): the margin band 0.0850 to 0.0933 governs the H2a(ii) comparison against v3; the hw band [0.0603, 0.135] stays printed, not governing.
17. F4 and Q6 (§33): keep both as built; Q6 is recorded as WU-0003 plan amendment 11. [owner: K2, d3 shown on scratch copies of the S3 pair — "covered by keep as built" | ...]
18. WU-0003.6 (§33): DEC-0028 (reproducibility tolerance) and DEC-0029 (sample size).

**Alternatives weighed.** As listed in the cited note sections and the mathematician's notes (2026-10-14-math-wu0003.md, 2026-10-14-math-wu0003-9-q1.md, 2026-10-14-math-wu0003-3a-kappa.md, 2026-10-17-math-block-length.md).

**Affects:** tools/compare_runs.py, tools/lm_doubling.py, tools/rehearsal_diagnostics.py, tools/rehearsal_report.py, lpcstudy/budget.py (OF-4), WU-0003, WU-0004.1, WU-0016.

**Dissent and resolution (REPRO.8):** OF-5, see DEC-0028. Otherwise none recorded.

**Status:** owner rulings (question tool); ledger rulings L12 to L17. Items 6, 8, 9, 12 and 17 carry confirmations the owner fills in above. Needs owner review before freeze (tolerance, comparison and statistics tool code).
```

- **Evidence:**
  - `WU-0003.9c-review.md`;
  - `WU-0003.8d-review.md`;
  - `WU-0005.6-rule-r-order-review.md`;
  - `docs/study/lm_doubling_dev0_report_v3.md`;
  - `docs/agent/notes/2026-10-17-math-block-length.md`;
  - the run records cited in D1.
- **From:** §§26, 29, 30, 31, 33; freeze blockers B3 item 3, C11 (i).

### D4. DEC-0031: confirmatory device (B4)

- **Type:** `decisions.md` entry.
- **Subject:** one official sealed run on the CPU; a GPU run of the same seed is a cross-check and informs only.
- **Text:**

```
## DEC-0031: The confirmatory run is on the CPU; a GPU run of the same sealed seed is a cross-check that informs only  (2026-10-18, human owner; answer given through the question tool after the clarification of §35, recorded in docs/agent/notes/2026-10-11-amendments-for-owner.md §36; text drafted by claude-opus-5-5)

**Decision.** Pre-declared before the freeze (WU-0003 plan amendment 1, A12 O4):
1. The official sealed run (CONF-1, full preset) runs on the CPU at LPC_THREADS=8. Device and thread count are part of the freeze configuration (LPC.PC.8; DEF-0023: the thread count changes results in the last bits).
2. A GPU run of the same sealed seed is a cross-check. It is compared with the official run by tools/compare_runs.py with the TD statistic, away-arm form, failing bound 3.4 (DEC-0028 item 3). The CPU verdicts stand. A differing verdict-type leaf, a TD failure or a GPU gate failure is reported as information and changes no verdict.
3. The GPU cross-run is a second use of the sealed seed: it needs its own per-action authorization (LPC.AUTH.6), and its outputs are released only with the official run's release decision.
4. The regeneration by another actor (WU-0016) runs on the CPU: bitwise (T0) on the same platform and LPC_THREADS, otherwise judged by the A6 tiers (DEC-0028 item 2).
5. [owner: whether R1 (GPU pilot), R3 (CPU pilot) and R6 (CPU full) satisfy LPC.PC.6 "validation gate V1-V7 passes on all three systems in the rehearsal", with R5's Chua V6 failure (GPU context) recorded under DEF-0026 — "yes" | "the rehearsal must pass at full size on the CPU (R6 did)" | ...]
6. [owner: O3 for the GPU cross-run: "XLA_FLAGS not set (R1 = R2 bitwise without it)" | "set --xla_gpu_deterministic_ops=true".]

**Evidence (DEVELOPMENT; not hypothesis tests).** R5 against R6 (DEV-2, full): tier TD, 18 of 18 parts, 0 failing, max |z_away| 2.26; 52 verdict-type leaves differ; Chua V6 fails on the GPU context (2.405e-3 against 1e-3) and passes on the CPU context (3.3e-4). R1 = R2 bitwise on the GPU (20533 leaves). CPU wall time of R6 17031 s (4.73 h; possibly shared CPU), within LPC.PC.22's 12 h. Records: WU-0003-R1R2.md, WU-0003-R3R6.md, WU-0003-R3R6-compare-R5-R6.txt, WU-0003-R3R6-gates-clips-R6.txt.

**Alternatives weighed.** Both runs on the GPU (fast; a regeneration on another GPU is only TD; the only full-size GPU rehearsal failed V6). Accepting TD for the regeneration (weakest). Pinning trajectory generation to the CPU (a numbers-changing code step after the rehearsal).

**What this does not change.** The per-seed gate risk (DEF-0026: about 4.6% for Chua V6, 11 to 25% for V4 or V6 at full size) is the same on either device. A gate failure of the official CPU run is a hard stop referred to the owner, never retuned (DEC-0027; no pre-seal response rule, §26).

**Affects:** the freeze configuration (WU-0004.7), WU-0015, WU-0016, DEC-0028 item 4, the gpu test of B10 (which tests the cross-check device only). Supersedes plan amendment 1 O4's recommendation "(b) same device type".

**Dissent and resolution (REPRO.8):** none recorded. **Status:** owner ruling 2026-10-18; ledger ruling L20.
```

- **Evidence:** as in the text.
- **From:** §35 (B4, clarification asked), §36 (B4); freeze blockers B4.

### D5. DEC-0024 addendum A3 (OF-4)

- **Type:** `decisions.md` addendum.
- **Subject:** F1 is an indicative value, not a worst case for the median.
- **Text:** paste drafts §3.2, the fenced block at lines 93-113, unchanged.
- **Evidence:** `docs/agent/notes/2026-10-14-math-wu0003.md` §M5; `m5_d5sim.log`; `lpcstudy/budget.py` lines 565, 570, 702.
- **From:** §16 (OF-4), §33, §34 point 7; drafts §3; freeze blockers B11 bullet 1, C3.

### D6. WU-0003 plan amendment 11 (Q6)

- **Type:** record in the unit file, not `decisions.md` and not the ledger. The main session or the owner appends it.
- **Subject:** B2 d1 is met on synthetic trees plus the real-schema extract (K1), and a record of d3 as built (K2).
- **Text:** paste drafts §4, the fenced block at lines 128-145, into `docs/agent/records/work/WU-0003-dev-rehearsal.md` after plan amendment 10. Add the owner's answer on K2 (observation 6).
- **From:** §33 (F4 and Q6), §34 point 8; drafts §4.

### D7. DEC-0032: the freeze-blocker rulings B5 to B11 (except B4)

- **Type:** `decisions.md` entry.
- **Subject:** the owner's answers of §35 and §36 on main, the limitations, the LM row, the dirty-tree guard, the en-bloc ratification, the gpu test and the freeze record.
- **Text:**

```
## DEC-0032: Owner rulings of 2026-10-18 on the freeze blockers B5 to B11 (B4 is DEC-0031)  (2026-10-18, human owner; answers given through the question tool, recorded in docs/agent/notes/2026-10-11-amendments-for-owner.md §35 and §36 against docs/agent/notes/2026-10-18-freeze-blockers.md; text drafted by claude-opus-5-5)

**Decision.**
1. B5 (where the freeze lives): develop is merged into main after the owner's code review (WU-0004.5) and a green full suite at the freeze gate; the freeze commit and tag live on main. No main request is made now.
2. B6a (DEF-0020): keep the pre-registered percentile intervals and block length 5; no widening and no other interval procedure. The measured undercoverage (DEF-0020, DEC-0018) and the report-only block-sensitive label are stated as limitations.
3. B6b (DEF-0018): keep H3a as is (no per-regime or event-count minimum; DEC-0011 O1 stands); report the event counts per regime; state the exposure (one event in a tiny regime can give an extreme log-rank p and a Holm-adjusted pass) as a limitation. To be implemented: h3a_logrank reports per-regime state counts, not event counts.
4. B7 (LM row; WU-0005.6 O4 and O6): the DEV-0 flags are quoted as development evidence with the sqrt(n_full/n_pilot) projection; the sealed report keeps "not estimated" plus a pointer; no sealed 30-iteration twin run. A text and small budget change (WU-0004b), with review and owner review.
5. B8 (DEC-0008 C): implement the refusal of a sealed run on a dirty tree or an unknown commit (code, tests, independent review, then the owner's review). VmHWM recording: [owner: "yes" | "not now"].
6. B9: ratify en bloc the working defaults and stricter readings of freeze blockers B9 [owner: "all B9 items" | "only: N2/N3 under Option C, PF-1 to PF-5, OF-H1, OF-I2, C6-R6, the R3 families of WU-0003.9b, the planner defaults of WU-0002.11c (Q1, Q2) and WU-0002.14 (O1 to O8), WU-0005.6 O1 to O3, WU-0003 plan amendment 1 O1 to O8"], except that plan amendment 1 O2 (R4, not run), O3 (GPU deterministic-ops flag, never set) and O4 (same device type; replaced by DEC-0031) are recorded as overtaken, not ratified. Ruled separately: N2 and N3 keep the code's reading (N1, N2 and N3 computed and reported, none asserted; the consistency ranges asserted); OF-I1 keeps the min anchor (H1d at 98.3% prints 0.9794). The DEV registry statuses are updated (DEV-1, DEV-2 used; DEV-3, DEV-4 used for V6 contexts only).
7. B10: write tests/gpu/test_reproducibility.py (smoke twice on the GPU against the tolerance of DEC-0028), under the GPU lock; the owner edits the ROADMAP WU-0003.4 row and definition of done to what was done.
8. B11: the sealed run keeps the states dump off; the freeze is recorded as a ledger classification entry (entry to CSQ2) plus the commitment entry written by the seed-sealing step. [owner: WU-0004.8, the governance reread (LPC.PC.25), is performed by <name>.]

**Alternatives weighed.** As in the freeze-blocker note, B5 to B11.

**Affects:** WU-0004.1 to .8, WU-0015, WU-0016, lpcstudy/analysis.py and report.py (B6b), lpcstudy/budget.py (B7), lpcstudy/__main__.py and provenance.py (B8), tests/gpu/ (B10), seeds/development_seeds.json (B9), ROADMAP.md (B10).

**Dissent and resolution (REPRO.8):** none recorded. **Status:** owner rulings 2026-10-18; ledger note L21 and ruling L22.
```

- **Evidence:** `docs/agent/notes/2026-10-18-freeze-blockers.md` B5-B11; DEF-0018, DEF-0020 and their status lines; `WU-0006.5-option-c.md` R1; `WU-0005.6-lm-doubling.md` O4-O6.
- **From:** §35, §36; freeze blockers B5 to B11.

---

## 3. Ledger entries (each is for the owner to enter)

### Governance hygiene

**L1. `amendment`: fill the blank governance fields.**
- **Subject:** the owner's name and the operating-cost discipline.
- **From:** §4, last row; DEC-0008 C; freeze blockers B3 item 5, B11.
- **Evidence:** the commit that fills the fields; DEC-0008 C.
- **Note:** this must come first, so that `--actor` matches the constitution.

```
python3 tools/ledger.py append --type amendment --actor "<owner name>" --role "human owner" \
  --authority "GOV.41; GOV.36; DEC-0008 C" \
  --summary "Fill the blank fields: owner name (project-constitution.md line 11), operating-cost discipline (project-constitution.md line 185; authorizations.md LPC.AUTH.4, line 53)" \
  --files docs/agent/governance/project-constitution.md docs/agent/governance/authorizations.md \
  --data '{"ruled_on": "2026-10-11", "source": "amendments note section 4; DEC-0008 C", "evidence": ["docs/agent/records/decisions.md#DEC-0008"]}'
```

**L2. `note`: correct entries 4, 5 and 6 (GOV.36).**
- **Subject:** the actor of entries 4 to 6 and the authorizations they granted.
- **From:** §5; DEC-0008 C; freeze blockers B3 item 1.
- **Evidence:** ledger entries 4 to 6 (observation 1).

```
python3 tools/ledger.py append --type note --actor "<owner name>" --role "human owner" \
  --authority "GOV.36; PRIME.5; DEC-0008 C" \
  --summary "Correction of entries 4, 5 and 6 (not edited): the actor recorded as <you> is <owner name>; entry 4 granted <LPC.AUTH identifiers and limits>; entry 6 <repeats entry 4 | granted LPC.AUTH identifiers>" \
  --data '{"ruled_on": "2026-10-11", "source": "amendments note section 5", "corrects_entries": [4, 5, 6]}'
```

**L3. `authorization`: lift the LPC.AUTH.2 page cap (DEC-0009).**
- **Subject:** the 50-pages-per-unit limit of LPC.AUTH.2(b) is lifted for the researcher for the rest of the season.
- **From:** §5; DEC-0009; freeze blockers B3 item 1.
- **Evidence:** `decisions.md` DEC-0009 and DEC-0010; `docs/agent/records/network-log.jsonl`.
- **Owner choices before entering:**
  - The §5 draft adds "researcher may use the alphaXiv connectors". DEC-0009 does not record that approval. Keep that clause only if it was given. It also needs an edit to `.claude/agents/researcher.md` (L5).
  - "Season" has no end date. State one if wanted.
  - Alternative: change the limit in `authorizations.md` line 36 itself (fold it into L1), because the governed text still says 50 pages.

```
python3 tools/ledger.py append --type authorization --actor "<owner name>" --role "human owner" \
  --authority "LPC.AUTH.2; PRIME.7" \
  --summary "Lift the 50-pages-per-unit cap of LPC.AUTH.2(b) on researcher retrievals for the remainder of the season; all other LPC.AUTH.2 limits unchanged" \
  --data '{"ruled_on": "2026-10-11", "quote": "Cap is hereby removed for the remainder of this season. Proceed with all recommendations.", "source": "decisions.md DEC-0009; amendments note section 5", "acted_on_before_entry": "researcher retrievals for WU-0007, WU-0012 and WU-0013 follow-ups (DEC-0009, DEC-0010)"}'
```

**L4. `amendment`: `.claude/settings.json`.**
- **Subject:** `Bash(git merge *)` is removed from the ask list, as edited by the owner on `main` on 2026-10-17.
- **From:** §24; freeze blockers A2 (ledger row), B3 item 2.
- **Evidence:** `git diff .claude/settings.json` in the main worktree; `ledger.py status` in the main worktree.
- **Note:** if L5 also edits `settings.json` (`PJRT_NPROC`/`NPROC`, §7; the old `flock` forms, §4), do one amendment in L5 instead.

```
python3 tools/ledger.py append --type amendment --actor "<owner name>" --role "human owner" \
  --authority "GOV.36; owner instruction of 2026-10-17 (amendments note section 24)" \
  --summary "Amend .claude/settings.json: remove Bash(git merge *) from the ask list" \
  --files .claude/settings.json \
  --data '{"ruled_on": "2026-10-17", "source": "amendments note section 24"}'
```

**L5. `amendment`: ROADMAP, DEVELOPMENT_WORKFLOW and `.claude/` (B1).**
- **Subject:** the governed documents are brought to what the code tests.
- **From:** §1, §4, §7, §9 to §14, §33, §35 (the B10 row); freeze blockers B1, B3 item 2.
- **Evidence:** the commit with the owner's edits.
- **Note:** B1's option (all four document groups, the minimum set, or an addendum) is not yet chosen. List only the files actually edited.

```
python3 tools/ledger.py append --type amendment --actor "<owner name>" --role "human owner" \
  --authority "GOV.36; DEC-0008; DEC-0026; DEC-0030; DEC-0032" \
  --summary "Amend ROADMAP.md, DEVELOPMENT_WORKFLOW.md and .claude/ files per amendments note sections 1, 4, 7, 9-14, 33, 35; re-adopt the changed governed files" \
  --files ROADMAP.md DEVELOPMENT_WORKFLOW.md <each changed .claude/ file> \
  --data '{"source": "amendments note sections 1, 4, 7, 9-14, 33, 35; freeze-blockers B1", "commit": "<hash of the edit commit>"}'
```

**L6. `amendment`: v3 and Methods v2 (B1).**
- **Subject:** v3 and Methods v2 state the DEC-0008 definitions, the §7 verdict rules and the corrected gate-risk text.
- **From:** §2, §3, §8, §11, §13, §14 (O8), §15; freeze blockers B1.
- **Evidence:** the re-exported `docs/study/proposal_and_methods_v3.md` with its SHA-256; the Methods v2 edit commit.
- **Note:** neither file is governed today. Listing them in `--files` makes `status` track them from then on, so a later change shows CHANGED. That is useful for the LPC.PC.8 SHA-256, and it is the owner's choice.

```
python3 tools/ledger.py append --type amendment --actor "<owner name>" --role "human owner" \
  --authority "GOV.36; DEC-0008; DEC-0016; DEC-0025 D3; DEC-0026 item 8" \
  --summary "Amend proposal and methods v3 (re-exported) and Methods v2 per amendments note sections 2, 3, 8, 11, 13, 14 (O8), 15; v3 SHA-256 <sha256>" \
  --files docs/study/proposal_and_methods_v3.md docs/study/methods_experimental_procedures_v2.md \
  --data '{"source": "amendments note sections 2, 3, 8, 11, 13, 14, 15; freeze-blockers B1", "v3_sha256": "<sha256>"}'
```

### Rulings given 2026-10-11 to 2026-10-13

**L7. `ruling`: DEC-0008.**
- **Subject:** adopt every recommended ruling of the 2026-10-10 rulings document (A1 to A5, B, C, merge item 0), and confirm DEC-0003 to DEC-0007.
- **From:** DEC-0008; §1 to §6.
- **Evidence:** `decisions.md` DEC-0008; `docs/agent/notes/2026-10-10-rulings-for-owner.md`; `docs/agent/notes/2026-10-10-math-view-referral-rulings.md`.

```
python3 tools/ledger.py append --type ruling --actor "<owner name>" --role "human owner" --authority "PRIME.1; DEC-0008" \
  --summary "DEC-0008: every recommended ruling of the 2026-10-10 rulings document adopted (A1-A5, B, C, merge item 0); DEC-0003 to DEC-0007 confirmed" \
  --data '{"ruled_on": "2026-10-11", "quote": "I agree with and approve all recommendations. please proceed", "evidence": ["docs/agent/records/decisions.md#DEC-0008", "docs/agent/notes/2026-10-10-rulings-for-owner.md"], "executed": "merge develop into main 95ef937"}'
```

**L8. `ruling`: DEC-0015 (DEF-0014).**
- **Subject:** V7 is a plumbing check, judged at pilot size and above; smoke need not pass it.
- **From:** DEC-0015; §10.
- **Evidence:** DEC-0015; the `WU-0002.10-v7.md` Referral; `docs/study/dev_regression_dev0_vs_local_v1.md` (V7 passes at pilot size).
- **Owner choice:** state what "superseded" means, or leave it open.

```
python3 tools/ledger.py append --type ruling --actor "<owner name>" --role "human owner" --authority "DEC-0015; DEF-0014" \
  --summary "DEC-0015: V7 is plumbing only, judged at pilot size and above; smoke gate_pass false by design; V7 may be retired once superseded (<what supersedes it | open>)" \
  --data '{"ruled_on": "2026-10-11", "quote": "V7 is plumbing only and may be retired once superseded.", "evidence": ["docs/agent/records/decisions.md#DEC-0015"]}'
```

**L9. `ruling`: the DEV-0 pilot regression (DEC-0019, DEC-0020, DEC-0022, and the branch B result).**
- **Subject:** the fallback criterion, its four readings, the local v1 re-run as the new baseline, N1 kept, the platform record added, and the result accepted (branch B, 0 failures).
- **From:** §12; §13, last bullet; DEC-0019, DEC-0020, DEC-0022.
- **Evidence:**
  - `docs/study/dev_regression_dev0_vs_local_v1.md`;
  - `docs/study/pilot_results_v1_local_baseline.json`;
  - `WU-0002.12-pilot-regression.md`;
  - `WU-0001.6-platform-record.md`.

```
python3 tools/ledger.py append --type ruling --actor "<owner name>" --role "human owner" --authority "DEC-0019; DEC-0020; DEC-0022" \
  --summary "DEV-0 pilot regression: DEC-0019 criterion and DEC-0020 readings in force; local v1 re-run is the baseline; N1 kept; platform record added; branch B result (0 failures) accepted" \
  --data '{"ruled_on": "2026-10-11", "quotes": ["All 3 are approved", "Redo the v1 baseline and make that the new baseline. The old platform is not available. N1 I agree with the recommendation. Explain N3. Do 4, since this is our reference platform."], "open": "N3 licence scope (DEC-0022 item 3), unless covered by L22", "evidence": ["docs/study/dev_regression_dev0_vs_local_v1.md", "docs/agent/records/work/WU-0002.12-pilot-regression.md"]}'
```

**L10. `ruling`: the DEC-0026 ratification.**
- **Subject:** the owner ratified:
  - every written recommendation or default of DEC-0002 to DEC-0014, DEC-0016 to DEC-0021, DEC-0023, DEC-0024 (M1-M9 and A1) and DEC-0025;
  - Option C;
  - DEF-0017 and DEC-0017 Q1;
  - the WU-0002.11d conversions;
  - DEF-0019, DEF-0025 and DEF-0016;
  - WU-0002.11e OD1 to OD7;
  - the LM study instead of a convention;
  - the WU-0003 rehearsal as the next unit.
- **From:** DEC-0026; DEC-0024 A2 and its clarification.
- **Evidence:** `decisions.md` DEC-0026, DEC-0024 A2; `GATE-2026-10-11-develop-2.md`.

```
python3 tools/ledger.py append --type ruling --actor "<owner name>" --role "human owner" --authority "PRIME.1; DEC-0026" \
  --summary "DEC-0026: the written recommendations and defaults of DEC-0002-0014, 0016-0021, 0023, 0024 (M1-M9, A1), 0025 ratified; Option C (DEC-0018); DEF-0017 and DEC-0017 Q1; DEF-0019, DEF-0025, DEF-0016; WU-0002.11e OD1-OD7; LM doubling study; DEC-0024 A2 wording" \
  --data '{"ruled_on": "2026-10-12", "quote": "Ok good, please proceed with all recommendations, which are hereby ratified", "not_ratified_then": ["DEF-0018", "N3 licence scope", "DEC-0024 point 1 and 2", "main"], "evidence": ["docs/agent/records/decisions.md#DEC-0026", "docs/agent/records/work/GATE-2026-10-11-develop-2.md"]}'
```

**L11. `ruling`: DEC-0027 and the WU-0002.14 P1 result.**
- **Subject:** D3 uses both arms facing away; the triage order is adopted; a V4 failure is referred, never retuned; the redrawn-state P1 pilot is the new DEV-0 reference.
- **From:** DEC-0027; §15.
- **Evidence:**
  - `docs/study/dev_regression_p0_vs_baseline.md`;
  - `docs/study/dev_regression_p1_redrawn_states.md`;
  - `docs/study/pilot_results_v3_dev0_reference.json`;
  - `WU-0002.14-review-P1.md`.

```
python3 tools/ledger.py append --type ruling --actor "<owner name>" --role "human owner" --authority "DEC-0027; DEC-0019" \
  --summary "DEC-0027: D3 with both arms facing away, M5(a) triage order, V4 failure referred never retuned; WU-0002.14 P1 accepted (D2 exact, I1 33/33, R-f 30/30, D3 57/57, V1-V7 pass) and adopted as the DEV-0 reference" \
  --data '{"ruled_on": "2026-10-13", "quote": "O4 take the recommendation", "evidence": ["docs/study/dev_regression_p1_redrawn_states.md", "docs/study/pilot_results_v3_dev0_reference.json", "docs/agent/records/work/WU-0002.14-review-P1.md"]}'
```

### Rulings given 2026-10-17 and 2026-10-18 (DEC-0028 to DEC-0032)

**L12. `note`: R5 and R6 authorization (plan A4).**
- **Subject:** the owner authorized R5 (DEV-2 full, GPU, dump) and R6 (DEV-2 full, CPU, `LPC_THREADS=8`). Both ran on 2026-10-17.
- **From:** §26; freeze blockers B3 item 3.
- **Evidence:** `WU-0003-R1R2-R5-run-meta.json`; `WU-0003-R3R6-R6-run.meta.json`.

```
python3 tools/ledger.py append --type note --actor "<owner name>" --role "human owner" --authority "LPC.AUTH.3; WU-0003 plan amendment 1 A4" \
  --summary "R5 (full preset, DEV-2, GPU, states dump) and R6 (full preset, DEV-2, CPU, LPC_THREADS=8) authorized by the owner on 2026-10-17 and run that day (development runs)" \
  --data '{"ruled_on": "2026-10-17", "source": "amendments note section 26", "evidence": ["docs/agent/records/work/WU-0003-R1R2-R5-run-meta.json", "docs/agent/records/work/WU-0003-R3R6-R6-run.meta.json"]}'
```

**L13. `ruling`: the pre-run rehearsal rulings (DEC-0030 items 1, 3, 4).**
- **Subject:** OF-2 (equal contexts only); DEF-0026 (offline check only, no pre-seal response rule); OQ-R9 (diagnostic defaults fixed).
- **From:** §26.
- **Evidence:** DEC-0030; DEF-0026 status lines; `WU-0003-R0.md` (on `run/r0-e3b2645` only).

```
python3 tools/ledger.py append --type ruling --actor "<owner name>" --role "human owner" --authority "DEC-0030 items 1, 3, 4" \
  --summary "OF-2: V1 1e-12 rule for equal-context pairs only; DEF-0026: offline V6/V4 check only, no pre-seal response rule; OQ-R9: diagnostics seed 20261018, 1000 permutations, 2000 resamples are the pre-registered defaults" \
  --data '{"ruled_on": "2026-10-17", "source": "amendments note section 26", "evidence": ["docs/agent/records/decisions.md#DEC-0030", "docs/agent/records/defects.md#DEF-0026"]}'
```

**L14. `ruling`: the LM-doubling study (DEC-0030 items 5, 6).**
- **Subject:** O5 report-and-flag only (15 iterations stays); DEF-0028 amend the tool to the plan; the §30 readings as the owner confirms them.
- **From:** §29, §30.
- **Evidence:** `docs/study/lm_doubling_dev0_report_v3.md`; `WU-0005.6-rule-r-order-review.md`; DEF-0027, DEF-0028.

```
python3 tools/ledger.py append --type ruling --actor "<owner name>" --role "human owner" --authority "DEC-0030 items 5, 6; DEF-0027; DEF-0028" \
  --summary "LM iteration sensitivity: report and flag only (design value 15, no new reference run); DEF-0028: classify puts the structural switch before the X bullets (merged f14c8fa); section 30 readings <confirmed | ruled otherwise>" \
  --data '{"ruled_on": "2026-10-17", "source": "amendments note sections 29, 30", "evidence": ["docs/study/lm_doubling_dev0_report_v3.md", "docs/agent/records/work/WU-0005.6-rule-r-order-review.md"]}'
```

**L15. `ruling`: kappa_E and block length (DEC-0030 items 7, 8).**
- **Subject:** OF-R2 (the range governs); block length 5 for all systems; OF-3 (the pooled permutation reading governs D2); the report-only block-sensitive label; the WU-0003.8d judgement calls as the owner confirms them.
- **From:** §29, §31.
- **Evidence:** `docs/agent/notes/2026-10-17-math-block-length.md`; `docs/agent/notes/2026-10-14-math-wu0003-3a-kappa.md`; `WU-0003.8d-review.md`.

```
python3 tools/ledger.py append --type ruling --actor "<owner name>" --role "human owner" --authority "DEC-0030 items 7, 8" \
  --summary "kappa_E: pre-registered range [0.7071, 1] governs; block length 5 kept for all systems; OF-3: pooled permutation reading governs D2; report-only block-sensitive label; 8d judgement calls (b) exit code and (d) per part <confirmed | ...>" \
  --data '{"ruled_on": "2026-10-17", "source": "amendments note sections 29, 31", "evidence": ["docs/agent/notes/2026-10-17-math-block-length.md", "docs/agent/records/work/WU-0003.8d-review.md"]}'
```

**L16. `ruling`: the comparison-tool tolerances (DEC-0030 items 9 to 12 and 14).**
- **Subject:** OF-7 re-tag; OF-1 strict; O3 information only on T1 to T3; Q7 to Q9 and the handling-count scope strict; OF-5 away-arm failing rule; the RETAGS and `follows_k` readings as the owner confirms them.
- **From:** §17, §18, §33.
- **Evidence:** `tools/compare_runs.py` (RETAGS, `td_statistic`); `WU-0003.9c-review.md`; `WU-0003.9-review-round3.md`; `WU-0003-9c-compare-R1R3.txt`; `WU-0003-9c-compare-R5R6.txt`.

```
python3 tools/ledger.py append --type ruling --actor "<owner name>" --role "human owner" --authority "DEC-0030 items 9-12, 14" \
  --summary "compare_runs: OF-7 re-tag of the H1a fit leaves (ratio, ratio_ci <covered | cp 1e-12>; floor_rms <class g | class a>); OF-1 strict; O3 information only on T1-T3; Q7-Q9 and handling-count scope strict; follows_k <confirmed | ...>; OF-5 TD fails on |z_away| > 3.4" \
  --data '{"ruled_on": "2026-10-18", "source": "amendments note section 33", "evidence": ["docs/agent/records/work/WU-0003.9c-review.md", "docs/agent/records/work/WU-0003-9c-compare-R5R6.txt"]}'
```

**L17. `ruling`: the rehearsal-tool readings and OF-4 (DEC-0030 items 13, 15 to 17; D5; D6).**
- **Subject:** OF-F3 N = 24; OF-G3 margin band governs; F4 and Q6 kept as built (plan amendment 11; K2 as the owner says); the OF-4 correction (DEC-0024 A3).
- **From:** §33, §34 points 7, 8.
- **Evidence:** DEC-0024 A3; `WU-0003-dev-rehearsal.md` plan amendment 11; `docs/agent/notes/2026-10-14-math-wu0003.md` §M5.

```
python3 tools/ledger.py append --type ruling --actor "<owner name>" --role "human owner" --authority "DEC-0030 items 13, 15-17; DEC-0024 addendum A3" \
  --summary "OF-F3: N = 24 series; OF-G3: margin band governs H2a(ii) against v3; F4 and Q6 kept as built (plan amendment 11; K2 <covered | ...>); OF-4: F1 is indicative, not a worst case (DEC-0024 A3; budget.py text to change)" \
  --data '{"ruled_on": "2026-10-18", "source": "amendments note sections 33, 34", "evidence": ["docs/agent/records/decisions.md#DEC-0024", "docs/agent/notes/2026-10-18-owner-decision-drafts.md"]}'
```

**L18. `ruling`: WU-0003.6, the reproducibility tolerance (DEC-0028).**
- **Subject:** as D1.
- **From:** §29, §33; drafts §1.
- **Evidence:** as D1.

```
python3 tools/ledger.py append --type ruling --actor "<owner name>" --role "human owner" --authority "LPC.PC.18; DEC-0028" \
  --summary "WU-0003.6: reproducibility tolerance declared (DEC-0028): T0 bitwise; T1-T3 by the A6 tiers of compare_runs; TD by the away-arm TD statistic, bound 3.4; verdict-type leaves reported, not failed" \
  --data '{"ruled_on": "2026-10-18", "source": "amendments note sections 29, 33", "evidence": ["docs/agent/records/decisions.md#DEC-0028", "docs/agent/records/work/WU-0003-R3R6-compare-R5-R6.txt"]}'
```

**L19. `ruling`: WU-0003.6, the sample size (DEC-0029).**
- **Subject:** as D2.
- **From:** §29, §33; drafts §2.
- **Evidence:** as D2.

```
python3 tools/ledger.py append --type ruling --actor "<owner name>" --role "human owner" --authority "DEC-0029" \
  --summary "WU-0003.6: the confirmatory sample size stays the full preset (DEC-0029); no change to n, M or B" \
  --data '{"ruled_on": "2026-10-18", "source": "amendments note section 33", "evidence": ["docs/agent/records/decisions.md#DEC-0029", "docs/agent/records/work/WU-0003-R3R6-report-R6.txt"]}'
```

**L20. `ruling`: the confirmatory device (B4, DEC-0031).**
- **Subject:** as D4.
- **From:** §35, §36; freeze blockers B4.
- **Evidence:** as D4.

```
python3 tools/ledger.py append --type ruling --actor "<owner name>" --role "human owner" --authority "LPC.PC.8; DEC-0031" \
  --summary "Confirmatory device pre-declared (DEC-0031): one official sealed run on the CPU at LPC_THREADS=8; a GPU run of the same seed is a cross-check judged by the away-arm TD statistic, CPU verdict stands; the GPU run needs its own LPC.AUTH.6 authorization" \
  --data '{"ruled_on": "2026-10-18", "source": "amendments note sections 35, 36", "open": "rehearsal gate reading (DEC-0031 item 5); O3 (item 6)", "evidence": ["docs/agent/records/decisions.md#DEC-0031"]}'
```

**L21. `note`: intent to merge develop into main (B5, DEC-0032 item 1).**
- **Subject:** the merge to `main` comes after WU-0004.5 and a green full suite; the freeze lives on `main`; no request now.
- **From:** §35.
- **Evidence:** DEC-0032; `GATE-2026-10-18-develop.md`.
- **Note:** this records an intent, not an act. The merge itself is a later owner act.

```
python3 tools/ledger.py append --type note --actor "<owner name>" --role "human owner" --authority "LPC.PC.11; DEC-0032 item 1" \
  --summary "Intent: develop is merged into main after the owner's code review (WU-0004.5) and a green full suite at the freeze gate; the freeze commit and tag live on main; no main request now" \
  --data '{"ruled_on": "2026-10-18", "source": "amendments note section 35"}'
```

**L22. `ruling`: the freeze-blocker rulings B6 to B11 (DEC-0032 items 2 to 8).**
- **Subject:**
  - B6a and B6b: keep, and state as limitations;
  - B7: DEV-0 flags with the sqrt(n) projection, sealed row "not estimated" with a pointer;
  - B8: implement the dirty-tree and unknown-commit refusal;
  - B9: en-bloc ratification, with N2/N3 and OF-I1 ruled separately;
  - B10: the gpu test, and the ROADMAP row edited;
  - B11: dump off, and the freeze recorded as `classification` plus `commitment`.
- **From:** §35, §36.
- **Evidence:** DEC-0032; freeze blockers B6 to B11.
- **Owner choice:** split this into one entry per item if preferred. B9 is the largest, and it changes what the freeze package asserts.

```
python3 tools/ledger.py append --type ruling --actor "<owner name>" --role "human owner" --authority "DEC-0032 items 2-8; DEF-0018; DEF-0020" \
  --summary "Freeze blockers (DEC-0032): DEF-0020 and DEF-0018 kept and stated as limitations; LM row: DEV-0 flags quoted with projection, sealed row not estimated plus pointer; dirty-tree refusal to implement; B9 ratified en bloc <scope> (N2/N3 code reading; OF-I1 min anchor; amendment 1 O2-O4 overtaken); gpu test to write; sealed run dump off; freeze = classification plus commitment" \
  --data '{"ruled_on": "2026-10-18", "source": "amendments note sections 35, 36", "evidence": ["docs/agent/records/decisions.md#DEC-0032", "docs/agent/notes/2026-10-18-freeze-blockers.md"]}'
```

### Optional, then at the freeze

**L23. `waiver` (optional; B2 option 2 or 3).**
- **Subject:** a unit or file that the owner does not review before the freeze, with the reason.
- **From:** freeze blockers B2; WU-0004.1 ("or the owner waives it by ledger entry").
- **Evidence:** the review packet (`docs/agent/notes/2026-10-18-owner-review-packet.md`) and the independent reviews it lists.

```
python3 tools/ledger.py append --type waiver --actor "<owner name>" --role "human owner" --authority "LPC.PC.11; LPC.PC.6" \
  --summary "Owner review before freeze waived for <files or units>: <reason>; covered by the independent reviews <paths>" \
  --data '{"files": ["<path>"], "reviews": ["<path>"], "expires": "<date or event>"}'
```

**L24. `commitment` (WU-0004.6).**
- **Subject:** the confirmatory-seed commitment for CONF-1.
- **Note:** it is written by the owner's sealing step, not drafted here. Agents are barred from that path (LPC.PC.7; a hook refuses it). It must precede L25, which cites its `seq`.

**L25. `classification`: the freeze (LPC.PC.8; ruled as the freeze's type in §36, B11).**
- **Subject:** entry to CSQ2. It records the LPC.PC.8 fields.
- **From:** §36 (B11); freeze blockers B11 bullet 4; LPC.PC.5, LPC.PC.8.
- **Evidence:** the freeze checklist note (WU-0004.1); the audit (WU-0004.4); `requirements.lock`; the v3 export.

```
python3 tools/ledger.py append --type classification --actor "<owner name>" --role "human owner" \
  --authority "LPC.PC.5; LPC.PC.8; GOV.24; GOV.50; DEC-0032 item 8" \
  --summary "Freeze: the study enters CSQ2 at commit <hash> (tag freeze-1 on main); v3 SHA-256 <sha256>; configuration: full preset, CPU, LPC_THREADS=8, states dump off (DEC-0029, DEC-0031); dependency lock requirements.lock SHA-256 <sha256>; seed commitment entry <seq>" \
  --files requirements.lock docs/study/proposal_and_methods_v3.md \
  --data '{"commit": "<hash>", "tag": "freeze-1", "v3_sha256": "<sha256>", "configuration": {"preset": "full", "device": "cpu", "LPC_THREADS": 8, "states_dump": false, "platform": "<CPU model and BLAS kernel from the provenance block>"}, "dependency_lock_sha256": "<sha256>", "commitment_entry": "<seq>", "checklist": "<path of the WU-0004.1 note>", "audit": "<path of the WU-0004.4 audit>", "tolerance": "DEC-0028", "gpu_cross_check": "DEC-0031 item 2"}'
```

Two cautions for L25:
- `--files` makes `status` track `requirements.lock` and v3 from then on. Drop the flag if the owner prefers the hashes only in `data`.
- The platform belongs in the configuration because DEF-0023 and DEF-0024 make the last bits depend on the thread count and the BLAS kernel.

**L26. `note`: the governance reread at the freeze (WU-0004.8, LPC.PC.25).**
- **Subject:** which provisions were routinely waived, ignored or found ambiguous, and whether governance failed.
- **From:** freeze blockers B11 bullet 3; LPC.PC.25.
- **Evidence:** the reread note. Candidates that the records show:
  - the planner-free lane WU-0011.5 (DEC-0026 process note);
  - rulings acted on before their ledger entries (DEC-0009; this batch);
  - the process slip of §32;
  - entries 4 to 6 with a placeholder actor.

```
python3 tools/ledger.py append --type note --actor "<owner name>" --role "human owner" --authority "LPC.PC.25; GOV.46; GOV.47" \
  --summary "Governance reread at the freeze: <provisions routinely waived, ignored or ambiguous>; governance failed: <yes/no, how>" \
  --data '{"source": "<path of the reread note>"}'
```

---

## 4. Coverage: DEC-0008 to DEC-0027 and the §§26-36 rulings

| Record | Entry |
| --- | --- |
| DEC-0008 (and the confirmation of DEC-0003 to DEC-0007) | L7; blanks L1; note L2; C8 closed by L22 (B8) |
| DEC-0009 | L3 |
| DEC-0010 to DEC-0014, DEC-0016 to DEC-0018, DEC-0021, DEC-0023, DEC-0024 (with A1, A2), DEC-0025 | L10 (via DEC-0026); DEC-0023 and DEC-0024 A2 also B9 (L22) |
| DEC-0015 | L8 |
| DEC-0019, DEC-0020, DEC-0022 | L9 (DEC-0020 readings also in L10) |
| DEC-0026 | L10 |
| DEC-0027, WU-0002.14 P1 | L11 |
| §26 (OF-2, R5/R6, DEF-0026, OQ-R9) | L12, L13 (D3 items 1-4) |
| §29 to §31 (O5, DEF-0028, OF-R2, block length, OF-3, label) | L14, L15 (D3 items 5-8) |
| §33 (OF-7, OF-1, R5, Q7-Q9, handling, OF-4, OF-5, OF-F3, OF-G3, F4, Q6, WU-0003.6) | L16, L17, L18, L19 (D1, D2, D3 items 9-18, D5, D6) |
| §35 and §36 (B4 to B11) | L20, L21, L22 (D4, D7) |
| Freeze | L24, L25, L26 |

Totals:
- 26 ledger entries:
  - 18 owed now (L1 to L4, L7 to L22);
  - 2 after the B1 edits (L5, L6);
  - 1 optional (L23);
  - 3 at the freeze (L24 to L26), of which L24 is written by the owner's sealing step and not drafted here.
- 5 `decisions.md` entries (D1 to D4, D7) plus 1 addendum (D5).
- 1 plan amendment in a unit file (D6).
