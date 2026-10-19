# WU-0020: Preliminary findings document and data presentation (CONF-1, unpromoted)

| Field | Value |
| --- | --- |
| Status | planned |
| Class | CSQ3 for the tool and the DEV-2 dry run; CSQ2 for the build from the released sealed outputs |
| Agent(s) | claude-opus-5-5 (planner); developer, reviewer and main session to be named |
| Estimate | About 10 to 11 agent hours before release (critical path .2 → .3 → .4 → .6); about 3 to 4 h after release, plus the WU-0016 regeneration wall clock (about 4.7 h CPU) in parallel. No GPU. CPU use is seconds, niced. |

## Plan (written before execution)

Detail, the section list, the pipeline and the owner decisions D1 to D10 are in `docs/agent/notes/2026-10-19-preliminary-findings-plan.md` (the "note"). Owner's instruction, verbatim: "Once the CPU and GPU initial confirmatory runs are complete, we need to coalesce around a preliminary findings document and present the data. Plan out how to do this."

- **Scope.**
  - **In:**
    - a short internal document P1 (`docs/study/preliminary_findings_conf1.md`, written by the main session), with its trace file P2, figures P3 and one-page summary P4;
    - a number-free poster and slide outline P5;
    - the tool `tools/findings_build.py` (`render`, `check`, figures F1 to F3) and its unit test;
    - a dry run of the whole pipeline on DEV-2 (R6 CPU as "official", R5 GPU as "cross-check").
  - **Contents come only from the v3 design:**
    - v3 §2 rows and the §7 decision rules, overall rule and Q-N table;
    - v3 §6 E0 gate V1 to V7;
    - v3 §8 limitations;
    - v3 §9 item 3, the GPU cross-check (DEC-0031);
    - DEC-0028 TD rule, DEC-0033 M2 and M3, DEC-0024 A3.
  - **Out:**
    - any change in `lpcstudy/` (the freeze stands);
    - any new statistic, criterion, threshold, subgroup or recomputed verdict (LPC.PC.1, PRIME.2);
    - any new run on any seed, including a DEV ensemble;
    - figures for removed experiments;
    - the paper;
    - the promotion (WU-0018) and the regeneration (WU-0016), which are only sequenced.
  - **Governance limit:** P1 to P5 carry sealed numbers only to the owner and the student until WU-0018.3. QA.11: reporting an unpromoted result beyond its author is a blocking defect (note D5).
- **Sub-tasks.**

  | Sub-task | What | Owner | Effort | Depends on |
  | --- | --- | --- | --- | --- |
  | WU-0020.1 | Skeleton template `tools/findings/preliminary.template.md` (sections 0 to 11 and appendices A to C, as listed in the note §4); `tools/findings/design_constants.json` (each constant with its v3 section); number-free wording templates for supported / not supported / inconclusive / gate failure / GPU disagreement | planner drafts; owner and student review the wording | 2 h | — |
  | WU-0020.2 | `tools/findings_build.py` and `tests/unit/test_tools_findings_build.py` | developer | 4 to 5 h | .1 |
  | WU-0020.3 | DEV-2 dry run on scratch copies under `runs/dev/prelim-dryrun/`; `compare_runs` R6 against R5; render and check; dry-run document committed to `docs/agent/notes/`, labelled DEVELOPMENT | developer | 1 h | .2 |
  | WU-0020.4 | `/independent-review WU-0020` of .2 and .3 | reviewer | 1 h | .3 |
  | WU-0020.5 | Poster outline and 10-slide variant (number-free, slots F1 to F4), poster highlights fixed before release (D10), figure and table checklist | student with planner | 2 h | .1 |
  | WU-0020.6 | Merge to `develop` (merge gate, unit radius) | main session | 0.5 h | .4 |
  | WU-0020.7 | After release: build P1 to P4 from the committed outputs, `compare_runs` CPU against GPU, `check`; commit | main session | 0.5 h | .6, WU-0015.4 |
  | WU-0020.8 | Fresh-context review of P1 against `results.json` (every claim; 20 random trace rows re-read by hand) | reviewer | 1 to 2 h | .7 |
  | WU-0020.9 | Owner and student read (feeds WU-0017.3); the student writes §11; one dated line in §9 after WU-0016.4 | owner, student, main session | — | .8 |

- **Definition of done.**
  - .1 to .6 merged on `develop` with the dry-run document committed and `check` exit 0 on it.
  - After release: P1 to P4 built from the released CONF-1 outputs, `check` exit 0, review .8 with zero open findings.
  - The owner and the student have the document.
  - Every owner decision D1 to D10 is answered or explicitly left at its default by the owner.
