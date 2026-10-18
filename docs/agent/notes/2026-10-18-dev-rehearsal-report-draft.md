# Development rehearsal and precision report (WU-0003.3): DRAFT

**DEVELOPMENT (DEV-0, DEV-1, DEV-2): not a hypothesis test.** Every run below used a development seed. No number in this report is a result of the study, no verdict below is a finding of the study, and nothing here was used to choose or change a criterion. The confirmatory seed was not drawn, read or run.

**Status of this file.** Draft by the planner (claude-opus-5-5), 2026-10-18, from `develop` 7b6f6e6. Intended destination: `docs/study/dev_rehearsal_report.md` (ROADMAP WU-0003.3); agents may not write `docs/study/`, so the main session moves it. Every number is quoted from a committed file named in the source line under each table (keys in square brackets are listed with their full paths and git blob ids in Appendix A). Nothing was recomputed. This file is assembled by hand from the outputs of the committed tools (`tools/rehearsal_report.py`, `tools/rehearsal_diagnostics.py`, `tools/compare_runs.py`); it is not itself the output of a script (see section 10, item 12).

---

## 1. What the rehearsal was for

The study's confirmatory run happens once, on a sealed seed. Before that seed is used, the full pipeline was rehearsed on development seeds to answer four questions for the owner (unit plan `WU-0003-dev-rehearsal.md`, items 1 to 4 and amendments 1 to 10):

1. **Does the code run end to end on the target machine, and does the validation gate (V1 to V7) pass?**
2. **How precise will each pre-registered criterion be at the confirmatory (full) sample size?** For every v3 criterion: the interval half-width at the rehearsal size, its projection to the full preset, and which verdicts can be reached. This feeds the owner's sample-size decision.
3. **How reproducible are the outputs?** Same device twice, and GPU against CPU on the same seed. This feeds the reproducibility tolerance that the regeneration of the confirmatory run (WU-0016) is judged against.
4. **What do the diagnostics say about the statistical design** (dependence between states, block length 5, finite-M bias, iteration sensitivity)?

The decisions themselves belong to the owner. Section 11 lists what the owner has ruled on this evidence.

## 2. The runs

| Run | Preset | Seed | Device (threads) | Code / commit carried | Wall (s) | Peak RSS (B) | Exit | Purpose |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R0 (a) | smoke, 3 systems | DEV-1 | GPU RTX 4090 | e3b2645 / edb10e7 | 698 | not recorded here | 0 | GPU check, device probe |
| R0 (b) | smoke, 3 systems | DEV-1 | CPU | e3b2645 / edb10e7 | 175 | not recorded here | 0 | device probe |
| R0 (c) | smoke, default systems | DEV-0 | CPU | e3b2645 / edb10e7 | 61 | not recorded here | 0 | bitwise check against the step-4 reference |
| R1 | pilot, states dump on | DEV-1 | GPU RTX 4090 (4) | c9bb981 / 01d9fc7 | 1659 | 3 829 411 840 | 0 | the rehearsal |
| R2 | pilot | DEV-1 | GPU RTX 4090 (4) | c9bb981 / 01d9fc7 | 1640 | 3 810 615 296 | 0 | GPU repeat of R1 |
| R3 | pilot | DEV-1 | CPU (8) | c9bb981 / c47d4d1 | 5503 | 3 363 201 024 | 0 | GPU against CPU at pilot size |
| R4 | (as R3, emulated other host) | — | — | — | — | — | **not run** | would have exercised tiers T1 to T3 |
| R5 | full, states dump on | DEV-2 | GPU RTX 4090 (4) | c9bb981 / 6f1a8c8 | 2739 | 4 978 192 384 | 0 | full-size precision, budget, counts |
| R6 | full | DEV-2 | CPU (8) | c9bb981 / 059dc84 | 17031 | 4 749 778 944 | 0 | GPU against CPU at full size |

Sources: [R0] Runs table; [R1R2] Runs table and "R5 results"; [R1R2-meta-r1], [R1R2-meta-r2], [R5-meta], [R3-meta], [R6-meta]; [R3R6] "R3 result" and "R6 result"; peak RSS of R3, R5, R6 from [R3R6-gates-R3] and [R3R6-gates-R6]. In every run, provenance shows the development seed id, `dirty False`, `jax_x64 True` and the DEVELOPMENT label ([R1R2], [R3R6]). The commits carried differ from c9bb981 by documentation only ([R1R2] "Contents under test"; [R3R6] "Contents under test").

- **Wall times.** R1, R2 and R5 ran alone and are clean figures; R3 and R6 may have shared the CPU with other lanes, so their wall times are upper bounds ([R1R2] "R5 results"; [R3R6] "R3 result", "R6 result"). The full preset took 0.76 h on the GPU and 4.73 h on the CPU, both under the 12 h limit of LPC.PC.22 ([R3R6] "R6 result"; [drafts] §2).
- **GPU memory.** `nvidia-smi` at 30 s: 1205 MiB (R1), 1201 MiB (R2), 1283 MiB (R5) of 24 564 MiB ([R1R2]).
- **R4 was not run.** No rehearsal pair therefore fell in the equal-context tiers T1 to T3 ([drafts] §1, Evidence; [owner-note] §34 item 2).

## 3. Validation gate

The gate flags are V1, V2, V4, V5, V6 and V7; V3 is reported only (`lpcstudy/validation.py`, `gate_flags`). V6 is the step-halving check of the integrator, `integrator_max_dev_sigma` < 1e-3; V4 is the oracle-weight convergence check, M = 200 median half-width ≤ 0.05.

