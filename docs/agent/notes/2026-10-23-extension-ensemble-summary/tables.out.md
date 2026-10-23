### Extension systems (DEV-3, one run each)

**rossler_hyper** (DEVELOPMENT (DEV-3): not a hypothesis test; commit 974519a)

Gate: PASS (V1, V2, V4, V5, V6, V7).

| Part | Estimate | Interval (level 0.9833) | Pass band | Stored part word |
|---|---|---|---|---|
| H2a(i) median range of w* | 0.1945 | [0.1479, 0.2458] | upper < 0.1 | fail |
| H2a(ii) zero, partial corr. | -0.01999 | [-0.09713, 0.06449] | inside (-0.1, 0.1) | pass |
| H2a(ii) interior, partial corr. | 0.02349 | [-0.06761, 0.1185] | inside (-0.1, 0.1) | inconclusive |
| H2b(i) Spearman w* with rho | 0.4096 | [0.3653, 0.4556] | lower > 0 | pass |
| H2b(ii) library change of w* | 0.03182 | [0.01086, 0.05168] | lower > 0 | pass |
| H3c MSE ratio A5/A4 | 0.3274 | [0.145, 4.504] | upper <= 1.05 | inconclusive |

Per-system words (verdicts/<H>/by_system/rossler_hyper): H2a fail; H2b pass; H3c inconclusive (primaries); H1a pass; H1b fail; H1c pass; H1d pass; H2c inconclusive; H2d inconclusive; H2e pass; H3a pass; H3b fail; Q-N reduces (secondaries).
Counts: H2a eligible 580 / excluded 420 of 1000; w* = 0: 272, w* = 1: 12; H3a censored per regime [0, 0]; V3 CP valid-prediction time 1.567 LT (reported).

**lorenz63_r166** (DEVELOPMENT (DEV-3): not a hypothesis test; commit 974519a)

Gate: FAIL V7 -> PROVISIONAL. Stored V7: median δ/(ρν) by ρ 0.005: 1.111, 0.01: 25.98, 0.02: 16.42, 0.05: 11.25 (band [0.9, 1.1]); median slope 0.9268 (slope_pass True).

| Part | Estimate | Interval (level 0.9833) | Pass band | Stored part word |
|---|---|---|---|---|
| H2a(i) median range of w* | 0.2362 | [0.1667, 0.3188] | upper < 0.1 | fail |
| H2a(ii) zero, partial corr. | 0.03787 | [-0.04573, 0.1085] | inside (-0.1, 0.1) | inconclusive |
| H2a(ii) interior, partial corr. | -0.1179 | [-0.2363, -0.01293] | inside (-0.1, 0.1) | inconclusive |
| H2b(i) Spearman w* with rho | 0.2334 | [0.181, 0.2817] | lower > 0 | pass |
| H2b(ii) library change of w* | -0.008574 | [-0.03499, 0.01649] | lower > 0 | inconclusive |
| H3c MSE ratio A5/A4 | 0.8994 | [0.8365, 0.976] | upper <= 1.05 | pass |

Per-system words (verdicts/<H>/by_system/lorenz63_r166): H2a fail; H2b inconclusive; H3c pass (primaries); H1a fail; H1b fail; H1c fail; H1d fail; H2c fail; H2d inconclusive; H2e inconclusive; H3a pass; H3b fail; Q-N reduces (secondaries).
Counts: H2a eligible 395 / excluded 605 of 1000; w* = 0: 155, w* = 1: 155; H3a censored per regime [4, 84, 15, 22]; V3 CP valid-prediction time 3.367 LT (reported).

**rossler_z** (DEVELOPMENT (DEV-3): not a hypothesis test; commit 974519a)

Gate: FAIL V7 -> PROVISIONAL. Stored V7: median δ/(ρν) by ρ 0.005: 1.025, 0.01: 1.07, 0.02: 1.111, 0.05: 0.9378 (band [0.9, 1.1]); median slope 0.8718 (slope_pass False).

| Part | Estimate | Interval (level 0.9833) | Pass band | Stored part word |
|---|---|---|---|---|
| H2a(i) median range of w* | 0.2145 | [0.1833, 0.2584] | upper < 0.1 | fail |
| H2a(ii) zero, partial corr. | 0.01603 | [-0.07028, 0.09484] | inside (-0.1, 0.1) | pass |
| H2a(ii) interior, partial corr. | -0.1832 | [-0.2634, -0.08966] | inside (-0.1, 0.1) | inconclusive |
| H2b(i) Spearman w* with rho | 0.1327 | [0.08508, 0.1877] | lower > 0 | pass |
| H2b(ii) library change of w* | -0.01982 | [-0.0409, -0.002553] | lower > 0 | fail |
| H3c MSE ratio A5/A4 | 0.9242 | [0.839, 1.007] | upper <= 1.05 | pass |

