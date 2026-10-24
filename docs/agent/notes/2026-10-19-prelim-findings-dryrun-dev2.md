**DEVELOPMENT (DEV-2): not a hypothesis test** · **UNPROMOTED**
PRELIMINARY: internal to the owner and the student until promotion (QA.11, LPC.PC.13).

**DEVELOPMENT DRY RUN (WU-0020.3).** Every number below comes from a development seed. It rehearses the build and is not a result of the study.

# Preliminary findings for seed DEV-2

This document is built by `tools/findings_build.py` from the files named in §2. Every number in it is either read from one of those files (and listed in the trace file) or is a design constant of the v3 proposal that cites its section. The build computes no statistic and no verdict. Agents write the tables and this frame; the student writes §11. `check` re-renders the whole document and accepts a difference only in §11 and in dated lines appended to §9.

## 1. The question

The study asks whether four measurable local conditions of a chaotic system (recurrence, observability, instability and noise sensitivity) can decide, state by state, how much to trust an analog forecaster against a physics-based forecaster. The analog forecaster (CP) copies the future of the nearest past delay vector. The physics-based forecaster (PLP) estimates the hidden state and integrates the known equations. The two are blended with a weight w on CP. Three pre-registered primary hypotheses (H2a, H2b and H3c) are tested on Lorenz-63, Rössler and Chua's circuit. This document reports what the pre-registered analysis returned and adds no statistic, threshold, subgroup or recomputed verdict.

## 2. What was run

| Item | Value |
|---|---|
| Seed id | DEV-2 |
| Seed kind | development |
| Label | DEVELOPMENT (DEV-2): not a hypothesis test |
| Preset | full |
| Commit | 059dc84f7a958b82bedcea7a5f3ed7ff5a6e1091 |
| Freeze check | not applicable (development run) |
| Backend | cpu |
| LPC_THREADS | 8 |
| Dirty | no |
| Complete | yes |
| Wall seconds | 17028 |
| Start (UTC) | 2026-10-17T16:43:13+00:00 |
| End (UTC) | 2026-10-17T21:27:02+00:00 |
| SHA-256 of results.json | 5e2eaf6824c06f19c30f1d0fc9e06b663e7fa74281ec1fb3feaa98154a6dd752 |
| SHA-256 of RESULTS.md | 9ee9b8493c4df67acd18c2ae348cc8c230de36529decf469bdfbacb8c0f65b55 |
| Manifest hashes | none given (development) |
| Release reference | none (development dry run) |
| Cross-check seed id | DEV-2 |
| Cross-check backend | gpu |
| Cross-check SHA-256 | f0649d75eb9d341b210c75a05460ef7ef5f507f6fa157437d94c12ecf13e52b2 |
| compare_runs text | REF is the official run and NEW the cross-check (by realpath and realpath) |
| Cross-check commit | 6f1a8c854f35552546a3dd68f56b2b5de416f3de (same as official: no) |

Cross-check commits that differ from the official commit: 1 (a later commit is allowed only if `git diff --name-only` shows paths under docs/agent/records/ or the ledger alone; check: not checked (development run); both commits are shown above).

## 3. Validation gate (experiment E0) [PRE-REGISTERED]

Checks V1 to V7 of v3 §6, per system. A system whose gate failed is marked PROVISIONAL in every table and figure below. Its verdicts are still computed and shown (v3 §6, E0), and the failure is referred to the owner (DEC-0027, DEC-0031). V3 is reported, not checked.

| System | Check | Statistic | Value | Bar | Pass |
|---|---|---|---|---|---|
| lorenz63 | V1 | delay_jacobian_rel_err | 2.61e-09 | relative error < 10⁻⁴ | yes |
| lorenz63 | V1 | gain_rel_err | 1.61e-09 |  |  |
| lorenz63 | V2 | crlb_ratio_min | 0.870 | ratio in [0.8, 1.2] | yes |
| lorenz63 | V2 | crlb_ratio_max | 1.065 |  |  |
| lorenz63 | V3 | cp_median_vpt_lyapunov | 2.1 | reported, no bar | n/a |
| lorenz63 | V4 | median_half_width at the design M | 0.029 | median half-width ≤ 0.05 | yes |
| lorenz63 | V5 | km_max_abs_dev | 0.00583 | deviation < 0.01 | yes |
| lorenz63 | V6 | integrator_max_dev_sigma | 2.18e-05 | change < 10⁻³ σ_x | yes |
| lorenz63 | V7 | median_slope | 1.0008 | median slope and median δ/(ρν) at every ρ in [0.9, 1.1] | yes |
| lorenz63 | V7 | efficiency_median rho-0.5% | 1.0040 |  |  |
| lorenz63 | V7 | efficiency_median rho-1% | 1.0055 |  |  |
| lorenz63 | V7 | efficiency_median rho-2% | 1.0072 |  |  |
| lorenz63 | V7 | efficiency_median rho-5% | 1.0112 |  |  |
| lorenz63 | gate | gate_pass | | | yes |
| rossler | V1 | delay_jacobian_rel_err | 1.21e-09 | relative error < 10⁻⁴ | yes |
| rossler | V1 | gain_rel_err | 1.55e-09 |  |  |
| rossler | V2 | crlb_ratio_min | 0.856 | ratio in [0.8, 1.2] | yes |
| rossler | V2 | crlb_ratio_max | 1.067 |  |  |
| rossler | V3 | cp_median_vpt_lyapunov | 3.47 | reported, no bar | n/a |
| rossler | V4 | median_half_width at the design M | 0.035 | median half-width ≤ 0.05 | yes |
| rossler | V5 | km_max_abs_dev | 0.00583 | deviation < 0.01 | yes |
| rossler | V6 | integrator_max_dev_sigma | 3.06e-05 | change < 10⁻³ σ_x | yes |
| rossler | V7 | median_slope | 1.0000 | median slope and median δ/(ρν) at every ρ in [0.9, 1.1] | yes |
| rossler | V7 | efficiency_median rho-0.5% | 0.9967 |  |  |
| rossler | V7 | efficiency_median rho-1% | 0.9961 |  |  |
| rossler | V7 | efficiency_median rho-2% | 0.9977 |  |  |
| rossler | V7 | efficiency_median rho-5% | 0.9985 |  |  |
| rossler | gate | gate_pass | | | yes |
| chua | V1 | delay_jacobian_rel_err | 2.44e-09 | relative error < 10⁻⁴ | yes |
| chua | V1 | gain_rel_err | 1.59e-09 |  |  |
| chua | V2 | crlb_ratio_min | 0.858 | ratio in [0.8, 1.2] | yes |
| chua | V2 | crlb_ratio_max | 1.001 |  |  |
| chua | V3 | cp_median_vpt_lyapunov | 2.87 | reported, no bar | n/a |
| chua | V4 | median_half_width at the design M | 0.023 | median half-width ≤ 0.05 | yes |
| chua | V5 | km_max_abs_dev | 0.00583 | deviation < 0.01 | yes |
| chua | V6 | integrator_max_dev_sigma | 0.000334 | change < 10⁻³ σ_x | yes |
| chua | V7 | median_slope | 1.0001 | median slope and median δ/(ρν) at every ρ in [0.9, 1.1] | yes |
| chua | V7 | efficiency_median rho-0.5% | 1.0002 |  |  |
| chua | V7 | efficiency_median rho-1% | 1.0003 |  |  |
| chua | V7 | efficiency_median rho-2% | 1.0007 |  |  |
| chua | V7 | efficiency_median rho-5% | 1.0034 |  |  |
| chua | gate | gate_pass | | | yes |

> Every system passed the validation gate, so no result carries the PROVISIONAL mark.

