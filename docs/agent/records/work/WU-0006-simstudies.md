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

## Review

## Audit
