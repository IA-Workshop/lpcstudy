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

lpcstudy/report.py (1143 -> see end of log)
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
