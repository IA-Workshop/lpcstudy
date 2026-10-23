# Mathematics note: mapping between the Dysts forecasting benchmark and this study (WU-0024.2; draft input to WU-0024.3)

**DEVELOPMENT (DEV-1, DEV-3, DEV-4): not a hypothesis test · UNPROMOTED · descriptive only.**

- **Author:** applied-mathematician (claude-opus-5-5), 2026-10-23, worktree `wu/benchmark-map` (branch from develop b34859b).
- **Scope.**
  - This note makes no ranking claim, and no claim about one forecaster or one study against another.
  - It gives no overall verdict for the extension systems. Their stored overall word is `per-system only` (DEC-0038).
  - No sealed number appears here, and none may be set beside these values. Nothing under the sealed run was read.
  - No new run and no new statistic. Every study number is a stored leaf. The only computations are the stated unit conversions in §2.3, each with its formula.
- **Inputs.**
  - `docs/agent/notes/2026-10-23-researcher-dysts-tables.md` ("R23"): benchmark definitions and status words.
  - `docs/agent/notes/2026-10-20-researcher-dysts-extension.md` §C ("R20"): carried-over items.
  - `docs/agent/notes/2026-10-23-extension-ensemble-summary.md`: run paths and gate words.
  - The code at b34859b: `lpcstudy/`. The V3 code is identical at the run commits 3dec086, 974519a and 392a069 (checked with `git show`, §1).
- **Status words** follow R23:
  - **confirmed** means seen in text fetched on 2026-10-23;
  - **not confirmed** means carried over or not found.

  A benchmark item that R23 lists as unconfirmed stays marked unconfirmed here.

## 0. Assumptions

- **A1.** The study conventions:
  - time is counted in observation steps;
  - 1 LT = 30 steps, with LT = 1/λ_max and λ_max the code's own RK4 Benettin estimate, stored at `systems/<s>/context/lambda_max`;
  - the interval is Δ = 1/(30 λ_max), checked equal to the stored `context/interval` to all digits (§2.3);
  - the observable is normalized, (x − mean)/σ_x (`lpcstudy/data.py` line 549);
  - ρ is a fraction of σ_x;
  - hidden states are whitened.
- **A2.** Gilpin 2023 = arXiv:2303.08011. The journal reference *Phys. Rev. Res.* 5, 043252 is **not confirmed** (R23 D.7). "ZG25" = Zhang and Gilpin, arXiv:2409.15771. "ZG26" = Zhang and Gilpin, arXiv:2505.11349 (ICLR 2026).
- **A3.** Identifications that are inferences, not statements:
  - (i) the Gilpin 2023 t_peak is the Dysts JSON `period` field. R23 A.4 quotes the README: "The `period` field contains the timescale associated with the dominant frequency". Gilpin 2023 App. B says "dominant significant Fourier timescale t_peak". They have the same wording, but no text links the two. **Not confirmed.**
  - (ii) The λ in ZG25/ZG26 "30 points per Lyapunov time" is the Dysts `maximum_lyapunov_estimated` field. **Not confirmed** (R23 D.2).
  - (iii) Which λ_max Gilpin 2023 uses for its λ_max t unit. **Not confirmed** (not in pp.1–12 read).

  Every conversion that uses one of these is labeled CONDITIONAL.

## 1. The study quantity, from the code

V3 is the CP valid-prediction time of v3 §6 E0: "CP's valid prediction time is reported, for comparison with Zhang & Gilpin (2026)".

The code path (b34859b; identical at the three run commits):

- `lpcstudy/experiments.py::_cp_horizon_check` (lines 408–440) calls `lpcstudy/validation.py::check_cp_horizon` (lines 304–360) with:
  - `theta = 0.4` (a literal, line 428);
  - `cfg.horizon_max` = 8 LT = 240 steps;
  - `cfg.steps_per_lyapunov` = 30.
- The call site (`experiments.py` lines 940–960) uses:
  - the core cell `cfg.core_noise` = 0.01 and `cfg.core_library` = 10⁴;
  - the test split (n_test = 1000);
  - **one** query-noise and **one** verification-noise draw per state (`unit_noise(..., 1, ...)`).
- The error is `err = batch.cp_err[:, 0] - setup.noise * verify_unit[:, 0]`. Here `cp_err` is CP forecast minus noise-free truth in σ_x units, clipped at ±10 (`lpcstudy/ensemble.py::clip_errors`). So `err` is the forecast minus the **noisy** verifying observation.
- `lpcstudy/oracle.py::realized_horizon` (lines 452–479) gives τ_i, the first H in 1..240 with |err_{i,H}| > 0.4, or 240 if censored.
- `lpcstudy/statistics.py::kaplan_meier(...).median()` gives the smallest H with Ŝ(H) ≤ 1/2.

