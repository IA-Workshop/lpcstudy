## Runs

| run | seed | device | wall s | exit | commit | dirty | complete | promoted | failed var. | skipped var. | robustness | label |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ens-DEV-1 | DEV-1 | gpu (NVIDIA GeForce RTX 4090) | 2777 | 0 | 3dec086 | False | True | False | 0 | 0 | run | DEVELOPMENT (DEV-1): not a hypothesis test |
| ens-DEV-3 | DEV-3 | gpu (NVIDIA GeForce RTX 4090) | 2450 | 0 | 3dec086 | False | True | False | 0 | 0 | run | DEVELOPMENT (DEV-3): not a hypothesis test |
| ens-DEV-4 | DEV-4 | gpu (NVIDIA GeForce RTX 4090) | 2319 | 0 | 3dec086 | False | True | False | 0 | 0 | run | DEVELOPMENT (DEV-4): not a hypothesis test |
| ext-rossler_hyper | DEV-3 | gpu (NVIDIA GeForce RTX 4090) | 2835 | 0 | 974519a | False | True | False | 0 | 0 | skipped | DEVELOPMENT (DEV-3): not a hypothesis test |
| ext-lorenz63_r166 | DEV-3 | gpu (NVIDIA GeForce RTX 4090) | 2723 | 0 | 974519a | False | True | False | 0 | 0 | skipped | DEVELOPMENT (DEV-3): not a hypothesis test |
| ext-rossler_z | DEV-3 | gpu (NVIDIA GeForce RTX 4090) | 906 | 0 | 974519a | False | True | False | 0 | 0 | skipped | DEVELOPMENT (DEV-3): not a hypothesis test |
| ext-hindmarsh_rose | DEV-3 | gpu (NVIDIA GeForce RTX 4090) | 5169 | 0 | 392a069 | False | True | False | 0 | 0 | skipped | DEVELOPMENT (DEV-3): not a hypothesis test |
| ext-hyper_jha | DEV-3 | gpu (NVIDIA GeForce RTX 4090) | 4042 | 0 | 392a069 | False | True | False | 0 | 0 | skipped | DEVELOPMENT (DEV-3): not a hypothesis test |
| ext-lorenz96_4 | DEV-3 | gpu (NVIDIA GeForce RTX 4090) | 1304 | 0 | 392a069 | False | True | False | 0 | 0 | skipped | DEVELOPMENT (DEV-3): not a hypothesis test |

## Gate

| run | system | V1 | V2 | V4 | V5 | V6 | V7 | V3 (LT, reported) | gate | V7 stored numbers |
|---|---|---|---|---|---|---|---|---|---|---|
| ens-DEV-1 | lorenz63 | pass | pass | pass | pass | pass | pass | 2 | PASS | slope 1.001 [1.001, 1.001] (pass True); median δ/(ρν) 0.005: 1.002, 0.01: 1.003, 0.02: 1.006, 0.05: 1.013; n_nonfinite 0 |
| ens-DEV-1 | rossler | pass | pass | pass | pass | pass | pass | 3.3 | PASS | slope 1 [1, 1] (pass True); median δ/(ρν) 0.005: 0.999, 0.01: 0.9993, 0.02: 0.9994, 0.05: 1.002; n_nonfinite 0 |
| ens-DEV-1 | chua | pass | pass | pass | pass | pass | pass | 2.9 | PASS | slope 1 [1, 1.001] (pass True); median δ/(ρν) 0.005: 0.9976, 0.01: 0.9975, 0.02: 0.9989, 0.05: 1.002; n_nonfinite 0 |
| ens-DEV-3 | lorenz63 | pass | pass | pass | pass | pass | pass | 2.033 | PASS | slope 1.001 [1.001, 1.001] (pass True); median δ/(ρν) 0.005: 1, 0.01: 1.002, 0.02: 1.004, 0.05: 1.009; n_nonfinite 0 |
| ens-DEV-3 | rossler | pass | pass | pass | pass | pass | pass | 3.133 | PASS | slope 1 [1, 1] (pass True); median δ/(ρν) 0.005: 0.9986, 0.01: 0.9986, 0.02: 0.9997, 0.05: 1.001; n_nonfinite 0 |
| ens-DEV-3 | chua | pass | pass | pass | pass | pass | pass | 2.9 | PASS | slope 1 [1, 1] (pass True); median δ/(ρν) 0.005: 1, 0.01: 1, 0.02: 1.001, 0.05: 1.003; n_nonfinite 0 |
| ens-DEV-4 | lorenz63 | pass | pass | pass | pass | pass | pass | 2.033 | PASS | slope 1.001 [1.001, 1.001] (pass True); median δ/(ρν) 0.005: 1.001, 0.01: 1.003, 0.02: 1.004, 0.05: 1.012; n_nonfinite 0 |
| ens-DEV-4 | rossler | pass | pass | pass | pass | pass | pass | 3.233 | PASS | slope 1 [1, 1] (pass True); median δ/(ρν) 0.005: 0.9983, 0.01: 0.9979, 0.02: 0.9988, 0.05: 1; n_nonfinite 0 |
| ens-DEV-4 | chua | pass | pass | pass | pass | pass | pass | 2.967 | PASS | slope 1 [1, 1] (pass True); median δ/(ρν) 0.005: 0.9986, 0.01: 0.9993, 0.02: 1, 0.05: 1.001; n_nonfinite 0 |
| rossler_hyper | rossler_hyper | pass | pass | pass | pass | pass | pass | 1.567 | PASS | slope 1 [1, 1.001] (pass True); median δ/(ρν) 0.005: 1.005, 0.01: 1.006, 0.02: 1.007, 0.05: 1.013; n_nonfinite 0 |
| lorenz63_r166 | lorenz63_r166 | pass | pass | pass | pass | pass | FAIL | 3.367 | FAIL -> PROVISIONAL | slope 0.9268 [0.7922, 0.9792] (pass True); median δ/(ρν) 0.005: 1.111, 0.01: 25.98, 0.02: 16.42, 0.05: 11.25; n_nonfinite 0 |
| rossler_z | rossler_z | pass | pass | pass | pass | pass | FAIL | 0.4667 | FAIL -> PROVISIONAL | slope 0.8718 [0.8308, 0.9017] (pass False); median δ/(ρν) 0.005: 1.025, 0.01: 1.07, 0.02: 1.111, 0.05: 0.9378; n_nonfinite 0 |
| hindmarsh_rose | hindmarsh_rose | pass | pass | pass | pass | pass | FAIL | 0.8667 | FAIL -> PROVISIONAL | slope 0.4054 [0.354, 0.4957] (pass False); median δ/(ρν) 0.005: 67.91, 0.01: 52.46, 0.02: 32.46, 0.05: 17.2; n_nonfinite 0 |
| hyper_jha | hyper_jha | pass | pass | pass | pass | pass | FAIL | 0.3667 | FAIL -> PROVISIONAL | slope 1.005 [1.002, 1.008] (pass True); median δ/(ρν) 0.005: 1.029, 0.01: 1.041, 0.02: 1.081, 0.05: 3.376; n_nonfinite 0 |
| lorenz96_4 | lorenz96_4 | pass | pass | pass | pass | pass | FAIL | 0.9 | FAIL -> PROVISIONAL | slope 1.011 [1.007, 1.02] (pass True); median δ/(ρν) 0.005: 1.023, 0.01: 1.037, 0.02: 1.094, 0.05: 2.753; n_nonfinite 0 |

