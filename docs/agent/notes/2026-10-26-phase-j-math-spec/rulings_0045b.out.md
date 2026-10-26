# WU-0045b diagnostics

DEVELOPMENT (DEV-1): exploratory, not a hypothesis test; analysis code 108d7d5.

## Point 2: effective size of the reference rule's per-state excess (deployable)

| system | H | rule | realized S - V(w*) | abs(realized) | substituted mean_j V(g) - V(w*) | kappa |
|---|---|---|---|---|---|---|
| lorenz63 | 8 | A4 (stored) | 9.0 | 9.2 | 15.2 | 23.3 |
| lorenz63 | 15 | A4 (stored) | 10.6 | 14.5 | 17.0 | 20.9 |
| lorenz63 | 30 | A4 (stored) | 14.4 | 19.8 | 24.8 | 62.8 |
| lorenz63 | 60 | A4 (stored) | 25.1 | 53.4 | 55.1 | 123.5 |
| lorenz63 | 120 | A4 (stored) | 74.6 | 282.3 | 214.9 | 439.0 |
| rossler | 8 | A4 (stored) | 45.7 | 305.9 | 142.7 | 269.2 |
| rossler | 8 | ROIN | 26.9 | 314.3 | 57.2 | 269.2 |
| rossler | 8 | RON | 27.0 | 314.4 | 51.9 | 269.2 |
| rossler | 15 | A4 (stored) | 36.5 | 228.3 | 96.6 | 174.9 |
| rossler | 30 | A4 (stored) | 21.8 | 137.3 | 108.8 | 112.4 |
| rossler | 60 | A4 (stored) | 20.3 | 98.0 | 98.4 | 123.9 |
| rossler | 120 | A4 (stored) | 73.1 | 234.8 | 186.6 | 392.5 |
| chua | 8 | A4 (stored) | 3.4 | 24.8 | 5.1 | 19.4 |
| chua | 8 | ROIN | 3.6 | 26.3 | 4.0 | 19.4 |
| chua | 8 | RON | 5.0 | 25.2 | 4.4 | 19.4 |
| chua | 15 | A4 (stored) | 4.0 | 18.9 | 20.6 | 14.6 |
| chua | 30 | A4 (stored) | 0.6 | 13.7 | 26.4 | 41.2 |
| chua | 60 | A4 (stored) | 15.9 | 123.2 | 110.0 | 200.5 |
| chua | 120 | A4 (stored) | 55.6 | 300.7 | 215.5 | 497.5 |

## Point 3: exact decomposition of the paired dependence bias, Chua, H = 8

Means over the 1000 test states, in units of the mean V of the rule; T0 = noise at the draw-mean weight, T1 = 2 Cov(d, h) part, T2 = Cov(d^2, Delta^2) part. Top-5 share: share of the sum of the term carried by the 5 states with the largest |D|.

| rule | mean draw-SD of w | total/V | T0/V | T1/V | T2/V | top-5 share of total | top-5 share of T1 | top-5 share of T2 |
|---|---|---|---|---|---|---|---|---|
| A4 (stored) | 0.0497 | +0.0260 | +0.0099 | +0.0153 | +0.0008 | 0.74 | -0.12 | 1.48 |
| ROIN | 0.0377 | +0.0625 | +0.0396 | +0.0221 | +0.0008 | 0.49 | 0.03 | 0.63 |
| RON | 0.0366 | +0.0802 | +0.0635 | +0.0161 | +0.0006 | 0.81 | 0.09 | 1.04 |

RON, the five states with the largest |D_i| (paired):

| state | D_i / mean V | T1_i / mean V | T2_i / mean V | draw-SD of w | kappa / median kappa | max_j Delta^2 / kappa |
|---|---|---|---|---|---|---|
| 4 | +51.672 | +0.000 | +0.000 | 0.000 | 268.7 | 0.8 |
| 737 | +6.554 | +0.537 | -0.035 | 0.058 | 41.9 | 5.4 |
| 455 | +5.861 | +3.351 | +0.583 | 0.116 | 120.3 | 3.3 |
| 487 | +5.417 | +0.477 | -0.117 | 0.060 | 1023.3 | 1.0 |
| 568 | -4.158 | -2.919 | +0.171 | 0.050 | 1223.7 | 1.3 |

