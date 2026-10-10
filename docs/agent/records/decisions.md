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

## DEC-0003: WU-0011 blast-radius tool follows DEVELOPMENT_WORKFLOW §4.2 as written  (2026-10-10, proposed by claude-sonnet-5-5 (main session); for owner confirmation)

**Decision.** `tools/test_impact.py` implements the §4.2 change classes as the adopted text states them. The planner's six questions (WU-0011 plan, `### Questions for the owner`) are answered so that the tool never selects fewer tests than §4.2 does:

- *Q1.* The core-module list is a designated constant, as §4.2 lists it. It cannot be derived from the import graph (`embedding`, `networks` and `estimation` reach more modules than `statistics` and `oracle` but are not core). Proposal for the owner, not implemented: say in §4.2 that the list is designated.
- *Q2.* **Not implemented; recommended for the owner.** A test file is not also selected when a module it imports directly changes. Consequence under §4.2 as written: a change to `systems` (a core module) does not select `test_dynamics.py` or `test_embedding.py`, which import `lpcstudy.systems`. The extra rule would only add tests (about 1 s of selection), so I recommend adopting it by a dated amendment to §4.2; until then the tool follows §4.2, and the gap is recorded in the WU-0011 log.
- *Q3.* A `description` field in the JSON fixture plus the comparison test's docstring satisfy "fixture docstring names it as the independent reference".
- *Q4.* "Leaf module" in criterion (a) means "not a core module" (§4.2).
- *Q5.* When a changed test file is under `tests/slow/` or `tests/gpu/`, criterion (g) wins: it is not selected without `--include-slow` or `--include-gpu`, and the tool prints an `excluded` line.
- *Q6.* `--run` delegates to `tools/run_tests.sh` when it exists (WU-0012.1) and otherwise sets the environment by hand. The skill's `2>/dev/null || echo` fallback hides the tool's errors; the owner may edit it (`.claude/` is not mine to change).

**Alternatives weighed and why rejected.** *Derive the core list from the graph:* every graph rule tried gives either a list unlike §4.2 or 11 core modules (integration run on almost every change). *Implement Q2 now:* it changes §4.2's behavior, which is adopted governance (GOV.49).

**Affects:** WU-0011 only. The risk in Q2 is under-selection, not over-selection.

**Dissent and resolution (REPRO.8):** none so far. Status: proposed.
