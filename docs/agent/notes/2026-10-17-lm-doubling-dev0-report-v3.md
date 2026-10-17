# Levenberg-Marquardt iteration doubling of the PLP estimator, pilot preset, DEV-0 (WU-0005.6), version 3

**DEVELOPMENT (DEV-0): conditional on one realization; not a hypothesis test; nothing here is promoted.**

Status: version 3 of the report for the owner, written by claude-sonnet-5-5, 2026-10-17, after the owner's ruling on DEF-0028 ("amend the tool to
the plan's order", question tool, 2026-10-17; amendments note sections 20 and 29). It replaces nothing in
`docs/study/lm_doubling_dev0_report.md` (version 1, sha256 `a4b2b0fd02711171a432c1ddf532cb7b5da19679c3895ea92dec6b22e0567273`) or in
`docs/study/lm_doubling_dev0_report_v2.md` (version 2, sha256 `466219fc179cef1aebfd87905046e193d014a29ef04cc34a0baf6b6e1ee01f5f`), which stay unchanged. The data are the
same as in version 2 (three results.json, the Part A probe, develop commit `e29cb16`, DEV-0, not promoted); only the tool's classification was re-run offline
(`compare` over the stored files, 0.6 s, no new experiment) after the tool change of branch `wu/0005-6-rule-r-order` (pending independent review).
Placement: this file is `docs/agent/notes/2026-10-17-lm-doubling-dev0-report-v3.md`; the developer role may not write `docs/study/`, so the coordinator moves it to
`docs/study/lm_doubling_dev0_report_v3.md` (content unchanged).

## 0. What changed relative to version 2

- **The order of a structural switch in the tool.** `classify` in `tools/lm_doubling.py` now checks a structural switch (M7) **before** every X bullet, as the plan
  says (rule R: U is "every other case, including the structural switches of M7"; M7: a switch "makes the part class U"). Before, a switch blocked only N and the third
  X bullet (S >= 0.1 with both ratio conditions), so a part with a switch and d1 >= 0.1 or a changed verdict was X (DEF-0028). The same change makes an **infinite bound**
  (the third switch of M7) U even when the verdicts differ; that case does not occur on DEV-0. A half-width that is not positive or a NaN value is not a listed switch and
  keeps its earlier class (U, or X if the verdicts differ).
- **Effect on DEV-0 (offline re-run of `compare`; in the 620-line text output one line differs, the Chua H3c row (class, size, reasons); in the JSON five values of that one part differ: `cls` X -> U, `class_point_only` X -> U, `size_kind`, `size`, and one added reason; the re-run after fix round 1 of the tool, which adds the infinite-bound reason, is byte-identical).** Chua H3c: **X -> U** (K of A5: 8, 5, 5; d1 = 0.1821 >= 0.1 and S = 0.1839,
  which the tool formerly turned into X with an "estimate under H-geo" size of S hw = 0.0554; the size is now d1 hw = 0.0549, d2 hw = 0.00028, tail not supported). The counts
  are **N 5 / X 6 / U 7** (version 1 and the earlier tool: 5 / 7 / 6); Chua N 1 / X 2 / U 3. **No other part and no number changes.**
  **The LM-row flag (yes iff class N) is unchanged: yes for 5 of 18 parts, no for 13.**
- The primary reading of version 2 (plan-faithful) is now the tool's only reading. The secondary "class in the tool" column of version 2 is dropped.
- Everything else of version 2 (endpoint statement, sizes, M7 counts, options of O5) is carried over unchanged, except where it spoke of the tool's order (sections 2, 3, 6, 7).

## 1. Question

The PLP state estimator runs a fixed 15 Levenberg-Marquardt iterations (v3 section 4). The budget table lists the iterative
error of every primary quantity of interest (QoI) as "not estimated" (DEC-0024). This study measures the change of each
QoI when the iteration count is doubled, 15 to 30 and 30 to 60, on common inputs, and asks whether the 15-iteration
error is below 10% of the sampling half-width (strict, `budget.below_tenth`).

## 2. Setup and definitions

