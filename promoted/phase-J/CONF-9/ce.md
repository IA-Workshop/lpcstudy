# Phase J experiments C and E: CONF-9

**PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.** Run `phasej-CONF-9/phasej`; analysis commit `c19ad486b93a2ee96d64ce069ec42fd440428211` (dirty: False); A/D record `phasej-CONF-9/contrib-j/contrib.json`. Estimates with 95% intervals from the shared moving-block index sets (models fixed; training variance not included). Readings are descriptive; no causal claim; nothing here is set beside CONF-1.

## lorenz63

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| check | result |
|---|---|
| A2 rebuilt on 1..H_max equals the dumped A2 (bitwise); A4 horizon-free | True, True |
| refit reproduces WU-0048 (max abs: A/ROIN MSE oracle, deployable; W/ROIN L_w oracle, deployable) | 0 / 0 / 0 / 0 |
| T_c counts T = 1 / e_(T-1) = theta (A2 train, g train, A2 test, g test, A4 calibration) | 19/0, 80/0, 25/0, 142/0, 100/0 |
| A2 on 1..H_max: pooled curvature floor / columns at 0 or 1 | 0 / 0 |
| weights clipped to [0, 1] | g_oracle_test 2435, g_oracle_train_oof 2377, gw_oracle_test 2466, gw_oracle_train_oof 1927, g_deployable_test 7005, g_deployable_train_oof 5224, gw_deployable_test 2717, gw_deployable_train_oof 2161 |

### C1. Separate performance (from the A/D record, no refit)

Allocation: MSE per rule (oracle: moment form; deployable: realized); reading of the rung against F (MSE ratio, 1.05 table, n_eff guard). G(F) = 1 - L_A(F)/L_A(constant).

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| horizon | profile | constant | separation | RO | F (ROIN) | X | X+F | G(F) | sep vs F | RO vs F | X+F vs F |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 0.0171 | 0.00715 | 0.00655 | 0.00646 | 0.00706 | 0.00681 | 0.846 | undetermined | undetermined | undetermined |
| H=8 (0.27 LT) | deployable | 0.0185 | 0.0345 | 0.0119 | 0.0176 | 0.0076 | 0.00726 | 0.0653 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | oracle | 0.0301 | 0.0162 | 0.0155 | 0.014 | 0.0144 | 0.0141 | 0.832 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | deployable | 0.0319 | 0.0397 | 0.03 | 0.0246 | 0.0157 | 0.0168 | 0.346 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | oracle | 0.0546 | 0.0379 | 0.0388 | 0.0428 | 0.0373 | 0.0357 | 0.412 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | deployable | 0.0594 | 0.0653 | 0.0523 | 0.0483 | 0.0404 | 0.0412 | 0.331 | substantial | undetermined | lowers |
| H=60 (2.00 LT) | oracle | 0.153 | 0.143 | 0.14 | 0.138 | 0.14 | 0.136 | 0.286 | needed, size not determined | negligible | negligible |
| H=60 (2.00 LT) | deployable | 0.156 | 0.159 | 0.155 | 0.151 | 0.145 | 0.145 | 0.075 | needed, size not determined | undetermined | lowers |
| H=120 (4.00 LT) | oracle | 0.858 | 0.92 | 0.851 | 0.851 | 0.847 | 0.843 | 0.0285 | substantial | negligible | lowers |
| H=120 (4.00 LT) | deployable | 0.858 | 0.895 | 0.851 | 0.849 | 0.846 | 0.845 | 0.0348 | needed, size not determined | negligible | negligible |

Horizon (Y = ln min(T_c, H_max)): pinball at 0.5 / Harrell's C / coverage of q_0.1 below the cap; reading against F.

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | C | cov q_0.1 | reading vs F |
|---|---|---|---|---|---|
| oracle | none | 0.197 | 0.5 | 0.0963 | substantial |
| oracle | lyapunov | 0.305 | 0.615 | 0.0815 | substantial |
| oracle | RO | 0.193 | 0.567 | 0.129 | substantial |
| oracle | ROIN | 0.151 | 0.688 | 0.141 |  |
| oracle | X | 0.16 | 0.678 | 0.148 | needed, size not determined |
| oracle | X+F | 0.132 | 0.742 | 0.156 | lowers |
| oracle | Lyapunov rank | | 0.608 | | |
| deployable | none | 0.197 | 0.5 | 0.0963 | substantial |
| deployable | lyapunov | 0.297 | 0.622 | 0.0773 | substantial |
| deployable | RO | 0.191 | 0.574 | 0.117 | substantial |
| deployable | ROIN | 0.151 | 0.687 | 0.126 |  |
| deployable | X | 0.159 | 0.679 | 0.141 | needed, size not determined |
| deployable | X+F | 0.132 | 0.731 | 0.143 | lowers |
| deployable | Lyapunov rank | | 0.614 | | |

### C2. Shared information (oracle and deployable profiles)

Skill retained = [L(constant) - L(bottleneck)] / [L(constant) - L(F)]; reading: keeps most (CI > 0.5), loses most (CI < 0.5), else not determined. Forward: horizon from g (five clipped weights; g_w: the L_w fits); reverse: weight from h (three quantiles), scored by L_A (MSE; deployable: realized per draw, R2 guard) and by L_w (weight units, unit-weight fits). Training inputs cross-fitted.

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| profile | direction | horizon | full skill [CI] | retained L_A / pinball [CI] | reading | retained L_w [CI] | reading L_w |
|---|---|---|---|---|---|---|---|
| oracle | forward (g; g_w) | all five | 0.0456 [0.0409, 0.0503] | 0.132 [0.106, 0.158] | loses most | 0.405 [0.337, 0.465] | loses most |
| oracle | forward, one weight | H=8 (0.27 LT) | | 0.00306 [-0.00807, 0.0153] | loses most | | |
| oracle | forward, one weight | H=15 (0.50 LT) | | 0.00693 [-0.00327, 0.017] | loses most | | |
| oracle | forward, one weight | H=30 (1.00 LT) | | 0.0258 [0.0155, 0.0376] | loses most | | |
| oracle | forward, one weight | H=60 (2.00 LT) | | 0.0336 [0.0215, 0.0456] | loses most | | |
| oracle | forward, one weight | H=120 (4.00 LT) | | 0.0876 [0.059, 0.115] | loses most | | |
| oracle | reverse | H=8 (0.27 LT) | 0.0106 [0.00764, 0.0137] | 0.363 [0.0444, 0.646] | not determined (n_eff < 50) | 0.25 [0.208, 0.289] | loses most |
| oracle | reverse | H=15 (0.50 LT) | 0.0162 [0.0118, 0.0195] | 0.348 [0.0488, 0.538] | not determined (n_eff < 50) | 0.252 [0.213, 0.289] | loses most |
| oracle | reverse | H=30 (1.00 LT) | 0.0118 [0.00404, 0.018] | 0.358 [-0.428, 0.913] | not determined (n_eff < 50) | 0.311 [0.264, 0.354] | loses most |
| oracle | reverse | H=60 (2.00 LT) | 0.0156 [0.0108, 0.02] | 0.144 [0.000525, 0.258] | loses most | 0.287 [0.235, 0.33] | loses most |
| oracle | reverse | H=120 (4.00 LT) | 0.00723 [0.000285, 0.0142] | 0.922 [0.219, 19.4] | not determined (interval spans 0.5) | 0.351 [0.259, 0.458] | loses most |
| deployable | forward (g; g_w) | all five | 0.0458 [0.0412, 0.0502] | 0.23 [0.195, 0.263] | loses most | 0.401 [0.356, 0.447] | loses most |
| deployable | forward, one weight | H=8 (0.27 LT) | | 0.0873 [0.0704, 0.106] | loses most | | |
| deployable | forward, one weight | H=15 (0.50 LT) | | 0.0972 [0.0803, 0.115] | loses most | | |
| deployable | forward, one weight | H=30 (1.00 LT) | | 0.0778 [0.0615, 0.0947] | loses most | | |
| deployable | forward, one weight | H=60 (2.00 LT) | | 0.00275 [-0.00316, 0.00883] | loses most | | |
| deployable | forward, one weight | H=120 (4.00 LT) | | 0.138 [0.113, 0.162] | loses most | | |
| deployable | reverse | H=8 (0.27 LT) | 0.00091 [-0.00706, 0.00668] | 0.97 [-, -] | not determined (full-profile skill not established) | 0.265 [0.184, 0.349] | loses most |
| deployable | reverse | H=15 (0.50 LT) | 0.00734 [0.00133, 0.0124] | -0.0707 [-4.53, 0.425] | not determined (n_eff < 50) | 0.257 [0.178, 0.334] | loses most |
| deployable | reverse | H=30 (1.00 LT) | 0.011 [0.00496, 0.0164] | 0.553 [-0.214, 1] | not determined (interval spans 0.5) | 0.331 [0.26, 0.402] | loses most |
| deployable | reverse | H=60 (2.00 LT) | 0.00426 [0.000232, 0.00773] | 0.369 [-0.643, 2.78] | not determined (interval spans 0.5) | 0.266 [0.189, 0.338] | loses most |
| deployable | reverse | H=120 (4.00 LT) | 0.0088 [0.00526, 0.0124] | 0.7 [0.146, 1.14] | not determined (interval spans 0.5) | 0.715 [0.537, 0.913] | keeps most |

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| profile | forward C-index F / g / g_w | reverse MSE(h)/MSE(F) per horizon | math-spec prediction (both lose most) | largest single-weight retention at H |
|---|---|---|---|---|
| oracle | 0.688 / 0.595 / 0.622 | H=8 (0.27 LT) 2.05 [1.5, 3.63] undetermined (n_eff < 50); H=15 (0.50 LT) 1.76 [1.47, 2.18] undetermined (n_eff < 50); H=30 (1.00 LT) 1.18 [1.01, 1.39] undetermined (n_eff < 50); H=60 (2.00 LT) 1.1 [1.07, 1.13] substantial; H=120 (4.00 LT) 1 [0.993, 1.01] negligible | **consistent** | 120 |
| deployable | 0.687 / 0.618 / 0.618 | H=8 (0.27 LT) 1 [0.676, 1.63] undetermined (n_eff < 50); H=15 (0.50 LT) 1.32 [1.15, 1.53] undetermined (n_eff < 50); H=30 (1.00 LT) 1.1 [1, 1.22] undetermined; H=60 (2.00 LT) 1.02 [0.997, 1.04] negligible; H=120 (4.00 LT) 1 [0.999, 1.01] negligible | **consistent** | 120 |

