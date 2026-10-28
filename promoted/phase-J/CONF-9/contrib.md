# Phase J contribution study: CONF-9

**PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.** Run `phasej-CONF-9/phasej`; analysis commit `c19ad486b93a2ee96d64ce069ec42fd440428211` (dirty: False). Every reading is an estimate; Shapley shares and interactions are predictive, not causal. Training variance is not in the intervals.

## lorenz63

**PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.**

| check | result |
|---|---|
| (f1) state_mse from per-draw errors, max rel diff | A0 0.0e+00, A1 0.0e+00, A2 0.0e+00, A3 0.0e+00, A4 0.0e+00, A5 0.0e+00 (within 1e-12: True) |
| (g) WU-0039b (b1), (b2) rows reproduced | drop-N: True, all rows: True |
| separation formula on F-hat vs stored A4 at H_ref, max abs | 1.67e-16 |
| T_c: T = 1 / e_(T-1) = theta (train, test) | 6/0, 11/0 |
| (f2) dependence bias, deployable rows (reported, not gating) | 131 rows; 22 flagged: H=8 I: dependence bias detectable (interval excludes 0), t1+t2 / V 0.256, z 0.182; H=8 RI: dependence bias detectable (interval excludes 0), t1+t2 / V 0.263, z -0.305; H=8 OI: dependence bias detectable (interval excludes 0), t1+t2 / V 0.113, z -1.3; H=8 IN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.264, z 0.0725; H=8 ROI: dependence bias detectable (interval excludes 0), t1+t2 / V 0.113, z -1.42; H=8 RIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.259, z -0.35; H=8 OIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0751, z -1.55; H=8 ROIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0938, z -1.58; H=8 swap-R: dependence bias detectable (interval excludes 0), t1+t2 / V 0.00249, z -2.08; H=8 swap-O: dependence bias detectable (interval excludes 0), t1+t2 / V -0.0346, z -2.39; H=8 swap-N: dependence bias detectable (interval excludes 0), t1+t2 / V 0.00169, z -2.21; H=15 O: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0519, z -0.17 ... |

### A. Allocation: drop-one and Shapley

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED. MSE ratio MSE(F without X)/MSE(F) at level 1 - 0.05/4 (reading by the 1.05 table, with the n_eff guard); excess ratio L_A(F without X)/L_A(F) and Holm p (Delta MSE > 0) are estimates. phi = Shapley share of L_A (95%). Oracle rows: moment form; deployable rows: realized per draw.

| horizon | profile | X | MSE ratio [CI] | reading | excess ratio | Holm p | phi_X [95% CI] | share |
|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | R | 1.02 [0.824, 1.33] | undetermined (n_eff < 50) | 1.06 | 0.889 | 0.000593 [0.000106, 0.0012] | 0.0559 |
| H=8 (0.27 LT) | oracle | O | 1.37 [1.04, 2.72] | undetermined (n_eff < 50) | 2.26 | 0.012 | 0.00633 [0.00476, 0.00785] | 0.597 |
| H=8 (0.27 LT) | oracle | I | 1.06 [0.922, 1.39] | undetermined (n_eff < 50) | 1.19 | 0.55 | 0.00404 [0.00219, 0.00639] | 0.381 |
| H=8 (0.27 LT) | oracle | N | 0.816 [0.392, 1.03] | undetermined (n_eff < 50) | 0.381 | 0.986 | -0.000357 [-0.00187, 0.000963] | -0.0337 |
| H=8 (0.27 LT) | deployable | R | 0.975 [0.907, 1.08] | undetermined (n_eff < 50) | 0.966 | 1 | 0.000461 [-0.000708, 0.00147] | 0.507 |
| H=8 (0.27 LT) | deployable | O | 1.16 [0.913, 1.73] | undetermined (n_eff < 50) | 1.21 | 0.27 | 0.00418 [0.00207, 0.00639] | 4.59 |
| H=8 (0.27 LT) | deployable | I | 0.646 [0.307, 1.06] | undetermined (n_eff < 50) | 0.522 | 1 | -0.00449 [-0.0116, 0.000666] | -4.94 |
| H=8 (0.27 LT) | deployable | N | 0.997 [0.931, 1.17] | undetermined (n_eff < 50) | 0.995 | 1 | 0.000767 [-0.00044, 0.00192] | 0.843 |
| H=15 (0.50 LT) | oracle | R | 1.05 [0.965, 1.16] | undetermined (n_eff < 50) | 1.21 | 0.102 | 0.00101 [-0.000659, 0.00237] | 0.0623 |
| H=15 (0.50 LT) | oracle | O | 1.76 [1.29, 2.63] | undetermined (n_eff < 50) | 4.24 | 0.002 | 0.0129 [0.00866, 0.0176] | 0.799 |
| H=15 (0.50 LT) | oracle | I | 1.07 [0.981, 1.21] | undetermined (n_eff < 50) | 1.3 | 0.102 | 0.00273 [0.000724, 0.00436] | 0.169 |
| H=15 (0.50 LT) | oracle | N | 1.08 [0.978, 1.28] | undetermined (n_eff < 50) | 1.36 | 0.102 | -0.000487 [-0.00399, 0.00237] | -0.0302 |
| H=15 (0.50 LT) | deployable | R | 1.11 [0.899, 1.37] | undetermined (n_eff < 50) | 1.2 | 0.157 | 0.00268 [-0.00187, 0.00616] | 0.365 |
| H=15 (0.50 LT) | deployable | O | 1.07 [0.946, 1.23] | undetermined (n_eff < 50) | 1.13 | 0.157 | 0.00154 [-0.000378, 0.00326] | 0.209 |
| H=15 (0.50 LT) | deployable | I | 1.13 [0.966, 1.33] | undetermined (n_eff < 50) | 1.22 | 0.116 | 0.00181 [-0.000645, 0.00376] | 0.247 |
| H=15 (0.50 LT) | deployable | N | 1.12 [0.951, 1.34] | undetermined (n_eff < 50) | 1.21 | 0.144 | 0.00131 [-0.00115, 0.00391] | 0.179 |
| H=30 (1.00 LT) | oracle | R | 0.935 [0.784, 1.09] | undetermined (n_eff < 50) | 0.834 | 1 | -0.00183 [-0.00416, 0.000481] | -0.156 |
| H=30 (1.00 LT) | oracle | O | 1.15 [0.919, 1.46] | undetermined (n_eff < 50) | 1.39 | 0.236 | 0.0118 [0.00733, 0.0161] | 1 |
| H=30 (1.00 LT) | oracle | I | 0.955 [0.789, 1.14] | undetermined (n_eff < 50) | 0.885 | 1 | 0.00301 [0.000106, 0.00537] | 0.256 |
| H=30 (1.00 LT) | oracle | N | 0.892 [0.758, 1.03] | undetermined (n_eff < 50) | 0.725 | 1 | -0.00118 [-0.00382, 0.00102] | -0.1 |
| H=30 (1.00 LT) | deployable | R | 1.12 [1.02, 1.25] | needed, size not determined | 1.25 | 0.01 | 0.0051 [0.00162, 0.00827] | 0.462 |
| H=30 (1.00 LT) | deployable | O | 1.08 [0.981, 1.21] | undetermined | 1.17 | 0.0795 | 0.00271 [-0.000103, 0.00556] | 0.246 |
| H=30 (1.00 LT) | deployable | I | 1.02 [0.915, 1.15] | undetermined | 1.05 | 0.579 | 0.00203 [-0.0018, 0.00518] | 0.184 |
| H=30 (1.00 LT) | deployable | N | 1.01 [0.953, 1.1] | undetermined | 1.03 | 0.579 | 0.00119 [-0.000822, 0.0032] | 0.108 |
| H=60 (2.00 LT) | oracle | R | 1.02 [0.995, 1.04] | negligible | 1.06 | 0.031 | 0.00171 [-0.000522, 0.00376] | 0.11 |
| H=60 (2.00 LT) | oracle | O | 1.09 [1.05, 1.12] | substantial | 1.31 | 0.002 | 0.0107 [0.00697, 0.0142] | 0.689 |
| H=60 (2.00 LT) | oracle | I | 1.02 [0.998, 1.03] | negligible | 1.05 | 0.025 | 0.00202 [0.000946, 0.00309] | 0.13 |
| H=60 (2.00 LT) | oracle | N | 1.02 [1, 1.03] | small | 1.05 | 0.0135 | 0.00113 [-0.000303, 0.00242] | 0.0722 |
| H=60 (2.00 LT) | deployable | R | 1.01 [0.993, 1.03] | negligible | 1.03 | 0.142 | 0.000422 [-0.00112, 0.00187] | 0.0991 |
| H=60 (2.00 LT) | deployable | O | 1.02 [0.996, 1.05] | negligible | 1.06 | 0.036 | 0.00174 [-0.000867, 0.00406] | 0.409 |
| H=60 (2.00 LT) | deployable | I | 1.03 [1.02, 1.05] | needed, size not determined | 1.1 | 0.002 | 0.00348 [0.00211, 0.00491] | 0.818 |
| H=60 (2.00 LT) | deployable | N | 0.991 [0.974, 1.01] | negligible | 0.973 | 0.93 | -0.00139 [-0.00295, 1.99e-05] | -0.326 |
| H=120 (4.00 LT) | oracle | R | 1 [0.99, 1.01] | negligible | 0.999 | 1 | 0.00427 [0.000617, 0.00843] | 0.59 |
| H=120 (4.00 LT) | oracle | O | 0.999 [0.991, 1.01] | negligible | 0.995 | 1 | 0.00171 [-0.000664, 0.00386] | 0.236 |
| H=120 (4.00 LT) | oracle | I | 0.999 [0.992, 1.01] | negligible | 0.996 | 1 | 0.00175 [-0.000772, 0.00426] | 0.242 |
| H=120 (4.00 LT) | oracle | N | 0.998 [0.993, 1] | negligible | 0.992 | 1 | -0.000489 [-0.00223, 0.00121] | -0.0676 |
| H=120 (4.00 LT) | deployable | R | 1 [0.996, 1.01] | negligible | 1 | 0.585 | 0.00371 [0.00135, 0.00615] | 0.421 |
| H=120 (4.00 LT) | deployable | O | 1 [0.999, 1] | negligible | 1 | 0.585 | 0.00155 [-2.97e-05, 0.00306] | 0.176 |
| H=120 (4.00 LT) | deployable | I | 1 [1, 1] | negligible | 1.01 | 0.074 | 0.00243 [0.000669, 0.00418] | 0.276 |
| H=120 (4.00 LT) | deployable | N | 1 [1, 1] | negligible | 1 | 0.451 | 0.00112 [0.000251, 0.00206] | 0.127 |

### A. Allocation: summary per horizon

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED. n_eff = Kish size of kappa on the test states; G = 1 - L_A(rule)/L_A(constant), estimate (95%).

| horizon | profile | n_eff(kappa) | G(F) [CI] | G(separation) | MSE(F)/MSE(sep) [CI] | reading | settings (A) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 66.3 | 0.846 [0.724, 0.944] | 0.791 | 0.904 [0.659, 1.79] | undetermined (n_eff < 50) | F: qn; qn 6, mid 7, low 2 |
| H=8 (0.27 LT) | deployable | 66.3 | 0.0653 [-0.478, 0.518] | -1.15 | 0.51 [0.318, 0.714] | undetermined (n_eff < 50) | F: mid; qn 0, mid 12, low 3 |
| H=15 (0.50 LT) | oracle | 106 | 0.832 [0.719, 0.901] | 0.716 | 0.86 [0.741, 0.959] | undetermined (n_eff < 50) | F: qn; qn 6, mid 3, low 6 |
| H=15 (0.50 LT) | deployable | 106 | 0.346 [0.0686, 0.536] | -0.368 | 0.619 [0.478, 0.827] | undetermined (n_eff < 50) | F: qn; qn 1, mid 10, low 4 |
| H=30 (1.00 LT) | oracle | 180 | 0.412 [0.148, 0.606] | 0.583 | 1.13 [0.997, 1.3] | undetermined (n_eff < 50) | F: low; qn 2, mid 5, low 8 |
| H=30 (1.00 LT) | deployable | 180 | 0.331 [0.164, 0.465] | -0.178 | 0.74 [0.635, 0.875] | lowers | F: qn; qn 6, mid 4, low 5 |
| H=60 (2.00 LT) | oracle | 477 | 0.286 [0.209, 0.352] | 0.183 | 0.961 [0.942, 0.98] | lowers | F: mid; qn 0, mid 8, low 7 |
| H=60 (2.00 LT) | deployable | 477 | 0.075 [0.00461, 0.137] | -0.0667 | 0.949 [0.925, 0.979] | lowers | F: mid; qn 0, mid 6, low 9 |
| H=120 (4.00 LT) | oracle | 1.67e+03 | 0.0285 [0.00112, 0.0555] | -0.244 | 0.925 [0.911, 0.938] | lowers | F: mid; qn 0, mid 4, low 11 |
| H=120 (4.00 LT) | deployable | 1.67e+03 | 0.0348 [0.0211, 0.0488] | -0.148 | 0.948 [0.936, 0.96] | lowers | F: low; qn 0, mid 1, low 14 |

### B. Allocation: pairwise interactions (logit u, interior states)

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED. Delta = L(additive) - L(additive + pair) on the test states, models fixed; level 1 - 0.05/6; Holm over the six pairs. R x I and O x I are primary.

