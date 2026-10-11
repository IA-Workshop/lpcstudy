# WU-0006: Statistical-procedure verification (coverage, size, null ΔR², verdict error rates)

| Field | Value |
| --- | --- |
| Status | planned (plan written; awaiting the applied-mathematician's confirmation and the owner's answers to O1 to O5) |
| Class | CSQ3 development; verification of statistics and verdict code: **needs owner review before freeze** (LPC.PC.11, ROADMAP WU-0006.4) |
| Agent(s) | planner claude-opus-5-5; then applied-mathematician (design, Monte Carlo statements), developer, reviewer |
| Estimate | ROADMAP WU-0006.1 (M), .2 (M), .3 (M), .4 (S). Compute: ≈ 42 min single-process or ≈ 11–12 min with 4 workers for one run of the three files (measured basis below) |

## Plan (written before execution)

Planner: claude-opus-5-5, 2026-10-11, on branch `wu/0006-simstudies` at e52c6ad (`develop`, which holds WU-0002.1 to .10). Governing texts: v3 §7 (blocks of 5, 2000 resamples, levels 1 − 0.05/3 for H2a, H2b and H3c and 95% otherwise, the band rule, the Q-N reading table); v3 §2 rows H1d, H2a to H2e, H3a, H3c; DEC-0008 A1 and A3; DEC-0011 O1; DEC-0012 (shared helpers); DEC-0016; ROADMAP rows WU-0006.1 to .4 and their acceptance rows; DEVELOPMENT_WORKFLOW §4.1, §4.2 and §4.7; `NVVUQ-instantiation-LPC.md` row NVVUQ.7.

**Disclosure (VV.3).** While timing the code, the planner ran `qn_profile_block` once on a synthetic null (seed 1, 900 training and 500 test states, B = 2000; not the test design or seed). The interior-logit ΔR² was −0.045, with interval [−0.070, −0.011]. That interval excludes 0 from below. This single draw informs the prediction for N1 below. No R, bound or level was chosen after it: all of them come from the ROADMAP rows.

### Scope

**In.**
- **WU-0006.1, harness: `tests/slow/slow_harness.py`.** This is a helper module. It has no `test_` prefix, so it is not collected.
  - **AR(1) generators.** Each starts stationary (x₀ ~ N(0, 1)) and runs x_t = φx_{t−1} + √(1−φ²)ε_t, with lag-1 autocorrelation φ ∈ {0, 0.3}. A bivariate version has a common φ and a lag-0 cross-correlation c, and gives a stationary marginal correlation of c.
  - **Paired log-normal per-state "MSE" series.** a = exp(μ_a + σu), b = exp(σv), with (u, v) a bivariate AR(1).
  - **Seeds.** The data come from `make_rng(WU0006_SEED, "wu0006", <case>, f"{φ:g}", r, "data")`, with the literal `WU0006_SEED = 6006`, which is not a registered seed. Replication r uses `cfg_r = replace(FULL, seed=s_r)`, where s_r is an integer drawn from `make_rng(WU0006_SEED, "wu0006", <case>, f"{φ:g}", r, "boot")`. The real code therefore derives its bootstrap seeds (salts and `make_rng` labels) exactly as in the pipeline. The test asserts `FULL.bootstrap_resamples == 2000` and `FULL.bootstrap_block == 5`.
  - **Replication runner.** It uses `ProcessPoolExecutor` with the spawn context and `max_workers = LPC_THREADS` (default 4). Workers start with OMP, MKL and OpenBLAS threads set to 1 and `JAX_PLATFORMS=cpu`, so the total stays within the cap. Results are collected by replication index, so they do not depend on the worker count. This needs owner answer O1; the fallback is in the risks.
  - **Result rows.** Each run writes JSON to `runs/tests/wu0006/<test>-<UTC>.json`, which is not committed. The same row goes into every assertion message, so a failure shows its numbers under `-rfE`.
- **WU-0006.2: coverage and verdict error rates of the moving-block percentile intervals.**
  - **Path.** Every case calls `bootstrap_values` and then `percentile_interval` at both levels. This is the body of `block_bootstrap_counted`. The verdict comes from `criterion_verdict`, with the band and edge constants imported from `analysis`.
  - **Identity checks (I).** For the first replications of each case, the production function returns the same interval and verdict bitwise.
  - **Truth on the band edge.** Each case puts the true value on the edge of its criterion's band. The same replications then give the two-sided coverage, both one-sided miss rates, and P(pass) and P(fail) under the null "true value = edge".

| Case | Criterion and production path | n | Data, truth | Level and band of its verdict |
| --- | --- | --- | --- | --- |
| C1 | mean (generic; `block_bootstrap_counted`) | 500 | Gaussian AR(1), μ = 0 | none (coverage only) |
| C2 | H2c, mean of A4 − A2 (analysis.py:1540) | 500 | log-normal pair, equal marginals, σ = 1, c = 0.8; E[a − b] = 0 | 95%, (−∞, 0) open |
| C3 | median (generic) | 500 | Gaussian AR(1), median 0 (analytic) | none |
| C4 | H3c `h3c_ratio` | 500 | log-normal pair, μ_a = ln 1.05; E a / E b = 1.05 | 1 − 0.05/3, (−∞, 1.05] closed |
| C5 | H2d `h2d_empirical_comparison` (`SimpleNamespace` stand-ins for `scores`) | 500 | as C4, μ_a = ln 1.10; truth 0.10 | 95%, (−∞, 0.10] closed |
| C6 | H1d Spearman (`h1d_correlations` call) | 500 | bivariate Gaussian AR(1), c = 2 sin(0.7π/6) = 0.716736, so ρ_S = 0.7 exactly | 95%, [0.7, ∞) closed |
| C7 | H2a(ii-b) `h2a_part_ii`, interior part | 500 | logit w\* = 0.5s₁ − 0.3s₂² + e₁; Λ̃ = 0.4s₂ + 0.2s₁s₂ + e₂; corr(e₁, e₂) = 0.1. Both means are in span[1, Q], so the partial correlation is 0.1 exactly | 1 − 0.05/3, (−0.1, 0.1) open |
| C8 | H2b(ii) `_paired_change`, mean | 300 | paired Gaussian AR(1), difference mean 0 | 1 − 0.05/3, (0, ∞) open |
| C9 | H2e `_paired_change`, median | 300 | as C8, median of the difference 0 | 95%, (0, ∞) open |
| C1s | C1 at φ ∈ {0.1, 0.2} | 500 | as C1 | reported only, no assertion (a dependence curve for the owner) |

  - Every case runs at φ ∈ {0, 0.3}. n is the pilot size where the criterion is computed: 500 test states, or 300 sweep states for H2b and H2e. ρ_S denotes the Spearman correlation.
  - The cross-checks of the truths are cheap. C6: Spearman of 10⁷ i.i.d. draws, within 3 SE. C4 and C5: E[a]/E[b] from 10⁷ draws, within 3 SE. The analytic values are the references.
- **WU-0006.3: size of H3a and null ΔR².**
  - **Log-rank family, through `h3a_logrank`.**
    - Durations: a geometric hazard h = 0.0125 per step, censored at H_max = 240 steps (about 4.9% censored). They are generated by a Gaussian copula of an AR(1) latent.
    - Regime labels: the terciles of an independent AR(1) latent, so each of the 3 regimes has exactly 200 states.
    - `horizons_km` comes from `kaplan_meier(...).median()` on an independent calibration draw, as in allocation.py:413.
    - L1: global null (equal hazards). L2: partial null (regimes 0 and 1 at h, regime 2 at 2h).
    - Both run at φ ∈ {0, 0.3}, with R = 2000 families each.
  - **Q-N null, through `qn_profile_block`.**
    - Profile: x₁ to x₃ are AR(1); x₄ = 0.6x₁ + 0.8ξ. All three targets are functions of x₁ to x₃ plus noise that is independent of x₄.
    - w\* has about 15% exact zeros, so all three targets are exercised.
    - Sizes: 900 training states (pilot construction plus calibration) and 1000 test states (ROADMAP; see O3). R = 500, at φ ∈ {0, 0.3}.

**Out.**
- Any change under `lpcstudy/`. If a production change looks necessary, the developer stops and refers it.
- Changing block length, B, the levels or a band. That is a design change for the owner.
- H3b's bootstrap over construction states (tree refits are too costly for R = 1000; recorded as a known gap for WU-0008).
- H1a, H1b, H1c and H2a(i)'s eligibility-in-resample statistic.
- The zero-inflated w\* variant of the paired change (question for the AM, M3).
- Tooling changes to `tools/test_impact.py`.

### Sub-steps (one commit group each)
1. **.1** Harness, plus self-checks H1 to H3. Commit.
2. **.2** `tests/slow/test_statistics_coverage.py`: C1 to C9 and C1s, parametrized by (case, φ) so that one failure does not hide the others. Commit.
3. **.3** `tests/slow/test_statistics_logrank_size.py` (L1, L2) and `tests/slow/test_analysis_null_delta_r2.py` (N1 to N3). Commit.
4. One background run of the three files: `tools/run_tests.sh slow --background --durations=10 <3 files>`. The Log gets the results table, any DEFs, and the timing.
5. **.4** The applied-mathematician's section, then `/independent-review`, then owner checkpoint.

