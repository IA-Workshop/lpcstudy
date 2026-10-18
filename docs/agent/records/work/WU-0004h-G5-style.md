# WU-0004h-G5: owner's code review of 2026-10-18, group G5 (statistics, pipeline, dump)

| Field | Value |
| --- | --- |
| Status | done (pending review) |
| Class | CSQ3 development |
| Agent(s) | claude-sonnet-5-5 |
| Estimate | one session |

## Plan (written before execution)

- **Scope:** `lpcstudy/statistics.py`, `lpcstudy/pipeline.py`, `lpcstudy/dump.py` and their tests
  `tests/unit/test_statistics.py`, `tests/unit/test_pipeline.py`, `tests/unit/test_dump.py`. Nothing else.
  The brief is `/tmp/claude-1000/style_brief.md` (owner's review points 1 to 4: black at 80 columns, one item
  per line, pedagogical American-English docstrings, complexity reduction).
- **Definition of done:** the six files are formatted by black 26.10.1 (idempotent), every docstring is
  rewritten, American spelling in comments, docstrings and identifiers, dead code and duplication removed
  where safe, no change of behavior.
- **Acceptance criteria:** (a) tests of the six files pass; (b) `tools/compare_runs.py` of a smoke run against
  `runs/refactor-base3/smoke` shows tier T0, 13914 leaves, all equal, 0 different, 0 one-sided, exit 0;
  (c) AST comparison (docstrings and bare string statements ignored) shows only the code changes listed in the Log;
  (d) no tolerance changed.
- **Affected checks:** blast radius = the three test files of the group plus `tests/unit/test_rng_hygiene.py`
  (it scans call sites in `lpcstudy/` by name and argument position).

## Log

### Per file

| File | Lines before | Lines after |
| --- | --- | --- |
| lpcstudy/statistics.py | 739 | 952 |
| lpcstudy/pipeline.py | 1091 | 1735 |
| lpcstudy/dump.py | 429 | 627 |
| tests/unit/test_statistics.py | 1021 | 1464 |
| tests/unit/test_pipeline.py | 809 | 1447 |
| tests/unit/test_dump.py | 423 | 807 |

Line counts grow because black puts one item per line and the docstrings now explain terms.

### Code changes (statistics.py), each with its reason

1. `_draw_indices`: removed `base = np.arange(n_items)` and `base[np.minimum(idx, n_items - 1)]`; it yields `idx`
   directly. The clip never fires (every start is at most `n_items - block`, or 0, and `idx` is cut to
   `n_items`, so `idx <= n_items - 1`), and `base[...]` was an identity copy. A silent clip that never fires is
   removed, not counted (PRIME.4). Bitwise: `test_block_resample_indices_equal_those_recorded_inside_old_function`
   compares with the verbatim old code, which keeps the clip.
2. `_check_values` (new): the argument check shared by `percentile_interval` and `endpoint_mc_error`
   (identical code and messages before).
3. `_failures_reach` (new): `n_failed >= floor((B - 1) * q) + 1`, written three times before.
4. `_fill_failed` (new): the replacement of failed values by the finite minimum and maximum, written twice
   before. In `percentile_interval` the former `n_failed == 0` branch is gone: with no failures the filled arrays
   equal the input, so `np.quantile` returns the same numbers.
5. `_VERDICTS` and `_check_labels` (new): the verdict-label check of `combine_verdicts` and `overall_verdict`
   (same error text).
6. `endpoint_mc_error.half_range`: `(Q(q+d) - Q(q-d)) / 2` kept as two `np.quantile` calls (as before).

Not removed (names used outside the group): `block_bootstrap` (tests/unit/test_analysis.py,
tests/unit/test_rng_hygiene.py use it as the independent reference), `block_bootstrap_dropped`
(analysis.py), `entry_names` and `v4_arrays` in dump.py (experiments.py).

### Code changes (pipeline.py)

1. `_oracle_blocks`: the key is computed on its own line (`key = ...`); same value.
2. `cell_id`: `kind = "core" if core else "sweep"` before the f-string; same string.
3. `score_rules`: local `favours_cp` renamed `favors_cp` (American spelling).

### Code changes (dump.py)

None. `strip_compare.py` (all bare string statements ignored) prints "AST equal".

### Code changes (tests)

Tests: no assertion, tolerance, seed or reference changed. Changes: one `lambda` assigned to a name became a
`def` (`as_data` in test_statistics); a conditional expression became an `if` (`with_nans`); local variable
`neighbour` became `neighbor`; test `test_estimator_streams_are_labelled_by_...` became `..._labeled_by_...`
(no other file refers to it); two function-local imports in test_pipeline swapped order; chained `and`
asserts were split into separate asserts by black; helper docstrings added.

### Removed symbols and tests

None. Every public name of the three modules has a caller outside its own file or is the independent reference
of a test (grep over lpcstudy/, tools/, tests/).

### Runtime strings with British spelling

None found in the three modules (grep for the usual -our/-ise/-yse/-re forms over the six files, after the edits).

### 4.9 checklist (before the test run)

1. Change set: the six files above (`git status --porcelain`), nothing else.
2. Radius: `tests/unit/test_statistics.py tests/unit/test_pipeline.py tests/unit/test_dump.py` and
   `tests/unit/test_rng_hygiene.py` (rule: test file of each changed module, plus the file that scans their
   call sites); unit tier; smaller than the whole suite.
3. Already run: no, first run on this code.
4. Device: `tools/run_tests.sh` sets `JAX_PLATFORMS=cpu`.
5. Threads: `LPC_THREADS` default 4; unit timeout 300 s.
6. Contention: no preset running (CPU only).
7. Output: quiet via the wrapper.
8. Command: `LPC_PYTHON=/home/brianm/projects/physics/chaos/lpcstudy/.venv/bin/python tools/run_tests.sh unit tests/unit/test_statistics.py tests/unit/test_pipeline.py tests/unit/test_dump.py tests/unit/test_rng_hygiene.py`

### Results

- Tests (once, after all edits): `124 passed in 2.96s` (test_statistics, test_pipeline, test_dump, test_rng_hygiene).
- Black: `uvx black==26.10.1 --check` on the six files: "6 files would be left unchanged".
- AST comparison with `develop` (docstrings and bare string statements ignored): dump.py equal; statistics.py,
  pipeline.py and the tests differ only by the changes listed above (`astdiff.py` output read line by line).
- Bitwise neutrality: smoke run, DEV-0, three systems, `--out /tmp/claude-1000/style-g5-smoke` (88 s), compared with
  `runs/refactor-base3/smoke`: tier T0, leaves REF 13914 / NEW 13914, equal 13914, different 0, one-sided 0,
  RESULT: PASS (exit 0).
- Lines over 80 columns that remain: only `def test_...` lines whose names alone exceed 80 columns (black cannot
  split a name; renaming a test was not done, except the spelling fix above).

## Review

- **Reviewer:** pending (main session)
- **Findings and resolution:**

## Audit

- Notes for successors: the main session decides about the flagged items in the hand-back.
