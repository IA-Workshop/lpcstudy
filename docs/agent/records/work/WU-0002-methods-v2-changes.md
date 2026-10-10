# WU-0002: Code changes for Methods v2 §M15 and v3 identifiers

| Field | Value |
| --- | --- |
| Status | planned (MAY be split into smaller units) |
| Class | CSQ3 development |
| Agent(s) | — |

## Plan

**Scope.** Bring the code in line with the v3 design: the proposal and methods v3 doc, Methods v2 §M15, and the identifier map in `docs/study/decision_log_lpc.md`. Items:

1. **Library size.** Rename it to `n_lib` in configuration, labels and reports.
2. **Excess MSE and regime weights.**
   - Excess MSE is computed exactly as V(w) − V(w*) from the moments (Theorem P1), replacing c(w − w*)² with clipped w*.
   - The regime weight is clip(Σcᵢuᵢ / Σcᵢ) with unclipped uᵢ (Theorem P3a).
   - K selection: the smallest K in {2, 3, 4, 5, 6, 8} within 5% of the minimum calibration excess.
3. **Mechanism hypotheses.**
   - H1a (v2 H1b) fits the median ε_s² instead of the mean.
   - H1b (v2 H1c) gets a PLP-only verdict; the CP slope is reported.
   - H1d (v2 H1e) gets bootstrap intervals for the Spearman correlations; N̂ is reported, not tested.
4. **Q-N estimate.** Oracle-primary, with the four-way reading table; the deployable estimate is secondary.
5. **H2b and H2e.**
   - H2b(ii) becomes the mean paired change in w* from N_lib = 10³ to 10⁴ at ρ = 1%, at level 1 − 0.05/3; mean and median curves are reported with intervals.
   - H2e (v2 H2f) is the median per-state change in CP–PLP error correlation from 10³ to 10⁵ at ρ = 1% and 2%. The correlation is set to 0 where CP's error does not vary.
6. **Regime and allocator hypotheses.**
   - H3a: log-rank test only, with the IQR reported.
   - Remove v2 H3b.
   - H3c (v2 H3d): block-bootstrap interval on MSE_A5/MSE_A4, at level 1 − 0.05/3.
   - H2d: remove part (ii) and the shift experiment.
7. **Verdict logic** (v3 §7):
   - per system: pass, fail or inconclusive;
   - multi-part criteria pass only if every part passes, and fail if any part fails;
   - overall: supported, not supported or inconclusive;
   - remove "partially supported".
8. **Removals.** Remove A4f, Lorenz-96, transfer, the τ_d-halved variant and the shift cells.
9. **Validation and presets.**
   - Add V7 (estimator efficiency) to the validation gate.
   - Full preset: 1000 sweep states.
10. **Hypothesis identifiers.** Switch to the v3 identifiers everywhere: code, report, figure labels.
11. **DEF-0001.** Count and report every replacement, clip and fallback.

**Definition of done.** Every item is implemented with tests; the smoke and pilot presets run on DEV-0; the regression comparison passes; reviewed.

**Acceptance criteria** (fixed now):

- **Item 2.**
  - Exact excess MSE agrees with brute-force minimization of V(w) on a 10⁴-point grid of w, within 10⁻⁶ relative, on random moment triples, including clipped cases.
  - The regime weight agrees with a brute-force minimizer of Σ Vᵢ(w) within 10⁻⁶.
- **Items 3–6.**
  - Each statistic is tested against an independent computation on synthetic data with a known answer: for example, a Spearman interval against `scipy.stats.spearmanr` on data with known correlation, and a paired change against a hand calculation.
  - Verdict logic is tested on synthetic intervals covering every branch.
- **Regression on DEV-0 (CPU).** The pilot preset reproduces the v1 pilot values of every quantity this unit does not intend to change (oracle moments, w*, proxies, fitted coefficients) bit for bit, or within 10⁻¹² relative where the summation order changed. Every changed statistic is listed with its old and new value and the reason.
- **Tests.** The full test suite passes.

