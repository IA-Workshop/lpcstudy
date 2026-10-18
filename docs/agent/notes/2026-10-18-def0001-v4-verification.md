# DEF-0001: independent V4 grep verification of the WU-0002.11 inventory (2026-10-18)

- **Who:** reviewer, claude-opus-5-5, fresh context, read-only. No test, no preset, no run, no web, no sealed seed.
- **What this is:** an independent read that supports the empty `## Audit` of `docs/agent/records/work/WU-0002.11-counters.md`. **It is not the audit.** The owner's `/audit freeze` (WU-0004.4) remains the confirmation that DEF-0001 needs. No record was edited and no code was changed.
- **Tree:** develop at `c89ebe5` (worktree `lpcstudy-wt/wu/def0001-audit-note`, branch `wu/def0001-audit-note`). The inventory was taken at `8fbfa6b`, so line numbers differ from the inventory's. Every row below gives the site at `c89ebe5` and maps it to the inventory row by content.
- **Modules added after `8fbfa6b`:** `clip_sensitivity.py` (9ffc518, WU-0002.11e), `budget.py` (dff3692, WU-0008.3) and `dump.py` (bcbf54e, WU-0003.7b). All three are in the scan.

## Method

The pattern is the plan's V4 pattern, verbatim (unit file, `### Inventory of silent sites`):
`np.clip|clip(|nan_to_num|isfinite|nanmedian|nanquantile|nanmean|np.maximum(|np.minimum(|1e-300|1e-12|1e300|1e6|try:|except|warnings|errstate|fallback|default_rng|jnp.where`.

The command was `grep -rnF -f <the 20 fixed strings, one per line> lpcstudy/ --include=*.py`. It returned **257 hit lines**. A script then mapped every hit to a class by `file:line`, and it fails if any hit is unmapped or any mapping is unused. Both checks passed.

Classes:

- **C:** covered. The hit maps to an inventory row (id given) and its counter, or to the defect the row moved to.
- **J:** justified benign use. The reason is given: a definition, an algorithm step, a refusal, a visible NaN, null or label, a fixture, or a proof or test.
- **text:** not a code site. The hit is a docstring, comment or string, or an identifier substring: `registry:`, `entry:` and `entry: dict` all contain `try:`.
- **U:** not covered. This is a silent clip, replacement, skip, fallback or swallow that is neither counted nor justified in the code.

## Counts

| Class | Hit lines |
|---|---|
| C (covered by an inventory row and its counter) | 86 |
| J (justified benign use) | 89 |
| text (not a code site) | 78 |
| **U (not covered)** | **4 lines = 2 sites** |
| **Total** | **257** |

## Uncovered sites

**UNCOVERED-1. `lpcstudy/clip_sensitivity.py:408-409`.** Severity: **low**, report-only. It feeds no verdict.

- **What the code does.** `h1b_part` floors the H1b PLP squared error twice, as `np.maximum(sq_plp, 1e-12)` (original) and `np.maximum(sq_plp_2, 1e-12)` (under P2), before the log. Neither floor is counted.
- **Why it is not covered.** It is not an inventory row: the module postdates `8fbfa6b`. Its production counterpart is counted, as `H1b.PLP.n_floored` (row N4, `analysis.py:479-483`).
- **What it affects.** Only the H1b entry of `clip_sensitivity.by_hypothesis` (the RESULTS.md `clip` column). No verdict changes.
- **A justification is available, but the code does not carry it.**
  1. `perturb_moments` adds `3 L^2 q / M >= 0` to `sq_plp` at H_ref and `+0.0` (bitwise unchanged) where `q = 0`.
  2. A state with `q >= 1` clipped draws already has `sq_plp >= 100 q / M`, which is far above `1e-12`.
  3. So the set of states floored under P2 equals the original floored set, and its size is exactly `H1b.PLP.n_floored`.
- **Suggested fix.** Either write the argument as one docstring sentence in `h1b_part` and add a test that the floored masks before and after P2 are equal (reference: the hand argument above; exact boolean equality), or report `n_floored` in the part entry.

**UNCOVERED-2. `lpcstudy/clip_sensitivity.py:577-579`.** Severity: **very low**.

- **What the code does.** In `_failed`, `except Exception: by_hypothesis = {}` swallows a second exception, the one raised while listing the parts. It is not logged and not added to `reason`.
- **What stays visible.** The block is already `status = "not_computed"`. The first reason is logged and shown in RESULTS.md (`_clip_text` returns "not computed (reason)" before it reads the parts). Only the second error's identity is lost, and the part list comes out empty. The test `test_an_exception_inside_the_block_is_recorded_not_raised` (the `worse` case) asserts `by_hypothesis == {}`.
- **Suggested fix.** Add `LOG.exception(...)` in that `except`, or append `"; parts not listed: <repr>"` to `reason`.

The other broad excepts of the module, at lines 570 and 619, are **J**. Their failures are recorded in `results.json` (`status`, `reason`, `error: <repr>`), logged with a traceback, and printed in RESULTS.md. Line 570 is tested; line 619 is not (see O-3).

## Observations outside the V4 hit count (not grep hits)

- **O-1 (low, report-only).** `clip_sensitivity.py:454` discards `n_constant_states` under P2 (`rho_corr, _ = ...`), and `:458` discards the `n_failed` of `percentile_interval`. More generally, `part_entry` carries no failed-resample count for any recomputed tier-A part. Failed resamples go to the A3 tail rather than being dropped, so the interval is conservative. Still, the counts behind the P2 recomputation are not reported.
- **O-2 (low, report-only).** The `1e-300` floors of `oracle_weight`, `global_weight` and `regime_weight` run on the **perturbed** moments in `clip_sensitivity.py:665, 668, 729, 821` and are not counted.
  - **Justification (not written in the code):** with the CP sentinel at 0 (checked at `:600-604`), `|chi| <= L q / M`. So `c' - c = 3 L^2 q / M - 2 L chi >= L^2 q / M >= 0`, and `q = 0` leaves `c` bitwise unchanged.
  - So the floors under P2 bind on a subset of the states where they already bind, and those are counted by `curvature_floor` and `pooled_curvature_floor`.
  - **Suggested fix:** one docstring sentence in `perturb_moments`.
- **O-3 (low).** The per-criterion `_guarded` failure path (`clip_sensitivity.py:617-621`) has no direct test: no injection inside a single criterion builder. Also, `log_flags` writes no WARNING for a part that is `not_computed` inside a computed block. Only the ERROR traceback from `LOG.exception` appears.
- **O-4 (known, residue (c) of the DEF-0001 line of 2026-10-18).** `skipped_variants` (DEF-0025) goes to `run.log` only. It is not in `results.json` (`experiments.py:496-501`, with the comment "not in the results block: no schema change"). No configured preset can skip a variant.
- **O-5 (informational).** `dump.py:319-374` calls `oracle_weight` on half-draw moments for the opt-in state dump. Its floors are not counted, but the dump is a diagnostic artefact outside `results.json`.
- **Confirmed absent.**
  - `statistics.block_bootstrap`, which drops silently, has no caller in `lpcstudy/` or `tools/*.py`.
  - `ParametricEstimator.estimate`, which drops the flags, is called only through `estimate_counted`.
  - `_per_state_spearman`, the uncounted delegate, has no caller.
  - Every `bootstrap_values`, `block_bootstrap_counted` and `_boot` call in `analysis.py` and `clip_sensitivity.py` passes a `make_rng(...)` generator. The int-seed branch of `statistics.py:218` is reached only by the V2 and V5 fixtures (`validation.py:114`, `:160`, by design, Q7) and by tests.

## Do the counters reach `results.json` and RESULTS.md?

