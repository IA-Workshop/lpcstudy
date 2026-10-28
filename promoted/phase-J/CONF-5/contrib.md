# Phase J contribution study: CONF-5

**PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.** Run `phasej-CONF-5/phasej`; analysis commit `c19ad486b93a2ee96d64ce069ec42fd440428211` (dirty: False). Every reading is an estimate; Shapley shares and interactions are predictive, not causal. Training variance is not in the intervals.

## lorenz63

**PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.**

| check | result |
|---|---|
| (f1) state_mse from per-draw errors, max rel diff | A0 0.0e+00, A1 0.0e+00, A2 0.0e+00, A3 0.0e+00, A4 0.0e+00, A5 0.0e+00 (within 1e-12: True) |
| (g) WU-0039b (b1), (b2) rows reproduced | drop-N: True, all rows: True |
| separation formula on F-hat vs stored A4 at H_ref, max abs | 1.67e-16 |
| T_c: T = 1 / e_(T-1) = theta (train, test) | 7/0, 12/0 |
| (f2) dependence bias, deployable rows (reported, not gating) | 131 rows; 36 flagged: H=8 R: dependence bias detectable (interval excludes 0), t1+t2 / V -0.0237, z -0.0441; H=8 I: dependence bias detectable (interval excludes 0), t1+t2 / V 0.227, z 2.1; H=8 RI: dependence bias detectable (interval excludes 0), t1+t2 / V 0.233, z 1.84; H=8 OI: dependence bias detectable (interval excludes 0), t1+t2 / V 0.126, z 0.752; H=8 IN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.189, z 1.68; H=8 ROI: dependence bias detectable (interval excludes 0), t1+t2 / V 0.122, z 0.743; H=8 RIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.126, z 1.13; H=8 OIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.12, z 1.1; H=8 ROIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.109, z 0.911; H=8 swap-R: dependence bias detectable (interval excludes 0), t1+t2 / V 0.00174, z 0.143; H=8 swap-I: dependence bias detectable (interval excludes 0), t1+t2 / V 0.00646, z 0.158; H=8 swap-N: dependence bias detectable (interval excludes 0), t1+t2 / V 0.00127, z 0.141 ... |

### A. Allocation: drop-one and Shapley

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED. MSE ratio MSE(F without X)/MSE(F) at level 1 - 0.05/4 (reading by the 1.05 table, with the n_eff guard); excess ratio L_A(F without X)/L_A(F) and Holm p (Delta MSE > 0) are estimates. phi = Shapley share of L_A (95%). Oracle rows: moment form; deployable rows: realized per draw.

| horizon | profile | X | MSE ratio [CI] | reading | excess ratio | Holm p | phi_X [95% CI] | share |
|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | R | 1.02 [1.01, 1.25] | undetermined (n_eff < 50) | 1.04 | 0.002 | -0.000601 [-0.00143, 0.000138] | -0.0567 |
| H=8 (0.27 LT) | oracle | O | 2.65 [1.29, 17.4] | undetermined (n_eff < 50) | 3.55 | 0.002 | 0.00821 [0.00428, 0.0125] | 0.774 |
| H=8 (0.27 LT) | oracle | I | 1 [0.994, 1.08] | undetermined (n_eff < 50) | 1.01 | 0.434 | 0.00337 [0.00212, 0.0047] | 0.318 |
| H=8 (0.27 LT) | oracle | N | 0.997 [0.989, 1.01] | undetermined (n_eff < 50) | 0.995 | 0.898 | -0.000373 [-0.00214, 0.00103] | -0.0352 |
| H=8 (0.27 LT) | deployable | R | 1.11 [1.02, 1.22] | undetermined (n_eff < 50) | 1.13 | 0.006 | 0.00116 [0.000288, 0.00216] | 0.274 |
| H=8 (0.27 LT) | deployable | O | 1.17 [0.95, 1.67] | undetermined (n_eff < 50) | 1.21 | 0.109 | 0.0025 [0.000451, 0.00454] | 0.588 |
| H=8 (0.27 LT) | deployable | I | 1.05 [0.894, 1.28] | undetermined (n_eff < 50) | 1.05 | 0.46 | 0.000517 [-0.00185, 0.00258] | 0.122 |
| H=8 (0.27 LT) | deployable | N | 0.943 [0.721, 1.18] | undetermined (n_eff < 50) | 0.933 | 0.704 | 6.66e-05 [-0.00156, 0.00152] | 0.0157 |
| H=15 (0.50 LT) | oracle | R | 1.11 [1.02, 1.24] | undetermined (n_eff < 50) | 1.63 | 0.003 | 0.00176 [0.000703, 0.00287] | 0.093 |
| H=15 (0.50 LT) | oracle | O | 1.68 [1.39, 2.12] | undetermined (n_eff < 50) | 5.01 | 0.002 | 0.0111 [0.00903, 0.0135] | 0.587 |
| H=15 (0.50 LT) | oracle | I | 1.06 [0.972, 1.17] | undetermined (n_eff < 50) | 1.36 | 0.136 | 0.00436 [0.003, 0.00578] | 0.23 |
| H=15 (0.50 LT) | oracle | N | 1.01 [0.995, 1.02] | undetermined (n_eff < 50) | 1.04 | 0.136 | 0.0017 [0.000351, 0.00292] | 0.0897 |
| H=15 (0.50 LT) | deployable | R | 1.22 [0.997, 1.53] | undetermined (n_eff < 50) | 1.36 | 0.034 | 0.00438 [0.00208, 0.00685] | 0.417 |
| H=15 (0.50 LT) | deployable | O | 1.02 [0.838, 1.24] | undetermined (n_eff < 50) | 1.03 | 0.533 | 0.000858 [-0.00111, 0.00272] | 0.0816 |
| H=15 (0.50 LT) | deployable | I | 1.09 [0.853, 1.51] | undetermined (n_eff < 50) | 1.15 | 0.533 | 0.00292 [0.000577, 0.0055] | 0.278 |
| H=15 (0.50 LT) | deployable | N | 1.13 [0.992, 1.28] | undetermined (n_eff < 50) | 1.2 | 0.034 | 0.00235 [-0.000211, 0.00505] | 0.223 |
| H=30 (1.00 LT) | oracle | R | 1.17 [1.08, 1.32] | undetermined (n_eff < 50) | 1.7 | 0.002 | 0.00137 [-0.000158, 0.00286] | 0.059 |
| H=30 (1.00 LT) | oracle | O | 1.13 [1, 1.29] | undetermined (n_eff < 50) | 1.53 | 0.0065 | 0.00915 [0.00542, 0.0127] | 0.396 |
| H=30 (1.00 LT) | oracle | I | 1.21 [1.11, 1.36] | undetermined (n_eff < 50) | 1.85 | 0.002 | 0.00893 [0.00704, 0.011] | 0.386 |
| H=30 (1.00 LT) | oracle | N | 1.12 [1.04, 1.23] | undetermined (n_eff < 50) | 1.47 | 0.002 | 0.00369 [0.00242, 0.00509] | 0.159 |
| H=30 (1.00 LT) | deployable | R | 1.06 [1, 1.13] | undetermined (n_eff < 50) | 1.12 | 0.016 | 0.00452 [0.00255, 0.00641] | 0.393 |
| H=30 (1.00 LT) | deployable | O | 1 [0.916, 1.09] | undetermined (n_eff < 50) | 1.01 | 0.554 | -0.00119 [-0.00394, 0.00161] | -0.104 |
| H=30 (1.00 LT) | deployable | I | 1.15 [1.01, 1.32] | undetermined (n_eff < 50) | 1.32 | 0.016 | 0.00688 [0.00312, 0.0105] | 0.598 |
| H=30 (1.00 LT) | deployable | N | 1.02 [0.94, 1.14] | undetermined (n_eff < 50) | 1.05 | 0.554 | 0.0013 [-0.00149, 0.00381] | 0.113 |
| H=60 (2.00 LT) | oracle | R | 1.04 [1.02, 1.08] | needed, size not determined | 1.14 | 0.002 | 0.00354 [0.00161, 0.00564] | 0.185 |
| H=60 (2.00 LT) | oracle | O | 1.07 [0.993, 1.14] | undetermined | 1.23 | 0.023 | 0.0102 [0.00209, 0.0165] | 0.536 |
| H=60 (2.00 LT) | oracle | I | 1.03 [1.01, 1.04] | small | 1.09 | 0.002 | 0.00298 [0.00181, 0.00423] | 0.156 |
| H=60 (2.00 LT) | oracle | N | 1.01 [0.991, 1.03] | negligible | 1.02 | 0.123 | 0.00236 [0.000294, 0.00443] | 0.123 |
| H=60 (2.00 LT) | deployable | R | 1 [0.985, 1.02] | negligible | 1.01 | 0.694 | 0.000243 [-0.00153, 0.00214] | 0.0332 |
| H=60 (2.00 LT) | deployable | O | 1.02 [0.994, 1.04] | negligible | 1.04 | 0.0975 | 0.00194 [6.86e-05, 0.0038] | 0.265 |
| H=60 (2.00 LT) | deployable | I | 1.04 [1.01, 1.06] | needed, size not determined | 1.1 | 0.002 | 0.00379 [0.00201, 0.00569] | 0.519 |
| H=60 (2.00 LT) | deployable | N | 1 [0.98, 1.02] | negligible | 1 | 0.694 | 0.00134 [-0.000735, 0.00337] | 0.183 |
| H=120 (4.00 LT) | oracle | R | 1.01 [0.999, 1.02] | negligible | 1.03 | 0.0435 | 0.00608 [0.000974, 0.0111] | 0.502 |
| H=120 (4.00 LT) | oracle | O | 1.01 [0.999, 1.02] | negligible | 1.03 | 0.0435 | 0.0048 [-0.000403, 0.00999] | 0.397 |
| H=120 (4.00 LT) | oracle | I | 1.01 [1, 1.01] | small | 1.02 | 0.018 | 0.00204 [-0.000195, 0.00416] | 0.168 |
| H=120 (4.00 LT) | oracle | N | 1 [0.996, 1.01] | negligible | 1 | 0.37 | -0.000802 [-0.00305, 0.0016] | -0.0662 |
| H=120 (4.00 LT) | deployable | R | 1 [0.997, 1.01] | negligible | 1.01 | 0.386 | 0.00309 [-1.74e-05, 0.00605] | 0.817 |
| H=120 (4.00 LT) | deployable | O | 0.999 [0.996, 1] | negligible | 0.995 | 1 | -0.000916 [-0.00344, 0.00161] | -0.242 |
| H=120 (4.00 LT) | deployable | I | 1 [0.998, 1] | negligible | 1.01 | 0.386 | 0.00128 [-0.000983, 0.00342] | 0.338 |
| H=120 (4.00 LT) | deployable | N | 1 [1, 1] | negligible | 1 | 1 | 0.00033 [-0.000517, 0.0012] | 0.0874 |

### A. Allocation: summary per horizon

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED. n_eff = Kish size of kappa on the test states; G = 1 - L_A(rule)/L_A(constant), estimate (95%).

| horizon | profile | n_eff(kappa) | G(F) [CI] | G(separation) | MSE(F)/MSE(sep) [CI] | reading | settings (A) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 81.4 | 0.769 [0.448, 0.994] | 0.774 | 1.02 [0.608, 1.17] | undetermined (n_eff < 50) | F: mid; qn 2, mid 9, low 4 |
| H=8 (0.27 LT) | deployable | 81.4 | 0.311 [0.0161, 0.609] | -1.37 | 0.326 [0.181, 0.517] | undetermined (n_eff < 50) | F: mid; qn 2, mid 8, low 5 |
| H=15 (0.50 LT) | oracle | 95.7 | 0.924 [0.89, 0.948] | 0.869 | 0.891 [0.79, 0.982] | undetermined (n_eff < 50) | F: low; qn 5, mid 0, low 10 |
| H=15 (0.50 LT) | deployable | 95.7 | 0.465 [0.317, 0.594] | -0.502 | 0.474 [0.379, 0.587] | lowers | F: mid; qn 6, mid 6, low 3 |
| H=30 (1.00 LT) | oracle | 188 | 0.758 [0.659, 0.834] | 0.71 | 0.954 [0.863, 1.07] | undetermined (n_eff < 50) | F: qn; qn 2, mid 7, low 6 |
| H=30 (1.00 LT) | deployable | 188 | 0.355 [0.153, 0.526] | -0.29 | 0.676 [0.562, 0.812] | lowers | F: qn; qn 6, mid 4, low 5 |
| H=60 (2.00 LT) | oracle | 461 | 0.333 [0.199, 0.431] | 0.259 | 0.965 [0.937, 0.996] | lowers | F: mid; qn 0, mid 8, low 7 |
| H=60 (2.00 LT) | deployable | 461 | 0.128 [0.0562, 0.196] | -0.0838 | 0.915 [0.88, 0.954] | lowers | F: mid; qn 0, mid 6, low 9 |
| H=120 (4.00 LT) | oracle | 1.7e+03 | 0.0463 [0.0149, 0.0776] | -0.19 | 0.934 [0.921, 0.945] | lowers | F: mid; qn 0, mid 7, low 8 |
| H=120 (4.00 LT) | deployable | 1.7e+03 | 0.015 [-0.00216, 0.0317] | -0.192 | 0.943 [0.932, 0.955] | lowers | F: low; qn 0, mid 2, low 13 |

### B. Allocation: pairwise interactions (logit u, interior states)

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED. Delta = L(additive) - L(additive + pair) on the test states, models fixed; level 1 - 0.05/6; Holm over the six pairs. R x I and O x I are primary.

