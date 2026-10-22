# Promotion proposal (WU-0018.2) for CONF-1 — DRAFT for the owner; not a ledger entry

- **Author:** claude-sonnet-5-5 (developer), 2026-10-22, on develop. This is the text of the proposal. The ledger is the owner's to append (the command is below and is **not run**). Nothing here promotes anything.
- **Status words:** every result in this note is PRELIMINARY and the run is `CONFIRMATORY: UNPROMOTED` until the owner's promotion entry exists. "Supported" is written "supported (preliminary, unpromoted)", as in the findings document.
- **Sources read for this note:** the findings document `docs/agent/notes/2026-10-20-prelim-findings-conf1.md` (line numbers below are lines of that file at the develop tip that holds this note; its `check` gives `check passed: 1266 traced values, 0 problems`), the audits `docs/agent/notes/2026-10-21-audit-pre-promotion-conf1.md` and `docs/agent/notes/2026-10-22-audit-promotion-conf1.md`, the ledger (36 entries, chain intact), `docs/agent/records/results-manifest.md`, the unit files WU-0015 to WU-0018.

## 1. The promoted set (answers audit major M-A)

The audit asks the proposal to name the promoted artifact and where each ruled sentence lives. Proposed set, two parts:

| Part | Files (paths relative to the repository root) | Hashes (sha256) | What it is |
|---|---|---|---|
| A. Sealed output of the official run (run-1, CPU) | `runs/confirmatory/run-1/full/results.json`; `runs/confirmatory/run-1/full/RESULTS.md`; `runs/confirmatory/run-1/full/figures/` (`kaplan_meier_by_rule.png`, `knob_response_library.png`, `regret_vs_regimes.png`, `separation_weight_vs_horizon.png`); `runs/confirmatory/run-1/full/run.log` | `results.json` `ae4b0fe5bf488f6c147bce6c91a2398e87408f6a5d372ae66d89bdfc90b0cebe`; `RESULTS.md` `2a4c1d06859d07584b1633c6e7f1b5df205ffe445402509834383fb474649577`; sidecar `runs/confirmatory/run-1.sha256` | The v3 report of WU-0017.1 as the frozen code writes it. Not edited. |
| B. Report text | `docs/agent/notes/2026-10-20-prelim-findings-conf1.md` with `.trace.csv`, `.sources.json`, `.compare.txt` and `.figures/` (F1, F2, F3) | document `98389556be3aa983f2d87782773ae3b54217940a37a3794a433232cedbbace01`; trace `99016cb9e6688684018109f54f52639fa418ed8fb087f34cf7322e3f9672ce1e`; sources `f93399ba27c3c0989adc0328a4e30802f7b41135d3f19196cb49b29cb51f5809` (hashes before any commit message edit; recompute at the entry) | The narrative report. Carries the limitations (section 10), the interval labels (appendix B), the figure map and the ruled sentences, which `RESULTS.md` cannot carry (it is sealed output). |

Not promoted: the GPU cross-check files (`runs/confirmatory/run-1-gpu/`, `run-1-compare.txt`; information only, DEC-0031), the regeneration run-2 files (evidence, T0), the development appendix (empty).

Manifest row: `docs/agent/records/results-manifest.md` line 29 (run-1, run-1-gpu, comparison; "Status: unpromoted; hypothesis-test result") and line 30 (run-2 and its comparison). The promotion adds a new dated manifest line naming the promotion entry; it does not edit these (append-only).

## 2. Result words (from section 4 of the findings document only)

Decision rule v3 §7: supported if pass on all three systems, not supported if fail on at least one, inconclusive otherwise. Lines are the table rows of section 4 (lines 94 onward).

