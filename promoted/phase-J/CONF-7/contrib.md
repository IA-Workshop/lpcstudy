# Phase J contribution study: CONF-7

**PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.** Run `phasej-CONF-7/phasej`; analysis commit `c19ad486b93a2ee96d64ce069ec42fd440428211` (dirty: False). Every reading is an estimate; Shapley shares and interactions are predictive, not causal. Training variance is not in the intervals.

## lorenz63

**PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.**

| check | result |
|---|---|
| (f1) state_mse from per-draw errors, max rel diff | A0 0.0e+00, A1 0.0e+00, A2 0.0e+00, A3 0.0e+00, A4 0.0e+00, A5 0.0e+00 (within 1e-12: True) |
| (g) WU-0039b (b1), (b2) rows reproduced | drop-N: True, all rows: True |
| separation formula on F-hat vs stored A4 at H_ref, max abs | 2.22e-16 |
| T_c: T = 1 / e_(T-1) = theta (train, test) | 10/0, 13/0 |
| (f2) dependence bias, deployable rows (reported, not gating) | 131 rows; 30 flagged: H=8 O: dependence bias detectable (interval excludes 0), t1+t2 / V 0.05, z 0.0749; H=8 I: dependence bias detectable (interval excludes 0), t1+t2 / V 0.22, z 0.995; H=8 RI: dependence bias detectable (interval excludes 0), t1+t2 / V 0.186, z 0.937; H=8 OI: dependence bias detectable (interval excludes 0), t1+t2 / V 0.145, z 0.633; H=8 IN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.177, z 0.801; H=8 ROI: dependence bias detectable (interval excludes 0), t1+t2 / V 0.128, z 0.436; H=8 RIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.173, z 0.875; H=8 OIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.173, z 0.712; H=8 ROIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.12, z 0.504; H=8 X+F: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0296, z 0.0242; H=8 swap-N: dependence bias detectable (interval excludes 0), t1+t2 / V 0.000551, z -0.0471; H=15 O: dependence bias detectable (interval excludes 0), t1+t2 / V 0.114, z 1.15 ... |

### A. Allocation: drop-one and Shapley

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED. MSE ratio MSE(F without X)/MSE(F) at level 1 - 0.05/4 (reading by the 1.05 table, with the n_eff guard); excess ratio L_A(F without X)/L_A(F) and Holm p (Delta MSE > 0) are estimates. phi = Shapley share of L_A (95%). Oracle rows: moment form; deployable rows: realized per draw.

| horizon | profile | X | MSE ratio [CI] | reading | excess ratio | Holm p | phi_X [95% CI] | share |
|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | R | 1.1 [1.02, 1.17] | undetermined (n_eff < 50) | 1.24 | 0.002 | -0.000317 [-0.00105, 0.00033] | -0.0305 |
| H=8 (0.27 LT) | oracle | O | 2.12 [1.19, 5.67] | undetermined (n_eff < 50) | 3.75 | 0.002 | 0.00766 [0.00508, 0.0108] | 0.737 |
| H=8 (0.27 LT) | oracle | I | 1.1 [1.01, 1.18] | undetermined (n_eff < 50) | 1.25 | 0.006 | 0.00315 [0.00177, 0.00488] | 0.303 |
| H=8 (0.27 LT) | oracle | N | 0.97 [0.936, 1.06] | undetermined (n_eff < 50) | 0.926 | 0.85 | -0.000104 [-0.00122, 0.000777] | -0.0101 |
| H=8 (0.27 LT) | deployable | R | 1.03 [0.882, 1.23] | undetermined (n_eff < 50) | 1.04 | 0.588 | -0.000473 [-0.00257, 0.00127] | -0.2 |
| H=8 (0.27 LT) | deployable | O | 1.2 [1.06, 1.39] | undetermined (n_eff < 50) | 1.26 | 0.004 | 0.00211 [0.000942, 0.00341] | 0.893 |
| H=8 (0.27 LT) | deployable | I | 0.953 [0.762, 1.12] | undetermined (n_eff < 50) | 0.94 | 0.743 | 5.22e-05 [-0.00165, 0.00191] | 0.0221 |
| H=8 (0.27 LT) | deployable | N | 1.09 [0.88, 1.38] | undetermined (n_eff < 50) | 1.12 | 0.462 | 0.000672 [-0.000912, 0.00204] | 0.285 |
| H=15 (0.50 LT) | oracle | R | 1.14 [1.07, 1.25] | undetermined (n_eff < 50) | 1.88 | 0.002 | 0.00227 [9.28e-05, 0.00449] | 0.0868 |
| H=15 (0.50 LT) | oracle | O | 2.1 [1.62, 2.92] | undetermined (n_eff < 50) | 7.9 | 0.002 | 0.0162 [0.0127, 0.02] | 0.619 |
| H=15 (0.50 LT) | oracle | I | 1.07 [0.989, 1.21] | undetermined (n_eff < 50) | 1.44 | 0.043 | 0.00502 [0.00344, 0.00684] | 0.192 |
| H=15 (0.50 LT) | oracle | N | 1.07 [0.993, 1.21] | undetermined (n_eff < 50) | 1.43 | 0.043 | 0.00267 [0.000451, 0.00459] | 0.102 |
| H=15 (0.50 LT) | deployable | R | 1.23 [0.975, 1.61] | undetermined (n_eff < 50) | 1.35 | 0.046 | 0.008 [0.00304, 0.0132] | 0.597 |
| H=15 (0.50 LT) | deployable | O | 0.995 [0.94, 1.06] | undetermined (n_eff < 50) | 0.993 | 0.595 | -6.79e-05 [-0.0023, 0.00194] | -0.00507 |
| H=15 (0.50 LT) | deployable | I | 1 [0.997, 1.01] | undetermined (n_eff < 50) | 1 | 0.383 | 0.00112 [-0.000252, 0.00246] | 0.0836 |
| H=15 (0.50 LT) | deployable | N | 1.1 [0.986, 1.25] | undetermined (n_eff < 50) | 1.15 | 0.054 | 0.00434 [0.00193, 0.00668] | 0.324 |
| H=30 (1.00 LT) | oracle | R | 1.01 [0.939, 1.09] | undetermined (n_eff < 50) | 1.04 | 0.638 | 0.000275 [-0.00175, 0.00213] | 0.011 |
| H=30 (1.00 LT) | oracle | O | 1.35 [1.13, 1.68] | undetermined (n_eff < 50) | 2.14 | 0.002 | 0.0162 [0.0122, 0.0209] | 0.653 |
| H=30 (1.00 LT) | oracle | I | 1.02 [0.985, 1.05] | undetermined (n_eff < 50) | 1.05 | 0.325 | 0.00695 [0.00474, 0.00935] | 0.279 |
| H=30 (1.00 LT) | oracle | N | 0.971 [0.942, 0.998] | undetermined (n_eff < 50) | 0.905 | 0.995 | 0.0014 [-0.00088, 0.00344] | 0.0564 |
| H=30 (1.00 LT) | deployable | R | 1.07 [0.971, 1.21] | undetermined (n_eff < 50) | 1.13 | 0.198 | 0.00539 [0.00185, 0.00912] | 0.473 |
| H=30 (1.00 LT) | deployable | O | 1.02 [0.971, 1.08] | undetermined (n_eff < 50) | 1.04 | 0.466 | 0.00152 [-0.000182, 0.00348] | 0.134 |
| H=30 (1.00 LT) | deployable | I | 0.939 [0.833, 1.05] | undetermined (n_eff < 50) | 0.882 | 0.917 | 0.00173 [-0.00231, 0.00559] | 0.152 |
| H=30 (1.00 LT) | deployable | N | 1.02 [0.966, 1.07] | undetermined (n_eff < 50) | 1.04 | 0.466 | 0.00276 [0.000449, 0.00503] | 0.242 |
| H=60 (2.00 LT) | oracle | R | 1.01 [0.994, 1.03] | negligible | 1.04 | 0.141 | 0.00332 [0.00164, 0.00493] | 0.166 |
| H=60 (2.00 LT) | oracle | O | 1.07 [1.03, 1.11] | needed, size not determined | 1.25 | 0.002 | 0.014 [0.00936, 0.0187] | 0.702 |
| H=60 (2.00 LT) | oracle | I | 1 [0.985, 1.02] | negligible | 1.01 | 0.557 | 0.00269 [0.000261, 0.00502] | 0.135 |
| H=60 (2.00 LT) | oracle | N | 0.995 [0.982, 1.01] | negligible | 0.983 | 0.818 | -5.46e-05 [-0.00187, 0.00177] | -0.00274 |
| H=60 (2.00 LT) | deployable | R | 1.03 [0.999, 1.08] | undetermined | 1.09 | 0.032 | 0.00669 [0.00221, 0.0118] | 0.593 |
| H=60 (2.00 LT) | deployable | O | 1.01 [0.993, 1.03] | negligible | 1.03 | 0.177 | 0.00158 [-0.000296, 0.00335] | 0.14 |
| H=60 (2.00 LT) | deployable | I | 1.01 [0.987, 1.03] | negligible | 1.02 | 0.343 | 0.00116 [-0.0015, 0.00377] | 0.103 |
| H=60 (2.00 LT) | deployable | N | 1 [0.981, 1.02] | negligible | 1 | 0.433 | 0.00185 [-0.000317, 0.00407] | 0.164 |
| H=120 (4.00 LT) | oracle | R | 1 [0.997, 1.01] | negligible | 1.01 | 0.444 | 0.00358 [0.00149, 0.0057] | 0.295 |
| H=120 (4.00 LT) | oracle | O | 1 [0.996, 1.01] | negligible | 1.02 | 0.378 | 0.00455 [-0.0011, 0.00973] | 0.375 |
| H=120 (4.00 LT) | oracle | I | 1 [0.995, 1.01] | negligible | 1.01 | 0.444 | 0.00424 [0.00167, 0.00681] | 0.35 |
| H=120 (4.00 LT) | oracle | N | 0.999 [0.995, 1] | negligible | 0.996 | 0.786 | -0.000241 [-0.00189, 0.00139] | -0.0199 |
| H=120 (4.00 LT) | deployable | R | 1 [0.999, 1] | negligible | 1 | 0.333 | 0.00221 [0.000175, 0.0045] | 0.429 |
| H=120 (4.00 LT) | deployable | O | 0.999 [0.998, 1] | negligible | 0.998 | 0.844 | 0.000335 [-0.00162, 0.00214] | 0.0649 |
| H=120 (4.00 LT) | deployable | I | 1 [0.999, 1] | negligible | 1.01 | 0.285 | 0.0019 [-0.000232, 0.00395] | 0.369 |
| H=120 (4.00 LT) | deployable | N | 1 [1, 1] | negligible | 1 | 0.202 | 0.000708 [-0.000307, 0.0018] | 0.137 |

### A. Allocation: summary per horizon

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED. n_eff = Kish size of kappa on the test states; G = 1 - L_A(rule)/L_A(constant), estimate (95%).

| horizon | profile | n_eff(kappa) | G(F) [CI] | G(separation) | MSE(F)/MSE(sep) [CI] | reading | settings (A) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 95.1 | 0.849 [0.652, 0.977] | 0.783 | 0.851 [0.758, 1.02] | undetermined (n_eff < 50) | F: mid; qn 3, mid 6, low 6 |
| H=8 (0.27 LT) | deployable | 95.1 | 0.197 [-0.0596, 0.404] | -1.54 | 0.372 [0.26, 0.528] | lowers | F: mid; qn 1, mid 7, low 7 |
| H=15 (0.50 LT) | oracle | 101 | 0.943 [0.905, 0.969] | 0.91 | 0.914 [0.828, 0.99] | undetermined (n_eff < 50) | F: mid; qn 4, mid 5, low 6 |
| H=15 (0.50 LT) | deployable | 101 | 0.457 [0.289, 0.61] | -0.34 | 0.508 [0.379, 0.668] | lowers | F: low; qn 0, mid 5, low 10 |
| H=30 (1.00 LT) | oracle | 203 | 0.724 [0.628, 0.805] | 0.731 | 1.01 [0.955, 1.06] | undetermined (n_eff < 50) | F: mid; qn 0, mid 13, low 2 |
| H=30 (1.00 LT) | deployable | 203 | 0.336 [0.159, 0.498] | -0.282 | 0.676 [0.562, 0.797] | lowers | F: mid; qn 0, mid 10, low 5 |
| H=60 (2.00 LT) | oracle | 506 | 0.32 [0.218, 0.408] | 0.289 | 0.987 [0.954, 1.02] | negligible | F: mid; qn 0, mid 11, low 4 |
| H=60 (2.00 LT) | deployable | 506 | 0.166 [0.0605, 0.262] | -0.0715 | 0.91 [0.86, 0.957] | lowers | F: mid; qn 0, mid 8, low 7 |
| H=120 (4.00 LT) | oracle | 1.73e+03 | 0.0458 [0.0197, 0.0699] | -0.278 | 0.911 [0.896, 0.925] | lowers | F: mid; qn 0, mid 7, low 8 |
| H=120 (4.00 LT) | deployable | 1.73e+03 | 0.0203 [0.00569, 0.0345] | -0.206 | 0.938 [0.926, 0.95] | lowers | F: low; qn 0, mid 0, low 15 |

### B. Allocation: pairwise interactions (logit u, interior states)

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED. Delta = L(additive) - L(additive + pair) on the test states, models fixed; level 1 - 0.05/6; Holm over the six pairs. R x I and O x I are primary.

