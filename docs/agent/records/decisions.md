# Decisions

Append-only record of decisions that affect a result or a contract (REPRO.7). Earlier study-design decisions, D1–D6 of 2026-10-10, are in `docs/study/decision_log_lpc.md`. A small decision MAY instead be recorded as a comment where it is implemented.

Use this format for each entry:

```
## DEC-nnnn: <title>  (YYYY-MM-DD, <actor>)
Decision:
Alternatives weighed and why rejected:
Affects:
Dissent and resolution (REPRO.8):
```

---

## DEC-0001: Development and confirmatory seeds are separated by commitment  (2026-10-10, proposed by Claude; for owner adoption with the governance)

**Decision.**

- Development runs use registered `DEV-n` master seeds.
- The confirmatory master seed is drawn by the owner at the freeze, committed by salted SHA-256 in the ledger, and supplied only at run time.

**Alternatives weighed.**

- *Reuse the pilot seed for the confirmatory run.* Rejected: its results have been seen.
- *Keep the confirmatory seed in the repository and simply promise not to use it.* Rejected: not verifiable.

**Affects:** every run; LPC.PC.7.

## DEC-0002: WU-0010 acceptance checks worded for what the tooling can run  (2026-10-10, proposed by claude-sonnet-5-5 (main session); for owner confirmation)

**Decision.** Four acceptance criteria of ROADMAP.md §2 WU-0010 are checked in a different form from their literal wording, with no loosening (plan amendment in `docs/agent/records/work/WU-0010-test-tiers.md`, answers to Q1–Q4):

- *Q1.* The collect-only check names each tier directory (and `tests/test_core.py` until removed) instead of bare `tests`, which the test-gate hook blocks outside a gate. The conftest raises a UsageError for any test outside a tier directory.
- *Q2.* "Exactly 14 passed in `tests/unit`" becomes: exactly 14 collected from the seven moved files, and 14+k passed for the tier, where k is the number of marker tests that WU-0010.1 itself places in `tests/unit` (k = 5 after fix round 1).
- *Q3.* `git diff -M` cannot detect a 1-to-7 split as renames. The evidence is an `ast` source and AST comparison of each moved test and the shared helper against `main:tests/test_core.py` (stricter than the criterion), plus `--color-moved`, with `git diff -M --stat` recorded as is.
- *Q4.* "The module it imports first" is read as "the module it exercises" (the ROADMAP row's wording); each file's imports are ordered so its first import names the file.

**Alternatives weighed and why rejected.**

- *Run the bare-`tests` collection under `LPC_GATE`.* Rejected: a gate run for a collect-only check is out of proportion, and the hook exists to prevent exactly this.
- *Edit ROADMAP.md to match.* Rejected: the roadmap is adopted governance; an agent does not alter it (GOV.49).
- *Hold the unit for the owner before executing.* Rejected: the checks are equal or stricter, nothing is irreversible, and the owner can still override before merge.

**Affects:** WU-0010.1 to .3 only; no code under `lpcstudy/`. The reviewer (claude-opus-5-5) accepted each substitute check (R4 of the review). ROADMAP.md line 11 and the other text that still names `tests/test_core.py` as the live suite (`.claude/rules/test-discipline.md:18`, `.claude/skills/test-impact/SKILL.md:27`, DEVELOPMENT_WORKFLOW.md lines 89 and 138) go stale at the merge; the owner updates or adopts changes to those files.

**Dissent and resolution (REPRO.8):** none so far. Status: proposed; the merge to `main` waits for the owner to confirm or override.

- 2026-10-10, recorded by claude-sonnet-5-5 (main session) at the human owner's instruction: the human owner confirmed DEC-0002 as written, in the session chat ("I agree, confirmed as written"). Status: **confirmed**. This line records the owner's statement and is not itself a ledger `ruling`; the owner MAY append one.
