DEVELOPMENT (DEV-3): exploratory, not a hypothesis test | run commit f701a47 | analysis ea0bd77 dirty False

Checks
- lorenz63: f1 True, g drop-N True all True, 391s; (f2) flagged 18: H=8 RO: dependence bias detectable (interval excludes 0) (t1+t2/V -0.149, z 0.386); H=8 X+F: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0445, z 0.786); H=8 swap-R: dependence bias detectable (interval excludes 0) (t1+t2/V 0.00828, z 0.773); H=15 RON: dependence bias detectable (interval excludes 0) (t1+t2/V -0.0405, z -0.925); H=15 swap-R: dependence bias detectable (interval excludes 0) (t1+t2/V 0.000265, z -0.787); H=15 swap-I: dependence bias detectable (interval excludes 0) (t1+t2/V 0.00436, z -0.779) ...
- rossler: f1 True, g drop-N True all True, 387s; (f2) flagged 71: H=8 R: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0137, z 0.351); H=8 N: dependence bias detectable (interval excludes 0) (t1+t2/V 0.013, z 0.442); H=8 RO: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0188, z 0.241); H=8 RI: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0137, z 0.329); H=8 RN: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0186, z 0.398); H=8 OI: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0031, z 0.206) ...
- chua: f1 True, g drop-N True all True, 387s; (f2) flagged 22: H=8 R: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0118, z 1.13); H=8 RO: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0144, z 0.363); H=8 RI: dependence bias detectable (interval excludes 0) (t1+t2/V 0.00999, z 0.761); H=8 RN: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0121, z 0.69); H=8 ROI: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0105, z 0.868); H=8 RON: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0119, z 0.778) ...

A. Allocation drop-one MSE(F\X)/MSE(F) [CI 1-0.05/4] reading (* = n_eff<50); Shapley share of phi_A R/O/I/N
| sys | H | prof | n_eff k / x~ | R | O | I | N | phi share R/O/I/N |
|---|---|---|---|---|---|---|---|---|
| lorenz63 | H=8 (0.27 LT) | ora | 24.1 / 17.8 | 1.06 [1.03, 1.16] und* | 3.6 [1.27, 9.33] und* | 1.09 [0.967, 1.18] und* | 1.01 [0.998, 1.02] und* | 0.00474/0.672/0.268/0.0555 |
| lorenz63 | H=8 (0.27 LT) | dep | 24.1 / 17.8 | 0.79 [0.426, 1.45] und* | 1.74 [1.2, 2.52] und* | 1.49 [0.857, 1.88] und* | 1.05 [0.823, 1.21] und* | -0.366/0.808/0.417/0.14 |
| lorenz63 | H=30 (1.00 LT) | ora | 62.6 / 33.8 | 1.07 [0.97, 1.21] und* | 1.07 [0.833, 1.41] und* | 1 [0.954, 1.05] und* | 0.972 [0.879, 1.05] und* | 0.0896/0.533/0.259/0.119 |
| lorenz63 | H=30 (1.00 LT) | dep | 62.6 / 33.8 | 1.12 [0.896, 1.47] und* | 1.04 [0.961, 1.14] und* | 0.994 [0.898, 1.08] und* | 1.03 [0.98, 1.11] und* | 0.548/0.0814/0.244/0.126 |
| lorenz63 | H=120 (4.00 LT) | ora | 447 / 301 | 1 [0.99, 1.02] negl | 1 [0.999, 1.01] negl | 1 [0.998, 1] negl | 1 [0.997, 1] negl | 0.395/1.01/0.189/-0.59 |
| lorenz63 | H=120 (4.00 LT) | dep | 447 / 301 | 0.996 [0.99, 1] negl | 1 [0.998, 1] negl | 1 [0.996, 1.01] negl | 1 [0.999, 1] negl | -0.575/1.17/0.272/0.129 |
| rossler | H=8 (0.27 LT) | ora | 189 / 9.95 | 1.18 [1.04, 1.48] needed | 1.09 [1, 1.27] needed | 0.999 [0.994, 1] negl | 1.01 [0.998, 1.01] negl | 0.618/0.347/-0.0418/0.0769 |
| rossler | H=8 (0.27 LT) | dep | 189 / 9.95 | 1 [0.987, 1.01] und* | 1 [0.987, 1.01] und* | 1 [0.993, 1.01] und* | 0.999 [0.991, 1.01] und* | 1.36/-0.465/-0.568/0.67 |
| rossler | H=30 (1.00 LT) | ora | 98 / 111 | 1.1 [1.07, 1.14] subst | 1.03 [1.01, 1.05] needed | 1 [0.992, 1.01] negl | 1 [0.99, 1.01] negl | 0.697/0.141/-0.00336/0.166 |
| rossler | H=30 (1.00 LT) | dep | 98 / 111 | 1.02 [1, 1.05] small | 1.02 [1.01, 1.04] small | 1 [0.994, 1.01] negl | 0.994 [0.98, 1.01] negl | 0.681/0.666/-0.0381/-0.309 |
| rossler | H=120 (4.00 LT) | ora | 395 / 203 | 1.01 [0.991, 1.02] negl | 0.993 [0.979, 1.01] negl | 1 [0.988, 1.02] negl | 0.999 [0.988, 1.01] negl | 0.694/-0.145/0.425/0.026 |
| rossler | H=120 (4.00 LT) | dep | 395 / 203 | 1 [0.993, 1.01] negl | 0.995 [0.986, 1] negl | 1.01 [0.998, 1.02] negl | 1 [0.998, 1] negl | 0.57/-0.57/0.724/0.276 |
| chua | H=8 (0.27 LT) | ora | 5.98 / 2.58 | 1.07 [1.01, 1.12] und* | 1.22 [1, 1.42] und* | 1.06 [0.991, 1.11] und* | 0.987 [0.945, 1.05] und* | 0.215/0.738/0.0568/-0.00992 |
| chua | H=8 (0.27 LT) | dep | 5.98 / 2.58 | 0.998 [0.981, 1.02] und* | 1 [0.999, 1.01] und* | 1.01 [0.996, 1.04] und* | 0.993 [0.981, 1] und* | 0.62/-0.386/-1.13/1.9 |
| chua | H=30 (1.00 LT) | ora | 49.5 / 12.4 | 1.03 [0.899, 1.15] und* | 0.984 [0.874, 1.06] und* | 0.989 [0.929, 1.04] und* | 1 [0.966, 1.03] und* | 1.51/-0.334/0.0933/-0.271 |
| chua | H=30 (1.00 LT) | dep | 49.5 / 12.4 | 1.02 [0.984, 1.06] und* | 0.999 [0.955, 1.05] und* | 1.01 [0.998, 1.03] und* | 0.984 [0.924, 1.05] und* | 0.642/0.00551/0.281/0.0724 |
| chua | H=120 (4.00 LT) | ora | 508 / 343 | 1.01 [0.996, 1.02] negl | 1 [0.997, 1] negl | 1 [0.999, 1.01] negl | 1 [0.999, 1] negl | 0.41/-0.00496/0.218/0.377 |
| chua | H=120 (4.00 LT) | dep | 508 / 343 | 1 [0.994, 1.01] negl | 0.999 [0.996, 1] negl | 1 [0.998, 1.01] negl | 1 [0.998, 1] negl | 0.0911/0.00806/0.427/0.473 |

