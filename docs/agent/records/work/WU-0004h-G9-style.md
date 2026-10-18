# WU-0004h-G9: owner's code review (2026-10-18), group G9: tools ledger, gpu_hours, lm_doubling, test_impact

| Field | Value |
| --- | --- |
| Status | in progress |
| Class | CSQ3 development |
| Agent(s) | claude-sonnet-5-5 |
| Estimate | small (formatting, docstrings, small simplifications) |

## Plan (written before execution)

- **Scope:** apply the owner's four review comments (black at 80 columns, one item per line, pedagogical American-English docstrings, complexity reduction) to `tools/lm_doubling.py`, `tools/gpu_hours.py`, `tools/ledger.py`, `tools/test_impact.py` and the tests `tests/unit/test_tools_lm_doubling.py`, `test_tools_gpu_hours.py`, `test_tools_test_impact.py`. Out: the owner-only seal script and the shell scripts (not touched), `tests/integration/test_lm_doubling_probe.py` (group G10), every other file. `tools/ledger.py` has no test file.
- **Definition of done:** behavior unchanged (no numeric result, no CLI output, no string that reaches a result file); `ledger verify` prints `ledger chain intact` and `ledger status` is unchanged; the stored offline `lm_doubling.py compare` over the DEV-0 inputs is byte-identical; the unit tests of the three test files pass; black 26.10.1 is idempotent.
- **Acceptance criteria:** (a) the AST of files with no code change equals develop's up to docstrings; (b) every code change is listed below with its reason; (c) the three test files run once, all pass, no tolerance touched; (d) the smoke compare is not needed, because nothing in `lpcstudy/` imports these tools (grep: `lpcstudy/budget.py` only names `lm_doubling_dev0_report_v3.md` in text).
- **Affected checks:** `tests/unit/test_tools_lm_doubling.py`, `tests/unit/test_tools_gpu_hours.py`, `tests/unit/test_tools_test_impact.py` (rule: a `tools/<t>.py` change maps to `tests/unit/test_tools_<t>.py`, DEVELOPMENT_WORKFLOW 4.2; `tools/ledger.py` has none).

## Log

### Edits (2026-10-18)

Line counts before (develop 6ddf9cb) and after (`wc -l`); black's one-item-per-line layout and the longer docstrings make the files grow:

| File | Before | After |
| --- | --- | --- |
| tools/lm_doubling.py | 1906 | 3216 |
| tools/gpu_hours.py | 325 | 441 |
| tools/ledger.py | 160 | 241 |
| tools/test_impact.py | 547 | 775 |
| tests/unit/test_tools_lm_doubling.py | 1474 | 2685 |
| tests/unit/test_tools_gpu_hours.py | 416 | 749 |
| tests/unit/test_tools_test_impact.py | 800 | 1165 |

