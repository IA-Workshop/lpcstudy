# WU-0016: Regeneration by another actor (by ruling, the owner: DEC-0035) and run comparison

| Field | Value |
| --- | --- |
| Status | WU-0016.1 to .4: done as events, evidence below; unit record written after the fact on 2026-10-21. Open for the owner: audit M3 wording (same actor, same host) |
| Class | CSQ2 (use), CSQ3 (the comparison tool) |
| Agent(s) | the regeneration was run by the owner (Brian J. McDermott), as the regenerating actor under DEC-0035. This record was written by claude-sonnet-5-5 (developer) on 2026-10-21 from existing evidence only (audit B1). |
| Estimate | run-2 7884 s wall-clock (about 2.2 h) |

## Plan (written before execution)

The plan is `ROADMAP.md` phase F, rows WU-0016.1 to WU-0016.4 and the phase F acceptance paragraph: "tier T0 (bitwise) on the same platform; otherwise every QoI within the WU-0003.6 tolerance of its tier and every verdict identical; otherwise a DEF is opened and promotion is blocked". The row says the regeneration is run by "an agent session other than the producer, or the owner". v3 section 9 item 4 says "another actor". This file did not exist when the regeneration was made (audit B1).

## Log (written 2026-10-21, after the events)

### WU-0016.1 Authorization

- Ledger seq 21, 2026-10-20T08:44:49Z: `commit df8928fd06721d681469c9c3e40705e1b4b8053f`, `run runs/confirmatory/run-2`, quote "regenerating to confirm bitwise identity across CPU runs". It precedes the run start (2026-10-20T08:51:39Z).
- Ruling on who may regenerate: ledger seq 23 (2026-10-20T11:41:58Z, DEC-0035): "Another actor is fine to be me." The owner is the regenerating actor.

### WU-0016.2 Regeneration run

- From the clean detached worktree `/home/brianm/projects/physics/chaos/lpcstudy-wt/run/regen-freeze-1` at `df8928fd06721d681469c9c3e40705e1b4b8053f` (`freeze-1`); full preset, the sealed-run option, CPU, `LPC_THREADS=8`; `dirty false`, `complete true`; start 2026-10-20T08:51:39Z, end 2026-10-20T11:03:03Z, "study finished in 7884s". Label `CONFIRMATORY: UNPROMOTED`, `promoted false`.
- Pre-run script note (recorded in `WU-0020-preliminary-findings.md`, 2026-10-20): `tools/owner_freeze_run.sh prerun` printed "BLOCKED: .git/info/exclude holds more than .venv" in the linked worktree, a false positive because `.git` is a file there. The owner checked the shared exclude file (exactly `.venv`), no attributes file, HEAD df8928f, clean tree, and launched run 2.
- Files: `runs/confirmatory/run-2/full/results.json` sha256 `08f3de8f7491b7fd632d2ae87f7b9f04fb0773598c70dd00c9cc9f0ff3b9f2f9`; `RESULTS.md` `e382b1110107ce1f83aa4a8d2a6c5939d096af42fc209c1850319511710c497b`; sidecar `runs/confirmatory/run-2.sha256`; console log `runs/confirmatory/run-2.console.log`. The two `results.json` files differ as files (provenance leaves differ); the comparison below is by leaf.
- The wall-clock of run-2 (7884 s) is about half that of run-1 (15555 s) with bitwise-equal compared leaves. No cause is recorded; it is noted, not explained.

### WU-0016.3 Comparison tool

- `tools/compare_runs.py` with tests `tests/unit/test_tools_compare_runs.py`. Its tolerance and verdict rules were ratified by the owner (DEC-0030 items OF-5 and OF-7; DEC-0032 item 6, B9). The banner in its output text ("needs owner review before freeze") was stale and is replaced in the same branch (audit m6; commit message "B1-minors m6"). Texts already committed keep the old banner (records are not rewritten).

### WU-0016.4 Comparison and manifest entry

- `runs/confirmatory/run-2-compare.txt`, sha256 `11007a4e1d169946f431a447018b92f94705352700c10d1eb155c6006b646df5`: tier T0; leaves REF 20766, NEW 20766, union 20766, common 20766, equal 20766, different 0, one-sided 0; provenance (147 leaves) and timing (23 leaves) excluded on both sides; "RESULT: PASS (exit 0)". The claim supported is "every compared leaf equal", not "the files are identical" (audit item 8).
- Manifest entry (2026-10-20, owner) and outputs committed in `15c9eef` (2026-10-20 07:41 local, "WU-0016.4: manifest entry and outputs of the CONF-1 regeneration run-2 and its comparison with run-1 (unpromoted)").
- Release to agents: ledger seq 22, 2026-10-20T11:26:51Z (audience Brian McDermott and Deem Albaty; paths `runs/confirmatory/run-2/full` and `runs/confirmatory/run-2-compare.txt`; `promoted false`).

### Honest notes

- Same actor, same host, same environment: the T0 match shows the determinism of the pipeline at this commit on this machine. It does not show independence from the host, the environment or the operator (audit M3). DEC-0035 and seq 23 rule that the owner satisfies item 4; the promoted report must say "regenerated bitwise by the producer on the same host (DEC-0035); no independent-actor or second-host regeneration", and must not imply independent reproduction. An agent-session regeneration (about 2.2 h at 8 threads, no GPU, under its own LPC.AUTH.6 authorization) would also meet LPC.PC.13's second branch; it is optional and was not done.
- GPU cross-check (WU-0015.2b): a different device, TD tier, information only (DEC-0031). It is not a regeneration in the sense of v3 section 9 item 4.
- Not recorded for WU-0016.2: the pre-run lock and no-other-run check beyond the owner's script note above.

## Review

- **Reviewer:** none for this record. Examined by the audit of 2026-10-21 (items 7, 8; M3).
- **Findings and resolution:** audit B1 addressed by this file; M3 wording to be carried in the promoted report (owner decision on the optional agent regeneration).

## Audit

- Is the definition of done met? Tier T0 on the same platform: yes (20766 of 20766 compared leaves equal, 0 different, PASS). Per-action authorization: seq 21, before the run. "Another actor": met by ruling, not by independence (M3).
- Defects recorded: none opened.
- Notes for successors: none.