| Run (seed, size, device) | Lorenz-63 | Rössler | Chua | V6 statistic (L63 / Rö / Chua) | V4 half-width, M = 200 (L63 / Rö / Chua) |
| --- | --- | --- | --- | --- | --- |
| R1 = R2 (DEV-1, pilot, GPU) | all pass | all pass | all pass | pass (value not printed in the R1/R2 gate file) | 0.0349 / 0.0439 / 0.0272 |
| R3 (DEV-1, pilot, CPU) | all pass | all pass | all pass | 2.6e-05 / 3.07e-05 / 0.000109 | 0.0261 / 0.0455 / 0.0236 |
| R5 (DEV-2, full, GPU) | all pass | all pass | **V6 FAILED** | 3.59e-05 / 3.81e-05 / **0.00241** | 0.0263 / 0.0424 / 0.0299 |
| R6 (DEV-2, full, CPU) | all pass | all pass | all pass | 2.18e-05 / 3.06e-05 / 0.000334 | 0.0290 / 0.0350 / 0.0230 |

Sources: [R1R2-gate], [R5-gate], [R3R6-gates-R3], [R3R6-gates-R6]; [R1R2] "R5 results".

- **The R5 Chua V6 failure.** On the GPU context of DEV-2 at full size, Chua's V6 statistic was 2.405e-3 against the 1e-3 bar; the code flagged the Chua results as provisional. It was reported and not repaired; no bar, tolerance or criterion changed ([R1R2] "R5 results"; [owner-note] §28).
- **The R6 pass.** The CPU context of the same seed passed (Chua 3.3e-4), as the offline check had predicted from the CPU context (3.34e-4) ([R3R6] "R6 result"; [R1R2] R5 checklist item 9). GPU and CPU build different trajectories for the same seed (section 4), so R5 and R6 are two different realizations, and the gate outcome depended on the device.
- **Pre-registered gate predictions (P-2).** P(at least one V6 failure over DEV-1 and DEV-2) ≈ 8.8% (12.9% if R3 is TD); P(at least one V4 failure) ≈ 50% to 71% (plan amendment 2, B1 item 12). Observed: one V6 failure (R5, Chua, GPU), no V4 failure in any run ([R3R6] "R6 result", item (1)). The per-seed risk estimated offline is in section 10.
- **V4 at full size (first measurement).** All three systems pass in R5 and R6. R5's values are 1.19, 1.53 and 1.74 times the √(40/100) scaling of R1's pilot values (0.022, 0.028, 0.017) ([R1R2] "R5 results"). V4 at full size is not pooled with the pilot V4.
- **R0 (smoke) gates** printed "FAILED, provisional" with different flags on GPU and CPU; read as the smoke size plus different trajectories, not a finding ([R0] Runs).
- **Other run-integrity checks.** P2(c): 0 violations and every chain counter 0 on every system of R1, R3, R5 and R6, with 1023 to 1232 switching states per system at the pilot and 2972 to 3598 at full size (premise: at least 100). States with a clipped H_ref oracle draw: 0 in every split of every run (limits 8 of 1400 and 16 of 4000), so the DEV-0 clip bound transferred ([R1R2-gate], [R5-gate], [R3R6-gates-R3], [R3R6-gates-R6]).

## 4. Reproducibility

| Pair | Seed, preset | Devices | Tier | Leaves | TD parts failing | max z, away / symmetric | Σ z², away / symmetric | Verdict-type leaves differing | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R0 (c) against the step-4 reference | DEV-0, smoke | CPU, CPU | T0 | 4794 common, 0 different | — | — | — | 0 | PASS |
| R0 (a) against R0 (b) | DEV-1, smoke | GPU, CPU | TD | — | 0 of 18 | 2.61 / 2.53 | 17.15 / 19.17 | 73 | PASS |
| R1 against R2 | DEV-1, pilot | GPU, GPU | **T0** | **20 533 of 20 533 equal** | — | — | — | 0 | PASS |
| R1 against R3 | DEV-1, pilot | GPU, CPU | TD | 20 509 common: 10 158 equal, 10 351 different; 36 one-sided | 0 of 18 | 2.72 / 2.73 | 24.89 / 23.77 | 30 | PASS |
| R2 against R3 | DEV-1, pilot | GPU, CPU | TD | identical to R1 against R3 | 0 of 18 | 2.72 / 2.73 | 24.89 / 23.77 | 30 | PASS |
| R5 against R6 | DEV-2, full | GPU, CPU | TD | 20 649 common: 10 022 equal, 10 627 different; 6 one-sided | 0 of 18 | 2.26 / 2.32 | 15.77 / 16.45 | 52 | PASS |

Sources: [R0] sections (3) and (4); [R0-t0]; [R0-gpu-cpu]; [R1R2-compare]; [R3R6-compare-R1R3], [R3R6-compare-R2R3], [R3R6-compare-R5R6]; the re-runs under the OF-5 rule [9c-R1R3] and [9c-R5R6], whose z values are identical to the stored ones (WU-0003.9c Log, "Offline stored comparisons").

How to read it:

- **Tiers** are chosen mechanically by `tools/compare_runs.py` from the context digests. **T0**: same host, device and threads, so every leaf must be bitwise equal. **TD**: the trajectory itself differs, so no per-leaf tolerance applies. Each of the 18 primary parts (6 per system: H2a(i), H2a(ii) zero, H2a(ii) interior, H2b(i), H2b(ii), H3c) is then tested for statistical agreement: z = |d| / √(se₀² + se₁²), with the standard errors taken from the interval arms that face each other (the "away" form), z level 2.394, bound 3.4. Since the owner's ruling OF-5 (2026-10-18) the away form governs and the symmetric form is printed as information ([9c-R1R3], footer). Both forms pass on every pair.
- **Same device: bitwise.** Repeating a run on the same GPU and host gave identical output in every leaf, digests and robustness block included ([R1R2]). The DEV-0 CPU smoke was bitwise equal to its reference ([R0] (4)). So the ROADMAP rule "10 times the GPU-to-GPU difference" gives 10 × 0: the same-device tolerance is "bitwise on the same device type" ([drafts] §1).
- **GPU against CPU: different realizations.** At every size, GPU and CPU produced different trajectories on all three systems: every context digest differed, λ_max differed by 1.9e-4 to 2.2e-2 relative at smoke, and the start states differed completely ([R0] (3)). The six V1 leaves differed across devices by 3.5e-10 to 1.5e-8 absolute, which is why the owner ruled that the V1 1e-12 rule applies only to pairs with equal contexts (OF-2, [owner-note] §25, §26).
- **What a TD pass does not mean.** It does not reproduce verdicts or the gate: 30 (pilot) and 52 (full) verdict-type leaves differ, and Chua's gate passes on the CPU and fails on the GPU for DEV-2 ([drafts] §1 item 4).
- **Not exercised.** No equal-context, non-bitwise pair (T1 to T3) exists among the rehearsal runs, because R4 was not run. The T1 to T3 tolerances rest on the WU-0003.9 kernel-pair evidence at smoke size (class (a) declared 1e-5 with largest relative difference 2.94e-7; classes (b) to (g) 1e-4) ([drafts] §1, Evidence).

## 5. Precision

### 5.1 How to read the projections

`tools/rehearsal_report.py` projects each pilot half-width (hw) to the full preset. The printed factor combines √(n_run/n_full) for the criterion's own n with the resampling factor for B (plan amendment 2, B1 item 6). Three groups get a range instead of one factor: H2c, H2d and H3c (the evaluation-draw factor κ_E, whose pre-registered range [0.7071, 1] governs, because no unbiased point estimator exists: OF-R2, kept by the owner on 2026-10-17), and Q-N (the training-size range). On a full-size run (R5, R6) every factor is 1, so the numbers are the observed half-widths. H3a and H3c are conditional on the number of regimes K that A5 chose in that run. Two readings compare each projection with the v3 §7 precision statements: reading (i) against the √(n) factor alone, reading (ii) against the factor ranges; a projection outside [0.67, 1.5] times the v3 value is reported as "v3 precision not reproduced" ([R1-report] header and rows; plan amendment 2 B1 item 6; amendment 8 H1 to H3).

### 5.2 Half-widths per criterion

Columns: R1 (DEV-1, pilot, GPU) half-width and its projection to full size; R5 (DEV-2, full, GPU) and R6 (DEV-2, full, CPU) observed half-widths. R5 and R6 are two realizations of the same seed (section 4). A range in the projection column comes from κ_E or the Q-N training size.

**Lorenz-63**

| Criterion | R1 hw (pilot) | R1 projected to full | R5 hw (full) | R6 hw (full) |
| --- | --- | --- | --- | --- |
| H1a ratio, ρ = 1% | 0.1962 | 0.1082 | 0.1055 | 0.1425 |
| H1b PLP slope | 0.0756 | 0.0538 | 0.0410 | 0.0375 |
| H1c PLP median ratio | 0.1318 | 0.0938 | 0.0831 | 0.0568 |
| H1d analog seed | 0.0290 | 0.0207 | 0.0271 | 0.0288 |
| Q-N oracle logit (v3 ±0.04) | 0.0611 | 0.0265–0.0435 | 0.0265 | 0.0210 |
| H2a(i) | 0.0497 | 0.0357 | 0.0279 | 0.0266 |
| H2a(ii) zero | 0.0939 | 0.0673 | 0.0773 | 0.0646 |
| H2a(ii) interior | 0.1154 | 0.0828 | 0.0905 | 0.0992 |
| H2b(i) | 0.0941 | 0.0523 | 0.0503 | 0.0505 |
| H2b(ii) (v3 0.03) | 0.0406 | 0.0226 | 0.0257 | 0.0239 |
| H2c A4–A2 | 0.0335 | 0.0169–0.0238 | 0.0069 | 0.0105 |
| H2c A4–A1 | 0.0056 | 0.0028–0.0040 | 0.0043 | 0.0083 |
| H2d | 0.9590 | 0.4828–0.6828 | 0.4274 | 0.2561 |
| H2e, ρ = 1% (v3 0.04) | 0.0441 | 0.0243 | 0.0178 | 0.0207 |
| H2e, ρ = 2% (v3 0.04) | 0.0551 | 0.0304 | 0.0237 | 0.0283 |
| H3c | 0.1932 | 0.0979–0.1385 | 0.2052 | 0.1677 |

**Rössler**

| Criterion | R1 hw (pilot) | R1 projected to full | R5 hw (full) | R6 hw (full) |
| --- | --- | --- | --- | --- |
| H1a ratio, ρ = 1% | 0.1568 | 0.0865 | 0.0693 | 0.0660 |
| H1b PLP slope | 0.0608 | 0.0433 | 0.0434 | 0.0393 |
| H1c PLP median ratio | 0.0493 | 0.0351 | 0.0283 | 0.0444 |
| H1d analog seed | 0.0452 | 0.0322 | 0.0347 | 0.0295 |
| Q-N oracle logit (v3 ±0.04) | 0.0546 | 0.0237–0.0389 | 0.0322 | 0.0353 |
| H2a(i) | 0.0418 | 0.0300 | 0.0385 | 0.0349 |
| H2a(ii) zero | 0.0944 | 0.0677 | 0.0825 | 0.0798 |
| H2a(ii) interior | 0.1439 | 0.1031 | 0.1117 | 0.0885 |
| H2b(i) | 0.1053 | 0.0585 | 0.0504 | 0.0532 |
| H2b(ii) (v3 0.03) | 0.0466 | 0.0259 | 0.0211 | 0.0221 |
| H2c A4–A2 (relative hw) | 0.0741 | 0.0373–0.0528 | 0.0454 | 0.0364 |
| H2c A4–A1 (relative hw) | 0.0971 | 0.0489–0.0692 | 0.0547 | 0.0427 |
| H2d | 0.1046 | 0.0527–0.0745 | 0.0468 | 0.0495 |
| H2e, ρ = 1% (v3 0.04) | 0.0490 | 0.0270 | 0.0211 | 0.0218 |
| H2e, ρ = 2% (v3 0.04) | 0.0450 | 0.0248 | 0.0238 | 0.0277 |
| H3c | 0.0949 | 0.0481–0.0680 | 0.0450 | 0.0431 |