| horizon | profile | pair | Delta [CI] | Holm p | reading | loss ratio reading |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | RI (primary) | 0.0284 [-0.0423, 0.0932] | 0.755 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | OI (primary) | 0.0111 [-0.0436, 0.0692] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | RO | 0.106 [0.0084, 0.198] | 0.012 | interaction gain detected | needed, size not determined |
| H=8 (0.27 LT) | oracle | RN | -0.0127 [-0.0798, 0.0453] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | ON | -0.00427 [-0.0704, 0.0612] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | IN | -0.0182 [-0.0485, 0.0115] | 1 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RI (primary) | 0.0639 [0.00558, 0.128] | 0.015 | interaction gain detected | small |
| H=8 (0.27 LT) | deployable | OI (primary) | 0.00319 [-0.00227, 0.00913] | 0.244 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RO | 0.126 [0.053, 0.191] | 0.003 | interaction gain detected | small |
| H=8 (0.27 LT) | deployable | RN | 0.00694 [-0.0165, 0.0288] | 0.275 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | ON | 0.00605 [-0.00405, 0.0157] | 0.244 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | IN | 0.00204 [-0.00299, 0.00611] | 0.275 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | RI (primary) | 0.0172 [-0.0523, 0.0832] | 0.763 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | OI (primary) | 0.00114 [-0.107, 0.0971] | 0.763 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | RO | 0.149 [0.0525, 0.242] | 0.003 | interaction gain detected | needed, size not determined |
| H=15 (0.50 LT) | oracle | RN | 0.0446 [-0.0594, 0.141] | 0.642 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | ON | 0.0108 [-0.0535, 0.0725] | 0.763 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | IN | 0.0181 [-0.0227, 0.0534] | 0.642 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | RI (primary) | 0.074 [-0.0059, 0.155] | 0.036 | interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | OI (primary) | 0.0889 [0.017, 0.152] | 0.005 | interaction gain detected | small |
| H=15 (0.50 LT) | deployable | RO | 0.182 [0.0858, 0.279] | 0.003 | interaction gain detected | needed, size not determined |
| H=15 (0.50 LT) | deployable | RN | -0.00463 [-0.0273, 0.0177] | 0.715 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | ON | 0.0123 [-0.00809, 0.0349] | 0.199 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | IN | 0.0102 [-0.00841, 0.0291] | 0.199 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | RI (primary) | 0.0155 [-0.0527, 0.0891] | 1 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | OI (primary) | 0.0114 [-0.0703, 0.0895] | 1 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | RO | 0.151 [0.0331, 0.267] | 0.003 | interaction gain detected | needed, size not determined |
| H=30 (1.00 LT) | oracle | RN | -0.0548 [-0.209, 0.0775] | 1 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | ON | -0.0288 [-0.0973, 0.0387] | 1 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | IN | 0.0023 [-0.0518, 0.0589] | 1 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | RI (primary) | 0.0394 [0.00359, 0.0753] | 0.012 | interaction gain detected | small |
| H=30 (1.00 LT) | deployable | OI (primary) | 0.0297 [0.00414, 0.0562] | 0.005 | interaction gain detected | small |
| H=30 (1.00 LT) | deployable | RO | 0.0985 [0.0591, 0.142] | 0.003 | interaction gain detected | small |
| H=30 (1.00 LT) | deployable | RN | -0.00223 [-0.0394, 0.041] | 0.563 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | ON | 0.0231 [-0.0116, 0.0596] | 0.088 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | IN | 0.0354 [-0.00572, 0.0783] | 0.0465 | interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | RI (primary) | 0.0508 [-0.0549, 0.142] | 0.467 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | OI (primary) | 0.0805 [-0.0327, 0.183] | 0.204 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | RO | 0.0492 [-0.0642, 0.163] | 0.544 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | RN | -0.0209 [-0.11, 0.0698] | 1 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | ON | -0.0929 [-0.188, -0.0034] | 1 | no interaction gain; the pair model fits worse | no interaction gain; the pair model fits worse |
| H=60 (2.00 LT) | oracle | IN | 0.0228 [-0.0427, 0.0862] | 0.592 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | RI (primary) | 0.0641 [0.0149, 0.118] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | OI (primary) | 0.0546 [0.0223, 0.0907] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | RO | 0.0567 [-0.00164, 0.119] | 0.03 | interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | RN | 0.000537 [-0.0401, 0.0427] | 0.666 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | ON | 0.00593 [-0.0313, 0.0402] | 0.666 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | IN | 0.0273 [-0.0168, 0.0716] | 0.129 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RI (primary) | 0.016 [-0.02, 0.0507] | 0.41 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | OI (primary) | 0.0392 [0.00121, 0.078] | 0.024 | interaction gain detected | small |
| H=120 (4.00 LT) | oracle | RO | 0.00701 [-0.0307, 0.047] | 0.633 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RN | 0.00692 [-0.0189, 0.0305] | 0.633 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | ON | 0.0023 [-0.0257, 0.0319] | 0.633 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | IN | 0.0195 [-0.0114, 0.0521] | 0.297 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RI (primary) | 0.00335 [-0.00991, 0.0189] | 0.826 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | OI (primary) | 0.00051 [-0.00996, 0.0105] | 0.908 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RO | 0.000256 [-0.00839, 0.00928] | 0.908 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RN | 0.0147 [-0.000618, 0.0298] | 0.039 | interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | ON | 0.00678 [-0.00595, 0.0193] | 0.372 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | IN | 0.00605 [-0.00821, 0.0219] | 0.57 | no interaction gain detected | negligible |

### D. Allocation ladder (rung against the full profile)

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED. MSE ratio MSE(rung)/MSE(F) at level 1 - 0.05/m (m rungs); Holm p for Delta MSE > 0. Theory gap L_A(oracle F) is an upper bound; estimation gap = L_A(deployable F) - L_A(oracle F) (95%).

| horizon | profile | rung | MSE | MSE ratio vs F [CI] | reading | Holm p |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | none | 0.0149 | 3.28 [1.81, 10.6] | undetermined (n_eff < 50) | 0.0045 |
| H=8 (0.27 LT) | oracle | separation | 0.00536 | 1.18 [0.937, 1.37] | undetermined (n_eff < 50) | 0.188 |
| H=8 (0.27 LT) | oracle | RO | 0.00431 | 0.944 [0.817, 1.2] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | R | 0.0165 | 3.63 [1.98, 11.7] | undetermined (n_eff < 50) | 0.0045 |
| H=8 (0.27 LT) | oracle | O | 0.00494 | 1.08 [1.01, 1.2] | undetermined (n_eff < 50) | 0.012 |
| H=8 (0.27 LT) | oracle | I | 0.00886 | 1.94 [0.921, 5.78] | undetermined (n_eff < 50) | 0.0325 |
| H=8 (0.27 LT) | oracle | N | 0.0149 | 3.27 [1.91, 10.1] | undetermined (n_eff < 50) | 0.0045 |
| H=8 (0.27 LT) | oracle | F (ROIN) | 0.00456 | 1 | | |
| H=8 (0.27 LT) | oracle | X | 0.00404 | 0.885 [0.429, 1.54] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | oracle | X+F | 0.00473 | 1.04 [0.945, 1.12] | undetermined (n_eff < 50) | 0.313 |
| H=8 (0.27 LT) | deployable | none | 0.0147 | 1.19 [0.849, 1.65] | undetermined (n_eff < 50) | 0.49 |
| H=8 (0.27 LT) | deployable | A2 (stored) | 0.0145 | 1.18 [0.846, 1.63] | undetermined (n_eff < 50) | 0.52 |
| H=8 (0.27 LT) | deployable | separation | 0.0331 | 2.69 [1.62, 4.56] | undetermined (n_eff < 50) | 0.006 |
| H=8 (0.27 LT) | deployable | A4 (stored) | 0.0331 | 2.69 [1.62, 4.56] | undetermined (n_eff < 50) | 0.006 |
| H=8 (0.27 LT) | deployable | RO | 0.0123 | 0.997 [0.777, 1.2] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | R | 0.0157 | 1.27 [0.969, 1.68] | undetermined (n_eff < 50) | 0.105 |
| H=8 (0.27 LT) | deployable | O | 0.0129 | 1.04 [0.792, 1.37] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | I | 0.0139 | 1.12 [0.844, 1.61] | undetermined (n_eff < 50) | 0.873 |
| H=8 (0.27 LT) | deployable | N | 0.0141 | 1.14 [0.801, 1.54] | undetermined (n_eff < 50) | 0.829 |
| H=8 (0.27 LT) | deployable | F (ROIN) | 0.0123 | 1 | | |
| H=8 (0.27 LT) | deployable | X | 0.00424 | 0.344 [0.146, 0.634] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | A3 (stored) | 0.0133 | 1.08 [0.636, 1.84] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | X+F | 0.00382 | 0.309 [0.13, 0.587] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | oracle | none | 0.036 | 3.66 [2.73, 5.25] | undetermined (n_eff < 50) | 0.0045 |
| H=15 (0.50 LT) | oracle | separation | 0.0108 | 1.09 [0.988, 1.27] | undetermined (n_eff < 50) | 0.0285 |
| H=15 (0.50 LT) | oracle | RO | 0.0104 | 1.06 [0.969, 1.22] | undetermined (n_eff < 50) | 0.0915 |
| H=15 (0.50 LT) | oracle | R | 0.0299 | 3.04 [2.09, 4.45] | undetermined (n_eff < 50) | 0.0045 |
| H=15 (0.50 LT) | oracle | O | 0.0116 | 1.18 [1.06, 1.37] | undetermined (n_eff < 50) | 0.0045 |
| H=15 (0.50 LT) | oracle | I | 0.0237 | 2.41 [1.9, 3.3] | undetermined (n_eff < 50) | 0.0045 |
| H=15 (0.50 LT) | oracle | N | 0.0294 | 2.98 [2.11, 4.56] | undetermined (n_eff < 50) | 0.0045 |
| H=15 (0.50 LT) | oracle | F (ROIN) | 0.00984 | 1 | | |
| H=15 (0.50 LT) | oracle | X | 0.014 | 1.42 [1.17, 1.81] | undetermined (n_eff < 50) | 0.0045 |
| H=15 (0.50 LT) | oracle | X+F | 0.0115 | 1.17 [0.965, 1.44] | undetermined (n_eff < 50) | 0.0285 |
| H=15 (0.50 LT) | deployable | none | 0.0376 | 1.55 [1.16, 2.18] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | A2 (stored) | 0.0377 | 1.56 [1.15, 2.22] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | separation | 0.0475 | 1.97 [1.32, 3.03] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | A4 (stored) | 0.0475 | 1.97 [1.32, 3.03] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | RO | 0.0273 | 1.13 [0.993, 1.29] | undetermined (n_eff < 50) | 0.0225 |
| H=15 (0.50 LT) | deployable | R | 0.0272 | 1.13 [1.05, 1.23] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | O | 0.0383 | 1.58 [1.22, 2.26] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | I | 0.0357 | 1.48 [1.12, 2.11] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | N | 0.0312 | 1.29 [0.966, 1.85] | undetermined (n_eff < 50) | 0.024 |
| H=15 (0.50 LT) | deployable | F (ROIN) | 0.0242 | 1 | | |
| H=15 (0.50 LT) | deployable | X | 0.0145 | 0.6 [0.401, 0.875] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | A3 (stored) | 0.0243 | 1 [0.743, 1.4] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | X+F | 0.015 | 0.621 [0.435, 0.904] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | none | 0.0556 | 1.81 [1.49, 2.37] | undetermined (n_eff < 50) | 0.0045 |
| H=30 (1.00 LT) | oracle | separation | 0.0304 | 0.991 [0.918, 1.07] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | RO | 0.0306 | 0.996 [0.958, 1.04] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | R | 0.0559 | 1.82 [1.43, 2.4] | undetermined (n_eff < 50) | 0.0045 |
| H=30 (1.00 LT) | oracle | O | 0.0337 | 1.1 [1, 1.23] | undetermined (n_eff < 50) | 0.0175 |
| H=30 (1.00 LT) | oracle | I | 0.0411 | 1.34 [1.16, 1.61] | undetermined (n_eff < 50) | 0.0045 |
| H=30 (1.00 LT) | oracle | N | 0.0508 | 1.65 [1.35, 2.16] | undetermined (n_eff < 50) | 0.0045 |
| H=30 (1.00 LT) | oracle | F (ROIN) | 0.0307 | 1 | | |
| H=30 (1.00 LT) | oracle | X | 0.0314 | 1.02 [0.92, 1.13] | undetermined (n_eff < 50) | 0.986 |
| H=30 (1.00 LT) | oracle | X+F | 0.0297 | 0.968 [0.929, 1] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | deployable | none | 0.0551 | 1.26 [1.05, 1.56] | undetermined (n_eff < 50) | 0.0065 |
| H=30 (1.00 LT) | deployable | A2 (stored) | 0.0555 | 1.27 [1.05, 1.58] | undetermined (n_eff < 50) | 0.0065 |
| H=30 (1.00 LT) | deployable | separation | 0.0647 | 1.48 [1.17, 1.9] | undetermined (n_eff < 50) | 0.0065 |
| H=30 (1.00 LT) | deployable | A4 (stored) | 0.0647 | 1.48 [1.17, 1.9] | undetermined (n_eff < 50) | 0.0065 |
| H=30 (1.00 LT) | deployable | RO | 0.0428 | 0.979 [0.828, 1.14] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | deployable | R | 0.049 | 1.12 [0.949, 1.36] | undetermined (n_eff < 50) | 0.212 |
| H=30 (1.00 LT) | deployable | O | 0.0542 | 1.24 [1.03, 1.55] | undetermined (n_eff < 50) | 0.0135 |
| H=30 (1.00 LT) | deployable | I | 0.0499 | 1.14 [0.982, 1.34] | undetermined (n_eff < 50) | 0.036 |
| H=30 (1.00 LT) | deployable | N | 0.0511 | 1.17 [0.989, 1.4] | undetermined (n_eff < 50) | 0.0385 |
| H=30 (1.00 LT) | deployable | A5 (stored) | 0.0496 | 1.13 [0.974, 1.37] | undetermined (n_eff < 50) | 0.0385 |
| H=30 (1.00 LT) | deployable | F (ROIN) | 0.0437 | 1 | | |
| H=30 (1.00 LT) | deployable | X | 0.0324 | 0.742 [0.57, 0.909] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | deployable | A3 (stored) | 0.0409 | 0.935 [0.733, 1.12] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | deployable | X+F | 0.0345 | 0.79 [0.627, 0.934] | undetermined (n_eff < 50) | 1 |
| H=60 (2.00 LT) | oracle | none | 0.168 | 1.13 [1.06, 1.22] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | separation | 0.15 | 1.01 [0.962, 1.06] | undetermined | 0.687 |
| H=60 (2.00 LT) | oracle | RO | 0.149 | 1 [0.971, 1.02] | negligible | 0.867 |
| H=60 (2.00 LT) | oracle | R | 0.165 | 1.11 [1.04, 1.18] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | O | 0.152 | 1.02 [0.987, 1.06] | undetermined | 0.146 |
| H=60 (2.00 LT) | oracle | I | 0.165 | 1.11 [1.05, 1.17] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | N | 0.17 | 1.15 [1.08, 1.23] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | F (ROIN) | 0.148 | 1 | | |
| H=60 (2.00 LT) | oracle | X | 0.154 | 1.04 [0.988, 1.1] | undetermined | 0.08 |
| H=60 (2.00 LT) | oracle | X+F | 0.146 | 0.981 [0.954, 1.01] | negligible | 0.977 |
| H=60 (2.00 LT) | deployable | none | 0.174 | 1.07 [1, 1.14] | needed, size not determined | 0.016 |
| H=60 (2.00 LT) | deployable | A2 (stored) | 0.174 | 1.07 [1, 1.14] | needed, size not determined | 0.016 |
| H=60 (2.00 LT) | deployable | separation | 0.179 | 1.1 [1.02, 1.2] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | A4 (stored) | 0.179 | 1.1 [1.02, 1.2] | needed, size not determined | 0.006 |
| H=60 (2.00 LT) | deployable | RO | 0.165 | 1.02 [0.978, 1.05] | undetermined | 0.498 |
| H=60 (2.00 LT) | deployable | R | 0.166 | 1.02 [0.98, 1.06] | undetermined | 0.412 |
| H=60 (2.00 LT) | deployable | O | 0.173 | 1.07 [1, 1.13] | needed, size not determined | 0.015 |
| H=60 (2.00 LT) | deployable | I | 0.172 | 1.06 [1, 1.12] | needed, size not determined | 0.015 |
| H=60 (2.00 LT) | deployable | N | 0.172 | 1.05 [0.995, 1.12] | undetermined | 0.033 |
| H=60 (2.00 LT) | deployable | F (ROIN) | 0.163 | 1 | | |
| H=60 (2.00 LT) | deployable | X | 0.159 | 0.979 [0.927, 1.03] | negligible | 1 |
| H=60 (2.00 LT) | deployable | A3 (stored) | 0.163 | 1 [0.928, 1.07] | undetermined | 1 |
| H=60 (2.00 LT) | deployable | X+F | 0.157 | 0.962 [0.925, 0.995] | lowers | 1 |
| H=120 (4.00 LT) | oracle | none | 0.887 | 1.01 [1, 1.02] | small | 0.007 |
| H=120 (4.00 LT) | oracle | separation | 0.96 | 1.1 [1.07, 1.12] | substantial | 0.0045 |
| H=120 (4.00 LT) | oracle | RO | 0.88 | 1.01 [1, 1.01] | small | 0.015 |
| H=120 (4.00 LT) | oracle | R | 0.882 | 1.01 [0.997, 1.02] | negligible | 0.0585 |
| H=120 (4.00 LT) | oracle | O | 0.883 | 1.01 [1, 1.02] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | I | 0.883 | 1.01 [1, 1.02] | small | 0.015 |
| H=120 (4.00 LT) | oracle | N | 0.887 | 1.01 [1, 1.02] | small | 0.007 |
| H=120 (4.00 LT) | oracle | F (ROIN) | 0.875 | 1 | | |
| H=120 (4.00 LT) | oracle | X | 0.873 | 0.998 [0.987, 1.01] | negligible | 1 |
| H=120 (4.00 LT) | oracle | X+F | 0.868 | 0.993 [0.986, 0.999] | lowers | 1 |
| H=120 (4.00 LT) | deployable | none | 0.876 | 1.01 [1, 1.01] | small | 0.0225 |
| H=120 (4.00 LT) | deployable | A2 (stored) | 0.876 | 1.01 [1, 1.01] | small | 0.0225 |
| H=120 (4.00 LT) | deployable | separation | 0.929 | 1.07 [1.05, 1.09] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | A4 (stored) | 0.929 | 1.07 [1.05, 1.09] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | RO | 0.873 | 1 [0.999, 1.01] | negligible | 0.24 |
| H=120 (4.00 LT) | deployable | R | 0.873 | 1 [0.998, 1.01] | negligible | 0.282 |
| H=120 (4.00 LT) | deployable | O | 0.875 | 1 [1, 1.01] | small | 0.0225 |
| H=120 (4.00 LT) | deployable | I | 0.874 | 1 [0.998, 1.01] | negligible | 0.24 |
| H=120 (4.00 LT) | deployable | N | 0.876 | 1.01 [0.999, 1.01] | negligible | 0.072 |
| H=120 (4.00 LT) | deployable | F (ROIN) | 0.871 | 1 | | |
| H=120 (4.00 LT) | deployable | X | 0.867 | 0.995 [0.985, 1] | negligible | 1 |
| H=120 (4.00 LT) | deployable | A3 (stored) | 0.893 | 1.02 [1.01, 1.04] | small | 0.006 |
| H=120 (4.00 LT) | deployable | X+F | 0.867 | 0.995 [0.987, 1] | negligible | 1 |

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| horizon | theory gap (upper bound) [CI] | estimation gap [CI] | gap with R estimated | gap with O estimated | gap with I estimated | gap with N estimated |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 0.00185 [0.000251, 0.00486] | 0.00778 [0.00486, 0.0114] | 0.00015 [-0.000177, 0.000537] | 0.00436 [0.00178, 0.0073] | 0.000178 [-9.79e-05, 0.00051] | -4.59e-05 [-0.000438, 0.000334] |
| H=15 (0.50 LT) | 0.00157 [0.000867, 0.00261] | 0.0143 [0.00909, 0.0204] | 0.000952 [-0.00148, 0.00384] | 0.0102 [0.00542, 0.0154] | 0.000197 [-0.00215, 0.00297] | -7.22e-05 [-0.00243, 0.00262] |
| H=30 (1.00 LT) | 0.00949 [0.00653, 0.0129] | 0.013 [0.00584, 0.0208] | 0.000182 [-0.00449, 0.00463] | 0.00961 [0.00252, 0.0175] | -0.000722 [-0.00497, 0.00337] | -0.00133 [-0.00535, 0.00259] |
| H=60 (2.00 LT) | 0.0425 [0.0365, 0.0489] | 0.0144 [0.0021, 0.0268] | 0.00704 [-0.00498, 0.0189] | 0.012 [-0.00108, 0.0247] | 0.00326 [-0.00834, 0.0148] | 0.00304 [-0.00858, 0.0146] |
| H=120 (4.00 LT) | 0.253 [0.241, 0.265] | -0.00354 [-0.029, 0.0217] | -0.00643 [-0.0318, 0.0174] | -0.00345 [-0.029, 0.0219] | -0.00539 [-0.0311, 0.0182] | -0.00843 [-0.0335, 0.0159] |

