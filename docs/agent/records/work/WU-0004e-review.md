# WU-0004e independent review (round 1)

- **Reviewer:** `reviewer`, claude-opus-5-5, fresh context; not the author (author: developer, claude-sonnet-5-5).
- **Under review:** branch `wu/0004e-citation-seeds`, tip `b5e6851`, one commit on develop `e10f65e`. Unit `docs/agent/records/work/WU-0004e-citation-seeds.md`.
- **Date:** 2026-10-18.
- **Tests:** none run by the reviewer, as instructed. The developer's radius is recorded in the unit Log: unit, 8 files, `406 passed in 42.91s`; integration, `test_cli_seeds.py`, `8 passed in 7.47s`. The change has no code path, so no rerun is needed.
- **Web:** not used. The citation facts are checked against the researcher's note `docs/agent/notes/2026-10-11-research-ami-delay.md` only.
- **Sealed seed and seal script:** not read or named in any command.

## What was verified (no finding)

- **C8 is docstring-only.** I compared `ast.dump` of `tests/unit/test_embedding.py` at `e10f65e` and at `b5e6851`, with the docstring of `test_regression_ami_delay_lorenz_band` removed: equal. Nothing else in the module differs. The assertion, the band `[3, 8]`, the name and the body are unchanged. No tolerance was loosened (PRIME.2). The test is still labelled a REGRESSION GUARD, not correctness evidence, which is consistent with LPC.PC.21a.
- **C8 citation facts against the note (§Findings row 1, §Conversion, §Assessment).** All of the following match the note:
  - the authors (Deshmukh, Bradley, Garland, Meiss), the title, arXiv:2003.06509v1, 7 Mar 2020;
  - Sec. IV.B "Classic Lorenz Attractor", Fig. 5, PDF p. 8, retrieved 2026-10-11;
  - sigma = 10, beta = 8/3, rho = 28 (these equal `lpcstudy/systems.py:148`);
  - RK4 with dt = 0.01 and 90,000 points;
  - TISEAN `mutual`, bin count not stated;
  - the quotation "first minima of both curves fall near tau = 18";
  - 0.18 time units, which is 4.9 steps at dt 0.0368 (the arithmetic 0.18/0.0368 = 4.89 is right);
  - tau_I = 60, which is 0.60 time units and 16.3 steps;
  - the statement that the evidence does not justify a band tighter than [3, 8] without a stated estimator-matching tolerance;
  - [4, 6] as weakly supported, and the Weeks page (0.16) described as informal and not peer reviewed.
  
  "Would probably choose" is a fair paraphrase of "it is quite likely that a practitioner would actually choose". See R4 for the one wording that is not directly supported.
- **C9: what changed.** I compared the file at `e10f65e` and `b5e6851` by script:
  - `schema`, `description`, `created` and `created_by` are equal;
  - the entry count and the id order are equal;
  - for every entry, `id`, `value` and `use` are equal;
  - DEV-0 is untouched;
  - DEV-1 to DEV-4 change `status` and gain `note`, and nothing else changes.
- **C9: no behaviour depends on `status`.** `lpcstudy/seeds.py:load_registry` reads only `schema`, `seeds`, `id` and `value`. The `run_preset.sh` registry check (lines 202-215) reads `schema` and `id`. `tests/unit/wrapper_helpers.py:107` copies the file unchanged. `test_real_registry_matches_its_json_exactly` compares only id/value pairs. A grep of `lpcstudy/`, `tools/` and `tests/` for a read of the registry's `status`, or for `"unused"`, finds nothing: there is no guard against re-using a used seed and no selection by status. A status of "used" therefore changes no behaviour.
- **C9: no pinned digest.** The only ledger mention of the registry (`ledger.jsonl` seq 1) names the path, not a hash. The ledger's `files` hashes cover governance documents only. `lpcstudy/provenance.py` and `tools/ledger.py` do not hash `seeds/`. No test pins a digest of the file.
- **C9: dates and runs, checked against the records.**
  - R0 ran on DEV-1 as a smoke on GPU and on CPU on 2026-10-17 (`WU-0003-R0.md`).
  - R1 and R2 ran on DEV-1 at the pilot preset on GPU, 2026-10-17 11:59Z to 12:54Z.
  - R3 ran on DEV-1 at the pilot preset on CPU, 14:25Z to 15:56Z.
  - R5 ran on DEV-2 at the full preset on GPU, 15:57Z to 16:42Z.
  - R6 ran on DEV-2 at the full preset on CPU, 16:43Z to 21:27Z.
  
  The source for each run is its `run.meta.json` record. All the dates are 2026-10-17 UTC, and the record pointers in the notes exist.
