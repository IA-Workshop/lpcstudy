# Phase J experiments C and E: DEV-4

**DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.** Run `/home/brianm/projects/physics/chaos/lpcstudy-wt/run/phj-f701a47/runs/dev/phj-DEV-4/full`; analysis commit `33cb71e06322baa281454f26e4b74f804a725026` (dirty: False); A/D record `/home/brianm/projects/physics/chaos/lpcstudy-wt/run/phj-f701a47/runs/dev/phj-DEV-4/contrib-33cb71e/contrib.json`. Estimates with 95% intervals from the shared moving-block index sets (models fixed; training variance not included). Readings are descriptive; no causal claim; nothing here is set beside CONF-1.

## lorenz63

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| check | result |
|---|---|
| A2 rebuilt on 1..H_max equals the dumped A2 (bitwise); A4 horizon-free | True, True |
| refit reproduces WU-0048 (max abs: A/ROIN MSE oracle, deployable; W/ROIN L_w oracle, deployable) | 0 / 0 / 0 / 0 |
| T_c counts T = 1 / e_(T-1) = theta (A2 train, g train, A2 test, g test, A4 calibration) | 21/0, 100/0, 6/0, 36/0, 152/0 |
| A2 on 1..H_max: pooled curvature floor / columns at 0 or 1 | 0 / 0 |
| weights clipped to [0, 1] | g_oracle_test 744, g_oracle_train_oof 2403, gw_oracle_test 630, gw_oracle_train_oof 1902, g_deployable_test 562, g_deployable_train_oof 2837, gw_deployable_test 356, gw_deployable_train_oof 904 |

### C1. Separate performance (from the A/D record, no refit)

Allocation: MSE per rule (oracle: moment form; deployable: realized); reading of the rung against F (MSE ratio, 1.05 table, n_eff guard). G(F) = 1 - L_A(F)/L_A(constant).

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| horizon | profile | constant | separation | RO | F (ROIN) | X | X+F | G(F) | sep vs F | RO vs F | X+F vs F |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 0.0147 | 0.00593 | 0.0087 | 0.00604 | 0.00571 | 0.00509 | 0.777 | undetermined | undetermined | undetermined |
| H=8 (0.27 LT) | deployable | 0.0143 | 0.0236 | 0.00989 | 0.00912 | 0.00512 | 0.00399 | 0.484 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | oracle | 0.0284 | 0.0115 | 0.0114 | 0.0114 | 0.0153 | 0.0112 | 0.833 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | deployable | 0.03 | 0.0319 | 0.0214 | 0.0229 | 0.0148 | 0.0154 | 0.32 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | oracle | 0.0454 | 0.0361 | 0.0365 | 0.0371 | 0.0299 | 0.0347 | 0.334 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | deployable | 0.0519 | 0.0551 | 0.0464 | 0.0469 | 0.0327 | 0.0326 | 0.159 | undetermined | undetermined | undetermined |
| H=60 (2.00 LT) | oracle | 0.158 | 0.161 | 0.15 | 0.156 | 0.152 | 0.149 | 0.0395 | undetermined | undetermined | undetermined |
| H=60 (2.00 LT) | deployable | 0.141 | 0.138 | 0.139 | 0.136 | 0.139 | 0.133 | 0.115 | undetermined | undetermined | undetermined |
| H=120 (4.00 LT) | oracle | 0.89 | 0.947 | 0.882 | 0.875 | 0.885 | 0.876 | 0.0554 | needed, size not determined | negligible | negligible |
| H=120 (4.00 LT) | deployable | 0.878 | 0.916 | 0.875 | 0.874 | 0.874 | 0.871 | 0.0169 | needed, size not determined | negligible | negligible |

Horizon (Y = ln min(T_c, H_max)): pinball at 0.5 / Harrell's C / coverage of q_0.1 below the cap; reading against F.

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| profile | rung | pinball | C | cov q_0.1 | reading vs F |
|---|---|---|---|---|---|
| oracle | none | 0.195 | 0.5 | 0.103 | substantial |
| oracle | lyapunov | 0.298 | 0.624 | 0.0718 | substantial |
| oracle | RO | 0.19 | 0.574 | 0.125 | substantial |
| oracle | ROIN | 0.148 | 0.692 | 0.148 |  |
| oracle | X | 0.158 | 0.673 | 0.142 | undetermined |
| oracle | X+F | 0.127 | 0.736 | 0.153 | lowers |
| oracle | Lyapunov rank | | 0.627 | | |
| deployable | none | 0.195 | 0.5 | 0.103 | substantial |
| deployable | lyapunov | 0.29 | 0.625 | 0.0769 | substantial |
| deployable | RO | 0.189 | 0.584 | 0.116 | substantial |
| deployable | ROIN | 0.144 | 0.701 | 0.12 |  |
| deployable | X | 0.158 | 0.672 | 0.144 | undetermined |
| deployable | X+F | 0.129 | 0.736 | 0.135 | lowers |
| deployable | Lyapunov rank | | 0.628 | | |

### C2. Shared information (oracle and deployable profiles)

Skill retained = [L(constant) - L(bottleneck)] / [L(constant) - L(F)]; reading: keeps most (CI > 0.5), loses most (CI < 0.5), else not determined. Forward: horizon from g (five clipped weights; g_w: the L_w fits); reverse: weight from h (three quantiles), scored by L_A (MSE; deployable: realized per draw, R2 guard) and by L_w (weight units, unit-weight fits). Training inputs cross-fitted.

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| profile | direction | horizon | full skill [CI] | retained L_A / pinball [CI] | reading | retained L_w [CI] | reading L_w |
|---|---|---|---|---|---|---|---|
| oracle | forward (g; g_w) | all five | 0.0467 [0.0369, 0.0575] | 0.0951 [0.0464, 0.149] | loses most | 0.301 [0.182, 0.426] | loses most |
| oracle | forward, one weight | H=8 (0.27 LT) | | -0.00577 [-0.0298, 0.0186] | loses most | | |
| oracle | forward, one weight | H=15 (0.50 LT) | | -0.0056 [-0.0365, 0.0249] | loses most | | |
| oracle | forward, one weight | H=30 (1.00 LT) | | -0.0138 [-0.0421, 0.0133] | loses most | | |
| oracle | forward, one weight | H=60 (2.00 LT) | | 0.00834 [-0.0117, 0.0282] | loses most | | |
| oracle | forward, one weight | H=120 (4.00 LT) | | 0.0759 [0.023, 0.135] | loses most | | |
| oracle | reverse | H=8 (0.27 LT) | 0.00864 [0.00633, 0.0113] | -0.225 [-0.775, 0.204] | not determined (n_eff < 50) | 0.208 [0.127, 0.284] | loses most |
| oracle | reverse | H=15 (0.50 LT) | 0.017 [0.012, 0.0226] | -0.195 [-0.929, 0.317] | not determined (n_eff < 50) | 0.234 [0.165, 0.302] | loses most |
| oracle | reverse | H=30 (1.00 LT) | 0.00837 [-0.0038, 0.0194] | -1.87 [-, -] | not determined (full-profile skill not established) | 0.21 [0.127, 0.291] | loses most |
| oracle | reverse | H=60 (2.00 LT) | 0.0023 [-0.0115, 0.0163] | -2.79 [-, -] | not determined (full-profile skill not established) | 0.243 [0.139, 0.359] | loses most |
| oracle | reverse | H=120 (4.00 LT) | 0.0151 [0.000592, 0.0289] | -0.0436 [-3.69, 1.08] | not determined (interval spans 0.5) | 0.134 [-0.0223, 0.317] | loses most |
| deployable | forward (g; g_w) | all five | 0.0502 [0.041, 0.0595] | 0.201 [0.135, 0.267] | loses most | 0.304 [0.224, 0.39] | loses most |
| deployable | forward, one weight | H=8 (0.27 LT) | | 0.0556 [0.0225, 0.0888] | loses most | | |
| deployable | forward, one weight | H=15 (0.50 LT) | | 0.0233 [0.00107, 0.048] | loses most | | |
| deployable | forward, one weight | H=30 (1.00 LT) | | 0.0478 [0.0137, 0.082] | loses most | | |
| deployable | forward, one weight | H=60 (2.00 LT) | | 0.0229 [-0.0168, 0.0638] | loses most | | |
| deployable | forward, one weight | H=120 (4.00 LT) | | 0.118 [0.0759, 0.164] | loses most | | |
| deployable | reverse | H=8 (0.27 LT) | 0.0052 [0.00229, 0.00868] | -0.428 [-1.2, 0.568] | not determined (n_eff < 50) | 0.0824 [-0.0745, 0.227] | loses most |
| deployable | reverse | H=15 (0.50 LT) | 0.00704 [0.000691, 0.0128] | -0.844 [-18.7, 0.87] | not determined (n_eff < 50) | 0.115 [0.0411, 0.189] | loses most |
| deployable | reverse | H=30 (1.00 LT) | 0.005 [-0.00715, 0.0168] | -1.22 [-, -] | not determined (full-profile skill not established) | 0.128 [-0.0107, 0.256] | loses most |
| deployable | reverse | H=60 (2.00 LT) | 0.00471 [-0.00244, 0.0119] | 0.491 [-, -] | not determined (full-profile skill not established) | 0.18 [-0.0292, 0.384] | loses most |
| deployable | reverse | H=120 (4.00 LT) | 0.0044 [-0.00458, 0.0133] | 1.84 [-, -] | not determined (full-profile skill not established) | 0.444 [0.08, 0.866] | not determined (interval spans 0.5) |

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| profile | forward C-index F / g / g_w | reverse MSE(h)/MSE(F) per horizon | math-spec prediction (both lose most) | largest single-weight retention at H |
|---|---|---|---|---|
| oracle | 0.692 / 0.582 / 0.616 | H=8 (0.27 LT) 2.75 [1.83, 12.1] undetermined (n_eff < 50); H=15 (0.50 LT) 2.79 [1.77, 5.06] undetermined (n_eff < 50); H=30 (1.00 LT) 1.65 [1.16, 2.54] undetermined (n_eff < 50); H=60 (2.00 LT) 1.06 [0.986, 1.14] undetermined (n_eff < 50); H=120 (4.00 LT) 1.02 [1, 1.04] small | **consistent** | 120 |
| deployable | 0.701 / 0.622 / 0.612 | H=8 (0.27 LT) 1.81 [1.15, 3.09] undetermined (n_eff < 50); H=15 (0.50 LT) 1.57 [1.07, 2.34] undetermined (n_eff < 50); H=30 (1.00 LT) 1.24 [1.08, 1.47] undetermined (n_eff < 50); H=60 (2.00 LT) 1.02 [0.974, 1.07] undetermined; H=120 (4.00 LT) 0.996 [0.987, 1] negligible | **consistent** | 120 |

