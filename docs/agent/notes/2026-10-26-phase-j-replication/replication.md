# Phase J replication (rule M-6)

**DEVELOPMENT: phase J replication (held-out development seeds), not a hypothesis test.** Seeds DEV-5, DEV-6, DEV-7, DEV-8, DEV-9; analysis commit `0929a9a2c2fb8d41983c8c27fdec712eb9ed49b2` (dirty: False); preset phasej; mode rule, at least 4 of 5. No pooling across seeds. Readings and claims are estimates on development seeds; no pass or fail.

Rule: replicated: one claim-bearing reading on at least 4 of 5 seeds and no pair of seeds with jointly unsatisfiable interval claims; contradicted: some such pair; replicated (point readings): the same count on a row whose claims are all point claims, which never contradict; else not replicated. Fallback: atomic interval claims implied on at least 4 seeds and contradicted by none, listed as 'replicated claim', or as 'replicated claim within a contradicted row' beneath a contradicted row. C1 rows are checked equal to D vs full and left out of the family counts.

## Summary by family

C1 rows are display only: on every seed they equal their D vs-full source (240, 240, 240, 240, 240 checked per seed) and are not counted here.

DEVELOPMENT: phase J replication (held-out development seeds), not a hypothesis test.

| family | rows | replicated | replicated (point readings) | contradicted | not replicated | with replicated claim | replicated claim within a contradicted row | absent on some seed |
|---|---|---|---|---|---|---|---|---|
| A drop-one | 144 | 72 | 0 | 1 | 71 | 17 | 1 | 0 |
| A vs separation | 480 | 254 | 0 | 4 | 222 | 47 | 3 | 0 |
| B loss ratio | 624 | 388 | 0 | 8 | 228 | 150 | 5 | 0 |
| B pair | 624 | 101 | 0 | 7 | 516 | 0 | 0 | 0 |
| C2 oracle vs deployable | 36 | 10 | 0 | 4 | 22 | 0 | 0 | 0 |
| C2 prediction | 6 | 2 | 0 | 3 | 1 | 0 | 0 | 0 |
| C2 ratio | 42 | 20 | 0 | 1 | 21 | 8 | 1 | 0 |
| C2 retained | 102 | 65 | 0 | 6 | 31 | 0 | 0 | 0 |
| C3 ratio | 66 | 43 | 0 | 1 | 22 | 5 | 1 | 0 |
| D vs below | 372 | 192 | 0 | 10 | 170 | 53 | 10 | 0 |
| D vs full | 372 | 176 | 0 | 5 | 191 | 45 | 4 | 0 |
| E-H2a | 3 | 1 | 0 | 0 | 2 | 0 | 0 | 0 |
| E-H2e | 18 | 3 | 0 | 2 | 13 | 0 | 0 | 0 |
| E-H3c | 3 | 0 | 3 | 0 | 0 | 0 | 0 | 0 |
| check (f2) | 393 | 94 | 0 | 4 | 295 | 0 | 0 | 0 |

## Claims of every reading word

A word with claims `none` never contradicts and never counts toward the minimum. Point claims (marked point) count through the word only and never establish a contradiction or a fallback claim.

DEVELOPMENT: phase J replication (held-out development seeds), not a hypothesis test.

| row type | word | claims |
|---|---|---|
| ratio (1.05 table) | lowers | ratio < 1 |
| ratio (1.05 table) | negligible | ratio <= 1.05 |
| ratio (1.05 table) | small | ratio > 1 and ratio <= 1.05 |
| ratio (1.05 table) | substantial | ratio > 1.05 |
| ratio (1.05 table) | needed, size not determined | ratio > 1 |
| ratio (1.05 table) | undetermined | none |
| ratio (1.05 table) | not identifiable | none |
| ratio (1.05 table) | no interaction gain; the pair model fits worse | ratio < 1 |
| B pair (Delta, Holm) | interaction gain detected | delta > 0 |
| B pair (Delta, Holm) | no interaction gain detected | none |
| B pair (Delta, Holm) | no interaction gain; the pair model fits worse | delta < 0 |
| C2 retained | keeps most | retained > 0.5 |
| C2 retained | loses most | retained < 0.5 |
| C2 retained | not determined (...) | none |
| C2 oracle vs deployable | deployable retains less | difference < 0 |
| C2 oracle vs deployable | deployable retains more | difference > 0 |
| C2 oracle vs deployable | no difference detected | none |
| C2 oracle vs deployable | not determined (...) | none |
| C2 prediction (both lose most) | consistent | forward retained < 0.5, and reverse@H retained < 0.5 at every H whose reading is determined |
| C2 prediction (both lose most) | not consistent | retained > 0.5 on every component reading 'keeps most' |
| C2 prediction (both lose most) | not determined | none |
| check (f2) dependence bias | no detectable dependence bias | none |
| check (f2) dependence bias | realized-noise outlier, no detectable dependence bias | none |
| check (f2) dependence bias | dependence bias detectable (interval excludes 0) | bias > 0 or bias < 0, the side of the interval |
| E-H2a | consistent | at every supporting H: Spearman(m, I)@H > 0.1 or < -0.1 (the side of its interval), and drift(high I) - drift(low I)@H > 0 (point) |
| E-H2a | not consistent | at every usable H: -0.1 < Spearman(m, I)@H < 0.1 |
| E-H2a | not determined (...) | none |
| E-H2e part | consistent | median Delta corr > 0 and Spearman(Delta corr, Delta R) < 0 |
| E-H2e part | not consistent | Spearman > 0 and/or median < 0, whichever interval established it |
| E-H2e part | not determined | none |
| E-H2e level (final) | consistent / not consistent | the claims of both parts (all, both_defined), which agree |
| E-H2e level (final) | not determined (...) | none |
| E-H3c Lorenz-63 part (point) | consistent | top-1% share >= 0.1 and median I percentile >= 2/3 |
| E-H3c Lorenz-63 part (point) | not consistent | top-1% share < 0.05 and/or median I percentile < 1/2, whichever holds |
| E-H3c Lorenz-63 part (point) | not determined | none |
| E-H3c Rossler part (point) | consistent | BC < 0.5556 for R, O, I and N |
| E-H3c Rossler part (point) | not consistent | BC > 0.5556 for each coordinate where it holds (two or more) |
| E-H3c Rossler part (point) | not determined | none |
| E-H3c overall (point) | consistent | width ordering (Lorenz-63 widest, Rossler narrowest) and both parts' consistent claims |
| E-H3c overall (point) | not consistent | width ordering and the claims of each part that reads not consistent |
| E-H3c overall (point) | not determined (...) | none |

## A drop-one

DEVELOPMENT: phase J replication (held-out development seeds), not a hypothesis test.

| system | decision | profile | horizon | item | DEV-5 | DEV-6 | DEV-7 | DEV-8 | DEV-9 | class | replicated reading or claims |
|---|---|---|---|---|---|---|---|---|---|---|---|
| chua | allocation | deployable | H=120 (4.00 LT) | drop I: MSE ratio | negligible | negligible | negligible | small | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | drop N: MSE ratio | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | drop O: MSE ratio | small | small | negligible | small | small | replicated | small |
| chua | allocation | deployable | H=120 (4.00 LT) | drop R: MSE ratio | negligible | negligible | negligible | small | negligible | replicated | negligible |
| chua | allocation | deployable | H=15 (0.50 LT) | drop I: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | drop N: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | drop O: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | drop R: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | drop I: MSE ratio | undetermined | undetermined | negligible | undetermined | negligible | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | drop N: MSE ratio | undetermined | undetermined | negligible | undetermined | negligible | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | drop O: MSE ratio | undetermined | undetermined | negligible | undetermined | negligible | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | drop R: MSE ratio | undetermined | undetermined | negligible | undetermined | negligible | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | drop I: MSE ratio | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=60 (2.00 LT) | drop N: MSE ratio | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=60 (2.00 LT) | drop O: MSE ratio | negligible | negligible | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=60 (2.00 LT) | drop R: MSE ratio | negligible | negligible | negligible | small | negligible | replicated | negligible |
| chua | allocation | deployable | H=8 (0.27 LT) | drop I: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | drop N: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | drop O: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | drop R: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=120 (4.00 LT) | drop I: MSE ratio | small | small | small | small | negligible | replicated | small |
| chua | allocation | oracle | H=120 (4.00 LT) | drop N: MSE ratio | negligible | negligible | negligible | lowers | negligible | replicated | negligible |
| chua | allocation | oracle | H=120 (4.00 LT) | drop O: MSE ratio | negligible | small | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=120 (4.00 LT) | drop R: MSE ratio | small | small | small | small | small | replicated | small |
| chua | allocation | oracle | H=15 (0.50 LT) | drop I: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | drop N: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | drop O: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | drop R: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | drop I: MSE ratio | undetermined | undetermined | negligible | undetermined | negligible | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | drop N: MSE ratio | undetermined | undetermined | negligible | undetermined | negligible | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | drop O: MSE ratio | undetermined | undetermined | negligible | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | drop R: MSE ratio | undetermined | undetermined | needed, size not determined | undetermined | negligible | not replicated |  |
| chua | allocation | oracle | H=60 (2.00 LT) | drop I: MSE ratio | negligible | negligible | negligible | small | negligible | replicated | negligible |
| chua | allocation | oracle | H=60 (2.00 LT) | drop N: MSE ratio | negligible | negligible | negligible | small | lowers | contradicted | DEV-8 small vs DEV-9 lowers; replicated claim within a contradicted row: ratio <= 1.05 |
| chua | allocation | oracle | H=60 (2.00 LT) | drop O: MSE ratio | negligible | negligible | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=60 (2.00 LT) | drop R: MSE ratio | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| chua | allocation | oracle | H=8 (0.27 LT) | drop I: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | drop N: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | drop O: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | drop R: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | horizon | deployable | T_c | drop I: pinball ratio | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | deployable | T_c | drop N: pinball ratio | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | horizon | deployable | T_c | drop O: pinball ratio | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | deployable | T_c | drop R: pinball ratio | small | small | negligible | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | horizon | oracle | T_c | drop I: pinball ratio | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | oracle | T_c | drop N: pinball ratio | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | horizon | oracle | T_c | drop O: pinball ratio | needed, size not determined | needed, size not determined | needed, size not determined | substantial | needed, size not determined | replicated | needed, size not determined |
| chua | horizon | oracle | T_c | drop R: pinball ratio | small | small | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | drop I: MSE ratio | negligible | small | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | drop N: MSE ratio | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | drop O: MSE ratio | negligible | lowers | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | drop R: MSE ratio | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | drop I: MSE ratio | undetermined | undetermined | undetermined | substantial | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | drop N: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | drop O: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | drop R: MSE ratio | undetermined | undetermined | undetermined | needed, size not determined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | drop I: MSE ratio | needed, size not determined | needed, size not determined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | drop N: MSE ratio | undetermined | undetermined | needed, size not determined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | drop O: MSE ratio | needed, size not determined | needed, size not determined | undetermined | undetermined | negligible | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | drop R: MSE ratio | undetermined | undetermined | needed, size not determined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | drop I: MSE ratio | needed, size not determined | negligible | needed, size not determined | negligible | negligible | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | drop N: MSE ratio | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | drop O: MSE ratio | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | drop R: MSE ratio | negligible | negligible | negligible | negligible | needed, size not determined | replicated | negligible |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | drop I: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | drop N: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | drop O: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | drop R: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | drop I: MSE ratio | negligible | small | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | drop N: MSE ratio | lowers | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | drop O: MSE ratio | negligible | small | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | drop R: MSE ratio | small | small | small | small | negligible | replicated | small |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | drop I: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | drop N: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | drop O: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | drop R: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | drop I: MSE ratio | needed, size not determined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | drop N: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | drop O: MSE ratio | substantial | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | drop R: MSE ratio | needed, size not determined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | drop I: MSE ratio | needed, size not determined | small | negligible | needed, size not determined | negligible | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | drop N: MSE ratio | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | drop O: MSE ratio | needed, size not determined | needed, size not determined | needed, size not determined | undetermined | needed, size not determined | replicated | needed, size not determined |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | drop R: MSE ratio | negligible | negligible | undetermined | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | drop I: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | drop N: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | drop O: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | drop R: MSE ratio | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | horizon | deployable | T_c | drop I: pinball ratio | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | deployable | T_c | drop N: pinball ratio | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | horizon | deployable | T_c | drop O: pinball ratio | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | deployable | T_c | drop R: pinball ratio | small | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | horizon | oracle | T_c | drop I: pinball ratio | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | oracle | T_c | drop N: pinball ratio | negligible | lowers | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | horizon | oracle | T_c | drop O: pinball ratio | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | oracle | T_c | drop R: pinball ratio | negligible | needed, size not determined | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=120 (4.00 LT) | drop I: MSE ratio | negligible | negligible | small | small | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=120 (4.00 LT) | drop N: MSE ratio | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=120 (4.00 LT) | drop O: MSE ratio | negligible | small | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=120 (4.00 LT) | drop R: MSE ratio | negligible | negligible | negligible | small | negligible | replicated | negligible |
| rossler | allocation | deployable | H=15 (0.50 LT) | drop I: MSE ratio | negligible | negligible | undetermined | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=15 (0.50 LT) | drop N: MSE ratio | negligible | negligible | undetermined | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=15 (0.50 LT) | drop O: MSE ratio | negligible | negligible | undetermined | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=15 (0.50 LT) | drop R: MSE ratio | negligible | negligible | undetermined | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | drop I: MSE ratio | negligible | negligible | lowers | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | drop N: MSE ratio | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | drop O: MSE ratio | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | drop R: MSE ratio | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | drop I: MSE ratio | negligible | small | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | drop N: MSE ratio | negligible | negligible | lowers | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | drop O: MSE ratio | negligible | small | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=60 (2.00 LT) | drop R: MSE ratio | negligible | negligible | lowers | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=8 (0.27 LT) | drop I: MSE ratio | undetermined | negligible | undetermined | negligible | negligible | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | drop N: MSE ratio | undetermined | negligible | undetermined | negligible | negligible | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | drop O: MSE ratio | undetermined | negligible | undetermined | negligible | negligible | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | drop R: MSE ratio | undetermined | negligible | undetermined | negligible | negligible | not replicated |  |
| rossler | allocation | oracle | H=120 (4.00 LT) | drop I: MSE ratio | small | negligible | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=120 (4.00 LT) | drop N: MSE ratio | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=120 (4.00 LT) | drop O: MSE ratio | negligible | small | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=120 (4.00 LT) | drop R: MSE ratio | negligible | small | small | small | small | replicated | small |
| rossler | allocation | oracle | H=15 (0.50 LT) | drop I: MSE ratio | undetermined | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=15 (0.50 LT) | drop N: MSE ratio | undetermined | small | small | small | small | replicated | small |
| rossler | allocation | oracle | H=15 (0.50 LT) | drop O: MSE ratio | undetermined | small | needed, size not determined | small | small | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | oracle | H=15 (0.50 LT) | drop R: MSE ratio | undetermined | substantial | substantial | needed, size not determined | substantial | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | oracle | H=30 (1.00 LT) | drop I: MSE ratio | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=30 (1.00 LT) | drop N: MSE ratio | negligible | small | negligible | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=30 (1.00 LT) | drop O: MSE ratio | small | small | small | small | small | replicated | small |
| rossler | allocation | oracle | H=30 (1.00 LT) | drop R: MSE ratio | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=60 (2.00 LT) | drop I: MSE ratio | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=60 (2.00 LT) | drop N: MSE ratio | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=60 (2.00 LT) | drop O: MSE ratio | small | small | negligible | small | small | replicated | small |
| rossler | allocation | oracle | H=60 (2.00 LT) | drop R: MSE ratio | substantial | substantial | substantial | needed, size not determined | substantial | replicated | substantial |
| rossler | allocation | oracle | H=8 (0.27 LT) | drop I: MSE ratio | undetermined | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=8 (0.27 LT) | drop N: MSE ratio | undetermined | small | small | small | small | replicated | small |
| rossler | allocation | oracle | H=8 (0.27 LT) | drop O: MSE ratio | undetermined | small | needed, size not determined | small | small | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | oracle | H=8 (0.27 LT) | drop R: MSE ratio | undetermined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| rossler | horizon | deployable | T_c | drop I: pinball ratio | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | deployable | T_c | drop N: pinball ratio | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | horizon | deployable | T_c | drop O: pinball ratio | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | deployable | T_c | drop R: pinball ratio | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | horizon | oracle | T_c | drop I: pinball ratio | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | oracle | T_c | drop N: pinball ratio | negligible | negligible | small | negligible | negligible | replicated | negligible |
| rossler | horizon | oracle | T_c | drop O: pinball ratio | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | oracle | T_c | drop R: pinball ratio | small | small | small | small | small | replicated | small |

## A vs separation

DEVELOPMENT: phase J replication (held-out development seeds), not a hypothesis test.