The quantity is:

  **V3 = (1/30) · min{ H ∈ {1, …, 240} : Ŝ_KM(H) ≤ 1/2 }**, Ŝ_KM the Kaplan–Meier survival of τ_i over the 1000 test states.

Leaf: `systems/<s>/validation/cp_median_vpt_lyapunov`. RESULTS label: "V3 CP valid-prediction time (LT, theta=0.4)" (`lpcstudy/report.py` line 129).

Properties used below:

- **P-a (resolution).** V3 is a multiple of 1/30 LT. The stored V3 × 30 is an integer in every run (§3).
- **P-b (clip).** The ±10 clip does not move τ_i. A clipped entry has |cp_err| = 10, so |err| ≥ 10 − ρ|v| > 0.4 whenever |v| < 960, which holds for Gaussian v with probability 1 − O(e^{−460 000}).
- **P-c (noise cannot cross).** At ρ = 0.01 the verification noise alone has s.d. 0.01. The threshold 0.4 is 40 noise s.d. and 9.4 × 3√2ρ (3√2ρ = 0.0424, the v3 §6 admissibility bound). The bound holds.

**Two documentation points.**

- **(i) θ.** θ = 0.4 is in v2 (`methods_experimental_procedures_v2.md` line 303, "V3. CP valid-prediction time at θ = 0.4 (reported)"). v3 §6 V3 does not state θ. 0.4 is outside the v3 set θ ∈ {0.1, 0.2, 0.3, 0.5}, whose primary is 0.2. The appendix caption must state θ = 0.4 (finding F1, §6).
- **(ii) Verification target.** V3 is measured against the noisy verifying observation. This is the v3 §6 "Horizons" convention. The MSE quantities are measured against the noise-free truth (v3 §4 "Hybrid"). The caller's convention list ("errors against noise-free truth") therefore does not apply to V3 (finding F4).

### 1.1 Four relations between the definitions (derived; used for the comparability column)

- **L1. A running mean crosses no earlier than the pointwise curve.**
  - Let p(t) ≥ 0 be a pointwise error curve on [t*, ∞) and m(t) = (t − t*)⁻¹ ∫_{t*}^{t} p. If p < S on [t*, t₁), then m(t₁) < S.
  - Hence first-passage(m, S) ≥ first-passage(p, S) for every forecast and every threshold S. **Status: correct.** No hypothesis is needed beyond integrability of p.
  - Gilpin 2023 defines ε(t) ≡ 2/(t − t*) ∫ |y − ŷ|/(|y| + |ŷ|) dt′ (p.3, confirmed). This is a running mean. The study's τ_i is pointwise.
- **L2. "Latest time below S" is no earlier than "first time above S".**
  - Gilpin 2023 App. A uses "the latest time when SMAPE < 50" (confirmed). ZG25 uses "the first forecast horizon at which the sMAPE exceeds a fixed threshold ε" (confirmed).
  - For one curve, sup{t : c(t) < S} ≥ inf{t : c(t) > S}, with equality iff c crosses S once. **Correct.**
  - Whether the sMAPE inside ZG25's VPT is pointwise or a running mean is **not confirmed**.
- **L3. sMAPE is a state-dependent bound on the absolute error, and is not translation invariant.**
  - Pointwise sMAPE (percent) s = 200 |e| / (|y| + |ŷ|), with e = y − ŷ.
  - So s < S is equivalent to |e| < (S/200)(|y| + |ŷ|). The allowed absolute error scales with the current amplitude |y| + |ŷ|. It tends to 0 as y, ŷ → 0, and it changes when a constant is added to the series.
  - The study's criterion |e| < θσ_x is a constant bound, invariant under translation, on an observable centered at 0 by construction (A1).
  - **No map between the two thresholds exists without the joint distribution of (|y|, |ŷ|) along each forecast**, and that distribution is not stored. **Correct** (it is an identity).
  - Whether Gilpin 2023 computes sMAPE on raw or standardized coordinates is **not confirmed**.
- **L4. Converting between time units.**
  - If the benchmark's Lyapunov time uses λ_B and the study's uses λ_S, then a duration of T_S study LT equals T_S · λ_B/λ_S benchmark LT. A duration of n samples at 30 samples per benchmark LT equals (n/30) · λ_S/λ_B study LT.
  - **Correct**, under the hypothesis that both λ are per unit of the same equation time. R23 A.4 confirms this for Dysts: "`_rhs` ... carries no time factor".

