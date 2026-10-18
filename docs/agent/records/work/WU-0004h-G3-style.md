# WU-0004h-G3: owner's code review of 2026-10-18, group G3 (allocation, ensemble, experiments)

| Field | Value |
| --- | --- |
| Status | done (pending review) |
| Class | CSQ3 development |
| Agent(s) | claude-sonnet-5-5 |
| Estimate | small (style only; no numeric change) |

## Plan (written before execution)

- **Scope:** `lpcstudy/allocation.py`, `lpcstudy/ensemble.py`, `lpcstudy/experiments.py` and their unit tests `tests/unit/test_allocation.py`, `tests/unit/test_ensemble.py`, `tests/unit/test_experiments.py`. Out: every other file.
- **Definition of done:** the four owner comments applied (80 columns by black, one item per line, pedagogical docstrings in American English, complexity reduced) with no change of any numeric result, results.json leaf, RESULTS.md line or CLI behavior.
- **Acceptance criteria:** unit tests of the six files pass; black `--check` idempotent; smoke compare against `refactor-base3/smoke` reports tier T0, 13914 leaves, all equal, 0 different, 0 one-sided, exit 0.
- **Affected checks:** `tools/run_tests.sh unit` on the three test files, once.

## Log

### Complexity audit (per file)

allocation.py (before 607 lines):
- `global_weight`, `regime_weight` and `pooled_floor_count` each re-wrote the same sums (`sum(sq_plp - cross)`, `sum(curvature)`); consolidated into the private helpers `_pooled_sums` and `_pooled_weight`. The expressions and their order are unchanged (a slice `[:]` of the whole array is the array itself), so the bits are the same; `test_floor_counters_a5_...` compares all three with the old expressions bitwise.
- `interp` lambda assigned to a name in `ErrorPredictor.weights` became a local `def`.
- No name removed: every public name has a caller outside the file (grep over lpcstudy/, tools/, tests/).

ensemble.py (before 899 lines):
- The reference-horizon column lookup was written twice (`forecast_draws`, `ensemble_moments`); consolidated into `_reference_column`. One behavior difference, on invalid input only: `ensemble_moments` with a reference horizon not among the horizons used to raise `IndexError` (from `[0][0]`) and now raises the same `ValueError` message as `forecast_draws`. New test `test_ensemble_moments_rejects_a_missing_reference_horizon`.
- In `forecast_draws`, the repeated `x.reshape(n_states, n_draws).sum(axis=1)` became a local `per_state`; the two `if ref_col is not None` blocks were merged (same statements, same order).
- In `ensemble_moments`, the always-equivalent condition `halves is not None and half_out is not None` became `halves is not None` (halves is None exactly when half_out is None).
- No name removed (`ERROR_CLIP`, `THREADS_DEFAULT`, `ClipMasks`, `LM_FIELDS`, `stack_optional`, `CORRELATION_FIELDS` all have callers inside the repo, checked by grep).

experiments.py (before 814 lines):
- `_v4_extra_forecasts(study, ...)`: the `study` argument was deleted by `del study` on the first line and documented as "unused"; removed from the signature and its one caller (`convergence_check`). No test or tool calls it (grep).
- `from .pipeline import SplitData` inside `_sweep_subset` moved to the module's existing top-level import from `.pipeline` (no cycle: the module already imported from there).
- The `bits` lambda built inside the loop of `_v4_extra_forecasts` became a local `def` before the loop.
- No name removed.

Tests: no test removed. One test added (above).

### Runtime strings flagged (not changed)

None: no runtime string (log message, error message, results leaf) was changed, and none contains a British spelling (grep list: behaviour, normalis*, colour, centre, neighbour, analyse, minimis*, optimis*, initialis*, ...). The log messages were only re-wrapped across implicit string concatenation; the concatenated text is identical.

### 4.9 checklist before the unit test run

1. Change set: lpcstudy/allocation.py, ensemble.py, experiments.py; tests/unit/test_allocation.py, test_ensemble.py, test_experiments.py; this unit file.
2. Radius: the three unit test files of the three modules (brief: tests of my files, once). Smaller than the whole suite; unit tier.
3. Already run: no (first run on this code).
4. Device: `JAX_PLATFORMS=cpu` (the wrapper sets it).
5. Threads and time: `LPC_THREADS=4` via the wrapper; unit tier, minutes at most.
6. Contention: no GPU job, no preset run by me; CPU only.
7. Output: `-q --tb=short -rfE` (the wrapper).
8. Command: `LPC_PYTHON=/home/brianm/projects/physics/chaos/lpcstudy/.venv/bin/python tools/run_tests.sh unit tests/unit/test_allocation.py tests/unit/test_ensemble.py tests/unit/test_experiments.py`

### Results

- Line counts (wc -l), before to after: allocation.py 607 to 823; ensemble.py 899 to 1187; experiments.py 814 to 1279; test_allocation.py 428 to 627; test_ensemble.py 760 to 1159; test_experiments.py 1093 to 1876. The growth is black putting one item per line at 80 columns and the longer docstrings; the logic shrank slightly (shared helpers).
- Symbols removed: 0 functions or classes; 1 unused parameter (`study` of `_v4_extra_forecasts`). Tests removed: 0. Tests added: 1.
- Code changes (all stated above under "Complexity audit"): reasons are duplication (helpers), an unused argument, an in-function import and a name-bound lambda. A script comparing every non-docstring string constant of old and new files found no difference in the three source files; in the tests the only new constants are those of the added test.
- Black: `uvx black==26.10.1 --check` on the six files: unchanged (idempotent).
- Unit tests of the six files, once: `80 passed in 1.98s`.
- Bitwise neutrality: smoke DEV-0 (lorenz63 rossler chua) in 76 s, compared with `refactor-base3/smoke`: tier T0, 13914 leaves, equal 13914, different 0, one-sided 0, RESULT PASS (exit 0).
- Status: done pending independent review.