### Horizon decision (Y = ln min(T_c, H_max))

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED. Pinball loss at tau = 0.5; drop-one ratio at level 1 - 0.05/4; ladder ratio vs F at 1 - 0.05/m; C = Harrell's C (95%); coverage of q_0.1, q_0.5, q_0.9 and the 80% interval below the cap.

| profile | X | pinball ratio [CI] | reading | Holm p | phi [CI] |
|---|---|---|---|---|---|
| oracle | R | 1.01 [0.99, 1.03] | negligible | 0.198 | 0.00174 [0.000655, 0.0028] |
| oracle | O | 1.07 [1.05, 1.09] | substantial | 0.002 | 0.00783 [0.00632, 0.00946] |
| oracle | I | 1.22 [1.17, 1.27] | substantial | 0.002 | 0.0287 [0.0247, 0.0331] |
| oracle | N | 0.995 [0.979, 1.01] | negligible | 0.82 | 0.00155 [0.00049, 0.00254] |
| deployable | R | 0.995 [0.984, 1.01] | negligible | 0.848 | 0.00127 [0.000643, 0.00193] |
| deployable | O | 1.07 [1.06, 1.09] | substantial | 0.002 | 0.0086 [0.00733, 0.00984] |
| deployable | I | 1.21 [1.17, 1.25] | substantial | 0.002 | 0.0274 [0.0236, 0.0313] |
| deployable | N | 1.01 [0.999, 1.01] | negligible | 0.028 | 0.00122 [0.0006, 0.00181] |

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | ratio vs F [CI] | reading | C [CI] | cov 0.1 / 0.5 / 0.9 / 80% |
|---|---|---|---|---|---|---|
| oracle | none | 0.197 | 1.25 [1.2, 1.31] | substantial | 0.5 [0.5, 0.5] | 0.111 / 0.509 / 0.889 / 0.778 |
| oracle | lyapunov | 0.3 | 1.92 [1.83, 2.01] | substantial | 0.613 [0.602, 0.625] | 0.0843 / 0.481 / 0.856 / 0.815 |
| oracle | RO | 0.193 | 1.23 [1.18, 1.29] | substantial | 0.564 [0.554, 0.574] | 0.143 / 0.496 / 0.893 / 0.75 |
| oracle | R | 0.195 | 1.25 [1.2, 1.3] | substantial | 0.535 [0.525, 0.545] | 0.13 / 0.505 / 0.894 / 0.765 |
| oracle | O | 0.194 | 1.24 [1.19, 1.3] | substantial | 0.547 [0.537, 0.557] | 0.134 / 0.507 / 0.897 / 0.763 |
| oracle | I | 0.175 | 1.12 [1.08, 1.16] | substantial | 0.624 [0.613, 0.636] | 0.12 / 0.523 / 0.881 / 0.761 |
| oracle | N | 0.194 | 1.24 [1.18, 1.29] | substantial | 0.563 [0.552, 0.572] | 0.109 / 0.506 / 0.9 / 0.791 |
| oracle | ROIN | 0.157 | 1 |  | 0.679 [0.668, 0.689] | 0.158 / 0.518 / 0.859 / 0.701 |
| oracle | X | 0.166 | 1.06 [1.01, 1.11] | needed, size not determined | 0.679 [0.668, 0.689] | 0.155 / 0.503 / 0.86 / 0.704 |
| oracle | X+F | 0.137 | 0.874 [0.851, 0.897] | lowers | 0.726 [0.716, 0.736] | 0.166 / 0.505 / 0.855 / 0.689 |
| oracle | Lyapunov rank (C only) | | | | 0.607 [0.595, 0.618] | |
| deployable | none | 0.197 | 1.24 [1.2, 1.29] | substantial | 0.5 [0.5, 0.5] | 0.111 / 0.509 / 0.889 / 0.778 |
| deployable | lyapunov | 0.295 | 1.86 [1.77, 1.96] | substantial | 0.614 [0.602, 0.625] | 0.0795 / 0.49 / 0.856 / 0.818 |
| deployable | RO | 0.193 | 1.22 [1.18, 1.26] | substantial | 0.561 [0.552, 0.57] | 0.125 / 0.509 / 0.896 / 0.771 |
| deployable | R | 0.195 | 1.23 [1.19, 1.28] | substantial | 0.531 [0.523, 0.54] | 0.116 / 0.502 / 0.897 / 0.781 |
| deployable | O | 0.193 | 1.22 [1.18, 1.27] | substantial | 0.551 [0.541, 0.56] | 0.108 / 0.508 / 0.894 / 0.786 |
| deployable | I | 0.177 | 1.12 [1.09, 1.15] | substantial | 0.615 [0.605, 0.625] | 0.116 / 0.516 / 0.891 / 0.775 |
| deployable | N | 0.195 | 1.23 [1.19, 1.28] | substantial | 0.546 [0.538, 0.554] | 0.108 / 0.503 / 0.899 / 0.791 |
| deployable | ROIN | 0.158 | 1 |  | 0.678 [0.668, 0.688] | 0.135 / 0.509 / 0.871 / 0.737 |
| deployable | X | 0.165 | 1.04 [1, 1.09] | needed, size not determined | 0.681 [0.671, 0.691] | 0.155 / 0.508 / 0.868 / 0.713 |
| deployable | X+F | 0.141 | 0.892 [0.871, 0.912] | lowers | 0.722 [0.712, 0.731] | 0.158 / 0.505 / 0.863 / 0.705 |
| deployable | Lyapunov rank (C only) | | | | 0.61 [0.598, 0.621] | |

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| profile | pair | Delta [CI] | Holm p | detected |
|---|---|---|---|---|
| oracle | RO | 0.00351 [-0.000371, 0.00801] | 0.021 | True |
| oracle | RI (primary) | 0.00463 [0.000432, 0.00897] | 0.006 | True |
| oracle | RN | 0.000535 [-0.00397, 0.00538] | 0.369 | False |
| oracle | OI (primary) | 0.015 [0.0102, 0.0206] | 0.003 | True |
| oracle | ON | 0.000577 [4.85e-05, 0.00113] | 0.0075 | True |
| oracle | IN | 0.00133 [0.00033, 0.00234] | 0.003 | True |
| deployable | RO | 0.00133 [0.000369, 0.00231] | 0.003 | True |
| deployable | RI (primary) | 0.0033 [0.000898, 0.00588] | 0.003 | True |
| deployable | RN | -0.000909 [-0.00191, 2.16e-05] | 0.994 | False |
| deployable | OI (primary) | 0.015 [0.0119, 0.0184] | 0.003 | True |
| deployable | ON | 0.00138 [0.00064, 0.00217] | 0.003 | True |
| deployable | IN | 2.95e-05 [-0.00103, 0.00111] | 0.931 | False |

## rossler

**PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.**

| check | result |
|---|---|
| (f1) state_mse from per-draw errors, max rel diff | A0 0.0e+00, A1 0.0e+00, A2 0.0e+00, A3 0.0e+00, A4 0.0e+00, A5 0.0e+00 (within 1e-12: True) |
| (g) WU-0039b (b1), (b2) rows reproduced | drop-N: True, all rows: True |
| separation formula on F-hat vs stored A4 at H_ref, max abs | 2.22e-16 |
| T_c: T = 1 / e_(T-1) = theta (train, test) | 0/0, 0/0 |
| (f2) dependence bias, deployable rows (reported, not gating) | 131 rows; 70 flagged: H=8 R: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0157, z 0.79; H=8 N: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0174, z 1.38; H=8 RO: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0226, z 0.466; H=8 RI: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0155, z 0.667; H=8 RN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0232, z 1.09; H=8 ON: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0174, z 0.837; H=8 IN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0169, z 1.3; H=8 ROI: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0226, z 0.476; H=8 RON: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0274, z 0.553; H=8 RIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.023, z 1.06; H=8 OIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0175, z 0.846; H=8 ROIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0269, z 0.472 ... |

### A. Allocation: drop-one and Shapley

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED. MSE ratio MSE(F without X)/MSE(F) at level 1 - 0.05/4 (reading by the 1.05 table, with the n_eff guard); excess ratio L_A(F without X)/L_A(F) and Holm p (Delta MSE > 0) are estimates. phi = Shapley share of L_A (95%). Oracle rows: moment form; deployable rows: realized per draw.

