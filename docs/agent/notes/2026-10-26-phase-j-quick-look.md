# WU-0048a (phase J, J3a): quick look at what R, O, I and N add to allocation

**PROTOTYPE, DEVELOPMENT (DEV-2), old code c9bb981: not a hypothesis test.** Every number in this note and in its folder carries this label. None of it is placed beside, or compared with, CONF-1. These prototype numbers are not carried into the phase J report (plan §5, WU-0048a row).

- Author: developer (claude-opus-5-5), 2026-10-26. Unit WU-0048a, plan `2026-10-26-phase-j-lpc-contribution-plan.md` (§3; experiments A, B and D of §4).
- Script and output: `2026-10-26-phase-j-quick-look/` holds `quick_look.py`, `quick_look.json` (every number), `tables.md` (every table, all 5 horizons, both profiles), `tables_key.md` (the same at 0.27, 1 and 4 LT), `quick_look.log`, and the diagnostic `overfit_check.py` with its `.json` and `.log`. Run with the project `.venv` (`python -I`), CPU, `JAX_PLATFORMS=cpu`, 4 threads, `nice -n 19`.
- Input (read only): the DEV-2 full-preset dumps `lpcstudy-wt/run/r1-c9bb981/runs/r5-gpu-dev2/full/states/{lorenz63,rossler,chua}.npz` (schema /2) and the `results.json` beside them. The run's provenance commit is 6f1a8c8. `git diff --stat c9bb981 6f1a8c8 -- lpcstudy tools` is empty, so the run's code is c9bb981.

## 1. What was done

Allocation only, at the 5 horizons in the dump (8, 15, 30, 60 and 120 steps). The first is **8 steps = 0.27 LT**, not 0.25 LT: the run rounds 0.25 × 30 = 7.5 steps to 8. Tables label it "0.27 LT".

