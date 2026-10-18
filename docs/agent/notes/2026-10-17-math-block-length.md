# Block length of the moving-block bootstrap after R1 and R5: one consolidated recommendation

**DEVELOPMENT (DEV-1, DEV-2).** Two realizations, so this is conditional evidence and not a hypothesis test of the study. It is a draft for the owner: every ruling below is the owner's.

- **Author:** applied-mathematician (claude-opus-5-5), 2026-10-17.
- **Scope:** read-only analysis of existing dumps. CPU only, about 20 s of compute in total. No preset run, no GPU, no test run, and the sealed seed was not touched.
- **Owner question answered:** the "D2 block length 5" item of amendments note §29 ("Report only, decide after R6"). It also gives an answer to OF-3 (§16, §21).
- **Inputs:**
  - the diagnostics records:
    - `docs/agent/records/work/WU-0003-R1R2-rehearsal-diagnostics-r1.txt` (R1: DEV-1, pilot, GPU, dump);
    - `docs/agent/records/work/WU-0003-R1R2-R5-rehearsal-diagnostics-r5.txt` (R5: DEV-2, full, GPU, dump);
  - the dumps and `results.json` of R1 and R5 under `lpcstudy-wt/run/r1-c9bb981/runs/{r1-gpu-dev1/pilot,r5-gpu-dev2/full}/`;
  - the plan (`WU-0003-dev-rehearsal.md`: A5 C8/C9, amendment B1 7.D2, F3);
  - the WU-0003 mathematics note §M4.2;
  - v3 §7 and Methods v2 "Intervals".
- **Missing runs:** R3 and R6 ran without the dump, so D2 is "not computable" for them and they add nothing here.

## 0. Answer in brief

1. **D2 firing is what no dependence produces, so it is not a defect signal.** The A5 rule fired on 4 of 24 primaries in each run. The permutation null keeps each system's cross-series dependence and gives these expected counts:

   | Run | Expected count under no dependence | P(count ≥ 4) |
   | --- | --- | --- |
   | R1 | 4.15 | 0.60 |
   | R5 | 2.23 | 0.19 |

   The two calibrated readings of B1 7.D2 fired nowhere in either run:
   - β̂₅: 0 of 48 primary series;
   - the pooled permutation reading: 0 of 6 system-runs, smallest p 0.025 against the 0.01 trigger.
2. **Serial dependence exists but block 5 captures it on the evidence available.**
   - **At lags of a few states the dependence is real.** It is clearest on Lorenz-63:
     - V\*(5)/V\*(1) is 7.7% above the no-dependence null (both runs, p = 0.003);
     - pooled over all 24 primaries in R5, the excess is 4.4% (p = 0.002).
   - **Beyond 5 states, pooled over both runs and all systems, the evidence is weak:**

     | Ratio | Point excess | One-sided 95% upper | p |
     | --- | --- | --- | --- |
     | V\*(10)/V\*(5) | 1.1% | 3.2% | 0.21 |
     | V\*(20)/V\*(5) | 4.1% | 9.0% | 0.075 |

     The only nominal signals do not survive multiplicity:
     - Lorenz-63 in R5 at b = 8 to 10 (p 0.010 to 0.022);
     - Rössler at b = 20 over both runs (p 0.035).
   - **No verdict changes in R5.** I widened each primary interval to its own block-10, block-20 or "plateau" variance (§2.5). In R1 one part changes: Rössler H1a ρ = 2%, whose lower bound 0.7594 sits 0.009 from the 0.75 edge (point 0.9818), so any widening above 4.2% moves it.
3. **Recommendation: keep L = 5** for all three systems.
   - **No amendment is needed to keep it.**
   - **Two additions for the owner, neither loosening anything:**
     - (a) rule OF-3 so that the pooled permutation reading governs the block-length design question, with the A5 rule and β̂₅ reported as information;
     - (b) optionally, a report-only "block-sensitive" qualifier on any primary verdict that the first-order block-10 widening would change (§4).
   - **The alternative, if the owner gives weight to the a-priori physical argument (§2.6),** is L = 10 for Lorenz-63 only. Its statistical cost at the confirmatory size n = 1000 is negligible (§3). Its administrative cost is large: two amendments, a recomputed WU-0006 table, code, and a new full-size rehearsal (§4.3).

## 1. Question 1: what D2 tests, and whether its firing means anything