## 2. Mapping table

### 2.1 Quantities

| # | Quantity | Benchmark: cited text (source, location, status) | This study: code symbol or leaf | Comparable | Reason; conversion |
|---|---|---|---|---|---|
| M1 | Systems and equations | Dysts `flows.py` `_rhs`. Lorenz: `xdot = sigma * y - sigma * x` …. Rössler: `xdot = -y - z` …. Chua: `ramp_x = m1 * x + 0.5 * (m0 - m1) * (np.abs(x + 1) - np.abs(x - 1))` … (R23 A.1, confirmed, fetch extract). Gilpin 2023: "well-known systems such as the Lorenz, Rössler, and Chua attractors" (p.2, confirmed) | `lpcstudy/systems.py::SYSTEMS` lines 339–367: `lorenz63_field`, `rossler_field`, `chua_field`; `params` | **yes** | Same vector fields. Parameters differ only by rounding: β 2.667 against 8/3; m0 −1.142857 against −1.143; m1 −0.71429 against −0.714 (relative 1.2·10⁻⁴ to 4·10⁻⁴; R23 A.1) |
| M2 | Observed coordinates | ZG26: "dimensionality three and six" (Sec. 4, confirmed). Whether the scored series is the full state or one coordinate is **not confirmed** for Gilpin 2023 and ZG26 | `SystemSpec.observed_index` = 0 (x) for all three; `h(s) = s[observed_index]` | **partly** | The study scores one scalar observable (x). Any benchmark average over coordinates is a different quantity. Not convertible |
| M3 | Time unit (which λ) | Gilpin 2023: "We report our forecast results scaled by this quantity, in units of λ_max t" (p.4, confirmed); which λ_max estimate is **not confirmed** (A3 iii). ZG26: "τ≡λ^{-1}", "Each system is annotated with its largest Lyapunov exponent" (Sec. 4, confirmed); the source of λ is **not confirmed** (A3 ii) | `StudyConfig.steps_per_lyapunov` = 30; `systems/<s>/context/lambda_max` (RK4 Benettin, `lyapunov_cached`) | **partly** | Convertible by L4 once λ_B is known. If λ_B is the Dysts max field (CONDITIONAL), the factor λ_B/λ_S is 0.9846 (Lorenz), 2.100 (Rössler) and 2.790 (Chua) (§2.3). If λ_B is the Dysts spectrum[0], it is 1.205, 1.064 and 1.045. The two Dysts fields give factors that differ by 1.97 times (Rössler) and 2.67 times (Chua), so the conversion is undetermined until λ_B is confirmed |
| M4 | Sampling interval | Gilpin 2023: "trajectories are resampled to 100 timepoints per t_peak" (App. B p.8, confirmed). ZG25: "3030 timepoints per Lyapunov time τ", read as 30 (Sec. 4, confirmed with the doubled-digit artifact); ZG26: "a fixed sampling rate of 30 points per Lyapunov time" (Sec. 4, confirmed) | `systems/<s>/context/interval` Δ = 1/(30 λ_max); `lpcstudy/data.py` line 478 | **partly** | Against ZG: the same 30 per LT, but of a different LT for Rössler and Chua (M3). Their step would be 0.03738, 0.2213 and 0.02710 against the study's 0.03681, 0.4648 and 0.07561 (CONDITIONAL, A3 ii). Against Gilpin 2023: the study has 40.8, 12.7 and 18.8 steps per t_peak (CONDITIONAL, A3 i) against 100 |
| M5 | Error metric | Gilpin 2023: "symmetric mean absolute percent error (sMAPE) ε_ik(t) ≡ 2/(t−t*) ∫ (\|y_test,k − ŷ_test,ik\|)/(\|y_test,k\| + \|ŷ_test,ik\|) dt′" (p.3, confirmed). ZG26 metrics: sMAPE, MSE, MAE … (Sec. 4, confirmed) | absolute pointwise error \|err\| in σ_x units (`validation.py::check_cp_horizon`; `oracle.py::realized_horizon`) | **no** | L3: sMAPE is a relative error with an amplitude-dependent denominator; the study's error is absolute. No conversion exists |
| M6 | Threshold | Gilpin 2023: "SMAPE < 50" (App. A p.8, confirmed). ZG25: "We set ε=30, as in prior studies" (Sec. 4 Metrics, confirmed). ZG26: definition **not present** in the text read (R23 B.2) | θ = 0.4 σ_x, a literal at `experiments.py` line 428; v2 line 303. v3 §6 does not state it (F1) | **no** | Different metrics (M5). By L3, sMAPE 30 or 50 is no fixed multiple of σ_x |
| M7 | Horizon definition | Gilpin 2023: "the latest time when SMAPE < 50", on the running mean (App. A, p.3, confirmed). ZG25: "The first forecast horizon at which the sMAPE exceeds a fixed threshold ε" (confirmed) | first passage τ_i = first H with \|err\| > θ (`realized_horizon`) | **partly** (ZG25); **no** (Gilpin 2023) | ZG25 uses the same first-passage form, on another metric. Gilpin 2023 uses "latest time" on a running mean, which is never earlier than first passage by L1 and L2. The direction of the definitional difference is known; its size is not |
| M8 | Verification target | Gilpin 2023: test data are "a trajectory generated from different initial conditions than the trajectory used for training" (p.9, confirmed). Whether the noisy or clean series is scored under ZG26 App. E noise is **not confirmed** | V3: forecast minus the **noisy** verifying observation (`err = cp_err - noise * verify_unit`); v3 §6 "Horizons" | **partly** | Both score held-out trajectories. The noisy-versus-clean target matters only at the noise level (P-c: 40 noise s.d. below θ) |
| M9 | Aggregation | Gilpin 2023: "the average valid forecast horizon of the best-performing model averaged across all 135 systems is equal to 13.9 ± 2.8 λ_max^-1" (App. A, confirmed); the meaning of ± is **not confirmed**. ZG26 Table 5: values ± (meaning not stated; average across systems, R20 C.2, **not confirmed** on 10-23) | Kaplan–Meier median over 1000 test states of one system, one noise draw each, right-censored at 8 LT (`statistics.py::kaplan_meier`, `SurvivalCurve.median`) | **no** | Median of one system against a mean over many systems. First-passage times are skewed and censored, so a median and a mean differ in general. No per-system benchmark value exists to align with (§3) |
| M10 | Forecast window and censoring | Gilpin 2023: "t ∈ [0.01–50] t_peak"; "forecasts up to an additional t = 2 t_peak after t*" (p.9, confirmed; R23 reads 2 t_peak as validation). ZG25: "the last 300 timepoints set aside to determine final test scores" (Sec. 4, confirmed); ZG26: "predict the next 300 data points, equivalent to 10 Lyapunov times" (confirmed as relayed) | `StudyConfig.horizon_max_lyapunov` = 8 LT (240 steps) | **partly** | ZG's 300 points are 10 of their LT, which is 10.16, 4.762 and 3.584 study LT (CONDITIONAL, §2.3). The window matters only when it truncates: the study censors at 8 LT. Every stored V3 is ≤ 3.3667 LT (§3), so the median is not censored in any run |
| M11 | Training or library length | Gilpin 2023: "10 full periods comprising 1000 timepoints are used to train the model ... this corresponds to an average of 11 λ_max^-1 used for training each system" (App. E p.12, confirmed). ZG25/ZG26: context length 512 (confirmed) | `StudyConfig.core_library` = 10⁴ admissible delay vectors (`data.py::library_admissible`: consecutive indices); sweep `library_sizes` 10³ to 10⁵ | **partly** | Study: 10⁴ steps = 333.3 study LT (sweep 33.3 to 3333 LT). Gilpin 2023: 10 t_peak = 13.59, 4.238 and 6.276 study LT (CONDITIONAL A3 i). ZG: 512 points = 17.07 of their LT = 17.33, 8.128 and 6.116 study LT (CONDITIONAL A3 ii). The core library is 19.5 times the ZG context in samples |
| M12 | Where the analogs come from | ZG26: "context parroting can be seen as a nearest neighbor algorithm in the D-dimensional delay-embedded space"; App. F.1: "a continuous 1-nearest-neighbor search over sequences of length D" (confirmed). The search set is the context itself | separate library segment, with gaps longer than one Theiler window (1 LT) plus the delay and forecast windows (`data.py` lines 519–533; v3 §4 "Data partition") | **partly** | Both are 1-nearest-neighbor. The study searches an independent noisy segment. ZG26 searches the forecast's own history |
| M13 | Noise | Gilpin 2023: noise **not present** in the main experiments (App. B p.8, confirmed). ZG26 App. E: "We add Gaussian noise to normalized chaotic trajectories"; "a noise level of 0.1 translates to" a 10% perturbation per point; levels 10⁻³, 10⁻², 10⁻¹ (confirmed). R20 C.1 reads the normalization as zero mean, unit s.d. (carried over) | iid Gaussian observation noise ρσ_x on the scalar observable, in the library, the query and the verification; V3 at ρ = `core_noise` = 0.01 (v3 §4 "Observation and embedding") | **partly** | ZG26 level 10⁻² corresponds to ρ = 0.01 if the noise s.d. is the level times the coordinate s.d. and the noise is observational (both **not confirmed**). Against Gilpin 2023: **no** (no noise there) |
| M14 | Analog forecaster | ZG26 context parroting (M12, confirmed) | CP: exact Euclidean 1-NN on delay vectors X_t = (x_t, …, x_{t−6τ}), D = 7, τ = `context/delay` steps; copies the analog's noisy future (v3 §4 "CP") | **partly** | Same class. The study's library is independent and lagged by τ steps; ZG26 uses consecutive-sample sequences of length D. Their D is not in the text read (**not confirmed**) |
| M15 | Physics-based forecaster | Gilpin 2023 App. D.A lists ESN, nVAR and neural ODE under "Physics-based methods" (confirmed). These are data-driven models with built-in structure and no known equation of the target (R23 B.1) | PLP: known equations, Levenberg–Marquardt state estimate, RK4 propagation (v3 §4 "PLP") | **no** | There is no counterpart with a known model in the benchmark texts read |
| M16 | λ_max values | Dysts `maximum_lyapunov_estimated` 0.8917, 0.1506, 1.2301; `lyapunov_spectrum_estimated[0]` 1.0911, 0.07633, 0.4605 (R23 A.2, confirmed, no s.e.). Published: Lorenz 0.90563 (Sprott, confirmed); 0.90410 ± 0.00076 (Bogdanov and Bogdanova, confirmed); Rössler 0.07062 ± 0.00066 (confirmed); 0.0714 (Sprott, secondary, **not confirmed** first-hand); Chua: none found | `systems/<s>/context/lambda_max` (ensemble, GPU): 0.905669, 0.0717189, 0.440852 | **partly** | Study/published: Lorenz 1.00004 (Sprott) and 1.0017 (B&B); Rössler 1.0156 (B&B) and 1.0045 (Sprott). Chua has no published referent. The Dysts max field is 2.10 and 2.79 times the study value for Rössler and Chua (§2.3); R23 calls it internally inconsistent. No verdict word: neither side has an s.e. |

