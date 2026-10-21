# WU-0015: Confirmatory run (CONF-1, full preset)

| Field | Value |
| --- | --- |
| Status | WU-0015.1: partly evidenced (see below); .2, .2b, .3, .4: done as events, evidence below; unit record written after the fact on 2026-10-21 |
| Class | CSQ2 confirmatory |
| Agent(s) | the runs were launched by the owner (Brian J. McDermott). This record was written by claude-sonnet-5-5 (developer) on 2026-10-21 from existing evidence only (audit B1, `docs/agent/notes/2026-10-21-audit-pre-promotion-conf1.md`). No run, seed or sealed output was touched in writing it. |
| Estimate | official CPU run 15555 s wall-clock (about 4.3 h) |

## Plan (written before execution)

The plan is `ROADMAP.md` phase F, rows WU-0015.1 to WU-0015.4 and the "Definition of done and acceptance criteria, phase F" paragraph. It is not restated here. This file did not exist when the runs were made (audit B1, 2026-10-21): it records, per sub-task, what the evidence shows and what is not evidenced.

## Log (written 2026-10-21, after the events; every line cites existing evidence)

All times: the ledger and provenance times are UTC; the manifest and `run.log` times are the owner's local time (UTC minus 4 h).

### WU-0015.1 Pre-run checks and per-action authorization