## 4. Overall verdicts and the decision rule [PRE-REGISTERED]

Decision rule (v3 §7). A hypothesis is supported if it passes on all three systems, not supported if it fails on at least one system, and inconclusive otherwise, including when a system has no result. Requiring every system to pass is an intersection–union test, so the error of "supported" needs no further multiplicity correction. The error of "not supported" is not controlled this way: with 95% intervals it can reach about 7.3% over three systems (about 14% for H2c's two parts).

Each cell below is the stored verdict word. A "supported" verdict is always written "supported (preliminary, unpromoted)". The last column is the clip-sensitivity text copied from RESULTS.md.

| ID | Role | lorenz63 | rossler | chua | Overall | clip |
|---|---|---|---|---|---|---|
| H1a | secondary | inconclusive | inconclusive | fail | not supported | lorenz63: n/a; rossler: n/a; chua: n/a |
| H1b | secondary | pass | fail | pass | not supported | lorenz63: —; rossler: —; chua: — |
| H1c | secondary | fail | pass | inconclusive | not supported | lorenz63: invariant; rossler: invariant; chua: invariant |
| H1d | secondary | pass | pass | inconclusive | inconclusive | lorenz63: n/a; rossler: n/a; chua: n/a |
| Q-N | estimate | logit: reduces; indicator: substantial | logit: reduces; indicator: substantial | logit: reduces; indicator: substantial | estimate (read, no pass/fail); the stored per-system words are the logit part only | lorenz63: —; rossler: —; chua: — |
| H2a | primary | inconclusive | fail | fail | not supported | lorenz63: (i) invariant; (ii) —; rossler: (i) invariant; (ii) —; chua: (i) invariant; (ii) — |
| H2b | primary | pass | pass | inconclusive | inconclusive | lorenz63: —; rossler: —; chua: — |
| H2c | secondary | fail | fail | inconclusive | not supported | lorenz63: —; rossler: —; chua: — |
| H2d | secondary | inconclusive | pass | pass | inconclusive | lorenz63: —; rossler: —; chua: — |
| H2e | secondary | pass | pass | pass | supported (preliminary, unpromoted) | lorenz63: —; rossler: —; chua: — |
| gain_bound | reported | reported | reported | reported | reported (no pass/fail) | lorenz63: n/a; rossler: n/a; chua: n/a |
| H3a | secondary | inconclusive | inconclusive | pass | inconclusive | lorenz63: invariant; rossler: invariant; chua: invariant |
| H3b | secondary | inconclusive | pass | inconclusive | inconclusive | lorenz63: —; rossler: —; chua: — |
| H3c | primary | pass | pass | inconclusive | inconclusive | lorenz63: —; rossler: —; chua: — |

Q-N is read by the table of v3 §7, separately for each of its two parts (logit w* on the interior states, and the indicator of w* at zero), and is never pass or fail; the Q-N row shows both stored readings. v3 §2 and §7 read the two parts separately, but the stored overall word `verdicts.Q-N` collapses them to the logit part: its per-system words are lorenz63 reduces, rossler reduces, chua reduces. The hybrid's horizon gain is reported, v1 statistic, v3 screen pending.

Primary hypotheses, stored overall words:
- **H2a**: not supported. Fail on at least one system. The error of "not supported" is not controlled this way (§7), and this is not a statement about systems beyond the three studied. Pre-registered reading of a failure (v3 §7): instability enters the weight through anisotropic seeds, and the size of the departure measures how far real attractors are from the separation assumption. v3 §7 pre-registered this reading and it is not tested here. Parts whose stored word is fail: lorenz63: none; rossler: H2a(i) (fail); chua: H2a(i) (fail). Precision (v3 §7, DEF-0022): H2a's second part can be refuted but essentially cannot pass: that would need a partial correlation within about 0.01 of zero.
- **H2b**: inconclusive. No system failed and at least one could not be decided at this precision. Inconclusive does not say the effect is absent.
- **H3c**: inconclusive. No system failed and at least one could not be decided at this precision. Inconclusive does not say the effect is absent.

Secondary rows (v3 §2; each is read at the level 95% with no multiplicity adjustment, v3 §7):
- **H2c (secondary)**: not supported. Fail on at least one system. The error of "not supported" is not controlled this way (§7), and this is not a statement about systems beyond the three studied. Pre-registered reading (v3 §7), to be applied by the reader from the reported A4o − A2 interval: if H2c fails but A4o beats A2, the theory is right and the deployable seed estimates limit it.
- **H2e (secondary)**: supported (preliminary, unpromoted). Pass on all three systems in this preliminary, unpromoted run. The error of "supported" needs no further multiplicity correction (intersection–union).
- **H3a (secondary)**: inconclusive. No system failed and at least one could not be decided at this precision. Inconclusive does not say the effect is absent.

## 5. The three primary hypotheses (E1, E2, E4, E5) [PRE-REGISTERED]

Each row is one primary part on one system: the stored estimate, its interval at the level stored in the result (or the primary level of v3 §7 where the result stores none), the pass band of v3 §2 and the stored verdict. The two notes on every row are limitations stated before the run (v3 §8). Endpoints are rounded to four-digit precision for printing; every verdict uses the unrounded endpoints (v3 §7), so a printed edge can equal a band edge that the stored endpoint does not reach.

| System | Part | Estimate | Interval | Level | Band | Verdict | Notes |
|---|---|---|---|---|---|---|---|
| lorenz63 | H2a(i) | 0.1011 | [0.0793, 0.1326] | 0.9833 (design value, not stored) | interval below 0.1 (strict) | inconclusive | LM iteration error: not estimated; block-sensitive label: not computable for the sealed run |
| lorenz63 | H2a(ii) zero | -0.03464 | [-0.09541, 0.03384] | 0.9833 (design value, not stored) | interval inside (−0.1, 0.1) (strict) | pass | LM iteration error: not estimated; block-sensitive label: not computable for the sealed run |
| lorenz63 | H2a(ii) interior | 0.1895 | [0.0903, 0.2886] | 0.9833 (design value, not stored) | interval inside (−0.1, 0.1) (strict) | inconclusive | LM iteration error: not estimated; block-sensitive label: not computable for the sealed run |
| lorenz63 | H2b(i) | 0.1907 | [0.1411, 0.242] | 0.9833 (design value, not stored) | lower bound > 0 (strict) | pass | LM iteration error: not estimated; block-sensitive label: not computable for the sealed run |
| lorenz63 | H2b(ii) | 0.08514 | [0.06243, 0.1102] | 0.9833 | lower bound > 0 (strict) | pass | LM iteration error: not estimated; block-sensitive label: not computable for the sealed run |
| lorenz63 | H3c | 0.7455 | [0.5661, 0.9016] | 0.9833 | upper bound ≤ 1.05 (closed) | pass | LM iteration error: not estimated; block-sensitive label: not computable for the sealed run |
| rossler | H2a(i) | 0.2917 | [0.2455, 0.3154] | 0.9833 (design value, not stored) | interval below 0.1 (strict) | fail | LM iteration error: not estimated; block-sensitive label: not computable for the sealed run |
| rossler | H2a(ii) zero | -0.05337 | [-0.1304, 0.0293] | 0.9833 (design value, not stored) | interval inside (−0.1, 0.1) (strict) | inconclusive | LM iteration error: not estimated; block-sensitive label: not computable for the sealed run |
| rossler | H2a(ii) interior | 0.02144 | [-0.06819, 0.1089] | 0.9833 (design value, not stored) | interval inside (−0.1, 0.1) (strict) | inconclusive | LM iteration error: not estimated; block-sensitive label: not computable for the sealed run |
| rossler | H2b(i) | 0.1405 | [0.08557, 0.192] | 0.9833 (design value, not stored) | lower bound > 0 (strict) | pass | LM iteration error: not estimated; block-sensitive label: not computable for the sealed run |
| rossler | H2b(ii) | 0.04943 | [0.02753, 0.07171] | 0.9833 | lower bound > 0 (strict) | pass | LM iteration error: not estimated; block-sensitive label: not computable for the sealed run |
| rossler | H3c | 0.9677 | [0.9282, 1.014] | 0.9833 | upper bound ≤ 1.05 (closed) | pass | LM iteration error: not estimated; block-sensitive label: not computable for the sealed run |
| chua | H2a(i) | 0.1561 | [0.1253, 0.1849] | 0.9833 (design value, not stored) | interval below 0.1 (strict) | fail | LM iteration error: not estimated; block-sensitive label: not computable for the sealed run |
| chua | H2a(ii) zero | -0.07083 | [-0.1494, 0.007693] | 0.9833 (design value, not stored) | interval inside (−0.1, 0.1) (strict) | inconclusive | LM iteration error: not estimated; block-sensitive label: not computable for the sealed run |
| chua | H2a(ii) interior | 0.2236 | [0.08551, 0.3466] | 0.9833 (design value, not stored) | interval inside (−0.1, 0.1) (strict) | inconclusive | LM iteration error: not estimated; block-sensitive label: not computable for the sealed run |
| chua | H2b(i) | 0.2672 | [0.2122, 0.3186] | 0.9833 (design value, not stored) | lower bound > 0 (strict) | pass | LM iteration error: not estimated; block-sensitive label: not computable for the sealed run |
| chua | H2b(ii) | 0.008392 | [-0.01395, 0.03061] | 0.9833 | lower bound > 0 (strict) | inconclusive | LM iteration error: not estimated; block-sensitive label: not computable for the sealed run |
| chua | H3c | 0.9849 | [0.9364, 1.058] | 0.9833 | upper bound ≤ 1.05 (closed) | inconclusive | LM iteration error: not estimated; block-sensitive label: not computable for the sealed run |

Level cells that show a design value: 12.

Iterative error of the PLP estimator: not estimated for this run. Development evidence is in docs/study/lm_doubling_dev0_report_v3.md and in the limitation on iterative error (DEF-0027) in §10.

![F1](2026-10-19-prelim-findings-dryrun-dev2.figures/F1_primary.png)

*Figure F1 (experiments E1, E2, E4 and E5; v3 identifiers H2a, H2b and H3c). One panel per primary part, one row per system. Each marker is the stored estimate and each bar its moving-block bootstrap percentile interval (blocks of 5 consecutive test states, 2000 resamples) at level 98.33% (each panel states its level). The shaded region is the pass band of v3 §2. Marker shape and text give the stored verdict: filled circle pass, cross fail, open diamond inconclusive. A system that failed the validation gate is marked PROVISIONAL.*

Cells written "not recorded" so far: 0. Null leaves written "not computed" so far: 0. The full list is in Appendix C.

## 6. Secondary hypotheses, Q-N, H3a counts and the gain bound (E2 to E5) [PRE-REGISTERED]

Endpoints are rounded to four-digit precision for printing; every verdict uses the unrounded endpoints (v3 §7). The H2c row A4o minus A2 is reported with its interval and carries no verdict (v3 §2).

| System | Part | Estimate | Interval | Level | Band | Verdict |
|---|---|---|---|---|---|---|
| lorenz63 | H1a rho-1% | 1.204 | [1.064, 1.349] | 0.9500 | interval inside [0.75, 1.25] (closed) | inconclusive |
| lorenz63 | H1a rho-2% | 1.254 | [1.08, 1.419] | 0.9500 | interval inside [0.75, 1.25] (closed) | inconclusive |
| lorenz63 | H1b PLP | 0.874 | [0.8401, 0.9152] | 0.95 (design value, not stored) | interval inside [0.8, 1.2] (closed) | pass |
| lorenz63 | H1c PLP | 0.5652 | [0.5015, 0.6152] | 0.95 (design value, not stored) | interval inside [0.8, 1.25] (closed) | fail |
| lorenz63 | H1d analog seed | 0.7759 | [0.7451, 0.8028] | 0.9500 | lower bound ≥ 0.7 (closed) | pass |
| lorenz63 | H1d estimation seed | 0.9127 | [0.8839, 0.9392] | 0.9500 | lower bound ≥ 0.7 (closed) | pass |
| lorenz63 | H1d growth | 0.9857 | [0.9792, 0.991] | 0.9500 | lower bound ≥ 0.7 (closed) | pass |
| lorenz63 | H2c A4 - A2 | 0.01523 | [0.005794, 0.02677] | 0.95 (design value, not stored) | upper bound < 0 (strict) | fail |
| lorenz63 | H2c A4 - A1 | -0.01038 | [-0.01983, -0.003257] | 0.95 (design value, not stored) | upper bound < 0 (strict) | pass |
| lorenz63 | H2c A4o - A2 (reported) | -0.0255 | [-0.03815, -0.01414] | 0.9500 | reported with its interval, no verdict (v3 §2 H2c) | reported |
| lorenz63 | H2d | 0.1684 | [-0.009443, 0.5028] | 0.95 (design value, not stored) | upper bound ≤ 0.10 (closed) | inconclusive |
| lorenz63 | H2e rho-1% | 0.3554 | [0.335, 0.3764] | 0.9500 | lower bound > 0 (strict) | pass |
| lorenz63 | H2e rho-2% | 0.3124 | [0.2845, 0.341] | 0.9500 | lower bound > 0 (strict) | pass |
| lorenz63 | H3b weight tree | 0.1072 | [0, 0.8625] | 0.9500 | interval inside [0, 0.2) (closed at 0, open at 0.2) | inconclusive |
| lorenz63 | H3b horizon tree D | -0.2192 | [-0.4297, 0.2398] | 0.9500 | lower bound > 0 (strict) | inconclusive |
| rossler | H1a rho-1% | 0.9209 | [0.8622, 0.9942] | 0.9500 | interval inside [0.75, 1.25] (closed) | pass |
| rossler | H1a rho-2% | 0.786 | [0.6999, 0.8695] | 0.9500 | interval inside [0.75, 1.25] (closed) | inconclusive |
| rossler | H1b PLP | 0.6705 | [0.6303, 0.7089] | 0.95 (design value, not stored) | interval inside [0.8, 1.2] (closed) | fail |
| rossler | H1c PLP | 0.986 | [0.9397, 1.029] | 0.95 (design value, not stored) | interval inside [0.8, 1.25] (closed) | pass |
| rossler | H1d analog seed | 0.7697 | [0.7375, 0.7965] | 0.9500 | lower bound ≥ 0.7 (closed) | pass |
| rossler | H1d estimation seed | 0.9588 | [0.9505, 0.9652] | 0.9500 | lower bound ≥ 0.7 (closed) | pass |
| rossler | H1d growth | 0.9925 | [0.99, 0.9945] | 0.9500 | lower bound ≥ 0.7 (closed) | pass |
| rossler | H2c A4 - A2 | 3.259e-05 | [3.301e-06, 5.999e-05] | 0.95 (design value, not stored) | upper bound < 0 (strict) | fail |
| rossler | H2c A4 - A1 | 1.877e-05 | [-1.654e-05, 5.114e-05] | 0.95 (design value, not stored) | upper bound < 0 (strict) | inconclusive |
| rossler | H2c A4o - A2 (reported) | -5.895e-05 | [-9.242e-05, -2.812e-05] | 0.9500 | reported with its interval, no verdict (v3 §2 H2c) | reported |
| rossler | H2d | 0.001396 | [-0.05371, 0.04521] | 0.95 (design value, not stored) | upper bound ≤ 0.10 (closed) | pass |
| rossler | H2e rho-1% | 0.3537 | [0.3338, 0.3775] | 0.9500 | lower bound > 0 (strict) | pass |
| rossler | H2e rho-2% | 0.2515 | [0.2263, 0.2817] | 0.9500 | lower bound > 0 (strict) | pass |
| rossler | H3b weight tree | 0.07115 | [0, 0.1846] | 0.9500 | interval inside [0, 0.2) (closed at 0, open at 0.2) | pass |
| rossler | H3b horizon tree D | 0.3903 | [0.1772, 0.5221] | 0.9500 | lower bound > 0 (strict) | pass |
| chua | H1a rho-1% | 0.7458 | [0.6611, 0.8214] | 0.9500 | interval inside [0.75, 1.25] (closed) | inconclusive |
| chua | H1a rho-2% | 0.5827 | [0.4981, 0.6783] | 0.9500 | interval inside [0.75, 1.25] (closed) | fail |
| chua | H1b PLP | 1.054 | [1.027, 1.08] | 0.95 (design value, not stored) | interval inside [0.8, 1.2] (closed) | pass |
| chua | H1c PLP | 0.7643 | [0.7183, 0.8205] | 0.95 (design value, not stored) | interval inside [0.8, 1.25] (closed) | inconclusive |
| chua | H1d analog seed | 0.7339 | [0.6998, 0.7643] | 0.9500 | lower bound ≥ 0.7 (closed) | inconclusive |
| chua | H1d estimation seed | 0.9454 | [0.918, 0.9677] | 0.9500 | lower bound ≥ 0.7 (closed) | pass |
| chua | H1d growth | 0.9756 | [0.9658, 0.9834] | 0.9500 | lower bound ≥ 0.7 (closed) | pass |
| chua | H2c A4 - A2 | 0.0003368 | [-0.00102, 0.002111] | 0.95 (design value, not stored) | upper bound < 0 (strict) | inconclusive |
| chua | H2c A4 - A1 | -0.00108 | [-0.002596, 0.0001691] | 0.95 (design value, not stored) | upper bound < 0 (strict) | inconclusive |
| chua | H2c A4o - A2 (reported) | -0.005324 | [-0.01291, -8.391e-05] | 0.9500 | reported with its interval, no verdict (v3 §2 H2c) | reported |
| chua | H2d | -0.01179 | [-0.06308, 0.05348] | 0.95 (design value, not stored) | upper bound ≤ 0.10 (closed) | pass |
| chua | H2e rho-1% | 0.3095 | [0.283, 0.3312] | 0.9500 | lower bound > 0 (strict) | pass |
| chua | H2e rho-2% | 0.2192 | [0.1923, 0.241] | 0.9500 | lower bound > 0 (strict) | pass |
| chua | H3b weight tree | 0.4676 | [0, 0.5301] | 0.9500 | interval inside [0, 0.2) (closed at 0, open at 0.2) | inconclusive |
| chua | H3b horizon tree D | 0.8076 | [0.6553, 0.8935] | 0.9500 | lower bound > 0 (strict) | pass |

Level cells that show a design value: 15.

The band of the H3b weight tree is [0, 0.2): closed at 0 and open at 0.2 (v3 §2). An interval whose lower bound is exactly 0 is therefore inside the band, and the verdict words in the table are the stored ones.

Q-N, oracle values, read by the table of v3 §7 (a reading, never pass or fail):

| System | Part | Estimate | Interval | Level | Band | Verdict |
|---|---|---|---|---|---|---|
| lorenz63 | Q-N oracle logit w* | -0.009238 | [-0.03016, 0.01182] | 0.95 (design value, not stored) | read by the table of v3 §7 (edges 0 and 0.05) | reduces |
| lorenz63 | Q-N oracle zero indicator | 0.2342 | [0.1815, 0.2905] | 0.95 (design value, not stored) | read by the table of v3 §7 (edges 0 and 0.05) | substantial |
| rossler | Q-N oracle logit w* | 0.01192 | [-0.02354, 0.04698] | 0.95 (design value, not stored) | read by the table of v3 §7 (edges 0 and 0.05) | reduces |
| rossler | Q-N oracle zero indicator | 0.1298 | [0.07593, 0.18] | 0.95 (design value, not stored) | read by the table of v3 §7 (edges 0 and 0.05) | substantial |
| chua | Q-N oracle logit w* | -0.004859 | [-0.03977, 0.02341] | 0.95 (design value, not stored) | read by the table of v3 §7 (edges 0 and 0.05) | reduces |
| chua | Q-N oracle zero indicator | 0.09748 | [0.05075, 0.1437] | 0.95 (design value, not stored) | read by the table of v3 §7 (edges 0 and 0.05) | substantial |

Level cells that show a design value: 6.

H3a: events and censored states per regime, with the stored Holm-adjusted log-rank p-values (DEF-0018). H3a cannot fail, since no equivalence margin is set (v3 §2).

| System | Regime | States | Events | Censored |
|---|---|---|---|---|
| lorenz63 | r0 | 25 | not recorded | not recorded |
| lorenz63 | r1 | 21 | not recorded | not recorded |
| lorenz63 | r2 | 196 | not recorded | not recorded |
| lorenz63 | r3 | 234 | not recorded | not recorded |
| lorenz63 | r4 | 147 | not recorded | not recorded |
| lorenz63 | r5 | 64 | not recorded | not recorded |
| lorenz63 | r6 | 127 | not recorded | not recorded |
| lorenz63 | r7 | 186 | not recorded | not recorded |
| rossler | r0 | 170 | not recorded | not recorded |
| rossler | r1 | 462 | not recorded | not recorded |
| rossler | r2 | 368 | not recorded | not recorded |
| chua | r0 | 405 | not recorded | not recorded |
| chua | r1 | 387 | not recorded | not recorded |
| chua | r2 | 170 | not recorded | not recorded |
| chua | r3 | 38 | not recorded | not recorded |

| System | Pair (a, b) | Raw p | Holm p |
|---|---|---|---|
| lorenz63 | 1, 0 | 0.373 | 0.684 |
| lorenz63 | 0, 7 | 2.7e-32 | 1.89e-31 |
| lorenz63 | 7, 3 | 0.0738 | 0.369 |
| lorenz63 | 3, 6 | 0.114 | 0.454 |
| lorenz63 | 6, 2 | 0.342 | 0.684 |
| lorenz63 | 2, 4 | 0.000247 | 0.00148 |
| lorenz63 | 4, 5 | 0.19 | 0.57 |
| rossler | 1, 2 | 0.204 | 0.204 |
| rossler | 2, 0 | 2.38e-17 | 4.75e-17 |
| chua | 3, 2 | 6.71e-05 | 6.71e-05 |
| chua | 2, 1 | 2.19e-18 | 6.58e-18 |
| chua | 1, 0 | 9.3e-08 | 1.86e-07 |

Cells written "not recorded" so far: 30. Null leaves written "not computed" so far: 0. The full list is in Appendix C.

Hybrid horizon gain against the P1 bound (reported, v1 statistic, v3 screen pending):

| System | fraction_within_bound | n_states | n_total_states | median_gain_lyapunov | max_gain_lyapunov |
|---|---|---|---|---|---|
| lorenz63 | 0.950 | 654 | 1000 | 0 | 2.3 |
| rossler | 0.880 | 676 | 1000 | 0 | 3.2 |
| chua | 0.932 | 644 | 1000 | 0 | 2.07 |

Reported quantities that carry no verdict (v3 §2 lists each as reported; each value is read from its stored leaf, and no verdict depends on it):

| System | Quantity | Value | Interval |
|---|---|---|---|
| lorenz63 | H2a: test states excluded from part (i) (fewer than two leading horizons) | 288 |  |
| lorenz63 | H2a: test states eligible for part (i) | 712 |  |
| lorenz63 | H2a: median range of w*, span of horizons {1, 2} LT | 0.05504 |  |
| lorenz63 | H2a: states in the span {1, 2} LT | 564 |  |
| lorenz63 | H2a: median range of w*, span of horizons {1, 2, 4} LT | 0.5111 |  |
| lorenz63 | H2a: states in the span {1, 2, 4} LT | 148 |  |
| lorenz63 | H2a: complete-case {1, 2, 4} LT range (a sensitivity), median and interval | 0.5111 | [0.3975, 0.6046] |
| lorenz63 | H2a: states in the complete-case set | 148 |  |
| lorenz63 | H2a: test states with w* = 0 | 292 |  |
| lorenz63 | H2a: test states with w* = 1 | 29 |  |
| lorenz63 | H1a: floor f (r.m.s.) at rho 1% | 0.02777 |  |
| lorenz63 | H1a: floor f (r.m.s.) at rho 2% | 0.05252 |  |
| lorenz63 | H1c: CP median ratio and interval (reported; the tested part is PLP) | 0.5078 | [0.4729, 0.5465] |
| lorenz63 | H1d: N-hat Spearman correlation and interval (reported, not tested) | 0.6703 | [0.6261, 0.7151] |
| lorenz63 | H3b: stability fraction (share of resamples with D > 0) | 0.198 |  |
| rossler | H2a: test states excluded from part (i) (fewer than two leading horizons) | 65 |  |
| rossler | H2a: test states eligible for part (i) | 935 |  |
| rossler | H2a: median range of w*, span of horizons {1, 2} LT | 0.09402 |  |
| rossler | H2a: states in the span {1, 2} LT | 273 |  |
| rossler | H2a: median range of w*, span of horizons {1, 2, 4} LT | 0.3703 |  |
| rossler | H2a: states in the span {1, 2, 4} LT | 662 |  |
| rossler | H2a: complete-case {1, 2, 4} LT range (a sensitivity), median and interval | 0.3703 | [0.3309, 0.4135] |
| rossler | H2a: states in the complete-case set | 662 |  |
| rossler | H2a: test states with w* = 0 | 293 |  |
| rossler | H2a: test states with w* = 1 | 1 |  |
| rossler | H1a: floor f (r.m.s.) at rho 1% | 0.01614 |  |
| rossler | H1a: floor f (r.m.s.) at rho 2% | 0.0316 |  |
| rossler | H1c: CP median ratio and interval (reported; the tested part is PLP) | 1.04 | [0.9917, 1.082] |
| rossler | H1d: N-hat Spearman correlation and interval (reported, not tested) | 0.5779 | [0.5277, 0.6269] |
| rossler | H3b: stability fraction (share of resamples with D > 0) | 1 |  |
| chua | H2a: test states excluded from part (i) (fewer than two leading horizons) | 338 |  |
| chua | H2a: test states eligible for part (i) | 662 |  |
| chua | H2a: median range of w*, span of horizons {1, 2} LT | 0.08287 |  |
| chua | H2a: states in the span {1, 2} LT | 418 |  |
| chua | H2a: median range of w*, span of horizons {1, 2, 4} LT | 0.3727 |  |
| chua | H2a: states in the span {1, 2, 4} LT | 244 |  |
| chua | H2a: complete-case {1, 2, 4} LT range (a sensitivity), median and interval | 0.3727 | [0.2912, 0.4365] |
| chua | H2a: states in the complete-case set | 244 |  |
| chua | H2a: test states with w* = 0 | 324 |  |
| chua | H2a: test states with w* = 1 | 15 |  |
| chua | H1a: floor f (r.m.s.) at rho 1% | 0.03698 |  |
| chua | H1a: floor f (r.m.s.) at rho 2% | 0.06972 |  |
| chua | H1c: CP median ratio and interval (reported; the tested part is PLP) | 0.8128 | [0.7461, 0.8628] |
| chua | H1d: N-hat Spearman correlation and interval (reported, not tested) | 0.6958 | [0.6548, 0.7364] |
| chua | H3b: stability fraction (share of resamples with D > 0) | 1 |  |

The H2c part labelled A4 - A1 is A4 minus the better single forecaster, chosen on the calibration split (v3 §2 H2c). The stored best_single is lorenz63 A1, rossler A1, chua A1; A1 is PLP alone (w = 0).

![F2](2026-10-19-prelim-findings-dryrun-dev2.figures/F2_secondary.png)

*Figure F2 (experiments E2 to E5; v3 identifiers H1a to H1d, H2c to H2e, H3b and Q-N). One panel per secondary part, one row per system. Each marker is the stored estimate and each bar its moving-block bootstrap percentile interval (blocks of 5 consecutive test states, 2000 resamples; H3b resamples construction states) at the level stated in each panel (95% unless the result stores another). The shaded region is the pass band of v3 §2. For Q-N no band is shaded: dashed lines mark the reading edges of v3 §7. Each panel states its level, and the three H2c panels are drawn one per system because the scales differ. Marker shape and text give the stored verdict or reading: filled circle pass, cross fail, open diamond inconclusive, square a Q-N reading (both readings, the logit part and the indicator part) or a quantity that is reported with no verdict. A system that failed the validation gate is marked PROVISIONAL.*

Cells written "not recorded" so far: 30. Null leaves written "not computed" so far: 0. The full list is in Appendix C.

## 7. Handling counters (nothing is silent) [DIAGNOSTIC]

The handling counters of the main systems (PRIME.4). Zero counters are printed, never omitted. The counters of the robustness variants are not listed here: they are in `handling.robustness` of results.json. All nonzero result counts are listed in the Handling section of RESULTS.md; the floors, exclusions and screen-outs among them are read from their stored leaves in the table after the counters.

| Counter | Total | lorenz63 | rossler | chua |
|---|---|---|---|---|
| invariant_mean_replacements | 425 | 0 | 425 | 0 |
| nu_replacements | 425 | 0 | 425 | 0 |
| error_clips | 0 | 0 | 0 | 0 |
| error_clips_cp | 0 | 0 | 0 | 0 |
| error_clips_plp | 0 | 0 | 0 | 0 |
| error_clips_nonfinite | 0 | 0 | 0 | 0 |
| error_clips_plp_href | 0 | 0 | 0 | 0 |
| error_clips_nonfinite_href | 0 | 0 | 0 | 0 |
| gain_replacements | 0 | 0 | 0 | 0 |
| gain_floor | 0 | 0 | 0 | 0 |
| zero_variance_corr | 505565 | 254220 | 104910 | 146435 |
| zero_variance_corr_cp | 505565 | 254220 | 104910 | 146435 |
| zero_variance_corr_plp | 0 | 0 | 0 | 0 |
| curvature_floor | 0 | 0 | 0 | 0 |
| decisive_floor | 0 | 0 | 0 | 0 |
| lm_nonfinite_cost | 716 | 24 | 692 | 0 |
| lm_nonfinite_jacobian | 425 | 0 | 425 | 0 |
| local_dim_zero_distance | 0 | 0 | 0 | 0 |
| oracle_gain_floor | 0 | 0 | 0 | 0 |
| oracle_nonfinite | 0 | 0 | 0 | 0 |
| nu_cap_clips | 460 | 154 | 160 | 146 |
| closed_form_floor_a4 | 0 | 0 | 0 | 0 |
| closed_form_floor_a4o | 0 | 0 | 0 | 0 |
| empty_regime_fallback | 0 | 0 | 0 | 0 |
| empty_regime_fallback_chosen | 0 | 0 | 0 | 0 |
| pooled_curvature_floor | 0 | 0 | 0 | 0 |
| regime_target_constant | 0 | 0 | 0 | 0 |

Failed robustness variants: 0. Robustness variants not run (skipped_variants): not recorded.

| Result count (leaf of each system) | lorenz63 | rossler | chua |
|---|---|---|---|
| H1b/CP/n_floored | 101 | 93 | 111 |
| H2a/n_excluded_states | 288 | 65 | 338 |
| H1c/PLP/n_ineligible_states | 177 | 40 | 152 |
| H1c/CP/n_ineligible_states | 150 | 45 | 155 |
| H2b/noise/n_constant_states | 52 | 71 | 44 |
| gain_bound/n_screened_out/growth_nonpositive | 145 | 40 | 148 |
| gain_bound/n_screened_out/negative_covariance | 242 | 301 | 245 |
| gain_bound/n_screened_out/censored_single_forecaster | 0 | 1 | 2 |

## 8. GPU cross-check (information only) [CROSS-CHECK: information only]

The GPU run of the same seed is a cross-check, never the result (v3 §9 item 3, DEC-0031). The z value uses the interval arm facing away from the other estimate, and a part disagrees if it exceeds the bound 3.4. The numbers in the first table are copied from the compare_runs text. The hw ratio column is the half-width of the cross-check (GPU) interval divided by the half-width of the official (CPU) interval (the column hw1/hw0 of the compare_runs text, whose REF is the official run and NEW the cross-check), so a value above 1 means the GPU interval is wider.

| System | Part | d | z_sym (information) | z_away (governs) | hw ratio | Status |
|---|---|---|---|---|---|---|
| lorenz63 | H2a(i) | 0.0179 | 1.11 | 1.06 | 1.045 | ok |
| lorenz63 | H2a(ii) zero | 0.0269 | 0.64 | 0.65 | 1.196 | ok |
| lorenz63 | H2a(ii) interior | 0.0299 | 0.53 | 0.54 | 0.912 | ok |
| lorenz63 | H2b(i) | 0.0399 | 1.34 | 1.35 | 0.996 | ok |
| lorenz63 | H2b(ii) | -0.0090 | 0.61 | 0.60 | 1.076 | ok |
| lorenz63 | H3c | -0.0312 | 0.28 | 0.29 | 1.223 | ok |
| rossler | H2a(i) | -0.0047 | 0.22 | 0.26 | 1.103 | ok |
| rossler | H2a(ii) zero | -0.0103 | 0.21 | 0.21 | 1.033 | ok |
| rossler | H2a(ii) interior | -0.0004 | 0.01 | 0.01 | 1.262 | ok |
| rossler | H2b(i) | 0.0710 | 2.32 | 2.26 | 0.948 | ok |
| rossler | H2b(ii) | 0.0073 | 0.57 | 0.56 | 0.956 | ok |
| rossler | H3c | -0.0162 | 0.62 | 0.62 | 1.043 | ok |
| chua | H2a(i) | 0.0266 | 1.19 | 1.07 | 1.488 | ok |
| chua | H2a(ii) zero | 0.0217 | 0.46 | 0.46 | 1.038 | ok |
| chua | H2a(ii) interior | 0.0277 | 0.41 | 0.40 | 0.725 | ok |
| chua | H2b(i) | -0.0350 | 1.12 | 1.13 | 0.988 | ok |
| chua | H2b(ii) | 0.0233 | 1.69 | 1.67 | 1.101 | ok |
| chua | H3c | -0.0174 | 0.44 | 0.42 | 1.178 | ok |

Parts computed 18 of 18; sum of z squared (away) 15.77; largest z (away) 2.26; failing parts 0 (bound 3.4).

Stored verdict words that differ between the official (CPU) and the cross-check (GPU) results files, read from the two files as a string comparison of the stored words (nothing is recomputed). Overall rows: 13. Rows per system: 28. The compare_runs text prints a limited number of leaf lines (20 lines against 52 verdict-type leaves counted, which also include boolean flags of the verdict rows); the tables below are read from the results files and list every string verdict word that differs.

| Overall leaf | Official (CPU) | Cross-check (GPU) |
|---|---|---|
| H2a/by_system/lorenz63 | inconclusive | fail |
| H2b/by_system/chua | inconclusive | pass |
| H2b/verdict | inconclusive | supported (preliminary, unpromoted) |
| H3c/by_system/chua | inconclusive | pass |
| H3c/verdict | inconclusive | supported (preliminary, unpromoted) |
| H1a/by_system/chua | fail | inconclusive |
| H1a/by_system/lorenz63 | inconclusive | pass |
| H1a/verdict | not supported | inconclusive |
| H1b/by_system/lorenz63 | pass | inconclusive |
| H1c/by_system/chua | inconclusive | fail |
| Q-N/by_system/rossler | reduces | undetermined |
| H2d/by_system/lorenz63 | inconclusive | fail |
| H2d/verdict | inconclusive | not supported |

| System | Leaf | Official (CPU) | Cross-check (GPU) |
|---|---|---|---|
| lorenz63 | H2a/part_ii/interior/verdict | inconclusive | fail |
| lorenz63 | H2a/part_ii_verdict | inconclusive | fail |
| lorenz63 | H2a/verdict | inconclusive | fail |
| lorenz63 | H1a/by_noise/0.01/verdict | inconclusive | pass |
| lorenz63 | H1a/by_noise/0.02/verdict | inconclusive | pass |
| lorenz63 | H1a/verdict | inconclusive | pass |
| lorenz63 | H1b/verdict | pass | inconclusive |
| lorenz63 | H2d/verdict | inconclusive | fail |
| lorenz63 | Q-N/deployable/logit_w_interior/reading | reduces | undetermined |
| lorenz63 | clip_sensitivity/by_hypothesis/H1b/parts/PLP/verdict_2L | pass | inconclusive |
| lorenz63 | clip_sensitivity/by_hypothesis/H2a/parts/interior/verdict_2L | inconclusive | fail |
| lorenz63 | clip_sensitivity/by_hypothesis/H2d/parts/A4_over_A3/verdict_2L | inconclusive | fail |
| rossler | Q-N/deployable/logit_w_interior/reading | reduces | substantial |
| rossler | Q-N/oracle/logit_w_interior/reading | reduces | undetermined |
| chua | H2a/part_ii/interior/verdict | inconclusive | fail |
| chua | H2a/part_ii_verdict | inconclusive | fail |
| chua | H2b/library_change/verdict | inconclusive | pass |
| chua | H2b/verdict | inconclusive | pass |
| chua | H3c/verdict | inconclusive | pass |
| chua | H1a/by_noise/0.01/verdict | inconclusive | pass |
| chua | H1a/by_noise/0.02/verdict | fail | inconclusive |
| chua | H1a/verdict | fail | inconclusive |
| chua | H1c/PLP/verdict | inconclusive | fail |
| chua | H1c/verdict | inconclusive | fail |
| chua | Q-N/deployable/logit_w_interior/reading | reduces | undetermined |
| chua | clip_sensitivity/by_hypothesis/H2a/parts/interior/verdict_2L | inconclusive | fail |
| chua | clip_sensitivity/by_hypothesis/H2b/parts/library_change/verdict_2L | inconclusive | pass |
| chua | clip_sensitivity/by_hypothesis/H3c/parts/A5_over_A4/verdict_2L | inconclusive | pass |

H3a regimes per system (the stored chosen_K of each run). When the numbers differ, the regime-indexed H3a leaves of the longer list have no counterpart in the other run; compare_runs lists them with no per-leaf rule.

| System | Regimes, official (CPU) | Regimes, cross-check (GPU) |
|---|---|---|
| lorenz63 | 8 | 8 |
| rossler | 3 | 4 |
| chua | 4 | 4 |

No primary part exceeds the bound: failing parts 0, largest z (away) 2.26, bound 3.4.

Verdict-type leaves that differ between the two runs: 52. The stored verdict words among them are in the tables above; the official words stand.

GPU validation gate, stored gate_pass: lorenz63 yes, rossler yes, chua no. The GPU validation gate did not pass on chua, or its result is not recorded there. This is reported only (DEC-0031).

compare_runs result: PASS (exit 0). What a TD pass does not mean: it does not reproduce verdicts or the gate outcome. All of this is reported only and changes no verdict (DEC-0031).

![F3](2026-10-19-prelim-findings-dryrun-dev2.figures/F3_crosscheck.png)

*Figure F3 (cross-check, information only; v3 §9 item 3, DEC-0031; experiments E1, E2, E4 and E5). For each of the 18 primary parts, the away-arm z value comparing the official CPU run with the GPU run of the same seed, from the compare_runs text (interval procedure: the 98.33% moving-block bootstrap intervals of the two runs). The dashed line is the bound 3.4. A row would name a failed GPU validation gate and a PROVISIONAL official system if there were one; the footer states the GPU gate of each system. This figure changes no verdict.*

## 9. Reproducibility

Regeneration of the official run (WU-0016, v3 §9 item 4): each dated line below is appended after the event it reports.

## 10. Limitations

All items of v3 §8 apply, plus the registered deficiencies and rulings listed here.

- Deployable closed form: the deployable closed form A4 depends almost only on recurrence distance in noise units.
- Exact model: with an exact model, PLP usually wins after one Lyapunov time.
- Deployable features carry little of the information in the exact ones.
- N̂ measures retrieval sensitivity at the observed (noisy) query, not at the true one, so it is reported, not tested (DEF-0008).
- The seed × amplifier test (H1b) assumes isotropic seeds and is applied to PLP only.
- Same attractors, fresh seeds: this is not a new set of systems.
- Interval coverage (DEF-0020): The block-5 percentile intervals undercover at these sample sizes: about 0.938 to 0.947 at 95% with independent states and 0.923 to 0.931 at lag-1 autocorrelation 0.3, which adds about 1 to 2 percentage points of false-verdict probability under dependence (v3 §8; DEF-0020). The pre-registered intervals and block length are kept.
- Slow dependence beyond five states cannot be resolved at these sample sizes.
- Small regimes in H3a (DEF-0018): no minimum is set per regime, so counts are reported beside every p-value.
- Iterative error of PLP (DEF-0027): the iterative error of the fixed Levenberg–Marquardt budget of the PLP estimator (15 iterations) is not estimated for this run. On the development seed DEV-0, a study with 15, 30 and 60 iterations showed the iterative change below 10% of the sampling half-width for 5 of the 18 primary parts (class N) and did not show it below 10% for the other 13 (class X, not negligible, 6; class U, not certified, 7). The projection of its size against the half-width to the full preset, by the square root of the ratio of the numbers of states (test states for H2a and H3c, sweep states for H2b), is stated and not applied. This is development evidence, not a result of this run. The report is docs/study/lm_doubling_dev0_report_v3.md.
- Per-seed gate risk (DEF-0026): V4 and V6 can fail on a given seed, and a failure is referred, never repaired.
- lambda_max for Chua has no published reference value at the study's parameters.
- Doubled thinning is not checked (Methods v2 §M16; DEF-0009).
- Bitwise agreement at the official size is extrapolated from smoke size (DEC-0033 M2).
- The gain-bound screen is reported only, computed with the v1 statistic, and the v3 screen is pending (DEC-0033 M3).
- One realization per system: one sealed seed gives one set of data per system, so no replicate variation is estimated.
- The block-sensitive label (a primary verdict that widening the half-width would change) is not computable for the sealed run, because the sealed run writes no states dump (owner default D6).
- Q-N and the gain bound are reported and carry no verdict.
- Power of H2a(ii) (DEF-0022): the second part of H2a (the partial-correlation margin test) has low power at these sample sizes: it can be refuted but essentially cannot pass, which v3 §7 anticipated. The owner accepted this as a known limitation (DEC-0041, ledger seq 32). The margin that v3 §7 projects for it is not reproduced part by part at the full sample size (DEF-0022 status line; the full-size report of WU-0003): this is development evidence, not a result of this run (owner answer B7). In this run the stored interval of the Rossler interior part is wider than the margin band of v3 §2, so that part could not pass at any estimate. The verdict words of its parts are in section 5; an inconclusive word there means the interval was too wide to decide. The pre-registered rule is kept.
- Regeneration by the same actor (DEC-0035): Run-2 (WU-0016) shows determinism, not an independent reproduction. The compared leaves are bitwise equal, and the same host, environment and actor produced both runs (DEC-0035). Results depend on the thread count and on the BLAS kernel of the host (DEF-0023, DEF-0024), which is why a second host may differ. The owner waived the independent-actor requirement for this case (ledger seq 31) and accepted agent-based cross-checking for this project (ledger seq 34).
- Verification and validation status of the code: owner code review waived (ledger seq 33); results spot-checked by the owner; code covered by independent agent reviews. DEF-0001 stays open until the owner closes it.
- Reporting gaps of the official RESULTS.md (NVVUQ.22), accepted by the owner (ledger seq 36): there is no numerical-error estimate (G1) and no per-QoI verification and validation status (G2) for the nine secondary or reported rows, which have no budget table; and the status wording of the secondaries (pre-registered, exploratory on development seeds) does not say whether a secondary is confirmatory in this run (G3). The five primary budget parts carry all six items.
- Figures of the official RESULTS.md (WU-0017.2, ledger seq 36): the four captions name no experiment or v3 identifier and none shows an interval. The figure map of docs/agent/notes/2026-10-21-promotion-figure-map.md gives them: separation_weight_vs_horizon, E4, H2a; kaplan_meier_by_rule, E4, rules behind H2c, H2d and H3c, no verdict; regret_vs_regimes, E5, H3c; knob_response_library, E1 and E2, H2b. The dotted line of regret_vs_regimes, which the caption calls a criterion, is a reference line drawn at 5.0 by the code (axhline(5.0), report.py at the frozen commit); it is not a pre-registered criterion for the plotted quantity (regret as a percent of the best-single MSE). The K rule of v3 §5 (1.05 times the minimum calibration excess MSE) is a different quantity.

## 11. What it means and does not mean [STUDENT]

The student writes this section in their own words. Prompts only, with no results: What did each primary hypothesis claim? Which verdicts are supported, not supported or inconclusive, and what does each word allow you to say? Which limitations matter most for what you say? What would you check next?

## A. Development context [DEVELOPMENT]

No development appendix in this build. Development-seed numbers appear only here, labeled, and never beside the official result (owner ruling D4). A development ensemble may be appended later.

## B. Interval labels

Copied verbatim from the `RESULTS.md` of the official run, one per row (procedure, level, dependence and multiplicity; NVVUQ.16).

- H1a (secondary) — procedure: moving-block bootstrap percentile interval, blocks of 5 consecutive test states in time order, B = 2000; level: 95%; dependence: resampled in blocks of 5 consecutive test states in time order (Künsch 1989), so dependence is kept within a block and none is assumed beyond it; multiplicity: none (secondary, unadjusted), intersection–union across systems, every part of the criterion must pass
- H1b (secondary) — procedure: moving-block bootstrap percentile interval, blocks of 5 consecutive test states in time order, B = 2000; level: 95%; dependence: resampled in blocks of 5 consecutive test states in time order (Künsch 1989), so dependence is kept within a block and none is assumed beyond it; multiplicity: none (secondary, unadjusted), intersection–union across systems, every part of the criterion must pass
- H1c (secondary) — procedure: moving-block bootstrap percentile interval, blocks of 5 consecutive test states in time order, B = 2000; level: 95%; dependence: resampled in blocks of 5 consecutive test states in time order (Künsch 1989), so dependence is kept within a block and none is assumed beyond it; multiplicity: none (secondary, unadjusted), intersection–union across systems, every part of the criterion must pass
- H1d (secondary) — procedure: moving-block bootstrap percentile interval, blocks of 5 consecutive test states in time order, B = 2000; level: 95%; dependence: resampled in blocks of 5 consecutive test states in time order (Künsch 1989), so dependence is kept within a block and none is assumed beyond it; multiplicity: none (secondary, unadjusted), intersection–union across systems, every part of the criterion must pass
- Q-N (estimate) — procedure: moving-block bootstrap percentile interval, blocks of 5 consecutive test states in time order, B = 2000; level: 95%; dependence: resampled in blocks of 5 consecutive test states in time order (Künsch 1989), so dependence is kept within a block and none is assumed beyond it; multiplicity: none (an estimate, read by the table of v3 section 7, not decided)
- H2a (primary) — procedure: moving-block bootstrap percentile interval, blocks of 5 consecutive test states (all of them, not only the eligible ones) in time order, B = 2000, with the eligibility of part (i) and the domain of part (ii) re-evaluated inside each resample (DEC-0008 A4); level: 1 − 0.05/3 (98.33%); dependence: resampled in blocks of 5 consecutive test states in time order (Künsch 1989), so dependence is kept within a block and none is assumed beyond it; multiplicity: Bonferroni over the three primaries (H2a, H2b, H3c), intersection–union across systems, every part of the criterion must pass; iterative error: the fixed 15-iteration Levenberg–Marquardt error of the PLP estimator is not estimated and is unverified (DEC-0024)
- H2b (primary) — procedure: moving-block bootstrap percentile interval, blocks of 5 consecutive test states in time order, B = 2000; level: 1 − 0.05/3 (98.33%); dependence: resampled in blocks of 5 consecutive test states in time order (Künsch 1989), so dependence is kept within a block and none is assumed beyond it; multiplicity: Bonferroni over the three primaries (H2a, H2b, H3c), intersection–union across systems, every part of the criterion must pass; iterative error: the fixed 15-iteration Levenberg–Marquardt error of the PLP estimator is not estimated and is unverified (DEC-0024)
- H2c (secondary) — procedure: moving-block bootstrap percentile interval, blocks of 5 consecutive test states in time order, B = 2000; level: 95%; dependence: resampled in blocks of 5 consecutive test states in time order (Künsch 1989), so dependence is kept within a block and none is assumed beyond it; multiplicity: none (secondary, unadjusted), intersection–union across systems, every part of the criterion must pass
- H2d (secondary) — procedure: moving-block bootstrap percentile interval, blocks of 5 consecutive test states in time order, B = 2000; level: 95%; dependence: resampled in blocks of 5 consecutive test states in time order (Künsch 1989), so dependence is kept within a block and none is assumed beyond it; multiplicity: none (secondary, unadjusted), intersection–union across systems, every part of the criterion must pass
- H2e (secondary) — procedure: moving-block bootstrap percentile interval, blocks of 5 consecutive test states in time order, B = 2000; level: 95%; dependence: resampled in blocks of 5 consecutive test states in time order (Künsch 1989), so dependence is kept within a block and none is assumed beyond it; multiplicity: none (secondary, unadjusted), intersection–union across systems, every part of the criterion must pass
- (reported) — procedure: none, a fraction of states within the P1 bound is reported with no interval; level: not applicable; dependence: not applicable; multiplicity: none (reported with no pass/fail bar)
- H3a (secondary) — procedure: Holm-adjusted log-rank tests between consecutive regimes, p-values with no interval; level: each adjusted p must be below 0.01; dependence: the log-rank test treats states as independent, serial dependence between neighbouring states is not modelled; multiplicity: Holm over the consecutive comparisons within a system, intersection–union across systems
- H3b (secondary) — procedure: moving-block bootstrap percentile interval over construction states, blocks of 5 consecutive states in time order, B = 2000; level: 95%; dependence: resampled in blocks of 5 consecutive construction states in time order (Künsch 1989), so dependence is kept within a block and none is assumed beyond it; multiplicity: none (secondary, unadjusted), intersection–union across systems, every part of the criterion must pass; coverage not measured: the interval conditions on the fitted proxies and is not guaranteed to cover, because the split variable can switch between resamples (the bootstrap of a non-smooth functional; the WU-0006 coverage study has no H3b case)
- H3c (primary) — procedure: moving-block bootstrap percentile interval, blocks of 5 consecutive test states in time order, B = 2000; level: 1 − 0.05/3 (98.33%); dependence: resampled in blocks of 5 consecutive test states in time order (Künsch 1989), so dependence is kept within a block and none is assumed beyond it; multiplicity: Bonferroni over the three primaries (H2a, H2b, H3c), intersection–union across systems, every part of the criterion must pass; iterative error: the fixed 15-iteration Levenberg–Marquardt error of the PLP estimator is not estimated and is unverified (DEC-0024)

## C. Trace

Every number quoted above is listed with its source and leaf path in `2026-10-19-prelim-findings-dryrun-dev2.trace.csv`. Run the `check` command of `tools/findings_build.py` on this directory to verify the document against the sources.

Leaves not found in the sources, written "not recorded": 31. Null leaves written "not computed": 0.
- official:handling/skipped_variants
- official:systems/chua/H3a/n_censored_per_regime/0
- official:systems/chua/H3a/n_censored_per_regime/1
- official:systems/chua/H3a/n_censored_per_regime/2
- official:systems/chua/H3a/n_censored_per_regime/3
- official:systems/chua/H3a/n_events_per_regime/0
- official:systems/chua/H3a/n_events_per_regime/1
- official:systems/chua/H3a/n_events_per_regime/2
- official:systems/chua/H3a/n_events_per_regime/3
- official:systems/lorenz63/H3a/n_censored_per_regime/0
- official:systems/lorenz63/H3a/n_censored_per_regime/1
- official:systems/lorenz63/H3a/n_censored_per_regime/2
- official:systems/lorenz63/H3a/n_censored_per_regime/3
- official:systems/lorenz63/H3a/n_censored_per_regime/4
- official:systems/lorenz63/H3a/n_censored_per_regime/5
- official:systems/lorenz63/H3a/n_censored_per_regime/6
- official:systems/lorenz63/H3a/n_censored_per_regime/7
- official:systems/lorenz63/H3a/n_events_per_regime/0
- official:systems/lorenz63/H3a/n_events_per_regime/1
- official:systems/lorenz63/H3a/n_events_per_regime/2
- official:systems/lorenz63/H3a/n_events_per_regime/3
- official:systems/lorenz63/H3a/n_events_per_regime/4
- official:systems/lorenz63/H3a/n_events_per_regime/5
- official:systems/lorenz63/H3a/n_events_per_regime/6
- official:systems/lorenz63/H3a/n_events_per_regime/7
- official:systems/rossler/H3a/n_censored_per_regime/0
- official:systems/rossler/H3a/n_censored_per_regime/1
- official:systems/rossler/H3a/n_censored_per_regime/2
- official:systems/rossler/H3a/n_events_per_regime/0
- official:systems/rossler/H3a/n_events_per_regime/1
- official:systems/rossler/H3a/n_events_per_regime/2
