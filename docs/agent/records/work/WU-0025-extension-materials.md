# WU-0025: How the extension and the ensemble enter the 10/28 materials (appendix A, research statement, poster outline)

| Field | Value |
| --- | --- |
| Status | planned |
| Class | CSQ3 (tool and development appendix). The sealed sections of the findings document are untouched. |
| Agent(s) | claude-opus-5-5 (planner); developer, reviewer, main session and student to be named; under DEC-0037 and D4 and D5 of WU-0020 |
| Estimate | About 9 agent hours. Unit-test CPU seconds only. **Appendix inputs cut off 2026-10-26 18:00; materials ready 2026-10-27.** |

## Plan (written before execution)

- **Scope.**
  - **In:**
    - (.1) Extend `tools/findings_build.py`:
      - `--development` becomes repeatable, for the ensemble runs DEV-1, DEV-3 and DEV-4 (WU-0026), shown side by side in appendix A.1: per run the stored per-system verdict words and the 18 primary-part estimates and intervals;
      - a new repeatable `--extension`, for development runs whose systems are outside v3 (WU-0021 and WU-0023), shown in appendix A.2: per system the gate V1 to V7, the stored per-system verdict words, λ_max and CP VPT;
      - every value is a traced placeholder.
    - (.3) A number-free paragraph in the research statement: what the extension asks, labeled exploratory, and the Dysts context.
    - (.4) Poster outline updates.
    - (.5) The build of appendix A.
    - (.6) Its review.
  - **Out:**
    - any change to the `[PRE-REGISTERED]` and `[CROSS-CHECK]` sections;
    - any derived statistic across seeds (no mean, standard deviation or range: the stored values are shown side by side, O7);
    - the overall verdict of an extension run;
    - any sealed number in the statement or the poster outline before promotion (QA.11).
- **Sub-tasks.**

  | Id | What | Owner | Effort | Depends on | Target |
  | --- | --- | --- | --- | --- | --- |
  | .1 | Tool extension and tests | developer | M (4 h) | — | 10-21 |
  | .2 | Independent review, at most two fix rounds, merge to `develop` | reviewer, main session | S | .1 | 10-22 |
  | .3 | Research statement paragraph and a trace row for it | planner or developer drafts; student edits | S | WU-0021.2, WU-0022.1 | 10-23 |
  | .4 | Poster outline: §0 line "There is no new DEV ensemble before the fair" replaced (DEC-0037); appendix panel and slide "Development context: not a hypothesis test" with A.1, A.2 and the WU-0024 table as text; honesty checklist items | planner drafts; student edits | S | .1 | 10-24 |
  | .5 | Build: `render` with the sealed inputs (as WU-0020.7) plus `--development` × 3 and `--extension` × n; then `check` | main session | S | .2, WU-0026.2, WU-0021.9, WU-0023.5 and WU-0024.3, each if ready by the cutoff | 10-26 |
  | .6 | Fresh-context review of appendix A, the statement paragraph and the outline changes | reviewer | S | .5 | 10-27 |

- **Definition of done.**
  - The tool is merged on `develop` with the review approved.
  - The sealed document is rebuilt with appendix A and `check` exits 0.
  - The statement and the outline are updated, and the student has edited them.
  - Review .6 has zero open findings.
- **Acceptance criteria** (the WU-0020 criteria A1 to A13 still hold; added):
  - **E1 Regression.**
    - With none of the new arguments, `render` on the DEV-2 dry-run pair gives a document, trace and PNGs byte-identical (SHA-256) to the committed `docs/agent/notes/2026-10-19-prelim-findings-dryrun-dev2.*`. `sources.json` may differ only in its worktree paths.
    - The main session re-renders the sealed document with the new tool and no new arguments. It must be byte-identical to the committed `2026-10-20-prelim-findings-conf1.md` and its trace.
  - **E2 Trace.** Every number in A.1 and A.2 is a placeholder resolved from its run, and `check` re-verifies it. The SHA-256 of each development file is recorded in `sources.json` and checked again.
  - **E3 No recomputation** (A3 extended). The new code imports no verdict or statistics function and computes no aggregate across runs. A unit test greps the source and checks a planted, inconsistent stored leaf: it must be shown as stored.
  - **E4 Separation** (A6 extended). Sources `dev:<id>` and `ext:<id>` resolve only inside appendix A. One planted violation per new source kind fails `check`.
  - **E5 Refusals.** The tool refuses:
    - a `--development` or `--extension` file that is not a development run (`classify`);
    - a duplicate file (same realpath or same SHA-256);
    - an `--extension` run that contains a v3 system;
    - a `--development` run whose `core_systems` are not the three v3 systems.
  - **E6 Determinism.** Two renders give byte-identical outputs.
  - **E7 Labels.** Every appendix table is headed "Development context: not a hypothesis test" and names its seed ids. The extension table also says "systems outside the v3 design; exploratory readings pre-specified in WU-0021.2".
  - **E8 Statement and outline.** No digit in the new statement paragraph, except system names such as "Lorenz-63". The honesty checklist gains one item per new appendix element.
- **Affected checks.**
  - `tools/findings_build.py`, `tools/findings/design_constants.json` and the template map to `tests/unit/test_tools_findings_build.py` (unit tier, `TOOL_DATA_TESTS`).
  - `tests/unit/test_tools_test_impact.py` is added only if `tools/test_impact.py` changes.
  - Nothing in `lpcstudy/` changes, so there is no integration tier.
  - Run with `LPC_THREADS=1` under `nice -n 19` while run-2 is active.
- **Owner checkpoints.**
  - O7: side by side, no aggregates.
  - The poster appendix wording.
  - D5: the sealed numbers stay with the owner and the student until promotion.
  - No verdict, seed, provenance or dependency change.
- **Ordering with the sealed track.** WU-0016, WU-0017 and WU-0018 take precedence for the main session and the reviewer. .5 never delays the promotion.

## Log

## Review

- **Reviewer:**
- **Findings and resolution:**

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:

## Referral
