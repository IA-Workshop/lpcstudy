# DEVELOPMENT_WORKFLOW: how code changes are made, tested, reviewed and merged

**Status:** Draft, proposed by planner (Fable) 2026-10-10 for the human owner's adoption. **Relation to other files:** `ROADMAP.md` is the plan and `docs/agent/records/work/queue.md` is the live status; this file is the cycle every task follows. Where this file and the governance (`docs/agent/governance/`) differ, the governance governs (GOV.38). SHALL, SHOULD and MAY are used as in the governance: SHALL is an obligation, SHOULD a default that needs a recorded reason to depart from, MAY a permission.

## 1. Scope

This file covers every change to `lpcstudy/`, `tests/`, `tools/`, `seeds/`, `requirements.txt` and the records under `docs/agent/records/`. It does not cover the study documents in `docs/study/` (agents do not change criteria; `.claude/rules/study-docs.md`) or governance (owner only, GOV.49).

## 2. Roles and the cycle

Every unit of work (LPC.PC.9) goes through the steps below. A sub-task `WU-nnnn.k` of `ROADMAP.md` is a unit for this purpose.

### 2.1 Planner

The planner SHALL write the unit's `## Plan` before any code changes: scope in and out, definition of done, acceptance criteria with references and tolerances, affected checks, owner checkpoints (QA.1, VV.3, LPC.AI.6). The acceptance criteria are fixed once execution starts; after that they change only by an appended, dated amendment that keeps the original (`.claude/rules/records.md`), and never after a result is seen (PRIME.2). The planner SHALL state the blast-radius test set of §4.2 in "Affected checks". The planner runs no tests and no computations.

### 2.2 Developer, with self-check

The developer implements the plan: failing test first, with an independent reference (skill `numerical-test`, LPC.PC.21), then the simplest change (SIMPL.1). Before requesting review the developer SHALL do a self-check and log it in `## Log`:

1. re-read the full diff (`git diff main...HEAD` plus the working tree) against the plan, item by item;
2. compute the blast radius (§4.2) and run exactly that set through `tools/run_tests.sh`, once;
3. grep the diff for `clip`, `nan_to_num`, `isfinite`, `where(`, `try:` and `except` and confirm every site is counted and reported (PRIME.4, NVVUQ.11);
4. grep the diff for `default_rng`, `random.`, `PRNGKey` and confirm randomness comes only from `make_rng` with the run's master seed, or from a fixed seed inside a test (LPC.AI.9);
5. confirm no tolerance, reference or criterion was loosened (compare every numeric literal in a changed `assert` or `approx` with the plan);
6. fix its own defects, then commit (§3) and hand back: what changed, the test command and its summary line, what is open.

The developer SHALL NOT request review with a known failing test, an unrun radius, or an uncounted special value.

### 2.3 Reviewer, without prior context

Review is independent (QA.7, LPC.PC.11, LPC.AI.7). The main session runs `/independent-review WU-nnnn`, which forks a fresh `reviewer` subagent given only the diff, the unit file and the governance. The reviewer SHALL run the blast-radius set itself, once, and paste the summary line. The reviewer never edits code.

**Routing findings back.** The reviewer writes `## Review` in the unit file: its identity, a verdict (`approve`, `approve with fixes`, `changes required`) and numbered findings `R1`, `R2`, ... each with file, line, why it matters and the fix. The main session then resumes **the developer agent that implemented the change** (the same subagent, by `SendMessage` or resume; if that agent is gone, a new developer given the unit file and the diff) with the message "address R1–Rn in `## Review` of WU-nnnn". The developer SHALL answer every finding in the unit file, under the finding, as `fixed in <commit>` or `disputed: <reason>`, and SHALL NOT dispute a finding that names a governance provision without a referral. A re-review covers only the fixed and disputed findings and is a new fresh reviewer context.

**Rounds.** At most two fix rounds after the initial review (three reviewer contexts in all). If findings remain, or the same finding recurs, the main session SHALL stop the unit and refer it to the owner with the LPC.AI.13 statement (§5). A finding that identifies a wrong acceptance criterion is never fixed by changing the criterion: it is recorded as a decision for the owner (QA.6).

**Merge.** After `approve`, or `approve with fixes` with every finding resolved, the main session merges to `main` (§3). Code that computes a verdict, statistic or acceptance criterion, seed and provenance code, and dependency additions are additionally marked `needs owner review before freeze` in `queue.md`; they merge now and the owner reviews before the freeze (LPC.PC.11). The merge is a gate: the whole `unit` and `integration` tiers run there, once, by the main session (§4.3), and nowhere else during development.

### 2.4 Auditor