| system | decision | profile | horizon | item | DEV-5 | DEV-6 | DEV-7 | DEV-8 | DEV-9 | class | replicated reading or claims |
|---|---|---|---|---|---|---|---|---|---|---|---|
| chua | allocation | deployable | H=120 (4.00 LT) | I: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | deployable | H=120 (4.00 LT) | IN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | deployable | H=120 (4.00 LT) | N: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | deployable | H=120 (4.00 LT) | O: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | deployable | H=120 (4.00 LT) | OI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | deployable | H=120 (4.00 LT) | OIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | deployable | H=120 (4.00 LT) | ON: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | deployable | H=120 (4.00 LT) | R: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | deployable | H=120 (4.00 LT) | RI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | deployable | H=120 (4.00 LT) | RIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | deployable | H=120 (4.00 LT) | RN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | deployable | H=120 (4.00 LT) | RO: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | deployable | H=120 (4.00 LT) | ROI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | deployable | H=120 (4.00 LT) | ROIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | deployable | H=120 (4.00 LT) | RON: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | deployable | H=120 (4.00 LT) | none: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | deployable | H=15 (0.50 LT) | I: MSE(F)/MSE(sep) | undetermined | negligible | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | IN: MSE(F)/MSE(sep) | undetermined | negligible | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | N: MSE(F)/MSE(sep) | undetermined | negligible | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | O: MSE(F)/MSE(sep) | undetermined | negligible | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | OI: MSE(F)/MSE(sep) | undetermined | negligible | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | OIN: MSE(F)/MSE(sep) | undetermined | negligible | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | ON: MSE(F)/MSE(sep) | undetermined | negligible | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | R: MSE(F)/MSE(sep) | undetermined | negligible | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | RI: MSE(F)/MSE(sep) | undetermined | negligible | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | RIN: MSE(F)/MSE(sep) | undetermined | negligible | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | RN: MSE(F)/MSE(sep) | undetermined | negligible | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | RO: MSE(F)/MSE(sep) | undetermined | negligible | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | ROI: MSE(F)/MSE(sep) | undetermined | negligible | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | ROIN: MSE(F)/MSE(sep) | undetermined | negligible | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | RON: MSE(F)/MSE(sep) | undetermined | negligible | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | none: MSE(F)/MSE(sep) | undetermined | negligible | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | I: MSE(F)/MSE(sep) | undetermined | undetermined | negligible | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | IN: MSE(F)/MSE(sep) | undetermined | undetermined | negligible | undetermined | negligible | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | N: MSE(F)/MSE(sep) | undetermined | undetermined | negligible | undetermined | negligible | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | O: MSE(F)/MSE(sep) | undetermined | undetermined | negligible | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | OI: MSE(F)/MSE(sep) | undetermined | undetermined | negligible | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | OIN: MSE(F)/MSE(sep) | undetermined | undetermined | negligible | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | ON: MSE(F)/MSE(sep) | undetermined | undetermined | negligible | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | R: MSE(F)/MSE(sep) | undetermined | undetermined | negligible | undetermined | negligible | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | RI: MSE(F)/MSE(sep) | undetermined | undetermined | negligible | undetermined | negligible | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | RIN: MSE(F)/MSE(sep) | undetermined | undetermined | negligible | undetermined | negligible | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | RN: MSE(F)/MSE(sep) | undetermined | undetermined | negligible | undetermined | negligible | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | RO: MSE(F)/MSE(sep) | undetermined | undetermined | negligible | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | ROI: MSE(F)/MSE(sep) | undetermined | undetermined | negligible | undetermined | negligible | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | ROIN: MSE(F)/MSE(sep) | undetermined | undetermined | lowers | undetermined | negligible | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | RON: MSE(F)/MSE(sep) | undetermined | undetermined | negligible | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | none: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | I: MSE(F)/MSE(sep) | negligible | lowers | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=60 (2.00 LT) | IN: MSE(F)/MSE(sep) | negligible | lowers | lowers | negligible | lowers | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=60 (2.00 LT) | N: MSE(F)/MSE(sep) | negligible | lowers | lowers | negligible | lowers | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=60 (2.00 LT) | O: MSE(F)/MSE(sep) | negligible | lowers | negligible | negligible | lowers | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=60 (2.00 LT) | OI: MSE(F)/MSE(sep) | negligible | lowers | lowers | negligible | lowers | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=60 (2.00 LT) | OIN: MSE(F)/MSE(sep) | negligible | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | deployable | H=60 (2.00 LT) | ON: MSE(F)/MSE(sep) | negligible | lowers | lowers | negligible | lowers | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=60 (2.00 LT) | R: MSE(F)/MSE(sep) | negligible | lowers | lowers | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=60 (2.00 LT) | RI: MSE(F)/MSE(sep) | negligible | lowers | lowers | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=60 (2.00 LT) | RIN: MSE(F)/MSE(sep) | negligible | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | deployable | H=60 (2.00 LT) | RN: MSE(F)/MSE(sep) | negligible | lowers | lowers | negligible | lowers | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=60 (2.00 LT) | RO: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | deployable | H=60 (2.00 LT) | ROI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | deployable | H=60 (2.00 LT) | ROIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | deployable | H=60 (2.00 LT) | RON: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | deployable | H=60 (2.00 LT) | none: MSE(F)/MSE(sep) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=8 (0.27 LT) | I: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | IN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | N: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | O: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | OI: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | OIN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | ON: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | R: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | RI: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | RIN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | RN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | RO: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | ROI: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | ROIN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | RON: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | none: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=120 (4.00 LT) | I: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | oracle | H=120 (4.00 LT) | IN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | oracle | H=120 (4.00 LT) | N: MSE(F)/MSE(sep) | lowers | lowers | lowers | negligible | lowers | replicated | lowers |
| chua | allocation | oracle | H=120 (4.00 LT) | O: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | oracle | H=120 (4.00 LT) | OI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | oracle | H=120 (4.00 LT) | OIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | oracle | H=120 (4.00 LT) | ON: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | oracle | H=120 (4.00 LT) | R: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | oracle | H=120 (4.00 LT) | RI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | oracle | H=120 (4.00 LT) | RIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | oracle | H=120 (4.00 LT) | RN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | oracle | H=120 (4.00 LT) | RO: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | oracle | H=120 (4.00 LT) | ROI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | oracle | H=120 (4.00 LT) | ROIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | oracle | H=120 (4.00 LT) | RON: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | oracle | H=120 (4.00 LT) | none: MSE(F)/MSE(sep) | lowers | lowers | lowers | negligible | lowers | replicated | lowers |
| chua | allocation | oracle | H=15 (0.50 LT) | I: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | substantial | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | IN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | substantial | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | N: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | substantial | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | O: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | substantial | needed, size not determined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | OI: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | substantial | needed, size not determined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | OIN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | needed, size not determined | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | ON: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | substantial | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | R: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | substantial | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | RI: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | substantial | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | RIN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | needed, size not determined | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | RN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | substantial | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | RO: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | substantial | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | ROI: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | needed, size not determined | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | ROIN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | RON: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | substantial | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | none: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | substantial | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | I: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | IN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | N: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | O: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | OI: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | OIN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | ON: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | R: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | RI: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | RIN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | RN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | RO: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | ROI: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | ROIN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | RON: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | none: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=60 (2.00 LT) | I: MSE(F)/MSE(sep) | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| chua | allocation | oracle | H=60 (2.00 LT) | IN: MSE(F)/MSE(sep) | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| chua | allocation | oracle | H=60 (2.00 LT) | N: MSE(F)/MSE(sep) | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| chua | allocation | oracle | H=60 (2.00 LT) | O: MSE(F)/MSE(sep) | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| chua | allocation | oracle | H=60 (2.00 LT) | OI: MSE(F)/MSE(sep) | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| chua | allocation | oracle | H=60 (2.00 LT) | OIN: MSE(F)/MSE(sep) | small | small | small | needed, size not determined | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| chua | allocation | oracle | H=60 (2.00 LT) | ON: MSE(F)/MSE(sep) | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| chua | allocation | oracle | H=60 (2.00 LT) | R: MSE(F)/MSE(sep) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| chua | allocation | oracle | H=60 (2.00 LT) | RI: MSE(F)/MSE(sep) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| chua | allocation | oracle | H=60 (2.00 LT) | RIN: MSE(F)/MSE(sep) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=60 (2.00 LT) | RN: MSE(F)/MSE(sep) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| chua | allocation | oracle | H=60 (2.00 LT) | RO: MSE(F)/MSE(sep) | lowers | lowers | lowers | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=60 (2.00 LT) | ROI: MSE(F)/MSE(sep) | lowers | lowers | lowers | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=60 (2.00 LT) | ROIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | negligible | replicated | lowers |
| chua | allocation | oracle | H=60 (2.00 LT) | RON: MSE(F)/MSE(sep) | lowers | lowers | lowers | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=60 (2.00 LT) | none: MSE(F)/MSE(sep) | substantial | needed, size not determined | needed, size not determined | substantial | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| chua | allocation | oracle | H=8 (0.27 LT) | I: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | IN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | N: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | O: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | OI: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | OIN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | ON: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | R: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | RI: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | RIN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | RN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | RO: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | ROI: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | ROIN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | RON: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | none: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | I: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | IN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | N: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | O: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | OI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | OIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | ON: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | R: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | RI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | RIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | RN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | RO: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | ROI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | ROIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | RON: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | none: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | I: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | IN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | undetermined | replicated | lowers |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | N: MSE(F)/MSE(sep) | lowers | lowers | lowers | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | O: MSE(F)/MSE(sep) | negligible | lowers | lowers | lowers | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | OI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | undetermined | replicated | lowers |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | OIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | undetermined | replicated | lowers |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | ON: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | undetermined | replicated | lowers |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | R: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | RI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | RIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | RN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | RO: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | ROI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | undetermined | replicated | lowers |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | ROIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | negligible | replicated | lowers |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | RON: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | none: MSE(F)/MSE(sep) | negligible | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | I: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | IN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | N: MSE(F)/MSE(sep) | negligible | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | O: MSE(F)/MSE(sep) | lowers | lowers | lowers | undetermined | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | OI: MSE(F)/MSE(sep) | lowers | lowers | lowers | negligible | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | OIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | ON: MSE(F)/MSE(sep) | lowers | lowers | lowers | undetermined | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | R: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | RI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | RIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | RN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | RO: MSE(F)/MSE(sep) | lowers | lowers | lowers | undetermined | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | ROI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | ROIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | RON: MSE(F)/MSE(sep) | lowers | lowers | lowers | negligible | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | none: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | I: MSE(F)/MSE(sep) | lowers | lowers | lowers | negligible | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | IN: MSE(F)/MSE(sep) | lowers | negligible | lowers | negligible | lowers | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | N: MSE(F)/MSE(sep) | lowers | negligible | lowers | negligible | lowers | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | O: MSE(F)/MSE(sep) | lowers | lowers | lowers | negligible | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | OI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | OIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | negligible | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | ON: MSE(F)/MSE(sep) | lowers | lowers | lowers | negligible | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | R: MSE(F)/MSE(sep) | lowers | lowers | lowers | negligible | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | RI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | RIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | negligible | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | RN: MSE(F)/MSE(sep) | lowers | negligible | lowers | negligible | lowers | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | RO: MSE(F)/MSE(sep) | negligible | lowers | lowers | negligible | lowers | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | ROI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | ROIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | negligible | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | RON: MSE(F)/MSE(sep) | lowers | lowers | lowers | negligible | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | none: MSE(F)/MSE(sep) | negligible | lowers | lowers | negligible | lowers | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | I: MSE(F)/MSE(sep) | undetermined | lowers | undetermined | undetermined | lowers | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | IN: MSE(F)/MSE(sep) | undetermined | lowers | undetermined | undetermined | lowers | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | N: MSE(F)/MSE(sep) | undetermined | lowers | undetermined | undetermined | lowers | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | O: MSE(F)/MSE(sep) | undetermined | lowers | undetermined | undetermined | lowers | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | OI: MSE(F)/MSE(sep) | undetermined | lowers | undetermined | undetermined | lowers | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | OIN: MSE(F)/MSE(sep) | undetermined | lowers | undetermined | undetermined | lowers | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | ON: MSE(F)/MSE(sep) | undetermined | lowers | undetermined | undetermined | lowers | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | R: MSE(F)/MSE(sep) | undetermined | lowers | undetermined | undetermined | lowers | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | RI: MSE(F)/MSE(sep) | undetermined | lowers | undetermined | undetermined | lowers | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | RIN: MSE(F)/MSE(sep) | undetermined | lowers | undetermined | undetermined | lowers | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | RN: MSE(F)/MSE(sep) | undetermined | lowers | undetermined | undetermined | lowers | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | RO: MSE(F)/MSE(sep) | undetermined | lowers | undetermined | undetermined | lowers | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | ROI: MSE(F)/MSE(sep) | undetermined | lowers | undetermined | undetermined | lowers | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | ROIN: MSE(F)/MSE(sep) | undetermined | lowers | undetermined | undetermined | lowers | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | RON: MSE(F)/MSE(sep) | undetermined | lowers | undetermined | undetermined | lowers | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | none: MSE(F)/MSE(sep) | undetermined | lowers | undetermined | undetermined | lowers | not replicated |  |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | I: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | IN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | N: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | O: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | OI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | OIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | ON: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | R: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | RI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | RIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | RN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | RO: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | ROI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | ROIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | RON: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | none: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | I: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | IN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | N: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | O: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | OI: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | OIN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | ON: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | R: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | RI: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | RIN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | RN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | RO: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | ROI: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | ROIN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | RON: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | none: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | I: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | IN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | N: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | O: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | OI: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | OIN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | ON: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | R: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | RI: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | RIN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | RN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | RO: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | ROI: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | ROIN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | RON: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | none: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | I: MSE(F)/MSE(sep) | needed, size not determined | undetermined | undetermined | needed, size not determined | needed, size not determined | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | IN: MSE(F)/MSE(sep) | needed, size not determined | undetermined | undetermined | undetermined | needed, size not determined | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | N: MSE(F)/MSE(sep) | substantial | needed, size not determined | undetermined | needed, size not determined | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | O: MSE(F)/MSE(sep) | undetermined | negligible | negligible | needed, size not determined | negligible | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | OI: MSE(F)/MSE(sep) | negligible | negligible | lowers | undetermined | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | OIN: MSE(F)/MSE(sep) | negligible | negligible | lowers | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | ON: MSE(F)/MSE(sep) | needed, size not determined | negligible | lowers | needed, size not determined | undetermined | contradicted | DEV-5 needed, size not determined vs DEV-7 lowers |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | R: MSE(F)/MSE(sep) | needed, size not determined | needed, size not determined | undetermined | needed, size not determined | substantial | not replicated | replicated claim: ratio > 1 |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | RI: MSE(F)/MSE(sep) | needed, size not determined | undetermined | undetermined | undetermined | needed, size not determined | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | RIN: MSE(F)/MSE(sep) | needed, size not determined | undetermined | undetermined | undetermined | needed, size not determined | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | RN: MSE(F)/MSE(sep) | needed, size not determined | undetermined | undetermined | needed, size not determined | needed, size not determined | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | RO: MSE(F)/MSE(sep) | negligible | negligible | lowers | undetermined | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | ROI: MSE(F)/MSE(sep) | lowers | lowers | lowers | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | ROIN: MSE(F)/MSE(sep) | negligible | lowers | lowers | negligible | undetermined | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | RON: MSE(F)/MSE(sep) | undetermined | negligible | lowers | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | none: MSE(F)/MSE(sep) | substantial | needed, size not determined | undetermined | needed, size not determined | substantial | not replicated | replicated claim: ratio > 1 |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | I: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | IN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | N: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | O: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | OI: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | OIN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | ON: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | R: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | RI: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | RIN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | RN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | RO: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | ROI: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | ROIN: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | RON: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | none: MSE(F)/MSE(sep) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | I: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=120 (4.00 LT) | IN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=120 (4.00 LT) | N: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=120 (4.00 LT) | O: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=120 (4.00 LT) | OI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=120 (4.00 LT) | OIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=120 (4.00 LT) | ON: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=120 (4.00 LT) | R: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=120 (4.00 LT) | RI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=120 (4.00 LT) | RIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=120 (4.00 LT) | RN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=120 (4.00 LT) | RO: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=120 (4.00 LT) | ROI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=120 (4.00 LT) | ROIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=120 (4.00 LT) | RON: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=120 (4.00 LT) | none: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=15 (0.50 LT) | I: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=15 (0.50 LT) | IN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=15 (0.50 LT) | N: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=15 (0.50 LT) | O: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=15 (0.50 LT) | OI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=15 (0.50 LT) | OIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=15 (0.50 LT) | ON: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=15 (0.50 LT) | R: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=15 (0.50 LT) | RI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=15 (0.50 LT) | RIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=15 (0.50 LT) | RN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=15 (0.50 LT) | RO: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=15 (0.50 LT) | ROI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=15 (0.50 LT) | ROIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=15 (0.50 LT) | RON: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=15 (0.50 LT) | none: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=30 (1.00 LT) | I: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=30 (1.00 LT) | IN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=30 (1.00 LT) | N: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=30 (1.00 LT) | O: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=30 (1.00 LT) | OI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | negligible | replicated | lowers |
| rossler | allocation | deployable | H=30 (1.00 LT) | OIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=30 (1.00 LT) | ON: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=30 (1.00 LT) | R: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=30 (1.00 LT) | RI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=30 (1.00 LT) | RIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=30 (1.00 LT) | RN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=30 (1.00 LT) | RO: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=30 (1.00 LT) | ROI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=30 (1.00 LT) | ROIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=30 (1.00 LT) | RON: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=30 (1.00 LT) | none: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=60 (2.00 LT) | I: MSE(F)/MSE(sep) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | IN: MSE(F)/MSE(sep) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | N: MSE(F)/MSE(sep) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | O: MSE(F)/MSE(sep) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | OI: MSE(F)/MSE(sep) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | OIN: MSE(F)/MSE(sep) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | ON: MSE(F)/MSE(sep) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | R: MSE(F)/MSE(sep) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | RI: MSE(F)/MSE(sep) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | RIN: MSE(F)/MSE(sep) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | RN: MSE(F)/MSE(sep) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | RO: MSE(F)/MSE(sep) | lowers | negligible | negligible | negligible | lowers | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=60 (2.00 LT) | ROI: MSE(F)/MSE(sep) | lowers | lowers | small | negligible | lowers | contradicted | DEV-5 lowers vs DEV-7 small; replicated claim within a contradicted row: ratio <= 1.05 |
| rossler | allocation | deployable | H=60 (2.00 LT) | ROIN: MSE(F)/MSE(sep) | lowers | lowers | needed, size not determined | negligible | lowers | contradicted | DEV-5 lowers vs DEV-7 needed, size not determined; replicated claim within a contradicted row: ratio <= 1.05 |
| rossler | allocation | deployable | H=60 (2.00 LT) | RON: MSE(F)/MSE(sep) | lowers | negligible | small | negligible | lowers | contradicted | DEV-5 lowers vs DEV-7 small; replicated claim within a contradicted row: ratio <= 1.05 |
| rossler | allocation | deployable | H=60 (2.00 LT) | none: MSE(F)/MSE(sep) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=8 (0.27 LT) | I: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=8 (0.27 LT) | IN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=8 (0.27 LT) | N: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=8 (0.27 LT) | O: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=8 (0.27 LT) | OI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=8 (0.27 LT) | OIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=8 (0.27 LT) | ON: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=8 (0.27 LT) | R: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=8 (0.27 LT) | RI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=8 (0.27 LT) | RIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=8 (0.27 LT) | RN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=8 (0.27 LT) | RO: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=8 (0.27 LT) | ROI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=8 (0.27 LT) | ROIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=8 (0.27 LT) | RON: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=8 (0.27 LT) | none: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=120 (4.00 LT) | I: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=120 (4.00 LT) | IN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=120 (4.00 LT) | N: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=120 (4.00 LT) | O: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=120 (4.00 LT) | OI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=120 (4.00 LT) | OIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=120 (4.00 LT) | ON: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=120 (4.00 LT) | R: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=120 (4.00 LT) | RI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=120 (4.00 LT) | RIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=120 (4.00 LT) | RN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=120 (4.00 LT) | RO: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=120 (4.00 LT) | ROI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=120 (4.00 LT) | ROIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=120 (4.00 LT) | RON: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=120 (4.00 LT) | none: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=15 (0.50 LT) | I: MSE(F)/MSE(sep) | needed, size not determined | needed, size not determined | needed, size not determined | small | needed, size not determined | replicated | needed, size not determined |
| rossler | allocation | oracle | H=15 (0.50 LT) | IN: MSE(F)/MSE(sep) | needed, size not determined | small | needed, size not determined | negligible | small | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | oracle | H=15 (0.50 LT) | N: MSE(F)/MSE(sep) | needed, size not determined | small | needed, size not determined | negligible | small | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | oracle | H=15 (0.50 LT) | O: MSE(F)/MSE(sep) | needed, size not determined | needed, size not determined | needed, size not determined | small | needed, size not determined | replicated | needed, size not determined |
| rossler | allocation | oracle | H=15 (0.50 LT) | OI: MSE(F)/MSE(sep) | needed, size not determined | needed, size not determined | needed, size not determined | small | needed, size not determined | replicated | needed, size not determined |
| rossler | allocation | oracle | H=15 (0.50 LT) | OIN: MSE(F)/MSE(sep) | needed, size not determined | small | needed, size not determined | negligible | negligible | not replicated |  |
| rossler | allocation | oracle | H=15 (0.50 LT) | ON: MSE(F)/MSE(sep) | needed, size not determined | small | needed, size not determined | negligible | small | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | oracle | H=15 (0.50 LT) | R: MSE(F)/MSE(sep) | undetermined | lowers | negligible | lowers | lowers | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=15 (0.50 LT) | RI: MSE(F)/MSE(sep) | undetermined | lowers | undetermined | lowers | lowers | not replicated |  |
| rossler | allocation | oracle | H=15 (0.50 LT) | RIN: MSE(F)/MSE(sep) | negligible | lowers | negligible | lowers | lowers | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=15 (0.50 LT) | RN: MSE(F)/MSE(sep) | undetermined | lowers | negligible | lowers | lowers | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=15 (0.50 LT) | RO: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=15 (0.50 LT) | ROI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=15 (0.50 LT) | ROIN: MSE(F)/MSE(sep) | negligible | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=15 (0.50 LT) | RON: MSE(F)/MSE(sep) | negligible | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=15 (0.50 LT) | none: MSE(F)/MSE(sep) | needed, size not determined | needed, size not determined | needed, size not determined | small | needed, size not determined | replicated | needed, size not determined |
| rossler | allocation | oracle | H=30 (1.00 LT) | I: MSE(F)/MSE(sep) | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=30 (1.00 LT) | IN: MSE(F)/MSE(sep) | substantial | substantial | substantial | needed, size not determined | substantial | replicated | substantial |
| rossler | allocation | oracle | H=30 (1.00 LT) | N: MSE(F)/MSE(sep) | substantial | substantial | substantial | needed, size not determined | substantial | replicated | substantial |
| rossler | allocation | oracle | H=30 (1.00 LT) | O: MSE(F)/MSE(sep) | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=30 (1.00 LT) | OI: MSE(F)/MSE(sep) | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=30 (1.00 LT) | OIN: MSE(F)/MSE(sep) | substantial | substantial | substantial | needed, size not determined | substantial | replicated | substantial |
| rossler | allocation | oracle | H=30 (1.00 LT) | ON: MSE(F)/MSE(sep) | substantial | substantial | substantial | needed, size not determined | substantial | replicated | substantial |
| rossler | allocation | oracle | H=30 (1.00 LT) | R: MSE(F)/MSE(sep) | small | negligible | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=30 (1.00 LT) | RI: MSE(F)/MSE(sep) | small | negligible | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=30 (1.00 LT) | RIN: MSE(F)/MSE(sep) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=30 (1.00 LT) | RN: MSE(F)/MSE(sep) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=30 (1.00 LT) | RO: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=30 (1.00 LT) | ROI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=30 (1.00 LT) | ROIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=30 (1.00 LT) | RON: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=30 (1.00 LT) | none: MSE(F)/MSE(sep) | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=60 (2.00 LT) | I: MSE(F)/MSE(sep) | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=60 (2.00 LT) | IN: MSE(F)/MSE(sep) | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=60 (2.00 LT) | N: MSE(F)/MSE(sep) | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=60 (2.00 LT) | O: MSE(F)/MSE(sep) | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=60 (2.00 LT) | OI: MSE(F)/MSE(sep) | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=60 (2.00 LT) | OIN: MSE(F)/MSE(sep) | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=60 (2.00 LT) | ON: MSE(F)/MSE(sep) | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=60 (2.00 LT) | R: MSE(F)/MSE(sep) | small | small | small | small | small | replicated | small |
| rossler | allocation | oracle | H=60 (2.00 LT) | RI: MSE(F)/MSE(sep) | small | small | small | small | small | replicated | small |
| rossler | allocation | oracle | H=60 (2.00 LT) | RIN: MSE(F)/MSE(sep) | small | small | needed, size not determined | small | small | replicated | small |
| rossler | allocation | oracle | H=60 (2.00 LT) | RN: MSE(F)/MSE(sep) | small | small | small | small | small | replicated | small |
| rossler | allocation | oracle | H=60 (2.00 LT) | RO: MSE(F)/MSE(sep) | negligible | small | small | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=60 (2.00 LT) | ROI: MSE(F)/MSE(sep) | negligible | small | small | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=60 (2.00 LT) | ROIN: MSE(F)/MSE(sep) | negligible | small | small | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=60 (2.00 LT) | RON: MSE(F)/MSE(sep) | negligible | small | small | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=60 (2.00 LT) | none: MSE(F)/MSE(sep) | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=8 (0.27 LT) | I: MSE(F)/MSE(sep) | needed, size not determined | small | needed, size not determined | negligible | small | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | oracle | H=8 (0.27 LT) | IN: MSE(F)/MSE(sep) | undetermined | negligible | undetermined | lowers | lowers | not replicated |  |
| rossler | allocation | oracle | H=8 (0.27 LT) | N: MSE(F)/MSE(sep) | undetermined | negligible | undetermined | lowers | lowers | not replicated |  |
| rossler | allocation | oracle | H=8 (0.27 LT) | O: MSE(F)/MSE(sep) | needed, size not determined | small | needed, size not determined | negligible | small | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | oracle | H=8 (0.27 LT) | OI: MSE(F)/MSE(sep) | needed, size not determined | small | needed, size not determined | negligible | small | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | oracle | H=8 (0.27 LT) | OIN: MSE(F)/MSE(sep) | undetermined | negligible | undetermined | lowers | lowers | not replicated |  |
| rossler | allocation | oracle | H=8 (0.27 LT) | ON: MSE(F)/MSE(sep) | undetermined | negligible | undetermined | lowers | lowers | not replicated |  |
| rossler | allocation | oracle | H=8 (0.27 LT) | R: MSE(F)/MSE(sep) | negligible | lowers | negligible | lowers | lowers | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=8 (0.27 LT) | RI: MSE(F)/MSE(sep) | negligible | lowers | negligible | lowers | lowers | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=8 (0.27 LT) | RIN: MSE(F)/MSE(sep) | negligible | lowers | negligible | lowers | lowers | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=8 (0.27 LT) | RN: MSE(F)/MSE(sep) | negligible | lowers | negligible | lowers | lowers | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=8 (0.27 LT) | RO: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=8 (0.27 LT) | ROI: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=8 (0.27 LT) | ROIN: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=8 (0.27 LT) | RON: MSE(F)/MSE(sep) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=8 (0.27 LT) | none: MSE(F)/MSE(sep) | needed, size not determined | small | needed, size not determined | negligible | small | not replicated | replicated claim: ratio > 1 |

## B loss ratio

DEVELOPMENT: phase J replication (held-out development seeds), not a hypothesis test.

