# DEF-0005: exact document edits for the owner (v3, Methods v2, ROADMAP): DRAFT

Prepared 2026-10-18 by the planner (claude-opus-5-5). Read-only basis: `develop` e52177f (the repository copies of v3, Methods v2 and ROADMAP are unchanged since `f01360d`; v3 export sha256 `6fb99e8eeaac437b...`). Sources: freeze-blockers note B1 (and B4, B6, B7, B10); DEF-0005 lines in `defects.md`; amendments note §§1-3, 8, 9, 11, 13-15, 26-37; `decisions.md` DEC-0008 to DEC-0027; the ledger-batch drafts DEC-0028 to DEC-0032 (not yet entered); plan amendments 12-13 (draft); `lpcstudy/identifiers.py`, `analysis.py`, `allocation.py`, `pipeline.py`, `config.py`.

**Status.** Drafts only. Agents may not edit v3, Methods v2, the decision log or ROADMAP (GOV.49). The owner edits, records one ledger `amendment` per document, re-adopts the changed governed files, and re-exports v3 (the freeze records the SHA-256 of the final export, LPC.PC.8). DEF-0005 closes when these edits are made and the gain-bound row is opened or ruled out (DEF-0005 status line, 2026-10-18).

**Classes.** **R** = required for the freeze: the text is false against the code or a ruling, or it omits a definition the code uses to decide a verdict or the gate, or a ruling says "state it as a limitation". **N** = nice to have. **U** = the evidence or ruling is not yet decided by the owner (listed in §4). "R/U" = required, but its wording depends on an open point.

**Old text** is quoted verbatim from the export (Markdown escapes such as `w\*` kept so a search finds it). **New text** is written without escapes, for pasting into the Claude Doc.

---

## 0. Findings that change what B1 asked for (read first)

1. **The "13x margin" text is not in v3.** The export has no "13×", no "M5(d)" and no risk "R1". That text is in the WU-0002.14 unit file (`WU-0002.14-seeded-states.md` line 375, plan M5(d), and line 132, Risks R1), and the amended text is already appended there (lines 725-760). B1 and amendments note §15 place it in v3 by mistake. **No v3 replacement exists.** The v3 counterpart is an insertion that states the gate risk (V23e); whether v3 states it is undecided (U2).
2. **The F1 wording (OF-4) is not in v3.** It lives in WU-0008 M3, DEC-0024 point 2 (draft addendum A3) and `lpcstudy/budget.py`, which WU-0004b already corrected (614d889). **No v3 edit.**
3. **N2/N3 are WU-0006 test criteria, not v3 text.** The required edit is the ROADMAP WU-0006.3 row (P10). V20b is an optional v3 sentence on the Q-N estimand.
4. **v3 has no reproducibility section.** The device rule (B4) and the away-arm TD rule (OF-5) are inserted into §9 (V24).
5. **The Claude Doc cannot be inspected from here.** If it differs from the export, use the quoted old text as the search string.

---

## 1. Proposal and methods v3 (`docs/study/proposal_and_methods_v3.md`; the owner edits the Claude Doc and re-exports)

**V1. §2 RQ1 table, row H1a (line 79).** R. Source: DEC-0008 A4(h), A1, A5; amendments §2; WU-0002.4.
Old: `| H1a | The analog seed shrinks with library size as nearest-neighbor theory predicts | Fit of the median ε\_s² to b² N\_lib^(−2/d) + f² | interval of 1/d within ±25% of the independently estimated 1/d |`
New:
```
| H1a | The analog seed shrinks with library size as nearest-neighbor theory predicts | Fit of the median ε_s² to b² N_lib^(−2/d) + f², at ρ = 1% and 2%; the ratio of the fitted 1/d to the independently estimated 1/d (the mean over states of the per-state Levina–Bickel inverse estimates), with its interval from a joint block bootstrap; the floor f is reported | ratio interval inside [0.75, 1.25] (closed), at both ρ |
```

**V2. §2 RQ1 table, row H1c (line 81).** N. Source: DEC-0016 O3.
Old: `| Median of Λ̄ × dT/d ln θ (PLP) |` New: `| Median of Λ̄ × dT/d ln θ (PLP; the CP value is reported without a verdict) |`

**V3. §2 RQ1 table, row H1d (line 82).** N. Source: `analysis.h1d_proxies`; DEC-0008 A1.
Old: `| Spearman correlation, each | ≥ 0.7 |` New: `| Spearman correlation, each, on the first evaluation draw; N̂ reported, not tested | each lower bound ≥ 0.7 |`

**V4. §2 RQ1 table, row Q-N (line 83).** R. Source: DEC-0008 A4(a); DEC-0014; amendments §2, §8; WU-0002.6.
Old: `| Out-of-sample gain in R² (ΔR²) for predicting logit w\*, with exact (oracle) values | read by the table in §7 |`
New:
```
| Out-of-sample gain in R² (ΔR²), with exact (oracle) values, in two parts: for predicting logit w* on the states with 0 < w* < 1, and for predicting the indicator of w* = 0 | each part read by the table in §7; a part with fewer than 50 states is inconclusive |
```

**V5. §2 RQ2 table, row H2a (line 89).** R. Source: DEC-0008 A4(a), (a2), (b); amendments §1, §2; WU-0002.6; `analysis.quadratic_controls`, `h2a_initial_segments`, `h2a_part_ii`.
Old: `| (i) median range of w\* over 1, 2, 4 LT in the small-error regime; (ii) partial correlation of logit w\* with Λ̃ given both seeds | (i) interval below 0.1 and (ii) interval inside (−0.1, 0.1) |`
New:
```
| (i) median range of w* over the horizons 1, 2, 4 LT, up to the last horizon at which both r.m.s. errors are ≤ 0.5 σ_x (spans {1, 2} or {1, 2, 4} LT); states with fewer than two such horizons are excluded and counted; medians and counts per span reported; the complete-case {1, 2, 4} range reported as a sensitivity. (ii) two parts at H_ref, given both seeds: the partial correlation with Λ̃ of the indicator of w* = 0 (all test states) and of logit w* (states with 0 < w* < 1); the seed controls are x₁, x₂, x₁², x₂², x₁x₂ with x₁ = ln(ε_s/ρ), x₂ = ln(δ/ρ); the counts of w* = 0 and w* = 1 are reported, and a third part (the indicator of w* = 1) is added if w* = 1 exceeds 5% of states | (i) interval below 0.1 and (ii) every part's interval inside (−0.1, 0.1) |
```

