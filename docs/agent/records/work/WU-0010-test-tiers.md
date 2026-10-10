# WU-0010: Test tiers, module-per-file split, smoke integration test

| Field | Value |
| --- | --- |
| Status | in progress |
| Class | CSQ3 development |
| Agent(s) | claude-sonnet-5-5 (main session) under governance ledger entry 5 (authorizations 4, 6) |
| Estimate | 3 sub-tasks, each S (ROADMAP.md §2) |

## Plan (written before execution)

Planner: claude-opus-5-5, 2026-10-10. Sources: ROADMAP.md §2 rows and acceptance criteria for WU-0010.1 to .3; DEVELOPMENT_WORKFLOW.md §2.2, §2.3, §4.1, §4.2, §4.5, §4.9; `.claude/rules/tests.md`; `.claude/hooks/test_gate.py`; `runs/baseline/smoke/results.json`. This is test infrastructure only. No v3 or Methods v2 content is touched, so LPC.PC.1 is not engaged. **Order: .1, then .2, then .3**, with one commit per sub-task. Item .3 depends only on .1, but it lands after .2 so that it arrives in the final layout.

- **Scope, in:** the files listed per sub-task below.
- **Scope, out:**
  - edits to test bodies, tolerances or references (WU-0013);
  - `tools/run_tests.sh` (WU-0012.1) and `tools/test_impact.py` (WU-0011);
  - catching implicit default-device GPU use (see R1);
  - `tests/slow/` and `tests/gpu/` content (WU-0005.5, WU-0003.4). Those directories are created with their first test, not now;
  - any change under `lpcstudy/`.
- **pytest.ini, not pyproject.** The repository has no `pyproject.toml`. DEVELOPMENT_WORKFLOW §4.1 and the §4.2 mapping rule name `pytest.ini`. Creating a `pyproject.toml` only for pytest would also be read by ruff and by packaging tools. Writing `/pytest.ini` is not in the Edit allow-list, so it prompts the owner once.
- **Dependencies:** none. `pytester` ships with pytest 9.1.1 and is enabled by `-p pytester`. The timeout is the `timeout=` argument of `subprocess.run`, so no `pytest-timeout` is needed.
- **Owner checkpoints (LPC.PC.11):** none. No verdict, statistics, seed, provenance or dependency code is touched. The applied-mathematician step is a confirmation only: no tolerance is introduced, and the 300 s timeout is the §4.1 budget.

### WU-0010.1: markers and conftest

- **Files.**
  - **`pytest.ini` (new)** contains:
    - `[pytest]`;
    - `testpaths = tests`;
    - `pythonpath = .` (lpcstudy is not installed in `.venv`; this makes a bare `pytest` import it);
    - `addopts = --strict-markers -p pytester`;
    - `markers =` with `unit`, `integration`, `slow` and `gpu`, each with a one-line description from the §4.1 table.
  - **`tests/conftest.py` (new)** contains:
    - `TIERS = ("unit", "integration", "slow", "gpu")`.
    - A pure function `tier_of(path, tests_root) -> str | None`. It returns the first path component under `tests/` if that component is in `TIERS`, or `"unit"` for the transitional `tests/test_core.py`. That transitional entry is deleted in .2. For anything else it returns `None`.
    - `pytest_collection_modifyitems`, which adds `getattr(pytest.mark, tier)` to each item and raises `pytest.UsageError` that lists every item whose tier is `None` ("place a test by cost and device", `.claude/rules/tests.md`).
    - An autouse fixture `_refuse_gpu(request, monkeypatch)`. For items whose tier is not `gpu`, it wraps `jax.devices` (backend: first positional or `backend=`) and `jax.local_devices` (backend: second positional or `backend=`).
  - **How the fixture detects a GPU request.** If the backend is a string whose lowercase form is in `{"gpu", "cuda", "rocm"}`, the wrapper calls `pytest.fail("GPU device requested outside tests/gpu/ (tier '<tier>', <nodeid>): CPU-only tiers never touch the GPU (DEVELOPMENT_WORKFLOW.md §4.5); move the test to tests/gpu/.", pytrace=False)`. It does this before delegating to jax, so CUDA is never initialized. `Failed` is a `BaseException`, so the test's own `except Exception` cannot swallow it. Any other argument delegates unchanged. The check does not depend on `JAX_PLATFORMS`.
  - **`tests/unit/test_conftest_markers.py` (new).** All of its tests use `pytester` and copy the real `tests/conftest.py` and `pytest.ini` into the synthetic tree:
    - (a) Synthetic `tests/{unit,integration,slow,gpu}/test_<tier>_probe.py` files, collected with `pytester.inline_genitems()`. Each item carries exactly its directory's tier marker and no other tier marker.
    - (b) A synthetic `tests/misc/test_x.py` makes collection fail with the UsageError text.
    - (c) A synthetic `tests/unit/test_gpu_call.py` calls `jax.devices("gpu")` and is run with `runpytest_subprocess` and `JAX_PLATFORMS` deleted (`monkeypatch.delenv`). It must give exit code 1 and output that matches `*GPU device requested outside tests/gpu/*`.
    - (d) The same file under `tests/gpu/` is run with `JAX_PLATFORMS=cpu`, so jax refuses natively and the GPU is never touched. Its output must not contain the conftest message.
    - Each test stays under 5 s. The docstrings name the reference: the directory-to-tier table of DEVELOPMENT_WORKFLOW §4.1. They have no numerical tolerance.