**Affected checks.** All tests; the smoke preset; the pilot preset on DEV-0 (about 1 hour on CPU, faster on GPU).

**Owner checkpoint.** The owner reviews the code that computes verdicts and statistics before the freeze (LPC.PC.11).

### Plan amendment, 2026-10-10, planner (claude-opus-5-5): WU-0002.1 and WU-0002.2 only

The plan above is kept as written. This amendment details sub-tasks .1 and .2, the only ones that depend on no owner ruling. WU-0002.3 to .13 are planned later, against the owner's rulings on the WU-0014 referral and `docs/agent/notes/2026-10-10-rulings-for-owner.md`. Branch `wu/0002-removals-ids`, from `develop` 295d5cd. Both sub-tasks **remove or rename only**. They redefine no statistic, band, level or verdict rule. For the statistics under referral (H1a, H2a, H2c, H3a, H3b, Q-N), only the key, the function name and the label text change.

**ROADMAP rows (verbatim; fixed):**

| WU-0002.1 | Removals: A4f, Lorenz-96, transfer (`run_transfer*`, `transfer_*` config fields, `--skip-transfer`), the τ_d-halved variant, the shift cells and `shift_gaps`, T1 | developer | WU-0010.2 | CSQ3 | §M15 item 9; v3 drops E5 (shift); D3; LPC.PC.1 | `test_config`, `test_allocation`, `test_analysis`, `test_report`; smoke | M |
| WU-0002.2 | One identifier table (v3 ids, roles primary/secondary/estimate/reported, criterion text) used by analysis, report and figures; rename library size to `n_lib` in config labels and report text | developer | WU-0002.1 | CSQ3 | §M15 items 1 and 10; decision-log map; DEF-0005 | `test_report`, `test_analysis`, `test_config`; smoke | M |

| WU-0002.1 | No Lorenz-96, transfer, A4f, τ_d-halved or shift code path remains; smoke runs | `grep -rn "lorenz96\|transfer\|A4f\|shift" lpcstudy/` returns only comments explaining the removal, or nothing; `StudyConfig` has no `transfer_*` fields; `tests/unit` pass; smoke passes the gate on DEV-0. Removed tests are listed in the log with the reason (none of the 14 v1 tests exercises removed code, so none should go). |
| WU-0002.2 | Every hypothesis key in `results.json`, `RESULTS.md` and figure labels is a v3 id | Unit: the identifier table has exactly the rows of the decision-log map (14 rows) and each v2 id maps to the v3 id of that table; `grep -rn "H1f\|H3d" lpcstudy/` finds no live code symbol (v2 `H3d` becomes v3 `H3c`; v2 `H1f` becomes `Q-N`); the docstrings of `config.py` and `data.py` that call the library size ``N``, the `N=` log and result labels in `pipeline.py`, `experiments.py` and `report.py`, and every figure axis for library size read `n_lib`. |

(Referral item 2 of WU-0014 notes that "v3 drops E5 (shift)" should read "v2 E5 (shift)". The wording is not changed here.)

#### WU-0002.1: removals (M)

**Scope.**
- **In:** remove code that is not in v3: A4f (M2 §M14; v3 §5), Lorenz-96 and T1 (DL D3), the transfer stage, the τ_d/2 robustness variant (§M15 item 9; v3 §6 E6 lists D, k and ±5/10% only), and the shift experiment (v2 E5; DL, 10 Oct later).
- **In:** remove H2d part (ii), because it consumes only the shift cells. The DL says "H2d, part (ii) dropped", and §M15 item 7 agrees. ROADMAP places this in .8; .1 must do it or the shift path stays.
- **Out:** H2d's verdict basis (point estimate against interval; D-14 → .9). `gain_proxy` in `EvaluationDraws`, which is unused after A4f goes; it lives in the core module `ensemble` (see the note for the owner). Experiment-id relabels. Anything in .3 to .11.

