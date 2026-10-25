# LPC Study: Experimental Procedure (as run for CONF-1)

This document says, step by step, how the confirmatory run CONF-1 was done. It names the variables, the materials and instruments, the sample sizes, the number of trials and repetitions, and how the data were analyzed. It is written so that a reader who can use a terminal and read Python can repeat the work from this document and the repository alone.

- **Governing design:** `docs/study/proposal_and_methods_v3.md` (written "v3" below; SHA-256 `4f2ead48…5abe073`, recorded in ledger entry 12). Where this document and v3 differ, v3 governs.
- **Code that was run:** git tag `freeze-1`, commit `df8928fd06721d681469c9c3e40705e1b4b8053f`.
- **Result:** `promoted/CONF-1/` (promoted by ledger entry 40, 2026-10-23).

Every design constant below is quoted from v3 or from `lpcstudy/config.py` at `freeze-1`. Every measured value of the run (time steps, delays, run times) is copied from the run's own records: `runs/confirmatory/run-1.console.log` and the `provenance` block of `promoted/CONF-1/results.json`.

---

## 1. What the study asks, and where each question is answered

The study compares two ways of forecasting a chaotic system when only one noisy measurement is available:

- **CP (context parroting)**, an *analog* forecaster. It finds the moment in a library of past measurements that looks most like the present and copies what happened next.
- **PLP (physics-based latent-state propagation)**, a *physics* forecaster. It estimates the hidden state of the system from the recent measurements, then runs the known equations forward.

The two forecasts are blended as x̂ = w · x̂_CP + (1 − w) · x̂_PLP, where w (between 0 and 1) is the **weight on CP**. The study asks whether four measurable *local predictability conditions* (LPCs) of the current state can tell us what w should be:

| Condition | What it measures | Symbol |
|---|---|---|
| Recurrence | how close the nearest past analog is | R (and the analog error ε_s) |
| Observability | how well the hidden state can be reconstructed from the measurements | ν (and the estimation error δ) |
| Instability | how fast small errors grow from this state | Λ̃ |
| Noise sensitivity | how much the chosen analog changes when the measurement noise changes | N |

The three research questions, their hypotheses, and the experiments that feed them (v3 §2 and §6):

| Research question | Hypotheses | Role | Experiments |
|---|---|---|---|
| **RQ1 (mechanism).** Do the four conditions predict each forecaster's error in the form the theory gives, and is noise sensitivity distinct from the other three? | H1a, H1b, H1c, H1d; estimate Q-N | secondary; estimate | E2, E3 |
| **RQ2 (decision).** Does allocation derived from the conditions beat simple alternatives, and do the two interventions move the weight as predicted? | **H2a**, **H2b**; H2c, H2d, H2e | **primary**; secondary | E1, E2, E4 |
| **RQ3 (compression).** Can a few regimes defined by the four conditions carry the weight and the horizon? | **H3c**; H3a, H3b | **primary**; secondary | E5 |

The three **primary** hypotheses, in words:

- **H2a (separation).** Once the two initial errors are known, the best weight w\* does not depend on the forecast horizon or on instability.
- **H2b (interventions).** w\* rises when the measurement noise rises, and when the library grows (below saturation).
- **H3c (regimes).** A lookup table with a few regimes, defined by the four conditions, loses almost nothing (at most 5% in mean squared error) against the closed-form allocation rule.

The study also has two proved results, which are not tested by the experiment but tell us what to expect: **P1** (the best weight has a closed form, and blending can extend the horizon by at most half an error-doubling time) and **P2** (when analog retrieval is stable under noise). See v3 §3.

---

## 2. Variables

### 2.1 Independent variables (deliberately changed)

Only two quantities are true interventions, set by the experimenter and changed while everything else is held fixed:

| Variable | Levels | Where it is changed |
|---|---|---|
| Observation noise ρ (standard deviation of the noise, as a fraction of σ_x, the standard deviation of the measured variable) | 0.5%, 1%, 2%, 5% | E1 (noise sweep), at N_lib = 10⁴ |
| Library size N_lib (number of past delay vectors CP can search) | 10³, 10^3.5 (3,162), 10⁴, 10^4.5 (31,623), 10⁵ | E2 (library sweep), at ρ = 1% and 2% |

The same random draws are rescaled across noise levels and library sizes (*common random numbers*), and the smaller libraries are the first part of the larger ones (*nested libraries*). So when ρ or N_lib changes, the difference in the result comes from the intervention and not from new random numbers.

### 2.2 Design factors (conditions that are crossed, not interventions)