| horizon | profile | pair | Delta [CI] | Holm p | reading | loss ratio reading |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | RI (primary) | 0.0278 [-0.0542, 0.106] | 0.552 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | OI (primary) | 0.0544 [-0.00937, 0.126] | 0.0725 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | RO | 0.203 [0.109, 0.297] | 0.003 | interaction gain detected | needed, size not determined |
| H=8 (0.27 LT) | oracle | RN | -0.0163 [-0.0844, 0.0561] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | ON | -0.0223 [-0.0988, 0.053] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | IN | 0.0176 [-0.0207, 0.0575] | 0.552 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RI (primary) | 0.0286 [-0.0207, 0.0799] | 0.278 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | OI (primary) | 0.0175 [-0.0129, 0.0486] | 0.277 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RO | 0.142 [0.0805, 0.209] | 0.003 | interaction gain detected | small |
| H=8 (0.27 LT) | deployable | RN | -0.0116 [-0.0543, 0.0277] | 0.775 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | ON | 0.00676 [-0.03, 0.0436] | 0.628 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | IN | 0.0132 [-0.0292, 0.0562] | 0.628 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | RI (primary) | 0.0194 [-0.0381, 0.0772] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | OI (primary) | -0.035 [-0.102, 0.0342] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | RO | 0.00668 [-0.0708, 0.0763] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | RN | 0.0132 [-0.0515, 0.0801] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | ON | -0.0157 [-0.0779, 0.0515] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | IN | 0.0102 [-0.0274, 0.0512] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | RI (primary) | 0.02 [-0.0248, 0.0668] | 0.504 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | OI (primary) | -0.0646 [-0.215, 0.0819] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | RO | 0.243 [0.057, 0.436] | 0.003 | interaction gain detected | needed, size not determined |
| H=15 (0.50 LT) | deployable | RN | 0.00841 [-0.0225, 0.0404] | 0.678 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | ON | -0.0926 [-0.24, 0.053] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | IN | 0.0295 [-0.00751, 0.0681] | 0.102 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | RI (primary) | 0.0311 [-0.0508, 0.114] | 0.53 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | OI (primary) | 0.0358 [-0.0467, 0.112] | 0.53 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | RO | 0.0462 [-0.0313, 0.125] | 0.295 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | RN | 0.0135 [-0.0546, 0.0821] | 0.601 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | ON | 0.0132 [-0.0693, 0.0874] | 0.601 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | IN | 0.0513 [-0.01, 0.109] | 0.072 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | RI (primary) | 0.0429 [0.0111, 0.0754] | 0.005 | interaction gain detected | small |
| H=30 (1.00 LT) | deployable | OI (primary) | -0.0098 [-0.0425, 0.0223] | 0.773 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | RO | 0.15 [0.0772, 0.23] | 0.003 | interaction gain detected | small |
| H=30 (1.00 LT) | deployable | RN | 0.0299 [-0.0107, 0.0682] | 0.106 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | ON | 0.0123 [-0.0368, 0.0572] | 0.726 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | IN | 0.01 [-0.0327, 0.0543] | 0.726 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | RI (primary) | 0.0382 [-0.0441, 0.117] | 0.456 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | OI (primary) | 0.0804 [-0.00075, 0.158] | 0.039 | interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | RO | -0.000638 [-0.0966, 0.0955] | 1 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | RN | 0.0582 [-0.0932, 0.205] | 0.478 | no interaction gain detected | undetermined |
| H=60 (2.00 LT) | oracle | ON | -0.00765 [-0.0856, 0.074] | 1 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | IN | 0.0506 [-0.0133, 0.116] | 0.075 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | RI (primary) | 0.0555 [0.0126, 0.0964] | 0.0075 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | OI (primary) | 0.00822 [-0.0154, 0.0315] | 0.595 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | RO | 0.085 [0.0181, 0.153] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | RN | 0.00981 [-0.0176, 0.04] | 0.595 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | ON | -0.00162 [-0.0393, 0.0355] | 0.595 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | IN | 0.0287 [0.000132, 0.0566] | 0.018 | interaction gain detected | small |
| H=120 (4.00 LT) | oracle | RI (primary) | 0.0347 [-0.00143, 0.0665] | 0.033 | interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | OI (primary) | 0.0278 [-0.0158, 0.0752] | 0.312 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RO | 0.0189 [-0.0262, 0.0639] | 0.382 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RN | -0.00383 [-0.028, 0.0208] | 0.848 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | ON | 0.00299 [-0.0324, 0.0394] | 0.848 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | IN | 0.0202 [-0.0174, 0.0569] | 0.344 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RI (primary) | 0.0392 [0.0124, 0.0672] | 0.003 | interaction gain detected | small |
| H=120 (4.00 LT) | deployable | OI (primary) | 0.0186 [-0.0285, 0.0613] | 0.524 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RO | -0.00252 [-0.0311, 0.0241] | 0.794 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RN | 0.00159 [-0.0213, 0.0222] | 0.794 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | ON | 0.0161 [-0.00313, 0.0351] | 0.075 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | IN | 0.00796 [-0.0213, 0.0369] | 0.778 | no interaction gain detected | negligible |

### D. Allocation ladder (rung against the full profile)

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED. MSE ratio MSE(rung)/MSE(F) at level 1 - 0.05/m (m rungs); Holm p for Delta MSE > 0. Theory gap L_A(oracle F) is an upper bound; estimation gap = L_A(deployable F) - L_A(oracle F) (95%).

| horizon | profile | rung | MSE | MSE ratio vs F [CI] | reading | Holm p |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | none | 0.0155 | 3.15 [1.36, 20.5] | undetermined (n_eff < 50) | 0.0045 |
| H=8 (0.27 LT) | oracle | separation | 0.00484 | 0.985 [0.823, 1.93] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | RO | 0.00487 | 0.991 [0.984, 1.03] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | R | 0.0163 | 3.31 [1.33, 23.8] | undetermined (n_eff < 50) | 0.0045 |
| H=8 (0.27 LT) | oracle | O | 0.00499 | 1.02 [1, 1.17] | undetermined (n_eff < 50) | 0.024 |
| H=8 (0.27 LT) | oracle | I | 0.00783 | 1.59 [0.651, 11.3] | undetermined (n_eff < 50) | 0.542 |
| H=8 (0.27 LT) | oracle | N | 0.0145 | 2.95 [1.39, 19.8] | undetermined (n_eff < 50) | 0.0045 |
| H=8 (0.27 LT) | oracle | F (ROIN) | 0.00492 | 1 | | |
| H=8 (0.27 LT) | oracle | X | 0.00496 | 1.01 [0.555, 6.65] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | X+F | 0.00483 | 0.982 [0.939, 1.19] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | none | 0.0154 | 1.38 [0.916, 2.94] | undetermined (n_eff < 50) | 0.129 |
| H=8 (0.27 LT) | deployable | A2 (stored) | 0.0158 | 1.42 [0.935, 3] | undetermined (n_eff < 50) | 0.096 |
| H=8 (0.27 LT) | deployable | separation | 0.0342 | 3.06 [1.63, 6.91] | undetermined (n_eff < 50) | 0.006 |
| H=8 (0.27 LT) | deployable | A4 (stored) | 0.0342 | 3.06 [1.63, 6.91] | undetermined (n_eff < 50) | 0.006 |
| H=8 (0.27 LT) | deployable | RO | 0.0109 | 0.978 [0.626, 1.56] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | R | 0.0149 | 1.34 [0.875, 2.95] | undetermined (n_eff < 50) | 0.247 |
| H=8 (0.27 LT) | deployable | O | 0.0143 | 1.28 [1.05, 1.95] | undetermined (n_eff < 50) | 0.009 |
| H=8 (0.27 LT) | deployable | I | 0.0158 | 1.42 [1.12, 2.24] | undetermined (n_eff < 50) | 0.006 |
| H=8 (0.27 LT) | deployable | N | 0.0151 | 1.35 [0.877, 2.83] | undetermined (n_eff < 50) | 0.216 |
| H=8 (0.27 LT) | deployable | F (ROIN) | 0.0112 | 1 | | |
| H=8 (0.27 LT) | deployable | X | 0.00494 | 0.442 [0.0925, 1.04] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | A3 (stored) | 0.0149 | 1.33 [0.644, 3.65] | undetermined (n_eff < 50) | 0.67 |
| H=8 (0.27 LT) | deployable | X+F | 0.00575 | 0.516 [0.0904, 1.35] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | oracle | none | 0.0282 | 3.06 [2.25, 4.5] | undetermined (n_eff < 50) | 0.0045 |
| H=15 (0.50 LT) | oracle | separation | 0.0103 | 1.12 [0.991, 1.38] | undetermined (n_eff < 50) | 0.024 |
| H=15 (0.50 LT) | oracle | RO | 0.00965 | 1.05 [0.96, 1.14] | undetermined (n_eff < 50) | 0.153 |
| H=15 (0.50 LT) | oracle | R | 0.0235 | 2.56 [1.93, 3.66] | undetermined (n_eff < 50) | 0.0045 |
| H=15 (0.50 LT) | oracle | O | 0.0108 | 1.17 [1.03, 1.45] | undetermined (n_eff < 50) | 0.0045 |
| H=15 (0.50 LT) | oracle | I | 0.0189 | 2.06 [1.63, 2.82] | undetermined (n_eff < 50) | 0.0045 |
| H=15 (0.50 LT) | oracle | N | 0.0222 | 2.41 [1.83, 3.27] | undetermined (n_eff < 50) | 0.0045 |
| H=15 (0.50 LT) | oracle | F (ROIN) | 0.0092 | 1 | | |
| H=15 (0.50 LT) | oracle | X | 0.0124 | 1.34 [1.14, 1.68] | undetermined (n_eff < 50) | 0.0045 |
| H=15 (0.50 LT) | oracle | X+F | 0.00987 | 1.07 [0.96, 1.23] | undetermined (n_eff < 50) | 0.153 |
| H=15 (0.50 LT) | deployable | none | 0.0302 | 1.53 [1.22, 2.06] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | A2 (stored) | 0.0302 | 1.53 [1.22, 2.06] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | separation | 0.0416 | 2.11 [1.55, 3.05] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | A4 (stored) | 0.0416 | 2.11 [1.55, 3.05] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | RO | 0.0266 | 1.35 [1.08, 1.78] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | R | 0.024 | 1.22 [0.991, 1.54] | undetermined (n_eff < 50) | 0.0105 |
| H=15 (0.50 LT) | deployable | O | 0.0284 | 1.44 [1.17, 1.85] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | I | 0.026 | 1.32 [1.09, 1.68] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | N | 0.0278 | 1.41 [1.07, 1.85] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | F (ROIN) | 0.0197 | 1 | | |
| H=15 (0.50 LT) | deployable | X | 0.0135 | 0.687 [0.49, 0.929] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | A3 (stored) | 0.0267 | 1.36 [1.02, 1.78] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | X+F | 0.0158 | 0.802 [0.634, 0.961] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | none | 0.0532 | 1.77 [1.46, 2.26] | undetermined (n_eff < 50) | 0.0045 |
| H=30 (1.00 LT) | oracle | separation | 0.0315 | 1.05 [0.884, 1.2] | undetermined (n_eff < 50) | 0.188 |
| H=30 (1.00 LT) | oracle | RO | 0.0359 | 1.2 [1.09, 1.37] | undetermined (n_eff < 50) | 0.0045 |
| H=30 (1.00 LT) | oracle | R | 0.0545 | 1.81 [1.5, 2.34] | undetermined (n_eff < 50) | 0.0045 |
| H=30 (1.00 LT) | oracle | O | 0.0368 | 1.22 [1.11, 1.43] | undetermined (n_eff < 50) | 0.0045 |
| H=30 (1.00 LT) | oracle | I | 0.0384 | 1.28 [1.07, 1.54] | undetermined (n_eff < 50) | 0.0045 |
| H=30 (1.00 LT) | oracle | N | 0.0463 | 1.54 [1.29, 1.92] | undetermined (n_eff < 50) | 0.0045 |
| H=30 (1.00 LT) | oracle | F (ROIN) | 0.0301 | 1 | | |
| H=30 (1.00 LT) | oracle | X | 0.0363 | 1.21 [1.01, 1.47] | undetermined (n_eff < 50) | 0.0045 |
| H=30 (1.00 LT) | oracle | X+F | 0.0346 | 1.15 [1.05, 1.32] | undetermined (n_eff < 50) | 0.0045 |
| H=30 (1.00 LT) | deployable | none | 0.0551 | 1.26 [1.04, 1.54] | undetermined (n_eff < 50) | 0.01 |
| H=30 (1.00 LT) | deployable | A2 (stored) | 0.0552 | 1.27 [1.03, 1.55] | undetermined (n_eff < 50) | 0.01 |
| H=30 (1.00 LT) | deployable | separation | 0.0645 | 1.48 [1.14, 1.9] | undetermined (n_eff < 50) | 0.0065 |
| H=30 (1.00 LT) | deployable | A4 (stored) | 0.0645 | 1.48 [1.14, 1.9] | undetermined (n_eff < 50) | 0.0065 |
| H=30 (1.00 LT) | deployable | RO | 0.0505 | 1.16 [0.967, 1.38] | undetermined (n_eff < 50) | 0.0665 |
| H=30 (1.00 LT) | deployable | R | 0.0501 | 1.15 [0.932, 1.39] | undetermined (n_eff < 50) | 0.15 |
| H=30 (1.00 LT) | deployable | O | 0.0582 | 1.34 [1.11, 1.63] | undetermined (n_eff < 50) | 0.0065 |
| H=30 (1.00 LT) | deployable | I | 0.0492 | 1.13 [0.926, 1.36] | undetermined (n_eff < 50) | 0.198 |
| H=30 (1.00 LT) | deployable | N | 0.0537 | 1.23 [1, 1.52] | undetermined (n_eff < 50) | 0.016 |
| H=30 (1.00 LT) | deployable | A5 (stored) | 0.0509 | 1.17 [0.959, 1.43] | undetermined (n_eff < 50) | 0.09 |
| H=30 (1.00 LT) | deployable | F (ROIN) | 0.0436 | 1 | | |
| H=30 (1.00 LT) | deployable | X | 0.039 | 0.894 [0.699, 1.11] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | deployable | A3 (stored) | 0.0476 | 1.09 [0.835, 1.39] | undetermined (n_eff < 50) | 0.544 |
| H=30 (1.00 LT) | deployable | X+F | 0.0403 | 0.925 [0.794, 1.09] | undetermined (n_eff < 50) | 1 |
| H=60 (2.00 LT) | oracle | none | 0.138 | 1.16 [1.05, 1.26] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | separation | 0.123 | 1.04 [0.993, 1.08] | undetermined | 0.039 |
| H=60 (2.00 LT) | oracle | RO | 0.123 | 1.03 [1, 1.07] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | R | 0.135 | 1.13 [1.03, 1.23] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | O | 0.126 | 1.06 [1.02, 1.1] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | I | 0.135 | 1.14 [1.04, 1.22] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | N | 0.134 | 1.12 [1.03, 1.21] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | F (ROIN) | 0.119 | 1 | | |
| H=60 (2.00 LT) | oracle | X | 0.123 | 1.03 [0.947, 1.1] | undetermined | 0.284 |
| H=60 (2.00 LT) | oracle | X+F | 0.119 | 1 [0.955, 1.05] | negligible | 0.496 |
| H=60 (2.00 LT) | deployable | none | 0.138 | 1.06 [1.01, 1.11] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | A2 (stored) | 0.138 | 1.06 [1.01, 1.11] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | separation | 0.143 | 1.09 [1.03, 1.15] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | A4 (stored) | 0.143 | 1.09 [1.03, 1.15] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | RO | 0.137 | 1.05 [1.01, 1.09] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | R | 0.14 | 1.07 [1.02, 1.11] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | O | 0.137 | 1.05 [1.01, 1.1] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | I | 0.136 | 1.04 [0.995, 1.09] | undetermined | 0.028 |
| H=60 (2.00 LT) | deployable | N | 0.136 | 1.04 [1, 1.08] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | F (ROIN) | 0.131 | 1 | | |
| H=60 (2.00 LT) | deployable | X | 0.122 | 0.936 [0.886, 0.991] | lowers | 1 |
| H=60 (2.00 LT) | deployable | A3 (stored) | 0.131 | 0.999 [0.94, 1.06] | undetermined | 1 |
| H=60 (2.00 LT) | deployable | X+F | 0.121 | 0.924 [0.884, 0.965] | lowers | 1 |
| H=120 (4.00 LT) | oracle | none | 0.883 | 1.01 [1, 1.03] | small | 0.018 |
| H=120 (4.00 LT) | oracle | separation | 0.933 | 1.07 [1.05, 1.09] | substantial | 0.0045 |
| H=120 (4.00 LT) | oracle | RO | 0.873 | 1 [0.996, 1.01] | negligible | 0.42 |
| H=120 (4.00 LT) | oracle | R | 0.877 | 1.01 [0.996, 1.02] | negligible | 0.15 |
| H=120 (4.00 LT) | oracle | O | 0.879 | 1.01 [0.998, 1.02] | negligible | 0.0675 |
| H=120 (4.00 LT) | oracle | I | 0.883 | 1.01 [1, 1.03] | small | 0.014 |
| H=120 (4.00 LT) | oracle | N | 0.884 | 1.02 [1, 1.03] | small | 0.012 |
| H=120 (4.00 LT) | oracle | F (ROIN) | 0.871 | 1 | | |
| H=120 (4.00 LT) | oracle | X | 0.874 | 1 [0.99, 1.02] | negligible | 0.434 |
| H=120 (4.00 LT) | oracle | X+F | 0.867 | 0.996 [0.989, 1] | negligible | 0.959 |
| H=120 (4.00 LT) | deployable | none | 0.873 | 1 [0.997, 1.01] | negligible | 0.388 |
| H=120 (4.00 LT) | deployable | A2 (stored) | 0.873 | 1 [0.997, 1.01] | negligible | 0.388 |
| H=120 (4.00 LT) | deployable | separation | 0.921 | 1.06 [1.04, 1.08] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | A4 (stored) | 0.921 | 1.06 [1.04, 1.08] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | RO | 0.87 | 1 [0.998, 1] | negligible | 0.388 |
| H=120 (4.00 LT) | deployable | R | 0.869 | 1 [0.996, 1] | negligible | 1 |
| H=120 (4.00 LT) | deployable | O | 0.873 | 1 [0.999, 1.01] | negligible | 0.121 |
| H=120 (4.00 LT) | deployable | I | 0.872 | 1 [0.997, 1.01] | negligible | 0.388 |
| H=120 (4.00 LT) | deployable | N | 0.872 | 1 [0.998, 1.01] | negligible | 0.388 |
| H=120 (4.00 LT) | deployable | F (ROIN) | 0.869 | 1 | | |
| H=120 (4.00 LT) | deployable | X | 0.861 | 0.991 [0.979, 1] | negligible | 1 |
| H=120 (4.00 LT) | deployable | A3 (stored) | 0.885 | 1.02 [1, 1.04] | small | 0.025 |
| H=120 (4.00 LT) | deployable | X+F | 0.861 | 0.991 [0.981, 1] | negligible | 1 |

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| horizon | theory gap (upper bound) [CI] | estimation gap [CI] | gap with R estimated | gap with O estimated | gap with I estimated | gap with N estimated |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 0.00319 [8.07e-05, 0.0082] | 0.00623 [0.00266, 0.0109] | 8.79e-05 [7.39e-06, 0.000188] | 0.00663 [0.0018, 0.013] | 6.92e-05 [-3.49e-05, 0.000195] | 2.23e-05 [-5.39e-05, 0.000114] |
| H=15 (0.50 LT) | 0.00156 [0.00107, 0.00221] | 0.0105 [0.00673, 0.0144] | 0.00141 [-3.47e-05, 0.00305] | 0.0072 [0.00439, 0.0101] | 0.000764 [-0.000843, 0.00236] | -2.81e-05 [-0.00127, 0.00129] |
| H=30 (1.00 LT) | 0.0074 [0.00506, 0.0104] | 0.0135 [0.00699, 0.021] | 0.00754 [0.0014, 0.0149] | 0.00494 [0.000332, 0.0101] | 0.00236 [-0.00236, 0.0082] | 0.00614 [-0.000126, 0.0138] |
| H=60 (2.00 LT) | 0.0382 [0.0321, 0.0456] | 0.0117 [-8.6e-05, 0.0217] | 0.0107 [-0.000136, 0.0211] | 0.00465 [-0.00612, 0.014] | -0.000198 [-0.00864, 0.0078] | 0.00078 [-0.00781, 0.00889] |
| H=120 (4.00 LT) | 0.25 [0.237, 0.262] | -0.00177 [-0.0258, 0.0231] | -0.00784 [-0.0311, 0.0155] | 0.00178 [-0.0221, 0.0249] | -0.00854 [-0.031, 0.0137] | -0.0121 [-0.035, 0.0111] |

