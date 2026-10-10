# Test and compute discipline (LPC.PC.12, RSRC.11, RSRC.12, PRIME.2)

This file is always loaded. Full rules: `DEVELOPMENT_WORKFLOW.md` §4.

- **IMPORTANT: blast radius only.** Before any test run:
  - compute the affected set from the change set (`git diff --name-only main...HEAD` plus `git status --porcelain`) with `/test-impact`;
  - write the set and the rule into the unit's `## Log`;
  - run only that set.

  Until `tools/test_impact.py` exists (WU-0011), derive the set by hand from §4.2. Whole-suite runs happen only at a gate (merge, phase end, freeze, promotion), by the main session, with `LPC_GATE=<gate>`. A hook blocks them otherwise.
- **Once.** Never run the same test twice without a code change. On a failure: fix, run the failing test with `--lf`, then run the radius once. A flakiness measurement is planned and recorded, never a retry.
- **Tiers:**
  - `unit`: under 5 s each, CPU;
  - `integration`: smoke, CPU;
  - `slow`: coverage and size simulations, CPU, run only by the owner of the statistic;
  - `gpu`: under the lock.

  `tests/test_core.py` is the whole suite until WU-0010 splits it. It takes about 5 s, so it is already the radius for any `lpcstudy/` change.
- **Device and threads.**
  - Settings default to `JAX_PLATFORMS=cpu`, `XLA_PYTHON_CLIENT_PREALLOCATE=false`, and `LPC_THREADS` and `OMP/MKL/OPENBLAS` threads = 4. Do not override them except for GPU work.
  - No `pytest -n`.
- **One GPU job at a time** across all agents and worktrees. Use `tools/run_preset.sh` or, until it exists, `flock -n /tmp/lpcstudy-gpu.lock env JAX_PLATFORMS=cuda XLA_PYTHON_CLIENT_PREALLOCATE=false python -m lpcstudy --preset ...`. Exit 75 or "lock held" means busy: do other work. Never wait or poll in a loop.
- **Heavy runs in the background.** Run `pilot`, `full`, `slow` and `gpu` in the background, and poll with `tail -n 5 <log>`. Never start one while `pgrep -fa "lpcstudy --preset"` shows a run.
- **Quiet output.** Use `-q --tb=short -rfE`. Record only the summary line and the failures.
- **Statistical tests:** fixed seeds, Monte Carlo error stated in the docstring, `slow` marker. Never change the seed, R, the level or the bound to pass.
- **Checklist.** Answer the §4.9 checklist in one line per item in the `## Log` before every invocation.