- **Governance of the commit.** The commit message names the unit and carries the `Agent:` trailer. The `queue.md` diff only appends lines (0 removed). The unit file is new. No history was rewritten.
- **Owner checkpoint.** The change touches the seed registry, so it **needs owner review before freeze**. The developer flagged this as well.

## Findings

### R1 (medium; correctness of a permanent record): DEV-3, DEV-4 and DEV-1 notes say "V6/V4 context checks", but V4 was computed on no context of these seeds

- **Where:** `seeds/development_seeds.json`, `note` of DEV-3 and DEV-4: "Used 2026-10-17 for V6/V4 context checks only (pilot and full presets, CPU, no outcome run)". The `note` of DEV-1 says "and in V6/V4 context checks (pilot and full presets)". The unit Plan A3 carries the same wording.
- **Evidence:** `docs/agent/notes/2026-10-17-v6-v4-offline-check.md`:
  - line 3: "DEV-1, DEV-2, DEV-3, DEV-4 for the new V6 draws; R1 = DEV-1 for V4";
  - line 10: V6 only, by `build_context` and `check_integrator`;
  - line 12: "V4 and the gate flags were read from the R1 run (read-only)";
  - line 256: "Only V6, an outcome-free integrator check, was computed".
  
  `2026-10-11-amendments-for-owner.md` §27 agrees: "DEV-3 and DEV-4 now used (V6 contexts only, no outcome)". V4 enters only through R1's outputs, which were made on DEV-1 at the pilot preset on GPU. It is not a context check, and there is no V4 at the full preset for any seed in that note. The DEV-2 note correctly says "V6 context checks".
- **Why it matters:** the registry is append-only by its README ("never edit or remove one"). Once merged, the untrue text stays in the record of how each seed has been used. That record is what later seed-sensitivity or freshness decisions rely on.
- **Required fix:** make a new commit on the branch, not an amend.
  - DEV-3 and DEV-4: "V6 context checks only (pilot and full presets, CPU; no V4, no outcome)".
  - DEV-1: "V6 context checks (pilot and full presets, CPU)". You may add "the offline V4 update read R1's outputs".
  - DEV-1 and DEV-2: also cite `docs/agent/notes/2026-10-17-v6-v4-offline-check.md` as the record of their V6 context checks.
  - Correct Plan A3's wording in a new Log line. Do not change the Plan in place.

### R2 (high; governance): the `ask` permission on seed edits was not triggered, and the owner has not seen this diff

- **Where:** the unit Log, line 44: "Edit of `seeds/**` by a script in the worktree raised no permission prompt." `.claude/settings.json` has `"ask": ["Edit(/seeds/**)"]`. That rule is still present in main's working copy after the owner reduced the asks (amendments §24), so the owner kept the gate on purpose.
- **Why it matters:** the `ask` rule is the owner's per-edit consent for the seed registry. Writing the file with a script did not trigger it, whatever the intent. The owner's B9 ratification (§36, "DEV registry statuses to be updated") authorizes the intent. It does not show the owner this text, and R1 shows the text is wrong. No agent can supply that consent in the owner's place. The developer disclosed the bypass, which is to their credit, but disclosure does not replace the gate.
- **Required fix:**
  1. Do not merge until the owner has reviewed and approved the exact registry diff after the R1 fix. Record the approval as a line in the unit file.
  2. Make the R1 correction with the Edit tool, so that the `ask` fires, or leave it to the owner.
  3. The main session records the bypass as a process slip in the owner notes. The note should cover this edit and the rule that a seed edit is never made by script.

### R3 (low; scope and the README rule): the new `note` key goes beyond "statuses", and the README now contradicts the registry