| Factor | Levels |
|---|---|
| System | Lorenz-63, Rössler, Chua's circuit |
| Forecast horizon H | 0.25, 0.5, 1, 2, 4 Lyapunov times (LT) for the weights and errors; 1 to 240 steps (up to 8 LT) for horizons. The reference horizon is H_ref = 1 LT = 30 steps |
| Error tolerance θ (for the forecast horizon) | 0.1, 0.2, 0.3, 0.5 σ_x, keeping only θ ≥ 3√2 ρ; θ = 0.2 is primary |
| Allocation rule | A0 (CP alone), A1 (PLP alone), A2 (one global weight), A3 (learned allocator), A4 (closed form), A5 (regime lookup); references A4o (closed form with exact errors) and A\* (state-optimal) |
| Number of regimes K | 2, 3, 4, 5, 6, 8, 12, 16 |

### 2.3 Measured explanatory variables (observed per state, not manipulated)

The four conditions cannot be set by the experimenter: they are properties of each state on the attractor. They are *measured* for every test state, twice:

- **exactly (oracle)**, using the true state, to test the mechanism;
- **deployably**, from the measurements, the model and ρ only, to test allocation fairly.

| Quantity | Exact (oracle) version | Deployable version |
|---|---|---|
| Analog error (seed) ε_s | r.m.s. hidden-state mismatch of the retrieved analog, over 200 noise draws | ε̂² = a(R ν̂)² + b(ρ ν̂)² |
| Estimation error (seed) δ | r.m.s. error of the state estimate, over 200 noise draws | δ̂² = a′(ρ ν̂)² + b′ρ² |
| Observability ν | ν² = tr[(JᵀJ)⁻¹], J the Jacobian of the delay map | ν̂ = ν at the estimated state, capped at its 99th percentile |
| Instability Λ̃ | growth rate of the observable's sensitivity over 1 LT, in units of λ_max | Λ̂, the same from the estimated state |
| Noise sensitivity N | r.m.s. displacement of the retrieved analog under noise, in units of ρ | N̂, from 16 synthetic perturbations of the observed query |

The coefficients a, b, a′, b′ are fitted on the construction states (robust least squares on a log scale). This matters for interpretation: **H2a and H3b are observational** (they ask how w\* varies with measured conditions), while **H2b is interventional** (it asks how w\* responds when ρ and N_lib are changed).

### 2.4 Dependent variables (outcomes)

| Outcome | Definition | Used by |
|---|---|---|
| Optimal weight w\* | w\* = clip to [0, 1] of (E_P − C)/(E_C + E_P − 2C), where E_C, E_P are the mean squared errors of CP and PLP over 200 noise draws and C is their mean cross-product (Theorem P1) | H2a, H2b, Q-N |
| Mean squared error of each rule | mean over test states of the squared blended error at H_ref, measured against the noise-free truth | H2c, H2d, H3c |
| Realized forecast horizon | first step at which the error against the *noisy* verifying measurement exceeds θ σ_x; right-censored at 8 LT | H1c, H3a, H3b |
| Error correlation | per-state correlation of the CP and PLP errors | H2e |
| PLP error at H_ref | r.m.s. PLP error | H1b |

All errors are measured against the noise-free truth and clipped at 10 σ_x (every clip is counted; see §6.6).

### 2.5 Controlled variables (held fixed throughout)

| Controlled variable | Value |
|---|---|
| Equations and parameters | exact, and the same for the truth and for PLP (v3 §4; §3.2 below) |
| Measured variable | the first coordinate x, normalized to unit variance |
| Time scale | 1 Lyapunov time (LT = 1/λ_max) = 30 observation steps, for every system |
| Integrator | classical 4th-order Runge–Kutta, with the observation interval cut into equal substeps no longer than the system's maximum step |
| Delay embedding | D = 7 delays, delay τ at the first minimum of the average mutual information (capped so the window spans at most 1 LT) |
| Burn-in | 100 LT discarded before any data are used |
| Theiler window and gaps between data splits | 1 LT plus the delay and forecast windows |
| Spacing of evaluation states | max(5 · min(τ_ac, 1 LT), 1 LT), with τ_ac the autocorrelation time |
| State estimator | neural-network first guess plus 15 Levenberg–Marquardt iterations |
| Number formats | float64 everywhere (`jax_x64` true) |
| Randomness | one master seed; every random stream is derived from it by `make_rng(seed, *labels)` |
| Software | Python 3.13.16; jax and jaxlib 0.11.2, optax 0.2.8, numpy 2.5.3, scipy 1.18.1, scikit-learn 1.9.1, matplotlib 3.11.2 |
| Device and threads | CPU only (`JAX_PLATFORMS=cpu`), `LPC_THREADS=8` (and OMP, MKL, OpenBLAS threads = 8) |
| Analysis plan | fixed in v3 before the run: statistics, bands, levels, block length, resample count |

