# WU-0004h-G10: style review, shared test files, tier tests and shell wrappers

| Field | Value |
| --- | --- |
| Status | done (awaiting review) |
| Class | CSQ3 development |
| Agent(s) | claude-sonnet-5-5 under the owner's code review of 2026-10-18 (common brief `/tmp/claude-1000/style_brief.md`, group G10) |
| Estimate | a few minutes of CPU for the unit tests; no GPU |

## Plan (written before execution)

- **Scope:** `tests/conftest.py`, `tests/integration/*.py`, `tests/slow/*.py` (including `wu0006_harness.py` and `wu0006_reference.py`), `tests/gpu/*.py`, the unit files that no module group owns (`test_conftest_markers.py`, `test_gpu_reproducibility_probe.py`, `test_tools_run_tests.py`, `test_tools_run_preset.py`, `unit_helpers.py`, `wrapper_helpers.py`) and the shell scripts `tools/run_tests.sh`, `tools/run_preset.sh`, `tools/owner_freeze_run.sh` (comments and header only). Out: `tests/unit/golden_rehearsal.py` (it produces the goldens of the rehearsal tools, so it belongs with the rehearsal-tool group), every fixture, every other file.
- **Definition of done:** (1) black 26.10.1 clean and idempotent; (2) every docstring plain and NumPy style, American spelling; (3) complexity audit done, dead code removed with grep evidence; (4) AST of every Python file equal to `develop` except for the listed removals; (5) the unit files of this group pass once; (6) the integration, slow and gpu files are verified by AST equality only (the main session runs the gates); (7) the three shell scripts pass `bash -n`, their code lines are unchanged, and the usage text of `owner_freeze_run.sh` (lines 2 to 18) is byte-identical.
- **Acceptance criteria:** no tolerance, seed, reference or assertion changes (PRIME.2). No golden fixture regenerated. No runtime string that reaches results.json, RESULTS.md, logs or pinned error messages changed.
- **Affected checks:** unit files of this group, plus `test_tools_gpu_hours.py` (it imports `wrapper_helpers`). Integration, slow and gpu tiers are not run here.

## Log

### 4.9 checklist before the unit run

1. Change set: `git status --porcelain` lists only the files of the scope above plus this unit file; `git diff --name-only develop...HEAD` adds nothing else.
2. Radius (DEVELOPMENT_WORKFLOW.md section 4.2, by hand): a test file maps to itself; `wrapper_helpers.py` maps to its importers `test_tools_run_tests.py`, `test_tools_run_preset.py` and `test_tools_gpu_hours.py`; `unit_helpers.py` changed in docstrings only (AST equal), its importers are in other groups and unaffected. Integration, slow and gpu files are not run here.
3. Already run: no, first run after all edits.
4. Device: the wrapper sets `JAX_PLATFORMS=cpu`.
5. Threads and timeout: `LPC_THREADS` default 4; unit timeout 300 s.
6. Contention: CPU only, no preset or GPU job started.
7. Output: wrapper uses `-q --tb=short -rfE`.
8. Command: `LPC_PYTHON=/home/brianm/projects/physics/chaos/lpcstudy/.venv/bin/python tools/run_tests.sh unit tests/unit/test_conftest_markers.py tests/unit/test_gpu_reproducibility_probe.py tests/unit/test_tools_run_tests.py tests/unit/test_tools_run_preset.py tests/unit/test_tools_gpu_hours.py`.

### Results

