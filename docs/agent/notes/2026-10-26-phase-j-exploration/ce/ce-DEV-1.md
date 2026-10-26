# Phase J experiments C and E: DEV-1

**DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.** Run `/home/brianm/projects/physics/chaos/lpcstudy-wt/run/phj-f701a47/runs/dev/phj-DEV-1/full`; analysis commit `33cb71e06322baa281454f26e4b74f804a725026` (dirty: False); A/D record `/home/brianm/projects/physics/chaos/lpcstudy-wt/run/phj-f701a47/runs/dev/phj-DEV-1/contrib-33cb71e/contrib.json`. Estimates with 95% intervals from the shared moving-block index sets (models fixed; training variance not included). Readings are descriptive; no causal claim; nothing here is set beside CONF-1.

## lorenz63

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| check | result |
|---|---|
| A2 rebuilt on 1..H_max equals the dumped A2 (bitwise); A4 horizon-free | True, True |
| refit reproduces WU-0048 (max abs: A/ROIN MSE oracle, deployable; W/ROIN L_w oracle, deployable) | 0 / 0 / 0 / 0 |
| T_c counts T = 1 / e_(T-1) = theta (A2 train, g train, A2 test, g test, A4 calibration) | 14/0, 110/0, 7/0, 30/0, 104/0 |
| A2 on 1..H_max: pooled curvature floor / columns at 0 or 1 | 0 / 0 |
| weights clipped to [0, 1] | g_oracle_test 554, g_oracle_train_oof 2058, gw_oracle_test 598, gw_oracle_train_oof 1930, g_deployable_test 769, g_deployable_train_oof 3235, gw_deployable_test 355, gw_deployable_train_oof 682 |

### C1. Separate performance (from the A/D record, no refit)

Allocation: MSE per rule (oracle: moment form; deployable: realized); reading of the rung against F (MSE ratio, 1.05 table, n_eff guard). G(F) = 1 - L_A(F)/L_A(constant).

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| horizon | profile | constant | separation | RO | F (ROIN) | X | X+F | G(F) | sep vs F | RO vs F | X+F vs F |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 0.00898 | 0.000829 | 0.000795 | 0.000742 | 0.000916 | 0.000696 | 0.988 | undetermined | undetermined | undetermined |
| H=8 (0.27 LT) | deployable | 0.00939 | 0.0316 | 0.00879 | 0.00547 | 0.00106 | 0.00137 | 0.448 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | oracle | 0.0337 | 0.0109 | 0.0106 | 0.0111 | 0.0122 | 0.0104 | 0.896 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | deployable | 0.0287 | 0.0393 | 0.0297 | 0.0244 | 0.00945 | 0.0113 | 0.209 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | oracle | 0.0536 | 0.0249 | 0.0265 | 0.0247 | 0.0363 | 0.0244 | 0.75 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | deployable | 0.0578 | 0.0665 | 0.0481 | 0.0399 | 0.0405 | 0.0367 | 0.419 | undetermined | undetermined | undetermined |
| H=60 (2.00 LT) | oracle | 0.151 | 0.131 | 0.137 | 0.132 | 0.133 | 0.131 | 0.305 | undetermined | undetermined | negligible |
| H=60 (2.00 LT) | deployable | 0.166 | 0.168 | 0.163 | 0.153 | 0.143 | 0.142 | 0.168 | needed, size not determined | needed, size not determined | lowers |
| H=120 (4.00 LT) | oracle | 0.906 | 1 | 0.912 | 0.908 | 0.884 | 0.893 | -0.00857 | substantial | negligible | lowers |
| H=120 (4.00 LT) | deployable | 0.893 | 0.946 | 0.891 | 0.886 | 0.873 | 0.872 | 0.0263 | needed, size not determined | negligible | negligible |

Horizon (Y = ln min(T_c, H_max)): pinball at 0.5 / Harrell's C / coverage of q_0.1 below the cap; reading against F.

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| profile | rung | pinball | C | cov q_0.1 | reading vs F |
|---|---|---|---|---|---|
| oracle | none | 0.185 | 0.5 | 0.099 | substantial |
| oracle | lyapunov | 0.313 | 0.59 | 0.0861 | substantial |
| oracle | RO | 0.179 | 0.576 | 0.115 | substantial |
| oracle | ROIN | 0.146 | 0.678 | 0.144 |  |
| oracle | X | 0.151 | 0.683 | 0.136 | undetermined |
| oracle | X+F | 0.126 | 0.72 | 0.146 | lowers |
| oracle | Lyapunov rank | | 0.587 | | |
| deployable | none | 0.185 | 0.5 | 0.099 | substantial |
| deployable | lyapunov | 0.31 | 0.592 | 0.0741 | substantial |
| deployable | RO | 0.179 | 0.568 | 0.119 | substantial |
| deployable | ROIN | 0.147 | 0.673 | 0.129 |  |
| deployable | X | 0.149 | 0.679 | 0.134 | undetermined |
| deployable | X+F | 0.127 | 0.716 | 0.144 | lowers |
| deployable | Lyapunov rank | | 0.59 | | |

### C2. Shared information (oracle and deployable profiles)

Skill retained = [L(constant) - L(bottleneck)] / [L(constant) - L(F)]; reading: keeps most (CI > 0.5), loses most (CI < 0.5), else not determined. Forward: horizon from g (five clipped weights; g_w: the L_w fits); reverse: weight from h (three quantiles), scored by L_A (MSE; deployable: realized per draw, R2 guard) and by L_w (weight units, unit-weight fits). Training inputs cross-fitted.

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| profile | direction | horizon | full skill [CI] | retained L_A / pinball [CI] | reading | retained L_w [CI] | reading L_w |
|---|---|---|---|---|---|---|---|
| oracle | forward (g; g_w) | all five | 0.0384 [0.0297, 0.0475] | 0.129 [0.0587, 0.192] | loses most | 0.275 [0.162, 0.381] | loses most |
| oracle | forward, one weight | H=8 (0.27 LT) | | 0.0127 [-0.039, 0.0617] | loses most | | |
| oracle | forward, one weight | H=15 (0.50 LT) | | 0.0355 [-0.0013, 0.0697] | loses most | | |
| oracle | forward, one weight | H=30 (1.00 LT) | | 0.0159 [-0.0245, 0.0526] | loses most | | |
| oracle | forward, one weight | H=60 (2.00 LT) | | 0.0451 [0.000173, 0.091] | loses most | | |
| oracle | forward, one weight | H=120 (4.00 LT) | | 0.0759 [0.012, 0.138] | loses most | | |
| oracle | reverse | H=8 (0.27 LT) | 0.00824 [0.0057, 0.0114] | 0.598 [0.364, 0.746] | not determined (n_eff < 50) | 0.135 [0.0912, 0.176] | loses most |
| oracle | reverse | H=15 (0.50 LT) | 0.0226 [0.0133, 0.0329] | 0.47 [0.318, 0.59] | not determined (n_eff < 50) | 0.119 [0.08, 0.162] | loses most |
| oracle | reverse | H=30 (1.00 LT) | 0.0289 [0.0186, 0.041] | 0.606 [0.386, 0.77] | not determined (n_eff < 50) | 0.172 [0.126, 0.216] | loses most |
| oracle | reverse | H=60 (2.00 LT) | 0.0192 [0.00959, 0.0297] | 0.444 [0.238, 0.775] | not determined (interval spans 0.5) | 0.146 [0.0902, 0.208] | loses most |
| oracle | reverse | H=120 (4.00 LT) | -0.00236 [-0.015, 0.01] | - [-, -] | not determined (full-profile skill not established) | 0.298 [0.0624, 0.928] | not determined (interval spans 0.5) |
| deployable | forward (g; g_w) | all five | 0.0378 [0.029, 0.0469] | 0.126 [0.068, 0.186] | loses most | 0.0974 [-0.0847, 0.244] | loses most |
| deployable | forward, one weight | H=8 (0.27 LT) | | 0.0979 [0.0566, 0.145] | loses most | | |
| deployable | forward, one weight | H=15 (0.50 LT) | | 0.0969 [0.05, 0.148] | loses most | | |
| deployable | forward, one weight | H=30 (1.00 LT) | | 0.0746 [0.0274, 0.121] | loses most | | |
| deployable | forward, one weight | H=60 (2.00 LT) | | 0.0482 [0.0226, 0.0767] | loses most | | |
| deployable | forward, one weight | H=120 (4.00 LT) | | 0.0634 [0.00811, 0.119] | loses most | | |
| deployable | reverse | H=8 (0.27 LT) | 0.00392 [0.00035, 0.00776] | 0.124 [-1.2, 1.84] | not determined (n_eff < 50) | 0.241 [0.142, 0.371] | loses most |
| deployable | reverse | H=15 (0.50 LT) | 0.00423 [-0.00475, 0.0147] | 1.53 [-, -] | not determined (full-profile skill not established) | 0.22 [0.132, 0.326] | loses most |
| deployable | reverse | H=30 (1.00 LT) | 0.0179 [0.0061, 0.0319] | 0.785 [0.423, 1.21] | not determined (n_eff < 50) | 0.308 [0.16, 0.475] | loses most |
| deployable | reverse | H=60 (2.00 LT) | 0.013 [0.00553, 0.0223] | 0.477 [0.223, 0.822] | not determined (interval spans 0.5) | 0.289 [0.162, 0.441] | loses most |
| deployable | reverse | H=120 (4.00 LT) | 0.0069 [-0.00332, 0.0172] | 0.0631 [-, -] | not determined (full-profile skill not established) | 0.541 [0.0745, 1.9] | not determined (interval spans 0.5) |

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| profile | forward C-index F / g / g_w | reverse MSE(h)/MSE(F) per horizon | math-spec prediction (both lose most) | largest single-weight retention at H |
|---|---|---|---|---|
| oracle | 0.678 / 0.569 / 0.608 | H=8 (0.27 LT) 5.47 [3.45, 8.68] undetermined (n_eff < 50); H=15 (0.50 LT) 2.08 [1.56, 3.17] undetermined (n_eff < 50); H=30 (1.00 LT) 1.46 [1.24, 1.8] undetermined (n_eff < 50); H=60 (2.00 LT) 1.08 [1.02, 1.16] needed, size not determined; H=120 (4.00 LT) 0.991 [0.978, 1.01] negligible | **consistent** | 120 |
| deployable | 0.673 / 0.573 / 0.595 | H=8 (0.27 LT) 1.63 [0.939, 2.88] undetermined (n_eff < 50); H=15 (0.50 LT) 0.908 [0.672, 1.32] undetermined (n_eff < 50); H=30 (1.00 LT) 1.1 [0.954, 1.34] undetermined (n_eff < 50); H=60 (2.00 LT) 1.04 [1.01, 1.09] needed, size not determined; H=120 (4.00 LT) 1.01 [0.997, 1.02] negligible | **consistent** | 8 |