B. Primary pairs, logit u interior: Delta [CI 1-0.05/6], Holm p, reading
| sys | H | prof | R x I | O x I | other pairs detected |
|---|---|---|---|---|---|
| lorenz63 | H=8 (0.27 LT) | ora | 0.0898 [-0.0555, 0.228] p=0.23 none | 0.00185 [-0.0998, 0.113] p=1 none | RO |
| lorenz63 | H=8 (0.27 LT) | dep | -0.00642 [-0.0664, 0.0517] p=0.78 none | 0.00613 [-0.0485, 0.0578] p=0.78 none | none |
| lorenz63 | H=30 (1.00 LT) | ora | 0.0143 [-0.122, 0.153] p=1 none | 0.0246 [-0.122, 0.155] p=1 none | none |
| lorenz63 | H=30 (1.00 LT) | dep | -0.0467 [-0.114, 0.0216] p=1 none | 0.0149 [-0.0387, 0.0746] p=1 none | none |
| lorenz63 | H=120 (4.00 LT) | ora | 0.0698 [0.00474, 0.15] p=0.0075 DETECTED | 0.0918 [0.0184, 0.166] p=0.003 DETECTED | none |
| lorenz63 | H=120 (4.00 LT) | dep | 0.0193 [-0.0322, 0.0791] p=0.712 none | 0.0425 [-0.0131, 0.0988] p=0.102 none | none |
| rossler | H=8 (0.27 LT) | ora | 0.00502 [-0.0303, 0.0398] p=0.702 none | 0.00833 [-0.0185, 0.0385] p=0.66 none | RN |
| rossler | H=8 (0.27 LT) | dep | 0.008 [-0.0161, 0.0348] p=0.58 none | 0.0209 [-0.0158, 0.0567] p=0.342 none | RO |
| rossler | H=30 (1.00 LT) | ora | 0.0143 [-0.0436, 0.0713] p=0.528 none | 0.00412 [-0.0518, 0.0625] p=0.528 none | RO,RN,ON |
| rossler | H=30 (1.00 LT) | dep | 0.0113 [-0.051, 0.068] p=0.84 none | -0.00495 [-0.0661, 0.0665] p=0.84 none | none |
| rossler | H=120 (4.00 LT) | ora | 0.0238 [-0.00819, 0.0583] p=0.102 none | 0.0222 [-0.00561, 0.0502] p=0.081 none | none |
| rossler | H=120 (4.00 LT) | dep | 0.0631 [0.00537, 0.123] p=0.012 DETECTED | 0.00658 [-0.0353, 0.0502] p=0.339 none | RN,IN |
| chua | H=8 (0.27 LT) | ora | 0.00495 [-0.0309, 0.042] p=0.707 none | 0.0216 [-0.0231, 0.0754] p=0.55 none | ON |
| chua | H=8 (0.27 LT) | dep | -0.0317 [-0.0719, 0.00963] p=0.981 none | 0.00815 [-0.0455, 0.0594] p=0.818 none | RO |
| chua | H=30 (1.00 LT) | ora | 0.0386 [-0.0311, 0.12] p=0.231 none | 0.0685 [0.00979, 0.136] p=0.006 DETECTED | none |
| chua | H=30 (1.00 LT) | dep | -0.0173 [-0.0713, 0.0426] p=1 none | 0.0471 [-0.0229, 0.115] p=0.231 none | none |
| chua | H=120 (4.00 LT) | ora | 0.017 [-0.016, 0.0507] p=0.564 none | 0.0135 [-0.0241, 0.0536] p=0.564 none | none |
| chua | H=120 (4.00 LT) | dep | 0.00524 [-0.0435, 0.0565] p=1 none | 0.0295 [-0.0353, 0.0922] p=0.552 none | none |

