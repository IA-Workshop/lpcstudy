# WU-0045 checks

DEVELOPMENT (DEV-2): exploratory, not a hypothesis test; prototype, old code c9bb981

## M-2: curvature, unclipped minimizer, fitting target

DEVELOPMENT (DEV-2): exploratory, not a hypothesis test; prototype, old code c9bb981

| system | H | min kappa/rho^2 | median kappa/rho^2 | n_eff(kappa) | top-1% share of sum kappa | share u<0 (w*=0) | share u>1 (w*=1) | max abs u | n_eff(A2 excess) | median E_C / median E_P | median C / sqrt(E_C E_P) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| lorenz63 | 8 | 0.061 | 10.4 | 11.0 | 0.65 | 0.298 | 0.015 | 1.62 | 7.4 | 9.40 | 0.12 |
| lorenz63 | 15 | 0.046 | 15.2 | 27.3 | 0.52 | 0.281 | 0.013 | 1.03 | 26.0 | 8.28 | 0.12 |
| lorenz63 | 30 | 0.162 | 39.0 | 51.0 | 0.34 | 0.290 | 0.023 | 1.14 | 33.5 | 8.98 | 0.16 |
| lorenz63 | 60 | 0.082 | 421.1 | 135.9 | 0.18 | 0.302 | 0.039 | 1.31 | 76.8 | 9.99 | 0.19 |
| lorenz63 | 120 | 0.048 | 9551.3 | 414.4 | 0.06 | 0.148 | 0.121 | 1.91 | 309.9 | 1.06 | 0.30 |
| rossler | 8 | 0.030 | 5.3 | 127.9 | 0.21 | 0.262 | 0.004 | 1.09 | 186.8 | 5.27 | 0.17 |
| rossler | 15 | 0.079 | 6.8 | 108.1 | 0.24 | 0.243 | 0.001 | 1.01 | 159.9 | 4.60 | 0.18 |
| rossler | 30 | 0.027 | 16.1 | 126.9 | 0.21 | 0.293 | 0.003 | 1.01 | 96.9 | 4.86 | 0.21 |
| rossler | 60 | 0.118 | 89.9 | 121.2 | 0.21 | 0.302 | 0.016 | 1.15 | 73.1 | 4.57 | 0.26 |
| rossler | 120 | 1.223 | 1030.4 | 404.5 | 0.07 | 0.180 | 0.076 | 1.62 | 206.0 | 1.34 | 0.33 |
| chua | 8 | 0.016 | 4.9 | 7.1 | 0.81 | 0.293 | 0.001 | 1.00 | 7.7 | 6.78 | 0.20 |
| chua | 15 | 0.042 | 7.1 | 16.5 | 0.64 | 0.273 | 0.009 | 1.08 | 21.3 | 5.60 | 0.20 |
| chua | 30 | 0.012 | 17.4 | 48.3 | 0.38 | 0.297 | 0.009 | 1.07 | 11.8 | 6.86 | 0.21 |
| chua | 60 | 0.045 | 338.4 | 217.1 | 0.11 | 0.260 | 0.053 | 1.22 | 148.9 | 5.06 | 0.23 |
| chua | 120 | 4.058 | 6989.2 | 466.9 | 0.05 | 0.159 | 0.103 | 1.28 | 330.5 | 0.63 | 0.33 |

Sample-weight scale with l2_regularization = 1 (synthetic, in-sample R^2):

| weight scale | R^2 |
|---|---|
| 1 | 0.9796 |
| 0.01 | 0.9773 |
| 0.001 | 0.9681 |
| 0.0001 | 0.8282 |

Cross-fitted targets (5 contiguous folds of 200 test states; oracle profile; train 800 states). L_A = mean excess MSE V(g) - V(w*), as a ratio to the kappa-weighted constant; L_w = mean of (g-u)^2 - (w*-u)^2 (kappa = 1), as a ratio to the unweighted constant.

