DEVELOPMENT (DEV-1, DEV-3, DEV-4): not a hypothesis test.

## 1. Per-seed one-sided error and the p^3 product

| case | p per seed | p^3 | (2p)^3 | (3p)^3 |
|---|---|---|---|---|
| secondary 95%, nominal | 0.0250 | 1.56e-05 | 1.25e-04 | 4.22e-04 |
| secondary 95%, phi=0 (cov 0.945) | 0.0275 | 2.08e-05 | 1.66e-04 | 5.62e-04 |
| secondary 95%, phi=0.3 (cov 0.926) | 0.0372 | 5.13e-05 | 4.10e-04 | 1.38e-03 |
| primary 98.3%, nominal | 0.0083 | 5.79e-07 | 4.63e-06 | 1.56e-05 |
| primary 98.3%, phi=0 (cov 0.980) | 0.0100 | 1.00e-06 | 8.00e-06 | 2.70e-05 |
| primary 98.3%, phi=0.3 (cov 0.9695) | 0.0152 | 3.55e-06 | 2.84e-05 | 9.58e-05 |

Family (6 systems x 12 criteria, false fail with union over parts, H3a at FWER 0.013), nominal: 6.08e-03 (false pass words only, k = 1: 8.54e-04)

Family (6 systems x 12 criteria, false fail with union over parts, H3a at FWER 0.013), undercoverage phi=0.3: 2.06e-02 (false pass words only, k = 1: 2.83e-03)
Family, tau=0.8, nominal coverage: p_prim 0.0308, p_sec 0.0629, family 1.06e-01
  (false pass words only, k = 1: 1.40e-02)
Family, tau=0.8, undercoverage phi=0.3: p_prim 0.0456, p_sec 0.0817, family 2.44e-01
  (false pass words only, k = 1: 3.12e-02)

Per-seed false-pass rate against the seed-mean estimand, estimand SD tau (in SE units):
- primary: tau=0.0: p=0.0083, p^3=5.8e-07; tau=0.5: p=0.0161, p^3=4.2e-06; tau=1.0: p=0.0452, p^3=9.3e-05; tau=1.5: p=0.0921, p^3=7.8e-04
- secondary: tau=0.0: p=0.0250, p^3=1.6e-05; tau=0.5: p=0.0398, p^3=6.3e-05; tau=1.0: p=0.0829, p^3=5.7e-04; tau=1.5: p=0.1385, p^3=2.7e-03

## 2. Word stability, frozen systems, DEV-1/3/4

- per-system words: 36; same on all three seeds: 22 (0.61); of these decisive 17, inconclusive 5
- decisive (pass or fail) per seed: {'DEV-1': 27, 'DEV-3': 24, 'DEV-4': 22}; mean 24.3 of 36 (0.68)
- promoted decisive 17 of 36 (0.47); retained share of the per-seed decisive words 0.70
- words with both pass and fail across seeds: 0

## 3. Pairwise z for the primary parts (frozen systems)

| system | part | z_away 1-3 | 1-4 | 3-4 | max |
|---|---|---|---|---|---|
| chua | H2a(i) | 1.09 | 0.38 | 0.84 | 1.09 |
| chua | H2a(ii) interior | 0.81 | 0.52 | 1.37 | 1.37 |
| chua | H2a(ii) zero | 0.99 | 0.65 | 0.38 | 0.99 |
| chua | H2b(i) noise | 0.50 | 0.92 | 0.44 | 0.92 |
| chua | H2b(ii) library | 1.12 | 2.40 | 1.24 | 2.40 |
| chua | H3c | 2.10 | 2.10 | 0.55 | 2.10 |
| lorenz63 | H2a(i) | 2.15 | 0.25 | 2.06 | 2.15 |
| lorenz63 | H2a(ii) interior | 0.63 | 0.31 | 0.27 | 0.63 |
| lorenz63 | H2a(ii) zero | 1.77 | 0.43 | 2.25 | 2.25 |
| lorenz63 | H2b(i) noise | 0.43 | 0.84 | 0.40 | 0.84 |
| lorenz63 | H2b(ii) library | 0.87 | 0.22 | 0.66 | 0.87 |
| lorenz63 | H3c | 0.53 | 2.28 | 1.55 | 2.28 |
| rossler | H2a(i) | 0.71 | 0.63 | 0.11 | 0.71 |
| rossler | H2a(ii) interior | 0.60 | 1.58 | 2.10 | 2.10 |
| rossler | H2a(ii) zero | 0.35 | 0.10 | 0.46 | 0.46 |
| rossler | H2b(i) noise | 2.83 | 4.06 | 1.14 | 4.06 |
| rossler | H2b(ii) library | 0.78 | 0.72 | 0.06 | 0.78 |
| rossler | H3c | 0.79 | 0.69 | 1.50 | 1.50 |

- pairs: 54; mean z_sym^2 = 1.696 (1 + tau^2/SE^2 under a seed-dependent estimand; 1 under a fixed one; pairs share seeds, so the effective count is about 36)
- z_away > 1.645: 11 of 54 (expected under a fixed estimand and normal SEs: 5.4)
- z_away > 1.96: 10 of 54 (expected under a fixed estimand and normal SEs: 2.7)
- z_away > 2.576: 2 of 54 (expected under a fixed estimand and normal SEs: 0.5)
- z_away > 3.4: 1 of 54 (expected under a fixed estimand and normal SEs: 0.0)
- max z_away 4.06, max z_sym 4.00

## 4. Power of the all-three rule

| per-seed pi | pi^3 (promoted) | 1 - sum pi_w^3 if the rest is inconclusive |
|---|---|---|
| 0.5 | 0.125 | 0.750 |
| 0.7 | 0.343 | 0.630 |
| 0.8 | 0.512 | 0.480 |
| 0.9 | 0.729 | 0.270 |
| 0.95 | 0.857 | 0.143 |
| 0.99 | 0.970 | 0.030 |

- primary 98.3%: distance from the band edge for 80% power, in SE: one seed 3.236, all three 3.857; ratio 1.192; equivalent one-seed sample-size factor 1.421

- secondary 95%: distance from the band edge for 80% power, in SE: one seed 2.802, all three 3.423; ratio 1.222; equivalent one-seed sample-size factor 1.493
