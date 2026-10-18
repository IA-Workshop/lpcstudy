# WU-0004h-G6: style review of report.py, budget.py, clip_sensitivity.py and their tests

| Field | Value |
| --- | --- |
| Status | in progress |
| Class | CSQ3 development |
| Agent(s) | claude-sonnet-5-5 |
| Estimate | one session |

## Plan (written before execution)

- **Scope:** the owner's code review of 2026-10-18 (common brief `/tmp/claude-1000/style_brief.md`), applied to group G6: `lpcstudy/report.py`, `lpcstudy/budget.py`, `lpcstudy/clip_sensitivity.py`, and their tests `tests/unit/test_report.py`, `tests/unit/test_budget.py`, `tests/unit/test_clip_sensitivity.py`. Out of scope: every other file.
- **Definition of done:** (1) the six files formatted by `black==26.10.1` at 80 columns and idempotent; (2) every module, class, function and test docstring rewritten in NumPy style, plain language, American spelling; (3) dead code, forwarding wrappers and never-varied parameters removed where no caller outside the group exists; (4) no behavior change.
- **Acceptance criteria:** (a) AST of each file equals the develop version apart from the deliberately listed changes (below); (b) `RESULTS.md`, `results.json` and the four PNG figures rendered from a stored smoke `results.json` are byte-identical before and after; (c) unit tests of the files and their importers pass with no tolerance changed; (d) the DEV-0 smoke run compares as tier T0, 13914 leaves all equal.
- **Affected checks:** `tools/test_impact.py --base develop` (listed in the Log).

## Log

### Changes by file (code-level changes; everything else is docstring, comment or layout)

lpcstudy/report.py
- Removed `_qn_primary_reading` (one caller; inlined into `verdicts`), `_lm_number` and `_lm_ratio` (`_lm_number` equals `_fmt` for every finite or `None` input; they differ only for a NaN, which `estimation.lm_block` never stores because it uses `finite_or_none`; the ratio is a local helper of `_lm_lines`).
- Merged the three `from .budget import` hunks (with their `# --- WU-0008.x begin/end ---` markers, which no tool reads) into one import.
- `write_markdown` split into `_verdict_rows`, `_allocation_lines`, `_validation_lines` and `_robustness_lines`; the gate-line insertion by `list.index` is replaced by building the list in order. `make_figures` uses `_new_figure` and `_save_figure` (the same calls in the same order: `tight_layout`, `caption_figure`, `savefig`, `close`).
- `_clip_text` merges the H1c and H3a branches (identical code), `Q-N`/`H3b` use `in`, and `_invariance_text` is shared with the H2a branch.
- The gate words use a small dict instead of a nested conditional (same three outputs).
- Attribute docstrings (bare strings after constants) became comments.

lpcstudy/budget.py
- Removed `NO_INTERVAL_KEYS` (no reader anywhere in lpcstudy/, tools/, tests/, docs).
- `_oracle_cell`: the `oracle_change_share(...)` call is bound to a name before it is formatted (same value).
- Attribute docstrings became comments.

lpcstudy/clip_sensitivity.py
- Removed `TIERS` (no reader: the module docstring describes the tiers).
- Removed the `clip` parameter of `perturb_moments` and `perturb_errors` (always the default `ERROR_CLIP`; callers are all in this group and none passes it); the body uses `ERROR_CLIP` directly (same value, same operations).
- `_block`, `_guarded` and `_compute` take `caught` as a required argument (the only callers pass it; the `None` default branches could not run). `n_caught_exceptions` counting is unchanged.
- The explanatory text after `# noqa: BLE001` moved to a comment line above the `except`.

tests (no assertion, reference or tolerance changed)
- test_report.py: renamed `..._is_labelled_report_only_...` to `..._is_labeled_report_only_...` and shortened three test names that exceeded 80 columns in the `def` line: `test_key_numbers_of_h1a_h1b_h1d_show_fail_and_inconclusive_with_the_reason` -> `test_key_numbers_h1_show_fail_and_inconclusive_with_reason`, `test_handling_section_lists_only_nonzero_counters_with_blocks_and_denominators` -> `test_handling_section_lists_only_nonzero_counters`, `test_markdown_flags_inconclusive_rows_and_leaves_the_gain_bound_without_a_flag` -> `test_markdown_flags_inconclusive_rows_gain_bound_has_none`. Two module-level docstring strings became comments.
- test_budget.py: renames for the same reason (`..._labelled_...` -> `..._labeled_...` and four long names); one list comprehension in `test_lm_development_note_under_every_table` became a loop (same expression, same expected list).
- test_clip_sensitivity.py: nine long names shortened (listed in the hand-back); the `lambda` stub in T1 became a local `def` (same body).
- No test was removed.

### Verification so far
- Rendering check (bitwise): `RESULTS.md`, `results.json` and the four PNGs rendered from the stored smoke `results.json` of `runs/refactor-base3/smoke` with the develop code and with this branch are byte-identical (`diff`, `cmp`).
- Black: `uvx black==26.10.1 --check` on the six files: unchanged (idempotent). No line over 80 columns.

