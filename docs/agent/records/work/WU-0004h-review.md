# WU-0004h independent review: style and simplification refactor (G1 to G11 and main-session commits)

## Review

- **Reviewer:** `reviewer`, fresh context, model `claude-opus-5-5` (the brief named Sonnet 5.5; this review was run by Opus 5.5 and is signed as such).
- **Range:** `6ddf9cb..e326c87` (develop tip). 109 files: 24 in `lpcstudy/`, 13 in `tools/` (3 shell), 60 in `tests/`, 12 unit records.
- **Mode:** read-only. No test, smoke run, tool run or GPU use (the main session was running the gate). Evidence is static: `git diff/show`, `grep`, and throwaway AST scripts in the session scratchpad.

### Method

1. For each changed `.py` file, old and new were parsed with `ast`. Every docstring and every bare-string statement was stripped, at any depth, and the top-level definitions and class methods were compared. 39 files were equal. Each differing definition was diffed with `ast.unparse` and read.
2. Tests were compared a second time with function-local imports also stripped, so that import hoisting does not hide a change. Renamed tests were paired by body: a test removed under one name and added under another had to have an identical body. The test count of every file was compared.
3. The runtime strings were compared as multisets: every string constant and f-string outside docstrings, in `lpcstudy/` and `tools/`, old against new. The same was done for numeric constants in all three trees, to catch tolerance edits.
4. Every removed symbol was searched for over the whole repository at HEAD and at the base: `lpcstudy/`, `tools/`, `tests/`, `*.sh`, `docs/` scripts and notes, `.claude`, the ledger, records. So was every old test name, every module-qualified access (`mod.NAME`) and every `__doc__` use.
5. Three structural checks:
   - the intra-package import graph, old against new;
   - the helper-name mention map used by `tools/test_impact.py::_helper_paths`;
   - the scan markers `SCAN_MARKERS`.

### Verified equal (no finding)

**`statistics._draw_indices`.** The guard in `block_resample_indices` ensures `n_items >= 1` and `block >= 1`.
- If `n_items >= block`, then `starts_max = n_items - block + 1`, so every start is `<= n_items - block` and every index is `<= n_items - 1`.
- If `n_items <= block`, then `starts_max = max(1, ...) = 1`, so the start is always 0 and the indices are `arange(block)[:n_items]`.

The clip could never act. The generator is consumed identically and the dtype is int64. Equal.

**`statistics._fill_failed`, `_failures_reach`, `_check_values`, `_check_labels`.**
- With no failures, `np.where(all-False, ...)` returns a value-identical copy.
- The all-failed case returns before `_fill_failed`, because `floor((n-1)*alpha)+1 <= n` for `alpha < 0.5`, so `finite.min()` is never taken on an empty array.
- Quantile order in `half_range` is unchanged.
- `_VERDICTS` is a tuple, so membership semantics are unchanged.

**`allocation._pooled_sums` and `_pooled_weight`.** The sums are the same: `[slice(None)]` is the same view, so the summation order is the same. `pooled_floor_count` now also computes the numerator. That costs time only; no warning path is new, because `curvature` already evaluates the same terms.

**`ensemble`.**
- `_reference_column`: equal for valid input.
- The `half_out` condition: `halves is None` exactly when `half_out is None`.
- `per_state`: equal.
- `clip_sign`, moved inside the `if`: equal.
- The IndexError-to-ValueError change: see R4.

**`analysis`.**
- `characteristic_horizon` is pure (`oracle.py:444-449`), so calling it once is equal.
- `_masked_logit` and the inlined `_at_bound` are equal.
- The import moves add names from `allocation`, which `analysis` already imported at module top. The import graph is unchanged (computed old against new: no edge differs), so there is no new cycle.
- The monkeypatch targets in two tests moved from `allocation.state_horizon_target` to `an.state_horizon_target`, consistent with the module-level binding. No other test patches an `allocation` name expecting `analysis` to see it.

**`__main__._refuse`.** The output is identical. The parser description literal equals the old `__doc__`, byte for byte.

**`experiments`.** The removed `study` argument was `del`'d on entry; its one caller was updated. `bits` is now a `def`.

**`report`.**
- The `write_markdown` split keeps the line order, including the insertion point of the gate lines, which is right after `## Hypothesis verdicts`.
- `gate_words` is equal for `True`, falsy-not-`None` and `None`.
- `_parts_text`: `x if g else (r or 'bound')` equals `g or r or 'bound'`.
- `_lm_number` was replaced by `_fmt`. They differ only for NaN, and `estimation.lm_summary` never stores NaN: it raises on a NaN residual and maps a non-finite value to `None`.
- `_save_figure` and `_new_figure`: same calls, same order.