---

## 3. Materials and instruments

This is a computational study. The "materials" are a computer, software, and three mathematical systems; the "instruments" are the numerical routines that measure each quantity, each checked before its numbers are used.

### 3.1 Hardware and software (as recorded by the official run)

| Item | Value |
|---|---|
| Computer | workstation with an Intel Core i9-14900K (32 logical CPUs); 8 threads used |
| Operating system | Linux 7.2.9 (CachyOS), glibc 2.44, x86-64 |
| Linear-algebra library | OpenBLAS (the copies bundled with numpy and scipy), kernel "Haswell" |
| Peak memory | about 4.7 GB (4,698,107,904 bytes) |
| Run time | 15,555 s (about 4 h 19 min), 2026-10-19 08:38 to 12:57 UTC |
| Software | Python 3.13.16 and the pinned packages in `requirements.txt` (direct) and `requirements.lock` (complete installed set) |
| GPU (cross-check only) | NVIDIA GeForce RTX 4090, `jax[cuda12]==0.11.2`; 2,696 s |

### 3.2 The three systems

Each is a set of three ordinary differential equations with a chaotic attractor. Only x is measured.

| System | Equations | Parameters | Start state of the reference orbit | Orbit bound on abs(x) |
|---|---|---|---|---|
| Lorenz-63 | ẋ = σ(y − x), ẏ = x(r − z) − y, ż = xy − bz | σ = 10, r = 28, b = 8/3 | (1, 1, 1) | 40 |
| Rössler | ẋ = −y − z, ẏ = x + ay, ż = b + z(x − c) | a = 0.2, b = 0.2, c = 5.7 | (1, 1, 0) | 25 |
| Chua (dimensionless, piecewise-linear diode) | ẋ = α(y − x − f(x)), ẏ = x − y + z, ż = −βy, with f(x) = m₁x + ½(m₀ − m₁)(abs(x + 1) − abs(x − 1)) | α = 15.6, β = 28, m₀ = −1.143, m₁ = −0.714 | (0.7, 0, 0) | 3 |

Values derived by the code at the start of the run (identical for every seed, because they come from the fixed reference orbit):

| System | λ_max (per time unit) | Observation interval Δ = 1/(30 λ_max) | Max RK4 step | RK4 substeps per observation | σ_x | Delay τ (steps) | Autocorrelation time (steps) | State spacing (steps) |
|---|---|---|---|---|---|---|---|---|
| Lorenz-63 | 0.9055 | 0.03681 | 0.01 | 4 | 7.925 | 5 | 9 | 45 |
| Rössler | 0.07194 | 0.4634 | 0.04 | 12 | 5.150 | 3 | 1500 | 150 |
| Chua | 0.4311 | 0.07732 | 0.005 | 16 | 1.419 | 5 | 76 | 150 |

### 3.3 Instruments (measurement routines) and their checks

| Instrument | Method | Code (`lpcstudy/`) | Check before use |
|---|---|---|---|
| Integrator | RK4 flow map | `systems.py` | V6: halving the step changes x by less than 10⁻³ σ_x over 1 LT |
| Largest Lyapunov exponent λ_max | Benettin's method (Benettin et al. 1980) | `systems.py` | validated against published Lorenz-63, Rössler and Chua cases (no published value exists for Chua at these parameters) |
| Delay τ | first minimum of average mutual information (Fraser & Swinney 1986) | `embedding.py` | — |
| Jacobians and amplifier g_H | automatic differentiation | `dynamics.py` | V1: agree with finite differences, relative error < 10⁻⁴ |
| Analog search (CP) | exact Euclidean nearest neighbour (k-d tree) | `ensemble.py` | — |
| State estimator ψ (PLP stage 1) | MLP, 2 hidden layers, GELU, Adam with cosine-decayed learning rate 2×10⁻³, minibatch 256, 10% held out; trained on 100,000 noise-free delay vectors of a separate trajectory with fresh noise at the cell's ρ in every minibatch, 40 epochs; widths 64 and 128 tried, the smallest within 5% of the best validation loss kept | `networks.py` | — |
| State estimator ψ (PLP stage 2) | 15 Levenberg–Marquardt iterations fitting the model to the delay window | `estimation.py` | V2: at ρ = 10⁻⁴ the error attains the Cramér–Rao value, ratio in [0.8, 1.2]; V7: median δ/(ρν) and the median per-state slope of ln δ on ln ρ in [0.9, 1.1] |
| Oracle moments and w\* | 200 noise draws per state | `ensemble.py`, `oracle.py` | V4: w\* converged at M = 200 (median bootstrap half-width ≤ 0.05; checked at M = 50, 200, 800 on 100 states) |
| Learned allocator (A3) | MLP of width 64, 40 epochs, trained on 50 oracle draws per construction state to predict both forecasters' log squared errors; w = ê²_PLP/(ê²_CP + ê²_PLP) | `allocation.py` | — |
| Regime trees (A5) | regression tree (`sklearn` `DecisionTreeRegressor`) on the deployable profile with K leaves | `allocation.py` | — |
| Local dimension | Levina–Bickel estimator | `analysis.py` | — |
| Q-N regressors | gradient-boosted trees (`HistGradientBoostingRegressor`: 300 iterations, learning rate 0.05, 15 leaves, 20 samples per leaf, L2 = 1.0) | `analysis.py` | — |
| Survival curves | Kaplan–Meier | `statistics.py` | V5: matches exact censored survival, maximum deviation < 0.01 |
| Intervals | moving-block bootstrap (Künsch 1989) | `statistics.py` | coverage measured in simulation before the freeze (v3 §8) |