### 4.9 checklist before the unit-test run
1. Change set: `lpcstudy/report.py`, `lpcstudy/budget.py`, `lpcstudy/clip_sensitivity.py`, `tests/unit/test_report.py`, `tests/unit/test_budget.py`, `tests/unit/test_clip_sensitivity.py`, this unit file (`git diff --name-only develop...HEAD` plus `git status --porcelain`).
2. Radius: `python3 tools/test_impact.py --base develop --explain` gives the unit set `test___main__, test_analysis, test_budget, test_clip_sensitivity, test_data, test_experiments, test_identifiers, test_report, test_rng_hygiene, test_tools_test_impact`; I add `test_tools_lm_doubling` (the tool `tools/lm_doubling.py` imports `budget`). Smaller than the whole suite. The integration tier is left to the main session (brief).
3. Already run? No: first run on this code (the rendering check above is not a pytest run).
4. Device: `JAX_PLATFORMS=cpu` is set by the wrapper.
5. Threads and time: `LPC_THREADS` default 4; unit timeout 300 s.
6. Contention: no preset or GPU job is started by this unit.
7. Output: wrapper default (`-q --tb=short -rfE`); only the summary and failures are recorded.
8. Command: `LPC_PYTHON=/home/brianm/projects/physics/chaos/lpcstudy/.venv/bin/python tools/run_tests.sh unit tests/unit/test___main__.py tests/unit/test_analysis.py tests/unit/test_budget.py tests/unit/test_clip_sensitivity.py tests/unit/test_data.py tests/unit/test_experiments.py tests/unit/test_identifiers.py tests/unit/test_report.py tests/unit/test_rng_hygiene.py tests/unit/test_tools_lm_doubling.py tests/unit/test_tools_test_impact.py`

### Results
- Unit run (the command above, once): `1 failed, 548 passed in 42.98s`. The one failure is `tests/unit/test_identifiers.py::test_criterion_text_is_the_v3_section_2_row`. It is not caused by this unit: it compares `HYPOTHESIS_TABLE` with the proposal text, and the same test fails identically on the develop worktree (tip ab7431f; one run of `test_identifiers.py` there: `1 failed, 10 passed`). No file of this group is involved. No tolerance, test or criterion was changed.
- Bitwise neutrality: `python -m lpcstudy --preset smoke --seed-id DEV-0 --systems lorenz63 rossler chua --out /tmp/claude-1000/style-g6-smoke` (66 s), then `tools/compare_runs.py runs/refactor-base3/smoke /tmp/claude-1000/style-g6-smoke/smoke`: tier T0, leaves REF 13914, NEW 13914, equal 13914, different 0, one-sided 0, `RESULT: PASS (exit 0)`. The four PNG figures are byte-identical to the reference, and `RESULTS.md` differs only in the four timing and memory rows of the provenance table.
- Line counts (before -> after black at 80 columns, with the new docstrings): report.py 1143 -> 1840, budget.py 1026 -> 1596, clip_sensitivity.py 1014 -> 1743, test_report.py 1334 -> 2323, test_budget.py 1100 -> 1705, test_clip_sensitivity.py 1591 -> 2841 (one item per line and wrapped docstrings grow the files; code removal is small).
- Removed symbols (no caller anywhere in lpcstudy/, tools/, tests/, docs scripts: `grep -rnw` over the whole repo): report `_qn_primary_reading` (one caller, inlined), `_lm_number`, `_lm_ratio`; budget `NO_INTERVAL_KEYS`; clip_sensitivity `TIERS`. Removed parameters: `clip` of `perturb_moments` and `perturb_errors`; the `None` defaults of `caught` in `_block`, `_guarded`, `_compute`. Tests removed: none.
- Runtime strings with British spelling, left unchanged (they reach RESULTS.md or an error message pinned by a test): budget.py:134 `a defect, not relabelled` (ValueError; pinned by the regex at tests/unit/test_budget.py:287); budget.py:211-212 `serial dependence between neighbouring states is not modelled` (H3a interval label in RESULTS.md); budget.py:1113 `favours a pass` (budget cell, RESULTS.md); budget.py:1152 `partly cancelling in the pair` (budget cell, RESULTS.md). Outside the group: lpcstudy/identifiers.py:299 `neighbouring`.

## Review

- **Reviewer:** not yet assigned.
- **Findings and resolution:** none yet.

## Audit

- Is the definition of done met? Items (1) to (4) are met; the evidence is in the Log. One pre-existing failure outside the group is reported.
- Defects recorded: none new. `test_identifiers.py::test_criterion_text_is_the_v3_section_2_row` already fails on develop.
- Notes for successors: the unit-wide rule used here was that a name used outside the group keeps its name and signature; `budget._parts_of`, `budget.QOI_KEYS`, `budget.QOI_IDS`, `budget.below_tenth`, `budget.stored_levels` and `budget.role_level` are read from tools/ or other tests.