- **Unit run (once, after all edits):** `LPC_PYTHON=... tools/run_tests.sh unit tests/unit/test_conftest_markers.py tests/unit/test_gpu_reproducibility_probe.py tests/unit/test_tools_run_tests.py tests/unit/test_tools_run_preset.py tests/unit/test_tools_gpu_hours.py` gave `235 passed in 10.01s`. No test was edited to pass and no tolerance, seed or assertion changed.
- **Integration, slow and gpu files were NOT run** (the main session runs the gates). They are verified by AST equality only, see below.
- **Smoke bitwise comparison (brief item d):** not run. None of the files of this group is imported by `lpcstudy/`, so the unit tests and the AST checks suffice (brief, "Tools groups").
- **Black:** `uvx black==26.10.1` on all 25 Python files, then `--check`: `25 files would be left unchanged` (idempotent). Shell scripts: `bash -n` passes on the three scripts; black does not apply.
- **Line counts (before = develop, after; lines)**, mostly growth from the one-item-per-line rule and fuller docstrings:

| File | Before | After |
| --- | --- | --- |
| `tests/conftest.py` | 105 | 148 |
| `tests/gpu/test_reproducibility.py` | 333 | 502 |
| `tests/integration/test_cli_seeds.py` | 95 | 156 |
| `tests/integration/test_clip_failure.py` | 95 | 162 |
| `tests/integration/test_lm_doubling_probe.py` | 115 | 224 |
| `tests/integration/test_preset_wrapper.py` | 138 | 252 |
| `tests/integration/test_smoke_pipeline.py` | 220 | 352 |
| `tests/integration/test_states_dump.py` | 231 | 393 |
| `tests/slow/test_analysis_coverage.py` | 151 | 209 |
| `tests/slow/test_analysis_logrank_size.py` | 91 | 144 |
| `tests/slow/test_analysis_null_delta_r2.py` | 142 | 200 |
| `tests/slow/test_p2_bound.py` | 96 | 154 |
| `tests/slow/test_rehearsal_diagnostics_mc.py` | 98 | 161 |
| `tests/slow/test_rehearsal_report_mc.py` | 94 | 142 |
| `tests/slow/test_start_states.py` | 174 | 271 |
| `tests/slow/test_statistics_coverage.py` | 112 | 158 |
| `tests/slow/test_wu0006_harness.py` | 790 | 1298 |
| `tests/slow/wu0006_harness.py` | 1080 | 1621 |
| `tests/slow/wu0006_reference.py` | 171 | 305 |
| `tests/unit/test_conftest_markers.py` | 98 | 135 |
| `tests/unit/test_gpu_reproducibility_probe.py` | 98 | 179 |
| `tests/unit/test_tools_run_tests.py` | 331 | 474 |
| `tests/unit/test_tools_run_preset.py` | 718 | 1205 |
| `tests/unit/unit_helpers.py` | 51 | 111 |
| `tests/unit/wrapper_helpers.py` | 148 | 204 |
| `tools/run_tests.sh` | 137 | 143 |
| `tools/run_preset.sh` | 312 | 324 |
| `tools/owner_freeze_run.sh` | 176 | 181 |
| total | 6400 | 9808 |

### AST checks (brief item a, `/tmp/claude-1000/ast_compare.py`, docstrings ignored)

`AST equal (docstrings ignored)` for 21 of the 25 Python files: `tests/conftest.py`, all six `tests/integration/*.py`, `tests/gpu/test_reproducibility.py`, `tests/slow/test_analysis_coverage.py`, `test_analysis_logrank_size.py`, `test_analysis_null_delta_r2.py`, `test_p2_bound.py`, `test_rehearsal_diagnostics_mc.py`, `test_rehearsal_report_mc.py`, `test_start_states.py`, `test_statistics_coverage.py`, `wu0006_reference.py`, `tests/unit/test_conftest_markers.py`, `test_gpu_reproducibility_probe.py`, `test_tools_run_tests.py` and `unit_helpers.py`. Black, the reflow of docstrings and comments, and the moves of trailing comments above their lines changed no AST.

### Code changes (brief item b)

The four files below differ in AST from `develop`; for each, the difference was confirmed to be exactly the listed change by applying that change to the `develop` text and comparing again (`equal`).

