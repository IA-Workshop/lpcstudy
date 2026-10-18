# WU-0004c: the `gpu` reproducibility test (owner ruling B10)

| Field | Value |
| --- | --- |
| Status | in progress |
| Class | CSQ3 development |
| Agent(s) | claude-sonnet-5-5 (developer) |
| Estimate | S: one test file, one GPU run of about 10 to 15 minutes (two smoke runs, each measured about 4x slower on the GPU than on the CPU) |

## Plan (written before execution)

- **Origin.** Owner ruling B10 (amendments note `docs/agent/notes/2026-10-11-amendments-for-owner.md` section 35): "write `tests/gpu/test_reproducibility.py` (smoke twice on the GPU against the declared tolerance, after the WU-0003.6 decision); the owner edits the ROADMAP row to what was done". ROADMAP rows WU-0003.4 (line 176) and its definition of done (line 187); WU-0003 plan amendment 1 item A6 (reproducibility tiers); draft decision `docs/agent/notes/2026-10-18-owner-decision-drafts.md` section 1 (item 1: same context, same device type, same host, code, seed and environment is tier T0, bitwise).
- **Scope in.** One new file, `tests/gpu/test_reproducibility.py` (the `gpu` tier has no test today; the tier marker comes from the directory, `tests/conftest.py`). The test runs the smoke preset on development seed DEV-0 twice on the GPU with identical settings and compares the two `results.json` files.
- **Scope out.** Any comparison between GPU and CPU (the cross-device rule is the TD statistic of `tools/compare_runs.py`, not a per-leaf tolerance; it is decided and tested elsewhere). Any change to `lpcstudy/`, to `tools/`, to the ROADMAP row (the owner's edit), to governance, `seeds/` or `docs/study/`. The sealed seed and `--confirmatory`: never touched; the smoke preset on DEV-0 only. No merge.
- **Definition of done.** The test file exists and carries a docstring that states the declared tolerance and its justification, names the independent reference, and (when run) prints the measured maximum difference; it skips (does not fail) with a clear message when no GPU backend is available; it has been run once under the GPU lock through `tools/run_tests.sh gpu tests/gpu/test_reproducibility.py` and its summary line and measured difference are in this Log; branch committed, not merged.
- **Acceptance criteria (fixed now, VV.3).**
  1. **Reference.** The first run against the second run of the same code and settings (the pair is its own reference: the claim is the equality of two executions, not a value). The comparison is computed by the test itself, by a walk of the two JSON trees and an IEEE-bytes comparison of every float, independent of `tools/compare_runs.py`.
  2. **Declared tolerance.** Bitwise: maximum absolute difference 0.0 and maximum relative difference 0.0 over every leaf except timing (any key `seconds`) and the top-level `provenance` block; no leaf present on one side only; no integer, boolean, string or null leaf different. Source: draft decision section 1, item 1 (tier T0: "bitwise"), measured fact R1 against R2 (DEV-1 pilot, GPU, 20,533 of 20,533 leaves equal). The tolerance is not chosen from the result and is not loosened if the test fails (PRIME.2): a failure is a finding (a nondeterminism measurement; open a DEF).
  3. **Identical settings.** The test asserts that the two `provenance` blocks agree on `seed_id`, `seed_kind`, `preset`, `config`, `commit`, `dirty`, `device`, `env`, `packages`, so that "identical settings" is checked rather than assumed; and that the backend recorded is a GPU backend, the seed id is DEV-0 and the seed kind is `development`.
  4. **Not degenerate.** More than 1,000 compared leaves, of which more than 1,000 are floats (the measured smoke has about 13.8 thousand leaves), so that an empty tree cannot pass.
  5. **Tier.** `tools/compare_runs.py` is imported (its `compare_trees`) and classifies the pair: tier `T0`, no differing leaf, no one-sided leaf, exit code 0. Information only beyond that; no assertion on any cross-device quantity.
  6. **Skip, not fail, without a GPU.** A probe subprocess asks jax for a `gpu` device; a missing GPU backend skips with the probe's message. Any other probe failure (jax missing or broken) fails.
  7. **Output.** The measured maximum absolute and relative differences, the number of leaves compared and different, the tier, the exit code of the comparison and the wall-clock time of each run are printed with capture disabled and recorded through `record_property`, so they appear in the test output of a passing run.
  8. **No new randomness, no silent handling.** The test draws no random number; it clips, replaces and skips nothing silently (the one skip is the GPU one, with its message).
- **Affected checks (4.2 by hand; `tools/test_impact.py` not run: one new file in `tests/gpu/`, no code under `lpcstudy/` or `tools/` changes).** The new file itself, `gpu` tier, once, under the lock. The `unit` and `integration` tiers are unaffected (nothing they import changes; `tests/unit/test_conftest_markers.py` tests `tier_of` on synthetic paths and does not scan `tests/gpu/`; checked below).
- **Cost.** About 10 to 15 minutes of one GPU (two smoke runs plus a probe), about 0.2 GPU-hours against the LPC.AUTH.3 weekly tally. The test runs `python -m lpcstudy` directly rather than `tools/run_preset.sh`, because the wrapper `tools/run_tests.sh gpu` already holds the lock and `run_preset.sh` would take it again (exit 75); so no `run.meta.json` is written and `tools/gpu_hours.py` does not see these hours. The wall-clock is recorded here for the owner's tally.
- **Owner checkpoint.** None new: the test asserts the tolerance the owner has ruled on (WU-0003.6, to be entered as a decision). The ROADMAP row edit is the owner's.

## Log

<dated entries: what was done, commands, results, commits>