| system | decision | profile | horizon | item | DEV-5 | DEV-6 | DEV-7 | DEV-8 | DEV-9 | class | replicated reading or claims |
|---|---|---|---|---|---|---|---|---|---|---|---|
| chua | allocation | deployable | H=120 (4.00 LT) | decision IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | decision OI: L(add)/L(pair) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | decision ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | decision RI: L(add)/L(pair) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | decision RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | decision RO: L(add)/L(pair) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | logit IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | logit OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | logit ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | logit RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | logit RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | logit RO: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | one IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | one OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | one ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | one RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | one RN: L(add)/L(pair) | small | negligible | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=120 (4.00 LT) | one RO: L(add)/L(pair) | negligible | negligible | negligible | negligible | small | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | zero IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | zero OI: L(add)/L(pair) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | zero ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | zero RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | zero RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | zero RO: L(add)/L(pair) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| chua | allocation | deployable | H=15 (0.50 LT) | decision IN: L(add)/L(pair) | undetermined | negligible | negligible | needed, size not determined | negligible | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | decision OI: L(add)/L(pair) | undetermined | small | negligible | negligible | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | decision ON: L(add)/L(pair) | negligible | small | small | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=15 (0.50 LT) | decision RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=15 (0.50 LT) | decision RN: L(add)/L(pair) | negligible | undetermined | negligible | negligible | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | decision RO: L(add)/L(pair) | negligible | undetermined | negligible | negligible | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | logit IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=15 (0.50 LT) | logit OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=15 (0.50 LT) | logit ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=15 (0.50 LT) | logit RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=15 (0.50 LT) | logit RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=15 (0.50 LT) | logit RO: L(add)/L(pair) | small | negligible | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=15 (0.50 LT) | zero IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=15 (0.50 LT) | zero OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | small | replicated | negligible |
| chua | allocation | deployable | H=15 (0.50 LT) | zero ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=15 (0.50 LT) | zero RI: L(add)/L(pair) | small | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=15 (0.50 LT) | zero RN: L(add)/L(pair) | small | negligible | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=15 (0.50 LT) | zero RO: L(add)/L(pair) | small | negligible | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=30 (1.00 LT) | decision IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=30 (1.00 LT) | decision OI: L(add)/L(pair) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| chua | allocation | deployable | H=30 (1.00 LT) | decision ON: L(add)/L(pair) | negligible | small | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=30 (1.00 LT) | decision RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=30 (1.00 LT) | decision RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=30 (1.00 LT) | decision RO: L(add)/L(pair) | negligible | undetermined | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=30 (1.00 LT) | logit IN: L(add)/L(pair) | small | negligible | negligible | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=30 (1.00 LT) | logit OI: L(add)/L(pair) | small | small | small | small | small | replicated | small |
| chua | allocation | deployable | H=30 (1.00 LT) | logit ON: L(add)/L(pair) | negligible | negligible | negligible | small | small | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=30 (1.00 LT) | logit RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=30 (1.00 LT) | logit RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=30 (1.00 LT) | logit RO: L(add)/L(pair) | negligible | small | small | small | small | replicated | small |
| chua | allocation | deployable | H=30 (1.00 LT) | zero IN: L(add)/L(pair) | negligible | small | negligible | small | small | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=30 (1.00 LT) | zero OI: L(add)/L(pair) | small | small | small | negligible | small | replicated | small |
| chua | allocation | deployable | H=30 (1.00 LT) | zero ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=30 (1.00 LT) | zero RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=30 (1.00 LT) | zero RN: L(add)/L(pair) | negligible | negligible | small | small | small | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=30 (1.00 LT) | zero RO: L(add)/L(pair) | negligible | negligible | negligible | negligible | no interaction gain; the pair model fits worse | replicated | negligible |
| chua | allocation | deployable | H=60 (2.00 LT) | decision IN: L(add)/L(pair) | negligible | small | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=60 (2.00 LT) | decision OI: L(add)/L(pair) | small | needed, size not determined | small | needed, size not determined | negligible | not replicated | replicated claim: ratio > 1 |
| chua | allocation | deployable | H=60 (2.00 LT) | decision ON: L(add)/L(pair) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| chua | allocation | deployable | H=60 (2.00 LT) | decision RI: L(add)/L(pair) | negligible | small | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=60 (2.00 LT) | decision RN: L(add)/L(pair) | small | negligible | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=60 (2.00 LT) | decision RO: L(add)/L(pair) | negligible | small | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=60 (2.00 LT) | logit IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=60 (2.00 LT) | logit OI: L(add)/L(pair) | negligible | negligible | small | small | small | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=60 (2.00 LT) | logit ON: L(add)/L(pair) | small | negligible | small | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=60 (2.00 LT) | logit RI: L(add)/L(pair) | negligible | negligible | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=60 (2.00 LT) | logit RN: L(add)/L(pair) | small | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=60 (2.00 LT) | logit RO: L(add)/L(pair) | small | small | negligible | small | small | replicated | small |
| chua | allocation | deployable | H=60 (2.00 LT) | one IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=60 (2.00 LT) | one OI: L(add)/L(pair) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| chua | allocation | deployable | H=60 (2.00 LT) | one ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=60 (2.00 LT) | one RI: L(add)/L(pair) | no interaction gain; the pair model fits worse | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=60 (2.00 LT) | one RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | small | replicated | negligible |
| chua | allocation | deployable | H=60 (2.00 LT) | one RO: L(add)/L(pair) | negligible | small | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=60 (2.00 LT) | zero IN: L(add)/L(pair) | small | small | small | small | small | replicated | small |
| chua | allocation | deployable | H=60 (2.00 LT) | zero OI: L(add)/L(pair) | small | negligible | small | small | small | replicated | small |
| chua | allocation | deployable | H=60 (2.00 LT) | zero ON: L(add)/L(pair) | small | small | small | negligible | small | replicated | small |
| chua | allocation | deployable | H=60 (2.00 LT) | zero RI: L(add)/L(pair) | negligible | negligible | negligible | small | small | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=60 (2.00 LT) | zero RN: L(add)/L(pair) | negligible | negligible | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=60 (2.00 LT) | zero RO: L(add)/L(pair) | small | small | small | small | small | replicated | small |
| chua | allocation | deployable | H=8 (0.27 LT) | decision IN: L(add)/L(pair) | negligible | negligible | negligible | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | decision OI: L(add)/L(pair) | undetermined | negligible | no interaction gain; the pair model fits worse | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | decision ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=8 (0.27 LT) | decision RI: L(add)/L(pair) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| chua | allocation | deployable | H=8 (0.27 LT) | decision RN: L(add)/L(pair) | negligible | negligible | small | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=8 (0.27 LT) | decision RO: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=8 (0.27 LT) | logit IN: L(add)/L(pair) | negligible | negligible | small | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=8 (0.27 LT) | logit OI: L(add)/L(pair) | negligible | negligible | small | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=8 (0.27 LT) | logit ON: L(add)/L(pair) | negligible | negligible | small | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=8 (0.27 LT) | logit RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=8 (0.27 LT) | logit RN: L(add)/L(pair) | negligible | small | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=8 (0.27 LT) | logit RO: L(add)/L(pair) | negligible | small | negligible | small | small | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=8 (0.27 LT) | zero IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=8 (0.27 LT) | zero OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=8 (0.27 LT) | zero ON: L(add)/L(pair) | negligible | negligible | negligible | small | small | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=8 (0.27 LT) | zero RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=8 (0.27 LT) | zero RN: L(add)/L(pair) | small | negligible | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=8 (0.27 LT) | zero RO: L(add)/L(pair) | negligible | negligible | negligible | negligible | small | replicated | negligible |
| chua | allocation | oracle | H=120 (4.00 LT) | decision IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=120 (4.00 LT) | decision OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=120 (4.00 LT) | decision ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=120 (4.00 LT) | decision RI: L(add)/L(pair) | small | negligible | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=120 (4.00 LT) | decision RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=120 (4.00 LT) | decision RO: L(add)/L(pair) | negligible | small | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=120 (4.00 LT) | logit IN: L(add)/L(pair) | negligible | small | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=120 (4.00 LT) | logit OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=120 (4.00 LT) | logit ON: L(add)/L(pair) | negligible | small | negligible | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=120 (4.00 LT) | logit RI: L(add)/L(pair) | negligible | small | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=120 (4.00 LT) | logit RN: L(add)/L(pair) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| chua | allocation | oracle | H=120 (4.00 LT) | logit RO: L(add)/L(pair) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| chua | allocation | oracle | H=120 (4.00 LT) | one IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=120 (4.00 LT) | one OI: L(add)/L(pair) | small | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=120 (4.00 LT) | one ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=120 (4.00 LT) | one RI: L(add)/L(pair) | small | small | negligible | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=120 (4.00 LT) | one RN: L(add)/L(pair) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| chua | allocation | oracle | H=120 (4.00 LT) | one RO: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=120 (4.00 LT) | zero IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=120 (4.00 LT) | zero OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=120 (4.00 LT) | zero ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=120 (4.00 LT) | zero RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | small | replicated | negligible |
| chua | allocation | oracle | H=120 (4.00 LT) | zero RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=120 (4.00 LT) | zero RO: L(add)/L(pair) | negligible | small | negligible | small | small | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=15 (0.50 LT) | decision IN: L(add)/L(pair) | needed, size not determined | negligible | negligible | undetermined | negligible | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | decision OI: L(add)/L(pair) | needed, size not determined | negligible | negligible | undetermined | negligible | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | decision ON: L(add)/L(pair) | negligible | negligible | needed, size not determined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | decision RI: L(add)/L(pair) | needed, size not determined | negligible | negligible | undetermined | negligible | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | decision RN: L(add)/L(pair) | negligible | negligible | negligible | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | decision RO: L(add)/L(pair) | undetermined | needed, size not determined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | logit IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=15 (0.50 LT) | logit OI: L(add)/L(pair) | small | small | negligible | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=15 (0.50 LT) | logit ON: L(add)/L(pair) | small | small | small | negligible | small | replicated | small |
| chua | allocation | oracle | H=15 (0.50 LT) | logit RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=15 (0.50 LT) | logit RN: L(add)/L(pair) | negligible | small | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=15 (0.50 LT) | logit RO: L(add)/L(pair) | small | small | negligible | small | small | replicated | small |
| chua | allocation | oracle | H=15 (0.50 LT) | zero IN: L(add)/L(pair) | negligible | small | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=15 (0.50 LT) | zero OI: L(add)/L(pair) | negligible | negligible | negligible | small | small | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=15 (0.50 LT) | zero ON: L(add)/L(pair) | small | small | negligible | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=15 (0.50 LT) | zero RI: L(add)/L(pair) | negligible | small | negligible | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=15 (0.50 LT) | zero RN: L(add)/L(pair) | negligible | small | negligible | small | small | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=15 (0.50 LT) | zero RO: L(add)/L(pair) | small | small | small | small | small | replicated | small |
| chua | allocation | oracle | H=30 (1.00 LT) | decision IN: L(add)/L(pair) | needed, size not determined | negligible | negligible | small | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | decision OI: L(add)/L(pair) | needed, size not determined | negligible | negligible | small | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | decision ON: L(add)/L(pair) | needed, size not determined | small | negligible | needed, size not determined | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | decision RI: L(add)/L(pair) | needed, size not determined | small | negligible | negligible | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | decision RN: L(add)/L(pair) | undetermined | negligible | negligible | negligible | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | decision RO: L(add)/L(pair) | needed, size not determined | needed, size not determined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | logit IN: L(add)/L(pair) | small | negligible | negligible | small | small | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=30 (1.00 LT) | logit OI: L(add)/L(pair) | small | small | negligible | small | small | replicated | small |
| chua | allocation | oracle | H=30 (1.00 LT) | logit ON: L(add)/L(pair) | negligible | small | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=30 (1.00 LT) | logit RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=30 (1.00 LT) | logit RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=30 (1.00 LT) | logit RO: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=30 (1.00 LT) | zero IN: L(add)/L(pair) | small | small | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=30 (1.00 LT) | zero OI: L(add)/L(pair) | small | small | small | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=30 (1.00 LT) | zero ON: L(add)/L(pair) | negligible | small | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=30 (1.00 LT) | zero RI: L(add)/L(pair) | small | small | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=30 (1.00 LT) | zero RN: L(add)/L(pair) | small | negligible | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=30 (1.00 LT) | zero RO: L(add)/L(pair) | small | small | small | small | negligible | replicated | small |
| chua | allocation | oracle | H=60 (2.00 LT) | decision IN: L(add)/L(pair) | negligible | negligible | small | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=60 (2.00 LT) | decision OI: L(add)/L(pair) | negligible | negligible | small | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=60 (2.00 LT) | decision ON: L(add)/L(pair) | negligible | negligible | small | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=60 (2.00 LT) | decision RI: L(add)/L(pair) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| chua | allocation | oracle | H=60 (2.00 LT) | decision RN: L(add)/L(pair) | needed, size not determined | small | negligible | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=60 (2.00 LT) | decision RO: L(add)/L(pair) | needed, size not determined | negligible | needed, size not determined | undetermined | negligible | not replicated |  |
| chua | allocation | oracle | H=60 (2.00 LT) | logit IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=60 (2.00 LT) | logit OI: L(add)/L(pair) | small | negligible | small | small | small | replicated | small |
| chua | allocation | oracle | H=60 (2.00 LT) | logit ON: L(add)/L(pair) | negligible | negligible | small | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=60 (2.00 LT) | logit RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=60 (2.00 LT) | logit RN: L(add)/L(pair) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| chua | allocation | oracle | H=60 (2.00 LT) | logit RO: L(add)/L(pair) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| chua | allocation | oracle | H=60 (2.00 LT) | one IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=60 (2.00 LT) | one OI: L(add)/L(pair) | negligible | negligible | small | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=60 (2.00 LT) | one ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=60 (2.00 LT) | one RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=60 (2.00 LT) | one RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=60 (2.00 LT) | one RO: L(add)/L(pair) | small | negligible | negligible | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=60 (2.00 LT) | zero IN: L(add)/L(pair) | small | small | small | small | small | replicated | small |
| chua | allocation | oracle | H=60 (2.00 LT) | zero OI: L(add)/L(pair) | small | negligible | small | small | small | replicated | small |
| chua | allocation | oracle | H=60 (2.00 LT) | zero ON: L(add)/L(pair) | small | negligible | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=60 (2.00 LT) | zero RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | small | replicated | negligible |
| chua | allocation | oracle | H=60 (2.00 LT) | zero RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | small | replicated | negligible |
| chua | allocation | oracle | H=60 (2.00 LT) | zero RO: L(add)/L(pair) | negligible | small | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=8 (0.27 LT) | decision IN: L(add)/L(pair) | small | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | decision OI: L(add)/L(pair) | negligible | undetermined | undetermined | undetermined | negligible | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | decision ON: L(add)/L(pair) | negligible | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | decision RI: L(add)/L(pair) | negligible | no interaction gain; the pair model fits worse | undetermined | needed, size not determined | undetermined | contradicted | DEV-6 no interaction gain; the pair model fits worse vs DEV-8 needed, size not determined |
| chua | allocation | oracle | H=8 (0.27 LT) | decision RN: L(add)/L(pair) | small | undetermined | needed, size not determined | needed, size not determined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | decision RO: L(add)/L(pair) | needed, size not determined | undetermined | undetermined | needed, size not determined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | logit IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=8 (0.27 LT) | logit OI: L(add)/L(pair) | negligible | small | small | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=8 (0.27 LT) | logit ON: L(add)/L(pair) | negligible | small | small | small | small | replicated | small |
| chua | allocation | oracle | H=8 (0.27 LT) | logit RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=8 (0.27 LT) | logit RN: L(add)/L(pair) | negligible | negligible | negligible | small | small | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=8 (0.27 LT) | logit RO: L(add)/L(pair) | small | small | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=8 (0.27 LT) | zero IN: L(add)/L(pair) | negligible | negligible | small | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=8 (0.27 LT) | zero OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=8 (0.27 LT) | zero ON: L(add)/L(pair) | negligible | negligible | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=8 (0.27 LT) | zero RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | small | replicated | negligible |
| chua | allocation | oracle | H=8 (0.27 LT) | zero RN: L(add)/L(pair) | small | negligible | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=8 (0.27 LT) | zero RO: L(add)/L(pair) | small | small | negligible | small | small | replicated | small |
| chua | horizon | deployable | T_c | log T IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | horizon | deployable | T_c | log T OI: L(add)/L(pair) | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| chua | horizon | deployable | T_c | log T ON: L(add)/L(pair) | small | small | negligible | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | horizon | deployable | T_c | log T RI: L(add)/L(pair) | small | small | negligible | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | horizon | deployable | T_c | log T RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | horizon | deployable | T_c | log T RO: L(add)/L(pair) | small | negligible | small | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | horizon | oracle | T_c | log T IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | horizon | oracle | T_c | log T OI: L(add)/L(pair) | needed, size not determined | small | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| chua | horizon | oracle | T_c | log T ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | small | replicated | negligible |
| chua | horizon | oracle | T_c | log T RI: L(add)/L(pair) | small | small | negligible | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | horizon | oracle | T_c | log T RN: L(add)/L(pair) | small | negligible | negligible | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| chua | horizon | oracle | T_c | log T RO: L(add)/L(pair) | small | negligible | negligible | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | decision IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | decision OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | decision ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | decision RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | decision RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | decision RO: L(add)/L(pair) | negligible | negligible | negligible | negligible | no interaction gain; the pair model fits worse | replicated | negligible |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | logit IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | logit OI: L(add)/L(pair) | negligible | negligible | small | small | small | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | logit ON: L(add)/L(pair) | negligible | negligible | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | logit RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | small | replicated | negligible |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | logit RN: L(add)/L(pair) | negligible | small | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | logit RO: L(add)/L(pair) | negligible | small | small | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | one IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | one OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | one ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | small | replicated | negligible |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | one RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | one RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | one RO: L(add)/L(pair) | negligible | negligible | negligible | negligible | small | replicated | negligible |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | zero IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | zero OI: L(add)/L(pair) | negligible | negligible | small | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | zero ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | zero RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | zero RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | zero RO: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | decision IN: L(add)/L(pair) | undetermined | undetermined | needed, size not determined | needed, size not determined | negligible | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | decision OI: L(add)/L(pair) | undetermined | negligible | undetermined | undetermined | negligible | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | decision ON: L(add)/L(pair) | needed, size not determined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | decision RI: L(add)/L(pair) | undetermined | undetermined | undetermined | substantial | negligible | contradicted | DEV-8 substantial vs DEV-9 negligible |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | decision RN: L(add)/L(pair) | undetermined | undetermined | undetermined | undetermined | negligible | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | decision RO: L(add)/L(pair) | undetermined | undetermined | undetermined | undetermined | negligible | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | logit IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | logit OI: L(add)/L(pair) | negligible | small | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | logit ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | logit RI: L(add)/L(pair) | negligible | small | negligible | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | logit RN: L(add)/L(pair) | negligible | negligible | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | logit RO: L(add)/L(pair) | small | undetermined | needed, size not determined | small | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | zero IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | zero OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | zero ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | zero RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | zero RN: L(add)/L(pair) | small | negligible | small | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | zero RO: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | decision IN: L(add)/L(pair) | undetermined | undetermined | needed, size not determined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | decision OI: L(add)/L(pair) | undetermined | undetermined | undetermined | undetermined | needed, size not determined | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | decision ON: L(add)/L(pair) | needed, size not determined | needed, size not determined | negligible | needed, size not determined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | decision RI: L(add)/L(pair) | needed, size not determined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | decision RN: L(add)/L(pair) | undetermined | negligible | undetermined | undetermined | negligible | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | decision RO: L(add)/L(pair) | undetermined | small | undetermined | needed, size not determined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | logit IN: L(add)/L(pair) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | logit OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | small | replicated | negligible |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | logit ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | logit RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | small | replicated | negligible |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | logit RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | logit RO: L(add)/L(pair) | small | negligible | needed, size not determined | small | small | not replicated | replicated claim: ratio > 1; ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | zero IN: L(add)/L(pair) | small | small | negligible | small | small | replicated | small |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | zero OI: L(add)/L(pair) | small | small | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | zero ON: L(add)/L(pair) | small | negligible | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | zero RI: L(add)/L(pair) | small | small | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | zero RN: L(add)/L(pair) | small | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | zero RO: L(add)/L(pair) | small | small | negligible | small | small | replicated | small |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | decision IN: L(add)/L(pair) | negligible | undetermined | negligible | undetermined | negligible | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | decision OI: L(add)/L(pair) | negligible | undetermined | negligible | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | decision ON: L(add)/L(pair) | negligible | undetermined | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | decision RI: L(add)/L(pair) | undetermined | undetermined | undetermined | negligible | needed, size not determined | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | decision RN: L(add)/L(pair) | undetermined | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | decision RO: L(add)/L(pair) | undetermined | small | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | logit IN: L(add)/L(pair) | small | small | negligible | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | logit OI: L(add)/L(pair) | negligible | small | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | logit ON: L(add)/L(pair) | small | negligible | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | logit RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | logit RN: L(add)/L(pair) | small | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | logit RO: L(add)/L(pair) | small | negligible | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | zero IN: L(add)/L(pair) | small | small | negligible | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | zero OI: L(add)/L(pair) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | zero ON: L(add)/L(pair) | small | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | zero RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | zero RN: L(add)/L(pair) | small | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | zero RO: L(add)/L(pair) | small | negligible | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | decision IN: L(add)/L(pair) | negligible | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | decision OI: L(add)/L(pair) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | decision ON: L(add)/L(pair) | negligible | undetermined | negligible | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | decision RI: L(add)/L(pair) | negligible | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | decision RN: L(add)/L(pair) | negligible | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | decision RO: L(add)/L(pair) | negligible | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | logit IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | logit OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | logit ON: L(add)/L(pair) | negligible | negligible | negligible | no interaction gain; the pair model fits worse | no interaction gain; the pair model fits worse | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | logit RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | no interaction gain; the pair model fits worse | replicated | negligible |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | logit RN: L(add)/L(pair) | small | negligible | negligible | negligible | no interaction gain; the pair model fits worse | contradicted | DEV-5 small vs DEV-9 no interaction gain; the pair model fits worse; replicated claim within a contradicted row: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | logit RO: L(add)/L(pair) | negligible | small | negligible | small | small | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | zero IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | zero OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | zero ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | zero RI: L(add)/L(pair) | small | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | zero RN: L(add)/L(pair) | small | small | small | small | small | replicated | small |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | zero RO: L(add)/L(pair) | negligible | small | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | decision IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | decision OI: L(add)/L(pair) | negligible | small | small | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | decision ON: L(add)/L(pair) | small | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | decision RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | decision RN: L(add)/L(pair) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | decision RO: L(add)/L(pair) | negligible | small | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | logit IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | logit OI: L(add)/L(pair) | small | small | small | small | small | replicated | small |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | logit ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | logit RI: L(add)/L(pair) | negligible | negligible | small | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | logit RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | logit RO: L(add)/L(pair) | negligible | small | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | one IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | one OI: L(add)/L(pair) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | one ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | one RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | one RN: L(add)/L(pair) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | one RO: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | zero IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | zero OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | zero ON: L(add)/L(pair) | small | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | zero RI: L(add)/L(pair) | negligible | small | small | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | zero RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | zero RO: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | decision IN: L(add)/L(pair) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | decision OI: L(add)/L(pair) | undetermined | undetermined | undetermined | substantial | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | decision ON: L(add)/L(pair) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | decision RI: L(add)/L(pair) | undetermined | negligible | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | decision RN: L(add)/L(pair) | needed, size not determined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | decision RO: L(add)/L(pair) | substantial | undetermined | undetermined | substantial | substantial | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | logit IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | logit OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | logit ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | logit RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | logit RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | logit RO: L(add)/L(pair) | negligible | small | needed, size not determined | negligible | needed, size not determined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | zero IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | zero OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | zero ON: L(add)/L(pair) | small | negligible | negligible | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | zero RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | zero RN: L(add)/L(pair) | small | small | small | small | small | replicated | small |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | zero RO: L(add)/L(pair) | small | small | small | small | small | replicated | small |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | decision IN: L(add)/L(pair) | undetermined | substantial | negligible | undetermined | undetermined | contradicted | DEV-6 substantial vs DEV-7 negligible |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | decision OI: L(add)/L(pair) | undetermined | substantial | needed, size not determined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | decision ON: L(add)/L(pair) | negligible | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | decision RI: L(add)/L(pair) | needed, size not determined | needed, size not determined | needed, size not determined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | decision RN: L(add)/L(pair) | undetermined | negligible | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | decision RO: L(add)/L(pair) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | logit IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | logit OI: L(add)/L(pair) | negligible | negligible | needed, size not determined | needed, size not determined | negligible | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | logit ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | logit RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | logit RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | logit RO: L(add)/L(pair) | undetermined | negligible | undetermined | negligible | needed, size not determined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | zero IN: L(add)/L(pair) | negligible | small | small | small | small | replicated | small |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | zero OI: L(add)/L(pair) | small | small | negligible | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | zero ON: L(add)/L(pair) | small | negligible | negligible | small | small | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | zero RI: L(add)/L(pair) | negligible | negligible | negligible | small | small | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | zero RN: L(add)/L(pair) | small | small | negligible | small | small | replicated | small |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | zero RO: L(add)/L(pair) | small | small | small | small | small | replicated | small |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | decision IN: L(add)/L(pair) | needed, size not determined | undetermined | negligible | negligible | negligible | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | decision OI: L(add)/L(pair) | needed, size not determined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | decision ON: L(add)/L(pair) | negligible | negligible | no interaction gain; the pair model fits worse | undetermined | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | decision RI: L(add)/L(pair) | undetermined | undetermined | undetermined | undetermined | negligible | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | decision RN: L(add)/L(pair) | undetermined | negligible | undetermined | negligible | negligible | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | decision RO: L(add)/L(pair) | undetermined | undetermined | negligible | needed, size not determined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | logit IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | logit OI: L(add)/L(pair) | small | negligible | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | logit ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | logit RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | small | replicated | negligible |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | logit RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | logit RO: L(add)/L(pair) | negligible | negligible | needed, size not determined | needed, size not determined | needed, size not determined | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | zero IN: L(add)/L(pair) | small | small | small | negligible | small | replicated | small |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | zero OI: L(add)/L(pair) | small | small | small | small | small | replicated | small |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | zero ON: L(add)/L(pair) | small | small | small | small | small | replicated | small |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | zero RI: L(add)/L(pair) | negligible | small | negligible | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | zero RN: L(add)/L(pair) | negligible | negligible | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | zero RO: L(add)/L(pair) | small | small | small | small | small | replicated | small |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | decision IN: L(add)/L(pair) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | decision OI: L(add)/L(pair) | undetermined | undetermined | undetermined | substantial | substantial | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | decision ON: L(add)/L(pair) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | decision RI: L(add)/L(pair) | undetermined | undetermined | undetermined | undetermined | negligible | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | decision RN: L(add)/L(pair) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | decision RO: L(add)/L(pair) | substantial | undetermined | undetermined | substantial | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | logit IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | logit OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | logit ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | logit RI: L(add)/L(pair) | small | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | logit RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | logit RO: L(add)/L(pair) | needed, size not determined | undetermined | needed, size not determined | undetermined | needed, size not determined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | zero IN: L(add)/L(pair) | small | small | small | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | zero OI: L(add)/L(pair) | small | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | zero ON: L(add)/L(pair) | small | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | zero RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | zero RN: L(add)/L(pair) | small | small | small | small | small | replicated | small |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | zero RO: L(add)/L(pair) | small | small | small | small | small | replicated | small |
| lorenz63 | horizon | deployable | T_c | log T IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | horizon | deployable | T_c | log T OI: L(add)/L(pair) | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | deployable | T_c | log T ON: L(add)/L(pair) | negligible | negligible | small | negligible | negligible | replicated | negligible |
| lorenz63 | horizon | deployable | T_c | log T RI: L(add)/L(pair) | needed, size not determined | small | needed, size not determined | small | small | not replicated | replicated claim: ratio > 1 |
| lorenz63 | horizon | deployable | T_c | log T RN: L(add)/L(pair) | negligible | negligible | small | negligible | negligible | replicated | negligible |
| lorenz63 | horizon | deployable | T_c | log T RO: L(add)/L(pair) | negligible | negligible | small | negligible | negligible | replicated | negligible |
| lorenz63 | horizon | oracle | T_c | log T IN: L(add)/L(pair) | negligible | negligible | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | horizon | oracle | T_c | log T OI: L(add)/L(pair) | substantial | substantial | substantial | substantial | needed, size not determined | replicated | substantial |
| lorenz63 | horizon | oracle | T_c | log T ON: L(add)/L(pair) | small | negligible | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | horizon | oracle | T_c | log T RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | horizon | oracle | T_c | log T RN: L(add)/L(pair) | negligible | negligible | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | horizon | oracle | T_c | log T RO: L(add)/L(pair) | small | negligible | small | needed, size not determined | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=120 (4.00 LT) | decision IN: L(add)/L(pair) | negligible | negligible | small | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=120 (4.00 LT) | decision OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=120 (4.00 LT) | decision ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | small | replicated | negligible |
| rossler | allocation | deployable | H=120 (4.00 LT) | decision RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=120 (4.00 LT) | decision RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=120 (4.00 LT) | decision RO: L(add)/L(pair) | negligible | negligible | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=120 (4.00 LT) | logit IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | small | replicated | negligible |
| rossler | allocation | deployable | H=120 (4.00 LT) | logit OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=120 (4.00 LT) | logit ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=120 (4.00 LT) | logit RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=120 (4.00 LT) | logit RN: L(add)/L(pair) | negligible | small | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=120 (4.00 LT) | logit RO: L(add)/L(pair) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| rossler | allocation | deployable | H=120 (4.00 LT) | one IN: L(add)/L(pair) | negligible | small | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=120 (4.00 LT) | one OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=120 (4.00 LT) | one ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=120 (4.00 LT) | one RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=120 (4.00 LT) | one RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=120 (4.00 LT) | one RO: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=120 (4.00 LT) | zero IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | small | replicated | negligible |
| rossler | allocation | deployable | H=120 (4.00 LT) | zero OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=120 (4.00 LT) | zero ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=120 (4.00 LT) | zero RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=120 (4.00 LT) | zero RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=120 (4.00 LT) | zero RO: L(add)/L(pair) | negligible | negligible | negligible | small | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=15 (0.50 LT) | decision IN: L(add)/L(pair) | small | negligible | negligible | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=15 (0.50 LT) | decision OI: L(add)/L(pair) | small | negligible | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=15 (0.50 LT) | decision ON: L(add)/L(pair) | negligible | small | small | small | small | replicated | small |
| rossler | allocation | deployable | H=15 (0.50 LT) | decision RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=15 (0.50 LT) | decision RN: L(add)/L(pair) | small | small | small | small | small | replicated | small |
| rossler | allocation | deployable | H=15 (0.50 LT) | decision RO: L(add)/L(pair) | undetermined | undetermined | needed, size not determined | needed, size not determined | needed, size not determined | not replicated |  |
| rossler | allocation | deployable | H=15 (0.50 LT) | logit IN: L(add)/L(pair) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| rossler | allocation | deployable | H=15 (0.50 LT) | logit OI: L(add)/L(pair) | small | negligible | negligible | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=15 (0.50 LT) | logit ON: L(add)/L(pair) | negligible | small | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=15 (0.50 LT) | logit RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=15 (0.50 LT) | logit RN: L(add)/L(pair) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| rossler | allocation | deployable | H=15 (0.50 LT) | logit RO: L(add)/L(pair) | small | small | small | negligible | small | replicated | small |
| rossler | allocation | deployable | H=15 (0.50 LT) | zero IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=15 (0.50 LT) | zero OI: L(add)/L(pair) | small | negligible | negligible | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=15 (0.50 LT) | zero ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=15 (0.50 LT) | zero RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=15 (0.50 LT) | zero RN: L(add)/L(pair) | small | negligible | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=15 (0.50 LT) | zero RO: L(add)/L(pair) | negligible | negligible | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=30 (1.00 LT) | decision IN: L(add)/L(pair) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | decision OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | decision ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | decision RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | decision RN: L(add)/L(pair) | small | negligible | small | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=30 (1.00 LT) | decision RO: L(add)/L(pair) | needed, size not determined | needed, size not determined | undetermined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| rossler | allocation | deployable | H=30 (1.00 LT) | logit IN: L(add)/L(pair) | negligible | negligible | small | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | logit OI: L(add)/L(pair) | small | negligible | small | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=30 (1.00 LT) | logit ON: L(add)/L(pair) | negligible | negligible | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=30 (1.00 LT) | logit RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | logit RN: L(add)/L(pair) | negligible | negligible | small | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | logit RO: L(add)/L(pair) | small | small | small | small | small | replicated | small |
| rossler | allocation | deployable | H=30 (1.00 LT) | zero IN: L(add)/L(pair) | small | negligible | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=30 (1.00 LT) | zero OI: L(add)/L(pair) | small | small | negligible | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=30 (1.00 LT) | zero ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | zero RI: L(add)/L(pair) | small | small | small | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=30 (1.00 LT) | zero RN: L(add)/L(pair) | negligible | small | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=30 (1.00 LT) | zero RO: L(add)/L(pair) | small | negligible | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=60 (2.00 LT) | decision IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | decision OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | decision ON: L(add)/L(pair) | negligible | small | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | decision RI: L(add)/L(pair) | negligible | small | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | decision RN: L(add)/L(pair) | negligible | small | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | decision RO: L(add)/L(pair) | negligible | small | negligible | small | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=60 (2.00 LT) | logit IN: L(add)/L(pair) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | logit OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | logit ON: L(add)/L(pair) | negligible | negligible | small | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | logit RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | logit RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | logit RO: L(add)/L(pair) | negligible | small | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | zero IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | zero OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | zero ON: L(add)/L(pair) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | zero RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | zero RN: L(add)/L(pair) | small | negligible | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=60 (2.00 LT) | zero RO: L(add)/L(pair) | negligible | negligible | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=8 (0.27 LT) | decision IN: L(add)/L(pair) | small | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=8 (0.27 LT) | decision OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=8 (0.27 LT) | decision ON: L(add)/L(pair) | small | small | negligible | small | small | replicated | small |
| rossler | allocation | deployable | H=8 (0.27 LT) | decision RI: L(add)/L(pair) | small | negligible | negligible | negligible | no interaction gain; the pair model fits worse | contradicted | DEV-5 small vs DEV-9 no interaction gain; the pair model fits worse; replicated claim within a contradicted row: ratio <= 1.05 |
| rossler | allocation | deployable | H=8 (0.27 LT) | decision RN: L(add)/L(pair) | small | small | small | small | negligible | replicated | small |
| rossler | allocation | deployable | H=8 (0.27 LT) | decision RO: L(add)/L(pair) | small | small | needed, size not determined | small | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | deployable | H=8 (0.27 LT) | logit IN: L(add)/L(pair) | negligible | negligible | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=8 (0.27 LT) | logit OI: L(add)/L(pair) | negligible | small | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=8 (0.27 LT) | logit ON: L(add)/L(pair) | small | negligible | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=8 (0.27 LT) | logit RI: L(add)/L(pair) | negligible | negligible | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=8 (0.27 LT) | logit RN: L(add)/L(pair) | small | negligible | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=8 (0.27 LT) | logit RO: L(add)/L(pair) | small | small | small | small | small | replicated | small |
| rossler | allocation | deployable | H=8 (0.27 LT) | zero IN: L(add)/L(pair) | negligible | no interaction gain; the pair model fits worse | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=8 (0.27 LT) | zero OI: L(add)/L(pair) | negligible | negligible | small | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=8 (0.27 LT) | zero ON: L(add)/L(pair) | negligible | negligible | small | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=8 (0.27 LT) | zero RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=8 (0.27 LT) | zero RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=8 (0.27 LT) | zero RO: L(add)/L(pair) | negligible | small | small | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=120 (4.00 LT) | decision IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=120 (4.00 LT) | decision OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=120 (4.00 LT) | decision ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=120 (4.00 LT) | decision RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=120 (4.00 LT) | decision RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | no interaction gain; the pair model fits worse | replicated | negligible |
| rossler | allocation | oracle | H=120 (4.00 LT) | decision RO: L(add)/L(pair) | negligible | negligible | small | small | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=120 (4.00 LT) | logit IN: L(add)/L(pair) | negligible | small | small | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=120 (4.00 LT) | logit OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=120 (4.00 LT) | logit ON: L(add)/L(pair) | negligible | small | negligible | negligible | no interaction gain; the pair model fits worse | contradicted | DEV-6 small vs DEV-9 no interaction gain; the pair model fits worse; replicated claim within a contradicted row: ratio <= 1.05 |
| rossler | allocation | oracle | H=120 (4.00 LT) | logit RI: L(add)/L(pair) | negligible | small | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=120 (4.00 LT) | logit RN: L(add)/L(pair) | negligible | small | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=120 (4.00 LT) | logit RO: L(add)/L(pair) | small | negligible | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=120 (4.00 LT) | one IN: L(add)/L(pair) | small | small | no interaction gain; the pair model fits worse | negligible | negligible | contradicted | DEV-5 small vs DEV-7 no interaction gain; the pair model fits worse; replicated claim within a contradicted row: ratio <= 1.05 |
| rossler | allocation | oracle | H=120 (4.00 LT) | one OI: L(add)/L(pair) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| rossler | allocation | oracle | H=120 (4.00 LT) | one ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=120 (4.00 LT) | one RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=120 (4.00 LT) | one RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=120 (4.00 LT) | one RO: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=120 (4.00 LT) | zero IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=120 (4.00 LT) | zero OI: L(add)/L(pair) | negligible | negligible | small | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=120 (4.00 LT) | zero ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=120 (4.00 LT) | zero RI: L(add)/L(pair) | negligible | negligible | small | small | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=120 (4.00 LT) | zero RN: L(add)/L(pair) | negligible | small | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=120 (4.00 LT) | zero RO: L(add)/L(pair) | negligible | negligible | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=15 (0.50 LT) | decision IN: L(add)/L(pair) | negligible | negligible | negligible | no interaction gain; the pair model fits worse | negligible | replicated | negligible |
| rossler | allocation | oracle | H=15 (0.50 LT) | decision OI: L(add)/L(pair) | small | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=15 (0.50 LT) | decision ON: L(add)/L(pair) | needed, size not determined | small | undetermined | small | negligible | not replicated |  |
| rossler | allocation | oracle | H=15 (0.50 LT) | decision RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=15 (0.50 LT) | decision RN: L(add)/L(pair) | small | needed, size not determined | needed, size not determined | small | negligible | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | oracle | H=15 (0.50 LT) | decision RO: L(add)/L(pair) | substantial | substantial | substantial | needed, size not determined | substantial | replicated | substantial |
| rossler | allocation | oracle | H=15 (0.50 LT) | logit IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=15 (0.50 LT) | logit OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | small | replicated | negligible |
| rossler | allocation | oracle | H=15 (0.50 LT) | logit ON: L(add)/L(pair) | small | small | small | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=15 (0.50 LT) | logit RI: L(add)/L(pair) | negligible | small | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=15 (0.50 LT) | logit RN: L(add)/L(pair) | small | negligible | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=15 (0.50 LT) | logit RO: L(add)/L(pair) | needed, size not determined | needed, size not determined | small | negligible | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | oracle | H=15 (0.50 LT) | zero IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=15 (0.50 LT) | zero OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=15 (0.50 LT) | zero ON: L(add)/L(pair) | negligible | negligible | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=15 (0.50 LT) | zero RI: L(add)/L(pair) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| rossler | allocation | oracle | H=15 (0.50 LT) | zero RN: L(add)/L(pair) | negligible | negligible | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=15 (0.50 LT) | zero RO: L(add)/L(pair) | small | small | small | small | small | replicated | small |
| rossler | allocation | oracle | H=30 (1.00 LT) | decision IN: L(add)/L(pair) | negligible | negligible | negligible | needed, size not determined | undetermined | not replicated |  |
| rossler | allocation | oracle | H=30 (1.00 LT) | decision OI: L(add)/L(pair) | small | small | negligible | negligible | undetermined | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=30 (1.00 LT) | decision ON: L(add)/L(pair) | undetermined | needed, size not determined | undetermined | undetermined | undetermined | not replicated |  |
| rossler | allocation | oracle | H=30 (1.00 LT) | decision RI: L(add)/L(pair) | small | negligible | negligible | negligible | needed, size not determined | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=30 (1.00 LT) | decision RN: L(add)/L(pair) | needed, size not determined | undetermined | negligible | undetermined | undetermined | not replicated |  |
| rossler | allocation | oracle | H=30 (1.00 LT) | decision RO: L(add)/L(pair) | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=30 (1.00 LT) | logit IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=30 (1.00 LT) | logit OI: L(add)/L(pair) | negligible | negligible | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=30 (1.00 LT) | logit ON: L(add)/L(pair) | negligible | negligible | small | small | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=30 (1.00 LT) | logit RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=30 (1.00 LT) | logit RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=30 (1.00 LT) | logit RO: L(add)/L(pair) | needed, size not determined | needed, size not determined | small | small | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | oracle | H=30 (1.00 LT) | zero IN: L(add)/L(pair) | small | negligible | small | small | small | replicated | small |
| rossler | allocation | oracle | H=30 (1.00 LT) | zero OI: L(add)/L(pair) | small | small | small | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=30 (1.00 LT) | zero ON: L(add)/L(pair) | small | small | small | negligible | small | replicated | small |
| rossler | allocation | oracle | H=30 (1.00 LT) | zero RI: L(add)/L(pair) | negligible | negligible | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=30 (1.00 LT) | zero RN: L(add)/L(pair) | negligible | small | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=30 (1.00 LT) | zero RO: L(add)/L(pair) | small | small | small | small | small | replicated | small |
| rossler | allocation | oracle | H=60 (2.00 LT) | decision IN: L(add)/L(pair) | negligible | small | negligible | undetermined | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=60 (2.00 LT) | decision OI: L(add)/L(pair) | negligible | small | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=60 (2.00 LT) | decision ON: L(add)/L(pair) | negligible | undetermined | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=60 (2.00 LT) | decision RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=60 (2.00 LT) | decision RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=60 (2.00 LT) | decision RO: L(add)/L(pair) | undetermined | undetermined | undetermined | needed, size not determined | undetermined | not replicated |  |
| rossler | allocation | oracle | H=60 (2.00 LT) | logit IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | small | replicated | negligible |
| rossler | allocation | oracle | H=60 (2.00 LT) | logit OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=60 (2.00 LT) | logit ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | small | replicated | negligible |
| rossler | allocation | oracle | H=60 (2.00 LT) | logit RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=60 (2.00 LT) | logit RN: L(add)/L(pair) | small | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=60 (2.00 LT) | logit RO: L(add)/L(pair) | negligible | small | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=60 (2.00 LT) | zero IN: L(add)/L(pair) | negligible | negligible | small | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=60 (2.00 LT) | zero OI: L(add)/L(pair) | negligible | small | small | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=60 (2.00 LT) | zero ON: L(add)/L(pair) | small | small | small | negligible | no interaction gain; the pair model fits worse | contradicted | DEV-5 small vs DEV-9 no interaction gain; the pair model fits worse; replicated claim within a contradicted row: ratio <= 1.05 |
| rossler | allocation | oracle | H=60 (2.00 LT) | zero RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=60 (2.00 LT) | zero RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=60 (2.00 LT) | zero RO: L(add)/L(pair) | small | small | small | negligible | small | replicated | small |
| rossler | allocation | oracle | H=8 (0.27 LT) | decision IN: L(add)/L(pair) | small | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=8 (0.27 LT) | decision OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=8 (0.27 LT) | decision ON: L(add)/L(pair) | small | undetermined | undetermined | negligible | negligible | not replicated |  |
| rossler | allocation | oracle | H=8 (0.27 LT) | decision RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=8 (0.27 LT) | decision RN: L(add)/L(pair) | undetermined | needed, size not determined | needed, size not determined | negligible | small | not replicated |  |
| rossler | allocation | oracle | H=8 (0.27 LT) | decision RO: L(add)/L(pair) | substantial | substantial | needed, size not determined | undetermined | substantial | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | oracle | H=8 (0.27 LT) | logit IN: L(add)/L(pair) | negligible | small | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=8 (0.27 LT) | logit OI: L(add)/L(pair) | negligible | small | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=8 (0.27 LT) | logit ON: L(add)/L(pair) | small | small | small | small | negligible | replicated | small |
| rossler | allocation | oracle | H=8 (0.27 LT) | logit RI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=8 (0.27 LT) | logit RN: L(add)/L(pair) | small | negligible | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=8 (0.27 LT) | logit RO: L(add)/L(pair) | needed, size not determined | small | needed, size not determined | small | small | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | oracle | H=8 (0.27 LT) | zero IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=8 (0.27 LT) | zero OI: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=8 (0.27 LT) | zero ON: L(add)/L(pair) | small | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=8 (0.27 LT) | zero RI: L(add)/L(pair) | negligible | small | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=8 (0.27 LT) | zero RN: L(add)/L(pair) | small | small | small | negligible | small | replicated | small |
| rossler | allocation | oracle | H=8 (0.27 LT) | zero RO: L(add)/L(pair) | small | small | small | small | small | replicated | small |
| rossler | horizon | deployable | T_c | log T IN: L(add)/L(pair) | negligible | negligible | negligible | negligible | small | replicated | negligible |
| rossler | horizon | deployable | T_c | log T OI: L(add)/L(pair) | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | deployable | T_c | log T ON: L(add)/L(pair) | negligible | small | negligible | negligible | negligible | replicated | negligible |
| rossler | horizon | deployable | T_c | log T RI: L(add)/L(pair) | small | negligible | small | small | small | replicated | small |
| rossler | horizon | deployable | T_c | log T RN: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | horizon | deployable | T_c | log T RO: L(add)/L(pair) | negligible | small | negligible | negligible | negligible | replicated | negligible |
| rossler | horizon | oracle | T_c | log T IN: L(add)/L(pair) | negligible | negligible | negligible | small | negligible | replicated | negligible |
| rossler | horizon | oracle | T_c | log T OI: L(add)/L(pair) | needed, size not determined | substantial | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| rossler | horizon | oracle | T_c | log T ON: L(add)/L(pair) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | horizon | oracle | T_c | log T RI: L(add)/L(pair) | small | negligible | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | horizon | oracle | T_c | log T RN: L(add)/L(pair) | small | negligible | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | horizon | oracle | T_c | log T RO: L(add)/L(pair) | small | small | negligible | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |

## B pair

DEVELOPMENT: phase J replication (held-out development seeds), not a hypothesis test.

| system | decision | profile | horizon | item | DEV-5 | DEV-6 | DEV-7 | DEV-8 | DEV-9 | class | replicated reading or claims |
|---|---|---|---|---|---|---|---|---|---|---|---|
| chua | allocation | deployable | H=120 (4.00 LT) | decision IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | decision OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | decision ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | decision RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | decision RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | decision RO: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | logit IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | logit OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | logit ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | logit RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | logit RN: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | logit RO: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | one IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | one OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | one ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | one RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | one RN: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | one RO: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | zero IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | zero OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | zero ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | zero RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | zero RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | zero RO: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | decision IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | decision OI: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | decision ON: Delta | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | decision RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | decision RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | decision RO: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | logit IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | logit OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | logit ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | logit RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | logit RN: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | logit RO: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | zero IN: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | zero OI: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | zero ON: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | zero RI: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | zero RN: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | zero RO: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | decision IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | decision OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | decision ON: Delta | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | decision RI: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | decision RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | decision RO: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | logit IN: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | logit OI: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| chua | allocation | deployable | H=30 (1.00 LT) | logit ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | logit RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | logit RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | logit RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| chua | allocation | deployable | H=30 (1.00 LT) | zero IN: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | zero OI: Delta | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| chua | allocation | deployable | H=30 (1.00 LT) | zero ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | zero RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | zero RN: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | zero RO: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain; the pair model fits worse | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | decision IN: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | decision OI: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | replicated | interaction gain detected |
| chua | allocation | deployable | H=60 (2.00 LT) | decision ON: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | decision RI: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | decision RN: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | decision RO: Delta | no interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | logit IN: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | logit OI: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| chua | allocation | deployable | H=60 (2.00 LT) | logit ON: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | logit RI: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | logit RN: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | logit RO: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| chua | allocation | deployable | H=60 (2.00 LT) | one IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | one OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | one ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | one RI: Delta | no interaction gain; the pair model fits worse | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | one RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | one RO: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | zero IN: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| chua | allocation | deployable | H=60 (2.00 LT) | zero OI: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| chua | allocation | deployable | H=60 (2.00 LT) | zero ON: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| chua | allocation | deployable | H=60 (2.00 LT) | zero RI: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | zero RN: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | zero RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| chua | allocation | deployable | H=8 (0.27 LT) | decision IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | decision OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain; the pair model fits worse | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | decision ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | decision RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | decision RN: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | decision RO: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | logit IN: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | logit OI: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | logit ON: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | logit RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | logit RN: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | logit RO: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | zero IN: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | zero OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | zero ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | zero RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | zero RN: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | zero RO: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=120 (4.00 LT) | decision IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=120 (4.00 LT) | decision OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=120 (4.00 LT) | decision ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=120 (4.00 LT) | decision RI: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=120 (4.00 LT) | decision RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=120 (4.00 LT) | decision RO: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=120 (4.00 LT) | logit IN: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=120 (4.00 LT) | logit OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=120 (4.00 LT) | logit ON: Delta | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=120 (4.00 LT) | logit RI: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=120 (4.00 LT) | logit RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=120 (4.00 LT) | logit RO: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=120 (4.00 LT) | one IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=120 (4.00 LT) | one OI: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=120 (4.00 LT) | one ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=120 (4.00 LT) | one RI: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=120 (4.00 LT) | one RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=120 (4.00 LT) | one RO: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=120 (4.00 LT) | zero IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=120 (4.00 LT) | zero OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=120 (4.00 LT) | zero ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=120 (4.00 LT) | zero RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=120 (4.00 LT) | zero RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=120 (4.00 LT) | zero RO: Delta | no interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| chua | allocation | oracle | H=15 (0.50 LT) | decision IN: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | decision OI: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | decision ON: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | decision RI: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | decision RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | decision RO: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | logit IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | logit OI: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | logit ON: Delta | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| chua | allocation | oracle | H=15 (0.50 LT) | logit RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | logit RN: Delta | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | logit RO: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| chua | allocation | oracle | H=15 (0.50 LT) | zero IN: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | zero OI: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | zero ON: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | zero RI: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | zero RN: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | zero RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| chua | allocation | oracle | H=30 (1.00 LT) | decision IN: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | decision OI: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | decision ON: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | decision RI: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | decision RN: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | decision RO: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | logit IN: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | logit OI: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| chua | allocation | oracle | H=30 (1.00 LT) | logit ON: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | logit RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | logit RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | logit RO: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | zero IN: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | zero OI: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| chua | allocation | oracle | H=30 (1.00 LT) | zero ON: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | zero RI: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | zero RN: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | replicated | interaction gain detected |
| chua | allocation | oracle | H=30 (1.00 LT) | zero RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | replicated | interaction gain detected |
| chua | allocation | oracle | H=60 (2.00 LT) | decision IN: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=60 (2.00 LT) | decision OI: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=60 (2.00 LT) | decision ON: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=60 (2.00 LT) | decision RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=60 (2.00 LT) | decision RN: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=60 (2.00 LT) | decision RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=60 (2.00 LT) | logit IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=60 (2.00 LT) | logit OI: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| chua | allocation | oracle | H=60 (2.00 LT) | logit ON: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=60 (2.00 LT) | logit RI: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=60 (2.00 LT) | logit RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=60 (2.00 LT) | logit RO: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=60 (2.00 LT) | one IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=60 (2.00 LT) | one OI: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=60 (2.00 LT) | one ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=60 (2.00 LT) | one RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=60 (2.00 LT) | one RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=60 (2.00 LT) | one RO: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=60 (2.00 LT) | zero IN: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| chua | allocation | oracle | H=60 (2.00 LT) | zero OI: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| chua | allocation | oracle | H=60 (2.00 LT) | zero ON: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| chua | allocation | oracle | H=60 (2.00 LT) | zero RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=60 (2.00 LT) | zero RN: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=60 (2.00 LT) | zero RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | replicated | interaction gain detected |
| chua | allocation | oracle | H=8 (0.27 LT) | decision IN: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | decision OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | decision ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | decision RI: Delta | no interaction gain detected | no interaction gain; the pair model fits worse | no interaction gain detected | interaction gain detected | no interaction gain detected | contradicted | DEV-6 no interaction gain; the pair model fits worse vs DEV-8 interaction gain detected |
| chua | allocation | oracle | H=8 (0.27 LT) | decision RN: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | decision RO: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | logit IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | logit OI: Delta | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | logit ON: Delta | no interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| chua | allocation | oracle | H=8 (0.27 LT) | logit RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | logit RN: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| chua | allocation | oracle | H=8 (0.27 LT) | logit RO: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | zero IN: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | zero OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | zero ON: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | zero RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | zero RN: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| chua | allocation | oracle | H=8 (0.27 LT) | zero RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| chua | horizon | deployable | T_c | log T IN: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | horizon | deployable | T_c | log T OI: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| chua | horizon | deployable | T_c | log T ON: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | horizon | deployable | T_c | log T RI: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| chua | horizon | deployable | T_c | log T RN: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | horizon | deployable | T_c | log T RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | horizon | oracle | T_c | log T IN: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | horizon | oracle | T_c | log T OI: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| chua | horizon | oracle | T_c | log T ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| chua | horizon | oracle | T_c | log T RI: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| chua | horizon | oracle | T_c | log T RN: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| chua | horizon | oracle | T_c | log T RO: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | decision IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | decision OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | decision ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | decision RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | decision RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | decision RO: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain; the pair model fits worse | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | logit IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | logit OI: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | logit ON: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | logit RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | logit RN: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | logit RO: Delta | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | one IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | one OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | one ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | one RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | one RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | one RO: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | zero IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | zero OI: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | zero ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | zero RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | zero RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | zero RO: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | decision IN: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | decision OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | decision ON: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | decision RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | decision RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | decision RO: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | logit IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | logit OI: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | logit ON: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | logit RI: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | logit RN: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | logit RO: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | zero IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | zero OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | zero ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | zero RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | zero RN: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | zero RO: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | decision IN: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | decision OI: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | decision ON: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | decision RI: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | decision RN: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | decision RO: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | logit IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | logit OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | logit ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | logit RI: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | logit RN: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | logit RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | zero IN: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | zero OI: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | zero ON: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | zero RI: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | zero RN: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | zero RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | decision IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | decision OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | decision ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | decision RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | decision RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | decision RO: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | logit IN: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | logit OI: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | logit ON: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | logit RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | logit RN: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | logit RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | replicated | interaction gain detected |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | zero IN: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | zero OI: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | zero ON: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | zero RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | zero RN: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | zero RO: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | decision IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | decision OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | decision ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | decision RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | decision RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | decision RO: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | logit IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | logit OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | logit ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain; the pair model fits worse | no interaction gain; the pair model fits worse | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | logit RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain; the pair model fits worse | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | logit RN: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain; the pair model fits worse | contradicted | DEV-5 interaction gain detected vs DEV-9 no interaction gain; the pair model fits worse |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | logit RO: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | zero IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | zero OI: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | zero ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | zero RI: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | zero RN: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | zero RO: Delta | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | decision IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | decision OI: Delta | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | decision ON: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | decision RI: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | decision RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | decision RO: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | logit IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | logit OI: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | logit ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | logit RI: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | logit RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | logit RO: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | one IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | one OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | one ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | one RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | one RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | one RO: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | zero IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | zero OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | zero ON: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | zero RI: Delta | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | zero RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | zero RO: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | decision IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | decision OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | decision ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | decision RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | decision RN: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | decision RO: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | logit IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | logit OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | logit ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | logit RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | logit RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | logit RO: Delta | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | zero IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | zero OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | zero ON: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | zero RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | zero RN: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | zero RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | decision IN: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | decision OI: Delta | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | decision ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | decision RI: Delta | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | decision RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | decision RO: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | logit IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | logit OI: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | logit ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | logit RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | logit RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | logit RO: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | zero IN: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | zero OI: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | zero ON: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | zero RI: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | zero RN: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | zero RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | decision IN: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | decision OI: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | decision ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain; the pair model fits worse | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | decision RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | decision RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | decision RO: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | logit IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | logit OI: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | logit ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | logit RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | logit RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | logit RO: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | zero IN: Delta | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | zero OI: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | zero ON: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | zero RI: Delta | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | zero RN: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | zero RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | decision IN: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | decision OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | decision ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | decision RI: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | decision RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | decision RO: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | logit IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | logit OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | logit ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | logit RI: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | logit RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | logit RO: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | zero IN: Delta | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | zero OI: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | zero ON: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | zero RI: Delta | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | zero RN: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | zero RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| lorenz63 | horizon | deployable | T_c | log T IN: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | horizon | deployable | T_c | log T OI: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| lorenz63 | horizon | deployable | T_c | log T ON: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | horizon | deployable | T_c | log T RI: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| lorenz63 | horizon | deployable | T_c | log T RN: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | horizon | deployable | T_c | log T RO: Delta | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | horizon | oracle | T_c | log T IN: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | horizon | oracle | T_c | log T OI: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| lorenz63 | horizon | oracle | T_c | log T ON: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| lorenz63 | horizon | oracle | T_c | log T RI: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | horizon | oracle | T_c | log T RN: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| lorenz63 | horizon | oracle | T_c | log T RO: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | decision IN: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | decision OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | decision ON: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | decision RI: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | decision RN: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | decision RO: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | logit IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | logit OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | logit ON: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | logit RI: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | logit RN: Delta | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | logit RO: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | one IN: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | one OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | one ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | one RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | one RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | one RO: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | zero IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | zero OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | zero ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | zero RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | zero RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | zero RO: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=15 (0.50 LT) | decision IN: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=15 (0.50 LT) | decision OI: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=15 (0.50 LT) | decision ON: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | deployable | H=15 (0.50 LT) | decision RI: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=15 (0.50 LT) | decision RN: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | deployable | H=15 (0.50 LT) | decision RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | deployable | H=15 (0.50 LT) | logit IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=15 (0.50 LT) | logit OI: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=15 (0.50 LT) | logit ON: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=15 (0.50 LT) | logit RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=15 (0.50 LT) | logit RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=15 (0.50 LT) | logit RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | deployable | H=15 (0.50 LT) | zero IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=15 (0.50 LT) | zero OI: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=15 (0.50 LT) | zero ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=15 (0.50 LT) | zero RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=15 (0.50 LT) | zero RN: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=15 (0.50 LT) | zero RO: Delta | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=30 (1.00 LT) | decision IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=30 (1.00 LT) | decision OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=30 (1.00 LT) | decision ON: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=30 (1.00 LT) | decision RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=30 (1.00 LT) | decision RN: Delta | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=30 (1.00 LT) | decision RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | deployable | H=30 (1.00 LT) | logit IN: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=30 (1.00 LT) | logit OI: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=30 (1.00 LT) | logit ON: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=30 (1.00 LT) | logit RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=30 (1.00 LT) | logit RN: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=30 (1.00 LT) | logit RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | deployable | H=30 (1.00 LT) | zero IN: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | deployable | H=30 (1.00 LT) | zero OI: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | deployable | H=30 (1.00 LT) | zero ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=30 (1.00 LT) | zero RI: Delta | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | deployable | H=30 (1.00 LT) | zero RN: Delta | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | deployable | H=30 (1.00 LT) | zero RO: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | decision IN: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | decision OI: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | decision ON: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | decision RI: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | decision RN: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | decision RO: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | logit IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | logit OI: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | logit ON: Delta | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | logit RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | logit RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | logit RO: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | zero IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | zero OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | zero ON: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | zero RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | zero RN: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | zero RO: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | deployable | H=8 (0.27 LT) | decision IN: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | decision OI: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | decision ON: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | deployable | H=8 (0.27 LT) | decision RI: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain; the pair model fits worse | contradicted | DEV-5 interaction gain detected vs DEV-9 no interaction gain; the pair model fits worse |
| rossler | allocation | deployable | H=8 (0.27 LT) | decision RN: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | deployable | H=8 (0.27 LT) | decision RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | deployable | H=8 (0.27 LT) | logit IN: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | logit OI: Delta | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | logit ON: Delta | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | deployable | H=8 (0.27 LT) | logit RI: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | logit RN: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | deployable | H=8 (0.27 LT) | logit RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | deployable | H=8 (0.27 LT) | zero IN: Delta | no interaction gain detected | no interaction gain; the pair model fits worse | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | zero OI: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | zero ON: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | zero RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | zero RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | zero RO: Delta | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=120 (4.00 LT) | decision IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=120 (4.00 LT) | decision OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=120 (4.00 LT) | decision ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=120 (4.00 LT) | decision RI: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=120 (4.00 LT) | decision RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain; the pair model fits worse | not replicated |  |
| rossler | allocation | oracle | H=120 (4.00 LT) | decision RO: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=120 (4.00 LT) | logit IN: Delta | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=120 (4.00 LT) | logit OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=120 (4.00 LT) | logit ON: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain; the pair model fits worse | contradicted | DEV-6 interaction gain detected vs DEV-9 no interaction gain; the pair model fits worse |
| rossler | allocation | oracle | H=120 (4.00 LT) | logit RI: Delta | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | oracle | H=120 (4.00 LT) | logit RN: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=120 (4.00 LT) | logit RO: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=120 (4.00 LT) | one IN: Delta | interaction gain detected | interaction gain detected | no interaction gain; the pair model fits worse | no interaction gain detected | no interaction gain detected | contradicted | DEV-5 interaction gain detected vs DEV-7 no interaction gain; the pair model fits worse |
| rossler | allocation | oracle | H=120 (4.00 LT) | one OI: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=120 (4.00 LT) | one ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=120 (4.00 LT) | one RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=120 (4.00 LT) | one RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=120 (4.00 LT) | one RO: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=120 (4.00 LT) | zero IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=120 (4.00 LT) | zero OI: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=120 (4.00 LT) | zero ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=120 (4.00 LT) | zero RI: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=120 (4.00 LT) | zero RN: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=120 (4.00 LT) | zero RO: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=15 (0.50 LT) | decision IN: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain; the pair model fits worse | no interaction gain detected | contradicted | DEV-6 interaction gain detected vs DEV-8 no interaction gain; the pair model fits worse |
| rossler | allocation | oracle | H=15 (0.50 LT) | decision OI: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=15 (0.50 LT) | decision ON: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=15 (0.50 LT) | decision RI: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=15 (0.50 LT) | decision RN: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | oracle | H=15 (0.50 LT) | decision RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | oracle | H=15 (0.50 LT) | logit IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=15 (0.50 LT) | logit OI: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=15 (0.50 LT) | logit ON: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | oracle | H=15 (0.50 LT) | logit RI: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=15 (0.50 LT) | logit RN: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=15 (0.50 LT) | logit RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | oracle | H=15 (0.50 LT) | zero IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=15 (0.50 LT) | zero OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=15 (0.50 LT) | zero ON: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=15 (0.50 LT) | zero RI: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=15 (0.50 LT) | zero RN: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=15 (0.50 LT) | zero RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | oracle | H=30 (1.00 LT) | decision IN: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=30 (1.00 LT) | decision OI: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=30 (1.00 LT) | decision ON: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=30 (1.00 LT) | decision RI: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=30 (1.00 LT) | decision RN: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=30 (1.00 LT) | decision RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | oracle | H=30 (1.00 LT) | logit IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=30 (1.00 LT) | logit OI: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=30 (1.00 LT) | logit ON: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | oracle | H=30 (1.00 LT) | logit RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=30 (1.00 LT) | logit RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=30 (1.00 LT) | logit RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | oracle | H=30 (1.00 LT) | zero IN: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | oracle | H=30 (1.00 LT) | zero OI: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | oracle | H=30 (1.00 LT) | zero ON: Delta | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | oracle | H=30 (1.00 LT) | zero RI: Delta | no interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=30 (1.00 LT) | zero RN: Delta | no interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | oracle | H=30 (1.00 LT) | zero RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | oracle | H=60 (2.00 LT) | decision IN: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=60 (2.00 LT) | decision OI: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=60 (2.00 LT) | decision ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=60 (2.00 LT) | decision RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=60 (2.00 LT) | decision RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=60 (2.00 LT) | decision RO: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=60 (2.00 LT) | logit IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=60 (2.00 LT) | logit OI: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=60 (2.00 LT) | logit ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=60 (2.00 LT) | logit RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=60 (2.00 LT) | logit RN: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=60 (2.00 LT) | logit RO: Delta | no interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | oracle | H=60 (2.00 LT) | zero IN: Delta | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=60 (2.00 LT) | zero OI: Delta | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=60 (2.00 LT) | zero ON: Delta | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain; the pair model fits worse | contradicted | DEV-5 interaction gain detected vs DEV-9 no interaction gain; the pair model fits worse |
| rossler | allocation | oracle | H=60 (2.00 LT) | zero RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=60 (2.00 LT) | zero RN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=60 (2.00 LT) | zero RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | oracle | H=8 (0.27 LT) | decision IN: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=8 (0.27 LT) | decision OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=8 (0.27 LT) | decision ON: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=8 (0.27 LT) | decision RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=8 (0.27 LT) | decision RN: Delta | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | oracle | H=8 (0.27 LT) | decision RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | oracle | H=8 (0.27 LT) | logit IN: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=8 (0.27 LT) | logit OI: Delta | no interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=8 (0.27 LT) | logit ON: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | oracle | H=8 (0.27 LT) | logit RI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=8 (0.27 LT) | logit RN: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=8 (0.27 LT) | logit RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | oracle | H=8 (0.27 LT) | zero IN: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=8 (0.27 LT) | zero OI: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=8 (0.27 LT) | zero ON: Delta | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=8 (0.27 LT) | zero RI: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | allocation | oracle | H=8 (0.27 LT) | zero RN: Delta | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | allocation | oracle | H=8 (0.27 LT) | zero RO: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | horizon | deployable | T_c | log T IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | not replicated |  |
| rossler | horizon | deployable | T_c | log T OI: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | horizon | deployable | T_c | log T ON: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | horizon | deployable | T_c | log T RI: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | horizon | deployable | T_c | log T RN: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | horizon | deployable | T_c | log T RO: Delta | no interaction gain detected | interaction gain detected | no interaction gain detected | no interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | horizon | oracle | T_c | log T IN: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | horizon | oracle | T_c | log T OI: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |
| rossler | horizon | oracle | T_c | log T ON: Delta | no interaction gain detected | no interaction gain detected | no interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | horizon | oracle | T_c | log T RI: Delta | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | not replicated |  |
| rossler | horizon | oracle | T_c | log T RN: Delta | interaction gain detected | interaction gain detected | interaction gain detected | interaction gain detected | no interaction gain detected | replicated | interaction gain detected |
| rossler | horizon | oracle | T_c | log T RO: Delta | interaction gain detected | interaction gain detected | no interaction gain detected | interaction gain detected | interaction gain detected | replicated | interaction gain detected |

## C1 (display only, not counted)

DEVELOPMENT: phase J replication (held-out development seeds), not a hypothesis test.