## lambda_max (stored)

DEV-1
- lorenz63: 0.9057
- rossler: 0.07172
- chua: 0.4409
DEV-3
- lorenz63: 0.9057
- rossler: 0.07172
- chua: 0.4409
DEV-4
- lorenz63: 0.9057
- rossler: 0.07172
- chua: 0.4409
rossler_hyper
- rossler_hyper: 0.1127
lorenz63_r166
- lorenz63_r166: 0.6224
rossler_z
- rossler_z: 0.07165
hindmarsh_rose
- hindmarsh_rose: 0.2168
hyper_jha
- hyper_jha: 0.3596
lorenz96_4
- lorenz96_4: 1.196

## Words: ensemble

| Hypothesis | ens-DEV-1:lorenz63 | ens-DEV-1:rossler | ens-DEV-1:chua | ens-DEV-3:lorenz63 | ens-DEV-3:rossler | ens-DEV-3:chua | ens-DEV-4:lorenz63 | ens-DEV-4:rossler | ens-DEV-4:chua |
|---|---|---|---|---|---|---|---|---|---|
| H2a | inconclusive | fail | fail | inconclusive | fail | fail | inconclusive | fail | fail |
| H2b | pass | pass | pass | pass | pass | pass | pass | pass | inconclusive |
| H3c | pass | pass | pass | inconclusive | pass | inconclusive | inconclusive | pass | inconclusive |
| H1a | inconclusive | pass | pass | inconclusive | pass | pass | pass | pass | inconclusive |
| H1b | pass | fail | pass | pass | fail | pass | inconclusive | fail | pass |
| H1c | fail | pass | fail | fail | pass | fail | fail | pass | fail |
| H1d | pass | pass | inconclusive | inconclusive | pass | inconclusive | pass | pass | inconclusive |
| H2c | fail | inconclusive | fail | fail | inconclusive | inconclusive | inconclusive | fail | inconclusive |
| H2d | fail | pass | pass | fail | pass | pass | inconclusive | pass | pass |
| H2e | pass | pass | pass | pass | pass | pass | pass | pass | pass |
| H3a | inconclusive | inconclusive | pass | inconclusive | inconclusive | pass | inconclusive | inconclusive | inconclusive |
| H3b | inconclusive | inconclusive | inconclusive | inconclusive | pass | inconclusive | fail | pass | inconclusive |
| Q-N | reduces | reduces | undetermined | reduces | reduces | undetermined | substantial | undetermined | reduces |
| gain_bound | reported | reported | reported | reported | reported | reported | reported | reported | reported |

## Words: extension

| Hypothesis | rossler_hyper:rossler_hyper | lorenz63_r166:lorenz63_r166 | rossler_z:rossler_z | hindmarsh_rose:hindmarsh_rose | hyper_jha:hyper_jha | lorenz96_4:lorenz96_4 |
|---|---|---|---|---|---|---|
| H2a | fail | fail | fail | inconclusive | fail | fail |
| H2b | pass | inconclusive | fail | fail | pass | pass |
| H3c | inconclusive | pass | pass | pass | pass | pass |
| H1a | pass | fail | fail | fail | inconclusive | inconclusive |
| H1b | fail | fail | pass | fail | fail | fail |
| H1c | pass | fail | fail | fail | fail | inconclusive |
| H1d | pass | fail | fail | fail | fail | fail |
| H2c | inconclusive | fail | inconclusive | fail | fail | fail |
| H2d | inconclusive | inconclusive | pass | fail | inconclusive | inconclusive |
| H2e | pass | inconclusive | pass | inconclusive | fail | inconclusive |
| H3a | pass | pass | inconclusive | inconclusive | pass | pass |
| H3b | fail | fail | fail | inconclusive | fail | fail |
| Q-N | reduces | reduces | reduces | reduces | reduces | substantial |
| gain_bound | reported | reported | reported | reported | reported | reported |

## Primary intervals