(Rössler H2c is printed as a relative half-width because its absolute half-width rounds to 0.0000 at four digits.)

**Chua**

| Criterion | R1 hw (pilot) | R1 projected to full | R5 hw (full; gate failed V6) | R6 hw (full) |
| --- | --- | --- | --- | --- |
| H1a ratio, ρ = 1% | 0.1424 | 0.0785 | 0.0759 | 0.0801 |
| H1b PLP slope | 0.0545 | 0.0388 | 0.0326 | 0.0265 |
| H1c PLP median ratio | 0.0833 | 0.0593 | 0.0551 | 0.0511 |
| H1d analog seed | 0.0530 | 0.0378 | 0.0355 | 0.0323 |
| Q-N oracle logit (v3 ±0.04) | 0.0628 | 0.0273–0.0447 | 0.0339 | 0.0316 |
| H2a(i) | 0.0388 | 0.0278 | 0.0443 | 0.0298 |
| H2a(ii) zero | 0.1041 | 0.0746 | 0.0816 | 0.0785 |
| H2a(ii) interior | 0.1447 | 0.1038 | 0.0946 | 0.1306 |
| H2b(i) | 0.0779 | 0.0433 | 0.0526 | 0.0532 |
| H2b(ii) (v3 0.03) | 0.0447 | 0.0249 | 0.0245 | 0.0223 |
| H2c A4–A2 | 0.0033 | 0.0017–0.0024 | 0.0012 | 0.0016 |
| H2c A4–A1 | 0.0008 | 0.0004–0.0005 | 0.0013 | 0.0014 |
| H2d | 0.0512 | 0.0258–0.0365 | 0.0448 | 0.0583 |
| H2e, ρ = 1% (v3 0.04) | 0.0368 | 0.0203 | 0.0278 | 0.0241 |
| H2e, ρ = 2% (v3 0.04) | 0.0450 | 0.0248 | 0.0276 | 0.0244 |
| H3c | 0.1086 | 0.0550–0.0778 | 0.0715 | 0.0606 |

Sources: [R1-report], [R5-report], [R6-report] (per-system rows). The R3 projections (DEV-1, pilot, CPU) are in [R3-report] and summarized in 5.3. V7 rows are in the same files.

### 5.3 Against the v3 §7 precision statements

v3 §7 states: "Most criteria can be decided in at least one direction"; H2a(ii) "essentially cannot pass: that would need a partial correlation within about 0.01 of zero"; "The Q-N interval is about ±0.04"; H2b(ii) and H2e have "projected half-widths 0.03 and 0.04" (`docs/study/proposal_and_methods_v3.md` §7).

| Run | Compared | Reading (i) fires | Reading (ii) fires | H2a(ii) margin reading (governing) fires | Pre-registered predictions within |
| --- | --- | --- | --- | --- | --- |
| R1 (DEV-1, pilot, GPU) | projection | 10 of 18 | 10 of 18 | 6 of 6 | 11 of 12 (outside: Rössler H2b(ii), 0.863 of 0.03) |
| R3 (DEV-1, pilot, CPU) | projection | 12 of 18 | 11 of 18 | 5 of 6 | 11 of 12 (outside: Rössler H2b(ii), projected 0.0197) |
| R5 (DEV-2, full, GPU) | observed | 10 of 18 | 10 of 18 | 5 of 6 | 10 of 12 (outside: Lorenz-63 Q-N oracle logit; Lorenz-63 H2b(ii)) |
| R6 (DEV-2, full, CPU) | observed | 10 of 18 | 10 of 18 | 5 of 6 | 11 of 12 (outside: Lorenz-63 Q-N oracle logit) |
| R5 observed against the R1 projection | 69 parts | 11 of 69 | 4 of 69 | — | predicted false triggers over 69 parts: 0.47 |

Sources: Summary sections of [R1-report], [R3-report], [R5-report], [R6-report], [R1-obs-R5].