### 1.1 Definition

V\*(b) is b times the variance (ddof 0) of the n − b + 1 overlapping block means of the influence series ψ. This is the exact moving-block bootstrap variance of the mean, with no resampling noise (M4.2).

To first order, the half-width of every primary interval is z·√(V\*(5)/n) of its ψ. This holds under these hypotheses:

- the statistic is asymptotically linear, with influence function ψ (M4.1);
- the series is stationary;
- the dependence is weak.

A ratio V\*(b)/V\*(5) > 1 for large b says the long-run variance is not yet reached at b = 5, so the block-5 interval is too narrow by about √(V\*(5)/V\*(∞)). The A5 rule asks this of each single series with fixed cut-offs: V\*(10)/V\*(5) > 1.1, or V\*(20)/V\*(5) > 1.15.

### 1.2 Calibration of the A5 rule

**The calibration is correct as stated (M4.2).** Under no dependence the ratio has a sampling SD of 0.108, 0.083 and 0.058 at n = 300, 500 and 1000 (for V\*(20)/V\*(5): 0.22, 0.17 and 0.12). The cut-offs sit only 1.3 to 1.9 SD above the null mean, which gives these trigger rates:

| | Pilot (R1) | Full (R5) |
| --- | --- | --- |
| Per series, no dependence | 0.21 (n = 300), 0.164 (n = 500) | 0.094 (n = 1000) |
| At least one of 24, no dependence | 0.993 | 0.906 |
| Per series, power at the φ = 0.3 stress | about 0.40 | about 0.40 |

The rule therefore **cannot distinguish "block 5 is inadequate" from "no dependence".** The reason is intrinsic: a single-series long-run variance at n ≤ 1000 has a relative SD of 6 to 20%, against a decision-relevant effect of 7 to 11%.

### 1.3 Observed against the null

The null is my own permutation null: 2000 permutations, one per system per draw, applied to all of that system's primary series as in the tool. Script `block_curve.py`, section C.

| Run | A5 fired (of 24) | Which series | Null mean (SD) | P(count ≥ obs) | P(count ≥ 1), null | Printed prediction |
| --- | --- | --- | --- | --- | --- | --- |
| R1 (DEV-1, pilot) | 4 | Rössler H2b(ii), Rössler H1a 2%, Chua H2a(ii) zero, Chua H1a 1% | 4.15 (1.94) | 0.60 | 0.988 | 0.993 |
| R5 (DEV-2, full) | 4 | L63 H2b(ii), L63 H1a 1%, Rössler H2a(ii) zero, Rössler H2b(i) | 2.23 (1.50) | 0.19 | 0.897 | 0.906 |

- **The predictions are confirmed.** The permutation P(at least one) matches the binomial prediction of F3 within its Monte Carlo error. The permutation keeps the cross-series correlation, which lowers P(at least one) slightly.
- **The fired sets do not overlap.** No series fires in both runs, and the systems flagged differ: R1 flags Rössler and Chua, R5 flags Lorenz-63 and Rössler.
- **The calibrated readings are quiet:**
  - β̂₅ fired on 0 of 24 in each run. Its geometric-acf premise failed on 8 of 78 series in R1 and 15 of 78 in R5, where it is "not used".
  - The pooled permutation reading fired on 0 of 3 systems in each run (p = 0.86, 0.18, 0.41 in R1; 0.025, 0.26, 0.57 in R5).

**Answer to Q1:**
- D2's A5 rule tests per series whether the block variance keeps rising past b = 5.
- Its firing at 4 of 24 is at the no-dependence expectation in R1 and within it in R5 (p = 0.19). It does not indicate a defect of block length 5.
- The "design question" flags in both runs come only from the A5 rule.

## 2. Question 2: is there dependence that block 5 under-corrects?

All numbers in this section are DEVELOPMENT (DEV-1 and DEV-2). Sources: `block_curve.out`, `max_series_null.out` and `verdict_sensitivity.out` in `2026-10-17-math-block-length-scripts/`.

### 2.1 Method

