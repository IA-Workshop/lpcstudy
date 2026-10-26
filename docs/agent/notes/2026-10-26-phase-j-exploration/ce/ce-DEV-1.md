# Phase J experiments C and E: DEV-1

**DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.** Run `/home/brianm/projects/physics/chaos/lpcstudy-wt/run/phj-f701a47/runs/dev/phj-DEV-1/full`; analysis commit `199e43a32db3ace33c88a0e8f2ad8ce2b405cc4d` (dirty: False); A/D record `/home/brianm/projects/physics/chaos/lpcstudy-wt/run/phj-f701a47/runs/dev/phj-DEV-1/contrib-ea0bd77/contrib.json`. Estimates with 95% intervals from the shared moving-block index sets (models fixed; training variance not included). Readings are descriptive; no causal claim; nothing here is set beside CONF-1.

## lorenz63

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| check | result |
|---|---|
| A2 rebuilt on 1..H_max equals the dumped A2 (bitwise); A4 horizon-free | True, True |
| g refit reproduces WU-0048 A/ROIN MSE (max abs, oracle / deployable) | 0 / 0 |
| T_c counts T = 1 / e_(T-1) = theta (A2 train, g train, A2 test, g test, A4 calibration) | 14/0, 110/0, 7/0, 30/0, 104/0 |
| A2 on 1..H_max: pooled curvature floor / columns at 0 or 1 | 0 / 0 |
| weights clipped to [0, 1] (g oracle test / train OOF, g deployable test / train OOF) | 554, 2058, 769, 3235 |

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

### C2. Shared information (oracle profile)

Skill retained = [L(constant) - L(bottleneck)] / [L(constant) - L(F)]; reading: keeps most (CI > 0.5), loses most (CI < 0.5), else not determined. Forward: horizon from g(F) (five clipped weights); reverse: weight from h(F) (three quantiles). Training inputs cross-fitted.

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| direction | horizon | L(constant) | L(F) | L(bottleneck) | full skill [CI] | retained [CI] | reading |
|---|---|---|---|---|---|---|---|
| forward (pinball) | all five | 0.185 | 0.146 | 0.18 | 0.0384 [0.0297, 0.0475] | 0.129 [0.0587, 0.192] | loses most |
| forward, one weight | H=8 (0.27 LT) | | | 0.184 | | 0.0127 [-0.039, 0.0617] | loses most |
| forward, one weight | H=15 (0.50 LT) | | | 0.183 | | 0.0355 [-0.0013, 0.0697] | loses most |
| forward, one weight | H=30 (1.00 LT) | | | 0.184 | | 0.0159 [-0.0245, 0.0526] | loses most |
| forward, one weight | H=60 (2.00 LT) | | | 0.183 | | 0.0451 [0.000173, 0.091] | loses most |
| forward, one weight | H=120 (4.00 LT) | | | 0.182 | | 0.0759 [0.012, 0.138] | loses most |
| reverse (MSE) | H=8 (0.27 LT) | 0.00898 | 0.000742 | 0.00406 | 0.00824 [0.0057, 0.0114] | 0.598 [0.364, 0.746] | not determined (n_eff < 50) |
| reverse (MSE) | H=15 (0.50 LT) | 0.0337 | 0.0111 | 0.023 | 0.0226 [0.0133, 0.0329] | 0.47 [0.318, 0.59] | not determined (n_eff < 50) |
| reverse (MSE) | H=30 (1.00 LT) | 0.0536 | 0.0247 | 0.0361 | 0.0289 [0.0186, 0.041] | 0.606 [0.386, 0.77] | not determined (n_eff < 50) |
| reverse (MSE) | H=60 (2.00 LT) | 0.151 | 0.132 | 0.142 | 0.0192 [0.00959, 0.0297] | 0.444 [0.238, 0.775] | not determined (interval spans 0.5) |
| reverse (MSE) | H=120 (4.00 LT) | 0.906 | 0.908 | 0.9 | -0.00236 [-0.015, 0.01] | - [-, -] | not determined (full-profile skill not established) |

