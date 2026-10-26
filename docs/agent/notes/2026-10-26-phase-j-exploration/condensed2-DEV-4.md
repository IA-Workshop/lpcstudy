DEVELOPMENT (DEV-4): exploratory, not a hypothesis test | run commit f701a47 | analysis ea0bd77 dirty False

Checks
- lorenz63: f1 True, g drop-N True all True, 396s; (f2) flagged 17: H=8 O: dependence bias detectable (interval excludes 0) (t1+t2/V -0.0716, z -0.653); H=8 N: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0338, z -0.438); H=8 RO: dependence bias detectable (interval excludes 0) (t1+t2/V -0.0813, z -0.623); H=8 ON: dependence bias detectable (interval excludes 0) (t1+t2/V -0.0562, z -0.61); H=8 X+F: dependence bias detectable (interval excludes 0) (t1+t2/V -0.116, z -0.601); H=8 swap-R: dependence bias detectable (interval excludes 0) (t1+t2/V 0.00322, z -0.481) ...
- rossler: f1 True, g drop-N True all True, 392s; (f2) flagged 64: H=8 R: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0134, z 3.87); H=8 N: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0137, z 3.27); H=8 RO: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0211, z 4.27); H=8 RI: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0134, z 4.02); H=8 RN: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0184, z 3.79); H=8 ON: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0149, z 3.07) ...
- chua: f1 True, g drop-N True all True, 393s; (f2) flagged 34: H=8 R: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0146, z 2.92); H=8 RO: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0134, z 2.56); H=8 RI: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0136, z 2.9); H=8 RN: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0144, z 2.41); H=8 ROI: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0138, z 2.82); H=8 RON: dependence bias detectable (interval excludes 0) (t1+t2/V 0.0136, z 2.19) ...

A. Allocation drop-one MSE(F\X)/MSE(F) [CI 1-0.05/4] reading (* = n_eff<50); Shapley share of phi_A R/O/I/N
| sys | H | prof | n_eff k / x~ | R | O | I | N | phi share R/O/I/N |
|---|---|---|---|---|---|---|---|---|
| lorenz63 | H=8 (0.27 LT) | ora | 24.4 / 18.7 | 1.08 [1, 1.21] und* | 1.22 [0.559, 5.9] und* | 1.71 [0.69, 2.84] und* | 0.982 [0.911, 1.11] und* | 0.105/0.277/0.6/0.0184 |
| lorenz63 | H=8 (0.27 LT) | dep | 24.4 / 18.7 | 1.01 [0.807, 1.31] und* | 1.22 [0.907, 1.79] und* | 1.18 [0.743, 1.87] und* | 0.958 [0.804, 1.08] und* | 0.0765/0.653/0.509/-0.238 |
| lorenz63 | H=30 (1.00 LT) | ora | 47.9 / 47 | 0.948 [0.704, 1.18] und* | 1.06 [0.715, 1.63] und* | 0.987 [0.756, 1.21] und* | 1.03 [0.923, 1.13] und* | -0.17/1.04/0.313/-0.18 |
| lorenz63 | H=30 (1.00 LT) | dep | 47.9 / 47 | 1.18 [1.04, 1.39] und* | 1.03 [0.961, 1.11] und* | 1.06 [0.857, 1.27] und* | 0.964 [0.871, 1.03] und* | 1.29/0.186/0.454/-0.933 |
| lorenz63 | H=120 (4.00 LT) | ora | 445 / 322 | 0.994 [0.977, 1.01] negl | 1.02 [1, 1.03] negl | 1.01 [0.998, 1.02] negl | 1 [0.994, 1.01] negl | -0.164/0.837/0.339/-0.0119 |
| lorenz63 | H=120 (4.00 LT) | dep | 445 / 322 | 0.998 [0.992, 1] negl | 1 [0.999, 1.01] negl | 1 [0.997, 1.01] negl | 1 [0.999, 1] negl | -0.19/0.452/0.779/-0.041 |
| rossler | H=8 (0.27 LT) | ora | 195 / 205 | 1.04 [1.03, 1.06] needed | 1.01 [1, 1.02] small | 1 [1, 1] negl | 1.01 [1, 1.02] negl | 0.622/0.0746/-0.00318/0.307 |
| rossler | H=8 (0.27 LT) | dep | 195 / 205 | 1 [0.99, 1.01] negl | 1 [0.992, 1.01] negl | 1 [0.996, 1] negl | 1.01 [0.995, 1.02] negl | 0.142/-0.688/-0.779/2.32 |
| rossler | H=30 (1.00 LT) | ora | 123 / 99.3 | 1.09 [1.06, 1.14] subst | 1.03 [1.01, 1.05] small | 0.999 [0.993, 1] negl | 1.01 [0.998, 1.02] negl | 0.657/0.101/0.0162/0.225 |
| rossler | H=30 (1.00 LT) | dep | 123 / 99.3 | 1.01 [0.983, 1.03] negl | 1.01 [0.993, 1.03] negl | 1 [0.997, 1] negl | 0.999 [0.987, 1.01] negl | 0.384/0.312/-0.00207/0.306 |
| rossler | H=120 (4.00 LT) | ora | 414 / 227 | 1.01 [0.999, 1.02] negl | 1 [1, 1.01] small | 1 [0.994, 1.01] negl | 1 [0.997, 1] negl | 0.538/0.116/0.254/0.0917 |
| rossler | H=120 (4.00 LT) | dep | 414 / 227 | 1 [0.995, 1.01] negl | 1 [0.999, 1.01] negl | 1 [0.996, 1.01] negl | 0.999 [0.997, 1] negl | 0.145/0.171/0.614/0.0699 |
| chua | H=8 (0.27 LT) | ora | 13.7 / 5.11 | 1.04 [1, 1.07] und* | 1.06 [0.987, 1.15] und* | 1.05 [0.984, 1.12] und* | 1.04 [0.984, 1.11] und* | 0.255/0.322/0.144/0.279 |
| chua | H=8 (0.27 LT) | dep | 13.7 / 5.11 | 0.985 [0.957, 1.02] und* | 1 [0.999, 1] und* | 0.992 [0.984, 0.998] und* | 1 [0.991, 1.01] und* | 0.676/-0.0487/0.231/0.142 |
| chua | H=30 (1.00 LT) | ora | 47.9 / 14.6 | 1.09 [0.943, 1.28] und* | 0.987 [0.913, 1.03] und* | 1 [0.999, 1] und* | 1.01 [0.997, 1.03] und* | 0.891/-0.0562/0.0251/0.141 |
| chua | H=30 (1.00 LT) | dep | 47.9 / 14.6 | 1.05 [0.981, 1.15] und* | 0.994 [0.956, 1.02] und* | 1.02 [1, 1.04] und* | 1.01 [0.994, 1.04] und* | 0.612/-0.0433/0.138/0.294 |
| chua | H=120 (4.00 LT) | ora | 502 / 326 | 1.02 [1.01, 1.04] small | 1 [0.998, 1.01] negl | 1 [0.998, 1.01] negl | 1.01 [0.996, 1.02] negl | 0.71/0.0914/0.0336/0.165 |
| chua | H=120 (4.00 LT) | dep | 502 / 326 | 0.996 [0.986, 1.01] negl | 0.996 [0.987, 1.01] negl | 0.995 [0.983, 1.01] negl | 1 [0.996, 1.01] negl | 0.329/0.377/-0.865/1.16 |