- **H2e (v3 0.04): narrower than v3.** Ratios of the half-width to 0.04, in the order L63 ρ 1%, L63 ρ 2%, Rö ρ 1%, Rö ρ 2%, Chua ρ 1%, Chua ρ 2%: R1 projected 0.607, 0.760, 0.676, 0.620, 0.508, 0.620; R5 observed 0.444, 0.592, 0.529, 0.595, 0.696, 0.691; R6 observed 0.517, 0.707, 0.546, 0.692, 0.602, 0.609. All lie inside the pre-registered 0.44 to 0.76. In each of these three runs, 4 of the 6 parts are below 0.67 of v3 and read "v3 precision not reproduced" on the narrow side: a precision gain, not a loss.
- **H2b(ii) (v3 0.03): near the lower edge.** Ratios to 0.03 (L63, Rö, Chua): R1 0.752, 0.863, 0.828; R5 0.857, 0.704, 0.818; R6 0.796, 0.736, 0.743. All are inside the band [0.67, 1.5]; two of these nine values fall outside the narrower pre-registered 0.68 to 0.85 (R1 Rössler 0.863, R5 Lorenz-63 0.857), and R3's Rössler projection (0.0197) falls below the band.
- **Q-N oracle logit (v3 ±0.04).** The pilot projection was "undetermined" on all three systems, as pre-registered (R1: 0.663–1.087, 0.593–0.972, 0.682–1.118 of 0.04). At full size, Lorenz-63 was narrower than v3 (R5 0.662, R6 0.525 of 0.04), while Rössler (0.804, 0.881) and Chua (0.847, 0.790) were inside the band.
- **H2a(ii): the margin 0.1 − hw_full against v3's "about 0.01"** (band [0.0067, 0.015], OF-G3). L63 zero, L63 interior, Rö zero, Rö interior, Chua zero, Chua interior: R1 +0.0327, +0.0172, +0.0323, −0.0031, +0.0254, −0.0038; R5 +0.0227, +0.0095, +0.0175, −0.0117, +0.0184, +0.0054; R6 +0.0354, +0.0008, +0.0202, +0.0115, +0.0215, −0.0306. A negative margin means that a pass is impossible at that half-width: the tool prints "IMPOSSIBLE" for Rössler and Chua interior (R1), Rössler interior (R5), Chua interior (R6), and Rössler interior in R3 (margin −0.0077). The zero parts can pass only with |partial correlation| below +0.018 to +0.035 at full size. In R5 the part that is inside the band is **Lorenz-63 interior** (+0.0095), not Chua interior (+0.0054, which fires); see section 10, item 13.

### 5.4 Which verdicts are reachable

The tool computes reachability explicitly for H3a (below) and H2a(ii) (the "pass needs |pc| < …" line above). For the other criteria it prints the precision against v3 (5.3) but no reachability line.

**H3a** (the regime-ordering criterion; Holm-adjusted log-rank p against the bar 0.01; conditional on K):

| Run | Lorenz-63: K, largest projected Holm p | Rössler | Chua |
| --- | --- | --- | --- |
| R1 (DEV-1, pilot projection, GPU) | K 6, 1: not reachable | K 4, 0.131: not reachable | K 5, 0.176: not reachable |
| R3 (DEV-1, pilot projection, CPU) | K 5, 0.8: not reachable | K 6, 0.156: not reachable | K 2, 4.67e-64: reachable |
| R5 (DEV-2, full, GPU) | K 8, 1: not reachable | K 4, 0.726: not reachable | K 4, 0.00397: reachable |
| R6 (DEV-2, full, CPU) | K 8, 0.684: not reachable | K 3, 0.204: not reachable | K 4, 6.71e-05: reachable |

Sources: H3a lines of [R1-report], [R3-report], [R5-report], [R6-report].

At full size, an H3a pass was reachable only on Chua, in both realizations of DEV-2. At the pilot it depended on the device: GPU (R1) reached it on no system, CPU (R3) on Chua. K differs between devices for the same seed, so the H3a reading is conditional on one realization and its K.

### 5.5 The H3c interval

The pilot preset had no H3c interval; the rehearsal provides one.

| Run | Lorenz-63 | Rössler | Chua |
| --- | --- | --- | --- |
| R1 hw → projected (DEV-1, GPU) | 0.1932 → 0.0979–0.1385 | 0.0949 → 0.0481–0.0680 | 0.1086 → 0.0550–0.0778 |
| R3 hw → projected (DEV-1, CPU) | 0.3082 → 0.1562–0.2210 | 0.0810 → 0.0411–0.0581 | 0.1698 → 0.0861–0.1218 |
| R5 observed (DEV-2, GPU) | 0.2052 | 0.0450 | 0.0715 |
| R6 observed (DEV-2, CPU) | 0.1677 | 0.0431 | 0.0606 |

Sources: H3c rows of [R1-report], [R3-report], [R5-report], [R6-report].

The H3c projection carries the κ_E range and is conditional on K; its predicted false-trigger rate for the band is 7.0%, against 0.4% for most other parts ([R1-report]). Lorenz-63 has the widest H3c interval in every run, and R5's Lorenz-63 value (0.2052) lies above the R1 projection, outside the band by reading (i) ([R1-obs-R5]).

### 5.6 R5 observed against the R1 projection

Different seeds and contexts: a calibration check of the projection, not a defect. 11 of 69 parts lie outside the band by reading (i) and 4 by reading (ii) (Lorenz-63 H2c A4–A2, 0.0069 against 0.0169–0.0238; Lorenz-63 V7 median slope; Chua H2a(i), 0.0443 against 0.0278; Chua H2c A4–A1, 0.0013 against 0.0004–0.0005), where 0.47 false triggers over 69 parts were predicted under the projection model ([R1-obs-R5] Summary; [R1R2] "R5 results", item 2).

## 6. Diagnostics D1 to D6 and the block length

Diagnostics need the states dump, so they exist for R1 and R5 only (R3 and R6 ran without the dump and report "not computable", as planned). The values below are from the current tool (WU-0003.8d, with the OF-3 headline and the block-sensitive label), run offline on the R1 and R5 dumps with the pre-registered defaults (seed 20261018, 1000 permutations, 2000 resamples).

