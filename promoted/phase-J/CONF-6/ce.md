# Phase J experiments C and E: CONF-6

**PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.** Run `phasej-CONF-6/phasej`; analysis commit `c19ad486b93a2ee96d64ce069ec42fd440428211` (dirty: False); A/D record `phasej-CONF-6/contrib-j/contrib.json`. Estimates with 95% intervals from the shared moving-block index sets (models fixed; training variance not included). Readings are descriptive; no causal claim; nothing here is set beside CONF-1.

## lorenz63

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| check | result |
|---|---|
| A2 rebuilt on 1..H_max equals the dumped A2 (bitwise); A4 horizon-free | True, True |
| refit reproduces WU-0048 (max abs: A/ROIN MSE oracle, deployable; W/ROIN L_w oracle, deployable) | 0 / 0 / 0 / 0 |
| T_c counts T = 1 / e_(T-1) = theta (A2 train, g train, A2 test, g test, A4 calibration) | 10/0, 64/0, 34/0, 150/0, 100/0 |
| A2 on 1..H_max: pooled curvature floor / columns at 0 or 1 | 0 / 0 |
| weights clipped to [0, 1] | g_oracle_test 3501, g_oracle_train_oof 2409, gw_oracle_test 2414, gw_oracle_train_oof 2050, g_deployable_test 5240, g_deployable_train_oof 4115, gw_deployable_test 2644, gw_deployable_train_oof 2118 |

### C1. Separate performance (from the A/D record, no refit)

Allocation: MSE per rule (oracle: moment form; deployable: realized); reading of the rung against F (MSE ratio, 1.05 table, n_eff guard). G(F) = 1 - L_A(F)/L_A(constant).

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| horizon | profile | constant | separation | RO | F (ROIN) | X | X+F | G(F) | sep vs F | RO vs F | X+F vs F |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 0.0111 | 0.00204 | 0.0019 | 0.00202 | 0.00205 | 0.00172 | 0.946 | undetermined | undetermined | undetermined |
| H=8 (0.27 LT) | deployable | 0.0101 | 0.0212 | 0.00478 | 0.00481 | 0.00214 | 0.00255 | 0.617 | substantial | undetermined | lowers |
| H=15 (0.50 LT) | oracle | 0.0314 | 0.0119 | 0.0114 | 0.0111 | 0.0143 | 0.0112 | 0.899 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | deployable | 0.0331 | 0.0416 | 0.0246 | 0.0234 | 0.0136 | 0.0148 | 0.399 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | oracle | 0.0605 | 0.0388 | 0.038 | 0.0375 | 0.0401 | 0.0373 | 0.671 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | deployable | 0.0643 | 0.0725 | 0.0544 | 0.0501 | 0.0444 | 0.0453 | 0.373 | substantial | needed, size not determined | lowers |
| H=60 (2.00 LT) | oracle | 0.146 | 0.132 | 0.131 | 0.13 | 0.133 | 0.128 | 0.271 | undetermined | negligible | negligible |
| H=60 (2.00 LT) | deployable | 0.155 | 0.159 | 0.15 | 0.147 | 0.141 | 0.138 | 0.116 | needed, size not determined | undetermined | lowers |
| H=120 (4.00 LT) | oracle | 0.87 | 0.932 | 0.861 | 0.861 | 0.858 | 0.857 | 0.0366 | substantial | negligible | lowers |
| H=120 (4.00 LT) | deployable | 0.861 | 0.907 | 0.853 | 0.852 | 0.847 | 0.846 | 0.0343 | needed, size not determined | negligible | negligible |

Horizon (Y = ln min(T_c, H_max)): pinball at 0.5 / Harrell's C / coverage of q_0.1 below the cap; reading against F.

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | C | cov q_0.1 | reading vs F |
|---|---|---|---|---|---|
| oracle | none | 0.195 | 0.5 | 0.111 | substantial |
| oracle | lyapunov | 0.298 | 0.625 | 0.0794 | substantial |
| oracle | RO | 0.191 | 0.56 | 0.143 | substantial |
| oracle | ROIN | 0.152 | 0.684 | 0.15 |  |
| oracle | X | 0.164 | 0.67 | 0.158 | needed, size not determined |
| oracle | X+F | 0.135 | 0.724 | 0.171 | lowers |
| oracle | Lyapunov rank | | 0.621 | | |
| deployable | none | 0.195 | 0.5 | 0.111 | substantial |
| deployable | lyapunov | 0.298 | 0.623 | 0.0797 | substantial |
| deployable | RO | 0.191 | 0.562 | 0.108 | substantial |
| deployable | ROIN | 0.149 | 0.689 | 0.135 |  |
| deployable | X | 0.165 | 0.669 | 0.154 | substantial |
| deployable | X+F | 0.136 | 0.717 | 0.157 | lowers |
| deployable | Lyapunov rank | | 0.622 | | |

### C2. Shared information (oracle and deployable profiles)

Skill retained = [L(constant) - L(bottleneck)] / [L(constant) - L(F)]; reading: keeps most (CI > 0.5), loses most (CI < 0.5), else not determined. Forward: horizon from g (five clipped weights; g_w: the L_w fits); reverse: weight from h (three quantiles), scored by L_A (MSE; deployable: realized per draw, R2 guard) and by L_w (weight units, unit-weight fits). Training inputs cross-fitted.

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| profile | direction | horizon | full skill [CI] | retained L_A / pinball [CI] | reading | retained L_w [CI] | reading L_w |
|---|---|---|---|---|---|---|---|
| oracle | forward (g; g_w) | all five | 0.0428 [0.038, 0.0477] | 0.148 [0.116, 0.178] | loses most | 0.18 [0.144, 0.218] | loses most |
| oracle | forward, one weight | H=8 (0.27 LT) | | 0.0205 [0.00631, 0.0342] | loses most | | |
| oracle | forward, one weight | H=15 (0.50 LT) | | 0.0341 [0.0154, 0.0527] | loses most | | |
| oracle | forward, one weight | H=30 (1.00 LT) | | -0.00183 [-0.013, 0.00839] | loses most | | |
| oracle | forward, one weight | H=60 (2.00 LT) | | 0.0218 [0.0118, 0.0327] | loses most | | |
| oracle | forward, one weight | H=120 (4.00 LT) | | 0.0957 [0.0652, 0.124] | loses most | | |
| oracle | reverse | H=8 (0.27 LT) | 0.0091 [0.00725, 0.0112] | 0.238 [0.056, 0.403] | not determined (n_eff < 50) | 0.0761 [0.0547, 0.0962] | loses most |
| oracle | reverse | H=15 (0.50 LT) | 0.0202 [0.0158, 0.025] | 0.288 [0.149, 0.401] | not determined (n_eff < 50) | 0.0982 [0.0791, 0.116] | loses most |
| oracle | reverse | H=30 (1.00 LT) | 0.0229 [0.0172, 0.029] | 0.361 [0.246, 0.469] | not determined (n_eff < 50) | 0.095 [0.062, 0.129] | loses most |
| oracle | reverse | H=60 (2.00 LT) | 0.0164 [0.0105, 0.0229] | 0.157 [0.0466, 0.26] | loses most | 0.0427 [0.0236, 0.0625] | loses most |
| oracle | reverse | H=120 (4.00 LT) | 0.00959 [0.00441, 0.0146] | 0.272 [-0.108, 0.615] | not determined (interval spans 0.5) | 0.218 [0.14, 0.31] | loses most |
| deployable | forward (g; g_w) | all five | 0.0455 [0.0409, 0.0504] | 0.171 [0.132, 0.209] | loses most | 0.314 [0.271, 0.357] | loses most |
| deployable | forward, one weight | H=8 (0.27 LT) | | 0.0477 [0.0345, 0.0614] | loses most | | |
| deployable | forward, one weight | H=15 (0.50 LT) | | 0.0546 [0.0353, 0.0731] | loses most | | |
| deployable | forward, one weight | H=30 (1.00 LT) | | 0.068 [0.051, 0.0852] | loses most | | |
| deployable | forward, one weight | H=60 (2.00 LT) | | 0.00642 [0.0012, 0.0119] | loses most | | |
| deployable | forward, one weight | H=120 (4.00 LT) | | 0.109 [0.079, 0.137] | loses most | | |
| deployable | reverse | H=8 (0.27 LT) | 0.00532 [0.00369, 0.0072] | 0.24 [-0.0644, 0.552] | not determined (interval spans 0.5) | 0.177 [0.127, 0.228] | loses most |
| deployable | reverse | H=15 (0.50 LT) | 0.00968 [0.00288, 0.0161] | 0.612 [0.335, 1.58] | not determined (n_eff < 50) | 0.17 [0.116, 0.224] | loses most |
| deployable | reverse | H=30 (1.00 LT) | 0.0142 [0.00805, 0.0206] | 0.493 [0.115, 0.788] | not determined (interval spans 0.5) | 0.183 [0.114, 0.255] | loses most |
| deployable | reverse | H=60 (2.00 LT) | 0.00799 [0.00322, 0.0135] | 0.553 [0.048, 1.16] | not determined (interval spans 0.5) | 0.155 [0.0834, 0.225] | loses most |
| deployable | reverse | H=120 (4.00 LT) | 0.00868 [0.00314, 0.015] | 0.608 [0.219, 1.53] | not determined (interval spans 0.5) | 0.446 [0.314, 0.613] | not determined (interval spans 0.5) |

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| profile | forward C-index F / g / g_w | reverse MSE(h)/MSE(F) per horizon | math-spec prediction (both lose most) | largest single-weight retention at H |
|---|---|---|---|---|
| oracle | 0.684 / 0.595 / 0.598 | H=8 (0.27 LT) 4.43 [2.78, 8.54] undetermined (n_eff < 50); H=15 (0.50 LT) 2.29 [1.92, 2.85] undetermined (n_eff < 50); H=30 (1.00 LT) 1.39 [1.25, 1.58] undetermined (n_eff < 50); H=60 (2.00 LT) 1.11 [1.07, 1.15] substantial; H=120 (4.00 LT) 1.01 [1, 1.01] small | **consistent** | 120 |
| deployable | 0.689 / 0.597 / 0.606 | H=8 (0.27 LT) 1.84 [1.44, 2.37] substantial; H=15 (0.50 LT) 1.16 [0.932, 1.49] undetermined (n_eff < 50); H=30 (1.00 LT) 1.14 [1.05, 1.28] needed, size not determined; H=60 (2.00 LT) 1.02 [0.995, 1.06] undetermined; H=120 (4.00 LT) 1 [0.997, 1.01] negligible | **consistent** | 120 |

