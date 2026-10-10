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

#### 2026-10-10 developer (claude-sonnet-5-5), WU-0002.1: radius results and the smoke regression (a)-(c)

Radius results (each set run once): `tools/run_tests.sh unit` on the 14 unit files `test___main__ test_allocation test_analysis test_config test_data test_dynamics test_embedding test_ensemble test_oracle test_provenance test_report test_seeds test_systems test_tools_run_preset`: `209 passed in 15.69s`. `tools/run_tests.sh integration tests/integration/test_cli_seeds.py tests/integration/test_preset_wrapper.py`: `10 passed in 137.52s (0:02:17)`. No failure, no `--lf` run.

Self-check of the diff: no `clip|nan_to_num|isfinite|where(|try:|except` added (only deletions in those files); no `default_rng|random.|PRNGKey` added in `lpcstudy/` (the tests use fixed `np.random.default_rng(7)` for a manufactured input); no tolerance in an existing assert changed; the only new tolerance is `abs=1e-12` in the H2d test, justified in its docstring.

Smoke regression (a). Clean committed tree at `696b3b367acc1bc7e682df03bcb233cfe739d8cf` (`git status --porcelain` empty; no `lpcstudy --preset` run active). Baseline `/home/brianm/projects/physics/chaos/lpcstudy/runs/baseline/smoke/results.json` read-only, sha256 re-checked `0da48771ee967525f71518d4bb6e7aec675349ff175a2d4544234d4f8f084b79` (matches). Run once, CPU, via the wrapper: `tools/run_preset.sh smoke DEV-0 runs/dev/wu0002-1` (exit 0, 62 s study time, 65 s wall; output under `runs/dev/wu0002-1/smoke/`, gitignored). Comparison: a one-off script (session scratchpad, not committed), WU-0001.5 method.

- Deleted from both (counted): `seconds` 5 in each; new only: `provenance` 1 and `config.seed_id` 1; `handling` 0.
- Deleted from the baseline only (leaf counts; the run changed no number outside these): `config.transfer_targets` and `config.transfer_sources` (empty lists in the smoke preset, 0 leaves, 2 keys); `systems.lorenz63.shift` 20; `scores.A4f` 14; `km_curves.A4f` 240; `oracle_recovery.mse_at_href.A4f` 1; `H2d.shift_wins_A4_over_A3` 1; `H2d.shift_cells` 1; `H2d.shift_pass` 1. Total 278 leaves (plus the 2 empty-list keys).
- Intended value change: `H2d.pass` baseline `false` (= `in_distribution_pass` `false`), new `false`. The script asserts new `pass` equals the baseline `in_distribution_pass`; the baseline value is set to it before the comparison.
- Result: `json.dumps(sort_keys=True, allow_nan=True)` texts are **equal** (56984 characters each). The 3316 remaining leaves (3238 numbers, 52 booleans, 26 strings, 0 null) are bitwise equal; no path differs. No tolerance.

(b) Gate: `validation.gate` of `lorenz63` is `{V1: true, V2: true, V4: true, V5: true, V6: true, gate_pass: true}`. (c) Greps: `grep -rn "lorenz96\|transfer\|A4f\|shift" lpcstudy/` returns nothing; `grep -rn "delay_scale\|delay/2\|lorenz96" lpcstudy/ tools/ tests/` returns only the three new tests that name the removed symbols as strings (`test_systems.py`, `test_data.py`, `test_config.py`). `tests/unit/wrapper_helpers.py` contains a shell `shift` outside `lpcstudy/` (not in the grep scope). The provenance block of the new file: `seed_id` DEV-0, `complete` true, `dirty` false, commit `696b3b36`.

Open for the reviewer: the owner checkpoint of the plan applies (`__main__` option set, `tools/run_preset.sh`, the T1 branch, H2d `pass`). The sweep cells now run `with_evals=False`: the bitwise equality shows the moments are unaffected by that.

### 2026-10-10 developer (claude-sonnet-5-5), WU-0002.2: identifier table, v3 ids, `n_lib` (three commits, before the radius run)