| Diagnostic | R1 (DEV-1, pilot, GPU) | R5 (DEV-2, full, GPU) | Reading |
| --- | --- | --- | --- |
| D1: lag-1 autocorrelation of each influence series | 77 of 78 series within threshold (24 of 24 primary); exception Rössler H1d estimation seed, +0.178 | 77 of 78 (23 of 24 primary); exception Lorenz-63 H1a ρ = 1%, +0.115 against 0.11 | Predicted P(some primary series above) under no dependence: 0.1154 (pilot), 0.012 (full) |
| D2: the A5 variance-ratio rule (information) | fired on 4 of 24 primary series | fired on 4 of 24 | Predicted P(at least one) with no dependence: 0.993 (pilot), 0.906 (full) |
| D2: pooled permutation reading (**governs**, OF-3) | fired on 0 of 3 systems; smallest p 0.1838 | fired on 0 of 3; smallest p 0.0250 | Trigger: the 0.99 quantile of the null. "Block length 5 is a design question": **no** |
| D2: β̂₅ reading (information) | 0 series | 0 series | — |
| Block-sensitive label (report-only) | 1 of 24 primary parts (Rössler H1a ρ = 2%) | 0 of 24 | A verdict that widening by √max(1, V*(10)/V*(5)) would change; changes nothing |
| D3: log-SD of per-state evaluation MSE (A1, A4, A5) | L63 3.103, 3.066, 2.645; Rö 2.179, 2.110, 2.178; Chua 2.993, 2.871, 3.001 | L63 2.965, 2.910, 2.675; Rö 1.973, 1.906, 1.967; Chua 2.870, 2.845, 2.923 | Above 1.5 everywhere: the heavy-tailed C2h/C4h coverage rows apply |
| D4: split-half reliability, H2a(ii) interior attenuation A (L63, Rö, Chua) | 0.9932, 0.9875, 0.9913 | 0.9924, 0.9902, 0.9933 | Small attenuation; the interior values overstate reliability (labelled) |
| D5: finite-M bias of the H2a(i) median range | not determined on all 3 | not determined on all 3; B_V4(200) −0.11497, −0.00244, −0.05450 | Budget row 1 stays "not below 10%" (PF-5) |
| D6: H2b(ii) clip-boundary bias | not determined on all 3 | not determined on all 3 | f_b at n_lib 1000 (L63, Rö, Chua): R1 0.653, 0.433, 0.510; R5 0.677, 0.433, 0.575 |
| Exact reproduction of H1d `nhat` Spearman | not computable exactly on 3 systems (ties created by the stored log transform) | same | The tools' exit 2; known artefact, not a defect of the results |

Sources: [8d-r1], [8d-r5] (per-system sections and "Run level"); R1 predicted acf rate from [R1R2] "Pre-registered predictions", item 5; β̂₅ counts from the "D2 owner flag" lines of [8d-r1] and [8d-r5]; the H1d artefact from `docs/agent/notes/2026-10-17-h1d-spearman-mismatch.md` and [R1R2] R5 "Contents under test".

**Block length.** The applied mathematician's analysis of the R1 and R5 dumps ([block-length]; summarized in [owner-note] §31) found:

- The A5 rule's 4 of 24 is what no dependence produces (null mean 4.15 and 2.23; P(count ≥ 4) 0.60 and 0.19).
- The calibrated readings never fired: β̂₅ on 0 of 48 series, the pooled permutation on 0 of 6 system-runs (smallest p 0.025 against 0.01).
- Short-range dependence is real on Lorenz-63 (V*(5)/V*(1) ×1.077, p 0.003) and is absorbed by blocks of 5.
- Beyond 5 states the pooled V*(10)/V*(5) is ×1.011 (upper 1.032) and V*(20)/V*(5) ×1.041 (upper 1.090): at most +1.6% and +4.4% on a half-width, below the φ = 0.3 stress row (+7.3%).

The owner kept block length 5 for all three systems, made the pooled permutation reading govern D2, and added the report-only block-sensitive label (2026-10-17, [owner-note] §31).

## 7. Iteration sensitivity of the PLP estimator (DEV-0)

The PLP state estimator runs a fixed 15 Levenberg–Marquardt iterations by design (v3 §4). A separate development study doubled the iteration count, 15 to 30 and 30 to 60, on the DEV-0 pilot (CPU, `LPC_THREADS=8`, one realization), and classified each of the 18 primary parts by rule R: N (negligible), X (not negligible), U (not certified) ([lm-v3] §1, §2).

- **Counts: N 5, X 6, U 7.** The LM-row flag ("negligible") is yes on 5 of 18 parts and no on 13 ([lm-v3] §0).
- **Rule R order (DEF-0028).** The owner ruled that the tool applies the plan's order: a structural switch (a change of A5's K, an H2a(ii) "one" part at some arms only, or an infinite bound) makes a part U before any X bullet. On DEV-0 this moved Chua H3c from X to U; no other part and no number changed ([lm-v3] §0; [owner-note] §29, §30).
- **The owner's ruling on O5 of the doubling study (DEF-0027): "report and flag only".** The design value stays 15 iterations, the flag is reported per part and not corrected, and there is no new reference run ([owner-note] §29). How the DEV-0 flags enter the confirmatory report: quoted as development evidence with the √(n_full/n_pilot) projection; the sealed report keeps "not estimated" plus a pointer ([owner-note] §35, B7).

## 8. Counted handling

Nothing is clipped, replaced or skipped silently; every handling event is counted. Totals over all systems:

| Counter | R1 = R2 (DEV-1, pilot, GPU) | R3 (DEV-1, pilot, CPU) | R5 (DEV-2, full, GPU) | R6 (DEV-2, full, CPU) |
| --- | --- | --- | --- | --- |
| ν-cap clips | 116 | 105 | 501 | 460 |
| ν replacements = invariant-mean replacements (Rössler only) | 267 | 14 | 163 | 425 |
| LM non-finite cost | 523 | 140 | 472 | 716 |
| LM non-finite Jacobian | 267 | 14 | 163 | 425 |
| Zero-variance correlations (CP side) | 171 465 | 188 220 | 524 135 | 505 565 |
| Error clips (PLP) | 0 | 11 (Chua, one sweep cell, 11 of 300 000 entries) | 0 | 0 |
| Failed variants | not in the R1 file | 0 | 0 | 0 |
| States with a clipped H_ref oracle draw | 0 | 0 | 0 | 0 |
| C4 LM readings outside a band (information) | 2 (Rössler) | 1 (L63 `fraction_above_chi2` 0.0457 against [0.0099, 0.041]) | 0 | 1 (Rössler `fraction_no_decrease` 0.0017 against [0, 0.0013]) |

