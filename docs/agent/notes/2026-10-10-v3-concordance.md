# v3 concordance (WU-0014.2)

- **Date / author:** 2026-10-10, planner agent (claude-opus-5-5). Branch `wu/0014-2-concordance`.
- **Status:** working note (no instruction authority, PRIME.11). It produces no numbers and is not a hypothesis test.
- **Inputs:**
  - `docs/study/proposal_and_methods_v3.md`, SHA-256 `6fb99e8eeaac437ba1e561e01bd88f26fc86f836173460c7f2a0f8899fabad2b` (checked with `sha256sum` today);
  - `docs/study/methods_experimental_procedures_v2.md` ("M2");
  - `docs/study/decision_log_lpc.md` ("DL"): the v2-to-v3 map and the v1-to-v3 correction;
  - `ROADMAP.md` WU-0002.1 to .13;
  - the code on `main` (v1): `lpcstudy/analysis.py` ("an."), `experiments.py` ("ex."), plus `pipeline.py`, `allocation.py`, `validation.py`, `report.py` and `config.py`.
- **Identifier note.** The code keys are v1 identifiers (DL correction). For every identifier that exists in both v1 and v2, the v1 and v2 ids are the same. The only differences are:
  - v1 H1a, which became V7;
  - v1 H1f, which became Q-N;
  - v1 H3b, which v2 dropped;
  - T1.

  So the ROADMAP's "v2 Hxx" labels name the current code keys.

## 1. Concordance

### 1a. Hypotheses (14 rows)

"Function today" names the current function. "To add" means no function computes the v3 statistic yet.

| # | v3 id (role) | v2 id (= code key) | M2 section | Criterion as v3 states it (§2 unless noted) | Function today / WU |
| --- | --- | --- | --- | --- | --- |
| 1 | H1a (sec.) | H1b | §M11 row H1b; §M10 E2 | "Fit of the median ε_s² to b² N_lib^(−2/d) + f²"; pass if the "interval of 1/d within ±25% of the independently estimated 1/d" | `an.h1b_library_scaling` (mean fit). Median: WU-0002.4. Verdict from the interval: WU-0002.9. See D-19 |
| 2 | H1b (sec.) | H1c | §M11 row H1c; §M10 E3 | "Slope of log r.m.s. PLP error on log(g_H δ/√m) at H_ref", in [0.8, 1.2]; PLP only (v3 §8) | `an.h1c_seed_amplifier`. PLP-only pass: WU-0002.4 |
| 3 | H1c (sec.) | H1d | §M11 row H1d; §M10 E3 | "Median of Λ̄ × dT/d ln θ (PLP)", in [0.8, 1.25] | `an.h1d_horizon_law`. Verdict from the interval: WU-0002.9 |
| 4 | H1d (sec.) | H1e | §M11 row H1e; §M10 E3 | Spearman correlation of the deployable recurrence, observability and instability estimates with their exact values, each ≥ 0.7; N̂ "reported, not tested" (v3 §8) | `an.h1e_proxies`. Intervals and N̂ out of the pass: WU-0002.5 |
| 5 | Q-N (estimate) | Q-N (code H1f) | §M11 row Q-N and reading table; §M10 E3 | "Out-of-sample gain in R² (ΔR²) for predicting logit w\*, with exact (oracle) values", "read by the table in §7". v3 §7: oracle ΔR² for logit w\* at 1 LT; the deployable version is secondary | `an.h1f_noise_redundancy`. To rework in WU-0002.6 |
| 6 | **H2a** (primary) | H2a | §M11 row H2a; §M10 E4 | "(i) median range of w\* over 1, 2, 4 LT in the small-error regime; (ii) partial correlation of logit w\* with Λ̃ given both seeds": "(i) interval below 0.1 and (ii) interval inside (−0.1, 0.1)" | `an.h2a_separation`. Three-valued verdict: WU-0002.9 |
| 7 | **H2b** (primary) | H2b | §M11 row H2b; §M10 E1, E2 | "(i) mean per-state rank correlation of w\* with ρ; (ii) mean paired change in w\* from N_lib = 10³ to 10⁴ at ρ = 1%": "both lower bounds > 0" | `an.h2b_knob_response`: (i) is computed. (ii) is to add in WU-0002.7 |
| 8 | H2c (sec.) | H2c | §M11 row H2c; §M10 E4 | "Paired MSE differences at H_ref" of the closed form against a global weight and against the better single forecaster: "both upper bounds < 0" | `an.h2c_state_dependence`. See D-20 (A4o − A2) |
| 9 | H2d (sec.) | H2d | §M11 row H2d; §M14 | "MSE ratio minus 1 at H_ref" (closed form against the learned allocator): "upper bound ≤ 0.10" | `an.h2d_empirical_comparison`. Remove part (ii): WU-0002.8 |
| 10 | H2e (sec.) | H2f | §M11 row H2f; §M10 E2 | "Median per-state change in error correlation, N_lib 10³ → 10⁵": "lower bound > 0 at ρ = 1% and 2%" | None. To add in WU-0002.7 |
| 11 | gain bound (reported) | H2e | §M11 row H2e; §M9 P1(d) | "The hybrid's horizon gain over the better forecaster is reported against the P1 bound, without a pass/fail bar" (v3 §2, after the RQ3 table) | `an.h2e_horizon_bound` (still has a 0.9 pass bar). See D-21 |
| 12 | H3a (sec.) | H3a | §M11 row H3a; §M10 E6 | "Holm-adjusted log-rank tests between consecutive regimes": "all p < 0.01" | `an.h3_regimes` key `H3a` (still has the regret and IQR bars). WU-0002.8 |
| 13 | H3b (sec.) | H3c | §M11 row H3c; §M10 E6 | "Importances in a weight tree and a horizon tree": "weight tree: Λ̃ < 0.2; horizon tree: Λ̃ highest" | `an.h3_regimes` key `H3c`. Rename: WU-0002.2. Verdict: see D-24 |
| 14 | **H3c** (primary) | H3d | §M11 row H3d; §M10 E6 | "MSE ratio, regimes / closed form, at H_ref": "upper bound ≤ 1.05" | `an.h3_regimes` key `H3d` (point estimate only). Interval at 1 − 0.05/3: WU-0002.8 |

