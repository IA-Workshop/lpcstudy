# Phase J experiments C and E: DEV-3

**DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.** Run `/home/brianm/projects/physics/chaos/lpcstudy-wt/run/phj-f701a47/runs/dev/phj-DEV-3/full`; analysis commit `199e43a32db3ace33c88a0e8f2ad8ce2b405cc4d` (dirty: False); A/D record `/home/brianm/projects/physics/chaos/lpcstudy-wt/run/phj-f701a47/runs/dev/phj-DEV-3/contrib-ea0bd77/contrib.json`. Estimates with 95% intervals from the shared moving-block index sets (models fixed; training variance not included). Readings are descriptive; no causal claim; nothing here is set beside CONF-1.

## lorenz63

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| check | result |
|---|---|
| A2 rebuilt on 1..H_max equals the dumped A2 (bitwise); A4 horizon-free | True, True |
| g refit reproduces WU-0048 A/ROIN MSE (max abs, oracle / deployable) | 0 / 0 |
| T_c counts T = 1 / e_(T-1) = theta (A2 train, g train, A2 test, g test, A4 calibration) | 20/0, 91/0, 6/0, 30/0, 119/0 |
| A2 on 1..H_max: pooled curvature floor / columns at 0 or 1 | 0 / 0 |
| weights clipped to [0, 1] (g oracle test / train OOF, g deployable test / train OOF) | 737, 1746, 1206, 4225 |

### C1. Separate performance (from the A/D record, no refit)

Allocation: MSE per rule (oracle: moment form; deployable: realized); reading of the rung against F (MSE ratio, 1.05 table, n_eff guard). G(F) = 1 - L_A(F)/L_A(constant).

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| horizon | profile | constant | separation | RO | F (ROIN) | X | X+F | G(F) | sep vs F | RO vs F | X+F vs F |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 0.0104 | 0.00121 | 0.00148 | 0.00136 | 0.00173 | 0.00152 | 0.942 | undetermined | undetermined | undetermined |
| H=8 (0.27 LT) | deployable | 0.00972 | 0.0223 | 0.00814 | 0.00514 | 0.0017 | 0.00186 | 0.514 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | oracle | 0.025 | 0.0119 | 0.0114 | 0.0115 | 0.0124 | 0.011 | 0.803 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | deployable | 0.0271 | 0.0373 | 0.0201 | 0.0162 | 0.0129 | 0.0142 | 0.579 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | oracle | 0.0539 | 0.0313 | 0.0348 | 0.0353 | 0.0338 | 0.0336 | 0.608 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | deployable | 0.062 | 0.072 | 0.0461 | 0.0447 | 0.0379 | 0.0396 | 0.447 | undetermined | undetermined | undetermined |
| H=60 (2.00 LT) | oracle | 0.158 | 0.143 | 0.14 | 0.138 | 0.141 | 0.137 | 0.345 | undetermined | undetermined | undetermined |
| H=60 (2.00 LT) | deployable | 0.176 | 0.185 | 0.167 | 0.158 | 0.152 | 0.147 | 0.243 | needed, size not determined | needed, size not determined | negligible |
| H=120 (4.00 LT) | oracle | 0.94 | 1.02 | 0.937 | 0.937 | 0.933 | 0.937 | 0.0129 | needed, size not determined | negligible | negligible |
| H=120 (4.00 LT) | deployable | 0.979 | 1.05 | 0.976 | 0.976 | 0.969 | 0.966 | 0.00898 | needed, size not determined | negligible | negligible |

Horizon (Y = ln min(T_c, H_max)): pinball at 0.5 / Harrell's C / coverage of q_0.1 below the cap; reading against F.

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| profile | rung | pinball | C | cov q_0.1 | reading vs F |
|---|---|---|---|---|---|
| oracle | none | 0.188 | 0.5 | 0.101 | substantial |
| oracle | lyapunov | 0.304 | 0.601 | 0.0687 | substantial |
| oracle | RO | 0.186 | 0.571 | 0.107 | substantial |
| oracle | ROIN | 0.149 | 0.675 | 0.118 |  |
| oracle | X | 0.158 | 0.67 | 0.145 | undetermined |
| oracle | X+F | 0.128 | 0.731 | 0.144 | lowers |
| oracle | Lyapunov rank | | 0.595 | | |
| deployable | none | 0.188 | 0.5 | 0.101 | substantial |
| deployable | lyapunov | 0.303 | 0.601 | 0.0734 | substantial |
| deployable | RO | 0.183 | 0.582 | 0.101 | substantial |
| deployable | ROIN | 0.15 | 0.676 | 0.108 |  |
| deployable | X | 0.16 | 0.666 | 0.142 | undetermined |
| deployable | X+F | 0.133 | 0.714 | 0.147 | lowers |
| deployable | Lyapunov rank | | 0.598 | | |

### C2. Shared information (oracle profile)

Skill retained = [L(constant) - L(bottleneck)] / [L(constant) - L(F)]; reading: keeps most (CI > 0.5), loses most (CI < 0.5), else not determined. Forward: horizon from g(F) (five clipped weights); reverse: weight from h(F) (three quantiles). Training inputs cross-fitted.

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| direction | horizon | L(constant) | L(F) | L(bottleneck) | full skill [CI] | retained [CI] | reading |
|---|---|---|---|---|---|---|---|
| forward (pinball) | all five | 0.188 | 0.149 | 0.181 | 0.0398 [0.0307, 0.0495] | 0.179 [0.107, 0.258] | loses most |
| forward, one weight | H=8 (0.27 LT) | | | 0.188 | | 0.00426 [-0.017, 0.0254] | loses most |
| forward, one weight | H=15 (0.50 LT) | | | 0.188 | | -2.27e-05 [-0.0465, 0.039] | loses most |
| forward, one weight | H=30 (1.00 LT) | | | 0.188 | | 0.0168 [-0.0182, 0.0516] | loses most |
| forward, one weight | H=60 (2.00 LT) | | | 0.188 | | 0.00149 [-0.0367, 0.0427] | loses most |
| forward, one weight | H=120 (4.00 LT) | | | 0.183 | | 0.134 [0.0829, 0.19] | loses most |
| reverse (MSE) | H=8 (0.27 LT) | 0.0104 | 0.00136 | 0.00573 | 0.009 [0.00526, 0.0141] | 0.514 [0.076, 0.779] | not determined (n_eff < 50) |
| reverse (MSE) | H=15 (0.50 LT) | 0.025 | 0.0115 | 0.0181 | 0.0134 [0.00736, 0.0208] | 0.513 [0.173, 0.752] | not determined (n_eff < 50) |
| reverse (MSE) | H=30 (1.00 LT) | 0.0539 | 0.0353 | 0.0387 | 0.0186 [0.00597, 0.0304] | 0.815 [0.481, 2.06] | not determined (n_eff < 50) |
| reverse (MSE) | H=60 (2.00 LT) | 0.158 | 0.138 | 0.154 | 0.02 [0.00701, 0.033] | 0.184 [0.0343, 0.483] | not determined (n_eff < 50) |
| reverse (MSE) | H=120 (4.00 LT) | 0.94 | 0.937 | 0.939 | 0.00364 [-0.0028, 0.0101] | 0.323 [-, -] | not determined (full-profile skill not established) |

