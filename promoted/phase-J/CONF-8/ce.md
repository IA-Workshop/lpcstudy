# Phase J experiments C and E: CONF-8

**PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.** Run `phasej-CONF-8/phasej`; analysis commit `c19ad486b93a2ee96d64ce069ec42fd440428211` (dirty: False); A/D record `phasej-CONF-8/contrib-j/contrib.json`. Estimates with 95% intervals from the shared moving-block index sets (models fixed; training variance not included). Readings are descriptive; no causal claim; nothing here is set beside CONF-1.

## lorenz63

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| check | result |
|---|---|
| A2 rebuilt on 1..H_max equals the dumped A2 (bitwise); A4 horizon-free | True, True |
| refit reproduces WU-0048 (max abs: A/ROIN MSE oracle, deployable; W/ROIN L_w oracle, deployable) | 0 / 0 / 0 / 0 |
| T_c counts T = 1 / e_(T-1) = theta (A2 train, g train, A2 test, g test, A4 calibration) | 24/0, 86/0, 25/0, 106/0, 84/0 |
| A2 on 1..H_max: pooled curvature floor / columns at 0 or 1 | 0 / 0 |
| weights clipped to [0, 1] | g_oracle_test 3223, g_oracle_train_oof 2413, gw_oracle_test 2799, gw_oracle_train_oof 2386, g_deployable_test 7323, g_deployable_train_oof 4633, gw_deployable_test 3116, gw_deployable_train_oof 2565 |

### C1. Separate performance (from the A/D record, no refit)

Allocation: MSE per rule (oracle: moment form; deployable: realized); reading of the rung against F (MSE ratio, 1.05 table, n_eff guard). G(F) = 1 - L_A(F)/L_A(constant).

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| horizon | profile | constant | separation | RO | F (ROIN) | X | X+F | G(F) | sep vs F | RO vs F | X+F vs F |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 0.0148 | 0.00488 | 0.00458 | 0.00458 | 0.00541 | 0.00472 | 0.912 | undetermined | undetermined | undetermined |
| H=8 (0.27 LT) | deployable | 0.0145 | 0.0292 | 0.00804 | 0.0101 | 0.00515 | 0.00513 | 0.407 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | oracle | 0.0271 | 0.00844 | 0.00842 | 0.0082 | 0.0104 | 0.00802 | 0.935 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | deployable | 0.0294 | 0.0376 | 0.0227 | 0.0184 | 0.00995 | 0.0132 | 0.491 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | oracle | 0.051 | 0.0305 | 0.0316 | 0.0308 | 0.0322 | 0.0287 | 0.678 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | deployable | 0.0525 | 0.061 | 0.0434 | 0.0418 | 0.0325 | 0.0312 | 0.344 | substantial | undetermined | lowers |
| H=60 (2.00 LT) | oracle | 0.144 | 0.134 | 0.133 | 0.13 | 0.133 | 0.13 | 0.274 | undetermined | needed, size not determined | negligible |
| H=60 (2.00 LT) | deployable | 0.14 | 0.144 | 0.139 | 0.135 | 0.129 | 0.132 | 0.101 | needed, size not determined | undetermined | negligible |
| H=120 (4.00 LT) | oracle | 0.886 | 0.953 | 0.879 | 0.872 | 0.873 | 0.87 | 0.0551 | substantial | small | negligible |
| H=120 (4.00 LT) | deployable | 0.898 | 0.947 | 0.889 | 0.883 | 0.882 | 0.879 | 0.0545 | substantial | small | negligible |

Horizon (Y = ln min(T_c, H_max)): pinball at 0.5 / Harrell's C / coverage of q_0.1 below the cap; reading against F.

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | C | cov q_0.1 | reading vs F |
|---|---|---|---|---|---|
| oracle | none | 0.187 | 0.5 | 0.1 | substantial |
| oracle | lyapunov | 0.292 | 0.615 | 0.0701 | substantial |
| oracle | RO | 0.183 | 0.57 | 0.132 | substantial |
| oracle | ROIN | 0.142 | 0.687 | 0.136 |  |
| oracle | X | 0.153 | 0.69 | 0.142 | needed, size not determined |
| oracle | X+F | 0.122 | 0.737 | 0.152 | lowers |
| oracle | Lyapunov rank | | 0.612 | | |
| deployable | none | 0.187 | 0.5 | 0.1 | substantial |
| deployable | lyapunov | 0.285 | 0.62 | 0.0691 | substantial |
| deployable | RO | 0.18 | 0.578 | 0.12 | substantial |
| deployable | ROIN | 0.139 | 0.696 | 0.119 |  |
| deployable | X | 0.155 | 0.688 | 0.139 | substantial |
| deployable | X+F | 0.124 | 0.731 | 0.144 | lowers |
| deployable | Lyapunov rank | | 0.616 | | |

### C2. Shared information (oracle and deployable profiles)

Skill retained = [L(constant) - L(bottleneck)] / [L(constant) - L(F)]; reading: keeps most (CI > 0.5), loses most (CI < 0.5), else not determined. Forward: horizon from g (five clipped weights; g_w: the L_w fits); reverse: weight from h (three quantiles), scored by L_A (MSE; deployable: realized per draw, R2 guard) and by L_w (weight units, unit-weight fits). Training inputs cross-fitted.

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| profile | direction | horizon | full skill [CI] | retained L_A / pinball [CI] | reading | retained L_w [CI] | reading L_w |
|---|---|---|---|---|---|---|---|
| oracle | forward (g; g_w) | all five | 0.0447 [0.0398, 0.0497] | 0.0884 [0.0527, 0.121] | loses most | 0.322 [0.27, 0.374] | loses most |
| oracle | forward, one weight | H=8 (0.27 LT) | | 0.0312 [0.0141, 0.0485] | loses most | | |
| oracle | forward, one weight | H=15 (0.50 LT) | | 0.0496 [0.0331, 0.0657] | loses most | | |
| oracle | forward, one weight | H=30 (1.00 LT) | | 0.0247 [0.00981, 0.0398] | loses most | | |
| oracle | forward, one weight | H=60 (2.00 LT) | | -0.00521 [-0.0154, 0.00522] | loses most | | |
| oracle | forward, one weight | H=120 (4.00 LT) | | 0.0422 [0.0209, 0.0648] | loses most | | |
| oracle | reverse | H=8 (0.27 LT) | 0.0102 [0.00779, 0.013] | 0.371 [0.202, 0.496] | not determined (n_eff < 50) | 0.189 [0.144, 0.236] | loses most |
| oracle | reverse | H=15 (0.50 LT) | 0.0189 [0.0151, 0.0235] | 0.625 [0.458, 0.744] | not determined (n_eff < 50) | 0.205 [0.16, 0.251] | loses most |
| oracle | reverse | H=30 (1.00 LT) | 0.0202 [0.0146, 0.0262] | 0.383 [-0.0228, 0.673] | not determined (n_eff < 50) | 0.218 [0.177, 0.256] | loses most |
| oracle | reverse | H=60 (2.00 LT) | 0.0138 [0.0078, 0.0198] | 0.316 [0.174, 0.529] | not determined (interval spans 0.5) | 0.188 [0.14, 0.235] | loses most |
| oracle | reverse | H=120 (4.00 LT) | 0.0145 [0.00852, 0.0205] | 0.446 [0.244, 0.772] | not determined (interval spans 0.5) | 0.193 [0.0639, 0.322] | loses most |
| deployable | forward (g; g_w) | all five | 0.0477 [0.0427, 0.0526] | 0.143 [0.115, 0.174] | loses most | 0.342 [0.304, 0.382] | loses most |
| deployable | forward, one weight | H=8 (0.27 LT) | | 0.0422 [0.021, 0.0623] | loses most | | |
| deployable | forward, one weight | H=15 (0.50 LT) | | 0.0782 [0.0601, 0.0962] | loses most | | |
| deployable | forward, one weight | H=30 (1.00 LT) | | 0.094 [0.0707, 0.117] | loses most | | |
| deployable | forward, one weight | H=60 (2.00 LT) | | -0.00406 [-0.0177, 0.00897] | loses most | | |
| deployable | forward, one weight | H=120 (4.00 LT) | | 0.0643 [0.0435, 0.0872] | loses most | | |
| deployable | reverse | H=8 (0.27 LT) | 0.00443 [0.00193, 0.00672] | 0.653 [0.351, 1.19] | not determined (n_eff < 50) | 0.234 [0.17, 0.29] | loses most |
| deployable | reverse | H=15 (0.50 LT) | 0.0111 [0.00616, 0.0161] | 0.536 [0.263, 0.856] | not determined (n_eff < 50) | 0.269 [0.205, 0.329] | loses most |
| deployable | reverse | H=30 (1.00 LT) | 0.0108 [0.0054, 0.0165] | 0.736 [0.132, 1.1] | not determined (interval spans 0.5) | 0.224 [0.184, 0.264] | loses most |
| deployable | reverse | H=60 (2.00 LT) | 0.00475 [0.000941, 0.00868] | 0.937 [0.453, 2.67] | not determined (interval spans 0.5) | 0.22 [0.168, 0.276] | loses most |
| deployable | reverse | H=120 (4.00 LT) | 0.015 [0.00941, 0.0206] | 0.523 [0.353, 0.784] | not determined (interval spans 0.5) | 0.457 [0.343, 0.608] | not determined (interval spans 0.5) |

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| profile | forward C-index F / g / g_w | reverse MSE(h)/MSE(F) per horizon | math-spec prediction (both lose most) | largest single-weight retention at H |
|---|---|---|---|---|
| oracle | 0.687 / 0.579 / 0.618 | H=8 (0.27 LT) 2.4 [1.65, 8.77] undetermined (n_eff < 50); H=15 (0.50 LT) 1.87 [1.56, 2.34] undetermined (n_eff < 50); H=30 (1.00 LT) 1.4 [1.21, 1.64] undetermined (n_eff < 50); H=60 (2.00 LT) 1.07 [1.03, 1.12] needed, size not determined; H=120 (4.00 LT) 1.01 [1, 1.02] small | **consistent** | 15 |
| deployable | 0.696 / 0.59 / 0.622 | H=8 (0.27 LT) 1.15 [0.959, 1.47] undetermined (n_eff < 50); H=15 (0.50 LT) 1.28 [1.05, 1.56] undetermined (n_eff < 50); H=30 (1.00 LT) 1.07 [0.974, 1.18] undetermined; H=60 (2.00 LT) 1 [0.981, 1.02] negligible; H=120 (4.00 LT) 1.01 [1, 1.01] small | **consistent** | 30 |

