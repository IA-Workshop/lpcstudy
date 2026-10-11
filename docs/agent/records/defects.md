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
