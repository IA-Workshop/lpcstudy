# r measurement (M-6): output of r_measurement.py

**DEVELOPMENT (DEV-1, DEV-3, DEV-4): exploratory, not a hypothesis test.** Analysis commit(s): `2b2891cb45a4ee9a37b4da514ff22d9746eea1a2`. Inputs: `/home/brianm/projects/physics/chaos/lpcstudy-wt/run/phj-f701a47/runs/dev/phj-DEV-n/contrib-2b2891c`, `contrib-ce-2b2891c`.

p = Phi(-1.96/sqrt(1+r^2)); P4 = P(at least 4 of 5); P3 = P(at least 3 of 5); E1000 = expected false replications per 1000 null rows at P4. M-6 table reproduced by `check_m6_table` (passed).

DEVELOPMENT (DEV-1, DEV-3, DEV-4): exploratory, not a hypothesis test.

| family | subset | rows | excluded | r_tot median [Q1, Q3] | r_tot RMS | r_omit median [Q1, Q3] | r_omit RMS |
|---|---|---|---|---|---|---|---|
| allocation drop-one | all | 120 |  | 1.05 [0.71, 1.48] | 1.22 | 0.34 [0.00, 1.09] | 0.86 |
| allocation drop-one | unguarded | 60 |  | 0.95 [0.60, 1.35] | 1.16 | 0.00 [0.00, 0.91] | 0.81 |
| horizon drop-one | all | 24 |  | 0.81 [0.48, 1.24] | 1.02 | 0.00 [0.00, 0.74] | 0.67 |
| horizon drop-one | unguarded | 24 |  | 0.81 [0.48, 1.24] | 1.02 | 0.00 [0.00, 0.74] | 0.67 |
| B Delta | all | 612 |  | 0.98 [0.64, 1.47] | 1.24 | 0.00 [0.00, 1.08] | 0.91 |
| B Delta | unguarded | 612 |  | 0.98 [0.64, 1.47] | 1.24 | 0.00 [0.00, 1.08] | 0.91 |
| B Delta | allocation logit | 180 |  | 0.86 [0.56, 1.20] | 1.11 | 0.00 [0.00, 0.65] | 0.77 |
| B Delta | allocation zero/one/decision | 396 |  | 1.08 [0.72, 1.59] | 1.32 | 0.42 [0.00, 1.24] | 0.99 |
| B Delta | horizon (log T) | 36 |  | 0.77 [0.60, 1.28] | 1.03 | 0.00 [0.00, 0.80] | 0.66 |
| D rungs | all | 372 |  | 1.01 [0.63, 1.45] | 1.25 | 0.17 [0.00, 1.05] | 0.92 |
| D rungs | unguarded | 211 |  | 0.93 [0.55, 1.27] | 1.10 | 0.00 [0.00, 0.78] | 0.74 |
| C2 retained | all | 83 | non-finite point or bound 19 | 1.38 [0.90, 2.23] | 1.84 | 0.94 [0.00, 2.00] | 1.60 |
| C2 retained | unguarded | 79 |  | 1.38 [0.92, 2.21] | 1.84 | 0.94 [0.00, 1.97] | 1.60 |

DEVELOPMENT (DEV-1, DEV-3, DEV-4): exploratory, not a hypothesis test.

| family | r used | r | p | P4 | P3 | E1000 |
|---|---|---|---|---|---|---|
| allocation drop-one | r_tot median | 1.05 | 0.089 | 2.9e-04 | 6.1e-03 | 0.29 |
| allocation drop-one | r_tot Q3 | 1.48 | 0.136 | 1.5e-03 | 2.0e-02 | 1.52 |
| allocation drop-one | r_tot RMS | 1.22 | 0.107 | 6.1e-04 | 1.0e-02 | 0.61 |
| allocation drop-one | r_omit median | 0.34 | 0.032 | 4.8e-06 | 3.0e-04 | 0.00 |
| allocation drop-one | r_omit RMS | 0.86 | 0.069 | 1.1e-04 | 3.0e-03 | 0.11 |
| horizon drop-one | r_tot median | 0.81 | 0.064 | 8.0e-05 | 2.4e-03 | 0.08 |
| horizon drop-one | r_tot Q3 | 1.24 | 0.110 | 6.6e-04 | 1.1e-02 | 0.66 |
| horizon drop-one | r_tot RMS | 1.02 | 0.085 | 2.5e-04 | 5.5e-03 | 0.25 |
| horizon drop-one | r_omit median | 0.00 | 0.025 | 1.9e-06 | 1.5e-04 | 0.00 |
| horizon drop-one | r_omit RMS | 0.67 | 0.051 | 3.3e-05 | 1.3e-03 | 0.03 |
| B Delta | r_tot median | 0.98 | 0.081 | 2.0e-04 | 4.6e-03 | 0.20 |
| B Delta | r_tot Q3 | 1.47 | 0.135 | 1.5e-03 | 2.0e-02 | 1.49 |
| B Delta | r_tot RMS | 1.24 | 0.110 | 6.6e-04 | 1.1e-02 | 0.66 |
| B Delta | r_omit median | 0.00 | 0.025 | 1.9e-06 | 1.5e-04 | 0.00 |
| B Delta | r_omit RMS | 0.91 | 0.074 | 1.4e-04 | 3.6e-03 | 0.14 |
| D rungs | r_tot median | 1.01 | 0.084 | 2.4e-04 | 5.3e-03 | 0.24 |
| D rungs | r_tot Q3 | 1.45 | 0.133 | 1.4e-03 | 1.9e-02 | 1.39 |
| D rungs | r_tot RMS | 1.25 | 0.111 | 6.9e-04 | 1.1e-02 | 0.69 |
| D rungs | r_omit median | 0.17 | 0.027 | 2.5e-06 | 1.8e-04 | 0.00 |
| D rungs | r_omit RMS | 0.92 | 0.074 | 1.4e-04 | 3.7e-03 | 0.14 |
| C2 retained | r_tot median | 1.38 | 0.125 | 1.1e-03 | 1.6e-02 | 1.08 |
| C2 retained | r_tot Q3 | 2.23 | 0.212 | 8.3e-03 | 6.7e-02 | 8.32 |
| C2 retained | r_tot RMS | 1.84 | 0.175 | 4.0e-03 | 4.0e-02 | 4.00 |
| C2 retained | r_omit median | 0.94 | 0.077 | 1.7e-04 | 4.1e-03 | 0.17 |
| C2 retained | r_omit RMS | 1.60 | 0.149 | 2.2e-03 | 2.6e-02 | 2.17 |

With 2 degrees of freedom, the true SD of a row lies between 0.52 and 6.28 times its estimate (95%); for a common r the median of the per-row ratios is biased low by a factor 0.833 (median of sqrt(chi2_2 / 2)), while the RMS estimates r^2 without that bias.