**Removals, file by file** (grep at 295d5cd):

| File:line | Item | Action |
| --- | --- | --- |
| `systems.py:104-121`, `:170-174` | `lorenz96_field`, `SYSTEMS["lorenz96"]` | delete |
| `config.py:23-26`, `:117-118`, `:214-215` | `transfer_targets`, `transfer_sources` (docstring, fields, SMOKE `replace` arguments) | delete |
| `experiments.py:7`, `:126-127`, `:219-259` | `run_transfer_target`, `run_transfer`, and the docstring lines naming transfer | delete; the docstrings say "robustness" |
| `__main__.py:16`, `:40`, `:136-141` | transfer imports, `--skip-transfer`, transfer block | delete. `--skip-transfer` then falls into `choose_seed`'s unrecognized-option refusal (exit 64) |
| `report.py:88-92`, `:226-231` | T1 verdict branch and T1 Markdown section | delete |
| `tools/run_preset.sh:5`, `:131`, `:157` | `--skip-transfer` pass-through and usage text | delete; the wrapper then refuses the flag ("unexpected argument", exit 64) |
| `allocation.py:30`, `:192-219` | `RULE_LABELS["A4f"]`, `full_form_weight` | delete |
| `pipeline.py:23`, `:96-97`, `:335-336`, `:373`, `:389-390`, `:412-413`; `experiments.py:107-108` | A4f import and entry; `FittedRules.n_analogs` and `.state_dim`, and the `state_dim` parameter of `rule_weights` (used only by A4f; the developer greps to confirm) | delete |
| `experiments.py:326`; `pipeline.py:133-140`, `:212`, `:233-234`, `:247`; `data.py:198`, `:212-213`, `:239` | `"delay/2"` variant; the `delay_scale` plumbing | delete. `int(round(min(..) * 1.0))` equals `int(round(min(..)))` for integer `min`, so `delay` is unchanged |
| `experiments.py:172`, `:177`, `:179`, `:188-196`; `analysis.py:565-595` | `shift_scores`, `extreme_sizes`, `with_evals=shifted`, `core_sub_scores`, `res["shift"]`, `shift_gaps` | delete. Noise and library sweep cells run with `with_evals=False` unless the grep finds another consumer of their `evals` |
| `analysis.py:493-520`; `experiments.py:208`; `report.py:39-40`, `:139-140` | H2d `shift` argument, `shift_*` keys, `pass = in_dist_ok and shift_ok` | `pass = in_dist_ok` (point value as today); drop part (ii) from the text and the key number |
| `README.md:14`, `:34`, `:43`, `:51`, `:54` | mentions | edit text (no tests) |
| `tests/unit/test___main__.py:209`; `tests/unit/test_tools_run_preset.py:245-252` | `--skip-transfer` in argv | drop it from argv. The assertions are unchanged; this is not a loosening |

**Tests (new; all exact, discrete, no tolerance):**
- `test_config.py::test_config_has_no_transfer_fields`: no field of `dataclasses.fields(StudyConfig)` starts with `transfer`. Reference: DL D3 and the .1 acceptance.
- `test_systems.py` (new file; core module `systems`): `set(SYSTEMS) == {"lorenz63", "rossler", "chua"}`. Reference: DL D3 and v3 §4.
- `test_allocation.py`: `set(RULE_LABELS) == {A0, A1, A2, A3, A4, A5, A4o, A*}`. Reference: v3 §5 and concordance 1c.
- `test___main__.py`: `main([... "--skip-transfer"])` returns 64 with one stderr line. Reference: the refusal contract of `choose_seed`.
- `test_tools_run_preset.py`: the wrapper refuses `--skip-transfer` with exit 64 and starts nothing. Reference: the wrapper's refusal contract.
- `inspect.signature` of `build_context`, `Study.context` and `Study.run_cell` has no `delay_scale`. In `test_data.py`, or in a pipeline check placed in `test_analysis.py` if the developer prefers; record which.