### 2.2 Systems of the extension runs (DEV-3 only)

| System (code) | Dysts entry | Status of the match | Comparable |
|---|---|---|---|
| `rossler_hyper` | `HyperRossler` | Same `_rhs` and parameters a 0.25, b 3, c 0.5, d 0.05 (R20 B.1, confirmed 10-20, full digits cross-checked). The Dysts Lyapunov fields contradict the published spectrum (R20 B.1) | **partly** (system yes; time unit no, because the Dysts λ fields are unusable) |
| `lorenz63_r166` | none at r = 166.1 | confirmed absent (R20 B.2) | **no** |
| `rossler_z` | `Rossler` | Same system, observed through z (`rossler_zfirst_field`, `observed_index` 0 is z). Stored λ 0.0716502 against `rossler` 0.0717189 (ratio 0.99904; same system, different trajectory) | **partly** (observable differs, M2) |
| `hindmarsh_rose`, `hyper_jha`, `lorenz96_4` | `HindmarshRose`, `HyperJha`, `Lorenz96` | Parameters in `systems.py` lines 410–449 equal the values relayed in R20 D.2. R20 §0 says rows other than the four it cross-checked "should be re-read before any number is quoted". **Not confirmed** | **not established** |

### 2.3 Stated conversions (the only computed numbers; script `2026-10-23-math-benchmark-mapping/extract_v3.py`)

