# V6 margin under redrawn states: the law of the gate statistic, per-seed failure probabilities, and amended M5(d) and risk R1 (WU-0002.14, P1 review finding R1)

DEVELOPMENT (DEV-0, plus literal scratch seeds): not a hypothesis test.

Date: 2026-10-13. Agent: applied-mathematician (claude-opus-5-5). Worktree `wu/0002-14-seeded-states` at 4fd0ef7.

**Scope.** This note answers finding R1 of `docs/agent/records/work/WU-0002.14-review-P1.md`. It does three things:
1. It explains why V6 has a heavy-tailed law across seeds, and why the M5(d) estimate was wrong.
2. It estimates the per-seed probability that V6 fails, and the same for V4 and V2.
3. It drafts the amended text of M5(d), of the hypothesis row H3 and of risk R1.

It changes no bar, no criterion and no code. The owner decides any bar question.

**What was run.**
- **Scratch scripts only**, on CPU within `LPC_THREADS = 4`. They import `lpcstudy/` read-only (`build_context`, `check_integrator`, `make_flow_step`, `simulate_trajectory`). `mech.py` and `refcheck.py` also contain two references independent of the package: a NumPy RK4 and a SciPy DOP853 integrator.
- **Seeds.** DEV-0 (`config.seed` = 20261005) only to rebuild the P0 and P1 test states. Every other draw uses literal scratch seeds (`default_rng(140006)`, `(140007)`, `(5)`, `(7)`).
- **Not run:** no preset, no test, no suite and no GPU. Nothing was written to either run directory; the Lyapunov caches were copied to the scratchpad. The confirmatory seed was not read, drawn or run.
- **Scripts and logs** are committed in `2026-10-13-v6-margin-scripts/` (REPRO.10). The commands are in §6.

---

## 0. Determinations

| Item | Determination |
| --- | --- |
| V6 law | V6 is the **maximum of 20 draws** of a per-state deviation D(s), s ~ μ. D spans 4 to 7 decades on the attractor. Its tail is set by the finite-time stretching over the 1-LT window, and for Chua also by the breakpoint crossings of the diode, where RK4 is not 4th order. So P(V6 ≥ c) ≈ 20·μ(D ≥ c). |
| Reproduction | `check_integrator` was re-evaluated on the rebuilt P0 and P1 test states. It reproduces all six recorded V6 values **bitwise**. The independent NumPy RK4 reproduces D to 3 significant digits at all 48 states checked. |
| **P(V6 fails), per fresh seed** | **Chua 4.4%** (95% CI 4.0 to 4.9%). **Lorenz-63 0.11%** (0.06 to 0.16%). **Rössler 0** (the per-state D never exceeds 4.45e-5, 22× below the bar). **Any system: 4.5%** (4.0 to 5.1%). |
| P0 and P1 against this law | Percentile ranks: Lorenz 0.53 (P0) and 0.994 (P1); Rössler 0.15 and 0.79; Chua 0.075 and 0.70. A KS test of uniformity on the 6 ranks gives D = 0.20, p = 0.93, so the law is consistent with every observed draw. P1 Lorenz was an unlucky draw (about 1 in 170) of a benign law. **P0 Chua was a lucky draw**: the 13× margin in M5(d) came from the 7.5th percentile. |
| Why M5(d) was wrong | It read one realization as if V6 were a deterministic discretization error with a fixed margin (bar / value). The a5cd75b pilot, the v1 baseline and P0 share one state sample. Chua's median V6 margin is 5.1×, its 95th percentile is 1.05×, and its 99th percentile fails (2.5e-3). |
| P(V4 fails), per fresh seed | **Poorly determined from n = 2 realizations.** The plug-in estimate is 2% (Lorenz), 15% (Rössler) and 15% (Chua). Over the 95% CI of the between-seed spread it ranges from 0 to 29% (Lorenz) and from 3 to 39% (Rössler, Chua). For any system: plug-in 29%, predictive 46%. M5(d)'s "2 to 10%" sits at the low end of what the data allow. |
| V2 | The per-state minimum (0.838 in P1) is a minimum over **5** states (`check_cramer_rao(n_states=5)`), not 20. It is not gated. The gated median lies 6.4 SDs from the nearer edge. Distribution-free bound: P(fail) ≤ 0.9% per system (95%). Essentially 0 under a Gaussian model. |
| V1, V5, V7 | No new information; M5(d) stands. |
| N4 / gate risk per fresh seed | **At least 4.5% from V6 alone**, which is well determined. With V4 included, plausibly 10% to 50%, and the V4 share is not determined. |
| Sealed run | A gate failure cannot be retuned (PRIME.2; DEC-0027(3) as the review cites it). v3 E0 marks that system's results provisional, and the caller's brief treats it as a hard stop. The V6 law is preset-independent, so these probabilities apply to the confirmatory run. Neutral options are in §5. |

