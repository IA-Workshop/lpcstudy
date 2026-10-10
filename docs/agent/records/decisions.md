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

## DEC-0004: WU-0001 plan: answers to the planner's questions  (2026-10-10, proposed by claude-sonnet-5-5 (main session); for owner confirmation)

**Decision.** The WU-0001 plan amendment (`docs/agent/records/work/WU-0001-seed-provenance.md`, branch `wu/0001-seeds-provenance`) asks eight questions. Answers, none of which changes a verdict, a statistic or a fixed criterion except where stated:

- *Q1 (WU-0001.5).* The bitwise comparison with the baseline smoke reference removes `provenance`, `seconds`, `handling` **and `config.seed_id`**, and nothing else. `config.seed_id` is a necessary consequence of WU-0001.1; the criterion's "the unit adds nothing else" cannot hold literally. This is a change to how a fixed criterion is checked, not to what it protects: every number must still be bitwise identical.
- *Q2.* `--seed-id` defaults to `DEV-0` when omitted (CLAUDE.md: "until then, runs use DEV-0"), so `tests/integration/test_smoke_pipeline.py` stays valid.
- *Q3.* Development headers carry both the `DEVELOPMENT (DEV-n): not a hypothesis test` label and `UNPROMOTED` (LPC.PC.13).
- *Q4.* The sklearn seed-size defect is `DEF-0010`, to be fixed in WU-0002 after an owner ruling; not in WU-0001.
- *Q5.* Prefer **not** to change `tools/ledger.py`: tests point the ledger readers at a `tmp_path` ledger by monkeypatching the module-level ledger path. Only if that is impossible may the developer add an optional path argument, with its own test and the reviewer's explicit attention.
- *Q6.* Refusing a confirmatory run on a dirty tree or unknown commit is **not implemented** in WU-0001; recorded for the owner to decide before the freeze (WU-0004).
- *Q7.* The test file is `tests/unit/test___main__.py` (the name `tools/test_impact.py` looks for). When `tools/ledger.py` changes, add `test_seeds` by hand (the Q2 gap of DEC-0003). DEVELOPMENT_WORKFLOW §4.2's import-graph table needs rows for the new modules; that is an owner edit (adopted governance).
- *Q8.* The ledger path can be overridden only from Python, never by a flag or environment variable.

**Alternatives weighed.** *Hold WU-0001 until the owner answers:* rejected, since nothing here is irreversible and the owner can override before the owner review that the unit requires anyway.

**Affects:** WU-0001 only. Marked `needs owner review before freeze` (seed and provenance code).

**Dissent and resolution (REPRO.8):** none so far. Status: proposed.

## DEC-0005: WU-0012 plan: answers to the planner's questions  (2026-10-10, proposed by claude-sonnet-5-5 (main session); for owner confirmation)

**Decision.** The WU-0012 plan (`docs/agent/records/work/WU-0012-wrappers.md`, branch `wu/0012-wrappers`) asks six questions. Answers:

- *Q1.* The smoke "same `results.json` as a direct invocation" check excludes the wall-clock `seconds` fields (and, once WU-0001.4 lands, its timing fields): the same reading as WU-0009.3, where the criterion itself removes them.
- *Q2.* "Calendar week" is the ISO week in UTC. A shared append-only tally in addition to the per-run `run.meta.json` files is **not** added in WU-0012; the risk (deleting `runs/` or a worktree loses hours from the count) is recorded for the owner.
- *Q3.* The XLA flag that caps CPU threads in jax 0.11.2 is **not set** in WU-0012 (an unknown `XLA_FLAGS` entry aborts XLA). Finding it needs a `researcher` retrieval; deferred, under the open question of the web-retrieval cap.
- *Q4.* Split the wrapper tests into three files named for the tools, so that `tools/test_impact.py` finds them under the §4.2 pattern: `tests/unit/test_tools_run_tests.py`, `test_tools_run_preset.py`, `test_tools_gpu_hours.py`. (This overrides the plan's single `test_tools_wrappers.py` file name; the criterion's radius names that file, so the log records the substitution.)
- *Q5.* `run.meta.json` does not record peak memory: its field list is fixed by the criterion, and peak RSS goes into the provenance block (WU-0001.4).
- *Q6.* CPU `pilot` and `full` runs (WU-0002.12) take the same lock as GPU runs, so that only one long run is active at a time. The GPU-hour tally counts only runs whose device is a GPU.

**Alternatives weighed.** *Keep one test file and add a mapping line to §4.2 and `test_impact.py`:* rejected, since §4.2 is adopted governance (an owner edit).

**Affects:** WU-0012 only. The seed check and `run.meta.json` need owner review before the freeze (planner's note).

**Dissent and resolution (REPRO.8):** none so far. Status: proposed.