**Code identifiers with no v3 row:**

| Code id | What happens to it | Code today | WU |
| --- | --- | --- | --- |
| v1 H1a | becomes V7 | `an.h1a_noise_scaling` | WU-0002.10 |
| v1 H3b | dropped | `an.h3_regimes` key `H3b` | WU-0002.8 |
| T1 | dropped | `ex.run_transfer`, `report.verdicts` | WU-0002.1 |

### 1b. Experiments (7 rows plus the dropped shift experiment)

| v3 | v2 | M2 | Design as v3 §6 states it | Function today / WU |
| --- | --- | --- | --- | --- |
| E0 | E0 | §M10 E0 | Checks V1–V7; "a failure marks that system's results provisional" | `ex.run_system` (validation block) and `ex.convergence_check` (V4). The checks are in `validation.py`: `check_jacobians`, `check_cramer_rao`, `check_cp_horizon`, `check_kaplan_meier`, `check_integrator`, `gate_status`. V7 is to add in WU-0002.10; `an.h1a_noise_scaling` computes its inputs today |
| E1 | E1 | §M10 E1 | ρ ∈ {0.5, 1, 2, 5}% at N_lib = 10⁴; ψ retrained at each ρ; feeds V7 and H2b(i) | `ex.run_system` (the `noise_cells` loop). It still feeds `shift_scores`, which WU-0002.1 removes |
| E2 | E2 | §M10 E2 | N_lib ∈ {10³, 10^3.5, 10⁴, 10^4.5, 10⁵} at ρ ∈ {1, 2}%, nested libraries; feeds H1a, H2b(ii) and H2e | `ex.run_system` (the `library_cells` loop). The `n_lib` relabel is WU-0002.2. The 1000 sweep states are WU-0002.10 |
| E3 | E3 | §M10 E3 | Core cell ρ = 1%, N_lib = 10⁴, horizons 1–240: seed × amplifier fit, horizons over θ, proxy fidelity, Q-N; feeds H1b–H1d and Q-N | `ex.run_system`; `an.h1c_seed_amplifier`, `an.h1d_horizon_law`, `an.h1e_proxies`, `an.h1f_noise_redundancy` |
| E4 | E4 | §M10 E4 | All rules on the core test split; MSE at 0.25, 0.5, 1, 2, 4 LT; w\*(H) per state; horizon gain; feeds H2a, H2c, H2d | `ex.run_system`; `an.summarize_scores`, `an.weight_profiles`, `an.h2a_separation`, `an.h2c_state_dependence`, `an.h2d_empirical_comparison`, `an.h2e_horizon_bound`. Exact excess MSE is WU-0002.3 |
| E5 | **E6** | §M10 E6 | A5 for K ∈ {2, 3, 4, 5, 6, 8, 12, 16}; excess error against K; log-rank tests; tree importances; feeds H3a–H3c | `an.h3_regimes`, with the regime fits in `pipeline.fit_rules`. WU-0002.3 and WU-0002.8 |
| E6 | **E7** | §M10 E7 | Lorenz-63 and Rössler, reported only: D ∈ {5, 10}; 5 averaged analogs; model parameters ±5% and ±10%; finite-amplitude growth in place of Λ̄ | `ex.run_robustness`, `ex._variant_summary`, `ex._perturbation_scale_variant`. The τ_d/2 variant is removed in WU-0002.1. See D-17 |
| **dropped in v3** | E5 (shift) | §M10 E5 | Not in v3. DL (10 Oct, later): "E5 (shift) is dropped from v3" | `ex.run_system` (`shift_scores`) and `an.shift_gaps`. Removed in WU-0002.1 |