D. Allocation ladder, key rungs: MSE(rung)/MSE(F) [CI 1-0.05/m] reading; gaps (L_A)
| sys | H | prof | constant | separation | RO | X+F | theory gap (UB) | estimation gap |
|---|---|---|---|---|---|---|---|---|
| lorenz63 | H=8 (0.27 LT) | ora | 7.63 [2.74, 21.2] und* | 0.889 [0.383, 2.2] und* | 1.09 [0.979, 1.19] und* | 1.12 [0.951, 1.26] und* | 0.00055 [4.82e-05, 0.00152] | 0.00378 [0.00113, 0.0077] |
| lorenz63 | H=8 (0.27 LT) | dep | 1.89 [1.41, 2.99] und* | 4.34 [1.22, 9.77] und* | 1.59 [0.868, 2.11] und* | 0.361 [0.111, 1.13] und* |  |  |
| lorenz63 | H=30 (1.00 LT) | ora | 1.53 [0.959, 2.55] und* | 0.886 [0.573, 1.11] und* | 0.987 [0.878, 1.09] und* | 0.953 [0.802, 1.08] und* | 0.012 [0.0041, 0.0232] | 0.00942 [-0.00502, 0.0234] |
| lorenz63 | H=30 (1.00 LT) | dep | 1.39 [0.973, 2.16] und* | 1.61 [1, 2.77] und* | 1.03 [0.897, 1.17] und* | 0.885 [0.658, 1.02] und* |  |  |
| lorenz63 | H=120 (4.00 LT) | ora | 1 [0.995, 1.01] negl | 1.09 [1.05, 1.14] needed | 1 [0.996, 1.01] negl | 1 [0.98, 1.02] negl | 0.278 [0.252, 0.302] | 0.0392 [-0.00843, 0.0884] |
| lorenz63 | H=120 (4.00 LT) | dep | 1 [0.992, 1.01] negl | 1.08 [1.04, 1.12] needed | 1 [0.995, 1] negl | 0.99 [0.967, 1.01] negl |  |  |
| rossler | H=8 (0.27 LT) | ora | 1.24 [1.07, 1.63] subst | 1.05 [1.01, 1.07] needed | 1 [0.995, 1.01] negl | 0.994 [0.982, 1.01] negl | 1.36e-05 [1.14e-05, 1.62e-05] | 3.9e-06 [-3.19e-06, 1.09e-05] |
| rossler | H=8 (0.27 LT) | dep | 0.999 [0.975, 1.02] und* | 1.09 [1.06, 1.13] und* | 1.01 [0.991, 1.02] und* | 0.995 [0.974, 1.02] und* |  |  |
| rossler | H=30 (1.00 LT) | ora | 1.15 [1.11, 1.2] subst | 1.02 [0.994, 1.03] negl | 1 [0.99, 1.02] negl | 0.997 [0.989, 1] negl | 5.82e-05 [4.71e-05, 7.07e-05] | 9.63e-05 [3.55e-05, 0.000163] |
| rossler | H=30 (1.00 LT) | dep | 1.02 [0.987, 1.06] und | 1.04 [1.01, 1.08] needed | 0.993 [0.977, 1.01] negl | 0.996 [0.978, 1.01] negl |  |  |
| rossler | H=120 (4.00 LT) | ora | 1.02 [0.993, 1.04] negl | 1.05 [1.01, 1.09] needed | 1 [0.986, 1.02] negl | 0.993 [0.98, 1.01] negl | 0.0285 [0.0248, 0.0328] | 0.00126 [-0.00455, 0.0075] |
| rossler | H=120 (4.00 LT) | dep | 1.01 [0.993, 1.03] negl | 1.04 [1, 1.08] needed | 1.01 [0.995, 1.02] negl | 0.996 [0.991, 1] negl |  |  |
| chua | H=8 (0.27 LT) | ora | 1.26 [1.03, 1.49] und* | 0.785 [0.459, 1.08] und* | 0.937 [0.84, 1.05] und* | 0.966 [0.886, 1.04] und* | 0.000233 [3.14e-05, 0.00056] | 1.03e-05 [-0.000349, 0.000288] |
| chua | H=8 (0.27 LT) | dep | 0.993 [0.972, 1.01] und* | 1.09 [1.01, 1.2] und* | 0.999 [0.973, 1.04] und* | 0.998 [0.965, 1.02] und* |  |  |
| chua | H=30 (1.00 LT) | ora | 1.03 [0.862, 1.17] und* | 0.965 [0.878, 1.04] und* | 0.986 [0.911, 1.05] und* | 0.968 [0.867, 1.04] und* | 0.0055 [0.00261, 0.00955] | -5.89e-05 [-0.00534, 0.00552] |
| chua | H=30 (1.00 LT) | dep | 1.05 [0.98, 1.12] und* | 0.994 [0.915, 1.11] und* | 1.02 [0.999, 1.05] und* | 0.984 [0.898, 1.04] und* |  |  |
| chua | H=120 (4.00 LT) | ora | 1.02 [1, 1.03] small | 1.06 [1.02, 1.1] needed | 1.02 [1.01, 1.03] small | 0.998 [0.995, 1] negl | 0.178 [0.161, 0.196] | 0.0461 [0.0122, 0.0779] |
| chua | H=120 (4.00 LT) | dep | 1.01 [1, 1.02] negl | 1.07 [1.03, 1.11] needed | 1.01 [0.999, 1.01] negl | 0.994 [0.984, 1] negl |  |  |

