# Levenberg-Marquardt iteration doubling of the PLP estimator, pilot preset, DEV-0 (WU-0005.6)

**DEVELOPMENT (DEV-0): conditional on one realization; not a hypothesis test; nothing here is promoted.**

Status: report of a development study for the owner (decision O5). Written by claude-sonnet-5-5, 2026-10-15.
Placement: this file is on the branch `wu/0005-6-lm-doubling` under `docs/agent/notes/` because the developer
role may not edit `docs/study/`; the coordinator can move it to `docs/study/lm_doubling_dev0_report.md`.

## 1. Question

The PLP state estimator runs a fixed 15 Levenberg-Marquardt iterations (v3 section 4). The budget table lists the iterative
error of every primary quantity of interest (QoI) as "not estimated" (DEC-0024). This study measures the change of each
QoI when the iteration count is doubled, 15 to 30 and 30 to 60, on common inputs, and asks whether the 15-iteration
error is below 10% of the sampling half-width (strict, `budget.below_tenth`).

## 2. Setup

- Code: develop commit `e29cb16929b5a1e15ec02e005dc6904869804cae` (gate pass at `083f594`: unit 1202, integration 14),
  a clean detached worktree (`git status` empty) used for the three arms and the probe. Tool: `tools/lm_doubling.py`
  (WU-0005.6b), decision rule R of the Mathematics check (it replaced the plan's D1 to D3).
- Run: preset `pilot`, seed id DEV-0 (20261005), CPU, `LPC_THREADS=8`, `tools/run_preset.sh` with
  `--estimator-refine-steps 15 | 30 | 60`, jax and jaxlib 0.11.2, one preset at a time, Intel Core i9-14900K.
- Wall times: arm 15, 5343 s (2026-10-14T11:18:58Z to 12:48:01Z); arm 30, 9578 s (12:48:04Z to 15:27:42Z); arm 60, 18184 s
  (15:28:14Z to 20:31:18Z); Part A probe, 19673 s. The machine was shared with other lanes, so these times are not a cost benchmark.
- Part A (per estimate): every PLP input of the five QoIs (core cell, all three splits, oracle and evaluation draws; the test rows
  0 to 299 of the noise-sweep cells at rho = 0.5%, 2%, 5%) re-estimated at 15, 30, 60 and 120 iterations in the pipeline's chunks.
- Statistics: for each QoI part and system, with hw = half-width of the 15-iteration interval, d1 = largest of |change of the point,
  lower end, upper end| from 15 to 30 divided by hw, d2 likewise from 30 to 60, S = d1 + 2 d2, and the tail ratio r_A of Part A
  (rule R). Class N (negligible, LM-row flag "yes") needs: the part verdict the same at 15, 30 and 60; d2 <= d1/2; r_A <= 1/2; S < 0.1.
  Class X (not negligible): the verdict differs among the arms, or d1 >= 0.1, or (d2 <= d1/2 and r_A <= 1/2 and S >= 0.1).
  Class U (not certified): every other case (including a structural switch, a part missing at an arm, an unsupported tail).
  The size S hw is an estimate only under the hypothesis H-geo (each doubling after 60 at least halves the QoI change).

## 3. Result: 18 parts, N 5, X 7, U 6

LM-row flag ("below 10% of the sampling half-width": yes iff class N): **yes for 5 of 18 parts, no for 13.**

| system | QoI part | class | LM-row flag | d1 (sets) | d2 (sets) | S = d1 + 2 d2 | size in QoI units | r_A | S x sqrt(n_full/n) | endpoint-limited |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chua | H2a(i) | X | no | 0.116 (hi) | 0.000163 (lo) | 0.117 | 0.00606, S hw (estimate under H-geo) | 0.25 | 0.165 | yes |
| chua | H2a(ii) interior | U | no | 0.0204 (pt) | 0.0434 (lo) | 0.107 | 0.00269, d1 hw (tail not supported) | 0.25 | 0.151 | no |
| chua | H2a(ii) zero | U | no | 0.0471 (pt) | 0.043 (hi) | 0.133 | 0.00472, d1 hw (tail not supported) | 0.25 | 0.188 | yes |
| chua | H2b(i) | X | no | 0.108 (pt) | 0.0759 (lo) | 0.26 | 0.0103, >= d1 hw | 0.403 | 0.474 | no |
| chua | H2b(ii) | N | yes | 0.00605 (pt) | 0.00139 (lo) | 0.00884 | 0.000323, S hw (estimate under H-geo) | 0.205 | 0.0161 | no |
| chua | H3c | X | no | 0.182 (lo) | 0.000918 (lo) | 0.184 | 0.0554, S hw (estimate under H-geo) | 0.246 | 0.26 | no |
| lorenz63 | H2a(i) | X | no | 0.182 (hi) | 0.0958 (hi) | 0.373 | 0.00763, >= d1 hw | 0.411 | 0.528 | yes |
| lorenz63 | H2a(ii) interior | U | no | 0.0301 (pt) | 0.0154 (hi) | 0.061 | 0.00349, d1 hw (tail not supported) | 0.411 | 0.0862 | yes |
| lorenz63 | H2a(ii) zero | N | yes | 0.0711 (lo) | 0.00316 (hi) | 0.0775 | 0.00726, S hw (estimate under H-geo) | 0.411 | 0.11 | no |
| lorenz63 | H2b(i) | X | no | 0.156 (hi) | 0.00788 (pt) | 0.172 | 0.0145, S hw (estimate under H-geo) | 0.401 | 0.313 | no |
| lorenz63 | H2b(ii) | X | no | 0.115 (hi) | 0.00686 (hi) | 0.128 | 0.0056, S hw (estimate under H-geo) | 0.41 | 0.234 | yes |
| lorenz63 | H3c | X | no | 0.305 (hi) | 0.151 (hi) | 0.607 | 0.195, S hw (estimate under H-geo) | 0.434 | 0.859 | no |
| rossler | H2a(i) | U | no | 0.0088 (hi) | 0.0088 (hi) | 0.0264 | 0.000395, d1 hw (tail not supported) | 0 | 0.0373 | yes |
| rossler | H2a(ii) interior | N | yes | 0.0118 (hi) | 0.00097 (hi) | 0.0137 | 0.00169, S hw (estimate under H-geo) | 0 | 0.0194 | no |
| rossler | H2a(ii) zero | N | yes | 4.79e-05 (pt) | 7.17e-06 (pt) | 6.22e-05 | 7.89e-06, S hw (estimate under H-geo) | 0 | 8.8e-05 | no |
| rossler | H2b(i) | U | no | 0 (pt) | 0 (pt) | 0 | 0, d1 hw (tail not supported) | 0.571 | 0 | no |
| rossler | H2b(ii) | N | yes | 7.58e-05 (lo) | 2.63e-05 (pt) | 0.000128 | 5.69e-06, S hw (estimate under H-geo) | 0 | 0.000234 | yes |
| rossler | H3c | U | no | 3.32e-05 (lo) | 3.7e-05 (lo) | 0.000107 | 2.4e-06, d1 hw (tail not supported) | 0.49 | 0.000151 | no |

Class counts per system: lorenz63 N 1 / X 4 / U 1; rossler N 3 / X 0 / U 3; chua N 1 / X 3 / U 2.

Notes on specific rows:

- lorenz63 H3c: the verdict differs among the arms (pass at 15, inconclusive at 30, pass at 60), which alone makes it class X.
- chua H3c: the number of regimes K chosen by A5 changes (8 at 15, 5 at 30, 5 at 60); a structural switch (it blocks class N and the S >= 0.1 bullet of X; here d1 = 0.18 gives X anyway).
- Endpoint-limited at B = 500 (the point estimate alone would give another class): lorenz63 H2a(i), H2a(ii) interior, H2b(ii); chua H2a(i), H2a(ii) zero; rossler H2a(i), H2b(ii). The change of a bootstrap endpoint carries Monte Carlo noise of the order of the 0.05 trigger at B = 500 (Mathematics check M2); no floor was applied, so noise pushes toward X or U, never toward N.
- rossler H2b(i) is U only because r_A = 0.571 exceeds 1/2 (d1 = d2 = 0: the QoI does not move).
- rossler: 3 to 28 estimates per Part A group had a replaced state or nu at some level and are left out of the per-estimate ratios (counted, reported in the probe file); lorenz63 and chua had none.
- Part A, share of estimates that move by more than 0.1 rho nu(30) from one doubling to the next (all groups pooled): lorenz63 2.3% (15 to 30), 1.2% (30 to 60), 0.52% (60 to 120); rossler 0.024%, 0.003%, 0.0013%; chua 0.34%, 0.082%, 0.032%.
- Estimates with c/rho^2 above the chi-square 0.999 quantile (core test split, 100000 estimates, at 15, 30, 60, 120 iterations): lorenz63 2916, 2299, 2072, 2042; rossler 106, 106, 106, 106 (not converging: the wrong-basin or misfit group); chua 405, 330, 282, 276. No estimate crossed from below to above at any doubling.

## 4. Evidence that the comparison is paired and exact

- C0 (leaves that cannot read a PLP output, 35 patterns with a producer line each) bitwise equal across every pair of arms: 0 violations, over 6360, 6559 and 4745 differing leaves for the pairs 15-30, 15-60 and 30-60. All 35 patterns match at least one leaf (no coverage gap), including the robustness patterns.
- P0: the probe's pooled `lm_summary` and counts equal the stored ones exactly, at the 15, 30 and 60 arms, for all three systems (core oracle and evaluation kinds, and the sweep cells). Part A and the arms share commit, preset, seed id, CPU, `LPC_THREADS`, `XLA_FLAGS`, jax and jaxlib; the probe recorded each arm's start and end time.
- P1 (the 30-iteration run starts with the 15-iteration run, so the cost never rises and the accepted count never falls): 1404 exact comparisons of the stored `lm` summaries, 0 violations; per estimate, 0 violations in every group and doubling.
- Smoke checks before the pilot (K3): the flag at 15 and an absent flag give bitwise identical results (4555 leaves, provenance and wall-clock excluded).
- Review: independent review rounds 1 and 2 of the tool and the knob are in the unit file; the knob and the tool were merged into develop at `083f594`.

## 5. Limits

- One realization (DEV-0), one trajectory, one trained network per noise level; the numbers say nothing about between-realization variability.
- Pilot sizes (test 500, sweep 300, M = 200, evaluation draws 2) and B = 500 resamples; the full run has test 1000, sweep 1000 and B = 2000.
- The transfer column S x sqrt(n_full/n) is reported, never applied: a systematic iterative change does not shrink with n while the half-width does, so relative to hw it grows like sqrt(n). It rests on that scaling and on H-geo; a full-run 30/60 twin would remove the projection (open question O4).
- H-geo (each doubling after 60 at least halves the QoI change) cannot be verified from three levels; r_A (60 to 120 against 30 to 60, per estimate) is the supporting check.
- Part A covers the PLP inputs listed above; the V3 and V4 checks and the robustness variants were not re-estimated at the doubled budgets.
- Within a class X part, S is a lower estimate when a ratio condition fails; U parts have no supported size.

## 6. What is not concluded

- No hypothesis (H1 to H3) is tested, and no verdict is given or changed here; the verdict changes quoted are those of the doubled runs on DEV-0.
- No statement about the confirmatory run, no promotion, no bound on the error of the full-size run.
- No claim that the 15-iteration design is wrong or right: the class of a part describes the size of its change under doubling, not a defect.
- No choice among the options below.

## 7. Options for the owner (O5), stated without a recommendation

If the iterative error is not below 10% of the half-width for a quantity (class X or U), the owner can:

1. **Adopt a convention:** "PLP is the fixed 15-iteration Levenberg-Marquardt estimator" (like LPC.NV.1 for the discretization), so that the estimand is defined with 15 iterations. The budget's iterative row would then report the measured sizes above as a property of the estimand, with the flag as measured. No number of the study moves.
2. **Raise the design value** (a v3 change; for example 30 or 60). Every PLP number moves, and the change could be folded into the seed-step regeneration so that no extra reference run is needed. The 30-iteration results above would then be the design arm, with its own tail to check.
3. **Report and flag only:** keep 15 iterations, print the measured row of the budget with the "no" flags, and state the limitation in the report.

Related open items: the budget row text for WU-0008 (O6); the transfer of these DEV-0 numbers to the confirmatory run (O4).

## 8. Files

Run directory (not tracked): `lpcstudy-wt/run/lm-post/runs/dev/wu0005-6/` with `k15`, `k30`, `k60` (each `pilot/results.json`), `probe-pilot/pilot/probe_pilot.json` (and `.npz`), `pilot-compare.txt` and `pilot-compare.json`. The sha256 values are in `docs/agent/records/results-manifest.md`.
