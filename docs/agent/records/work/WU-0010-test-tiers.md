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

## Review

- **Reviewer:** <actor, not the author>
- **Findings and resolution:**

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:

## Referral

<only if halted; use the form in agent-instructions.md, LPC.AI.13>
