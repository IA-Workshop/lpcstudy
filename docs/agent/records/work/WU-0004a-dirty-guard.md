# WU-0004a: refuse a sealed run on a dirty tree or an unknown commit (B8)

| Field | Value |
| --- | --- |
| Status | implemented; pending independent review and owner review |
| Class | CSQ3 development (code and unit tests only; no sealed run, no sealed seed) |
| Agent(s) | claude-sonnet-5-5 (developer) |
| Estimate | S |

## Plan (written before execution)

- **Source of the requirement.** Owner ruling B8 of 2026-10-18 (`docs/agent/notes/2026-10-11-amendments-for-owner.md` section 35: "implement the dirty-tree and unknown-commit refusal for the sealed run (code, tests, independent review, then the owner's review); VmHWM recording optional"); DEC-0008 C (decide "at the pre-freeze review"); `docs/agent/notes/2026-10-18-freeze-blockers.md` B8. Branch `wu/0004a-dirty-guard` from develop 7b6f6e6.
- **Scope in.** One new guard in `lpcstudy/__main__.py`, `choose_clean_tree(args)`, called in `main` after the two existing option guards (`choose_refine_steps`, `choose_states_dump`) and **before** `choose_seed` (the only place the sealed seed is read). It acts only when the sealed flag is given. It reads the repository state with `provenance.git_state(provenance.ROOT)` (the same reader that fills `commit` and `dirty` in the provenance block) and refuses, as a `SeedRefusal` (exit 64, one stderr line `lpcstudy: refused (LPC.PC.7): <reason>`, nothing created), when:
  1. the commit is not known: `commit` is `None`, empty, or not a full hexadecimal object name (40 or 64 characters), or `dirty` is `None` (git failed, so cleanliness is unknown); or
  2. the tree is dirty: `dirty` is `True` (`git status --porcelain` is non-empty, so untracked files count).
  The reason never echoes git's error text (it can hold newlines and paths). Development runs (`DEV-n`) are untouched: the guard does not call git for them.
- **Scope out.** The seal script, the seed registry, the ledger, `seeds/`, governance, `.claude/`. No sealed run, no real sealed seed, no real run with the sealed flag. No check that the commit is the *tagged* freeze commit (the ruling says clean and known; the tag does not exist yet; see Q1). `VmHWM`: see Q2 (decision below).
- **Definition of done.**
  1. A sealed request on a dirty tree, or with an unknown or unreadable commit, exits 64 with exactly one stderr line, before `confirmatory_seed` is called, before `provenance.collect`, and before any output directory is created; the line holds neither the seed nor the salt nor git's error text.
  2. A sealed request on a clean tree with a known commit behaves as before (the seed is read once; the faked run completes; the block records `dirty` false).
  3. A development run on a dirty tree behaves as before (the block records `dirty` true).
  4. Every existing guard keeps its own message and order: the knob and dump refusals (checked first) still name their flag on a dirty tree; `--seed-id` with the sealed flag, a raw seed and a missing or mismatched commitment are still refused.
  5. Unit tests as in the acceptance criteria pass; the unit radius is run once.