- The 24 primary ψ series per run are rebuilt with the diagnostics tool's own builders (`extract_series.py`). As a check, the extracted series reproduce every V\*(10)/V\*(5) and V\*(20)/V\*(5) printed in both records to the printed digits.
- For each series I compute V\*(b)/V\*(1) for b = 1 to 30. V\*(1) is the iid variance.
- The statistic is the mean of log V\*(b)/V\*(1) per system and pooled, and the contrast log V\*(b)/V\*(5). Each is tested against the same per-system permutation null. The null carries the O(b/n) downward bias of V\*(b), so "excess over null" is bias-corrected.
- The two runs use independent seeds, so they are combined as an equal-weight mean against the mean of their independent nulls.
- Independent algorithm: the Politis–White (2004; Patton–Politis–White 2009) automatic block length for each series.

### 2.2 Short-range dependence: present, and what block 5 is for

V\*(5)/V\*(1), excess over the null:

| Group | R1 | R5 | Both runs |
| --- | --- | --- | --- |
| Lorenz-63 | ×1.06 (p 0.089) | ×1.094 (p 0.001) | **×1.077 (p 0.003)** |
| Rössler | ×1.006 (p 0.44) | ×1.023 (p 0.21) | ×1.014 (p 0.29) |
| Chua | ×1.022 (p 0.32) | ×1.015 (p 0.28) | ×1.019 (p 0.24) |
| All 24 | ×1.029 (p 0.13) | **×1.044 (p 0.002)** | **×1.036 (p 0.009)** |

The study's influence series have weak positive short-range dependence, concentrated in Lorenz-63. This is the dependence the block bootstrap exists to absorb, and block 5 does absorb it: the V\*(b)/V\*(1) curve of Lorenz-63 rises from b = 1 to b = 5 in both runs.

### 2.3 Dependence beyond 5 states: weak and not reproduced

V\*(b)/V\*(5), excess over the null:

| Group | b | R1 | R5 | Both runs: factor (one-sided 95% upper), p |
| --- | --- | --- | --- | --- |
| Lorenz-63 | 10 | ×0.964 (p 0.84) | ×1.047 (p 0.022) | ×1.004 (1.042), p 0.44 |
| Lorenz-63 | 20 | ×0.944 (p 0.76) | ×1.085 (p 0.049) | ×1.012 (1.095), p 0.42 |
| Rössler | 10 | ×1.034 (p 0.19) | ×1.014 (p 0.27) | ×1.024 (1.062), p 0.14 |
| Rössler | 20 | ×1.127 (p 0.069) | ×1.050 (p 0.15) | ×1.088 (1.176), p 0.035 |
| Chua | 10 | ×1.010 (p 0.41) | ×0.996 (p 0.58) | ×1.003 (1.041), p 0.45 |
| Chua | 20 | ×1.079 (p 0.17) | ×0.976 (p 0.70) | ×1.026 (1.110), p 0.30 |
| **All 24** | 10 | ×1.002 (p 0.46) | ×1.019 (p 0.072) | **×1.011 (1.032), p 0.21** |
| **All 24** | 20 | ×1.047 (p 0.17) | ×1.036 (p 0.10) | **×1.041 (1.090), p 0.075** |

- **Lorenz-63 in R5** has its smallest p at b = 8 (0.010). R1 points the other way, though at n = 300 to 500 it has less power at large b.
- **Rössler at b = 20** is positive in both runs, and its combined p is 0.035. The mechanism is plausible: Rössler is phase-coherent, with an observable acf time of 1500 steps (50 LT) against a state spacing of 5 LT.
- **Multiplicity:** 16 primary contrasts (b ∈ {10, 20} × 4 groups × 2 runs) give a Bonferroni level of 0.003, and nothing beyond b = 5 reaches it.
- **Politis–White** chooses b = 1 for 47 of 48 series, because no significant autocorrelation is found. The exception is R5 Lorenz-63 H1a ρ = 1%, at b = 3.75. This is a mean-squared-error-optimal rule for the variance estimate, not a coverage-optimal one. It does not ask for longer blocks anywhere.

### 2.4 The one series that stands out

**Lorenz-63 H1a ρ = 1%** has the largest acf(1) of the 24 primaries in both runs:

| Run | acf(1) | n | P(max of 24 ≥ obs), selection-adjusted null |
| --- | --- | --- | --- |
| R1 | +0.131 | 300 | 0.16 |
| R5 | +0.115 | 1000 | 0.018 |