The λ_S are the ensemble leaves `systems/<s>/context/lambda_max`, identical on DEV-1/3/4. The Dysts fields are from R23 A.2.

| Conversion | Formula | Lorenz-63 | Rössler | Chua |
|---|---|---|---|---|
| Δ check | 1/(30 λ_S) against stored `context/interval` | 0.0368052 = stored | 0.464777 = stored | 0.0756112 = stored |
| Factor to Dysts-max-field LT (CONDITIONAL A3 ii) | λ_max-field / λ_S | 0.9846 | 2.100 | 2.790 |
| Factor to Dysts-spectrum[0] LT | spectrum[0] / λ_S | 1.205 | 1.064 | 1.045 |
| Study steps per t_peak (CONDITIONAL A3 i) | period / Δ | 40.78 | 12.71 | 18.83 |
| Gilpin 2023 training 10 t_peak in study LT (CONDITIONAL A3 i) | 10 · period · λ_S | 13.59 | 4.238 | 6.276 |
| ZG context 512 points in study LT (CONDITIONAL A3 ii) | (512/30) · λ_S/λ_max-field | 17.33 | 8.128 | 6.116 |
| ZG forecast window 300 points in study LT (CONDITIONAL A3 ii) | 10 · λ_S/λ_max-field | 10.16 | 4.762 | 3.584 |
| Study core library in study LT | 10⁴ / 30 | 333.3 | 333.3 | 333.3 |