The `critical-elite-auditor` reviews the whole, not one diff: cross-unit consistency, conformance to the v3 design and the decision-log map, governance, NVVUQ, pre-registration integrity. The owner directs the scope with `/audit <scope>`: the full feature set of a phase, or the full codebase. Audits happen:

- at the end of each phase of `ROADMAP.md` (A to D), on the merged `main`;
- before the freeze (`/audit freeze`, WU-0004.4), full codebase;
- before promotion (`/audit promotion`, WU-0018.1), the report and results;
- on request.

The auditor writes `docs/agent/records/audits/<date>-<scope>.md` and edits nothing else. Each blocker becomes a `DEF-nnnn` (LPC.PC.14) and a unit in the queue. A phase does not close with an open blocker.

### 2.5 Specialized agents and their triggers

| Agent | SHALL be dispatched when | Output |
| --- | --- | --- |
| `applied-mathematician` | A plan or change involves a derivation, a numerical method, a statistical procedure, a tolerance, a Monte Carlo error statement, a projection, or a theorem hypothesis (LPC.PC.21b, NVVUQ.5–7, NVVUQ.14). In `ROADMAP.md` this is every task that names it. | `## Mathematics review` in the unit file, before execution; it MAY tighten a tolerance, never loosen one |
| `researcher` | An external fact is needed: a citation, a published reference value, library or method documentation (VV.2, LPC.AUTH.2). No other agent fetches anything (PRIME.12); the web gate hook enforces it. | A note under `docs/agent/notes/` with status per claim |
| `reviewer` | Every change, before merge (§2.3). | `## Review` |
| `critical-elite-auditor` | §2.4. | audit file |