Sources: [R3R6] "R3 result" (R1 and R3 totals), [R3R6-gates-R3], [R3R6-gates-R6] ("totals nonzero" for R3, R5 and R6); [R1R2] "R5 results" (C4 of R5); [owner-note] §28 (C4 of R1); [R3R6] "R6 result" (C4 of R6).

## 9. Compute

The full preset runs in 2739 s on the GPU (R5, clean) and 17 031 s on the CPU at `LPC_THREADS=8` (R6, possibly shared; above the 4 h planning bound of plan amendment 1 A1, below 12 h). The GPU full run was 6.2 times faster than the CPU full run, and 1.65 times its own pilot ([R1R2] "R5 results"; [R3R6] "R6 result"). Peak host memory at full size was 4 978 192 384 B (R5) and 4 749 778 944 B (R6; "within 10 GB", [R3R6] "R6 result") (section 2).

## 10. Limitations

From the owner-decision drafts ([drafts] §5), with additions from the rulings of [owner-note] §35 and from this draft's reading of the records:

1. **Slow weak dependence.** Blocks of 5 absorb the short-range dependence measured on Lorenz-63 (V*(5)/V*(1) ×1.077). Dependence beyond 5 states (pooled V*(20)/V*(5) ×1.041, upper 1.090) cannot be resolved at n ≤ 1000. Lorenz-63 H1a at ρ = 1% has the largest acf(1) in both runs (selection-adjusted p 0.018 in R5).
2. **One realization per system and seed.** Every interval is conditional on one trajectory, library, noise and network realization, and H3c on the fitted A4 and A5. Everything said about dependence beyond 5 states rests on one realization per run.
3. **The gate depends on the device.** GPU and CPU build different contexts, so for the same seed they are different realizations. DEV-2 Chua V6 fails on the GPU (2.405e-3 against 1e-3) and passes on the CPU (3.3e-4), and 52 verdict-type leaves differ between R5 and R6 although the TD statistic passes.
4. **V6 Chua gate risk (DEF-0026).** About 4.6% per fresh seed for Chua (4.3% under the GPU law), 4.8% for any system. Combined V4 or V6 failure is about 11% to 25% per seed at full size. A failure in the sealed run is a hard stop referred to the owner, never retuned, with no pre-seal response rule.
5. **LM sensitivity (O5, DEF-0027).** The PLP estimator is the fixed 15-iteration Levenberg–Marquardt by design. On the DEV-0 doubling study (15 against 30 iterations, B = 500, one realization), the LM row is flagged on 5 of 18 primary parts (rule R after DEF-0028: N 5, X 6, U 7). The flag is reported per part and not corrected (owner ruling "report and flag only").
6. **Interval undercoverage (DEF-0020).** The pre-registered block-5 percentile intervals are kept; their undercoverage at these sizes is stated, together with the report-only block-sensitive label (owner ruling of 2026-10-18, [owner-note] §35, B6a).
7. **Small H3a regimes (DEF-0018).** Kept as is; event counts are reported per regime, and the exposure (a tiny regime can give an extreme log-rank p) is stated (owner ruling of 2026-10-18, [owner-note] §35, B6b).
8. **Equal-context tolerances not exercised.** R4 was not run, so no rehearsal pair tested tiers T1 to T3; those rest on smoke-size kernel-pair evidence (section 4).
9. **Finite-M bias and the κ_E range.** D5 is "not determined" on every system, so budget row 1 stays "not below 10%". H2c, H2d and H3c projections use the pre-registered κ_E range, not a point estimate (section 5.1).
10. **Wall times of the CPU runs are not clean** (other lanes may have shared the CPU), so the CPU timing is an upper bound.
11. **Reachability** is computed explicitly only for H3a and H2a(ii) (section 5.4).
12. **This report is hand-assembled** from committed tool outputs; it is not regenerated by one script from `results.json` as ROADMAP WU-0003.3 and the unit plan's acceptance criteria ask (REPRO.10). The `results.json` files themselves live under the ignored `runs/` trees of the run worktrees and no SHA-256 of them is committed; Appendix A identifies the committed record files by git blob id.
13. **Record inconsistencies, found while drafting.** (a) [R1R2] "R5 results" and [owner-note] §28 say that in R5 "chua interior no longer fires (margin +0.0054 within 0.0067 to 0.015)"; the tool output [R5-report] shows Chua interior +0.0054 firing and Lorenz-63 interior +0.0095 inside the band. This report follows the tool output. (b) [R1R2-gate] labels the V2 statistic (`crlb_ratio_*`) as "V6 keys", and [R5-gate] prints `integrator_max_dev` (the V6 statistic) in its V2 group. The gate flags themselves are correct; the R1 V6 value is not in any committed R1 file read for this draft.
14. **R0's record is committed only on branch `run/r0-e3b2645`**, not on `develop`.

## 11. What the owner ruled on this evidence

These are owner rulings recorded by the main session in [owner-note] (question tool; not ledger entries). The `DEC-nnnn` entries are drafted ([drafts] §1, §2) and are the owner's to enter.

