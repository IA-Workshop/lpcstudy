# WU-0004h-G2: style pass on the systems, dynamics, oracle, validation, networks and estimation modules

| Field | Value |
| --- | --- |
| Status | in progress |
| Class | CSQ3 development |
| Agent(s) | claude-sonnet-5-5 |
| Estimate | about 2 hours; no GPU |

## Plan (written before execution)

- **Scope:** the owner's code review of 2026-10-18, applied to the group G2 files `lpcstudy/systems.py`, `dynamics.py`, `oracle.py`, `validation.py`, `networks.py`, `estimation.py` and the tests that belong to them (`tests/unit/test_systems.py`, `test_dynamics.py`, `test_oracle.py`, `test_estimation.py` and the validation part of `test_validation.py`; the networks tests live in `test_estimation.py`). Out: every other file; the V7 part of `test_validation.py` (it tests `analysis.py`, another group's module) is left as it is.
- **Definition of done:** (1) code formatted by black at 80 columns; (2) long lists, tuples, dicts and argument lists one item per line (black's magic trailing commas); (3) every module, class, function and test docstring rewritten in plain early-undergraduate language, American spelling; (4) dead code and duplication removed, with grep evidence; (5) no behavior change: smoke compare tier T0, 13914 leaves, all equal.
- **Acceptance criteria:** tests of the group pass, once; `compare_runs` smoke result PASS with 0 different and 0 one-sided; files with no code change are AST-equal (docstrings ignored); every code change is listed with its reason.
- **Affected checks:** the five test files above (unit tier, CPU), then one smoke run on DEV-0. No whole suite and no integration tier (the main session runs the gates).

## Log

### 2026-10-18 test-run checklist (DEVELOPMENT_WORKFLOW.md 4.9), before the one test run

1. Change set: the six `lpcstudy/` modules and five test files of G2 (worktree `wu/style-g2`, branch from develop 6ddf9cb) plus this unit file.
2. Radius: `tests/unit/test_systems.py`, `test_dynamics.py`, `test_oracle.py`, `test_validation.py`, `test_estimation.py`, unit tier. This is what the brief names; it is smaller than the whole suite. Removed names have no caller outside the group (see below), so no other test file imports a changed name.
3. Already run? No: first run on this code.
4. Device: `JAX_PLATFORMS=cpu` (set by `tools/run_tests.sh`).
5. Threads and time: `LPC_THREADS` default 4; unit timeout 300 s.
6. Contention: other groups run smoke on CPU; no GPU run, no lock needed.
7. Output: the wrapper's quiet output; only the summary line is recorded.
8. Command: `LPC_PYTHON=/home/brianm/projects/physics/chaos/lpcstudy/.venv/bin/python tools/run_tests.sh unit tests/unit/test_systems.py tests/unit/test_dynamics.py tests/unit/test_oracle.py tests/unit/test_validation.py tests/unit/test_estimation.py`

### Line counts (wc -l, before -> after; black at 80 columns expands one-line signatures and calls, and the docstrings are longer)

| File | Before | After |
| --- | ---: | ---: |
| lpcstudy/systems.py | 398 | 468 |
| lpcstudy/dynamics.py | 291 | 346 |
| lpcstudy/oracle.py | 383 | 479 |
| lpcstudy/validation.py | 598 | 871 |
| lpcstudy/networks.py | 293 | 337 |
| lpcstudy/estimation.py | 434 | 550 |
| tests/unit/test_systems.py | 403 | 549 |
| tests/unit/test_dynamics.py | 148 | 200 |
| tests/unit/test_oracle.py | 716 | 978 |
| tests/unit/test_validation.py | 784 | 1074 |
| tests/unit/test_estimation.py | 791 | 1138 |

### Complexity audit: removed symbols (grep of the whole repository, including tools/, tests/ and docs scripts, found no caller)

- `dynamics.advance_states` and `dynamics._advance` (and the `functools.partial` import): `grep -rwn "advance_states\|_advance" --include=*.py .` finds only their own definitions, plus an unrelated local helper named `_advance` in `tests/slow/test_start_states.py`.
- `networks.estimator_jacobian_norm`: `grep -rln "estimator_jacobian_norm" .` finds only `lpcstudy/networks.py`.
- `oracle.local_dimension`: a wrapper that only forwarded to `local_dimension_counted(...)[0]`. Its only callers were `oracle.py` docstrings and `tests/unit/test_oracle.py`; the tests now call `local_dimension_counted(...)[0]`. Records and notes under `docs/agent/` still mention the old name in prose (they are append-only and untouched).
- `systems.SystemSpec.extra` (field, and the `dataclasses.field` import): never passed (`grep -rn "extra=" lpcstudy tools tests` finds none) and never read (the only `.extra` hits are `spec.extra` of an unrelated spec in `tools/rehearsal_report.py`). `SystemSpec` is not serialized (`dataclasses.asdict` is applied to the config only).
- Kept on purpose (used outside the group): `systems.estimate_lyapunov` (a thin wrapper, but `tests/unit/test_data.py` and the notes scripts call it), `estimation.StateEstimator.estimate` and `Refinement.trace`/`cost`/`generate` (tests).

### Removed tests

None removed. One assertion was dropped from `test_local_dimension_counts_zero_distance_a7`: `local_dimension(reference, queries).tobytes() == ref.tobytes()`, because it tested only the removed wrapper; the same bitwise comparison of `local_dimension_counted` stays. The other tests that called `local_dimension` now call `local_dimension_counted(...)[0]`, and the two `__defaults__ == (20,)` checks refer to `local_dimension_counted`.

### Code changes (everything else is formatting and docstrings)

- `systems.py`: removed `SystemSpec.extra` and the `field` import (above).
- `dynamics.py`: removed `_advance`, `advance_states` and the `partial` import (above).
- `oracle.py`: removed `local_dimension` (above); in `state_oracles` the expression `ctx.eval_states[t_chunk - ctx.history]` is bound to the local `oldest` before it is passed to `nu_fn` (same value, shorter line).
- `networks.py`: removed `estimator_jacobian_norm` (above).
- `validation.py`: the key `"centre"` of the `p2_bound_terms` result is now `"center"` (American spelling; the key is read only by `tests/unit/test_validation.py`, which is updated; it never reaches `results.json`, `p2_bound_summary` does not use it).
- `estimation.py`: no code change.
- Tests: renamed `test_oracle_pool_is_the_seeded_labelled_draw_shared_by_the_splits` to `..._labeled_...` (spelling), `test_train_mlp_draws_its_randomness_from_the_generator_in_the_documented_order` to `test_train_mlp_draws_randomness_from_generator_in_documented_order`, `test_trained_network_weights_digest_is_sha256_of_the_layer_arrays_in_order` to `test_weights_digest_is_sha256_of_layer_arrays_in_order` and `test_p2_stable_case_generic_coordinates_is_zero_up_to_centring_round_off` to `test_p2_stable_case_generic_coordinates_centering_round_off` (the last three so that the `def` line fits in 80 columns; the last also for the spelling). The note `docs/agent/notes/2026-10-18-nvvuq-status-lines-proposal.md` line 121 cites the old name of the last one.

### Verification

(a) AST check against develop with docstrings (including attribute docstrings, the strings after an assignment) ignored, with my extended copy `/tmp/claude-1000/astdiff_g2.py` of `ast_compare.py` (the stock tool also strips function and class docstrings only, so it prints "AST DIFFERENT" for `estimation.py` because of its three attribute docstrings; the extended tool prints an empty diff):

- `estimation.py`: empty AST diff (no code change).
- `systems.py`: only the `extra` field and the `field` import.
- `dynamics.py`: only `_advance`, `advance_states` and the `partial` import.
- `oracle.py`: only `local_dimension` and the `oldest` local.
- `networks.py`: only `estimator_jacobian_norm`.
- `validation.py`: only `centre` -> `center` (three places).

(c) Unit tests of the group, once: `101 passed in 16.72s` (exit 0).

(d) Bitwise neutrality, once: `python -m lpcstudy --preset smoke --seed-id DEV-0 --systems lorenz63 rossler chua` finished in 89 s; `tools/compare_runs.py` against `runs/refactor-base3/smoke`: tier T0, leaves REF 13914, NEW 13914, equal 13914, different 0, one-sided 0, RESULT: PASS (exit 0).

Black: `uvx black==26.10.1` run on all files, then `--check` clean (for `tests/unit/test_validation.py` with `--line-ranges` limited to the import block and the validation tests, so the V7 tests of another group are not touched).

### Runtime strings flagged

None found: the only runtime strings of G2 that reach `results.json` (`P2C_KIND`, `P2C_FORM`, the `tolerances.tau_N` text, the `OrbitDivergence` and `ValueError` messages) contain no British spelling and are unchanged.

### Not done / for the main session

- `tests/unit/test_validation.py` lines 1-282 (the V7 tests and the module docstring) belong to `analysis.py` and keep their old docstrings and line lengths; the module docstring there says "V7 and the validation gate" and should be rewritten by whoever owns `analysis.py`. Both groups touch this file: merge the validation import block (lines 25-35) and everything after `_passing_validation` from this branch.

## Review

- **Reviewer:** not yet assigned.
- **Findings and resolution:**

## Audit

- Is the definition of done met? See Verification above.
- Defects recorded: none.
- Notes for successors: the black line length forces many one-line calls into one-argument-per-line form, so line counts grow; that is expected.

## Referral

None.