| run | system | part | estimate | interval | level | word | reason | counts | leaf |
|---|---|---|---|---|---|---|---|---|---|
| ens-DEV-1 | lorenz63 | H2a(i) | 0.09618 | [0.07453, 0.1172] | 0.9833 (design value, not stored) | inconclusive | interval meets band edge | n_eligible 689, n_excluded 311 | systems/lorenz63/H2a/median_range, range_ci, part_i_verdict |
| ens-DEV-1 | lorenz63 | H2a(ii) zero | 0.02441 | [-0.04988, 0.09939] | 0.9833 (design value, not stored) | pass | None | n 1000 | systems/lorenz63/H2a/part_ii/zero/{partial_corr,ci,verdict} |
| ens-DEV-1 | lorenz63 | H2a(ii) interior | 0.1372 | [0.04383, 0.2322] | 0.9833 (design value, not stored) | inconclusive | interval meets band edge | n 675 | systems/lorenz63/H2a/part_ii/interior/{partial_corr,ci,verdict} |
| ens-DEV-1 | lorenz63 | H2b(i) noise | 0.2352 | [0.1886, 0.2783] | 0.9833 (design value, not stored) | pass | None | n_constant 67 | systems/lorenz63/H2b/noise/{mean_state_spearman,ci,verdict} |
| ens-DEV-1 | lorenz63 | H2b(ii) library | 0.07039 | [0.05001, 0.09156] | 0.9833 | pass | None | n 1000, zero-diff 143 | systems/lorenz63/H2b/library_change/{mean_change,ci,level,verdict} |
| ens-DEV-1 | lorenz63 | H3c | 0.7105 | [0.5271, 0.8958] | 0.9833 | pass | None | n 1000 | systems/lorenz63/H3c/{A5_over_A4_mse,ci,level,verdict} |
| ens-DEV-1 | rossler | H2a(i) | 0.2631 | [0.2332, 0.3068] | 0.9833 (design value, not stored) | fail | None | n_eligible 924, n_excluded 76 | systems/rossler/H2a/median_range, range_ci, part_i_verdict |
| ens-DEV-1 | rossler | H2a(ii) zero | -0.04123 | [-0.1223, 0.04559] | 0.9833 (design value, not stored) | inconclusive | interval meets band edge | n 1000 | systems/rossler/H2a/part_ii/zero/{partial_corr,ci,verdict} |
| ens-DEV-1 | rossler | H2a(ii) interior | -0.0202 | [-0.1167, 0.07393] | 0.9833 (design value, not stored) | inconclusive | interval meets band edge | n 713 | systems/rossler/H2a/part_ii/interior/{partial_corr,ci,verdict} |
| ens-DEV-1 | rossler | H2b(i) noise | 0.1141 | [0.06475, 0.1677] | 0.9833 (design value, not stored) | pass | None | n_constant 80 | systems/rossler/H2b/noise/{mean_state_spearman,ci,verdict} |
| ens-DEV-1 | rossler | H2b(ii) library | 0.06492 | [0.04269, 0.08973] | 0.9833 | pass | None | n 1000, zero-diff 96 | systems/rossler/H2b/library_change/{mean_change,ci,level,verdict} |
| ens-DEV-1 | rossler | H3c | 0.9685 | [0.9224, 1.014] | 0.9833 | pass | None | n 1000 | systems/rossler/H3c/{A5_over_A4_mse,ci,level,verdict} |
| ens-DEV-1 | chua | H2a(i) | 0.1648 | [0.1277, 0.1973] | 0.9833 (design value, not stored) | fail | None | n_eligible 684, n_excluded 316 | systems/chua/H2a/median_range, range_ci, part_i_verdict |
| ens-DEV-1 | chua | H2a(ii) zero | -0.01555 | [-0.0925, 0.067] | 0.9833 (design value, not stored) | pass | None | n 1000 | systems/chua/H2a/part_ii/zero/{partial_corr,ci,verdict} |
| ens-DEV-1 | chua | H2a(ii) interior | 0.1926 | [0.08444, 0.2922] | 0.9833 (design value, not stored) | inconclusive | interval meets band edge | n 701 | systems/chua/H2a/part_ii/interior/{partial_corr,ci,verdict} |
| ens-DEV-1 | chua | H2b(i) noise | 0.2298 | [0.174, 0.279] | 0.9833 (design value, not stored) | pass | None | n_constant 39 | systems/chua/H2b/noise/{mean_state_spearman,ci,verdict} |
| ens-DEV-1 | chua | H2b(ii) library | 0.05757 | [0.03504, 0.07962] | 0.9833 | pass | None | n 1000, zero-diff 142 | systems/chua/H2b/library_change/{mean_change,ci,level,verdict} |
| ens-DEV-1 | chua | H3c | 0.9533 | [0.9026, 1.001] | 0.9833 | pass | None | n 1000 | systems/chua/H3c/{A5_over_A4_mse,ci,level,verdict} |
| ens-DEV-3 | lorenz63 | H2a(i) | 0.1269 | [0.09376, 0.1533] | 0.9833 (design value, not stored) | inconclusive | interval meets band edge | n_eligible 669, n_excluded 331 | systems/lorenz63/H2a/median_range, range_ci, part_i_verdict |
| ens-DEV-3 | lorenz63 | H2a(ii) zero | -0.05012 | [-0.1172, 0.03021] | 0.9833 (design value, not stored) | inconclusive | interval meets band edge | n 1000 | systems/lorenz63/H2a/part_ii/zero/{partial_corr,ci,verdict} |
| ens-DEV-3 | lorenz63 | H2a(ii) interior | 0.173 | [0.07993, 0.2721] | 0.9833 (design value, not stored) | inconclusive | interval meets band edge | n 698 | systems/lorenz63/H2a/part_ii/interior/{partial_corr,ci,verdict} |
| ens-DEV-3 | lorenz63 | H2b(i) noise | 0.2471 | [0.1978, 0.2934] | 0.9833 (design value, not stored) | pass | None | n_constant 63 | systems/lorenz63/H2b/noise/{mean_state_spearman,ci,verdict} |
| ens-DEV-3 | lorenz63 | H2b(ii) library | 0.05911 | [0.03659, 0.08476] | 0.9833 | pass | None | n 1000, zero-diff 152 | systems/lorenz63/H2b/library_change/{mean_change,ci,level,verdict} |
| ens-DEV-3 | lorenz63 | H3c | 0.7939 | [0.5886, 1.125] | 0.9833 | inconclusive | interval meets band edge | n 1000 | systems/lorenz63/H3c/{A5_over_A4_mse,ci,level,verdict} |
| ens-DEV-3 | rossler | H2a(i) | 0.2763 | [0.239, 0.309] | 0.9833 (design value, not stored) | fail | None | n_eligible 916, n_excluded 84 | systems/rossler/H2a/median_range, range_ci, part_i_verdict |
| ens-DEV-3 | rossler | H2a(ii) zero | -0.02326 | [-0.1094, 0.06864] | 0.9833 (design value, not stored) | inconclusive | interval meets band edge | n 1000 | systems/rossler/H2a/part_ii/zero/{partial_corr,ci,verdict} |
| ens-DEV-3 | rossler | H2a(ii) interior | -0.0558 | [-0.1629, 0.04628] | 0.9833 (design value, not stored) | inconclusive | interval meets band edge | n 734 | systems/rossler/H2a/part_ii/interior/{partial_corr,ci,verdict} |
| ens-DEV-3 | rossler | H2b(i) noise | 0.1987 | [0.1468, 0.2507] | 0.9833 (design value, not stored) | pass | None | n_constant 63 | systems/rossler/H2b/noise/{mean_state_spearman,ci,verdict} |
| ens-DEV-3 | rossler | H2b(ii) library | 0.05353 | [0.0288, 0.07507] | 0.9833 | pass | None | n 1000, zero-diff 102 | systems/rossler/H2b/library_change/{mean_change,ci,level,verdict} |
| ens-DEV-3 | rossler | H3c | 0.9897 | [0.9457, 1.035] | 0.9833 | pass | None | n 1000 | systems/rossler/H3c/{A5_over_A4_mse,ci,level,verdict} |
| ens-DEV-3 | chua | H2a(i) | 0.1882 | [0.1474, 0.2237] | 0.9833 (design value, not stored) | fail | None | n_eligible 662, n_excluded 338 | systems/chua/H2a/median_range, range_ci, part_i_verdict |
| ens-DEV-3 | chua | H2a(ii) zero | -0.06327 | [-0.1434, 0.01502] | 0.9833 (design value, not stored) | inconclusive | interval meets band edge | n 1000 | systems/chua/H2a/part_ii/zero/{partial_corr,ci,verdict} |
| ens-DEV-3 | chua | H2a(ii) interior | 0.144 | [0.04015, 0.251] | 0.9833 (design value, not stored) | inconclusive | interval meets band edge | n 711 | systems/chua/H2a/part_ii/interior/{partial_corr,ci,verdict} |
| ens-DEV-3 | chua | H2b(i) noise | 0.2459 | [0.1961, 0.2996] | 0.9833 (design value, not stored) | pass | None | n_constant 45 | systems/chua/H2b/noise/{mean_state_spearman,ci,verdict} |
| ens-DEV-3 | chua | H2b(ii) library | 0.04154 | [0.01525, 0.06636] | 0.9833 | pass | None | n 1000, zero-diff 121 | systems/chua/H2b/library_change/{mean_change,ci,level,verdict} |
| ens-DEV-3 | chua | H3c | 1.054 | [0.9794, 1.157] | 0.9833 | inconclusive | interval meets band edge | n 1000 | systems/chua/H3c/{A5_over_A4_mse,ci,level,verdict} |
| ens-DEV-4 | lorenz63 | H2a(i) | 0.09938 | [0.08136, 0.1205] | 0.9833 (design value, not stored) | inconclusive | interval meets band edge | n_eligible 669, n_excluded 331 | systems/lorenz63/H2a/median_range, range_ci, part_i_verdict |
| ens-DEV-4 | lorenz63 | H2a(ii) zero | 0.04332 | [-0.03229, 0.1167] | 0.9833 (design value, not stored) | inconclusive | interval meets band edge | n 1000 | systems/lorenz63/H2a/part_ii/zero/{partial_corr,ci,verdict} |
| ens-DEV-4 | lorenz63 | H2a(ii) interior | 0.156 | [0.04334, 0.2661] | 0.9833 (design value, not stored) | inconclusive | interval meets band edge | n 687 | systems/lorenz63/H2a/part_ii/interior/{partial_corr,ci,verdict} |
| ens-DEV-4 | lorenz63 | H2b(i) noise | 0.2587 | [0.2109, 0.307] | 0.9833 (design value, not stored) | pass | None | n_constant 67 | systems/lorenz63/H2b/noise/{mean_state_spearman,ci,verdict} |
| ens-DEV-4 | lorenz63 | H2b(ii) library | 0.06757 | [0.0452, 0.08875] | 0.9833 | pass | None | n 1000, zero-diff 161 | systems/lorenz63/H2b/library_change/{mean_change,ci,level,verdict} |
| ens-DEV-4 | lorenz63 | H3c | 0.9983 | [0.8118, 1.239] | 0.9833 | inconclusive | interval meets band edge | n 1000 | systems/lorenz63/H3c/{A5_over_A4_mse,ci,level,verdict} |
| ens-DEV-4 | rossler | H2a(i) | 0.2744 | [0.2486, 0.3056] | 0.9833 (design value, not stored) | fail | None | n_eligible 923, n_excluded 77 | systems/rossler/H2a/median_range, range_ci, part_i_verdict |
| ens-DEV-4 | rossler | H2a(ii) zero | -0.04614 | [-0.1226, 0.02963] | 0.9833 (design value, not stored) | inconclusive | interval meets band edge | n 1000 | systems/rossler/H2a/part_ii/zero/{partial_corr,ci,verdict} |
| ens-DEV-4 | rossler | H2a(ii) interior | 0.06591 | [-0.01515, 0.1538] | 0.9833 (design value, not stored) | inconclusive | interval meets band edge | n 698 | systems/rossler/H2a/part_ii/interior/{partial_corr,ci,verdict} |
| ens-DEV-4 | rossler | H2b(i) noise | 0.2331 | [0.1848, 0.283] | 0.9833 (design value, not stored) | pass | None | n_constant 60 | systems/rossler/H2b/noise/{mean_state_spearman,ci,verdict} |
| ens-DEV-4 | rossler | H2b(ii) library | 0.05443 | [0.03018, 0.07794] | 0.9833 | pass | None | n 1000, zero-diff 125 | systems/rossler/H2b/library_change/{mean_change,ci,level,verdict} |
| ens-DEV-4 | rossler | H3c | 0.9507 | [0.9083, 0.9906] | 0.9833 | pass | None | n 1000 | systems/rossler/H3c/{A5_over_A4_mse,ci,level,verdict} |
| ens-DEV-4 | chua | H2a(i) | 0.1727 | [0.1462, 0.2052] | 0.9833 (design value, not stored) | fail | None | n_eligible 679, n_excluded 321 | systems/chua/H2a/median_range, range_ci, part_i_verdict |
| ens-DEV-4 | chua | H2a(ii) zero | -0.04581 | [-0.1214, 0.02915] | 0.9833 (design value, not stored) | inconclusive | interval meets band edge | n 1000 | systems/chua/H2a/part_ii/zero/{partial_corr,ci,verdict} |
| ens-DEV-4 | chua | H2a(ii) interior | 0.2235 | [0.1327, 0.3164] | 0.9833 (design value, not stored) | fail | None | n 699 | systems/chua/H2a/part_ii/interior/{partial_corr,ci,verdict} |
| ens-DEV-4 | chua | H2b(i) noise | 0.259 | [0.2093, 0.3103] | 0.9833 (design value, not stored) | pass | None | n_constant 46 | systems/chua/H2b/noise/{mean_state_spearman,ci,verdict} |
| ens-DEV-4 | chua | H2b(ii) library | 0.02235 | [-0.00507, 0.0472] | 0.9833 | inconclusive | interval meets band edge | n 1000, zero-diff 119 | systems/chua/H2b/library_change/{mean_change,ci,level,verdict} |
| ens-DEV-4 | chua | H3c | 1.025 | [0.9513, 1.089] | 0.9833 | inconclusive | interval meets band edge | n 1000 | systems/chua/H3c/{A5_over_A4_mse,ci,level,verdict} |
| rossler_hyper | rossler_hyper | H2a(i) | 0.1945 | [0.1479, 0.2458] | 0.9833 (design value, not stored) | fail | None | n_eligible 580, n_excluded 420 | systems/rossler_hyper/H2a/median_range, range_ci, part_i_verdict |
| rossler_hyper | rossler_hyper | H2a(ii) zero | -0.01999 | [-0.09713, 0.06449] | 0.9833 (design value, not stored) | pass | None | n 1000 | systems/rossler_hyper/H2a/part_ii/zero/{partial_corr,ci,verdict} |
| rossler_hyper | rossler_hyper | H2a(ii) interior | 0.02349 | [-0.06761, 0.1185] | 0.9833 (design value, not stored) | inconclusive | interval meets band edge | n 716 | systems/rossler_hyper/H2a/part_ii/interior/{partial_corr,ci,verdict} |
| rossler_hyper | rossler_hyper | H2b(i) noise | 0.4096 | [0.3653, 0.4556] | 0.9833 (design value, not stored) | pass | None | n_constant 86 | systems/rossler_hyper/H2b/noise/{mean_state_spearman,ci,verdict} |
| rossler_hyper | rossler_hyper | H2b(ii) library | 0.03182 | [0.01086, 0.05168] | 0.9833 | pass | None | n 1000, zero-diff 175 | systems/rossler_hyper/H2b/library_change/{mean_change,ci,level,verdict} |
| rossler_hyper | rossler_hyper | H3c | 0.3274 | [0.145, 4.504] | 0.9833 | inconclusive | interval meets band edge | n 1000 | systems/rossler_hyper/H3c/{A5_over_A4_mse,ci,level,verdict} |
| lorenz63_r166 | lorenz63_r166 | H2a(i) | 0.2362 | [0.1667, 0.3188] | 0.9833 (design value, not stored) | fail | None | n_eligible 395, n_excluded 605 | systems/lorenz63_r166/H2a/median_range, range_ci, part_i_verdict |
| lorenz63_r166 | lorenz63_r166 | H2a(ii) zero | 0.03787 | [-0.04573, 0.1085] | 0.9833 (design value, not stored) | inconclusive | interval meets band edge | n 1000 | systems/lorenz63_r166/H2a/part_ii/zero/{partial_corr,ci,verdict} |
| lorenz63_r166 | lorenz63_r166 | H2a(ii) interior | -0.1179 | [-0.2363, -0.01293] | 0.9833 (design value, not stored) | inconclusive | interval meets band edge | n 690 | systems/lorenz63_r166/H2a/part_ii/interior/{partial_corr,ci,verdict} |
| lorenz63_r166 | lorenz63_r166 | H2b(i) noise | 0.2334 | [0.181, 0.2817] | 0.9833 (design value, not stored) | pass | None | n_constant 43 | systems/lorenz63_r166/H2b/noise/{mean_state_spearman,ci,verdict} |
| lorenz63_r166 | lorenz63_r166 | H2b(ii) library | -0.008574 | [-0.03499, 0.01649] | 0.9833 | inconclusive | interval meets band edge | n 1000, zero-diff 148 | systems/lorenz63_r166/H2b/library_change/{mean_change,ci,level,verdict} |
| lorenz63_r166 | lorenz63_r166 | H3c | 0.8994 | [0.8365, 0.976] | 0.9833 | pass | None | n 1000 | systems/lorenz63_r166/H3c/{A5_over_A4_mse,ci,level,verdict} |
| rossler_z | rossler_z | H2a(i) | 0.2145 | [0.1833, 0.2584] | 0.9833 (design value, not stored) | fail | None | n_eligible 625, n_excluded 375 | systems/rossler_z/H2a/median_range, range_ci, part_i_verdict |
| rossler_z | rossler_z | H2a(ii) zero | 0.01603 | [-0.07028, 0.09484] | 0.9833 (design value, not stored) | pass | None | n 1000 | systems/rossler_z/H2a/part_ii/zero/{partial_corr,ci,verdict} |
| rossler_z | rossler_z | H2a(ii) interior | -0.1832 | [-0.2634, -0.08966] | 0.9833 (design value, not stored) | inconclusive | interval meets band edge | n 696 | systems/rossler_z/H2a/part_ii/interior/{partial_corr,ci,verdict} |
| rossler_z | rossler_z | H2b(i) noise | 0.1327 | [0.08508, 0.1877] | 0.9833 (design value, not stored) | pass | None | n_constant 63 | systems/rossler_z/H2b/noise/{mean_state_spearman,ci,verdict} |
| rossler_z | rossler_z | H2b(ii) library | -0.01982 | [-0.0409, -0.002553] | 0.9833 | fail | None | n 1000, zero-diff 166 | systems/rossler_z/H2b/library_change/{mean_change,ci,level,verdict} |
| rossler_z | rossler_z | H3c | 0.9242 | [0.839, 1.007] | 0.9833 | pass | None | n 1000 | systems/rossler_z/H3c/{A5_over_A4_mse,ci,level,verdict} |
| hindmarsh_rose | hindmarsh_rose | H2a(i) | 0.09542 | [0.0642, 0.1828] | 0.9833 (design value, not stored) | inconclusive | interval meets band edge | n_eligible 132, n_excluded 868 | systems/hindmarsh_rose/H2a/median_range, range_ci, part_i_verdict |
| hindmarsh_rose | hindmarsh_rose | H2a(ii) zero | -0.004176 | [-0.08196, 0.07904] | 0.9833 (design value, not stored) | pass | None | n 1000 | systems/hindmarsh_rose/H2a/part_ii/zero/{partial_corr,ci,verdict} |
| hindmarsh_rose | hindmarsh_rose | H2a(ii) interior | -0.07718 | [-0.1709, 0.0202] | 0.9833 (design value, not stored) | inconclusive | interval meets band edge | n 746 | systems/hindmarsh_rose/H2a/part_ii/interior/{partial_corr,ci,verdict} |
| hindmarsh_rose | hindmarsh_rose | H2b(i) noise | -0.05458 | [-0.108, -0.00137] | 0.9833 (design value, not stored) | fail | None | n_constant 53 | systems/hindmarsh_rose/H2b/noise/{mean_state_spearman,ci,verdict} |
| hindmarsh_rose | hindmarsh_rose | H2b(ii) library | 0.01784 | [-0.007791, 0.04557] | 0.9833 | inconclusive | interval meets band edge | n 1000, zero-diff 127 | systems/hindmarsh_rose/H2b/library_change/{mean_change,ci,level,verdict} |
| hindmarsh_rose | hindmarsh_rose | H3c | 0.806 | [0.7164, 0.894] | 0.9833 | pass | None | n 1000 | systems/hindmarsh_rose/H3c/{A5_over_A4_mse,ci,level,verdict} |
| hyper_jha | hyper_jha | H2a(i) | 0.261 | [0.1732, 0.3874] | 0.9833 (design value, not stored) | fail | None | n_eligible 101, n_excluded 899 | systems/hyper_jha/H2a/median_range, range_ci, part_i_verdict |
| hyper_jha | hyper_jha | H2a(ii) zero | -0.04939 | [-0.1132, 0.02276] | 0.9833 (design value, not stored) | inconclusive | interval meets band edge | n 1000 | systems/hyper_jha/H2a/part_ii/zero/{partial_corr,ci,verdict} |
| hyper_jha | hyper_jha | H2a(ii) interior | 0.2785 | [0.1753, 0.3773] | 0.9833 (design value, not stored) | fail | None | n 669 | systems/hyper_jha/H2a/part_ii/interior/{partial_corr,ci,verdict} |
| hyper_jha | hyper_jha | H2b(i) noise | 0.4433 | [0.398, 0.4858] | 0.9833 (design value, not stored) | pass | None | n_constant 86 | systems/hyper_jha/H2b/noise/{mean_state_spearman,ci,verdict} |
| hyper_jha | hyper_jha | H2b(ii) library | 0.04383 | [0.01546, 0.06929] | 0.9833 | pass | None | n 1000, zero-diff 226 | systems/hyper_jha/H2b/library_change/{mean_change,ci,level,verdict} |
| hyper_jha | hyper_jha | H3c | 0.8411 | [0.8, 0.8962] | 0.9833 | pass | None | n 1000 | systems/hyper_jha/H3c/{A5_over_A4_mse,ci,level,verdict} |
| lorenz96_4 | lorenz96_4 | H2a(i) | 0.2787 | [0.1978, 0.3493] | 0.9833 (design value, not stored) | fail | None | n_eligible 313, n_excluded 687 | systems/lorenz96_4/H2a/median_range, range_ci, part_i_verdict |
| lorenz96_4 | lorenz96_4 | H2a(ii) zero | -0.04372 | [-0.1177, 0.02958] | 0.9833 (design value, not stored) | inconclusive | interval meets band edge | n 1000 | systems/lorenz96_4/H2a/part_ii/zero/{partial_corr,ci,verdict} |
| lorenz96_4 | lorenz96_4 | H2a(ii) interior | 0.1162 | [0.02352, 0.2093] | 0.9833 (design value, not stored) | inconclusive | interval meets band edge | n 734 | systems/lorenz96_4/H2a/part_ii/interior/{partial_corr,ci,verdict} |
| lorenz96_4 | lorenz96_4 | H2b(i) noise | 0.4805 | [0.4318, 0.5254] | 0.9833 (design value, not stored) | pass | None | n_constant 39 | systems/lorenz96_4/H2b/noise/{mean_state_spearman,ci,verdict} |
| lorenz96_4 | lorenz96_4 | H2b(ii) library | 0.1283 | [0.1004, 0.1554] | 0.9833 | pass | None | n 1000, zero-diff 171 | systems/lorenz96_4/H2b/library_change/{mean_change,ci,level,verdict} |
| lorenz96_4 | lorenz96_4 | H3c | 0.7802 | [0.7142, 0.8633] | 0.9833 | pass | None | n 1000 | systems/lorenz96_4/H3c/{A5_over_A4_mse,ci,level,verdict} |

