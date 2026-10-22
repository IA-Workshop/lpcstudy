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
4. **Label removal on copies:** the builder has no promoted-copy mode and `check` refuses an edited document, so the copy of the findings document with its PRELIMINARY line and UNPROMOTED labels removed cannot pass `check`; the owner decides whether the copy is an edited text file (checked by hand against the original with the label lines as the only difference) or a tool change. The labels inside the PNG figures of the findings document are drawn images; whether they are re-rendered is the owner's call. The sealed `RESULTS.md` has its label in the first lines and in the stored provenance cells (`label`, `promoted false`); per ROADMAP only the header label is removed on the copy, and the stored provenance stays.
5. Open owner items from the audits that do not block: seq 36 reading (m-1), m8 (v3 §9 item numbering, frozen).

## 7. The ledger `proposal` command (draft, **not run**)

To be run by the owner from the repository root once the items in section 6 that the owner wishes to settle are settled. The actor and role words are placeholders for the owner to set. `--files` hashes the named governed files into the entry.

```
python3 tools/ledger.py append --type proposal \
  --actor "Brian J. McDermott" --role "human owner" \
  --authority "LPC.PC.13; ROADMAP WU-0018.2" \
  --summary "WU-0018.2: proposal to promote the CONF-1 result (run-1 official CPU files and the findings document as report text); regeneration run-2 T0 20766 of 20766 equal; two audits; waivers seq 31 and 33; rulings seq 30, 32, 34, 36" \
  --files docs/agent/notes/2026-10-22-promotion-proposal.md docs/agent/notes/2026-10-20-prelim-findings-conf1.md \
  --data '{"seed_id":"CONF-1","manifest":"docs/agent/records/results-manifest.md lines 29 and 30","results_sha256":"ae4b0fe5bf488f6c147bce6c91a2398e87408f6a5d372ae66d89bdfc90b0cebe","results_md_sha256":"2a4c1d06859d07584b1633c6e7f1b5df205ffe445402509834383fb474649577","regeneration_compare_sha256":"11007a4e1d169946f431a447018b92f94705352700c10d1eb155c6006b646df5","audits":["docs/agent/notes/2026-10-21-audit-pre-promotion-conf1.md","docs/agent/notes/2026-10-22-audit-promotion-conf1.md"],"waivers":[31,33],"rulings":[30,32,34,36],"promoted":false}'
python3 tools/ledger.py verify
```

(I did not run the command, so I do not know whether `--files` accepts files that are not governed instruments; if the tool refuses them, drop `--files` and put the hashes in `--data`.)

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

# 3. promoted copies; the label is removed on the COPIES only, the originals stay as they are
mkdir -p promoted/CONF-1
cp -r runs/confirmatory/run-1/full/figures promoted/CONF-1/figures
cp runs/confirmatory/run-1/full/results.json promoted/CONF-1/results.json
cp runs/confirmatory/run-1/full/RESULTS.md promoted/CONF-1/RESULTS.md
cp docs/agent/notes/2026-10-20-prelim-findings-conf1.md promoted/CONF-1/report.md
#    remove the header label line of each copy by hand or with a one-line sed on the copy; see section 6 item 4
sha256sum promoted/CONF-1/*    # record in the manifest line

# 4. verify and sync
python3 tools/ledger.py verify
#    sync main as for entries 1 to 28 (commit 83520cc): the owner merges develop into main; main only when fully green (owner authorizes)
```

The sketch is a sketch: the folder name `promoted/` and the form of the label removal are proposals, not an adopted procedure.