B. Primary pairs, logit u interior: Delta [CI 1-0.05/6], Holm p, reading
| sys | H | prof | R x I | O x I | other pairs detected |
|---|---|---|---|---|---|
| lorenz63 | H=8 (0.27 LT) | ora | 0.0798 [-0.13, 0.28] p=0.592 none | -0.0106 [-0.0838, 0.0559] p=0.82 none | RO,RN |
| lorenz63 | H=8 (0.27 LT) | dep | 9.68e-05 [-0.0776, 0.0815] p=1 none | 0.0123 [-0.041, 0.0761] p=1 none | none |
| lorenz63 | H=30 (1.00 LT) | ora | 0.121 [-0.0425, 0.31] p=0.154 none | -0.0901 [-0.331, 0.112] p=1 none | IN |
| lorenz63 | H=30 (1.00 LT) | dep | 0.0914 [-0.00513, 0.21] p=0.045 DETECTED | 0.0148 [-0.0569, 0.0848] p=0.291 none | none |
| lorenz63 | H=120 (4.00 LT) | ora | 0.026 [-0.0379, 0.0838] p=0.867 none | 0.0263 [-0.0988, 0.141] p=1 none | none |
| lorenz63 | H=120 (4.00 LT) | dep | 0.0194 [-0.01, 0.0513] p=0.252 none | 0.0446 [-0.078, 0.159] p=0.634 none | none |
| rossler | H=8 (0.27 LT) | ora | -0.0166 [-0.0682, 0.0395] p=1 none | -6.58e-05 [-0.0399, 0.0432] p=1 none | none |
| rossler | H=8 (0.27 LT) | dep | -0.00388 [-0.0318, 0.0285] p=1 none | 0.0396 [0.00362, 0.0795] p=0.015 DETECTED | RO |
| rossler | H=30 (1.00 LT) | ora | 0.00938 [-0.032, 0.0486] p=0.559 none | -0.00671 [-0.0611, 0.0482] p=0.628 none | RO,RN,ON,IN |
| rossler | H=30 (1.00 LT) | dep | -0.00369 [-0.0443, 0.0367] p=1 none | -0.0108 [-0.0655, 0.0417] p=1 none | none |
| rossler | H=120 (4.00 LT) | ora | 0.0247 [-0.0038, 0.0543] p=0.066 none | -0.00395 [-0.0189, 0.0107] p=1 none | none |
| rossler | H=120 (4.00 LT) | dep | 0.00449 [-0.00806, 0.0171] p=0.477 none | 0.00627 [-0.00395, 0.0166] p=0.252 none | RO |
| chua | H=8 (0.27 LT) | ora | 0.00114 [-0.0484, 0.0536] p=0.975 none | 0.0255 [-0.0297, 0.0851] p=0.318 none | none |
| chua | H=8 (0.27 LT) | dep | 0.0237 [-0.0345, 0.0764] p=0.56 none | -0.00372 [-0.0578, 0.0484] p=1 none | none |
| chua | H=30 (1.00 LT) | ora | 0.0142 [-0.0615, 0.0849] p=0.864 none | 0.0172 [-0.0744, 0.12] p=0.864 none | none |
| chua | H=30 (1.00 LT) | dep | 0.0463 [-0.0109, 0.109] p=0.0825 none | 0.071 [-0.0337, 0.183] p=0.148 none | IN |
| chua | H=120 (4.00 LT) | ora | 0.00216 [-0.105, 0.119] p=1 none | 0.00528 [-0.0843, 0.0959] p=1 none | none |
| chua | H=120 (4.00 LT) | dep | 0.0217 [-0.0227, 0.0645] p=0.594 none | 0.0148 [-0.0882, 0.126] p=1 none | none |