- Working tree clean at `freeze-1`: evidenced after the fact by the run's own provenance, `commit df8928fd06721d681469c9c3e40705e1b4b8053f` (equal to `freeze-1^{commit}`; the tag was made 2026-10-19 08:34:05Z) and `dirty false` (`runs/confirmatory/run-1/full/results.json`, `run.log` line 1). The code's second git read (`check_tree_unchanged`) refuses a changed tree before any output exists.
- `pip freeze` equal to `requirements.lock`: not recorded as a pre-run check. The audit of 2026-10-21 (item 1) compared the packages stored in the provenance with `requirements.lock` at `freeze-1` and found them equal (jax and jaxlib 0.11.2, numpy 2.5.3, scipy 1.18.1, scikit-learn 1.9.1, optax 0.2.8, matplotlib 3.11.2, Python 3.13.16). This is after-the-fact evidence by the auditor, not a recorded pre-run step.
- No other preset run on the CPU, run lock free: **not recorded**. No evidence in the records.
- `LPC_THREADS=8`: stored in the provenance of the run (audit item 1).
- Per-action authorization (LPC.AUTH.6): **entered retroactively.** Ledger seq 15, 2026-10-20T08:37:48Z, `data.entered_after_run: true`, `quote: "entered retroactively"`, `run_started: "2026-10-19T04:38:31"` (local time, no zone). The run started 2026-10-19T08:38:31Z, six minutes after the commitment entry (seq 13, 08:32:50Z) and four minutes after the `freeze-1` tag. The ROADMAP acceptance ("the ledger holds the per-action `authorization` entry quoting the owner's words") was not met at the time of the run, and the entry quotes no authorizing words. Audit finding M2 asks the owner for a `ruling` entry (the owner launched the run under the owner's own authority; seq 15 accepted as its record; stating whether any agent assisted). That ruling is **not yet recorded**. This file does not supply it.
- Status: authorization and clean tree evidenced as stated; the pre-run checklist as such is not recorded; the owner's ruling on seq 15 is pending.

### WU-0015.2 Official run

- Full preset, the sealed-run option, seed id CONF-1, CPU (`device backend cpu`), `LPC_THREADS=8`, label `CONFIRMATORY: UNPROMOTED`, `promoted false`, `complete true`. Start 2026-10-19T08:38:31Z, end 2026-10-19T12:57:46Z, "study finished in 15555s" (`run.log` line 228): under the 12 h bound of the acceptance paragraph.
- The seed value appears in no output (audit item 4: no leaf holds a seed value, `config/seed` is null, only `CONF-1` appears in log, console log and `RESULTS.md`).
- Files: `runs/confirmatory/run-1/full/results.json` sha256 `ae4b0fe5bf488f6c147bce6c91a2398e87408f6a5d372ae66d89bdfc90b0cebe`; `RESULTS.md` `2a4c1d06859d07584b1633c6e7f1b5df205ffe445402509834383fb474649577`; sidecar `runs/confirmatory/run-1.sha256`; console log `runs/confirmatory/run-1.console.log`.
- It was launched by the owner, not through an agent, on every indication in the records (owner commit e754601 carries no `Agent:` line; DEC-0035 says the owner ran both executions). No record names who typed the launch command; the audit asks the owner to say so in the M2 ruling.

### WU-0015.2b GPU cross-check

- Authorization: ledger seq 14, 2026-10-20T07:34:04Z (`quote "CONF-1-GPU"`, `run runs/confirmatory/run-1-gpu`), before the run (start 2026-10-20T07:37:05Z).
- NVIDIA GeForce RTX 4090, commit `78f7f2f2d0431f52a6088a349b2dec8a9a3fba17` (`freeze-1` plus one commit that changes only `docs/agent/governance/ledger.jsonl`; audit item 3), `dirty false`, `complete true`, "study finished in 2696s", end 2026-10-20T08:22:02Z.
- Files: `runs/confirmatory/run-1-gpu/full/results.json` sha256 `b768cb036854012301e96f645cb0bb26ab58dbaa1edd19178792d04dc5ac5887`; `RESULTS.md` `e858294ed14844f39106618a25a5a5dba9bb52d151ba4f45f34cf06fddaa6cc4`.
- Comparison `runs/confirmatory/run-1-compare.txt`: tier TD, 18 of 18 parts computed, maximum z (away) 2.21 against the bound 3.4, 0 failing parts, RESULT PASS. Per DEC-0031 the GPU result informs only and changes no verdict. The 44 stored verdict words that differ between the CPU and GPU files (11 overall, 33 per system; audit item 7) are information only; the official words stand.

### WU-0015.3 Manifest entry and stored outputs

- `docs/agent/records/results-manifest.md`, 2026-10-20 entry "CONF-1 sealed run, UNPROMOTED", by the owner; commit `e754601` (2026-10-20 04:41 local, "WU-0015.3: manifest entry and outputs of the sealed CPU run and the GPU cross-check (unpromoted)"). Status in the manifest: unpromoted; hypothesis-test result. Hashes in the entry equal the sidecars and the files (audit item 1).

### WU-0015.4 Release of the outputs to agents

- Ledger seq 20, 2026-10-20T08:43:08Z: audience Brian McDermott and Deem Albaty; paths `runs/confirmatory/run-1/full`, `runs/confirmatory/run-1-gpu/full`, `runs/confirmatory/run-1-compare.txt`; `promoted false`; quote "completion of confirmatory CPU and GPU runs".
- Ordering note (DEC-0035 item 1, ledger seq 23): the output commit e754601 (2026-10-20 04:41 local, 08:41Z) preceded the release entry (08:43:08Z) by about two minutes. The owner ruled this acceptable ("A13 is fine"). Agents first read the sealed outputs after the release entry (audit item 10).

## Review

- **Reviewer:** none for this record. The runs themselves were examined by the pre-promotion audit of 2026-10-21 (`critical-elite-auditor`, claude-fable-5-1): "the sealed result itself is in good order".
- **Findings and resolution:** audit B1 (no unit file) is addressed by this file; M2 (retroactive authorization) remains with the owner.

## Audit

- Is the definition of done met? The run, the cross-check, the manifest entries and the release exist and are consistent. Not met as written in the ROADMAP: the pre-run checklist record and the contemporaneous per-action authorization quoting the owner's words (M2).
- Defects recorded: none opened here.
- Notes for successors: future ledger entries for runs should carry an explicit UTC zone (audit M2).