| Commit | Content |
| --- | --- |
| `47f420a` | New `lpcstudy/identifiers.py` (no intra-package imports): `Hypothesis` (frozen dataclass), `HYPOTHESIS_TABLE` (14 rows), `V1_KEY_MAP` (16 v1 keys); `tests/unit/test_identifiers.py` tests (i)-(iv). Deviation from the commit table, for consistency: the fixture node `identifiers: []` and the `test_fixture_schema` count 20 -> 21 are in this commit, because adding the module file is itself a graph change (otherwise `sorted(graph) == stems` fails at this commit). |
| `9cf698c` | All renames at once (below), imports of `identifiers` in `analysis`, `experiments`, `report`, fixture edges by hand, `source_commit` set to `47f420a`; test (v) (AST scan), `check_keys` plumbing, report tests (vii) and (ix). |
| `33bc928` | `n_lib` (below); report tests (vi) and (viii), `check_keys` test. |

Decisions within the plan (no criterion changed):

- Tests (v)-(ix) were added in the commit where the code they test lands (the plan puts them all in .2 without a per-commit split). Test (vi) and (viii) are in `33bc928` because their strings contain `n_lib`.
- `identifiers.py` imports `dataclass` from the standard library. "No imports" is read as "no intra-package imports" (the graph node is `identifiers: []`).
- Row field `v3_id` of the gain bound is `(reported)` exactly as in the decision-log table (test (i) compares with the parsed table); its `key` is `gain_bound`. For the other 13 rows `key == v3_id`. `_key_number` and `verdicts` are keyed by `key` (equal to the v3 id except for the gain bound).
- `criterion` format: `"<statistic>; pass if <rule>"` from v3 section 2 (Q-N: `pass if read by the table in §7`); the gain bound is the sentence after the RQ3 table. Test (iii) parses section 2 independently and compares.
- `pending` was copied from the ROADMAP rows of WU-0002.4 to .8 as the plan says: H1a, H1b (.4), H1d (.5), Q-N (.6), H2b, H2e (.7), H2d, H3a, H3c (.8). Rows no ROADMAP row names (H1c, H2a, H2c, v3 H3b, gain bound) are not marked, although D-14, D-20, D-25 say their v1 statistics or verdicts may change (the concordance referral). The report therefore does not mark them; flagged for the reviewer.
- The report text `[computed with the v1 statistic until WU-0002.x]` is appended to the criterion of a pending row in the Markdown table. A row of the table without a result (v3 H2e) is listed with `n/a: no result` cells and the verdict `no result`; `verdicts` has no entry for it.
- `identifiers.check_keys` (not in the plan): called where results are assembled (`run_system`, `_variant_summary`, `h3_regimes`). It raises `ValueError` for a key shaped like a hypothesis id that is not in the table, so a leftover v1/v2 id fails loudly; it replaces nothing and counts as the runtime use of the module by `analysis` and `experiments` (the plan's import edges). It adds no clip, fallback or silent path.
- Rules left untouched: `verdicts` still produces `"partially supported"` and still reads `["pass"]` (WU-0002.9); `PRIMARY_LEVEL` stays on H2a and H2b (`analysis.py`); the H3 figure's 5% line, the gain bound's 0.9 bar and every `pass` expression are unchanged. The report intro sentence "*partially supported* if on at least one" is unchanged.
- Result key `V7` (v1 H1a) is top-level in `systems.*`, written without a flag; it has no row in the verdict table (so RESULTS.md no longer shows a v1 H1a row, and `verdicts` has no entry for it, as the plan says).
- Regime figure: `report.make_figures` reads `systems.*.regime_curve.regret_ratio_by_K` (moved from v1 `H3b`), so the figure exists before and after.
- ROADMAP check noted for the reviewer and owner: WU-0002.8's check "no `H3b` key exists anywhere in results" conflicts with the v3 `H3b` (structure, v1 `H3c`) that this unit creates; this is the pending ruling A2 of DEC-0007. Nothing was done about it here.

Map of old to new function names (analysis.py), for the concordance D-rows that cite v1 names:

| v1 name | v3 name |
| --- | --- |
| `h1a_noise_scaling` | `v7_noise_scaling` |
| `h1b_library_scaling` | `h1a_library_scaling` |
| `h1c_seed_amplifier` | `h1b_seed_amplifier` |
| `h1d_horizon_law` | `h1c_horizon_law` |
| `h1e_proxies` | `h1d_proxies` |
| `h1f_noise_redundancy` | `qn_noise_redundancy` |
| `h2e_horizon_bound` | `gain_horizon_bound` |
| `h2a_separation`, `h2b_knob_response`, `h2c_state_dependence`, `h2d_empirical_comparison`, `h3_regimes` | unchanged names (`h3_regimes` now returns `H3a`, `H3b`, `H3c` and `regime_curve`) |

`n_lib` sites changed: result keys `mean_seed_by_N`, `median_w_by_N`, `median_at_largest_N` (with the report readers); the H2b `threshold` string; docstrings in `config.py` (library sizes), `data.py`, `ensemble.py`, `pipeline.py` (module vocabulary) and `analysis.py` (`_fit_seed_law`, H1a, `h1a_library_scaling` argument, H2b); the `N=%d` label in the cell log of `pipeline.py` (`n_lib=%d`); the report key-number strings (H1a and H2b) and the library-figure axis. Not changed, per the plan: the `N` that is noise sensitivity (`analysis.py` Q-N docstring, `report.py` H1d string, `ensemble.py`), `oracle.py:50` (sample count), `StudyConfig` field names (`library_sizes`, `core_library`), the criterion text (v3's own `N_lib`, DEC-0007 answer 3).

#### §4.9 checklist, WU-0002.2 radius run (unit tier, then integration)

1. Change set: `git diff --name-only develop...HEAD` plus status: as for .1, plus `lpcstudy/identifiers.py` (new), `tests/unit/test_{identifiers (new),report,tools_test_impact}.py`, `tests/unit/fixtures/lpcstudy_graph.json`, `lpcstudy/{analysis,experiments,report,pipeline,ensemble,data,config}.py` (changed again), `README.md`, this unit file.
2. Radius: `python3 tools/test_impact.py --base develop --explain` (it also lists .1's files) selects the 14 unit files `test___main__ test_allocation test_analysis test_config test_data test_ensemble test_identifiers test_oracle test_provenance test_report test_seeds test_systems test_tools_run_preset test_tools_test_impact` and `tests/integration`. Plan for .2: the .1 set without `test_systems.py` and `test_tools_run_preset.py` (not touched in .2), plus `test_identifiers.py` and `test_tools_test_impact.py`, with `test_dynamics.py` and `test_embedding.py` kept because the plan says "the same set". Integration narrowed to `test_cli_seeds.py` and `test_preset_wrapper.py`, with the hand smoke of (d)/(e) replacing `test_smoke_pipeline.py`. Smaller than the suite; no gate.
3. Already run: no (the .1 run was on the code before the .2 commits; `test_identifiers.py` and the new report tests have not run).
4. Device: `JAX_PLATFORMS=cpu` (set by `tools/run_tests.sh`).
5. Threads and time: `LPC_THREADS=4`; unit timeout 300 s, integration 900 s.
6. Contention: `pgrep -fa "lpcstudy --preset"` shows no run; no GPU use.
7. Output: wrapper default `-q --tb=short -rfE`.
8. Commands: `tools/run_tests.sh unit <the 14 unit files above for .2>` and `tools/run_tests.sh integration tests/integration/test_cli_seeds.py tests/integration/test_preset_wrapper.py`.

#### 2026-10-10 developer (claude-sonnet-5-5), WU-0002.2: radius results (first pass)

Unit set (14 files, listed in the checklist above): `1 failed, 201 passed in 11.17s`. The failure: `test_identifiers.py::test_check_keys_accepts_table_keys_and_refuses_stale_ids`, "DID NOT RAISE". Diagnosis: my own new test used the made-up id `H9z`; `check_keys` treats an id as hypothesis-shaped only when the letter is in `a`-`f` (the pattern `^(H\d[a-f]|Q-N|T1)$` of the ROADMAP grep), so `H9z` is correctly not refused. The code is as designed; the example in the test was wrong. Fix (test only): `H9z` becomes `H9f`. `--lf` on the failing test: `1 passed, 6 deselected in 0.30s`. The other 13 files were not re-run (no code or test change in them). Integration (`test_cli_seeds.py`, `test_preset_wrapper.py`): `10 passed in 137.28s (0:02:17)`.

Before the smoke run I refined one report string (found while reading the smoke `RESULTS.md`): the v3 `H2e` row has no result, but its text read "[computed with the v1 statistic until WU-0002.7]", which is false for a row that is not computed. `report.write_markdown` now writes "[not computed until WU-0002.7]" for a row without a result (`_hypothesis_text(row, computed=False)`); rows with a result and a pending sub-task are unchanged. The test (vii) expectation changed with it (my own new test; the changed expectation is the new wording, nothing was loosened).

§4.9 checklist for the re-run after this report change (`report.py` is a pipeline module):

1. Change set: `lpcstudy/report.py`, `tests/unit/test_report.py`, this file.
2. Radius: `report` -> own unit test `test_report.py` and the direct dependent `test___main__.py`, plus `tests/integration` (narrowed as above to `test_cli_seeds.py` and `test_preset_wrapper.py`; the hand smoke of (d) is its replacement). Smaller than the suite; no gate.
3. Already run: not on this code (the earlier run was before the change).
4. Device: `JAX_PLATFORMS=cpu`. 5. Threads: 4; unit 300 s, integration 900 s. 6. Contention: no preset run. 7. Output: `-q --tb=short -rfE`.
8. Commands: `tools/run_tests.sh unit tests/unit/test_report.py tests/unit/test___main__.py`; `tools/run_tests.sh integration tests/integration/test_cli_seeds.py tests/integration/test_preset_wrapper.py`.

#### 2026-10-10 developer (claude-sonnet-5-5), WU-0002.2: radius re-run and the smoke regression (d), (e)

Re-run after the report wording change: `tools/run_tests.sh unit tests/unit/test_report.py tests/unit/test___main__.py`: `41 passed in 1.55s`; integration (`test_cli_seeds.py`, `test_preset_wrapper.py`): `10 passed in 137.25s (0:02:17)`. Summary of the .2 evidence: unit radius `201 passed, 1 failed` (the failing test fixed with `--lf`, `1 passed`), then `41 passed`; integration `10 passed` twice (once per code state). No test removed. Edited existing tests in .2: `tests/unit/test_tools_test_impact.py::test_fixture_schema` (module count 20 -> 21 and its docstring, as the plan says: a count of modules, not a tolerance; the independent part, `sorted(graph) == stems`, is unchanged). `test_report.py` and `test_identifiers.py` only gained new tests.

Smoke regression (d). Clean committed tree at `5cd25e97` (`git status --porcelain` empty; no preset run active; the first smoke run of this sub-task, at `ce92c610`, was discarded because the report wording changed after it; this is the single retained run). Baseline sha256 re-checked `0da48771ee967525f71518d4bb6e7aec675349ff175a2d4544234d4f8f084b79` (matches). Run once, CPU, `tools/run_preset.sh smoke DEV-0 runs/dev/wu0002-2` (exit 0, 64 s study time). Comparison: one-off script (scratchpad, not committed) that applies, to the baseline only, the .1 deletions and then `lpcstudy.identifiers.V1_KEY_MAP` to `systems.*` and `verdicts`:

- Stripped as before: `seconds` 5 in each file; `provenance` 1 and `config.seed_id` 1 in the new file only.
- Deleted from the baseline (leaves; 286 in all): the 278 of .1 (`systems.lorenz63.shift` 20, `scores.A4f` 14, `km_curves.A4f` 240, `oracle_recovery.mse_at_href.A4f` 1, `H2d.shift_wins_A4_over_A3`, `shift_cells`, `shift_pass` 1 each; the `config.transfer_*` keys hold empty lists, 0 leaves); plus v1 `H3b.{loglog_slope, p_eff, threshold, pass}` 4; verdict v1 `H1a` (now `V7`, no verdict) 2; verdict v1 `H3b` 2.
- Moved: v1 `H3b.{regret_ratio_by_K, realized_K}` to `regime_curve`, 6 leaves.
- Renamed keys only (121 leaf positions, values compared): `systems.lorenz63` v1 `H1a` to `V7` (8), `H1b` to `H1a` (11), `H1c` to `H1b` (11), `H1d` to `H1c` (17), `H1e` to `H1d` (7), `H1f` to `Q-N` (27), `H2e` to `gain_bound` (6), `H3c` to `H3b` (10), `H3d` to `H3c` (3); verdicts `H1b`..`H1f`, `H2e`, `H3c`, `H3d` to their v3 keys (16); the `n_lib` keys `mean_seed_by_N` (2), `median_w_by_N` (2), `median_at_largest_N` (1) (these are nested inside the H1a/H2b results and counted again in their rows).
- Text excluded from both sides: `systems.lorenz63.H2b.threshold` (old: "... for N at each rho; median w*(N_max) < 0.95 ..."; new: the same with `n_lib`, `n_lib max`).
- `H2d.pass`: baseline `false` = `in_distribution_pass` `false`; new `false` (asserted equal).
- Result: `json.dumps(sort_keys=True, allow_nan=True)` texts **equal** (56646 characters each). The remaining 3307 leaves (3236 numbers, 49 booleans, 22 strings) are bitwise equal; no path differs; no tolerance.

(e) Key check on the smoke output: the hypothesis-shaped keys of `systems.lorenz63` are `H1a H1b H1c H1d H2a H2b H2c H2d H3a H3b H3c Q-N`, all keys of the table; `V7`, `regime_curve` and `gain_bound` are present; `H2e` is absent (not computed). The `verdicts` keys are the 13 table keys that have a result (no `H2e`, no `V7`). The 14 first-column ids of the `RESULTS.md` verdict table equal the table's v3 ids in order (`H1a H1b H1c H1d Q-N H2a H2b H2c H2d H2e (reported) H3a H3b H3c`); the `H2e` row reads `[not computed until WU-0002.7] | n/a: no result | no result`. Gate `gate_pass` true; the four figures are written; `run.log` cell lines read `n_lib=10000`. Provenance: `seed_id` DEV-0, `complete` true, `dirty` false, commit `5cd25e97`.

Greps: `grep -rn "H1f\|H3d\|H1e\|H2f\|T1" lpcstudy/` finds only `identifiers.py` (the table rows, `V1_KEY_MAP` and the `check_keys` docstring and code: historical data of the map, DEC-0007 answer 1). The `N` that is noise sensitivity and `oracle.py:50` are unchanged. Self-check of the diff `develop...HEAD`: no `clip|nan_to_num|isfinite|where(|try:|except` and no `default_rng|random.|PRNGKey` added in `lpcstudy/`; no tolerance in an existing assert grew; new tolerances: `abs=1e-12` in the H2d test only.

Open points for the reviewer and the owner (unit status not set):
1. The `pending` marks cover only the rows a ROADMAP row names (H1c, H2a, H2c, v3 H3b and the gain bound are unmarked although their statistics or verdicts may change under the concordance referral).
2. The `check_keys` guard and the `(reported)` v3 id of the gain bound are my choices within the plan (Log above).
3. WU-0002.8's "no `H3b` key exists anywhere in results" now collides with v3 `H3b` (ruling A2 pending, DEC-0007).
4. Owner checkpoint: `__main__` option set and `tools/run_preset.sh` (.1); T1 branch, H2d `pass`, verdict code (.1, .2).

## Review

## Audit
