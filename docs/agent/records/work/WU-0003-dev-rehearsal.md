# WU-0003: Development rehearsal and precision report

| Field | Value |
| --- | --- |
| Status | planned |
| Class | CSQ3 development. Its precision estimates inform the owner's sample-size decision (LPC.PC.5). |
| Agent(s) | — |

## Plan

**Scope.**

1. **Rehearsal.** Run the v2 code at the pilot preset on `DEV-1`, on the owner's GPU, under LPC.AUTH.3.
2. **Optional full-preset run.** If time allows, run the full preset on `DEV-2`, within the 12-hour per-run limit of LPC.AUTH.3.
3. **Precision report** at `docs/study/dev_rehearsal_report.md`, labeled `DEVELOPMENT: not a hypothesis test`. For every v3 criterion it gives:
   - the interval half-width at the rehearsal size;
   - the half-width projected to the full preset;
   - which verdicts are reachable.

   It covers the H3c interval in particular, since the pilot had none.
4. **Reproducibility tolerance.** Run one core cell twice on GPU, and once on CPU with the same seed. Record the largest absolute and relative differences in w*, the seeds and the verdict statistics. Propose the tolerance that LPC.PC.18 declares, at about ten times the observed GPU-to-GPU variation.

**Out of scope:** looking at any confirmatory data; changing any criterion. A finding that a criterion is undecidable is reported to the owner, not fixed.

**Definition of done.** The report exists, the tolerance is proposed, and the owner has the information for the sample-size and freeze decisions.

**Acceptance criteria.**

- The run completes with the validation gate passing on all three systems, or the failure is reported.
- The report's numbers are regenerated from the run's `results.json` by a script committed with the unit (REPRO.10).
- Every number in the report states its seed id.

## Log

## Review

## Audit