| horizon | profile | pair | Delta [CI] | Holm p | reading | loss ratio reading |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | RI (primary) | 0.0813 [0.00586, 0.165] | 0.0075 | interaction gain detected | small |
| H=8 (0.27 LT) | oracle | OI (primary) | 0.0241 [-0.0399, 0.0925] | 0.626 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | RO | 0.128 [0.0266, 0.236] | 0.003 | interaction gain detected | needed, size not determined |
| H=8 (0.27 LT) | oracle | RN | -0.0158 [-0.0888, 0.0554] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | ON | 0.00616 [-0.0673, 0.0787] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | IN | -0.0102 [-0.0448, 0.0244] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RI (primary) | -0.0138 [-0.0733, 0.0467] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | OI (primary) | 0.000148 [-0.0276, 0.0277] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RO | 0.103 [0.0323, 0.177] | 0.003 | interaction gain detected | small |
| H=8 (0.27 LT) | deployable | RN | -0.000438 [-0.0375, 0.0347] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | ON | 0.0067 [-0.0251, 0.0418] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | IN | 0.0121 [-0.0124, 0.0384] | 0.507 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | RI (primary) | 0.0484 [-0.0122, 0.118] | 0.068 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | OI (primary) | -0.026 [-0.102, 0.0598] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | RO | 0.0825 [0.00105, 0.168] | 0.0225 | interaction gain detected | needed, size not determined |
| H=15 (0.50 LT) | oracle | RN | 0.00794 [-0.0563, 0.0709] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | ON | -0.0248 [-0.101, 0.0499] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | IN | 0.0458 [0.00908, 0.084] | 0.006 | interaction gain detected | small |
| H=15 (0.50 LT) | deployable | RI (primary) | 0.0305 [-0.0108, 0.0712] | 0.13 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | OI (primary) | -0.135 [-0.303, 0.0201] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | RO | 0.00563 [-0.194, 0.197] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | RN | 0.000723 [-0.0492, 0.0537] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | ON | -0.166 [-0.315, -0.017] | 1 | no interaction gain; the pair model fits worse | no interaction gain; the pair model fits worse |
| H=15 (0.50 LT) | deployable | IN | 0.0239 [-0.00473, 0.0555] | 0.099 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | RI (primary) | 0.0141 [-0.0558, 0.0926] | 1 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | OI (primary) | 0.0086 [-0.0699, 0.102] | 1 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | RO | 0.27 [0.159, 0.391] | 0.003 | interaction gain detected | needed, size not determined |
| H=30 (1.00 LT) | oracle | RN | 0.00295 [-0.0618, 0.0691] | 1 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | ON | -0.0813 [-0.168, 0.0101] | 1 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | IN | 0.0199 [-0.0357, 0.0682] | 0.847 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | RI (primary) | 0.0122 [-0.0356, 0.0573] | 0.82 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | OI (primary) | 0.00934 [-0.0217, 0.0427] | 0.82 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | RO | 0.127 [0.0675, 0.183] | 0.003 | interaction gain detected | small |
| H=30 (1.00 LT) | deployable | RN | 0.00611 [-0.0422, 0.0597] | 0.82 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | ON | -0.00455 [-0.0353, 0.0232] | 0.82 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | IN | 0.0254 [-0.0072, 0.0608] | 0.0925 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | RI (primary) | 0.0891 [0.0255, 0.151] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | oracle | OI (primary) | 0.135 [0.0739, 0.193] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | oracle | RO | 0.137 [0.0505, 0.221] | 0.003 | interaction gain detected | needed, size not determined |
| H=60 (2.00 LT) | oracle | RN | 0.0478 [0.0112, 0.0845] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | oracle | ON | 0.0312 [-0.00896, 0.0746] | 0.025 | interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | IN | 0.0405 [0.00756, 0.0737] | 0.004 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | RI (primary) | 0.169 [0.0844, 0.246] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | OI (primary) | 0.00234 [-0.0025, 0.00736] | 0.11 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | RO | 0.156 [0.0744, 0.237] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | RN | 0.151 [0.0838, 0.217] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | ON | 0.131 [0.0743, 0.19] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | IN | 0.0265 [0.00502, 0.0488] | 0.003 | interaction gain detected | small |
| H=120 (4.00 LT) | oracle | RI (primary) | 0.0512 [0.0091, 0.0925] | 0.004 | interaction gain detected | small |
| H=120 (4.00 LT) | oracle | OI (primary) | 0.073 [0.0313, 0.115] | 0.003 | interaction gain detected | small |
| H=120 (4.00 LT) | oracle | RO | 0.0686 [0.0285, 0.107] | 0.003 | interaction gain detected | small |
| H=120 (4.00 LT) | oracle | RN | 0.00947 [-0.0182, 0.0359] | 0.414 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | ON | 0.0131 [-0.0171, 0.0413] | 0.414 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | IN | -0.000676 [-0.0232, 0.0215] | 0.524 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RI (primary) | 0.0504 [0.0211, 0.0821] | 0.003 | interaction gain detected | small |
| H=120 (4.00 LT) | deployable | OI (primary) | 0.0594 [0.0194, 0.0991] | 0.003 | interaction gain detected | small |
| H=120 (4.00 LT) | deployable | RO | 0.0458 [0.0182, 0.0694] | 0.003 | interaction gain detected | small |
| H=120 (4.00 LT) | deployable | RN | -0.00138 [-0.0259, 0.0214] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | ON | -0.0108 [-0.0377, 0.0143] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | IN | -0.00231 [-0.0358, 0.0258] | 1 | no interaction gain detected | negligible |

### D. Allocation ladder (rung against the full profile)

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED. MSE ratio MSE(rung)/MSE(F) at level 1 - 0.05/m (m rungs); Holm p for Delta MSE > 0. Theory gap L_A(oracle F) is an upper bound; estimation gap = L_A(deployable F) - L_A(oracle F) (95%).