In R5 this is the one primary above the D1 threshold (0.11). Its R5 acf lags 1 to 5 are +0.115, +0.082, +0.091, +0.002, +0.087, and V\*(b)/V\*(1) is 1.36 (b = 5), 1.62 (b = 10), 1.82 (b = 20), 1.89 (b = 30). Taken at face value this would make V\*(5) about 0.72 of the long-run variance, and the 95% interval would cover at about 0.90 (model "L63-H1a-like" in §3). R1 does not reproduce the growth past b = 5 (1.15 at b = 5, then 1.0 to 1.13).

**Reading:**
- The positive lag-1 dependence of this series is fairly well supported: it ranks top in both runs, and its selection-adjusted p is 0.018 in R5.
- That the dependence extends beyond 5 states rests on R5 alone (V\*(20)/V\*(5) = 1.339, selection-adjusted p 0.072).

Lorenz-63 H2b(ii) shows the same pattern more weakly: V\*(5)/V\*(1) is 1.29 (R1) and 1.23 (R5), and only R5 keeps rising (1.44 at b = 20).

### 2.5 Would any verdict change? (`verdict_sensitivity.py`)

Each primary part's interval of R1 and R5 is widened on each side about its point estimate by f = √max(1, V\*(b)/V\*(5)) of its own ψ, at three settings: b = 10, b = 20, and the most pessimistic "plateau" (the maximum over b = 8 to 30). The verdict rules are those of v3 §2.

- **R5 (full size, the confirmatory configuration):** 0 changes in 72 (24 parts × 3 widenings). The largest factors are L63 H1a 1% (1.09 / 1.16 / 1.18) and L63 H2b(ii) (1.04 / 1.08 / 1.15); both stay "pass" with clear margin. For example, the L63 H2b(ii) lower bound goes from 0.0506 to 0.047 at the plateau factor, against the bound 0.
- **R1 (pilot):** one part changes at all three widenings: Rössler H1a ρ = 2%, from pass to inconclusive. Its lower bound is 0.7594 against the band edge 0.75 (point 0.9818), so any widening above 4.2% moves it. Its factor at b = 10 is 1.067, from V\*(10)/V\*(5) = 1.139, a ratio that is 1.5 SD of the n = 300 null above its mean. This is a margin case under a noisy ratio, not a dependence finding: Rössler shows no short-range excess (§2.2).

### 2.6 A physical point the data cannot settle

The state spacing is max(⌈5·acf time⌉, Theiler), measured on the observable:

| System | Spacing | Block 5 covers |
| --- | --- | --- |
| Lorenz-63 | 45 steps = 1.5 LT | 7.5 LT |
| Rössler | 150 steps = 5 LT | 25 LT |
| Chua | 150 steps = 5 LT | 25 LT |

Methods v2 states this range ("about 7–25 LT"), so it is by design. However, the influence quantities depend on local predictability along the orbit, through w\*, the seed errors and the horizons. On Lorenz-63 that predictability is plausibly organised on lobe-residence timescales, longer than the observable's 0.3-LT acf time. Two observations fit this: Lorenz-63 is where §2.2 finds the dependence, and the maximal horizon (8 LT) exceeds the Lorenz-63 block (7.5 LT).

This is an a-priori argument for a longer Lorenz-63 block. It is not established by the data: §2.3 does not show it beyond one realization.

### 2.7 What no block length can fix

A slow, weak component, such as a phase-coherent envelope, can hide a large long-run variance behind a small V\*(20)/V\*(5). The model "slow-weak" of §3 has acf(1) ≈ 0.01, invisible to D1, and V\*(20)/V\*(5) ≈ 1.10, close to the Rössler point estimate. Yet V\*(5) captures only 0.75 of the long-run variance, and moving to b = 20 recovers less than 1 percentage point of coverage at n = 1000.

**The rehearsal data do not show this model holds:** Rössler's combined p is 0.035, nominal, and does not survive multiplicity. They also cannot exclude it at n ≤ 1000. It is a limitation of any block length at these sample sizes, not an argument for a particular L. It belongs in the stated limitations (v3 §8), as a dependence assumption.

## 3. Cost and benefit of candidate block lengths (`coverage_by_block.py`)

### 3.1 Set-up