**`dump` and `pipeline`.** `dump.py` is AST-equal. `cell_id` and `_oracle_blocks` give equal strings.

**`embedding.mutual_information`.** The only caller, at base and at HEAD, used the default 32 bins, and `MI_BINS = 32`.

**`oracle.local_dimension`.** No production caller. The tests use `local_dimension_counted(...)[0]`. The dropped assertion compared only the removed wrapper.

**`systems.SystemSpec.extra`.** Every construction uses keywords, there is no `.extra` reader, and `SystemSpec` is never serialized, hashed or `asdict`'d. (`tools/rehearsal_report.py` `spec.extra` is that tool's own `Spec`.)

**`validation`.** The `'center'` key has no reader outside `tests/unit/test_validation.py`: no tool, note script or summary reads it, and `p2_bound_summary` does not. The pooled dict is internal.

**`tools/compare_runs`.**
- All 12 `_pass_or` call sites match the old inline code (`<=`, and FAIL or FINDING per site). The count is 12 at base and 12 at HEAD.
- `_one_row`: equal.
- The dropped second `cpu_device` assignment is reached only after the "absent fact" return, where `[]` equals `.get`.
- `RANK`, `TAG_CHAINS`, `RULES` and `DReport.passed` have no reader. `NReport.passed`, which the tests use, is kept.

**`tools/lm_doubling`.** `strict_flag`, `_stored_choice` and `Path_` were inlined. `doubling_stats` uses `TOLERANCE` and no caller passed `tolerance`. The `--help` description is identical.

**`tools/rehearsal_diagnostics`.**
- `skip`, `results_leaf`, `seed_controls`, `block_bootstrap_se`, `_d1_lines`, `_d2_lines` and `_owner_flag_text` give identical text and the same RNG labels (`d5-bootstrap`, `d6-bootstrap`).
- `OUTSIDE_SCHEMA` was empty, so its loop never ran.
- `curvature` was never passed; `h1a_hessian` keeps its default `True`.

**`tools/rehearsal_report`.** `check_level`, `side` and `NON_GOVERNING_NOTE` give identical strings. `outside_v3_range(·,·,MARGIN_V3)` equals the old `outside_margin`.

**`tools/test_impact`.** Every member of `WHOLE_SUITE` strips to a member, so the dropped `or p in WHOLE_SUITE` was redundant.

**`--help` texts.** These are now literals equal to the old first lines: `gpu_hours`, `rehearsal_*`, `lm_doubling` and `__main__`. In `compare_pilot`, `compare_runs` and `leafdiff` the description now contains a newline, which argparse's default formatter collapses. Text equal.

**Shell scripts.** Only comments changed, plus one no-op removed from `owner_freeze_run.sh`. The usage lines 2 to 18 are unchanged.

**Tests.**
- No test was lost or duplicated. The per-file counts are equal, except `test_ensemble.py` with +1, a new test. No module-level or class-level name is defined twice.
- Every renamed test has an identical body, except the `lyapunov` rename (see R1).
- Merged asserts were only ever split, never merged. No numeric constant changed except through deduplication into helpers (`_reference_fit_predict`, `_h1c_stub_world`).
- The new helpers compute the same values. The one data-layout difference, the boolean-mask copy in `n_pred`, gives the same values.

**Test-impact inputs.** No old test name appears in a `-k`, marker list, script, `.claude` file or the ledger. The helper-mention map and `SCAN_MARKERS` hits are the same old and new.

**Runtime strings.** Commit `587d63b` changed exactly the strings it lists. No other runtime string changed in `lpcstudy/` or `tools/`, apart from the deliberate criterion texts of R3.

### Findings

**R1. Blocking, before merge to main or freeze. RESULTS.md now cites a test that does not exist.**
- Where: `lpcstudy/report.py:838-841` (`LYAPUNOV_MEMO_TEST`), pinned by `tests/unit/test_report.py:953-956`. The renamed test is `tests/unit/test_data.py:437`; it was `:312` at base.
- Evidence: G1 renamed `test_lyapunov_cached_matches_published_reference` to `test_lyapunov_record_matches_published_reference`. The `_lyapunov_lines` row of RESULTS.md for the Chua memo set still reads "within 10% is asserted by `tests/unit/test_data.py::test_lyapunov_cached_matches_published_reference[chua_memo]`". That node id no longer exists.
- Why it was missed: G1's `grep -w lyapunov_cached` cannot match inside `test_lyapunov_cached_matches...`, because the neighbors are word characters. The test pins the stale string, so the gate stays green.
- Why it matters: this is a validation claim in the study's deliverable whose evidence pointer is broken (traceability, NVVUQ).
- Fix (preferred, zero RESULTS.md change): rename the test back to `test_lyapunov_cached_matches_published_reference` in `tests/unit/test_data.py`. Alternative: update `LYAPUNOV_MEMO_TEST` and the pin in `test_report.py`. That is a RESULTS.md line change and needs the owner.

