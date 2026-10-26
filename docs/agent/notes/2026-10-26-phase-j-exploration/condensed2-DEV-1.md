DEVELOPMENT (DEV-1): exploratory, not a hypothesis test | run commit f701a47 | analysis ea0bd77 dirty False

Checks
- lorenz63: f1 True, g drop-N True all True, 397s; (f2) flagged 15: H=8 O: dependence bias detectable (interval excludes 0) (t1+t2/V 0.132, z -0.266); H=8 RO: dependence bias detectable (interval excludes 0) (t1+t2/V 0.136, z -0.245); H=8 OI: dependence bias detectable (interval excludes 0) (t1+t2/V 0.163, z -0.213); H=8 X+F: dependence bias detectable (interval excludes 0) (t1+t2/V 0.256, z -0.362); H=8 swap-R: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0161, z -0.43); H=8 swap-O: dependence bias detectable (interval excludes 0) (t1+t2/V 0.071, z -0.43) ...
- rossler: f1 True, g drop-N True all True, 390s; (f2) flagged 69: H=8 R: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0147, z 1.05); H=8 N: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0155, z 1.52); H=8 RO: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0244, z 1.05); H=8 RI: dependence bias detectable (interval excludes 0) (t1+t2/V 0.015, z 0.946); H=8 RN: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0214, z 1.62); H=8 ON: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0188, z 1.76) ...
- chua: f1 True, g drop-N True all True, 392s; (f2) flagged 11: H=8 ON: dependence bias detectable (interval excludes 0) (t1+t2/V -0.0177, z -0.792); H=8 RON: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0167, z 6.44); H=8 ROIN: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0229, z 4); H=8 X+F: dependence bias detectable (interval excludes 0) (t1+t2/V 0.00684, z 3.27); H=8 swap-N: dependence bias detectable (interval excludes 0) (t1+t2/V 0.000237, z 1.84); H=15 N: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0319, z 1.74) ...