| horizon | profile | X | MSE ratio [CI] | reading | excess ratio | Holm p | phi_X [95% CI] | share |
|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | R | 1.12 [1.05, 1.27] | substantial | 2.24 | 0.002 | 1.21e-05 [6.33e-06, 2.15e-05] | 0.705 |
| H=8 (0.27 LT) | oracle | O | 1.05 [1.02, 1.11] | needed, size not determined | 1.49 | 0.002 | 2.99e-06 [1.23e-06, 5.69e-06] | 0.174 |
| H=8 (0.27 LT) | oracle | I | 1 [0.998, 1] | negligible | 1.01 | 0.216 | 7.16e-08 [-5.75e-08, 2.21e-07] | 0.00416 |
| H=8 (0.27 LT) | oracle | N | 1.01 [1.01, 1.01] | small | 1.1 | 0.002 | 2.02e-06 [1.44e-06, 2.5e-06] | 0.117 |
| H=8 (0.27 LT) | deployable | R | 0.995 [0.986, 1.01] | undetermined (n_eff < 50) | 0.973 | 1 | -9.7e-07 [-1.69e-06, -2.36e-07] | 0.801 |
| H=8 (0.27 LT) | deployable | O | 1 [0.994, 1.01] | undetermined (n_eff < 50) | 1.02 | 0.844 | 3.54e-07 [-8.98e-08, 8.23e-07] | -0.292 |
| H=8 (0.27 LT) | deployable | I | 1 [0.995, 1.01] | undetermined (n_eff < 50) | 1.01 | 0.844 | 7.33e-08 [-1.34e-07, 3.04e-07] | -0.0606 |
| H=8 (0.27 LT) | deployable | N | 0.998 [0.99, 1.01] | undetermined (n_eff < 50) | 0.987 | 1 | -6.67e-07 [-1.27e-06, -1.39e-07] | 0.551 |
| H=15 (0.50 LT) | oracle | R | 1.14 [1.07, 1.29] | substantial | 2.7 | 0.002 | 2.65e-05 [1.61e-05, 4.3e-05] | 0.712 |
| H=15 (0.50 LT) | oracle | O | 1.05 [1.03, 1.1] | needed, size not determined | 1.65 | 0.002 | 6.62e-06 [3.42e-06, 1.12e-05] | 0.178 |
| H=15 (0.50 LT) | oracle | I | 0.999 [0.997, 1] | negligible | 0.993 | 0.686 | -2.24e-07 [-5.61e-07, 7.4e-08] | -0.00604 |
| H=15 (0.50 LT) | oracle | N | 1.01 [1, 1.01] | small | 1.12 | 0.002 | 4.3e-06 [3.17e-06, 5.29e-06] | 0.116 |
| H=15 (0.50 LT) | deployable | R | 0.994 [0.983, 1.01] | undetermined (n_eff < 50) | 0.971 | 1 | -1.8e-06 [-3.42e-06, -2.99e-07] | 1.12 |
| H=15 (0.50 LT) | deployable | O | 1 [0.994, 1.01] | undetermined (n_eff < 50) | 1.01 | 0.8 | 8.82e-07 [-5.16e-09, 1.81e-06] | -0.548 |
| H=15 (0.50 LT) | deployable | I | 1 [0.996, 1.01] | undetermined (n_eff < 50) | 1.01 | 0.8 | 1.56e-07 [-1.86e-07, 5.18e-07] | -0.0968 |
| H=15 (0.50 LT) | deployable | N | 0.995 [0.99, 1] | undetermined (n_eff < 50) | 0.976 | 1 | -8.43e-07 [-1.86e-06, 6.32e-08] | 0.524 |
| H=30 (1.00 LT) | oracle | R | 1.13 [1.1, 1.15] | substantial | 2.68 | 0.002 | 7.84e-05 [6.75e-05, 8.98e-05] | 0.682 |
| H=30 (1.00 LT) | oracle | O | 1.05 [1.04, 1.06] | needed, size not determined | 1.66 | 0.002 | 1.83e-05 [1.44e-05, 2.23e-05] | 0.159 |
| H=30 (1.00 LT) | oracle | I | 1 [0.998, 1] | negligible | 1.01 | 0.227 | 1.17e-06 [4.78e-07, 1.9e-06] | 0.0102 |
| H=30 (1.00 LT) | oracle | N | 1.01 [1, 1.01] | small | 1.1 | 0.002 | 1.71e-05 [1.37e-05, 2.06e-05] | 0.149 |
| H=30 (1.00 LT) | deployable | R | 0.999 [0.99, 1.01] | negligible | 0.994 | 0.618 | -1.54e-06 [-6.22e-06, 3.08e-06] | -0.148 |
| H=30 (1.00 LT) | deployable | O | 1.01 [1, 1.02] | small | 1.06 | 0.002 | 6.92e-06 [3.41e-06, 1.05e-05] | 0.662 |
| H=30 (1.00 LT) | deployable | I | 1 [0.999, 1] | negligible | 1.01 | 0.348 | 7.9e-07 [-6.43e-07, 2.15e-06] | 0.0756 |
| H=30 (1.00 LT) | deployable | N | 1 [0.995, 1.01] | negligible | 1.01 | 0.478 | 4.28e-06 [-8.37e-07, 1e-05] | 0.41 |
| H=60 (2.00 LT) | oracle | R | 1.1 [1.07, 1.14] | substantial | 1.53 | 0.002 | 0.00123 [0.000995, 0.00146] | 0.832 |
| H=60 (2.00 LT) | oracle | O | 1.02 [1.01, 1.03] | small | 1.11 | 0.002 | 0.000134 [7.7e-05, 0.000193] | 0.091 |
| H=60 (2.00 LT) | oracle | I | 0.998 [0.992, 1] | negligible | 0.99 | 0.781 | -4.15e-05 [-8.46e-05, 3.39e-06] | -0.0281 |
| H=60 (2.00 LT) | oracle | N | 1 [0.996, 1.01] | negligible | 1 | 0.781 | 0.000156 [7.43e-05, 0.000239] | 0.105 |
| H=60 (2.00 LT) | deployable | R | 0.998 [0.984, 1.01] | negligible | 0.994 | 1 | -6.63e-05 [-0.000215, 7.93e-05] | -3.04 |
| H=60 (2.00 LT) | deployable | O | 1.01 [0.994, 1.02] | negligible | 1.02 | 0.512 | 3.58e-05 [-8.31e-05, 0.00016] | 1.64 |
| H=60 (2.00 LT) | deployable | I | 1 [0.995, 1] | negligible | 0.999 | 1 | 9.19e-06 [-2.94e-05, 4.81e-05] | 0.421 |
| H=60 (2.00 LT) | deployable | N | 1 [0.994, 1.01] | negligible | 1 | 1 | 4.31e-05 [-4.91e-05, 0.000139] | 1.98 |
| H=120 (4.00 LT) | oracle | R | 1.01 [1.01, 1.02] | small | 1.05 | 0.002 | 0.00133 [0.000752, 0.00188] | 0.544 |
| H=120 (4.00 LT) | oracle | O | 1.01 [1, 1.01] | small | 1.02 | 0.002 | 0.000428 [0.000209, 0.000647] | 0.176 |
| H=120 (4.00 LT) | oracle | I | 1 [1, 1.01] | small | 1.01 | 0.002 | 0.000638 [0.000313, 0.000945] | 0.262 |
| H=120 (4.00 LT) | oracle | N | 1 [0.999, 1] | negligible | 0.999 | 0.929 | 4.62e-05 [-0.00019, 0.000272] | 0.0189 |
| H=120 (4.00 LT) | deployable | R | 1 [1, 1.01] | negligible | 1.01 | 0.054 | 0.000401 [8.51e-05, 0.000732] | 0.26 |
| H=120 (4.00 LT) | deployable | O | 1 [0.999, 1.01] | negligible | 1.01 | 0.083 | 0.000295 [5.5e-05, 0.00054] | 0.191 |
| H=120 (4.00 LT) | deployable | I | 1.01 [1, 1.01] | small | 1.02 | 0.002 | 0.000787 [0.00045, 0.0011] | 0.511 |
| H=120 (4.00 LT) | deployable | N | 1 [0.999, 1] | negligible | 0.999 | 0.744 | 5.77e-05 [-0.000137, 0.000259] | 0.0374 |

### A. Allocation: summary per horizon

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED. n_eff = Kish size of kappa on the test states; G = 1 - L_A(rule)/L_A(constant), estimate (95%).

| horizon | profile | n_eff(kappa) | G(F) [CI] | G(separation) | MSE(F)/MSE(sep) [CI] | reading | settings (A) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 631 | 0.607 [0.468, 0.72] | 0.32 | 0.935 [0.928, 0.941] | lowers | F: qn; qn 4, mid 1, low 10 |
| H=8 (0.27 LT) | deployable | 631 | -0.0577 [-0.125, 0.00215] | -0.554 | 0.924 [0.914, 0.935] | lowers | F: qn; qn 1, mid 3, low 11 |
| H=15 (0.50 LT) | oracle | 651 | 0.688 [0.585, 0.776] | 0.481 | 0.947 [0.941, 0.953] | lowers | F: qn; qn 4, mid 3, low 8 |
| H=15 (0.50 LT) | deployable | 651 | -0.0372 [-0.103, 0.0195] | -0.385 | 0.938 [0.926, 0.95] | lowers | F: mid; qn 0, mid 3, low 12 |
| H=30 (1.00 LT) | oracle | 353 | 0.695 [0.66, 0.727] | 0.543 | 0.964 [0.958, 0.971] | lowers | F: qn; qn 4, mid 4, low 7 |
| H=30 (1.00 LT) | deployable | 353 | 0.0706 [0.0144, 0.127] | -0.146 | 0.96 [0.943, 0.977] | lowers | F: mid; qn 0, mid 13, low 2 |
| H=60 (2.00 LT) | oracle | 515 | 0.398 [0.334, 0.457] | 0.428 | 1.01 [1, 1.02] | small | F: mid; qn 0, mid 5, low 10 |
| H=60 (2.00 LT) | deployable | 515 | 0.00571 [-0.0584, 0.0677] | -0.0125 | 0.995 [0.983, 1.01] | negligible | F: mid; qn 0, mid 9, low 6 |
| H=120 (4.00 LT) | oracle | 1.52e+03 | 0.0785 [0.0569, 0.0987] | -0.0955 | 0.952 [0.94, 0.964] | lowers | F: low; qn 0, mid 0, low 15 |
| H=120 (4.00 LT) | deployable | 1.52e+03 | 0.05 [0.0326, 0.0663] | -0.164 | 0.943 [0.93, 0.957] | lowers | F: low; qn 0, mid 0, low 15 |

### B. Allocation: pairwise interactions (logit u, interior states)

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED. Delta = L(additive) - L(additive + pair) on the test states, models fixed; level 1 - 0.05/6; Holm over the six pairs. R x I and O x I are primary.

| horizon | profile | pair | Delta [CI] | Holm p | reading | loss ratio reading |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | RI (primary) | 0.0125 [-0.00724, 0.0328] | 0.13 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | OI (primary) | 0.000204 [-0.0179, 0.0181] | 0.514 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | RO | 0.0655 [0.0144, 0.114] | 0.006 | interaction gain detected | small |
| H=8 (0.27 LT) | oracle | RN | 0.0395 [0.00751, 0.0723] | 0.005 | interaction gain detected | small |
| H=8 (0.27 LT) | oracle | ON | 0.0344 [0.0106, 0.0601] | 0.003 | interaction gain detected | small |
| H=8 (0.27 LT) | oracle | IN | 0.0065 [-0.00545, 0.0183] | 0.149 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RI (primary) | 0.00578 [-0.009, 0.0207] | 0.153 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | OI (primary) | 0.0144 [-0.00241, 0.0325] | 0.0405 | interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RO | 0.0808 [0.0452, 0.117] | 0.003 | interaction gain detected | small |
| H=8 (0.27 LT) | deployable | RN | 0.0188 [0.00133, 0.0389] | 0.01 | interaction gain detected | small |
| H=8 (0.27 LT) | deployable | ON | 0.0309 [0.0113, 0.052] | 0.003 | interaction gain detected | small |
| H=8 (0.27 LT) | deployable | IN | 0.00792 [-0.00159, 0.0175] | 0.0405 | interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | RI (primary) | 0.00199 [-0.0127, 0.0171] | 0.495 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | OI (primary) | 0.00657 [-0.0122, 0.0264] | 0.495 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | RO | 0.0977 [0.0527, 0.142] | 0.003 | interaction gain detected | needed, size not determined |
| H=15 (0.50 LT) | oracle | RN | 0.0493 [0.0203, 0.0772] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | oracle | ON | 0.0535 [0.0307, 0.0764] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | oracle | IN | 0.00309 [-0.00754, 0.0145] | 0.495 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | RI (primary) | 0.01 [-0.00888, 0.029] | 0.268 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | OI (primary) | 0.00537 [-0.0182, 0.0292] | 0.568 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | RO | 0.123 [0.0818, 0.168] | 0.003 | interaction gain detected | needed, size not determined |
| H=15 (0.50 LT) | deployable | RN | 0.0263 [0.00366, 0.0519] | 0.015 | interaction gain detected | small |
| H=15 (0.50 LT) | deployable | ON | 0.0163 [-0.000449, 0.0325] | 0.024 | interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | IN | 0.000889 [-0.00844, 0.0102] | 0.568 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | RI (primary) | -0.0141 [-0.035, 0.00844] | 0.964 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | OI (primary) | 0.0227 [-0.00713, 0.0518] | 0.075 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | RO | 0.11 [0.0548, 0.168] | 0.003 | interaction gain detected | needed, size not determined |
| H=30 (1.00 LT) | oracle | RN | 0.0226 [-0.000395, 0.0479] | 0.0325 | interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | ON | 0.0223 [-0.00245, 0.0458] | 0.0325 | interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | IN | 0.00619 [-0.00277, 0.0153] | 0.075 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | RI (primary) | 0.00838 [-0.0197, 0.036] | 0.467 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | OI (primary) | 0.0367 [0.000814, 0.0733] | 0.0175 | interaction gain detected | small |
| H=30 (1.00 LT) | deployable | RO | 0.0757 [0.035, 0.12] | 0.003 | interaction gain detected | small |
| H=30 (1.00 LT) | deployable | RN | 0.0186 [-0.00705, 0.0459] | 0.09 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | ON | 0.0172 [-0.000903, 0.0355] | 0.028 | interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | IN | -0.000279 [-0.0112, 0.0102] | 0.521 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | RI (primary) | 0.0122 [-0.0184, 0.0447] | 0.403 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | OI (primary) | 0.0186 [-0.00839, 0.0461] | 0.152 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | RO | 0.0844 [0.0366, 0.134] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | oracle | RN | 0.0103 [-0.0202, 0.0404] | 0.403 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | ON | 0.0113 [-0.0226, 0.0469] | 0.403 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | IN | 0.0261 [0.00811, 0.0447] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | RI (primary) | 0.0234 [0.00553, 0.0419] | 0.005 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | OI (primary) | 0.0139 [-0.0122, 0.0392] | 0.22 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | RO | 0.056 [0.0187, 0.0892] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | RN | 0.0095 [-0.00866, 0.0284] | 0.22 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | ON | 0.00147 [-0.019, 0.0234] | 0.43 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | IN | 0.0125 [-0.00294, 0.0299] | 0.086 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RI (primary) | 0.0198 [-0.0193, 0.0647] | 0.477 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | OI (primary) | 0.00981 [-0.0276, 0.051] | 0.658 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RO | 0.0171 [-0.0166, 0.0534] | 0.477 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RN | 0.00617 [-0.0327, 0.0469] | 0.658 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | ON | -0.00114 [-0.0217, 0.02] | 0.658 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | IN | 0.012 [-0.0188, 0.0421] | 0.612 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RI (primary) | 0.00377 [-0.0114, 0.0195] | 0.501 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | OI (primary) | 0.00853 [-0.0132, 0.0294] | 0.418 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RO | 0.00329 [-0.0173, 0.0244] | 0.501 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RN | 0.00659 [-0.00665, 0.0187] | 0.358 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | ON | 0.0202 [-0.015, 0.0523] | 0.324 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | IN | 0.00974 [-0.00628, 0.0265] | 0.324 | no interaction gain detected | negligible |

### D. Allocation ladder (rung against the full profile)

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED. MSE ratio MSE(rung)/MSE(F) at level 1 - 0.05/m (m rungs); Holm p for Delta MSE > 0. Theory gap L_A(oracle F) is an upper bound; estimation gap = L_A(deployable F) - L_A(oracle F) (95%).