- **Model:** the first-order interval mean(ψ) ± z√(V\*(b)/n), on Gaussian series with the exact true variance of the mean. R = 20 000 per cell, paired across b on the same draws.
- **Monte Carlo SE of a coverage:** 0.0015 near 0.95 and 0.0009 near 0.983. Differences between values of b are paired, so their SE is smaller.
- **Assumptions:**
  - first-order linearisation (M4.1);
  - Gaussian tails (heavier tails raise the SD of V\*);
  - normal intervals rather than the production percentile intervals.
- **Cross-check against existing numbers:**
  - iid, n = 500, b = 5 gives 0.9451 / 0.9797, against the WU-0006 φ = 0 rows (e.g. 0.9443 / 0.9794);
  - AR(1) φ = 0.3 gives E V\*(5)/V = 0.859, against β₅ = 0.8685 (M4.2).
- **Dependence models:**
  - iid;
  - AR(1) with φ = 0.1;
  - AR(1) with φ = 0.3, the stress case already in the budget;
  - "L63-H1a-like": 0.875 iid plus 0.125 of an AR(1) with φ = 0.8, matched to §2.4;
  - "slow-weak": 0.99 iid plus 0.01 of an AR(1) with φ = 0.95, matched to the Rössler b = 20 point estimate.

### 3.2 Coverage at the confirmatory size n = 1000

Entries are 95% / 98.3% coverage; the last column is the change in percentage points from b = 5 to b = 10.

| Model | b = 5 | b = 10 | b = 20 | Change, b 5 → 10 |
| --- | --- | --- | --- | --- |
| iid | 0.9494 / 0.9833 | 0.9478 / 0.9825 | 0.9451 / 0.9802 | −0.16 / −0.08 |
| AR(1) 0.1 | 0.9443 / 0.9799 | 0.9452 / 0.9799 | 0.9427 / 0.9787 | +0.09 / 0.00 |
| AR(1) 0.3 (stress) | 0.9286 / 0.9722 | 0.9359 / 0.9763 | 0.9373 / 0.9759 | +0.73 / +0.41 |
| L63-H1a-like | 0.8828 / 0.9466 | 0.9095 / 0.9607 | 0.9244 / 0.9697 | +2.67 / +1.41 |
| slow-weak | 0.9109 / 0.9617 | 0.9148 / 0.9636 | 0.9193 / 0.9646 | +0.39 / +0.19 |

### 3.3 Half-width at n = 1000

| | b = 5 | b = 10 | b = 20 |
| --- | --- | --- | --- |
| Mean half-width / true, iid | 0.997 | 0.994 | 0.987 |
| SD of V\*/V, iid | 0.082 | 0.115 | 0.163 |

Longer blocks make the half-width slightly narrower on average under no dependence, from the O(b/n) centring bias, and noisier. The relative SD of the half-width rises from about 4% to about 6% (b = 10) and 8% (b = 20).

### 3.4 At the pilot size n = 300

Under iid, b = 10 costs −0.52 / −0.39 percentage points and b = 20 costs −1.5 / −1.0 points. This matters only for development runs, not for the sealed full-size run.

### 3.5 Reading

At n = 1000, L = 10 is never worse than L = 5 by more than about 0.2 percentage points in these models, and it is better by 0.4 to 2.7 points under dependence. Statistically it is nearly free at the confirmatory size.

L = 20 costs 0.3 to 0.4 points under iid and gains more only under the strong-memory model.

Neither L restores nominal coverage under "L63-H1a-like" or "slow-weak". Block length is not the lever for those cases.

## 4. Recommendation (a draft for the owner)

### 4.1 Keep L = 5 (the governing block length for all three systems)

**Reasons:**

1. D2's firing is at its no-dependence rate (§1). The calibrated readings fired nowhere.
2. The measured dependence is short-range and inside 5 states on the pooled evidence (§2.2, §2.3). The pooled residual beyond 5 has a 95% upper bound of 3.2% in variance at b = 10 and 9.0% at b = 20, which is 1.6% and 4.4% in half-width. Both are below the φ = 0.3 stress row already in the budget: β₅ = 0.8685, or 15% in variance and 7.3% in half-width.
3. No R5 verdict changes under the most pessimistic widening (§2.5).
4. The evidence for a change is one realization at nominal p 0.01 to 0.05.

**Cost:** none. No pre-registered number changes, and v3 §7 and Methods v2 "Intervals" stay as written.

### 4.2 Two additions, both at least as strict (owner's choice)