V3 (CP's valid prediction time) is reported for comparison with Zhang & Gilpin (2026) and has no bar. V1 to V7 together form the **validation gate** (experiment E0). A system that fails it is marked PROVISIONAL; it is never repaired by retuning or rerunning. In CONF-1 every check passed on all three systems.

---

## 4. Sample size, trials and repetitions

### 4.1 Per system, per run

| Unit | Count | Notes |
|---|---|---|
| Systems | 3 | Lorenz-63, Rössler, Chua |
| Cells (noise × library combinations) | 12 | the core cell (ρ = 1%, N_lib = 10⁴), 3 more noise levels at N_lib = 10⁴, and 4 more library sizes at each of ρ = 1% and 2% |
| Construction states (core cell) | 2,000 | fit the proxies, the global weight, the learned allocator, the regime trees |
| Calibration states (core cell) | 1,000 | choose K; regime weights and horizons |
| **Test states (core cell)** | **1,000** | all reported results of the core cell |
| Test states per sweep cell | 1,000 | noise and library sweeps |
| Oracle noise draws per state, M | 200 | exact error moments and w\* |
| Evaluation noise draws per state | 4 | deployable evaluation (the first draw is used where one observation per state is needed) |
| Synthetic perturbations for N̂ | 16 | per evaluation draw |
| Estimator training pairs | 100,000 | separate trajectory, retrained at each ρ |
| Bootstrap resamples, B | 2,000 | blocks of 5 consecutive states |

The 50-state rule: a statistic computed on fewer than 50 states is inconclusive (v3 §7).

### 4.2 Trials and repetitions

- **One confirmatory trial.** CONF-1 is one run with one sealed seed, so it is **one realization per system**. No variation between independent replicate datasets is estimated; this is a stated limitation. The uncertainty in every reported number comes from the bootstrap over test states inside that realization.
- **Repetitions within the trial.** Each test state is forecast under 200 independent noise draws (exact moments) and 4 evaluation draws. Each interval comes from 2,000 bootstrap resamples.
- **Repetition of the run (determinism).** The owner regenerated the official run from the same commit on the same computer (run-2, 7,884 s). Every compared value was bitwise equal (20,766 of 20,766 leaves). This shows the code is deterministic. It is not an independent reproduction, because the same person and computer produced both runs.
- **Cross-check on another device.** A GPU run of the same seed agreed statistically on all 18 primary parts (largest z = 2.21 against the bound 3.4). GPU and CPU build slightly different trajectories, so 11 stored overall or per-system verdict words differed (listed in `promoted/CONF-1/report.md` §8). The official CPU words stand.
- **Development runs (not part of the result).** Before the freeze, the procedure was rehearsed on development seeds (DEV-0 to DEV-4) at the smoke, pilot and full sizes, to check the plumbing and the projected precision. These runs are never reported as tests of the hypotheses.

### 4.3 Why these sizes

The design fixed the sample sizes before the run (v3 §4 and §7). The pilot (smaller sizes, development seed) was used to project the interval widths to the full size; v3 §7 records which criteria were expected to be decidable. It also records, in advance, that H2a part (ii) can be refuted but essentially cannot pass at these sizes. The coverage of the intervals at these sizes was measured in simulation and is stated in v3 §8.

---

## 5. Procedure, step by step

### 5.1 Before the run: fixing the design (done once, in this order)

1. **Write the design.** The research questions, hypotheses, statistics, pass bands, levels and decision rules were written in v3 (dated 2026-10-10) before any confirmatory data existed.
2. **Freeze the code and design.** The owner recorded the freeze in the ledger (entry 12, 2026-10-19 08:26 UTC), naming commit `2d22bed` and the SHA-256 of v3. The tag `freeze-1` is that commit plus one commit that adds only the ledger entries; the study code is the same.
3. **Seal a fresh seed.** The owner ran `tools/seal_confirmatory_seed.py`, which draws a 62-bit random seed and a 128-bit salt and prints a salted SHA-256 commitment. The commitment went into the ledger (entry 13, 08:32 UTC); the seed and salt stayed outside the repository. At run time the code checks the seed against the commitment and refuses to run on a mismatch. This proves the seed was fixed before any result existed.
4. **Run once.** The owner started the official run 6 minutes later (08:38 UTC):

   ```bash
   python -m lpcstudy --preset full --confirmatory --out runs/confirmatory/run-1
   ```

   on the CPU with `LPC_THREADS=8`. Its verdicts are the study's.

The sealed seed is not in the repository, so nobody else can rerun CONF-1 exactly. A replication uses a different seed (§5.2, step 5) and is expected to give different numbers.

### 5.2 Repeating the study on your own computer

You need Linux (the only platform used; others are untested), Python 3.13, about 5 GB of free memory, and several hours of CPU time (or a CUDA GPU).

1. **Get the code at the frozen commit.** The `main` branch now also contains later, additive extension code, so check out the tag:

   ```bash
   git clone <repository URL> lpcstudy
   cd lpcstudy
   git checkout freeze-1
   ```

2. **Install the pinned software** in a fresh virtual environment:

   ```bash
   python3.13 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt        # or requirements.lock for the complete set
   ```

   On a CUDA GPU, replace the jax line with `jax[cuda12]==0.11.2`.

3. **Set the device and thread count** used by the official run:

   ```bash
   export JAX_PLATFORMS=cpu XLA_PYTHON_CLIENT_PREALLOCATE=false
   export LPC_THREADS=8 OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
   ```

4. **Check the plumbing** (about 1 minute; tiny sizes, Lorenz-63 only):

   ```bash
   python -m lpcstudy --preset smoke --out results
   ```

   It should finish with exit code 0 and write `results/smoke/results.json`, `RESULTS.md`, `figures/` and `run.log`.

5. **Run the full study on a development seed.** Pick a registered seed from `seeds/development_seeds.json` (for example `DEV-1`), or append a new entry to that file:

   ```bash
   python -m lpcstudy --preset full --seed-id DEV-1 --out results/replication
   ```

   The wrapper `tools/run_preset.sh full DEV-1 runs/replication --device cpu` does the same, sets the thread variables from `LPC_THREADS`, and records a `run.meta.json`. Expect about 4 to 5 hours on a fast 8-thread CPU, or about 45 minutes on an RTX 4090. The `pilot` preset (smaller samples, same design) takes about 1.5 hours and is a good first attempt; its intervals are wider.

6. **Rebuild the report without recomputing** if needed:

   ```bash
   python -m lpcstudy --preset full --out results/replication --report-only
   ```

7. **Compare two runs** (for example a rerun of the same seed, or a CPU and a GPU run):

   ```bash
   python3 tools/compare_runs.py results/replication/full results/replication-2/full
   ```

   On the same computer, seed, thread count and commit, the result should be tier T0 (bitwise equal). On another computer or device, it is judged by statistical tolerances (tier TD).

### 5.3 What the program does, in order (for each system)

The program in `lpcstudy/experiments.py` runs five stages per system. These are the steps a reader would follow to rebuild it by hand.

**Stage (i): build the system and its data**

1. **Reference orbit.** Integrate from the fixed start state (§3.2), discard 100 LT of burn-in, and compute from this orbit: λ_max (Benettin), the observation interval Δ = 1/(30 λ_max), σ_x and the mean of x, the mean and covariance of the state (used to *whiten* the hidden state so all errors are dimensionless), the delay τ, the autocorrelation time and the state spacing. This orbit is the same for every seed and holds no test data.
2. **Two seeded trajectories.** Start a *main* trajectory and a *separate* (estimator-training) trajectory from seed-drawn points of the reference orbit, each perturbed by 10⁻⁶ in whitened units, and discard 100 LT of burn-in. Stop the run if any orbit leaves its bound (§3.2) or becomes non-finite.
3. **Measurements.** Normalize x to unit variance and add independent Gaussian noise of standard deviation ρ to each sample. Build delay vectors X_t = (x_t, x_{t−τ}, …, x_{t−6τ}).
4. **Split the main trajectory** in time order into library | construction | calibration | test, separated by gaps longer than 1 LT plus the delay and forecast windows, so that no window crosses a boundary. Pick evaluation states at the spacing of §3.2.

**Stage (ii): forecasters and mechanism checks**

5. **CP.** For each query delay vector, find the nearest of the N_lib library vectors by exact Euclidean distance and copy its noisy future for up to 8 LT. Record the recurrence distance R.
6. **PLP.** Train the state-estimator network on the separate trajectory at the cell's ρ (stage 1), refine its guess with 15 Levenberg–Marquardt iterations against the model (stage 2), then integrate the model forward. Estimates that converge to a wrong basin (a real property of nonlinear estimation) are kept and counted.
7. **Oracle quantities.** For each state, repeat both forecasts over M = 200 independent noise draws. Compute ε_s, δ, ν, g_H and Λ̃, N, the moments E_C, E_P, C at each horizon, w\* (Theorem P1) and the characteristic horizons.
8. **Noise sweep (E1)** at ρ = 0.5, 1, 2, 5% with N_lib = 10⁴, retraining the estimator at each ρ. **Library sweep (E2)** at N_lib = 10³ to 10⁵ for ρ = 1% and 2%.
9. **Validation gate (E0).** Run V1 to V7 (§3.3). The gate is final after V7, which needs the noise sweep.

**Stage (iii): allocation and horizons (E3, E4)**

10. **Deployable proxies.** Fit a, b, a′, b′ on the construction states; compute ν̂, ε̂, δ̂, Λ̂ and N̂ for every state; form the profile F̂ = (ln ε̂/ρ, ln δ̂/ρ, Λ̂, ln(N̂ + 0.01)).
11. **Fit the rules.** A2 (one weight per horizon) and A3 (learned allocator) on construction states; A4 = δ̂²/(ε̂² + δ̂²); A4o with the exact seeds; A\* = w\*.
12. **Score the rules** on the 1,000 test states: mean squared error at 0.25, 0.5, 1, 2 and 4 LT, and realized horizons at each admissible θ.

**Stage (iv): regimes (E5)**

13. **Regime trees.** For each K in {2, 3, 4, 5, 6, 8, 12, 16}, fit a regression tree with K leaves on F̂ (construction states). Give each leaf its curvature-weighted weight (Theorem P3) and a Kaplan–Meier horizon (calibration states). Choose the primary K as the smallest value in {2, 3, 4, 5, 6, 8} whose mean calibration excess MSE at H_ref is at most 1.05 times the minimum over that set.

**Stage (v): robustness (E6, reported only, Lorenz-63 and Rössler)**

14. Rerun the core cell with D = 5 and 10, with 5 averaged analogs, with model parameters scaled by 1 ± 5% and 1 ± 10% (one random sign per parameter), and with finite-amplitude growth in place of Λ̃. These results carry no verdict.

**Analysis and report**

15. Compute every statistic of §6, its interval and its verdict; write `results.json` (all numbers), `RESULTS.md`, the figures, and the handling counters (§6.6).

---

## 6. How the data were analyzed

The whole analysis plan was fixed in v3 §7 before the run. No statistic, threshold or subgroup was added afterwards.

### 6.1 Intervals

- **Method.** Moving-block bootstrap percentile intervals over the test states in time order (Künsch 1989). Consecutive test states are grouped into blocks of 5, blocks are drawn with replacement to make a new sample of the same size, the statistic is recomputed, and this is repeated 2,000 times. The interval is the middle part of the 2,000 values. Blocks keep the short-range dependence between neighbouring states.
- **Level.** The three primary hypotheses use 1 − 0.05/3 = **98.33%** (a Bonferroni split of 5% over three primaries). Everything else uses 95%.
- **Failed resamples.** A resample whose statistic cannot be computed is counted and placed at the unfavourable end, never dropped. Too many failures make the bound infinite, and the verdict inconclusive.
- **H3b** resamples construction states instead. **H3a** uses Holm-adjusted log-rank p-values instead of intervals.

### 6.2 Verdict for one system

| Verdict | Rule |
|---|---|
| **pass** | the interval lies inside the pass band, or entirely on the predicted side of the bound |
| **fail** | the interval lies entirely outside |
| **inconclusive** | otherwise, or the statistic could not be computed, or it used fewer than 50 states |

A criterion with several parts passes only if every part passes, and fails if any part fails. Bands are strict (open) for H2a, H2b, H2c, H2e and H3a, and closed for H1a to H1d, H2d and H3c. Endpoints are compared unrounded.

### 6.3 Overall verdict (across the three systems)

| Overall word | Rule |
|---|---|
| **supported** | pass on all three systems |
| **not supported** | fail on at least one system |
| **inconclusive** | otherwise, including a system with no result |

Requiring all three systems to pass is an *intersection–union test*, so the error rate of "supported" needs no further correction. The error rate of "not supported" is not controlled this way: with 95% intervals it can reach about 7.3% over three systems.

### 6.4 The primary statistics, in detail

All three use the core cell (ρ = 1%, N_lib = 10⁴) or its sweeps, the 1,000 test states, w\* from 200 noise draws, and 98.33% intervals.

**H2a (separation).** Two parts; both must pass.

- *(i) Horizon dependence.* For each test state, compute w\* at 1, 2 and 4 LT, up to the last horizon at which both r.m.s. errors are at most 0.5 σ_x (so the span is {1, 2} or {1, 2, 4} LT). States with fewer than two such horizons are excluded and counted. The statistic is the median over states of the range (largest minus smallest w\*). **Pass if the interval lies below 0.1.**
- *(ii) Instability dependence, given the seeds.* At H_ref, with x₁ = ln(ε_s/ρ) and x₂ = ln(δ/ρ), compute the partial correlation of Λ̃ with (a) the indicator of w\* = 0, on all test states, and (b) logit w\*, on the states with 0 < w\* < 1, controlling for x₁, x₂, x₁², x₂² and x₁x₂. **Pass if each part's interval lies inside (−0.1, 0.1).**

**H2b (interventions).** Two parts; both must pass.

- *(i) Noise.* For each test state, the Spearman rank correlation of w\*(H_ref) with ρ across the four noise levels; the statistic is the mean over states. **Pass if the lower bound > 0.**
- *(ii) Library.* For each test state, the change in w\*(H_ref) from N_lib = 10³ to 10⁴ at ρ = 1%; the statistic is the mean paired change. **Pass if the lower bound > 0.**

**H3c (regimes).** The ratio of mean squared errors at H_ref on the test states, regime lookup A5 (at the chosen K) over closed form A4. **Pass if the upper bound ≤ 1.05.**

### 6.5 The secondary statistics (95%, no multiplicity adjustment)

| ID | Statistic | Pass if |
|---|---|---|
| H1a | fit of median ε_s² to b² N_lib^(−2/d) + f² at ρ = 1% and 2%; ratio of fitted 1/d to the Levina–Bickel 1/d | ratio interval inside [0.75, 1.25], at both ρ |
| H1b | slope of log r.m.s. PLP error on log(g_H δ/√m) at H_ref | in [0.8, 1.2] |
| H1c | median of Λ̄ × dT/d ln θ (PLP; CP reported) | in [0.8, 1.25] |
| H1d | Spearman correlation of each deployable proxy with its exact value (first evaluation draw; N̂ reported, not tested) | each lower bound ≥ 0.7 |
| Q-N | out-of-sample gain in R² from adding N to the other three conditions, for logit w\* (interior states) and for the indicator of w\* = 0 | read by the table in v3 §7 (reduces / distinct but small / substantial / undetermined); never pass or fail |
| H2c | paired MSE differences at H_ref: A4 − A2, and A4 − the better single forecaster (chosen on calibration) | both upper bounds < 0 |
| H2d | MSE ratio A4/A3 minus 1 at H_ref | upper bound ≤ 0.10 |
| H2e | median per-state change in CP–PLP error correlation, N_lib 10³ → 10⁵ | lower bound > 0 at ρ = 1% and 2% |
| H3a | Holm-adjusted log-rank tests between regimes consecutive in Kaplan–Meier median horizon | all adjusted p < 0.01; otherwise inconclusive (H3a cannot fail) |
| H3b | importances of Λ̃ in an 8-leaf weight tree and an 8-leaf horizon tree | weight tree: interval inside [0, 0.2); horizon tree: lower bound of D > 0 |

The hybrid's horizon gain over the better single forecaster is reported against the P1 bound with no pass/fail bar.

### 6.6 Nothing is handled silently

Every clip, replacement, exclusion, floor and failed resample is counted and written to the `handling` block of `results.json` and to the run log, including the zero counts. The CONF-1 counters are printed in `promoted/CONF-1/report.md` §7. A clip-sensitivity check recomputes the MSE- and weight-based verdicts with the error clip at 20 σ_x instead of 10 σ_x, and reports any verdict the clip would move. It never changes a verdict.

### 6.7 Pre-registered readings of failures (v3 §7)

- If H2a fails: instability enters the weight through anisotropic seeds; the size of the departure measures how far real attractors are from the separation assumption.
- If H2c fails but A4o beats A2: the theory is right, and the deployable estimates of the seeds limit it.
- If H3c holds while excess error is flat in K: this is the P3 floor.

---

## 7. What CONF-1 returned (primary hypotheses)

All three systems passed the validation gate, so no result is PROVISIONAL. The stored verdict words (from `promoted/CONF-1/results.json`, not recomputed):

| Hypothesis | Overall word | Lorenz-63 | Rössler | Chua |
|---|---|---|---|---|
| H2a | **not supported** | fail | fail | fail |
| H2b | **supported** | pass | pass | pass |
| H3c | **inconclusive** | inconclusive | pass | inconclusive |

"Not supported" is not "disproved", and "inconclusive" does not mean "no effect". Estimates, intervals, the secondary rows and all limitations are in `promoted/CONF-1/report.md`.

---

## 8. Alignment check: design compared with what was run

**Matches the design.**

- The run used the frozen commit (`freeze-1`), the `full` preset (whose constants are those of v3), a clean worktree, the CPU and `LPC_THREADS=8`, as v3 §9 item 3 requires.
- The seed was committed in the ledger before the run, and checked by the code at start-up.
- Every hypothesis in v3 §2 has a stored statistic, interval and verdict, computed by the rules of v3 §7. The primary hypotheses map to the experiments listed in v3 §6: H2a to E4, H2b to E1 and E2, H3c to E5.
- The validation gate ran before any verdict was read, and passed everywhere.
- The GPU cross-check was run and compared by the rule of v3 §9 item 3, and changed no verdict.

**Known departures, all recorded and accepted by the owner before or at promotion** (details in `promoted/CONF-1/report.md` §10):

- **Regeneration by the same person.** v3 §9 item 4 asks for another actor to regenerate the run. The owner regenerated it on the same computer (bitwise equal); the other-actor requirement was waived (ledger entry 31). This shows determinism, not independent reproduction.
- **Iterative error of PLP not estimated.** The error left after 15 Levenberg–Marquardt iterations was measured only on a development seed; for CONF-1 it is listed as not estimated.
- **Block-sensitive label not computable.** v3 §8 describes a "block-sensitive" label; the sealed run writes no per-state dump, so it could not be computed.
- **Gain-bound screen.** Reported with the v1 statistic; the v3 screen is pending. It is reported only and carries no verdict.
- **Q-N overall word.** v3 reads Q-N's two parts separately. The stored overall word keeps the logit part only; the report prints both parts.
- **Interval level not stored for some parts.** For some parts the result file stores no level; the report shows the design value (98.33% for primaries, 95% otherwise) and says so.
- **Owner code review waived** (ledger entry 33); the code was covered by independent AI-agent reviews and the owner spot-checked the results.

---

## 9. What a replication should expect

- **Same seed, same computer, same thread count:** bitwise-equal results.
- **Same seed, different computer, thread count or device:** small numerical differences, because floating-point sums are added in a different order and the linear-algebra library differs. Results then agree statistically, not bitwise, and a verdict word near a band edge can change (the GPU cross-check of CONF-1 is an example).
- **Different seed** (any replication outside the owner's sealed run): new trajectories, noise, libraries and network weights, so new numbers. Verdicts may differ. A development-seed run is development evidence, not a test of the pre-registered hypotheses.

---

## 10. Glossary

| Term | Meaning |
|---|---|
| Attractor | the set of states a chaotic system settles onto |
| Lyapunov time (LT) | 1/λ_max, the time over which small errors grow by a factor of e; 30 observation steps here |
| Delay vector | the current measurement and six earlier ones, spaced τ steps apart |
| Seed (of an error) | a forecaster's initial error: ε_s for CP, δ for PLP |
| Seed (random) | the integer that fixes every random number in a run |
| Oracle | a quantity computed with knowledge of the true state, used only to test the theory |
| Deployable | a quantity computed from measurements only, as a real forecaster would |
| Whitened | rescaled so the state has zero mean and identity covariance on the attractor |
| Censored | a horizon not reached by the 8-LT limit; summarized by Kaplan–Meier, never by plain averages |
| Ledger | the hash-chained, append-only record of every decision (`docs/agent/governance/ledger.jsonl`) |
