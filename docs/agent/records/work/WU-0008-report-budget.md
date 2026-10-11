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

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:
