# WU-0005: Code-verification tests (RK4 order, k-d tree, Levina-Bickel, LM residuals, N bound)

| Field | Value |
| --- | --- |
| Status | in progress (WU-0005.1 to .3 now; .4 waits for WU-0002.11, .5 for WU-0002.2) |
| Class | CSQ3 development |
| Agent(s) | claude-sonnet-5-5 (main session) under governance ledger entry 5 (authorizations 4, 6) |
| Estimate | WU-0005.1 S, .2 S, .3 S (this round); .4 M, .5 M later (ROADMAP.md §2) |

## Plan (written before execution)

Planner: claude-opus-5-5, 2026-10-10, on wu/0005-verification at 1574fb4. This plan covers **WU-0005.1 to .3 only**. WU-0005.4 waits for WU-0002.11 and WU-0005.5 waits for WU-0002.2. Both are planned later, in a dated amendment to this section. WU-0005.6 follows .1 to .5.

- **Scope.**
  - **In:** three test-only additions closing the NVVUQ.5 gaps "RK4", "Analog search" and "Levina–Bickel" (`NVVUQ-instantiation-LPC.md`). The design basis is v3 §4 (RK4 step bound; "Levina–Bickel ... on library states") and Methods v2 M4 ("Exact Euclidean k-d tree search"; LB with k = 20 on 2×10⁴ states).
  - **Out:**
    - any change under `lpcstudy/`;
    - `AnalogLibrary.build` and `analog_vectors` (covered by `test_embedding` and `test_data`);
    - the margin Δ and P2(c) (WU-0005.5);
    - V6 step halving (already met);
    - the `workers=-1` thread use in `cKDTree.query` (an observation, listed below).
  - **If a test fails, it is a finding.** Do not change the test. Record it as a DEF and `/refer` it. A fix to `systems`, `ensemble` or `oracle` changes study numbers and is a separate, planned change (PRIME.2).
- **Definition of done:** the three tests below exist with docstrings that give the reference and the tolerance derivation (skill `numerical-test`). Each passes once in the blast radius, with the §4.9 checklist and the summary line in `## Log`. There is one commit per sub-task. The applied-mathematician's confirmations are recorded in `## Log` before execution.

**Acceptance criteria (ROADMAP.md §2, verbatim; fixed. The applied-mathematician may tighten them before execution, never loosen them):**