### Horizon decision (Y = ln min(T_c, H_max))

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED. Pinball loss at tau = 0.5; drop-one ratio at level 1 - 0.05/4; ladder ratio vs F at 1 - 0.05/m; C = Harrell's C (95%); coverage of q_0.1, q_0.5, q_0.9 and the 80% interval below the cap.

| profile | X | pinball ratio [CI] | reading | Holm p | phi [CI] |
|---|---|---|---|---|---|
| oracle | R | 1.01 [0.999, 1.02] | negligible | 0.02 | 0.00228 [0.00137, 0.00312] |
| oracle | O | 1.1 [1.08, 1.13] | substantial | 0.002 | 0.00973 [0.00823, 0.0112] |
| oracle | I | 1.22 [1.18, 1.26] | substantial | 0.002 | 0.027 [0.0231, 0.0308] |
| oracle | N | 0.996 [0.987, 1.01] | negligible | 0.816 | 0.0016 [0.000632, 0.0025] |
| deployable | R | 1 [0.994, 1.01] | negligible | 0.866 | 0.00212 [0.00143, 0.00282] |
| deployable | O | 1.08 [1.07, 1.1] | substantial | 0.002 | 0.00946 [0.00814, 0.0107] |
| deployable | I | 1.23 [1.19, 1.27] | substantial | 0.002 | 0.0277 [0.0238, 0.0316] |
| deployable | N | 0.996 [0.99, 1] | negligible | 0.972 | 0.000891 [0.000417, 0.00134] |

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | ratio vs F [CI] | reading | C [CI] | cov 0.1 / 0.5 / 0.9 / 80% |
|---|---|---|---|---|---|---|
| oracle | none | 0.19 | 1.27 [1.22, 1.32] | substantial | 0.5 [0.5, 0.5] | 0.089 / 0.489 / 0.903 / 0.814 |
| oracle | lyapunov | 0.3 | 2.01 [1.89, 2.12] | substantial | 0.612 [0.601, 0.623] | 0.0758 / 0.45 / 0.839 / 0.81 |
| oracle | RO | 0.184 | 1.23 [1.19, 1.28] | substantial | 0.58 [0.569, 0.591] | 0.115 / 0.494 / 0.892 / 0.777 |
| oracle | R | 0.188 | 1.26 [1.21, 1.31] | substantial | 0.539 [0.528, 0.549] | 0.0865 / 0.487 / 0.897 / 0.811 |
| oracle | O | 0.187 | 1.25 [1.21, 1.3] | substantial | 0.554 [0.544, 0.564] | 0.0862 / 0.49 / 0.889 / 0.803 |
| oracle | I | 0.17 | 1.14 [1.11, 1.18] | substantial | 0.61 [0.6, 0.621] | 0.12 / 0.479 / 0.883 / 0.763 |
| oracle | N | 0.187 | 1.25 [1.2, 1.3] | substantial | 0.569 [0.559, 0.58] | 0.0887 / 0.492 / 0.901 / 0.812 |
| oracle | ROIN | 0.149 | 1 |  | 0.686 [0.675, 0.696] | 0.141 / 0.488 / 0.866 / 0.726 |
| oracle | X | 0.156 | 1.05 [0.994, 1.1] | undetermined | 0.673 [0.662, 0.683] | 0.141 / 0.48 / 0.85 / 0.709 |
| oracle | X+F | 0.13 | 0.87 [0.847, 0.892] | lowers | 0.736 [0.725, 0.746] | 0.144 / 0.488 / 0.853 / 0.71 |
| oracle | Lyapunov rank (C only) | | | | 0.609 [0.598, 0.621] | |
| deployable | none | 0.19 | 1.27 [1.22, 1.32] | substantial | 0.5 [0.5, 0.5] | 0.089 / 0.489 / 0.903 / 0.814 |
| deployable | lyapunov | 0.298 | 1.99 [1.88, 2.09] | substantial | 0.609 [0.598, 0.619] | 0.0768 / 0.449 / 0.839 / 0.809 |
| deployable | RO | 0.185 | 1.24 [1.19, 1.28] | substantial | 0.569 [0.559, 0.579] | 0.0937 / 0.495 / 0.899 / 0.805 |
| deployable | R | 0.188 | 1.26 [1.21, 1.31] | substantial | 0.542 [0.533, 0.551] | 0.0881 / 0.484 / 0.9 / 0.812 |
| deployable | O | 0.186 | 1.24 [1.2, 1.3] | substantial | 0.552 [0.543, 0.562] | 0.0875 / 0.493 / 0.895 / 0.807 |
| deployable | I | 0.171 | 1.14 [1.11, 1.18] | substantial | 0.612 [0.602, 0.623] | 0.0951 / 0.49 / 0.893 / 0.798 |
| deployable | N | 0.188 | 1.26 [1.21, 1.31] | substantial | 0.549 [0.542, 0.556] | 0.0899 / 0.488 / 0.894 / 0.805 |
| deployable | ROIN | 0.15 | 1 |  | 0.677 [0.667, 0.688] | 0.129 / 0.492 / 0.876 / 0.747 |
| deployable | X | 0.157 | 1.05 [0.997, 1.1] | undetermined | 0.675 [0.664, 0.684] | 0.136 / 0.481 / 0.853 / 0.717 |
| deployable | X+F | 0.132 | 0.884 [0.861, 0.908] | lowers | 0.723 [0.712, 0.733] | 0.147 / 0.492 / 0.863 / 0.716 |
| deployable | Lyapunov rank (C only) | | | | 0.612 [0.601, 0.623] | |

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| profile | pair | Delta [CI] | Holm p | detected |
|---|---|---|---|---|
| oracle | RO | 0.00268 [0.000932, 0.00443] | 0.003 | True |
| oracle | RI (primary) | 0.00318 [0.00122, 0.00506] | 0.003 | True |
| oracle | RN | 0.000318 [-0.00161, 0.00203] | 0.326 | False |
| oracle | OI (primary) | 0.0161 [0.0123, 0.0199] | 0.003 | True |
| oracle | ON | 0.000898 [-0.000744, 0.00246] | 0.138 | False |
| oracle | IN | 0.00117 [0.000185, 0.00208] | 0.003 | True |
| deployable | RO | 0.00163 [-8.84e-05, 0.0032] | 0.011 | True |
| deployable | RI (primary) | 0.00484 [0.00236, 0.00747] | 0.003 | True |
| deployable | RN | 0.00057 [0.000297, 0.000862] | 0.003 | True |
| deployable | OI (primary) | 0.0178 [0.0145, 0.0213] | 0.003 | True |
| deployable | ON | 0.000282 [-0.000236, 0.000769] | 0.074 | False |
| deployable | IN | 0.000955 [0.000386, 0.00154] | 0.003 | True |

## rossler

**PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.**

| check | result |
|---|---|
| (f1) state_mse from per-draw errors, max rel diff | A0 0.0e+00, A1 0.0e+00, A2 0.0e+00, A3 0.0e+00, A4 0.0e+00, A5 0.0e+00 (within 1e-12: True) |
| (g) WU-0039b (b1), (b2) rows reproduced | drop-N: True, all rows: True |
| separation formula on F-hat vs stored A4 at H_ref, max abs | 2.22e-16 |
| T_c: T = 1 / e_(T-1) = theta (train, test) | 0/0, 0/0 |
| (f2) dependence bias, deployable rows (reported, not gating) | 131 rows; 75 flagged: H=8 R: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0128, z 6.75; H=8 I: dependence bias detectable (interval excludes 0), t1+t2 / V 0.000724, z 0.836; H=8 N: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0144, z 5.63; H=8 RO: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0207, z 6.93; H=8 RI: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0128, z 6.72; H=8 RN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.02, z 7.44; H=8 ON: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0146, z 5.37; H=8 IN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0135, z 5.69; H=8 ROI: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0205, z 6.82; H=8 RON: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0248, z 7.65; H=8 RIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0189, z 7.68; H=8 OIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0149, z 5.44 ... |

### A. Allocation: drop-one and Shapley

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED. MSE ratio MSE(F without X)/MSE(F) at level 1 - 0.05/4 (reading by the 1.05 table, with the n_eff guard); excess ratio L_A(F without X)/L_A(F) and Holm p (Delta MSE > 0) are estimates. phi = Shapley share of L_A (95%). Oracle rows: moment form; deployable rows: realized per draw.