| system | decision | profile | horizon | item | DEV-5 | DEV-6 | DEV-7 | DEV-8 | DEV-9 | class | replicated reading or claims |
|---|---|---|---|---|---|---|---|---|---|---|---|
| chua | allocation | deployable | H=120 (4.00 LT) | A2 (stored): MSE ratio vs F | small | small | small | small | small | replicated | small |
| chua | allocation | deployable | H=120 (4.00 LT) | A3 (stored): MSE ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| chua | allocation | deployable | H=120 (4.00 LT) | A4 (stored): MSE ratio vs F | needed, size not determined | needed, size not determined | substantial | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| chua | allocation | deployable | H=120 (4.00 LT) | RO: MSE ratio vs F | negligible | negligible | negligible | small | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | X+F: MSE ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | X: MSE ratio vs F | small | small | small | small | small | replicated | small |
| chua | allocation | deployable | H=120 (4.00 LT) | none: MSE ratio vs F | small | small | small | small | small | replicated | small |
| chua | allocation | deployable | H=120 (4.00 LT) | separation: MSE ratio vs F | needed, size not determined | needed, size not determined | substantial | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| chua | allocation | deployable | H=15 (0.50 LT) | A2 (stored): MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | A3 (stored): MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | A4 (stored): MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | RO: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | X+F: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | X: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | none: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | separation: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | A2 (stored): MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | A3 (stored): MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | A4 (stored): MSE ratio vs F | undetermined | undetermined | negligible | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | A5 (stored): MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | RO: MSE ratio vs F | undetermined | undetermined | small | undetermined | negligible | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | X+F: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | negligible | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | X: MSE ratio vs F | undetermined | undetermined | needed, size not determined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | none: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | separation: MSE ratio vs F | undetermined | undetermined | negligible | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | A2 (stored): MSE ratio vs F | needed, size not determined | undetermined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| chua | allocation | deployable | H=60 (2.00 LT) | A3 (stored): MSE ratio vs F | negligible | negligible | undetermined | needed, size not determined | undetermined | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | A4 (stored): MSE ratio vs F | undetermined | needed, size not determined | needed, size not determined | small | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| chua | allocation | deployable | H=60 (2.00 LT) | RO: MSE ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=60 (2.00 LT) | X+F: MSE ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=60 (2.00 LT) | X: MSE ratio vs F | negligible | negligible | negligible | small | negligible | replicated | negligible |
| chua | allocation | deployable | H=60 (2.00 LT) | none: MSE ratio vs F | needed, size not determined | undetermined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| chua | allocation | deployable | H=60 (2.00 LT) | separation: MSE ratio vs F | undetermined | needed, size not determined | needed, size not determined | small | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| chua | allocation | deployable | H=8 (0.27 LT) | A2 (stored): MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | A3 (stored): MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | A4 (stored): MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | RO: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | X+F: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | X: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | none: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | separation: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=120 (4.00 LT) | RO: MSE ratio vs F | small | negligible | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=120 (4.00 LT) | X+F: MSE ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=120 (4.00 LT) | X: MSE ratio vs F | small | small | small | small | small | replicated | small |
| chua | allocation | oracle | H=120 (4.00 LT) | none: MSE ratio vs F | small | small | small | needed, size not determined | small | replicated | small |
| chua | allocation | oracle | H=120 (4.00 LT) | separation: MSE ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| chua | allocation | oracle | H=15 (0.50 LT) | RO: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | X+F: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | X: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | none: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | separation: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | RO: MSE ratio vs F | undetermined | undetermined | negligible | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | X+F: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | negligible | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | X: MSE ratio vs F | undetermined | undetermined | needed, size not determined | undetermined | needed, size not determined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | none: MSE ratio vs F | undetermined | undetermined | needed, size not determined | undetermined | needed, size not determined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | separation: MSE ratio vs F | undetermined | undetermined | negligible | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=60 (2.00 LT) | RO: MSE ratio vs F | negligible | negligible | negligible | small | negligible | replicated | negligible |
| chua | allocation | oracle | H=60 (2.00 LT) | X+F: MSE ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=60 (2.00 LT) | X: MSE ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| chua | allocation | oracle | H=60 (2.00 LT) | none: MSE ratio vs F | substantial | substantial | substantial | substantial | needed, size not determined | replicated | substantial |
| chua | allocation | oracle | H=60 (2.00 LT) | separation: MSE ratio vs F | negligible | undetermined | needed, size not determined | negligible | negligible | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | RO: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | X+F: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | X: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | none: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | separation: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | horizon | deployable | T_c | RO: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | deployable | T_c | X+F: pinball ratio vs F | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | horizon | deployable | T_c | X: pinball ratio vs F | substantial | needed, size not determined | substantial | substantial | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| chua | horizon | deployable | T_c | lyapunov: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | deployable | T_c | none: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | oracle | T_c | RO: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | oracle | T_c | X+F: pinball ratio vs F | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | horizon | oracle | T_c | X: pinball ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | substantial | needed, size not determined | replicated | needed, size not determined |
| chua | horizon | oracle | T_c | lyapunov: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | oracle | T_c | none: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | A2 (stored): MSE ratio vs F | small | small | small | small | negligible | replicated | small |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | A3 (stored): MSE ratio vs F | needed, size not determined | small | negligible | needed, size not determined | small | not replicated | replicated claim: ratio > 1 |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | A4 (stored): MSE ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | RO: MSE ratio vs F | negligible | small | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | X+F: MSE ratio vs F | lowers | negligible | negligible | negligible | lowers | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | X: MSE ratio vs F | negligible | negligible | negligible | negligible | lowers | replicated | negligible |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | none: MSE ratio vs F | small | small | small | small | negligible | replicated | small |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | separation: MSE ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | A2 (stored): MSE ratio vs F | undetermined | undetermined | undetermined | substantial | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | A3 (stored): MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | A4 (stored): MSE ratio vs F | undetermined | undetermined | undetermined | substantial | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | RO: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | X+F: MSE ratio vs F | undetermined | undetermined | undetermined | lowers | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | X: MSE ratio vs F | undetermined | undetermined | undetermined | lowers | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | none: MSE ratio vs F | undetermined | undetermined | undetermined | substantial | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | separation: MSE ratio vs F | undetermined | undetermined | undetermined | substantial | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | A2 (stored): MSE ratio vs F | substantial | substantial | substantial | undetermined | substantial | replicated | substantial |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | A3 (stored): MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | negligible | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | A4 (stored): MSE ratio vs F | substantial | substantial | substantial | undetermined | substantial | replicated | substantial |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | A5 (stored): MSE ratio vs F | undetermined | needed, size not determined | needed, size not determined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | RO: MSE ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | substantial | undetermined | not replicated | replicated claim: ratio > 1 |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | X+F: MSE ratio vs F | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | X: MSE ratio vs F | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | none: MSE ratio vs F | substantial | substantial | substantial | undetermined | substantial | replicated | substantial |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | separation: MSE ratio vs F | substantial | substantial | substantial | undetermined | substantial | replicated | substantial |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | A2 (stored): MSE ratio vs F | needed, size not determined | undetermined | needed, size not determined | undetermined | needed, size not determined | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | A3 (stored): MSE ratio vs F | undetermined | lowers | negligible | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | A4 (stored): MSE ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | undetermined | substantial | not replicated | replicated claim: ratio > 1 |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | RO: MSE ratio vs F | needed, size not determined | negligible | needed, size not determined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | X+F: MSE ratio vs F | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | X: MSE ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | none: MSE ratio vs F | needed, size not determined | undetermined | needed, size not determined | undetermined | needed, size not determined | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | separation: MSE ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | undetermined | substantial | not replicated | replicated claim: ratio > 1 |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | A2 (stored): MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | A3 (stored): MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | A4 (stored): MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | RO: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | X+F: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | X: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | none: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | separation: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | RO: MSE ratio vs F | negligible | small | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | X+F: MSE ratio vs F | lowers | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | X: MSE ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | none: MSE ratio vs F | small | small | small | small | negligible | replicated | small |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | separation: MSE ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | RO: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | X+F: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | X: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | none: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | separation: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | RO: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | X+F: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | X: MSE ratio vs F | needed, size not determined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | none: MSE ratio vs F | substantial | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | separation: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | RO: MSE ratio vs F | negligible | negligible | negligible | undetermined | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | X+F: MSE ratio vs F | negligible | negligible | negligible | negligible | lowers | replicated | negligible |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | X: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | negligible | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | none: MSE ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | undetermined | replicated | needed, size not determined |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | separation: MSE ratio vs F | undetermined | undetermined | needed, size not determined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | RO: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | X+F: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | X: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | none: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | separation: MSE ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | horizon | deployable | T_c | RO: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | deployable | T_c | X+F: pinball ratio vs F | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | horizon | deployable | T_c | X: pinball ratio vs F | substantial | substantial | substantial | needed, size not determined | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| lorenz63 | horizon | deployable | T_c | lyapunov: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | deployable | T_c | none: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | oracle | T_c | RO: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | oracle | T_c | X+F: pinball ratio vs F | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | horizon | oracle | T_c | X: pinball ratio vs F | substantial | needed, size not determined | substantial | needed, size not determined | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| lorenz63 | horizon | oracle | T_c | lyapunov: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | oracle | T_c | none: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | deployable | H=120 (4.00 LT) | A2 (stored): MSE ratio vs F | negligible | small | small | small | small | replicated | small |
| rossler | allocation | deployable | H=120 (4.00 LT) | A3 (stored): MSE ratio vs F | negligible | small | small | needed, size not determined | small | not replicated | replicated claim: ratio <= 1.05; ratio > 1 |
| rossler | allocation | deployable | H=120 (4.00 LT) | A4 (stored): MSE ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| rossler | allocation | deployable | H=120 (4.00 LT) | RO: MSE ratio vs F | negligible | negligible | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=120 (4.00 LT) | X+F: MSE ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=120 (4.00 LT) | X: MSE ratio vs F | negligible | small | small | small | small | replicated | small |
| rossler | allocation | deployable | H=120 (4.00 LT) | none: MSE ratio vs F | negligible | small | small | small | small | replicated | small |
| rossler | allocation | deployable | H=120 (4.00 LT) | separation: MSE ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| rossler | allocation | deployable | H=15 (0.50 LT) | A2 (stored): MSE ratio vs F | negligible | negligible | undetermined | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=15 (0.50 LT) | A3 (stored): MSE ratio vs F | needed, size not determined | needed, size not determined | undetermined | substantial | substantial | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | deployable | H=15 (0.50 LT) | A4 (stored): MSE ratio vs F | substantial | needed, size not determined | undetermined | substantial | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | deployable | H=15 (0.50 LT) | RO: MSE ratio vs F | negligible | negligible | undetermined | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=15 (0.50 LT) | X+F: MSE ratio vs F | lowers | lowers | undetermined | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=15 (0.50 LT) | X: MSE ratio vs F | negligible | negligible | undetermined | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=15 (0.50 LT) | none: MSE ratio vs F | negligible | negligible | undetermined | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=15 (0.50 LT) | separation: MSE ratio vs F | substantial | needed, size not determined | undetermined | substantial | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | deployable | H=30 (1.00 LT) | A2 (stored): MSE ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | A3 (stored): MSE ratio vs F | needed, size not determined | undetermined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| rossler | allocation | deployable | H=30 (1.00 LT) | A4 (stored): MSE ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| rossler | allocation | deployable | H=30 (1.00 LT) | A5 (stored): MSE ratio vs F | negligible | negligible | negligible | negligible | small | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | RO: MSE ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | X+F: MSE ratio vs F | negligible | lowers | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | X: MSE ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | none: MSE ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | separation: MSE ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| rossler | allocation | deployable | H=60 (2.00 LT) | A2 (stored): MSE ratio vs F | negligible | small | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=60 (2.00 LT) | A3 (stored): MSE ratio vs F | negligible | undetermined | negligible | undetermined | needed, size not determined | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | A4 (stored): MSE ratio vs F | small | small | lowers | negligible | negligible | contradicted | DEV-5 small vs DEV-7 lowers; replicated claim within a contradicted row: ratio <= 1.05 |
| rossler | allocation | deployable | H=60 (2.00 LT) | RO: MSE ratio vs F | negligible | small | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | X+F: MSE ratio vs F | negligible | negligible | negligible | negligible | lowers | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | X: MSE ratio vs F | negligible | small | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | none: MSE ratio vs F | negligible | small | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=60 (2.00 LT) | separation: MSE ratio vs F | small | small | lowers | negligible | negligible | contradicted | DEV-5 small vs DEV-7 lowers; replicated claim within a contradicted row: ratio <= 1.05 |
| rossler | allocation | deployable | H=8 (0.27 LT) | A2 (stored): MSE ratio vs F | undetermined | negligible | undetermined | negligible | negligible | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | A3 (stored): MSE ratio vs F | undetermined | small | undetermined | substantial | substantial | contradicted | DEV-6 small vs DEV-8 substantial |
| rossler | allocation | deployable | H=8 (0.27 LT) | A4 (stored): MSE ratio vs F | undetermined | substantial | undetermined | substantial | substantial | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | RO: MSE ratio vs F | undetermined | negligible | undetermined | negligible | negligible | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | X+F: MSE ratio vs F | undetermined | lowers | undetermined | lowers | lowers | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | X: MSE ratio vs F | undetermined | negligible | undetermined | negligible | negligible | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | none: MSE ratio vs F | undetermined | negligible | undetermined | negligible | negligible | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | separation: MSE ratio vs F | undetermined | substantial | undetermined | substantial | substantial | not replicated |  |
| rossler | allocation | oracle | H=120 (4.00 LT) | RO: MSE ratio vs F | small | negligible | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=120 (4.00 LT) | X+F: MSE ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=120 (4.00 LT) | X: MSE ratio vs F | small | small | small | small | small | replicated | small |
| rossler | allocation | oracle | H=120 (4.00 LT) | none: MSE ratio vs F | small | small | small | small | small | replicated | small |
| rossler | allocation | oracle | H=120 (4.00 LT) | separation: MSE ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| rossler | allocation | oracle | H=15 (0.50 LT) | RO: MSE ratio vs F | undetermined | small | small | small | small | replicated | small |
| rossler | allocation | oracle | H=15 (0.50 LT) | X+F: MSE ratio vs F | undetermined | lowers | lowers | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=15 (0.50 LT) | X: MSE ratio vs F | undetermined | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=15 (0.50 LT) | none: MSE ratio vs F | undetermined | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=15 (0.50 LT) | separation: MSE ratio vs F | undetermined | needed, size not determined | needed, size not determined | substantial | substantial | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | oracle | H=30 (1.00 LT) | RO: MSE ratio vs F | negligible | small | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=30 (1.00 LT) | X+F: MSE ratio vs F | negligible | lowers | negligible | negligible | lowers | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=30 (1.00 LT) | X: MSE ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=30 (1.00 LT) | none: MSE ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=30 (1.00 LT) | separation: MSE ratio vs F | small | small | small | small | small | replicated | small |
| rossler | allocation | oracle | H=60 (2.00 LT) | RO: MSE ratio vs F | negligible | small | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=60 (2.00 LT) | X+F: MSE ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=60 (2.00 LT) | X: MSE ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=60 (2.00 LT) | none: MSE ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=60 (2.00 LT) | separation: MSE ratio vs F | negligible | lowers | lowers | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=8 (0.27 LT) | RO: MSE ratio vs F | undetermined | small | negligible | small | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=8 (0.27 LT) | X+F: MSE ratio vs F | undetermined | lowers | negligible | negligible | lowers | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=8 (0.27 LT) | X: MSE ratio vs F | undetermined | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=8 (0.27 LT) | none: MSE ratio vs F | undetermined | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=8 (0.27 LT) | separation: MSE ratio vs F | undetermined | needed, size not determined | needed, size not determined | substantial | substantial | not replicated | replicated claim: ratio > 1 |
| rossler | horizon | deployable | T_c | RO: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | deployable | T_c | X+F: pinball ratio vs F | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | horizon | deployable | T_c | X: pinball ratio vs F | needed, size not determined | undetermined | undetermined | needed, size not determined | needed, size not determined | not replicated |  |
| rossler | horizon | deployable | T_c | lyapunov: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | deployable | T_c | none: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | oracle | T_c | RO: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | oracle | T_c | X+F: pinball ratio vs F | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | horizon | oracle | T_c | X: pinball ratio vs F | negligible | negligible | negligible | undetermined | undetermined | not replicated |  |
| rossler | horizon | oracle | T_c | lyapunov: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | oracle | T_c | none: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |

## C2 oracle vs deployable

DEVELOPMENT: phase J replication (held-out development seeds), not a hypothesis test.

| system | decision | profile | horizon | item | DEV-5 | DEV-6 | DEV-7 | DEV-8 | DEV-9 | class | replicated reading or claims |
|---|---|---|---|---|---|---|---|---|---|---|---|
| chua | joint | both | forward | retained difference | no difference detected | deployable retains more | deployable retains more | deployable retains more | deployable retains more | replicated | deployable retains more |
| chua | joint | both | forward_w | retained difference | deployable retains less | deployable retains more | no difference detected | deployable retains more | no difference detected | contradicted | DEV-5 deployable retains less vs DEV-6 deployable retains more |
| chua | joint | both | reverse/120 | retained difference | deployable retains more | no difference detected | no difference detected | deployable retains more | deployable retains more | not replicated |  |
| chua | joint | both | reverse/15 | retained difference | not determined (n_eff < 50) | not determined (n_eff < 50) | not determined (n_eff < 50) | not determined (n_eff < 50) | not determined (full-profile skill not established) | not replicated |  |
| chua | joint | both | reverse/30 | retained difference | not determined (n_eff < 50) | not determined (n_eff < 50) | no difference detected | not determined (n_eff < 50) | not determined (full-profile skill not established) | not replicated |  |
| chua | joint | both | reverse/60 | retained difference | deployable retains more | deployable retains more | no difference detected | deployable retains more | no difference detected | not replicated |  |
| chua | joint | both | reverse/8 | retained difference | not determined (n_eff < 50) | not determined (full-profile skill not established) | not determined (n_eff < 50) | not determined (n_eff < 50) | not determined (full-profile skill not established) | not replicated |  |
| chua | joint | both | reverse_w/120 | retained difference | deployable retains more | deployable retains more | deployable retains more | deployable retains more | deployable retains more | replicated | deployable retains more |
| chua | joint | both | reverse_w/15 | retained difference | deployable retains more | no difference detected | deployable retains more | deployable retains more | deployable retains more | replicated | deployable retains more |
| chua | joint | both | reverse_w/30 | retained difference | no difference detected | deployable retains more | deployable retains more | deployable retains more | deployable retains more | replicated | deployable retains more |
| chua | joint | both | reverse_w/60 | retained difference | deployable retains more | deployable retains more | deployable retains more | deployable retains more | deployable retains more | replicated | deployable retains more |
| chua | joint | both | reverse_w/8 | retained difference | no difference detected | no difference detected | deployable retains less | no difference detected | deployable retains less | not replicated |  |
| lorenz63 | joint | both | forward | retained difference | no difference detected | deployable retains more | deployable retains more | deployable retains more | no difference detected | not replicated |  |
| lorenz63 | joint | both | forward_w | retained difference | no difference detected | deployable retains more | deployable retains less | no difference detected | no difference detected | contradicted | DEV-6 deployable retains more vs DEV-7 deployable retains less |
| lorenz63 | joint | both | reverse/120 | retained difference | no difference detected | no difference detected | deployable retains more | deployable retains more | not determined (full-profile skill not established) | not replicated |  |
| lorenz63 | joint | both | reverse/15 | retained difference | not determined (n_eff < 50) | not determined (n_eff < 50) | not determined (n_eff < 50) | not determined (n_eff < 50) | not determined (n_eff < 50) | not replicated |  |
| lorenz63 | joint | both | reverse/30 | retained difference | no difference detected | not determined (n_eff < 50) | not determined (n_eff < 50) | not determined (n_eff < 50) | not determined (n_eff < 50) | not replicated |  |
| lorenz63 | joint | both | reverse/60 | retained difference | deployable retains more | no difference detected | no difference detected | deployable retains more | no difference detected | not replicated |  |
| lorenz63 | joint | both | reverse/8 | retained difference | not determined (n_eff < 50) | not determined (n_eff < 50) | not determined (n_eff < 50) | not determined (n_eff < 50) | not determined (n_eff < 50) | not replicated |  |
| lorenz63 | joint | both | reverse_w/120 | retained difference | deployable retains more | no difference detected | deployable retains more | deployable retains more | deployable retains more | replicated | deployable retains more |
| lorenz63 | joint | both | reverse_w/15 | retained difference | no difference detected | deployable retains more | no difference detected | no difference detected | no difference detected | not replicated |  |
| lorenz63 | joint | both | reverse_w/30 | retained difference | no difference detected | deployable retains more | no difference detected | deployable retains more | no difference detected | not replicated |  |
| lorenz63 | joint | both | reverse_w/60 | retained difference | no difference detected | deployable retains more | deployable retains less | no difference detected | no difference detected | contradicted | DEV-6 deployable retains more vs DEV-7 deployable retains less |
| lorenz63 | joint | both | reverse_w/8 | retained difference | no difference detected | deployable retains more | no difference detected | deployable retains more | no difference detected | not replicated |  |
| rossler | joint | both | forward | retained difference | deployable retains less | no difference detected | deployable retains more | no difference detected | deployable retains more | contradicted | DEV-5 deployable retains less vs DEV-7 deployable retains more |
| rossler | joint | both | forward_w | retained difference | no difference detected | no difference detected | deployable retains more | no difference detected | no difference detected | not replicated |  |
| rossler | joint | both | reverse/120 | retained difference | not determined (full-profile skill not established) | deployable retains more | no difference detected | no difference detected | deployable retains more | not replicated |  |
| rossler | joint | both | reverse/15 | retained difference | not determined (n_eff < 50) | not determined (full-profile skill not established) | not determined (full-profile skill not established) | not determined (full-profile skill not established) | no difference detected | not replicated |  |
| rossler | joint | both | reverse/30 | retained difference | not determined (full-profile skill not established) | not determined (full-profile skill not established) | not determined (full-profile skill not established) | not determined (full-profile skill not established) | not determined (full-profile skill not established) | not replicated |  |
| rossler | joint | both | reverse/60 | retained difference | not determined (full-profile skill not established) | no difference detected | not determined (full-profile skill not established) | no difference detected | not determined (full-profile skill not established) | not replicated |  |
| rossler | joint | both | reverse/8 | retained difference | not determined (n_eff < 50) | not determined (full-profile skill not established) | not determined (full-profile skill not established) | not determined (full-profile skill not established) | not determined (full-profile skill not established) | not replicated |  |
| rossler | joint | both | reverse_w/120 | retained difference | deployable retains more | no difference detected | no difference detected | deployable retains more | deployable retains more | not replicated |  |
| rossler | joint | both | reverse_w/15 | retained difference | deployable retains less | deployable retains less | deployable retains less | deployable retains less | deployable retains less | replicated | deployable retains less |
| rossler | joint | both | reverse_w/30 | retained difference | deployable retains less | deployable retains less | deployable retains less | deployable retains less | deployable retains less | replicated | deployable retains less |
| rossler | joint | both | reverse_w/60 | retained difference | no difference detected | deployable retains less | deployable retains less | deployable retains less | deployable retains less | replicated | deployable retains less |
| rossler | joint | both | reverse_w/8 | retained difference | deployable retains less | deployable retains less | deployable retains less | deployable retains less | deployable retains less | replicated | deployable retains less |

## C2 prediction

DEVELOPMENT: phase J replication (held-out development seeds), not a hypothesis test.

| system | decision | profile | horizon | item | DEV-5 | DEV-6 | DEV-7 | DEV-8 | DEV-9 | class | replicated reading or claims |
|---|---|---|---|---|---|---|---|---|---|---|---|
| chua | joint | deployable | all five | both lose most | not consistent | not consistent | not consistent | not consistent | not consistent | replicated | not consistent |
| chua | joint | oracle | all five | both lose most | not determined | not consistent | consistent | consistent | not determined | contradicted | DEV-6 not consistent vs DEV-7 consistent |
| lorenz63 | joint | deployable | all five | both lose most | not consistent | consistent | consistent | not consistent | not consistent | not replicated |  |
| lorenz63 | joint | oracle | all five | both lose most | consistent | consistent | consistent | consistent | consistent | replicated | consistent |
| rossler | joint | deployable | all five | both lose most | consistent | not determined | not determined | not consistent | not determined | contradicted | DEV-5 consistent vs DEV-8 not consistent |
| rossler | joint | oracle | all five | both lose most | not determined | not determined | consistent | not consistent | consistent | contradicted | DEV-7 consistent vs DEV-8 not consistent |

## C2 ratio

DEVELOPMENT: phase J replication (held-out development seeds), not a hypothesis test.

| system | decision | profile | horizon | item | DEV-5 | DEV-6 | DEV-7 | DEV-8 | DEV-9 | class | replicated reading or claims |
|---|---|---|---|---|---|---|---|---|---|---|---|
| chua | joint | deployable | H=120 (4.00 LT) | reverse MSE(h)/MSE(F) | negligible | small | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | joint | deployable | H=15 (0.50 LT) | reverse MSE(h)/MSE(F) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | joint | deployable | H=30 (1.00 LT) | reverse MSE(h)/MSE(F) | undetermined | undetermined | negligible | undetermined | negligible | not replicated |  |
| chua | joint | deployable | H=60 (2.00 LT) | reverse MSE(h)/MSE(F) | negligible | negligible | needed, size not determined | small | small | not replicated | replicated claim: ratio <= 1.05 |
| chua | joint | deployable | H=8 (0.27 LT) | reverse MSE(h)/MSE(F) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | joint | deployable | all five | forward pinball_ratio_bottleneck_over_F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | joint | deployable | all five | forward pinball_ratio_bottleneck_over_F_w | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | joint | oracle | H=120 (4.00 LT) | reverse MSE(h)/MSE(F) | small | small | small | small | small | replicated | small |
| chua | joint | oracle | H=15 (0.50 LT) | reverse MSE(h)/MSE(F) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | joint | oracle | H=30 (1.00 LT) | reverse MSE(h)/MSE(F) | undetermined | undetermined | needed, size not determined | undetermined | needed, size not determined | not replicated |  |
| chua | joint | oracle | H=60 (2.00 LT) | reverse MSE(h)/MSE(F) | substantial | needed, size not determined | needed, size not determined | substantial | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| chua | joint | oracle | H=8 (0.27 LT) | reverse MSE(h)/MSE(F) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | joint | oracle | all five | forward pinball_ratio_bottleneck_over_F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | joint | oracle | all five | forward pinball_ratio_bottleneck_over_F_w | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | joint | deployable | H=120 (4.00 LT) | reverse MSE(h)/MSE(F) | negligible | negligible | small | negligible | negligible | replicated | negligible |
| lorenz63 | joint | deployable | H=15 (0.50 LT) | reverse MSE(h)/MSE(F) | undetermined | undetermined | undetermined | substantial | undetermined | not replicated |  |
| lorenz63 | joint | deployable | H=30 (1.00 LT) | reverse MSE(h)/MSE(F) | substantial | substantial | substantial | undetermined | substantial | replicated | substantial |
| lorenz63 | joint | deployable | H=60 (2.00 LT) | reverse MSE(h)/MSE(F) | needed, size not determined | negligible | needed, size not determined | negligible | negligible | not replicated |  |
| lorenz63 | joint | deployable | H=8 (0.27 LT) | reverse MSE(h)/MSE(F) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | joint | deployable | all five | forward pinball_ratio_bottleneck_over_F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | joint | deployable | all five | forward pinball_ratio_bottleneck_over_F_w | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | joint | oracle | H=120 (4.00 LT) | reverse MSE(h)/MSE(F) | small | negligible | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | joint | oracle | H=15 (0.50 LT) | reverse MSE(h)/MSE(F) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | joint | oracle | H=30 (1.00 LT) | reverse MSE(h)/MSE(F) | substantial | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | joint | oracle | H=60 (2.00 LT) | reverse MSE(h)/MSE(F) | substantial | substantial | needed, size not determined | needed, size not determined | undetermined | not replicated | replicated claim: ratio > 1 |
| lorenz63 | joint | oracle | H=8 (0.27 LT) | reverse MSE(h)/MSE(F) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | joint | oracle | all five | forward pinball_ratio_bottleneck_over_F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | joint | oracle | all five | forward pinball_ratio_bottleneck_over_F_w | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | joint | deployable | H=120 (4.00 LT) | reverse MSE(h)/MSE(F) | negligible | negligible | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | joint | deployable | H=15 (0.50 LT) | reverse MSE(h)/MSE(F) | negligible | negligible | undetermined | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | joint | deployable | H=30 (1.00 LT) | reverse MSE(h)/MSE(F) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | joint | deployable | H=60 (2.00 LT) | reverse MSE(h)/MSE(F) | negligible | small | lowers | small | negligible | contradicted | DEV-6 small vs DEV-7 lowers; replicated claim within a contradicted row: ratio <= 1.05 |
| rossler | joint | deployable | H=8 (0.27 LT) | reverse MSE(h)/MSE(F) | undetermined | small | undetermined | negligible | negligible | not replicated |  |
| rossler | joint | deployable | all five | forward pinball_ratio_bottleneck_over_F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | joint | deployable | all five | forward pinball_ratio_bottleneck_over_F_w | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | joint | oracle | H=120 (4.00 LT) | reverse MSE(h)/MSE(F) | small | small | small | small | small | replicated | small |
| rossler | joint | oracle | H=15 (0.50 LT) | reverse MSE(h)/MSE(F) | undetermined | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | joint | oracle | H=30 (1.00 LT) | reverse MSE(h)/MSE(F) | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | joint | oracle | H=60 (2.00 LT) | reverse MSE(h)/MSE(F) | substantial | substantial | needed, size not determined | substantial | substantial | replicated | substantial |
| rossler | joint | oracle | H=8 (0.27 LT) | reverse MSE(h)/MSE(F) | undetermined | substantial | needed, size not determined | substantial | substantial | not replicated | replicated claim: ratio > 1 |
| rossler | joint | oracle | all five | forward pinball_ratio_bottleneck_over_F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | joint | oracle | all five | forward pinball_ratio_bottleneck_over_F_w | substantial | substantial | substantial | substantial | substantial | replicated | substantial |

## C2 retained

DEVELOPMENT: phase J replication (held-out development seeds), not a hypothesis test.