Code changes (everything else is docstrings, comments, black layout, and splitting a long string literal into two adjacent literals with the same value; the AST was compared against develop's with docstrings ignored):

- `tools/ledger.py`: none (AST equal). `--help`, `verify` and `status` output compared with develop's.
- `tools/gpu_hours.py`: (1) `Run.path` removed: never read (`load_run` stored it, nothing used it). (2) `tally_week(..., walk_errors)` takes `walk_errors` as a required argument: the only caller passes it, so the `or []` default could not run. (3) `existing_roots` keeps only the roots that are directories: the dedup by resolved path was redundant, because `find_meta_files` already counts each file once and records an unreadable directory once by name. (4) `build_parser` description is the same text as before, written as a string literal instead of `__doc__.split("\n")[0]`, so that the module docstring could be rewritten without changing `--help`. (5) `main` binds `repo` in a local before `default_roots`. `--help` output is identical.
- `tools/test_impact.py`: (1) `_test_files` binds `folder` before the glob (layout). (2) `pytest_commands` tests `p.rstrip("/") in WHOLE_SUITE` only: every member of `WHOLE_SUITE` is its own stripped form or strips to a member, so the second test `p in WHOLE_SUITE` was redundant.
- `tools/lm_doubling.py`: (1) `strict_flag` removed (a wrapper that only forwarded to `budget.below_tenth`); its two callers call `budget.below_tenth` directly; the test that called it now calls `lm.budget.below_tenth` with the same assertions. (2) `_stored_choice` removed (used once; inlined as `_walk(arms[k], ("systems", system, "fitted", "chosen_K"))`). (3) The `Path_ = tuple` alias removed; annotations say `tuple`. (4) `doubling_stats(..., tolerance=TOLERANCE)`: the parameter was never varied (all callers use the default, and `chi2_stats` already used the constant); the constant `TOLERANCE` is used directly. (5) `build_parser` description: the same text as before, as a literal (same reason as in gpu_hours). (6) In `classify`, the trailing `# M7 ...` comment on the `if structural:` line moved to the lines above it (black layout).
- `tests/unit/test_tools_lm_doubling.py`: (1) `lm.strict_flag` calls became `lm.budget.below_tenth` (same arguments, same asserted values). (2) The test `test_def0028_r1_infinite_bound_is_not_labelled_endpoint_limited` was renamed `..._not_labeled_...` (American spelling; the old name appears in earlier records). (3) The local `check = lambda ...` in `test_precondition_mismatches_name_each_difference` became a local `def check(...)` (black would otherwise leave an over-long line); same call.
- `tests/unit/test_tools_gpu_hours.py`, `tests/unit/test_tools_test_impact.py`: no code change (AST equal to develop's, docstrings ignored).

Removed symbols and the evidence of no other caller (`grep -rn` over `lpcstudy/`, `tools/`, `tests/`, the shell scripts and the markdown files outside the records): `strict_flag` (only `tools/lm_doubling.py` and `tests/unit/test_tools_lm_doubling.py`), `_stored_choice` (only `tools/lm_doubling.py`), `Path_` (only `tools/lm_doubling.py`), `Run.path` (only `tools/gpu_hours.py`). 4 symbols removed, 0 tests removed.

Runtime strings with non-American spelling: none found in the seven files (grep for the usual British forms). One test identifier was renamed (above).

Behavior checks done before any test run:

- `python3 tools/ledger.py verify` prints `ledger chain intact`; `status` output is identical to the output before the edit (diff empty); `--help` identical.
- `tools/lm_doubling.py compare k15 k30 k60 --probe probe-pilot/pilot/probe_pilot.json --json ...` over the stored inputs in `lpcstudy-wt/run/lm-post/runs/dev/wu0005-6/`: exit 0; stdout sha256 `41c6e6487d71...` and JSON sha256 `633558134...`, equal to the manifest hashes of `pilot-compare-v3.txt` and `.json`; checked before the edits, after the code changes, and after the docstring pass.
- `--help` of `lm_doubling.py` and `gpu_hours.py` identical to develop's.

### Test run

4.9 checklist before the invocation:

1. Change set: `git status --porcelain`: the seven files above plus this unit file (branch `wu/style-g9` from develop 6ddf9cb).
2. Radius: rule of 4.2 for `tools/<t>.py`: `tests/unit/test_tools_lm_doubling.py`, `tests/unit/test_tools_gpu_hours.py`, `tests/unit/test_tools_test_impact.py`, unit tier; far smaller than the whole suite; no gate.
3. Already run: no (first run on this code).
4. Device: the wrapper sets `JAX_PLATFORMS=cpu`.
5. Threads and time: `LPC_THREADS` default 4; the wrapper's unit timeout applies.
6. Contention: none needed (CPU only, no preset).
7. Output: the wrapper uses `-q --tb=short -rfE`.
8. Command: `LPC_PYTHON=/home/brianm/projects/physics/chaos/lpcstudy/.venv/bin/python tools/run_tests.sh unit tests/unit/test_tools_lm_doubling.py tests/unit/test_tools_gpu_hours.py tests/unit/test_tools_test_impact.py`.

Result (once, after all edits, commit c81fd03): `231 passed in 6.08s` for the three files. No tolerance in any assert or approx was changed.

After the run, unchanged by any code edit: `compare` over the stored DEV-0 inputs again byte-identical (stdout `41c6e6487d71...`, JSON `633558134...`, exit 0); `ledger verify` prints `ledger chain intact`; `ledger status` identical to before. `uvx black==26.10.1 --check` on the seven files: unchanged (idempotent). The usage text of the `compare` and `probe` subcommands differs between develop's file and this one only when the old file is run under a different file name (argparse wraps the usage by the length of the program name); with the same name the help texts are identical.

No smoke run: nothing in `lpcstudy/` imports these tools (they import `lpcstudy`, not the reverse).

## Review

- **Reviewer:** pending
- **Findings and resolution:**

## Audit

- Is the definition of done met? See the Log.
- Defects recorded: none.
- Notes for successors: test names longer than 80 columns are left as they are (black cannot wrap an identifier): six in `test_tools_lm_doubling.py`.