| system | H | rule | L_A ratio | L_w ratio |
|---|---|---|---|---|
| lorenz63 | 8 | const kappa | 1.000 | 3.098 |
| lorenz63 | 8 | const unit | 0.964 | 1.000 |
| lorenz63 | 8 | u, kappa/mean | 0.980 | 0.559 |
| lorenz63 | 8 | u, raw kappa | 0.961 | 0.647 |
| lorenz63 | 8 | u, unit | 0.689 | 0.433 |
| lorenz63 | 8 | w*, unit | 0.699 | 0.438 |
| lorenz63 | 8 | two-part logit | 0.412 | 0.454 |
| lorenz63 | 8 | separation formula | 0.438 | 0.494 |
| lorenz63 | 30 | const kappa | 1.000 | 1.013 |
| lorenz63 | 30 | const unit | 0.986 | 1.000 |
| lorenz63 | 30 | u, kappa/mean | 0.484 | 0.694 |
| lorenz63 | 30 | u, raw kappa | 0.488 | 0.674 |
| lorenz63 | 30 | u, unit | 0.621 | 0.575 |
| lorenz63 | 30 | w*, unit | 0.651 | 0.582 |
| lorenz63 | 30 | two-part logit | 0.628 | 0.629 |
| lorenz63 | 30 | separation formula | 0.356 | 0.625 |
| lorenz63 | 120 | const kappa | 1.000 | 1.221 |
| lorenz63 | 120 | const unit | 1.235 | 1.000 |
| lorenz63 | 120 | u, kappa/mean | 1.266 | 1.223 |
| lorenz63 | 120 | u, raw kappa | 1.279 | 1.236 |
| lorenz63 | 120 | u, unit | 1.342 | 1.094 |
| lorenz63 | 120 | w*, unit | 1.291 | 1.041 |
| lorenz63 | 120 | two-part logit | 1.239 | 1.112 |
| lorenz63 | 120 | separation formula | 1.301 | 1.581 |
| rossler | 8 | const kappa | 1.000 | 1.273 |
| rossler | 8 | const unit | 2.181 | 1.000 |
| rossler | 8 | u, kappa/mean | 0.632 | 0.728 |
| rossler | 8 | u, raw kappa | 0.673 | 0.902 |
| rossler | 8 | u, unit | 1.296 | 0.781 |
| rossler | 8 | w*, unit | 1.373 | 0.785 |
| rossler | 8 | two-part logit | 0.876 | 0.812 |
| rossler | 8 | separation formula | 0.886 | 0.773 |
| rossler | 30 | const kappa | 1.000 | 1.256 |
| rossler | 30 | const unit | 1.867 | 1.000 |
| rossler | 30 | u, kappa/mean | 0.459 | 0.608 |
| rossler | 30 | u, raw kappa | 0.469 | 0.665 |
| rossler | 30 | u, unit | 0.694 | 0.649 |
| rossler | 30 | w*, unit | 0.738 | 0.644 |
| rossler | 30 | two-part logit | 0.632 | 0.659 |
| rossler | 30 | separation formula | 0.494 | 0.606 |
| rossler | 120 | const kappa | 1.000 | 1.028 |
| rossler | 120 | const unit | 1.026 | 1.000 |
| rossler | 120 | u, kappa/mean | 1.233 | 1.158 |
| rossler | 120 | u, raw kappa | 1.216 | 1.143 |
| rossler | 120 | u, unit | 1.200 | 1.068 |
| rossler | 120 | w*, unit | 1.142 | 1.038 |
| rossler | 120 | two-part logit | 1.148 | 1.077 |
| rossler | 120 | separation formula | 1.155 | 1.300 |
| chua | 8 | const kappa | 1.000 | 1.296 |
| chua | 8 | const unit | 4.421 | 1.000 |
| chua | 8 | u, kappa/mean | 1.561 | 0.830 |
| chua | 8 | u, raw kappa | 0.870 | 0.805 |
| chua | 8 | u, unit | 2.965 | 0.759 |
| chua | 8 | w*, unit | 2.979 | 0.753 |
| chua | 8 | two-part logit | 1.006 | 0.797 |
| chua | 8 | separation formula | 0.654 | 0.845 |
| chua | 30 | const kappa | 1.000 | 1.179 |
| chua | 30 | const unit | 1.270 | 1.000 |
| chua | 30 | u, kappa/mean | 1.286 | 0.897 |
| chua | 30 | u, raw kappa | 1.235 | 0.879 |
| chua | 30 | u, unit | 1.353 | 0.788 |
| chua | 30 | w*, unit | 1.417 | 0.799 |
| chua | 30 | two-part logit | 1.264 | 0.844 |
| chua | 30 | separation formula | 0.898 | 0.774 |
| chua | 120 | const kappa | 1.000 | 1.063 |
| chua | 120 | const unit | 1.061 | 1.000 |
| chua | 120 | u, kappa/mean | 1.110 | 1.082 |
| chua | 120 | u, raw kappa | 1.105 | 1.083 |
| chua | 120 | u, unit | 1.149 | 1.049 |
| chua | 120 | w*, unit | 1.127 | 1.014 |
| chua | 120 | two-part logit | 1.089 | 1.095 |
| chua | 120 | separation formula | 1.179 | 1.405 |

