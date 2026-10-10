# WU-0013: DEF-0007 audit of the 14 v1 tests, and fixes

| Field | Value |
| --- | --- |
| Status | in progress |
| Class | CSQ3 development |
| Agent(s) | claude-sonnet-5-5 (main session) under governance ledger entry 5 (authorizations 4, 6) |
| Estimate | WU-0013.1 M, .2 S (ROADMAP.md §2) |

## Plan (written before execution)

- **Scope:** ROADMAP.md §2 phase A, WU-0013.1 and .2. In: the 14 v1 tests (now in `tests/unit/test_{allocation,analysis,dynamics,embedding,ensemble,oracle,statistics}.py`; not the marker tests of WU-0010 or the tool tests of WU-0011). WU-0013.1 is an audit by the reviewer that touches no test; WU-0013.2 is the developer's fixes. Out: `lpcstudy/`, governance, and any change to a tolerance that makes a test easier to pass.
- **Definition of done and acceptance criteria** (verbatim from ROADMAP.md §2, fixed before execution, VV.3):

| Id | Definition of done | Acceptance criteria (checkable) |
| --- | --- | --- |
| WU-0013.1 | `docs/agent/records/audits/<date>-def-0007-tests.md` lists all 14 tests with reference, independence and tolerance status | Every test is classified `reference`, `regression guard` or `defective`; each `reference` row names the reference kind from LPC.PC.21a. Tests found self-referential are listed for WU-0013.2. The audit touches no test. |
| WU-0013.2 | Every test has a docstring naming its reference and tolerance justification (`.claude/rules/tests.md`) | All 14 tests pass; `git diff` shows no tolerance that grew (reviewer checks each numeric literal in an `assert` or `approx`); DEF-0007 gets a dated `resolved` line with the audit path. |

- **Affected checks:** WU-0013.1: none (no test or code is touched). WU-0013.2: the test files it edits, per §4.2, unit tier (the 14 tests live in 7 files; the radius is those files). The audit file is `docs/agent/records/audits/2026-10-10-def-0007-tests.md`.
- **Owner checkpoints (LPC.PC.11):** none (no verdict, statistics, seed, provenance or dependency code).
- **Order:** .1 (reviewer), then .2 (developer), then independent review of .2 by a reviewer other than the .1 auditor where possible.
- **Note for the audit:** a test marked `reference` must name an independent reference (closed form, brute force, a published value, a conservation law or a property check, LPC.PC.21a); a test that checks a function against itself or against a copy of the same formula is `defective`; a test that pins current behaviour is a `regression guard` and is renamed `test_regression_*` in .2 (renaming a test is not a change of its assertions).

## Log

<dated entries: what was done, commands, results, commits>

- **2026-10-10, WU-0013.1 audit** (`reviewer`, claude-opus-5-5, fresh context, worktree `wu/0013-def0007-audit` at `0da91a7`).
  - **What was audited.** All 14 v1 tests in `tests/unit/test_{allocation,analysis,dynamics,embedding,ensemble,oracle,statistics}.py`, plus `tests/unit/unit_helpers.py`, together with every `lpcstudy` function they call. The audit is in `docs/agent/records/audits/2026-10-10-def-0007-tests.md`.
  - **Result.** 13 `reference`, 0 `regression guard`, 1 `defective`.
    - **Defective:** `test_dynamics.py::test_observability_matches_independent_jacobians` copies the ν formula of dynamics.py:220–222 at test L32. It also shares the delay-index expression through `delay_map_forward`.
    - **Weak or uncited `reference` tests, listed for WU-0013.2:** `test_delay_and_acf` (the AMI band is uncited and wider than its own docstring) and `test_logrank_detects_difference_and_not_null` (no check of the p-value's value).
  - **Docstrings.** None of the 14 docstrings states both a reference and a tolerance justification. All 14 are listed for WU-0013.2, with fixes that loosen no tolerance.
  - **What was not run or changed.** No test was run (WU-0013.1 needs none). No test or `lpcstudy/` file was touched. The Monte Carlo error figures in the audit are scratch NumPy arithmetic, run without importing `lpcstudy`.

## Review

- **Reviewer:** <actor, not the author>
- **Findings and resolution:**

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:

## Referral

<only if halted; use the form in agent-instructions.md, LPC.AI.13>