- **Sample size:** keep the full preset (2000/1000/1000 states, sweep cells 1000, M = 200, B = 2000) (2026-10-18, §33).
- **Reproducibility tolerance:** bitwise for the same context on the same device type; the A6 per-leaf tolerances for equal contexts on different devices or hosts; the TD statistic (away-arm form, z level 2.394, bound 3.4) across devices, with verdict-type leaves reported, not failed (2026-10-18, §33; OF-5 §33; OF-2 §26).
- **Block length:** 5 for all three systems; the pooled permutation reading governs D2; report-only block-sensitive label (2026-10-17, §31).
- **κ_E:** the pre-registered range governs (2026-10-17, §29).
- **Confirmatory device:** one official sealed run on the CPU at `LPC_THREADS=8`; a GPU run of the same sealed seed as a cross-check judged by the TD statistic; the CPU verdict stands; each sealed use needs its own authorization (2026-10-18, §36, B4). To be pre-declared before the freeze.

---

## Appendix A. Sources (all on `develop` 7b6f6e6 unless a branch is named; git blob ids, first 12 characters)

| Key | Path | Blob |
| --- | --- | --- |
| [R0] | `docs/agent/records/work/WU-0003-R0.md` (branch `run/r0-e3b2645`) | 3e1ee475e251 |
| [R0-t0] | `docs/agent/records/work/WU-0003-R0-compare-dev0-t0.txt` (branch `run/r0-e3b2645`) | fb75568d66fa |
| [R0-gpu-cpu] | `docs/agent/records/work/WU-0003-R0-compare-gpu-cpu.txt` (branch `run/r0-e3b2645`) | e5a386bb3663 |
| [R1R2] | `docs/agent/records/work/WU-0003-R1R2.md` | d129414b2f18 |
| [R1R2-meta-r1] | `docs/agent/records/work/WU-0003-R1R2-run-meta-r1.json` | cc264a1f8ef6 |
| [R1R2-meta-r2] | `docs/agent/records/work/WU-0003-R1R2-run-meta-r2.json` | a723d4d10bec |
| [R1R2-compare] | `docs/agent/records/work/WU-0003-R1R2-compare-r1-r2.txt` | f5b3035d291a |
| [R1R2-gate] | `docs/agent/records/work/WU-0003-R1R2-gate-and-counts.txt` | 9cf57ed39d36 |
| [R1-report] | `docs/agent/records/work/WU-0003-R1R2-rehearsal-report-r1.txt` | 036ea903ce82 |
| [R5-meta] | `docs/agent/records/work/WU-0003-R1R2-R5-run-meta.json` | 009cf21e2052 |
| [R5-gate] | `docs/agent/records/work/WU-0003-R1R2-R5-gate-and-counts.txt` | 2baa4bc0ba77 |
| [R5-report] | `docs/agent/records/work/WU-0003-R1R2-R5-rehearsal-report-r5.txt` | 3786c2eb6ff7 |
| [R1-obs-R5] | `docs/agent/records/work/WU-0003-R1R2-R5-rehearsal-report-r1-observed-r5.txt` | 4f7789e697d3 |
| [R3R6] | `docs/agent/records/work/WU-0003-R3R6.md` | 38aadd482f74 |
| [R3-meta] | `docs/agent/records/work/WU-0003-R3R6-R3-run.meta.json` | 64cd5e2b7442 |
| [R6-meta] | `docs/agent/records/work/WU-0003-R3R6-R6-run.meta.json` | 9fbe320eee7b |
| [R3R6-gates-R3] | `docs/agent/records/work/WU-0003-R3R6-gates-clips-R3.txt` | 96a8baf7a6fd |
| [R3R6-gates-R6] | `docs/agent/records/work/WU-0003-R3R6-gates-clips-R6.txt` | 8128bedeafd0 |
| [R3-report] | `docs/agent/records/work/WU-0003-R3R6-report-R3.txt` | eae4add8d7dc |
| [R6-report] | `docs/agent/records/work/WU-0003-R3R6-report-R6.txt` | 90c5f6ada1db |
| [R3R6-compare-R1R3] | `docs/agent/records/work/WU-0003-R3R6-compare-R1-R3.txt` | 3002c66a9e99 |
| [R3R6-compare-R2R3] | `docs/agent/records/work/WU-0003-R3R6-compare-R2-R3.txt` | a5ec76f6f2c9 |
| [R3R6-compare-R5R6] | `docs/agent/records/work/WU-0003-R3R6-compare-R5-R6.txt` | c7f35b5d1f2e |
| [9c-R1R3] | `docs/agent/records/work/WU-0003-9c-compare-R1R3.txt` | 41a5b109af1c |
| [9c-R5R6] | `docs/agent/records/work/WU-0003-9c-compare-R5R6.txt` | 7e5b6c5b45e4 |
| [8d-r1] | `docs/agent/records/work/WU-0003-8d-diagnostics-r1.txt` | d9774bca9ef5 |
| [8d-r5] | `docs/agent/records/work/WU-0003-8d-diagnostics-r5.txt` | a8e5b4fbe18d |
| [lm-v3] | `docs/study/lm_doubling_dev0_report_v3.md` | 0d49df01be76 |
| [block-length] | `docs/agent/notes/2026-10-17-math-block-length.md` | 241796c46995 |
| [owner-note] | `docs/agent/notes/2026-10-11-amendments-for-owner.md` | 3fb1db08b820 |
| [drafts] | `docs/agent/notes/2026-10-18-owner-decision-drafts.md` | c3851c2ae0eb |

Run outputs (`results.json`, the states dumps) are under `runs/` in the run worktrees `lpcstudy-wt/run/r1-c9bb981` (R1, R2, R5) and `lpcstudy-wt/run/r3r6-c9bb981` (R3, R6); they are not committed.