| Hypothesis | Role | lorenz63 | rossler | chua | Overall |
|---|---|---|---|---|---|
| H1a | secondary | pass | pass | inconclusive | inconclusive |
| H1b | secondary | inconclusive | fail | pass | not supported |
| H1c | secondary | fail | pass | inconclusive | not supported |
| H1d | secondary | pass | pass | inconclusive | inconclusive |
| Q-N | estimate | logit: reduces; indicator: substantial | logit: reduces; indicator: substantial | logit: reduces; indicator: substantial | estimate (read, no pass/fail); the stored per-system words are the logit part only |
| H2a | primary | fail | fail | fail | not supported |
| H2b | primary | pass | pass | pass | supported (preliminary, unpromoted) |
| H2c | secondary | inconclusive | inconclusive | pass | inconclusive |
| H2d | secondary | inconclusive | pass | pass | inconclusive |
| H2e | secondary | pass | pass | pass | supported (preliminary, unpromoted) |
| gain bound | reported | reported | reported | reported | reported (no pass/fail) |
| H3a | secondary | inconclusive | inconclusive | inconclusive | inconclusive |
| H3b | secondary | fail | pass | inconclusive | not supported |
| H3c | primary | inconclusive | pass | inconclusive | inconclusive |

Primaries: H2a not supported, H2b supported (preliminary, unpromoted), H3c inconclusive.

## 3. Evidence

- **Manifest and hashes:** as in section 1; the three hashes equal the manifest, the sidecars and `sources.json` (audit 2026-10-21 item 1; audit 2026-10-22 item 1).
- **Regeneration (run-2):** `runs/confirmatory/run-2-compare.txt` (sha256 `11007a4e1d169946f431a447018b92f94705352700c10d1eb155c6006b646df5`): tier T0; REF 20766, NEW 20766, common 20766, equal 20766, different 0, one-sided 0; provenance (147) and timing (23) leaves excluded on both sides; RESULT PASS. Claim: every compared leaf equal, not "the files are identical". Run-2 files: `runs/confirmatory/run-2/full/` (`results.json` `08f3de8f7491b7fd632d2ae87f7b9f04fb0773598c70dd00c9cc9f0ff3b9f2f9`, `RESULTS.md` `e382b1110107ce1f83aa4a8d2a6c5939d096af42fc209c1850319511710c497b`).
- **Report-only regeneration (WU-0017.1):** twice by the developer and once more by the 2026-10-22 audit, from the freeze worktree: `RESULTS.md` `2a4c1d06…4577` each time, `results.json` unchanged, four figures byte-equal (`WU-0017-v3-report.md`).
- **GPU cross-check, information only:** `runs/confirmatory/run-1-compare.txt`: tier TD, 18 of 18 parts, max z (away) 2.21 against the bound 3.4, 0 failing, PASS. The stored verdict words that differ between the CPU and GPU files are listed in section 8 of the findings document; the CPU words stand (DEC-0031).
- **Both audits:** `docs/agent/notes/2026-10-21-audit-pre-promotion-conf1.md` (findings document sound; NO-GO until B1 and M1 to M4 closed) and `docs/agent/notes/2026-10-22-audit-promotion-conf1.md` (zero blockers; GO for this proposal; majors M-A to M-D before the transaction; 13 of 13 sampled numbers; 14 of 14 overall and 24 of 24 primary words recomputed).

## 4. Where each ruled sentence stands in the report text (answers M-A)

All in the findings document (part B), at the lines shown.

| Ruled item | Ledger | Sentence in the report | File and line |
|---|---|---|---|
| Same host and actor (audit M3) | waiver seq 31 (scope CONF-1 only), ruling seq 34 | "Run-2 (WU-0016) shows determinism, not an independent reproduction. The compared leaves are bitwise equal, and the same host, environment and actor produced both runs (DEC-0035). … waived … (ledger seq 31) … agent-based cross-checking … (ledger seq 34)." With DEF-0023 and DEF-0024 named | `2026-10-20-prelim-findings-conf1.md` line 516; constant `same_host_limit` |
| Verification and validation status (audit M1) | waiver seq 33 | "owner code review waived (ledger seq 33); results spot-checked by the owner; code covered by independent agent reviews. DEF-0001 stays open until the owner closes it." | same file, line 517; constant `vv_status_limit` |
| DEF-0022 power finding (audit M4) | ruling seq 32 (DEC-0041) | accepted as a known limitation; the projected margin is not reproduced at full size, labeled development evidence, not a result of this run | same file, line 515; constant `def0022_proposed` |
| NVVUQ.22 gaps G1 to G3 | ruling seq 36 (DEC-0042 item 4) | no numerical-error estimate and no per-QoI V&V status for the nine secondary or reported rows; status wording of the secondaries | same file, line 518; constant `nvvuq_gaps_limit` |
| Figure map and caption note | ruling seq 36 | the four captions name no experiment or identifier; the map is given; the dotted line of `regret_vs_regimes.png` is a reference line drawn at 5.0 by the code, not a pre-registered criterion | same file, line 519; constant `figure_map_limit`; map in `docs/agent/notes/2026-10-21-promotion-figure-map.md` |
| Q-N two readings | DEC-0036 (seq 24) | both readings shown; the stored overall word is the logit part only | same file, line 117 (section 4) and the Q-N rows of the section 4 table |
| DEF-0027 iterative error | owner answers O5, B7 (DEC-0024) | the iterative error of the fixed 15-iteration Levenberg–Marquardt budget is not estimated for this run; the development study is labeled development evidence | same file, line 506 |
| GPU cross-check as information only | DEC-0031 (v3 §9 item 3) | "The GPU run of the same seed is a cross-check, never the result" | same file, section 8, lines 385 to 387 |