### 1c. Allocation rules (A0–A5, A4o, A\*; unchanged between v2 and v3)

The ids are the same in v2 and v3. The definitions are in M2 §M7 and v3 §5. No rule is computed in `analysis.py` or `experiments.py`. They are built in `pipeline.rule_weights` and fitted in `pipeline.fit_rules`.

| Rule | v3 §5 definition | Code today | WU |
| --- | --- | --- | --- |
| A0 | CP alone, w = 1 | `pipeline.rule_weights` | — |
| A1 | PLP alone, w = 0 | `pipeline.rule_weights` | — |
| A2 | One global weight per horizon, fitted on construction | `allocation.global_weight` (pooled clip(Σ(E_P − C)/Σc), which is P3(a) on all states) | — |
| A3 | Learned allocator: w = ê²_PLP/(ê²_CP + ê²_PLP), from X_t | `allocation.ErrorPredictor` | — |
| A4 | w = δ̂²/(ε̂² + δ̂²); inputs R, ν̂, ρ | `allocation.closed_form_weight`, `ProfileProxies` | — |
| A5 | Tree on F̂ with K leaves; the P3 regime weight; a KM horizon. "K is the smallest value in {2, 3, 4, 5, 6, 8} whose calibration error is within 5% of the best value in that set" | `allocation.fit_regime_tree`, `allocation.calibrate_regimes`, `pipeline._choose_regimes` | WU-0002.3 |
| A4o | A4 with exact seeds | `pipeline.rule_weights` | — |
| A\* | State-optimal w\* | `oracle.oracle_weight` | — |
| (A4f) | not in v3 (M2 §M14) | `allocation.full_form_weight` | removed in WU-0002.1 |

## 2. Discrepancies and dispositions (WU-0014.3)

Kinds:

- **code:** the code differs from v3, and a ROADMAP row covers it.
- **gap:** the code differs from v3, and no ROADMAP row names it. A home is proposed.
- **ref:** a document disagrees with another document (v3, M2, DL or ROADMAP). It is referred to the owner (§3) and not resolved here.

| # | Discrepancy (evidence) | Kind | Disposition |
| --- | --- | --- | --- |
| D-01 | v3 H1a fits the median ε_s². `h1b_library_scaling` fits `sq[idx].mean(axis=0)` | code | WU-0002.4 |
| D-02 | v3 H1b is PLP only (v3 §8). `h1c_seed_amplifier` sets `pass = CP and PLP` | code | WU-0002.4 |
| D-03 | v3 H1d tests three correlations with intervals. `h1e_proxies` includes `noise_sensitivity` (N̂) in `pass` and has no interval | code | WU-0002.5 |
| D-04 | v3 Q-N reads the oracle ΔR² for logit w\* by the v3 §7 table (0.05 bounds). `h1f_noise_redundancy` instead (a) treats the deployable profile as primary, (b) uses a margin of 0.01, (c) reads both targets jointly, and (d) sets `pass` = "redundant". The WU-0002.6 row does not say that the reading uses logit w\* only (v3 §7); the log horizon is then reported | code | WU-0002.6. The unit plan must state the target |
| D-05 | v3 H2b(ii) is the mean paired change 10³ → 10⁴ at ρ = 1%. The code takes a per-state Spearman over all five N_lib at each ρ and adds "median w\*(N_max) < 0.95" (dropped in M2 §M14) | code | WU-0002.7 |
| D-06 | v3 H2e (noise matching) has no code | code | WU-0002.7 |
| D-07 | v3 H2d has one part. The code has `shift_pass` (≥ 4 of 5 shift wins) in `pass` | code | WU-0002.8, with the shift path removed in WU-0002.1 |
| D-08 | v3 H3a is log-rank only. The code's `pass` also requires `regret_ratio ≤ 0.05` and `mean_iqr ≤ 0.5` | code | WU-0002.8 |
| D-09 | v1 H3b (p_eff) is still computed and verdicted | code | WU-0002.8 |
| D-10 | v3 H3c is decided by an interval at 1 − 0.05/3 (v3 §7). The code computes a point ratio with `pass = ratio ≤ 1.05` | code | WU-0002.8 |
| D-11 | v3 §5 requires exact excess V(w) − V(w\*). `allocation.regime_regret`, `RuleScores.regret` and `ex._variant_summary` (`A5_regret_ratio`) use c(w − w\*)² with clipped w\* (DEF-0002) | code | WU-0002.3. The E6 summary must use the same function |
| D-12 | P3 regime weight: `calibrate_regimes` averages clipped w\* (DEF-0003) | code | WU-0002.3 |
| D-13 | K rule (v3 §5). `_choose_regimes` takes the first K ≤ `regime_max_primary` (= 5) with a regret ratio ≤ 0.05 against best-single and falls back to 5 | code | WU-0002.3. `regime_max_primary` must cover 8 |
| D-14 | v3 §7 verdicts. `report.verdicts` aggregates point-estimate `pass` booleans into "partially supported" and has a T1 branch. Most `pass` flags compare a point estimate, not an interval (H1a, H1c, H1d, H2d, H3c) | code | WU-0002.9. The T1 branch goes in WU-0002.1 |
| D-15 | V7 is missing from `gate_status`. `FULL.n_test_sweep = 500`, but v3 §4 says 1000 | code | WU-0002.10 |
| D-16 | Identifiers: result keys, `report.HYPOTHESES` text and the robustness summary key `H1c` are v1. The `analysis.py` module docstring names the primaries as "H2a, H2b, H3a"; v3 says H2a, H2b, H3c | code | WU-0002.2 |
| D-17 | A4f, Lorenz-96, transfer and the τ_d/2 robustness variant (`ex.run_robustness` `"delay/2"`) are not in v3 | code | WU-0002.1 |
| D-18 | Silent fallbacks that feed verdicts:<br>• `h1d_horizon_law` returns `pass False` if fewer than 10 states qualify;<br>• `h2a_separation` replaces an empty range set with NaN;<br>• `h3_regimes` sets `logrank_ok = False` when there are no p-values | code | WU-0002.11 (count). The verdict mapping goes to WU-0002.9, subject to D-24 |
| D-19 | `h1b_library_scaling` adds a pass condition, "floor increasing in ρ". Neither v3 §2 nor M2 §M11 has it; M2 says "floor f reported". WU-0002.4 names only the median | gap | Propose WU-0002.4: remove the condition from `pass` and keep the floor as reported |
| D-20 | The M2 §M11 H2c row says "A4o − A2 reported", and the v3 §7 failure reading uses "H2c fails but A4o beats A2". `h2c_state_dependence` does not compute A4o − A2 with an interval. No ROADMAP row covers this | gap | Propose WU-0002.8 |
| D-21 | Gain bound:<br>(a) `h2e_horizon_bound` keeps `threshold 0.9` and `pass`, but v3 says there is no bar;<br>(b) its C ≥ 0 screen uses the centered covariance `cross − mean_cp·mean_plp` at a single horizon, while P1(c) and (d) need the raw C = E[e_C e_P] ≥ 0 at every horizon;<br>(c) the M2 §M11 subset "satisfying P1's hypotheses at every horizon" is not computed.<br>No ROADMAP row covers this | gap | Propose WU-0002.8, with (a) also in WU-0002.9 (role "reported") |
| D-22 | **Boundary convention.** WU-0002.9 says "Methods v2 §M11 does not state whether an endpoint equal to the bound counts as inside" and proposes closed comparison for all criteria. v3 §2 states the operator for each criterion:<br>• strict: H2a(i) "below 0.1", H2a(ii) "inside (−0.1, 0.1)", H2b, H2e "> 0", H2c "< 0", H3a "p < 0.01";<br>• closed: H1b [0.8, 1.2], H1c [0.8, 1.25], H1d "≥ 0.7", H2d "≤ 0.10", H3c "≤ 1.05".<br>A uniform closed rule would change the primary H2a and H2b. v3 is silent only on the fail side and on the "within 5%" of the K rule (WU-0002.3 treats a tie as inside) | ref | Referral item 1 |
| D-23 | The WU-0002.8 acceptance says "no `H3b` key exists anywhere in results". v3 has an H3b (tree importances, = v2 H3c), which WU-0002.2 must create. As written, this criterion cannot pass on a v3-conformant implementation | ref | Referral item 2 |
| D-24 | v3 §7 says "Every criterion in §2 is decided by an interval". However, H3a is a p-value rule ("all p < 0.01") and H3b is an importance comparison with no interval (v3 §2; M2 §M11 likewise). No document says how pass, fail and inconclusive apply to these two, or to a statistic that cannot be computed (D-18) | ref | Referral item 3. Blocks the H3a and H3b parts of WU-0002.9 |
| D-25 | Code definitions that change tested statistics but appear in no document:<br>(a) logit w\* uses w\* clipped to [0.01, 0.99] (`h2a_separation`, `h1f_noise_redundancy`). This affects primary H2a(ii) and Q-N, and 22–36% of states have w\* = 0 (v3 §8);<br>(b) the H2a(i) small-error regime is applied per (state, horizon); a state needs ≥ 2 small-error horizons, and the range is taken over those only;<br>(c) the Q-N regressor sets `l2_regularization=1.0`, beyond the M2 §M10 E3 hyperparameters;<br>(d) the A5 tree is a two-output CART on standardized (w\*(H_ref), log T), with `min_samples_leaf = max(10, nE/50)`;<br>(e) the H3b trees use `max_leaf_nodes = max(K, 4)`;<br>(f) the H3a log-rank tests use the A5 realized horizons of the first evaluation draw;<br>(g) the E6 ±5%/±10% perturbation is one random sign per parameter (`pipeline.Study.setup`) | ref | Referral item 4 |
| D-26 | Points where v3 is silent and M2 is specific:<br>• H1a "at both ρ". The M2 §M11 multi-part list (H1e, H2a, H2b, H2c, H2f, H3c) omits H1b, although it has two ρ parts;<br>• V7 "at every ρ" (M2 §M10);<br>• Q-N's two targets (M2 §M10 E3) against v3 §7's logit w\* reading;<br>• "at H_ref" for H2b and H2e;<br>• state spacing: v3 §4 says "at least 1 LT apart"; M2 §M3 says 5·min(τ_ac, 1 LT) | ref | Referral item 5 (confirm that M2 detail governs) |
| D-27 | The WU-0002.1 row says "v3 drops E5 (shift)". In v3, E5 is Regimes; the shift experiment is v2 E5 | ref | Referral item 2 (wording only) |
| — | M2 §M10 E5 and §M14 report the shift experiment, while v3 drops it | resolved | DL (10 Oct, later) states the drop. No action |

