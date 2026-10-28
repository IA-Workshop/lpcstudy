# Phase J contribution study: CONF-8

**PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.** Run `phasej-CONF-8/phasej`; analysis commit `c19ad486b93a2ee96d64ce069ec42fd440428211` (dirty: False). Every reading is an estimate; Shapley shares and interactions are predictive, not causal. Training variance is not in the intervals.

## lorenz63

**PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.**

| check | result |
|---|---|
| (f1) state_mse from per-draw errors, max rel diff | A0 0.0e+00, A1 0.0e+00, A2 0.0e+00, A3 0.0e+00, A4 0.0e+00, A5 0.0e+00 (within 1e-12: True) |
| (g) WU-0039b (b1), (b2) rows reproduced | drop-N: True, all rows: True |
| separation formula on F-hat vs stored A4 at H_ref, max abs | 2.22e-16 |
| T_c: T = 1 / e_(T-1) = theta (train, test) | 8/0, 3/0 |
| (f2) dependence bias, deployable rows (reported, not gating) | 131 rows; 42 flagged: H=8 I: dependence bias detectable (interval excludes 0), t1+t2 / V 0.253, z 1.42; H=8 RI: dependence bias detectable (interval excludes 0), t1+t2 / V 0.246, z 1.17; H=8 OI: dependence bias detectable (interval excludes 0), t1+t2 / V 0.109, z 0.642; H=8 IN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.229, z 1.53; H=8 RIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.206, z 1.11; H=8 OIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.116, z 0.791; H=8 ROIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.1, z 0.633; H=8 X: dependence bias detectable (interval excludes 0), t1+t2 / V -0.0015, z 0.147; H=8 swap-R: dependence bias detectable (interval excludes 0), t1+t2 / V 0.00356, z 0.198; H=8 swap-N: dependence bias detectable (interval excludes 0), t1+t2 / V 0.00161, z 0.194; H=15 O: dependence bias detectable (interval excludes 0), t1+t2 / V 0.121, z 1.27; H=15 RO: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0908, z 0.165 ... |

### A. Allocation: drop-one and Shapley

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED. MSE ratio MSE(F without X)/MSE(F) at level 1 - 0.05/4 (reading by the 1.05 table, with the n_eff guard); excess ratio L_A(F without X)/L_A(F) and Holm p (Delta MSE > 0) are estimates. phi = Shapley share of L_A (95%). Oracle rows: moment form; deployable rows: realized per draw.

| horizon | profile | X | MSE ratio [CI] | reading | excess ratio | Holm p | phi_X [95% CI] | share |
|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | R | 1.01 [1, 1.09] | undetermined (n_eff < 50) | 1.06 | 0.002 | 0.000133 [-0.000561, 0.00077] | 0.013 |
| H=8 (0.27 LT) | oracle | O | 1.89 [1.35, 6.82] | undetermined (n_eff < 50) | 5.12 | 0.002 | 0.00708 [0.0053, 0.0092] | 0.693 |
| H=8 (0.27 LT) | oracle | I | 0.997 [0.963, 1] | undetermined (n_eff < 50) | 0.988 | 0.838 | 0.00252 [0.00148, 0.00371] | 0.246 |
| H=8 (0.27 LT) | oracle | N | 1 [0.997, 1.03] | undetermined (n_eff < 50) | 1.01 | 0.17 | 0.00049 [-0.000649, 0.00152] | 0.048 |
| H=8 (0.27 LT) | deployable | R | 1.2 [1.03, 1.49] | undetermined (n_eff < 50) | 1.32 | 0.006 | 0.00208 [0.000718, 0.00369] | 0.47 |
| H=8 (0.27 LT) | deployable | O | 1.22 [1.03, 1.56] | undetermined (n_eff < 50) | 1.34 | 0.006 | 0.00341 [0.002, 0.00496] | 0.771 |
| H=8 (0.27 LT) | deployable | I | 0.842 [0.643, 1.02] | undetermined (n_eff < 50) | 0.754 | 1 | 0.000193 [-0.00134, 0.00166] | 0.0435 |
| H=8 (0.27 LT) | deployable | N | 0.822 [0.665, 0.957] | undetermined (n_eff < 50) | 0.722 | 1 | -0.00126 [-0.00283, 9.23e-05] | -0.284 |
| H=15 (0.50 LT) | oracle | R | 1.07 [1.02, 1.13] | undetermined (n_eff < 50) | 1.41 | 0.002 | 0.00117 [-4.18e-05, 0.00235] | 0.062 |
| H=15 (0.50 LT) | oracle | O | 2.33 [1.64, 3.73] | undetermined (n_eff < 50) | 9.31 | 0.002 | 0.0135 [0.0102, 0.0176] | 0.71 |
| H=15 (0.50 LT) | oracle | I | 1.02 [0.963, 1.08] | undetermined (n_eff < 50) | 1.1 | 0.255 | 0.00231 [0.00109, 0.00343] | 0.122 |
| H=15 (0.50 LT) | oracle | N | 1.01 [0.992, 1.03] | undetermined (n_eff < 50) | 1.05 | 0.217 | 0.002 [-0.000749, 0.00427] | 0.105 |
| H=15 (0.50 LT) | deployable | R | 1.47 [1.2, 1.82] | undetermined (n_eff < 50) | 1.75 | 0.002 | 0.00685 [0.00378, 0.0102] | 0.619 |
| H=15 (0.50 LT) | deployable | O | 1.19 [1.05, 1.35] | undetermined (n_eff < 50) | 1.3 | 0.002 | 0.000492 [-0.000767, 0.00169] | 0.0444 |
| H=15 (0.50 LT) | deployable | I | 1.16 [1.02, 1.31] | undetermined (n_eff < 50) | 1.26 | 0.007 | 0.0023 [0.00116, 0.00351] | 0.207 |
| H=15 (0.50 LT) | deployable | N | 1.19 [0.903, 1.56] | undetermined (n_eff < 50) | 1.3 | 0.0535 | 0.00143 [-0.00213, 0.00541] | 0.13 |
| H=30 (1.00 LT) | oracle | R | 1.03 [0.966, 1.1] | undetermined (n_eff < 50) | 1.08 | 0.271 | 0.00133 [0.000319, 0.00241] | 0.0659 |
| H=30 (1.00 LT) | oracle | O | 1.31 [1.08, 1.67] | undetermined (n_eff < 50) | 1.99 | 0.004 | 0.0135 [0.00877, 0.0183] | 0.67 |
| H=30 (1.00 LT) | oracle | I | 1.04 [0.983, 1.09] | undetermined (n_eff < 50) | 1.13 | 0.111 | 0.00304 [8.23e-05, 0.00593] | 0.151 |
| H=30 (1.00 LT) | oracle | N | 1.01 [0.975, 1.04] | undetermined (n_eff < 50) | 1.02 | 0.282 | 0.0023 [0.000338, 0.00418] | 0.114 |
| H=30 (1.00 LT) | deployable | R | 1.08 [0.979, 1.2] | undetermined | 1.17 | 0.063 | 0.00465 [0.00214, 0.00748] | 0.432 |
| H=30 (1.00 LT) | deployable | O | 1.03 [0.955, 1.11] | undetermined | 1.06 | 0.299 | 0.000197 [-0.00185, 0.00207] | 0.0183 |
| H=30 (1.00 LT) | deployable | I | 1.1 [1.03, 1.18] | needed, size not determined | 1.2 | 0.002 | 0.00639 [0.00423, 0.00878] | 0.593 |
| H=30 (1.00 LT) | deployable | N | 0.939 [0.839, 1.05] | undetermined | 0.875 | 0.922 | -0.000465 [-0.00337, 0.00209] | -0.0432 |
| H=60 (2.00 LT) | oracle | R | 1.02 [0.996, 1.05] | undetermined | 1.09 | 0.032 | 0.00243 [-0.00063, 0.00491] | 0.176 |
| H=60 (2.00 LT) | oracle | O | 1.06 [1.02, 1.1] | needed, size not determined | 1.21 | 0.0045 | 0.00779 [0.00351, 0.0121] | 0.564 |
| H=60 (2.00 LT) | oracle | I | 1.02 [1.01, 1.04] | small | 1.08 | 0.002 | 0.00244 [0.00134, 0.00363] | 0.177 |
| H=60 (2.00 LT) | oracle | N | 1 [0.989, 1.02] | negligible | 1.01 | 0.386 | 0.00115 [-0.000122, 0.00244] | 0.0834 |
| H=60 (2.00 LT) | deployable | R | 1.02 [0.998, 1.04] | negligible | 1.06 | 0.0435 | 0.00176 [-0.000385, 0.00406] | 0.37 |
| H=60 (2.00 LT) | deployable | O | 1.01 [0.992, 1.03] | negligible | 1.04 | 0.131 | 0.000641 [-0.000562, 0.00177] | 0.135 |
| H=60 (2.00 LT) | deployable | I | 1.02 [1, 1.04] | small | 1.07 | 0.006 | 0.00226 [0.000972, 0.00355] | 0.475 |
| H=60 (2.00 LT) | deployable | N | 1.01 [0.992, 1.03] | negligible | 1.04 | 0.131 | 9.55e-05 [-0.00115, 0.00138] | 0.0201 |
| H=120 (4.00 LT) | oracle | R | 1.01 [1, 1.02] | small | 1.03 | 0.0075 | 0.00502 [0.00169, 0.00832] | 0.346 |
| H=120 (4.00 LT) | oracle | O | 1.01 [1, 1.01] | small | 1.02 | 0.0075 | 0.00447 [0.00254, 0.00643] | 0.309 |
| H=120 (4.00 LT) | oracle | I | 1.01 [1, 1.01] | small | 1.02 | 0.004 | 0.00448 [0.00241, 0.00673] | 0.309 |
| H=120 (4.00 LT) | oracle | N | 1 [0.996, 1.01] | negligible | 1 | 0.464 | 0.000521 [-0.0018, 0.00285] | 0.0359 |
| H=120 (4.00 LT) | deployable | R | 1 [0.998, 1.01] | negligible | 1.01 | 0.062 | 0.00458 [0.00144, 0.00748] | 0.306 |
| H=120 (4.00 LT) | deployable | O | 1 [1, 1.01] | small | 1.02 | 0.009 | 0.00399 [0.00179, 0.00613] | 0.267 |
| H=120 (4.00 LT) | deployable | I | 1.01 [1, 1.01] | small | 1.02 | 0.002 | 0.00406 [0.00206, 0.00631] | 0.271 |
| H=120 (4.00 LT) | deployable | N | 1.01 [1, 1.01] | small | 1.02 | 0.006 | 0.00233 [0.000665, 0.00397] | 0.156 |

### A. Allocation: summary per horizon

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED. n_eff = Kish size of kappa on the test states; G = 1 - L_A(rule)/L_A(constant), estimate (95%).

| horizon | profile | n_eff(kappa) | G(F) [CI] | G(separation) | MSE(F)/MSE(sep) [CI] | reading | settings (A) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 81.7 | 0.912 [0.748, 0.993] | 0.886 | 0.94 [0.757, 1.25] | undetermined (n_eff < 50) | F: mid; qn 3, mid 10, low 2 |
| H=8 (0.27 LT) | deployable | 81.7 | 0.407 [0.19, 0.592] | -1.35 | 0.345 [0.244, 0.463] | undetermined (n_eff < 50) | F: mid; qn 1, mid 5, low 9 |
| H=15 (0.50 LT) | oracle | 102 | 0.935 [0.893, 0.963] | 0.923 | 0.971 [0.929, 1.01] | undetermined (n_eff < 50) | F: mid; qn 7, mid 5, low 3 |
| H=15 (0.50 LT) | deployable | 102 | 0.491 [0.319, 0.634] | -0.362 | 0.488 [0.37, 0.641] | lowers | F: qn; qn 1, mid 2, low 12 |
| H=30 (1.00 LT) | oracle | 188 | 0.678 [0.544, 0.781] | 0.688 | 1.01 [0.931, 1.12] | undetermined (n_eff < 50) | F: mid; qn 1, mid 9, low 5 |
| H=30 (1.00 LT) | deployable | 188 | 0.344 [0.187, 0.483] | -0.271 | 0.684 [0.583, 0.791] | lowers | F: mid; qn 3, mid 6, low 6 |
| H=60 (2.00 LT) | oracle | 497 | 0.274 [0.16, 0.374] | 0.201 | 0.973 [0.948, 0.997] | lowers | F: mid; qn 0, mid 9, low 6 |
| H=60 (2.00 LT) | deployable | 497 | 0.101 [0.0214, 0.18] | -0.0749 | 0.942 [0.913, 0.972] | lowers | F: mid; qn 1, mid 3, low 11 |
| H=120 (4.00 LT) | oracle | 1.78e+03 | 0.0551 [0.0326, 0.0776] | -0.255 | 0.915 [0.9, 0.928] | lowers | F: mid; qn 0, mid 3, low 12 |
| H=120 (4.00 LT) | deployable | 1.78e+03 | 0.0545 [0.035, 0.0747] | -0.178 | 0.933 [0.921, 0.944] | lowers | F: mid; qn 0, mid 3, low 12 |

### B. Allocation: pairwise interactions (logit u, interior states)

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED. Delta = L(additive) - L(additive + pair) on the test states, models fixed; level 1 - 0.05/6; Holm over the six pairs. R x I and O x I are primary.