**V6. §2 RQ2 table, row H2c (line 91).** R. Source: DEC-0008 A4(i); concordance D-20; WU-0002.8.
Old: `| Paired MSE differences at H\_ref | both upper bounds < 0 |`
New: `| Paired MSE differences at H_ref: A4 − A2, and A4 − the better single forecaster, chosen on the calibration split; A4o − A2 reported with its interval | both upper bounds < 0 |`

**V7. §2 RQ3 table, rows H3a and H3b (lines 99-100).** R. Source: DEC-0008 A3, A4(e), (f); DEC-0011 O1; B6b (DEC-0032 item 3 draft); WU-0002.8, WU-0004d.
Old: `| H3a | Regimes separate forecast horizons | Holm-adjusted log-rank tests between consecutive regimes | all p < 0.01 |`
New:
```
| H3a | Regimes separate forecast horizons | Holm-adjusted log-rank tests between regimes consecutive in Kaplan–Meier median horizon, one observation per test state (the first evaluation draw); at least 50 test states in total, no minimum per regime; a pair that cannot be computed enters at p = 1; events and censored states per regime reported | all adjusted p < 0.01; otherwise inconclusive (no equivalence margin is set, so H3a cannot fail) |
```
Old: `| H3b | Instability sets the horizon, not the weight | Importances in a weight tree and a horizon tree | weight tree: Λ̃ < 0.2; horizon tree: Λ̃ highest |`
New:
```
| H3b | Instability sets the horizon, not the weight | Importances in a weight tree and a horizon tree, each with 8 leaves, with block-bootstrap intervals over construction states (both trees refitted in each resample); D = horizon-tree importance of Λ̃ minus the largest other; the stability fraction is reported | weight tree: interval of Λ̃'s importance inside [0, 0.2); horizon tree: lower bound of D > 0 |
```

**V8. §2, sentence after the RQ3 table (line 103), gain bound.** U (U1). Source: DEC-0016 O2; concordance D-21; `analysis.gain_horizon_bound`.
Old: `The hybrid's horizon gain over the better forecaster is reported against the P1 bound, without a pass/fail bar.`
New, if the owner **opens the row** (P9 option A): no change.
New, if the owner **rules it out of scope** (P9 option B):
```
The hybrid's horizon gain over the better forecaster is reported against the P1 bound, without a pass/fail bar, on the states with positive growth, uncensored single-forecaster horizons and a nonnegative error covariance at the better forecaster's crossing. The subset that satisfies P1's hypotheses at every horizon is not computed (§8).
```

**V9. §4 Trajectories (lines 200-204).** R. Source: DEF-0017; DEC-0026 item 3; WU-0002.14 O8 with the R7 correction (unit file lines 293, 641, 680).
Old: `**Trajectories.** Each system gets three trajectories, after a 100-LT burn-in:`
New (replace that line; keep the three bullets; add the paragraph after them):
```
**Trajectories.** Each system gets three trajectories:
```
Insert after the bullet `- **separate:** used only to train the state estimator's first stage.`:
```
The statistics orbit (and the orbit used for λ_max) starts from a fixed state of the system and defines its units: σ_x, the mean and covariance, the delay, the state spacing and λ_max. It is the same for every seed and carries no test data. The main and separate trajectories each start from a seed-drawn point of the statistics orbit, perturbed by 10⁻⁶ in whitened units, and discard a 100-LT burn-in. A new seed therefore redraws every state used as data, the observation noise, the network initializations and the bootstrap resamples. An orbit that leaves a fixed bound (Lorenz-63 40, Rössler 25, Chua 3) stops the run.
```

**V10. §4 PLP, stage 2 and the wrong-basin sentence (lines 224-226).** R. Source: DEF-0027; owner O5 ("report and flag only", §29) and B7 (§35); DEC-0025 D1, D3; DEC-0026 item 9 (the convention was **not** adopted, so the text must not call the 15 iterations a definition).
Old: `2. Fifteen Levenberg–Marquardt iterations then fit the known model to the delay window. This is the maximum-likelihood estimate, so it reaches the Cramér–Rao floor ρν to first order. Here ν² = tr\[(JᵀJ)⁻¹\], with J the delay-map Jacobian.`
New:
```
2. Fifteen Levenberg–Marquardt iterations then fit the known model to the delay window. At convergence this is the maximum-likelihood estimate, which reaches the Cramér–Rao floor ρν to first order (checked by V7). Here ν² = tr[(JᵀJ)⁻¹], with J the delay-map Jacobian. Fifteen is the design value; it is not assumed that every estimate has converged by then.
```
Old: `The model is then integrated forward. About 2% of estimates (Lorenz-63, ρ = 1%) converge to a wrong basin. They are kept, because this is a real property of nonlinear estimation (Judd 2003).`
New:
```
The model is then integrated forward. About 2% of estimates (Lorenz-63, ρ = 1%, in the pilot) converge to a wrong basin. They are kept, because this is a real property of nonlinear estimation (Judd 2003). The final residual is reported in noise units, with the fraction of estimates above the 0.999 quantile of χ² with D − 3 degrees of freedom (18.47); this is a diagnostic, not a gate. The error left at the fifteenth iteration was measured on a development seed and is reported per primary quantity, not corrected (§8).
```

**V11. §4 Hybrid (line 228).** N. Source: DEC-0026 item 8 (WU-0002.11e OD1-OD7).
Append to the paragraph: `A clip-sensitivity flag recomputes the MSE- and weight-based verdicts with the clip at 20 σ_x and marks a verdict whose interval or outcome the clip moves; it is reported only and never marks results provisional.`

**V12. §4 sampling (line 239).** R. Source: DEC-0008 A5; amendments §2.
Old: `Evaluation states are at least 1 LT apart.` New: `Evaluation states are max(5·min(τ_ac, 1 LT), 1 LT) apart, where τ_ac is the autocorrelation time.`