Forward C-index: F 0.675, g(F) 0.587. Reverse MSE(h(F))/MSE(F): H=8 (0.27 LT) 4.23 [2.35, 8.76] undetermined (n_eff < 50); H=15 (0.50 LT) 1.57 [1.2, 2.48] undetermined (n_eff < 50); H=30 (1.00 LT) 1.1 [0.82, 1.43] undetermined (n_eff < 50); H=60 (2.00 LT) 1.12 [1.03, 1.23] undetermined (n_eff < 50); H=120 (4.00 LT) 1 [0.995, 1.01] negligible.

Math-spec prediction (both bottlenecks lose most): **consistent**; largest single-weight forward retention at H = 120.

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| horizon | Spearman(phi allocation, phi horizon) (4 items, descriptive) | phi_alloc R/O/I/N | phi_horizon R/O/I/N |
|---|---|---|---|
| H=8 (0.27 LT) | 0.6 | 4.3e-05/0.0061/0.0024/0.0005 | 0.0032/0.011/0.024/0.0022 |
| H=15 (0.50 LT) | 0.6 | 0.0014/0.0085/0.002/0.0015 | 0.0032/0.011/0.024/0.0022 |
| H=30 (1.00 LT) | 0.6 | 0.0017/0.0099/0.0048/0.0022 | 0.0032/0.011/0.024/0.0022 |
| H=60 (2.00 LT) | 0.4 | 0.0039/0.013/0.0029/3.6e-05 | 0.0032/0.011/0.024/0.0022 |
| H=120 (4.00 LT) | 0.4 | 0.0014/0.0037/0.00069/-0.0022 | 0.0032/0.011/0.024/0.0022 |

### C3. The deployable chain

