# Phase J experiments C and E: CONF-7

**PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.** Run `phasej-CONF-7/phasej`; analysis commit `c19ad486b93a2ee96d64ce069ec42fd440428211` (dirty: False); A/D record `phasej-CONF-7/contrib-j/contrib.json`. Estimates with 95% intervals from the shared moving-block index sets (models fixed; training variance not included). Readings are descriptive; no causal claim; nothing here is set beside CONF-1.

## lorenz63

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| check | result |
|---|---|
| A2 rebuilt on 1..H_max equals the dumped A2 (bitwise); A4 horizon-free | True, True |
| refit reproduces WU-0048 (max abs: A/ROIN MSE oracle, deployable; W/ROIN L_w oracle, deployable) | 0 / 0 / 0 / 0 |
| T_c counts T = 1 / e_(T-1) = theta (A2 train, g train, A2 test, g test, A4 calibration) | 34/0, 114/0, 44/0, 141/0, 134/0 |
| A2 on 1..H_max: pooled curvature floor / columns at 0 or 1 | 0 / 0 |
| weights clipped to [0, 1] | g_oracle_test 3330, g_oracle_train_oof 2567, gw_oracle_test 2300, gw_oracle_train_oof 1926, g_deployable_test 2858, g_deployable_train_oof 3418, gw_deployable_test 1478, gw_deployable_train_oof 1051 |

### C1. Separate performance (from the A/D record, no refit)

Allocation: MSE per rule (oracle: moment form; deployable: realized); reading of the rung against F (MSE ratio, 1.05 table, n_eff guard). G(F) = 1 - L_A(F)/L_A(constant).

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| horizon | profile | constant | separation | RO | F (ROIN) | X | X+F | G(F) | sep vs F | RO vs F | X+F vs F |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 0.0149 | 0.00536 | 0.00431 | 0.00456 | 0.00404 | 0.00473 | 0.849 | undetermined | undetermined | undetermined |
| H=8 (0.27 LT) | deployable | 0.0147 | 0.0331 | 0.0123 | 0.0123 | 0.00424 | 0.00382 | 0.197 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | oracle | 0.036 | 0.0108 | 0.0104 | 0.00984 | 0.014 | 0.0115 | 0.943 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | deployable | 0.0376 | 0.0475 | 0.0273 | 0.0242 | 0.0145 | 0.015 | 0.457 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | oracle | 0.0556 | 0.0304 | 0.0306 | 0.0307 | 0.0314 | 0.0297 | 0.724 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | deployable | 0.0551 | 0.0647 | 0.0428 | 0.0437 | 0.0324 | 0.0345 | 0.336 | undetermined | undetermined | undetermined |
| H=60 (2.00 LT) | oracle | 0.168 | 0.15 | 0.149 | 0.148 | 0.154 | 0.146 | 0.32 | undetermined | negligible | negligible |
| H=60 (2.00 LT) | deployable | 0.174 | 0.179 | 0.165 | 0.163 | 0.159 | 0.157 | 0.166 | needed, size not determined | undetermined | lowers |
| H=120 (4.00 LT) | oracle | 0.887 | 0.96 | 0.88 | 0.875 | 0.873 | 0.868 | 0.0458 | substantial | small | lowers |
| H=120 (4.00 LT) | deployable | 0.876 | 0.929 | 0.873 | 0.871 | 0.867 | 0.867 | 0.0203 | needed, size not determined | negligible | negligible |

Horizon (Y = ln min(T_c, H_max)): pinball at 0.5 / Harrell's C / coverage of q_0.1 below the cap; reading against F.

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | C | cov q_0.1 | reading vs F |
|---|---|---|---|---|---|
| oracle | none | 0.197 | 0.5 | 0.111 | substantial |
| oracle | lyapunov | 0.3 | 0.613 | 0.0843 | substantial |
| oracle | RO | 0.193 | 0.564 | 0.143 | substantial |
| oracle | ROIN | 0.157 | 0.679 | 0.158 |  |
| oracle | X | 0.166 | 0.679 | 0.155 | needed, size not determined |
| oracle | X+F | 0.137 | 0.726 | 0.166 | lowers |
| oracle | Lyapunov rank | | 0.607 | | |
| deployable | none | 0.197 | 0.5 | 0.111 | substantial |
| deployable | lyapunov | 0.295 | 0.614 | 0.0795 | substantial |
| deployable | RO | 0.193 | 0.561 | 0.125 | substantial |
| deployable | ROIN | 0.158 | 0.678 | 0.135 |  |
| deployable | X | 0.165 | 0.681 | 0.155 | needed, size not determined |
| deployable | X+F | 0.141 | 0.722 | 0.158 | lowers |
| deployable | Lyapunov rank | | 0.61 | | |

### C2. Shared information (oracle and deployable profiles)

Skill retained = [L(constant) - L(bottleneck)] / [L(constant) - L(F)]; reading: keeps most (CI > 0.5), loses most (CI < 0.5), else not determined. Forward: horizon from g (five clipped weights; g_w: the L_w fits); reverse: weight from h (three quantiles), scored by L_A (MSE; deployable: realized per draw, R2 guard) and by L_w (weight units, unit-weight fits). Training inputs cross-fitted.

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| profile | direction | horizon | full skill [CI] | retained L_A / pinball [CI] | reading | retained L_w [CI] | reading L_w |
|---|---|---|---|---|---|---|---|
| oracle | forward (g; g_w) | all five | 0.0398 [0.0343, 0.0454] | 0.115 [0.0845, 0.149] | loses most | 0.267 [0.211, 0.322] | loses most |
| oracle | forward, one weight | H=8 (0.27 LT) | | 0.0168 [-0.000682, 0.0344] | loses most | | |
| oracle | forward, one weight | H=15 (0.50 LT) | | 0.0318 [0.0143, 0.0491] | loses most | | |
| oracle | forward, one weight | H=30 (1.00 LT) | | 0.00604 [-0.00569, 0.0183] | loses most | | |
| oracle | forward, one weight | H=60 (2.00 LT) | | 0.00578 [-0.00604, 0.0175] | loses most | | |
| oracle | forward, one weight | H=120 (4.00 LT) | | 0.0838 [0.0532, 0.118] | loses most | | |
| oracle | reverse | H=8 (0.27 LT) | 0.0104 [0.00804, 0.0133] | 0.232 [0.0147, 0.551] | not determined (n_eff < 50) | 0.155 [0.122, 0.188] | loses most |
| oracle | reverse | H=15 (0.50 LT) | 0.0262 [0.0215, 0.0316] | 0.318 [0.17, 0.452] | not determined (n_eff < 50) | 0.196 [0.164, 0.226] | loses most |
| oracle | reverse | H=30 (1.00 LT) | 0.0249 [0.0197, 0.0307] | 0.447 [0.208, 0.649] | not determined (n_eff < 50) | 0.228 [0.191, 0.266] | loses most |
| oracle | reverse | H=60 (2.00 LT) | 0.0199 [0.0126, 0.0277] | 0.316 [0.187, 0.473] | loses most | 0.167 [0.12, 0.211] | loses most |
| oracle | reverse | H=120 (4.00 LT) | 0.0121 [0.00513, 0.0187] | 0.495 [0.27, 1.09] | not determined (interval spans 0.5) | 0.115 [0.0455, 0.189] | loses most |
| deployable | forward (g; g_w) | all five | 0.0385 [0.0339, 0.043] | 0.182 [0.151, 0.214] | loses most | 0.242 [0.205, 0.281] | loses most |
| deployable | forward, one weight | H=8 (0.27 LT) | | 0.0702 [0.0534, 0.0881] | loses most | | |
| deployable | forward, one weight | H=15 (0.50 LT) | | 0.0792 [0.0599, 0.1] | loses most | | |
| deployable | forward, one weight | H=30 (1.00 LT) | | 0.138 [0.112, 0.165] | loses most | | |
| deployable | forward, one weight | H=60 (2.00 LT) | | 0.03 [0.0138, 0.0458] | loses most | | |
| deployable | forward, one weight | H=120 (4.00 LT) | | 0.0972 [0.0677, 0.127] | loses most | | |
| deployable | reverse | H=8 (0.27 LT) | 0.00236 [-0.000756, 0.00496] | 0.728 [-, -] | not determined (full-profile skill not established) | 0.336 [0.263, 0.409] | loses most |
| deployable | reverse | H=15 (0.50 LT) | 0.0134 [0.00786, 0.0193] | 0.558 [0.343, 0.846] | not determined (n_eff < 50) | 0.314 [0.255, 0.373] | loses most |
| deployable | reverse | H=30 (1.00 LT) | 0.0114 [0.00519, 0.0176] | 0.568 [0.21, 0.857] | not determined (n_eff < 50) | 0.39 [0.313, 0.466] | loses most |
| deployable | reverse | H=60 (2.00 LT) | 0.0113 [0.00401, 0.0192] | 0.43 [0.00757, 0.689] | not determined (interval spans 0.5) | 0.322 [0.245, 0.402] | loses most |
| deployable | reverse | H=120 (4.00 LT) | 0.00516 [0.00145, 0.00874] | 1.08 [0.57, 2.52] | keeps most | 0.413 [0.223, 0.614] | not determined (interval spans 0.5) |

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| profile | forward C-index F / g / g_w | reverse MSE(h)/MSE(F) per horizon | math-spec prediction (both lose most) | largest single-weight retention at H |
|---|---|---|---|---|
| oracle | 0.679 / 0.583 / 0.603 | H=8 (0.27 LT) 2.75 [1.53, 6.64] undetermined (n_eff < 50); H=15 (0.50 LT) 2.81 [2.25, 3.62] undetermined (n_eff < 50); H=30 (1.00 LT) 1.45 [1.24, 1.73] undetermined (n_eff < 50); H=60 (2.00 LT) 1.09 [1.05, 1.14] needed, size not determined; H=120 (4.00 LT) 1.01 [0.999, 1.01] negligible | **consistent** | 120 |
| deployable | 0.678 / 0.606 / 0.61 | H=8 (0.27 LT) 1.05 [0.818, 1.3] undetermined (n_eff < 50); H=15 (0.50 LT) 1.25 [1.05, 1.51] undetermined (n_eff < 50); H=30 (1.00 LT) 1.11 [1.02, 1.22] undetermined (n_eff < 50); H=60 (2.00 LT) 1.04 [1.01, 1.07] needed, size not determined; H=120 (4.00 LT) 1 [0.996, 1] negligible | **not consistent** | 30 |