## M-8: V(w) substitution for learned, draw-dependent weights at H_ref

DEVELOPMENT (DEV-2): exploratory, not a hypothesis test; prototype, old code c9bb981

WU-0036 construction: D_i = S_i - mean_j V_i(w_ij); SE from the half-draw moments; paired rows subtract A1 (w = 0). Rule of WU-0036: |z| <= 4.

| system | rule | mean draw-SD of w | mean w | rel D (direct) | z (direct) | rel D (paired) | z (paired) | rel tol (paired) |
|---|---|---|---|---|---|---|---|---|
| lorenz63 | A4 | 0.0323 | 0.113 | +0.071 | +0.65 | +0.008 | +0.27 | 0.112 |
| lorenz63 | A3 | 0.0038 | 0.087 | -0.022 | -0.17 | -0.106 | -1.44 | 0.293 |
| lorenz63 | A5 | 0.0614 | 0.322 | -0.046 | -0.50 | -0.125 | -1.40 | 0.358 |
| rossler | A4 | 0.0497 | 0.169 | +0.058 | +1.28 | +0.044 | +1.90 | 0.092 |
| rossler | A3 | 0.0064 | 0.121 | +0.010 | +0.23 | -0.004 | -0.28 | 0.056 |
| rossler | A5 | 0.0107 | 0.037 | +0.033 | +0.73 | +0.018 | +1.97 | 0.037 |
| chua | A4 | 0.0467 | 0.162 | +0.232 | +1.26 | +0.030 | +1.02 | 0.117 |
| chua | A3 | 0.0070 | 0.119 | +0.193 | +1.04 | -0.008 | -0.39 | 0.084 |
| chua | A5 | 0.0096 | 0.060 | +0.197 | +1.07 | -0.006 | -0.23 | 0.105 |

Draw dependence of the deployable profile: within-state SD over the E draws divided by the total SD, per coordinate (0 = a function of the state only; 1 = all draw noise).

| system | R_hat | O_hat | I_hat | N_hat |
|---|---|---|---|---|
| lorenz63 | 0.25 | 0.13 | 0.20 | 0.69 |
| rossler | 0.29 | 0.02 | 0.14 | 0.78 |
| chua | 0.38 | 0.07 | 0.26 | 0.69 |

## M-4, M-5: horizon target, ties, Lyapunov baseline, Harrell's C

DEVELOPMENT (DEV-2): exploratory, not a hypothesis test; prototype, old code c9bb981

T = oracle-hybrid characteristic horizon at theta = 0.2 (steps), stored as log T; T = 240 is treated as censored (the dump has no event flag). T0 = (30 / I) ln(theta sqrt(3) / (rho e^s)), s = softmin(R, O); I <= 0 or T0 > 240 gives 240, T0 < 1 gives 1 (counted).

| system | n censored | distinct T | largest atom | n I<=0 | n T0 clipped | median ln(T/T0) | IQR ln(T/T0) | C(T0) | C(1/I) | C(-s) | Spearman(T, T0) | H1c PLP median ratio |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lorenz63 | 0 | 160 | 0.026 | 148 | 277 | -0.568 | 1.059 | 0.609 | 0.606 | 0.493 | 0.306 | 0.583 |
| rossler | 2 | 154 | 0.022 | 50 | 96 | -0.098 | 0.581 | 0.658 | 0.643 | 0.581 | 0.454 | 0.972 |
| chua | 4 | 181 | 0.017 | 169 | 251 | -0.242 | 1.037 | 0.688 | 0.679 | 0.609 | 0.534 | 0.743 |