| horizon | profile | pair | Delta [CI] | Holm p | reading | loss ratio reading |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | RI (primary) | -0.0552 [-0.124, 0.00801] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | OI (primary) | -0.0245 [-0.0813, 0.0389] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | RO | 0.137 [0.0429, 0.229] | 0.003 | interaction gain detected | needed, size not determined |
| H=8 (0.27 LT) | oracle | RN | 0.00606 [-0.0497, 0.0584] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | ON | -0.0547 [-0.118, 0.0115] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | IN | -0.00779 [-0.0474, 0.0286] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RI (primary) | -0.101 [-0.23, 0.0363] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | OI (primary) | 0.00649 [-0.0204, 0.0327] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RO | 0.0166 [-0.175, 0.192] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RN | -0.00354 [-0.041, 0.0361] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | ON | 0.0124 [-0.0166, 0.0435] | 0.771 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | IN | 0.00765 [-0.0194, 0.0371] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | RI (primary) | 0.00796 [-0.0619, 0.0707] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | OI (primary) | -0.0146 [-0.085, 0.0607] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | RO | -0.0269 [-0.114, 0.0563] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | RN | -0.0349 [-0.103, 0.041] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | ON | -0.0357 [-0.109, 0.0392] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | IN | -0.000256 [-0.0405, 0.0487] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | RI (primary) | 0.0511 [0.014, 0.0895] | 0.004 | interaction gain detected | small |
| H=15 (0.50 LT) | deployable | OI (primary) | 0.0368 [0.011, 0.0652] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | deployable | RO | 0.129 [0.054, 0.2] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | deployable | RN | -0.00954 [-0.0393, 0.0198] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | ON | 0.00339 [-0.0318, 0.0359] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | IN | -0.0126 [-0.0388, 0.0149] | 1 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | RI (primary) | 0.0267 [-0.0445, 0.0983] | 0.805 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | OI (primary) | 0.0193 [-0.0647, 0.111] | 0.882 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | RO | 0.101 [0.025, 0.183] | 0.006 | interaction gain detected | needed, size not determined |
| H=30 (1.00 LT) | oracle | RN | -0.00739 [-0.0656, 0.0564] | 1 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | ON | -0.0584 [-0.134, 0.0125] | 1 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | IN | 0.0165 [-0.0333, 0.0613] | 0.805 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | RI (primary) | 0.072 [0.0259, 0.124] | 0.003 | interaction gain detected | small |
| H=30 (1.00 LT) | deployable | OI (primary) | 0.0276 [-0.0075, 0.0604] | 0.047 | interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | RO | 0.0931 [0.0329, 0.157] | 0.003 | interaction gain detected | small |
| H=30 (1.00 LT) | deployable | RN | 0.00328 [-0.0315, 0.0404] | 0.406 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | ON | 0.0338 [-0.00056, 0.069] | 0.018 | interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | IN | 0.0525 [0.0139, 0.0949] | 0.004 | interaction gain detected | small |
| H=60 (2.00 LT) | oracle | RI (primary) | -0.00526 [-0.122, 0.102] | 1 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | OI (primary) | 0.0885 [-0.0175, 0.19] | 0.105 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | RO | 0.00116 [-0.113, 0.119] | 1 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | RN | -0.0223 [-0.112, 0.0588] | 1 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | ON | -0.0932 [-0.168, -0.0182] | 1 | no interaction gain; the pair model fits worse | no interaction gain; the pair model fits worse |
| H=60 (2.00 LT) | oracle | IN | 0.00781 [-0.054, 0.0724] | 1 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | RI (primary) | 0.109 [0.0481, 0.164] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | OI (primary) | 0.0441 [0.00427, 0.0839] | 0.01 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | RO | 0.0539 [-0.00509, 0.117] | 0.019 | interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | RN | 0.0391 [-0.00587, 0.0845] | 0.019 | interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | ON | 0.0318 [0.00325, 0.0632] | 0.01 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | IN | 0.0579 [0.0179, 0.1] | 0.003 | interaction gain detected | small |
| H=120 (4.00 LT) | oracle | RI (primary) | -0.0163 [-0.0619, 0.0298] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | OI (primary) | 0.0643 [0.0303, 0.1] | 0.003 | interaction gain detected | small |
| H=120 (4.00 LT) | oracle | RO | 0.0059 [-0.0313, 0.0453] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RN | -0.0114 [-0.0468, 0.0211] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | ON | -0.00596 [-0.0377, 0.0288] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | IN | -0.0041 [-0.0315, 0.0227] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RI (primary) | 0.015 [-0.0163, 0.0455] | 0.422 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | OI (primary) | 0.0355 [0.0066, 0.066] | 0.006 | interaction gain detected | small |
| H=120 (4.00 LT) | deployable | RO | 0.0108 [-0.0135, 0.0351] | 0.422 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RN | 0.0128 [-0.0119, 0.0391] | 0.422 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | ON | -0.00128 [-0.0205, 0.0175] | 0.905 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | IN | 0.00108 [-0.0214, 0.0243] | 0.905 | no interaction gain detected | negligible |

### D. Allocation ladder (rung against the full profile)

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED. MSE ratio MSE(rung)/MSE(F) at level 1 - 0.05/m (m rungs); Holm p for Delta MSE > 0. Theory gap L_A(oracle F) is an upper bound; estimation gap = L_A(deployable F) - L_A(oracle F) (95%).