A. Allocation drop-one MSE(F\X)/MSE(F) [CI 1-0.05/4] reading (* = n_eff<50); Shapley share of phi_A R/O/I/N
| sys | H | prof | n_eff k / x~ | R | O | I | N | phi share R/O/I/N |
|---|---|---|---|---|---|---|---|---|
| lorenz63 | H=8 (0.27 LT) | ora | 23.3 / 31.1 | 1.05 [0.884, 1.2] und* | 4.33 [3.19, 6.31] und* | 1.01 [0.843, 1.23] und* | 0.979 [0.924, 1.02] und* | -0.0456/0.636/0.314/0.0949 |
| lorenz63 | H=8 (0.27 LT) | dep | 23.3 / 31.1 | 0.937 [0.603, 1.49] und* | 1.21 [0.858, 1.74] und* | 1.11 [0.724, 1.9] und* | 1.3 [0.862, 1.83] und* | -0.199/0.358/0.364/0.478 |
| lorenz63 | H=30 (1.00 LT) | ora | 62.8 / 32 | 1.12 [1, 1.36] und* | 1.19 [1.03, 1.47] und* | 1.05 [0.995, 1.11] und* | 1.03 [0.942, 1.13] und* | 0.0703/0.458/0.32/0.152 |
| lorenz63 | H=30 (1.00 LT) | dep | 62.8 / 32 | 1.05 [0.94, 1.25] und* | 1 [0.941, 1.08] und* | 1.09 [0.97, 1.3] und* | 1.1 [0.991, 1.28] und* | 0.117/0.0816/0.505/0.296 |
| lorenz63 | H=120 (4.00 LT) | ora | 439 / 260 | 0.996 [0.982, 1.01] negl | 0.995 [0.981, 1.01] negl | 1.01 [1, 1.01] small | 0.998 [0.989, 1.01] negl | 0.664/1.62/-2.15/0.873 |
| lorenz63 | H=120 (4.00 LT) | dep | 439 / 260 | 0.998 [0.992, 1.01] negl | 1 [0.994, 1.01] negl | 1 [0.997, 1.01] negl | 1 [0.995, 1.01] negl | 0.059/0.294/0.445/0.202 |
| rossler | H=8 (0.27 LT) | ora | 269 / 61.8 | 1.06 [1.03, 1.12] needed | 1.02 [1.01, 1.05] needed | 1 [0.999, 1] negl | 1.01 [1.01, 1.02] small | 0.607/0.126/0.00167/0.266 |
| rossler | H=8 (0.27 LT) | dep | 269 / 61.8 | 1 [0.993, 1.01] negl | 1 [0.986, 1.02] negl | 1 [0.998, 1] negl | 0.994 [0.984, 1] negl | 0.333/-0.12/-0.0447/0.831 |
| rossler | H=30 (1.00 LT) | ora | 112 / 111 | 1.1 [1.06, 1.14] subst | 1.04 [1.02, 1.07] needed | 1 [0.995, 1.01] negl | 1.01 [0.995, 1.02] negl | 0.637/0.167/0.00086/0.195 |
| rossler | H=30 (1.00 LT) | dep | 112 / 111 | 1.01 [0.998, 1.04] negl | 1.01 [0.996, 1.04] negl | 1 [0.994, 1.01] negl | 1 [0.994, 1.01] negl | 0.361/0.373/-0.0183/0.284 |
| rossler | H=120 (4.00 LT) | ora | 392 / 236 | 1.02 [1, 1.04] small | 0.999 [0.991, 1.01] negl | 1 [0.997, 1.01] negl | 1 [0.998, 1] negl | 0.833/-0.0495/0.136/0.0805 |
| rossler | H=120 (4.00 LT) | dep | 392 / 236 | 1.01 [0.998, 1.01] negl | 1 [0.992, 1.01] negl | 1 [0.996, 1.01] negl | 0.999 [0.997, 1] negl | 0.664/0.0647/0.228/0.0426 |
| chua | H=8 (0.27 LT) | ora | 19.4 / 10.4 | 0.984 [0.893, 1.05] und* | 1.04 [0.859, 1.23] und* | 1.27 [0.926, 2.1] und* | 1.05 [0.841, 1.33] und* | 0.0376/0.139/0.735/0.0889 |
| chua | H=8 (0.27 LT) | dep | 19.4 / 10.4 | 1.08 [0.934, 1.35] und* | 1.02 [0.8, 1.36] und* | 1.06 [0.952, 1.3] und* | 0.981 [0.88, 1.1] und* | 0.617/0.362/-0.359/0.379 |
| chua | H=30 (1.00 LT) | ora | 41.2 / 30.2 | 1.02 [0.98, 1.08] und* | 1.05 [0.985, 1.21] und* | 1.01 [0.999, 1.01] und* | 1.04 [0.982, 1.08] und* | 0.203/0.314/0.178/0.305 |
| chua | H=30 (1.00 LT) | dep | 41.2 / 30.2 | 0.997 [0.973, 1.02] und* | 1.02 [0.997, 1.05] und* | 1 [0.997, 1.01] und* | 0.998 [0.99, 1.01] und* | 21/-20.4/-15.8/16.2 |
| chua | H=120 (4.00 LT) | ora | 498 / 305 | 1.01 [1, 1.03] small | 1 [0.997, 1.01] negl | 0.998 [0.991, 1.01] negl | 1 [0.998, 1] negl | 0.872/0.0822/-0.142/0.188 |
| chua | H=120 (4.00 LT) | dep | 498 / 305 | 1 [0.995, 1.01] negl | 1.01 [0.998, 1.02] negl | 0.998 [0.984, 1.01] negl | 1 [0.997, 1.01] negl | 0.225/0.56/-0.231/0.447 |

