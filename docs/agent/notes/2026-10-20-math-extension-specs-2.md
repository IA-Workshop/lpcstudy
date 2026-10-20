# Extension program, second note: specifications of the further candidates S4, S5, S6 (S7 not specified), batching and cost

**DEVELOPMENT / EXPLORATORY: not a hypothesis test.** No sealed seed, no sealed flag, no read of `runs/confirmatory`. Every computation ran on CPU, one thread, `nice -n 19`, no preset, no test tier, no GPU, while run-2 and the GPU ensemble were active. Nothing under `lpcstudy/`, `tools/`, records or the ledger was changed. This note is WU-0023.2 for S4–S7 (owner instruction of 2026-10-20 relayed by the main session; `WU-0023-dysts-systems.md` Log). It extends `2026-10-20-math-extension-specs.md` (WU-0021.2; "note 1" below); §§0–7 follow note 1's format, §8 answers (a)–(c).

- **Agent:** applied-mathematician (claude-fable-5-1). **Branch:** `wu/ext-math`, merged from develop 02b274e (contains the researcher note `2026-10-20-researcher-dysts-extension.md`, §B.3 and §D.2, from which the candidates and their Dysts parameters are taken).
- **Scripts and logs:** the same directory as note 1, `docs/agent/notes/2026-10-20-math-extension-specs/`, with the candidate specs added to `ext_common.py` (S4–S6) and the logs suffixed `_s456`, `_s45_fine`, `_s5`, plus `bursts.py`/`bursts.log`. `run.sh` now takes `ARGS="S4 S5"` to pass selectors. Scratch seed 20261020.
- **Every spectrum below was recomputed here** (independent Benettin/QR on the code's RK4 flow map, long runs, block SE over 50 blocks) and the value the code will cache was computed with the code's own `lyapunov_guarded` at the specified `lyapunov_steps`. The Dysts Lyapunov fields were used for nothing (researcher §A.3, §B.1).

## 0. What the developer writes (S4, S5, S6)

Additive `SystemSpec` entries as in note 1 §0 (same `lyapunov_steps` field, same `LYAPUNOV_REFERENCES` keys with empty lists, the same three registry-pinning tests updated; the `--systems` route; no `config.py` or `checked_bound` change).

| Field | S4 `hindmarsh_rose` | S5 `hyper_jha` | S6 `lorenz96_4` |
| --- | --- | --- | --- |
| `field_fn` | new `hindmarsh_rose_field` (equations in §1.1; **ẏ and ż UNVERIFIED, see R-S4-1**) | new `hyper_jha_field`: ẋ = a(y − x) + w, ẏ = −xz + bx − y, ż = xy − cz, ẇ = −xz + dw | new `lorenz96_field`: Ẋ_k = (X_{k+1} − X_{k−2}) X_{k−1} − X_k + F, k mod 4 |
| `params` | `{"a": 0.49, "b": 1.0, "c": 0.0322, "d": 1.0, "s": 1.0, "tx": 0.03, "tz": 0.8}` | `{"a": 10.0, "b": 28.0, "c": 2.667, "d": 1.3}` (Dysts' 2.667, not 8/3: the Dysts entry is the reference) | `{"F": 20.0}` |
| `dim` | 3 | 4 | 4 |
| `observed_index` | 0 (x, the fast membrane variable) | 0 (x) | 0 (X_1) |
| `initial_state` | `(0.1, 0.1, 0.1)` | `(1.0, 1.0, 1.0, 1.0)` | `(20.0, 20.01, 20.0, 20.0)` (the fixed point X_k = F perturbed) |
| `max_dt` | 0.0025 | 0.0025 | 0.005 |
| `orbit_bound` (coordinate 0) | 5.0 | 80.0 | 60.0 |
| `lyapunov_steps` | 2 000 000 | 2 000 000 | 1 000 000 |
| cached λ on this host (expected, bitwise) | 0.21688316515721046 | 0.3603046265219353 | 1.2018430962199733 |
| Δ = 1/(30 λ); substeps | 0.153693; 62 | 0.092514; 38 | 0.027735; 6 |

**S4 may not be implemented until R-S4-1 (the ẏ, ż equations) is confirmed by the researcher.** Everything else in this note about S4 is conditional on those equations.

## 1. Exact definitions and derived units

### 1.1 S4: Hindmarsh–Rose in the Dysts parameterisation (`HindmarshRose`; Marhl & Perc 2005 as cited by Dysts)

**Equations.** The researcher note quotes only ẋ = −x + y/t_x − a x³/t_x + b x²/t_x + z/t_x "etc." The other two I wrote from memory of `dysts/flows.py`: **ẏ = −a x³ − (d − b) x² + z; ż = (−s x − z + c)/t_z. UNVERIFIED.** Two consistency checks support them: the orbit is chaotic with the slow–fast structure Dysts describes (λ₁ = 0.217 against Dysts' 0.262, a 21% gap of the kind the researcher documents for every Dysts spectrum field), and the x mean and standard deviation (0.010, 0.306) match the Dysts `mean`/`std` fields quoted by the researcher (0.003, 0.33) to 8% in the standard deviation. A sign or coefficient error in ẏ or ż would in general change the attractor qualitatively, so the agreement is evidence, not proof. Researcher request R-S4-1: read the `HindmarshRose._rhs` lines verbatim.

- **Spectrum (`spectra_s456.log`, 10⁶ steps at interval 0.1):** λ = (+0.21635 ± 0.00144, +0.00002 ± 0.00017, −6.363 ± 0.011); d_KY = 2.034; LT = 4.62 time units.
- **Cached value** (interval 20·max_dt = 0.05, `lyapunov_steps` = 2·10⁶ = 10⁵ time units): **0.21688316515721046**, SE 0.92% (`lyap_long_s45.log`; plan criterion ≤ 1%: met). Δ = 0.153693; substeps 62; dt = 0.002479. Note the 2.4% difference between the 10⁵-step smoke-context value (0.2118) and this one: the 10⁵-step SE is 2.5% on this system.
- **Statistics orbit** (`units_long_s456.log`): x mean 0.010, **σ_x = 0.3057**; state mean (0.010, −0.093, 0.022); standard deviations (0.306, 0.131, 0.111); covariance eigenvalues (0.0097, 0.0144, 0.0989), condition 10.2; **whitening scale** (0.098, 0.120, 0.314): one whitened unit is 0.1–0.3 natural units (the coordinates are small; nothing in the code depends on absolute scale except the V1 finite-difference step, which is scaled by `unwhiten`). The observable is skewed (1.48) and heavy-tailed (kurtosis 10.7): spikes to x ≈ 1.7 from a baseline near 0; quantiles 1/50/99% = (−0.72, 0.01, 1.40).
- **Orbit maxima of |x|:** Benettin 1.93 (with the transient from (0.1, 0.1, 0.1)); statistics orbit with burn-in 1.93; 2·10⁶ steps at Δ (3·10⁵ time units): 1.679, block maxima all 1.68 (the spike height is sharply bounded). **Bound 5 = 2.6 × the largest value seen** (the registry ratio is 2–2.2; the spike ceiling makes a false refusal implausible, and 5 keeps a margin for the transient).
- **Burst structure against the sampling (`bursts.log`, 2·10⁵ steps at Δ):** spikes (maxima above 0.84) every 59 steps = 2.0 LT (10/90% 49/111 steps); "bursts" (spike trains separated by more than 177 steps) hold a median of 58 spikes and last a median 133 LT; the quiet intervals between them last a median 6.6 LT (90% 8.1 LT) and occupy **3% of the time**. So at these parameters the system is a nearly continuous spiker with rare short quiet phases, not a slow burster with long silences; the slow variable z ranges over [−0.46, 0.26]. The AMI first minimum is 11 steps (long run; 25 on the 10⁵-step orbit), capped to **τ = 5**, so the delay window (D−1)τ = 30 steps = 1 LT spans half a spike interval; the ACF 1/e envelope time is **2 steps** (the signal decorrelates within 0.07 LT between spikes), so spacing = max(⌈5·2⌉, 30) = **30 steps = 1 LT** (as Lorenz-63's 45) and a 5-block is 5 LT. The 1-LT window therefore never straddles a quiet phase and a burst except at the 3% of states near a quiet interval; "delay window versus burst structure" is not a problem at Δ, but the 1-LT window does straddle spikes (every 2 LT), which is what makes ν and Λ̃ so broad (next item).
- **Per-state distributions** (2 000 thinned states): **ν from 0.14 to 9.6 (p1–p99; max 37; ratio 67)**: the widest observability range after S3's; **Λ̃ is bimodal**: quantiles (1/5/25/50/75/95/99%) = (−3.0, −2.5, −0.36, 1.71, 3.78, 6.09, 7.66), 32% of states below 0.3 and 53% above 1.5, with a trough at Λ̃ ≈ 0.5–1.25 in the histogram; **g_H at 1 LT median 14.4, 95th percentile 1 720** (Lorenz-63: 2.5 and 25). This is the bimodal local instability that S2 was chosen for and does not show (note 1 §1.2). 1/d_LB = 0.518 (d = 1.93).
- **Starts:** as note 1 (label `make_rng(seed, "start", "hindmarsh_rose")`).

### 1.2 S5: HyperJha (`HyperJha`; Dysts citation a web page, Meier 2003: weak provenance, researcher §B.3)

Equations quoted in full by the researcher (§B.3, §D.2). Divergence check: ∇·f = −a − 1 − c + d = −12.367; the spectrum sum below is −12.367 ± 0.002, so the field as implemented is the one integrated.

- **Spectrum (10⁶ steps at interval 0.1):** λ = (+0.35600 ± 0.00140, +0.21168 ± 0.00134, −0.00000 ± 0.00010, −12.935 ± 0.001); **λ₂/λ₁ = 0.59** (Dysts' fields say 0.39, 0.29: wrong, as expected); d_KY = 3.044; LT = 2.81. Symmetry (x, y, z, w) → (−x, −y, z, −w).
- **Cached value** (interval 0.05, 2·10⁶ steps): **0.3603046265219353**, SE 0.43%. Δ = 0.092514; substeps 38; dt = 0.002435.
- **"The Lyapunov time" with two comparable rates, and what the spec pins.** The code's convention is Δ = 1/(30 λ₁) with λ₁ the cached largest exponent, and every "LT" in a report means 1/λ₁ = 2.81. With λ₂/λ₁ = 0.59 the second unstable direction grows by e^{0.59} per LT, so a generic error doubles in volume terms faster than λ₁ says; the per-state 1-LT exponent Λ̃ (median 1.34, mean 1.56; quantiles (−0.30, 0.06, 0.63, 1.34, 2.15, 3.96, 6.08)) exceeds 1 because the observable's sensitivity picks up both directions. Nothing in the pipeline uses λ₂: the horizon law (H1c) and Λ̃ are per-state fits over 30 steps, the amplifier g_H is the full tangent map, and H_ref = 30 steps is a convention. **Pin in the spec:** λ₁ (the cached value above) as the time unit, and record λ₂ = 0.2117 ± 0.0013 and the ratio 0.59 as system constants in the note and the report row (reported, not used). The hypothesis most exposed is H1b (seed × amplifier) and H2a(ii), as for S1 (note 1 §5); S5 is the stronger test because the two rates are comparable.
- **Statistics orbit:** x mean −0.006, **σ_x = 9.656**; state mean (0, 0, 24.1, −0.13); standard deviations (9.66, 8.65, 8.13, **70.2**); covariance eigenvalues (12.8, 66.1, 137.8, 4 940), condition 385; whitening scale (3.58, 8.13, 11.74, 70.28). The fourth coordinate's range (|w| up to 339) is absorbed by the whitening: whitened quantities are unaffected, and the x-observable (symmetric, kurtosis 2.5, quantiles ±26 at 0.1/99.9%) is not the wide one. The condition number 385 of C is the largest of any system (Lorenz-63: 16); `_symmetric_root` handles it (eigenvalues ≥ 12.8).
- **Orbit maxima of |x|:** Benettin 38.1; statistics with burn-in 37.6; 2·10⁶ steps at Δ 38.08 (block maxima 35.2–37.1). **Bound 80 = 2.10 × the maximum** (the registry ratio). w reaches 339 and is not guarded (coordinate 0 only).
- **Derived units:** AMI minimum 5 → τ = 5, window 1 LT; ACF time 9 steps (0.30 LT, as Lorenz-63) → spacing 45 steps = 1.5 LT, 5-block 7.5 LT; ν median 3.02 (p1 1.28, p99 18.8, max 93); g_H at 1 LT median 4.1 (p95 54); **1/d_LB = 0.330 (d = 3.04)**: the cleanest d ≈ 3 case (S1: 0.357).
- **Starts:** label `make_rng(seed, "start", "hyper_jha")`.

### 1.3 S6: Lorenz-96 with N = 4, F = 20 (`Lorenz96`; Lorenz 1995 equation, Dysts parameters)

**What is new, plainly.** LPC.PC.1 / Methods v2 D3 excluded Lorenz-96 because at N = 8 the state dimension exceeds D − 1 = 6, so JᵀJ is singular and PLP is undefined; nothing in that argument touches N = 4, where D = 7 ≥ m + 1 = 5 (dof 3) and D > 2 d_KY = 5.5. DEC-0037 authorizes additional attractors for the extension; S6 is Lorenz-96 at a dimension the original objection does not reach, as a development system. It is not a reversal of the scope ruling for N = 8.

- **Spectrum (10⁶ steps at interval 0.1):** λ = (+1.20184 ± 0.00349, +0.00000 ± 0.00009, −1.588 ± 0.003, −3.614 ± 0.003); sum −4.000 = −N (exact for this field); **one positive exponent** (the Dysts fields' second positive exponent 0.172 is not there); d_KY = 2 + 1.202/1.588 = **2.757**; LT = 0.832. F = 20 at N = 4 is not checked against a source (researcher §B.3: Lorenz used K = 4 only at F = 15, 18).
- **Cached value** (interval 0.1, 10⁶ steps): **1.2018430962199733**, SE 0.29%. Δ = 0.027735; substeps 6; dt = 0.004623.
- **Statistics orbit:** X_1 mean 2.85, **σ_x = 6.961**; state mean (2.85, 2.87, 2.80, 2.80) (cyclic symmetry); standard deviations 6.95–7.00; covariance eigenvalues (20.9, 34.9, 68.8, 69.7), condition 3.3; whitening scale (4.57, 5.91, 8.30, 8.35). Observable quantiles 0.1/50/99.9% = (−12.8, 2.2, 18.6), skewness 0.37.
- **Orbit maxima of |x|:** on the attractor 19.4 (2·10⁶ steps, block maxima 19.1–19.3); **the transient from the fixed point (20, 20.01, 20, 20) reaches 30.5** (statistics orbit with burn-in) and 28.7 (Benettin), and the guard checks the burn-in. **Bound 60 = 2.0 × the transient maximum, 3.1 × the attractor maximum.** (A start on the attractor would allow 40; the fixed-point start is kept for its simplicity, as (1, 1, 1) is for Lorenz-63, whose transient also exceeds the attractor.)
- **Derived units:** AMI minimum 10 → τ = 5 (cap), window 1 LT; ACF time 43 steps (1.43 LT) → spacing 150 (5 LT); ν median 2.25 (p1 1.22, p99 7.7, max 10.9): the narrowest ν range of any candidate; Λ̃ quantiles (−0.49, −0.02, 0.86, 1.61, 2.55, 4.10, 5.37), 10% below 0.3; g_H at 1 LT median 5.6 (p95 56); **1/d_LB = 0.385 (d = 2.60)**.
- **Starts:** label `make_rng(seed, "start", "lorenz96_4")`.

### 1.4 S7: coupled Lorenz (`LorenzCoupled`, 6-D) — not specified

The researcher note has the class name and the Dysts parameters (β = 2.667, ε = 2.85, ρ = 28, ρ₁ = 35, ρ₂ = 1.15, σ = 10) but states "equations not read". Per the instruction, the equations are therefore **unverified and S7 is not specified**. If the researcher reads `LorenzCoupled._rhs` verbatim, the §1–§2 procedure of note 1 applies unchanged; what is known now: m = 6 gives dof = D − m = 1 (the χ² 0.999 quantile with 1 dof is 10.83; the LM is still defined), D > 2 d_KY needs d_KY < 3.5 (Dysts' 3.04 is unreliable but plausible), the robustness filter would skip D = 5, and the cost is about 3× Chua at a Lorenz-like step. Recommendation in §8(c).

### 1.5 Comparison table (same recipe as note 1 §1.4)

| Quantity | L63 | Chua (pilot) | S1 | S4 | S5 | S6 |
| --- | --- | --- | --- | --- | --- | --- |
| λ cached; SE | 0.9055; 0.15% | 0.4311 | 0.1125; 0.50% | 0.2169; 0.92% | 0.3603; 0.43% | 1.2018; 0.29% |
| positive exponents; d_KY | 1; 2.06 | 1; 2.10 | 2 (ratio 0.18); 3.01 | 1; 2.03 | **2 (ratio 0.59); 3.04** | 1; 2.76 |
| Δ; substeps | 0.0368; 4 | 0.0773; 16 | 0.2963; 30 | 0.1537; 62 | 0.0925; 38 | 0.0277; 6 |
| σ_x | 7.92 | 1.42 | 21.68 | 0.306 | 9.66 | 6.96 |
| τ (AMI → cap 5) | 5 → 5 | 5 → 5 | 6 → 5 | 11 → 5 | 5 → 5 | 10 → 5 |
| ACF time (steps); spacing | 9; 45 | 76; 150 | 228; 150 | **2; 30** | 9; 45 | 43; 150 |
| ν median (p1, p99) | 1.67 (0.72, 6.7) | — | 1.91 (1.14, 21) | **0.95 (0.14, 9.6)** | 3.02 (1.28, 18.8) | 2.25 (1.22, 7.7) |
| Λ̃ quartiles; % < 0.3 | 0.33, 0.74, 1.45; 24% | — | 0.80, 1.02, 1.76; 4% | **−0.36, 1.71, 3.78; 32% (bimodal)** | 0.63, 1.34, 2.15; 12% | 0.86, 1.61, 2.55; 10% |
| g_H at 1 LT median (p95) | 2.5 (25) | — | 2.7 (10) | **14.4 (1 720)** | 4.1 (54) | 5.6 (56) |
| 1/d_LB; d | 0.487; 2.05 | 0.503; 1.99 | 0.357; 2.80 | 0.518; 1.93 | 0.330; 3.04 | 0.385; 2.60 |

## 2. Time conventions, RK4 step and cost

- **30 steps per LT kept** for all three (λ₁ > 0, finite). `lyapunov_steps` as in §0; the SEs meet the plan's ≤ 1% criterion (S4 at 0.92% is the closest; 4·10⁶ would give 0.65% at 25 s).
- **RK4 step and V6** (`integrator_s456.log`: 20 attractor states, 30 steps of Δ, the code's statistic; gate < 10⁻³; formal order 4; and the code's own `check_integrator` on real smoke-size contexts, `gate_checks_s45_fine.log`, `gate_checks_s456.log`):

| System | max_dt | substeps | V6 (20 states) | V6 by the code's check | observed order p | Richardson error at h/2 (σ_x) |
| --- | --- | --- | --- | --- | --- | --- |
| S4 | 0.01 | 16 | 4.9·10⁻³ FAIL | — | 3.86 | 2.5·10⁻⁵ |
| S4 | 0.005 | 31 | 3.4·10⁻⁴ (2.9× margin) | 4.2·10⁻⁵ | 4.03 | 1.4·10⁻⁶ |
| S4 | **0.0025** | **62** | **2.1·10⁻⁵** | **3.4·10⁻⁶** | 3.97 | 9·10⁻⁸ |
| S5 | 0.01 | 10 | 4.9·10⁻³ FAIL | — | 3.17 | 6.8·10⁻⁵ |
| S5 | 0.005 | 19 | 5.4·10⁻⁴ (1.8× margin) | 5.1·10⁻⁵ | 3.79 | 3.0·10⁻⁶ |
| S5 | **0.0025** | **38** | **3.9·10⁻⁵** | **7.0·10⁻⁶** | 3.83 | 2.1·10⁻⁷ |
| S6 | 0.01 | 3 | 7.5·10⁻⁵ | — | 3.74 | 4.6·10⁻⁷ |
| S6 | **0.005** | **6** | **5.6·10⁻⁶** | **6.2·10⁻⁶** | 3.84 | 2.9·10⁻⁸ |

  Orders 3.7–4.0 at the chosen steps (S5 at 0.02→0.01 gives 1.2: not yet asymptotic there, which is why 0.01 fails). S4: t_x = 0.03 is resolved by dt = 0.0025 (12 substeps per fast time constant); at 0.005 the margin on my 20 states is only 2.9×, and the run's V6 uses 20 test states that may include faster spikes, so 0.0025 is fixed (margin 48×, 290× by the code's check). S5: 0.0025 (margin 26×; 0.005 leaves 1.8×). S6: 0.005 (margin 180×; 0.01 would pass with 13× at half the cost, but 6 substeps already make S6 the cheapest system).
- **Cost relative to Chua** (16 substeps × m = 3 = 48 substep-dimensions; Jacobian paths scale as substeps × m²): **S4 62 × 3 = 186 → 3.9×** (the most expensive system of the program); **S5 38 × 4 = 152 → 3.2× (≈ 4.2× on the Jacobian paths)**; **S6 6 × 4 = 24 → 0.5×** (about Lorenz-63's cost). For the batch estimate see §8(a).

## 3. Embedding, estimator and library

- **τ, D, window:** τ = 5 for all three (S4's AMI minimum 11 and S6's 10 are capped; S5's is 5 uncapped); D = 7; window 1 LT.
- **dof condition:** S4 dof = 4 (χ² reference 18.47, as the frozen systems); S5 and S6 dof = 3 (16.27), automatic in the code (note 1 §3). `robustness_dimensions` keeps (5, 10) for every candidate (not run).
- **Embedding:** S5 d_KY = 3.04 → D > 2 d_box needs d_box < 3.5 (unverified; ν finite on all 2 000 sampled states, max 93); S6 d_KY = 2.76 → 7 > 5.5 with margin; S4 d_KY = 2.03. The delay-map Jacobian is full rank wherever ν is finite: S4's ν minimum 0.14 (a very well-observed spike state) and maximum 37 are both finite.
- **Estimator width rule, library sizes, noise levels, thresholds:** unchanged (note 1 §3). S4's σ_x = 0.306 makes ρ = 1% a noise of 0.003 natural units; the thresholds θ σ_x are 0.03–0.15 natural units against spikes of 1.7: the horizon statistics will be set by spike-timing errors, as for S3's spikes, but here the spikes are the signal (99% quantile 1.40 against a baseline of ±0.3), not a rare event.
- **Thinning and effective sample size:** S4 spacing 30 steps = 1 LT with an ACF time of 2 steps (states 15 ACF times apart: the most independent sample of any system); S5 spacing 45 at ACF 9 (5 ACF times, as Lorenz-63); S6 spacing 150 at ACF 43 (3.5 ACF times). Trajectory lengths (full preset): S4 main 170 831 steps (as Lorenz-63's layout at spacing 30: shorter), S5 230 831 (spacing 45), S6 701 831 (spacing 150).
- **Clipping at 10 σ_x:** S4 spikes reach 5.5 σ_x, S5 |x| reaches 3.9 σ_x, S6 2.7 σ_x: no clip expected from the dynamics; the counters will show any.

## 4. Expected behaviour of the gate V1–V7 (tolerances as written; none changed)

The code's own V1, V2 and V6 ran on real smoke-size contexts of all three (specs registered in-process only), and the damped-LM efficiency probe of note 1 §4 ran at the four noise levels (40 states × 50 draws, started from the true window-start state: optimistic for the pipeline).

| Check | Gate | S4 | S5 | S6 |
| --- | --- | --- | --- | --- |
| V1 Jacobians vs finite differences | both < 10⁻⁴ | **pass measured, at risk:** delay-map 3.2·10⁻⁶, **gain 5.8·10⁻⁵ (2× margin)** at max_dt 0.0025 (6.0·10⁻⁷ / 2.4·10⁻⁶ at 0.005). The gain check differences a 30-step map whose gain reaches 1 700 with h = 10⁻⁶ whitened; the FD error grows with the gain and the curvature of the spikes. A different seed's 10 test states can exceed 10⁻⁴: a V1 failure on S4 would be a finite-difference-resolution effect, not a Jacobian defect, and would still mark S4 PROVISIONAL by rule | pass measured: 8.5·10⁻⁹, 1.9·10⁻⁹ | pass measured: 9.0·10⁻¹⁰, 7.1·10⁻¹⁰ |
| V2 Cramér–Rao at ρ = 10⁻⁴ | median ∈ [0.8, 1.2] | pass measured: 1.022 (0.91–1.09) | pass measured: 0.987 (0.92–1.21) | pass measured: 1.026 (0.96–1.05) |
| V3 CP valid time | report | report; spike timing | report | report; expect short (d ≈ 2.6, fast) |
| V4 w* converged at M = 200 | median half-width ≤ 0.05 | **at risk:** between spikes x ≈ 0 ± 0.3 and both forecasters are near-exact in σ_x units at short H; c = E[(e_C − e_P)²] small at those states (`curvature_floor` counts); w* half-widths may exceed 0.05 | pass expected | pass expected |
| V5 KM fixture | < 0.01 | pass | pass | pass |
| V6 step halving | < 10⁻³ σ_x | pass measured: 3.4·10⁻⁶ | pass measured: 7.0·10⁻⁶ | pass measured: 6.2·10⁻⁶ |
| V7 efficiency (median ratio at every ρ; median slope) ∈ [0.9, 1.1] | both | **at risk:** LM probe medians 0.962 / 0.958 / 0.954 / 0.941 at max_dt 0.005 (ρ = 0.5 / 1 / 2 / 5%), 0.985 at 5% at 0.0025; p10 falls to 0.68 at 5% (15 of 40 states below 0.9). Ratios below 1 at states with tiny ν (spike states) mean the first-order CR floor over-predicts the error where the window is strongly nonlinear; the median stays inside, barely | pass expected: 0.986 / 0.980 / 0.990 / 0.999 (0.961 at 5% at 0.0025); 22 of 2 000 draws far at 5% | pass expected: 0.980 / 0.981 / 0.984 / 0.995; no far draws |

**Failure rule** as in note 1 §4: PROVISIONAL, shown, referred, never repaired. S4 carries three gate risks (V1 resolution, V4 curvature, V7 median near the edge); each would be a finding about spiking dynamics under this gate's first-order criteria, pre-stated here. S5 and S6 are expected to pass.

## 5. Pre-specified exploratory analysis (same estimands, rules, levels, block length and labels as note 1 §5; DEV-3; per-system verdicts only; no overall verdict)

| Hypothesis | S4 | S5 | S6 |
| --- | --- | --- | --- |
| H1a (±25% of 1/d_LB) | decidable (≈ 0.52) | decidable (≈ 0.33, band ±0.08) | decidable (≈ 0.385) |
| H1b (PLP slope ∈ [0.8, 1.2]) | decidable; the x-range of the fit is the widest anywhere (g_H 0.17–1 720): the pre-specified counterexample is an interval outside the band read as "the linear regime fails inside spikes" | decidable; **the sharpest test of the seed × amplifier law with two comparable rates**; counterexample reading as S1 (note 1 §5 item 3) | decidable; control: m = 4 with one exponent (if S1/S5 fail and S6 passes, the two-rate reading stands; if all three fail, it is m = 4, not the rates) |
| H1c (horizon law) | **structurally weak:** T(θ) on ln θ is set by spike timing; expect inconclusive or fail with the reading "P1-5 envelope fails" | decidable | decidable |
| H1d (Spearman ≥ 0.7) | decidable; δ̂ strongest (ν spans 67×) | decidable | decidable |
| Q-N | reachable; logit part may be thin (w* = 0 common where PLP is exact) | reachable | reachable |
| H2a (i) range < 0.1; (ii) partial r ∈ (−0.1, 0.1) | (i) decidable; (ii) refutable only; predicted: **large |r|** (bimodal Λ̃ enters the weight through anisotropic seeds across spikes) | (i) decidable; (ii) refutable only; predicted |r| larger than on the three (two comparable directions) | (i) decidable; (ii) refutable only |
| H2b | decidable | decidable | decidable |
| H2c (A4 − A2, A4 − best single < 0) | **can pass**: ν varies 67× and Λ̃ is bimodal, so state-dependent allocation has something to gain; readings as note 1 §5 item 7 | likely inconclusive | likely inconclusive |
| H2d | undetermined | undetermined | undetermined |
| H2e | decidable | decidable | decidable |
| H3a | inconclusive-prone | inconclusive-prone | inconclusive-prone |
| H3b (weight-tree Λ̃ < 0.2; horizon-tree Λ̃ largest) | **the target claim for S4** (bimodal instability): horizon-tree Λ̃ largest and weight-tree Λ̃ < 0.2 = "instability sets the horizon, not the weight" holds across spikes; weight-tree Λ̃ ≥ 0.2 = the pre-registered "seed anisotropy" reading with the spike/quiet split as its mechanism | decidable; predicted: horizon-tree Λ̃ importance lower than on the three (two rates) | decidable |
| H3c (A5/A4 ≤ 1.05) | decidable | decidable | decidable |
| gain-bound screen | report; expect the lowest within-bound fraction (envelope hypothesis fails inside spikes) | report | report |

Additional reading rules (fixed now, in addition to note 1 §5 items 1, 8, 9): (10) S4 with any gate failure: PROVISIONAL; its H3b and H2c readings are shown with the label and quoted only as "what the gated machinery would say". (11) S5 versus S1: if H1b fails on S5 and passes on S1, the seed × amplifier law tolerates a weak second rate (0.18) but not a comparable one (0.59); if both fail with S6 passing, two rates break it at any ratio; if S6 also fails, the reading is m = 4 (the embedding at D = 7), not the rates. (12) S6 H1a at 1/d_LB ≈ 0.385: the first system between d ≈ 2 and d ≈ 3; pass extends the N_lib^{−2/d} law continuously; fail below the band reads as the Rössler/Chua shortfall.

## 6. Regression requirement

As note 1 §6, unchanged: additive entries; the WU-0021.3 reference (smoke, DEV-0, `--systems lorenz63 rossler chua`, CPU, `LPC_THREADS=1`) compared with `tools/leafdiff.py` and `tools/compare_runs.py` at tier T0 on the same host; the three registry-pinning tests updated by design to the full set of names (and `spec.dim == 3` replaced by the per-spec value); `LYAPUNOV_REFERENCES` keys for S4, S5, S6 (empty lists; no published λ for any of the three: Dysts' fields are not references). Reference-value tests as note 1 §6.7 for each new spec, with the §0 cached values, the V6 statistics above, and the guard checks (A5). One addition: a unit test that the S5 field's divergence equals −a − 1 − c + d (an exact identity that pins the equations as transcribed; the same for S6: trace = −N) and, for S4 once R-S4-1 is confirmed, that the transcribed `_rhs` lines match the field function term by term (typed into the test from the researcher's verbatim quote).

## 7. Risks and open questions for the owner, with recommendations

- **R-S4-1. S4's ẏ, ż equations are from memory (unverified).** Do not implement S4 until the researcher quotes `HindmarshRose._rhs` verbatim. If it differs, every S4 number here is void and the §1–§2 procedure is rerun (one hour of single-thread work). **Recommend: researcher request now; S4 implementation gated on it.**
- **R-S4-2. S4's gate risks** (V1 gain 2× margin, V4 curvature, V7 median 0.94–0.99): pre-stated; a failure is PROVISIONAL by rule and is the finding "spiking dynamics leave the first-order regime of the gate". **Recommend running S4 anyway** (it is the only candidate with a bimodal Λ̃ and a 67× ν range, the two features the program is looking for).
- **R-S5-1. Provenance:** HyperJha's Dysts citation is a web page; the equations are as Dysts implements them (confirmed by the researcher's quote and the divergence identity). It is a Lorenz-family hyperchaotic system with no primary paper named; label it "Dysts `HyperJha`" in every table. **Recommend keeping it: the cleanest d ≈ 3, two-comparable-rates case, gate expected to pass, 3.2× Chua.**
- **R-S6-1. S6 is not what the Dysts fields promised:** one positive exponent, d_KY 2.76, not 3.17 with two. Its role becomes the m = 4, single-exponent control for S1/S5 (§5 item 11) at half of Chua's cost. **Recommend keeping it as the cheapest member, lowest priority.**
- **R-S7-1. S7 cannot be specified** (equations not read). **Recommend dropping S7 from this round**; if the researcher reads the equations, it is a S-size follow-up.
- **R-ALL-1. Orbit bounds** S4 5, S5 80, S6 60 (S6's covers the fixed-point transient); a refusal names the step and stops the invocation (and, in a batch, the systems after it: §8(a)); bounds may be raised only by a recorded decision before a fresh run.
- **R-ALL-2.** The statistics-orbit lengths and all derived units were computed at the specified cached λ for S4–S6 (`units_long_s456.log`); the gate checks ran at the 10⁵-step smoke-context λ (2.4% off for S4, 1.9% for S5), which cannot change a pass/fail at these margins except V1 on S4, which is already flagged.

## 8. Batching, CPU parallelism, and what to drop

**(a) One batched invocation on the GPU (DEV-3, `--systems <list> --skip-robustness`).** The study loop runs the listed systems **serially** in one process (`__main__`: `for system in config.core_systems: run_system(...)`, then `save_json` after each system), so batching saves only the start-up, the lock and the human turnaround, not compute; and `results["handling"]`, `verdicts`, `provenance.finish`, `RESULTS.md` and the figures are written only after the last system. **An exception in system k (an orbit-guard refusal, a non-finite state, a V-check error) ends the invocation: systems 1…k−1 keep their per-system blocks in `results.json` (saved after each), systems k+1… are never run, and the verdict and handling blocks are missing.** Order the list by refusal risk ascending and value, and run a per-system smoke first (plumbing and guard) as WU-0021.5 already requires:

| Order | System | Cost (Chua = 1) | Why here |
| --- | --- | --- | --- |
| 1 | S3 `rossler_z` | 0.75 | bound 50 at ratio 2.2 on a tightly bounded orbit; cheap |
| 2 | S6 `lorenz96_4` | 0.5 | cheap; bound covers the transient 2× |
| 3 | S2 `lorenz63_r166` | 1.7 | analytic bound: no refusal possible |
| 4 | S5 `hyper_jha` | 3.2–4.2 | highest value per hour; bound at the registry ratio |
| 5 | S1 `rossler_hyper` | 2.5–3.3 | empirical bound with rare excursions (1.7× the largest seen) |
| 6 | S4 `hindmarsh_rose` | 3.9 | most expensive; three gate risks; implementation gated on R-S4-1 |

  Total ≈ 12.5–14 Chua-equivalents with note 1's S1 step; **with the re-specified S1 step (§11: 5× Chua) the total is ≈ 15–17 Chua-equivalents** and S1 moves to last with S4. Converting with the plan's own figure (WU-0021.8: 1–1.5 h GPU wall clock for a full run of one new system at about 2× Chua, i.e. about 0.5–0.75 h per Chua-equivalent, which is an extrapolation and not a measurement), **one batched full run of all six on DEV-3 is about 6.5–10 h of GPU wall clock**, S4 and S5 taking 2–3 h each; the plan's "pilot folded into the full run" means no separate pilot. If the GPU window is shorter, split into two invocations: {S3, S6, S2, S5} (≈ 3–4.5 h) and {S1, S4} (≈ 3–5 h), the second only after S4's equations are confirmed. If S4 is dropped the batch is 8.6–10 Chua-equivalents.

**(b) CPU in parallel.** Running CPU jobs beside the GPU job does not change the GPU job's bits (fixed thread counts; DEC-0037 item 4), but the GPU run's host-side parts (the k-d tree queries at `worker_count()` = `LPC_THREADS` threads, the bootstrap, the sklearn trees) compete for cores and lengthen its wall clock. Until run-2 ends this evening the CPU is taken (8 threads) and nothing more should start (one niced thread for scratch work only, as here). After run-2: the cheap systems S3, S6 and S2 (≈ 3 Chua-equivalents together; on the CPU a full preset of three frozen systems took about 4.7 h in the pilot era, so about 5 h at 8 threads for these three) can run on the CPU at `LPC_THREADS=8` as the plan's TD cross-device check, leaving the GPU to S5, S1, S4, **provided the host has at least 8 + the GPU job's `LPC_THREADS` cores free**; otherwise run the CPU job at a lower thread count (its bits depend on the thread count, so record it) or not at all. The CPU result never replaces the GPU result (plan), and a CPU run of the same system on the same seed is the TD-tier comparison of `compare_runs.py`, not a regression.

**(c) Drop or demote.** **Drop S7** (not specifiable now). **Demote S6** to the last optional slot (it adds a control, not a new regime). **Gate S4** on the equation check; if the researcher cannot confirm `_rhs` by the time the batch is assembled, run the batch without S4 rather than with unverified equations. Keep S5 at full priority. Among note 1's systems, keep S2 as the reference the owner asked for, and S3 as recommended there.

## 9. Scripts and logs added (same directory as note 1)

| Script / log | Content |
| --- | --- |
| `ext_common.py` (extended) | S4, S5, S6 candidate specs; `run.sh` takes `ARGS` |
| `spectra_s456.log` | spectra, d_KY, 10⁵-step cache values, per-coordinate maxima (max_dt 0.005 for all three) |
| `lyap_long_s456.log`, `lyap_long_s45.log` | cached λ at 10⁶ steps (max_dt 0.005) and at the specified steps and max_dt 0.0025 (S4, S5) |
| `integrator_s456.log` | V6 grid, orders, Richardson errors |
| `bound_tail_s456.log`, `bound_tail_s5.log` | |x| tails; S5 at bound 80 |
| `units_s456.log`, `units_long_s456.log` | derived units at the 10⁵-step and the specified λ |
| `bursts.py`, `bursts.log` | S4 spike and burst statistics against Δ and the window |
| `gate_checks_s456.log`, `gate_checks_s45_fine.log` | the code's V1, V2, V6 and the LM probe (max_dt 0.005; then 0.0025 for S4, S5) |

## 10. What I could not verify

- S4's ẏ and ż (R-S4-1); the Dysts `HindmarshRose` initial conditions and any published λ for this parameterisation (Marhl & Perc 2005 not read); F = 20 at N = 4 against a source; the primary source of HyperJha; d_box for S5; S7's equations.
- The pipeline's V4 and V7 on S4 (the probe is from the true start; the network-started LM is untested); the GPU wall-clock conversion in §8(a) (an extrapolation from the plan's figure).

## Summary (≤ 200 words)

S4 Hindmarsh–Rose (Dysts parameters; ẏ, ż from memory, **unverified: implementation gated on the researcher's verbatim `_rhs`**): λ = 0.2169 (SE 0.9%), d_KY 2.03, max_dt 0.0025 (62 substeps, t_x resolved), bound 5, spacing 30; a near-continuous spiker (quiet phases 3% of the time) with a **bimodal Λ̃** (32% below 0.3, 53% above 1.5), g_H p95 = 1 720 and ν spanning 67×: the features S2 lacks; gate risks V1 (2× margin), V4, V7; 3.9× Chua. S5 HyperJha: λ = (0.3603, 0.2117, 0, −12.94), **ratio 0.59**, d_KY 3.04, 1/d_LB 0.330; max_dt 0.0025 (38 substeps), bound 80; the time unit is pinned to λ₁ with λ₂ recorded; gate expected to pass; 3.2–4.2× Chua; highest value. S6 Lorenz-96 N = 4, F = 20: **one** positive exponent (Dysts' two is wrong), λ = 1.2018, d_KY 2.76; max_dt 0.005 (6 substeps), bound 60 (transient); the m = 4 single-exponent control; 0.5× Chua. S7 not specified (equations not read). The code's own V1/V2/V6 pass on all three. Batch: serial within one invocation, an exception ends it, order S3, S6, S2, S5, S1, S4; ≈ 12.5–14 Chua-equivalents, about 6.5–10 h GPU (extrapolated). CPU after run-2: S3, S6, S2 at 8 threads if cores remain. Drop S7; demote S6; gate S4.

## 11. S1 re-specification (review WU-0021.7 R1): RK4 stability at the attractor's |x| ceiling, step, bound, cached λ

**Finding accepted.** The reviewer's diagnosis is reproduced here (`s1_restab.log`, `stability_margins.log`): the 7 non-finite orbits of the S-D1 test were RK4 instability at the production step, not a dynamical escape, and the bound 300 of note 1 lay inside the attractor's reach. My note 1 §1.1 tail study (one 4·10⁶-step orbit, max |x| 174) was too short by a factor of about 20 to see the excursions (their rate is about 1 per 1.6·10⁵ time units); the reviewer's 400 × 7·10⁵-step runs and the 64 × 7·10⁵-step batch below (13.3·10⁶ time units) do.

- **Mechanism (stated).** In S1, ż = b + x z gives ∂ż/∂z = x. At the excursion states the Jacobian is J = [[0, −1, −1, 0], [1, a, 0, 1], [z, 0, x, 0], [0, 0, −c, d]] with eigenvalues {x, 0.12 ± 0.99i, 0.05} (measured at the recorded minimum-x states: real parts (−303.3, 0.12, 0.12, 0.05)); the stiff mode is x itself, the other three modes are the slow physical ones (the w-equation's d = 0.05 and the x–y rotation), and z ≈ 0.01, w ≈ 130 there. RK4's stability polynomial R(hλ) = Σ_{k≤4} (hλ)^k/k! has |R| ≤ 1 on the negative real axis only for |hλ| ≤ 2.785, so the integrator is stable at a state only if **h |x| < 2.785**. At the old step h = 0.009875 the limit is |x| < 282; the attractor reaches |x| = 303–304 (next item); the frozen-coefficient spectral radius ρ(R(hJ)) at the recorded states is 1.19–1.37 at the old step (unstable; growth by that factor per substep over the ~0.5 time units the excursion spends below −282, which is 100 substeps: enough to blow up) and 1.0006 at h = 0.004951 and 1.0005 at h = 0.00395 (the 0.0005 is the physical growth e^{0.12 h} of the unstable mode, not instability).
- **The |x| ceiling (tail at a stable step).** 64 attractor starts, 7·10⁵ steps each at max_dt 0.005 (h = 0.004946): 0 non-finite; per-orbit maxima sorted: 303.3, 302.1, 301.4, 300.7, 294.3, 293.6, 284.8, 181.4, 176.9, …; 7 of 64 orbits above 200, 4 above 300, **0 above 304**; 324 steps of 4.5·10⁷ above 200 and 4 above 300. The reviewer's 400 orbits at h/2 and h/4 give max 303.45 and 303.74 with the 99th percentile of the per-orbit maximum at 302.8. The excursion is one recurring type (x ≈ −300, w ≈ 130, z ≈ 0.01) with a sharp peak at 303–304 converged in h; nothing in 464 orbit-runs (about 9.7·10⁷ time units in total) exceeded 304.
- **Bound: 460 = 1.5 × 304, rounded up to the nearest 10** (the plan's rule). There is no trapping region for this field, so the bound is not a theorem: it is a loud check that stops the run and names the step and the maximum (DEF-0015). What it means: at a stable step a refusal can only be a new excursion type beyond anything seen in 10⁸ time units, which would itself be a finding (reported, never repaired by raising the bound during a run). A non-finite value is impossible below |x| = 563 at the new step (next item), so a non-finite refusal would be a code defect.
- **Step: max_dt = 0.005, so h = Δ/60 = 0.004951; stable for |x| < 2.785/h = 563: safety factor 1.85 at the ceiling (h·304 = 1.50) and 1.22 at the bound (h·460 = 2.28).** The guard therefore refuses an orbit before the integrator can become unstable (460 < 563): stability holds everywhere the guard admits. On the typical orbit (2·10⁵ steps sampled every 5) the stiffest decaying eigenvalue is 169 (|x| at the typical maximum) with max |R| = 1.0000 and margin 3.3. The alternative max_dt = 0.004 (75 substeps, stable to 705, safety 2.3 at the ceiling) costs 25% more; not needed, since nothing admitted by the guard is within 20% of the limit. The z spikes themselves are not stiff (z ≈ 0.01 at the excursion; ∂ż/∂x = z is tiny); the fourth coordinate's own eigenvalue d = 0.05 is slow; neither adds to the stiff mode.
- **Δ, substeps, V6, order.** `lyapunov_steps` = 2·10⁶ at interval 20·max_dt = 0.1 (2·10⁵ time units; the guard at 460 passed; max |x| 166.3 on that orbit): **cached λ = 0.11220508610149857, SE 0.47%** (`lyap_long_s1_005.log`; the step change moves λ by −0.3% from the note 1 value at max_dt 0.01, within the SEs). **Δ = 0.297075; substeps 60; h = 0.004951.** V6 at max_dt 0.005: 7.4·10⁻⁸ on my 20 states (`integrator.log`), **3.4·10⁻⁷ by the code's own `check_integrator`** on a real context (`gate_checks_s1_005.log`); observed order 3.92 (h, h/2, h/4), Richardson error at h/2 3·10⁻¹⁰ σ_x. V1 9.1·10⁻⁹ / 3.9·10⁻⁹; V2 0.971 (0.89–1.12); LM probe median 0.997 at ρ = 5% (30 of 2 000 draws far). All gate predictions of note 1 §4 for S1 stand.
- **Derived units at the new step** (`units_long_s1_005.log`): σ_x = 21.58; state mean (−24.83, −2.55, 2.55, 25.47); AMI 6 → τ = 5; ACF 205 steps → spacing 150; ν median 1.92 (p1 1.20, p99 16.5); Λ̃ quartiles (0.82, 1.08, 1.80); 1/d_LB = 0.355 (d = 2.82). Statistics-orbit maximum with burn-in 146.1.
- **Cost:** 60 substeps × m = 4 = 240 substep-dimensions → **5× Chua** (about 6.7× on the Jacobian paths), up from the 2.5× of note 1; S1 becomes the most expensive system of the program with S4. Batch estimate in §8(a): total ≈ 15–17 Chua-equivalents for six systems, about 8–12 h GPU by the plan's conversion.
- **Revised S-D1 expectation (criterion unchanged: 0 refusals of 400 starts over burn + 705 000 steps).** At the new step no non-finite is possible below 563, and no orbit of the 464 examined (about 9.7·10⁷ time units) exceeded 304, so **the expected count is 0 of 400**. The honest rate: with 0 exceedances of 304 in 464 orbit-runs of the test's length, the 95% upper bound on the per-orbit probability of exceeding 304 is about 0.65% (rule of three), i.e. the test could still see up to 2–3 refusals at the 95% level only if the tail continues above 304, which the clustering at 300.7–303.7 argues against; an exceedance of 460 needs a different excursion type. If a refusal occurs, it is reported as a result (Ruling 2) and the mechanism is read from the recorded maximum: a maximum between 304 and 460 cannot happen (the guard admits it); a maximum at 460 with finite state is a new excursion; a non-finite state is a defect.
- **For the developer (S1 only):** `max_dt = 0.005`, `orbit_bound = 460.0`, `lyapunov_steps = 2_000_000`, expected cached λ 0.11220508610149857 (this host; the A6 regression-guard label of review R3 applies). Then rerun A3, A4, A6, R11, S-D1 and A7 for S1 as the review requires. S2 and S3 are unchanged.

### 11.1 Can the same mechanism bite S2–S7? Stability margins at the proposed steps

The mechanism needs a Jacobian eigenvalue whose magnitude grows with the state (a diagonal term proportional to a coordinate, as x z in ż) **and** an attractor that visits states where h·|λ| approaches 2.785. Measured along 2·10⁵-step orbits at Δ (40 000 sampled states; `stability_margins.log`), with max_i |R(h λ_i)| over the decaying modes and the real-axis margin 2.785/(h·max|Re λ|):

| System | h | stiff eigenvalue: form, measured max |Re λ| | max |R(hλ)| decaying | margin | can an excursion close it? |
| --- | --- | --- | --- | --- | --- |
| S1 (new step) | 0.00495 | ∂ż/∂z = x; 169 typical, **304 at the ceiling**, 460 at the bound | 1.0000 | 3.3 typical, **1.85 at the ceiling, 1.22 at the bound** | the guard refuses before the limit (460 < 563) |
| S2 Lorenz r = 166.1 | 0.00199 | the Lorenz Jacobian's eigenvalues scale with √(σ|r − z|) and |x|, |y|; 40.6 (|λ| 59) | 1.0000 | 34 | no: the trapping ball bounds every coordinate (z ≤ 358, |x| ≤ 182, |y| ≤ 182), so |λ| stays below about 100: margin ≥ 14 everywhere admitted |
| S3 Rössler-z | 0.0385 | ∂ż/∂z = x − c ∈ [−16.9, 5.7]; 14.8 | 1.0000 | 4.9 | no: |x| ≤ 11.4 on every orbit seen (registry system, registry step) |
| S4 Hindmarsh–Rose | 0.0025 | ∂ẋ/∂x = −1 + (2b x − 3a x²)/t_x: −80 at x = −0.76, −29 at the spike peak 1.68 | 1.0000 | 14 | the eigenvalue grows like x²/t_x, so |x| would have to reach about 3× the sharply bounded spike ceiling (block maxima all 1.68): no |
| S5 HyperJha | 0.00245 | the x z and x y terms are off-diagonal (diagonal constant: −a, −1, −c, d); eigenvalues scale with the state, 22 (|λ| 39, complex) | 1.0000 | 51 | the orbit maximum is tight (block maxima 35–37 against 38); an excursion to about 7× the typical state would be needed: none in 2·10⁶ steps |
| S6 Lorenz-96 N = 4 | 0.00459 | entries are the X_k themselves; 8.8 (|λ| 27) | 1.0000 | 69 | no: block maxima 19.1–19.3; the transient from the fixed point (30.5) is also far inside |
| S7 (not specified) | — | Lorenz-type: would behave as S2 | — | — | assess when specified |

Rule for every future spec (added to the §1–§2 procedure of note 1): compute the frozen-coefficient margin along the orbit **and at the recorded extreme states of a multi-orbit tail study of at least 10⁸ time units at a step already known to be stable**, and choose max_dt so that the integrator is stable up to the orbit bound itself, not only on the typical orbit. S1 is the only candidate whose stiff eigenvalue is a bare coordinate with heavy excursions; the others have margins of 5–69 with tightly bounded orbits.

