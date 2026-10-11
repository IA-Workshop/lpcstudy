# Defects

Append-only (PRIME.5). To change an entry's status, add a dated status line under it; never edit the original text (LPC.PC.14).

**Blocking** means the defect blocks the freeze and any reporting of the results it affects. **Tracked** means it is resolved on the stated schedule or reported as a known limitation (INTPR.10).

---

**DEF-0001: Silent handling of bad values is not counted or reported** (PRIME.4, LPC.PC.21d)

- **Blocking:** yes, before the freeze.
- **Affects:** every run.
- **Description.** These cases are documented in Methods v2 but not counted per run in `results.json`:
  - non-finite state estimates replaced by the invariant mean;
  - forecast errors clipped at 10 σ_x;
  - the regime-count fallback.
- **Resolution:** WU-0002, item 11.
- 2026-10-10: opened (Claude).
- 2026-10-10 (claude-sonnet-5-5, main session, on the WU-0013.2 reviewer's finding R3; both sites checked): two further silent cases that WU-0002.11 must count and report: `lpcstudy/statistics.py:61` (`kaplan_meier` sets the hazard to 0 where no subject is at risk) and `lpcstudy/statistics.py:95-96` (`logrank_test` returns p = 1.0 when the variance is not positive). Both feed H3a. Any fix is statistics code and needs owner review before the freeze.
- 2026-10-10 (claude-sonnet-5-5, main session, on the WU-0005 reviewer's observation; checked): a third uncounted silent case for WU-0002.11: `lpcstudy/oracle.py:62` (`local_dimension`) clamps zero neighbour distances with `np.maximum(dist, 1e-300)` (duplicate library points) without counting them.
- 2026-10-11 (claude-sonnet-5-5, on the WU-0002.10 reviewer's finding R4): V7's `n_nonfinite` counts non-finite or non-positive delta and nu, but `ParametricEstimator.estimate` (`lpcstudy/estimation.py:141-142`) replaces non-finite estimates with the state mean upstream, so `n_nonfinite` is 0 in real runs and 0 does not mean nothing diverged. WU-0002.11 must report the replacement count beside V7.
- 2026-10-11 (claude-sonnet-5-5, on the WU-0002.3 reviewer's finding R3): the K-choice fallback this defect lists (to K = 5 when no K is within 5% of best-single) was removed by WU-0002.3 (the rule now picks the smallest K within 5% of the minimum excess). Still uncounted and to be counted in WU-0002.11: the `1e-300` floors at `lpcstudy/oracle.py:131` and `lpcstudy/allocation.py:368` (deferred by WU-0002.3) and the empty-leaf weight fallback at `lpcstudy/allocation.py:404-405`.
- 2026-10-11 (claude-sonnet-5-5, on the WU-0002.4/.5 phase-2 reviewer's finding R4): further silent handling for WU-0002.11 to count and report: the 2/d bounds [0.01, 10] clip in the H1a fit (a resample hitting a bound gives an extreme ratio that is not counted); the H1b CP interval uses `block_bootstrap`, which drops non-finite resamples without counting them (reported only, no pass); and the existing `np.maximum(..., 1e-12)` in H1b.

**DEF-0002: Excess MSE uses c(w − w\*)² with clipped w\*** (VV.1)

- **Blocking:** yes.
- **Affects:** regret ratios, the K choice, the H3 statistics.
- **Description.** The formula understates the excess error for states where w\* is clipped (Methods v2 §M13, item 7).
- **Resolution:** WU-0002, item 2.
- 2026-10-10: opened (Claude).

**DEF-0003: Regime weight is the curvature-weighted mean of clipped w\*, not the optimum** (Theorem P3a)

- **Blocking:** yes.
- **Affects:** A5 and H3c.
- **Resolution:** WU-0002, item 2.
- 2026-10-10: opened (Claude).

**DEF-0004: Missing intervals for some tested statistics** (VV.3, v3 §7)

- **Blocking:** yes.
- **Affects:** H1d proxy correlations (v2 H1e) and H3c MSE ratio (v2 H3d), which have no bootstrap interval.
- **Resolution:** WU-0002, items 3 and 6.
- 2026-10-10: opened (Claude).

**DEF-0005: Hypothesis identifiers and criteria in code follow v1/v2, not v3** (INTPR.3)

- **Blocking:** yes.
- **Affects:** the report, figures and verdicts.
- **Resolution:** WU-0002, items 3–10.
- 2026-10-10: opened (Claude).

**DEF-0006: Outputs carry no provenance block** (REPRO.4)

- **Blocking:** yes.
- **Affects:** every output. Missing: seed id, commit, environment, device.
- **Resolution:** WU-0001.
- 2026-10-10: opened (Claude).

**DEF-0007: Tests not yet audited for regression guards versus reference tests** (VV.7, LPC.PC.21a)

- **Blocking:** yes, before the freeze.
- **Affects:** correctness evidence.
- **Description.** Some of the 14 v1 tests may compare against the code's own output. Each test must be labeled with its reference, or as a regression guard.
- **Resolution:** a unit before the freeze.
- 2026-10-10: opened (Claude).
- 2026-10-10 **resolved** (claude-sonnet-5-5, main session): WU-0013 audited all 14 tests (`docs/agent/records/audits/2026-10-10-def-0007-tests.md`: 13 reference, 1 defective) and fixed them (merged; merge gate 78 passed; independent review approved). Every test now names its reference and justifies its tolerances; the defective test is now a regression guard with three independent tests beside it. Open follow-up, not a reopening: the AMI delay band is uncited (needs the researcher).

**DEF-0008: N̂ does not estimate N without bias** (INTPR.10)

- **Blocking:** no (tracked).
- **Affects:** H1d's N̂ row and the deployable Q-N.
- **Description.** N̂ perturbs the noisy query, not the clean one.
- **Schedule:** reported as a known limitation in v3 §8. A fix is future work.
- 2026-10-10: opened (Claude).

**DEF-0009: Bootstrap-interval stability under doubled thinning not checked** (Methods v2 §M16)

- **Blocking:** no (tracked).
- **Schedule:** future work, reported as a limitation.
- 2026-10-10: opened (Claude).

**DEF-0010: Registered seeds of 2³² or more crash scikit-learn calls that take `config.seed` as `random_state`** (PRIME.4, LPC.PC.7)

- **Blocking:** yes. Blocks WU-0003 (the DEV-1 rehearsal) and the confirmatory run.
- **Affects:** runs on DEV-1 to DEV-4 (their registered values are all at least 2³²) and on any 62-bit confirmatory seed. DEV-0 (20261005) is unaffected, which is why the pilot and the baseline smoke run did not show it.
- **Description.** scikit-learn accepts `random_state` only in [0, 2³² − 1]. `check_random_state(2844678021587022684)` raises `ValueError: Seed must be between 0 and 2**32 - 1` (verified in the project venv by the main session, 2026-10-10). The code passes `config.seed` directly at `lpcstudy/analysis.py:295`, `:678`, `:680` and `lpcstudy/allocation.py:358`. Found by the WU-0001 planner while planning WU-0001.1; no test catches it, because every test and the smoke preset use DEV-0.
- **Resolution:** a fix in WU-0002 (a plan item to be added by amendment). It changes the random streams of every scikit-learn call, so it changes numbers for every seed unless the derivation keeps `config.seed` unchanged below 2³². The choice between "derive a 32-bit value with `make_rng(seed, label)` for all seeds" and "leave seeds below 2³² untouched" affects the WU-0002.12 regression against the pilot and is the owner's to rule on. Until then, only DEV-0 can be run.
- 2026-10-10: opened (claude-sonnet-5-5, main session).
- 2026-10-11 (claude-sonnet-5-5, recording the owner's ruling, DEC-0008 B): fix = option B: the raw seed below 2**32, a derived 32-bit value from `make_rng(seed, "sklearn", label)` otherwise; planned in WU-0002 with the `random_state` sites of `analysis.py` and `allocation.py`.

**DEF-0011: Reference pool for the 1/d estimate is drawn with a fixed literal seed, outside `make_rng`** (LPC.PC.21, CLAUDE.md "Randomness only via `lpcstudy.data.make_rng`")

- **Blocking:** no (tracked). To be ruled on by the owner before the freeze, because fixing it changes numbers.
- **Affects:** every run: the pool of up to 2×10⁴ library states used for the 1/d reference is the same for every seed id.
- **Description.** `lpcstudy/oracle.py:101` has `rng = np.random.default_rng(0)` and draws the pool with `rng.choice`. Found by the WU-0014 reviewer (who cited line 99; checked by the main session at line 101). A grep also shows other `np.random.default_rng(...)` calls that take a seed directly instead of `make_rng(seed, *labels)`: `dynamics.py:147`, `validation.py:107` and `:147`, `statistics.py:151`, `networks.py:145`, `experiments.py:88`. Whether those derive correctly from the study seed has not been audited here.
- **Resolution:** to be planned in WU-0002 (the owner decides whether the pool should depend on the seed id; the pilot used the fixed pool, so a change affects the WU-0002.12 regression).
- 2026-10-10: opened (claude-sonnet-5-5, main session, on the WU-0014 reviewer's finding).
- 2026-10-11 (claude-sonnet-5-5, recording the owner's ruling, DEC-0008 B): option 1: keep until the WU-0002.12 regression, then route through `make_rng(config.seed, "oracle-pool")`; audit the other `default_rng` sites in WU-0002.11.
- 2026-10-11 (claude-sonnet-5-5, on the WU-0002.10 reviewer's finding R3): add to the WU-0002.11 audit list the new report-only V7 interval seeds `config.seed + 7000 + i` (`analysis.py`, WU-0002.10), another integer-salt seed that bypasses `make_rng` (DEC-0012 convention: existing integer salts are not converted until the audit decides).

**DEF-0012: k-d tree queries use all cores and ignore the `LPC_THREADS` cap** (RSRC.11, RSRC.12; `.claude/rules/test-discipline.md` "Device and threads")

- **Blocking:** no (tracked).
- **Affects:** every run and every test that builds an analog search or a Levina–Bickel estimate; on a shared machine the thread budget (`LPC_THREADS`, default 4) is not honored.
- **Description.** `lpcstudy/ensemble.py:110` and `lpcstudy/oracle.py:61` call `cKDTree.query(..., workers=-1)`, which uses every core. The `OMP_NUM_THREADS`, `MKL_NUM_THREADS` and `OPENBLAS_NUM_THREADS` caps set by the wrappers do not apply to scipy's own worker threads. Found by the WU-0005 planner; both sites checked by the main session.
- **Resolution:** pass the `LPC_THREADS` value as `workers`. This does not change any number (a query's result does not depend on the worker count); a test can pin that. To be done in a small unit after WU-0002.1 and .2 (it touches `ensemble.py` and `oracle.py`).
- 2026-10-10: opened (claude-sonnet-5-5, main session).
- 2026-10-11 (claude-sonnet-5-5, recording the owner's ruling, DEC-0008 B): pass `LPC_THREADS` as `workers`; a small unit after WU-0002.1 and .2 (done); no numbers change.

**DEF-0013: Regime ordering uses a default (unstable) `argsort`; tie order depends on the CPU** (LPC.PC.18, REPRO)

- **Blocking:** no (tracked); fixed inside WU-0002.8.
- **Affects:** H3a (the pairs of consecutive regimes tested) and anything downstream of the A5 regime ordering when two regimes have equal horizons or when NaN horizons are mapped to infinity and tie.
- **Description.** `lpcstudy/analysis.py:613` orders regimes with `np.argsort(np.nan_to_num(rmap.horizons_km, nan=np.inf))`. NumPy's default sort is not stable and its tie order depends on the CPU's vector instructions: the WU-0002.7/.8 mathematician measured that the default `argsort` differs from `kind="stable"` on tied arrays in 19,534 of 30,000 trials on this machine. With integer Kaplan–Meier medians and NaN to infinity, ties are realistic, so the pairs tested could differ between machines. The pilot was produced on different hardware; a mismatch in H3a at the WU-0002.12 regression is a candidate explanation. The other sort-order-dependent sites in `lpcstudy/` were checked by the main session: `statistics.py:114` (`holm_adjust`) gives identical adjusted values to tied p-values under either order; `np.searchsorted` and `np.unique` are deterministic.
- **Resolution:** WU-0002.8 rewrites this ordering with `kind="stable"` and tie order by regime index (confirmed by the applied-mathematician); a test pins it with tied horizons.
- 2026-10-11: opened (claude-sonnet-5-5, main session, on the WU-0002.7/.8 mathematician's finding M6).

**DEF-0014: The V7 estimator-efficiency check fails at the smoke preset sizes, so the validation gate is false on every smoke run** (VV.3, NVVUQ.20; found while implementing WU-0002.10)

- **Blocking:** no for plumbing; to be ruled on by the owner (referral in `docs/agent/records/work/WU-0002.10-v7.md`) before any rule is written that treats `gate_pass` at smoke as meaningful.
- **Affects:** the smoke preset only (tests, `RESULTS.md` header of smoke runs, the WU-0001.5 / WU-0002.x regression style comparisons that include `gate_pass`). Pilot and full sizes are not yet measured with V7.
- **Description.** On DEV-0 at the smoke preset, V7's median per-state slope of ln delta on ln rho is 1.00072 (inside [0.9, 1.1]) and the median efficiency delta/(rho nu) is 1.0960 at rho = 1% (inside) and 5.8535 at rho = 2% (outside), so `V7.pass` and `gate_pass` are false. The applied-mathematician's analysis (Log of the unit) shows the estimators are sound and that sampling error (SD about 0.02 at smoke size) is not the cause; the cause is the untrained estimator network at smoke size (validation loss 1.73, against 0.0025 in the pilot), which puts many states in the wrong basin. The earlier v1 smoke run already had the same V7 values under the v1 key `H1a`, but the v1 gate did not include V7, so `gate_pass` was true.
- **Resolution:** pending the owner's ruling (options in the referral). No threshold, sample size or training setting was changed (tuning is excluded by the plan and by PRIME.2).
- 2026-10-11: opened (claude-sonnet-5-5, main session).

**DEF-0015: `estimate_lyapunov` returns a finite, positive, plausible value for orbits that diverge** (PRIME.4, LPC.PC.21d)

- **Blocking:** to be ruled on by the owner (it can silently corrupt a Lyapunov time, and the Lyapunov time sets the spacing, the sampling interval and the time unit of the whole study); the pilot's own values come from the registry start states, which are inside the basin.
- **Affects:** `lpcstudy/dynamics.py` `estimate_lyapunov` and `lyapunov_cached` (every system, every run).
- **Description.** The WU-0007 applied-mathematician ran the code's own estimator about 130 times (scratch scripts, working in the Log of `docs/agent/records/work/WU-0007-lyapunov-validation.md`). For Chua, in 3 of 12 perturbed starting states the orbit left the double-scroll basin (diverged) and the function still returned a finite, positive value (0.1854 for the memo-case parameters, 0.3055 for the registry parameters). A test or a guard that only checks "finite and positive" therefore catches nothing. The registry start state (0.7, 0, 0) is inside the basin for both parameter sets, and the pilot values do not show the problem. Not independently re-run by the main session: this entry relies on the mathematician's log.
- **Resolution:** the WU-0007.2 test simulates the orbit from the same start and asserts that all values are finite and bounded (max |x| at most 3 for Chua, with the per-system bound justified in the plan). A guard in the library (refuse or flag a diverging orbit and count it) is outside WU-0007 and is proposed for WU-0002.11 (counted, reported, never silent).
- 2026-10-11: opened (claude-sonnet-5-5, main session, on the WU-0007 mathematician's finding F1).

**DEF-0016: `tools/test_impact.py` does not select a test file that imports a changed module directly when the file's name does not match it** (PRIME.2, test discipline)

- **Blocking:** no (the radius can be extended by hand); to be fixed in a WU-0011 follow-up.
- **Affects:** the blast-radius set for every change to a module whose direct importers are not named after it. Example: `tests/unit/test_validation.py` imports `lpcstudy.analysis` directly, but `tools/test_impact.py --base 089e278` on the WU-0002.6 branch (changes to `analysis`, `experiments`, `identifiers`, `report`) selected five unit files and not `test_validation.py`. The WU-0002.6 (b) and (c) runs left it out (review R3).
- **Description.** Same gap as DEC-0003 Q2 (changed `systems`/`config` do not select `test_dynamics.py`/`test_embedding.py`), now seen on `analysis`. The rule "a test file is also selected when a module it imports directly is changed" (amendments note section 4) would close it and only adds tests. Verified by the main session by running the tool on the branch (selection printed above).
- **Resolution:** pending a WU-0011.5 follow-up (implement the direct-import rule and a regression test with the fixture); until then, planners add `test_validation.py` by hand when `analysis` changes. Also, a change to any `lpcstudy/*.py` should select `test_tools_test_impact.py` (the hand-written graph fixture is checked there).
- 2026-10-11: opened (claude-sonnet-5-5, main session, on the WU-0002.6 review R3).
- 2026-10-11: resolved by owner ruling (DEC-0015): V7 is plumbing only; `gate_pass` false at smoke is by design; V7 to be confirmed at pilot size in WU-0002.12 and may be retired once superseded (claude-sonnet-5-5, main session).

**DEF-0017: the system states do not depend on the seed: every DEV run and the confirmatory run use the same trajectories** (LPC.PC.21, Methods v2 change-list item 8; candidate defect, needs an owner ruling)

- **Blocking:** to be ruled on by the owner before the freeze (it changes what the confirmatory run is independent of); not blocking development.
- **Affects:** `lpcstudy/data.py` `build_context` (lines 268, 299 to 307): the statistics, main and separate trajectories start from `spec.initial_state` (the separate one from `initial_state + 1e-3`), none from `make_rng`. Only the observation noise and the networks/bootstraps depend on the seed.
- **Description.** Found by the WU-0002.11 applied-mathematician (Log of `docs/agent/records/work/WU-0002.11-counters.md`, finding F-A); verified by the main session by reading `data.py` (the seed does not enter the trajectory start). Consequence: all DEV seeds and the confirmatory seed share identical latent states and oracle quantities; the confirmatory run is fresh in noise only, and the bootstrap over test states models a variability that is never redrawn at the seed level. This may or may not contradict the intent of the design documents (v3 section on Trajectories says "three trajectories, after a 100-LT burn-in", silent on seeding the start state).
- **Resolution:** pending the owner's ruling. Mathematician's recommendation: seed-dependent start states (drawn with `make_rng(seed, "start", system)` near the attractor, burn-in unchanged), which needs the DEF-0015 diverging-orbit guard (WU-0002.11c) first and changes every number (re-baseline and re-run the DEV-0 regression). Not acted on.
- 2026-10-11: opened (claude-sonnet-5-5, main session).

**DEF-0018: the H3a log-rank can give extreme p-values for tiny regimes** (v3 H3a; candidate defect, owner view)

- **Blocking:** no.
- **Affects:** `statistics.logrank_test` / `analysis.h3a_logrank`. One event against 99 censored gives p = 2.5e-23 (mathematician's calculation, WU-0002.11 Log, F-B). DEC-0011 O1 waived the 50-state minimum for individual regimes on purpose; the minimum applies to the total (WU-0002.7/.8 review R3).
- **Resolution:** pending; the owner may want a per-regime minimum or an event-count minimum, which would revisit DEC-0011 O1. Not acted on. Candidate for the WU-0002.9 follow-ups.
- 2026-10-11: opened (claude-sonnet-5-5, main session).
- DEF-0001, status line (2026-10-11, claude-sonnet-5-5, main session; WU-0002.11a, branch wu/0002-11-counters, 2cc3c09, reviewed): E1-E5, S1, S2, D2, O1, O2, O5, L3, L4, L6, L7, L8, P1, X1 and N1 are counted in `results.json` `handling` (schema `lpcstudy.handling/1`), with tests A1-A14; S3 and S4 go to WU-0005.4, E6 to DEF-0012, the T/N rows to lane .11b, R1 to .11d. DEV-0 smoke: 3655 common leaves identical, 0 removed, 2 added (`V7.invariant_mean_replacements`). Not yet merged to develop at the time of this line.
- DEF-0012, status line (2026-10-11, claude-sonnet-5-5, main session; WU-0012.6, branch wu/0012-6-def0012-workers, reviewed: approve, 0 findings): both k-d tree queries (`AnalogLibrary.query` in ensemble.py, `local_dimension_counted` in oracle.py) pass `workers = worker_count()`, which reads `LPC_THREADS` (integer 1 to 99, unset or empty gives 4, anything else raises ValueError naming the variable), per DEC-0008 B. No number changes: DEV-0 smoke `results.json` 4211 leaves, 0 changed, 0 added, 0 removed outside provenance and seconds. Resolved.

**DEF-0019: H2b(i) is verdict-bearing and its bootstrap still drops failed resamples silently** (PRIME.4, DEC-0008 A3, applied-mathematician M6 of WU-0002.11)

- **Blocking:** no (no impact reachable today); to be fixed before the WU-0002.12 regression or the freeze.
- **Affects:** `lpcstudy/analysis.py` `h2b_knob_response` (bootstrap through `_boot`, integer salt 3, at `PRIMARY_LEVEL`).
- **Description.** WU-0002.9 moved H1b-PLP, H1c, H2c and H2d to `block_bootstrap_counted`, but not H2b(i), although the applied-mathematician's M6 assigned it to WU-0002.9. The lane WU-0002.11b counts the dropped resamples (`n_dropped_resamples`, 0 at smoke) but, count-only by DEC-0017 Q5, does not convert. Impact: none reachable today, because the statistic is a mean of finite Spearman values, so the count is structurally 0. Found by the WU-0002.11b reviewer (R6).
- **Resolution:** pending: switch to `block_bootstrap_counted` at the same integer seed and level (expected bitwise-neutral, as for H1b-PLP), proven by a regression test, with owner confirmation; a small follow-up unit (WU-0002.9b) before WU-0002.12.
- 2026-10-11: opened (claude-sonnet-5-5, main session, on the WU-0002.11b review R6).
- DEF-0001, status line (2026-10-11, claude-sonnet-5-5, main session; WU-0002.11b, branch wu/0002-11-counters, reviewed twice: approve): the T/N sites of the inventory in `statistics.py` and `analysis.py` are counted in `results.json` (`handling.result_counts`, 78 paths at smoke; V7 and H2b(i) `n_dropped_resamples`, H1a `n_exponent_at_bound` and `n_covariance_warnings`, H1b `n_floored` and `CP.n_dropped_resamples`, H2b(i) `n_constant_states`, H3a `n_empty_regimes` and `n_degenerate_pairs`) and listed in a `## Handling` section of `RESULTS.md`; `block_bootstrap` is bitwise unchanged (`block_bootstrap_dropped` added); DEV-0 smoke: 3760 common leaves identical, 0 removed, 14 added. Remaining: H2b(i) conversion to `block_bootstrap_counted` (DEF-0019), the clip-sensitivity flag (WU-0002.11e), the diverging-orbit guard (WU-0002.11c, DEF-0015), the `default_rng` audit (WU-0002.11d, DEF-0011), the Levenberg-Marquardt internals (WU-0005.4).
- DEF-0019, status line (2026-10-11, claude-sonnet-5-5, main session; WU-0002.9b, branch wu/0002-9b-h2b-counted, reviewed: approve with wording fixes): fixed; **awaiting owner confirmation** per the Resolution above. `h2b_knob_response` part (i) now uses `block_bootstrap_counted` (same seed config.seed + 3, level and block length) with the A3 tail; with no failed resamples the interval is bitwise equal to the old one; H2b(i) is now inconclusive at 2 or more failed resamples (B = 200); new key `H2b.noise.n_failed_resamples`; `n_dropped_resamples` kept as an alias (it duplicates the count in `handling.result_counts` and now counts NaN and plus or minus inf, unlike the same key in V7 and H1b CP; retiring it at the next schema change is open for the owner). DEV-0 smoke: 4285 leaves, 0 changed, 0 removed, 2 added (both 0). Needs owner review before freeze (verdict path).

**DEF-0020: the block-5 percentile bootstrap intervals undercover the ROADMAP's WU-0006 bounds at pilot sample sizes** (NVVUQ.7, NVVUQ.16; method property, not a code defect; predicted in DEC-0018)

- **Blocking:** to be ruled on by the owner (Option C or K, DEC-0018); the code is correct.
- **Affects:** every interval-versus-band verdict computed with the production moving-block bootstrap (block 5, B = 2000, percentile intervals) at the pilot sizes (500 test states, 300 sweep states), most under serial dependence.
- **Description.** WU-0006 run 2 (`tests/slow/test_statistics_coverage.py`, `test_analysis_coverage.py`; R = 1000; 4 workers; 18 min 39 s; DEV-independent synthetic data, seeds `make_rng(6006, "wu0006", ...)`): 16 coverage and edge-rate rows failed the ROADMAP bounds (>= 0.929 at 95%, >= 0.971 at 98.3%, edge rates <= 0.039 or 0.016): at lag-1 0: C4 and C5 at 98.3% (971 against 972; predicted P(fail) 0.12 and 0.15); at lag-1 0.3: C1 (926, 969), C2 (918, 969, fail 43), C4 (912, 961, pass 19, fail 20), C5 (919, 966, pass 43), C8 (fail 18), C9 (fail 43). All 16 counts lie inside the mathematician's pre-registered consistency ranges, so the code reproduces the reference procedure; the reference expected 1.7 failures at lag-1 0 and 11.4 at lag-1 0.3 for correct code. Passing: C3, C6, C7, C8 and C9 coverage at lag-1 0.3; log-rank size (L1 FWER 19 and 26 of 2000, bound 33); null delta-R2 N2 (8 to 10 of 500, bound 22) and N3 (475 to 478, bound 461).
- **Resolution:** pending the owner's choice (DEC-0018): K keeps the assertions as failing findings at every gate; C turns the ROADMAP-bound rows into labelled characterization rows with the consistency ranges as the defect test. Neither changes a bound, level or R. Whether the study should use a different interval (e.g. a longer block, studentized or BCa intervals) is a design question for the owner and the applied-mathematician, not for this unit; the study's verdicts at lag-1 0.3 carry about 1 to 2 percentage points of extra false-verdict probability.
- 2026-10-11: opened (claude-sonnet-5-5, main session, on the WU-0006 run 2 result).

**DEF-0021: the ROADMAP's null delta-R2 criterion N1 ('interval contains 0') fails by construction** (NVVUQ.7; estimand mismatch)

- **Blocking:** to be ruled on by the owner (DEC-0018 O5); no code defect.
- **Description.** WU-0006 run 2: N1 460 of 500 (indicator, lag-1 0) and 457 of 500 (logit, lag-1 0.3) against 461, as the mathematician predicted: the Q-N interval covers the conditional gain of the two fitted models with training held fixed (about -0.003 to -0.010 under the null), not the population delta-R2 (0). N2 (false 'distinct' rate) and N3 (coverage of the conditional gain) pass in all four rows.
- **Resolution:** pending: amend the ROADMAP row so N2 and N3 are the criteria (N1 reported), by the owner.
- 2026-10-11: opened (claude-sonnet-5-5, main session).

**DEF-0022: the pre-registered reference range for C7 'pass' counts is wrong, and H2a(ii-b) can barely reach 'pass' at n = 500** (VV.3; defect of the reference, and a power finding for the study)

- **Blocking:** no; the mathematician corrects the reference (WU-0006.4); the power finding goes to the owner.
- **Description.** WU-0006 run 2: the consistency-range test for C7 at lag-1 0.3 failed (observed 'pass' edge count 0, range (2, 27); 1 at lag-1 0 against (1, 23)). The reference counted a 'pass' as the one-sided miss (truth above the upper bound), but a real pass for the band (-0.1, 0.1) also needs the lower bound above -0.1. The 98.3% interval is about 0.21 to 0.22 wide, wider than the band (0.2), so a pass is almost impossible. The range is not edited by the developer; the mathematician corrects it with a derivation, and the correction is recorded as made after the result was seen (VV.3). Power point: at pilot size (n = 500 test states) the H2a(ii) partial-correlation criterion of 'both intervals inside (-0.1, 0.1)' is nearly unreachable as a pass; at the full preset sizes it must be checked (interval width scales as 1/sqrt(n)): WU-0003.3's precision report must cover it.
- **Resolution:** pending the mathematician's corrected range; owner informed (DEC-0018).
- 2026-10-11: opened (claude-sonnet-5-5, main session, on the WU-0006 developer's finding F3).

**DEF-0023: numerical results depend on the XLA CPU thread count (A3 chain differs by about 1 ulp when the thread pool is capped)** (LPC.PC.18, REPRO.3; finding, not a code defect)

- **Blocking:** no; the approved pilot-regression criterion (DEC-0019, branch N) expects it; relevant to the reproducibility tolerance of WU-0003.4.
- **Description.** Found by the WU-0002.12 developer while isolating why the A3 scores (`scores/A3/mse/*`, `scores/A3/mse_href`, `oracle_recovery/mse_at_href/A3`, `H2d/ci[1]`) differ from the v1 baseline smoke by about 1e-16 relative: a bisect over develop commits (CPU smokes, DEV-0) shows 0 of 6 A3 leaves differing at 09f66c9 and 6 of 6 at 58ce42c (the WU-0012.4 merge, whose diff touches only the wrappers, their tests and the unit file). Setting `PJRT_NPROC=4 NPROC=4` by hand on 09f66c9 gives the same 6 of 6. So the XLA CPU thread-pool cap changes the trained allocator's results in the last bits (the XLA CPU kernels partition reductions by thread count). The WU-0012.4 Log's statement that 4 and 32 threads are bitwise equal holds for what it compared (not for the A3 chain). Consequences: bitwise reproducibility on CPU requires the same `LPC_THREADS`/`PJRT_NPROC`, which the provenance block now records (WU-0012.5); the pilot runs at `LPC_THREADS=8` while the v1 pilot ran on 2 sandbox cores, so the A3 chain cannot be expected bitwise (branch N of DEC-0019); the GPU-versus-CPU tolerance of WU-0003.4 should be set knowing that thread count alone moves these leaves by about 1e-16 relative.
- **Resolution:** none planned for the code; record in the WU-0003.4 reproducibility tolerance; consider fixing `LPC_THREADS` for the confirmatory CPU regeneration (WU-0016.2) and stating it in the freeze record.
- 2026-10-11: opened (claude-sonnet-5-5, main session, on the WU-0002.12 developer's A3 isolation).
- DEF-0022 (2026-10-11, claude-sonnet-5-5, main session): the reference range for the C7 'pass' counts was corrected by the mathematician (db82ac5: (0, 6) at lag-1 0 and (0, 3) at lag-1 0.3, from the design and 60 000 reference replications; run-2 counts 1 and 0 lie inside); the correction was made after run 2 showed the failure and is documented as such. Power finding confirmed (v3 section 7 already pre-registers that H2a's second part cannot essentially pass; interval width about 4.76/sqrt(n) independent, 5.10/sqrt(n) at lag-1 0.3; no true partial correlation passes with probability 0.8 at n = 500 or 1000). Reference corrected; power finding with the owner. Not blocking.

**DEF-0024: the whitening matrices W and U depend on the host's BLAS kernel and are not reported, so cross-machine comparisons of the CP, oracle and fixture chains cannot be bitwise** (REPRO.3, LPC.PC.18; finding from the WU-0002.12 regression)

- **Blocking:** no for development; relevant to the reproducibility tolerance of WU-0003.4, the confirmatory regeneration (WU-0016.2) and the reading of the pilot regression.
- **Description.** In the DEV-0 pilot regression (branch N of DEC-0019), 69 leaves of the network-independent chains differ from the v1 pilot (cp: 63, up to 2.4e-14 relative; oracle: 4, up to 1e-15; fixture, V1 and V2: 15 of the V-check leaves, up to 1.3e-6 relative). The applied-mathematician (WU-0002.12 Log, block 'N1 failures'; scripts in `docs/agent/notes/2026-10-11-math-wu0002-12-n1-scripts/`) traced them to the whitening matrices W = C^(-1/2) and U = C^(1/2) built by `_symmetric_root` (`data.py:206`) with `np.linalg.eigh` and BLAS products: numpy's bundled OpenBLAS picks its kernel by CPU model, so W and U differ by a few ulps between machines (four kernel families on the i9-14900K give four different pairs; one reproduces the v1 Lorenz-63 `delay_jacobian_rel_err` bitwise). They are not reported in `context`, so the branch switch and the divergence-locus table cannot see them. Not thread count (1, 2, 8 threads give bitwise identical results), not code (v1-baseline and a5cd75b are bitwise equal on this host), not XLA. The 1.3e-6 fixture differences are 1-ulp inputs amplified by finite-difference round-off (factor 1/e, about 6e6 to 7e8). The v1 pilot's CPU and BLAS kernel were never recorded, so it cannot be reproduced bitwise on any other host.
- **Resolution:** pending the owner: (1) a local re-reference run (v1-baseline, pilot preset, DEV-0, this host, `LPC_THREADS=8`) to settle N1 and N3 (predicted branch B, N1 bitwise); (2) report a digest of W and U in `context` and record the CPU model and the BLAS kernel in the provenance block (a WU-0001 follow-up; touches provenance code); (3) fix cross-host tolerances before WU-0003.4 and WU-0016.3 (mathematician's proposal: cp and oracle 1e-12 relative, V1 1e-12 absolute on e, V2 1e-10 relative; the PLP-derived leaves 1e-8 to 1e-4 for CPU against GPU).
- 2026-10-11: opened (claude-sonnet-5-5, main session, on the WU-0002.12 mathematician's analysis).
- DEF-0024, status line (2026-10-11, claude-sonnet-5-5, main session): per the owner's instruction (DEC-0022): N1 kept as written; the v1 baseline is re-run on this reference platform and becomes the new baseline; the platform record (digest of W and U, CPU model and BLAS kernel) is added in WU-0001.6.
- DEF-0016, status line (2026-10-11, claude-sonnet-5-5, main session): a second instance of the radius gap, found by the WU-0008 developer: `tests/unit/test_identifiers.py::test_no_stale_identifier_in_the_package` scans the source text of every `lpcstudy/*.py` (not an import), so `tools/test_impact.py` never selects it for a change to `statistics.py`; the WU-0002.11b docstring 'inventory row T1' (a486b7d) made develop red from its merge (1db8a85) until the docstring was reworded (this commit), unseen by the lane's radius. Fix for the tool: select `test_identifiers.py` (and any test that globs `lpcstudy/*.py`, found by scanning the tests for `PACKAGE.glob`/`glob("*.py")`) for any change under `lpcstudy/`; until then, planners add it by hand. The next merge gate (whole suite) would have caught it.
- DEF-0024, status line (2026-10-11, claude-sonnet-5-5, main session): the local v1 re-run finished (exit 0, 5493 s) and the v3 pilot regression against it is **branch B**: all 8850 unchanged leaves bitwise equal, 0 failures (`docs/study/dev_regression_dev0_vs_local_v1.md`). This confirms the mathematician's diagnosis: the 69 N1 differences against the original pilot are a platform effect (host OpenBLAS kernel in W/U and the covariance), not code, thread count or XLA. Resolution step (1) done; step (2) (the platform record, WU-0001.6) is in review. Remaining: the owner's ruling on N1 as a cross-host criterion for WU-0003.4 and WU-0016.3 (tolerances fixed before the results they apply to exist).
- DEF-0001, status line (2026-10-11, claude-sonnet-5-5, main session, from the WU-0005.4 Log): S3 (non-finite cost, mapped to inf) and S4 (non-finite Jacobian entry, set to 0) are now counted per estimate inside the compiled Levenberg-Marquardt loop (`lm_nonfinite_cost`, `lm_nonfinite_jacobian`; unit: one estimate; denominator `estimates`), with tests L3(i) and L3(ii); handling schema `lpcstudy.handling/2`. The residual, the accepted-step count and a late-progress flag are reported per cell in `handling.cells.<id>.lm` (NVVUQ.10). The estimates are bitwise unchanged (L4; scratch comparison with the base commit; V1 smoke before/after at 221ae9a and 15edf09: 4285 identical leaves, 0 changed, 0 removed, 246 new leaves all under `handling`). First measured rates at smoke size: `lm_nonfinite_cost` 1 of 7800 (core) and 1 of 1800 (sweep, rho 0.01, n_lib 1000), `lm_nonfinite_jacobian` 0, no estimate left with a non-decreasing cost; not production rates (small, weakly trained network). Merged to develop at b0c939c.

**DEF-0025: the robustness filter admits a dimension equal to the number of fitted parameters, where the chi-square reference has zero degrees of freedom** (found by the WU-0005.4 mathematician and independent reviewer; PRIME.4 satisfied (the failure is loud), but results would be lost)

- **Blocking:** no (no configured preset can reach it).
- **Description.** `experiments.py` (`run_robustness`) keeps embedding dimensions with `d >= spec.dim`. For `d == spec.dim` (3) the whole cell would be computed and then `gof_threshold(0)` raises a ValueError; for a robustness variant the broad except records a failed variant (its results are lost), for a core cell the run aborts. Configured values: `embedding_dim` 7 in every preset, `robustness_dims` (5, 7, 10) in full and (7,) in smoke; m = 3 for all three systems, so dof is 2, 4, 7.
- **Resolution:** pending the owner or planner: either filter `d > spec.dim`, or let the fraction above the chi-square threshold return None at dof 0. No change made (a one-line choice with a visible consequence).
- 2026-10-11: opened (claude-sonnet-5-5, main session).