B. Primary pairs, logit u interior: Delta [CI 1-0.05/6], Holm p, reading
| sys | H | prof | R x I | O x I | other pairs detected |
|---|---|---|---|---|---|
| lorenz63 | H=8 (0.27 LT) | ora | 0.0363 [-0.087, 0.161] p=1 none | -0.0291 [-0.169, 0.128] p=1 none | none |
| lorenz63 | H=8 (0.27 LT) | dep | 0.00102 [-0.0599, 0.0595] p=1 none | 0.00286 [-0.0576, 0.0625] p=1 none | none |
| lorenz63 | H=30 (1.00 LT) | ora | 0.029 [-0.101, 0.148] p=1 none | 0.111 [-0.0389, 0.258] p=0.15 none | none |
| lorenz63 | H=30 (1.00 LT) | dep | 0.0285 [-0.0493, 0.102] p=0.807 none | -0.00493 [-0.0604, 0.0476] p=1 none | none |
| lorenz63 | H=120 (4.00 LT) | ora | -0.0012 [-0.0616, 0.0581] p=1 none | 0.0878 [0.0133, 0.154] p=0.006 DETECTED | RO |
| lorenz63 | H=120 (4.00 LT) | dep | 0.0269 [-0.00137, 0.0533] p=0.039 DETECTED | 0.0412 [-0.0603, 0.129] p=0.587 none | none |
| rossler | H=8 (0.27 LT) | ora | 0.0119 [-0.0387, 0.0621] p=0.706 none | 0.0233 [-0.0155, 0.0599] p=0.26 none | RO |
| rossler | H=8 (0.27 LT) | dep | -0.0154 [-0.0599, 0.0243] p=0.824 none | 0.0375 [-0.0152, 0.0877] p=0.167 none | RO |
| rossler | H=30 (1.00 LT) | ora | 0.0786 [-0.0616, 0.226] p=0.425 none | 0.0637 [-0.0811, 0.209] p=0.514 none | none |
| rossler | H=30 (1.00 LT) | dep | 0.0264 [-0.0195, 0.0725] p=0.202 none | 0.0112 [-0.0285, 0.0525] p=0.258 none | none |
| rossler | H=120 (4.00 LT) | ora | 0.00423 [-0.0276, 0.0335] p=1 none | 0.00418 [-0.01, 0.0177] p=1 none | none |
| rossler | H=120 (4.00 LT) | dep | 0.00243 [-0.0107, 0.0168] p=1 none | 0.00763 [-0.0112, 0.03] p=0.825 none | none |
| chua | H=8 (0.27 LT) | ora | 0.00999 [-0.0426, 0.0658] p=1 none | 0.0434 [0.00435, 0.0904] p=0.018 DETECTED | none |
| chua | H=8 (0.27 LT) | dep | 0.0285 [-0.00752, 0.0668] p=0.122 none | 0.0229 [-0.0108, 0.0583] p=0.138 none | none |
| chua | H=30 (1.00 LT) | ora | 0.0289 [-0.0415, 0.104] p=0.417 none | 0.0439 [-0.0218, 0.107] p=0.165 none | ON |
| chua | H=30 (1.00 LT) | dep | 0.0199 [-0.0295, 0.0703] p=0.36 none | 0.0454 [-0.0105, 0.103] p=0.096 none | none |
| chua | H=120 (4.00 LT) | ora | 0.0181 [-0.112, 0.139] p=1 none | 0.041 [-0.0367, 0.115] p=0.507 none | none |
| chua | H=120 (4.00 LT) | dep | -0.0529 [-0.155, 0.0465] p=1 none | -0.0183 [-0.128, 0.0849] p=1 none | none |