Oracle against deployable: retained (deployable) minus retained (oracle), paired 95% interval.

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| row | oracle | deployable | difference [CI] | reading |
|---|---|---|---|---|
| forward | 0.132 | 0.23 | 0.0978 [0.0627, 0.131] | deployable retains more |
| forward_w | 0.405 | 0.401 | -0.00422 [-0.0663, 0.063] | no difference detected |
| reverse/8 | 0.363 | 0.97 | 0.608 [-, -] | not determined (n_eff < 50) |
| reverse_w/8 | 0.25 | 0.265 | 0.015 [-0.0681, 0.114] | no difference detected |
| reverse/15 | 0.348 | -0.0707 | -0.419 [-4.76, 0.145] | not determined (n_eff < 50) |
| reverse_w/15 | 0.252 | 0.257 | 0.00545 [-0.0711, 0.0841] | no difference detected |
| reverse/30 | 0.358 | 0.553 | 0.194 [-0.662, 1] | not determined (n_eff < 50) |
| reverse_w/30 | 0.311 | 0.331 | 0.0199 [-0.0541, 0.0975] | no difference detected |
| reverse/60 | 0.144 | 0.369 | 0.225 [-0.758, 2.6] | no difference detected |
| reverse_w/60 | 0.287 | 0.266 | -0.0209 [-0.102, 0.0604] | no difference detected |
| reverse/120 | 0.922 | 0.7 | -0.222 [-18.9, 0.689] | no difference detected |
| reverse_w/120 | 0.351 | 0.715 | 0.364 [0.196, 0.535] | deployable retains more |

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| horizon | Spearman(phi allocation, phi horizon) (4 items, descriptive) | phi_alloc R/O/I/N | phi_horizon R/O/I/N |
|---|---|---|---|
| H=8 (0.27 LT) | 0.6 | 0.00059/0.0063/0.004/-0.00036 | 0.0024/0.0091/0.032/0.0025 |
| H=15 (0.50 LT) | 0.6 | 0.001/0.013/0.0027/-0.00049 | 0.0024/0.0091/0.032/0.0025 |
| H=30 (1.00 LT) | 0.8 | -0.0018/0.012/0.003/-0.0012 | 0.0024/0.0091/0.032/0.0025 |
| H=60 (2.00 LT) | 0.6 | 0.0017/0.011/0.002/0.0011 | 0.0024/0.0091/0.032/0.0025 |
| H=120 (4.00 LT) | -0.2 | 0.0043/0.0017/0.0017/-0.00049 | 0.0024/0.0091/0.032/0.0025 |

### C3. The deployable chain

