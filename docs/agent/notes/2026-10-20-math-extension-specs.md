# Extension program: specifications of the additional attractors S1, S2 (and S3)

**DEVELOPMENT / EXPLORATORY: not a hypothesis test.** No sealed seed, no sealed flag, no read of `runs/confirmatory`. Every computation here ran on CPU, one thread, `nice -n 19`, with no preset and no test tier, while the run-2 CPU job and the GPU ensemble were in progress. Nothing under `lpcstudy/`, `tools/`, `docs/study/`, `seeds/`, `ROADMAP.md`, the ledger or the records was changed.

- **Date:** 2026-10-20. **Agent:** applied-mathematician (claude-fable-5-1). **Authorization:** DEC-0037. **Branch:** `wu/ext-math` from develop 22483b4.
- **Read:** my note of 2026-10-19 (`2026-10-19-math-other-attractors.md`, §A.2, A.3, C.3, D) and the researcher's checks of it (`2026-10-19-researcher-attractor-references.md`); `lpcstudy/systems.py`, `config.py`, `data.py`, `dynamics.py`, `oracle.py`, `validation.py`, `embedding.py`, `estimation.py` (LM), `experiments.py` (dof, robustness filter, V4), `analysis.py` (H1a reference, H1b, V7), `pipeline.py` (dof, width rule), `report.py` (`LYAPUNOV_REFERENCES`), `statistics.py` (`V3_SYSTEMS`, `overall_verdict`), `__main__.py` (`--systems`); proposal and methods v3 §2–§9; Methods v2 M2–M4, M11–M13; `docs/study/pilot_results_v3_dev0_reference.json`; `tools/compare_runs.py` (tiers); `tests/unit/test_systems.py`, `test_experiments.py` (registry pins). **Not present yet:** the researcher's Dysts note (`2026-10-20-researcher-dysts-extension.md`); every Dysts statement in §8 is from memory and marked unverified.
- **Scripts and logs:** `docs/agent/notes/2026-10-20-math-extension-specs/` (§9). Scratch seed 20261020 where a seed was needed; DEV-0 pilot leaves read only.

## 0. Summary of what the developer writes (no choice left open)

Three additive `SystemSpec` entries in `lpcstudy/systems.py`; no change to `config.py` (a new system is run with `--systems <name>`, which replaces `core_systems`; `build_context` reads `SYSTEMS[name]`); one key each in `report.LYAPUNOV_REFERENCES` (an empty list: "no confirmed published value"); the three registry-pinning tests updated to the new set (§6).

| Field | S1 `rossler_hyper` | S2 `lorenz63_r166` | S3 `rossler_z` (optional, recommended) |
| --- | --- | --- | --- |
| `field_fn` | new `rossler_hyper_field`: ẋ = −y − z, ẏ = x + a y + w, ż = b + x z, ẇ = −c z + d w | `lorenz63_field` (registry function) | new `rossler_zfirst_field`: state (z, x, y), ż = b + z(x − c), ẋ = −y − z, ẏ = x + a y |
| `params` | `{"a": 0.25, "b": 3.0, "c": 0.5, "d": 0.05}` | `{"sigma": 10.0, "rho": 166.1, "beta": 8.0 / 3.0}` | `{"a": 0.2, "b": 0.2, "c": 5.7}` |
| `dim` | 4 | 3 | 3 |
| `observed_index` | 0 (x) | 0 (x) | 0 (= z of Rössler) |
| `initial_state` | `(-10.0, -6.0, 0.0, 10.0)` | `(1.0, 1.0, 1.0)` | `(0.0, 1.0, 1.0)` (= the registry start (1, 1, 0) permuted) |
| `max_dt` | 0.01 | 0.002 | 0.04 (registry) |
| `orbit_bound` (on coordinate 0) | 300.0 | 185.0 | 50.0 |

Everything else (λ_max, Δ, σ_x, C, τ, ACF time, spacing, starts of the main and estimator trajectories) is derived by the code from these fields; the values below say what the code will derive, so that the first run can be checked against them.

## 1. Exact definitions and derived units

### 1.1 S1: hyperchaotic Rössler (Rössler 1979)

Equations and parameters: confirmed by two secondary sources (researcher note, request 1); the published spectrum is unverified (a Scholarpedia snippet gives 0.112, 0.019, 0, −25.188).