D. Allocation ladder, key rungs: MSE(rung)/MSE(F) [CI 1-0.05/m] reading; gaps (L_A)
| sys | H | prof | constant | separation | RO | X+F | theory gap (UB) | estimation gap |
|---|---|---|---|---|---|---|---|---|
| lorenz63 | H=8 (0.27 LT) | ora | 2.43 [1.47, 14.3] und* | 0.981 [0.618, 1.21] und* | 1.44 [0.794, 2.13] und* | 0.842 [0.289, 1.18] und* | 0.00248 [0.000118, 0.00655] | 0.00307 [-1.11e-05, 0.00641] |
| lorenz63 | H=8 (0.27 LT) | dep | 1.57 [1.11, 2.85] und* | 2.59 [1.2, 6.34] und* | 1.09 [0.604, 1.82] und* | 0.438 [0.0846, 0.798] und* |  |  |
| lorenz63 | H=30 (1.00 LT) | ora | 1.23 [0.811, 2.1] und* | 0.976 [0.66, 1.27] und* | 0.986 [0.739, 1.22] und* | 0.937 [0.695, 1.17] und* | 0.0167 [0.0082, 0.0284] | 0.00981 [-0.00314, 0.0232] |
| lorenz63 | H=30 (1.00 LT) | dep | 1.11 [0.759, 1.56] und* | 1.18 [0.742, 1.87] und* | 0.99 [0.755, 1.29] und* | 0.697 [0.468, 0.906] und* |  |  |
| lorenz63 | H=120 (4.00 LT) | ora | 1.02 [0.994, 1.04] negl | 1.08 [1.03, 1.14] needed | 1.01 [0.996, 1.02] negl | 1 [0.984, 1.02] negl | 0.257 [0.234, 0.283] | -0.0014 [-0.0504, 0.0464] |
| lorenz63 | H=120 (4.00 LT) | dep | 1.01 [0.991, 1.02] negl | 1.05 [1.01, 1.09] needed | 1 [0.995, 1.01] negl | 0.998 [0.979, 1.02] negl |  |  |
| rossler | H=8 (0.27 LT) | ora | 1.08 [1.06, 1.11] subst | 1.07 [1.05, 1.08] needed | 1.01 [1, 1.02] small | 0.997 [0.993, 1] negl | 1.21e-05 [1.05e-05, 1.37e-05] | 1.46e-05 [6.37e-06, 2.29e-05] |
| rossler | H=8 (0.27 LT) | dep | 1 [0.98, 1.02] negl | 1.1 [1.06, 1.14] subst | 1.01 [0.991, 1.02] negl | 0.987 [0.978, 0.997] lowers |  |  |
| rossler | H=30 (1.00 LT) | ora | 1.16 [1.11, 1.22] subst | 1.04 [1.02, 1.06] needed | 1.01 [0.996, 1.02] negl | 1.01 [0.99, 1.04] negl | 5.15e-05 [4.39e-05, 6e-05] | 8.83e-05 [2.1e-05, 0.000156] |
| rossler | H=30 (1.00 LT) | dep | 1.03 [0.994, 1.07] und | 1.08 [1.03, 1.13] needed | 1 [0.985, 1.01] negl | 0.995 [0.981, 1.01] negl |  |  |
| rossler | H=120 (4.00 LT) | ora | 1.02 [1, 1.04] small | 1.04 [1, 1.07] needed | 1 [0.993, 1.01] negl | 0.997 [0.991, 1] negl | 0.0306 [0.0271, 0.0344] | 0.000492 [-0.00558, 0.00654] |
| rossler | H=120 (4.00 LT) | dep | 1.01 [0.996, 1.03] negl | 1.07 [1.04, 1.12] needed | 1 [0.994, 1.01] negl | 0.996 [0.988, 1] negl |  |  |
| chua | H=8 (0.27 LT) | ora | 1.1 [1.02, 1.19] und* | 1.51 [0.968, 3.13] und* | 1.07 [0.986, 1.17] und* | 1.01 [0.998, 1.02] und* | 0.000112 [4.17e-05, 0.000225] | -8.81e-05 [-0.000264, 4.13e-05] |
| chua | H=8 (0.27 LT) | dep | 0.976 [0.936, 1.01] und* | 1.16 [1.06, 1.27] und* | 0.994 [0.981, 1] und* | 1 [0.995, 1] und* |  |  |
| chua | H=30 (1.00 LT) | ora | 1.12 [0.918, 1.36] und* | 0.915 [0.691, 1.06] und* | 1.02 [0.997, 1.04] und* | 1.02 [0.985, 1.08] und* | 0.0044 [0.0023, 0.00757] | 0.000444 [-0.00292, 0.00423] |
| chua | H=30 (1.00 LT) | dep | 1.1 [0.987, 1.25] und* | 1.01 [0.945, 1.09] und* | 1.03 [0.998, 1.07] und* | 1.04 [0.992, 1.11] und* |  |  |
| chua | H=120 (4.00 LT) | ora | 1.03 [1.01, 1.05] needed | 1.04 [1.01, 1.08] needed | 1.01 [0.997, 1.01] negl | 1 [0.989, 1.02] negl | 0.16 [0.144, 0.176] | 0.0402 [0.0095, 0.0653] |
| chua | H=120 (4.00 LT) | dep | 1 [0.985, 1.02] negl | 1.04 [0.998, 1.09] und | 0.995 [0.981, 1.01] negl | 0.994 [0.983, 1.01] negl |  |  |

