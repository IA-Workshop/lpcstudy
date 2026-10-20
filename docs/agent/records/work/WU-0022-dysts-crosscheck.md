# WU-0022: Dysts cross-check of the three studied systems (parameters, conventions, λ_max; the Chua exponent difference)

| Field | Value |
| --- | --- |
| Status | planned |
| Class | CSQ3 development (documentation and scratch computation) |
| Agent(s) | claude-opus-5-5 (planner); researcher and applied-mathematician to be named; under DEC-0037 |
| Estimate | About 3 agent hours; CPU minutes at one thread. Target 2026-10-21 (feeds the research statement and the open Chua limitation, DEC-0010). |

## Plan (written before execution)

- **Scope.**
  - **In:** for Lorenz-63, Rössler and Chua, this unit compares the Dysts database entries with the code. For each system it records:
    - the Dysts entry name, its equations and parameters, and whether the parameters equal those in `SYSTEMS`;
    - the Dysts time and sampling convention (its "period" and points per period or per Lyapunov time) against the code's "30 steps per LT" (`systems.py` docstring);
    - the Dysts λ_max and the method Dysts uses to estimate it;
    - the code's λ_max from `docs/study/pilot_results_v3_dev0_reference.json` (`systems/<s>/context/lambda_max`), a DEV-0 development reference;
    - the relative difference between the two.

    The unit also attributes the Chua difference to its causes.
  - **Out:**
    - any change to `report.LYAPUNOV_REFERENCES` for the three systems (frozen report text; any proposal goes to the owner);
    - any change to the sealed document or to v3;
    - sealed numbers;
    - installing `dysts` (O4: values are read from the source and quoted).
- **Sub-tasks.**

  | Id | What | Owner | Effort | Depends on | Target |
  | --- | --- | --- | --- | --- | --- |
  | .1 | Table and sources. This is part of the running note `2026-10-20-researcher-dysts-extension.md` if the dispatch covers it; else a follow-up dispatch | researcher | S | — | 10-20/21 |
  | .2 | Attribution note `docs/agent/notes/2026-10-21-dysts-chua-attribution.md`, with its scratch scripts beside it | applied-mathematician | S | .1 | 10-21 |

- **Definition of done.**
  - Table committed.
  - Attribution stated for Chua: "explained by <cause> within its SE" or "unexplained".
  - A one-sentence, number-free summary for WU-0025.3.
  - A proposed wording for the DEC-0010 limitation, for the owner.
- **Acceptance criteria.**
  - **B1.** Every value carries a source (URL or DOI and commit or version of the Dysts data file), a quote and a status: confirmed, or unconfirmed (memory). Nothing from memory is used.
  - **B2.** Agreement is judged by |Δλ| ≤ 3·√(SE_code² + SE_dysts²).
    - SE_code is the batch SE of the code's 100 000-step Benettin estimate. The mathematician computes it once from an independent implementation, single-threaded and niced.
    - SE_dysts is whatever Dysts states. If it states nothing, the difference is reported without the words "agree" or "disagree".
  - **B3** (Chua). Each candidate cause is tested by a scratch computation, or is marked "untested" with the reason. The candidates are:
    - (i) a different parameter set or diode form;
    - (ii) a time rescaling, for example per period against per unit time;
    - (iii) the length or method of Dysts' estimate;
    - (iv) the code's run length and step (LPC.NV.1).

    The code's sealed or frozen values are not changed (PRIME.2).
  - **B4.** Lorenz-63 and Rössler also get a row. Their published references (Sprott; Bogdanov & Bogdanova) are listed beside the Dysts value, so that any Dysts-to-literature difference is visible.
- **Affected checks.** None: documents and scratch scripts outside `tests/` and `lpcstudy/`. The scratch runs use one thread under `nice -n 19` while run-2 is active.
- **Owner checkpoints.** No code. Owner reads the proposed DEC-0010 wording.

## Log

## Review

- **Reviewer:**
- **Findings and resolution:**

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:

## Referral
