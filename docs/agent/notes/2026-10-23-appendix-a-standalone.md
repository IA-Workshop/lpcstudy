**DEVELOPMENT APPENDIX: not a hypothesis test**

# Development appendix: not a hypothesis test

This document is built by `tools/findings_build.py appendix` from the development run files listed in its sources file. It holds the development appendix only: no host document, no result of the sealed run and no decision rule. `check` re-renders it from those files and accepts no other text.

## A. Development context [DEVELOPMENT]

Development context: not a hypothesis test. This appendix holds development seeds, exploratory, not confirmatory. Every value in it is a stored leaf of a development run, copied as stored and listed in the trace. No mean, spread, range, count of passes, pooled or overall verdict is made. The values of these runs appear only in this appendix, and none is compared with the result of any other section of this document (owner ruling D4).

### A.1 Ensemble by seed (the three systems of v3)

Runs of the full preset on development seeds, shown side by side by seed, one system after another. The rows of a system are the seeds; nothing is combined across them.

Development context: not a hypothesis test. Seeds: DEV-1, DEV-3, DEV-4; development seeds, exploratory, not confirmatory. Runs: provenance and completeness.

| Seed | Systems | Label | Preset | Commit | Backend | Complete | Dirty | Wall seconds | Start (UTC) | End (UTC) | SHA-256 of results.json |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DEV-1 | lorenz63, rossler, chua | DEVELOPMENT (DEV-1): not a hypothesis test | full | 3dec0864dcb2dc11e09ff82cc8016e9d7b9bc2ed | gpu | yes | no | 2775 | 2026-10-20T09:31:52+00:00 | 2026-10-20T10:18:06+00:00 | 0a4ef215c7262340cef3e95cc073c4b7a374c73d688a12ad68ed5517d6102860 |
| DEV-3 | lorenz63, rossler, chua | DEVELOPMENT (DEV-3): not a hypothesis test | full | 3dec0864dcb2dc11e09ff82cc8016e9d7b9bc2ed | gpu | yes | no | 2447 | 2026-10-20T10:18:54+00:00 | 2026-10-20T10:59:41+00:00 | 24a7c4b77a253ec34a1a6e301a932d3171ec22c1a70568941158c9a6787af247 |
| DEV-4 | lorenz63, rossler, chua | DEVELOPMENT (DEV-4): not a hypothesis test | full | 3dec0864dcb2dc11e09ff82cc8016e9d7b9bc2ed | gpu | yes | no | 2316 | 2026-10-20T10:59:56+00:00 | 2026-10-20T11:38:32+00:00 | 8eadc3992bcbffbeb399c46523eb308d351eb081937a622029119f68861c5655 |

Development context: not a hypothesis test. Seeds: DEV-1, DEV-3, DEV-4; development seeds, exploratory, not confirmatory. Validation gate: stored flags (V3 is reported, no bar).

| System | Seed | V1 | V2 | V4 | V5 | V6 | V7 | gate_pass |
|---|---|---|---|---|---|---|---|---|
| lorenz63 | DEV-1 | yes | yes | yes | yes | yes | yes | yes |
| lorenz63 | DEV-3 | yes | yes | yes | yes | yes | yes | yes |
| lorenz63 | DEV-4 | yes | yes | yes | yes | yes | yes | yes |
| rossler | DEV-1 | yes | yes | yes | yes | yes | yes | yes |
| rossler | DEV-3 | yes | yes | yes | yes | yes | yes | yes |
| rossler | DEV-4 | yes | yes | yes | yes | yes | yes | yes |
| chua | DEV-1 | yes | yes | yes | yes | yes | yes | yes |
| chua | DEV-3 | yes | yes | yes | yes | yes | yes | yes |
| chua | DEV-4 | yes | yes | yes | yes | yes | yes | yes |

A system whose stored gate_pass is not true is marked PROVISIONAL on every line below that belongs to it. Its words are shown as stored and the failure is reported, never repaired (v3 §6, E0, DEC-0027, DEC-0031). Marked in this part: none.

