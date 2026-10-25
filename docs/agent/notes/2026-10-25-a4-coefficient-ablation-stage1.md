# WU-0036: A4 coefficient ablation, stage 1 (offline, existing dumps)

**DEVELOPMENT (DEV-1, DEV-2): not a hypothesis test.** Every number in this note carries this label. None of it is placed beside, or compared with, the sealed CONF-1 result.

- Author: applied-mathematician (claude-opus-5-5), 2026-10-25. Unit WU-0036, ROADMAP.md §9 (phase I, P1).
- Script and output: `docs/agent/notes/2026-10-25-a4-coefficient-ablation-stage1/` (`a4_ablation.py`, run with the project `.venv` interpreter, `python3 -I`, CPU, one thread, `nice -n 19`). Stage `tolerance` never reads `state_mse/`; stage `full` does.
- Inputs: the DEV-1 pilot dumps (`r1-gpu-dev1/pilot/states/*.npz`, run commit 01d9fc7) and the DEV-2 full dumps (`r5-gpu-dev2/full/states/*.npz`, run commit 6f1a8c8), with their `results.json`. `git diff 01d9fc7 c9bb981 -- lpcstudy/` and `git diff 6f1a8c8 c9bb981 -- lpcstudy/` are both empty, so the A4 code of c9bb981 is the code of both runs.

## 1. A4 and its reconstruction from the dump

At c9bb981 (`allocation.py`): `nu = min(nu_hat, nu_cap)`, `eps_hat^2 = a (R nu)^2 + b (rho nu)^2`, `delta_hat^2 = a' (rho nu)^2 + b' rho^2`, `w = delta_hat^2 / max(eps_hat^2 + delta_hat^2, 1e-300)`, with `(a, b) = fitted/analog_proxy/(slope, floor)`, `(a', b') = fitted/estimation_proxy/(slope, floor)`, `rho = config/core_noise = 0.01`. The A4 weight does not depend on the horizon (`pipeline.rule_weights` broadcasts it).

The dump does not hold `nu` per evaluation draw. It holds `R` and the profile `(ln eps_hat/rho, ln delta_hat/rho, ...)`. The script recovers

`nu^2 = rho^2 exp(2 F_1) / (a R^2 + b rho^2)`

from the analog coordinate (a sum of positive terms: no cancellation, relative conditioning 1). It then checks, each at 1e-12 relative:

1. **Independent consistency:** `a' (rho nu)^2 + b' rho^2` against `rho^2 exp(2 F_2)`. The estimation coordinate is not used to recover `nu`, so this tests `R`, `rho`, the four coefficients and the formula together.
2. The A4 weight by the package's code path (sqrt, square, floor) against `weight_href/A4`.
3. The simplified hand formula `(a' nu^2 + b') / (nu^2 (a (R/rho)^2 + b) + a' nu^2 + b')` against that code path.
4. No recovered `nu` above `nu_cap`.

Round-off scale: `exp(2 F)` with `|2F|` of order 10 carries about `10 u ≈ 2e-15` relative error (`u = 1.1e-16`), so 1e-12 leaves a margin of about 500.

## 2. Approximation check: tolerance fixed before the stored score was read

### 2.1 What is compared

For state `i` and evaluation draw `j = 1..E` at `H_ref = 30` steps:

- **Stored:** `S_i = state_mse/A4[i, ref] = (1/E) sum_j (w_ij e_C,ij + (1 - w_ij) e_P,ij)^2`, the realized errors of the evaluation draws (`pipeline.score_rules`).
- **Reconstructed:** `Q_i = (1/E) sum_j V_i(w_ij)` with `V_i(w) = w^2 E_C + (1-w)^2 E_P + 2 w (1-w) C`, the moments of the `M = 200` oracle draws.
- `D_i = S_i - Q_i`.

### 2.2 Hypotheses under which `E[D_i] = 0`

