# Phase J confirmatory verdicts

**PHASE J CONFIRMATORY (CONF-5, CONF-6, CONF-7, CONF-8, CONF-9): pre-registered verdicts, UNPROMOTED.** Seeds CONF-5, CONF-6, CONF-7, CONF-8, CONF-9; mode sealed; analysis commit `c19ad486b93a2ee96d64ce069ec42fd440428211` (dirty: False); preset phasej; claim table `../../docs/study/preregistration_phase_j/claims.json` (sha256 `9d1a34bf3e72a478599b3290bbc2a8aa792728f8a72bead8964f3b19fa522648`); pinned Lyapunov cache sha256 `852ce1f67cdcc55275f388c72817348b1b83e2146b4751c8c8aedc7a85453417`. At least 4 seeds; no pooling across seeds.

Rule: Per row: confirmed if the claim is implied by the reading on at least 4 seeds among those present and no two present seeds have jointly unsatisfiable interval claims; contradicted if some such pair exists; not confirmable if fewer than 4 seeds are present (gate failures make a system's rows absent for that seed, DC-5); otherwise not confirmed. Per claim and system: confirmed if every row of that system is confirmed; contradicted if any is contradicted; not confirmable if any is not confirmable and none is contradicted; otherwise not confirmed. Rows of J-I1 and J-C2 are read by reading_tables; their claims enter the same rule.

## Inputs

PHASE J CONFIRMATORY (CONF-5, CONF-6, CONF-7, CONF-8, CONF-9): pre-registered verdicts, UNPROMOTED.

| seed | gate pass | cache equals pinned | cache sha256 |
|---|---|---|---|
| CONF-5 | lorenz63 True, rossler True, chua True | True | `852ce1f67cdcc55275f388c72817348b1b83e2146b4751c8c8aedc7a85453417` |
| CONF-6 | lorenz63 True, rossler True, chua True | True | `852ce1f67cdcc55275f388c72817348b1b83e2146b4751c8c8aedc7a85453417` |
| CONF-7 | lorenz63 True, rossler True, chua True | True | `852ce1f67cdcc55275f388c72817348b1b83e2146b4751c8c8aedc7a85453417` |
| CONF-8 | lorenz63 True, rossler True, chua True | True | `852ce1f67cdcc55275f388c72817348b1b83e2146b4751c8c8aedc7a85453417` |
| CONF-9 | lorenz63 True, rossler True, chua True | True | `852ce1f67cdcc55275f388c72817348b1b83e2146b4751c8c8aedc7a85453417` |

## Verdicts by claim and system

PHASE J CONFIRMATORY (CONF-5, CONF-6, CONF-7, CONF-8, CONF-9): pre-registered verdicts, UNPROMOTED.

| claim | system | verdict | rows | row verdicts |
|---|---|---|---|---|
| J-H1 | chua | **confirmed** | 2 | confirmed 2 |
| J-H1 | lorenz63 | **confirmed** | 2 | confirmed 2 |
| J-H1 | rossler | **confirmed** | 2 | confirmed 2 |
| J-H2 | chua | **confirmed** | 2 | confirmed 2 |
| J-H2 | lorenz63 | **confirmed** | 2 | confirmed 2 |
| J-H2 | rossler | **confirmed** | 2 | confirmed 2 |
| J-H3 | chua | **confirmed** | 2 | confirmed 2 |
| J-H3 | lorenz63 | **confirmed** | 2 | confirmed 2 |
| J-H3 | rossler | **confirmed** | 2 | confirmed 2 |
| J-H4 | chua | **confirmed** | 2 | confirmed 2 |
| J-H4 | lorenz63 | **confirmed** | 2 | confirmed 2 |
| J-H4 | rossler | **confirmed** | 2 | confirmed 2 |
| J-H5 | chua | **confirmed** | 2 | confirmed 2 |
| J-H5 | lorenz63 | **confirmed** | 2 | confirmed 2 |
| J-H5 | rossler | **confirmed** | 2 | confirmed 2 |
| J-H6 | chua | **confirmed** | 2 | confirmed 2 |
| J-H6 | lorenz63 | **confirmed** | 2 | confirmed 2 |
| J-H6 | rossler | **confirmed** | 2 | confirmed 2 |
| J-A1 | rossler | **confirmed** | 1 | confirmed 1 |
| J-A2 | rossler | **confirmed** | 1 | confirmed 1 |
| J-A3 | chua | **confirmed** | 2 | confirmed 2 |
| J-A3 | lorenz63 | **confirmed** | 2 | confirmed 2 |
| J-A3 | rossler | **confirmed** | 2 | confirmed 2 |
| J-A4 | lorenz63 | **not confirmed** | 1 | not confirmed 1 |
| J-I1 | lorenz63 | **confirmed** | 1 | confirmed 1 |
| J-I1 | chua | **confirmed** | 1 | confirmed 1 |
| J-C2 | rossler | **confirmed** | 1 | confirmed 1 |

## J-H1: A drop-one, claim `ratio > 1.05`

PHASE J CONFIRMATORY (CONF-5, CONF-6, CONF-7, CONF-8, CONF-9): pre-registered verdicts, UNPROMOTED.

| system | profile | horizon | item | CONF-5 | CONF-6 | CONF-7 | CONF-8 | CONF-9 | implying | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| chua | deployable | T_c | drop I: pinball ratio | substantial | substantial | substantial | substantial | substantial | 5 of 5 | confirmed |
| chua | oracle | T_c | drop I: pinball ratio | substantial | substantial | substantial | substantial | substantial | 5 of 5 | confirmed |
| lorenz63 | deployable | T_c | drop I: pinball ratio | substantial | substantial | substantial | substantial | substantial | 5 of 5 | confirmed |
| lorenz63 | oracle | T_c | drop I: pinball ratio | substantial | substantial | substantial | substantial | substantial | 5 of 5 | confirmed |
| rossler | deployable | T_c | drop I: pinball ratio | substantial | substantial | substantial | substantial | substantial | 5 of 5 | confirmed |
| rossler | oracle | T_c | drop I: pinball ratio | substantial | substantial | substantial | substantial | substantial | 5 of 5 | confirmed |

## J-H2: A drop-one, claim `ratio > 1`

PHASE J CONFIRMATORY (CONF-5, CONF-6, CONF-7, CONF-8, CONF-9): pre-registered verdicts, UNPROMOTED.

| system | profile | horizon | item | CONF-5 | CONF-6 | CONF-7 | CONF-8 | CONF-9 | implying | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| chua | deployable | T_c | drop O: pinball ratio | substantial | substantial | substantial | substantial | substantial | 5 of 5 | confirmed |
| chua | oracle | T_c | drop O: pinball ratio | substantial | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | 5 of 5 | confirmed |
| lorenz63 | deployable | T_c | drop O: pinball ratio | substantial | substantial | substantial | substantial | substantial | 5 of 5 | confirmed |
| lorenz63 | oracle | T_c | drop O: pinball ratio | substantial | substantial | substantial | substantial | substantial | 5 of 5 | confirmed |
| rossler | deployable | T_c | drop O: pinball ratio | substantial | substantial | substantial | substantial | substantial | 5 of 5 | confirmed |
| rossler | oracle | T_c | drop O: pinball ratio | substantial | substantial | substantial | substantial | substantial | 5 of 5 | confirmed |

## J-H3: A drop-one, claim `ratio <= 1.05`

PHASE J CONFIRMATORY (CONF-5, CONF-6, CONF-7, CONF-8, CONF-9): pre-registered verdicts, UNPROMOTED.

| system | profile | horizon | item | CONF-5 | CONF-6 | CONF-7 | CONF-8 | CONF-9 | implying | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| chua | deployable | T_c | drop N: pinball ratio | negligible | negligible | negligible | negligible | lowers | 5 of 5 | confirmed |
| chua | oracle | T_c | drop N: pinball ratio | negligible | negligible | negligible | negligible | small | 5 of 5 | confirmed |
| lorenz63 | deployable | T_c | drop N: pinball ratio | negligible | lowers | negligible | negligible | negligible | 5 of 5 | confirmed |
| lorenz63 | oracle | T_c | drop N: pinball ratio | negligible | negligible | negligible | negligible | negligible | 5 of 5 | confirmed |
| rossler | deployable | T_c | drop N: pinball ratio | negligible | negligible | negligible | negligible | negligible | 5 of 5 | confirmed |
| rossler | oracle | T_c | drop N: pinball ratio | small | negligible | negligible | small | small | 5 of 5 | confirmed |

## J-H4: B pair, claim `delta > 0`

PHASE J CONFIRMATORY (CONF-5, CONF-6, CONF-7, CONF-8, CONF-9): pre-registered verdicts, UNPROMOTED.

| system | profile | horizon | item | CONF-5 | CONF-6 | CONF-7 | CONF-8 | CONF-9 | implying | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| chua | deployable | T_c | log T OI: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | 5 of 5 | confirmed |
| chua | oracle | T_c | log T OI: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | 5 of 5 | confirmed |
| lorenz63 | deployable | T_c | log T OI: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | 5 of 5 | confirmed |
| lorenz63 | oracle | T_c | log T OI: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | 5 of 5 | confirmed |
| rossler | deployable | T_c | log T OI: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | 5 of 5 | confirmed |
| rossler | oracle | T_c | log T OI: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | 5 of 5 | confirmed |

## J-H5: D vs full, claim `ratio > 1.05`

PHASE J CONFIRMATORY (CONF-5, CONF-6, CONF-7, CONF-8, CONF-9): pre-registered verdicts, UNPROMOTED.

| system | profile | horizon | item | CONF-5 | CONF-6 | CONF-7 | CONF-8 | CONF-9 | implying | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| chua | deployable | T_c | lyapunov: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | 5 of 5 | confirmed |
| chua | oracle | T_c | lyapunov: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | 5 of 5 | confirmed |
| lorenz63 | deployable | T_c | lyapunov: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | 5 of 5 | confirmed |
| lorenz63 | oracle | T_c | lyapunov: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | 5 of 5 | confirmed |
| rossler | deployable | T_c | lyapunov: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | 5 of 5 | confirmed |
| rossler | oracle | T_c | lyapunov: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | 5 of 5 | confirmed |

## J-H6: D vs full, claim `ratio < 1`

PHASE J CONFIRMATORY (CONF-5, CONF-6, CONF-7, CONF-8, CONF-9): pre-registered verdicts, UNPROMOTED.

| system | profile | horizon | item | CONF-5 | CONF-6 | CONF-7 | CONF-8 | CONF-9 | implying | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| chua | deployable | T_c | X+F: pinball ratio vs F | lowers | lowers | lowers | lowers | lowers | 5 of 5 | confirmed |
| chua | oracle | T_c | X+F: pinball ratio vs F | lowers | lowers | lowers | lowers | lowers | 5 of 5 | confirmed |
| lorenz63 | deployable | T_c | X+F: pinball ratio vs F | lowers | lowers | lowers | lowers | lowers | 5 of 5 | confirmed |
| lorenz63 | oracle | T_c | X+F: pinball ratio vs F | lowers | lowers | lowers | lowers | lowers | 5 of 5 | confirmed |
| rossler | deployable | T_c | X+F: pinball ratio vs F | lowers | lowers | lowers | lowers | lowers | 5 of 5 | confirmed |
| rossler | oracle | T_c | X+F: pinball ratio vs F | lowers | lowers | lowers | lowers | lowers | 5 of 5 | confirmed |

## J-A1: A drop-one, claim `ratio > 1.05`

PHASE J CONFIRMATORY (CONF-5, CONF-6, CONF-7, CONF-8, CONF-9): pre-registered verdicts, UNPROMOTED.

| system | profile | horizon | item | CONF-5 | CONF-6 | CONF-7 | CONF-8 | CONF-9 | implying | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| rossler | oracle | H=30 (1.00 LT) | drop R: MSE ratio | substantial | substantial | substantial | substantial | substantial | 5 of 5 | confirmed |

## J-A2: D vs full, claim `ratio <= 1.05`

PHASE J CONFIRMATORY (CONF-5, CONF-6, CONF-7, CONF-8, CONF-9): pre-registered verdicts, UNPROMOTED.

| system | profile | horizon | item | CONF-5 | CONF-6 | CONF-7 | CONF-8 | CONF-9 | implying | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| rossler | deployable | H=30 (1.00 LT) | none: mse ratio vs F | negligible | negligible | negligible | negligible | negligible | 5 of 5 | confirmed |

## J-A3: A vs separation, claim `ratio < 1`

PHASE J CONFIRMATORY (CONF-5, CONF-6, CONF-7, CONF-8, CONF-9): pre-registered verdicts, UNPROMOTED.

| system | profile | horizon | item | CONF-5 | CONF-6 | CONF-7 | CONF-8 | CONF-9 | implying | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| chua | deployable | H=120 (4.00 LT) | none: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | 5 of 5 | confirmed |
| chua | oracle | H=120 (4.00 LT) | none: MSE(F)/MSE(sep) | lowers | negligible | lowers | lowers | lowers | 4 of 5 | confirmed |
| lorenz63 | deployable | H=120 (4.00 LT) | none: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | 5 of 5 | confirmed |
| lorenz63 | oracle | H=120 (4.00 LT) | none: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | 5 of 5 | confirmed |
| rossler | deployable | H=120 (4.00 LT) | none: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | 5 of 5 | confirmed |
| rossler | oracle | H=120 (4.00 LT) | none: MSE(F)/MSE(sep) | lowers | lowers | lowers | negligible | lowers | 4 of 5 | confirmed |

## J-A4: D vs full, claim `ratio < 1`

PHASE J CONFIRMATORY (CONF-5, CONF-6, CONF-7, CONF-8, CONF-9): pre-registered verdicts, UNPROMOTED.

| system | profile | horizon | item | CONF-5 | CONF-6 | CONF-7 | CONF-8 | CONF-9 | implying | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| lorenz63 | deployable | H=30 (1.00 LT) | X: mse ratio vs F | undetermined | lowers | undetermined | lowers | lowers | 3 of 5 | not confirmed |

## J-I1: pipeline results.json, claim `delta_r2 > 0`

PHASE J CONFIRMATORY (CONF-5, CONF-6, CONF-7, CONF-8, CONF-9): pre-registered verdicts, UNPROMOTED.

| system | profile | horizon | item | CONF-5 | CONF-6 | CONF-7 | CONF-8 | CONF-9 | implying | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| lorenz63 | deployable |  | drop I: Delta R^2 on logit w* (Q-N procedure) | reduces | distinct but small | substantial | substantial | substantial | 4 of 5 | confirmed |
| chua | deployable |  | drop I: Delta R^2 on logit w* (Q-N procedure) | substantial | substantial | substantial | substantial | substantial | 5 of 5 | confirmed |

## J-C2: ce.json, claim `false_trust > 0.10`

PHASE J CONFIRMATORY (CONF-5, CONF-6, CONF-7, CONF-8, CONF-9): pre-registered verdicts, UNPROMOTED.

| system | profile | horizon | item | CONF-5 | CONF-6 | CONF-7 | CONF-8 | CONF-9 | implying | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| rossler | deployable |  | C3 full deployable system: realized false-trust rate | above target | above target | above target | above target | above target | 5 of 5 | confirmed |