| system | decision | profile | horizon | item | DEV-5 | DEV-6 | DEV-7 | DEV-8 | DEV-9 | class | replicated reading or claims |
|---|---|---|---|---|---|---|---|---|---|---|---|
| chua | joint | deployable | H=120 (4.00 LT) | forward one weight retained | loses most | loses most | loses most | loses most | not determined (interval spans 0.5) | replicated | loses most |
| chua | joint | deployable | H=120 (4.00 LT) | reverse retained | keeps most | not determined (interval spans 0.5) | loses most | keeps most | not determined (interval spans 0.5) | contradicted | DEV-5 keeps most vs DEV-7 loses most |
| chua | joint | deployable | H=120 (4.00 LT) | reverse retained_w | not determined (interval spans 0.5) | keeps most | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not replicated |  |
| chua | joint | deployable | H=15 (0.50 LT) | forward one weight retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| chua | joint | deployable | H=15 (0.50 LT) | reverse retained | not determined (full-profile skill not established) | not determined (full-profile skill not established) | not determined (full-profile skill not established) | not determined (full-profile skill not established) | not determined (full-profile skill not established) | not replicated |  |
| chua | joint | deployable | H=15 (0.50 LT) | reverse retained_w | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| chua | joint | deployable | H=30 (1.00 LT) | forward one weight retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| chua | joint | deployable | H=30 (1.00 LT) | reverse retained | not determined (full-profile skill not established) | not determined (n_eff < 50) | not determined (interval spans 0.5) | not determined (n_eff < 50) | not determined (full-profile skill not established) | not replicated |  |
| chua | joint | deployable | H=30 (1.00 LT) | reverse retained_w | loses most | loses most | not determined (interval spans 0.5) | not determined (interval spans 0.5) | loses most | not replicated |  |
| chua | joint | deployable | H=60 (2.00 LT) | forward one weight retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| chua | joint | deployable | H=60 (2.00 LT) | reverse retained | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not replicated |  |
| chua | joint | deployable | H=60 (2.00 LT) | reverse retained_w | keeps most | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not replicated |  |
| chua | joint | deployable | H=8 (0.27 LT) | forward one weight retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| chua | joint | deployable | H=8 (0.27 LT) | reverse retained | not determined (full-profile skill not established) | not determined (full-profile skill not established) | not determined (full-profile skill not established) | not determined (full-profile skill not established) | not determined (full-profile skill not established) | not replicated |  |
| chua | joint | deployable | H=8 (0.27 LT) | reverse retained_w | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| chua | joint | deployable | all five | forward retained | not determined (interval spans 0.5) | keeps most | keeps most | keeps most | keeps most | replicated | keeps most |
| chua | joint | deployable | all five | forward retained_w | not determined (interval spans 0.5) | keeps most | keeps most | keeps most | keeps most | replicated | keeps most |
| chua | joint | oracle | H=120 (4.00 LT) | forward one weight retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| chua | joint | oracle | H=120 (4.00 LT) | reverse retained | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not replicated |  |
| chua | joint | oracle | H=120 (4.00 LT) | reverse retained_w | loses most | loses most | not determined (interval spans 0.5) | loses most | loses most | replicated | loses most |
| chua | joint | oracle | H=15 (0.50 LT) | forward one weight retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| chua | joint | oracle | H=15 (0.50 LT) | reverse retained | not determined (n_eff < 50) | not determined (n_eff < 50) | not determined (n_eff < 50) | not determined (n_eff < 50) | not determined (full-profile skill not established) | not replicated |  |
| chua | joint | oracle | H=15 (0.50 LT) | reverse retained_w | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| chua | joint | oracle | H=30 (1.00 LT) | forward one weight retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| chua | joint | oracle | H=30 (1.00 LT) | reverse retained | not determined (n_eff < 50) | not determined (n_eff < 50) | not determined (interval spans 0.5) | not determined (n_eff < 50) | not determined (interval spans 0.5) | not replicated |  |
| chua | joint | oracle | H=30 (1.00 LT) | reverse retained_w | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| chua | joint | oracle | H=60 (2.00 LT) | forward one weight retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| chua | joint | oracle | H=60 (2.00 LT) | reverse retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| chua | joint | oracle | H=60 (2.00 LT) | reverse retained_w | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| chua | joint | oracle | H=8 (0.27 LT) | forward one weight retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| chua | joint | oracle | H=8 (0.27 LT) | reverse retained | not determined (n_eff < 50) | not determined (full-profile skill not established) | not determined (n_eff < 50) | not determined (n_eff < 50) | not determined (full-profile skill not established) | not replicated |  |
| chua | joint | oracle | H=8 (0.27 LT) | reverse retained_w | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| chua | joint | oracle | all five | forward retained | not determined (interval spans 0.5) | keeps most | loses most | loses most | not determined (interval spans 0.5) | contradicted | DEV-6 keeps most vs DEV-7 loses most |
| chua | joint | oracle | all five | forward retained_w | keeps most | keeps most | keeps most | not determined (interval spans 0.5) | keeps most | replicated | keeps most |
| lorenz63 | joint | deployable | H=120 (4.00 LT) | forward one weight retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| lorenz63 | joint | deployable | H=120 (4.00 LT) | reverse retained | keeps most | not determined (interval spans 0.5) | not determined (interval spans 0.5) | keeps most | not determined (full-profile skill not established) | not replicated |  |
| lorenz63 | joint | deployable | H=120 (4.00 LT) | reverse retained_w | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not replicated |  |
| lorenz63 | joint | deployable | H=15 (0.50 LT) | forward one weight retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| lorenz63 | joint | deployable | H=15 (0.50 LT) | reverse retained | not determined (n_eff < 50) | not determined (n_eff < 50) | not determined (n_eff < 50) | loses most | not determined (full-profile skill not established) | not replicated |  |
| lorenz63 | joint | deployable | H=15 (0.50 LT) | reverse retained_w | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| lorenz63 | joint | deployable | H=30 (1.00 LT) | forward one weight retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| lorenz63 | joint | deployable | H=30 (1.00 LT) | reverse retained | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not replicated |  |
| lorenz63 | joint | deployable | H=30 (1.00 LT) | reverse retained_w | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| lorenz63 | joint | deployable | H=60 (2.00 LT) | forward one weight retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| lorenz63 | joint | deployable | H=60 (2.00 LT) | reverse retained | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not determined (interval spans 0.5) | keeps most | not replicated |  |
| lorenz63 | joint | deployable | H=60 (2.00 LT) | reverse retained_w | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| lorenz63 | joint | deployable | H=8 (0.27 LT) | forward one weight retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| lorenz63 | joint | deployable | H=8 (0.27 LT) | reverse retained | not determined (full-profile skill not established) | not determined (n_eff < 50) | not determined (full-profile skill not established) | not determined (full-profile skill not established) | not determined (n_eff < 50) | not replicated |  |
| lorenz63 | joint | deployable | H=8 (0.27 LT) | reverse retained_w | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| lorenz63 | joint | deployable | all five | forward retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| lorenz63 | joint | deployable | all five | forward retained_w | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| lorenz63 | joint | oracle | H=120 (4.00 LT) | forward one weight retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| lorenz63 | joint | oracle | H=120 (4.00 LT) | reverse retained | not determined (interval spans 0.5) | not determined (interval spans 0.5) | loses most | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not replicated |  |
| lorenz63 | joint | oracle | H=120 (4.00 LT) | reverse retained_w | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| lorenz63 | joint | oracle | H=15 (0.50 LT) | forward one weight retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| lorenz63 | joint | oracle | H=15 (0.50 LT) | reverse retained | not determined (n_eff < 50) | not determined (n_eff < 50) | not determined (n_eff < 50) | not determined (n_eff < 50) | not determined (n_eff < 50) | not replicated |  |
| lorenz63 | joint | oracle | H=15 (0.50 LT) | reverse retained_w | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| lorenz63 | joint | oracle | H=30 (1.00 LT) | forward one weight retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| lorenz63 | joint | oracle | H=30 (1.00 LT) | reverse retained | loses most | not determined (n_eff < 50) | not determined (n_eff < 50) | not determined (n_eff < 50) | not determined (n_eff < 50) | not replicated |  |
| lorenz63 | joint | oracle | H=30 (1.00 LT) | reverse retained_w | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| lorenz63 | joint | oracle | H=60 (2.00 LT) | forward one weight retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| lorenz63 | joint | oracle | H=60 (2.00 LT) | reverse retained | loses most | loses most | not determined (interval spans 0.5) | loses most | not determined (interval spans 0.5) | not replicated |  |
| lorenz63 | joint | oracle | H=60 (2.00 LT) | reverse retained_w | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| lorenz63 | joint | oracle | H=8 (0.27 LT) | forward one weight retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| lorenz63 | joint | oracle | H=8 (0.27 LT) | reverse retained | not determined (n_eff < 50) | not determined (n_eff < 50) | not determined (n_eff < 50) | not determined (n_eff < 50) | not determined (n_eff < 50) | not replicated |  |
| lorenz63 | joint | oracle | H=8 (0.27 LT) | reverse retained_w | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| lorenz63 | joint | oracle | all five | forward retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| lorenz63 | joint | oracle | all five | forward retained_w | loses most | loses most | loses most | loses most | not determined (interval spans 0.5) | replicated | loses most |
| rossler | joint | deployable | H=120 (4.00 LT) | forward one weight retained | loses most | loses most | loses most | keeps most | loses most | contradicted | DEV-5 loses most vs DEV-8 keeps most |
| rossler | joint | deployable | H=120 (4.00 LT) | reverse retained | not determined (full-profile skill not established) | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not replicated |  |
| rossler | joint | deployable | H=120 (4.00 LT) | reverse retained_w | keeps most | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not replicated |  |
| rossler | joint | deployable | H=15 (0.50 LT) | forward one weight retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| rossler | joint | deployable | H=15 (0.50 LT) | reverse retained | not determined (full-profile skill not established) | not determined (full-profile skill not established) | not determined (full-profile skill not established) | not determined (full-profile skill not established) | not determined (interval spans 0.5) | not replicated |  |
| rossler | joint | deployable | H=15 (0.50 LT) | reverse retained_w | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| rossler | joint | deployable | H=30 (1.00 LT) | forward one weight retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| rossler | joint | deployable | H=30 (1.00 LT) | reverse retained | not determined (full-profile skill not established) | not determined (full-profile skill not established) | not determined (full-profile skill not established) | not determined (full-profile skill not established) | not determined (full-profile skill not established) | not replicated |  |
| rossler | joint | deployable | H=30 (1.00 LT) | reverse retained_w | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| rossler | joint | deployable | H=60 (2.00 LT) | forward one weight retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| rossler | joint | deployable | H=60 (2.00 LT) | reverse retained | not determined (full-profile skill not established) | loses most | not determined (full-profile skill not established) | not determined (interval spans 0.5) | not determined (full-profile skill not established) | not replicated |  |
| rossler | joint | deployable | H=60 (2.00 LT) | reverse retained_w | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| rossler | joint | deployable | H=8 (0.27 LT) | forward one weight retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| rossler | joint | deployable | H=8 (0.27 LT) | reverse retained | not determined (full-profile skill not established) | not determined (full-profile skill not established) | not determined (full-profile skill not established) | not determined (full-profile skill not established) | not determined (full-profile skill not established) | not replicated |  |
| rossler | joint | deployable | H=8 (0.27 LT) | reverse retained_w | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| rossler | joint | deployable | all five | forward retained | loses most | not determined (interval spans 0.5) | not determined (interval spans 0.5) | keeps most | not determined (interval spans 0.5) | contradicted | DEV-5 loses most vs DEV-8 keeps most |
| rossler | joint | deployable | all five | forward retained_w | keeps most | not determined (interval spans 0.5) | keeps most | keeps most | keeps most | replicated | keeps most |
| rossler | joint | oracle | H=120 (4.00 LT) | forward one weight retained | loses most | loses most | loses most | keeps most | loses most | contradicted | DEV-5 loses most vs DEV-8 keeps most |
| rossler | joint | oracle | H=120 (4.00 LT) | reverse retained | not determined (interval spans 0.5) | not determined (interval spans 0.5) | loses most | not determined (interval spans 0.5) | not determined (interval spans 0.5) | not replicated |  |
| rossler | joint | oracle | H=120 (4.00 LT) | reverse retained_w | loses most | not determined (interval spans 0.5) | not determined (interval spans 0.5) | loses most | loses most | not replicated |  |
| rossler | joint | oracle | H=15 (0.50 LT) | forward one weight retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| rossler | joint | oracle | H=15 (0.50 LT) | reverse retained | not determined (n_eff < 50) | loses most | loses most | loses most | loses most | replicated | loses most |
| rossler | joint | oracle | H=15 (0.50 LT) | reverse retained_w | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| rossler | joint | oracle | H=30 (1.00 LT) | forward one weight retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| rossler | joint | oracle | H=30 (1.00 LT) | reverse retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| rossler | joint | oracle | H=30 (1.00 LT) | reverse retained_w | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| rossler | joint | oracle | H=60 (2.00 LT) | forward one weight retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| rossler | joint | oracle | H=60 (2.00 LT) | reverse retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| rossler | joint | oracle | H=60 (2.00 LT) | reverse retained_w | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| rossler | joint | oracle | H=8 (0.27 LT) | forward one weight retained | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| rossler | joint | oracle | H=8 (0.27 LT) | reverse retained | not determined (n_eff < 50) | loses most | loses most | loses most | loses most | replicated | loses most |
| rossler | joint | oracle | H=8 (0.27 LT) | reverse retained_w | loses most | loses most | loses most | loses most | loses most | replicated | loses most |
| rossler | joint | oracle | all five | forward retained | not determined (interval spans 0.5) | not determined (interval spans 0.5) | loses most | keeps most | loses most | contradicted | DEV-7 loses most vs DEV-8 keeps most |
| rossler | joint | oracle | all five | forward retained_w | keeps most | not determined (interval spans 0.5) | not determined (interval spans 0.5) | keeps most | not determined (interval spans 0.5) | not replicated |  |

## C3 ratio

DEVELOPMENT: phase J replication (held-out development seeds), not a hypothesis test.

| system | decision | profile | horizon | item | DEV-5 | DEV-6 | DEV-7 | DEV-8 | DEV-9 | class | replicated reading or claims |
|---|---|---|---|---|---|---|---|---|---|---|---|
| chua | joint | deployable | H=120 (4.00 LT) | A2 + constant: MSE ratio to A2 | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | joint | deployable | H=120 (4.00 LT) | A2 + h(F-hat): MSE ratio to A2 | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | joint | deployable | H=120 (4.00 LT) | A4 + KM leaf: MSE ratio to A2 | needed, size not determined | small | needed, size not determined | small | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| chua | joint | deployable | H=120 (4.00 LT) | g(F-hat) + h(F-hat): MSE ratio to A2 | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | joint | deployable | H=15 (0.50 LT) | A2 + constant: MSE ratio to A2 | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | joint | deployable | H=15 (0.50 LT) | A2 + h(F-hat): MSE ratio to A2 | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | joint | deployable | H=15 (0.50 LT) | A4 + KM leaf: MSE ratio to A2 | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | joint | deployable | H=15 (0.50 LT) | g(F-hat) + h(F-hat): MSE ratio to A2 | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | joint | deployable | H=30 (1.00 LT) | A2 + constant: MSE ratio to A2 | undetermined | undetermined | negligible | undetermined | negligible | not replicated |  |
| chua | joint | deployable | H=30 (1.00 LT) | A2 + h(F-hat): MSE ratio to A2 | undetermined | undetermined | negligible | undetermined | negligible | not replicated |  |
| chua | joint | deployable | H=30 (1.00 LT) | A4 + KM leaf: MSE ratio to A2 | undetermined | undetermined | negligible | undetermined | negligible | not replicated |  |
| chua | joint | deployable | H=30 (1.00 LT) | g(F-hat) + h(F-hat): MSE ratio to A2 | undetermined | undetermined | lowers | undetermined | negligible | not replicated |  |
| chua | joint | deployable | H=60 (2.00 LT) | A2 + constant: MSE ratio to A2 | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | joint | deployable | H=60 (2.00 LT) | A2 + h(F-hat): MSE ratio to A2 | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | joint | deployable | H=60 (2.00 LT) | A4 + KM leaf: MSE ratio to A2 | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | joint | deployable | H=60 (2.00 LT) | g(F-hat) + h(F-hat): MSE ratio to A2 | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | joint | deployable | H=8 (0.27 LT) | A2 + constant: MSE ratio to A2 | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | joint | deployable | H=8 (0.27 LT) | A2 + h(F-hat): MSE ratio to A2 | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | joint | deployable | H=8 (0.27 LT) | A4 + KM leaf: MSE ratio to A2 | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | joint | deployable | H=8 (0.27 LT) | g(F-hat) + h(F-hat): MSE ratio to A2 | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | joint | deployable | T_c | h_A2(F-hat): pinball constant/model | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | joint | deployable | T_c | h_g(F-hat): pinball constant/model | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | joint | deployable | H=120 (4.00 LT) | A2 + constant: MSE ratio to A2 | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | joint | deployable | H=120 (4.00 LT) | A2 + h(F-hat): MSE ratio to A2 | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | joint | deployable | H=120 (4.00 LT) | A4 + KM leaf: MSE ratio to A2 | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| lorenz63 | joint | deployable | H=120 (4.00 LT) | g(F-hat) + h(F-hat): MSE ratio to A2 | lowers | lowers | lowers | lowers | negligible | replicated | lowers |
| lorenz63 | joint | deployable | H=15 (0.50 LT) | A2 + constant: MSE ratio to A2 | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | joint | deployable | H=15 (0.50 LT) | A2 + h(F-hat): MSE ratio to A2 | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | joint | deployable | H=15 (0.50 LT) | A4 + KM leaf: MSE ratio to A2 | undetermined | substantial | undetermined | substantial | undetermined | not replicated |  |
| lorenz63 | joint | deployable | H=15 (0.50 LT) | g(F-hat) + h(F-hat): MSE ratio to A2 | lowers | lowers | lowers | lowers | undetermined | replicated | lowers |
| lorenz63 | joint | deployable | H=30 (1.00 LT) | A2 + constant: MSE ratio to A2 | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | joint | deployable | H=30 (1.00 LT) | A2 + h(F-hat): MSE ratio to A2 | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | joint | deployable | H=30 (1.00 LT) | A4 + KM leaf: MSE ratio to A2 | needed, size not determined | substantial | substantial | needed, size not determined | substantial | not replicated | replicated claim: ratio > 1 |
| lorenz63 | joint | deployable | H=30 (1.00 LT) | g(F-hat) + h(F-hat): MSE ratio to A2 | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | joint | deployable | H=60 (2.00 LT) | A2 + constant: MSE ratio to A2 | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | joint | deployable | H=60 (2.00 LT) | A2 + h(F-hat): MSE ratio to A2 | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | joint | deployable | H=60 (2.00 LT) | A4 + KM leaf: MSE ratio to A2 | negligible | small | small | negligible | needed, size not determined | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | joint | deployable | H=60 (2.00 LT) | g(F-hat) + h(F-hat): MSE ratio to A2 | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | joint | deployable | H=8 (0.27 LT) | A2 + constant: MSE ratio to A2 | undetermined | undetermined | undetermined | negligible | negligible | not replicated |  |
| lorenz63 | joint | deployable | H=8 (0.27 LT) | A2 + h(F-hat): MSE ratio to A2 | undetermined | undetermined | undetermined | negligible | negligible | not replicated |  |
| lorenz63 | joint | deployable | H=8 (0.27 LT) | A4 + KM leaf: MSE ratio to A2 | undetermined | undetermined | undetermined | substantial | substantial | not replicated |  |
| lorenz63 | joint | deployable | H=8 (0.27 LT) | g(F-hat) + h(F-hat): MSE ratio to A2 | undetermined | undetermined | undetermined | negligible | lowers | not replicated |  |
| lorenz63 | joint | deployable | T_c | h_A2(F-hat): pinball constant/model | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | joint | deployable | T_c | h_g(F-hat): pinball constant/model | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | joint | deployable | H=120 (4.00 LT) | A2 + constant: MSE ratio to A2 | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | joint | deployable | H=120 (4.00 LT) | A2 + h(F-hat): MSE ratio to A2 | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | joint | deployable | H=120 (4.00 LT) | A4 + KM leaf: MSE ratio to A2 | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| rossler | joint | deployable | H=120 (4.00 LT) | g(F-hat) + h(F-hat): MSE ratio to A2 | negligible | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | joint | deployable | H=15 (0.50 LT) | A2 + constant: MSE ratio to A2 | negligible | negligible | undetermined | negligible | negligible | replicated | negligible |
| rossler | joint | deployable | H=15 (0.50 LT) | A2 + h(F-hat): MSE ratio to A2 | negligible | negligible | undetermined | negligible | negligible | replicated | negligible |
| rossler | joint | deployable | H=15 (0.50 LT) | A4 + KM leaf: MSE ratio to A2 | substantial | needed, size not determined | undetermined | substantial | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| rossler | joint | deployable | H=15 (0.50 LT) | g(F-hat) + h(F-hat): MSE ratio to A2 | negligible | negligible | undetermined | negligible | lowers | not replicated | replicated claim: ratio <= 1.05 |
| rossler | joint | deployable | H=30 (1.00 LT) | A2 + constant: MSE ratio to A2 | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | joint | deployable | H=30 (1.00 LT) | A2 + h(F-hat): MSE ratio to A2 | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | joint | deployable | H=30 (1.00 LT) | A4 + KM leaf: MSE ratio to A2 | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | small | replicated | needed, size not determined |
| rossler | joint | deployable | H=30 (1.00 LT) | g(F-hat) + h(F-hat): MSE ratio to A2 | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | joint | deployable | H=60 (2.00 LT) | A2 + constant: MSE ratio to A2 | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | joint | deployable | H=60 (2.00 LT) | A2 + h(F-hat): MSE ratio to A2 | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | joint | deployable | H=60 (2.00 LT) | A4 + KM leaf: MSE ratio to A2 | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | joint | deployable | H=60 (2.00 LT) | g(F-hat) + h(F-hat): MSE ratio to A2 | negligible | lowers | needed, size not determined | lowers | negligible | contradicted | DEV-6 lowers vs DEV-7 needed, size not determined; replicated claim within a contradicted row: ratio <= 1.05 |
| rossler | joint | deployable | H=8 (0.27 LT) | A2 + constant: MSE ratio to A2 | negligible | negligible | undetermined | negligible | negligible | replicated | negligible |
| rossler | joint | deployable | H=8 (0.27 LT) | A2 + h(F-hat): MSE ratio to A2 | negligible | negligible | undetermined | negligible | negligible | replicated | negligible |
| rossler | joint | deployable | H=8 (0.27 LT) | A4 + KM leaf: MSE ratio to A2 | substantial | substantial | undetermined | substantial | substantial | replicated | substantial |
| rossler | joint | deployable | H=8 (0.27 LT) | g(F-hat) + h(F-hat): MSE ratio to A2 | negligible | negligible | undetermined | negligible | negligible | replicated | negligible |
| rossler | joint | deployable | T_c | h_A2(F-hat): pinball constant/model | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | joint | deployable | T_c | h_g(F-hat): pinball constant/model | substantial | substantial | substantial | substantial | substantial | replicated | substantial |

## D vs below

DEVELOPMENT: phase J replication (held-out development seeds), not a hypothesis test.