## Ensemble agreement

| Hypothesis | DEV-1 | DEV-3 | DEV-4 | agree |
|---|---|---|---|---|
| H2a | not supported | not supported | not supported | yes |
| H2b | supported | supported | inconclusive | NO |
| H3c | supported | inconclusive | inconclusive | NO |
| H1a | inconclusive | inconclusive | inconclusive | yes |
| H1b | not supported | not supported | not supported | yes |
| H1c | not supported | not supported | not supported | yes |
| H1d | inconclusive | inconclusive | inconclusive | yes |
| H2c | not supported | not supported | not supported | yes |
| H2d | not supported | not supported | inconclusive | NO |
| H2e | supported | supported | supported | yes |
| H3a | inconclusive | inconclusive | inconclusive | yes |
| H3b | inconclusive | inconclusive | not supported | NO |
| Q-N | estimate (read, no pass/fail) | estimate (read, no pass/fail) | estimate (read, no pass/fail) | yes |
| gain_bound | reported (no pass/fail) | reported (no pass/fail) | reported (no pass/fail) | yes |

Per-system words that differ across seeds (verdicts/<H>/by_system/<s>):
- H2b/chua: DEV-1 pass, DEV-3 pass, DEV-4 inconclusive
- H3c/lorenz63: DEV-1 pass, DEV-3 inconclusive, DEV-4 inconclusive
- H3c/chua: DEV-1 pass, DEV-3 inconclusive, DEV-4 inconclusive
- H1a/lorenz63: DEV-1 inconclusive, DEV-3 inconclusive, DEV-4 pass
- H1a/chua: DEV-1 pass, DEV-3 pass, DEV-4 inconclusive
- H1b/lorenz63: DEV-1 pass, DEV-3 pass, DEV-4 inconclusive
- H1d/lorenz63: DEV-1 pass, DEV-3 inconclusive, DEV-4 pass
- H2c/lorenz63: DEV-1 fail, DEV-3 fail, DEV-4 inconclusive
- H2c/rossler: DEV-1 inconclusive, DEV-3 inconclusive, DEV-4 fail
- H2c/chua: DEV-1 fail, DEV-3 inconclusive, DEV-4 inconclusive
- H2d/lorenz63: DEV-1 fail, DEV-3 fail, DEV-4 inconclusive
- H3a/chua: DEV-1 pass, DEV-3 pass, DEV-4 inconclusive
- H3b/lorenz63: DEV-1 inconclusive, DEV-3 inconclusive, DEV-4 fail
- H3b/rossler: DEV-1 inconclusive, DEV-3 pass, DEV-4 pass
- Q-N/lorenz63: DEV-1 reduces, DEV-3 reduces, DEV-4 substantial
- Q-N/rossler: DEV-1 reduces, DEV-3 reduces, DEV-4 undetermined
- Q-N/chua: DEV-1 undetermined, DEV-3 undetermined, DEV-4 reduces