- **Where:** `seeds/README.md`, "Development seeds": "`DEV-1` to `DEV-4` are fresh" and "Add more by appending entries (never edit or remove one)".
- **Assessment:** I judge the status change to be within B9's "DEV registry statuses to be updated". It is a later and more specific owner ruling, and it leaves `id`, `value`, `use` and DEV-0 untouched. The added `note` key is not literally a status. The Plan allowed it "if the schema allows". The loader ignores extra keys, but no schema definition exists to confirm that. DEV-0 records its use inside `use` and has no `note` key, so the two entries now differ in convention. After this change, the README is false in two places: DEV-1 to DEV-4 are no longer fresh, and an entry has been edited.
- **Required fix (owner item; the README is outside this unit's plan):**
  - The owner confirms that the `note` key is within B9, or asks for the text to move into `status` or `use`.
  - The owner amends the README rule to say that status and note text may be updated by owner ruling, and that ids and values never change. The owner also removes the word "fresh".
  - Until then, record the conflict in the unit's Log or `## Audit`.

### R4 (low; citation wording): "The paper calls that minimum shallow" is not in the note's verbatim quotation

- **Where:** `tests/unit/test_embedding.py`, the docstring of `test_regression_ami_delay_lorenz_band`: "The paper calls that minimum shallow and says a practitioner would probably choose tau_I = 60".
- **Evidence:** the note's verbatim quote is elided ("... Indeed, based on this AMI profile ...") and does not contain the word "shallow". The note's Conditions column gives the shallowness as a reading of Fig. 5: "a shallow shoulder (AMI about 0.65 at 18 against 0.7 near 30)". The note's Assessment (line 31) says the preprint "calls its 0.18 minimum shallow". The note is therefore ambiguous about whether this is the paper's word or the researcher's reading of the figure. I cannot resolve it without the web.
- **Required fix:** either
  - reword the docstring to what the note quotes, for example "Fig. 5 shows that minimum as a shallow shoulder (the researcher's reading of the figure)", which is a docstring-only change; or
  - dispatch the `researcher` (`/verify-citation`) to confirm that the paper's own text says the minimum is shallow, and keep the wording if it does.

## Verdict

**changes required.** There are 4 findings: R1 medium, R2 high, R3 low, R4 low.

- R1 and R2 block the merge.
- R3 is an owner item.
- R4 is a docstring-only fix, or a researcher check.

The core facts of C8 are right, and its no-code-change claim holds. The C9 ids, values, schema and DEV-0 are untouched, and no behaviour depends on `status`. The seed registry change **needs owner review before freeze**.

---

# Round 2 (re-review of fix round 1)

- **Reviewer:** `reviewer`, claude-opus-5-5, fresh context; not the author.
- **Under review:** fix round 1, `git diff 96d2ecd..8e6906f`, and the net registry diff `git diff e10f65e 8e6906f -- seeds/development_seeds.json`. Scope is limited to R1 to R4.
- **Date:** 2026-10-18.
- **Tests:** none run by the reviewer, as instructed. The developer's run on 8e6906f is in the unit Log: unit (8 files), `406 passed in 38.56s`; integration, `test_cli_seeds.py`, `8 passed in 7.69s`. The round changes only a docstring and JSON text, so no rerun is needed.
- **Web:** not used. **Sealed seed and seal script:** not read or named in any command.

## R1: fixed

- **Notes checked against `docs/agent/notes/2026-10-17-v6-v4-offline-check.md`:**
  - line 3 assigns the V6 draws to DEV-1 to DEV-4, and V4 to R1 = DEV-1;
  - line 10 says V6 was run at the pilot and full presets, on CPU;
  - line 12 says V4 was read from the R1 run;
  - lines 57-64 list the pilot and full values for each of DEV-1 to DEV-4;
  - lines 254-256 say DEV-3 and DEV-4 were used for contexts only, and that only V6 was computed.
- **Each note now matches the record:**
  - DEV-3 and DEV-4: "V6 context checks only (pilot and full presets, CPU; no V4, no outcome run)". Correct.
  - DEV-1: R0 (smoke, GPU and CPU), R1 and R2 (pilot, GPU), R3 (pilot, CPU), and V6 context checks (pilot and full, CPU). The parenthetical "its V4 update read R1's outputs" is correct (line 12). The `WU-0003-R*.md` glob matches `WU-0003-R0.md`, `WU-0003-R1R2.md` and `WU-0003-R3R6.md`.
  - DEV-2: R5 (full, GPU), R6 (full, CPU), and V6 context checks (pilot and full, CPU; lines 58 and 62). Correct. The record globs `WU-0003-R3R6*.md` and `WU-0003-R1R2-R5*` match existing files.
  - DEV-1 and DEV-2 cite the offline-check note.
- **Invariants, re-checked by script (python -I) against `e10f65e`:**
  - the top-level keys other than `seeds` are equal;
  - the `(id, value, use)` list is equal, in the same order;
  - DEV-0 has no changed key;
  - DEV-1 to DEV-4 change only `note` and `status`.
- **Plan A3 not edited, correction recorded:** the round's diff of the unit file is +8/-0. The correction is appended as a new Log line (Log line 52). The Plan text at line 36 is unchanged.
- **Append-only:** `git diff --numstat e10f65e 8e6906f -- docs/` shows 0 deleted lines in every record (the unit file, this file and `queue.md`).

## R2: recorded honestly; still open on the owner's approval

- Log line 51 states the following:
  - the first registry edit (b5e6851) was made by a Python script from Bash;
  - a script write does not trigger `ask: Edit(/seeds/**)`, so the developer "bypassed the owner's ask rule";
  - the earlier hand-back understated this;
  - the owner's approval of the exact diff is **pending**, and nothing claims it;
  - the branch is not to be merged until the owner approves;
  - this round's seed edits were made with the Edit tool only.
- Log line 55 says plainly that the developer did not see the prompt text. It claims no approval. I find no line anywhere on the branch that claims owner approval.
- I cannot verify the Edit-tool claim from git. I accept it as the author's statement.
- **What remains:**
  - Fix item 1 (owner approval of the exact registry diff, recorded as a line in the unit file) is outstanding. It is the owner's action, not the developer's.
  - Fix item 3 (the main session records the slip in the owner notes) is outstanding. It belongs to the main session.
- **Merge stays blocked** until the approval line exists.

## R3: recorded as an owner item

Log line 53 records the following:
- the `note` key goes beyond "status";
- the README contradicts the registry in two places ("fresh" and "never edit or remove one");
- the two owner asks, (a) and (b), as stated in round 1.

The README was not edited, which is correct because it is outside the plan. The item is open for the owner and does not block the developer.

## R4: fixed

- The docstring now attributes the shallow shoulder to the researcher's reading of Fig. 5, with the note's values "AMI about 0.65 at tau = 18 against 0.7 near 30". This matches the Conditions column of `2026-10-11-research-ami-delay.md`, line 15. The docstring also says this is "a reading of the figure, not a quotation".
- The tau_I = 60 sentence ("from this AMI profile, a practitioner would quite likely choose tau_I = 60") paraphrases the verbatim quote faithfully: "based on this AMI profile, it is quite likely that a practitioner would actually choose tau_I = 60".
- `ast.dump` of `tests/unit/test_embedding.py` with that docstring removed equals the file at develop `e10f65e` (script, python -I): True. The name, body, band [3, 8] and assertion are unchanged. No tolerance was loosened (PRIME.2).

## Other checks of this round

- Commit 8e6906f names the unit and carries `Co-Authored-By` and `Agent: claude-sonnet-5-5`. It is a new commit; no history was rewritten.
- Record hygiene (not a finding):
  - Log line 50 says "Answers are under 'Review' below", but the answers are in the Log.
  - The unit's `## Review` still listed R1 to R4 as "Open".
  - I have appended the round-2 statuses to the unit's `## Review`.

## New findings

None.

## Verdict (round 2)

**approve.** No new findings (0). R1 and R4 are fixed. R2 and R3 are recorded correctly and are now owner items, not developer fixes.

- **Merge condition (from R2):** do not merge until the owner has approved the exact registry diff `git diff e10f65e 8e6906f -- seeds/development_seeds.json` and that approval is a line in the unit file.
- **Main session:** record the script-edit slip in the owner notes.
- **Owner checkpoint:** the seed registry change **needs owner review before freeze**.