- **Loss.** For each state, V(w) = w²E_C + (1−w)²E_P + 2w(1−w)C, exact from the oracle moments (200 draws). V\* is the minimum over [0, 1]. The excess loss of a weight rule g is L(g) = mean over the 1000 test states of [V(g) − V\*]. On the deployable profile, each state's term is averaged over its E = 4 draws. The gain share is G(g) = [V(A2) − V(g)] / [V(A2) − V\*] = 1 − L(g)/L(A2).
- **Cross-fitting.** The 1000 test states are cut, in time order, into 5 contiguous blocks of 200. Each block is predicted by models fitted on the other four. Contiguous blocks keep serial dependence away from the train/test boundary, except at the 4 block edges, where the neighboring state of a test state can be a training state. No gap was left. The dependence is weak: the lag-1 autocorrelation in time order at H_ref is at most 0.09 for u and w\*, and at most 0.19 for any profile coordinate (Rössler's O). The block bootstrap (block 5) covers more than that.
- **Learner.** `analysis.qn_regressor` (the Q-N hyperparameters: 300 iterations, rate 0.05, 15 leaves, at least 20 samples per leaf, l2 = 1). Target u = (E_P − C)/κ, sample weight κ = E_C + E_P − 2C. Since V(w) − V(w\*) = κ(w − u)² − κ(w\* − u)², this is weighted least squares on the decision loss itself. Predictions are clipped to [0, 1]. On the deployable profile the training rows are (state, draw) pairs, with the state's u and κ repeated.
- **Feature sets.** A2 (the best constant on the training folds, in closed form clip(Σ(E_P − C)/Σκ, 0, 1); it is also the empty subset), the 15 non-empty subsets of {R, O, I, N}, the additive model (`interaction_cst = [[0],[1],[2],[3]]`), the additive model with one pair allowed to interact (6 models), and the separation formula w = 1/(1 + e^{2(R−O)}) with no fit. Every set is refitted on its own inputs. That is 3300 fits in 958 s.
- **Intervals.** Moving-block bootstrap over the test states in time order (block 5, 2000 resamples, 95% percentile). The out-of-fold predictions are held fixed. One index set per system, from `make_rng(seed, "wu0048a-quick-look", system)`, is shared by every model, horizon and profile, so every comparison is paired. Ratios are read by `ablation.ratio_reading_reason` (margin 1.05, at least 50 states). Ratios are oriented simpler/richer, so a value above 1 means the richer model is better.
- **Shapley.** φ_X = Σ_{S ∌ X} |S|!(3−|S|)!/4! [L(S) − L(S ∪ X)] over the 16 subsets. The tables report φ_X / L(A2), the Shapley part of the gain share. The four parts sum to G(F). The share φ_X / (L(∅) − L(F)) is in the JSON, but it means nothing when G(F) ≤ 0, which happens often here (§3).

### Counts and checks (every cell: 3 systems × 5 horizons × 2 profiles)

- κ ≤ 1e-10 (E_C + E_P): **0 states** (they would be left out of the fit, counted, and kept in the score). The smallest κ/(E_C + E_P) is 0.04.
- Negative excess V(ŵ) − V\*: **0 entries**. The minimum is exactly 0 (states where ŵ = w\* = 0).
- Predictions clipped to [0, 1]: counted per model, horizon and profile (`clips_low_high` in the JSON; the full model's counts are in `tables.md`). Most clips are below 0. They are expected: about 15 to 30% of states have w\* = 0, and their u is negative. On the oracle profile at H_ref, the full model clips 267 (Lorenz-63), 228 (Rössler) and 233 (Chua) of 1000 predictions low, and 19, 0 and 0 high.
- Failed bootstrap resamples: **0** in every row.
- Identity checks: the κ form of the excess equals V(w) − V(w\*) to at most 5.8e-16 relative (tolerance 1e-12). w\* computed here equals the run's dumped `core/w_star` exactly (maximum difference 0). Σφ = L(∅) − L(F) holds to at most 7e-18 absolute (tolerance 1e-12).

## 2. Key tables (0.27, 1 and 4 LT)

All 5 horizons, both profiles, the MSE ratios and G for every subset are in `tables.md`. Readings: SUBST. = substantial, needed = needed, size not determined, negl. = negligible, undet. = undetermined.

### lorenz63 (oracle profile unless marked)

*PROTOTYPE, DEVELOPMENT (DEV-2), old code c9bb981: not a hypothesis test.*

Drop-one, L(F∖X)/L(F), excess loss:

| | 0.27 LT | 1 LT | 4 LT |
|---|---|---|---|
| R | 0.960 [0.699, 1.086] undet. | 1.638 [1.196, 2.323] SUBST. | 0.993 [0.912, 1.076] undet. |
| O | 0.706 [0.312, 14.924] undet. | 1.634 [0.901, 3.083] undet. | 0.951 [0.904, 1.005] negl. |
| I | 0.763 [0.034, 1.376] undet. | 1.020 [0.728, 1.333] undet. | 1.037 [0.966, 1.118] undet. |
| N | 0.942 [0.057, 1.274] undet. | 0.981 [0.782, 1.141] undet. | 0.982 [0.921, 1.048] negl. |

Shapley parts of G(F), φ_X/L(A2):

| | 0.27 LT | 1 LT | 4 LT |
|---|---|---|---|
| R | -0.13 [-0.26, -0.03] | 0.08 [-0.10, 0.25] | -0.09 [-0.17, -0.02] |
| O | -0.03 [-0.43, 0.73] | 0.39 [0.14, 0.65] | -0.13 [-0.19, -0.08] |
| I | -0.13 [-0.52, 0.32] | 0.21 [0.03, 0.38] | -0.02 [-0.08, 0.05] |
| N | 0.33 [-0.22, 0.51] | -0.17 [-0.45, 0.04] | -0.04 [-0.11, 0.02] |
| G(F) | 0.04 [-0.29, 0.97] | 0.51 [0.18, 0.74] | -0.28 [-0.43, -0.14] |

Pairs, L(additive)/L(additive + pair):

| | 0.27 LT | 1 LT | 4 LT |
|---|---|---|---|
| R×O | 1.018 [0.943, 1.129] undet. | 1.422 [1.011, 1.910] needed | 1.032 [0.986, 1.079] undet. |
| R×I | 0.949 [0.726, 1.006] negl. | 1.160 [0.999, 1.330] undet. | 1.055 [0.995, 1.115] undet. |
| R×N | 0.965 [0.582, 1.084] undet. | 1.125 [0.963, 1.275] undet. | 0.994 [0.949, 1.032] negl. |
| O×I | 0.923 [0.701, 1.659] undet. | 1.094 [0.838, 1.361] undet. | 1.030 [0.994, 1.065] undet. |
| O×N | 1.016 [0.634, 2.025] undet. | 1.063 [0.800, 1.494] undet. | 1.011 [0.967, 1.054] undet. |
| I×N | 0.958 [0.688, 1.357] undet. | 1.109 [0.973, 1.319] undet. | 1.006 [0.954, 1.060] undet. |
| ceiling L(add)/L(F) | 0.943 [0.709, 5.322] undet. | 1.630 [1.032, 2.654] needed | 1.017 [0.935, 1.097] undet. |

D ladder, gain share G (oracle; deployable in the last three rows):

| | 0.27 LT | 1 LT | 4 LT |
|---|---|---|---|
| separation formula | 0.56 [0.27, 0.98] | 0.64 [0.43, 0.81] | -0.30 [-0.46, -0.15] |
| {R, O} learned | 0.12 [-0.21, 0.88] | 0.50 [0.21, 0.70] | -0.35 [-0.50, -0.21] |
| full F | 0.04 [-0.29, 0.97] | 0.51 [0.18, 0.74] | -0.28 [-0.43, -0.14] |
| separation formula, deployable | -0.24 [-1.52, 0.48] | -0.10 [-0.22, 0.04] | -0.19 [-0.26, -0.12] |
| {R, O} learned, deployable | -0.14 [-0.42, 0.43] | 0.01 [-0.33, 0.28] | -0.21 [-0.32, -0.11] |
| full F, deployable | 0.29 [-0.08, 0.61] | 0.25 [-0.14, 0.53] | -0.18 [-0.29, -0.08] |
| L(A2) | 0.0227 | 0.0345 | 0.29 |

### rossler (oracle profile unless marked)

*PROTOTYPE, DEVELOPMENT (DEV-2), old code c9bb981: not a hypothesis test.*

Drop-one, L(F∖X)/L(F), excess loss:

| | 0.27 LT | 1 LT | 4 LT |
|---|---|---|---|
| R | 1.237 [1.178, 1.305] SUBST. | 2.291 [1.843, 2.874] SUBST. | 1.019 [0.953, 1.085] undet. |
| O | 1.040 [1.015, 1.065] needed | 1.344 [1.199, 1.507] SUBST. | 1.041 [0.983, 1.097] undet. |
| I | 0.992 [0.985, 0.998] lowers | 0.985 [0.955, 1.012] negl. | 1.020 [0.938, 1.096] undet. |
| N | 1.028 [0.998, 1.058] undet. | 1.054 [0.987, 1.128] undet. | 0.953 [0.877, 1.025] negl. |

Shapley parts of G(F), φ_X/L(A2):

| | 0.27 LT | 1 LT | 4 LT |
|---|---|---|---|
| R | 0.22 [0.18, 0.26] | 0.49 [0.38, 0.62] | -0.05 [-0.13, 0.03] |
| O | 0.01 [-0.00, 0.02] | -0.01 [-0.11, 0.07] | -0.05 [-0.12, -0.00] |
| I | -0.01 [-0.02, 0.00] | -0.01 [-0.06, 0.05] | -0.01 [-0.09, 0.06] |
| N | 0.10 [0.07, 0.13] | 0.06 [-0.04, 0.14] | -0.11 [-0.20, -0.03] |
| G(F) | 0.33 [0.29, 0.37] | 0.53 [0.45, 0.60] | -0.22 [-0.37, -0.09] |

Pairs, L(additive)/L(additive + pair):

| | 0.27 LT | 1 LT | 4 LT |
|---|---|---|---|
| R×O | 1.045 [1.026, 1.065] needed | 1.398 [1.223, 1.604] SUBST. | 0.988 [0.946, 1.036] negl. |
| R×I | 1.002 [0.994, 1.010] negl. | 1.011 [0.953, 1.073] undet. | 0.991 [0.946, 1.037] negl. |
| R×N | 1.018 [1.004, 1.035] small | 1.057 [1.003, 1.117] needed | 0.976 [0.914, 1.043] negl. |
| O×I | 0.999 [0.998, 1.000] lowers | 1.039 [0.991, 1.088] undet. | 1.010 [0.962, 1.056] undet. |
| O×N | 1.007 [1.001, 1.013] small | 0.998 [0.952, 1.046] negl. | 0.997 [0.946, 1.050] negl. |
| I×N | 0.999 [0.993, 1.005] negl. | 1.085 [1.012, 1.210] needed | 0.974 [0.926, 1.022] negl. |
| ceiling L(add)/L(F) | 1.049 [1.028, 1.067] needed | 1.420 [1.216, 1.688] SUBST. | 0.962 [0.893, 1.039] negl. |

D ladder, gain share G (oracle; deployable in the last three rows):

| | 0.27 LT | 1 LT | 4 LT |
|---|---|---|---|
| separation formula | 0.11 [-0.05, 0.24] | 0.51 [0.40, 0.59] | -0.16 [-0.26, -0.03] |
| {R, O} learned | 0.31 [0.27, 0.35] | 0.52 [0.44, 0.59] | -0.17 [-0.28, -0.08] |
| full F | 0.33 [0.29, 0.37] | 0.53 [0.45, 0.60] | -0.22 [-0.37, -0.09] |
| separation formula, deployable | -0.30 [-0.51, -0.14] | -0.05 [-0.23, 0.11] | -0.25 [-0.35, -0.13] |
| {R, O} learned, deployable | 0.10 [0.04, 0.15] | -0.12 [-0.47, 0.14] | -0.10 [-0.20, -0.02] |
| full F, deployable | 0.10 [0.05, 0.15] | -0.25 [-0.81, 0.10] | -0.11 [-0.20, -0.04] |
| L(A2) | 2.14e-05 | 0.000151 | 0.0294 |

### chua (oracle profile unless marked)

*PROTOTYPE, DEVELOPMENT (DEV-2), old code c9bb981: not a hypothesis test.*

Drop-one, L(F∖X)/L(F), excess loss:

| | 0.27 LT | 1 LT | 4 LT |
|---|---|---|---|
| R | 1.681 [0.940, 3.154] undet. | 1.107 [0.935, 1.380] undet. | 1.079 [0.990, 1.171] undet. |
| O | 0.872 [0.551, 1.111] undet. | 1.064 [0.763, 1.421] undet. | 1.145 [1.074, 1.224] SUBST. |
| I | 1.128 [0.978, 1.385] undet. | 0.970 [0.628, 1.433] undet. | 1.028 [0.962, 1.098] undet. |
| N | 1.208 [0.888, 1.809] undet. | 1.424 [0.976, 2.242] undet. | 0.901 [0.843, 0.961] lowers |

Shapley parts of G(F), φ_X/L(A2):

| | 0.27 LT | 1 LT | 4 LT |
|---|---|---|---|
| R | 0.40 [0.07, 1.23] | -0.03 [-0.31, 0.22] | 0.00 [-0.07, 0.07] |
| O | -0.29 [-1.08, 0.04] | -0.11 [-0.78, 0.23] | 0.03 [-0.03, 0.09] |
| I | -0.05 [-0.27, 0.14] | -0.14 [-0.73, 0.17] | -0.01 [-0.07, 0.04] |
| N | 0.07 [-0.44, 0.48] | 0.05 [-0.25, 0.49] | -0.13 [-0.19, -0.08] |
| G(F) | 0.13 [-0.24, 0.40] | -0.24 [-1.17, 0.19] | -0.11 [-0.21, -0.00] |

Pairs, L(additive)/L(additive + pair):

| | 0.27 LT | 1 LT | 4 LT |
|---|---|---|---|
| R×O | 0.906 [0.771, 1.016] negl. | 1.064 [0.904, 1.256] undet. | 1.162 [1.096, 1.231] SUBST. |
| R×I | 1.094 [1.020, 1.284] needed | 0.976 [0.852, 1.131] undet. | 1.069 [1.023, 1.122] needed |
| R×N | 1.113 [0.994, 1.367] undet. | 0.964 [0.859, 1.099] undet. | 0.959 [0.916, 1.001] negl. |
| O×I | 0.875 [0.626, 1.095] undet. | 0.823 [0.721, 0.945] lowers | 0.991 [0.951, 1.032] negl. |
| O×N | 0.734 [0.463, 1.082] undet. | 1.104 [0.832, 1.482] undet. | 1.004 [0.955, 1.057] undet. |
| I×N | 1.049 [0.900, 1.368] undet. | 1.084 [0.923, 1.295] undet. | 0.978 [0.938, 1.016] negl. |
| ceiling L(add)/L(F) | 1.090 [0.945, 1.310] undet. | 1.269 [0.998, 1.656] undet. | 1.081 [0.990, 1.185] undet. |

D ladder, gain share G (oracle; deployable in the last three rows):

| | 0.27 LT | 1 LT | 4 LT |
|---|---|---|---|
| separation formula | 0.35 [-0.10, 0.54] | 0.10 [0.01, 0.28] | -0.18 [-0.27, -0.08] |
| {R, O} learned | -0.09 [-0.83, 0.28] | -0.52 [-1.39, -0.12] | -0.02 [-0.11, 0.07] |
| full F | 0.13 [-0.24, 0.40] | -0.24 [-1.17, 0.19] | -0.11 [-0.21, -0.00] |
| separation formula, deployable | -0.30 [-0.91, -0.07] | -0.02 [-0.13, 0.09] | -0.22 [-0.31, -0.13] |
| {R, O} learned, deployable | -0.27 [-1.04, 0.09] | -0.88 [-2.70, 0.02] | -0.11 [-0.19, -0.03] |
| full F, deployable | -1.02 [-4.13, 0.06] | -0.80 [-2.57, -0.12] | -0.08 [-0.16, -0.00] |
| L(A2) | 0.000104 | 0.00677 | 0.171 |


## 3. What does not work on this data (the main finding of the quick look)

**The learned allocator mostly fails to beat a constant weight out of fold.** On the oracle profile, G(F) is clearly positive only for Rössler from 0.27 to 1 LT, and for Lorenz-63 at 0.5 and 1 LT. Elsewhere it is near 0 or negative. At 4 LT it is negative on all three systems, as is the separation formula. A drop-one ratio or a Shapley share of a model that loses to A2 describes the learner, not the conditions. So the A and B readings above are interpretable only in those cells.

`overfit_check.py` (oracle profile; output in `overfit_check.log` and `.json`) gives two reasons:

1. **The decision loss sits on a few states.** The weight κ is very heavy-tailed at short horizons. The Kish effective sample size (Σκ)²/Σκ² of the 1000 test states is:

   | | 0.27 LT | 0.5 LT | 1 LT | 2 LT | 4 LT |
   |---|---|---|---|---|---|
   | Lorenz-63 | 11 | 27 | 51 | 136 | 414 |
   | Rössler | 128 | 108 | 127 | 121 | 405 |
   | Chua | 7 | 16 | 48 | 217 | 467 |

   The top 1% of states hold 65% (Lorenz-63) and 81% (Chua) of Σκ at 0.27 LT. The fitted A2 constant itself moves from 0.40 to 0.82 across the five Lorenz-63 training sets at 0.27 LT. In MSE terms, allocation at short horizons on Lorenz-63 and Chua comes down to about ten states.
2. **The Q-N learner overfits at 800 training states.** In-sample G of the full model is 0.67 to 1.00 in every Lorenz-63 and Chua cell, against out-of-fold G of −0.69 to 0.85. A much more regularized learner (50 iterations, 4 leaves, at least 100 states per leaf; a sensitivity, not the plan's learner) removes most of the negative G: out-of-fold G of the full profile at 4 LT is −0.01, 0.08 and 0.04 (Lorenz-63, Rössler, Chua), against −0.28, −0.22 and −0.11. It also lowers G where the Q-N learner worked (Rössler at 1 LT: 0.32 against 0.53). Model complexity therefore needs choosing, for example by inner cross-validation on the training folds.

Other points:

- **The separation formula is a strong baseline.** It has no fit, so it cannot overfit. On the oracle profile it matches or beats the best of the 15 learned subsets on Lorenz-63 from 0.27 to 2 LT (G = 0.56, 0.89, 0.64 and 0.08, against 0.56, 0.90, 0.52 and −0.10) and on Chua from 0.27 to 2 LT. On Rössler it ties the full profile at 1 LT (0.51 against 0.53) and beats every learned set at 2 LT (0.40 against 0.23). It loses to A2 at 4 LT on all three systems (G between −0.16 and −0.30). That is consistent with separation breaking down at long horizons.
- **Deployable profile.** The separation formula on the deployable coordinates has a negative G point estimate in 13 of the 15 cells. Unlike A4, it has no fitted proxy coefficients, so this is not A4's performance. The learned deployable models are erratic (Chua's full F at 0.27 LT: G = −1.02 [−4.13, 0.06]). With the deployable draws as training rows, each state contributes 4 rows with the same target, so `min_samples_leaf = 20` is effectively 5 states.
- **B on the u scale picks up the link.** The task asked for B on the same loss as A (u with weight κ). On that scale, the separation formula makes R and O "interact" through the logistic link alone (plan DS-3). The R×O rows (Rössler at 1 LT: 1.40 [1.22, 1.60] substantial; Lorenz-63 at 1 LT: needed) are therefore expected under pure separation and are not evidence of a mechanism. The plan's B uses the logit w\* scale for this reason. Holm over the 6 pairs was not applied in this quick look.
- **Excess-loss ratios against MSE ratios.** The 1.05 margin of `ratio_reading` was set for ratios of MSE. A ratio of excess losses is a much more sensitive scale: the same model change gives a ratio further from 1. The quick look reports both for drop-one (`tables.md`). For example, Rössler O at 0.27 LT reads "needed" on the excess scale (1.040) and "small" on the MSE scale (1.005). WU-0045 (M-1/M-2) should say which scale the margin applies to.

## 4. What the interpretable cells say

These are prototype estimates, not readings for the report.

- **Rössler, 0.27 to 1 LT (oracle).** R carries most of the gain: its Shapley part is 0.22 of G(F) = 0.33 at 0.27 LT, and 0.49 of 0.53 at 1 LT. N is second at short horizons (0.10 at 0.27 and at 0.5 LT). O's drop-one is substantial at 1 LT (1.34 [1.20, 1.51]), but its Shapley part is about 0. O is needed only together with R, which is what the separation formula's dependence on R − O predicts. I is negligible or "lowers" at every horizon up to 1 LT. {R, O} learned recovers nearly all of the full profile's gain (L(RO)/L(F) undetermined, point estimates 1.02 to 1.03).
- **Lorenz-63, 1 LT (oracle).** G(F) = 0.51 [0.18, 0.74], below the separation formula's 0.64 [0.43, 0.81]. The Shapley parts are O 0.39, I 0.21, R 0.08 and N −0.17. R's drop-one is substantial (1.64), O's is undetermined.
- **Against the plan's predictions (§4 A, oracle).** "R and O carry most of the value at 0.25 to 1 LT": consistent on Rössler and at Lorenz-63 1 LT. "I's drop-one grows with horizon and is not negligible at 2 to 4 LT": not determinable here, because no learned model beats A2 at 4 LT, and at 2 LT G(F) is −0.29 (Lorenz-63), 0.22 (Rössler) and 0.08 (Chua). The B prediction for R×I and O×I at 2 to 4 LT cannot be read from this learner on this data.

## 5. Suggestions for WU-0045 and WU-0048

These are suggestions only; the plan is not changed here.

1. Report the Kish effective sample size of κ with every allocation row, and read rows with n_eff < 50 as undetermined (by analogy with the 50-state rule). Alternatively, add a per-state normalized loss (for example V(g)/V(A2) per state, averaged) as a secondary scale (M-1/M-2).
2. Choose the learner's complexity by inner cross-validation on the training data, or use a fixed, much more regularized learner. With construction + calibration (3000 states), n_eff will be about 3.75 times larger, which is still about 25 to 40 at 0.27 LT for Lorenz-63 and Chua.
3. Keep the separation formula as rung 2 of D. It is the bar any learned rule has to clear at short horizons.
4. For B, use the logit scale as planned (DS-3). On the u scale, R×O mostly reflects the link.
5. On the deployable profile, set `min_samples_leaf` in states, not rows, or train on the per-state mean of the draws.

## 6. Reproduce

```
cd docs/agent/notes/2026-10-26-phase-j-quick-look
JAX_PLATFORMS=cpu OMP_NUM_THREADS=4 nice -n 19 <repo>/.venv/bin/python -I quick_look.py --out . --deployable-pairs   # 958 s
JAX_PLATFORMS=cpu OMP_NUM_THREADS=4 nice -n 19 <repo>/.venv/bin/python -I overfit_check.py                          # ~3 min
python -I quick_look.py --out . --render-only   # rewrite tables.md and tables_key.md from the JSON
```