Primary part-level words that differ across seeds:
- lorenz63 H2a(i): DEV-1 inconclusive, DEV-3 inconclusive, DEV-4 inconclusive
- lorenz63 H2a(ii) zero: DEV-1 pass, DEV-3 inconclusive, DEV-4 inconclusive  <- differs
- lorenz63 H2a(ii) interior: DEV-1 inconclusive, DEV-3 inconclusive, DEV-4 inconclusive
- lorenz63 H2b(i): DEV-1 pass, DEV-3 pass, DEV-4 pass
- lorenz63 H2b(ii): DEV-1 pass, DEV-3 pass, DEV-4 pass
- lorenz63 H3c: DEV-1 pass, DEV-3 inconclusive, DEV-4 inconclusive  <- differs
- rossler H2a(i): DEV-1 fail, DEV-3 fail, DEV-4 fail
- rossler H2a(ii) zero: DEV-1 inconclusive, DEV-3 inconclusive, DEV-4 inconclusive
- rossler H2a(ii) interior: DEV-1 inconclusive, DEV-3 inconclusive, DEV-4 inconclusive
- rossler H2b(i): DEV-1 pass, DEV-3 pass, DEV-4 pass
- rossler H2b(ii): DEV-1 pass, DEV-3 pass, DEV-4 pass
- rossler H3c: DEV-1 pass, DEV-3 pass, DEV-4 pass
- chua H2a(i): DEV-1 fail, DEV-3 fail, DEV-4 fail
- chua H2a(ii) zero: DEV-1 pass, DEV-3 inconclusive, DEV-4 inconclusive  <- differs
- chua H2a(ii) interior: DEV-1 inconclusive, DEV-3 inconclusive, DEV-4 fail  <- differs
- chua H2b(i): DEV-1 pass, DEV-3 pass, DEV-4 pass
- chua H2b(ii): DEV-1 pass, DEV-3 pass, DEV-4 inconclusive  <- differs
- chua H3c: DEV-1 pass, DEV-3 inconclusive, DEV-4 inconclusive  <- differs