Oracle against deployable: retained (deployable) minus retained (oracle), paired 95% interval.

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| row | oracle | deployable | difference [CI] | reading |
|---|---|---|---|---|
| forward | 0.115 | 0.182 | 0.0669 [0.0371, 0.0972] | deployable retains more |
| forward_w | 0.267 | 0.242 | -0.0245 [-0.0865, 0.0359] | no difference detected |
| reverse/8 | 0.232 | 0.728 | 0.495 [-, -] | not determined (n_eff < 50) |
| reverse_w/8 | 0.155 | 0.336 | 0.181 [0.114, 0.251] | deployable retains more |
| reverse/15 | 0.318 | 0.558 | 0.24 [0.0189, 0.533] | not determined (n_eff < 50) |
| reverse_w/15 | 0.196 | 0.314 | 0.118 [0.0637, 0.176] | deployable retains more |
| reverse/30 | 0.447 | 0.568 | 0.121 [-0.208, 0.46] | not determined (n_eff < 50) |
| reverse_w/30 | 0.228 | 0.39 | 0.162 [0.0909, 0.236] | deployable retains more |
| reverse/60 | 0.316 | 0.43 | 0.113 [-0.347, 0.405] | no difference detected |
| reverse_w/60 | 0.167 | 0.322 | 0.156 [0.0786, 0.237] | deployable retains more |
| reverse/120 | 0.495 | 1.08 | 0.584 [-0.144, 2.07] | no difference detected |
| reverse_w/120 | 0.115 | 0.413 | 0.298 [0.109, 0.486] | deployable retains more |

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| horizon | Spearman(phi allocation, phi horizon) (4 items, descriptive) | phi_alloc R/O/I/N | phi_horizon R/O/I/N |
|---|---|---|---|
| H=8 (0.27 LT) | 0.6 | -0.00032/0.0077/0.0031/-0.0001 | 0.0017/0.0078/0.029/0.0015 |
| H=15 (0.50 LT) | 0.6 | 0.0023/0.016/0.005/0.0027 | 0.0017/0.0078/0.029/0.0015 |
| H=30 (1.00 LT) | 0.6 | 0.00027/0.016/0.007/0.0014 | 0.0017/0.0078/0.029/0.0015 |
| H=60 (2.00 LT) | 0.4 | 0.0033/0.014/0.0027/-5.5e-05 | 0.0017/0.0078/0.029/0.0015 |
| H=120 (4.00 LT) | 0.8 | 0.0036/0.0045/0.0042/-0.00024 | 0.0017/0.0078/0.029/0.0015 |

### C3. The deployable chain

