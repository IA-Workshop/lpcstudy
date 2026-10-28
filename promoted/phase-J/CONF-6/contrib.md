# Phase J contribution study: CONF-6

**PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.** Run `phasej-CONF-6/phasej`; analysis commit `c19ad486b93a2ee96d64ce069ec42fd440428211` (dirty: False). Every reading is an estimate; Shapley shares and interactions are predictive, not causal. Training variance is not in the intervals.

## lorenz63

**PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.**

| check | result |
|---|---|
| (f1) state_mse from per-draw errors, max rel diff | A0 0.0e+00, A1 0.0e+00, A2 0.0e+00, A3 0.0e+00, A4 0.0e+00, A5 0.0e+00 (within 1e-12: True) |
| (g) WU-0039b (b1), (b2) rows reproduced | drop-N: True, all rows: True |
| separation formula on F-hat vs stored A4 at H_ref, max abs | 2.22e-16 |
| T_c: T = 1 / e_(T-1) = theta (train, test) | 2/0, 18/0 |
| (f2) dependence bias, deployable rows (reported, not gating) | 131 rows; 26 flagged: H=8 RO: dependence bias detectable (interval excludes 0), t1+t2 / V -0.113, z 0.918; H=8 RON: dependence bias detectable (interval excludes 0), t1+t2 / V -0.113, z 1.25; H=8 swap-R: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0132, z 1.8; H=8 swap-N: dependence bias detectable (interval excludes 0), t1+t2 / V 0.00557, z 1.81; H=8 separation: dependence bias detectable (interval excludes 0), t1+t2 / V 0.00368, z 1.75; H=8 A4 (stored): dependence bias detectable (interval excludes 0), t1+t2 / V 0.00368, z 1.75; H=15 O: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0873, z 0.321; H=15 I: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0781, z 0.44; H=15 RO: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0608, z -0.383; H=15 OI: dependence bias detectable (interval excludes 0), t1+t2 / V 0.103, z 0.111; H=15 ON: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0724, z 0.36; H=15 A3 (stored): dependence bias detectable (interval excludes 0), t1+t2 / V -0.0023, z -0.0909 ... |

### A. Allocation: drop-one and Shapley

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED. MSE ratio MSE(F without X)/MSE(F) at level 1 - 0.05/4 (reading by the 1.05 table, with the n_eff guard); excess ratio L_A(F without X)/L_A(F) and Holm p (Delta MSE > 0) are estimates. phi = Shapley share of L_A (95%). Oracle rows: moment form; deployable rows: realized per draw.

| horizon | profile | X | MSE ratio [CI] | reading | excess ratio | Holm p | phi_X [95% CI] | share |
|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | R | 0.921 [0.805, 1.09] | undetermined (n_eff < 50) | 0.694 | 1 | -2.98e-05 [-0.000431, 0.000367] | -0.00327 |
| H=8 (0.27 LT) | oracle | O | 2.9 [1.95, 5.58] | undetermined (n_eff < 50) | 8.36 | 0.002 | 0.00651 [0.00517, 0.00806] | 0.715 |
| H=8 (0.27 LT) | oracle | I | 0.924 [0.826, 1.07] | undetermined (n_eff < 50) | 0.706 | 1 | 0.00239 [0.00165, 0.00314] | 0.263 |
| H=8 (0.27 LT) | oracle | N | 1.04 [1, 1.08] | undetermined (n_eff < 50) | 1.14 | 0.018 | 0.000229 [-0.000171, 0.00061] | 0.0251 |
| H=8 (0.27 LT) | deployable | R | 1.05 [0.933, 1.21] | undetermined | 1.08 | 0.484 | 0.001 [0.000354, 0.00172] | 0.189 |
| H=8 (0.27 LT) | deployable | O | 1.29 [0.94, 1.9] | undetermined | 1.42 | 0.154 | 0.00242 [0.000973, 0.00452] | 0.455 |
| H=8 (0.27 LT) | deployable | I | 0.925 [0.715, 1.2] | undetermined | 0.89 | 0.769 | 0.00139 [0.000331, 0.00248] | 0.261 |
| H=8 (0.27 LT) | deployable | N | 1.01 [0.98, 1.04] | negligible | 1.01 | 0.484 | 0.000505 [-0.000324, 0.00124] | 0.0949 |
| H=15 (0.50 LT) | oracle | R | 1.06 [0.945, 1.16] | undetermined (n_eff < 50) | 1.29 | 0.286 | 0.00236 [0.00106, 0.00374] | 0.117 |
| H=15 (0.50 LT) | oracle | O | 1.58 [1.33, 1.98] | undetermined (n_eff < 50) | 3.85 | 0.002 | 0.0123 [0.00948, 0.0155] | 0.609 |
| H=15 (0.50 LT) | oracle | I | 0.984 [0.852, 1.09] | undetermined (n_eff < 50) | 0.922 | 0.832 | 0.00321 [0.00152, 0.00492] | 0.159 |
| H=15 (0.50 LT) | oracle | N | 1.01 [0.909, 1.09] | undetermined (n_eff < 50) | 1.03 | 0.832 | 0.00233 [0.000526, 0.00392] | 0.115 |
| H=15 (0.50 LT) | deployable | R | 1.08 [0.912, 1.28] | undetermined (n_eff < 50) | 1.12 | 0.429 | 0.00599 [0.0032, 0.00895] | 0.619 |
| H=15 (0.50 LT) | deployable | O | 1.09 [0.96, 1.25] | undetermined (n_eff < 50) | 1.14 | 0.242 | 0.00179 [-0.00016, 0.00368] | 0.185 |
| H=15 (0.50 LT) | deployable | I | 0.946 [0.776, 1.1] | undetermined (n_eff < 50) | 0.912 | 1 | 0.00187 [-0.00224, 0.00529] | 0.193 |
| H=15 (0.50 LT) | deployable | N | 0.948 [0.755, 1.12] | undetermined (n_eff < 50) | 0.916 | 1 | 3.27e-05 [-0.00266, 0.0024] | 0.00337 |
| H=30 (1.00 LT) | oracle | R | 1.03 [0.99, 1.09] | undetermined (n_eff < 50) | 1.11 | 0.0975 | 0.00108 [-0.000663, 0.00294] | 0.0471 |
| H=30 (1.00 LT) | oracle | O | 1.16 [1.07, 1.27] | undetermined (n_eff < 50) | 1.54 | 0.002 | 0.0135 [0.00998, 0.017] | 0.589 |
| H=30 (1.00 LT) | oracle | I | 1.02 [0.993, 1.04] | undetermined (n_eff < 50) | 1.06 | 0.0975 | 0.00723 [0.00509, 0.00933] | 0.315 |
| H=30 (1.00 LT) | oracle | N | 0.976 [0.9, 1.06] | undetermined (n_eff < 50) | 0.92 | 0.774 | 0.00112 [-0.00078, 0.00285] | 0.0488 |
| H=30 (1.00 LT) | deployable | R | 1.03 [0.992, 1.07] | undetermined | 1.06 | 0.104 | 0.00454 [0.00183, 0.00736] | 0.32 |
| H=30 (1.00 LT) | deployable | O | 1.04 [0.987, 1.09] | undetermined | 1.08 | 0.117 | 0.00202 [0.000396, 0.00377] | 0.143 |
| H=30 (1.00 LT) | deployable | I | 1.08 [0.964, 1.24] | undetermined | 1.17 | 0.117 | 0.00705 [0.00372, 0.0107] | 0.497 |
| H=30 (1.00 LT) | deployable | N | 1.02 [0.992, 1.06] | undetermined | 1.05 | 0.117 | 0.000557 [-0.0015, 0.00254] | 0.0393 |
| H=60 (2.00 LT) | oracle | R | 0.994 [0.969, 1.02] | negligible | 0.982 | 1 | 0.00082 [-0.000843, 0.00231] | 0.0499 |
| H=60 (2.00 LT) | oracle | O | 1.08 [1.03, 1.13] | needed, size not determined | 1.23 | 0.002 | 0.0119 [0.00722, 0.0169] | 0.724 |
| H=60 (2.00 LT) | oracle | I | 1.03 [0.994, 1.06] | undetermined | 1.08 | 0.0795 | 0.00367 [0.00204, 0.00542] | 0.223 |
| H=60 (2.00 LT) | oracle | N | 0.984 [0.963, 1] | negligible | 0.954 | 1 | 5.04e-05 [-0.00196, 0.00187] | 0.00306 |
| H=60 (2.00 LT) | deployable | R | 1.02 [0.99, 1.05] | negligible | 1.04 | 0.25 | 0.00319 [0.000844, 0.00583] | 0.399 |
| H=60 (2.00 LT) | deployable | O | 1.01 [0.989, 1.02] | negligible | 1.01 | 0.365 | 0.001 [-0.000444, 0.00257] | 0.125 |
| H=60 (2.00 LT) | deployable | I | 1.03 [0.998, 1.06] | undetermined | 1.06 | 0.04 | 0.00367 [0.00124, 0.00626] | 0.459 |
| H=60 (2.00 LT) | deployable | N | 1 [0.984, 1.02] | negligible | 1 | 0.43 | 0.000135 [-0.00122, 0.00158] | 0.0169 |
| H=120 (4.00 LT) | oracle | R | 1.01 [1, 1.01] | small | 1.02 | 0.002 | 0.00776 [0.00441, 0.0108] | 0.809 |
| H=120 (4.00 LT) | oracle | O | 0.998 [0.994, 1] | negligible | 0.992 | 0.95 | -0.00021 [-0.00323, 0.003] | -0.0219 |
| H=120 (4.00 LT) | oracle | I | 1 [0.999, 1] | negligible | 1 | 0.235 | 0.00137 [-0.000242, 0.00302] | 0.143 |
| H=120 (4.00 LT) | oracle | N | 1 [0.999, 1] | negligible | 1 | 0.548 | 0.000667 [-0.000153, 0.00148] | 0.0695 |
| H=120 (4.00 LT) | deployable | R | 1 [1, 1.01] | small | 1.01 | 0.022 | 0.00621 [0.00272, 0.0101] | 0.716 |
| H=120 (4.00 LT) | deployable | O | 0.999 [0.997, 1] | negligible | 0.997 | 1 | 0.000714 [-0.00231, 0.00393] | 0.0822 |
| H=120 (4.00 LT) | deployable | I | 1 [0.999, 1] | negligible | 1.01 | 0.0645 | 0.00189 [-1.24e-05, 0.00394] | 0.218 |
| H=120 (4.00 LT) | deployable | N | 1 [0.999, 1] | negligible | 0.999 | 1 | -0.000142 [-0.00103, 0.000759] | -0.0164 |

### A. Allocation: summary per horizon

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED. n_eff = Kish size of kappa on the test states; G = 1 - L_A(rule)/L_A(constant), estimate (95%).

| horizon | profile | n_eff(kappa) | G(F) [CI] | G(separation) | MSE(F)/MSE(sep) [CI] | reading | settings (A) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 97.5 | 0.946 [0.903, 0.978] | 0.943 | 0.99 [0.795, 1.18] | undetermined (n_eff < 50) | F: qn; qn 4, mid 4, low 7 |
| H=8 (0.27 LT) | deployable | 97.5 | 0.617 [0.525, 0.697] | -1.28 | 0.227 [0.166, 0.317] | lowers | F: low; qn 0, mid 11, low 4 |
| H=15 (0.50 LT) | oracle | 84.8 | 0.899 [0.835, 0.948] | 0.867 | 0.938 [0.841, 1.05] | undetermined (n_eff < 50) | F: mid; qn 4, mid 4, low 7 |
| H=15 (0.50 LT) | deployable | 84.8 | 0.399 [0.13, 0.619] | -0.352 | 0.563 [0.401, 0.775] | lowers | F: qn; qn 8, mid 4, low 3 |
| H=30 (1.00 LT) | oracle | 195 | 0.671 [0.569, 0.757] | 0.635 | 0.968 [0.894, 1.04] | undetermined (n_eff < 50) | F: mid; qn 1, mid 9, low 5 |
| H=30 (1.00 LT) | deployable | 195 | 0.373 [0.234, 0.517] | -0.217 | 0.691 [0.587, 0.793] | lowers | F: mid; qn 1, mid 8, low 6 |
| H=60 (2.00 LT) | oracle | 505 | 0.271 [0.186, 0.351] | 0.236 | 0.984 [0.956, 1.01] | negligible | F: mid; qn 0, mid 7, low 8 |
| H=60 (2.00 LT) | deployable | 505 | 0.116 [0.0502, 0.183] | -0.056 | 0.925 [0.889, 0.959] | lowers | F: mid; qn 0, mid 6, low 9 |
| H=120 (4.00 LT) | oracle | 1.75e+03 | 0.0366 [0.017, 0.0555] | -0.235 | 0.923 [0.909, 0.94] | lowers | F: low; qn 0, mid 0, low 15 |
| H=120 (4.00 LT) | deployable | 1.75e+03 | 0.0343 [0.0126, 0.0583] | -0.183 | 0.939 [0.927, 0.952] | lowers | F: low; qn 0, mid 0, low 15 |

### B. Allocation: pairwise interactions (logit u, interior states)

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED. Delta = L(additive) - L(additive + pair) on the test states, models fixed; level 1 - 0.05/6; Holm over the six pairs. R x I and O x I are primary.