## Extension words against frozen-system words (string membership only)

| Hypothesis | words on frozen systems (9 system-seed cells) | rossler_hyper | lorenz63_r166 | rossler_z | hindmarsh_rose | hyper_jha | lorenz96_4 |
|---|---|---|---|---|---|---|---|
| H2a | fail, inconclusive | fail | fail | fail | inconclusive | fail | fail |
| H2b | inconclusive, pass | pass | inconclusive | **fail** (not seen on frozen) | **fail** (not seen on frozen) | pass | pass |
| H3c | inconclusive, pass | inconclusive | pass | pass | pass | pass | pass |
| H1a | inconclusive, pass | pass | **fail** (not seen on frozen) | **fail** (not seen on frozen) | **fail** (not seen on frozen) | inconclusive | inconclusive |
| H1b | fail, inconclusive, pass | fail | fail | pass | fail | fail | fail |
| H1c | fail, pass | pass | fail | fail | fail | fail | **inconclusive** (not seen on frozen) |
| H1d | inconclusive, pass | pass | **fail** (not seen on frozen) | **fail** (not seen on frozen) | **fail** (not seen on frozen) | **fail** (not seen on frozen) | **fail** (not seen on frozen) |
| H2c | fail, inconclusive | inconclusive | fail | inconclusive | fail | fail | fail |
| H2d | fail, inconclusive, pass | inconclusive | inconclusive | pass | fail | inconclusive | inconclusive |
| H2e | pass | pass | **inconclusive** (not seen on frozen) | pass | **inconclusive** (not seen on frozen) | **fail** (not seen on frozen) | **inconclusive** (not seen on frozen) |
| H3a | inconclusive, pass | pass | pass | inconclusive | inconclusive | pass | pass |
| H3b | fail, inconclusive, pass | fail | fail | fail | inconclusive | fail | fail |
| Q-N | reduces, substantial, undetermined | reduces | reduces | reduces | reduces | reduces | substantial |
| gain_bound | reported | reported | reported | reported | reported | reported | reported |