- **(a) OF-3 ruling (recommended).**
  - The pooled per-system permutation reading of B1 7.D2 governs "block length 5 is a design question". This is mean log V\*(10)/V\*(5) against the 0.99 quantile of 1000 permutations: about 1% false-alarm per system and about 3% per run. It keeps the cross-series dependence and the tails.
  - The A5 rule stays computed and reported, with its predicted rates, as information. It cannot inform the decision (§1.2).
  - β̂₅ stays reported. It misses the non-geometric pattern of the one series that matters (§2.4: its premise fails there).
  - **Readings under this rule:** R1 and R5 both read "no design question". This changes no threshold and no pre-registered number; it selects one of the three readings, as OF-3 asks.
- **(b) "Block-sensitive" qualifier (optional, report-only).**
  - **What it adds:** for each primary part, the first-order widening f₁₀ = √max(1, V\*(10)/V\*(5)) of its own ψ is printed beside the half-width. A verdict that the widened interval would change is labelled "block-sensitive". The governing verdict stays the block-5 one.
  - **Direction:** strictly more information. Nothing is loosened.
  - **Status on DEV:** on R5 it would label nothing; on R1 it would label Rössler H1a ρ = 2% (§2.5).
  - **Cost:** the computation exists in `tools/rehearsal_diagnostics.py`, which already computes V\*(10)/V\*(5). It needs the states dump in the confirmatory run, or the same few lines in the pipeline (a developer unit).
  - **Records:** an entry in the Methods v2 amendment log and the decision log. No change to v3 §7, because the governing rule is unchanged.

### 4.3 The alternative if the a-priori argument of §2.6 is preferred: L = 10 for Lorenz-63 only

This gives a 15-LT block, against 25 LT for Rössler and Chua.

**Statistical effect at n = 1000:**
- iid: −0.16 / −0.08 percentage points of coverage, and −0.3% mean half-width;
- dependence: +0.4 to +2.7 points;
- the R5 Lorenz-63 half-widths would widen by factors of 1.00 to 1.09 at most (§2.5), with no verdict change on DEV-2.