| horizon | profile | X | MSE ratio [CI] | reading | excess ratio | Holm p | phi_X [95% CI] | share |
|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | R | 1.05 [1.04, 1.06] | needed, size not determined | 1.47 | 0.002 | 6.12e-06 [5.36e-06, 6.93e-06] | 0.635 |
| H=8 (0.27 LT) | oracle | O | 1.01 [1.01, 1.02] | small | 1.12 | 0.002 | 7.92e-07 [5.48e-07, 1.05e-06] | 0.0822 |
| H=8 (0.27 LT) | oracle | I | 1 [0.999, 1] | negligible | 0.998 | 0.899 | 3.05e-08 [-1.63e-08, 8.3e-08] | 0.00317 |
| H=8 (0.27 LT) | oracle | N | 1.01 [1.01, 1.01] | small | 1.09 | 0.002 | 2.7e-06 [2.4e-06, 2.98e-06] | 0.28 |
| H=8 (0.27 LT) | deployable | R | 0.999 [0.993, 1] | negligible | 0.993 | 1 | -2.88e-07 [-7.66e-07, 1.6e-07] | 0.707 |
| H=8 (0.27 LT) | deployable | O | 0.997 [0.992, 1] | negligible | 0.984 | 1 | -1.1e-07 [-5.15e-07, 2.82e-07] | 0.27 |
| H=8 (0.27 LT) | deployable | I | 1 [1, 1] | negligible | 1 | 0.22 | 3.79e-08 [-5.89e-08, 1.27e-07] | -0.093 |
| H=8 (0.27 LT) | deployable | N | 0.999 [0.995, 1] | negligible | 0.996 | 1 | -4.74e-08 [-5.27e-07, 4.25e-07] | 0.116 |
| H=15 (0.50 LT) | oracle | R | 1.07 [1.05, 1.08] | substantial | 1.76 | 0.002 | 1.47e-05 [1.3e-05, 1.66e-05] | 0.682 |
| H=15 (0.50 LT) | oracle | O | 1.02 [1.01, 1.03] | small | 1.22 | 0.002 | 2.1e-06 [1.4e-06, 2.84e-06] | 0.0974 |
| H=15 (0.50 LT) | oracle | I | 1 [0.999, 1] | negligible | 0.999 | 0.679 | -1.64e-07 [-4.04e-07, 4.91e-08] | -0.00761 |
| H=15 (0.50 LT) | oracle | N | 1.01 [1, 1.01] | small | 1.09 | 0.002 | 4.92e-06 [4.06e-06, 5.72e-06] | 0.228 |
| H=15 (0.50 LT) | deployable | R | 1 [0.996, 1.01] | negligible | 1.02 | 0.536 | -3.77e-08 [-1.27e-06, 1.17e-06] | 0.0307 |
| H=15 (0.50 LT) | deployable | O | 1 [0.993, 1.01] | negligible | 1 | 0.785 | 1.6e-07 [-9.48e-07, 1.26e-06] | -0.13 |
| H=15 (0.50 LT) | deployable | I | 1 [0.998, 1] | negligible | 1 | 0.591 | -1.48e-07 [-8.51e-07, 4.71e-07] | 0.121 |
| H=15 (0.50 LT) | deployable | N | 0.997 [0.991, 1] | negligible | 0.985 | 0.834 | -1.2e-06 [-2.35e-06, -3.45e-08] | 0.979 |
| H=30 (1.00 LT) | oracle | R | 1.09 [1.07, 1.11] | substantial | 2.03 | 0.002 | 6.44e-05 [5.58e-05, 7.37e-05] | 0.695 |
| H=30 (1.00 LT) | oracle | O | 1.03 [1.02, 1.04] | small | 1.33 | 0.002 | 1.09e-05 [7.28e-06, 1.45e-05] | 0.118 |
| H=30 (1.00 LT) | oracle | I | 0.998 [0.993, 1] | negligible | 0.974 | 0.902 | 8.28e-07 [-4.51e-07, 2.11e-06] | 0.00893 |
| H=30 (1.00 LT) | oracle | N | 1 [0.997, 1.01] | negligible | 1.05 | 0.104 | 1.65e-05 [1.24e-05, 2.05e-05] | 0.178 |
| H=30 (1.00 LT) | deployable | R | 1.01 [0.995, 1.02] | negligible | 1.03 | 0.294 | 1.28e-06 [-3.42e-06, 5.93e-06] | -0.326 |
| H=30 (1.00 LT) | deployable | O | 1 [0.991, 1.01] | negligible | 1.01 | 0.793 | -2.49e-07 [-4.84e-06, 4.28e-06] | 0.0636 |
| H=30 (1.00 LT) | deployable | I | 1 [0.996, 1.01] | negligible | 1.01 | 0.793 | -1.02e-06 [-4.46e-06, 2.01e-06] | 0.261 |
| H=30 (1.00 LT) | deployable | N | 0.998 [0.99, 1.01] | negligible | 0.991 | 0.793 | -3.92e-06 [-8.77e-06, 8e-07] | 1 |
| H=60 (2.00 LT) | oracle | R | 1.08 [1.06, 1.1] | substantial | 1.34 | 0.002 | 0.000943 [0.000756, 0.00114] | 0.803 |
| H=60 (2.00 LT) | oracle | O | 1.01 [0.998, 1.03] | negligible | 1.06 | 0.051 | 0.000132 [3.95e-05, 0.000225] | 0.112 |
| H=60 (2.00 LT) | oracle | I | 1 [0.998, 1.01] | negligible | 1.01 | 0.208 | 5.07e-05 [1.77e-05, 8.45e-05] | 0.0432 |
| H=60 (2.00 LT) | oracle | N | 0.993 [0.984, 1] | negligible | 0.97 | 0.968 | 4.87e-05 [-5.65e-05, 0.000148] | 0.0415 |
| H=60 (2.00 LT) | deployable | R | 1 [0.995, 1.01] | negligible | 1.01 | 0.412 | 2.16e-05 [-5.75e-05, 0.000109] | 0.155 |
| H=60 (2.00 LT) | deployable | O | 1.01 [0.998, 1.02] | negligible | 1.02 | 0.135 | 8.7e-05 [-9.04e-06, 0.000187] | 0.625 |
| H=60 (2.00 LT) | deployable | I | 1 [1, 1] | small | 1.01 | 0.012 | 6e-05 [1.88e-05, 0.000106] | 0.431 |
| H=60 (2.00 LT) | deployable | N | 0.998 [0.993, 1] | negligible | 0.993 | 0.861 | -2.94e-05 [-0.00011, 4.2e-05] | -0.211 |
| H=120 (4.00 LT) | oracle | R | 1.01 [1, 1.02] | small | 1.04 | 0.002 | 0.00126 [0.00066, 0.00188] | 0.528 |
| H=120 (4.00 LT) | oracle | O | 1 [1, 1.01] | small | 1.01 | 0.011 | 0.000163 [-7.47e-05, 0.000392] | 0.0683 |
| H=120 (4.00 LT) | oracle | I | 1.01 [1, 1.01] | small | 1.02 | 0.0075 | 0.000655 [0.000295, 0.00102] | 0.275 |
| H=120 (4.00 LT) | oracle | N | 1 [0.999, 1] | negligible | 1 | 0.504 | 0.000307 [0.000123, 0.000494] | 0.129 |
| H=120 (4.00 LT) | deployable | R | 1 [1, 1] | small | 1.01 | 0.0165 | 0.000484 [0.000246, 0.000749] | 0.294 |
| H=120 (4.00 LT) | deployable | O | 1 [1, 1] | negligible | 1.01 | 0.022 | 0.000222 [5.56e-05, 0.000379] | 0.135 |
| H=120 (4.00 LT) | deployable | I | 1.01 [1, 1.01] | small | 1.03 | 0.004 | 0.000742 [0.000344, 0.00111] | 0.451 |
| H=120 (4.00 LT) | deployable | N | 1 [0.999, 1] | negligible | 1 | 0.273 | 0.000197 [-2.41e-06, 0.000399] | 0.12 |

### A. Allocation: summary per horizon

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED. n_eff = Kish size of kappa on the test states; G = 1 - L_A(rule)/L_A(constant), estimate (95%).

| horizon | profile | n_eff(kappa) | G(F) [CI] | G(separation) | MSE(F)/MSE(sep) [CI] | reading | settings (A) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 875 | 0.457 [0.429, 0.485] | 0.0783 | 0.935 [0.928, 0.943] | lowers | F: mid; qn 0, mid 7, low 8 |
| H=8 (0.27 LT) | deployable | 875 | -0.0201 [-0.0679, 0.0208] | -0.548 | 0.921 [0.91, 0.932] | lowers | F: mid; qn 0, mid 9, low 6 |
| H=15 (0.50 LT) | oracle | 561 | 0.537 [0.503, 0.569] | 0.254 | 0.948 [0.942, 0.955] | lowers | F: mid; qn 0, mid 9, low 6 |
| H=15 (0.50 LT) | deployable | 561 | -0.033 [-0.0955, 0.0203] | -0.466 | 0.934 [0.92, 0.948] | lowers | F: mid; qn 0, mid 13, low 2 |
| H=30 (1.00 LT) | oracle | 270 | 0.599 [0.549, 0.642] | 0.449 | 0.967 [0.959, 0.976] | lowers | F: qn; qn 4, mid 4, low 7 |
| H=30 (1.00 LT) | deployable | 270 | -0.0241 [-0.091, 0.0258] | -0.247 | 0.956 [0.941, 0.972] | lowers | F: mid; qn 0, mid 8, low 7 |
| H=60 (2.00 LT) | oracle | 557 | 0.305 [0.241, 0.365] | 0.331 | 1.01 [1, 1.02] | negligible | F: mid; qn 0, mid 5, low 10 |
| H=60 (2.00 LT) | deployable | 557 | 0.0331 [0.00377, 0.0621] | 0.00316 | 0.991 [0.98, 1] | negligible | F: low; qn 0, mid 0, low 15 |
| H=120 (4.00 LT) | oracle | 1.52e+03 | 0.079 [0.0566, 0.101] | -0.0973 | 0.951 [0.939, 0.963] | lowers | F: low; qn 0, mid 1, low 14 |
| H=120 (4.00 LT) | deployable | 1.52e+03 | 0.0626 [0.044, 0.0818] | -0.179 | 0.941 [0.927, 0.954] | lowers | F: low; qn 0, mid 0, low 15 |

### B. Allocation: pairwise interactions (logit u, interior states)

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED. Delta = L(additive) - L(additive + pair) on the test states, models fixed; level 1 - 0.05/6; Holm over the six pairs. R x I and O x I are primary.

| horizon | profile | pair | Delta [CI] | Holm p | reading | loss ratio reading |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | RI (primary) | 0.0126 [-0.00391, 0.0296] | 0.102 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | OI (primary) | 0.000547 [-0.0131, 0.0138] | 0.456 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | RO | 0.0581 [0.015, 0.1] | 0.003 | interaction gain detected | small |
| H=8 (0.27 LT) | oracle | RN | 0.0197 [-0.0032, 0.0406] | 0.065 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | ON | 0.0187 [-0.00503, 0.0431] | 0.09 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | IN | 0.00362 [-0.00897, 0.0163] | 0.447 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RI (primary) | -0.000297 [-0.0185, 0.0169] | 0.52 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | OI (primary) | 0.0197 [0.00496, 0.0335] | 0.004 | interaction gain detected | small |
| H=8 (0.27 LT) | deployable | RO | 0.0556 [0.0208, 0.0893] | 0.003 | interaction gain detected | small |
| H=8 (0.27 LT) | deployable | RN | 0.0234 [0.00466, 0.0411] | 0.003 | interaction gain detected | small |
| H=8 (0.27 LT) | deployable | ON | 0.0142 [-0.000802, 0.028] | 0.0225 | interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | IN | 0.00705 [-0.000702, 0.0149] | 0.0225 | interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | RI (primary) | -0.00732 [-0.0313, 0.0144] | 0.972 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | OI (primary) | 0.000317 [-0.0173, 0.0195] | 0.972 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | RO | 0.0686 [0.0275, 0.111] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | oracle | RN | 0.0122 [-0.0154, 0.0386] | 0.442 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | ON | 0.0193 [-0.00397, 0.0432] | 0.085 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | IN | 0.00573 [-0.0102, 0.0222] | 0.442 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | RI (primary) | -0.0152 [-0.0411, 0.00837] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | OI (primary) | 0.0126 [-0.00361, 0.0283] | 0.076 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | RO | 0.0469 [0.0123, 0.0825] | 0.006 | interaction gain detected | small |
| H=15 (0.50 LT) | deployable | RN | 0.0125 [-0.0036, 0.0297] | 0.129 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | ON | 0.0127 [-0.00118, 0.0256] | 0.0325 | interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | IN | -0.00144 [-0.0112, 0.00837] | 1 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | RI (primary) | 0.000643 [-0.0236, 0.0261] | 0.476 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | OI (primary) | 0.0199 [-0.00333, 0.0451] | 0.0375 | interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | RO | 0.113 [0.0588, 0.167] | 0.003 | interaction gain detected | needed, size not determined |
| H=30 (1.00 LT) | oracle | RN | 0.0417 [0.0167, 0.0636] | 0.003 | interaction gain detected | small |
| H=30 (1.00 LT) | oracle | ON | 0.0408 [0.014, 0.0659] | 0.004 | interaction gain detected | small |
| H=30 (1.00 LT) | oracle | IN | 0.0042 [-0.00882, 0.0168] | 0.436 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | RI (primary) | 0.0124 [-0.0118, 0.0377] | 0.292 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | OI (primary) | 0.0327 [0.0157, 0.0504] | 0.003 | interaction gain detected | small |
| H=30 (1.00 LT) | deployable | RO | 0.0719 [0.0345, 0.111] | 0.003 | interaction gain detected | small |
| H=30 (1.00 LT) | deployable | RN | 0.0224 [0.00103, 0.0437] | 0.012 | interaction gain detected | small |
| H=30 (1.00 LT) | deployable | ON | 0.00828 [-0.00822, 0.0258] | 0.292 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | IN | 0.0021 [-0.00845, 0.0124] | 0.3 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | RI (primary) | 0.00916 [-0.0256, 0.0421] | 0.225 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | OI (primary) | 0.0375 [0.00831, 0.0674] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | oracle | RO | 0.0721 [0.0242, 0.119] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | oracle | RN | 0.0128 [-0.0164, 0.0375] | 0.225 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | ON | 0.0301 [-0.00477, 0.064] | 0.038 | interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | IN | 0.0157 [-0.00566, 0.0357] | 0.0885 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | RI (primary) | 0.0161 [-0.00493, 0.0378] | 0.0735 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | OI (primary) | 0.0195 [-0.00796, 0.0453] | 0.0735 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | RO | 0.0674 [0.032, 0.101] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | RN | 0.0168 [0.000925, 0.033] | 0.0175 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | ON | 0.0146 [-0.00856, 0.0386] | 0.0735 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | IN | 0.0151 [-0.00276, 0.0346] | 0.054 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RI (primary) | 0.0149 [0.000146, 0.0301] | 0.0225 | interaction gain detected | small |
| H=120 (4.00 LT) | oracle | OI (primary) | 0.00684 [-0.00431, 0.0185] | 0.189 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RO | 0.0139 [0.00266, 0.0261] | 0.009 | interaction gain detected | small |
| H=120 (4.00 LT) | oracle | RN | 0.00118 [-0.0147, 0.0167] | 0.845 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | ON | 0.00635 [-0.00222, 0.0144] | 0.096 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | IN | -8.96e-05 [-0.0115, 0.011] | 0.845 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RI (primary) | 0.00743 [-0.00759, 0.0215] | 0.267 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | OI (primary) | -0.00109 [-0.0132, 0.0119] | 0.589 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RO | 0.00681 [-0.000733, 0.0147] | 0.05 | interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RN | 0.00189 [-0.00203, 0.00554] | 0.267 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | ON | 0.00445 [6.73e-05, 0.00918] | 0.027 | interaction gain detected | small |
| H=120 (4.00 LT) | deployable | IN | 0.00487 [-0.00329, 0.013] | 0.21 | no interaction gain detected | negligible |

### D. Allocation ladder (rung against the full profile)

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED. MSE ratio MSE(rung)/MSE(F) at level 1 - 0.05/m (m rungs); Holm p for Delta MSE > 0. Theory gap L_A(oracle F) is an upper bound; estimation gap = L_A(deployable F) - L_A(oracle F) (95%).