## Exclusion, censoring and clip flags

| run | system | H2a eligible/excluded | H2a noncontiguous | H3a censored per regime | H3a KM not reached | H3a empty regimes | Q-N n w*=0 / w*=1 | H1c PLP states/ineligible | gain bound states/total | clip status | clip-sensitive hypotheses |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ens-DEV-1 | lorenz63 | 689/311 | 23 | [0, 0, 0, 0, 0, 0] | 0 | 0 | 302/23 | 832/168 | 670/1000 | computed | none |
| ens-DEV-1 | rossler | 924/76 | 61 | [0, 1, 0, 0] | 0 | 0 | 283/4 | 953/47 | 629/1000 | computed | none |
| ens-DEV-1 | chua | 684/316 | 11 | [5, 0] | 0 | 0 | 293/6 | 828/172 | 624/1000 | computed | none |
| ens-DEV-3 | lorenz63 | 669/331 | 18 | [0, 0, 0, 0, 0, 0, 0, 0] | 0 | 0 | 282/20 | 838/162 | 642/1000 | computed | none |
| ens-DEV-3 | rossler | 916/84 | 55 | [0, 0, 1, 0] | 0 | 0 | 263/3 | 946/54 | 656/1000 | computed | none |
| ens-DEV-3 | chua | 662/338 | 12 | [1, 2, 2] | 0 | 0 | 284/5 | 852/148 | 646/1000 | computed | none |
| ens-DEV-4 | lorenz63 | 669/331 | 24 | [0, 0, 0, 0, 0, 0, 0, 0] | 0 | 0 | 292/21 | 843/157 | 643/1000 | computed | none |
| ens-DEV-4 | rossler | 923/77 | 55 | [1, 0, 2] | 0 | 0 | 300/2 | 944/56 | 650/1000 | computed | none |
| ens-DEV-4 | chua | 679/321 | 7 | [3, 3, 0, 0] | 0 | 0 | 291/10 | 835/165 | 632/1000 | computed | none |
| rossler_hyper | rossler_hyper | 580/420 | 79 | [0, 0] | 0 | 0 | 272/12 | 966/34 | 557/1000 | computed | H2c, H1b, H2e |
| lorenz63_r166 | lorenz63_r166 | 395/605 | 40 | [4, 84, 15, 22] | 0 | 0 | 155/155 | 307/693 | 503/1000 | computed | none |
| rossler_z | rossler_z | 625/375 | 289 | [0, 0, 0] | 0 | 0 | 250/54 | 588/412 | 590/1000 | computed | none |
| hindmarsh_rose | hindmarsh_rose | 132/868 | 15 | [0, 0, 0] | 0 | 0 | 53/201 | 291/709 | 501/1000 | computed | none |
| hyper_jha | hyper_jha | 101/899 | 10 | [0, 0] | 0 | 0 | 242/89 | 678/322 | 525/1000 | computed | none |
| lorenz96_4 | lorenz96_4 | 313/687 | 22 | [0, 0] | 0 | 0 | 178/88 | 814/186 | 510/1000 | computed | none |

## Stored reasons

