# WU-0026: Development ensemble records (full preset, GPU, DEV-1, DEV-3, DEV-4 at develop 3dec086)

| Field | Value |
| --- | --- |
| Status | in progress (runs launched 2026-10-20 05:31 local by the main session) |
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

## Review

- **Reviewer:**
- **Findings and resolution:**

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:

## Referral