Development context: not a hypothesis test. Seeds: DEV-1, DEV-3, DEV-4; development seeds, exploratory, not confirmatory. Reported values (no bar).

| System | Seed | lambda_max (stored) | CP median VPT (V3, reported, no bar) | V7 median slope |
|---|---|---|---|---|
| lorenz63 | DEV-1 | 0.9057 | 2 | 1.0012 |
| lorenz63 | DEV-3 | 0.9057 | 2.03 | 1.0009 |
| lorenz63 | DEV-4 | 0.9057 | 2.03 | 1.0011 |
| rossler | DEV-1 | 0.07172 | 3.3 | 1.0000 |
| rossler | DEV-3 | 0.07172 | 3.13 | 1.0000 |
| rossler | DEV-4 | 0.07172 | 3.23 | 1.0001 |
| chua | DEV-1 | 0.4409 | 2.9 | 1.0004 |
| chua | DEV-3 | 0.4409 | 2.9 | 1.0003 |
| chua | DEV-4 | 0.4409 | 2.97 | 1.0002 |

Development context: not a hypothesis test. Seeds: DEV-1, DEV-3, DEV-4; development seeds, exploratory, not confirmatory. Stored per-system verdict words, primary hypotheses.

| System | Seed | H2a | H2b | H3c |
|---|---|---|---|---|
| lorenz63 | DEV-1 | inconclusive | pass | pass |
| lorenz63 | DEV-3 | inconclusive | pass | inconclusive |
| lorenz63 | DEV-4 | inconclusive | pass | inconclusive |
| rossler | DEV-1 | fail | pass | pass |
| rossler | DEV-3 | fail | pass | pass |
| rossler | DEV-4 | fail | pass | pass |
| chua | DEV-1 | fail | pass | pass |
| chua | DEV-3 | fail | pass | inconclusive |
| chua | DEV-4 | fail | inconclusive | inconclusive |

Development context: not a hypothesis test. Seeds: DEV-1, DEV-3, DEV-4; development seeds, exploratory, not confirmatory. Stored per-system verdict words, secondary hypotheses.

| System | Seed | H1a | H1b | H1c | H1d | H2c | H2d | H2e | H3a | H3b |
|---|---|---|---|---|---|---|---|---|---|---|
| lorenz63 | DEV-1 | inconclusive | pass | fail | pass | fail | fail | pass | inconclusive | inconclusive |
| lorenz63 | DEV-3 | inconclusive | pass | fail | inconclusive | fail | fail | pass | inconclusive | inconclusive |
| lorenz63 | DEV-4 | pass | inconclusive | fail | pass | inconclusive | inconclusive | pass | inconclusive | fail |
| rossler | DEV-1 | pass | fail | pass | pass | inconclusive | pass | pass | inconclusive | inconclusive |
| rossler | DEV-3 | pass | fail | pass | pass | inconclusive | pass | pass | inconclusive | pass |
| rossler | DEV-4 | pass | fail | pass | pass | fail | pass | pass | inconclusive | pass |
| chua | DEV-1 | pass | pass | fail | inconclusive | fail | pass | pass | pass | inconclusive |
| chua | DEV-3 | pass | pass | fail | inconclusive | inconclusive | pass | pass | pass | inconclusive |
| chua | DEV-4 | inconclusive | pass | fail | inconclusive | inconclusive | pass | pass | inconclusive | inconclusive |

Development context: not a hypothesis test. Seeds: DEV-1, DEV-3, DEV-4; development seeds, exploratory, not confirmatory. Q-N readings and the reported gain bound (read, no pass or fail).

| System | Seed | Q-N logit | Q-N indicator | gain_bound |
|---|---|---|---|---|
| lorenz63 | DEV-1 | reduces | substantial | reported |
| lorenz63 | DEV-3 | reduces | substantial | reported |
| lorenz63 | DEV-4 | substantial | substantial | reported |
| rossler | DEV-1 | reduces | substantial | reported |
| rossler | DEV-3 | reduces | substantial | reported |
| rossler | DEV-4 | undetermined | substantial | reported |
| chua | DEV-1 | undetermined | substantial | reported |
| chua | DEV-3 | undetermined | substantial | reported |
| chua | DEV-4 | reduces | substantial | reported |

Development context: not a hypothesis test. Seeds: DEV-1, DEV-3, DEV-4; development seeds, exploratory, not confirmatory. Primary parts: stored estimate, interval and verdict.

| System | Seed | Part | Estimate | Interval | Level | Band | Verdict |
|---|---|---|---|---|---|---|---|
| lorenz63 | DEV-1 | H2a(i) | 0.09618 | [0.07453, 0.1172] | 0.9833 (design value, not stored) | interval below 0.1 (strict) | inconclusive |
| lorenz63 | DEV-1 | H2a(ii) zero | 0.02441 | [-0.04988, 0.09939] | 0.9833 (design value, not stored) | interval inside (−0.1, 0.1) (strict) | pass |
| lorenz63 | DEV-1 | H2a(ii) interior | 0.1372 | [0.04383, 0.2322] | 0.9833 (design value, not stored) | interval inside (−0.1, 0.1) (strict) | inconclusive |
| lorenz63 | DEV-1 | H2b(i) | 0.2352 | [0.1886, 0.2783] | 0.9833 (design value, not stored) | lower bound > 0 (strict) | pass |
| lorenz63 | DEV-1 | H2b(ii) | 0.07039 | [0.05001, 0.09156] | 0.9833 | lower bound > 0 (strict) | pass |
| lorenz63 | DEV-1 | H3c | 0.7105 | [0.5271, 0.8958] | 0.9833 | upper bound ≤ 1.05 (closed) | pass |
| lorenz63 | DEV-3 | H2a(i) | 0.1269 | [0.09376, 0.1533] | 0.9833 (design value, not stored) | interval below 0.1 (strict) | inconclusive |
| lorenz63 | DEV-3 | H2a(ii) zero | -0.05012 | [-0.1172, 0.03021] | 0.9833 (design value, not stored) | interval inside (−0.1, 0.1) (strict) | inconclusive |
| lorenz63 | DEV-3 | H2a(ii) interior | 0.173 | [0.07993, 0.2721] | 0.9833 (design value, not stored) | interval inside (−0.1, 0.1) (strict) | inconclusive |
| lorenz63 | DEV-3 | H2b(i) | 0.2471 | [0.1978, 0.2934] | 0.9833 (design value, not stored) | lower bound > 0 (strict) | pass |
| lorenz63 | DEV-3 | H2b(ii) | 0.05911 | [0.03659, 0.08476] | 0.9833 | lower bound > 0 (strict) | pass |
| lorenz63 | DEV-3 | H3c | 0.7939 | [0.5886, 1.125] | 0.9833 | upper bound ≤ 1.05 (closed) | inconclusive |
| lorenz63 | DEV-4 | H2a(i) | 0.09938 | [0.08136, 0.1205] | 0.9833 (design value, not stored) | interval below 0.1 (strict) | inconclusive |
| lorenz63 | DEV-4 | H2a(ii) zero | 0.04332 | [-0.03229, 0.1167] | 0.9833 (design value, not stored) | interval inside (−0.1, 0.1) (strict) | inconclusive |
| lorenz63 | DEV-4 | H2a(ii) interior | 0.156 | [0.04334, 0.2661] | 0.9833 (design value, not stored) | interval inside (−0.1, 0.1) (strict) | inconclusive |
| lorenz63 | DEV-4 | H2b(i) | 0.2587 | [0.2109, 0.307] | 0.9833 (design value, not stored) | lower bound > 0 (strict) | pass |
| lorenz63 | DEV-4 | H2b(ii) | 0.06757 | [0.0452, 0.08875] | 0.9833 | lower bound > 0 (strict) | pass |
| lorenz63 | DEV-4 | H3c | 0.9983 | [0.8118, 1.239] | 0.9833 | upper bound ≤ 1.05 (closed) | inconclusive |
| rossler | DEV-1 | H2a(i) | 0.2631 | [0.2332, 0.3068] | 0.9833 (design value, not stored) | interval below 0.1 (strict) | fail |
| rossler | DEV-1 | H2a(ii) zero | -0.04123 | [-0.1223, 0.04559] | 0.9833 (design value, not stored) | interval inside (−0.1, 0.1) (strict) | inconclusive |
| rossler | DEV-1 | H2a(ii) interior | -0.0202 | [-0.1167, 0.07393] | 0.9833 (design value, not stored) | interval inside (−0.1, 0.1) (strict) | inconclusive |
| rossler | DEV-1 | H2b(i) | 0.1141 | [0.06475, 0.1677] | 0.9833 (design value, not stored) | lower bound > 0 (strict) | pass |
| rossler | DEV-1 | H2b(ii) | 0.06492 | [0.04269, 0.08973] | 0.9833 | lower bound > 0 (strict) | pass |
| rossler | DEV-1 | H3c | 0.9685 | [0.9224, 1.014] | 0.9833 | upper bound ≤ 1.05 (closed) | pass |
| rossler | DEV-3 | H2a(i) | 0.2763 | [0.239, 0.309] | 0.9833 (design value, not stored) | interval below 0.1 (strict) | fail |
| rossler | DEV-3 | H2a(ii) zero | -0.02326 | [-0.1094, 0.06864] | 0.9833 (design value, not stored) | interval inside (−0.1, 0.1) (strict) | inconclusive |
| rossler | DEV-3 | H2a(ii) interior | -0.0558 | [-0.1629, 0.04628] | 0.9833 (design value, not stored) | interval inside (−0.1, 0.1) (strict) | inconclusive |
| rossler | DEV-3 | H2b(i) | 0.1987 | [0.1468, 0.2507] | 0.9833 (design value, not stored) | lower bound > 0 (strict) | pass |
| rossler | DEV-3 | H2b(ii) | 0.05353 | [0.0288, 0.07507] | 0.9833 | lower bound > 0 (strict) | pass |
| rossler | DEV-3 | H3c | 0.9897 | [0.9457, 1.035] | 0.9833 | upper bound ≤ 1.05 (closed) | pass |
| rossler | DEV-4 | H2a(i) | 0.2744 | [0.2486, 0.3056] | 0.9833 (design value, not stored) | interval below 0.1 (strict) | fail |
| rossler | DEV-4 | H2a(ii) zero | -0.04614 | [-0.1226, 0.02963] | 0.9833 (design value, not stored) | interval inside (−0.1, 0.1) (strict) | inconclusive |
| rossler | DEV-4 | H2a(ii) interior | 0.06591 | [-0.01515, 0.1538] | 0.9833 (design value, not stored) | interval inside (−0.1, 0.1) (strict) | inconclusive |
| rossler | DEV-4 | H2b(i) | 0.2331 | [0.1848, 0.283] | 0.9833 (design value, not stored) | lower bound > 0 (strict) | pass |
| rossler | DEV-4 | H2b(ii) | 0.05443 | [0.03018, 0.07794] | 0.9833 | lower bound > 0 (strict) | pass |
| rossler | DEV-4 | H3c | 0.9507 | [0.9083, 0.9906] | 0.9833 | upper bound ≤ 1.05 (closed) | pass |
| chua | DEV-1 | H2a(i) | 0.1648 | [0.1277, 0.1973] | 0.9833 (design value, not stored) | interval below 0.1 (strict) | fail |
| chua | DEV-1 | H2a(ii) zero | -0.01555 | [-0.0925, 0.067] | 0.9833 (design value, not stored) | interval inside (−0.1, 0.1) (strict) | pass |
| chua | DEV-1 | H2a(ii) interior | 0.1926 | [0.08444, 0.2922] | 0.9833 (design value, not stored) | interval inside (−0.1, 0.1) (strict) | inconclusive |
| chua | DEV-1 | H2b(i) | 0.2298 | [0.174, 0.279] | 0.9833 (design value, not stored) | lower bound > 0 (strict) | pass |
| chua | DEV-1 | H2b(ii) | 0.05757 | [0.03504, 0.07962] | 0.9833 | lower bound > 0 (strict) | pass |
| chua | DEV-1 | H3c | 0.9533 | [0.9026, 1.001] | 0.9833 | upper bound ≤ 1.05 (closed) | pass |
| chua | DEV-3 | H2a(i) | 0.1882 | [0.1474, 0.2237] | 0.9833 (design value, not stored) | interval below 0.1 (strict) | fail |
| chua | DEV-3 | H2a(ii) zero | -0.06327 | [-0.1434, 0.01502] | 0.9833 (design value, not stored) | interval inside (−0.1, 0.1) (strict) | inconclusive |
| chua | DEV-3 | H2a(ii) interior | 0.144 | [0.04015, 0.251] | 0.9833 (design value, not stored) | interval inside (−0.1, 0.1) (strict) | inconclusive |
| chua | DEV-3 | H2b(i) | 0.2459 | [0.1961, 0.2996] | 0.9833 (design value, not stored) | lower bound > 0 (strict) | pass |
| chua | DEV-3 | H2b(ii) | 0.04154 | [0.01525, 0.06636] | 0.9833 | lower bound > 0 (strict) | pass |
| chua | DEV-3 | H3c | 1.054 | [0.9794, 1.157] | 0.9833 | upper bound ≤ 1.05 (closed) | inconclusive |
| chua | DEV-4 | H2a(i) | 0.1727 | [0.1462, 0.2052] | 0.9833 (design value, not stored) | interval below 0.1 (strict) | fail |
| chua | DEV-4 | H2a(ii) zero | -0.04581 | [-0.1214, 0.02915] | 0.9833 (design value, not stored) | interval inside (−0.1, 0.1) (strict) | inconclusive |
| chua | DEV-4 | H2a(ii) interior | 0.2235 | [0.1327, 0.3164] | 0.9833 (design value, not stored) | interval inside (−0.1, 0.1) (strict) | fail |
| chua | DEV-4 | H2b(i) | 0.259 | [0.2093, 0.3103] | 0.9833 (design value, not stored) | lower bound > 0 (strict) | pass |
| chua | DEV-4 | H2b(ii) | 0.02235 | [-0.00507, 0.0472] | 0.9833 | lower bound > 0 (strict) | inconclusive |
| chua | DEV-4 | H3c | 1.025 | [0.9513, 1.089] | 0.9833 | upper bound ≤ 1.05 (closed) | inconclusive |

Level cells that show a design value: 36.

### A.2 Extension systems (outside the v3 design)

Systems outside the v3 design; exploratory readings pre-specified in WU-0021.2. Per-system only, no overall verdict: the stored per-system words are shown, no word is formed across systems and the decision rule of v3 §7 is not applied. Systems: hindmarsh_rose, hyper_jha, lorenz63_r166, lorenz96_4, rossler_hyper, rossler_z.

Development context: not a hypothesis test. Seeds: DEV-3; development seeds, exploratory, not confirmatory; systems outside the v3 design; exploratory readings pre-specified in WU-0021.2; per-system only, no overall verdict. Runs: provenance and completeness.

| Seed | Systems | Label | Preset | Commit | Backend | Complete | Dirty | Wall seconds | Start (UTC) | End (UTC) | SHA-256 of results.json |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DEV-3 | hindmarsh_rose PROVISIONAL | DEVELOPMENT (DEV-3): not a hypothesis test | full | 392a069d25a8efd2d9d74d46d3475ba17f010bbf | gpu | yes | no | 5167 | 2026-10-21T08:00:41+00:00 | 2026-10-21T09:26:48+00:00 | 090f82e0ba16aed9f01666d2ab4043f394f32c6cebc2273c7d804059f7b1b8e4 |
| DEV-3 | hyper_jha PROVISIONAL | DEVELOPMENT (DEV-3): not a hypothesis test | full | 392a069d25a8efd2d9d74d46d3475ba17f010bbf | gpu | yes | no | 4040 | 2026-10-21T08:00:41+00:00 | 2026-10-21T09:08:01+00:00 | 5edfd1deb91eac73e56701cbc8ee9abaa852b1c714e1571cd1e96be87c603b7a |
| DEV-3 | lorenz63_r166 PROVISIONAL | DEVELOPMENT (DEV-3): not a hypothesis test | full | 974519a81a4a53e62069b85ab04c8ce783e17106 | gpu | yes | no | 2721 | 2026-10-20T11:55:08+00:00 | 2026-10-20T12:40:29+00:00 | 183a151966ae5c851bd1bde05ab1e8ff7b82c7da13a0974a2896ef8e60671e4c |
| DEV-3 | lorenz96_4 PROVISIONAL | DEVELOPMENT (DEV-3): not a hypothesis test | full | 392a069d25a8efd2d9d74d46d3475ba17f010bbf | gpu | yes | no | 1302 | 2026-10-21T09:08:43+00:00 | 2026-10-21T09:30:25+00:00 | 8aaac680997ae24407526cba6f5cc55f7b5744d47330596e4ec03323c4da2e6b |
| DEV-3 | rossler_hyper | DEVELOPMENT (DEV-3): not a hypothesis test | full | 974519a81a4a53e62069b85ab04c8ce783e17106 | gpu | yes | no | 2833 | 2026-10-20T12:41:10+00:00 | 2026-10-20T13:28:23+00:00 | ac588151e6aad4efabf1be0e9977c4d3366d895d605722cf6a1c660c054ceffc |
| DEV-3 | rossler_z PROVISIONAL | DEVELOPMENT (DEV-3): not a hypothesis test | full | 974519a81a4a53e62069b85ab04c8ce783e17106 | gpu | yes | no | 904 | 2026-10-20T11:39:06+00:00 | 2026-10-20T11:54:10+00:00 | f95ae88a22bccfe04dba48aa1f23632243a5b3c8cd740b261f098a17c5fdbf93 |

Development context: not a hypothesis test. Seeds: DEV-3; development seeds, exploratory, not confirmatory; systems outside the v3 design; exploratory readings pre-specified in WU-0021.2; per-system only, no overall verdict. Validation gate: stored flags (V3 is reported, no bar).

| System | Seed | V1 | V2 | V4 | V5 | V6 | V7 | gate_pass |
|---|---|---|---|---|---|---|---|---|
| hindmarsh_rose PROVISIONAL | DEV-3 | yes | yes | yes | yes | yes | no | no |
| hyper_jha PROVISIONAL | DEV-3 | yes | yes | yes | yes | yes | no | no |
| lorenz63_r166 PROVISIONAL | DEV-3 | yes | yes | yes | yes | yes | no | no |
| lorenz96_4 PROVISIONAL | DEV-3 | yes | yes | yes | yes | yes | no | no |
| rossler_hyper | DEV-3 | yes | yes | yes | yes | yes | yes | yes |
| rossler_z PROVISIONAL | DEV-3 | yes | yes | yes | yes | yes | no | no |

A system whose stored gate_pass is not true is marked PROVISIONAL on every line below that belongs to it. Its words are shown as stored and the failure is reported, never repaired (v3 §6, E0, DEC-0027, DEC-0031). Marked in this part: hindmarsh_rose (seed DEV-3: V7); hyper_jha (seed DEV-3: V7); lorenz63_r166 (seed DEV-3: V7); lorenz96_4 (seed DEV-3: V7); rossler_z (seed DEV-3: V7).

Development context: not a hypothesis test. Seeds: DEV-3; development seeds, exploratory, not confirmatory; systems outside the v3 design; exploratory readings pre-specified in WU-0021.2; per-system only, no overall verdict. Reported values (no bar).

| System | Seed | lambda_max (stored) | CP median VPT (V3, reported, no bar) | V7 median slope |
|---|---|---|---|---|
| hindmarsh_rose PROVISIONAL | DEV-3 | 0.2168 | 0.867 | 0.4054 |
| hyper_jha PROVISIONAL | DEV-3 | 0.3596 | 0.367 | 1.0047 |
| lorenz63_r166 PROVISIONAL | DEV-3 | 0.6224 | 3.37 | 0.9268 |
| lorenz96_4 PROVISIONAL | DEV-3 | 1.196 | 0.9 | 1.0109 |
| rossler_hyper | DEV-3 | 0.1127 | 1.57 | 1.0004 |
| rossler_z PROVISIONAL | DEV-3 | 0.07165 | 0.467 | 0.8718 |

Development context: not a hypothesis test. Seeds: DEV-3; development seeds, exploratory, not confirmatory; systems outside the v3 design; exploratory readings pre-specified in WU-0021.2; per-system only, no overall verdict. Stored per-system verdict words, primary hypotheses.

| System | Seed | H2a | H2b | H3c |
|---|---|---|---|---|
| hindmarsh_rose PROVISIONAL | DEV-3 | inconclusive | fail | pass |
| hyper_jha PROVISIONAL | DEV-3 | fail | pass | pass |
| lorenz63_r166 PROVISIONAL | DEV-3 | fail | inconclusive | pass |
| lorenz96_4 PROVISIONAL | DEV-3 | fail | pass | pass |
| rossler_hyper | DEV-3 | fail | pass | inconclusive |
| rossler_z PROVISIONAL | DEV-3 | fail | fail | pass |

Development context: not a hypothesis test. Seeds: DEV-3; development seeds, exploratory, not confirmatory; systems outside the v3 design; exploratory readings pre-specified in WU-0021.2; per-system only, no overall verdict. Stored per-system verdict words, secondary hypotheses.

| System | Seed | H1a | H1b | H1c | H1d | H2c | H2d | H2e | H3a | H3b |
|---|---|---|---|---|---|---|---|---|---|---|
| hindmarsh_rose PROVISIONAL | DEV-3 | fail | fail | fail | fail | fail | fail | inconclusive | inconclusive | inconclusive |
| hyper_jha PROVISIONAL | DEV-3 | inconclusive | fail | fail | fail | fail | inconclusive | fail | pass | fail |
| lorenz63_r166 PROVISIONAL | DEV-3 | fail | fail | fail | fail | fail | inconclusive | inconclusive | pass | fail |
| lorenz96_4 PROVISIONAL | DEV-3 | inconclusive | fail | inconclusive | fail | fail | inconclusive | inconclusive | pass | fail |
| rossler_hyper | DEV-3 | pass | fail | pass | pass | inconclusive | inconclusive | pass | pass | fail |
| rossler_z PROVISIONAL | DEV-3 | fail | pass | fail | fail | inconclusive | pass | pass | inconclusive | fail |

Development context: not a hypothesis test. Seeds: DEV-3; development seeds, exploratory, not confirmatory; systems outside the v3 design; exploratory readings pre-specified in WU-0021.2; per-system only, no overall verdict. Q-N readings and the reported gain bound (read, no pass or fail).

| System | Seed | Q-N logit | Q-N indicator | gain_bound |
|---|---|---|---|---|
| hindmarsh_rose PROVISIONAL | DEV-3 | reduces | undetermined | reported |
| hyper_jha PROVISIONAL | DEV-3 | reduces | reduces | reported |
| lorenz63_r166 PROVISIONAL | DEV-3 | reduces | undetermined | reported |
| lorenz96_4 PROVISIONAL | DEV-3 | substantial | undetermined | reported |
| rossler_hyper | DEV-3 | reduces | substantial | reported |
| rossler_z PROVISIONAL | DEV-3 | reduces | substantial | reported |

## B. Trace

Every number quoted above is listed with its source and leaf path in `2026-10-23-appendix-a-standalone.trace.csv`. Run the `check` command of `tools/findings_build.py` on this directory to verify the document against the development files.

Leaves not found in the sources, written "not recorded": 0. Null leaves written "not computed": 0.