Oracle against deployable: retained (deployable) minus retained (oracle), paired 95% interval.

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| row | oracle | deployable | difference [CI] | reading |
|---|---|---|---|---|
| forward | 0.0884 | 0.143 | 0.0549 [0.0228, 0.0893] | deployable retains more |
| forward_w | 0.322 | 0.342 | 0.0194 [-0.0416, 0.0774] | no difference detected |
| reverse/8 | 0.371 | 0.653 | 0.282 [-0.0429, 0.867] | not determined (n_eff < 50) |
| reverse_w/8 | 0.189 | 0.234 | 0.0455 [-0.0134, 0.108] | no difference detected |
| reverse/15 | 0.625 | 0.536 | -0.089 [-0.363, 0.265] | not determined (n_eff < 50) |
| reverse_w/15 | 0.205 | 0.269 | 0.0646 [0.00288, 0.132] | deployable retains more |
| reverse/30 | 0.383 | 0.736 | 0.353 [-0.171, 0.796] | not determined (n_eff < 50) |
| reverse_w/30 | 0.218 | 0.224 | 0.00604 [-0.038, 0.0532] | no difference detected |
| reverse/60 | 0.316 | 0.937 | 0.621 [0.131, 2.29] | deployable retains more |
| reverse_w/60 | 0.188 | 0.22 | 0.0314 [-0.0298, 0.101] | no difference detected |
| reverse/120 | 0.446 | 0.523 | 0.0769 [-0.236, 0.353] | no difference detected |
| reverse_w/120 | 0.193 | 0.457 | 0.264 [0.126, 0.424] | deployable retains more |

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| horizon | Spearman(phi allocation, phi horizon) (4 items, descriptive) | phi_alloc R/O/I/N | phi_horizon R/O/I/N |
|---|---|---|---|
| H=8 (0.27 LT) | 0.8 | 0.00013/0.0071/0.0025/0.00049 | 0.0012/0.0091/0.032/0.0026 |
| H=15 (0.50 LT) | 0.8 | 0.0012/0.013/0.0023/0.002 | 0.0012/0.0091/0.032/0.0026 |
| H=30 (1.00 LT) | 0.8 | 0.0013/0.014/0.003/0.0023 | 0.0012/0.0091/0.032/0.0026 |
| H=60 (2.00 LT) | 0.6 | 0.0024/0.0078/0.0024/0.0012 | 0.0012/0.0091/0.032/0.0026 |
| H=120 (4.00 LT) | -0.2 | 0.005/0.0045/0.0045/0.00052 | 0.0012/0.0091/0.032/0.0026 |

### C3. The deployable chain