Oracle against deployable: retained (deployable) minus retained (oracle), paired 95% interval.

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| row | oracle | deployable | difference [CI] | reading |
|---|---|---|---|---|
| forward | 0.0951 | 0.201 | 0.106 [0.0478, 0.163] | deployable retains more |
| forward_w | 0.301 | 0.304 | 0.00317 [-0.135, 0.146] | no difference detected |
| reverse/8 | -0.225 | -0.428 | -0.203 [-0.845, 0.653] | not determined (n_eff < 50) |
| reverse_w/8 | 0.208 | 0.0824 | -0.126 [-0.286, 0.0203] | no difference detected |
| reverse/15 | -0.195 | -0.844 | -0.649 [-17.9, 1] | not determined (n_eff < 50) |
| reverse_w/15 | 0.234 | 0.115 | -0.119 [-0.209, -0.0236] | deployable retains less |
| reverse/30 | -1.87 | -1.22 | 0.654 [-, -] | not determined (full-profile skill not established) |
| reverse_w/30 | 0.21 | 0.128 | -0.0823 [-0.214, 0.0416] | no difference detected |
| reverse/60 | -2.79 | 0.491 | 3.28 [-, -] | not determined (full-profile skill not established) |
| reverse_w/60 | 0.243 | 0.18 | -0.063 [-0.278, 0.138] | no difference detected |
| reverse/120 | -0.0436 | 1.84 | 1.88 [-, -] | not determined (full-profile skill not established) |
| reverse_w/120 | 0.134 | 0.444 | 0.309 [-0.014, 0.714] | no difference detected |

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| horizon | Spearman(phi allocation, phi horizon) (4 items, descriptive) | phi_alloc R/O/I/N | phi_horizon R/O/I/N |
|---|---|---|---|
| H=8 (0.27 LT) | 1 | 0.00091/0.0024/0.0052/0.00016 | 0.00081/0.013/0.033/0.00047 |
| H=15 (0.50 LT) | 0.4 | 0.0033/0.018/0.0015/-0.0058 | 0.00081/0.013/0.033/0.00047 |
| H=30 (1.00 LT) | 0.8 | -0.0014/0.0087/0.0026/-0.0015 | 0.00081/0.013/0.033/0.00047 |
| H=60 (2.00 LT) | 0.4 | 0.001/0.004/-0.00044/-0.0023 | 0.00081/0.013/0.033/0.00047 |
| H=120 (4.00 LT) | 0.6 | -0.0025/0.013/0.0051/-0.00018 | 0.00081/0.013/0.033/0.00047 |

### C3. The deployable chain

