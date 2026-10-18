# WU-0004g: Fixes of the two failures of merge gate 2026-10-18c (develop 1b263d7)

| Field | Value |
| --- | --- |
| Status | in progress |
| Class | CSQ3 development; test-only changes (no `lpcstudy/` change) |
| Agent(s) | claude-sonnet-5-5 (developer), on the request of the main session |
| Estimate | XS |

## Plan (written before execution)

Branch `wu/0004g-gate-fixes` from develop 226667b.

- **F1** `tests/integration/test_clip_failure.py`: since WU-0004f the counters of the `clip_sensitivity` subtree are mirrored in `systems/<s>/handling/result_counts` under keys `clip_sensitivity/...`; `comparable()` dropped only the subtree, so the normal and failed runs differ in the mirrors (e.g. `n_caught_exceptions` 0 vs 1, 13 more items). Fix: `comparable()` also drops those mirror keys (they are the subtree's leaves); everything else stays compared bitwise. Add: the mirror `clip_sensitivity/n_caught_exceptions` is `>= 1` in the failed run and `== 0` in the normal run (the failure is counted: the intent of the test). Docstring updated. The cause was my WU-0004f change; its radius did not include the integration test.
- **F2** `tests/unit/test_tools_run_preset.py::alive` (a test helper): reading `/proc/<pid>/stat` of a process that vanished raises `ProcessLookupError`, not `FileNotFoundError`; treat both as "not alive", keep the zombie handling, change no assertion. Add a tiny test of the helper (a pid beyond `pid_max` is not alive; this process is).
- **Acceptance:** F1 integration test passes once (`run_tests.sh integration tests/integration/test_clip_failure.py`); F2 `tests/unit/test_tools_run_preset.py` passes once. No tolerance or assertion loosened; no `lpcstudy/` change.

## Log

**Flakiness finding (for the main session's defect entry).** `test_background_run_has_the_checks_of_the_front_end` failed once in the merge gate with `ProcessLookupError` in `alive(pid)` (`Path('/proc/<pid>/stat').read_text()`): a race in the test helper (the process vanishes between the existence check and the read), unrelated to WU-0004f. Observed once in three gates; it passed in the two previous ones. Fixed in the helper (F2), not retried. The main session will open the defect entry.

**Test-run checklist (§4.9), both runs.** (1) Change set: `tests/integration/test_clip_failure.py`, `tests/unit/test_tools_run_preset.py`, this file (no `lpcstudy/` or `tools/` change). (2) Radius: each changed test file only (§4.2: a single test file); not the whole suite, not a gate. (3) Not run on this code (the gate ran the old test code). (4) CPU (wrapper). (5) `LPC_THREADS` 4; unit 300 s, integration 900 s. (6) No `lpcstudy --preset` or test run active (checked with `ps`). (7) `-q --tb=short -rfE`. (8) `LPC_PYTHON=.../lpcstudy/.venv/bin/python tools/run_tests.sh unit tests/unit/test_tools_run_preset.py` and `... integration tests/integration/test_clip_failure.py`.
