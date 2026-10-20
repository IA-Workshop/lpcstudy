# Extension program: specifications of the additional attractors S1, S2 (and S3)

**Correction 2026-10-20 (review WU-0021.7 R1):** the S1 values `max_dt = 0.01`, `orbit_bound = 300` and `lyapunov_steps = 1 000 000` of §0, §1.1 and §2 are superseded by `2026-10-20-math-extension-specs-2.md` §11 (max_dt 0.005, bound 460, 2·10⁶ steps, cached λ 0.11220508610149857): at h = 0.009875 RK4 is unstable where the attractor reaches x ≈ −304 (∂ż/∂z = x), and the bound 300 lay inside the attractor's reach. S2 and S3 are unchanged.

**DEVELOPMENT / EXPLORATORY: not a hypothesis test.** No sealed seed, no sealed flag, no read of `runs/confirmatory`. Every computation here ran on CPU, one thread, `nice -n 19`, with no preset and no test tier, while the run-2 CPU job and the GPU ensemble were in progress. Nothing under `lpcstudy/`, `tools/`, `docs/study/`, `seeds/`, `ROADMAP.md`, the ledger or the records was changed. This note is WU-0021.2.

- **Date:** 2026-10-20 (stage 1 committed at noon; this is the refined version). **Agent:** applied-mathematician (claude-fable-5-1). **Authorization:** DEC-0037. **Branch:** `wu/ext-math` from develop 22483b4.
- **Read:** my note of 2026-10-19 (`2026-10-19-math-other-attractors.md`, §A.2, A.3, C.3, D) and the researcher's checks of it (`2026-10-19-researcher-attractor-references.md`); the researcher's Dysts note `2026-10-20-researcher-dysts-extension.md` (WU-0021.1, read from the develop worktree); the unit file `WU-0021-extension-attractors.md` (plan, R1–R3, A1–A8, the .3 reference); `lpcstudy/systems.py`, `config.py`, `data.py`, `dynamics.py`, `oracle.py`, `validation.py`, `embedding.py`, `estimation.py` (LM), `experiments.py` (dof, robustness filter, V4), `analysis.py` (H1a reference, H1b, V7), `pipeline.py` (dof, width rule), `report.py` (`LYAPUNOV_REFERENCES`), `statistics.py` (`V3_SYSTEMS`, `overall_verdict`), `__main__.py` (`--systems`); proposal and methods v3 §2–§9; Methods v2 M2–M4, M11–M13; `docs/study/pilot_results_v3_dev0_reference.json`; `tools/compare_runs.py`, `tools/leafdiff.py`; `tests/unit/test_systems.py`, `test_experiments.py` (registry pins).
- **Scripts and logs:** `docs/agent/notes/2026-10-20-math-extension-specs/` (§9). Scratch seed 20261020 where a seed was needed; DEV-0 pilot leaves read only.

## 0. What the developer writes (no choice left open)