**Acceptance additions** (fixed now; these strengthen the row and replace nothing):
- **(a) Smoke regression.** CPU smoke on DEV-0 (`python -m lpcstudy --preset smoke --seed-id DEV-0 --out <wt>/runs/dev/wu0002-1`, thread variables at 4). It is compared with `/home/brianm/projects/physics/chaos/lpcstudy/runs/baseline/smoke/results.json` (read-only; re-check sha256 `0da48771…4b79` first), using the WU-0001.5 method: delete `provenance`, every `seconds`, and `config.seed_id` (DEC-0004). Then also delete and count, from the baseline:
  - `config.transfer_targets` and `config.transfer_sources`;
  - `systems.*.shift`;
  - `scores.A4f`, `km_curves.A4f` and `oracle_recovery.mse_at_href.A4f`;
  - `H2d.shift_wins_A4_over_A3`, `H2d.shift_cells` and `H2d.shift_pass`.

  Then compare `json.dumps(sort_keys=True, allow_nan=True)` for **bitwise** equality. The one intended value change: the new `H2d.pass` must equal the baseline's `H2d.in_distribution_pass` (both `false` in the baseline, so the text is equal). Any other difference fails. Tolerance: none. CPU-to-CPU determinism holds (WU-0009.3), and no numeric code path changes.
- **(b) Gate.** `gate_pass` is true in the new smoke file.
- **(c) Grep.** The ROADMAP grep holds, and in addition `grep -rn "delay_scale\|delay/2\|lorenz96" lpcstudy/ tools/ tests/` finds nothing.

#### WU-0002.2: one identifier table; `n_lib` (M)

**Scope.**
- **In:** a new module `lpcstudy/identifiers.py` with no imports, holding:
  - `HYPOTHESIS_TABLE`: 14 frozen rows with `v3_id`, `v2_id`, `key` (the `results.json` key), `role` (`primary`, `secondary`, `estimate` or `reported`), `criterion` (v3 §2 statistic and "pass if" text, verbatim with markdown escapes removed; for the gain bound, the sentence after the RQ3 table), and `pending` (the ROADMAP sub-task ids whose row names this id, copied, e.g. H1a `("WU-0002.4",)`). The report marks rows still computed with the v1 statistic, so v3 text never silently labels a v1 number.
  - `V1_KEY_MAP`: the DL correction table (v1 key → v3 key or `None`). WU-0002.12 needs it for `pilot_results_v1.json`.
- **Used by:**
  - `experiments.run_system` and `_variant_summary` (result keys);
  - `analysis.h3_regimes` (keys);
  - `report`: `HYPOTHESES` is derived from the table, `verdicts` iterates its rows, `_key_number` is keyed by v3 id, the robustness header, and the figure keys.
- **In:** the `n_lib` relabel (§M15 item 1).
- **Out:**
  - every definition, band, level (`PRIMARY_LEVEL` stays on H2a and H2b), `pass` expression and verdict rule;
  - V7 in the gate (.10);
  - the gain bound's bar (D-21: .8/.9);
  - the H3 figure's 5% line;
  - `StudyConfig` field names (`library_sizes` and `core_library` stay, so `config_record` and later ROADMAP references are unchanged);
  - the `N` that denotes noise sensitivity (`analysis.py:269`, `report.py:119`, `ensemble.py:256-294`) and `oracle.py:50` (sample count).

**Renames (one mapping, applied at once).** Sequential search-and-replace cascades (H1b→H1a collides with v1 H1a; H3c→H3b with v1 H3b; gain-bound H2e with v3 H2e). Each is checked against the DL correction table, lines 78-94:

| v1 key (file:line) | v3 key | Function rename (`analysis.py`) |
| --- | --- | --- |
| H1a (`experiments.py:199`) | `V7`, top-level, reported without a flag until .10 | `h1a_noise_scaling` (`:35`) → `v7_noise_scaling` |
| H1b (`:200`) | H1a | `h1b_library_scaling` (`:83`) → `h1a_library_scaling` |
| H1c (`:201`, robustness `:272`) | H1b | `h1c_seed_amplifier` (`:126`) → `h1b_seed_amplifier` |
| H1d (`:202`) | H1c | `h1d_horizon_law` (`:159`) → `h1c_horizon_law` |
| H1e (`:203`) | H1d | `h1e_proxies` (`:201`) → `h1d_proxies` |
| H1f (`:204`) | `Q-N` | `h1f_noise_redundancy` (`:241`) → `qn_noise_redundancy` |
| H2e (`:209`) | `gain_bound` (role reported) | `h2e_horizon_bound` (`:523`) → `gain_horizon_bound` |
| H3b (`analysis.py:662-669`) | dropped (DL). `regret_ratio_by_K` and `realized_K` move to the reported key `regime_curve`, which the figure (`report.py:353`) reads; `loglog_slope`, `p_eff`, `threshold` and `pass` are deleted | — |
| H3c (`:684-688`) | H3b | — |
| H3d (`:690-692`) | H3c | — |
| H2a to H2d, H3a | unchanged | — |

Also:
- the module docstring `analysis.py:1-6` (ids; primaries H2a, H2b, H3c; D-16);
- the `report.py:23-48` texts, which become the table;
- `report.py:101-154`;
- the robustness header (`report.py:266-280`);
- `verdicts`: skip a row with no result in any system (v3 H2e until .7) instead of a `KeyError`, and drop V7 (it is no longer a hypothesis).

**`n_lib` sites:**
- **Result keys (`results.json` schema change):** `analysis.py:116` `mean_seed_by_N`, `:453` `median_w_by_N` and `:456` `median_at_largest_N` become `…n_lib`. Readers: `report.py:131`, `:375-376`.
- **Result string value:** `analysis.py:458-459` (H2b `threshold`).
- **Text only:**
  - `config.py:40`;
  - `data.py:135`;
  - `ensemble.py:64`;
  - `pipeline.py:8`, `:10` and `:278` (`N=%d` becomes `n_lib=%d`, in `run.log`);
  - `analysis.py:72`, `:85`, `:90`, `:411`;
  - `report.py:131` (`N@`, `Nmax`);
  - the axis at `report.py:378` ("Library size n_lib").
- The `experiments.py:192` `N=` label is removed in .1.

**Import graph.** New node `identifiers: []`; new edges `analysis`, `experiments` and `report` → `identifiers`. Edit `tests/unit/fixtures/lpcstudy_graph.json` by hand from the import statements, in the same commit as the imports, with a dated line in `description` and a new `source_commit`; never from tool output. `test_tools_test_impact.py::test_fixture_schema` pins `len(stems) == 20`, which becomes 21. This is a module count, not a tolerance.

**Tests** (all exact equality of discrete objects or strings; no tolerance):
- `test_identifiers.py` (new):
  - (i) the rows `(v3_id, v2_id, role)` equal the table parsed from `docs/study/decision_log_lpc.md` (the "v3 ID | v2 ID | Role" block), 14 rows;
  - (ii) `V1_KEY_MAP` equals a hand transcription of DL lines 78-94 in the test;
  - (iii) each `criterion` equals the v3 §2 row parsed from `docs/study/proposal_and_methods_v3.md`;
  - (iv) the primaries are {H2a, H2b, H3c} (v3 §7);
  - (v) an AST scan of `lpcstudy/*.py`, excluding `identifiers.py`: every string constant matching `^(H\d[a-f]|Q-N|T1)$` is a table key, and no name or constant contains `H1e|H1f|H2f|H3d|T1` or `h1e_|h1f_` (this is the ROADMAP grep, with the documented exception).