Per-system words (verdicts/<H>/by_system/rossler_z): H2a fail; H2b fail; H3c pass (primaries); H1a fail; H1b pass; H1c fail; H1d fail; H2c inconclusive; H2d pass; H2e pass; H3a inconclusive; H3b fail; Q-N reduces (secondaries).
Counts: H2a eligible 625 / excluded 375 of 1000; w* = 0: 250, w* = 1: 54; H3a censored per regime [0, 0, 0]; V3 CP valid-prediction time 0.4667 LT (reported).

**hindmarsh_rose** (DEVELOPMENT (DEV-3): not a hypothesis test; commit 392a069)

Gate: FAIL V7 -> PROVISIONAL. Stored V7: median δ/(ρν) by ρ 0.005: 67.91, 0.01: 52.46, 0.02: 32.46, 0.05: 17.2 (band [0.9, 1.1]); median slope 0.4054 (slope_pass False).

| Part | Estimate | Interval (level 0.9833) | Pass band | Stored part word |
|---|---|---|---|---|
| H2a(i) median range of w* | 0.09542 | [0.0642, 0.1828] | upper < 0.1 | inconclusive |
| H2a(ii) zero, partial corr. | -0.004176 | [-0.08196, 0.07904] | inside (-0.1, 0.1) | pass |
| H2a(ii) interior, partial corr. | -0.07718 | [-0.1709, 0.0202] | inside (-0.1, 0.1) | inconclusive |
| H2b(i) Spearman w* with rho | -0.05458 | [-0.108, -0.00137] | lower > 0 | fail |
| H2b(ii) library change of w* | 0.01784 | [-0.007791, 0.04557] | lower > 0 | inconclusive |
| H3c MSE ratio A5/A4 | 0.806 | [0.7164, 0.894] | upper <= 1.05 | pass |

Per-system words (verdicts/<H>/by_system/hindmarsh_rose): H2a inconclusive; H2b fail; H3c pass (primaries); H1a fail; H1b fail; H1c fail; H1d fail; H2c fail; H2d fail; H2e inconclusive; H3a inconclusive; H3b inconclusive; Q-N reduces (secondaries).
Counts: H2a eligible 132 / excluded 868 of 1000; w* = 0: 53, w* = 1: 201; H3a censored per regime [0, 0, 0]; V3 CP valid-prediction time 0.8667 LT (reported).

**hyper_jha** (DEVELOPMENT (DEV-3): not a hypothesis test; commit 392a069)

Gate: FAIL V7 -> PROVISIONAL. Stored V7: median δ/(ρν) by ρ 0.005: 1.029, 0.01: 1.041, 0.02: 1.081, 0.05: 3.376 (band [0.9, 1.1]); median slope 1.005 (slope_pass True).

| Part | Estimate | Interval (level 0.9833) | Pass band | Stored part word |
|---|---|---|---|---|
| H2a(i) median range of w* | 0.261 | [0.1732, 0.3874] | upper < 0.1 | fail |
| H2a(ii) zero, partial corr. | -0.04939 | [-0.1132, 0.02276] | inside (-0.1, 0.1) | inconclusive |
| H2a(ii) interior, partial corr. | 0.2785 | [0.1753, 0.3773] | inside (-0.1, 0.1) | fail |
| H2b(i) Spearman w* with rho | 0.4433 | [0.398, 0.4858] | lower > 0 | pass |
| H2b(ii) library change of w* | 0.04383 | [0.01546, 0.06929] | lower > 0 | pass |
| H3c MSE ratio A5/A4 | 0.8411 | [0.8, 0.8962] | upper <= 1.05 | pass |

Per-system words (verdicts/<H>/by_system/hyper_jha): H2a fail; H2b pass; H3c pass (primaries); H1a inconclusive; H1b fail; H1c fail; H1d fail; H2c fail; H2d inconclusive; H2e fail; H3a pass; H3b fail; Q-N reduces (secondaries).
Counts: H2a eligible 101 / excluded 899 of 1000; w* = 0: 242, w* = 1: 89; H3a censored per regime [0, 0]; V3 CP valid-prediction time 0.3667 LT (reported).

**lorenz96_4** (DEVELOPMENT (DEV-3): not a hypothesis test; commit 392a069)

Gate: FAIL V7 -> PROVISIONAL. Stored V7: median δ/(ρν) by ρ 0.005: 1.023, 0.01: 1.037, 0.02: 1.094, 0.05: 2.753 (band [0.9, 1.1]); median slope 1.011 (slope_pass True).

| Part | Estimate | Interval (level 0.9833) | Pass band | Stored part word |
|---|---|---|---|---|
| H2a(i) median range of w* | 0.2787 | [0.1978, 0.3493] | upper < 0.1 | fail |
| H2a(ii) zero, partial corr. | -0.04372 | [-0.1177, 0.02958] | inside (-0.1, 0.1) | inconclusive |
| H2a(ii) interior, partial corr. | 0.1162 | [0.02352, 0.2093] | inside (-0.1, 0.1) | inconclusive |
| H2b(i) Spearman w* with rho | 0.4805 | [0.4318, 0.5254] | lower > 0 | pass |
| H2b(ii) library change of w* | 0.1283 | [0.1004, 0.1554] | lower > 0 | pass |
| H3c MSE ratio A5/A4 | 0.7802 | [0.7142, 0.8633] | upper <= 1.05 | pass |