File names amend the ROADMAP's (`test_coverage_bootstrap.py`, `test_size_logrank.py`, `test_null_delta_r2.py`) so that `tools/test_impact.py` selects them by its `test_<module>_*.py` convention (O2).

### Definition of done
1. The three test files and the harness exist. Each test's docstring names its reference (truth), R, the Monte Carlo SE, the bound, and the predicted value from the table below.
2. They ran once, in one background run. The Log holds the summary line, the full results table, the wall time, and the §4.9 checklist.
3. Every failed assertion has a DEF with the observed value, the bound and the prediction. No R, seed, level, bound or design value changed after the run (PRIME.2, §4.7).
4. The total of failed (non-finite) resamples is reported per case (PRIME.4).
5. The applied-mathematician's confirmation and the review are recorded, marked "needs owner review before freeze".

### Acceptance criteria (fixed now, VV.3; z = 3, SE = √(p(1 − p)/R) at the nominal p)

Where the ROADMAP gives a formula and a rounded value, the stricter of the two is used, so no bound is loosened by rounding.

| # | Check | R | Bound (SE) |
| --- | --- | --- | --- |
| A1 | Two-sided coverage, C1 to C9, at 95% | 1000 per case, φ and level (both levels from the same replications) | ≥ 0.929324 (SE 0.00689) |
| A2 | Two-sided coverage, C1 to C9, at 1 − 0.05/3 | as above | ≥ 0.971188 (SE 0.00405) |
| A3 | Verdict at the edge, C2 and C4 to C9, at the criterion's own level: P(pass) and P(fail) each | 1000 | 95%: ≤ 0.039811 (SE 0.00494); 98.3%: ≤ 0.016957 (SE 0.00287) |
| A4 | `criterion_verdict` agrees with the one-sided miss: pass ⇔ the predicted-side bound is beyond the edge (open or closed as coded), counted per replication | 1000 | exact equality of counts |
| A5 | Failed resamples, C1 to C9 | — | 0 exactly (continuous data, no constant resample) |
| L1 | Global null: FWER = P(any Holm-adjusted p < 0.01), and P(H3a verdict = pass) | 2000 per φ | each ≤ 0.016675 (SE 0.00222) |
| L2 | Partial null: P(pass) (needs the null pair to reject) | 2000 per φ | ≤ 0.016675 |
| L3 | Pairs not computed (zero variance or empty) | — | 0, counted |
| N1 | ROADMAP, as written: the 95% interval contains 0, for `logit_w_interior` and `w_zero_indicator` | 500 per φ | ≥ 0.921 (formula 0.92076; SE 0.00975) |
| N2 | False "distinct": P(lower bound > 0), same targets | 500 | ≤ 0.045950 (SE 0.00698) |
| N3 | Coverage of the conditional estimand: ΔR² of the fitted pair on 10⁵ fresh states. Refitting `qn_regressor(seed)` must reproduce the returned `delta_r2` bitwise | 500 | ≥ 0.921 |
| I | Identity: production interval and verdict equal the harness's, bitwise. 10 replications for C4, C5, C7 to C9; 3 for C6 (h1d makes 4 Spearman bootstraps) | — | exact |
| H1 | AR(1) generator, 10⁶ draws: lag-1 autocorrelation and variance | — | within 3 SE: φ ± 3(1 − φ²)/√N; 1 ± 3√(2(1 + φ²)/((1 − φ²)N)) |
| H2 | Per-replication results with 1 worker and with 2 workers (first 8 replications of C4 and L1) | — | bitwise equal |
| H3 | Truth cross-checks (C4, C5, C6) | 10⁷ draws | within 3 SE of the analytic value |
| T | Wall time of the three files at `LPC_THREADS=4` | — | ≤ 20 min, leaving ≥ 10 min of the 30-min tier for WU-0005.5. Recorded from `--durations`, not asserted |

**Predictions, fixed now so that a failure is a finding and not a surprise.** These are first-order normal approximations from the exact expected moving-block-bootstrap variance for blocks of 5, computed with tr(MΣ) for AR(1) covariances, divided by the variance of the bootstrap centre. Variance-estimator noise and the percentile endpoints lower each value by roughly 0.002 to 0.005 more; the AM confirms or refines.

| Setting | Expected coverage 95% / 98.3% | Against A1/A2 |
| --- | --- | --- |
| φ = 0, every case | 0.947–0.948 / 0.982 | pass expected (margin ≈ 2.6 SE) |
| φ = 0.3: C1 mean (n = 500) | 0.930 / 0.973 | **at the bound**: P(fail) ≈ 45% |
| φ = 0.3: C8 paired mean (n = 300) | 0.9285 / 0.9723 | **below the bound at 95%**: failure more likely than not |
| φ = 0.3: C3, C9 median; C2, C4, C5 log-normal | ≈ 0.933–0.935 / ≈ 0.975 | P(fail) ≈ 20–30% each |
| φ = 0.3: C6, C7 (influence acf ≈ φ^{2k}) | ≈ 0.944 / ≈ 0.980 | pass expected |
| C1s: φ = 0.1, 0.2 (n = 500) | 0.943, 0.937 | reported |

- **Why the φ = 0.3 cases are at risk.** The block-5 bootstrap captures a long-run variance factor of about 1.60 against the true 1.857 at φ = 0.3: the Bartlett-type truncation of 1 + 2Σφ^k. This is a property of block length 5 against lag-1 dependence 0.3, not a code defect.
- **What a failure means.** It opens a DEF and goes to the owner. The owner's options are:
  - show that the study's residual lag-1 autocorrelation is well below 0.3 (O4);
  - change the block length (a v3 amendment);
  - record it as a known limitation in the WU-0008 budget.

  It is never tuned away.
- **Log-rank.** At φ = 0, the expected FWER is about 0.0099 (Holm at 2 pairs, which comes to Bonferroni at 0.005), so it passes. At φ = 0.3, serially correlated labels and durations inflate the log-rank variance by about 1 + 2Σ_k acf_label(k)·acf_ψ(k), roughly 1.1. Then FWER is about 0.015 to 0.02, which is **near or above 0.016675**. The log-rank test assumes independent states, and a failure here is a finding of the same kind.
- **N1.** It is **predicted to fail** for `logit_w_interior` (see the disclosure). The interval holds the fitted models fixed (v3 and Methods v2 E3), so it estimates the conditional ΔR², which is negative under the null because F4 overfits x₄, not 0. N2 is predicted to pass with a wide margin. N3 is the check of the procedure itself. If N1 fails, the DEF is about the ROADMAP's estimand; the test stays as written (O5).
- **Multiplicity.** There are about 80 probabilistic assertions (36 for A1 and A2, 28 for A3, 6 for L, 12 for N). At z = 3 each has a spurious-failure probability of about 0.0015 to 0.003, so even when everything is exactly nominal, at least one spurious failure among the roughly 40 φ = 0 assertions has a probability of about 5–10%. This is stated, not corrected (z = 3 is the ROADMAP's).

### Compute budget (measured on this 4-CPU host, single process, B = 2000)
- **Bootstrap intervals at n = 500.** Per interval: mean 0.014 s, median 0.028 s, ratio 0.016 s, partial correlation 0.155 s, Spearman 0.37 s (scipy call overhead).
- **Other units.** `h3a_logrank`: 3.3 ms per family. `qn_profile_block` (900/1000 states, 1 thread): 0.69 s, plus about 0.5 s for N3's refits and 10⁵-state prediction.
- **Totals.** Coverage ≈ 1300 s, log-rank ≈ 35 s, ΔR² ≈ 1200 s: ≈ 42 min single-process, which is over the 30-min tier. With 4 workers: ≈ 11–12 min.
- **Untouched.** R, B and the bounds are not reduced: a smaller R would loosen the bounds.

### Affected checks (DEVELOPMENT_WORKFLOW §4.2)
- **Change set:** `tests/slow/` (new files) and `docs/`. No `lpcstudy/`, `tests/conftest.py`, `pytest.ini` or `requirements.txt` change.
- **Rule:** "a test file: that file only"; slow tier, run by the developer once (§4.1).
- **Radius:** the three new `tests/slow/` files; the harness is "unknown mapping", and its importers are the same three files. No unit and no integration tier (the pipeline is not touched). The run goes in the background through `tools/run_tests.sh slow --background` (timeout 3600 s), after `pgrep -fa "lpcstudy --preset"` shows no heavy run.

### Owner checkpoints (LPC.PC.11)
- **Statistics and verdict code:** verified here, not changed. The whole unit needs owner review before freeze (WU-0006.4).
- **Seeds and provenance:** none. The test seed is a literal, and no registered DEV or CONF seed is read.
- **Dependencies:** none with the pool through environment variables. If the developer instead imports `threadpoolctl` (installed transitively by scikit-learn, not pinned), that is a dependency decision for the owner.

### Applied-mathematician must confirm before execution
- **M1.** R, z = 3, the stricter-of rule, and the SE in each row of the acceptance table.
- **M2.** The coverage predictions: refine them with second-order terms (variance-estimator noise at blocks of 5, and the endpoint Monte Carlo error at B = 2000), and state a predicted P(fail) per φ = 0.3 case.
- **M3.** The synthetic designs:
  - log-normal σ = 1 and c = 0.8 (does σ match the heavy tails of per-state MSE?);
  - whether φ applies to the latent or to the observed series;
  - the C7 construction;
  - whether C8 needs a bounded or zero-inflated variant;
  - geometric h = 0.0125 with 4.9% censoring;
  - the ΔR² generating process.
- **M4.** The ΔR² estimand: are N1, N2 and N3 right, and is the Monte Carlo error of N3's 10⁵-state truth below a tenth of the interval half-width?
- **M5.** The log-rank inflation prediction under dependent labels (L1 at φ = 0.3).
- **M6.** That the one-sided A3 bounds are the verdict error rates v3 §7 implies at the edge, and that the A4 equality is exact for the open and closed edges as coded.

### Risks
- **R1. Predicted failures at φ = 0.3 (A1, A2, L1).** Each is recorded as a DEF and referred. Nothing is retried, re-seeded or loosened.
- **R2. Budget.** The timings are from this host; the owner's workstation may differ. If the pool is refused (O1), the fallbacks are an owner-approved budget of about 45 min for WU-0006 (within the 3600 s timeout), or B = 500 (the pilot B) for C6, C7 and the ΔR² nulls, as an owner amendment. Never a smaller R.
- **R3. Spawn pool under pytest** (main-module import, inherited environment). H2 detects nondeterminism.
- **R4. Later changes to the statistics** (WU-0002.11 counting, WU-0002.12 seed conversions) change the bootstrap seeds and the counts. By §4.2's last row, the owning slow test reruns once per such change; the criteria do not change.
- **R5. The name convention covers only one module per file.** An `analysis.py` call-site change does not auto-select `test_statistics_coverage.py`, so the §4.2 last-row rule is applied by hand.

### Open questions for the owner
- **O1.** Approve the process pool: `LPC_THREADS` workers, 1 thread each, spawn, no new dependency.
- **O2.** Approve the file names `test_statistics_coverage.py`, `test_statistics_logrank_size.py` and `test_analysis_null_delta_r2.py` in place of the ROADMAP's names.
- **O3.** ΔR² sizes: read the ROADMAP's "1000 states" as 1000 test states with 900 training states (planned)? The alternatives are the pilot 500/900 or the full 1000/3000 (≈ +60% cost).
- **O4.** Measure the residual lag-1 autocorrelation of each per-state series that enters a criterion on the DEV-0 or DEV-1 pilot outputs. This would be a small separate unit, or inside WU-0003. It decides whether φ = 0.3 is a realistic case or a stress case.
- **O5.** If N1 fails as predicted: keep N1 as the ROADMAP criterion and record the DEF, or amend the criterion to N2 and N3 by decision, keeping the original in history (QA.6).

## Log

**2026-10-11, applied-mathematician (claude-opus-5-5): WU-0006 mathematician review (M1 to M6, O1 to O5), on the plan at d954db9.**

- **Basis.** Full derivations and tables are in `docs/agent/notes/2026-10-11-math-wu0006.md`. The scripts and output logs are in `docs/agent/notes/2026-10-11-math-wu0006-scripts/` (REPRO.10).
  - All data are synthetic. Every computation ran on CPU as 4 spawned single-thread workers, with the scratch seed literal 20261011. No preset, no test suite, no GPU, no DEV or CONF seed.
  - The reference reimplements each statistic on the production index arrays. It agrees with production `spearman`, `partial_correlation` and the resampled mean to ≤ 4e-16. ΔR² and log-rank go through production `qn_profile_block` and `h3a_logrank`.
  - Disclosure: for about 2 min one 4-thread script overlapped the 4-worker job (8 threads). I stopped it; no result is affected.
- **M1: confirmed, with two corrections.**
  - Confirmed: R (1000, 2000, 500), z = 3, the stricter-of rule, and every SE.
  - Integer rules: A1 ≥ 930/1000; A2 ≥ 972; A3 ≤ 39 (95%) and ≤ 16 (98.3%); L ≤ 33/2000; N1 and N3 ≥ 461/500; N2 ≤ 22/500.
  - **N2 bound 0.045946**, not 0.045950. Same count.
  - **H1 lag-1 SE is Bartlett's √((1 − φ²)/N)**, not (1 − φ²)/√N. Empirical 0.00944, Bartlett 0.00954, plan 0.00910 at φ = 0.3. This is a derivation error and no result exists yet. Keeping the stricter form is admissible; its spurious-failure probability is 0.004 instead of 0.0027.
- **M2: the procedure is not nominal, even at φ = 0.**
  - Reference coverage, 95% / 98.3% (B = 2000):
    - φ = 0: 0.938–0.947 / 0.977–0.981. The log-normal cases C2, C4 and C5 are lowest, at 0.938–0.940, against the plan's 0.947–0.948.
    - φ = 0.3: means, ratios and medians 0.923–0.931 / 0.968–0.974; C6 0.944 / 0.980; C7 0.939 / 0.976.
    - C1s: 0.940 (φ = 0.1) and 0.933 (φ = 0.2).
  - Second-order terms: noise of the MBB variance −0.001 to −0.005; heavy tails −0.005 to −0.007; B = 2000 endpoint about −0.0004.
  - **Per-assertion P(fail) for correct code is tabulated in the note.**
    - φ = 0: 0.01–0.15 per assertion; about 1.1–1.7 expected failures among 32.
    - φ = 0.3: 0.33–0.78 for C1–C5, C8 and C9; about 11.4 expected among 32.
  - **Design (owner decides).** The ROADMAP bound is a method-validity criterion, and a failure of it is a true detection, not a code defect.
    - Recommended now, as a tightening: add a **reference-consistency assertion**. Each observed count must lie in the pre-registered range of the note. These are 64 coverage and A3 ranges plus 6 log-rank ranges, with a family-wise false alarm ≤ 3.5%. This is the "fail = defect" test.
    - Then either **Option C (recommended, decided before the run, QA.6).** A1 to A3 become characterization rows: the ROADMAP outcome is computed and reported to the Log and to WU-0008, the pytest outcome is the consistency assertion, and the predictions are fixed now.
    - Or **Option K.** Keep A1 to A3 as assertions. About 13 DEFs of class "method (predicted)" are expected, and they recur at every gate.
- **M3: designs.**
  - **Generator specification fixed in the note**; the predictions apply only to it.
  - **σ = 1 is probably too light.** The O4 proxy puts the log-SD of 1-LT amplification at 1.5–1.9, so per-state MSE log-SD is about 1.7–2.0. At φ = 0, σ = 1.5 gives 95% coverage 0.930–0.933 and σ = 2 gives 0.920–0.923. **This is the main finding for WU-0008:** the H2c, H2d and H3c intervals may run at an effective 0.92–0.93. Add C2h and C4h characterization rows.
  - φ stays on the latent. The influence-series lag-1 at φ = 0.3 is 0.30 (mean), 0.19 (median), 0.16 (log-normal) and ≤ 0.09 (Spearman, partial correlation).
  - The C7 truth is exact. But the zero part is then all-NaN, so **A5 applies to the interior column**, **A3 and A4 use `part_ii["interior"]`** (and the H1d per-row verdict), and the zero column should be asserted as "not computable" with 2000 failed.
  - C8 needs no zero-inflated variant.
  - Log-rank censoring is (1 − h)²⁴⁰ = 0.0489. The design is adequate.
  - ΔR² process: specified in the note, with R²₃ = 0.35 / 0.27.
- **M4: what the interval covers.** The Q-N interval covers **Δ_cond** = [E(Y − f̂₃)² − E(Y − f̂₄)²]/Var(Y), with the fitted models fixed, over a new stationary test state in the target's domain. It does not cover the population ΔR², which is 0 under the null.
  - Under the null, Δ_cond has mean −0.007 (logit) and −0.010 (indicator) at 900/1000, and −0.002 / −0.0035 at 3000/1000. It is positive in 14–21% of training sets.
  - **N1 is predicted to fail:** P(0 ∈ CI) = 0.86–0.93, so P(fail) = 0.66–1.0. This is an estimand mismatch, not a defect.
  - **N2 is the right error criterion:** a false "distinct" occurs at 0.013–0.035, and P(fail) < 0.01.
  - **N3 is the procedure check:** 0.946 ± 0.008 (logit) and 0.960 ± 0.007 (indicator); P(fail) about 0.03.
  - The truth's MC SE is 0.051 (mean) and 0.070 (max) of the half-width, which meets "below a tenth". The refit was bitwise in 1000/1000 replications.
  - The v3 reading under the null is "reduces" 92–99% of the time.
- **M5: log-rank.** Variance inflation at φ = 0.3 is 1.079 (planner: about 1.1).
  - L1 FWER: 0.0105 at φ = 0 and 0.0134 at φ = 0.3. The planner's 0.015–0.02 was too high. P(L1 fails) is 0.006 and 0.10.
  - L2 P(pass): 0.0115 and 0.0122, so P(fail) is 0.02–0.04.
  - L3: 0 uncomputed pairs in 160 000 families.
- **M6: verdict error rates.** A3's α/2 is the right nominal: one-sided non-coverage at the edge, worst case over the null, the same for open and closed edges.
  - A4 is exact. Assert it per replication, with C7's two-sided rule.
  - A4 cannot test the open/closed flags, since ties never occur. Deterministic unit tie tests cover H2a(i), H2a(ii), H2b, H2c, H2d and H3c. **None found for H1d's closed edge at 0.7** (a gap for a later unit).
- **Multiplicity.** There are 82 assertions. If the procedures were exactly nominal, P(≥ 1 spurious failure at φ = 0) would be about 13%. **For correct code about 16–17 ROADMAP-bound failures are expected** (A1 to A3: 1.1–1.7 and 11.4; L: 0.2; N1: 3.6; N3: 0.03–0.3). The plan's multiplicity paragraph must be replaced.
- **O1.** Approve the spawned pool, with the thread variables set to 1 in the parent's `os.environ` before the pool is created (an initializer is too late). B = 500 is not equivalent: it is a different procedure and loses about 0.0016 more coverage.
- **O2.** `test_impact` selects slow files for the changed module only. Use:
  - `test_statistics_coverage.py` (C1, C3, C1s);
  - `test_analysis_coverage.py` (C2, C4–C9);
  - `test_analysis_logrank_size.py`;
  - `test_analysis_null_delta_r2.py`.

  The R5 by-hand rule remains for `statistics.py` changes.
- **O3.** Use 3000/1000 (FULL) if the pool is approved, which fits T ≤ 20 min. Otherwise 900/1000, where my predictions apply.
- **O4.** The existing development outputs hold no per-state series, so the autocorrelation cannot be measured from them.
  - The CPU dynamics proxy gives lag-1 of −0.06 (Lorenz), +0.13 (Rössler, lag-3 −0.20) and +0.06 (Chua). φ = 0.3 is therefore very likely a stress case.
  - The real measurement needs a per-state dump from a DEV pilot: influence acf, V*(b = 10, 20)/V*(b = 5), and the per-state MSE log-SD. It belongs in WU-0003, before the freeze, not now.
- **O5.** Amend now (QA.6, original kept): N1 becomes reported characterization; N2 and N3 are the assertions. Otherwise record the predicted DEF.
- **Plan amendments needed before execution.**
  1. N2 bound and H1 lag-1 SE corrections.
  2. Generator specification.
  3. A5, A3 and A4 column and verdict choice for C7 and C6.
  4. A4 per replication.
  5. Consistency ranges, plus the C2h and C4h rows.
  6. Replace the predictions and multiplicity text.
  7. Owner decisions C or K, and O1 to O5.

  Every item is a tightening or a correction; no bound is loosened.

**2026-10-11, claude-sonnet-5-5 (main session): Plan amendment (main session).** This amends the plan above before any code, on the applied-mathematician's review (9d1152e) and DEC-0018 (proposed). It supersedes the plan wherever they differ.

- **Accepted as tightenings or corrections (mathematician amendments 1 to 6).**
  1. N2 bound 0.045946 (count rule ≤ 22 of 500). The H1 lag-1 standard error is √((1 − φ²)/N) (Bartlett).
  2. The generator specifications of the note, M3 (a) and (g), replace the plan's descriptions. The predictions apply only to them.
  3. C7 and C6 column and verdict choices: A5, A3 and A4 use `part_ii["interior"]` for C7 and the per-row verdict of `h1d_correlations` for C6. The C7 zero column is asserted "not computable" with 2000 failed resamples.
  4. A4 (verdict equality) is asserted per replication.
  5. Every bound is an integer count: A1 ≥ 930/1000, A2 ≥ 972/1000, A3 ≤ 39/1000 (95%) or ≤ 16/1000 (98.3%), L ≤ 33/2000, N1 and N3 ≥ 461/500, N2 ≤ 22/500.
  6. A pre-registered consistency range for each observed count from the reference (the 70 ranges: 36 coverage, 28 A3, 6 log-rank) is the defect test and is always asserted. The characterization rows C2h and C4h (σ = 1.5 and 2, c = 0.8, φ = 0) are added, and C1s keeps its role. Neither is asserted.
- **Option K until the owner rules (DEC-0018).** The ROADMAP-bound assertions (A1, A2, A3, L1, L2, N1) are asserted behind one module-level constant `ASSERT_ROADMAP_BOUNDS = True` in the harness. Their outcomes are always computed and written to a results table (JSON under `runs/tests/`, plus a summary pasted into this Log). Flipping the constant to `False` (Option C) turns those rows into recorded characterization rows with the consistency ranges as the defect test. Both modes are implemented and the switch itself is tested. N2 and N3 of the delta-R2 study are always asserted; N1 is under the constant. A failed asserted row is a FINDING to record, never something to tune. No R, B = 2000, block = 5, level or bound changes.
- **O1.** The spawned worker pool is approved. Workers are single-thread: OMP, MKL and OPENBLAS_NUM_THREADS = 1, LPC_THREADS = 1 and PJRT_NPROC = NPROC = 1 are set in the parent environment before the pool is created, the start method is spawn, the pool size is min(LPC_THREADS, 4) of the invoking environment, and there is no new dependency.
- **O2 (file names).** `tests/slow/test_statistics_coverage.py` (C1, C3, C1s), `tests/slow/test_analysis_coverage.py` (C2, C4 to C9, C2h, C4h), `tests/slow/test_analysis_logrank_size.py` and `tests/slow/test_analysis_null_delta_r2.py`, with a shared harness module `tests/slow/wu0006_harness.py` and a fast harness smoke `tests/slow/test_wu0006_harness.py`. No `lpcstudy/` change and no import-graph change.
- **O3.** The delta-R2 study uses 3000 training and 1000 test states. Seeds are `make_rng(6006, "wu0006", case, ...)`, never a DEV or confirmatory seed.
- **Process.** The §4.9 checklist is logged before each test invocation. The slow tier runs once for the whole set through `tools/run_tests.sh slow --background`. If it needs more than the 3600 s tier timeout, stop and report; R is never reduced.

**2026-10-11, developer (claude-sonnet-5-5): implementation log (WU-0006.1 to .3).**

- Merge: `git merge develop` conflicted only in `queue.md` (both sides appended log lines; kept both); no markers remain (`git grep '^<<<<<<<'` empty). Commit 7c277ce.
- Files: `tests/slow/wu0006_harness.py` (generators, pool, evaluation, results table), `tests/slow/wu0006_reference.py` (the 70 ranges and the reference tables, transcribed by script from the note), `tests/slow/test_wu0006_harness.py` (smoke and self-checks), and the four study files of O2. No change under `lpcstudy/`, `tools/`, `tests/conftest.py` or `tests/unit`.
- `python3 tools/test_impact.py --base develop --explain`: each of the four study files and the smoke is "test file: that file only"; the harness and reference modules are "test helper: tests naming it". `_convention` confirms the selection by module: `statistics` selects `test_statistics_coverage.py`; `analysis` selects `test_analysis_coverage.py`, `test_analysis_logrank_size.py` and `test_analysis_null_delta_r2.py`. The unit and integration radius is empty (no `lpcstudy/` or `tools/` change), so no unit test is run.
- Ad hoc development check (not a test run; one process, a few replications, no pytest): all nine coverage designs reproduce the production call site bitwise (identity 1 in each), the C7 zero column reads "not computable", the log-rank replication costs 4 to 10 ms and one delta-R2 replication 2.9 s.

**Test run 1 (the harness smoke), §4.9 checklist.**
1. Change set: `git diff --name-only develop...HEAD` is the note and scripts, the unit file and `queue.md`, and seven files under `tests/slow/`; `git status --porcelain` is clean.
2. Radius: `tests/slow/test_wu0006_harness.py` only (slow tier; rule "a test file: that file only"); far smaller than the suite; no gate.
3. Already run? No, this code has never run under pytest.
4. Device: `JAX_PLATFORMS=cpu` (set by the wrapper, and in the workers by `worker_pool`).
5. Threads and time: `LPC_THREADS=4` (pool of 4 single-thread workers); slow timeout 3600 s; expected 2 to 4 minutes.
6. Contention: `pgrep -fa 'lpcstudy --preset|run_tests.sh slow'` shows nothing but itself; no GPU use.
7. Output: `-q --tb=short -rfE` by the wrapper, plus `--durations=10`.
8. Command: `tools/run_tests.sh slow --background --durations=10 tests/slow/test_wu0006_harness.py`.

**Test run 1 result.** `29 passed in 20.20s` (`runs/tests/slow-20261011T165352Z.log`, exit 0). The slowest was the end-to-end tiny-R run of all designs on the pool (13 s); the 10^7-draw truth checks took 0.8 to 1.5 s each. Self-check greps of the new files: the only `np.where`/`isfinite`/`try` sites are the design (hazard of regime 2; the w* = 0 rule below the 15% quantile), the exclusion of an uncomputed log-rank p from the variance-inflation diagnostic (those pairs are counted and asserted zero by L3), JSON serialization, the environment restore in `worker_pool`, and the exception cache in `RunCache` (re-raised, never swallowed). Randomness comes from `make_rng` only (no `default_rng`, `random.` or `PRNGKey` site).

**Test run 2 (the four study files, once), §4.9 checklist.**
1. Change set: as for run 1, plus the run-1 log entry; `git status --porcelain` is clean after the commit that precedes the run.
2. Radius: `tests/slow/test_statistics_coverage.py`, `test_analysis_coverage.py`, `test_analysis_logrank_size.py` and `test_analysis_null_delta_r2.py` (slow tier; "a test file: that file only", the four files named by `test_impact` for `statistics` and `analysis`); smaller than the suite; no gate. The smoke file is not rerun (no code change since run 1).
3. Already run? No. These four files have never run.
4. Device: `JAX_PLATFORMS=cpu` (wrapper; workers via `worker_pool`).
5. Threads and time: `LPC_THREADS=4`, pool of 4 single-thread workers; slow timeout 3600 s; expected 15 to 20 minutes (one delta-R2 replication costs 2.9 s: 1000 replications / 4 workers about 12 minutes; coverage a few minutes; log-rank under a minute). If it nears the limit: stop and report, do not reduce R.
6. Contention: `pgrep -fa 'lpcstudy --preset|run_tests.sh slow'` shows nothing; no GPU use.
7. Output: `-q --tb=short -rfE` by the wrapper, plus `--durations=10`.
8. Command: `tools/run_tests.sh slow --background --durations=10 tests/slow/test_statistics_coverage.py tests/slow/test_analysis_coverage.py tests/slow/test_analysis_logrank_size.py tests/slow/test_analysis_null_delta_r2.py`.

**Owner authorization (conversation; ledger entry is the owner's).** Relayed by the main session on 2026-10-11, stated by the owner in the session: "For the slow job, you are authorized to run in parallel and or use the GPU if needed." Use: it permits running in parallel with other CPU work and up to 8 single-thread spawned workers, and the GPU only if measured to be needed (GPU lock rules unchanged); it changes no R, B, level, bound or seed and does not extend to any other job. **Not used:** run 2 had already finished (18 min 39 s with 4 workers, far under the 3600 s timeout), so no code or setting was changed for it; the GPU was not used and no need was measured (the simulations are numpy bootstrap and single-thread scikit-learn work).

**Test run 2 result (the four study files, once).** `12 failed, 66 passed in 1119.37s (0:18:39)` (`runs/tests/slow-20261011T165447Z.log`, exit 1; 4 workers). Per-case counts are in `runs/tests/wu0006_{coverage_statistics,coverage_analysis,logrank,delta_r2}.json` (not committed; `runs/` is ignored) and in the table below.

**Test run 3 (after the harness fix), §4.9 checklist.**
1. Change set: as above plus the harness fix commit; `git status --porcelain` clean before the run.
2. Radius: `tests/slow/test_wu0006_harness.py` (the harness changed, so the smoke reruns once) and the two nodes `test_analysis_coverage.py::test_exact_checks[C7-0.0]` and `[C7-0.3]` (the only tests whose code path changed); not the whole study.
3. Already run? Not on this code: the harness changed after runs 1 and 2.
4. Device: `JAX_PLATFORMS=cpu`. 5. Threads and time: `LPC_THREADS=4`, 4 workers; about 2 minutes. 6. Contention: nothing running (`pgrep` as before). 7. Output: `-q --tb=short -rfE`.
8. Command: `tools/run_tests.sh slow --background tests/slow/test_wu0006_harness.py "tests/slow/test_analysis_coverage.py::test_exact_checks[C7-0.0]" "tests/slow/test_analysis_coverage.py::test_exact_checks[C7-0.3]"`.

**Test run 3 result.** `32 passed in 99.89s` (`runs/tests/slow-20261011T171519Z.log`, exit 0): the 30 smoke tests (29 plus the new C7 zero-column rule test) and `test_exact_checks[C7-0.0]`, `[C7-0.3]`.

**Results of WU-0006.2 and .3 (run 2; R = 1000 for coverage, 2000 for log-rank, 500 for delta R2; counts out of R; "range" is the pre-registered consistency range; ROADMAP bounds: A1 >= 930, A2 >= 972, A3 <= 39 (95%) or <= 16 (98.3%), L <= 33, N1 and N3 >= 461, N2 <= 22).**

| case, phi | cover 95% (range) | cover 98.3% (range) | edge pass / fail (range) | ROADMAP rows failed | consistency |
| --- | --- | --- | --- | --- | --- |
| C1, 0 | 945 (918-969) | 983 (963-994) | - | none | ok |
| C1, 0.3 | **926** (895-953) | **969** (949-987) | - | A1, A2 | ok |
| C3, 0 | 953 (917-969) | 984 (963-994) | - | none | ok |
| C3, 0.3 | 937 (899-956) | 973 (953-989) | - | none | ok |
| C2, 0 | 932 (911-964) | 974 (959-992) | 29 / 39 (14-52 / 13-50) at 95% | none | ok |
| C2, 0.3 | **918** (898-955) | **969** (950-987) | 39 / **43** (17-58) | A1, A2, A3 fail | ok |
| C4, 0 | 940 (912-965) | **971** (959-992) | 13 / 16 (2-25) at 98.3% | A2 (one below 972) | ok |
| C4, 0.3 | **912** (896-954) | **961** (951-988) | **19 / 20** (3-30 / 3-29) | A1, A2, A3 pass, A3 fail | ok |
| C5, 0 | 933 (910-963) | **971** (958-991) | 34 / 33 (14-53 / 13-50) at 95% | A2 (one below 972) | ok |
| C5, 0.3 | **919** (897-955) | **966** (948-986) | **43** / 38 (17-59) | A1, A2, A3 pass | ok |
| C6, 0 | 959 (919-971) | 985 (961-993) | 19 / 22 (10-47) at 95% | none | ok |
| C6, 0.3 | 944 (915-968) | 977 (962-994) | 25 / 31 (11-48 / 12-50) | none | ok |
| C7, 0 | 946 (917-968) | 972 (962-993) | 1 / 15 (1-23 / 1-24) at 98.3% | none | ok |
| C7, 0.3 | 930 (910-964) | 977 (957-991) | **0** / 9 (2-27 / 2-25) | none | **A3 pass 0 below 2 (see F3)** |
| C8, 0 | 953 (917-968) | 987 (963-994) | 6 / 7 (1-23 / 1-22) at 98.3% | none | ok |
| C8, 0.3 | 933 (892-951) | 972 (947-986) | 10 / **18** (4-31 / 4-32) | A3 fail | ok |
| C9, 0 | 949 (915-967) | 982 (960-993) | 28 / 23 (13-51 / 11-48) at 95% | none | ok |
| C9, 0.3 | 934 (901-958) | 977 (954-990) | 23 / **43** (15-56 / 17-58) | A3 fail | ok |

Failed resamples (A5): 0 in every coverage case, in every log-rank family (L3: 0 uncomputed pairs in 8000 families) and every delta-R2 replication. Identity with the production call site (bitwise) and A4 (verdict equals the independent rule in every replication) hold for all 18 asserted cells and the 7 characterization cells. The C7 zero column read "not computable" with 2000 failed resamples in every checked replication (after the fix of F4).

| row | FWER count | P(pass) count | censored | mean chi-square of the null pair(s) (reference) | ROADMAP (<= 33) | consistency |
| --- | --- | --- | --- | --- | --- | --- |
| L1, 0 | 19 (7-39) | 3 (0-9) | 0.0490 | 1.018 (1.009) | ok | ok |
| L1, 0.3 | 26 (11-47) | 2 (0-10) | 0.0489 | 1.075 (1.079) | ok | ok |
| L2, 0 | - | 27 (8-42) | 0.0333 | 1.025 (1.012) | ok | ok |
| L2, 0.3 | - | 27 (9-44) | 0.0335 | 1.035 (1.046) | ok | ok |

| delta R2 (3000 / 1000), phi, target | N1 (>= 461) | N2 (<= 22) | N3 (>= 461) | mean conditional gain | P(gain > 0) | mean half-width | P("reduces") |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0, logit | 467 | 8 | 475 | -0.0025 | 0.14 | 0.0155 | 0.984 |
| 0, indicator | **460** | 10 | 475 | -0.0033 | 0.18 | 0.0249 | 0.972 |
| 0.3, logit | **457** | 8 | 478 | -0.0027 | 0.14 | 0.0156 | 0.984 |
| 0.3, indicator | 467 | 8 | 476 | -0.0031 | 0.23 | 0.0252 | 0.982 |

Refit bitwise equal in 500 of 500 replications in each row; the truth's Monte Carlo SE is at most 0.071 of the half-width (below a tenth). Reference (phi = 0, R = 200): gain -0.0023 and -0.0035, half-width 0.0155 and 0.0253, N1 0.925 and 0.890 (observed 0.934, 0.920), N2 0.020 and 0.035 (observed 0.016, 0.020), N3 0.960 and 0.925 (observed 0.950, 0.950).

Characterization rows (coverage 95% / 98.3% out of 1000; z against the reference with both Monte Carlo errors): C1s phi 0.1: 947 / 982 (z 0.9, 0.6); phi 0.2: 935 / 980 (0.3, 1.2). C2h sigma 1.5: 949 / 980 (2.3, 1.3); sigma 2: 925 / 964 (0.4, -1.0). C4h sigma 1.5: 927 / 965 (-0.8, -1.8); sigma 2: 939 / 984 (1.9, 3.0). The largest deviation (C4h sigma 2 at 98.3%, z 3.0) is a reported row, not an assertion; with eight z-values the chance of one near 3 is about 2%. None of these shows the lower coverage the reference predicts for sigma 2 more clearly than the reference's own R = 20 000 does; the rows are consistent with the reference at this R and are not evidence for a different effective level.

**Findings (failed asserted rows are findings, nothing was tuned; DEF numbers are for the main session to assign).**
- **F1 (class "method", predicted).** 16 ROADMAP-bound coverage and edge rows failed: 2 at phi = 0 (C4 and C5 at 98.3%, each 971 against 972, P(fail | correct code) 0.12 and 0.15) and 14 at phi = 0.3 (C1: A1, A2; C2: A1, A2, A3 fail; C4: A1, A2, A3 pass, A3 fail; C5: A1, A2, A3 pass; C8: A3 fail; C9: A3 fail). The reference expected 1.7 and 11.4 for correct code. Every one of these counts lies inside its pre-registered consistency range, and the code agrees bitwise with the independent computation, so they are properties of the block-5 percentile interval (undercoverage, most for the log-normal cases and lag-1 0.3), not defects. Tests: `test_roadmap_coverage_bounds[C1-0.3]`, `test_roadmap_coverage_and_verdict_bounds[C2-0.3, C4-0.0, C4-0.3, C5-0.0, C5-0.3, C8-0.3, C9-0.3]`. Passing at phi = 0.3: C3, C6, C7, and C8 and C9 coverage. This is the content of DEC-0018.
- **F2 (N1, predicted estimand mismatch).** N1 failed in 2 of 4 rows (460 and 457 of 500, bound 461): the interval targets the conditional gain (mean -0.0025 to -0.0033), not the population gain 0. N2 (8 to 10 of 500) and N3 (475 to 478) pass in all four rows. Tests: `test_roadmap_interval_contains_zero[0.0]` and `[0.3]`.
- **F3 (defect of the pre-registered reference, not of the code; the only consistency-range failure).** `test_counts_are_consistent_with_the_reference[C7-0.3]` failed: the edge "pass" count is 0, below the range (2, 27); at phi = 0 it is 1, at the bottom of (1, 23). The reference took P(pass) at the edge to be the one-sided miss (truth above the upper bound, 10 to 13 per 1000). The verdict "pass" for the open two-sided band (-0.1, 0.1) also needs the lower bound above -0.1, and the 98.3% interval is 0.209 to 0.224 wide (mean half-width 0.086 to 0.112), wider than the band (0.2): once the upper bound is below 0.1 the lower bound is below -0.1. Evidence: in an ad hoc check of 200 replications (phi = 0) the truth was above the upper bound in 2 and the lower bound was at or below -0.1 in both, so there were no passes; the per-replication A4 equality and the identity with production hold. The review's M6 ("the far edge is never touched") holds for the fail side only. The range was not edited (PRIME.2, fixed before the result); the applied-mathematician should correct the reference (the expected P(pass) at the edge for C7 is about 0) and the owner should note a design consequence for WU-0008: with a block-bootstrap interval of this width at n = 500 and a 98.3% level, H2a(ii-b) can hardly reach "pass" at all (it needs a half-width below 0.1 around an estimate within about 0.1 of 0), whatever the truth is near the edge.
- **F4 (defect of the harness, fixed in the commit after run 2).** `test_exact_checks[C7-0.3]` failed in run 2 because my check of the C7 zero column required the combined (ii) verdict "inconclusive", while `combine_verdicts` correctly returns "fail" when the interior part fails (one replication of the ten checked had an interior "fail"). The expectation was wrong, not the production code; fixed (combined = "fail" if the interior fails, else "inconclusive"), a unit-style test added, and the C7 nodes rerun in run 3 (pass). No bound or tolerance moved.
- **F5 (reported).** The characterization rows are consistent with their references (above). The C7 and C6 truths, the log-normal truths and the generators passed H1 and H3 in the smoke.

**Runtime and budget.** Run 2: 18 min 39 s with 4 workers (timeout 3600 s; the plan's T <= 20 min is met). By part: delta R2 about 375 s per phi (about 12.5 min; the review had estimated 8), C6 about 100 s per phi, C7 38 s, every other coverage case 3 to 7 s, log-rank 2 to 3 s per row. Run 1: 20 s; run 3: 100 s. No R, B, level, bound or seed changed. The owner's authorization of 8 workers and the GPU was not needed.

**Deviations from the plan and the amendment.** (1) Added `test_wu0006_harness.py` (30 self-checks) and `wu0006_reference.py`. (2) `evaluate_*` keep a `strict` switch used only by the smoke. (3) The ROADMAP-bound tests of a (case, phi) are one test each (all of A1, A2, A3 together), with every violated row listed in the message. (4) The C7 pass range failure (F3) stays a recorded failure; nothing was relaxed. (5) The unit tier radius is empty (no `lpcstudy/`, `tools/` or `tests/unit` change), so no unit test was run. (6) Not done: the independent review, WU-0006.4 (the applied-mathematician's section) and the status, which are the main session's.

**2026-10-11, applied-mathematician (claude-opus-5-5): WU-0006.4 mathematician review (C7 correction), part 1, on 1ef7b9c.**

The full form is the addendum A1 to A8 of `docs/agent/notes/2026-10-11-math-wu0006.md`. Scripts and logs: `c7_extend.py`, `c7_verdict_ranges.py` and `h2a_power.py` in the scripts folder. All data are synthetic, from the scratch seeds 20261011, 20261012 and 20261013; no DEV or CONF seed, preset, test run or GPU was used. CPU only, 4 single-thread workers, about 7 min.

- **VV.3 (stated plainly).**
  - This correction is made **after run 2 showed the failure** (F3, DEF-0022). I had read the run-2 C7 counts before deriving anything.
  - The derivation uses **only the design and reference replications**, never the run-2 counts.
  - The range rule was fixed before any corrected count existed. It is the rule of the other 70 ranges: the central 1 − 0.0005 interval of Bin(1000, p) mixed over p ~ N(p_ref, se_ref²).
  - R_ref was extended from 20 000 to 60 000 per φ (seed 20261012) because the original reference pass counts were only 25 and 7. The test counts played no part in that decision.
- **The error was mine (M6).**
  - The reference counted "pass" as the one-sided miss P(0.1 > hi).
  - H2a(ii-b) passes only if lo > −0.1 and hi < 0.1.
  - The 98.3% interval is 0.210 (φ = 0) and 0.224 (φ = 0.3) wide on average, wider than the band of 0.2. So a pass needs width < 0.2 (P = 0.25 and 0.07) and an estimate about 2.2 SD below the truth.
  - "The far edge is never touched" was reversed. It is struck through in the note.
- **Corrected ranges (counts out of 1000, R_ref = 60 000).**

  | φ | pass, old → new | fail | inconclusive (new, not asserted) |
  | --- | --- | --- | --- |
  | 0 | (1, 23) → **(0, 6)**, rate 0.00103 | (1, 24) kept | (975, 998) |
  | 0.3 | (2, 27) → **(0, 3)**, rate 0.00025 | (2, 25) kept | (974, 998) |

  - **Fail ranges are kept.** Their definition was already exact: hi ≤ −0.1 occurred in 0 of 60 000 replications per φ.
  - **Reference error.** The reference SE is 0.13 and 0.06 counts against range widths of 6 and 3, which is negligible. The Jeffreys sensitivity check gives the same ranges.
  - **False alarm.** The per-range false alarm is ≤ 0.00018. The family-wise bound stays ≤ 3.5%.
  - **ROADMAP rows.** P(A3-pass bound fails) for C7 is now 0 (was 0.03 and 0.14). The expected ROADMAP failures for correct code become 1.66 and 11.23.
  - **Cross-checks.** An independent-seed shift estimate gives 0.001 at both φ. Normal theory gives 0.0017 and 0.00045, the same order.
- **Comparison with run 2 (made only after the ranges were written).**
  - φ = 0: pass 1 in (0, 6), fail 15 in (1, 24), inconclusive 984 in (975, 998).
  - φ = 0.3: pass 0 in (0, 3), fail 9 in (2, 25), inconclusive 991 in (974, 998).
  - **All are inside.** P(K = 0) is 0.78 at φ = 0.3, a typical value.
  - F3 is therefore a reference defect, not a code defect. The production verdict, the harness rule and A4 were right.
- **Power of H2a(ii-b)** (n = states in the part's domain; 98.3%; B = 2000).
  - **Width.** W ≈ 4.76/√n (independent states) and 5.10/√n (lag-1 0.3). The observed exponent is 0.48–0.50.
    - n = 500: 0.212 and 0.226. n = 1000 (FULL n_test): 0.151 and 0.161. n = 2000: 0.106 and 0.114.
    - A pass needs W < 0.2, which means n > 566 and n > 650.
  - **P(pass) ≥ 0.8 is reached for no true partial correlation**, at either the pilot size (n_test = 500; max P = 0.018 and 0.003 at ρ = 0) or the full size (n_test = 1000; max 0.56 and 0.43 at ρ = 0). These are for one part with all test states interior; the interior part has fewer.
    - At n = 2000 it is reached for |ρ| ≤ 0.027 and 0.023.
    - n needed at ρ = 0: 1360 and 1600; at ρ = 0.02: 1660 and 1950; at ρ = 0.05: 4180 and 4890.
    - Jointly, (ii) needs every part to pass and "supported" needs three systems: at best about 0.03 at FULL.
  - **Refutation is reachable** with 0.8 for |ρ| ≳ 0.25 (n = 500) and 0.20 (n = 1000).
  - **This is the limitation v3 §7 already pre-registers** ("H2a's second part … essentially cannot pass"). DEF-0022's power point confirms and quantifies it; it is not a new defect. Any change is a v3 matter for the owner.
- **Monte Carlo statements in `tests/slow/*.py` docstrings, against M1.**
  - **Correct:** the A1–A3, L, N1 and N2 bounds and SEs, the integer rules, the 3.5% family-wise bound, the H1 Bartlett SE and the log-rank ranges.
  - **Wrong or missing** (developer to fix; none moves a bound):
    1. N2's "P(fail) < 0.01" and N3's "about 0.03" hold at 900/1000. At 3000/1000 the indicator reference (R_ref 200) gives **0.25 and 0.42**. I recommend a 3000/1000 reference with R_ref ≥ 1000 (about 12 min) before the next gate.
    2. N1's "0.5 and 1.0" should read 0.42 and 0.88.
    3. `test_analysis_coverage.py`:
       - "R_ref 20 000 to 40 000" should read 10 000 to 40 000 (C6);
       - "one-sided-miss rule" is wrong for C7, whose rule is two-sided;
       - the A3 reference rates are missing.
    4. Harness smoke:
       - the C7 truth check's "SE about 3e-3" is the chunk SD; the SE is 3.1e-4;
       - the log-normal "SE near 1e-3" is really 3.3e-4 to 5.2e-4;
       - the bivariate lag-1 bias is 0.46 SE (false alarm 0.0058, not 0.0027);
       - the corr(x₄, x₁) tolerance 3e-3 is 4.7 SE (SE 6.4e-4), and may be tightened to 1.9e-3.
- **Integrity.**
  - `tests/slow/wu0006_reference.py` changes only the two C7 pass tuples, with the old values kept in dated comments. It adds a dated docstring paragraph and the unasserted `C7_INCONCLUSIVE_REFERENCE`.
  - **The other 68 ranges are untouched.** (70 in total; the two C7 pass ranges at φ = 0 and 0.3 shared the error.) A regeneration from the saved reference arrays reproduces 62 of 64 coverage and A3 ranges exactly, and the 6 log-rank ranges equal M5.
  - No other code or test changed. No test was run; the slow tier was not run.
  - Rerun owed by the §4.2 rule: the reference module changed, so the C7 consistency nodes (`test_analysis_coverage.py::test_counts_are_consistent_with_the_reference[C7-0.0]` and `[C7-0.3]`) and the smoke `test_reference_tables_hold_the_70_ranges` are the radius, for the developer or the main session.

**2026-10-11, developer (claude-sonnet-5-5): fix round after the mathematician's C7 correction (db82ac5) and addendum A7.** Docstring, comment and Log corrections only; no assertion, bound, R, B, level or seed changed, with one disclosed exception that is a tightening of a self-check (item 2c).
1. `test_analysis_coverage.py`: "R_ref 20 000 to 40 000" is now "10 000 to 40 000 (C6 10 000; the C7 verdict counts 60 000)". The A4 wording no longer says "one-sided-miss" for the verdict rule: it is the band rule, one-sided for C2, C4 to C6, C8 and C9 and two-sided for C7 (same fix in `expected_verdict`'s docstring and in the tie-test docstring of the smoke; the code was already right). The edge pass and fail reference rates, with the corrected C7 pass entries (0.00103 and 0.00025; ranges (0, 6) and (0, 3), DEF-0022), are stated in a table; the docstring says the C7 pass row cannot fail its bound.
2. `test_wu0006_harness.py`: (a) the C7 truth check's "SE about 3e-3" is the per-chunk SD (3.1e-3); the standard error of the mean is 3.1e-4: corrected. (b) The log-normal "SE near 1e-3" is 3.3e-4 to 5.2e-4: corrected. (c) The bivariate lag-1 check: its bias is 0.46 SE and its false-alarm rate 0.0058 (not 0.0027): stated, 3 SE kept. (d) The tolerance on corr(x4, x1) was 3e-3 = 4.7 SE (SE (1 - 0.36)/sqrt(10^6) = 6.4e-4); I tightened it to 1.9e-3 = 3 SE, the rule of every other self-check, and say so in the docstring. It is a harness self-check of the generator (not a study bound), the new value follows from the stated SE and the 3-SE rule fixed for these checks and not from a result, and the run below tests it once; if it fails it is a finding about the generator. The module docstring's false-alarm sentence is updated (0.6% for the lag-1 check).
3. `test_analysis_null_delta_r2.py`: N1 predicted P(fail) "about 0.5 and 1.0" now reads 0.42 and 0.88. The N2 ("< 0.01") and N3 ("about 0.03") numbers are NOT corrected: each carries a marked note "TO BE REPLACED by the 3000/1000 reference" (they hold at 900/1000 only, addendum A7 items 1 and 2; the mathematician is producing the 3000/1000 reference).
4. Answered: addendum A7 items 1 and 2 (open, marked in the docstring, awaiting the 3000/1000 reference), item 3 (fixed), item 4 (fixed: the R_ref range, the band-rule wording and the edge rates), item 5 (fixed, together with the other Monte Carlo statements above). The F3 and F4 entries above stand; F3 is now resolved by the corrected C7 pass range (db82ac5), which the run-2 count of 0 and 1 satisfies.

**Test run 4, §4.9 checklist.**
1. Change set: `git diff --name-only develop...HEAD` as before plus `tests/slow/wu0006_reference.py` (the mathematician's correction) and the docstring edits of this round; `git status --porcelain` shows the four edited files under `tests/slow/` and this Log until committed (committed before the run).
2. Radius (the tests whose assertion or reference changed, nodes as collected): `test_analysis_coverage.py::test_counts_are_consistent_with_the_reference[C7-0.0]` and `[C7-0.3]` (the corrected C7 ranges), and in `test_wu0006_harness.py`: `test_reference_tables_hold_the_70_ranges` (the tables changed) and `test_delta_r2_design_marginals` (its tolerance changed). The other edits are docstrings, so the rest of the study and of the smoke does not rerun; nothing else depends on `wu0006_reference.py`.
3. Already run? Not on this code: the reference module and the tolerance changed after runs 2 and 3.
4. Device: `JAX_PLATFORMS=cpu`. 5. Threads and time: `LPC_THREADS=4`; expected about 1 minute (the C7 run costs 38 s per phi). 6. Contention: the mathematician's reference simulations may overlap; the owner's authorization allows parallel runs; no GPU use. 7. Output: `-q --tb=short -rfE` by the wrapper.
8. Command: `tools/run_tests.sh slow --background "tests/slow/test_analysis_coverage.py::test_counts_are_consistent_with_the_reference[C7-0.0]" "tests/slow/test_analysis_coverage.py::test_counts_are_consistent_with_the_reference[C7-0.3]" "tests/slow/test_wu0006_harness.py::test_reference_tables_hold_the_70_ranges" "tests/slow/test_wu0006_harness.py::test_delta_r2_design_marginals"`.

**Test run 4 result.** `4 passed in 101.86s (0:01:41)` (`runs/tests/slow-20261011T173439Z.log`, exit 0): `test_counts_are_consistent_with_the_reference[C7-0.0]` and `[C7-0.3]` (run-2 counts: pass 1 and 0, fail 15 and 9, inside the corrected and kept ranges), `test_reference_tables_hold_the_70_ranges` (still 70 ranges, each containing its rate) and `test_delta_r2_design_marginals` with the tightened 1.9e-3 tolerance on corr(x4, x1). The run-2 coverage and delta-R2 results stand; the C7 consistency failure of run 2 (F3) is now resolved by the corrected reference.

**2026-10-11, applied-mathematician (claude-opus-5-5): WU-0006.4 mathematician review, part 2: the null ΔR² reference at 3000/1000 (note addendum A9).**

- **What was run.**
  - `dr2_full_ref.py`: the same replication as the harness's `_delta_replicate`, through production `qn_profile_block` with B = 2000 and blocks of 5. The truth is computed on 10⁵ fresh i.i.d. states.
  - R_ref = 1000 per φ ∈ {0, 0.3}, both targets, scratch seed 20261014.
  - 8 spawned single-thread workers, 16.5 min wall, CPU only.
  - It ran in parallel with an 8-thread CPU pilot preset run (DEV-0, another worktree), under the owner's parallel-run authorization for the WU-0006 slow job as relayed by the main session. The host has 32 cores and the load was about 3, so there was no oversubscription.
  - Integrity: the refit was bitwise in 4000 of 4000 target replications, with 0 failed resamples. The truth's MC SE is 0.051 of the half-width on average (maximum 0.074).
  - My `dr2_full_ref.py`, `dr2_full_ranges.py` and README entry were committed by the main session in f406046 and d6643f3 while the job ran. This commit adds the two logs.
- **VV.3.** The run-2 N counts were known before this reference. They were not used, and they were compared only after the ranges were fixed.
- **Reference and pre-registered values** (R_test = 500; P(fail) of the slow test's bound, mixed over the reference error; range = the WU-0006 rule, central 1 − 0.0005 of Bin(500, p) mixed over N(p, SE²)):

  | φ, target | N1 (P(fail); range) | N2 (P(fail); range) | N3 (P(fail); range) |
  | --- | --- | --- | --- |
  | 0, logit | 0.919 (0.54; [431, 483]) | 0.016 (0.000; [0, 23]) | 0.941 (0.066; [446, 490]) |
  | 0, indicator | 0.933 (0.19; [440, 487]) | 0.019 (0.001; [0, 25]) | 0.945 (0.033; [448, 491]) |
  | 0.3, logit | 0.924 (0.41; [434, 484]) | 0.009 (0.000; [0, 16]) | 0.946 (0.028; [449, 491]) |
  | 0.3, indicator | 0.926 (0.35; [436, 485]) | 0.014 (0.000; [0, 21]) | 0.945 (0.033; [448, 491]) |

  - Mean Δ_cond is −0.0024 to −0.0034 and the half-width is 0.0155 (logit) and 0.0251 (indicator).
  - **Retraction.** The R_ref = 200 values (indicator N2 0.035, N3 0.925) were tail draws, consistent with these at z ≥ −1.8. **My earlier P(fail) figures of 0.25 (N2) and 0.42 (N3), and the N1 figures 0.42 and 0.88, are retracted.**
  - The current docstring of `test_analysis_null_delta_r2.py`, which I prompted, says "0.42 and 0.88" for N1. It should read 0.19–0.54 per row. Its "TO BE REPLACED" lines should take the N2 and N3 values above.
  - `DELTA_R2_REFERENCE` should take the R_ref = 1000 values.
- **Run 2 against these ranges** (compared only after they were fixed): all 12 counts are inside.
- **Meaning for the study's tests.**
  - The always-asserted N2 and N3 rows are not flaky at 0.25 or 0.42. N2 is safe (P ≤ 0.001), and each N3 row fails with P 0.03–0.07.
  - But the 8 always-asserted rows together have **P(at least one spurious failure) ≈ 0.15 per run**. That is too high for a defect test; the consistency ranges give at most 3.5% family-wise.
  - **The cause is the bounds' basis, not the sizes.** N3's bound is nominal − 3 SE (0.921), while the procedure covers Δ_cond at 0.941–0.946 (block-5 undercoverage, as in A1/A2). The margin is only 2.0–2.4 SE, and a larger R does not help (0.012 at R 500 against 0.019 at R 1000 at a true 0.945).
  - **Going back to 900/1000 is not a remedy.** Its reference has N3 0.930 for the logit at φ = 0 (P(fail) about 0.29) and N1 0.86–0.91. It would verify a configuration the study does not use. And choosing sizes by which one passes is the PRIME.2 pattern.
- **Recommendation (owner decides; no test changed by me).**
  - Keep 3000/1000.
  - Put the N2 and N3 nominal bounds under the same switch as A1–A3 (`ASSERT_ROADMAP_BOUNDS`, DEC-0018 K or C).
  - Make the 12 N consistency ranges above the always-asserted defect test (family-wise ≤ 0.6%). They are fixed after run 2, so their first assertion at the next run is a genuine pre-registration.
  - If N2 and N3 stay always asserted, record now that an N3 failure inside its range is a predicted "method" finding (about 15% per run), not a defect.

**2026-10-11, developer (claude-sonnet-5-5): delta-R2 reference replacement and N-row switch (addendum A9, DEC-0018 update by the main session).**
- `wu0006_reference.py`: `DELTA_R2_REFERENCE` is now the A9 table (R_ref = 1000 per phi, seed 20261014), keyed by (phi, target), each cell with the N1, N2, N3 rate, SE, P(bound fails at R = 500) and consistency range, plus mean gain, P(gain > 0) and half-width. The old R_ref = 200 values and their retracted failure probabilities are kept in a dated comment (a documented correction made after run 2, VV.3; the derivation does not use the run-2 counts). Hand-checked against the A9 table: 12 ranges.
- `wu0006_harness.py`: `evaluate_delta` now sends the nominal bounds of N1, N2 and N3 (>= 461, <= 22, >= 461 of 500) to `roadmap` (under `ASSERT_ROADMAP_BOUNDS`, whose default stays True, so nothing is weaker today), and the 12 ranges fill `consistency` (always asserted), with one entry per row in `consistency_rows`. The `always` group is gone. The constant's docstring says so.
- `test_analysis_null_delta_r2.py`: module docstring has the A9 table and the predictions (N1 P(fail) 0.19 to 0.54 per row, N2 at most 0.001, N3 0.03 to 0.07; about 0.15 per run that at least one of the 8 N2 and N3 rows fails under Option K); the "TO BE REPLACED" notes are gone. Tests: 12 consistency nodes `test_count_is_consistent_with_the_reference[<row>-<target>-<phi>]` (always asserted), `test_roadmap_false_distinct_rate_and_conditional_coverage[phi]` (N2, N3, through `enforce`), `test_roadmap_interval_contains_zero[phi]` (N1, through `enforce`), and the unchanged refit test.
- `test_wu0006_harness.py`: fake-data tests of the new logic: `test_evaluate_delta_applies_the_registered_bounds_exactly`, `test_delta_roadmap_rows_follow_the_switch_in_both_modes` (N1, N2, N3 raise under Option K and only report under Option C), `test_evaluate_delta_applies_the_a9_ranges_exactly` (inclusive ends, row by row, both phi) and `test_delta_reference_holds_12_ranges`. `test_reference_tables_hold_the_70_ranges` is unchanged: the 70 earlier ranges are the same set (the delta ranges are a separate set of 12).
- **The 12 real consistency nodes need a fresh delta-R2 study run.** The consistency tests read the counts from `cache.delta`, which runs the study (about 6 minutes per phi on 4 workers, 12 minutes in all, less with 8); the run-2 JSON is not read by any test, and a test that read it would assert against a stale run, not against the code. I therefore did NOT run them and stopped there, as instructed; the run-2 counts (N1 467, 460, 457, 467; N2 8, 10, 8, 8; N3 475, 475, 478, 476) lie inside all 12 ranges (A9), so a rerun with the identical design and seeds is expected to pass them. The rerun is the main session's call.

**Test run 5, §4.9 checklist.**
1. Change set: as before plus `wu0006_reference.py`, `wu0006_harness.py`, `test_analysis_null_delta_r2.py`, `test_wu0006_harness.py` and this Log; committed before the run, `git status --porcelain` clean.
2. Radius: only the tests whose reference or assertion changed, nodes as collected, all in `tests/slow/test_wu0006_harness.py`: `test_reference_tables_hold_the_70_ranges`, `test_roadmap_switch_has_both_modes`, `test_evaluate_delta_applies_the_registered_bounds_exactly`, `test_delta_roadmap_rows_follow_the_switch_in_both_modes`, `test_evaluate_delta_applies_the_a9_ranges_exactly`, `test_delta_reference_holds_12_ranges`, and `test_every_design_runs_end_to_end_and_passes_the_exact_checks` (it runs `evaluate_delta` at R = 2). Not run: the study files (their code path through the pool is unchanged except `evaluate_delta`, covered above) and the 12 consistency nodes (see above).
3. Already run? Not on this code. 4. Device `JAX_PLATFORMS=cpu`. 5. `LPC_THREADS=4`; about 20 s. 6. Contention: other worktrees may run CPU work (authorized); no GPU. 7. `-q --tb=short -rfE`.
8. Command: `tools/run_tests.sh slow` on the seven node ids above.

**Test run 5 result.** `1 failed, 6 passed in 15.52s` (`runs/tests/slow-20261011T175523Z.log`). The failure was an arithmetic error in my own fake-data test `test_evaluate_delta_applies_the_a9_ranges_exactly`: `fake_delta(478, 24, 461)` asks for 478 + 24 = 502 of 500 replications (IndexError in the fake). Fixed to `fake_delta(470, 24, 461)` (N1 470 lies inside both N1 ranges, N2 24 is outside the logit range (0, 23) and inside the indicator range (0, 25)); no reference, range or bound changed. The other six passed: the 70-ranges table test, the switch test, the exact-bounds test, the delta switch test, the 12-ranges table test and the end-to-end tiny-R run.

**Test run 6 (the one fixed test), §4.9 checklist.** 1. Change set: as run 5 plus this fix, committed first. 2. Radius: `test_wu0006_harness.py::test_evaluate_delta_applies_the_a9_ranges_exactly` only (a changed test, rerun with `--lf` semantics by node id). 3. Already run? Yes, on the previous code, where it failed; it changed. 4 to 7 as run 5, about 5 s. 8. `tools/run_tests.sh slow --background tests/slow/test_wu0006_harness.py::test_evaluate_delta_applies_the_a9_ranges_exactly`.

## Review

## Audit
