## Provenance

| run | seed_id | seed_kind | label | promoted | commit | dirty | complete | steps/LT | H_max (LT) | core rho | core n_lib | n_test | SHA-256 results.json |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ens-DEV-1 | DEV-1 | development | DEVELOPMENT (DEV-1): not a hypothesis test | False | 3dec086 | False | True | 30 | 8.0 | 0.01 | 10000 | 1000 | `0a4ef215c7262340cef3e95cc073c4b7a374c73d688a12ad68ed5517d6102860` |
| ens-DEV-3 | DEV-3 | development | DEVELOPMENT (DEV-3): not a hypothesis test | False | 3dec086 | False | True | 30 | 8.0 | 0.01 | 10000 | 1000 | `24a7c4b77a253ec34a1a6e301a932d3171ec22c1a70568941158c9a6787af247` |
| ens-DEV-4 | DEV-4 | development | DEVELOPMENT (DEV-4): not a hypothesis test | False | 3dec086 | False | True | 30 | 8.0 | 0.01 | 10000 | 1000 | `8eadc3992bcbffbeb399c46523eb308d351eb081937a622029119f68861c5655` |
| ext-rossler_hyper | DEV-3 | development | DEVELOPMENT (DEV-3): not a hypothesis test | False | 974519a | False | True | 30 | 8.0 | 0.01 | 10000 | 1000 | `ac588151e6aad4efabf1be0e9977c4d3366d895d605722cf6a1c660c054ceffc` |
| ext-lorenz63_r166 | DEV-3 | development | DEVELOPMENT (DEV-3): not a hypothesis test | False | 974519a | False | True | 30 | 8.0 | 0.01 | 10000 | 1000 | `183a151966ae5c851bd1bde05ab1e8ff7b82c7da13a0974a2896ef8e60671e4c` |
| ext-rossler_z | DEV-3 | development | DEVELOPMENT (DEV-3): not a hypothesis test | False | 974519a | False | True | 30 | 8.0 | 0.01 | 10000 | 1000 | `f95ae88a22bccfe04dba48aa1f23632243a5b3c8cd740b261f098a17c5fdbf93` |
| ext-hindmarsh_rose | DEV-3 | development | DEVELOPMENT (DEV-3): not a hypothesis test | False | 392a069 | False | True | 30 | 8.0 | 0.01 | 10000 | 1000 | `090f82e0ba16aed9f01666d2ab4043f394f32c6cebc2273c7d804059f7b1b8e4` |
| ext-hyper_jha | DEV-3 | development | DEVELOPMENT (DEV-3): not a hypothesis test | False | 392a069 | False | True | 30 | 8.0 | 0.01 | 10000 | 1000 | `5edfd1deb91eac73e56701cbc8ee9abaa852b1c714e1571cd1e96be87c603b7a` |
| ext-lorenz96_4 | DEV-3 | development | DEVELOPMENT (DEV-3): not a hypothesis test | False | 392a069 | False | True | 30 | 8.0 | 0.01 | 10000 | 1000 | `8aaac680997ae24407526cba6f5cc55f7b5744d47330596e4ec03323c4da2e6b` |

## V3 leaves (systems/<s>/validation/cp_median_vpt_lyapunov; context/*)

| run | system | V3 (LT) | V3 x 30 (steps) | lambda_max | interval | obs_scale | gate |
|---|---|---|---|---|---|---|---|
| ens-DEV-1 | lorenz63 | 2.0 | 60.0 | 0.905668542691417 | 0.03680522372376447 | 7.924482883275749 | PASS |
| ens-DEV-1 | rossler | 3.3 | 99.0 | 0.07171891954365615 | 0.46477740525696204 | 5.1596518151848025 | PASS |
| ens-DEV-1 | chua | 2.9 | 87.0 | 0.4408520035546002 | 0.07561116443742089 | 1.4198204918975599 | PASS |
| ens-DEV-3 | lorenz63 | 2.033333333333333 | 61.0 | 0.905668542691417 | 0.03680522372376447 | 7.924482883275749 | PASS |
| ens-DEV-3 | rossler | 3.1333333333333333 | 94.0 | 0.07171891954365615 | 0.46477740525696204 | 5.1596518151848025 | PASS |
| ens-DEV-3 | chua | 2.9 | 87.0 | 0.4408520035546001 | 0.0756111644374209 | 1.421888122370662 | PASS |
| ens-DEV-4 | lorenz63 | 2.033333333333333 | 61.0 | 0.905668542691417 | 0.03680522372376447 | 7.924482883275749 | PASS |
| ens-DEV-4 | rossler | 3.2333333333333334 | 97.0 | 0.07171891954365615 | 0.46477740525696204 | 5.1596518151848025 | PASS |
| ens-DEV-4 | chua | 2.966666666666667 | 89.0 | 0.4408520035546002 | 0.07561116443742089 | 1.4198204918975599 | PASS |
| ext-rossler_hyper | rossler_hyper | 1.5666666666666667 | 47.0 | 0.11272865874045755 | 0.29569528907532566 | 22.009616418751378 | PASS |
| ext-lorenz63_r166 | lorenz63_r166 | 3.3666666666666667 | 101.0 | 0.6224320098292552 | 0.053553372588400934 | 20.336283446397765 | FAIL (PROVISIONAL) |
| ext-rossler_z | rossler_z | 0.4666666666666667 | 14.0 | 0.07165017999321659 | 0.46522330211158064 | 2.844297825017483 | FAIL (PROVISIONAL) |
| ext-hindmarsh_rose | hindmarsh_rose | 0.8666666666666667 | 26.0 | 0.21678000879703424 | 0.15376571630524524 | 0.30548619691534085 | FAIL (PROVISIONAL) |
| ext-hyper_jha | hyper_jha | 0.36666666666666664 | 11.0 | 0.3596491603967948 | 0.09268291714224283 | 9.665746003911426 | FAIL (PROVISIONAL) |
| ext-lorenz96_4 | lorenz96_4 | 0.9 | 27.0 | 1.1964213277385642 | 0.027860865199000495 | 6.9824073186166595 | FAIL (PROVISIONAL) |