Three additive `SystemSpec` entries in `lpcstudy/systems.py`, one additive field `lyapunov_steps: int = 100_000` on `SystemSpec` that `data.lyapunov_record` passes as `n_steps` (the plan's exception R2 (i); the default equals today's literal, so the three frozen entries and their cached values are unchanged), one key each in `report.LYAPUNOV_REFERENCES` (S1: the published spectrum row of §1.1; S2 and S3: an empty list), and the three registry-pinning tests updated to the new set (§6). No change to `config.py` (a new system is run with `--systems <name>`, which replaces `core_systems`; `build_context` reads `SYSTEMS[name]`) and **no change to `checked_bound`** (S3 is a permuted-state spec, §1.3; the plan's exception R2 (ii) is not needed).

| Field | S1 `rossler_hyper` | S2 `lorenz63_r166` | S3 `rossler_z` (optional lane .4b; recommended) |
| --- | --- | --- | --- |
| `field_fn` | new `rossler_hyper_field`: ẋ = −y − z, ẏ = x + a y + w, ż = b + x z, ẇ = −c z + d w | `lorenz63_field` (registry function) | new `rossler_zfirst_field`: state (z, x, y), ż = b + z(x − c), ẋ = −y − z, ẏ = x + a y |
| `params` | `{"a": 0.25, "b": 3.0, "c": 0.5, "d": 0.05}` | `{"sigma": 10.0, "rho": 166.1, "beta": 8.0 / 3.0}` | `{"a": 0.2, "b": 0.2, "c": 5.7}` |
| `dim` | 4 | 3 | 3 |
| `observed_index` | 0 (x) | 0 (x) | 0 (= z of Rössler) |
| `initial_state` | `(-10.0, -6.0, 0.0, 10.0)` | `(1.0, 1.0, 1.0)` | `(0.0, 1.0, 1.0)` (= the registry start (1, 1, 0) permuted) |
| `max_dt` | 0.01 | 0.002 | 0.04 (registry) |
| `orbit_bound` (on coordinate 0) | 300.0 | 185.0 | 50.0 |
| `lyapunov_steps` | 1 000 000 | 4 000 000 | 1 000 000 |
| cached λ on this host (expected, bitwise; §2) | 0.11251662457254265 | 0.6217010154674514 | 0.07133265490530956 |
| Δ = 1/(30 λ); substeps | 0.296253; 30 | 0.053616; 27 | 0.467294; 12 |

Everything else (σ_x, C, τ, ACF time, spacing, starts of the main and estimator trajectories) is derived by the code; the values below say what it will derive (`units_long.log`, computed with the `build_context` recipe at the cached λ above), so that the first run can be checked.

## 1. Exact definitions and derived units

### 1.1 S1: hyperchaotic Rössler (Rössler 1979)

Equations and parameters: confirmed (researcher, 2026-10-19 request 1; 2026-10-20 §B.1, Dysts `HyperRossler` identical). **Published spectrum (Ramasubramanian & Sriram, arXiv:chao-dyn/9909029, Table 1, read directly by the researcher):** 0.1121, 0.0196, 0.0000, −25.1886 (standard method, t = 10⁵; their other method 0.1128, 0.0214, 0, −24.75), d_KY = 3.0052 derived. **The Dysts `HyperRossler` Lyapunov fields (0.279, 0, −0.30, −70.3; max 0.172) contradict the published spectrum and must not be used** (researcher §B.1).

- **Spectrum (this note, `spectra.log`, independent Benettin/QR, 10⁶ steps at interval 0.2 after a 5 000-step burn-in, block SE over 50 blocks):** λ = (+0.11252 ± 0.00056, +0.02072 ± 0.00034, −0.00001 ± 0.00006, −24.765 ± 0.105); d_KY = 3.005; LT = 8.89 time units; λ₂/λ₁ = 0.184. Against the published values: λ₁ +0.4%, λ₂ inside the 0.0196–0.0214 method spread, λ₄ +1.7% (their −25.19 to −24.75). Two positive exponents: the second direction grows by e^{0.18} per LT.
- **Cached value** (`lyapunov_guarded`, interval 20·max_dt = 0.2, `lyapunov_steps` = 10⁶, burn-in 5 000, from `initial_state`): **0.11251662457254265** on this host and XLA build (`lyap_long.log`; the registry Lorenz-63 and Rössler cached values of the pilot reference are reproduced bitwise here, `lyap_check.log`), relative SE 0.50% (plan criterion ≤ 1%: met). At the code's old default 10⁵ steps the value would be 0.11225907424447891 with SE 1.6%. Δ = 0.296253; substeps 30; dt = 0.009875.
- **Statistics orbit** (start `initial_state`, burn-in 100 LT = 3 000 steps, 200 000 steps at Δ): x mean −24.94, **σ_x = 21.68**; state mean (−24.94, −2.56, 2.54, 25.57); standard deviations (21.68, 20.20, 12.37, 8.48); covariance eigenvalues (49.6, 144.1, 387.0, 522.2), condition 10.5; **whitening scale** √eig = (7.04, 12.00, 19.67, 22.85). The observable is skewed (−0.95), 0.1% quantile −110, 99.9% quantile +14.4.
- **Orbit maxima of |x|** (coordinate 0): Benettin orbit (10⁶ steps) 166.4; statistics orbit with burn-in 141.4; a 4·10⁶-step orbit at Δ (1.19·10⁶ time units, 133 000 LT) **174.1**, block maxima over 100 000-step blocks with median 143.6 and 90th percentile 161.0; 41 steps of 4·10⁶ above 150 (`bound_tail.log`). Other coordinates reach |y| 95, |z| 410, |w| 69 (not guarded, as for the frozen systems). **Bound 300 = 1.72 × the largest excursion seen in 1.2·10⁶ time units.** No analytic trapping region is available; the bound is empirical and generous so that a false refusal (which stops a run, DEF-0015) is improbable over a full-preset trajectory (0.7·10⁶ steps ≈ 2·10⁵ time units). My earlier note's "bound on x ≈ 60" was wrong (it read the maximum over all coordinates of a short orbit); the guard refused the first attempt at 60 at step 927 (`spectra.log`, first run), which is the guard working as designed.
- **Starts.** Statistics and Benettin orbits at `initial_state` for every seed (M2); main and estimator trajectories at seed-drawn points of the post-burn-in statistics orbit perturbed by 10⁻⁶ whitened (`draw_starts`, label `make_rng(seed, "start", "rossler_hyper")`), same 3 000-step burn-in. The transient from (−10, −6, 0, 10) stays below |x| = 142.

### 1.2 S2: Lorenz-63 at r = 166.1 (type-I intermittency regime, Manneville & Pomeau 1980, r_c = 166.07)

- **Spectrum (4·10⁶ steps at interval 0.04, 1.6·10⁵ time units):** λ = (+0.6217 ± 0.0066, −0.0000 ± 0.0001, −14.288 ± 0.007); d_KY = 2.044; LT = 1.609. Published λ at r = 166.1: none (researcher, both notes); the literature gives only λ ∝ √(r − r_c) for r − r_c ≪ 1 (Crisanti et al., no constant). Dysts has no entry at r = 166.1.
- **Cached value** (interval 0.04, `lyapunov_steps` = 4·10⁶ = 1.6·10⁵ time units): **0.6217010154674514**; block SE 1.06%, which is the reached SE to report (plan criterion: ≤ 1% or reported). **The block SE underestimates:** a 2·10⁵-step run in the r-scan gave 0.665 ± 0.018, 2.3 block-SEs from this value, so the slow laminar/burst correlation makes the true uncertainty of a run of this length about 2%. At the old default 10⁵ steps the value would be 0.6204447073633099 with a nominal 5.5% SE. Δ = 0.053616; substeps 27; dt = 0.001986.
- **Statistics orbit:** x mean −0.00, **σ_x = 20.34**; state mean (0.00, 0.00, 155.1); standard deviations (20.34, 35.86, 34.96); covariance eigenvalues (248.7, 1222.0, 1450.5), condition 5.8; **whitening scale** (15.77, 34.96, 38.09). The observable is symmetric (skewness 0.001), platykurtic (2.32), quantiles ±44 at 0.1/99.9%.
- **Orbit maxima of |x|:** Benettin 62.4; statistics (with burn-in) 61.8; 2·10⁶ steps at Δ: 56.4 (block maxima 52.4–54.8). **Bound 185 = the analytic trapping ball, rounded up.** Derivation (`trapping.py`, identity checked to 4·10⁻¹⁵): with V = x² + y² + (z − σ − r)² and c = σ + r, dV/dt = −2σx² − 2y² − 2β(z − c/2)² + βc²/2, negative outside the ellipsoid E: σx² + y² + β(z − c/2)² ≤ βc²/4. The ball V ≤ max_E V is forward-invariant and contains every ω-limit set; max_E V = 33 079 (SLSQP and 2·10⁶-point surface sampling agree), so every orbit starting in the ball has |x| ≤ 181.9 for all time. At r = 28 the same derivation gives 39.25, which the ratified bound 40 just exceeds: 185 continues the registry convention. A false refusal is impossible for an orbit starting inside the ball ((1, 1, 1): V = 30 660 < 33 079); the guard then catches only non-finite values (a code defect), its purpose on a globally bounded system.
- **Character of the attractor at r = 166.1 (measured; weaker than my earlier note claimed).** The r-scan (`intermittency_scan.log`; RK4 at max_dt 0.002, interval 0.04, 4·10⁵ steps per r) gives λ = 0.000 at r = 166.0, 0.42 at 166.075, 0.44 at 166.08, 0.67 at 166.1, 0.79 at 166.15, 0.91 at 166.2, 1.41 at 166.5, 1.69 at 167: the exponent rises continuously from zero at r ≈ 166.07, the type-I onset of Manneville and Pomeau with this integrator. The fraction of 1-LT windows whose Benettin growth is below 0.1 falls from 0.50 (r = 166.0, neutral) to 0.35 (166.1) to 0.14 (167). But (i) the per-state Λ̃ = 30Λ̄ distribution over 1 LT at r = 166.1 is **not bimodal**: quantiles (1/5/25/50/75/95/99%) = (−0.98, −0.54, 0.11, 0.89, 1.83, 4.81, 5.77) against (−1.16, −0.82, 0.33, 0.74, 1.45, 4.22, 6.43) for the registry Lorenz-63 (`units_long.log`, `units.log`); 30% of states below 0.3 against 24%. (ii) The "laminar phase" is not a stretch of near-periodic z-maxima: the r = 166.0 attractor itself (λ = 0 ± 2·10⁻⁴) is a modulated orbit whose z-maxima alternate between about 190 and 227 and drift (lag-2 differences, median 7.2), and r = 166.1 shows the same pattern with the same lag-2 statistics (`laminar_r166.1.log`, `laminar_r166.0.log`); a return-map diagnostic does not separate the phases at this resolution and I have no laminar-length distribution. What S2 measurably adds over Lorenz-63 at r = 28: long coherence (ACF time 191 steps = 6.4 LT against 0.3 LT), a heavier amplifier tail (g_H at 1 LT: median 6.5, 95th percentile **185** against 2.5 and 25), a lower local dimension (1/d_LB 0.537, d = 1.86, against 0.487, d = 2.05), and the onset regime itself. **Owner decision R2.**
- **Starts:** as S1, label `make_rng(seed, "start", "lorenz63_r166")`.

### 1.3 S3: Rössler observed through z, as a permuted-state spec (optional lane .4b; recommended as a full member)

`checked_bound` refuses `observed_index ≠ 0`. Rather than change ratified guard code (plan exception R2 (ii), ROADMAP "the S3 guard change"), S3 is the registry Rössler with the state written as (z, x, y): `observed_index = 0` observes z and the bound is on z. Whitening, ν, g_H, the delay map and the Levina–Bickel dimension are invariant under a coordinate permutation (the symmetric root C^{±1/2} permutes with the state; every reported quantity is a trace, a norm or a distance in whitened coordinates). Plan item A5's "S3 only: a spec with `observed_index ≠ 0` ... is still refused" stays true unchanged.

- **The orbit is not bitwise the registry orbit:** XLA rounds the permuted field differently (first difference at step 37 of a 5 000-step orbit, 1 ulp, `orbit_bits.log`), so S3 is a different realization of the same attractor. **Cached value** (interval 0.8, `lyapunov_steps` = 10⁶): **0.07133265490530956**, SE 0.23%; the registry Rössler's cached value (10⁵ steps) is 0.07193978510879935, so the S3 sampling interval is 0.85% longer (0.467294 against 0.463350), within the registry value's own 0.8% SE. Substeps 12; dt 0.03894.
- **Units:** z mean 0.884, **σ_x = σ_z = 2.850**; spike-dominated: median 0.042, 90% quantile 1.80, 99.9% quantile 22.0, skewness 4.7, kurtosis 27. State standard deviations (z, x, y) = (2.85, 5.15, 4.84); eigenvalues (6.37, 21.47, 30.22), condition 4.7; whitening scale (2.52, 4.63, 5.50).
- **Noise meaning:** ρ is a fraction of σ_z. At ρ = 1% the noise (0.029) is 70% of the median z; in the flat phase (z ≲ 0.05, about half of the time) the observable is below the noise for every ρ ≥ 1%. This is the observability stress S3 is chosen for.
- **Bound 50** on z: maximum 22.85 on every orbit examined (2·10⁶ steps); ratio 2.19, the registry Rössler's ratio (25 against 11.43).
- **Alternative (R3):** `observed_index = 2` on the registry spec with the guard change: identical orbit and λ, but edits ratified code (DEC-0017 Q1, DEC-0026) and its test. **Recommend the permuted spec.**

### 1.4 Registry comparison values (same script, same recipe)

| Quantity | L63 r = 28 | Rössler | S1 | S2 | S3 |
| --- | --- | --- | --- | --- | --- |
| λ cached (code settings) | 0.905494 (10⁵ steps) | 0.071940 (10⁵) | 0.112517 (10⁶) | 0.621701 (4·10⁶) | 0.071333 (10⁶) |
| relative SE of the cached λ | ≈ 0.15% | 0.8% | 0.50% | 1.06% block (≈ 2% true) | 0.23% |
| Δ, substeps | 0.0368, 4 | 0.4634, 12 | 0.2963, 30 | 0.0536, 27 | 0.4673, 12 |
| σ_x | 7.92 | 5.15 | 21.68 | 20.34 | 2.85 |
| AMI delay → τ (cap 5) | 5 → 5 | 3 → 3 | 6 → 5 | 5 → 5 | 3 → 3 |
| window (D−1)τ | 30 = 1 LT | 18 = 0.6 LT | 30 = 1 LT | 30 = 1 LT | 18 = 0.6 LT |
| ACF time (steps; LT) | 9; 0.3 | 1500; 50 (cap) | 228; 7.6 | 191; 6.4 | 289; 9.6 |
| spacing (steps) | 45 | 150 | 150 | 150 | 150 |
| ν median (p1, p99) | 1.67 (0.72, 6.65) | 1.13 (0.78, 10.1) | 1.91 (1.14, 21.0) | 1.31 (0.53, 5.79) | **13.8 (1.14, 130)** |
| Λ̃ quartiles (p25, p50, p75) | 0.33, 0.74, 1.45 | 0.86, 1.13, 1.35 | 0.80, 1.02, 1.76 | 0.11, 0.89, 1.83 | 0.00, 0.70, 1.77 |
| g_H at 1 LT median (p95) | 2.46 (25) | 3.32 (7.4) | 2.69 (10.3) | 6.47 (185) | 0.045 (21) |
| 1/d_LB (k = 20), d | 0.487, 2.05 | 0.514, 1.94 | **0.357, 2.80** | 0.537, 1.86 | 0.521, 1.92 |

Pilot reference (DEV-0): 1/d_LB 0.489 / 0.510 / 0.503 (L63 / Rössler / Chua), consistent with the column values (different scratch pool).

## 2. Time conventions

- **The 30-steps-per-LT convention is kept for all three**; no override is needed (λ_max > 0 and finite). The study's λ is its own Benettin value; **the Dysts `maximum_lyapunov_estimated` must not be used for any of these systems** (it is 2.09× and 2.85× the study's for Rössler and Chua and inconsistent with Dysts' own spectrum; researcher §A.3–A.5, §B.1).
- **Run lengths** (plan: block SE ≤ 1% of λ or the reached SE reported): `lyapunov_steps` = 10⁶ (S1, 0.50%), 4·10⁶ (S2, 1.06% block, about 2% true: reported), 10⁶ (S3, 0.23%); cost 7 s, 23 s, 6 s single-threaded (`lyap_long.log`). The field is additive with default 10⁵, so the three frozen cached values are untouched (R1 covers it). The exact expected cached values are in §0; a different host or XLA build compares at the T1 rule (1e-12 relative).
- **RK4 step and V6** (`integrator.log`: 20 attractor states, 30 steps of Δ, the code's statistic max |x_h − x_{h/2}|/σ_x; gate < 10⁻³; formal order 4; and `gate_checks.log`: the code's own `check_integrator` on real contexts at the smoke sizes):

| System | max_dt | substeps | V6 statistic (20 states) | V6 by the code's own check | observed order p (h, h/2, h/4) | Richardson error at h/2 (σ_x) |
| --- | --- | --- | --- | --- | --- | --- |
| S1 | 0.02 | 15 | 1.7·10⁻⁵ | — | 3.88 | 8·10⁻⁸ |
| S1 | **0.01** | **30** | **1.1·10⁻⁶** | **3.2·10⁻⁶** | 3.95 | 5·10⁻⁹ |
| S1 | 0.005 | 60 | 7.4·10⁻⁸ | — | 3.92 | 3·10⁻¹⁰ |
| S2 | 0.008 | 7 | 9.9·10⁻³ FAIL | — | 4.78 | 1·10⁻⁵ |
| S2 | 0.004 | 14 | 3.6·10⁻⁴ (2.8× margin) | — | 4.41 | 8·10⁻⁷ |
| S2 | **0.002** | **27** | **1.7·10⁻⁵** | **8.2·10⁻⁵** | 4.51 | 3·10⁻⁸ |
| S3 | 0.08 | 6 | 1.6·10⁻³ FAIL | — | 3.80 | 9·10⁻⁶ |
| S3 | **0.04** | **12** | **1.2·10⁻⁴** | **1.3·10⁻⁴** | 3.91 | 6·10⁻⁷ |

  Observed orders 3.8–4.5 (4 formal; S2's 4.4–4.8 reflects the fastest states entering the asymptotic regime late): no bug, no non-smoothness. Registry pilot values: 4.8·10⁻⁴ (Lorenz), 4.3·10⁻⁵ (Rössler), 2.9·10⁻⁴ (Chua). Choices: S1 max_dt = 0.01 (margin 300× by the code's check; 0.02 would pass with a 60× margin at half the cost; 0.01 is fixed because the Benettin interval 0.2 then gives the 0.5% exponent at 10⁶ steps); S2 max_dt = 0.002 (0.004 leaves only 2.8× on my states and the code's check on test states is 5× worse than mine); S3 the registry's 0.04 (margin 7.6×). The discretization error at 1 LT is 10⁻⁸–10⁻⁶ σ_x, four or more orders below the smallest noise level 0.005 σ_x; the QoI is defined on the discrete map (LPC.NV.1).
- **Cost.** RK4 work per flow-map step scales with substeps × m (field) and substeps × m² (Jacobian paths: LM, ν, g_H). Relative to Chua (16 substeps, m = 3): S1 (30, 4) ≈ 2.5–3.3×; S2 (27, 3) ≈ 1.7×; S3 ≈ Rössler. Data generation is 36 M / 33 M / 15 M RK4 substeps at the full preset (a minute or two); forecasts and the LM dominate as in the pilot. Expect S1's pilot to take about 2.5–3× Chua's pilot time (R7).

## 3. Embedding, estimator and library

- **Delay τ (AMI first minimum, cap ⌊30/6⌋ = 5):** S1: AMI minimum 6 → τ = 5 (capped), window 30 steps = 1 LT; S2: 5 → 5, 1 LT; S3: 3 → 3, 18 steps = 0.6 LT (as the registry Rössler). D = 7 unchanged; the window cap ≤ 1 LT holds.
- **Embedding of S1:** d_KY = 3.005; Sauer–Yorke–Casdagli needs D > 2 d_box (prevalent, generic; researcher request 11): 7 > 6.01 if d_box ≈ d_KY (unverified). Empirical check: ν finite on all 1 333 sampled states (max 37.6, p99 21), so AᵀA (4×4) is invertible everywhere sampled and the delay map is locally injective there. No symmetry of the x-observable, so the two-to-one fold of Lorenz-z (catalog #7) is not expected. 1/d_LB = 0.357 (d = 2.80): the H1a reference regime "d ≈ 3".
- **PLP estimator:** window-start state u ∈ ℝ^m, D = 7 residuals; damped LM on the m×m normal equations (`estimation.py`): needs D ≥ m (7 > 4) and a full-rank Jacobian (ν finite). **dof = D − m = 3 for S1** (4 otherwise): the χ² 0.999 reference becomes 16.27 (3 dof) instead of 18.47; the code computes `embed_dim − spec.dim` everywhere (`gof_threshold`, `lm_block`, `check_record`), so this is automatic; only the explanatory text in `report.py` says "dof 4" (cosmetic, R9). `robustness_dimensions` keeps d > m: (5, 10) for every new system (not run: `robustness_systems` unchanged; `--skip-robustness` per the plan).
- **Estimator width rule** (`networks.py`): widths (64, 128), the smallest width whose validation loss is within 5% of the best; 10⁵ pairs (pilot 4·10⁴) at stride 5 from the separate trajectory; the target is the whitened window-start state in ℝ^m (4 outputs for S1). No change.
- **Library sizes:** unchanged (10³ … 10⁵); the library segment is 100 271 steps (S1, S2) or 100 259 (S3) plus the 8-LT future. For S1 at d ≈ 3 the analog seed should scale as N_lib^{−2/3} (1/d_LB ≈ 0.36) instead of N_lib^{−1}: CP is relatively worse at every N_lib.
- **ACF time, thinning and effective sample size.** ACF 1/e envelope times 228 / 191 / 289 steps (7.6 / 6.4 / 9.6 LT) are above the 1-LT cap, so spacing = max(⌈5·30⌉, 30) = 150 steps = 5 LT for all three (Rössler and Chua have 150; Lorenz-63 45). Consecutive states are 0.66 / 0.79 / 0.52 ACF times apart: not independent at the observable level, the same situation as Rössler (0.1) and Chua (2). Block length 5 is fixed by v3 (25 LT per block); the per-state statistics decorrelate faster than the observable; the block-sensitivity flag (√max(1, V*(10)/V*(5)), v3 §8) is the pre-registered instrument and should fire more often on S3 than on the others. Trajectory lengths: main 311 831 (pilot) / 701 831 (full) steps for S1 and S2, 311 735 / 701 735 for S3, the same as Rössler and Chua.
- **Noise levels ρ** unchanged (0.5, 1, 2, 5% of σ_x); admissible thresholds unchanged (θ ≥ 3√2 ρ: at ρ = 5% only θ ∈ {0.3, 0.5}). The meaning of σ_x per system is in §1.
- **Clipping at 10 σ_x:** S3's spikes reach 7.7 σ_z, so a wrong-phase forecast errs by up to about 8 σ_z, below the clip; the counters will show any clip.

## 4. Expected behaviour of the gate V1–V7 (tolerances exactly as written in `gate_status`; none changed)

The code's own V1, V2 and V6 were run on real `SystemContext`s of the three systems at the smoke sizes (candidate specs registered in-process only; `gate_checks.log`), and the V7 mechanism was probed with a damped LM (15 iterations, the pipeline's accept/damping rule) started from the *true* window-start state at the study's four noise levels on 40 test states × 50 draws, which is optimistic for the pipeline (no network start, no wrong basins from a bad start).

| Check | Gate | S1 | S2 | S3 |
| --- | --- | --- | --- | --- |
| V1 Jacobians vs finite differences | both < 10⁻⁴ | **pass measured:** 6.0·10⁻⁹, 3.6·10⁻⁹ | **pass measured:** 1.3·10⁻⁸, 4.1·10⁻⁸ | **pass measured:** 6.6·10⁻¹⁰, 1.6·10⁻⁸ |
| V2 Cramér–Rao at ρ = 10⁻⁴ | median ∈ [0.8, 1.2] | **pass measured:** 1.036 (0.94–1.06) | **pass measured:** 0.946 (0.91–1.10) | **pass measured:** 0.940 (0.82–1.00) |
| V3 CP valid time | report only | expect below Rössler's 3.3 LT (d ≈ 3 seed) | report | dominated by spike timing |
| V4 w* converged at M = 200 | median half-width ≤ 0.05 | pass expected | pass expected | **at risk**: in the flat phase both errors are tiny, c = E[(e_C − e_P)²] is near zero and w* is ill-conditioned (`curvature_floor` counts); half-widths may exceed 0.05 |
| V5 Kaplan–Meier fixture | < 0.01 | pass (system-independent) | pass | pass |
| V6 step halving over 1 LT | < 10⁻³ σ_x | **pass measured:** 3.2·10⁻⁶ | **pass measured:** 8.2·10⁻⁵ | **pass measured:** 1.3·10⁻⁴ |
| V7 efficiency: median δ/(ρν) at every ρ and the median per-state slope, both ∈ [0.9, 1.1] | both | pass expected: LM probe medians 0.985 / 0.987 / 0.986 / 0.992 at ρ = 0.5 / 1 / 2 / 5%; 9 of 2 000 draws at 5% end > 1 whitened unit away | pass expected: 0.999 / 0.996 / 0.969 / 0.983; 1 far draw | **at risk, but not predicted to fail by the median criteria:** 1.022 / 1.065 / 1.079 / 0.991 with the spread widening to p10 0.41, p90 1.30 at ρ = 5%, where 239 of 2 000 draws (12%) end > 1 whitened unit away (80 at 2%, 14 at 1%). The states with ν > 30 saturate; the median does not. The pipeline's network-started LM may do worse (wrong basins), and the slope criterion was not probed; my earlier "likely FAIL" is withdrawn |

**What a failure means (study rule, v3 §6 E0):** the system is marked PROVISIONAL, every verdict is computed and shown with that label, the failure is reported and referred to the owner, and nothing is retuned, rerun or repaired. On S3 a V4 or V7 failure is itself the finding the system was chosen to expose (the Cramér–Rao floor is a first-order statement; where ν is large the estimator leaves the linear regime at the study's noise levels, visibly in the 12% of saturated draws at ρ = 5%). On S1 and S2 the gate is expected to pass; a failure there goes to the owner as a defect candidate.

## 5. Pre-specified exploratory analysis (fixed before any run on the new systems)

**Label:** DEVELOPMENT / EXPLORATORY, seed named in every table: **DEV-3** (WU-0021.6 pilot, WU-0021.8 full), never a seed used for the system before, never the confirmatory seed, never `--confirmatory`; one system per run, `--systems <name>`, `--skip-robustness`; pilot after a smoke plumbing run; full by the plan (.8).

**Estimands and decision rules:** exactly those of v3 §2 and §7 (bands, levels 1 − 0.05/3 for H2a, H2b, H3c and 95% otherwise, block length 5, 2 000 resamples (500 at pilot), the 50-state minimum, the Q-N reading table, the K rule, the gain-bound screen), applied unchanged, per system. No criterion, band, level, block length or threshold is changed; the per-system verdict rule (pass / fail / inconclusive) is the code's.

**Per-system verdicts only; no overall verdict.** `overall_verdict` requires `V3_SYSTEMS` = (lorenz63, rossler, chua) and reads "inconclusive" when any is missing, so a run of a new system prints an overall line that must not be read. The reason is statistical as well as formal: v3's "supported" is an intersection–union test over the three pre-registered systems, which controls the error of "supported" at the per-system level without a multiplicity correction; "not supported" is a union, whose error grows with the number of systems (about 7.3% over three at 95%, about 23% over five). Adding systems to the required set after the freeze would change both error rates of the sealed verdict; keeping them out leaves it untouched. The extension therefore reports, per new system, the per-hypothesis verdict word and interval, and states that no extension result bears on the sealed study's overall verdicts. A confirmatory claim about any new system needs its own sealed seed and freeze (DEC-0037 item 1).

**Decidability at the full preset (projected from v3 §7 and M12; "structural" means the design, not the sample size, decides):**

| Hypothesis | S1 | S2 | S3 |
| --- | --- | --- | --- |
| H1a (1/d_fit vs 1/d_LB, ±25%) | decidable; reference ≈ 0.36, band ±0.09, projected half-width ≈ 0.05–0.07 | decidable (≈ 0.54) | decidable (≈ 0.52) |
| H1b (PLP slope ∈ [0.8, 1.2]) | decidable; pre-specified counterexample: interval entirely outside the band (two growth directions) | decidable | decidable; wider x-range (g_H spans 0.004–21) |
| H1c (horizon law ratio ∈ [0.8, 1.25]) | decidable | decidable; the per-state Λ̄ straddles bursts | **structurally weak**: T(θ) on ln θ is set by spike timing, not smooth growth; expect inconclusive or fail with the reading "the exponential envelope (P1-5) fails" |
| H1d (Spearman ≥ 0.7 for ε̂, δ̂, Λ̂) | decidable | decidable | decidable; δ̂ strongest (ν̂ carries two orders of magnitude) |
| Q-N (ΔR² reading) | reachable (±0.04) | reachable | logit part needs ≥ 50 interior states: may be undetermined |
| H2a (i) range < 0.1; (ii) partial r ∈ (−0.1, 0.1) | (i) decidable; (ii) refutable only; predicted: larger |r| than on the three (anisotropic two-direction seeds) | (i) decidable; (ii) refutable only | (i) decidable; (ii) refutable; w* = 1 states may exceed 5%, adding the third part by the existing rule |
| H2b (i), (ii) lower bounds > 0 | decidable | decidable | decidable |
| H2c (A4 − A2 and A4 − best single, upper bounds < 0) | likely inconclusive (as Rössler, Chua) | likely inconclusive | **the one system where it can pass**: ν varies by 100×; readings: pass = observability makes allocation pay; fail with A4o − A2 < 0 = "deployable seeds limit it"; fail with A4o − A2 > 0 = counterexample to the mechanism, not to P1 |
| H2d (A4/A3 − 1 ≤ 0.10) | undetermined (wide) | undetermined | undetermined |
| H2e (noise matching, lower bound > 0 at both ρ) | decidable | decidable | decidable |
| H3a (Holm log-rank, all p < 0.01) | inconclusive-prone (small regimes; v3 §8) | same | same; many censored horizons in the flat phase |
| H3b (weight-tree Λ̃ < 0.2; horizon-tree Λ̃ largest) | decidable in part; predicted: horizon-tree Λ̃ importance lower than on the three (two rates) | decidable; the target claim for S2 | decidable; predicted: the weight tree loads on ln δ̂/ρ, not Λ̃ |
| H3c (A5/A4 ≤ 1.05) | decidable | decidable | decidable |
| gain-bound screen | report | report | report |

**Reading rules per outcome pattern (fixed now; to be copied into the unit's Log before .6):**

1. Gate fails on a system: all its verdicts PROVISIONAL, shown, referred (§4); no other rule applies.
2. S1, H1a passes at 1/d_LB ≈ 0.36: the N_lib^{−2/d} law holds at d ≈ 3 (new regime). Fails below the band: the same shortfall as Rössler/Chua, with no published prediction (researcher request 12); fails above: report, no reading pre-specified.
3. S1, H1b interval entirely outside [0.8, 1.2]: the seed × amplifier law breaks when the amplifier is not rank-one dominated (P1-5/L1 regime); inside: the law survives two growth directions.
4. S1, H2a(ii) interval wholly above the sealed Lorenz-63 / Rössler / Chua values: predicted sign (anisotropy from two directions); the sealed values are quoted from the promoted document only, unchanged, with no claim about them.
5. S2, H3b: horizon-tree Λ̃ largest and weight-tree Λ̃ < 0.2 = "instability sets the horizon, not the weight" holds at the type-I onset; weight-tree Λ̃ ≥ 0.2 = the pre-registered reading "seed anisotropy", with the amplifier tail (g_H p95 = 185) named as the mechanism.
6. S2, H1c: pass = the per-state exponential law survives the bursts; fail = read with the Λ̃ spread (30% of states below 0.3), not as a numerical defect.
7. S3, V7 passes and H2c passes: observability decides allocation where it varies (the mechanism the three frozen systems could not show, Methods v2 M13 item 1). V7 passes and H2c fails with A4o − A2 < 0: the deployable δ̂ limits it. H1d-δ̂ ≥ 0.7 with H1d-ε̂ < 0.7: L4 (ε̂ through R ν̂) is the weak proxy.
8. Any system: fraction of states with w* = 0 or w* = 1 reported; a part with < 50 states is inconclusive by the code's rule, never "fail".
9. Any system: block-sensitive flags reported as in v3 §8; no interval widened; λ's uncertainty (§2) reported beside every "LT" conversion.

## 6. Regression requirement for the developer (plan R1, zero tolerance)

1. **Additive only.** New `SystemSpec` entries, field functions and the `lyapunov_steps` field with default 100 000; the three frozen entries byte-identical; `LYAPUNOV_REFERENCES` gains three keys; `config.py` and `checked_bound` unchanged.
2. **The reference exists (WU-0021.3):** smoke, DEV-0, `--systems lorenz63 rossler chua`, CPU, **`LPC_THREADS=1`**, `nice -n 19`, through `tools/run_preset.sh`, from a clean worktree at develop fc49d5f whose `lpcstudy/` equals `freeze-1`; `results.json` sha256 `07d75aad92835990a62cf16b11c65642a9f25ddaf57da1a1dfa0f6bbde821d46` (as recorded in the unit file); path `/home/brianm/projects/physics/chaos/lpcstudy-wt/run/ext-ref-fc49d5f/runs/ext-ref/smoke/`.
3. **The comparison.** The NEW run uses the same command (smoke, DEV-0, the three systems, CPU, `LPC_THREADS=1`) on the **same host**, from a clean tree at the extension tip; then `python3 -I tools/leafdiff.py <ref results.json> <new results.json>` (exit 0 = no differing leaf; the plan's tool) and, as a second reading, `python3 -I tools/compare_runs.py REF NEW`, which must select tier T0 (same host, device and `LPC_THREADS`) and report bitwise equality of every leaf except `seconds` and `provenance`. **The dispatch message said "LPC_THREADS 8": that would select tier T1 against the `LPC_THREADS=1` reference and would not be bitwise; use 1.** A plain smoke run (no `--systems`) exercises Lorenz-63 only and is not the regression. The cached `lambda_max`, the trajectory digests and all verdict words are among the compared leaves; `lyapunov.json` is recomputed in each run directory (the default 10⁵ steps for the frozen specs).
4. **A spec-literal unit test** (added, not modified): the three frozen specs' `params`, `dim`, `observed_index`, `initial_state`, `max_dt`, `orbit_bound`, `lyapunov_steps` equal the ratified literals typed into the test.
5. **Tests that pin the registry** and change by design (recorded, not loosened): `tests/unit/test_systems.py::200` (`set(SYSTEMS)`), `::326` (bounds dict), `tests/unit/test_experiments.py::975` (`set(SYSTEMS)` and `spec.dim == 3` for every spec, false for S1; the expected `robustness_dimensions` result stays `([5, 10], [])` for every spec since 5 > 4).
6. `tests/slow/test_start_states.py` parametrizes over `SYSTEMS`: three new slow cases (run once by their owner).
7. **Reference-value tests for the new specs** (plan A6/A7; mine to write if assigned): the cached λ of each new spec equals the §0 value bitwise on this host (a different host compares at 1e-12 relative, the T1 rule) and agrees with an independent Benettin/QR (my `spectra.py` routine, or one written in the test without importing `lpcstudy.systems`) within 3 block-SEs; the V6 statistic of each new spec below 10⁻³ (its own gate); `guard_orbit` accepts |x| = B and refuses B(1 + 10⁻⁹) and NaN (A5); the S2 trapping bound 181.88 reproduced by the SLSQP derivation to 10⁻⁶ (the bound's provenance); `inverse_dimension` on the S1 statistics orbit within 3 SE of 0.357 (the H1a reference regime).

## 7. Risks and open questions for the owner, with recommendations

- **R1. S2's time unit.** Specified: `lyapunov_steps` = 4·10⁶ (block SE 1.06%, about 2% true). Accept the reported SE, or raise to 10⁷ (about 1 min; block SE ≈ 0.7%, true ≈ 1.3%): the gain is marginal against a convention that no verdict depends on. **Recommend 4·10⁶ with the SE reported beside every "LT" statement for S2.**
- **R2. S2's rationale.** The bimodal Λ̃ I predicted is absent at 1 LT; S2 is Lorenz-63 at the type-I onset with long coherence and a heavy amplifier tail (§1.2). The scan shows no r near r_c with a clearly bimodal 1-LT exponent. **Recommend keeping S2 (authorized) with the corrected description, and promoting S3 to a full member** (zero cost; the largest qualitative departure available: ν spans two orders of magnitude; the code's V1/V2/V6 pass on it).
- **R3. S3 implementation:** permuted spec (additive; +0.85% in Δ, a different rounding realization of the same attractor) versus `observed_index = 2` with the guard change. **Recommend the permuted spec**; the plan's exception R2 (ii) and the ROADMAP's "S3 guard change" then lapse.
- **R4. Orbit bounds.** S1 300 is empirical; a refusal names the step and the maximum and stops the run; the bound may be raised only by a recorded decision before a fresh run. S2 185 is analytic. S3 50 follows the registry ratio. **Recommend as written.**
- **R5. The registry-pinning tests** change by design (§6.5): record it as such.
- **R6. D = 7 for S1** rests on d_box ≈ d_KY = 3.0 (unverified) and the empirical finiteness of ν; a D = 10 check needs S1 in `robustness_systems` (config change: not in this program).
- **R7. Compute.** S1 at about 2.5–3× Chua; the GPU is held by the ensemble and the CPU by run-2; the plan's .6 waits for the GPU.
- **R8. Expected gate risks on S3 (V4; V7 less than I first said)** are findings, not defects; pre-stated so that they are not read as power failures or repaired.
- **R9. Cosmetic:** `report.py` text says "dof 4"; the numbers use the computed dof. Leave it or batch with the Dysts report unit.
- **R10. Dysts comparison** (§8): a sMAPE-type valid time on the study's forecasts is a code addition (report-only statistic), its own unit (WU-0024).
- **R11. `LYAPUNOV_REFERENCES` for S1:** add the published row (0.1121, Ramasubramanian & Sriram 1999, tolerance 3% as for Rössler's secondary source: the code's 0.11252 is +0.4%); S2 and S3 get the "no confirmed published value" row.

## 8. Items 2 and 3 of the program: further Dysts systems and the descriptive comparison

Facts below are the researcher's (2026-10-20 note, §A, §C, §D); what remains unread there stays unverified.

**What makes a comparison honest (mapping):**

1. **Time.** Dysts integrates in the equation's own time (Radau, rtol = atol = 10⁻¹²) and, with `resample=True`, samples 100 points per dominant period (`period`; `dt` = period/5000 is derived); `timescale="Lyapunov"` samples 100 points per 1/`maximum_lyapunov_estimated`. Zhang & Gilpin (2409.15771, 2505.11349) use 30 points per Lyapunov time with the Dysts annotation. **That annotation is 2.09× (Rössler) and 2.85× (Chua) the study's λ and is inconsistent with Dysts' own spectrum**, so their "Lyapunov times" for Rössler and Chua are 0.48 and 0.35 of the study's. Convert every horizon with the study's λ, print both λ values beside it, and never equate the two "LT" units.
2. **Noise.** 2505.11349 App. E adds Gaussian noise 10⁻³, 10⁻², 10⁻¹ to unit-variance series; the 2021 sweep uses 0–5 standard deviations (no 1% level); 2023 has none. The study's CP copies a *noisy* future at ρ ≥ 0.5% and verifies against the *noisy* truth: the honest rows are ρ = 0.5% and 1% against the 10⁻² level, with the ρ floor stated.
3. **Error metric.** 2021 reports sMAPE averaged over the whole forecast window (no horizon); 2023 defines a valid time as the latest time with sMAPE < 50; 2409.15771 defines VPT as the first horizon with sMAPE > 30; all on the full state. The study's horizon is the first passage of the absolute error on one observed coordinate above θ σ_x (θ = 0.2 primary), censored at 8 LT, Kaplan–Meier median. A sMAPE threshold on a zero-mean coordinate is not a σ-multiple; the two are not interchangeable. Honest options: (a) quote the study's V3 statistic (`cp_median_vpt_lyapunov`; at ρ = 1% the researcher quotes 1.97 / 3.43 / 2.8 LT) with its definition, descriptively; (b) add a report-only VPT with the sMAPE-30 and sMAPE-50 definitions restricted to the observed coordinate, computed on the same forecasts (WU-0024, a code addition), and show both; never convert one into the other. The one Dysts number near ours, context parroting VPT 2.10 ± 0.18 at noise 10⁻² (2505.11349 Table 5, units unstated, averaged over 135 systems), is uncontrolled and is quoted only as such.
4. **Context versus library; baselines.** Context parroting is a 1-nearest-neighbour search in the delay-embedded context (512 or 2 000 points); the study's CP uses N_lib admissible analogs with an 8-LT future (10⁴ analogs ≈ 333 LT of trajectory). State both lengths in LT. **PLP has no counterpart in any Dysts benchmark** (no known-equation model; 2023 says so).
5. **No hypothesis test:** descriptive, labeled DEVELOPMENT, per system, seed id shown; sealed CP numbers quoted only from the promoted document, unchanged.

**Which Dysts systems the machinery can take with only a `SystemSpec`:**

- Criteria: an autonomous ODE flow with a smooth (or continuous piecewise-linear) field writable in `jax.numpy`; a bounded chaotic attractor reached from the registry start; λ_max > 0 (a null needs an interval override: code change); m ≤ 6 (D = 7 ≥ m + 1 for the LM and the χ² dof; D > 2 d_box for the embedding, borderline at m = 6 if d_KY ≈ 3); the observed coordinate at index 0 (permute the state as for S3); a bound on |coordinate 0| justified as in §1 (a non-zero mean is fine: the bound is on |x|); `max_dt` by a V6 check as in §2; **λ recomputed by the study's Benettin (the Dysts Lyapunov fields are unreliable: researcher §A.3, §B.1, §D.1)** with `lyapunov_steps` set for a ≤ 1% SE.
- Eligible from the researcher's ranked list (Dysts names; parameters as relayed there): `Lorenz96` (N = 4, F = 20; m = 4), `HyperLu` (m = 4; λ₄ ≈ −19: stiffness sets max_dt), `HyperJha` (m = 4; two comparable rates), `HindmarshRose` (m = 3; tx = 0.03 sets max_dt), `Chen` (m = 3; fast, Δ ≈ 0.017), `Colpitts` (m = 3; ReLU-type term, C¹ not C² like Chua), `Arneodo` (m = 3), `LorenzCoupled` (m = 6; dof 1, D > 2 d_KY = 6.1 borderline; cost ×3). Each needs the §1–§2 procedure (spectrum, bound tail, V6 order, units) before its spec is written (WU-0023.2).
- Not eligible without code changes: delay equations (`MackeyGlass` and the other `delay: true` entries), PDEs, maps, the `nonautonomous: true` entries (an unbounded phase breaks the whitening and the guard; a (cos, sin) lift makes C singular), Hamiltonian entries with unbounded angles (`DoublePendulum`; `HenonHeiles` is bounded but non-ergodic), m ≥ 7, and entries whose Dysts fields look wrong for a dissipative flow (`SprottA`, `NoseHoover`, `Bouali2`, …) until recomputed.

## 9. Scripts and logs (`docs/agent/notes/2026-10-20-math-extension-specs/`, run by `run.sh`: project venv, `python -s`, one thread, nice 19, `JAX_PLATFORMS=cpu`)

| Script | What it computes | Log |
| --- | --- | --- |
| `ext_common.py` | the candidate specs (not imported by `lpcstudy`); `L63`, `ROS` aliases of the registry | — |
| `spectra.py` | full Benettin/QR spectra (long runs), d_KY, the 10⁵-step cache value and its SE, per-coordinate orbit maxima, the Lorenz trapping bound (SLSQP), S2 per-window exponents | `spectra.log` |
| `lyap_long.py` | the cache value at the specified `lyapunov_steps` by the code's own `lyapunov_guarded`, with the independent block SE | `lyap_long.log` |
| `units.py` | the `build_context` recipe: σ_x, C, whitening scale, AMI delay, ACF time, spacing, split layout per preset, RK4 work, ν / Λ̃ / g_H / 1/d_LB distributions; `LYAP_LONG=1` uses the specified run lengths | `units_long.log` (specified lengths), `units.log` (10⁵ steps; registry L63 and Rössler) |
| `integrator.py` | V6 statistic per `max_dt`, observed order, Richardson error | `integrator.log` |
| `gate_checks.py` | the code's own V1, V2, V6 on real contexts (smoke sizes; specs registered in-process), and the damped-LM efficiency probe at the four noise levels | `gate_checks.log` |
| `trapping.py` | numerical check of the dV/dt identity and of max_E V by surface sampling | `trapping.log` |
| `bound_tail.py` | |x| tails on 2–4·10⁶-step orbits, block maxima | `bound_tail.log` |
| `lyap_check.py` | registry Rössler bitwise against the pilot reference; permuted S3; S1 at max_dt 0.01 (10⁵ steps) | `lyap_check.log` |
| `orbit_bits.py` | whether the permuted Rössler orbit is bitwise the registry orbit (no: 1 ulp at step 37) | `orbit_bits.log` |
| `laminar.py` | S2 z-maxima return-map statistics (lag 2) at r = 166.1 and the control r = 166.0 | `laminar_r166.1.log`, `laminar_r166.0.log` |
| `intermittency_scan.py` | λ and growth-free window fraction for r = 166.0 … 167 | `intermittency_scan.log` |

## 10. What I could not verify

- d_box of S1 (D > 2 d_box uses d_KY as a stand-in); any published λ at r = 166.1; the per-system Dysts benchmark numbers and the VPT definition of 2505.11349 (researcher §E).
- A laminar-length distribution for S2 (§1.2).
- The pipeline's V4 and V7 on the new systems (the LM probe is from the true start; the network-started LM and the slope criterion are untested); the S1 pilot cost is an extrapolation from substep counts.
- The gate checks and the probe used the 10⁵-step Δ (`gate_checks.py` ran before the run lengths were fixed); the specified Δ differs by 0.2–0.9%, which cannot change a pass/fail at these margins.

## Summary (≤ 250 words)

Three additive `SystemSpec` entries are fully specified (§0): S1 hyperchaotic Rössler (m = 4; start (−10, −6, 0, 10); max_dt 0.01; bound 300 on x; 10⁶ Benettin steps → cached λ 0.11251662457254265, +0.4% from the published 0.1121), S2 Lorenz-63 at r = 166.1 (max_dt 0.002; bound 185 from an analytic trapping ball that also reproduces the registry's 40 at r = 28; 4·10⁶ steps → 0.6217010154674514, SE ≈ 1–2%), and S3 Rössler observed through z as a permuted-state spec (bound 50 on z; 10⁶ steps → 0.07133265490530956), which needs no guard change; plus one additive field `lyapunov_steps` (default 10⁵, frozen values untouched). The 30-steps-per-LT convention holds for all. The code's own V1, V2 and V6 pass on real contexts of all three (V6 3·10⁻⁶, 8·10⁻⁵, 1.3·10⁻⁴; RK4 orders 3.8–4.5). Derived units are tabulated against the registry (τ = 5, 5, 3; spacing 150; 1/d_LB 0.357 for S1; ν spanning 1–130 on S3). S2's expected bimodal Λ̃ is absent: it sits at the type-I onset with long coherence and a heavy amplifier tail (R2; recommend keeping S2 and promoting S3). A damped-LM probe keeps V7's median criteria inside the band on S3 at every ρ while 12% of draws saturate at ρ = 5%; V4 remains at risk there; any failure marks the system PROVISIONAL by rule. The exploratory analysis (§5) applies v3's rules unchanged, per system, DEV-3, no overall verdict. The regression is leafdiff/compare_runs T0 bitwise against the WU-0021.3 reference at `LPC_THREADS=1` (not 8) with `--systems lorenz63 rossler chua`, plus by-design updates of three registry-pinning tests. Dysts mapping and eligible systems in §8.
