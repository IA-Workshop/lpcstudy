# Exploratory theorem checks on the existing per-state dumps (WU-0028)

**DEVELOPMENT (DEV-1, DEV-2): not a hypothesis test.** No run, no GPU, no new data. Every number comes from the stored
arrays of `states/<system>.npz` (schema `lpcstudy.states/2`): DEV-2 `full` (1000 test states, GPU) and DEV-1 `pilot`
(500 test states, 300 sweep states). Script: `2026-10-21-theory-dump-checks/theory_dump_checks.py`; log `run.log`;
complete outputs `tables.md`, `results.json` in the same directory. Reproduce:
`python theory_dump_checks.py <full/states> <pilot/states> <outdir>` (one niced thread, about 20 s).

## Conventions reused, and limits

- First passage is the study's rule `sqrt(mse + rho^2) > theta` (`oracle.characteristic_horizon`), theta = 0.2
  (`primary_threshold`), rho = 0.01 (`core_noise`). The dump does not store rho or theta; they are the config defaults
  (listed under missing fields). The self-test confirms the grid first passage equals `characteristic_horizon` on 200
  random contiguous curves. The envelope is `min(E_C, E_P)`, the hybrid is the clipped oracle weight, `u = (E_P - C)/c`,
  `c = E_C + E_P - 2C` (the pipeline's A* definition).
- **The stored horizon grid is five points, {8, 15, 30, 60, 120} steps** (0.27, 0.5, 1, 2, 4 LT), not the contiguous
  1..240 of the pipeline. First passage is therefore known only to the grid cell, and censoring is at 120 steps (4 LT),
  not 240. All gains and bounds below are differences of grid points (multiples of 7, 15, 30, 60 steps).
  P1(d') and N4(b) are proved for any ordered set of horizons, so the grid statement is exact as stated, but a
  gain below one cell is invisible. A state whose T_m and T_m(sqrt2 theta) fall in the same cell has bound 0 and gain 0, which
  cannot fail. We therefore report the informative subset (bound > 0) separately.
- One dump per system and seed; estimates are conditioned on the stored grid and on the 200 oracle draws. No
  uncertainty intervals are attached (no replication). Nothing here is a verdict.
- On the stored moments P1(c) and N4 are algebraic identities (`V_min/min(E)` is a function of `E_C, E_P, C`), so
  "0 violations" tests the pipeline's moments and the proof's bookkeeping, not an empirical law.
- Self-test (known answers, logged in `run.log`): T1 first passage equals the oracle function; T2 a manufactured case with
  gain 60 = bound 60 steps (hand-computed); T3 a C<0 case with f = 0.05 exactly; T3b N4 identity and predicted gain;
  T4 R_c^2 = 1 for u constant on cells, < 0.02 for independent u, Pythagoras residual < 1e-12; T5 row Spearman against
  `scipy.stats.spearmanr`. All pass.

## (a) P1(d')

### T1. P1(d') on the grid (study rule, tolerance sqrt2*theta; theta=0.2, rho=0.01)

| dump | n | T_m censored | H1 censored (bound inf.) | C<0 at H1 (outside hypothesis) | tested (C>=0 at H1) | of which bound>0 | tested gain>0 | gain=bound>0 | bound>0, gain 0 | violations (tested) | violations (C<0 states) | lower-bound violations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEV-2 full/lorenz63 | 1000 | 185 | 90 | 137 | 588 | 51 | 11 | 11 | 40 | 0 | 1 | 0 |
| DEV-2 full/rossler | 1000 | 559 | 150 | 37 | 254 | 8 | 2 | 2 | 6 | 0 | 4 | 0 |
| DEV-2 full/chua | 1000 | 339 | 93 | 86 | 482 | 39 | 7 | 7 | 32 | 0 | 4 | 0 |
| DEV-1 pilot/lorenz63 | 500 | 93 | 44 | 61 | 302 | 26 | 10 | 10 | 16 | 0 | 1 | 0 |
| DEV-1 pilot/rossler | 500 | 271 | 66 | 20 | 143 | 4 | 0 | 0 | 4 | 0 | 2 | 0 |
| DEV-1 pilot/chua | 500 | 144 | 42 | 52 | 262 | 29 | 6 | 4 | 23 | 0 | 4 | 0 |

The tolerance rule with the exact noise form (mse > 2(theta^2 - rho^2)) differs by at most one tested state per dump (see tables.md).


Reading. Consistent with P1(d'): no violation among the tested states in any dump (the bound is the algebraic result
above), and no lower-bound violation (T_h >= T_m) in any state. The informative states are few (4 to 51 per dump), and
among them the gain equals the bound in 0 to 11 (a tight case on the grid, as in the constructed two-phase curves of
A1.8), and is zero with a positive bound in the rest. The states with C < 0 at H1 (20 to 137 per dump) are outside the
hypothesis; 1 to 4 per dump exceed the bound there, which is what P1(e) allows, not a violation. After bracketing the
true step inside each grid cell (previous grid point to grid point), no state is a certain violation. The reported-only
screen `ln2/(2 Lambda_bar)` is exceeded (grid-resolved) in 10, 2 and 5 of the 509, 252 and 411 screened DEV-2 states
(Lorenz, Rossler, Chua); this is a count at grid resolution and cannot be compared with the 1-step tolerance of the study's
own screen.

## (b) N4

### T2. N4 on the grid

| dump | max |V/min - f| (interior rows) | interior rows / all | states with f valid at crossing | hypothesis met | bound violations | gain = predicted (grid) | predicted gain 0 | median f at crossing | median varrho at crossing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEV-2 full/lorenz63 | 1.8e-15 | 3470/5000 | 604 | 586 | 0 | 586 | 575 | 0.855 | 0.189 |
| DEV-2 full/rossler | 1.0e-15 | 3620/5000 | 349 | 300 | 0 | 300 | 299 | 0.825 | 0.284 |
| DEV-2 full/chua | 7.8e-16 | 3543/5000 | 506 | 476 | 0 | 476 | 467 | 0.881 | 0.264 |
| DEV-1 pilot/lorenz63 | 4.4e-16 | 1736/2500 | 302 | 284 | 0 | 284 | 275 | 0.824 | 0.204 |
| DEV-1 pilot/rossler | 6.7e-16 | 1843/2500 | 179 | 157 | 0 | 157 | 157 | 0.816 | 0.321 |
| DEV-1 pilot/chua | 1.3e-15 | 1729/2500 | 283 | 264 | 0 | 263 | 256 | 0.883 | 0.255 |


The predicted threshold is `(theta^2 - rho^2)/f_j` with f_j taken at the crossing grid step j; the N4(b) hypothesis
(f at the predicted step >= f_j) is checked per state. Reading. The identity `V_min/min(E) = f(varrho, r)` holds to
1e-15 on every interior row (C <= min(E_C, E_P)); 28 to 31% of rows have C > min (clipped weight, f not exact, excluded).
The bound `T_h <= T_pred` has 0 violations among states meeting its hypothesis. The realized gain equals the predicted
one in all but one hypothesis-meeting state (the one exception is DEV-1 Chua, 263 of 264), but this agreement is weak
evidence: 97 to 100% of these states have predicted and realized gain 0 on the grid, so the comparison can only
distinguish zero from a one-cell gain. It is consistent with N4, not discriminating. Median f at the crossing is
0.83 to 0.88 and median varrho 0.19 to 0.28 (full dumps), so the typical state sits in the weak-gain region.

Dependence on library size. The sweep groups hold H_ref moments only (E_C, E_P, C, w*, err_corr at 30 steps), for the
first nS states, at rho in {0.01, 0.02} for n_lib in {1000, ..., 100000}. **The realized horizon gain against n_lib cannot be
computed from these data** (no per-horizon curves in the sweep groups). What can be computed is f at H_ref, and the
N4 exponential-growth prediction `ln(1/f)/(2 Lambda_bar)` evaluated at H_ref, a model-based number, not a measured gain:


| system | n_lib | frac C<0 | median varrho | median r | median f (interior) | median ln(1/f)/(2 Lambda_bar) steps |
| --- | --- | --- | --- | --- | --- | --- |
| lorenz63 | 1000 | 0.374 | 0.043 | 0.015 | 0.96 | 0.73 |
| lorenz63 | 3162 | 0.312 | 0.074 | 0.04 | 0.932 | 1.11 |
| lorenz63 | 10000 | 0.23 | 0.158 | 0.082 | 0.918 | 1.34 |
| lorenz63 | 31623 | 0.141 | 0.279 | 0.161 | 0.889 | 1.57 |
| lorenz63 | 100000 | 0.076 | 0.401 | 0.244 | 0.923 | 1.2 |
| rossler | 1000 | 0.338 | 0.048 | 0.031 | 0.948 | 0.71 |
| rossler | 3162 | 0.288 | 0.094 | 0.066 | 0.928 | 1.1 |
| rossler | 10000 | 0.144 | 0.213 | 0.163 | 0.899 | 1.45 |
| rossler | 31623 | 0.078 | 0.342 | 0.25 | 0.9 | 1.43 |
| rossler | 100000 | 0.031 | 0.433 | 0.297 | 0.92 | 1.12 |
| chua | 1000 | 0.335 | 0.062 | 0.037 | 0.927 | 1.07 |
| chua | 3162 | 0.256 | 0.128 | 0.074 | 0.918 | 1.21 |
| chua | 10000 | 0.184 | 0.208 | 0.138 | 0.906 | 1.44 |
| chua | 31623 | 0.106 | 0.329 | 0.199 | 0.911 | 1.36 |
| chua | 100000 | 0.078 | 0.396 | 0.24 | 0.926 | 1.0 |

Paired change n_lib 1000 -> 100000, rho=0.01 (DEV-2): fraction with varrho up / f up

| system | pairs | frac varrho up | frac f up | median change f |
| --- | --- | --- | --- | --- |
| lorenz63 | 439 | 0.875 | 0.435 | -0.011 |
| rossler | 521 | 0.939 | 0.464 | -0.0092 |
| chua | 500 | 0.85 | 0.51 | 0.001 |


Reading. The correlation varrho rises with n_lib in all three systems (fraction of states increasing 85% to 94% from
1000 to 100000 at rho = 0.01; median from 0.04 to 0.40 in Lorenz), and the share of states with C < 0 falls (0.37 to 0.08
in Lorenz). That is the mechanism N4 invokes. But the median f does not rise monotonically: in Lorenz it goes 0.96, 0.93,
0.92, 0.89, 0.92 across the five sizes, because r = min/max also grows with the library, and f depends on both. The paired
change in f from 1000 to 100000 is small and of mixed sign (median -0.011 Lorenz, -0.009 Rossler, +0.001 Chua at rho = 0.01; +0.011, +0.027, +0.027 at
rho = 0.02). The exponential-growth predicted gain at H_ref is non-monotone in n_lib (0.7 to 1.6 steps in Lorenz).
So the data are consistent with varrho rising with the library, and **not consistent with a monotone fall of the
predicted gain with n_lib at H_ref in these dumps**; whether the realized crossing-horizon gain falls cannot be shown
from them. The predicted gains are all about 1 step or less, far below the 7-step grid resolution at H_ref.

## (c) N6

The curvature-weighted R_c^2 is computed on `u` at H_ref. The oracle profile is `qn/oracle/x_test` (one row per state).
The deployable profile is `core/profile` (4 evaluation draws per state, pooled, with the state's c repeated per draw as in
the pipeline's pooled tree). Stored A5 leaf map: `core/a5_leaf` (the chosen-K tree fitted on construction; here the leaf
means of u are refitted on the test states, which is in-sample and optimistic).


| dump | u outside [0,1] | leaves | R_c^2 leaf map | global excess | floor (1-R^2)*excess | clip-consistent leaf regret | observed A5 regret | observed A2 regret | clip-consistent best-global regret | linear R_c^2 oracle (in/cross) | linear R_c^2 deployable (in/cross) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEV-2 full/lorenz63 | 0.313 | 8 | 0.311 | 0.0342 | 0.0236 | 0.0231 | 0.0244 | 0.0337 | 0.0337 | 0.61 / 0.47 | 0.10 / -0.11 |
| DEV-2 full/rossler | 0.296 | 4 | 0.074 | 0.000162 | 0.00015 | 0.000137 | 0.000138 | 0.000148 | 0.000148 | 0.43 / 0.41 | 0.18 / 0.17 |
| DEV-2 full/chua | 0.306 | 4 | 0.023 | 0.00679 | 0.00664 | 0.00646 | 0.00685 | 0.0067 | 0.00662 | 0.11 / -0.08 | 0.06 / -0.08 |
| DEV-1 pilot/lorenz63 | 0.326 | 6 | 0.5 | 0.0328 | 0.0164 | 0.0163 | 0.018 | 0.0333 | 0.0327 | 0.91 / 0.88 | 0.53 / 0.61 |
| DEV-1 pilot/rossler | 0.27 | 4 | 0.047 | 0.000174 | 0.000166 | 0.000151 | 0.000156 | 0.000162 | 0.00016 | 0.42 / -0.51 | 0.16 / -0.24 |
| DEV-1 pilot/chua | 0.362 | 5 | 0.059 | 0.0124 | 0.0117 | 0.0115 | 0.015 | 0.0138 | 0.0123 | 0.76 / 0.66 | 0.27 / -0.08 |

CART R_c^2 against K (in-sample / two-fold cross-fit on contiguous halves), all states

| dump | profile | K=2 | K=3 | K=4 | K=5 | K=6 | K=8 | K=12 | K=16 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEV-2 full/lorenz63 | oracle | 0.47 / 0.29 | 0.60 / 0.25 | 0.62 / 0.29 | 0.63 / 0.33 | 0.63 / 0.27 | 0.64 / 0.27 | 0.64 / 0.22 | 0.64 / 0.22 |
| DEV-2 full/lorenz63 | deployable | 0.17 / 0.13 | 0.25 / 0.07 | 0.32 / 0.18 | 0.39 / -0.03 | 0.44 / -0.06 | 0.49 / -0.03 | 0.54 / 0.05 | 0.56 / 0.04 |
| DEV-2 full/rossler | oracle | 0.25 / 0.24 | 0.35 / 0.24 | 0.42 / 0.30 | 0.49 / 0.30 | 0.51 / 0.26 | 0.56 / 0.27 | 0.60 / 0.32 | 0.62 / 0.32 |
| DEV-2 full/rossler | deployable | 0.08 / 0.06 | 0.12 / -0.03 | 0.14 / -0.39 | 0.15 / -0.38 | 0.20 / -0.54 | 0.21 / -0.52 | 0.23 / -0.55 | 0.25 / -0.56 |
| DEV-2 full/chua | oracle | 0.09 / -0.71 | 0.13 / -0.73 | 0.16 / -0.77 | 0.18 / -0.87 | 0.19 / -0.96 | 0.25 / -0.96 | 0.33 / -0.92 | 0.34 / -0.95 |
| DEV-2 full/chua | deployable | 0.05 / -0.16 | 0.07 / -0.45 | 0.13 / -0.45 | 0.17 / -0.48 | 0.18 / -0.48 | 0.22 / -0.50 | 0.24 / -0.52 | 0.25 / -0.56 |
| DEV-1 pilot/lorenz63 | oracle | 0.89 / 0.92 | 0.92 / 0.89 | 0.94 / 0.90 | 0.95 / 0.92 | 0.95 / 0.92 | 0.95 / 0.91 | 0.95 / 0.90 | 0.95 / 0.90 |
| DEV-1 pilot/lorenz63 | deployable | 0.60 / 0.43 | 0.65 / 0.40 | 0.68 / 0.42 | 0.70 / 0.42 | 0.72 / 0.49 | 0.80 / 0.51 | 0.84 / 0.38 | 0.86 / 0.25 |
| DEV-1 pilot/rossler | oracle | 0.40 / 0.31 | 0.49 / 0.34 | 0.57 / 0.37 | 0.64 / 0.43 | 0.67 / 0.45 | 0.71 / 0.53 | 0.75 / 0.48 | 0.77 / 0.46 |
| DEV-1 pilot/rossler | deployable | 0.10 / -0.06 | 0.17 / -0.11 | 0.22 / -0.01 | 0.26 / -0.03 | 0.29 / -0.06 | 0.33 / -0.03 | 0.36 / -0.08 | 0.39 / -0.23 |
| DEV-1 pilot/chua | oracle | 0.75 / 0.66 | 0.83 / 0.66 | 0.87 / 0.71 | 0.89 / 0.71 | 0.89 / 0.66 | 0.90 / 0.63 | 0.92 / 0.62 | 0.93 / 0.60 |
| DEV-1 pilot/chua | deployable | 0.59 / 0.06 | 0.64 / 0.02 | 0.67 / 0.01 | 0.69 / -0.01 | 0.70 / -0.02 | 0.71 / -0.04 | 0.72 / -0.08 | 0.73 / -0.14 |


Reading.
- **Assumption failure.** 30% of states have u outside [0, 1] (29% with u < 0), so N6's no-clipping assumption fails for a
  large share; the clip-consistent regret column uses the exact `excess_mse` definition with the clipped leaf weight
  (P3(a)). The interior-only variants (u in [0,1]) are in `tables.md`; selecting on u biases R_c^2 and is shown for
  comparison only.
- **Predicted floor against observed regret (stored K only).** At the stored chosen-K leaf map the predicted floor is
  0.0236, 1.5e-4 and 6.6e-3 (Lorenz, Rossler, Chua; clip-consistent 0.0231, 1.4e-4, 6.5e-3) against the observed A5 regret
  0.0244, 1.4e-4, 6.8e-3. The unclipped floor is within 9% of the observed regret (3%, 9%, 3%) and the clip-consistent one within 6%. It is consistent with N6, but it is partly built in: the
  A5 leaves are fitted to the same states' u structure, the floor is evaluated in-sample, and the best-global excess differs
  little from the A5 regret in Rossler and Chua (R_c^2 of 0.07 and 0.02), so any floor near the global excess matches. Lorenz
  is the informative case (R_c^2 = 0.31, floor about 30% below the global excess, observed A5 regret 28% below A2's).
- **Regret against K is not derivable.** Only the chosen-K leaves are stored (8, 4, 4 distinct leaves in the full test
  set), so the plateau of A5 regret over K = 2..16 cannot be compared with a predicted floor. The CART table gives a
  separate, optimistic prediction of what R_c^2 a K-leaf map can reach: in-sample it rises steadily with K (Lorenz oracle
  0.47 to 0.64), but the two-fold cross-fit is flat or negative, so the stored data do not show that more regimes would
  help out of sample. The weighted R_c^2 is dominated by a few high-curvature states, which makes the cross-fit unstable.
- Deployable-profile R_c^2 is far below the oracle-profile one (Lorenz linear 0.10 against 0.61 in-sample; cross-fit
  negative for the deployable profile in Lorenz and Chua): consistent with the deployable profile
  carrying much less of the structure of u than the oracle profile does (it does not identify why).

## (d) N8 (partial)

Per state, Spearman correlation of w*(H_ref) over the four noise levels (n_lib = 10^4, first nS states, common
oracle draws), grouped by the core oracle noise sensitivity N (rho = 0.01): N = 0 means the analog never changed
under the noise draws (N < 1e-9; round-off is about 1e-13), then low and high N around the median positive N.

| dump | group (N at rho=0.01) | n | defined | median | frac =+1 | frac >0 | frac non-decreasing | w* median by rho (0.005, 0.01, 0.02, 0.05) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEV-2 full/lorenz63 | N=0 | 282 | 274 | 0.4 | 0.274 | 0.58 | 0.348 | 0.022, 0.051, 0.078, 0.107 |
| DEV-2 full/lorenz63 | N>0 low | 359 | 353 | 0.2 | 0.156 | 0.544 | 0.228 | 0.022, 0.051, 0.078, 0.107 |
| DEV-2 full/lorenz63 | N>0 high | 359 | 302 | 0.77 | 0.126 | 0.748 | 0.521 | 0.022, 0.051, 0.078, 0.107 |
| DEV-2 full/rossler | N=0 | 112 | 109 | -0.2 | 0.138 | 0.394 | 0.179 | 0.036, 0.075, 0.102, 0.135 |
| DEV-2 full/rossler | N>0 low | 444 | 438 | 0.4 | 0.155 | 0.589 | 0.2 | 0.036, 0.075, 0.102, 0.135 |
| DEV-2 full/rossler | N>0 high | 444 | 393 | 0.77 | 0.117 | 0.725 | 0.453 | 0.036, 0.075, 0.102, 0.135 |
| DEV-2 full/chua | N=0 | 140 | 133 | 0.4 | 0.256 | 0.586 | 0.329 | 0.032, 0.063, 0.079, 0.169 |
| DEV-2 full/chua | N>0 low | 430 | 424 | 0.32 | 0.158 | 0.55 | 0.242 | 0.032, 0.063, 0.079, 0.169 |
| DEV-2 full/chua | N>0 high | 430 | 385 | 0.77 | 0.122 | 0.735 | 0.451 | 0.032, 0.063, 0.079, 0.169 |
| DEV-1 pilot/lorenz63 | N=0 | 67 | 67 | 0.0 | 0.179 | 0.493 | 0.239 | 0.022, 0.049, 0.077, 0.128 |
| DEV-1 pilot/lorenz63 | N>0 low | 117 | 117 | 0.32 | 0.188 | 0.547 | 0.214 | 0.022, 0.049, 0.077, 0.128 |
| DEV-1 pilot/lorenz63 | N>0 high | 116 | 99 | 0.77 | 0.111 | 0.717 | 0.474 | 0.022, 0.049, 0.077, 0.128 |
| DEV-1 pilot/rossler | N=0 | 34 | 33 | -0.2 | 0.0 | 0.333 | 0.029 | 0.051, 0.096, 0.104, 0.112 |
| DEV-1 pilot/rossler | N>0 low | 133 | 132 | 0.2 | 0.189 | 0.523 | 0.211 | 0.051, 0.096, 0.104, 0.112 |
| DEV-1 pilot/rossler | N>0 high | 133 | 112 | 0.4 | 0.134 | 0.732 | 0.406 | 0.051, 0.096, 0.104, 0.112 |
| DEV-1 pilot/chua | N=0 | 37 | 35 | -0.2 | 0.257 | 0.429 | 0.324 | 0.023, 0.044, 0.067, 0.182 |
| DEV-1 pilot/chua | N>0 low | 132 | 131 | 0.4 | 0.145 | 0.595 | 0.227 | 0.023, 0.044, 0.067, 0.182 |
| DEV-1 pilot/chua | N>0 high | 131 | 122 | 0.77 | 0.115 | 0.746 | 0.496 | 0.023, 0.044, 0.067, 0.182 |

Reading. The median w* rises with rho in every dump and system (e.g. Lorenz DEV-2: 0.022, 0.051, 0.078, 0.107), which is
the aggregate form of H2b(i) and consistent with N8. Per state, the picture is weaker than N8's "near +1 in the
stable group": in the N = 0 group the median Spearman is 0.4 (Lorenz), -0.2 (Rossler), 0.4 (Chua) and only 14 to 27% of
states have a perfectly rising w* over the four levels (a four-point rank correlation takes values in steps of 0.2, so
+1 is a strict criterion). The high-N group has the highest median in all six dumps (0.78 in five, 0.4 in the sixth) and the most positive correlations (72 to 75%),
the opposite of what the stable-versus-switching reading predicts; but it also has the most states with constant w*
(clipped at 0 at all levels; 45 to 57 of about 400). Not consistent with N8's prediction of the stable group having the
higher rank correlation, with these limits.

**What cannot be separated.** N is measured at rho = 0.01 only. "N = 0" says the analog did not change under the noise draws at
that level, not that it is unchanged at rho = 0.005 or 0.05, so the group is a proxy for stable retrieval, not the
condition N8 assumes. The theorem needs A (the amplified mismatch), z (the copied noise draw), and q per state; none
is stored. The analog index at each rho is not stored, so switching with rho cannot be identified directly. w* is clipped at
0 at all four levels in 3% to 8% of states, which makes a rank correlation undefined for them (counted above as
non-defined). With four rho levels per state the rank correlation is coarse.

## Fields missing from the dump schema (input to the dump schema /3 unit WU-0029)

1. `rho` (core noise) and `theta` (primary threshold) in `meta/`; the script assumes the config defaults 0.01 and 0.2.
2. Per-horizon moments `E_C(H), E_P(H), C(H)` for H = 1..240 (the pipeline's contiguous grid); the dump has five
   horizons, and censoring at 4 LT. This limits P1(d') and N4(b) to cell resolution (item C2 of the theorem program).
3. The same per-horizon moments (or at least the crossing-relevant ones) for each sweep cell (n_lib, rho); the sweep groups hold
   H_ref only, so the N4 library prediction (gain against n_lib) cannot be measured.
4. A5 regret (or leaf maps) at every K in `regime_counts` (2..16), with the construction-fit weights, to compare the N6
   floor with the regret plateau; only the chosen-K leaf ids are stored. Also the construction and calibration splits'
   moments, so R_c^2 can be fitted out of sample on a split the tree did not see.
5. For N8: the analog index (retrieved library row) per state and noise level and per oracle draw (or a switching indicator),
   the base-analog mismatch A, the copied-noise term z, PLP's q, per state at H_ref; N at each rho, not only the core one.
6. For N4(b) with noise: the verification-noise draw count and the evaluation `theta` list (the study has four
   thresholds; only the primary is used here).
7. Not needed here but listed by the theorem program: mismatch `d`, `Sigma_s`, `Gamma_H`, and the 20 nearest competitors
   (N2, N3, N7).

## Summary of consistency (no verdict)

| Result | Consistent with | Not consistent with / unresolved |
| --- | --- | --- |
| P1(d') | 0 violations among tested states, 0 lower-bound violations; the bound is attained on the grid in 0 to 11 states per dump | gains below the grid resolution are invisible; most states have bound 0 |
| N4 identity | `V_min/min(E) = f` to 1e-15 | |
| N4 gain prediction | 0 violations; predicted equals realized in 99.6% to 100% of hypothesis-meeting states | not discriminating (97 to 100% zero gain); realized gain against n_lib cannot be computed |
| N4 library | varrho rises and C < 0 falls with n_lib | median f at H_ref is not monotone in n_lib |
| N6 | predicted floor within 9% (clip-consistent 6%) of the observed A5 regret at the chosen K | 30% of states have u outside [0,1]; regret against K not derivable; cross-fit R_c^2 flat or negative |
| N8 | median w* rises with rho in all systems | per-state rank correlation is not highest in the N = 0 group; N = 0 at one rho is a weak proxy |
