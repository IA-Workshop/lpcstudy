# WU-0004h-G4: owner's code review of 2026-10-18, group G4 (analysis)

| Field | Value |
| --- | --- |
| Status | done (awaiting merge by the main session) |
| Class | CSQ3 development (style and simplification, no behavior change) |
| Agent(s) | claude-sonnet-5-5 |
| Estimate | one session |

## Plan (written before execution)

- **Scope:** `lpcstudy/analysis.py`, `tests/unit/test_analysis.py`. No other file.
  Rules: the common brief of the owner's review (80 columns by black,
  one item per line, pedagogical docstrings, American spelling, complexity audit).
- **Definition of done:** behavior unchanged (no numeric result, no string leaf
  of results.json, no RESULTS.md line); tests of the two files pass; smoke
  comparison against `refactor-base3` reports tier T0, 13914 leaves, all equal.
- **Acceptance criteria:** unchanged tolerances and test assertions of live behavior
  (PRIME.2); every removed symbol has no caller outside this group; every code change
  is bitwise neutral and listed below.
- **Affected checks:** `tests/unit/test_analysis.py` (the unit file of the module);
  also `tests/unit/test_rng_hygiene.py` (it scans `analysis.py` by AST for
  `make_rng` sites and `_boot` call positions) and `tests/unit/test_budget.py`
  (reads `analysis.PRIMARY_LEVEL`, `H1_LEVEL`) in the same single run.

## Log

### 2026-10-18 Section 4.9 checklist before the one test run

1. Change set: `lpcstudy/analysis.py`, `tests/unit/test_analysis.py`,
   this unit file (three commits on `wu/style-g4`, base develop 6ddf9cb).
2. Radius: `tools/test_impact.py --base develop` gives the unit set
   test_analysis, test_budget, test_clip_sensitivity, test_data, test_experiments,
   test_identifiers, test_pipeline, test_rng_hygiene, test_tools_rehearsal_diagnostics,
   test_tools_rehearsal_report, test_tools_test_impact, test_validation. Smaller
   than the whole suite. The integration tier is excluded by the brief
   (the main session runs the gates). `test_rng_hygiene` scans `analysis.py` by AST.