Oracle against deployable: retained (deployable) minus retained (oracle), paired 95% interval.

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| row | oracle | deployable | difference [CI] | reading |
|---|---|---|---|---|
| forward | 0.129 | 0.126 | -0.00232 [-0.0692, 0.0683] | no difference detected |
| forward_w | 0.275 | 0.0974 | -0.177 [-0.364, -0.0192] | deployable retains less |
| reverse/8 | 0.598 | 0.124 | -0.473 [-1.81, 1.33] | not determined (n_eff < 50) |
| reverse_w/8 | 0.135 | 0.241 | 0.105 [0.0129, 0.239] | deployable retains more |
| reverse/15 | 0.47 | 1.53 | 1.06 [-, -] | not determined (n_eff < 50) |
| reverse_w/15 | 0.119 | 0.22 | 0.101 [0.019, 0.203] | deployable retains more |
| reverse/30 | 0.606 | 0.785 | 0.179 [-0.176, 0.712] | not determined (n_eff < 50) |
| reverse_w/30 | 0.172 | 0.308 | 0.137 [-0.00228, 0.295] | no difference detected |
| reverse/60 | 0.444 | 0.477 | 0.0327 [-0.363, 0.432] | no difference detected |
| reverse_w/60 | 0.146 | 0.289 | 0.143 [0.0246, 0.288] | deployable retains more |
| reverse/120 | - | 0.0631 | - [-, -] | not determined (full-profile skill not established) |
| reverse_w/120 | 0.298 | 0.541 | 0.243 [-0.446, 1.34] | no difference detected |

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| horizon | Spearman(phi allocation, phi horizon) (4 items, descriptive) | phi_alloc R/O/I/N | phi_horizon R/O/I/N |
|---|---|---|---|
| H=8 (0.27 LT) | 0.6 | -0.00038/0.0052/0.0026/0.00078 | 0.0028/0.0085/0.027/0.00037 |
| H=15 (0.50 LT) | 0.8 | 0.0028/0.013/0.0043/0.0025 | 0.0028/0.0085/0.027/0.00037 |
| H=30 (1.00 LT) | 0.6 | 0.002/0.013/0.0092/0.0044 | 0.0028/0.0085/0.027/0.00037 |
| H=60 (2.00 LT) | 0.8 | 0.0015/0.013/0.004/0.00054 | 0.0028/0.0085/0.027/0.00037 |
| H=120 (4.00 LT) | 0.4 | -0.0016/-0.0038/0.0051/-0.0021 | 0.0028/0.0085/0.027/0.00037 |

### C3. The deployable chain