- **Acceptance (verbatim, fixed):** `pytest --strict-markers --collect-only -q tests` succeeds; a test placed under `tests/gpu/` carries `gpu`, under `tests/slow/` carries `slow`, and so on (asserted by `tests/unit/test_conftest_markers.py` on a synthetic item); a test outside `tests/gpu/` that calls `jax.devices("gpu")` fails with a clear message when `JAX_PLATFORMS=cpu` is unset. See Q1.
- **Affected checks.** Rule: `tests/conftest.py` and `pytest.ini` require the whole `unit` tier. This is a gate-sized run and the log must say so. The command is `python -m pytest -q --tb=short -rfE tests/test_core.py tests/unit`, on CPU, once. The tier is the 14 tests plus k marker tests, and k is recorded in the log.

### WU-0010.2: module-per-file split

- **Files.**
  - Create seven files under `tests/unit/`, as in the table below.
  - Create `tests/unit/unit_helpers.py`, which holds `_moments_from_draws` verbatim. It is shared by test_oracle and test_allocation and is imported as `from unit_helpers import _moments_from_draws` (prepend import mode, no `__init__.py`). No conftest fixture is needed.
  - Delete `tests/test_core.py`, and delete the transitional entry in `tests/conftest.py`.
  - Each new file has a one-line module docstring, `from __future__ import annotations`, and only the imports it uses. Its first `from lpcstudy.` import is the file's own module, and function-level imports stay inside their tests.
- **Target rule.** A test goes to the module whose function the assertion checks. The import order is arranged so that the first lpcstudy import names the file (Q4).

| Test | Target | Other lpcstudy imports |
| --- | --- | --- |
| `test_oracle_weight_minimizes_ensemble_mse` | test_oracle | helper (ensemble) |
| `test_regret_identity` | test_oracle | helper |
| `test_characteristic_horizon_and_censoring` | test_oracle | — |
| `test_closed_form_matches_uncorrelated_isotropic_case` | test_allocation | oracle, helper |
| `test_seed_proxy_recovers_parameters` | test_allocation | — |
| `test_kaplan_meier_matches_geometric_survival` | test_statistics | — |
| `test_logrank_detects_difference_and_not_null` | test_statistics | — |
| `test_holm` | test_statistics | — |
| `test_partial_correlation_removes_confounder` | test_statistics | — |
| `test_delay_vectors_order` | test_embedding | — |
| `test_delay_and_acf` | test_embedding | systems, `jnp` |
| `test_observability_matches_independent_jacobians` | test_dynamics | systems, `jax`, `jnp` |
| `test_per_state_spearman_handles_ties` | test_analysis | (function-level analysis) |
| `test_retrieval_spread` | test_ensemble | (function-level ensemble) |

  `test_closed_form_matches_uncorrelated_isotropic_case` goes to test_allocation because `closed_form_weight` lives in allocation. allocation is a non-core module, and its radius does not include test_oracle.
- **Acceptance (verbatim, fixed):** `pytest -q tests/unit` reports exactly 14 passed; `git diff --stat` shows only moves and import lines (`git diff -M` detects renames). Each file's name matches the module its tests import first. See Q2 and Q3. Additional evidence, stricter and not a replacement:
  - an `ast` one-liner shows that the source segment of each of the 14 functions and of the helper is byte-identical between `main:tests/test_core.py` and the new files;
  - `git diff --color-moved=plain main...HEAD -- tests` leaves only header and import lines unmoved.
- **Affected checks.** Rule: the change touches `tests/conftest.py`, so the whole `unit` tier runs (gate-sized). Command: `python -m pytest -q --tb=short -rfE tests/unit`, once, with expected summary `14+k passed`. Before that, `--collect-only -q` on the seven files is expected to list exactly 14. Collection only, not a run.

### WU-0010.3: smoke integration test

- **Files.** `tests/integration/test_smoke_pipeline.py` (new).
  - It runs `subprocess.run([sys.executable, "-m", "lpcstudy", "--preset", "smoke", "--out", str(tmp_path)], cwd=<repo root>, env={**os.environ, "JAX_PLATFORMS": "cpu", "XLA_PYTHON_CLIENT_PREALLOCATE": "false"}, capture_output=True, timeout=300)`.
  - It passes no seed argument, so the run uses the default 20261005 = DEV-0. It must never pass any other seed.
  - The outputs land in `tmp_path / "smoke"`. The test asserts that `results.json`, `RESULTS.md` and `run.log` are files and that `figures/` is a directory with at least one `.png` file. This is tighter than mere existence; the baseline has 4.
  - It asserts that `results["systems"]` is non-empty and that, for every system, `isinstance(results["systems"][s]["validation"]["gate"]["gate_pass"], bool)`. For smoke the only system is `lorenz63`, and this is the real path in `runs/baseline/smoke/results.json`. The test does not assert True: this is plumbing, not science.
  - On failure, the assertion message carries the last 20 lines of stderr.
  - The docstring names the reference as the output contract of `lpcstudy/__main__.py` plus the baseline schema. Its only bound is the 300 s timeout from the §4.1 budget; the baseline took 49 s. It is a plumbing check, not correctness evidence.