Forward C-index: F 0.678, g(F) 0.569. Reverse MSE(h(F))/MSE(F): H=8 (0.27 LT) 5.47 [3.45, 8.68] undetermined (n_eff < 50); H=15 (0.50 LT) 2.08 [1.56, 3.17] undetermined (n_eff < 50); H=30 (1.00 LT) 1.46 [1.24, 1.8] undetermined (n_eff < 50); H=60 (2.00 LT) 1.08 [1.02, 1.16] needed, size not determined; H=120 (4.00 LT) 0.991 [0.978, 1.01] negligible.

Math-spec prediction (both bottlenecks lose most): **consistent**; largest single-weight forward retention at H = 120.

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
| g refit reproduces WU-0048 A/ROIN MSE (max abs, oracle / deployable) | 0 / 0 |
| T_c counts T = 1 / e_(T-1) = theta (A2 train, g train, A2 test, g test, A4 calibration) | 0/0, 0/0, 0/0, 0/0, 0/0 |
| A2 on 1..H_max: pooled curvature floor / columns at 0 or 1 | 0 / 0 |
| weights clipped to [0, 1] (g oracle test / train OOF, g deployable test / train OOF) | 869, 2674, 2529, 8051 |

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

### C2. Shared information (oracle profile)

Skill retained = [L(constant) - L(bottleneck)] / [L(constant) - L(F)]; reading: keeps most (CI > 0.5), loses most (CI < 0.5), else not determined. Forward: horizon from g(F) (five clipped weights); reverse: weight from h(F) (three quantiles). Training inputs cross-fitted.

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| direction | horizon | L(constant) | L(F) | L(bottleneck) | full skill [CI] | retained [CI] | reading |
|---|---|---|---|---|---|---|---|
| forward (pinball) | all five | 0.155 | 0.117 | 0.137 | 0.0383 [0.031, 0.0447] | 0.475 [0.379, 0.581] | not determined (interval spans 0.5) |
| forward, one weight | H=8 (0.27 LT) | | | 0.151 | | 0.103 [0.037, 0.174] | loses most |
| forward, one weight | H=15 (0.50 LT) | | | 0.151 | | 0.106 [0.0399, 0.179] | loses most |
| forward, one weight | H=30 (1.00 LT) | | | 0.152 | | 0.0869 [0.0142, 0.167] | loses most |
| forward, one weight | H=60 (2.00 LT) | | | 0.149 | | 0.167 [0.0863, 0.264] | loses most |
| forward, one weight | H=120 (4.00 LT) | | | 0.141 | | 0.378 [0.284, 0.488] | loses most |
| reverse (MSE) | H=8 (0.27 LT) | 0.000124 | 0.000112 | 0.000121 | 1.21e-05 [8.81e-06, 1.7e-05] | 0.311 [0.15, 0.439] | loses most |
| reverse (MSE) | H=15 (0.50 LT) | 0.000231 | 0.000202 | 0.000221 | 2.91e-05 [2e-05, 4.27e-05] | 0.346 [0.184, 0.466] | loses most |
| reverse (MSE) | H=30 (1.00 LT) | 0.000814 | 0.000708 | 0.000801 | 0.000107 [8.17e-05, 0.000136] | 0.124 [0.0611, 0.187] | loses most |
| reverse (MSE) | H=60 (2.00 LT) | 0.0139 | 0.0126 | 0.0136 | 0.0013 [0.000763, 0.00189] | 0.206 [0.0227, 0.41] | loses most |
| reverse (MSE) | H=120 (4.00 LT) | 0.105 | 0.103 | 0.104 | 0.0024 [0.000989, 0.00378] | 0.704 [0.297, 1.54] | not determined (interval spans 0.5) |

Forward C-index: F 0.692, g(F) 0.617. Reverse MSE(h(F))/MSE(F): H=8 (0.27 LT) 1.07 [1.06, 1.09] substantial; H=15 (0.50 LT) 1.09 [1.07, 1.12] substantial; H=30 (1.00 LT) 1.13 [1.1, 1.17] substantial; H=60 (2.00 LT) 1.08 [1.04, 1.13] needed, size not determined; H=120 (4.00 LT) 1.01 [0.994, 1.02] negligible.

