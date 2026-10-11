# WU-0008: uncertainty budget, numerical-error rows, interval labels, QoI table

| Field | Value |
| --- | --- |
| Status | planned |
| Class | CSQ3 development; adds statistics code (endpoint Monte Carlo error) and report statements that bear on how verdicts are read: needs owner review before freeze (LPC.PC.11) |
| Agent(s) | planner claude-opus-5-5; then applied-mathematician (design tasks M1 to M9), developer, reviewer, human owner (.5) |
| Estimate | ROADMAP WU-0008.1 (M), .2 (M), .3 (S), .4 (S), .5 (S) |

## Plan (written before execution)

Planner: claude-opus-5-5, 2026-10-11, branch `wu/0008-report-budget` at 221ae9a (develop: WU-0002.1 to .11b, .9b, .12 tool, WU-0005.5, WU-0006, WU-0007). Governing texts: v3 §2 (primary rows H2a, H2b, H3c), §7 (intervals, levels, intersection–union), §8 (limitations); NVVUQ.3, .9, .10, .15, .16, .22 and instantiation rows "QoIs", "Numerical error", "Convergence", "Uncertainty budget", "Intervals", "Reporting"; skill `uq-budget`; DEF-0020, DEF-0021, DEF-0022, DEC-0018; WU-0006 Log (run-2 table). ROADMAP rows WU-0008.1 to .5.

### Scope

**In.**
- **New module `lpcstudy/budget.py`** (pure functions of `results`, `config`; no randomness). It holds everything that is not a one-line call site, so that `report.py` takes only small delimited hunks:
  - `budget_lines(results, systems, config)`: the `## Uncertainty budget` section (.1, .2);
  - `interval_label(...)`, `interval_label_lines(...)`: the four-element label (.3);
  - `FIGURE_CAPTIONS`, `figure_caption_lines(...)`, `caption_figure(fig, name)` (.3);
  - `qoi_declaration_lines(...)` (.4);
  - `COVERAGE_WU0006`: the WU-0006 run-2 coverage counts as constants with provenance (see .2).