| system | decision | profile | horizon | item | DEV-5 | DEV-6 | DEV-7 | DEV-8 | DEV-9 | class | replicated reading or claims |
|---|---|---|---|---|---|---|---|---|---|---|---|
| chua | allocation | deployable | H=120 (4.00 LT) | A2 (stored) -> separation | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | deployable | H=120 (4.00 LT) | A3 (stored) -> X+F | needed, size not determined | small | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| chua | allocation | deployable | H=120 (4.00 LT) | A4 (stored) -> RO | needed, size not determined | needed, size not determined | substantial | needed, size not determined | substantial | not replicated | replicated claim: ratio > 1 |
| chua | allocation | deployable | H=120 (4.00 LT) | I -> N | negligible | negligible | negligible | lowers | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | N -> ROIN | small | small | small | small | small | replicated | small |
| chua | allocation | deployable | H=120 (4.00 LT) | O -> I | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | R -> O | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | RO -> R | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | deployable | H=120 (4.00 LT) | ROIN -> X | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | deployable | H=120 (4.00 LT) | X -> A3 (stored) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | deployable | H=120 (4.00 LT) | none -> A2 (stored) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | separation -> A4 (stored) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=15 (0.50 LT) | A2 (stored) -> separation | undetermined | negligible | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | A3 (stored) -> X+F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | A4 (stored) -> RO | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | I -> N | undetermined | undetermined | undetermined | undetermined | negligible | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | N -> ROIN | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | O -> I | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | R -> O | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | RO -> R | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | ROIN -> X | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | X -> A3 (stored) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | none -> A2 (stored) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | separation -> A4 (stored) | undetermined | negligible | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | A2 (stored) -> separation | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | A3 (stored) -> X+F | undetermined | undetermined | negligible | undetermined | negligible | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | A4 (stored) -> RO | undetermined | undetermined | negligible | undetermined | negligible | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | A5 (stored) -> ROIN | undetermined | undetermined | needed, size not determined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | I -> N | undetermined | undetermined | negligible | undetermined | negligible | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | N -> A5 (stored) | undetermined | undetermined | negligible | undetermined | negligible | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | O -> I | undetermined | undetermined | negligible | undetermined | needed, size not determined | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | R -> O | undetermined | undetermined | negligible | undetermined | lowers | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | RO -> R | undetermined | undetermined | negligible | undetermined | negligible | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | ROIN -> X | undetermined | undetermined | lowers | undetermined | lowers | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | X -> A3 (stored) | undetermined | undetermined | undetermined | undetermined | needed, size not determined | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | none -> A2 (stored) | undetermined | undetermined | negligible | undetermined | negligible | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | separation -> A4 (stored) | undetermined | undetermined | negligible | undetermined | negligible | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | A2 (stored) -> separation | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=60 (2.00 LT) | A3 (stored) -> X+F | negligible | negligible | needed, size not determined | needed, size not determined | needed, size not determined | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | A4 (stored) -> RO | small | small | needed, size not determined | small | small | replicated | small |
| chua | allocation | deployable | H=60 (2.00 LT) | I -> N | small | negligible | negligible | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=60 (2.00 LT) | N -> ROIN | small | small | needed, size not determined | small | negligible | not replicated | replicated claim: ratio > 1; ratio <= 1.05 |
| chua | allocation | deployable | H=60 (2.00 LT) | O -> I | negligible | negligible | negligible | negligible | lowers | replicated | negligible |
| chua | allocation | deployable | H=60 (2.00 LT) | R -> O | negligible | negligible | negligible | negligible | small | replicated | negligible |
| chua | allocation | deployable | H=60 (2.00 LT) | RO -> R | lowers | lowers | lowers | lowers | negligible | replicated | lowers |
| chua | allocation | deployable | H=60 (2.00 LT) | ROIN -> X | negligible | negligible | negligible | lowers | negligible | replicated | negligible |
| chua | allocation | deployable | H=60 (2.00 LT) | X -> A3 (stored) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=60 (2.00 LT) | none -> A2 (stored) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=60 (2.00 LT) | separation -> A4 (stored) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=8 (0.27 LT) | A2 (stored) -> separation | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | A3 (stored) -> X+F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | A4 (stored) -> RO | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | I -> N | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | N -> ROIN | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | O -> I | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | R -> O | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | RO -> R | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | ROIN -> X | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | X -> A3 (stored) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | none -> A2 (stored) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | separation -> A4 (stored) | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=120 (4.00 LT) | I -> N | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=120 (4.00 LT) | N -> ROIN | small | small | small | small | small | replicated | small |
| chua | allocation | oracle | H=120 (4.00 LT) | O -> I | negligible | negligible | small | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=120 (4.00 LT) | R -> O | lowers | lowers | lowers | lowers | negligible | replicated | lowers |
| chua | allocation | oracle | H=120 (4.00 LT) | RO -> R | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | oracle | H=120 (4.00 LT) | ROIN -> X | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | oracle | H=120 (4.00 LT) | X -> X+F | small | small | small | small | small | replicated | small |
| chua | allocation | oracle | H=120 (4.00 LT) | none -> separation | lowers | lowers | lowers | negligible | lowers | replicated | lowers |
| chua | allocation | oracle | H=120 (4.00 LT) | separation -> RO | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| chua | allocation | oracle | H=15 (0.50 LT) | I -> N | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | N -> ROIN | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | O -> I | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | R -> O | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | RO -> R | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | ROIN -> X | undetermined | lowers | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | X -> X+F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | none -> separation | undetermined | undetermined | undetermined | substantial | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | separation -> RO | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | I -> N | undetermined | undetermined | negligible | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | N -> ROIN | undetermined | undetermined | needed, size not determined | undetermined | needed, size not determined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | O -> I | undetermined | undetermined | negligible | undetermined | negligible | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | R -> O | undetermined | undetermined | negligible | undetermined | negligible | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | RO -> R | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | ROIN -> X | undetermined | undetermined | lowers | undetermined | lowers | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | X -> X+F | undetermined | undetermined | undetermined | undetermined | substantial | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | none -> separation | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | separation -> RO | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=60 (2.00 LT) | I -> N | small | negligible | negligible | small | small | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=60 (2.00 LT) | N -> ROIN | needed, size not determined | substantial | substantial | needed, size not determined | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| chua | allocation | oracle | H=60 (2.00 LT) | O -> I | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=60 (2.00 LT) | R -> O | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | oracle | H=60 (2.00 LT) | RO -> R | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | oracle | H=60 (2.00 LT) | ROIN -> X | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | allocation | oracle | H=60 (2.00 LT) | X -> X+F | substantial | needed, size not determined | needed, size not determined | substantial | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| chua | allocation | oracle | H=60 (2.00 LT) | none -> separation | substantial | needed, size not determined | needed, size not determined | substantial | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| chua | allocation | oracle | H=60 (2.00 LT) | separation -> RO | small | small | small | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=8 (0.27 LT) | I -> N | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | N -> ROIN | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | O -> I | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | R -> O | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | RO -> R | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | ROIN -> X | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | X -> X+F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | none -> separation | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | separation -> RO | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | horizon | deployable | T_c | I -> N | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | horizon | deployable | T_c | N -> ROIN | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | deployable | T_c | O -> I | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | deployable | T_c | R -> O | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | deployable | T_c | RO -> R | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | horizon | deployable | T_c | ROIN -> X | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | horizon | deployable | T_c | X -> X+F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | deployable | T_c | lyapunov -> RO | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | deployable | T_c | none -> lyapunov | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | horizon | oracle | T_c | I -> N | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | horizon | oracle | T_c | N -> ROIN | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | oracle | T_c | O -> I | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | oracle | T_c | R -> O | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | oracle | T_c | RO -> R | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | horizon | oracle | T_c | ROIN -> X | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | horizon | oracle | T_c | X -> X+F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | oracle | T_c | lyapunov -> RO | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | oracle | T_c | none -> lyapunov | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | A2 (stored) -> separation | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | A3 (stored) -> X+F | needed, size not determined | small | small | needed, size not determined | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | A4 (stored) -> RO | substantial | needed, size not determined | needed, size not determined | substantial | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | I -> N | negligible | lowers | negligible | negligible | lowers | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | N -> ROIN | small | small | small | small | small | replicated | small |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | O -> I | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | R -> O | lowers | lowers | negligible | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | RO -> R | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | ROIN -> X | small | negligible | negligible | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | X -> A3 (stored) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | none -> A2 (stored) | negligible | negligible | small | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | separation -> A4 (stored) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | A2 (stored) -> separation | negligible | lowers | undetermined | lowers | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | A3 (stored) -> X+F | undetermined | undetermined | undetermined | substantial | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | A4 (stored) -> RO | undetermined | substantial | undetermined | substantial | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | I -> N | undetermined | undetermined | needed, size not determined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | N -> ROIN | undetermined | undetermined | undetermined | substantial | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | O -> I | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | R -> O | undetermined | lowers | negligible | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | RO -> R | undetermined | negligible | undetermined | lowers | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | ROIN -> X | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | X -> A3 (stored) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | none -> A2 (stored) | small | negligible | lowers | negligible | lowers | contradicted | DEV-5 small vs DEV-7 lowers; replicated claim within a contradicted row: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | separation -> A4 (stored) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | A2 (stored) -> separation | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | A3 (stored) -> X+F | substantial | needed, size not determined | undetermined | undetermined | needed, size not determined | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | A4 (stored) -> RO | substantial | substantial | substantial | undetermined | substantial | replicated | substantial |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | A5 (stored) -> ROIN | needed, size not determined | substantial | substantial | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | I -> N | lowers | lowers | negligible | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | N -> A5 (stored) | substantial | needed, size not determined | needed, size not determined | undetermined | substantial | not replicated | replicated claim: ratio > 1 |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | O -> I | needed, size not determined | substantial | needed, size not determined | substantial | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | R -> O | undetermined | undetermined | negligible | lowers | lowers | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | RO -> R | lowers | lowers | lowers | needed, size not determined | negligible | contradicted | DEV-5 lowers vs DEV-8 needed, size not determined; replicated claim within a contradicted row: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | ROIN -> X | substantial | substantial | undetermined | substantial | substantial | replicated | substantial |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | X -> A3 (stored) | lowers | lowers | lowers | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | none -> A2 (stored) | small | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | separation -> A4 (stored) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | A2 (stored) -> separation | negligible | lowers | lowers | negligible | lowers | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | A3 (stored) -> X+F | needed, size not determined | negligible | undetermined | needed, size not determined | needed, size not determined | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | A4 (stored) -> RO | undetermined | needed, size not determined | needed, size not determined | undetermined | substantial | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | I -> N | negligible | lowers | negligible | lowers | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | N -> ROIN | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | O -> I | negligible | negligible | small | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | R -> O | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | RO -> R | negligible | lowers | negligible | negligible | lowers | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | ROIN -> X | undetermined | needed, size not determined | negligible | undetermined | needed, size not determined | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | X -> A3 (stored) | lowers | negligible | negligible | lowers | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | none -> A2 (stored) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | separation -> A4 (stored) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | A2 (stored) -> separation | undetermined | lowers | undetermined | undetermined | lowers | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | A3 (stored) -> X+F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | A4 (stored) -> RO | undetermined | undetermined | undetermined | undetermined | substantial | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | I -> N | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | N -> ROIN | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | O -> I | undetermined | undetermined | undetermined | undetermined | negligible | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | R -> O | undetermined | undetermined | undetermined | undetermined | substantial | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | RO -> R | negligible | lowers | undetermined | undetermined | lowers | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | ROIN -> X | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | X -> A3 (stored) | undetermined | undetermined | undetermined | undetermined | lowers | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | none -> A2 (stored) | undetermined | undetermined | undetermined | negligible | small | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | separation -> A4 (stored) | undetermined | negligible | undetermined | undetermined | negligible | not replicated |  |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | I -> N | negligible | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | N -> ROIN | small | small | small | small | small | replicated | small |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | O -> I | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | R -> O | lowers | negligible | lowers | lowers | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | RO -> R | negligible | lowers | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | ROIN -> X | small | negligible | negligible | lowers | negligible | contradicted | DEV-5 small vs DEV-8 lowers; replicated claim within a contradicted row: ratio <= 1.05 |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | X -> X+F | small | negligible | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | none -> separation | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | separation -> RO | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | I -> N | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | N -> ROIN | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | O -> I | undetermined | lowers | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | R -> O | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | RO -> R | lowers | lowers | lowers | lowers | undetermined | replicated | lowers |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | ROIN -> X | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | X -> X+F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | none -> separation | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | separation -> RO | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | I -> N | lowers | lowers | lowers | negligible | lowers | replicated | lowers |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | N -> ROIN | substantial | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | O -> I | lowers | lowers | lowers | lowers | undetermined | replicated | lowers |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | R -> O | substantial | undetermined | undetermined | undetermined | substantial | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | RO -> R | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | ROIN -> X | lowers | undetermined | undetermined | negligible | lowers | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | X -> X+F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | none -> separation | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | separation -> RO | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | I -> N | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | N -> ROIN | substantial | substantial | substantial | needed, size not determined | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | O -> I | lowers | lowers | lowers | negligible | lowers | replicated | lowers |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | R -> O | needed, size not determined | substantial | needed, size not determined | negligible | substantial | contradicted | DEV-6 substantial vs DEV-8 negligible; replicated claim within a contradicted row: ratio > 1 |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | RO -> R | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | ROIN -> X | negligible | negligible | negligible | negligible | undetermined | replicated | negligible |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | X -> X+F | needed, size not determined | undetermined | undetermined | undetermined | negligible | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | none -> separation | substantial | needed, size not determined | undetermined | needed, size not determined | substantial | not replicated | replicated claim: ratio > 1 |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | separation -> RO | negligible | undetermined | needed, size not determined | negligible | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | I -> N | undetermined | undetermined | undetermined | lowers | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | N -> ROIN | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | O -> I | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | R -> O | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | RO -> R | lowers | lowers | undetermined | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | ROIN -> X | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | X -> X+F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | none -> separation | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | separation -> RO | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | horizon | deployable | T_c | I -> N | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | horizon | deployable | T_c | N -> ROIN | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | deployable | T_c | O -> I | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | deployable | T_c | R -> O | negligible | small | small | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | horizon | deployable | T_c | RO -> R | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | horizon | deployable | T_c | ROIN -> X | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | horizon | deployable | T_c | X -> X+F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | deployable | T_c | lyapunov -> RO | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | deployable | T_c | none -> lyapunov | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | horizon | oracle | T_c | I -> N | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | horizon | oracle | T_c | N -> ROIN | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | oracle | T_c | O -> I | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | oracle | T_c | R -> O | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | horizon | oracle | T_c | RO -> R | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | horizon | oracle | T_c | ROIN -> X | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | horizon | oracle | T_c | X -> X+F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | oracle | T_c | lyapunov -> RO | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | oracle | T_c | none -> lyapunov | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=120 (4.00 LT) | A2 (stored) -> separation | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=120 (4.00 LT) | A3 (stored) -> X+F | negligible | small | small | small | small | replicated | small |
| rossler | allocation | deployable | H=120 (4.00 LT) | A4 (stored) -> RO | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| rossler | allocation | deployable | H=120 (4.00 LT) | I -> N | lowers | negligible | negligible | negligible | lowers | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=120 (4.00 LT) | N -> ROIN | negligible | small | small | small | small | replicated | small |
| rossler | allocation | deployable | H=120 (4.00 LT) | O -> I | small | negligible | negligible | small | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=120 (4.00 LT) | R -> O | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=120 (4.00 LT) | RO -> R | negligible | negligible | lowers | lowers | lowers | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=120 (4.00 LT) | ROIN -> X | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=120 (4.00 LT) | X -> A3 (stored) | negligible | negligible | negligible | lowers | negligible | replicated | negligible |
| rossler | allocation | deployable | H=120 (4.00 LT) | none -> A2 (stored) | negligible | lowers | negligible | negligible | lowers | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=120 (4.00 LT) | separation -> A4 (stored) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=15 (0.50 LT) | A2 (stored) -> separation | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=15 (0.50 LT) | A3 (stored) -> X+F | substantial | needed, size not determined | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | deployable | H=15 (0.50 LT) | A4 (stored) -> RO | substantial | substantial | undetermined | substantial | substantial | replicated | substantial |
| rossler | allocation | deployable | H=15 (0.50 LT) | I -> N | negligible | negligible | undetermined | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=15 (0.50 LT) | N -> ROIN | negligible | negligible | undetermined | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=15 (0.50 LT) | O -> I | negligible | negligible | undetermined | negligible | lowers | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=15 (0.50 LT) | R -> O | negligible | negligible | undetermined | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=15 (0.50 LT) | RO -> R | negligible | negligible | undetermined | negligible | lowers | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=15 (0.50 LT) | ROIN -> X | negligible | small | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=15 (0.50 LT) | X -> A3 (stored) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=15 (0.50 LT) | none -> A2 (stored) | negligible | small | undetermined | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=15 (0.50 LT) | separation -> A4 (stored) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | A2 (stored) -> separation | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=30 (1.00 LT) | A3 (stored) -> X+F | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| rossler | allocation | deployable | H=30 (1.00 LT) | A4 (stored) -> RO | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| rossler | allocation | deployable | H=30 (1.00 LT) | A5 (stored) -> ROIN | negligible | negligible | negligible | negligible | small | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | I -> N | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | N -> A5 (stored) | negligible | small | lowers | negligible | lowers | contradicted | DEV-6 small vs DEV-7 lowers; replicated claim within a contradicted row: ratio <= 1.05 |
| rossler | allocation | deployable | H=30 (1.00 LT) | O -> I | lowers | negligible | lowers | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=30 (1.00 LT) | R -> O | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | RO -> R | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | ROIN -> X | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | X -> A3 (stored) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=30 (1.00 LT) | none -> A2 (stored) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | separation -> A4 (stored) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | A2 (stored) -> separation | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | A3 (stored) -> X+F | small | needed, size not determined | negligible | needed, size not determined | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | deployable | H=60 (2.00 LT) | A4 (stored) -> RO | small | negligible | negligible | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=60 (2.00 LT) | I -> N | negligible | negligible | small | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | N -> ROIN | small | small | lowers | small | small | contradicted | DEV-5 small vs DEV-7 lowers; replicated claim within a contradicted row: ratio <= 1.05 |
| rossler | allocation | deployable | H=60 (2.00 LT) | O -> I | negligible | small | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | R -> O | negligible | negligible | lowers | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | RO -> R | negligible | lowers | needed, size not determined | negligible | lowers | contradicted | DEV-6 lowers vs DEV-7 needed, size not determined; replicated claim within a contradicted row: ratio <= 1.05 |
| rossler | allocation | deployable | H=60 (2.00 LT) | ROIN -> X | negligible | lowers | needed, size not determined | lowers | negligible | contradicted | DEV-6 lowers vs DEV-7 needed, size not determined; replicated claim within a contradicted row: ratio <= 1.05 |
| rossler | allocation | deployable | H=60 (2.00 LT) | X -> A3 (stored) | negligible | negligible | negligible | negligible | lowers | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | none -> A2 (stored) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | separation -> A4 (stored) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=8 (0.27 LT) | A2 (stored) -> separation | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=8 (0.27 LT) | A3 (stored) -> X+F | undetermined | needed, size not determined | needed, size not determined | substantial | substantial | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | deployable | H=8 (0.27 LT) | A4 (stored) -> RO | undetermined | substantial | undetermined | substantial | substantial | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | I -> N | negligible | negligible | undetermined | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=8 (0.27 LT) | N -> ROIN | undetermined | negligible | undetermined | negligible | negligible | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | O -> I | negligible | negligible | undetermined | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=8 (0.27 LT) | R -> O | negligible | negligible | undetermined | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=8 (0.27 LT) | RO -> R | lowers | lowers | undetermined | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=8 (0.27 LT) | ROIN -> X | small | negligible | undetermined | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=8 (0.27 LT) | X -> A3 (stored) | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | deployable | H=8 (0.27 LT) | none -> A2 (stored) | negligible | small | undetermined | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=8 (0.27 LT) | separation -> A4 (stored) | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=120 (4.00 LT) | I -> N | negligible | lowers | negligible | negligible | lowers | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=120 (4.00 LT) | N -> ROIN | small | small | small | small | small | replicated | small |
| rossler | allocation | oracle | H=120 (4.00 LT) | O -> I | small | negligible | negligible | small | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=120 (4.00 LT) | R -> O | lowers | negligible | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=120 (4.00 LT) | RO -> R | negligible | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=120 (4.00 LT) | ROIN -> X | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=120 (4.00 LT) | X -> X+F | small | small | small | small | small | replicated | small |
| rossler | allocation | oracle | H=120 (4.00 LT) | none -> separation | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=120 (4.00 LT) | separation -> RO | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| rossler | allocation | oracle | H=15 (0.50 LT) | I -> N | small | small | undetermined | small | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | oracle | H=15 (0.50 LT) | N -> ROIN | undetermined | substantial | substantial | needed, size not determined | substantial | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | oracle | H=15 (0.50 LT) | O -> I | negligible | negligible | undetermined | negligible | lowers | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=15 (0.50 LT) | R -> O | lowers | lowers | undetermined | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=15 (0.50 LT) | RO -> R | undetermined | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=15 (0.50 LT) | ROIN -> X | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=15 (0.50 LT) | X -> X+F | undetermined | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=15 (0.50 LT) | none -> separation | needed, size not determined | needed, size not determined | needed, size not determined | small | needed, size not determined | replicated | needed, size not determined |
| rossler | allocation | oracle | H=15 (0.50 LT) | separation -> RO | small | small | needed, size not determined | needed, size not determined | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | oracle | H=30 (1.00 LT) | I -> N | small | small | small | small | small | replicated | small |
| rossler | allocation | oracle | H=30 (1.00 LT) | N -> ROIN | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=30 (1.00 LT) | O -> I | negligible | negligible | negligible | negligible | small | replicated | negligible |
| rossler | allocation | oracle | H=30 (1.00 LT) | R -> O | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=30 (1.00 LT) | RO -> R | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=30 (1.00 LT) | ROIN -> X | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=30 (1.00 LT) | X -> X+F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=30 (1.00 LT) | none -> separation | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=30 (1.00 LT) | separation -> RO | small | small | small | small | small | replicated | small |
| rossler | allocation | oracle | H=60 (2.00 LT) | I -> N | negligible | negligible | small | small | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=60 (2.00 LT) | N -> ROIN | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=60 (2.00 LT) | O -> I | negligible | small | negligible | negligible | lowers | contradicted | DEV-6 small vs DEV-9 lowers; replicated claim within a contradicted row: ratio <= 1.05 |
| rossler | allocation | oracle | H=60 (2.00 LT) | R -> O | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=60 (2.00 LT) | RO -> R | lowers | lowers | negligible | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=60 (2.00 LT) | ROIN -> X | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=60 (2.00 LT) | X -> X+F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=60 (2.00 LT) | none -> separation | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=60 (2.00 LT) | separation -> RO | negligible | lowers | lowers | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=8 (0.27 LT) | I -> N | small | small | undetermined | small | small | replicated | small |
| rossler | allocation | oracle | H=8 (0.27 LT) | N -> ROIN | undetermined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| rossler | allocation | oracle | H=8 (0.27 LT) | O -> I | small | negligible | undetermined | negligible | lowers | contradicted | DEV-5 small vs DEV-9 lowers; replicated claim within a contradicted row: ratio <= 1.05 |
| rossler | allocation | oracle | H=8 (0.27 LT) | R -> O | lowers | lowers | undetermined | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=8 (0.27 LT) | RO -> R | undetermined | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=8 (0.27 LT) | ROIN -> X | lowers | lowers | undetermined | lowers | lowers | replicated | lowers |
| rossler | allocation | oracle | H=8 (0.27 LT) | X -> X+F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=8 (0.27 LT) | none -> separation | needed, size not determined | small | needed, size not determined | negligible | small | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | oracle | H=8 (0.27 LT) | separation -> RO | needed, size not determined | needed, size not determined | substantial | substantial | substantial | not replicated | replicated claim: ratio > 1 |
| rossler | horizon | deployable | T_c | I -> N | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | horizon | deployable | T_c | N -> ROIN | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | deployable | T_c | O -> I | substantial | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| rossler | horizon | deployable | T_c | R -> O | substantial | needed, size not determined | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | deployable | T_c | RO -> R | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | horizon | deployable | T_c | ROIN -> X | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | horizon | deployable | T_c | X -> X+F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | deployable | T_c | lyapunov -> RO | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | deployable | T_c | none -> lyapunov | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | horizon | oracle | T_c | I -> N | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | horizon | oracle | T_c | N -> ROIN | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | oracle | T_c | O -> I | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | oracle | T_c | R -> O | needed, size not determined | small | needed, size not determined | small | small | not replicated | replicated claim: ratio > 1 |
| rossler | horizon | oracle | T_c | RO -> R | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | horizon | oracle | T_c | ROIN -> X | negligible | undetermined | negligible | negligible | negligible | replicated | negligible |
| rossler | horizon | oracle | T_c | X -> X+F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | oracle | T_c | lyapunov -> RO | needed, size not determined | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | oracle | T_c | none -> lyapunov | negligible | lowers | lowers | lowers | lowers | replicated | lowers |

## D vs full

DEVELOPMENT: phase J replication (held-out development seeds), not a hypothesis test.