| horizon | profile | rung | MSE | MSE ratio vs F [CI] | reading | Holm p |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | none | 0.000125 | 1.08 [1.07, 1.1] | substantial | 0.0045 |
| H=8 (0.27 LT) | oracle | separation | 0.000124 | 1.07 [1.06, 1.08] | substantial | 0.0045 |
| H=8 (0.27 LT) | oracle | RO | 0.000117 | 1.01 [1.01, 1.01] | small | 0.0045 |
| H=8 (0.27 LT) | oracle | R | 0.000119 | 1.02 [1.02, 1.03] | small | 0.0045 |
| H=8 (0.27 LT) | oracle | O | 0.000125 | 1.08 [1.07, 1.09] | substantial | 0.0045 |
| H=8 (0.27 LT) | oracle | I | 0.000125 | 1.08 [1.07, 1.09] | substantial | 0.0045 |
| H=8 (0.27 LT) | oracle | N | 0.000121 | 1.05 [1.04, 1.06] | needed, size not determined | 0.0045 |
| H=8 (0.27 LT) | oracle | F (ROIN) | 0.000116 | 1 | | |
| H=8 (0.27 LT) | oracle | X | 0.000125 | 1.08 [1.07, 1.09] | substantial | 0.0045 |
| H=8 (0.27 LT) | oracle | X+F | 0.000115 | 0.998 [0.995, 1] | negligible | 0.995 |
| H=8 (0.27 LT) | deployable | none | 0.000125 | 0.997 [0.986, 1.01] | negligible | 1 |
| H=8 (0.27 LT) | deployable | A2 (stored) | 0.000125 | 0.997 [0.986, 1.01] | negligible | 1 |
| H=8 (0.27 LT) | deployable | separation | 0.000136 | 1.09 [1.07, 1.1] | substantial | 0.006 |
| H=8 (0.27 LT) | deployable | A4 (stored) | 0.000136 | 1.09 [1.07, 1.1] | substantial | 0.006 |
| H=8 (0.27 LT) | deployable | RO | 0.000125 | 1 [0.996, 1.01] | negligible | 1 |
| H=8 (0.27 LT) | deployable | R | 0.000125 | 1 [0.991, 1.01] | negligible | 1 |
| H=8 (0.27 LT) | deployable | O | 0.000124 | 0.996 [0.986, 1.01] | negligible | 1 |
| H=8 (0.27 LT) | deployable | I | 0.000125 | 0.997 [0.987, 1.01] | negligible | 1 |
| H=8 (0.27 LT) | deployable | N | 0.000125 | 0.998 [0.99, 1] | negligible | 1 |
| H=8 (0.27 LT) | deployable | F (ROIN) | 0.000125 | 1 | | |
| H=8 (0.27 LT) | deployable | X | 0.000124 | 0.993 [0.98, 1.01] | negligible | 1 |
| H=8 (0.27 LT) | deployable | A3 (stored) | 0.000132 | 1.06 [1.03, 1.09] | needed, size not determined | 0.006 |
| H=8 (0.27 LT) | deployable | X+F | 0.000124 | 0.994 [0.987, 1] | negligible | 1 |
| H=15 (0.50 LT) | oracle | none | 0.00023 | 1.1 [1.09, 1.12] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | separation | 0.00022 | 1.05 [1.04, 1.07] | needed, size not determined | 0.0045 |
| H=15 (0.50 LT) | oracle | RO | 0.00021 | 1.01 [1, 1.01] | small | 0.0045 |
| H=15 (0.50 LT) | oracle | R | 0.000215 | 1.03 [1.02, 1.04] | small | 0.0045 |
| H=15 (0.50 LT) | oracle | O | 0.00023 | 1.11 [1.09, 1.12] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | I | 0.00023 | 1.11 [1.09, 1.12] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | N | 0.000222 | 1.06 [1.05, 1.08] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | F (ROIN) | 0.000208 | 1 | | |
| H=15 (0.50 LT) | oracle | X | 0.00023 | 1.1 [1.09, 1.12] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | X+F | 0.000208 | 0.999 [0.997, 1] | negligible | 0.981 |
| H=15 (0.50 LT) | deployable | none | 0.000227 | 0.995 [0.983, 1.01] | negligible | 1 |
| H=15 (0.50 LT) | deployable | A2 (stored) | 0.000227 | 0.995 [0.983, 1.01] | negligible | 1 |
| H=15 (0.50 LT) | deployable | separation | 0.000244 | 1.07 [1.05, 1.1] | needed, size not determined | 0.006 |
| H=15 (0.50 LT) | deployable | A4 (stored) | 0.000244 | 1.07 [1.05, 1.1] | needed, size not determined | 0.006 |
| H=15 (0.50 LT) | deployable | RO | 0.000228 | 1 [0.992, 1.01] | negligible | 1 |
| H=15 (0.50 LT) | deployable | R | 0.000228 | 0.998 [0.988, 1.01] | negligible | 1 |
| H=15 (0.50 LT) | deployable | O | 0.000227 | 0.994 [0.982, 1.01] | negligible | 1 |
| H=15 (0.50 LT) | deployable | I | 0.000228 | 0.997 [0.985, 1.01] | negligible | 1 |
| H=15 (0.50 LT) | deployable | N | 0.000229 | 1 [0.994, 1.01] | negligible | 1 |
| H=15 (0.50 LT) | deployable | F (ROIN) | 0.000228 | 1 | | |
| H=15 (0.50 LT) | deployable | X | 0.000227 | 0.992 [0.977, 1.01] | negligible | 1 |
| H=15 (0.50 LT) | deployable | A3 (stored) | 0.000239 | 1.05 [1.02, 1.08] | needed, size not determined | 0.006 |
| H=15 (0.50 LT) | deployable | X+F | 0.000227 | 0.994 [0.985, 1] | negligible | 1 |
| H=30 (1.00 LT) | oracle | none | 0.000782 | 1.13 [1.11, 1.16] | substantial | 0.0045 |
| H=30 (1.00 LT) | oracle | separation | 0.000712 | 1.03 [1.02, 1.05] | small | 0.0045 |
| H=30 (1.00 LT) | oracle | RO | 0.000693 | 1.01 [0.997, 1.01] | negligible | 0.075 |
| H=30 (1.00 LT) | oracle | R | 0.00072 | 1.04 [1.03, 1.06] | needed, size not determined | 0.0045 |
| H=30 (1.00 LT) | oracle | O | 0.000784 | 1.14 [1.11, 1.16] | substantial | 0.0045 |
| H=30 (1.00 LT) | oracle | I | 0.00078 | 1.13 [1.1, 1.16] | substantial | 0.0045 |
| H=30 (1.00 LT) | oracle | N | 0.000755 | 1.1 [1.07, 1.12] | substantial | 0.0045 |
| H=30 (1.00 LT) | oracle | F (ROIN) | 0.000689 | 1 | | |
| H=30 (1.00 LT) | oracle | X | 0.000784 | 1.14 [1.11, 1.17] | substantial | 0.0045 |
| H=30 (1.00 LT) | oracle | X+F | 0.00069 | 1 [0.995, 1.01] | negligible | 0.249 |
| H=30 (1.00 LT) | deployable | none | 0.000789 | 0.995 [0.979, 1.01] | negligible | 1 |
| H=30 (1.00 LT) | deployable | A2 (stored) | 0.000789 | 0.995 [0.979, 1.01] | negligible | 1 |
| H=30 (1.00 LT) | deployable | separation | 0.00083 | 1.05 [1.02, 1.07] | needed, size not determined | 0.0065 |
| H=30 (1.00 LT) | deployable | A4 (stored) | 0.00083 | 1.05 [1.02, 1.07] | needed, size not determined | 0.0065 |
| H=30 (1.00 LT) | deployable | RO | 0.000793 | 1 [0.989, 1.01] | negligible | 1 |
| H=30 (1.00 LT) | deployable | R | 0.000789 | 0.994 [0.978, 1.01] | negligible | 1 |
| H=30 (1.00 LT) | deployable | O | 0.000789 | 0.994 [0.979, 1.01] | negligible | 1 |
| H=30 (1.00 LT) | deployable | I | 0.000791 | 0.997 [0.979, 1.01] | negligible | 1 |
| H=30 (1.00 LT) | deployable | N | 0.000794 | 1 [0.989, 1.01] | negligible | 1 |
| H=30 (1.00 LT) | deployable | A5 (stored) | 0.000802 | 1.01 [0.996, 1.03] | negligible | 0.16 |
| H=30 (1.00 LT) | deployable | F (ROIN) | 0.000793 | 1 | | |
| H=30 (1.00 LT) | deployable | X | 0.000789 | 0.994 [0.971, 1.02] | negligible | 1 |
| H=30 (1.00 LT) | deployable | A3 (stored) | 0.000816 | 1.03 [1, 1.06] | undetermined | 0.0385 |
| H=30 (1.00 LT) | deployable | X+F | 0.000786 | 0.991 [0.978, 1] | negligible | 1 |
| H=60 (2.00 LT) | oracle | none | 0.013 | 1.1 [1.07, 1.13] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | separation | 0.0117 | 0.992 [0.979, 1] | negligible | 1 |
| H=60 (2.00 LT) | oracle | RO | 0.0118 | 0.994 [0.985, 1] | negligible | 1 |
| H=60 (2.00 LT) | oracle | R | 0.012 | 1.02 [0.996, 1.04] | negligible | 0.068 |
| H=60 (2.00 LT) | oracle | O | 0.0129 | 1.09 [1.06, 1.13] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | I | 0.0129 | 1.09 [1.06, 1.13] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | N | 0.0128 | 1.08 [1.06, 1.12] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | F (ROIN) | 0.0118 | 1 | | |
| H=60 (2.00 LT) | oracle | X | 0.013 | 1.1 [1.06, 1.13] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | X+F | 0.0118 | 0.999 [0.99, 1.01] | negligible | 1 |
| H=60 (2.00 LT) | deployable | none | 0.0134 | 1.01 [0.996, 1.02] | negligible | 0.112 |
| H=60 (2.00 LT) | deployable | A2 (stored) | 0.0134 | 1.01 [0.997, 1.03] | negligible | 0.0855 |
| H=60 (2.00 LT) | deployable | separation | 0.0134 | 1.01 [0.993, 1.03] | negligible | 0.374 |
| H=60 (2.00 LT) | deployable | A4 (stored) | 0.0134 | 1.01 [0.993, 1.03] | negligible | 0.374 |
| H=60 (2.00 LT) | deployable | RO | 0.0132 | 1 [0.995, 1.01] | negligible | 0.47 |
| H=60 (2.00 LT) | deployable | R | 0.0134 | 1.01 [0.999, 1.03] | negligible | 0.055 |
| H=60 (2.00 LT) | deployable | O | 0.0133 | 1.01 [0.993, 1.02] | negligible | 0.47 |
| H=60 (2.00 LT) | deployable | I | 0.0133 | 1 [0.991, 1.02] | negligible | 0.47 |
| H=60 (2.00 LT) | deployable | N | 0.0134 | 1.01 [1, 1.03] | small | 0.012 |
| H=60 (2.00 LT) | deployable | F (ROIN) | 0.0132 | 1 | | |
| H=60 (2.00 LT) | deployable | X | 0.0133 | 1.01 [0.994, 1.02] | negligible | 0.374 |
| H=60 (2.00 LT) | deployable | A3 (stored) | 0.0135 | 1.02 [1, 1.04] | small | 0.0275 |
| H=60 (2.00 LT) | deployable | X+F | 0.0133 | 1 [0.997, 1.01] | negligible | 0.47 |
| H=120 (4.00 LT) | oracle | none | 0.106 | 1.02 [1.01, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | separation | 0.109 | 1.05 [1.03, 1.07] | needed, size not determined | 0.0045 |
| H=120 (4.00 LT) | oracle | RO | 0.105 | 1.01 [1, 1.01] | small | 0.006 |
| H=120 (4.00 LT) | oracle | R | 0.105 | 1.01 [1, 1.02] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | O | 0.106 | 1.02 [1.01, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | I | 0.106 | 1.02 [1.01, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | N | 0.106 | 1.02 [1.01, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | F (ROIN) | 0.104 | 1 | | |
| H=120 (4.00 LT) | oracle | X | 0.106 | 1.02 [1.01, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | X+F | 0.103 | 0.992 [0.985, 0.999] | lowers | 1 |
| H=120 (4.00 LT) | deployable | none | 0.102 | 1.02 [1.01, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | A2 (stored) | 0.102 | 1.02 [1.01, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | separation | 0.107 | 1.06 [1.04, 1.09] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | A4 (stored) | 0.107 | 1.06 [1.04, 1.09] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | RO | 0.101 | 1.01 [1, 1.01] | small | 0.006 |
| H=120 (4.00 LT) | deployable | R | 0.102 | 1.01 [1, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | O | 0.102 | 1.02 [1.01, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | I | 0.102 | 1.01 [1, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | N | 0.102 | 1.01 [1.01, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | F (ROIN) | 0.101 | 1 | | |
| H=120 (4.00 LT) | deployable | X | 0.102 | 1.01 [1, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | A3 (stored) | 0.105 | 1.05 [1.03, 1.07] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | X+F | 0.1 | 0.995 [0.986, 1] | negligible | 0.952 |

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| horizon | theory gap (upper bound) [CI] | estimation gap [CI] | gap with R estimated | gap with O estimated | gap with I estimated | gap with N estimated |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 1.15e-05 [1.06e-05, 1.23e-05] | 9.21e-06 [5.31e-06, 1.34e-05] | 4.9e-06 [1.01e-06, 8.96e-06] | -9.17e-07 [-4.45e-06, 2.87e-06] | -8.22e-07 [-4.36e-06, 3.02e-06] | 7.95e-07 [-2.82e-06, 4.72e-06] |
| H=15 (0.50 LT) | 1.86e-05 [1.71e-05, 2.01e-05] | 1.98e-05 [1.11e-05, 2.89e-05] | 1.02e-05 [1.9e-06, 1.88e-05] | -1.98e-06 [-9.71e-06, 5.9e-06] | -2.3e-06 [-9.97e-06, 5.56e-06] | 3.1e-07 [-7.26e-06, 8.22e-06] |
| H=30 (1.00 LT) | 6.21e-05 [5.6e-05, 6.92e-05] | 0.000104 [7.06e-05, 0.000141] | 6.57e-05 [3.24e-05, 0.000102] | 3.67e-06 [-2.8e-05, 3.65e-05] | -3.53e-06 [-3.41e-05, 2.79e-05] | 6.75e-06 [-2.52e-05, 3.89e-05] |
| H=60 (2.00 LT) | 0.00268 [0.00234, 0.00305] | 0.00139 [0.000662, 0.00219] | 0.00117 [0.000454, 0.00192] | 0.000118 [-0.000513, 0.00075] | 0.000219 [-0.000414, 0.000848] | 0.000142 [-0.000471, 0.00076] |
| H=120 (4.00 LT) | 0.0278 [0.0261, 0.0296] | -0.00315 [-0.00615, -1.79e-05] | -0.00306 [-0.00604, 3.02e-06] | -0.00399 [-0.00686, -0.00097] | -0.004 [-0.00689, -0.000999] | -0.00397 [-0.00683, -0.000958] |

### Horizon decision (Y = ln min(T_c, H_max))

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED. Pinball loss at tau = 0.5; drop-one ratio at level 1 - 0.05/4; ladder ratio vs F at 1 - 0.05/m; C = Harrell's C (95%); coverage of q_0.1, q_0.5, q_0.9 and the 80% interval below the cap.

| profile | X | pinball ratio [CI] | reading | Holm p | phi [CI] |
|---|---|---|---|---|---|
| oracle | R | 1.01 [1, 1.02] | small | 0.003 | 0.00217 [0.00149, 0.00288] |
| oracle | O | 1.09 [1.06, 1.11] | substantial | 0.002 | 0.00835 [0.00663, 0.00995] |
| oracle | I | 1.21 [1.18, 1.24] | substantial | 0.002 | 0.0242 [0.0218, 0.0267] |
| oracle | N | 1.01 [1.01, 1.02] | small | 0.002 | 0.00459 [0.00353, 0.00566] |
| deployable | R | 1 [0.999, 1.01] | negligible | 0.031 | 0.00138 [0.000888, 0.00189] |
| deployable | O | 1.13 [1.1, 1.15] | substantial | 0.002 | 0.0144 [0.0124, 0.0162] |
| deployable | I | 1.23 [1.2, 1.27] | substantial | 0.002 | 0.0247 [0.0225, 0.0271] |
| deployable | N | 1.01 [0.999, 1.01] | negligible | 0.031 | 0.0033 [0.00261, 0.004] |

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | ratio vs F [CI] | reading | C [CI] | cov 0.1 / 0.5 / 0.9 / 80% |
|---|---|---|---|---|---|---|
| oracle | none | 0.16 | 1.33 [1.28, 1.37] | substantial | 0.5 [0.5, 0.5] | 0.103 / 0.498 / 0.884 / 0.781 |
| oracle | lyapunov | 0.169 | 1.4 [1.35, 1.46] | substantial | 0.63 [0.62, 0.641] | 0.0698 / 0.478 / 0.871 / 0.833 |
| oracle | RO | 0.151 | 1.25 [1.21, 1.29] | substantial | 0.572 [0.561, 0.581] | 0.112 / 0.506 / 0.889 / 0.777 |
| oracle | R | 0.157 | 1.3 [1.26, 1.34] | substantial | 0.522 [0.512, 0.532] | 0.108 / 0.502 / 0.887 / 0.78 |
| oracle | O | 0.155 | 1.28 [1.25, 1.32] | substantial | 0.563 [0.552, 0.572] | 0.11 / 0.496 / 0.885 / 0.775 |
| oracle | I | 0.137 | 1.14 [1.11, 1.17] | substantial | 0.614 [0.605, 0.624] | 0.0993 / 0.495 / 0.881 / 0.782 |
| oracle | N | 0.152 | 1.26 [1.22, 1.31] | substantial | 0.566 [0.557, 0.575] | 0.103 / 0.498 / 0.882 / 0.779 |
| oracle | ROIN | 0.121 | 1 |  | 0.678 [0.669, 0.688] | 0.138 / 0.508 / 0.884 / 0.747 |
| oracle | X | 0.122 | 1.01 [0.971, 1.05] | undetermined | 0.695 [0.686, 0.703] | 0.138 / 0.503 / 0.853 / 0.715 |
| oracle | X+F | 0.0912 | 0.756 [0.733, 0.781] | lowers | 0.77 [0.763, 0.777] | 0.149 / 0.499 / 0.851 / 0.702 |
| oracle | Lyapunov rank (C only) | | | | 0.628 [0.618, 0.638] | |
| deployable | none | 0.16 | 1.38 [1.33, 1.42] | substantial | 0.5 [0.5, 0.5] | 0.103 / 0.498 / 0.884 / 0.781 |
| deployable | lyapunov | 0.171 | 1.47 [1.41, 1.52] | substantial | 0.624 [0.614, 0.635] | 0.0736 / 0.481 / 0.871 / 0.834 |
| deployable | RO | 0.145 | 1.25 [1.22, 1.29] | substantial | 0.603 [0.594, 0.611] | 0.108 / 0.495 / 0.884 / 0.776 |
| deployable | R | 0.158 | 1.36 [1.32, 1.41] | substantial | 0.518 [0.51, 0.528] | 0.107 / 0.499 / 0.884 / 0.777 |
| deployable | O | 0.148 | 1.27 [1.24, 1.31] | substantial | 0.597 [0.587, 0.606] | 0.108 / 0.499 / 0.884 / 0.777 |
| deployable | I | 0.138 | 1.19 [1.15, 1.22] | substantial | 0.614 [0.605, 0.624] | 0.1 / 0.494 / 0.878 / 0.778 |
| deployable | N | 0.153 | 1.32 [1.28, 1.36] | substantial | 0.551 [0.544, 0.559] | 0.102 / 0.5 / 0.885 / 0.783 |
| deployable | ROIN | 0.116 | 1 |  | 0.694 [0.685, 0.702] | 0.123 / 0.5 / 0.864 / 0.741 |
| deployable | X | 0.122 | 1.05 [1.01, 1.09] | needed, size not determined | 0.694 [0.686, 0.702] | 0.131 / 0.503 / 0.862 / 0.732 |
| deployable | X+F | 0.0905 | 0.779 [0.756, 0.802] | lowers | 0.769 [0.762, 0.775] | 0.141 / 0.494 / 0.859 / 0.718 |
| deployable | Lyapunov rank (C only) | | | | 0.623 [0.613, 0.633] | |

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| profile | pair | Delta [CI] | Holm p | detected |
|---|---|---|---|---|
| oracle | RO | -2.29e-05 [-0.000772, 0.000713] | 0.529 | False |
| oracle | RI (primary) | 0.00145 [0.000339, 0.00251] | 0.003 | True |
| oracle | RN | 0.000298 [4.45e-06, 0.000592] | 0.016 | True |
| oracle | OI (primary) | 0.00798 [0.00571, 0.01] | 0.003 | True |
| oracle | ON | 0.000627 [-4.17e-05, 0.00134] | 0.016 | True |
| oracle | IN | 0.00151 [4.71e-05, 0.00278] | 0.016 | True |
| deployable | RO | 0.000308 [-0.000316, 0.000952] | 0.258 | False |
| deployable | RI (primary) | 0.00235 [0.00125, 0.00347] | 0.003 | True |
| deployable | RN | 7.73e-05 [-0.00024, 0.000421] | 0.503 | False |
| deployable | OI (primary) | 0.0104 [0.00842, 0.0123] | 0.003 | True |
| deployable | ON | -0.00113 [-0.00261, 0.000134] | 0.988 | False |
| deployable | IN | 0.00117 [0.00016, 0.00208] | 0.004 | True |

## chua

**PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.**

| check | result |
|---|---|
| (f1) state_mse from per-draw errors, max rel diff | A0 0.0e+00, A1 0.0e+00, A2 0.0e+00, A3 0.0e+00, A4 0.0e+00, A5 0.0e+00 (within 1e-12: True) |
| (g) WU-0039b (b1), (b2) rows reproduced | drop-N: True, all rows: True |
| separation formula on F-hat vs stored A4 at H_ref, max abs | 2.22e-16 |
| T_c: T = 1 / e_(T-1) = theta (train, test) | 2/0, 2/0 |
| (f2) dependence bias, deployable rows (reported, not gating) | 131 rows; 42 flagged: H=8 N: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0089, z 0.307; H=8 RI: dependence bias detectable (interval excludes 0), t1+t2 / V -0.0172, z -0.608; H=8 RN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.00814, z 0.146; H=8 IN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0284, z 1.19; H=8 RON: dependence bias detectable (interval excludes 0), t1+t2 / V 0.00819, z 0.256; H=8 X: dependence bias detectable (interval excludes 0), t1+t2 / V -0.00272, z 0.044; H=8 swap-R: dependence bias detectable (interval excludes 0), t1+t2 / V 0.00373, z -0.439; H=8 swap-I: dependence bias detectable (interval excludes 0), t1+t2 / V -0.0796, z -0.54; H=8 swap-N: dependence bias detectable (interval excludes 0), t1+t2 / V 0.00433, z -0.419; H=15 N: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0293, z 3; H=15 RN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0254, z 3.36; H=15 ON: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0242, z 3.33 ... |

### A. Allocation: drop-one and Shapley

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED. MSE ratio MSE(F without X)/MSE(F) at level 1 - 0.05/4 (reading by the 1.05 table, with the n_eff guard); excess ratio L_A(F without X)/L_A(F) and Holm p (Delta MSE > 0) are estimates. phi = Shapley share of L_A (95%). Oracle rows: moment form; deployable rows: realized per draw.

| horizon | profile | X | MSE ratio [CI] | reading | excess ratio | Holm p | phi_X [95% CI] | share |
|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | R | 0.993 [0.916, 1.06] | undetermined (n_eff < 50) | 0.985 | 1 | -1.23e-05 [-8.92e-05, 4.95e-05] | -0.0823 |
| H=8 (0.27 LT) | oracle | O | 0.695 [0.445, 1] | undetermined (n_eff < 50) | 0.366 | 1 | 1.01e-06 [-0.000316, 0.000272] | 0.00676 |
| H=8 (0.27 LT) | oracle | I | 0.766 [0.57, 1.09] | undetermined (n_eff < 50) | 0.513 | 1 | 8.7e-05 [-4.97e-05, 0.000286] | 0.583 |
| H=8 (0.27 LT) | oracle | N | 0.99 [0.969, 1.02] | undetermined (n_eff < 50) | 0.979 | 1 | 7.35e-05 [1.09e-05, 0.000144] | 0.492 |
| H=8 (0.27 LT) | deployable | R | 0.867 [0.663, 1.06] | undetermined (n_eff < 50) | 0.756 | 1 | -3.66e-07 [-0.000252, 0.000325] | -0.0053 |
| H=8 (0.27 LT) | deployable | O | 0.984 [0.955, 1.01] | undetermined (n_eff < 50) | 0.971 | 1 | 2.87e-05 [-0.000128, 0.000144] | 0.416 |
| H=8 (0.27 LT) | deployable | I | 1.05 [0.954, 1.15] | undetermined (n_eff < 50) | 1.1 | 0.834 | 5.99e-05 [-3.88e-05, 0.000173] | 0.867 |
| H=8 (0.27 LT) | deployable | N | 0.802 [0.546, 1.32] | undetermined (n_eff < 50) | 0.638 | 1 | -1.92e-05 [-0.000279, 0.000221] | -0.278 |
| H=15 (0.50 LT) | oracle | R | 1.27 [1.04, 1.89] | needed, size not determined | 2.88 | 0.002 | 0.000308 [9.05e-05, 0.000687] | 0.604 |
| H=15 (0.50 LT) | oracle | O | 1.15 [1.05, 1.31] | substantial | 2.07 | 0.002 | 0.000245 [-4.9e-05, 0.000596] | 0.482 |
| H=15 (0.50 LT) | oracle | I | 1.02 [1, 1.04] | negligible | 1.14 | 0.018 | -6.53e-05 [-0.000241, 4.12e-05] | -0.128 |
| H=15 (0.50 LT) | oracle | N | 1.01 [0.984, 1.05] | negligible | 1.09 | 0.173 | 2.15e-05 [-6.27e-05, 0.0001] | 0.0423 |
| H=15 (0.50 LT) | deployable | R | 0.956 [0.901, 1.01] | undetermined (n_eff < 50) | 0.857 | 1 | -3.07e-05 [-0.00013, 6.56e-05] | 0.141 |
| H=15 (0.50 LT) | deployable | O | 0.998 [0.949, 1.05] | undetermined (n_eff < 50) | 0.992 | 1 | -1.25e-05 [-0.000235, 0.000168] | 0.0576 |
| H=15 (0.50 LT) | deployable | I | 1.01 [0.964, 1.05] | undetermined (n_eff < 50) | 1.03 | 1 | -1.61e-05 [-9.52e-05, 7.13e-05] | 0.0743 |
| H=15 (0.50 LT) | deployable | N | 0.932 [0.833, 1.03] | undetermined (n_eff < 50) | 0.779 | 1 | -0.000158 [-0.000477, 8.46e-05] | 0.727 |
| H=30 (1.00 LT) | oracle | R | 1.05 [1.02, 1.08] | undetermined (n_eff < 50) | 1.17 | 0.002 | 0.000741 [0.000238, 0.00112] | 0.674 |
| H=30 (1.00 LT) | oracle | O | 1.01 [0.984, 1.06] | undetermined (n_eff < 50) | 1.05 | 0.263 | 0.000161 [-0.000129, 0.000462] | 0.147 |
| H=30 (1.00 LT) | oracle | I | 0.985 [0.969, 0.997] | undetermined (n_eff < 50) | 0.948 | 1 | -4.14e-05 [-0.000151, 5.57e-05] | -0.0377 |
| H=30 (1.00 LT) | oracle | N | 1.01 [0.999, 1.02] | undetermined (n_eff < 50) | 1.03 | 0.06 | 0.000238 [0.000116, 0.000363] | 0.217 |
| H=30 (1.00 LT) | deployable | R | 1.01 [0.967, 1.06] | undetermined | 1.02 | 0.307 | 0.000195 [-8.49e-05, 0.000457] | 0.288 |
| H=30 (1.00 LT) | deployable | O | 1.02 [0.999, 1.03] | negligible | 1.04 | 0.032 | 0.000158 [-0.000161, 0.00051] | 0.234 |
| H=30 (1.00 LT) | deployable | I | 1.01 [1, 1.02] | negligible | 1.02 | 0.032 | 0.000186 [9.24e-05, 0.000299] | 0.276 |
| H=30 (1.00 LT) | deployable | N | 1.01 [0.993, 1.02] | negligible | 1.01 | 0.307 | 0.000137 [-0.000186, 0.00045] | 0.202 |
| H=60 (2.00 LT) | oracle | R | 1.05 [1.02, 1.07] | needed, size not determined | 1.15 | 0.002 | 0.00959 [0.00635, 0.0127] | 0.793 |
| H=60 (2.00 LT) | oracle | O | 0.999 [0.991, 1.01] | negligible | 0.997 | 0.611 | 0.000331 [-0.000817, 0.0015] | 0.0274 |
| H=60 (2.00 LT) | oracle | I | 1 [1, 1] | negligible | 1 | 0.141 | 0.000551 [-2.42e-05, 0.0011] | 0.0456 |
| H=60 (2.00 LT) | oracle | N | 1 [0.999, 1.01] | negligible | 1.01 | 0.0855 | 0.00162 [0.000804, 0.00247] | 0.134 |
| H=60 (2.00 LT) | deployable | R | 0.999 [0.988, 1.01] | negligible | 0.997 | 1 | 8.99e-05 [-0.00146, 0.00165] | 0.0278 |
| H=60 (2.00 LT) | deployable | O | 1 [0.994, 1.01] | negligible | 1.01 | 0.652 | 0.0013 [2.65e-05, 0.0026] | 0.403 |
| H=60 (2.00 LT) | deployable | I | 1 [0.998, 1.01] | negligible | 1.01 | 0.256 | 0.00109 [4.14e-05, 0.00213] | 0.336 |
| H=60 (2.00 LT) | deployable | N | 1 [0.998, 1] | negligible | 0.999 | 1 | 0.000754 [-0.000116, 0.00166] | 0.233 |
| H=120 (4.00 LT) | oracle | R | 1.02 [1.01, 1.02] | small | 1.06 | 0.002 | 0.0113 [0.00812, 0.0146] | 0.604 |
| H=120 (4.00 LT) | oracle | O | 1 [0.999, 1] | negligible | 1.01 | 0.105 | 0.00127 [-0.0001, 0.00262] | 0.0675 |
| H=120 (4.00 LT) | oracle | I | 1 [1, 1.01] | small | 1.02 | 0.002 | 0.00433 [0.00278, 0.00591] | 0.231 |
| H=120 (4.00 LT) | oracle | N | 1 [1, 1] | negligible | 1 | 0.475 | 0.00183 [0.00094, 0.00278] | 0.0976 |
| H=120 (4.00 LT) | deployable | R | 1 [0.997, 1.01] | negligible | 1.01 | 0.243 | 0.00262 [0.000161, 0.00503] | 0.223 |
| H=120 (4.00 LT) | deployable | O | 1 [0.997, 1.01] | negligible | 1.01 | 0.313 | 0.00156 [-0.000619, 0.00389] | 0.133 |
| H=120 (4.00 LT) | deployable | I | 1.01 [1, 1.01] | small | 1.03 | 0.01 | 0.00578 [0.00329, 0.00809] | 0.492 |
| H=120 (4.00 LT) | deployable | N | 1 [0.999, 1] | negligible | 1 | 0.313 | 0.00178 [0.000788, 0.00268] | 0.152 |

### A. Allocation: summary per horizon

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED. n_eff = Kish size of kappa on the test states; G = 1 - L_A(rule)/L_A(constant), estimate (95%).

| horizon | profile | n_eff(kappa) | G(F) [CI] | G(separation) | MSE(F)/MSE(sep) [CI] | reading | settings (A) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 77.2 | 0.263 [-0.476, 0.671] | 0.82 | 1.57 [1.18, 2.16] | undetermined (n_eff < 50) | F: low; qn 7, mid 2, low 6 |
| H=8 (0.27 LT) | deployable | 77.2 | 0.113 [-0.054, 0.377] | 0.207 | 1.06 [0.861, 1.41] | undetermined (n_eff < 50) | F: low; qn 8, mid 0, low 7 |
| H=15 (0.50 LT) | oracle | 71.3 | 0.567 [0.407, 0.688] | 0.445 | 0.961 [0.914, 1] | negligible | F: qn; qn 5, mid 2, low 8 |
| H=15 (0.50 LT) | deployable | 71.3 | -0.266 [-0.805, 0.0684] | -0.0107 | 1.07 [0.959, 1.19] | undetermined (n_eff < 50) | F: mid; qn 3, mid 4, low 8 |
| H=30 (1.00 LT) | oracle | 190 | 0.204 [0.137, 0.272] | 0.239 | 1.01 [0.991, 1.04] | undetermined (n_eff < 50) | F: low; qn 0, mid 0, low 15 |
| H=30 (1.00 LT) | deployable | 190 | 0.0949 [0.0436, 0.169] | 0.0503 | 0.982 [0.957, 1] | negligible | F: low; qn 0, mid 2, low 13 |
| H=60 (2.00 LT) | oracle | 836 | 0.175 [0.123, 0.222] | 0.142 | 0.988 [0.978, 0.999] | lowers | F: low; qn 0, mid 0, low 15 |
| H=60 (2.00 LT) | deployable | 836 | 0.0534 [0.0161, 0.095] | -0.0277 | 0.974 [0.962, 0.986] | lowers | F: low; qn 0, mid 1, low 14 |
| H=120 (4.00 LT) | oracle | 2.07e+03 | 0.101 [0.0808, 0.122] | -0.0667 | 0.954 [0.945, 0.963] | lowers | F: low; qn 0, mid 0, low 15 |
| H=120 (4.00 LT) | deployable | 2.07e+03 | 0.0647 [0.0382, 0.0912] | -0.128 | 0.949 [0.938, 0.961] | lowers | F: mid; qn 0, mid 4, low 11 |

### B. Allocation: pairwise interactions (logit u, interior states)

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED. Delta = L(additive) - L(additive + pair) on the test states, models fixed; level 1 - 0.05/6; Holm over the six pairs. R x I and O x I are primary.

| horizon | profile | pair | Delta [CI] | Holm p | reading | loss ratio reading |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | RI (primary) | 0.00437 [-0.0186, 0.0276] | 0.915 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | OI (primary) | 0.0113 [-0.00904, 0.0324] | 0.31 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | RO | 0.0369 [-0.00151, 0.0769] | 0.035 | interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | RN | 0.0364 [0.000377, 0.0725] | 0.024 | interaction gain detected | small |
| H=8 (0.27 LT) | oracle | ON | -0.0137 [-0.0552, 0.0271] | 0.915 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | IN | 0.0029 [-0.0182, 0.0245] | 0.915 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RI (primary) | 0.00905 [-0.013, 0.0338] | 0.772 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | OI (primary) | 0.000363 [-0.0201, 0.0225] | 0.97 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RO | 0.028 [-0.00753, 0.063] | 0.105 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RN | 0.00712 [-0.0172, 0.0318] | 0.834 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | ON | -0.00456 [-0.0251, 0.0186] | 0.97 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | IN | 0.00245 [-0.00969, 0.015] | 0.933 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | RI (primary) | 0.00857 [-0.0143, 0.0308] | 0.155 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | OI (primary) | 0.0473 [0.0154, 0.0814] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | oracle | RO | 0.0846 [0.0427, 0.128] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | oracle | RN | 0.0264 [-0.000173, 0.0552] | 0.022 | interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | ON | 0.0309 [-0.00471, 0.0686] | 0.024 | interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | IN | 0.0199 [-0.00161, 0.0421] | 0.024 | interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | RI (primary) | 0.0291 [-0.00131, 0.0598] | 0.03 | interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | OI (primary) | 0.0359 [-0.00149, 0.0737] | 0.03 | interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | RO | 0.0625 [0.028, 0.103] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | deployable | RN | 0.0114 [-0.00728, 0.0288] | 0.047 | interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | ON | 0.0196 [-0.00436, 0.0433] | 0.031 | interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | IN | 0.0153 [-0.000675, 0.0297] | 0.03 | interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | RI (primary) | 0.0256 [-0.0278, 0.0758] | 0.116 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | OI (primary) | 0.0633 [0.0286, 0.099] | 0.003 | interaction gain detected | small |
| H=30 (1.00 LT) | oracle | RO | 0.0525 [0.00316, 0.0968] | 0.01 | interaction gain detected | small |
| H=30 (1.00 LT) | oracle | RN | 0.0266 [-0.00587, 0.0593] | 0.057 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | ON | 0.0283 [-0.00583, 0.0626] | 0.057 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | IN | 0.0272 [0.00345, 0.0523] | 0.01 | interaction gain detected | small |
| H=30 (1.00 LT) | deployable | RI (primary) | 0.0078 [-0.023, 0.0411] | 0.691 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | OI (primary) | 0.0434 [0.0119, 0.0741] | 0.003 | interaction gain detected | small |
| H=30 (1.00 LT) | deployable | RO | 0.0178 [-0.0124, 0.0461] | 0.27 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | RN | 0.00481 [-0.0126, 0.0226] | 0.691 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | ON | 0.0176 [-0.00283, 0.0367] | 0.06 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | IN | -0.0114 [-0.0346, 0.0129] | 0.905 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | RI (primary) | 0.0386 [-0.0253, 0.106] | 0.322 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | OI (primary) | 0.119 [0.0444, 0.204] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | oracle | RO | 0.0205 [-0.0518, 0.0904] | 0.556 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | RN | 0.0105 [-0.0407, 0.0579] | 0.556 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | ON | 0.0199 [-0.0285, 0.0725] | 0.556 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | IN | 0.0124 [-0.0234, 0.0497] | 0.556 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | RI (primary) | 0.0542 [0.00148, 0.104] | 0.018 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | OI (primary) | 0.129 [0.0505, 0.211] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | RO | 0.101 [0.0328, 0.175] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | RN | 0.0208 [-0.0118, 0.0494] | 0.148 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | ON | 0.0103 [-0.024, 0.0491] | 0.471 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | IN | -0.000372 [-0.0313, 0.0314] | 0.521 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RI (primary) | 0.0231 [-0.0247, 0.0677] | 0.471 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | OI (primary) | 0.0181 [-0.0183, 0.0512] | 0.485 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RO | -0.011 [-0.0443, 0.0241] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RN | 0.00172 [-0.0317, 0.0331] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | ON | -0.0189 [-0.0713, 0.0326] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | IN | -0.0287 [-0.0799, 0.0181] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RI (primary) | 0.0111 [-0.0107, 0.0339] | 0.348 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | OI (primary) | 0.0461 [0.00733, 0.0882] | 0.009 | interaction gain detected | small |
| H=120 (4.00 LT) | deployable | RO | 0.00381 [-0.0322, 0.0379] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RN | 0.00805 [-0.00596, 0.0216] | 0.342 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | ON | 0.00439 [-0.0284, 0.0361] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | IN | -0.0201 [-0.0554, 0.0201] | 1 | no interaction gain detected | negligible |

### D. Allocation ladder (rung against the full profile)

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED. MSE ratio MSE(rung)/MSE(F) at level 1 - 0.05/m (m rungs); Holm p for Delta MSE > 0. Theory gap L_A(oracle F) is an upper bound; estimation gap = L_A(deployable F) - L_A(oracle F) (95%).

| horizon | profile | rung | MSE | MSE ratio vs F [CI] | reading | Holm p |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | none | 0.00102 | 1.17 [0.665, 1.96] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | separation | 0.000554 | 0.637 [0.398, 0.92] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | RO | 0.000792 | 0.91 [0.643, 1.14] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | R | 0.00103 | 1.19 [0.695, 2.27] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | O | 0.0008 | 0.919 [0.679, 1.12] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | I | 0.000619 | 0.711 [0.438, 1.04] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | N | 0.000924 | 1.06 [0.528, 2.22] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | F (ROIN) | 0.000871 | 1 | | |
| H=8 (0.27 LT) | oracle | X | 0.000751 | 0.862 [0.445, 1.7] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | X+F | 0.000697 | 0.8 [0.6, 1.02] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | none | 0.00106 | 1.07 [0.924, 1.28] | undetermined (n_eff < 50) | 0.877 |
| H=8 (0.27 LT) | deployable | A2 (stored) | 0.00142 | 1.42 [1.03, 1.95] | undetermined (n_eff < 50) | 0.006 |
| H=8 (0.27 LT) | deployable | separation | 0.000938 | 0.942 [0.65, 1.24] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | A4 (stored) | 0.000938 | 0.942 [0.65, 1.24] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | RO | 0.00094 | 0.944 [0.65, 1.83] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | R | 0.0011 | 1.11 [0.493, 2.38] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | O | 0.00119 | 1.2 [0.768, 1.86] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | I | 0.00118 | 1.18 [0.852, 1.5] | undetermined (n_eff < 50) | 0.745 |
| H=8 (0.27 LT) | deployable | N | 0.0011 | 1.11 [0.981, 1.2] | undetermined (n_eff < 50) | 0.126 |
| H=8 (0.27 LT) | deployable | F (ROIN) | 0.000996 | 1 | | |
| H=8 (0.27 LT) | deployable | X | 0.000835 | 0.838 [0.636, 1.02] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | A3 (stored) | 0.000911 | 0.914 [0.65, 1.18] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | X+F | 0.00085 | 0.854 [0.652, 1.04] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | oracle | none | 0.00321 | 1.19 [1.08, 1.38] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | separation | 0.00282 | 1.04 [0.982, 1.12] | undetermined | 0.061 |
| H=15 (0.50 LT) | oracle | RO | 0.00281 | 1.04 [0.996, 1.09] | undetermined | 0.024 |
| H=15 (0.50 LT) | oracle | R | 0.0032 | 1.18 [1.07, 1.35] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | O | 0.00305 | 1.13 [1.06, 1.21] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | I | 0.00326 | 1.2 [1.08, 1.4] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | N | 0.00334 | 1.23 [1.1, 1.44] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | F (ROIN) | 0.00271 | 1 | | |
| H=15 (0.50 LT) | oracle | X | 0.00314 | 1.16 [1.08, 1.26] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | X+F | 0.00275 | 1.02 [0.988, 1.05] | negligible | 0.061 |
| H=15 (0.50 LT) | deployable | none | 0.00313 | 0.935 [0.83, 1.05] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | A2 (stored) | 0.00337 | 1.01 [0.894, 1.14] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | separation | 0.00314 | 0.938 [0.789, 1.1] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | A4 (stored) | 0.00314 | 0.938 [0.789, 1.1] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | RO | 0.00313 | 0.934 [0.819, 1.04] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | R | 0.00322 | 0.962 [0.856, 1.07] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | O | 0.00344 | 1.03 [0.815, 1.42] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | I | 0.00329 | 0.981 [0.865, 1.11] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | N | 0.00346 | 1.03 [0.955, 1.11] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | F (ROIN) | 0.00335 | 1 | | |
| H=15 (0.50 LT) | deployable | X | 0.00307 | 0.915 [0.803, 1.02] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | A3 (stored) | 0.00306 | 0.912 [0.781, 1.06] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | X+F | 0.00315 | 0.941 [0.837, 1.05] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | none | 0.0161 | 1.07 [1.03, 1.11] | undetermined (n_eff < 50) | 0.0045 |
| H=30 (1.00 LT) | oracle | separation | 0.0148 | 0.988 [0.951, 1.02] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | RO | 0.015 | 1 [0.978, 1.02] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | R | 0.0154 | 1.03 [0.995, 1.07] | undetermined (n_eff < 50) | 0.058 |
| H=30 (1.00 LT) | oracle | O | 0.016 | 1.07 [1.03, 1.12] | undetermined (n_eff < 50) | 0.0045 |
| H=30 (1.00 LT) | oracle | I | 0.016 | 1.07 [1.03, 1.1] | undetermined (n_eff < 50) | 0.0045 |
| H=30 (1.00 LT) | oracle | N | 0.0159 | 1.06 [1.02, 1.09] | undetermined (n_eff < 50) | 0.0045 |
| H=30 (1.00 LT) | oracle | F (ROIN) | 0.015 | 1 | | |
| H=30 (1.00 LT) | oracle | X | 0.0164 | 1.1 [1.04, 1.15] | undetermined (n_eff < 50) | 0.0045 |
| H=30 (1.00 LT) | oracle | X+F | 0.015 | 1 [0.991, 1.01] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | deployable | none | 0.0178 | 1.04 [1.01, 1.07] | needed, size not determined | 0.0065 |
| H=30 (1.00 LT) | deployable | A2 (stored) | 0.0178 | 1.04 [1.01, 1.07] | needed, size not determined | 0.0065 |
| H=30 (1.00 LT) | deployable | separation | 0.0175 | 1.02 [0.99, 1.06] | undetermined | 0.147 |
| H=30 (1.00 LT) | deployable | A4 (stored) | 0.0175 | 1.02 [0.99, 1.06] | undetermined | 0.147 |
| H=30 (1.00 LT) | deployable | RO | 0.0173 | 1.01 [0.994, 1.03] | negligible | 0.147 |
| H=30 (1.00 LT) | deployable | R | 0.0177 | 1.03 [1.01, 1.06] | needed, size not determined | 0.0065 |
| H=30 (1.00 LT) | deployable | O | 0.0177 | 1.03 [1, 1.07] | needed, size not determined | 0.009 |
| H=30 (1.00 LT) | deployable | I | 0.0177 | 1.03 [0.997, 1.06] | undetermined | 0.0385 |
| H=30 (1.00 LT) | deployable | N | 0.0176 | 1.02 [0.994, 1.06] | undetermined | 0.096 |
| H=30 (1.00 LT) | deployable | A5 (stored) | 0.0177 | 1.03 [1, 1.06] | needed, size not determined | 0.02 |
| H=30 (1.00 LT) | deployable | F (ROIN) | 0.0172 | 1 | | |
| H=30 (1.00 LT) | deployable | X | 0.0179 | 1.04 [1.01, 1.07] | needed, size not determined | 0.0065 |
| H=30 (1.00 LT) | deployable | A3 (stored) | 0.0175 | 1.02 [0.99, 1.05] | undetermined | 0.147 |
| H=30 (1.00 LT) | deployable | X+F | 0.0175 | 1.02 [0.97, 1.08] | undetermined | 0.147 |
| H=60 (2.00 LT) | oracle | none | 0.195 | 1.07 [1.04, 1.1] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | separation | 0.185 | 1.01 [0.997, 1.03] | negligible | 0.024 |
| H=60 (2.00 LT) | oracle | RO | 0.184 | 1 [1, 1.01] | negligible | 0.016 |
| H=60 (2.00 LT) | oracle | R | 0.185 | 1.01 [1, 1.02] | negligible | 0.016 |
| H=60 (2.00 LT) | oracle | O | 0.194 | 1.06 [1.03, 1.09] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | I | 0.194 | 1.06 [1.03, 1.09] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | N | 0.192 | 1.05 [1.02, 1.08] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | F (ROIN) | 0.183 | 1 | | |
| H=60 (2.00 LT) | oracle | X | 0.191 | 1.05 [1.02, 1.08] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | X+F | 0.182 | 0.997 [0.986, 1.01] | negligible | 0.783 |
| H=60 (2.00 LT) | deployable | none | 0.186 | 1.02 [0.999, 1.04] | negligible | 0.0495 |
| H=60 (2.00 LT) | deployable | A2 (stored) | 0.186 | 1.02 [1, 1.04] | negligible | 0.0495 |
| H=60 (2.00 LT) | deployable | separation | 0.188 | 1.03 [1.01, 1.04] | small | 0.006 |
| H=60 (2.00 LT) | deployable | A4 (stored) | 0.188 | 1.03 [1.01, 1.04] | small | 0.006 |
| H=60 (2.00 LT) | deployable | RO | 0.184 | 1 [0.998, 1.01] | negligible | 0.196 |
| H=60 (2.00 LT) | deployable | R | 0.186 | 1.02 [1, 1.03] | small | 0.006 |
| H=60 (2.00 LT) | deployable | O | 0.185 | 1.01 [0.993, 1.02] | negligible | 0.285 |
| H=60 (2.00 LT) | deployable | I | 0.185 | 1.01 [0.989, 1.03] | negligible | 0.486 |
| H=60 (2.00 LT) | deployable | N | 0.185 | 1.01 [0.995, 1.02] | negligible | 0.196 |
| H=60 (2.00 LT) | deployable | F (ROIN) | 0.183 | 1 | | |
| H=60 (2.00 LT) | deployable | X | 0.181 | 0.989 [0.968, 1.01] | negligible | 1 |
| H=60 (2.00 LT) | deployable | A3 (stored) | 0.181 | 0.989 [0.964, 1.01] | negligible | 1 |
| H=60 (2.00 LT) | deployable | X+F | 0.179 | 0.979 [0.959, 0.999] | lowers | 1 |
| H=120 (4.00 LT) | oracle | none | 0.664 | 1.03 [1.02, 1.04] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | separation | 0.676 | 1.05 [1.03, 1.06] | needed, size not determined | 0.0045 |
| H=120 (4.00 LT) | oracle | RO | 0.648 | 1 [1, 1.01] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | R | 0.651 | 1.01 [1, 1.01] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | O | 0.662 | 1.03 [1.02, 1.04] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | I | 0.658 | 1.02 [1.01, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | N | 0.659 | 1.02 [1.01, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | F (ROIN) | 0.645 | 1 | | |
| H=120 (4.00 LT) | oracle | X | 0.661 | 1.02 [1.01, 1.04] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | X+F | 0.645 | 1 [0.999, 1] | negligible | 0.676 |
| H=120 (4.00 LT) | deployable | none | 0.66 | 1.02 [1.01, 1.03] | small | 0.006 |
| H=120 (4.00 LT) | deployable | A2 (stored) | 0.66 | 1.02 [1.01, 1.03] | small | 0.006 |
| H=120 (4.00 LT) | deployable | separation | 0.683 | 1.05 [1.04, 1.07] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | A4 (stored) | 0.683 | 1.05 [1.04, 1.07] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | RO | 0.653 | 1.01 [1, 1.01] | small | 0.006 |
| H=120 (4.00 LT) | deployable | R | 0.656 | 1.01 [1, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | O | 0.658 | 1.02 [1.01, 1.03] | small | 0.006 |
| H=120 (4.00 LT) | deployable | I | 0.652 | 1.01 [0.998, 1.02] | negligible | 0.028 |
| H=120 (4.00 LT) | deployable | N | 0.656 | 1.01 [1, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | F (ROIN) | 0.648 | 1 | | |
| H=120 (4.00 LT) | deployable | X | 0.658 | 1.02 [1, 1.03] | small | 0.006 |
| H=120 (4.00 LT) | deployable | A3 (stored) | 0.677 | 1.04 [1.03, 1.06] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | X+F | 0.647 | 0.999 [0.993, 1] | negligible | 0.722 |

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| horizon | theory gap (upper bound) [CI] | estimation gap [CI] | gap with R estimated | gap with O estimated | gap with I estimated | gap with N estimated |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 0.000419 [0.000206, 0.000746] | 0.000125 [-0.000332, 0.000688] | -1.16e-05 [-4.98e-05, 2.77e-05] | -0.000304 [-0.000644, -6.87e-05] | -0.000208 [-0.000432, -5.69e-06] | -7.72e-05 [-0.000158, -1.32e-05] |
| H=15 (0.50 LT) | 0.000389 [0.000315, 0.000468] | 0.000646 [7.05e-05, 0.0013] | 0.000175 [-0.000255, 0.000641] | 0.000234 [-0.000233, 0.000743] | 0.000156 [-0.000251, 0.000641] | 0.000204 [-0.000218, 0.000671] |
| H=30 (1.00 LT) | 0.00427 [0.00322, 0.00556] | 0.00218 [-0.000739, 0.00517] | 0.0019 [-0.000911, 0.00474] | 0.00144 [-0.00136, 0.00429] | 0.00132 [-0.00149, 0.00419] | 0.00137 [-0.00142, 0.00423] |
| H=60 (2.00 LT) | 0.057 [0.0515, 0.0622] | 0.000276 [-0.01, 0.0106] | -0.000297 [-0.0106, 0.0099] | -0.00877 [-0.0187, 0.000573] | -0.009 [-0.0187, 0.000314] | -0.00865 [-0.0184, 0.00074] |
| H=120 (4.00 LT) | 0.167 [0.159, 0.175] | 0.00287 [-0.0111, 0.0174] | 0.00415 [-0.00983, 0.0185] | -0.0049 [-0.0186, 0.00946] | -0.00521 [-0.019, 0.00907] | -0.00477 [-0.0186, 0.00962] |

### Horizon decision (Y = ln min(T_c, H_max))

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED. Pinball loss at tau = 0.5; drop-one ratio at level 1 - 0.05/4; ladder ratio vs F at 1 - 0.05/m; C = Harrell's C (95%); coverage of q_0.1, q_0.5, q_0.9 and the 80% interval below the cap.

| profile | X | pinball ratio [CI] | reading | Holm p | phi [CI] |
|---|---|---|---|---|---|
| oracle | R | 1.02 [1.01, 1.03] | small | 0.002 | 0.00304 [0.00212, 0.0039] |
| oracle | O | 1.07 [1.05, 1.09] | substantial | 0.002 | 0.0142 [0.0122, 0.016] |
| oracle | I | 1.26 [1.22, 1.3] | substantial | 0.002 | 0.0459 [0.0415, 0.0502] |
| oracle | N | 1.01 [0.997, 1.02] | negligible | 0.029 | 0.00364 [0.00255, 0.00476] |
| deployable | R | 1.01 [1, 1.02] | small | 0.002 | 0.00196 [0.00117, 0.00276] |
| deployable | O | 1.08 [1.06, 1.1] | substantial | 0.002 | 0.0178 [0.0154, 0.0201] |
| deployable | I | 1.22 [1.19, 1.26] | substantial | 0.002 | 0.0423 [0.0384, 0.0462] |
| deployable | N | 1 [0.994, 1.01] | negligible | 0.497 | 0.00337 [0.00261, 0.00412] |

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | ratio vs F [CI] | reading | C [CI] | cov 0.1 / 0.5 / 0.9 / 80% |
|---|---|---|---|---|---|---|
| oracle | none | 0.225 | 1.42 [1.37, 1.48] | substantial | 0.5 [0.5, 0.5] | 0.102 / 0.498 / 0.895 / 0.793 |
| oracle | lyapunov | 0.263 | 1.65 [1.59, 1.72] | substantial | 0.672 [0.663, 0.681] | 0.0904 / 0.457 / 0.836 / 0.802 |
| oracle | RO | 0.202 | 1.27 [1.23, 1.32] | substantial | 0.63 [0.62, 0.64] | 0.111 / 0.499 / 0.898 / 0.787 |
| oracle | R | 0.223 | 1.41 [1.35, 1.46] | substantial | 0.542 [0.533, 0.553] | 0.109 / 0.51 / 0.886 / 0.777 |
| oracle | O | 0.209 | 1.32 [1.27, 1.36] | substantial | 0.611 [0.601, 0.621] | 0.103 / 0.495 / 0.897 / 0.793 |
| oracle | I | 0.174 | 1.1 [1.07, 1.12] | substantial | 0.685 [0.677, 0.694] | 0.0968 / 0.492 / 0.893 / 0.796 |
| oracle | N | 0.219 | 1.38 [1.33, 1.44] | substantial | 0.575 [0.564, 0.584] | 0.106 / 0.498 / 0.897 / 0.791 |
| oracle | ROIN | 0.159 | 1 |  | 0.722 [0.714, 0.73] | 0.139 / 0.499 / 0.888 / 0.749 |
| oracle | X | 0.173 | 1.09 [1.05, 1.14] | needed, size not determined | 0.697 [0.687, 0.706] | 0.141 / 0.496 / 0.849 / 0.708 |
| oracle | X+F | 0.135 | 0.85 [0.828, 0.872] | lowers | 0.769 [0.761, 0.776] | 0.151 / 0.503 / 0.851 / 0.7 |
| oracle | Lyapunov rank (C only) | | | | 0.669 [0.66, 0.679] | |
| deployable | none | 0.225 | 1.41 [1.36, 1.46] | substantial | 0.5 [0.5, 0.5] | 0.102 / 0.498 / 0.895 / 0.793 |
| deployable | lyapunov | 0.264 | 1.65 [1.59, 1.72] | substantial | 0.669 [0.66, 0.678] | 0.0908 / 0.462 / 0.836 / 0.803 |
| deployable | RO | 0.198 | 1.24 [1.2, 1.27] | substantial | 0.628 [0.619, 0.638] | 0.113 / 0.498 / 0.881 / 0.767 |
| deployable | R | 0.225 | 1.4 [1.36, 1.46] | substantial | 0.522 [0.514, 0.53] | 0.103 / 0.505 / 0.893 / 0.79 |
| deployable | O | 0.203 | 1.27 [1.23, 1.31] | substantial | 0.618 [0.608, 0.627] | 0.111 / 0.493 / 0.893 / 0.782 |
| deployable | I | 0.177 | 1.11 [1.08, 1.13] | substantial | 0.68 [0.672, 0.689] | 0.0921 / 0.501 / 0.895 / 0.803 |
| deployable | N | 0.219 | 1.37 [1.32, 1.42] | substantial | 0.574 [0.566, 0.582] | 0.104 / 0.501 / 0.891 / 0.787 |
| deployable | ROIN | 0.16 | 1 |  | 0.717 [0.71, 0.725] | 0.127 / 0.501 / 0.872 / 0.745 |
| deployable | X | 0.171 | 1.07 [1.04, 1.11] | needed, size not determined | 0.698 [0.69, 0.707] | 0.137 / 0.496 / 0.858 / 0.721 |
| deployable | X+F | 0.139 | 0.868 [0.849, 0.888] | lowers | 0.759 [0.752, 0.767] | 0.147 / 0.5 / 0.858 / 0.711 |
| deployable | Lyapunov rank (C only) | | | | 0.664 [0.656, 0.674] | |

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| profile | pair | Delta [CI] | Holm p | detected |
|---|---|---|---|---|
| oracle | RO | 0.00169 [-0.000514, 0.00388] | 0.052 | False |
| oracle | RI (primary) | 0.003 [0.00171, 0.00422] | 0.003 | True |
| oracle | RN | 0.000902 [0.0004, 0.00143] | 0.003 | True |
| oracle | OI (primary) | 0.00737 [0.00466, 0.0101] | 0.003 | True |
| oracle | ON | 0.00164 [0.000761, 0.0025] | 0.003 | True |
| oracle | IN | 0.000747 [-0.000373, 0.00192] | 0.052 | False |
| deployable | RO | 0.00054 [-0.000567, 0.00162] | 0.444 | False |
| deployable | RI (primary) | 0.00105 [-0.000279, 0.00243] | 0.0925 | False |
| deployable | RN | -0.000458 [-0.00101, 0.000186] | 0.974 | False |
| deployable | OI (primary) | 0.00733 [0.00515, 0.00949] | 0.003 | True |
| deployable | ON | 0.000246 [-0.000708, 0.00127] | 0.517 | False |
| deployable | IN | 0.00036 [-0.00046, 0.00126] | 0.444 | False |