## Stated conversions (frozen systems only)

| ens-DEV-1 | lorenz63 | T = V3/lambda = 2.20831 | T/t_peak = 1.471 | V3 x lambda_max_field/lambda = 1.969 (conditional) | V3 x spectrum0/lambda = 2.409 | 10 t_peak x lambda = 13.59 LT | 512/30 x lambda/lambda_max_field = 17.33 LT (conditional) | 300/30 x lambda/lambda_max_field = 10.16 LT (conditional) | ratio lambda_max_field/lambda = 0.9846 |
| ens-DEV-1 | rossler | T = V3/lambda = 46.013 | T/t_peak = 7.787 | V3 x lambda_max_field/lambda = 6.929 (conditional) | V3 x spectrum0/lambda = 3.512 | 10 t_peak x lambda = 4.238 LT | 512/30 x lambda/lambda_max_field = 8.128 LT (conditional) | 300/30 x lambda/lambda_max_field = 4.762 LT (conditional) | ratio lambda_max_field/lambda = 2.1 |
| ens-DEV-1 | chua | T = V3/lambda = 6.57817 | T/t_peak = 4.621 | V3 x lambda_max_field/lambda = 8.092 (conditional) | V3 x spectrum0/lambda = 3.03 | 10 t_peak x lambda = 6.276 LT | 512/30 x lambda/lambda_max_field = 6.116 LT (conditional) | 300/30 x lambda/lambda_max_field = 3.584 LT (conditional) | ratio lambda_max_field/lambda = 2.79 |
| ens-DEV-3 | lorenz63 | T = V3/lambda = 2.24512 | T/t_peak = 1.496 | V3 x lambda_max_field/lambda = 2.002 (conditional) | V3 x spectrum0/lambda = 2.45 | 10 t_peak x lambda = 13.59 LT | 512/30 x lambda/lambda_max_field = 17.33 LT (conditional) | 300/30 x lambda/lambda_max_field = 10.16 LT (conditional) | ratio lambda_max_field/lambda = 0.9846 |
| ens-DEV-3 | rossler | T = V3/lambda = 43.6891 | T/t_peak = 7.394 | V3 x lambda_max_field/lambda = 6.579 (conditional) | V3 x spectrum0/lambda = 3.335 | 10 t_peak x lambda = 4.238 LT | 512/30 x lambda/lambda_max_field = 8.128 LT (conditional) | 300/30 x lambda/lambda_max_field = 4.762 LT (conditional) | ratio lambda_max_field/lambda = 2.1 |
| ens-DEV-3 | chua | T = V3/lambda = 6.57817 | T/t_peak = 4.621 | V3 x lambda_max_field/lambda = 8.092 (conditional) | V3 x spectrum0/lambda = 3.03 | 10 t_peak x lambda = 6.276 LT | 512/30 x lambda/lambda_max_field = 6.116 LT (conditional) | 300/30 x lambda/lambda_max_field = 3.584 LT (conditional) | ratio lambda_max_field/lambda = 2.79 |
| ens-DEV-4 | lorenz63 | T = V3/lambda = 2.24512 | T/t_peak = 1.496 | V3 x lambda_max_field/lambda = 2.002 (conditional) | V3 x spectrum0/lambda = 2.45 | 10 t_peak x lambda = 13.59 LT | 512/30 x lambda/lambda_max_field = 17.33 LT (conditional) | 300/30 x lambda/lambda_max_field = 10.16 LT (conditional) | ratio lambda_max_field/lambda = 0.9846 |
| ens-DEV-4 | rossler | T = V3/lambda = 45.0834 | T/t_peak = 7.63 | V3 x lambda_max_field/lambda = 6.789 (conditional) | V3 x spectrum0/lambda = 3.441 | 10 t_peak x lambda = 4.238 LT | 512/30 x lambda/lambda_max_field = 8.128 LT (conditional) | 300/30 x lambda/lambda_max_field = 4.762 LT (conditional) | ratio lambda_max_field/lambda = 2.1 |
| ens-DEV-4 | chua | T = V3/lambda = 6.72939 | T/t_peak = 4.727 | V3 x lambda_max_field/lambda = 8.278 (conditional) | V3 x spectrum0/lambda = 3.099 | 10 t_peak x lambda = 6.276 LT | 512/30 x lambda/lambda_max_field = 6.116 LT (conditional) | 300/30 x lambda/lambda_max_field = 3.584 LT (conditional) | ratio lambda_max_field/lambda = 2.79 |