Per-run conversions of V3 itself (natural time T = V3/λ_S, T/t_peak, and the CONDITIONAL rescaling V3 · λ_max-field/λ_S) are printed in `extract_v3.out.md`. They are not used in §3. They are not comparable with any published per-system number, because none exists.

**What the conversions show.** Even the unit of the benchmark's time axis is uncertain for Rössler and Chua: a factor 2.1 to 2.8 hangs on an unconfirmed item (A3 ii). Any table that puts the study's V3 in "benchmark Lyapunov times" must carry that condition.

## 3. Descriptive table (draft for WU-0024.3)

**Development context: not a hypothesis test.**

The table is development only: seeds DEV-1, DEV-3 and DEV-4, unpromoted. It is not to be placed beside any sealed value. It makes no ranking claim.

### 3.1 Runs (provenance; `run.meta.json`, `results.json/provenance`)

| Run (path under `/home/brianm/projects/physics/chaos/lpcstudy-wt/run/`) | seed_id | commit | dirty | complete | SHA-256 `results.json` |
|---|---|---|---|---|---|
| `ens-3dec086/runs/dev/ens-DEV-1/full` | DEV-1 | 3dec086 | false | true | `0a4ef215c7262340cef3e95cc073c4b7a374c73d688a12ad68ed5517d6102860` |
| `ens-3dec086/runs/dev/ens-DEV-3/full` | DEV-3 | 3dec086 | false | true | `24a7c4b77a253ec34a1a6e301a932d3171ec22c1a70568941158c9a6787af247` |
| `ens-3dec086/runs/dev/ens-DEV-4/full` | DEV-4 | 3dec086 | false | true | `8eadc3992bcbffbeb399c46523eb308d351eb081937a622029119f68861c5655` |
| `ext-run-974519a/runs/dev/ext-rossler_hyper-gpu/full` | DEV-3 | 974519a | false | true | `ac588151e6aad4efabf1be0e9977c4d3366d895d605722cf6a1c660c054ceffc` |
| `ext-run-974519a/runs/dev/ext-lorenz63_r166-gpu/full` | DEV-3 | 974519a | false | true | `183a151966ae5c851bd1bde05ab1e8ff7b82c7da13a0974a2896ef8e60671e4c` |
| `ext-run-974519a/runs/dev/ext-rossler_z-gpu/full` | DEV-3 | 974519a | false | true | `f95ae88a22bccfe04dba48aa1f23632243a5b3c8cd740b261f098a17c5fdbf93` |
| `ext-run-392a069/runs/dev/ext-hindmarsh_rose-gpu/full` | DEV-3 | 392a069 | false | true | `090f82e0ba16aed9f01666d2ab4043f394f32c6cebc2273c7d804059f7b1b8e4` |
| `ext-run-392a069/runs/dev/ext-hyper_jha-gpu/full` | DEV-3 | 392a069 | false | true | `5edfd1deb91eac73e56701cbc8ee9abaa852b1c714e1571cd1e96be87c603b7a` |
| `ext-run-392a069/runs/dev/ext-lorenz96_4-gpu/full` | DEV-3 | 392a069 | false | true | `8aaac680997ae24407526cba6f5cc55f7b5744d47330596e4ec03323c4da2e6b` |

Every run stores `label` "DEVELOPMENT (DEV-n): not a hypothesis test", `promoted` false, `steps_per_lyapunov` 30, `horizon_max_lyapunov` 8, `core_noise` 0.01, `core_library` 10000 and `n_test` 1000.

### 3.2 Overlapping systems: CP valid-prediction time V3, θ = 0.4 σ_x, ρ = 1% σ_x, N_lib = 10⁴, in study LT

