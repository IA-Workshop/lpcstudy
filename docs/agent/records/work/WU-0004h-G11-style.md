# WU-0004h-G11: style review, golden_rehearsal, two fixture extract scripts and the V7 tests

| Field | Value |
| --- | --- |
| Status | in progress |
| Class | CSQ3 development |
| Agent(s) | claude-sonnet-5-5 under the owner's code review of 2026-10-18 (common brief `/tmp/claude-1000/style_brief.md`, group G11) |
| Estimate | seconds of CPU; no GPU |

## Plan (written before execution)

- **Scope:** `tests/unit/golden_rehearsal.py`, `tests/unit/fixtures/pilot_schema/extract_paths.py`, `tests/unit/fixtures/rehearsal_report/extract_p0p1.py`, and in `tests/unit/test_validation.py` only the module docstring and the docstrings of the V7 and gate tests (first 380 lines, up to `test_gate_status_requires_and_reports_v7`). Docstrings, comments and American spelling only. The golden fixture files are not touched.
- **Definition of done:** (1) docstrings plain, NumPy style, American; (2) black 26.10.1 clean; (3) AST of each file equal to `develop` with docstrings ignored; (4) dead-code audit reported; (5) `test_validation.py` and `test_tools_rehearsal_common.py` pass once.
- **Acceptance criteria:** no code, name, printed string, golden text, tolerance or assertion changes (PRIME.2). The first paragraph of the `extract_paths.py` module docstring is the argparse `--help` description, so it stays byte-identical.
- **Affected checks:** `tests/unit/test_validation.py` (edited) and `tests/unit/test_tools_rehearsal_common.py` (imports `golden_rehearsal`). The two extract scripts are imported by no test.

## Log

### 4.9 checklist before the unit run

1. Change set: the four files above plus this unit file (`git status --porcelain`).
2. Radius (section 4.2, by hand): a test file maps to itself; `golden_rehearsal.py` maps to its importer `test_tools_rehearsal_common.py`; the extract scripts have no importer (grep). No whole suite, no integration tier.
3. Already run on this code: no; first run after all edits.
4. Device: the wrapper sets `JAX_PLATFORMS=cpu`; no GPU.
5. Threads and timeout: `LPC_THREADS` default 4; unit timeout 300 s.
6. No preset or pilot run involved; no smoke run (none of the files is imported by `lpcstudy/`).
7. Output: wrapper flags only; the summary and failures are recorded.
8. Command: `LPC_PYTHON=.../lpcstudy/.venv/bin/python tools/run_tests.sh unit tests/unit/test_validation.py tests/unit/test_tools_rehearsal_common.py`.

### Complexity audit

- `golden_rehearsal.py`: `GOLDEN`, `produce`, `main` are used by `test_tools_rehearsal_common.py` and the golden README (grep). Nothing is dead.
- `extract_paths.py`: every function is used by `main`; the script itself is a documented generator for committed fixtures. `extract_p0p1.py`: same. No removal.
- Line counts before/after: golden_rehearsal 201/275, extract_paths 157/219, extract_p0p1 84/111, test_validation 1128/1237 (docstrings only).

### Verification

- AST: `extract_paths.py`, `extract_p0p1.py`, `test_validation.py` print "AST equal (docstrings ignored)". `golden_rehearsal.py` prints "AST DIFFERENT" from the helper because the file has attribute docstrings (bare strings after `DIAGNOSTIC_OPTIONS` and `STACK_LINE`); with a script that drops every bare string statement the ASTs are equal.
- black 26.10.1 `--check`: 4 files unchanged.

### Flagged runtime names (not changed)

- `golden_rehearsal.py`: private functions `_normalise_text` and `_normalise_json` carry British spelling in their names; they are used only in this file and were not renamed (the brief forbids changing names).

### Results

- `tools/run_tests.sh unit tests/unit/test_validation.py tests/unit/test_tools_rehearsal_common.py`: `37 passed in 7.10s` (run once, after all edits).
- Status: done (awaiting review). No smoke run (no file is imported by `lpcstudy/`).