| File | Change | Reason and evidence |
| --- | --- | --- |
| `tests/unit/wrapper_helpers.py` | Removed the constant `FAKE_FLOCK` (a fake `flock` script text). | Dead code. `grep -rn FAKE_FLOCK .` finds only its definition. `test_tools_run_tests.py::test_gpu_tier_default_wait_is_30_s` writes its own inline fake with `write_script`. |
| `tests/slow/wu0006_harness.py` | Removed the function `_rate(count, total)`. | Dead code. `grep -rn "_rate(" tests` finds only the definition. |
| `tests/slow/wu0006_harness.py` | Renamed the local variable `centre` to `center`. | American spelling of an identifier; local to `_bootstrap_plan`. |
| `tests/slow/wu0006_harness.py` | Turned the seven bare-string attribute "docstrings" (after `ASSERT_ROADMAP_BOUNDS`, `WU0006_SEED`, `C6_CORR`, `VERDICT_LEVEL`, `DELTA_Q15` and the two `Evaluation` fields) into comments above the attribute. | A bare string after an assignment is a no-op statement that tools do not read; a comment says the same and wraps at 80 columns. No value changed. |
| `tests/slow/test_wu0006_harness.py` | Renamed the local variable `centred` to `centered` in `test_ar1_has_the_stated_lag1_and_variance`. | American spelling of an identifier. |
| `tests/unit/test_tools_run_preset.py` | Removed the redundant `import os` inside `test_alive_is_false_for_a_pid_that_does_not_exist_and_true_for_this_process`. | `os` is already imported at module level (line 14 of `develop`). |

No test was removed. No public name used outside this group changed (grep of the whole repository for each removed name found no other user).

### Shell scripts (comments and headers only)

- `tools/run_tests.sh`, `tools/run_preset.sh`: the header comment was rewritten in plain language (a "why this script exists" paragraph added; American spelling; "folder", "study command" instead of jargon). The phrase "ignores SIGHUP like nohup" was kept on purpose because `test_script_has_no_second_entry_point` removes exactly "like nohup" before it checks that the script has no `nohup`. The diff of the non-comment, non-blank lines against `develop` is empty for both scripts (`diff <(grep -v '^\s*#' old | grep -v '^$') <(...)` printed nothing).
- `tools/owner_freeze_run.sh`: lines 2 to 18 are printed as the usage text (`sed -n 2,18p "$0"`), so they are byte-identical (`diff` of the two ranges is empty). A plain-language paragraph was added after line 18. One no-op command was removed from `preflight`: `git diff --quiet 2>/dev/null || true` (it prints nothing and its status is discarded). All other code lines are unchanged.

### Items for the main session

- **Runtime strings that are not American or are long:** none are British (grep for British forms found none). Long string literals that black does not split remain over 80 columns (messages in `tests/gpu/test_reproducibility.py`, `tests/slow/wu0006_harness.py`, `tests/conftest.py`, `tests/integration/test_preset_wrapper.py`, `test_states_dump.py`, `tests/slow/test_p2_bound.py`, `test_start_states.py`, `tests/unit/wrapper_helpers.py` fake-interpreter source) and a few long test function names. They are runtime or pinned strings; splitting would be a code change.
- **Markdown tables** in the module docstrings of `test_analysis_coverage.py` and `test_analysis_null_delta_r2.py` stay wider than 80 columns (wrapping would break the table).
- **Not touched, flagged:** `tests/unit/golden_rehearsal.py` (belongs with the rehearsal-tool tests), `C7_INCONCLUSIVE_REFERENCE` in `tests/slow/wu0006_reference.py` (no code user, but two records cite it by name and it is pre-registered reference data, so it stays).
- **Possible consolidation not done (the slow, integration and gpu tiers cannot be run here):** the same `pool` and `cache` fixtures are repeated in four `tests/slow/test_*.py` files and could move to a `tests/slow/conftest.py`; `leaves`/`run_smoke` helpers are repeated in `tests/integration/test_clip_failure.py`, `test_states_dump.py` and `tests/gpu/test_reproducibility.py`.