- **(H1) Same draw law.** The evaluation and oracle draws are independent noise realizations of the same state, with the same forecasters and the same clip. Both use `clip_errors`. The test-split clip counts at `H_ref` are reported by the script, and they are 0 in all six cells.
- **(H2) Weight independent of the draw's own errors.** `w_ij` is a function of `R_ij` and `nu_hat_ij`, and those come from the same noisy window as `e_C,ij` and `e_P,ij`. So (H2) does **not** hold exactly. `E[S_i] - E[Q_i] = E_j[(w_j e_C + (1-w_j) e_P)^2] - E_j[V_i(w_j)]` is a covariance between the weight and the squared error, the *dependence bias*. Its size is not knowable from the dumps beforehand. The check is therefore partly a test of whether this bias is detectable at the available precision. If it is, the oracle-moment V of a variant does not stand in for its realized score, and stage 1 should report nothing. The proxies are fitted on the construction split, so `w_ij` does not depend on the oracle draws. Given `w`, `V_hat_i(w)` is therefore unbiased for `V_i(w)`.
- **(H3) Independence across states.** Given the test states, the noise of different states is independent. Moving-block bootstrap SEs of mean D are reported as a diagnostic only.
- **(H4) Finite fourth moments** of the errors at `H_ref`, so the variances below exist.

### 2.3 Expected size

**Per state.** With Gaussian errors, one squared error has relative SD `sqrt(2)`. So `S_i` has relative SD about `sqrt(2/E)`: 100% for the pilot (E = 2) and 71% for the full preset (E = 4). The oracle term adds `sqrt(2/M) = 10%`. A per-state tolerance would be useless, so **the check is on the mean over states, per system and run (six cells).**

**On the mean.** I make no Gaussian assumption. The per-draw variance `sigma_i^2(w)` of one squared error is estimated from the two half-draw moment sets in the dump (`_A`, `_B`, 100 draws each) as `(V_A(w) - V_B(w))^2 / (1/M_A + 1/M_B)`. This captures the real kurtosis. Then:

- `Var S_i = sum_j sigma_i^2(w_ij) / E^2`;
- `Var Q_i = (Q_A,i - Q_B,i)^2 / (1/M_A + 1/M_B) / M` (the E weights share the oracle draws);
- `SE = sqrt(sum_i Var D_i) / n`.

These use only the oracle moments and the weights. The stored score is not read.

### 2.4 Tightening: a paired check

Most A4 weights are near 0 (see `mean_Q` of A4 against A1 below). So `S(A4) - S(A1)` cancels most of the realized-noise term, and `D(A4) - D(A1)` tests the weight-dependent part, which is where a dependence bias would sit, with 2 to 6 times smaller relative SE. I add it as a second gating check, with the same rule and the same variance construction applied to `V(w) - V(0)`. This tightens the ROADMAP criterion and loosens nothing.

`A0` (w = 1), `A1` (w = 0), `A4o` (weight from the oracle seeds, constant per state) and `A4o - A1` are run as **controls**, under the same rule, reported and not gating. Their weights do not depend on the draw, so (H2) holds for them exactly, and they isolate (H1) and the bookkeeping.

### 2.5 The rule (fixed now)

**Pass iff `|mean_i D_i| <= 4 SE`, for both `A4` and `A4-A1`, in every one of the six cells (12 gating tests).**

Why `z = 4`:

- Under normality of the mean, the false-fail rate is 6.3e-5 per test and about 8e-4 for the family of 12.
- The margin over `z = 3` covers the error of the SE estimate itself. Each state's variance estimate has one degree of freedom, and the sum is dominated by a few states (`n_eff_var` 2 to 21, below). The relative error of the estimated variance is about `sqrt(2/n_eff_var)`, so the SE can be off by a factor of about 1.5 to 2.
- An SE underestimated by a factor of 2 still leaves an effective `z = 2`.
- I do not go above 4. That would make the check unable to see a dependence bias of the size that matters for the ablation ratios.

Limitation stated now: with `n_eff_var` this small, the check has low power against a bias below about 10% to 25% of `V(A4)` (the `A4-A1` relative tolerances). A pass means "no bias detectable at this precision". It does not mean "no bias".

### 2.6 Tolerance table (stage `tolerance`, before `state_mse/` was read)

DEVELOPMENT (DEV-1, DEV-2): not a hypothesis test. `rel tol` = `4 SE / mean V(rule)`.