False trust = P(T <= q_0.1) per (state, draw), target 0.1; T realized (the run's first passage against the noisy truth) or characteristic (moments). Trusted horizon = mean q_0.1 (LT). A4 + KM leaf uses the calibration A4 hybrid's characteristic horizon (no per-draw calibration errors on the full grid).

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| policy | false trust realized [CI] | false trust characteristic [CI] | mean trusted (LT) [CI] | q at cap |
|---|---|---|---|---|
| A2 + constant | 0.0805 [0.068, 0.0932] | 0.107 [0.091, 0.123] | 0.621 [0.621, 0.621] | 0 |
| A2 + h(F-hat) | 0.108 [0.0952, 0.122] | 0.123 [0.107, 0.14] | 1.06 [1.03, 1.08] | 0 |
| A4 + KM leaf | 0.096 [0.084, 0.109] | 0.135 [0.116, 0.156] | 1.13 [1.12, 1.15] | 0 |
| g(F-hat) + h(F-hat) | 0.0963 [0.0835, 0.109] | 0.121 [0.103, 0.138] | 1.15 [1.13, 1.17] | 0 |

Hybrid MSE ratio to A2 (realized per draw; 1.05 table, R2 guard).

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| policy | H=8 (0.27 LT) | H=15 (0.50 LT) | H=30 (1.00 LT) | H=60 (2.00 LT) | H=120 (4.00 LT) |
|---|---|---|---|---|---|
| A4 + KM leaf | 3.38 [2.18, 4.18] undetermined (n_eff < 50) | 1.37 [1.12, 1.56] undetermined (n_eff < 50) | 1.15 [1.04, 1.25] undetermined (n_eff < 50) | 1.01 [0.981, 1.04] negligible | 1.06 [1.04, 1.08] needed, size not determined |
| g(F-hat) + h(F-hat) | 0.584 [0.322, 0.958] undetermined (n_eff < 50) | 0.855 [0.539, 1.17] undetermined (n_eff < 50) | 0.688 [0.487, 0.884] undetermined (n_eff < 50) | 0.919 [0.864, 0.965] lowers | 0.992 [0.98, 1] negligible |

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| full system minus | false trust realized [CI] | false trust characteristic [CI] | trusted LT [CI] |
|---|---|---|---|
| A2 + constant | 0.0158 [0.00225, 0.0293] | 0.0138 [-0.00501, 0.0312] | 0.53 [0.505, 0.553] |
| A2 + h(F-hat) | -0.0123 [-0.023, -0.00199] | -0.002 [-0.0175, 0.0135] | 0.0957 [0.0771, 0.111] |
| A4 + KM leaf | 0.00025 [-0.014, 0.0125] | -0.014 [-0.035, 0.0045] | 0.0172 [-0.00951, 0.0391] |

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| horizon model (own characteristic target) | pinball / constant's | constant/model ratio [CI] reading | cov 0.1 / 0.5 / 0.9 | C |
|---|---|---|---|---|
| h_A2(F-hat) | 0.207 / 0.256 | 1.24 [1.16, 1.32] substantial | 0.123 / 0.51 / 0.887 | 0.672 |
| h_g(F-hat) | 0.189 / 0.219 | 1.16 [1.09, 1.23] substantial | 0.121 / 0.498 / 0.888 | - |

### E-H2a. Amplification mismatch m(H) (H_0 = 1 LT; both r.m.s. <= 0.5 sigma_x)

Medians by tercile of I (low / mid / high). Spearman(m, I) on the kept states [95%]. B and A columns from the A/D record (oracle).

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| horizon | kept | m | abs drift w* | corr C/sqrt(E_C E_P) | Spearman(m, I) | B RI / OI | A drop-I (MSE) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 884 | -0.064 / -0.0041 / 0.047 | 0.049 / 0.038 / 0.09 | 0.12 / 0.16 / 0.13 | 0.0543 [-0.0141, 0.123] | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=15 (0.50 LT) | 878 | 0.043 / 0.026 / -0.00017 | 0.035 / 0.048 / 0.064 | 0.11 / 0.15 / 0.16 | -0.029 [-0.0944, 0.0458] | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=30 (1.00 LT) | 892 | 0 / 0 / 0 | 0 / 0 / 0 | 0.14 / 0.16 / 0.2 | (H_0) | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=60 (2.00 LT) | 689 | -0.091 / 0.032 / -0.044 | 0.048 / 0.082 / 0.06 | 0.12 / 0.21 / 0.18 | -0.0236 [-0.0978, 0.0538] | no interaction gain detected / no interaction gain detected | needed, size not determined |
| H=120 (4.00 LT) | 155 | -1.8 / -2.7 / -2.7 | 0.29 / 0.5 / 0.47 | 0.22 / 0.34 / 0.34 | -0.115 [-0.288, 0.0526] | no interaction gain detected / interaction gain detected | small |

**Reading: not determined** (horizons_used: ['60', '120'], horizons_supporting: [], horizons_null: ['60']).

### E-H2e. Library size and error correlation (sweep states)

1000 sweep states. Delta = value at N_lib 100000 minus 1000. corr = the H2e correlation (0 by convention where an error is constant over the draws).

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| rho | valid | corr 0 small / large lib | median corr small -> large | set | median Delta corr [CI] | Spearman(Delta corr, Delta R) [CI] | reading |
|---|---|---|---|---|---|---|---|
| 0.01 | 1000 | 674 / 15 | 0 -> 0.441 | all (1000) | 0.382 [0.354, 0.402] | 0.0733 [0.00877, 0.136] | not consistent |
| 0.01 | 1000 | 674 / 15 | 0 -> 0.441 | both_defined (323) | 0.249 [0.208, 0.282] | -0.0926 [-0.193, 0.014] | not determined |
| 0.02 | 1000 | 432 / 3 | 0 -> 0.466 | all (1000) | 0.339 [0.318, 0.367] | -0.0259 [-0.0842, 0.0317] | not determined |
| 0.02 | 1000 | 432 / 3 | 0 -> 0.466 | both_defined (568) | 0.242 [0.206, 0.279] | -0.107 [-0.18, -0.0271] | consistent |

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| rho | stratifier | median Delta corr low / mid / high | median Delta R low / mid / high |
|---|---|---|---|
| 0.01 | R | 0.39 / 0.39 / 0.36 | -1.6 / -1.8 / -1.8 |
| 0.01 | O | 0.4 / 0.39 / 0.34 | -1.8 / -1.7 / -1.8 |
| 0.01 | I | 0.35 / 0.43 / 0.36 | -1.8 / -1.7 / -1.6 |
| 0.01 | N | 0.34 / 0.41 / 0.39 | -1.8 / -1.6 / -1.8 |
| 0.01 | delta_R | 0.35 / 0.36 / 0.42 | -2.7 / -1.8 / -0.69 |
| 0.02 | R | 0.34 / 0.34 / 0.33 | -1.2 / -1.3 / -1.2 |
| 0.02 | O | 0.34 / 0.37 / 0.31 | -1.2 / -1.1 / -1.3 |
| 0.02 | I | 0.33 / 0.36 / 0.33 | -1.3 / -1.2 / -1.2 |
| 0.02 | N | 0.27 / 0.37 / 0.37 | -1.3 / -1.1 / -1.3 |
| 0.02 | delta_R | 0.38 / 0.32 / 0.34 | -2.1 / -1.2 / -0.28 |

**Reading** (final, after the convention check): rho 0.01: not determined (depends on the zero-variance convention); rho 0.02: not determined (depends on the zero-variance convention).

### E-H3c. A5 against A4

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| item | value |
|---|---|
| H3c ratio MSE(A5)/MSE(A4) [CI at level 0.983] (run) | 0.711 [0.527, 0.896], width 0.369 |
| top-1% share: A5 loss / A4 loss / abs(A5 - A4) | 0.576 / 0.568 / 0.683 |
| autocorrelation of d = A5 - A4, lags 1..5 | -0.0058, -0.0074, -0.0061, 0.002, -0.016 |
| block-5 means: lag-1 autocorrelation, variance ratio | -0.032, 0.973 |
| K chosen; leaves used test / calibration; largest leaf share test | 6; 6 / 6; 0.316 |
| w*(H_ref) within-leaf share of variance | 0.916 |
| bimodality coefficient R/O/I/N, oracle; deployable | 0.29/0.78/0.53/0.83; 0.33/0.43/0.54/0.9 |
| Spearman pairs (oracle) | RO 0.53, RI -0.026, RN 0.29, OI 0.037, ON -0.074, IN 0.045 |
| top-1% abs(d) states: mean percentile R/O/I/N | 0.6/0.98/0.31/0.18 |
| top-1% abs(d) states: median I pct; share high-I; median abs(x) pct; share sign change in window; share of sum d | 0.266; 0.1; 0.328; 0.9; 0.885 |

## rossler

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| check | result |
|---|---|
| A2 rebuilt on 1..H_max equals the dumped A2 (bitwise); A4 horizon-free | True, True |
| refit reproduces WU-0048 (max abs: A/ROIN MSE oracle, deployable; W/ROIN L_w oracle, deployable) | 0 / 0 / 0 / 0 |
| T_c counts T = 1 / e_(T-1) = theta (A2 train, g train, A2 test, g test, A4 calibration) | 0/0, 0/0, 0/0, 0/0, 0/0 |
| A2 on 1..H_max: pooled curvature floor / columns at 0 or 1 | 0 / 0 |
| weights clipped to [0, 1] | g_oracle_test 869, g_oracle_train_oof 2674, gw_oracle_test 443, gw_oracle_train_oof 1554, g_deployable_test 2529, g_deployable_train_oof 8051, gw_deployable_test 541, gw_deployable_train_oof 1567 |

### C1. Separate performance (from the A/D record, no refit)

Allocation: MSE per rule (oracle: moment form; deployable: realized); reading of the rung against F (MSE ratio, 1.05 table, n_eff guard). G(F) = 1 - L_A(F)/L_A(constant).

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| horizon | profile | constant | separation | RO | F (ROIN) | X | X+F | G(F) | sep vs F | RO vs F | X+F vs F |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 0.000124 | 0.000119 | 0.000113 | 0.000112 | 0.000122 | 0.000112 | 0.51 | needed, size not determined | small | negligible |
| H=8 (0.27 LT) | deployable | 0.000119 | 0.000127 | 0.000119 | 0.00012 | 0.000117 | 0.000118 | -0.0421 | needed, size not determined | negligible | lowers |
| H=15 (0.50 LT) | oracle | 0.000231 | 0.000212 | 0.000203 | 0.000202 | 0.000228 | 0.000202 | 0.598 | needed, size not determined | negligible | negligible |
| H=15 (0.50 LT) | deployable | 0.000222 | 0.000231 | 0.000217 | 0.000219 | 0.00022 | 0.000217 | 0.0832 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | oracle | 0.000814 | 0.000735 | 0.000711 | 0.000708 | 0.000811 | 0.00071 | 0.66 | needed, size not determined | negligible | negligible |
| H=30 (1.00 LT) | deployable | 0.000815 | 0.000833 | 0.0008 | 0.000796 | 0.000811 | 0.00079 | 0.113 | needed, size not determined | negligible | negligible |
| H=60 (2.00 LT) | oracle | 0.0139 | 0.0125 | 0.0125 | 0.0126 | 0.0139 | 0.0124 | 0.348 | negligible | negligible | negligible |
| H=60 (2.00 LT) | deployable | 0.0144 | 0.0142 | 0.0143 | 0.0142 | 0.0143 | 0.0142 | 0.0363 | negligible | negligible | negligible |
| H=120 (4.00 LT) | oracle | 0.105 | 0.106 | 0.103 | 0.103 | 0.105 | 0.101 | 0.0807 | undetermined | negligible | negligible |
| H=120 (4.00 LT) | deployable | 0.104 | 0.108 | 0.103 | 0.103 | 0.103 | 0.101 | 0.032 | needed, size not determined | negligible | negligible |

Horizon (Y = ln min(T_c, H_max)): pinball at 0.5 / Harrell's C / coverage of q_0.1 below the cap; reading against F.

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| profile | rung | pinball | C | cov q_0.1 | reading vs F |
|---|---|---|---|---|---|
| oracle | none | 0.155 | 0.5 | 0.099 | substantial |
| oracle | lyapunov | 0.171 | 0.621 | 0.0572 | substantial |
| oracle | RO | 0.144 | 0.595 | 0.101 | substantial |
| oracle | ROIN | 0.117 | 0.692 | 0.132 |  |
| oracle | X | 0.118 | 0.701 | 0.141 | undetermined |
| oracle | X+F | 0.0868 | 0.777 | 0.129 | lowers |
| oracle | Lyapunov rank | | 0.62 | | |
| deployable | none | 0.155 | 0.5 | 0.099 | substantial |
| deployable | lyapunov | 0.172 | 0.615 | 0.0588 | substantial |
| deployable | RO | 0.14 | 0.603 | 0.114 | substantial |
| deployable | ROIN | 0.116 | 0.691 | 0.126 |  |
| deployable | X | 0.118 | 0.697 | 0.133 | undetermined |
| deployable | X+F | 0.087 | 0.777 | 0.133 | lowers |
| deployable | Lyapunov rank | | 0.615 | | |

### C2. Shared information (oracle and deployable profiles)

Skill retained = [L(constant) - L(bottleneck)] / [L(constant) - L(F)]; reading: keeps most (CI > 0.5), loses most (CI < 0.5), else not determined. Forward: horizon from g (five clipped weights; g_w: the L_w fits); reverse: weight from h (three quantiles), scored by L_A (MSE; deployable: realized per draw, R2 guard) and by L_w (weight units, unit-weight fits). Training inputs cross-fitted.

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| profile | direction | horizon | full skill [CI] | retained L_A / pinball [CI] | reading | retained L_w [CI] | reading L_w |
|---|---|---|---|---|---|---|---|
| oracle | forward (g; g_w) | all five | 0.0383 [0.031, 0.0447] | 0.475 [0.379, 0.581] | not determined (interval spans 0.5) | 0.45 [0.337, 0.562] | not determined (interval spans 0.5) |
| oracle | forward, one weight | H=8 (0.27 LT) | | 0.103 [0.037, 0.174] | loses most | | |
| oracle | forward, one weight | H=15 (0.50 LT) | | 0.106 [0.0399, 0.179] | loses most | | |
| oracle | forward, one weight | H=30 (1.00 LT) | | 0.0869 [0.0142, 0.167] | loses most | | |
| oracle | forward, one weight | H=60 (2.00 LT) | | 0.167 [0.0863, 0.264] | loses most | | |
| oracle | forward, one weight | H=120 (4.00 LT) | | 0.378 [0.284, 0.488] | loses most | | |
| oracle | reverse | H=8 (0.27 LT) | 1.21e-05 [8.81e-06, 1.7e-05] | 0.311 [0.15, 0.439] | loses most | 0.268 [0.177, 0.356] | loses most |
| oracle | reverse | H=15 (0.50 LT) | 2.91e-05 [2e-05, 4.27e-05] | 0.346 [0.184, 0.466] | loses most | 0.37 [0.266, 0.465] | loses most |
| oracle | reverse | H=30 (1.00 LT) | 0.000107 [8.17e-05, 0.000136] | 0.124 [0.0611, 0.187] | loses most | 0.353 [0.243, 0.452] | loses most |
| oracle | reverse | H=60 (2.00 LT) | 0.0013 [0.000763, 0.00189] | 0.206 [0.0227, 0.41] | loses most | 0.446 [0.336, 0.565] | not determined (interval spans 0.5) |
| oracle | reverse | H=120 (4.00 LT) | 0.0024 [0.000989, 0.00378] | 0.704 [0.297, 1.54] | not determined (interval spans 0.5) | 0.385 [0.148, 0.697] | not determined (interval spans 0.5) |
| deployable | forward (g; g_w) | all five | 0.0393 [0.0329, 0.0454] | 0.442 [0.355, 0.52] | not determined (interval spans 0.5) | 0.477 [0.386, 0.568] | not determined (interval spans 0.5) |
| deployable | forward, one weight | H=8 (0.27 LT) | | 0.0904 [0.0378, 0.149] | loses most | | |
| deployable | forward, one weight | H=15 (0.50 LT) | | 0.0934 [0.0457, 0.146] | loses most | | |
| deployable | forward, one weight | H=30 (1.00 LT) | | 0.132 [0.0736, 0.197] | loses most | | |
| deployable | forward, one weight | H=60 (2.00 LT) | | 0.182 [0.118, 0.254] | loses most | | |
| deployable | forward, one weight | H=120 (4.00 LT) | | 0.35 [0.264, 0.435] | loses most | | |
| deployable | reverse | H=8 (0.27 LT) | -7.65e-07 [-2.65e-06, 1.16e-06] | - [-, -] | not determined (full-profile skill not established) | 0.073 [0.011, 0.14] | loses most |
| deployable | reverse | H=15 (0.50 LT) | 3.3e-06 [-1.3e-06, 8.48e-06] | 0.573 [-, -] | not determined (full-profile skill not established) | 0.0623 [-0.0347, 0.155] | loses most |
| deployable | reverse | H=30 (1.00 LT) | 1.82e-05 [8.69e-08, 4e-05] | 0.0816 [-14.7, 9.4] | not determined (interval spans 0.5) | 0.145 [0.0724, 0.22] | loses most |
| deployable | reverse | H=60 (2.00 LT) | 0.000153 [-0.000122, 0.00044] | -0.165 [-, -] | not determined (full-profile skill not established) | 0.224 [0.0901, 0.372] | loses most |
| deployable | reverse | H=120 (4.00 LT) | 0.000911 [-0.000254, 0.00216] | 2.04 [-, -] | not determined (full-profile skill not established) | 0.661 [0.101, 1.32] | not determined (interval spans 0.5) |

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| profile | forward C-index F / g / g_w | reverse MSE(h)/MSE(F) per horizon | math-spec prediction (both lose most) | largest single-weight retention at H |
|---|---|---|---|---|
| oracle | 0.692 / 0.617 / 0.612 | H=8 (0.27 LT) 1.07 [1.06, 1.09] substantial; H=15 (0.50 LT) 1.09 [1.07, 1.12] substantial; H=30 (1.00 LT) 1.13 [1.1, 1.17] substantial; H=60 (2.00 LT) 1.08 [1.04, 1.13] needed, size not determined; H=120 (4.00 LT) 1.01 [0.994, 1.02] negligible | **not determined** | 120 |
| deployable | 0.691 / 0.615 / 0.624 | H=8 (0.27 LT) 0.994 [0.98, 1.01] negligible; H=15 (0.50 LT) 1.01 [0.988, 1.03] undetermined (n_eff < 50); H=30 (1.00 LT) 1.02 [1, 1.04] small; H=60 (2.00 LT) 1.01 [0.996, 1.03] negligible; H=120 (4.00 LT) 0.991 [0.983, 1] lowers | **not determined** | 120 |

Oracle against deployable: retained (deployable) minus retained (oracle), paired 95% interval.

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| row | oracle | deployable | difference [CI] | reading |
|---|---|---|---|---|
| forward | 0.475 | 0.442 | -0.0334 [-0.14, 0.0644] | no difference detected |
| forward_w | 0.45 | 0.477 | 0.0267 [-0.0937, 0.142] | no difference detected |
| reverse/8 | 0.311 | - | - [-, -] | not determined (full-profile skill not established) |
| reverse_w/8 | 0.268 | 0.073 | -0.195 [-0.295, -0.0863] | deployable retains less |
| reverse/15 | 0.346 | 0.573 | 0.227 [-, -] | not determined (full-profile skill not established) |
| reverse_w/15 | 0.37 | 0.0623 | -0.308 [-0.438, -0.18] | deployable retains less |
| reverse/30 | 0.124 | 0.0816 | -0.0426 [-14.8, 9.24] | no difference detected |
| reverse_w/30 | 0.353 | 0.145 | -0.208 [-0.314, -0.0896] | deployable retains less |
| reverse/60 | 0.206 | -0.165 | -0.371 [-, -] | not determined (full-profile skill not established) |
| reverse_w/60 | 0.446 | 0.224 | -0.222 [-0.399, -0.0364] | deployable retains less |
| reverse/120 | 0.704 | 2.04 | 1.34 [-, -] | not determined (full-profile skill not established) |
| reverse_w/120 | 0.385 | 0.661 | 0.276 [-0.28, 0.844] | no difference detected |

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| horizon | Spearman(phi allocation, phi horizon) (4 items, descriptive) | phi_alloc R/O/I/N | phi_horizon R/O/I/N |
|---|---|---|---|
| H=8 (0.27 LT) | -1 | 7.3e-06/1.5e-06/2e-08/3.2e-06 | 0.0036/0.0093/0.022/0.0036 |
| H=15 (0.50 LT) | -1 | 2e-05/3.5e-06/-1.5e-07/5.8e-06 | 0.0036/0.0093/0.022/0.0036 |
| H=30 (1.00 LT) | -1 | 6.8e-05/1.8e-05/9.2e-08/2.1e-05 | 0.0036/0.0093/0.022/0.0036 |
| H=60 (2.00 LT) | -0.8 | 0.0011/9.1e-05/2.5e-05/8.3e-05 | 0.0036/0.0093/0.022/0.0036 |
| H=120 (4.00 LT) | -0.4 | 0.002/-0.00012/0.00033/0.00019 | 0.0036/0.0093/0.022/0.0036 |

### C3. The deployable chain

False trust = P(T <= q_0.1) per (state, draw), target 0.1; T realized (the run's first passage against the noisy truth) or characteristic (moments). Trusted horizon = mean q_0.1 (LT). A4 + KM leaf uses the calibration A4 hybrid's characteristic horizon (no per-draw calibration errors on the full grid).

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| policy | false trust realized [CI] | false trust characteristic [CI] | mean trusted (LT) [CI] | q at cap |
|---|---|---|---|---|
| A2 + constant | 0.0897 [0.0783, 0.101] | 0.1 [0.082, 0.119] | 1.89 [1.89, 1.89] | 0 |
| A2 + h(F-hat) | 0.131 [0.117, 0.143] | 0.129 [0.111, 0.15] | 2.21 [2.17, 2.24] | 0 |
| A4 + KM leaf | 0.105 [0.0917, 0.118] | 0.102 [0.084, 0.121] | 2.13 [2.09, 2.16] | 0 |
| g(F-hat) + h(F-hat) | 0.13 [0.117, 0.142] | 0.128 [0.11, 0.147] | 2.25 [2.21, 2.29] | 0 |

Hybrid MSE ratio to A2 (realized per draw; 1.05 table, R2 guard).

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| policy | H=8 (0.27 LT) | H=15 (0.50 LT) | H=30 (1.00 LT) | H=60 (2.00 LT) | H=120 (4.00 LT) |
|---|---|---|---|---|---|
| A4 + KM leaf | 1.07 [1.04, 1.1] needed, size not determined | 1.04 [1, 1.08] undetermined (n_eff < 50) | 1.02 [0.975, 1.07] undetermined | 0.99 [0.962, 1.02] negligible | 1.04 [1.02, 1.06] needed, size not determined |
| g(F-hat) + h(F-hat) | 1.01 [0.991, 1.02] negligible | 0.985 [0.962, 1.01] undetermined (n_eff < 50) | 0.977 [0.952, 1] lowers | 0.99 [0.97, 1.01] negligible | 0.991 [0.979, 1] negligible |

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| full system minus | false trust realized [CI] | false trust characteristic [CI] | trusted LT [CI] |
|---|---|---|---|
| A2 + constant | 0.04 [0.0285, 0.0512] | 0.028 [0.0075, 0.049] | 0.359 [0.32, 0.393] |
| A2 + h(F-hat) | -0.00075 [-0.00775, 0.007] | -0.001 [-0.012, 0.00976] | 0.0462 [0.0389, 0.0532] |
| A4 + KM leaf | 0.025 [0.0145, 0.0352] | 0.026 [0.008, 0.0433] | 0.123 [0.0997, 0.144] |

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| horizon model (own characteristic target) | pinball / constant's | constant/model ratio [CI] reading | cov 0.1 / 0.5 / 0.9 | C |
|---|---|---|---|---|
| h_A2(F-hat) | 0.103 / 0.145 | 1.41 [1.34, 1.48] substantial | 0.129 / 0.496 / 0.876 | 0.704 |
| h_g(F-hat) | 0.103 / 0.152 | 1.47 [1.4, 1.55] substantial | 0.128 / 0.485 / 0.873 | - |

### E-H2a. Amplification mismatch m(H) (H_0 = 1 LT; both r.m.s. <= 0.5 sigma_x)

Medians by tercile of I (low / mid / high). Spearman(m, I) on the kept states [95%]. B and A columns from the A/D record (oracle).

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| horizon | kept | m | abs drift w* | corr C/sqrt(E_C E_P) | Spearman(m, I) | B RI / OI | A drop-I (MSE) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 999 | -0.035 / 0.18 / 0.07 | 0.09 / 0.097 / 0.067 | 0.14 / 0.16 / 0.19 | 0.0508 [-0.00445, 0.111] | no interaction gain detected / no interaction gain detected | negligible |
| H=15 (0.50 LT) | 999 | -0.041 / 0.11 / 0.11 | 0.082 / 0.099 / 0.054 | 0.17 / 0.18 / 0.2 | 0.061 [0.00114, 0.122] | no interaction gain detected / no interaction gain detected | negligible |
| H=30 (1.00 LT) | 999 | 0 / 0 / 0 | 0 / 0 / 0 | 0.19 / 0.2 / 0.23 | (H_0) | no interaction gain detected / no interaction gain detected | negligible |
| H=60 (2.00 LT) | 924 | -0.08 / -0.2 / -0.16 | 0.086 / 0.13 / 0.094 | 0.21 / 0.23 / 0.28 | -0.0425 [-0.107, 0.021] | no interaction gain detected / interaction gain detected | negligible |
| H=120 (4.00 LT) | 695 | -1.2 / -1.4 / -1.4 | 0.21 / 0.32 / 0.3 | 0.3 / 0.38 / 0.32 | -0.05 [-0.125, 0.0233] | no interaction gain detected / no interaction gain detected | negligible |

**Reading: not determined** (horizons_used: ['60', '120'], horizons_supporting: [], horizons_null: []).

### E-H2e. Library size and error correlation (sweep states)

1000 sweep states. Delta = value at N_lib 100000 minus 1000. corr = the H2e correlation (0 by convention where an error is constant over the draws).

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| rho | valid | corr 0 small / large lib | median corr small -> large | set | median Delta corr [CI] | Spearman(Delta corr, Delta R) [CI] | reading |
|---|---|---|---|---|---|---|---|
| 0.01 | 1000 | 624 / 0 | 0 -> 0.458 | all (1000) | 0.379 [0.361, 0.397] | 0.204 [0.143, 0.26] | not consistent |
| 0.01 | 1000 | 624 / 0 | 0 -> 0.458 | both_defined (376) | 0.152 [0.118, 0.195] | 0.198 [0.0933, 0.291] | not consistent |
| 0.02 | 1000 | 299 / 0 | 0.119 -> 0.459 | all (1000) | 0.279 [0.254, 0.296] | 0.172 [0.106, 0.231] | not consistent |
| 0.02 | 1000 | 299 / 0 | 0.119 -> 0.459 | both_defined (701) | 0.173 [0.154, 0.204] | 0.167 [0.0889, 0.241] | not consistent |

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| rho | stratifier | median Delta corr low / mid / high | median Delta R low / mid / high |
|---|---|---|---|
| 0.01 | R | 0.35 / 0.38 / 0.39 | -1.3 / -1.3 / -1.4 |
| 0.01 | O | 0.37 / 0.38 / 0.38 | -1.4 / -1.4 / -1.2 |
| 0.01 | I | 0.37 / 0.34 / 0.42 | -1.4 / -1.3 / -1.3 |
| 0.01 | N | 0.4 / 0.35 / 0.39 | -1.4 / -1.3 / -1.3 |
| 0.01 | delta_R | 0.29 / 0.4 / 0.42 | -2 / -1.3 / -0.55 |
| 0.02 | R | 0.24 / 0.28 / 0.31 | -0.76 / -0.77 / -0.88 |
| 0.02 | O | 0.29 / 0.26 / 0.28 | -0.93 / -0.8 / -0.71 |
| 0.02 | I | 0.26 / 0.25 / 0.32 | -0.88 / -0.78 / -0.75 |
| 0.02 | N | 0.31 / 0.23 / 0.29 | -0.91 / -0.7 / -0.82 |
| 0.02 | delta_R | 0.22 / 0.27 / 0.33 | -1.4 / -0.8 / -0.13 |

**Reading** (final, after the convention check): rho 0.01: not consistent; rho 0.02: not consistent.

### E-H3c. A5 against A4

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| item | value |
|---|---|
| H3c ratio MSE(A5)/MSE(A4) [CI at level 0.983] (run) | 0.969 [0.922, 1.01], width 0.0915 |
| top-1% share: A5 loss / A4 loss / abs(A5 - A4) | 0.186 / 0.194 / 0.213 |
| autocorrelation of d = A5 - A4, lags 1..5 | 0.0065, 0.053, -0.011, -0.0011, -0.0074 |
| block-5 means: lag-1 autocorrelation, variance ratio | -0.0321, 1.07 |
| K chosen; leaves used test / calibration; largest leaf share test | 4; 4 / 4; 0.333 |
| w*(H_ref) within-leaf share of variance | 0.949 |
| bimodality coefficient R/O/I/N, oracle; deployable | 0.33/0.78/0.46/0.82; 0.5/0.79/0.46/0.91 |
| Spearman pairs (oracle) | RO 0.41, RI -0.023, RN 0.41, OI -0.034, ON 0.025, IN 0.013 |
| top-1% abs(d) states: mean percentile R/O/I/N | 0.72/0.89/0.76/0.47 |
| top-1% abs(d) states: median I pct; share high-I; median abs(x) pct; share sign change in window; share of sum d | 0.879; 0.8; 0.495; 1; 0.415 |

## chua

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| check | result |
|---|---|
| A2 rebuilt on 1..H_max equals the dumped A2 (bitwise); A4 horizon-free | True, True |
| refit reproduces WU-0048 (max abs: A/ROIN MSE oracle, deployable; W/ROIN L_w oracle, deployable) | 0 / 0 / 0 / 0 |
| T_c counts T = 1 / e_(T-1) = theta (A2 train, g train, A2 test, g test, A4 calibration) | 6/0, 12/0, 2/0, 0/0, 4/0 |
| A2 on 1..H_max: pooled curvature floor / columns at 0 or 1 | 0 / 0 |
| weights clipped to [0, 1] | g_oracle_test 644, g_oracle_train_oof 2144, gw_oracle_test 526, gw_oracle_train_oof 1625, g_deployable_test 1670, g_deployable_train_oof 6849, gw_deployable_test 456, gw_deployable_train_oof 1325 |

### C1. Separate performance (from the A/D record, no refit)

Allocation: MSE per rule (oracle: moment form; deployable: realized); reading of the rung against F (MSE ratio, 1.05 table, n_eff guard). G(F) = 1 - L_A(F)/L_A(constant).

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| horizon | profile | constant | separation | RO | F (ROIN) | X | X+F | G(F) | sep vs F | RO vs F | X+F vs F |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 0.000822 | 0.000577 | 0.00092 | 0.000626 | 0.000734 | 0.000687 | 0.617 | undetermined | undetermined | undetermined |
| H=8 (0.27 LT) | deployable | 0.000725 | 0.00068 | 0.000666 | 0.000672 | 0.000629 | 0.000627 | 0.241 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | oracle | 0.00217 | 0.00191 | 0.00224 | 0.00208 | 0.00252 | 0.00201 | 0.16 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | deployable | 0.00208 | 0.00233 | 0.00223 | 0.00256 | 0.00261 | 0.00255 | -1.02 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | oracle | 0.0143 | 0.014 | 0.0143 | 0.0137 | 0.0145 | 0.0138 | 0.203 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | deployable | 0.0129 | 0.0137 | 0.013 | 0.0129 | 0.0134 | 0.0131 | -0.00214 | undetermined | undetermined | undetermined |
| H=60 (2.00 LT) | oracle | 0.196 | 0.184 | 0.185 | 0.185 | 0.194 | 0.185 | 0.191 | negligible | negligible | negligible |
| H=60 (2.00 LT) | deployable | 0.182 | 0.182 | 0.177 | 0.176 | 0.179 | 0.176 | 0.141 | undetermined | negligible | negligible |
| H=120 (4.00 LT) | oracle | 0.649 | 0.669 | 0.636 | 0.637 | 0.648 | 0.64 | 0.0696 | needed, size not determined | negligible | negligible |
| H=120 (4.00 LT) | deployable | 0.615 | 0.639 | 0.608 | 0.609 | 0.613 | 0.611 | 0.0485 | needed, size not determined | negligible | negligible |

Horizon (Y = ln min(T_c, H_max)): pinball at 0.5 / Harrell's C / coverage of q_0.1 below the cap; reading against F.

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| profile | rung | pinball | C | cov q_0.1 | reading vs F |
|---|---|---|---|---|---|
| oracle | none | 0.214 | 0.5 | 0.091 | substantial |
| oracle | lyapunov | 0.249 | 0.675 | 0.0793 | substantial |
| oracle | RO | 0.191 | 0.636 | 0.093 | substantial |
| oracle | ROIN | 0.15 | 0.725 | 0.121 |  |
| oracle | X | 0.163 | 0.707 | 0.137 | undetermined |
| oracle | X+F | 0.124 | 0.776 | 0.134 | lowers |
| oracle | Lyapunov rank | | 0.671 | | |
| deployable | none | 0.214 | 0.5 | 0.091 | substantial |
| deployable | lyapunov | 0.254 | 0.67 | 0.0709 | substantial |
| deployable | RO | 0.186 | 0.648 | 0.0965 | substantial |
| deployable | ROIN | 0.15 | 0.727 | 0.116 |  |
| deployable | X | 0.167 | 0.699 | 0.12 | needed, size not determined |
| deployable | X+F | 0.127 | 0.773 | 0.133 | lowers |
| deployable | Lyapunov rank | | 0.666 | | |

### C2. Shared information (oracle and deployable profiles)

Skill retained = [L(constant) - L(bottleneck)] / [L(constant) - L(F)]; reading: keeps most (CI > 0.5), loses most (CI < 0.5), else not determined. Forward: horizon from g (five clipped weights; g_w: the L_w fits); reverse: weight from h (three quantiles), scored by L_A (MSE; deployable: realized per draw, R2 guard) and by L_w (weight units, unit-weight fits). Training inputs cross-fitted.

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| profile | direction | horizon | full skill [CI] | retained L_A / pinball [CI] | reading | retained L_w [CI] | reading L_w |
|---|---|---|---|---|---|---|---|
| oracle | forward (g; g_w) | all five | 0.0638 [0.0531, 0.0738] | 0.485 [0.405, 0.573] | not determined (interval spans 0.5) | 0.496 [0.404, 0.58] | not determined (interval spans 0.5) |
| oracle | forward, one weight | H=8 (0.27 LT) | | 0.0319 [0.00587, 0.0562] | loses most | | |
| oracle | forward, one weight | H=15 (0.50 LT) | | 0.0386 [0.00888, 0.0673] | loses most | | |
| oracle | forward, one weight | H=30 (1.00 LT) | | 0.111 [0.0765, 0.149] | loses most | | |
| oracle | forward, one weight | H=60 (2.00 LT) | | 0.145 [0.0979, 0.197] | loses most | | |
| oracle | forward, one weight | H=120 (4.00 LT) | | 0.249 [0.168, 0.324] | loses most | | |
| oracle | reverse | H=8 (0.27 LT) | 0.000196 [6.71e-05, 0.000364] | 0.482 [0.141, 1.07] | not determined (n_eff < 50) | 0.183 [0.042, 0.3] | loses most |
| oracle | reverse | H=15 (0.50 LT) | 9.1e-05 [-0.000162, 0.000315] | -2.7 [-, -] | not determined (full-profile skill not established) | 0.299 [0.184, 0.41] | loses most |
| oracle | reverse | H=30 (1.00 LT) | 0.000558 [-0.00011, 0.00119] | 0.475 [-, -] | not determined (full-profile skill not established) | 0.279 [0.17, 0.378] | loses most |
| oracle | reverse | H=60 (2.00 LT) | 0.0112 [0.00557, 0.0171] | 0.374 [0.0304, 0.76] | not determined (interval spans 0.5) | 0.466 [0.345, 0.601] | not determined (interval spans 0.5) |
| oracle | reverse | H=120 (4.00 LT) | 0.012 [0.00448, 0.0192] | 0.307 [-0.293, 0.723] | not determined (interval spans 0.5) | 0.531 [0.272, 0.826] | not determined (interval spans 0.5) |
| deployable | forward (g; g_w) | all five | 0.0642 [0.0538, 0.0736] | 0.48 [0.4, 0.554] | not determined (interval spans 0.5) | 0.477 [0.406, 0.548] | not determined (interval spans 0.5) |
| deployable | forward, one weight | H=8 (0.27 LT) | | 0.0266 [0.00639, 0.0443] | loses most | | |
| deployable | forward, one weight | H=15 (0.50 LT) | | 0.152 [0.121, 0.188] | loses most | | |
| deployable | forward, one weight | H=30 (1.00 LT) | | 0.0642 [0.0254, 0.101] | loses most | | |
| deployable | forward, one weight | H=60 (2.00 LT) | | 0.161 [0.108, 0.216] | loses most | | |
| deployable | forward, one weight | H=120 (4.00 LT) | | 0.304 [0.225, 0.377] | loses most | | |
| deployable | reverse | H=8 (0.27 LT) | 5.33e-05 [-2.56e-05, 0.000133] | 1.28 [-, -] | not determined (full-profile skill not established) | 0.231 [-0.00519, 0.501] | not determined (interval spans 0.5) |
| deployable | reverse | H=15 (0.50 LT) | -0.000483 [-0.00123, 4.63e-05] | - [-, -] | not determined (full-profile skill not established) | 0.332 [0.151, 0.536] | not determined (interval spans 0.5) |
| deployable | reverse | H=30 (1.00 LT) | -3.06e-06 [-0.000315, 0.000284] | - [-, -] | not determined (full-profile skill not established) | 0.436 [0.254, 0.593] | not determined (interval spans 0.5) |
| deployable | reverse | H=60 (2.00 LT) | 0.00634 [-0.0011, 0.0139] | 0.274 [-, -] | not determined (full-profile skill not established) | 0.534 [0.391, 0.706] | not determined (interval spans 0.5) |
| deployable | reverse | H=120 (4.00 LT) | 0.00673 [-0.00338, 0.0163] | 0.32 [-, -] | not determined (full-profile skill not established) | 0.418 [-0.24, 1.13] | not determined (interval spans 0.5) |

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| profile | forward C-index F / g / g_w | reverse MSE(h)/MSE(F) per horizon | math-spec prediction (both lose most) | largest single-weight retention at H |
|---|---|---|---|---|
| oracle | 0.725 / 0.65 / 0.668 | H=8 (0.27 LT) 1.16 [0.993, 1.35] undetermined (n_eff < 50); H=15 (0.50 LT) 1.16 [0.955, 1.42] undetermined (n_eff < 50); H=30 (1.00 LT) 1.02 [0.981, 1.09] undetermined (n_eff < 50); H=60 (2.00 LT) 1.04 [1.01, 1.07] needed, size not determined; H=120 (4.00 LT) 1.01 [1, 1.02] small | **not determined** | 120 |
| deployable | 0.727 / 0.657 / 0.668 | H=8 (0.27 LT) 0.978 [0.913, 1.04] undetermined (n_eff < 50); H=15 (0.50 LT) 0.905 [0.698, 1.17] undetermined (n_eff < 50); H=30 (1.00 LT) 0.999 [0.976, 1.03] undetermined (n_eff < 50); H=60 (2.00 LT) 1.03 [0.998, 1.06] undetermined; H=120 (4.00 LT) 1.01 [0.997, 1.02] negligible | **not determined** | 120 |

Oracle against deployable: retained (deployable) minus retained (oracle), paired 95% interval.

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| row | oracle | deployable | difference [CI] | reading |
|---|---|---|---|---|
| forward | 0.485 | 0.48 | -0.00478 [-0.0957, 0.0849] | no difference detected |
| forward_w | 0.496 | 0.477 | -0.0195 [-0.102, 0.0754] | no difference detected |
| reverse/8 | 0.482 | 1.28 | 0.795 [-, -] | not determined (n_eff < 50) |
| reverse_w/8 | 0.183 | 0.231 | 0.0483 [-0.203, 0.351] | no difference detected |
| reverse/15 | -2.7 | - | - [-, -] | not determined (full-profile skill not established) |
| reverse_w/15 | 0.299 | 0.332 | 0.0337 [-0.161, 0.271] | no difference detected |
| reverse/30 | 0.475 | - | - [-, -] | not determined (full-profile skill not established) |
| reverse_w/30 | 0.279 | 0.436 | 0.157 [-0.0118, 0.315] | no difference detected |
| reverse/60 | 0.374 | 0.274 | -0.1 [-, -] | not determined (full-profile skill not established) |
| reverse_w/60 | 0.466 | 0.534 | 0.0678 [-0.0871, 0.242] | no difference detected |
| reverse/120 | 0.307 | 0.32 | 0.0131 [-, -] | not determined (full-profile skill not established) |
| reverse_w/120 | 0.531 | 0.418 | -0.113 [-0.689, 0.49] | no difference detected |

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| horizon | Spearman(phi allocation, phi horizon) (4 items, descriptive) | phi_alloc R/O/I/N | phi_horizon R/O/I/N |
|---|---|---|---|
| H=8 (0.27 LT) | 1 | 7.4e-06/2.7e-05/0.00014/1.7e-05 | 0.0022/0.015/0.043/0.0041 |
| H=15 (0.50 LT) | -1 | 0.00022/-9.2e-05/-0.00016/0.00012 | 0.0022/0.015/0.043/0.0041 |
| H=30 (1.00 LT) | -0.2 | 0.00011/0.00018/0.0001/0.00017 | 0.0022/0.015/0.043/0.0041 |
| H=60 (2.00 LT) | -0.8 | 0.0093/0.0011/0.00031/0.0006 | 0.0022/0.015/0.043/0.0041 |
| H=120 (4.00 LT) | -1 | 0.01/0.00099/-0.0017/0.0023 | 0.0022/0.015/0.043/0.0041 |

### C3. The deployable chain

False trust = P(T <= q_0.1) per (state, draw), target 0.1; T realized (the run's first passage against the noisy truth) or characteristic (moments). Trusted horizon = mean q_0.1 (LT). A4 + KM leaf uses the calibration A4 hybrid's characteristic horizon (no per-draw calibration errors on the full grid).

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| policy | false trust realized [CI] | false trust characteristic [CI] | mean trusted (LT) [CI] | q at cap |
|---|---|---|---|---|
| A2 + constant | 0.0685 [0.0573, 0.08] | 0.093 [0.075, 0.111] | 0.967 [0.967, 0.967] | 0 |
| A2 + h(F-hat) | 0.0922 [0.08, 0.104] | 0.114 [0.0983, 0.132] | 1.41 [1.38, 1.44] | 0 |
| A4 + KM leaf | 0.0725 [0.0607, 0.0838] | 0.0955 [0.079, 0.112] | 1.21 [1.19, 1.23] | 0 |
| g(F-hat) + h(F-hat) | 0.0915 [0.0798, 0.102] | 0.115 [0.0985, 0.132] | 1.46 [1.43, 1.49] | 0 |

Hybrid MSE ratio to A2 (realized per draw; 1.05 table, R2 guard).

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| policy | H=8 (0.27 LT) | H=15 (0.50 LT) | H=30 (1.00 LT) | H=60 (2.00 LT) | H=120 (4.00 LT) |
|---|---|---|---|---|---|
| A4 + KM leaf | 0.888 [0.756, 1.02] undetermined (n_eff < 50) | 1.14 [0.999, 1.31] undetermined (n_eff < 50) | 1.06 [1.01, 1.12] undetermined (n_eff < 50) | 0.998 [0.964, 1.03] negligible | 1.04 [1.01, 1.06] needed, size not determined |
| g(F-hat) + h(F-hat) | 0.877 [0.752, 1] undetermined (n_eff < 50) | 1.25 [0.989, 1.57] undetermined (n_eff < 50) | 1 [0.974, 1.03] undetermined (n_eff < 50) | 0.967 [0.921, 1.01] negligible | 0.989 [0.973, 1.01] negligible |

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| full system minus | false trust realized [CI] | false trust characteristic [CI] | trusted LT [CI] |
|---|---|---|---|
| A2 + constant | 0.023 [0.00975, 0.0362] | 0.0215 [0.0015, 0.0425] | 0.493 [0.463, 0.528] |
| A2 + h(F-hat) | -0.00075 [-0.00751, 0.0055] | 0.00025 [-0.009, 0.0095] | 0.0533 [0.043, 0.064] |
| A4 + KM leaf | 0.019 [0.00725, 0.0302] | 0.019 [0.0035, 0.035] | 0.25 [0.225, 0.277] |

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| horizon model (own characteristic target) | pinball / constant's | constant/model ratio [CI] reading | cov 0.1 / 0.5 / 0.9 | C |
|---|---|---|---|---|
| h_A2(F-hat) | 0.155 / 0.229 | 1.48 [1.39, 1.56] substantial | 0.114 / 0.481 / 0.875 | 0.728 |
| h_g(F-hat) | 0.151 / 0.225 | 1.48 [1.4, 1.57] substantial | 0.115 / 0.479 / 0.868 | - |

### E-H2a. Amplification mismatch m(H) (H_0 = 1 LT; both r.m.s. <= 0.5 sigma_x)

Medians by tercile of I (low / mid / high). Spearman(m, I) on the kept states [95%]. B and A columns from the A/D record (oracle).

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| horizon | kept | m | abs drift w* | corr C/sqrt(E_C E_P) | Spearman(m, I) | B RI / OI | A drop-I (MSE) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 934 | -0.089 / 0.44 / 0.37 | 0.041 / 0.11 / 0.13 | 0.21 / 0.13 / 0.27 | 0.164 [0.103, 0.227] | no interaction gain detected / interaction gain detected | undetermined (n_eff < 50) |
| H=15 (0.50 LT) | 933 | -0.094 / -0.067 / 0.13 | 0.059 / 0.14 / 0.11 | 0.19 / 0.2 / 0.25 | 0.0895 [0.0292, 0.149] | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=30 (1.00 LT) | 938 | 0 / 0 / 0 | 0 / 0 / 0 | 0.2 / 0.19 / 0.31 | (H_0) | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=60 (2.00 LT) | 684 | -0.42 / -0.32 / -0.37 | 0.06 / 0.12 / 0.13 | 0.22 / 0.19 / 0.29 | 0.0353 [-0.0411, 0.105] | no interaction gain detected / no interaction gain detected | negligible |
| H=120 (4.00 LT) | 256 | -1.4 / -1.1 / -1.9 | 0.21 / 0.23 / 0.4 | 0.28 / 0.29 / 0.35 | -0.0127 [-0.13, 0.107] | no interaction gain detected / no interaction gain detected | negligible |

**Reading: not determined** (horizons_used: ['60', '120'], horizons_supporting: [], horizons_null: []).

### E-H2e. Library size and error correlation (sweep states)

1000 sweep states. Delta = value at N_lib 100000 minus 1000. corr = the H2e correlation (0 by convention where an error is constant over the draws).

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| rho | valid | corr 0 small / large lib | median corr small -> large | set | median Delta corr [CI] | Spearman(Delta corr, Delta R) [CI] | reading |
|---|---|---|---|---|---|---|---|
| 0.01 | 1000 | 562 / 12 | 0 -> 0.435 | all (1000) | 0.341 [0.321, 0.357] | 0.0275 [-0.0338, 0.0884] | not determined |
| 0.01 | 1000 | 562 / 12 | 0 -> 0.435 | both_defined (435) | 0.22 [0.181, 0.264] | 0.0101 [-0.0843, 0.102] | not determined |
| 0.02 | 1000 | 271 / 2 | 0.03 -> 0.414 | all (1000) | 0.28 [0.262, 0.307] | -0.11 [-0.169, -0.0474] | consistent |
| 0.02 | 1000 | 271 / 2 | 0.03 -> 0.414 | both_defined (727) | 0.224 [0.198, 0.251] | -0.136 [-0.209, -0.067] | consistent |

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| rho | stratifier | median Delta corr low / mid / high | median Delta R low / mid / high |
|---|---|---|---|
| 0.01 | R | 0.35 / 0.32 / 0.34 | -1.3 / -1.2 / -1.6 |
| 0.01 | O | 0.37 / 0.36 / 0.31 | -1.6 / -1.4 / -1.1 |
| 0.01 | I | 0.35 / 0.29 / 0.35 | -1.5 / -1.4 / -1.1 |
| 0.01 | N | 0.34 / 0.33 / 0.35 | -1.5 / -1.2 / -1.4 |
| 0.01 | delta_R | 0.34 / 0.33 / 0.35 | -2.2 / -1.3 / -0.55 |
| 0.02 | R | 0.24 / 0.26 / 0.34 | -0.75 / -0.67 / -1.1 |
| 0.02 | O | 0.35 / 0.24 / 0.26 | -1.2 / -0.8 / -0.56 |
| 0.02 | I | 0.31 / 0.25 / 0.28 | -1 / -0.93 / -0.54 |
| 0.02 | N | 0.33 / 0.25 / 0.29 | -1 / -0.63 / -0.87 |
| 0.02 | delta_R | 0.35 / 0.27 / 0.24 | -1.7 / -0.8 / -0.16 |

**Reading** (final, after the convention check): rho 0.01: not determined; rho 0.02: consistent.

### E-H3c. A5 against A4

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| item | value |
|---|---|
| H3c ratio MSE(A5)/MSE(A4) [CI at level 0.983] (run) | 0.953 [0.903, 1], width 0.0988 |
| top-1% share: A5 loss / A4 loss / abs(A5 - A4) | 0.61 / 0.618 / 0.347 |
| autocorrelation of d = A5 - A4, lags 1..5 | 0.012, -0.05, 0.0055, -0.035, -0.048 |
| block-5 means: lag-1 autocorrelation, variance ratio | -0.167, 1 |
| K chosen; leaves used test / calibration; largest leaf share test | 2; 2 / 2; 0.787 |
| w*(H_ref) within-leaf share of variance | 0.99 |
| bimodality coefficient R/O/I/N, oracle; deployable | 0.21/0.26/0.45/0.84; 0.37/0.45/0.46/0.9 |
| Spearman pairs (oracle) | RO 0.069, RI -0.037, RN 0.38, OI 0.37, ON 0.065, IN -0.015 |
| top-1% abs(d) states: mean percentile R/O/I/N | 0.54/0.59/0.91/0.4 |
| top-1% abs(d) states: median I pct; share high-I; median abs(x) pct; share sign change in window; share of sum d | 0.952; 0.9; 0.536; 0.1; 0.762 |

## E-H3c reading (this seed)

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| item | value |
|---|---|
| H3c interval widths | lorenz63 0.369, rossler 0.0915, chua 0.0988 |
| pattern (Lorenz-63 widest, Rössler narrowest) reproduced | True |
| Lorenz-63 part (top-1% share of sum abs(d) 0.683, median I percentile 0.266) | not consistent |
| Rössler part (BC deployable: R 0.501, O 0.787, I 0.46, N 0.906) | not consistent |
| **reading** | **not consistent** |