- **Acceptance (verbatim, fixed):** Run under `JAX_PLATFORMS=cpu`; wall-clock under 5 min on the workstation (the smoke preset is about 1 min); the test asserts presence of the four outputs and `validation.gate.gate_pass` is a bool. It is excluded from the `unit` tier by marker. Evidence for the last clause: `pytest --collect-only -q -m unit tests/integration` collects 0 and deselects 1.
- **Affected checks.** Rule: a single new test file means that file only, and no manual smoke run (§4.2: "run one of them, not both"). Command: `python -m pytest -q --tb=short -rfE tests/integration/test_smoke_pipeline.py`, integration tier, CPU, once. Record the wall-clock.

### Definition of done

- All three acceptance criteria are met with the evidence above, pasted into `## Log`, along with the §4.9 checklist before each run.
- `tests/test_core.py` is gone.
- There are three commits naming WU-0010.k and ending `Agent:`.
- Independent review is approved.

### Risks

- **R1. Implicit GPU use is not caught.** With `JAX_PLATFORMS` unset on the GPU workstation, a test's default-device jnp operations would initialize CUDA without calling `jax.devices`. Mitigations: the settings env forces cpu, and WU-0012.1 forces it per tier.
- **R2. `from jax import devices` bypasses the wrapper.** An alias bound at import time escapes it. lpcstudy has no such call today.
- **R3. Basename collisions across tier directories.** In prepend mode, a test module name may be used only once across the tier directories.
- **R4. The integration test passes no seed argument.** WU-0001.1 must keep DEV-0 as the default, or update this test in the same change.
- **R5. Some radii miss tests that use systems.** `test_delay_and_acf` and the observability test use `systems` but are not in its §4.2 dependent set. WU-0011 should map by the imports of the test file.

### Questions for the owner

- **Q1. The .1 collect command is blocked by the hook.** `.claude/hooks/test_gate.py` blocks the bare `tests` path without `LPC_GATE`. Proposed: run `pytest --strict-markers --collect-only -q <every existing tier dir> [tests/test_core.py]`. The conftest's UsageError guarantees that no test lives elsewhere. The alternative is for the main session to run it with `LPC_GATE`.
- **Q2. "Exactly 14 passed" conflicts with the marker test.** `tests/unit/test_conftest_markers.py` from .1 also lives in `tests/unit`. Proposed: exactly 14 collected from the seven moved files, and exactly 14+k passed for `tests/unit`, with k fixed in the .1 log.
- **Q3. Git will not detect a 1-to-7 split as a rename.** Every piece is under about 25% of 172 lines, below the default 50% similarity. Proposed: the stricter `ast` byte-identity check plus `--color-moved` as the evidence, with `git diff -M --stat` recorded as is.
- **Q4. "Imports first" and "exercises" differ for three tests.** In the old import order, tests 1, 2 and 3 import ensemble or allocation before oracle. Proposed: the "exercises" rule of the ROADMAP row, with imports ordered to match. Please confirm.

### Plan amendment 2026-10-10, claude-sonnet-5-5 (main session), before execution (VV.3)

Answers to Q1 to Q4, taking the planner's proposals. None loosens an acceptance criterion; each fixes how a criterion is checked, and Q3 is stricter than the criterion. The owner MAY override any of them before WU-0010.1 is reviewed; this unit changes no verdict, statistics, seed, provenance or dependency code.