- ens-DEV-1:lorenz63 H1a: `rho=0.01: interval meets band edge; rho=0.02: interval meets band edge` (systems/lorenz63/H1a/reason)
- ens-DEV-1:lorenz63 H3a: `largest Holm-adjusted p 1 >= 0.01` (systems/lorenz63/H3a/reason)
- ens-DEV-1:lorenz63 H3b: `weight_lambda: interval meets band edge; D: interval meets band edge` (systems/lorenz63/H3b/reason)
- ens-DEV-1:rossler H2c: `A4_minus_A2: interval meets band edge; A4_minus_A1: interval meets band edge` (systems/rossler/H2c/reason)
- ens-DEV-1:rossler H3a: `largest Holm-adjusted p 0.487 >= 0.01` (systems/rossler/H3a/reason)
- ens-DEV-1:rossler H3b: `weight_lambda: interval meets band edge` (systems/rossler/H3b/reason)
- ens-DEV-1:chua H1d: `analog_seed: interval meets band edge` (systems/chua/H1d/reason)
- ens-DEV-1:chua H3b: `weight_lambda: interval meets band edge` (systems/chua/H3b/reason)
- ens-DEV-3:lorenz63 H3c: `interval meets band edge` (systems/lorenz63/H3c/reason)
- ens-DEV-3:lorenz63 H1a: `rho=0.02: interval meets band edge` (systems/lorenz63/H1a/reason)
- ens-DEV-3:lorenz63 H1d: `analog_seed: interval meets band edge` (systems/lorenz63/H1d/reason)
- ens-DEV-3:lorenz63 H3a: `largest Holm-adjusted p 1 >= 0.01` (systems/lorenz63/H3a/reason)
- ens-DEV-3:lorenz63 H3b: `weight_lambda: interval meets band edge` (systems/lorenz63/H3b/reason)
- ens-DEV-3:rossler H2c: `A4_minus_A2: interval meets band edge; A4_minus_A1: interval meets band edge` (systems/rossler/H2c/reason)
- ens-DEV-3:rossler H3a: `largest Holm-adjusted p 0.562 >= 0.01` (systems/rossler/H3a/reason)
- ens-DEV-3:chua H3c: `interval meets band edge` (systems/chua/H3c/reason)
- ens-DEV-3:chua H1d: `analog_seed: interval meets band edge` (systems/chua/H1d/reason)
- ens-DEV-3:chua H2c: `A4_minus_A2: interval meets band edge; A4_minus_A1: interval meets band edge` (systems/chua/H2c/reason)
- ens-DEV-3:chua H3b: `weight_lambda: interval meets band edge` (systems/chua/H3b/reason)
- ens-DEV-4:lorenz63 H3c: `interval meets band edge` (systems/lorenz63/H3c/reason)
- ens-DEV-4:lorenz63 H1b: `interval meets band edge` (systems/lorenz63/H1b/reason)
- ens-DEV-4:lorenz63 H2c: `A4_minus_A2: interval meets band edge` (systems/lorenz63/H2c/reason)
- ens-DEV-4:lorenz63 H2d: `interval meets band edge` (systems/lorenz63/H2d/reason)
- ens-DEV-4:lorenz63 H3a: `largest Holm-adjusted p 0.803 >= 0.01` (systems/lorenz63/H3a/reason)
- ens-DEV-4:rossler H3a: `largest Holm-adjusted p 0.0205 >= 0.01` (systems/rossler/H3a/reason)
- ens-DEV-4:chua H2b: `library_change: interval meets band edge` (systems/chua/H2b/reason)
- ens-DEV-4:chua H3c: `interval meets band edge` (systems/chua/H3c/reason)
- ens-DEV-4:chua H1a: `rho=0.02: interval meets band edge` (systems/chua/H1a/reason)
- ens-DEV-4:chua H1d: `analog_seed: interval meets band edge` (systems/chua/H1d/reason)
- ens-DEV-4:chua H2c: `A4_minus_A2: interval meets band edge` (systems/chua/H2c/reason)
- ens-DEV-4:chua H3a: `largest Holm-adjusted p 0.506 >= 0.01` (systems/chua/H3a/reason)
- ens-DEV-4:chua H3b: `weight_lambda: interval meets band edge` (systems/chua/H3b/reason)
- rossler_hyper:rossler_hyper H3c: `interval meets band edge` (systems/rossler_hyper/H3c/reason)
- rossler_hyper:rossler_hyper H2c: `A4_minus_A2: interval meets band edge` (systems/rossler_hyper/H2c/reason)
- rossler_hyper:rossler_hyper H2d: `interval meets band edge` (systems/rossler_hyper/H2d/reason)
- lorenz63_r166:lorenz63_r166 H2b: `library_change: interval meets band edge` (systems/lorenz63_r166/H2b/reason)
- lorenz63_r166:lorenz63_r166 H2d: `interval meets band edge` (systems/lorenz63_r166/H2d/reason)
- lorenz63_r166:lorenz63_r166 H2e: `rho=0.01: interval meets band edge; rho=0.02: interval meets band edge` (systems/lorenz63_r166/H2e/reason)
- rossler_z:rossler_z H2c: `A4_minus_A2: interval meets band edge` (systems/rossler_z/H2c/reason)
- rossler_z:rossler_z H3a: `largest Holm-adjusted p 0.321 >= 0.01` (systems/rossler_z/H3a/reason)
- hindmarsh_rose:hindmarsh_rose H2e: `rho=0.02: interval meets band edge` (systems/hindmarsh_rose/H2e/reason)
- hindmarsh_rose:hindmarsh_rose H3a: `largest Holm-adjusted p 0.562 >= 0.01` (systems/hindmarsh_rose/H3a/reason)
- hindmarsh_rose:hindmarsh_rose H3b: `weight_lambda: interval meets band edge; D: interval meets band edge` (systems/hindmarsh_rose/H3b/reason)
- hyper_jha:hyper_jha H1a: `rho=0.01: interval meets band edge; rho=0.02: interval meets band edge` (systems/hyper_jha/H1a/reason)
- hyper_jha:hyper_jha H2d: `interval meets band edge` (systems/hyper_jha/H2d/reason)
- lorenz96_4:lorenz96_4 H1a: `rho=0.01: interval meets band edge; rho=0.02: interval meets band edge` (systems/lorenz96_4/H1a/reason)
- lorenz96_4:lorenz96_4 H1c: `interval meets band edge` (systems/lorenz96_4/H1c/reason)
- lorenz96_4:lorenz96_4 H2d: `interval meets band edge` (systems/lorenz96_4/H2d/reason)
- lorenz96_4:lorenz96_4 H2e: `rho=0.01: interval meets band edge` (systems/lorenz96_4/H2e/reason)