Horizon (Y = ln min(T_c, 240)): drop-one pinball ratio [CI 1-0.05/4] reading; Harrell's C
| sys | prof | R | O | I | N | C(F) | C(X+F) | C(Lyapunov rank) | pairs detected |
|---|---|---|---|---|---|---|---|---|---|
| lorenz63 | ora | 1.01 [0.967, 1.05] und | 1.14 [1.08, 1.21] subst | 1.28 [1.18, 1.39] subst | 0.991 [0.967, 1.01] negl | 0.692 | 0.736 | 0.627 | OI |
| lorenz63 | dep | 1 [0.989, 1.02] negl | 1.14 [1.1, 1.19] subst | 1.29 [1.2, 1.39] subst | 0.985 [0.972, 0.999] lowers | 0.701 | 0.736 | 0.628 | RI,OI,ON |
| rossler | ora | 1.02 [1, 1.05] small | 1.1 [1.06, 1.14] subst | 1.23 [1.17, 1.31] subst | 1.01 [0.994, 1.02] negl | 0.683 | 0.759 | 0.638 | RO,OI |
| rossler | dep | 0.994 [0.985, 1] negl | 1.14 [1.1, 1.19] subst | 1.21 [1.14, 1.27] subst | 0.999 [0.988, 1.01] negl | 0.693 | 0.766 | 0.633 | RO,RI,OI |
| chua | ora | 1.02 [0.992, 1.04] negl | 1.09 [1.06, 1.13] subst | 1.23 [1.16, 1.3] subst | 1.02 [0.995, 1.04] negl | 0.721 | 0.766 | 0.654 | RI,OI |
| chua | dep | 1.01 [0.994, 1.02] negl | 1.1 [1.07, 1.14] subst | 1.23 [1.16, 1.29] subst | 1 [0.992, 1.02] negl | 0.727 | 0.76 | 0.657 | OI |
