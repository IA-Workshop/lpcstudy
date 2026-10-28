# Phase J experiments C and E: CONF-5

**PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.** Run `phasej-CONF-5/phasej`; analysis commit `c19ad486b93a2ee96d64ce069ec42fd440428211` (dirty: False); A/D record `phasej-CONF-5/contrib-j/contrib.json`. Estimates with 95% intervals from the shared moving-block index sets (models fixed; training variance not included). Readings are descriptive; no causal claim; nothing here is set beside CONF-1.

## lorenz63

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| check | result |
|---|---|
| A2 rebuilt on 1..H_max equals the dumped A2 (bitwise); A4 horizon-free | True, True |
| refit reproduces WU-0048 (max abs: A/ROIN MSE oracle, deployable; W/ROIN L_w oracle, deployable) | 0 / 0 / 0 / 0 |
| T_c counts T = 1 / e_(T-1) = theta (A2 train, g train, A2 test, g test, A4 calibration) | 15/0, 90/0, 34/0, 111/0, 104/0 |
| A2 on 1..H_max: pooled curvature floor / columns at 0 or 1 | 0 / 0 |
| weights clipped to [0, 1] | g_oracle_test 2495, g_oracle_train_oof 2571, gw_oracle_test 2633, gw_oracle_train_oof 2361, g_deployable_test 5271, g_deployable_train_oof 5251, gw_deployable_test 3430, gw_deployable_train_oof 2682 |

### C1. Separate performance (from the A/D record, no refit)

Allocation: MSE per rule (oracle: moment form; deployable: realized); reading of the rung against F (MSE ratio, 1.05 table, n_eff guard). G(F) = 1 - L_A(F)/L_A(constant).

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| horizon | profile | constant | separation | RO | F (ROIN) | X | X+F | G(F) | sep vs F | RO vs F | X+F vs F |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 0.0155 | 0.00484 | 0.00487 | 0.00492 | 0.00496 | 0.00483 | 0.769 | undetermined | undetermined | undetermined |
| H=8 (0.27 LT) | deployable | 0.0154 | 0.0342 | 0.0109 | 0.0112 | 0.00494 | 0.00575 | 0.311 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | oracle | 0.0282 | 0.0103 | 0.00965 | 0.0092 | 0.0124 | 0.00987 | 0.924 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | deployable | 0.0302 | 0.0416 | 0.0266 | 0.0197 | 0.0135 | 0.0158 | 0.465 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | oracle | 0.0532 | 0.0315 | 0.0359 | 0.0301 | 0.0363 | 0.0346 | 0.758 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | deployable | 0.0551 | 0.0645 | 0.0505 | 0.0436 | 0.039 | 0.0403 | 0.355 | undetermined | undetermined | undetermined |
| H=60 (2.00 LT) | oracle | 0.138 | 0.123 | 0.123 | 0.119 | 0.123 | 0.119 | 0.333 | undetermined | needed, size not determined | negligible |
| H=60 (2.00 LT) | deployable | 0.138 | 0.143 | 0.137 | 0.131 | 0.122 | 0.121 | 0.128 | needed, size not determined | needed, size not determined | lowers |
| H=120 (4.00 LT) | oracle | 0.883 | 0.933 | 0.873 | 0.871 | 0.874 | 0.867 | 0.0463 | substantial | negligible | negligible |
| H=120 (4.00 LT) | deployable | 0.873 | 0.921 | 0.87 | 0.869 | 0.861 | 0.861 | 0.015 | needed, size not determined | negligible | negligible |

Horizon (Y = ln min(T_c, H_max)): pinball at 0.5 / Harrell's C / coverage of q_0.1 below the cap; reading against F.

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | C | cov q_0.1 | reading vs F |
|---|---|---|---|---|---|
| oracle | none | 0.19 | 0.5 | 0.089 | substantial |
| oracle | lyapunov | 0.3 | 0.612 | 0.0758 | substantial |
| oracle | RO | 0.184 | 0.58 | 0.115 | substantial |
| oracle | ROIN | 0.149 | 0.686 | 0.141 |  |
| oracle | X | 0.156 | 0.673 | 0.141 | undetermined |
| oracle | X+F | 0.13 | 0.736 | 0.144 | lowers |
| oracle | Lyapunov rank | | 0.609 | | |
| deployable | none | 0.19 | 0.5 | 0.089 | substantial |
| deployable | lyapunov | 0.298 | 0.609 | 0.0768 | substantial |
| deployable | RO | 0.185 | 0.569 | 0.0937 | substantial |
| deployable | ROIN | 0.15 | 0.677 | 0.129 |  |
| deployable | X | 0.157 | 0.675 | 0.136 | undetermined |
| deployable | X+F | 0.132 | 0.723 | 0.147 | lowers |
| deployable | Lyapunov rank | | 0.612 | | |

### C2. Shared information (oracle and deployable profiles)

Skill retained = [L(constant) - L(bottleneck)] / [L(constant) - L(F)]; reading: keeps most (CI > 0.5), loses most (CI < 0.5), else not determined. Forward: horizon from g (five clipped weights; g_w: the L_w fits); reverse: weight from h (three quantiles), scored by L_A (MSE; deployable: realized per draw, R2 guard) and by L_w (weight units, unit-weight fits). Training inputs cross-fitted.

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| profile | direction | horizon | full skill [CI] | retained L_A / pinball [CI] | reading | retained L_w [CI] | reading L_w |
|---|---|---|---|---|---|---|---|
| oracle | forward (g; g_w) | all five | 0.0406 [0.0359, 0.0452] | 0.134 [0.0955, 0.17] | loses most | 0.385 [0.326, 0.447] | loses most |
| oracle | forward, one weight | H=8 (0.27 LT) | | -0.014 [-0.0348, 0.00774] | loses most | | |
| oracle | forward, one weight | H=15 (0.50 LT) | | -0.0311 [-0.0534, -0.0115] | loses most | | |
| oracle | forward, one weight | H=30 (1.00 LT) | | 0.0126 [-0.00616, 0.0308] | loses most | | |
| oracle | forward, one weight | H=60 (2.00 LT) | | 0.00388 [-0.00822, 0.0164] | loses most | | |
| oracle | forward, one weight | H=120 (4.00 LT) | | 0.083 [0.0597, 0.108] | loses most | | |
| oracle | reverse | H=8 (0.27 LT) | 0.0106 [0.00642, 0.0142] | 0.328 [-0.132, 0.65] | not determined (n_eff < 50) | 0.0993 [0.0692, 0.128] | loses most |
| oracle | reverse | H=15 (0.50 LT) | 0.019 [0.0149, 0.023] | 0.378 [0.245, 0.505] | not determined (n_eff < 50) | 0.106 [0.0881, 0.122] | loses most |
| oracle | reverse | H=30 (1.00 LT) | 0.0231 [0.0181, 0.0285] | 0.618 [0.495, 0.745] | not determined (n_eff < 50) | 0.148 [0.114, 0.18] | loses most |
| oracle | reverse | H=60 (2.00 LT) | 0.0191 [0.0106, 0.0263] | 0.131 [0.00513, 0.262] | loses most | 0.083 [0.059, 0.105] | loses most |
| oracle | reverse | H=120 (4.00 LT) | 0.0121 [0.00388, 0.0205] | 0.183 [-0.117, 0.627] | not determined (interval spans 0.5) | 0.149 [0.0801, 0.228] | loses most |
| deployable | forward (g; g_w) | all five | 0.0402 [0.0355, 0.0448] | 0.132 [0.104, 0.159] | loses most | 0.435 [0.383, 0.484] | loses most |
| deployable | forward, one weight | H=8 (0.27 LT) | | 0.0394 [0.0187, 0.0602] | loses most | | |
| deployable | forward, one weight | H=15 (0.50 LT) | | 0.0721 [0.0499, 0.0942] | loses most | | |
| deployable | forward, one weight | H=30 (1.00 LT) | | 0.0566 [0.0363, 0.0749] | loses most | | |
| deployable | forward, one weight | H=60 (2.00 LT) | | -0.0022 [-0.0142, 0.0105] | loses most | | |
| deployable | forward, one weight | H=120 (4.00 LT) | | 0.0819 [0.0574, 0.106] | loses most | | |
| deployable | reverse | H=8 (0.27 LT) | 0.00424 [0.000253, 0.00772] | 0.334 [-0.267, 6.02] | not determined (n_eff < 50) | 0.215 [0.164, 0.264] | loses most |
| deployable | reverse | H=15 (0.50 LT) | 0.0105 [0.0067, 0.0142] | 0.0151 [-0.463, 0.326] | not determined (n_eff < 50) | 0.31 [0.243, 0.376] | loses most |
| deployable | reverse | H=30 (1.00 LT) | 0.0115 [0.00451, 0.0181] | 0.444 [0.122, 1.08] | not determined (n_eff < 50) | 0.307 [0.233, 0.377] | loses most |
| deployable | reverse | H=60 (2.00 LT) | 0.0073 [0.00285, 0.012] | 0.553 [0.322, 1.18] | not determined (interval spans 0.5) | 0.237 [0.171, 0.301] | loses most |
| deployable | reverse | H=120 (4.00 LT) | 0.00378 [-0.000527, 0.00806] | 1.68 [-, -] | not determined (full-profile skill not established) | 0.399 [0.247, 0.554] | not determined (interval spans 0.5) |

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| profile | forward C-index F / g / g_w | reverse MSE(h)/MSE(F) per horizon | math-spec prediction (both lose most) | largest single-weight retention at H |
|---|---|---|---|---|
| oracle | 0.686 / 0.583 / 0.614 | H=8 (0.27 LT) 2.45 [1.37, 12.8] undetermined (n_eff < 50); H=15 (0.50 LT) 2.28 [1.81, 2.93] undetermined (n_eff < 50); H=30 (1.00 LT) 1.29 [1.16, 1.46] undetermined (n_eff < 50); H=60 (2.00 LT) 1.14 [1.07, 1.2] substantial; H=120 (4.00 LT) 1.01 [1, 1.02] small | **consistent** | 120 |
| deployable | 0.677 / 0.583 / 0.618 | H=8 (0.27 LT) 1.25 [0.891, 2.04] undetermined (n_eff < 50); H=15 (0.50 LT) 1.52 [1.34, 1.75] undetermined (n_eff < 50); H=30 (1.00 LT) 1.15 [0.99, 1.31] undetermined (n_eff < 50); H=60 (2.00 LT) 1.02 [0.995, 1.05] undetermined; H=120 (4.00 LT) 0.997 [0.993, 1] negligible | **consistent** | 120 |