False trust = P(T <= q_0.1) per (state, draw), target 0.1; T realized (the run's first passage against the noisy truth) or characteristic (moments). Trusted horizon = mean q_0.1 (LT). A4 + KM leaf uses the calibration A4 hybrid's characteristic horizon (no per-draw calibration errors on the full grid).

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| policy | false trust realized [CI] | false trust characteristic [CI] | mean trusted (LT) [CI] | q at cap |
|---|---|---|---|---|
| A2 + constant | 0.0714 [0.0654, 0.0779] | 0.103 [0.0948, 0.111] | 0.556 [0.556, 0.556] | 0 |
| A2 + h(F-hat) | 0.11 [0.103, 0.117] | 0.137 [0.128, 0.147] | 1.07 [1.06, 1.08] | 0 |
| A4 + KM leaf | 0.0729 [0.0676, 0.0786] | 0.12 [0.112, 0.129] | 0.965 [0.954, 0.976] | 0 |
| g(F-hat) + h(F-hat) | 0.116 [0.108, 0.123] | 0.14 [0.13, 0.149] | 1.15 [1.13, 1.16] | 0 |

Hybrid MSE ratio to A2 (realized per draw; 1.05 table, R2 guard).

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| policy | H=8 (0.27 LT) | H=15 (0.50 LT) | H=30 (1.00 LT) | H=60 (2.00 LT) | H=120 (4.00 LT) |
|---|---|---|---|---|---|
| A4 + KM leaf | 2.28 [1.65, 3.02] substantial | 1.26 [1.14, 1.37] substantial | 1.16 [1.11, 1.22] substantial | 1.03 [1.01, 1.05] small | 1.06 [1.05, 1.07] needed, size not determined |
| g(F-hat) + h(F-hat) | 0.849 [0.67, 1.05] undetermined | 0.641 [0.506, 0.786] lowers | 0.787 [0.678, 0.901] lowers | 0.935 [0.892, 0.977] lowers | 0.994 [0.99, 0.998] lowers |

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| full system minus | false trust realized [CI] | false trust characteristic [CI] | trusted LT [CI] |
|---|---|---|---|
| A2 + constant | 0.0441 [0.0367, 0.0512] | 0.0369 [0.0277, 0.0459] | 0.591 [0.578, 0.604] |
| A2 + h(F-hat) | 0.00581 [0.000561, 0.0111] | 0.00263 [-0.00538, 0.0101] | 0.0771 [0.0681, 0.086] |
| A4 + KM leaf | 0.0426 [0.0361, 0.0493] | 0.0197 [0.0104, 0.0293] | 0.182 [0.168, 0.196] |

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| horizon model (own characteristic target) | pinball / constant's | constant/model ratio [CI] reading | cov 0.1 / 0.5 / 0.9 | C |
|---|---|---|---|---|
| h_A2(F-hat) | 0.209 / 0.268 | 1.29 [1.25, 1.33] substantial | 0.137 / 0.517 / 0.869 | 0.674 |
| h_g(F-hat) | 0.196 / 0.239 | 1.22 [1.19, 1.26] substantial | 0.14 / 0.511 / 0.867 | - |

### E-H2a. Amplification mismatch m(H) (H_0 = 1 LT; both r.m.s. <= 0.5 sigma_x)

Medians by tercile of I (low / mid / high). Spearman(m, I) on the kept states [95%]. B and A columns from the A/D record (oracle).

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| horizon | kept | m | abs drift w* | corr C/sqrt(E_C E_P) | Spearman(m, I) | B RI / OI | A drop-I (MSE) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 3556 | -0.064 / 0.047 / 0.2 | 0.052 / 0.036 / 0.067 | 0.1 / 0.13 / 0.14 | 0.0809 [0.0479, 0.113] | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=15 (0.50 LT) | 3517 | 0.056 / 0.059 / 0.082 | 0.054 / 0.046 / 0.068 | 0.11 / 0.14 / 0.15 | 0.0216 [-0.0115, 0.0527] | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=30 (1.00 LT) | 3588 | 0 / 0 / 0 | 0 / 0 / 0 | 0.12 / 0.16 / 0.19 | (H_0) | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=60 (2.00 LT) | 2749 | -0.034 / -0.035 / -0.14 | 0.064 / 0.087 / 0.084 | 0.14 / 0.19 / 0.19 | -0.026 [-0.0627, 0.011] | no interaction gain detected / no interaction gain detected | negligible |
| H=120 (4.00 LT) | 701 | -1.4 / -2.3 / -2.5 | 0.27 / 0.41 / 0.47 | 0.24 / 0.32 / 0.32 | -0.176 [-0.245, -0.106] | no interaction gain detected / interaction gain detected | negligible |

**Reading: consistent** (horizons_used: ['60', '120'], horizons_supporting: ['120'], horizons_null: ['60']).

### E-H2e. Library size and error correlation (sweep states)

1000 sweep states. Delta = value at N_lib 100000 minus 1000. corr = the H2e correlation (0 by convention where an error is constant over the draws).

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| rho | valid | corr 0 small / large lib | median corr small -> large | set | median Delta corr [CI] | Spearman(Delta corr, Delta R) [CI] | reading |
|---|---|---|---|---|---|---|---|
| 0.01 | 1000 | 689 / 17 | 0 -> 0.435 | all (1000) | 0.353 [0.329, 0.372] | 0.2 [0.142, 0.252] | not consistent |
| 0.01 | 1000 | 689 / 17 | 0 -> 0.435 | both_defined (308) | 0.163 [0.117, 0.209] | 0.129 [0.0197, 0.238] | not consistent |
| 0.02 | 1000 | 441 / 1 | 0 -> 0.449 | all (1000) | 0.287 [0.254, 0.311] | 0.195 [0.138, 0.253] | not consistent |
| 0.02 | 1000 | 441 / 1 | 0 -> 0.449 | both_defined (559) | 0.195 [0.16, 0.222] | 0.173 [0.0967, 0.247] | not consistent |

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| rho | stratifier | median Delta corr low / mid / high | median Delta R low / mid / high |
|---|---|---|---|
| 0.01 | R | 0.36 / 0.37 / 0.32 | -1.6 / -1.5 / -1.6 |
| 0.01 | O | 0.35 / 0.38 / 0.29 | -1.5 / -1.5 / -1.6 |
| 0.01 | I | 0.35 / 0.38 / 0.33 | -1.6 / -1.6 / -1.5 |
| 0.01 | N | 0.3 / 0.4 / 0.35 | -1.7 / -1.5 / -1.6 |
| 0.01 | delta_R | 0.26 / 0.37 / 0.41 | -2.3 / -1.6 / -0.64 |
| 0.02 | R | 0.33 / 0.27 / 0.24 | -1 / -0.98 / -1.1 |
| 0.02 | O | 0.33 / 0.3 / 0.2 | -0.97 / -1 / -1.1 |
| 0.02 | I | 0.29 / 0.28 / 0.28 | -1.1 / -1 / -0.91 |
| 0.02 | N | 0.24 / 0.3 / 0.3 | -1.1 / -0.92 / -1 |
| 0.02 | delta_R | 0.22 / 0.24 / 0.37 | -1.7 / -1 / -0.23 |

**Reading** (final, after the convention check): rho 0.01: not consistent; rho 0.02: not consistent.

### E-H3c. A5 against A4

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| item | value |
|---|---|
| H3c ratio MSE(A5)/MSE(A4) [CI at level 0.983] (run) | 0.767 [0.655, 0.896], width 0.242 |
| top-1% share: A5 loss / A4 loss / abs(A5 - A4) | 0.577 / 0.567 / 0.627 |
| autocorrelation of d = A5 - A4, lags 1..5 | -0.00057, 0.00052, 0.017, -0.00091, -0.0028 |
| block-5 means: lag-1 autocorrelation, variance ratio | 0.0172, 0.997 |
| K chosen; leaves used test / calibration; largest leaf share test | 5; 5 / 5; 0.413 |
| w*(H_ref) within-leaf share of variance | 0.877 |
| bimodality coefficient R/O/I/N, oracle; deployable | 0.21/0.8/0.54/0.83; 0.32/0.4/0.53/0.9 |
| Spearman pairs (oracle) | RO 0.51, RI -0.046, RN 0.29, OI -0.022, ON -0.06, IN 0.067 |
| top-1% abs(d) states: mean percentile R/O/I/N | 0.78/0.89/0.29/0.21 |
| top-1% abs(d) states: median I pct; share high-I; median abs(x) pct; share sign change in window; share of sum d | 0.22; 0.075; 0.265; 0.875; 0.772 |

## rossler

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| check | result |
|---|---|
| A2 rebuilt on 1..H_max equals the dumped A2 (bitwise); A4 horizon-free | True, True |
| refit reproduces WU-0048 (max abs: A/ROIN MSE oracle, deployable; W/ROIN L_w oracle, deployable) | 0 / 0 / 0 / 0 |
| T_c counts T = 1 / e_(T-1) = theta (A2 train, g train, A2 test, g test, A4 calibration) | 0/0, 0/0, 0/0, 0/0, 0/0 |
| A2 on 1..H_max: pooled curvature floor / columns at 0 or 1 | 0 / 0 |
| weights clipped to [0, 1] | g_oracle_test 3116, g_oracle_train_oof 2391, gw_oracle_test 2003, gw_oracle_train_oof 1519, g_deployable_test 10604, g_deployable_train_oof 7873, gw_deployable_test 1637, gw_deployable_train_oof 1307 |

### C1. Separate performance (from the A/D record, no refit)

Allocation: MSE per rule (oracle: moment form; deployable: realized); reading of the rung against F (MSE ratio, 1.05 table, n_eff guard). G(F) = 1 - L_A(F)/L_A(constant).

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| horizon | profile | constant | separation | RO | F (ROIN) | X | X+F | G(F) | sep vs F | RO vs F | X+F vs F |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 0.000133 | 0.000124 | 0.000117 | 0.000116 | 0.000129 | 0.000116 | 0.607 | substantial | small | lowers |
| H=8 (0.27 LT) | deployable | 0.000126 | 0.000138 | 0.000127 | 0.000127 | 0.000126 | 0.000126 | -0.0577 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | oracle | 0.000238 | 0.000212 | 0.000202 | 0.0002 | 0.000228 | 0.0002 | 0.688 | needed, size not determined | small | negligible |
| H=15 (0.50 LT) | deployable | 0.000227 | 0.000243 | 0.000228 | 0.000228 | 0.000226 | 0.000226 | -0.0372 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | oracle | 0.000787 | 0.000698 | 0.000677 | 0.000672 | 0.000778 | 0.00067 | 0.695 | small | small | negligible |
| H=30 (1.00 LT) | deployable | 0.00077 | 0.000792 | 0.000763 | 0.00076 | 0.000762 | 0.000755 | 0.0706 | needed, size not determined | negligible | negligible |
| H=60 (2.00 LT) | oracle | 0.0128 | 0.0112 | 0.0113 | 0.0114 | 0.0128 | 0.0114 | 0.398 | negligible | negligible | negligible |
| H=60 (2.00 LT) | deployable | 0.0129 | 0.013 | 0.0129 | 0.0129 | 0.0129 | 0.0129 | 0.00571 | negligible | negligible | negligible |
| H=120 (4.00 LT) | oracle | 0.11 | 0.113 | 0.108 | 0.108 | 0.11 | 0.107 | 0.0785 | needed, size not determined | negligible | lowers |
| H=120 (4.00 LT) | deployable | 0.11 | 0.115 | 0.109 | 0.108 | 0.109 | 0.108 | 0.05 | needed, size not determined | small | lowers |

Horizon (Y = ln min(T_c, H_max)): pinball at 0.5 / Harrell's C / coverage of q_0.1 below the cap; reading against F.

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | C | cov q_0.1 | reading vs F |
|---|---|---|---|---|---|
| oracle | none | 0.16 | 0.5 | 0.099 | substantial |
| oracle | lyapunov | 0.165 | 0.64 | 0.08 | substantial |
| oracle | RO | 0.154 | 0.559 | 0.111 | substantial |
| oracle | ROIN | 0.121 | 0.681 | 0.141 |  |
| oracle | X | 0.124 | 0.693 | 0.148 | undetermined |
| oracle | X+F | 0.094 | 0.765 | 0.162 | lowers |
| oracle | Lyapunov rank | | 0.637 | | |
| deployable | none | 0.16 | 0.5 | 0.099 | substantial |
| deployable | lyapunov | 0.167 | 0.634 | 0.0703 | substantial |
| deployable | RO | 0.145 | 0.603 | 0.113 | substantial |
| deployable | ROIN | 0.117 | 0.693 | 0.134 |  |
| deployable | X | 0.126 | 0.689 | 0.141 | needed, size not determined |
| deployable | X+F | 0.0917 | 0.77 | 0.15 | lowers |
| deployable | Lyapunov rank | | 0.631 | | |

### C2. Shared information (oracle and deployable profiles)

Skill retained = [L(constant) - L(bottleneck)] / [L(constant) - L(F)]; reading: keeps most (CI > 0.5), loses most (CI < 0.5), else not determined. Forward: horizon from g (five clipped weights; g_w: the L_w fits); reverse: weight from h (three quantiles), scored by L_A (MSE; deployable: realized per draw, R2 guard) and by L_w (weight units, unit-weight fits). Training inputs cross-fitted.

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| profile | direction | horizon | full skill [CI] | retained L_A / pinball [CI] | reading | retained L_w [CI] | reading L_w |
|---|---|---|---|---|---|---|---|
| oracle | forward (g; g_w) | all five | 0.039 [0.0355, 0.0424] | 0.406 [0.352, 0.456] | loses most | 0.454 [0.402, 0.501] | not determined (interval spans 0.5) |
| oracle | forward, one weight | H=8 (0.27 LT) | | -0.00114 [-0.0287, 0.0283] | loses most | | |
| oracle | forward, one weight | H=15 (0.50 LT) | | -0.00637 [-0.0378, 0.0252] | loses most | | |
| oracle | forward, one weight | H=30 (1.00 LT) | | 0.0218 [-0.00562, 0.0488] | loses most | | |
| oracle | forward, one weight | H=60 (2.00 LT) | | 0.079 [0.0474, 0.108] | loses most | | |
| oracle | forward, one weight | H=120 (4.00 LT) | | 0.338 [0.284, 0.389] | loses most | | |
| oracle | reverse | H=8 (0.27 LT) | 1.72e-05 [9.81e-06, 2.86e-05] | 0.178 [0.0979, 0.242] | loses most | 0.375 [0.323, 0.426] | loses most |
| oracle | reverse | H=15 (0.50 LT) | 3.72e-05 [2.4e-05, 5.72e-05] | 0.124 [0.0957, 0.169] | loses most | 0.373 [0.323, 0.425] | loses most |
| oracle | reverse | H=30 (1.00 LT) | 0.000115 [0.000101, 0.000131] | 0.211 [0.134, 0.282] | loses most | 0.357 [0.306, 0.405] | loses most |
| oracle | reverse | H=60 (2.00 LT) | 0.00148 [0.00118, 0.00175] | 0.128 [0.0245, 0.219] | loses most | 0.354 [0.307, 0.401] | loses most |
| oracle | reverse | H=120 (4.00 LT) | 0.00244 [0.00176, 0.0031] | 0.221 [-0.0277, 0.422] | loses most | 0.454 [0.356, 0.556] | not determined (interval spans 0.5) |
| deployable | forward (g; g_w) | all five | 0.0426 [0.0392, 0.0462] | 0.475 [0.426, 0.522] | not determined (interval spans 0.5) | 0.565 [0.526, 0.604] | keeps most |
| deployable | forward, one weight | H=8 (0.27 LT) | | 0.0523 [0.0268, 0.0779] | loses most | | |
| deployable | forward, one weight | H=15 (0.50 LT) | | 0.049 [0.0299, 0.0684] | loses most | | |
| deployable | forward, one weight | H=30 (1.00 LT) | | 0.0711 [0.0488, 0.0923] | loses most | | |
| deployable | forward, one weight | H=60 (2.00 LT) | | 0.171 [0.137, 0.202] | loses most | | |
| deployable | forward, one weight | H=120 (4.00 LT) | | 0.418 [0.366, 0.463] | loses most | | |
| deployable | reverse | H=8 (0.27 LT) | -1.21e-06 [-2.4e-06, 4.61e-08] | - [-, -] | not determined (full-profile skill not established) | 0.0447 [-0.0159, 0.108] | loses most |
| deployable | reverse | H=15 (0.50 LT) | -1.61e-06 [-4.28e-06, 8.49e-07] | - [-, -] | not determined (full-profile skill not established) | 0.088 [0.0606, 0.116] | loses most |
| deployable | reverse | H=30 (1.00 LT) | 1.05e-05 [1.88e-06, 2e-05] | -0.0807 [-0.811, 0.126] | loses most | 0.115 [0.0729, 0.157] | loses most |
| deployable | reverse | H=60 (2.00 LT) | 2.18e-05 [-0.000214, 0.000268] | 2.6 [-, -] | not determined (full-profile skill not established) | 0.18 [0.0893, 0.263] | loses most |
| deployable | reverse | H=120 (4.00 LT) | 0.00154 [0.000989, 0.00206] | 0.948 [0.681, 1.33] | keeps most | 0.641 [0.489, 0.801] | not determined (interval spans 0.5) |

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| profile | forward C-index F / g / g_w | reverse MSE(h)/MSE(F) per horizon | math-spec prediction (both lose most) | largest single-weight retention at H |
|---|---|---|---|---|
| oracle | 0.681 / 0.597 / 0.618 | H=8 (0.27 LT) 1.12 [1.07, 1.21] substantial; H=15 (0.50 LT) 1.16 [1.1, 1.26] substantial; H=30 (1.00 LT) 1.13 [1.12, 1.16] substantial; H=60 (2.00 LT) 1.11 [1.09, 1.14] substantial; H=120 (4.00 LT) 1.02 [1.01, 1.02] small | **consistent** | 120 |
| deployable | 0.693 / 0.616 / 0.639 | H=8 (0.27 LT) 0.991 [0.981, 1] undetermined (n_eff < 50); H=15 (0.50 LT) 0.992 [0.981, 1] undetermined (n_eff < 50); H=30 (1.00 LT) 1.01 [1, 1.03] small; H=60 (2.00 LT) 0.997 [0.982, 1.01] negligible; H=120 (4.00 LT) 1 [0.996, 1.01] negligible | **not consistent** | 120 |

Oracle against deployable: retained (deployable) minus retained (oracle), paired 95% interval.

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| row | oracle | deployable | difference [CI] | reading |
|---|---|---|---|---|
| forward | 0.406 | 0.475 | 0.0691 [0.0208, 0.119] | deployable retains more |
| forward_w | 0.454 | 0.565 | 0.112 [0.0637, 0.161] | deployable retains more |
| reverse/8 | 0.178 | - | - [-, -] | not determined (full-profile skill not established) |
| reverse_w/8 | 0.375 | 0.0447 | -0.33 [-0.398, -0.257] | deployable retains less |
| reverse/15 | 0.124 | - | - [-, -] | not determined (full-profile skill not established) |
| reverse_w/15 | 0.373 | 0.088 | -0.285 [-0.339, -0.229] | deployable retains less |
| reverse/30 | 0.211 | -0.0807 | -0.291 [-1.02, -0.0857] | deployable retains less |
| reverse_w/30 | 0.357 | 0.115 | -0.242 [-0.297, -0.185] | deployable retains less |
| reverse/60 | 0.128 | 2.6 | 2.47 [-, -] | not determined (full-profile skill not established) |
| reverse_w/60 | 0.354 | 0.18 | -0.174 [-0.268, -0.0862] | deployable retains less |
| reverse/120 | 0.221 | 0.948 | 0.727 [0.428, 1.17] | deployable retains more |
| reverse_w/120 | 0.454 | 0.641 | 0.188 [0.0455, 0.332] | deployable retains more |

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| horizon | Spearman(phi allocation, phi horizon) (4 items, descriptive) | phi_alloc R/O/I/N | phi_horizon R/O/I/N |
|---|---|---|---|
| H=8 (0.27 LT) | -0.8 | 1.2e-05/3e-06/7.2e-08/2e-06 | 0.0016/0.0082/0.027/0.0022 |
| H=15 (0.50 LT) | -0.8 | 2.6e-05/6.6e-06/-2.2e-07/4.3e-06 | 0.0016/0.0082/0.027/0.0022 |
| H=30 (1.00 LT) | -0.8 | 7.8e-05/1.8e-05/1.2e-06/1.7e-05 | 0.0016/0.0082/0.027/0.0022 |
| H=60 (2.00 LT) | -1 | 0.0012/0.00013/-4.2e-05/0.00016 | 0.0016/0.0082/0.027/0.0022 |
| H=120 (4.00 LT) | -0.2 | 0.0013/0.00043/0.00064/4.6e-05 | 0.0016/0.0082/0.027/0.0022 |

### C3. The deployable chain

False trust = P(T <= q_0.1) per (state, draw), target 0.1; T realized (the run's first passage against the noisy truth) or characteristic (moments). Trusted horizon = mean q_0.1 (LT). A4 + KM leaf uses the calibration A4 hybrid's characteristic horizon (no per-draw calibration errors on the full grid).

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| policy | false trust realized [CI] | false trust characteristic [CI] | mean trusted (LT) [CI] | q at cap |
|---|---|---|---|---|
| A2 + constant | 0.0932 [0.087, 0.0999] | 0.1 [0.091, 0.11] | 1.87 [1.87, 1.87] | 0 |
| A2 + h(F-hat) | 0.138 [0.131, 0.145] | 0.132 [0.123, 0.142] | 2.23 [2.22, 2.25] | 0 |
| A4 + KM leaf | 0.107 [0.101, 0.114] | 0.109 [0.1, 0.118] | 2.01 [2, 2.02] | 0 |
| g(F-hat) + h(F-hat) | 0.139 [0.133, 0.146] | 0.127 [0.118, 0.136] | 2.28 [2.26, 2.3] | 0 |

Hybrid MSE ratio to A2 (realized per draw; 1.05 table, R2 guard).

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| policy | H=8 (0.27 LT) | H=15 (0.50 LT) | H=30 (1.00 LT) | H=60 (2.00 LT) | H=120 (4.00 LT) |
|---|---|---|---|---|---|
| A4 + KM leaf | 1.09 [1.08, 1.11] undetermined (n_eff < 50) | 1.07 [1.05, 1.09] undetermined (n_eff < 50) | 1.03 [1, 1.05] needed, size not determined | 1.01 [0.987, 1.02] negligible | 1.05 [1.03, 1.06] needed, size not determined |
| g(F-hat) + h(F-hat) | 1.01 [0.999, 1.02] undetermined (n_eff < 50) | 1.01 [0.996, 1.02] undetermined (n_eff < 50) | 0.985 [0.974, 0.997] lowers | 1 [0.98, 1.02] negligible | 0.986 [0.981, 0.991] lowers |

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| full system minus | false trust realized [CI] | false trust characteristic [CI] | trusted LT [CI] |
|---|---|---|---|
| A2 + constant | 0.0459 [0.0396, 0.052] | 0.0269 [0.016, 0.0374] | 0.409 [0.389, 0.43] |
| A2 + h(F-hat) | 0.00125 [-0.0025, 0.00531] | -0.00544 [-0.0119, 0.000627] | 0.0407 [0.0368, 0.0452] |
| A4 + KM leaf | 0.0319 [0.0262, 0.0376] | 0.018 [0.008, 0.0278] | 0.269 [0.255, 0.282] |

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| horizon model (own characteristic target) | pinball / constant's | constant/model ratio [CI] reading | cov 0.1 / 0.5 / 0.9 | C |
|---|---|---|---|---|
| h_A2(F-hat) | 0.102 / 0.15 | 1.47 [1.44, 1.52] substantial | 0.132 / 0.511 / 0.875 | 0.713 |
| h_g(F-hat) | 0.101 / 0.153 | 1.52 [1.48, 1.56] substantial | 0.127 / 0.505 / 0.873 | - |

### E-H2a. Amplification mismatch m(H) (H_0 = 1 LT; both r.m.s. <= 0.5 sigma_x)

Medians by tercile of I (low / mid / high). Spearman(m, I) on the kept states [95%]. B and A columns from the A/D record (oracle).

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| horizon | kept | m | abs drift w* | corr C/sqrt(E_C E_P) | Spearman(m, I) | B RI / OI | A drop-I (MSE) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 3994 | -0.089 / 0.18 / 0.07 | 0.074 / 0.077 / 0.076 | 0.2 / 0.19 / 0.18 | 0.0577 [0.0263, 0.0896] | no interaction gain detected / no interaction gain detected | negligible |
| H=15 (0.50 LT) | 3994 | -0.17 / 0.14 / 0.065 | 0.077 / 0.076 / 0.05 | 0.19 / 0.19 / 0.19 | 0.0832 [0.0513, 0.116] | no interaction gain detected / no interaction gain detected | negligible |
| H=30 (1.00 LT) | 3994 | 0 / 0 / 0 | 0 / 0 / 0 | 0.21 / 0.22 / 0.23 | (H_0) | no interaction gain detected / no interaction gain detected | negligible |
| H=60 (2.00 LT) | 3684 | -0.24 / -0.16 / -0.34 | 0.085 / 0.09 / 0.11 | 0.23 / 0.27 / 0.29 | -0.0386 [-0.0714, -0.007] | no interaction gain detected / no interaction gain detected | negligible |
| H=120 (4.00 LT) | 2802 | -1.3 / -1.5 / -1.4 | 0.23 / 0.32 / 0.3 | 0.35 / 0.38 / 0.36 | -0.0158 [-0.0527, 0.0227] | no interaction gain detected / no interaction gain detected | small |

**Reading: not consistent** (horizons_used: ['60', '120'], horizons_supporting: [], horizons_null: ['60', '120']).

### E-H2e. Library size and error correlation (sweep states)

1000 sweep states. Delta = value at N_lib 100000 minus 1000. corr = the H2e correlation (0 by convention where an error is constant over the draws).

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| rho | valid | corr 0 small / large lib | median corr small -> large | set | median Delta corr [CI] | Spearman(Delta corr, Delta R) [CI] | reading |
|---|---|---|---|---|---|---|---|
| 0.01 | 1000 | 586 / 1 | 0 -> 0.446 | all (1000) | 0.357 [0.341, 0.382] | 0.149 [0.0905, 0.213] | not consistent |
| 0.01 | 1000 | 586 / 1 | 0 -> 0.446 | both_defined (414) | 0.22 [0.195, 0.258] | 0.104 [0.0117, 0.201] | not consistent |
| 0.02 | 1000 | 286 / 0 | 0.0988 -> 0.456 | all (1000) | 0.291 [0.269, 0.313] | 0.167 [0.109, 0.23] | not consistent |
| 0.02 | 1000 | 286 / 0 | 0.0988 -> 0.456 | both_defined (714) | 0.206 [0.18, 0.238] | 0.144 [0.0748, 0.211] | not consistent |

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| rho | stratifier | median Delta corr low / mid / high | median Delta R low / mid / high |
|---|---|---|---|
| 0.01 | R | 0.32 / 0.39 / 0.38 | -1.3 / -1.1 / -1.4 |
| 0.01 | O | 0.39 / 0.35 / 0.33 | -1.3 / -1.2 / -1.3 |
| 0.01 | I | 0.33 / 0.34 / 0.4 | -1.4 / -1.3 / -1.2 |
| 0.01 | N | 0.34 / 0.36 / 0.37 | -1.5 / -1.1 / -1.3 |
| 0.01 | delta_R | 0.31 / 0.37 / 0.4 | -2 / -1.3 / -0.44 |
| 0.02 | R | 0.24 / 0.26 / 0.37 | -0.74 / -0.69 / -0.87 |
| 0.02 | O | 0.3 / 0.27 / 0.3 | -0.8 / -0.71 / -0.81 |
| 0.02 | I | 0.26 / 0.28 / 0.34 | -0.83 / -0.79 / -0.7 |
| 0.02 | N | 0.29 / 0.26 / 0.32 | -0.94 / -0.61 / -0.74 |
| 0.02 | delta_R | 0.21 / 0.29 / 0.35 | -1.4 / -0.76 / -0.012 |

**Reading** (final, after the convention check): rho 0.01: not consistent; rho 0.02: not consistent.

### E-H3c. A5 against A4

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| item | value |
|---|---|
| H3c ratio MSE(A5)/MSE(A4) [CI at level 0.983] (run) | 0.969 [0.946, 0.994], width 0.048 |
| top-1% share: A5 loss / A4 loss / abs(A5 - A4) | 0.165 / 0.164 / 0.184 |
| autocorrelation of d = A5 - A4, lags 1..5 | 0.0036, -0.0047, 0.0099, 0.0009, -0.0085 |
| block-5 means: lag-1 autocorrelation, variance ratio | -0.0175, 1.04 |
| K chosen; leaves used test / calibration; largest leaf share test | 3; 3 / 3; 0.456 |
| w*(H_ref) within-leaf share of variance | 0.946 |
| bimodality coefficient R/O/I/N, oracle; deployable | 0.25/0.78/0.5/0.82; 0.48/0.79/0.5/0.9 |
| Spearman pairs (oracle) | RO 0.37, RI -0.058, RN 0.37, OI -0.043, ON -0.012, IN -0.04 |
| top-1% abs(d) states: mean percentile R/O/I/N | 0.69/0.84/0.75/0.47 |
| top-1% abs(d) states: median I pct; share high-I; median abs(x) pct; share sign change in window; share of sum d | 0.851; 0.725; 0.386; 1; 0.401 |

## chua

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| check | result |
|---|---|
| A2 rebuilt on 1..H_max equals the dumped A2 (bitwise); A4 horizon-free | True, True |
| refit reproduces WU-0048 (max abs: A/ROIN MSE oracle, deployable; W/ROIN L_w oracle, deployable) | 0 / 0 / 0 / 0 |
| T_c counts T = 1 / e_(T-1) = theta (A2 train, g train, A2 test, g test, A4 calibration) | 7/0, 24/0, 5/0, 20/0, 8/0 |
| A2 on 1..H_max: pooled curvature floor / columns at 0 or 1 | 0 / 0 |
| weights clipped to [0, 1] | g_oracle_test 2086, g_oracle_train_oof 1726, gw_oracle_test 1524, gw_oracle_train_oof 1331, g_deployable_test 7351, g_deployable_train_oof 5837, gw_deployable_test 732, gw_deployable_train_oof 780 |

### C1. Separate performance (from the A/D record, no refit)

Allocation: MSE per rule (oracle: moment form; deployable: realized); reading of the rung against F (MSE ratio, 1.05 table, n_eff guard). G(F) = 1 - L_A(F)/L_A(constant).

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| horizon | profile | constant | separation | RO | F (ROIN) | X | X+F | G(F) | sep vs F | RO vs F | X+F vs F |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 0.00104 | 0.000731 | 0.00097 | 0.000691 | 0.00103 | 0.000866 | 0.624 | undetermined | undetermined | undetermined |
| H=8 (0.27 LT) | deployable | 0.00113 | 0.00121 | 0.00117 | 0.00141 | 0.00111 | 0.00116 | -0.443 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | oracle | 0.00304 | 0.00237 | 0.00255 | 0.00269 | 0.00282 | 0.00246 | 0.288 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | deployable | 0.00332 | 0.00353 | 0.00345 | 0.00352 | 0.00331 | 0.0033 | -0.129 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | oracle | 0.0191 | 0.017 | 0.019 | 0.0183 | 0.0187 | 0.0182 | 0.128 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | deployable | 0.0221 | 0.0218 | 0.0219 | 0.0217 | 0.0217 | 0.0215 | 0.0539 | undetermined | undetermined | undetermined |
| H=60 (2.00 LT) | oracle | 0.184 | 0.178 | 0.175 | 0.175 | 0.182 | 0.175 | 0.148 | negligible | negligible | negligible |
| H=60 (2.00 LT) | deployable | 0.179 | 0.178 | 0.174 | 0.175 | 0.177 | 0.175 | 0.0693 | undetermined | negligible | negligible |
| H=120 (4.00 LT) | oracle | 0.617 | 0.633 | 0.604 | 0.604 | 0.618 | 0.605 | 0.0753 | needed, size not determined | negligible | negligible |
| H=120 (4.00 LT) | deployable | 0.614 | 0.637 | 0.608 | 0.607 | 0.614 | 0.607 | 0.0374 | needed, size not determined | negligible | negligible |

Horizon (Y = ln min(T_c, H_max)): pinball at 0.5 / Harrell's C / coverage of q_0.1 below the cap; reading against F.

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | C | cov q_0.1 | reading vs F |
|---|---|---|---|---|---|
| oracle | none | 0.221 | 0.5 | 0.102 | substantial |
| oracle | lyapunov | 0.251 | 0.674 | 0.075 | substantial |
| oracle | RO | 0.201 | 0.621 | 0.117 | substantial |
| oracle | ROIN | 0.16 | 0.719 | 0.106 |  |
| oracle | X | 0.171 | 0.695 | 0.148 | needed, size not determined |
| oracle | X+F | 0.135 | 0.765 | 0.155 | lowers |
| oracle | Lyapunov rank | | 0.671 | | |
| deployable | none | 0.221 | 0.5 | 0.102 | substantial |
| deployable | lyapunov | 0.255 | 0.671 | 0.0769 | substantial |
| deployable | RO | 0.194 | 0.635 | 0.122 | substantial |
| deployable | ROIN | 0.158 | 0.72 | 0.124 |  |
| deployable | X | 0.172 | 0.694 | 0.137 | needed, size not determined |
| deployable | X+F | 0.135 | 0.767 | 0.143 | lowers |
| deployable | Lyapunov rank | | 0.668 | | |

### C2. Shared information (oracle and deployable profiles)

Skill retained = [L(constant) - L(bottleneck)] / [L(constant) - L(F)]; reading: keeps most (CI > 0.5), loses most (CI < 0.5), else not determined. Forward: horizon from g (five clipped weights; g_w: the L_w fits); reverse: weight from h (three quantiles), scored by L_A (MSE; deployable: realized per draw, R2 guard) and by L_w (weight units, unit-weight fits). Training inputs cross-fitted.

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| profile | direction | horizon | full skill [CI] | retained L_A / pinball [CI] | reading | retained L_w [CI] | reading L_w |
|---|---|---|---|---|---|---|---|
| oracle | forward (g; g_w) | all five | 0.0608 [0.0559, 0.0654] | 0.438 [0.397, 0.481] | loses most | 0.594 [0.552, 0.636] | keeps most |
| oracle | forward, one weight | H=8 (0.27 LT) | | -0.00476 [-0.0132, 0.00344] | loses most | | |
| oracle | forward, one weight | H=15 (0.50 LT) | | 0.0557 [0.0384, 0.0739] | loses most | | |
| oracle | forward, one weight | H=30 (1.00 LT) | | 0.0824 [0.0606, 0.104] | loses most | | |
| oracle | forward, one weight | H=60 (2.00 LT) | | 0.132 [0.11, 0.154] | loses most | | |
| oracle | forward, one weight | H=120 (4.00 LT) | | 0.228 [0.192, 0.266] | loses most | | |
| oracle | reverse | H=8 (0.27 LT) | 0.000346 [1.65e-05, 0.00097] | 0.2 [-6.47, 0.653] | not determined (n_eff < 50) | 0.161 [0.119, 0.2] | loses most |
| oracle | reverse | H=15 (0.50 LT) | 0.000341 [-0.00024, 0.00105] | 0.423 [-, -] | not determined (full-profile skill not established) | 0.214 [0.171, 0.258] | loses most |
| oracle | reverse | H=30 (1.00 LT) | 0.000737 [7.97e-05, 0.00136] | -0.229 [-4.43, 0.484] | not determined (n_eff < 50) | 0.191 [0.124, 0.258] | loses most |
| oracle | reverse | H=60 (2.00 LT) | 0.00983 [0.00687, 0.0127] | 0.404 [0.25, 0.606] | not determined (interval spans 0.5) | 0.403 [0.348, 0.464] | loses most |
| oracle | reverse | H=120 (4.00 LT) | 0.0139 [0.0104, 0.0179] | 0.393 [0.243, 0.544] | not determined (interval spans 0.5) | 0.268 [0.162, 0.388] | loses most |
| deployable | forward (g; g_w) | all five | 0.0628 [0.0579, 0.0675] | 0.28 [0.243, 0.319] | loses most | 0.562 [0.528, 0.598] | keeps most |
| deployable | forward, one weight | H=8 (0.27 LT) | | -0.0663 [-0.0831, -0.05] | loses most | | |
| deployable | forward, one weight | H=15 (0.50 LT) | | 0.0572 [0.0411, 0.073] | loses most | | |
| deployable | forward, one weight | H=30 (1.00 LT) | | 0.0505 [0.0354, 0.0659] | loses most | | |
| deployable | forward, one weight | H=60 (2.00 LT) | | 0.0958 [0.0709, 0.121] | loses most | | |
| deployable | forward, one weight | H=120 (4.00 LT) | | 0.234 [0.193, 0.275] | loses most | | |
| deployable | reverse | H=8 (0.27 LT) | -0.000286 [-0.00068, -2.32e-06] | - [-, -] | not determined (full-profile skill not established) | 0.0636 [0.036, 0.0892] | loses most |
| deployable | reverse | H=15 (0.50 LT) | -0.000191 [-0.000355, -3.76e-05] | - [-, -] | not determined (full-profile skill not established) | 0.279 [0.214, 0.349] | loses most |
| deployable | reverse | H=30 (1.00 LT) | 0.000475 [4.73e-05, 0.000986] | 0.442 [-1.72, 3.9] | not determined (n_eff < 50) | 0.432 [0.342, 0.516] | not determined (interval spans 0.5) |
| deployable | reverse | H=60 (2.00 LT) | 0.00422 [0.000234, 0.00822] | 0.829 [0.396, 8.19] | not determined (interval spans 0.5) | 0.619 [0.545, 0.705] | keeps most |
| deployable | reverse | H=120 (4.00 LT) | 0.00678 [0.00209, 0.0117] | 0.771 [0.441, 1.93] | not determined (interval spans 0.5) | 0.533 [0.393, 0.722] | not determined (interval spans 0.5) |

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| profile | forward C-index F / g / g_w | reverse MSE(h)/MSE(F) per horizon | math-spec prediction (both lose most) | largest single-weight retention at H |
|---|---|---|---|---|
| oracle | 0.719 / 0.648 / 0.674 | H=8 (0.27 LT) 1.4 [1.14, 1.69] undetermined (n_eff < 50); H=15 (0.50 LT) 1.07 [0.921, 1.24] undetermined (n_eff < 50); H=30 (1.00 LT) 1.05 [1.01, 1.09] undetermined (n_eff < 50); H=60 (2.00 LT) 1.03 [1.02, 1.05] needed, size not determined; H=120 (4.00 LT) 1.01 [1.01, 1.02] small | **consistent** | 120 |
| deployable | 0.72 / 0.616 / 0.671 | H=8 (0.27 LT) 0.996 [0.777, 1.17] undetermined (n_eff < 50); H=15 (0.50 LT) 1.04 [0.938, 1.2] undetermined (n_eff < 50); H=30 (1.00 LT) 1.01 [0.989, 1.04] undetermined (n_eff < 50); H=60 (2.00 LT) 1 [0.986, 1.02] negligible; H=120 (4.00 LT) 1 [0.996, 1.01] negligible | **consistent** | 120 |

Oracle against deployable: retained (deployable) minus retained (oracle), paired 95% interval.

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| row | oracle | deployable | difference [CI] | reading |
|---|---|---|---|---|
| forward | 0.438 | 0.28 | -0.159 [-0.2, -0.116] | deployable retains less |
| forward_w | 0.594 | 0.562 | -0.0318 [-0.0771, 0.0143] | no difference detected |
| reverse/8 | 0.2 | - | - [-, -] | not determined (n_eff < 50) |
| reverse_w/8 | 0.161 | 0.0636 | -0.0976 [-0.139, -0.0556] | deployable retains less |
| reverse/15 | 0.423 | - | - [-, -] | not determined (full-profile skill not established) |
| reverse_w/15 | 0.214 | 0.279 | 0.0653 [-0.0031, 0.138] | no difference detected |
| reverse/30 | -0.229 | 0.442 | 0.672 [-, -] | not determined (n_eff < 50) |
| reverse_w/30 | 0.191 | 0.432 | 0.241 [0.172, 0.306] | deployable retains more |
| reverse/60 | 0.404 | 0.829 | 0.425 [-0.0483, 7.77] | no difference detected |
| reverse_w/60 | 0.403 | 0.619 | 0.216 [0.142, 0.299] | deployable retains more |
| reverse/120 | 0.393 | 0.771 | 0.378 [0.0703, 1.5] | deployable retains more |
| reverse_w/120 | 0.268 | 0.533 | 0.265 [0.141, 0.42] | deployable retains more |

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| horizon | Spearman(phi allocation, phi horizon) (4 items, descriptive) | phi_alloc R/O/I/N | phi_horizon R/O/I/N |
|---|---|---|---|
| H=8 (0.27 LT) | 0.8 | 0.0001/0.00012/0.00032/-0.00019 | 0.0013/0.013/0.043/0.0031 |
| H=15 (0.50 LT) | 0 | 0.00016/0.00031/5.4e-05/-0.00018 | 0.0013/0.013/0.043/0.0031 |
| H=30 (1.00 LT) | -0.8 | 0.00042/0.00023/-6.5e-05/0.00015 | 0.0013/0.013/0.043/0.0031 |
| H=60 (2.00 LT) | -0.4 | 0.005/0.0027/0.0012/0.00097 | 0.0013/0.013/0.043/0.0031 |
| H=120 (4.00 LT) | -0.8 | 0.0079/0.0028/0.0013/0.002 | 0.0013/0.013/0.043/0.0031 |

### C3. The deployable chain

False trust = P(T <= q_0.1) per (state, draw), target 0.1; T realized (the run's first passage against the noisy truth) or characteristic (moments). Trusted horizon = mean q_0.1 (LT). A4 + KM leaf uses the calibration A4 hybrid's characteristic horizon (no per-draw calibration errors on the full grid).

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| policy | false trust realized [CI] | false trust characteristic [CI] | mean trusted (LT) [CI] | q at cap |
|---|---|---|---|---|
| A2 + constant | 0.0751 [0.069, 0.0813] | 0.0965 [0.0872, 0.106] | 0.978 [0.978, 0.978] | 0 |
| A2 + h(F-hat) | 0.0979 [0.0921, 0.104] | 0.118 [0.109, 0.128] | 1.38 [1.36, 1.39] | 0 |
| A4 + KM leaf | 0.0746 [0.0692, 0.0803] | 0.0938 [0.0853, 0.102] | 1.28 [1.27, 1.29] | 0 |
| g(F-hat) + h(F-hat) | 0.0978 [0.0917, 0.104] | 0.121 [0.112, 0.131] | 1.4 [1.39, 1.42] | 0 |

Hybrid MSE ratio to A2 (realized per draw; 1.05 table, R2 guard).

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| policy | H=8 (0.27 LT) | H=15 (0.50 LT) | H=30 (1.00 LT) | H=60 (2.00 LT) | H=120 (4.00 LT) |
|---|---|---|---|---|---|
| A4 + KM leaf | 1.07 [0.941, 1.12] undetermined (n_eff < 50) | 1.06 [1.01, 1.1] undetermined (n_eff < 50) | 0.985 [0.954, 1.01] undetermined (n_eff < 50) | 0.993 [0.975, 1.01] negligible | 1.04 [1.02, 1.05] needed, size not determined |
| g(F-hat) + h(F-hat) | 1.24 [0.992, 1.77] undetermined (n_eff < 50) | 1.05 [1.01, 1.1] undetermined (n_eff < 50) | 0.98 [0.961, 0.998] undetermined (n_eff < 50) | 0.976 [0.954, 0.999] lowers | 0.989 [0.981, 0.996] lowers |

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| full system minus | false trust realized [CI] | false trust characteristic [CI] | trusted LT [CI] |
|---|---|---|---|
| A2 + constant | 0.0227 [0.0161, 0.0299] | 0.0248 [0.0142, 0.0358] | 0.423 [0.407, 0.44] |
| A2 + h(F-hat) | -0.000125 [-0.00363, 0.00306] | 0.003 [-0.002, 0.00806] | 0.0247 [0.0206, 0.0287] |
| A4 + KM leaf | 0.0232 [0.0179, 0.0283] | 0.0275 [0.0199, 0.0355] | 0.117 [0.107, 0.127] |

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| horizon model (own characteristic target) | pinball / constant's | constant/model ratio [CI] reading | cov 0.1 / 0.5 / 0.9 | C |
|---|---|---|---|---|
| h_A2(F-hat) | 0.16 / 0.233 | 1.46 [1.42, 1.5] substantial | 0.118 / 0.504 / 0.875 | 0.726 |
| h_g(F-hat) | 0.16 / 0.234 | 1.46 [1.42, 1.5] substantial | 0.121 / 0.503 / 0.873 | - |

### E-H2a. Amplification mismatch m(H) (H_0 = 1 LT; both r.m.s. <= 0.5 sigma_x)

Medians by tercile of I (low / mid / high). Spearman(m, I) on the kept states [95%]. B and A columns from the A/D record (oracle).

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| horizon | kept | m | abs drift w* | corr C/sqrt(E_C E_P) | Spearman(m, I) | B RI / OI | A drop-I (MSE) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 3681 | -0.076 / 0.14 / 0.42 | 0.05 / 0.11 / 0.14 | 0.2 / 0.18 / 0.24 | 0.17 [0.139, 0.201] | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=15 (0.50 LT) | 3668 | -0.031 / -0.091 / 0.2 | 0.05 / 0.11 / 0.12 | 0.18 / 0.18 / 0.25 | 0.116 [0.0853, 0.148] | no interaction gain detected / interaction gain detected | undetermined (n_eff < 50) |
| H=30 (1.00 LT) | 3691 | 0 / 0 / 0 | 0 / 0 / 0 | 0.19 / 0.2 / 0.27 | (H_0) | no interaction gain detected / interaction gain detected | undetermined (n_eff < 50) |
| H=60 (2.00 LT) | 2664 | -0.31 / -0.69 / -0.24 | 0.066 / 0.14 / 0.1 | 0.22 / 0.18 / 0.25 | 0.0102 [-0.0264, 0.0443] | interaction gain detected / interaction gain detected | negligible |
| H=120 (4.00 LT) | 1058 | -1.5 / -1.6 / -0.93 | 0.27 / 0.3 / 0.25 | 0.28 / 0.27 / 0.31 | 0.0777 [0.0147, 0.141] | no interaction gain detected / interaction gain detected | negligible |

**Reading: not determined** (horizons_used: ['60', '120'], horizons_supporting: [], horizons_null: ['60']).

### E-H2e. Library size and error correlation (sweep states)

1000 sweep states. Delta = value at N_lib 100000 minus 1000. corr = the H2e correlation (0 by convention where an error is constant over the draws).

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| rho | valid | corr 0 small / large lib | median corr small -> large | set | median Delta corr [CI] | Spearman(Delta corr, Delta R) [CI] | reading |
|---|---|---|---|---|---|---|---|
| 0.01 | 1000 | 554 / 12 | 0 -> 0.418 | all (1000) | 0.334 [0.316, 0.363] | 0.0464 [-0.0174, 0.106] | not determined |
| 0.01 | 1000 | 554 / 12 | 0 -> 0.418 | both_defined (442) | 0.231 [0.174, 0.286] | 0.00821 [-0.0939, 0.101] | not determined |
| 0.02 | 1000 | 259 / 1 | 0.0358 -> 0.404 | all (1000) | 0.268 [0.234, 0.288] | 0.0141 [-0.0476, 0.0776] | not determined |
| 0.02 | 1000 | 259 / 1 | 0.0358 -> 0.404 | both_defined (741) | 0.208 [0.179, 0.231] | 0.017 [-0.0602, 0.0895] | not determined |

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| rho | stratifier | median Delta corr low / mid / high | median Delta R low / mid / high |
|---|---|---|---|
| 0.01 | R | 0.32 / 0.36 / 0.33 | -1.4 / -1 / -1.5 |
| 0.01 | O | 0.33 / 0.34 / 0.33 | -1.7 / -1.4 / -0.93 |
| 0.01 | I | 0.32 / 0.32 / 0.39 | -1.4 / -1.4 / -1.2 |
| 0.01 | N | 0.3 / 0.36 / 0.34 | -1.5 / -1 / -1.4 |
| 0.01 | delta_R | 0.3 / 0.35 / 0.36 | -2.2 / -1.3 / -0.52 |
| 0.02 | R | 0.24 / 0.28 / 0.27 | -0.87 / -0.62 / -0.98 |
| 0.02 | O | 0.26 / 0.28 / 0.26 | -1.2 / -0.89 / -0.54 |
| 0.02 | I | 0.23 / 0.23 / 0.31 | -0.85 / -0.86 / -0.74 |
| 0.02 | N | 0.27 / 0.26 / 0.28 | -0.99 / -0.57 / -0.92 |
| 0.02 | delta_R | 0.28 / 0.25 / 0.27 | -1.7 / -0.83 / -0.12 |

**Reading** (final, after the convention check): rho 0.01: not determined; rho 0.02: not determined.

### E-H3c. A5 against A4

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| item | value |
|---|---|
| H3c ratio MSE(A5)/MSE(A4) [CI at level 0.983] (run) | 0.989 [0.949, 1.04], width 0.0861 |
| top-1% share: A5 loss / A4 loss / abs(A5 - A4) | 0.618 / 0.642 / 0.477 |
| autocorrelation of d = A5 - A4, lags 1..5 | 0.006, -0.015, 0.0014, -0.013, 0.0031 |
| block-5 means: lag-1 autocorrelation, variance ratio | -0.000757, 0.973 |
| K chosen; leaves used test / calibration; largest leaf share test | 4; 4 / 4; 0.405 |
| w*(H_ref) within-leaf share of variance | 0.937 |
| bimodality coefficient R/O/I/N, oracle; deployable | 0.22/0.23/0.43/0.84; 0.35/0.46/0.44/0.89 |
| Spearman pairs (oracle) | RO 0.1, RI -0.0063, RN 0.36, OI 0.35, ON 0.04, IN 0.017 |
| top-1% abs(d) states: mean percentile R/O/I/N | 0.65/0.55/0.89/0.46 |
| top-1% abs(d) states: median I pct; share high-I; median abs(x) pct; share sign change in window; share of sum d | 0.972; 0.9; 0.597; 0.35; 0.469 |

## E-H3c reading (this seed)

PHASE J CONFIRMATORY (CONF-7): pre-registered analysis, UNPROMOTED.

| item | value |
|---|---|
| H3c interval widths | lorenz63 0.242, rossler 0.048, chua 0.0861 |
| pattern (Lorenz-63 widest, Rössler narrowest) reproduced | True |
| Lorenz-63 part (top-1% share of sum abs(d) 0.627, median I percentile 0.22) | not consistent |
| Rössler part (BC deployable: R 0.48, O 0.793, I 0.496, N 0.903) | not consistent |
| **reading** | **not consistent** |