- **Acceptance criteria** (fixed now; checked mechanically):
  - **A1 Banner.** Line 1 of P1 equals the provenance label as `report.header_lines` renders it: `**CONFIRMATORY: UNPROMOTED**` for CONF-1, and the DEVELOPMENT label for the dry run. Line 2 is the PRELIMINARY line of the note §2.1. The reference is `provenance.label`; the comparison is exact string equality.
  - **A2 Trace.** `findings_build.py check` exits 0. Every number in P1 and P4 is either a placeholder whose rendered string equals the declared formatter applied to the leaf (exact string equality: deterministic formatting of the same float, so no tolerance applies) or a constant in `design_constants.json` that cites its v3 section. P2 has one row per quoted number.
  - **A3 No recomputation.** Every verdict word in P1 equals `verdicts.<id>.verdict`, `verdicts.<id>.by_system.<s>` or the part's `verdict` leaf. The tool imports none of `statistics.criterion_verdict`, `combine_verdicts`, `overall_verdict` and compares no interval with a band. This is pinned by a unit test that greps the source and checks a planted `verdict` leaf that contradicts its interval: the planted leaf must be shown as stored.
  - **A4 Completeness.**
    - All 14 rows of `identifiers` (H1a to H3c, Q-N, gain bound) appear once in the verdict table.
    - All 18 primary parts (`compare_runs.TD_PARTS` × 3 systems) appear in the parts table and in F1. Each shows its estimate, its interval, the level stored in the leaf (1 − 0.05/3 for the primaries), the band and the verdict.
    - Each row carries its interval label from `RESULTS.md`.
    - Each H3a system shows events and censored states per regime, or "not recorded".
    - Q-N shows its reading.
    - The gain bound is labelled "reported, v1 statistic, v3 screen pending".
  - **A5 Gate and handling.**
    - V1, V2, V4, V5, V6 and V7 are shown per system with their statistic. A system whose `gate_pass` is false carries PROVISIONAL in every table row and figure panel of that system.
    - The handling run totals equal `handling.totals`, with zero counters printed as 0.
    - `failed_variants` is shown.
  - **A6 Separation.** Every placeholder in a `[PRE-REGISTERED]` section resolves to the official CPU file. `[CROSS-CHECK]` placeholders resolve to the GPU file or the TD text. `[DEVELOPMENT]` text is only in Appendix A. `check` fails a cross-tag placeholder (unit test with one planted violation per tag).
  - **A7 Limitations.** §10 lists each item of v3 §8 plus:
    - DEF-0018, DEF-0020, DEF-0026, DEF-0027;
    - DEC-0033 M2 and M3;
    - one realization per system;
    - the block-sensitive label status (D6).

    The check is by a fixed keyword list in `design_constants.json`.
  - **A8 Language.** Zero hits, case-insensitive, of the banned list of the note §2.7 in `[PRE-REGISTERED]` sections. The v3 §7 sentence on the uncontrolled error of "not supported" is present.
  - **A9 Provenance.** P1 §2 shows:
    - the commit, equal to `git rev-parse freeze-1^{commit}` for CONF-1;
    - `seed_id` CONF-1, CPU backend, `LPC_THREADS` 8, `dirty` false, `complete` true;
    - the SHA-256 of each `results.json`, equal to the WU-0015.3 manifest row;
    - the release ledger sequence.

    The tool refuses a confirmatory `seed_kind` without `--release-ref` (unit test).
  - **A10 Dry-run TD reference.** On DEV-2, the 18 z_away values, the maximum (2.26), the sum of z² (15.77) and "failing parts 0" equal `docs/agent/records/work/WU-0003-9c-compare-R5R6.txt` at its printed precision. This is exact: same inputs, same arithmetic, and z_away is symmetric when the two runs are swapped. A difference is a finding to report, never a tolerance to widen.
  - **A11 Figures.**
    - F1 and F2 draw exactly the stored estimates and interval endpoints. A unit test checks the plotted arrays against the leaves of a synthetic file with planted values (exact equality).
    - Every caption names the experiment E1 to E6, the v3 identifier and the interval procedure (WU-0017.2).
    - `grep` of the tool and captions finds no shift, transfer, Lorenz-96 or A4f.
    - Verdicts are encoded by marker shape and text as well as colour (Okabe–Ito).
  - **A12 Determinism.** Two `render` runs on the same inputs give byte-identical P1, P2 and PNGs (SHA-256 equal; matplotlib `metadata={"Software": None}`, fixed dpi).
  - **A13 Sealed-data discipline.** No agent reads or commits anything under `runs/confirmatory/` before the release record (WU-0015.4) exists in the ledger or queue. Checked by `git log --format=%H -- runs/confirmatory docs/study/preliminary_findings_conf1.md`: the first commit follows the release record. No sealed number appears in P5 until the WU-0018.3 promotion entry exists.
- **Affected checks** (DEVELOPMENT_WORKFLOW.md §4.2):
  - `tools/findings_build.py` maps to `tests/unit/test_tools_findings_build.py` (unit tier, under 5 s per test, CPU, run under `nice -n 19`).
  - Nothing in `lpcstudy/` changes, so there is no integration tier and no smoke run.
  - Template and JSON files under `tools/findings/` are covered by the same test file.
  - The dry run uses CPU seconds. No `python -m lpcstudy --preset` while `pgrep -fa "lpcstudy --preset"` shows the sealed run; the tool calls `report.write_markdown` and `make_figures` in-process on scratch copies instead.
- **Owner checkpoints** (LPC.PC.11):
  - verdict or statistics code: none changed (the tool reads only, A3);
  - seed or provenance code: none changed, but the tool reads released sealed outputs and refuses them without `--release-ref`, so the owner should glance at that guard;
  - dependencies: none (matplotlib and numpy are already pinned);
  - owner acts: the release (WU-0015.4), D1 to D10, and the reading (WU-0017.3).
- **Split.** Before release: .1 to .6 (CSQ3, one coherent tool plus template). After release: .7 to .9 (CSQ2, a build and review). The after-release half does not start before WU-0015.4.
- **Open questions for the researcher:** the science fair's date, its rules on preliminary or unverified results, its AI-use disclosure rules, and the poster size limits.

## Log

## Review

- **Reviewer:**
- **Findings and resolution:**

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:

## Referral
