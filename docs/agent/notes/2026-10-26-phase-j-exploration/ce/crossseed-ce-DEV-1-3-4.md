# Phase J experiments C and E: DEV-1, DEV-3, DEV-4 side by side

**DEVELOPMENT (DEV-1, DEV-3, DEV-4): exploratory, not a hypothesis test.** One column per seed; no pooling and no new statistic. Every cell is copied from that seed's ce.json.

| system | item | DEV-1 | DEV-3 | DEV-4 |
|---|---|---|---|---|
| lorenz63 | C1 G(F) oracle, 1 LT | 0.75 | 0.608 | 0.334 |
| lorenz63 | C1 F pinball / C, oracle | 0.146 / 0.678 | 0.149 / 0.675 | 0.148 / 0.692 |
| lorenz63 | C2 forward retained [CI] | 0.129 [0.0587, 0.192] loses most | 0.179 [0.107, 0.258] loses most | 0.0951 [0.0464, 0.149] loses most |
| lorenz63 | C2 reverse retained, H=8 | 0.598 [0.364, 0.746] not determined (n_eff < 50) | 0.514 [0.076, 0.779] not determined (n_eff < 50) | -0.225 [-0.775, 0.204] not determined (n_eff < 50) |
| lorenz63 | C2 reverse retained, H=30 | 0.606 [0.386, 0.77] not determined (n_eff < 50) | 0.815 [0.481, 2.06] not determined (n_eff < 50) | -1.87 [-, -] not determined (full-profile skill not established) |
| lorenz63 | C2 reverse retained, H=120 | - [-, -] not determined (full-profile skill not established) | 0.323 [-, -] not determined (full-profile skill not established) | -0.0436 [-3.69, 1.08] not determined (interval spans 0.5) |
| lorenz63 | C2 prediction (both lose most) | consistent | consistent | consistent |
| lorenz63 | C2 Spearman(phi), 1 LT | 0.6 | 0.6 | 0.8 |
| lorenz63 | C3 false trust realized: A2 + constant | 0.0805 [0.068, 0.0932] | 0.0658 [0.0525, 0.0778] | 0.0612 [0.0495, 0.0732] |
| lorenz63 | C3 trusted LT: A2 + constant | 0.621 [0.621, 0.621] | 0.538 [0.538, 0.538] | 0.39 [0.39, 0.39] |
| lorenz63 | C3 false trust realized: A2 + h(F-hat) | 0.108 [0.0952, 0.122] | 0.089 [0.076, 0.102] | 0.0925 [0.0798, 0.106] |
| lorenz63 | C3 trusted LT: A2 + h(F-hat) | 1.06 [1.03, 1.08] | 0.991 [0.966, 1.02] | 0.95 [0.923, 0.976] |
| lorenz63 | C3 false trust realized: A4 + KM leaf | 0.096 [0.084, 0.109] | 0.0628 [0.052, 0.0722] | 0.0658 [0.0547, 0.0772] |
| lorenz63 | C3 trusted LT: A4 + KM leaf | 1.13 [1.12, 1.15] | 0.974 [0.95, 0.999] | 0.669 [0.648, 0.69] |
| lorenz63 | C3 false trust realized: g(F-hat) + h(F-hat) | 0.0963 [0.0835, 0.109] | 0.0902 [0.078, 0.101] | 0.106 [0.0915, 0.121] |
| lorenz63 | C3 trusted LT: g(F-hat) + h(F-hat) | 1.15 [1.13, 1.17] | 1.09 [1.06, 1.11] | 1.04 [1.01, 1.07] |
| lorenz63 | C3 MSE g / A2 at 1 LT | 0.688 [0.487, 0.884] undetermined (n_eff < 50) | 0.719 [0.531, 0.928] undetermined (n_eff < 50) | 0.901 [0.7, 1.14] undetermined (n_eff < 50) |
| lorenz63 | E-H2a reading | not determined | not determined | consistent |
| lorenz63 | E-H2a Spearman(m, I) at 2 LT | -0.0236 [-0.0978, 0.0538] | 0.000719 [-0.0692, 0.0738] | 0.0794 [-0.000604, 0.147] |
| lorenz63 | E-H2e reading rho 0.01 | not determined (depends on the zero-variance convention) | not determined (depends on the zero-variance convention) | not determined (depends on the zero-variance convention) |
| lorenz63 | E-H2e Spearman all, rho 0.01 | 0.0733 [0.00877, 0.136] | 0.0911 [0.0309, 0.153] | 0.161 [0.1, 0.211] |
| lorenz63 | E-H2e reading rho 0.02 | not determined (depends on the zero-variance convention) | not determined (depends on the zero-variance convention) | not determined (depends on the zero-variance convention) |
| lorenz63 | E-H2e Spearman all, rho 0.02 | -0.0259 [-0.0842, 0.0317] | -0.0436 [-0.104, 0.0163] | 0.111 [0.0496, 0.165] |
| lorenz63 | E-H3c ratio [CI] | 0.711 [0.527, 0.896] | 0.794 [0.589, 1.12] | 0.998 [0.812, 1.24] |
| lorenz63 | E-H3c top-1% share abs(d) | 0.683 | 0.597 | 0.585 |
| rossler | C1 G(F) oracle, 1 LT | 0.66 | 0.627 | 0.688 |
| rossler | C1 F pinball / C, oracle | 0.117 / 0.692 | 0.121 / 0.686 | 0.122 / 0.683 |
| rossler | C2 forward retained [CI] | 0.475 [0.379, 0.581] not determined (interval spans 0.5) | 0.483 [0.368, 0.586] not determined (interval spans 0.5) | 0.581 [0.49, 0.675] not determined (interval spans 0.5) |
| rossler | C2 reverse retained, H=8 | 0.311 [0.15, 0.439] loses most | 0.0572 [0.00163, 0.119] loses most | 0.154 [0.118, 0.197] loses most |
| rossler | C2 reverse retained, H=30 | 0.124 [0.0611, 0.187] loses most | 0.124 [0.0456, 0.198] loses most | 0.0971 [0.0498, 0.155] loses most |
| rossler | C2 reverse retained, H=120 | 0.704 [0.297, 1.54] not determined (interval spans 0.5) | -0.183 [-118, 2.49] not determined (interval spans 0.5) | 0.424 [0.11, 0.814] not determined (interval spans 0.5) |
| rossler | C2 prediction (both lose most) | not determined | not determined | not determined |
| rossler | C2 Spearman(phi), 1 LT | -1 | -1 | -0.8 |
| rossler | C3 false trust realized: A2 + constant | 0.0897 [0.0783, 0.101] | 0.105 [0.0925, 0.118] | 0.0983 [0.0867, 0.11] |
| rossler | C3 trusted LT: A2 + constant | 1.89 [1.89, 1.89] | 1.89 [1.89, 1.89] | 1.87 [1.87, 1.87] |
| rossler | C3 false trust realized: A2 + h(F-hat) | 0.131 [0.117, 0.143] | 0.145 [0.132, 0.159] | 0.136 [0.122, 0.15] |
| rossler | C3 trusted LT: A2 + h(F-hat) | 2.21 [2.17, 2.24] | 2.21 [2.18, 2.25] | 2.2 [2.16, 2.23] |
| rossler | C3 false trust realized: A4 + KM leaf | 0.105 [0.0917, 0.118] | 0.123 [0.11, 0.136] | 0.123 [0.111, 0.136] |
| rossler | C3 trusted LT: A4 + KM leaf | 2.13 [2.09, 2.16] | 2.15 [2.11, 2.19] | 2.1 [2.07, 2.14] |
| rossler | C3 false trust realized: g(F-hat) + h(F-hat) | 0.13 [0.117, 0.142] | 0.15 [0.137, 0.165] | 0.141 [0.128, 0.156] |
| rossler | C3 trusted LT: g(F-hat) + h(F-hat) | 2.25 [2.21, 2.29] | 2.27 [2.24, 2.32] | 2.24 [2.2, 2.28] |
| rossler | C3 MSE g / A2 at 1 LT | 0.977 [0.952, 1] lowers | 0.979 [0.955, 1] negligible | 0.97 [0.944, 0.995] lowers |
| rossler | E-H2a reading | not determined | not consistent | not determined |
| rossler | E-H2a Spearman(m, I) at 2 LT | -0.0425 [-0.107, 0.021] | -0.0345 [-0.0965, 0.032] | 0.019 [-0.0475, 0.0858] |
| rossler | E-H2e reading rho 0.01 | not consistent | not consistent | not determined (depends on the zero-variance convention) |
| rossler | E-H2e Spearman all, rho 0.01 | 0.204 [0.143, 0.26] | 0.259 [0.199, 0.311] | 0.09 [0.0245, 0.152] |
| rossler | E-H2e reading rho 0.02 | not consistent | not consistent | not consistent |
| rossler | E-H2e Spearman all, rho 0.02 | 0.172 [0.106, 0.231] | 0.218 [0.162, 0.272] | 0.169 [0.109, 0.231] |
| rossler | E-H3c ratio [CI] | 0.969 [0.922, 1.01] | 0.99 [0.946, 1.04] | 0.951 [0.908, 0.991] |
| rossler | E-H3c top-1% share abs(d) | 0.213 | 0.166 | 0.2 |
| chua | C1 G(F) oracle, 1 LT | 0.203 | 0.0773 | 0.247 |
| chua | C1 F pinball / C, oracle | 0.15 / 0.725 | 0.166 / 0.712 | 0.159 / 0.721 |
| chua | C2 forward retained [CI] | 0.485 [0.405, 0.573] not determined (interval spans 0.5) | 0.404 [0.315, 0.489] loses most | 0.372 [0.286, 0.462] loses most |
| chua | C2 reverse retained, H=8 | 0.482 [0.141, 1.07] not determined (n_eff < 50) | -1.59 [-19, 0.569] not determined (n_eff < 50) | 0.261 [-0.212, 0.425] not determined (n_eff < 50) |
| chua | C2 reverse retained, H=30 | 0.475 [-, -] not determined (full-profile skill not established) | 0.44 [-, -] not determined (full-profile skill not established) | -0.0726 [-, -] not determined (full-profile skill not established) |
| chua | C2 reverse retained, H=120 | 0.307 [-0.293, 0.723] not determined (interval spans 0.5) | 0.063 [-0.419, 0.417] loses most | 0.0818 [-0.141, 0.34] loses most |
| chua | C2 prediction (both lose most) | not determined | consistent | consistent |
| chua | C2 Spearman(phi), 1 LT | -0.2 | 0 | -0.8 |
| chua | C3 false trust realized: A2 + constant | 0.0685 [0.0573, 0.08] | 0.0793 [0.0665, 0.091] | 0.0665 [0.056, 0.0775] |
| chua | C3 trusted LT: A2 + constant | 0.967 [0.967, 0.967] | 0.995 [0.995, 0.995] | 1.01 [1.01, 1.01] |
| chua | C3 false trust realized: A2 + h(F-hat) | 0.0922 [0.08, 0.104] | 0.116 [0.103, 0.13] | 0.102 [0.0902, 0.115] |
| chua | C3 trusted LT: A2 + h(F-hat) | 1.41 [1.38, 1.44] | 1.4 [1.37, 1.43] | 1.46 [1.43, 1.49] |
| chua | C3 false trust realized: A4 + KM leaf | 0.0725 [0.0607, 0.0838] | 0.0983 [0.0855, 0.111] | 0.068 [0.057, 0.0798] |
| chua | C3 trusted LT: A4 + KM leaf | 1.21 [1.19, 1.23] | 1.35 [1.33, 1.38] | 1.29 [1.27, 1.32] |
| chua | C3 false trust realized: g(F-hat) + h(F-hat) | 0.0915 [0.0798, 0.102] | 0.111 [0.098, 0.125] | 0.0948 [0.084, 0.107] |
| chua | C3 trusted LT: g(F-hat) + h(F-hat) | 1.46 [1.43, 1.49] | 1.43 [1.4, 1.46] | 1.51 [1.48, 1.55] |
| chua | C3 MSE g / A2 at 1 LT | 1 [0.974, 1.03] undetermined (n_eff < 50) | 0.952 [0.906, 1] undetermined (n_eff < 50) | 0.908 [0.826, 0.982] undetermined (n_eff < 50) |
| chua | E-H2a reading | not determined | not determined | not determined |
| chua | E-H2a Spearman(m, I) at 2 LT | 0.0353 [-0.0411, 0.105] | 0.0025 [-0.0717, 0.0881] | 0.0166 [-0.0529, 0.0959] |
| chua | E-H2e reading rho 0.01 | not determined | not determined | not determined |
| chua | E-H2e Spearman all, rho 0.01 | 0.0275 [-0.0338, 0.0884] | 0.0537 [-0.00696, 0.116] | 0.0467 [-0.0135, 0.109] |
| chua | E-H2e reading rho 0.02 | consistent | not determined | not determined (depends on the zero-variance convention) |
| chua | E-H2e Spearman all, rho 0.02 | -0.11 [-0.169, -0.0474] | -0.0351 [-0.0982, 0.0292] | -0.0618 [-0.127, -0.000661] |
| chua | E-H3c ratio [CI] | 0.953 [0.903, 1] | 1.05 [0.967, 1.12] | 1.02 [0.951, 1.09] |
| chua | E-H3c top-1% share abs(d) | 0.347 | 0.392 | 0.458 |

DEVELOPMENT (DEV-1, DEV-3, DEV-4): exploratory, not a hypothesis test.

| system | item | DEV-1 | DEV-3 | DEV-4 |
|---|---|---|---|---|
| all | E-H3c reading | not consistent | not consistent | not consistent |