**R2. Should-fix: owner ruling and decision record needed before freeze. Commit `587d63b` changes results.json string leaves and RESULTS.md lines, against the brief.**
- Where:
  - results.json: `lpcstudy/analysis.py:594` (`H1a/reference_estimator`, "normalisation" to "normalization") and `:1924` (`H2a/controls`, "centred" to "centered"). That is two string leaves per system, six in all.
  - RESULTS.md and error text: `lpcstudy/budget.py:134, 211, 1113, 1152` and `lpcstudy/identifiers.py:565`.
  - Tool notes: `tools/compare_runs.py:1984, 2005`.
- Evidence: the brief forbids changing a string leaf of results.json or a RESULTS.md line. The commit message records the change, but no DEC entry exists (`decisions.md` has none).
- Consequences:
  - In T0, `compare_runs` treats a differing non-verdict string as a FAIL (`tools/compare_runs.py:1969-1970`, T0 bitwise). In T1 to T3 it is a categorical FAIL, "text differs" (`:1995-1996`).
  - So every comparison of a run made before `587d63b` with one made after shows these six leaves as FAIL and exits non-zero. Pre-`587d63b` runs include `runs/refactor-base3/smoke`, which holds three "normalisation" and three "centred", and the rehearsal and pilot runs.
  - Prediction for the main session's own final gate: the step `compare_runs.py runs/refactor-base3/smoke /tmp/claude-1000/final-smoke/smoke` will report six FAIL leaves, not PASS. That is expected from this commit and is not a numeric regression.
- Fix: either revert the two results.json strings (keep the RESULTS.md-only spelling if the owner wants it), or record an owner decision. The decision should say that pre-refactor baselines differ in exactly these six leaves, and should add a documented exception or re-baseline.

**R3. Should-fix: owner acknowledgment and record. The criterion text of eight HYPOTHESIS_TABLE rows was rewritten inside a style unit.**
- Where: `lpcstudy/identifiers.py:79` onward (merge `c92a770`).
- Evidence: the `criterion` strings of H1a, H1c, H1d, Q-N, H2a, H2c, H3a and H3b now follow the v3 section-2 rows edited in `e4da1f9`. That edit had left `test_criterion_text_is_the_v3_section_2_row` failing on the base. These strings are printed in the RESULTS.md hypothesis table (`report._hypothesis_text`, `budget.py:539`).
- Assessment: the fix is right (code follows the documents) and is disclosed in G1's record. But it is a content change bundled into a no-behavior-change unit (LPC.PC.1, SIMPL.3), it changes RESULTS.md, and it repairs a defect that has no DEF entry.
- Fix: a DEF or DEC line that names the defect (a red test on develop at `6ddf9cb`) and the owner's acceptance of the RESULTS.md change. No code change.

**R4. Note: an error type changed.** In `lpcstudy/ensemble.py:429-445` (`_reference_column`), `ensemble_moments` with a `reference_horizon` not in `horizons` now raises ValueError instead of IndexError.
- Nothing catches IndexError for it; the only `except IndexError` is `tools/rehearsal_diagnostics.py:3520`, which is unrelated.
- The broad `except` at `lpcstudy/experiments.py:1270` would store `repr(exc)` in `robustness[label].error`. That text would differ, but the path is unreachable with any valid configuration: variants never change the horizons.
- Deliberate and pinned by the new test `tests/unit/test_ensemble.py:1140`. Accept as is; mention it in the unit closure.

**R5. Note: unreadable directories can be counted twice.**
- Where: `tools/gpu_hours.py:313` (`existing_roots`) and `:227` (`on_error`).
- Evidence: the resolved-path dedup of roots was removed. `find_meta_files` dedups meta *files* by resolved path, so the GPU-hour totals cannot double. But `on_error` keys unreadable *directories* by the unresolved `error.filename`. An unreadable directory reached through two aliased roots, for example `--root runs --root $PWD/runs` or a symlinked worktree path, is now listed and counted twice.
- The exit is unchanged, since any unreadable entry refuses. The printed count and list are not. G9's record ("records an unreadable directory once by name") holds only per spelling.
- Fix: restore the `resolve()` dedup in `existing_roots`, or key `errors` by `Path(...).resolve()`.