**V13. §5 K rule (line 289).** R. Source: DEC-0008 A1, A5; DEC-0013 (horizon H_ref; ratified by DEC-0026 item 1); `pipeline.choose_regime_count`.
Old: `K is the smallest value in {2, 3, 4, 5, 6, 8} whose calibration error is within 5% of the best value in that set. Excess error is computed exactly from the moments, as V(w) − V(w\*).`
New:
```
K is the smallest value in {2, 3, 4, 5, 6, 8} whose mean calibration excess MSE at H_ref is at most 1.05 times the minimum over that set (a value exactly at 1.05 times counts as within). Excess error is computed exactly from the moments, as V(w) − V(w*).
```

**V14. §6 E0 and the validation checks (lines 297, 305, 313).**
- **V14a** R. Source: DEC-0008 A2; concordance D-28; Methods v2 §M10. Old (313): `- **V7.** The estimator is efficient: median δ/(ρν), and the median slope of ln δ on ln ρ, both in \[0.9, 1.1\].` New: `- **V7.** The estimator is efficient: median δ/(ρν) at every ρ, and the median per-state slope of ln δ on ln ρ, both in [0.9, 1.1].`
- **V14b** R/U (U3). Source: DEC-0016 O4; DEC-0027 (3); plan amendment 13 Y6 (owner to confirm). Old (297): `| E0 | Validation gate | Checks V1–V7 below; a failure marks that system's results provisional | all |` New: `| E0 | Validation gate | Checks V1–V7 below; a failure marks that system's results provisional, is reported, and is referred to the owner; it is never repaired by retuning or rerunning. Verdicts are computed and shown as provisional | all |`
- **V14c** N (export artifact). Old (305): `**Validation checks (****R****u****n**** ****a****t**** ****E0).**` New: `**Validation checks (run at E0).**`

**V15. §6 E6 robustness (line 303).** N. Source: DEC-0008 A4(g); DEF-0025; `pipeline.py` lines 174-177.
Old: `model parameters perturbed ±5% and ±10%;` New: `model parameters scaled by 1 ± 5% and 1 ± 10%, with one random sign per parameter drawn once per seed and system;`

**V16. §7 Intervals (lines 324-327).** R. Source: DEC-0008 A3; DEC-0012; DEF-0019; WU-0002.9b.
Old: `Every criterion in §2 is decided by an interval, and the rules below are fixed before the confirmatory run.`
New: `Every criterion in §2 except H3a is decided by an interval (H3a by Holm-adjusted p-values), and the rules below are fixed before the confirmatory run.`
Old: `- Moving-block bootstrap over test states in time order (Künsch 1989): blocks of 5 states, 2000 resamples.`
New:
```
- Moving-block bootstrap percentile intervals over test states in time order (Künsch 1989): blocks of 5 states, 2000 resamples (H3b resamples construction states). A resample whose statistic cannot be computed is counted and placed at the unfavourable tail, so too many failures make the bound infinite; it is never dropped.
```

**V17. §7 Verdict per system (lines 329-335).** R. Source: DEC-0008 A1, A3.
Insert after `A criterion with several parts passes only if every part passes, and fails if any part fails.`:
```
Bands are strict for H2a, H2b, H2c, H2e and H3a and closed for H1a to H1d, H2d and H3c, exactly as §2 writes them; endpoints are compared unrounded. A statistic that cannot be computed, or one computed on fewer than 50 states, is inconclusive, with the reason and the count reported.
```

**V18. §7 Overall verdict (lines 337-343).** R. Source: DEC-0016 O1 and its error-rate note.
Old: `- **inconclusive:** otherwise.` (the bullet under **Overall verdict**) New: `- **inconclusive:** otherwise, including when a system has no result.`
Old: `Requiring every system to pass is an intersection–union test, so it needs no further multiplicity correction.`
New: `Requiring every system to pass is an intersection–union test, so the error of "supported" needs no further multiplicity correction. The error of "not supported" is not controlled this way: with 95% intervals it can reach about 7.3% over three systems (about 14% for H2c's two parts).`

**V19. §7 Reading Q-N (line 345).** V19a R; V19b N. Source: V4 sources; DEF-0021; DEC-0018 O5.
- V19a. Old: `**Reading Q-N** (oracle ΔR² for logit w\* at 1 LT; the deployable version is secondary):` New: `**Reading Q-N** (oracle ΔR² at 1 LT, read separately for its two parts, logit w* on 0 < w* < 1 and the indicator of w* = 0; a part with fewer than 50 states is undetermined; the deployable version is secondary):`
- V19b. Insert after the Q-N table: `The interval covers the gain of the two fitted models with their training held fixed. Under no added information this gain is slightly negative (about −0.003 to −0.010 in simulation), so an interval that excludes 0 from below is expected and reads "reduces".`