| horizon | profile | pair | Delta [CI] | Holm p | reading | loss ratio reading |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | RI (primary) | 0.00615 [-0.0661, 0.0747] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | OI (primary) | -0.0192 [-0.0892, 0.0592] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | RO | 0.165 [0.0747, 0.261] | 0.003 | interaction gain detected | needed, size not determined |
| H=8 (0.27 LT) | oracle | RN | -0.0898 [-0.181, -0.00655] | 1 | no interaction gain; the pair model fits worse | no interaction gain; the pair model fits worse |
| H=8 (0.27 LT) | oracle | ON | -0.0271 [-0.098, 0.0423] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | IN | 0.0117 [-0.0197, 0.0449] | 0.877 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RI (primary) | 0.0124 [-0.0238, 0.0508] | 0.786 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | OI (primary) | -0.0163 [-0.0619, 0.0298] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RO | 0.0896 [0.0443, 0.138] | 0.003 | interaction gain detected | small |
| H=8 (0.27 LT) | deployable | RN | 0.00456 [-0.0309, 0.038] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | ON | -0.0138 [-0.0573, 0.03] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | IN | 0.0169 [-0.0279, 0.0604] | 0.742 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | RI (primary) | 0.0217 [-0.0451, 0.0893] | 0.617 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | OI (primary) | 0.0102 [-0.0596, 0.0744] | 0.714 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | RO | 0.0336 [-0.0472, 0.122] | 0.617 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | RN | 0.0307 [-0.0398, 0.1] | 0.617 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | ON | -0.0145 [-0.0781, 0.0495] | 0.715 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | IN | 0.0212 [-0.0217, 0.062] | 0.585 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | RI (primary) | 0.0315 [-0.00369, 0.0678] | 0.03 | interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | OI (primary) | 0.0507 [0.0228, 0.0774] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | deployable | RO | 0.166 [0.0979, 0.233] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | deployable | RN | -0.0389 [-0.0907, 0.0151] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | ON | -0.0468 [-0.102, 0.0129] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | IN | 0.0623 [0.0189, 0.103] | 0.003 | interaction gain detected | small |
| H=30 (1.00 LT) | oracle | RI (primary) | 0.0017 [-0.0684, 0.074] | 1 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | OI (primary) | 0.0397 [-0.0307, 0.109] | 0.315 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | RO | 0.0774 [-0.0126, 0.166] | 0.084 | no interaction gain detected | undetermined |
| H=30 (1.00 LT) | oracle | RN | -0.0258 [-0.101, 0.0515] | 1 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | ON | -0.0244 [-0.0988, 0.0451] | 1 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | IN | 0.0315 [-0.0224, 0.0846] | 0.315 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | RI (primary) | 0.0021 [-0.0342, 0.0372] | 0.928 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | OI (primary) | 0.01 [-0.0163, 0.0386] | 0.722 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | RO | 0.0784 [0.0277, 0.128] | 0.003 | interaction gain detected | small |
| H=30 (1.00 LT) | deployable | RN | 0.0103 [-0.0261, 0.0444] | 0.722 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | ON | -0.011 [-0.0507, 0.0304] | 0.928 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | IN | 0.0118 [-0.0223, 0.0433] | 0.722 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | RI (primary) | 0.0712 [0.0151, 0.135] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | oracle | OI (primary) | 0.136 [0.0718, 0.205] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | oracle | RO | 0.179 [0.0973, 0.264] | 0.003 | interaction gain detected | needed, size not determined |
| H=60 (2.00 LT) | oracle | RN | 0.0125 [-0.0229, 0.0506] | 0.354 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | ON | 0.00378 [-0.0375, 0.0479] | 0.406 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | IN | 0.0289 [-0.0136, 0.0671] | 0.0855 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | RI (primary) | 0.0433 [-0.00156, 0.0905] | 0.028 | interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | OI (primary) | 0.051 [0.00228, 0.0967] | 0.0175 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | RO | 0.0716 [0.0217, 0.124] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | RN | 0.018 [-0.0147, 0.0498] | 0.0705 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | ON | 0.0326 [-0.00165, 0.0687] | 0.028 | interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | IN | 0.0222 [-0.00694, 0.0516] | 0.057 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RI (primary) | 0.0319 [0.000176, 0.0653] | 0.0225 | interaction gain detected | small |
| H=120 (4.00 LT) | oracle | OI (primary) | 0.0586 [0.0168, 0.101] | 0.003 | interaction gain detected | small |
| H=120 (4.00 LT) | oracle | RO | -0.00334 [-0.0435, 0.0394] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RN | 0.00442 [-0.0292, 0.0351] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | ON | -0.00849 [-0.0434, 0.0275] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | IN | 0.00319 [-0.0241, 0.0333] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RI (primary) | 0.021 [-0.0051, 0.0491] | 0.078 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | OI (primary) | 0.0299 [-0.0019, 0.0661] | 0.045 | interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RO | 0.00745 [-0.019, 0.0348] | 0.721 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RN | -0.000305 [-0.0212, 0.0204] | 0.996 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | ON | -0.000961 [-0.0283, 0.0302] | 0.996 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | IN | 0.0205 [-0.0026, 0.0446] | 0.045 | interaction gain detected | negligible |

### D. Allocation ladder (rung against the full profile)

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED. MSE ratio MSE(rung)/MSE(F) at level 1 - 0.05/m (m rungs); Holm p for Delta MSE > 0. Theory gap L_A(oracle F) is an upper bound; estimation gap = L_A(deployable F) - L_A(oracle F) (95%).

