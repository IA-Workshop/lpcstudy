# WU-0026: Development ensemble records (full preset, GPU, DEV-1, DEV-3, DEV-4 at develop 3dec086)

| Field | Value |
| --- | --- |
| Status | done (records from existing evidence, 2026-10-23); runs launched 2026-10-20 by the main session |
| Class | CSQ3 development |
| Agent(s) | claude-opus-5-5 (planner); main session to be named; under DEC-0037 item 4 and LPC.AUTH.3 |
| Estimate | About 2.5 h of GPU wall clock (launched); about 1 agent hour of records. |

## Plan (written before execution)

- **Scope.**
  - **In:**
    - records of the three launched runs: manifest rows, GPU-hour tally, gate and completeness flags;
    - the inputs for appendix A.1 (WU-0025) and for the WU-0024 table.
  - **Out:**
    - any further seed;
    - any aggregate statistic across seeds (O7);
    - any comparison with the sealed run;
    - any rerun.
- **Sub-tasks.**

  | Id | What | Owner | Effort | Depends on | Target |
  | --- | --- | --- | --- | --- | --- |
  | .1 | Manifest rows and the GPU tally (`tools/gpu_hours.py` reads `run.meta.json`) | main session | S | the runs end | 10-20 |
  | .2 | Gate V1 to V7 per system and `complete` per run, read with a one-line `python -c`; failures recorded as provisional, never rerun | main session | S | .1 | 10-20 |

- **Definition of done.** Three manifest rows, labeled exploratory, and the gate table in the Log.
- **Acceptance criteria.**
  - **F1.** Each row gives:
    - the commit (3dec086);
    - the result of `git diff --quiet freeze-1 3dec086 -- lpcstudy/`, which must be true;
    - the seed id, the preset `full`, the device (CUDA) and `LPC_THREADS`;
    - the wall clock from `run.meta.json`;
    - the SHA-256 of `results.json`;
    - the label `DEVELOPMENT (DEV-n): not a hypothesis test`, checked against the `RESULTS.md` header.
  - **F2.** A run with a non-zero exit, or with `complete` false, is listed as such and is not used in appendix A.1 (PRIME.4).
- **Affected checks.** None (records only).
- **Owner checkpoints.** None beyond LPC.AUTH.3 (the weekly GPU tally).

## Log

- **2026-10-23, records pass (claude-sonnet-5-5; no run, no test; results.json files read only).**
  - **WU-0026.1.** Manifest lines appended to `docs/agent/records/results-manifest.md` (2026-10-23): the three ensemble runs (DEV-1, DEV-3, DEV-4; commit `3dec0864dcb2dc11e09ff82cc8016e9d7b9bc2ed` read from the provenance block of each results.json, `dirty` false), and, as development context, the two extension batches (`974519a`, `392a069`). All labeled development, unpromoted by design, exploratory.
  - **F1 check.** `git diff --quiet freeze-1 3dec086 -- lpcstudy/` returns 0 (true, as required). For the extension commits the same command returns 1 (`974519a`: `data.py` 2 lines changed, `report.py` +130, `systems.py` +111; `392a069`: `data.py` 2 lines, `report.py` +146, `systems.py` +256), additive extension code; tests also differ (`tests/slow/test_extension_lyapunov.py`, `tests/slow/test_start_states.py`, `tests/unit/{test_experiments,test_extension_systems,test_report,test_systems}.py`, and the tools tests). F1 applies to the ensemble commit only.
  - **GPU hours.** `python3 -I tools/gpu_hours.py sum` (read-only): `week=2026-W43 gpu_hours=6.8125 gpu_seconds=24525 runs=9 open=0 cpu_excluded=24 unreadable=0`.
  - **WU-0026.2. Gate flags and `complete` per run** (read from `systems/<s>/validation/gate`, `systems/<s>/V7/slope_pass` and `provenance/complete` of results.json; none rerun, none edited). Exit code 0 for every run.

  | Run | complete | System: V1 V2 V4 V5 V6 V7, gate_pass | Provisional? |
  | --- | --- | --- | --- |
  | ens-DEV-1 | true | lorenz63, rossler, chua: all true, gate_pass true | no |
  | ens-DEV-3 | true | lorenz63, rossler, chua: all true, gate_pass true | no |
  | ens-DEV-4 | true | lorenz63, rossler, chua: all true, gate_pass true | no |
  | ext-rossler_hyper (S1) | true | V1 V2 V4 V5 V6 V7 true, gate_pass true | no |
  | ext-rossler_z (S3) | true | V7 false (slope_pass false), others true, gate_pass false | yes |
  | ext-lorenz63_r166 (S2) | true | V7 false (slope_pass true), others true, gate_pass false | yes |
  | ext-hyper_jha (S5) | true | V7 false (slope_pass true), others true, gate_pass false | yes |
  | ext-hindmarsh_rose (S4) | true | V7 false (slope_pass false), others true, gate_pass false | yes |
  | ext-lorenz96_4 (S6) | true | V7 false (slope_pass true), others true, gate_pass false | yes |

  - Per F2: no run has a non-zero exit or `complete` false, so none is excluded on that ground; the five provisional extension runs are marked provisional and are not rerun.
  - Handling counts (clips, replacements) are stored in `handling` of each results.json and are reported in the summary note; notable: ext-rossler_hyper `error_clips` 677809 (667517 non-finite), ext-rossler_z `error_clips` 1156, ens-DEV-3 `error_clips` 1 (PLP). They are not hidden by this record.
  - Summary note: `docs/agent/notes/2026-10-23-extension-ensemble-summary.md` (commits `482d619`, merged `beb6254`). No aggregate across seeds (O7).

## Review

- **Reviewer:**
- **Findings and resolution:**

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:

- **2026-10-23, main session records pass.** Definition of done: three manifest rows (plus six for the extension runs, outside the original scope, recorded because they share the tally) and the gate table in the Log: met, evidence above. Defects recorded: none new. Notes for successors: appendix A.1 (WU-0025) and the WU-0024 table may use the three ensemble runs only; the extension rows are exploratory and provisional (five of six fail V7). Cross-reference: the promotion close-out note concerns CONF-1 only and was not edited.

## Referral
