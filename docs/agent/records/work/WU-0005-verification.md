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

## Review

- **Reviewer:** <actor, not the author>
- **Findings and resolution:**

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:

## Referral

<only if halted; use the form in agent-instructions.md, LPC.AI.13>