- **Spectrum (this note, `spectra.log`, Benettin/QR, 10⁶ steps at interval 0.2 after a 5 000-step burn-in, block SE over 50 blocks):** λ = (+0.11252 ± 0.00056, +0.02072 ± 0.00034, −0.00001 ± 0.00006, −24.765 ± 0.105); d_KY = 3.005; LT = 1/λ₁ = 8.89 time units; λ₂/λ₁ = 0.184. Two positive exponents: the second direction grows by e^{0.18} per LT.
- **Value the code will cache** (`lyapunov_record`: interval = 20·max_dt = 0.2, 100 000 steps, burn-in 5 000, from `initial_state`): **0.11225907424447891** on this host and XLA build (the registry Lorenz-63 and Rössler values of the pilot reference are reproduced bitwise here, `lyap_check.log`, so this is the number a run on this host will record). Its relative standard error at the code's settings is 1.6% (independent routine, same settings). Δ = 1/(30 λ) = 0.296932; substeps = ⌈Δ/0.01⌉ = 30; dt = 0.009898.
- **Statistics orbit** (registry recipe: start `initial_state`, burn-in 100 LT = 3 000 steps, 200 000 steps at Δ): x mean −24.98, **σ_x = 21.72**; state mean (−24.98, −2.56, 2.56, 25.62); state standard deviations (21.72, 20.23, 12.50, 8.50); covariance eigenvalues (49.7, 147.1, 388.2, 524.3), condition 10.5; **whitening scale** √eig = (7.05, 12.13, 19.70, 22.90) (one whitened unit is 7–23 natural units depending on the direction). The observable is skewed (−0.95) with a long negative tail (0.1% quantile −110.6, 99.9% quantile +14.4).
- **Orbit maxima of |x|** (coordinate 0, the guard's coordinate): Benettin orbit 135.4; statistics orbit with burn-in 129.4; a 4·10⁶-step orbit at Δ (1.19·10⁶ time units, 133 000 LT) **174.1**, block maxima over 100 000-step blocks with median 143.6 and 90th percentile 161.0; 41 steps of 4·10⁶ above 150 (`bound_tail.log`). The other coordinates reach |y| 115, |z| 372, |w| 86; they are not guarded (the bound is on coordinate 0 only, as for the three frozen systems). **Bound 300 = 1.72 × the largest excursion seen in 1.2·10⁶ time units.** The hyperchaotic Rössler attractor has rare large excursions in x and no analytic trapping region that I could derive; the bound is empirical, chosen so that a false refusal (which stops a run, DEF-0015) is improbable over a full-preset trajectory (0.7·10⁶ steps ≈ 2·10⁵ time units, one sixth of the orbit examined). My earlier note's "bound on x ≈ 60" was wrong (it read the Benettin orbit only and the maximum over all coordinates); the guard refused the first attempt at 60 at step 927 (`spectra.log`, first run), which is the guard working as designed.
- **Starts.** The statistics and Benettin orbits start at `initial_state` for every seed (M2); the main and estimator trajectories start at seed-drawn points of the post-burn-in statistics orbit perturbed by 10⁻⁶ whitened (`draw_starts`, label `make_rng(seed, "start", "rossler_hyper")`) and discard the same 3 000-step burn-in. The transient from (−10, −6, 0, 10) stays below |x| = 130, so the burn-in is guarded without a margin problem.

### 1.2 S2: Lorenz-63 at r = 166.1 (type-I intermittency regime, Manneville & Pomeau 1980, r_c = 166.07)

- **Spectrum (4·10⁶ steps at interval 0.04, 1.6·10⁵ time units):** λ = (+0.6217 ± 0.0066, −0.0000 ± 0.0001, −14.288 ± 0.007); d_KY = 2.044; LT = 1.609. Published λ at r = 166.1: none found (researcher, request 2).
- **Value the code will cache** (interval 0.04, 100 000 steps = 4 000 time units): **0.6204447073633099**; its relative standard error at those settings is **5.5% by the block estimate, and larger in truth**: a 200 000-step run in the r-scan gave 0.665 ± 0.018 (`intermittency_scan.log`), 2.3 block-SEs from the long-run value, so the block SE underestimates the slow laminar/burst correlation. The cached value happens to lie 0.2% from the long-run value. See risk R1: the time unit of S2 is uncertain at the 5–8% level with the code's hard-wired 100 000 steps. Δ = 0.053725; substeps ⌈Δ/0.002⌉ = 27; dt = 0.001990.
- **Statistics orbit:** x mean −0.01, **σ_x = 20.34**; state mean (−0.01, −0.01, 155.1); standard deviations (20.34, 35.86, 34.97); covariance eigenvalues (248.7, 1222.9, 1451.1), condition 5.8; **whitening scale** √eig = (15.77, 34.97, 38.09). The observable is symmetric (skewness 0.000) and platykurtic (2.32); quantiles ±44 at 0.1/99.9%.
- **Orbit maxima of |x|:** Benettin 62.4; statistics (with burn-in) 61.5; 2·10⁶ steps at Δ: 56.4 (block maxima 52.4–54.8). **Bound 185 = the analytic trapping ball, rounded up.** Derivation (`trapping.py`, identity checked to 4·10⁻¹⁵): with V = x² + y² + (z − σ − r)² and c = σ + r, dV/dt = −2σx² − 2y² − 2β(z − c/2)² + βc²/2, which is negative outside the ellipsoid E: σx² + y² + β(z − c/2)² ≤ βc²/4. The ball V ≤ max_E V is therefore forward-invariant and contains every ω-limit set; max_E V = 33 079 (SLSQP and 2·10⁶-point surface sampling agree), so every orbit that starts in the ball has |x| ≤ 181.9 for all time. The same derivation at r = 28 gives 39.25, which the ratified registry bound 40 just exceeds: the registry convention is consistent with the trapping ball, and 185 continues it. A false refusal is impossible for an orbit that starts inside the ball ((1, 1, 1) does: V = 30 660 < 33 079). The guard then catches only non-finite values (a code defect), which is its purpose on a globally bounded system.
- **Character of the attractor at r = 166.1 (the point of choosing it) — measured, and weaker than my earlier note claimed.** The scan `intermittency_scan.log` (RK4 at max_dt 0.002, interval 0.04, 4·10⁵ steps per r) gives λ = 0.000 at r = 166.0, 0.42 at 166.075, 0.44 at 166.08, 0.67 at 166.1, 0.79 at 166.15, 0.91 at 166.2, 1.41 at 166.5, 1.69 at 167: the exponent rises continuously from zero at r ≈ 166.07, which is the type-I onset of Manneville and Pomeau with this integrator. The fraction of 1.6-time-unit (1 LT) windows whose Benettin growth is below 0.1 falls from 0.50 (r = 166.0, neutral) to 0.35 (166.1) to 0.14 (167). But (i) the per-state Λ̃ = 30 Λ̄ distribution over 1 LT at r = 166.1 is **not bimodal**: quantiles (1/5/25/50/75/95/99%) = (−0.76, −0.48, 0.13, 0.87, 1.85, 4.88, 6.17) against (−1.16, −0.82, 0.33, 0.74, 1.45, 4.22, 6.43) for the registry Lorenz-63 (`units.log`, both on 1 333–2 000 thinned statistics-orbit states); 29% of states below 0.3 against 24%. (ii) The "laminar phase" is not a stretch of near-periodic z-maxima: the r = 166.0 attractor itself (λ = 0 ± 2·10⁻⁴) is a modulated orbit whose successive z-maxima alternate between about 190 and 227 and drift (lag-2 differences, median 7.2), and r = 166.1 shows the same pattern with the same lag-2 statistics (`laminar_r166.1.log`, `laminar_r166.0.log`); so a return-map diagnostic of laminar length does not separate the phases at this resolution, and I did not get a laminar-length distribution. What S2 measurably adds over Lorenz-63 at r = 28: a long coherence (ACF time 191 steps = 6.4 LT against 0.3 LT), a heavier amplifier tail (g_H at 1 LT: median 6.0, 95th percentile **241** against 2.5 and 25), a lower local dimension (1/d_LB 0.537, d = 1.86, against 0.487, d = 2.05), and the onset regime itself (λ continuous from 0). **The owner should decide whether that is the "qualitative departure" wanted (risk R2).**
- **Starts:** as S1, label `make_rng(seed, "start", "lorenz63_r166")`.

### 1.3 S3: Rössler observed through z, as a permuted-state spec (optional; recommended as a full member)

The guard (`checked_bound`) refuses `observed_index ≠ 0`. Rather than change ratified guard code, S3 is the registry Rössler with the state written as (z, x, y): `observed_index = 0` then observes z and the bound is on z. Whitening, ν, g_H, the delay map and the Levina–Bickel dimension are invariant under a coordinate permutation (the symmetric root C^{±1/2} permutes with the state, and every reported quantity is a trace, a norm or a distance in whitened coordinates).

- **The orbit is not bitwise the registry orbit:** XLA rounds the permuted field differently (first difference at step 37 of a 5 000-step orbit, 1 ulp, `orbit_bits.log`), so S3 is a different realization of the same attractor. Its cached exponent is **0.07220367383989693** (interval 0.8, 100 000 steps), +0.37% from the registry Rössler's 0.07193978510879935, within the 0.8% standard error of either; long run 0.07133 ± 0.00017 (10⁶ steps). Δ = 0.461657 (registry 0.463350); substeps 12; dt 0.03847.
- **Units:** z mean 0.885, **σ_x = σ_z = 2.835**; the observable is spike-dominated: median 0.042, 90% quantile 1.82, 99.9% quantile 22.0, skewness 4.7, kurtosis 26.8. State standard deviations (z, x, y) = (2.84, 5.16, 4.84); eigenvalues (6.29, 21.51, 30.28), condition 4.8; whitening scale (2.51, 4.64, 5.50).
- **Noise meaning:** ρ is a fraction of σ_z. At ρ = 1% the noise (0.028) is 70% of the median z; in the flat phase (z ≲ 0.05, about half of the time) the observable sits below the noise for every ρ ≥ 1%. This is the observability stress the system is chosen for.
- **Bound 50** on z (coordinate 0): maximum 22.85 on every orbit examined (2·10⁶ steps); ratio 2.19, the same ratio as the registry Rössler's 25 against max |x| 11.43.
- **Alternative (owner decision, R3):** `observed_index = 2` on the registry spec with a one-line change in `checked_bound` (keep the bound on coordinate 0 = x). That keeps the registry orbit and λ bitwise and is the design I named in the earlier note, but it edits a ratified guard (DEC-0017 Q1, DEC-0026) and its test. I recommend the permuted spec: purely additive, and a +0.37% difference in the sampling interval is immaterial.

### 1.4 Registry comparison values (same script, same recipe)

| Quantity | L63 r = 28 | Rössler | S1 | S2 | S3 |
| --- | --- | --- | --- | --- | --- |
| λ cached (code settings) | 0.905494 | 0.071940 | 0.112259 | 0.620445 | 0.072204 |
| relative SE of the cached λ | ≈ 0.15% | 0.8% | 1.6% | 5.5% (block; truly 5–8%) | 0.8% |
| Δ, substeps | 0.0368, 4 | 0.4634, 12 | 0.2969, 30 | 0.0537, 27 | 0.4617, 12 |
| σ_x | 7.92 | 5.15 | 21.72 | 20.34 | 2.84 |
| AMI delay → τ (cap 5) | 5 → 5 | 3 → 3 | 6 → 5 | 5 → 5 | 3 → 3 |
| window (D−1)τ | 30 = 1 LT | 18 = 0.6 LT | 30 = 1 LT | 30 = 1 LT | 18 = 0.6 LT |
| ACF time (steps; LT) | 9; 0.3 | 1500; 50 (cap) | 205; 6.8 | 191; 6.4 | 356; 11.9 |
| spacing (steps) | 45 | 150 | 150 | 150 | 150 |
| ν median (p1, p99) | 1.67 (0.72, 6.65) | 1.13 (0.78, 10.1) | 1.91 (1.15, 20.0) | 1.28 (0.45, 5.76) | **14.2 (1.11, 121)** |
| Λ̃ quartiles (p25, p50, p75) | 0.33, 0.74, 1.45 | 0.86, 1.13, 1.35 | 0.82, 1.07, 1.80 | 0.13, 0.87, 1.85 | −0.12, 0.71, 1.67 |
| g_H at 1 LT median (p95) | 2.46 (25) | 3.32 (7.4) | 2.91 (10.2) | 5.99 (241) | 0.044 (23) |
| 1/d_LB (k = 20), d | 0.487, 2.05 | 0.514, 1.94 | **0.350, 2.86** | 0.537, 1.86 | 0.523, 1.91 |

Pilot reference (DEV-0) for the registry systems: 1/d_LB reference 0.489 / 0.510 / 0.503 (L63 / Rössler / Chua), consistent with the column values above (my scratch pool differs from the run's).

## 2. Time conventions

- **The 30-steps-per-LT convention is kept for all three**; no override is needed (λ_max > 0 and finite in each case). The null (Rössler c = 2.5, λ = 0) would need one and is not part of this program.
- **λ_max, standard errors and run lengths:** §1. Steps for a 1% relative SE at the code's interval: S1 about 2.5·10⁵ (interval 0.2); S2 about 3·10⁶ by the block estimate (more in truth); S3 7·10⁴. The code runs 10⁵ (hard-wired in `lyapunov_record`). Consequence: S2's time unit is a 5–8%-noisy function of the start state and the step. It is a convention (every horizon is in steps and Λ̃ is per 30 steps), so no verdict depends on its accuracy, but "1 LT" on S2 means 30 steps of 0.0537, which may be 0.95–1.08 true Lyapunov times. Recommendation R1: an additive `SystemSpec` field `lyapunov_steps: int = 100_000` read by `lyapunov_record`, set to 3 000 000 for S2 (about 3 min single-threaded; the frozen specs keep the default and their cached values bitwise).
- **RK4 step and V6** (`integrator.log`; 20 attractor states, 30 steps of Δ, the code's statistic max |x_h − x_{h/2}|/σ_x; gate < 10⁻³; formal order 4):

| System | max_dt | substeps | V6 statistic | observed order p (h, h/2, h/4) | Richardson error at h/2 (σ_x) |
| --- | --- | --- | --- | --- | --- |
| S1 | 0.02 | 15 | 1.7·10⁻⁵ | 3.88 | 8·10⁻⁸ |
| S1 | **0.01** | **30** | **1.1·10⁻⁶** | 3.95 | 5·10⁻⁹ |
| S1 | 0.005 | 60 | 7.4·10⁻⁸ | 3.92 | 3·10⁻¹⁰ |
| S2 | 0.008 | 7 | 9.9·10⁻³ FAIL | 4.78 | 1·10⁻⁵ |
| S2 | 0.004 | 14 | 3.6·10⁻⁴ (2.8× margin) | 4.41 | 8·10⁻⁷ |
| S2 | **0.002** | **27** | **1.7·10⁻⁵** | 4.51 | 3·10⁻⁸ |
| S3 | 0.08 | 6 | 1.6·10⁻³ FAIL | 3.80 | 9·10⁻⁶ |
| S3 | **0.04** | **12** | **1.2·10⁻⁴** | 3.91 | 6·10⁻⁷ |

  The observed orders are 3.8–4.5 (4 formal; S2's 4.4–4.8 reflects the error being dominated by the fastest states where the asymptotic regime is entered late), so no bug and no non-smoothness. The registry values are 4.8·10⁻⁴ (Lorenz), 4.3·10⁻⁵ (Rössler), 2.9·10⁻⁴ (Chua) in the pilot. Choices: S1 max_dt = 0.01 (V6 margin 900×, half the cost of 0.005; 0.02 would also pass with a 60× margin and halve the cost again; I fix 0.01 because the Benettin cache interval 20·max_dt = 0.2 then also gives the 1.6% exponent); S2 max_dt = 0.002 (0.004 passes with only 2.8× margin on 20 states; the run's V6 uses 20 test states that may include faster ones); S3 the registry's 0.04. The QoI (the discrete map, LPC.NV.1) is defined at these steps; the discretization error at 1 LT is 10⁻⁸–10⁻⁶ σ_x, four or more orders below the smallest noise level 0.005 σ_x.
- **Cost.** RK4 work per flow-map step scales with substeps × m (field) and with substeps × m² for the Jacobian paths (LM, ν, g_H). Relative to Chua (16 substeps, m = 3): S1 (30, m = 4) ≈ 2.5–3.3×; S2 (27, 3) ≈ 1.7×; S3 ≈ Rössler (1×). Data generation alone (statistics + main + estimator trajectories, burn-ins included) is 36 M RK4 substeps for S1 at the full preset, 33 M for S2, 15 M for S3 (`units.log`), a minute or two; the forecasts and the LM dominate as in the pilot. Expect the pilot preset on S1 to take about 2.5–3× Chua's pilot time; the owner schedules it (R7).

## 3. Embedding, estimator and library

- **Delay τ (AMI first minimum, cap ⌊30/6⌋ = 5):** S1: AMI minimum 6 → τ = 5 (capped), window 30 steps = 1 LT; S2: 5 → 5, window 1 LT; S3: 3 → 3, window 18 steps = 0.6 LT (as the registry Rössler). D = 7 unchanged. Window cap ≤ 1 LT holds for all.
- **Embedding of S1:** d_KY = 3.005; Sauer–Yorke–Casdagli needs D > 2 d_box (box-counting, prevalent, generic; researcher request 11): 7 > 6.01 if d_box ≈ d_KY, which is unverified. Empirical check: ν is finite on all 1 333 sampled states (max 38.8, p99 20.0; `units.log`), so AᵀA (the 4×4 delay-map information at D = 7) is invertible everywhere sampled; the delay map is locally injective there. Global two-to-one folds (the Lorenz-z failure mode, catalog #7) are not expected: the x-observable of the hyperchaotic Rössler has no symmetry. The 1/d_LB = 0.350 (d = 2.86) is the H1a reference regime "d ≈ 3".
- **PLP estimator:** window-start state u ∈ ℝ^m, D = 7 residuals; the LM solves the m×m normal equations with damping (`estimation.py`), so it needs D ≥ m (D = 7 > 4) and a full-rank 7×m Jacobian (ν finite). **dof = D − m = 3 for S1** (4 for the others): the χ² goodness-of-fit reference changes to the 0.999 quantile with 3 dof (16.27 instead of 18.47); the code computes `embed_dim − spec.dim` everywhere (`gof_threshold`, `lm_block`, `check_record`), so this is automatic; only the explanatory text in `report.py` says "dof 4" (cosmetic, R9). `robustness_dimensions` keeps d > m: (5, 10) for every new system (not run: `robustness_systems` stays `("lorenz63", "rossler")`).
- **Estimator width rule** (`networks.py`): widths (64, 128) at the full and pilot presets, the smallest width whose validation loss is within 5% of the best is kept; `estimator_pairs` = 10⁵ (pilot 4·10⁴) from the separate trajectory at stride 5, targets the whitened window-start state in ℝ^m (m = 4 outputs for S1; the network adapts). No change.
- **Library sizes:** unchanged, (10³, 10^3.5, 10⁴, 10^4.5, 10⁵); the library segment is 100 271 steps (S1, S2) or 100 259 (S3) plus the 8-LT future; the core cell 10⁴ at ρ = 1%. For S1 at d ≈ 3 the analog seed should scale as N_lib^{−2/3} (H1a's prediction with 1/d_LB ≈ 0.35) instead of N_lib^{−1} at d ≈ 2: CP is relatively worse at every N_lib.
- **ACF time, thinning and effective sample size.** ACF 1/e envelope times 205 / 191 / 356 steps (6.8 / 6.4 / 11.9 LT) are all above the 1-LT cap, so spacing = max(⌈5·30⌉, 30) = 150 steps = 5 LT for all three (as Rössler and Chua; Lorenz-63 has 45). Consecutive states are therefore 0.73 (S1), 0.79 (S2), 0.42 (S3) ACF times apart: not independent at the observable level, which is the same situation as Rössler (0.1 ACF times) and Chua (2). The block length is fixed at 5 by v3 (25 LT per block); the per-state statistics (w*, horizons) decorrelate faster than the observable, and the block-sensitivity flag (√max(1, V*(10)/V*(5)), v3 §8) is the pre-registered instrument: expect it to fire more often on S3 than on the others. Trajectory lengths: main 311 831 (pilot) / 701 831 (full) steps for S1 and S2, 311 735 / 701 735 for S3, the same as Rössler and Chua.
- **Noise levels ρ** unchanged (0.5, 1, 2, 5% of σ_x); admissible thresholds unchanged (θ ≥ 3√2 ρ: at ρ = 5% only θ ∈ {0.3, 0.5}). The meaning of σ_x per system is in §1; for S3 see the spike remark.
- **Clipping at 10 σ_x:** S3's spikes reach 7.8 σ_z, so a wrong-phase forecast can produce errors up to about 8 σ_z, below the clip; the counters will show whether any clip occurs.

## 4. Expected behaviour of the gate V1–V7 (tolerances exactly as written in `gate_status`; none changed)

| Check | Gate | S1 | S2 | S3 |
| --- | --- | --- | --- | --- |
| V1 Jacobians vs finite differences | both < 10⁻⁴ | pass (smooth polynomial field; registry values 10⁻⁸–10⁻⁹) | pass | pass |
| V2 Cramér–Rao at ρ = 10⁻⁴, 5 states | median ∈ [0.8, 1.2] | pass (ρν ≤ 4·10⁻³ whitened: linear) | pass | pass expected (ρν ≤ 0.02 even at ν = 190); 5 states only, so one flat-phase state cannot move the median outside |
| V3 CP valid time | report only | report; expect below Rössler's 3.3 LT (d ≈ 3 seed) | report | report; dominated by spike timing |
| V4 w* converged at M = 200 | median half-width ≤ 0.05 | pass expected | pass expected | **at risk**: in the flat phase both errors are tiny, c = E[(e_C − e_P)²] is near zero and w* is ill-conditioned (`curvature_floor` counts); half-widths of w* may exceed 0.05 |
| V5 Kaplan–Meier fixture | < 0.01 | pass (system-independent) | pass | pass |
| V6 step halving over 1 LT | < 10⁻³ σ_x | pass, 1.1·10⁻⁶ | pass, 1.7·10⁻⁵ | pass, 1.2·10⁻⁴ |
| V7 efficiency: median δ/(ρν) at every ρ and median slope, both ∈ [0.9, 1.1] | both | pass expected (ν p99 = 20 → ρν ≤ 1 at ρ = 5%; the median state has ρν = 0.1) | pass expected (as Lorenz-63: 0.998–1.017 in the pilot) | **likely FAIL at ρ = 5% and possibly 2%**: a quarter of the states have ν > 31, so ρν ≥ 1.5 whitened units at ρ = 5%, beyond the linear regime; δ saturates at the attractor size (2–3 whitened), the ratio falls below 0.9 for those states and the median slope of ln δ on ln ρ drops below 0.9 |

**What a failure means (study rule, v3 §6 E0):** the system is marked PROVISIONAL, every verdict is computed and shown with that label, the failure is reported and referred to the owner, and nothing is retuned, rerun or repaired. For S3 a V7 failure is itself the finding the system was chosen to expose (the Cramér–Rao floor is a first-order statement; where ν is large the estimator leaves the linear regime at the study's noise levels). For S1 and S2 I expect the gate to pass; a V4 or V7 failure there would be unexpected and would go to the owner as a defect candidate, not as a tuning problem.

## 5. Pre-specified exploratory analysis (fixed before any run on the new systems)

**Label:** DEVELOPMENT / EXPLORATORY, development seed named in every table (DEV-3 or DEV-4, never a seed used for the system before, never the confirmatory seed, never `--confirmatory`), one system per run, `--systems <name>`, pilot preset after a smoke plumbing run; the full preset only by owner decision.

**Estimands and decision rules:** exactly those of v3 §2 and §7 (bands, levels 1 − 0.05/3 for H2a, H2b, H3c and 95% otherwise, block length 5, 2 000 resamples (500 at pilot), the 50-state minimum, the Q-N reading table, the K rule, the gain-bound screen), applied unchanged, per system. No criterion, band, level, block length or threshold is changed for the extension; the per-system verdict rule (pass / fail / inconclusive) is the code's.

**Per-system verdicts only; no overall verdict.** `overall_verdict` requires `V3_SYSTEMS` = (lorenz63, rossler, chua) and reads "inconclusive" when any is missing, so a run of a new system prints an overall line that must not be read. The reason is statistical as well as formal: v3's "supported" is an intersection–union test over the three pre-registered systems, which controls the error of "supported" at the per-system level without a multiplicity correction; "not supported" is a union, whose error grows with the number of systems (about 7.3% over three at 95%, about 23% over five). Adding systems to the required set after the freeze would change both error rates of the sealed verdict; keeping them out leaves it untouched. The extension therefore reports, per new system, the per-hypothesis verdict with its interval, and states that no extension result bears on the sealed study's overall verdicts. A confirmatory claim about any new system would need its own sealed seed and freeze (DEC-0037 item 1).

**Decidability at the full preset (projected from v3 §7 and M12; "structural" means the design, not the sample size, decides):**

| Hypothesis | S1 | S2 | S3 |
| --- | --- | --- | --- |
| H1a (1/d_fit vs 1/d_LB, ±25%) | decidable; reference ≈ 0.35, band ±0.09, projected half-width ≈ 0.07 | decidable (≈ 0.54) | decidable (≈ 0.52) |
| H1b (PLP slope ∈ [0.8, 1.2]) | decidable; the pre-specified counterexample is an interval entirely outside the band (two growth directions) | decidable | decidable, but the fit has a wider x-range (g_H spans 0.003–23) |
| H1c (horizon law ratio ∈ [0.8, 1.25]) | decidable | decidable; the per-state Λ̄ straddles bursts | **structurally weak**: T(θ) on ln θ is set by spike timing, not by smooth error growth; expect inconclusive or fail with the reading "the exponential envelope hypothesis (P1-5) fails" |
| H1d (Spearman ≥ 0.7 for ε̂, δ̂, Λ̂) | decidable | decidable | decidable; δ̂ should be the strongest (ν̂ carries two orders of magnitude) |
| Q-N (ΔR² reading) | reachable (±0.04) | reachable | logit part needs ≥ 50 interior states: may be undetermined |
| H2a (i) range < 0.1; (ii) partial r ∈ (−0.1, 0.1) | (i) decidable; (ii) refutable only (needs |r| ≲ 0.01 to pass); predicted: a larger |r| than on the three (anisotropic two-direction seeds) | (i) decidable; (ii) refutable only | (i) decidable; (ii) refutable; w* = 1 states may exceed 5%, adding the third part by the existing rule |
| H2b (i), (ii) lower bounds > 0 | decidable | decidable | decidable |
| H2c (A4 − A2 and A4 − best single, upper bounds < 0) | likely inconclusive (as Rössler, Chua) | likely inconclusive | **the one system where it can pass**: ν varies by 100×, so a state-dependent rule has something to gain; pre-specified readings: pass = observability makes allocation pay; fail with A4o − A2 < 0 = "deployable seeds limit it"; fail with A4o − A2 > 0 = counterexample to the mechanism, not to P1 |
| H2d (A4/A3 − 1 ≤ 0.10) | undetermined (wide) | undetermined | undetermined |
| H2e (noise matching, lower bound > 0 at both ρ) | decidable | decidable | decidable |
| H3a (Holm log-rank, all p < 0.01) | inconclusive-prone (small regimes; v3 §8) | same | same; many censored horizons in the flat phase |
| H3b (weight-tree Λ̃ < 0.2; horizon-tree Λ̃ largest) | decidable in part; predicted: horizon-tree Λ̃ importance lower than on the three (two rates) | decidable; the target claim for S2 | decidable; predicted: the weight tree loads on ln δ̂/ρ (observability), not Λ̃ |
| H3c (A5/A4 ≤ 1.05) | decidable | decidable | decidable |
| gain-bound screen | report | report | report |

**Reading rules per outcome pattern (fixed now):**

1. Gate fails on a system: all its verdicts PROVISIONAL, shown, referred (§4); no other rule applies.
2. S1, H1a passes at 1/d_LB ≈ 0.35: the N_lib^{−2/d} law holds at d ≈ 3 (new regime). Fails below the band: the same shortfall as Rössler/Chua, with no published prediction (researcher request 12); fails above: report, no reading pre-specified.
3. S1, H1b interval entirely outside [0.8, 1.2]: the seed × amplifier law breaks when the amplifier is not rank-one dominated (P1-5/L1 regime); inside: the law survives two growth directions.
4. S1, H2a(ii) interval wholly above the Lorenz-63 / Rössler / Chua confirmatory values: predicted sign (anisotropy from two directions); report the three sealed values beside it without any claim about them.
5. S2, H3b: horizon-tree Λ̃ largest and weight-tree Λ̃ < 0.2 = "instability sets the horizon, not the weight" holds at the type-I onset; weight-tree Λ̃ ≥ 0.2 = the pre-registered reading "seed anisotropy", with the amplifier tail (g_H p95 = 241) named as the mechanism.
6. S2, H1c: pass = the per-state exponential law survives the bursts; fail = read with the Λ̃ spread (29% of states below 0.3), not as a numerical defect.
7. S3, V7 passes and H2c passes: observability decides allocation where it varies (the mechanism the three frozen systems could not show, Methods v2 M13 item 1). V7 passes and H2c fails with A4o − A2 < 0: the deployable δ̂ limits it. H1d-δ̂ ≥ 0.7 with H1d-ε̂ < 0.7: L4 (ε̂ through R ν̂) is the weak proxy.
8. Any system: fraction of states with w* = 0 or w* = 1 reported; a part with < 50 states is inconclusive by the code's rule, never "fail".
9. Any system: block-sensitive flags reported as in v3 §8; no interval widened.

## 6. Regression requirement for the developer

1. **Additive only.** New `SystemSpec` entries and field functions; the three frozen entries byte-identical; `LYAPUNOV_REFERENCES` gains three keys with empty lists; `config.py` unchanged; no change to `checked_bound` (under the permuted-S3 recommendation).
2. **The bitwise comparison.** `tools/compare_runs.py REF NEW` with REF = a smoke run at freeze-1 and NEW = a smoke run at the new commit, **both on the same host and XLA build, both at `LPC_THREADS=8`, both with `--systems lorenz63 rossler chua`**. Tier T0 is selected mechanically (same host, device, threads) and requires every leaf except `seconds` and `provenance` to be IEEE-bitwise equal; that includes the cached `lambda_max`, the trajectory digests, and all verdicts. **It needs more than "smoke at LPC_THREADS 8":** (a) the smoke preset's `core_systems` is `("lorenz63",)`, so a plain smoke run never exercises the frozen Rössler and Chua paths; the `--systems` override (a config replacement at run time, not a file change) covers all three; (b) a different host or thread count makes the tier T1 (tolerances), which is not bitwise; (c) the freeze-1 REF run must exist on the same host or be regenerated there at freeze-1 (an owner action, since it reads the freeze-1 tree).
3. **A spec-literal unit test** (added, not modified): the three frozen specs' `params`, `dim`, `observed_index`, `initial_state`, `max_dt`, `orbit_bound` equal the ratified literals typed into the test (stronger than the existing bound-only test).
4. **Tests that pin the registry** and must be updated by design (not loosened): `tests/unit/test_systems.py::200` (`set(SYSTEMS) == {...}`), `::326` (bounds dict), `tests/unit/test_experiments.py::975` (`set(SYSTEMS)` and `spec.dim == 3` for every spec, which is false for S1). The expected sets become the five names and the robustness-dimension expectation becomes `(kept, skipped) = ([5, 10], [])` for every spec (5 > 4 holds). The change is recorded in the unit log as a by-design update with the reason.
5. `tests/slow/test_start_states.py` parametrizes over `SYSTEMS`: three new slow cases appear (cost; run by their owner only).
6. **Reference-value tests for the new specs** (the ones I would write if the unit assigns them to me): the cached λ of S1 and S3 on this host equal the values in §1 bitwise (regression, same host and build; a different host compares at 1e-12 relative per the compare_runs T1 rule); the V6 statistic of each new spec below 10⁻³ (its own gate); the S2 analytic trapping bound 181.88 reproduced by the SLSQP derivation to 1e-6 (an independent check of the bound's provenance); `inverse_dimension` on the S1 statistics orbit within 3 SE of 0.350.

## 7. Risks and open questions for the owner, with recommendations

- **R1. S2's time unit.** The code's 10⁵-step Benettin run gives λ with a 5–8% uncertainty on S2 (1.6% on S1). Options: accept (convention; record the long-run 0.6217 ± 0.0066 beside the cached value), or add `lyapunov_steps` (additive field, default 10⁵) and set 3·10⁶ for S2. **Recommend the field.**
- **R2. S2's rationale.** The bimodal Λ̃ I predicted is not there at 1 LT; S2 is Lorenz-63 at the type-I onset with long coherence and a heavy amplifier tail (§1.2). Keep r = 166.1 as authorized, with that description, or replace the second departure. The scan shows no r near r_c with a clearly bimodal 1-LT exponent. **Recommend keeping S2 with the corrected description, and promoting S3 from optional to a full member** (zero cost, the largest qualitative departure available: ν spans two orders of magnitude).
- **R3. S3 implementation:** permuted spec (additive; +0.37% in λ, a different realization) versus `observed_index = 2` with a guard change (identical orbit; edits ratified code). **Recommend the permuted spec.**
- **R4. Orbit bounds.** S1 300 is empirical (1.72× the largest excursion in 1.2·10⁶ time units); a refusal in a run names the step and the maximum and stops the run; the bound may then be raised only by a recorded decision before a fresh run, never during one. S2 185 is analytic. S3 50 follows the registry ratio. **Recommend as written.**
- **R5. The registry-pinning tests** change by design (§6.4); this is not a loosening but must be recorded as such.
- **R6. D = 7 for S1** rests on d_box ≈ d_KY = 3.0 (unverified) and on the empirical finiteness of ν; a robustness pass at D = 10 is available through `robustness_dims` only if S1 is added to `robustness_systems` (a config change: not in this program).
- **R7. Compute.** S1 at about 2.5–3× Chua's time; the GPU is held by the ensemble (DEC-0037 item 4) and the CPU by run-2; the pilot on S1 waits for one of them.
- **R8. Expected gate failure on S3 (V7, possibly V4)** is a finding, not a defect; pre-stated here so that it is not read as a power failure or repaired.
- **R9. Cosmetic:** `report.py` text says "dof 4"; the numbers use the computed dof. A text fix is a non-additive edit to the report module; leave it or batch it with the Dysts report unit.
- **R10. Dysts comparison** (§8) needs the researcher's note before any number is quoted; a sMAPE-type valid time is a code addition (a new report-only statistic), its own unit.

## 8. Items 2 and 3 of the program: further Dysts systems and the descriptive comparison

**Everything about Dysts below is from memory and unverified until `2026-10-20-researcher-dysts-extension.md` says otherwise.**

**What makes a comparison honest (mapping):**

1. **Time.** Dysts samples trajectories at a fixed number of points per dominant period (I recall `pts_per_period` ≈ 100 with `resample=True`), not per Lyapunov time; its `maximum_lyapunov_estimated` and the study's cached λ differ by a few per cent for the same system. Convert every horizon to Lyapunov times with the λ of the framework that produced it, and print both λ values side by side. The study's convention (30 steps per LT, Δ = 1/(30 λ)) is itself quoted as the Dysts convention in `systems.py`; whether Dysts states it as such is for the researcher.
2. **Noise.** The Dysts forecasting benchmark and the context-parroting paper forecast noise-free (or separately noised) trajectories; the study's CP copies a *noisy* future from a library at ρ ≥ 0.5% and verifies against the *noisy* truth. The honest row is the study's ρ = 0.5% cell with the ρ floor stated; at larger ρ the study's valid time is a different quantity.
3. **Error metric.** Dysts / Zhang & Gilpin use sMAPE (percent, over all state coordinates, I recall a threshold of 30 for the valid prediction time) on the full state; the study uses the first passage of the absolute error on one observed coordinate above θ σ_x (θ = 0.2 primary; noisy verification; censored at 8 LT; Kaplan–Meier median). A sMAPE of 30% on a zero-mean coordinate is not a fixed σ-multiple, so the two valid times are not interchangeable. Honest options: (a) report the study's V3 statistic (`cp_median_vpt_lyapunov`, pilot 2.1 / 3.3 / 3.0 LT) with the metric spelled out, as a descriptive comparison only; (b) add a report-only valid time with the sMAPE definition restricted to the observed coordinate, computed on the same forecasts (a code addition, its own unit), and show both; never convert one into the other.
4. **Context versus library.** Context parroting uses a context window from the same trajectory; the study's CP uses N_lib admissible analogs each with an 8-LT future. State N_lib in LT of trajectory (10⁴ analogs = 333 LT) beside the paper's context length.
5. **No hypothesis test:** the comparison is descriptive, labeled DEVELOPMENT, per system, with the seed id; the sealed CP numbers may be quoted only from the promoted document, unchanged.

**Which Dysts systems the machinery can take with only a `SystemSpec`** (criteria, then names from memory):

- Criteria: an autonomous ODE flow with a smooth (or continuous piecewise-linear) field writable in `jax.numpy`; a bounded chaotic attractor reached from the registry start; λ_max > 0 (a null needs an interval override: code change); state dimension m ≤ 6 (D = 7 ≥ m + 1 for the LM and the χ² dof; D > 2 d_box for the embedding); the observed coordinate placed at index 0 (permute the state as for S3); a bound on coordinate 0 justified as in §1; `max_dt` set by a V6 check as in §2. The code then derives everything else.
- Likely eligible (names as I recall them in Dysts; unverified): Lorenz84, Rossler, Thomas, Halvorsen, Chen, Lu, Dadras, Arneodo, RabinovichFabrikant, the Sprott family, HyperRossler (= S1), HyperLorenz and other 4-D hyperchaotic flows, Lorenz96 at N = 5 or 6 (one positive exponent; N = 8 needs D ≥ 11: config change), HenonHeiles (a Hamiltonian flow; non-ergodic phase space, so the statistics orbit samples one component: caveat), Lorenz63 variants (= S2).
- Not eligible without code changes: delay equations (MackeyGlass), PDEs (KuramotoSivashinsky), maps (Henon, Lozi, Ikeda), non-autonomous forced systems (an unbounded phase breaks the whitening and the guard; a (cos, sin) lift makes C singular), systems with m ≥ 7, systems whose attractor is not bounded in coordinate 0.

## 9. Scripts and logs (`docs/agent/notes/2026-10-20-math-extension-specs/`, run by `run.sh`: project venv, `python -s`, one thread, nice 19, `JAX_PLATFORMS=cpu`)

| Script | What it computes | Log |
| --- | --- | --- |
| `ext_common.py` | the candidate specs (not imported by `lpcstudy`) | — |
| `spectra.py` | full Benettin/QR spectra (long runs), d_KY, the code's cache value and its SE, per-coordinate orbit maxima, the Lorenz trapping bound (SLSQP), S2 per-window exponents | `spectra.log` |
| `units.py` | the `build_context` recipe: σ_x, C, whitening scale, AMI delay, ACF time, spacing, split layout per preset, RK4 work, ν / Λ̃ / g_H / 1/d_LB distributions; also for the registry L63 and Rössler | `units.log` |
| `integrator.py` | V6 statistic per `max_dt`, observed order, Richardson error | `integrator.log` |
| `trapping.py` | numerical check of the dV/dt identity and of max_E V by surface sampling | `trapping.log` |
| `bound_tail.py` | |x| tails on 2–4·10⁶-step orbits, block maxima | `bound_tail.log` |
| `lyap_check.py` | registry Rössler bitwise against the pilot reference; permuted S3; S1 at max_dt 0.01 | `lyap_check.log` |
| `orbit_bits.py` | whether the permuted Rössler orbit is bitwise the registry orbit (no: 1 ulp at step 37) | `orbit_bits.log` |
| `laminar.py` | S2 z-maxima return-map statistics (lag 2) at r = 166.1 and the control r = 166.0 | `laminar_r166.1.log`, `laminar_r166.0.log` |
| `intermittency_scan.py` | λ and growth-free window fraction for r = 166.0 … 167 | `intermittency_scan.log` |

## 10. What I could not verify

- The published spectrum and d_KY of the hyperchaotic Rössler; any published λ at r = 166.1; d_box of S1 (D > 2 d_box uses d_KY as a stand-in); every Dysts convention in §8 (sampling, metric, threshold, noise).
- A laminar-length distribution for S2 (my return-map diagnostic does not separate the phases; §1.2).
- The real pipeline's V4 and V7 on the new systems (predictions only; the first smoke/pilot run is the check). The S1 pilot cost is an extrapolation from substep counts.
- Whether the freeze-1 smoke reference exists on this host at `LPC_THREADS=8` with `--systems lorenz63 rossler chua` (an owner action if not).

## Summary (≤ 250 words)

Three additive `SystemSpec` entries are fully specified (§0): S1 hyperchaotic Rössler (m = 4, a = 0.25, b = 3, c = 0.5, d = 0.05, start (−10, −6, 0, 10), max_dt 0.01, bound 300 on x), S2 Lorenz-63 at r = 166.1 (max_dt 0.002, bound 185 from an analytic trapping ball that also reproduces the registry's 40 for r = 28), and S3 Rössler observed through z as a permuted-state spec (bound 50 on z), which avoids any guard change. The 30-steps-per-LT convention holds for all; the code will cache λ = 0.112259 (S1, SE 1.6%), 0.620445 (S2, SE 5–8%: risk R1, recommend an additive `lyapunov_steps` field) and 0.072204 (S3, +0.37% from the registry's, a different rounding realization). V6 passes with margins of 900×, 60× and 8×; observed RK4 orders 3.8–4.5. Derived units (τ = 5, 5, 3; spacing 150 for all; 1/d_LB = 0.350 for S1, the d ≈ 3 regime; ν spanning 1–121 on S3) are tabulated against the registry systems. S2's expected bimodal Λ̃ is not present: the attractor is at the type-I onset (λ continuous from 0 at r ≈ 166.07) with long coherence and a heavy amplifier tail; owner decision R2, with the recommendation to keep S2 as described and promote S3. The gate is expected to pass on S1 and S2 and to fail V7 (possibly V4) on S3, which marks it PROVISIONAL by rule and is itself the finding. The exploratory analysis (§5) applies v3's estimands and rules unchanged, per system, with no overall verdict; the regression requires T0 bitwise equality on smoke with `--systems lorenz63 rossler chua` at `LPC_THREADS=8` on the same host, plus by-design updates of three registry-pinning tests.