| Cell | n | E | A4 tol (rel) | A4-A1 tol (rel) | n_eff_var A4 / A4-A1 |
| --- | --- | --- | --- | --- | --- |
| DEV-1 pilot lorenz63 | 500 | 2 | 2.90e-2 (0.47) | 7.27e-3 (0.12) | 9.3 / 1.9 |
| DEV-1 pilot rossler | 500 | 2 | 2.71e-4 (0.34) | 1.74e-4 (0.22) | 21.3 / 10.0 |
| DEV-1 pilot chua | 500 | 2 | 1.70e-2 (0.73) | 6.14e-3 (0.26) | 4.4 / 4.5 |
| DEV-2 full lorenz63 | 1000 | 4 | 2.95e-2 (0.44) | 7.59e-3 (0.11) | 9.9 / 3.0 |
| DEV-2 full rossler | 1000 | 4 | 1.42e-4 (0.18) | 7.23e-5 (0.09) | 15.5 / 19.2 |
| DEV-2 full chua | 1000 | 4 | 1.34e-2 (0.73) | 2.15e-3 (0.12) | 3.4 / 5.6 |

Units: those of `state_mse` (squared forecast error of the observable, as stored). The full values are in `a4_ablation_tolerance.json`.

## 3. Results (stage `full`)

**DEVELOPMENT (DEV-1, DEV-2): not a hypothesis test.** This covers every number in §§3 to 6. Source: `a4_ablation_full.json` and `a4_ablation_full.log`. The script is unchanged since the tolerance commit 882eb23.

### 3.1 Reconstruction (1e-12 relative): passed in all six cells

| Check | Max over the six cells |
| --- | --- |
| `delta_hat^2` from the recovered `nu` against the profile | 1.5e-15 |
| reconstructed A4 weight against `weight_href/A4` | 1.1e-15 |
| hand formula against the code path, unchanged A4 | 1.0e-15 |
| hand formula against the code path, each of the four variants (asserted) | 1.0e-15 |
| recovered `nu` above `nu_cap` | 0 entries |
| recomputed `w*` against the stored `w_star` (absolute) | 0 |

Draws at the cap, for information: 16 to 21 of 1000 (DEV-1) and 31 to 58 of 4000 (DEV-2). Clipped errors at `H_ref` in the test split, evaluation and oracle draws: 0 in every cell.

### 3.2 Approximation check: passed in all six cells (12 of 12 gating tests)

DEVELOPMENT (DEV-1, DEV-2): not a hypothesis test. `z = mean D / SE` (SE from the halves, §2.3). The rule is `|z| <= 4`. `rel D = mean D / mean V(rule)`.

| Cell | A4: rel D, z | A4-A1 (paired): rel D, z | controls A0 / A1 / A4o / A4o-A1: z |
| --- | --- | --- | --- |
| DEV-1 pilot lorenz63 | +0.385, +3.29 | -0.008, -0.27 | +0.10 / +2.97 / -0.51 / -3.71 |
| DEV-1 pilot rossler | -0.046, -0.55 | +0.044, +0.81 | -1.75 / -1.03 / -1.38 / -0.21 |
| DEV-1 pilot chua | +0.025, +0.14 | +0.041, +0.63 | +1.43 / -0.07 / -0.06 / +0.05 |
| DEV-2 full lorenz63 | +0.071, +0.65 | +0.008, +0.27 | +0.63 / +0.51 / -0.40 / -1.18 |
| DEV-2 full rossler | +0.058, +1.28 | +0.044, +1.90 | -0.34 / +0.32 / +0.71 / +0.62 |
| DEV-2 full chua | +0.232, +1.26 | +0.030, +1.02 | +1.13 / +1.04 / +1.20 / +0.40 |

Reading:

- **The paired check, which carries the weight-dependent part and so any dependence bias (H2), is small everywhere:** `|rel D| <= 4.4%`, `|z| <= 1.9`.
- **One cell is close to the bound: DEV-1 pilot lorenz63, A4 direct, z = +3.29.**
  - The same excess appears in the control A1 (z = +2.97), whose weight does not depend on the draw, so (H2) cannot cause it.
  - It cancels in the pair (z = -0.27).
  - So it is a realized-PLP-error excess shared by A4 and A1, not an A4 effect.
  - The diagnostic block-bootstrap SE of mean D is 1.8 times the half-draw SE in that cell (1.31e-2 against 7.26e-3; with it, z = 1.8). This is the SE underestimate at small `n_eff_var` that §2.5 anticipated. It passes under the fixed rule, and I report it as close to the bound.
- **Conclusion:** at this precision, the oracle-moment V of a weight stands in for its realized stored score. So the ablation numbers below are reported. Section 2.5 states the power limitation of the check.

### 3.3 Fitted coefficients (the variants are not refitted)

DEVELOPMENT (DEV-1, DEV-2): not a hypothesis test. Values from `fitted/` of each `results.json`. The fit is on the construction split, `rho = 0.01`.

| Cell | a | b | a′ | b′ | a / a′ |
| --- | --- | --- | --- | --- | --- |
| DEV-1 pilot lorenz63 | 0.27134 | 9.9e-13 | 1.09046 | 6.668e-3 | 0.249 |
| DEV-1 pilot rossler | 0.24552 | 9.3e-13 | 1.00041 | 9.7e-13 | 0.245 |
| DEV-1 pilot chua | 0.26399 | 5.6e-12 | 0.98743 | 7.196e-2 | 0.267 |
| DEV-2 full lorenz63 | 0.28305 | 1.4e-7 | 1.04533 | 9.048e-3 | 0.271 |
| DEV-2 full rossler | 0.25811 | 4.1e-9 | 0.99693 | 1.0e-15 | 0.259 |
| DEV-2 full chua | 0.27537 | 4.9e-14 | 0.99185 | 7.577e-2 | 0.278 |

**`b` is at the boundary of its domain (the log-scale fit drives it to about 0) in all six cells, and so is `b′` for Rössler in both runs.**

### 3.4 Ablation: ratios against the unchanged A4 at `H_ref`

DEVELOPMENT (DEV-1, DEV-2): not a hypothesis test.

- **Interval:** paired moving-block bootstrap over test states in time order, block 5, 2000 resamples, percentile, level `1 - 0.05/3`, one shared index set per cell for all eight statistics, `make_rng(seed, "wu0036", system, "ablation-ratio")`. No failed resample.
- **Ratios:** mean over states of the draw-averaged `V`, and of the draw-averaged exact excess `V(w) - V(w*)`.
- **Crossing:** the share of states whose draw-mean weight changes side of 0.5, and the same per (state, draw).