| horizon | profile | rung | MSE | MSE ratio vs F [CI] | reading | Holm p |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | none | 0.0111 | 5.5 [3.03, 13.5] | undetermined (n_eff < 50) | 0.0045 |
| H=8 (0.27 LT) | oracle | separation | 0.00204 | 1.01 [0.798, 1.37] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | RO | 0.0019 | 0.94 [0.793, 1.16] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | R | 0.0115 | 5.66 [3.15, 13.6] | undetermined (n_eff < 50) | 0.0045 |
| H=8 (0.27 LT) | oracle | O | 0.00201 | 0.995 [0.775, 1.33] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | I | 0.00628 | 3.11 [1.98, 6.48] | undetermined (n_eff < 50) | 0.0045 |
| H=8 (0.27 LT) | oracle | N | 0.011 | 5.42 [2.92, 13.7] | undetermined (n_eff < 50) | 0.0045 |
| H=8 (0.27 LT) | oracle | F (ROIN) | 0.00202 | 1 | | |
| H=8 (0.27 LT) | oracle | X | 0.00205 | 1.01 [0.735, 1.7] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | X+F | 0.00172 | 0.851 [0.649, 1.08] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | none | 0.0101 | 2.11 [1.68, 2.85] | substantial | 0.006 |
| H=8 (0.27 LT) | deployable | A2 (stored) | 0.00987 | 2.05 [1.65, 2.72] | substantial | 0.006 |
| H=8 (0.27 LT) | deployable | separation | 0.0212 | 4.4 [2.63, 7.02] | substantial | 0.006 |
| H=8 (0.27 LT) | deployable | A4 (stored) | 0.0212 | 4.4 [2.63, 7.02] | substantial | 0.006 |
| H=8 (0.27 LT) | deployable | RO | 0.00478 | 0.995 [0.774, 1.3] | undetermined | 1 |
| H=8 (0.27 LT) | deployable | R | 0.00911 | 1.89 [1.31, 2.84] | substantial | 0.006 |
| H=8 (0.27 LT) | deployable | O | 0.00718 | 1.49 [1.14, 2.01] | substantial | 0.006 |
| H=8 (0.27 LT) | deployable | I | 0.00749 | 1.56 [1.19, 2.15] | substantial | 0.006 |
| H=8 (0.27 LT) | deployable | N | 0.00927 | 1.93 [1.36, 2.75] | substantial | 0.006 |
| H=8 (0.27 LT) | deployable | F (ROIN) | 0.00481 | 1 | | |
| H=8 (0.27 LT) | deployable | X | 0.00214 | 0.444 [0.228, 0.724] | lowers | 1 |
| H=8 (0.27 LT) | deployable | A3 (stored) | 0.00876 | 1.82 [1.1, 2.72] | substantial | 0.008 |
| H=8 (0.27 LT) | deployable | X+F | 0.00255 | 0.53 [0.232, 0.901] | lowers | 1 |
| H=15 (0.50 LT) | oracle | none | 0.0314 | 2.82 [2.1, 4.09] | undetermined (n_eff < 50) | 0.0045 |
| H=15 (0.50 LT) | oracle | separation | 0.0119 | 1.07 [0.901, 1.25] | undetermined (n_eff < 50) | 0.376 |
| H=15 (0.50 LT) | oracle | RO | 0.0114 | 1.03 [0.854, 1.19] | undetermined (n_eff < 50) | 0.656 |
| H=15 (0.50 LT) | oracle | R | 0.0267 | 2.4 [1.83, 3.49] | undetermined (n_eff < 50) | 0.0045 |
| H=15 (0.50 LT) | oracle | O | 0.0127 | 1.14 [0.951, 1.35] | undetermined (n_eff < 50) | 0.094 |
| H=15 (0.50 LT) | oracle | I | 0.0244 | 2.19 [1.52, 3.33] | undetermined (n_eff < 50) | 0.0045 |
| H=15 (0.50 LT) | oracle | N | 0.0256 | 2.3 [1.72, 3.42] | undetermined (n_eff < 50) | 0.0045 |
| H=15 (0.50 LT) | oracle | F (ROIN) | 0.0111 | 1 | | |
| H=15 (0.50 LT) | oracle | X | 0.0143 | 1.28 [1.11, 1.54] | undetermined (n_eff < 50) | 0.0045 |
| H=15 (0.50 LT) | oracle | X+F | 0.0112 | 1 [0.893, 1.1] | undetermined (n_eff < 50) | 0.656 |
| H=15 (0.50 LT) | deployable | none | 0.0331 | 1.41 [0.986, 2.13] | undetermined (n_eff < 50) | 0.0405 |
| H=15 (0.50 LT) | deployable | A2 (stored) | 0.0328 | 1.4 [1.01, 2.07] | undetermined (n_eff < 50) | 0.02 |
| H=15 (0.50 LT) | deployable | separation | 0.0416 | 1.78 [1.14, 2.95] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | A4 (stored) | 0.0416 | 1.78 [1.14, 2.95] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | RO | 0.0246 | 1.05 [0.738, 1.49] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | R | 0.0224 | 0.955 [0.683, 1.3] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | O | 0.0312 | 1.33 [0.941, 2.01] | undetermined (n_eff < 50) | 0.077 |
| H=15 (0.50 LT) | deployable | I | 0.0276 | 1.18 [0.916, 1.57] | undetermined (n_eff < 50) | 0.21 |
| H=15 (0.50 LT) | deployable | N | 0.0325 | 1.39 [0.965, 2.09] | undetermined (n_eff < 50) | 0.068 |
| H=15 (0.50 LT) | deployable | F (ROIN) | 0.0234 | 1 | | |
| H=15 (0.50 LT) | deployable | X | 0.0136 | 0.582 [0.365, 0.848] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | A3 (stored) | 0.0252 | 1.08 [0.684, 1.79] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | X+F | 0.0148 | 0.633 [0.382, 0.937] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | none | 0.0605 | 1.61 [1.36, 1.99] | undetermined (n_eff < 50) | 0.0045 |
| H=30 (1.00 LT) | oracle | separation | 0.0388 | 1.03 [0.935, 1.16] | undetermined (n_eff < 50) | 0.603 |
| H=30 (1.00 LT) | oracle | RO | 0.038 | 1.01 [0.967, 1.07] | undetermined (n_eff < 50) | 0.603 |
| H=30 (1.00 LT) | oracle | R | 0.0602 | 1.6 [1.34, 2] | undetermined (n_eff < 50) | 0.0045 |
| H=30 (1.00 LT) | oracle | O | 0.0396 | 1.05 [0.978, 1.15] | undetermined (n_eff < 50) | 0.11 |
| H=30 (1.00 LT) | oracle | I | 0.0466 | 1.24 [1.11, 1.42] | undetermined (n_eff < 50) | 0.0045 |
| H=30 (1.00 LT) | oracle | N | 0.0568 | 1.51 [1.29, 1.83] | undetermined (n_eff < 50) | 0.0045 |
| H=30 (1.00 LT) | oracle | F (ROIN) | 0.0375 | 1 | | |
| H=30 (1.00 LT) | oracle | X | 0.0401 | 1.07 [0.977, 1.17] | undetermined (n_eff < 50) | 0.11 |
| H=30 (1.00 LT) | oracle | X+F | 0.0373 | 0.995 [0.923, 1.11] | undetermined (n_eff < 50) | 0.618 |
| H=30 (1.00 LT) | deployable | none | 0.0643 | 1.28 [1.09, 1.57] | substantial | 0.0065 |
| H=30 (1.00 LT) | deployable | A2 (stored) | 0.0642 | 1.28 [1.09, 1.57] | substantial | 0.0065 |
| H=30 (1.00 LT) | deployable | separation | 0.0725 | 1.45 [1.19, 1.85] | substantial | 0.0065 |
| H=30 (1.00 LT) | deployable | A4 (stored) | 0.0725 | 1.45 [1.19, 1.85] | substantial | 0.0065 |
| H=30 (1.00 LT) | deployable | RO | 0.0544 | 1.09 [1.01, 1.21] | needed, size not determined | 0.0125 |
| H=30 (1.00 LT) | deployable | R | 0.0571 | 1.14 [1.02, 1.32] | needed, size not determined | 0.009 |
| H=30 (1.00 LT) | deployable | O | 0.0636 | 1.27 [1.08, 1.54] | substantial | 0.0065 |
| H=30 (1.00 LT) | deployable | I | 0.0552 | 1.1 [1.02, 1.22] | needed, size not determined | 0.0065 |
| H=30 (1.00 LT) | deployable | N | 0.0637 | 1.27 [1.11, 1.5] | substantial | 0.0065 |
| H=30 (1.00 LT) | deployable | A5 (stored) | 0.0562 | 1.12 [0.977, 1.33] | undetermined | 0.05 |
| H=30 (1.00 LT) | deployable | F (ROIN) | 0.0501 | 1 | | |
| H=30 (1.00 LT) | deployable | X | 0.0444 | 0.886 [0.78, 0.983] | lowers | 1 |
| H=30 (1.00 LT) | deployable | A3 (stored) | 0.051 | 1.02 [0.893, 1.19] | undetermined | 1 |
| H=30 (1.00 LT) | deployable | X+F | 0.0453 | 0.904 [0.8, 0.977] | lowers | 1 |
| H=60 (2.00 LT) | oracle | none | 0.146 | 1.13 [1.06, 1.21] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | separation | 0.132 | 1.02 [0.972, 1.06] | undetermined | 0.447 |
| H=60 (2.00 LT) | oracle | RO | 0.131 | 1.01 [0.977, 1.05] | negligible | 0.447 |
| H=60 (2.00 LT) | oracle | R | 0.144 | 1.11 [1.05, 1.19] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | O | 0.133 | 1.02 [0.983, 1.07] | undetermined | 0.3 |
| H=60 (2.00 LT) | oracle | I | 0.142 | 1.09 [1.03, 1.16] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | N | 0.145 | 1.12 [1.06, 1.19] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | F (ROIN) | 0.13 | 1 | | |
| H=60 (2.00 LT) | oracle | X | 0.133 | 1.02 [0.982, 1.07] | undetermined | 0.3 |
| H=60 (2.00 LT) | oracle | X+F | 0.128 | 0.985 [0.954, 1.02] | negligible | 0.88 |
| H=60 (2.00 LT) | deployable | none | 0.155 | 1.05 [1.01, 1.11] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | A2 (stored) | 0.154 | 1.05 [1.01, 1.11] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | separation | 0.159 | 1.08 [1.02, 1.15] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | A4 (stored) | 0.159 | 1.08 [1.02, 1.15] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | RO | 0.15 | 1.02 [0.988, 1.06] | undetermined | 0.21 |
| H=60 (2.00 LT) | deployable | R | 0.149 | 1.02 [0.979, 1.06] | undetermined | 0.374 |
| H=60 (2.00 LT) | deployable | O | 0.153 | 1.04 [1, 1.09] | needed, size not determined | 0.0105 |
| H=60 (2.00 LT) | deployable | I | 0.15 | 1.02 [0.984, 1.07] | undetermined | 0.27 |
| H=60 (2.00 LT) | deployable | N | 0.154 | 1.05 [1.01, 1.09] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | F (ROIN) | 0.147 | 1 | | |
| H=60 (2.00 LT) | deployable | X | 0.141 | 0.959 [0.908, 1.01] | negligible | 1 |
| H=60 (2.00 LT) | deployable | A3 (stored) | 0.147 | 1 [0.944, 1.06] | undetermined | 1 |
| H=60 (2.00 LT) | deployable | X+F | 0.138 | 0.943 [0.899, 0.982] | lowers | 1 |
| H=120 (4.00 LT) | oracle | none | 0.87 | 1.01 [1, 1.02] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | separation | 0.932 | 1.08 [1.06, 1.11] | substantial | 0.0045 |
| H=120 (4.00 LT) | oracle | RO | 0.861 | 1 [0.998, 1] | negligible | 0.58 |
| H=120 (4.00 LT) | oracle | R | 0.86 | 0.999 [0.994, 1] | negligible | 1 |
| H=120 (4.00 LT) | oracle | O | 0.868 | 1.01 [1, 1.01] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | I | 0.868 | 1.01 [1, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | oracle | N | 0.869 | 1.01 [1, 1.02] | small | 0.0075 |
| H=120 (4.00 LT) | oracle | F (ROIN) | 0.861 | 1 | | |
| H=120 (4.00 LT) | oracle | X | 0.858 | 0.997 [0.988, 1.01] | negligible | 1 |
| H=120 (4.00 LT) | oracle | X+F | 0.857 | 0.996 [0.993, 1] | lowers | 1 |
| H=120 (4.00 LT) | deployable | none | 0.861 | 1.01 [1, 1.02] | small | 0.016 |
| H=120 (4.00 LT) | deployable | A2 (stored) | 0.861 | 1.01 [1, 1.02] | small | 0.016 |
| H=120 (4.00 LT) | deployable | separation | 0.907 | 1.06 [1.04, 1.09] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | A4 (stored) | 0.907 | 1.06 [1.04, 1.09] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | RO | 0.853 | 1 [0.998, 1] | negligible | 0.236 |
| H=120 (4.00 LT) | deployable | R | 0.852 | 1 [0.995, 1] | negligible | 1 |
| H=120 (4.00 LT) | deployable | O | 0.859 | 1.01 [1, 1.01] | small | 0.006 |
| H=120 (4.00 LT) | deployable | I | 0.859 | 1.01 [1, 1.02] | negligible | 0.0175 |
| H=120 (4.00 LT) | deployable | N | 0.861 | 1.01 [1, 1.02] | small | 0.016 |
| H=120 (4.00 LT) | deployable | F (ROIN) | 0.852 | 1 | | |
| H=120 (4.00 LT) | deployable | X | 0.847 | 0.994 [0.983, 1] | negligible | 1 |
| H=120 (4.00 LT) | deployable | A3 (stored) | 0.874 | 1.03 [1.01, 1.05] | small | 0.006 |
| H=120 (4.00 LT) | deployable | X+F | 0.846 | 0.993 [0.984, 1] | negligible | 1 |

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| horizon | theory gap (upper bound) [CI] | estimation gap [CI] | gap with R estimated | gap with O estimated | gap with I estimated | gap with N estimated |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 0.000523 [0.000211, 0.000926] | 0.00278 [0.00179, 0.0039] | 0.000384 [-0.000486, 0.00141] | 0.00385 [0.00216, 0.00602] | 5.25e-05 [-0.000519, 0.00061] | 0.000489 [-0.00045, 0.00173] |
| H=15 (0.50 LT) | 0.00227 [0.00115, 0.00368] | 0.0123 [0.0066, 0.0196] | 0.00106 [-0.00183, 0.00416] | 0.00598 [0.00219, 0.0101] | 0.000162 [-0.00264, 0.00304] | 0.000481 [-0.00241, 0.00348] |
| H=30 (1.00 LT) | 0.0112 [0.00805, 0.0147] | 0.0126 [0.00514, 0.0204] | 0.00676 [-2.13e-05, 0.0138] | 0.0136 [0.00635, 0.0211] | 0.00568 [-0.000512, 0.0123] | 0.00296 [-0.00299, 0.00892] |
| H=60 (2.00 LT) | 0.0442 [0.0387, 0.05] | 0.0168 [0.00578, 0.0277] | 0.00461 [-0.00491, 0.0137] | 0.0161 [0.00505, 0.027] | 0.00781 [-0.00156, 0.0167] | 0.0043 [-0.00468, 0.0128] |
| H=120 (4.00 LT) | 0.252 [0.24, 0.264] | -0.00838 [-0.0323, 0.0146] | -0.00775 [-0.0317, 0.0157] | -0.00833 [-0.0322, 0.0151] | -0.00773 [-0.0311, 0.0164] | -0.00715 [-0.0305, 0.0165] |

### Horizon decision (Y = ln min(T_c, H_max))

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED. Pinball loss at tau = 0.5; drop-one ratio at level 1 - 0.05/4; ladder ratio vs F at 1 - 0.05/m; C = Harrell's C (95%); coverage of q_0.1, q_0.5, q_0.9 and the 80% interval below the cap.

| profile | X | pinball ratio [CI] | reading | Holm p | phi [CI] |
|---|---|---|---|---|---|
| oracle | R | 1 [0.992, 1.01] | negligible | 0.483 | 0.00111 [0.000452, 0.00171] |
| oracle | O | 1.09 [1.07, 1.12] | substantial | 0.002 | 0.0083 [0.00662, 0.00993] |
| oracle | I | 1.25 [1.21, 1.3] | substantial | 0.002 | 0.0325 [0.0287, 0.0366] |
| oracle | N | 0.999 [0.989, 1.01] | negligible | 0.589 | 0.000801 [4.7e-05, 0.00153] |
| deployable | R | 1 [0.997, 1.01] | negligible | 0.163 | 0.00208 [0.00154, 0.00261] |
| deployable | O | 1.09 [1.07, 1.11] | substantial | 0.002 | 0.00972 [0.00825, 0.0111] |
| deployable | I | 1.27 [1.23, 1.32] | substantial | 0.002 | 0.0336 [0.0298, 0.0377] |
| deployable | N | 0.992 [0.983, 1] | lowers | 0.994 | 0.000177 [-0.00036, 0.000744] |

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | ratio vs F [CI] | reading | C [CI] | cov 0.1 / 0.5 / 0.9 / 80% |
|---|---|---|---|---|---|---|
| oracle | none | 0.195 | 1.28 [1.23, 1.33] | substantial | 0.5 [0.5, 0.5] | 0.111 / 0.517 / 0.906 / 0.795 |
| oracle | lyapunov | 0.298 | 1.96 [1.86, 2.09] | substantial | 0.625 [0.614, 0.637] | 0.0794 / 0.462 / 0.849 / 0.814 |
| oracle | RO | 0.191 | 1.26 [1.21, 1.31] | substantial | 0.56 [0.549, 0.57] | 0.143 / 0.517 / 0.893 / 0.75 |
| oracle | R | 0.193 | 1.27 [1.22, 1.32] | substantial | 0.538 [0.527, 0.548] | 0.136 / 0.508 / 0.899 / 0.763 |
| oracle | O | 0.193 | 1.27 [1.22, 1.33] | substantial | 0.544 [0.534, 0.553] | 0.113 / 0.527 / 0.902 / 0.79 |
| oracle | I | 0.168 | 1.11 [1.08, 1.14] | substantial | 0.635 [0.624, 0.646] | 0.113 / 0.521 / 0.902 / 0.789 |
| oracle | N | 0.193 | 1.27 [1.22, 1.32] | substantial | 0.55 [0.54, 0.56] | 0.114 / 0.518 / 0.899 / 0.786 |
| oracle | ROIN | 0.152 | 1 |  | 0.684 [0.672, 0.695] | 0.15 / 0.519 / 0.865 / 0.715 |
| oracle | X | 0.164 | 1.08 [1.03, 1.13] | needed, size not determined | 0.67 [0.659, 0.68] | 0.158 / 0.513 / 0.855 / 0.698 |
| oracle | X+F | 0.135 | 0.887 [0.865, 0.91] | lowers | 0.724 [0.713, 0.734] | 0.171 / 0.522 / 0.862 / 0.691 |
| oracle | Lyapunov rank (C only) | | | | 0.621 [0.609, 0.632] | |
| deployable | none | 0.195 | 1.31 [1.26, 1.36] | substantial | 0.5 [0.5, 0.5] | 0.111 / 0.517 / 0.906 / 0.795 |
| deployable | lyapunov | 0.298 | 2 [1.89, 2.11] | substantial | 0.623 [0.612, 0.634] | 0.0797 / 0.462 / 0.845 / 0.813 |
| deployable | RO | 0.191 | 1.28 [1.23, 1.33] | substantial | 0.562 [0.551, 0.572] | 0.108 / 0.524 / 0.893 / 0.785 |
| deployable | R | 0.193 | 1.3 [1.25, 1.35] | substantial | 0.538 [0.528, 0.546] | 0.106 / 0.515 / 0.896 / 0.79 |
| deployable | O | 0.192 | 1.29 [1.24, 1.34] | substantial | 0.554 [0.545, 0.564] | 0.11 / 0.527 / 0.898 / 0.788 |
| deployable | I | 0.171 | 1.15 [1.11, 1.18] | substantial | 0.628 [0.618, 0.638] | 0.108 / 0.519 / 0.906 / 0.799 |
| deployable | N | 0.194 | 1.3 [1.25, 1.35] | substantial | 0.54 [0.533, 0.548] | 0.111 / 0.517 / 0.899 / 0.788 |
| deployable | ROIN | 0.149 | 1 |  | 0.689 [0.678, 0.699] | 0.135 / 0.516 / 0.87 / 0.735 |
| deployable | X | 0.165 | 1.11 [1.06, 1.15] | substantial | 0.669 [0.659, 0.679] | 0.154 / 0.51 / 0.862 / 0.708 |
| deployable | X+F | 0.136 | 0.91 [0.889, 0.931] | lowers | 0.717 [0.706, 0.727] | 0.157 / 0.516 / 0.861 / 0.703 |
| deployable | Lyapunov rank (C only) | | | | 0.622 [0.61, 0.634] | |

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| profile | pair | Delta [CI] | Holm p | detected |
|---|---|---|---|---|
| oracle | RO | 0.000336 [-0.000113, 0.000758] | 0.108 | False |
| oracle | RI (primary) | 0.000573 [-0.000567, 0.00158] | 0.256 | False |
| oracle | RN | 0.00048 [4.44e-05, 0.000919] | 0.0125 | True |
| oracle | OI (primary) | 0.015 [0.0107, 0.0191] | 0.003 | True |
| oracle | ON | 0.000201 [-0.000379, 0.000762] | 0.344 | False |
| oracle | IN | -0.000278 [-0.00213, 0.00152] | 0.642 | False |
| deployable | RO | 0.000878 [2.79e-05, 0.00174] | 0.016 | True |
| deployable | RI (primary) | 0.00431 [0.00243, 0.00633] | 0.003 | True |
| deployable | RN | 0.000172 [-0.000422, 0.000707] | 0.198 | False |
| deployable | OI (primary) | 0.0185 [0.0149, 0.0225] | 0.003 | True |
| deployable | ON | 0.000542 [-0.000253, 0.0013] | 0.0795 | False |
| deployable | IN | 0.000572 [-0.000284, 0.00143] | 0.086 | False |

## rossler

**PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.**

| check | result |
|---|---|
| (f1) state_mse from per-draw errors, max rel diff | A0 0.0e+00, A1 0.0e+00, A2 0.0e+00, A3 0.0e+00, A4 0.0e+00, A5 0.0e+00 (within 1e-12: True) |
| (g) WU-0039b (b1), (b2) rows reproduced | drop-N: True, all rows: True |
| separation formula on F-hat vs stored A4 at H_ref, max abs | 2.22e-16 |
| T_c: T = 1 / e_(T-1) = theta (train, test) | 0/0, 0/0 |
| (f2) dependence bias, deployable rows (reported, not gating) | 131 rows; 78 flagged: H=8 R: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0126, z 7.06; H=8 N: dependence bias detectable (interval excludes 0), t1+t2 / V 0.014, z 5.9; H=8 RO: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0213, z 6.98; H=8 RI: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0124, z 6.69; H=8 RN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0211, z 8.11; H=8 ON: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0135, z 5.62; H=8 IN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0144, z 5.89; H=8 ROI: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0206, z 6.74; H=8 RON: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0256, z 8.01; H=8 RIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0218, z 7.88; H=8 OIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0137, z 5.65; H=8 ROIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0251, z 7.84 ... |

### A. Allocation: drop-one and Shapley

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED. MSE ratio MSE(F without X)/MSE(F) at level 1 - 0.05/4 (reading by the 1.05 table, with the n_eff guard); excess ratio L_A(F without X)/L_A(F) and Holm p (Delta MSE > 0) are estimates. phi = Shapley share of L_A (95%). Oracle rows: moment form; deployable rows: realized per draw.

| horizon | profile | X | MSE ratio [CI] | reading | excess ratio | Holm p | phi_X [95% CI] | share |
|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | R | 1.06 [1.05, 1.07] | substantial | 1.63 | 0.002 | 7.58e-06 [6.83e-06, 8.33e-06] | 0.663 |
| H=8 (0.27 LT) | oracle | O | 1.02 [1.01, 1.02] | small | 1.16 | 0.002 | 1.06e-06 [8.41e-07, 1.3e-06] | 0.0924 |
| H=8 (0.27 LT) | oracle | I | 0.999 [0.999, 1] | negligible | 0.993 | 0.992 | -4e-08 [-1.19e-07, 2.77e-08] | -0.0035 |
| H=8 (0.27 LT) | oracle | N | 1.01 [1.01, 1.02] | small | 1.11 | 0.002 | 2.83e-06 [2.49e-06, 3.16e-06] | 0.248 |
| H=8 (0.27 LT) | deployable | R | 1.01 [0.999, 1.01] | negligible | 1.03 | 0.0675 | 1.76e-07 [-3.59e-07, 7.06e-07] | 0.198 |
| H=8 (0.27 LT) | deployable | O | 1.01 [1, 1.01] | small | 1.04 | 0.004 | 5.44e-07 [2.35e-07, 8.69e-07] | 0.613 |
| H=8 (0.27 LT) | deployable | I | 1 [0.999, 1] | negligible | 1.01 | 0.187 | 1.02e-07 [-1.05e-08, 2.21e-07] | 0.115 |
| H=8 (0.27 LT) | deployable | N | 1 [0.995, 1] | negligible | 1 | 0.464 | 6.56e-08 [-4.3e-07, 5.29e-07] | 0.074 |
| H=15 (0.50 LT) | oracle | R | 1.07 [1.06, 1.09] | substantial | 1.82 | 0.002 | 1.56e-05 [1.37e-05, 1.75e-05] | 0.683 |
| H=15 (0.50 LT) | oracle | O | 1.02 [1.01, 1.03] | small | 1.21 | 0.002 | 2.16e-06 [1.5e-06, 2.88e-06] | 0.0947 |
| H=15 (0.50 LT) | oracle | I | 1 [0.999, 1] | negligible | 0.999 | 0.613 | 2.04e-08 [-1.97e-07, 2.38e-07] | 0.000893 |
| H=15 (0.50 LT) | oracle | N | 1.01 [1.01, 1.01] | small | 1.1 | 0.002 | 5.04e-06 [4.36e-06, 5.77e-06] | 0.221 |
| H=15 (0.50 LT) | deployable | R | 1 [0.993, 1.01] | negligible | 1.02 | 0.636 | 1.05e-06 [-4.08e-07, 2.53e-06] | 0.523 |
| H=15 (0.50 LT) | deployable | O | 1 [0.991, 1.01] | negligible | 1 | 0.86 | 2.75e-07 [-8.53e-07, 1.39e-06] | 0.137 |
| H=15 (0.50 LT) | deployable | I | 1 [0.999, 1] | negligible | 1.01 | 0.356 | 3.52e-07 [-1.23e-08, 7.29e-07] | 0.176 |
| H=15 (0.50 LT) | deployable | N | 0.999 [0.994, 1] | negligible | 0.994 | 0.86 | 3.29e-07 [-7.21e-07, 1.41e-06] | 0.164 |
| H=30 (1.00 LT) | oracle | R | 1.1 [1.08, 1.12] | substantial | 2.3 | 0.002 | 6.35e-05 [5.55e-05, 7.28e-05] | 0.669 |
| H=30 (1.00 LT) | oracle | O | 1.03 [1.02, 1.05] | small | 1.46 | 0.002 | 1.33e-05 [9.47e-06, 1.77e-05] | 0.14 |
| H=30 (1.00 LT) | oracle | I | 1 [0.997, 1] | negligible | 1 | 0.476 | 8.49e-07 [4.79e-08, 1.69e-06] | 0.00894 |
| H=30 (1.00 LT) | oracle | N | 1.01 [1.01, 1.02] | small | 1.14 | 0.002 | 1.74e-05 [1.45e-05, 2.04e-05] | 0.183 |
| H=30 (1.00 LT) | deployable | R | 1 [0.992, 1.02] | negligible | 1.02 | 0.606 | 2.19e-06 [-3.2e-06, 7.62e-06] | 0.458 |
| H=30 (1.00 LT) | deployable | O | 1 [0.989, 1.01] | negligible | 1 | 0.606 | 3.94e-07 [-3.72e-06, 4.4e-06] | 0.0824 |
| H=30 (1.00 LT) | deployable | I | 1 [0.999, 1] | negligible | 1.01 | 0.292 | 1e-06 [2.57e-08, 1.97e-06] | 0.209 |
| H=30 (1.00 LT) | deployable | N | 1 [0.995, 1.01] | negligible | 1.01 | 0.606 | 1.19e-06 [-3.16e-06, 5.13e-06] | 0.25 |
| H=60 (2.00 LT) | oracle | R | 1.07 [1.04, 1.09] | needed, size not determined | 1.3 | 0.002 | 0.000862 [0.00067, 0.00105] | 0.796 |
| H=60 (2.00 LT) | oracle | O | 1.01 [0.994, 1.02] | negligible | 1.03 | 0.145 | 3.23e-05 [-3.16e-05, 9.37e-05] | 0.0298 |
| H=60 (2.00 LT) | oracle | I | 1 [0.998, 1.01] | negligible | 1.01 | 0.145 | 3.13e-05 [5.92e-06, 5.61e-05] | 0.0289 |
| H=60 (2.00 LT) | oracle | N | 1.01 [1, 1.01] | small | 1.03 | 0.006 | 0.000157 [9.46e-05, 0.000217] | 0.145 |
| H=60 (2.00 LT) | deployable | R | 1.01 [0.998, 1.02] | negligible | 1.03 | 0.092 | 0.000128 [6.8e-06, 0.00025] | 0.619 |
| H=60 (2.00 LT) | deployable | O | 1 [0.999, 1.01] | negligible | 1.01 | 0.092 | 3.22e-05 [-2.32e-06, 6.72e-05] | 0.156 |
| H=60 (2.00 LT) | deployable | I | 1 [1, 1] | negligible | 1 | 0.092 | 4.14e-05 [1.23e-05, 6.99e-05] | 0.201 |
| H=60 (2.00 LT) | deployable | N | 0.998 [0.994, 1] | negligible | 0.993 | 0.904 | 5.2e-06 [-6.64e-05, 7.99e-05] | 0.0251 |
| H=120 (4.00 LT) | oracle | R | 1.01 [1, 1.01] | small | 1.03 | 0.002 | 0.00108 [0.000646, 0.00147] | 0.642 |
| H=120 (4.00 LT) | oracle | O | 1 [0.999, 1] | negligible | 1 | 0.18 | 9.4e-05 [-9.02e-05, 0.000275] | 0.0562 |
| H=120 (4.00 LT) | oracle | I | 1 [1, 1.01] | small | 1.02 | 0.002 | 0.000623 [0.000339, 0.000899] | 0.372 |
| H=120 (4.00 LT) | oracle | N | 0.998 [0.995, 1] | negligible | 0.993 | 0.919 | -0.000118 [-0.000494, 0.000257] | -0.0703 |
| H=120 (4.00 LT) | deployable | R | 1 [0.999, 1] | negligible | 1 | 0.379 | 0.000255 [-6.04e-05, 0.000561] | 0.181 |
| H=120 (4.00 LT) | deployable | O | 1 [0.999, 1] | negligible | 1 | 0.379 | 8.87e-05 [-0.000121, 0.000294] | 0.0632 |
| H=120 (4.00 LT) | deployable | I | 1.01 [1, 1.01] | small | 1.03 | 0.002 | 0.00093 [0.000615, 0.00126] | 0.662 |
| H=120 (4.00 LT) | deployable | N | 1 [0.997, 1] | negligible | 1 | 0.499 | 0.000131 [-0.000201, 0.000464] | 0.0931 |

### A. Allocation: summary per horizon

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED. n_eff = Kish size of kappa on the test states; G = 1 - L_A(rule)/L_A(constant), estimate (95%).

| horizon | profile | n_eff(kappa) | G(F) [CI] | G(separation) | MSE(F)/MSE(sep) [CI] | reading | settings (A) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 721 | 0.503 [0.477, 0.525] | 0.206 | 0.945 [0.938, 0.951] | lowers | F: mid; qn 2, mid 6, low 7 |
| H=8 (0.27 LT) | deployable | 721 | 0.0403 [-0.00147, 0.0816] | -0.399 | 0.928 [0.916, 0.94] | lowers | F: mid; qn 0, mid 6, low 9 |
| H=15 (0.50 LT) | oracle | 463 | 0.556 [0.523, 0.589] | 0.314 | 0.953 [0.947, 0.959] | lowers | F: mid; qn 0, mid 9, low 6 |
| H=15 (0.50 LT) | deployable | 463 | 0.0452 [-0.0139, 0.101] | -0.259 | 0.943 [0.931, 0.955] | lowers | F: mid; qn 0, mid 9, low 6 |
| H=30 (1.00 LT) | oracle | 349 | 0.645 [0.606, 0.681] | 0.499 | 0.97 [0.964, 0.976] | lowers | F: qn; qn 4, mid 4, low 7 |
| H=30 (1.00 LT) | deployable | 349 | 0.0301 [-0.0352, 0.0895] | -0.159 | 0.964 [0.95, 0.979] | lowers | F: mid; qn 0, mid 4, low 11 |
| H=60 (2.00 LT) | oracle | 558 | 0.291 [0.23, 0.346] | 0.298 | 1 [0.994, 1.01] | negligible | F: mid; qn 0, mid 4, low 11 |
| H=60 (2.00 LT) | deployable | 558 | 0.0461 [0.00907, 0.0819] | 0.0335 | 0.996 [0.985, 1.01] | negligible | F: low; qn 0, mid 0, low 15 |
| H=120 (4.00 LT) | oracle | 1.54e+03 | 0.0543 [0.0376, 0.0712] | -0.174 | 0.938 [0.925, 0.95] | lowers | F: low; qn 0, mid 0, low 15 |
| H=120 (4.00 LT) | deployable | 1.54e+03 | 0.0433 [0.0269, 0.0583] | -0.242 | 0.921 [0.908, 0.934] | lowers | F: low; qn 0, mid 0, low 15 |

### B. Allocation: pairwise interactions (logit u, interior states)

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED. Delta = L(additive) - L(additive + pair) on the test states, models fixed; level 1 - 0.05/6; Holm over the six pairs. R x I and O x I are primary.

| horizon | profile | pair | Delta [CI] | Holm p | reading | loss ratio reading |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | RI (primary) | -0.00885 [-0.037, 0.0173] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | OI (primary) | 0.00528 [-0.0143, 0.0235] | 0.72 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | RO | 0.0643 [0.018, 0.11] | 0.003 | interaction gain detected | small |
| H=8 (0.27 LT) | oracle | RN | 0.0211 [-0.0118, 0.0522] | 0.192 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | ON | 0.0443 [0.0177, 0.0723] | 0.003 | interaction gain detected | small |
| H=8 (0.27 LT) | oracle | IN | -0.0188 [-0.0371, -0.00033] | 1 | no interaction gain; the pair model fits worse | no interaction gain; the pair model fits worse |
| H=8 (0.27 LT) | deployable | RI (primary) | 0.0119 [-0.00365, 0.0266] | 0.093 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | OI (primary) | 0.014 [-0.0117, 0.0419] | 0.149 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RO | 0.106 [0.0685, 0.147] | 0.003 | interaction gain detected | small |
| H=8 (0.27 LT) | deployable | RN | 0.0251 [0.00407, 0.0463] | 0.005 | interaction gain detected | small |
| H=8 (0.27 LT) | deployable | ON | 0.0187 [0.00145, 0.0343] | 0.006 | interaction gain detected | small |
| H=8 (0.27 LT) | deployable | IN | -0.00386 [-0.0141, 0.00547] | 0.857 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | RI (primary) | 7.01e-05 [-0.0241, 0.026] | 0.993 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | OI (primary) | 0.0125 [0.000641, 0.025] | 0.0105 | interaction gain detected | small |
| H=15 (0.50 LT) | oracle | RO | 0.0649 [0.0208, 0.112] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | oracle | RN | 0.028 [0.00375, 0.0522] | 0.008 | interaction gain detected | small |
| H=15 (0.50 LT) | oracle | ON | 0.0379 [0.0118, 0.0641] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | oracle | IN | -0.00958 [-0.0226, 0.00493] | 0.993 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | RI (primary) | 0.00379 [-0.013, 0.0223] | 0.57 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | OI (primary) | 0.0174 [0.00545, 0.0291] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | deployable | RO | 0.078 [0.0359, 0.118] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | deployable | RN | 0.0258 [0.00637, 0.0451] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | deployable | ON | 0.0335 [0.0152, 0.0535] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | deployable | IN | 0.000397 [-0.00879, 0.00985] | 0.57 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | RI (primary) | 0.0136 [-0.00996, 0.0377] | 0.138 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | OI (primary) | 0.0233 [-0.00239, 0.0491] | 0.03 | interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | RO | 0.113 [0.0684, 0.168] | 0.003 | interaction gain detected | needed, size not determined |
| H=30 (1.00 LT) | oracle | RN | 0.0291 [0.00528, 0.0588] | 0.0075 | interaction gain detected | small |
| H=30 (1.00 LT) | oracle | ON | 0.0292 [0.00217, 0.0563] | 0.012 | interaction gain detected | small |
| H=30 (1.00 LT) | oracle | IN | 0.00222 [-0.00896, 0.0144] | 0.302 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | RI (primary) | 0.0258 [0.00373, 0.049] | 0.01 | interaction gain detected | small |
| H=30 (1.00 LT) | deployable | OI (primary) | 0.0195 [-0.00903, 0.0535] | 0.1 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | RO | 0.059 [0.0165, 0.103] | 0.006 | interaction gain detected | small |
| H=30 (1.00 LT) | deployable | RN | 0.016 [-0.00815, 0.037] | 0.1 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | ON | 0.0105 [-0.00432, 0.0251] | 0.094 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | IN | 0.00742 [-0.00321, 0.0178] | 0.1 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | RI (primary) | 0.0503 [0.00986, 0.089] | 0.004 | interaction gain detected | small |
| H=60 (2.00 LT) | oracle | OI (primary) | 0.0761 [0.0438, 0.105] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | oracle | RO | 0.0869 [0.0472, 0.131] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | oracle | RN | 0.0191 [-0.00909, 0.049] | 0.0415 | interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | ON | 0.0403 [0.0035, 0.0752] | 0.0045 | interaction gain detected | small |
| H=60 (2.00 LT) | oracle | IN | 0.0221 [0.00147, 0.0435] | 0.005 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | RI (primary) | 0.0353 [0.00787, 0.0615] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | OI (primary) | 0.0555 [0.029, 0.0817] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | RO | 0.0688 [0.0344, 0.103] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | RN | 0.0145 [-0.0052, 0.0321] | 0.084 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | ON | 0.0093 [-0.00658, 0.0244] | 0.154 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | IN | 0.0045 [-0.0163, 0.0233] | 0.299 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RI (primary) | 0.015 [-0.00259, 0.0322] | 0.054 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | OI (primary) | 0.00517 [-0.00397, 0.0149] | 0.256 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RO | 0.014 [-0.00167, 0.0303] | 0.045 | interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RN | 0.0057 [-0.00741, 0.019] | 0.265 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | ON | 0.00916 [0.00164, 0.0168] | 0.006 | interaction gain detected | small |
| H=120 (4.00 LT) | oracle | IN | -0.00183 [-0.0167, 0.0127] | 0.623 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RI (primary) | -0.00156 [-0.0113, 0.00888] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | OI (primary) | -0.000371 [-0.0105, 0.00962] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RO | 9.69e-05 [-0.00605, 0.00584] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RN | -0.00163 [-0.0081, 0.00468] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | ON | 7.13e-06 [-0.00474, 0.00498] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | IN | -0.00532 [-0.0184, 0.00659] | 1 | no interaction gain detected | negligible |

### D. Allocation ladder (rung against the full profile)

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED. MSE ratio MSE(rung)/MSE(F) at level 1 - 0.05/m (m rungs); Holm p for Delta MSE > 0. Theory gap L_A(oracle F) is an upper bound; estimation gap = L_A(deployable F) - L_A(oracle F) (95%).

| horizon | profile | rung | MSE | MSE ratio vs F [CI] | reading | Holm p |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | none | 0.000126 | 1.1 [1.09, 1.11] | substantial | 0.0045 |
| H=8 (0.27 LT) | oracle | separation | 0.000122 | 1.06 [1.05, 1.07] | needed, size not determined | 0.0045 |
| H=8 (0.27 LT) | oracle | RO | 0.000116 | 1.01 [1, 1.01] | small | 0.0045 |
| H=8 (0.27 LT) | oracle | R | 0.000119 | 1.03 [1.03, 1.04] | small | 0.0045 |
| H=8 (0.27 LT) | oracle | O | 0.000126 | 1.1 [1.09, 1.11] | substantial | 0.0045 |
| H=8 (0.27 LT) | oracle | I | 0.000126 | 1.1 [1.09, 1.11] | substantial | 0.0045 |
| H=8 (0.27 LT) | oracle | N | 0.000122 | 1.06 [1.05, 1.07] | substantial | 0.0045 |
| H=8 (0.27 LT) | oracle | F (ROIN) | 0.000115 | 1 | | |
| H=8 (0.27 LT) | oracle | X | 0.000125 | 1.09 [1.07, 1.1] | substantial | 0.0045 |
| H=8 (0.27 LT) | oracle | X+F | 0.000115 | 1 [0.992, 1.01] | negligible | 0.561 |
| H=8 (0.27 LT) | deployable | none | 0.000126 | 1.01 [0.996, 1.02] | negligible | 0.206 |
| H=8 (0.27 LT) | deployable | A2 (stored) | 0.000126 | 1.01 [0.996, 1.02] | negligible | 0.206 |
| H=8 (0.27 LT) | deployable | separation | 0.000134 | 1.08 [1.06, 1.1] | substantial | 0.006 |
| H=8 (0.27 LT) | deployable | A4 (stored) | 0.000134 | 1.08 [1.06, 1.1] | substantial | 0.006 |
| H=8 (0.27 LT) | deployable | RO | 0.000125 | 1 [0.996, 1.01] | negligible | 0.696 |
| H=8 (0.27 LT) | deployable | R | 0.000126 | 1.01 [1, 1.02] | small | 0.009 |
| H=8 (0.27 LT) | deployable | O | 0.000126 | 1.01 [0.995, 1.02] | negligible | 0.25 |
| H=8 (0.27 LT) | deployable | I | 0.000126 | 1.01 [0.996, 1.02] | negligible | 0.247 |
| H=8 (0.27 LT) | deployable | N | 0.000126 | 1.01 [1, 1.01] | small | 0.02 |
| H=8 (0.27 LT) | deployable | F (ROIN) | 0.000125 | 1 | | |
| H=8 (0.27 LT) | deployable | X | 0.000124 | 0.993 [0.98, 1] | negligible | 1 |
| H=8 (0.27 LT) | deployable | A3 (stored) | 0.000132 | 1.06 [1.04, 1.09] | needed, size not determined | 0.006 |
| H=8 (0.27 LT) | deployable | X+F | 0.000124 | 0.993 [0.988, 0.998] | lowers | 1 |
| H=15 (0.50 LT) | oracle | none | 0.000224 | 1.11 [1.1, 1.13] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | separation | 0.000211 | 1.05 [1.04, 1.06] | needed, size not determined | 0.0045 |
| H=15 (0.50 LT) | oracle | RO | 0.000203 | 1.01 [1.01, 1.01] | small | 0.0045 |
| H=15 (0.50 LT) | oracle | R | 0.000208 | 1.03 [1.03, 1.04] | small | 0.0045 |
| H=15 (0.50 LT) | oracle | O | 0.000223 | 1.11 [1.1, 1.13] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | I | 0.000223 | 1.11 [1.1, 1.13] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | N | 0.000216 | 1.07 [1.06, 1.09] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | F (ROIN) | 0.000201 | 1 | | |
| H=15 (0.50 LT) | oracle | X | 0.00022 | 1.1 [1.08, 1.12] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | X+F | 0.0002 | 0.998 [0.995, 1] | lowers | 0.999 |
| H=15 (0.50 LT) | deployable | none | 0.000227 | 1.01 [0.992, 1.03] | negligible | 0.612 |
| H=15 (0.50 LT) | deployable | A2 (stored) | 0.000227 | 1.01 [0.992, 1.03] | negligible | 0.612 |
| H=15 (0.50 LT) | deployable | separation | 0.000238 | 1.06 [1.04, 1.08] | needed, size not determined | 0.006 |
| H=15 (0.50 LT) | deployable | A4 (stored) | 0.000238 | 1.06 [1.04, 1.08] | needed, size not determined | 0.006 |
| H=15 (0.50 LT) | deployable | RO | 0.000225 | 1 [0.994, 1.01] | negligible | 1 |
| H=15 (0.50 LT) | deployable | R | 0.000226 | 1 [0.99, 1.02] | negligible | 0.698 |
| H=15 (0.50 LT) | deployable | O | 0.000227 | 1.01 [0.993, 1.03] | negligible | 0.612 |
| H=15 (0.50 LT) | deployable | I | 0.000227 | 1.01 [0.991, 1.02] | negligible | 0.612 |
| H=15 (0.50 LT) | deployable | N | 0.000226 | 1.01 [0.992, 1.02] | negligible | 0.612 |
| H=15 (0.50 LT) | deployable | F (ROIN) | 0.000225 | 1 | | |
| H=15 (0.50 LT) | deployable | X | 0.000223 | 0.993 [0.979, 1.01] | negligible | 1 |
| H=15 (0.50 LT) | deployable | A3 (stored) | 0.000234 | 1.04 [1.02, 1.06] | needed, size not determined | 0.006 |
| H=15 (0.50 LT) | deployable | X+F | 0.000223 | 0.99 [0.985, 0.996] | lowers | 1 |
| H=30 (1.00 LT) | oracle | none | 0.0008 | 1.13 [1.11, 1.16] | substantial | 0.0045 |
| H=30 (1.00 LT) | oracle | separation | 0.000726 | 1.03 [1.02, 1.04] | small | 0.0045 |
| H=30 (1.00 LT) | oracle | RO | 0.000713 | 1.01 [1.01, 1.02] | small | 0.0045 |
| H=30 (1.00 LT) | oracle | R | 0.000743 | 1.05 [1.04, 1.07] | needed, size not determined | 0.0045 |
| H=30 (1.00 LT) | oracle | O | 0.0008 | 1.14 [1.11, 1.16] | substantial | 0.0045 |
| H=30 (1.00 LT) | oracle | I | 0.000799 | 1.13 [1.11, 1.16] | substantial | 0.0045 |
| H=30 (1.00 LT) | oracle | N | 0.000774 | 1.1 [1.08, 1.12] | substantial | 0.0045 |
| H=30 (1.00 LT) | oracle | F (ROIN) | 0.000704 | 1 | | |
| H=30 (1.00 LT) | oracle | X | 0.000788 | 1.12 [1.1, 1.14] | substantial | 0.0045 |
| H=30 (1.00 LT) | oracle | X+F | 0.000707 | 1 [0.997, 1.01] | negligible | 0.0895 |
| H=30 (1.00 LT) | deployable | none | 0.000811 | 1.01 [0.988, 1.02] | negligible | 1 |
| H=30 (1.00 LT) | deployable | A2 (stored) | 0.000811 | 1.01 [0.987, 1.02] | negligible | 1 |
| H=30 (1.00 LT) | deployable | separation | 0.000836 | 1.04 [1.02, 1.06] | needed, size not determined | 0.0065 |
| H=30 (1.00 LT) | deployable | A4 (stored) | 0.000836 | 1.04 [1.02, 1.06] | needed, size not determined | 0.0065 |
| H=30 (1.00 LT) | deployable | RO | 0.000809 | 1 [0.995, 1.01] | negligible | 0.92 |
| H=30 (1.00 LT) | deployable | R | 0.000809 | 1 [0.987, 1.02] | negligible | 1 |
| H=30 (1.00 LT) | deployable | O | 0.00081 | 1.01 [0.987, 1.02] | negligible | 1 |
| H=30 (1.00 LT) | deployable | I | 0.00081 | 1 [0.987, 1.02] | negligible | 1 |
| H=30 (1.00 LT) | deployable | N | 0.00081 | 1 [0.99, 1.02] | negligible | 1 |
| H=30 (1.00 LT) | deployable | A5 (stored) | 0.000813 | 1.01 [0.992, 1.02] | negligible | 0.913 |
| H=30 (1.00 LT) | deployable | F (ROIN) | 0.000806 | 1 | | |
| H=30 (1.00 LT) | deployable | X | 0.000799 | 0.991 [0.973, 1.01] | negligible | 1 |
| H=30 (1.00 LT) | deployable | A3 (stored) | 0.000815 | 1.01 [0.988, 1.04] | negligible | 0.92 |
| H=30 (1.00 LT) | deployable | X+F | 0.000798 | 0.99 [0.983, 0.998] | lowers | 1 |
| H=60 (2.00 LT) | oracle | none | 0.0127 | 1.09 [1.06, 1.12] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | separation | 0.0116 | 0.998 [0.987, 1.01] | negligible | 1 |
| H=60 (2.00 LT) | oracle | RO | 0.0117 | 1.01 [1, 1.01] | small | 0.012 |
| H=60 (2.00 LT) | oracle | R | 0.0118 | 1.01 [0.998, 1.03] | negligible | 0.033 |
| H=60 (2.00 LT) | oracle | O | 0.0127 | 1.1 [1.07, 1.13] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | I | 0.0127 | 1.09 [1.06, 1.12] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | N | 0.0125 | 1.07 [1.05, 1.1] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | F (ROIN) | 0.0116 | 1 | | |
| H=60 (2.00 LT) | oracle | X | 0.0127 | 1.09 [1.06, 1.12] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | X+F | 0.0116 | 0.996 [0.986, 1] | negligible | 1 |
| H=60 (2.00 LT) | deployable | none | 0.0135 | 1.02 [0.996, 1.04] | negligible | 0.095 |
| H=60 (2.00 LT) | deployable | A2 (stored) | 0.0135 | 1.02 [0.997, 1.04] | negligible | 0.0825 |
| H=60 (2.00 LT) | deployable | separation | 0.0133 | 1 [0.988, 1.02] | negligible | 0.876 |
| H=60 (2.00 LT) | deployable | A4 (stored) | 0.0133 | 1 [0.988, 1.02] | negligible | 0.876 |
| H=60 (2.00 LT) | deployable | RO | 0.0133 | 0.999 [0.994, 1] | negligible | 1 |
| H=60 (2.00 LT) | deployable | R | 0.0134 | 1.01 [0.995, 1.02] | negligible | 0.367 |
| H=60 (2.00 LT) | deployable | O | 0.0135 | 1.02 [0.996, 1.04] | negligible | 0.095 |
| H=60 (2.00 LT) | deployable | I | 0.0134 | 1.01 [0.994, 1.03] | negligible | 0.234 |
| H=60 (2.00 LT) | deployable | N | 0.0135 | 1.01 [1, 1.03] | small | 0.018 |
| H=60 (2.00 LT) | deployable | F (ROIN) | 0.0133 | 1 | | |
| H=60 (2.00 LT) | deployable | X | 0.0134 | 1.01 [0.992, 1.03] | negligible | 0.27 |
| H=60 (2.00 LT) | deployable | A3 (stored) | 0.0135 | 1.02 [0.996, 1.04] | negligible | 0.128 |
| H=60 (2.00 LT) | deployable | X+F | 0.0133 | 1 [0.996, 1] | negligible | 1 |
| H=120 (4.00 LT) | oracle | none | 0.108 | 1.02 [1.01, 1.02] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | separation | 0.113 | 1.07 [1.05, 1.09] | needed, size not determined | 0.0045 |
| H=120 (4.00 LT) | oracle | RO | 0.106 | 1 [0.999, 1.01] | negligible | 0.058 |
| H=120 (4.00 LT) | oracle | R | 0.107 | 1.01 [1, 1.01] | small | 0.006 |
| H=120 (4.00 LT) | oracle | O | 0.108 | 1.02 [1.01, 1.02] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | I | 0.107 | 1.01 [1, 1.02] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | N | 0.108 | 1.02 [1.01, 1.02] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | F (ROIN) | 0.106 | 1 | | |
| H=120 (4.00 LT) | oracle | X | 0.107 | 1.01 [1, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | X+F | 0.105 | 0.992 [0.982, 1] | negligible | 0.989 |
| H=120 (4.00 LT) | deployable | none | 0.109 | 1.01 [1.01, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | A2 (stored) | 0.109 | 1.01 [1.01, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | separation | 0.117 | 1.09 [1.06, 1.11] | substantial | 0.006 |
| H=120 (4.00 LT) | deployable | A4 (stored) | 0.117 | 1.09 [1.06, 1.11] | substantial | 0.006 |
| H=120 (4.00 LT) | deployable | RO | 0.109 | 1.01 [1, 1.01] | small | 0.006 |
| H=120 (4.00 LT) | deployable | R | 0.109 | 1.01 [1, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | O | 0.109 | 1.01 [1.01, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | I | 0.108 | 1 [0.997, 1.01] | negligible | 0.15 |
| H=120 (4.00 LT) | deployable | N | 0.109 | 1.01 [1.01, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | F (ROIN) | 0.108 | 1 | | |
| H=120 (4.00 LT) | deployable | X | 0.109 | 1.01 [0.993, 1.02] | negligible | 0.196 |
| H=120 (4.00 LT) | deployable | A3 (stored) | 0.111 | 1.03 [1.01, 1.04] | small | 0.006 |
| H=120 (4.00 LT) | deployable | X+F | 0.107 | 0.992 [0.981, 1] | negligible | 0.979 |

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| horizon | theory gap (upper bound) [CI] | estimation gap [CI] | gap with R estimated | gap with O estimated | gap with I estimated | gap with N estimated |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 1.13e-05 [1.05e-05, 1.21e-05] | 9.81e-06 [6.03e-06, 1.38e-05] | 5.51e-06 [1.92e-06, 9.28e-06] | -1.56e-06 [-4.96e-06, 1.98e-06] | -1.64e-06 [-5.1e-06, 1.89e-06] | 5.09e-08 [-3.3e-06, 3.64e-06] |
| H=15 (0.50 LT) | 1.82e-05 [1.67e-05, 1.98e-05] | 2.41e-05 [1.65e-05, 3.15e-05] | 1.63e-05 [8.69e-06, 2.4e-05] | 1.99e-06 [-4.91e-06, 8.89e-06] | 2.34e-06 [-4.47e-06, 9.18e-06] | 5.13e-06 [-1.74e-06, 1.21e-05] |
| H=30 (1.00 LT) | 5.22e-05 [4.8e-05, 5.67e-05] | 0.000102 [5.98e-05, 0.000145] | 7.6e-05 [3.65e-05, 0.000118] | -7.44e-07 [-3.38e-05, 3.79e-05] | -7.55e-07 [-3.41e-05, 3.7e-05] | 1.34e-05 [-2.18e-05, 5.31e-05] |
| H=60 (2.00 LT) | 0.00264 [0.00232, 0.00296] | 0.00164 [0.000786, 0.00252] | 0.0014 [0.000553, 0.00226] | 0.000552 [-0.000203, 0.00136] | 0.000475 [-0.000269, 0.00128] | 0.000536 [-0.000193, 0.00134] |
| H=120 (4.00 LT) | 0.0291 [0.0274, 0.0308] | 0.0019 [-0.0011, 0.00484] | 0.00207 [-0.000889, 0.00501] | 0.00126 [-0.00177, 0.0041] | 0.00131 [-0.00173, 0.00412] | 0.00108 [-0.00189, 0.00391] |

### Horizon decision (Y = ln min(T_c, H_max))

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED. Pinball loss at tau = 0.5; drop-one ratio at level 1 - 0.05/4; ladder ratio vs F at 1 - 0.05/m; C = Harrell's C (95%); coverage of q_0.1, q_0.5, q_0.9 and the 80% interval below the cap.

| profile | X | pinball ratio [CI] | reading | Holm p | phi [CI] |
|---|---|---|---|---|---|
| oracle | R | 1.01 [0.999, 1.02] | negligible | 0.027 | 0.00125 [0.000434, 0.00203] |
| oracle | O | 1.09 [1.06, 1.11] | substantial | 0.002 | 0.00839 [0.00695, 0.00993] |
| oracle | I | 1.24 [1.2, 1.28] | substantial | 0.002 | 0.0262 [0.0232, 0.0291] |
| oracle | N | 1 [0.991, 1.02] | negligible | 0.225 | 0.00165 [0.000696, 0.00257] |
| deployable | R | 1 [0.999, 1.01] | negligible | 0.057 | 0.0012 [0.000656, 0.00177] |
| deployable | O | 1.12 [1.1, 1.14] | substantial | 0.002 | 0.0145 [0.0127, 0.0164] |
| deployable | I | 1.24 [1.2, 1.28] | substantial | 0.002 | 0.0257 [0.023, 0.0284] |
| deployable | N | 1 [0.992, 1.01] | negligible | 0.51 | 0.000779 [0.000153, 0.0014] |

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | ratio vs F [CI] | reading | C [CI] | cov 0.1 / 0.5 / 0.9 / 80% |
|---|---|---|---|---|---|---|
| oracle | none | 0.16 | 1.3 [1.25, 1.35] | substantial | 0.5 [0.5, 0.5] | 0.102 / 0.505 / 0.899 / 0.798 |
| oracle | lyapunov | 0.172 | 1.4 [1.35, 1.45] | substantial | 0.637 [0.627, 0.648] | 0.0767 / 0.482 / 0.871 / 0.834 |
| oracle | RO | 0.154 | 1.26 [1.21, 1.3] | substantial | 0.566 [0.557, 0.576] | 0.101 / 0.503 / 0.903 / 0.803 |
| oracle | R | 0.16 | 1.3 [1.25, 1.35] | substantial | 0.524 [0.513, 0.534] | 0.102 / 0.508 / 0.904 / 0.802 |
| oracle | O | 0.155 | 1.26 [1.22, 1.3] | substantial | 0.564 [0.555, 0.574] | 0.102 / 0.506 / 0.905 / 0.803 |
| oracle | I | 0.138 | 1.12 [1.09, 1.15] | substantial | 0.626 [0.616, 0.636] | 0.102 / 0.498 / 0.897 / 0.795 |
| oracle | N | 0.158 | 1.28 [1.23, 1.33] | substantial | 0.534 [0.524, 0.544] | 0.102 / 0.505 / 0.9 / 0.798 |
| oracle | ROIN | 0.123 | 1 |  | 0.682 [0.672, 0.691] | 0.144 / 0.507 / 0.889 / 0.745 |
| oracle | X | 0.122 | 0.992 [0.953, 1.03] | negligible | 0.696 [0.689, 0.704] | 0.15 / 0.512 / 0.868 / 0.718 |
| oracle | X+F | 0.0951 | 0.773 [0.752, 0.794] | lowers | 0.765 [0.758, 0.772] | 0.149 / 0.508 / 0.852 / 0.703 |
| oracle | Lyapunov rank (C only) | | | | 0.635 [0.625, 0.646] | |
| deployable | none | 0.16 | 1.36 [1.3, 1.41] | substantial | 0.5 [0.5, 0.5] | 0.102 / 0.505 / 0.899 / 0.798 |
| deployable | lyapunov | 0.172 | 1.45 [1.4, 1.5] | substantial | 0.632 [0.622, 0.642] | 0.0786 / 0.482 / 0.874 / 0.835 |
| deployable | RO | 0.147 | 1.25 [1.21, 1.29] | substantial | 0.602 [0.593, 0.612] | 0.0997 / 0.506 / 0.899 / 0.799 |
| deployable | R | 0.159 | 1.35 [1.29, 1.39] | substantial | 0.528 [0.519, 0.536] | 0.0989 / 0.503 / 0.901 / 0.802 |
| deployable | O | 0.147 | 1.25 [1.21, 1.29] | substantial | 0.605 [0.596, 0.614] | 0.0991 / 0.508 / 0.9 / 0.801 |
| deployable | I | 0.138 | 1.17 [1.14, 1.2] | substantial | 0.627 [0.618, 0.636] | 0.0999 / 0.497 / 0.896 / 0.796 |
| deployable | N | 0.159 | 1.34 [1.29, 1.39] | substantial | 0.521 [0.513, 0.529] | 0.0993 / 0.507 / 0.9 / 0.8 |
| deployable | ROIN | 0.118 | 1 |  | 0.697 [0.688, 0.705] | 0.124 / 0.501 / 0.871 / 0.747 |
| deployable | X | 0.124 | 1.05 [1.01, 1.08] | needed, size not determined | 0.692 [0.684, 0.7] | 0.141 / 0.51 / 0.873 / 0.733 |
| deployable | X+F | 0.0919 | 0.778 [0.756, 0.798] | lowers | 0.769 [0.762, 0.776] | 0.142 / 0.504 / 0.858 / 0.716 |
| deployable | Lyapunov rank (C only) | | | | 0.63 [0.62, 0.64] | |

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| profile | pair | Delta [CI] | Holm p | detected |
|---|---|---|---|---|
| oracle | RO | 0.000223 [-0.000495, 0.000942] | 0.561 | False |
| oracle | RI (primary) | 0.000121 [-0.000907, 0.00121] | 0.794 | False |
| oracle | RN | 0.000217 [-0.000185, 0.000643] | 0.42 | False |
| oracle | OI (primary) | 0.00658 [0.00468, 0.00833] | 0.003 | True |
| oracle | ON | 0.000283 [-0.000453, 0.000938] | 0.56 | False |
| oracle | IN | -0.000144 [-0.00118, 0.000812] | 0.794 | False |
| deployable | RO | -5.76e-08 [-0.00014, 0.000145] | 1 | False |
| deployable | RI (primary) | 0.00214 [0.000847, 0.00341] | 0.003 | True |
| deployable | RN | 6.34e-05 [-0.0001, 0.000252] | 0.638 | False |
| deployable | OI (primary) | 0.0108 [0.00873, 0.0128] | 0.003 | True |
| deployable | ON | 0.00048 [-0.000796, 0.00174] | 0.638 | False |
| deployable | IN | -0.000279 [-0.00104, 0.000474] | 1 | False |

## chua

**PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.**

| check | result |
|---|---|
| (f1) state_mse from per-draw errors, max rel diff | A0 0.0e+00, A1 0.0e+00, A2 0.0e+00, A3 0.0e+00, A4 0.0e+00, A5 0.0e+00 (within 1e-12: True) |
| (g) WU-0039b (b1), (b2) rows reproduced | drop-N: True, all rows: True |
| separation formula on F-hat vs stored A4 at H_ref, max abs | 2.22e-16 |
| T_c: T = 1 / e_(T-1) = theta (train, test) | 1/0, 0/0 |
| (f2) dependence bias, deployable rows (reported, not gating) | 131 rows; 38 flagged: H=8 R: dependence bias detectable (interval excludes 0), t1+t2 / V 0.00713, z 1.55; H=8 N: dependence bias detectable (interval excludes 0), t1+t2 / V 0.011, z 1.92; H=8 RO: dependence bias detectable (interval excludes 0), t1+t2 / V 0.00811, z 1.05; H=8 RI: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0086, z 1.56; H=8 RN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0112, z 2; H=8 ON: dependence bias detectable (interval excludes 0), t1+t2 / V 0.00891, z 1.4; H=8 IN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0104, z 1.98; H=8 ROI: dependence bias detectable (interval excludes 0), t1+t2 / V 0.00875, z 1.22; H=8 RON: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0105, z 1.43; H=8 RIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0111, z 2.05; H=8 OIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0114, z 1.69; H=8 ROIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0118, z 1.62 ... |

### A. Allocation: drop-one and Shapley

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED. MSE ratio MSE(F without X)/MSE(F) at level 1 - 0.05/4 (reading by the 1.05 table, with the n_eff guard); excess ratio L_A(F without X)/L_A(F) and Holm p (Delta MSE > 0) are estimates. phi = Shapley share of L_A (95%). Oracle rows: moment form; deployable rows: realized per draw.

| horizon | profile | X | MSE ratio [CI] | reading | excess ratio | Holm p | phi_X [95% CI] | share |
|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | R | 1.01 [0.846, 1.16] | undetermined (n_eff < 50) | 1.06 | 1 | 1.86e-05 [-4.94e-06, 3.75e-05] | 0.48 |
| H=8 (0.27 LT) | oracle | O | 1.02 [0.823, 1.22] | undetermined (n_eff < 50) | 1.11 | 1 | 2.28e-05 [-2.47e-05, 7.16e-05] | 0.588 |
| H=8 (0.27 LT) | oracle | I | 0.987 [0.827, 1.13] | undetermined (n_eff < 50) | 0.936 | 1 | -6.16e-06 [-2.99e-05, 1.46e-05] | -0.159 |
| H=8 (0.27 LT) | oracle | N | 0.982 [0.838, 1.09] | undetermined (n_eff < 50) | 0.911 | 1 | 3.51e-06 [-1.8e-05, 1.84e-05] | 0.0906 |
| H=8 (0.27 LT) | deployable | R | 1.02 [0.999, 1.04] | undetermined (n_eff < 50) | 1.13 | 0.036 | 4.26e-06 [-1.33e-06, 1e-05] | -0.771 |
| H=8 (0.27 LT) | deployable | O | 0.994 [0.97, 1.01] | undetermined (n_eff < 50) | 0.944 | 1 | -5.36e-06 [-1.54e-05, 7.96e-07] | 0.97 |
| H=8 (0.27 LT) | deployable | I | 1 [0.996, 1.01] | undetermined (n_eff < 50) | 1.01 | 0.841 | 4.8e-07 [-3.77e-06, 5.26e-06] | -0.0868 |
| H=8 (0.27 LT) | deployable | N | 0.999 [0.993, 1] | undetermined (n_eff < 50) | 0.987 | 1 | -4.9e-06 [-1.4e-05, 9.89e-07] | 0.887 |
| H=15 (0.50 LT) | oracle | R | 1.01 [0.965, 1.05] | undetermined (n_eff < 50) | 1.03 | 1 | 3.5e-05 [-4.32e-05, 0.00011] | 0.343 |
| H=15 (0.50 LT) | oracle | O | 1.01 [1, 1.02] | undetermined (n_eff < 50) | 1.06 | 0.012 | 3.18e-05 [6.89e-06, 6.24e-05] | 0.311 |
| H=15 (0.50 LT) | oracle | I | 1 [0.981, 1.02] | undetermined (n_eff < 50) | 1.01 | 1 | 1.83e-05 [-1.5e-05, 5.26e-05] | 0.18 |
| H=15 (0.50 LT) | oracle | N | 0.997 [0.981, 1.01] | undetermined (n_eff < 50) | 0.985 | 1 | 1.69e-05 [-2.2e-05, 5.27e-05] | 0.166 |
| H=15 (0.50 LT) | deployable | R | 0.99 [0.961, 1.02] | undetermined (n_eff < 50) | 0.952 | 1 | -3.42e-05 [-0.000104, 3.51e-05] | 1.95 |
| H=15 (0.50 LT) | deployable | O | 1.01 [0.995, 1.02] | undetermined (n_eff < 50) | 1.03 | 0.328 | 1.84e-05 [-2.48e-06, 3.96e-05] | -1.05 |
| H=15 (0.50 LT) | deployable | I | 0.998 [0.991, 1.01] | undetermined (n_eff < 50) | 0.99 | 1 | -6.62e-06 [-1.96e-05, 5.98e-06] | 0.377 |
| H=15 (0.50 LT) | deployable | N | 1.01 [0.988, 1.02] | undetermined (n_eff < 50) | 1.02 | 0.676 | 4.8e-06 [-3.18e-05, 4.48e-05] | -0.274 |
| H=30 (1.00 LT) | oracle | R | 1.02 [1.01, 1.04] | undetermined (n_eff < 50) | 1.08 | 0.002 | 0.000552 [0.000378, 0.000749] | 0.851 |
| H=30 (1.00 LT) | oracle | O | 0.99 [0.966, 1.01] | undetermined (n_eff < 50) | 0.965 | 0.87 | -0.000237 [-0.000541, 9.58e-05] | -0.365 |
| H=30 (1.00 LT) | oracle | I | 1 [0.987, 1.02] | undetermined (n_eff < 50) | 1.01 | 0.633 | 0.000153 [-6.79e-05, 0.00037] | 0.236 |
| H=30 (1.00 LT) | oracle | N | 1.01 [0.995, 1.02] | undetermined (n_eff < 50) | 1.02 | 0.259 | 0.00018 [-3.44e-05, 0.000408] | 0.278 |
| H=30 (1.00 LT) | deployable | R | 1 [0.992, 1.01] | undetermined (n_eff < 50) | 1 | 0.949 | 8.99e-05 [-5.99e-05, 0.000271] | 0.211 |
| H=30 (1.00 LT) | deployable | O | 1.01 [0.982, 1.03] | undetermined (n_eff < 50) | 1.02 | 0.826 | 3.56e-05 [-0.000309, 0.000393] | 0.0834 |
| H=30 (1.00 LT) | deployable | I | 1.02 [1, 1.03] | undetermined (n_eff < 50) | 1.04 | 0.002 | 0.000312 [0.000152, 0.000482] | 0.732 |
| H=30 (1.00 LT) | deployable | N | 1 [0.986, 1.01] | undetermined (n_eff < 50) | 0.999 | 0.949 | -1.12e-05 [-0.000209, 0.00019] | -0.0262 |
| H=60 (2.00 LT) | oracle | R | 1.04 [1.02, 1.06] | needed, size not determined | 1.12 | 0.002 | 0.00895 [0.00638, 0.0115] | 0.951 |
| H=60 (2.00 LT) | oracle | O | 0.992 [0.969, 1.01] | negligible | 0.973 | 1 | 0.00048 [-0.00165, 0.00259] | 0.051 |
| H=60 (2.00 LT) | oracle | I | 0.989 [0.974, 1] | negligible | 0.963 | 1 | -0.000366 [-0.00144, 0.000692] | -0.0389 |
| H=60 (2.00 LT) | oracle | N | 0.989 [0.975, 1] | negligible | 0.963 | 1 | 0.000346 [-0.000674, 0.00135] | 0.0368 |
| H=60 (2.00 LT) | deployable | R | 1.01 [1, 1.02] | small | 1.03 | 0.002 | 0.00152 [0.000264, 0.00285] | 0.399 |
| H=60 (2.00 LT) | deployable | O | 1 [0.986, 1.02] | negligible | 1 | 0.49 | -0.000296 [-0.00265, 0.00197] | -0.0779 |
| H=60 (2.00 LT) | deployable | I | 1.01 [1, 1.01] | small | 1.02 | 0.002 | 0.00115 [0.000456, 0.00185] | 0.302 |
| H=60 (2.00 LT) | deployable | N | 1 [0.993, 1.02] | negligible | 1.01 | 0.315 | 0.00143 [0.000662, 0.00221] | 0.377 |
| H=120 (4.00 LT) | oracle | R | 1.01 [1.01, 1.02] | small | 1.04 | 0.002 | 0.00959 [0.0066, 0.0128] | 0.508 |
| H=120 (4.00 LT) | oracle | O | 1 [0.999, 1.01] | negligible | 1.01 | 0.053 | 0.00418 [0.0023, 0.00601] | 0.221 |
| H=120 (4.00 LT) | oracle | I | 1 [1, 1] | negligible | 1.01 | 0.0285 | 0.00351 [0.00231, 0.00485] | 0.186 |
| H=120 (4.00 LT) | oracle | N | 1 [1, 1] | negligible | 1 | 0.747 | 0.0016 [0.000183, 0.00289] | 0.0848 |
| H=120 (4.00 LT) | deployable | R | 1 [0.999, 1.01] | negligible | 1.01 | 0.053 | 0.00396 [0.0017, 0.00629] | 0.268 |
| H=120 (4.00 LT) | deployable | O | 1.01 [1, 1.01] | small | 1.02 | 0.003 | 0.00491 [0.00276, 0.00705] | 0.333 |
| H=120 (4.00 LT) | deployable | I | 1 [1, 1.01] | small | 1.01 | 0.002 | 0.0039 [0.0025, 0.00534] | 0.264 |
| H=120 (4.00 LT) | deployable | N | 1 [1, 1] | negligible | 1 | 1 | 0.002 [0.000868, 0.00312] | 0.135 |

### A. Allocation: summary per horizon

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED. n_eff = Kish size of kappa on the test states; G = 1 - L_A(rule)/L_A(constant), estimate (95%).

| horizon | profile | n_eff(kappa) | G(F) [CI] | G(separation) | MSE(F)/MSE(sep) [CI] | reading | settings (A) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 32.4 | 0.234 [-0.625, 0.583] | 0.455 | 1.06 [0.96, 1.23] | undetermined (n_eff < 50) | F: qn; qn 1, mid 5, low 9 |
| H=8 (0.27 LT) | deployable | 32.4 | -0.0953 [-0.578, 0.0569] | -1.14 | 0.903 [0.871, 0.94] | undetermined (n_eff < 50) | F: low; qn 0, mid 0, low 15 |
| H=15 (0.50 LT) | oracle | 80.3 | 0.168 [-0.00181, 0.318] | 0.323 | 1.04 [0.975, 1.12] | undetermined | F: low; qn 0, mid 1, low 14 |
| H=15 (0.50 LT) | deployable | 80.3 | -0.0319 [-0.256, 0.16] | -0.325 | 0.943 [0.921, 0.966] | undetermined (n_eff < 50) | F: low; qn 0, mid 0, low 15 |
| H=30 (1.00 LT) | oracle | 190 | 0.114 [0.0299, 0.21] | 0.185 | 1.02 [0.999, 1.05] | undetermined (n_eff < 50) | F: low; qn 0, mid 1, low 14 |
| H=30 (1.00 LT) | deployable | 190 | 0.0614 [-0.00394, 0.136] | 0.0279 | 0.988 [0.971, 1] | undetermined (n_eff < 50) | F: low; qn 0, mid 0, low 15 |
| H=60 (2.00 LT) | oracle | 843 | 0.141 [0.0757, 0.202] | 0.133 | 0.997 [0.974, 1.02] | negligible | F: mid; qn 0, mid 1, low 14 |
| H=60 (2.00 LT) | deployable | 843 | 0.0606 [0.0165, 0.102] | -0.0232 | 0.972 [0.958, 0.988] | lowers | F: low; qn 0, mid 2, low 13 |
| H=120 (4.00 LT) | oracle | 1.88e+03 | 0.1 [0.0795, 0.122] | -0.0431 | 0.958 [0.947, 0.969] | lowers | F: low; qn 0, mid 0, low 15 |
| H=120 (4.00 LT) | deployable | 1.88e+03 | 0.0759 [0.0576, 0.0959] | -0.116 | 0.943 [0.93, 0.956] | lowers | F: low; qn 0, mid 0, low 15 |

### B. Allocation: pairwise interactions (logit u, interior states)

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED. Delta = L(additive) - L(additive + pair) on the test states, models fixed; level 1 - 0.05/6; Holm over the six pairs. R x I and O x I are primary.

| horizon | profile | pair | Delta [CI] | Holm p | reading | loss ratio reading |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | RI (primary) | -0.0224 [-0.0489, 0.00462] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | OI (primary) | 0.015 [-0.0038, 0.0347] | 0.08 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | RO | 0.0251 [-0.0112, 0.0574] | 0.115 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | RN | 0.0296 [0.000291, 0.0615] | 0.0225 | interaction gain detected | small |
| H=8 (0.27 LT) | oracle | ON | 0.0338 [0.0034, 0.0664] | 0.015 | interaction gain detected | small |
| H=8 (0.27 LT) | oracle | IN | -0.00415 [-0.0184, 0.00985] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RI (primary) | -0.0192 [-0.0472, 0.00641] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | OI (primary) | 0.0154 [-0.0142, 0.0461] | 0.43 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RO | 0.0266 [-0.00647, 0.0592] | 0.09 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RN | -0.000506 [-0.0204, 0.0182] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | ON | 8.52e-05 [-0.0212, 0.0225] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | IN | -0.00262 [-0.0166, 0.0119] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | RI (primary) | -0.00264 [-0.0375, 0.0315] | 0.581 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | OI (primary) | 0.0257 [-0.00148, 0.0539] | 0.028 | interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | RO | 0.00915 [-0.0306, 0.05] | 0.527 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | RN | 0.0368 [0.0121, 0.0616] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | oracle | ON | 0.0449 [0.0142, 0.0794] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | oracle | IN | 0.00726 [-0.0108, 0.0263] | 0.511 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | RI (primary) | 0.0105 [-0.0139, 0.0326] | 0.343 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | OI (primary) | 0.0301 [0.00207, 0.0597] | 0.016 | interaction gain detected | small |
| H=15 (0.50 LT) | deployable | RO | 0.0518 [0.0198, 0.0839] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | deployable | RN | 0.0199 [0.00291, 0.0381] | 0.01 | interaction gain detected | small |
| H=15 (0.50 LT) | deployable | ON | 0.000619 [-0.0187, 0.0216] | 0.675 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | IN | 0.00233 [-0.0112, 0.0156] | 0.675 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | RI (primary) | 0.0471 [0.0103, 0.0914] | 0.003 | interaction gain detected | small |
| H=30 (1.00 LT) | oracle | OI (primary) | 0.0582 [0.0244, 0.0925] | 0.003 | interaction gain detected | small |
| H=30 (1.00 LT) | oracle | RO | 0.0526 [0.00937, 0.0939] | 0.008 | interaction gain detected | small |
| H=30 (1.00 LT) | oracle | RN | 0.0239 [0.00159, 0.0481] | 0.009 | interaction gain detected | small |
| H=30 (1.00 LT) | oracle | ON | 0.0313 [0.00209, 0.0592] | 0.009 | interaction gain detected | small |
| H=30 (1.00 LT) | oracle | IN | 0.022 [-0.00844, 0.0501] | 0.0215 | interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | RI (primary) | 0.00757 [-0.0221, 0.038] | 0.736 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | OI (primary) | 0.0258 [-0.00725, 0.0581] | 0.098 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | RO | 0.061 [0.0234, 0.0983] | 0.003 | interaction gain detected | small |
| H=30 (1.00 LT) | deployable | RN | 0.000127 [-0.0206, 0.0202] | 0.955 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | ON | 0.0128 [-0.00198, 0.0288] | 0.075 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | IN | -0.0119 [-0.0293, 0.00584] | 0.965 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | RI (primary) | 0.0485 [-0.0193, 0.115] | 0.053 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | OI (primary) | 0.0902 [0.0254, 0.151] | 0.006 | interaction gain detected | small |
| H=60 (2.00 LT) | oracle | RO | 0.0738 [0.0201, 0.129] | 0.006 | interaction gain detected | small |
| H=60 (2.00 LT) | oracle | RN | 0.0347 [0.00803, 0.0624] | 0.006 | interaction gain detected | small |
| H=60 (2.00 LT) | oracle | ON | 0.0339 [-0.00481, 0.0736] | 0.0375 | interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | IN | 0.00913 [-0.0344, 0.0553] | 0.3 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | RI (primary) | 0.0117 [-0.0344, 0.0542] | 0.516 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | OI (primary) | 0.0861 [0.0289, 0.14] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | RO | 0.0457 [0.00246, 0.0888] | 0.0175 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | RN | 0.0288 [-0.000303, 0.0575] | 0.022 | interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | ON | 0.0186 [-0.0131, 0.0513] | 0.205 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | IN | 0.00175 [-0.0325, 0.0361] | 0.516 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RI (primary) | 0.00298 [-0.0327, 0.0403] | 0.427 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | OI (primary) | 0.0117 [-0.021, 0.0515] | 0.392 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RO | 0.0928 [0.0369, 0.148] | 0.003 | interaction gain detected | small |
| H=120 (4.00 LT) | oracle | RN | 0.0185 [-0.0146, 0.054] | 0.304 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | ON | 0.0361 [-0.00227, 0.0778] | 0.04 | interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | IN | 0.0136 [-0.0171, 0.0463] | 0.349 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RI (primary) | -0.0179 [-0.0375, 0.00128] | 0.994 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | OI (primary) | 0.0191 [-0.0163, 0.056] | 0.31 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RO | 0.0132 [-0.0204, 0.0465] | 0.423 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RN | 0.0207 [-0.00806, 0.0519] | 0.192 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | ON | 0.0147 [-0.00934, 0.0408] | 0.275 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | IN | 0.00729 [-0.0107, 0.0263] | 0.423 | no interaction gain detected | negligible |

### D. Allocation ladder (rung against the full profile)

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED. MSE ratio MSE(rung)/MSE(F) at level 1 - 0.05/m (m rungs); Holm p for Delta MSE > 0. Theory gap L_A(oracle F) is an upper bound; estimation gap = L_A(deployable F) - L_A(oracle F) (95%).

| horizon | profile | rung | MSE | MSE ratio vs F [CI] | reading | Holm p |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | none | 0.000668 | 1.06 [0.831, 1.28] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | separation | 0.000593 | 0.942 [0.757, 1.05] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | RO | 0.000614 | 0.976 [0.825, 1.11] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | R | 0.000648 | 1.03 [0.808, 1.24] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | O | 0.000645 | 1.03 [0.859, 1.17] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | I | 0.000681 | 1.08 [0.855, 1.27] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | N | 0.000657 | 1.04 [0.816, 1.25] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | F (ROIN) | 0.000629 | 1 | | |
| H=8 (0.27 LT) | oracle | X | 0.000626 | 0.995 [0.821, 1.09] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | X+F | 0.000634 | 1.01 [0.959, 1.07] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | none | 0.00056 | 0.99 [0.954, 1.01] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | A2 (stored) | 0.00056 | 0.99 [0.953, 1.01] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | separation | 0.000626 | 1.11 [1.05, 1.17] | undetermined (n_eff < 50) | 0.006 |
| H=8 (0.27 LT) | deployable | A4 (stored) | 0.000626 | 1.11 [1.05, 1.17] | undetermined (n_eff < 50) | 0.006 |
| H=8 (0.27 LT) | deployable | RO | 0.000567 | 1 [0.993, 1.01] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | R | 0.000562 | 0.993 [0.962, 1.01] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | O | 0.00057 | 1.01 [0.991, 1.02] | undetermined (n_eff < 50) | 0.873 |
| H=8 (0.27 LT) | deployable | I | 0.000564 | 0.998 [0.961, 1.02] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | N | 0.000573 | 1.01 [0.99, 1.06] | undetermined (n_eff < 50) | 0.873 |
| H=8 (0.27 LT) | deployable | F (ROIN) | 0.000566 | 1 | | |
| H=8 (0.27 LT) | deployable | X | 0.000569 | 1.01 [0.954, 1.05] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | A3 (stored) | 0.000636 | 1.12 [1.05, 1.24] | undetermined (n_eff < 50) | 0.006 |
| H=8 (0.27 LT) | deployable | X+F | 0.000562 | 0.993 [0.972, 1.01] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | oracle | none | 0.00272 | 1.04 [0.98, 1.09] | undetermined (n_eff < 50) | 0.247 |
| H=15 (0.50 LT) | oracle | separation | 0.00252 | 0.964 [0.854, 1.04] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | oracle | RO | 0.0026 | 0.992 [0.962, 1.01] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | oracle | R | 0.00266 | 1.01 [0.987, 1.04] | undetermined (n_eff < 50) | 0.568 |
| H=15 (0.50 LT) | oracle | O | 0.00268 | 1.02 [0.971, 1.08] | undetermined (n_eff < 50) | 0.605 |
| H=15 (0.50 LT) | oracle | I | 0.00268 | 1.02 [0.969, 1.08] | undetermined (n_eff < 50) | 0.605 |
| H=15 (0.50 LT) | oracle | N | 0.00266 | 1.02 [0.969, 1.06] | undetermined (n_eff < 50) | 0.605 |
| H=15 (0.50 LT) | oracle | F (ROIN) | 0.00262 | 1 | | |
| H=15 (0.50 LT) | oracle | X | 0.00269 | 1.03 [0.968, 1.08] | undetermined (n_eff < 50) | 0.605 |
| H=15 (0.50 LT) | oracle | X+F | 0.00261 | 0.998 [0.99, 1.01] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | none | 0.00266 | 0.993 [0.952, 1.04] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | A2 (stored) | 0.00266 | 0.994 [0.953, 1.04] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | separation | 0.00284 | 1.06 [1.02, 1.1] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | A4 (stored) | 0.00284 | 1.06 [1.02, 1.1] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | RO | 0.00269 | 1 [0.982, 1.03] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | R | 0.00271 | 1.01 [0.988, 1.04] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | O | 0.00265 | 0.987 [0.944, 1.03] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | I | 0.00267 | 0.997 [0.955, 1.05] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | N | 0.00268 | 0.998 [0.965, 1.04] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | F (ROIN) | 0.00268 | 1 | | |
| H=15 (0.50 LT) | deployable | X | 0.00264 | 0.986 [0.941, 1.04] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | A3 (stored) | 0.00278 | 1.04 [0.978, 1.1] | undetermined (n_eff < 50) | 0.415 |
| H=15 (0.50 LT) | deployable | X+F | 0.00265 | 0.989 [0.961, 1.02] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | none | 0.0184 | 1.04 [0.997, 1.09] | undetermined (n_eff < 50) | 0.052 |
| H=30 (1.00 LT) | oracle | separation | 0.0173 | 0.977 [0.939, 1.01] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | RO | 0.0178 | 1 [0.984, 1.03] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | R | 0.0177 | 0.996 [0.961, 1.04] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | O | 0.0187 | 1.05 [1.02, 1.09] | undetermined (n_eff < 50) | 0.0045 |
| H=30 (1.00 LT) | oracle | I | 0.0181 | 1.02 [0.981, 1.06] | undetermined (n_eff < 50) | 0.56 |
| H=30 (1.00 LT) | oracle | N | 0.0181 | 1.02 [0.985, 1.06] | undetermined (n_eff < 50) | 0.249 |
| H=30 (1.00 LT) | oracle | F (ROIN) | 0.0177 | 1 | | |
| H=30 (1.00 LT) | oracle | X | 0.0182 | 1.03 [0.993, 1.07] | undetermined (n_eff < 50) | 0.108 |
| H=30 (1.00 LT) | oracle | X+F | 0.0178 | 1 [0.987, 1.02] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | deployable | none | 0.0196 | 1.02 [0.987, 1.07] | undetermined (n_eff < 50) | 0.31 |
| H=30 (1.00 LT) | deployable | A2 (stored) | 0.0196 | 1.02 [0.986, 1.07] | undetermined (n_eff < 50) | 0.31 |
| H=30 (1.00 LT) | deployable | separation | 0.0194 | 1.01 [0.99, 1.04] | undetermined (n_eff < 50) | 0.535 |
| H=30 (1.00 LT) | deployable | A4 (stored) | 0.0194 | 1.01 [0.99, 1.04] | undetermined (n_eff < 50) | 0.535 |
| H=30 (1.00 LT) | deployable | RO | 0.0194 | 1.01 [0.994, 1.03] | undetermined (n_eff < 50) | 0.236 |
| H=30 (1.00 LT) | deployable | R | 0.0194 | 1.01 [0.981, 1.05] | undetermined (n_eff < 50) | 0.587 |
| H=30 (1.00 LT) | deployable | O | 0.0197 | 1.02 [0.999, 1.06] | undetermined (n_eff < 50) | 0.048 |
| H=30 (1.00 LT) | deployable | I | 0.0193 | 1 [0.973, 1.05] | undetermined (n_eff < 50) | 0.772 |
| H=30 (1.00 LT) | deployable | N | 0.0196 | 1.02 [0.993, 1.06] | undetermined (n_eff < 50) | 0.255 |
| H=30 (1.00 LT) | deployable | A5 (stored) | 0.0194 | 1.01 [0.983, 1.06] | undetermined (n_eff < 50) | 0.587 |
| H=30 (1.00 LT) | deployable | F (ROIN) | 0.0192 | 1 | | |
| H=30 (1.00 LT) | deployable | X | 0.0195 | 1.01 [0.983, 1.06] | undetermined (n_eff < 50) | 0.587 |
| H=30 (1.00 LT) | deployable | A3 (stored) | 0.0199 | 1.04 [1, 1.09] | undetermined (n_eff < 50) | 0.0065 |
| H=30 (1.00 LT) | deployable | X+F | 0.0191 | 0.996 [0.979, 1.02] | undetermined (n_eff < 50) | 0.772 |
| H=60 (2.00 LT) | oracle | none | 0.193 | 1.05 [1.01, 1.09] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | separation | 0.184 | 1 [0.971, 1.04] | negligible | 1 |
| H=60 (2.00 LT) | oracle | RO | 0.181 | 0.987 [0.969, 1] | negligible | 1 |
| H=60 (2.00 LT) | oracle | R | 0.183 | 0.998 [0.968, 1.03] | negligible | 1 |
| H=60 (2.00 LT) | oracle | O | 0.191 | 1.04 [1.01, 1.07] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | I | 0.193 | 1.05 [1.01, 1.09] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | N | 0.191 | 1.04 [1.01, 1.07] | needed, size not determined | 0.005 |
| H=60 (2.00 LT) | oracle | F (ROIN) | 0.183 | 1 | | |
| H=60 (2.00 LT) | oracle | X | 0.191 | 1.04 [1.01, 1.07] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | X+F | 0.182 | 0.992 [0.976, 1.01] | negligible | 1 |
| H=60 (2.00 LT) | deployable | none | 0.189 | 1.02 [1, 1.04] | negligible | 0.0245 |
| H=60 (2.00 LT) | deployable | A2 (stored) | 0.189 | 1.02 [1, 1.04] | small | 0.02 |
| H=60 (2.00 LT) | deployable | separation | 0.19 | 1.03 [1, 1.05] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | A4 (stored) | 0.19 | 1.03 [1, 1.05] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | RO | 0.188 | 1.02 [1.01, 1.03] | small | 0.006 |
| H=60 (2.00 LT) | deployable | R | 0.187 | 1.01 [0.992, 1.03] | negligible | 0.304 |
| H=60 (2.00 LT) | deployable | O | 0.189 | 1.02 [1.01, 1.03] | small | 0.006 |
| H=60 (2.00 LT) | deployable | I | 0.188 | 1.01 [0.992, 1.03] | negligible | 0.222 |
| H=60 (2.00 LT) | deployable | N | 0.186 | 1.01 [0.989, 1.02] | negligible | 0.412 |
| H=60 (2.00 LT) | deployable | F (ROIN) | 0.185 | 1 | | |
| H=60 (2.00 LT) | deployable | X | 0.187 | 1.01 [0.993, 1.03] | negligible | 0.292 |
| H=60 (2.00 LT) | deployable | A3 (stored) | 0.187 | 1.01 [0.983, 1.04] | negligible | 0.412 |
| H=60 (2.00 LT) | deployable | X+F | 0.185 | 1 [0.993, 1.01] | negligible | 0.506 |
| H=120 (4.00 LT) | oracle | none | 0.63 | 1.03 [1.02, 1.04] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | separation | 0.639 | 1.04 [1.03, 1.06] | needed, size not determined | 0.0045 |
| H=120 (4.00 LT) | oracle | RO | 0.613 | 1 [0.999, 1] | negligible | 0.03 |
| H=120 (4.00 LT) | oracle | R | 0.618 | 1.01 [1.01, 1.02] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | O | 0.624 | 1.02 [1.01, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | I | 0.624 | 1.02 [1.01, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | N | 0.626 | 1.02 [1.02, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | F (ROIN) | 0.612 | 1 | | |
| H=120 (4.00 LT) | oracle | X | 0.627 | 1.03 [1.02, 1.04] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | X+F | 0.612 | 1 [0.998, 1] | negligible | 0.196 |
| H=120 (4.00 LT) | deployable | none | 0.636 | 1.02 [1.02, 1.03] | small | 0.006 |
| H=120 (4.00 LT) | deployable | A2 (stored) | 0.637 | 1.02 [1.02, 1.03] | small | 0.006 |
| H=120 (4.00 LT) | deployable | separation | 0.659 | 1.06 [1.04, 1.08] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | A4 (stored) | 0.659 | 1.06 [1.04, 1.08] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | RO | 0.624 | 1 [1, 1.01] | small | 0.006 |
| H=120 (4.00 LT) | deployable | R | 0.63 | 1.01 [1.01, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | O | 0.629 | 1.01 [1, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | I | 0.629 | 1.01 [1, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | N | 0.631 | 1.02 [1.01, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | F (ROIN) | 0.621 | 1 | | |
| H=120 (4.00 LT) | deployable | X | 0.633 | 1.02 [1.01, 1.03] | small | 0.006 |
| H=120 (4.00 LT) | deployable | A3 (stored) | 0.642 | 1.03 [1.01, 1.05] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | X+F | 0.623 | 1 [0.999, 1.01] | negligible | 0.029 |

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| horizon | theory gap (upper bound) [CI] | estimation gap [CI] | gap with R estimated | gap with O estimated | gap with I estimated | gap with N estimated |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 0.000127 [5.47e-05, 0.000231] | -6.35e-05 [-0.000174, 2.41e-05] | -1.48e-05 [-9.06e-05, 6.74e-05] | -8.93e-05 [-0.000199, -2.02e-06] | -8.52e-05 [-0.000166, -1.62e-05] | -7.33e-05 [-0.000168, 1.85e-06] |
| H=15 (0.50 LT) | 0.000507 [0.00033, 0.000738] | 6.13e-05 [-0.000322, 0.000495] | 8.75e-06 [-0.000366, 0.000416] | 5.77e-05 [-0.000316, 0.000483] | 2.79e-05 [-0.000346, 0.000448] | 1.92e-05 [-0.000368, 0.000456] |
| H=30 (1.00 LT) | 0.00506 [0.00359, 0.00677] | 0.00146 [-0.00122, 0.00442] | 0.00151 [-0.00109, 0.00441] | 0.00103 [-0.00151, 0.00392] | 0.00102 [-0.00148, 0.00392] | 0.00127 [-0.0013, 0.00411] |
| H=60 (2.00 LT) | 0.0571 [0.0512, 0.0631] | 0.0018 [-0.00758, 0.0115] | 0.00297 [-0.00647, 0.0127] | -0.00595 [-0.0149, 0.00337] | -0.0041 [-0.0133, 0.00516] | -0.0054 [-0.0143, 0.00381] |
| H=120 (4.00 LT) | 0.17 [0.162, 0.178] | 0.00987 [-0.00472, 0.0244] | 0.00894 [-0.00534, 0.0233] | 0.00308 [-0.0112, 0.0179] | 0.00303 [-0.0112, 0.0176] | 0.00307 [-0.0112, 0.0176] |

### Horizon decision (Y = ln min(T_c, H_max))

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED. Pinball loss at tau = 0.5; drop-one ratio at level 1 - 0.05/4; ladder ratio vs F at 1 - 0.05/m; C = Harrell's C (95%); coverage of q_0.1, q_0.5, q_0.9 and the 80% interval below the cap.

| profile | X | pinball ratio [CI] | reading | Holm p | phi [CI] |
|---|---|---|---|---|---|
| oracle | R | 1.02 [1.01, 1.03] | small | 0.002 | 0.00192 [0.00116, 0.00264] |
| oracle | O | 1.05 [1.04, 1.07] | needed, size not determined | 0.002 | 0.0143 [0.0121, 0.0163] |
| oracle | I | 1.23 [1.19, 1.27] | substantial | 0.002 | 0.0427 [0.038, 0.0469] |
| oracle | N | 0.997 [0.99, 1] | negligible | 0.873 | 0.00134 [0.000631, 0.00202] |
| deployable | R | 1.01 [1, 1.01] | small | 0.002 | 0.00121 [0.000727, 0.00168] |
| deployable | O | 1.08 [1.07, 1.1] | substantial | 0.002 | 0.0186 [0.0165, 0.0205] |
| deployable | I | 1.22 [1.19, 1.26] | substantial | 0.002 | 0.0413 [0.0372, 0.045] |
| deployable | N | 0.998 [0.993, 1] | negligible | 0.788 | 0.0016 [0.00109, 0.0021] |

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | ratio vs F [CI] | reading | C [CI] | cov 0.1 / 0.5 / 0.9 / 80% |
|---|---|---|---|---|---|---|
| oracle | none | 0.224 | 1.37 [1.31, 1.42] | substantial | 0.5 [0.5, 0.5] | 0.0978 / 0.503 / 0.891 / 0.793 |
| oracle | lyapunov | 0.261 | 1.59 [1.53, 1.66] | substantial | 0.672 [0.663, 0.681] | 0.0878 / 0.446 / 0.843 / 0.811 |
| oracle | RO | 0.203 | 1.24 [1.2, 1.28] | substantial | 0.625 [0.615, 0.635] | 0.106 / 0.504 / 0.884 / 0.778 |
| oracle | R | 0.223 | 1.36 [1.3, 1.4] | substantial | 0.527 [0.516, 0.537] | 0.108 / 0.511 / 0.886 / 0.778 |
| oracle | O | 0.203 | 1.24 [1.2, 1.28] | substantial | 0.624 [0.614, 0.633] | 0.106 / 0.507 / 0.891 / 0.785 |
| oracle | I | 0.175 | 1.07 [1.04, 1.09] | needed, size not determined | 0.682 [0.673, 0.691] | 0.107 / 0.502 / 0.886 / 0.779 |
| oracle | N | 0.22 | 1.34 [1.29, 1.39] | substantial | 0.556 [0.546, 0.567] | 0.0985 / 0.505 / 0.886 / 0.787 |
| oracle | ROIN | 0.164 | 1 |  | 0.704 [0.694, 0.713] | 0.119 / 0.502 / 0.883 / 0.764 |
| oracle | X | 0.173 | 1.05 [1.01, 1.09] | needed, size not determined | 0.696 [0.686, 0.705] | 0.145 / 0.484 / 0.85 / 0.705 |
| oracle | X+F | 0.138 | 0.839 [0.82, 0.859] | lowers | 0.764 [0.755, 0.771] | 0.163 / 0.488 / 0.835 / 0.672 |
| oracle | Lyapunov rank (C only) | | | | 0.664 [0.655, 0.673] | |
| deployable | none | 0.224 | 1.39 [1.34, 1.43] | substantial | 0.5 [0.5, 0.5] | 0.0978 / 0.503 / 0.891 / 0.793 |
| deployable | lyapunov | 0.26 | 1.61 [1.54, 1.67] | substantial | 0.67 [0.662, 0.679] | 0.0836 / 0.453 / 0.844 / 0.812 |
| deployable | RO | 0.198 | 1.22 [1.19, 1.26] | substantial | 0.634 [0.623, 0.644] | 0.11 / 0.501 / 0.894 / 0.784 |
| deployable | R | 0.223 | 1.38 [1.33, 1.42] | substantial | 0.529 [0.522, 0.536] | 0.102 / 0.51 / 0.887 / 0.785 |
| deployable | O | 0.201 | 1.24 [1.2, 1.27] | substantial | 0.627 [0.617, 0.637] | 0.103 / 0.502 / 0.891 / 0.788 |
| deployable | I | 0.177 | 1.09 [1.07, 1.11] | substantial | 0.68 [0.671, 0.688] | 0.108 / 0.507 / 0.888 / 0.78 |
| deployable | N | 0.221 | 1.36 [1.32, 1.41] | substantial | 0.552 [0.545, 0.561] | 0.0958 / 0.508 / 0.89 / 0.794 |
| deployable | ROIN | 0.162 | 1 |  | 0.712 [0.703, 0.72] | 0.133 / 0.504 / 0.885 / 0.752 |
| deployable | X | 0.173 | 1.07 [1.03, 1.11] | needed, size not determined | 0.697 [0.688, 0.706] | 0.14 / 0.479 / 0.858 / 0.718 |
| deployable | X+F | 0.139 | 0.859 [0.839, 0.88] | lowers | 0.762 [0.754, 0.769] | 0.146 / 0.498 / 0.851 / 0.705 |
| deployable | Lyapunov rank (C only) | | | | 0.661 [0.651, 0.669] | |

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| profile | pair | Delta [CI] | Holm p | detected |
|---|---|---|---|---|
| oracle | RO | 0.000842 [-0.00132, 0.00299] | 0.483 | False |
| oracle | RI (primary) | 0.00126 [-0.0011, 0.00358] | 0.37 | False |
| oracle | RN | -0.000541 [-0.00243, 0.00141] | 1 | False |
| oracle | OI (primary) | 0.00522 [0.00281, 0.00752] | 0.003 | True |
| oracle | ON | 0.000828 [4.24e-06, 0.00159] | 0.0225 | True |
| oracle | IN | -0.00025 [-0.00106, 0.000457] | 1 | False |
| deployable | RO | 0.000507 [-0.000389, 0.00145] | 0.26 | False |
| deployable | RI (primary) | 0.000564 [-0.000406, 0.00166] | 0.26 | False |
| deployable | RN | -0.000622 [-0.00184, 0.000625] | 1 | False |
| deployable | OI (primary) | 0.00845 [0.00648, 0.0105] | 0.003 | True |
| deployable | ON | -0.000313 [-0.00155, 0.000906] | 1 | False |
| deployable | IN | 0.000538 [-0.000373, 0.00144] | 0.26 | False |