False trust = P(T <= q_0.1) per (state, draw), target 0.1; T realized (the run's first passage against the noisy truth) or characteristic (moments). Trusted horizon = mean q_0.1 (LT). A4 + KM leaf uses the calibration A4 hybrid's characteristic horizon (no per-draw calibration errors on the full grid).

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| policy | false trust realized [CI] | false trust characteristic [CI] | mean trusted (LT) [CI] | q at cap |
|---|---|---|---|---|
| A2 + constant | 0.0612 [0.0495, 0.0732] | 0.092 [0.076, 0.108] | 0.39 [0.39, 0.39] | 0 |
| A2 + h(F-hat) | 0.0925 [0.0798, 0.106] | 0.122 [0.105, 0.14] | 0.95 [0.923, 0.976] | 0 |
| A4 + KM leaf | 0.0658 [0.0547, 0.0772] | 0.11 [0.094, 0.127] | 0.669 [0.648, 0.69] | 0 |
| g(F-hat) + h(F-hat) | 0.106 [0.0915, 0.121] | 0.13 [0.113, 0.149] | 1.04 [1.01, 1.07] | 0 |

Hybrid MSE ratio to A2 (realized per draw; 1.05 table, R2 guard).

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| policy | H=8 (0.27 LT) | H=15 (0.50 LT) | H=30 (1.00 LT) | H=60 (2.00 LT) | H=120 (4.00 LT) |
|---|---|---|---|---|---|
| A4 + KM leaf | 1.64 [0.97, 2.75] undetermined (n_eff < 50) | 1.02 [0.782, 1.27] undetermined (n_eff < 50) | 1.06 [0.935, 1.18] undetermined (n_eff < 50) | 0.982 [0.944, 1.02] negligible | 1.04 [1.02, 1.07] needed, size not determined |
| g(F-hat) + h(F-hat) | 0.633 [0.409, 0.828] undetermined (n_eff < 50) | 0.733 [0.551, 0.936] undetermined (n_eff < 50) | 0.901 [0.7, 1.14] undetermined (n_eff < 50) | 0.966 [0.917, 1.02] negligible | 0.995 [0.985, 1.01] negligible |

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| full system minus | false trust realized [CI] | false trust characteristic [CI] | trusted LT [CI] |
|---|---|---|---|
| A2 + constant | 0.045 [0.0307, 0.0598] | 0.0382 [0.021, 0.0568] | 0.651 [0.623, 0.675] |
| A2 + h(F-hat) | 0.0138 [0.00225, 0.025] | 0.0085 [-0.0055, 0.023] | 0.09 [0.073, 0.107] |
| A4 + KM leaf | 0.0405 [0.025, 0.0568] | 0.0205 [0, 0.0415] | 0.371 [0.336, 0.405] |

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| horizon model (own characteristic target) | pinball / constant's | constant/model ratio [CI] reading | cov 0.1 / 0.5 / 0.9 | C |
|---|---|---|---|---|
| h_A2(F-hat) | 0.213 / 0.282 | 1.33 [1.25, 1.41] substantial | 0.122 / 0.488 / 0.867 | 0.683 |
| h_g(F-hat) | 0.188 / 0.251 | 1.33 [1.27, 1.41] substantial | 0.13 / 0.496 / 0.866 | - |

### E-H2a. Amplification mismatch m(H) (H_0 = 1 LT; both r.m.s. <= 0.5 sigma_x)

Medians by tercile of I (low / mid / high). Spearman(m, I) on the kept states [95%]. B and A columns from the A/D record (oracle).

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| horizon | kept | m | abs drift w* | corr C/sqrt(E_C E_P) | Spearman(m, I) | B RI / OI | A drop-I (MSE) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 864 | -0.16 / 0.13 / 0.11 | 0.043 / 0.049 / 0.07 | 0.083 / 0.13 / 0.13 | 0.0932 [0.0196, 0.164] | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=15 (0.50 LT) | 852 | -0.1 / 0.14 / 0.11 | 0.036 / 0.046 / 0.071 | 0.087 / 0.13 / 0.14 | 0.0744 [0.00993, 0.144] | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=30 (1.00 LT) | 877 | 0 / 0 / 0 | 0 / 0 / 0 | 0.11 / 0.15 / 0.18 | (H_0) | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=60 (2.00 LT) | 669 | -0.25 / 0.16 / -0.04 | 0.06 / 0.089 / 0.065 | 0.12 / 0.19 / 0.19 | 0.0794 [-0.000604, 0.147] | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=120 (4.00 LT) | 156 | -1.2 / -1.8 / -2.5 | 0.28 / 0.4 / 0.42 | 0.29 / 0.31 / 0.27 | -0.164 [-0.315, -0.0191] | no interaction gain detected / no interaction gain detected | negligible |

**Reading: not determined** (horizons_used: ['60', '120'], horizons_supporting: [], horizons_null: []).

### E-H2e. Library size and error correlation (sweep states)

1000 sweep states. Delta = value at N_lib 100000 minus 1000. corr = the H2e correlation (0 by convention where an error is constant over the draws).

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| rho | valid | corr 0 small / large lib | median corr small -> large | set | median Delta corr [CI] | Spearman(Delta corr, Delta R) [CI] | reading |
|---|---|---|---|---|---|---|---|
| 0.01 | 1000 | 702 / 14 | 0 -> 0.44 | all (1000) | 0.386 [0.361, 0.409] | 0.161 [0.1, 0.211] | not consistent |
| 0.01 | 1000 | 702 / 14 | 0 -> 0.44 | both_defined (295) | 0.212 [0.17, 0.285] | 0.0138 [-0.0959, 0.121] | not determined |
| 0.02 | 1000 | 472 / 2 | 0 -> 0.452 | all (1000) | 0.333 [0.313, 0.348] | 0.111 [0.0496, 0.165] | not consistent |
| 0.02 | 1000 | 472 / 2 | 0 -> 0.452 | both_defined (527) | 0.243 [0.202, 0.285] | -0.00466 [-0.0865, 0.0695] | not determined |

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| rho | stratifier | median Delta corr low / mid / high | median Delta R low / mid / high |
|---|---|---|---|
| 0.01 | R | 0.36 / 0.39 / 0.4 | -1.6 / -1.6 / -1.8 |
| 0.01 | O | 0.37 / 0.41 / 0.37 | -1.7 / -1.6 / -1.7 |
| 0.01 | I | 0.36 / 0.4 / 0.4 | -1.7 / -1.7 / -1.6 |
| 0.01 | N | 0.34 / 0.42 / 0.39 | -1.9 / -1.4 / -1.7 |
| 0.01 | delta_R | 0.33 / 0.36 / 0.44 | -2.6 / -1.7 / -0.67 |
| 0.02 | R | 0.32 / 0.33 / 0.35 | -1.1 / -1.1 / -1.3 |
| 0.02 | O | 0.32 / 0.35 / 0.3 | -1.1 / -1.1 / -1.2 |
| 0.02 | I | 0.32 / 0.33 / 0.35 | -1.2 / -1.2 / -1.1 |
| 0.02 | N | 0.29 / 0.35 / 0.36 | -1.3 / -0.96 / -1.2 |
| 0.02 | delta_R | 0.29 / 0.33 / 0.37 | -1.9 / -1.1 / -0.26 |

**Reading** (final, after the convention check): rho 0.01: not determined (depends on the zero-variance convention); rho 0.02: not determined (depends on the zero-variance convention).

### E-H3c. A5 against A4

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| item | value |
|---|---|
| H3c ratio MSE(A5)/MSE(A4) [CI at level 0.983] (run) | 0.998 [0.812, 1.24], width 0.427 |
| top-1% share: A5 loss / A4 loss / abs(A5 - A4) | 0.468 / 0.508 / 0.585 |
| autocorrelation of d = A5 - A4, lags 1..5 | 0.0039, 0.00022, -6.1e-06, -0.0092, 0.0047 |
| block-5 means: lag-1 autocorrelation, variance ratio | 0.006, 1 |
| K chosen; leaves used test / calibration; largest leaf share test | 8; 8 / 8; 0.285 |
| w*(H_ref) within-leaf share of variance | 0.907 |
| bimodality coefficient R/O/I/N, oracle; deployable | 0.3/0.78/0.53/0.83; 0.35/0.4/0.52/0.89 |
| Spearman pairs (oracle) | RO 0.5, RI -0.081, RN 0.32, OI -0.054, ON -0.053, IN 0.12 |
| top-1% abs(d) states: mean percentile R/O/I/N | 0.68/0.77/0.26/0.34 |
| top-1% abs(d) states: median I pct; share high-I; median abs(x) pct; share sign change in window; share of sum d | 0.215; 0; 0.153; 0.5; -15.5 |

## rossler

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| check | result |
|---|---|
| A2 rebuilt on 1..H_max equals the dumped A2 (bitwise); A4 horizon-free | True, True |
| refit reproduces WU-0048 (max abs: A/ROIN MSE oracle, deployable; W/ROIN L_w oracle, deployable) | 0 / 0 / 0 / 0 |
| T_c counts T = 1 / e_(T-1) = theta (A2 train, g train, A2 test, g test, A4 calibration) | 0/0, 0/0, 0/0, 0/0, 0/0 |
| A2 on 1..H_max: pooled curvature floor / columns at 0 or 1 | 0 / 0 |
| weights clipped to [0, 1] | g_oracle_test 845, g_oracle_train_oof 2777, gw_oracle_test 537, gw_oracle_train_oof 1465, g_deployable_test 2626, g_deployable_train_oof 7754, gw_deployable_test 264, gw_deployable_train_oof 857 |

### C1. Separate performance (from the A/D record, no refit)

Allocation: MSE per rule (oracle: moment form; deployable: realized); reading of the rung against F (MSE ratio, 1.05 table, n_eff guard). G(F) = 1 - L_A(F)/L_A(constant).

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| horizon | profile | constant | separation | RO | F (ROIN) | X | X+F | G(F) | sep vs F | RO vs F | X+F vs F |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 0.000131 | 0.000129 | 0.000122 | 0.000121 | 0.000131 | 0.000121 | 0.456 | needed, size not determined | small | negligible |
| H=8 (0.27 LT) | deployable | 0.000136 | 0.000149 | 0.000136 | 0.000136 | 0.000135 | 0.000134 | 0.0139 | substantial | negligible | lowers |
| H=15 (0.50 LT) | oracle | 0.000227 | 0.000218 | 0.000207 | 0.000206 | 0.000226 | 0.000206 | 0.519 | needed, size not determined | small | negligible |
| H=15 (0.50 LT) | deployable | 0.000237 | 0.000256 | 0.000235 | 0.000234 | 0.000236 | 0.000232 | 0.0742 | substantial | negligible | negligible |
| H=30 (1.00 LT) | oracle | 0.000836 | 0.000753 | 0.000728 | 0.000723 | 0.000836 | 0.000727 | 0.688 | needed, size not determined | negligible | negligible |
| H=30 (1.00 LT) | deployable | 0.000836 | 0.000875 | 0.000811 | 0.000811 | 0.000834 | 0.000807 | 0.152 | needed, size not determined | negligible | negligible |
| H=60 (2.00 LT) | oracle | 0.0136 | 0.0124 | 0.0124 | 0.0124 | 0.0137 | 0.0124 | 0.312 | negligible | negligible | negligible |
| H=60 (2.00 LT) | deployable | 0.0146 | 0.0149 | 0.0147 | 0.0146 | 0.0149 | 0.0147 | -0.00176 | undetermined | negligible | negligible |
| H=120 (4.00 LT) | oracle | 0.116 | 0.117 | 0.114 | 0.113 | 0.115 | 0.113 | 0.0715 | needed, size not determined | negligible | negligible |
| H=120 (4.00 LT) | deployable | 0.115 | 0.122 | 0.114 | 0.114 | 0.114 | 0.113 | 0.0368 | needed, size not determined | negligible | negligible |

Horizon (Y = ln min(T_c, H_max)): pinball at 0.5 / Harrell's C / coverage of q_0.1 below the cap; reading against F.

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| profile | rung | pinball | C | cov q_0.1 | reading vs F |
|---|---|---|---|---|---|
| oracle | none | 0.162 | 0.5 | 0.104 | substantial |
| oracle | lyapunov | 0.163 | 0.641 | 0.0796 | substantial |
| oracle | RO | 0.15 | 0.586 | 0.113 | substantial |
| oracle | ROIN | 0.122 | 0.683 | 0.115 |  |
| oracle | X | 0.119 | 0.712 | 0.152 | undetermined |
| oracle | X+F | 0.0963 | 0.759 | 0.144 | lowers |
| oracle | Lyapunov rank | | 0.638 | | |
| deployable | none | 0.162 | 0.5 | 0.104 | substantial |
| deployable | lyapunov | 0.165 | 0.635 | 0.0748 | substantial |
| deployable | RO | 0.142 | 0.617 | 0.11 | substantial |
| deployable | ROIN | 0.118 | 0.693 | 0.113 |  |
| deployable | X | 0.121 | 0.704 | 0.145 | undetermined |
| deployable | X+F | 0.0926 | 0.766 | 0.141 | lowers |
| deployable | Lyapunov rank | | 0.633 | | |

### C2. Shared information (oracle and deployable profiles)

Skill retained = [L(constant) - L(bottleneck)] / [L(constant) - L(F)]; reading: keeps most (CI > 0.5), loses most (CI < 0.5), else not determined. Forward: horizon from g (five clipped weights; g_w: the L_w fits); reverse: weight from h (three quantiles), scored by L_A (MSE; deployable: realized per draw, R2 guard) and by L_w (weight units, unit-weight fits). Training inputs cross-fitted.

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| profile | direction | horizon | full skill [CI] | retained L_A / pinball [CI] | reading | retained L_w [CI] | reading L_w |
|---|---|---|---|---|---|---|---|
| oracle | forward (g; g_w) | all five | 0.0407 [0.0339, 0.0472] | 0.581 [0.49, 0.675] | not determined (interval spans 0.5) | 0.682 [0.583, 0.784] | keeps most |
| oracle | forward, one weight | H=8 (0.27 LT) | | 0.0525 [-0.00982, 0.113] | loses most | | |
| oracle | forward, one weight | H=15 (0.50 LT) | | 0.0329 [-0.0156, 0.0853] | loses most | | |
| oracle | forward, one weight | H=30 (1.00 LT) | | 0.027 [-0.0212, 0.0821] | loses most | | |
| oracle | forward, one weight | H=60 (2.00 LT) | | 0.042 [-0.038, 0.122] | loses most | | |
| oracle | forward, one weight | H=120 (4.00 LT) | | 0.531 [0.437, 0.626] | not determined (interval spans 0.5) | | |
| oracle | reverse | H=8 (0.27 LT) | 1.01e-05 [8.22e-06, 1.21e-05] | 0.154 [0.118, 0.197] | loses most | 0.307 [0.223, 0.399] | loses most |
| oracle | reverse | H=15 (0.50 LT) | 2.06e-05 [1.59e-05, 2.67e-05] | 0.265 [0.172, 0.356] | loses most | 0.399 [0.309, 0.502] | not determined (interval spans 0.5) |
| oracle | reverse | H=30 (1.00 LT) | 0.000114 [8.64e-05, 0.000144] | 0.0971 [0.0498, 0.155] | loses most | 0.312 [0.232, 0.393] | loses most |
| oracle | reverse | H=60 (2.00 LT) | 0.00119 [0.000721, 0.0017] | 0.0762 [-0.364, 0.322] | loses most | 0.31 [0.211, 0.416] | loses most |
| oracle | reverse | H=120 (4.00 LT) | 0.00236 [0.00104, 0.00371] | 0.424 [0.11, 0.814] | not determined (interval spans 0.5) | 0.449 [0.223, 0.909] | not determined (interval spans 0.5) |
| deployable | forward (g; g_w) | all five | 0.0447 [0.0381, 0.0512] | 0.552 [0.472, 0.638] | not determined (interval spans 0.5) | 0.645 [0.556, 0.723] | keeps most |
| deployable | forward, one weight | H=8 (0.27 LT) | | 0.0572 [0.016, 0.0992] | loses most | | |
| deployable | forward, one weight | H=15 (0.50 LT) | | 0.0238 [-0.0127, 0.0624] | loses most | | |
| deployable | forward, one weight | H=30 (1.00 LT) | | 0.0785 [0.0357, 0.126] | loses most | | |
| deployable | forward, one weight | H=60 (2.00 LT) | | 0.149 [0.102, 0.203] | loses most | | |
| deployable | forward, one weight | H=120 (4.00 LT) | | 0.541 [0.459, 0.627] | not determined (interval spans 0.5) | | |
| deployable | reverse | H=8 (0.27 LT) | 3.76e-07 [-1.68e-06, 2.25e-06] | -0.603 [-, -] | not determined (full-profile skill not established) | 0.0746 [0.0175, 0.138] | loses most |
| deployable | reverse | H=15 (0.50 LT) | 3.73e-06 [1.59e-07, 7.45e-06] | 0.0722 [-0.883, 3.65] | not determined (interval spans 0.5) | 0.119 [0.0476, 0.203] | loses most |
| deployable | reverse | H=30 (1.00 LT) | 2.51e-05 [3.79e-06, 4.75e-05] | -0.0722 [-0.973, 0.9] | not determined (interval spans 0.5) | 0.0761 [0.00618, 0.138] | loses most |
| deployable | reverse | H=60 (2.00 LT) | -8.5e-06 [-0.000288, 0.000247] | - [-, -] | not determined (full-profile skill not established) | 0.184 [0.0202, 0.332] | loses most |
| deployable | reverse | H=120 (4.00 LT) | 0.00119 [8.5e-05, 0.00239] | 1.1 [0.403, 9.24] | not determined (interval spans 0.5) | 0.812 [0.438, 1.57] | not determined (interval spans 0.5) |

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| profile | forward C-index F / g / g_w | reverse MSE(h)/MSE(F) per horizon | math-spec prediction (both lose most) | largest single-weight retention at H |
|---|---|---|---|---|
| oracle | 0.683 / 0.63 / 0.639 | H=8 (0.27 LT) 1.07 [1.06, 1.09] substantial; H=15 (0.50 LT) 1.07 [1.05, 1.1] substantial; H=30 (1.00 LT) 1.14 [1.11, 1.18] substantial; H=60 (2.00 LT) 1.09 [1.06, 1.12] substantial; H=120 (4.00 LT) 1.01 [1, 1.02] small | **not determined** | 120 |
| deployable | 0.693 / 0.615 / 0.648 | H=8 (0.27 LT) 1 [0.99, 1.02] negligible; H=15 (0.50 LT) 1.01 [0.999, 1.03] negligible; H=30 (1.00 LT) 1.03 [1, 1.06] needed, size not determined; H=60 (2.00 LT) 0.995 [0.973, 1.02] negligible; H=120 (4.00 LT) 0.999 [0.991, 1.01] negligible | **not determined** | 120 |

Oracle against deployable: retained (deployable) minus retained (oracle), paired 95% interval.

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| row | oracle | deployable | difference [CI] | reading |
|---|---|---|---|---|
| forward | 0.581 | 0.552 | -0.0293 [-0.111, 0.0504] | no difference detected |
| forward_w | 0.682 | 0.645 | -0.037 [-0.16, 0.0673] | no difference detected |
| reverse/8 | 0.154 | -0.603 | -0.757 [-, -] | not determined (full-profile skill not established) |
| reverse_w/8 | 0.307 | 0.0746 | -0.233 [-0.327, -0.144] | deployable retains less |
| reverse/15 | 0.265 | 0.0722 | -0.193 [-1.11, 3.37] | no difference detected |
| reverse_w/15 | 0.399 | 0.119 | -0.281 [-0.388, -0.174] | deployable retains less |
| reverse/30 | 0.0971 | -0.0722 | -0.169 [-1.05, 0.825] | no difference detected |
| reverse_w/30 | 0.312 | 0.0761 | -0.236 [-0.316, -0.161] | deployable retains less |
| reverse/60 | 0.0762 | - | - [-, -] | not determined (full-profile skill not established) |
| reverse_w/60 | 0.31 | 0.184 | -0.127 [-0.301, 0.0311] | no difference detected |
| reverse/120 | 0.424 | 1.1 | 0.676 [-0.0488, 9.26] | no difference detected |
| reverse_w/120 | 0.449 | 0.812 | 0.364 [-0.101, 1.02] | no difference detected |

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| horizon | Spearman(phi allocation, phi horizon) (4 items, descriptive) | phi_alloc R/O/I/N | phi_horizon R/O/I/N |
|---|---|---|---|
| H=8 (0.27 LT) | -0.8 | 6.3e-06/7.5e-07/-3.2e-08/3.1e-06 | 0.0029/0.01/0.026/0.0019 |
| H=15 (0.50 LT) | -0.8 | 1.4e-05/1.6e-06/1.5e-07/4.9e-06 | 0.0029/0.01/0.026/0.0019 |
| H=30 (1.00 LT) | -0.8 | 7.5e-05/1.2e-05/1.8e-06/2.6e-05 | 0.0029/0.01/0.026/0.0019 |
| H=60 (2.00 LT) | -0.8 | 0.00097/1.9e-05/1.3e-05/0.0002 | 0.0029/0.01/0.026/0.0019 |
| H=120 (4.00 LT) | 0.4 | 0.0013/0.00027/0.0006/0.00022 | 0.0029/0.01/0.026/0.0019 |

### C3. The deployable chain

False trust = P(T <= q_0.1) per (state, draw), target 0.1; T realized (the run's first passage against the noisy truth) or characteristic (moments). Trusted horizon = mean q_0.1 (LT). A4 + KM leaf uses the calibration A4 hybrid's characteristic horizon (no per-draw calibration errors on the full grid).

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| policy | false trust realized [CI] | false trust characteristic [CI] | mean trusted (LT) [CI] | q at cap |
|---|---|---|---|---|
| A2 + constant | 0.0983 [0.0867, 0.11] | 0.106 [0.087, 0.126] | 1.87 [1.87, 1.87] | 0 |
| A2 + h(F-hat) | 0.136 [0.122, 0.15] | 0.122 [0.102, 0.141] | 2.2 [2.16, 2.23] | 0 |
| A4 + KM leaf | 0.123 [0.111, 0.136] | 0.122 [0.105, 0.142] | 2.1 [2.07, 2.14] | 0 |
| g(F-hat) + h(F-hat) | 0.141 [0.128, 0.156] | 0.129 [0.108, 0.146] | 2.24 [2.2, 2.28] | 0 |

Hybrid MSE ratio to A2 (realized per draw; 1.05 table, R2 guard).

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| policy | H=8 (0.27 LT) | H=15 (0.50 LT) | H=30 (1.00 LT) | H=60 (2.00 LT) | H=120 (4.00 LT) |
|---|---|---|---|---|---|
| A4 + KM leaf | 1.1 [1.06, 1.13] substantial | 1.08 [1.05, 1.11] needed, size not determined | 1.05 [1.01, 1.09] needed, size not determined | 1.02 [0.992, 1.05] undetermined | 1.06 [1.04, 1.09] needed, size not determined |
| g(F-hat) + h(F-hat) | 0.997 [0.983, 1.01] negligible | 0.984 [0.969, 0.999] lowers | 0.97 [0.944, 0.995] lowers | 1 [0.982, 1.02] negligible | 0.99 [0.98, 1] lowers |

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| full system minus | false trust realized [CI] | false trust characteristic [CI] | trusted LT [CI] |
|---|---|---|---|
| A2 + constant | 0.0432 [0.0325, 0.0548] | 0.0225 [0.001, 0.0418] | 0.375 [0.336, 0.412] |
| A2 + h(F-hat) | 0.006 [-0.00025, 0.0127] | 0.0065 [-0.0045, 0.0173] | 0.0453 [0.038, 0.0527] |
| A4 + KM leaf | 0.0185 [0.008, 0.0302] | 0.006 [-0.014, 0.0248] | 0.137 [0.113, 0.159] |

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| horizon model (own characteristic target) | pinball / constant's | constant/model ratio [CI] reading | cov 0.1 / 0.5 / 0.9 | C |
|---|---|---|---|---|
| h_A2(F-hat) | 0.103 / 0.151 | 1.46 [1.38, 1.54] substantial | 0.122 / 0.499 / 0.872 | 0.713 |
| h_g(F-hat) | 0.103 / 0.155 | 1.5 [1.42, 1.59] substantial | 0.129 / 0.509 / 0.872 | - |

### E-H2a. Amplification mismatch m(H) (H_0 = 1 LT; both r.m.s. <= 0.5 sigma_x)

Medians by tercile of I (low / mid / high). Spearman(m, I) on the kept states [95%]. B and A columns from the A/D record (oracle).

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| horizon | kept | m | abs drift w* | corr C/sqrt(E_C E_P) | Spearman(m, I) | B RI / OI | A drop-I (MSE) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 999 | -0.079 / 0.19 / 0.081 | 0.074 / 0.11 / 0.069 | 0.2 / 0.19 / 0.23 | 0.0901 [0.0248, 0.152] | no interaction gain detected / no interaction gain detected | negligible |
| H=15 (0.50 LT) | 999 | -0.013 / 0.028 / -0.0079 | 0.07 / 0.087 / 0.038 | 0.18 / 0.18 / 0.24 | 0.0151 [-0.0471, 0.0737] | no interaction gain detected / no interaction gain detected | negligible |
| H=30 (1.00 LT) | 999 | 0 / 0 / 0 | 0 / 0 / 0 | 0.22 / 0.21 / 0.24 | (H_0) | no interaction gain detected / no interaction gain detected | negligible |
| H=60 (2.00 LT) | 923 | -0.23 / -0.18 / -0.19 | 0.1 / 0.1 / 0.087 | 0.22 / 0.25 / 0.29 | 0.019 [-0.0475, 0.0858] | no interaction gain detected / no interaction gain detected | negligible |
| H=120 (4.00 LT) | 670 | -1.2 / -1.4 / -1.4 | 0.22 / 0.36 / 0.3 | 0.28 / 0.44 / 0.34 | -0.0272 [-0.108, 0.0454] | no interaction gain detected / no interaction gain detected | negligible |

**Reading: not determined** (horizons_used: ['60', '120'], horizons_supporting: [], horizons_null: ['60']).

### E-H2e. Library size and error correlation (sweep states)

1000 sweep states. Delta = value at N_lib 100000 minus 1000. corr = the H2e correlation (0 by convention where an error is constant over the draws).

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| rho | valid | corr 0 small / large lib | median corr small -> large | set | median Delta corr [CI] | Spearman(Delta corr, Delta R) [CI] | reading |
|---|---|---|---|---|---|---|---|
| 0.01 | 1000 | 615 / 1 | 0 -> 0.461 | all (1000) | 0.387 [0.366, 0.399] | 0.09 [0.0245, 0.152] | not consistent |
| 0.01 | 1000 | 615 / 1 | 0 -> 0.461 | both_defined (384) | 0.191 [0.169, 0.22] | 0.0509 [-0.0537, 0.15] | not determined |
| 0.02 | 1000 | 308 / 0 | 0.0944 -> 0.467 | all (1000) | 0.295 [0.27, 0.317] | 0.169 [0.109, 0.231] | not consistent |
| 0.02 | 1000 | 308 / 0 | 0.0944 -> 0.467 | both_defined (692) | 0.191 [0.169, 0.214] | 0.146 [0.0769, 0.217] | not consistent |

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| rho | stratifier | median Delta corr low / mid / high | median Delta R low / mid / high |
|---|---|---|---|
| 0.01 | R | 0.35 / 0.38 / 0.41 | -1.4 / -1.4 / -1.4 |
| 0.01 | O | 0.37 / 0.38 / 0.4 | -1.5 / -1.4 / -1.4 |
| 0.01 | I | 0.35 / 0.4 / 0.41 | -1.4 / -1.4 / -1.4 |
| 0.01 | N | 0.39 / 0.39 / 0.38 | -1.5 / -1.4 / -1.4 |
| 0.01 | delta_R | 0.37 / 0.38 / 0.39 | -2.1 / -1.4 / -0.59 |
| 0.02 | R | 0.29 / 0.26 / 0.36 | -0.85 / -0.89 / -0.89 |
| 0.02 | O | 0.27 / 0.28 / 0.33 | -0.98 / -0.8 / -0.84 |
| 0.02 | I | 0.27 / 0.31 / 0.31 | -0.95 / -0.84 / -0.83 |
| 0.02 | N | 0.27 / 0.3 / 0.31 | -0.96 / -0.88 / -0.81 |
| 0.02 | delta_R | 0.19 / 0.34 / 0.34 | -1.4 / -0.88 / -0.15 |

**Reading** (final, after the convention check): rho 0.01: not determined (depends on the zero-variance convention); rho 0.02: not consistent.

### E-H3c. A5 against A4

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| item | value |
|---|---|
| H3c ratio MSE(A5)/MSE(A4) [CI at level 0.983] (run) | 0.951 [0.908, 0.991], width 0.0823 |
| top-1% share: A5 loss / A4 loss / abs(A5 - A4) | 0.191 / 0.181 / 0.2 |
| autocorrelation of d = A5 - A4, lags 1..5 | 0.013, -0.032, -0.071, 0.011, -0.0011 |
| block-5 means: lag-1 autocorrelation, variance ratio | 0.0249, 0.84 |
| K chosen; leaves used test / calibration; largest leaf share test | 3; 3 / 3; 0.505 |
| w*(H_ref) within-leaf share of variance | 0.918 |
| bimodality coefficient R/O/I/N, oracle; deployable | 0.33/0.78/0.48/0.8; 0.49/0.8/0.49/0.9 |
| Spearman pairs (oracle) | RO 0.35, RI -0.025, RN 0.47, OI -0.018, ON 0.029, IN -0.0024 |
| top-1% abs(d) states: mean percentile R/O/I/N | 0.79/0.9/0.7/0.57 |
| top-1% abs(d) states: median I pct; share high-I; median abs(x) pct; share sign change in window; share of sum d | 0.79; 0.6; 0.394; 1; 0.0869 |

## chua

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| check | result |
|---|---|
| A2 rebuilt on 1..H_max equals the dumped A2 (bitwise); A4 horizon-free | True, True |
| refit reproduces WU-0048 (max abs: A/ROIN MSE oracle, deployable; W/ROIN L_w oracle, deployable) | 0 / 0 / 0 / 0 |
| T_c counts T = 1 / e_(T-1) = theta (A2 train, g train, A2 test, g test, A4 calibration) | 0/0, 0/0, 1/0, 4/0, 0/0 |
| A2 on 1..H_max: pooled curvature floor / columns at 0 or 1 | 0 / 0 |
| weights clipped to [0, 1] | g_oracle_test 628, g_oracle_train_oof 2193, gw_oracle_test 538, gw_oracle_train_oof 1688, g_deployable_test 2398, g_deployable_train_oof 6830, gw_deployable_test 545, gw_deployable_train_oof 1300 |

### C1. Separate performance (from the A/D record, no refit)

Allocation: MSE per rule (oracle: moment form; deployable: realized); reading of the rung against F (MSE ratio, 1.05 table, n_eff guard). G(F) = 1 - L_A(F)/L_A(constant).

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| horizon | profile | constant | separation | RO | F (ROIN) | X | X+F | G(F) | sep vs F | RO vs F | X+F vs F |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 0.00071 | 0.000976 | 0.00069 | 0.000647 | 0.000715 | 0.000652 | 0.36 | undetermined | undetermined | undetermined |
| H=8 (0.27 LT) | deployable | 0.000546 | 0.000647 | 0.000556 | 0.000559 | 0.000549 | 0.000559 | -1.26 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | oracle | 0.00227 | 0.00221 | 0.00217 | 0.00213 | 0.00225 | 0.00252 | 0.216 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | deployable | 0.0021 | 0.00212 | 0.00208 | 0.00202 | 0.0021 | 0.002 | 0.18 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | oracle | 0.014 | 0.0115 | 0.0128 | 0.0126 | 0.0143 | 0.0129 | 0.247 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | deployable | 0.0143 | 0.0131 | 0.0134 | 0.013 | 0.0144 | 0.0135 | 0.209 | undetermined | undetermined | undetermined |
| H=60 (2.00 LT) | oracle | 0.169 | 0.162 | 0.159 | 0.159 | 0.164 | 0.159 | 0.166 | undetermined | negligible | negligible |
| H=60 (2.00 LT) | deployable | 0.172 | 0.17 | 0.165 | 0.161 | 0.165 | 0.161 | 0.18 | needed, size not determined | undetermined | negligible |
| H=120 (4.00 LT) | oracle | 0.618 | 0.623 | 0.601 | 0.598 | 0.616 | 0.599 | 0.111 | needed, size not determined | negligible | negligible |
| H=120 (4.00 LT) | deployable | 0.641 | 0.664 | 0.636 | 0.638 | 0.637 | 0.635 | 0.011 | undetermined | negligible | negligible |

Horizon (Y = ln min(T_c, H_max)): pinball at 0.5 / Harrell's C / coverage of q_0.1 below the cap; reading against F.

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| profile | rung | pinball | C | cov q_0.1 | reading vs F |
|---|---|---|---|---|---|
| oracle | none | 0.219 | 0.5 | 0.101 | substantial |
| oracle | lyapunov | 0.262 | 0.658 | 0.0683 | substantial |
| oracle | RO | 0.195 | 0.631 | 0.131 | substantial |
| oracle | ROIN | 0.159 | 0.721 | 0.121 |  |
| oracle | X | 0.173 | 0.689 | 0.166 | undetermined |
| oracle | X+F | 0.135 | 0.766 | 0.161 | lowers |
| oracle | Lyapunov rank | | 0.654 | | |
| deployable | none | 0.219 | 0.5 | 0.101 | substantial |
| deployable | lyapunov | 0.26 | 0.654 | 0.0717 | substantial |
| deployable | RO | 0.193 | 0.633 | 0.113 | substantial |
| deployable | ROIN | 0.156 | 0.727 | 0.128 |  |
| deployable | X | 0.176 | 0.677 | 0.157 | needed, size not determined |
| deployable | X+F | 0.137 | 0.76 | 0.162 | lowers |
| deployable | Lyapunov rank | | 0.657 | | |

### C2. Shared information (oracle and deployable profiles)

Skill retained = [L(constant) - L(bottleneck)] / [L(constant) - L(F)]; reading: keeps most (CI > 0.5), loses most (CI < 0.5), else not determined. Forward: horizon from g (five clipped weights; g_w: the L_w fits); reverse: weight from h (three quantiles), scored by L_A (MSE; deployable: realized per draw, R2 guard) and by L_w (weight units, unit-weight fits). Training inputs cross-fitted.

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| profile | direction | horizon | full skill [CI] | retained L_A / pinball [CI] | reading | retained L_w [CI] | reading L_w |
|---|---|---|---|---|---|---|---|
| oracle | forward (g; g_w) | all five | 0.0598 [0.0509, 0.0687] | 0.372 [0.286, 0.462] | loses most | 0.496 [0.409, 0.581] | not determined (interval spans 0.5) |
| oracle | forward, one weight | H=8 (0.27 LT) | | 0.00336 [-0.0234, 0.0287] | loses most | | |
| oracle | forward, one weight | H=15 (0.50 LT) | | 0.0124 [-0.0174, 0.0416] | loses most | | |
| oracle | forward, one weight | H=30 (1.00 LT) | | 0.00277 [-0.0272, 0.0319] | loses most | | |
| oracle | forward, one weight | H=60 (2.00 LT) | | 0.0785 [0.0282, 0.137] | loses most | | |
| oracle | forward, one weight | H=120 (4.00 LT) | | 0.0417 [0.00523, 0.0778] | loses most | | |
| oracle | reverse | H=8 (0.27 LT) | 6.3e-05 [2.02e-05, 0.00013] | 0.261 [-0.212, 0.425] | not determined (n_eff < 50) | 0.157 [0.0677, 0.245] | loses most |
| oracle | reverse | H=15 (0.50 LT) | 0.000137 [-1.23e-05, 0.000299] | 0.511 [-, -] | not determined (full-profile skill not established) | 0.168 [0.0809, 0.255] | loses most |
| oracle | reverse | H=30 (1.00 LT) | 0.00145 [-0.000285, 0.00344] | -0.0726 [-, -] | not determined (full-profile skill not established) | 0.208 [0.0976, 0.31] | loses most |
| oracle | reverse | H=60 (2.00 LT) | 0.00953 [0.000543, 0.0184] | 0.0296 [-5.4, 1.03] | not determined (interval spans 0.5) | 0.28 [0.133, 0.426] | loses most |
| oracle | reverse | H=120 (4.00 LT) | 0.0199 [0.0107, 0.0275] | 0.0818 [-0.141, 0.34] | loses most | 0.34 [0.14, 0.598] | not determined (interval spans 0.5) |
| deployable | forward (g; g_w) | all five | 0.0623 [0.0542, 0.0702] | 0.49 [0.416, 0.567] | not determined (interval spans 0.5) | 0.407 [0.319, 0.482] | loses most |
| deployable | forward, one weight | H=8 (0.27 LT) | | 0.073 [0.0419, 0.104] | loses most | | |
| deployable | forward, one weight | H=15 (0.50 LT) | | 0.0163 [0.000118, 0.0325] | loses most | | |
| deployable | forward, one weight | H=30 (1.00 LT) | | 0.0247 [-0.0103, 0.0574] | loses most | | |
| deployable | forward, one weight | H=60 (2.00 LT) | | 0.0721 [0.0266, 0.118] | loses most | | |
| deployable | forward, one weight | H=120 (4.00 LT) | | 0.123 [0.0564, 0.189] | loses most | | |
| deployable | reverse | H=8 (0.27 LT) | -1.34e-05 [-2.9e-05, -2.74e-07] | - [-, -] | not determined (full-profile skill not established) | 0.214 [0.0342, 0.364] | loses most |
| deployable | reverse | H=15 (0.50 LT) | 8.47e-05 [-9.53e-05, 0.000299] | -0.178 [-, -] | not determined (full-profile skill not established) | 0.22 [0.0737, 0.332] | loses most |
| deployable | reverse | H=30 (1.00 LT) | 0.00128 [0.000226, 0.00265] | 0.278 [-0.302, 1.01] | not determined (n_eff < 50) | 0.214 [-0.0114, 0.377] | loses most |
| deployable | reverse | H=60 (2.00 LT) | 0.0108 [0.00441, 0.0174] | 0.345 [0.121, 0.726] | not determined (interval spans 0.5) | 0.419 [0.205, 0.607] | not determined (interval spans 0.5) |
| deployable | reverse | H=120 (4.00 LT) | 0.00222 [-0.00603, 0.0104] | 1.23 [-, -] | not determined (full-profile skill not established) | 0.395 [-0.395, 1.03] | not determined (interval spans 0.5) |

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| profile | forward C-index F / g / g_w | reverse MSE(h)/MSE(F) per horizon | math-spec prediction (both lose most) | largest single-weight retention at H |
|---|---|---|---|---|
| oracle | 0.721 / 0.635 / 0.661 | H=8 (0.27 LT) 1.07 [1.04, 1.11] undetermined (n_eff < 50); H=15 (0.50 LT) 1.03 [0.982, 1.09] undetermined (n_eff < 50); H=30 (1.00 LT) 1.12 [0.986, 1.29] undetermined (n_eff < 50); H=60 (2.00 LT) 1.06 [1.01, 1.11] needed, size not determined; H=120 (4.00 LT) 1.03 [1.01, 1.04] small | **consistent** | 60 |
| deployable | 0.727 / 0.648 / 0.646 | H=8 (0.27 LT) 0.976 [0.947, 1] undetermined (n_eff < 50); H=15 (0.50 LT) 1.05 [0.969, 1.13] undetermined (n_eff < 50); H=30 (1.00 LT) 1.07 [1, 1.16] undetermined (n_eff < 50); H=60 (2.00 LT) 1.04 [1.01, 1.09] needed, size not determined; H=120 (4.00 LT) 0.999 [0.988, 1.01] negligible | **not determined** | 120 |

Oracle against deployable: retained (deployable) minus retained (oracle), paired 95% interval.

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| row | oracle | deployable | difference [CI] | reading |
|---|---|---|---|---|
| forward | 0.372 | 0.49 | 0.118 [0.0093, 0.221] | deployable retains more |
| forward_w | 0.496 | 0.407 | -0.0895 [-0.19, 0.00404] | no difference detected |
| reverse/8 | 0.261 | - | - [-, -] | not determined (n_eff < 50) |
| reverse_w/8 | 0.157 | 0.214 | 0.0569 [-0.132, 0.216] | no difference detected |
| reverse/15 | 0.511 | -0.178 | -0.69 [-, -] | not determined (full-profile skill not established) |
| reverse_w/15 | 0.168 | 0.22 | 0.0517 [-0.111, 0.183] | no difference detected |
| reverse/30 | -0.0726 | 0.278 | 0.351 [-, -] | not determined (full-profile skill not established) |
| reverse_w/30 | 0.208 | 0.214 | 0.0056 [-0.193, 0.166] | no difference detected |
| reverse/60 | 0.0296 | 0.345 | 0.315 [-0.581, 5.64] | no difference detected |
| reverse_w/60 | 0.28 | 0.419 | 0.139 [-0.0831, 0.332] | no difference detected |
| reverse/120 | 0.0818 | 1.23 | 1.15 [-, -] | not determined (full-profile skill not established) |
| reverse_w/120 | 0.34 | 0.395 | 0.0552 [-0.735, 0.684] | no difference detected |

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| horizon | Spearman(phi allocation, phi horizon) (4 items, descriptive) | phi_alloc R/O/I/N | phi_horizon R/O/I/N |
|---|---|---|---|
| H=8 (0.27 LT) | -0.2 | 1.6e-05/2e-05/9.1e-06/1.8e-05 | 0.0014/0.017/0.039/0.002 |
| H=15 (0.50 LT) | -0.8 | 7e-05/-2.2e-06/2.6e-05/4.4e-05 | 0.0014/0.017/0.039/0.002 |
| H=30 (1.00 LT) | -0.8 | 0.0013/-8.1e-05/3.6e-05/0.0002 | 0.0014/0.017/0.039/0.002 |
| H=60 (2.00 LT) | -0.4 | 0.0048/0.003/0.0016/0.00022 | 0.0014/0.017/0.039/0.002 |
| H=120 (4.00 LT) | -1 | 0.014/0.0018/0.00067/0.0033 | 0.0014/0.017/0.039/0.002 |

### C3. The deployable chain

False trust = P(T <= q_0.1) per (state, draw), target 0.1; T realized (the run's first passage against the noisy truth) or characteristic (moments). Trusted horizon = mean q_0.1 (LT). A4 + KM leaf uses the calibration A4 hybrid's characteristic horizon (no per-draw calibration errors on the full grid).

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| policy | false trust realized [CI] | false trust characteristic [CI] | mean trusted (LT) [CI] | q at cap |
|---|---|---|---|---|
| A2 + constant | 0.0665 [0.056, 0.0775] | 0.102 [0.084, 0.121] | 1.01 [1.01, 1.01] | 0 |
| A2 + h(F-hat) | 0.102 [0.0902, 0.115] | 0.139 [0.122, 0.159] | 1.46 [1.43, 1.49] | 0 |
| A4 + KM leaf | 0.068 [0.057, 0.0798] | 0.0943 [0.0777, 0.111] | 1.29 [1.27, 1.32] | 0 |
| g(F-hat) + h(F-hat) | 0.0948 [0.084, 0.107] | 0.127 [0.11, 0.143] | 1.51 [1.48, 1.55] | 0 |

Hybrid MSE ratio to A2 (realized per draw; 1.05 table, R2 guard).

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| policy | H=8 (0.27 LT) | H=15 (0.50 LT) | H=30 (1.00 LT) | H=60 (2.00 LT) | H=120 (4.00 LT) |
|---|---|---|---|---|---|
| A4 + KM leaf | 1.18 [1.09, 1.28] undetermined (n_eff < 50) | 1.01 [0.844, 1.22] undetermined (n_eff < 50) | 0.917 [0.834, 1] undetermined (n_eff < 50) | 0.99 [0.952, 1.03] negligible | 1.04 [1.01, 1.07] needed, size not determined |
| g(F-hat) + h(F-hat) | 1.02 [1, 1.05] undetermined (n_eff < 50) | 0.959 [0.88, 1.05] undetermined (n_eff < 50) | 0.908 [0.826, 0.982] undetermined (n_eff < 50) | 0.937 [0.899, 0.973] lowers | 0.996 [0.983, 1.01] negligible |

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| full system minus | false trust realized [CI] | false trust characteristic [CI] | trusted LT [CI] |
|---|---|---|---|
| A2 + constant | 0.0283 [0.014, 0.043] | 0.0245 [0.0025, 0.0465] | 0.506 [0.472, 0.54] |
| A2 + h(F-hat) | -0.00675 [-0.0143, 0.000506] | -0.0127 [-0.0232, -0.003] | 0.0561 [0.0489, 0.0635] |
| A4 + KM leaf | 0.0267 [0.0155, 0.0377] | 0.0323 [0.0175, 0.0478] | 0.219 [0.201, 0.238] |

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| horizon model (own characteristic target) | pinball / constant's | constant/model ratio [CI] reading | cov 0.1 / 0.5 / 0.9 | C |
|---|---|---|---|---|
| h_A2(F-hat) | 0.159 / 0.231 | 1.45 [1.38, 1.53] substantial | 0.139 / 0.498 / 0.874 | 0.726 |
| h_g(F-hat) | 0.156 / 0.226 | 1.44 [1.37, 1.52] substantial | 0.127 / 0.495 / 0.869 | - |

### E-H2a. Amplification mismatch m(H) (H_0 = 1 LT; both r.m.s. <= 0.5 sigma_x)

Medians by tercile of I (low / mid / high). Spearman(m, I) on the kept states [95%]. B and A columns from the A/D record (oracle).

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| horizon | kept | m | abs drift w* | corr C/sqrt(E_C E_P) | Spearman(m, I) | B RI / OI | A drop-I (MSE) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 933 | -0.0085 / 0.049 / 0.39 | 0.051 / 0.11 / 0.13 | 0.19 / 0.16 / 0.26 | 0.126 [0.0676, 0.195] | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=15 (0.50 LT) | 931 | -0.023 / -0.2 / 0.24 | 0.055 / 0.12 / 0.12 | 0.23 / 0.17 / 0.25 | 0.12 [0.0549, 0.187] | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=30 (1.00 LT) | 933 | 0 / 0 / 0 | 0 / 0 / 0 | 0.2 / 0.2 / 0.27 | (H_0) | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=60 (2.00 LT) | 679 | -0.27 / -0.99 / -0.17 | 0.075 / 0.19 / 0.14 | 0.26 / 0.2 / 0.25 | 0.0166 [-0.0529, 0.0959] | no interaction gain detected / no interaction gain detected | negligible |
| H=120 (4.00 LT) | 269 | -1.2 / -1.6 / -2 | 0.24 / 0.24 / 0.27 | 0.25 / 0.29 / 0.35 | 0.00606 [-0.103, 0.126] | no interaction gain detected / no interaction gain detected | negligible |

**Reading: not determined** (horizons_used: ['60', '120'], horizons_supporting: [], horizons_null: ['60']).

### E-H2e. Library size and error correlation (sweep states)

1000 sweep states. Delta = value at N_lib 100000 minus 1000. corr = the H2e correlation (0 by convention where an error is constant over the draws).

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| rho | valid | corr 0 small / large lib | median corr small -> large | set | median Delta corr [CI] | Spearman(Delta corr, Delta R) [CI] | reading |
|---|---|---|---|---|---|---|---|
| 0.01 | 1000 | 536 / 17 | 0 -> 0.422 | all (1000) | 0.322 [0.294, 0.348] | 0.0467 [-0.0135, 0.109] | not determined |
| 0.01 | 1000 | 536 / 17 | 0 -> 0.422 | both_defined (458) | 0.221 [0.179, 0.258] | 0.033 [-0.0578, 0.136] | not determined |
| 0.02 | 1000 | 243 / 3 | 0.0668 -> 0.398 | all (1000) | 0.232 [0.211, 0.255] | -0.0618 [-0.127, -0.000661] | consistent |
| 0.02 | 1000 | 243 / 3 | 0.0668 -> 0.398 | both_defined (756) | 0.17 [0.137, 0.202] | 0.0142 [-0.0613, 0.0859] | not determined |

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| rho | stratifier | median Delta corr low / mid / high | median Delta R low / mid / high |
|---|---|---|---|
| 0.01 | R | 0.31 / 0.31 / 0.37 | -1.2 / -1 / -1.6 |
| 0.01 | O | 0.36 / 0.33 / 0.27 | -1.7 / -1.2 / -1 |
| 0.01 | I | 0.3 / 0.29 / 0.37 | -1.3 / -1.3 / -1.2 |
| 0.01 | N | 0.32 / 0.32 / 0.32 | -1.6 / -0.92 / -1.3 |
| 0.01 | delta_R | 0.32 / 0.28 / 0.36 | -2.3 / -1.3 / -0.36 |
| 0.02 | R | 0.21 / 0.22 / 0.29 | -0.65 / -0.58 / -1.1 |
| 0.02 | O | 0.32 / 0.21 / 0.18 | -1.2 / -0.68 / -0.56 |
| 0.02 | I | 0.24 / 0.2 / 0.28 | -0.77 / -0.7 / -0.75 |
| 0.02 | N | 0.26 / 0.23 / 0.23 | -1 / -0.49 / -0.79 |
| 0.02 | delta_R | 0.32 / 0.14 / 0.24 | -1.7 / -0.74 / -0.081 |

**Reading** (final, after the convention check): rho 0.01: not determined; rho 0.02: not determined (depends on the zero-variance convention).

### E-H3c. A5 against A4

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| item | value |
|---|---|
| H3c ratio MSE(A5)/MSE(A4) [CI at level 0.983] (run) | 1.02 [0.951, 1.09], width 0.138 |
| top-1% share: A5 loss / A4 loss / abs(A5 - A4) | 0.582 / 0.55 / 0.458 |
| autocorrelation of d = A5 - A4, lags 1..5 | -0.0019, -0.031, -0.00063, 0.0027, -0.0036 |
| block-5 means: lag-1 autocorrelation, variance ratio | 0.0059, 0.946 |
| K chosen; leaves used test / calibration; largest leaf share test | 4; 4 / 4; 0.413 |
| w*(H_ref) within-leaf share of variance | 0.935 |
| bimodality coefficient R/O/I/N, oracle; deployable | 0.27/0.23/0.47/0.87; 0.36/0.45/0.48/0.9 |
| Spearman pairs (oracle) | RO 0.1, RI 0.074, RN 0.32, OI 0.3, ON 0.071, IN -0.0055 |
| top-1% abs(d) states: mean percentile R/O/I/N | 0.42/0.68/0.77/0.37 |
| top-1% abs(d) states: median I pct; share high-I; median abs(x) pct; share sign change in window; share of sum d | 0.89; 0.7; 0.484; 0; 0.876 |

## E-H3c reading (this seed)

DEVELOPMENT (DEV-4): exploratory, not a hypothesis test.

| item | value |
|---|---|
| H3c interval widths | lorenz63 0.427, rossler 0.0823, chua 0.138 |
| pattern (Lorenz-63 widest, Rössler narrowest) reproduced | True |
| Lorenz-63 part (top-1% share of sum abs(d) 0.585, median I percentile 0.215) | not consistent |
| Rössler part (BC deployable: R 0.486, O 0.798, I 0.485, N 0.902) | not consistent |
| **reading** | **not consistent** |