| Cell | Coef | ratio of mean V [CI] | ratio of mean excess [CI] | states crossing 0.5 | draws crossing 0.5 | mean w, variant (A4) |
| --- | --- | --- | --- | --- | --- | --- |
| DEV-1 pilot lorenz63 | a | 1.3119 [0.5950, 3.7660] | 1.3406 [0.5739, 4.2408] | 1.000 | 0.995 | 1.0000 (0.1170) |
| DEV-1 pilot lorenz63 | b | 1.00000 [1.00000, 1.00000] | 1.00000 [1.00000, 1.00000] | 0.000 | 0.000 | 0.1170 (0.1170) |
| DEV-1 pilot lorenz63 | a′ | 1.0544 [1.0135, 1.1206] | 1.0594 [1.0149, 1.1376] | 0.000 | 0.005 | 0.0004 (0.1170) |
| DEV-1 pilot lorenz63 | b′ | 1.00011 [0.99998, 1.00031] | 1.00012 [0.99998, 1.00034] | 0.000 | 0.000 | 0.1167 (0.1170) |
| DEV-1 pilot rossler | a | 10.3709 [6.7660, 17.6673] | 46.5808 [27.4107, 83.1693] | 0.998 | 0.981 | 1.0000 (0.1833) |
| DEV-1 pilot rossler | b | 1.00000 [1.00000, 1.00000] | 1.00000 [1.00000, 1.00000] | 0.000 | 0.000 | 0.1833 (0.1833) |
| DEV-1 pilot rossler | a′ | 1.0078 [0.9468, 1.0762] | 1.0381 [0.7566, 1.3994] | 0.002 | 0.019 | 0.0000 (0.1833) |
| DEV-1 pilot rossler | b′ | 1.00000 [1.00000, 1.00000] | 1.00000 [1.00000, 1.00000] | 0.000 | 0.000 | 0.1833 (0.1833) |
| DEV-1 pilot chua | a | 3.1025 [1.1689, 9.4638] | 4.3004 [1.1978, 43.3230] | 0.994 | 0.992 | 1.0000 (0.1708) |
| DEV-1 pilot chua | b | 1.00000 [1.00000, 1.00000] | 1.00000 [1.00000, 1.00000] | 0.000 | 0.000 | 0.1708 (0.1708) |
| DEV-1 pilot chua | a′ | 1.0598 [1.0189, 1.1793] | 1.0939 [1.0236, 1.8303] | 0.006 | 0.008 | 0.0027 (0.1708) |
| DEV-1 pilot chua | b′ | 0.99987 [0.9992, 1.00012] | 0.99980 [0.9961, 1.00021] | 0.002 | 0.000 | 0.1692 (0.1708) |
| DEV-2 full lorenz63 | a | 3.0587 [1.9359, 5.0527] | 4.6893 [2.5287, 9.2425] | 1.000 | 0.994 | 1.0000 (0.1131) |
| DEV-2 full lorenz63 | b | 1.00000 [1.00000, 1.00000] | 1.00000 [1.00000, 1.00000] | 0.000 | 0.000 | 0.1131 (0.1131) |
| DEV-2 full lorenz63 | a′ | 1.0875 [1.0161, 1.1892] | 1.1568 [1.0322, 1.3056] | 0.000 | 0.006 | 0.0006 (0.1131) |
| DEV-2 full lorenz63 | b′ | 1.00009 [0.99990, 1.00026] | 1.00016 [0.99979, 1.00042] | 0.000 | 0.000 | 0.1128 (0.1131) |
| DEV-2 full rossler | a | 9.6847 [7.9985, 11.5246] | 44.2096 [35.6366, 54.4260] | 0.999 | 0.986 | 1.0000 (0.1688) |
| DEV-2 full rossler | b | 1.00000 [1.00000, 1.00000] | 1.00000 [1.00000, 1.00000] | 0.000 | 0.000 | 0.1688 (0.1688) |
| DEV-2 full rossler | a′ | 0.9989 [0.9549, 1.0438] | 0.9943 [0.7807, 1.2258] | 0.001 | 0.015 | 0.0000 (0.1688) |
| DEV-2 full rossler | b′ | 1.00000 [1.00000, 1.00000] | 1.00000 [1.00000, 1.00000] | 0.000 | 0.000 | 0.1688 (0.1688) |
| DEV-2 full chua | a | 7.0436 [4.6843, 11.8309] | 16.9950 [9.0937, 39.3229] | 1.000 | 0.988 | 1.0000 (0.1622) |
| DEV-2 full chua | b | 1.00000 [1.00000, 1.00000] | 1.00000 [1.00000, 1.00000] | 0.000 | 0.000 | 0.1622 (0.1622) |
| DEV-2 full chua | a′ | 1.0097 [0.9627, 1.0617] | 1.0256 [0.8744, 1.1711] | 0.000 | 0.012 | 0.0025 (0.1622) |
| DEV-2 full chua | b′ | 0.9992 [0.9980, 0.99994] | 0.9980 [0.9938, 0.99987] | 0.000 | 0.000 | 0.1607 (0.1622) |

**Unchanged A4, for scale** (DEVELOPMENT (DEV-1, DEV-2): not a hypothesis test). Mean V, then mean excess, at `H_ref`:

- DEV-1: lorenz63 6.20e-2 and 5.68e-2; rossler 8.02e-4 and 1.65e-4; chua 2.33e-2 and 1.49e-2.
- DEV-2: lorenz63 6.77e-2 and 3.78e-2; rossler 7.84e-4 and 1.58e-4; chua 1.83e-2 and 6.92e-3.