Leaf: `systems/<s>/validation/cp_median_vpt_lyapunov`. The value × 30 is the step count. Seeds are side by side; no mean, spread or range is taken (schedule O7).

| System | DEV-1 | DEV-3 | DEV-4 | Gate (all seeds) | Published per-system value of a comparable quantity | Status |
|---|---|---|---|---|---|---|
| Lorenz-63 | 2.0 (60 steps) | 2.0333 (61) | 2.0333 (61) | PASS | **none** | None was found in any text read: Gilpin 2023 pp.1–12, ZG25 and ZG26 extracts. Gilpin 2023 Appendix F (pp.13+) and the `dysts_data` results files were not read (R23 D.6). ZG26 shows Lorenz only in figures, with no number (R23 B.2) |
| Rössler | 3.3 (99) | 3.1333 (94) | 3.2333 (97) | PASS | **none** | as above |
| Chua | 2.9 (87) | 2.9 (87) | 2.9667 (89) | PASS | **none** | as above |

### 3.3 Extension systems (DEV-3 only, one run each; no overall verdict)

| System | V3 (LT) | Gate | Dysts entry (§2.2) | Published per-system value | Status |
|---|---|---|---|---|---|
| rossler_hyper | 1.5667 (47 steps) | PASS | HyperRossler | **none** | none found |
| lorenz63_r166 | 3.3667 (101) | FAIL V7 → PROVISIONAL | none | **none** | no Dysts entry |
| rossler_z | 0.46667 (14) | FAIL V7 → PROVISIONAL | Rossler (observed through z) | **none** | none found |
| hindmarsh_rose | 0.86667 (26) | FAIL V7 → PROVISIONAL | HindmarshRose (parameters not confirmed) | **none** | none found |
| hyper_jha | 0.36667 (11) | FAIL V7 → PROVISIONAL | HyperJha (parameters not confirmed) | **none** | none found |
| lorenz96_4 | 0.9 (27) | FAIL V7 → PROVISIONAL | Lorenz96 (parameters not confirmed) | **none** | none found |

V3 is CP-only and does not use the PLP estimator, so the V7 failure does not enter its computation. The PROVISIONAL label applies to the run as a whole (v3 §6 E0) and is kept here.

### 3.4 Published benchmark values (not per system; listed for context, not beside the rows above)

| Value | Quantity, as defined in the source | Source and status | Why it is not a comparable number for any row of §3.2 |
|---|---|---|---|
| 13.9 ± 2.8 λ_max⁻¹ | "latest time when SMAPE < 50", "best-performing model averaged across all 135 systems" | Gilpin 2023 App. A p.8, **confirmed**; meaning of ± **not confirmed** | M5–M7, M9; no noise (M13); a mean over systems of the best of 24 models |
| 15 ± 5.3 λ_max⁻¹ | "first doubling of accumulated pointwise errors" | Gilpin 2023 App. A p.8, **confirmed** | as above; different error criterion |
| 14 ± 2 λ_max⁻¹ | "the best-performing models achieve an average prediction time" | Gilpin 2023 Sec. III.A p.4, **confirmed** | as above |
| 2.10 ± 0.18 | context parroting, "Valid prediction time across noise levels", noise level 10⁻² | ZG26 App. E Table 5 (R20 C.2, fetch extract 2026-10-20). **Not confirmed** on 10-23: R23 B.2 saw the caption but not the value; the unit, the VPT definition and the aggregation are not stated | Unit unknown (M3); definition unknown (M6, M7); averaged across systems (M9) |

## 4. Uncertainty budget for V3 (development; uq-budget skill)

| Source | Type | How estimated | Size (LT) | In a reported interval? |
|---|---|---|---|---|
| Sampling of test states | aleatory | **not estimated**: no interval is stored for V3, and the unit excludes new statistics | — | no interval exists; V3 is a point value |
| One noise draw per state | aleatory | not estimated | — | no |
| Seed (DEV-1/3/4) | aleatory | the three stored values side by side (§3.2); no spread statistic (O7) | see §3.2 | no |
| Median resolution | numerical | exact: V3 ∈ (1/30)ℕ (P-a) | grid 0.0333 | no |
| RK4 discretization | numerical | The QoI is defined on the discrete map (LPC.NV.1). Truth and library come from the same integrator, and CP does not integrate. V6 bounds the step-halving change at < 10⁻³ σ_x over 1 LT. At the crossing, with error growth ∝ e^{H/30}, de/dH ≈ θ/30 = 0.0133 σ_x per step, so a first-order shift ≤ 10⁻³/0.0133 = 0.075 steps | ≤ 0.0025, below the grid | no |
| Clip at 10 σ_x | numerical | P-b: cannot move τ_i | 0 | no |
| Time unit (λ_S) | epistemic or numerical | GPU against CPU λ on the same code and seed (WU-0003-R0): ratio 1.00019 (Lorenz), 0.99693 (Rössler), 1.0225 (Chua). Against published: Lorenz 1.00004, Rössler 1.0045 or 1.0156; Chua none | Converting V3 to natural time carries the relative λ difference, up to 2.2% on Chua | no |
| Definitional gap to the benchmark (metric, threshold, aggregation, λ_B) | epistemic | not estimable (L3, M3, M9) | — | no; stated as a limitation |