- **Q1.** The .1 collect check lists each existing tier directory (and `tests/test_core.py` until it is removed) instead of bare `tests`; the conftest's UsageError for tests outside a tier directory is the guarantee that nothing is missed.
- **Q2.** .2 is checked as: exactly 14 tests collected from the seven moved files, and 14+k passed for `tests/unit`, with k (the number of tests in `test_conftest_markers.py`) fixed in the .1 log before .2 runs.
- **Q3.** .2 evidence: each moved test's source is `ast`-identical to its original, plus `git diff --color-moved` and `git diff -M --stat` recorded as they are (git will not report a 1-to-7 split as renames).
- **Q4.** "Module it exercises" (the ROADMAP row's wording) decides the target file; each file's imports are ordered so its first import names the file.

## Log

<dated entries: what was done, commands, results, commits>

### 2026-10-10, claude-sonnet-5-5 (developer): WU-0010.1 markers and conftest, before the run

Files: `pytest.ini` (new), `tests/conftest.py` (new), `tests/unit/test_conftest_markers.py` (new, 4 tests, so **k = 4**). No file under `lpcstudy/` is touched.

§4.9 checklist before the .1 invocations:

1. Change set: `pytest.ini`, `tests/conftest.py`, `tests/unit/test_conftest_markers.py` (all new, uncommitted); the unit file's `## Log`.
2. Radius: rule "`tests/conftest.py`, `pytest.ini` -> the whole `unit` tier" (§4.2). This is a gate-sized run by rule, but the tier is small: `tests/test_core.py` (14 tests, transitional unit) plus `tests/unit` (4). It is not the whole suite, since no `slow`/`gpu`/`integration` test exists yet.
3. Already run: no. These files are new.
4. Device: `JAX_PLATFORMS=cpu` from the settings env, not overridden. Test (c) deletes it only inside the pytester subprocess, where the guard acts before jax is called.
5. Threads and time: `LPC_THREADS=4` from the settings; unit timeout 300 s, expected well under.
6. Contention: no preset, `slow` or `gpu` run is started.
7. Output: `-q --tb=short -rfE`; only the summary and failures are recorded.
8. Command (hand-set variables, WU-0012 not landed): (i) per Q1, `python -m pytest --strict-markers --collect-only -q tests/unit tests/test_core.py`; (ii) `python -m pytest -q --tb=short -rfE tests/test_core.py tests/unit`.

### 2026-10-10, claude-sonnet-5-5 (developer): WU-0010.1 results

- (i) `python -m pytest --strict-markers --collect-only -q tests/unit tests/test_core.py`: `18 tests collected in 0.56s` (14 in test_core, 4 in test_conftest_markers). Strict markers accepted all four tier markers. Per Q1 the bare `tests` path was not used.
- (ii) `python -m pytest -q --tb=short -rfE tests/test_core.py tests/unit`: `18 passed in 5.64s`. No failure, no rerun.
- **k = 4** (tests in `tests/unit/test_conftest_markers.py`). Expected summary for `tests/unit` in .2 is therefore 14 + 4 = 18 passed.
- Counts: no clip, replacement or fallback in the new code. The guard raises `pytest.fail` on a GPU request. The transitional `test_core.py -> unit` entry in `tier_of` is the one special case and is removed in .2.
- Self-check: the grep for `clip|nan_to_num|isfinite|where(|try:|except` on the new files finds only `try/except ValueError` in `tier_of`, which maps a path outside `tests/` to `None` (the UsageError then reports it if collected). The grep for `default_rng|random.|PRNGKey` finds none. No tolerance exists in the new tests.

### 2026-10-10, claude-sonnet-5-5 (developer): WU-0010.2 module-per-file split, before the run

Files: new `tests/unit/test_{oracle,allocation,statistics,embedding,dynamics,analysis,ensemble}.py` and `tests/unit/unit_helpers.py`; `tests/test_core.py` deleted (`git rm`); `tests/conftest.py` loses the transitional `test_core.py` entry (`TRANSITIONAL` and its branch in `tier_of`). The new files were generated by a scratchpad script that copies each function's source segment (`ast.get_source_segment`) from `main:tests/test_core.py`, so no test text is edited by hand. Placement follows the plan table (Q4: "exercises" rule; the first `lpcstudy` import of test_oracle, test_allocation, test_statistics, test_embedding and test_dynamics names the file; test_analysis and test_ensemble import their module at function level, as in the original).

§4.9 checklist before the .2 invocations:

1. Change set: `tests/conftest.py` (modified), `tests/test_core.py` (deleted), seven new `tests/unit/test_*.py`, new `tests/unit/unit_helpers.py`; nothing under `lpcstudy/`.
2. Radius: rule "`tests/conftest.py` -> the whole `unit` tier" (§4.2), gate-sized by rule, and now the whole suite is `tests/unit` only (no other tier has a test yet). Command targets `tests/unit`, not the bare `tests` path.
3. Already run: the moved tests ran in .1 as `tests/test_core.py`, but the code is different (new files, conftest edited), so this is a new run. The collection-only check has not run.
4. Device: `JAX_PLATFORMS=cpu` from the settings, not overridden.
5. Threads and time: `LPC_THREADS=4`; unit timeout 300 s, expected about 6 s.
6. Contention: no preset, `slow` or `gpu` run.
7. Output: `-q --tb=short -rfE`; summary and failures only.
8. Commands: (i) `python -m pytest --collect-only -q tests/unit/test_oracle.py tests/unit/test_allocation.py tests/unit/test_statistics.py tests/unit/test_embedding.py tests/unit/test_dynamics.py tests/unit/test_analysis.py tests/unit/test_ensemble.py` (expect 14); (ii) `python -m pytest -q --tb=short -rfE tests/unit` (expect 14 + k = 18 passed).

### 2026-10-10, claude-sonnet-5-5 (developer): WU-0010.2 results (commit 0bd0b1c)

- (i) `python -m pytest --collect-only -q <the seven files>`: `14 tests collected in 0.58s`.
- (ii) `python -m pytest -q --tb=short -rfE tests/unit`: `18 passed in 2.80s` (= 14 + k, k = 4). No failure, no rerun.
- **ast byte-identity** (scratchpad script: for each `FunctionDef` in `git show main:tests/test_core.py` and in the new `tests/unit/*.py` except `test_conftest_markers.py`, compare `ast.get_source_segment`): `15 functions (14 tests + helper); not byte-identical: []`. Placement: oracle: `test_oracle_weight_minimizes_ensemble_mse`, `test_regret_identity`, `test_characteristic_horizon_and_censoring`; allocation: `test_closed_form_matches_uncorrelated_isotropic_case`, `test_seed_proxy_recovers_parameters`; statistics: `test_kaplan_meier_matches_geometric_survival`, `test_logrank_detects_difference_and_not_null`, `test_holm`, `test_partial_correlation_removes_confounder`; embedding: `test_delay_vectors_order`, `test_delay_and_acf`; dynamics: `test_observability_matches_independent_jacobians`; analysis: `test_per_state_spearman_handles_ties`; ensemble: `test_retrieval_spread`; `unit_helpers.py`: `_moments_from_draws`. This matches the plan table.
- **`git diff -M --stat HEAD~1 HEAD -- tests`** (recorded as is; git reports no rename for a 1-to-7 split, Q3): `10 files changed, 222 insertions(+), 178 deletions(-)`; `tests/test_core.py` -172; per file: test_allocation +32, test_analysis +14, test_dynamics +34, test_embedding +27, test_ensemble +16, test_oracle +39, test_statistics +43, unit_helpers +14, conftest.py 9 changed (transitional entry removed).
- **`git diff --color-moved=plain HEAD~1 HEAD -- tests/test_core.py tests/unit/`**: the lines not detected as moved, other than blanks, are exactly 12: the old module docstring (removed), the seven new one-line module docstrings and the helper's docstring, and the new lines `from lpcstudy.oracle import oracle_weight` (test_allocation) and `from unit_helpers import _moments_from_draws` (test_allocation and test_oracle). `import` lines that repeat an old line count as moved, so the unmoved set is header and import lines only, as the plan requires. (conftest.py is outside this diff; its change is the removal of the transitional entry.)
- Self-check: no test body or tolerance changed (ast evidence); `ruff check --select F tests` passes (no unused imports); no clip, replacement or fallback added; `tier_of` lost its special case.

### 2026-10-10, claude-sonnet-5-5 (developer): WU-0010.3 smoke integration test, before the run

File: `tests/integration/test_smoke_pipeline.py` (new). It runs `python -m lpcstudy --preset smoke --out <tmp_path>` with `cwd` at the repo root, `JAX_PLATFORMS=cpu`, `XLA_PYTHON_CLIENT_PREALLOCATE=false`, `timeout=300`, and no seed argument (default 20261005 = DEV-0). Asserts: exit code 0 (message carries the last 20 stderr lines); `results.json`, `RESULTS.md`, `run.log` are files; `figures/` is a directory with at least one `.png`; `systems` is non-empty and every `validation.gate.gate_pass` is a `bool` (not asserted True).

§4.9 checklist before the .3 invocations:

1. Change set: `tests/integration/test_smoke_pipeline.py` (new, uncommitted); nothing under `lpcstudy/`.
2. Radius: rule "a single new test file means that file only" (§4.2); no separate manual smoke run (same evidence, "run one of them, not both"). Tier: integration. Smaller than the whole suite.
3. Already run: no, the file is new. The marker-exclusion collection `--collect-only -m unit tests/integration` is collection only and has not run.
4. Device: `JAX_PLATFORMS=cpu` (settings, and forced again in the test's subprocess env).
5. Threads and time: `LPC_THREADS=4` inherited by the subprocess; the test's own timeout is 300 s; the integration tier budget is 900 s.
6. Contention: `pgrep -fa "lpcstudy --preset"` showed no run (only the pgrep's own shell); no GPU lock needed on CPU.
7. Output: `-q --tb=short -rfE`; summary and failures only. Wall-clock taken with `time`.
8. Commands: (i) `python -m pytest --collect-only -q -m unit tests/integration` (expect 0 collected, 1 deselected); (ii) `time python -m pytest -q --tb=short -rfE tests/integration/test_smoke_pipeline.py`.

### 2026-10-10, claude-sonnet-5-5 (developer): WU-0010.3 results

- (i) `python -m pytest --collect-only -q -m unit tests/integration`: `no tests collected (1 deselected) in 0.00s`. The integration test carries only `integration` (from `tests/integration/`), so the `unit` tier excludes it.
- (ii) `python -m pytest -q --tb=short -rfE tests/integration/test_smoke_pipeline.py`: `1 passed in 66.97s (0:01:06)`; `time`: real 1m7.209s, user 1m50.325s, sys 2.663s, on the workstation, CPU, `LPC_THREADS=4`. This is under the 5 min acceptance bound and under the 300 s test timeout (baseline: 49 s). No failure, no rerun.
- Outputs asserted present: `results.json`, `RESULTS.md`, `run.log`, `figures/` with at least one `.png`; `validation.gate.gate_pass` is a `bool` for `lorenz63`. The seed is the default DEV-0 (20261005); no seed argument is passed.
- Self-check: no clip, replacement or fallback; no tolerance (only the 300 s timeout from §4.1); no randomness in the test; the subprocess env sets `JAX_PLATFORMS=cpu` and `XLA_PYTHON_CLIENT_PREALLOCATE=false` explicitly.

### 2026-10-10, claude-sonnet-5-5 (developer): fix round 1 (R1-R3), before the run

Changes: `tests/conftest.py` (R1: `pytest_collection_modifyitems` raises a `UsageError` when an item's own tier markers differ from its directory tier, and `_refuse_gpu` decides from `tier_of(request.node.path, ...)`, not from the marker; R2: a "Limits" paragraph in the guard's docstring); `tests/unit/test_conftest_markers.py` (R3: test (c) also sets `CUDA_VISIBLE_DEVICES=""` and `ROCR_VISIBLE_DEVICES=""`; R1: new test (e) `test_tier_marker_that_differs_from_directory_fails_collection`, so k becomes 5). No assertion or tolerance changed; the ast check still reports `not byte-identical: []` for the 14 moved tests and the helper. No clip, replacement or fallback added; the new `UsageError` counts and names every mismatched item.

§4.9 checklist before the run:

1. Change set: `tests/conftest.py`, `tests/unit/test_conftest_markers.py` (modified, uncommitted); nothing under `lpcstudy/`.
2. Radius: rule "`tests/conftest.py` -> the whole `unit` tier" (§4.2, gate-sized by rule), plus `tests/integration/` because the conftest applies to it. Not the whole suite: no `slow` or `gpu` test exists.
3. Already run: the files changed since the reviewer's run, so this is a new run; nothing has run on this code.
4. Device: `JAX_PLATFORMS=cpu` from the settings, not overridden.
5. Threads and time: `LPC_THREADS=4`; unit 300 s, integration 900 s; expected about 70 s.
6. Contention: no preset, `slow` or `gpu` run active.
7. Output: `-q --tb=short -rfE`, summary and failures only.
8. Command: `python -m pytest -q --tb=short -rfE tests/unit tests/integration`, once; expect 14 + 5 + 1 = 20 passed.

### 2026-10-10, claude-sonnet-5-5 (developer): fix round 1 results

- `python -m pytest -q --tb=short -rfE tests/unit tests/integration`: `20 passed in 68.34s (0:01:08)` (14 moved + k = 5 marker tests + 1 smoke). No failure, no rerun.
- **k is now 5** (was 4 at .1); the earlier "18 passed" for `tests/unit` becomes 19.
- Self-check: grep for `clip|nan_to_num|isfinite|where(|try:|except` in the diff finds only the existing `try/except ValueError` in `tier_of` and the word "except" in a docstring; no randomness; no tolerance changed. Resolution text in `## Review` is left to the main session.

### Merge gate, 2026-10-10, claude-sonnet-5-5 (main session), checklist before the run (§4.9, §4.3)

DEC-0002 confirmed by the human owner in chat (recorded in `decisions.md`); R4 is closed.

1. **Change set:** `git diff --name-only main...HEAD` lists `pytest.ini`, `tests/conftest.py`, `tests/integration/test_smoke_pipeline.py`, `tests/test_core.py` (removed), `tests/unit/` (7 split files, `unit_helpers.py`, `test_conftest_markers.py`), `decisions.md` and this file. `git status --porcelain` is empty before the records commit of this entry.
2. **Radius:** the merge gate of §4.3, tiers `unit` and `integration`, by the main session (the named role). Whole suite: `tests/unit tests/integration` (there is no `slow` or `gpu` content yet).
3. **Already run?** Yes, and I say so: the developer ran this exact set on this exact code at ff945e9 (`20 passed in 68.34s`), and no code has changed since (only records). This run is not a retry. It is the independent merge-gate run that §4.3 assigns to the main session and the work-unit process requires, on the merge candidate, and it runs once. A failure would be handled by §4.4 (fix, `--lf`, radius once).
4. **Device:** `JAX_PLATFORMS=cpu`, `XLA_PYTHON_CLIENT_PREALLOCATE=false`.
5. **Threads and time:** `LPC_THREADS=4`, `OMP/MKL/OPENBLAS_NUM_THREADS=4`, `timeout 600`.
6. **Contention:** no preset running; GPU lock free.
7. **Output:** `-q --tb=short -rfE`.
8. **Command:** `LPC_GATE=merge timeout 600 .venv/bin/python -m pytest -q --tb=short -rfE tests/unit tests/integration` with the variables above set by hand.

## Review

- **Reviewer:** reviewer, claude-opus-5-5, fresh context, 2026-10-10. Reviewed `git diff main...HEAD` (8045928, 0bd0b1c, 3cae35c, 6e306b3 on top of plan 4ea348c and merge 8967757) against the plan, amendment Q1–Q4, ROADMAP §2 rows and DEVELOPMENT_WORKFLOW §2.3, §4.
- **Independent run (§4.9, one line each).** (1) Change set: `pytest.ini`, `tests/conftest.py`, `tests/integration/test_smoke_pipeline.py`, `tests/unit/*` (8 new), `tests/test_core.py` deleted, this unit file; tree clean. (2) Radius: `tests/conftest.py` and `pytest.ini` give the whole `unit` tier (gate-sized by rule), plus `tests/integration/` because the new integration test is in the change set; the hand-derived set of §4.2 (no `tools/test_impact.py` yet); no `slow`/`gpu` tests exist. (3) Already run: not by the reviewer. (4) Device: `JAX_PLATFORMS=cpu`, `XLA_PYTHON_CLIENT_PREALLOCATE=false` (settings). (5) Threads: `LPC_THREADS`/OMP/MKL/OPENBLAS = 4. (6) Contention: `pgrep -fa "lpcstudy --preset"` empty. (7) Output: `-q --tb=short -rfE`. (8) Command: `.venv/bin/python -m pytest -q --tb=short -rfE tests/unit tests/integration`, no `LPC_GATE`, no `-n`, once. **Result: `19 passed in 63.86s (0:01:03)`** (18 unit = 14 moved + k = 4, plus 1 integration; real 1m4.4s). Tree still clean after the smoke subprocess.
- **Checks that pass.**
  - .1: markers registered in `pytest.ini` with `--strict-markers` in `addopts`; directory marker asserted on synthetic items (test (a)); misplacement raises UsageError (b); guard message with `JAX_PLATFORMS` unset (c); gpu tier unguarded (d). Reviewer collect-only check `pytest --collect-only -q -m integration tests/unit tests/integration` gives `1/19 tests collected (18 deselected)`, so directory markers are applied before `-m` filtering (the developer's `-m unit` check alone could not show this). Wrapper signatures match jax 0.11.2 (`devices(backend=None)`, `local_devices(process_index=None, backend=None, host_id=None)`).
  - .2: own `ast` comparison against `git show main:tests/test_core.py` (source text including decorators, and `ast.dump`): 15 functions (14 tests + `_moments_from_draws`), none missing, none extra, text differs: [], AST differs: []. Placement matches the plan table exactly. `tests/test_core.py` removed. First `from lpcstudy.` import names the file in oracle, allocation, statistics, embedding, dynamics; analysis and ensemble import their module at function level as in the original (Q4). No tolerance or assert changed.
  - .3: `tmp_path`, no seed argument (default `StudyConfig.seed = 20261005` = DEV-0 in `seeds/development_seeds.json`), four outputs asserted, `gate_pass` checked as `bool` at `systems.<s>.validation.gate.gate_pass` (the baseline path), not asserted True; excluded from `-m unit` and selected by `-m integration`; 64 s here, under the 300 s timeout and 5 min bound.
  - No change under `lpcstudy/`, `.claude/`, governance, or `requirements.txt`; no new dependency (`pytester` is built in). No randomness added; no clip, replacement or swallowed exception (the one `except ValueError` in `tier_of` returns `None`, which the UsageError then reports). Commits name WU-0010.k and end `Agent: claude-sonnet-5-5`. §4.9 checklist precedes every logged run. Owner checkpoint: none (no verdict, statistics, seed, provenance or dependency code).
- **Findings.**
  - **R1 (medium; correctness against the .1 criterion and §4.5). `tests/conftest.py:61` (and `:45`).** The guard and the tier are keyed on the *marker*, not the directory. A test in `tests/unit/` decorated `@pytest.mark.gpu` skips the guard (`get_closest_marker("gpu")` finds the decorator) and carries two tier markers, so it is selected by both `-m unit` and `-m gpu`. Reviewer probe (synthetic tree in the scratchpad, real `conftest.py` and `pytest.ini`, `JAX_PLATFORMS=cpu`): the test failed with jax's own `RuntimeError: Unknown backend: 'gpu'`, not the guard message, and `--collect-only -m unit` still collected it. With `JAX_PLATFORMS` unset on the workstation it would initialize CUDA from the unit tier, outside the lock: exactly the case the criterion ("a test outside `tests/gpu/` that calls `jax.devices("gpu")` fails with a clear message") must cover. A stray `@pytest.mark.slow` on a unit-dir test (which `.claude/rules/tests.md` "Speed" seems to invite) also breaks the one-tier-per-item invariant asserted by test (a). **Fix:** in `pytest_collection_modifyitems`, raise the same UsageError for any item whose own tier markers differ from its directory tier (name the item and both tiers). In `_refuse_gpu`, decide from `tier_of(request.node.path, Path(__file__).parent) != "gpu"`, not from the marker. Add marker test (e): a `@pytest.mark.gpu` probe under `tests/unit/` fails collection with that message.
  - **R2 (low; governance, honest statement of a safety control). `tests/conftest.py:55-60`.** The guard's docstring, like §4.5, reads as total ("Fail any test outside `tests/gpu/` that asks jax for a GPU device"). The limits the plan accepted (Risks R1: implicit default-device use with `JAX_PLATFORMS` unset; R2: names bound at import, such as `from jax import devices`, and a non-string backend argument) are recorded only in this unit file. A reader of the conftest, or WU-0012.1, would overestimate the control. **Fix:** add a short "Limits" paragraph to the docstring naming these cases and stating that `JAX_PLATFORMS=cpu` (settings, then `tools/run_tests.sh`, WU-0012.1) is the primary control and this guard is the backstop.
  - **R3 (low; §4.5, GPU contention). `tests/unit/test_conftest_markers.py:63-64`.** Test (c) deletes `JAX_PLATFORMS` in a unit-tier subprocess. If the guard ever regresses, that subprocess calls the real `jax.devices("gpu")` and initializes CUDA on the workstation without the lock. **Fix:** keep `JAX_PLATFORMS` unset, as the criterion requires, but also set `CUDA_VISIBLE_DEVICES=""` (and `ROCR_VISIBLE_DEVICES=""`) for that subprocess. A regressed guard then fails the `fnmatch` without touching the device; the passing path is unchanged.
  - **R4 (low; governance, owner record; main session, not the developer). Plan amendment, lines 115-122.** Q1–Q3 answer questions addressed to the owner, and they depart from the literal ROADMAP §2 criteria: bare `tests` is not collected; 18 passed, not "exactly 14"; `git diff -M` does not detect renames. Each substitute check is equal or stricter, and I accept the evidence. However, §2.3 and QA.6 require a wrong criterion to be recorded as a decision for the owner, and `docs/agent/records/decisions.md` has no WU-0010 entry. **Fix:** the main session appends a decision entry, or adds the item to the owner's referral batch, recording Q1–Q4 for owner confirmation. No code change.
  - Note, not a finding (out of the developer's scope, which excludes `.claude/` and governance): text that still names `tests/test_core.py` as the live suite is now stale. It is in `.claude/rules/test-discipline.md:18`, `.claude/skills/test-impact/SKILL.md:27`, DEVELOPMENT_WORKFLOW §4.1 (line 89) and §4.2 (line 138), and ROADMAP line 11. Most of these phrases are conditional ("until WU-0010"); the main session may queue an update.
- **Verdict: approve with fixes.** 4 findings (R1 medium, R2–R4 low). R1–R3 go to the developer. R4 is for the main session. A re-review covers R1–R3 as fixed or disputed.

### Re-review, fix round 1, 2026-10-10, reviewer (claude-opus-5-5), fresh context

Scope: R1–R3 only, as of commit ff945e9 (`git show ff945e9`) and the developer's fix-round log. I ran no tests. No code has changed since the developer's single run at this commit (`20 passed in 68.34s (0:01:08)`, = 14 moved tests + k = 5 marker tests + 1 smoke).

- **R1: fixed.**
  - `pytest_collection_modifyitems` reads each item's own tier markers before adding the directory marker. When they exist and differ from `[tier]`, it lists `nodeid (directory tier, markers)` and raises a `UsageError` after the misplacement check. Each mismatch is counted and named, not dropped silently.
  - `_refuse_gpu` now takes `tier = tier_of(request.node.path, Path(__file__).parent)` and returns early only for `"gpu"`. The failure message uses that directory tier.
  - The new test (e), `test_tier_marker_that_differs_from_directory_fails_collection`, builds the case I probed: a `@pytest.mark.gpu` test under `tests/unit/`, run with the real conftest and pytest.ini copies. It asserts `ExitCode.USAGE_ERROR` and the message with `directory tier 'unit'` and `gpu`. Under the pre-fix conftest that tree collects with exit 0, so (e) would have failed.
- **R2: fixed.** The "Limits" paragraph is accurate. It names the guard as a backstop with `JAX_PLATFORMS=cpu` as the primary control, plus the three uncaught cases I listed: implicit default-device use, a name bound at import, and a non-string backend.
  - Non-blocking suggestion: one sentence such as "only `jax.devices` and `jax.local_devices` are wrapped; other entry points (e.g. `jax.extend.backend.get_backend`, which exists in jax 0.11.2) and child processes are not guarded" would make the scope explicit. This is not required to close R2.
- **R3: fixed.** Test (c) keeps `JAX_PLATFORMS` deleted and sets `CUDA_VISIBLE_DEVICES=""` and `ROCR_VISIBLE_DEVICES=""` through `monkeypatch.setenv`, which `runpytest_subprocess` inherits. Its assertions are unchanged.
- **Invariants re-checked independently.**
  - My own `ast` comparison against `git show main:tests/test_core.py` covers the source text including decorators and the `ast.dump`. All 15 functions (14 tests + `_moments_from_draws`) are present, none extra; text differs: [], AST differs: [].
  - `git diff 6e306b3 ff945e9` outside `tests/` and this unit file is empty.
  - No assertion was removed or weakened. The fix only adds lines to (c), adds (e) and adds a UsageError branch. The log diff removes no earlier line.
- **Procedural note (not a finding).** §2.3 asks the developer to answer under each finding (`fixed in <commit>`). The developer's log leaves that to the main session, so the main session should record `fixed in ff945e9` for R1–R3. R4 (owner decision record for Q1–Q4) is still open with the main session and is required before merge under "approve with fixes".
- **Verdict: approve.** R1–R3 are fixed, with no open developer findings. Merge after the main session closes R4.

### Resolution of findings, 2026-10-10, claude-sonnet-5-5 (main session)

- **R1: fixed in ff945e9** (re-review: fixed).
- **R2: fixed in ff945e9** (re-review: fixed; the reviewer's optional sentence naming the only wrapped entry points is not adopted, because the Limits paragraph already lists them).
- **R3: fixed in ff945e9** (re-review: fixed).
- **R4: recorded as `DEC-0002` in `docs/agent/records/decisions.md`, proposed, for owner confirmation.** The merge to `main` waits for it.

- **Correction to the R2 line above (main session, 2026-10-10).** The stated reason for not adopting the reviewer's optional sentence was wrong: the Limits paragraph (`tests/conftest.py:75-79`) does not say that only `jax.devices` and `jax.local_devices` are wrapped, nor that child processes are unguarded. The sentence is not adopted because it is optional and non-blocking, and a comment-only change after review would need another radius run; it is left as a note for the next change to `tests/conftest.py`.

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:

## Referral

<only if halted; use the form in agent-instructions.md, LPC.AI.13>