The mean weight is 0.11 to 0.18, and at most 0.6% of states have a draw-mean weight above 0.5.

### 3.5 What the variants are, algebraically

Because `b` is about 0 (§3.3), with the other coefficients fixed:

- **Without `a`:** `eps_hat^2 = b (rho nu)^2`, about 0, so `w = 1 - O(b / a′)`. **The variant is CP alone (A0)**, and its ratio is `mean V(A0) / mean V(A4)`.
- **Without `b`:** the weight changes by at most `b / (a (R/rho)^2)` relative: max |Δw| = 8.4e-8 (DEV-2 lorenz63, `b = 1.4e-7`) and at most 3e-9 in the other cells. Every ratio is within 3e-9 of 1. **The ratio is 1 by construction**, and it says nothing about the role of an analog floor, because the fit has already removed it.
- **Without `a′`:** `w = b′ / (nu^2 (a (R/rho)^2 + b) + b′)`, mean 0 to 0.003, max 0.048. **The variant is nearly PLP alone (A1)**, and for Rössler, where `b′` is about 0, the max weight is 2.4e-12.
- **Without `b′`:** `nu` cancels, `w = 1 / (1 + (a/a′)(R/rho)^2)`, with `a/a′ = 0.245` to `0.278`. This is the v3 known-limitation form. The ratios within 8e-4 of 1 confirm that `nu_hat` hardly enters A4 in these runs, even where `b′` is not 0 (Lorenz, Chua: max |Δw| = 2.4e-3 to 1.3e-2).

So stage 1 compares A4 with A0, with nearly A1, with itself, and with its own `nu`-free form. Without a refit, it does not measure what each term contributes to a re-optimised allocator. That is stage 2 (WU-0039).

## 4. The predictions, compared with the results (wording unchanged)

The predictions are those given for this unit: "removing a gives a large loss; b small; a′ moderate; b′ about zero". I did not find them written in `ROADMAP.md` at 2a630bb (§9 and the rest of the file were searched). They should be written into the pre-registration, with a quantitative reading, before stage 2 is read (WU-0041).

DEVELOPMENT (DEV-1, DEV-2): not a hypothesis test.

- **a, large loss: held in 5 of 6 cells, not shown in 1.**
  - Ratios 3.06 to 10.4, with every interval excluding 1, in DEV-1 rossler and chua and in all of DEV-2.
  - DEV-1 pilot lorenz63: 1.31 [0.60, 3.77]. The interval includes 1, so the loss is not shown there (500 states, E = 2, heavy-tailed V: `n_eff` of mean V about 12).
- **b, small: held, trivially.** `b` is fitted at the boundary (about 1e-7 to 1e-13), and the ratio is 1 within 3e-9 in every cell. This is consistent with the prediction. It does not test the analog floor term.
- **a′, moderate: held in 3 of 6 cells, not shown in 3.**
  - A loss of 5% to 9%, with the interval excluding 1, in lorenz63 (both runs) and DEV-1 chua.
  - No detectable change in rossler (both runs) and DEV-2 chua: points 0.999 to 1.010, intervals including 1.
  - Removing `a′` makes A4 nearly PLP alone. The small size reflects that A4 already puts 82% to 89% of the weight on PLP.
- **b′, about zero: held.** `|ratio - 1| <= 8e-4` in every cell, and for Rössler `b′` is fitted at about 0.
  - In DEV-2 chua the interval excludes 1 on the favorable side: 0.9992 [0.9980, 0.99994]. Removing `b′` there makes A4 slightly *better*, by less than 0.1%.

## 5. Uncertainty budget (QoI: ratio of mean V, variant over A4, per cell)