There is no reported interval, so the 10× rule for numerical rows has nothing to compare against. The numerical rows (grid, RK4, clip) are each at most one grid step (0.033 LT). The stored seed values are shown side by side in §3.2, with no spread statistic. V3 is a reported sanity reference, not gated (v3 §6). Interval level and dependence: none, because no interval is reported.

## 5. Plain-language paragraph for the appendix (draft; the owner reads the caption first)

> Gilpin's Dysts benchmark contains the same Lorenz, Rössler and Chua equations that this study uses. Its numbers still cannot be put on the same scale as ours. The benchmark scores forecasts with a percentage error (sMAPE) that depends on the size of the signal at each moment. Our study uses a fixed error limit: 0.4 standard deviations of the observed coordinate. The benchmark also measures time in Lyapunov times computed in a way that, for Rössler and Chua, may differ from ours by a factor of about two to three, and its published results are averages over 135 systems rather than values for each system. For these reasons we list our development values of the analog forecaster's valid-prediction time next to the benchmark's definitions, and we do not compare them. The benchmark has no counterpart of our physics-based forecaster. These are development runs, not a hypothesis test.

## 6. Findings for the caller

- **F1.** The V3 threshold θ = 0.4 is a literal in code (`experiments.py` line 428) and in v2 (line 303). v3 §6 does not state it, and 0.4 is not in the v3 θ set. The caption and any comparison text must say θ = 0.4 σ_x. Recording it in a v3 amendment is the owner's decision.
- **F2.** R20 §C.3 quotes the study's CP values as "1.97 (Lorenz), 3.43 (Rössler), 2.8 (Chua)" at "error above 0.2". The threshold label disagrees with the code (0.4). The values match no V3 leaf read here: DEV-0 stores 2.1 / 3.2667 / 2.9667, and the ensemble values are in §3.2. The same values recur in `2026-10-20-math-extension-specs.md` line 198. **They must not be used.**
- **F3.** R23's Lyapunov ratios (2.093, 2.853) use the DEV-0 CPU leaf: Chua 0.431133. The ensemble GPU leaf is 0.440852, which gives 2.100 and 2.790. Quote the ratio of the run that supplies the values.
- **F4.** V3 measures against the noisy verifying observation (v3 §6 Horizons), not the noise-free truth.
- **F5.** For Gilpin 2023 the identification t_peak = Dysts `period` (A3 i) and the source of λ_max (A3 iii) are inferences. The training-length and sampling rows depend on them.

## 7. Banned-word check (D3)

**Words checked.** The seven words and phrases of WU-0024 D3, as listed in `docs/agent/records/work/WU-0024-dysts-benchmark.md`, plus the hyphenated variant of the fourth phrase. They are not spelled out here, so that this section does not match itself.

**Command.** A case-insensitive `grep -n -i -E` on that alternation, over `2026-10-23-math-benchmark-mapping.md`, `2026-10-23-math-benchmark-mapping/extract_v3.py` and `2026-10-23-math-benchmark-mapping/extract_v3.out.md`.

- **Result: 0 hits** in all three files, with no line excluded.
- **Wider net** (the stems beat, better, worse, best-perform): apart from this line, the only hits are the quoted source phrase "best-performing model(s)", three times, in §2.1 M9 and §3.4. It is quoted from Gilpin 2023 App. A and Sec. III.A, and it is not on the D3 list. The poster caption should paraphrase it ("the top model of the benchmark") or drop it.

## 8. Reproduction

`python3 -I docs/agent/notes/2026-10-23-math-benchmark-mapping/extract_v3.py > .../extract_v3.out.md`

- Standard library only; CPU; read-only on the run folders.
- It prints:
  - every leaf with its path;
  - the SHA-256 of each `results.json`;
  - the conversions of §2.3.