Harrell's C: vectorized form equals the brute-force count to 1e-12 on the first 150 states of each system (asserted).

Quartiles (25, 50, 75%) of T in LT, of L' = ln(theta sqrt(3) / (rho e^s)), and of the separation weight p = 1 / (1 + e^{2(R - O)}):

| system | T / LT | L' | p |
|---|---|---|---|
| lorenz63 | 1.77, 2.37, 2.97 | 2.86, 3.12, 3.45 | 0.0382, 0.0929, 0.259 |
| rossler | 2.3, 3.37, 4.3 | 3.41, 3.54, 3.68 | 0.0638, 0.141, 0.289 |
| chua | 1.76, 2.92, 3.93 | 2.5, 2.74, 2.95 | 0.0601, 0.148, 0.279 |

## M-6: replication rules, binomial error rates (5 independent seeds)

p = per-seed probability that a seed gives the reading. P(rule) = P(at least k of 5).

| p | 0.01 | 0.025 | 0.05 | 0.063 | 0.1 | 0.2 | 0.5 | 0.7 | 0.8 | 0.9 | 0.95 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| >= 3 of 5 | 9.9e-06 | 0.00015 | 0.0012 | 0.0023 | 0.0086 | 0.058 | 0.5 | 0.84 | 0.94 | 0.99 | 1 |
| >= 4 of 5 | 5e-08 | 1.9e-06 | 3e-05 | 7.5e-05 | 0.00046 | 0.0067 | 0.19 | 0.53 | 0.74 | 0.92 | 0.98 |
| >= 5 of 5 | 1e-10 | 9.8e-09 | 3.1e-07 | 9.9e-07 | 1e-05 | 0.00032 | 0.031 | 0.17 | 0.33 | 0.59 | 0.77 |

Per-seed probability p of a false decisive bound claim at 95% when the interval omits a between-seed SD of r times the within-seed SE: p = Phi(-1.96 / sqrt(1 + r^2)).

| r | p | P(>= 3 of 5) | P(>= 4 of 5) |
|---|---|---|---|
| 0 | 0.0250 | 0.00015 | 1.9e-06 |
| 0.5 | 0.0398 | 0.00059 | 1.2e-05 |
| 0.8 | 0.0629 | 0.0023 | 7.5e-05 |
| 1 | 0.0829 | 0.005 | 0.00022 |
| 1.5 | 0.1385 | 0.021 | 0.0016 |
| 2 | 0.1904 | 0.051 | 0.0056 |

## Oracle Monte Carlo bias of the excess; failed-resample thresholds

DEVELOPMENT (DEV-2): exploratory, not a hypothesis test; prototype, old code c9bb981

bias_i = kappa_i (w*_A - w*_B)^2 / 4 (half-draw moments): the expected upward bias of every rule's estimated excess, because w* is estimated from the same moments.

| system | H | mean bias / mean excess of the constant rule | median half-width of w* |
|---|---|---|---|
| lorenz63 | 8 | 0.0017 | 0.0068 |
| lorenz63 | 15 | 0.0018 | 0.0069 |
| lorenz63 | 30 | 0.0021 | 0.0077 |
| lorenz63 | 60 | 0.0049 | 0.0066 |
| lorenz63 | 120 | 0.0052 | 0.0110 |
| rossler | 8 | 0.0178 | 0.0089 |
| rossler | 15 | 0.0182 | 0.0096 |
| rossler | 30 | 0.0177 | 0.0098 |
| rossler | 60 | 0.0099 | 0.0097 |
| rossler | 120 | 0.0065 | 0.0112 |
| chua | 8 | 0.0194 | 0.0087 |
| chua | 15 | 0.0206 | 0.0092 |
| chua | 30 | 0.0091 | 0.0088 |
| chua | 60 | 0.0060 | 0.0077 |
| chua | 120 | 0.0056 | 0.0106 |

| level | failures that make both bounds infinite (B = 2000) |
|---|---|
| 0.95000 | 50 |
| 0.98333 | 17 |
| 0.98750 | 13 |
| 0.99167 | 9 |

