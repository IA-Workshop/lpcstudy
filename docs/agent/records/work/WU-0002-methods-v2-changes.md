# WU-0002: Code changes for Methods v2 §M15 and v3 identifiers

| Field | Value |
| --- | --- |
| Status | planned (MAY be split into smaller units) |
| Class | CSQ3 development |
| Agent(s) | — |

## Plan

**Scope.** Bring the code in line with the v3 design: the proposal and methods v3 doc, Methods v2 §M15, and the identifier map in `docs/study/decision_log_lpc.md`. Items:

1. **Library size.** Rename it to `n_lib` in configuration, labels and reports.
2. **Excess MSE and regime weights.**
   - Excess MSE is computed exactly as V(w) − V(w*) from the moments (Theorem P1), replacing c(w − w*)² with clipped w*.
   - The regime weight is clip(Σcᵢuᵢ / Σcᵢ) with unclipped uᵢ (Theorem P3a).
   - K selection: the smallest K in {2, 3, 4, 5, 6, 8} within 5% of the minimum calibration excess.
3. **Mechanism hypotheses.**
   - H1a (v2 H1b) fits the median ε_s² instead of the mean.
   - H1b (v2 H1c) gets a PLP-only verdict; the CP slope is reported.
   - H1d (v2 H1e) gets bootstrap intervals for the Spearman correlations; N̂ is reported, not tested.
4. **Q-N estimate.** Oracle-primary, with the four-way reading table; the deployable estimate is secondary.
5. **H2b and H2e.**
   - H2b(ii) becomes the mean paired change in w* from N_lib = 10³ to 10⁴ at ρ = 1%, at level 1 − 0.05/3; mean and median curves are reported with intervals.
   - H2e (v2 H2f) is the median per-state change in CP–PLP error correlation from 10³ to 10⁵ at ρ = 1% and 2%. The correlation is set to 0 where CP's error does not vary.
6. **Regime and allocator hypotheses.**
   - H3a: log-rank test only, with the IQR reported.
   - Remove v2 H3b.
   - H3c (v2 H3d): block-bootstrap interval on MSE_A5/MSE_A4, at level 1 − 0.05/3.
   - H2d: remove part (ii) and the shift experiment.
7. **Verdict logic** (v3 §7):
   - per system: pass, fail or inconclusive;
   - multi-part criteria pass only if every part passes, and fail if any part fails;
   - overall: supported, not supported or inconclusive;
   - remove "partially supported".
8. **Removals.** Remove A4f, Lorenz-96, transfer, the τ_d-halved variant and the shift cells.
9. **Validation and presets.**
   - Add V7 (estimator efficiency) to the validation gate.
   - Full preset: 1000 sweep states.
10. **Hypothesis identifiers.** Switch to the v3 identifiers everywhere: code, report, figure labels.
11. **DEF-0001.** Count and report every replacement, clip and fallback.

**Definition of done.** Every item is implemented with tests; the smoke and pilot presets run on DEV-0; the regression comparison passes; reviewed.

**Acceptance criteria** (fixed now):

- **Item 2.**
  - Exact excess MSE agrees with brute-force minimization of V(w) on a 10⁴-point grid of w, within 10⁻⁶ relative, on random moment triples, including clipped cases.
  - The regime weight agrees with a brute-force minimizer of Σ Vᵢ(w) within 10⁻⁶.
- **Items 3–6.**
  - Each statistic is tested against an independent computation on synthetic data with a known answer: for example, a Spearman interval against `scipy.stats.spearmanr` on data with known correlation, and a paired change against a hand calculation.
  - Verdict logic is tested on synthetic intervals covering every branch.
- **Regression on DEV-0 (CPU).** The pilot preset reproduces the v1 pilot values of every quantity this unit does not intend to change (oracle moments, w*, proxies, fitted coefficients) bit for bit, or within 10⁻¹² relative where the summation order changed. Every changed statistic is listed with its old and new value and the reason.
- **Tests.** The full test suite passes.

**Affected checks.** All tests; the smoke preset; the pilot preset on DEV-0 (about 1 hour on CPU, faster on GPU).

**Owner checkpoint.** The owner reviews the code that computes verdicts and statistics before the freeze (LPC.PC.11).

## Log

## Review

## Audit