Oracle against deployable: retained (deployable) minus retained (oracle), paired 95% interval.

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| row | oracle | deployable | difference [CI] | reading |
|---|---|---|---|---|
| forward | 0.148 | 0.171 | 0.0224 [-0.0131, 0.059] | no difference detected |
| forward_w | 0.18 | 0.314 | 0.135 [0.0846, 0.182] | deployable retains more |
| reverse/8 | 0.238 | 0.24 | 0.0029 [-0.378, 0.37] | not determined (n_eff < 50) |
| reverse_w/8 | 0.0761 | 0.177 | 0.101 [0.0578, 0.146] | deployable retains more |
| reverse/15 | 0.288 | 0.612 | 0.324 [0.0143, 1.35] | not determined (n_eff < 50) |
| reverse_w/15 | 0.0982 | 0.17 | 0.072 [0.0199, 0.123] | deployable retains more |
| reverse/30 | 0.361 | 0.493 | 0.132 [-0.262, 0.44] | not determined (n_eff < 50) |
| reverse_w/30 | 0.095 | 0.183 | 0.0882 [0.0268, 0.154] | deployable retains more |
| reverse/60 | 0.157 | 0.553 | 0.396 [-0.128, 1.01] | no difference detected |
| reverse_w/60 | 0.0427 | 0.155 | 0.113 [0.0429, 0.181] | deployable retains more |
| reverse/120 | 0.272 | 0.608 | 0.336 [-0.0757, 1.25] | no difference detected |
| reverse_w/120 | 0.218 | 0.446 | 0.228 [0.105, 0.382] | deployable retains more |

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| horizon | Spearman(phi allocation, phi horizon) (4 items, descriptive) | phi_alloc R/O/I/N | phi_horizon R/O/I/N |
|---|---|---|---|
| H=8 (0.27 LT) | 0.6 | -3e-05/0.0065/0.0024/0.00023 | 0.0011/0.0083/0.033/0.0008 |
| H=15 (0.50 LT) | 0.8 | 0.0024/0.012/0.0032/0.0023 | 0.0011/0.0083/0.033/0.0008 |
| H=30 (1.00 LT) | 0.6 | 0.0011/0.014/0.0072/0.0011 | 0.0011/0.0083/0.033/0.0008 |
| H=60 (2.00 LT) | 0.8 | 0.00082/0.012/0.0037/5e-05 | 0.0011/0.0083/0.033/0.0008 |
| H=120 (4.00 LT) | 0 | 0.0078/-0.00021/0.0014/0.00067 | 0.0011/0.0083/0.033/0.0008 |

### C3. The deployable chain