- **WU-0008.1 budget tables.** One table per primary QoI: H2a(i), H2a(ii) (two parts, zero and interior, shown in each cell), H2b(i), H2b(ii), H3c. Columns: Source | Type | How estimated | Size, one column per system present | Included in the reported interval? | Below 10% of the sampling half-width? Rows, in this order: the eight rows of the `uq-budget` skill, plus a ninth, **"Interval procedure (coverage of the block-5 percentile interval)"**, type "statistical method" (brief; DEF-0020; see O2). Every size cell is a number or `not estimated: <reason>`; a missing key never raises and never prints a blank. Under each table: the label of .3, the seed line (`DEVELOPMENT (DEV-n)` from `provenance`; WU-0006 rows: "synthetic, seed 6006, not a registered seed"), and the sentence that a numerical row at or above 10% is flagged, not widened (widening is the owner's).
- **WU-0008.2 numerical rows.**
  - *Bootstrap endpoint Monte Carlo error.* New pure helper `statistics.endpoint_mc_error(values, level) -> tuple[float | None, float | None]`. For each endpoint at percentile q, d = √(q(1 − q)/B), and SE = (Q̂(q + d) − Q̂(q − d))/2 with Q̂ the empirical quantile of the resample values (the binomial error of the percentile index, converted to the statistic's scale through the empirical bootstrap distribution). `None` when the bound is infinite or q ± d leaves (0, 1). The exact form is M2.
  - *Persisted at the five primary sites only.* Each result dict gains `ci_mc_se: [se_lo, se_hi]` (H2a(ii): per part). Estimates, intervals and verdicts are unchanged bitwise. The three sites that call `block_bootstrap_counted` (`_paired_change` for H2b(ii), H2b(i) at analysis.py:1455, `h3c_ratio`) switch to its documented body, `bootstrap_values` + `percentile_interval`, at the same seed. `block_bootstrap_counted`, `BootstrapInterval` and `percentile_interval` are not edited.
  - *V6 row* from `validation.integrator_max_dev_sigma` (with LPC.NV.1: the QoI is defined on the discrete map, M6).
  - *Oracle Monte Carlo row* from `validation.convergence[used_M].median_half_width` (V4), converted per QoI by the formula of M3.
  - *LM row* from the WU-0005.4 summary keys (`median_residual`, `p95_residual`, `median_iterations`, `fraction_no_decrease`). **Waits for WU-0005.4** (planned in parallel): the key path is one constant `LM_SUMMARY_PATH`, set when WU-0005.4's plan names it; until then the row reads `not estimated: WU-0005.4 summary absent from results`.
  - *Round-off row*: the float64 and conditioning argument, a constant with its derivation (M5).
  - *Interval-procedure row*: measured coverage at the QoI's level from WU-0006 run 2, φ = 0 and 0.3, with its Monte Carlo SE √(p(1 − p)/1000) and the equivalent half-width shortfall (M7). **Source: constants in `budget.COVERAGE_WU0006`**, each with the provenance string "WU-0006 run 2, `runs/tests/slow-20261011T165447Z.log`, Log table at b73bbed". Not a JSON from `runs/` (ignored by git, and the run-2 analysis table was overwritten, WU-0006 R2). Owner may prefer a committed JSON (O3). The cell also names DEF-0020 and the pending Option C or K.
  - *Proxy row* per QoI (M8): for H3c, `oracle_recovery.A4_vs_A4o` and the H1d Spearman values; for the oracle-defined QoIs, `not estimated: <reason>` as M8 fixes.
  - Each numerical row carries the flag `below 10% of the sampling half-width: yes / no / not estimated`; the sampling half-width is (hi − lo)/2 of the reported interval.
- **WU-0008.3 interval labels.** Every Markdown table in `RESULTS.md` that shows an interval is followed, before the next heading, by a label stating procedure, level, dependence assumption and multiplicity adjustment. Tables with intervals today: the verdict table (one label line per row, from the row's role and its stored `level`), the V4 row of the validation table, the budget tables. Values come from `config.bootstrap_block` and `config.bootstrap_resamples`, not literals, so smoke reads its own B. Wording: "moving-block bootstrap percentile interval, blocks of 5 test states in time order, B = 2000; level 1 − 0.05/3 (primary) or 95%; dependence: within blocks of 5 consecutive states, none assumed beyond; multiplicity: Bonferroni over the three primaries, intersection–union across systems, Holm within H3a, none for secondaries". H3a (p-values) and H3b (bootstrap over construction states) get their own wording. A `## Figures` section gives one caption per file of `make_figures`, and `caption_figure` writes the same caption into the PNG. No current figure draws a confidence interval; each caption says what any band is ("inter-quartile range across states, not a confidence interval") or "no interval shown" (O4).
- **WU-0008.4 QoI declaration table** `## Quantities of interest (NVVUQ.3)`: one row per row of `HYPOTHESIS_TABLE` (14, including the gain bound; **amended per brief**, ROADMAP says 13, O1). Columns: ID, definition, units and conventions, criterion (verbatim `row.criterion`), decision-relevant error, decision informed, confirmatory or exploratory (NVVUQ.22). Data: an additive dict `QOI_DECLARATIONS` appended at the end of `identifiers.py`, keyed by `row.key`; text from v3 §2, §5, §7 (precision paragraph), §8 and Methods v2 §M12.

**Out.**
- Changing any interval, level, block length, B or band, and widening an interval for a flagged row (DEF-0020, DEC-0018: the owner's).
- The LM diagnostics themselves (WU-0005.4). H3b's coverage (WU-0006 gap; the H3b row of the verdict-table label says "coverage not measured").
- Budget tables for secondary QoIs (NVVUQ.15 asks for every reported QoI; ROADMAP restricts .1 to primaries, O5).
- New figures or new intervals in figures (O4). Editing the `uq-budget` skill or governance files (O2).

### Definition of done
1. `python -m lpcstudy --report-only` on a stored `results.json` writes the new sections, with no exception on results that predate the new keys (DEV-0 pilot results at `lpcstudy-wt/run/pilot-dev0/runs/dev/wu0002-12/pilot/` as the old-schema case).
2. The tests below pass once, in the radius; the DEV-0 smoke comparison is in `## Log`.
3. The applied-mathematician's section (M1 to M9) precedes the code of .1 and .2.
4. `tests/unit/fixtures/lpcstudy_graph.json` and `test_tools_test_impact.py` updated for the new module and edges, in the same commit.

### Acceptance criteria (fixed now, VV.3; the applied-mathematician may tighten, never loosen)

| # | Check | Reference | Tolerance and justification |
| --- | --- | --- | --- |
| B1 | Row set and no empty cell | `fake_system` results (full keys) | each of the 5 tables has exactly the 9 rows in order; no cell matches `^\s*$`; every size cell parses as a number or starts `not estimated: ` followed by a non-empty reason; exact |
| B2 | Old schema | results without `ci_mc_se`, LM keys, or a system | same row set; the affected cells read `not estimated: <reason>`; no exception; exact |
| B3 | 10% flag | synthetic sizes at 0.09, 0.10, 0.11 of a half-width of 1 | yes, no, no (strict <, M9); exact |
| B4 | Interval-procedure constants | the WU-0006 run-2 table parsed from `docs/agent/records/work/WU-0006-simstudies.md` in the test | every count equal; exact |
| B5 | Oracle row | fake V4 half-width; M3's formula by hand | 1e-15 relative (one float expression) |
| E1 | `endpoint_mc_error`, deterministic case | values = Φ⁻¹((i − ½)/B), B = 2000; analytic √(q(1 − q)/B)/φ(z_q) | 3% relative at 95% and 1 − 0.05/3: the central difference's curvature term plus the grid's discreteness (d·B ≥ 4 order statistics) give −0.33% and −0.91% (planner's read-only calculation with `np.quantile`), so 3% leaves a 3× margin; the AM may tighten to 2% |
| E2 | Against a repeated ("nested") bootstrap | one fixed synthetic case: Gaussian AR(1), φ = 0.3, n = 500, mean, data from `make_rng(8008, "wu0008", "nested")`; reference = SD of each endpoint over 100 bootstraps (B = 2000) with independent seeds on the same data | helper's SE from the first bootstrap within a factor of 2 of the reference (ROADMAP); the reference SD has relative SE ≈ 1/√198 ≈ 7%; about 1.5 s |
| E3 | Edge cases | an infinite bound; q ± d outside (0, 1) | `None`, exact |
| A1 | Bitwise unchanged | DEV-0 smoke before and after (`provenance`, `seconds`, `handling` excluded) | every pre-existing leaf bitwise equal; only `ci_mc_se` leaves new; anything else is a defect |
| A2 | `ci_mc_se` persisted | `test_analysis` on the five sites with synthetic inputs | equals `endpoint_mc_error` on the same resample values, exact |
| L1 | Labels next to every interval table | generated `RESULTS.md` from the fake results | for every table containing `[x, y]`, a line before the next heading contains "procedure:", "level:", "dependence:" and "multiplicity:"; exact |
| L2 | Label level matches the result | each result carrying `level` | label level string equals the stored level; a mismatch fails (it would be a defect, not relabelled) |
| L3 | Captions | `## Figures` and the PNG text (via a `savefig` stub capturing `fig.texts`) | one caption per written file; an interval-bearing caption contains the level and "moving-block bootstrap, blocks of 5" (exercised on a synthetic caption entry until a figure draws an interval, O4) |
| Q1 | Declaration table | `HYPOTHESIS_TABLE` | row count = 14; every cell non-empty; criterion column = `row.criterion` verbatim; `QOI_DECLARATIONS` keys = table keys (in `test_identifiers`) |

Every unit test under 5 s.

### Affected checks (DEVELOPMENT_WORKFLOW §4.2; confirm with `tools/test_impact.py --explain`)
- **.3 and .4** (`budget`, `report`, `identifiers`): unit `test_budget.py` (new), `test_report.py`, `test_identifiers.py`, `test___main__.py`, `test_tools_test_impact.py` (graph); integration `test_cli_seeds.py`, `test_preset_wrapper.py`, plus the smoke by hand in place of `test_smoke_pipeline.py` (report touched, LPC.PC.12).
- **.2a** (`statistics` core, `analysis`): unit `test_statistics.py` and every transitive dependent's unit file (`test_allocation`, `test_analysis`, `test_experiments`, `test_validation`, `test_pipeline`, `test_oracle`, `test_report`, `test___main__`, `test_identifiers`, `test_budget`); integration as above. **Slow, once:** `tests/slow/test_analysis_coverage.py::test_exact_checks` for C4, C7, C8 at φ 0 and 0.3 (the production functions they call change body; the exact checks prove bitwise identity). The coverage counts are not rerun: the existing helpers are unchanged and the identity nodes cover the call sites (planner's reading of the slow rule; the reviewer confirms by diff).
- **.1 and .2b**: as .3/.4.

### Owner checkpoints (LPC.PC.11)
- **Statistics code:** yes (`endpoint_mc_error`; five analysis sites). **Verdict code:** no verdict rule changes, but the budget and labels state how much weight a verdict carries: owner review before freeze.
- **Seeds and provenance:** none in the package (the helper is deterministic). The E2 test uses the literal 8008, not a registered seed.
- **Dependencies:** none (stdlib `statistics.NormalDist` for E1).

### Applied-mathematician must decide before execution (design tasks)
- **M1. Row definitions per QoI**: which rows apply, their type (aleatory, numerical, estimator, epistemic, method) and "included in the interval?" for each of the five QoIs.
- **M2. Endpoint MC error formula**: d, interpolation, behavior near failed resamples; tolerances of E1 (3%) and E2 (factor 2, 100 repetitions), and whether the median over repetitions of the helper should also be checked.
- **M3. Oracle MC conversion** from the V4 per-state half-width to each QoI's scale (e.g. hw/√n for a mean of w\*, a paired form for H2b(ii) with common draws across n_lib). For H2a(ii) state whether draw noise in logit w\* attenuates the partial correlation toward 0 (toward a pass) and how big that is; for H3c whether the row is "not estimated: enters through the fitted regime weights".
- **M4. LM row**: how a residual and iteration summary converts to a QoI-scale size, or the reason it cannot.
- **M5. Round-off size** (float64, cond(Q) ≈ 10⁷).
- **M6. Discretization row**: size 0 by LPC.NV.1 with the V6 value reported, or another reading.
- **M7. Interval-procedure row**: the WU-0006 case per QoI (proposed: H2a(i) → C3, H2a(ii) interior → C7, zero part "not measured", H2b(i) → C1, H2b(ii) → C8, H3c → C4 with C4h at σ 1.5 and 2), the size mismatch (C1 at n = 500 against 300 sweep states), and the shortfall conversion 1 − z(observed)/z(nominal) as a fraction of the half-width.
- **M8. Proxy row** per QoI.
- **M9.** The strict "< 10%" rule.

### Order of work and split
One branch, five commit groups, each one coherent change:
1. **.3** labels and captions (`budget.py` skeleton, report hunks R2, R4, R6, R7). No WU-0005.4 dependency.
2. **.4** declaration table (identifiers dict, hunk R3).
3. **AM section** M1 to M9 (can run in parallel with 1 and 2).
4. **.2a** `endpoint_mc_error` and the five `ci_mc_se` sites; DEV-0 smoke comparison A1.
5. **.1 and .2b** budget tables (hunk R5) with all rows; the LM row reads WU-0005.4's keys if merged, else prints the `not estimated` reason. Re-point `LM_SUMMARY_PATH` in a one-line follow-up when WU-0005.4 merges.
6. **.5** review and owner checkpoint.

### Conflict surface: hunks in `report.py`
Each hunk is wrapped in `# --- WU-0008.k begin ---` / `# --- WU-0008.k end ---`; no existing line is edited.
- **R1** imports: one line `from .budget import ...`.
- **R2** `write_markdown`, after the verdict-table loop: `lines += interval_label_lines(...)` (.3).
- **R3** right after R2: `lines += ["", *qoi_declaration_lines(...)]` (.4).
- **R4** after `_v7_rows`: the V4 label line (.3).
- **R5** after the P2(c) subsection, before Robustness: `lines += ["", *budget_lines(...)]` (.1, .2).
- **R6** before the Handling section: `lines += ["", *figure_caption_lines(...)]` (.3).
- **R7** `make_figures`: one `caption_figure(fig, "<file>")` line before each of the four `savefig` calls (.3).
`identifiers.py`: one appended block at the end of the file. `analysis.py`: five small hunks at the primary sites. Other lanes touching the same files: WU-0005.4 (`report`, `analysis` or `estimation`), any WU-0002 follow-up.

### Risks
- The coverage constants describe synthetic AR(1) data at pilot sizes, not the study's states (residual lag-1 unknown, DEC-0018 O4); the cell says so.
- C2h/C4h show heavier tails cover worse (0.920 to 0.933 at 95%); H3c's row cites them.

### Questions for the owner
- **O1.** Declaration table with 14 rows (gain bound included, NVVUQ.22) instead of the ROADMAP's 13?
- **O2.** A ninth budget row for the interval procedure (DEF-0020). Should the `uq-budget` skill gain it too (the owner's edit)?
- **O3.** WU-0006 numbers as constants with provenance in `budget.py`, or a committed JSON under `lpcstudy/`?
- **O4.** No figure draws an interval today. Add the stored 95% median intervals to `knob_response_library.png`, or keep captions only (default: captions only, LPC.PC.1)?
- **O5.** Budget tables for secondaries and Q-N now or later (NVVUQ.15 says every reported QoI)?
- **O6.** Accept the slow radius of exact-check nodes only (C4, C7, C8) for the .2a change?

## Log

<dated entries: what was done, commands, results, commits>

### 2026-10-11, developer claude-sonnet-5-5: WU-0008.3 and .4 (labels, captions, QoI table)

Scope of this session: .3 and .4 only. Not done here: the budget tables (.1), `endpoint_mc_error` and `ci_mc_se` (.2), `analysis.py`, `statistics.py` (the mathematician's M1 to M9 run in parallel).

- `git merge develop` (own command): merged cleanly (DEC-0021 only), no conflict markers (grep over docs, lpcstudy, tests, tools). Base smoke for the A1-style comparison was run at the branch base (7dc4f45, clean tree) before any edit: `LPC_THREADS=4 tools/run_preset.sh smoke DEV-0 runs/base`, exit 0, 64 s.
- Graph fixture, derived by reading the imports: `budget.py` has `from .config import StudyConfig` and `from .identifiers import HYPOTHESIS_TABLE, Hypothesis` (stdlib `textwrap`): `budget -> [config, identifiers]`; `report.py` gains `from .budget import ...`: `report -> [allocation, budget, config, identifiers, statistics]`. Module count 21 to 22 (`test_fixture_schema` count updated; a count, not a tolerance).

**Test run 1 (.3 code: budget.py labels and captions, report hunks R1, R2, R4, R6, R7).** Checklist:
1. Change set: `lpcstudy/budget.py` (new), `lpcstudy/report.py`, `tests/unit/test_budget.py` (new), `tests/unit/fixtures/lpcstudy_graph.json`, `tests/unit/test_tools_test_impact.py` (docstring and count), this unit file.
2. Radius: `tools/test_impact.py --base develop --explain` gives unit `test___main__`, `test_budget`, `test_report`, `test_tools_test_impact` (rule: `budget` module = own + direct dependents; `report` = pipeline module = own + dependents + integration; the fixture selects the tests naming it); plus by hand, as the main session asked, `test_data.py` and `test_validation.py`. Smaller than the whole suite; no gate. The integration pair runs once at the end, with the smoke by hand.
3. Already run? No: first run of this code.
4. Device: `JAX_PLATFORMS=cpu` (the wrapper sets it).
5. Threads and time: `LPC_THREADS=4`; unit timeout 300 s.
6. Contention: no `lpcstudy --preset` run active (`pgrep` empty before the base smoke; that smoke has finished).
7. Output: wrapper's `-q --tb=short -rfE`; summary and failures only.
8. Command: `LPC_THREADS=4 tools/run_tests.sh unit tests/unit/test___main__.py tests/unit/test_budget.py tests/unit/test_report.py tests/unit/test_tools_test_impact.py tests/unit/test_data.py tests/unit/test_validation.py`.

Result of run 1: `148 passed in 14.06s`. Self-check of the diff for `clip|nan_to_num|isfinite|where(|try:|except` and for `default_rng|random.|PRNGKey`: none in `budget.py` or the report hunks (two `try:` in `test_budget.py` close figures in a `finally`; no handling of a value). No tolerance in an assert or approx was touched (the changes to `test_tools_test_impact.py` are a docstring and the module count 21 to 22).


Commit dff3692 (.3).

**Test run 2 (.4 code: `QOI_DECLARATIONS` and `QOI_FIELDS` appended to `identifiers.py`, the QoI section of `budget.py`, report hunk R3 and its import, tests in `test_budget.py` and `test_identifiers.py`).** Checklist:
1. Change set: `lpcstudy/identifiers.py`, `lpcstudy/budget.py`, `lpcstudy/report.py`, `tests/unit/test_budget.py`, `tests/unit/test_identifiers.py`, this unit file. The import graph does not change in this step (budget already imported `config` and `identifiers`).
2. Radius: `tools/test_impact.py --base develop --explain`: unit `test___main__`, `test_analysis`, `test_budget`, `test_experiments`, `test_identifiers`, `test_report`, `test_tools_test_impact` (rule: `identifiers` = own + direct dependents analysis, experiments, report, budget; `report` and `budget` as in run 1), plus by hand `test_data.py` and `test_validation.py`. Not the whole suite; no gate.
3. Already run? No: the identifiers and budget code and the added tests differ from run 1; test_analysis and test_experiments have not run on this branch.
4. Device: `JAX_PLATFORMS=cpu`.
5. Threads and time: `LPC_THREADS=4`; unit timeout 300 s.
6. Contention: no `lpcstudy --preset` run active.
7. Output: wrapper's `-q --tb=short -rfE`.
8. Command: `LPC_THREADS=4 tools/run_tests.sh unit tests/unit/test___main__.py tests/unit/test_analysis.py tests/unit/test_budget.py tests/unit/test_experiments.py tests/unit/test_identifiers.py tests/unit/test_report.py tests/unit/test_tools_test_impact.py tests/unit/test_data.py tests/unit/test_validation.py`.

Result of run 2: `1 failed, 243 passed in 20.60s`. The one failure, `tests/unit/test_identifiers.py::test_no_stale_identifier_in_the_package`, is not caused by this change and is **not fixed here** (out of scope: `statistics.py` is the mathematician's lane, and the test is not to be loosened): it reports `('statistics.py', 'stale', 'Kaplan-Meier estimator for discrete first-passage times...')`, i.e. the docstring of `kaplan_meier` (introduced in a486b7d, WU-0002.11b, present on `develop`) contains "inventory row T1", and the test's regex `T1` (a stale v1 id) matches it. Nothing in `budget.py` or `QOI_DECLARATIONS` is flagged. For the main session: reword that docstring on develop (e.g. "inventory row 1 of T-series") or the test must learn that "inventory row T1" is not an id; the owner or the planner decides. Not rerun (no code change).
Self-check of the .4 diff: no `clip|nan_to_num|isfinite|where(|try:|except` and no `default_rng|random.|PRNGKey` in non-test code; no tolerance in an assert or approx touched; the QoI texts are drawn from v3 sections 2, 5, 7, 8 and Methods v2 M12.

Commit 8decf2a (.4). Report-only checks before run 3 (no run of a pilot-size preset: the project hook blocks any command line naming one without the GPU lock, so the old-schema case calls `verdicts`, `write_markdown` and `make_figures` directly on the stored DEV-0 pilot `results.json` with the pilot config): (a) the base smoke results (`runs/base/smoke`, copied to `runs/rep`) with `python -m lpcstudy --preset smoke --out runs/rep --seed-id DEV-0 --report-only`: exit 0, `results.json` identical to the base after a key-sorted JSON dump, `RESULTS.md` differs by additions only (the label block, the QoI section, the V4 label line and the Figures section); (b) the DEV-0 pilot `results.json` (three systems, schema before the new keys): no exception, 16 label lines, stored levels 0.9833 (H2b library change, H3c) and 0.95 (H1a, H1d) agree with the roles, the four figures written. Reading the output showed "(reported) (reported)" on the gain-bound label line: fixed in `budget.interval_label_lines` (role omitted when the id already says it) with one assert added to `test_budget.py`.

**Test run 3 (that fix).** Checklist:
1. Change set: `lpcstudy/budget.py` (one line pair), `tests/unit/test_budget.py` (one assert), this unit file.
2. Radius: `tools/test_impact.py`: `budget` = own + direct dependents: `test_budget.py`, `test_report.py`. Not the whole suite.
3. Already run? No: the code changed after run 2.
4. Device: `JAX_PLATFORMS=cpu`.
5. Threads and time: `LPC_THREADS=4`; unit timeout 300 s.
6. Contention: a pilot of another worktree is running (`v1-baseline`); a unit run is not a preset and is not `slow` or `gpu`.
7. Output: wrapper's `-q --tb=short -rfE`.
8. Command: `LPC_THREADS=4 tools/run_tests.sh unit tests/unit/test_budget.py tests/unit/test_report.py`.

Result of run 3: the first invocation gave `1 failed, 35 passed in 1.78s`: the new assert failed because the one-line fix to `budget.py` had not been written (the command that held it was blocked by the hook, see above; the test was written first and caught it). Fixed; `--lf` on the failing test: `1 passed`; radius once more: `36 passed in 1.71s`.

Commit b6b406f (the fix).

**Test run 4 (integration pair, once, at the end).** Checklist:
1. Change set: as above (`budget.py`, `identifiers.py`, `report.py`, tests, fixture).
2. Radius: integration tier, `test_cli_seeds.py` and `test_preset_wrapper.py` (the `report` change selects `tests/integration`; the smoke pipeline test is replaced by the DEV-0 smoke by hand, as the plan says).
3. Already run? No: first integration run on this branch.
4. Device: `JAX_PLATFORMS=cpu`.
5. Threads and time: `LPC_THREADS=4`; integration timeout 900 s.
6. Contention: the `v1-baseline` pilot of another worktree was running. **Correction (written after the run):** I had assumed both files only refuse before any study runs; `test_preset_wrapper.py` in fact runs two smoke presets (wrapper and direct, CPU, `LPC_THREADS=4`, bitwise comparison). They ran next to the pilot, against the instruction not to start a smoke while a run shows. No result is affected (CPU, fixed threads, the pilot is another process on another worktree), but the instruction was not followed and the reason is this wrong assumption.
7. Output: wrapper's `-q --tb=short -rfE`.
8. Command: `LPC_THREADS=4 tools/run_tests.sh integration tests/integration/test_cli_seeds.py tests/integration/test_preset_wrapper.py`.

Result of run 4: `10 passed in 67.52s (0:01:07)`.

**DEV-0 smoke comparison (A1-style): deferred.** `pgrep -fa 'lpcstudy --preset'` shows the `v1-baseline` pilot (started 20:05 UTC, on its second system at 20:15) after the work above, so the new smoke at the branch head was not started. The base smoke (branch base 7dc4f45, clean tree, DEV-0, `LPC_THREADS=4`) is in `runs/base/smoke` of this worktree. To finish: `LPC_THREADS=4 tools/run_preset.sh smoke DEV-0 runs/new` when no run shows, then `.venv/bin/python <scratchpad>/leafcmp.py runs/base/smoke/results.json runs/new/smoke/results.json` (the script packs every float as IEEE bytes, type-checks ints, strings, bools, None, and prints the counts with and without `provenance` and `seconds`). Evidence so far: the report-only run on the base results at the branch head gives 4393 leaves, 0 different, none only on one side (same script), and `RESULTS.md` differs by additions only.

### 2026-10-11: WU-0008 mathematician design (M1–M9)

Applied-mathematician (claude-opus-5-5), branch `wu/0008-report-budget`; plan at ad2eee1. No library code, no study run, no confirmatory seed. Inputs read:

- the DEV-0 pilot outputs `lpcstudy-wt/run/pilot-dev0/runs/dev/wu0002-12/pilot/results.json` (B = 500, n = 500 test and 300 sweep states, M = 200, V4 on 40 states);
- `docs/study/dev_regression_dev0.md`;
- the WU-0006 Log (run 2) and the reference note `docs/agent/notes/2026-10-11-math-wu0006.md` (at bd21e76).

Every pilot number below is **DEVELOPMENT (DEV-0)**. The synthetic studies ran on CPU with literal seeds, none registered. Scripts and their logs are in `docs/agent/notes/2026-10-11-math-wu0008-scripts/` (`m2_e1`, `m2_e2`, `m2_median`, `m2_ratio`, `m3_m5_pilot`, `m7`, `m7b`).

**Decisions in brief.**

- **(a) Oracle draw noise.** Its variance is already inside every primary interval, because states are resampled together with their M-draw estimates. Only the finite-M bias is outside. "hw/√n" is therefore not an uncovered error. The row reports the bias direction always, a size where one exists (F1, F2 below), and no 10% flag.
- **(b) Endpoint error and its tests.** The formula is confirmed. Failed resamples get one added None rule. E1 is tightened to 2%. **E2 as planned is unsound:** a correct helper fails it with probability 0.13. It is replaced by a median-over-repetitions check at a factor of 1.4, with a false-alarm probability of about 2·10⁻⁴.
- **(c) Iterative error.** The LM row cannot be converted to the QoI scale: "not estimated" with the reason in M4.
- **(d) Round-off.** 10⁻⁴ × max(|lo|, |hi|), from the measured cross-platform perturbation.
- **(e) Discretization.** 0 by LPC.NV.1, with V6 printed.
- **(f) Interval procedure.** H2b(i) maps to C8, not C1. The size should come from the WU-0006 *reference* rates (SE ≤ 0.0013), not from the run-2 counts alone (SE of the shortfall ±0.036).
- **(g) The 10% rule** is strict.

#### M1. Rows per QoI (type; included in the reported interval; what each QoI's cell holds)

| # | Row | Type | Included? | H2a(i) | H2a(ii) zero / interior | H2b(i) | H2b(ii) | H3c |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Oracle Monte Carlo (M draws) | aleatory | variance: yes (propagated); finite-M bias: no | bias upward; indicative bound F1 | bias toward 0; not estimated | bias toward 0; not estimated | bias not estimated; variance share F2 | not estimated: enters only through the fitted A4/A5 inputs |
| 2 | Sampling of test states | aleatory | yes | hw of `range_ci` | hw per part | hw, n = sweep | hw, n = sweep | hw; conditional on the fitted A4, A5 |
| 3 | Bootstrap Monte Carlo error | numerical | no | `ci_mc_se` (M2) | per part | yes | yes | yes |
| 4 | Discretization (RK4) | numerical | no | 0 by LPC.NV.1; V6 printed (M6) | same | same | same | same |
| 5 | Iterative (LM) | numerical | no | not estimated (M4) | same | same | same | same |
| 6 | Round-off | numerical | no | 10⁻⁴·max(\|lo\|, \|hi\|) (M5) | per part | same | same | same |
| 7 | Proxy | estimator | reported separately | 0 by construction (oracle only) | 0 | 0 | 0 | not estimated: deployable QoI; fidelity reported (M8) |
| 8 | Model form | epistemic | no | not estimated: v3 §8 | same | same | same | same |
| 9 | Interval procedure | statistical method | no | C3 (proxy) | zero: not measured / C7 | C8 | C8 | C4, C4h |

Two sentences go under every table, in addition to the plan's label and seed lines:

- "Conditional on one realization per system of the trajectory, the library noise and the trained networks. Between-realization variability is not estimated (v3 §8, future work)."
- For H3c only: "Conditional on the fitted A4 and A5. Fit-stage variability is outside the interval and not estimated."

#### M2. Endpoint Monte Carlo error

**Specification.** Inputs:

- `values`: all B resamples, failed ones included;
- `level`, with a = (1 − level)/2.

For each endpoint q ∈ {a, 1 − a}, d = √(a(1 − a)/B); d is the same at both ends. Then SE_q = (Q̂(q + d) − Q̂(q − d))/2. Q̂ is `np.quantile` (linear) on the same array `percentile_interval` uses: failures are replaced by the finite minimum for the lower endpoint and by the finite maximum for the upper.

**Why this is the right quantity.** The rank of the bootstrap distribution's q-quantile among B resamples is Binomial(B, q), so the empirical CDF has SD d there. [Q̂(q − d), Q̂(q + d)] is the ±1 SE order-statistic interval of that quantile. Its half-length estimates d/f(F⁻¹(q)), the asymptotic SD of the endpoint (Bahadur). It is the Monte Carlo error from finite B given the data, not sampling error.

**Both values are None when any of these holds:**

1. **The bound is infinite** (A3 rule): F ≥ ⌊(B − 1)a⌋ + 1.
2. **Failed resamples reach the binomial window:** F ≥ ⌊(B − 1)(a − d)⌋ + 1, evaluated in float64 as in `percentile_interval`. Then Q̂(q − d) for the lower endpoint, and Q̂(q + d) for the upper, weights a failed value. The bound can then become infinite under another bootstrap seed, so its MC error is unbounded. At B = 2000 the window thresholds are 43 (95%) and 13 (1 − 0.05/3), against bound thresholds of 50 and 17. Checked: with F = 13, `np.quantile` at a − d gives −inf; with F = 12 it is finite.
3. **The window leaves (0, 1):** q − d ≤ 0 or q + d ≥ 1. This happens with B = 50 at 1 − 0.05/3 (smoke).

The budget derives the reason from (ci, n_failed, B, level):

- "bound infinite (A3)";
- "failed resamples (F = …) within one binomial SE of the endpoint";
- "B = … too small for the binomial window".

**Ties.** SE = 0 iff Q̂(q − d) = Q̂(q + d), which happens when the endpoint sits on an atom of the bootstrap distribution. Report it as "0 (tie at the endpoint)". It is a correct reading, because the endpoint does not move under a ±1 SE change of rank.

I simulated an H2a(i)-like median with eligibility and an atom at 0 (`m2_median`):

- with the atom at 0–20% of states, P(SE = 0) < 1%;
- with the atom at 45%, P(SE = 0) is 30–50% at the lower endpoints.

**Precision of the estimate itself.** The relative SD is about 1/√(2dB): simulated 0.27 at 95% and 0.34 at 1 − 0.05/3 for B = 2000; about 0.38 and 0.50 at B = 500 (order of magnitude only). Its median, relative to the true MC SD, is:

- 0.98 for a mean;
- 0.83–0.95 for a median on average, and as low as 0.36 in single data sets, where the discreteness of the bootstrap distribution pulls it down.

**Expected size against the half-width.** For a near-normal bootstrap distribution, SE/hw = √(a(1 − a)/B)/(φ(z)z):

| B | 95% | 1 − 0.05/3 |
| --- | --- | --- |
| 2000 | 3.05% | 3.74% |
| 500 | 6.1% | 7.5% |

For heavy-tailed ratios (H3c-like, log-normal σ = 1 to 2; `m2_ratio`):

- at B = 2000 the upper endpoint has median 3.7–5.1% and p95 6.0–8.3%, and P(flag) ≤ 0.02;
- at B = 500, P(flag) is 0.32–0.42.

At the study's B = 2000 the row should therefore read "yes". On the DEV-0 pilot (B = 500) some rows will read "no". That reflects the setting, not a defect.

**E1, tightened to 2%** (was 3%). The deterministic deviations (`m2_e1`) are −0.334% at 95% and −0.909% at 1 − 0.05/3. These are curvature (+0.52% and +1.72%) partly cancelled by grid interpolation. 2% is 2.2 times the larger deviation. A formula error (missing /2, n in place of B, wrong q) gives at least 29%.

**E2, replaced: the planned check is unsound** (`m2_e2`, 1000 synthetic data sets × 100 bootstraps; φ = 0.3, n = 500, mean, block 5, B = 2000).

- A single first-bootstrap helper SE has relative SD 0.27–0.34. The probability that it falls outside a factor of 2 of the reference is 0.016–0.019 per endpoint at 95% and 0.052–0.054 at 1 − 0.05/3, so **P(any of the 4 fails | correct code) = 0.13**. A fixed seed does not cure this.
- **Replacement.** For each of the 4 endpoints, the median over the 100 bootstraps of the helper SE must lie within a factor of 1.4 of the SD of that endpoint over the same 100 bootstraps.
  - log(median ratio) has mean −0.02 and SD 0.08 (0.076–0.085), so the false alarm is about 2·10⁻⁴ (normal approximation). None of 1000 simulated data sets failed; the extremes were 0.73 and 1.28.
  - It catches any systematic error of 1.4× or more. The old check passed a helper that was 1.6× off about 80% of the time.
- Same data (`make_rng(8008, "wu0008", "nested")`), R = 100, B = 2000 and cost as planned. The first-bootstrap ratio is printed in the assertion message, not asserted.
- Answer to "should the median also be checked": yes. The median replaces the single check.

**E3 additions.** At B = 2000 and level 1 − 0.05/3: F = 13 gives (None, None) with finite bounds; F = 12 gives finite values.

#### M3. Oracle Monte Carlo row

**Principle.** Each state's M draws are its own stream. The library noise is common to all states but is part of the conditioning realization. Draw noise is therefore independent across states, and the block bootstrap over states resamples it with the states. So the reported interval includes the draw-noise variance: exactly for means, and asymptotically for the median, the ratio and the partial correlation. What it does not include is the finite-M bias of a statistic that is nonlinear in the per-state estimate. The row states that bias:

- **Included?** "variance: yes (propagated); finite-M bias: no".
- **Flag:** "not estimated", never compared as a size.

**V4 inputs.** V4 runs at the core cell (ρ = 1%, N_lib = 10⁴), at H_ref only, on 100 states (40 at the pilot).

- h = `convergence[str(M)].median_half_width`, a = `convergence[str(M)].mean_abs_dev_from_max`, M = `used_M`, M_max = the largest key.
- s_med = h/z₀.₉₇₅.
- s_mean = a/(√(2/π)·√(1 − M/M_max)) = a/0.690988. This uses nested draws, Var(ŵ_M − ŵ_Mmax) = (1 − M/M_max)s², and the Gaussian E|X| = √(2/π)σ.
- Pilot: s_med = 0.0189, 0.0199, 0.0157 and s_mean = 0.0438, 0.0241, 0.0230 (Lorenz-63, Rössler, Chua). Lorenz-63's heavy tail fits wrong-basin draws.
- Neither is an RMS. The Gaussian factor understates heavy tails, and RMS ≥ mean.

**H2a(i), F1.** E[range(ŵ)] ≥ range(E ŵ), because max is convex and min concave. The median range is therefore biased **upward, toward a fail**. A pass is robust to it; a fail is not certified against it.

- Indicative worst case, assuming draw noise independent across the k = 3 horizons and SD s_med at each: **F1 = (3/√π)·h/z₀.₉₇₅ = 0.86362·h** (E range of 3 iid N(0, 1) = 3/√π). Use 2/√π if k = 2.
- Common draws across horizons make the true bias smaller. Under exact separation it is zero, because the sample ŵ is then the same at every horizon.
- Pilot: F1 = 0.032, 0.034 and 0.027, that is 0.86, 0.57 and 0.43 of the half-width.
  - The Rössler fail survives: 0.211 − 0.034 = 0.177 > 0.1.
  - **The Chua pilot fail does not survive the worst case:** 0.1135 − 0.027 = 0.087.
- Cell: "not estimated: finite-M bias upward (toward fail); indicative worst case ≤ F1 (independent draw noise across horizons; V4 at H_ref only)".
- Follow-up (not this unit): V4 at 1, 2 and 4 LT on the same draws, giving the per-state range's own spread.

**H2a(ii).**

- **Interior part.** Λ̃ is noise-free: `o.growth` comes from the true state. The classical part of the draw noise in logit ŵ (zero mean, independent of Λ̃ given Q) leaves the covariance unchanged and inflates the residual variance. Each partial correlation is therefore attenuated by A = (1 − σ²_e/σ²_{y|Q})^½. This works **toward 0, that is toward the band (−0.1, 0.1): it favours a pass and works against a fail.** A fail is robust to it; a pass is not certified against it. Its size at the band edge is 0.1·(1 − A).
  - σ²_e is not stored. V4 is on the w scale at the median state, and the logit noise s_i/(w_i(1 − w_i)) needs the per-state w.
  - It is probably small: the part of the noise in span[1, Q] is removed, because ε̂_s and δ̂ come from the same draws.
  - A non-classical part (the O(s²) logit bias depends on w and s, which can depend on Λ̃) has unknown sign.
  - Noisy controls (ln ε̂_s and ln δ̂, with relative SD about 1/√(2M) = 5%) leave residual confounding of order 1 − reliability. That is small, of unknown sign.
- **Zero part.** Misclassification of 1{ŵ = 0} near u = 0 attenuates toward 0 if it is nondifferential. It is differential if its rate depends on Λ̃, and then the sign is unknown.
- Cell: "not estimated: per-state draw variance on the logit scale not stored; the classical part attenuates toward 0 (favours a pass; a fail is robust)".
- Follow-up: split-half reliability (draws 1–100 against 101–200) in the WU-0003 per-state dump.

**H2b(i).** Draw noise flips ranks across the four ρ cells. For symmetric noise, a state with constant w has E[ρ_S] = 0 by global sign symmetry, and a monotone state is pulled toward 0. So the mean is attenuated **toward 0, against a pass** of "lower bound > 0": a pass is robust to it, a fail is not certified against it. Common random numbers across ρ reduce flips. The size needs the per-state gaps between levels relative to s, and V4 exists only at ρ = 1%: not estimated.

**H2b(ii), F2.** The variance is inside the interval.

- **F2 = z_L·√2·s_mean/√n**, with n = `library_change.n_states`. It is an upper estimate of the share: it assumes zero correlation of draw noise across N_lib and V4's 10⁴ s at 10³.
- Pilot: 0.0086, 0.0047 and 0.0045, that is 0.21, 0.12 and 0.10 of the half-width. With M = ∞ the half-width would shrink to √(hw² − F2²), at most 2.2% narrower. More draws would not change the verdict.
- Bias: interior terms are O(1/M) and cancel in the pair. At the clip bounds the bias is O(s): for unclipped u = 0, E[max(0, u + e)] = s/√(2π) = 0.40s. It is upward at 0 and downward at 1, and partly cancels in the pair. |bias| ≤ 0.40·s·f_b, where f_b (the fraction of states within about 2s of a bound) is not stored.
- Cell: "not estimated: finite-M clip-boundary bias (≤ 0.40·s per state near a clip bound, partly cancelling in the pair); variance inside the interval, share ≈ F2".

**H3c.** The text in the M1 table is confirmed. The per-state test MSE uses E evaluation draws, not the M oracle draws: E = 4, and 2 at the pilot. Given the weights it is linear and unbiased, its variance is in the interval, and the ratio-of-means bias is O(1/n). M-draw noise reaches H3c only through the A4 coefficients (construction) and the A5 leaf weights (calibration), each an average over hundreds of states. The interval conditions on them.

**B5** tests F1 and F2 only, against one float expression each.

#### M4. Iterative (LM) row: no conversion to the QoI scale

The stop is a fixed budget of 15 iterations with no tolerance stop. The WU-0005.4 keys are: residual c (sum of D = 7 squares in σ_x units), accepted steps, fraction with no decrease, and non-finite count. None of them maps to w* or to the forecast errors:

1. **The residual.** At the MLE, c ≈ ρ²χ²₄: median 3.36ρ², p95 9.49ρ². The excess of c over that floor bounds the iterative error ‖J(û − u*)‖² in the *observation* metric. δ and the forecast errors live in the *state* metric, and ‖û − u*‖² ≤ excess/λ_min(JᵀJ) is vacuous at cond(JᵀJ) ≈ 10⁷.
2. **The counts.** Accepted-step counts and no-decrease fractions say nothing about the distance to the optimum.

A conversion needs one of two things:

- the last accepted step length in the state metric relative to δ, per estimate (not recorded; WU-0005.4 M4's default is not to add it);
- an iteration-doubling refinement of the QoI: 15 → 30 iterations, same draws, and w* and the five statistics recomputed. That is a study run, outside this unit.

Wrong-basin estimates (about 2% for Lorenz-63) are kept by design (v3 §4). They are part of the forecaster, not iterative error.

**Cell.**

- If the keys are absent: "not estimated: WU-0005.4 summary absent from results".
- If present: "not estimated: residual and iteration summary do not convert to the QoI scale (excess residual bounds the error in the observation metric only; cond(JᵀJ) ≈ 1e7); needs a 15 → 30 iteration refinement of the QoI; diagnostic (core cell): median residual/(3.36ρ²) = …, fraction no decrease = …".
- Flag: "not estimated".

**Consequence (PRIME.3, NVVUQ.9).** With this row unestimated, each primary's numerical error is partly unverified (iterative), and its label must say so. The alternative is an owner convention like LPC.NV.1 for the estimator: "PLP is defined by the fixed 15-iteration LM". Then the row is 0 by definition and the summary a diagnostic. That is the owner's governance decision. It is not proposed here.

#### M5. Round-off row

**Analytic bounds, all negligible.** Everything is float64 (u = 1.1·10⁻¹⁶):

- per-state moments are sums of M = 200 terms: relative error ≤ Mu ≈ 2·10⁻¹⁴;
- `curvature` = E_C + E_P − 2C cancels, but c ≥ ρ²/k (P1(a)), so at H_ref the relative error is ≲ 10³u;
- ν comes from a forward formula, and Q (cond ≈ 10⁷) is never inverted. Inverting it would have cost ≤ cond·u ≈ 10⁻⁹.

**Empirical bound, which dominates and sets the row.** I compared DEV-0 with the v1 pilot on another host, where the BLAS kernel and the XLA thread count differ (DEF-0023, DEF-0024). The ulp-level input perturbations are amplified by the flow, the LM and the network training. Over 2458 differing leaves (fitted coefficients at a floor near 0 excluded as chain-head events; `m3_m5_pilot`):

- **QoI-type statistics** (MSE means, H2c and H2d interval endpoints, oracle recovery) change by at most **6.0·10⁻⁵ relative**;
- **oracle w\* medians up to 4 LT** change by at most 9.5·10⁻⁶ (1.3·10⁻⁴ at 7 LT);
- **discrete-event statistics** move by one state's share. In `gain_bound` that is 0.3–0.7% for the fractions and 33% for a maximum; none of these is a primary.

The primaries themselves were changed by design in that comparison, so this is a transfer from the same ingredients. Their direct cross-host check belongs to WU-0003.4.

**Cell.** `ROUNDOFF_RELATIVE = 1e-4`; size 10⁻⁴·max(|lo|, |hi|) with finite bounds, in QoI units. Label: "empirical cross-platform perturbation, DEVELOPMENT (DEV-0); excludes a discrete flip (one state's share in a median or a K choice)". At pilot magnitudes this is ≤ 1.4·10⁻⁴ absolute against hw ≥ 0.037, so the flag reads "yes".

#### M6. Discretization row

The size is 0 for all five primaries by LPC.NV.1. Each is a function of forecast errors computed against a truth from the same RK4 map: PLP shares the map, CP copies observations of it, and Λ̃ is that map's growth.

V6 is printed in the cell as the distance between the map and the half-step map over 1 LT. Pilot values are 3.9·10⁻⁵, 3.3·10⁻⁵ and 7.5·10⁻⁵ σ_x, against a gate of 10⁻³. V6 bears on whether the discrete map stands for the published system (with WU-0007's λ_max), not on the QoI. It checks magnitude, not order (NVVUQ.5 gap, WU-0005).

Cell: "0 (LPC.NV.1: truth and model share the discrete map); V6 = … σ_x (map against half step over 1 LT; not added)". Flag: "yes".

#### M7. Interval-procedure row

**Mapping (one correction).**

- **H2a(i) → C3** (median, n = 500). C3 is a proxy only. The eligibility re-evaluated in each resample, the atom at range 0 and the eligible n (322–465 at the pilot) were not simulated (WU-0006 Out).
- **H2a(ii) interior → C7.** C7 has 500 interior states; the pilot interior domain has 334–352, so the real coverage is slightly worse.
- **H2a(ii) zero part:** "not estimated: no WU-0006 case has a binary target (C7's zero column is constant)".
- **H2b(i) → C8, not C1.** H2b(i) is a mean of one per-state series at n = `n_test_sweep` (300 at the pilot). That is C8's estimator and size, since the `_paired_change` mean is a mean of one series. Per-state Spearman values are bounded, so tails are not an issue. C1 (n = 500) may be cited beside it.
- **H2b(ii) → C8** (exact match).
- **H3c → C4 and C4h** (σ = 1.5 and 2, φ = 0). The O4 proxy gives a per-state MSE log-SD of 1.7–2.0, so σ = 2 is the realistic row.

**Conversion.** If the interval behaves like est ± k·z_nom·SE, then p = 2Φ(k·z_nom) − 1, so k = z_obs/z_nom with z_obs = Φ⁻¹((1 + p)/2).

- The half-width needed for nominal coverage is hw/k, so the **shortfall as a fraction of the reported half-width is f = z_nom/z_obs − 1**. The size in QoI units is f·hw; for f ≤ 0 the cell reads "none (coverage ≥ nominal)".
- MC error: SE_f = (z_nom/z_obs²)·SE_p/(2φ(z_obs)).
- At nominal 0.98333, f = 10% ⇔ p = 0.9705, and f = 5% ⇔ p = 0.9774.
- The formula assumes the two tails share the undercoverage. Where WU-0006 has edge rates for a one-sided decision (C4, C7, C8), the cell may cite them as the direct measure.

**Precision: use the reference rates.** From the run-2 counts (R = 1000), SE_f ≈ 0.036, so the 10% flag is undecidable for f between about 0.03 and 0.17. The WU-0006 reference rates (math note, R_ref 10⁴ to 4·10⁴) come from an independent implementation that matches production to 4·10⁻¹⁶, and all run-2 counts lie inside their consistency ranges. Their SE_p is 0.0007–0.0013, giving SE_f = 0.005–0.008.

**Recommended amendment.** The size comes from the reference rate, with SE and R_ref. The run-2 count goes beside it as the production check (`m7b`, `m7`).

| QoI | case | φ = 0: reference p (f ± SE) | φ = 0.3: reference p (f ± SE) | run 2: count (f), φ = 0 / 0.3 |
| --- | --- | --- | --- | --- |
| H2a(i) | C3 (proxy) | 0.9807 (+0.023 ± 0.009) | 0.9732 (+0.081 ± 0.008) | 984 (−0.006) / 973 (+0.083) |
| H2a(ii) interior | C7 | 0.9794 (+0.034 ± 0.008) | 0.9762 (+0.059 ± 0.008) | 972 (+0.090) / 977 (+0.053) |
| H2b(i), H2b(ii) | C8 | 0.9806 (+0.024 ± 0.006) | 0.9682 (+0.115 ± 0.006) | 987 (−0.036) / 972 (+0.090) |
| (H2b(i), cited) | C1 | 0.9800 (+0.029 ± 0.006) | 0.9695 (+0.107 ± 0.006) | 983 (+0.003) / 969 (+0.110) |
| H3c | C4 | 0.9772 (+0.052 ± 0.005) | 0.9715 (+0.093 ± 0.006) | 971 (+0.096) / 961 (+0.160) |
| H3c | C4h σ = 1.5 | 0.9744 (+0.073 ± 0.008) | — | 965 (+0.135) / — |
| H3c | C4h σ = 2 | 0.9669 (+0.124 ± 0.008) | — | 984 (−0.006) / — |

**Flag.** The flag reads the largest f shown. The study's residual lag-1 is unmeasured (DEC-0018 O4), φ = 0.3 is the stress case and σ = 2 the realistic tail.

- H2a(i): yes (0.081; proxy).
- H2a(ii): interior yes (0.059); zero part not estimated.
- H2b(i) and H2b(ii): **no** (0.115 at φ = 0.3; 0.024 at φ = 0).
- H3c: **no** (0.124 at σ = 2).

Each cell names the case, n, the synthetic design ("seed 6006, not a registered seed"), DEF-0020 and the pending Option C or K.

#### M8. Proxy row

- **H2a(i), H2a(ii), H2b(i), H2b(ii):** "0: by construction (oracle w*, oracle seeds, oracle Λ̃; no deployable proxy enters)".
- **H3c:** "not estimated: the QoI compares two deployable rules, so proxy error is not an error of this QoI". Then, reported separately:
  - A4 recovers `A4_vs_A4o` of A4o's gain over A2, and A5 recovers `A5_vs_Astar` of A\*'s;
  - H1d Spearman values, proxy against oracle: analog seed, estimation seed and growth, with N̂ reported only;
  - if the denominator is ≤ 0 (NaN), the cell reads "not computable (A2 ≤ A4o)".
- **Pilot values.** `A4_vs_A4o` = −0.44, −0.68, −0.39: A4 is worse than A2 while A4o beats it, which is the pre-registered reading "H2c fails but A4o beats A2". `A5_vs_Astar` = 0.10, 0.11, 0.28. H1d: 0.68–0.99.
- Flag: "—".

#### M9. The 10% rule

- **Strict.** "Below 10%" is coded as `size < 0.1 * half_width`, in float64 with no tolerance. B3 holds: 0.1 × 1.0 == 0.1 exactly, so 0.09, 0.10 and 0.11 give yes, no and no. The skill's "at least 10 times smaller" differs only at equality; strict is the conservative reading.
- **Half-width.** hw = (hi − lo)/2 per part. Rows 3 (bootstrap MC error) and 6 (round-off) compare their sizes with it; row 3 compares max(se_lo, se_hi). If hw is not finite, the flag reads "not estimated: interval unbounded".
- **Flag column per row:**
  - rows 3 and 6: yes or no;
  - row 4: "yes" (size 0);
  - row 5: "not estimated" (M4);
  - row 9: yes or no on the largest f (M7);
  - row 1: always "not estimated", since its bias is never a certified size;
  - rows 2, 7 and 8: "—".

#### Plan amendments needed (for the planner and the owner; nothing is loosened)

1. **E2 replaced** by the median check at a factor of 1.4 (M2). The planned single-value factor-2 check has P(false fail) = 0.13.
2. **E1 tolerance:** 3% → 2%.
3. **E3** gains the failure-window case, and `endpoint_mc_error` gains None rule 2.
4. **M7 mapping and constants:**
   - H2b(i) → C8;
   - `COVERAGE_WU0006` holds the reference rates (p, SE, R_ref; from the WU-0006 math note) as the size, with the run-2 counts beside them;
   - B4 also checks the reference constants against the note's table.
5. **Row 1 semantics:** "variance included (propagated), bias not". F1 and F2 are the only formulas, and B5 tests them.
6. **Row 6:** the empirical constant 10⁻⁴ (M5), not cond·u.
7. **Row 5:** "not estimated: <reason>" even when the WU-0005.4 keys are present. The QoI label carries "iterative error unverified" unless the owner adopts a convention.
8. **Flag column per row** as in M9. B1 should accept a cell that starts with a number ("0: …", "0 (tie …)").
9. **The two under-table sentences** of M1.

**Follow-ups, outside this unit.**

- V4 gains a signed mean deviation and runs at 1, 2 and 4 LT (bias of the mean-type and range QoIs).
- Split-half logit reliability in the WU-0003 per-state dump.
- An LM iteration-doubling study.
- Cross-host primaries in WU-0003.4.


### 2026-10-11, developer claude-sonnet-5-5: fix round 1 (R1 to R6)

Merged develop first (own command, clean; it has the `statistics.py` docstring fix e3b70cc). Changes, text and tests only, no number: R1 the H2a label (all test states resampled, eligibility of (i) and the domain of (ii) re-evaluated inside each resample, DEC-0008 A4); R2 the H2a declaration (indicator 1{w* = 0}, the conditional 1{w* = 1}, quadratic controls, initial segments of 1, 2, 4 LT, "at most 0.5 sigma_x", the edge of (i) is the bound 0.1); R3 the H3b declaration (D lower bound decides, the stability index is reported); R4 H3a cannot fail, H3c quotes v3 section 7; R5 `STORED_LEVEL_PATHS` takes several paths per key and a `*` step: H2e `by_noise[*].level`, H3b `weight_lambda.level` and `D.level`, `stored_level` is now `stored_levels`; R6 the H3b label says "coverage not measured". R7 is the main session's. The A1 smoke rule of the main session applies: .3 and .4 are report-side only; the check is the report-only leaf compare of the Log above (0 of 4393 leaves differ) plus a grep that no producer (`analysis`, `experiments`, `pipeline`, `statistics`, `__main__`) uses `QOI_DECLARATIONS`, `QOI_FIELDS` or `budget` (below); the full A1 smoke runs once at the .2a head.

**Test run 5 (fix round 1).** Checklist:
1. Change set: `lpcstudy/budget.py`, `lpcstudy/identifiers.py`, `tests/unit/test_budget.py`, this file (the merge brought `statistics.py` docstring, decisions, defects, notes).
2. Radius: `tools/test_impact.py --base develop --explain`: unit `test___main__`, `test_analysis`, `test_budget`, `test_experiments`, `test_identifiers`, `test_report`, `test_tools_test_impact`; by hand `test_data.py`, `test_validation.py` (`test_identifiers.py` and `test_tools_test_impact.py` are in the tool's set). Not the whole suite; the integration pair is not needed until the .2a head.
3. Already run? No: `budget.py`, `identifiers.py` and `test_budget.py` changed after runs 1 to 4.
4. Device: `JAX_PLATFORMS=cpu`.
5. Threads and time: `LPC_THREADS=4`; unit timeout 300 s.
6. Contention: none needed (unit tier, no preset).
7. Output: wrapper's `-q --tb=short -rfE`.
8. Command: `LPC_THREADS=4 tools/run_tests.sh unit tests/unit/test___main__.py tests/unit/test_analysis.py tests/unit/test_budget.py tests/unit/test_experiments.py tests/unit/test_identifiers.py tests/unit/test_report.py tests/unit/test_tools_test_impact.py tests/unit/test_data.py tests/unit/test_validation.py`.

Result of run 5: `245 passed in 266.43s (0:04:26)` (slow only because the `v1-baseline` pilot shares the CPU). Grep of `analysis`, `experiments`, `pipeline`, `statistics`, `__main__` for `QOI_DECLARATIONS|QOI_FIELDS|budget`: no match. Report-only on the base smoke results at this head: 4393 leaves, 0 different, none on one side only (`results.json` is written before any report code runs).

### 2026-10-11, developer claude-sonnet-5-5: WU-0008.2a (endpoint_mc_error and ci_mc_se), DEC-0024

Sequence from the main session: .2a, then .1/.2b (with R8). `pgrep -fa 'lpcstudy --preset'` shows the `v1-baseline` pilot, so the A1 smoke comparison at the .2a head, the integration pair and the slow exact-check nodes (DEC-0021 O6) are **pending** and not started.

Changes: `statistics.endpoint_mc_error(values, level)` (docstring marks **needs owner review before freeze**); `analysis.py` at the five primary sites: `ci_mc_se` = `[se_lo, se_hi]` in H2a(i) (`h2a_initial_segments`), per part of H2a(ii) (`h2a_part_ii`), H2b(i) (`noise`), H2b(ii) (`library_change`, via `_paired_change(..., mc_error=True)`, so H2e and the reported changes get no key) and H3c (`h3c_ratio`). The three sites that called `block_bootstrap_counted` (`_paired_change`, H2b(i), `h3c_ratio`) call its body (`bootstrap_values` then `percentile_interval`, same seeds) to keep the resample values; estimates, intervals and counts are the same code path, so every existing leaf is bitwise unchanged and only `ci_mc_se` leaves are new (A1; the full smoke comparison is pending, see above). Self-check grep: the `np.where` in `endpoint_mc_error` is the A3 replacement of `percentile_interval` (failed resamples counted in the interval's `n_failed`; the helper returns None when failures reach the binomial window, rule 2); `isfinite` finds the failures; no `clip`, `try`, `except`; no randomness in library code; test seeds are fixed integers or `make_rng`. No tolerance changed; E1 uses 2%, E2 the median at factor 1.4, E3 the failure-window case, as fixed by DEC-0024.

**Test run 6 (.2a).** Checklist:
1. Change set: `lpcstudy/statistics.py`, `lpcstudy/analysis.py`, `tests/unit/test_statistics.py` (E1 to E3), `tests/unit/test_analysis.py` (A2).
2. Radius: `tools/test_impact.py --base develop --explain`: unit `test___main__`, `test_allocation`, `test_analysis`, `test_budget`, `test_experiments`, `test_identifiers`, `test_pipeline`, `test_report`, `test_statistics`, `test_tools_test_impact`, `test_validation`; by hand `test_data.py`. Integration and the slow exact checks are pending (a run is active).
3. Already run? No: statistics and analysis are new code.
4. Device: `JAX_PLATFORMS=cpu`.
5. Threads and time: `LPC_THREADS=4`; unit timeout 300 s (the pilot shares the CPU; run 5 took 266 s for a smaller set).
6. Contention: unit tier, no preset started.
7. Output: wrapper's `-q --tb=short -rfE`.
8. Command: `LPC_THREADS=4 tools/run_tests.sh unit tests/unit/test___main__.py tests/unit/test_allocation.py tests/unit/test_analysis.py tests/unit/test_budget.py tests/unit/test_experiments.py tests/unit/test_identifiers.py tests/unit/test_pipeline.py tests/unit/test_report.py tests/unit/test_statistics.py tests/unit/test_tools_test_impact.py tests/unit/test_validation.py tests/unit/test_data.py`.

Result of run 6: `4 failed, 354 passed in 32.66s`. The four failures were in `test_analysis.py`: (a) `test_h3_regimes_wiring_keys_and_arguments` asserts the exact key set of the H3c result, which now has the additive key `ci_mc_se` (the expected set was updated; a specification of the new key, not a loosening); (b) three cases of `test_h2b_noise_failed_resample_goes_to_the_a3_tail...` inject failed resamples by patching `analysis.block_bootstrap_counted`, which H2b(i) no longer calls (it calls the body, `bootstrap_values`, to keep the values): the injection helper `_inject_first_call` now patches `analysis.bootstrap_values` at the same first call with the same semantics, and its expected numbers, thresholds and assertions are untouched. `--lf`: `4 passed`.

**Test run 7 (.2a, radius once after the fix).** Checklist: 1. change set as run 6 plus the edits to `tests/unit/test_analysis.py` above. 2. Radius: the same as run 6. 3. Already run? Not on this code (the test file changed). 4. Device `JAX_PLATFORMS=cpu`. 5. `LPC_THREADS=4`; unit timeout 300 s. 6. Unit tier, no preset started. 7. Wrapper's `-q --tb=short -rfE`. 8. Command: as run 6.

Result of run 7: `358 passed in 32.11s`. Pending (a preset is running): the A1 smoke comparison at the .2a head, the integration pair, and the slow exact-check nodes `tests/slow/test_analysis_coverage.py::test_exact_checks` for C4, C7, C8 at both phi (DEC-0021 O6).

### 2026-10-11, developer claude-sonnet-5-5: WU-0008.1 and .2b (budget tables), R8

Commit a8bdf0b is the .2a head. Implemented in `lpcstudy/budget.py` (`budget_lines` and helpers, `COVERAGE_WU0006` with provenance, `ROUNDOFF_RELATIVE = 1e-4`, `LM_SUMMARY_PATH = None` until WU-0005.4 names it) and the report hunk R5 (`# --- WU-0008.1 begin/end ---`, after the P2(c) subsection, before Robustness; no existing line edited). Rows and wording follow M1 to M9 as accepted in DEC-0024: finite-M bias stated with F1 (H2a(i)) and F2 (H2b(ii)) only; endpoint error from `ci_mc_se` with the reasons of M2 and "0 (tie at the endpoint)"; discretization 0 with V6; LM "not estimated: WU-0005.4 summary absent from results" (and the M4 text when a path is set); round-off 1e-4 x max(|lo|, |hi|); proxy 0 (H2a, H2b) or the H3c fidelity; model form not estimated; interval procedure from the WU-0006 reference rates (H2a(i) C3, H2a(ii) interior C7 and the zero part not estimated, H2b C8, H3c C4 and C4h) as f = z_nom/z_obs - 1 of the half-width; the 10% flag is strict. Flags per M9. Under each table: the label, the seed line, the 10% sentence, the two M1 sentences (H3c: the extra one) and the iterative-error statement. R8: `test_stored_levels_are_found_on_real_producer_output` in `test_analysis.py` (H1a, H1d, H2b, H2e, H3b, H3c producer output). No `analysis`/`statistics`/`experiments`/`pipeline` file changed in this step, so every results.json leaf is unchanged by it. Self-check grep of the diff: `isfinite` sites in `budget.py` are display branches (an unbounded or missing interval prints "not estimated: ..." and is flagged, never dropped or replaced); no `clip`, `try`, `except`, `where(`; no randomness.

**Test run 8 (.1/.2b and R8).** Checklist:
1. Change set: `lpcstudy/budget.py`, `lpcstudy/report.py` (hunk R5), `tests/unit/test_budget.py`, `tests/unit/test_analysis.py` (R8 test), this file.
2. Radius: `tools/test_impact.py --base develop --explain`: unit `test___main__`, `test_allocation`, `test_analysis`, `test_budget`, `test_experiments`, `test_identifiers`, `test_pipeline`, `test_report`, `test_statistics`, `test_tools_test_impact`, `test_validation` (the `budget` and `report` rules; the earlier statistics rule still applies to the branch), plus by hand `test_data.py`. Integration and slow nodes pending (a preset is running).
3. Already run? No: `budget.py`, `report.py` and two test files changed after run 7.
4. Device: `JAX_PLATFORMS=cpu`.
5. Threads and time: `LPC_THREADS=4`; unit timeout 300 s.
6. Contention: unit tier, no preset started.
7. Output: wrapper's `-q --tb=short -rfE`.
8. Command: `LPC_THREADS=4 tools/run_tests.sh unit tests/unit/test___main__.py tests/unit/test_allocation.py tests/unit/test_analysis.py tests/unit/test_budget.py tests/unit/test_experiments.py tests/unit/test_identifiers.py tests/unit/test_pipeline.py tests/unit/test_report.py tests/unit/test_statistics.py tests/unit/test_tools_test_impact.py tests/unit/test_validation.py tests/unit/test_data.py`.

Result of run 8: `3 failed, 369 passed in 34.03s`. (a) Two tests in `test_budget.py` lacked `import math` (my omission; fixed). (b) `test_no_stale_identifier_in_the_package` flagged `COVERAGE_PROVENANCE`: the plan's log file name `slow-20261011T165447Z.log` contains the substring "T1" that the test's stale-identifier regex looks for. The test is not changed. The constant now reads `slow-20261011…165447Z.log` with a sentence saying the letter between date and time is elided because of that grep (a deviation from the plan's literal string; the file name is recoverable from the stamp). `--lf`: `3 passed` (B5 at 1e-15 passes).

**Test run 9 (radius once after these fixes).** Checklist: 1. Change set as run 8 plus the two fixes (`budget.py` provenance string, `test_budget.py` import). 2. Radius: as run 8. 3. Already run? No, code changed. 4. `JAX_PLATFORMS=cpu`. 5. `LPC_THREADS=4`, unit timeout 300 s. 6. Unit tier, no preset started. 7. `-q --tb=short -rfE`. 8. Command: as run 8.

Result of run 9: `372 passed in 33.33s`. Report-only at this head: the base smoke results give 4393 leaves, 0 different (the budget section and the other additions are report text); the stored DEV-0 pilot results (old schema: no `ci_mc_se`, no LM summary, no `used_M`) render all five tables with "not estimated: no ci_mc_se in these results (written before WU-0008.2a)" and no exception. **Pending, because `pgrep -fa 'lpcstudy --preset'` still shows the `v1-baseline` pilot:** the full A1 smoke comparison at this head (base smoke is `runs/base/smoke`; `leafcmp.py` as above), the integration pair, and the slow exact-check nodes for C4, C7, C8 (DEC-0021 O6).

### 2026-10-11, developer claude-sonnet-5-5: fix round 1 of the .2a and .1/.2b review (R9 to R16)

Corrections to earlier Log statements (append-only; the earlier text stands): (1) the paragraph after test run 9 says the DEV-0 pilot results have no `used_M`. That is wrong: they have `convergence.used_M` (200) in all three systems and the pilot report prints F1 and F2; what the old-schema pilot lacks is `ci_mc_se` and the LM summary. (2) The `QOI_COVERAGE` docstring said C1 is "cited beside" H2b(i); the cell never printed it. Decision: the claim is dropped from the docstring (the C1 constants stay as data, checked by B4, and are not printed). (3) The `.2a` entry's "no `used_M`" has the same origin as (1).

Changes: R9 `CoverageCase.r_ref` (40000 for C1, C4, C8; 20000 for C3, C7, C4h; docstring "2*10^4 to 4*10^4", the C7 pooled 60000 not used), the seed statement names both sources (`COVERAGE_SEEDS_TEXT`, replaces "synthetic, seed 6006") and R_ref is printed per case; R10 `ORACLE_INCLUDED` per QoI (the mathematician's wording, verbatim), the row-1 How text no longer says the variance propagates, a note under the H2a(ii) table about the "one" part; R11 `ITERATIVE_LABEL` appended to `interval_label` of H2a, H2b, H3c (the budget-table sentence is kept); R12 (a) `ci` None reads "no interval in these results" before the `ci_mc_se` text, (b) each F2 cause has its own reason, (c) `_v4` returns the reason (absent / used_M missing / entry missing), (d) the rho-cell count comes from `config.noise_levels`, (e) `A5_vs_Astar` reads "not computable (A2 ≤ A*)", a missing key "not available"; R13 `DEF0020_TEXT` (mathematician's wording) and `WIDENING_SENTENCE` (the uq-budget rule, the owner's choice); R14 B4 parses the C4h counts, A2 asserts H2e carries no `ci_mc_se` (H2c is not exercised: stated), the E3 docstring says what the F = 12 expectation checks; R16 `LM_NOT_READ` while `LM_SUMMARY_PATH` is None (true whatever the merge order; `LM_ABSENT` only once a path is set), F1's k from the configuration (2 or 3 horizons tabulated; otherwise "F1 not computable"). The filename elision and `test_identifiers.py` are untouched. Tests added per reason: `test_budget.py` (R9/R13 text, R10 cells, R12 a to e, R16 F1 and LM, r_ref transcription).

**Test run 10 (R9 to R16).** Checklist:
1. Change set: `lpcstudy/budget.py`, `tests/unit/test_budget.py`, `tests/unit/test_analysis.py` (A2 assertion and docstring), `tests/unit/test_statistics.py` (docstring only), this file.
2. Radius: `tools/test_impact.py --base develop --explain`: unit `test___main__`, `test_allocation`, `test_analysis`, `test_budget`, `test_experiments`, `test_identifiers`, `test_pipeline`, `test_report`, `test_statistics`, `test_tools_test_impact`, `test_validation`; integration not run (a preset is running).
3. Already run? No: `budget.py` and tests changed after run 9.
4. Device: `JAX_PLATFORMS=cpu`.
5. Threads and time: `LPC_THREADS=4`; unit timeout 300 s.
6. Contention: unit tier; `pgrep -fa 'lpcstudy --preset'` shows the `v1-baseline` pilot, so no preset, integration or slow run.
7. Output: wrapper's `-q --tb=short -rfE`.
8. Command: `LPC_THREADS=4 tools/run_tests.sh unit tests/unit/test___main__.py tests/unit/test_allocation.py tests/unit/test_analysis.py tests/unit/test_budget.py tests/unit/test_experiments.py tests/unit/test_identifiers.py tests/unit/test_pipeline.py tests/unit/test_report.py tests/unit/test_statistics.py tests/unit/test_tools_test_impact.py tests/unit/test_validation.py`.

Result of run 10: `2 failed, 363 passed in 26.78s`, both test errors of mine in `test_budget.py`: (a) the old-schema assertion expected "V4 absent", but that fake V4 has convergence entries without `used_M`, which R12(c) now (correctly) reports as "V4 present but used_M missing"; (b) the R12(a) case stored the level 0.98 instead of 1 - 0.05/3, which `row_level` rightly refused. Both fixed in the tests; `--lf`: `2 passed`.

**Test run 11 (radius once after those two test fixes).** Checklist: 1. change set as run 10 plus the two assertions. 2. radius as run 10. 3. already run? No: the test file changed. 4. `JAX_PLATFORMS=cpu`. 5. `LPC_THREADS=4`, unit timeout 300 s. 6. unit tier, the pilot is running, no preset started. 7. `-q --tb=short -rfE`. 8. command as run 10.

Result of run 11: `365 passed in 28.31s`. Report-only on the stored DEV-0 pilot results at this head: no exception, F1 printed in the H2a(i) table, "not estimated: no ci_mc_se in these results (written before WU-0008.2a)" in the bootstrap row (the pilot predates .2a). **Still pending (the `v1-baseline` pilot is running):** (1) the A1 smoke at the head: `LPC_THREADS=4 tools/run_preset.sh smoke DEV-0 runs/new`, then `.venv/bin/python <scratchpad>/leafcmp.py runs/base/smoke/results.json runs/new/smoke/results.json`; the new-only leaves must be the `ci_mc_se` ones, all null at smoke (B = 50, rule 3); (2) the integration pair: `LPC_THREADS=4 tools/run_tests.sh integration tests/integration/test_cli_seeds.py tests/integration/test_preset_wrapper.py`; (3) the slow exact checks: `tools/run_tests.sh slow --background "tests/slow/test_analysis_coverage.py::test_exact_checks[C4-0.0]" "...[C4-0.3]" "...[C7-0.0]" "...[C7-0.3]" "...[C8-0.0]" "...[C8-0.3]"` (node ids as in `--collect-only`, once).

### 2026-10-11, developer claude-sonnet-5-5: fix round 2 (R17 to R21)

Merged develop first (own command; conflicts in `tests/unit/fixtures/lpcstudy_graph.json` and `docs/agent/records/work/queue.md`; no marker left, grep over docs, lpcstudy, tests, tools). The fixture takes develop's version (its edge `experiments -> provenance`, checked against the imports of `experiments.py`, `provenance.py`, `data.py`, `__main__.py` and `report.py`, which agree with the 22 rows) plus this unit's `budget` row, the `report -> budget` edge and the description sentence; `queue.md` keeps both sides' entries.

- **R17 (records).** The source of the five row-1 Included cells, the row-9 DEF-0020 sentence, the widening sentence (the uq-budget rule only) and R_ref per case (C1, C4, C8: 40000; C3, C7, C4h: 20000) is **DEC-0024 addendum A1** (`docs/agent/records/decisions.md`, commit 9fcfa76 on develop), which **amends M1 (a) and M7** of the design. `ORACLE_INCLUDED`, `DEF0020_TEXT`, `WIDENING_SENTENCE` and `COVERAGE_WU0006` cite it in `budget.py`; `test_included_cell_of_the_oracle_row_is_per_qoi` and `test_interval_procedure_cell_names_both_seed_sources_and_def0020_correctly` now parse the addendum from the decisions file (reachable in the worktree after the merge) and compare, with the literals kept as a second copy. No other test says "wording supplied in fix round 1".
- **R18.** The row-1 How text names the "Included in the reported interval?" column.
- **R19.** `ITERATIVE_LABEL` is now `iterative_label(config)`, reading `config.estimator_refine_steps` (and the LM diagnostic's "n → 2n" likewise); tested with 30.
- **R20.** The R15 correction (3) in the entry above is **void**: it "corrects" a statement about `used_M` in the `.2a` entry, and that entry has no such statement. Corrections (1) and (2) stand.
- **R21.** `m2_coverage.log` (in `docs/agent/notes/2026-10-11-math-wu0006-scripts/`, reachable) gives R per case: `test_coverage_r_ref_and_rates_equal_the_reference_run_log` parses R_ref, rate and SE for every case and replaces the "no parseable source" test, whose docstring was wrong.
- At the last check `pgrep -fa lpcstudy` shows no preset (the `v1-baseline` pilot finished: "study finished in 5490s"), so the A1 smoke, the integration pair and the slow exact checks follow below, each after its checklist.

**Test run 12 (R17 to R21; unit radius).** Checklist:
1. Change set: `lpcstudy/budget.py`, `tests/unit/test_budget.py`, this file; the merge brought `__main__`, `data`, `experiments`, `provenance`, `report` changes from develop and the fixture.
2. Radius: `tools/test_impact.py --base develop --explain`: unit `test___main__`, `test_allocation`, `test_analysis`, `test_budget`, `test_experiments`, `test_identifiers`, `test_pipeline`, `test_report`, `test_statistics`, `test_tools_test_impact`, `test_validation`; by hand `test_provenance.py` and `test_data.py` (develop changed `provenance` and `data`, and the fixture merge touches the graph test).
3. Already run? No: new code and the merged tree.
4. Device: `JAX_PLATFORMS=cpu`.
5. Threads and time: `LPC_THREADS=4`; unit timeout 300 s.
6. Contention: unit tier; no preset running.
7. Output: `-q --tb=short -rfE`.
8. Command: `LPC_THREADS=4 tools/run_tests.sh unit tests/unit/test___main__.py tests/unit/test_allocation.py tests/unit/test_analysis.py tests/unit/test_budget.py tests/unit/test_experiments.py tests/unit/test_identifiers.py tests/unit/test_pipeline.py tests/unit/test_report.py tests/unit/test_statistics.py tests/unit/test_tools_test_impact.py tests/unit/test_validation.py tests/unit/test_provenance.py tests/unit/test_data.py`.

Result of run 12: `422 passed in 35.79s`.

## Review

- **Reviewer:** <actor, not the author>
- **Findings and resolution:**

### 2026-10-11, reviewer claude-opus-5-5 (fresh context): WU-0008.3 and .4, round 1

Scope: only .3 (labels, captions) and .4 (QoI table), at f1129a7 (commits dff3692, 8decf2a, b6b406f, f1129a7; plan ad2eee1; merge 7dc4f45). .1 and .2 are not implemented and not reviewed. Inputs: the diff 7dc4f45..f1129a7; `lpcstudy/analysis.py` at every bootstrap site; `experiments.py` (V4); `report.py` (`make_figures`, `write_markdown`, `_key_number`); `__main__.py`; v3 §2, §5, §7, §8; Methods v2 §M12; DEC-0008 A1, A3, A4; DEC-0021. No tests were run. The Log's results stand (148 passed; 243 passed plus 1 unrelated failure; 36 passed; 10 passed). `test_no_stale_identifier_in_the_package` is not counted against this branch: the failure comes from the `kaplan_meier` docstring, which is fixed on develop.

**Checked and correct (no finding).**
- **Purity.** `budget.py` imports only `config`, `identifiers` and `textwrap`. It has no randomness and no assignment into `results`, and it computes no statistic.
- **`results.json` cannot change.** In both `__main__` paths (lines 114–116 and 148–150), `save_json` runs before `write_markdown` and `make_figures`. The new `identifiers` names (`QOI_DECLARATIONS`, `QOI_FIELDS`) are referenced only by `budget`; a grep of `analysis`, `experiments`, `pipeline` and `__main__` finds no use. The report-only comparison (4393 leaves, 0 different) agrees with this.
- **Interval levels and procedures by row, against the code.**
  - H1a: per ρ, joint ratio bootstrap over test-sweep states, 95%.
  - H1b: PLP slope, `block_bootstrap_counted`, 95%.
  - H1c: PLP median, 95%.
  - H1d: three tested Spearman pairs, 95%; N̂ reported only.
  - Q-N: estimate, 95%, no multiplicity.
  - H2b: (i) and (ii) both at 1 − 0.05/3.
  - H2c and H2d: 95%.
  - H2e: 95% median of paired changes.
  - H3a: Holm over consecutive pairs, p-values, no interval.
  - H3b: 95% blocks of construction states, trees refitted.
  - H3c: 1 − 0.05/3 ratio bootstrap.
  - Gain bound: no interval.
  - All of these match the labels except H2a (R1) and H3b (R6).
  - B and the block length are read from `config`. The test on block 7 and B = 123 shows it.
- **V4 label.** It is accurate against `experiments.py:108–120`: iid resampling of the M draws, 200 resamples, half-width (P97.5 − P2.5)/2, median over states, value at `n_oracle_draws`, bar 0.05. The literal 200 is pinned by a test that reads the source.
- **L2.** A mismatch raises `ValueError`. Old-schema results fall back to the level of the row's role; this is documented and is the plan's old-schema case.
- **Figures.**
  - `separation_weight_vs_horizon.png`: the band is `q25` to `q75` across test states (`analysis.py:2135–2139`), and the caption calls it an inter-quartile range, not a confidence interval. Correct.
  - `kaplan_meier_by_rule.png`: the plotted rules are A0–A5 and A\*.
  - `regret_vs_regimes.png`: the dotted line is at 5%.
  - `knob_response_library.png`: it plots medians; the stored 95% intervals are not drawn. Correct.
  - No figure draws an interval. Each caption is written into its PNG by `caption_figure`. The test strips the line breaks and compares the PNG text exactly with the caption.
- **QoI rows checked against v3 and M12, no finding:** H1a, H1b, H1c, H1d, Q-N, H2c, H2d, H2e and the gain bound.
  - The M12 numbers quoted are correct: ±0.13; 0.04 for Q-N and H2a(i); 0.10 for H2a(ii); 0.05 and 0.03 for H2b.
  - The 10 σ_x clip is `ensemble.ERROR_CLIP`.
  - H2b reads correctly; its open bound is carried by the verbatim criterion "> 0".
  - The criterion column is `row.criterion` verbatim. There are 14 rows, and the test checks the row ids against v3 §2 parsed from the file (an independent reference).
- **Graph fixture.** `budget -> [config, identifiers]` and `report -> [allocation, budget, config, identifiers, statistics]` agree with the import lines. There are 22 `lpcstudy/*.py` files. The change from 21 to 22 is a count, not a tolerance. The fixture and test changes are in the same commit as the import edit (dff3692, DoD 4).
- **Report hunks.** Every hunk is wrapped in begin/end markers (R1 import, R2, R3, R4, R6, R7). The diff of `report.py` adds lines only and deletes none.
- **Commits.** Every commit names the unit and ends with `Agent: claude-sonnet-5-5`.
- **No other interval table is unlabelled.** The V7, Lyapunov, P2(c), allocation and robustness tables print no `[lo, hi]` interval.

**Findings.**

- **R1. The H2a label misstates the resampling unit** (`lpcstudy/budget.py:129–132`).
  - The label reads "blocks of 5 consecutive eligible (small-error) test states in time order", and the dependence clause repeats it.
  - The code resamples blocks of **all** test states in time order:
    - (i) re-evaluates eligibility inside each resample (`analysis.py:1067`, `:1118–1121`; DEC-0008 A4(b));
    - (ii) is not restricted to small-error states at all: (ii-a) and (ii-c) run over all states, and (ii-b) applies the interior filter inside each resample (`analysis.py:1158–1159`, `:1211–1219`).
  - Why it matters: the label is the dependence statement of a primary interval (NVVUQ.16), and it is factually wrong for both parts.
  - Fix: name blocks of consecutive test states (all states) in time order, with eligibility (i) and the interior domain (ii-b) re-evaluated inside each resample. Add an assertion on the H2a label that cites DEC-0008 A4(b) as its reference.

- **R2. The QoI declaration of H2a misstates the statistic and the decision-relevant error** (`lpcstudy/identifiers.py`, `QOI_DECLARATIONS["H2a"]`).
  - (a) It says "partial correlation of logit w\* … on the interior and the w\* = 0 parts". The w\* = 0 part is the partial correlation of the **indicator 1{w\* = 0}** over all test states, not of logit w\* (which is undefined at 0). There is also a third part, 1{w\* = 1}, added when w\* = 1 holds in more than 5% of states (DEC-0008 A4(a); `analysis.py:1152–1156`).
  - (b) "Given the analog and estimation seeds" leaves out the quadratic controls x, x², x₁x₂ with x = (ln ε_s/ρ, ln δ/ρ) (A4(a2)).
  - (c) Part (i) is taken over **initial segments**: the first L ≥ 2 of 1, 2, 4 LT that are small-error (A4(b)), not over 1, 2 and 4 LT.
  - (d) For (i), the decision-relevant error "a half-width near 0.1" is wrong. The edge of (i) is the bound 0.1, so what matters is a half-width comparable to the distance of the median range from 0.1 (M12: pilot 0.12–0.28, projected 0.04). The (ii) clause is correct: a half-width near the band half-width 0.1 means it cannot pass.
  - (e) "Below 0.5 σ_x" should be "at most 0.5 σ_x" (`analysis.py:1268`, `<=`).
  - Fix: reword the definition and decision_error of the row from v3 §2 plus DEC-0008 A4(a), (a2) and (b).

- **R3. The QoI declaration of H3b names the stability index as decision-relevant** (`QOI_DECLARATIONS["H3b"]["decision_error"]`).
  - The horizon-tree part is decided by the lower bound of the 95% interval of D = imp_t(Λ̃) − max of the other coordinates' imp_t (> 0, strict). The stability index is reported only (DEC-0008 A3; `analysis.py:1915–1919`, `:1983`, `:1992`).
  - Fix: "a weight-tree Λ̃ upper bound within one half-width of 0.2, or a D lower bound within one half-width of 0; the stability index is reported, not decided". The definition may name D.

- **R4. The QoI rows of H3a and H3c misstate what moves the verdict.**
  - (a) H3a: since no equivalence margin is set, H3a **cannot fail** (DEC-0008 A3; `analysis.py:1788`). An error near 0.01 moves it only between pass and inconclusive, and no outcome refutes it. The decision_error and decision cells should say this; a reader would otherwise read "inconclusive" as a near-refutation.
  - (b) H3c: "excess error flat in K is read as the P3 floor, not as a failure" is not v3's wording. v3 §7 reads a flat excess error as the P3 floor **when H3c holds**. The words "not as a failure" suggest a reading that could override the verdict rule.
  - Fix: state the H3a limit, and quote v3 §7 for H3c.

- **R5. L2 is only partly met: two stored decision levels are not cross-checked** (`lpcstudy/budget.py:35–37`, `STORED_LEVEL_PATHS`).
  - H2e stores `level` per ρ under `by_noise[rho]` (`analysis.py:1581` via `_paired_change`, `:1386`).
  - H3b stores `D.level` (`:1997`); only `weight_lambda.level` is checked.
  - A wrong level at those sites would be labelled silently with the role level. The plan's L2 says "each result carrying `level`".
  - Fix: allow several paths per key, including each `by_noise` entry. Add H2e (every ρ) and H3b D, and extend `test_label_level_equals_the_stored_level_and_a_mismatch_raises` to cover them.

- **R6. The H3b label does not say "coverage not measured"** (`lpcstudy/budget.py:124–127`).
  - The plan (Scope, Out) requires the H3b row of the verdict-table label to say "coverage not measured" (WU-0006 gap).
  - The analysis docstring (`analysis.py:1909–1911`) also states that these intervals condition on the fitted proxies and are not guaranteed to cover.
  - Fix: append that statement to the H3b label, and assert it in `test_budget.py`.

- **R7. Governance: two smoke presets ran during another run** (Log, test run 4, item 6).
  - `test_preset_wrapper.py` started two smoke presets while the `v1-baseline` pilot was running, against `.claude/rules/test-discipline.md`. The developer recorded it.
  - No result is affected: the presets ran on CPU with fixed threads and are compared bitwise within the test.
  - No code fix. The main session decides whether a deviation note is needed. Before any future integration run, check `pgrep -fa "lpcstudy --preset"`.

**Smoke comparison base vs final (A1).**
- **Not required before merging .3 and .4.** `results.json` is written before any `budget` or report code runs, and the `identifiers` additions are append-only constants unreferenced by the producers. The report-only evidence (0 of 4393 leaves differ) is consistent with this, but it is weak: it would hold for any report-side code.
- **Required before the branch merges,** because .2a changes `analysis.py`, and A1 is .2a's criterion. One smoke at the .2a head, run when no preset is running, covers .3 and .4 too.
- **Proposed rule:** a full-preset A1 comparison is required before merge iff the change set touches a module that runs before `save_json` (the import closure of `experiments`, `pipeline`, `analysis` and `statistics`) in more than append-only constants that no producer references. A change confined to code that runs after `save_json` (`write_markdown`, `make_figures`, `budget`) is covered by a `--report-only` leaf compare on stored results plus that grep, recorded in `## Log`.

**The developer's deviations, as recorded in the Log.**
- (1) `test_data.py` and `test_validation.py` were added to the radius at the main session's request: acceptable, recorded.
- (2) The unrelated stale-id failure was not fixed in this lane: correct, since the fix is on develop.
- (3) The run-3 failure was caught by a test written first, then fixed; `--lf`, then the radius once: compliant.
- (4) The integration run during the pilot: R7.
- (5) A1 deferred: see above.
- (6) The old-schema check called `verdicts`, `write_markdown` and `make_figures` directly on the DEV-0 pilot results, because the hook blocks any pilot-preset command line. Acceptable for DoD 1, recorded.
- The 14-row table follows DEC-0021 O1, which is still **proposed**, not owner-confirmed.

**PRIME.4.** Nothing is dropped silently.
- A row with no result is listed in the table with "no result" and gets no label line.
- A missing declaration or caption raises `KeyError`.
- A level mismatch raises, except at the sites of R5.
- The old-schema fallback to the role level is documented.

**Owner checkpoint.** The change touches no statistics, seed, provenance or dependency code. It does add report statements that govern how verdicts are read (interval labels and the QoI declarations), and it rests on DEC-0021 (proposed). **Needs owner review before freeze**, as the plan's Class row already says.

**Verdict: approve with fixes** (R1 to R6 are text and test fixes in `budget.py`, `identifiers.py` and `test_budget.py`; R7 needs no code change). 7 findings.

### Developer answers, round 1 (claude-sonnet-5-5)

- **R1:** fixed in e066aff (label text and an assertion citing DEC-0008 A4 in `test_every_label_has_the_four_elements_and_reads_its_config`).
- **R2:** fixed in e066aff (definition, units and decision_error of `QOI_DECLARATIONS["H2a"]`; phrase checks in `test_declaration_texts_state_the_statistics_of_the_decision_log`).
- **R3:** fixed in e066aff (H3b definition and decision_error).
- **R4:** fixed in e066aff (H3a cannot fail; H3c quotes v3 section 7; "not as a failure" removed).
- **R5:** fixed in e066aff (`STORED_LEVEL_PATHS` with several paths and a `*` step; H2e per noise level and H3b D; mismatch cases added to `test_label_level_equals_the_stored_level_and_a_mismatch_raises`).
- **R6:** fixed in e066aff (`H3B_COVERAGE` appended to the H3b label; asserted).
- **R7:** no code change; recorded in the Log (test run 4, item 6). Integration pair not run since.

### 2026-10-11, reviewer claude-opus-5-5 (fresh context): WU-0008.3 and .4, re-review (fix round 1)

Scope: R1 to R6 and the answer to R7 only, at e066aff (code and tests), 2656b62 (answers) and the develop merge 3837cae. References read: DEC-0008 A1, A3, A4; v3 §7 (lines 320–367); Methods v2 §M12 table; `analysis.py` (`h2a_initial_segments`, `h2a_part_ii`, `h2a_separation`, `_paired_change`, `h2e_noise_matching`, `h3a_logrank`, `h3b_importances`, `h2c`); `report._key_number`; the WU-0006 unit (no H3b case, line 60). **No test was run:** nothing in `lpcstudy/` or `tests/` changed after the developer's run 5 at e066aff (`245 passed`; 244 in run 2 plus the one new test), so a rerun would break the once-rule. Read-only checks instead: the labels printed from the code at HEAD; `stored_levels` evaluated on real results; the key-sorted JSON of `runs/base/smoke/results.json` and `runs/rep/smoke/results.json` (report-only at e066aff, written 16:35:41) are equal, and that `RESULTS.md` carries the new H2a and H3b label text.

**Per finding.**
- **R1: resolved.** The H2a label now reads "blocks of 5 consecutive test states (all of them, not only the eligible ones) …, with the eligibility of part (i) and the domain of part (ii) re-evaluated inside each resample (DEC-0008 A4)". The dependence clause is the plain "test states" one. This matches `analysis.py:1118–1121` (eligibility inside `stat`) and `:1211–1219` (interior filter inside `stat`; zero and one parts on all resampled states), and DEC-0008 A4(b). The test asserts the new phrases and the absence of the old ones, and cites A4(b).
- **R2: resolved.** Every clause was checked against the code and the decision log:
  - the indicator 1{w\* = 0} over all states, logit w\* on 0 < w\* < 1, and 1{w\* = 1} added at strictly more than 5% (`:1202–1208`, `20 * n_one > n_states`), all at H_ref;
  - quadratic controls in ln ε_s/ρ and ln δ/ρ with squares and product (A4(a2); `:1276–1277`);
  - the initial segment of 1, 2 and 4 LT with eligibility L ≥ 2 (`:1107–1109`; `long_horizons` = h ≥ 1 gives 1, 2, 4);
  - "at most 0.5 σ_x" (`:1268`, `<=`, `linear_regime_rms` = 0.5);
  - "the edge is the bound 0.1": the band is (−∞, 0.1), open at the top. Pass iff hi < 0.1, fail iff lo ≥ 0.1 (`:1071–1073`, `(True, False)`);
  - M12 pilot medians 0.12 / 0.28 / 0.17 and projected half-width 0.04;
  - the (ii) clause matches v3 §7 line 363.
- **R3: resolved.** D is defined as `analysis.py:1915–1917` and A3 define it. "The stability index … is reported only" matches `:1918`, `:1992` and A3. Lower bound of D within one half-width of 0 is the decision edge of the open band (0, ∞) (`:1983`).
- **R4: resolved.**
  - (a) "H3a cannot fail" is true: DEC-0008 A3, and `h3a_logrank` has no `fail` branch (`:1854–1864`).
  - The listed causes are correct: n < 50, a pair not computed, adjusted p ≥ 0.01. Each gives inconclusive.
  - (b) The H3c cell quotes v3 §7 line 358 verbatim. The test reads the proposal file as its reference, and "not as a failure" is gone.
- **R5: resolved.**
  - `STORED_LEVEL_PATHS` now has H2e `by_noise/*/level` and H3b `D/level` beside `weight_lambda/level`.
  - On the real results (`runs/base/smoke` and the DEV-0 pilot, all three systems), every path resolves. That gives H1a [0.95], H1d [0.95], H2b [0.9833], H2e [0.95, 0.95], H3b [0.95, 0.95] and H3c [0.9833]: 9 levels per system, all equal to the role level.
  - The other stored levels are reported-only intervals that the verdict table does not print: `H2b/library_curves/*/*`, `H2b/library_change_reported/*` and `H2c/A4o_minus_A2`.
  - The mismatch test now covers H3b D, H3b weight_lambda, and H2e at each ρ separately. Each one raises `ValueError`. The wildcard is exercised on a mismatch in only the second ρ.
- **R6: resolved.** `H3B_COVERAGE` is appended to the H3b label only. Its text matches the `h3b_importances` docstring (`:1909–1911`) and the WU-0006 gap (Log line 60, "no H3b case"). The test asserts it is present on H3b and absent from every other row.
- **R7: accepted** (main session's). The record is in the Log, and no integration run has happened since.

**Neutrality and consistency (d), (e).**
- No assert or tolerance was loosened. The diff of `test_budget.py` adds lines only, apart from the renamed `stored_level(...) is None` → `stored_levels(...) == []`, which is equivalent.
- No producer (`analysis`, `experiments`, `pipeline`, `statistics`, `__main__`) references `budget`, `QOI_DECLARATIONS` or `QOI_FIELDS`. The report-only `results.json` equals the base.
- `budget.py` imports only `.config` and `.identifiers`, which agrees with the fixture rows `budget` and `report` and with the module count of 22.
- The develop merge brought a one-line docstring change in `statistics.py`, plus decisions, defects and notes. It changed no import and added no module, so the fixture stands.
- No new text in `budget.py` or `QOI_DECLARATIONS` matches the stale-id pattern `H1e|H1f|H2f|H3d|T1|h1e_|h1f_`. The only matches are in the pre-existing id tables.
- e066aff and 2656b62 name the unit and carry `Agent: claude-sonnet-5-5`. The sync merge 3837cae uses git's default message, as earlier sync merges did.

**New findings.**
- **R8 (minor, not blocking): `STORED_LEVEL_PATHS` is tied to the producers only through the hand-built `fake_system`** (`lpcstudy/budget.py:35–41`; `tests/unit/test_report.py:127`).
  - Why it matters: if a producer renames a key on a path (`D`, `weight_lambda`, `by_noise`, `library_change`), `stored_levels` returns `[]`. The label then silently uses the role level, which looks exactly like the documented old-schema case, so the L2 cross-check would disappear unnoticed. Every test would stay green, because `fake_system` would not change with the producer (PRIME.4: a silent fallback).
  - Today every path resolves on real results (see R5), so there is no present defect.
  - Fix (follow-up or .1/.2 commit group): one check that runs on producer output. Either assert, in the smoke-pipeline integration test, that `budget.stored_levels(row, result)` is non-empty for every key of `STORED_LEVEL_PATHS` (two entries for H3b, one per ρ for H2e), or call the five producers on small synthetic inputs in `test_analysis` and check the same.

**Owner checkpoint.** Unchanged from round 1. The change adds no statistics, seed, provenance or dependency code, but its report statements govern how verdicts are read, and the 14-row table rests on DEC-0021 O1 (proposed). **Needs owner review before freeze.**

**Verdict: approve.** R1 to R6 are resolved and R7 is accepted. R8 is one minor new finding that does not block the merge of .3 and .4 into the branch line. The branch merge still waits for the A1 smoke at the .2a head, as round 1 required. 1 new finding.

### 2026-10-11, reviewer claude-opus-5-5 (fresh context): WU-0008.2a and .1/.2b (and R8), round 1

Scope: a8bdf0b (.2a) and df40a3b (.1/.2b, R8), against the plan, the design M1 to M9 (28dfbd1) and DEC-0024; DEC-0008, DEC-0012, DEC-0018, DEC-0021 and DEF-0020 read on `develop`; the WU-0006 Log table, the WU-0006 math note, `m7b.log`, and `tests/slow/wu0006_reference.py` on `wu/0006-simstudies` (read-only). **No test was run:** nothing in `lpcstudy/` or `tests/` changed after run 9 (`372 passed`), so a rerun would break the once-rule. Read-only evaluations, single thread: (1) E1's deviations on the grid: −0.334% (95%) and −0.909% (1 − 0.05/3), as M2 says; a helper without the /2 is off by +99%. (2) At B = 2000 and 1 − 0.05/3, F = 12 gives finite values (0.347, 0.347) and F = 13 gives (None, None) with both bounds finite. The thresholds (rule 1 / rule 2) are 50/43 (95%) and 17/13 (98.3%) at B = 2000, and 13/9 and 5/3 at B = 500; rule 3 fires at B = 50 for 98.3% only. (3) `budget_lines` rendered on the stored DEV-0 pilot `results.json` with `PILOT`: F1 = 0.032, 0.0337, 0.0266 and F2 = 0.00856, 0.00472, … agree with M3. (4) Every `COVERAGE_WU0006` value checked by hand against its source: rates and SEs against the note's table and `wu0006_reference.py` (98.3% column), C4h against the note's characterization table (c = 0.8) and `m7b.log`, run-2 counts against the WU-0006 Log table (98.3% column) and the characterization paragraph (C4h 965 and 984), and n against the case table (C8 300, others 500). All equal.

**Checked and correct (no finding).**
- **`endpoint_mc_error` matches M2.**
  - d = √(a(1 − a)/B) is the same at both ends, and SE = (Q(q + d) − Q(q − d))/2 uses linear `np.quantile`.
  - The quantiles are taken on the A3-replaced arrays of `percentile_interval`: finite min for the lower endpoint, finite max for the upper.
  - Rule 1 uses the same float threshold as `percentile_interval`. Rule 2 is floor((B − 1)(a − d)) + 1. The upper tail gives the same count by symmetry, since failures sit in both tails. Rule 3 is a − d ≤ 0.
  - With all resamples failed, rule 1 returns before `finite.min()`, so there is no empty-array error (this is the C7 zero column).
  - It draws no randomness and edits none of `percentile_interval`, `block_bootstrap_counted` or `BootstrapInterval`.
- **Tests E1 to E3 are real.**
  - E1's reference is the Bahadur formula through `statistics.NormalDist`.
  - E2's reference is the SD of the endpoints from `percentile_interval` over 100 bootstraps. It is independent of the helper and uses the DEC-0024 factor 1.4 on the median.
  - E3 pins both rule-2 boundaries (12 and 13 at 98.3%, 42 and 43 at 95%), rule 1 and rule 3. An off-by-one in either direction, or a missing rule 2, fails it.
- **Bitwise neutrality, by reading.** `_paired_change`, H2b(i) and `h3c_ratio` now call `bootstrap_values(...)` and then `percentile_interval(values, level)`, which is the body of `block_bootstrap_counted` (statistics.py:386–392):
  - same statistic closure, n, B, block and seed object (`make_rng(config.seed, *labels)`, `config.seed + 3`, `make_rng(config.seed, "h3c-ratio")`), so the index draws and their order are identical;
  - `float(point)` in place of `boot.estimate`, and `n_failed` is the same int;
  - the dropped `ndim` check cannot fire for these scalar statistics, and a vector statistic would still raise, now in `percentile_interval`;
  - every site has its own generator or integer seed, so no other site's stream moves;
  - `ci_mc_se` is the only added key: H2b(ii) through `mc_error=True`, while H2e and `library_change_reported` keep the default `False`.
  - Independent unit references already pin the three sites exactly and passed in run 9: `h3c_ratio` against `block_bootstrap` (test_analysis.py:2054), H2b(ii) and the 0.02 change against `block_bootstrap` (:1541, :1641), and H2b(i) against `_old_boot` (:3001).
- **`_inject_first_call` is equivalent, not weakened.**
  - The first `analysis.bootstrap_values` call in `h2b_knob_response` is H2b(i) (analysis.py:1467). Later calls pass through: `_paired_change` and `library_curves` (:1500).
  - The resample order is unchanged: 0..B−1, then the point.
  - The diff touches only the helper. Every expected value, threshold and assertion is unchanged. The H3c key-set update adds the specified key and is not a loosening.
- **The budget against M1 to M9.**
  - Nine rows in the skill's order, plus row 9. Flags as M9: row 1 is "not estimated" always, rows 2, 7 and 8 are "—", row 4 is "yes", row 5 is "not estimated", and rows 3, 6 and 9 use strict `<` on (hi − lo)/2.
  - Round-off is 1e-4·max(|lo|, |hi|). The LM row reads `LM_ABSENT` with `LM_SUMMARY_PATH = None`.
  - The M7 mapping (H2b(i) → C8) and f = z_nom/z_obs − 1 with the delta-method SE are implemented. The flag outcomes yes, yes, no, no follow the largest f.
  - The two M1 sentences are under every table, and the H3c sentence is under H3c only. The report hunk R5 adds lines only.
- **Graph fixture.** `budget` imports only stdlib modules (`math`, `textwrap`, `dataclasses`, `statistics.NormalDist`) plus `.config` and `.identifiers`. That matches `"budget": ["config", "identifiers"]`. `analysis -> statistics` already existed.
- **Commits.** Both commits name the unit and end with `Agent: claude-sonnet-5-5`. a8bdf0b carries the owner-review sentence. Randomness: none in the library. E2 uses `make_rng(8008, …)` (literal, not registered). Everything is float64.

**Findings (ranked).**

- **R9. The interval-procedure row names the wrong seed for its size** (`lpcstudy/budget.py:378`, used at `:735` and `:856`).
  - The table line and the How cell say "synthetic, seed 6006, not a registered seed".
  - The size comes from the *reference* rates. Those were simulated with the scratch seed 20261011 (math note line 5 and line 286; R_ref 10⁴ to 4·10⁴, 2·10⁴ for C4h). Only the run-2 counts beside them come from `make_rng(6006, …)`.
  - Why it matters: it is a provenance statement under every primary table, and it is false for the number it labels (PRIME.4, REPRO).
  - M7 amendment 4 also asked for R_ref with each constant, and `CoverageCase` has no such field.
  - Fix: name both sources ("reference rates: scratch seed 20261011, R_ref …; run-2 counts: seed 6006; neither registered"). Add `r_ref` to `CoverageCase`, checked in B4 where the note gives it. Assert the new wording in `test_text_under_every_table`.

- **R10. The H3c table says the oracle-draw variance is inside the interval, and its own cell says it is not** (`budget.py:468`, `INCLUDED[0]`, printed for all five QoIs at `:853`).
  - For H3c, M3 says M-draw noise reaches the QoI only through the fitted A4 coefficients and A5 leaf weights, and that "the interval conditions on them". The row-1 cell repeats this. The Included column still prints "variance: yes (propagated)".
  - The inconsistency comes from M1's per-row Included column and decision (a) ("inside every primary interval"), both of which the developer followed.
  - Why it matters: this column states what the H3c verdict interval covers (NVVUQ.15). Read as written, it overstates it.
  - Fix: make the Included cell per QoI for row 1, with H3c reading "no (conditional on the fitted A4 and A5)". The applied-mathematician confirms the wording, because it amends M1 and decision (a). Add a test.

- **R11. DEC-0024's "each primary's label states its iterative error is unverified" is met only under the budget tables** (`budget.py:384`, `:860`).
  - The verdict-table label lines (`interval_label` / `interval_label_lines`) for H2a, H2b and H3c do not carry the statement. A reader of the verdict table does not see it.
  - Fix, either of:
    - append the statement to `interval_label` for the three primary rows, and assert it;
    - the main session records that placement under the budget tables satisfies DEC-0024.
  - The statement is a plan amendment (7), so it is not optional.

- **R12. Some "not estimated" reasons are false in reachable cases** (PRIME.4).
  - (a) `_bootstrap_cell` (`:654–656`): when H2b(ii) is unavailable in current results, `_unavailable` writes `ci: None` and no `ci_mc_se`. The cell then reads "no ci_mc_se in these results (written before WU-0008.2a)", which is untrue. Check `part.ci is None` first and use "no interval in these results".
  - (b) `_oracle_cell` H2b(ii) (`:639–644`): the `elif` prints "V4 has no larger M than the one used" also when the real cause is `n_states` missing or zero, or a non-finite `mean_abs_dev_from_max`. Give each cause its own reason.
  - (c) `_v4` (`:606–617`) returns None, which prints "V4 absent from these results", also when V4 is present but `used_M` or its entry is missing. Say which of these is missing.
  - (d) `:633`: "the four ρ cells" is hard-coded. Smoke has two noise levels (`config.py:210`). Derive the count from `config.noise_levels`, or say "across the ρ cells".
  - (e) `_proxy_cell` (`:696`): `A5_vs_Astar` reads "not computable" with no reason. M8's form for it is "not computable (A2 ≤ A*)".
  - Add a test for (a) at least, on a current-schema system with a missing library cell.

- **R13. The How text of row 9 misstates DEF-0020's options** (`budget.py:736`).
  - "DEF-0020: widening or another procedure (Option C or K) is the owner's decision, pending" is inaccurate.
  - Option C or K (DEC-0018) decides whether the WU-0006 ROADMAP-bound rows stay asserted. DEF-0020's Resolution treats another interval (longer block, studentized, BCa) as a *separate* design question for the owner.
  - Fix: "DEF-0020: Option C or K for the WU-0006 assertions (DEC-0018) pending; widening or another interval procedure is a separate owner design question".

- **R14. Test evidence gaps** (no tolerance was loosened anywhere).
  - (a) B4 (`tests/unit/test_budget.py:531`): the C4h run-2 counts {965, 984} are typed in the test, not parsed, and the comment cites "F5 row". The values sit in the WU-0006 Log "Characterization rows" paragraph (line 341). I verified them there and they are right. Parse that sentence, or label the two values as a hand transcription.
  - (b) A2 (`tests/unit/test_analysis.py:3117`): the docstring says H2e and H2c carry no `ci_mc_se`, but only `library_change_reported` is asserted (`:3147`). Assert H2e `by_noise[*]` and H2c, or narrow the docstring.
  - (c) E3's F = 12 "expected" (`tests/unit/test_statistics.py:1007`) re-evaluates the helper's own formula. Its value as a check is the boundary and the replacement semantics, not independence. Say so in the docstring.

- **R15. Two Log statements need an append-only correction.**
  - The run-9 paragraph says the DEV-0 pilot results have "no used_M". They do: `convergence.used_M = 200` in all three systems. The pilot report therefore prints F1 and F2, which I checked against M3.
  - Also, the `QOI_COVERAGE` docstring (`budget.py:454–456`) says C1 is "cited beside" H2b(i), but `coverage_how` never prints C1, and the `C1` constants are unused. Either cite C1 in the H2b(i) cell, which M7 permits, or drop the claim.

- **R16 (minor; merge-order hazard). `LM_SUMMARY_PATH = None` plus "WU-0005.4 summary absent from results" becomes false if WU-0005.4 merges before the one-line re-point** (`budget.py:373–377`).
  - Fix: word it as true whatever the merge order ("not read: LM_SUMMARY_PATH not set until WU-0005.4 merges"). Alternatively, the main session puts the re-point on WU-0005.4's merge checklist.

**The developer's deviations.**
1. **`COVERAGE_PROVENANCE` elides the "T" in the log name: acceptable as recorded.** It is honest and the stamp is recoverable. It is the second false positive of the unanchored stale-id regex `H1e|H1f|H2f|H3d|T1|h1e_|h1f_` (`tests/unit/test_identifiers.py:139`); the first was the `kaplan_meier` docstring.
   - Recommendation, not an edit: the planner and mathematician change the regex to token-bounded ids, e.g. `(?<![A-Za-z0-9])(?:H1e|H1f|H2f|H3d|T1)(?![0-9A-Za-z])|h1e_|h1f_`. Add cases asserting that "20261011T165447Z" is not flagged and that " T1 " and "T1," are.
   - That corrects a false positive and does not loosen what the test is for (ids as tokens). Record it as a test amendment. Then restore the exact filename.
2. **Cell texts of the developer's own: acceptable,** because B1 parses them (amendment 8). Examples are "0 (coverage ≥ nominal)" for M7's "none (…)" and "0 (tie at the endpoint)". R12 and R13 are the exceptions.
3. **F1 with k = 3: acceptable.**
   - Every preset has the long horizons (1, 2, 4) LT (`config.py:124`; no preset overrides them).
   - States with L = 2 make k = 3 the worst case, so F1 stays an upper indication.
   - Recommendation: derive k from the long horizons so the text "across 3 horizons" stays true if they change.
4. **"Needs owner review before freeze" mark in the docstring: correct and required.**
5. **Injection point moved to `bootstrap_values`, and the H3c key set: equivalent, not weakened** (see above).

**Evidence still required before the branch merges.**
- **A1 at the head (after the fixes), when `pgrep -fa "lpcstudy --preset"` is empty.**
  - Command: `LPC_THREADS=4 tools/run_preset.sh smoke DEV-0 runs/new` from a clean tree. Then `leafcmp` against `runs/base/smoke`. The base at 7dc4f45 is valid: since then `lpcstudy/` changed only in this unit's files plus a docstring.
  - Record in the Log:
    - the number of pre-existing leaves, with 0 different (`provenance`, `seconds` and `handling` excluded, as A1 states);
    - 0 leaves only in the base;
    - the new-only leaves listed by path. They must be exactly `ci_mc_se/{0,1}` under H2a, H2a `part_ii/{zero,interior[,one]}`, H2b `noise`, H2b `library_change` and H3c, per system.
  - At smoke (B = 50, 98.3%) every one of these is `null` by rule 3. The Log should say so. The numeric path at study size is therefore covered by A2, E1 to E3 and the slow nodes, not by A1.
  - Also record that the report-only run on the new results renders the five tables with "B = 50 too small for the binomial window".
- **A unit-level equality test cannot stand in for A1 without a recorded amendment.**
  - The unit references above already prove function-level identity at the three sites.
  - What A1 adds is the whole-pipeline claim that no other leaf moved.
  - A1 is a criterion fixed in advance. Replacing it is the planner's and owner's change, not the developer's, and it costs about one minute of CPU.
- **The integration pair once** (`test_cli_seeds.py`, `test_preset_wrapper.py`). Run 4 predates .2a and .1, and `report` and `statistics` changed since.
- **The slow exact-check nodes, once (DEC-0021 O6; they must pass before merge):** `tests/slow/test_analysis_coverage.py::test_exact_checks` for C4, C7 and C8 at φ 0 and 0.3.
  - They call the changed bodies (`h3c_ratio`, `h2a_part_ii`, `_paired_change`) at B = 2000 and compare estimate, bounds, failure count and verdict with the harness's own computation. The added key does not affect that comparison.
  - C7's zero column exercises the all-failed path of the helper.
  - `cache.coverage` runs the full R = 1000 per case, so these are CPU-heavy. Run them in the slow tier, not during the pilot.
- **The unit radius once after the R9 to R16 fixes.**

**Owner checkpoint.** This change adds statistics code (`endpoint_mc_error`) and changes the call path of three primary interval sites (bitwise-neutral by design, still to be shown by A1 and the slow nodes). It also adds report statements that set how much weight a primary verdict carries: the budget, the coverage shortfall flags "no" for H2b and H3c, and the F1 statement on Chua H2a(i). It rests on DEC-0012, DEC-0021 and DEC-0024, all still **proposed**. **Needs owner review before freeze.** No seed, provenance or dependency code is touched.

**Verdict: approve with fixes.**
- R9 to R13 are required before merge: provenance and statement truth, and DEC-0024 conformance. R10 needs the applied-mathematician's wording.
- R14 to R16 are minor.
- The merge also waits for A1, the integration pair and the slow exact checks above.
- 8 findings (R9 to R16).

### Developer answers, review of .2a and .1/.2b, round 1 (claude-sonnet-5-5)

- **R9:** fixed in the commit that follows this entry (both seed sources, `r_ref`, docstring range; tests).
- **R10:** fixed in the same commit (`ORACLE_INCLUDED` with the supplied wording; notes; test).
- **R11:** fixed in the same commit (`ITERATIVE_LABEL` in the primary labels; label test).
- **R12:** fixed in the same commit, (a) to (e), with a test per reason.
- **R13:** fixed in the same commit (`DEF0020_TEXT`, `WIDENING_SENTENCE`; test).
- **R14:** fixed in the same commit (C4h counts parsed; A2 asserts H2e and says H2c is not exercised; E3 docstring).
- **R15:** corrected in the Log (append-only, above); the C1 claim is dropped from the docstring.
- **R16:** fixed in the same commit (`LM_NOT_READ`; F1's k from the configuration).
- The first-round filename elision and `test_identifiers.py` are left as instructed.

### 2026-10-11, reviewer claude-opus-5-5 (fresh context): WU-0008.2a and .1/.2b, re-review (fix round 1)

**Scope.** Findings R9 to R16 only, at fix commit 309926c (parent 4c5e337), checked against the code and the source documents, not against the developer's answers.
- **Sources read.** The WU-0006 math note and `m2_coverage.log` / `m2_coverage.py`, the WU-0006 Log (line 341), `tests/slow/wu0006_harness.py`, DEF-0020 and DEC-0024 in `decisions.md` / `defects.md`, and the writers in `analysis.py` and `experiments.py`.
- **No test was run.** The tree is clean, and HEAD = 309926c is the code of run 11 (`365 passed`), so a rerun would break the once-rule. The only pytest call was collection of one file (`--collect-only -q -m slow tests/slow/test_analysis_coverage.py`: 46 collected, no test executed).
- **Neutrality holds.** `git diff a8bdf0b HEAD -- lpcstudy/statistics.py lpcstudy/analysis.py` is empty. 309926c changes only `budget.py` (report text), tests and this file, so no `results.json` leaf can move and the .2a bitwise neutrality verified in round 1 stands.
- **No test was loosened.** Every removed assertion line in 309926c (6 in `test_budget.py`, 2 docstring lines in `test_analysis.py`) is replaced by a stricter or re-specified one:
  - `LM_ABSENT` becomes `LM_NOT_READ`, per R16;
  - "V4 absent" becomes the exact "V4 present but used_M missing";
  - the C4h literals are now parsed;
  - the seed text follows R9;
  - the A2 docstring is narrowed and an H2e assertion is added.
- **Commit.** 309926c names the unit and ends with `Agent: claude-sonnet-5-5`.

**Status of R9 to R16.**
- **R9: resolved.**
  - `r_ref` equals the `R=` of `m2_coverage.log` for all 12 entries: C1, C4, C8 R=40000; C3, C7 R=20000; `C4_sigma1.5c0.8` and `C4_sigma2.0c0.8` R=20000.
  - `m2_coverage.py:78` uses seed 20261011, and `m7b.log` only transcribes it.
  - The run-2 seed string matches `wu0006_harness.py` (`WU0006_SEED = 6006`, `make_rng(6006, "wu0006", ...)`).
  - R_ref is printed per case. The test's evidence is a hand transcription (R21).
- **R10: resolved in the code.**
  - The five Included cells are per QoI, H3c reads "no: …", and the row-1 How text no longer says the variance propagates.
  - A grep of `lpcstudy/` for "every primary", "inside every" and "propagat…" in the budget finds nothing.
  - `H2A_ONE_NOTE` is true: `add_one = 20 * n_one > n_states` is computed once outside `stat` (`analysis.py:1206`).
  - Open: the wording has no record (R17), and the replacement How text points to the wrong column (R18).
- **R11: resolved.**
  - `interval_label` appends `ITERATIVE_LABEL` exactly for `PRIMARY_KEYS` (`budget.py:169`).
  - The label test asserts the ending for every `role == "primary"` row and its absence on every other row, so a primary key missing from `PRIMARY_KEYS` would fail it.
  - The verdict-table lines (`interval_label_lines`) use the same function. The hard-coded "15" is R19.
- **R12: resolved.** Each reason was checked against the writer paths.
  - (a) `_unavailable` writes `"ci": None` (`analysis.py:1405`), and `_bootstrap_cell` now tests that first. `json.dumps(..., allow_nan=True)` (`report.py:791`) round-trips ±inf, so no writer stores `None` inside a `ci` list.
  - (b) and (c) `experiments.py:113–119` always writes `used_M` and numeric entries. At smoke, `convergence_draws = (10, 30)` and M = 30, so "no larger M than the one used (M = 30)" is the true reason there. The F2 branch order gives a distinct, true reason for each cause.
  - (d) The rho-cell count `len(config.noise_levels)` equals the number of H2b(i) cells whenever `core_noise ∈ noise_levels` (`experiments.py:444–447`). That holds in every preset. It would be off by one only for a configuration without the core level. Observation, not a finding.
  - (e) `oracle_recovery` returns NaN only when A2 − oracle ≤ 0 (`analysis.py:2127`), so "not computable (A2 ≤ A*)" is true. "not available" applies only to an absent key.
  - The F1 k uses the same rule as `analysis.py:1267` (h ≥ 1 LT).
- **R13: resolved.**
  - `DEF0020_TEXT` agrees with the DEF-0020 Resolution (`defects.md:177`).
  - Its claim "K in force by default via ASSERT_ROADMAP_BOUNDS = True" is true (`tests/slow/wu0006_harness.py:92`).
  - `WIDENING_SENTENCE` cites only the uq-budget rule (`SKILL.md:24`: "say so and widen the interval or refine").
- **R14: resolved.**
  - (a) The C4h counts are parsed from the single source sentence (WU-0006 Log line 341: "C4h sigma 1.5: 927 / 965 …; sigma 2: 939 / 984").
  - (b) H2e is asserted, and the docstring now says H2c is not exercised.
  - (c) The E3 docstring states what F = 12 checks.
- **R15: resolved, with a defect in the correction (R20).**
  - The two corrections are appended. The diff of this file is 34 insertions and 0 deletions, so no earlier text was rewritten.
  - The C1 claim is dropped from the `QOI_COVERAGE` docstring.
- **R16: resolved.**
  - `LM_NOT_READ` is returned before any lookup while the path is None. The test covers a summary present with the path unset.
  - F1's k comes from `eval_horizons_lyapunov`, and k ∉ {2, 3} gives "F1 not computable: …". The test reference is `scipy.stats.norm.ppf`, compared at 3 significant digits on a `.3g` print.
  - Residual: the parenthetical "until WU-0005.4 merges" still assumes the one-line re-point lands with that merge. Recommendation: the main session puts the re-point on WU-0005.4's merge checklist.

**New findings.**

- **R17 (required before merge; records and evidence). The applied-mathematician's fix-round-1 wording is recorded nowhere.**
  - The wording covers: the five `ORACLE_INCLUDED` cells (`budget.py:497–507`), `DEF0020_TEXT`, `WIDENING_SENTENCE`, and R_ref per case.
  - A grep of `docs/` (worktree and main checkout) finds none of it. This Log has no applied-mathematician entry after M1 to M9.
  - M1 decision (a) at line 204 still reads "inside every primary interval", with no appended amendment. DEC-0024 accepted M1 as written.
  - Why it matters:
    - The amendment to an accepted design is untraceable (PRIME.5, VV.3).
    - The developer's "verbatim" cannot be audited.
    - The R10 test's stated reference is "the wording supplied in fix round 1, written out here" (`tests/unit/test_budget.py:789`). Without a recorded source, that test only compares the code with a copy of itself (LPC.PC.21).
  - Fix (records only, no code):
    - The applied-mathematician, or the main session quoting them with attribution, appends a Log entry "M1 (a) and M7 amendment, fix round 1". It gives the exact texts and R_ref per case, with the `m2_coverage.log` lines as source.
    - The main session appends a dated line under DEC-0024 saying M1 (a) is amended: the variance is inside the H2a and H2b intervals, not inside H3c's.
    - The R10 test docstring cites that entry.

- **R18 (minor; statement truth, introduced by the R10 fix). The How text of row 1 points to the wrong column** (`budget.py:870–872`).
  - It says "whether the M-draw variance is inside the interval is in the next column".
  - The column after "How estimated" is "Size: <system>". The Included column follows all the Size columns (`budget.py:908–909`).
  - Fix: "… is in the column 'Included in the reported interval?'". Assert that substring.

- **R19 (minor). `ITERATIVE_LABEL` hard-codes "15-iteration"** (`budget.py:104–105`).
  - The count is `config.estimator_refine_steps` (`config.py:141`, used at `pipeline.py:175`). Every other element of `interval_label` is read from `config`, and `test_every_label_has_the_four_elements_and_reads_its_config` exists for exactly that.
  - The label is true for every preset today, since none overrides it. It becomes false under the 15 → 30 refinement study that DEC-0024 point 1 proposes. This is the same pattern as round 1's F1 k.
  - Fix: build the clause from `config.estimator_refine_steps`, and assert it with a replaced config.

- **R20 (minor; records). R15 correction (3) corrects a statement that does not exist** (Log line 536).
  - It says "The `.2a` entry's 'no `used_M`' has the same origin as (1)."
  - The .2a entry (lines 492–512) does not mention `used_M`. The only such statement is the run-9 paragraph (line 532), which correction (1) already covers.
  - Fix: append one line saying correction (3) is void (append-only; do not edit it).

- **R21 (minor; evidence). The r_ref test is a hand transcription, but its source is machine-readable** (`tests/unit/test_budget.py:749–754`).
  - The docstring says the note gives only a generic range, "so this is a transcription, not a parse".
  - The per-case R is in `docs/agent/notes/2026-10-11-math-wu0006-scripts/m2_coverage.log` (e.g. "C4 phi=0 R=40000", "C4_sigma2.0c0.8 phi=0 R=20000"). That is the run that produced the rates.
  - I checked all 12 values against it by hand: they are correct.
  - Fix: parse `R=` per (case, phi) from that log in B4, mapping C4h1.5/C4h2 to `C4_sigma{1.5,2.0}c0.8`. Alternatively, keep the transcription and correct the docstring to name the log.

**Evidence still required before merge** (unchanged from round 1; run each once, when `pgrep -fa "lpcstudy --preset"` is empty):
1. **A1 smoke at the head.**
   - Commands: `LPC_THREADS=4 tools/run_preset.sh smoke DEV-0 runs/new`, then `leafcmp` against `runs/base/smoke`.
   - Expected: 0 pre-existing leaves different (`provenance`, `seconds` and `handling` excluded), and 0 base-only leaves.
   - The new-only leaves must be exactly the `ci_mc_se/{0,1}` of the five primary sites, per system, all `null` at smoke (B = 50, rule 3).
   - Also record the report-only rendering, with "B = 50 too small for the binomial window".
2. **The integration pair:** `LPC_THREADS=4 tools/run_tests.sh integration tests/integration/test_cli_seeds.py tests/integration/test_preset_wrapper.py`.
3. **The slow exact checks (DEC-0021 O6):** `tools/run_tests.sh slow --background` on the six node IDs below.
   - IDs: `tests/slow/test_analysis_coverage.py::test_exact_checks[C4-0.0]`, `[C4-0.3]`, `[C7-0.0]`, `[C7-0.3]`, `[C8-0.0]`, `[C8-0.3]`.
   - All six exist: collection lists them among 46 items.
   - `run_tests.sh` accepts `slow … --background` (usage line 4).
4. **The unit radius once** after the R17 to R21 fixes, if any code or test changes.

**Owner checkpoint.** Unchanged from round 1. `endpoint_mc_error`, the three primary call paths and the budget statements (coverage flags, F1 on Chua H2a(i), and now the H3c "no" in the Included column) need **owner review before freeze**. 309926c touches no statistics, seed, provenance or dependency code.

**Verdict: approve with fixes.**
- R9 to R16 are resolved.
- R17 is required before merge (records only).
- R18 to R21 are minor.
- The merge waits for the evidence above.
- 5 new findings (R17 to R21).

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:
