# Development results: ensemble DEV-1, DEV-3, DEV-4 and the six extension systems (internal summary for the owner)

**DEVELOPMENT (DEV-1, DEV-3, DEV-4): not a hypothesis test · UNPROMOTED · exploratory, not confirmatory.**

- **Author:** applied-mathematician (claude-opus-5-5), 2026-10-23, worktree `wu/ext-summary`.
- **Placement.** This note is internal. It is not placed beside the sealed CONF-1 result, and none of its numbers may be set beside that result. No CONF-1 number appears here. The promoted findings note was read only for its verdict vocabulary.
- **No overall verdict for the extension systems.** Their stored overall word is `per-system only` (DEC-0038 option (a)).
- **Unreviewed verdict code.** The owner's review of the verdict-reporting code is still pending (DEC-0038 addenda A1 and A2). That code covers `report.verdicts`, `extension_text` and the names in `EXTENSION_SYSTEMS`, and it produces those words.
- **Method.** Every number and word below is a stored leaf of `results.json` or `run.meta.json`. The scripts named in §10 print each one with its leaf path. Nothing below is recomputed. I computed only two kinds of quantity:
  - string comparisons of stored words;
  - one numerical diagnostic, the bootstrap Monte Carlo margin in §7. It changes no word.
- **Ensemble seeds.** No mean, standard deviation or range is taken across seeds (schedule O7). Seeds are shown side by side.

## 1. Runs

| Run | Seed | Device | Wall clock | Commit | complete | failed / skipped variants | Robustness |
|---|---|---|---|---|---|---|---|
| ens-DEV-1 (frozen 3 systems) | DEV-1 | GPU (RTX 4090) | 2777 s (46 min) | 3dec086 | true | 0 / 0 | run |
| ens-DEV-3 | DEV-3 | GPU | 2450 s (41 min) | 3dec086 | true | 0 / 0 | run |
| ens-DEV-4 | DEV-4 | GPU | 2319 s (39 min) | 3dec086 | true | 0 / 0 | run |
| S1 rossler_hyper | DEV-3 | GPU | 2835 s (47 min) | 974519a | true | 0 / 0 | skipped (flag) |
| S2 lorenz63_r166 | DEV-3 | GPU | 2723 s (45 min) | 974519a | true | 0 / 0 | skipped (flag) |
| S3 rossler_z | DEV-3 | GPU | 906 s (15 min) | 974519a | true | 0 / 0 | skipped (flag) |
| S4 hindmarsh_rose | DEV-3 | GPU | 5169 s (86 min) | 392a069 | true | 0 / 0 | skipped (flag) |
| S5 hyper_jha | DEV-3 | GPU | 4042 s (67 min) | 392a069 | true | 0 / 0 | skipped (flag) |
| S6 lorenz96_4 | DEV-3 | GPU | 1304 s (22 min) | 392a069 | true | 0 / 0 | skipped (flag) |

Notes on the runs:

- **Exit and labels.** Every run has exit code 0, `dirty` false, `promoted` false, and preset `full`.
- **Configuration.** The configurations are identical to ens-DEV-1 except for `core_systems`, `seed_id` and `seed`. All seven DEV-3 runs store the same seed integer.
- **Robustness flag.** `robustness_systems` is `[lorenz63, rossler]` in every configuration. The `--skip-robustness` flag therefore removes no experiment on an extension system.
- **Wall clocks.** S4 and S5 started together, at 08:00:40Z on 10-21, in the two development GPU slots of DEC-0039. S6 overlapped S4. Their wall clocks were measured on a shared GPU and are not comparable with the others.
- **Replicates.** Each extension system has exactly one run, on DEV-3. There is no seed-to-seed replicate (schedule O3).

## 2. Validation gate V1–V7 (V3 reported, not checked)

| System | V1 | V2 | V4 | V5 | V6 | V7 | Gate | Stored V7 numbers (band [0.9, 1.1] for each) |
|---|---|---|---|---|---|---|---|---|
| lorenz63, rossler, chua × DEV-1/3/4 | pass | pass | pass | pass | pass | pass | PASS (9 of 9) | medians δ/(ρν) 0.9975–1.013, slopes 1.000–1.001 |
| S1 rossler_hyper | pass | pass | pass | pass | pass | pass | **PASS** | medians 1.005 / 1.006 / 1.007 / 1.013; slope 1.000 |
| S2 lorenz63_r166 | pass | pass | pass | pass | pass | **FAIL** | **PROVISIONAL** | medians at ρ = 0.5 / 1 / 2 / 5%: **1.111 / 25.98 / 16.42 / 11.25**; slope 0.927 (pass) |
| S3 rossler_z | pass | pass | pass | pass | pass | **FAIL** | **PROVISIONAL** | medians 1.025 / 1.070 / **1.111** / 0.938; slope **0.872** (fail) |
| S4 hindmarsh_rose | pass | pass | pass | pass | pass | **FAIL** | **PROVISIONAL** | medians **67.91 / 52.46 / 32.46 / 17.20**; slope **0.405** (fail) |
| S5 hyper_jha | pass | pass | pass | pass | pass | **FAIL** | **PROVISIONAL** | medians 1.029 / 1.041 / 1.081 / **3.376**; slope 1.005 (pass) |
| S6 lorenz96_4 | pass | pass | pass | pass | pass | **FAIL** | **PROVISIONAL** | medians 1.023 / 1.037 / 1.094 / **2.753**; slope 1.011 (pass) |

Leaves: `systems/<s>/validation/gate`, `systems/<s>/V7/{efficiency_median_by_noise, median_slope, slope_pass}`. RESULTS.md prints "FAIL (results provisional)" for S2 to S6. The console log says "VALIDATION GATE FAILED … results are flagged as provisional".

**Why V7 failed, as stored.** The run's stored reason is the numbers in the table: the efficiency criterion of V7 (the median of δ/(ρν) at every ρ, and the median slope of ln δ on ln ρ) falls outside [0.9, 1.1].

- **S5 and S6** fail only at ρ = 5%.
- **S3** fails marginally at ρ = 2% and fails on the slope.
- **S2** fails at every ρ, by a factor of 10 to 26 at ρ ≥ 1%.
- **S4** fails at every ρ, by a factor of 17 to 68, and on the slope.

V7 has no `n_nonfinite` and drops no resample on any system.

**Why V7 might fail: hypotheses written before the runs, not tested here.** The specification notes give a possible mechanism: a wrong-basin or nonlinear-regime Levenberg–Marquardt estimate, where δ tracks the attractor size rather than ρν (specs-2 §4, §13; specs §4 on S3). Those notes predicted pass for S2, S5 and S6, "at risk" for S3, and "at risk / expecting PROVISIONAL" for S4. Nothing here tests that mechanism. Under v3 §6 E0, each failed system's verdicts are shown with the label and referred, and nothing is retuned.

**Other gate values** (extension systems, stored):

| Check | Range over the six systems | Band |
|---|---|---|
| V2 | 0.967–1.02 | [0.8, 1.2] |
| V4 half-width | 0.0162–0.0263 | ≤ 0.05 |
| V6 | 4.5·10⁻⁷ to 1.34·10⁻⁴ σ_x (largest on S3) | < 10⁻³ |
| V1 | ≤ 4.3·10⁻⁶ (S4 gain) | < 10⁻⁴ |

**Largest Lyapunov exponent against published values** (report only, not in the gate). Only S1 has a published referent: 0.112729 against 0.1121, +0.56%, "PASS: within 3%". S2 to S6 are stored "not validated: no confirmed published value at these parameters". For them the time unit (1 LT = 30 steps) rests on the code's own λ_max, with no external check.

## 3. Development ensemble, frozen systems (DEV-1, DEV-3, DEV-4)

### 3.1 Overall words per seed (`verdicts/<H>/verdict`)

| Hypothesis | DEV-1 | DEV-3 | DEV-4 | Same on all three |
|---|---|---|---|---|
| **H2a** (primary) | not supported | not supported | not supported | yes |
| **H2b** (primary) | `supported` | `supported` | inconclusive | **no** |
| **H3c** (primary) | `supported` | inconclusive | inconclusive | **no** |
| H1a | inconclusive | inconclusive | inconclusive | yes |
| H1b | not supported | not supported | not supported | yes |
| H1c | not supported | not supported | not supported | yes |
| H1d | inconclusive | inconclusive | inconclusive | yes |
| H2c | not supported | not supported | not supported | yes |
| H2d | not supported | not supported | inconclusive | **no** |
| H2e | `supported` | `supported` | `supported` | yes |
| H3a | inconclusive | inconclusive | inconclusive | yes |
| H3b | inconclusive | inconclusive | not supported | **no** |
| Q-N | estimate (read, no pass/fail) | same | same | yes |

`supported` is the stored word of a development run, and its label is "not a hypothesis test". It is not the sealed word "supported (preliminary, unpromoted)".

### 3.2 What flips across seeds (stored per-system and part words)

- **H2b on DEV-4.** chua turns inconclusive because H2b(ii), the library change, is inconclusive: interval [−0.00507, 0.0472], reason `interval meets band edge`. Every other H2b system and part reads `pass` on all three seeds.
- **H3c.** rossler passes on all three seeds. lorenz63 and chua pass on DEV-1 only and are inconclusive on DEV-3 and DEV-4, with reason `interval meets band edge` each time. No seed and no system gives fail.
- **H2a.** The per-system words are stable: lorenz63 inconclusive, rossler fail and chua fail on every seed. The parts move:
  - H2a(ii) zero is `pass` on DEV-1 for lorenz63 and chua, and inconclusive on DEV-3 and DEV-4;
  - H2a(ii) interior on chua is inconclusive on DEV-1 and DEV-3 and fail on DEV-4.
- **Secondaries, per system.** The words that differ are:
  - H1a: lorenz63 and chua;
  - H1b: lorenz63;
  - H1d: lorenz63;
  - H2c: all three systems;
  - H2d: lorenz63;
  - H3a: chua;
  - H3b: lorenz63 and rossler;
  - Q-N: all three systems.

  Every pass/fail-type flip runs between pass and inconclusive, or between fail and inconclusive. No per-system word goes from pass to fail across seeds. The Q-N readings also change (reduces, substantial, undetermined); they carry no pass or fail.

### 3.3 Primary intervals, frozen systems (level 0.9833; H2a(i) band: upper < 0.1; H2a(ii): inside (−0.1, 0.1); H2b: lower > 0; H3c: upper ≤ 1.05)

| System | Part | DEV-1 | DEV-3 | DEV-4 |
|---|---|---|---|---|
| lorenz63 | H2a(i) | 0.0962 [0.0745, 0.117] inc. | 0.127 [0.0938, 0.153] inc. | 0.0994 [0.0814, 0.121] inc. |
| lorenz63 | H2a(ii) zero | 0.0244 [−0.0499, 0.0994] pass | −0.0501 [−0.117, 0.0302] inc. | 0.0433 [−0.0323, 0.117] inc. |
| lorenz63 | H2a(ii) interior | 0.137 [0.0438, 0.232] inc. | 0.173 [0.0799, 0.272] inc. | 0.156 [0.0433, 0.266] inc. |
| lorenz63 | H2b(i) | 0.235 [0.189, 0.278] pass | 0.247 [0.198, 0.293] pass | 0.259 [0.211, 0.307] pass |
| lorenz63 | H2b(ii) | 0.0704 [0.0500, 0.0916] pass | 0.0591 [0.0366, 0.0848] pass | 0.0676 [0.0452, 0.0888] pass |
| lorenz63 | H3c | 0.711 [0.527, 0.896] pass | 0.794 [0.589, 1.125] inc. | 0.998 [0.812, 1.239] inc. |
| rossler | H2a(i) | 0.263 [0.233, 0.307] fail | 0.276 [0.239, 0.309] fail | 0.274 [0.249, 0.306] fail |
| rossler | H2a(ii) zero | −0.0412 [−0.122, 0.0456] inc. | −0.0233 [−0.109, 0.0686] inc. | −0.0461 [−0.123, 0.0296] inc. |
| rossler | H2a(ii) interior | −0.0202 [−0.117, 0.0739] inc. | −0.0558 [−0.163, 0.0463] inc. | 0.0659 [−0.0152, 0.154] inc. |
| rossler | H2b(i) | 0.114 [0.0648, 0.168] pass | 0.199 [0.147, 0.251] pass | 0.233 [0.185, 0.283] pass |
| rossler | H2b(ii) | 0.0649 [0.0427, 0.0897] pass | 0.0535 [0.0288, 0.0751] pass | 0.0544 [0.0302, 0.0779] pass |
| rossler | H3c | 0.969 [0.922, 1.014] pass | 0.990 [0.946, 1.035] pass | 0.951 [0.908, 0.991] pass |
| chua | H2a(i) | 0.165 [0.128, 0.197] fail | 0.188 [0.147, 0.224] fail | 0.173 [0.146, 0.205] fail |
| chua | H2a(ii) zero | −0.0156 [−0.0925, 0.0670] pass | −0.0633 [−0.143, 0.0150] inc. | −0.0458 [−0.121, 0.0292] inc. |
| chua | H2a(ii) interior | 0.193 [0.0844, 0.292] inc. | 0.144 [0.0402, 0.251] inc. | 0.224 [0.133, 0.316] fail |
| chua | H2b(i) | 0.230 [0.174, 0.279] pass | 0.246 [0.196, 0.300] pass | 0.259 [0.209, 0.310] pass |
| chua | H2b(ii) | 0.0576 [0.0350, 0.0796] pass | 0.0415 [0.0153, 0.0664] pass | 0.0224 [−0.00507, 0.0472] inc. |
| chua | H3c | 0.953 [0.903, 1.001] pass | 1.054 [0.979, 1.157] inc. | 1.025 [0.951, 1.089] inc. |

Leaves:

- H2a(i): `systems/<s>/H2a/{median_range, range_ci, part_i_verdict}`;
- H2a(ii): `.../H2a/part_ii/{zero,interior}/{partial_corr, ci, verdict}`;
- H2b: `.../H2b/noise/{mean_state_spearman, ci, verdict}` and `.../H2b/library_change/{mean_change, ci, level, verdict}`;
- H3c: `.../H3c/{A5_over_A4_mse, ci, level, verdict}`.

The level 0.9833 is stored for H2b(ii) and H3c. For H2a and H2b(i) it is the design value of v3 §7, and the results file does not store it. Endpoints are printed to three or four digits, while the words use the unrounded endpoints.

## 4. Extension systems, one compact table each (DEV-3; level 0.9833 as in §3.3)

### S1 rossler_hyper: gate PASS (the only extension system whose gate passes)

| Part | Estimate | Interval | Part word |
|---|---|---|---|
| H2a(i) | 0.1945 | [0.1479, 0.2458] | fail |
| H2a(ii) zero | −0.01999 | [−0.09713, 0.06449] | pass |
| H2a(ii) interior | 0.02349 | [−0.06761, 0.1185] | inconclusive |
| H2b(i) | 0.4096 | [0.3653, 0.4556] | pass |
| H2b(ii) | 0.03182 | [0.01086, 0.05168] | pass |
| H3c | 0.3274 | [0.145, 4.504] | inconclusive |

- **Per-system words.** Primaries: H2a fail, H2b pass, H3c inconclusive. Secondaries: H1a pass, H1b fail, H1c pass, H1d pass, H2c inconclusive, H2d inconclusive, H2e pass, H3a pass, H3b fail; Q-N reduces.
- **Limits.**
  - 420 of 1000 states are excluded from H2a(i).
  - Three verdicts are **clip-sensitive** (stored flags): H1b (|Δ|/hw 0.88; still fail at 20 σ_x), H2c (A4−A2 |Δ|/hw 2.5) and H2e. H3a invariance is "not guaranteed".
  - The handling footprint is the largest of any run. At the core cell, 658 502 of 195 840 000 error entries were clipped as nonfinite (0.34%), 2 399 of 816 000 H_ref draws (0.29%), and 6 890 of 816 000 LM Jacobians were nonfinite. The frozen systems show 0 to 1 error clips.
  - The H3c interval is very wide and skewed: [0.145, 4.504].

### S2 lorenz63_r166: PROVISIONAL (V7)

| Part | Estimate | Interval | Part word |
|---|---|---|---|
| H2a(i) | 0.2362 | [0.1667, 0.3188] | fail |
| H2a(ii) zero | 0.03787 | [−0.04573, 0.1085] | inconclusive |
| H2a(ii) interior | −0.1179 | [−0.2363, −0.01293] | inconclusive |
| H2b(i) | 0.2334 | [0.181, 0.2817] | pass |
| H2b(ii) | −0.008574 | [−0.03499, 0.01649] | inconclusive |
| H3c | 0.8994 | [0.8365, 0.976] | pass |

- **Per-system words.** Primaries: H2a fail, H2b inconclusive, H3c pass. Secondaries: H1a fail, H1b fail, H1c fail, H1d fail, H2c fail, H2d inconclusive, H2e inconclusive, H3a pass, H3b fail; Q-N reduces.
- **Limits.**
  - 605 of 1000 states are excluded from H2a(i).
  - H3a censoring is [4, 84, 15, 22] per regime (125 states). That is the largest of any run; every other run has 0 to 6.
  - 693 of 1000 states are ineligible for H1c (PLP).

### S3 rossler_z: PROVISIONAL (V7)

| Part | Estimate | Interval | Part word |
|---|---|---|---|
| H2a(i) | 0.2145 | [0.1833, 0.2584] | fail |
| H2a(ii) zero | 0.01603 | [−0.07028, 0.09484] | pass |
| H2a(ii) interior | −0.1832 | [−0.2634, −0.08966] | inconclusive |
| H2b(i) | 0.1327 | [0.08508, 0.1877] | pass |
| H2b(ii) | −0.01982 | [−0.0409, −0.002553] | fail |
| H3c | 0.9242 | [0.839, 1.007] | pass |

- **Per-system words.** Primaries: H2a fail, H2b fail, H3c pass. Secondaries: H1a fail, H1b pass, H1c fail, H1d fail, H2c inconclusive, H2d pass, H2e pass, H3a inconclusive, H3b fail; Q-N reduces.
- **Limits.**
  - 375 states are excluded from H2a(i), and 289 are noncontiguous.
  - H3a invariance is "not guaranteed": 446 calibration-oracle entries were clipped.
  - CP valid-prediction time is 0.47 LT (V3, reported).

### S4 hindmarsh_rose: PROVISIONAL (V7, the largest departure)

| Part | Estimate | Interval | Part word |
|---|---|---|---|
| H2a(i) | 0.09542 | [0.0642, 0.1828] | inconclusive |
| H2a(ii) zero | −0.004176 | [−0.08196, 0.07904] | pass |
| H2a(ii) interior | −0.07718 | [−0.1709, 0.0202] | inconclusive |
| H2b(i) | −0.05458 | [−0.108, −0.00137] | fail |
| H2b(ii) | 0.01784 | [−0.007791, 0.04557] | inconclusive |
| H3c | 0.806 | [0.7164, 0.894] | pass |

- **Per-system words.** Primaries: H2a inconclusive, H2b fail, H3c pass. Secondaries: H1a fail, H1b fail, H1c fail, H1d fail, H2c fail, H2d fail, H2e inconclusive, H3a inconclusive, H3b inconclusive; Q-N reduces.
- **Limits.**
  - H2a(i) rests on only 132 eligible states (868 excluded).
  - The word of H2b(i) sits 1.0 bootstrap Monte Carlo s.e. from the band edge (§7).
  - w* = 0 holds on only 53 states, just above the minimum of 50 that a Q-N part needs to be read.
  - 709 of 1000 states are ineligible for H1c.

### S5 hyper_jha: PROVISIONAL (V7)

| Part | Estimate | Interval | Part word |
|---|---|---|---|
| H2a(i) | 0.261 | [0.1732, 0.3874] | fail |
| H2a(ii) zero | −0.04939 | [−0.1132, 0.02276] | inconclusive |
| H2a(ii) interior | 0.2785 | [0.1753, 0.3773] | fail |
| H2b(i) | 0.4433 | [0.398, 0.4858] | pass |
| H2b(ii) | 0.04383 | [0.01546, 0.06929] | pass |
| H3c | 0.8411 | [0.8, 0.8962] | pass |

- **Per-system words.** Primaries: H2a fail, H2b pass, H3c pass. Secondaries: H1a inconclusive, H1b fail, H1c fail, H1d fail, H2c fail, H2d inconclusive, H2e fail, H3a pass, H3b fail; Q-N reduces.
- **Limits.**
  - H2a(i) rests on only 101 eligible states (899 excluded).
  - CP valid-prediction time is 0.37 LT (V3, reported).
  - The run shared the GPU with S4.

### S6 lorenz96_4: PROVISIONAL (V7)

| Part | Estimate | Interval | Part word |
|---|---|---|---|
| H2a(i) | 0.2787 | [0.1978, 0.3493] | fail |
| H2a(ii) zero | −0.04372 | [−0.1177, 0.02958] | inconclusive |
| H2a(ii) interior | 0.1162 | [0.02352, 0.2093] | inconclusive |
| H2b(i) | 0.4805 | [0.4318, 0.5254] | pass |
| H2b(ii) | 0.1283 | [0.1004, 0.1554] | pass |
| H3c | 0.7802 | [0.7142, 0.8633] | pass |

- **Per-system words.** Primaries: H2a fail, H2b pass, H3c pass. Secondaries: H1a inconclusive, H1b fail, H1c inconclusive, H1d fail, H2c fail, H2d inconclusive, H2e inconclusive, H3a pass, H3b fail; Q-N substantial.
- **Limits.**
  - 687 of 1000 states are excluded from H2a(i).

## 5. Where the stored words on the new attractors differ from those on the frozen systems

This is string membership only. The test for each extension word: does it appear among the nine frozen system-seed words of the ensemble, for the same hypothesis? No reading rule of the specification notes (§5 of both) is applied here.

| Hypothesis | Words on frozen systems (DEV-1/3/4) | Extension words not in that set |
|---|---|---|
| H2a | fail, inconclusive | none (fail on S1, S2, S3, S5, S6; inconclusive on S4) |
| H2b | pass, inconclusive | **fail** on S3 (via H2b(ii)) and S4 (via H2b(i)); both PROVISIONAL |
| H3c | pass, inconclusive | none (pass on S2 to S6; inconclusive on S1) |
| H1a | pass, inconclusive | **fail** on S2, S3, S4 (all PROVISIONAL) |
| H1c | fail, pass | **inconclusive** on S6 (PROVISIONAL) |
| H1d | pass, inconclusive | **fail** on S2, S3, S4, S5, S6 (all PROVISIONAL) |
| H2e | pass | **inconclusive** on S2, S4, S6; **fail** on S5 (all PROVISIONAL) |
| H1b, H2c, H2d, H3a, H3b, Q-N | (all words seen) | none |

Four points follow from the table:

1. Every word outside the frozen set occurs on a PROVISIONAL system.
2. S1 is the only extension system whose gate passes, and it shows no word outside the frozen set.
3. Among the primaries, only H2b has an outside word.
4. A frequency, not a new word: H3b reads fail on S1, S2, S3, S5 and S6. Among the frozen system-seed words, fail appears once (lorenz63 on DEV-4).

## 6. Where gates, exclusion, censoring and clipping limit the reading

1. **Gate.** Five of the six extension systems are PROVISIONAL through V7. Their words are "what the gated machinery would say" (specs-2 §5, rule 10). V7 compares the realized estimation error δ of the deployed estimator with its first-order prediction ρν (v3 §6). On those five systems, the PLP arm and every quantity built on δ or ν rest on an estimator whose efficiency check failed.
2. **The H2a(i) small-error restriction.** A state needs at least two horizons at which both r.m.s. errors are ≤ 0.5 σ_x. Excluded states:

   | Systems | Excluded of 1000 |
   |---|---|
   | frozen | 76–338 |
   | S1 | 420 |
   | S3 | 375 |
   | S2 | 605 |
   | S6 | 687 |
   | S4 | 868 |
   | S5 | 899 |

   On S4 and S5, H2a(i) describes about 10–13% of the test states.
3. **Kaplan–Meier censoring** is negligible, 0 to 6 states per run, except on S2, where H3a has 125 censored states.
4. **Clipping.** Clip sensitivity is "computed" in every run. Stored CLIP-SENSITIVE flags occur only on S1 (H1b, H2c, H2e). The frozen-system runs in this ensemble carry no flag.
5. **Precision.** The fifteen system-runs carry 53 inconclusive per-system words. The stored reason of 44 of them is `interval meets band edge`. The other 9 are H3a's "largest Holm-adjusted p ≥ 0.01". An inconclusive word means the run could not decide at this precision. It is not evidence of no effect.
6. **H2c compares against a different forecaster.** H2c's best single forecaster on calibration is A0 on S2, S3 and S4, and A1 everywhere else. On those three systems the stored part is `A4_minus_A0`, so their H2c words compare A4 with a different forecaster.
7. **Single seed.** Each extension word is one DEV-3 draw. §3.2 shows that on the frozen systems, H3c, the H2b library part and several secondaries change word between seeds. No extension word can be read as stable across seeds.

## 7. Uncertainty-budget remarks for the primaries (uq-budget skill; development numbers)

| Source | Type | Evidence in the runs | Size | In the interval? |
|---|---|---|---|---|
| Test-state sampling | aleatory | moving-block bootstrap, block 5, 2000 resamples | the intervals in §3.3 and §4 | yes |
| Bootstrap Monte Carlo | numerical | stored `ci_mc_se` per endpoint | max s.e./half-width ≤ 0.10 in 89 of 90 part-cells; **0.19 on S4 H2a(i)** (132 states) | no |
| Oracle MC (M = 200) | aleatory | V4 | median half-width 0.016–0.026 | propagated |
| RK4 discretization | numerical | V6 step halving | ≤ 1.34·10⁻⁴ σ_x | no |
| LM iteration / estimator | numerical | V2, V7; LM nonfinite counters | **V7 fails on S2–S6: unverified for those systems** | no |
| Round-off | numerical | float64, not estimated | — | no |
| Time unit (λ_max) | epistemic | published comparison | S1 +0.56%; S2–S6 no referent | no |
| Model form (exact model, scalar observable, one seed) | epistemic | not estimated | — | no |

**Bootstrap Monte Carlo margin** (script `edge_margin.py`). For each stored endpoint e with Monte Carlo s.e. s, and each band edge b, the script computes z = |e − b|/s. Five part words have z < 2:

| Run | Part | Stored word | z (s.e. from the edge) |
|---|---|---|---|
| DEV-1 lorenz63 | H2a(ii) zero | pass | 0.2 |
| DEV-1 chua | H2a(ii) zero | pass | 1.95 |
| S1 | H2a(ii) zero | pass | 1.4 |
| S3 | H2a(ii) zero | pass | 1.6 |
| S4 | H2b(i) | fail | 1.0 |

Only the S4 case can move a per-system word. If H2b(i) on S4 read inconclusive, S4's H2b word would become inconclusive, because H2b(ii) there is already inconclusive. In the other four cases the per-system word is fixed by another part. The numerical rows that have evidence are at least 10 times smaller than the half-widths, except the two rows marked in bold in the table.

## 8. What these numbers can and cannot support

**Can support:**

- **Ensemble.** A description of how the stored words of the frozen pipeline vary across three development seeds.
- **Flips.** A list of the parts that change word between those seeds.
- **Extension systems.** A per-system, single-seed account of what the unchanged pipeline returns on six further attractors, with gate status and counts.
- **Leads for planning.** The list of words that differ from the frozen-system words is a set of leads for a pre-specified follow-up.

**Cannot support:**

- **Confirmatory claims.** No statement about any hypothesis is confirmatory. These are development seeds, the results are unpromoted, and the verdict code is not yet reviewed by the owner.
- **Overall verdicts.** There is no overall verdict on the extension systems.
- **Ranking.** Systems and forecasters are not ranked.
- **Pooling.** Seeds are not pooled and no seed-to-seed spread statistic is computed.
- **Comparison with CONF-1.** Nothing here may be compared with the sealed CONF-1 numbers or placed beside them.
- **Reading inconclusive as no effect.** No reading of "inconclusive" as "no effect".
- **Mechanisms.** No claim that a hypothesis holds or fails *because of* a system property (dimension, hyperchaos, intermittency, spiking). The PROVISIONAL label blocks this for five systems. One seed per system blocks it for all six.

A confirmatory statement on any new system would need a new sealed seed and freeze (DEC-0037 item 1), which is the owner's decision.

## 9. Plain-language synopsis for the owner (10 lines)

1. All nine development runs finished cleanly on the GPU. They are labeled development and are not a hypothesis test.
2. On the three original systems, the validation gate passed on all three seeds.
3. Across those seeds, H2a read "not supported" every time. H2b read "supported" twice and "inconclusive" once. H3c read "supported" once and "inconclusive" twice.
4. Every pass/fail word that changed between seeds moved to or from "inconclusive". None went from pass to fail.
5. Of the six new attractors, only the hyperchaotic Rössler system passed the gate. The other five failed check V7 and are provisional.
6. V7 failed because the estimator's error did not match its first-order prediction. On the spiking Hindmarsh–Rose system the median error was up to 68 times the predicted value.
7. On the new systems, H2a read fail on five of six, and H3c read pass on five of six. H2b read pass on three, inconclusive on one and fail on two.
8. Every word that never appeared on the original systems came from a provisional system.
9. Each new system was run once on one seed, and on some systems H2a(i) used only about one state in ten.
10. These are leads for a planned follow-up, not findings. "Inconclusive" does not mean "no effect".

## 10. Reproduction

The scripts and their outputs are in `docs/agent/notes/2026-10-23-extension-ensemble-summary/`:

- `extract.py`: every stored leaf used above, with leaf paths. Output: `extract.out.md`.
- `tables.py`: the per-system tables. Output: `tables.out.md`.
- `edge_margin.py`: the Monte Carlo margin. Output: `edge_margin.out.md`.

Each runs with `python3 -I <script>` (standard library only, CPU, read-only on the run folders under `lpcstudy-wt/run/`).