| Source | Type | How estimated | Size | In the interval? |
| --- | --- | --- | --- | --- |
| Oracle Monte Carlo (M = 200 per state) | aleatory | `\|r_A - r_B\| / 2` from the half-draw moments (1 df per cell, rough) | a: 6e-3 to 0.14; a′: 9e-4 to 3.9e-3; b′: below 3e-5 | no; at least 10 times below the half-width in every row except the round-off-width rows (b everywhere, b′ in Rössler, half-widths below 3e-9) |
| Sampling of test states | aleatory | paired moving-block bootstrap (block 5, 2000, level 1 - 0.05/3) | half-widths in §3.4 | yes |
| Bootstrap Monte Carlo error | numerical | `endpoint_mc_error` (binomial order statistic) | see §6: up to 0.32 (upper endpoint, DEV-1 lorenz63, a) | no; below a tenth of the half-width except in the rows of §6 |
| Dependence bias (H2): the oracle V used for the realized score | estimator | approximation check, paired (§3.2) | paired `\|rel D\|` at most 4.4% of V(A4), not significant | no; bounded by the check's tolerances (9% to 26%) |
| Reconstruction (nu from the profile, weights) | numerical | 1e-12 checks (§3.1) | at most 1.5e-15 relative | no; negligible |
| Discretization (RK4), Levenberg-Marquardt | numerical | inherited from the runs (V6, LM summaries); not re-estimated here | not estimated in this unit | no |
| Round-off | numerical | float64, positive-sum formulas | about 1e-15 | no |
| No refit of the remaining coefficients | epistemic | not estimated; stage 2 (WU-0039) | — | no |
| Model form: three systems, `rho = 0.01` core cell, scalar observable, `H_ref` only | epistemic | not estimated; limitation | — | no |

The level is `1 - 0.05/3` per interval, as for H3c. It is a Bonferroni level within a system's family of three, not adjusted for the 24 intervals per run. Dependence assumption: block-stationary dependence of consecutive test states, captured by blocks of 5. The interval conditions on the fitted coefficients. Seeds: DEV-1 (pilot, R1, commit 01d9fc7) and DEV-2 (full, R5, commit 6f1a8c8).

## 6. Numerical-error flags (NVVUQ.9 rule: numerical rows at least 10 times below the half-width)

DEVELOPMENT (DEV-1, DEV-2): not a hypothesis test. The bootstrap endpoint Monte Carlo error exceeds a tenth of the half-width in the following rows:

| Row | Half-width | Endpoint MC error |
| --- | --- | --- |
| DEV-1 lorenz63, a, ratio of mean V | 1.59 | 0.32 |
| DEV-1 lorenz63, a, ratio of mean excess | 1.83 | 0.66 |
| DEV-1 chua, b′, ratio of mean V | 4.6e-4 | 6.0e-5 |
| DEV-1 chua, b′, ratio of mean excess | 2.0e-3 | 2.2e-4 |
| DEV-2 chua, a, ratio of mean excess | 15.1 | 1.5 |

None of these changes a reading in §4:

- the DEV-1 lorenz63 lower endpoints (0.595, 0.574) are far below 1;
- the DEV-1 chua b′ intervals straddle 1 by several MC errors;
- the DEV-2 chua lower endpoint (9.09) is far above 1.

The upper endpoints of those rows carry about 2 significant figures. The oracle Monte Carlo error is below a tenth of the half-width in every row.

## 7. Consequences for stage 2 (WU-0039, WU-0041), for the planner

1. **Boundary coefficients.** `b` is at the boundary in 6 of 6 cells and `b′` in Rössler. So a zero-term variant for them is a null by construction, and a refit without them reproduces the full fit. The WU-0039 synthetic recovery test ("a refit on synthetic data generated without the term recovers the other coefficients") should include the boundary case. The log-parametrised `soft_l1` fit cannot return an exact zero: a coefficient at the boundary comes out as a small positive number, 1e-16 to 1e-7 in these runs. So a tolerance for a recovered zero must be stated in absolute terms, as a weight change, not as a relative error.
2. **The zero-`a` and zero-`a′` variants are, to round-off, A0 and almost A1**, which are already scored. A pre-registered reading should say so, so that the ablation row is not read as new evidence about the conditions.
3. **Write the four predictions into the pre-registration**, with a quantitative reading table (for example: "large" means the lower bound is above 1.5; "about zero" means the interval lies within [0.99, 1.01]), before any stage-2 number exists.
4. With E = 2, realized-score checks at the pilot preset have relative tolerances of 34% to 73% (direct) and 12% to 26% (paired). A stage-2 check should use the paired form.