**`results.json`.**

- **Per system.** `experiments.py:674` writes `res["handling"] = study.system_handling(system, collect_result_counts(res))`. The assembly is `pipeline.py:291-313`, with schema `lpcstudy.handling/2`: `cells`, `oracles`, `fitting`, `result_counts` and `totals`.
- **Per run.** `__main__.py:308` writes `results["handling"] = run_handling(study, results)`, defined at `experiments.py:466-501`: `totals`, `by_system`, `robustness` and `failed_variants`.
- **Result keys.** These are copied by the walker `collect_result_counts` (`experiments.py:362`) under `RESULT_COUNT_KEYS` (`experiments.py:340-345`).
- **Clip block.** `experiments.py:671-673` writes `clip_sensitivity`.
- **Artefact check.** The checked-in DEV-0 reference `docs/study/pilot_results_v3_dev0_reference.json` (pilot, commit 5b3fd8f) has:
  - `handling.schema = lpcstudy.handling/2`;
  - 27 run-total counters;
  - per system: `cells` (14, each with `counts`, `by_kind`, `denominators`, `lm`, `evaluation`), `oracles`, `fitting`, 139 `result_counts` paths, and `totals`;
  - `clip_sensitivity.status = computed` for all three systems;
  - `failed_variants = 0`.
- **Nonzero there.** `zero_variance_corr` (all three systems), `nu_cap_clips` (all three), `invariant_mean_replacements` and `nu_replacements` = 104, `lm_nonfinite_cost` = 182 and `lm_nonfinite_jacobian` = 104 (Rössler), and `error_clips_plp` = 1 (Chua).

**RESULTS.md.**

- **Handling section.** `report.handling_lines` (`report.py:368`), called at `report.py:1002`, prints the `## Handling` section. It gives the run totals, `failed_variants`, every nonzero counter of every cell, `evaluation`, `fitting` and oracle block with its denominators (`_handling_blocks`, `report.py:348-361`), and every nonzero `result_counts` path, with sentinels labelled.
- **Clip column.** `report.clip_lines` (`report.py:730`) and the `clip` column (`report.py:880`) print the clip block.
- **What I could not check.** No reference RESULTS.md is checked in, so the markdown was checked from the code and from `test_report.py` (for example `:638`), not from an artefact.

## Does each counter name have a test?

- **Names checked:** 41.
  - The 27 run totals.
  - `empty_regime_fallback_by_K`, `failed_variants` and `skipped_variants`.
  - The seven .11b result keys.
  - `n_failed_resamples`, `n_excluded_nonfinite` and `n_km_not_reached`.
  - `error_clips_plp_href` and `error_clips_nonfinite_href`.
- **Result:** every name occurs in `lpcstudy/` and in `tests/unit/`.
- **Value assertions spot-checked (17 names):**
  - `zero_variance_corr_plp == 3`: `test_pipeline.py:262`.
  - `closed_form_floor_a4` and `_a4o`: `test_pipeline.py:497`, `:504`.
  - `regime_target_constant`, `pooled_curvature_floor`, `empty_regime_fallback`, `_chosen` and `_by_K`: `test_pipeline.py:322`, `:505-508`.
  - `curvature_floor == 2` and `decisive_floor == 1`: `test_pipeline.py:292`.
  - `lm_nonfinite_cost` and `lm_nonfinite_jacobian`: `test_pipeline.py:620`.
  - `local_dim_zero_distance`, `oracle_gain_floor` and `oracle_nonfinite`: `test_pipeline.py:503`.
  - `n_km_not_reached`: `test_analysis.py:1874`, `:3174`.
  - `n_covariance_warnings`: `test_analysis.py:3051`.
  - `n_floored`: `test_analysis.py:3094`.
  - `n_constant_states`: `test_analysis.py:3146`.
  - `n_empty_regimes`: `test_analysis.py:3173`.
  - `n_dropped_resamples`: `test_analysis.py:2911-2923`.
  - `skipped_variants`: `test_experiments.py:528`.
  - `gain_replacements` and `gain_floor`: `test_ensemble.py:407`.
- **Limit of this check.** The rest was checked for occurrence only, not read assertion by assertion.

## Verdict of this read

- **Coverage.** Every hit of the full V4 pattern outside `clip_sensitivity.py` is covered by an inventory row at its final status, or is a justified or non-code hit.
- **Gaps.** Inside `clip_sensitivity.py` (report-only, postdating the inventory), two sites are not covered: UNCOVERED-1 (low) and UNCOVERED-2 (very low). Two further uncounted floor sets have justifications available that the code does not state (O-1, O-2).
- **Effect on verdicts.** None of these affects a verdict-bearing quantity.
- **What remains.** DEF-0001 still needs the owner's `/audit freeze` and the owner's code review (freeze-blockers B2). This note does not replace either.

## Classified table (all 257 hits)