| system | decision | profile | horizon | item | DEV-5 | DEV-6 | DEV-7 | DEV-8 | DEV-9 | class | replicated reading or claims |
|---|---|---|---|---|---|---|---|---|---|---|---|
| chua | allocation | deployable | H=120 (4.00 LT) | A2 (stored): mse ratio vs F | small | small | small | small | small | replicated | small |
| chua | allocation | deployable | H=120 (4.00 LT) | A3 (stored): mse ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| chua | allocation | deployable | H=120 (4.00 LT) | A4 (stored): mse ratio vs F | needed, size not determined | needed, size not determined | substantial | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| chua | allocation | deployable | H=120 (4.00 LT) | I: mse ratio vs F | small | small | small | small | negligible | replicated | small |
| chua | allocation | deployable | H=120 (4.00 LT) | N: mse ratio vs F | small | small | small | small | small | replicated | small |
| chua | allocation | deployable | H=120 (4.00 LT) | O: mse ratio vs F | negligible | small | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=120 (4.00 LT) | R: mse ratio vs F | small | small | negligible | small | small | replicated | small |
| chua | allocation | deployable | H=120 (4.00 LT) | RO: mse ratio vs F | negligible | negligible | negligible | small | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | X+F: mse ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=120 (4.00 LT) | X: mse ratio vs F | small | small | small | small | small | replicated | small |
| chua | allocation | deployable | H=120 (4.00 LT) | none: mse ratio vs F | small | small | small | small | small | replicated | small |
| chua | allocation | deployable | H=120 (4.00 LT) | separation: mse ratio vs F | needed, size not determined | needed, size not determined | substantial | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| chua | allocation | deployable | H=15 (0.50 LT) | A2 (stored): mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | A3 (stored): mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | A4 (stored): mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | I: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | N: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | O: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | R: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | RO: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | X+F: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | X: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | none: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | separation: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | A2 (stored): mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | A3 (stored): mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | A4 (stored): mse ratio vs F | undetermined | undetermined | negligible | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | A5 (stored): mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | I: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | negligible | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | N: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | negligible | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | O: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | needed, size not determined | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | R: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | negligible | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | RO: mse ratio vs F | undetermined | undetermined | small | undetermined | negligible | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | X+F: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | negligible | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | X: mse ratio vs F | undetermined | undetermined | needed, size not determined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | none: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | separation: mse ratio vs F | undetermined | undetermined | negligible | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | A2 (stored): mse ratio vs F | needed, size not determined | undetermined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| chua | allocation | deployable | H=60 (2.00 LT) | A3 (stored): mse ratio vs F | negligible | negligible | undetermined | needed, size not determined | undetermined | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | A4 (stored): mse ratio vs F | undetermined | needed, size not determined | needed, size not determined | small | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| chua | allocation | deployable | H=60 (2.00 LT) | I: mse ratio vs F | needed, size not determined | negligible | needed, size not determined | needed, size not determined | undetermined | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | N: mse ratio vs F | negligible | small | needed, size not determined | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=60 (2.00 LT) | O: mse ratio vs F | small | negligible | needed, size not determined | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | deployable | H=60 (2.00 LT) | R: mse ratio vs F | small | small | needed, size not determined | small | undetermined | not replicated | replicated claim: ratio > 1 |
| chua | allocation | deployable | H=60 (2.00 LT) | RO: mse ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=60 (2.00 LT) | X+F: mse ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | deployable | H=60 (2.00 LT) | X: mse ratio vs F | negligible | negligible | negligible | small | negligible | replicated | negligible |
| chua | allocation | deployable | H=60 (2.00 LT) | none: mse ratio vs F | needed, size not determined | undetermined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| chua | allocation | deployable | H=60 (2.00 LT) | separation: mse ratio vs F | undetermined | needed, size not determined | needed, size not determined | small | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| chua | allocation | deployable | H=8 (0.27 LT) | A2 (stored): mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | A3 (stored): mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | A4 (stored): mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | I: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | N: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | O: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | R: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | RO: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | X+F: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | X: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | none: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | separation: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=120 (4.00 LT) | I: mse ratio vs F | small | small | small | small | small | replicated | small |
| chua | allocation | oracle | H=120 (4.00 LT) | N: mse ratio vs F | small | small | small | small | small | replicated | small |
| chua | allocation | oracle | H=120 (4.00 LT) | O: mse ratio vs F | small | small | small | small | small | replicated | small |
| chua | allocation | oracle | H=120 (4.00 LT) | R: mse ratio vs F | small | small | small | small | small | replicated | small |
| chua | allocation | oracle | H=120 (4.00 LT) | RO: mse ratio vs F | small | negligible | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| chua | allocation | oracle | H=120 (4.00 LT) | X+F: mse ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=120 (4.00 LT) | X: mse ratio vs F | small | small | small | small | small | replicated | small |
| chua | allocation | oracle | H=120 (4.00 LT) | none: mse ratio vs F | small | small | small | needed, size not determined | small | replicated | small |
| chua | allocation | oracle | H=120 (4.00 LT) | separation: mse ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| chua | allocation | oracle | H=15 (0.50 LT) | I: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | N: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | O: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | R: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | RO: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | X+F: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | X: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | none: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=15 (0.50 LT) | separation: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | I: mse ratio vs F | undetermined | undetermined | needed, size not determined | undetermined | needed, size not determined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | N: mse ratio vs F | undetermined | undetermined | needed, size not determined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | O: mse ratio vs F | undetermined | undetermined | needed, size not determined | undetermined | needed, size not determined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | R: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | RO: mse ratio vs F | undetermined | undetermined | negligible | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | X+F: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | negligible | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | X: mse ratio vs F | undetermined | undetermined | needed, size not determined | undetermined | needed, size not determined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | none: mse ratio vs F | undetermined | undetermined | needed, size not determined | undetermined | needed, size not determined | not replicated |  |
| chua | allocation | oracle | H=30 (1.00 LT) | separation: mse ratio vs F | undetermined | undetermined | negligible | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=60 (2.00 LT) | I: mse ratio vs F | substantial | needed, size not determined | needed, size not determined | substantial | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| chua | allocation | oracle | H=60 (2.00 LT) | N: mse ratio vs F | needed, size not determined | needed, size not determined | substantial | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| chua | allocation | oracle | H=60 (2.00 LT) | O: mse ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| chua | allocation | oracle | H=60 (2.00 LT) | R: mse ratio vs F | small | needed, size not determined | small | small | small | replicated | small |
| chua | allocation | oracle | H=60 (2.00 LT) | RO: mse ratio vs F | negligible | negligible | negligible | small | negligible | replicated | negligible |
| chua | allocation | oracle | H=60 (2.00 LT) | X+F: mse ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| chua | allocation | oracle | H=60 (2.00 LT) | X: mse ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| chua | allocation | oracle | H=60 (2.00 LT) | none: mse ratio vs F | substantial | substantial | substantial | substantial | needed, size not determined | replicated | substantial |
| chua | allocation | oracle | H=60 (2.00 LT) | separation: mse ratio vs F | negligible | undetermined | needed, size not determined | negligible | negligible | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | I: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | N: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | O: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | R: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | RO: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | X+F: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | X: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | none: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | allocation | oracle | H=8 (0.27 LT) | separation: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| chua | horizon | deployable | T_c | I: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | deployable | T_c | N: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | deployable | T_c | O: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | deployable | T_c | R: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | deployable | T_c | RO: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | deployable | T_c | X+F: pinball ratio vs F | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | horizon | deployable | T_c | X: pinball ratio vs F | substantial | needed, size not determined | substantial | substantial | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| chua | horizon | deployable | T_c | lyapunov: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | deployable | T_c | none: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | oracle | T_c | I: pinball ratio vs F | substantial | substantial | substantial | substantial | needed, size not determined | replicated | substantial |
| chua | horizon | oracle | T_c | N: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | oracle | T_c | O: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | oracle | T_c | R: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | oracle | T_c | RO: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | oracle | T_c | X+F: pinball ratio vs F | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| chua | horizon | oracle | T_c | X: pinball ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | substantial | needed, size not determined | replicated | needed, size not determined |
| chua | horizon | oracle | T_c | lyapunov: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| chua | horizon | oracle | T_c | none: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | A2 (stored): mse ratio vs F | small | small | small | small | negligible | replicated | small |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | A3 (stored): mse ratio vs F | needed, size not determined | small | negligible | needed, size not determined | small | not replicated | replicated claim: ratio > 1 |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | A4 (stored): mse ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | I: mse ratio vs F | small | negligible | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | N: mse ratio vs F | small | small | small | small | small | replicated | small |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | O: mse ratio vs F | small | small | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | R: mse ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | RO: mse ratio vs F | negligible | small | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | X+F: mse ratio vs F | lowers | negligible | negligible | negligible | lowers | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | X: mse ratio vs F | negligible | negligible | negligible | negligible | lowers | replicated | negligible |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | none: mse ratio vs F | small | small | small | small | negligible | replicated | small |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | separation: mse ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | A2 (stored): mse ratio vs F | undetermined | undetermined | undetermined | substantial | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | A3 (stored): mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | A4 (stored): mse ratio vs F | undetermined | undetermined | undetermined | substantial | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | I: mse ratio vs F | undetermined | undetermined | undetermined | substantial | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | N: mse ratio vs F | undetermined | undetermined | undetermined | substantial | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | O: mse ratio vs F | undetermined | undetermined | undetermined | substantial | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | R: mse ratio vs F | undetermined | undetermined | undetermined | substantial | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | RO: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | X+F: mse ratio vs F | undetermined | undetermined | undetermined | lowers | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | X: mse ratio vs F | undetermined | undetermined | undetermined | lowers | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | none: mse ratio vs F | undetermined | undetermined | undetermined | substantial | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | separation: mse ratio vs F | undetermined | undetermined | undetermined | substantial | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | A2 (stored): mse ratio vs F | substantial | substantial | substantial | undetermined | substantial | replicated | substantial |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | A3 (stored): mse ratio vs F | undetermined | undetermined | undetermined | undetermined | negligible | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | A4 (stored): mse ratio vs F | substantial | substantial | substantial | undetermined | substantial | replicated | substantial |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | A5 (stored): mse ratio vs F | undetermined | needed, size not determined | needed, size not determined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | I: mse ratio vs F | needed, size not determined | needed, size not determined | substantial | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | N: mse ratio vs F | substantial | substantial | substantial | undetermined | substantial | replicated | substantial |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | O: mse ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | R: mse ratio vs F | substantial | substantial | substantial | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | RO: mse ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | substantial | undetermined | not replicated | replicated claim: ratio > 1 |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | X+F: mse ratio vs F | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | X: mse ratio vs F | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | none: mse ratio vs F | substantial | substantial | substantial | undetermined | substantial | replicated | substantial |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | separation: mse ratio vs F | substantial | substantial | substantial | undetermined | substantial | replicated | substantial |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | A2 (stored): mse ratio vs F | needed, size not determined | undetermined | needed, size not determined | undetermined | needed, size not determined | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | A3 (stored): mse ratio vs F | undetermined | lowers | negligible | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | A4 (stored): mse ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | undetermined | substantial | not replicated | replicated claim: ratio > 1 |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | I: mse ratio vs F | undetermined | negligible | needed, size not determined | undetermined | needed, size not determined | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | N: mse ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | undetermined | needed, size not determined | replicated | needed, size not determined |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | O: mse ratio vs F | needed, size not determined | undetermined | needed, size not determined | undetermined | needed, size not determined | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | R: mse ratio vs F | needed, size not determined | negligible | needed, size not determined | undetermined | needed, size not determined | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | RO: mse ratio vs F | needed, size not determined | negligible | needed, size not determined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | X+F: mse ratio vs F | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | X: mse ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | none: mse ratio vs F | needed, size not determined | undetermined | needed, size not determined | undetermined | needed, size not determined | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | separation: mse ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | undetermined | substantial | not replicated | replicated claim: ratio > 1 |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | A2 (stored): mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | A3 (stored): mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | A4 (stored): mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | I: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | N: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | O: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | R: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | RO: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | X+F: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | X: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | none: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | separation: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | I: mse ratio vs F | small | small | small | small | negligible | replicated | small |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | N: mse ratio vs F | small | small | small | small | small | replicated | small |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | O: mse ratio vs F | small | small | small | small | small | replicated | small |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | R: mse ratio vs F | negligible | small | small | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | RO: mse ratio vs F | negligible | small | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | X+F: mse ratio vs F | lowers | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | X: mse ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | none: mse ratio vs F | small | small | small | small | negligible | replicated | small |
| lorenz63 | allocation | oracle | H=120 (4.00 LT) | separation: mse ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | I: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | N: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | O: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | R: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | RO: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | X+F: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | X: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | none: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=15 (0.50 LT) | separation: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | I: mse ratio vs F | substantial | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | N: mse ratio vs F | substantial | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | O: mse ratio vs F | needed, size not determined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | R: mse ratio vs F | substantial | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | RO: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | X+F: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | X: mse ratio vs F | needed, size not determined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | none: mse ratio vs F | substantial | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=30 (1.00 LT) | separation: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | I: mse ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | N: mse ratio vs F | substantial | substantial | needed, size not determined | needed, size not determined | undetermined | not replicated | replicated claim: ratio > 1 |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | O: mse ratio vs F | undetermined | undetermined | undetermined | needed, size not determined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | R: mse ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | RO: mse ratio vs F | negligible | negligible | negligible | undetermined | negligible | replicated | negligible |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | X+F: mse ratio vs F | negligible | negligible | negligible | negligible | lowers | replicated | negligible |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | X: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | negligible | not replicated |  |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | none: mse ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | undetermined | replicated | needed, size not determined |
| lorenz63 | allocation | oracle | H=60 (2.00 LT) | separation: mse ratio vs F | undetermined | undetermined | needed, size not determined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | I: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | N: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | O: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | R: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | RO: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | X+F: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | X: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | none: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | allocation | oracle | H=8 (0.27 LT) | separation: mse ratio vs F | undetermined | undetermined | undetermined | undetermined | undetermined | not replicated |  |
| lorenz63 | horizon | deployable | T_c | I: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | deployable | T_c | N: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | deployable | T_c | O: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | deployable | T_c | R: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | deployable | T_c | RO: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | deployable | T_c | X+F: pinball ratio vs F | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | horizon | deployable | T_c | X: pinball ratio vs F | substantial | substantial | substantial | needed, size not determined | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| lorenz63 | horizon | deployable | T_c | lyapunov: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | deployable | T_c | none: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | oracle | T_c | I: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | oracle | T_c | N: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | oracle | T_c | O: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | oracle | T_c | R: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | oracle | T_c | RO: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | oracle | T_c | X+F: pinball ratio vs F | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| lorenz63 | horizon | oracle | T_c | X: pinball ratio vs F | substantial | needed, size not determined | substantial | needed, size not determined | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| lorenz63 | horizon | oracle | T_c | lyapunov: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| lorenz63 | horizon | oracle | T_c | none: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | deployable | H=120 (4.00 LT) | A2 (stored): mse ratio vs F | negligible | small | small | small | small | replicated | small |
| rossler | allocation | deployable | H=120 (4.00 LT) | A3 (stored): mse ratio vs F | negligible | small | small | needed, size not determined | small | not replicated | replicated claim: ratio <= 1.05; ratio > 1 |
| rossler | allocation | deployable | H=120 (4.00 LT) | A4 (stored): mse ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| rossler | allocation | deployable | H=120 (4.00 LT) | I: mse ratio vs F | negligible | small | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=120 (4.00 LT) | N: mse ratio vs F | negligible | small | small | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=120 (4.00 LT) | O: mse ratio vs F | negligible | small | small | small | small | replicated | small |
| rossler | allocation | deployable | H=120 (4.00 LT) | R: mse ratio vs F | negligible | small | small | small | small | replicated | small |
| rossler | allocation | deployable | H=120 (4.00 LT) | RO: mse ratio vs F | negligible | negligible | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=120 (4.00 LT) | X+F: mse ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=120 (4.00 LT) | X: mse ratio vs F | negligible | small | small | small | small | replicated | small |
| rossler | allocation | deployable | H=120 (4.00 LT) | none: mse ratio vs F | negligible | small | small | small | small | replicated | small |
| rossler | allocation | deployable | H=120 (4.00 LT) | separation: mse ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| rossler | allocation | deployable | H=15 (0.50 LT) | A2 (stored): mse ratio vs F | negligible | negligible | undetermined | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=15 (0.50 LT) | A3 (stored): mse ratio vs F | needed, size not determined | needed, size not determined | undetermined | substantial | substantial | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | deployable | H=15 (0.50 LT) | A4 (stored): mse ratio vs F | substantial | needed, size not determined | undetermined | substantial | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | deployable | H=15 (0.50 LT) | I: mse ratio vs F | negligible | negligible | undetermined | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=15 (0.50 LT) | N: mse ratio vs F | negligible | negligible | undetermined | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=15 (0.50 LT) | O: mse ratio vs F | negligible | negligible | undetermined | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=15 (0.50 LT) | R: mse ratio vs F | negligible | negligible | undetermined | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=15 (0.50 LT) | RO: mse ratio vs F | negligible | negligible | undetermined | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=15 (0.50 LT) | X+F: mse ratio vs F | lowers | lowers | undetermined | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=15 (0.50 LT) | X: mse ratio vs F | negligible | negligible | undetermined | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=15 (0.50 LT) | none: mse ratio vs F | negligible | negligible | undetermined | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=15 (0.50 LT) | separation: mse ratio vs F | substantial | needed, size not determined | undetermined | substantial | needed, size not determined | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | deployable | H=30 (1.00 LT) | A2 (stored): mse ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | A3 (stored): mse ratio vs F | needed, size not determined | undetermined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| rossler | allocation | deployable | H=30 (1.00 LT) | A4 (stored): mse ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| rossler | allocation | deployable | H=30 (1.00 LT) | A5 (stored): mse ratio vs F | negligible | negligible | negligible | negligible | small | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | I: mse ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | N: mse ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | O: mse ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | R: mse ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | RO: mse ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | X+F: mse ratio vs F | negligible | lowers | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | X: mse ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | none: mse ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=30 (1.00 LT) | separation: mse ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| rossler | allocation | deployable | H=60 (2.00 LT) | A2 (stored): mse ratio vs F | negligible | small | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=60 (2.00 LT) | A3 (stored): mse ratio vs F | negligible | undetermined | negligible | undetermined | needed, size not determined | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | A4 (stored): mse ratio vs F | small | small | lowers | negligible | negligible | contradicted | DEV-5 small vs DEV-7 lowers; replicated claim within a contradicted row: ratio <= 1.05 |
| rossler | allocation | deployable | H=60 (2.00 LT) | I: mse ratio vs F | negligible | negligible | negligible | small | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | N: mse ratio vs F | small | small | lowers | negligible | negligible | contradicted | DEV-5 small vs DEV-7 lowers; replicated claim within a contradicted row: ratio <= 1.05 |
| rossler | allocation | deployable | H=60 (2.00 LT) | O: mse ratio vs F | negligible | small | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | R: mse ratio vs F | negligible | small | lowers | small | negligible | contradicted | DEV-6 small vs DEV-7 lowers; replicated claim within a contradicted row: ratio <= 1.05 |
| rossler | allocation | deployable | H=60 (2.00 LT) | RO: mse ratio vs F | negligible | small | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | X+F: mse ratio vs F | negligible | negligible | negligible | negligible | lowers | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | X: mse ratio vs F | negligible | small | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | deployable | H=60 (2.00 LT) | none: mse ratio vs F | negligible | small | negligible | small | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | deployable | H=60 (2.00 LT) | separation: mse ratio vs F | small | small | lowers | negligible | negligible | contradicted | DEV-5 small vs DEV-7 lowers; replicated claim within a contradicted row: ratio <= 1.05 |
| rossler | allocation | deployable | H=8 (0.27 LT) | A2 (stored): mse ratio vs F | undetermined | negligible | undetermined | negligible | negligible | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | A3 (stored): mse ratio vs F | undetermined | small | undetermined | substantial | substantial | contradicted | DEV-6 small vs DEV-8 substantial |
| rossler | allocation | deployable | H=8 (0.27 LT) | A4 (stored): mse ratio vs F | undetermined | substantial | undetermined | substantial | substantial | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | I: mse ratio vs F | undetermined | negligible | undetermined | negligible | negligible | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | N: mse ratio vs F | undetermined | negligible | undetermined | negligible | negligible | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | O: mse ratio vs F | undetermined | negligible | undetermined | negligible | negligible | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | R: mse ratio vs F | undetermined | negligible | undetermined | negligible | negligible | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | RO: mse ratio vs F | undetermined | negligible | undetermined | negligible | negligible | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | X+F: mse ratio vs F | undetermined | lowers | undetermined | lowers | lowers | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | X: mse ratio vs F | undetermined | negligible | undetermined | negligible | negligible | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | none: mse ratio vs F | undetermined | negligible | undetermined | negligible | negligible | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | separation: mse ratio vs F | undetermined | substantial | undetermined | substantial | substantial | not replicated |  |
| rossler | allocation | oracle | H=120 (4.00 LT) | I: mse ratio vs F | small | small | small | small | small | replicated | small |
| rossler | allocation | oracle | H=120 (4.00 LT) | N: mse ratio vs F | small | small | small | small | small | replicated | small |
| rossler | allocation | oracle | H=120 (4.00 LT) | O: mse ratio vs F | small | small | small | small | small | replicated | small |
| rossler | allocation | oracle | H=120 (4.00 LT) | R: mse ratio vs F | small | small | small | small | small | replicated | small |
| rossler | allocation | oracle | H=120 (4.00 LT) | RO: mse ratio vs F | small | negligible | small | negligible | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=120 (4.00 LT) | X+F: mse ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=120 (4.00 LT) | X: mse ratio vs F | small | small | small | small | small | replicated | small |
| rossler | allocation | oracle | H=120 (4.00 LT) | none: mse ratio vs F | small | small | small | small | small | replicated | small |
| rossler | allocation | oracle | H=120 (4.00 LT) | separation: mse ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| rossler | allocation | oracle | H=15 (0.50 LT) | I: mse ratio vs F | undetermined | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=15 (0.50 LT) | N: mse ratio vs F | undetermined | substantial | substantial | needed, size not determined | substantial | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | oracle | H=15 (0.50 LT) | O: mse ratio vs F | undetermined | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=15 (0.50 LT) | R: mse ratio vs F | undetermined | small | needed, size not determined | small | small | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | oracle | H=15 (0.50 LT) | RO: mse ratio vs F | undetermined | small | small | small | small | replicated | small |
| rossler | allocation | oracle | H=15 (0.50 LT) | X+F: mse ratio vs F | undetermined | lowers | lowers | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=15 (0.50 LT) | X: mse ratio vs F | undetermined | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=15 (0.50 LT) | none: mse ratio vs F | undetermined | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=15 (0.50 LT) | separation: mse ratio vs F | undetermined | needed, size not determined | needed, size not determined | substantial | substantial | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | oracle | H=30 (1.00 LT) | I: mse ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=30 (1.00 LT) | N: mse ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=30 (1.00 LT) | O: mse ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=30 (1.00 LT) | R: mse ratio vs F | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| rossler | allocation | oracle | H=30 (1.00 LT) | RO: mse ratio vs F | negligible | small | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=30 (1.00 LT) | X+F: mse ratio vs F | negligible | lowers | negligible | negligible | lowers | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=30 (1.00 LT) | X: mse ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=30 (1.00 LT) | none: mse ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=30 (1.00 LT) | separation: mse ratio vs F | small | small | small | small | small | replicated | small |
| rossler | allocation | oracle | H=60 (2.00 LT) | I: mse ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=60 (2.00 LT) | N: mse ratio vs F | substantial | substantial | needed, size not determined | needed, size not determined | substantial | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | oracle | H=60 (2.00 LT) | O: mse ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=60 (2.00 LT) | R: mse ratio vs F | negligible | small | negligible | small | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=60 (2.00 LT) | RO: mse ratio vs F | negligible | small | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=60 (2.00 LT) | X+F: mse ratio vs F | negligible | negligible | negligible | negligible | negligible | replicated | negligible |
| rossler | allocation | oracle | H=60 (2.00 LT) | X: mse ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=60 (2.00 LT) | none: mse ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=60 (2.00 LT) | separation: mse ratio vs F | negligible | lowers | lowers | negligible | negligible | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=8 (0.27 LT) | I: mse ratio vs F | undetermined | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=8 (0.27 LT) | N: mse ratio vs F | undetermined | needed, size not determined | needed, size not determined | needed, size not determined | needed, size not determined | replicated | needed, size not determined |
| rossler | allocation | oracle | H=8 (0.27 LT) | O: mse ratio vs F | undetermined | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=8 (0.27 LT) | R: mse ratio vs F | undetermined | small | needed, size not determined | small | small | not replicated | replicated claim: ratio > 1 |
| rossler | allocation | oracle | H=8 (0.27 LT) | RO: mse ratio vs F | undetermined | small | negligible | small | small | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=8 (0.27 LT) | X+F: mse ratio vs F | undetermined | lowers | negligible | negligible | lowers | not replicated | replicated claim: ratio <= 1.05 |
| rossler | allocation | oracle | H=8 (0.27 LT) | X: mse ratio vs F | undetermined | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=8 (0.27 LT) | none: mse ratio vs F | undetermined | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | allocation | oracle | H=8 (0.27 LT) | separation: mse ratio vs F | undetermined | needed, size not determined | needed, size not determined | substantial | substantial | not replicated | replicated claim: ratio > 1 |
| rossler | horizon | deployable | T_c | I: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | deployable | T_c | N: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | deployable | T_c | O: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | deployable | T_c | R: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | deployable | T_c | RO: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | deployable | T_c | X+F: pinball ratio vs F | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | horizon | deployable | T_c | X: pinball ratio vs F | needed, size not determined | undetermined | undetermined | needed, size not determined | needed, size not determined | not replicated |  |
| rossler | horizon | deployable | T_c | lyapunov: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | deployable | T_c | none: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | oracle | T_c | I: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | oracle | T_c | N: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | oracle | T_c | O: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | oracle | T_c | R: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | oracle | T_c | RO: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | oracle | T_c | X+F: pinball ratio vs F | lowers | lowers | lowers | lowers | lowers | replicated | lowers |
| rossler | horizon | oracle | T_c | X: pinball ratio vs F | negligible | negligible | negligible | undetermined | undetermined | not replicated |  |
| rossler | horizon | oracle | T_c | lyapunov: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |
| rossler | horizon | oracle | T_c | none: pinball ratio vs F | substantial | substantial | substantial | substantial | substantial | replicated | substantial |

## E-H2a

DEVELOPMENT: phase J replication (held-out development seeds), not a hypothesis test.

| system | decision | profile | horizon | item | DEV-5 | DEV-6 | DEV-7 | DEV-8 | DEV-9 | class | replicated reading or claims |
|---|---|---|---|---|---|---|---|---|---|---|---|
| chua | mechanism | oracle | all | reading | not determined | not determined | not consistent | not consistent | not consistent | not replicated |  |
| lorenz63 | mechanism | oracle | all | reading | not determined | not determined | not determined | not determined | not consistent | not replicated |  |
| rossler | mechanism | oracle | all | reading | not consistent | not consistent | not consistent | not consistent | not consistent | replicated | not consistent |

## E-H2e

DEVELOPMENT: phase J replication (held-out development seeds), not a hypothesis test.

| system | decision | profile | horizon | item | DEV-5 | DEV-6 | DEV-7 | DEV-8 | DEV-9 | class | replicated reading or claims |
|---|---|---|---|---|---|---|---|---|---|---|---|
| chua | mechanism | oracle | rho 0.01 | final | not determined | not determined (depends on the zero-variance convention) | not determined | not consistent | not determined (depends on the zero-variance convention) | not replicated |  |
| chua | mechanism | oracle | rho 0.01 | part all | not determined | not consistent | not determined | not consistent | not consistent | not replicated |  |
| chua | mechanism | oracle | rho 0.01 | part both_defined | not determined | not determined | not determined | not consistent | not determined | not replicated |  |
| chua | mechanism | oracle | rho 0.02 | final | not determined | not determined | not determined (depends on the zero-variance convention) | not determined | not consistent | not replicated |  |
| chua | mechanism | oracle | rho 0.02 | part all | not determined | not determined | consistent | not determined | not consistent | contradicted | DEV-7 consistent vs DEV-9 not consistent |
| chua | mechanism | oracle | rho 0.02 | part both_defined | not determined | not determined | not determined | not determined | not consistent | not replicated |  |
| lorenz63 | mechanism | oracle | rho 0.01 | final | not determined (depends on the zero-variance convention) | not consistent | not determined (depends on the zero-variance convention) | not determined (depends on the zero-variance convention) | not determined | not replicated |  |
| lorenz63 | mechanism | oracle | rho 0.01 | part all | not consistent | not consistent | not consistent | not consistent | not determined | replicated | not consistent |
| lorenz63 | mechanism | oracle | rho 0.01 | part both_defined | not determined | not consistent | not determined | not determined | not determined | not replicated |  |
| lorenz63 | mechanism | oracle | rho 0.02 | final | not consistent | not consistent | not consistent | not determined | not determined (depends on the zero-variance convention) | not replicated |  |
| lorenz63 | mechanism | oracle | rho 0.02 | part all | not consistent | not consistent | not consistent | not determined | not determined | not replicated |  |
| lorenz63 | mechanism | oracle | rho 0.02 | part both_defined | not consistent | not consistent | not consistent | not determined | consistent | contradicted | DEV-5 not consistent vs DEV-9 consistent |
| rossler | mechanism | oracle | rho 0.01 | final | not determined | not determined (depends on the zero-variance convention) | not determined (depends on the zero-variance convention) | not determined (depends on the zero-variance convention) | not determined (depends on the zero-variance convention) | not replicated |  |
| rossler | mechanism | oracle | rho 0.01 | part all | not determined | not consistent | not consistent | not consistent | not consistent | replicated | not consistent |
| rossler | mechanism | oracle | rho 0.01 | part both_defined | not determined | not determined | not determined | not determined | not determined | not replicated |  |
| rossler | mechanism | oracle | rho 0.02 | final | not determined | not consistent | not consistent | not consistent | not determined (depends on the zero-variance convention) | not replicated |  |
| rossler | mechanism | oracle | rho 0.02 | part all | not determined | not consistent | not consistent | not consistent | not determined | not replicated |  |
| rossler | mechanism | oracle | rho 0.02 | part both_defined | not determined | not consistent | not consistent | not consistent | not consistent | replicated | not consistent |

## E-H3c

DEVELOPMENT: phase J replication (held-out development seeds), not a hypothesis test.

| system | decision | profile | horizon | item | DEV-5 | DEV-6 | DEV-7 | DEV-8 | DEV-9 | class | replicated reading or claims |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all | mechanism | deployable | H_ref | lorenz63_part | not consistent | not consistent | not consistent | not consistent | not consistent | replicated (point readings) | not consistent |
| all | mechanism | deployable | H_ref | overall | not consistent | not consistent | not consistent | not consistent | not consistent | replicated (point readings) | not consistent |
| all | mechanism | deployable | H_ref | rossler_part | not consistent | not consistent | not consistent | not consistent | not consistent | replicated (point readings) | not consistent |

## check (f2)

DEVELOPMENT: phase J replication (held-out development seeds), not a hypothesis test.

| system | decision | profile | horizon | item | DEV-5 | DEV-6 | DEV-7 | DEV-8 | DEV-9 | class | replicated reading or claims |
|---|---|---|---|---|---|---|---|---|---|---|---|
| chua | allocation | deployable | H=120 (4.00 LT) | A2 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | A3 (stored): dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | A4 (stored): dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | I: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | IN: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | N: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | O: dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | OI: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | OIN: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | ON: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | R: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | RI: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | RIN: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | RN: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | RO: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | ROI: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | ROIN: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | RON: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | X+F: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | X: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | none: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | separation: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | swap-I: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | swap-N: dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | swap-O: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=120 (4.00 LT) | swap-R: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | A2 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | A3 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | A4 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | I: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | IN: dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | N: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | O: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | OI: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | OIN: dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| chua | allocation | deployable | H=15 (0.50 LT) | ON: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | R: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | RI: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | RIN: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | RN: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | RO: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | ROI: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | ROIN: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| chua | allocation | deployable | H=15 (0.50 LT) | RON: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | X+F: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | X: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | none: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | separation: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | swap-I: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | swap-N: dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | swap-O: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=15 (0.50 LT) | swap-R: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | A2 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | A3 (stored): dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | A4 (stored): dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| chua | allocation | deployable | H=30 (1.00 LT) | A5 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | I: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| chua | allocation | deployable | H=30 (1.00 LT) | IN: dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | N: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | O: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | OI: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | OIN: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | ON: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | R: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| chua | allocation | deployable | H=30 (1.00 LT) | RI: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | RIN: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | RN: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | RO: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| chua | allocation | deployable | H=30 (1.00 LT) | ROI: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | ROIN: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | RON: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | X+F: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | X: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | none: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | separation: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| chua | allocation | deployable | H=30 (1.00 LT) | swap-I: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | swap-N: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | swap-O: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=30 (1.00 LT) | swap-R: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | A2 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | A3 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | A4 (stored): dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | I: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | IN: dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | N: dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | O: dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | OI: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | OIN: dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | ON: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | R: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | RI: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | replicated | dependence bias detectable (interval excludes 0) |
| chua | allocation | deployable | H=60 (2.00 LT) | RIN: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | RN: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | RO: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | ROI: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | ROIN: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | RON: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | X+F: dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | X: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | none: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | separation: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | swap-I: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | swap-N: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | swap-O: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=60 (2.00 LT) | swap-R: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| chua | allocation | deployable | H=8 (0.27 LT) | A2 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | A3 (stored): dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | A4 (stored): dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | I: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | IN: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | N: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| chua | allocation | deployable | H=8 (0.27 LT) | O: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | OI: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | OIN: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | ON: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | R: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| chua | allocation | deployable | H=8 (0.27 LT) | RI: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | RIN: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | RN: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| chua | allocation | deployable | H=8 (0.27 LT) | RO: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| chua | allocation | deployable | H=8 (0.27 LT) | ROI: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | ROIN: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| chua | allocation | deployable | H=8 (0.27 LT) | RON: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| chua | allocation | deployable | H=8 (0.27 LT) | X+F: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| chua | allocation | deployable | H=8 (0.27 LT) | X: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | none: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | separation: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | swap-I: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | swap-N: dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | swap-O: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| chua | allocation | deployable | H=8 (0.27 LT) | swap-R: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | A2 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | A3 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | A4 (stored): dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | I: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | IN: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | N: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | O: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | OI: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | OIN: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | ON: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | R: dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | RI: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | RIN: dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | RN: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | RO: dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | ROI: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | ROIN: dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | contradicted | DEV-7 dependence bias detectable (interval excludes 0) vs DEV-9 dependence bias detectable (interval excludes 0) |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | RON: dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | X+F: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | X: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | none: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | separation: dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | swap-I: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | swap-N: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | swap-O: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=120 (4.00 LT) | swap-R: dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | A2 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | A3 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | A4 (stored): dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | I: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | IN: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | N: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | O: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | OI: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | OIN: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | ON: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | R: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | RI: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | RIN: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | RN: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | RO: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | ROI: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | ROIN: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | RON: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | X+F: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | X: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | none: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | separation: dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | swap-I: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | swap-N: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | swap-O: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=15 (0.50 LT) | swap-R: dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | A2 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | A3 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | A4 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | A5 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | I: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | IN: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | N: dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | O: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | OI: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | OIN: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | ON: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | R: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | RI: dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | RIN: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | RN: dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | RO: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | ROI: dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | ROIN: dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | RON: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | X+F: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | X: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | none: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | separation: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | swap-I: dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | contradicted | DEV-7 dependence bias detectable (interval excludes 0) vs DEV-9 dependence bias detectable (interval excludes 0) |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | swap-N: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | swap-O: dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=30 (1.00 LT) | swap-R: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | A2 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | A3 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | A4 (stored): dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | replicated | dependence bias detectable (interval excludes 0) |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | I: dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | IN: dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | N: dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | O: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | OI: dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | OIN: dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | contradicted | DEV-5 dependence bias detectable (interval excludes 0) vs DEV-7 dependence bias detectable (interval excludes 0) |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | ON: dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | R: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | RI: dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | RIN: dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | RN: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | RO: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | ROI: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | ROIN: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | RON: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | X+F: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | X: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | none: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | separation: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | replicated | dependence bias detectable (interval excludes 0) |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | swap-I: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | swap-N: dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | swap-O: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=60 (2.00 LT) | swap-R: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | A2 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | A3 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | A4 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | I: dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | IN: dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | N: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | O: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | OI: dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | OIN: dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | ON: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | R: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | RI: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | RIN: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | RN: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | RO: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | ROI: dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | ROIN: dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | RON: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | X+F: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | X: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | none: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | separation: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | swap-I: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | swap-N: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | swap-O: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| lorenz63 | allocation | deployable | H=8 (0.27 LT) | swap-R: dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | A2 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | A3 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | A4 (stored): dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | I: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | IN: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | N: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | O: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | OI: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | OIN: dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | ON: dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | R: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | RI: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | RIN: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | RN: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | RO: dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | ROI: dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | contradicted | DEV-5 dependence bias detectable (interval excludes 0) vs DEV-8 dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=120 (4.00 LT) | ROIN: dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | RON: dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | X+F: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | X: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | none: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | separation: dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | swap-I: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | swap-N: dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | swap-O: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=120 (4.00 LT) | swap-R: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=15 (0.50 LT) | A2 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=15 (0.50 LT) | A3 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=15 (0.50 LT) | A4 (stored): dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=15 (0.50 LT) | I: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| rossler | allocation | deployable | H=15 (0.50 LT) | IN: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=15 (0.50 LT) | N: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=15 (0.50 LT) | O: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=15 (0.50 LT) | OI: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=15 (0.50 LT) | OIN: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=15 (0.50 LT) | ON: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=15 (0.50 LT) | R: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=15 (0.50 LT) | RI: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=15 (0.50 LT) | RIN: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=15 (0.50 LT) | RN: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=15 (0.50 LT) | RO: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=15 (0.50 LT) | ROI: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=15 (0.50 LT) | ROIN: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=15 (0.50 LT) | RON: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=15 (0.50 LT) | X+F: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=15 (0.50 LT) | X: dependence bias | no detectable dependence bias | no detectable dependence bias | realized-noise outlier, no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=15 (0.50 LT) | none: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=15 (0.50 LT) | separation: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=15 (0.50 LT) | swap-I: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=15 (0.50 LT) | swap-N: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=15 (0.50 LT) | swap-O: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=15 (0.50 LT) | swap-R: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=30 (1.00 LT) | A2 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=30 (1.00 LT) | A3 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=30 (1.00 LT) | A4 (stored): dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=30 (1.00 LT) | A5 (stored): dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=30 (1.00 LT) | I: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=30 (1.00 LT) | IN: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=30 (1.00 LT) | N: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=30 (1.00 LT) | O: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=30 (1.00 LT) | OI: dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | not replicated |  |
| rossler | allocation | deployable | H=30 (1.00 LT) | OIN: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=30 (1.00 LT) | ON: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=30 (1.00 LT) | R: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=30 (1.00 LT) | RI: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=30 (1.00 LT) | RIN: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=30 (1.00 LT) | RN: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=30 (1.00 LT) | RO: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=30 (1.00 LT) | ROI: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=30 (1.00 LT) | ROIN: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=30 (1.00 LT) | RON: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=30 (1.00 LT) | X+F: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=30 (1.00 LT) | X: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=30 (1.00 LT) | none: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=30 (1.00 LT) | separation: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=30 (1.00 LT) | swap-I: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=30 (1.00 LT) | swap-N: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=30 (1.00 LT) | swap-O: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=30 (1.00 LT) | swap-R: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=60 (2.00 LT) | A2 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | A3 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | A4 (stored): dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=60 (2.00 LT) | I: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | IN: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=60 (2.00 LT) | N: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=60 (2.00 LT) | O: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | OI: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | OIN: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=60 (2.00 LT) | ON: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=60 (2.00 LT) | R: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=60 (2.00 LT) | RI: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=60 (2.00 LT) | RIN: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=60 (2.00 LT) | RN: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=60 (2.00 LT) | RO: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=60 (2.00 LT) | ROI: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=60 (2.00 LT) | ROIN: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=60 (2.00 LT) | RON: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=60 (2.00 LT) | X+F: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=60 (2.00 LT) | X: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | none: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | separation: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=60 (2.00 LT) | swap-I: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | swap-N: dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | swap-O: dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=60 (2.00 LT) | swap-R: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=8 (0.27 LT) | A2 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | A3 (stored): dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | A4 (stored): dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=8 (0.27 LT) | I: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | IN: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=8 (0.27 LT) | N: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=8 (0.27 LT) | O: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | dependence bias detectable (interval excludes 0) | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | OI: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | OIN: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=8 (0.27 LT) | ON: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=8 (0.27 LT) | R: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=8 (0.27 LT) | RI: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=8 (0.27 LT) | RIN: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=8 (0.27 LT) | RN: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=8 (0.27 LT) | RO: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=8 (0.27 LT) | ROI: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=8 (0.27 LT) | ROIN: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=8 (0.27 LT) | RON: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=8 (0.27 LT) | X+F: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=8 (0.27 LT) | X: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | none: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | separation: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=8 (0.27 LT) | swap-I: dependence bias | no detectable dependence bias | no detectable dependence bias | realized-noise outlier, no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | swap-N: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
| rossler | allocation | deployable | H=8 (0.27 LT) | swap-O: dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | no detectable dependence bias | not replicated |  |
| rossler | allocation | deployable | H=8 (0.27 LT) | swap-R: dependence bias | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | dependence bias detectable (interval excludes 0) | replicated | dependence bias detectable (interval excludes 0) |