**Counts:**

| Kind | Number | Items |
| --- | --- | --- |
| code | 18 | D-01 to D-18, all mapped to WU-0002.1 to .11 |
| gap | 3 | D-19 to D-21, proposed for WU-0002.4 and .8 |
| ref | 6 | D-22 to D-27, in five referral items |
| resolved | 1 | the shift experiment |

## 3. Referral (LPC.AI.13 form)

The main session should copy this into the WU-0014 unit file under `## Referral`. This agent edits only this note.

```
## Referral: five document discrepancies the v3 concordance found (agents do not change criteria)
Unit: WU-0014 (.2 -> .3)   Raised by: claude-opus-5-5   Date: 2026-10-10
What I was doing:  Building the v3 concordance (docs/agent/notes/2026-10-10-v3-concordance.md).
What stopped me:   .claude/rules/study-docs.md and LPC.AI.12: criteria, decision rules and
                   fixed acceptance criteria (VV.3) are the owner's to change.
Findings:          1. Boundary convention (D-22): ROADMAP WU-0002.9's premise and its
                      uniform "closed" proposal conflict with v3 §2's explicit per-criterion
                      operators (strict for H2a, H2b, H2c, H2e, H3a; closed for H1b-H1d,
                      H2d, H3c). Open: endpoint on the fail side; the K-rule "within 5%" tie.
                   2. ROADMAP text (D-23, D-27): WU-0002.8 acceptance "no H3b key exists
                      anywhere" contradicts v3 H3b; WU-0002.1 "v3 drops E5" should read
                      "v2 E5 (shift)".
                   3. Verdict for non-interval criteria (D-24): v3 §7 says every criterion
                      is decided by an interval; H3a (p-values) and H3b (importances) have
                      none, and no rule covers a statistic that cannot be computed.
                   4. Undocumented code definitions (D-25 a-g), of which (a) the logit clip
                      at [0.01, 0.99] and (b) the H2a(i) eligibility rule affect the primary
                      H2a.
                   5. v3 silent, M2 specific (D-26).
Options:           1. Owner rules each item in decisions.md (and amends ROADMAP rows
                      WU-0002.1/.8/.9 by dated amendment); WU-0002 plans cite the rulings.
                      Effect: WU-0002.8/.9 can be planned; cost: one owner session.
                   2. Amend v3/M2 text (a dated amendment) for items 1, 3, 4. Effect: the
                      documents state what the code computes; cost: a document revision
                      before the freeze.
                   3. Defer: plan WU-0002.1-.7 and .10-.11 now, hold the parts of .8/.9
                      that depend on items 1-3. Effect: no block on the rest; risk: rework.
Recommendation:    Option 1 now, with option 2 for item 4(a)-(b), because they define
                   a primary statistic. For item 1, follow v3 §2's operators as written
                   rather than one uniform convention. For item 2, change the WU-0002.8
                   check to "no key for v1 H3b (p_eff)". For item 5, confirm that the M2
                   detail governs where v3 is silent.
To verify the outcome: each D-22..D-27 cites a decisions.md entry or a dated ROADMAP or
                   document amendment; WU-0002.8/.9 plans reference them.
State left in:     branch wu/0014-2-concordance, this note uncommitted; no other file edited.
```