False trust = P(T <= q_0.1) per (state, draw), target 0.1; T realized (the run's first passage against the noisy truth) or characteristic (moments). Trusted horizon = mean q_0.1 (LT). A4 + KM leaf uses the calibration A4 hybrid's characteristic horizon (no per-draw calibration errors on the full grid).

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| policy | false trust realized [CI] | false trust characteristic [CI] | mean trusted (LT) [CI] | q at cap |
|---|---|---|---|---|
| A2 + constant | 0.0713 [0.0651, 0.0781] | 0.106 [0.0983, 0.115] | 0.562 [0.562, 0.562] | 0 |
| A2 + h(F-hat) | 0.0957 [0.0899, 0.102] | 0.127 [0.118, 0.136] | 1.05 [1.04, 1.07] | 0 |
| A4 + KM leaf | 0.0678 [0.0628, 0.0731] | 0.104 [0.0961, 0.113] | 1.1 [1.09, 1.1] | 0 |
| g(F-hat) + h(F-hat) | 0.091 [0.0849, 0.097] | 0.113 [0.106, 0.122] | 1.16 [1.15, 1.18] | 0 |

Hybrid MSE ratio to A2 (realized per draw; 1.05 table, R2 guard).

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| policy | H=8 (0.27 LT) | H=15 (0.50 LT) | H=30 (1.00 LT) | H=60 (2.00 LT) | H=120 (4.00 LT) |
|---|---|---|---|---|---|
| A4 + KM leaf | 2 [1.5, 2.7] substantial | 1.28 [1.16, 1.38] substantial | 1.16 [1.1, 1.22] substantial | 1.03 [1.01, 1.04] small | 1.05 [1.04, 1.07] needed, size not determined |
| g(F-hat) + h(F-hat) | 0.689 [0.515, 0.857] lowers | 0.625 [0.5, 0.771] lowers | 0.797 [0.698, 0.894] lowers | 0.966 [0.939, 0.993] lowers | 0.983 [0.977, 0.989] lowers |

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| full system minus | false trust realized [CI] | false trust characteristic [CI] | trusted LT [CI] |
|---|---|---|---|
| A2 + constant | 0.0197 [0.0129, 0.0264] | 0.00719 [-0.00175, 0.0157] | 0.601 [0.588, 0.614] |
| A2 + h(F-hat) | -0.00469 [-0.0103, 0.000687] | -0.0134 [-0.0204, -0.006] | 0.111 [0.0997, 0.122] |
| A4 + KM leaf | 0.0232 [0.0173, 0.0292] | 0.00912 [0.000748, 0.0179] | 0.0677 [0.0563, 0.0804] |

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| horizon model (own characteristic target) | pinball / constant's | constant/model ratio [CI] reading | cov 0.1 / 0.5 / 0.9 | C |
|---|---|---|---|---|
| h_A2(F-hat) | 0.204 / 0.267 | 1.31 [1.27, 1.35] substantial | 0.127 / 0.502 / 0.871 | 0.68 |
| h_g(F-hat) | 0.174 / 0.219 | 1.26 [1.22, 1.3] substantial | 0.113 / 0.495 / 0.871 | - |

### E-H2a. Amplification mismatch m(H) (H_0 = 1 LT; both r.m.s. <= 0.5 sigma_x)

Medians by tercile of I (low / mid / high). Spearman(m, I) on the kept states [95%]. B and A columns from the A/D record (oracle).

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| horizon | kept | m | abs drift w* | corr C/sqrt(E_C E_P) | Spearman(m, I) | B RI / OI | A drop-I (MSE) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 3537 | -0.094 / 0.089 / 0.24 | 0.052 / 0.038 / 0.071 | 0.12 / 0.12 / 0.15 | 0.114 [0.0807, 0.148] | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=15 (0.50 LT) | 3495 | 0.00012 / 0.056 / 0.068 | 0.046 / 0.052 / 0.064 | 0.13 / 0.12 / 0.16 | 0.0459 [0.0124, 0.0768] | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=30 (1.00 LT) | 3574 | 0 / 0 / 0 | 0 / 0 / 0 | 0.13 / 0.14 / 0.18 | (H_0) | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=60 (2.00 LT) | 2746 | -0.15 / 0.046 / -0.075 | 0.058 / 0.071 / 0.077 | 0.14 / 0.19 / 0.18 | 0.0358 [-0.000262, 0.0723] | no interaction gain detected / no interaction gain detected | small |
| H=120 (4.00 LT) | 629 | -1.9 / -2.6 / -2.5 | 0.31 / 0.48 / 0.48 | 0.26 / 0.33 / 0.32 | -0.0953 [-0.167, -0.0224] | no interaction gain detected / interaction gain detected | small |

**Reading: not determined** (horizons_used: ['60', '120'], horizons_supporting: [], horizons_null: ['60']).

### E-H2e. Library size and error correlation (sweep states)

1000 sweep states. Delta = value at N_lib 100000 minus 1000. corr = the H2e correlation (0 by convention where an error is constant over the draws).

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| rho | valid | corr 0 small / large lib | median corr small -> large | set | median Delta corr [CI] | Spearman(Delta corr, Delta R) [CI] | reading |
|---|---|---|---|---|---|---|---|
| 0.01 | 1000 | 726 / 11 | 0 -> 0.425 | all (1000) | 0.38 [0.36, 0.402] | 0.0425 [-0.015, 0.101] | not determined |
| 0.01 | 1000 | 726 / 11 | 0 -> 0.425 | both_defined (272) | 0.194 [0.149, 0.248] | -0.116 [-0.225, 0.00067] | not determined |
| 0.02 | 1000 | 489 / 2 | 0 -> 0.439 | all (1000) | 0.34 [0.318, 0.362] | -0.055 [-0.111, 0.00456] | not determined |
| 0.02 | 1000 | 489 / 2 | 0 -> 0.439 | both_defined (511) | 0.239 [0.202, 0.27] | -0.0965 [-0.184, -0.00332] | consistent |

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| rho | stratifier | median Delta corr low / mid / high | median Delta R low / mid / high |
|---|---|---|---|
| 0.01 | R | 0.4 / 0.4 / 0.34 | -1.7 / -1.8 / -1.9 |
| 0.01 | O | 0.42 / 0.39 / 0.32 | -1.7 / -1.8 / -1.8 |
| 0.01 | I | 0.35 / 0.41 / 0.38 | -1.8 / -1.9 / -1.7 |
| 0.01 | N | 0.33 / 0.43 / 0.38 | -2 / -1.7 / -1.7 |
| 0.01 | delta_R | 0.39 / 0.34 / 0.41 | -2.8 / -1.8 / -0.77 |
| 0.02 | R | 0.34 / 0.37 / 0.31 | -1.1 / -1.3 / -1.3 |
| 0.02 | O | 0.36 / 0.37 / 0.25 | -1.1 / -1.3 / -1.3 |
| 0.02 | I | 0.33 / 0.38 / 0.32 | -1.4 / -1.3 / -1.1 |
| 0.02 | N | 0.3 / 0.38 / 0.33 | -1.4 / -1.1 / -1.2 |
| 0.02 | delta_R | 0.38 / 0.31 / 0.34 | -2.2 / -1.2 / -0.31 |

**Reading** (final, after the convention check): rho 0.01: not determined; rho 0.02: not determined (depends on the zero-variance convention).

### E-H3c. A5 against A4

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| item | value |
|---|---|
| H3c ratio MSE(A5)/MSE(A4) [CI at level 0.983] (run) | 0.769 [0.688, 0.846], width 0.158 |
| top-1% share: A5 loss / A4 loss / abs(A5 - A4) | 0.51 / 0.556 / 0.644 |
| autocorrelation of d = A5 - A4, lags 1..5 | -0.0034, -0.0096, -0.013, 0.0081, 0.054 |
| block-5 means: lag-1 autocorrelation, variance ratio | 0.056, 0.958 |
| K chosen; leaves used test / calibration; largest leaf share test | 6; 6 / 6; 0.312 |
| w*(H_ref) within-leaf share of variance | 0.905 |
| bimodality coefficient R/O/I/N, oracle; deployable | 0.26/0.78/0.53/0.83; 0.32/0.41/0.54/0.9 |
| Spearman pairs (oracle) | RO 0.52, RI -0.022, RN 0.31, OI 0.0094, ON -0.045, IN 0.076 |
| top-1% abs(d) states: mean percentile R/O/I/N | 0.74/0.93/0.36/0.27 |
| top-1% abs(d) states: median I pct; share high-I; median abs(x) pct; share sign change in window; share of sum d | 0.266; 0.15; 0.594; 0.7; 0.988 |

## rossler

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| check | result |
|---|---|
| A2 rebuilt on 1..H_max equals the dumped A2 (bitwise); A4 horizon-free | True, True |
| refit reproduces WU-0048 (max abs: A/ROIN MSE oracle, deployable; W/ROIN L_w oracle, deployable) | 0 / 0 / 0 / 0 |
| T_c counts T = 1 / e_(T-1) = theta (A2 train, g train, A2 test, g test, A4 calibration) | 0/0, 0/0, 0/0, 0/0, 0/0 |
| A2 on 1..H_max: pooled curvature floor / columns at 0 or 1 | 0 / 0 |
| weights clipped to [0, 1] | g_oracle_test 3197, g_oracle_train_oof 2495, gw_oracle_test 1711, gw_oracle_train_oof 1519, g_deployable_test 9775, g_deployable_train_oof 7421, gw_deployable_test 1607, gw_deployable_train_oof 1459 |

### C1. Separate performance (from the A/D record, no refit)

Allocation: MSE per rule (oracle: moment form; deployable: realized); reading of the rung against F (MSE ratio, 1.05 table, n_eff guard). G(F) = 1 - L_A(F)/L_A(constant).

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| horizon | profile | constant | separation | RO | F (ROIN) | X | X+F | G(F) | sep vs F | RO vs F | X+F vs F |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 0.000126 | 0.000123 | 0.000116 | 0.000115 | 0.000124 | 0.000115 | 0.464 | substantial | small | lowers |
| H=8 (0.27 LT) | deployable | 0.000126 | 0.000134 | 0.000126 | 0.000126 | 0.000125 | 0.000125 | 0.0205 | needed, size not determined | negligible | lowers |
| H=15 (0.50 LT) | oracle | 0.000216 | 0.000206 | 0.000196 | 0.000195 | 0.000215 | 0.000194 | 0.558 | needed, size not determined | small | negligible |
| H=15 (0.50 LT) | deployable | 0.000216 | 0.000231 | 0.000217 | 0.000217 | 0.000215 | 0.000215 | -0.0164 | needed, size not determined | negligible | lowers |
| H=30 (1.00 LT) | oracle | 0.000793 | 0.000706 | 0.000695 | 0.000691 | 0.000791 | 0.000689 | 0.622 | small | small | negligible |
| H=30 (1.00 LT) | deployable | 0.000799 | 0.000825 | 0.000802 | 0.000799 | 0.000787 | 0.00079 | -0.00311 | needed, size not determined | negligible | lowers |
| H=60 (2.00 LT) | oracle | 0.0127 | 0.0113 | 0.0114 | 0.0114 | 0.0127 | 0.0115 | 0.366 | negligible | negligible | negligible |
| H=60 (2.00 LT) | deployable | 0.0131 | 0.0129 | 0.0129 | 0.0129 | 0.0131 | 0.0129 | 0.051 | negligible | negligible | negligible |
| H=120 (4.00 LT) | oracle | 0.11 | 0.111 | 0.108 | 0.107 | 0.11 | 0.107 | 0.0866 | needed, size not determined | small | negligible |
| H=120 (4.00 LT) | deployable | 0.11 | 0.115 | 0.109 | 0.109 | 0.11 | 0.109 | 0.0427 | needed, size not determined | small | negligible |

Horizon (Y = ln min(T_c, H_max)): pinball at 0.5 / Harrell's C / coverage of q_0.1 below the cap; reading against F.

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | C | cov q_0.1 | reading vs F |
|---|---|---|---|---|---|
| oracle | none | 0.161 | 0.5 | 0.102 | substantial |
| oracle | lyapunov | 0.172 | 0.631 | 0.0664 | substantial |
| oracle | RO | 0.156 | 0.571 | 0.0998 | substantial |
| oracle | ROIN | 0.122 | 0.681 | 0.105 |  |
| oracle | X | 0.121 | 0.7 | 0.15 | negligible |
| oracle | X+F | 0.0936 | 0.769 | 0.144 | lowers |
| oracle | Lyapunov rank | | 0.629 | | |
| deployable | none | 0.161 | 0.5 | 0.102 | substantial |
| deployable | lyapunov | 0.173 | 0.626 | 0.0678 | substantial |
| deployable | RO | 0.149 | 0.601 | 0.106 | substantial |
| deployable | ROIN | 0.12 | 0.691 | 0.122 |  |
| deployable | X | 0.123 | 0.695 | 0.142 | undetermined |
| deployable | X+F | 0.0909 | 0.771 | 0.142 | lowers |
| deployable | Lyapunov rank | | 0.624 | | |

### C2. Shared information (oracle and deployable profiles)

Skill retained = [L(constant) - L(bottleneck)] / [L(constant) - L(F)]; reading: keeps most (CI > 0.5), loses most (CI < 0.5), else not determined. Forward: horizon from g (five clipped weights; g_w: the L_w fits); reverse: weight from h (three quantiles), scored by L_A (MSE; deployable: realized per draw, R2 guard) and by L_w (weight units, unit-weight fits). Training inputs cross-fitted.

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| profile | direction | horizon | full skill [CI] | retained L_A / pinball [CI] | reading | retained L_w [CI] | reading L_w |
|---|---|---|---|---|---|---|---|
| oracle | forward (g; g_w) | all five | 0.0385 [0.035, 0.0419] | 0.388 [0.336, 0.439] | loses most | 0.415 [0.357, 0.472] | loses most |
| oracle | forward, one weight | H=8 (0.27 LT) | | -0.00857 [-0.03, 0.0119] | loses most | | |
| oracle | forward, one weight | H=15 (0.50 LT) | | 0.0145 [-0.00788, 0.0367] | loses most | | |
| oracle | forward, one weight | H=30 (1.00 LT) | | 0.013 [-0.00229, 0.0277] | loses most | | |
| oracle | forward, one weight | H=60 (2.00 LT) | | 0.0331 [0.00532, 0.0608] | loses most | | |
| oracle | forward, one weight | H=120 (4.00 LT) | | 0.373 [0.313, 0.432] | loses most | | |
| oracle | reverse | H=8 (0.27 LT) | 1.02e-05 [9.31e-06, 1.12e-05] | 0.0791 [0.0574, 0.1] | loses most | 0.276 [0.228, 0.328] | loses most |
| oracle | reverse | H=15 (0.50 LT) | 2.13e-05 [1.91e-05, 2.36e-05] | 0.107 [0.0896, 0.125] | loses most | 0.231 [0.192, 0.269] | loses most |
| oracle | reverse | H=30 (1.00 LT) | 0.000102 [8.98e-05, 0.000114] | 0.0755 [0.0529, 0.0993] | loses most | 0.248 [0.202, 0.292] | loses most |
| oracle | reverse | H=60 (2.00 LT) | 0.00137 [0.00112, 0.00165] | 0.102 [0.0661, 0.14] | loses most | 0.294 [0.244, 0.342] | loses most |
| oracle | reverse | H=120 (4.00 LT) | 0.00278 [0.00208, 0.00346] | 0.292 [0.131, 0.443] | loses most | 0.264 [0.161, 0.358] | loses most |
| deployable | forward (g; g_w) | all five | 0.0412 [0.0376, 0.0446] | 0.418 [0.366, 0.47] | loses most | 0.455 [0.406, 0.502] | not determined (interval spans 0.5) |
| deployable | forward, one weight | H=8 (0.27 LT) | | 0.0187 [0.00591, 0.0328] | loses most | | |
| deployable | forward, one weight | H=15 (0.50 LT) | | 0.0234 [0.00895, 0.0383] | loses most | | |
| deployable | forward, one weight | H=30 (1.00 LT) | | 0.0513 [0.0337, 0.0701] | loses most | | |
| deployable | forward, one weight | H=60 (2.00 LT) | | 0.0491 [0.0282, 0.0701] | loses most | | |
| deployable | forward, one weight | H=120 (4.00 LT) | | 0.365 [0.313, 0.417] | loses most | | |
| deployable | reverse | H=8 (0.27 LT) | 4.63e-07 [-4.53e-07, 1.42e-06] | -0.166 [-, -] | not determined (full-profile skill not established) | 0.0233 [-0.000346, 0.047] | loses most |
| deployable | reverse | H=15 (0.50 LT) | -6.26e-07 [-3.62e-06, 2.36e-06] | - [-, -] | not determined (full-profile skill not established) | 0.0344 [0.00729, 0.0613] | loses most |
| deployable | reverse | H=30 (1.00 LT) | -5.29e-07 [-1.43e-05, 1.22e-05] | - [-, -] | not determined (full-profile skill not established) | 0.0643 [0.0382, 0.0908] | loses most |
| deployable | reverse | H=60 (2.00 LT) | 0.00021 [4.19e-05, 0.000401] | 0.236 [-0.0585, 1.11] | not determined (interval spans 0.5) | 0.133 [0.0749, 0.193] | loses most |
| deployable | reverse | H=120 (4.00 LT) | 0.00139 [0.000889, 0.00194] | 0.804 [0.533, 1.13] | keeps most | 0.516 [0.287, 0.703] | not determined (interval spans 0.5) |

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| profile | forward C-index F / g / g_w | reverse MSE(h)/MSE(F) per horizon | math-spec prediction (both lose most) | largest single-weight retention at H |
|---|---|---|---|---|
| oracle | 0.681 / 0.611 / 0.617 | H=8 (0.27 LT) 1.08 [1.07, 1.09] substantial; H=15 (0.50 LT) 1.1 [1.09, 1.11] substantial; H=30 (1.00 LT) 1.14 [1.12, 1.15] substantial; H=60 (2.00 LT) 1.11 [1.09, 1.13] substantial; H=120 (4.00 LT) 1.02 [1.01, 1.02] small | **consistent** | 120 |
| deployable | 0.691 / 0.614 / 0.625 | H=8 (0.27 LT) 1 [0.997, 1.01] negligible; H=15 (0.50 LT) 0.998 [0.985, 1.01] negligible; H=30 (1.00 LT) 1 [0.985, 1.02] negligible; H=60 (2.00 LT) 1.01 [1, 1.03] negligible; H=120 (4.00 LT) 1 [0.999, 1.01] negligible | **not consistent** | 120 |

Oracle against deployable: retained (deployable) minus retained (oracle), paired 95% interval.

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| row | oracle | deployable | difference [CI] | reading |
|---|---|---|---|---|
| forward | 0.388 | 0.418 | 0.0302 [-0.0144, 0.0767] | no difference detected |
| forward_w | 0.415 | 0.455 | 0.0393 [-0.00418, 0.0881] | no difference detected |
| reverse/8 | 0.0791 | -0.166 | -0.245 [-, -] | not determined (full-profile skill not established) |
| reverse_w/8 | 0.276 | 0.0233 | -0.253 [-0.305, -0.203] | deployable retains less |
| reverse/15 | 0.107 | - | - [-, -] | not determined (full-profile skill not established) |
| reverse_w/15 | 0.231 | 0.0344 | -0.197 [-0.238, -0.155] | deployable retains less |
| reverse/30 | 0.0755 | - | - [-, -] | not determined (full-profile skill not established) |
| reverse_w/30 | 0.248 | 0.0643 | -0.184 [-0.235, -0.131] | deployable retains less |
| reverse/60 | 0.102 | 0.236 | 0.133 [-0.163, 1.01] | no difference detected |
| reverse_w/60 | 0.294 | 0.133 | -0.161 [-0.234, -0.0845] | deployable retains less |
| reverse/120 | 0.292 | 0.804 | 0.512 [0.252, 0.853] | deployable retains more |
| reverse_w/120 | 0.264 | 0.516 | 0.251 [0.0447, 0.445] | deployable retains more |

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| horizon | Spearman(phi allocation, phi horizon) (4 items, descriptive) | phi_alloc R/O/I/N | phi_horizon R/O/I/N |
|---|---|---|---|
| H=8 (0.27 LT) | -1 | 6.5e-06/1.2e-06/1.2e-08/2.6e-06 | 0.00071/0.01/0.026/0.0014 |
| H=15 (0.50 LT) | -1 | 1.5e-05/2.3e-06/-1.9e-07/4.3e-06 | 0.00071/0.01/0.026/0.0014 |
| H=30 (1.00 LT) | -0.8 | 7.2e-05/1.4e-05/1.5e-06/1.4e-05 | 0.00071/0.01/0.026/0.0014 |
| H=60 (2.00 LT) | -1 | 0.001/0.00015/1.1e-05/0.00017 | 0.00071/0.01/0.026/0.0014 |
| H=120 (4.00 LT) | -0.2 | 0.0017/0.00028/0.00072/9.5e-05 | 0.00071/0.01/0.026/0.0014 |

### C3. The deployable chain

False trust = P(T <= q_0.1) per (state, draw), target 0.1; T realized (the run's first passage against the noisy truth) or characteristic (moments). Trusted horizon = mean q_0.1 (LT). A4 + KM leaf uses the calibration A4 hybrid's characteristic horizon (no per-draw calibration errors on the full grid).

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| policy | false trust realized [CI] | false trust characteristic [CI] | mean trusted (LT) [CI] | q at cap |
|---|---|---|---|---|
| A2 + constant | 0.0987 [0.0927, 0.105] | 0.106 [0.0965, 0.115] | 1.89 [1.89, 1.89] | 0 |
| A2 + h(F-hat) | 0.13 [0.123, 0.137] | 0.128 [0.119, 0.137] | 2.23 [2.21, 2.25] | 0 |
| A4 + KM leaf | 0.12 [0.114, 0.127] | 0.119 [0.11, 0.128] | 2.12 [2.11, 2.13] | 0 |
| g(F-hat) + h(F-hat) | 0.134 [0.128, 0.141] | 0.126 [0.116, 0.134] | 2.26 [2.24, 2.28] | 0 |

Hybrid MSE ratio to A2 (realized per draw; 1.05 table, R2 guard).

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| policy | H=8 (0.27 LT) | H=15 (0.50 LT) | H=30 (1.00 LT) | H=60 (2.00 LT) | H=120 (4.00 LT) |
|---|---|---|---|---|---|
| A4 + KM leaf | 1.06 [1.04, 1.08] needed, size not determined | 1.07 [1.04, 1.09] needed, size not determined | 1.03 [1.01, 1.06] needed, size not determined | 0.985 [0.965, 1] negligible | 1.05 [1.03, 1.06] needed, size not determined |
| g(F-hat) + h(F-hat) | 0.996 [0.988, 1] negligible | 1 [0.989, 1.02] negligible | 1 [0.984, 1.02] negligible | 0.984 [0.97, 0.997] lowers | 0.987 [0.982, 0.991] lowers |

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| full system minus | false trust realized [CI] | false trust characteristic [CI] | trusted LT [CI] |
|---|---|---|---|
| A2 + constant | 0.0357 [0.0301, 0.0414] | 0.0196 [0.00894, 0.0297] | 0.376 [0.356, 0.394] |
| A2 + h(F-hat) | 0.00444 [0.001, 0.00788] | -0.00269 [-0.00838, 0.00256] | 0.034 [0.03, 0.0378] |
| A4 + KM leaf | 0.0139 [0.00906, 0.019] | 0.00656 [-0.002, 0.0147] | 0.143 [0.132, 0.155] |

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| horizon model (own characteristic target) | pinball / constant's | constant/model ratio [CI] reading | cov 0.1 / 0.5 / 0.9 | C |
|---|---|---|---|---|
| h_A2(F-hat) | 0.107 / 0.153 | 1.43 [1.4, 1.47] substantial | 0.128 / 0.522 / 0.885 | 0.708 |
| h_g(F-hat) | 0.106 / 0.157 | 1.47 [1.43, 1.51] substantial | 0.126 / 0.517 / 0.883 | - |

### E-H2a. Amplification mismatch m(H) (H_0 = 1 LT; both r.m.s. <= 0.5 sigma_x)

Medians by tercile of I (low / mid / high). Spearman(m, I) on the kept states [95%]. B and A columns from the A/D record (oracle).

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| horizon | kept | m | abs drift w* | corr C/sqrt(E_C E_P) | Spearman(m, I) | B RI / OI | A drop-I (MSE) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 3987 | -0.08 / 0.2 / 0.18 | 0.074 / 0.08 / 0.085 | 0.19 / 0.17 / 0.19 | 0.119 [0.0877, 0.149] | no interaction gain detected / no interaction gain detected | negligible |
| H=15 (0.50 LT) | 3987 | -0.1 / 0.17 / 0.099 | 0.082 / 0.074 / 0.051 | 0.18 / 0.17 / 0.2 | 0.1 [0.0687, 0.131] | no interaction gain detected / interaction gain detected | negligible |
| H=30 (1.00 LT) | 3987 | 0 / 0 / 0 | 0 / 0 / 0 | 0.2 / 0.21 / 0.21 | (H_0) | no interaction gain detected / no interaction gain detected | negligible |
| H=60 (2.00 LT) | 3717 | -0.22 / -0.23 / -0.22 | 0.076 / 0.094 / 0.11 | 0.22 / 0.26 / 0.31 | 0.000569 [-0.0305, 0.0324] | interaction gain detected / interaction gain detected | negligible |
| H=120 (4.00 LT) | 2770 | -1.4 / -1.3 / -1.3 | 0.26 / 0.31 / 0.29 | 0.32 / 0.39 / 0.36 | 0.0221 [-0.0127, 0.0577] | interaction gain detected / no interaction gain detected | small |

**Reading: not consistent** (horizons_used: ['60', '120'], horizons_supporting: [], horizons_null: ['60', '120']).

### E-H2e. Library size and error correlation (sweep states)

1000 sweep states. Delta = value at N_lib 100000 minus 1000. corr = the H2e correlation (0 by convention where an error is constant over the draws).

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| rho | valid | corr 0 small / large lib | median corr small -> large | set | median Delta corr [CI] | Spearman(Delta corr, Delta R) [CI] | reading |
|---|---|---|---|---|---|---|---|
| 0.01 | 1000 | 601 / 0 | 0 -> 0.456 | all (1000) | 0.373 [0.355, 0.392] | 0.123 [0.0613, 0.183] | not consistent |
| 0.01 | 1000 | 601 / 0 | 0 -> 0.456 | both_defined (399) | 0.196 [0.168, 0.229] | 0.131 [0.032, 0.228] | not consistent |
| 0.02 | 1000 | 297 / 0 | 0.0784 -> 0.47 | all (1000) | 0.293 [0.271, 0.317] | 0.146 [0.0832, 0.206] | not consistent |
| 0.02 | 1000 | 297 / 0 | 0.0784 -> 0.47 | both_defined (703) | 0.195 [0.163, 0.223] | 0.183 [0.111, 0.253] | not consistent |

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| rho | stratifier | median Delta corr low / mid / high | median Delta R low / mid / high |
|---|---|---|---|
| 0.01 | R | 0.32 / 0.39 / 0.41 | -1.2 / -1.3 / -1.5 |
| 0.01 | O | 0.34 / 0.39 / 0.39 | -1.4 / -1.3 / -1.4 |
| 0.01 | I | 0.35 / 0.35 / 0.43 | -1.3 / -1.3 / -1.4 |
| 0.01 | N | 0.39 / 0.37 / 0.36 | -1.4 / -1.2 / -1.3 |
| 0.01 | delta_R | 0.35 / 0.38 / 0.4 | -2 / -1.3 / -0.45 |
| 0.02 | R | 0.25 / 0.28 / 0.34 | -0.67 / -0.79 / -1 |
| 0.02 | O | 0.27 / 0.3 / 0.31 | -0.79 / -0.81 / -0.85 |
| 0.02 | I | 0.27 / 0.26 / 0.37 | -0.78 / -0.82 / -0.85 |
| 0.02 | N | 0.32 / 0.29 / 0.28 | -0.91 / -0.71 / -0.83 |
| 0.02 | delta_R | 0.27 / 0.26 / 0.34 | -1.4 / -0.82 / -0.025 |

**Reading** (final, after the convention check): rho 0.01: not consistent; rho 0.02: not consistent.

### E-H3c. A5 against A4

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| item | value |
|---|---|
| H3c ratio MSE(A5)/MSE(A4) [CI at level 0.983] (run) | 0.978 [0.955, 1], width 0.0452 |
| top-1% share: A5 loss / A4 loss / abs(A5 - A4) | 0.16 / 0.167 / 0.21 |
| autocorrelation of d = A5 - A4, lags 1..5 | 0.029, -0.012, 0.012, -0.0071, 0.0048 |
| block-5 means: lag-1 autocorrelation, variance ratio | 0.0362, 0.999 |
| K chosen; leaves used test / calibration; largest leaf share test | 8; 8 / 8; 0.211 |
| w*(H_ref) within-leaf share of variance | 0.924 |
| bimodality coefficient R/O/I/N, oracle; deployable | 0.27/0.79/0.44/0.83; 0.52/0.8/0.44/0.91 |
| Spearman pairs (oracle) | RO 0.4, RI -0.044, RN 0.39, OI -0.032, ON 0.031, IN -0.039 |
| top-1% abs(d) states: mean percentile R/O/I/N | 0.74/0.86/0.73/0.57 |
| top-1% abs(d) states: median I pct; share high-I; median abs(x) pct; share sign change in window; share of sum d | 0.803; 0.7; 0.45; 1; 0.566 |

## chua

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| check | result |
|---|---|
| A2 rebuilt on 1..H_max equals the dumped A2 (bitwise); A4 horizon-free | True, True |
| refit reproduces WU-0048 (max abs: A/ROIN MSE oracle, deployable; W/ROIN L_w oracle, deployable) | 0 / 0 / 0 / 0 |
| T_c counts T = 1 / e_(T-1) = theta (A2 train, g train, A2 test, g test, A4 calibration) | 2/0, 10/0, 0/0, 0/0, 4/0 |
| A2 on 1..H_max: pooled curvature floor / columns at 0 or 1 | 0 / 0 |
| weights clipped to [0, 1] | g_oracle_test 2854, g_oracle_train_oof 1767, gw_oracle_test 1942, gw_oracle_train_oof 1340, g_deployable_test 2750, g_deployable_train_oof 2332, gw_deployable_test 1102, gw_deployable_train_oof 961 |

### C1. Separate performance (from the A/D record, no refit)

Allocation: MSE per rule (oracle: moment form; deployable: realized); reading of the rung against F (MSE ratio, 1.05 table, n_eff guard). G(F) = 1 - L_A(F)/L_A(constant).

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| horizon | profile | constant | separation | RO | F (ROIN) | X | X+F | G(F) | sep vs F | RO vs F | X+F vs F |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 0.000628 | 0.0006 | 0.00112 | 0.00105 | 0.000683 | 0.000831 | -3.46 | undetermined | undetermined | undetermined |
| H=8 (0.27 LT) | deployable | 0.000597 | 0.000676 | 0.000603 | 0.000627 | 0.000743 | 0.000661 | -0.336 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | oracle | 0.00267 | 0.00251 | 0.00272 | 0.00317 | 0.00301 | 0.00299 | -0.896 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | deployable | 0.0026 | 0.00279 | 0.00273 | 0.00276 | 0.00321 | 0.00274 | -0.32 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | oracle | 0.016 | 0.0147 | 0.0157 | 0.0164 | 0.017 | 0.0161 | -0.0916 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | deployable | 0.0183 | 0.0179 | 0.0183 | 0.0183 | 0.0187 | 0.018 | -0.00547 | undetermined | undetermined | undetermined |
| H=60 (2.00 LT) | oracle | 0.195 | 0.186 | 0.183 | 0.183 | 0.188 | 0.182 | 0.184 | negligible | negligible | negligible |
| H=60 (2.00 LT) | deployable | 0.196 | 0.197 | 0.189 | 0.187 | 0.187 | 0.185 | 0.14 | needed, size not determined | negligible | negligible |
| H=120 (4.00 LT) | oracle | 0.643 | 0.66 | 0.63 | 0.629 | 0.64 | 0.63 | 0.073 | needed, size not determined | negligible | negligible |
| H=120 (4.00 LT) | deployable | 0.643 | 0.672 | 0.634 | 0.631 | 0.641 | 0.631 | 0.0664 | needed, size not determined | negligible | negligible |

Horizon (Y = ln min(T_c, H_max)): pinball at 0.5 / Harrell's C / coverage of q_0.1 below the cap; reading against F.

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | C | cov q_0.1 | reading vs F |
|---|---|---|---|---|---|
| oracle | none | 0.225 | 0.5 | 0.0988 | substantial |
| oracle | lyapunov | 0.257 | 0.672 | 0.0957 | substantial |
| oracle | RO | 0.199 | 0.64 | 0.11 | substantial |
| oracle | ROIN | 0.159 | 0.722 | 0.113 |  |
| oracle | X | 0.174 | 0.7 | 0.137 | needed, size not determined |
| oracle | X+F | 0.135 | 0.774 | 0.153 | lowers |
| oracle | Lyapunov rank | | 0.671 | | |
| deployable | none | 0.225 | 0.5 | 0.0988 | substantial |
| deployable | lyapunov | 0.259 | 0.67 | 0.0967 | substantial |
| deployable | RO | 0.195 | 0.647 | 0.0949 | substantial |
| deployable | ROIN | 0.158 | 0.726 | 0.134 |  |
| deployable | X | 0.175 | 0.7 | 0.131 | substantial |
| deployable | X+F | 0.135 | 0.772 | 0.144 | lowers |
| deployable | Lyapunov rank | | 0.667 | | |

### C2. Shared information (oracle and deployable profiles)

Skill retained = [L(constant) - L(bottleneck)] / [L(constant) - L(F)]; reading: keeps most (CI > 0.5), loses most (CI < 0.5), else not determined. Forward: horizon from g (five clipped weights; g_w: the L_w fits); reverse: weight from h (three quantiles), scored by L_A (MSE; deployable: realized per draw, R2 guard) and by L_w (weight units, unit-weight fits). Training inputs cross-fitted.

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| profile | direction | horizon | full skill [CI] | retained L_A / pinball [CI] | reading | retained L_w [CI] | reading L_w |
|---|---|---|---|---|---|---|---|
| oracle | forward (g; g_w) | all five | 0.0665 [0.0615, 0.0716] | 0.292 [0.257, 0.329] | loses most | 0.59 [0.551, 0.631] | keeps most |
| oracle | forward, one weight | H=8 (0.27 LT) | | 0.00493 [-0.00324, 0.0132] | loses most | | |
| oracle | forward, one weight | H=15 (0.50 LT) | | 0.0208 [0.00376, 0.0377] | loses most | | |
| oracle | forward, one weight | H=30 (1.00 LT) | | 0.0236 [0.0057, 0.0417] | loses most | | |
| oracle | forward, one weight | H=60 (2.00 LT) | | 0.145 [0.118, 0.175] | loses most | | |
| oracle | forward, one weight | H=120 (4.00 LT) | | 0.093 [0.0653, 0.121] | loses most | | |
| oracle | reverse | H=8 (0.27 LT) | -0.000419 [-0.00135, 6.49e-05] | - [-, -] | not determined (full-profile skill not established) | 0.29 [0.242, 0.344] | loses most |
| oracle | reverse | H=15 (0.50 LT) | -0.000505 [-0.00131, 6.91e-05] | - [-, -] | not determined (full-profile skill not established) | 0.28 [0.236, 0.326] | loses most |
| oracle | reverse | H=30 (1.00 LT) | -0.000458 [-0.00232, 0.00109] | - [-, -] | not determined (full-profile skill not established) | 0.341 [0.283, 0.4] | loses most |
| oracle | reverse | H=60 (2.00 LT) | 0.0125 [0.00892, 0.0159] | 0.378 [0.281, 0.51] | not determined (interval spans 0.5) | 0.403 [0.339, 0.465] | loses most |
| oracle | reverse | H=120 (4.00 LT) | 0.0136 [0.00924, 0.0179] | 0.338 [0.184, 0.531] | not determined (interval spans 0.5) | 0.389 [0.259, 0.545] | not determined (interval spans 0.5) |
| deployable | forward (g; g_w) | all five | 0.0674 [0.0626, 0.0722] | 0.525 [0.484, 0.564] | not determined (interval spans 0.5) | 0.515 [0.476, 0.552] | not determined (interval spans 0.5) |
| deployable | forward, one weight | H=8 (0.27 LT) | | 0.0708 [0.06, 0.0818] | loses most | | |
| deployable | forward, one weight | H=15 (0.50 LT) | | 0.0461 [0.0306, 0.0611] | loses most | | |
| deployable | forward, one weight | H=30 (1.00 LT) | | -0.00105 [-0.00993, 0.00721] | loses most | | |
| deployable | forward, one weight | H=60 (2.00 LT) | | 0.182 [0.155, 0.209] | loses most | | |
| deployable | forward, one weight | H=120 (4.00 LT) | | 0.304 [0.27, 0.339] | loses most | | |
| deployable | reverse | H=8 (0.27 LT) | -3.02e-05 [-5.38e-05, -1.09e-05] | - [-, -] | not determined (full-profile skill not established) | 0.108 [0.0713, 0.15] | loses most |
| deployable | reverse | H=15 (0.50 LT) | -0.000159 [-0.000367, -3.37e-05] | - [-, -] | not determined (full-profile skill not established) | 0.35 [0.283, 0.419] | loses most |
| deployable | reverse | H=30 (1.00 LT) | -3.99e-05 [-0.000571, 0.000461] | - [-, -] | not determined (full-profile skill not established) | 0.43 [0.355, 0.501] | not determined (interval spans 0.5) |
| deployable | reverse | H=60 (2.00 LT) | 0.00972 [0.00589, 0.0136] | 0.6 [0.346, 0.874] | not determined (interval spans 0.5) | 0.581 [0.508, 0.653] | keeps most |
| deployable | reverse | H=120 (4.00 LT) | 0.0124 [0.00746, 0.0175] | 0.463 [0.275, 0.725] | not determined (interval spans 0.5) | 0.539 [0.399, 0.713] | not determined (interval spans 0.5) |

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| profile | forward C-index F / g / g_w | reverse MSE(h)/MSE(F) per horizon | math-spec prediction (both lose most) | largest single-weight retention at H |
|---|---|---|---|---|
| oracle | 0.722 / 0.619 / 0.68 | H=8 (0.27 LT) 1.01 [0.96, 1.1] undetermined (n_eff < 50); H=15 (0.50 LT) 0.965 [0.784, 1.11] undetermined (n_eff < 50); H=30 (1.00 LT) 0.987 [0.909, 1.06] undetermined (n_eff < 50); H=60 (2.00 LT) 1.04 [1.03, 1.06] needed, size not determined; H=120 (4.00 LT) 1.01 [1.01, 1.02] small | **consistent** | 60 |
| deployable | 0.726 / 0.656 / 0.671 | H=8 (0.27 LT) 1.02 [0.98, 1.08] undetermined (n_eff < 50); H=15 (0.50 LT) 0.985 [0.918, 1.04] undetermined (n_eff < 50); H=30 (1.00 LT) 0.994 [0.968, 1.02] undetermined (n_eff < 50); H=60 (2.00 LT) 1.02 [1, 1.04] small; H=120 (4.00 LT) 1.01 [1, 1.02] small | **not determined** | 120 |

Oracle against deployable: retained (deployable) minus retained (oracle), paired 95% interval.

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| row | oracle | deployable | difference [CI] | reading |
|---|---|---|---|---|
| forward | 0.292 | 0.525 | 0.232 [0.188, 0.275] | deployable retains more |
| forward_w | 0.59 | 0.515 | -0.0752 [-0.124, -0.0288] | deployable retains less |
| reverse/8 | - | - | - [-, -] | not determined (full-profile skill not established) |
| reverse_w/8 | 0.29 | 0.108 | -0.182 [-0.244, -0.122] | deployable retains less |
| reverse/15 | - | - | - [-, -] | not determined (full-profile skill not established) |
| reverse_w/15 | 0.28 | 0.35 | 0.0699 [-0.00413, 0.146] | no difference detected |
| reverse/30 | - | - | - [-, -] | not determined (full-profile skill not established) |
| reverse_w/30 | 0.341 | 0.43 | 0.0888 [0.0228, 0.154] | deployable retains more |
| reverse/60 | 0.378 | 0.6 | 0.222 [-0.0509, 0.481] | no difference detected |
| reverse_w/60 | 0.403 | 0.581 | 0.178 [0.106, 0.252] | deployable retains more |
| reverse/120 | 0.338 | 0.463 | 0.125 [-0.0775, 0.384] | no difference detected |
| reverse_w/120 | 0.389 | 0.539 | 0.15 [-0.00277, 0.321] | no difference detected |

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| horizon | Spearman(phi allocation, phi horizon) (4 items, descriptive) | phi_alloc R/O/I/N | phi_horizon R/O/I/N |
|---|---|---|---|
| H=8 (0.27 LT) | -0.4 | 9.7e-06/-0.0004/-7.2e-06/-2.4e-05 | 0.0024/0.016/0.045/0.0025 |
| H=15 (0.50 LT) | -0.8 | 8.8e-05/-0.0003/-0.00023/-6.6e-05 | 0.0024/0.016/0.045/0.0025 |
| H=30 (1.00 LT) | 0.4 | -0.00048/0.00022/-0.0001/-9.9e-05 | 0.0024/0.016/0.045/0.0025 |
| H=60 (2.00 LT) | -0.4 | 0.0065/0.0042/0.00093/0.0009 | 0.0024/0.016/0.045/0.0025 |
| H=120 (4.00 LT) | -0.2 | 0.0072/0.002/0.003/0.0014 | 0.0024/0.016/0.045/0.0025 |

### C3. The deployable chain

False trust = P(T <= q_0.1) per (state, draw), target 0.1; T realized (the run's first passage against the noisy truth) or characteristic (moments). Trusted horizon = mean q_0.1 (LT). A4 + KM leaf uses the calibration A4 hybrid's characteristic horizon (no per-draw calibration errors on the full grid).

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| policy | false trust realized [CI] | false trust characteristic [CI] | mean trusted (LT) [CI] | q at cap |
|---|---|---|---|---|
| A2 + constant | 0.0791 [0.0732, 0.0855] | 0.102 [0.0927, 0.111] | 0.971 [0.971, 0.971] | 0 |
| A2 + h(F-hat) | 0.106 [0.0993, 0.113] | 0.123 [0.113, 0.132] | 1.41 [1.4, 1.43] | 0 |
| A4 + KM leaf | 0.0724 [0.0664, 0.0781] | 0.101 [0.0922, 0.11] | 1.21 [1.2, 1.22] | 0 |
| g(F-hat) + h(F-hat) | 0.104 [0.0979, 0.11] | 0.125 [0.116, 0.133] | 1.45 [1.44, 1.47] | 0 |

Hybrid MSE ratio to A2 (realized per draw; 1.05 table, R2 guard).

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| policy | H=8 (0.27 LT) | H=15 (0.50 LT) | H=30 (1.00 LT) | H=60 (2.00 LT) | H=120 (4.00 LT) |
|---|---|---|---|---|---|
| A4 + KM leaf | 1.13 [1.09, 1.17] undetermined (n_eff < 50) | 1.08 [1.03, 1.14] needed, size not determined | 0.981 [0.954, 1.01] undetermined (n_eff < 50) | 1 [0.987, 1.02] negligible | 1.04 [1.03, 1.06] needed, size not determined |
| g(F-hat) + h(F-hat) | 1.05 [1.02, 1.09] undetermined (n_eff < 50) | 1.07 [1.02, 1.15] needed, size not determined | 1 [0.976, 1.03] undetermined (n_eff < 50) | 0.95 [0.931, 0.97] lowers | 0.981 [0.973, 0.988] lowers |

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| full system minus | false trust realized [CI] | false trust characteristic [CI] | trusted LT [CI] |
|---|---|---|---|
| A2 + constant | 0.0249 [0.0183, 0.0313] | 0.0236 [0.0129, 0.0335] | 0.482 [0.466, 0.498] |
| A2 + h(F-hat) | -0.002 [-0.00594, 0.00175] | 0.00231 [-0.00263, 0.00713] | 0.039 [0.0349, 0.0434] |
| A4 + KM leaf | 0.0316 [0.0264, 0.0366] | 0.024 [0.016, 0.0322] | 0.245 [0.233, 0.257] |

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| horizon model (own characteristic target) | pinball / constant's | constant/model ratio [CI] reading | cov 0.1 / 0.5 / 0.9 | C |
|---|---|---|---|---|
| h_A2(F-hat) | 0.152 / 0.234 | 1.54 [1.5, 1.58] substantial | 0.123 / 0.51 / 0.888 | 0.741 |
| h_g(F-hat) | 0.153 / 0.233 | 1.52 [1.48, 1.56] substantial | 0.125 / 0.493 / 0.881 | - |

### E-H2a. Amplification mismatch m(H) (H_0 = 1 LT; both r.m.s. <= 0.5 sigma_x)

Medians by tercile of I (low / mid / high). Spearman(m, I) on the kept states [95%]. B and A columns from the A/D record (oracle).

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| horizon | kept | m | abs drift w* | corr C/sqrt(E_C E_P) | Spearman(m, I) | B RI / OI | A drop-I (MSE) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 3688 | -0.12 / 0.27 / 0.4 | 0.053 / 0.082 / 0.12 | 0.17 / 0.16 / 0.25 | 0.17 [0.139, 0.203] | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=15 (0.50 LT) | 3679 | 0.016 / 0.023 / 0.17 | 0.053 / 0.1 / 0.11 | 0.18 / 0.18 / 0.26 | 0.11 [0.0783, 0.142] | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=30 (1.00 LT) | 3693 | 0 / 0 / 0 | 0 / 0 / 0 | 0.18 / 0.2 / 0.27 | (H_0) | no interaction gain detected / interaction gain detected | undetermined (n_eff < 50) |
| H=60 (2.00 LT) | 2630 | -0.36 / -0.53 / -0.26 | 0.062 / 0.12 / 0.094 | 0.22 / 0.2 / 0.28 | -0.00371 [-0.0401, 0.0365] | interaction gain detected / interaction gain detected | negligible |
| H=120 (4.00 LT) | 1036 | -1.4 / -1.3 / -1.2 | 0.21 / 0.22 / 0.22 | 0.3 / 0.27 / 0.36 | 0.00827 [-0.0563, 0.0725] | no interaction gain detected / no interaction gain detected | small |

**Reading: not consistent** (horizons_used: ['60', '120'], horizons_supporting: [], horizons_null: ['60', '120']).

### E-H2e. Library size and error correlation (sweep states)

1000 sweep states. Delta = value at N_lib 100000 minus 1000. corr = the H2e correlation (0 by convention where an error is constant over the draws).

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| rho | valid | corr 0 small / large lib | median corr small -> large | set | median Delta corr [CI] | Spearman(Delta corr, Delta R) [CI] | reading |
|---|---|---|---|---|---|---|---|
| 0.01 | 1000 | 528 / 15 | 0 -> 0.418 | all (1000) | 0.321 [0.297, 0.347] | 0.0166 [-0.0468, 0.081] | not determined |
| 0.01 | 1000 | 528 / 15 | 0 -> 0.418 | both_defined (468) | 0.195 [0.164, 0.226] | 0.0224 [-0.0654, 0.115] | not determined |
| 0.02 | 1000 | 273 / 6 | 0.0605 -> 0.399 | all (1000) | 0.234 [0.204, 0.268] | -0.0592 [-0.122, 0.00525] | not determined |
| 0.02 | 1000 | 273 / 6 | 0.0605 -> 0.399 | both_defined (725) | 0.181 [0.151, 0.204] | -0.054 [-0.13, 0.0216] | not determined |

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| rho | stratifier | median Delta corr low / mid / high | median Delta R low / mid / high |
|---|---|---|---|
| 0.01 | R | 0.3 / 0.33 / 0.34 | -1.3 / -1.1 / -1.6 |
| 0.01 | O | 0.34 / 0.3 / 0.32 | -1.6 / -1.3 / -1.1 |
| 0.01 | I | 0.3 / 0.27 / 0.37 | -1.3 / -1.5 / -1.2 |
| 0.01 | N | 0.29 / 0.33 / 0.35 | -1.6 / -1 / -1.4 |
| 0.01 | delta_R | 0.31 / 0.33 / 0.32 | -2.1 / -1.3 / -0.5 |
| 0.02 | R | 0.2 / 0.23 / 0.28 | -0.79 / -0.68 / -1 |
| 0.02 | O | 0.27 / 0.22 / 0.23 | -1.1 / -0.76 / -0.65 |
| 0.02 | I | 0.22 / 0.16 / 0.31 | -0.89 / -0.89 / -0.77 |
| 0.02 | N | 0.26 / 0.2 / 0.26 | -1 / -0.57 / -0.89 |
| 0.02 | delta_R | 0.26 / 0.23 / 0.21 | -1.6 / -0.83 / -0.11 |

**Reading** (final, after the convention check): rho 0.01: not determined; rho 0.02: not determined.

### E-H3c. A5 against A4

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| item | value |
|---|---|
| H3c ratio MSE(A5)/MSE(A4) [CI at level 0.983] (run) | 1.01 [0.98, 1.05], width 0.0664 |
| top-1% share: A5 loss / A4 loss / abs(A5 - A4) | 0.627 / 0.609 / 0.436 |
| autocorrelation of d = A5 - A4, lags 1..5 | 0.0094, 0.0064, 0.0092, -0.017, -0.00046 |
| block-5 means: lag-1 autocorrelation, variance ratio | 0.00254, 1 |
| K chosen; leaves used test / calibration; largest leaf share test | 2; 2 / 2; 0.761 |
| w*(H_ref) within-leaf share of variance | 0.977 |
| bimodality coefficient R/O/I/N, oracle; deployable | 0.22/0.19/0.45/0.84; 0.33/0.45/0.46/0.89 |
| Spearman pairs (oracle) | RO 0.065, RI -4.4e-05, RN 0.37, OI 0.35, ON 0.079, IN 0.047 |
| top-1% abs(d) states: mean percentile R/O/I/N | 0.47/0.66/0.9/0.4 |
| top-1% abs(d) states: median I pct; share high-I; median abs(x) pct; share sign change in window; share of sum d | 0.947; 0.975; 0.555; 0.05; 0.918 |

## E-H3c reading (this seed)

PHASE J CONFIRMATORY (CONF-8): pre-registered analysis, UNPROMOTED.

| item | value |
|---|---|
| H3c interval widths | lorenz63 0.158, rossler 0.0452, chua 0.0664 |
| pattern (Lorenz-63 widest, Rössler narrowest) reproduced | True |
| Lorenz-63 part (top-1% share of sum abs(d) 0.644, median I percentile 0.266) | not consistent |
| Rössler part (BC deployable: R 0.517, O 0.798, I 0.444, N 0.908) | not consistent |
| **reading** | **not consistent** |