---

## 1. What V6 is, and its law under redrawn states

### 1.1 Definition (code at 4fd0ef7, read-only)

`validation.check_integrator(ctx, n_states=20, horizon=30)`:

V6 = max over i = 1..20 of D(s_i), where

D(s) = max over j = 0..30 of |x_j^{(h)}(s) − x_j^{(h')}(s)| / σ_x.

- **The integrators.** x^{(h)} is the production map: RK4 with n_c = ⌈Δ/max_dt⌉ substeps per observation interval Δ = 1/(30 λ). x^{(h')} uses `max_dt/2`, which gives n_f = ⌈2Δ/max_dt⌉ substeps:
  - Lorenz-63: n_c = 4, n_f = 8;
  - Rössler: 12 and 24;
  - Chua: 16 and **31** (so h/h' = 1.94 for Chua, not 2).
- **The states.** s_i = `eval_states[test[i]]`, the first 20 states of the test split. They are spaced by `spacing` = 45, 150 and 150 steps, so the 1-LT windows (30 steps) are disjoint.
- **The gate.** It passes when V6 < 1e-3 (`gate_status`).
- **Preset independence.** `n_states`, `horizon`, `spacing` (from `thinning_factor` = 5 and `theiler_window` = 30), Δ and σ_x are identical at the pilot and full presets (checked from `PRESETS`). So the law below is also the law of V6 at the confirmatory run.

**Where the seed enters.** The test block starts a fixed number of steps after the main trajectory's first post-burn-in state. By M1(a) (KS-checked) that state is a fresh draw from the invariant measure μ of the RK4 map. So under a redraw, the block start u is distributed as μ, and

V6(seed) = max over k < 20 of D(Φ^{u + k·spacing}),  with u ~ μ.

Hence, with p(c) = μ{D ≥ c}:

P(V6 ≥ c) = P(∪_k {D(s_k) ≥ c}) ≤ 20·p(c), with equality to first order in p. The windows are disjoint, and a single dangerous passage lasts a few steps, far fewer than the spacing.

**V6 is therefore a sample maximum.** It is not a stable property of the integrator. Its law across seeds is the law of the largest of 20 draws of D, and the upper tail of that law is the upper tail of D.

### 1.2 Why D is heavy-tailed

**The error representation.** The global error of the coarse map after j steps is

e_j ≈ Σ_k DΦ(t_j, t_k) τ_k,

where τ_k is the local truncation error of substep k and DΦ is the tangent propagator. The halving difference is D ≈ |e^{(h)} − e^{(h')}|. When RK4 is in its asymptotic regime, D ≈ (1 − (h'/h)^4)|e^{(h)}| ≈ 0.94|e^{(h)}|. So D is roughly (local error size) × (stretching of the tangent map over at most 1 LT). Both factors vary strongly along the attractor.

**(a) Finite-time stretching.** Let σ₁ be the largest singular value of the 30-step tangent map. Over 4000 random states per system:

| System | ln σ₁, median | ln σ₁, 99th percentile | top 1% of D: median ln σ₁ | 12 largest D episodes: ln σ₁ | Spearman(log D, ln σ₁) |
| --- | --- | --- | --- | --- | --- |
| Lorenz-63 | 1.83 | 5.81 | 6.06 | 8.8 to 9.9 | 0.20 |
| Chua | 2.42 | 5.12 | 4.93 | 7.5 to 8.9 | 0.35 |

- **Reading.** The bulk of D is governed by the local error, through the speed and curvature of the window, so the overall rank correlation is modest. The tail is governed by stretching. The largest deviations sit at the extreme 1-LT stretching factors, e^7.5 to e^10 (about 2·10³ to 2·10⁴). Where on the attractor these passages lie was not localized further here.
- **Rössler's stretching is uniformly mild.** Its per-state D is bounded: the maximum is 4.452e-5, reproduced in each of 5 independent orbits.

**(b) Chua: the diode's breakpoints.** The Chua field is Lipschitz, but its Jacobian jumps on |x| = 1. On a substep that crosses a breakpoint, the solution has a jump in its second derivative, so the RK4 local error there is O(h³) rather than O(h⁵). Its constant depends on where the crossing falls within the substep. Windows with crossings are therefore not in the order-4 regime.

Measured against an independent DOP853 reference:
- **Windows that stay in one linear region** show exactly p = 4.00 and D ≈ 6e-9.
- **Windows with crossings** show erratic observed orders, from −0.4 to 9.4, and D is larger by orders of magnitude.

Crossings multiplied by stretching make Chua's tail far heavier than Lorenz's, although the two medians are similar.

**Per-state law of D** (10⁶ states per system: 5 independent orbits × 2·10⁵, 3000-step burn-in):

| System | 50% | 90% | 99% | 99.9% | max | μ(D ≥ 1e-3) (states; episodes) |
| --- | --- | --- | --- | --- | --- | --- |
| Lorenz-63 | 9.9e-6 | 2.3e-5 | 7.3e-5 | 2.9e-4 | 1.42e-3 | 5.5e-5 (55; 22) |
| Rössler | 1.65e-5 | 3.25e-5 | 4.28e-5 | 4.43e-5 | 4.45e-5 | 0 |
| Chua | 1.3e-5 | 8.9e-5 | 4.0e-4 | 1.6e-3 | **4.0e-2** | 2.27e-3 (2274; 277) |

Per-orbit μ(D ≥ 1e-3) for Chua is 1.6, 2.4, 2.4, 2.5 and 2.5 (×10⁻³), which is consistent across orbits. For Lorenz it is 0.5 to 10 (×10⁻⁵): with only 22 episodes, it is Poisson-dominated.

### 1.3 Solution verification at the tail states (skill `convergence-study`)

**Setup.**
- **QoI:** e_h = max over j of |x_j^{(h)} − x_j^{ref}| / σ_x, over the 1-LT window.
- **Levels:** n_c, 2n_c, 4n_c and 8n_c substeps (r = 2).
- **Reference:** SciPy DOP853 at rtol 1e-13.
- **Reference accuracy, Chua tail states:** it differs from DOP853 at rtol 1e-10 by ≤ 5.3e-6 σ_x, and from RK4 at 128 n_c by ≤ 1.5e-6 σ_x (`refcheck.log`). The two coarsest levels are therefore accurate to a few per cent. The two finest levels at the Chua tail states (1.5e-5 to 2e-4) carry up to about 30% reference error, so p2 and p3 there are indicative.

Excerpt (full table in `mech.log`):

| State | D (library) | D (NumPy) | e_h | e_h/2 | e_h/4 | e_h/8 | p₁ | p₂ | p₃ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Lorenz top (22731) | 1.40e-3 | 1.40e-3 | 1.49e-3 | 9.12e-5 | 5.64e-6 | 3.51e-7 | 4.03 | 4.01 | 4.01 |
| Lorenz random (161000) | 1.37e-5 | 1.37e-5 | 1.44e-5 | 8.82e-7 | 5.44e-8 | 3.38e-9 | 4.03 | 4.02 | 4.01 |
| Chua top (179261) | 4.03e-2 | 4.03e-2 | 4.07e-2 | 6.07e-5 | 3.04e-5 | 1.51e-5 | 9.39 | (1.0) | (1.0) |
| Chua top (138297) | 2.58e-2 | 2.58e-2 | 1.51e-2 | 4.45e-3 | 9.93e-4 | 1.05e-4 | 1.76 | 2.17 | (3.2) |
| Chua random, no crossing (134158) | 5.8e-9 | 5.8e-9 | 6.28e-9 | 3.91e-10 | 2.44e-11 | 1.49e-12 | 4.00 | 4.00 | 4.03 |
| Chua random, crossings (55584) | 3.24e-4 | 3.24e-4 | 2.38e-4 | 1.46e-4 | 7.69e-6 | 5.68e-6 | 0.70 | 4.25 | (0.4) |

- **Lorenz-63.** It is in the asymptotic regime at every state checked, the tail included: p = 4.00 ± 0.05 against the formal order 4. D/e_h = 0.94 ≈ 1 − 2⁻⁴. V6 is a faithful Richardson estimate of the production map's 1-LT deviation from the flow.
- **Chua.** Wherever a window crosses a breakpoint, the formal order is not attained, as the skill anticipates for the diode's breakpoints. D is still within a factor of 0.59 to 1.71 of the true coarse error e_h at the 12 tail states. So V6 measures a real map-to-flow deviation of that size, not an artefact of the halving. It is not an asymptotically exact error estimate there.
- **Not a code defect.** The library and the independent NumPy RK4 agree at every state. The QoIs are defined on the discrete map (LPC.NV.1), so this affects V6's interpretation (row H3, §4.3) and not the validity of any hypothesis test.

### 1.4 Why M5(d) was wrong

1. **One realization read as a margin.** The M5(d) values (3.9e-5, 3.3e-5, 7.5e-5) came from a5cd75b. Its test states are identical to P0's and to the v1 baseline's, because main used to continue the statistics orbit. "≥ 13×" was bar / value for one draw.
2. **A sample maximum treated as a deterministic error.** For a discretization error at a fixed state, a 13× margin would mean "≈ 0 risk". V6 is instead the maximum of 20 draws of a quantity whose 99.9th percentile is 125 times its median (Chua), so a margin read from one draw says little about the next.
3. **The draw was in Chua's lower tail.** P0's 7.5e-5 is Chua's 7.5th percentile. The law's median is 1.96e-4 (margin 5.1×) and its 95th percentile is 9.5e-4 (margin 1.05×).
4. **No h⁴ argument applies to Chua** (§1.3), so no "small error at the step size" reasoning could have bounded the tail.

P1's Lorenz value of 4.83e-4 is the 99.4th percentile of a law that fails only 0.11% of the time. It looked alarming against M5(d), but it is not where the risk lies. The material V6 risk is Chua's: P0's draw hid it, and P1's draw (the 70th percentile) did not reveal it either.

---

## 2. Per-seed failure probabilities

### 2.1 V6 (well determined)

**The V6 law.** Each synthetic seed is a block start u on a long orbit, and V6(u) is evaluated exactly by sliding windows: 20 states at the production spacing. CIs come from a moving-block bootstrap over 95 orbit segments of 10⁴ starts (≫ an episode length), with 4000 resamples (`law.py`).

| System | V6 median | 90% | 95% | 99% | 99.9% | **P(V6 ≥ 1e-3)** | 95% CI | P0 rank | P1 rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Lorenz-63 | 3.8e-5 | 1.0e-4 | 1.6e-4 | 4.0e-4 | 1.03e-3 | **1.1e-3** | [6.2e-4, 1.6e-3] | 0.53 | 0.994 |
| Rössler | 3.7e-5 | 4.35e-5 | 4.39e-5 | 4.44e-5 | 4.45e-5 | **0** | (D ≤ 4.45e-5 on 10⁶ states) | 0.15 | 0.79 |
| Chua | 2.0e-4 | 5.7e-4 | 9.5e-4 | 2.5e-3 | 1.1e-2 | **4.4e-2** | [4.0e-2, 4.9e-2] | 0.075 | 0.70 |

- **Any system:** 1 − (1 − 0.0443)(1 − 0.0011) = **4.5%** (4.0 to 5.1%). The three systems' test states are drawn from independent generators, so the systems are independent.
- **Chua beyond the bar:** P(V6 ≥ 2e-3) = 1.4%, P(V6 ≥ 5e-3) = 0.31%, P(V6 ≥ 1e-2) = 0.11%.
- **Check on the computation:** 20·μ(D ≥ 1e-3) gives 1.10e-3 (Lorenz) and 4.55e-2 (Chua), against the direct 1.08e-3 and 4.48e-2. The union bound is tight, as §1.1 predicts.

**Hypotheses of this estimate, and where they are checked (NVVUQ.14).**

| Hypothesis | Check |
| --- | --- |
| A1. The test-block start is μ-distributed. | M1(a) of the unit: iid KS of post-burn starts against the orbit, p ≥ 0.33. The block lies ≥ 10⁵ steps after the start. |
| A2. 5 × 2·10⁵ states sample μ's tail. | Per-orbit agreement (§1.2): Chua is tight. For Lorenz, 22 episodes give the wider CI, which is reported. |
| A3. Same code and law as the sealed run. | `check_integrator` reproduces P0 and P1 bitwise. The law is preset-independent (§1.1). The confirmatory run uses the same code, unless `validation.py` or `systems.py` changes. |
| A4. Round-off is irrelevant. | The values that decide P(fail) are D ≥ 1e-4 σ_x; the round-off in x is about 1e-15 relative, 10 orders smaller. |

What remains uncertain is the Monte Carlo error above. The model rests only on A1, which is verified.

### 2.2 V4 (poorly determined): what n = 2 can and cannot say

**What we have.** The gated value is the median, over 40 states, of the per-state bootstrap half-width of the clipped weight w* at M = 200. Only that median (at M = 50, 200 and 800) is stored. No per-state half-widths, no dumps. Earlier pilots (a5cd75b, the v1 baseline, `pilot_results_v1.json`) share P0's states and seeds, and their V4 values agree with P0's to 1e-9, so they add nothing. That leaves **two independent realizations per system**:

| System | P0 | P1 | Geometric mean | Margin to 0.05 |
| --- | --- | --- | --- | --- |
| Lorenz-63 | 0.0370 | 0.0187 | 0.0263 | ×1.90 |
| Rössler | 0.0390 | 0.0334 | 0.0361 | ×1.39 |
| Chua | 0.0308 | 0.0420 | 0.0360 | ×1.39 |

**Model (an assumption, not verified).** Take log V4 ~ N(μ_s, σ²), with σ common to the systems. The pooled within-system estimate is s = 0.314 on 3 df, with 95% CI [0.178, 1.17]. Without Lorenz it is 0.174 on 2 df. The Lorenz pair (a factor of 2) dominates. M5(d) assumed SD(median)/median ≈ 0.14 to 0.2, which lies at or below the lower CI end.

| System | Plug-in P(fail) | Predictive (t₃, μ and σ estimated) | Plug-in over the σ CI |
| --- | --- | --- | --- |
| Lorenz-63 | 0.020 | 0.096 | 0.000 to 0.29 |
| Rössler | 0.149 | 0.229 | 0.033 to 0.39 |
| Chua | 0.146 | 0.227 | 0.031 to 0.39 |
| Any system | 0.29 | 0.46 | about 0.06 to 0.7 |

**What can be concluded.**
- Rössler and Chua sit at ×1.39 on average and moved by 16% and 36% between two draws.
- A per-seed V4 failure rate of several per cent per system is the low end of what the data allow. "≈ 15% per system" is the central estimate.
- M5(d)'s "2 to 10% per system" is not supported as an upper bound.

**What cannot be concluded.**
- σ is known only to within a factor of 6.6.
- Log-normality and a common σ are untested.
- Whether the Lorenz halving reflects a change in the share of states at the clip (w* = 0 or 1, half-width near 0) is plausible but unverified: the per-state half-widths are not stored. The M = 50 to 200 ratio was 1.65 in P1 against 1.96 in P0, which fits that reading.
- **Only more realizations narrow this.** Each extra seed adds 1 df per system: DEV-1 and DEV-2 together take the pooled df from 3 to 9, which shrinks the σ CI to about [0.69 s, 1.83 s], that is [0.21, 0.57] at s = 0.31.

### 2.3 V2

- **The gated statistic.** It is the median of **5** per-state ratios (`check_cramer_rao(n_states=5, n_draws=200, noise=1e-4, seed=0)`), each a Monte Carlo mean over 200 fixed-seed draws. The per-state spread estimated from the six (min, median, max) triples (mean range / 2.326 for n = 5) is SD ≈ 0.047. The six medians have mean 0.982 and SD 0.028.
- **The per-state minimum.** It is the minimum of 5 values, so 0.838 lies about 3 per-state SDs below the mean. That is uncommon for one triple of 5 but unremarkable among the 6 triples observed, and it is **not gated**. M5(d)'s "per-state min 0.91" was the P0 Lorenz minimum, again one draw.
- **Risk.** The nearer edge (0.8) is 6.4 median-SDs away.
  - Distribution-free bound: all 30 observed per-state values lie in the band, so the per-state out-of-band probability is q ≤ 0.095 (95%), and P(median of 5 out of band) ≤ C(5,3)·q³ ≤ 0.9% per system.
  - Under a Gaussian per-state model it is below 1e-9.
  - **V2: ≈ 0** (≤ 0.9%, distribution-free).

---

## 3. Uncertainty budget of the headline number P(V6 fails per seed) (skill `uq-budget`, adapted)

| Source | Type | How estimated | Size | In the reported interval? |
| --- | --- | --- | --- | --- |
| Finite attractor sample (5 × 2·10⁵ states) | aleatory (Monte Carlo) | moving-block bootstrap over 95 segments | Chua ±0.5 points; Lorenz [0.06, 0.16]% | yes |
| Block start ~ μ (A1) | epistemic | M1(a) KS (p ≥ 0.33 at n = 4000) | not material at this resolution | no |
| Code and law identity with the sealed run (A3) | epistemic | bitwise reproduction of P0 and P1 | 0 while `validation.py` and `systems.py` are unchanged | no |
| Round-off | numerical | float64 against the deciding D ≥ 1e-4 σ_x | < 1e-10 relative | no |
| Reference accuracy (§1.3, mechanism only) | numerical | DOP853 at two tolerances; RK4 at 128 n_c | ≤ 5e-6 σ_x | not used in P(fail) |

The interval is a 95% percentile interval under block dependence (blocks of 10⁴ starts). The seeds are DEV-0 for the P0 and P1 states, and literal scratch seeds for the law.

---

## 4. Draft amended text for the unit file (not applied; the main session or planner applies it)

### 4.1 M5(d), the gate-margin table (replaces the table and the two bullets after it)

> **(d) Gate margins and the chance of an N4 failure.** *Amended 2026-10-13 after P1 (review P1 R1; `docs/agent/notes/2026-10-13-v6-margin-mathematics.md`). The original values came from one state realization (a5cd75b = P0) and are kept as the P0 column.*
>
> | Check | P0 (L / R / C) | P1 (L / R / C) | Band | Law under a redraw | P(fail) per fresh seed |
> | --- | --- | --- | --- | --- | --- |
> | V1 Jacobian / gain | ≤ 1.7e-7 | ≤ 1.5e-8 | < 1e-4 | ≥ 580× margin, smooth in the state | ≈ 0 |
> | V2 CRLB ratio, median of 5 states | 0.954 / 0.982 / 0.950 | 1.011 / 0.976 / 1.019 | [0.8, 1.2] | median SD ≈ 0.03; per-state min (5 states, not gated) 0.84 to 0.94 | ≤ 0.9% per system (distribution-free, 95%); ≈ 0 under a Gaussian model |
> | V4 median half-width, M = 200 | 0.0370 / 0.0390 / 0.0308 | 0.0187 / 0.0334 / 0.0420 | ≤ 0.05 | log-SD 0.31 (3 df; CI 0.18 to 1.17); two draws per system | plug-in 2% / 15% / 15%; predictive 10% / 23% / 23%; **not determined** (range 0 to 39% per system) |
> | V5 | fixture | fixture | < 0.01 | exact | 0 |
> | V6 max over 20 test states of the 1-LT step-halving deviation / σ_x | 3.9e-5 / 3.3e-5 / 7.5e-5 | 4.8e-4 / 4.3e-5 / 2.9e-4 | < 1e-3 | max of 20 draws of a heavy-tailed per-state deviation (stretching; Chua breakpoint crossings). Median 3.8e-5 / 3.7e-5 / 2.0e-4; 95th percentile 1.6e-4 / 4.4e-5 / 9.5e-4 | **0.11% / 0 / 4.4%** (CI 0.06 to 0.16% and 4.0 to 4.9%); any system 4.5% |
> | V7 slope; efficiency | 1.0007 / 1.0004 / 1.0007 | 1.0012 / 1.0000 / 1.0013 | [0.9, 1.1] | many SEs | ≈ 0 for a trained ψ |
>
> - V6's law was computed exactly by sliding 20-state windows (production spacing) over 10⁶ attractor states per system, and it reproduces P0 and P1 bitwise. It is preset-independent, so it is also the law at the confirmatory run.
> - The V4 figures assume a log-normal V4 with a common between-seed SD, estimated from two realizations. They are indicative only.
> - **Predicted P(N4 failure) per fresh seed:**
>   - at least 4.5% from V6 (Chua), which is well determined;
>   - plausibly 10 to 50% in total once V4 is included, where the V4 share is not determined.
>
>   A V4 or V6 failure is therefore a plausible outcome of correct code. At a development seed it goes to the owner (R-d), never to a retune.
> - *Correction of the original text:* "V6 ≥ 13×, P(fail) ≈ 0" read one draw as a margin. P0's Chua value was the 7.5th percentile of its law.

### 4.2 Risk R1 (replaces the line under `### Risks`)

> - **R1.** A gate check fails at a new realization. This covers P1 and every later seed, including the confirmatory one. *Amended 2026-10-13 (review P1 R1; note `2026-10-13-v6-margin-mathematics.md`).*
>   - **Per-seed probabilities:**
>     - V6: Chua 4.4% (4.0 to 4.9%), Lorenz-63 0.11%, Rössler 0; 4.5% for any system;
>     - V4: not determined from two realizations (central about 15% each for Rössler and Chua, and 2% for Lorenz; range 0 to 39%);
>     - V1, V2, V5, V7: ≈ 0.
>   - **At P1** no check failed: margins ×2.07 (Lorenz V6) and ×1.19 (Chua V4).
>   - **At a development seed**, a failure is referred (R-d).
>   - **At the sealed run**, a failure cannot be retuned (PRIME.2). It marks that system's results provisional (v3 E0). The owner's options are listed in the note's §5. The risk is owned by the owner, not by this unit.

### 4.3 Hypothesis table row H3 (NVVUQ.14), amended

> | H3 (invariance under the RK4 map) | All runs use the same map. V6 (step halving) estimates the map's 1-LT distance from the flow: for Lorenz-63 and Rössler as a Richardson estimate (observed order 4.00, D ≈ 0.94 e_h); **for Chua it is a heuristic indicator**, because RK4 is not 4th order across the diode breakpoints (observed orders −0.4 to 9.4 at crossing windows), although at the tail states D agrees with the true coarse error within a factor of 0.6 to 1.7 against a DOP853 reference. The QoIs are defined on the discrete map (LPC.NV.1), so this concerns V6's reading, not the tests. |

---

## 5. What this means for the sealed run, and neutral options for the owner

**Meaning.**
- The confirmatory seed draws new test states from the same law. With no change to code or criteria, the sealed run fails V6 on Chua with probability about 4.4%, and on some system with probability about 4.5%.
- A V4 failure on some system is at least as likely, but its probability is not yet determined.
- A failure there cannot be repaired by a retune or a rerun (PRIME.2; DEC-0027(3) as the review cites it). Per v3 E0 it marks that system's confirmatory results provisional. The caller's brief treats it as a hard stop.
- **A pre-screen on development seeds does not change the confirmatory probability.** It only tests the estimate.

**Options.** These are listed neutrally, and I recommend none. Any change to a criterion, bar or statistic is the owner's alone, must be made before the seal, and must rest on development evidence only.

| # | Option | What it buys | Cost |
| --- | --- | --- | --- |
| a | **Record the risk as computed.** Put the per-seed probabilities into the risk register and the preregistration text, so that a Chua V6 failure is an anticipated outcome, read under v3 E0, and not a surprise | Transparency. No change to any criterion | Text only |
| b | **Offline V6 pre-screen on DEV-1 to DEV-4.** V6 depends only on (seed, system) through `build_context`, so `repro.py` (with the seed swapped) gives V6 for each development seed in about 10 s per system on CPU, with no pipeline run. It adds 4 draws per system to test the law (P0 and P1 give 2). Under the law, the chance that at least one of 4 Chua draws fails is about 17% | A check of the law on registered development seeds | Minutes, CPU |
| c | **Full gate in the WU-0003 rehearsal on DEV-1 and DEV-2.** Two more V4 realizations per system, which takes the pooled df from 3 to 9 | A V4 spread known within a factor of about 2.7 instead of 6.6 | Already planned |
| d | **V4-only study over k synthetic development seeds**, using the guarded production context (as the review proposes). It needs the estimator ψ, the CP library and the oracle forecasts per seed and system | A determined V4 risk (k ≈ 10 gives a σ CI within about ±30%) | Several CPU minutes per seed and system; owner to authorize |
| e | **Pre-specify, before the seal, the response to a gate failure:** which statements remain reportable for a provisional system, and that no seed or setting is changed after the fact | The response is fixed before any confirmatory outcome exists | Text only |
| f | **Order the sealed run so that the outcome-free gate checks (V1, V2, V5, V6) are evaluated and recorded first,** before any hypothesis statistic is computed | A V6 failure would be known before any outcome. The probability is unchanged | An implementation check; possibly already the case |
| g | **The definition or bar of V6** (the statistic over the 20 states, or the treatment of Chua's breakpoints). Owner's decision only. §2.1 gives the law (quantiles) needed to evaluate any proposal. No recommendation is made here | — | — |

An agent may not compute V6, or any check, on the confirmatory seed (LPC.PC.7). Any rule that conditions on the confirmatory seed would be the owner's decision and would raise a seed-selection question of its own.

---

## 6. Reproduction (REPRO.10)

Run from the scratchpad, with `PY=.venv/bin/python -I`, `W=` this worktree and `C=` a copy of the run's `cache/` holding `lyapunov.json` (P0 and P1 are bitwise equal). Every command runs on CPU.

```
$PY repro.py $W $C p1.npz                      # P1 V6 bitwise + per-state D (P0: code root = run/p0-1b20db9)
$PY perstate.py $W $C <system> 5 200000 D_<system>.npz   # per-state law, 10^6 states
$PY law.py D_<system>.npz <spacing> <P0 V6> <P1 V6>      # V6 law, P(fail), block-bootstrap CI
$PY mech.py $W $C <system>                     # refinement study, stretching, crossings
$PY refcheck.py $W $C                          # reference accuracy (Chua)
$PY stretch.py $W $C <system>                  # Spearman(log D, ln sigma_1)
$PY v4v2.py                                    # V4 and V2 estimates from P0 and P1
```

Spacing: Lorenz-63 45, Rössler 150, Chua 150. The logs (`*.log`) are the outputs quoted above. The `D_*.npz` arrays (8 MB each) are not committed; `perstate.py` regenerates them in about 1 minute per system.