Subagents do not spawn subagents (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1`); the main session orchestrates.

### 2.6 The owner

The owner adopts governance, answers referrals, and performs the checkpoints listed in `ROADMAP.md` §4: reviews of verdict, statistics, seed and provenance code and dependencies before the freeze; the sample-size and tolerance decisions; the freeze; the per-action authorizations of the confirmatory run and the regeneration; promotion. Agents SHALL batch questions into one referral per unit and continue with other units while it is pending (LPC.PC.24).

## 3. Commits, branches and worktrees

- **Branches.** One branch per unit or sub-task, named `wu/<nnnn>-<k>-<slug>`, from `main`. `main` receives only reviewed merges (LPC.PC.11). Merges are ordinary merge commits (`git merge` is under "ask" in `.claude/settings.json`; the owner approves at the prompt).
- **Commits.** Small and often. The message says what and why, names `WU-nnnn`, and ends with `Agent: <model id>` for agent commits (LPC.AI.8). Results directories are never committed unless `results-manifest.md` lists them.
- **No history rewrite.** No `--amend`, `rebase`, `reset --hard`, `filter-branch` or force push, ever (LPC.AI.5, LPC.RAR.2). A mistake gets a new commit. A merge conflict is resolved in a merge commit.
- **Worktrees.** Parallel agents SHALL use `git worktree add ../lpcstudy-wt/<branch> <branch>`; one worktree per branch. Each worktree has its own `runs/` and `.pytest_cache/`. All worktrees share the one GPU lock (§4.5), the one weekly GPU-hour tally and the one ledger (the ledger lives on `main`; a worktree appends only `proposal` and `note` entries and merges them). Two agents SHALL NOT edit the same function in parallel; the main session assigns disjoint sub-tasks (`ROADMAP.md` §3, lanes).
- **Records.** Append-only (`.claude/rules/records.md`). A worktree's unit file is merged with the branch.

## 4. Test discipline

This section is strict because the suites will grow and agents share one machine. The rule is: **run the smallest set that establishes the evidence, once, on the right device, with bounded threads and time** (LPC.PC.12, RSRC.11, RSRC.12).

### 4.1 Tiers

Markers are registered in `pytest.ini` with `--strict-markers` and applied by `tests/conftest.py` from the directory (WU-0010.1).

| Tier (marker) | Where | What | Budget | Device | Who may run | When |
| --- | --- | --- | --- | --- | --- | --- |
| `unit` | `tests/unit/test_<module>.py` | Fast reference tests of one module | under 5 s each; whole tier under 2 min | CPU only (`JAX_PLATFORMS=cpu`) | any agent | the blast-radius subset per change; the whole tier at gates |
| `integration` | `tests/integration/` | Smoke-level end-to-end runs (`python -m lpcstudy --preset smoke`, CLI refusals) | under 5 min each | CPU only | any agent | when the pipeline is touched (§4.2); at gates |
| `slow` | `tests/slow/` | Coverage and size simulations, convergence studies, the P2 bound on a cell | under 30 min for the tier | CPU only | developer or reviewer of the unit that owns the test, once per change to the statistic under test; main session at gates | WU-0006 and WU-0005.5 changes; gates |
| `gpu` | `tests/gpu/` | Reproducibility and device checks | under 30 min for the tier | GPU, under the lock | developer of WU-0003; main session at the freeze | WU-0003.4; the freeze gate |

Every test under `tests/unit/` SHALL finish in under 5 s (`.claude/rules/tests.md`); a test that cannot moves to `slow` with a reason in its docstring. The current suite is 14 tests in `tests/test_core.py`, 4.8 s on this bundle's 2-core CPU; the longest single test, `test_observability_matches_independent_jacobians`, takes 2.5 s.

### 4.2 The mandatory blast-radius-only check

Before any test invocation an agent SHALL compute the set of tests its change can affect and run only that set. "Run the suite to be safe" is forbidden outside the gates of §4.3.

**Change set.** `git diff --name-only <base>...HEAD` plus the working tree (`git status --porcelain`, including untracked files), where `<base>` is `main`.

**Module dependency graph of `lpcstudy/`** (from the `from .x import` statements, including function-level imports; the fixture of WU-0011.2 is the reference):

| Module | Imports from | Direct dependents |
| --- | --- | --- |
| `config` | — | `data`, `pipeline`, `analysis`, `experiments`, `report`, `__main__` |
| `systems` | — | `data`, `oracle`, `validation`, `pipeline` |
| `embedding` | — | `data`, `ensemble` |
| `dynamics` | — | `estimation`, `ensemble`, `oracle`, `validation`, `experiments` |
| `networks` | — | `estimation`, `allocation`, `pipeline` |
| `statistics` | — | `allocation`, `analysis`, `experiments`, `validation`, `pipeline` |
| `data` | `config`, `embedding`, `systems` | `estimation`, `ensemble`, `oracle`, `validation`, `pipeline` |
| `estimation` | `data`, `dynamics`, `networks` | `ensemble`, `pipeline` |
| `ensemble` | `data`, `dynamics`, `embedding`, `estimation` | `oracle`, `allocation`, `validation`, `pipeline`, `experiments` |
| `oracle` | `data`, `dynamics`, `ensemble`, `systems` | `allocation`, `analysis`, `validation`, `pipeline`, `experiments` |
| `allocation` | `ensemble`, `networks`, `oracle`, `statistics` | `analysis`, `pipeline`, `experiments`, `report` |
| `validation` | `data`, `dynamics`, `ensemble`, `oracle`, `statistics`, `systems` | `experiments` |
| `pipeline` | `allocation`, `config`, `data`, `ensemble`, `estimation`, `networks`, `oracle`, `statistics`, `systems` | `analysis`, `experiments`, `__main__` |
| `analysis` | `allocation`, `config`, `oracle`, `pipeline`, `statistics` | `experiments` |
| `experiments` | `analysis`, `allocation`, `config`, `dynamics`, `ensemble`, `oracle`, `pipeline`, `statistics`, `validation` | `__main__` |
| `report` | `allocation`, `config` | `__main__` |
| `__main__` | `config`, `experiments`, `pipeline`, `report` | — |

**Mapping rules**, applied per changed file, union over the change set:

| Changed file | Tests to run |
| --- | --- |
| `lpcstudy/<m>.py`, `<m>` not a core module | `tests/unit/test_<m>.py` plus `tests/unit/test_<d>.py` for each direct dependent `<d>` |
| `lpcstudy/<m>.py`, `<m>` a **core module**: `config`, `data`, `systems`, `dynamics`, `statistics`, `ensemble`, `oracle` | `tests/unit/test_<m>.py` plus the unit tests of every transitive dependent, plus `tests/integration/` |
| `lpcstudy/pipeline.py`, `experiments.py`, `report.py`, `__main__.py` ("the pipeline is touched", LPC.PC.12) | own and direct dependents' unit tests, plus `tests/integration/` |
| `tests/unit/test_x.py` or any single test file | that file only |
| `tests/conftest.py`, `pytest.ini` | the whole `unit` tier (a gate-sized run; say so in the log) |
| `tools/<t>.py` or `tools/<t>.sh` | `tests/unit/test_tools_<t>.py` if it exists; otherwise none, with a warning that the tool has no test |
| `seeds/development_seeds.json` | `tests/unit/test_seeds.py` and `tests/integration/test_cli_seeds.py` (after WU-0001) |
| `requirements.txt` | the whole `unit` tier plus `tests/integration/`, run once by the main session; the change is a recorded decision (LPC.PC.17) |
| `docs/**`, `.claude/**`, `README.md`, `ROADMAP.md`, this file, `seeds/README.md` | **no tests** |
| A statistic that `tests/slow/` verifies (`statistics.py`, the bootstrap, log-rank, Holm, ΔR², verdict rules) | the rules above plus the `slow` test that owns that statistic, once |

The smoke preset run by hand and `tests/integration/test_smoke_pipeline.py` (WU-0010.3) are the same evidence: run one of them, not both.

**Unknown mapping.** A new module, or a file the rules do not name: run its own test file if one exists plus the unit tests of its direct dependents from the graph, and say in the log that the default was used. Never the whole suite.

**The tool.** `tools/test_impact.py` (WU-0011) implements the rules: it prints the selected files, the tier, the reasons with `--explain`, and the exact command; `--run` executes it through `tools/run_tests.sh`. It never selects `slow` or `gpu` without `--include-slow` or `--include-gpu`. **Until it exists**, the agent SHALL apply the two tables above by hand and write the derived set and the reason into the unit's `## Log` before running. While the suite is still `tests/test_core.py` (before WU-0010.2), the radius for any `lpcstudy/` change is that one file, 5 s, plus the smoke preset when the pipeline is touched; that is already the smallest set.

### 4.3 When the full suite may run

The full suite (`unit`, `integration` and `slow` on CPU; `gpu` on the GPU) runs only at these gates, once per gate, by the named role, with the output pasted into the unit file or checklist:

| Gate | Who | Tiers |
| --- | --- | --- |
| Merge of a reviewed branch to `main` | main session | `unit` and `integration` |
| End of a roadmap phase | main session, before `/audit` | `unit`, `integration`, `slow` |
| The freeze (WU-0004.2) | main session, then the owner may repeat | all four |
| Promotion (WU-0018) | auditor, on the frozen commit, only if the environment changed since the freeze | all four |

Anyone else who believes the full suite is needed refers it. "I changed a core module" is not a reason: the core-module rule of §4.2 already expands the radius.

### 4.4 No repeated runs

Running the same test twice without a code change between the runs is forbidden. The one exception is a deliberate flakiness or nondeterminism measurement: it is planned, states the number of repetitions in advance, records every outcome in the unit file, and opens a `DEF-nnnn` if outcomes differ. "Retry until green" is a PRIME.2 violation and a DEF against the agent's log, not a pass. On a failure, fix the code, then rerun only the failing test with `--lf` (§4.6); the radius runs again only after the fix, once.

### 4.5 Resource contention

One workstation, one GPU, several agents. These rules apply to every test and every preset run, through `tools/run_tests.sh` and `tools/run_preset.sh` (WU-0012); before those exist, the agent SHALL set the same variables by hand and record them.

- **CPU-only tiers never touch the GPU.** `unit`, `integration` and `slow` run with `JAX_PLATFORMS=cpu`. `tests/conftest.py` fails any test outside `tests/gpu/` that requests a GPU device.
- **No preallocation.** Whenever the GPU is used, `XLA_PYTHON_CLIENT_PREALLOCATE=false`, so a smoke check or a `gpu` test does not take the card's memory from a running job.
- **One GPU job at a time, across all agents and worktrees.** Every GPU job runs under `flock` on `/tmp/lpcstudy-gpu.lock` (override with `LPC_GPU_LOCK`). A preset run uses `flock -n`: if the lock is held it exits 75 at once, the agent logs "GPU busy" and continues with other work, polling later. A `gpu` test waits at most 30 s (`flock -w 30`) and then exits 75. No agent waits in a loop on the lock; a busy GPU is a reason to do something else.
- **Thread cap.** Every test run and CPU preset run sets `OMP_NUM_THREADS`, `MKL_NUM_THREADS` and `OPENBLAS_NUM_THREADS` to `LPC_THREADS` (default 4) and passes the same count to XLA's CPU thread flag through `XLA_FLAGS` (the wrapper sets it; WU-0012.1 verifies that observed CPU use stays within the cap). The CPU regression run (WU-0002.12) uses `LPC_THREADS=8`. At most four agent test runs are active at once; the main session assigns the budget. `pytest-xdist` is not a dependency and `-n` is not used.
- **Long runs in the background.** `pilot` and `full` presets, the `slow` tier and the `gpu` tier start with `nohup ... &` through the wrapper, which prints the PID and the log path. The agent polls `tail -n 5 <log>` or `grep -c finished <log>` at intervals of minutes, never streams the log into its context, and never blocks a tool call on the run.
- **Never start a preset while a heavy run is active.** Before `pilot`, `full`, `slow` or `gpu`, check `pgrep -f "lpcstudy --preset (pilot|full)"` and the lock; if either is busy, do not start. The smoke preset on CPU MAY run alongside a GPU job because it holds no lock and uses at most `LPC_THREADS` threads.
- **Compute limits.** `pilot` and `full` run only on registered development seeds, one at a time, under 12 h each (`timeout 12h` in the wrapper), within 60 GPU-hours per week (`tools/gpu_hours.py` refuses a start that would pass it), and the wall-clock is recorded in `run.meta.json` and the unit file (LPC.AUTH.3, LPC.PC.22).
- **Timeouts.** `tools/run_tests.sh` wraps pytest in coreutils `timeout`: `unit` 300 s, `integration` 900 s, `slow` 3600 s, `gpu` 1800 s. A timeout is a failure to investigate, not a reason to raise the limit; raising a limit is a plan amendment.

### 4.6 Output discipline

- Quiet runs: `-q --tb=short -rfE`. The agent reads the last lines of the output (the summary and the `FAILED`/`ERROR` lines) and records in the unit file only the summary line and the failures. Full tracebacks are read with `--tb=long` only for the failing test, after `--lf`.
- On failure: rerun only the failing test, `pytest --lf -q --tb=short <file>`, not the radius; the radius runs again once after the fix (§4.4).
- Never `-s`, never `-v` across a tier, never `--durations` except once per unit to justify a `slow` move.
- Preset runs: the agent reads `run.log` by `tail` and the gate flags from `results.json` with a one-line `python -c`, not the whole file.

### 4.7 Statistical and stochastic tests

- Fixed seeds, from `make_rng(seed, "test", <name>)` or `np.random.default_rng(<int>)` in the test (`.claude/rules/tests.md`).
- Each test states its Monte Carlo error in its docstring and sets its tolerance above it: for a coverage p from R replications, `z·sqrt(p(1 − p)/R)`; for a mean, `z·sd/sqrt(R)` (skill `numerical-test`). WU-0006 uses `z = 3` and states R.
- A coverage, size or convergence simulation is `slow`.
- A statistical test that fails is a finding about the code or about the test's error analysis. Never change the seed, R, the level or the bound to pass (PRIME.2). Record the decision and keep the original (QA.6).

### 4.8 Verification cadence

LPC.PC.12 in practice: per change, the blast-radius set, plus `tests/integration/` when the pipeline is touched; at merge, `unit` and `integration`; at phase end and at the freeze, the gates of §4.3; the DEV-0 regression and the validation gate V1–V7 at the freeze from the recorded rehearsal. Deferral is recorded in the unit file with the gate at which the deferred check runs; **deferral never becomes omission**: the freeze checklist (WU-0004.1) lists every deferred check and the freeze does not proceed with one open.

### 4.9 Test-run checklist

Before every test invocation, the agent answers these in the `## Log`, in one line each:

1. **Change set:** `git diff --name-only main...HEAD` plus `git status --porcelain`: which files?
2. **Radius:** which test files and tier follow from §4.2 (tool output, or the hand-derived set with its rule)? Is it smaller than the whole suite? If not, which gate am I at, and am I the named role?
3. **Already run?** Has this exact set run on this exact code? If yes, stop: no rerun without a change (§4.4).
4. **Device:** `JAX_PLATFORMS=cpu` set, unless `gpu` tier under the lock with `XLA_PYTHON_CLIENT_PREALLOCATE=false`.
5. **Threads and time:** `LPC_THREADS` within the budget; the tier's timeout applies.
6. **Contention:** no `pilot` or `full` run active if this is `slow`, `gpu` or a preset; lock available.
7. **Output:** `-q --tb=short -rfE`; only the summary and failures go into the record.
8. **Command:** the exact command, through `tools/run_tests.sh` (or with the variables set by hand until WU-0012 lands).

## 5. Stopping rule and referral

A unit halts under LPC.PC.10: three attempts at the same failing approach without new information, four hours without measurable progress toward its definition of done, or cost at twice the recorded estimate. The two fix rounds of §2.3 count toward the three attempts. On halting, the agent runs `/refer`, writes the LPC.AI.13 statement in the unit file, sets the unit to `halted` in `queue.md`, leaves the branch committed, and continues with another unit that does not depend on it (LPC.AI.12, LPC.PC.24). It never routes around the block (PRIME.12).

## 6. Owner checkpoints

The owner's checkpoints are listed in `ROADMAP.md` §4. Work marked `needs owner review before freeze` merges to `main` and continues; the owner reviews it in one sitting before the freeze. Referrals and proposals arrive batched per unit, with the options and a recommendation, so each checkpoint costs the owner minutes.