D. Allocation ladder, key rungs: MSE(rung)/MSE(F) [CI 1-0.05/m] reading; gaps (L_A)
| sys | H | prof | constant | separation | RO | X+F | theory gap (UB) | estimation gap |
|---|---|---|---|---|---|---|---|---|
| lorenz63 | H=8 (0.27 LT) | ora | 12.1 [6.22, 21.5] und* | 1.12 [0.863, 1.66] und* | 1.07 [0.838, 1.46] und* | 0.937 [0.793, 1.07] und* | 9.6e-05 [3.29e-05, 0.000209] | 0.00473 [0.00223, 0.0081] |
| lorenz63 | H=8 (0.27 LT) | dep | 1.72 [0.841, 4.03] und* | 5.78 [2.03, 16.7] und* | 1.61 [0.938, 3.39] und* | 0.25 [0.111, 0.623] und* |  |  |
| lorenz63 | H=30 (1.00 LT) | ora | 2.17 [1.47, 3.52] und* | 1.01 [0.901, 1.13] und* | 1.08 [0.95, 1.24] und* | 0.99 [0.873, 1.14] und* | 0.00965 [0.00504, 0.0155] | 0.0152 [0.00428, 0.0297] |
| lorenz63 | H=30 (1.00 LT) | dep | 1.45 [1.04, 2.44] und* | 1.67 [1.09, 3.03] und* | 1.21 [1.02, 1.62] und* | 0.92 [0.727, 1.17] und* |  |  |
| lorenz63 | H=120 (4.00 LT) | ora | 0.997 [0.978, 1.02] negl | 1.11 [1.05, 1.16] subst | 1 [0.993, 1.02] negl | 0.983 [0.97, 0.999] lowers | 0.277 [0.253, 0.304] | -0.0223 [-0.0663, 0.0285] |
| lorenz63 | H=120 (4.00 LT) | dep | 1.01 [0.991, 1.02] negl | 1.07 [1.03, 1.11] needed | 1.01 [0.997, 1.02] negl | 0.984 [0.968, 1] negl |  |  |
| rossler | H=8 (0.27 LT) | ora | 1.11 [1.07, 1.17] subst | 1.06 [1.03, 1.08] needed | 1.01 [1, 1.02] small | 0.999 [0.996, 1] negl | 1.16e-05 [9.81e-06, 1.36e-05] | 7.34e-06 [5.27e-07, 1.42e-05] |
| rossler | H=8 (0.27 LT) | dep | 0.994 [0.973, 1.02] negl | 1.06 [1.03, 1.1] needed | 0.994 [0.981, 1] negl | 0.986 [0.974, 0.997] lowers |  |  |
| rossler | H=30 (1.00 LT) | ora | 1.15 [1.1, 1.21] subst | 1.04 [1.02, 1.06] needed | 1.01 [0.994, 1.02] negl | 1 [0.992, 1.02] negl | 5.51e-05 [4.67e-05, 6.52e-05] | 8.88e-05 [2.01e-05, 0.00016] |
| rossler | H=30 (1.00 LT) | dep | 1.02 [0.99, 1.06] und | 1.05 [1.01, 1.09] needed | 1 [0.992, 1.02] negl | 0.991 [0.975, 1.01] negl |  |  |
| rossler | H=120 (4.00 LT) | ora | 1.02 [1, 1.04] small | 1.03 [0.993, 1.06] und | 1 [0.996, 1.01] negl | 0.985 [0.969, 1] negl | 0.0273 [0.0247, 0.0301] | 0.000176 [-0.005, 0.00533] |
| rossler | H=120 (4.00 LT) | dep | 1.01 [0.994, 1.03] negl | 1.05 [1.01, 1.08] needed | 1 [0.993, 1.01] negl | 0.983 [0.967, 1] negl |  |  |
| chua | H=8 (0.27 LT) | ora | 1.31 [1.05, 1.71] und* | 0.922 [0.718, 1.07] und* | 1.47 [0.978, 2.45] und* | 1.1 [0.843, 1.47] und* | 0.000122 [5.17e-05, 0.000217] | 4.63e-05 [-9.54e-05, 0.000207] |
| chua | H=8 (0.27 LT) | dep | 1.08 [0.93, 1.29] und* | 1.01 [0.909, 1.1] und* | 0.991 [0.89, 1.1] und* | 0.932 [0.85, 0.996] und* |  |  |
| chua | H=30 (1.00 LT) | ora | 1.04 [0.979, 1.16] und* | 1.02 [0.987, 1.06] und* | 1.04 [1.01, 1.09] und* | 1.01 [0.993, 1.02] und* | 0.0022 [0.00142, 0.00315] | -0.000765 [-0.00593, 0.00415] |
| chua | H=30 (1.00 LT) | dep | 1 [0.966, 1.05] und* | 1.06 [1.02, 1.13] und* | 1 [0.989, 1.02] und* | 1.02 [0.994, 1.07] und* |  |  |
| chua | H=120 (4.00 LT) | ora | 1.02 [1, 1.04] small | 1.05 [1.02, 1.08] needed | 0.998 [0.99, 1.01] negl | 1.01 [0.992, 1.02] negl | 0.16 [0.147, 0.176] | -0.0285 [-0.0572, 0.00146] |
| chua | H=120 (4.00 LT) | dep | 1.01 [0.987, 1.04] negl | 1.05 [1.01, 1.1] needed | 0.998 [0.982, 1.01] negl | 1 [0.992, 1.02] negl |  |  |

Horizon (Y = ln min(T_c, 240)): drop-one pinball ratio [CI 1-0.05/4] reading; Harrell's C
| sys | prof | R | O | I | N | C(F) | C(X+F) | C(Lyapunov rank) | pairs detected |
|---|---|---|---|---|---|---|---|---|---|
| lorenz63 | ora | 1.01 [0.982, 1.03] negl | 1.08 [1.03, 1.14] needed | 1.22 [1.15, 1.31] subst | 0.992 [0.959, 1.02] negl | 0.678 | 0.72 | 0.587 | RO,RI,OI |
| lorenz63 | dep | 1 [0.986, 1.01] negl | 1.07 [1.03, 1.12] needed | 1.21 [1.13, 1.31] subst | 0.99 [0.976, 1] negl | 0.673 | 0.716 | 0.59 | OI,IN |
| rossler | ora | 1.03 [1, 1.05] small | 1.1 [1.05, 1.16] subst | 1.2 [1.14, 1.27] subst | 1.01 [0.983, 1.03] negl | 0.692 | 0.777 | 0.62 | RO,OI |
| rossler | dep | 1.01 [0.998, 1.02] negl | 1.13 [1.09, 1.17] subst | 1.19 [1.13, 1.25] subst | 1.01 [0.998, 1.02] negl | 0.691 | 0.777 | 0.615 | OI |
| chua | ora | 1.02 [0.99, 1.04] negl | 1.07 [1.04, 1.11] needed | 1.25 [1.17, 1.34] subst | 1 [0.983, 1.02] negl | 0.725 | 0.776 | 0.671 | RO,OI |
| chua | dep | 1.01 [0.995, 1.03] negl | 1.08 [1.05, 1.12] subst | 1.23 [1.16, 1.3] subst | 1 [0.991, 1.01] negl | 0.727 | 0.773 | 0.666 | OI |