- `test_report.py`:
  - (vi) `_key_number` for each v3 key on a synthetic result dict returns its numbers, and the H1a and H2b strings say `n_lib`;
  - (vii) `write_markdown` on fake per-system results lists exactly the table's v3 ids in table order, and marks pending rows;
  - (viii) the library figure's x-label is "Library size n_lib" (`monkeypatch` `report.plt.close` to keep the figures);
  - (ix) `verdicts` on results without H2e has no `H2e` entry and no `KeyError`.

**Acceptance additions** (fixed now):
- **(d) Smoke regression, as (a)**, after the .1 deletions plus `V1_KEY_MAP` applied to `systems.*` and `verdicts`:
  - verdicts H1a (now V7) and H3b-v1 deleted and counted;
  - v1 `H3b.{loglog_slope, p_eff, threshold, pass}` deleted, with `{regret_ratio_by_K, realized_K}` moved to `regime_curve`;
  - the three `…_N` keys renamed;
  - the H2b `threshold` string excluded and listed.

  Every remaining numeric and boolean leaf must be **bitwise** equal. The developer lists every deleted, moved or text-changed leaf with its count.
- **(e) Smoke key check.** On the smoke output, every key of `systems.*` matching `^(H\d[a-z]|Q-N|T1)$` is a table key. Every id in the `RESULTS.md` verdict table is a v3 id.

#### Affected checks (§4.2; run once per sub-task, after its last code commit)

Before running, compare with `python3 tools/test_impact.py --explain` and take the union with the set below.

- **.1:**
  - Unit: `tests/unit/test_{config,systems,data,ensemble,oracle,allocation,analysis,report,__main__,seeds,provenance}.py`, plus `test_dynamics.py` and `test_embedding.py` (the known gap, added by hand: they import `systems`), plus `test_tools_run_preset.py`.
  - Integration: `tests/integration/test_cli_seeds.py` and `test_preset_wrapper.py`.
  - The hand smoke run of (a) replaces `test_smoke_pipeline.py` (same evidence, §4.2).
- **.2:** the same unit set without `test_systems.py` and `test_tools_run_preset.py`, plus `test_identifiers.py` and `test_tools_test_impact.py` (fixture). Integration as for .1, with the hand smoke run of (d).
- **Not run:** `slow`, `gpu`, `test_statistics`, `test_conftest_markers`, `test_tools_{gpu_hours,run_tests}`.
- The ROADMAP's "`tests/unit` pass" is read as this radius now, plus the unit tier at the merge gate (RSRC.11).

#### Order and commits

- **.1**, one commit each:
  1. A4f;
  2. Lorenz-96, transfer and T1, together with `run_preset.sh` and the two CLI tests;
  3. τ_d/2;
  4. shift and H2d part (ii);

  then one radius run, the smoke regression (a)–(c), and a Log commit.
- **.2:**
  1. `identifiers.py` and `test_identifiers.py` (no imports yet; no graph change);
  2. renames, with the imports, the fixture and the 20→21 count edit;
  3. `n_lib`;

  then one radius run, (d) and (e), and a Log commit.
- Review .1 and .2 as one group (WU-0002.13).

#### Risks

- **Rename cascade.** Apply all renames in one mapping step. Test (v) catches leftovers.
- **Lost regret-vs-K figure** if v1 H3b is deleted before `regime_curve` exists.
- **Report and verdict `KeyError`** for the table row H2e, which has no result yet.
- **v3 criterion text next to v1 statistics.** Mitigated by `pending`.
- **Report, figures and the integration test are not covered by the bitwise check** (`RESULTS.md` is text). Mitigated by tests (vi)–(ix).
- **Edited tests:** `test___main__.py` (argv), `test_tools_run_preset.py` (argv plus a new assertion), `test_tools_test_impact.py` (count). Each is listed in the Log with its reason.
- **No test is removed.** The 14 v1 tests exercise no removed code.
- **Scope moved from later sub-tasks.** .8 loses "remove v1 H3b" and "H2d part (ii)", which move to .2 and .1. The v1 H1a → `V7` key rename precedes .10. Log a map of old to new function names for the concordance (D-rows cite v1 names).