| horizon | profile | rung | MSE | MSE ratio vs F [CI] | reading | Holm p |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | none | 0.000133 | 1.15 [1.08, 1.3] | substantial | 0.0045 |
| H=8 (0.27 LT) | oracle | separation | 0.000124 | 1.07 [1.06, 1.08] | substantial | 0.0045 |
| H=8 (0.27 LT) | oracle | RO | 0.000117 | 1.01 [1, 1.01] | small | 0.0045 |
| H=8 (0.27 LT) | oracle | R | 0.000123 | 1.06 [1.02, 1.12] | needed, size not determined | 0.0045 |
| H=8 (0.27 LT) | oracle | O | 0.000133 | 1.14 [1.08, 1.29] | substantial | 0.0045 |
| H=8 (0.27 LT) | oracle | I | 0.000133 | 1.15 [1.08, 1.3] | substantial | 0.0045 |
| H=8 (0.27 LT) | oracle | N | 0.00013 | 1.12 [1.05, 1.28] | substantial | 0.0045 |
| H=8 (0.27 LT) | oracle | F (ROIN) | 0.000116 | 1 | | |
| H=8 (0.27 LT) | oracle | X | 0.000129 | 1.11 [1.07, 1.18] | substantial | 0.0045 |
| H=8 (0.27 LT) | oracle | X+F | 0.000116 | 0.995 [0.991, 0.999] | lowers | 0.999 |
| H=8 (0.27 LT) | deployable | none | 0.000126 | 0.99 [0.976, 1] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | A2 (stored) | 0.000126 | 0.991 [0.976, 1.01] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | separation | 0.000138 | 1.08 [1.06, 1.1] | undetermined (n_eff < 50) | 0.006 |
| H=8 (0.27 LT) | deployable | A4 (stored) | 0.000138 | 1.08 [1.06, 1.1] | undetermined (n_eff < 50) | 0.006 |
| H=8 (0.27 LT) | deployable | RO | 0.000127 | 0.999 [0.99, 1.01] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | R | 0.000127 | 1 [0.99, 1.01] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | O | 0.000126 | 0.988 [0.974, 1] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | I | 0.000126 | 0.991 [0.977, 1.01] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | N | 0.000127 | 0.999 [0.989, 1.01] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | F (ROIN) | 0.000127 | 1 | | |
| H=8 (0.27 LT) | deployable | X | 0.000126 | 0.986 [0.971, 1] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | A3 (stored) | 0.000134 | 1.05 [1.02, 1.08] | undetermined (n_eff < 50) | 0.006 |
| H=8 (0.27 LT) | deployable | X+F | 0.000126 | 0.991 [0.983, 1] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | oracle | none | 0.000238 | 1.19 [1.11, 1.35] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | separation | 0.000212 | 1.06 [1.05, 1.07] | needed, size not determined | 0.0045 |
| H=15 (0.50 LT) | oracle | RO | 0.000202 | 1.01 [1, 1.01] | small | 0.0045 |
| H=15 (0.50 LT) | oracle | R | 0.000213 | 1.06 [1.04, 1.11] | needed, size not determined | 0.0045 |
| H=15 (0.50 LT) | oracle | O | 0.000235 | 1.17 [1.11, 1.31] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | I | 0.000238 | 1.19 [1.11, 1.35] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | N | 0.000231 | 1.15 [1.08, 1.32] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | F (ROIN) | 0.0002 | 1 | | |
| H=15 (0.50 LT) | oracle | X | 0.000228 | 1.14 [1.1, 1.21] | substantial | 0.0045 |
| H=15 (0.50 LT) | oracle | X+F | 0.0002 | 0.996 [0.992, 1] | negligible | 0.997 |
| H=15 (0.50 LT) | deployable | none | 0.000227 | 0.993 [0.977, 1.01] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | A2 (stored) | 0.000227 | 0.993 [0.977, 1.01] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | separation | 0.000243 | 1.07 [1.05, 1.09] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | A4 (stored) | 0.000243 | 1.07 [1.05, 1.09] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | RO | 0.000228 | 0.998 [0.991, 1] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | R | 0.000229 | 1 [0.991, 1.02] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | O | 0.000226 | 0.989 [0.973, 1] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | I | 0.000227 | 0.993 [0.977, 1.01] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | N | 0.000228 | 0.997 [0.985, 1.01] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | F (ROIN) | 0.000228 | 1 | | |
| H=15 (0.50 LT) | deployable | X | 0.000226 | 0.989 [0.973, 1.01] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | A3 (stored) | 0.000237 | 1.04 [1.01, 1.07] | undetermined (n_eff < 50) | 0.006 |
| H=15 (0.50 LT) | deployable | X+F | 0.000226 | 0.991 [0.985, 0.997] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | none | 0.000787 | 1.17 [1.14, 1.2] | substantial | 0.0045 |
| H=30 (1.00 LT) | oracle | separation | 0.000698 | 1.04 [1.03, 1.05] | small | 0.0045 |
| H=30 (1.00 LT) | oracle | RO | 0.000677 | 1.01 [1, 1.01] | small | 0.0045 |
| H=30 (1.00 LT) | oracle | R | 0.000717 | 1.07 [1.05, 1.08] | needed, size not determined | 0.0045 |
| H=30 (1.00 LT) | oracle | O | 0.000786 | 1.17 [1.14, 1.2] | substantial | 0.0045 |
| H=30 (1.00 LT) | oracle | I | 0.000785 | 1.17 [1.14, 1.2] | substantial | 0.0045 |
| H=30 (1.00 LT) | oracle | N | 0.000759 | 1.13 [1.1, 1.16] | substantial | 0.0045 |
| H=30 (1.00 LT) | oracle | F (ROIN) | 0.000672 | 1 | | |
| H=30 (1.00 LT) | oracle | X | 0.000778 | 1.16 [1.13, 1.19] | substantial | 0.0045 |
| H=30 (1.00 LT) | oracle | X+F | 0.00067 | 0.997 [0.992, 1] | negligible | 0.961 |
| H=30 (1.00 LT) | deployable | none | 0.00077 | 1.01 [0.997, 1.03] | negligible | 0.09 |
| H=30 (1.00 LT) | deployable | A2 (stored) | 0.000771 | 1.01 [0.997, 1.03] | negligible | 0.075 |
| H=30 (1.00 LT) | deployable | separation | 0.000792 | 1.04 [1.02, 1.07] | needed, size not determined | 0.0065 |
| H=30 (1.00 LT) | deployable | A4 (stored) | 0.000792 | 1.04 [1.02, 1.07] | needed, size not determined | 0.0065 |
| H=30 (1.00 LT) | deployable | RO | 0.000763 | 1 [0.996, 1.01] | negligible | 0.232 |
| H=30 (1.00 LT) | deployable | R | 0.000774 | 1.02 [1, 1.04] | small | 0.0065 |
| H=30 (1.00 LT) | deployable | O | 0.000766 | 1.01 [0.992, 1.03] | negligible | 0.232 |
| H=30 (1.00 LT) | deployable | I | 0.00077 | 1.01 [0.996, 1.03] | negligible | 0.09 |
| H=30 (1.00 LT) | deployable | N | 0.000765 | 1.01 [0.995, 1.02] | negligible | 0.232 |
| H=30 (1.00 LT) | deployable | A5 (stored) | 0.000767 | 1.01 [0.996, 1.02] | negligible | 0.15 |
| H=30 (1.00 LT) | deployable | F (ROIN) | 0.00076 | 1 | | |
| H=30 (1.00 LT) | deployable | X | 0.000762 | 1 [0.984, 1.02] | negligible | 0.695 |
| H=30 (1.00 LT) | deployable | A3 (stored) | 0.000772 | 1.02 [0.992, 1.04] | negligible | 0.15 |
| H=30 (1.00 LT) | deployable | X+F | 0.000755 | 0.994 [0.984, 1] | negligible | 0.973 |
| H=60 (2.00 LT) | oracle | none | 0.0128 | 1.13 [1.09, 1.17] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | separation | 0.0112 | 0.99 [0.977, 1] | negligible | 1 |
| H=60 (2.00 LT) | oracle | RO | 0.0113 | 0.997 [0.988, 1.01] | negligible | 1 |
| H=60 (2.00 LT) | oracle | R | 0.0116 | 1.02 [1.01, 1.04] | small | 0.0045 |
| H=60 (2.00 LT) | oracle | O | 0.0129 | 1.13 [1.09, 1.18] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | I | 0.013 | 1.14 [1.1, 1.19] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | N | 0.0126 | 1.11 [1.07, 1.14] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | F (ROIN) | 0.0114 | 1 | | |
| H=60 (2.00 LT) | oracle | X | 0.0128 | 1.13 [1.09, 1.17] | substantial | 0.0045 |
| H=60 (2.00 LT) | oracle | X+F | 0.0114 | 1 [0.991, 1.01] | negligible | 1 |
| H=60 (2.00 LT) | deployable | none | 0.0129 | 1 [0.978, 1.03] | negligible | 1 |
| H=60 (2.00 LT) | deployable | A2 (stored) | 0.0129 | 1 [0.975, 1.03] | negligible | 1 |
| H=60 (2.00 LT) | deployable | separation | 0.013 | 1.01 [0.989, 1.02] | negligible | 1 |
| H=60 (2.00 LT) | deployable | A4 (stored) | 0.013 | 1.01 [0.989, 1.02] | negligible | 1 |
| H=60 (2.00 LT) | deployable | RO | 0.0129 | 0.999 [0.991, 1.01] | negligible | 1 |
| H=60 (2.00 LT) | deployable | R | 0.0131 | 1.01 [0.992, 1.03] | negligible | 0.654 |
| H=60 (2.00 LT) | deployable | O | 0.0129 | 1 [0.978, 1.03] | negligible | 1 |
| H=60 (2.00 LT) | deployable | I | 0.0129 | 1 [0.977, 1.03] | negligible | 1 |
| H=60 (2.00 LT) | deployable | N | 0.0128 | 0.994 [0.97, 1.02] | negligible | 1 |
| H=60 (2.00 LT) | deployable | F (ROIN) | 0.0129 | 1 | | |
| H=60 (2.00 LT) | deployable | X | 0.0129 | 1 [0.978, 1.03] | negligible | 1 |
| H=60 (2.00 LT) | deployable | A3 (stored) | 0.0131 | 1.01 [0.988, 1.04] | negligible | 0.929 |
| H=60 (2.00 LT) | deployable | X+F | 0.0129 | 0.998 [0.987, 1.01] | negligible | 1 |
| H=120 (4.00 LT) | oracle | none | 0.11 | 1.02 [1.01, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | separation | 0.113 | 1.05 [1.03, 1.07] | needed, size not determined | 0.0045 |
| H=120 (4.00 LT) | oracle | RO | 0.108 | 1 [1, 1.01] | negligible | 0.014 |
| H=120 (4.00 LT) | oracle | R | 0.109 | 1.01 [1.01, 1.02] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | O | 0.11 | 1.02 [1.01, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | I | 0.109 | 1.02 [1.01, 1.02] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | N | 0.11 | 1.02 [1.01, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | F (ROIN) | 0.108 | 1 | | |
| H=120 (4.00 LT) | oracle | X | 0.11 | 1.02 [1.01, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | X+F | 0.107 | 0.991 [0.983, 0.999] | lowers | 0.999 |
| H=120 (4.00 LT) | deployable | none | 0.11 | 1.01 [1.01, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | A2 (stored) | 0.11 | 1.01 [1.01, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | separation | 0.115 | 1.06 [1.04, 1.08] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | A4 (stored) | 0.115 | 1.06 [1.04, 1.08] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | RO | 0.109 | 1 [1, 1.01] | small | 0.006 |
| H=120 (4.00 LT) | deployable | R | 0.109 | 1.01 [1, 1.01] | small | 0.006 |
| H=120 (4.00 LT) | deployable | O | 0.109 | 1.01 [1, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | I | 0.109 | 1 [0.999, 1.01] | negligible | 0.03 |
| H=120 (4.00 LT) | deployable | N | 0.11 | 1.01 [1.01, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | F (ROIN) | 0.108 | 1 | | |
| H=120 (4.00 LT) | deployable | X | 0.109 | 1.01 [1, 1.02] | small | 0.006 |
| H=120 (4.00 LT) | deployable | A3 (stored) | 0.11 | 1.02 [1, 1.04] | small | 0.006 |
| H=120 (4.00 LT) | deployable | X+F | 0.108 | 0.996 [0.992, 1] | lowers | 0.999 |

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| horizon | theory gap (upper bound) [CI] | estimation gap [CI] | gap with R estimated | gap with O estimated | gap with I estimated | gap with N estimated |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 1.12e-05 [1.04e-05, 1.2e-05] | 1.11e-05 [7.26e-06, 1.48e-05] | 5.93e-06 [2.26e-06, 9.43e-06] | -5.1e-07 [-4.05e-06, 2.9e-06] | -2.32e-07 [-3.68e-06, 3.19e-06] | 1.51e-06 [-2.06e-06, 4.94e-06] |
| H=15 (0.50 LT) | 1.68e-05 [1.55e-05, 1.83e-05] | 2.8e-05 [2e-05, 3.68e-05] | 1.82e-05 [1.05e-05, 2.64e-05] | 2.37e-06 [-4.75e-06, 1.03e-05] | 1.98e-06 [-5.12e-06, 9.98e-06] | 4.54e-06 [-2.55e-06, 1.24e-05] |
| H=30 (1.00 LT) | 5.04e-05 [4.56e-05, 5.57e-05] | 8.71e-05 [4.96e-05, 0.000125] | 6.51e-05 [2.9e-05, 0.0001] | -1.8e-05 [-5.15e-05, 1.46e-05] | -1.56e-05 [-4.87e-05, 1.69e-05] | -7.17e-06 [-4.14e-05, 2.66e-05] |
| H=60 (2.00 LT) | 0.00223 [0.00195, 0.00251] | 0.00156 [0.000821, 0.00234] | 0.00137 [0.000628, 0.00214] | 0.000262 [-0.000436, 0.000952] | 0.000293 [-0.000401, 0.000967] | 0.000289 [-0.000415, 0.000966] |
| H=120 (4.00 LT) | 0.0286 [0.0269, 0.0304] | 0.000659 [-0.00229, 0.0035] | 0.000662 [-0.00229, 0.00349] | -0.000212 [-0.00313, 0.00254] | -0.000299 [-0.00319, 0.0024] | -0.000292 [-0.00321, 0.00243] |

### Horizon decision (Y = ln min(T_c, H_max))

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED. Pinball loss at tau = 0.5; drop-one ratio at level 1 - 0.05/4; ladder ratio vs F at 1 - 0.05/m; C = Harrell's C (95%); coverage of q_0.1, q_0.5, q_0.9 and the 80% interval below the cap.

| profile | X | pinball ratio [CI] | reading | Holm p | phi [CI] |
|---|---|---|---|---|---|
| oracle | R | 1.01 [1, 1.02] | small | 0.005 | 0.00161 [0.000857, 0.00231] |
| oracle | O | 1.09 [1.07, 1.12] | substantial | 0.002 | 0.00818 [0.00672, 0.0097] |
| oracle | I | 1.24 [1.21, 1.28] | substantial | 0.002 | 0.0269 [0.024, 0.0299] |
| oracle | N | 1.01 [0.996, 1.02] | negligible | 0.0795 | 0.00223 [0.00124, 0.00308] |
| deployable | R | 1 [0.996, 1.01] | negligible | 0.528 | 0.00135 [0.000861, 0.00185] |
| deployable | O | 1.12 [1.09, 1.14] | substantial | 0.002 | 0.0146 [0.0126, 0.0165] |
| deployable | I | 1.23 [1.19, 1.27] | substantial | 0.002 | 0.0254 [0.0227, 0.0281] |
| deployable | N | 0.997 [0.991, 1] | negligible | 0.885 | 0.00132 [0.000709, 0.00188] |

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | ratio vs F [CI] | reading | C [CI] | cov 0.1 / 0.5 / 0.9 / 80% |
|---|---|---|---|---|---|---|
| oracle | none | 0.16 | 1.32 [1.28, 1.37] | substantial | 0.5 [0.5, 0.5] | 0.099 / 0.509 / 0.9 / 0.801 |
| oracle | lyapunov | 0.165 | 1.36 [1.32, 1.41] | substantial | 0.64 [0.63, 0.651] | 0.08 / 0.486 / 0.892 / 0.853 |
| oracle | RO | 0.154 | 1.27 [1.23, 1.32] | substantial | 0.559 [0.549, 0.569] | 0.111 / 0.518 / 0.895 / 0.784 |
| oracle | R | 0.159 | 1.31 [1.27, 1.36] | substantial | 0.517 [0.507, 0.526] | 0.105 / 0.511 / 0.9 / 0.795 |
| oracle | O | 0.156 | 1.29 [1.25, 1.34] | substantial | 0.557 [0.548, 0.567] | 0.104 / 0.519 / 0.897 / 0.794 |
| oracle | I | 0.137 | 1.13 [1.1, 1.16] | substantial | 0.631 [0.621, 0.642] | 0.101 / 0.509 / 0.906 / 0.805 |
| oracle | N | 0.157 | 1.3 [1.25, 1.34] | substantial | 0.537 [0.526, 0.547] | 0.097 / 0.516 / 0.896 / 0.799 |
| oracle | ROIN | 0.121 | 1 |  | 0.681 [0.671, 0.69] | 0.141 / 0.519 / 0.89 / 0.749 |
| oracle | X | 0.124 | 1.02 [0.986, 1.06] | undetermined | 0.693 [0.685, 0.701] | 0.148 / 0.522 / 0.892 / 0.744 |
| oracle | X+F | 0.094 | 0.777 [0.756, 0.801] | lowers | 0.765 [0.759, 0.772] | 0.162 / 0.525 / 0.851 / 0.689 |
| oracle | Lyapunov rank (C only) | | | | 0.637 [0.627, 0.647] | |
| deployable | none | 0.16 | 1.36 [1.32, 1.41] | substantial | 0.5 [0.5, 0.5] | 0.099 / 0.509 / 0.9 / 0.801 |
| deployable | lyapunov | 0.167 | 1.42 [1.38, 1.48] | substantial | 0.634 [0.623, 0.644] | 0.0703 / 0.472 / 0.894 / 0.863 |
| deployable | RO | 0.145 | 1.24 [1.2, 1.28] | substantial | 0.603 [0.593, 0.613] | 0.113 / 0.518 / 0.898 / 0.785 |
| deployable | R | 0.158 | 1.35 [1.3, 1.4] | substantial | 0.52 [0.511, 0.529] | 0.0999 / 0.507 / 0.898 / 0.798 |
| deployable | O | 0.147 | 1.25 [1.21, 1.29] | substantial | 0.601 [0.592, 0.612] | 0.107 / 0.524 / 0.897 / 0.79 |
| deployable | I | 0.137 | 1.17 [1.14, 1.2] | substantial | 0.632 [0.622, 0.642] | 0.0971 / 0.509 / 0.904 / 0.807 |
| deployable | N | 0.157 | 1.34 [1.29, 1.39] | substantial | 0.536 [0.528, 0.544] | 0.106 / 0.514 / 0.901 / 0.795 |
| deployable | ROIN | 0.117 | 1 |  | 0.693 [0.685, 0.702] | 0.134 / 0.51 / 0.868 / 0.734 |
| deployable | X | 0.126 | 1.07 [1.03, 1.11] | needed, size not determined | 0.689 [0.681, 0.697] | 0.141 / 0.526 / 0.894 / 0.754 |
| deployable | X+F | 0.0917 | 0.782 [0.76, 0.803] | lowers | 0.77 [0.763, 0.777] | 0.15 / 0.518 / 0.862 / 0.711 |
| deployable | Lyapunov rank (C only) | | | | 0.631 [0.621, 0.641] | |

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| profile | pair | Delta [CI] | Holm p | detected |
|---|---|---|---|---|
| oracle | RO | 6.59e-05 [-0.00039, 0.000561] | 0.487 | False |
| oracle | RI (primary) | 0.000763 [-6.64e-05, 0.00154] | 0.026 | True |
| oracle | RN | 0.000657 [0.000253, 0.00106] | 0.003 | True |
| oracle | OI (primary) | 0.00688 [0.00463, 0.00903] | 0.003 | True |
| oracle | ON | 0.000122 [-0.000325, 0.000543] | 0.487 | False |
| oracle | IN | 0.000338 [-0.000557, 0.0012] | 0.487 | False |
| deployable | RO | 0.000523 [-0.000708, 0.0016] | 0.349 | False |
| deployable | RI (primary) | 0.00213 [0.000753, 0.00352] | 0.003 | True |
| deployable | RN | 5.37e-05 [-9.13e-05, 0.000207] | 0.349 | False |
| deployable | OI (primary) | 0.0109 [0.00878, 0.013] | 0.003 | True |
| deployable | ON | 0.000175 [-0.000243, 0.000572] | 0.349 | False |
| deployable | IN | 0.000659 [-0.000488, 0.00178] | 0.294 | False |

## chua

**PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.**

| check | result |
|---|---|
| (f1) state_mse from per-draw errors, max rel diff | A0 0.0e+00, A1 0.0e+00, A2 0.0e+00, A3 0.0e+00, A4 0.0e+00, A5 0.0e+00 (within 1e-12: True) |
| (g) WU-0039b (b1), (b2) rows reproduced | drop-N: True, all rows: True |
| separation formula on F-hat vs stored A4 at H_ref, max abs | 2.22e-16 |
| T_c: T = 1 / e_(T-1) = theta (train, test) | 3/0, 0/0 |
| (f2) dependence bias, deployable rows (reported, not gating) | 131 rows; 40 flagged: H=8 R: dependence bias detectable (interval excludes 0), t1+t2 / V 0.00471, z -0.144; H=8 I: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0853, z 0.523; H=8 RO: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0641, z 0.768; H=8 RI: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0802, z 0.407; H=8 ROI: dependence bias detectable (interval excludes 0), t1+t2 / V 0.269, z 1.23; H=8 RON: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0902, z 0.752; H=8 OIN: dependence bias detectable (interval excludes 0), t1+t2 / V 0.107, z 0.776; H=8 swap-R: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0065, z -0.174; H=8 swap-N: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0116, z -0.213; H=8 separation: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0082, z 1.69; H=8 A4 (stored): dependence bias detectable (interval excludes 0), t1+t2 / V 0.0082, z 1.69; H=15 N: dependence bias detectable (interval excludes 0), t1+t2 / V 0.0178, z 0.809 ... |

### A. Allocation: drop-one and Shapley

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED. MSE ratio MSE(F without X)/MSE(F) at level 1 - 0.05/4 (reading by the 1.05 table, with the n_eff guard); excess ratio L_A(F without X)/L_A(F) and Holm p (Delta MSE > 0) are estimates. phi = Shapley share of L_A (95%). Oracle rows: moment form; deployable rows: realized per draw.

| horizon | profile | X | MSE ratio [CI] | reading | excess ratio | Holm p | phi_X [95% CI] | share |
|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | R | 1.17 [0.981, 1.51] | undetermined (n_eff < 50) | 1.56 | 0.0705 | 0.000102 [-3.26e-05, 0.000293] | 0.294 |
| H=8 (0.27 LT) | oracle | O | 1.45 [0.897, 2.58] | undetermined (n_eff < 50) | 2.49 | 0.23 | 0.000116 [-0.000302, 0.000676] | 0.335 |
| H=8 (0.27 LT) | oracle | I | 1.56 [0.991, 2.38] | undetermined (n_eff < 50) | 2.87 | 0.032 | 0.000317 [6.41e-05, 0.000686] | 0.917 |
| H=8 (0.27 LT) | oracle | N | 0.967 [0.791, 1.1] | undetermined (n_eff < 50) | 0.89 | 0.644 | -0.000189 [-0.000461, -1.86e-05] | -0.546 |
| H=8 (0.27 LT) | deployable | R | 0.912 [0.625, 1.17] | undetermined (n_eff < 50) | 0.866 | 1 | -1.7e-05 [-9.76e-05, 4.83e-05] | 0.0596 |
| H=8 (0.27 LT) | deployable | O | 0.751 [0.501, 1.04] | undetermined (n_eff < 50) | 0.621 | 1 | -0.000228 [-0.00044, -6.24e-05] | 0.798 |
| H=8 (0.27 LT) | deployable | I | 1.12 [0.763, 1.77] | undetermined (n_eff < 50) | 1.18 | 0.876 | 2.19e-05 [-0.00016, 0.000185] | -0.0768 |
| H=8 (0.27 LT) | deployable | N | 0.979 [0.752, 1.15] | undetermined (n_eff < 50) | 0.968 | 1 | -6.25e-05 [-0.000182, 5.65e-05] | 0.219 |
| H=15 (0.50 LT) | oracle | R | 1.01 [0.966, 1.05] | undetermined (n_eff < 50) | 1.03 | 0.963 | 0.000162 [-3.33e-07, 0.000363] | 0.475 |
| H=15 (0.50 LT) | oracle | O | 1.29 [1.04, 1.63] | undetermined (n_eff < 50) | 1.94 | 0.004 | 0.000309 [-0.000351, 0.001] | 0.907 |
| H=15 (0.50 LT) | oracle | I | 1 [0.842, 1.22] | undetermined (n_eff < 50) | 1.02 | 1 | 5.42e-05 [-0.000231, 0.0004] | 0.159 |
| H=15 (0.50 LT) | oracle | N | 0.919 [0.832, 1.01] | undetermined (n_eff < 50) | 0.742 | 1 | -0.000184 [-0.000402, -2.16e-05] | -0.541 |
| H=15 (0.50 LT) | deployable | R | 1 [0.993, 1.01] | undetermined (n_eff < 50) | 0.999 | 1 | 7.57e-06 [-2.22e-05, 3.79e-05] | -0.0397 |
| H=15 (0.50 LT) | deployable | O | 0.972 [0.913, 1.03] | undetermined (n_eff < 50) | 0.941 | 1 | -0.000112 [-0.000231, -9.45e-06] | 0.588 |
| H=15 (0.50 LT) | deployable | I | 0.996 [0.944, 1.05] | undetermined (n_eff < 50) | 0.992 | 1 | -8.95e-07 [-0.0001, 9.96e-05] | 0.00469 |
| H=15 (0.50 LT) | deployable | N | 1.01 [0.986, 1.03] | undetermined (n_eff < 50) | 1.01 | 1 | -8.53e-05 [-0.000157, -2.62e-05] | 0.447 |
| H=30 (1.00 LT) | oracle | R | 1.03 [0.994, 1.07] | undetermined (n_eff < 50) | 1.11 | 0.078 | 0.000421 [-9.1e-05, 0.000935] | 0.571 |
| H=30 (1.00 LT) | oracle | O | 1.02 [0.983, 1.06] | undetermined (n_eff < 50) | 1.07 | 0.292 | 0.000234 [-0.000151, 0.000647] | 0.318 |
| H=30 (1.00 LT) | oracle | I | 1 [0.988, 1.02] | undetermined (n_eff < 50) | 1.01 | 0.53 | -6.48e-05 [-0.000454, 0.000336] | -0.088 |
| H=30 (1.00 LT) | oracle | N | 0.998 [0.981, 1.01] | undetermined (n_eff < 50) | 0.994 | 0.553 | 0.000147 [-9.56e-05, 0.000412] | 0.199 |
| H=30 (1.00 LT) | deployable | R | 1.01 [0.992, 1.03] | undetermined (n_eff < 50) | 1.02 | 0.291 | 0.000284 [1.84e-06, 0.000631] | 0.599 |
| H=30 (1.00 LT) | deployable | O | 0.997 [0.978, 1.02] | undetermined (n_eff < 50) | 0.992 | 1 | -0.000162 [-0.000391, 8.26e-05] | -0.341 |
| H=30 (1.00 LT) | deployable | I | 1.01 [0.998, 1.03] | undetermined (n_eff < 50) | 1.03 | 0.09 | 0.00033 [9.25e-05, 0.000603] | 0.694 |
| H=30 (1.00 LT) | deployable | N | 0.999 [0.994, 1] | undetermined (n_eff < 50) | 0.997 | 1 | 2.31e-05 [-0.00013, 0.00019] | 0.0487 |
| H=60 (2.00 LT) | oracle | R | 1.03 [1.01, 1.05] | small | 1.08 | 0.004 | 0.00499 [0.00215, 0.00764] | 0.507 |
| H=60 (2.00 LT) | oracle | O | 1.01 [1, 1.02] | small | 1.04 | 0.0045 | 0.00265 [0.00127, 0.00395] | 0.27 |
| H=60 (2.00 LT) | oracle | I | 1 [0.999, 1.01] | negligible | 1.01 | 0.059 | 0.00123 [0.000692, 0.00178] | 0.125 |
| H=60 (2.00 LT) | oracle | N | 0.986 [0.976, 0.996] | lowers | 0.957 | 1 | 0.000968 [0.000145, 0.00182] | 0.0984 |
| H=60 (2.00 LT) | deployable | R | 1 [0.991, 1.01] | negligible | 1.01 | 1 | 0.00127 [-2.37e-05, 0.0026] | 0.301 |
| H=60 (2.00 LT) | deployable | O | 1 [0.975, 1.03] | negligible | 1.01 | 1 | 0.00101 [-0.00177, 0.00381] | 0.24 |
| H=60 (2.00 LT) | deployable | I | 0.998 [0.979, 1.01] | negligible | 0.993 | 1 | 0.000774 [-0.000611, 0.00201] | 0.183 |
| H=60 (2.00 LT) | deployable | N | 0.998 [0.993, 1] | negligible | 0.995 | 1 | 0.00116 [0.000263, 0.00201] | 0.275 |
| H=120 (4.00 LT) | oracle | R | 1.01 [1.01, 1.02] | small | 1.04 | 0.002 | 0.00791 [0.00548, 0.0106] | 0.567 |
| H=120 (4.00 LT) | oracle | O | 1.01 [1, 1.01] | small | 1.03 | 0.002 | 0.00275 [0.0012, 0.00423] | 0.197 |
| H=120 (4.00 LT) | oracle | I | 1 [0.998, 1.01] | negligible | 1.01 | 0.134 | 0.00132 [-0.000989, 0.00364] | 0.0943 |
| H=120 (4.00 LT) | oracle | N | 1 [1, 1.01] | small | 1.02 | 0.007 | 0.00197 [0.000378, 0.00354] | 0.141 |
| H=120 (4.00 LT) | deployable | R | 1 [0.999, 1.01] | negligible | 1.01 | 0.134 | 0.00218 [0.000334, 0.00414] | 0.322 |
| H=120 (4.00 LT) | deployable | O | 1 [0.997, 1.01] | negligible | 1.01 | 0.34 | 0.00234 [-0.000206, 0.00476] | 0.345 |
| H=120 (4.00 LT) | deployable | I | 1 [0.996, 1.01] | negligible | 1.01 | 0.364 | 0.00251 [6.56e-05, 0.0051] | 0.37 |
| H=120 (4.00 LT) | deployable | N | 0.998 [0.995, 1] | negligible | 0.994 | 0.878 | -0.000249 [-0.00205, 0.00158] | -0.0367 |

### A. Allocation: summary per horizon

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED. n_eff = Kish size of kappa on the test states; G = 1 - L_A(rule)/L_A(constant), estimate (95%).

| horizon | profile | n_eff(kappa) | G(F) [CI] | G(separation) | MSE(F)/MSE(sep) [CI] | reading | settings (A) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 25.7 | 0.624 [0.11, 0.78] | 0.551 | 0.945 [0.72, 1.24] | undetermined (n_eff < 50) | F: qn; qn 10, mid 2, low 3 |
| H=8 (0.27 LT) | deployable | 25.7 | -0.443 [-4.19, -0.00203] | -0.135 | 1.16 [0.926, 1.8] | undetermined (n_eff < 50) | F: qn; qn 3, mid 2, low 10 |
| H=15 (0.50 LT) | oracle | 73.6 | 0.288 [-0.342, 0.562] | 0.559 | 1.14 [1.02, 1.29] | undetermined (n_eff < 50) | F: mid; qn 4, mid 5, low 6 |
| H=15 (0.50 LT) | deployable | 73.6 | -0.129 [-0.327, -0.0243] | -0.141 | 0.995 [0.953, 1.04] | undetermined (n_eff < 50) | F: low; qn 0, mid 0, low 15 |
| H=30 (1.00 LT) | oracle | 198 | 0.128 [0.0159, 0.222] | 0.353 | 1.08 [1.03, 1.13] | undetermined (n_eff < 50) | F: low; qn 1, mid 0, low 14 |
| H=30 (1.00 LT) | deployable | 198 | 0.0539 [0.00623, 0.11] | 0.0409 | 0.995 [0.969, 1.02] | undetermined (n_eff < 50) | F: low; qn 0, mid 0, low 15 |
| H=60 (2.00 LT) | oracle | 801 | 0.148 [0.104, 0.189] | 0.104 | 0.983 [0.968, 0.998] | lowers | F: low; qn 0, mid 1, low 14 |
| H=60 (2.00 LT) | deployable | 801 | 0.0693 [0.00388, 0.133] | 0.0212 | 0.984 [0.96, 1.01] | negligible | F: mid; qn 0, mid 6, low 9 |
| H=120 (4.00 LT) | oracle | 1.99e+03 | 0.0753 [0.0568, 0.0959] | -0.0853 | 0.953 [0.943, 0.964] | lowers | F: low; qn 0, mid 3, low 12 |
| H=120 (4.00 LT) | deployable | 1.99e+03 | 0.0374 [0.0117, 0.0632] | -0.13 | 0.952 [0.94, 0.965] | lowers | F: mid; qn 0, mid 5, low 10 |

### B. Allocation: pairwise interactions (logit u, interior states)

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED. Delta = L(additive) - L(additive + pair) on the test states, models fixed; level 1 - 0.05/6; Holm over the six pairs. R x I and O x I are primary.

| horizon | profile | pair | Delta [CI] | Holm p | reading | loss ratio reading |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | RI (primary) | -0.00164 [-0.0246, 0.0233] | 0.877 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | OI (primary) | 0.00877 [-0.00862, 0.0252] | 0.326 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | RO | 0.0233 [-0.0264, 0.0685] | 0.326 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | oracle | RN | 0.0534 [0.0182, 0.0852] | 0.003 | interaction gain detected | small |
| H=8 (0.27 LT) | oracle | ON | 0.0535 [0.0176, 0.0852] | 0.003 | interaction gain detected | small |
| H=8 (0.27 LT) | oracle | IN | 0.00121 [-0.0195, 0.0217] | 0.877 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RI (primary) | 0.00179 [-0.0201, 0.0247] | 0.802 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | OI (primary) | 0.0279 [0.00743, 0.0465] | 0.003 | interaction gain detected | small |
| H=8 (0.27 LT) | deployable | RO | 0.0195 [-0.0203, 0.0571] | 0.295 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | RN | 0.028 [0.00609, 0.0499] | 0.003 | interaction gain detected | small |
| H=8 (0.27 LT) | deployable | ON | 0.00176 [-0.0226, 0.0258] | 0.802 | no interaction gain detected | negligible |
| H=8 (0.27 LT) | deployable | IN | 0.022 [0.00548, 0.0385] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | oracle | RI (primary) | -0.0222 [-0.0497, 0.00352] | 0.987 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | OI (primary) | 0.0293 [0.00745, 0.0516] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | oracle | RO | 0.0331 [-0.014, 0.0747] | 0.055 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | oracle | RN | 0.0476 [0.0133, 0.0845] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | oracle | ON | 0.0418 [0.00918, 0.078] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | oracle | IN | 0.0285 [0.00407, 0.0547] | 0.006 | interaction gain detected | small |
| H=15 (0.50 LT) | deployable | RI (primary) | 0.0278 [0.00841, 0.0476] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | deployable | OI (primary) | 0.0511 [-0.0428, 0.137] | 0.14 | no interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | RO | 0.059 [0.0276, 0.0887] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | deployable | RN | 0.0245 [-0.00119, 0.0486] | 0.0165 | interaction gain detected | negligible |
| H=15 (0.50 LT) | deployable | ON | 0.039 [0.0187, 0.0592] | 0.003 | interaction gain detected | small |
| H=15 (0.50 LT) | deployable | IN | 0.0104 [-0.00796, 0.0293] | 0.14 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | RI (primary) | 0.0192 [-0.018, 0.0581] | 0.177 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | OI (primary) | 0.0843 [0.0447, 0.125] | 0.003 | interaction gain detected | small |
| H=30 (1.00 LT) | oracle | RO | 0.0281 [-0.0104, 0.0665] | 0.0825 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | RN | 0.00948 [-0.0273, 0.0426] | 0.225 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | oracle | ON | 0.0409 [0.01, 0.0711] | 0.003 | interaction gain detected | small |
| H=30 (1.00 LT) | oracle | IN | 0.0296 [-0.00167, 0.062] | 0.034 | interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | RI (primary) | 0.0106 [-0.0255, 0.0447] | 0.63 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | OI (primary) | 0.0796 [0.0354, 0.125] | 0.003 | interaction gain detected | small |
| H=30 (1.00 LT) | deployable | RO | 0.0364 [-0.00103, 0.0747] | 0.0275 | interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | RN | 0.0165 [-0.00483, 0.0384] | 0.09 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | ON | 0.00533 [-0.0131, 0.0236] | 0.63 | no interaction gain detected | negligible |
| H=30 (1.00 LT) | deployable | IN | 0.00358 [-0.0169, 0.0238] | 0.63 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | RI (primary) | 0.0574 [0.00781, 0.106] | 0.0125 | interaction gain detected | small |
| H=60 (2.00 LT) | oracle | OI (primary) | 0.077 [0.0104, 0.143] | 0.0125 | interaction gain detected | small |
| H=60 (2.00 LT) | oracle | RO | 0.0321 [-0.0329, 0.0935] | 0.096 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | RN | 0.0277 [-0.0161, 0.0696] | 0.096 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | oracle | ON | 0.0676 [0.0163, 0.118] | 0.003 | interaction gain detected | small |
| H=60 (2.00 LT) | oracle | IN | 0.0333 [-0.00932, 0.0751] | 0.0615 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | RI (primary) | 0.0361 [-7.22e-05, 0.0727] | 0.02 | interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | OI (primary) | 0.103 [-0.0396, 0.232] | 0.044 | interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | RO | 0.0509 [-0.00521, 0.106] | 0.0285 | interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | RN | 0.0349 [0.00362, 0.0684] | 0.015 | interaction gain detected | small |
| H=60 (2.00 LT) | deployable | ON | 0.0119 [-0.0281, 0.0507] | 0.23 | no interaction gain detected | negligible |
| H=60 (2.00 LT) | deployable | IN | 0.0305 [0.0049, 0.0575] | 0.009 | interaction gain detected | small |
| H=120 (4.00 LT) | oracle | RI (primary) | -0.0134 [-0.0519, 0.0233] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | OI (primary) | 0.0366 [-0.00152, 0.0759] | 0.045 | interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RO | 0.00855 [-0.0487, 0.0662] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | RN | 0.00701 [-0.0321, 0.0417] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | ON | 0.015 [-0.0245, 0.0542] | 0.795 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | oracle | IN | -0.00208 [-0.0695, 0.0602] | 1 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RI (primary) | -0.00627 [-0.0305, 0.0183] | 0.741 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | OI (primary) | 0.0212 [-0.015, 0.0612] | 0.165 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RO | 0.0343 [-0.0118, 0.081] | 0.094 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | RN | 0.0181 [-0.00329, 0.0416] | 0.09 | no interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | ON | 0.0248 [-0.00116, 0.0541] | 0.036 | interaction gain detected | negligible |
| H=120 (4.00 LT) | deployable | IN | 0.0112 [-0.00554, 0.0285] | 0.165 | no interaction gain detected | negligible |

### D. Allocation ladder (rung against the full profile)

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED. MSE ratio MSE(rung)/MSE(F) at level 1 - 0.05/m (m rungs); Holm p for Delta MSE > 0. Theory gap L_A(oracle F) is an upper bound; estimation gap = L_A(deployable F) - L_A(oracle F) (95%).

| horizon | profile | rung | MSE | MSE ratio vs F [CI] | reading | Holm p |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | none | 0.00104 | 1.5 [0.97, 2.58] | undetermined (n_eff < 50) | 0.05 |
| H=8 (0.27 LT) | oracle | separation | 0.000731 | 1.06 [0.726, 1.63] | undetermined (n_eff < 50) | 0.382 |
| H=8 (0.27 LT) | oracle | RO | 0.00097 | 1.4 [0.951, 2] | undetermined (n_eff < 50) | 0.04 |
| H=8 (0.27 LT) | oracle | R | 0.00102 | 1.47 [0.937, 2.54] | undetermined (n_eff < 50) | 0.063 |
| H=8 (0.27 LT) | oracle | O | 0.00102 | 1.48 [1.01, 2.31] | undetermined (n_eff < 50) | 0.0175 |
| H=8 (0.27 LT) | oracle | I | 0.000981 | 1.42 [0.978, 2.24] | undetermined (n_eff < 50) | 0.033 |
| H=8 (0.27 LT) | oracle | N | 0.00118 | 1.7 [1.05, 2.75] | undetermined (n_eff < 50) | 0.008 |
| H=8 (0.27 LT) | oracle | F (ROIN) | 0.000691 | 1 | | |
| H=8 (0.27 LT) | oracle | X | 0.00103 | 1.49 [0.923, 2.45] | undetermined (n_eff < 50) | 0.063 |
| H=8 (0.27 LT) | oracle | X+F | 0.000866 | 1.25 [1.07, 1.58] | undetermined (n_eff < 50) | 0.0045 |
| H=8 (0.27 LT) | deployable | none | 0.00113 | 0.798 [0.449, 1.05] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | A2 (stored) | 0.00114 | 0.806 [0.472, 1.06] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | separation | 0.00121 | 0.859 [0.459, 1.14] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | A4 (stored) | 0.00121 | 0.859 [0.459, 1.14] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | RO | 0.00117 | 0.827 [0.465, 1.08] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | R | 0.00113 | 0.797 [0.452, 1.05] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | O | 0.00118 | 0.833 [0.466, 1.09] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | I | 0.00111 | 0.787 [0.44, 1.08] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | N | 0.00124 | 0.881 [0.513, 1.19] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | F (ROIN) | 0.00141 | 1 | | |
| H=8 (0.27 LT) | deployable | X | 0.00111 | 0.786 [0.493, 1.11] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | A3 (stored) | 0.00103 | 0.729 [0.444, 1.13] | undetermined (n_eff < 50) | 1 |
| H=8 (0.27 LT) | deployable | X+F | 0.00116 | 0.819 [0.504, 1.13] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | oracle | none | 0.00304 | 1.13 [0.862, 1.5] | undetermined (n_eff < 50) | 0.888 |
| H=15 (0.50 LT) | oracle | separation | 0.00237 | 0.881 [0.735, 1.01] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | oracle | RO | 0.00255 | 0.944 [0.834, 1.06] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | oracle | R | 0.00301 | 1.12 [0.856, 1.48] | undetermined (n_eff < 50) | 0.888 |
| H=15 (0.50 LT) | oracle | O | 0.00298 | 1.11 [0.965, 1.31] | undetermined (n_eff < 50) | 0.261 |
| H=15 (0.50 LT) | oracle | I | 0.00314 | 1.16 [0.916, 1.47] | undetermined (n_eff < 50) | 0.4 |
| H=15 (0.50 LT) | oracle | N | 0.00308 | 1.14 [0.872, 1.53] | undetermined (n_eff < 50) | 0.829 |
| H=15 (0.50 LT) | oracle | F (ROIN) | 0.00269 | 1 | | |
| H=15 (0.50 LT) | oracle | X | 0.00282 | 1.05 [0.853, 1.27] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | oracle | X+F | 0.00246 | 0.913 [0.788, 1.02] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | none | 0.00332 | 0.946 [0.883, 1.01] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | A2 (stored) | 0.00333 | 0.948 [0.886, 1.02] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | separation | 0.00353 | 1 [0.934, 1.07] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | A4 (stored) | 0.00353 | 1 [0.934, 1.07] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | RO | 0.00345 | 0.98 [0.921, 1.05] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | R | 0.00331 | 0.941 [0.884, 1] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | O | 0.00342 | 0.974 [0.914, 1.03] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | I | 0.00331 | 0.942 [0.859, 1.01] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | N | 0.0035 | 0.995 [0.93, 1.06] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | F (ROIN) | 0.00352 | 1 | | |
| H=15 (0.50 LT) | deployable | X | 0.00331 | 0.94 [0.772, 1.09] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | A3 (stored) | 0.00358 | 1.02 [0.934, 1.12] | undetermined (n_eff < 50) | 1 |
| H=15 (0.50 LT) | deployable | X+F | 0.0033 | 0.938 [0.794, 1.06] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | none | 0.0191 | 1.04 [0.987, 1.1] | undetermined (n_eff < 50) | 0.105 |
| H=30 (1.00 LT) | oracle | separation | 0.017 | 0.929 [0.86, 0.984] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | oracle | RO | 0.019 | 1.04 [0.944, 1.15] | undetermined (n_eff < 50) | 0.43 |
| H=30 (1.00 LT) | oracle | R | 0.0188 | 1.03 [0.998, 1.06] | undetermined (n_eff < 50) | 0.044 |
| H=30 (1.00 LT) | oracle | O | 0.019 | 1.04 [0.988, 1.09] | undetermined (n_eff < 50) | 0.12 |
| H=30 (1.00 LT) | oracle | I | 0.0195 | 1.07 [1.02, 1.12] | undetermined (n_eff < 50) | 0.0045 |
| H=30 (1.00 LT) | oracle | N | 0.019 | 1.03 [0.981, 1.08] | undetermined (n_eff < 50) | 0.145 |
| H=30 (1.00 LT) | oracle | F (ROIN) | 0.0183 | 1 | | |
| H=30 (1.00 LT) | oracle | X | 0.0187 | 1.02 [0.971, 1.07] | undetermined (n_eff < 50) | 0.388 |
| H=30 (1.00 LT) | oracle | X+F | 0.0182 | 0.994 [0.965, 1.02] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | deployable | none | 0.0221 | 1.02 [0.994, 1.06] | undetermined (n_eff < 50) | 0.186 |
| H=30 (1.00 LT) | deployable | A2 (stored) | 0.0221 | 1.02 [0.994, 1.05] | undetermined (n_eff < 50) | 0.186 |
| H=30 (1.00 LT) | deployable | separation | 0.0218 | 1.01 [0.964, 1.05] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | deployable | A4 (stored) | 0.0218 | 1.01 [0.964, 1.05] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | deployable | RO | 0.0219 | 1.01 [0.991, 1.03] | undetermined (n_eff < 50) | 0.504 |
| H=30 (1.00 LT) | deployable | R | 0.0217 | 1 [0.978, 1.03] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | deployable | O | 0.0223 | 1.03 [1.01, 1.06] | undetermined (n_eff < 50) | 0.013 |
| H=30 (1.00 LT) | deployable | I | 0.0217 | 1 [0.972, 1.04] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | deployable | N | 0.022 | 1.02 [0.988, 1.05] | undetermined (n_eff < 50) | 0.409 |
| H=30 (1.00 LT) | deployable | A5 (stored) | 0.0215 | 0.994 [0.94, 1.05] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | deployable | F (ROIN) | 0.0217 | 1 | | |
| H=30 (1.00 LT) | deployable | X | 0.0217 | 1 [0.961, 1.04] | undetermined (n_eff < 50) | 1 |
| H=30 (1.00 LT) | deployable | A3 (stored) | 0.0228 | 1.06 [0.98, 1.14] | undetermined (n_eff < 50) | 0.186 |
| H=30 (1.00 LT) | deployable | X+F | 0.0215 | 0.994 [0.964, 1.02] | undetermined (n_eff < 50) | 1 |
| H=60 (2.00 LT) | oracle | none | 0.184 | 1.06 [1.03, 1.08] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | separation | 0.178 | 1.02 [0.997, 1.04] | negligible | 0.048 |
| H=60 (2.00 LT) | oracle | RO | 0.175 | 1 [0.997, 1.01] | negligible | 0.137 |
| H=60 (2.00 LT) | oracle | R | 0.179 | 1.03 [1.01, 1.04] | small | 0.0045 |
| H=60 (2.00 LT) | oracle | O | 0.181 | 1.04 [1.01, 1.06] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | I | 0.183 | 1.05 [1.02, 1.07] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | N | 0.181 | 1.03 [1.01, 1.06] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | F (ROIN) | 0.175 | 1 | | |
| H=60 (2.00 LT) | oracle | X | 0.182 | 1.04 [1.02, 1.07] | needed, size not determined | 0.0045 |
| H=60 (2.00 LT) | oracle | X+F | 0.175 | 1 [0.999, 1.01] | negligible | 0.048 |
| H=60 (2.00 LT) | deployable | none | 0.179 | 1.02 [0.989, 1.06] | undetermined | 0.234 |
| H=60 (2.00 LT) | deployable | A2 (stored) | 0.179 | 1.02 [0.989, 1.06] | undetermined | 0.234 |
| H=60 (2.00 LT) | deployable | separation | 0.178 | 1.02 [0.979, 1.05] | undetermined | 0.764 |
| H=60 (2.00 LT) | deployable | A4 (stored) | 0.178 | 1.02 [0.979, 1.05] | undetermined | 0.764 |
| H=60 (2.00 LT) | deployable | RO | 0.174 | 0.998 [0.975, 1.02] | negligible | 0.764 |
| H=60 (2.00 LT) | deployable | R | 0.177 | 1.01 [0.98, 1.05] | negligible | 0.764 |
| H=60 (2.00 LT) | deployable | O | 0.177 | 1.01 [0.989, 1.04] | negligible | 0.495 |
| H=60 (2.00 LT) | deployable | I | 0.177 | 1.01 [0.98, 1.04] | negligible | 0.764 |
| H=60 (2.00 LT) | deployable | N | 0.176 | 1.01 [0.977, 1.04] | negligible | 0.764 |
| H=60 (2.00 LT) | deployable | F (ROIN) | 0.175 | 1 | | |
| H=60 (2.00 LT) | deployable | X | 0.177 | 1.01 [0.982, 1.05] | negligible | 0.764 |
| H=60 (2.00 LT) | deployable | A3 (stored) | 0.179 | 1.02 [0.98, 1.07] | undetermined | 0.495 |
| H=60 (2.00 LT) | deployable | X+F | 0.175 | 1 [0.987, 1.02] | negligible | 0.764 |
| H=120 (4.00 LT) | oracle | none | 0.617 | 1.02 [1.02, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | separation | 0.633 | 1.05 [1.03, 1.07] | needed, size not determined | 0.0045 |
| H=120 (4.00 LT) | oracle | RO | 0.604 | 1 [0.997, 1.01] | negligible | 0.259 |
| H=120 (4.00 LT) | oracle | R | 0.606 | 1 [0.998, 1.01] | negligible | 0.0735 |
| H=120 (4.00 LT) | oracle | O | 0.615 | 1.02 [1.01, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | I | 0.614 | 1.02 [1.01, 1.02] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | N | 0.615 | 1.02 [1.01, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | F (ROIN) | 0.604 | 1 | | |
| H=120 (4.00 LT) | oracle | X | 0.618 | 1.02 [1.01, 1.03] | small | 0.0045 |
| H=120 (4.00 LT) | oracle | X+F | 0.605 | 1 [0.997, 1.01] | negligible | 0.117 |
| H=120 (4.00 LT) | deployable | none | 0.614 | 1.01 [1, 1.02] | negligible | 0.021 |
| H=120 (4.00 LT) | deployable | A2 (stored) | 0.614 | 1.01 [1, 1.02] | small | 0.02 |
| H=120 (4.00 LT) | deployable | separation | 0.637 | 1.05 [1.03, 1.07] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | A4 (stored) | 0.637 | 1.05 [1.03, 1.07] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | RO | 0.608 | 1 [0.994, 1.01] | negligible | 0.556 |
| H=120 (4.00 LT) | deployable | R | 0.611 | 1.01 [0.996, 1.02] | negligible | 0.194 |
| H=120 (4.00 LT) | deployable | O | 0.611 | 1.01 [0.996, 1.02] | negligible | 0.167 |
| H=120 (4.00 LT) | deployable | I | 0.609 | 1 [0.994, 1.01] | negligible | 0.388 |
| H=120 (4.00 LT) | deployable | N | 0.613 | 1.01 [1, 1.02] | negligible | 0.021 |
| H=120 (4.00 LT) | deployable | F (ROIN) | 0.607 | 1 | | |
| H=120 (4.00 LT) | deployable | X | 0.614 | 1.01 [1, 1.02] | small | 0.0135 |
| H=120 (4.00 LT) | deployable | A3 (stored) | 0.631 | 1.04 [1.02, 1.06] | needed, size not determined | 0.006 |
| H=120 (4.00 LT) | deployable | X+F | 0.607 | 0.999 [0.993, 1] | negligible | 0.642 |

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| horizon | theory gap (upper bound) [CI] | estimation gap [CI] | gap with R estimated | gap with O estimated | gap with I estimated | gap with N estimated |
|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 0.000209 [8.3e-05, 0.000378] | 0.000721 [0.000135, 0.00152] | 7.84e-05 [-7.08e-05, 0.00026] | 0.00044 [-6.87e-05, 0.00126] | 0.000296 [7.24e-06, 0.000694] | 2.28e-05 [-5.35e-05, 0.000107] |
| H=15 (0.50 LT) | 0.000844 [0.00058, 0.00119] | 0.000821 [-1.89e-06, 0.00177] | 0.000309 [-0.000127, 0.000792] | 0.000862 [3.67e-05, 0.00181] | 0.0002 [-0.000336, 0.000807] | 0.000171 [-0.000306, 0.00071] |
| H=30 (1.00 LT) | 0.00501 [0.00361, 0.00667] | 0.00332 [0.000359, 0.00669] | 0.00299 [0.000177, 0.00602] | 0.00282 [4.68e-05, 0.00591] | 0.0024 [-0.000254, 0.00537] | 0.00349 [0.000642, 0.00662] |
| H=60 (2.00 LT) | 0.0564 [0.0516, 0.0616] | 0.000242 [-0.00894, 0.00921] | 0.000683 [-0.00793, 0.0094] | -0.00302 [-0.0117, 0.00497] | -0.00293 [-0.0116, 0.00513] | -0.00439 [-0.0132, 0.00362] |
| H=120 (4.00 LT) | 0.171 [0.163, 0.18] | 0.0035 [-0.011, 0.0177] | 0.00316 [-0.0113, 0.0172] | -0.00116 [-0.0162, 0.0132] | -0.00142 [-0.0159, 0.0126] | -0.002 [-0.0169, 0.0122] |

### Horizon decision (Y = ln min(T_c, H_max))

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED. Pinball loss at tau = 0.5; drop-one ratio at level 1 - 0.05/4; ladder ratio vs F at 1 - 0.05/m; C = Harrell's C (95%); coverage of q_0.1, q_0.5, q_0.9 and the 80% interval below the cap.

| profile | X | pinball ratio [CI] | reading | Holm p | phi [CI] |
|---|---|---|---|---|---|
| oracle | R | 1.01 [1, 1.03] | small | 0.004 | 0.00128 [0.000637, 0.00196] |
| oracle | O | 1.05 [1.03, 1.07] | needed, size not determined | 0.002 | 0.0129 [0.0109, 0.015] |
| oracle | I | 1.24 [1.21, 1.28] | substantial | 0.002 | 0.0435 [0.0392, 0.0475] |
| oracle | N | 1.01 [0.996, 1.02] | negligible | 0.0625 | 0.00309 [0.00182, 0.00426] |
| deployable | R | 1.01 [1, 1.01] | negligible | 0.017 | 0.0011 [0.000652, 0.00155] |
| deployable | O | 1.09 [1.07, 1.1] | substantial | 0.002 | 0.0185 [0.0162, 0.0208] |
| deployable | I | 1.22 [1.19, 1.25] | substantial | 0.002 | 0.0407 [0.037, 0.0445] |
| deployable | N | 0.999 [0.991, 1.01] | negligible | 0.606 | 0.00249 [0.00163, 0.00338] |

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | ratio vs F [CI] | reading | C [CI] | cov 0.1 / 0.5 / 0.9 / 80% |
|---|---|---|---|---|---|---|
| oracle | none | 0.221 | 1.38 [1.33, 1.43] | substantial | 0.5 [0.5, 0.5] | 0.102 / 0.497 / 0.895 / 0.793 |
| oracle | lyapunov | 0.251 | 1.57 [1.51, 1.64] | substantial | 0.674 [0.665, 0.684] | 0.075 / 0.447 / 0.857 / 0.826 |
| oracle | RO | 0.201 | 1.26 [1.22, 1.3] | substantial | 0.621 [0.611, 0.631] | 0.117 / 0.488 / 0.89 / 0.773 |
| oracle | R | 0.22 | 1.37 [1.33, 1.42] | substantial | 0.523 [0.513, 0.533] | 0.101 / 0.498 / 0.893 / 0.792 |
| oracle | O | 0.202 | 1.26 [1.22, 1.3] | substantial | 0.618 [0.609, 0.628] | 0.118 / 0.498 / 0.89 / 0.772 |
| oracle | I | 0.172 | 1.08 [1.05, 1.1] | substantial | 0.683 [0.674, 0.692] | 0.102 / 0.501 / 0.894 / 0.792 |
| oracle | N | 0.215 | 1.34 [1.29, 1.39] | substantial | 0.573 [0.562, 0.583] | 0.106 / 0.497 / 0.898 / 0.792 |
| oracle | ROIN | 0.16 | 1 |  | 0.719 [0.711, 0.728] | 0.106 / 0.502 / 0.891 / 0.785 |
| oracle | X | 0.171 | 1.07 [1.02, 1.11] | needed, size not determined | 0.695 [0.685, 0.705] | 0.148 / 0.497 / 0.857 / 0.709 |
| oracle | X+F | 0.135 | 0.844 [0.823, 0.867] | lowers | 0.765 [0.758, 0.773] | 0.155 / 0.498 / 0.849 / 0.694 |
| oracle | Lyapunov rank (C only) | | | | 0.671 [0.662, 0.681] | |
| deployable | none | 0.221 | 1.4 [1.35, 1.45] | substantial | 0.5 [0.5, 0.5] | 0.102 / 0.497 / 0.895 / 0.793 |
| deployable | lyapunov | 0.255 | 1.61 [1.55, 1.67] | substantial | 0.671 [0.662, 0.68] | 0.0769 / 0.447 / 0.86 / 0.83 |
| deployable | RO | 0.194 | 1.23 [1.19, 1.27] | substantial | 0.635 [0.625, 0.645] | 0.122 / 0.497 / 0.901 / 0.779 |
| deployable | R | 0.221 | 1.4 [1.35, 1.45] | substantial | 0.511 [0.503, 0.519] | 0.0996 / 0.494 / 0.896 / 0.796 |
| deployable | O | 0.198 | 1.25 [1.22, 1.29] | substantial | 0.629 [0.619, 0.639] | 0.11 / 0.497 / 0.902 / 0.792 |
| deployable | I | 0.174 | 1.1 [1.08, 1.12] | substantial | 0.681 [0.673, 0.689] | 0.0949 / 0.503 / 0.898 / 0.803 |
| deployable | N | 0.216 | 1.36 [1.32, 1.41] | substantial | 0.565 [0.557, 0.573] | 0.105 / 0.495 / 0.899 / 0.794 |
| deployable | ROIN | 0.158 | 1 |  | 0.72 [0.712, 0.728] | 0.124 / 0.499 / 0.893 / 0.77 |
| deployable | X | 0.172 | 1.09 [1.05, 1.13] | needed, size not determined | 0.694 [0.685, 0.703] | 0.137 / 0.499 / 0.869 / 0.732 |
| deployable | X+F | 0.135 | 0.856 [0.834, 0.878] | lowers | 0.767 [0.761, 0.774] | 0.143 / 0.501 / 0.861 / 0.719 |
| deployable | Lyapunov rank (C only) | | | | 0.668 [0.659, 0.677] | |

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| profile | pair | Delta [CI] | Holm p | detected |
|---|---|---|---|---|
| oracle | RO | 0.00103 [0.000346, 0.0018] | 0.003 | True |
| oracle | RI (primary) | 0.0015 [0.000561, 0.00247] | 0.003 | True |
| oracle | RN | 0.00025 [-0.00024, 0.000748] | 0.095 | False |
| oracle | OI (primary) | 0.00563 [0.00306, 0.00835] | 0.003 | True |
| oracle | ON | 0.00151 [0.000651, 0.00245] | 0.003 | True |
| oracle | IN | 0.000796 [-0.00018, 0.0017] | 0.031 | True |
| deployable | RO | 0.00126 [0.000258, 0.00234] | 0.0075 | True |
| deployable | RI (primary) | 0.000261 [-0.000841, 0.00134] | 0.792 | False |
| deployable | RN | 0.000113 [-0.000358, 0.000578] | 0.792 | False |
| deployable | OI (primary) | 0.00823 [0.00608, 0.0104] | 0.003 | True |
| deployable | ON | 0.00069 [-0.000181, 0.00153] | 0.06 | False |
| deployable | IN | 0.000203 [-0.000787, 0.00125] | 0.792 | False |