False trust = P(T <= q_0.1) per (state, draw), target 0.1; T realized (the run's first passage against the noisy truth) or characteristic (moments). Trusted horizon = mean q_0.1 (LT). A4 + KM leaf uses the calibration A4 hybrid's characteristic horizon (no per-draw calibration errors on the full grid).

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| policy | false trust realized [CI] | false trust characteristic [CI] | mean trusted (LT) [CI] | q at cap |
|---|---|---|---|---|
| A2 + constant | 0.072 [0.0661, 0.0783] | 0.103 [0.0952, 0.111] | 0.597 [0.597, 0.597] | 0 |
| A2 + h(F-hat) | 0.104 [0.0972, 0.11] | 0.129 [0.12, 0.138] | 1.06 [1.04, 1.07] | 0 |
| A4 + KM leaf | 0.0679 [0.0627, 0.0736] | 0.102 [0.0943, 0.11] | 1.06 [1.05, 1.07] | 0 |
| g(F-hat) + h(F-hat) | 0.0988 [0.0924, 0.105] | 0.116 [0.108, 0.125] | 1.16 [1.14, 1.17] | 0 |

Hybrid MSE ratio to A2 (realized per draw; 1.05 table, R2 guard).

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| policy | H=8 (0.27 LT) | H=15 (0.50 LT) | H=30 (1.00 LT) | H=60 (2.00 LT) | H=120 (4.00 LT) |
|---|---|---|---|---|---|
| A4 + KM leaf | 2.14 [1.66, 2.61] substantial | 1.27 [1.11, 1.42] substantial | 1.13 [1.08, 1.17] substantial | 1.03 [1, 1.05] small | 1.05 [1.04, 1.07] needed, size not determined |
| g(F-hat) + h(F-hat) | 0.487 [0.405, 0.569] lowers | 0.714 [0.555, 0.896] lowers | 0.78 [0.68, 0.871] lowers | 0.95 [0.917, 0.98] lowers | 0.99 [0.982, 0.996] lowers |

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| full system minus | false trust realized [CI] | false trust characteristic [CI] | trusted LT [CI] |
|---|---|---|---|
| A2 + constant | 0.0267 [0.0199, 0.033] | 0.0132 [0.00375, 0.0223] | 0.561 [0.548, 0.573] |
| A2 + h(F-hat) | -0.00481 [-0.00956, 0] | -0.0128 [-0.0198, -0.0065] | 0.0991 [0.0906, 0.108] |
| A4 + KM leaf | 0.0309 [0.0244, 0.0371] | 0.0144 [0.00531, 0.0232] | 0.0971 [0.0855, 0.108] |

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| horizon model (own characteristic target) | pinball / constant's | constant/model ratio [CI] reading | cov 0.1 / 0.5 / 0.9 | C |
|---|---|---|---|---|
| h_A2(F-hat) | 0.195 / 0.264 | 1.36 [1.32, 1.4] substantial | 0.129 / 0.493 / 0.861 | 0.696 |
| h_g(F-hat) | 0.176 / 0.229 | 1.3 [1.27, 1.33] substantial | 0.116 / 0.488 / 0.86 | - |

### E-H2a. Amplification mismatch m(H) (H_0 = 1 LT; both r.m.s. <= 0.5 sigma_x)

Medians by tercile of I (low / mid / high). Spearman(m, I) on the kept states [95%]. B and A columns from the A/D record (oracle).

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| horizon | kept | m | abs drift w* | corr C/sqrt(E_C E_P) | Spearman(m, I) | B RI / OI | A drop-I (MSE) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 3545 | -0.14 / 0.057 / 0.15 | 0.049 / 0.034 / 0.069 | 0.11 / 0.11 / 0.15 | 0.0879 [0.0535, 0.125] | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=15 (0.50 LT) | 3498 | 0.02 / 0.05 / 0.11 | 0.046 / 0.048 / 0.063 | 0.11 / 0.14 / 0.15 | 0.0608 [0.0269, 0.0944] | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=30 (1.00 LT) | 3584 | 0 / 0 / 0 | 0 / 0 / 0 | 0.12 / 0.13 / 0.2 | (H_0) | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=60 (2.00 LT) | 2786 | -0.14 / 0.085 / 0.029 | 0.055 / 0.084 / 0.079 | 0.14 / 0.19 / 0.2 | 0.0454 [0.00813, 0.0823] | interaction gain detected / interaction gain detected | undetermined |
| H=120 (4.00 LT) | 609 | -1.5 / -2 / -2.8 | 0.28 / 0.42 / 0.47 | 0.25 / 0.31 / 0.31 | -0.14 [-0.22, -0.0629] | interaction gain detected / interaction gain detected | negligible |

**Reading: not determined** (horizons_used: ['60', '120'], horizons_supporting: [], horizons_null: ['60']).

### E-H2e. Library size and error correlation (sweep states)

1000 sweep states. Delta = value at N_lib 100000 minus 1000. corr = the H2e correlation (0 by convention where an error is constant over the draws).

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| rho | valid | corr 0 small / large lib | median corr small -> large | set | median Delta corr [CI] | Spearman(Delta corr, Delta R) [CI] | reading |
|---|---|---|---|---|---|---|---|
| 0.01 | 1000 | 697 / 13 | 0 -> 0.42 | all (1000) | 0.355 [0.33, 0.376] | 0.183 [0.127, 0.242] | not consistent |
| 0.01 | 1000 | 697 / 13 | 0 -> 0.42 | both_defined (301) | 0.167 [0.122, 0.23] | 0.0577 [-0.0534, 0.167] | not determined |
| 0.02 | 1000 | 431 / 0 | 0 -> 0.451 | all (1000) | 0.316 [0.295, 0.334] | 0.131 [0.0714, 0.195] | not consistent |
| 0.02 | 1000 | 431 / 0 | 0 -> 0.451 | both_defined (569) | 0.213 [0.186, 0.245] | 0.0622 [-0.0225, 0.152] | not determined |

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| rho | stratifier | median Delta corr low / mid / high | median Delta R low / mid / high |
|---|---|---|---|
| 0.01 | R | 0.37 / 0.36 / 0.32 | -1.5 / -1.5 / -1.8 |
| 0.01 | O | 0.38 / 0.38 / 0.28 | -1.5 / -1.6 / -1.7 |
| 0.01 | I | 0.33 / 0.37 / 0.36 | -1.9 / -1.5 / -1.4 |
| 0.01 | N | 0.32 / 0.38 / 0.36 | -1.7 / -1.4 / -1.6 |
| 0.01 | delta_R | 0.3 / 0.32 / 0.42 | -2.4 / -1.6 / -0.7 |
| 0.02 | R | 0.31 / 0.33 / 0.31 | -0.98 / -0.97 / -1.2 |
| 0.02 | O | 0.33 / 0.35 / 0.25 | -1 / -1 / -1.1 |
| 0.02 | I | 0.32 / 0.33 / 0.3 | -1.4 / -1 / -0.87 |
| 0.02 | N | 0.28 / 0.34 / 0.32 | -1.2 / -0.91 / -1.1 |
| 0.02 | delta_R | 0.29 / 0.26 / 0.37 | -1.9 / -1 / -0.21 |

**Reading** (final, after the convention check): rho 0.01: not determined (depends on the zero-variance convention); rho 0.02: not determined (depends on the zero-variance convention).

### E-H3c. A5 against A4

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| item | value |
|---|---|
| H3c ratio MSE(A5)/MSE(A4) [CI at level 0.983] (run) | 0.776 [0.688, 0.865], width 0.177 |
| top-1% share: A5 loss / A4 loss / abs(A5 - A4) | 0.574 / 0.588 / 0.66 |
| autocorrelation of d = A5 - A4, lags 1..5 | 0.00075, -0.0051, -0.0046, 0.0067, -0.0047 |
| block-5 means: lag-1 autocorrelation, variance ratio | -0.0075, 1.01 |
| K chosen; leaves used test / calibration; largest leaf share test | 6; 6 / 6; 0.315 |
| w*(H_ref) within-leaf share of variance | 0.914 |
| bimodality coefficient R/O/I/N, oracle; deployable | 0.28/0.78/0.55/0.83; 0.33/0.42/0.54/0.89 |
| Spearman pairs (oracle) | RO 0.52, RI -0.036, RN 0.31, OI -0.015, ON -0.043, IN 0.069 |
| top-1% abs(d) states: mean percentile R/O/I/N | 0.78/0.92/0.48/0.35 |
| top-1% abs(d) states: median I pct; share high-I; median abs(x) pct; share sign change in window; share of sum d | 0.277; 0.35; 0.698; 0.675; 0.933 |

## rossler

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| check | result |
|---|---|
| A2 rebuilt on 1..H_max equals the dumped A2 (bitwise); A4 horizon-free | True, True |
| refit reproduces WU-0048 (max abs: A/ROIN MSE oracle, deployable; W/ROIN L_w oracle, deployable) | 0 / 0 / 0 / 0 |
| T_c counts T = 1 / e_(T-1) = theta (A2 train, g train, A2 test, g test, A4 calibration) | 0/0, 0/0, 0/0, 0/0, 0/0 |
| A2 on 1..H_max: pooled curvature floor / columns at 0 or 1 | 0 / 0 |
| weights clipped to [0, 1] | g_oracle_test 3387, g_oracle_train_oof 2283, gw_oracle_test 2201, gw_oracle_train_oof 1692, g_deployable_test 9405, g_deployable_train_oof 7015, gw_deployable_test 1169, gw_deployable_train_oof 1015 |

### C1. Separate performance (from the A/D record, no refit)

Allocation: MSE per rule (oracle: moment form; deployable: realized); reading of the rung against F (MSE ratio, 1.05 table, n_eff guard). G(F) = 1 - L_A(F)/L_A(constant).

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| horizon | profile | constant | separation | RO | F (ROIN) | X | X+F | G(F) | sep vs F | RO vs F | X+F vs F |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 0.000126 | 0.000122 | 0.000116 | 0.000115 | 0.000125 | 0.000115 | 0.503 | needed, size not determined | small | negligible |
| H=8 (0.27 LT) | deployable | 0.000126 | 0.000134 | 0.000125 | 0.000125 | 0.000124 | 0.000124 | 0.0403 | substantial | negligible | lowers |
| H=15 (0.50 LT) | oracle | 0.000224 | 0.000211 | 0.000203 | 0.000201 | 0.00022 | 0.0002 | 0.556 | needed, size not determined | small | lowers |
| H=15 (0.50 LT) | deployable | 0.000227 | 0.000238 | 0.000225 | 0.000225 | 0.000223 | 0.000223 | 0.0452 | needed, size not determined | negligible | lowers |
| H=30 (1.00 LT) | oracle | 0.0008 | 0.000726 | 0.000713 | 0.000704 | 0.000788 | 0.000707 | 0.645 | small | small | negligible |
| H=30 (1.00 LT) | deployable | 0.000811 | 0.000836 | 0.000809 | 0.000806 | 0.000799 | 0.000798 | 0.0301 | needed, size not determined | negligible | lowers |
| H=60 (2.00 LT) | oracle | 0.0127 | 0.0116 | 0.0117 | 0.0116 | 0.0127 | 0.0116 | 0.291 | negligible | small | negligible |
| H=60 (2.00 LT) | deployable | 0.0135 | 0.0133 | 0.0133 | 0.0133 | 0.0134 | 0.0133 | 0.0461 | negligible | negligible | negligible |
| H=120 (4.00 LT) | oracle | 0.108 | 0.113 | 0.106 | 0.106 | 0.107 | 0.105 | 0.0543 | needed, size not determined | negligible | negligible |
| H=120 (4.00 LT) | deployable | 0.109 | 0.117 | 0.109 | 0.108 | 0.109 | 0.107 | 0.0433 | substantial | small | negligible |

Horizon (Y = ln min(T_c, H_max)): pinball at 0.5 / Harrell's C / coverage of q_0.1 below the cap; reading against F.

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | C | cov q_0.1 | reading vs F |
|---|---|---|---|---|---|
| oracle | none | 0.16 | 0.5 | 0.102 | substantial |
| oracle | lyapunov | 0.172 | 0.637 | 0.0767 | substantial |
| oracle | RO | 0.154 | 0.566 | 0.101 | substantial |
| oracle | ROIN | 0.123 | 0.682 | 0.144 |  |
| oracle | X | 0.122 | 0.696 | 0.15 | negligible |
| oracle | X+F | 0.0951 | 0.765 | 0.149 | lowers |
| oracle | Lyapunov rank | | 0.635 | | |
| deployable | none | 0.16 | 0.5 | 0.102 | substantial |
| deployable | lyapunov | 0.172 | 0.632 | 0.0786 | substantial |
| deployable | RO | 0.147 | 0.602 | 0.0997 | substantial |
| deployable | ROIN | 0.118 | 0.697 | 0.124 |  |
| deployable | X | 0.124 | 0.692 | 0.141 | needed, size not determined |
| deployable | X+F | 0.0919 | 0.769 | 0.142 | lowers |
| deployable | Lyapunov rank | | 0.63 | | |

### C2. Shared information (oracle and deployable profiles)

Skill retained = [L(constant) - L(bottleneck)] / [L(constant) - L(F)]; reading: keeps most (CI > 0.5), loses most (CI < 0.5), else not determined. Forward: horizon from g (five clipped weights; g_w: the L_w fits); reverse: weight from h (three quantiles), scored by L_A (MSE; deployable: realized per draw, R2 guard) and by L_w (weight units, unit-weight fits). Training inputs cross-fitted.

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| profile | direction | horizon | full skill [CI] | retained L_A / pinball [CI] | reading | retained L_w [CI] | reading L_w |
|---|---|---|---|---|---|---|---|
| oracle | forward (g; g_w) | all five | 0.0375 [0.0338, 0.0412] | 0.375 [0.318, 0.426] | loses most | 0.561 [0.505, 0.613] | keeps most |
| oracle | forward, one weight | H=8 (0.27 LT) | | 0.0321 [0.0111, 0.0521] | loses most | | |
| oracle | forward, one weight | H=15 (0.50 LT) | | 0.0227 [0.00135, 0.043] | loses most | | |
| oracle | forward, one weight | H=30 (1.00 LT) | | 0.0419 [0.0192, 0.064] | loses most | | |
| oracle | forward, one weight | H=60 (2.00 LT) | | 0.0574 [0.0331, 0.0791] | loses most | | |
| oracle | forward, one weight | H=120 (4.00 LT) | | 0.204 [0.155, 0.25] | loses most | | |
| oracle | reverse | H=8 (0.27 LT) | 1.14e-05 [1.05e-05, 1.24e-05] | 0.265 [0.22, 0.305] | loses most | 0.331 [0.279, 0.381] | loses most |
| oracle | reverse | H=15 (0.50 LT) | 2.28e-05 [2.01e-05, 2.55e-05] | 0.29 [0.242, 0.336] | loses most | 0.359 [0.307, 0.41] | loses most |
| oracle | reverse | H=30 (1.00 LT) | 9.51e-05 [8.29e-05, 0.000109] | 0.189 [0.107, 0.259] | loses most | 0.393 [0.347, 0.437] | loses most |
| oracle | reverse | H=60 (2.00 LT) | 0.00108 [0.000842, 0.00132] | 0.288 [0.197, 0.389] | loses most | 0.387 [0.34, 0.436] | loses most |
| oracle | reverse | H=120 (4.00 LT) | 0.00167 [0.00113, 0.00221] | 0.516 [0.23, 0.838] | not determined (interval spans 0.5) | 0.454 [0.346, 0.567] | not determined (interval spans 0.5) |
| deployable | forward (g; g_w) | all five | 0.0422 [0.0386, 0.0457] | 0.461 [0.416, 0.5] | loses most | 0.595 [0.554, 0.634] | keeps most |
| deployable | forward, one weight | H=8 (0.27 LT) | | 0.0164 [0.0019, 0.0299] | loses most | | |
| deployable | forward, one weight | H=15 (0.50 LT) | | 0.0131 [-0.00321, 0.0277] | loses most | | |
| deployable | forward, one weight | H=30 (1.00 LT) | | 0.0214 [0.00599, 0.0368] | loses most | | |
| deployable | forward, one weight | H=60 (2.00 LT) | | 0.105 [0.0827, 0.127] | loses most | | |
| deployable | forward, one weight | H=120 (4.00 LT) | | 0.292 [0.249, 0.33] | loses most | | |
| deployable | reverse | H=8 (0.27 LT) | 8.87e-07 [-3.26e-08, 1.8e-06] | -0.337 [-, -] | not determined (full-profile skill not established) | 0.0631 [0.0167, 0.112] | loses most |
| deployable | reverse | H=15 (0.50 LT) | 2e-06 [-5.81e-07, 4.57e-06] | 0.129 [-, -] | not determined (full-profile skill not established) | 0.0957 [0.0553, 0.142] | loses most |
| deployable | reverse | H=30 (1.00 LT) | 4.78e-06 [-5.3e-06, 1.41e-05] | -0.714 [-, -] | not determined (full-profile skill not established) | 0.109 [0.069, 0.149] | loses most |
| deployable | reverse | H=60 (2.00 LT) | 0.000207 [3.73e-05, 0.000381] | 0.0595 [-0.744, 0.538] | not determined (interval spans 0.5) | 0.239 [0.138, 0.333] | loses most |
| deployable | reverse | H=120 (4.00 LT) | 0.0014 [0.000852, 0.00192] | 0.811 [0.558, 1.24] | keeps most | 0.521 [0.321, 0.722] | not determined (interval spans 0.5) |

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| profile | forward C-index F / g / g_w | reverse MSE(h)/MSE(F) per horizon | math-spec prediction (both lose most) | largest single-weight retention at H |
|---|---|---|---|---|
| oracle | 0.682 / 0.591 / 0.626 | H=8 (0.27 LT) 1.07 [1.07, 1.08] substantial; H=15 (0.50 LT) 1.08 [1.07, 1.09] substantial; H=30 (1.00 LT) 1.11 [1.09, 1.13] substantial; H=60 (2.00 LT) 1.07 [1.05, 1.09] needed, size not determined; H=120 (4.00 LT) 1.01 [1, 1.01] small | **consistent** | 120 |
| deployable | 0.697 / 0.616 / 0.641 | H=8 (0.27 LT) 1.01 [1, 1.02] small; H=15 (0.50 LT) 1.01 [0.997, 1.02] negligible; H=30 (1.00 LT) 1.01 [0.998, 1.02] negligible; H=60 (2.00 LT) 1.01 [1, 1.03] small; H=120 (4.00 LT) 1 [0.998, 1.01] negligible | **not consistent** | 120 |

Oracle against deployable: retained (deployable) minus retained (oracle), paired 95% interval.

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| row | oracle | deployable | difference [CI] | reading |
|---|---|---|---|---|
| forward | 0.375 | 0.461 | 0.086 [0.0345, 0.139] | deployable retains more |
| forward_w | 0.561 | 0.595 | 0.0342 [-0.0211, 0.088] | no difference detected |
| reverse/8 | 0.265 | -0.337 | -0.601 [-, -] | not determined (full-profile skill not established) |
| reverse_w/8 | 0.331 | 0.0631 | -0.268 [-0.328, -0.203] | deployable retains less |
| reverse/15 | 0.29 | 0.129 | -0.161 [-, -] | not determined (full-profile skill not established) |
| reverse_w/15 | 0.359 | 0.0957 | -0.263 [-0.321, -0.203] | deployable retains less |
| reverse/30 | 0.189 | -0.714 | -0.904 [-, -] | not determined (full-profile skill not established) |
| reverse_w/30 | 0.393 | 0.109 | -0.284 [-0.335, -0.229] | deployable retains less |
| reverse/60 | 0.288 | 0.0595 | -0.229 [-1.03, 0.237] | no difference detected |
| reverse_w/60 | 0.387 | 0.239 | -0.148 [-0.246, -0.0475] | deployable retains less |
| reverse/120 | 0.516 | 0.811 | 0.294 [-0.0633, 0.755] | no difference detected |
| reverse_w/120 | 0.454 | 0.521 | 0.0678 [-0.115, 0.258] | no difference detected |

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| horizon | Spearman(phi allocation, phi horizon) (4 items, descriptive) | phi_alloc R/O/I/N | phi_horizon R/O/I/N |
|---|---|---|---|
| H=8 (0.27 LT) | -1 | 7.6e-06/1.1e-06/-4e-08/2.8e-06 | 0.0013/0.0084/0.026/0.0017 |
| H=15 (0.50 LT) | -1 | 1.6e-05/2.2e-06/2e-08/5e-06 | 0.0013/0.0084/0.026/0.0017 |
| H=30 (1.00 LT) | -1 | 6.4e-05/1.3e-05/8.5e-07/1.7e-05 | 0.0013/0.0084/0.026/0.0017 |
| H=60 (2.00 LT) | -1 | 0.00086/3.2e-05/3.1e-05/0.00016 | 0.0013/0.0084/0.026/0.0017 |
| H=120 (4.00 LT) | -0.2 | 0.0011/9.4e-05/0.00062/-0.00012 | 0.0013/0.0084/0.026/0.0017 |

### C3. The deployable chain

False trust = P(T <= q_0.1) per (state, draw), target 0.1; T realized (the run's first passage against the noisy truth) or characteristic (moments). Trusted horizon = mean q_0.1 (LT). A4 + KM leaf uses the calibration A4 hybrid's characteristic horizon (no per-draw calibration errors on the full grid).

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| policy | false trust realized [CI] | false trust characteristic [CI] | mean trusted (LT) [CI] | q at cap |
|---|---|---|---|---|
| A2 + constant | 0.0981 [0.0918, 0.104] | 0.108 [0.0995, 0.118] | 1.89 [1.89, 1.89] | 0 |
| A2 + h(F-hat) | 0.14 [0.133, 0.147] | 0.13 [0.121, 0.141] | 2.23 [2.22, 2.25] | 0 |
| A4 + KM leaf | 0.105 [0.0986, 0.112] | 0.11 [0.101, 0.119] | 2.04 [2.03, 2.05] | 0 |
| g(F-hat) + h(F-hat) | 0.143 [0.136, 0.15] | 0.126 [0.117, 0.136] | 2.29 [2.27, 2.3] | 0 |

Hybrid MSE ratio to A2 (realized per draw; 1.05 table, R2 guard).

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| policy | H=8 (0.27 LT) | H=15 (0.50 LT) | H=30 (1.00 LT) | H=60 (2.00 LT) | H=120 (4.00 LT) |
|---|---|---|---|---|---|
| A4 + KM leaf | 1.07 [1.05, 1.09] substantial | 1.05 [1.03, 1.07] needed, size not determined | 1.03 [1.01, 1.05] needed, size not determined | 0.988 [0.97, 1.01] negligible | 1.07 [1.06, 1.09] substantial |
| g(F-hat) + h(F-hat) | 0.993 [0.986, 1] negligible | 0.991 [0.98, 1] negligible | 0.994 [0.983, 1.01] negligible | 0.983 [0.971, 0.996] lowers | 0.988 [0.983, 0.993] lowers |

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| full system minus | false trust realized [CI] | false trust characteristic [CI] | trusted LT [CI] |
|---|---|---|---|
| A2 + constant | 0.0447 [0.0386, 0.0508] | 0.0176 [0.00718, 0.0282] | 0.394 [0.374, 0.414] |
| A2 + h(F-hat) | 0.00287 [-0.00106, 0.0065] | -0.004 [-0.00944, 0.00106] | 0.0524 [0.0483, 0.0562] |
| A4 + KM leaf | 0.0378 [0.0318, 0.0436] | 0.0161 [0.00769, 0.0248] | 0.244 [0.231, 0.257] |

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| horizon model (own characteristic target) | pinball / constant's | constant/model ratio [CI] reading | cov 0.1 / 0.5 / 0.9 | C |
|---|---|---|---|---|
| h_A2(F-hat) | 0.104 / 0.151 | 1.46 [1.42, 1.5] substantial | 0.13 / 0.499 / 0.875 | 0.715 |
| h_g(F-hat) | 0.103 / 0.155 | 1.5 [1.46, 1.54] substantial | 0.126 / 0.504 / 0.879 | - |

### E-H2a. Amplification mismatch m(H) (H_0 = 1 LT; both r.m.s. <= 0.5 sigma_x)

Medians by tercile of I (low / mid / high). Spearman(m, I) on the kept states [95%]. B and A columns from the A/D record (oracle).

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| horizon | kept | m | abs drift w* | corr C/sqrt(E_C E_P) | Spearman(m, I) | B RI / OI | A drop-I (MSE) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 3987 | -0.18 / 0.083 / 0.097 | 0.081 / 0.09 / 0.067 | 0.18 / 0.16 / 0.17 | 0.103 [0.0715, 0.134] | no interaction gain detected / no interaction gain detected | negligible |
| H=15 (0.50 LT) | 3987 | -0.14 / 0.078 / 0.063 | 0.075 / 0.079 / 0.053 | 0.19 / 0.18 / 0.19 | 0.0719 [0.0403, 0.103] | no interaction gain detected / interaction gain detected | negligible |
| H=30 (1.00 LT) | 3987 | 0 / 0 / 0 | 0 / 0 / 0 | 0.21 / 0.2 / 0.2 | (H_0) | no interaction gain detected / interaction gain detected | negligible |
| H=60 (2.00 LT) | 3669 | -0.17 / -0.25 / -0.35 | 0.079 / 0.11 / 0.11 | 0.24 / 0.24 / 0.29 | -0.0707 [-0.104, -0.0366] | interaction gain detected / interaction gain detected | negligible |
| H=120 (4.00 LT) | 2806 | -1.5 / -1.6 / -1.6 | 0.28 / 0.32 / 0.34 | 0.32 / 0.36 / 0.37 | -0.0167 [-0.0529, 0.0226] | no interaction gain detected / no interaction gain detected | small |

**Reading: not determined** (horizons_used: ['60', '120'], horizons_supporting: [], horizons_null: ['120']).

### E-H2e. Library size and error correlation (sweep states)

1000 sweep states. Delta = value at N_lib 100000 minus 1000. corr = the H2e correlation (0 by convention where an error is constant over the draws).

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| rho | valid | corr 0 small / large lib | median corr small -> large | set | median Delta corr [CI] | Spearman(Delta corr, Delta R) [CI] | reading |
|---|---|---|---|---|---|---|---|
| 0.01 | 1000 | 590 / 0 | 0 -> 0.446 | all (1000) | 0.372 [0.344, 0.39] | 0.171 [0.107, 0.23] | not consistent |
| 0.01 | 1000 | 590 / 0 | 0 -> 0.446 | both_defined (410) | 0.199 [0.159, 0.227] | 0.000611 [-0.095, 0.107] | not determined |
| 0.02 | 1000 | 310 / 0 | 0.104 -> 0.462 | all (1000) | 0.293 [0.275, 0.316] | 0.124 [0.0654, 0.184] | not consistent |
| 0.02 | 1000 | 310 / 0 | 0.104 -> 0.462 | both_defined (690) | 0.195 [0.165, 0.223] | 0.016 [-0.0541, 0.0889] | not determined |

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| rho | stratifier | median Delta corr low / mid / high | median Delta R low / mid / high |
|---|---|---|---|
| 0.01 | R | 0.33 / 0.37 / 0.39 | -1.2 / -1.3 / -1.5 |
| 0.01 | O | 0.36 / 0.36 / 0.38 | -1.4 / -1.4 / -1.4 |
| 0.01 | I | 0.3 / 0.36 / 0.44 | -1.4 / -1.4 / -1.4 |
| 0.01 | N | 0.36 / 0.36 / 0.38 | -1.5 / -1.1 / -1.5 |
| 0.01 | delta_R | 0.28 / 0.38 / 0.42 | -2 / -1.4 / -0.5 |
| 0.02 | R | 0.28 / 0.3 / 0.31 | -0.7 / -0.79 / -1 |
| 0.02 | O | 0.3 / 0.26 / 0.3 | -0.83 / -0.85 / -0.83 |
| 0.02 | I | 0.22 / 0.29 / 0.35 | -0.8 / -0.87 / -0.84 |
| 0.02 | N | 0.3 / 0.29 / 0.3 | -0.97 / -0.58 / -0.89 |
| 0.02 | delta_R | 0.28 / 0.27 / 0.34 | -1.4 / -0.84 / -0.082 |

**Reading** (final, after the convention check): rho 0.01: not determined (depends on the zero-variance convention); rho 0.02: not determined (depends on the zero-variance convention).

### E-H3c. A5 against A4

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| item | value |
|---|---|
| H3c ratio MSE(A5)/MSE(A4) [CI at level 0.983] (run) | 0.972 [0.948, 0.996], width 0.0487 |
| top-1% share: A5 loss / A4 loss / abs(A5 - A4) | 0.178 / 0.172 / 0.197 |
| autocorrelation of d = A5 - A4, lags 1..5 | 0.0063, 0.0055, 0.0035, -0.0031, 0.014 |
| block-5 means: lag-1 autocorrelation, variance ratio | -0.0477, 1.05 |
| K chosen; leaves used test / calibration; largest leaf share test | 4; 4 / 4; 0.303 |
| w*(H_ref) within-leaf share of variance | 0.959 |
| bimodality coefficient R/O/I/N, oracle; deployable | 0.28/0.78/0.46/0.84; 0.5/0.8/0.46/0.9 |
| Spearman pairs (oracle) | RO 0.4, RI 0.0045, RN 0.39, OI -0.034, ON 0.0054, IN -0.033 |
| top-1% abs(d) states: mean percentile R/O/I/N | 0.73/0.86/0.76/0.43 |
| top-1% abs(d) states: median I pct; share high-I; median abs(x) pct; share sign change in window; share of sum d | 0.841; 0.75; 0.498; 1; 0.224 |

## chua

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| check | result |
|---|---|
| A2 rebuilt on 1..H_max equals the dumped A2 (bitwise); A4 horizon-free | True, True |
| refit reproduces WU-0048 (max abs: A/ROIN MSE oracle, deployable; W/ROIN L_w oracle, deployable) | 0 / 0 / 0 / 0 |
| T_c counts T = 1 / e_(T-1) = theta (A2 train, g train, A2 test, g test, A4 calibration) | 4/0, 17/0, 2/0, 8/0, 12/0 |
| A2 on 1..H_max: pooled curvature floor / columns at 0 or 1 | 0 / 0 |
| weights clipped to [0, 1] | g_oracle_test 1721, g_oracle_train_oof 1545, gw_oracle_test 2002, gw_oracle_train_oof 1508, g_deployable_test 4473, g_deployable_train_oof 3841, gw_deployable_test 1376, gw_deployable_train_oof 976 |

### C1. Separate performance (from the A/D record, no refit)

Allocation: MSE per rule (oracle: moment form; deployable: realized); reading of the rung against F (MSE ratio, 1.05 table, n_eff guard). G(F) = 1 - L_A(F)/L_A(constant).

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| horizon | profile | constant | separation | RO | F (ROIN) | X | X+F | G(F) | sep vs F | RO vs F | X+F vs F |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 0.000668 | 0.000593 | 0.000614 | 0.000629 | 0.000626 | 0.000634 | 0.234 | undetermined | undetermined | undetermined |
| H=8 (0.27 LT) | deployable | 0.00056 | 0.000626 | 0.000567 | 0.000566 | 0.000569 | 0.000562 | -0.0953 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | oracle | 0.00272 | 0.00252 | 0.0026 | 0.00262 | 0.00269 | 0.00261 | 0.168 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | deployable | 0.00266 | 0.00284 | 0.00269 | 0.00268 | 0.00264 | 0.00265 | -0.0319 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | oracle | 0.0184 | 0.0173 | 0.0178 | 0.0177 | 0.0182 | 0.0178 | 0.114 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | deployable | 0.0196 | 0.0194 | 0.0194 | 0.0192 | 0.0195 | 0.0191 | 0.0614 | undetermined | undetermined | undetermined |
| H=60 (2.00 LT) | oracle | 0.193 | 0.184 | 0.181 | 0.183 | 0.191 | 0.182 | 0.141 | negligible | negligible | negligible |
| H=60 (2.00 LT) | deployable | 0.189 | 0.19 | 0.188 | 0.185 | 0.187 | 0.185 | 0.0606 | needed, size not determined | small | negligible |
| H=120 (4.00 LT) | oracle | 0.63 | 0.639 | 0.613 | 0.612 | 0.627 | 0.612 | 0.1 | needed, size not determined | negligible | negligible |
| H=120 (4.00 LT) | deployable | 0.636 | 0.659 | 0.624 | 0.621 | 0.633 | 0.623 | 0.0759 | needed, size not determined | small | negligible |

Horizon (Y = ln min(T_c, H_max)): pinball at 0.5 / Harrell's C / coverage of q_0.1 below the cap; reading against F.

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | C | cov q_0.1 | reading vs F |
|---|---|---|---|---|---|
| oracle | none | 0.224 | 0.5 | 0.0978 | substantial |
| oracle | lyapunov | 0.261 | 0.672 | 0.0878 | substantial |
| oracle | RO | 0.203 | 0.625 | 0.106 | substantial |
| oracle | ROIN | 0.164 | 0.704 | 0.119 |  |
| oracle | X | 0.173 | 0.696 | 0.145 | needed, size not determined |
| oracle | X+F | 0.138 | 0.764 | 0.163 | lowers |
| oracle | Lyapunov rank | | 0.664 | | |
| deployable | none | 0.224 | 0.5 | 0.0978 | substantial |
| deployable | lyapunov | 0.26 | 0.67 | 0.0836 | substantial |
| deployable | RO | 0.198 | 0.634 | 0.11 | substantial |
| deployable | ROIN | 0.162 | 0.712 | 0.133 |  |
| deployable | X | 0.173 | 0.697 | 0.14 | needed, size not determined |
| deployable | X+F | 0.139 | 0.762 | 0.146 | lowers |
| deployable | Lyapunov rank | | 0.661 | | |

### C2. Shared information (oracle and deployable profiles)

Skill retained = [L(constant) - L(bottleneck)] / [L(constant) - L(F)]; reading: keeps most (CI > 0.5), loses most (CI < 0.5), else not determined. Forward: horizon from g (five clipped weights; g_w: the L_w fits); reverse: weight from h (three quantiles), scored by L_A (MSE; deployable: realized per draw, R2 guard) and by L_w (weight units, unit-weight fits). Training inputs cross-fitted.

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| profile | direction | horizon | full skill [CI] | retained L_A / pinball [CI] | reading | retained L_w [CI] | reading L_w |
|---|---|---|---|---|---|---|---|
| oracle | forward (g; g_w) | all five | 0.0602 [0.0547, 0.0652] | 0.439 [0.395, 0.483] | loses most | 0.597 [0.553, 0.647] | keeps most |
| oracle | forward, one weight | H=8 (0.27 LT) | | -0.0156 [-0.0261, -0.00602] | loses most | | |
| oracle | forward, one weight | H=15 (0.50 LT) | | 0.0366 [0.0213, 0.0527] | loses most | | |
| oracle | forward, one weight | H=30 (1.00 LT) | | 0.0876 [0.0644, 0.111] | loses most | | |
| oracle | forward, one weight | H=60 (2.00 LT) | | 0.115 [0.0852, 0.146] | loses most | | |
| oracle | forward, one weight | H=120 (4.00 LT) | | 0.0697 [0.048, 0.0941] | loses most | | |
| oracle | reverse | H=8 (0.27 LT) | 3.88e-05 [-7e-05, 0.000134] | 0.146 [-, -] | not determined (full-profile skill not established) | 0.282 [0.209, 0.346] | loses most |
| oracle | reverse | H=15 (0.50 LT) | 0.000102 [-1.04e-06, 0.000193] | -0.275 [-, -] | not determined (full-profile skill not established) | 0.302 [0.25, 0.352] | loses most |
| oracle | reverse | H=30 (1.00 LT) | 0.000648 [0.000162, 0.00126] | 0.407 [-0.608, 1.38] | not determined (n_eff < 50) | 0.37 [0.32, 0.421] | loses most |
| oracle | reverse | H=60 (2.00 LT) | 0.00941 [0.00497, 0.0137] | 0.151 [-0.0113, 0.337] | loses most | 0.467 [0.41, 0.527] | not determined (interval spans 0.5) |
| oracle | reverse | H=120 (4.00 LT) | 0.0189 [0.015, 0.023] | 0.288 [0.193, 0.412] | loses most | 0.296 [0.221, 0.377] | loses most |
| deployable | forward (g; g_w) | all five | 0.0627 [0.0577, 0.0673] | 0.654 [0.618, 0.687] | keeps most | 0.594 [0.558, 0.628] | keeps most |
| deployable | forward, one weight | H=8 (0.27 LT) | | 0.0907 [0.0723, 0.108] | loses most | | |
| deployable | forward, one weight | H=15 (0.50 LT) | | -0.00207 [-0.0155, 0.0126] | loses most | | |
| deployable | forward, one weight | H=30 (1.00 LT) | | 0.281 [0.252, 0.31] | loses most | | |
| deployable | forward, one weight | H=60 (2.00 LT) | | 0.111 [0.0903, 0.134] | loses most | | |
| deployable | forward, one weight | H=120 (4.00 LT) | | 0.216 [0.185, 0.248] | loses most | | |
| deployable | reverse | H=8 (0.27 LT) | -5.52e-06 [-1.74e-05, 3.48e-06] | - [-, -] | not determined (full-profile skill not established) | 0.112 [0.0554, 0.166] | loses most |
| deployable | reverse | H=15 (0.50 LT) | -1.75e-05 [-9.81e-05, 6.9e-05] | - [-, -] | not determined (full-profile skill not established) | 0.247 [0.156, 0.329] | loses most |
| deployable | reverse | H=30 (1.00 LT) | 0.000427 [-2.28e-05, 0.000987] | 0.994 [-, -] | not determined (full-profile skill not established) | 0.361 [0.286, 0.428] | loses most |
| deployable | reverse | H=60 (2.00 LT) | 0.0038 [0.00102, 0.00649] | 0.196 [-0.798, 0.794] | not determined (interval spans 0.5) | 0.488 [0.42, 0.55] | not determined (interval spans 0.5) |
| deployable | reverse | H=120 (4.00 LT) | 0.0148 [0.0113, 0.0185] | 0.415 [0.305, 0.552] | not determined (interval spans 0.5) | 0.555 [0.393, 0.724] | not determined (interval spans 0.5) |

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| profile | forward C-index F / g / g_w | reverse MSE(h)/MSE(F) per horizon | math-spec prediction (both lose most) | largest single-weight retention at H |
|---|---|---|---|---|
| oracle | 0.704 / 0.64 / 0.667 | H=8 (0.27 LT) 1.05 [0.896, 1.2] undetermined (n_eff < 50); H=15 (0.50 LT) 1.05 [1.01, 1.09] undetermined (n_eff < 50); H=30 (1.00 LT) 1.02 [0.995, 1.05] undetermined (n_eff < 50); H=60 (2.00 LT) 1.04 [1.02, 1.07] needed, size not determined; H=120 (4.00 LT) 1.02 [1.02, 1.03] small | **consistent** | 60 |
| deployable | 0.712 / 0.669 / 0.671 | H=8 (0.27 LT) 1 [0.986, 1.02] undetermined (n_eff < 50); H=15 (0.50 LT) 1 [0.971, 1.03] undetermined (n_eff < 50); H=30 (1.00 LT) 1 [0.98, 1.02] undetermined (n_eff < 50); H=60 (2.00 LT) 1.02 [1, 1.03] small; H=120 (4.00 LT) 1.01 [1.01, 1.02] small | **not consistent** | 30 |

Oracle against deployable: retained (deployable) minus retained (oracle), paired 95% interval.

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| row | oracle | deployable | difference [CI] | reading |
|---|---|---|---|---|
| forward | 0.439 | 0.654 | 0.215 [0.168, 0.259] | deployable retains more |
| forward_w | 0.597 | 0.594 | -0.00303 [-0.0507, 0.0397] | no difference detected |
| reverse/8 | 0.146 | - | - [-, -] | not determined (full-profile skill not established) |
| reverse_w/8 | 0.282 | 0.112 | -0.17 [-0.251, -0.0877] | deployable retains less |
| reverse/15 | -0.275 | - | - [-, -] | not determined (full-profile skill not established) |
| reverse_w/15 | 0.302 | 0.247 | -0.0551 [-0.148, 0.0361] | no difference detected |
| reverse/30 | 0.407 | 0.994 | 0.587 [-, -] | not determined (n_eff < 50) |
| reverse_w/30 | 0.37 | 0.361 | -0.00859 [-0.0746, 0.0581] | no difference detected |
| reverse/60 | 0.151 | 0.196 | 0.0448 [-0.933, 0.586] | no difference detected |
| reverse_w/60 | 0.467 | 0.488 | 0.0202 [-0.0496, 0.0901] | no difference detected |
| reverse/120 | 0.288 | 0.415 | 0.128 [-0.0049, 0.264] | no difference detected |
| reverse_w/120 | 0.296 | 0.555 | 0.259 [0.119, 0.411] | deployable retains more |

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| horizon | Spearman(phi allocation, phi horizon) (4 items, descriptive) | phi_alloc R/O/I/N | phi_horizon R/O/I/N |
|---|---|---|---|
| H=8 (0.27 LT) | -0.2 | 1.9e-05/2.3e-05/-6.2e-06/3.5e-06 | 0.0019/0.014/0.043/0.0013 |
| H=15 (0.50 LT) | 0.2 | 3.5e-05/3.2e-05/1.8e-05/1.7e-05 | 0.0019/0.014/0.043/0.0013 |
| H=30 (1.00 LT) | -0.6 | 0.00055/-0.00024/0.00015/0.00018 | 0.0019/0.014/0.043/0.0013 |
| H=60 (2.00 LT) | -0.4 | 0.009/0.00048/-0.00037/0.00035 | 0.0019/0.014/0.043/0.0013 |
| H=120 (4.00 LT) | 0.2 | 0.0096/0.0042/0.0035/0.0016 | 0.0019/0.014/0.043/0.0013 |

### C3. The deployable chain

False trust = P(T <= q_0.1) per (state, draw), target 0.1; T realized (the run's first passage against the noisy truth) or characteristic (moments). Trusted horizon = mean q_0.1 (LT). A4 + KM leaf uses the calibration A4 hybrid's characteristic horizon (no per-draw calibration errors on the full grid).

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| policy | false trust realized [CI] | false trust characteristic [CI] | mean trusted (LT) [CI] | q at cap |
|---|---|---|---|---|
| A2 + constant | 0.0641 [0.0586, 0.0697] | 0.09 [0.0813, 0.0993] | 0.965 [0.965, 0.965] | 0 |
| A2 + h(F-hat) | 0.104 [0.0975, 0.111] | 0.133 [0.124, 0.142] | 1.43 [1.41, 1.44] | 0 |
| A4 + KM leaf | 0.0756 [0.0702, 0.0814] | 0.106 [0.0971, 0.115] | 1.23 [1.22, 1.24] | 0 |
| g(F-hat) + h(F-hat) | 0.103 [0.0969, 0.11] | 0.127 [0.119, 0.137] | 1.45 [1.43, 1.46] | 0 |

Hybrid MSE ratio to A2 (realized per draw; 1.05 table, R2 guard).

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| policy | H=8 (0.27 LT) | H=15 (0.50 LT) | H=30 (1.00 LT) | H=60 (2.00 LT) | H=120 (4.00 LT) |
|---|---|---|---|---|---|
| A4 + KM leaf | 1.12 [1.08, 1.16] undetermined (n_eff < 50) | 1.07 [1.02, 1.11] undetermined (n_eff < 50) | 0.99 [0.962, 1.02] undetermined (n_eff < 50) | 1.01 [0.99, 1.02] negligible | 1.03 [1.02, 1.05] small |
| g(F-hat) + h(F-hat) | 1.01 [0.994, 1.03] undetermined (n_eff < 50) | 1.01 [0.974, 1.03] undetermined (n_eff < 50) | 0.978 [0.951, 1] undetermined (n_eff < 50) | 0.979 [0.965, 0.993] lowers | 0.976 [0.97, 0.982] lowers |

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| full system minus | false trust realized [CI] | false trust characteristic [CI] | trusted LT [CI] |
|---|---|---|---|
| A2 + constant | 0.0393 [0.0322, 0.0465] | 0.0374 [0.0265, 0.0486] | 0.481 [0.465, 0.497] |
| A2 + h(F-hat) | -0.000562 [-0.00381, 0.00275] | -0.00588 [-0.0104, -0.00175] | 0.0196 [0.0158, 0.0233] |
| A4 + KM leaf | 0.0278 [0.022, 0.0334] | 0.0213 [0.0125, 0.0299] | 0.221 [0.209, 0.233] |

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| horizon model (own characteristic target) | pinball / constant's | constant/model ratio [CI] reading | cov 0.1 / 0.5 / 0.9 | C |
|---|---|---|---|---|
| h_A2(F-hat) | 0.157 / 0.232 | 1.48 [1.44, 1.51] substantial | 0.133 / 0.498 / 0.871 | 0.733 |
| h_g(F-hat) | 0.156 / 0.228 | 1.47 [1.43, 1.51] substantial | 0.127 / 0.499 / 0.874 | - |

### E-H2a. Amplification mismatch m(H) (H_0 = 1 LT; both r.m.s. <= 0.5 sigma_x)

Medians by tercile of I (low / mid / high). Spearman(m, I) on the kept states [95%]. B and A columns from the A/D record (oracle).

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| horizon | kept | m | abs drift w* | corr C/sqrt(E_C E_P) | Spearman(m, I) | B RI / OI | A drop-I (MSE) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 3722 | -0.12 / 0.24 / 0.48 | 0.061 / 0.099 / 0.12 | 0.18 / 0.17 / 0.25 | 0.198 [0.166, 0.231] | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=15 (0.50 LT) | 3715 | 0.026 / -0.081 / 0.26 | 0.048 / 0.11 / 0.096 | 0.18 / 0.19 / 0.25 | 0.116 [0.0833, 0.15] | no interaction gain detected / interaction gain detected | undetermined (n_eff < 50) |
| H=30 (1.00 LT) | 3728 | 0 / 0 / 0 | 0 / 0 / 0 | 0.19 / 0.2 / 0.28 | (H_0) | interaction gain detected / interaction gain detected | undetermined (n_eff < 50) |
| H=60 (2.00 LT) | 2634 | -0.41 / -0.61 / -0.21 | 0.071 / 0.13 / 0.12 | 0.22 / 0.21 / 0.27 | 0.00541 [-0.0326, 0.0439] | no interaction gain detected / interaction gain detected | negligible |
| H=120 (4.00 LT) | 1147 | -1.5 / -1.6 / -0.94 | 0.27 / 0.28 / 0.24 | 0.3 / 0.28 / 0.36 | 0.0438 [-0.016, 0.104] | no interaction gain detected / no interaction gain detected | negligible |

**Reading: not determined** (horizons_used: ['60', '120'], horizons_supporting: [], horizons_null: ['60']).

### E-H2e. Library size and error correlation (sweep states)

1000 sweep states. Delta = value at N_lib 100000 minus 1000. corr = the H2e correlation (0 by convention where an error is constant over the draws).

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| rho | valid | corr 0 small / large lib | median corr small -> large | set | median Delta corr [CI] | Spearman(Delta corr, Delta R) [CI] | reading |
|---|---|---|---|---|---|---|---|
| 0.01 | 1000 | 505 / 18 | 0 -> 0.419 | all (1000) | 0.311 [0.288, 0.331] | 0.09 [0.027, 0.15] | not consistent |
| 0.01 | 1000 | 505 / 18 | 0 -> 0.419 | both_defined (487) | 0.176 [0.144, 0.228] | 0.0391 [-0.0548, 0.125] | not determined |
| 0.02 | 1000 | 247 / 4 | 0.113 -> 0.406 | all (1000) | 0.217 [0.198, 0.241] | -0.00864 [-0.0746, 0.0547] | not determined |
| 0.02 | 1000 | 247 / 4 | 0.113 -> 0.406 | both_defined (750) | 0.17 [0.144, 0.19] | 0.0494 [-0.0311, 0.12] | not determined |

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| rho | stratifier | median Delta corr low / mid / high | median Delta R low / mid / high |
|---|---|---|---|
| 0.01 | R | 0.29 / 0.3 / 0.35 | -1.1 / -0.98 / -1.5 |
| 0.01 | O | 0.33 / 0.31 / 0.28 | -1.7 / -1.1 / -0.82 |
| 0.01 | I | 0.25 / 0.29 / 0.38 | -1.3 / -1.1 / -1.1 |
| 0.01 | N | 0.3 / 0.31 / 0.32 | -1.5 / -0.85 / -1.2 |
| 0.01 | delta_R | 0.3 / 0.28 / 0.35 | -2 / -1.1 / -0.31 |
| 0.02 | R | 0.21 / 0.19 / 0.28 | -0.69 / -0.54 / -0.92 |
| 0.02 | O | 0.3 / 0.2 / 0.19 | -1.1 / -0.6 / -0.44 |
| 0.02 | I | 0.19 / 0.2 / 0.28 | -0.73 / -0.66 / -0.61 |
| 0.02 | N | 0.24 / 0.19 / 0.23 | -0.92 / -0.4 / -0.69 |
| 0.02 | delta_R | 0.26 / 0.18 / 0.23 | -1.4 / -0.68 / 0.028 |

**Reading** (final, after the convention check): rho 0.01: not determined (depends on the zero-variance convention); rho 0.02: not determined.

### E-H3c. A5 against A4

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| item | value |
|---|---|
| H3c ratio MSE(A5)/MSE(A4) [CI at level 0.983] (run) | 1 [0.97, 1.03], width 0.0625 |
| top-1% share: A5 loss / A4 loss / abs(A5 - A4) | 0.673 / 0.663 / 0.446 |
| autocorrelation of d = A5 - A4, lags 1..5 | -0.018, 0.00066, 0.0071, 0.0025, 0.012 |
| block-5 means: lag-1 autocorrelation, variance ratio | 0.061, 0.964 |
| K chosen; leaves used test / calibration; largest leaf share test | 2; 2 / 2; 0.773 |
| w*(H_ref) within-leaf share of variance | 0.976 |
| bimodality coefficient R/O/I/N, oracle; deployable | 0.22/0.2/0.43/0.84; 0.36/0.46/0.44/0.89 |
| Spearman pairs (oracle) | RO 0.054, RI 0.04, RN 0.39, OI 0.33, ON 0.094, IN 0.0073 |
| top-1% abs(d) states: mean percentile R/O/I/N | 0.57/0.59/0.86/0.48 |
| top-1% abs(d) states: median I pct; share high-I; median abs(x) pct; share sign change in window; share of sum d | 0.938; 0.875; 0.502; 0.275; -9.94 |

## E-H3c reading (this seed)

PHASE J CONFIRMATORY (CONF-6): pre-registered analysis, UNPROMOTED.

| item | value |
|---|---|
| H3c interval widths | lorenz63 0.177, rossler 0.0487, chua 0.0625 |
| pattern (Lorenz-63 widest, Rössler narrowest) reproduced | True |
| Lorenz-63 part (top-1% share of sum abs(d) 0.66, median I percentile 0.277) | not consistent |
| Rössler part (BC deployable: R 0.503, O 0.798, I 0.458, N 0.905) | not consistent |
| **reading** | **not consistent** |

