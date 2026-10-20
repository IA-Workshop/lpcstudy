# WU-0024: Descriptive comparison with the Dysts forecasting benchmark (no ranking claim)

| Field | Value |
| --- | --- |
| Status | planned |
| Class | CSQ3 development (documentation; development values only) |
| Agent(s) | claude-opus-5-5 (planner); researcher, applied-mathematician, main session and reviewer to be named; under DEC-0037 |
| Estimate | About 4 agent hours; no compute beyond reading leaves. **Target 2026-10-24.** |

## Plan (written before execution)

- **Scope.**
  - **In:** a mapping table between the Dysts benchmark, which is Gilpin (2023), Phys. Rev. Res. 5, 043252, and the context-parroting results of Zhang & Gilpin (2026), arXiv:2505.11349 (both cited in v3), and this study. The table covers:
    - the valid prediction time (VPT) definition: error threshold and normalization;
    - the time unit (which λ, and Lyapunov times against periods);
    - noise (benchmark against ρ as a fraction of σ_x);
    - the length of the training or library data against n_lib;
    - the error metrics (sMAPE and the like against MSE in σ_x units);
    - the forecaster classes (their context parroting against this CP);
    - which systems overlap.

    A descriptive table follows. It puts published values beside this study's development values for the overlapping systems: CP VPT, the v3 §6 V3 leaf `systems/<s>/validation/cp_median_vpt_lyapunov`, read from the ensemble runs (WU-0026) and, where present, from the WU-0021 runs.
  - **Out:**
    - any ranking or "better/worse" claim;
    - sealed numbers;
    - any new run;
    - any new statistic: values are quoted as stored;
    - installing `dysts`.
- **Sub-tasks.**

  | Id | What | Owner | Effort | Depends on | Target |
  | --- | --- | --- | --- | --- | --- |
  | .1 | Definitions and published values, quoted with page or section | researcher | S | — | 10-21/22 |
  | .2 | Mapping note: per row, "comparable: yes, partly or no", with the reason, and the conversion if one exists | applied-mathematician | S | .1 | 10-22/23 |
  | .3 | Descriptive table and caption text, for WU-0025.5 and the poster appendix | main session | S | .2, WU-0026.2 | 10-24 |
  | .4 | Fresh-context check of every number against its source or leaf | reviewer | S | .3 | 10-24 |

- **Definition of done.** The note `docs/agent/notes/2026-10-2x-dysts-benchmark-comparison.md` is committed and reviewed, with zero open findings.
- **Acceptance criteria.**
  - **D1.** Every benchmark row cites the text with a quote. Every study row names the code symbol or leaf path.
  - **D2.** Every number is either a quoted published value or a stored development leaf with its run (seed id, commit, SHA-256 of `results.json`). Nothing is computed, except a stated unit conversion. Each conversion is written out, and the reviewer re-derives it.
  - **D3.** Zero hits, case-insensitive, of these words in the note and the caption: outperform, beats, better than, worse than, state of the art, superior, wins.
  - **D4.** The label "Development context: not a hypothesis test" heads the table (D4 of WU-0020).
- **Affected checks.** None: documents only.
- **Owner checkpoints.** None beyond D4. The owner reads the caption before it goes on the poster.

## Log

## Review

- **Reviewer:**
- **Findings and resolution:**

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:

## Referral