Oracle against deployable: retained (deployable) minus retained (oracle), paired 95% interval.

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| row | oracle | deployable | difference [CI] | reading |
|---|---|---|---|---|
| forward | 0.134 | 0.132 | -0.00215 [-0.0384, 0.0356] | no difference detected |
| forward_w | 0.385 | 0.435 | 0.0499 [-0.0267, 0.119] | no difference detected |
| reverse/8 | 0.328 | 0.334 | 0.00604 [-0.783, 6.06] | not determined (n_eff < 50) |
| reverse_w/8 | 0.0993 | 0.215 | 0.115 [0.0649, 0.164] | deployable retains more |
| reverse/15 | 0.378 | 0.0151 | -0.363 [-0.846, -0.00827] | not determined (n_eff < 50) |
| reverse_w/15 | 0.106 | 0.31 | 0.204 [0.141, 0.267] | deployable retains more |
| reverse/30 | 0.618 | 0.444 | -0.174 [-0.481, 0.45] | not determined (n_eff < 50) |
| reverse_w/30 | 0.148 | 0.307 | 0.159 [0.0878, 0.227] | deployable retains more |
| reverse/60 | 0.131 | 0.553 | 0.422 [0.158, 1.08] | deployable retains more |
| reverse_w/60 | 0.083 | 0.237 | 0.154 [0.0947, 0.215] | deployable retains more |
| reverse/120 | 0.183 | 1.68 | 1.5 [-, -] | not determined (full-profile skill not established) |
| reverse_w/120 | 0.149 | 0.399 | 0.25 [0.114, 0.382] | deployable retains more |

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| horizon | Spearman(phi allocation, phi horizon) (4 items, descriptive) | phi_alloc R/O/I/N | phi_horizon R/O/I/N |
|---|---|---|---|
| H=8 (0.27 LT) | 0.6 | -0.0006/0.0082/0.0034/-0.00037 | 0.0023/0.0097/0.027/0.0016 |
| H=15 (0.50 LT) | 0.8 | 0.0018/0.011/0.0044/0.0017 | 0.0023/0.0097/0.027/0.0016 |
| H=30 (1.00 LT) | 0.6 | 0.0014/0.0091/0.0089/0.0037 | 0.0023/0.0097/0.027/0.0016 |
| H=60 (2.00 LT) | 0.4 | 0.0035/0.01/0.003/0.0024 | 0.0023/0.0097/0.027/0.0016 |
| H=120 (4.00 LT) | 0.2 | 0.0061/0.0048/0.002/-0.0008 | 0.0023/0.0097/0.027/0.0016 |

### C3. The deployable chain