| # | Site | Text (trimmed) | Class | Row / reason |
|---|---|---|---|---|
| 1 | `embedding.py:58` | `edges[-1] += 1e-12` | J | L10 (histogram edges for the mutual-information delay; a definition, not data handling) |
| 2 | `embedding.py:59` | `codes = np.clip(np.searchsorted(edges, series, side="right") - 1, 0, n_bins - 1)` | J | L10 (histogram edges for the mutual-information delay; a definition, not data handling) |
| 3 | `__main__.py:54` | `"except one provenance leaf.")` | text | help string ('except') |
| 4 | `__main__.py:227` | `try:` | J | Z: refusal with one stderr line and exit 64 |
| 5 | `__main__.py:232` | `except SeedRefusal as refusal:` | J | Z: refusal with one stderr line and exit 64 |
| 6 | `__main__.py:251` | `try:` | J | Z: refusal with one stderr line and exit 64 |
| 7 | `__main__.py:253` | `except SeedRefusal as refusal:` | J | Z: refusal with one stderr line and exit 64 |
| 8 | `__main__.py:268` | `try:` | J | Z: refusal with one stderr line and exit 64 |
| 9 | `__main__.py:270` | `except ValueError as stale:` | J | Z: refusal with one stderr line and exit 64 |
| 10 | `__main__.py:293` | `log.warning("%d platform probe failure(s) or fallback(s), recorded in the provenance "` | J | Z: probe failures/fallbacks counted and logged (WARNING) and recorded in provenance |
| 11 | `dynamics.py:50` | `return jnp.where(jnp.isfinite(path), path, jnp.inf)` | C | D1 (non-finite path -> +inf; counted downstream as E2 `error_clips_nonfinite`) |
| 12 | `dynamics.py:114` | `logs = np.log(np.maximum(gains[:, :window], 1e-300))` | C | D2 (`gain_floor`, `oracle_gain_floor`, counted in the callers `sanitize_gains` and `state_oracles`) |
| 13 | `allocation.py:58` | `logarithm of the NNLS start is an initial guess, and the ``1e-300`` inside the residual's` | text | docstring |
| 14 | `allocation.py:96` | `start = np.log(np.maximum(coef, 1e-6))` | J | L1 (NNLS start floor: an initial guess; docstring :56-59) |
| 15 | `allocation.py:100` | `return np.log(design @ np.exp(log_coef) + 1e-300) - log_seed` | J | L2 (`+1e-300` in the log cannot bind: every design row is positive; docstring :56-59) |
| 16 | `allocation.py:133` | `nu = np.minimum(nu_hat, nu_cap)` | C | L3 `nu_cap_clips` (counted by `nu_cap_clip_count`, D3 placement in `evaluation`) |
| 17 | `allocation.py:206` | `return delta_sq / np.maximum(eps_sq + delta_sq, 1e-300)` | C | L4 `closed_form_floor_a4`, `_a4o` |
| 18 | `allocation.py:210` | `"""Entries on which the ``1e-300`` floor of :func:`closed_form_weight` binds (DEF-0001).` | text | docstring |
| 19 | `allocation.py:212` | `The floor binds where ``eps^2 + delta^2 < 1e-300``. Under the theory ``eps^2 > 0`` (FW` | text | docstring |
| 20 | `allocation.py:224` | `Number of entries with ``eps_sq + delta_sq < 1e-300``.` | text | docstring |
| 21 | `allocation.py:226` | `return int(np.sum(eps_sq + delta_sq < 1e-300))` | C | L4 counter itself (`closed_form_floor_count`) |
| 22 | `allocation.py:232` | ```features`` takes ``np.minimum(nu_hat, nu_cap)``, which changes exactly the entries with` | text | docstring |
| 23 | `allocation.py:253` | `"""Targets of :func:`fit_regime_tree` whose standard deviation is below its ``1e-12`` g...` | text | docstring |
| 24 | `allocation.py:255` | `The tree standardizes each target by ``std + 1e-12``. A constant target (std 0, or roun...` | text | docstring |
| 25 | `allocation.py:271` | `return int(np.sum(targets.std(axis=0) < 1e-12))` | C | L7 counter itself (`regime_target_constant`) |
| 26 | `allocation.py:275` | `"""Horizons at which a pooled curvature is below the ``1e-300`` floor (A2, regime weigh...` | text | docstring |
| 27 | `allocation.py:292` | `Number of horizons with ``sum c < 1e-300``.` | text | docstring |
| 28 | `allocation.py:296` | `return int(np.sum(denominator < 1e-300))` | C | L6 counter itself (`pooled_floor_count` -> `pooled_curvature_floor`) |
| 29 | `allocation.py:362` | `weight = 1.0 / (1.0 + np.exp(np.clip(diff, -50, 50)))` | J | L5 (`clip(diff, +-50)` before `exp`: overflow guard, changes w by < 2e-22; NaN passes through visibly) |
| 30 | `allocation.py:370` | `return np.clip(numer / np.maximum(denom, 1e-300), 0.0, 1.0)` | C | L6 `pooled_curvature_floor` (A2 pool); clip to [0, 1] is O3/P1 |
| 31 | `allocation.py:397` | ```fallback`` row (A2) and its Kaplan-Meier horizon is NaN (``empty_regime_fallback``).` | text | docstring |
| 32 | `allocation.py:400` | `Number of (regime, horizon) pools whose summed curvature was below the ``1e-300``` | text | docstring |
| 33 | `allocation.py:469` | `targets = (targets - targets.mean(axis=0)) / (targets.std(axis=0) + 1e-12)` | C | L7 `regime_target_constant` |
| 34 | `allocation.py:484` | ```w_S = clip(sum_i b_i / sum_i c_i, 0, 1)`` with ``b_i = E[e_P (e_P - e_C)]`` and` | text | docstring |
| 35 | `allocation.py:487` | ```1e-300`` floor of ``oracle_weight`` (it cannot bind under P1(a), where` | text | docstring |
| 36 | `allocation.py:514` | `return np.clip(numerator / np.maximum(denominator, 1e-300), 0.0, 1.0)` | C | L6 `pooled_curvature_floor` (regime pools, counted at :563); clip to [0, 1] is O3/P1 |
| 37 | `allocation.py:519` | `fallback: np.ndarray) -> RegimeMap:` | C | L8 `empty_regime_fallback` (+ `_by_K`, `_chosen`); `RegimeMap.empty`, KM NaN |
| 38 | `allocation.py:534` | `fallback : np.ndarray` | text | docstring |
| 39 | `allocation.py:546` | `Calibrated regime map; ``empty`` marks the regimes that fell back to ``fallback``` | text | docstring |
| 40 | `allocation.py:554` | `weights = np.tile(fallback, (n_regimes, 1)).astype(float)` | C | L8 `empty_regime_fallback` (+ `_by_K`, `_chosen`); `RegimeMap.empty`, KM NaN |
| 41 | `allocation.py:606` | `best = float(np.mean(np.minimum(moments.sq_cp[:, column], moments.sq_plp[:, column])))` | J | L10 (min of two MSEs: the best-single benchmark, a definition) |
| 42 | `config.py:193` | `if t >= self.threshold_noise_factor * noise - 1e-12)` | J | L10 (float tolerance on a threshold comparison) |
| 43 | `dump.py:15` | `line of this module runs. With it on, ``results.json`` is bitwise the same except one p...` | text | docstring ('except') |
| 44 | `systems.py:78` | `exactly. Its derivative is defined everywhere except the two breakpoints` | text | docstring ('except') |
| 45 | `systems.py:244` | `if bound is None or not (math.isfinite(bound) and bound > 0.0):` | C | D3 -> DEF-0015 (WU-0002.11c, 85531db): diverging or non-finite orbit is REFUSED (`OrbitDivergence`/`ValueError`), not replaced |
| 46 | `systems.py:255` | `size = f"{largest:.17g}" if math.isfinite(largest) else "non-finite"` | C | D3 -> DEF-0015 (WU-0002.11c, 85531db): diverging or non-finite orbit is REFUSED (`OrbitDivergence`/`ValueError`), not replaced |
| 47 | `systems.py:293` | `finite = np.isfinite(states).all(axis=1)` | C | D3 -> DEF-0015 (WU-0002.11c, 85531db): diverging or non-finite orbit is REFUSED (`OrbitDivergence`/`ValueError`), not replaced |
| 48 | `systems.py:343` | `finite = jnp.all(jnp.isfinite(state))` | C | D3 -> DEF-0015 (WU-0002.11c, 85531db): diverging or non-finite orbit is REFUSED (`OrbitDivergence`/`ValueError`), not replaced |
| 49 | `systems.py:344` | `size = jnp.where(finite, jnp.abs(state[0]), jnp.nan) # NaN marks a non-finite state` | C | D3 -> DEF-0015 (WU-0002.11c, 85531db): diverging or non-finite orbit is REFUSED (`OrbitDivergence`/`ValueError`), not replaced |
| 50 | `systems.py:346` | `return jnp.maximum(largest, size), jnp.where((first < 0) & bad, index, first)` | C | D3 -> DEF-0015 (WU-0002.11c, 85531db): diverging or non-finite orbit is REFUSED (`OrbitDivergence`/`ValueError`), not replaced |
| 51 | `data.py:55` | `return np.random.default_rng([seed, zlib.crc32(label)])` | J | R1: this is `make_rng` itself (the only sanctioned generator) |
| 52 | `ensemble.py:55` | `If ``LPC_THREADS`` is set and is not an integer from 1 to 99 (no fallback, PRIME.4).` | text | docstring ('no fallback') |
| 53 | `ensemble.py:114` | `The values are those of the original three lines, in the same order: CP is ``np.clip`` of` | text | docstring of E1-E3 / E5-D2 |
| 54 | `ensemble.py:115` | ```cp - truth``; PLP is ``nan_to_num`` (NaN and +inf to ``+clip``, -inf to ``-clip``) and` | text | docstring of E1-E3 / E5-D2 |
| 55 | `ensemble.py:116` | `then ``np.clip``. A NaN CP error is not clipped (``np.clip`` keeps it) and so is not` | text | docstring of E1-E3 / E5-D2 |
| 56 | `ensemble.py:138` | `cp_err = np.clip(cp_raw, -clip, clip)` | C | E1 `error_clips_cp` |
| 57 | `ensemble.py:139` | `plp_err = np.nan_to_num(plp_raw, nan=clip, posinf=clip, neginf=-clip)` | C | E2 `error_clips_nonfinite` (mask `~finite` at :141) |
| 58 | `ensemble.py:140` | `plp_err = np.clip(plp_err, -clip, clip)` | C | E3 `error_clips_plp` |
| 59 | `ensemble.py:141` | `finite = np.isfinite(plp_raw)` | C | E2/E3 masks (`ClipMasks`) |
| 60 | `ensemble.py:513` | `with np.errstate(divide="ignore", invalid="ignore"):` | C | E4 `zero_variance_corr`, `_cp`, `_plp` (constant rows set to 0 at :516 and counted) |
| 61 | `ensemble.py:794` | `The values are those of the original line, ``np.nan_to_num(gains, nan=1e300, posinf=1e3...` | text | docstring of E1-E3 / E5-D2 |
| 62 | `ensemble.py:797` | ```1e-300`` floor of that logarithm, after the replacement.` | text | docstring of E1-E3 / E5-D2 |
| 63 | `ensemble.py:813` | `replaced = ~np.isfinite(gains).all(axis=1)` | C | E5 `gain_replacements` (`replaced`) |
| 64 | `ensemble.py:814` | `clean = np.nan_to_num(gains, nan=1e300, posinf=1e300)` | C | E5 `gain_replacements` (`replaced`) |
| 65 | `ensemble.py:815` | `floored = (clean[:, :window] < 1e-300).any(axis=1)` | C | D2 `gain_floor` (`floored`) |
| 66 | `seeds.py:59` | `try:` | J | Z: refusal (`SeedRefusal`, exit 64), never a fallback |
| 67 | `seeds.py:61` | `except (OSError, ValueError) as exc:` | J | Z: refusal (`SeedRefusal`, exit 64), never a fallback |
| 68 | `seeds.py:68` | `registry: dict[str, int] = {}` | text | identifier substring ('registry:' matches 'try:') |
| 69 | `seeds.py:75` | `if seed_id in registry:` | text | identifier substring ('registry:' matches 'try:') |
| 70 | `seeds.py:86` | `def resolve_dev_seed(seed_id: str, registry: Mapping[str, int]) -> int:` | text | identifier substring ('registry:' matches 'try:') |
| 71 | `seeds.py:111` | `if seed_id not in registry:` | text | identifier substring ('registry:' matches 'try:') |
| 72 | `seeds.py:141` | `try:` | J | Z: refusal (`SeedRefusal`, exit 64), never a fallback |
| 73 | `seeds.py:144` | `except ImportError as exc:` | J | Z: refusal (`SeedRefusal`, exit 64), never a fallback |
| 74 | `seeds.py:147` | `try:` | J | Z: refusal (`SeedRefusal`, exit 64), never a fallback |
| 75 | `seeds.py:149` | `except OSError as exc:` | J | Z: refusal (`SeedRefusal`, exit 64), never a fallback |
| 76 | `estimation.py:146` | `Handling (DEF-0001, WU-0002.11, WU-0005.4). Inside the refinement, the ``1e-12`` added ...` | text | docstring |
| 77 | `estimation.py:203` | `return jnp.where(jnp.isfinite(value), value, jnp.inf)` | C | S3 `lm_nonfinite_cost` (WU-0005.4, b0c939c; `bad_cost` carry) |
| 78 | `estimation.py:211` | `finite = jnp.isfinite(a_mat)` | C | S4 `lm_nonfinite_jacobian` (`bad_jac` carry) |
| 79 | `estimation.py:212` | `a_mat = jnp.where(finite, a_mat, 0.0)` | C | S4 `lm_nonfinite_jacobian` (`bad_jac` carry) |
| 80 | `estimation.py:215` | `scale = jnp.trace(normal) / dim + 1e-12` | J | S5 (LM damping scale + 1e-12: part of the algorithm) |
| 81 | `estimation.py:220` | `u_new = jnp.where(accept, cand, u)` | J | S6 (LM accept/reject: part of the algorithm) |
| 82 | `estimation.py:221` | `c_new = jnp.where(accept, c_cand, c_u)` | J | S6 (LM accept/reject: part of the algorithm) |
| 83 | `estimation.py:222` | `damping_new = jnp.where(accept, damping / 3.0, damping * 4.0)` | J | S6 (LM accept/reject: part of the algorithm) |
| 84 | `estimation.py:229` | `jnp.where(material, jnp.int32(1), late), k + 1)` | C | late-progress flag of the NVVUQ.10 LM diagnostics (`handling.cells.<id>.lm`), not a replacement |
| 85 | `estimation.py:297` | `The values are those of the original ``estimate``: a non-finite ``nu`` becomes ``1e6`` and` | text | docstring |
| 86 | `estimation.py:325` | `finite_nu = np.isfinite(nu)` | C | S1 `nu_replacements` |
| 87 | `estimation.py:326` | `finite_state = np.isfinite(states)` | C | S2 `invariant_mean_replacements` (replacement at :328) |
| 88 | `estimation.py:327` | `nu = np.where(finite_nu, nu, 1e6)` | C | S1 `nu_replacements` |
| 89 | `estimation.py:420` | `return float(value) if np.isfinite(value) else None` | J | LM summary: a non-finite summary is reported as null (visible); NaN residuals raise at :417 |
| 90 | `provenance.py:113` | `try:` | J | Z: git failure recorded as `git_error` and logged (`__main__.py:281`) |
| 91 | `provenance.py:118` | `except (OSError, RuntimeError, subprocess.SubprocessError) as exc:` | J | Z: git failure recorded as `git_error` and logged (`__main__.py:281`) |
| 92 | `provenance.py:224` | `try:` | J | Z: platform-probe failure recorded in the block's `error` and logged via `probe_errors` (`__main__.py:290-294`); postdates 8fbfa6b (WU-0001.6) |
| 93 | `provenance.py:226` | `except Exception as exc: # noqa: BLE001 (recorded below, never dropped)` | J | Z: platform-probe failure recorded in the block's `error` and logged via `probe_errors` (`__main__.py:290-294`); postdates 8fbfa6b (WU-0001.6) |
| 94 | `provenance.py:243` | `try:` | J | control flow (try the next site-packages root / the next C symbol); the last failure raises and is recorded |
| 95 | `provenance.py:245` | `except ValueError:` | J | control flow (try the next site-packages root / the next C symbol); the last failure raises and is recorded |
| 96 | `provenance.py:263` | `try:` | J | control flow (try the next site-packages root / the next C symbol); the last failure raises and is recorded |
| 97 | `provenance.py:265` | `except AttributeError:` | J | control flow (try the next site-packages root / the next C symbol); the last failure raises and is recorded |
| 98 | `provenance.py:274` | `entry: dict = {"library": _site_relative(path), "corename": None, "config": None,` | text | identifier substring ('entry: dict' matches 'try:') |
| 99 | `provenance.py:276` | `try:` | J | Z: platform-probe failure recorded in the block's `error` and logged via `probe_errors` (`__main__.py:290-294`); postdates 8fbfa6b (WU-0001.6) |
| 100 | `provenance.py:280` | `except Exception as exc: # noqa: BLE001 (recorded in the entry, never dropped)` | J | Z: platform-probe failure recorded in the block's `error` and logged via `probe_errors` (`__main__.py:290-294`); postdates 8fbfa6b (WU-0001.6) |
| 101 | `provenance.py:300` | `try:` | J | Z: platform-probe failure recorded in the block's `error` and logged via `probe_errors` (`__main__.py:290-294`); postdates 8fbfa6b (WU-0001.6) |
| 102 | `provenance.py:302` | `except Exception as exc: # noqa: BLE001 (recorded, never dropped)` | J | Z: platform-probe failure recorded in the block's `error` and logged via `probe_errors` (`__main__.py:290-294`); postdates 8fbfa6b (WU-0001.6) |
| 103 | `provenance.py:315` | `try:` | J | Z: platform-probe failure recorded in the block's `error` and logged via `probe_errors` (`__main__.py:290-294`); postdates 8fbfa6b (WU-0001.6) |
| 104 | `provenance.py:318` | `except Exception as exc: # noqa: BLE001 (recorded, never dropped)` | J | Z: platform-probe failure recorded in the block's `error` and logged via `probe_errors` (`__main__.py:290-294`); postdates 8fbfa6b (WU-0001.6) |
| 105 | `provenance.py:323` | `"""Return one text per failed platform probe and per silent fallback of a block.` | text | docstring of `probe_errors` |
| 106 | `provenance.py:325` | `The caller counts and logs them (a failure or fallback is recorded in the block and never` | text | docstring of `probe_errors` |
| 107 | `provenance.py:326` | `silent, PRIME.4). A failure is a non-null ``error``. A fallback raises nothing but is n...` | text | docstring of `probe_errors` |
| 108 | `provenance.py:375` | `try:` | J | Z: missing package recorded as null and logged (`__main__.py:283-286`) |
| 109 | `provenance.py:377` | `except metadata.PackageNotFoundError:` | J | Z: missing package recorded as null and logged (`__main__.py:283-286`) |
| 110 | `budget.py:36` | `LEVEL_TOLERANCE = 1e-12` | J | equality tolerance of two identical float level expressions (docstring); not data handling; postdates 8fbfa6b |
| 111 | `budget.py:569` | `if half_width is None or not math.isfinite(half_width):` | J | report text: a non-finite half-width/bound is printed as an explicit label ('not estimated', 'bound infinite (A3)', 'not computable'), never a number; postdates 8fbfa6b |
| 112 | `budget.py:653` | `if ci is not None and any(not math.isfinite(float(bound)) for bound in ci):` | J | report text: a non-finite half-width/bound is printed as an explicit label ('not estimated', 'bound infinite (A3)', 'not computable'), never a number; postdates 8fbfa6b |
| 113 | `budget.py:699` | `if not isinstance(entry, dict) or "median_half_width" not in entry:` | text | identifier substring ('entry:' matches 'try:') |
| 114 | `budget.py:745` | `elif not math.isfinite(v4[1]):` | J | report text: a non-finite half-width/bound is printed as an explicit label ('not estimated', 'bound infinite (A3)', 'not computable'), never a number; postdates 8fbfa6b |
| 115 | `budget.py:818` | `if value is None or not math.isfinite(float(value)):` | J | report text: a non-finite half-width/bound is printed as an explicit label ('not estimated', 'bound infinite (A3)', 'not computable'), never a number; postdates 8fbfa6b |
| 116 | `budget.py:870` | `if half_width is None or not math.isfinite(half_width):` | J | report text: a non-finite half-width/bound is printed as an explicit label ('not estimated', 'bound infinite (A3)', 'not computable'), never a number; postdates 8fbfa6b |
| 117 | `budget.py:882` | `finite = half_width is not None and math.isfinite(half_width)` | J | report text: a non-finite half-width/bound is printed as an explicit label ('not estimated', 'bound infinite (A3)', 'not computable'), never a number; postdates 8fbfa6b |
| 118 | `statistics.py:88` | `hazard = np.where(at_risk > 0, deaths / np.maximum(at_risk, 1), 0.0)` | J | T1 (KM hazard 0 with nobody at risk; proof in the docstring, test B4) |
| 119 | `statistics.py:218` | `rng = seed if isinstance(seed, np.random.Generator) else np.random.default_rng(seed)` | J | R1 -> DEF-0011 (WU-0002.14, 4aa16a5): an int seed is still accepted by the API, but every production caller passes `make_rng(...)` (checked: analysis.py, clip_sensitivity.py) |
| 120 | `statistics.py:231` | `yield base[np.minimum(idx, n_items - 1)]` | J | T4 (block index truncation; cannot bind: max start + block - 1 <= n_items - 1, and for block > n_items the `[:n_items]` slice already truncates) |
| 121 | `statistics.py:244` | `"cannot compute" by returning NaN; exceptions are not caught.` | text | docstring |
| 122 | `statistics.py:319` | `failed = ~np.isfinite(resampled)` | C | T4/N9 `n_failed_resamples` (`percentile_interval`, A3 tail) |
| 123 | `statistics.py:448` | `failed = ~np.isfinite(resampled)` | C | N9 `n_failed_resamples` (Monte-Carlo-aware rule; failed -> None, i.e. inconclusive) |
| 124 | `statistics.py:620` | `if not np.isfinite(estimate) or np.isnan(lower) or np.isnan(upper):` | J | verdict 'inconclusive' with reason 'not computable' (DEC-0008 A3): visible |
| 125 | `statistics.py:637` | `resamples are dropped here (``np.nanquantile``), as ``block_bootstrap`` always did, and` | text | docstring |
| 126 | `statistics.py:640` | `dropped by ``np.nanquantile``: it stays in the quantiles and is not counted here. If every` | text | docstring |
| 127 | `statistics.py:669` | `return (float(statistic(np.arange(n_items))), float(np.nanquantile(values, alpha)),` | C | T3 `n_dropped_resamples` (`block_bootstrap_dropped`) |
| 128 | `statistics.py:670` | `float(np.nanquantile(values, 1.0 - alpha)), int(np.isnan(values).sum()))` | C | T3 `n_dropped_resamples` (`block_bootstrap_dropped`) |
| 129 | `statistics.py:680` | `resamples are dropped silently here (``np.nanquantile``); use` | text | docstring |
| 130 | `validation.py:114` | `rng = np.random.default_rng(seed)` | J | Q7/R1: V2 verification fixture with literal seed, docstring says why |
| 131 | `validation.py:160` | `rng = np.random.default_rng(seed)` | J | Q7/R1: V5 verification fixture with literal seed, docstring says why |
| 132 | `validation.py:164` | `durations = np.minimum(np.minimum(event_times, censor_times), horizon_max)` | J | definition of censoring in the V5 fixture (synthetic durations) |
| 133 | `validation.py:458` | `with np.errstate(divide="raise", invalid="raise"):` | J | `errstate(raise)`: the opposite of silencing (P2c check, postdates 8fbfa6b) |
| 134 | `validation.py:461` | `n_consistency = (np.abs(dist_query - dist_tree) > kappa * np.maximum(dist_query, dist_t...` | J | relative-tolerance scale `kappa * max(d1, d2)` in the P2c consistency count (a definition) |
| 135 | `validation.py:502` | `about 1e-12 per draw expected). Tightness: ``N / sqrt(B_M)`` over the states with ``B_M...` | text | docstring |
| 136 | `experiments.py:123` | `# The clip to [0, 1] is the definition of the admissible weight (P1), and 1e-300 the floor` | text | comment (DEF-0001, J) on the V4 weight |
| 137 | `experiments.py:128` | `return np.clip(num / np.maximum(den, 1e-300), 0, 1)` | J | O3 (`experiments.py:89` at 8fbfa6b): clip of w to [0, 1] is the definition (P1); the 1e-300 floor is that of `oracle_weight` (comment at :123) |
| 138 | `experiments.py:189` | `Unused except for its place in the call chain (kept for symmetry with the caller).` | text | docstring |
| 139 | `experiments.py:341` | `"degenerate_fits", "n_covariance_warnings", "n_constant_states", "n_degenerate_pairs",` | C | N9 `RESULT_COUNT_KEYS` (the walker copies the counts into `handling.result_counts`) |
| 140 | `experiments.py:349` | ```n_exponent_at_bound``, ``n_covariance_warnings``, ``n_floored``, ``n_constant_states``,` | text | docstring |
| 141 | `experiments.py:797` | `try:` | C | X1 `failed_variants` (`handling.failed_variants`; logged; entry `{error}`) |
| 142 | `experiments.py:803` | `except Exception as exc: # noqa: BLE001 - a failed variant is reported, not fatal` | C | X1 `failed_variants` (`handling.failed_variants`; logged; entry `{error}`) |
| 143 | `experiments.py:804` | `LOG.exception("variant %s failed", label)` | C | X1 `failed_variants` (`handling.failed_variants`; logged; entry `{error}`) |
| 144 | `clip_sensitivity.py:208` | `usable = bool(np.isfinite(half_width))` | J | flag rule: a non-finite half-width disables only the size clause (docstring :187-191, test t7) |
| 145 | `clip_sensitivity.py:248` | `if not np.isfinite(estimate):` | J | `part_entry`: non-finite T or T2 -> `status = not_computed` with a reason, never a False flag (test `test_part_entry_reports_what_cannot_be_computed...`) |
| 146 | `clip_sensitivity.py:250` | `if estimate_2l is None or interval_2l is None or not np.isfinite(estimate_2l):` | J | `part_entry`: non-finite T or T2 -> `status = not_computed` with a reason, never a False flag (test `test_part_entry_reports_what_cannot_be_computed...`) |
| 147 | `clip_sensitivity.py:285` | `if d.size == 0 or not np.all(np.isfinite(d)) or n_changed < 0:` | J | refusal (ValueError) in `median_bound` |
| 148 | `clip_sensitivity.py:309` | `if not np.isfinite(half_width):` | J | `bound_entry`: non-finite half-width -> `not_computed` with a reason (test `test_bound_entry...`) |
| 149 | `clip_sensitivity.py:403` | ```analysis.h1b_seed_amplifier``'s PLP regression (floor 0): ``y = 0.5 ln max(E e_P^2, 1...` | text | docstring, comment or string |
| 150 | `clip_sensitivity.py:408` | `keep = np.isfinite(x_all) & np.isfinite(0.5 * np.log(np.maximum(sq_plp, 1e-12)))` | U | UNCOVERED-1 (see below) |
| 151 | `clip_sensitivity.py:409` | `y_2 = 0.5 * np.log(np.maximum(sq_plp_2, 1e-12))` | U | UNCOVERED-1 (see below) |
| 152 | `clip_sensitivity.py:410` | `if not np.array_equal(keep, np.isfinite(x_all) & np.isfinite(y_2)):` | J | a change of the regression state set under P2 -> `not_computed` with a reason |
| 153 | `clip_sensitivity.py:502` | `"""Every part not computed, with ``reason`` (the block-level fallback)."""` | text | docstring, comment or string |
| 154 | `clip_sensitivity.py:564` | `block: **any** exception inside it is caught and recorded (``status = "not_computed"``,` | text | docstring, comment or string |
| 155 | `clip_sensitivity.py:565` | ```reason = "error: <repr>"``, ``LOG.exception``), so that a defect here can never end a...` | text | docstring, comment or string |
| 156 | `clip_sensitivity.py:568` | `try:` | J | block-level broad except: recorded (`status`, `reason` in results.json), LOG.exception, WARNING by `log_flags`, 'not computed (reason)' in RESULTS.md; tested (`test_an_exception_inside_the_block_is_recorded_not_raised`). Not an inventory row (module postdates 8fbfa6b) |
| 157 | `clip_sensitivity.py:570` | `except Exception as exc: # noqa: BLE001 - report-only block: recorded and logged, never...` | J | block-level broad except: recorded (`status`, `reason` in results.json), LOG.exception, WARNING by `log_flags`, 'not computed (reason)' in RESULTS.md; tested (`test_an_exception_inside_the_block_is_recorded_not_raised`). Not an inventory row (module postdates 8fbfa6b) |
| 158 | `clip_sensitivity.py:571` | `LOG.exception("clip sensitivity: block not computed: %r", exc)` | J | block-level broad except: recorded (`status`, `reason` in results.json), LOG.exception, WARNING by `log_flags`, 'not computed (reason)' in RESULTS.md; tested (`test_an_exception_inside_the_block_is_recorded_not_raised`). Not an inventory row (module postdates 8fbfa6b) |
| 159 | `clip_sensitivity.py:577` | `try:` | U | UNCOVERED-2 (see below) |
| 160 | `clip_sensitivity.py:579` | `except Exception: # noqa: BLE001 - malformed results: no parts to list, the reason stays` | U | UNCOVERED-2 (see below) |
| 161 | `clip_sensitivity.py:607` | `try:` | J | `_BaselineMismatch` -> `_failed(reason)`: recorded, WARNING by `log_flags`; tested (`test_missing_arrays_and_a_baseline...`) |
| 162 | `clip_sensitivity.py:610` | `except _BaselineMismatch as exc:` | J | `_BaselineMismatch` -> `_failed(reason)`: recorded, WARNING by `log_flags`; tested (`test_missing_arrays_and_a_baseline...`) |
| 163 | `clip_sensitivity.py:617` | `try:` | J | per-criterion broad except: LOG.exception, parts `not_computed` with 'error: <repr>' in results.json and RESULTS.md. No direct test of this path (observation O-3) |
| 164 | `clip_sensitivity.py:619` | `except Exception as exc: # noqa: BLE001 - a flag that cannot be computed is reported, n...` | J | per-criterion broad except: LOG.exception, parts `not_computed` with 'error: <repr>' in results.json and RESULTS.md. No direct test of this path (observation O-3) |
| 165 | `clip_sensitivity.py:620` | `LOG.exception("clip sensitivity: %s", exc)` | J | per-criterion broad except: LOG.exception, parts `not_computed` with 'error: <repr>' in results.json and RESULTS.md. No direct test of this path (observation O-3) |
| 166 | `clip_sensitivity.py:653` | `# a regime with no calibration member takes the fallback A2' (the construction oracle)` | text | docstring, comment or string |
| 167 | `clip_sensitivity.py:657` | `empty_used = bool(empty[regime_test].any()) # some test draw is scored with the fallback` | C | L8: mirrors `calibrate_regimes`' empty-regime fallback; the baseline is checked bitwise against `rmap.weights` and `rmap.empty` (:655, :670); `empty_used` enters the counts and the H3a invariance |
| 168 | `clip_sensitivity.py:659` | `def regime_weights(fallback: np.ndarray, moments: EnsembleMoments) -> np.ndarray:` | C | L8: mirrors `calibrate_regimes`' empty-regime fallback; the baseline is checked bitwise against `rmap.weights` and `rmap.empty` (:655, :670); `empty_used` enters the counts and the H3a invariance |
| 169 | `clip_sensitivity.py:660` | `# The weights of calibrate_regimes: an empty regime keeps the fallback, others regime_w...` | C | L8: mirrors `calibrate_regimes`' empty-regime fallback; the baseline is checked bitwise against `rmap.weights` and `rmap.empty` (:655, :670); `empty_used` enters the counts and the H3a invariance |
| 170 | `clip_sensitivity.py:661` | `table = np.tile(fallback, (rmap.n_regimes, 1)).astype(float)` | C | L8: mirrors `calibrate_regimes`' empty-regime fallback; the baseline is checked bitwise against `rmap.weights` and `rmap.empty` (:655, :670); `empty_used` enters the counts and the H3a invariance |
| 171 | `clip_sensitivity.py:805` | `"construction_oracle": ("construction oracle", "; A2 fallback of an empty regime")}` | text | docstring, comment or string |
| 172 | `clip_sensitivity.py:860` | `if not np.all(np.isfinite(diff)):` | J | non-finite per-state correlation -> `not_computed` with a reason |
| 173 | `clip_sensitivity.py:870` | `def part_state(entry: dict) -> str:` | text | identifier substring ('entry:' matches 'try:') |
| 174 | `oracle.py:37` | `below the ``1e-300`` floor of ``local_dimension``; a gain below that floor in the window;` | text | docstring |
| 175 | `oracle.py:59` | `A neighbour at distance below ``1e-300`` (an exact duplicate of the query in the refere...` | text | docstring |
| 176 | `oracle.py:60` | `which the contract excludes) is floored to ``1e-300`` before the logarithm. The dimension` | text | docstring |
| 177 | `oracle.py:77` | `Boolean ``(n,)``: at least one of the ``k`` neighbour distances was below ``1e-300``.` | text | docstring |
| 178 | `oracle.py:80` | `floored = (dist < 1e-300).any(axis=1)` | C | O1 `local_dim_zero_distance` |
| 179 | `oracle.py:81` | `dist = np.maximum(dist, 1e-300)` | C | O1 `local_dim_zero_distance` |
| 180 | `oracle.py:196` | ```oracle_gain_floor`` marks a state with a gain below the ``1e-300`` floor of` | text | docstring |
| 181 | `oracle.py:217` | `floor = (gains[:, :window] < 1e-300).any(axis=1)` | C | D2 `oracle_gain_floor` |
| 182 | `oracle.py:218` | `nonfinite = ~np.isfinite(nu) \| ~np.isfinite(gains).all(axis=1)` | C | O5 `oracle_nonfinite` (not replaced; NaN propagates) |
| 183 | `oracle.py:243` | `raw = (moments.sq_plp - moments.cross) / np.maximum(curv, 1e-300)` | C | O2 `curvature_floor` (derived from the moments in `pipeline.py:451`) |
| 184 | `oracle.py:244` | `return np.clip(raw, 0.0, 1.0) if clip else raw` | J | O3 (clip of w* to [0, 1]: the definition, P1; `n_w_zero`/`n_w_one` in H2a) |
| 185 | `oracle.py:278` | ```w* = clip(u, 0, 1)``, hence` | text | docstring |
| 186 | `oracle.py:291` | ```1e-300`` floor of ``oracle_weight``); the entries with ``c < 1e-300`` are counted as` | text | docstring |
| 187 | `oracle.py:323` | `optimum = np.clip(unclipped, 0.0, 1.0)` | J | O3 (clip of w* to [0, 1]: the definition, P1; `n_w_zero`/`n_w_one` in H2a) |
| 188 | `report.py:126` | `try:` | J | refusal of a pre-v3 results file (ValueError re-raised with the reason) |
| 189 | `report.py:128` | `except ValueError as stale:` | J | refusal of a pre-v3 results file (ValueError re-raised with the reason) |
| 190 | `report.py:321` | `except ``config``, then the full configuration as JSON in a ``<details>`` block.` | text | docstring |
| 191 | `report.py:345` | `error floors only below 1e-12, which is unreachable for rho >= 0.005)."""` | text | docstring |
| 192 | `report.py:377` | `the ``handling`` block existed get one line saying so, never an exception.` | text | docstring |
| 193 | `report.py:599` | `exception. Needs owner review before freeze.` | text | docstring |
| 194 | `report.py:663` | `def _parts_text(entry: dict) -> str:` | text | identifier substring ('entry:' matches 'try:') |
| 195 | `analysis.py:24` | `import warnings` | J | import of `warnings` for the N2 counter |
| 196 | `analysis.py:82` | `resamples that ``np.nanquantile`` dropped (DEF-0001, row T3).` | text | docstring |
| 197 | `analysis.py:151` | `bad = ~np.all(np.isfinite(deltas) & (deltas > 0), axis=1) \| ~(np.isfinite(nu) & (nu > 0))` | C | N1/N9 V7 `n_nonfinite` (bad states -> NaN, `pass` false); plus `V7.invariant_mean_replacements` for the upstream S2 replacement |
| 198 | `analysis.py:224` | `fewer, as in the smoke preset); the caller counts those warnings (``n_covariance_warnin...` | text | docstring |
| 199 | `analysis.py:228` | `try:` | C | N2 (curve_fit RuntimeError -> NaN -> failed resample, `n_failed_resamples`) |
| 200 | `analysis.py:232` | `except RuntimeError:` | C | N2 (curve_fit RuntimeError -> NaN -> failed resample, `n_failed_resamples`) |
| 201 | `analysis.py:239` | `return bool(np.isfinite(two_over_d)` | C | N3 `n_exponent_at_bound` (`_at_bound`) |
| 202 | `analysis.py:245` | `"""``[ratio, fitted 1/d, floor f^2, at bound, n warnings]`` of the median fit on ``rows``.` | text | docstring |
| 203 | `analysis.py:255` | `number of ``OptimizeWarning`` the fit emitted. The fit runs under ``catch_warnings(reco...` | text | docstring |
| 204 | `analysis.py:261` | `n_warnings = 0` | C | N2 `n_covariance_warnings` (OptimizeWarning counted; every other warning re-issued) |
| 205 | `analysis.py:262` | `if np.all(np.isfinite(medians) & (medians > 0)):` | C | N2 (non-finite medians or ValueError -> NaN -> failed resample, `n_failed_resamples`) |
| 206 | `analysis.py:263` | `try:` | C | N2 (non-finite medians or ValueError -> NaN -> failed resample, `n_failed_resamples`) |
| 207 | `analysis.py:264` | `with warnings.catch_warnings(record=True) as caught:` | C | N2 `n_covariance_warnings` (OptimizeWarning counted; every other warning re-issued) |
| 208 | `analysis.py:265` | `warnings.simplefilter("always")` | C | N2 `n_covariance_warnings` (OptimizeWarning counted; every other warning re-issued) |
| 209 | `analysis.py:267` | `except ValueError:` | C | N2 (non-finite medians or ValueError -> NaN -> failed resample, `n_failed_resamples`) |
| 210 | `analysis.py:271` | `n_warnings += 1` | C | N2 `n_covariance_warnings` (OptimizeWarning counted; every other warning re-issued) |
| 211 | `analysis.py:273` | `warnings.warn_explicit(note.message, note.category, note.filename, note.lineno,` | C | N2 `n_covariance_warnings` (OptimizeWarning counted; every other warning re-issued) |
| 212 | `analysis.py:277` | `ratio = fitted / reference if np.isfinite(fitted) and reference > 0 else float("nan")` | C | N2/N3: NaN ratio -> failed resample; the two count columns |
| 213 | `analysis.py:278` | `return np.array([ratio, fitted, floor_sq, float(_at_bound(two_over_d)), float(n_warning...` | C | N2/N3: NaN ratio -> failed resample; the two count columns |
| 214 | `analysis.py:353` | ```n_covariance_warnings`` (each ``{point, resamples}``: the fits whose ``2/d`` is at a ...` | text | docstring |
| 215 | `analysis.py:380` | `finite = np.isfinite(inverse_all)` | C | N9 H1a `n_excluded_nonfinite` |
| 216 | `analysis.py:385` | `finite &= np.all(np.isfinite(sq), axis=1)` | C | N9 H1a `n_excluded_nonfinite` |
| 217 | `analysis.py:420` | `"n_covariance_warnings": {"point": int(point[4]),` | C | N2 `n_covariance_warnings` (result key) |
| 218 | `analysis.py:444` | `The squared error enters as ``max(E e^2 - floor, 1e-12)``; a regression state where the...` | text | docstring |
| 219 | `analysis.py:445` | `binds (``E e^2 - floor < 1e-12``, so ``y`` is pinned at ``0.5 ln 1e-12 = -13.8``, a` | text | docstring |
| 220 | `analysis.py:479` | `y_all = 0.5 * np.log(np.maximum(sq - floor, 1e-12))` | C | N4 `H1b.<CP|PLP>.n_floored` |
| 221 | `analysis.py:480` | `keep = np.isfinite(x_all) & np.isfinite(y_all) # excluded and counted (DEC-0008 A3)` | C | N9 H1b `n_excluded_nonfinite` |
| 222 | `analysis.py:483` | `n_floored = int(((sq - floor) < 1e-12)[keep].sum()) # the floor binds: y = -13.8` | C | N4 `H1b.<CP|PLP>.n_floored` |
| 223 | `analysis.py:548` | `finite = np.isfinite(values)` | C | N5/N9 H1c `n_excluded_nonfinite` |
| 224 | `analysis.py:683` | `keep = np.isfinite(proxy) & np.isfinite(oracle)` | C | N9 H1d `n_excluded_nonfinite` |
| 225 | `analysis.py:927` | `if not np.all(np.isfinite(weight)) or weight.min() < 0.0 or weight.max() > 1.0:` | J | refusal: non-finite input raises ValueError (no replacement) |
| 226 | `analysis.py:1095` | `if x.ndim != 2 or x.shape[1] != 2 or not np.all(np.isfinite(x)):` | J | refusal: non-finite input raises ValueError (no replacement) |
| 227 | `analysis.py:1110` | `with np.errstate(invalid="ignore", divide="ignore"):` | C | T4: partial correlation NaN -> failed resample, `n_failed_resamples` |
| 228 | `analysis.py:1166` | `if not np.all(np.isfinite(w_arr)):` | J | refusal: non-finite input raises ValueError (no replacement) |
| 229 | `analysis.py:1261` | `if not np.all(np.isfinite(weight)) or weight.min() < 0.0 or weight.max() > 1.0:` | J | refusal: non-finite input raises ValueError (no replacement) |
| 230 | `analysis.py:1382` | `return (np.where(denom > 0, ranks_c @ lev_c / np.maximum(denom, 1e-300), 0.0),` | C | N6 `H2b.noise.n_constant_states`; the 1e-300 floor cannot bind: ranks are multiples of 1/2, so denom > 0 implies denom of order 0.1 or more |
| 231 | `analysis.py:1650` | `"n_nonfinite": int((~np.isfinite(corr[(rho, n)])).sum()),` | C | N9 H2e `n_nonfinite` |
| 232 | `analysis.py:1726` | `if not all(np.isfinite(v) for v in calibration_mse.values()):` | J | refusal: non-finite input raises ValueError (no replacement) |
| 233 | `analysis.py:1831` | `better = np.maximum(t_cp, t_plp)` | J | N8 (masked max; index clip on rows excluded by the screens and counted in `n_screened_out`) |
| 234 | `analysis.py:1832` | `col = np.clip(better - 1, 0, len(m.horizons) - 1)` | J | N8 (masked max; index clip on rows excluded by the screens and counted in `n_screened_out`) |
| 235 | `analysis.py:1854` | `return float(value) if np.isfinite(value) else None` | J | N8 (a degenerate fit is reported as null: visible) |
| 236 | `analysis.py:1930` | `order = np.argsort(np.nan_to_num(horizons_km, nan=np.inf), kind="stable")` | C | N7 (`n_km_not_reached`, `H3a.n_empty_regimes`; NaN horizons ordered last) |
| 237 | `networks.py:190` | `out_scale = targets[train_idx].std(axis=0) + 1e-12` | J | L10 (standardization guard `std + 1e-12` of the training targets) |
| 238 | `pipeline.py:419` | `* ``curvature_floor``: entries with ``c = E[(e_C - e_P)^2] < 1e-300`` (the expression of` | text | docstring |
| 239 | `pipeline.py:422` | `* ``decisive_floor``: states with ``E[e_P^2] < 1e-300`` at ``H_ref`` (the floor of the` | text | docstring |
| 240 | `pipeline.py:451` | `"curvature_floor": int((curvature(moments) < 1e-300).sum()),` | C | O2 counter `curvature_floor` |
| 241 | `pipeline.py:452` | `"decisive_floor": int((moments.sq_plp[:, where[0]] < 1e-300).sum())}` | C | P1 counter `decisive_floor` |
| 242 | `pipeline.py:511` | `"empty_regime_fallback", "empty_regime_fallback_chosen", "pooled_curvature_floor",` | C | L8/L6 counter plumbing (`FIT_COUNTERS`, `fit_counters`, denominators, record) |
| 243 | `pipeline.py:513` | `"""Scalar counters of one ``fit_rules`` call; ``empty_regime_fallback_by_K`` (a dict ke...` | text | docstring |
| 244 | `pipeline.py:521` | `* ``empty_regime_fallback``: (K, regime) pairs with no calibration (state, draw), summe...` | text | docstring |
| 245 | `pipeline.py:522` | `all fitted ``K``, with ``empty_regime_fallback_by_K`` and the count at the chosen ``K``` | text | docstring |
| 246 | `pipeline.py:523` | `(``empty_regime_fallback_chosen``: only the chosen ``K`` reaches A5 and H3).` | text | docstring |
| 247 | `pipeline.py:525` | `curvature was below ``1e-300`` at some horizon (summed over horizons).` | text | docstring |
| 248 | `pipeline.py:542` | `The counters of ``FIT_COUNTERS`` and ``empty_regime_fallback_by_K``.` | text | docstring |
| 249 | `pipeline.py:545` | `return {"empty_regime_fallback": sum(by_k.values()), "empty_regime_fallback_by_K": by_k,` | C | L8/L6 counter plumbing (`FIT_COUNTERS`, `fit_counters`, denominators, record) |
| 250 | `pipeline.py:546` | `"empty_regime_fallback_chosen": by_k[str(chosen)],` | C | L8/L6 counter plumbing (`FIT_COUNTERS`, `fit_counters`, denominators, record) |
| 251 | `pipeline.py:593` | `"empty_regime_fallback": "regimes", "empty_regime_fallback_chosen": "chosen_regimes",` | C | L8/L6 counter plumbing (`FIT_COUNTERS`, `fit_counters`, denominators, record) |
| 252 | `pipeline.py:808` | `binds (``eps_hat^2 + delta_hat^2 < 1e-300``); ``closed_form_floor_a4o``: test states with` | text | docstring |
| 253 | `pipeline.py:835` | `"empty_regime_fallback_by_K": dict(rules.handled["empty_regime_fallback_by_K"]),` | C | L8/L6 counter plumbing (`FIT_COUNTERS`, `fit_counters`, denominators, record) |
| 254 | `pipeline.py:842` | `return {"counts": dict.fromkeys(FIT_COUNTERS, 0), "empty_regime_fallback_by_K": {},` | C | L8/L6 counter plumbing (`FIT_COUNTERS`, `fit_counters`, denominators, record) |
| 255 | `pipeline.py:895` | `if not np.isfinite(value) or value < 0.0:` | J | refusal: a non-finite or negative excess MSE raises (no fallback K) |
| 256 | `pipeline.py:1066` | `decisive_ratio = np.sqrt(moments.sq_cp[:, ref] / np.maximum(moments.sq_plp[:, ref],` | C | P1 `decisive_floor` |
| 257 | `pipeline.py:1067` | `1e-300))` | C | P1 `decisive_floor` |