**V20. §7 Precision (lines 360-365).** U (U5). Source: DEF-0022 (status line of 2026-10-18 superseding: "power finding not accepted by any owner answer"); R6 report lines 143-152; rehearsal report draft §5 (not adopted).
Old: `- H2a's second part can be refuted but essentially cannot pass: that would need a partial correlation within about 0.01 of zero.`
Draft new (only if the owner accepts DEF-0022's finding and adopts the WU-0003.3 report):
```
- H2a's second part can be refuted but can rarely pass. In the full-size development rehearsal (DEV-2, CPU) the margin 0.1 − half-width was +0.035 and +0.001 for the two Lorenz-63 parts, +0.020 for Rössler's indicator part, and +0.022 and −0.031 for the two Chua parts: a pass needs the partial correlation within about that margin of zero.
```
The Q-N (±0.04) and H2e (0.04) projections of lines 364-365 also differ from the rehearsal (H2e narrower on all systems). No replacement is drafted until the owner adopts the report.

**V21. §8 Known limitations (insert after line 380, before "Future work").** Source per bullet.
```
- **Interval coverage.** The block-5 percentile intervals undercover at these sample sizes: about 0.938 to 0.947 at 95% with independent states and 0.923 to 0.931 at lag-1 autocorrelation 0.3, which adds about 1 to 2 percentage points of false-verdict probability under dependence. The pre-registered intervals and block length are kept. A primary verdict that widening the half-width by √max(1, V*(10)/V*(5)) would change is labelled "block-sensitive" (report only).
- **Slow dependence.** Block 5 absorbs the short-range dependence measured on development seeds; dependence beyond 5 states cannot be resolved at n ≤ 1000.
- **Small regimes in H3a.** No minimum is set per regime, so a regime with one event among many censored states can give an extreme log-rank p and a Holm-adjusted pass. Events and censored states are reported per regime.
- **Iterative error of PLP.** On a development seed (15 against 30 and 60 iterations), the error left at the fifteenth iteration is not negligible against the interval half-width for 5 of the 18 primary parts (Lorenz-63 and Chua; none on Rössler). It is reported per part as a flag, projected to the full size by √(n_full/n_pilot), and not corrected; the uncertainty budget lists it as not estimated for the confirmatory run.
- **λ_max for Chua** at the study's parameters has no published reference value; the routine is validated on a published Chua case and on Lorenz-63 and Rössler.
```
Classes: interval coverage R (B6a, DEF-0020); slow dependence R (§31, with B6a); small regimes R (B6b, DEF-0018); iterative error R (O5, B7, DEF-0027); Chua λ_max R (DEC-0010, ratified DEC-0026 item 1).
Further bullets, **U** (not ruled):
```
- **Validation-gate risk.** V6 is the largest of 20 per-state step-halving deviations and is heavy-tailed; for Chua, RK4 is not fourth order across the diode breakpoints, so V6 is a heuristic indicator there. At a fresh seed V6 fails with probability about 4.4 to 4.6% for Chua, 0.11% for Lorenz-63 and 0 for Rössler; V4 or V6 together about 11 to 25% at full size. GPU and CPU build different trajectories for the same seed, so the gate outcome depends on the device.
- **H2a's second part** (only with V20): it can rarely pass at n = 1000.
- **H3a "supported"** needs a pass on all three systems; at full size a pass was reachable only on Chua in the development rehearsal.
- **Gain bound** (only with V8 option B): the subset satisfying P1's hypotheses at every horizon is not computed.
```
Gate risk: U2 (DEF-0026; the owner chose only the offline check, §26). H2a: U5. H3a: U8. Gain bound: U1.
N: `- **Doubled thinning.** Whether the intervals are stable when the state spacing is doubled is not checked (Methods v2 §M16).` (DEF-0009).

**V22. §9 After 30 October (lines 399-401): device, configuration, regeneration, TD rule.** R/U (U4). Source: owner B4 ruling (§36; DEC-0031 draft); WU-0003.6 tolerance ruling (§33; DEC-0028 draft); OF-5 (§33; WU-0003.9c, 91c93f5); DEF-0023.
Old:
```
1. Update the code to match this document (about one day).
2. Freeze the pre-registration: a dated copy of this document, the code commit and the configuration.
3. Run the full study on fresh seeds on the mentor's GPU workstation.
```
New:
```
1. Update the code to match this document.
2. Freeze the pre-registration: a dated copy of this document, the code commit and the configuration, including the device (CPU), the thread count (LPC_THREADS = 8) and the platform record.
3. Run the full study once on a sealed fresh seed, on the CPU of the mentor's workstation with LPC_THREADS = 8. This run's verdicts are the study's. A GPU run of the same seed is a cross-check only: GPU and CPU build different trajectories, so it is compared by a statistical test on the 18 primary parts (z = |d| / √(se₁² + se₂²), each standard error taken from the interval arm facing away from the other estimate; a part disagrees if z > 3.4). A disagreement, a differing verdict or a GPU gate failure is reported and changes no verdict.
4. Another actor regenerates the official run on the CPU from the same commit and inputs. On the same platform and thread count it must agree bitwise; otherwise it is judged by the declared per-quantity tolerances.
```

**V23. Not edited (stated so the owner can tick it):** "13× margin" and "M5(d)" (finding 1); F1 (finding 2); N2/N3 (finding 3; ROADMAP P10).

**v3 count:** 25 edit items (V1-V22, with V14a-c and V19a-b counted separately and V21 as one item). Required: V1, V4, V5, V6, V7, V9, V10, V12, V13, V14a, V16, V17, V18, V19a, V21 (five R bullets) = 15; R/U: V14b, V22 = 2; U: V8, V20, V21 (U bullets) = 3; N: V2, V3, V11, V14c, V15, V19b, V21 (DEF-0009 bullet) = 7. (Items split across classes counted once per class.)

---

## 2. Methods v2 (`docs/study/methods_experimental_procedures_v2.md`) and the decision log

**M-body. §M2 Trajectories, line 92.** R. Source: DEF-0017; DEC-0026 item 3; WU-0002.14 O8 and R7.
Old: `- **separate:** from a perturbed start; used only to train the learned initial guess of the state estimator.`
New:
```
- **separate:** used only to train the learned initial guess of the state estimator.

The statistics orbit and the Lyapunov (Benettin) orbit start from the system's fixed registry state and define its units (σ_x, the mean and covariance, τ_d, the spacing, λ_max); they are identical for every seed. The main and separate trajectories each start from a seed-drawn point of the statistics orbit, perturbed by 10⁻⁶ in whitened units (start = stats[k] + 10⁻⁶ C^(1/2) u, k uniform on the 2×10⁵ post-burn-in states, u standard normal, one generator make_rng(seed, "start", system) in the order k_main, u_main, k_est, u_est), and each discards a 100-LT burn-in. The raw start states and indices are recorded in the results.
```

**M14b. Insert after the M14 table (after line 505) a new dated table.** Ids are v3 with the v2 id in parentheses; † marks a change made after seeing pilot or development-seed data.

```
**Amendments after the v3 export (code v3, 11 to 18 October 2026).** The code follows v3 and these entries; where they differ from §M1 to §M13 above, these entries govern.

| # | Date | Change | Reason and source |
|---|---|---|---|
| 1 | 11 Oct | Hypothesis identifiers in code, results and report are v3's (map in the decision log); this document keeps the v2 ids | One table, `lpcstudy/identifiers.py` (WU-0002.2; DEF-0005) |
| 2 | 11 Oct | E5 (interventional shift) removed; v2 E6 Regimes is v3 E5, v2 E7 Robustness is v3 E6 | v3 drops it (WU-0002.1; DEC-0008 A2) |
| 3 | 11 Oct | H1a (H1b): the reference 1/d_LB is the mean over states of the per-state Levina–Bickel inverse estimates; the verdict is on the ratio (1/d_fit)/(1/d_LB), joint block bootstrap, pass iff inside [0.75, 1.25] (closed), at both ρ; the floor f is reported, never a pass condition† | Concordance D-19; changes the pilot's reference estimator (DEC-0008 A4(h), A5; WU-0002.4) |
| 4 | 11 Oct | Q-N: two parts, ΔR² for logit w* on 0 < w* < 1 and for the indicator 1{w* = 0}, each read by the table; a part with fewer than 50 states is undetermined; the boosted regressors use l2_regularization = 1.0 (as in the pilot code)† | 22–36% of states have w* = 0 (§M13 item 2) (DEC-0008 A4(a), (c); DEC-0014; WU-0002.6) |
| 5 | 11 Oct | H2a(i): the range is over initial segments {1, 2} or {1, 2, 4} LT up to the last horizon in the small-error regime (both r.m.s. errors ≤ 0.5 σ_x); states with fewer than two horizons excluded and counted; eligibility re-evaluated in each resample; complete-case {1, 2, 4} reported as a sensitivity | DEC-0008 A4(b) (WU-0002.6) |
| 6 | 11 Oct | H2a(ii): two parts, the partial correlation with Λ̃ of 1{w* = 0} (all states) and of logit w* (0 < w* < 1); controls x₁, x₂, x₁², x₂², x₁x₂ with x = (ln(ε_s/ρ), ln(δ/ρ)); both intervals inside (−0.1, 0.1); a third part 1{w* = 1} if w* = 1 exceeds 5% of states† | Changes the pilot's treatment of w* = 0 (DEC-0008 A4(a), (a2); WU-0002.6) |
| 7 | 11 Oct | H2c: the better single forecaster is chosen on the calibration split; A4o − A2 has a block-bootstrap interval | Concordance D-20 (DEC-0008 A4(i); WU-0002.8) |
| 8 | 11 Oct | H2e (H2f): a state where PLP's error is constant across draws also gets correlation 0, counted (stricter) | DEC-0011 O2 (WU-0002.7) |
| 9 | 11 Oct | H3a: one observation per state (the first evaluation draw); regimes ordered by KM median with a stable sort; at least 50 test states in total, no per-regime minimum; an uncomputable pair enters Holm at p = 1; pass or inconclusive only (no margin, so H3a cannot fail); events and censored states per regime reported (18 Oct) | DEC-0008 A3, A4(f); DEC-0011 O1; DEF-0013; DEF-0018 and owner ruling B6b (WU-0002.8, WU-0004d) |
| 10 | 11 Oct | H3b (H3c): weight and horizon trees with a fixed 8 leaves; block bootstrap (blocks of 5, 2000, 95%, percentile) over construction states, refitting both trees; weight-tree importance of Λ̃ in [0, 0.2); D = imp_t(Λ̃) − max other > 0; stability fraction reported | DEC-0008 A3, A4(e); DEC-0011 (WU-0002.8) |
| 11 | 11 Oct | A5 tree: two-output CART (squared error) on the construction profile over all draws, targets w*(H_ref) and log characteristic horizon standardized; min_samples_leaf = max(10, n_states·n_draws/50); random_state from make_rng | Documented as required (DEC-0008 A4(d)) |
| 12 | 11 Oct | K rule: mean calibration excess MSE at H_ref, K the smallest with excess ≤ 1.05 × minimum (a value at 1.05 counts as within) | §M7 names no horizon (DEC-0013; DEC-0008 A1, A5; WU-0002.3) |
| 13 | 11 Oct | Verdicts: bands strict for H2a, H2b, H2c, H2e (v2 H2f), H3a, closed for the others; endpoints unrounded; percentile intervals; a failed resample is counted at the unfavourable tail, the bound infinite iff failures ≥ ⌊(B − 1)a⌋ + 1, a = (1 − level)/2; an uncomputable statistic or one on fewer than 50 states is inconclusive with the reason; overall verdict over the three fixed systems, a missing system inconclusive; verdicts are not conditioned on the gate, a gate failure shows "results provisional" | DEC-0008 A1, A3; DEC-0012; DEC-0016 O1, O4; DEF-0019 (WU-0002.9, .9b) |
| 14 | 11 Oct | V7 is a plumbing check: the smoke preset need not pass it; it is judged at pilot size and above and may be retired once superseded | Owner ruling DEC-0015 (DEF-0014) |
| 15 | 11 Oct | E6 (E7) robustness: parameters scaled by (1 + p·s), one sign s ∈ {−1, +1} per parameter from make_rng(seed, system, "misspec"); a variant with D not above the state dimension is skipped and counted | DEC-0008 A4(g); DEF-0025 |
| 16 | 11–14 Oct | Randomness: every stream comes from make_rng(seed, labels); scikit-learn seeds are the raw seed below 2³² and a derived 32-bit value otherwise; the oracle pool is seed-labelled† | DEF-0010, DEF-0011; DEC-0008 B; DEC-0012 (WU-0002.6, WU-0002.14) |
| 17 | 14 Oct | Start states of the main and separate trajectories are seed-dependent (text in §M2) | DEF-0017; DEC-0026 item 3 (WU-0002.14) |
| 18 | 12 Oct | A Lyapunov orbit that leaves a fixed bound (Lorenz-63 40, Rössler 25, Chua 3) stops the run | DEF-0015; DEC-0017 Q1 (WU-0002.11c) |
| 19 | 11–17 Oct | Every silent handling of a bad value (replacement, clip, fallback, zero variance) is counted in the results under `handling` | DEF-0001 (WU-0002.11) |
| 20 | 12 Oct | Clip sensitivity: MSE- and weight-based verdicts are recomputed with the clip at 20 σ_x; a flag marks a moved verdict; report only, never provisional | DEC-0026 item 8 (WU-0002.11e) |
| 21 | 11–18 Oct | PLP: 15 LM iterations stay the design value, not a convention; the final residual c and c/ρ² and the fraction above 18.47 (χ²(4), 0.999) are reported as diagnostics; the iteration sensitivity measured on DEV-0 (15, 30, 60) is reported per primary part as a flag, and the budget's LM row reads "not estimated" with a pointer† | DEC-0025 D1, D3; DEF-0027; owner rulings O5 and B7 (WU-0005.4, WU-0005.6, WU-0004b) |
| 22 | 11–18 Oct | An uncertainty budget per primary QoI with the Monte Carlo error of the interval endpoints is reported; F1 is an indicative value, not a worst case | DEC-0024 with addenda A1, A2 and A3 (draft) (WU-0008, WU-0004b) |
| 23 | 17–18 Oct | Block length 5 and percentile intervals kept; their undercoverage is a stated limitation; a report-only "block-sensitive" label† | DEF-0020; owner ruling of 17 Oct and B6a (WU-0003.8d) |
| 24 | 18 Oct | The confirmatory run is on the CPU at LPC_THREADS = 8; a GPU run of the same seed is a cross-check judged by the away-arm TD statistic (bound 3.4) and informs only; the regeneration is on the CPU, bitwise at equal contexts, else by the declared tolerances† | Owner rulings B4 and WU-0003.6 (DEC-0031, DEC-0028 drafts); OF-5 (WU-0003.9c) |
| 25 | 18 Oct | A confirmatory run is refused on a dirty tree or an unknown commit | Owner ruling B8 (WU-0004a) |
| 26 | — | H2e (gain bound, v3 "reported"): [option A] the screen is the raw C ≥ 0 at every horizon, with the per-screen counts (WU-0002.15) / [option B] the subset "satisfying P1's hypotheses at every horizon" is not computed; the screen is the v1 one (centered covariance at the better forecaster's crossing) | DEC-0016 O2; concordance D-21; owner ruling (pending) |
```
Classes: R: 1-7, 9-13, 15-17, 21, 24 (U4 for its open items), 26 once chosen (U1). N: 8, 14, 18, 19, 20, 22, 23, 25. Not needed: the spacing max(5·min(τ_ac, 1 LT), 1 LT) equals §M3's two bullets; H1e (v3 H1d) intervals are already §M15 item 4.

**DL-1. Decision log (`docs/study/decision_log_lpc.md`), append a dated section.** R. Source: amendments §3; DEC-0008 A4(a), (h).
```
## 11 October 2026: definitions changed from the pilot's (owner rulings, DEC-0008)

| # | Decision | Reason |
|---|---|---|
| D7 | H1a's reference 1/d is the mean of the per-state Levina–Bickel inverse estimates, and the verdict is on the ratio (1/d_fit)/(1/d_LB). | The pilot compared against a pooled estimate; the ratio carries both fits' uncertainty (WU-0014 concordance). |
| D8 | H2a(ii) and Q-N treat w* = 0 as its own part (indicator), separately from logit w* on 0 < w* < 1. | 22–36% of states sit at w* = 0, where the logit is undefined. |
```

**Methods v2 count:** 1 body edit + 26 log rows + 1 decision-log entry = 28. Required 19 (body, DL-1, rows 1-7, 9-13, 15-17, 21, and row 24 with its open items), N 8, U 1 (row 26).

---

## 3. ROADMAP.md

**P1. WU-0003.3, task row (line 175) and definition-of-done row (line 186).** R/U (U6). Source: amendments §37 point 5; WU-0003.3a; rehearsal-report draft.
Old (175): `| WU-0003.3 | \`tools/precision_report.py\` and \`docs/study/dev_rehearsal_report.md\`: per v3 criterion the half-width at rehearsal size, the projection to the full preset by √(n_pilot/n_full), and reachable verdicts; H3c included |`
New:
```
| WU-0003.3 | `tools/rehearsal_report.py` (WU-0003.3a) and `docs/study/dev_rehearsal_report.md`: per v3 criterion the half-width at rehearsal size (R1, pilot) and observed at full size (R5, R6), the projection to the full preset by √(n_run/n_full) times the resampling factor for B, with the pre-registered ranges for κ_E (H2c, H2d, H3c) and the Q-N training size; reachability computed for H3a and H2a(ii); H3c included |
```
(the remaining cells, `applied-mathematician (projection), developer | WU-0003.2 | CSQ3 | ... | \`tests/unit/test_tools_precision.py\` | M |`, change only in the test file: `tests/unit/test_tools_rehearsal_report.py`).
Old (186), acceptance cell: `Running the script twice gives identical output; every number states its seed id; the table has one row per v3 criterion with half-width, projected half-width and reachable verdicts; the H3c row has an interval. \`test_tools_precision\` checks the projection factor √(n_pilot/n_full) on a hand case to 10⁻¹².`
New:
```
The tool's output is identical on two runs (golden reports, WU-0003.10); every number states its seed id; the table has one row per v3 criterion with half-width, projected half-width and reachable verdicts; the H3c row has an interval; `test_tools_rehearsal_report` checks the projection factors on hand cases. The report is assembled from the committed tool outputs and run records (git blob ids cited), not regenerated by one script; the `results.json` files are not committed. Done when the owner adopts the report and it is committed as `docs/study/dev_rehearsal_report.md`.
```
And the definition-of-done cell `Report regenerated from \`results.json\` by the script (REPRO.10)` becomes `Report assembled from the committed tool outputs; owner-adopted`.

**P2. WU-0003.4, task row (line 176) and definition-of-done row (line 187).** R. Source: B10 and §35; amendments §29 (draft tolerance), §33 (WU-0003.6 ruling); §34 point 6; WU-0003.9/.9b/.9c; WU-0004c.
Old (176), title cell: `Reproducibility: one core cell twice on GPU and once on CPU with the same seed; largest absolute and relative differences in w\*, seeds and verdict statistics; tolerance proposed at about ten times the GPU-to-GPU variation`
New:
```
Reproducibility: whole-pilot and full-preset comparisons with `tools/compare_runs.py` (WU-0003.9, .9b, .9c): R1 against R2 (DEV-1 pilot, GPU twice), R1/R2 against R3 (GPU against CPU), R5 against R6 (DEV-2 full, GPU against CPU), plus the R0 smoke probes; tiers chosen from the context digests; tolerance proposed per tier (T0 bitwise; T1 to T3 per-leaf rules; TD statistic across devices); `tests/gpu/test_reproducibility.py` (smoke DEV-0 twice on the GPU, bitwise)
```
Owner cell: `developer; applied-mathematician (tolerance)` unchanged; Depends-on cell becomes `WU-0003.1, WU-0003.9`; Serves cell unchanged.
Old (187), DoD and acceptance cells: `| Differences table in the unit file; tolerance proposal in \`decisions.md\` as a proposal | GPU-to-GPU and GPU-to-CPU maximum absolute and relative differences ... it is not rerun to make it pass. |`
New:
```
| Comparison records in the unit file; tolerance declaration drafted for WU-0003.6 | R1 against R2: tier T0, every leaf bitwise equal (20533 of 20533), so the rule "ten times the GPU-to-GPU difference" is degenerate and is replaced by "bitwise on the same device type and host". GPU against CPU (R0 smoke, R1/R3 pilot, R5/R6 full): tier TD (contexts differ), the 18 primary parts pass the TD statistic (away-arm z, bound 3.4) and the differing verdict-type leaves are counted (30 pilot, 52 full). V1's 1e-12 rule applies only to equal contexts (OF-2). Tiers T1 to T3 rest on the WU-0003.9 kernel-pair evidence (R4 not run). `tests/gpu/test_reproducibility.py` asserts the two GPU smoke runs are bitwise equal (tier T0) and is not rerun to make it pass. |
```

**P3. Phase D summary row (line 22).** N. Old: `| D. Rehearsal and precision | WU-0003 on the GPU: DEV-1 pilot rehearsal, precision report, reproducibility tolerance, optional DEV-2 full |` New: `| D. Rehearsal and precision | WU-0003 on the GPU and the CPU: DEV-1 pilot rehearsal, precision report, reproducibility tolerance, DEV-2 full |`

**P4. WU-0015.1 (line 210).** R/U (U4). Source: B4 (§36; DEC-0031 draft); plan amendment 13 Y1, Y3.
Old: `Pre-run checks: working tree clean at \`freeze-1\`, environment matches \`requirements.lock\`, GPU free, weekly hours allow 12 h, per-action authorization recorded (LPC.AUTH.6)`
New: `Pre-run checks: working tree clean at \`freeze-1\`, environment matches \`requirements.lock\`, no other preset run on the CPU, \`LPC_THREADS=8\` as frozen, the run lock free, per-action authorization recorded (LPC.AUTH.6)`

**P5. WU-0015.2 (line 211).** R. Source: as P4.
Old: `Confirmatory run: full preset, \`--confirmatory\`, seed and salt supplied by the owner at run time through the environment, on the GPU, under the lock`
New: `Confirmatory run (official): full preset, \`--confirmatory\`, seed and salt supplied by the owner at run time through the environment, on the CPU with \`LPC_THREADS=8\` through \`tools/run_preset.sh\`, under the lock`

**P6. New row after WU-0015.2.** R/U (U4: order and whether mandatory are not ruled, Y7(a), (b), (d)). Source: B4; Y2, Y3.
```
| WU-0015.2b | GPU cross-check: the same sealed seed, full preset, on the GPU under the lock; compared with the official run by `tools/compare_runs.py` (TD statistic, away-arm form, bound 3.4); the CPU verdicts stand and the GPU result informs only; outputs released only with the official run's release decision | human owner (separate per-action authorization, LPC.AUTH.6), or an agent under it | WU-0015.2 | CSQ2 | LPC.AUTH.6, LPC.PC.7, LPC.PC.18 | none | M (wall-clock) |
```

**P7. WU-0016.2 (line 215).** R. Source: B4 (§36: "the regeneration by another actor (WU-0016) is on the CPU"); Y4.
Old: `Regeneration run on the GPU (or on CPU if the owner authorizes the longer run), same commit, same inputs`
New: `Regeneration run on the CPU with \`LPC_THREADS=8\`, same commit, same inputs`

**P8. Phase F definition of done (line 219).** R. Source: as P4-P7.
Old: `wall-clock under 12 h. WU-0016.3:`
New: `wall-clock under 12 h; provenance records the CPU device and \`LPC_THREADS=8\`. WU-0015.2b: the comparison report is committed; a differing verdict-type leaf, a failing TD part or a GPU gate failure is recorded as information and changes no verdict. WU-0016.3:`
Old: `WU-0016.2 and .4: every QoI within tolerance and every verdict identical;`
New: `WU-0016.2 and .4: tier T0 (bitwise) on the same platform; otherwise every QoI within the WU-0003.6 tolerance of its tier and every verdict identical;`

**P9. Gain-bound row.** U (U1): the owner picks A or B.

*Option A: open it.* Insert after WU-0002.14 in the Phase B task table:
```
| WU-0002.15 | Gain-bound screen (concordance D-21(b), (c); DEC-0016 O2): add to `analysis.gain_horizon_bound` the subset of states with raw C = E[e_C e_P] ≥ 0 at every horizon (P1(c), (d)), its fraction within ln 2/(2Λ̄) + 1 step, and the per-screen counts (growth ≤ 0, censored, raw C < 0 at some horizon); keep the v1 screen's numbers; no bar; remove `GAIN_BOUND_PENDING` | applied-mathematician (horizon range of the screen), developer | WU-0002.9 | CSQ3 | §M11 row H2e; v3 §2 (after RQ3); DEF-0005 | `test_analysis`, `test_identifiers`, `test_report`; smoke | S |
```
and in the Phase B definition-of-done table:
```
| WU-0002.15 | Subset and counts in `results.json` and `RESULTS.md`; no pending marker | Unit, hand-built moments (independent reference: arrays written in the test): a state with raw C < 0 at exactly one horizon and centered covariance ≥ 0 is out of the subset and counted once; the subset fraction equals the hand count ratio exactly (dyadic case, e.g. 3/8); the bound equals ln 2/(2Λ̄) + 1 step computed by NumPy in the test to 1e-15 relative; no `pass`, `threshold` or `verdict` key; `identifiers.ROWS` has no `pending` entry and `test_identifiers` pins it. Integration: a DEV-0 smoke differs from the pre-change smoke only by added `gain_bound` leaves (leafdiff: 0 changed, 0 removed). Marked "needs owner review before freeze" (statistics code). |
```
*Option B: rule it out.* Ruling text for `decisions.md` (and a ledger `ruling`), and a ROADMAP §5 (Out of scope) bullet:
```
DEC-nnnn: The gain-bound screen of concordance D-21(b), (c) is ruled out of scope by the owner (<date>). The gain bound stays as implemented: reported against the P1 bound without a bar, on the states with positive growth, uncensored single-forecaster horizons and a nonnegative centered error covariance at the better forecaster's crossing, with the counts each screen excludes. The subset satisfying P1's hypotheses at every horizon (Methods v2 §M11 row H2e) is not computed and is stated as a limitation (v3 §8). The pending marker `GAIN_BOUND_PENDING` in `lpcstudy/identifiers.py` is replaced by a reference to this entry (text-only change; radius `test_identifiers`, `test_report`). This closes DEF-0005's gain-bound condition.
```
ROADMAP §5 bullet: `- the gain-bound screen on the raw covariance at every horizon (concordance D-21(b), (c)); ruled out by the owner, DEC-nnnn;`
Note on B: the marker's text ("ROADMAP row not yet opened") becomes false, so B still needs a one-line code change with review.

**P10. WU-0006.3 row (line 135) and acceptance (line 158): N2/N3 as the criteria.** R. Source: DEF-0021; DEC-0018 O5; DEC-0026 item 2; owner B9 ruling (§36: N2/N3 keep the code's reading).
Old (135) title cell: `Size of the Holm-adjusted log-rank family under equal hazards; null ΔR² interval coverage of 0`
New: `Size of the Holm-adjusted log-rank family under equal hazards; null ΔR²: false "distinct" rate (N2) and coverage of the conditional gain (N3), with coverage of 0 (N1) reported`
Old (158): `Null ΔR²: target independent of the fourth coordinate given the other three (synthetic, 1000 states, R = 500): the 95% interval contains 0 in at least 0.95 − 3·sqrt(0.95·0.05/500) = 0.921 of replications.`
New:
```
Null ΔR²: target independent of the fourth coordinate given the other three (synthetic, 3000 training and 1000 test states, R = 500): N2, the lower bound exceeds 0 in at most 22 of 500 replications; N3, the 95% interval contains the conditional gain of the two fitted models (training held fixed) in at least 461 of 500; N1, the interval contains 0, is reported (it fails by construction, DEF-0021). Under Option C (DEC-0026 item 2) N1 to N3 and the other nominal bounds are recorded, not asserted; the pre-registered consistency ranges are asserted.
```

**Other ROADMAP items of B1, already drafted, not repeated here:** amendments note §1 (WU-0002.1/.4/.6/.7/.8/.9/.10 wording, DEF-0010/0012 rows), §10 (smoke gate wording), §12 (WU-0001.6b name; WU-0002.12 baseline), §13 (WU-0005.4 L2 form; WU-0008 H3c "Included = no"), §14 (WU-0003.7-.11 and seed-step dependencies; WU-0016.3 forward); the WU-0005.6 id clash (§41); the `tests/test_core.py` statement (§4).

**ROADMAP count:** 10 items (P1-P10). Required: P2, P5, P7, P8, P10; R/U: P1, P4, P6; U: P9; N: P3.

---

## 4. Points the owner has not decided (the edits above that depend on them)

| # | Open point | Edits | What exists |
| --- | --- | --- | --- |
| U1 | Gain-bound row: open (WU-0002.15) or rule out of scope | V8, V21 (gain bullet), M14b row 26, P9 | DEC-0016 O2 asks the owner to open a row; no ruling. |
| U2 | Whether v3 states the V6/V4 gate risk and the device dependence of the gate | V21 (gate bullet) | §26: the owner chose only the offline check, not a risk-register entry; the limitations list in the decision drafts §5 includes it but is not adopted. |
| U3 | Sealed-run gate failure: "provisional and referred, never retuned" (V14b wording) vs a hard stop of the whole run | V14b | Plan amendment 13 Y6 is a reading "owner to confirm"; DEC-0027 (3) concerns P1. |
| U4 | Device rule details: DEC-0028 and DEC-0031 are drafts, not entries; DEC-0031 items 5 (do R1, R3, R6 satisfy "gate passes in the rehearsal" with R5 recorded) and 6 (GPU deterministic-ops flag); Y7 (a) order of the two sealed runs and whether the cross-check is mandatory, (b) whether a failing TD part opens a DEF, (c) whether the regeneration host must match | V22, M14b row 24, P4, P6, P8 | Rulings §33, §36. |
| U5 | DEF-0022's power finding and the v3 §7 precision text | V20, V21 (H2a bullet) | Status line 2026-10-18: "not accepted by any owner answer". |
| U6 | WU-0003.3: adopt the hand-assembled rehearsal report, accepting that it is not regenerated by one script (REPRO.10) and that `results.json` is not committed | P1 | §37: the draft is not adopted; C10 open. |
| U7 | CPU bitwise repeat at `LPC_THREADS=8` is not demonstrated (only a smoke at 4 threads, R0 (c)); the regeneration's T0 claim and P7/P8 rest on it | P2, P7, P8, V22 | §37 point 2. The owner may want a CPU repeat at 8 threads before the freeze. |
| U8 | Whether v3 states that H3a "supported" may be unreachable at full size | V21 (H3a bullet) | Freeze blockers D; no ruling. |
| U9 | The two DEF-0028 readings of rule R (half-width ≤ 0, NaN, infinite point estimate) behind the "5 of 18" LM flag | V10, V21 (LM bullet), row 21 | Amendments §30: to confirm before freeze. |
| U10 | Whether the Claude Doc matches the export | all V items | Cannot be checked from the repository. |

**Totals:** v3 25 items, Methods v2 and decision log 28, ROADMAP 10: **63 edits**. Required (R and R/U): 17 + 19 + 8 = **44**; undecided only (U): 3 + 1 + 1 = **5**; nice to have: 7 + 8 + 1 = **16**. The class counts add to 65 because V21's bullets fall in three classes.
