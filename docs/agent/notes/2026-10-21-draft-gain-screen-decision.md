# Draft decision proposal for the owner: should the reported-only gain screen use P1(d′)? (C1.3)

**Status: draft, not applied; the owner decides.** The gain-bound row is reported only, with no pass/fail bar (v3 §2 last sentence; DEC-0016 O2). v3 §8 records that "the v3 screen is a change after the freeze to a reported-only quantity, recorded as a decision" (DEC-0033 M3), so a change here is within what the freeze allows, provided it is recorded as a decision and no verdict depends on it (none does). **No pre-registered v3 text is edited**; the sealed run's `results.json` is not recomputed by agents; development seeds only for any implementation work. Source: WU-0027, `2026-10-21-math-theory-verification.md`, findings V1, V3, V4, V12.

## 1. What the code does now (`analysis.gain_horizon_bound`, the "v1 statistic")

Per test state at the core cell, with θ = 0.2 and the noisy criterion √(MSE + ρ²) > θ:

1. T_C, T_P: first passages of the two single forecasters; `better = max(T_C, T_P)`.
2. T_h: first passage of the oracle hybrid (clipped optimal weight per horizon).
3. Screens: growth Λ̄ > 0; both single-forecaster passages uncensored; **centered** covariance `cross − mean_cp·mean_plp ≥ 0` at the horizon `better`.
4. Reported: fraction with gain = T_h − better ≤ ln 2/(2Λ̄) + 1 step, median and maximum gain, and the three screen counts.

ROADMAP WU-0002.15 (not built) plans to add the subset with **raw** C ≥ 0 at **every** horizon (P1(d)'s hypothesis), keeping the v1 numbers.

## 2. Where this differs from the theorems

- (a) `better` is the later single-forecaster passage, not the envelope's first passage T_m of min(E_C, E_P). They coincide for monotone error curves; for a curve that dips back under θ after crossing, T_m > max(T_C, T_P) and the reported gain exceeds T_h − T_m by the difference (A1.7 fine print).
- (b) P1(c) needs the **raw** cross-moment C = E[e_C e_P] ≥ 0; the screen uses the centered covariance. The DEV-0 counts "negative_covariance" (109, 162, 122 of 500) are therefore not "raw C < 0" counts (V4).
- (c) The ln 2/(2Λ̄) bound assumes exponential growth of the envelope at the rate fitted over the first LT and C ≥ 0 at every horizon; neither is checked by the screen, and the DEV-0 exceedances (4.5%, 9.7%, 7.7% of eligible states, largest 1.7–3.8 LT) are consistent with growth that slows between 1 LT and the crossing (N5: H1c's ratio 0.60 on Lorenz-63 says the error grows faster near the crossing than the amplifier over the first LT, i.e. the opposite direction there; the per-state picture needs the stored curves, Part C C2).

## 3. The P1(d′) alternative

P1(d′) (A1.8, verified in WU-0027 with the hypothesis fix V1): for any error curves, if the raw C ≥ 0 at the single step H₁ = T_m(√2θ′), then 0 ≤ T_h(θ) − T_m(θ) ≤ T_m(√2θ′) − T_m(θ′) in integer steps, exactly, for the optimal hybrid (the oracle hybrid is draw-independent, so the upper bound applies to it). In the study's units (noise in quadrature) the loosened level is θ′ = √(θ² − ρ²) scaled by √2, i.e. the noisy criterion at √(2θ² − ρ²), not √2θ (V12; at most 2.8% different under θ ≥ 3√2ρ).

What a P1(d′) screen would compute per state:

1. T_m(θ) from the envelope min(sq_cp, sq_plp) with the existing `characteristic_horizon` (one array call), and T_m at the level √(2θ² − ρ²).
2. Raw C at column H₁ = T_m(√2θ′) − 1: `m.cross[row, H₁ − 1] ≥ 0`.
3. Bound B = T_m(√2θ′) − T_m(θ′) steps, no +1; gain = T_h(θ) − T_m(θ).
4. Screens, each counted: envelope censored at θ; envelope censored at the √2 level; raw C < 0 at H₁. (Growth > 0 is not needed.)
5. Reported: the gain distribution, B's distribution, and the fraction with gain ≤ B.

**What it buys.** No growth fit, one checkable hypothesis at one step, exact in discrete steps, and a verification row in the sense of NVVUQ.14 (like `verification.P2c`): on the hybrid the code computes, the fraction within B must be exactly 1 wherever C(H₁) ≥ 0; any violation is a defect in the pipeline, not a property of the attractor.

**What it loses.** For the same reason it says nothing about the data: it is an identity-level consequence of the moments. The v3 §2 sentence "reported against the P1 bound" refers to the ln 2/(2Λ) form, whose exceedances carry the information "the envelope is not exponential at the fitted rate" or "C < 0 somewhere". A P1(d′) row alone would make the gain row uninformative.

## 4. Options

| Option | Content | Assessment |
| --- | --- | --- |
| A. Keep the plan (WU-0002.15) | add the raw-C-at-every-horizon subset to the ln 2/(2Λ̄) + 1 screen; keep v1 numbers | matches P1(d) as pre-registered; needs every horizon, so the subset will be small (DEV-0: raw C changes sign along the curve for many states) and the row stays a loose comparison |
| B. Replace by P1(d′) | §3 only | exact and fit-free, but uninformative about the data (§3, "what it loses") and a change of the pre-registered comparator |
| **C. Both (recommended)** | the ln 2/(2Λ̄) form as the reported gain row, with the WU-0002.15 raw-C subset and the envelope fix (a); **plus** P1(d′) as a verification row (`verification.P1d_prime`, 0 violations expected, counted screens) | keeps the pre-registered comparator and its reading; adds a check that can fail only through a bug; costs one function and one unit test with hand-built moments |

Recommended acceptance criteria for C, written before any code: a unit test with hand-built moments (independent reference: arrays written in the test) covering (i) a non-monotone CP curve where max(T_C, T_P) ≠ T_m, (ii) a state with centered covariance ≥ 0 and raw C < 0 at H₁ (screened out and counted once), (iii) a state censored at the √2 level only, (iv) the bound computed by NumPy in the test to 1e-15 relative and equal to T_m(√2θ′) − T_m(θ′) with no +1; the result has no `pass`, `threshold` or `verdict` key; a DEV-0 smoke differs from the pre-change smoke only by added leaves (leafdiff: 0 changed, 0 removed); the function is marked "needs owner review" as statistics code.

## 5. Cautions

- Reported-only quantity; no verdict, band, level or decision rule changes; the change is recorded as a decision (DEC-0033 M3 already anticipates it).
- No agent recomputes the sealed run; if the owner wants the new rows for CONF-1, that is a regeneration under the existing rules, by the owner.
- Development seeds for every implementation run; the usual blast-radius test discipline.
- The P1(d′) upper bound does not cover the deployable rules A3–A5 (draw-dependent weights, V1); the row is about the oracle hybrid only, as now.