False trust = P(T <= q_0.1) per (state, draw), target 0.1; T realized (the run's first passage against the noisy truth) or characteristic (moments). Trusted horizon = mean q_0.1 (LT). A4 + KM leaf uses the calibration A4 hybrid's characteristic horizon (no per-draw calibration errors on the full grid).

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| policy | false trust realized [CI] | false trust characteristic [CI] | mean trusted (LT) [CI] | q at cap |
|---|---|---|---|---|
| A2 + constant | 0.0658 [0.0525, 0.0778] | 0.091 [0.076, 0.106] | 0.538 [0.538, 0.538] | 0 |
| A2 + h(F-hat) | 0.089 [0.076, 0.102] | 0.11 [0.0935, 0.127] | 0.991 [0.966, 1.02] | 0 |
| A4 + KM leaf | 0.0628 [0.052, 0.0722] | 0.087 [0.0717, 0.101] | 0.974 [0.95, 0.999] | 0 |
| g(F-hat) + h(F-hat) | 0.0902 [0.078, 0.101] | 0.112 [0.0968, 0.127] | 1.09 [1.06, 1.11] | 0 |

Hybrid MSE ratio to A2 (realized per draw; 1.05 table, R2 guard).

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| policy | H=8 (0.27 LT) | H=15 (0.50 LT) | H=30 (1.00 LT) | H=60 (2.00 LT) | H=120 (4.00 LT) |
|---|---|---|---|---|---|
| A4 + KM leaf | 2.28 [1.1, 3.74] undetermined (n_eff < 50) | 1.33 [1.18, 1.44] undetermined (n_eff < 50) | 1.16 [1.05, 1.26] undetermined (n_eff < 50) | 1.05 [1.01, 1.09] needed, size not determined | 1.07 [1.05, 1.1] needed, size not determined |
| g(F-hat) + h(F-hat) | 0.526 [0.376, 0.647] undetermined (n_eff < 50) | 0.577 [0.344, 0.906] undetermined (n_eff < 50) | 0.719 [0.531, 0.928] undetermined (n_eff < 50) | 0.894 [0.838, 0.953] lowers | 0.997 [0.989, 1] negligible |

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| full system minus | false trust realized [CI] | false trust characteristic [CI] | trusted LT [CI] |
|---|---|---|---|
| A2 + constant | 0.0245 [0.0112, 0.037] | 0.0213 [0.0045, 0.0375] | 0.549 [0.524, 0.576] |
| A2 + h(F-hat) | 0.00125 [-0.00926, 0.0123] | 0.00225 [-0.0108, 0.0148] | 0.0958 [0.0796, 0.112] |
| A4 + KM leaf | 0.0275 [0.0168, 0.0387] | 0.0253 [0.0103, 0.04] | 0.112 [0.0864, 0.138] |

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| horizon model (own characteristic target) | pinball / constant's | constant/model ratio [CI] reading | cov 0.1 / 0.5 / 0.9 | C |
|---|---|---|---|---|
| h_A2(F-hat) | 0.202 / 0.257 | 1.27 [1.21, 1.34] substantial | 0.11 / 0.494 / 0.854 | 0.673 |
| h_g(F-hat) | 0.183 / 0.233 | 1.28 [1.23, 1.33] substantial | 0.112 / 0.492 / 0.861 | - |

### E-H2a. Amplification mismatch m(H) (H_0 = 1 LT; both r.m.s. <= 0.5 sigma_x)

Medians by tercile of I (low / mid / high). Spearman(m, I) on the kept states [95%]. B and A columns from the A/D record (oracle).

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| horizon | kept | m | abs drift w* | corr C/sqrt(E_C E_P) | Spearman(m, I) | B RI / OI | A drop-I (MSE) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 876 | -0.25 / -0.0038 / 0.15 | 0.051 / 0.043 / 0.082 | 0.12 / 0.11 / 0.12 | 0.0979 [0.034, 0.165] | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=15 (0.50 LT) | 870 | -0.013 / 0.045 / -0.15 | 0.046 / 0.054 / 0.09 | 0.12 / 0.11 / 0.12 | 0.00444 [-0.0633, 0.0704] | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=30 (1.00 LT) | 882 | 0 / 0 / 0 | 0 / 0 / 0 | 0.13 / 0.12 / 0.15 | (H_0) | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=60 (2.00 LT) | 669 | -0.15 / -0.034 / -0.27 | 0.062 / 0.076 / 0.1 | 0.13 / 0.15 / 0.16 | 0.000719 [-0.0692, 0.0738] | no interaction gain detected / interaction gain detected | undetermined (n_eff < 50) |
| H=120 (4.00 LT) | 149 | -1.5 / -1.5 / -2.4 | 0.23 / 0.43 / 0.45 | 0.23 / 0.37 / 0.32 | -0.127 [-0.296, 0.0499] | interaction gain detected / interaction gain detected | negligible |

**Reading: not determined** (horizons_used: ['60', '120'], horizons_supporting: [], horizons_null: ['60']).

### E-H2e. Library size and error correlation (sweep states)

1000 sweep states. Delta = value at N_lib 100000 minus 1000. corr = the H2e correlation (0 by convention where an error is constant over the draws).

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| rho | valid | corr 0 small / large lib | median corr small -> large | set | median Delta corr [CI] | Spearman(Delta corr, Delta R) [CI] | reading |
|---|---|---|---|---|---|---|---|
| 0.01 | 1000 | 666 / 17 | 0 -> 0.429 | all (1000) | 0.367 [0.34, 0.394] | 0.0911 [0.0309, 0.153] | not consistent |
| 0.01 | 1000 | 666 / 17 | 0 -> 0.429 | both_defined (330) | 0.2 [0.146, 0.254] | -0.0711 [-0.178, 0.0418] | not determined |
| 0.02 | 1000 | 435 / 3 | 0 -> 0.439 | all (1000) | 0.306 [0.276, 0.323] | -0.0436 [-0.104, 0.0163] | not determined |
| 0.02 | 1000 | 435 / 3 | 0 -> 0.439 | both_defined (564) | 0.214 [0.178, 0.243] | -0.0956 [-0.176, -0.00687] | consistent |

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| rho | stratifier | median Delta corr low / mid / high | median Delta R low / mid / high |
|---|---|---|---|
| 0.01 | R | 0.38 / 0.37 / 0.34 | -1.6 / -1.7 / -1.7 |
| 0.01 | O | 0.35 / 0.4 / 0.34 | -1.7 / -1.7 / -1.6 |
| 0.01 | I | 0.35 / 0.38 / 0.37 | -1.8 / -1.6 / -1.6 |
| 0.01 | N | 0.33 / 0.43 / 0.35 | -1.8 / -1.6 / -1.6 |
| 0.01 | delta_R | 0.35 / 0.32 / 0.41 | -2.7 / -1.7 / -0.72 |
| 0.02 | R | 0.31 / 0.31 / 0.29 | -1.1 / -1.2 / -1.2 |
| 0.02 | O | 0.31 / 0.34 / 0.26 | -1.1 / -1.2 / -1.1 |
| 0.02 | I | 0.28 / 0.33 / 0.29 | -1.3 / -1.1 / -1.1 |
| 0.02 | N | 0.29 / 0.35 / 0.28 | -1.2 / -1.1 / -1.1 |
| 0.02 | delta_R | 0.35 / 0.25 / 0.32 | -2.1 / -1.2 / -0.26 |

**Reading** (final, after the convention check): rho 0.01: not determined (depends on the zero-variance convention); rho 0.02: not determined (depends on the zero-variance convention).

### E-H3c. A5 against A4

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| item | value |
|---|---|
| H3c ratio MSE(A5)/MSE(A4) [CI at level 0.983] (run) | 0.794 [0.589, 1.12], width 0.536 |
| top-1% share: A5 loss / A4 loss / abs(A5 - A4) | 0.511 / 0.639 / 0.597 |
| autocorrelation of d = A5 - A4, lags 1..5 | -0.0055, -0.0031, 0.0041, -0.0026, -0.00039 |
| block-5 means: lag-1 autocorrelation, variance ratio | 0.0191, 1 |
| K chosen; leaves used test / calibration; largest leaf share test | 8; 8 / 8; 0.233 |
| w*(H_ref) within-leaf share of variance | 0.899 |
| bimodality coefficient R/O/I/N, oracle; deployable | 0.27/0.78/0.53/0.82; 0.31/0.39/0.54/0.88 |
| Spearman pairs (oracle) | RO 0.43, RI -0.0029, RN 0.33, OI 0.013, ON -0.047, IN 0.048 |
| top-1% abs(d) states: mean percentile R/O/I/N | 0.85/0.86/0.3/0.63 |
| top-1% abs(d) states: median I pct; share high-I; median abs(x) pct; share sign change in window; share of sum d | 0.19; 0.2; 0.337; 0.7; 1.08 |

## rossler

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| check | result |
|---|---|
| A2 rebuilt on 1..H_max equals the dumped A2 (bitwise); A4 horizon-free | True, True |
| g refit reproduces WU-0048 A/ROIN MSE (max abs, oracle / deployable) | 0 / 0 |
| T_c counts T = 1 / e_(T-1) = theta (A2 train, g train, A2 test, g test, A4 calibration) | 0/0, 0/0, 0/0, 0/0, 0/0 |
| A2 on 1..H_max: pooled curvature floor / columns at 0 or 1 | 0 / 0 |
| weights clipped to [0, 1] (g oracle test / train OOF, g deployable test / train OOF) | 794, 2792, 2510, 7207 |

### C1. Separate performance (from the A/D record, no refit)

Allocation: MSE per rule (oracle: moment form; deployable: realized); reading of the rung against F (MSE ratio, 1.05 table, n_eff guard). G(F) = 1 - L_A(F)/L_A(constant).

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| horizon | profile | constant | separation | RO | F (ROIN) | X | X+F | G(F) | sep vs F | RO vs F | X+F vs F |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 0.000141 | 0.000119 | 0.000114 | 0.000114 | 0.000127 | 0.000113 | 0.67 | needed, size not determined | negligible | negligible |
| H=8 (0.27 LT) | deployable | 0.000117 | 0.000128 | 0.000118 | 0.000118 | 0.000116 | 0.000117 | -0.00793 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | oracle | 0.000257 | 0.000216 | 0.000208 | 0.000207 | 0.000235 | 0.000205 | 0.736 | needed, size not determined | negligible | negligible |
| H=15 (0.50 LT) | deployable | 0.000232 | 0.000253 | 0.000232 | 0.000232 | 0.00023 | 0.000231 | 0.000656 | substantial | negligible | negligible |
| H=30 (1.00 LT) | oracle | 0.000759 | 0.000671 | 0.000663 | 0.000661 | 0.000758 | 0.000659 | 0.627 | negligible | negligible | negligible |
| H=30 (1.00 LT) | deployable | 0.000773 | 0.00079 | 0.000752 | 0.000757 | 0.00077 | 0.000754 | 0.0935 | needed, size not determined | negligible | negligible |
| H=60 (2.00 LT) | oracle | 0.0144 | 0.0131 | 0.0134 | 0.0133 | 0.0144 | 0.0134 | 0.279 | negligible | negligible | negligible |
| H=60 (2.00 LT) | deployable | 0.0142 | 0.014 | 0.014 | 0.0138 | 0.0142 | 0.0138 | 0.09 | undetermined | negligible | negligible |
| H=120 (4.00 LT) | oracle | 0.111 | 0.114 | 0.11 | 0.109 | 0.111 | 0.108 | 0.0566 | needed, size not determined | negligible | negligible |
| H=120 (4.00 LT) | deployable | 0.111 | 0.115 | 0.111 | 0.11 | 0.112 | 0.11 | 0.0331 | needed, size not determined | negligible | negligible |

Horizon (Y = ln min(T_c, H_max)): pinball at 0.5 / Harrell's C / coverage of q_0.1 below the cap; reading against F.

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| profile | rung | pinball | C | cov q_0.1 | reading vs F |
|---|---|---|---|---|---|
| oracle | none | 0.164 | 0.5 | 0.115 | substantial |
| oracle | lyapunov | 0.167 | 0.647 | 0.0903 | substantial |
| oracle | RO | 0.156 | 0.556 | 0.125 | substantial |
| oracle | ROIN | 0.121 | 0.686 | 0.164 |  |
| oracle | X | 0.125 | 0.692 | 0.161 | undetermined |
| oracle | X+F | 0.093 | 0.771 | 0.175 | lowers |
| oracle | Lyapunov rank | | 0.646 | | |
| deployable | none | 0.164 | 0.5 | 0.115 | substantial |
| deployable | lyapunov | 0.169 | 0.64 | 0.0862 | substantial |
| deployable | RO | 0.149 | 0.592 | 0.143 | substantial |
| deployable | ROIN | 0.118 | 0.699 | 0.15 |  |
| deployable | X | 0.126 | 0.69 | 0.165 | undetermined |
| deployable | X+F | 0.0905 | 0.777 | 0.172 | lowers |
| deployable | Lyapunov rank | | 0.64 | | |

### C2. Shared information (oracle profile)

Skill retained = [L(constant) - L(bottleneck)] / [L(constant) - L(F)]; reading: keeps most (CI > 0.5), loses most (CI < 0.5), else not determined. Forward: horizon from g(F) (five clipped weights); reverse: weight from h(F) (three quantiles). Training inputs cross-fitted.

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| direction | horizon | L(constant) | L(F) | L(bottleneck) | full skill [CI] | retained [CI] | reading |
|---|---|---|---|---|---|---|---|
| forward (pinball) | all five | 0.164 | 0.121 | 0.143 | 0.043 [0.0358, 0.0501] | 0.483 [0.368, 0.586] | not determined (interval spans 0.5) |
| forward, one weight | H=8 (0.27 LT) | | | 0.162 | | 0.0539 [0.00326, 0.104] | loses most |
| forward, one weight | H=15 (0.50 LT) | | | 0.162 | | 0.0478 [-0.0121, 0.11] | loses most |
| forward, one weight | H=30 (1.00 LT) | | | 0.16 | | 0.103 [0.03, 0.175] | loses most |
| forward, one weight | H=60 (2.00 LT) | | | 0.161 | | 0.0707 [-0.0192, 0.162] | loses most |
| forward, one weight | H=120 (4.00 LT) | | | 0.147 | | 0.396 [0.293, 0.494] | loses most |
| reverse (MSE) | H=8 (0.27 LT) | 0.000141 | 0.000114 | 0.00014 | 2.76e-05 [9.36e-06, 5.49e-05] | 0.0572 [0.00163, 0.119] | loses most |
| reverse (MSE) | H=15 (0.50 LT) | 0.000257 | 0.000207 | 0.000254 | 5.08e-05 [2.01e-05, 9.86e-05] | 0.0718 [-0.024, 0.163] | loses most |
| reverse (MSE) | H=30 (1.00 LT) | 0.000759 | 0.000661 | 0.000747 | 9.81e-05 [7.67e-05, 0.000121] | 0.124 [0.0456, 0.198] | loses most |
| reverse (MSE) | H=60 (2.00 LT) | 0.0144 | 0.0133 | 0.0144 | 0.0011 [0.000666, 0.00147] | 0.00943 [-0.179, 0.136] | loses most |
| reverse (MSE) | H=120 (4.00 LT) | 0.111 | 0.109 | 0.111 | 0.00171 [4.87e-06, 0.00338] | -0.183 [-118, 2.49] | not determined (interval spans 0.5) |

Forward C-index: F 0.686, g(F) 0.607. Reverse MSE(h(F))/MSE(F): H=8 (0.27 LT) 1.23 [1.08, 1.47] substantial; H=15 (0.50 LT) 1.23 [1.09, 1.45] substantial; H=30 (1.00 LT) 1.13 [1.1, 1.16] substantial; H=60 (2.00 LT) 1.08 [1.05, 1.11] needed, size not determined; H=120 (4.00 LT) 1.02 [1, 1.03] small.

Math-spec prediction (both bottlenecks lose most): **not determined**; largest single-weight forward retention at H = 120.

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| horizon | Spearman(phi allocation, phi horizon) (4 items, descriptive) | phi_alloc R/O/I/N | phi_horizon R/O/I/N |
|---|---|---|---|
| H=8 (0.27 LT) | -0.8 | 1.7e-05/9.6e-06/-1.2e-06/2.1e-06 | 0.0015/0.0092/0.029/0.0033 |
| H=15 (0.50 LT) | -0.8 | 3.1e-05/1.2e-05/5e-07/7.1e-06 | 0.0015/0.0092/0.029/0.0033 |
| H=30 (1.00 LT) | -1 | 6.8e-05/1.4e-05/-3.3e-07/1.6e-05 | 0.0015/0.0092/0.029/0.0033 |
| H=60 (2.00 LT) | -1 | 0.00089/2.6e-05/-5.3e-05/0.00024 | 0.0015/0.0092/0.029/0.0033 |
| H=120 (4.00 LT) | -0.4 | 0.0012/-0.00025/0.00073/4.4e-05 | 0.0015/0.0092/0.029/0.0033 |

### C3. The deployable chain

False trust = P(T <= q_0.1) per (state, draw), target 0.1; T realized (the run's first passage against the noisy truth) or characteristic (moments). Trusted horizon = mean q_0.1 (LT). A4 + KM leaf uses the calibration A4 hybrid's characteristic horizon (no per-draw calibration errors on the full grid).

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| policy | false trust realized [CI] | false trust characteristic [CI] | mean trusted (LT) [CI] | q at cap |
|---|---|---|---|---|
| A2 + constant | 0.105 [0.0925, 0.118] | 0.107 [0.088, 0.128] | 1.89 [1.89, 1.89] | 0 |
| A2 + h(F-hat) | 0.145 [0.132, 0.159] | 0.139 [0.119, 0.161] | 2.21 [2.18, 2.25] | 0 |
| A4 + KM leaf | 0.123 [0.11, 0.136] | 0.121 [0.104, 0.14] | 2.15 [2.11, 2.19] | 0 |
| g(F-hat) + h(F-hat) | 0.15 [0.137, 0.165] | 0.144 [0.124, 0.165] | 2.27 [2.24, 2.32] | 0 |

Hybrid MSE ratio to A2 (realized per draw; 1.05 table, R2 guard).

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| policy | H=8 (0.27 LT) | H=15 (0.50 LT) | H=30 (1.00 LT) | H=60 (2.00 LT) | H=120 (4.00 LT) |
|---|---|---|---|---|---|
| A4 + KM leaf | 1.09 [1.06, 1.13] undetermined (n_eff < 50) | 1.09 [1.05, 1.14] undetermined (n_eff < 50) | 1.02 [0.984, 1.06] undetermined | 0.991 [0.962, 1.02] negligible | 1.03 [1.01, 1.06] needed, size not determined |
| g(F-hat) + h(F-hat) | 1 [0.987, 1.02] undetermined (n_eff < 50) | 1 [0.971, 1.04] undetermined (n_eff < 50) | 0.979 [0.955, 1] negligible | 0.976 [0.944, 1.01] negligible | 0.991 [0.979, 1] negligible |

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| full system minus | false trust realized [CI] | false trust characteristic [CI] | trusted LT [CI] |
|---|---|---|---|
| A2 + constant | 0.0457 [0.034, 0.0583] | 0.0375 [0.015, 0.059] | 0.384 [0.348, 0.426] |
| A2 + h(F-hat) | 0.00525 [-0.00225, 0.0135] | 0.00525 [-0.00626, 0.0165] | 0.0613 [0.0534, 0.0699] |
| A4 + KM leaf | 0.0278 [0.0165, 0.0388] | 0.023 [0.00325, 0.042] | 0.125 [0.108, 0.142] |

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| horizon model (own characteristic target) | pinball / constant's | constant/model ratio [CI] reading | cov 0.1 / 0.5 / 0.9 | C |
|---|---|---|---|---|
| h_A2(F-hat) | 0.101 / 0.146 | 1.45 [1.37, 1.52] substantial | 0.139 / 0.536 / 0.884 | 0.716 |
| h_g(F-hat) | 0.102 / 0.155 | 1.52 [1.44, 1.6] substantial | 0.144 / 0.532 / 0.889 | - |

### E-H2a. Amplification mismatch m(H) (H_0 = 1 LT; both r.m.s. <= 0.5 sigma_x)

Medians by tercile of I (low / mid / high). Spearman(m, I) on the kept states [95%]. B and A columns from the A/D record (oracle).

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| horizon | kept | m | abs drift w* | corr C/sqrt(E_C E_P) | Spearman(m, I) | B RI / OI | A drop-I (MSE) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 998 | -0.062 / 0.19 / 0.049 | 0.094 / 0.093 / 0.064 | 0.15 / 0.15 / 0.21 | 0.0367 [-0.024, 0.0986] | no interaction gain detected / no interaction gain detected | negligible |
| H=15 (0.50 LT) | 998 | -0.095 / 0.15 / 0.077 | 0.092 / 0.071 / 0.052 | 0.17 / 0.15 / 0.2 | 0.0312 [-0.0378, 0.0984] | no interaction gain detected / no interaction gain detected | negligible |
| H=30 (1.00 LT) | 998 | 0 / 0 / 0 | 0 / 0 / 0 | 0.19 / 0.18 / 0.24 | (H_0) | no interaction gain detected / no interaction gain detected | negligible |
| H=60 (2.00 LT) | 916 | -0.26 / -0.26 / -0.31 | 0.095 / 0.096 / 0.094 | 0.2 / 0.23 / 0.28 | -0.0345 [-0.0965, 0.032] | no interaction gain detected / no interaction gain detected | negligible |
| H=120 (4.00 LT) | 687 | -1.5 / -1.4 / -1.6 | 0.21 / 0.29 / 0.37 | 0.34 / 0.32 / 0.36 | -0.0205 [-0.0895, 0.05] | no interaction gain detected / no interaction gain detected | negligible |

**Reading: not consistent** (horizons_used: ['60', '120'], horizons_supporting: [], horizons_null: ['60', '120']).

### E-H2e. Library size and error correlation (sweep states)

1000 sweep states. Delta = value at N_lib 100000 minus 1000. corr = the H2e correlation (0 by convention where an error is constant over the draws).

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| rho | valid | corr 0 small / large lib | median corr small -> large | set | median Delta corr [CI] | Spearman(Delta corr, Delta R) [CI] | reading |
|---|---|---|---|---|---|---|---|
| 0.01 | 1000 | 612 / 1 | 0 -> 0.448 | all (1000) | 0.366 [0.351, 0.388] | 0.259 [0.199, 0.311] | not consistent |
| 0.01 | 1000 | 612 / 1 | 0 -> 0.448 | both_defined (387) | 0.17 [0.134, 0.208] | 0.252 [0.16, 0.342] | not consistent |
| 0.02 | 1000 | 308 / 0 | 0.115 -> 0.46 | all (1000) | 0.271 [0.248, 0.294] | 0.218 [0.162, 0.272] | not consistent |
| 0.02 | 1000 | 308 / 0 | 0.115 -> 0.46 | both_defined (692) | 0.169 [0.14, 0.195] | 0.184 [0.116, 0.251] | not consistent |

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| rho | stratifier | median Delta corr low / mid / high | median Delta R low / mid / high |
|---|---|---|---|
| 0.01 | R | 0.35 / 0.41 / 0.37 | -1.3 / -1.2 / -1.5 |
| 0.01 | O | 0.35 / 0.37 / 0.38 | -1.3 / -1.3 / -1.3 |
| 0.01 | I | 0.3 / 0.34 / 0.43 | -1.3 / -1.3 / -1.3 |
| 0.01 | N | 0.37 / 0.39 / 0.34 | -1.4 / -1.1 / -1.3 |
| 0.01 | delta_R | 0.26 / 0.39 / 0.42 | -2 / -1.3 / -0.49 |
| 0.02 | R | 0.26 / 0.28 / 0.29 | -0.72 / -0.67 / -0.94 |
| 0.02 | O | 0.29 / 0.24 / 0.29 | -0.8 / -0.76 / -0.76 |
| 0.02 | I | 0.21 / 0.26 / 0.36 | -0.82 / -0.74 / -0.78 |
| 0.02 | N | 0.28 / 0.27 / 0.27 | -0.89 / -0.62 / -0.79 |
| 0.02 | delta_R | 0.19 / 0.27 / 0.34 | -1.4 / -0.78 / -0.031 |

**Reading** (final, after the convention check): rho 0.01: not consistent; rho 0.02: not consistent.

### E-H3c. A5 against A4

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| item | value |
|---|---|
| H3c ratio MSE(A5)/MSE(A4) [CI at level 0.983] (run) | 0.99 [0.946, 1.04], width 0.0897 |
| top-1% share: A5 loss / A4 loss / abs(A5 - A4) | 0.156 / 0.152 / 0.166 |
| autocorrelation of d = A5 - A4, lags 1..5 | -0.005, 0.0055, 0.033, 0.014, 0.058 |
| block-5 means: lag-1 autocorrelation, variance ratio | 0.0802, 1.06 |
| K chosen; leaves used test / calibration; largest leaf share test | 4; 4 / 4; 0.357 |
| w*(H_ref) within-leaf share of variance | 0.957 |
| bimodality coefficient R/O/I/N, oracle; deployable | 0.26/0.78/0.48/0.82; 0.51/0.79/0.49/0.9 |
| Spearman pairs (oracle) | RO 0.39, RI 0.019, RN 0.41, OI 0.016, ON 0.052, IN 0.053 |
| top-1% abs(d) states: mean percentile R/O/I/N | 0.76/0.85/0.71/0.6 |
| top-1% abs(d) states: median I pct; share high-I; median abs(x) pct; share sign change in window; share of sum d | 0.841; 0.7; 0.303; 1; 0.0753 |

## chua

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| check | result |
|---|---|
| A2 rebuilt on 1..H_max equals the dumped A2 (bitwise); A4 horizon-free | True, True |
| g refit reproduces WU-0048 A/ROIN MSE (max abs, oracle / deployable) | 0 / 0 |
| T_c counts T = 1 / e_(T-1) = theta (A2 train, g train, A2 test, g test, A4 calibration) | 4/0, 16/0, 1/0, 4/0, 8/0 |
| A2 on 1..H_max: pooled curvature floor / columns at 0 or 1 | 0 / 0 |
| weights clipped to [0, 1] (g oracle test / train OOF, g deployable test / train OOF) | 686, 1748, 1609, 5750 |

### C1. Separate performance (from the A/D record, no refit)

Allocation: MSE per rule (oracle: moment form; deployable: realized); reading of the rung against F (MSE ratio, 1.05 table, n_eff guard). G(F) = 1 - L_A(F)/L_A(constant).

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| horizon | profile | constant | separation | RO | F (ROIN) | X | X+F | G(F) | sep vs F | RO vs F | X+F vs F |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | oracle | 0.000925 | 0.000576 | 0.000688 | 0.000734 | 0.000918 | 0.000709 | 0.451 | undetermined | undetermined | undetermined |
| H=8 (0.27 LT) | deployable | 0.000739 | 0.000811 | 0.000744 | 0.000744 | 0.000744 | 0.000743 | -0.023 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | oracle | 0.00251 | 0.0021 | 0.00229 | 0.00214 | 0.00246 | 0.00216 | 0.468 | undetermined | undetermined | undetermined |
| H=15 (0.50 LT) | deployable | 0.0024 | 0.00293 | 0.00244 | 0.00245 | 0.00242 | 0.00247 | -0.064 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | oracle | 0.0173 | 0.0162 | 0.0166 | 0.0168 | 0.018 | 0.0163 | 0.0773 | undetermined | undetermined | undetermined |
| H=30 (1.00 LT) | deployable | 0.0175 | 0.0167 | 0.0172 | 0.0168 | 0.0187 | 0.0165 | 0.125 | undetermined | undetermined | undetermined |
| H=60 (2.00 LT) | oracle | 0.205 | 0.197 | 0.192 | 0.192 | 0.201 | 0.19 | 0.172 | undetermined | negligible | negligible |
| H=60 (2.00 LT) | deployable | 0.214 | 0.215 | 0.211 | 0.211 | 0.211 | 0.208 | 0.0377 | undetermined | negligible | negligible |
| H=120 (4.00 LT) | oracle | 0.663 | 0.687 | 0.66 | 0.65 | 0.66 | 0.649 | 0.0662 | needed, size not determined | small | negligible |
| H=120 (4.00 LT) | deployable | 0.704 | 0.743 | 0.7 | 0.696 | 0.699 | 0.692 | 0.0332 | needed, size not determined | negligible | negligible |

Horizon (Y = ln min(T_c, H_max)): pinball at 0.5 / Harrell's C / coverage of q_0.1 below the cap; reading against F.

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| profile | rung | pinball | C | cov q_0.1 | reading vs F |
|---|---|---|---|---|---|
| oracle | none | 0.232 | 0.5 | 0.119 | substantial |
| oracle | lyapunov | 0.252 | 0.684 | 0.084 | substantial |
| oracle | RO | 0.21 | 0.624 | 0.119 | substantial |
| oracle | ROIN | 0.166 | 0.712 | 0.167 |  |
| oracle | X | 0.183 | 0.689 | 0.152 | needed, size not determined |
| oracle | X+F | 0.14 | 0.767 | 0.153 | lowers |
| oracle | Lyapunov rank | | 0.686 | | |
| deployable | none | 0.232 | 0.5 | 0.119 | substantial |
| deployable | lyapunov | 0.253 | 0.681 | 0.0799 | substantial |
| deployable | RO | 0.204 | 0.632 | 0.123 | substantial |
| deployable | ROIN | 0.163 | 0.723 | 0.141 |  |
| deployable | X | 0.186 | 0.685 | 0.153 | substantial |
| deployable | X+F | 0.14 | 0.768 | 0.144 | lowers |
| deployable | Lyapunov rank | | 0.683 | | |

### C2. Shared information (oracle profile)

Skill retained = [L(constant) - L(bottleneck)] / [L(constant) - L(F)]; reading: keeps most (CI > 0.5), loses most (CI < 0.5), else not determined. Forward: horizon from g(F) (five clipped weights); reverse: weight from h(F) (three quantiles). Training inputs cross-fitted.

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| direction | horizon | L(constant) | L(F) | L(bottleneck) | full skill [CI] | retained [CI] | reading |
|---|---|---|---|---|---|---|---|
| forward (pinball) | all five | 0.232 | 0.166 | 0.205 | 0.0655 [0.0553, 0.0758] | 0.404 [0.315, 0.489] | loses most |
| forward, one weight | H=8 (0.27 LT) | | | 0.231 | | 0.00327 [-0.0247, 0.0324] | loses most |
| forward, one weight | H=15 (0.50 LT) | | | 0.231 | | 0.00451 [-0.0372, 0.0466] | loses most |
| forward, one weight | H=30 (1.00 LT) | | | 0.228 | | 0.0548 [0.0169, 0.0958] | loses most |
| forward, one weight | H=60 (2.00 LT) | | | 0.226 | | 0.0919 [0.0461, 0.139] | loses most |
| forward, one weight | H=120 (4.00 LT) | | | 0.224 | | 0.122 [0.0515, 0.196] | loses most |
| reverse (MSE) | H=8 (0.27 LT) | 0.000925 | 0.000734 | 0.00123 | 0.000191 [2.5e-05, 0.000464] | -1.59 [-19, 0.569] | not determined (n_eff < 50) |
| reverse (MSE) | H=15 (0.50 LT) | 0.00251 | 0.00214 | 0.00264 | 0.000371 [-1.85e-05, 0.000934] | -0.352 [-, -] | not determined (full-profile skill not established) |
| reverse (MSE) | H=30 (1.00 LT) | 0.0173 | 0.0168 | 0.0171 | 0.00046 [-0.00173, 0.00202] | 0.44 [-, -] | not determined (full-profile skill not established) |
| reverse (MSE) | H=60 (2.00 LT) | 0.205 | 0.192 | 0.204 | 0.0123 [0.00578, 0.0187] | 0.0376 [-0.183, 0.205] | loses most |
| reverse (MSE) | H=120 (4.00 LT) | 0.663 | 0.65 | 0.662 | 0.0126 [0.00594, 0.0193] | 0.063 [-0.419, 0.417] | loses most |

Forward C-index: F 0.712, g(F) 0.632. Reverse MSE(h(F))/MSE(F): H=8 (0.27 LT) 1.67 [1.11, 2.5] undetermined (n_eff < 50); H=15 (0.50 LT) 1.23 [1.06, 1.48] undetermined (n_eff < 50); H=30 (1.00 LT) 1.02 [0.901, 1.12] undetermined (n_eff < 50); H=60 (2.00 LT) 1.06 [1.03, 1.1] needed, size not determined; H=120 (4.00 LT) 1.02 [1.01, 1.03] small.

Math-spec prediction (both bottlenecks lose most): **consistent**; largest single-weight forward retention at H = 120.

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| horizon | Spearman(phi allocation, phi horizon) (4 items, descriptive) | phi_alloc R/O/I/N | phi_horizon R/O/I/N |
|---|---|---|---|
| H=8 (0.27 LT) | 0.4 | 4.1e-05/0.00014/1.1e-05/-1.9e-06 | 0.0016/0.013/0.049/0.0014 |
| H=15 (0.50 LT) | 0.8 | 8.5e-05/0.00023/0.00011/-5.3e-05 | 0.0016/0.013/0.049/0.0014 |
| H=30 (1.00 LT) | 0 | 0.0007/-0.00015/4.3e-05/-0.00012 | 0.0016/0.013/0.049/0.0014 |
| H=60 (2.00 LT) | -0.4 | 0.0084/0.0041/-0.0007/0.00063 | 0.0016/0.013/0.049/0.0014 |
| H=120 (4.00 LT) | -0.6 | 0.0052/-6.2e-05/0.0027/0.0047 | 0.0016/0.013/0.049/0.0014 |

### C3. The deployable chain

False trust = P(T <= q_0.1) per (state, draw), target 0.1; T realized (the run's first passage against the noisy truth) or characteristic (moments). Trusted horizon = mean q_0.1 (LT). A4 + KM leaf uses the calibration A4 hybrid's characteristic horizon (no per-draw calibration errors on the full grid).

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| policy | false trust realized [CI] | false trust characteristic [CI] | mean trusted (LT) [CI] | q at cap |
|---|---|---|---|---|
| A2 + constant | 0.0793 [0.0665, 0.091] | 0.118 [0.1, 0.139] | 0.995 [0.995, 0.995] | 0 |
| A2 + h(F-hat) | 0.116 [0.103, 0.13] | 0.135 [0.116, 0.154] | 1.4 [1.37, 1.43] | 0 |
| A4 + KM leaf | 0.0983 [0.0855, 0.111] | 0.123 [0.103, 0.138] | 1.35 [1.33, 1.38] | 0 |
| g(F-hat) + h(F-hat) | 0.111 [0.098, 0.125] | 0.132 [0.112, 0.149] | 1.43 [1.4, 1.46] | 0 |

Hybrid MSE ratio to A2 (realized per draw; 1.05 table, R2 guard).

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| policy | H=8 (0.27 LT) | H=15 (0.50 LT) | H=30 (1.00 LT) | H=60 (2.00 LT) | H=120 (4.00 LT) |
|---|---|---|---|---|---|
| A4 + KM leaf | 1.1 [1.03, 1.17] undetermined (n_eff < 50) | 1.22 [1.06, 1.38] undetermined (n_eff < 50) | 0.947 [0.873, 1.05] undetermined (n_eff < 50) | 1 [0.971, 1.03] negligible | 1.06 [1.03, 1.09] needed, size not determined |
| g(F-hat) + h(F-hat) | 1.01 [0.995, 1.02] undetermined (n_eff < 50) | 1.02 [0.962, 1.07] undetermined (n_eff < 50) | 0.952 [0.906, 1] undetermined (n_eff < 50) | 0.985 [0.95, 1.02] negligible | 0.989 [0.98, 0.998] lowers |

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| full system minus | false trust realized [CI] | false trust characteristic [CI] | trusted LT [CI] |
|---|---|---|---|
| A2 + constant | 0.0318 [0.018, 0.0462] | 0.0135 [-0.0115, 0.0348] | 0.435 [0.403, 0.468] |
| A2 + h(F-hat) | -0.00475 [-0.0123, 0.0025] | -0.00375 [-0.014, 0.00425] | 0.0293 [0.0231, 0.0359] |
| A4 + KM leaf | 0.0127 [0.00275, 0.0227] | 0.00875 [-0.006, 0.024] | 0.0762 [0.0531, 0.0999] |

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| horizon model (own characteristic target) | pinball / constant's | constant/model ratio [CI] reading | cov 0.1 / 0.5 / 0.9 | C |
|---|---|---|---|---|
| h_A2(F-hat) | 0.159 / 0.237 | 1.49 [1.41, 1.59] substantial | 0.135 / 0.515 / 0.878 | 0.738 |
| h_g(F-hat) | 0.159 / 0.238 | 1.5 [1.41, 1.59] substantial | 0.132 / 0.528 / 0.884 | - |

### E-H2a. Amplification mismatch m(H) (H_0 = 1 LT; both r.m.s. <= 0.5 sigma_x)

Medians by tercile of I (low / mid / high). Spearman(m, I) on the kept states [95%]. B and A columns from the A/D record (oracle).

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| horizon | kept | m | abs drift w* | corr C/sqrt(E_C E_P) | Spearman(m, I) | B RI / OI | A drop-I (MSE) |
|---|---|---|---|---|---|---|---|
| H=8 (0.27 LT) | 918 | -0.037 / 0.27 / 0.25 | 0.057 / 0.095 / 0.098 | 0.18 / 0.16 / 0.27 | 0.148 [0.0791, 0.215] | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=15 (0.50 LT) | 913 | 0.046 / 0.071 / 0.18 | 0.057 / 0.1 / 0.089 | 0.17 / 0.17 / 0.27 | 0.106 [0.0402, 0.172] | no interaction gain detected / no interaction gain detected | undetermined (n_eff < 50) |
| H=30 (1.00 LT) | 919 | 0 / 0 / 0 | 0 / 0 / 0 | 0.18 / 0.2 / 0.3 | (H_0) | no interaction gain detected / interaction gain detected | undetermined (n_eff < 50) |
| H=60 (2.00 LT) | 623 | -0.45 / -0.54 / -0.16 | 0.087 / 0.12 / 0.097 | 0.2 / 0.16 / 0.28 | 0.0025 [-0.0717, 0.0881] | interaction gain detected / interaction gain detected | negligible |
| H=120 (4.00 LT) | 237 | -1.2 / -1.7 / -0.89 | 0.17 / 0.32 / 0.16 | 0.31 / 0.27 / 0.34 | -0.0335 [-0.155, 0.108] | no interaction gain detected / no interaction gain detected | negligible |

**Reading: not determined** (horizons_used: ['60', '120'], horizons_supporting: [], horizons_null: ['60']).

### E-H2e. Library size and error correlation (sweep states)

1000 sweep states. Delta = value at N_lib 100000 minus 1000. corr = the H2e correlation (0 by convention where an error is constant over the draws).

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| rho | valid | corr 0 small / large lib | median corr small -> large | set | median Delta corr [CI] | Spearman(Delta corr, Delta R) [CI] | reading |
|---|---|---|---|---|---|---|---|
| 0.01 | 1000 | 534 / 18 | 0 -> 0.419 | all (1000) | 0.318 [0.292, 0.343] | 0.0537 [-0.00696, 0.116] | not determined |
| 0.01 | 1000 | 534 / 18 | 0 -> 0.419 | both_defined (464) | 0.189 [0.142, 0.232] | 0.075 [-0.0214, 0.163] | not determined |
| 0.02 | 1000 | 264 / 2 | 0.079 -> 0.409 | all (1000) | 0.252 [0.223, 0.275] | -0.0351 [-0.0982, 0.0292] | not determined |
| 0.02 | 1000 | 264 / 2 | 0.079 -> 0.409 | both_defined (735) | 0.189 [0.161, 0.214] | 0.0474 [-0.0265, 0.118] | not determined |

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| rho | stratifier | median Delta corr low / mid / high | median Delta R low / mid / high |
|---|---|---|---|
| 0.01 | R | 0.33 / 0.33 / 0.3 | -1.3 / -1.2 / -1.5 |
| 0.01 | O | 0.35 / 0.29 / 0.31 | -1.7 / -1.3 / -1 |
| 0.01 | I | 0.31 / 0.29 / 0.36 | -1.4 / -1.3 / -1.2 |
| 0.01 | N | 0.32 / 0.32 / 0.31 | -1.6 / -1 / -1.3 |
| 0.01 | delta_R | 0.31 / 0.32 / 0.33 | -2.2 / -1.3 / -0.48 |
| 0.02 | R | 0.23 / 0.27 / 0.26 | -0.71 / -0.67 / -0.98 |
| 0.02 | O | 0.33 / 0.22 / 0.22 | -1.2 / -0.74 / -0.52 |
| 0.02 | I | 0.22 / 0.24 / 0.28 | -0.84 / -0.86 / -0.64 |
| 0.02 | N | 0.25 / 0.26 / 0.24 | -1.1 / -0.55 / -0.73 |
| 0.02 | delta_R | 0.29 / 0.2 / 0.25 | -1.6 / -0.76 / -0.1 |

**Reading** (final, after the convention check): rho 0.01: not determined; rho 0.02: not determined.

### E-H3c. A5 against A4

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| item | value |
|---|---|
| H3c ratio MSE(A5)/MSE(A4) [CI at level 0.983] (run) | 1.05 [0.967, 1.12], width 0.158 |
| top-1% share: A5 loss / A4 loss / abs(A5 - A4) | 0.553 / 0.546 / 0.392 |
| autocorrelation of d = A5 - A4, lags 1..5 | 0.0055, 0.026, -0.0045, -0.016, -0.012 |
| block-5 means: lag-1 autocorrelation, variance ratio | 0.0254, 0.953 |
| K chosen; leaves used test / calibration; largest leaf share test | 6; 6 / 6; 0.256 |
| w*(H_ref) within-leaf share of variance | 0.908 |
| bimodality coefficient R/O/I/N, oracle; deployable | 0.22/0.26/0.47/0.85; 0.32/0.48/0.49/0.89 |
| Spearman pairs (oracle) | RO 0.085, RI -0.00079, RN 0.37, OI 0.33, ON 0.14, IN -0.0024 |
| top-1% abs(d) states: mean percentile R/O/I/N | 0.47/0.62/0.89/0.4 |
| top-1% abs(d) states: median I pct; share high-I; median abs(x) pct; share sign change in window; share of sum d | 0.947; 0.9; 0.655; 0.2; 0.428 |

## E-H3c reading (this seed)

DEVELOPMENT (DEV-3): exploratory, not a hypothesis test.

| item | value |
|---|---|
| H3c interval widths | lorenz63 0.536, rossler 0.0897, chua 0.158 |
| pattern (Lorenz-63 widest, Rössler narrowest) reproduced | True |
| Lorenz-63 part (top-1% share of sum abs(d) 0.597, median I percentile 0.19) | not consistent |
| Rössler part (BC deployable: R 0.507, O 0.786, I 0.489, N 0.897) | not consistent |
| **reading** | **not consistent** |