- Code: develop commit `e29cb16929b5a1e15ec02e005dc6904869804cae` (gate pass at `083f594`: unit 1202, integration 14),
  a clean detached worktree (`git status` empty) used for the three arms and the probe. Tool: `tools/lm_doubling.py`
  (WU-0005.6b), decision rule R of the Mathematics check (it replaced the plan's D1 to D3).
- Run: preset `pilot`, seed id DEV-0 (20261005), CPU, `LPC_THREADS=8`, `tools/run_preset.sh` with
  `--estimator-refine-steps 15 | 30 | 60`, jax and jaxlib 0.11.2, one preset at a time, Intel Core i9-14900K.
- Wall times: arm 15, 5343 s (2026-10-14T11:18:58Z to 12:48:01Z); arm 30, 9578 s (12:48:04Z to 15:27:42Z; 1.8 times arm 15); arm 60, 18184 s
  (15:28:14Z to 20:31:18Z; 3.4 times arm 15); Part A probe, 19673 s. The machine was shared with other lanes, so these times are not a cost benchmark.
- Part A (per estimate): every PLP input of the five QoIs (core cell, all three splits, oracle and evaluation draws; the test rows
  0 to 299 of the noise-sweep cells at rho = 0.5%, 2%, 5%) re-estimated at 15, 30, 60 and 120 iterations in the pipeline's chunks.
- Statistics: for each QoI part and system, with hw = half-width of the 15-iteration interval, d1 = largest of |change of the point,
  lower end, upper end| from 15 to 30 divided by hw, d2 likewise from 30 to 60, S = d1 + 2 d2, and the tail ratio r_A of Part A
  (rule R: max of F(60 to 120)/F(30 to 60) and T(60 to 120)/T(30 to 60), where F counts estimates that move by more than 0.1 rho nu(30)
  and T sums their moves; r_A = 0 if F(60 to 120) = 0).
- Classes of rule R (Mathematics check):
  - **N** (negligible, LM-row flag "yes"): the part verdict is the same at 15, 30 and 60; d2 <= d1/2; r_A <= 1/2; S < 0.1 (strict).
  - **X** (not negligible): the verdict differs among the arms, or d1 >= 0.1, or (d2 <= d1/2 and r_A <= 1/2 and S >= 0.1).
  - **U** (not certified): "every other case, including the structural switches of M7". A structural switch (M7) is the H2a(ii) "one" part existing at
    some arms only, a change of A5's chosen number of regimes K, or an infinite bound. Changes of membership counts (eligible states, zero set)
    are not structural switches; they stay inside d1 as iterative error (M7).
  - The size S hw is an estimate only under the hypothesis H-geo (each doubling after 60 at least halves the QoI change). Where a ratio
    condition fails, the lower estimate is d1 hw (monotone convergence), and U parts have no supported size: d1 hw and d2 hw are given.
- **Precedence of a structural switch (settled by the owner's ruling on DEF-0028).** Rule R makes U "every other case, including the structural switches", and M7 says the
  switches make the part class U; both hold only if a switch rules out N and every X bullet. The tool now applies that order: a structural switch gives U before the first
  (verdict change), second (d1 >= 0.1) and third (S >= 0.1) X bullets; the reasons of the bullets that would have fired are kept on the part. Version 1 and the earlier tool
  checked the switch after the first two bullets (a deviation from the plan, recorded in the unit Log before any output); version 2 stated the plan's reading as primary.
  The change affects one part on DEV-0 (Chua H3c) and no flag.

## 3. Result: 18 parts, N 5, X 6, U 7

LM-row flag ("below 10% of the sampling half-width": yes iff class N): **yes for 5 of 18 parts, no for 13** (unchanged by the order change).

| system | QoI part | class | LM-row flag | d1 (sets) | d2 (sets) | S = d1 + 2 d2 | size in QoI units | r_A | S x sqrt(n_full/n) | endpoint-limited |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chua | H2a(i) | X | no | 0.116 (hi) | 0.000163 (lo) | 0.117 | S hw = 0.00606 (estimate under H-geo) | 0.25 | 0.165 | yes |
| chua | H2a(ii) interior | U | no | 0.0204 (pt) | 0.0434 (lo) | 0.107 | d1 hw = 0.00269, d2 hw = 0.00572; tail not supported | 0.25 | 0.151 | no |
| chua | H2a(ii) zero | U | no | 0.0471 (pt) | 0.043 (hi) | 0.133 | d1 hw = 0.00472, d2 hw = 0.00431; tail not supported | 0.25 | 0.188 | yes |
| chua | H2b(i) | X | no | 0.108 (pt) | 0.0759 (lo) | 0.26 | >= d1 hw = 0.0103 (monotone convergence) | 0.403 | 0.474 | no |
| chua | H2b(ii) | N | yes | 0.00605 (pt) | 0.00139 (lo) | 0.00884 | S hw = 0.000323 (estimate under H-geo) | 0.205 | 0.0161 | no |
| chua | H3c | U | no | 0.182 (lo) | 0.000918 (lo) | 0.184 | d1 hw = 0.0549, d2 hw = 0.000277; tail not supported | 0.246 | 0.26 | no |
| lorenz63 | H2a(i) | X | no | 0.182 (hi) | 0.0958 (hi) | 0.373 | >= d1 hw = 0.00763 (monotone convergence) | 0.411 | 0.528 | yes |
| lorenz63 | H2a(ii) interior | U | no | 0.0301 (pt) | 0.0154 (hi) | 0.061 | d1 hw = 0.00349, d2 hw = 0.00178; tail not supported | 0.411 | 0.0862 | yes |
| lorenz63 | H2a(ii) zero | N | yes | 0.0711 (lo) | 0.00316 (hi) | 0.0775 | S hw = 0.00726 (estimate under H-geo) | 0.411 | 0.11 | no |
| lorenz63 | H2b(i) | X | no | 0.156 (hi) | 0.00788 (pt) | 0.172 | S hw = 0.0145 (estimate under H-geo) | 0.401 | 0.313 | no |
| lorenz63 | H2b(ii) | X | no | 0.115 (hi) | 0.00686 (hi) | 0.128 | S hw = 0.0056 (estimate under H-geo) | 0.41 | 0.234 | yes |
| lorenz63 | H3c | X | no | 0.305 (hi) | 0.151 (hi) | 0.607 | S hw = 0.195 (estimate under H-geo) | 0.434 | 0.859 | no |
| rossler | H2a(i) | U | no | 0.0088 (hi) | 0.0088 (hi) | 0.0264 | d1 hw = 0.000395, d2 hw = 0.000395; tail not supported | 0 | 0.0373 | yes |
| rossler | H2a(ii) interior | N | yes | 0.0118 (hi) | 0.00097 (hi) | 0.0137 | S hw = 0.00169 (estimate under H-geo) | 0 | 0.0194 | no |
| rossler | H2a(ii) zero | N | yes | 4.79e-05 (pt) | 7.17e-06 (pt) | 6.22e-05 | S hw = 7.89e-06 (estimate under H-geo) | 0 | 8.8e-05 | no |
| rossler | H2b(i) | U | no | 0 (pt) | 0 (pt) | 0 | d1 hw = 0, d2 hw = 0; tail not supported | 0.571 | 0 | no |
| rossler | H2b(ii) | N | yes | 7.58e-05 (lo) | 2.63e-05 (pt) | 0.000128 | S hw = 5.69e-06 (estimate under H-geo) | 0 | 0.000234 | yes |
| rossler | H3c | U | no | 3.32e-05 (lo) | 3.7e-05 (lo) | 0.000107 | d1 hw = 2.4e-06, d2 hw = 2.68e-06; tail not supported | 0.49 | 0.000151 | no |

Class counts per system: lorenz63 N 1 / X 4 / U 1; rossler N 3 / X 0 / U 3; chua N 1 / X 2 / U 3.

Notes on specific rows:

- lorenz63 H3c: the verdict differs among the arms (pass at 15, inconclusive at 30, pass at 60), which alone makes it class X.
- chua H3c: A5's chosen K switches discretely, 8 at 15 and 5 at 30 and 60. This is an M7 structural switch, so the part is **U** (sizes d1 hw = 0.0549, d2 hw = 0.00028,
  tail not supported); the earlier tool order gave X (d1 = 0.18 >= 0.1, size S hw = 0.0554). An H-geo estimate is not meaningful across a discrete switch, so no S hw is given.
  The "tail not supported" wording is the plan's fixed label for class U; here the ratio conditions hold (d2/d1 = 0.005, r_A = 0.246) and the part is U because of the switch alone.
- **Endpoints and class N (corrected statement).** d1, d2 and S are maxima over {point, lower end, upper end}. Using the bootstrap endpoints can only raise d1, d2 and S relative to the
  point alone, so the endpoints can never produce N through S < 0.1 and never remove an X that the point alone gives through d1 >= 0.1 (the guarantee of M2).
  The ratio condition d2 <= d1/2 compares maxima that may come from different components, so the endpoints can move a part in either direction through it. Of the 7
  endpoint-limited parts (the class from the point alone differs), 6 move away from N and 1 toward it: toward X through d1: chua H2a(i) (N to X), lorenz63 H2b(ii) (N to X), lorenz63 H2a(i) (U to X);
  toward U through the ratio: chua H2a(ii) zero, lorenz63 H2a(ii) interior, rossler H2a(i) (each N to U); toward N through the ratio: rossler H2b(ii) (U to N: the lower-end change raises d1 to 7.6e-5, so that
  d2 = 2.6e-5 <= d1/2; on the point alone d2 is 0.93 of d1). Relative to infinitely many resamples, endpoint Monte Carlo noise (B = 500) raises d1, d2 and S in expectation but not in every realization. No floor was applied.
- Sensitivity of two N parts: rossler H2b(ii) and chua H2b(ii) are N although one component's own ratio d2/d1 exceeds 1/2 (the test uses the maxima). For rossler H2b(ii) suppose the point kept
  its ratio 0.93 at every later doubling: the bound on the error at 15 is 3.9e-4 hw against 0.1, and r_A = 0. The class N stands; this is a sensitivity reading, not a reclassification.
- rossler H2b(i) is U only because r_A = 0.571 exceeds 1/2 (d1 = d2 = 0: the QoI does not move). The ratio rests on single-digit counts: F(30 to 60) = 9 and F(60 to 120) = 4 (ratio 0.44), T 2.63 and 1.50 (ratio 0.571).
  Other rossler tail values: H3c F 7 to 2 (r_A = 0.490, from the T ratio 1.91 to 0.94); H2a and H2b(ii) F 2 to 0, so r_A = 0.
- rossler: 3 to 28 estimates per Part A group had a replaced state or nu at some level and are left out of the per-estimate ratios (counted in the probe file); lorenz63 and chua had none.
- Part A, share of estimates that move by more than 0.1 rho nu(30) from one doubling to the next (all groups pooled): lorenz63 2.3% (15 to 30), 1.2% (30 to 60), 0.52% (60 to 120); rossler 0.024%, 0.003%, 0.0013%; chua 0.34%, 0.082%, 0.032%.
- Estimates with c/rho^2 above the chi-square 0.999 quantile (core test split, 100000 estimates, at 15, 30, 60, 120 iterations): lorenz63 2916, 2299, 2072, 2042; rossler 106, 106, 106, 106 (not converging: the wrong-basin or misfit group); chua 405, 330, 282, 276. No estimate crossed from below to above at any doubling.
- Membership counts (M7; they move with the iteration count and are part of d1, not switches):

| count (arms 15 / 30 / 60) | lorenz63 | rossler | chua |
| --- | --- | --- | --- |
| H2a(i) eligible states | 327 / 332 / 333 | 463 / 463 / 463 | 314 / 314 / 314 |
| w* = 0 states | 155 / 154 / 154 | 137 / 137 / 137 | 137 / 136 / 136 |
| w* = 1 states | 15 / 14 / 14 | 2 / 2 / 2 | 6 / 6 / 6 |
| H2a(ii) interior part n | 330 / 332 / 332 | 361 / 361 / 361 | 357 / 358 / 358 |
| H2b(i) constant states | 23 / 23 / 23 | 21 / 21 / 21 | 13 / 14 / 14 |
| H2b(ii) zero-difference states | 49 / 48 / 48 | 38 / 38 / 38 | 40 / 39 / 39 |
| A5 chosen K | 8 / 8 / 8 | 3 / 3 / 3 | 8 / 5 / 5 |

## 4. Evidence that the comparison is paired and exact

- C0 (leaves that cannot read a PLP output, 35 patterns with a producer line each) bitwise equal across every pair of arms: 0 violations, over 6360, 6559 and 4745 differing leaves for the pairs 15-30, 15-60 and 30-60. All 35 patterns match at least one leaf (no coverage gap), including the robustness patterns.
- P0: the probe's pooled `lm_summary` and counts equal the stored ones exactly, at the 15, 30 and 60 arms, for all three systems (core oracle and evaluation kinds, and the sweep cells). Part A and the arms share commit, preset, seed id, CPU, `LPC_THREADS`, `XLA_FLAGS`, jax and jaxlib; the probe recorded each arm's start and end time.
- P1 (the 30-iteration run starts with the 15-iteration run, so the cost never rises and the accepted count never falls): 1404 exact comparisons of the stored `lm` summaries, 0 violations; per estimate, 0 violations in every group and doubling.
- Smoke checks before the pilot (K3): the flag at 15 and an absent flag give bitwise identical results (4555 leaves, provenance and wall-clock excluded).
- Review: independent review rounds 1 and 2 of the tool and the knob, and the independent checks of versions 1 and 2 against their data (every number, class, count, side reading and hash correct), are in `docs/agent/records/work/`. Version 3 has had one independent review, `docs/agent/records/work/WU-0005.6-rule-r-order-review.md` (R1 to R3, corrected here and in the tool); it is not a re-check of every number of this report against its data beyond the offline re-run described in section 0.

## 5. Limits

- One realization (DEV-0), one trajectory, one trained network per noise level; the numbers say nothing about between-realization variability.
- Pilot sizes (test 500, sweep 300, M = 200, evaluation draws 2) and B = 500 resamples; the full run has test 1000, sweep 1000 and B = 2000.
- The transfer column S x sqrt(n_full/n) is reported, never applied: a systematic iterative change does not shrink with n while the half-width does, so relative to hw it grows like sqrt(n). It rests on that scaling and on H-geo; a full-run 30/60 twin would remove the projection (open question O4).
- H-geo (each doubling after 60 at least halves the QoI change) cannot be verified from three levels; r_A (60 to 120 against 30 to 60, per estimate) is the supporting check.
- Part A covers the PLP inputs listed above; the V3 and V4 checks and the robustness variants were not re-estimated at the doubled budgets.
- Sizes: S hw is an estimate under H-geo when both ratio conditions hold (N, and X by its third bullet). In a class X part whose ratio condition (d2 <= d1/2 or r_A <= 1/2) fails, the lower estimate is **d1 hw** under monotone convergence (rule R), not S hw. U parts have no supported size; both d1 hw and d2 hw are given.
- The classes describe the size of a change under doubling, not a defect of the design.

## 6. What is not concluded

- No hypothesis (H1 to H3) is tested, and no verdict is given or changed here; the verdict changes quoted are those of the doubled runs on DEV-0.
- No statement about the confirmatory run, no promotion, no bound on the error of the full-size run.
- No claim that the 15-iteration design is wrong or right.
- No choice among the options below. (The order of a structural switch is settled: section 2.)

## 7. Options for the owner (O5), stated without a recommendation

Measured: the iterative error is not shown negligible (class X or U) for 13 of 18 parts; the owner can:

1. **Adopt a convention:** "PLP is the fixed 15-iteration Levenberg-Marquardt estimator" (like LPC.NV.1 for the discretization), so the estimand is defined with 15 iterations (v3 section 4 wording).
   Pros: no new run, no number of the study moves, the existing reference stays valid. Cons: the budget's iterative row reports the measured changes as sizes of the estimand, with "no" flags for 13 of 18 parts; the estimand then depends on an algorithm setting rather than the converged maximum-likelihood estimate.
2. **Raise the design value** (30 or 60 iterations; a v3 change).
   Pros: the estimand is closer to the converged estimate; the measured change 30 to 60 (d2) is smaller than 15 to 30 (d1) in 15 of the 18 parts (equal, both 0, in rossler H2b(i); larger in chua H2a(ii) interior and rossler H3c). Cons: it needs a new reference run and costs run time (the measured pilot walls were 1.8 times at 30 and 3.4 times at 60 on a shared machine, not a benchmark); every PLP number moves; the new value has its own tail to measure. This is the same statement as DEF-0027.
3. **Report and flag only:** keep 15 iterations, print the measured row with the "no" flags, state the limitation.
   Pros: no change of design, run or number. Cons: the iterative error stays unquantified in the confirmatory sense for the 13 parts, and readers of the primary results carry that limitation.

Related open items: the budget row text for WU-0008 (O6); the transfer of these DEV-0 numbers to the confirmatory run (O4). DEF-0028 (order of a structural switch) is resolved by the tool change on branch `wu/0005-6-rule-r-order`, pending independent review.

## 8. Files

Run directory (not tracked): `lpcstudy-wt/run/lm-post/runs/dev/wu0005-6/` with `k15`, `k30`, `k60` (each `pilot/results.json`), `probe-pilot/pilot/probe_pilot.json` (and `.npz`), `pilot-compare.txt` and `pilot-compare.json`
(the earlier tool, unchanged), and the new `pilot-compare-v3.txt` (sha256 `41c6e6487d7101145112ff05fcff0ae49aab5646916fecafeb73676971bbb4ce`) and `pilot-compare-v3.json`
(sha256 `6335581348c7f31a034b484c3fa77e1ae8863fddabc3d63d0bf43ddad826a644`), written by
`python tools/lm_doubling.py compare k15 k30 k60 --probe probe-pilot/pilot/probe_pilot.json --json pilot-compare-v3.json` with the tool of branch `wu/0005-6-rule-r-order`
(exit 0; no halt). The sha256 values of the earlier files and of versions 1 and 2 are in `docs/agent/records/results-manifest.md`; version 3 has its own line there.