False trust = P(T <= q_0.1) per (state, draw), target 0.1; T realized (the run's first passage against the noisy truth) or characteristic (moments). Trusted horizon = mean q_0.1 (LT). A4 + KM leaf uses the calibration A4 hybrid's characteristic horizon (no per-draw calibration errors on the full grid).

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| policy | false trust realized [CI] | false trust characteristic [CI] | mean trusted (LT) [CI] | q at cap |
|---|---|---|---|---|
| A2 + constant | 0.0651 [0.059, 0.0711] | 0.09 [0.082, 0.0983] | 0.563 [0.563, 0.563] | 0 |
| A2 + h(F-hat) | 0.101 [0.094, 0.107] | 0.122 [0.113, 0.131] | 1.07 [1.05, 1.08] | 0 |
| A4 + KM leaf | 0.0699 [0.0645, 0.0754] | 0.0985 [0.0902, 0.107] | 0.944 [0.933, 0.955] | 0 |
| g(F-hat) + h(F-hat) | 0.0979 [0.0911, 0.105] | 0.114 [0.106, 0.123] | 1.14 [1.13, 1.15] | 0 |

Hybrid MSE ratio to A2 (realized per draw; 1.05 table, R2 guard).

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| policy | H=8 (0.27 LT) | H=15 (0.50 LT) | H=30 (1.00 LT) | H=60 (2.00 LT) | H=120 (4.00 LT) |
|---|---|---|---|---|---|
| A4 + KM leaf | 2.16 [1.71, 2.61] substantial | 1.37 [1.23, 1.51] substantial | 1.17 [1.1, 1.24] substantial | 1.04 [1.02, 1.05] needed, size not determined | 1.06 [1.04, 1.07] needed, size not determined |
| g(F-hat) + h(F-hat) | 0.704 [0.424, 0.965] lowers | 0.652 [0.546, 0.762] lowers | 0.79 [0.682, 0.916] lowers | 0.947 [0.917, 0.98] lowers | 0.996 [0.991, 1] negligible |

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| full system minus | false trust realized [CI] | false trust characteristic [CI] | trusted LT [CI] |
|---|---|---|---|
| A2 + constant | 0.0328 [0.0256, 0.0395] | 0.0244 [0.0156, 0.0333] | 0.577 [0.565, 0.59] |
| A2 + h(F-hat) | -0.00269 [-0.00813, 0.00263] | -0.008 [-0.0152, -0.000937] | 0.0728 [0.0648, 0.0812] |
| A4 + KM leaf | 0.0279 [0.0217, 0.0338] | 0.0159 [0.00725, 0.0243] | 0.196 [0.182, 0.211] |

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| horizon model (own characteristic target) | pinball / constant's | constant/model ratio [CI] reading | cov 0.1 / 0.5 / 0.9 | C |
|---|---|---|---|---|
| h_A2(F-hat) | 0.194 / 0.258 | 1.33 [1.29, 1.37] substantial | 0.122 / 0.505 / 0.877 | 0.687 |
| h_g(F-hat) | 0.176 / 0.222 | 1.27 [1.23, 1.31] substantial | 0.114 / 0.506 / 0.879 | - |

### E-H2a. Amplification mismatch m(H) (H_0 = 1 LT; both r.m.s. <= 0.5 sigma_x)

Medians by tercile of I (low / mid / high). Spearman(m, I) on the kept states [95%]. B and A columns from the A/D record (oracle).

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| horizon | kept | m | abs drift w* | corr C/sqrt(E_C E_P) | Spearman(m, I) | B RI / OI | A drop-I (MSE) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 3581 | -0.11 / 0.069 / 0.15 | 0.046 / 0.035 / 0.07 | 0.11 / 0.13 / 0.14 | 0.088 [0.0545, 0.123] | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=15 (0.50 LT) | 3535 | -0.033 / 0.055 / 0.08 | 0.047 / 0.039 / 0.067 | 0.11 / 0.15 / 0.14 | 0.048 [0.0144, 0.0832] | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=30 (1.00 LT) | 3620 | 0 / 0 / 0 | 0 / 0 / 0 | 0.12 / 0.17 / 0.17 | (H_0) | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=60 (2.00 LT) | 2834 | -0.25 / -0.092 / 0.0072 | 0.068 / 0.075 / 0.083 | 0.14 / 0.2 / 0.17 | 0.0478 [0.0103, 0.0853] | no interaction gain detected / interaction gain detected | small |
| H=120 (4.00 LT) | 654 | -1.5 / -2.8 / -2.7 | 0.3 / 0.47 / 0.47 | 0.27 / 0.34 / 0.3 | -0.121 [-0.193, -0.0429] | interaction gain detected / no interaction gain detected | small |

**Reading: not determined** (horizons_used: ['60', '120'], horizons_supporting: [], horizons_null: ['60']).

### E-H2e. Library size and error correlation (sweep states)

1000 sweep states. Delta = value at N_lib 100000 minus 1000. corr = the H2e correlation (0 by convention where an error is constant over the draws).

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| rho | valid | corr 0 small / large lib | median corr small -> large | set | median Delta corr [CI] | Spearman(Delta corr, Delta R) [CI] | reading |
|---|---|---|---|---|---|---|---|
| 0.01 | 1000 | 731 / 22 | 0 -> 0.425 | all (1000) | 0.387 [0.371, 0.406] | 0.147 [0.0951, 0.213] | not consistent |
| 0.01 | 1000 | 731 / 22 | 0 -> 0.425 | both_defined (265) | 0.243 [0.172, 0.345] | 0.00776 [-0.104, 0.117] | not determined |
| 0.02 | 1000 | 493 / 1 | 0 -> 0.446 | all (1000) | 0.354 [0.328, 0.382] | 0.0191 [-0.0341, 0.0831] | not determined |
| 0.02 | 1000 | 493 / 1 | 0 -> 0.446 | both_defined (507) | 0.219 [0.195, 0.258] | -0.0456 [-0.132, 0.0444] | not determined |

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| rho | stratifier | median Delta corr low / mid / high | median Delta R low / mid / high |
|---|---|---|---|
| 0.01 | R | 0.39 / 0.4 / 0.37 | -1.9 / -1.7 / -1.8 |
| 0.01 | O | 0.4 / 0.41 / 0.34 | -1.8 / -1.8 / -1.7 |
| 0.01 | I | 0.35 / 0.41 / 0.41 | -2 / -1.6 / -1.7 |
| 0.01 | N | 0.36 / 0.43 / 0.38 | -1.9 / -1.7 / -1.7 |
| 0.01 | delta_R | 0.34 / 0.38 / 0.44 | -2.8 / -1.8 / -0.77 |
| 0.02 | R | 0.36 / 0.34 / 0.35 | -1.3 / -1.2 / -1.3 |
| 0.02 | O | 0.38 / 0.39 / 0.31 | -1.3 / -1.3 / -1.2 |
| 0.02 | I | 0.33 / 0.34 / 0.38 | -1.5 / -1.1 / -1.2 |
| 0.02 | N | 0.32 / 0.38 / 0.37 | -1.4 / -1.2 / -1.3 |
| 0.02 | delta_R | 0.36 / 0.37 / 0.33 | -2.2 / -1.3 / -0.3 |

**Reading** (final, after the convention check): rho 0.01: not determined (depends on the zero-variance convention); rho 0.02: not determined.

### E-H3c. A5 against A4

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| item | value |
|---|---|
| H3c ratio MSE(A5)/MSE(A4) [CI at level 0.983] (run) | 0.789 [0.686, 0.908], width 0.223 |
| top-1% share: A5 loss / A4 loss / abs(A5 - A4) | 0.591 / 0.614 / 0.615 |
| autocorrelation of d = A5 - A4, lags 1..5 | 0.017, -0.0037, 0.0022, -0.0035, 0.012 |
| block-5 means: lag-1 autocorrelation, variance ratio | 0.061, 1.01 |
| K chosen; leaves used test / calibration; largest leaf share test | 5; 5 / 5; 0.27 |
| w*(H_ref) within-leaf share of variance | 0.924 |
| bimodality coefficient R/O/I/N, oracle; deployable | 0.26/0.77/0.53/0.83; 0.31/0.4/0.52/0.9 |
| Spearman pairs (oracle) | RO 0.51, RI -0.034, RN 0.33, OI 0.0099, ON -0.044, IN 0.062 |
| top-1% abs(d) states: mean percentile R/O/I/N | 0.75/0.86/0.36/0.34 |
| top-1% abs(d) states: median I pct; share high-I; median abs(x) pct; share sign change in window; share of sum d | 0.21; 0.15; 0.316; 0.875; 0.871 |

## rossler

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| check | result |
|---|---|
| A2 rebuilt on 1..H_max equals the dumped A2 (bitwise); A4 horizon-free | True, True |
| refit reproduces WU-0048 (max abs: A/ROIN MSE oracle, deployable; W/ROIN L_w oracle, deployable) | 0 / 0 / 0 / 0 |
| T_c counts T = 1 / e_(T-1) = theta (A2 train, g train, A2 test, g test, A4 calibration) | 0/0, 0/0, 0/0, 0/0, 0/0 |
| A2 on 1..H_max: pooled curvature floor / columns at 0 or 1 | 0 / 0 |
| weights clipped to [0, 1] | g_oracle_test 3995, g_oracle_train_oof 3081, gw_oracle_test 2002, gw_oracle_train_oof 1641, g_deployable_test 10562, g_deployable_train_oof 7894, gw_deployable_test 1626, gw_deployable_train_oof 1360 |

### C1. Separate performance (from the A/D record, no refit)

Allocation: MSE per rule (oracle: moment form; deployable: realized); reading of the rung against F (MSE ratio, 1.05 table, n_eff guard). G(F) = 1 - L_A(F)/L_A(constant).

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| horizon | profile | constant | separation | RO | F (ROIN) | X | X+F | G(F) | sep vs F | RO vs F | X+F vs F |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 0.000125 | 0.000124 | 0.000117 | 0.000116 | 0.000125 | 0.000115 | 0.457 | substantial | small | negligible |
| H=8 (0.27 LT) | deployable | 0.000125 | 0.000136 | 0.000125 | 0.000125 | 0.000124 | 0.000124 | -0.0201 | substantial | negligible | negligible |
| H=15 (0.50 LT) | oracle | 0.00023 | 0.00022 | 0.00021 | 0.000208 | 0.00023 | 0.000208 | 0.537 | needed, size not determined | small | negligible |
| H=15 (0.50 LT) | deployable | 0.000227 | 0.000244 | 0.000228 | 0.000228 | 0.000227 | 0.000227 | -0.033 | needed, size not determined | negligible | negligible |
| H=30 (1.00 LT) | oracle | 0.000782 | 0.000712 | 0.000693 | 0.000689 | 0.000784 | 0.00069 | 0.599 | small | negligible | negligible |
| H=30 (1.00 LT) | deployable | 0.000789 | 0.00083 | 0.000793 | 0.000793 | 0.000789 | 0.000786 | -0.0241 | needed, size not determined | negligible | negligible |
| H=60 (2.00 LT) | oracle | 0.013 | 0.0117 | 0.0118 | 0.0118 | 0.013 | 0.0118 | 0.305 | negligible | negligible | negligible |
| H=60 (2.00 LT) | deployable | 0.0134 | 0.0134 | 0.0132 | 0.0132 | 0.0133 | 0.0133 | 0.0331 | negligible | negligible | negligible |
| H=120 (4.00 LT) | oracle | 0.106 | 0.109 | 0.105 | 0.104 | 0.106 | 0.103 | 0.079 | needed, size not determined | small | lowers |
| H=120 (4.00 LT) | deployable | 0.102 | 0.107 | 0.101 | 0.101 | 0.102 | 0.1 | 0.0626 | needed, size not determined | small | negligible |

Horizon (Y = ln min(T_c, H_max)): pinball at 0.5 / Harrell's C / coverage of q_0.1 below the cap; reading against F.

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | C | cov q_0.1 | reading vs F |
|---|---|---|---|---|---|
| oracle | none | 0.16 | 0.5 | 0.103 | substantial |
| oracle | lyapunov | 0.169 | 0.63 | 0.0698 | substantial |
| oracle | RO | 0.151 | 0.572 | 0.112 | substantial |
| oracle | ROIN | 0.121 | 0.678 | 0.138 |  |
| oracle | X | 0.122 | 0.695 | 0.138 | undetermined |
| oracle | X+F | 0.0912 | 0.77 | 0.149 | lowers |
| oracle | Lyapunov rank | | 0.628 | | |
| deployable | none | 0.16 | 0.5 | 0.103 | substantial |
| deployable | lyapunov | 0.171 | 0.624 | 0.0736 | substantial |
| deployable | RO | 0.145 | 0.603 | 0.108 | substantial |
| deployable | ROIN | 0.116 | 0.694 | 0.123 |  |
| deployable | X | 0.122 | 0.694 | 0.131 | needed, size not determined |
| deployable | X+F | 0.0905 | 0.769 | 0.141 | lowers |
| deployable | Lyapunov rank | | 0.623 | | |

### C2. Shared information (oracle and deployable profiles)

Skill retained = [L(constant) - L(bottleneck)] / [L(constant) - L(F)]; reading: keeps most (CI > 0.5), loses most (CI < 0.5), else not determined. Forward: horizon from g (five clipped weights; g_w: the L_w fits); reverse: weight from h (three quantiles), scored by L_A (MSE; deployable: realized per draw, R2 guard) and by L_w (weight units, unit-weight fits). Training inputs cross-fitted.

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| profile | direction | horizon | full skill [CI] | retained L_A / pinball [CI] | reading | retained L_w [CI] | reading L_w |
|---|---|---|---|---|---|---|---|
| oracle | forward (g; g_w) | all five | 0.0394 [0.036, 0.0425] | 0.466 [0.42, 0.513] | not determined (interval spans 0.5) | 0.552 [0.499, 0.604] | not determined (interval spans 0.5) |
| oracle | forward, one weight | H=8 (0.27 LT) | | 0.0539 [0.0197, 0.0871] | loses most | | |
| oracle | forward, one weight | H=15 (0.50 LT) | | 0.0148 [-0.0169, 0.0473] | loses most | | |
| oracle | forward, one weight | H=30 (1.00 LT) | | 0.0715 [0.0354, 0.11] | loses most | | |
| oracle | forward, one weight | H=60 (2.00 LT) | | 0.131 [0.0945, 0.17] | loses most | | |
| oracle | forward, one weight | H=120 (4.00 LT) | | 0.472 [0.426, 0.519] | not determined (interval spans 0.5) | | |
| oracle | reverse | H=8 (0.27 LT) | 9.64e-06 [8.68e-06, 1.06e-05] | 0.303 [0.23, 0.363] | loses most | 0.403 [0.343, 0.454] | loses most |
| oracle | reverse | H=15 (0.50 LT) | 2.16e-05 [1.93e-05, 2.4e-05] | 0.321 [0.264, 0.377] | loses most | 0.385 [0.332, 0.433] | loses most |
| oracle | reverse | H=30 (1.00 LT) | 9.27e-05 [8.03e-05, 0.000106] | 0.211 [0.176, 0.246] | loses most | 0.405 [0.35, 0.457] | loses most |
| oracle | reverse | H=60 (2.00 LT) | 0.00117 [0.000915, 0.00145] | 0.317 [0.246, 0.408] | loses most | 0.421 [0.363, 0.482] | loses most |
| oracle | reverse | H=120 (4.00 LT) | 0.00239 [0.0017, 0.0031] | 0.533 [0.327, 0.728] | not determined (interval spans 0.5) | 0.47 [0.349, 0.586] | not determined (interval spans 0.5) |
| deployable | forward (g; g_w) | all five | 0.0438 [0.0405, 0.0469] | 0.58 [0.542, 0.622] | keeps most | 0.625 [0.589, 0.662] | keeps most |
| deployable | forward, one weight | H=8 (0.27 LT) | | 0.061 [0.0352, 0.087] | loses most | | |
| deployable | forward, one weight | H=15 (0.50 LT) | | 0.0527 [0.0282, 0.0776] | loses most | | |
| deployable | forward, one weight | H=30 (1.00 LT) | | 0.091 [0.0586, 0.124] | loses most | | |
| deployable | forward, one weight | H=60 (2.00 LT) | | 0.146 [0.114, 0.179] | loses most | | |
| deployable | forward, one weight | H=120 (4.00 LT) | | 0.517 [0.479, 0.56] | not determined (interval spans 0.5) | | |
| deployable | reverse | H=8 (0.27 LT) | -4.07e-07 [-1.27e-06, 4.33e-07] | - [-, -] | not determined (full-profile skill not established) | 0.0513 [0.0113, 0.0882] | loses most |
| deployable | reverse | H=15 (0.50 LT) | -1.23e-06 [-3.31e-06, 8.04e-07] | - [-, -] | not determined (full-profile skill not established) | 0.037 [0.00606, 0.0693] | loses most |
| deployable | reverse | H=30 (1.00 LT) | -3.91e-06 [-1.35e-05, 4.33e-06] | - [-, -] | not determined (full-profile skill not established) | 0.11 [0.0568, 0.16] | loses most |
| deployable | reverse | H=60 (2.00 LT) | 0.000139 [1.53e-05, 0.000272] | 1.57 [0.408, 8.39] | not determined (interval spans 0.5) | 0.237 [0.171, 0.307] | loses most |
| deployable | reverse | H=120 (4.00 LT) | 0.00165 [0.00115, 0.00214] | 0.864 [0.628, 1.13] | keeps most | 0.641 [0.463, 0.848] | not determined (interval spans 0.5) |

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| profile | forward C-index F / g / g_w | reverse MSE(h)/MSE(F) per horizon | math-spec prediction (both lose most) | largest single-weight retention at H |
|---|---|---|---|---|
| oracle | 0.678 / 0.613 / 0.624 | H=8 (0.27 LT) 1.06 [1.05, 1.07] substantial; H=15 (0.50 LT) 1.07 [1.06, 1.08] substantial; H=30 (1.00 LT) 1.11 [1.09, 1.12] substantial; H=60 (2.00 LT) 1.07 [1.05, 1.09] needed, size not determined; H=120 (4.00 LT) 1.01 [1.01, 1.02] small | **not determined** | 120 |
| deployable | 0.694 / 0.628 / 0.638 | H=8 (0.27 LT) 0.996 [0.989, 1] negligible; H=15 (0.50 LT) 0.993 [0.985, 1] negligible; H=30 (1.00 LT) 0.994 [0.983, 1.01] negligible; H=60 (2.00 LT) 0.994 [0.984, 1] negligible; H=120 (4.00 LT) 1 [0.998, 1.01] negligible | **not consistent** | 120 |

Oracle against deployable: retained (deployable) minus retained (oracle), paired 95% interval.

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| row | oracle | deployable | difference [CI] | reading |
|---|---|---|---|---|
| forward | 0.466 | 0.58 | 0.114 [0.0712, 0.159] | deployable retains more |
| forward_w | 0.552 | 0.625 | 0.0737 [0.0197, 0.122] | deployable retains more |
| reverse/8 | 0.303 | - | - [-, -] | not determined (full-profile skill not established) |
| reverse_w/8 | 0.403 | 0.0513 | -0.352 [-0.411, -0.287] | deployable retains less |
| reverse/15 | 0.321 | - | - [-, -] | not determined (full-profile skill not established) |
| reverse_w/15 | 0.385 | 0.037 | -0.348 [-0.406, -0.287] | deployable retains less |
| reverse/30 | 0.211 | - | - [-, -] | not determined (full-profile skill not established) |
| reverse_w/30 | 0.405 | 0.11 | -0.295 [-0.358, -0.23] | deployable retains less |
| reverse/60 | 0.317 | 1.57 | 1.25 [0.0983, 8.08] | deployable retains more |
| reverse_w/60 | 0.421 | 0.237 | -0.184 [-0.263, -0.102] | deployable retains less |
| reverse/120 | 0.533 | 0.864 | 0.331 [0.0728, 0.648] | deployable retains more |
| reverse_w/120 | 0.47 | 0.641 | 0.172 [0.0128, 0.375] | deployable retains more |

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| horizon | Spearman(phi allocation, phi horizon) (4 items, descriptive) | phi_alloc R/O/I/N | phi_horizon R/O/I/N |
|---|---|---|---|
| H=8 (0.27 LT) | -1 | 6.1e-06/7.9e-07/3.1e-08/2.7e-06 | 0.0022/0.0084/0.024/0.0046 |
| H=15 (0.50 LT) | -1 | 1.5e-05/2.1e-06/-1.6e-07/4.9e-06 | 0.0022/0.0084/0.024/0.0046 |
| H=30 (1.00 LT) | -1 | 6.4e-05/1.1e-05/8.3e-07/1.7e-05 | 0.0022/0.0084/0.024/0.0046 |
| H=60 (2.00 LT) | -0.4 | 0.00094/0.00013/5.1e-05/4.9e-05 | 0.0022/0.0084/0.024/0.0046 |
| H=120 (4.00 LT) | -0.4 | 0.0013/0.00016/0.00065/0.00031 | 0.0022/0.0084/0.024/0.0046 |

### C3. The deployable chain

False trust = P(T <= q_0.1) per (state, draw), target 0.1; T realized (the run's first passage against the noisy truth) or characteristic (moments). Trusted horizon = mean q_0.1 (LT). A4 + KM leaf uses the calibration A4 hybrid's characteristic horizon (no per-draw calibration errors on the full grid).

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| policy | false trust realized [CI] | false trust characteristic [CI] | mean trusted (LT) [CI] | q at cap |
|---|---|---|---|---|
| A2 + constant | 0.102 [0.0963, 0.109] | 0.103 [0.0938, 0.113] | 1.89 [1.89, 1.89] | 0 |
| A2 + h(F-hat) | 0.134 [0.128, 0.141] | 0.126 [0.117, 0.135] | 2.21 [2.2, 2.23] | 0 |
| A4 + KM leaf | 0.11 [0.104, 0.117] | 0.115 [0.106, 0.124] | 2.03 [2.02, 2.04] | 0 |
| g(F-hat) + h(F-hat) | 0.137 [0.131, 0.144] | 0.125 [0.116, 0.134] | 2.26 [2.24, 2.28] | 0 |

Hybrid MSE ratio to A2 (realized per draw; 1.05 table, R2 guard).

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| policy | H=8 (0.27 LT) | H=15 (0.50 LT) | H=30 (1.00 LT) | H=60 (2.00 LT) | H=120 (4.00 LT) |
|---|---|---|---|---|---|
| A4 + KM leaf | 1.09 [1.07, 1.11] substantial | 1.08 [1.05, 1.1] substantial | 1.05 [1.03, 1.07] needed, size not determined | 0.997 [0.98, 1.01] negligible | 1.05 [1.03, 1.06] needed, size not determined |
| g(F-hat) + h(F-hat) | 1 [0.997, 1.01] negligible | 1 [0.996, 1.01] negligible | 1 [0.995, 1.02] negligible | 0.988 [0.978, 0.998] lowers | 0.984 [0.979, 0.989] lowers |

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| full system minus | false trust realized [CI] | false trust characteristic [CI] | trusted LT [CI] |
|---|---|---|---|
| A2 + constant | 0.0348 [0.0284, 0.0408] | 0.0218 [0.0116, 0.0316] | 0.371 [0.351, 0.389] |
| A2 + h(F-hat) | 0.00294 [-0.000814, 0.00662] | -0.000625 [-0.00619, 0.00506] | 0.0514 [0.0478, 0.0552] |
| A4 + KM leaf | 0.0266 [0.0211, 0.0323] | 0.00994 [0.00156, 0.0184] | 0.233 [0.22, 0.245] |

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| horizon model (own characteristic target) | pinball / constant's | constant/model ratio [CI] reading | cov 0.1 / 0.5 / 0.9 | C |
|---|---|---|---|---|
| h_A2(F-hat) | 0.103 / 0.151 | 1.47 [1.43, 1.5] substantial | 0.126 / 0.503 / 0.868 | 0.711 |
| h_g(F-hat) | 0.102 / 0.156 | 1.53 [1.49, 1.57] substantial | 0.125 / 0.496 / 0.874 | - |

### E-H2a. Amplification mismatch m(H) (H_0 = 1 LT; both r.m.s. <= 0.5 sigma_x)

Medians by tercile of I (low / mid / high). Spearman(m, I) on the kept states [95%]. B and A columns from the A/D record (oracle).

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| horizon | kept | m | abs drift w* | corr C/sqrt(E_C E_P) | Spearman(m, I) | B RI / OI | A drop-I (MSE) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 3990 | -0.13 / 0.15 / 0.15 | 0.069 / 0.094 / 0.075 | 0.17 / 0.19 / 0.21 | 0.124 [0.0922, 0.155] | no interaction gain detected / no interaction gain detected | negligible |
| H=15 (0.50 LT) | 3990 | -0.19 / 0.093 / 0.09 | 0.065 / 0.091 / 0.055 | 0.18 / 0.18 / 0.21 | 0.127 [0.0978, 0.158] | no interaction gain detected / no interaction gain detected | negligible |
| H=30 (1.00 LT) | 3990 | 0 / 0 / 0 | 0 / 0 / 0 | 0.23 / 0.19 / 0.23 | (H_0) | no interaction gain detected / interaction gain detected | negligible |
| H=60 (2.00 LT) | 3736 | -0.22 / -0.25 / -0.22 | 0.069 / 0.11 / 0.098 | 0.24 / 0.25 / 0.28 | -0.00314 [-0.0365, 0.0305] | no interaction gain detected / interaction gain detected | negligible |
| H=120 (4.00 LT) | 2799 | -1.4 / -1.6 / -1.3 | 0.24 / 0.31 / 0.3 | 0.33 / 0.39 / 0.34 | 0.0351 [-0.00217, 0.0721] | interaction gain detected / no interaction gain detected | small |

**Reading: not consistent** (horizons_used: ['60', '120'], horizons_supporting: [], horizons_null: ['60', '120']).

### E-H2e. Library size and error correlation (sweep states)

1000 sweep states. Delta = value at N_lib 100000 minus 1000. corr = the H2e correlation (0 by convention where an error is constant over the draws).

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| rho | valid | corr 0 small / large lib | median corr small -> large | set | median Delta corr [CI] | Spearman(Delta corr, Delta R) [CI] | reading |
|---|---|---|---|---|---|---|---|
| 0.01 | 1000 | 603 / 1 | 0 -> 0.459 | all (1000) | 0.363 [0.334, 0.385] | 0.167 [0.101, 0.23] | not consistent |
| 0.01 | 1000 | 603 / 1 | 0 -> 0.459 | both_defined (397) | 0.144 [0.112, 0.191] | 0.156 [0.0471, 0.246] | not consistent |
| 0.02 | 1000 | 291 / 0 | 0.119 -> 0.461 | all (1000) | 0.273 [0.243, 0.301] | 0.177 [0.115, 0.235] | not consistent |
| 0.02 | 1000 | 291 / 0 | 0.119 -> 0.461 | both_defined (709) | 0.16 [0.126, 0.192] | 0.176 [0.102, 0.239] | not consistent |

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| rho | stratifier | median Delta corr low / mid / high | median Delta R low / mid / high |
|---|---|---|---|
| 0.01 | R | 0.35 / 0.34 / 0.39 | -1.4 / -1.4 / -1.4 |
| 0.01 | O | 0.38 / 0.37 / 0.35 | -1.4 / -1.4 / -1.3 |
| 0.01 | I | 0.31 / 0.35 / 0.42 | -1.4 / -1.4 / -1.4 |
| 0.01 | N | 0.36 / 0.34 / 0.38 | -1.5 / -1.2 / -1.4 |
| 0.01 | delta_R | 0.29 / 0.38 / 0.41 | -2.1 / -1.4 / -0.47 |
| 0.02 | R | 0.26 / 0.25 / 0.32 | -0.77 / -0.85 / -0.9 |
| 0.02 | O | 0.31 / 0.25 / 0.25 | -0.88 / -0.9 / -0.77 |
| 0.02 | I | 0.24 / 0.28 / 0.32 | -0.88 / -0.9 / -0.81 |
| 0.02 | N | 0.28 / 0.26 / 0.26 | -0.91 / -0.65 / -0.91 |
| 0.02 | delta_R | 0.2 / 0.26 / 0.33 | -1.5 / -0.85 / -0.053 |

**Reading** (final, after the convention check): rho 0.01: not consistent; rho 0.02: not consistent.

### E-H3c. A5 against A4

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| item | value |
|---|---|
| H3c ratio MSE(A5)/MSE(A4) [CI at level 0.983] (run) | 0.967 [0.944, 0.99], width 0.0463 |
| top-1% share: A5 loss / A4 loss / abs(A5 - A4) | 0.181 / 0.183 / 0.194 |
| autocorrelation of d = A5 - A4, lags 1..5 | -0.0055, -0.00075, 0.026, -0.021, 0.017 |
| block-5 means: lag-1 autocorrelation, variance ratio | -0.00363, 1.06 |
| K chosen; leaves used test / calibration; largest leaf share test | 4; 4 / 4; 0.283 |
| w*(H_ref) within-leaf share of variance | 0.95 |
| bimodality coefficient R/O/I/N, oracle; deployable | 0.26/0.79/0.44/0.83; 0.51/0.8/0.44/0.91 |
| Spearman pairs (oracle) | RO 0.37, RI -0.082, RN 0.42, OI -0.033, ON 0.021, IN -0.0032 |
| top-1% abs(d) states: mean percentile R/O/I/N | 0.68/0.83/0.76/0.55 |
| top-1% abs(d) states: median I pct; share high-I; median abs(x) pct; share sign change in window; share of sum d | 0.797; 0.85; 0.373; 1; 0.167 |

## chua

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| check | result |
|---|---|
| A2 rebuilt on 1..H_max equals the dumped A2 (bitwise); A4 horizon-free | True, True |
| refit reproduces WU-0048 (max abs: A/ROIN MSE oracle, deployable; W/ROIN L_w oracle, deployable) | 0 / 0 / 0 / 0 |
| T_c counts T = 1 / e_(T-1) = theta (A2 train, g train, A2 test, g test, A4 calibration) | 7/0, 13/0, 7/0, 24/0, 0/0 |
| A2 on 1..H_max: pooled curvature floor / columns at 0 or 1 | 0 / 0 |
| weights clipped to [0, 1] | g_oracle_test 2090, g_oracle_train_oof 1501, gw_oracle_test 2080, gw_oracle_train_oof 1519, g_deployable_test 4922, g_deployable_train_oof 5371, gw_deployable_test 2345, gw_deployable_train_oof 1713 |

### C1. Separate performance (from the A/D record, no refit)

Allocation: MSE per rule (oracle: moment form; deployable: realized); reading of the rung against F (MSE ratio, 1.05 table, n_eff guard). G(F) = 1 - L_A(F)/L_A(constant).

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| horizon | profile | constant | separation | RO | F (ROIN) | X | X+F | G(F) | sep vs F | RO vs F | X+F vs F |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 0.00102 | 0.000554 | 0.000792 | 0.000871 | 0.000751 | 0.000697 | 0.263 | undetermined | undetermined | undetermined |
| H=8 (0.27 LT) | deployable | 0.00106 | 0.000938 | 0.00094 | 0.000996 | 0.000835 | 0.00085 | 0.113 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | oracle | 0.00321 | 0.00282 | 0.00281 | 0.00271 | 0.00314 | 0.00275 | 0.567 | undetermined | undetermined | negligible |
| H=15 (0.50 LT) | deployable | 0.00313 | 0.00314 | 0.00313 | 0.00335 | 0.00307 | 0.00315 | -0.266 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | oracle | 0.0161 | 0.0148 | 0.015 | 0.015 | 0.0164 | 0.015 | 0.204 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | deployable | 0.0178 | 0.0175 | 0.0173 | 0.0172 | 0.0179 | 0.0175 | 0.0949 | undetermined | negligible | undetermined |
| H=60 (2.00 LT) | oracle | 0.195 | 0.185 | 0.184 | 0.183 | 0.191 | 0.182 | 0.175 | negligible | negligible | negligible |
| H=60 (2.00 LT) | deployable | 0.186 | 0.188 | 0.184 | 0.183 | 0.181 | 0.179 | 0.0534 | small | negligible | lowers |
| H=120 (4.00 LT) | oracle | 0.664 | 0.676 | 0.648 | 0.645 | 0.661 | 0.645 | 0.101 | needed, size not determined | small | negligible |
| H=120 (4.00 LT) | deployable | 0.66 | 0.683 | 0.653 | 0.648 | 0.658 | 0.647 | 0.0647 | needed, size not determined | small | negligible |

Horizon (Y = ln min(T_c, H_max)): pinball at 0.5 / Harrell's C / coverage of q_0.1 below the cap; reading against F.

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | C | cov q_0.1 | reading vs F |
|---|---|---|---|---|---|
| oracle | none | 0.225 | 0.5 | 0.102 | substantial |
| oracle | lyapunov | 0.263 | 0.672 | 0.0904 | substantial |
| oracle | RO | 0.202 | 0.63 | 0.111 | substantial |
| oracle | ROIN | 0.159 | 0.722 | 0.139 |  |
| oracle | X | 0.173 | 0.697 | 0.141 | needed, size not determined |
| oracle | X+F | 0.135 | 0.769 | 0.151 | lowers |
| oracle | Lyapunov rank | | 0.669 | | |
| deployable | none | 0.225 | 0.5 | 0.102 | substantial |
| deployable | lyapunov | 0.264 | 0.669 | 0.0908 | substantial |
| deployable | RO | 0.198 | 0.628 | 0.113 | substantial |
| deployable | ROIN | 0.16 | 0.717 | 0.127 |  |
| deployable | X | 0.171 | 0.698 | 0.137 | needed, size not determined |
| deployable | X+F | 0.139 | 0.759 | 0.147 | lowers |
| deployable | Lyapunov rank | | 0.664 | | |

### C2. Shared information (oracle and deployable profiles)

Skill retained = [L(constant) - L(bottleneck)] / [L(constant) - L(F)]; reading: keeps most (CI > 0.5), loses most (CI < 0.5), else not determined. Forward: horizon from g (five clipped weights; g_w: the L_w fits); reverse: weight from h (three quantiles), scored by L_A (MSE; deployable: realized per draw, R2 guard) and by L_w (weight units, unit-weight fits). Training inputs cross-fitted.

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| profile | direction | horizon | full skill [CI] | retained L_A / pinball [CI] | reading | retained L_w [CI] | reading L_w |
|---|---|---|---|---|---|---|---|
| oracle | forward (g; g_w) | all five | 0.0668 [0.0618, 0.0717] | 0.449 [0.409, 0.492] | loses most | 0.581 [0.533, 0.628] | keeps most |
| oracle | forward, one weight | H=8 (0.27 LT) | | 0.0502 [0.0341, 0.0661] | loses most | | |
| oracle | forward, one weight | H=15 (0.50 LT) | | 0.0291 [0.00879, 0.0493] | loses most | | |
| oracle | forward, one weight | H=30 (1.00 LT) | | 0.0622 [0.0454, 0.0807] | loses most | | |
| oracle | forward, one weight | H=60 (2.00 LT) | | 0.162 [0.138, 0.189] | loses most | | |
| oracle | forward, one weight | H=120 (4.00 LT) | | 0.261 [0.23, 0.295] | loses most | | |
| oracle | reverse | H=8 (0.27 LT) | 0.000149 [-0.000236, 0.000523] | 1.43 [-, -] | not determined (full-profile skill not established) | 0.0781 [0.0412, 0.116] | loses most |
| oracle | reverse | H=15 (0.50 LT) | 0.000509 [0.000272, 0.000831] | -0.103 [-0.724, 0.249] | loses most | 0.0935 [0.0547, 0.129] | loses most |
| oracle | reverse | H=30 (1.00 LT) | 0.0011 [0.000697, 0.00149] | -0.139 [-0.49, 0.125] | not determined (n_eff < 50) | 0.157 [0.107, 0.208] | loses most |
| oracle | reverse | H=60 (2.00 LT) | 0.0121 [0.0084, 0.0155] | 0.187 [0.0801, 0.317] | loses most | 0.32 [0.266, 0.372] | loses most |
| oracle | reverse | H=120 (4.00 LT) | 0.0188 [0.0149, 0.0226] | 0.348 [0.216, 0.486] | loses most | 0.276 [0.188, 0.365] | loses most |
| deployable | forward (g; g_w) | all five | 0.0654 [0.0608, 0.0704] | 0.446 [0.405, 0.485] | loses most | 0.578 [0.545, 0.613] | keeps most |
| deployable | forward, one weight | H=8 (0.27 LT) | | 0.0103 [-0.00221, 0.0225] | loses most | | |
| deployable | forward, one weight | H=15 (0.50 LT) | | 0.0579 [0.0402, 0.0757] | loses most | | |
| deployable | forward, one weight | H=30 (1.00 LT) | | 0.0697 [0.052, 0.0879] | loses most | | |
| deployable | forward, one weight | H=60 (2.00 LT) | | 0.124 [0.0984, 0.149] | loses most | | |
| deployable | forward, one weight | H=120 (4.00 LT) | | 0.323 [0.284, 0.36] | loses most | | |
| deployable | reverse | H=8 (0.27 LT) | 6.9e-05 [-3.85e-05, 0.000168] | 1.81 [-, -] | not determined (full-profile skill not established) | 0.137 [0.0632, 0.211] | loses most |
| deployable | reverse | H=15 (0.50 LT) | -0.000217 [-0.000547, 5.26e-05] | - [-, -] | not determined (full-profile skill not established) | 0.269 [0.209, 0.323] | loses most |
| deployable | reverse | H=30 (1.00 LT) | 0.000676 [0.000302, 0.00108] | 0.643 [0.0158, 1.44] | not determined (interval spans 0.5) | 0.328 [0.253, 0.397] | loses most |
| deployable | reverse | H=60 (2.00 LT) | 0.00323 [0.000922, 0.00563] | 0.639 [-0.19, 1.66] | not determined (interval spans 0.5) | 0.519 [0.454, 0.583] | not determined (interval spans 0.5) |
| deployable | reverse | H=120 (4.00 LT) | 0.0117 [0.00698, 0.0165] | 0.732 [0.526, 1.09] | keeps most | 0.625 [0.487, 0.769] | not determined (interval spans 0.5) |

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| profile | forward C-index F / g / g_w | reverse MSE(h)/MSE(F) per horizon | math-spec prediction (both lose most) | largest single-weight retention at H |
|---|---|---|---|---|
| oracle | 0.722 / 0.657 / 0.673 | H=8 (0.27 LT) 0.926 [0.608, 1.47] undetermined (n_eff < 50); H=15 (0.50 LT) 1.21 [1.1, 1.34] substantial; H=30 (1.00 LT) 1.08 [1.05, 1.12] undetermined (n_eff < 50); H=60 (2.00 LT) 1.05 [1.03, 1.07] needed, size not determined; H=120 (4.00 LT) 1.02 [1.01, 1.03] small | **consistent** | 120 |
| deployable | 0.717 / 0.651 / 0.676 | H=8 (0.27 LT) 0.944 [0.715, 1.16] undetermined (n_eff < 50); H=15 (0.50 LT) 1.02 [0.933, 1.13] undetermined (n_eff < 50); H=30 (1.00 LT) 1.01 [0.988, 1.04] negligible; H=60 (2.00 LT) 1.01 [0.995, 1.02] negligible; H=120 (4.00 LT) 1 [0.999, 1.01] negligible | **not consistent** | 120 |

Oracle against deployable: retained (deployable) minus retained (oracle), paired 95% interval.

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| row | oracle | deployable | difference [CI] | reading |
|---|---|---|---|---|
| forward | 0.449 | 0.446 | -0.00305 [-0.0492, 0.04] | no difference detected |
| forward_w | 0.581 | 0.578 | -0.00312 [-0.0504, 0.0454] | no difference detected |
| reverse/8 | 1.43 | 1.81 | 0.384 [-, -] | not determined (full-profile skill not established) |
| reverse_w/8 | 0.0781 | 0.137 | 0.059 [-0.015, 0.135] | no difference detected |
| reverse/15 | -0.103 | - | - [-, -] | not determined (full-profile skill not established) |
| reverse_w/15 | 0.0935 | 0.269 | 0.176 [0.12, 0.231] | deployable retains more |
| reverse/30 | -0.139 | 0.643 | 0.782 [0.271, 1.6] | not determined (n_eff < 50) |
| reverse_w/30 | 0.157 | 0.328 | 0.171 [0.111, 0.23] | deployable retains more |
| reverse/60 | 0.187 | 0.639 | 0.451 [-0.382, 1.47] | no difference detected |
| reverse_w/60 | 0.32 | 0.519 | 0.199 [0.141, 0.259] | deployable retains more |
| reverse/120 | 0.348 | 0.732 | 0.384 [0.178, 0.739] | deployable retains more |
| reverse_w/120 | 0.276 | 0.625 | 0.35 [0.242, 0.471] | deployable retains more |

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| horizon | Spearman(phi allocation, phi horizon) (4 items, descriptive) | phi_alloc R/O/I/N | phi_horizon R/O/I/N |
|---|---|---|---|
| H=8 (0.27 LT) | 0.8 | -1.2e-05/1e-06/8.7e-05/7.3e-05 | 0.003/0.014/0.046/0.0036 |
| H=15 (0.50 LT) | -0.8 | 0.00031/0.00025/-6.5e-05/2.2e-05 | 0.003/0.014/0.046/0.0036 |
| H=30 (1.00 LT) | -1 | 0.00074/0.00016/-4.1e-05/0.00024 | 0.003/0.014/0.046/0.0036 |
| H=60 (2.00 LT) | -0.8 | 0.0096/0.00033/0.00055/0.0016 | 0.003/0.014/0.046/0.0036 |
| H=120 (4.00 LT) | -0.4 | 0.011/0.0013/0.0043/0.0018 | 0.003/0.014/0.046/0.0036 |

### C3. The deployable chain

False trust = P(T <= q_0.1) per (state, draw), target 0.1; T realized (the run's first passage against the noisy truth) or characteristic (moments). Trusted horizon = mean q_0.1 (LT). A4 + KM leaf uses the calibration A4 hybrid's characteristic horizon (no per-draw calibration errors on the full grid).

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| policy | false trust realized [CI] | false trust characteristic [CI] | mean trusted (LT) [CI] | q at cap |
|---|---|---|---|---|
| A2 + constant | 0.0796 [0.0734, 0.0858] | 0.101 [0.0917, 0.11] | 0.972 [0.972, 0.972] | 0 |
| A2 + h(F-hat) | 0.107 [0.1, 0.113] | 0.126 [0.117, 0.135] | 1.39 [1.38, 1.41] | 0 |
| A4 + KM leaf | 0.0739 [0.0686, 0.0796] | 0.103 [0.095, 0.113] | 1.2 [1.19, 1.21] | 0 |
| g(F-hat) + h(F-hat) | 0.109 [0.103, 0.115] | 0.129 [0.12, 0.138] | 1.47 [1.45, 1.48] | 0 |

Hybrid MSE ratio to A2 (realized per draw; 1.05 table, R2 guard).

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| policy | H=8 (0.27 LT) | H=15 (0.50 LT) | H=30 (1.00 LT) | H=60 (2.00 LT) | H=120 (4.00 LT) |
|---|---|---|---|---|---|
| A4 + KM leaf | 0.663 [0.428, 0.996] undetermined (n_eff < 50) | 0.932 [0.863, 1.02] negligible | 0.981 [0.953, 1.01] negligible | 1.01 [0.992, 1.02] negligible | 1.03 [1.02, 1.05] small |
| g(F-hat) + h(F-hat) | 0.704 [0.548, 0.877] undetermined (n_eff < 50) | 0.994 [0.909, 1.08] undetermined | 0.963 [0.944, 0.982] lowers | 0.982 [0.97, 0.995] lowers | 0.982 [0.975, 0.989] lowers |

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| full system minus | false trust realized [CI] | false trust characteristic [CI] | trusted LT [CI] |
|---|---|---|---|
| A2 + constant | 0.0292 [0.0221, 0.0369] | 0.0284 [0.0179, 0.0394] | 0.494 [0.478, 0.512] |
| A2 + h(F-hat) | 0.00219 [-0.00181, 0.00625] | 0.00337 [-0.00181, 0.00875] | 0.0722 [0.0659, 0.0782] |
| A4 + KM leaf | 0.0349 [0.0289, 0.0409] | 0.0256 [0.0166, 0.0346] | 0.264 [0.252, 0.276] |

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| horizon model (own characteristic target) | pinball / constant's | constant/model ratio [CI] reading | cov 0.1 / 0.5 / 0.9 | C |
|---|---|---|---|---|
| h_A2(F-hat) | 0.164 / 0.239 | 1.45 [1.42, 1.49] substantial | 0.126 / 0.5 / 0.872 | 0.727 |
| h_g(F-hat) | 0.161 / 0.236 | 1.46 [1.43, 1.5] substantial | 0.129 / 0.496 / 0.878 | - |

### E-H2a. Amplification mismatch m(H) (H_0 = 1 LT; both r.m.s. <= 0.5 sigma_x)

Medians by tercile of I (low / mid / high). Spearman(m, I) on the kept states [95%]. B and A columns from the A/D record (oracle).

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| horizon | kept | m | abs drift w* | corr C/sqrt(E_C E_P) | Spearman(m, I) | B RI / OI | A drop-I (MSE) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 3732 | -0.0043 / 0.25 / 0.47 | 0.053 / 0.098 / 0.12 | 0.15 / 0.16 / 0.25 | 0.147 [0.114, 0.179] | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=15 (0.50 LT) | 3723 | 0.0056 / -0.15 / 0.21 | 0.045 / 0.12 / 0.098 | 0.17 / 0.17 / 0.25 | 0.0846 [0.054, 0.115] | no interaction gain detected / interaction gain detected | negligible |
| H=30 (1.00 LT) | 3738 | 0 / 0 / 0 | 0 / 0 / 0 | 0.16 / 0.2 / 0.28 | (H_0) | no interaction gain detected / interaction gain detected | undetermined (n_eff < 50) |
| H=60 (2.00 LT) | 2603 | -0.21 / -0.74 / -0.12 | 0.052 / 0.15 / 0.1 | 0.21 / 0.18 / 0.29 | -0.0252 [-0.0636, 0.0114] | no interaction gain detected / interaction gain detected | negligible |
| H=120 (4.00 LT) | 981 | -1.7 / -1.5 / -0.73 | 0.27 / 0.24 / 0.25 | 0.26 / 0.29 / 0.34 | 0.0318 [-0.0286, 0.0928] | no interaction gain detected / no interaction gain detected | small |

**Reading: not consistent** (horizons_used: ['60', '120'], horizons_supporting: [], horizons_null: ['60', '120']).

### E-H2e. Library size and error correlation (sweep states)

1000 sweep states. Delta = value at N_lib 100000 minus 1000. corr = the H2e correlation (0 by convention where an error is constant over the draws).

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| rho | valid | corr 0 small / large lib | median corr small -> large | set | median Delta corr [CI] | Spearman(Delta corr, Delta R) [CI] | reading |
|---|---|---|---|---|---|---|---|
| 0.01 | 1000 | 561 / 15 | 0 -> 0.423 | all (1000) | 0.337 [0.319, 0.36] | 0.0375 [-0.0223, 0.0938] | not determined |
| 0.01 | 1000 | 561 / 15 | 0 -> 0.423 | both_defined (436) | 0.227 [0.192, 0.263] | -0.0919 [-0.182, -0.0062] | consistent |
| 0.02 | 1000 | 266 / 3 | 0.00285 -> 0.403 | all (1000) | 0.297 [0.277, 0.314] | -0.0246 [-0.0851, 0.032] | not determined |
| 0.02 | 1000 | 266 / 3 | 0.00285 -> 0.403 | both_defined (732) | 0.258 [0.24, 0.291] | -0.0227 [-0.0989, 0.0434] | not determined |

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| rho | stratifier | median Delta corr low / mid / high | median Delta R low / mid / high |
|---|---|---|---|
| 0.01 | R | 0.32 / 0.37 / 0.33 | -1.3 / -1.3 / -1.6 |
| 0.01 | O | 0.33 / 0.34 / 0.34 | -1.6 / -1.4 / -1.3 |
| 0.01 | I | 0.32 / 0.3 / 0.39 | -1.5 / -1.4 / -1.3 |
| 0.01 | N | 0.35 / 0.32 / 0.34 | -1.7 / -1.1 / -1.6 |
| 0.01 | delta_R | 0.32 / 0.37 / 0.33 | -2.3 / -1.4 / -0.58 |
| 0.02 | R | 0.28 / 0.31 / 0.3 | -0.77 / -0.86 / -1.2 |
| 0.02 | O | 0.31 / 0.27 / 0.31 | -1.2 / -0.92 / -0.75 |
| 0.02 | I | 0.28 / 0.26 / 0.33 | -1 / -0.91 / -0.83 |
| 0.02 | N | 0.31 / 0.28 / 0.31 | -1.2 / -0.64 / -1 |
| 0.02 | delta_R | 0.31 / 0.31 / 0.26 | -1.7 / -0.93 / -0.21 |

**Reading** (final, after the convention check): rho 0.01: not determined (depends on the zero-variance convention); rho 0.02: not determined.

### E-H3c. A5 against A4

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| item | value |
|---|---|
| H3c ratio MSE(A5)/MSE(A4) [CI at level 0.983] (run) | 1.01 [0.971, 1.05], width 0.0795 |
| top-1% share: A5 loss / A4 loss / abs(A5 - A4) | 0.631 / 0.618 / 0.452 |
| autocorrelation of d = A5 - A4, lags 1..5 | -0.00041, -0.0025, 0.00038, -0.024, -0.0094 |
| block-5 means: lag-1 autocorrelation, variance ratio | -0.0752, 1 |
| K chosen; leaves used test / calibration; largest leaf share test | 2; 2 / 2; 0.776 |
| w*(H_ref) within-leaf share of variance | 0.967 |
| bimodality coefficient R/O/I/N, oracle; deployable | 0.23/0.2/0.44/0.84; 0.27/0.45/0.45/0.89 |
| Spearman pairs (oracle) | RO 0.095, RI -0.04, RN 0.39, OI 0.35, ON 0.053, IN 0.0094 |
| top-1% abs(d) states: mean percentile R/O/I/N | 0.48/0.72/0.89/0.52 |
| top-1% abs(d) states: median I pct; share high-I; median abs(x) pct; share sign change in window; share of sum d | 0.942; 0.9; 0.362; 0.2; 0.64 |

## E-H3c reading (this seed)

PHASE J CONFIRMATORY (CONF-5): pre-registered analysis, UNPROMOTED.

| item | value |
|---|---|
| H3c interval widths | lorenz63 0.223, rossler 0.0463, chua 0.0795 |
| pattern (Lorenz-63 widest, Rössler narrowest) reproduced | True |
| Lorenz-63 part (top-1% share of sum abs(d) 0.615, median I percentile 0.21) | not consistent |
| Rössler part (BC deployable: R 0.511, O 0.799, I 0.44, N 0.909) | not consistent |
| **reading** | **not consistent** |