Per-system words (verdicts/<H>/by_system/lorenz96_4): H2a fail; H2b pass; H3c pass (primaries); H1a inconclusive; H1b fail; H1c inconclusive; H1d fail; H2c fail; H2d inconclusive; H2e inconclusive; H3a pass; H3b fail; Q-N substantial (secondaries).
Counts: H2a eligible 313 / excluded 687 of 1000; w* = 0: 178, w* = 1: 88; H3a censored per regime [0, 0]; V3 CP valid-prediction time 0.9 LT (reported).

### Frozen systems in the development ensemble

**lorenz63** (DEV-1 | DEV-3 | DEV-4; gate PASS on all three seeds)

| Part | DEV-1 estimate [interval] word | DEV-3 | DEV-4 |
|---|---|---|---|
| H2a(i) median range of w* | 0.09618 [0.07453, 0.1172] inconclusive | 0.1269 [0.09376, 0.1533] inconclusive | 0.09938 [0.08136, 0.1205] inconclusive |
| H2a(ii) zero, partial corr. | 0.02441 [-0.04988, 0.09939] pass | -0.05012 [-0.1172, 0.03021] inconclusive | 0.04332 [-0.03229, 0.1167] inconclusive |
| H2a(ii) interior, partial corr. | 0.1372 [0.04383, 0.2322] inconclusive | 0.173 [0.07993, 0.2721] inconclusive | 0.156 [0.04334, 0.2661] inconclusive |
| H2b(i) Spearman w* with rho | 0.2352 [0.1886, 0.2783] pass | 0.2471 [0.1978, 0.2934] pass | 0.2587 [0.2109, 0.307] pass |
| H2b(ii) library change of w* | 0.07039 [0.05001, 0.09156] pass | 0.05911 [0.03659, 0.08476] pass | 0.06757 [0.0452, 0.08875] pass |
| H3c MSE ratio A5/A4 | 0.7105 [0.5271, 0.8958] pass | 0.7939 [0.5886, 1.125] inconclusive | 0.9983 [0.8118, 1.239] inconclusive |

**rossler** (DEV-1 | DEV-3 | DEV-4; gate PASS on all three seeds)

| Part | DEV-1 estimate [interval] word | DEV-3 | DEV-4 |
|---|---|---|---|
| H2a(i) median range of w* | 0.2631 [0.2332, 0.3068] fail | 0.2763 [0.239, 0.309] fail | 0.2744 [0.2486, 0.3056] fail |
| H2a(ii) zero, partial corr. | -0.04123 [-0.1223, 0.04559] inconclusive | -0.02326 [-0.1094, 0.06864] inconclusive | -0.04614 [-0.1226, 0.02963] inconclusive |
| H2a(ii) interior, partial corr. | -0.0202 [-0.1167, 0.07393] inconclusive | -0.0558 [-0.1629, 0.04628] inconclusive | 0.06591 [-0.01515, 0.1538] inconclusive |
| H2b(i) Spearman w* with rho | 0.1141 [0.06475, 0.1677] pass | 0.1987 [0.1468, 0.2507] pass | 0.2331 [0.1848, 0.283] pass |
| H2b(ii) library change of w* | 0.06492 [0.04269, 0.08973] pass | 0.05353 [0.0288, 0.07507] pass | 0.05443 [0.03018, 0.07794] pass |
| H3c MSE ratio A5/A4 | 0.9685 [0.9224, 1.014] pass | 0.9897 [0.9457, 1.035] pass | 0.9507 [0.9083, 0.9906] pass |

**chua** (DEV-1 | DEV-3 | DEV-4; gate PASS on all three seeds)

| Part | DEV-1 estimate [interval] word | DEV-3 | DEV-4 |
|---|---|---|---|
| H2a(i) median range of w* | 0.1648 [0.1277, 0.1973] fail | 0.1882 [0.1474, 0.2237] fail | 0.1727 [0.1462, 0.2052] fail |
| H2a(ii) zero, partial corr. | -0.01555 [-0.0925, 0.067] pass | -0.06327 [-0.1434, 0.01502] inconclusive | -0.04581 [-0.1214, 0.02915] inconclusive |
| H2a(ii) interior, partial corr. | 0.1926 [0.08444, 0.2922] inconclusive | 0.144 [0.04015, 0.251] inconclusive | 0.2235 [0.1327, 0.3164] fail |
| H2b(i) Spearman w* with rho | 0.2298 [0.174, 0.279] pass | 0.2459 [0.1961, 0.2996] pass | 0.259 [0.2093, 0.3103] pass |
| H2b(ii) library change of w* | 0.05757 [0.03504, 0.07962] pass | 0.04154 [0.01525, 0.06636] pass | 0.02235 [-0.00507, 0.0472] inconclusive |
| H3c MSE ratio A5/A4 | 0.9533 [0.9026, 1.001] pass | 1.054 [0.9794, 1.157] inconclusive | 1.025 [0.9513, 1.089] inconclusive |