False trust = P(T <= q_0.1) per (state, draw), target 0.1; T realized (the run's first passage against the noisy truth) or characteristic (moments). Trusted horizon = mean q_0.1 (LT). A4 + KM leaf uses the calibration A4 hybrid's characteristic horizon (no per-draw calibration errors on the full grid).

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| policy | false trust realized [CI] | false trust characteristic [CI] | mean trusted (LT) [CI] | q at cap |
|---|---|---|---|---|
| A2 + constant | 0.0778 [0.0712, 0.084] | 0.102 [0.0935, 0.11] | 0.631 [0.631, 0.631] | 0 |
| A2 + h(F-hat) | 0.0959 [0.0899, 0.102] | 0.116 [0.107, 0.125] | 1.04 [1.03, 1.06] | 0 |
| A4 + KM leaf | 0.0754 [0.0698, 0.0808] | 0.111 [0.102, 0.12] | 0.88 [0.871, 0.889] | 0 |
| g(F-hat) + h(F-hat) | 0.0953 [0.0894, 0.102] | 0.112 [0.103, 0.12] | 1.14 [1.13, 1.15] | 0 |

Hybrid MSE ratio to A2 (realized per draw; 1.05 table, R2 guard).

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| policy | H=8 (0.27 LT) | H=15 (0.50 LT) | H=30 (1.00 LT) | H=60 (2.00 LT) | H=120 (4.00 LT) |
|---|---|---|---|---|---|
| A4 + KM leaf | 1.86 [1.37, 2.47] substantial | 1.24 [1.09, 1.36] substantial | 1.1 [1.02, 1.16] needed, size not determined | 1.02 [1.01, 1.04] small | 1.04 [1.03, 1.06] needed, size not determined |
| g(F-hat) + h(F-hat) | 0.95 [0.576, 1.37] undetermined | 0.768 [0.628, 0.946] lowers | 0.814 [0.729, 0.913] lowers | 0.972 [0.95, 0.998] lowers | 0.99 [0.985, 0.994] lowers |

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| full system minus | false trust realized [CI] | false trust characteristic [CI] | trusted LT [CI] |
|---|---|---|---|
| A2 + constant | 0.0175 [0.0112, 0.0245] | 0.00975 [0.00137, 0.0189] | 0.509 [0.496, 0.523] |
| A2 + h(F-hat) | -0.000625 [-0.00594, 0.00506] | -0.00456 [-0.0121, 0.00319] | 0.0978 [0.0863, 0.109] |
| A4 + KM leaf | 0.0199 [0.014, 0.0264] | 0.000438 [-0.00806, 0.00919] | 0.26 [0.245, 0.275] |

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| horizon model (own characteristic target) | pinball / constant's | constant/model ratio [CI] reading | cov 0.1 / 0.5 / 0.9 | C |
|---|---|---|---|---|
| h_A2(F-hat) | 0.202 / 0.26 | 1.28 [1.24, 1.33] substantial | 0.116 / 0.488 / 0.853 | 0.68 |
| h_g(F-hat) | 0.177 / 0.233 | 1.31 [1.27, 1.36] substantial | 0.112 / 0.494 / 0.854 | - |

### E-H2a. Amplification mismatch m(H) (H_0 = 1 LT; both r.m.s. <= 0.5 sigma_x)

Medians by tercile of I (low / mid / high). Spearman(m, I) on the kept states [95%]. B and A columns from the A/D record (oracle).

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| horizon | kept | m | abs drift w* | corr C/sqrt(E_C E_P) | Spearman(m, I) | B RI / OI | A drop-I (MSE) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 3595 | -0.057 / 0.084 / 0.31 | 0.044 / 0.038 / 0.068 | 0.097 / 0.13 / 0.14 | 0.121 [0.0861, 0.155] | interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=15 (0.50 LT) | 3571 | 0.03 / 0.098 / 0.02 | 0.043 / 0.045 / 0.062 | 0.1 / 0.14 / 0.15 | 0.0256 [-0.00656, 0.0586] | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=30 (1.00 LT) | 3631 | 0 / 0 / 0 | 0 / 0 / 0 | 0.12 / 0.14 / 0.18 | (H_0) | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=60 (2.00 LT) | 2856 | -0.03 / -0.0044 / -0.14 | 0.052 / 0.066 / 0.08 | 0.13 / 0.2 / 0.2 | -0.0137 [-0.0485, 0.0241] | interaction gain detected / interaction gain detected | negligible |
| H=120 (4.00 LT) | 755 | -1.8 / -2 / -2.4 | 0.27 / 0.41 / 0.49 | 0.21 / 0.32 / 0.32 | -0.101 [-0.168, -0.0282] | interaction gain detected / interaction gain detected | negligible |

**Reading: not determined** (horizons_used: ['60', '120'], horizons_supporting: [], horizons_null: ['60']).

### E-H2e. Library size and error correlation (sweep states)

1000 sweep states. Delta = value at N_lib 100000 minus 1000. corr = the H2e correlation (0 by convention where an error is constant over the draws).

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| rho | valid | corr 0 small / large lib | median corr small -> large | set | median Delta corr [CI] | Spearman(Delta corr, Delta R) [CI] | reading |
|---|---|---|---|---|---|---|---|
| 0.01 | 1000 | 727 / 23 | 0 -> 0.431 | all (1000) | 0.364 [0.337, 0.387] | 0.103 [0.0375, 0.163] | not consistent |
| 0.01 | 1000 | 727 / 23 | 0 -> 0.431 | both_defined (267) | 0.196 [0.15, 0.264] | -0.114 [-0.219, 0.00548] | not determined |
| 0.02 | 1000 | 451 / 6 | 0 -> 0.446 | all (1000) | 0.319 [0.297, 0.341] | 0.0442 [-0.0152, 0.0999] | not determined |
| 0.02 | 1000 | 451 / 6 | 0 -> 0.446 | both_defined (546) | 0.242 [0.211, 0.27] | -0.047 [-0.126, 0.0341] | not determined |

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| rho | stratifier | median Delta corr low / mid / high | median Delta R low / mid / high |
|---|---|---|---|
| 0.01 | R | 0.36 / 0.41 / 0.32 | -1.6 / -1.7 / -1.8 |
| 0.01 | O | 0.4 / 0.35 / 0.33 | -1.6 / -1.8 / -1.6 |
| 0.01 | I | 0.31 / 0.4 / 0.39 | -2 / -1.6 / -1.5 |
| 0.01 | N | 0.29 / 0.4 / 0.39 | -1.9 / -1.6 / -1.7 |
| 0.01 | delta_R | 0.33 / 0.37 / 0.4 | -2.7 / -1.7 / -0.79 |
| 0.02 | R | 0.32 / 0.33 / 0.3 | -1.1 / -1.1 / -1.3 |
| 0.02 | O | 0.32 / 0.33 / 0.3 | -1.1 / -1.3 / -1.2 |
| 0.02 | I | 0.31 / 0.31 / 0.34 | -1.5 / -1.1 / -0.98 |
| 0.02 | N | 0.27 / 0.35 / 0.33 | -1.4 / -1 / -1.2 |
| 0.02 | delta_R | 0.32 / 0.3 / 0.34 | -2.1 / -1.2 / -0.34 |

**Reading** (final, after the convention check): rho 0.01: not determined (depends on the zero-variance convention); rho 0.02: not determined.

### E-H3c. A5 against A4

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| item | value |
|---|---|
| H3c ratio MSE(A5)/MSE(A4) [CI at level 0.983] (run) | 0.808 [0.713, 0.936], width 0.222 |
| top-1% share: A5 loss / A4 loss / abs(A5 - A4) | 0.543 / 0.561 / 0.661 |
| autocorrelation of d = A5 - A4, lags 1..5 | -0.0023, -0.0024, -0.015, -0.0034, -0.0075 |
| block-5 means: lag-1 autocorrelation, variance ratio | -0.0627, 1 |
| K chosen; leaves used test / calibration; largest leaf share test | 6; 6 / 6; 0.323 |
| w*(H_ref) within-leaf share of variance | 0.91 |
| bimodality coefficient R/O/I/N, oracle; deployable | 0.27/0.76/0.56/0.84; 0.33/0.43/0.56/0.9 |
| Spearman pairs (oracle) | RO 0.53, RI -0.047, RN 0.3, OI 0.028, ON -0.046, IN 0.067 |
| top-1% abs(d) states: mean percentile R/O/I/N | 0.76/0.88/0.32/0.29 |
| top-1% abs(d) states: median I pct; share high-I; median abs(x) pct; share sign change in window; share of sum d | 0.267; 0.05; 0.276; 0.725; 0.979 |

## rossler

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| check | result |
|---|---|
| A2 rebuilt on 1..H_max equals the dumped A2 (bitwise); A4 horizon-free | True, True |
| refit reproduces WU-0048 (max abs: A/ROIN MSE oracle, deployable; W/ROIN L_w oracle, deployable) | 0 / 0 / 0 / 0 |
| T_c counts T = 1 / e_(T-1) = theta (A2 train, g train, A2 test, g test, A4 calibration) | 0/0, 0/0, 0/0, 0/0, 0/0 |
| A2 on 1..H_max: pooled curvature floor / columns at 0 or 1 | 0 / 0 |
| weights clipped to [0, 1] | g_oracle_test 3722, g_oracle_train_oof 2760, gw_oracle_test 2133, gw_oracle_train_oof 1519, g_deployable_test 10529, g_deployable_train_oof 7805, gw_deployable_test 1391, gw_deployable_train_oof 1256 |

### C1. Separate performance (from the A/D record, no refit)

Allocation: MSE per rule (oracle: moment form; deployable: realized); reading of the rung against F (MSE ratio, 1.05 table, n_eff guard). G(F) = 1 - L_A(F)/L_A(constant).

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| horizon | profile | constant | separation | RO | F (ROIN) | X | X+F | G(F) | sep vs F | RO vs F | X+F vs F |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 0.000128 | 0.000126 | 0.000119 | 0.000118 | 0.000127 | 0.000118 | 0.498 | substantial | small | negligible |
| H=8 (0.27 LT) | deployable | 0.000127 | 0.000138 | 0.000127 | 0.000127 | 0.000126 | 0.000126 | -0.0134 | substantial | negligible | lowers |
| H=15 (0.50 LT) | oracle | 0.000221 | 0.000213 | 0.000203 | 0.000201 | 0.000221 | 0.000201 | 0.551 | substantial | small | negligible |
| H=15 (0.50 LT) | deployable | 0.000213 | 0.000229 | 0.000214 | 0.000214 | 0.000212 | 0.000213 | -0.0524 | needed, size not determined | negligible | lowers |
| H=30 (1.00 LT) | oracle | 0.000785 | 0.000715 | 0.000699 | 0.000696 | 0.000775 | 0.000692 | 0.597 | small | negligible | negligible |
| H=30 (1.00 LT) | deployable | 0.00076 | 0.000815 | 0.000767 | 0.000766 | 0.000755 | 0.000758 | -0.047 | needed, size not determined | negligible | lowers |
| H=60 (2.00 LT) | oracle | 0.0132 | 0.0117 | 0.0118 | 0.0118 | 0.0135 | 0.0118 | 0.375 | negligible | negligible | negligible |
| H=60 (2.00 LT) | deployable | 0.0128 | 0.0129 | 0.0127 | 0.0127 | 0.0131 | 0.0128 | 0.0364 | negligible | negligible | negligible |
| H=120 (4.00 LT) | oracle | 0.108 | 0.112 | 0.107 | 0.107 | 0.108 | 0.106 | 0.0515 | needed, size not determined | small | lowers |
| H=120 (4.00 LT) | deployable | 0.106 | 0.11 | 0.105 | 0.105 | 0.106 | 0.104 | 0.0345 | needed, size not determined | small | negligible |

Horizon (Y = ln min(T_c, H_max)): pinball at 0.5 / Harrell's C / coverage of q_0.1 below the cap; reading against F.

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | C | cov q_0.1 | reading vs F |
|---|---|---|---|---|---|
| oracle | none | 0.161 | 0.5 | 0.102 | substantial |
| oracle | lyapunov | 0.171 | 0.635 | 0.0806 | substantial |
| oracle | RO | 0.155 | 0.567 | 0.114 | substantial |
| oracle | ROIN | 0.123 | 0.679 | 0.11 |  |
| oracle | X | 0.122 | 0.699 | 0.161 | negligible |
| oracle | X+F | 0.0927 | 0.767 | 0.15 | lowers |
| oracle | Lyapunov rank | | 0.631 | | |
| deployable | none | 0.161 | 0.5 | 0.102 | substantial |
| deployable | lyapunov | 0.173 | 0.628 | 0.0785 | substantial |
| deployable | RO | 0.149 | 0.6 | 0.123 | substantial |
| deployable | ROIN | 0.12 | 0.689 | 0.129 |  |
| deployable | X | 0.123 | 0.696 | 0.153 | undetermined |
| deployable | X+F | 0.0922 | 0.768 | 0.148 | lowers |
| deployable | Lyapunov rank | | 0.625 | | |

### C2. Shared information (oracle and deployable profiles)

Skill retained = [L(constant) - L(bottleneck)] / [L(constant) - L(F)]; reading: keeps most (CI > 0.5), loses most (CI < 0.5), else not determined. Forward: horizon from g (five clipped weights; g_w: the L_w fits); reverse: weight from h (three quantiles), scored by L_A (MSE; deployable: realized per draw, R2 guard) and by L_w (weight units, unit-weight fits). Training inputs cross-fitted.

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| profile | direction | horizon | full skill [CI] | retained L_A / pinball [CI] | reading | retained L_w [CI] | reading L_w |
|---|---|---|---|---|---|---|---|
| oracle | forward (g; g_w) | all five | 0.0383 [0.0351, 0.0417] | 0.611 [0.558, 0.663] | keeps most | 0.482 [0.424, 0.543] | not determined (interval spans 0.5) |
| oracle | forward, one weight | H=8 (0.27 LT) | | 0.0417 [0.0125, 0.0699] | loses most | | |
| oracle | forward, one weight | H=15 (0.50 LT) | | 0.0123 [-0.0174, 0.0408] | loses most | | |
| oracle | forward, one weight | H=30 (1.00 LT) | | 0.03 [0.000348, 0.0596] | loses most | | |
| oracle | forward, one weight | H=60 (2.00 LT) | | 0.0428 [0.00723, 0.0756] | loses most | | |
| oracle | forward, one weight | H=120 (4.00 LT) | | 0.507 [0.456, 0.558] | not determined (interval spans 0.5) | | |
| oracle | reverse | H=8 (0.27 LT) | 1.04e-05 [9.35e-06, 1.15e-05] | 0.165 [0.131, 0.2] | loses most | 0.228 [0.179, 0.278] | loses most |
| oracle | reverse | H=15 (0.50 LT) | 2.05e-05 [1.84e-05, 2.26e-05] | 0.132 [0.0831, 0.174] | loses most | 0.236 [0.186, 0.288] | loses most |
| oracle | reverse | H=30 (1.00 LT) | 8.89e-05 [7.48e-05, 0.000104] | 0.0706 [0.0471, 0.0932] | loses most | 0.231 [0.191, 0.271] | loses most |
| oracle | reverse | H=60 (2.00 LT) | 0.00137 [0.00109, 0.00166] | -0.0205 [-0.149, 0.0782] | loses most | 0.225 [0.172, 0.274] | loses most |
| oracle | reverse | H=120 (4.00 LT) | 0.00159 [0.000938, 0.00219] | 0.411 [0.151, 0.712] | not determined (interval spans 0.5) | 0.305 [0.146, 0.46] | loses most |
| deployable | forward (g; g_w) | all five | 0.0412 [0.0381, 0.0446] | 0.576 [0.53, 0.619] | keeps most | 0.589 [0.547, 0.63] | keeps most |
| deployable | forward, one weight | H=8 (0.27 LT) | | 0.0385 [0.0163, 0.062] | loses most | | |
| deployable | forward, one weight | H=15 (0.50 LT) | | 0.0208 [0.000971, 0.0409] | loses most | | |
| deployable | forward, one weight | H=30 (1.00 LT) | | 0.0486 [0.0222, 0.0744] | loses most | | |
| deployable | forward, one weight | H=60 (2.00 LT) | | 0.054 [0.0349, 0.0738] | loses most | | |
| deployable | forward, one weight | H=120 (4.00 LT) | | 0.51 [0.468, 0.553] | not determined (interval spans 0.5) | | |
| deployable | reverse | H=8 (0.27 LT) | -2.67e-07 [-1.24e-06, 6.27e-07] | - [-, -] | not determined (full-profile skill not established) | 0.0355 [0.0096, 0.0604] | loses most |
| deployable | reverse | H=15 (0.50 LT) | -1.51e-06 [-4.68e-06, 1.18e-06] | - [-, -] | not determined (full-profile skill not established) | 0.0527 [0.0294, 0.0752] | loses most |
| deployable | reverse | H=30 (1.00 LT) | -5.83e-06 [-1.81e-05, 5.8e-06] | - [-, -] | not determined (full-profile skill not established) | 0.0806 [0.0501, 0.112] | loses most |
| deployable | reverse | H=60 (2.00 LT) | 0.000121 [-4.29e-05, 0.000282] | 0.397 [-, -] | not determined (full-profile skill not established) | 0.171 [0.117, 0.231] | loses most |
| deployable | reverse | H=120 (4.00 LT) | 0.00098 [0.000417, 0.00153] | 0.596 [-0.145, 1.21] | not determined (interval spans 0.5) | 0.609 [0.453, 0.789] | not determined (interval spans 0.5) |

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| profile | forward C-index F / g / g_w | reverse MSE(h)/MSE(F) per horizon | math-spec prediction (both lose most) | largest single-weight retention at H |
|---|---|---|---|---|
| oracle | 0.679 / 0.633 / 0.613 | H=8 (0.27 LT) 1.07 [1.07, 1.08] substantial; H=15 (0.50 LT) 1.09 [1.08, 1.1] substantial; H=30 (1.00 LT) 1.12 [1.1, 1.14] substantial; H=60 (2.00 LT) 1.12 [1.09, 1.15] substantial; H=120 (4.00 LT) 1.01 [1, 1.01] small | **not consistent** | 120 |
| deployable | 0.689 / 0.633 / 0.636 | H=8 (0.27 LT) 0.998 [0.991, 1.01] negligible; H=15 (0.50 LT) 0.993 [0.978, 1.01] negligible; H=30 (1.00 LT) 0.995 [0.98, 1.01] negligible; H=60 (2.00 LT) 1.01 [0.993, 1.02] negligible; H=120 (4.00 LT) 1 [0.998, 1.01] negligible | **not consistent** | 120 |

Oracle against deployable: retained (deployable) minus retained (oracle), paired 95% interval.

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| row | oracle | deployable | difference [CI] | reading |
|---|---|---|---|---|
| forward | 0.611 | 0.576 | -0.0345 [-0.0856, 0.0152] | no difference detected |
| forward_w | 0.482 | 0.589 | 0.107 [0.0463, 0.167] | deployable retains more |
| reverse/8 | 0.165 | - | - [-, -] | not determined (full-profile skill not established) |
| reverse_w/8 | 0.228 | 0.0355 | -0.193 [-0.24, -0.145] | deployable retains less |
| reverse/15 | 0.132 | - | - [-, -] | not determined (full-profile skill not established) |
| reverse_w/15 | 0.236 | 0.0527 | -0.183 [-0.235, -0.132] | deployable retains less |
| reverse/30 | 0.0706 | - | - [-, -] | not determined (full-profile skill not established) |
| reverse_w/30 | 0.231 | 0.0806 | -0.15 [-0.198, -0.101] | deployable retains less |
| reverse/60 | -0.0205 | 0.397 | 0.418 [-, -] | not determined (full-profile skill not established) |
| reverse_w/60 | 0.225 | 0.171 | -0.0541 [-0.126, 0.0228] | no difference detected |
| reverse/120 | 0.411 | 0.596 | 0.185 [-0.484, 0.743] | no difference detected |
| reverse_w/120 | 0.305 | 0.609 | 0.304 [0.111, 0.517] | deployable retains more |

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| horizon | Spearman(phi allocation, phi horizon) (4 items, descriptive) | phi_alloc R/O/I/N | phi_horizon R/O/I/N |
|---|---|---|---|
| H=8 (0.27 LT) | -1 | 6.7e-06/1.1e-06/3.1e-12/2.6e-06 | 0.00091/0.0097/0.025/0.0026 |
| H=15 (0.50 LT) | -1 | 1.3e-05/2e-06/4.5e-09/5.1e-06 | 0.00091/0.0097/0.025/0.0026 |
| H=30 (1.00 LT) | -1 | 6.4e-05/7.7e-06/6.5e-08/1.8e-05 | 0.00091/0.0097/0.025/0.0026 |
| H=60 (2.00 LT) | -1 | 0.0011/6.6e-05/7e-06/0.00018 | 0.00091/0.0097/0.025/0.0026 |
| H=120 (4.00 LT) | 0.4 | 0.00069/9.4e-05/0.00074/6.3e-05 | 0.00091/0.0097/0.025/0.0026 |

### C3. The deployable chain

False trust = P(T <= q_0.1) per (state, draw), target 0.1; T realized (the run's first passage against the noisy truth) or characteristic (moments). Trusted horizon = mean q_0.1 (LT). A4 + KM leaf uses the calibration A4 hybrid's characteristic horizon (no per-draw calibration errors on the full grid).

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| policy | false trust realized [CI] | false trust characteristic [CI] | mean trusted (LT) [CI] | q at cap |
|---|---|---|---|---|
| A2 + constant | 0.099 [0.0927, 0.105] | 0.11 [0.0995, 0.119] | 1.89 [1.89, 1.89] | 0 |
| A2 + h(F-hat) | 0.13 [0.124, 0.136] | 0.128 [0.118, 0.138] | 2.23 [2.21, 2.25] | 0 |
| A4 + KM leaf | 0.111 [0.105, 0.117] | 0.107 [0.0984, 0.116] | 2.13 [2.12, 2.15] | 0 |
| g(F-hat) + h(F-hat) | 0.134 [0.128, 0.141] | 0.129 [0.12, 0.138] | 2.27 [2.25, 2.29] | 0 |

Hybrid MSE ratio to A2 (realized per draw; 1.05 table, R2 guard).

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| policy | H=8 (0.27 LT) | H=15 (0.50 LT) | H=30 (1.00 LT) | H=60 (2.00 LT) | H=120 (4.00 LT) |
|---|---|---|---|---|---|
| A4 + KM leaf | 1.09 [1.07, 1.1] substantial | 1.08 [1.06, 1.1] substantial | 1.07 [1.05, 1.1] substantial | 1 [0.988, 1.02] negligible | 1.04 [1.03, 1.06] needed, size not determined |
| g(F-hat) + h(F-hat) | 1 [0.995, 1.01] negligible | 1.01 [0.994, 1.02] negligible | 1.01 [0.992, 1.02] negligible | 0.99 [0.977, 1] negligible | 0.991 [0.986, 0.997] lowers |

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| full system minus | false trust realized [CI] | false trust characteristic [CI] | trusted LT [CI] |
|---|---|---|---|
| A2 + constant | 0.0351 [0.0291, 0.0411] | 0.0195 [0.00869, 0.0306] | 0.383 [0.362, 0.403] |
| A2 + h(F-hat) | 0.004 [0, 0.00775] | 0.00106 [-0.00481, 0.00637] | 0.0455 [0.0417, 0.0494] |
| A4 + KM leaf | 0.0229 [0.0176, 0.028] | 0.0218 [0.013, 0.0309] | 0.14 [0.13, 0.151] |

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| horizon model (own characteristic target) | pinball / constant's | constant/model ratio [CI] reading | cov 0.1 / 0.5 / 0.9 | C |
|---|---|---|---|---|
| h_A2(F-hat) | 0.104 / 0.154 | 1.47 [1.44, 1.51] substantial | 0.128 / 0.507 / 0.867 | 0.712 |
| h_g(F-hat) | 0.105 / 0.157 | 1.5 [1.46, 1.54] substantial | 0.129 / 0.503 / 0.862 | - |

### E-H2a. Amplification mismatch m(H) (H_0 = 1 LT; both r.m.s. <= 0.5 sigma_x)

Medians by tercile of I (low / mid / high). Spearman(m, I) on the kept states [95%]. B and A columns from the A/D record (oracle).

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| horizon | kept | m | abs drift w* | corr C/sqrt(E_C E_P) | Spearman(m, I) | B RI / OI | A drop-I (MSE) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 3996 | -0.075 / 0.11 / 0.13 | 0.079 / 0.081 / 0.066 | 0.17 / 0.17 / 0.21 | 0.0876 [0.0576, 0.119] | no interaction gain detected / interaction gain detected | negligible |
| H=15 (0.50 LT) | 3996 | -0.057 / 0.17 / 0.11 | 0.074 / 0.069 / 0.046 | 0.19 / 0.17 / 0.22 | 0.0799 [0.0502, 0.112] | no interaction gain detected / interaction gain detected | negligible |
| H=30 (1.00 LT) | 3996 | 0 / 0 / 0 | 0 / 0 / 0 | 0.21 / 0.2 / 0.23 | (H_0) | no interaction gain detected / interaction gain detected | negligible |
| H=60 (2.00 LT) | 3695 | -0.25 / -0.2 / -0.27 | 0.083 / 0.1 / 0.1 | 0.26 / 0.24 / 0.28 | -0.0166 [-0.0489, 0.0158] | interaction gain detected / interaction gain detected | negligible |
| H=120 (4.00 LT) | 2780 | -1.2 / -1.6 / -1.5 | 0.21 / 0.34 / 0.31 | 0.34 / 0.35 / 0.34 | -0.0398 [-0.0724, -0.00393] | no interaction gain detected / no interaction gain detected | small |

**Reading: not consistent** (horizons_used: ['60', '120'], horizons_supporting: [], horizons_null: ['60', '120']).

### E-H2e. Library size and error correlation (sweep states)

1000 sweep states. Delta = value at N_lib 100000 minus 1000. corr = the H2e correlation (0 by convention where an error is constant over the draws).

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| rho | valid | corr 0 small / large lib | median corr small -> large | set | median Delta corr [CI] | Spearman(Delta corr, Delta R) [CI] | reading |
|---|---|---|---|---|---|---|---|
| 0.01 | 1000 | 592 / 0 | 0 -> 0.466 | all (1000) | 0.367 [0.344, 0.383] | 0.184 [0.122, 0.236] | not consistent |
| 0.01 | 1000 | 592 / 0 | 0 -> 0.466 | both_defined (408) | 0.151 [0.117, 0.192] | 0.117 [0.00784, 0.216] | not consistent |
| 0.02 | 1000 | 300 / 0 | 0.132 -> 0.469 | all (1000) | 0.27 [0.251, 0.294] | 0.236 [0.178, 0.293] | not consistent |
| 0.02 | 1000 | 300 / 0 | 0.132 -> 0.469 | both_defined (700) | 0.153 [0.126, 0.19] | 0.187 [0.112, 0.262] | not consistent |

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| rho | stratifier | median Delta corr low / mid / high | median Delta R low / mid / high |
|---|---|---|---|
| 0.01 | R | 0.35 / 0.36 / 0.4 | -1.4 / -1.4 / -1.4 |
| 0.01 | O | 0.39 / 0.36 / 0.34 | -1.5 / -1.4 / -1.3 |
| 0.01 | I | 0.36 / 0.34 / 0.38 | -1.5 / -1.3 / -1.4 |
| 0.01 | N | 0.36 / 0.36 / 0.38 | -1.4 / -1.3 / -1.4 |
| 0.01 | delta_R | 0.3 / 0.38 / 0.42 | -2 / -1.4 / -0.58 |
| 0.02 | R | 0.25 / 0.24 / 0.31 | -0.89 / -0.85 / -0.87 |
| 0.02 | O | 0.29 / 0.26 / 0.26 | -0.9 / -0.86 / -0.84 |
| 0.02 | I | 0.26 / 0.27 / 0.27 | -0.93 / -0.78 / -0.87 |
| 0.02 | N | 0.28 / 0.26 / 0.28 | -0.91 / -0.8 / -0.9 |
| 0.02 | delta_R | 0.18 / 0.26 / 0.33 | -1.4 / -0.86 / -0.11 |

**Reading** (final, after the convention check): rho 0.01: not consistent; rho 0.02: not consistent.

### E-H3c. A5 against A4

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| item | value |
|---|---|
| H3c ratio MSE(A5)/MSE(A4) [CI at level 0.983] (run) | 0.934 [0.915, 0.955], width 0.0402 |
| top-1% share: A5 loss / A4 loss / abs(A5 - A4) | 0.156 / 0.157 / 0.174 |
| autocorrelation of d = A5 - A4, lags 1..5 | -0.004, -0.0073, -0.019, 0.0015, 0.013 |
| block-5 means: lag-1 autocorrelation, variance ratio | -0.0204, 0.973 |
| K chosen; leaves used test / calibration; largest leaf share test | 4; 4 / 4; 0.39 |
| w*(H_ref) within-leaf share of variance | 0.959 |
| bimodality coefficient R/O/I/N, oracle; deployable | 0.22/0.79/0.46/0.84; 0.5/0.8/0.47/0.91 |
| Spearman pairs (oracle) | RO 0.37, RI -0.043, RN 0.38, OI -0.025, ON -0.023, IN -0.01 |
| top-1% abs(d) states: mean percentile R/O/I/N | 0.69/0.81/0.77/0.42 |
| top-1% abs(d) states: median I pct; share high-I; median abs(x) pct; share sign change in window; share of sum d | 0.781; 0.775; 0.485; 1; 0.345 |

## chua

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| check | result |
|---|---|
| A2 rebuilt on 1..H_max equals the dumped A2 (bitwise); A4 horizon-free | True, True |
| refit reproduces WU-0048 (max abs: A/ROIN MSE oracle, deployable; W/ROIN L_w oracle, deployable) | 0 / 0 / 0 / 0 |
| T_c counts T = 1 / e_(T-1) = theta (A2 train, g train, A2 test, g test, A4 calibration) | 1/0, 4/0, 2/0, 8/0, 0/0 |
| A2 on 1..H_max: pooled curvature floor / columns at 0 or 1 | 0 / 0 |
| weights clipped to [0, 1] | g_oracle_test 2102, g_oracle_train_oof 1725, gw_oracle_test 2077, gw_oracle_train_oof 1657, g_deployable_test 7552, g_deployable_train_oof 5585, gw_deployable_test 1540, gw_deployable_train_oof 1189 |

### C1. Separate performance (from the A/D record, no refit)

Allocation: MSE per rule (oracle: moment form; deployable: realized); reading of the rung against F (MSE ratio, 1.05 table, n_eff guard). G(F) = 1 - L_A(F)/L_A(constant).

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| horizon | profile | constant | separation | RO | F (ROIN) | X | X+F | G(F) | sep vs F | RO vs F | X+F vs F |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 0.00117 | 0.00117 | 0.00116 | 0.00121 | 0.00118 | 0.00115 | -0.245 | undetermined | undetermined | undetermined |
| H=8 (0.27 LT) | deployable | 0.00062 | 0.000687 | 0.000621 | 0.000623 | 0.000625 | 0.000624 | - | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | oracle | 0.00356 | 0.00327 | 0.00339 | 0.00339 | 0.00358 | 0.00337 | 0.212 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | deployable | 0.00286 | 0.00298 | 0.00286 | 0.00287 | 0.00285 | 0.00284 | -0.187 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | oracle | 0.0186 | 0.0168 | 0.0182 | 0.0173 | 0.0189 | 0.0175 | 0.187 | lowers | undetermined | negligible |
| H=30 (1.00 LT) | deployable | 0.0189 | 0.0189 | 0.0187 | 0.0186 | 0.0191 | 0.0186 | 0.0517 | undetermined | negligible | negligible |
| H=60 (2.00 LT) | oracle | 0.201 | 0.194 | 0.192 | 0.191 | 0.199 | 0.192 | 0.138 | negligible | negligible | small |
| H=60 (2.00 LT) | deployable | 0.202 | 0.203 | 0.196 | 0.195 | 0.2 | 0.195 | 0.103 | needed, size not determined | small | negligible |
| H=120 (4.00 LT) | oracle | 0.647 | 0.662 | 0.63 | 0.629 | 0.644 | 0.632 | 0.0951 | needed, size not determined | small | negligible |
| H=120 (4.00 LT) | deployable | 0.638 | 0.667 | 0.626 | 0.624 | 0.636 | 0.624 | 0.0785 | needed, size not determined | negligible | negligible |

Horizon (Y = ln min(T_c, H_max)): pinball at 0.5 / Harrell's C / coverage of q_0.1 below the cap; reading against F.

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| profile | rung | pinball | C | cov q_0.1 | reading vs F |
|---|---|---|---|---|---|
| oracle | none | 0.229 | 0.5 | 0.0995 | substantial |
| oracle | lyapunov | 0.257 | 0.671 | 0.0815 | substantial |
| oracle | RO | 0.207 | 0.622 | 0.113 | substantial |
| oracle | ROIN | 0.164 | 0.713 | 0.158 |  |
| oracle | X | 0.177 | 0.699 | 0.147 | needed, size not determined |
| oracle | X+F | 0.138 | 0.767 | 0.15 | lowers |
| oracle | Lyapunov rank | | 0.666 | | |
| deployable | none | 0.229 | 0.5 | 0.0995 | substantial |
| deployable | lyapunov | 0.258 | 0.67 | 0.0765 | substantial |
| deployable | RO | 0.203 | 0.628 | 0.102 | substantial |
| deployable | ROIN | 0.164 | 0.718 | 0.127 |  |
| deployable | X | 0.176 | 0.7 | 0.135 | needed, size not determined |
| deployable | X+F | 0.139 | 0.767 | 0.136 | lowers |
| deployable | Lyapunov rank | | 0.663 | | |

### C2. Shared information (oracle and deployable profiles)

Skill retained = [L(constant) - L(bottleneck)] / [L(constant) - L(F)]; reading: keeps most (CI > 0.5), loses most (CI < 0.5), else not determined. Forward: horizon from g (five clipped weights; g_w: the L_w fits); reverse: weight from h (three quantiles), scored by L_A (MSE; deployable: realized per draw, R2 guard) and by L_w (weight units, unit-weight fits). Training inputs cross-fitted.

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| profile | direction | horizon | full skill [CI] | retained L_A / pinball [CI] | reading | retained L_w [CI] | reading L_w |
|---|---|---|---|---|---|---|---|
| oracle | forward (g; g_w) | all five | 0.0651 [0.0602, 0.0701] | 0.334 [0.293, 0.376] | loses most | 0.496 [0.442, 0.548] | not determined (interval spans 0.5) |
| oracle | forward, one weight | H=8 (0.27 LT) | | 0.0211 [0.00963, 0.0315] | loses most | | |
| oracle | forward, one weight | H=15 (0.50 LT) | | 0.0217 [0.0116, 0.0332] | loses most | | |
| oracle | forward, one weight | H=30 (1.00 LT) | | 0.0151 [-0.00486, 0.0333] | loses most | | |
| oracle | forward, one weight | H=60 (2.00 LT) | | 0.161 [0.135, 0.186] | loses most | | |
| oracle | forward, one weight | H=120 (4.00 LT) | | 0.0845 [0.0615, 0.107] | loses most | | |
| oracle | reverse | H=8 (0.27 LT) | -3.76e-05 [-0.000241, 0.000129] | - [-, -] | not determined (full-profile skill not established) | 0.273 [0.215, 0.329] | loses most |
| oracle | reverse | H=15 (0.50 LT) | 0.000167 [8.24e-05, 0.000249] | -0.15 [-1.18, 0.292] | not determined (n_eff < 50) | 0.275 [0.222, 0.329] | loses most |
| oracle | reverse | H=30 (1.00 LT) | 0.00125 [0.000717, 0.00182] | 0.231 [0.0305, 0.406] | loses most | 0.378 [0.324, 0.431] | loses most |
| oracle | reverse | H=60 (2.00 LT) | 0.00969 [0.00551, 0.0135] | 0.263 [0.141, 0.449] | loses most | 0.394 [0.332, 0.461] | loses most |
| oracle | reverse | H=120 (4.00 LT) | 0.0186 [0.0136, 0.0234] | 0.322 [0.182, 0.477] | loses most | 0.416 [0.296, 0.553] | not determined (interval spans 0.5) |
| deployable | forward (g; g_w) | all five | 0.0655 [0.0608, 0.0704] | 0.493 [0.451, 0.531] | not determined (interval spans 0.5) | 0.649 [0.616, 0.682] | keeps most |
| deployable | forward, one weight | H=8 (0.27 LT) | | 0.0167 [0.00593, 0.0279] | loses most | | |
| deployable | forward, one weight | H=15 (0.50 LT) | | 0.0104 [0.000291, 0.0208] | loses most | | |
| deployable | forward, one weight | H=30 (1.00 LT) | | 0.0769 [0.0662, 0.0887] | loses most | | |
| deployable | forward, one weight | H=60 (2.00 LT) | | 0.133 [0.112, 0.153] | loses most | | |
| deployable | forward, one weight | H=120 (4.00 LT) | | 0.225 [0.192, 0.256] | loses most | | |
| deployable | reverse | H=8 (0.27 LT) | -2.64e-06 [-1.31e-05, 7.4e-06] | - [-, -] | not determined (full-profile skill not established) | 0.081 [0.0019, 0.156] | loses most |
| deployable | reverse | H=15 (0.50 LT) | -1.56e-05 [-8.01e-05, 4.24e-05] | - [-, -] | not determined (full-profile skill not established) | 0.332 [0.256, 0.408] | loses most |
| deployable | reverse | H=30 (1.00 LT) | 0.000362 [-0.000345, 0.00114] | 1.1 [-, -] | not determined (full-profile skill not established) | 0.385 [0.305, 0.461] | loses most |
| deployable | reverse | H=60 (2.00 LT) | 0.00731 [0.00496, 0.00979] | 0.5 [0.315, 0.751] | not determined (interval spans 0.5) | 0.542 [0.467, 0.617] | not determined (interval spans 0.5) |
| deployable | reverse | H=120 (4.00 LT) | 0.0147 [0.0103, 0.0187] | 0.618 [0.459, 0.839] | not determined (interval spans 0.5) | 0.558 [0.444, 0.707] | not determined (interval spans 0.5) |

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| profile | forward C-index F / g / g_w | reverse MSE(h)/MSE(F) per horizon | math-spec prediction (both lose most) | largest single-weight retention at H |
|---|---|---|---|---|
| oracle | 0.713 / 0.634 / 0.658 | H=8 (0.27 LT) 0.969 [0.758, 1.09] undetermined (n_eff < 50); H=15 (0.50 LT) 1.06 [1.02, 1.1] undetermined (n_eff < 50); H=30 (1.00 LT) 1.06 [1.03, 1.08] needed, size not determined; H=60 (2.00 LT) 1.04 [1.02, 1.06] needed, size not determined; H=120 (4.00 LT) 1.02 [1.01, 1.03] small | **consistent** | 60 |
| deployable | 0.718 / 0.651 / 0.68 | H=8 (0.27 LT) 1 [0.988, 1.02] undetermined (n_eff < 50); H=15 (0.50 LT) 0.996 [0.975, 1.02] undetermined (n_eff < 50); H=30 (1.00 LT) 0.998 [0.956, 1.04] negligible; H=60 (2.00 LT) 1.02 [1.01, 1.03] small; H=120 (4.00 LT) 1.01 [1, 1.01] small | **not determined** | 120 |

Oracle against deployable: retained (deployable) minus retained (oracle), paired 95% interval.

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| row | oracle | deployable | difference [CI] | reading |
|---|---|---|---|---|
| forward | 0.334 | 0.493 | 0.159 [0.112, 0.206] | deployable retains more |
| forward_w | 0.496 | 0.649 | 0.153 [0.103, 0.204] | deployable retains more |
| reverse/8 | - | - | - [-, -] | not determined (full-profile skill not established) |
| reverse_w/8 | 0.273 | 0.081 | -0.192 [-0.274, -0.114] | deployable retains less |
| reverse/15 | -0.15 | - | - [-, -] | not determined (n_eff < 50) |
| reverse_w/15 | 0.275 | 0.332 | 0.0573 [-0.0289, 0.142] | no difference detected |
| reverse/30 | 0.231 | 1.1 | 0.871 [-, -] | not determined (full-profile skill not established) |
| reverse_w/30 | 0.378 | 0.385 | 0.00754 [-0.0609, 0.0721] | no difference detected |
| reverse/60 | 0.263 | 0.5 | 0.237 [0.000927, 0.474] | deployable retains more |
| reverse_w/60 | 0.394 | 0.542 | 0.148 [0.0717, 0.224] | deployable retains more |
| reverse/120 | 0.322 | 0.618 | 0.296 [0.118, 0.523] | deployable retains more |
| reverse_w/120 | 0.416 | 0.558 | 0.143 [-0.00234, 0.299] | no difference detected |

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| horizon | Spearman(phi allocation, phi horizon) (4 items, descriptive) | phi_alloc R/O/I/N | phi_horizon R/O/I/N |
|---|---|---|---|
| H=8 (0.27 LT) | -0.8 | 5.9e-05/-4.7e-05/-2.9e-05/-2e-05 | 0.00095/0.016/0.046/0.0029 |
| H=15 (0.50 LT) | -0.8 | 0.00012/5e-05/-9.7e-06/1.1e-05 | 0.00095/0.016/0.046/0.0029 |
| H=30 (1.00 LT) | -0.8 | 0.00091/-8.1e-05/0.00021/0.00021 | 0.00095/0.016/0.046/0.0029 |
| H=60 (2.00 LT) | -0.4 | 0.0034/0.0035/0.00095/0.0018 | 0.00095/0.016/0.046/0.0029 |
| H=120 (4.00 LT) | -0.2 | 0.01/0.0028/0.0032/0.0025 | 0.00095/0.016/0.046/0.0029 |

### C3. The deployable chain

False trust = P(T <= q_0.1) per (state, draw), target 0.1; T realized (the run's first passage against the noisy truth) or characteristic (moments). Trusted horizon = mean q_0.1 (LT). A4 + KM leaf uses the calibration A4 hybrid's characteristic horizon (no per-draw calibration errors on the full grid).

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| policy | false trust realized [CI] | false trust characteristic [CI] | mean trusted (LT) [CI] | q at cap |
|---|---|---|---|---|
| A2 + constant | 0.0777 [0.0717, 0.0839] | 0.101 [0.0917, 0.111] | 0.967 [0.967, 0.967] | 0 |
| A2 + h(F-hat) | 0.106 [0.0989, 0.112] | 0.126 [0.116, 0.135] | 1.39 [1.37, 1.4] | 0 |
| A4 + KM leaf | 0.0918 [0.0857, 0.0983] | 0.114 [0.105, 0.124] | 1.36 [1.35, 1.38] | 0 |
| g(F-hat) + h(F-hat) | 0.102 [0.0964, 0.109] | 0.121 [0.113, 0.131] | 1.44 [1.42, 1.45] | 0 |

Hybrid MSE ratio to A2 (realized per draw; 1.05 table, R2 guard).

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| policy | H=8 (0.27 LT) | H=15 (0.50 LT) | H=30 (1.00 LT) | H=60 (2.00 LT) | H=120 (4.00 LT) |
|---|---|---|---|---|---|
| A4 + KM leaf | 1.11 [1.07, 1.15] undetermined (n_eff < 50) | 1.04 [0.997, 1.09] undetermined (n_eff < 50) | 0.999 [0.969, 1.03] negligible | 1 [0.988, 1.02] negligible | 1.05 [1.03, 1.06] needed, size not determined |
| g(F-hat) + h(F-hat) | 1 [0.988, 1.02] undetermined (n_eff < 50) | 1.01 [0.984, 1.03] undetermined (n_eff < 50) | 0.981 [0.942, 1.02] negligible | 0.963 [0.951, 0.975] lowers | 0.977 [0.971, 0.984] lowers |

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| full system minus | false trust realized [CI] | false trust characteristic [CI] | trusted LT [CI] |
|---|---|---|---|
| A2 + constant | 0.0248 [0.0181, 0.0314] | 0.0202 [0.0101, 0.0306] | 0.47 [0.454, 0.487] |
| A2 + h(F-hat) | -0.00313 [-0.00681, 0.000562] | -0.00406 [-0.00906, 0.00106] | 0.05 [0.0455, 0.0542] |
| A4 + KM leaf | 0.0106 [0.00525, 0.0161] | 0.00725 [-0.000314, 0.0147] | 0.0729 [0.0636, 0.0816] |

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| horizon model (own characteristic target) | pinball / constant's | constant/model ratio [CI] reading | cov 0.1 / 0.5 / 0.9 | C |
|---|---|---|---|---|
| h_A2(F-hat) | 0.163 / 0.237 | 1.46 [1.42, 1.49] substantial | 0.126 / 0.51 / 0.888 | 0.728 |
| h_g(F-hat) | 0.16 / 0.237 | 1.48 [1.44, 1.52] substantial | 0.121 / 0.514 / 0.885 | - |

### E-H2a. Amplification mismatch m(H) (H_0 = 1 LT; both r.m.s. <= 0.5 sigma_x)

Medians by tercile of I (low / mid / high). Spearman(m, I) on the kept states [95%]. B and A columns from the A/D record (oracle).

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| horizon | kept | m | abs drift w* | corr C/sqrt(E_C E_P) | Spearman(m, I) | B RI / OI | A drop-I (MSE) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 3686 | -0.049 / 0.19 / 0.46 | 0.054 / 0.1 / 0.12 | 0.19 / 0.15 / 0.24 | 0.177 [0.145, 0.209] | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=15 (0.50 LT) | 3678 | 0.024 / 0.04 / 0.28 | 0.058 / 0.11 / 0.099 | 0.19 / 0.17 / 0.25 | 0.129 [0.0991, 0.16] | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=30 (1.00 LT) | 3694 | 0 / 0 / 0 | 0 / 0 / 0 | 0.2 / 0.18 / 0.26 | (H_0) | no interaction gain detected / interaction gain detected | negligible |
| H=60 (2.00 LT) | 2626 | -0.36 / -0.65 / -0.071 | 0.069 / 0.16 / 0.11 | 0.24 / 0.2 / 0.27 | 0.0226 [-0.0177, 0.0592] | no interaction gain detected / no interaction gain detected | negligible |
| H=120 (4.00 LT) | 1054 | -1.5 / -1.9 / -0.74 | 0.25 / 0.39 / 0.17 | 0.29 / 0.27 / 0.35 | 0.0363 [-0.0255, 0.0994] | no interaction gain detected / interaction gain detected | small |

**Reading: not consistent** (horizons_used: ['60', '120'], horizons_supporting: [], horizons_null: ['60', '120']).

### E-H2e. Library size and error correlation (sweep states)

1000 sweep states. Delta = value at N_lib 100000 minus 1000. corr = the H2e correlation (0 by convention where an error is constant over the draws).

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| rho | valid | corr 0 small / large lib | median corr small -> large | set | median Delta corr [CI] | Spearman(Delta corr, Delta R) [CI] | reading |
|---|---|---|---|---|---|---|---|
| 0.01 | 1000 | 548 / 13 | 0 -> 0.43 | all (1000) | 0.338 [0.319, 0.359] | 0.0532 [-0.00621, 0.108] | not determined |
| 0.01 | 1000 | 548 / 13 | 0 -> 0.43 | both_defined (448) | 0.196 [0.16, 0.229] | 0.082 [-0.00707, 0.17] | not determined |
| 0.02 | 1000 | 290 / 0 | 0.0501 -> 0.407 | all (1000) | 0.25 [0.226, 0.278] | -0.00372 [-0.0612, 0.0552] | not determined |
| 0.02 | 1000 | 290 / 0 | 0.0501 -> 0.407 | both_defined (710) | 0.175 [0.14, 0.198] | 0.0399 [-0.037, 0.11] | not determined |

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| rho | stratifier | median Delta corr low / mid / high | median Delta R low / mid / high |
|---|---|---|---|
| 0.01 | R | 0.33 / 0.36 / 0.33 | -1.2 / -0.94 / -1.4 |
| 0.01 | O | 0.36 / 0.31 / 0.33 | -1.6 / -1.1 / -0.86 |
| 0.01 | I | 0.32 / 0.32 / 0.4 | -1.2 / -1.2 / -1.1 |
| 0.01 | N | 0.34 / 0.33 / 0.34 | -1.4 / -0.9 / -1.2 |
| 0.01 | delta_R | 0.32 / 0.32 / 0.36 | -2.2 / -1.2 / -0.37 |
| 0.02 | R | 0.23 / 0.25 / 0.29 | -0.67 / -0.48 / -0.96 |
| 0.02 | O | 0.34 / 0.23 / 0.21 | -1.1 / -0.69 / -0.44 |
| 0.02 | I | 0.22 / 0.25 / 0.28 | -0.75 / -0.8 / -0.65 |
| 0.02 | N | 0.29 / 0.21 / 0.25 | -0.97 / -0.45 / -0.73 |
| 0.02 | delta_R | 0.28 / 0.23 / 0.25 | -1.6 / -0.71 / -0.042 |

**Reading** (final, after the convention check): rho 0.01: not determined; rho 0.02: not determined.

### E-H3c. A5 against A4

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| item | value |
|---|---|
| H3c ratio MSE(A5)/MSE(A4) [CI at level 0.983] (run) | 0.992 [0.96, 1.03], width 0.0666 |
| top-1% share: A5 loss / A4 loss / abs(A5 - A4) | 0.598 / 0.619 / 0.464 |
| autocorrelation of d = A5 - A4, lags 1..5 | 0.0068, -0.01, 0.038, -0.0048, 0.013 |
| block-5 means: lag-1 autocorrelation, variance ratio | 0.0332, 1 |
| K chosen; leaves used test / calibration; largest leaf share test | 4; 4 / 4; 0.398 |
| w*(H_ref) within-leaf share of variance | 0.938 |
| bimodality coefficient R/O/I/N, oracle; deployable | 0.23/0.17/0.43/0.85; 0.32/0.47/0.44/0.89 |
| Spearman pairs (oracle) | RO 0.058, RI 0.05, RN 0.34, OI 0.32, ON 0.12, IN -0.0021 |
| top-1% abs(d) states: mean percentile R/O/I/N | 0.68/0.38/0.91/0.44 |
| top-1% abs(d) states: median I pct; share high-I; median abs(x) pct; share sign change in window; share of sum d | 0.973; 0.95; 0.344; 0.3; 1.25 |

## E-H3c reading (this seed)

PHASE J CONFIRMATORY (CONF-9): pre-registered analysis, UNPROMOTED.

| item | value |
|---|---|
| H3c interval widths | lorenz63 0.222, rossler 0.0402, chua 0.0666 |
| pattern (Lorenz-63 widest, Rössler narrowest) reproduced | True |
| Lorenz-63 part (top-1% share of sum abs(d) 0.661, median I percentile 0.267) | not consistent |
| Rössler part (BC deployable: R 0.502, O 0.801, I 0.466, N 0.91) | not consistent |
| **reading** | **not consistent** |