| horizon | profile | rung | MSE | MSE ratio vs F [CI] | reading | Holm p |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | none | 0.0171 | 2.64 [1.7, 8.09] | undetermined (n_eff < 50) | 0.0045 |
| H=8 (0.27 LT) | oracle | separation | 0.00715 | 1.11 [0.395, 1.66] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | RO | 0.00655 | 1.01 [0.349, 1.49] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | R | 0.0166 | 2.57 [1.64, 8.06] | undetermined (n_eff < 50) | 0.0045 |
| H=8 (0.27 LT) | oracle | O | 0.00695 | 1.07 [0.37, 1.6] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | I | 0.0103 | 1.59 [1.15, 4.01] | undetermined (n_eff < 50) | 0.0045 |
| H=8 (0.27 LT) | oracle | N | 0.0168 | 2.59 [1.59, 8.24] | undetermined (n_eff < 50) | 0.0045 |
| H=8 (0.27 LT) | oracle | F (ROIN) | 0.00646 | 1 | | |
| H=8 (0.27 LT) | oracle | X | 0.00706 | 1.09 [0.379, 1.5] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | X+F | 0.00681 | 1.05 [0.316, 1.44] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | none | 0.0185 | 1.05 [0.63, 2.18] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | A2 (stored) | 0.0185 | 1.05 [0.636, 2.17] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | separation | 0.0345 | 1.96 [1.24, 4.01] | undetermined (n_eff < 50) | 0.006 |
| H=8 (0.27 LT) | deployable | A4 (stored) | 0.0345 | 1.96 [1.24, 4.01] | undetermined (n_eff < 50) | 0.006 |
| H=8 (0.27 LT) | deployable | RO | 0.0119 | 0.676 [0.314, 1.15] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | R | 0.0186 | 1.06 [0.61, 2.2] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | O | 0.0138 | 0.787 [0.516, 1.4] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | I | 0.0224 | 1.27 [0.997, 2.11] | undetermined (n_eff < 50) | 0.04 |
| H=8 (0.27 LT) | deployable | N | 0.0175 | 0.994 [0.51, 2.26] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | F (ROIN) | 0.0176 | 1 | | |
| H=8 (0.27 LT) | deployable | X | 0.0076 | 0.432 [0.0724, 0.869] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | A3 (stored) | 0.0173 | 0.987 [0.475, 2.28] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | X+F | 0.00726 | 0.413 [0.0758, 0.838] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | oracle | none | 0.0301 | 2.16 [1.61, 3.05] | undetermined (n_eff < 50) | 0.0045 |
| H=15 (0.50 LT) | oracle | separation | 0.0162 | 1.16 [1.03, 1.46] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | oracle | RO | 0.0155 | 1.11 [0.996, 1.38] | undetermined (n_eff < 50) | 0.018 |
| H=15 (0.50 LT) | oracle | R | 0.0289 | 2.07 [1.58, 2.92] | undetermined (n_eff < 50) | 0.0045 |
| H=15 (0.50 LT) | oracle | O | 0.0173 | 1.24 [1.05, 1.55] | undetermined (n_eff < 50) | 0.0045 |
| H=15 (0.50 LT) | oracle | I | 0.027 | 1.94 [1.44, 2.82] | undetermined (n_eff < 50) | 0.0045 |
| H=15 (0.50 LT) | oracle | N | 0.0351 | 2.52 [1.6, 4] | undetermined (n_eff < 50) | 0.0045 |
| H=15 (0.50 LT) | oracle | F (ROIN) | 0.014 | 1 | | |
| H=15 (0.50 LT) | oracle | X | 0.0144 | 1.03 [0.9, 1.21] | undetermined (n_eff < 50) | 0.473 |
| H=15 (0.50 LT) | oracle | X+F | 0.0141 | 1.01 [0.938, 1.13] | undetermined (n_eff < 50) | 0.473 |
| H=15 (0.50 LT) | deployable | none | 0.0319 | 1.3 [0.976, 1.76] | undetermined (n_eff < 50) | 0.03 |
| H=15 (0.50 LT) | deployable | A2 (stored) | 0.032 | 1.3 [0.991, 1.75] | undetermined (n_eff < 50) | 0.024 |
| H=15 (0.50 LT) | deployable | separation | 0.0397 | 1.62 [1.07, 2.36] | undetermined (n_eff < 50) | 0.011 |
| H=15 (0.50 LT) | deployable | A4 (stored) | 0.0397 | 1.62 [1.07, 2.36] | undetermined (n_eff < 50) | 0.011 |
| H=15 (0.50 LT) | deployable | RO | 0.03 | 1.22 [1, 1.55] | undetermined (n_eff < 50) | 0.02 |
| H=15 (0.50 LT) | deployable | R | 0.0296 | 1.21 [1.03, 1.45] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | O | 0.0302 | 1.23 [0.94, 1.62] | undetermined (n_eff < 50) | 0.086 |
| H=15 (0.50 LT) | deployable | I | 0.0314 | 1.28 [1.04, 1.67] | undetermined (n_eff < 50) | 0.011 |
| H=15 (0.50 LT) | deployable | N | 0.0332 | 1.35 [1, 1.79] | undetermined (n_eff < 50) | 0.02 |
| H=15 (0.50 LT) | deployable | F (ROIN) | 0.0246 | 1 | | |
| H=15 (0.50 LT) | deployable | X | 0.0157 | 0.637 [0.441, 0.853] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | A3 (stored) | 0.0257 | 1.05 [0.732, 1.47] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | X+F | 0.0168 | 0.682 [0.512, 0.841] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | none | 0.0546 | 1.27 [1.01, 1.61] | undetermined (n_eff < 50) | 0.02 |
| H=30 (1.00 LT) | oracle | separation | 0.0379 | 0.886 [0.721, 1.05] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | RO | 0.0388 | 0.906 [0.762, 1.05] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | R | 0.0576 | 1.35 [1.08, 1.65] | undetermined (n_eff < 50) | 0.009 |
| H=30 (1.00 LT) | oracle | O | 0.0381 | 0.891 [0.718, 1.06] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | I | 0.0491 | 1.15 [0.873, 1.52] | undetermined (n_eff < 50) | 0.393 |
| H=30 (1.00 LT) | oracle | N | 0.0524 | 1.22 [0.961, 1.53] | undetermined (n_eff < 50) | 0.0735 |
| H=30 (1.00 LT) | oracle | F (ROIN) | 0.0428 | 1 | | |
| H=30 (1.00 LT) | oracle | X | 0.0373 | 0.87 [0.695, 1.05] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | X+F | 0.0357 | 0.835 [0.685, 0.98] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | deployable | none | 0.0594 | 1.23 [1.04, 1.47] | needed, size not determined | 0.011 |
| H=30 (1.00 LT) | deployable | A2 (stored) | 0.0593 | 1.23 [1.04, 1.47] | needed, size not determined | 0.011 |
| H=30 (1.00 LT) | deployable | separation | 0.0653 | 1.35 [1.05, 1.71] | substantial | 0.011 |
| H=30 (1.00 LT) | deployable | A4 (stored) | 0.0653 | 1.35 [1.05, 1.71] | substantial | 0.011 |
| H=30 (1.00 LT) | deployable | RO | 0.0523 | 1.08 [0.951, 1.23] | undetermined | 0.16 |
| H=30 (1.00 LT) | deployable | R | 0.0553 | 1.14 [0.992, 1.35] | undetermined | 0.018 |
| H=30 (1.00 LT) | deployable | O | 0.0571 | 1.18 [1.02, 1.37] | needed, size not determined | 0.0065 |
| H=30 (1.00 LT) | deployable | I | 0.0576 | 1.19 [1.03, 1.4] | needed, size not determined | 0.011 |
| H=30 (1.00 LT) | deployable | N | 0.0577 | 1.19 [1.03, 1.39] | needed, size not determined | 0.0065 |
| H=30 (1.00 LT) | deployable | A5 (stored) | 0.0528 | 1.09 [0.953, 1.27] | undetermined | 0.152 |
| H=30 (1.00 LT) | deployable | F (ROIN) | 0.0483 | 1 | | |
| H=30 (1.00 LT) | deployable | X | 0.0404 | 0.836 [0.724, 0.975] | lowers | 1 |
| H=30 (1.00 LT) | deployable | A3 (stored) | 0.0487 | 1.01 [0.837, 1.22] | undetermined | 1 |
| H=30 (1.00 LT) | deployable | X+F | 0.0412 | 0.853 [0.749, 0.968] | lowers | 1 |
| H=60 (2.00 LT) | oracle | none | 0.153 | 1.11 [1.06, 1.16] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | separation | 0.143 | 1.04 [1.01, 1.07] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | RO | 0.14 | 1.02 [0.995, 1.05] | negligible | 0.045 |
| H=60 (2.00 LT) | oracle | R | 0.152 | 1.1 [1.06, 1.14] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | O | 0.143 | 1.04 [1, 1.07] | needed, size not determined | 0.008 |
| H=60 (2.00 LT) | oracle | I | 0.151 | 1.1 [1.05, 1.15] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | N | 0.152 | 1.1 [1.06, 1.15] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | F (ROIN) | 0.138 | 1 | | |
| H=60 (2.00 LT) | oracle | X | 0.14 | 1.01 [0.971, 1.06] | undetermined | 0.389 |
| H=60 (2.00 LT) | oracle | X+F | 0.136 | 0.991 [0.966, 1.02] | negligible | 0.825 |
| H=60 (2.00 LT) | deployable | none | 0.156 | 1.03 [0.986, 1.06] | undetermined | 0.108 |
| H=60 (2.00 LT) | deployable | A2 (stored) | 0.156 | 1.03 [0.987, 1.07] | undetermined | 0.108 |
| H=60 (2.00 LT) | deployable | separation | 0.159 | 1.05 [1.01, 1.1] | needed, size not determined | 0.012 |
| H=60 (2.00 LT) | deployable | A4 (stored) | 0.159 | 1.05 [1.01, 1.1] | needed, size not determined | 0.012 |
| H=60 (2.00 LT) | deployable | RO | 0.155 | 1.02 [0.997, 1.06] | undetermined | 0.063 |
| H=60 (2.00 LT) | deployable | R | 0.155 | 1.03 [0.993, 1.06] | undetermined | 0.084 |
| H=60 (2.00 LT) | deployable | O | 0.154 | 1.02 [0.985, 1.05] | undetermined | 0.165 |
| H=60 (2.00 LT) | deployable | I | 0.153 | 1.01 [0.975, 1.05] | negligible | 0.794 |
| H=60 (2.00 LT) | deployable | N | 0.157 | 1.04 [1, 1.07] | needed, size not determined | 0.015 |
| H=60 (2.00 LT) | deployable | F (ROIN) | 0.151 | 1 | | |
| H=60 (2.00 LT) | deployable | X | 0.145 | 0.959 [0.906, 1.01] | negligible | 1 |
| H=60 (2.00 LT) | deployable | A3 (stored) | 0.153 | 1.01 [0.965, 1.06] | undetermined | 0.794 |
| H=60 (2.00 LT) | deployable | X+F | 0.145 | 0.956 [0.913, 0.994] | lowers | 1 |
| H=120 (4.00 LT) | oracle | none | 0.858 | 1.01 [0.997, 1.02] | negligible | 0.157 |
| H=120 (4.00 LT) | oracle | separation | 0.92 | 1.08 [1.06, 1.1] | substantial | 0.0045 |
| H=120 (4.00 LT) | oracle | RO | 0.851 | 1 [0.992, 1.01] | negligible | 1 |
| H=120 (4.00 LT) | oracle | R | 0.851 | 1 [0.991, 1.01] | negligible | 1 |
| H=120 (4.00 LT) | oracle | O | 0.856 | 1.01 [0.995, 1.02] | negligible | 0.312 |
| H=120 (4.00 LT) | oracle | I | 0.856 | 1.01 [0.995, 1.02] | negligible | 0.312 |
| H=120 (4.00 LT) | oracle | N | 0.859 | 1.01 [0.997, 1.02] | negligible | 0.144 |
| H=120 (4.00 LT) | oracle | F (ROIN) | 0.851 | 1 | | |
| H=120 (4.00 LT) | oracle | X | 0.847 | 0.995 [0.984, 1.01] | negligible | 1 |
| H=120 (4.00 LT) | oracle | X+F | 0.843 | 0.99 [0.982, 0.998] | lowers | 1 |
| H=120 (4.00 LT) | deployable | none | 0.858 | 1.01 [1, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | A2 (stored) | 0.858 | 1.01 [1, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | separation | 0.895 | 1.05 [1.03, 1.08] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | A4 (stored) | 0.895 | 1.05 [1.03, 1.08] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | RO | 0.851 | 1 [1, 1.01] | negligible | 0.018 |
| H=120 (4.00 LT) | deployable | R | 0.852 | 1 [1, 1.01] | negligible | 0.0175 |
| H=120 (4.00 LT) | deployable | O | 0.855 | 1.01 [1, 1.01] | small | 0.006 |
| H=120 (4.00 LT) | deployable | I | 0.855 | 1.01 [1, 1.01] | small | 0.006 |
| H=120 (4.00 LT) | deployable | N | 0.856 | 1.01 [1, 1.01] | small | 0.006 |
| H=120 (4.00 LT) | deployable | F (ROIN) | 0.849 | 1 | | |
| H=120 (4.00 LT) | deployable | X | 0.846 | 0.996 [0.986, 1.01] | negligible | 1 |
| H=120 (4.00 LT) | deployable | A3 (stored) | 0.864 | 1.02 [0.999, 1.04] | negligible | 0.018 |
| H=120 (4.00 LT) | deployable | X+F | 0.845 | 0.996 [0.99, 1] | negligible | 1 |

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| horizon | theory gap (upper bound) [CI] | estimation gap [CI] | gap with R estimated | gap with O estimated | gap with I estimated | gap with N estimated |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 0.00192 [0.000636, 0.00353] | 0.0111 [0.00429, 0.0198] | 0.000315 [-0.000793, 0.00162] | 0.00257 [0.000605, 0.00453] | 0.00086 [0.000195, 0.00181] | -0.000199 [-0.00168, 0.00126] |
| H=15 (0.50 LT) | 0.00326 [0.00182, 0.005] | 0.0106 [0.00621, 0.0159] | 0.000375 [-0.00192, 0.00275] | 0.00902 [0.00454, 0.014] | 0.00117 [-0.00124, 0.00376] | 0.0007 [-0.00174, 0.00332] |
| H=30 (1.00 LT) | 0.0168 [0.0109, 0.0237] | 0.00553 [-0.002, 0.0127] | -0.00195 [-0.00871, 0.00465] | 0.00759 [-0.000773, 0.0164] | -0.00223 [-0.00881, 0.0043] | -0.00296 [-0.00949, 0.0037] |
| H=60 (2.00 LT) | 0.0389 [0.0336, 0.0448] | 0.0136 [0.00246, 0.0252] | 0.00509 [-0.00538, 0.0161] | 0.0119 [0.00149, 0.0229] | 0.00219 [-0.00792, 0.0126] | 0.00264 [-0.0076, 0.0133] |
| H=120 (4.00 LT) | 0.247 [0.236, 0.259] | -0.00214 [-0.0245, 0.0209] | -0.0039 [-0.0256, 0.0183] | -0.00213 [-0.024, 0.0208] | -0.00368 [-0.0249, 0.0179] | -0.00712 [-0.0289, 0.0149] |

### Horizon decision (Y = ln min(T_c, H_max))

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED. Pinball loss at tau = 0.5; drop-one ratio at level 1 - 0.05/4; ladder ratio vs F at 1 - 0.05/m; C = Harrell's C (95%); coverage of q_0.1, q_0.5, q_0.9 and the 80% interval below the cap.

| profile | X | pinball ratio [CI] | reading | Holm p | phi [CI] |
|---|---|---|---|---|---|
| oracle | R | 1.02 [1, 1.03] | small | 0.002 | 0.00242 [0.00164, 0.00326] |
| oracle | O | 1.09 [1.07, 1.12] | substantial | 0.002 | 0.00911 [0.00776, 0.0104] |
| oracle | I | 1.25 [1.21, 1.29] | substantial | 0.002 | 0.0316 [0.0277, 0.0354] |
| oracle | N | 1.01 [0.995, 1.02] | negligible | 0.0775 | 0.00249 [0.00153, 0.00352] |
| deployable | R | 1.01 [0.998, 1.01] | negligible | 0.045 | 0.00252 [0.00182, 0.0032] |
| deployable | O | 1.08 [1.07, 1.11] | substantial | 0.002 | 0.00885 [0.00748, 0.0102] |
| deployable | I | 1.26 [1.22, 1.31] | substantial | 0.002 | 0.033 [0.0292, 0.0368] |
| deployable | N | 1 [0.994, 1.01] | negligible | 0.445 | 0.00143 [0.000877, 0.00197] |

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | ratio vs F [CI] | reading | C [CI] | cov 0.1 / 0.5 / 0.9 / 80% |
|---|---|---|---|---|---|---|
| oracle | none | 0.197 | 1.3 [1.25, 1.35] | substantial | 0.5 [0.5, 0.5] | 0.0963 / 0.487 / 0.894 / 0.797 |
| oracle | lyapunov | 0.305 | 2.02 [1.91, 2.13] | substantial | 0.615 [0.604, 0.626] | 0.0815 / 0.481 / 0.842 / 0.802 |
| oracle | RO | 0.193 | 1.28 [1.22, 1.33] | substantial | 0.567 [0.557, 0.577] | 0.129 / 0.488 / 0.89 / 0.761 |
| oracle | R | 0.194 | 1.29 [1.23, 1.34] | substantial | 0.546 [0.535, 0.556] | 0.115 / 0.497 / 0.894 / 0.779 |
| oracle | O | 0.194 | 1.29 [1.23, 1.34] | substantial | 0.552 [0.543, 0.562] | 0.114 / 0.487 / 0.882 / 0.768 |
| oracle | I | 0.172 | 1.14 [1.1, 1.17] | substantial | 0.63 [0.62, 0.642] | 0.105 / 0.485 / 0.886 / 0.781 |
| oracle | N | 0.192 | 1.27 [1.23, 1.32] | substantial | 0.563 [0.552, 0.574] | 0.102 / 0.491 / 0.894 / 0.793 |
| oracle | ROIN | 0.151 | 1 |  | 0.688 [0.678, 0.699] | 0.141 / 0.498 / 0.857 / 0.716 |
| oracle | X | 0.16 | 1.06 [1.01, 1.11] | needed, size not determined | 0.678 [0.668, 0.688] | 0.148 / 0.489 / 0.855 / 0.707 |
| oracle | X+F | 0.132 | 0.873 [0.853, 0.897] | lowers | 0.742 [0.732, 0.751] | 0.156 / 0.492 / 0.861 / 0.705 |
| oracle | Lyapunov rank (C only) | | | | 0.608 [0.597, 0.619] | |
| deployable | none | 0.197 | 1.3 [1.25, 1.36] | substantial | 0.5 [0.5, 0.5] | 0.0963 / 0.487 / 0.894 / 0.797 |
| deployable | lyapunov | 0.297 | 1.97 [1.86, 2.08] | substantial | 0.622 [0.611, 0.632] | 0.0773 / 0.476 / 0.85 / 0.812 |
| deployable | RO | 0.191 | 1.27 [1.22, 1.32] | substantial | 0.574 [0.565, 0.584] | 0.117 / 0.488 / 0.893 / 0.776 |
| deployable | R | 0.194 | 1.29 [1.24, 1.34] | substantial | 0.549 [0.539, 0.558] | 0.102 / 0.496 / 0.894 / 0.792 |
| deployable | O | 0.193 | 1.28 [1.23, 1.34] | substantial | 0.556 [0.547, 0.566] | 0.107 / 0.489 / 0.887 / 0.779 |
| deployable | I | 0.172 | 1.14 [1.11, 1.17] | substantial | 0.626 [0.616, 0.636] | 0.104 / 0.479 / 0.89 / 0.786 |
| deployable | N | 0.194 | 1.29 [1.24, 1.34] | substantial | 0.558 [0.551, 0.566] | 0.0993 / 0.489 / 0.895 / 0.796 |
| deployable | ROIN | 0.151 | 1 |  | 0.687 [0.677, 0.697] | 0.126 / 0.492 / 0.878 / 0.752 |
| deployable | X | 0.159 | 1.06 [1.01, 1.11] | needed, size not determined | 0.679 [0.669, 0.689] | 0.141 / 0.489 / 0.86 / 0.719 |
| deployable | X+F | 0.132 | 0.875 [0.854, 0.897] | lowers | 0.731 [0.72, 0.74] | 0.143 / 0.498 / 0.861 / 0.718 |
| deployable | Lyapunov rank (C only) | | | | 0.614 [0.603, 0.626] | |

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| profile | pair | Delta [CI] | Holm p | detected |
|---|---|---|---|---|
| oracle | RO | 0.00371 [0.000945, 0.00665] | 0.003 | True |
| oracle | RI (primary) | 0.00301 [0.000168, 0.00582] | 0.01 | True |
| oracle | RN | 0.000274 [-0.000213, 0.000776] | 0.153 | False |
| oracle | OI (primary) | 0.0165 [0.0121, 0.0212] | 0.003 | True |
| oracle | ON | 0.000544 [-3.33e-05, 0.00115] | 0.0165 | True |
| oracle | IN | 0.00127 [-0.00159, 0.00413] | 0.153 | False |
| deployable | RO | 0.00117 [0.000267, 0.0021] | 0.006 | True |
| deployable | RI (primary) | 0.00343 [0.00135, 0.00565] | 0.003 | True |
| deployable | RN | -0.00023 [-0.000794, 0.000408] | 0.839 | False |
| deployable | OI (primary) | 0.0151 [0.0114, 0.0188] | 0.003 | True |
| deployable | ON | 0.000658 [-2.07e-05, 0.00137] | 0.021 | True |
| deployable | IN | 0.000352 [-0.00107, 0.0018] | 0.499 | False |

## rossler

**PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.**

| check | result |
|---|---|
| (f1) state_mse from per-draw errors, max rel diff | A0 0.0e+00, A1 0.0e+00, A2 0.0e+00, A3 0.0e+00, A4 0.0e+00, A5 0.0e+00 (within 1e-12: True) |
| (g) WU-0039b (b1), (b2) rows reproduced | drop-N: True, all rows: True |
| separation formula on F-hat vs stored A4 at H_ref, max abs | 2.22e-16 |
| T_c: T = 1 / e_(T-1) = theta (train, test) | 0/0, 0/0 |
| (f2) dependence bias, deployable rows (reported, not gating) | 131 rows; 71 flagged: H=8 R: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0132, z 5.21; H=8 N: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0156, z 5.64; H=8 RO: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0196, z 5.47; H=8 RI: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0138, z 4.95; H=8 RN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0243, z 7.4; H=8 ON: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0172, z 5.01; H=8 IN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0155, z 5.67; H=8 ROI: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0194, z 5.54; H=8 RON: dependence bias detectable (interval excludes 0), t1+t2 / V 0.028, z 7.19; H=8 RIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0239, z 7.41; H=8 OIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0169, z 5.15; H=8 ROIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.028, z 7.25 ... |

### A. Allocation: drop-one and Shapley

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED. MSE ratio MSE(F without X)/MSE(F) at level 1 - 0.05/4 (reading by the 1.05 table, with the n_eff guard); excess ratio L_A(F without X)/L_A(F) and Holm p (Delta MSE > 0) are estimates. phi = Shapley share of L_A (95%). Oracle rows: moment form; deployable rows: realized per draw.

| horizon | profile | X | MSE ratio [CI] | reading | excess ratio | Holm p | phi_X [95% CI] | share |
|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | R | 1.05 [1.04, 1.06] | needed, size not determined | 1.6 | 0.002 | 6.71e-06 [5.9e-06, 7.57e-06] | 0.646 |
| H=8 (0.27 LT) | oracle | O | 1.02 [1.01, 1.02] | small | 1.18 | 0.002 | 1.1e-06 [8.3e-07, 1.39e-06] | 0.106 |
| H=8 (0.27 LT) | oracle | I | 1 [1, 1] | negligible | 1 | 0.115 | 3.06e-12 [-5.3e-08, 5.41e-08] | 2.95e-07 |
| H=8 (0.27 LT) | oracle | N | 1.01 [1.01, 1.01] | small | 1.1 | 0.002 | 2.57e-06 [2.27e-06, 2.84e-06] | 0.247 |
| H=8 (0.27 LT) | deployable | R | 0.999 [0.994, 1] | negligible | 0.995 | 1 | -2.45e-07 [-7.26e-07, 2.22e-07] | 0.917 |
| H=8 (0.27 LT) | deployable | O | 1 [0.998, 1.01] | negligible | 1.02 | 0.162 | 3.68e-07 [-3.2e-08, 7.63e-07] | -1.38 |
| H=8 (0.27 LT) | deployable | I | 1 [1, 1] | negligible | 1.01 | 0.205 | 4.54e-08 [-5.93e-08, 1.5e-07] | -0.17 |
| H=8 (0.27 LT) | deployable | N | 0.996 [0.992, 1] | negligible | 0.976 | 1 | -4.35e-07 [-9.43e-07, 1.73e-08] | 1.63 |
| H=15 (0.50 LT) | oracle | R | 1.06 [1.05, 1.07] | substantial | 1.74 | 0.002 | 1.34e-05 [1.18e-05, 1.5e-05] | 0.653 |
| H=15 (0.50 LT) | oracle | O | 1.02 [1.01, 1.02] | small | 1.21 | 0.002 | 2.01e-06 [1.42e-06, 2.63e-06] | 0.098 |
| H=15 (0.50 LT) | oracle | I | 1 [1, 1] | negligible | 1 | 0.047 | 4.5e-09 [-8.37e-08, 9.94e-08] | 0.00022 |
| H=15 (0.50 LT) | oracle | N | 1.01 [1.01, 1.01] | small | 1.12 | 0.002 | 5.1e-06 [4.48e-06, 5.69e-06] | 0.249 |
| H=15 (0.50 LT) | deployable | R | 1 [0.991, 1.01] | negligible | 0.999 | 1 | -1.42e-07 [-1.26e-06, 9.9e-07] | 0.0943 |
| H=15 (0.50 LT) | deployable | O | 0.995 [0.98, 1.01] | negligible | 0.966 | 1 | -5.52e-07 [-2.24e-06, 8.7e-07] | 0.366 |
| H=15 (0.50 LT) | deployable | I | 1 [0.996, 1] | negligible | 0.997 | 1 | -1.42e-07 [-5.04e-07, 1.51e-07] | 0.0943 |
| H=15 (0.50 LT) | deployable | N | 0.996 [0.988, 1] | negligible | 0.974 | 1 | -6.73e-07 [-1.96e-06, 5.07e-07] | 0.446 |
| H=30 (1.00 LT) | oracle | R | 1.09 [1.06, 1.11] | substantial | 1.99 | 0.002 | 6.36e-05 [5.42e-05, 7.35e-05] | 0.715 |
| H=30 (1.00 LT) | oracle | O | 1.02 [1, 1.03] | small | 1.19 | 0.0195 | 7.72e-06 [2.42e-06, 1.26e-05] | 0.0868 |
| H=30 (1.00 LT) | oracle | I | 0.997 [0.993, 1] | negligible | 0.971 | 0.906 | 6.54e-08 [-1.16e-06, 1.18e-06] | 0.000735 |
| H=30 (1.00 LT) | oracle | N | 1.01 [0.998, 1.02] | negligible | 1.1 | 0.063 | 1.75e-05 [1.4e-05, 2.11e-05] | 0.197 |
| H=30 (1.00 LT) | deployable | R | 0.997 [0.986, 1.01] | negligible | 0.98 | 1 | -3.08e-06 [-8.03e-06, 1.72e-06] | 0.528 |
| H=30 (1.00 LT) | deployable | O | 0.996 [0.981, 1.01] | negligible | 0.979 | 1 | -1.61e-06 [-9.96e-06, 5.98e-06] | 0.276 |
| H=30 (1.00 LT) | deployable | I | 1 [1, 1.01] | small | 1.02 | 0.018 | 6.56e-07 [-5.68e-07, 1.93e-06] | -0.113 |
| H=30 (1.00 LT) | deployable | N | 0.998 [0.991, 1] | negligible | 0.985 | 1 | -1.8e-06 [-6.49e-06, 2.67e-06] | 0.308 |
| H=60 (2.00 LT) | oracle | R | 1.09 [1.06, 1.12] | substantial | 1.45 | 0.002 | 0.00112 [0.0009, 0.00134] | 0.813 |
| H=60 (2.00 LT) | oracle | O | 1.01 [0.992, 1.03] | negligible | 1.06 | 0.09 | 6.55e-05 [-3.32e-05, 0.000159] | 0.0478 |
| H=60 (2.00 LT) | oracle | I | 1 [1, 1.01] | negligible | 1.01 | 0.039 | 7.02e-06 [-1.52e-05, 2.81e-05] | 0.00512 |
| H=60 (2.00 LT) | oracle | N | 1 [0.998, 1.01] | negligible | 1.02 | 0.09 | 0.000183 [9.03e-05, 0.000265] | 0.134 |
| H=60 (2.00 LT) | deployable | R | 1 [0.992, 1.02] | negligible | 1.02 | 0.639 | 1.6e-05 [-0.000104, 0.00014] | 0.133 |
| H=60 (2.00 LT) | deployable | O | 1.01 [0.998, 1.02] | negligible | 1.03 | 0.128 | 6.64e-05 [-1.91e-05, 0.000149] | 0.55 |
| H=60 (2.00 LT) | deployable | I | 1 [1, 1] | negligible | 1 | 0.639 | 5.06e-06 [-1.54e-05, 2.35e-05] | 0.042 |
| H=60 (2.00 LT) | deployable | N | 1 [0.989, 1.02] | negligible | 1.01 | 0.639 | 3.33e-05 [-5.32e-05, 0.000115] | 0.276 |
| H=120 (4.00 LT) | oracle | R | 1.01 [1, 1.01] | small | 1.03 | 0.0165 | 0.000693 [0.000169, 0.00118] | 0.435 |
| H=120 (4.00 LT) | oracle | O | 1 [0.999, 1.01] | negligible | 1.01 | 0.042 | 9.38e-05 [-0.000223, 0.000408] | 0.0589 |
| H=120 (4.00 LT) | oracle | I | 1.01 [1, 1.01] | small | 1.02 | 0.002 | 0.000743 [0.000459, 0.00104] | 0.466 |
| H=120 (4.00 LT) | oracle | N | 0.999 [0.998, 1] | negligible | 0.998 | 0.964 | 6.31e-05 [-5.81e-05, 0.00018] | 0.0396 |
| H=120 (4.00 LT) | deployable | R | 1 [0.999, 1.01] | negligible | 1.01 | 0.078 | 0.000423 [8.08e-05, 0.000764] | 0.432 |
| H=120 (4.00 LT) | deployable | O | 1 [0.995, 1] | negligible | 0.998 | 1 | -0.000156 [-0.000551, 0.000234] | -0.159 |
| H=120 (4.00 LT) | deployable | I | 1 [1, 1.01] | small | 1.02 | 0.002 | 0.000596 [0.000273, 0.000927] | 0.608 |
| H=120 (4.00 LT) | deployable | N | 0.999 [0.998, 1] | lowers | 0.997 | 1 | 0.000116 [-5.17e-05, 0.000278] | 0.119 |

### A. Allocation: summary per horizon

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED. n_eff = Kish size of kappa on the test states; G = 1 - L_A(rule)/L_A(constant), estimate (95%).

| horizon | profile | n_eff(kappa) | G(F) [CI] | G(separation) | MSE(F)/MSE(sep) [CI] | reading | settings (A) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 755 | 0.498 [0.469, 0.525] | 0.102 | 0.934 [0.927, 0.942] | lowers | F: mid; qn 2, mid 4, low 9 |
| H=8 (0.27 LT) | deployable | 755 | -0.0134 [-0.0665, 0.0298] | -0.542 | 0.924 [0.912, 0.935] | lowers | F: mid; qn 0, mid 9, low 6 |
| H=15 (0.50 LT) | oracle | 600 | 0.551 [0.52, 0.581] | 0.229 | 0.944 [0.938, 0.949] | lowers | F: mid; qn 0, mid 7, low 8 |
| H=15 (0.50 LT) | deployable | 600 | -0.0524 [-0.181, 0.0405] | -0.567 | 0.935 [0.923, 0.948] | lowers | F: mid; qn 0, mid 11, low 4 |
| H=30 (1.00 LT) | oracle | 473 | 0.597 [0.534, 0.65] | 0.474 | 0.974 [0.967, 0.983] | lowers | F: qn; qn 4, mid 3, low 8 |
| H=30 (1.00 LT) | deployable | 473 | -0.047 [-0.163, 0.0437] | -0.444 | 0.94 [0.926, 0.953] | lowers | F: mid; qn 0, mid 8, low 7 |
| H=60 (2.00 LT) | oracle | 519 | 0.375 [0.311, 0.433] | 0.396 | 1.01 [0.998, 1.02] | negligible | F: mid; qn 0, mid 5, low 10 |
| H=60 (2.00 LT) | deployable | 519 | 0.0364 [-0.0141, 0.0835] | -0.0154 | 0.987 [0.975, 0.998] | lowers | F: low; qn 0, mid 1, low 14 |
| H=120 (4.00 LT) | oracle | 1.54e+03 | 0.0515 [0.0303, 0.0704] | -0.117 | 0.953 [0.94, 0.967] | lowers | F: low; qn 0, mid 0, low 15 |
| H=120 (4.00 LT) | deployable | 1.54e+03 | 0.0345 [0.0149, 0.054] | -0.152 | 0.952 [0.937, 0.967] | lowers | F: low; qn 0, mid 0, low 15 |

### B. Allocation: pairwise interactions (logit u, interior states)

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED. Delta = L(additive) - L(additive + pair) on the test states, models fixed; level 1 - 0.05/6; Holm over the six pairs. R x I and O x I are primary.

| horizon | profile | pair | Delta [CI] | Holm p | reading | loss ratio reading |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | RI (primary) | 0.0102 [-0.00825, 0.027] | 0.199 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | OI (primary) | 0.0166 [0.000224, 0.0337] | 0.014 | interaction gain detected | small |
| H=8 (0.27 LT) | oracle | RO | 0.0625 [0.0221, 0.106] | 0.003 | interaction gain detected | small |
| H=8 (0.27 LT) | oracle | RN | -0.00147 [-0.0384, 0.0408] | 0.533 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | ON | 0.0264 [0.00249, 0.0495] | 0.01 | interaction gain detected | small |
| H=8 (0.27 LT) | oracle | IN | 0.00259 [-0.00926, 0.0154] | 0.533 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RI (primary) | 0.00725 [-0.00525, 0.0199] | 0.29 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | OI (primary) | -0.000491 [-0.0171, 0.0167] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RO | 0.0746 [0.0325, 0.118] | 0.003 | interaction gain detected | small |
| H=8 (0.27 LT) | deployable | RN | 0.0261 [-0.000882, 0.0555] | 0.03 | interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | ON | 0.0083 [-0.00811, 0.0262] | 0.337 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | IN | -0.000206 [-0.011, 0.0105] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | RI (primary) | 0.0144 [-0.00499, 0.0336] | 0.0765 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | OI (primary) | 0.0194 [0.00246, 0.0376] | 0.01 | interaction gain detected | small |
| H=15 (0.50 LT) | oracle | RO | 0.0575 [0.0153, 0.0946] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | oracle | RN | 0.00147 [-0.0238, 0.0279] | 0.519 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | ON | 0.0344 [0.0125, 0.0574] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | oracle | IN | 0.00355 [-0.0118, 0.0194] | 0.519 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | RI (primary) | 0.0111 [-0.00361, 0.0259] | 0.063 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | OI (primary) | 0.0256 [0.00887, 0.0437] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | deployable | RO | 0.0696 [0.0317, 0.111] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | deployable | RN | 0.0215 [-0.00674, 0.0485] | 0.063 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | ON | 0.0156 [0.0028, 0.0288] | 0.004 | interaction gain detected | small |
| H=15 (0.50 LT) | deployable | IN | 0.00312 [-0.00586, 0.0117] | 0.183 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | RI (primary) | 0.00614 [-0.0163, 0.0287] | 0.238 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | OI (primary) | 0.0234 [-0.00147, 0.049] | 0.018 | interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | RO | 0.0742 [0.0168, 0.129] | 0.003 | interaction gain detected | needed, size not determined |
| H=30 (1.00 LT) | oracle | RN | 0.0353 [0.00414, 0.0725] | 0.006 | interaction gain detected | small |
| H=30 (1.00 LT) | oracle | ON | 0.0412 [0.0122, 0.0718] | 0.003 | interaction gain detected | small |
| H=30 (1.00 LT) | oracle | IN | 0.015 [-0.00209, 0.0335] | 0.018 | interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | RI (primary) | 0.0119 [-0.0119, 0.036] | 0.398 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | OI (primary) | 0.0117 [-0.0193, 0.0429] | 0.398 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | RO | 0.0681 [0.0158, 0.121] | 0.009 | interaction gain detected | small |
| H=30 (1.00 LT) | deployable | RN | 0.0155 [-0.0145, 0.0434] | 0.37 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | ON | 0.00538 [-0.0145, 0.026] | 0.398 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | IN | 0.00518 [-0.00552, 0.0159] | 0.398 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | RI (primary) | 0.0224 [-0.00334, 0.0456] | 0.027 | interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | OI (primary) | 0.0361 [0.00551, 0.0642] | 0.01 | interaction gain detected | small |
| H=60 (2.00 LT) | oracle | RO | 0.0487 [-0.00428, 0.1] | 0.026 | interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | RN | 0.00965 [-0.0211, 0.0411] | 0.222 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | ON | 0.0278 [-0.00223, 0.0579] | 0.026 | interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | IN | 0.035 [0.0133, 0.0582] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | RI (primary) | 0.0186 [-0.00453, 0.0402] | 0.035 | interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | OI (primary) | 0.0297 [0.00457, 0.0559] | 0.0075 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | RO | 0.0614 [0.0249, 0.1] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | RN | 0.0146 [-0.0127, 0.0412] | 0.0855 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | ON | 0.0226 [-0.00328, 0.0485] | 0.024 | interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | IN | 0.015 [-0.000321, 0.0292] | 0.022 | interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RI (primary) | 0.0175 [-0.0185, 0.0599] | 0.367 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | OI (primary) | 0.028 [-0.00559, 0.0655] | 0.085 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RO | 0.0276 [-0.00576, 0.0659] | 0.09 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RN | 0.0152 [-0.02, 0.0565] | 0.367 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | ON | 0.0297 [-0.00537, 0.0662] | 0.072 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | IN | 0.015 [-0.0193, 0.0545] | 0.367 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RI (primary) | 0.00323 [-0.00222, 0.00864] | 0.26 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | OI (primary) | 0.00391 [-0.00724, 0.0156] | 0.373 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RO | 0.00854 [0.000491, 0.0171] | 0.015 | interaction gain detected | small |
| H=120 (4.00 LT) | deployable | RN | -0.0113 [-0.0374, 0.018] | 0.86 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | ON | 0.00597 [-0.00451, 0.0159] | 0.26 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | IN | 0.00367 [-0.00467, 0.0119] | 0.373 | no interaction gain detected | negligible |

### D. Allocation ladder (rung against the full profile)

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED. MSE ratio MSE(rung)/MSE(F) at level 1 - 0.05/m (m rungs); Holm p for Delta MSE > 0. Theory gap L_A(oracle F) is an upper bound; estimation gap = L_A(deployable F) - L_A(oracle F) (95%).

| horizon | profile | rung | MSE | MSE ratio vs F [CI] | reading | Holm p |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | none | 0.000128 | 1.09 [1.08, 1.1] | substantial | 0.0045 |
| H=8 (0.27 LT) | oracle | separation | 0.000126 | 1.07 [1.06, 1.08] | substantial | 0.0045 |
| H=8 (0.27 LT) | oracle | RO | 0.000119 | 1.01 [1.01, 1.01] | small | 0.0045 |
| H=8 (0.27 LT) | oracle | R | 0.000121 | 1.03 [1.02, 1.03] | small | 0.0045 |
| H=8 (0.27 LT) | oracle | O | 0.000128 | 1.09 [1.07, 1.1] | substantial | 0.0045 |
| H=8 (0.27 LT) | oracle | I | 0.000128 | 1.09 [1.08, 1.1] | substantial | 0.0045 |
| H=8 (0.27 LT) | oracle | N | 0.000124 | 1.05 [1.04, 1.07] | needed, size not determined | 0.0045 |
| H=8 (0.27 LT) | oracle | F (ROIN) | 0.000118 | 1 | | |
| H=8 (0.27 LT) | oracle | X | 0.000127 | 1.08 [1.06, 1.09] | substantial | 0.0045 |
| H=8 (0.27 LT) | oracle | X+F | 0.000118 | 1 [0.994, 1.01] | negligible | 0.359 |
| H=8 (0.27 LT) | deployable | none | 0.000127 | 0.998 [0.987, 1.01] | negligible | 1 |
| H=8 (0.27 LT) | deployable | A2 (stored) | 0.000127 | 0.998 [0.987, 1.01] | negligible | 1 |
| H=8 (0.27 LT) | deployable | separation | 0.000138 | 1.08 [1.06, 1.1] | substantial | 0.006 |
| H=8 (0.27 LT) | deployable | A4 (stored) | 0.000138 | 1.08 [1.06, 1.1] | substantial | 0.006 |
| H=8 (0.27 LT) | deployable | RO | 0.000127 | 0.997 [0.992, 1] | negligible | 1 |
| H=8 (0.27 LT) | deployable | R | 0.000128 | 1 [0.991, 1.01] | negligible | 1 |
| H=8 (0.27 LT) | deployable | O | 0.000127 | 0.995 [0.986, 1] | negligible | 1 |
| H=8 (0.27 LT) | deployable | I | 0.000127 | 0.998 [0.988, 1.01] | negligible | 1 |
| H=8 (0.27 LT) | deployable | N | 0.000128 | 1 [0.993, 1.01] | negligible | 1 |
| H=8 (0.27 LT) | deployable | F (ROIN) | 0.000127 | 1 | | |
| H=8 (0.27 LT) | deployable | X | 0.000126 | 0.988 [0.976, 1] | negligible | 1 |
| H=8 (0.27 LT) | deployable | A3 (stored) | 0.000136 | 1.06 [1.04, 1.09] | needed, size not determined | 0.006 |
| H=8 (0.27 LT) | deployable | X+F | 0.000126 | 0.991 [0.985, 0.995] | lowers | 1 |
| H=15 (0.50 LT) | oracle | none | 0.000221 | 1.1 [1.09, 1.12] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | separation | 0.000213 | 1.06 [1.05, 1.07] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | RO | 0.000203 | 1.01 [1.01, 1.01] | small | 0.0045 |
| H=15 (0.50 LT) | oracle | R | 0.000207 | 1.03 [1.02, 1.04] | small | 0.0045 |
| H=15 (0.50 LT) | oracle | O | 0.000221 | 1.1 [1.09, 1.12] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | I | 0.000221 | 1.1 [1.09, 1.12] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | N | 0.000213 | 1.06 [1.05, 1.08] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | F (ROIN) | 0.000201 | 1 | | |
| H=15 (0.50 LT) | oracle | X | 0.000221 | 1.1 [1.08, 1.11] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | X+F | 0.000201 | 0.999 [0.998, 1] | negligible | 0.974 |
| H=15 (0.50 LT) | deployable | none | 0.000213 | 0.993 [0.971, 1.01] | negligible | 1 |
| H=15 (0.50 LT) | deployable | A2 (stored) | 0.000213 | 0.993 [0.971, 1.01] | negligible | 1 |
| H=15 (0.50 LT) | deployable | separation | 0.000229 | 1.07 [1.05, 1.09] | needed, size not determined | 0.006 |
| H=15 (0.50 LT) | deployable | A4 (stored) | 0.000229 | 1.07 [1.05, 1.09] | needed, size not determined | 0.006 |
| H=15 (0.50 LT) | deployable | RO | 0.000214 | 0.996 [0.985, 1.01] | negligible | 1 |
| H=15 (0.50 LT) | deployable | R | 0.000213 | 0.993 [0.972, 1.01] | negligible | 1 |
| H=15 (0.50 LT) | deployable | O | 0.000213 | 0.992 [0.973, 1.01] | negligible | 1 |
| H=15 (0.50 LT) | deployable | I | 0.000213 | 0.994 [0.973, 1.01] | negligible | 1 |
| H=15 (0.50 LT) | deployable | N | 0.000213 | 0.994 [0.976, 1.01] | negligible | 1 |
| H=15 (0.50 LT) | deployable | F (ROIN) | 0.000214 | 1 | | |
| H=15 (0.50 LT) | deployable | X | 0.000212 | 0.99 [0.97, 1.01] | negligible | 1 |
| H=15 (0.50 LT) | deployable | A3 (stored) | 0.000229 | 1.07 [1.03, 1.1] | needed, size not determined | 0.006 |
| H=15 (0.50 LT) | deployable | X+F | 0.000213 | 0.991 [0.985, 0.996] | lowers | 1 |
| H=30 (1.00 LT) | oracle | none | 0.000785 | 1.13 [1.1, 1.16] | substantial | 0.0045 |
| H=30 (1.00 LT) | oracle | separation | 0.000715 | 1.03 [1.01, 1.04] | small | 0.0045 |
| H=30 (1.00 LT) | oracle | RO | 0.000699 | 1 [0.995, 1.01] | negligible | 0.259 |
| H=30 (1.00 LT) | oracle | R | 0.00072 | 1.03 [1.02, 1.06] | needed, size not determined | 0.0045 |
| H=30 (1.00 LT) | oracle | O | 0.000785 | 1.13 [1.1, 1.16] | substantial | 0.0045 |
| H=30 (1.00 LT) | oracle | I | 0.000784 | 1.13 [1.1, 1.16] | substantial | 0.0045 |
| H=30 (1.00 LT) | oracle | N | 0.000757 | 1.09 [1.06, 1.12] | substantial | 0.0045 |
| H=30 (1.00 LT) | oracle | F (ROIN) | 0.000696 | 1 | | |
| H=30 (1.00 LT) | oracle | X | 0.000775 | 1.11 [1.08, 1.14] | substantial | 0.0045 |
| H=30 (1.00 LT) | oracle | X+F | 0.000692 | 0.994 [0.987, 1] | negligible | 0.989 |
| H=30 (1.00 LT) | deployable | none | 0.00076 | 0.992 [0.971, 1.02] | negligible | 1 |
| H=30 (1.00 LT) | deployable | A2 (stored) | 0.00076 | 0.992 [0.971, 1.02] | negligible | 1 |
| H=30 (1.00 LT) | deployable | separation | 0.000815 | 1.06 [1.04, 1.09] | needed, size not determined | 0.0065 |
| H=30 (1.00 LT) | deployable | A4 (stored) | 0.000815 | 1.06 [1.04, 1.09] | needed, size not determined | 0.0065 |
| H=30 (1.00 LT) | deployable | RO | 0.000767 | 1 [0.993, 1.01] | negligible | 1 |
| H=30 (1.00 LT) | deployable | R | 0.000764 | 0.997 [0.976, 1.02] | negligible | 1 |
| H=30 (1.00 LT) | deployable | O | 0.00076 | 0.992 [0.975, 1.01] | negligible | 1 |
| H=30 (1.00 LT) | deployable | I | 0.000761 | 0.994 [0.973, 1.02] | negligible | 1 |
| H=30 (1.00 LT) | deployable | N | 0.000763 | 0.995 [0.977, 1.01] | negligible | 1 |
| H=30 (1.00 LT) | deployable | A5 (stored) | 0.000762 | 0.995 [0.975, 1.01] | negligible | 1 |
| H=30 (1.00 LT) | deployable | F (ROIN) | 0.000766 | 1 | | |
| H=30 (1.00 LT) | deployable | X | 0.000755 | 0.985 [0.964, 1.01] | negligible | 1 |
| H=30 (1.00 LT) | deployable | A3 (stored) | 0.000785 | 1.02 [0.995, 1.06] | undetermined | 0.137 |
| H=30 (1.00 LT) | deployable | X+F | 0.000758 | 0.989 [0.981, 0.998] | lowers | 1 |
| H=60 (2.00 LT) | oracle | none | 0.0132 | 1.12 [1.08, 1.15] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | separation | 0.0117 | 0.993 [0.979, 1.01] | negligible | 1 |
| H=60 (2.00 LT) | oracle | RO | 0.0118 | 1.01 [0.998, 1.01] | negligible | 0.07 |
| H=60 (2.00 LT) | oracle | R | 0.0119 | 1.01 [0.993, 1.03] | negligible | 0.127 |
| H=60 (2.00 LT) | oracle | O | 0.0131 | 1.12 [1.08, 1.15] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | I | 0.0132 | 1.12 [1.08, 1.16] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | N | 0.0128 | 1.09 [1.05, 1.12] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | F (ROIN) | 0.0118 | 1 | | |
| H=60 (2.00 LT) | oracle | X | 0.0135 | 1.15 [1.1, 1.2] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | X+F | 0.0118 | 1 [0.992, 1.01] | negligible | 1 |
| H=60 (2.00 LT) | deployable | none | 0.0128 | 1.01 [0.992, 1.03] | negligible | 0.512 |
| H=60 (2.00 LT) | deployable | A2 (stored) | 0.0128 | 1.01 [0.993, 1.03] | negligible | 0.512 |
| H=60 (2.00 LT) | deployable | separation | 0.0129 | 1.01 [0.997, 1.03] | negligible | 0.12 |
| H=60 (2.00 LT) | deployable | A4 (stored) | 0.0129 | 1.01 [0.997, 1.03] | negligible | 0.12 |
| H=60 (2.00 LT) | deployable | RO | 0.0127 | 0.999 [0.993, 1] | negligible | 0.707 |
| H=60 (2.00 LT) | deployable | R | 0.0128 | 1.01 [0.999, 1.03] | negligible | 0.066 |
| H=60 (2.00 LT) | deployable | O | 0.0128 | 1.01 [0.989, 1.03] | negligible | 0.512 |
| H=60 (2.00 LT) | deployable | I | 0.0128 | 1.01 [0.991, 1.03] | negligible | 0.512 |
| H=60 (2.00 LT) | deployable | N | 0.0128 | 1.01 [0.993, 1.02] | negligible | 0.512 |
| H=60 (2.00 LT) | deployable | F (ROIN) | 0.0127 | 1 | | |
| H=60 (2.00 LT) | deployable | X | 0.0131 | 1.03 [0.997, 1.07] | undetermined | 0.066 |
| H=60 (2.00 LT) | deployable | A3 (stored) | 0.0129 | 1.01 [0.985, 1.05] | negligible | 0.512 |
| H=60 (2.00 LT) | deployable | X+F | 0.0128 | 1.01 [0.989, 1.03] | negligible | 0.512 |
| H=120 (4.00 LT) | oracle | none | 0.108 | 1.01 [1.01, 1.02] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | separation | 0.112 | 1.05 [1.03, 1.07] | needed, size not determined | 0.0045 |
| H=120 (4.00 LT) | oracle | RO | 0.107 | 1.01 [1, 1.01] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | R | 0.108 | 1.01 [1, 1.02] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | O | 0.109 | 1.02 [1.01, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | I | 0.108 | 1.01 [1, 1.02] | negligible | 0.007 |
| H=120 (4.00 LT) | oracle | N | 0.108 | 1.01 [1, 1.02] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | F (ROIN) | 0.107 | 1 | | |
| H=120 (4.00 LT) | oracle | X | 0.108 | 1.01 [1, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | X+F | 0.106 | 0.997 [0.995, 1] | lowers | 0.998 |
| H=120 (4.00 LT) | deployable | none | 0.106 | 1.01 [1, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | A2 (stored) | 0.106 | 1.01 [1, 1.02] | small | 0.007 |
| H=120 (4.00 LT) | deployable | separation | 0.11 | 1.05 [1.03, 1.07] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | A4 (stored) | 0.11 | 1.05 [1.03, 1.07] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | RO | 0.105 | 1 [1, 1.01] | small | 0.018 |
| H=120 (4.00 LT) | deployable | R | 0.105 | 1 [0.997, 1.01] | negligible | 0.112 |
| H=120 (4.00 LT) | deployable | O | 0.106 | 1.01 [1.01, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | I | 0.105 | 1 [0.997, 1.01] | negligible | 0.215 |
| H=120 (4.00 LT) | deployable | N | 0.105 | 1.01 [0.999, 1.01] | negligible | 0.0725 |
| H=120 (4.00 LT) | deployable | F (ROIN) | 0.105 | 1 | | |
| H=120 (4.00 LT) | deployable | X | 0.106 | 1.01 [0.997, 1.02] | negligible | 0.0725 |
| H=120 (4.00 LT) | deployable | A3 (stored) | 0.107 | 1.02 [1, 1.04] | small | 0.006 |
| H=120 (4.00 LT) | deployable | X+F | 0.104 | 0.993 [0.983, 1] | negligible | 0.967 |

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| horizon | theory gap (upper bound) [CI] | estimation gap [CI] | gap with R estimated | gap with O estimated | gap with I estimated | gap with N estimated |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 1.05e-05 [9.79e-06, 1.11e-05] | 9.74e-06 [5.66e-06, 1.38e-05] | 5.19e-06 [1.2e-06, 9.12e-06] | -1.4e-06 [-5.08e-06, 2.25e-06] | -1.42e-06 [-5.07e-06, 2.25e-06] | -1.68e-08 [-3.75e-06, 3.68e-06] |
| H=15 (0.50 LT) | 1.67e-05 [1.54e-05, 1.81e-05] | 1.36e-05 [6.66e-06, 2.09e-05] | 3.91e-06 [-2.98e-06, 1.07e-05] | -9.04e-06 [-1.54e-05, -2.45e-06] | -9.34e-06 [-1.56e-05, -2.98e-06] | -6.46e-06 [-1.27e-05, 1.47e-08] |
| H=30 (1.00 LT) | 6.01e-05 [5.3e-05, 6.86e-05] | 6.97e-05 [3.89e-05, 0.000102] | 4.58e-05 [1.55e-05, 8e-05] | -2.01e-05 [-4.56e-05, 8.51e-06] | -1.72e-05 [-4.34e-05, 1.18e-05] | -1.35e-05 [-3.89e-05, 1.54e-05] |
| H=60 (2.00 LT) | 0.00228 [0.00199, 0.00259] | 0.000912 [0.000212, 0.00162] | 0.000616 [-7.22e-05, 0.00132] | -0.000487 [-0.00112, 0.000115] | -0.00042 [-0.00104, 0.000188] | -0.000346 [-0.000967, 0.000261] |
| H=120 (4.00 LT) | 0.0293 [0.0277, 0.031] | -0.00192 [-0.00472, 0.000647] | -0.00186 [-0.00463, 0.00071] | -0.00234 [-0.00504, 0.000198] | -0.00244 [-0.0051, 0.000148] | -0.00236 [-0.00503, 0.000201] |

### Horizon decision (Y = ln min(T_c, H_max))

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED. Pinball loss at tau = 0.5; drop-one ratio at level 1 - 0.05/4; ladder ratio vs F at 1 - 0.05/m; C = Harrell's C (95%); coverage of q_0.1, q_0.5, q_0.9 and the 80% interval below the cap.

| profile | X | pinball ratio [CI] | reading | Holm p | phi [CI] |
|---|---|---|---|---|---|
| oracle | R | 1.01 [0.999, 1.02] | negligible | 0.0105 | 0.000912 [5.4e-05, 0.00179] |
| oracle | O | 1.12 [1.09, 1.14] | substantial | 0.002 | 0.00967 [0.00802, 0.0114] |
| oracle | I | 1.24 [1.2, 1.27] | substantial | 0.002 | 0.0251 [0.0225, 0.0278] |
| oracle | N | 1.01 [1, 1.02] | small | 0.002 | 0.00265 [0.00156, 0.00376] |
| deployable | R | 0.991 [0.985, 0.996] | lowers | 1 | 0.00082 [0.000308, 0.00135] |
| deployable | O | 1.13 [1.1, 1.15] | substantial | 0.002 | 0.0143 [0.0123, 0.0164] |
| deployable | I | 1.22 [1.18, 1.25] | substantial | 0.002 | 0.0241 [0.0216, 0.0265] |
| deployable | N | 1 [0.993, 1.01] | negligible | 0.908 | 0.00203 [0.00127, 0.00282] |

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | ratio vs F [CI] | reading | C [CI] | cov 0.1 / 0.5 / 0.9 / 80% |
|---|---|---|---|---|---|---|
| oracle | none | 0.161 | 1.31 [1.27, 1.36] | substantial | 0.5 [0.5, 0.5] | 0.102 / 0.475 / 0.891 / 0.789 |
| oracle | lyapunov | 0.171 | 1.39 [1.34, 1.44] | substantial | 0.635 [0.625, 0.646] | 0.0806 / 0.48 / 0.871 / 0.826 |
| oracle | RO | 0.155 | 1.26 [1.22, 1.3] | substantial | 0.567 [0.557, 0.576] | 0.114 / 0.492 / 0.889 / 0.775 |
| oracle | R | 0.161 | 1.31 [1.27, 1.36] | substantial | 0.514 [0.504, 0.524] | 0.116 / 0.475 / 0.893 / 0.777 |
| oracle | O | 0.157 | 1.28 [1.24, 1.32] | substantial | 0.548 [0.538, 0.557] | 0.109 / 0.482 / 0.889 / 0.78 |
| oracle | I | 0.141 | 1.15 [1.12, 1.18] | substantial | 0.616 [0.607, 0.626] | 0.0932 / 0.496 / 0.892 / 0.799 |
| oracle | N | 0.158 | 1.28 [1.24, 1.33] | substantial | 0.541 [0.531, 0.552] | 0.103 / 0.49 / 0.894 / 0.79 |
| oracle | ROIN | 0.123 | 1 |  | 0.679 [0.67, 0.689] | 0.11 / 0.512 / 0.884 / 0.775 |
| oracle | X | 0.122 | 0.99 [0.952, 1.03] | negligible | 0.699 [0.691, 0.707] | 0.161 / 0.496 / 0.884 / 0.723 |
| oracle | X+F | 0.0927 | 0.754 [0.733, 0.775] | lowers | 0.767 [0.76, 0.775] | 0.15 / 0.507 / 0.857 / 0.707 |
| oracle | Lyapunov rank (C only) | | | | 0.631 [0.622, 0.642] | |
| deployable | none | 0.161 | 1.34 [1.3, 1.39] | substantial | 0.5 [0.5, 0.5] | 0.102 / 0.475 / 0.891 / 0.789 |
| deployable | lyapunov | 0.173 | 1.44 [1.39, 1.49] | substantial | 0.628 [0.618, 0.638] | 0.0785 / 0.479 / 0.871 / 0.83 |
| deployable | RO | 0.149 | 1.24 [1.2, 1.28] | substantial | 0.6 [0.591, 0.609] | 0.123 / 0.494 / 0.889 / 0.766 |
| deployable | R | 0.16 | 1.33 [1.29, 1.38] | substantial | 0.516 [0.508, 0.525] | 0.104 / 0.479 / 0.891 / 0.787 |
| deployable | O | 0.151 | 1.26 [1.22, 1.3] | substantial | 0.595 [0.585, 0.604] | 0.11 / 0.496 / 0.893 / 0.782 |
| deployable | I | 0.141 | 1.18 [1.15, 1.21] | substantial | 0.616 [0.607, 0.625] | 0.1 / 0.495 / 0.89 / 0.789 |
| deployable | N | 0.158 | 1.32 [1.27, 1.36] | substantial | 0.537 [0.529, 0.544] | 0.103 / 0.479 / 0.89 / 0.788 |
| deployable | ROIN | 0.12 | 1 |  | 0.689 [0.681, 0.698] | 0.129 / 0.5 / 0.865 / 0.736 |
| deployable | X | 0.123 | 1.02 [0.99, 1.07] | undetermined | 0.696 [0.688, 0.704] | 0.153 / 0.493 / 0.866 / 0.713 |
| deployable | X+F | 0.0922 | 0.768 [0.747, 0.792] | lowers | 0.768 [0.761, 0.775] | 0.148 / 0.498 / 0.857 / 0.709 |
| deployable | Lyapunov rank (C only) | | | | 0.625 [0.616, 0.635] | |

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| profile | pair | Delta [CI] | Holm p | detected |
|---|---|---|---|---|
| oracle | RO | 0.000882 [0.000135, 0.00168] | 0.004 | True |
| oracle | RI (primary) | -0.000517 [-0.00251, 0.0014] | 0.731 | False |
| oracle | RN | 0.000491 [7.96e-05, 0.000862] | 0.003 | True |
| oracle | OI (primary) | 0.00692 [0.00468, 0.00914] | 0.003 | True |
| oracle | ON | 0.000678 [-9.41e-05, 0.00146] | 0.033 | True |
| oracle | IN | 0.000833 [-0.000497, 0.00226] | 0.077 | False |
| deployable | RO | 5.32e-05 [-0.000741, 0.000827] | 1 | False |
| deployable | RI (primary) | 0.000832 [-0.000242, 0.00189] | 0.108 | False |
| deployable | RN | -8.3e-05 [-0.000517, 0.000336] | 1 | False |
| deployable | OI (primary) | 0.0101 [0.00823, 0.012] | 0.003 | True |
| deployable | ON | 0.000524 [-9.6e-05, 0.00119] | 0.085 | False |
| deployable | IN | -7.53e-05 [-0.000909, 0.000787] | 1 | False |

## chua

**PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.**

| check | result |
|---|---|
| (f1) state_mse from per-draw errors, max rel diff | A0 0.0e+00, A1 0.0e+00, A2 0.0e+00, A3 0.0e+00, A4 0.0e+00, A5 0.0e+00 (within 1e-12: True) |
| (g) WU-0039b (b1), (b2) rows reproduced | drop-N: True, all rows: True |
| separation formula on F-hat vs stored A4 at H_ref, max abs | 2.22e-16 |
| T_c: T = 1 / e_(T-1) = theta (train, test) | 0/0, 1/0 |
| (f2) dependence bias, deployable rows (reported, not gating) | 131 rows; 62 flagged: H=8 R: dependence bias detectable (interval excludes 0), t1+t2 / V 0.00788, z 3.38; H=8 N: dependence bias detectable (interval excludes 0), t1+t2 / V 0.00751, z 2.65; H=8 RO: dependence bias detectable (interval excludes 0), t1+t2 / V 0.00821, z 3.36; H=8 RI: dependence bias detectable (interval excludes 0), t1+t2 / V 0.00835, z 1.61; H=8 RN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.00981, z 2.51; H=8 ON: dependence bias detectable (interval excludes 0), t1+t2 / V 0.00716, z 2.42; H=8 IN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.00791, z 2.78; H=8 ROI: dependence bias detectable (interval excludes 0), t1+t2 / V 0.00794, z 3.22; H=8 RON: dependence bias detectable (interval excludes 0), t1+t2 / V 0.011, z 3.59; H=8 RIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0108, z 1.18; H=8 OIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.00709, z 1.83; H=8 ROIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0107, z 3.44 ... |

### A. Allocation: drop-one and Shapley

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED. MSE ratio MSE(F without X)/MSE(F) at level 1 - 0.05/4 (reading by the 1.05 table, with the n_eff guard); excess ratio L_A(F without X)/L_A(F) and Holm p (Delta MSE > 0) are estimates. phi = Shapley share of L_A (95%). Oracle rows: moment form; deployable rows: realized per draw.

| horizon | profile | X | MSE ratio [CI] | reading | excess ratio | Holm p | phi_X [95% CI] | share |
|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | R | 1.1 [1.02, 1.3] | undetermined (n_eff < 50) | 1.65 | 0.002 | 5.85e-05 [3.36e-05, 9.52e-05] | -1.56 |
| H=8 (0.27 LT) | oracle | O | 0.94 [0.674, 1.07] | undetermined (n_eff < 50) | 0.617 | 1 | -4.68e-05 [-0.000187, 8.77e-05] | 1.24 |
| H=8 (0.27 LT) | oracle | I | 0.941 [0.773, 1.02] | undetermined (n_eff < 50) | 0.625 | 1 | -2.93e-05 [-8.5e-05, 5.9e-06] | 0.778 |
| H=8 (0.27 LT) | oracle | N | 0.959 [0.802, 1.08] | undetermined (n_eff < 50) | 0.741 | 1 | -2.01e-05 [-8.14e-05, 2.33e-05] | 0.534 |
| H=8 (0.27 LT) | deployable | R | 1 [0.981, 1.02] | undetermined (n_eff < 50) | - | 0.853 | -3.99e-06 [-1.41e-05, 5.76e-06] | 1.51 |
| H=8 (0.27 LT) | deployable | O | 1.05 [1.02, 1.09] | undetermined (n_eff < 50) | - | 0.002 | 8.71e-06 [3.18e-06, 1.54e-05] | -3.29 |
| H=8 (0.27 LT) | deployable | I | 1 [0.998, 1] | undetermined (n_eff < 50) | - | 0.703 | -2.88e-07 [-2.52e-06, 2.06e-06] | 0.109 |
| H=8 (0.27 LT) | deployable | N | 0.997 [0.988, 1.01] | undetermined (n_eff < 50) | - | 0.853 | -7.07e-06 [-1.32e-05, -1.17e-06] | 2.67 |
| H=15 (0.50 LT) | oracle | R | 1.05 [0.987, 1.17] | undetermined (n_eff < 50) | 1.28 | 0.0855 | 0.000115 [3.86e-06, 0.000243] | 0.69 |
| H=15 (0.50 LT) | oracle | O | 1.03 [1, 1.08] | undetermined (n_eff < 50) | 1.16 | 0.024 | 5.02e-05 [-8.09e-05, 0.000181] | 0.301 |
| H=15 (0.50 LT) | oracle | I | 1 [0.995, 1.01] | undetermined (n_eff < 50) | 1 | 0.896 | -9.7e-06 [-3.48e-05, 1.17e-05] | -0.0582 |
| H=15 (0.50 LT) | oracle | N | 0.995 [0.967, 1.02] | undetermined (n_eff < 50) | 0.972 | 0.896 | 1.12e-05 [-8.2e-05, 7.52e-05] | 0.067 |
| H=15 (0.50 LT) | deployable | R | 1 [0.973, 1.03] | undetermined (n_eff < 50) | 1.07 | 1 | 2.12e-06 [-5.44e-05, 5.41e-05] | -0.136 |
| H=15 (0.50 LT) | deployable | O | 0.996 [0.987, 1] | undetermined (n_eff < 50) | 0.883 | 1 | -1.04e-05 [-3.28e-05, 1.04e-05] | 0.665 |
| H=15 (0.50 LT) | deployable | I | 1 [0.996, 1.01] | undetermined (n_eff < 50) | 1.08 | 0.622 | 1.07e-05 [-9.04e-06, 2.94e-05] | -0.686 |
| H=15 (0.50 LT) | deployable | N | 0.993 [0.981, 1.01] | undetermined (n_eff < 50) | 0.806 | 1 | -1.8e-05 [-4.9e-05, 1.25e-05] | 1.16 |
| H=30 (1.00 LT) | oracle | R | 1.05 [1.02, 1.09] | needed, size not determined | 1.17 | 0.002 | 0.00091 [0.000429, 0.0014] | 0.73 |
| H=30 (1.00 LT) | oracle | O | 1.02 [0.994, 1.05] | negligible | 1.06 | 0.105 | -8.09e-05 [-0.000543, 0.000381] | -0.0649 |
| H=30 (1.00 LT) | oracle | I | 1.01 [0.996, 1.02] | negligible | 1.03 | 0.105 | 0.000207 [6.68e-06, 0.000401] | 0.166 |
| H=30 (1.00 LT) | oracle | N | 1 [0.992, 1.01] | negligible | 0.998 | 0.565 | 0.00021 [-5.48e-05, 0.000453] | 0.168 |
| H=30 (1.00 LT) | deployable | R | 1.02 [0.992, 1.06] | undetermined | 1.07 | 0.072 | 0.000277 [-0.000139, 0.000707] | 0.767 |
| H=30 (1.00 LT) | deployable | O | 1.01 [0.981, 1.04] | negligible | 1.02 | 0.501 | 1.39e-05 [-0.000436, 0.000548] | 0.0386 |
| H=30 (1.00 LT) | deployable | I | 1.01 [1, 1.01] | small | 1.02 | 0.002 | 0.000187 [6.71e-05, 0.000316] | 0.516 |
| H=30 (1.00 LT) | deployable | N | 0.999 [0.992, 1.01] | negligible | 0.997 | 0.679 | -0.000116 [-0.000325, 9.53e-05] | -0.321 |
| H=60 (2.00 LT) | oracle | R | 1.01 [0.986, 1.03] | negligible | 1.04 | 0.346 | 0.00343 [-0.000768, 0.00698] | 0.354 |
| H=60 (2.00 LT) | oracle | O | 1.02 [1.01, 1.03] | small | 1.06 | 0.002 | 0.00353 [0.00225, 0.00485] | 0.364 |
| H=60 (2.00 LT) | oracle | I | 1 [0.998, 1.01] | negligible | 1.01 | 0.346 | 0.000953 [0.000332, 0.00154] | 0.0983 |
| H=60 (2.00 LT) | oracle | N | 0.998 [0.989, 1.01] | negligible | 0.995 | 0.653 | 0.00178 [0.00079, 0.00276] | 0.184 |
| H=60 (2.00 LT) | deployable | R | 1.01 [0.997, 1.02] | negligible | 1.02 | 0.075 | 0.00135 [-0.000522, 0.00328] | 0.185 |
| H=60 (2.00 LT) | deployable | O | 1.02 [1.01, 1.03] | small | 1.05 | 0.002 | 0.00346 [0.00205, 0.00494] | 0.474 |
| H=60 (2.00 LT) | deployable | I | 1 [1, 1.01] | small | 1.01 | 0.002 | 0.00122 [0.000605, 0.00184] | 0.167 |
| H=60 (2.00 LT) | deployable | N | 1 [0.998, 1] | negligible | 1 | 0.305 | 0.00127 [0.000352, 0.00214] | 0.174 |
| H=120 (4.00 LT) | oracle | R | 1.01 [1, 1.02] | small | 1.05 | 0.002 | 0.01 [0.00539, 0.0142] | 0.538 |
| H=120 (4.00 LT) | oracle | O | 1 [1, 1.01] | negligible | 1.01 | 0.017 | 0.00285 [0.00092, 0.00477] | 0.153 |
| H=120 (4.00 LT) | oracle | I | 1 [1, 1.01] | small | 1.01 | 0.003 | 0.00323 [0.00186, 0.00458] | 0.173 |
| H=120 (4.00 LT) | oracle | N | 1 [1, 1] | negligible | 1 | 0.112 | 0.00254 [0.00139, 0.00373] | 0.136 |
| H=120 (4.00 LT) | deployable | R | 1.01 [1, 1.01] | negligible | 1.02 | 0.0225 | 0.00465 [0.00124, 0.0077] | 0.317 |
| H=120 (4.00 LT) | deployable | O | 1 [0.998, 1.01] | negligible | 1.01 | 0.162 | 0.00413 [0.00189, 0.00646] | 0.281 |
| H=120 (4.00 LT) | deployable | I | 1 [1, 1.01] | small | 1.01 | 0.01 | 0.00396 [0.00226, 0.00578] | 0.27 |
| H=120 (4.00 LT) | deployable | N | 0.996 [0.991, 1] | lowers | 0.984 | 0.994 | 0.00195 [0.000529, 0.00325] | 0.133 |

### A. Allocation: summary per horizon

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED. n_eff = Kish size of kappa on the test states; G = 1 - L_A(rule)/L_A(constant), estimate (95%).

| horizon | profile | n_eff(kappa) | G(F) [CI] | G(separation) | MSE(F)/MSE(sep) [CI] | reading | settings (A) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 51.5 | -0.245 [-2.33, 0.592] | 0.0589 | 1.04 [0.962, 1.16] | undetermined (n_eff < 50) | F: qn; qn 3, mid 2, low 10 |
| H=8 (0.27 LT) | deployable | 51.5 | - [-, -] | 0.166 | 0.907 [0.881, 0.933] | undetermined (n_eff < 50) | F: low; qn 2, mid 1, low 12 |
| H=15 (0.50 LT) | oracle | 68.6 | 0.212 [0.108, 0.344] | 0.362 | 1.04 [0.966, 1.1] | undetermined | F: low; qn 0, mid 0, low 15 |
| H=15 (0.50 LT) | deployable | 68.6 | -0.187 [-, -] | -1.49 | 0.964 [0.927, 1] | undetermined (n_eff < 50) | F: low; qn 0, mid 0, low 15 |
| H=30 (1.00 LT) | oracle | 216 | 0.187 [0.119, 0.248] | 0.273 | 1.03 [1.01, 1.06] | undetermined (n_eff < 50) | F: low; qn 1, mid 0, low 14 |
| H=30 (1.00 LT) | deployable | 216 | 0.0517 [-0.0674, 0.157] | 0.00272 | 0.982 [0.945, 1.02] | negligible | F: low; qn 0, mid 0, low 15 |
| H=60 (2.00 LT) | oracle | 842 | 0.138 [0.0788, 0.192] | 0.0973 | 0.985 [0.97, 1] | negligible | F: low; qn 0, mid 1, low 14 |
| H=60 (2.00 LT) | deployable | 842 | 0.103 [0.0686, 0.14] | -0.0138 | 0.959 [0.945, 0.973] | lowers | F: low; qn 0, mid 0, low 15 |
| H=120 (4.00 LT) | oracle | 1.94e+03 | 0.0951 [0.0694, 0.119] | -0.0779 | 0.949 [0.939, 0.958] | lowers | F: low; qn 0, mid 0, low 15 |
| H=120 (4.00 LT) | deployable | 1.94e+03 | 0.0785 [0.0554, 0.101] | -0.155 | 0.935 [0.921, 0.948] | lowers | F: low; qn 0, mid 4, low 11 |

### B. Allocation: pairwise interactions (logit u, interior states)

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED. Delta = L(additive) - L(additive + pair) on the test states, models fixed; level 1 - 0.05/6; Holm over the six pairs. R x I and O x I are primary.

| horizon | profile | pair | Delta [CI] | Holm p | reading | loss ratio reading |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | RI (primary) | -0.01 [-0.0366, 0.0193] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | OI (primary) | 0.00332 [-0.0227, 0.0278] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | RO | 0.00338 [-0.0349, 0.0393] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | RN | 0.0153 [-0.0153, 0.0451] | 0.442 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | ON | 0.0204 [-0.0106, 0.0517] | 0.282 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | IN | -0.0148 [-0.0323, 0.00192] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RI (primary) | 0.00587 [-0.0173, 0.0305] | 0.76 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | OI (primary) | 0.0241 [-0.00143, 0.0484] | 0.04 | interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RO | 0.0176 [-0.0202, 0.0535] | 0.466 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RN | -0.00552 [-0.0249, 0.0132] | 0.792 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | ON | 0.0182 [0.000162, 0.0335] | 0.03 | interaction gain detected | small |
| H=8 (0.27 LT) | deployable | IN | 0.00187 [-0.0114, 0.0137] | 0.76 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | RI (primary) | -0.00217 [-0.0263, 0.0237] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | OI (primary) | -0.00134 [-0.0312, 0.0289] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | RO | 0.075 [0.0333, 0.125] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | oracle | RN | 0.0191 [-0.00379, 0.043] | 0.054 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | ON | 0.0499 [0.0125, 0.085] | 0.005 | interaction gain detected | small |
| H=15 (0.50 LT) | oracle | IN | 0.00631 [-0.0136, 0.0273] | 0.624 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | RI (primary) | 0.000733 [-0.0306, 0.033] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | OI (primary) | 0.0168 [-0.0139, 0.0544] | 0.41 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | RO | 0.0552 [0.0217, 0.0897] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | deployable | RN | 0.0029 [-0.0225, 0.0283] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | ON | -0.0256 [-0.0998, 0.0524] | 1 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | IN | 0.0077 [-0.00796, 0.024] | 0.41 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | RI (primary) | 0.0195 [-0.0216, 0.06] | 0.327 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | OI (primary) | 0.0385 [0.00169, 0.0794] | 0.01 | interaction gain detected | small |
| H=30 (1.00 LT) | oracle | RO | 0.0152 [-0.0233, 0.0537] | 0.34 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | RN | 0.00812 [-0.0233, 0.0377] | 0.34 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | ON | 0.0387 [0.0102, 0.0676] | 0.003 | interaction gain detected | small |
| H=30 (1.00 LT) | oracle | IN | 0.0248 [-0.00374, 0.0522] | 0.054 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | RI (primary) | 0.00712 [-0.0222, 0.0353] | 0.817 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | OI (primary) | 0.0571 [0.0176, 0.0979] | 0.003 | interaction gain detected | small |
| H=30 (1.00 LT) | deployable | RO | 0.0241 [-0.012, 0.0618] | 0.212 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | RN | 0.00173 [-0.0167, 0.0209] | 0.817 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | ON | 0.0134 [-0.00753, 0.0353] | 0.22 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | IN | 0.00221 [-0.0177, 0.023] | 0.817 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | RI (primary) | 0.0295 [-0.04, 0.0945] | 0.65 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | OI (primary) | 0.0472 [-0.0241, 0.119] | 0.225 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | RO | 0.00516 [-0.0684, 0.0738] | 0.81 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | RN | 0.00478 [-0.0411, 0.0525] | 0.81 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | ON | 0.0336 [-0.0145, 0.0791] | 0.225 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | IN | 0.0126 [-0.0418, 0.0625] | 0.796 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | RI (primary) | 0.0238 [-0.0113, 0.0582] | 0.165 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | OI (primary) | 0.0426 [-0.0154, 0.102] | 0.165 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | RO | 0.0301 [-0.0065, 0.0665] | 0.105 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | RN | 0.000245 [-0.0285, 0.0271] | 1 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | ON | -0.00336 [-0.0361, 0.0312] | 1 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | IN | -0.00321 [-0.0295, 0.0254] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RI (primary) | 0.0291 [-0.0155, 0.0747] | 0.212 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | OI (primary) | 0.0435 [0.00841, 0.0782] | 0.003 | interaction gain detected | small |
| H=120 (4.00 LT) | oracle | RO | -0.0316 [-0.097, 0.03] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RN | -0.0335 [-0.096, 0.0276] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | ON | 0.0315 [-0.0201, 0.0825] | 0.212 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | IN | 0.00998 [-0.0248, 0.0424] | 0.679 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RI (primary) | 0.0185 [-0.0118, 0.0479] | 0.0795 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | OI (primary) | 0.0591 [0.0182, 0.0977] | 0.003 | interaction gain detected | small |
| H=120 (4.00 LT) | deployable | RO | 0.0323 [-0.0102, 0.0783] | 0.0795 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RN | 0.0292 [-0.00649, 0.0683] | 0.072 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | ON | 0.03 [-0.00338, 0.0637] | 0.0425 | interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | IN | 0.0175 [-0.00877, 0.0432] | 0.0795 | no interaction gain detected | negligible |

### D. Allocation ladder (rung against the full profile)

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED. MSE ratio MSE(rung)/MSE(F) at level 1 - 0.05/m (m rungs); Holm p for Delta MSE > 0. Theory gap L_A(oracle F) is an upper bound; estimation gap = L_A(deployable F) - L_A(oracle F) (95%).

| horizon | profile | rung | MSE | MSE ratio vs F [CI] | reading | Holm p |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | none | 0.00117 | 0.969 [0.689, 1.1] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | separation | 0.00117 | 0.962 [0.798, 1.06] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | RO | 0.00116 | 0.959 [0.778, 1.09] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | R | 0.00114 | 0.942 [0.655, 1.08] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | O | 0.0012 | 0.989 [0.8, 1.14] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | I | 0.00118 | 0.972 [0.691, 1.11] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | N | 0.00117 | 0.965 [0.685, 1.1] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | F (ROIN) | 0.00121 | 1 | | |
| H=8 (0.27 LT) | oracle | X | 0.00118 | 0.972 [0.694, 1.11] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | X+F | 0.00115 | 0.952 [0.761, 1.04] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | none | 0.00062 | 0.996 [0.971, 1.02] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | A2 (stored) | 0.000621 | 0.997 [0.972, 1.02] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | separation | 0.000687 | 1.1 [1.06, 1.15] | undetermined (n_eff < 50) | 0.006 |
| H=8 (0.27 LT) | deployable | A4 (stored) | 0.000687 | 1.1 [1.06, 1.15] | undetermined (n_eff < 50) | 0.006 |
| H=8 (0.27 LT) | deployable | RO | 0.000621 | 0.997 [0.986, 1.01] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | R | 0.000621 | 0.997 [0.985, 1.01] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | O | 0.000626 | 1.01 [0.978, 1.03] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | I | 0.000621 | 0.998 [0.972, 1.02] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | N | 0.000625 | 1 [0.98, 1.02] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | F (ROIN) | 0.000623 | 1 | | |
| H=8 (0.27 LT) | deployable | X | 0.000625 | 1 [0.979, 1.03] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | A3 (stored) | 0.000687 | 1.1 [1.04, 1.17] | undetermined (n_eff < 50) | 0.006 |
| H=8 (0.27 LT) | deployable | X+F | 0.000624 | 1 [0.992, 1.01] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | oracle | none | 0.00356 | 1.05 [1.01, 1.1] | undetermined (n_eff < 50) | 0.0045 |
| H=15 (0.50 LT) | oracle | separation | 0.00327 | 0.965 [0.89, 1.05] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | oracle | RO | 0.00339 | 1 [0.983, 1.02] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | oracle | R | 0.00349 | 1.03 [1.01, 1.06] | undetermined (n_eff < 50) | 0.0045 |
| H=15 (0.50 LT) | oracle | O | 0.00353 | 1.04 [0.969, 1.14] | undetermined (n_eff < 50) | 0.392 |
| H=15 (0.50 LT) | oracle | I | 0.00357 | 1.05 [1.01, 1.1] | undetermined (n_eff < 50) | 0.0045 |
| H=15 (0.50 LT) | oracle | N | 0.00351 | 1.03 [1, 1.07] | undetermined (n_eff < 50) | 0.009 |
| H=15 (0.50 LT) | oracle | F (ROIN) | 0.00339 | 1 | | |
| H=15 (0.50 LT) | oracle | X | 0.00358 | 1.05 [1.01, 1.12] | undetermined (n_eff < 50) | 0.009 |
| H=15 (0.50 LT) | oracle | X+F | 0.00337 | 0.992 [0.976, 1] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | none | 0.00286 | 0.995 [0.964, 1.03] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | A2 (stored) | 0.00286 | 0.995 [0.965, 1.03] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | separation | 0.00298 | 1.04 [0.975, 1.1] | undetermined (n_eff < 50) | 0.335 |
| H=15 (0.50 LT) | deployable | A4 (stored) | 0.00298 | 1.04 [0.975, 1.1] | undetermined (n_eff < 50) | 0.335 |
| H=15 (0.50 LT) | deployable | RO | 0.00286 | 0.996 [0.982, 1.01] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | R | 0.00285 | 0.991 [0.971, 1.01] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | O | 0.00286 | 0.998 [0.96, 1.03] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | I | 0.00285 | 0.991 [0.96, 1.02] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | N | 0.00286 | 0.997 [0.975, 1.02] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | F (ROIN) | 0.00287 | 1 | | |
| H=15 (0.50 LT) | deployable | X | 0.00285 | 0.994 [0.941, 1.04] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | A3 (stored) | 0.00303 | 1.06 [0.982, 1.14] | undetermined (n_eff < 50) | 0.168 |
| H=15 (0.50 LT) | deployable | X+F | 0.00284 | 0.988 [0.976, 1] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | none | 0.0186 | 1.07 [1.03, 1.12] | needed, size not determined | 0.0045 |
| H=30 (1.00 LT) | oracle | separation | 0.0168 | 0.967 [0.931, 0.999] | lowers | 0.998 |
| H=30 (1.00 LT) | oracle | RO | 0.0182 | 1.05 [0.98, 1.15] | undetermined | 0.106 |
| H=30 (1.00 LT) | oracle | R | 0.0177 | 1.02 [0.993, 1.06] | undetermined | 0.088 |
| H=30 (1.00 LT) | oracle | O | 0.0192 | 1.1 [1.05, 1.17] | substantial | 0.0045 |
| H=30 (1.00 LT) | oracle | I | 0.0184 | 1.06 [1.03, 1.11] | needed, size not determined | 0.0045 |
| H=30 (1.00 LT) | oracle | N | 0.0183 | 1.06 [1.02, 1.09] | needed, size not determined | 0.0045 |
| H=30 (1.00 LT) | oracle | F (ROIN) | 0.0173 | 1 | | |
| H=30 (1.00 LT) | oracle | X | 0.0189 | 1.09 [1.05, 1.15] | needed, size not determined | 0.0045 |
| H=30 (1.00 LT) | oracle | X+F | 0.0175 | 1.01 [0.985, 1.05] | negligible | 0.598 |
| H=30 (1.00 LT) | deployable | none | 0.0189 | 1.02 [0.962, 1.08] | undetermined | 1 |
| H=30 (1.00 LT) | deployable | A2 (stored) | 0.0189 | 1.02 [0.96, 1.08] | undetermined | 1 |
| H=30 (1.00 LT) | deployable | separation | 0.0189 | 1.02 [0.962, 1.08] | undetermined | 1 |
| H=30 (1.00 LT) | deployable | A4 (stored) | 0.0189 | 1.02 [0.962, 1.08] | undetermined | 1 |
| H=30 (1.00 LT) | deployable | RO | 0.0187 | 1.01 [0.998, 1.02] | negligible | 0.13 |
| H=30 (1.00 LT) | deployable | R | 0.0187 | 1.01 [0.973, 1.05] | undetermined | 1 |
| H=30 (1.00 LT) | deployable | O | 0.019 | 1.02 [0.976, 1.08] | undetermined | 0.918 |
| H=30 (1.00 LT) | deployable | I | 0.0187 | 1.01 [0.953, 1.06] | undetermined | 1 |
| H=30 (1.00 LT) | deployable | N | 0.0191 | 1.03 [0.973, 1.08] | undetermined | 0.918 |
| H=30 (1.00 LT) | deployable | A5 (stored) | 0.0188 | 1.01 [0.963, 1.06] | undetermined | 1 |
| H=30 (1.00 LT) | deployable | F (ROIN) | 0.0186 | 1 | | |
| H=30 (1.00 LT) | deployable | X | 0.0191 | 1.03 [0.963, 1.1] | undetermined | 1 |
| H=30 (1.00 LT) | deployable | A3 (stored) | 0.0193 | 1.04 [0.965, 1.12] | undetermined | 0.858 |
| H=30 (1.00 LT) | deployable | X+F | 0.0186 | 0.999 [0.976, 1.02] | negligible | 1 |
| H=60 (2.00 LT) | oracle | none | 0.201 | 1.05 [1.02, 1.08] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | separation | 0.194 | 1.01 [0.992, 1.04] | negligible | 0.074 |
| H=60 (2.00 LT) | oracle | RO | 0.192 | 1 [0.996, 1] | negligible | 0.426 |
| H=60 (2.00 LT) | oracle | R | 0.196 | 1.03 [1.01, 1.04] | small | 0.0045 |
| H=60 (2.00 LT) | oracle | O | 0.198 | 1.03 [1, 1.06] | needed, size not determined | 0.0125 |
| H=60 (2.00 LT) | oracle | I | 0.199 | 1.04 [1.01, 1.07] | needed, size not determined | 0.007 |
| H=60 (2.00 LT) | oracle | N | 0.197 | 1.03 [1, 1.05] | undetermined | 0.0125 |
| H=60 (2.00 LT) | oracle | F (ROIN) | 0.191 | 1 | | |
| H=60 (2.00 LT) | oracle | X | 0.199 | 1.04 [1.01, 1.07] | needed, size not determined | 0.009 |
| H=60 (2.00 LT) | oracle | X+F | 0.192 | 1 [1, 1.01] | small | 0.0125 |
| H=60 (2.00 LT) | deployable | none | 0.202 | 1.04 [1.02, 1.06] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | A2 (stored) | 0.202 | 1.04 [1.02, 1.06] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | separation | 0.203 | 1.04 [1.02, 1.07] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | A4 (stored) | 0.203 | 1.04 [1.02, 1.07] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | RO | 0.196 | 1 [1, 1.01] | small | 0.006 |
| H=60 (2.00 LT) | deployable | R | 0.201 | 1.03 [1.02, 1.05] | small | 0.006 |
| H=60 (2.00 LT) | deployable | O | 0.198 | 1.02 [0.998, 1.03] | negligible | 0.011 |
| H=60 (2.00 LT) | deployable | I | 0.2 | 1.03 [1.01, 1.05] | small | 0.006 |
| H=60 (2.00 LT) | deployable | N | 0.199 | 1.02 [1.01, 1.04] | small | 0.006 |
| H=60 (2.00 LT) | deployable | F (ROIN) | 0.195 | 1 | | |
| H=60 (2.00 LT) | deployable | X | 0.2 | 1.03 [1.01, 1.05] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | A3 (stored) | 0.203 | 1.04 [1.01, 1.07] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | X+F | 0.195 | 1 [0.999, 1.01] | negligible | 0.013 |
| H=120 (4.00 LT) | oracle | none | 0.647 | 1.03 [1.02, 1.04] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | separation | 0.662 | 1.05 [1.04, 1.07] | needed, size not determined | 0.0045 |
| H=120 (4.00 LT) | oracle | RO | 0.63 | 1 [1, 1.01] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | R | 0.635 | 1.01 [1, 1.02] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | O | 0.643 | 1.02 [1.01, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | I | 0.642 | 1.02 [1.01, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | N | 0.641 | 1.02 [1.01, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | F (ROIN) | 0.629 | 1 | | |
| H=120 (4.00 LT) | oracle | X | 0.644 | 1.03 [1.01, 1.04] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | X+F | 0.632 | 1.01 [0.999, 1.01] | negligible | 0.0135 |
| H=120 (4.00 LT) | deployable | none | 0.638 | 1.02 [1.01, 1.03] | small | 0.006 |
| H=120 (4.00 LT) | deployable | A2 (stored) | 0.638 | 1.02 [1.01, 1.03] | small | 0.006 |
| H=120 (4.00 LT) | deployable | separation | 0.667 | 1.07 [1.05, 1.09] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | A4 (stored) | 0.667 | 1.07 [1.05, 1.09] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | RO | 0.626 | 1 [1, 1.01] | negligible | 0.009 |
| H=120 (4.00 LT) | deployable | R | 0.633 | 1.01 [1.01, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | O | 0.632 | 1.01 [1, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | I | 0.632 | 1.01 [1, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | N | 0.632 | 1.01 [1.01, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | F (ROIN) | 0.624 | 1 | | |
| H=120 (4.00 LT) | deployable | X | 0.636 | 1.02 [1.01, 1.03] | small | 0.006 |
| H=120 (4.00 LT) | deployable | A3 (stored) | 0.655 | 1.05 [1.03, 1.07] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | X+F | 0.624 | 1 [0.993, 1.01] | negligible | 0.405 |

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| horizon | theory gap (upper bound) [CI] | estimation gap [CI] | gap with R estimated | gap with O estimated | gap with I estimated | gap with N estimated |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 0.000191 [6.56e-05, 0.000383] | -0.00059 [-0.00168, 2.68e-05] | -0.000418 [-0.00132, 5.54e-05] | -0.00064 [-0.00174, -2.48e-05] | -0.000588 [-0.00161, -3.38e-05] | -0.000474 [-0.00144, 3.12e-05] |
| H=15 (0.50 LT) | 0.000619 [0.000369, 0.00101] | -0.000521 [-0.00211, 0.000399] | -0.000593 [-0.00218, 0.000328] | -0.000671 [-0.00226, 0.000269] | -0.000716 [-0.0023, 0.000182] | -0.000688 [-0.00227, 0.000216] |
| H=30 (1.00 LT) | 0.00541 [0.00407, 0.00695] | 0.00123 [-0.00211, 0.00449] | 0.00103 [-0.00221, 0.00431] | 0.000327 [-0.00297, 0.00359] | 0.000385 [-0.00285, 0.00369] | 0.000389 [-0.00288, 0.00366] |
| H=60 (2.00 LT) | 0.0605 [0.0548, 0.0671] | 0.00328 [-0.0077, 0.0137] | 0.00319 [-0.00747, 0.0136] | -0.000453 [-0.0108, 0.01] | -0.000919 [-0.0111, 0.00957] | -0.000948 [-0.0108, 0.00918] |
| H=120 (4.00 LT) | 0.177 [0.169, 0.187] | -0.00478 [-0.0184, 0.00963] | -0.00503 [-0.0187, 0.00951] | -0.00967 [-0.0237, 0.00474] | -0.00897 [-0.0231, 0.00577] | -0.00882 [-0.023, 0.00556] |

### Horizon decision (Y = ln min(T_c, H_max))

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED. Pinball loss at tau = 0.5; drop-one ratio at level 1 - 0.05/4; ladder ratio vs F at 1 - 0.05/m; C = Harrell's C (95%); coverage of q_0.1, q_0.5, q_0.9 and the 80% interval below the cap.

| profile | X | pinball ratio [CI] | reading | Holm p | phi [CI] |
|---|---|---|---|---|---|
| oracle | R | 1.01 [0.996, 1.02] | negligible | 0.053 | 0.000953 [0.00013, 0.00177] |
| oracle | O | 1.06 [1.05, 1.08] | needed, size not determined | 0.002 | 0.0156 [0.0133, 0.0178] |
| oracle | I | 1.25 [1.22, 1.29] | substantial | 0.002 | 0.0456 [0.0415, 0.0498] |
| oracle | N | 1.01 [1, 1.02] | small | 0.006 | 0.00292 [0.00224, 0.00362] |
| deployable | R | 1.01 [0.999, 1.01] | negligible | 0.043 | 0.000851 [0.000338, 0.00135] |
| deployable | O | 1.08 [1.07, 1.1] | substantial | 0.002 | 0.0192 [0.0168, 0.0217] |
| deployable | I | 1.23 [1.2, 1.26] | substantial | 0.002 | 0.0442 [0.0404, 0.0481] |
| deployable | N | 0.993 [0.987, 0.999] | lowers | 0.999 | 0.0012 [0.000698, 0.00173] |

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | ratio vs F [CI] | reading | C [CI] | cov 0.1 / 0.5 / 0.9 / 80% |
|---|---|---|---|---|---|---|
| oracle | none | 0.229 | 1.4 [1.35, 1.45] | substantial | 0.5 [0.5, 0.5] | 0.0995 / 0.511 / 0.896 / 0.796 |
| oracle | lyapunov | 0.257 | 1.56 [1.5, 1.63] | substantial | 0.671 [0.661, 0.68] | 0.0815 / 0.471 / 0.854 / 0.825 |
| oracle | RO | 0.207 | 1.26 [1.22, 1.3] | substantial | 0.622 [0.612, 0.631] | 0.113 / 0.5 / 0.89 / 0.777 |
| oracle | R | 0.228 | 1.39 [1.34, 1.44] | substantial | 0.528 [0.519, 0.539] | 0.106 / 0.511 / 0.891 / 0.785 |
| oracle | O | 0.208 | 1.27 [1.23, 1.31] | substantial | 0.62 [0.61, 0.629] | 0.11 / 0.504 / 0.897 / 0.787 |
| oracle | I | 0.179 | 1.09 [1.06, 1.11] | substantial | 0.68 [0.671, 0.689] | 0.1 / 0.504 / 0.892 / 0.792 |
| oracle | N | 0.224 | 1.37 [1.32, 1.41] | substantial | 0.558 [0.548, 0.569] | 0.101 / 0.509 / 0.898 / 0.797 |
| oracle | ROIN | 0.164 | 1 |  | 0.713 [0.705, 0.722] | 0.158 / 0.508 / 0.888 / 0.73 |
| oracle | X | 0.177 | 1.08 [1.03, 1.12] | needed, size not determined | 0.699 [0.69, 0.708] | 0.147 / 0.49 / 0.859 / 0.712 |
| oracle | X+F | 0.138 | 0.839 [0.814, 0.861] | lowers | 0.767 [0.759, 0.775] | 0.15 / 0.5 / 0.852 / 0.701 |
| oracle | Lyapunov rank (C only) | | | | 0.666 [0.656, 0.675] | |
| deployable | none | 0.229 | 1.4 [1.35, 1.45] | substantial | 0.5 [0.5, 0.5] | 0.0995 / 0.511 / 0.896 / 0.796 |
| deployable | lyapunov | 0.258 | 1.57 [1.51, 1.63] | substantial | 0.67 [0.661, 0.679] | 0.0765 / 0.468 / 0.852 / 0.823 |
| deployable | RO | 0.203 | 1.24 [1.2, 1.28] | substantial | 0.628 [0.619, 0.637] | 0.102 / 0.507 / 0.899 / 0.796 |
| deployable | R | 0.228 | 1.39 [1.35, 1.44] | substantial | 0.529 [0.521, 0.537] | 0.101 / 0.513 / 0.894 / 0.793 |
| deployable | O | 0.204 | 1.25 [1.21, 1.28] | substantial | 0.625 [0.615, 0.634] | 0.108 / 0.506 / 0.897 / 0.789 |
| deployable | I | 0.178 | 1.09 [1.07, 1.11] | substantial | 0.683 [0.675, 0.69] | 0.096 / 0.511 / 0.895 / 0.799 |
| deployable | N | 0.226 | 1.38 [1.33, 1.42] | substantial | 0.547 [0.539, 0.556] | 0.105 / 0.508 / 0.898 / 0.793 |
| deployable | ROIN | 0.164 | 1 |  | 0.718 [0.71, 0.725] | 0.127 / 0.512 / 0.869 / 0.742 |
| deployable | X | 0.176 | 1.08 [1.04, 1.12] | needed, size not determined | 0.7 [0.691, 0.709] | 0.135 / 0.478 / 0.866 / 0.731 |
| deployable | X+F | 0.139 | 0.847 [0.826, 0.868] | lowers | 0.767 [0.76, 0.774] | 0.136 / 0.49 / 0.856 / 0.72 |
| deployable | Lyapunov rank (C only) | | | | 0.663 [0.654, 0.672] | |

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| profile | pair | Delta [CI] | Holm p | detected |
|---|---|---|---|---|
| oracle | RO | 0.000472 [-0.000148, 0.00109] | 0.105 | False |
| oracle | RI (primary) | 0.00051 [-0.00206, 0.00294] | 1 | False |
| oracle | RN | -4.6e-05 [-0.000362, 0.000291] | 1 | False |
| oracle | OI (primary) | 0.00579 [0.00343, 0.00802] | 0.003 | True |
| oracle | ON | 0.000338 [-0.00159, 0.00253] | 1 | False |
| oracle | IN | 0.000147 [-0.000502, 0.000733] | 1 | False |
| deployable | RO | 0.000663 [-0.000243, 0.00157] | 0.155 | False |
| deployable | RI (primary) | 0.000228 [-0.00106, 0.00143] | 0.984 | False |
| deployable | RN | -6.22e-05 [-0.000678, 0.000458] | 1 | False |
| deployable | OI (primary) | 0.00839 [0.00617, 0.0105] | 0.003 | True |
| deployable | ON | 0.00028 [-0.000499, 0.00103] | 0.682 | False |
| deployable | IN | -0.000435 [-0.00146, 0.000547] | 1 | False |

