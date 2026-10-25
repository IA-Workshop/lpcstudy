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

## 3. Results

(Filled after stage `full`; see below.)