3. Already run: no (first and only run on this code).
4. Device: `JAX_PLATFORMS=cpu` (set by `tools/run_tests.sh`).
5. Threads and time: `LPC_THREADS` default 4; unit timeout 300 s.
6. Contention: no pilot, full or GPU run started by this unit.
7. Output: quiet, summary and failures only (the wrapper's default options).
8. Command: `LPC_PYTHON=/home/brianm/projects/physics/chaos/lpcstudy/.venv/bin/python
   tools/run_tests.sh unit <the twelve files above>`.

### 2026-10-18 Work done

Commits on `wu/style-g4`: 9254d5b (code), 3a431e9 (analysis docstrings,
spelling, black), 43a577a (test docstrings, spelling, black, one test-helper
consolidation), and the commit of this Log.

**Line counts (wc -l), develop 6ddf9cb to this branch**

| File | Before | After | Note |
| --- | --- | --- | --- |
| `lpcstudy/analysis.py` | 2252 | 3435 | black at 80 columns puts one item per line; the docstrings are longer and plainer |
| `tests/unit/test_analysis.py` | 3606 | 5775 | same reason |

**Code changes to `lpcstudy/analysis.py` (each bitwise neutral, with the reason)**

1. Removed `h1a_ratio` (a wrapper that returned `_median_fit_stats(...)[0]`).
   Evidence of no caller outside the tests of this file:
   `grep -rnw h1a_ratio --include=*.py lpcstudy tools tests` finds nothing now.
   The 16 uses in `test_analysis.py` go through the new test helper `_h1a_ratio`
   (same expression), so no assertion changed.
2. Removed `_per_state_spearman` (a wrapper that returned element 0 of
   `_per_state_spearman_counted`). Its only callers were three tests. Two use
   `_per_state_spearman_counted(...)[0]` (same values). One assertion was
   removed, `np.array_equal(rho, _per_state_spearman(levels, table))`, because it
   tested only the equality of the wrapper with the function it wraps.
3. Inlined `_at_bound` (3 lines, one caller) into `_median_fit_stats`.
   The test and tools grep shows no other user. The expression is the same.
4. `h1c_horizon_law`: `characteristic_horizon` was called twice per threshold
   (once for the horizon, once for the event flag). It is now called once per
   threshold and both outputs are used. The function is deterministic and pure,
   so the arrays are identical.
5. `NOISE_SENS_FLOOR`, `state_horizon_target` and `regime_regret` are imported at
   the top from `.allocation` instead of inside three functions (the module
   already imported `deployable_profile` from there, so there is no import cycle).
   Two tests that patched `allocation.state_horizon_target` now patch
   `an.state_horizon_target` (the name the module uses).
6. New helper `_masked_logit`, which replaces two identical inline
   computations (`logit_of` in `qn_profile_block` and the expression in
   `h2a_part_ii`). Same arithmetic, same order of operations.
7. Local variable `centre` renamed `center` in `_paired_change`.
8. Long string literals were split into adjacent literals (the parsed constant
   is unchanged). Constants were regrouped with comments; `H1_LEVEL` moved up. The
   AST comparison of the top-level statements against commit 9254d5b shows only
   docstring and `centre`/`center` differences.

Names used outside the group (`_paired_change`, `_per_state_spearman_counted`,
`_fit_seed_law`, `_median_fit_stats`, `_boot`, `_h3b_trees`, every public `h*` and
`qn_*`) keep their names and signatures. `tests/unit/test_rng_hygiene.py` scans
`analysis.py` for `make_rng` call sites by function name: none moved.

**Removed symbols: 3** (`h1a_ratio`, `_per_state_spearman`, `_at_bound`).
**Added: 1** (`_masked_logit`, which consolidates two copies).
**Removed tests: 0.** One redundant assertion (item 2).

**Test file changes (code, not only docstrings)**: all function-level
`from ... import` lines and the repeated `import pytest/json/itertools/warnings`
were hoisted to the top (module aliases `analysis`, `an`, `allocation`, `budget`
stay local because tests patch them; `curvature` stays local because many tests
use a local variable of that name). The `HistGradientBoostingRegressor`
construction with literal parameters (4 copies, independent of `qn_regressor` on
purpose) is now one helper `_reference_fit_predict`. The H1c stub world (two
copies) is now `_h1c_stub_world`. No tolerance, seed or assertion of live
behavior changed.

**Runtime strings that look British and were NOT changed** (they reach
results.json; the main session decides):

- `lpcstudy/analysis.py:594`, in `h1a_library_scaling`, key `reference_estimator`:
  "(Levina-Bickel with the k-1 normalisation; exactly unbiased for 1/d under the
  Poisson law)".
- `lpcstudy/analysis.py:1924`, in `h2a_part_ii`, key `controls`: "... centred on
  the full-sample mean".

**Not fixable by black**: 19 test `def` lines in `tests/unit/test_analysis.py` are
longer than 80 columns because the test names are 66 to 87 characters. The names
are cited in append-only records (WU-0002.4-5, 0002.9, 0002.9b, 0002.11, 0003.7c,
0004d, defects.md), so they were not renamed. Nothing else exceeds 80 columns in
the two files.

**Candidates outside this group** (not touched): `analysis.weight_profiles(cell,
config)` has an unused `config` parameter, but `experiments.py` passes it.

**Verification**

- (a) no file without a code change.
- (b) code changes listed above.
- (c) `LPC_PYTHON=... tools/run_tests.sh unit` on the twelve files of the radius:
  `1 failed, 511 passed in 40.59s`. The one failure,
  `tests/unit/test_identifiers.py::test_criterion_text_is_the_v3_section_2_row`,
  is not caused by this unit: `lpcstudy/identifiers.py` and the v3 export are not
  in the change set, and the same single test fails on the develop worktree
  (732e7d6): `1 failed, 10 passed`. All of `test_analysis.py`, `test_rng_hygiene.py`
  and `test_budget.py` pass.
- (d) Smoke, DEV-0, three systems, then `tools/compare_runs.py` against
  `refactor-base3/smoke`: tier T0, leaves REF 13914, NEW 13914, equal 13914,
  different 0, one-sided 0, `RESULT: PASS (exit 0)`.
- `uvx black==26.10.1 --check` on both files: unchanged (idempotent).

## Review

- **Reviewer:** none requested (style unit; the main session runs the gates).
- **Findings and resolution:** none.