Horizon (Y = ln min(T_c, 240)): drop-one pinball ratio [CI 1-0.05/4] reading; Harrell's C
| sys | prof | R | O | I | N | C(F) | C(X+F) | C(Lyapunov rank) | pairs detected |
|---|---|---|---|---|---|---|---|---|---|
| lorenz63 | ora | 1.02 [0.985, 1.06] und | 1.11 [1.06, 1.16] subst | 1.24 [1.17, 1.33] subst | 1 [0.973, 1.03] negl | 0.675 | 0.731 | 0.595 | OI |
| lorenz63 | dep | 0.997 [0.982, 1.01] negl | 1.09 [1.06, 1.13] subst | 1.21 [1.14, 1.29] subst | 0.996 [0.982, 1.01] negl | 0.676 | 0.714 | 0.598 | OI |
| rossler | ora | 1.02 [0.999, 1.05] negl | 1.1 [1.06, 1.16] subst | 1.26 [1.19, 1.34] subst | 1 [0.985, 1.02] negl | 0.686 | 0.771 | 0.646 | OI |
| rossler | dep | 1.01 [0.991, 1.02] negl | 1.13 [1.08, 1.18] subst | 1.25 [1.19, 1.32] subst | 0.999 [0.986, 1.01] negl | 0.699 | 0.777 | 0.64 | RO,RI,OI |
| chua | ora | 1.01 [0.985, 1.04] negl | 1.04 [1.01, 1.07] needed | 1.26 [1.2, 1.34] subst | 1 [0.983, 1.02] negl | 0.712 | 0.767 | 0.686 | RO,OI |
| chua | dep | 1.01 [0.996, 1.02] negl | 1.07 [1.04, 1.11] needed | 1.25 [1.17, 1.33] subst | 0.997 [0.987, 1.01] negl | 0.723 | 0.768 | 0.683 | RO,RN,OI,ON,IN |