| Sub-task | Criterion (verbatim) |
| --- | --- |
| WU-0005.1 | Reference: `scipy.linalg.expm(A t) x0` for a fixed 3×3 A with complex eigenvalues (independent of the integrator). Steps h, h/2, h/4 chosen so that the finest error is above 10⁻¹¹ (well above round-off) and the coarsest below 10⁻³; observed order in [3.8, 4.2]. Uses `make_flow_step` on a `SystemSpec` built in the test with the linear field and `max_dt` set to each step. Under 5 s. |
| WU-0005.2 | 10⁴ library vectors in ℝ⁷ and 200 queries from `np.random.default_rng(<fixed>)`: nearest index identical to an exhaustive `np.argmin` of squared distances for every query (exact), nearest distance within 10⁻¹² relative (round-off of a 7-term sum). Second-nearest also checked where the margin is reported. |
| WU-0005.3 | Sets: uniform on a line segment, a unit square and a unit cube embedded in ℝ⁷ by a fixed orthonormal map, 2×10⁴ points, k = 20 (the study's setting). Estimate within ±10% of 1, 2 and 3 respectively; the applied-mathematician confirms this from the estimator's bias and variance at k = 20 and n = 2×10⁴ before execution, and may tighten it. Fixed seed. |

**Test data.** Each test uses `np.random.default_rng(<literal>)` with seeds 50051, 50052 and 50053. This is synthetic data, not a study stream. It keeps the tests independent of `make_rng`, which `test_data` tests, and no study or DEV seed is touched (§4.7, LPC.PC.7).

**WU-0005.1. `tests/unit/test_systems.py::test_rk4_observed_order_is_four` (new file).**
- **Under test:** `make_flow_step` (`lpcstudy/systems.py`).
- **Construction:**
  - A = S B S⁻¹, with B = [[−0.1, −2, 0], [2, −0.1, 0], [0, 0, −0.5]] and S = [[1, 0.5, 0], [0, 1, 0.3], [0.2, 0, 1]]. The eigenvalues are −0.1 ± 2i and −0.5; the test asserts this premise with `np.linalg.eigvals`. A is non-normal and |λ|max ≈ 2.0.
  - `SystemSpec(name="linear", field_fn=lambda s, p: A_jax @ s, params={}, dim=3, observed_index=0, initial_state=x0, max_dt=h)`, with x0 = (1, 0.5, −0.3) and interval T = 1.
  - h ∈ {1/8, 1/16, 1/32}. These are dyadic, so `ceil(T/max_dt)` is exactly 8, 16 and 32 substeps.
- **Reference:** `scipy.linalg.expm(A T) @ x0`.
- **Derivation:**
  - The error of the RK4 stability polynomial is e^z − R(z) = z⁵/120 + z⁶/720 + …, so the global error ≈ (T h⁴/120)‖A⁵ e^{AT} x0‖ ≲ 0.56 h⁴. That gives ≈ 1.4e-4, 8.6e-6 and 5.3e-7.
  - The coarsest is below 1e-3 and the finest above 1e-11, a factor of 5e4. The test asserts both bounds as premises.
  - The round-off floor is about 32 steps × 4 stages × eps × ‖x‖ ≈ 1e-14. The error of `expm` is about 1e-15.
  - The z⁶ term biases the observed order by log₂((1 + z/6)/(1 + z/12)) ≈ +0.03 at z = h|λ| = 0.25.
  - Both pairs, (h, h/2) and (h/2, h/4), must give log₂(e_h / e_{h/2}) ∈ [3.8, 4.2], with ‖·‖₂ error at T. The predicted value is ≈ 4.03. The output dtype must be float64.
- **Proposed addition**, within v3 §4 "RK4 step ≤ …": `test_flow_step_respects_max_dt`. With `max_dt = 0.3` the result equals the result at `max_dt = 0.25` (4 substeps of dt = 1/4), with `atol=1e-15`, since both run the same arithmetic. This checks that the step used never exceeds `max_dt`.
- **Runtime:** three small `fori_loop` compilations, under 2 s.

**WU-0005.2. `tests/unit/test_ensemble.py::test_kdtree_query_matches_brute_force`.**
- **Under test:** `AnalogLibrary.query`, which wraps `cKDTree.query`, reshapes to (n, k) and maps positions to time indices.
- **Construction:**
  - 10⁴ standard-normal vectors in ℝ⁷.
  - `indices = np.arange(10_000) + 41`. The offset tests the position-to-time mapping.
  - `AnalogLibrary(indices, noisy_series=np.zeros(10_041), tree=cKDTree(vectors))`.
  - 200 queries: 190 standard-normal, plus 10 exact copies of library vectors (the zero-distance edge case).
- **Reference:** exhaustive squared distances `((q - vectors)**2).sum(1)`, in chunks of 20 queries (no ‖q‖² − 2q·x expansion, which cancels), then `np.argsort`.
- **Checks:**
  - For k ∈ {1, 2, 5}, where 5 is `config.analog_counts`: the shapes are (200, k).
  - All k indices equal the reference indices + 41 exactly.
  - Distances satisfy `rtol=1e-12, atol=0`, and the 10 copies give exactly 0.0.
  - k = 2 is the second-nearest check. The margin itself is not yet reported in the code (WU-0005.5).
- **Premise asserted:** every reference gap d²₍ⱼ₊₁₎ − d²₍ⱼ₎ > 1e-9·d²₍ⱼ₊₁₎ for j ≤ 5, so the index order is well defined (no ties).
- **Derivation:** a 7-term sum plus a sqrt carries ≤ ~8 eps ≈ 1.8e-15 relative error, so 1e-12 leaves a factor of 500.
- **Bad input:** a query of width 6 raises `ValueError`.
- **Runtime:** under 1 s.

**WU-0005.3. `tests/unit/test_oracle.py::test_local_dimension_known_sets`.**
- **Under test:** `local_dimension` at its default k, asserting that the default is 20 (the value `state_oracles` uses).
- **Construction**, for m ∈ {1, 2, 3}:
  - U = first factor of `qr(rng.standard_normal((7, m)))`, which has orthonormal columns. The offset is c = `rng.standard_normal(7)`.
  - Reference: c + U u for 2×10⁴ points u ~ U[0, 1]^m.
  - Queries: 2000 fresh points drawn uniformly in the interior box [0.2, 0.8]^m. They are not in the reference, as in the study.
- **Estimate:** the median over queries, the statistic H1b uses (`analysis.py`).
- **Derivation (for the applied-mathematician to confirm):**
  - Given T_k, the k − 1 inner neighbors are iid uniform in the ball. Every ball lies inside the set: P(T₂₀ > 0.2) = P(Poisson(≥ 670) < 20) ≈ 0. Hence log(T_k/T_j) are iid Exp(m) and S ~ Gamma(19, rate m), *exactly* for any n.
  - (k − 2)/S therefore has mean m (unbiased), sd m/√17 = 0.243m and median 18m/med Γ(19, 1) ≈ 0.964m, a bias of −3.6%.
  - The Monte Carlo sd of the median at 2000 queries is about 1.25 × 0.243m/√2000 ≈ 0.7% if the queries were independent; shared neighbors inflate it.
  - Even with an inflation of 2, the extreme is −3.6% − 3 × 1.4% = −7.8%, inside ±10%.
  - Boundary queries are excluded on purpose. Truncated balls bias the estimate down for about 37% of cube points (T₂₀ ≈ 0.062), which is a property of the estimator, not a code check.
- **Runtime:** under 1 s.

**Applied-mathematician: confirm before execution.**
- **Q1 (.1):** A, T, h and the error estimates above; the predicted order of 4.03. Tighten [3.8, 4.2]? Proposed: [3.9, 4.1]. Also add a leading-constant check: e at h/4 within 10% of ‖(T h⁴/120) A⁵ e^{AT} x0‖?
- **Q2 (.3):** the exact law of (k − 2)/S for interior queries; the interior-box design and n_q = 2000; a bound on the inter-query dependence; whether to tighten. Proposed: mean within ±3% of m, and median within ±3% of 0.964m.
  - Note that ±10% cannot detect the normalization. Using k − 1 instead of k − 2 gives a mean of +5.9% and a median of +1.8%.
- **Q3 (.2):** optional. Confirm 1e-12 against the round-off bound of about 1.8e-15.

**Affected checks.** The change set is three files under `tests/unit/` plus `docs/`. The rule "single test file: that file only" applies, and `docs/**` needs no tests. The radius is `tests/unit/test_systems.py`, `test_ensemble.py` and `test_oracle.py`, unit tier, CPU. There is no integration tier, since the pipeline is not touched. Use `python3 tools/test_impact.py --explain`, then `--run`, through `tools/run_tests.sh`; run each file once after it is written.

Known gap in §4.2: if a finding later leads to a change in `lpcstudy/systems.py`, the core-module rule misses `tests/unit/test_dynamics.py` and `test_embedding.py`. Both import `systems` directly but are not graph dependents, so add them by hand.

**Order and commits.**
1. WU-0005.2 first. It needs no confirmation; the developer owns it.
2. WU-0005.1, then WU-0005.3, after Q1 and Q2 are answered.

Each is one commit: "WU-0005.k: …", ending `Agent: <model id>`.

**Risks.**
- XLA may differ from the `max_dt` equality check by an ulp. Mitigation: `atol=1e-15`, set now, not after the run.
- Dependence inflation in .3 is larger than estimated (Q2).
- `cKDTree.query(workers=-1)` uses all cores, outside the `LPC_THREADS` cap. This is an observation for the main session, not in this scope; the impact is negligible at these sizes.

**Owner checkpoints (LPC.PC.11):** none expected. The change is test-only and touches no verdict, statistics, seed, provenance or dependency code. `scipy` is already pinned.

**Questions for the owner:** none.

**Open question for the researcher:** which normalization does Levina & Bickel (2005) use: 1/(k − 1) or k − 2 (MacKay–Ghahramani)? And is the global estimate a mean of m̂ or the inverse of a mean of inverses? v3 cites LB 2005 [U], and the code uses k − 2 and the median. This does not block .3 at ±10%, but it bears on Q2.


### Plan amendment 2026-10-10 (before the fix round), claude-sonnet-5-5 (main session), on review finding R2

Two tests go beyond the applied-mathematician's confirmed assertions, and the review asked for a recorded decision: (1) the nonlinear scalar RK4 test (y' = y², y0 = 0.5, T = 1), which the mathematician offered as an addition ("could add") and left to the main session; (2) the characterization of the median of the per-query Levina-Bickel estimates (the code's aggregator over states is a median, not the published arithmetic mean). **Both are accepted** as additional checks; neither loosens or replaces a criterion, both use tolerances the mathematician justified, and both were found sound in review. The median test's docstring is to claim only what it does: it pins the median of the per-query distribution against the exact Gamma law, not the callers' aggregation. See also the review's note on `lpcstudy/oracle.py:62` (an uncounted clamp), now a status line under DEF-0001 on `develop`.

## Log

<dated entries: what was done, commands, results, commits>

**2026-10-10, applied-mathematician (claude-opus-5-5): answers to Q1 to Q3 (before any test is written).** Scratch scripts run CPU-only with 2 threads, outside the repository: no test suite, no preset, no study or DEV seed. The Levina-Bickel numbers use the code's own `local_dimension`, with `cKDTree` patched to `workers=2`.

- **Q1 (WU-0005.1). Confirmed, and tightened.**
  - **Setup.** `make_flow_step` uses `substeps = max(1, ceil(interval/max_dt))` and `dt = interval/substeps`. For T = 1 and h = 1/8, 1/16, 1/32 these are exactly 8, 16 and 32 steps with dt = h. `max_dt` is the only step control.
  - **A.** A = S B S⁻¹ = [[0.75436893, −2.42718447, 0.72815534], [1.96504854, −1.08252427, 0.17475728], [0.05436893, −0.42718447, −0.37184466]]. Its eigenvalues are −0.1 ± 2i and −0.5, and cond(S) = 1.70. x0 = (1, 0.5, −0.3).
  - **Reference.** `scipy.linalg.expm(A)` agrees with a 50-digit Taylor series to 1.2e-15. The code's output is float64 and equals the RK4 stability polynomial R(hA)^N x0 to within 2.2e-15.
  - **Measured errors.** ‖x_ref − x_h‖₂ = 6.94e-5, 4.21e-6 and 2.59e-7 (≈ 0.27 h⁴). The planner's 1.4e-4, 8.6e-6 and 5.3e-7 are upper bounds. The coarsest error is below 1e-3 and the finest is above 1e-11, with a factor of 1e8 over round-off.
  - **Observed orders.** 4.042 for (1/8, 1/16) and 4.024 for (1/16, 1/32). The deviation from 4 is O(h): 0.042, 0.024, 0.013, 0.007 as h halves. The run is deterministic, so round-off moves p by about 1e-8.
  - **Correction to the derivation.** The sign of the leading term is now verified: x_ref − x_h = +(T h⁴/120) A⁵ e^{AT} x0 + O(h⁵).
  - **Final assertions.**
    1. Premises: `np.allclose(sorted eigvals, [−0.5, −0.1−2j, −0.1+2j])`, `e(1/8) < 1e-3`, `e(1/32) > 1e-11`, output dtype float64.
    2. For both pairs, `3.9 <= log2(e_h/e_{h/2}) <= 4.1`. This tightens the roadmap's [3.8, 4.2].
    3. Leading term at h = 1/32: ‖(x_ref − x_h) − L h⁴‖₂ ≤ 0.10 ‖L h⁴‖₂, with L = (T/120) A⁵ expm(AT) x0. The measured value is 0.043. This vector form also checks the direction and sign; the norm ratio alone is 1.019. This is an added check, so it tightens the criterion.
  - **`test_flow_step_respects_max_dt`.** Sound: max_dt = 0.3 and 0.25 both give 4 substeps of 0.25, so the arithmetic is identical. `atol=1e-15` stands.
  - **Limitation.** A linear field tests only the stability polynomial, which is the same for every 4-stage order-4 method. It cannot see an error in the nonlinear order conditions.
  - **Optional (main session decides).** A scalar autonomous ODE has the same order conditions as a system up to order 4, so it checks all of them. Take y′ = y², y0 = 0.5, T = 1, exact value 1. The measured errors are 2.90e-6, 1.84e-7 and 1.16e-8, with orders 3.975 and 3.993, inside [3.9, 4.1].
- **Q2 (WU-0005.3). Law confirmed, with corrections. Statistic: the mean. Tolerance tightened to ±3%.**
  - **Law.** Draws are iid, so given T_k the k − 1 inner neighbors are iid uniform in the ball. When the ball lies inside the set, S = Σ log(T_k/T_j) ~ Gamma(19, rate m) exactly for any n. Then (k − 2)/S has mean m and sd m/√(k − 3) = 0.2425m (exact). Its median is 18m/18.6677 = 0.9642m.
  - **Correction 1: normalization.** k − 1 instead of k − 2 multiplies *every* estimate by 19/18, which is **+5.56%**, not +5.9%. The planner's "median +1.8%" is relative to m. Against its own target 0.9642m the median also moves by +5.56%.
  - **Correction 2: boundary fraction.** The boundary fraction of the cube is **32%**, not 37% (measured 0.318: T₂₀ has mean 0.062 and max 0.078). For the square it is 6.9%, and for the segment 0.1%.
  - **Dependence.** 200 seeds were run for each m, with n = 2e4, k = 20 and 2000 interior queries. The sd of mean/m was 0.0054, 0.0057 and 0.0057 for m = 1, 2, 3. The iid value is 0.00542, so the inflation is 1.00–1.06 (sd of the estimate ≈ 5%): none detectable. The mean of mean/m was 0.9997, 0.9999 and 1.0007. The median/m averaged 0.9641, 0.9643 and 0.9653, with sd 0.006–0.0066.
  - **What ±10% about m catches.** It catches gross errors only: log10 (×0.43), a sign error, a query contained in the reference (estimate ≈ 0), or a factor of 2. It **cannot** catch k − 1 versus k − 2, with either statistic. It barely catches a numerator of k (+11.1% on the mean), and the median misses it (+7.1%).
  - **What ±3% catches.** k − 1 lies 2.56% beyond the bound, which is 4.5σ, so a miss has probability below 1e-5. A false alarm is 5.3σ away, with probability about 1e-6 over the three m. 3% sits near the balanced point of 2.78%.
  - **Boundary.** The exclusion is endorsed. A boundary-inclusive test measures the estimator's truncated-ball bias, not the code. For m = 3 that bias is −2.2% on the mean (median −5.6%), so it would push m = 3 against a ±3% bound. Its reference value would have to come from simulation, so it would not be independent.
  - **Mean or median.** Use the mean. It has an exact reference with no constant, a smaller Monte Carlo sd, and the same sensitivity to the normalization. The median describes H1b's aggregation, which is not the code under test.
  - **Final assertion.** For m ∈ {1, 2, 3}: `abs(est.mean()/m - 1) <= 0.03`, plus the premise `local_dimension.__defaults__ == (20,)`. This tightens the roadmap's ±10%.
  - **Reference run.** With seed 50053 and my draw order, mean/m was 0.9957, 0.9974 and 1.0067.
- **Q3 (WU-0005.2). Confirmed. Assertions unchanged.**
  - **Round-off.** Each of the two computations rounds the difference (u), the square (2u + u) and the 6 additions of nonnegative terms (6u), with no cancellation, for 9u. The sqrt gives 4.5u + u. Each is therefore ≤ 5.5u, and their difference ≤ 11u ≈ 1.2e-15 relative. The planner's 1.8e-15 is consistent. `rtol=1e-12` leaves a factor of about 800.
  - **Measured.** Over 31 seeds, including 50052, 6200 queries gave a relative difference of exactly 0, because the summation order is the same. The 10 copies give exactly 0.0.
  - **Ties.** The smallest relative gap was 1.2e-6 over 37,200 gaps, which implies a gap density near 0 of about 22. That gives P(some gap < 1e-9 in one test) ≈ 3e-5, and an exact float tie about 1e-12.
  - **Premise.** Keep the gap > 1e-9 premise as a hard assert, not a skip: at the fixed seed the minimum gap is 2.2e-5. Use `np.argsort(..., kind="stable")` so that the reference order is deterministic.
  - **Tightening.** Not needed. A wrong neighbor is caught by the exact index check, and any bug in a distance is O(1).

**2026-10-10, developer (claude-sonnet-5-5): WU-0005.2, run 1 (§4.9 checklist).**
1. Change set: `tests/unit/test_ensemble.py` (appended `test_kdtree_query_matches_brute_force`, parametrized k in {1, 2, 5}); plus docs notes and this unit file.
2. Radius: `python3 tools/test_impact.py --explain` gives "test file: that file only" -> `tests/unit/test_ensemble.py`, unit tier; smaller than the whole suite.
3. Already run: no (new code).
4. Device: wrapper sets `JAX_PLATFORMS=cpu`.
5. Threads: `LPC_THREADS` default 4 (wrapper); unit timeout 300 s.
6. Contention: no preset or slow/gpu run started by me.
7. Output: `-q --tb=short -rfE` (wrapper).
8. Command: `tools/run_tests.sh unit tests/unit/test_ensemble.py`.

**2026-10-10, developer (claude-sonnet-5-5): WU-0005.2 result.** `tools/run_tests.sh unit tests/unit/test_ensemble.py --durations=5`: `4 passed in 0.84s` (slowest new case 0.24 s). Measured by a scratch script after the run (not a test run): smallest relative gap 1.8e-4 (premise 1e-9); max relative distance difference k-d tree vs brute force 0.0 (tolerance 1e-12); indices identical; copies at exactly 0.0. After the run, only the docstring sentence quoting the minimum gap was corrected (1.8e-4 measured here, not the mathematician's 2.2e-5 from another draw order); no code or tolerance changed. No code defect.

**2026-10-10, developer (claude-sonnet-5-5): WU-0005.1, run 1 (§4.9 checklist).**
1. Change set: new `tests/unit/test_systems.py` (`test_rk4_observed_order_is_four`, `test_rk4_observed_order_nonlinear_scalar`, `test_flow_step_respects_max_dt`); nothing under `lpcstudy/`.
2. Radius: `python3 tools/test_impact.py --explain` maps `test_systems.py` -> "test file: that file only"; it also lists `test_ensemble.py` (branch diff), which already ran at the same code (WU-0005.2 result above), so only `tests/unit/test_systems.py` runs. No `lpcstudy/` change, so `test_dynamics.py`, `test_embedding.py` are not added.
3. Already run: no (new file).
4. Device: wrapper sets `JAX_PLATFORMS=cpu`.
5. Threads: `LPC_THREADS` default 4; unit timeout 300 s.
6. Contention: none started by me.
7. Output: `-q --tb=short -rfE`.
8. Command: `tools/run_tests.sh unit tests/unit/test_systems.py --durations=5`.
Note: the nonlinear check is feasible without touching `lpcstudy/`: `make_flow_step` takes any `field_fn(state, params)` from the spec, so `lambda s, p: s * s` with dim = 1 works.

**2026-10-10, developer (claude-sonnet-5-5): WU-0005.1 result.** `tools/run_tests.sh unit tests/unit/test_systems.py --durations=5`: `3 passed in 0.69s` (slowest 0.21 s). Values measured by a scratch script after the run (not a test run), matching the mathematician's: linear errors 6.94e-5, 4.21e-6, 2.59e-7; orders 4.042 and 4.024 (band [3.9, 4.1]); leading-constant residual 0.0425 (bound 0.10); nonlinear errors 2.90e-6, 1.84e-7, 1.16e-8, orders 3.975 and 3.993 (band [3.9, 4.1]); `max_dt` 0.3 vs 0.25 max abs difference 0.0 exactly (atol 1e-15); `max_dt` 0.5 differs from 0.25 by 1.7e-2. No code defect.

**2026-10-10, developer (claude-sonnet-5-5): WU-0005.3, run 1 (§4.9 checklist).**
1. Change set: `tests/unit/test_oracle.py` (helpers `_uniform_known_dimension`, `_assert_interior`; `test_local_dimension_known_sets[m]`, `test_local_dimension_median_poisson_value[m]`, m in {1, 2, 3}); nothing under `lpcstudy/`. Committed so far on the branch: `test_ensemble.py` (.2), `test_systems.py` (.1), both already run.
2. Radius: `python3 tools/test_impact.py --explain` -> "test file: that file only"; it lists test_ensemble, test_oracle, test_systems because of the branch diff; the first and last already ran on unchanged code, so only `tests/unit/test_oracle.py` runs.
3. Already run: no (new tests); `tests/unit/test_oracle.py` has not run on this branch.
4. Device: wrapper sets `JAX_PLATFORMS=cpu`.
5. Threads: `LPC_THREADS` default 4 (`local_dimension` uses `workers=-1` in `cKDTree.query`, an observation already listed in the plan risks); unit timeout 300 s.
6. Contention: none started by me.
7. Output: `-q --tb=short -rfE`.
8. Command: `tools/run_tests.sh unit tests/unit/test_oracle.py --durations=8`.
Tolerances fixed before the run: mean `abs(mean/m - 1) <= 0.03`; median `abs(median/(0.9642 m) - 1) <= 0.03`, the constant computed as 18/median(Gamma(19)).

**2026-10-10, developer (claude-sonnet-5-5): WU-0005.3 result.** `tools/run_tests.sh unit tests/unit/test_oracle.py --durations=8`: `12 passed in 1.03s` (slowest new case 0.34 s, includes the first import of scipy.stats). Values measured afterwards by a scratch script (not a test run), seed 50053: mean/m - 1 = -0.0043, -0.0026, +0.0067 for m = 1, 2, 3 (bound 0.03); median/(0.9642 m) - 1 = -0.0063, +0.0044, +0.0114 (bound 0.03); median/m = 0.9581, 0.9685, 0.9752; the k - 1 normalization would give mean/m - 1 = +0.051, +0.053, +0.063, all beyond the 0.03 bound (the test would catch it). No code defect. Self-check of the three diffs: no `clip`, `nan_to_num`, `isfinite`, `where(`, `try`, `except`; randomness only from fixed `np.random.default_rng(<literal>)` (50052 in .2, 50053 in .3; .1 has no random data, 50051 unused); no tolerance loosened (3.9/4.1, 10%, 1e-12, 1e-15, 0.03 are the confirmed values).

**2026-10-10, developer (claude-sonnet-5-5): fix round 1 (R1 to R3), docstrings only, before the run (§4.9 checklist).**
1. Change set: docstrings in `tests/unit/test_systems.py` (R1: the nonlinear test checks order-1 to 3 conditions through the nonlinearity plus one weighted sum of the non-tall order-4 conditions, not sum b c^3 = 1/4, since f''' = 0; the linear test's Limitation sentence no longer claims the scalar test covers the nonlinear conditions), `tests/unit/test_oracle.py` (R2: the median test computes `np.median` itself and pins the per-query distribution against the Gamma law, with no claim about callers; the mean test's cross-reference reworded likewise), `tests/unit/test_ensemble.py` (R3: gap "measured by a scratch script after the first run", the 1e-9 threshold fixed in the plan). No assertion, tolerance, seed or code changed.
2. Radius: `tools/test_impact.py --explain` gives the three files, unit tier, smaller than the whole suite.
3. Already run: the three files ran on the previous code; the test files have changed (docstrings), so one run of the set follows.
4. Device: wrapper sets `JAX_PLATFORMS=cpu`. 5. `LPC_THREADS` default 4, unit timeout 300 s. 6. No contention. 7. `-q --tb=short -rfE`.
8. Command: `tools/run_tests.sh unit tests/unit/test_ensemble.py tests/unit/test_systems.py tests/unit/test_oracle.py`.
Result: `19 passed in 3.04s`. Commit: "WU-0005 fix R1-R3: ..." (hash in the report).

### Resolution of findings (WU-0005.1 to .3), 2026-10-10, claude-sonnet-5-5 (main session)

- **R1, R2, R3: fixed in fbe2cc7** (docstring changes only). Checked by the main session: an `ast` comparison of `tests/unit/test_ensemble.py`, `test_systems.py` and `test_oracle.py` before (718580a) and after, with docstrings stripped, is identical for all three. The developer ran the three files once after the fix: `19 passed in 3.04s` (the reviewer's independent run before the fix: `19 passed in 2.27s`).
- **R2 decision recorded:** the nonlinear RK4 test and the median characterization test are accepted (plan amendment above).
- **Status of the unit:** WU-0005.1 to .3 are done and reviewed; the unit stays **open** for .4 (needs WU-0002.11) and .5 (needs WU-0002.2), with their own plans and review. No merge gate yet: this part is merged to `develop` only; the gate runs when `develop` is proposed for `main`.
- **Observation for WU-0002.11:** `lpcstudy/oracle.py:62` clamps zero neighbour distances without counting them (a status line under DEF-0001 on `develop`).

## Review

- **Reviewer:** reviewer (claude-opus-5-5), fresh context, 2026-10-10. Scope: WU-0005.1 to .3 (commits 40cf427, d6db030, 52e8a2a, 718580a) against `develop`. The unit stays open for .4 and .5.
- **Blast radius (hand-derived, rule "test file: that file only", no `lpcstudy/` change), run once:** `tools/run_tests.sh unit --durations=8 tests/unit/test_ensemble.py tests/unit/test_systems.py tests/unit/test_oracle.py` gives `19 passed in 2.27s` (slowest 0.33 s; every case is under 5 s).
- **Independent recomputation (scratch script outside the repo, not a test run).**
  - **RK4.** A pure-NumPy RK4 against `expm` gives errors 6.94e-5, 4.21e-6 and 2.59e-7, orders 4.042 and 4.024, and a leading-term residual of 0.0425.
  - **y' = y².** Errors 2.90e-6, 1.84e-7 and 1.16e-8, orders 3.975 and 3.993.
  - **Levina-Bickel and the tree.** The constant is 18/med Γ(19) = 0.96423. At seed 50053, mean/m − 1 = −0.0043, −0.0026 and +0.0067. The smallest relative gap in the tree test is 1.75e-4.
  - **Agreement.** All of these match the docstrings and the log.
- **Mutation probes** (monkeypatched in the scratch script; nothing in the repo changed). Every mutant is caught by at least one test in the radius:
  - substeps + 1: caught by both order tests;
  - `floor` for `ceil`, and dt = max_dt: caught by `test_flow_step_respects_max_dt`;
  - k4 built from k2: caught by both order tests;
  - LB numerator k − 1, skipping the nearest neighbour, and k − 1 neighbours: caught by the mean test and the median test, for every m;
  - tree, skipping the nearest neighbour, and index + 1: caught for k = 1, 2 and 5.
- **Checks that pass.**
  - The references are independent: `expm`, the closed form 1/(1/y0 − t), brute force with `argsort(kind="stable")`, and the exact Gamma law with `scipy.stats`.
  - The tolerances are exactly the confirmed ones or tighter: [3.9, 4.1] for both pairs, the vector leading-term check within 10%, exact indices, rtol 1e-12 with atol 0, and 3% on the mean.
  - Seeds are literal `default_rng`, used for test data only. float64 is asserted.
  - Only three test files changed, and no lines were removed. Nothing changed under `lpcstudy/`, and no `lpcstudy` imports changed.
  - d6db030 changes only docstring text, with no code or tolerance change.
  - The commits name the unit and carry `Agent:`.
  - The y' = y² test is legitimate: it uses a lambda `field_fn` in a test-built `SystemSpec`, and its band is the mathematician's.
  - The claim that the published aggregator is the arithmetic mean (eq. 9) agrees with the research note.
  - The median test is correctly not named `test_regression_*`, because its reference is the exact Gamma law and not the code's own output. Its docstring says honestly that a 3% bound about 0.964m does not separate the median from m (+3.7%, about 1 sd beyond).
  - No owner checkpoint: the change is test-only.
- **Findings and resolution:**
  - **R1 (low, accuracy of evidence). `tests/unit/test_systems.py:81-83` (and the "Limitation" sentence at :59-61).**
    - **What.** The docstring says that y' = y² exercises "the nonlinear conditions ... all".
    - **Why it matters.** For f = y², f''' ≡ 0, so the elementary differential of the bush tree, f'''(f, f, f), vanishes. The condition Σ bᵢcᵢ³ = 1/4 therefore never enters the error. The other three order-4 trees all have F(t) ∝ y⁵, so a single scalar ODE checks only one weighted sum of their defects. The equivalence "scalar = system up to order 4" holds for the class of scalar ODEs, not for one f. The applied-mathematician's log entry carries the same overstatement.
    - **Fix.** Reword both docstrings to say the test exercises Σ bc² = 1/3 and one combination of the non-tall order-4 conditions, and not Σ bc³ = 1/4. No assertion or tolerance changes. A field with f''' ≠ 0 would need the mathematician's confirmation first and is optional.
  - **R2 (low, scope and records, LPC.PC.1).** Two tests are beyond the confirmed assertions, with no recorded decision.
    - **What.**
      - `test_rk4_observed_order_nonlinear_scalar` (`test_systems.py:78`) was marked "Optional (main session decides)", and no decision is in `## Log`.
      - `test_local_dimension_median_poisson_value` (`test_oracle.py:229`): the mathematician's Q2 answer was "Use the mean", and the final assertion is the mean only. The median bound is the planner's proposal, supported by the mathematician's numbers.
    - **Why it matters.** The definition of done says "the three tests below". The additions are sound and tighten nothing wrongly, but the plan does not cover them.
    - **Fix.** The main session adds a dated plan amendment or log decision accepting both tests, with their tolerances, before close. Also trim the median docstring's first sentence: the test computes `np.median` itself and pins the median of the per-query law. It does not exercise the callers' (H1b, `analysis.py:102`) aggregation.
  - **R3 (low, provenance wording). `tests/unit/test_ensemble.py:48-49`.**
    - **What.** The docstring says the 1.8e-4 gap was "measured before the test was fixed". The developer's log says it was measured by a scratch script after the run, and the docstring was corrected in d6db030.
    - **Fix.** Reword it as "measured after the first run; the premise threshold 1e-9 was fixed in the plan".
- **Observation (not a finding, outside this diff).** `lpcstudy/oracle.py:62`, `np.maximum(dist, 1e-300)`, is an uncounted clip (PRIME.4). It is pre-existing, and the interior premise of these tests never triggers it. It belongs to the main session's queue, not to this unit.
- **Verdict: approve with fixes** (3 findings, all low; no code defect; no criterion loosened).

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:

## Referral

<only if halted; use the form in agent-instructions.md, LPC.AI.13>