**R6. Note on governance: two commits break the commit rules.**
- `df4cf9c`, "gate run log committed": no unit id and no `Agent:` trailer.
- `70a696d`: no unit id. It is a functional test-harness change: the GPU child environment gets `LPC_THREADS` (`tests/gpu/test_reproducibility.py:275`, `gpu_environment`). It is outside the style brief.

The change in `70a696d` looks correct and changes no tolerance. History must not be rewritten, so the fix is to record the unit attribution of both commits in the WU-0004h closure.

**R7. Note: the status-lines proposal cites renamed tests.**
- Where: `docs/agent/notes/2026-10-18-nvvuq-status-lines-proposal.md`, lines 58, 121, 132, 210, 225 and the table at 238.
- Evidence: the proposed RESULTS.md status lines and the "Tests (exist on develop)" column cite test node ids renamed in this refactor, such as `test_lyapunov_cached_...`, `..._labelled_report_only...`, `..._centring_round_off`, `test_every_table_has_nine_rows_in_order...` and `test_old_schema_and_a_missing_result...`. One also cites `local_dimension.__defaults__`.
- Fix: update the proposal before the owner adopts any line. Records under `docs/agent/records/work/` keep their historical names (append-only), which is fine.

### Verdict per group

| Group | Files (summary) | Verdict |
|---|---|---|
| G1 | data, seeds, config, provenance, `__main__`, identifiers, embedding, `__init__`, their tests | **reject until R1 is fixed** (a one-line test rename back); R3 needs an owner record; everything else approvable |
| G2 | systems, dynamics, oracle, validation, networks, estimation | approve |
| G3 | allocation, ensemble, experiments | approve with notes (R4) |
| G4 | analysis | approve |
| G5 | statistics, pipeline, dump | approve |
| G6 | report, budget, clip_sensitivity | approve with notes: it holds the stale pointer of R1 (the fix is in G1's file) |
| G7 | compare_pilot, compare_runs, rehearsal_common, leafdiff | approve |
| G8 | rehearsal_report, rehearsal_diagnostics | approve |
| G9 | lm_doubling, gpu_hours, ledger, test_impact | approve with notes (R5) |
| G10 | shared test helpers, shell wrappers, integration, slow and gpu files | approve |
| G11 | golden_rehearsal, extract scripts, V7 tests | approve |
| Main session | `587d63b`, `70a696d`, `df4cf9c`, `4dd5824`, `e326c87` | R2 (owner ruling), R6 (record) |

**Overall verdict: approve with fixes.** R1 is required. R2 and R3 need an owner decision before freeze. R4 to R7 are notes. Findings: 7.

**Owner checkpoint: needs owner review before freeze.** The range touches:
- verdict and statistics code: `statistics.py`, `analysis.py`, `compare_runs.decide` and `select_tier`;
- the seed-refusal path: `__main__._refuse`;
- the tolerance-tag tables of the comparison tools.

The behavior of each is equal by the analysis above.

**Reproducibility.**
- Randomness: no new source. Test helpers use the existing seeds, and the `make_rng` label sites are unchanged. `test_rng_hygiene.scan_labels` now builds on `label_templates` with the same filter.
- float64: no dtype change found.
- Provenance code (`provenance.py`, `seeds.py`, `config.py`, `dump.py`, `estimation.py`) is AST-equal.

### What I could not check

- Nothing was executed (per instruction). Bitwise equality of results.json (13,914 leaves), RESULTS.md and the goldens rests on the authors' runs and on the static equivalence argued above.
- The tests were not run. Passing is taken from the authors' logs and `/tmp/claude-1000/final_gate.log` (unit: `1870 passed`), which I read but did not reproduce.
- The semantic accuracy of the rewritten docstrings (tens of thousands of lines) was not reviewed. I checked only that no code path reads a changed docstring. The reads are the `--help` first lines, `tests/unit/test_dump.py:613` and `tests/unit/test_tools_compare_pilot.py:2891`, and the gate covers the last two.
- `docs/` Python scripts were checked only by grep for removed names. None references one.
- Whether `587d63b` also breaks a golden or integration expectation is left to the running integration gate. No `.py` file holds the old spellings.