Math-spec prediction (both bottlenecks lose most): **not determined**; largest single-weight forward retention at H = 120.

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
| g refit reproduces WU-0048 A/ROIN MSE (max abs, oracle / deployable) | 0 / 0 |
| T_c counts T = 1 / e_(T-1) = theta (A2 train, g train, A2 test, g test, A4 calibration) | 6/0, 12/0, 2/0, 0/0, 4/0 |
| A2 on 1..H_max: pooled curvature floor / columns at 0 or 1 | 0 / 0 |
| weights clipped to [0, 1] (g oracle test / train OOF, g deployable test / train OOF) | 644, 2144, 1670, 6849 |

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

### C2. Shared information (oracle profile)

Skill retained = [L(constant) - L(bottleneck)] / [L(constant) - L(F)]; reading: keeps most (CI > 0.5), loses most (CI < 0.5), else not determined. Forward: horizon from g(F) (five clipped weights); reverse: weight from h(F) (three quantiles). Training inputs cross-fitted.

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test.

| direction | horizon | L(constant) | L(F) | L(bottleneck) | full skill [CI] | retained [CI] | reading |
|---|---|---|---|---|---|---|---|
| forward (pinball) | all five | 0.214 | 0.15 | 0.183 | 0.0638 [0.0531, 0.0738] | 0.485 [0.405, 0.573] | not determined (interval spans 0.5) |
| forward, one weight | H=8 (0.27 LT) | | | 0.212 | | 0.0319 [0.00587, 0.0562] | loses most |
| forward, one weight | H=15 (0.50 LT) | | | 0.212 | | 0.0386 [0.00888, 0.0673] | loses most |
| forward, one weight | H=30 (1.00 LT) | | | 0.207 | | 0.111 [0.0765, 0.149] | loses most |
| forward, one weight | H=60 (2.00 LT) | | | 0.205 | | 0.145 [0.0979, 0.197] | loses most |
| forward, one weight | H=120 (4.00 LT) | | | 0.198 | | 0.249 [0.168, 0.324] | loses most |
| reverse (MSE) | H=8 (0.27 LT) | 0.000822 | 0.000626 | 0.000727 | 0.000196 [6.71e-05, 0.000364] | 0.482 [0.141, 1.07] | not determined (n_eff < 50) |
| reverse (MSE) | H=15 (0.50 LT) | 0.00217 | 0.00208 | 0.00242 | 9.1e-05 [-0.000162, 0.000315] | -2.7 [-, -] | not determined (full-profile skill not established) |
| reverse (MSE) | H=30 (1.00 LT) | 0.0143 | 0.0137 | 0.014 | 0.000558 [-0.00011, 0.00119] | 0.475 [-, -] | not determined (full-profile skill not established) |
| reverse (MSE) | H=60 (2.00 LT) | 0.196 | 0.185 | 0.192 | 0.0112 [0.00557, 0.0171] | 0.374 [0.0304, 0.76] | not determined (interval spans 0.5) |
| reverse (MSE) | H=120 (4.00 LT) | 0.649 | 0.637 | 0.645 | 0.012 [0.00448, 0.0192] | 0.307 [-0.293, 0.723] | not determined (interval spans 0.5) |

Forward C-index: F 0.725, g(F) 0.65. Reverse MSE(h(F))/MSE(F): H=8 (0.27 LT) 1.16 [0.993, 1.35] undetermined (n_eff < 50); H=15 (0.50 LT) 1.16 [0.955, 1.42] undetermined (n_eff < 50); H=30 (1.00 LT) 1.02 [0.981, 1.09] undetermined (n_eff < 50); H=60 (2.00 LT) 1.04 [1.01, 1.07] needed, size not determined; H=120 (4.00 LT) 1.01 [1, 1.02] small.

Math-spec prediction (both bottlenecks lose most): **not determined**; largest single-weight forward retention at H = 120.

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