`RESULTS.md` (part A) carries none of the first five sentences (it is the sealed output of the frozen code). They live in part B, and the transaction entry should name both parts.

## 5. Ruled deviations

- ROADMAP WU-0017.1 acceptance (six NVVUQ.22 items for every reported QoI) and WU-0017.2 acceptance (every caption names its experiment and v3 identifier) are **met only with the exceptions of ledger seq 36**: gaps G1 to G3 and the four sealed captions, with the figure map carried in the report text (DEC-0042 item 4; the owner's quote concerns future runs, and the reading is "for the owner to correct", audit m-1).
- The independent-actor requirement of v3 §9 item 4 and LPC.PC.6 is waived for CONF-1 (seq 31) and the owner code review is waived (seq 33).
- The authorization of the official run was entered after the run and is accepted by the owner (seq 15 and ruling seq 30).

## 6. Pending items (not mine to close)

1. **WU-0017.3: owner and student read the report. Pending.** The transaction depends on it (audit M-C). It is recorded as a dated line in `docs/agent/records/work/WU-0017-v3-report.md`; the student's interpretations, if any, as notes.
2. **Form of the waivers (audit M-B).** Seq 31 and seq 33 lack the risk accepted and an expiry condition (GOV.44, QA.10). A note by the owner is proposed. Draft: "Waivers seq 31 and seq 33: the risk accepted is an error in the verdict, statistics, seed or provenance code that agent review did not catch, and non-independence of the regeneration from host, environment and operator. They apply to the promotion of CONF-1 only and expire when the owner's code review is recorded or at the end-of-project governance review (WU-0019.2), whichever is first." The owner edits as wished.
3. **Ledger sync (audit M-D, second half).** Entries 32 to 36 are committed on develop (3d1a7f3); main's ledger stops at 28. The proposal and promotion entries go on this chain and main is synced after the transaction.
4. **Label removal on copies (WU-0033, `promote`).** The promoted copy of the findings document is produced by `findings_build.py promote` (branch `wu/promoted-copy`, to be reviewed and merged first): it removes only the listed labels and checks the difference. It cannot pass `check` (which refuses an edited document); the machine check of `promote` replaces it. What `promote` does not do, and the owner decides, is in section 9.
5. Open owner items from the audits that do not block: seq 36 reading (m-1), m8 (v3 §9 item numbering, frozen).

## 7. The ledger `proposal` command (draft, **not run**)

To be run by the owner from the repository root once the items in section 6 that the owner wishes to settle are settled. The actor and role words are placeholders for the owner to set. `--files` hashes the named governed files into the entry.

```
python3 tools/ledger.py append --type proposal \
  --actor "Brian J. McDermott" --role "human owner" \
  --authority "LPC.PC.13; ROADMAP WU-0018.2" \
  --summary "WU-0018.2: proposal to promote the CONF-1 result (run-1 official CPU files and the findings document as report text); regeneration run-2 T0 20766 of 20766 equal; two audits; waivers seq 31 and 33; rulings seq 30, 32, 34, 36" \
  --files docs/agent/notes/2026-10-22-promotion-proposal.md docs/agent/notes/2026-10-20-prelim-findings-conf1.md runs/confirmatory/run-1/full/results.json runs/confirmatory/run-1/full/RESULTS.md runs/confirmatory/run-2-compare.txt docs/agent/records/results-manifest.md \
  --data '{"seed_id":"CONF-1","manifest":"docs/agent/records/results-manifest.md lines 29 and 30","results_sha256":"ae4b0fe5bf488f6c147bce6c91a2398e87408f6a5d372ae66d89bdfc90b0cebe","results_md_sha256":"2a4c1d06859d07584b1633c6e7f1b5df205ffe445402509834383fb474649577","regeneration_compare_sha256":"11007a4e1d169946f431a447018b92f94705352700c10d1eb155c6006b646df5","audits":["docs/agent/notes/2026-10-21-audit-pre-promotion-conf1.md","docs/agent/notes/2026-10-22-audit-promotion-conf1.md"],"waivers":[31,33],"rulings":[30,32,34,36],"promoted":false}'
python3 tools/ledger.py verify
```

`--files` behavior (tested 2026-10-22 on a temporary copy of the tool and of the ledger, not on the real ledger): the tool accepts any existing file, governed instrument or not (run outputs, the findings document, the manifest), given relative to the repository root (an absolute path is also accepted); it stores each name as typed with its sha256 in the entry's `files` object, so the hashes of the sealed run files are recorded in the entry itself; a name that does not exist stops the command with "governed file not found" and no entry is written. Two side effects: `ledger.py verify` checks only the chain and does not re-hash these files; and `ledger.py status` lists every file named in a `proposal` entry as "proposed (entry n), NOT ADOPTED" (cosmetic noise, because the proposal files are not instruments); a `promotion` entry's files are not listed by `status`. The `--files` list above therefore also records the hashes of `results.json`, `RESULTS.md`, `run-2-compare.txt`, the manifest and the findings document at the time of the proposal; recompute them at the entry. In the promotion command of section 8, add the same run files to `--files` if the owner wants their hashes inside the promotion entry.

(If the proposal is to be entered as an agent's, the actor is the agent with its model id and the owner still runs the command, as the ledger is owner-only.)

## 8. WU-0018.3 promotion transaction — sketch, FOR THE OWNER, AFTER WU-0017.3

Not to be run before the reading is recorded (section 6 item 1) and the waiver note exists (item 2). The entry numbers `<P>` (proposal) and `<N>` (promotion) are read from the ledger.

```
# 0. preconditions
python3 tools/ledger.py verify && python3 tools/ledger.py status
python3 tools/findings_build.py check docs/agent/notes --stem 2026-10-20-prelim-findings-conf1   # must print 0 problems
sha256sum runs/confirmatory/run-1/full/results.json runs/confirmatory/run-1/full/RESULTS.md        # must equal the hashes in section 1

# 1. promotion ledger entry (owner); N is the new seq
python3 tools/ledger.py append --type promotion \
  --actor "Brian J. McDermott" --role "human owner" \
  --authority "LPC.PC.13; QA.11; ROADMAP WU-0018.3" \
  --summary "Promotion of the CONF-1 result: run-1 official CPU files and the findings document as report text, with the ruled limitations" \
  --files docs/agent/notes/2026-10-20-prelim-findings-conf1.md \
  --data '{"seed_id":"CONF-1","proposal_seq":<P>,"results_sha256":"ae4b0fe5bf488f6c147bce6c91a2398e87408f6a5d372ae66d89bdfc90b0cebe","results_md_sha256":"2a4c1d06859d07584b1633c6e7f1b5df205ffe445402509834383fb474649577","reading_recorded":"WU-0017.3 dated line","promoted":true}'

# 2. manifest: append a new dated line (the file is append-only); it names entry N and the hashes of the promoted copies
#    "- <date>, <owner> (WU-0018.3): CONF-1 run-1 PROMOTED by ledger entry <N>; Status: promoted."

# 3. promoted copies; the labels are removed on the COPIES only, the originals stay as they are
#    precondition: WU-0033 (branch wu/promoted-copy) is reviewed and merged to develop, so that `promote` exists
mkdir -p promoted/CONF-1
cp -r runs/confirmatory/run-1/full/figures promoted/CONF-1/figures
cp runs/confirmatory/run-1/full/results.json promoted/CONF-1/results.json
cp runs/confirmatory/run-1/full/RESULTS.md promoted/CONF-1/RESULTS.md
python3 tools/findings_build.py promote --document docs/agent/notes/2026-10-20-prelim-findings-conf1.md --out promoted/CONF-1/report.md
#    (writes only the new file, checks the difference on the bytes read back, and deletes the file with exit 1 if anything but the listed labels differs)
#    RESULTS.md copy: remove its header label by hand on the COPY: line 3 `**CONFIRMATORY: UNPROMOTED**` and the blank line 4 after it
sed -i '3,4d' promoted/CONF-1/RESULTS.md
diff runs/confirmatory/run-1/full/RESULTS.md promoted/CONF-1/RESULTS.md    # must print exactly: 3,4d2 and the two deleted lines, nothing else
grep -n -i "unpromoted\|promoted" promoted/CONF-1/RESULTS.md              # must show only the two stored provenance cells (label, promoted false)
#    the owner's decision on the findings figures F1 to F3 is in section 9 below; do this step after it
find promoted/CONF-1 -type f | sort | xargs sha256sum    # record in the manifest line (includes the files inside figures/)

# 4. verify and sync
python3 tools/ledger.py verify
#    sync main as for entries 1 to 28 (commit 83520cc): the owner merges develop into main; main only when fully green (owner authorizes)
```

The sketch is a sketch: the folder name `promoted/` and the form of the label removal are proposals, not an adopted procedure.

## 9. Owner decision: the findings figures and what the promoted copy still says (new, 2026-10-22)

Facts (checked on the files):

- The findings document embeds three images, F1, F2, F3 (document lines 158, 332, 480: `2026-10-20-prelim-findings-conf1.figures/F1_primary.png`, `F2_secondary.png`, `F3_crosscheck.png`). They are drawn by `tools/findings_build.py` with a title that reads "CONFIRMATORY: UNPROMOTED / PRELIMINARY: internal to the owner and the student until promotion (QA.11, LPC.PC.13)." (`status_title`). `promote` does not touch them. The four figures of the official `RESULTS.md` carry no status text (their captions are in the text) and can be copied as they are.
- In the promoted copy the image links of F1 to F3 point to a folder that the step-3 commands above do not copy (they copy `runs/confirmatory/run-1/full/figures` only).
- The provenance row of section 2 still reads `| Label | CONFIRMATORY: UNPROMOTED |`: it quotes the label stored in the sealed `results.json` and is kept on purpose (ROADMAP: only the header label is removed on the copy). The promoted report will therefore contain that string once; the same holds for the stored cells `label` and `promoted false` of the promoted `RESULTS.md`.
- Appendix C of the document (line 550 of the preliminary document, line 547 of the promoted copy) says the trace file sits "in this directory" and that the `check` command verifies the document against the sources. For the promoted copy that is not true (`check` refuses an edited document). `promote` leaves this sentence unchanged, because it is not in the allowed-edit table of the plan (adding it needs a reviewed change to the plan and the table).

Options for the figures:

| Option | What it does | Consequence |
|---|---|---|
| (a) Re-render F1 to F3 with a promoted status title | A reviewed change to `status_title` in the builder (a follow-up unit, for example WU-0034, not implemented here): new PNGs, same numbers; the same unit can add a rule that rewrites the appendix C sentence | The promoted report is free of the pre-promotion labels except the kept provenance row; new PNG hashes to record; builder change needs a review and the preliminary document must still pass `check` |
| (b) Copy F1 to F3 as they are, with a dated note | `cp -r` of the `.figures/` folder plus a dated line in the promoted copy | Fast, no tool change; the promoted report then shows three images that call themselves unpromoted and internal, which contradicts the text; the note has to say so, and the promoted copy is no longer made by `promote` alone |
| (c) Omit the images | Remove the three image links (and their captions) from the promoted copy | No contradiction; the report loses three figures, whose numbers stay in the tables; also needs an edit that `promote` does not make (a follow-up allowed-edit rule) |

Recommendation (stated as asked): **(a)**, as a follow-up unit before the promotion transaction if the owner is not pressed for time; the change is a title string in the builder and the numbers are untouched. If the promotion must come first, take **(c)** with the dated note rather than (b), because (b) places statements in a promoted report that the report itself denies. Either way the promoted report keeps the provenance row string "CONFIRMATORY: UNPROMOTED" once, and the owner should know this before placing the copy.
