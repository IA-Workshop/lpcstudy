# WU-0004h-G1: style pass on the data, seed, config, provenance, CLI, identifier and embedding modules

| Field | Value |
| --- | --- |
| Status | done pending review |
| Class | CSQ3 development |
| Agent(s) | claude-sonnet-5-5 (no ledger entry of its own; owner's order of 2026-10-18) |
| Estimate | one session |

## Plan (written before execution)

- **Scope:** the owner's code-review order of 2026-10-18 applied to group G1: `lpcstudy/data.py`, `seeds.py`, `config.py`, `provenance.py`, `__main__.py`, `identifiers.py`, `embedding.py`, `__init__.py`, and the tests that import only those modules: `tests/unit/test_data.py`, `test_seeds.py`, `test_config.py`, `test_provenance.py`, `test___main__.py`, `test_identifiers.py`, `test_embedding.py`, `test_rng_hygiene.py`, and `tests/integration/test_cli_seeds.py`. Out of scope: every other file, the seal script, `seeds/`, governance, records, ledger. `tests/slow/test_start_states.py` (imports `systems` too) is left to the main session.
- **Definition of done:** (1) black 26.10.1, 80 columns, one item per line for bracketed lists that do not fit on one line, idempotent; (2) every module, class, function and test docstring is NumPy style, plain early-undergraduate language, with the reason and the study link; (3) American spelling in comments, docstrings and names; (4) dead code, duplicate helpers and forwarding wrappers removed, with grep evidence; (5) no behavior change: no numeric result, no results.json leaf, no CLI behavior.
- **Acceptance criteria (fixed now):** the AST of every `lpcstudy/` file equals the base AST except the changes listed in the Log; the unit tests of the group pass without a changed tolerance; the smoke run at `DEV-0` compares to `runs/refactor-base3/smoke` with `tools/compare_runs.py`: tier T0, 13914 leaves equal, 0 different, 0 one-sided, exit 0.
- **Affected checks:** `tools/test_impact.py --base develop` selects almost every unit test and the integration directory (config and data are imported everywhere). The owner's brief limits the run to the unit tests of the group files; dependents are covered by the bitwise smoke comparison (their code and inputs are unchanged).

## 4.9 test-run checklist (before the run)

1. Change set: the 17 files above (`git diff --name-only 6ddf9cb...HEAD`), plus this record; working tree clean after the previous commit.
2. Radius: `tests/unit/test_{data,seeds,config,provenance,identifiers,embedding,rng_hygiene,__main__}.py` (unit tier) and `tests/integration/test_cli_seeds.py` (integration tier). Smaller than the whole suite. The full tool radius is wider (see Plan); the owner's brief limits it to these files.
3. Already run? No: first run on this code.
4. Device: `JAX_PLATFORMS=cpu` (set by `tools/run_tests.sh`).
5. Threads and time: `LPC_THREADS` default 4; unit timeout 300 s; integration 900 s.
6. Contention: no pilot or full run is started by this unit.
7. Output: wrapper output; summary line and failures only.
8. Command: `LPC_PYTHON=/home/brianm/projects/physics/chaos/lpcstudy/.venv/bin/python tools/run_tests.sh unit <the eight files>`, then the same with `integration tests/integration/test_cli_seeds.py`.

## Log

2026-10-18, branch `wu/style-g1` from `develop` at 6ddf9cb. Commits: 292b39c (sources), a test commit, 60d8809 (tests).

### Lines before and after (`wc -l`, base 6ddf9cb)

| File | before | after |
| --- | --- | --- |
| lpcstudy/data.py | 476 | 619 |
| lpcstudy/seeds.py | 206 | 305 |
| lpcstudy/config.py | 220 | 298 |
| lpcstudy/provenance.py | 443 | 691 |
| lpcstudy/__main__.py | 321 | 583 |
| lpcstudy/identifiers.py | 323 | 617 |
| lpcstudy/embedding.py | 119 | 180 |
| lpcstudy/__init__.py | 0 | 34 |
| tests/unit/test_data.py | 785 | 1140 |
| tests/unit/test_seeds.py | 395 | 582 |
| tests/unit/test_config.py | 72 | 101 |
| tests/unit/test_provenance.py | 907 | 1392 |
| tests/unit/test_identifiers.py | 279 | 452 |
| tests/unit/test_embedding.py | 76 | 99 |
| tests/unit/test_rng_hygiene.py | 706 | 1119 |
| tests/unit/test___main__.py | 945 | 1520 |
| tests/integration/test_cli_seeds.py | 95 | 150 |
| **Total** | **6368** | **9882** |

The growth is the owner's own rules: pedagogical docstrings (module, class, function and test) and one item per line. Code lines were reduced where possible (below).

### Complexity audit: removed or consolidated (grep evidence over the whole repository, `*.py *.md *.sh *.json`)

- `SystemContext.clean_delays` (data.py): removed. No caller anywhere (`grep -rwn clean_delays` finds only its definition). No test.
- `lyapunov_cached` (data.py): removed. It only forwarded to `lyapunov_record(...)[0]`. Callers: two tests in test_data.py, switched to `lyapunov_record(...)[0]`; no caller in `lpcstudy/`, `tools/` or the `docs/agent/notes` scripts (they call `lyapunov_record`). The test `test_lyapunov_cached_matches_published_reference` was renamed `test_lyapunov_record_matches_published_reference` (same cases, same tolerances, same assertions). In `test_cache_new_form_entry_does_not_recompute` the one assertion `lyapunov_cached(...) == 0.9054940534657817` was dropped because the line above it asserts the same value through `lyapunov_record`. No test was deleted.
- `embedding.mutual_information(series, lag, n_bins=32)`: the parameter `n_bins` was never varied (no caller outside `select_delay`, no test); replaced by the module constant `MI_BINS = 32`. Same arithmetic.
- `__main__.main`: three copies of `print("lpcstudy: refused (LPC.PC.7): ...", file=sys.stderr); return REFUSAL_EXIT` consolidated into `_refuse(reason)`. Same text, same stream, same exit code (pinned by test___main__.py and test_cli_seeds.py).
- `__main__.build_parser`: `description=__doc__` replaced by the literal original one-line text, so that `--help` is byte-identical although the module docstring was rewritten.
- Tests: inline imports hoisted to the top of test_data.py, test___main__.py and test_rng_hygiene.py (about 35 repeated import lines removed). In test_rng_hygiene.py `scan_labels` now builds on `label_templates` (both scanned the same calls with the same conditions; the body shrank from 33 to 12 lines; the tests of both are unchanged and still cover them).
- `lpcstudy/__init__.py` was empty: it now carries the package overview docstring (code unchanged).
- Considered and kept: `QOI_FIELDS` (used by a test and a documented schema), `with_seed` (30 callers outside the group), `check_commitment(seed_id=...)` (varied in a test), `own_git_env` duplicated in test_provenance.py and test___main__.py (a shared helper would need a file outside the group).

No other dead code found: every other top-level name in the eight modules has a caller (a grep of all names over the repository).

### Tests renamed (a def line longer than 80 columns cannot be formatted)

test_data.py: `test_draw_starts_support_and_the_norm_identity_within_the_derived_bound` -> `test_draw_starts_support_and_norm_identity`; `test_build_context_trajectory_digests_equal_sha256_of_the_simulated_post_burn_in_orbits` -> `test_build_context_trajectory_digests_are_sha256`; `test_lyapunov_cached_matches_published_reference` -> `test_lyapunov_record_matches_published_reference`. test_provenance.py: five names shortened (`..._hidden_by_core_excludes_file_in_config` -> `test_git_state_counts_a_file_hidden_by_excludes_file_in_config`, its `_in_environment` twin, `test_wall_seconds_is_within_one_percent_of_own_clock`, `test_array_digest_ignores_layout_and_byte_order`, `test_index_digest_is_sha256_of_int64_bytes`). test___main__.py: `test_sealed_flag_refused_on_dirty_tree_or_unknown_commit`. No test deleted; no tolerance, seed or bound changed (the AST of every test file equals the base AST apart from the hoisted imports, the renames, the `lyapunov_cached` edits and the `scan_labels` consolidation, checked with an AST diff).

### Runtime strings that tests or goldens pin (not changed; for the main session)

- `lpcstudy/identifiers.py`, `QOI_DECLARATIONS["H3a"]["decision_error"]` (about line 565): "...so serial dependence of neighbouring states could overstate significance". British spelling; the string is printed by `budget.qoi_declaration_lines` into RESULTS.md. Not changed.
- No other British spelling found in strings, messages or log text of the group.

### identifiers criterion text follows the owner's v3 edit of 2026-10-18

Cause: commit e4da1f9 (DEF-0005 edits) changed the section-2 rows of `docs/study/proposal_and_methods_v3.md`; `HYPOTHESIS_TABLE[*].criterion` still held the old text, so `test_criterion_text_is_the_v3_section_2_row` failed (code follows the documents). Fix (a deliberate text change): the `criterion` strings of H1a, H1c, H1d, Q-N, H2a, H2c, H3a and H3b now equal the new v3 rows exactly, generated from the file with the same parse as the test (unescape; `<statistic>; pass if <rule>`); a check script found 0 rows different afterwards. Test logic and v3 untouched. Where the text is used: `lpcstudy/report.py` (`_hypothesis_text`, `HYPOTHESES`) prints it in RESULTS.md (the hypothesis-table rows of those eight keys change). `criterion` is NOT stored in results.json (no leaf changes; `grep criterion runs/refactor-base3/smoke/results.json` is empty). No test or golden pins the old text (a grep of the old phrases over tests/, tools/ and lpcstudy/ finds only identifiers.py and one docstring in analysis.py).

### Behavior neutrality of the sources

AST check against the base (docstrings and every bare string statement ignored, since attribute docstrings are string statements): seeds.py, config.py and provenance.py equal; identifiers.py differs only in the eight criterion strings; data.py differs only by the removal of `clean_delays` and `lyapunov_cached`; embedding.py only by `n_bins` -> `MI_BINS`; __main__.py only by `_refuse` and the literal parser description; __init__.py only by its new docstring. The standard `ast_compare.py` reports DIFFERENT for provenance.py and identifiers.py only because their bare attribute-docstring statements (`ISA_FLAGS`, `GAIN_BOUND_PENDING`) were rewritten.

### Verification (2026-10-18)

- Black: `uvx black==26.10.1 --check` on the 17 files: "17 files would be left unchanged" (idempotent). No line over 80 columns in the 17 files (`awk 'length>80'`: 0).
- Unit tests, once, after all edits: `LPC_PYTHON=.../.venv/bin/python tools/run_tests.sh unit tests/unit/test_{data,seeds,config,provenance,identifiers,embedding,rng_hygiene,__main__}.py` -> `264 passed in 19.29s` (includes `test_criterion_text_is_the_v3_section_2_row`, which failed on the base).
- Integration, once: `tools/run_tests.sh integration tests/integration/test_cli_seeds.py` -> `8 passed in 7.06s`.
- Bitwise neutrality: `python -m lpcstudy --preset smoke --seed-id DEV-0 --systems lorenz63 rossler chua --out /tmp/claude-1000/style-g1-smoke` (4 threads, CPU; exit 0, 71 s), then `python tools/compare_runs.py runs/refactor-base3/smoke /tmp/claude-1000/style-g1-smoke/smoke`: tier T0, leaves REF 13914, NEW 13914, equal 13914, different 0, one-sided 0, RESULT: PASS (exit 0). RESULTS.md differs from the baseline only in the provenance table (commit, argv, times, memory) and in the criterion text of the eight rows listed above (expected).
- Dependents of config and data (pipeline, ensemble, oracle, ...) were not re-tested by their own unit files (owner's brief); their inputs and code are unchanged and the smoke comparison above is bitwise.

## Review

- **Reviewer:** not yet run.
- **Findings and resolution:**

## Audit

- Is the definition of done met? See the verification entries of the Log.
- Defects recorded:
- Notes for successors: `tests/slow/test_start_states.py` (imports `data` and `systems`) was not touched.