| horizon | profile | rung | MSE | MSE ratio vs F [CI] | reading | Holm p |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | none | 0.0148 | 3.23 [1.76, 16.3] | undetermined (n_eff < 50) | 0.0045 |
| H=8 (0.27 LT) | oracle | separation | 0.00488 | 1.06 [0.761, 1.35] | undetermined (n_eff < 50) | 0.659 |
| H=8 (0.27 LT) | oracle | RO | 0.00458 | 0.999 [0.96, 1.04] | undetermined (n_eff < 50) | 0.659 |
| H=8 (0.27 LT) | oracle | R | 0.0147 | 3.21 [1.75, 18] | undetermined (n_eff < 50) | 0.0045 |
| H=8 (0.27 LT) | oracle | O | 0.00465 | 1.01 [1, 1.11] | undetermined (n_eff < 50) | 0.0045 |
| H=8 (0.27 LT) | oracle | I | 0.00958 | 2.09 [1.34, 8.79] | undetermined (n_eff < 50) | 0.0045 |
| H=8 (0.27 LT) | oracle | N | 0.0139 | 3.03 [1.67, 16.9] | undetermined (n_eff < 50) | 0.0045 |
| H=8 (0.27 LT) | oracle | F (ROIN) | 0.00458 | 1 | | |
| H=8 (0.27 LT) | oracle | X | 0.00541 | 1.18 [1.06, 2.36] | undetermined (n_eff < 50) | 0.0045 |
| H=8 (0.27 LT) | oracle | X+F | 0.00472 | 1.03 [0.999, 1.36] | undetermined (n_eff < 50) | 0.0165 |
| H=8 (0.27 LT) | deployable | none | 0.0145 | 1.44 [1.05, 2.15] | undetermined (n_eff < 50) | 0.006 |
| H=8 (0.27 LT) | deployable | A2 (stored) | 0.0146 | 1.45 [1.06, 2.23] | undetermined (n_eff < 50) | 0.006 |
| H=8 (0.27 LT) | deployable | separation | 0.0292 | 2.9 [1.86, 4.94] | undetermined (n_eff < 50) | 0.006 |
| H=8 (0.27 LT) | deployable | A4 (stored) | 0.0292 | 2.9 [1.86, 4.94] | undetermined (n_eff < 50) | 0.006 |
| H=8 (0.27 LT) | deployable | RO | 0.00804 | 0.8 [0.453, 1.14] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | R | 0.0134 | 1.33 [0.98, 2.05] | undetermined (n_eff < 50) | 0.03 |
| H=8 (0.27 LT) | deployable | O | 0.0111 | 1.11 [0.865, 1.61] | undetermined (n_eff < 50) | 0.452 |
| H=8 (0.27 LT) | deployable | I | 0.0138 | 1.38 [1.07, 1.91] | undetermined (n_eff < 50) | 0.006 |
| H=8 (0.27 LT) | deployable | N | 0.0157 | 1.56 [1.24, 2.19] | undetermined (n_eff < 50) | 0.006 |
| H=8 (0.27 LT) | deployable | F (ROIN) | 0.0101 | 1 | | |
| H=8 (0.27 LT) | deployable | X | 0.00515 | 0.512 [0.152, 0.797] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | A3 (stored) | 0.0152 | 1.52 [0.927, 2.44] | undetermined (n_eff < 50) | 0.0525 |
| H=8 (0.27 LT) | deployable | X+F | 0.00513 | 0.511 [0.154, 0.794] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | oracle | none | 0.0271 | 3.31 [2.32, 4.92] | undetermined (n_eff < 50) | 0.0045 |
| H=15 (0.50 LT) | oracle | separation | 0.00844 | 1.03 [0.98, 1.09] | undetermined (n_eff < 50) | 0.208 |
| H=15 (0.50 LT) | oracle | RO | 0.00842 | 1.03 [0.969, 1.1] | undetermined (n_eff < 50) | 0.256 |
| H=15 (0.50 LT) | oracle | R | 0.0229 | 2.79 [1.98, 4.29] | undetermined (n_eff < 50) | 0.0045 |
| H=15 (0.50 LT) | oracle | O | 0.00911 | 1.11 [1.02, 1.23] | undetermined (n_eff < 50) | 0.005 |
| H=15 (0.50 LT) | oracle | I | 0.0202 | 2.46 [1.79, 3.65] | undetermined (n_eff < 50) | 0.0045 |
| H=15 (0.50 LT) | oracle | N | 0.0218 | 2.66 [1.9, 4.05] | undetermined (n_eff < 50) | 0.0045 |
| H=15 (0.50 LT) | oracle | F (ROIN) | 0.0082 | 1 | | |
| H=15 (0.50 LT) | oracle | X | 0.0104 | 1.27 [1.03, 1.67] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | oracle | X+F | 0.00802 | 0.978 [0.955, 1.01] | undetermined (n_eff < 50) | 0.984 |
| H=15 (0.50 LT) | deployable | none | 0.0294 | 1.6 [1.18, 2.23] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | A2 (stored) | 0.0294 | 1.6 [1.18, 2.23] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | separation | 0.0376 | 2.05 [1.33, 3.13] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | A4 (stored) | 0.0376 | 2.05 [1.33, 3.13] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | RO | 0.0227 | 1.23 [0.881, 1.74] | undetermined (n_eff < 50) | 0.102 |
| H=15 (0.50 LT) | deployable | R | 0.0228 | 1.24 [0.91, 1.72] | undetermined (n_eff < 50) | 0.102 |
| H=15 (0.50 LT) | deployable | O | 0.0307 | 1.67 [1.2, 2.35] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | I | 0.026 | 1.42 [1.03, 2.02] | undetermined (n_eff < 50) | 0.009 |
| H=15 (0.50 LT) | deployable | N | 0.0289 | 1.57 [1.24, 2] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | F (ROIN) | 0.0184 | 1 | | |
| H=15 (0.50 LT) | deployable | X | 0.00995 | 0.542 [0.334, 0.772] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | A3 (stored) | 0.0252 | 1.37 [0.887, 2.06] | undetermined (n_eff < 50) | 0.085 |
| H=15 (0.50 LT) | deployable | X+F | 0.0132 | 0.719 [0.506, 0.949] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | none | 0.051 | 1.66 [1.34, 2.16] | undetermined (n_eff < 50) | 0.0045 |
| H=30 (1.00 LT) | oracle | separation | 0.0305 | 0.99 [0.846, 1.11] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | RO | 0.0316 | 1.03 [0.963, 1.07] | undetermined (n_eff < 50) | 0.394 |
| H=30 (1.00 LT) | oracle | R | 0.0497 | 1.61 [1.3, 2.07] | undetermined (n_eff < 50) | 0.0045 |
| H=30 (1.00 LT) | oracle | O | 0.0337 | 1.09 [1.03, 1.18] | undetermined (n_eff < 50) | 0.0045 |
| H=30 (1.00 LT) | oracle | I | 0.0464 | 1.5 [1.15, 2.12] | undetermined (n_eff < 50) | 0.0045 |
| H=30 (1.00 LT) | oracle | N | 0.0473 | 1.53 [1.25, 1.96] | undetermined (n_eff < 50) | 0.0045 |
| H=30 (1.00 LT) | oracle | F (ROIN) | 0.0308 | 1 | | |
| H=30 (1.00 LT) | oracle | X | 0.0322 | 1.04 [0.896, 1.2] | undetermined (n_eff < 50) | 0.625 |
| H=30 (1.00 LT) | oracle | X+F | 0.0287 | 0.932 [0.815, 1.04] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | deployable | none | 0.0525 | 1.26 [1.07, 1.53] | substantial | 0.0065 |
| H=30 (1.00 LT) | deployable | A2 (stored) | 0.0524 | 1.26 [1.07, 1.52] | substantial | 0.0065 |
| H=30 (1.00 LT) | deployable | separation | 0.061 | 1.46 [1.18, 1.87] | substantial | 0.0065 |
| H=30 (1.00 LT) | deployable | A4 (stored) | 0.061 | 1.46 [1.18, 1.87] | substantial | 0.0065 |
| H=30 (1.00 LT) | deployable | RO | 0.0434 | 1.04 [0.891, 1.23] | undetermined | 0.918 |
| H=30 (1.00 LT) | deployable | R | 0.0492 | 1.18 [1.02, 1.37] | needed, size not determined | 0.0065 |
| H=30 (1.00 LT) | deployable | O | 0.0552 | 1.32 [1.12, 1.59] | substantial | 0.0065 |
| H=30 (1.00 LT) | deployable | I | 0.0451 | 1.08 [0.926, 1.26] | undetermined | 0.412 |
| H=30 (1.00 LT) | deployable | N | 0.0513 | 1.23 [1.09, 1.45] | substantial | 0.0065 |
| H=30 (1.00 LT) | deployable | A5 (stored) | 0.0469 | 1.12 [0.978, 1.31] | undetermined | 0.063 |
| H=30 (1.00 LT) | deployable | F (ROIN) | 0.0418 | 1 | | |
| H=30 (1.00 LT) | deployable | X | 0.0325 | 0.778 [0.642, 0.905] | lowers | 1 |
| H=30 (1.00 LT) | deployable | A3 (stored) | 0.0401 | 0.96 [0.78, 1.16] | undetermined | 1 |
| H=30 (1.00 LT) | deployable | X+F | 0.0312 | 0.746 [0.615, 0.882] | lowers | 1 |
| H=60 (2.00 LT) | oracle | none | 0.144 | 1.11 [1.04, 1.18] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | separation | 0.134 | 1.03 [0.994, 1.06] | undetermined | 0.04 |
| H=60 (2.00 LT) | oracle | RO | 0.133 | 1.03 [1, 1.06] | needed, size not determined | 0.015 |
| H=60 (2.00 LT) | oracle | R | 0.142 | 1.09 [1.04, 1.15] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | O | 0.134 | 1.03 [0.986, 1.08] | undetermined | 0.0855 |
| H=60 (2.00 LT) | oracle | I | 0.141 | 1.09 [1.03, 1.15] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | oracle | N | 0.141 | 1.08 [1.02, 1.15] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | F (ROIN) | 0.13 | 1 | | |
| H=60 (2.00 LT) | oracle | X | 0.133 | 1.03 [0.977, 1.07] | undetermined | 0.14 |
| H=60 (2.00 LT) | oracle | X+F | 0.13 | 0.997 [0.978, 1.02] | negligible | 0.671 |
| H=60 (2.00 LT) | deployable | none | 0.14 | 1.04 [0.995, 1.08] | undetermined | 0.0455 |
| H=60 (2.00 LT) | deployable | A2 (stored) | 0.14 | 1.03 [0.994, 1.08] | undetermined | 0.0455 |
| H=60 (2.00 LT) | deployable | separation | 0.144 | 1.06 [1.02, 1.11] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | A4 (stored) | 0.144 | 1.06 [1.02, 1.11] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | RO | 0.139 | 1.03 [0.999, 1.06] | undetermined | 0.036 |
| H=60 (2.00 LT) | deployable | R | 0.139 | 1.03 [0.996, 1.07] | undetermined | 0.065 |
| H=60 (2.00 LT) | deployable | O | 0.14 | 1.03 [0.999, 1.08] | undetermined | 0.027 |
| H=60 (2.00 LT) | deployable | I | 0.138 | 1.02 [0.989, 1.06] | undetermined | 0.116 |
| H=60 (2.00 LT) | deployable | N | 0.141 | 1.04 [1.01, 1.08] | needed, size not determined | 0.02 |
| H=60 (2.00 LT) | deployable | F (ROIN) | 0.135 | 1 | | |
| H=60 (2.00 LT) | deployable | X | 0.129 | 0.956 [0.912, 0.996] | lowers | 1 |
| H=60 (2.00 LT) | deployable | A3 (stored) | 0.133 | 0.982 [0.931, 1.03] | negligible | 1 |
| H=60 (2.00 LT) | deployable | X+F | 0.132 | 0.977 [0.941, 1.01] | negligible | 1 |
| H=120 (4.00 LT) | oracle | none | 0.886 | 1.02 [1.01, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | separation | 0.953 | 1.09 [1.07, 1.12] | substantial | 0.0045 |
| H=120 (4.00 LT) | oracle | RO | 0.879 | 1.01 [1, 1.02] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | R | 0.881 | 1.01 [1, 1.02] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | O | 0.882 | 1.01 [1, 1.02] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | I | 0.883 | 1.01 [1, 1.02] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | N | 0.885 | 1.02 [1.01, 1.02] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | F (ROIN) | 0.872 | 1 | | |
| H=120 (4.00 LT) | oracle | X | 0.873 | 1 [0.992, 1.01] | negligible | 0.682 |
| H=120 (4.00 LT) | oracle | X+F | 0.87 | 0.998 [0.991, 1] | negligible | 0.817 |
| H=120 (4.00 LT) | deployable | none | 0.898 | 1.02 [1.01, 1.03] | small | 0.006 |
| H=120 (4.00 LT) | deployable | A2 (stored) | 0.898 | 1.02 [1.01, 1.03] | small | 0.006 |
| H=120 (4.00 LT) | deployable | separation | 0.947 | 1.07 [1.05, 1.09] | substantial | 0.006 |
| H=120 (4.00 LT) | deployable | A4 (stored) | 0.947 | 1.07 [1.05, 1.09] | substantial | 0.006 |
| H=120 (4.00 LT) | deployable | RO | 0.889 | 1.01 [1, 1.01] | small | 0.006 |
| H=120 (4.00 LT) | deployable | R | 0.89 | 1.01 [1, 1.01] | small | 0.006 |
| H=120 (4.00 LT) | deployable | O | 0.892 | 1.01 [1, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | I | 0.893 | 1.01 [1, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | N | 0.895 | 1.01 [1.01, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | F (ROIN) | 0.883 | 1 | | |
| H=120 (4.00 LT) | deployable | X | 0.882 | 0.999 [0.989, 1.01] | negligible | 1 |
| H=120 (4.00 LT) | deployable | A3 (stored) | 0.919 | 1.04 [1.02, 1.06] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | X+F | 0.879 | 0.995 [0.989, 1] | negligible | 1 |

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| horizon | theory gap (upper bound) [CI] | estimation gap [CI] | gap with R estimated | gap with O estimated | gap with I estimated | gap with N estimated |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 0.000984 [7.86e-05, 0.00275] | 0.00547 [0.0033, 0.00809] | -1.08e-05 [-7.81e-05, 5.78e-05] | 0.0037 [0.00239, 0.00527] | -7.68e-05 [-0.000143, -1.53e-05] | -5.48e-05 [-0.000123, 7.09e-06] |
| H=15 (0.50 LT) | 0.00131 [0.000765, 0.0021] | 0.0102 [0.0063, 0.0146] | 0.0015 [-0.000479, 0.00373] | 0.00929 [0.00533, 0.0137] | 0.00185 [-0.000151, 0.00416] | 0.00156 [-0.000483, 0.00388] |
| H=30 (1.00 LT) | 0.0096 [0.00655, 0.0133] | 0.0109 [0.00462, 0.0176] | 0.00129 [-0.00348, 0.00678] | 0.0108 [0.00294, 0.0196] | 0.000899 [-0.00345, 0.00616] | 0.000457 [-0.00401, 0.00592] |
| H=60 (2.00 LT) | 0.0366 [0.0312, 0.0426] | 0.00551 [-0.00592, 0.0164] | 0.000611 [-0.0096, 0.0104] | 0.00632 [-0.00492, 0.017] | -0.000623 [-0.0101, 0.00905] | -0.000949 [-0.0106, 0.00907] |
| H=120 (4.00 LT) | 0.248 [0.237, 0.261] | 0.0111 [-0.0142, 0.0373] | 0.0145 [-0.011, 0.0404] | 0.0136 [-0.0119, 0.0384] | 0.0144 [-0.011, 0.0405] | 0.0161 [-0.0101, 0.0421] |

### Horizon decision (Y = ln min(T_c, H_max))

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED. Pinball loss at tau = 0.5; drop-one ratio at level 1 - 0.05/4; ladder ratio vs F at 1 - 0.05/m; C = Harrell's C (95%); coverage of q_0.1, q_0.5, q_0.9 and the 80% interval below the cap.

| profile | X | pinball ratio [CI] | reading | Holm p | phi [CI] |
|---|---|---|---|---|---|
| oracle | R | 1 [0.99, 1.01] | negligible | 0.477 | 0.0012 [0.000522, 0.00193] |
| oracle | O | 1.1 [1.08, 1.13] | substantial | 0.002 | 0.00912 [0.00751, 0.0108] |
| oracle | I | 1.26 [1.22, 1.31] | substantial | 0.002 | 0.0317 [0.0278, 0.0357] |
| oracle | N | 1.01 [0.994, 1.02] | negligible | 0.16 | 0.00264 [0.00176, 0.00352] |
| deployable | R | 1.01 [1, 1.02] | small | 0.003 | 0.00279 [0.00215, 0.00347] |
| deployable | O | 1.11 [1.08, 1.13] | substantial | 0.002 | 0.0104 [0.00894, 0.012] |
| deployable | I | 1.29 [1.24, 1.34] | substantial | 0.002 | 0.0329 [0.029, 0.037] |
| deployable | N | 1 [0.995, 1.01] | negligible | 0.19 | 0.00157 [0.000975, 0.00213] |

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | ratio vs F [CI] | reading | C [CI] | cov 0.1 / 0.5 / 0.9 / 80% |
|---|---|---|---|---|---|---|
| oracle | none | 0.187 | 1.32 [1.26, 1.37] | substantial | 0.5 [0.5, 0.5] | 0.1 / 0.511 / 0.906 / 0.805 |
| oracle | lyapunov | 0.292 | 2.06 [1.96, 2.17] | substantial | 0.615 [0.604, 0.626] | 0.0701 / 0.475 / 0.841 / 0.808 |
| oracle | RO | 0.183 | 1.29 [1.24, 1.34] | substantial | 0.57 [0.56, 0.58] | 0.132 / 0.493 / 0.895 / 0.763 |
| oracle | R | 0.185 | 1.3 [1.25, 1.36] | substantial | 0.542 [0.532, 0.552] | 0.105 / 0.5 / 0.898 / 0.793 |
| oracle | O | 0.184 | 1.3 [1.24, 1.35] | substantial | 0.552 [0.542, 0.561] | 0.116 / 0.511 / 0.911 / 0.795 |
| oracle | I | 0.162 | 1.14 [1.11, 1.18] | substantial | 0.63 [0.619, 0.641] | 0.105 / 0.501 / 0.901 / 0.796 |
| oracle | N | 0.182 | 1.29 [1.23, 1.34] | substantial | 0.571 [0.561, 0.581] | 0.101 / 0.501 / 0.898 / 0.797 |
| oracle | ROIN | 0.142 | 1 |  | 0.687 [0.676, 0.698] | 0.136 / 0.494 / 0.859 / 0.723 |
| oracle | X | 0.153 | 1.08 [1.03, 1.14] | needed, size not determined | 0.69 [0.68, 0.7] | 0.142 / 0.505 / 0.861 / 0.718 |
| oracle | X+F | 0.122 | 0.858 [0.831, 0.882] | lowers | 0.737 [0.727, 0.747] | 0.152 / 0.506 / 0.852 / 0.7 |
| oracle | Lyapunov rank (C only) | | | | 0.612 [0.601, 0.623] | |
| deployable | none | 0.187 | 1.34 [1.29, 1.4] | substantial | 0.5 [0.5, 0.5] | 0.1 / 0.511 / 0.906 / 0.805 |
| deployable | lyapunov | 0.285 | 2.06 [1.96, 2.17] | substantial | 0.62 [0.609, 0.631] | 0.0691 / 0.48 / 0.848 / 0.815 |
| deployable | RO | 0.18 | 1.3 [1.24, 1.35] | substantial | 0.578 [0.568, 0.587] | 0.12 / 0.501 / 0.903 / 0.783 |
| deployable | R | 0.184 | 1.33 [1.27, 1.39] | substantial | 0.543 [0.534, 0.553] | 0.105 / 0.51 / 0.901 / 0.797 |
| deployable | O | 0.184 | 1.32 [1.27, 1.38] | substantial | 0.549 [0.54, 0.558] | 0.105 / 0.508 / 0.909 / 0.804 |
| deployable | I | 0.164 | 1.18 [1.14, 1.22] | substantial | 0.628 [0.618, 0.638] | 0.103 / 0.502 / 0.902 / 0.799 |
| deployable | N | 0.184 | 1.33 [1.27, 1.39] | substantial | 0.554 [0.547, 0.561] | 0.101 / 0.509 / 0.888 / 0.788 |
| deployable | ROIN | 0.139 | 1 |  | 0.696 [0.685, 0.707] | 0.119 / 0.506 / 0.877 / 0.758 |
| deployable | X | 0.155 | 1.11 [1.06, 1.17] | substantial | 0.688 [0.678, 0.697] | 0.139 / 0.506 / 0.866 / 0.727 |
| deployable | X+F | 0.124 | 0.895 [0.872, 0.921] | lowers | 0.731 [0.72, 0.741] | 0.144 / 0.509 / 0.859 / 0.715 |
| deployable | Lyapunov rank (C only) | | | | 0.616 [0.604, 0.627] | |

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| profile | pair | Delta [CI] | Holm p | detected |
|---|---|---|---|---|
| oracle | RO | -2.18e-05 [-0.00193, 0.0019] | 0.508 | False |
| oracle | RI (primary) | 0.00143 [-0.000537, 0.00325] | 0.134 | False |
| oracle | RN | 0.000537 [-0.000905, 0.00195] | 0.357 | False |
| oracle | OI (primary) | 0.0146 [0.0105, 0.0187] | 0.003 | True |
| oracle | ON | 0.00153 [0.000651, 0.0025] | 0.003 | True |
| oracle | IN | 0.000774 [-0.000913, 0.00238] | 0.357 | False |
| deployable | RO | 0.00141 [0.000663, 0.00218] | 0.003 | True |
| deployable | RI (primary) | 0.00455 [0.00209, 0.00715] | 0.003 | True |
| deployable | RN | 0.000316 [-0.000272, 0.000898] | 0.069 | False |
| deployable | OI (primary) | 0.018 [0.0139, 0.0221] | 0.003 | True |
| deployable | ON | 0.000685 [-0.000127, 0.00144] | 0.031 | True |
| deployable | IN | 0.00092 [-3.35e-05, 0.00179] | 0.0195 | True |

## rossler

**PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.**

| check | result |
|---|---|
| (f1) state_mse from per-draw errors, max rel diff | A0 0.0e+00, A1 0.0e+00, A2 0.0e+00, A3 0.0e+00, A4 0.0e+00, A5 0.0e+00 (within 1e-12: True) |
| (g) WU-0039b (b1), (b2) rows reproduced | drop-N: True, all rows: True |
| separation formula on F-hat vs stored A4 at H_ref, max abs | 2.22e-16 |
| T_c: T = 1 / e_(T-1) = theta (train, test) | 0/0, 0/0 |
| (f2) dependence bias, deployable rows (reported, not gating) | 131 rows; 73 flagged: H=8 R: dependence bias detectable (interval excludes 0), t1+t2 / V 0.013, z 6.81; H=8 O: dependence bias detectable (interval excludes 0), t1+t2 / V 0.000441, z -0.638; H=8 N: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0117, z 5.87; H=8 RO: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0186, z 7.1; H=8 RI: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0128, z 6.79; H=8 RN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0192, z 8.42; H=8 ON: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0125, z 5.39; H=8 IN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.012, z 5.99; H=8 ROI: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0185, z 7.06; H=8 RON: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0235, z 8.18; H=8 RIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0191, z 8.4; H=8 OIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0135, z 5.84 ... |

### A. Allocation: drop-one and Shapley

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED. MSE ratio MSE(F without X)/MSE(F) at level 1 - 0.05/4 (reading by the 1.05 table, with the n_eff guard); excess ratio L_A(F without X)/L_A(F) and Holm p (Delta MSE > 0) are estimates. phi = Shapley share of L_A (95%). Oracle rows: moment form; deployable rows: realized per draw.

| horizon | profile | X | MSE ratio [CI] | reading | excess ratio | Holm p | phi_X [95% CI] | share |
|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | R | 1.05 [1.04, 1.06] | needed, size not determined | 1.52 | 0.002 | 6.45e-06 [5.73e-06, 7.17e-06] | 0.63 |
| H=8 (0.27 LT) | oracle | O | 1.02 [1.01, 1.02] | small | 1.17 | 0.002 | 1.16e-06 [9.37e-07, 1.42e-06] | 0.113 |
| H=8 (0.27 LT) | oracle | I | 1 [1, 1] | negligible | 1 | 0.222 | 1.21e-08 [-5.17e-08, 7.58e-08] | 0.00118 |
| H=8 (0.27 LT) | oracle | N | 1.01 [1.01, 1.01] | small | 1.09 | 0.002 | 2.62e-06 [2.33e-06, 2.92e-06] | 0.256 |
| H=8 (0.27 LT) | deployable | R | 1 [0.996, 1.01] | negligible | 1.01 | 0.424 | -7.66e-08 [-5.94e-07, 4.82e-07] | -0.166 |
| H=8 (0.27 LT) | deployable | O | 1.01 [1, 1.01] | negligible | 1.03 | 0.028 | 4.2e-07 [5.18e-08, 7.98e-07] | 0.907 |
| H=8 (0.27 LT) | deployable | I | 1 [0.999, 1] | negligible | 1 | 0.42 | -8.92e-09 [-9.68e-08, 8.39e-08] | -0.0193 |
| H=8 (0.27 LT) | deployable | N | 1 [0.996, 1] | negligible | 0.999 | 0.534 | 1.29e-07 [-2.67e-07, 5.27e-07] | 0.278 |
| H=15 (0.50 LT) | oracle | R | 1.08 [1.06, 1.09] | substantial | 1.87 | 0.002 | 1.48e-05 [1.31e-05, 1.67e-05] | 0.698 |
| H=15 (0.50 LT) | oracle | O | 1.02 [1.01, 1.03] | small | 1.23 | 0.002 | 2.3e-06 [1.72e-06, 2.94e-06] | 0.108 |
| H=15 (0.50 LT) | oracle | I | 1 [0.999, 1] | negligible | 1 | 0.391 | -1.89e-07 [-3.26e-07, -3.7e-08] | -0.00888 |
| H=15 (0.50 LT) | oracle | N | 1.01 [1.01, 1.01] | small | 1.11 | 0.002 | 4.32e-06 [3.83e-06, 4.82e-06] | 0.203 |
| H=15 (0.50 LT) | deployable | R | 1 [0.991, 1.01] | negligible | 1.01 | 0.883 | -4.68e-07 [-1.85e-06, 9.48e-07] | 0.747 |
| H=15 (0.50 LT) | deployable | O | 1 [0.987, 1.01] | negligible | 1 | 0.883 | -4.26e-08 [-1.66e-06, 1.59e-06] | 0.068 |
| H=15 (0.50 LT) | deployable | I | 1 [0.999, 1] | negligible | 1 | 0.883 | 2.18e-08 [-2.14e-07, 3e-07] | -0.0348 |
| H=15 (0.50 LT) | deployable | N | 1 [0.998, 1.01] | negligible | 1.01 | 0.302 | -1.38e-07 [-1.16e-06, 8.3e-07] | 0.22 |
| H=30 (1.00 LT) | oracle | R | 1.11 [1.09, 1.13] | substantial | 2.23 | 0.002 | 7.21e-05 [6.29e-05, 8.23e-05] | 0.709 |
| H=30 (1.00 LT) | oracle | O | 1.04 [1.03, 1.05] | small | 1.4 | 0.002 | 1.43e-05 [1.13e-05, 1.75e-05] | 0.14 |
| H=30 (1.00 LT) | oracle | I | 1 [0.992, 1.01] | negligible | 1 | 0.456 | 1.51e-06 [2.19e-07, 2.93e-06] | 0.0148 |
| H=30 (1.00 LT) | oracle | N | 1 [0.996, 1.01] | negligible | 1.04 | 0.224 | 1.39e-05 [9.97e-06, 1.76e-05] | 0.136 |
| H=30 (1.00 LT) | deployable | R | 1 [0.987, 1.01] | negligible | 1.01 | 0.604 | -1.9e-06 [-8.13e-06, 4.04e-06] | 3.6 |
| H=30 (1.00 LT) | deployable | O | 1 [0.99, 1.02] | negligible | 1.02 | 0.604 | 1.98e-06 [-3.69e-06, 7.79e-06] | -3.75 |
| H=30 (1.00 LT) | deployable | I | 1 [0.998, 1] | negligible | 1 | 0.604 | 4.77e-07 [-1.3e-06, 2.19e-06] | -0.902 |
| H=30 (1.00 LT) | deployable | N | 1 [0.997, 1.01] | negligible | 1.01 | 0.604 | -1.09e-06 [-6.91e-06, 4.58e-06] | 2.06 |
| H=60 (2.00 LT) | oracle | R | 1.09 [1.06, 1.12] | substantial | 1.43 | 0.002 | 0.00105 [0.000839, 0.00128] | 0.762 |
| H=60 (2.00 LT) | oracle | O | 1.02 [1.01, 1.04] | small | 1.11 | 0.002 | 0.000147 [7.73e-05, 0.000218] | 0.107 |
| H=60 (2.00 LT) | oracle | I | 0.999 [0.994, 1] | negligible | 0.994 | 0.749 | 1.05e-05 [-1.41e-05, 3.46e-05] | 0.00766 |
| H=60 (2.00 LT) | oracle | N | 1 [0.997, 1.01] | negligible | 1.02 | 0.121 | 0.000169 [9.1e-05, 0.000245] | 0.123 |
| H=60 (2.00 LT) | deployable | R | 1 [0.992, 1.02] | negligible | 1.01 | 0.615 | 6.62e-05 [-6.56e-05, 0.000213] | 0.316 |
| H=60 (2.00 LT) | deployable | O | 1.01 [1, 1.01] | small | 1.02 | 0.022 | 7.54e-05 [2.42e-05, 0.000132] | 0.359 |
| H=60 (2.00 LT) | deployable | I | 1 [0.999, 1] | negligible | 1 | 0.615 | 1.84e-05 [3.33e-06, 3.33e-05] | 0.0879 |
| H=60 (2.00 LT) | deployable | N | 1 [0.998, 1] | negligible | 1 | 0.615 | 4.98e-05 [-1.61e-05, 0.000114] | 0.237 |
| H=120 (4.00 LT) | oracle | R | 1.02 [1.01, 1.02] | small | 1.06 | 0.002 | 0.00168 [0.00112, 0.00229] | 0.606 |
| H=120 (4.00 LT) | oracle | O | 1 [1, 1.01] | small | 1.02 | 0.002 | 0.000278 [9.25e-05, 0.000466] | 0.1 |
| H=120 (4.00 LT) | oracle | I | 1.01 [1, 1.01] | small | 1.02 | 0.002 | 0.000722 [0.000385, 0.00109] | 0.26 |
| H=120 (4.00 LT) | oracle | N | 0.999 [0.997, 1] | negligible | 0.998 | 0.749 | 9.47e-05 [-0.000203, 0.000374] | 0.0341 |
| H=120 (4.00 LT) | deployable | R | 1 [0.998, 1] | negligible | 1 | 0.368 | 0.000221 [-8.28e-05, 0.000534] | 0.159 |
| H=120 (4.00 LT) | deployable | O | 1 [0.998, 1.01] | negligible | 1.01 | 0.292 | 0.000249 [-7.23e-05, 0.000581] | 0.179 |
| H=120 (4.00 LT) | deployable | I | 1.01 [1, 1.01] | small | 1.02 | 0.002 | 0.000689 [0.000331, 0.00105] | 0.496 |
| H=120 (4.00 LT) | deployable | N | 1 [0.999, 1] | negligible | 1 | 0.368 | 0.000231 [7.36e-05, 0.000392] | 0.166 |

### A. Allocation: summary per horizon

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED. n_eff = Kish size of kappa on the test states; G = 1 - L_A(rule)/L_A(constant), estimate (95%).

| horizon | profile | n_eff(kappa) | G(F) [CI] | G(separation) | MSE(F)/MSE(sep) [CI] | reading | settings (A) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 647 | 0.464 [0.439, 0.489] | 0.107 | 0.936 [0.927, 0.944] | lowers | F: mid; qn 0, mid 8, low 7 |
| H=8 (0.27 LT) | deployable | 647 | 0.0205 [-0.0211, 0.06] | -0.357 | 0.936 [0.923, 0.948] | lowers | F: mid; qn 0, mid 7, low 8 |
| H=15 (0.50 LT) | oracle | 497 | 0.558 [0.527, 0.588] | 0.262 | 0.945 [0.939, 0.951] | lowers | F: mid; qn 0, mid 9, low 6 |
| H=15 (0.50 LT) | deployable | 497 | -0.0164 [-0.101, 0.0565] | -0.386 | 0.939 [0.927, 0.95] | lowers | F: mid; qn 0, mid 10, low 5 |
| H=30 (1.00 LT) | oracle | 297 | 0.622 [0.59, 0.653] | 0.529 | 0.979 [0.971, 0.987] | lowers | F: mid; qn 2, mid 6, low 7 |
| H=30 (1.00 LT) | deployable | 297 | -0.00311 [-0.0894, 0.07] | -0.156 | 0.969 [0.954, 0.982] | lowers | F: mid; qn 0, mid 8, low 7 |
| H=60 (2.00 LT) | oracle | 458 | 0.366 [0.313, 0.421] | 0.375 | 1 [0.995, 1.01] | negligible | F: mid; qn 0, mid 4, low 11 |
| H=60 (2.00 LT) | deployable | 458 | 0.051 [0.0105, 0.0954] | 0.0464 | 0.999 [0.99, 1.01] | negligible | F: low; qn 0, mid 1, low 14 |
| H=120 (4.00 LT) | oracle | 1.5e+03 | 0.0866 [0.0656, 0.107] | -0.0489 | 0.961 [0.947, 0.976] | lowers | F: low; qn 0, mid 0, low 15 |
| H=120 (4.00 LT) | deployable | 1.5e+03 | 0.0427 [0.0273, 0.0597] | -0.16 | 0.943 [0.926, 0.96] | lowers | F: low; qn 0, mid 0, low 15 |

### B. Allocation: pairwise interactions (logit u, interior states)

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED. Delta = L(additive) - L(additive + pair) on the test states, models fixed; level 1 - 0.05/6; Holm over the six pairs. R x I and O x I are primary.

| horizon | profile | pair | Delta [CI] | Holm p | reading | loss ratio reading |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | RI (primary) | 0.0163 [-0.0104, 0.0423] | 0.098 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | OI (primary) | 0.00804 [-0.00909, 0.0244] | 0.111 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | RO | 0.117 [0.0716, 0.162] | 0.003 | interaction gain detected | needed, size not determined |
| H=8 (0.27 LT) | oracle | RN | 0.0434 [0.0019, 0.0842] | 0.014 | interaction gain detected | small |
| H=8 (0.27 LT) | oracle | ON | 0.0547 [0.0282, 0.0823] | 0.003 | interaction gain detected | small |
| H=8 (0.27 LT) | oracle | IN | 0.0151 [-0.00373, 0.0351] | 0.0525 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RI (primary) | 0.0112 [-0.00522, 0.0298] | 0.075 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | OI (primary) | 0.0305 [0.0152, 0.0457] | 0.003 | interaction gain detected | small |
| H=8 (0.27 LT) | deployable | RO | 0.0996 [0.0649, 0.13] | 0.003 | interaction gain detected | small |
| H=8 (0.27 LT) | deployable | RN | 0.0267 [0.00643, 0.0459] | 0.003 | interaction gain detected | small |
| H=8 (0.27 LT) | deployable | ON | 0.0279 [0.0115, 0.0439] | 0.003 | interaction gain detected | small |
| H=8 (0.27 LT) | deployable | IN | 0.00574 [-0.00694, 0.0184] | 0.12 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | RI (primary) | -0.00331 [-0.0255, 0.0192] | 0.617 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | OI (primary) | 0.0189 [0.00317, 0.0349] | 0.004 | interaction gain detected | small |
| H=15 (0.50 LT) | oracle | RO | 0.0933 [0.0489, 0.136] | 0.003 | interaction gain detected | needed, size not determined |
| H=15 (0.50 LT) | oracle | RN | 0.0191 [-0.013, 0.0511] | 0.171 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | ON | 0.0556 [0.0303, 0.0811] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | oracle | IN | 0.00444 [-0.0131, 0.022] | 0.448 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | RI (primary) | 0.00229 [-0.0165, 0.0239] | 0.367 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | OI (primary) | 0.0234 [0.00358, 0.0438] | 0.004 | interaction gain detected | small |
| H=15 (0.50 LT) | deployable | RO | 0.0682 [0.0287, 0.111] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | deployable | RN | 0.0332 [0.00949, 0.0567] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | deployable | ON | 0.0155 [-0.00059, 0.0315] | 0.0195 | interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | IN | 0.00789 [-0.0042, 0.0191] | 0.085 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | RI (primary) | -0.00524 [-0.0342, 0.0229] | 0.769 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | OI (primary) | 0.00394 [-0.0239, 0.0317] | 0.769 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | RO | 0.118 [0.071, 0.174] | 0.003 | interaction gain detected | needed, size not determined |
| H=30 (1.00 LT) | oracle | RN | 0.0416 [0.0131, 0.0707] | 0.003 | interaction gain detected | small |
| H=30 (1.00 LT) | oracle | ON | 0.0279 [-0.00225, 0.0591] | 0.038 | interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | IN | 0.0108 [-0.00417, 0.0263] | 0.111 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | RI (primary) | 0.0177 [-0.0161, 0.0504] | 0.346 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | OI (primary) | 0.0296 [-0.00216, 0.0597] | 0.0325 | interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | RO | 0.0864 [0.0458, 0.131] | 0.003 | interaction gain detected | small |
| H=30 (1.00 LT) | deployable | RN | 0.00359 [-0.0156, 0.0233] | 0.654 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | ON | 0.00135 [-0.0208, 0.0221] | 0.654 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | IN | 0.00549 [-0.00619, 0.0166] | 0.346 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | RI (primary) | 0.0526 [0.0273, 0.0768] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | oracle | OI (primary) | 0.0234 [0.000265, 0.0461] | 0.012 | interaction gain detected | small |
| H=60 (2.00 LT) | oracle | RO | 0.0981 [0.0541, 0.144] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | oracle | RN | 0.00186 [-0.0266, 0.0327] | 0.434 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | ON | 0.0338 [0.0036, 0.0657] | 0.012 | interaction gain detected | small |
| H=60 (2.00 LT) | oracle | IN | 0.0188 [-0.00663, 0.0455] | 0.051 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | RI (primary) | 0.0189 [-0.00113, 0.0388] | 0.0425 | interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | OI (primary) | 0.0217 [-0.00287, 0.0483] | 0.06 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | RO | 0.0538 [0.0255, 0.0846] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | RN | 0.00804 [-0.0142, 0.0292] | 0.321 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | ON | 0.00297 [-0.0161, 0.0207] | 0.325 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | IN | 0.0105 [-0.00445, 0.0254] | 0.127 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RI (primary) | 0.0162 [0.00322, 0.0291] | 0.006 | interaction gain detected | small |
| H=120 (4.00 LT) | oracle | OI (primary) | 0.00814 [-0.00343, 0.0197] | 0.132 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RO | 0.0168 [0.00326, 0.0303] | 0.006 | interaction gain detected | small |
| H=120 (4.00 LT) | oracle | RN | 0.00685 [-0.0043, 0.0179] | 0.132 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | ON | 0.0073 [-0.00759, 0.0222] | 0.132 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | IN | 0.0147 [0.000468, 0.0284] | 0.016 | interaction gain detected | small |
| H=120 (4.00 LT) | deployable | RI (primary) | 0.00344 [-0.00411, 0.0111] | 0.637 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | OI (primary) | -0.00137 [-0.0364, 0.0325] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RO | 0.00137 [-0.0059, 0.00797] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RN | 0.000788 [-0.00441, 0.00649] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | ON | 8.88e-05 [-0.00847, 0.00888] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | IN | 0.00594 [-0.00601, 0.0162] | 0.531 | no interaction gain detected | negligible |

### D. Allocation ladder (rung against the full profile)

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED. MSE ratio MSE(rung)/MSE(F) at level 1 - 0.05/m (m rungs); Holm p for Delta MSE > 0. Theory gap L_A(oracle F) is an upper bound; estimation gap = L_A(deployable F) - L_A(oracle F) (95%).

| horizon | profile | rung | MSE | MSE ratio vs F [CI] | reading | Holm p |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | none | 0.000126 | 1.09 [1.08, 1.1] | substantial | 0.0045 |
| H=8 (0.27 LT) | oracle | separation | 0.000123 | 1.07 [1.05, 1.08] | substantial | 0.0045 |
| H=8 (0.27 LT) | oracle | RO | 0.000116 | 1.01 [1.01, 1.01] | small | 0.0045 |
| H=8 (0.27 LT) | oracle | R | 0.000119 | 1.03 [1.03, 1.04] | small | 0.0045 |
| H=8 (0.27 LT) | oracle | O | 0.000126 | 1.09 [1.08, 1.1] | substantial | 0.0045 |
| H=8 (0.27 LT) | oracle | I | 0.000126 | 1.09 [1.08, 1.1] | substantial | 0.0045 |
| H=8 (0.27 LT) | oracle | N | 0.000122 | 1.05 [1.05, 1.07] | needed, size not determined | 0.0045 |
| H=8 (0.27 LT) | oracle | F (ROIN) | 0.000115 | 1 | | |
| H=8 (0.27 LT) | oracle | X | 0.000124 | 1.08 [1.07, 1.09] | substantial | 0.0045 |
| H=8 (0.27 LT) | oracle | X+F | 0.000115 | 0.996 [0.994, 0.998] | lowers | 1 |
| H=8 (0.27 LT) | deployable | none | 0.000126 | 1 [0.993, 1.01] | negligible | 1 |
| H=8 (0.27 LT) | deployable | A2 (stored) | 0.000126 | 1 [0.993, 1.01] | negligible | 1 |
| H=8 (0.27 LT) | deployable | separation | 0.000134 | 1.07 [1.05, 1.09] | needed, size not determined | 0.006 |
| H=8 (0.27 LT) | deployable | A4 (stored) | 0.000134 | 1.07 [1.05, 1.09] | needed, size not determined | 0.006 |
| H=8 (0.27 LT) | deployable | RO | 0.000126 | 1 [0.995, 1] | negligible | 1 |
| H=8 (0.27 LT) | deployable | R | 0.000127 | 1.01 [1, 1.02] | negligible | 0.0315 |
| H=8 (0.27 LT) | deployable | O | 0.000126 | 1 [0.993, 1.01] | negligible | 1 |
| H=8 (0.27 LT) | deployable | I | 0.000126 | 1 [0.994, 1.01] | negligible | 1 |
| H=8 (0.27 LT) | deployable | N | 0.000126 | 1 [0.994, 1.01] | negligible | 1 |
| H=8 (0.27 LT) | deployable | F (ROIN) | 0.000126 | 1 | | |
| H=8 (0.27 LT) | deployable | X | 0.000125 | 0.993 [0.983, 1.01] | negligible | 1 |
| H=8 (0.27 LT) | deployable | A3 (stored) | 0.000131 | 1.04 [1.02, 1.07] | needed, size not determined | 0.006 |
| H=8 (0.27 LT) | deployable | X+F | 0.000125 | 0.993 [0.989, 0.998] | lowers | 1 |
| H=15 (0.50 LT) | oracle | none | 0.000216 | 1.11 [1.09, 1.13] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | separation | 0.000206 | 1.06 [1.05, 1.07] | needed, size not determined | 0.0045 |
| H=15 (0.50 LT) | oracle | RO | 0.000196 | 1.01 [1.01, 1.01] | small | 0.0045 |
| H=15 (0.50 LT) | oracle | R | 0.000201 | 1.03 [1.03, 1.04] | small | 0.0045 |
| H=15 (0.50 LT) | oracle | O | 0.000216 | 1.11 [1.09, 1.13] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | I | 0.000217 | 1.11 [1.1, 1.13] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | N | 0.00021 | 1.08 [1.06, 1.09] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | F (ROIN) | 0.000195 | 1 | | |
| H=15 (0.50 LT) | oracle | X | 0.000215 | 1.11 [1.09, 1.12] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | X+F | 0.000194 | 0.999 [0.998, 1] | negligible | 0.887 |
| H=15 (0.50 LT) | deployable | none | 0.000216 | 0.997 [0.977, 1.02] | negligible | 1 |
| H=15 (0.50 LT) | deployable | A2 (stored) | 0.000216 | 0.998 [0.978, 1.02] | negligible | 1 |
| H=15 (0.50 LT) | deployable | separation | 0.000231 | 1.07 [1.05, 1.08] | needed, size not determined | 0.006 |
| H=15 (0.50 LT) | deployable | A4 (stored) | 0.000231 | 1.07 [1.05, 1.08] | needed, size not determined | 0.006 |
| H=15 (0.50 LT) | deployable | RO | 0.000217 | 1 [0.996, 1.01] | negligible | 1 |
| H=15 (0.50 LT) | deployable | R | 0.000217 | 1 [0.985, 1.02] | negligible | 1 |
| H=15 (0.50 LT) | deployable | O | 0.000216 | 0.997 [0.981, 1.01] | negligible | 1 |
| H=15 (0.50 LT) | deployable | I | 0.000216 | 0.998 [0.979, 1.02] | negligible | 1 |
| H=15 (0.50 LT) | deployable | N | 0.000217 | 1 [0.985, 1.02] | negligible | 1 |
| H=15 (0.50 LT) | deployable | F (ROIN) | 0.000217 | 1 | | |
| H=15 (0.50 LT) | deployable | X | 0.000215 | 0.991 [0.972, 1.01] | negligible | 1 |
| H=15 (0.50 LT) | deployable | A3 (stored) | 0.000235 | 1.08 [1.05, 1.12] | needed, size not determined | 0.006 |
| H=15 (0.50 LT) | deployable | X+F | 0.000215 | 0.992 [0.987, 0.997] | lowers | 1 |
| H=30 (1.00 LT) | oracle | none | 0.000793 | 1.15 [1.12, 1.18] | substantial | 0.0045 |
| H=30 (1.00 LT) | oracle | separation | 0.000706 | 1.02 [1.01, 1.03] | small | 0.0045 |
| H=30 (1.00 LT) | oracle | RO | 0.000695 | 1.01 [1, 1.01] | small | 0.0045 |
| H=30 (1.00 LT) | oracle | R | 0.000728 | 1.05 [1.04, 1.07] | needed, size not determined | 0.0045 |
| H=30 (1.00 LT) | oracle | O | 0.000791 | 1.14 [1.12, 1.17] | substantial | 0.0045 |
| H=30 (1.00 LT) | oracle | I | 0.000791 | 1.15 [1.12, 1.17] | substantial | 0.0045 |
| H=30 (1.00 LT) | oracle | N | 0.000771 | 1.12 [1.09, 1.14] | substantial | 0.0045 |
| H=30 (1.00 LT) | oracle | F (ROIN) | 0.000691 | 1 | | |
| H=30 (1.00 LT) | oracle | X | 0.000791 | 1.15 [1.12, 1.17] | substantial | 0.0045 |
| H=30 (1.00 LT) | oracle | X+F | 0.000689 | 0.998 [0.988, 1.01] | negligible | 0.743 |
| H=30 (1.00 LT) | deployable | none | 0.000799 | 0.999 [0.976, 1.02] | negligible | 1 |
| H=30 (1.00 LT) | deployable | A2 (stored) | 0.000799 | 1 [0.976, 1.02] | negligible | 1 |
| H=30 (1.00 LT) | deployable | separation | 0.000825 | 1.03 [1.01, 1.05] | needed, size not determined | 0.0065 |
| H=30 (1.00 LT) | deployable | A4 (stored) | 0.000825 | 1.03 [1.01, 1.05] | needed, size not determined | 0.0065 |
| H=30 (1.00 LT) | deployable | RO | 0.000802 | 1 [0.995, 1.01] | negligible | 1 |
| H=30 (1.00 LT) | deployable | R | 0.000803 | 1 [0.983, 1.03] | negligible | 1 |
| H=30 (1.00 LT) | deployable | O | 0.000796 | 0.995 [0.972, 1.02] | negligible | 1 |
| H=30 (1.00 LT) | deployable | I | 0.0008 | 1 [0.976, 1.02] | negligible | 1 |
| H=30 (1.00 LT) | deployable | N | 0.000802 | 1 [0.984, 1.02] | negligible | 1 |
| H=30 (1.00 LT) | deployable | A5 (stored) | 0.000807 | 1.01 [0.991, 1.03] | negligible | 0.695 |
| H=30 (1.00 LT) | deployable | F (ROIN) | 0.000799 | 1 | | |
| H=30 (1.00 LT) | deployable | X | 0.000787 | 0.984 [0.962, 1] | negligible | 1 |
| H=30 (1.00 LT) | deployable | A3 (stored) | 0.000858 | 1.07 [1.02, 1.14] | needed, size not determined | 0.011 |
| H=30 (1.00 LT) | deployable | X+F | 0.00079 | 0.989 [0.98, 0.998] | lowers | 1 |
| H=60 (2.00 LT) | oracle | none | 0.0127 | 1.12 [1.09, 1.16] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | separation | 0.0113 | 0.997 [0.983, 1.01] | negligible | 0.766 |
| H=60 (2.00 LT) | oracle | RO | 0.0114 | 1 [0.992, 1.01] | negligible | 0.687 |
| H=60 (2.00 LT) | oracle | R | 0.0117 | 1.03 [1.01, 1.05] | small | 0.0045 |
| H=60 (2.00 LT) | oracle | O | 0.0127 | 1.12 [1.09, 1.16] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | I | 0.0127 | 1.12 [1.09, 1.16] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | N | 0.0125 | 1.1 [1.07, 1.13] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | F (ROIN) | 0.0114 | 1 | | |
| H=60 (2.00 LT) | oracle | X | 0.0127 | 1.12 [1.09, 1.16] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | X+F | 0.0115 | 1.01 [0.999, 1.02] | negligible | 0.015 |
| H=60 (2.00 LT) | deployable | none | 0.0131 | 1.02 [0.998, 1.04] | negligible | 0.105 |
| H=60 (2.00 LT) | deployable | A2 (stored) | 0.0131 | 1.02 [0.998, 1.04] | negligible | 0.105 |
| H=60 (2.00 LT) | deployable | separation | 0.0129 | 1 [0.989, 1.01] | negligible | 1 |
| H=60 (2.00 LT) | deployable | A4 (stored) | 0.0129 | 1 [0.989, 1.01] | negligible | 1 |
| H=60 (2.00 LT) | deployable | RO | 0.0129 | 1 [0.998, 1] | negligible | 1 |
| H=60 (2.00 LT) | deployable | R | 0.013 | 1.01 [1, 1.02] | small | 0.006 |
| H=60 (2.00 LT) | deployable | O | 0.013 | 1.01 [0.99, 1.03] | negligible | 0.445 |
| H=60 (2.00 LT) | deployable | I | 0.013 | 1.01 [0.992, 1.03] | negligible | 0.28 |
| H=60 (2.00 LT) | deployable | N | 0.013 | 1.01 [0.993, 1.03] | negligible | 0.363 |
| H=60 (2.00 LT) | deployable | F (ROIN) | 0.0129 | 1 | | |
| H=60 (2.00 LT) | deployable | X | 0.0131 | 1.02 [0.994, 1.04] | negligible | 0.116 |
| H=60 (2.00 LT) | deployable | A3 (stored) | 0.0132 | 1.03 [0.997, 1.06] | undetermined | 0.055 |
| H=60 (2.00 LT) | deployable | X+F | 0.0129 | 1 [0.996, 1.01] | negligible | 1 |
| H=120 (4.00 LT) | oracle | none | 0.11 | 1.03 [1.02, 1.04] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | separation | 0.111 | 1.04 [1.02, 1.06] | needed, size not determined | 0.0045 |
| H=120 (4.00 LT) | oracle | RO | 0.108 | 1.01 [1, 1.01] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | R | 0.108 | 1.01 [1, 1.02] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | O | 0.11 | 1.03 [1.02, 1.04] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | I | 0.109 | 1.02 [1.01, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | N | 0.11 | 1.02 [1.02, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | F (ROIN) | 0.107 | 1 | | |
| H=120 (4.00 LT) | oracle | X | 0.11 | 1.02 [1.01, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | X+F | 0.107 | 1 [0.998, 1] | negligible | 0.203 |
| H=120 (4.00 LT) | deployable | none | 0.11 | 1.01 [1.01, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | A2 (stored) | 0.11 | 1.01 [1.01, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | separation | 0.115 | 1.06 [1.03, 1.09] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | A4 (stored) | 0.115 | 1.06 [1.03, 1.09] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | RO | 0.109 | 1.01 [1, 1.01] | small | 0.006 |
| H=120 (4.00 LT) | deployable | R | 0.11 | 1.01 [1, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | O | 0.11 | 1.01 [1, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | I | 0.109 | 1.01 [1, 1.01] | negligible | 0.007 |
| H=120 (4.00 LT) | deployable | N | 0.11 | 1.01 [1, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | F (ROIN) | 0.109 | 1 | | |
| H=120 (4.00 LT) | deployable | X | 0.11 | 1.01 [1, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | A3 (stored) | 0.111 | 1.02 [1.01, 1.04] | small | 0.006 |
| H=120 (4.00 LT) | deployable | X+F | 0.109 | 1 [0.996, 1] | negligible | 0.413 |

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| horizon | theory gap (upper bound) [CI] | estimation gap [CI] | gap with R estimated | gap with O estimated | gap with I estimated | gap with N estimated |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 1.18e-05 [1.1e-05, 1.27e-05] | 1.03e-05 [6.52e-06, 1.43e-05] | 6.37e-06 [2.74e-06, 1.02e-05] | 1.69e-07 [-3.25e-06, 3.73e-06] | 3.18e-07 [-3.11e-06, 3.88e-06] | 1.85e-06 [-1.62e-06, 5.61e-06] |
| H=15 (0.50 LT) | 1.68e-05 [1.56e-05, 1.82e-05] | 2.2e-05 [1.43e-05, 2.98e-05] | 1.48e-05 [7.14e-06, 2.25e-05] | -1.96e-06 [-8.75e-06, 5.29e-06] | -1.54e-06 [-8.22e-06, 5.75e-06] | 1.21e-06 [-5.63e-06, 8.55e-06] |
| H=30 (1.00 LT) | 6.2e-05 [5.58e-05, 6.83e-05] | 0.000109 [7.47e-05, 0.000144] | 8.39e-05 [5.08e-05, 0.000118] | 9.18e-06 [-2.17e-05, 4.15e-05] | 9.7e-06 [-2.07e-05, 4.15e-05] | 1.38e-05 [-1.73e-05, 4.66e-05] |
| H=60 (2.00 LT) | 0.00238 [0.00212, 0.00267] | 0.00153 [0.000781, 0.00232] | 0.00129 [0.000568, 0.00205] | 0.000489 [-0.000218, 0.00117] | 0.000371 [-0.000331, 0.00106] | 0.0004 [-0.000318, 0.00109] |
| H=120 (4.00 LT) | 0.0293 [0.0276, 0.0311] | 0.00186 [-0.00107, 0.00466] | 0.00184 [-0.00102, 0.00467] | 0.00038 [-0.00242, 0.00317] | 0.000618 [-0.00221, 0.00342] | 0.000484 [-0.0023, 0.00323] |

### Horizon decision (Y = ln min(T_c, H_max))

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED. Pinball loss at tau = 0.5; drop-one ratio at level 1 - 0.05/4; ladder ratio vs F at 1 - 0.05/m; C = Harrell's C (95%); coverage of q_0.1, q_0.5, q_0.9 and the 80% interval below the cap.

| profile | X | pinball ratio [CI] | reading | Holm p | phi [CI] |
|---|---|---|---|---|---|
| oracle | R | 1.01 [0.997, 1.02] | negligible | 0.032 | 0.000705 [-6.13e-05, 0.00144] |
| oracle | O | 1.12 [1.1, 1.14] | substantial | 0.002 | 0.0104 [0.00892, 0.0119] |
| oracle | I | 1.26 [1.22, 1.3] | substantial | 0.002 | 0.026 [0.023, 0.0289] |
| oracle | N | 1.01 [1, 1.02] | small | 0.003 | 0.0014 [0.000504, 0.00229] |
| deployable | R | 1 [0.995, 1.01] | negligible | 0.468 | 0.0013 [0.00076, 0.00184] |
| deployable | O | 1.13 [1.11, 1.15] | substantial | 0.002 | 0.0146 [0.0129, 0.0165] |
| deployable | I | 1.24 [1.2, 1.27] | substantial | 0.002 | 0.0241 [0.0213, 0.0267] |
| deployable | N | 1.01 [1, 1.01] | negligible | 0.015 | 0.00123 [0.000666, 0.00179] |

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | ratio vs F [CI] | reading | C [CI] | cov 0.1 / 0.5 / 0.9 / 80% |
|---|---|---|---|---|---|---|
| oracle | none | 0.161 | 1.31 [1.26, 1.36] | substantial | 0.5 [0.5, 0.5] | 0.102 / 0.496 / 0.914 / 0.812 |
| oracle | lyapunov | 0.172 | 1.4 [1.35, 1.46] | substantial | 0.631 [0.621, 0.641] | 0.0664 / 0.473 / 0.877 / 0.845 |
| oracle | RO | 0.156 | 1.27 [1.23, 1.32] | substantial | 0.571 [0.561, 0.58] | 0.0998 / 0.502 / 0.912 / 0.812 |
| oracle | R | 0.162 | 1.32 [1.27, 1.37] | substantial | 0.519 [0.509, 0.529] | 0.105 / 0.5 / 0.911 / 0.806 |
| oracle | O | 0.155 | 1.27 [1.23, 1.32] | substantial | 0.57 [0.56, 0.579] | 0.0945 / 0.502 / 0.913 / 0.819 |
| oracle | I | 0.141 | 1.15 [1.12, 1.19] | substantial | 0.621 [0.61, 0.631] | 0.103 / 0.498 / 0.908 / 0.805 |
| oracle | N | 0.16 | 1.31 [1.26, 1.36] | substantial | 0.525 [0.514, 0.534] | 0.113 / 0.499 / 0.909 / 0.796 |
| oracle | ROIN | 0.122 | 1 |  | 0.681 [0.671, 0.69] | 0.105 / 0.505 / 0.9 / 0.795 |
| oracle | X | 0.121 | 0.989 [0.952, 1.03] | negligible | 0.7 [0.692, 0.708] | 0.15 / 0.516 / 0.914 / 0.764 |
| oracle | X+F | 0.0936 | 0.765 [0.743, 0.788] | lowers | 0.769 [0.761, 0.776] | 0.144 / 0.52 / 0.866 / 0.721 |
| oracle | Lyapunov rank (C only) | | | | 0.629 [0.619, 0.639] | |
| deployable | none | 0.161 | 1.34 [1.3, 1.4] | substantial | 0.5 [0.5, 0.5] | 0.102 / 0.496 / 0.914 / 0.812 |
| deployable | lyapunov | 0.173 | 1.45 [1.4, 1.5] | substantial | 0.626 [0.615, 0.635] | 0.0678 / 0.467 / 0.876 / 0.845 |
| deployable | RO | 0.149 | 1.24 [1.21, 1.28] | substantial | 0.601 [0.592, 0.611] | 0.106 / 0.503 / 0.911 / 0.805 |
| deployable | R | 0.16 | 1.34 [1.29, 1.39] | substantial | 0.526 [0.518, 0.534] | 0.1 / 0.501 / 0.916 / 0.815 |
| deployable | O | 0.149 | 1.25 [1.21, 1.29] | substantial | 0.6 [0.591, 0.61] | 0.117 / 0.503 / 0.912 / 0.795 |
| deployable | I | 0.142 | 1.19 [1.16, 1.22] | substantial | 0.62 [0.61, 0.63] | 0.0968 / 0.498 / 0.902 / 0.805 |
| deployable | N | 0.159 | 1.33 [1.28, 1.38] | substantial | 0.528 [0.52, 0.536] | 0.104 / 0.496 / 0.91 / 0.807 |
| deployable | ROIN | 0.12 | 1 |  | 0.691 [0.683, 0.7] | 0.122 / 0.506 / 0.884 / 0.762 |
| deployable | X | 0.123 | 1.03 [0.989, 1.06] | undetermined | 0.695 [0.687, 0.703] | 0.142 / 0.516 / 0.915 / 0.773 |
| deployable | X+F | 0.0909 | 0.759 [0.735, 0.781] | lowers | 0.771 [0.764, 0.778] | 0.142 / 0.502 / 0.877 / 0.735 |
| deployable | Lyapunov rank (C only) | | | | 0.624 [0.613, 0.633] | |

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| profile | pair | Delta [CI] | Holm p | detected |
|---|---|---|---|---|
| oracle | RO | 0.000451 [-0.000103, 0.000986] | 0.06 | False |
| oracle | RI (primary) | 0.000669 [-0.000434, 0.00178] | 0.102 | False |
| oracle | RN | 0.0011 [0.000642, 0.00157] | 0.003 | True |
| oracle | OI (primary) | 0.0083 [0.00603, 0.0107] | 0.003 | True |
| oracle | ON | 0.000555 [-6.63e-05, 0.00114] | 0.048 | True |
| oracle | IN | 0.00063 [-0.000345, 0.00165] | 0.102 | False |
| deployable | RO | 0.000941 [0.000266, 0.00166] | 0.003 | True |
| deployable | RI (primary) | 0.00146 [0.000254, 0.00273] | 0.003 | True |
| deployable | RN | 0.000348 [2.18e-05, 0.000686] | 0.012 | True |
| deployable | OI (primary) | 0.0109 [0.00891, 0.013] | 0.003 | True |
| deployable | ON | 0.000545 [-0.000203, 0.00116] | 0.044 | True |
| deployable | IN | 0.00032 [-0.000467, 0.00111] | 0.156 | False |

## chua

**PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.**

| check | result |
|---|---|
| (f1) state_mse from per-draw errors, max rel diff | A0 0.0e+00, A1 0.0e+00, A2 0.0e+00, A3 0.0e+00, A4 0.0e+00, A5 0.0e+00 (within 1e-12: True) |
| (g) WU-0039b (b1), (b2) rows reproduced | drop-N: True, all rows: True |
| separation formula on F-hat vs stored A4 at H_ref, max abs | 2.22e-16 |
| T_c: T = 1 / e_(T-1) = theta (train, test) | 1/0, 0/0 |
| (f2) dependence bias, deployable rows (reported, not gating) | 131 rows; 38 flagged: H=8 R: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0063, z -0.0647; H=8 N: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0139, z 1.67; H=8 RO: dependence bias detectable (interval excludes 0), t1+t2 / V 0.00553, z 1.09; H=8 RN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0159, z 1.98; H=8 ON: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0133, z 1.31; H=8 IN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0169, z 0.804; H=8 RON: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0148, z 1.7; H=8 RIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0184, z 0.915; H=8 OIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0163, z 0.783; H=8 ROIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0177, z 0.972; H=8 X+F: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0108, z 0.493; H=15 swap-R: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0107, z 1.13 ... |

### A. Allocation: drop-one and Shapley

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED. MSE ratio MSE(F without X)/MSE(F) at level 1 - 0.05/4 (reading by the 1.05 table, with the n_eff guard); excess ratio L_A(F without X)/L_A(F) and Holm p (Delta MSE > 0) are estimates. phi = Shapley share of L_A (95%). Oracle rows: moment form; deployable rows: realized per draw.

| horizon | profile | X | MSE ratio [CI] | reading | excess ratio | Holm p | phi_X [95% CI] | share |
|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | R | 1.07 [1.02, 1.09] | undetermined (n_eff < 50) | 1.14 | 0.002 | 9.66e-06 [-3.45e-05, 3.79e-05] | -0.023 |
| H=8 (0.27 LT) | oracle | O | 0.638 [0.267, 1.33] | undetermined (n_eff < 50) | 0.298 | 1 | -0.000397 [-0.00116, 3.99e-05] | 0.948 |
| H=8 (0.27 LT) | oracle | I | 1.08 [0.964, 1.15] | undetermined (n_eff < 50) | 1.16 | 0.462 | -7.24e-06 [-7.23e-05, 7.57e-05] | 0.0173 |
| H=8 (0.27 LT) | oracle | N | 0.874 [0.48, 1.9] | undetermined (n_eff < 50) | 0.755 | 1 | -2.41e-05 [-0.000353, 0.000239] | 0.0575 |
| H=8 (0.27 LT) | deployable | R | 1.01 [1, 1.02] | undetermined (n_eff < 50) | 1.05 | 0.006 | -2.61e-05 [-5.76e-05, -4.07e-06] | 0.865 |
| H=8 (0.27 LT) | deployable | O | 1.01 [1, 1.02] | undetermined (n_eff < 50) | 1.04 | 0.039 | 5.89e-06 [-1.59e-06, 1.58e-05] | -0.195 |
| H=8 (0.27 LT) | deployable | I | 0.972 [0.925, 1.01] | undetermined (n_eff < 50) | 0.852 | 1 | -9e-06 [-2.65e-05, 8.26e-06] | 0.298 |
| H=8 (0.27 LT) | deployable | N | 0.985 [0.96, 1.01] | undetermined (n_eff < 50) | 0.923 | 1 | -9.58e-07 [-1.2e-05, 1.06e-05] | 0.0318 |
| H=15 (0.50 LT) | oracle | R | 1.02 [0.776, 1.21] | undetermined (n_eff < 50) | 1.07 | 1 | 8.81e-05 [-0.00014, 0.000239] | -0.174 |
| H=15 (0.50 LT) | oracle | O | 0.806 [0.599, 1.02] | undetermined (n_eff < 50) | 0.424 | 1 | -0.0003 [-0.00064, -5.06e-05] | 0.595 |
| H=15 (0.50 LT) | oracle | I | 0.854 [0.676, 1.02] | undetermined (n_eff < 50) | 0.567 | 1 | -0.000226 [-0.000435, -7.24e-05] | 0.448 |
| H=15 (0.50 LT) | oracle | N | 0.937 [0.743, 1.1] | undetermined (n_eff < 50) | 0.812 | 1 | -6.64e-05 [-0.00024, 6.32e-05] | 0.131 |
| H=15 (0.50 LT) | deployable | R | 0.958 [0.876, 1.01] | undetermined (n_eff < 50) | 0.824 | 1 | -6.6e-05 [-0.000209, 2.73e-05] | 0.416 |
| H=15 (0.50 LT) | deployable | O | 0.996 [0.94, 1.03] | undetermined (n_eff < 50) | 0.981 | 1 | -1.35e-05 [-8.54e-05, 4.3e-05] | 0.0847 |
| H=15 (0.50 LT) | deployable | I | 0.98 [0.953, 1] | undetermined (n_eff < 50) | 0.918 | 1 | -0.000131 [-0.000249, -3.84e-05] | 0.821 |
| H=15 (0.50 LT) | deployable | N | 1.02 [1, 1.04] | undetermined (n_eff < 50) | 1.07 | 0.004 | 5.11e-05 [1.98e-05, 8.62e-05] | -0.322 |
| H=30 (1.00 LT) | oracle | R | 0.951 [0.853, 1.05] | undetermined (n_eff < 50) | 0.851 | 1 | -0.000478 [-0.00168, 0.000565] | 1.04 |
| H=30 (1.00 LT) | oracle | O | 1.03 [0.921, 1.11] | undetermined (n_eff < 50) | 1.08 | 0.99 | 0.000221 [-0.0005, 0.000869] | -0.482 |
| H=30 (1.00 LT) | oracle | I | 0.979 [0.944, 1] | undetermined (n_eff < 50) | 0.937 | 1 | -0.000102 [-0.000296, 4.69e-05] | 0.222 |
| H=30 (1.00 LT) | oracle | N | 0.994 [0.91, 1.09] | undetermined (n_eff < 50) | 0.982 | 1 | -9.9e-05 [-0.000728, 0.000505] | 0.216 |
| H=30 (1.00 LT) | deployable | R | 0.988 [0.957, 1.01] | undetermined (n_eff < 50) | 0.97 | 1 | 2.39e-05 [-0.000351, 0.00039] | -0.599 |
| H=30 (1.00 LT) | deployable | O | 0.993 [0.977, 1] | undetermined (n_eff < 50) | 0.983 | 1 | -7.25e-05 [-0.000222, 4.84e-05] | 1.82 |
| H=30 (1.00 LT) | deployable | I | 0.998 [0.992, 1] | undetermined (n_eff < 50) | 0.995 | 1 | 5.11e-05 [-3.41e-05, 0.000145] | -1.28 |
| H=30 (1.00 LT) | deployable | N | 0.996 [0.978, 1.01] | undetermined (n_eff < 50) | 0.989 | 1 | -4.25e-05 [-0.000295, 0.000174] | 1.06 |
| H=60 (2.00 LT) | oracle | R | 1.03 [1.01, 1.05] | needed, size not determined | 1.11 | 0.002 | 0.00653 [0.00444, 0.00867] | 0.522 |
| H=60 (2.00 LT) | oracle | O | 1.02 [0.999, 1.04] | negligible | 1.06 | 0.027 | 0.00416 [0.0023, 0.00596] | 0.332 |
| H=60 (2.00 LT) | oracle | I | 0.999 [0.988, 1.01] | negligible | 0.996 | 1 | 0.000931 [9.98e-05, 0.00177] | 0.0743 |
| H=60 (2.00 LT) | oracle | N | 0.997 [0.99, 1.01] | negligible | 0.991 | 1 | 0.000904 [0.000332, 0.00151] | 0.0722 |
| H=60 (2.00 LT) | deployable | R | 0.999 [0.987, 1.01] | negligible | 0.997 | 1 | 0.000532 [-0.000827, 0.00204] | 0.0548 |
| H=60 (2.00 LT) | deployable | O | 1.03 [1.01, 1.04] | small | 1.08 | 0.003 | 0.00542 [0.00313, 0.00755] | 0.558 |
| H=60 (2.00 LT) | deployable | I | 1.01 [1, 1.03] | small | 1.05 | 0.002 | 0.00231 [0.000977, 0.00361] | 0.238 |
| H=60 (2.00 LT) | deployable | N | 0.998 [0.992, 1] | negligible | 0.994 | 1 | 0.00145 [0.000403, 0.00252] | 0.149 |
| H=120 (4.00 LT) | oracle | R | 1.01 [1, 1.02] | small | 1.03 | 0.0045 | 0.00716 [0.00357, 0.0107] | 0.528 |
| H=120 (4.00 LT) | oracle | O | 1 [1, 1] | negligible | 1.01 | 0.02 | 0.00195 [0.000806, 0.0032] | 0.144 |
| H=120 (4.00 LT) | oracle | I | 1 [1, 1] | small | 1.01 | 0.004 | 0.00303 [0.0017, 0.00443] | 0.223 |
| H=120 (4.00 LT) | oracle | N | 1 [0.999, 1] | negligible | 0.999 | 0.754 | 0.00142 [0.000258, 0.00264] | 0.105 |
| H=120 (4.00 LT) | deployable | R | 1 [0.999, 1.01] | negligible | 1.01 | 0.053 | 0.00371 [0.00105, 0.00645] | 0.3 |
| H=120 (4.00 LT) | deployable | O | 1.01 [1, 1.01] | small | 1.02 | 0.0165 | 0.0032 [0.00122, 0.00529] | 0.259 |
| H=120 (4.00 LT) | deployable | I | 1.01 [1, 1.01] | small | 1.02 | 0.016 | 0.00413 [0.00198, 0.00628] | 0.334 |
| H=120 (4.00 LT) | deployable | N | 0.999 [0.997, 1] | negligible | 0.997 | 0.913 | 0.00132 [0.00012, 0.00257] | 0.107 |

### A. Allocation: summary per horizon

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED. n_eff = Kish size of kappa on the test states; G = 1 - L_A(rule)/L_A(constant), estimate (95%).

| horizon | profile | n_eff(kappa) | G(F) [CI] | G(separation) | MSE(F)/MSE(sep) [CI] | reading | settings (A) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 31.5 | -3.46 [-12.7, 0.494] | 0.237 | 1.75 [0.95, 3.31] | undetermined (n_eff < 50) | F: qn; qn 7, mid 3, low 5 |
| H=8 (0.27 LT) | deployable | 31.5 | -0.336 [-0.803, -0.115] | -0.884 | 0.927 [0.887, 0.974] | undetermined (n_eff < 50) | F: low; qn 1, mid 0, low 14 |
| H=15 (0.50 LT) | oracle | 61.3 | -0.896 [-2.46, 0.124] | 0.285 | 1.27 [1.04, 1.59] | needed, size not determined | F: qn; qn 3, mid 0, low 12 |
| H=15 (0.50 LT) | deployable | 61.3 | -0.32 [-0.991, -0.0627] | -0.374 | 0.99 [0.944, 1.05] | negligible | F: low; qn 0, mid 0, low 15 |
| H=30 (1.00 LT) | oracle | 188 | -0.0916 [-0.531, 0.193] | 0.26 | 1.12 [1.03, 1.23] | undetermined (n_eff < 50) | F: mid; qn 0, mid 5, low 10 |
| H=30 (1.00 LT) | deployable | 188 | -0.00547 [-0.088, 0.0602] | 0.0482 | 1.02 [0.997, 1.05] | undetermined (n_eff < 50) | F: low; qn 0, mid 0, low 15 |
| H=60 (2.00 LT) | oracle | 837 | 0.184 [0.134, 0.232] | 0.141 | 0.984 [0.967, 1] | negligible | F: mid; qn 0, mid 2, low 13 |
| H=60 (2.00 LT) | deployable | 837 | 0.14 [0.0848, 0.195] | -0.0118 | 0.947 [0.929, 0.966] | lowers | F: mid; qn 0, mid 6, low 9 |
| H=120 (4.00 LT) | oracle | 2.01e+03 | 0.073 [0.0503, 0.096] | -0.0954 | 0.953 [0.944, 0.961] | lowers | F: low; qn 0, mid 0, low 15 |
| H=120 (4.00 LT) | deployable | 2.01e+03 | 0.0664 [0.0403, 0.0937] | -0.154 | 0.939 [0.927, 0.951] | lowers | F: mid; qn 0, mid 4, low 11 |

### B. Allocation: pairwise interactions (logit u, interior states)

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED. Delta = L(additive) - L(additive + pair) on the test states, models fixed; level 1 - 0.05/6; Holm over the six pairs. R x I and O x I are primary.

| horizon | profile | pair | Delta [CI] | Holm p | reading | loss ratio reading |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | RI (primary) | -0.0103 [-0.0312, 0.0112] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | OI (primary) | 0.00539 [-0.0127, 0.0219] | 0.835 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | RO | 0.0138 [-0.0228, 0.0541] | 0.835 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | RN | 0.0114 [-0.0165, 0.0403] | 0.835 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | ON | 0.0215 [-0.00761, 0.0491] | 0.183 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | IN | -0.00137 [-0.0158, 0.0136] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RI (primary) | -0.0126 [-0.0364, 0.00895] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | OI (primary) | 0.011 [-0.00464, 0.0267] | 0.121 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RO | 0.0434 [0.00961, 0.0779] | 0.006 | interaction gain detected | small |
| H=8 (0.27 LT) | deployable | RN | 0.0152 [0.000183, 0.0318] | 0.02 | interaction gain detected | small |
| H=8 (0.27 LT) | deployable | ON | 0.0166 [-0.00101, 0.034] | 0.03 | interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | IN | -0.00124 [-0.0123, 0.0108] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | RI (primary) | -0.015 [-0.0452, 0.0186] | 0.896 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | OI (primary) | 0.00951 [-0.0147, 0.0336] | 0.292 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | RO | 0.0522 [0.0108, 0.0872] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | oracle | RN | 0.0268 [0.00171, 0.0538] | 0.014 | interaction gain detected | small |
| H=15 (0.50 LT) | oracle | ON | 0.0392 [0.0041, 0.0777] | 0.0075 | interaction gain detected | small |
| H=15 (0.50 LT) | oracle | IN | 0.0201 [0.000353, 0.041] | 0.014 | interaction gain detected | small |
| H=15 (0.50 LT) | deployable | RI (primary) | -0.0172 [-0.0601, 0.0311] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | OI (primary) | -0.00302 [-0.095, 0.0859] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | RO | 0.0479 [-0.044, 0.134] | 0.459 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | RN | -0.0124 [-0.104, 0.0682] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | ON | -0.00488 [-0.097, 0.0798] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | IN | -0.0145 [-0.104, 0.0638] | 1 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | RI (primary) | 0.0149 [-0.024, 0.053] | 0.261 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | OI (primary) | 0.0662 [0.0232, 0.113] | 0.003 | interaction gain detected | small |
| H=30 (1.00 LT) | oracle | RO | 0.0205 [-0.0176, 0.0559] | 0.261 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | RN | 0.0154 [-0.0137, 0.0444] | 0.261 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | ON | 0.0514 [0.0132, 0.0886] | 0.003 | interaction gain detected | small |
| H=30 (1.00 LT) | oracle | IN | 0.0353 [-0.00411, 0.0741] | 0.042 | interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | RI (primary) | 0.0184 [-0.00951, 0.0479] | 0.121 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | OI (primary) | 0.0884 [0.0385, 0.139] | 0.003 | interaction gain detected | small |
| H=30 (1.00 LT) | deployable | RO | 0.0427 [0.00915, 0.075] | 0.003 | interaction gain detected | small |
| H=30 (1.00 LT) | deployable | RN | 0.0065 [-0.0107, 0.0234] | 0.327 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | ON | 0.0171 [-0.00295, 0.0394] | 0.076 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | IN | 0.00318 [-0.0162, 0.0223] | 0.34 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | RI (primary) | 0.0588 [0.00511, 0.115] | 0.015 | interaction gain detected | small |
| H=60 (2.00 LT) | oracle | OI (primary) | 0.106 [0.0371, 0.171] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | oracle | RO | -0.0142 [-0.0704, 0.0423] | 0.937 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | RN | 0.00581 [-0.0293, 0.0445] | 0.937 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | ON | 0.00714 [-0.0312, 0.0477] | 0.937 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | IN | 0.0344 [-0.00209, 0.069] | 0.024 | interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | RI (primary) | 0.0515 [0.00502, 0.0954] | 0.006 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | OI (primary) | 0.154 [0.091, 0.224] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | RO | 0.0826 [0.0317, 0.132] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | RN | 0.00057 [-0.0224, 0.0261] | 0.448 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | ON | 0.0257 [-0.00587, 0.0571] | 0.0465 | interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | IN | 0.0132 [-0.0129, 0.0389] | 0.16 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RI (primary) | 0.0176 [-0.0251, 0.0638] | 0.918 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | OI (primary) | 0.0143 [-0.0553, 0.081] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RO | 0.00116 [-0.0601, 0.0641] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RN | -0.0314 [-0.067, 0.00845] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | ON | 0.0127 [-0.0571, 0.0753] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | IN | -0.0117 [-0.0405, 0.018] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RI (primary) | 0.00392 [-0.00697, 0.0147] | 0.164 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | OI (primary) | 0.0467 [-0.00648, 0.103] | 0.023 | interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RO | 0.045 [0.018, 0.0726] | 0.003 | interaction gain detected | small |
| H=120 (4.00 LT) | deployable | RN | 0.0246 [0.00899, 0.0407] | 0.003 | interaction gain detected | small |
| H=120 (4.00 LT) | deployable | ON | 0.0314 [0.0138, 0.0487] | 0.003 | interaction gain detected | small |
| H=120 (4.00 LT) | deployable | IN | 0.011 [0.00146, 0.0195] | 0.003 | interaction gain detected | small |

### D. Allocation ladder (rung against the full profile)

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED. MSE ratio MSE(rung)/MSE(F) at level 1 - 0.05/m (m rungs); Holm p for Delta MSE > 0. Theory gap L_A(oracle F) is an upper bound; estimation gap = L_A(deployable F) - L_A(oracle F) (95%).

| horizon | profile | rung | MSE | MSE ratio vs F [CI] | reading | Holm p |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | none | 0.000628 | 0.6 [0.226, 1.15] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | separation | 0.0006 | 0.573 [0.223, 1.08] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | RO | 0.00112 | 1.07 [0.875, 1.66] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | R | 0.000602 | 0.575 [0.218, 1.11] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | O | 0.00103 | 0.985 [0.753, 1.55] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | I | 0.000668 | 0.638 [0.235, 1.26] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | N | 0.000626 | 0.597 [0.237, 1.13] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | F (ROIN) | 0.00105 | 1 | | |
| H=8 (0.27 LT) | oracle | X | 0.000683 | 0.653 [0.256, 1.25] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | X+F | 0.000831 | 0.793 [0.583, 1.14] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | none | 0.000597 | 0.952 [0.899, 0.993] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | A2 (stored) | 0.000599 | 0.955 [0.902, 0.996] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | separation | 0.000676 | 1.08 [1, 1.15] | undetermined (n_eff < 50) | 0.03 |
| H=8 (0.27 LT) | deployable | A4 (stored) | 0.000676 | 1.08 [1, 1.15] | undetermined (n_eff < 50) | 0.03 |
| H=8 (0.27 LT) | deployable | RO | 0.000603 | 0.961 [0.906, 1] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | R | 0.000715 | 1.14 [0.979, 1.46] | undetermined (n_eff < 50) | 0.215 |
| H=8 (0.27 LT) | deployable | O | 0.000608 | 0.969 [0.911, 1.02] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | I | 0.000613 | 0.977 [0.934, 1.01] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | N | 0.00061 | 0.973 [0.921, 1.02] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | F (ROIN) | 0.000627 | 1 | | |
| H=8 (0.27 LT) | deployable | X | 0.000743 | 1.18 [0.97, 1.68] | undetermined (n_eff < 50) | 0.243 |
| H=8 (0.27 LT) | deployable | A3 (stored) | 0.000655 | 1.04 [0.97, 1.11] | undetermined (n_eff < 50) | 0.344 |
| H=8 (0.27 LT) | deployable | X+F | 0.000661 | 1.05 [0.956, 1.27] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | oracle | none | 0.00267 | 0.841 [0.595, 1.07] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | oracle | separation | 0.00251 | 0.79 [0.561, 1] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | oracle | RO | 0.00272 | 0.859 [0.667, 1.05] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | oracle | R | 0.00257 | 0.809 [0.586, 1.02] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | oracle | O | 0.0028 | 0.883 [0.658, 1.09] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | oracle | I | 0.00275 | 0.866 [0.621, 1.09] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | oracle | N | 0.00262 | 0.825 [0.586, 1.04] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | oracle | F (ROIN) | 0.00317 | 1 | | |
| H=15 (0.50 LT) | oracle | X | 0.00301 | 0.95 [0.682, 1.27] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | oracle | X+F | 0.00299 | 0.943 [0.707, 1.14] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | none | 0.0026 | 0.942 [0.844, 0.999] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | A2 (stored) | 0.00258 | 0.937 [0.837, 0.994] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | separation | 0.00279 | 1.01 [0.936, 1.08] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | A4 (stored) | 0.00279 | 1.01 [0.936, 1.08] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | RO | 0.00273 | 0.989 [0.95, 1.02] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | R | 0.00265 | 0.961 [0.891, 1] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | O | 0.00264 | 0.958 [0.86, 1.02] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | I | 0.0029 | 1.05 [0.923, 1.21] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | N | 0.00258 | 0.936 [0.84, 0.995] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | F (ROIN) | 0.00276 | 1 | | |
| H=15 (0.50 LT) | deployable | X | 0.00321 | 1.16 [0.954, 1.58] | undetermined (n_eff < 50) | 0.264 |
| H=15 (0.50 LT) | deployable | A3 (stored) | 0.00283 | 1.03 [0.915, 1.16] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | X+F | 0.00274 | 0.992 [0.904, 1.06] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | none | 0.016 | 0.972 [0.836, 1.12] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | separation | 0.0147 | 0.893 [0.776, 1.01] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | RO | 0.0157 | 0.957 [0.86, 1.06] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | R | 0.0162 | 0.987 [0.854, 1.09] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | O | 0.016 | 0.972 [0.847, 1.1] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | I | 0.016 | 0.971 [0.835, 1.12] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | N | 0.0159 | 0.97 [0.849, 1.09] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | F (ROIN) | 0.0164 | 1 | | |
| H=30 (1.00 LT) | oracle | X | 0.017 | 1.04 [0.883, 1.21] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | X+F | 0.0161 | 0.98 [0.912, 1.04] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | deployable | none | 0.0183 | 0.998 [0.957, 1.04] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | deployable | A2 (stored) | 0.0183 | 0.998 [0.957, 1.04] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | deployable | separation | 0.0179 | 0.979 [0.936, 1.02] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | deployable | A4 (stored) | 0.0179 | 0.979 [0.936, 1.02] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | deployable | RO | 0.0183 | 0.999 [0.977, 1.02] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | deployable | R | 0.0181 | 0.986 [0.959, 1.01] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | deployable | O | 0.0184 | 1 [0.958, 1.05] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | deployable | I | 0.0183 | 0.996 [0.955, 1.03] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | deployable | N | 0.0183 | 0.999 [0.958, 1.03] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | deployable | A5 (stored) | 0.0181 | 0.99 [0.945, 1.03] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | deployable | F (ROIN) | 0.0183 | 1 | | |
| H=30 (1.00 LT) | deployable | X | 0.0187 | 1.02 [0.971, 1.07] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | deployable | A3 (stored) | 0.0184 | 1 [0.943, 1.07] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | deployable | X+F | 0.018 | 0.98 [0.948, 1.01] | undetermined (n_eff < 50) | 1 |
| H=60 (2.00 LT) | oracle | none | 0.195 | 1.07 [1.04, 1.1] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | separation | 0.186 | 1.02 [0.99, 1.04] | negligible | 0.105 |
| H=60 (2.00 LT) | oracle | RO | 0.183 | 0.999 [0.987, 1.01] | negligible | 1 |
| H=60 (2.00 LT) | oracle | R | 0.188 | 1.03 [1, 1.05] | needed, size not determined | 0.005 |
| H=60 (2.00 LT) | oracle | O | 0.19 | 1.04 [1.02, 1.07] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | I | 0.193 | 1.06 [1.03, 1.09] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | N | 0.193 | 1.05 [1.03, 1.08] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | F (ROIN) | 0.183 | 1 | | |
| H=60 (2.00 LT) | oracle | X | 0.188 | 1.03 [1.01, 1.06] | needed, size not determined | 0.005 |
| H=60 (2.00 LT) | oracle | X+F | 0.182 | 0.997 [0.983, 1.01] | negligible | 1 |
| H=60 (2.00 LT) | deployable | none | 0.196 | 1.05 [1.02, 1.08] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | A2 (stored) | 0.197 | 1.05 [1.02, 1.08] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | separation | 0.197 | 1.06 [1.03, 1.08] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | A4 (stored) | 0.197 | 1.06 [1.03, 1.08] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | RO | 0.189 | 1.01 [0.995, 1.02] | negligible | 0.084 |
| H=60 (2.00 LT) | deployable | R | 0.195 | 1.04 [1.02, 1.07] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | O | 0.19 | 1.02 [0.997, 1.04] | negligible | 0.0275 |
| H=60 (2.00 LT) | deployable | I | 0.194 | 1.04 [1.01, 1.07] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | N | 0.193 | 1.03 [1.01, 1.06] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | F (ROIN) | 0.187 | 1 | | |
| H=60 (2.00 LT) | deployable | X | 0.187 | 1 [0.98, 1.03] | negligible | 0.646 |
| H=60 (2.00 LT) | deployable | A3 (stored) | 0.191 | 1.02 [0.987, 1.06] | undetermined | 0.118 |
| H=60 (2.00 LT) | deployable | X+F | 0.185 | 0.993 [0.975, 1.01] | negligible | 0.86 |
| H=120 (4.00 LT) | oracle | none | 0.643 | 1.02 [1.01, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | separation | 0.66 | 1.05 [1.04, 1.06] | needed, size not determined | 0.0045 |
| H=120 (4.00 LT) | oracle | RO | 0.63 | 1 [1, 1] | negligible | 0.012 |
| H=120 (4.00 LT) | oracle | R | 0.633 | 1.01 [1, 1.01] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | O | 0.64 | 1.02 [1.01, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | I | 0.638 | 1.01 [1, 1.02] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | N | 0.639 | 1.02 [1.01, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | F (ROIN) | 0.629 | 1 | | |
| H=120 (4.00 LT) | oracle | X | 0.64 | 1.02 [1.01, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | X+F | 0.63 | 1 [0.995, 1.01] | negligible | 0.289 |
| H=120 (4.00 LT) | deployable | none | 0.643 | 1.02 [1.01, 1.03] | small | 0.006 |
| H=120 (4.00 LT) | deployable | A2 (stored) | 0.643 | 1.02 [1.01, 1.03] | small | 0.006 |
| H=120 (4.00 LT) | deployable | separation | 0.672 | 1.07 [1.04, 1.08] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | A4 (stored) | 0.672 | 1.07 [1.04, 1.08] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | RO | 0.634 | 1.01 [0.999, 1.01] | negligible | 0.019 |
| H=120 (4.00 LT) | deployable | R | 0.638 | 1.01 [1, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | O | 0.64 | 1.01 [1, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | I | 0.638 | 1.01 [1, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | N | 0.639 | 1.01 [1, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | F (ROIN) | 0.631 | 1 | | |
| H=120 (4.00 LT) | deployable | X | 0.641 | 1.02 [1, 1.03] | small | 0.006 |
| H=120 (4.00 LT) | deployable | A3 (stored) | 0.652 | 1.03 [1.01, 1.05] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | X+F | 0.631 | 1 [0.994, 1.01] | negligible | 0.417 |

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| horizon | theory gap (upper bound) [CI] | estimation gap [CI] | gap with R estimated | gap with O estimated | gap with I estimated | gap with N estimated |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 0.00054 [6.17e-05, 0.00146] | -0.00042 [-0.00137, 7.81e-05] | 0.000117 [-2.28e-05, 0.000349] | -0.000445 [-0.00139, 5.25e-05] | 9.08e-05 [-2.73e-05, 0.000268] | -0.000318 [-0.00104, 6.35e-05] |
| H=15 (0.50 LT) | 0.00107 [0.000489, 0.0019] | -0.000413 [-0.00113, 0.000198] | -0.000365 [-0.00104, 0.000166] | -0.000562 [-0.00142, 0.000156] | -0.000428 [-0.00121, 0.000166] | -4.4e-05 [-0.000557, 0.000435] |
| H=30 (1.00 LT) | 0.00545 [0.00376, 0.00752] | 0.00189 [-0.0012, 0.00511] | 0.00136 [-0.00145, 0.00432] | 0.00201 [-0.000679, 0.00483] | 0.00176 [-0.000624, 0.00433] | 0.00223 [-0.000513, 0.00515] |
| H=60 (2.00 LT) | 0.0554 [0.0505, 0.0604] | 0.00404 [-0.00589, 0.0139] | 0.00675 [-0.00294, 0.0168] | -0.00144 [-0.0107, 0.00784] | 0.000223 [-0.00912, 0.0099] | -0.000325 [-0.00949, 0.00873] |
| H=120 (4.00 LT) | 0.172 [0.164, 0.181] | 0.00174 [-0.013, 0.0172] | 0.00371 [-0.011, 0.019] | 0.00111 [-0.0133, 0.0165] | 0.00158 [-0.013, 0.0171] | 0.0018 [-0.013, 0.0172] |

### Horizon decision (Y = ln min(T_c, H_max))

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED. Pinball loss at tau = 0.5; drop-one ratio at level 1 - 0.05/4; ladder ratio vs F at 1 - 0.05/m; C = Harrell's C (95%); coverage of q_0.1, q_0.5, q_0.9 and the 80% interval below the cap.

| profile | X | pinball ratio [CI] | reading | Holm p | phi [CI] |
|---|---|---|---|---|---|
| oracle | R | 1.02 [1.01, 1.03] | small | 0.002 | 0.00239 [0.00177, 0.00299] |
| oracle | O | 1.06 [1.04, 1.08] | needed, size not determined | 0.002 | 0.0162 [0.0142, 0.0181] |
| oracle | I | 1.25 [1.21, 1.29] | substantial | 0.002 | 0.0454 [0.0409, 0.05] |
| oracle | N | 1 [0.993, 1.01] | negligible | 0.431 | 0.00253 [0.00159, 0.00346] |
| deployable | R | 1 [0.997, 1.01] | negligible | 0.13 | 0.00128 [0.000832, 0.00174] |
| deployable | O | 1.08 [1.06, 1.09] | substantial | 0.002 | 0.0204 [0.0184, 0.0225] |
| deployable | I | 1.23 [1.19, 1.26] | substantial | 0.002 | 0.043 [0.039, 0.047] |
| deployable | N | 0.997 [0.992, 1] | negligible | 0.922 | 0.00269 [0.00209, 0.00328] |

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | ratio vs F [CI] | reading | C [CI] | cov 0.1 / 0.5 / 0.9 / 80% |
|---|---|---|---|---|---|---|
| oracle | none | 0.225 | 1.42 [1.37, 1.48] | substantial | 0.5 [0.5, 0.5] | 0.0988 / 0.497 / 0.887 / 0.789 |
| oracle | lyapunov | 0.257 | 1.62 [1.55, 1.68] | substantial | 0.672 [0.663, 0.682] | 0.0957 / 0.453 / 0.849 / 0.815 |
| oracle | RO | 0.199 | 1.25 [1.21, 1.3] | substantial | 0.64 [0.631, 0.649] | 0.11 / 0.488 / 0.892 / 0.783 |
| oracle | R | 0.224 | 1.41 [1.36, 1.46] | substantial | 0.536 [0.526, 0.547] | 0.107 / 0.5 / 0.886 / 0.779 |
| oracle | O | 0.203 | 1.28 [1.23, 1.32] | substantial | 0.632 [0.623, 0.641] | 0.106 / 0.491 / 0.891 / 0.785 |
| oracle | I | 0.173 | 1.09 [1.07, 1.11] | substantial | 0.689 [0.68, 0.698] | 0.109 / 0.497 / 0.887 / 0.778 |
| oracle | N | 0.22 | 1.38 [1.34, 1.44] | substantial | 0.569 [0.559, 0.579] | 0.103 / 0.491 / 0.892 / 0.789 |
| oracle | ROIN | 0.159 | 1 |  | 0.722 [0.713, 0.73] | 0.113 / 0.496 / 0.885 / 0.772 |
| oracle | X | 0.174 | 1.09 [1.05, 1.14] | needed, size not determined | 0.7 [0.691, 0.708] | 0.137 / 0.483 / 0.862 / 0.725 |
| oracle | X+F | 0.135 | 0.847 [0.825, 0.867] | lowers | 0.774 [0.767, 0.781] | 0.153 / 0.493 / 0.849 / 0.696 |
| oracle | Lyapunov rank (C only) | | | | 0.671 [0.661, 0.68] | |
| deployable | none | 0.225 | 1.43 [1.38, 1.48] | substantial | 0.5 [0.5, 0.5] | 0.0988 / 0.497 / 0.887 / 0.789 |
| deployable | lyapunov | 0.259 | 1.64 [1.58, 1.7] | substantial | 0.67 [0.661, 0.679] | 0.0967 / 0.46 / 0.847 / 0.813 |
| deployable | RO | 0.195 | 1.23 [1.19, 1.27] | substantial | 0.647 [0.638, 0.657] | 0.0949 / 0.494 / 0.895 / 0.8 |
| deployable | R | 0.225 | 1.42 [1.37, 1.48] | substantial | 0.522 [0.515, 0.531] | 0.101 / 0.497 / 0.889 / 0.788 |
| deployable | O | 0.197 | 1.25 [1.21, 1.29] | substantial | 0.64 [0.631, 0.65] | 0.101 / 0.499 / 0.893 / 0.792 |
| deployable | I | 0.175 | 1.11 [1.09, 1.13] | substantial | 0.682 [0.674, 0.69] | 0.11 / 0.499 / 0.892 / 0.782 |
| deployable | N | 0.219 | 1.39 [1.34, 1.44] | substantial | 0.57 [0.563, 0.578] | 0.103 / 0.497 / 0.894 / 0.791 |
| deployable | ROIN | 0.158 | 1 |  | 0.726 [0.718, 0.734] | 0.134 / 0.502 / 0.89 / 0.755 |
| deployable | X | 0.175 | 1.11 [1.07, 1.15] | substantial | 0.7 [0.692, 0.708] | 0.131 / 0.49 / 0.866 / 0.735 |
| deployable | X+F | 0.135 | 0.856 [0.836, 0.876] | lowers | 0.772 [0.765, 0.779] | 0.144 / 0.49 / 0.865 / 0.721 |
| deployable | Lyapunov rank (C only) | | | | 0.667 [0.658, 0.677] | |

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| profile | pair | Delta [CI] | Holm p | detected |
|---|---|---|---|---|
| oracle | RO | 0.000322 [-0.00144, 0.00209] | 0.32 | False |
| oracle | RI (primary) | 0.00237 [0.00116, 0.00367] | 0.003 | True |
| oracle | RN | 0.000257 [-5.32e-05, 0.000576] | 0.034 | True |
| oracle | OI (primary) | 0.00794 [0.00536, 0.0107] | 0.003 | True |
| oracle | ON | 0.0012 [0.000257, 0.00218] | 0.003 | True |
| oracle | IN | 0.0013 [0.000215, 0.00242] | 0.003 | True |
| deployable | RO | 0.000564 [-0.000332, 0.00139] | 0.141 | False |
| deployable | RI (primary) | 0.00149 [0.000561, 0.00247] | 0.003 | True |
| deployable | RN | 5.85e-05 [-0.000497, 0.000618] | 0.771 | False |
| deployable | OI (primary) | 0.00856 [0.00624, 0.0108] | 0.003 | True |
| deployable | ON | -0.000125 [-0.00094, 0.000671] | 0.771 | False |
| deployable | IN | 0.000794 [-0.000292, 0.00197] | 0.1 | False |