- **Acceptance criteria (fixed now, VV.3).** All asserts are exact (exit codes, strings, call lists); there is no numerical tolerance. References are hand-written: the expected message strings below and the expected call order, independent of the code.
  - **A1 (refusal table).** For each git state in {dirty `("a"*40, True, None)`; unknown commit `(None, None, "RuntimeError: boom\nsecond line")`; `(None, False, None)`; `("", False, None)`; `("unknown", False, None)`; short hash `("abc1234", False, None)`; dirty flag unknown `("a"*40, None, None)`} and for the argument shapes {sealed; sealed with `--report-only`}: `main` returns 64; stderr is exactly one line equal to the expected string (dirty: `lpcstudy: refused (LPC.PC.7): the confirmatory flag needs a clean working tree (git status --porcelain is not empty); commit or remove the changes first`; the other six: `lpcstudy: refused (LPC.PC.7): the confirmatory flag needs a known commit and a readable git state (commit unknown or git unavailable)`; the plan's first draft of this wording was shortened when the tests were written, before the guard code existed; no criterion changed); a spy on `confirmatory_seed` and on `provenance.collect` is never called; the out directory does not exist; the env seed and salt, and the strings `boom` and `second line`, are not in stderr.
  - **A2 (order).** With a clean state, the first two recorded calls are `git_state(provenance.ROOT)` then `confirmatory_seed`: git is read first.
  - **A3 (clean sealed run unchanged).** Under the autouse clean state the existing `test_confirmatory_run_writes_no_seed_value` passes unmodified; plus a test asserting the saved block holds the pinned commit and `dirty` false.
  - **A4 (development unaffected).** `("a"*40, True, None)` with the default DEV seed: the fake run completes, seed 20261005 is used, the saved block has `dirty` true, and the guard did not call `git_state` itself (one call, from `collect`).
  - **A5 (existing guards first).** On a dirty tree, the sealed flag with `--estimator-refine-steps 30` and with `--states-dump` give the existing lines (they name their flag and say "confirmatory flag"), not the dirty-tree line.
  - **A6 (function level).** `choose_clean_tree` returns `None` for a clean known state and does not call git when the flag is absent (spy that fails if called).
  - **A7 (no tolerance changed).** `git diff` shows no `assert` or `approx` loosened; the only edits to existing tests are the ones named in the Log with their reason (an autouse clean-tree fixture, so the existing sealed tests do not depend on the state of the checkout the suite runs in; the integration driver likewise).
- **Affected checks (hand-derived, DEVELOPMENT_WORKFLOW.md 4.2).** Changed code: `lpcstudy/__main__.py` only. Tests that import `__main__` (or run it): `tests/unit/test___main__.py` (and, integration tier, `test_cli_seeds.py`, `test_states_dump.py`, `test_smoke_pipeline.py`, `test_preset_wrapper.py`, which the main session runs; not run by this unit). Tests that read the source of `lpcstudy/*.py` (scan rule): see the Log (computed with `tools/test_impact.py`). `lpcstudy/` changed, so a DEV-0 smoke neutrality check (C16) follows, run by the main session.
- **Owner checkpoints (LPC.PC.11):** **needs owner review before freeze** (seed and provenance code; the guard sits beside the seed guard).
- **Open questions for the owner (answered with the stricter or cheaper option, flagged).**
  - **Q1.** The blocker note reads "unless `dirty` is false and the commit is the tagged one". The ruling and this task say clean and known. Default: no tag check (the tag `freeze-1` does not exist yet and a tag check needs the tag name decided; the manual WU-0015.1 check "working tree clean at `freeze-1`" stays). A tag check is a small follow-up: compare `commit` with `git rev-parse freeze-1^{commit}`.
  - **Q2.** `VmHWM` (optional). Default: **not added**. Reason: recording it adds a key to the provenance block; the exact-key-set test (`tests/unit/test_provenance.py`, `KEYS`/`END_KEYS`) and two integration run-specific key lists (`test_preset_wrapper.py`, `test_states_dump.py`) would change, and the integration tier is not run in this unit. `run.meta.json` is written by the shell wrapper `tools/run_preset.sh`, which cannot see the child's `VmHWM` after it exits. Proposal if wanted: a separate unit adding `vm_hwm_bytes` (Linux `/proc/self/status`, `null` elsewhere) to `provenance.finish`, with the key lists updated and the integration tier run.

## Log

- **2026-10-18, claude-sonnet-5-5 (developer), implementation.** Worktree `lpcstudy-wt/wu/0004a-dirty-guard`, branch `wu/0004a-dirty-guard` from develop 7b6f6e6. Plan written first (above). Tests written before the guard: `tests/unit/test___main__.py` gets an autouse `_clean_tree` fixture and the A1 to A6 tests (new section at the end). Then `choose_clean_tree` in `lpcstudy/__main__.py` and its call in `main` between `choose_states_dump` and `choose_seed`.
  - **Edits to existing tests, and why (A7).** (1) `tests/unit/test___main__.py`: the autouse `_clean_tree` fixture pins `provenance.git_state` to a clean tree at a 40-hex commit for every test. Reason: the existing sealed-flag tests (`test_confirmatory_run_writes_no_seed_value`, `test_confirmatory_refusals_in_process`, `test_mismatched_commitment_in_process`, the faked sealed runs) would otherwise depend on whether the checkout is clean (a dirty checkout would make them test the new refusal instead of their own). No assertion, tolerance or expected value of an existing test changed. (2) `tests/integration/test_cli_seeds.py`: `DRIVER` pins `provenance.git_state` the same way, for the same reason (the subprocess runs in the repository checkout). The string was parsed with `ast` to check the syntax; the integration tier was **not run** (instruction), so this edit is unrun until the main session runs the tier.
  - **Self-check.** `git diff -U0 lpcstudy | grep -E "clip|nan_to_num|isfinite|where\(|try:|except|default_rng|random\.|PRNGKey"`: no match (no clip, replacement, fallback or randomness added; the one refusal is a raised `SeedRefusal`, printed as the one-line exit 64, so it is reported, not silent). `git diff -U0 tests | grep -E "approx|atol|rtol"`: no match (no tolerance anywhere). Message of the git failure is deliberately not echoed (test A1 checks that `boom` and `second line` are absent).
  - **Radius (tool, `tools/test_impact.py --base develop --explain`, agrees with the hand derivation of 4.2).** Change set: `lpcstudy/__main__.py` (rules: pipeline module, direct importers, source-scanning tests), `tests/unit/test___main__.py`, `tests/integration/test_cli_seeds.py`, this file. Unit set: `tests/unit/test___main__.py tests/unit/test_data.py tests/unit/test_identifiers.py tests/unit/test_rng_hygiene.py tests/unit/test_tools_test_impact.py`. Integration tier (`tests/integration`) is selected by the tool and is left to the main session (instruction: not run here). `provenance.py` is unchanged, so `test_provenance.py` is not in the radius.
- **2026-10-18, pre-run checklist (DEVELOPMENT_WORKFLOW.md 4.9), run 1.**
  1. Change set: `M lpcstudy/__main__.py`, `M tests/integration/test_cli_seeds.py`, `M tests/unit/test___main__.py`, `?? docs/agent/records/work/WU-0004a-dirty-guard.md` (and `queue.md` to follow); `git diff --name-only main...HEAD`: none yet on this branch beyond develop.
  2. Radius: the five unit files above (tool output, rule "pipeline module / direct import / scan the source"); much smaller than the whole suite.
  3. Already run? No: first invocation on this code.
  4. Device: the wrapper sets `JAX_PLATFORMS=cpu`, `XLA_PYTHON_CLIENT_PREALLOCATE=false`.
  5. Threads and time: `LPC_THREADS` default 4; unit timeout 300 s.
  6. Contention: no preset run is started by this unit; CPU only.
  7. Output: the wrapper adds `-q --tb=short -rfE`; only the summary and failures are recorded.
  8. Command: `tools/run_tests.sh unit tests/unit/test___main__.py tests/unit/test_data.py tests/unit/test_identifiers.py tests/unit/test_rng_hygiene.py tests/unit/test_tools_test_impact.py`.

- **2026-10-18, run 1 result.** `LPC_PYTHON=<main repo .venv python> tools/run_tests.sh unit tests/unit/test___main__.py tests/unit/test_data.py tests/unit/test_identifiers.py tests/unit/test_rng_hygiene.py tests/unit/test_tools_test_impact.py` -> `184 passed in 10.69s` (once; the worktree has no `.venv`, so the interpreter was selected with `LPC_PYTHON`; the tests import the worktree code, shown by the new tests importing `choose_clean_tree`). No failure, no `--lf`. Not run: the integration tier (the tool selects it; the `test_cli_seeds.py` driver edit and the faked-run tests in `test_states_dump.py`, `test_smoke_pipeline.py`, `test_preset_wrapper.py` are for the main session), the DEV-0 smoke neutrality check (C16, main session), `test_provenance.py` (provenance.py unchanged).
- **Evidence summary for the criteria.** A1 14 cases (7 states x run/report-only) pass; A2/A3 call order `[git, seed, collect, git]` and block commit/dirty; A4 `[collect, git]` and `dirty` true on a dev run; A5 both existing guards keep their lines and git is not read; A6 function level; plus 5 cases against the real `git_state` on throwaway repositories (clean, untracked, modified, no commit, not a repository). Mutation check not run (it would be a rerun without a code change to the product).

## Review

- **Reviewer:** `reviewer`, claude-opus-5-5 (fresh context), 2026-10-18.
- **Findings and resolution:** round 1 in `WU-0004a-review.md`. The verdict is **approve with fixes**, with 3 findings:
  - R1 (medium): the guard-to-`collect` window, and a docstring claim that the provenance block records exactly what was checked;
  - R2 (low): the clean reading depends on git config and environment (`status.showUntrackedFiles`, skip-worktree, `GIT_DIR`);
  - R3 (low): the Q1 tag-check follow-up is not registered.

  Open; all three go back to the developer. The unit still needs owner review before freeze.

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:

## Referral

<only if halted>