**Not recommended**, because the administrative cost after results exist is large. Each of the following would change (all are the owner's):

1. **v3 §7** "blocks of 5 states" becomes per-system: a v3 amendment, in the Claude Doc and re-exported.
2. **Methods v2 "Intervals"** ("blocks of 5 states, about 7–25 LT"): an amendment-log and code-change-list entry.
3. **`lpcstudy/config.py`** `bootstrap_block: int = 5` is global. A per-system value touches every caller (`budget.py`, `clip_sensitivity.py` and the statistics call sites) and needs tests: a developer unit.
4. **WU-0006 coverage table rows C1–C9** were computed at 2000 × 5. The harness asserts block 5 (`tests/slow/wu0006_harness.py:203`, `tests/slow/test_wu0006_harness.py:118`). The Lorenz-63 rows must be recomputed at b = 10 (slow tier).
5. **The stress constant** `BETA_STRESS` = 0.8685 = β₅(0.3) becomes β₁₀(0.3) ≈ 0.935 for Lorenz-63. The D1 coverage interpolation and the uq-budget "block 5" row change with it.
6. **D2 itself:** the A5 ratios, `UNION_NULL` / `UNION_STRESS`, the F3 predicted rates (0.993 / 0.906) and the permutation statistic are all defined against b = 5.
7. **The V4 gate** (median half-width ≤ 0.05 at M = 200), the DEF-0026 / OF-6 predicted V4 failure rates, and the D5/D6 SE, which use "the production block bootstrap, blocks of 5".
8. **Pre-registered predictions and projections** that use block-5 half-widths: H2e narrow side 0.04, the H2a(ii) margin band 0.0850–0.0933, H2b(ii) "at the lower edge", and the C7 projections of `rehearsal_report.py` (which reads `bootstrap_block`).
9. **Rehearsal validity.** R1 to R6 all ran at b = 5, so the rehearsal would no longer rehearse the confirmatory configuration. At least one new full-size DEV run with the dump would be needed before the seal.

Changing L globally to 10 adds Rössler and Chua to items 4 to 8, with no evidence asking for it. Its cost at the pilot size is also larger (§3.4).

**Timing:** whichever option is chosen must be fixed before the seal. Under PRIME.2, no block length may be changed after confirmatory results exist.

## 5. Uncertainty budget: the dependence row

This applies to every primary interval. Levels are 1 − 0.05/3 (H2a, H2b, H3c) and 95% (H1a). Dependence is handled by the moving-block bootstrap with blocks of 5, 2000 resamples.

| Source | Type | How estimated | Size | Included in the reported interval? |
| --- | --- | --- | --- | --- |
| Short-range serial dependence of ψ (lags ≤ 4 states) | aleatory | MBB, block 5 | Lorenz-63: V\*(5)/V\*(1) excess ×1.077; all 24: ×1.036 | yes (this is what the block absorbs) |
| Residual dependence beyond 5 states (pooled) | estimator / epistemic | exact V\*(b)/V\*(5) against the permutation null, R1 + R5 | variance ×1.011 (upper 1.032) at b = 10; ×1.041 (upper 1.090) at b = 20; half-width ≤ +1.6% / +4.4% | no; it lies within the φ = 0.3 stress row (half-width +7.3%), which is reported |
| Residual dependence beyond 5 states (worst single series) | estimator / epistemic | same, per series | R5 L63 H1a ρ = 1%: half-width ×1.09 (b = 10), ×1.18 (plateau); the plateau exceeds the stress row; one realization, selection-adjusted p 0.072 | no; flagged here, and by the §4.2(b) qualifier if adopted |
| Slow weak dependence (phase-coherent envelope) | epistemic | not estimable at n ≤ 1000 (§2.7) | not estimated | no; stated as a limitation |

**Seeds:**
- R1: DEV-1 (pilot, GPU context).
- R5: DEV-2 (full, GPU context).
- Permutations and simulations: scratch seed 20261017, via `make_rng(20261017, "block-length-note", …)`. These are not the diagnostic record: the pre-registered diagnostic defaults (seed 20261018, 1000 permutations; §26 OQ-R9) govern the recorded D2 readings, which are quoted unchanged in §1.3.

## 6. Evidence quality

**Solid (calibration, or exact):**
- The A5 rule's null law and its at-least-one rates. M4.2, and confirmed here by a permutation null on the real series: 0.988 / 0.897 against 0.993 / 0.906.
- The observed A5 counts are at or within null expectation (P(≥4) = 0.60 and 0.19).
- V\*(b) is exact: no bootstrap noise.
- The extracted series reproduce the recorded ratios.
- The coverage and half-width costs of §3 are Monte Carlo with stated SE, and are cross-checked against WU-0006 and β₅.

**Moderately supported:**
- Short-range positive dependence in Lorenz-63 influence series: both runs, combined p 0.003.
- Lorenz-63 H1a ρ = 1% has positive lag-1 dependence: the top series in both runs, selection-adjusted p 0.018 in R5.

**One realization, nominal only:**
- Dependence beyond 5 states: Lorenz-63 in R5 (p 0.010 to 0.022, contradicted in direction by R1), and Rössler at b = 20 (p 0.035 combined).
- The size of the L63 H1a long-run variance (V\*(5) ≈ 0.72 of it).
- None of these survives multiplicity.
- R6 and R3 have no dump, so there is no third realization.

**Not settled by any rehearsal at n ≤ 1000:** slow weak dependence (§2.7).

## 7. Reproduction

The scripts are in `docs/agent/notes/2026-10-17-math-block-length-scripts/`, with their outputs (`*.out`). Run them with the project venv, `-I`, `JAX_PLATFORMS=cpu`, threads 4, niced. `S` is a scratch folder and `RUNS` is `lpcstudy-wt/run/r1-c9bb981/runs`. Each script finished in under 10 s on CPU.

1. `extract_series.py WT RUNS/r1-gpu-dev1/pilot RUNS/r5-gpu-dev2/full S` writes `series-R1.npz` and `series-R5.npz` (regenerable, not committed).
2. `block_curve.py WT S` gives §2.2, §2.3 and §1.3.
3. `max_series_null.py WT S` gives §2.4.
4. `verdict_sensitivity.py S RUNS/r1-gpu-dev1/pilot RUNS/r5-gpu-dev2/full` gives §2.5.
5. `coverage_by_block.py WT` gives §3.

Here `WT` is a checkout with `tools/` and `lpcstudy/` at develop a144f6d or later. The scripts import `tools/rehearsal_diagnostics.py` read-only and `lpcstudy.data.make_rng`. They are not imported by anything else and are not tests.