#### Owner checkpoint (LPC.PC.11)

- **.1** touches seed and provenance surfaces: the `__main__.py` option set behind `choose_seed`'s refusal, and `tools/run_preset.sh`. It also touches verdict code: the T1 branch and H2d's `pass`.
- **.2** touches verdict and statistics code by renames only, plus the guard in `verdicts`.
- **Both:** "needs owner review before freeze" applies. Dependencies: none.

#### Questions for the owner (non-blocking; the defaults above apply unless the owner rules otherwise)

1. The .2 grep "finds no live code symbol". The table must carry v2 ids (and `V1_KEY_MAP` the v1 ids), so `H3d` and `H1f` appear in `identifiers.py`. The plan reads those fields as historical data, not live symbols. Confirm.
2. Key names: `gain_bound`, `regime_curve`, and a top-level `V7` until .10.
3. The criterion text is v3 verbatim, including v3's own `N_lib`. Should it be respelled `n_lib`?
4. `gain_proxy` is computed but unused after A4f goes. Remove it later (core `ensemble`; it does not affect the regression), or keep it?


#### Main-session amendment, 2026-10-10 (claude-sonnet-5-5), before execution (VV.3)

The owner questions above are answered in `DEC-0007` (proposed, on `develop`) by taking the plan's defaults; the pulled-forward items are recorded there with their consequence for the ROADMAP's WU-0002.8 "no `H3b` key" check (pending the owner's ruling A2). No acceptance criterion changes. Do not edit `decisions.md`, `defects.md` or `queue.md` in this branch.

## Log

### 2026-10-10 developer (claude-sonnet-5-5), WU-0002.1: removals (four commits, before the radius run)

Branch `wu/0002-removals-ids` from `develop` 5889058. Commits (each with the trailers `Agent: claude-sonnet-5-5` and `Co-Authored-By`):

| Commit | Content |
| --- | --- |
| `c011e9e` | A4f: `allocation.full_form_weight`, `RULE_LABELS["A4f"]`, the A4f entry of `pipeline.rule_weights`, `FittedRules.n_analogs` and `.state_dim`, the `state_dim` parameter of `rule_weights` (grep confirmed A4f was its only user; `analysis.py:146` reads `cell.setup.n_analogs`, not `FittedRules`); README row. New test `test_allocation.py::test_rule_set_is_the_v3_rule_set`. |
| `4f70254` | Lorenz-96 (`lorenz96_field`, `SYSTEMS["lorenz96"]`), `transfer_targets`/`transfer_sources` (docstring, fields, SMOKE `replace`), `run_transfer`, `run_transfer_target`, the transfer block and `--skip-transfer` in `__main__`, the T1 branch of `report.verdicts` and the T1 Markdown section, `--skip-transfer` in `tools/run_preset.sh` (header, usage, case); README. New tests: `test_systems.py` (new file), `test_config.py::test_config_has_no_transfer_fields`, `test___main__.py::test_removed_skip_transfer_option_is_refused`, `test_tools_run_preset.py::test_removed_skip_transfer_option_is_refused`. |
| `309b84f` | `"delay/2"` variant; `delay_scale` in `build_context`, `Study.context` (cache key now `(system, dim)`), `Study.run_cell`. `int(round(min(..) * 1.0))` became `int(round(min(..)))`. New test `test_data.py::test_no_delay_scale_parameter_remains` (placement: `test_data.py`, as the plan allows). |
| `e644653` | Shift: `shift_scores`, `extreme_sizes`, `shifted`, `core_sub_scores`, `res["shift"]`, `analysis.shift_gaps`; H2d signature now `(scores, config)`, keys `shift_wins_A4_over_A3`, `shift_cells`, `shift_pass` removed, `pass = bool(in_dist_ok)`; `report.py` H2d text and key number lose the shift clause. Noise- and library-sweep cells now run `with_evals=False`: the grep shows no consumer of their `evals` (`h1a`, `h1b`, `h2b` read `moments` and `oracles` only; `_sweep_subset` reads the core cell, which keeps its evals). New test `test_analysis.py::test_h2d_is_the_in_distribution_part_only`. |

Decisions within the plan (no criterion changed):

- Plan row `experiments.py:7` says docstrings "say robustness": module docstring stage (v) now reads "robustness"; `run_system`'s Returns note says "for robustness".
- `pipeline.fit_rules` docstring "several for pooled transfer" reworded (a transfer mention the plan's table did not list).
- `gain_proxy` kept (core `ensemble`; DEC-0007 answer 4). `_sweep_subset` still slices it.
- Experiment-id labels such as "(E5)" in the stage (iv) docstring are not touched (out of scope: relabels).
- The pure-removal commits did not touch the import graph (no module added or removed), so the fixture is unchanged in .1.
- `ruff check --select F lpcstudy` (an unused-import check, read-only) passes after the removals.
- Greps after the last commit: `grep -rn "lorenz96\|transfer\|A4f\|shift" lpcstudy/` returns nothing; `grep -rn "delay_scale\|delay/2\|lorenz96" lpcstudy/ tools/ tests/` returns only the three new tests that name the removed symbols as strings.

Existing tests edited (argv only, assertions unchanged, none removed):

| Test | Edit | Reason |
| --- | --- | --- |
| `tests/unit/test___main__.py::run_with_fakes` (helper used by the fake-study tests) | `"--skip-transfer"` dropped from argv | The option no longer exists; `choose_seed` would now refuse it. The assertions (`main(...) == 0`, saves) are unchanged. |
| `tests/unit/test_tools_run_preset.py::test_pass_through_arguments_follow_the_seed` | `--skip-transfer` dropped from argv and from the expected tail; docstring updated | The wrapper now refuses it. The assertions are the same checks on the remaining arguments. |
| (`tests/unit/test_tools_test_impact.py` is not touched in .1) | | |

#### §4.9 checklist, WU-0002.1 radius run (unit tier, then integration)

1. Change set: `git diff --name-only develop...HEAD` plus status: `README.md`, `lpcstudy/{__main__,allocation,analysis,config,data,experiments,pipeline,report,systems}.py`, `tools/run_preset.sh`, `tests/unit/test_{__main__,allocation,analysis,config,data,tools_run_preset}.py`, `tests/unit/test_systems.py` (new), this unit file.
2. Radius: `python3 tools/test_impact.py --base develop --explain` selects 12 unit files (`test___main__ test_allocation test_analysis test_config test_data test_ensemble test_oracle test_provenance test_report test_seeds test_systems test_tools_run_preset`) and `tests/integration`. Hand additions per the plan: `test_dynamics.py`, `test_embedding.py` (they import `systems`; the known graph gap). Integration narrowed to `test_cli_seeds.py` and `test_preset_wrapper.py`: the plan replaces `test_smoke_pipeline.py` by the hand smoke run of (a)-(c). Smaller than the suite; no gate.
3. Already run: no (all new code).
4. Device: `JAX_PLATFORMS=cpu` (set by `tools/run_tests.sh`).
5. Threads and time: `LPC_THREADS=4`; unit tier timeout 300 s, integration 900 s.
6. Contention: `pgrep -fa "lpcstudy --preset"` shows no run; no GPU use.
7. Output: wrapper default `-q --tb=short -rfE`.
8. Commands: `tools/run_tests.sh unit <the 14 unit files>` and `tools/run_tests.sh integration tests/integration/test_cli_seeds.py tests/integration/test_preset_wrapper.py`.

## Review

## Audit
