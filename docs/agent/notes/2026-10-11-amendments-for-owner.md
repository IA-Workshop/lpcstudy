# Amendments the owner's rulings require (drafts for the owner to adopt)

Prepared 2026-10-11 by claude-sonnet-5-5 (main session). The owner approved every recommended ruling on 2026-10-11 (`DEC-0008` in `docs/agent/records/decisions.md`). Implementation proceeds against DEC-0008. The texts below are **drafts of edits to adopted or governing documents**. An agent may not make them (GOV.49, `.claude/rules/study-docs.md`): the owner edits, then records each change with a ledger `amendment` entry (and re-adopts the governed files whose hash changed). **Freeze prerequisite (WU-0004.1):** v3, Methods v2 and ROADMAP.md must state what the code tests; the checklist item is "each DEC-0008 definition appears in the documents".

Line numbers are those of `main`/`develop` on 2026-10-11.

## 1. ROADMAP.md (adopted)

| Row (line) | Change | Draft wording |
| --- | --- | --- |
| WU-0002.1 (line 85) | wording | "v3 drops E5 (shift)" becomes "v2 E5 (shift) is dropped in v3 (v3's E5 is Regimes)". |
| WU-0002.8 acceptance (line 116) | wording | "no `H3b` key exists anywhere in results" becomes "no result key for v1 H3b (`p_eff`) exists; the v3 `H3b` key holds the tree importances (renamed from v1 H3c in WU-0002.2)". |
| WU-0002.9 acceptance (line 117) | resolves the owner decision | Replace "**Owner decision needed before execution:** … closed comparison for all criteria" with "Boundary convention (DEC-0008 A1): pass iff the interval is inside the band, fail iff it misses the band entirely, otherwise inconclusive; each band as v3 §2 writes it (strict for H2a, H2b, H2c, H2e, H3a; closed for H1b to H1d, H2d, H3c; H1a closed); unrounded float64; a K-rule tie is inside. A statistic that cannot be computed, or a subset statistic with fewer than 50 states, is inconclusive with the reason recorded (DEC-0008 A3)." Enumerations stay; add the cases for 'not computable' and 'n < 50'. |
| WU-0002.10 acceptance (line 118) | strengthens | Add: "V7 also tests the median slope of ln δ on ln ρ in [0.9, 1.1] (v3 E0) and holds at every ρ (Methods v2 §M10); unit tests pass a synthetic slope inside and outside the band and a per-ρ failure." |
| WU-0002.3 | none | K rule reads calibration excess MSE (already the row's wording); ties inside. |
| WU-0002.4 acceptance (line 112) | H1a reference | Add: "H1a is judged on the ratio (1/d_fit)/(1/d_LB), where 1/d_LB is the mean over states of the per-state Levina-Bickel inverse estimates, by a joint block bootstrap over the same resampled states; pass iff the ratio's interval lies inside [0.75, 1.25], at both ρ; the 'floor increasing in ρ' pass condition is removed (concordance D-19)." |
| WU-0002.6 acceptance (line 114) | two-part Q-N | Replace "oracle ΔR² primary" with: "Q-N reports ΔR² for the interior logit w\* (0 < w\* < 1) and for the indicator 1{w\* = 0}, read by the v3 §7 table; the reading function and the boundary cases are tested for each." |
| WU-0002.7 / H2a(ii) | two-part H2a(ii) | Add to the WU-0002.6 or a new sub-task row (the planner assigns): "H2a(ii): partial correlations of 1{w\*(H_ref)=0} (all test states) and of logit w\*(H_ref) (0 < w\* < 1) with Λ̃, residualized on x, x², x₁x₂ of the two seed logs; pass iff both intervals lie inside (−0.1, 0.1); counts of w\*=0 and w\*=1 reported; third part for w\*=1 if it exceeds 5% of states." |
| WU-0002.8 | H3b, H3a, H2c | H3a: pass or inconclusive only (no margin set). H3b: block-bootstrap intervals over refitted trees with a fixed leaf count of 8 (weight-tree importance of Λ̃ in [0, 0.2); D = imp_t(Λ̃) − max other > 0) and the stability fraction reported. H2c: the better single forecaster is chosen on the calibration split (DEC-0008 A4(i)); A4o − A2 reported with an interval (concordance D-20). |
| WU-0002.11 | counters | Add the cases "`statistics.py:61`, `statistics.py:95-96`, `oracle.py:62`" (DEF-0001 status lines) and the audit of the other `default_rng` sites (DEF-0011). |
| New rows | DEF-0010, DEF-0012 | WU-0002.12a: fix DEF-0010 (option B: raw seed below 2³², `make_rng`-derived 32-bit value otherwise, pinned by a test; DEV-1 smoke runs). WU-0002.12b (or a small unit): DEF-0012, `workers = LPC_THREADS`. |

## 2. Proposal and methods v3 (governing design; the owner edits the Claude Doc and re-exports)

| v3 location | Change |
| --- | --- |
| line 79 (H1a) | State the reference and the band: "the ratio of the fitted 1/d to the independently estimated 1/d (the mean over states of the per-state Levina–Bickel inverse estimates), with its interval from a joint block bootstrap, lies inside [0.75, 1.25] (closed), at both ρ." |
| lines 83, 345 (Q-N) | "ΔR² for predicting logit w\* on the states where 0 < w\* < 1, and for the indicator of w\* = 0." |
| line 89 (H2a) | (i) "median range of w\* over the horizons {1, 2, 4} LT up to the last at which both r.m.s. errors are ≤ 0.5 σ_x (A6); states with fewer than two such horizons are excluded and counted; medians per span reported". (ii) "two parts: the partial correlation of the indicator 1{w\* = 0} with Λ̃ given both seeds (all states), and of logit w\* given both seeds (0 < w\* < 1), both seed controls residualized on x, x², x₁x₂; both intervals inside (−0.1, 0.1)". |
| lines 99–100 (H3a, H3b) | H3a: "all Holm-adjusted p < 0.01, otherwise inconclusive". H3b: "block-bootstrap intervals for the weight-tree importance of Λ̃ (below 0.2) and for the difference between Λ̃'s horizon-tree importance and the largest other (above 0), trees of 8 leaves". |
| line 239 (spacing) | "Evaluation states are max(5·min(τ_ac, 1 LT), 1 LT) apart." |
| line 289 (K rule) | "K is the smallest value in {2, 3, 4, 5, 6, 8} whose calibration excess MSE, V(w) − V(w\*), is within 5% of the minimum excess over that set." |
| §7 (line 322 and nearby) | Add the verdict geometry and the rule for statistics that cannot be computed (DEC-0008 A1, A3). |

## 3. Methods v2 (design record) and the decision log

Document before the freeze (DEC-0008 A4): Q-N `l2_regularization = 1.0` (M2 E3); the A5 tree's split criterion and `min_samples_leaf`; the E6 perturbation sign vector and its seed; the H3a first-draw rule. Record in the decision log that H1a's reference estimator and the H2a(ii) treatment of w\* = 0 changed from the pilot's.

## 4. DEVELOPMENT_WORKFLOW.md and `.claude/` (adopted)

| File (line) | Change |
| --- | --- |
| DEVELOPMENT_WORKFLOW §4.2 (line 91) | Add a rule: "A test file is also selected when a module it imports directly is changed." (DEC-0003 Q2; adds tests only). Add rows for the modules `seeds`, `provenance` and `identifiers` to the import-graph table. |
| DEVELOPMENT_WORKFLOW (lines 89, 138) | Replace the statements that the suite is 14 tests in `tests/test_core.py`. |
| ROADMAP.md (line 11) | Same for the `tests/test_core.py` statement. |
| `.claude/rules/test-discipline.md` (line 18), `.claude/skills/test-impact/SKILL.md` (line 27) | Remove "`tests/test_core.py` is the whole suite". |
| `.claude/skills/test-impact/SKILL.md` (line 13), `.claude/skills/independent-review/SKILL.md` (line 22) | Replace `2>/dev/null || echo "..."` with `2>&1 \|\| echo "..."` so a tool error is visible. |
| `.claude/settings.json` (lines 43, 47) and `.claude/hooks/test_gate.py` (lines 80–82) | Remove the old `flock … python -m lpcstudy --preset` forms once you accept `tools/run_preset.sh` as the only entry; decide whether GPU-tier test runs count toward the 60 GPU-hours. |
| `docs/agent/governance/project-constitution.md` (line 11, 185), `authorizations.md` (line 53) | Fill in the owner name and the operating-cost discipline. |

## 5. Ledger commands (the owner appends; replace the placeholders)

```
python3 tools/ledger.py append --type authorization --actor "<name>" --role "human owner" \
  --authority "LPC.AUTH.2" \
  --summary "Lift the 50-pages-per-unit cap on researcher retrievals; researcher may use the alphaXiv connectors for papers (owner approval 2026-10-11)"

python3 tools/ledger.py append --type note --actor "<name>" --role "human owner" --authority "GOV.36" \
  --summary "Entries 4 and 6 were appended with the placeholder actor and a truncated summary; the actor is <name> and the authorizations granted are: <list the LPC.AUTH identifiers>"

python3 tools/ledger.py append --type amendment --actor "<name>" --role "human owner" --authority "DEC-0008" \
  --summary "Amend ROADMAP.md and DEVELOPMENT_WORKFLOW.md per docs/agent/notes/2026-10-11-amendments-for-owner.md sections 1 and 4" \
  --files ROADMAP.md DEVELOPMENT_WORKFLOW.md
```

The retrieval cap stays in force until that first entry exists: until then the researcher cannot fetch the Chua exponent, a cited AMI delay for Lorenz-63, or the XLA thread-cap flag. alphaXiv tools additionally need an edit to `.claude/agents/researcher.md` (its tool list has none).

## 6. Still open, for a later decision

- Concordance plan gaps D-19 to D-21 and D-28 (extra pass condition on H1a; no interval on A4o − A2; the gain bound's 0.9 bar and its covariance screen; V7 slope part) were proposed to WU-0002.4, .8, .9, .10 in the concordance; DEC-0008 covers V7 (A2), H1a's pass condition (above) and A4o − A2 (above) but not the gain bound beyond "reported, no bar" (v3). Planners follow the concordance's proposals and flag them in each plan.
- C8: refuse a confirmatory run on a dirty tree or unknown commit; record `VmHWM`. Decide at the pre-freeze review.

## 7. Additions after the XLA thread-cap work (WU-0012.4), 2026-10-11

- `DEVELOPMENT_WORKFLOW.md` §4.5 "Thread cap" says the XLA thread count goes through `XLA_FLAGS`. It does not: an unknown `XLA_FLAGS` entry aborts XLA, and the flag named in the 2019 jax issue is not registered. The cap is the plain environment variables `PJRT_NPROC` and `NPROC` (verified on jax and jaxlib 0.11.2 on this machine: the XLA pool equals the variable; unset it uses all 32 logical CPUs). Amend the text accordingly.
- `.claude/settings.json` `env` block: a direct `python -m lpcstudy` outside the wrappers still spawns 32 XLA threads. Add `"PJRT_NPROC": "4"` and `"NPROC": "4"` next to `LPC_THREADS` so interactive runs honor the budget too.
- Note for everyone: this machine has **32 logical CPUs**; "4 cores" is the thread budget (`LPC_THREADS`), and `nproc` shows 4 only because it reads `OMP_NUM_THREADS`.
- `PJRT_NPROC` is an undocumented knob (documented only in an XLA source comment): re-check it on every jax pin change.

## 8. Additions after the WU-0002.6 review, 2026-10-11

- v3 Q-N (lines 83, 345): add "a part with fewer than 50 states is inconclusive" (DEC-0014).
- WU-0011 follow-up (a main-session item, not an owner edit): a change to any `lpcstudy/*.py` should select `tests/unit/test_tools_test_impact.py` (the hand-written graph fixture is checked there), and `test_validation.py` was missing from the radius of the WU-0002.6 (b) and (c) runs because the tool's graph misses it (related to DEC-0003 Q2).

## 9. Additions after the WU-0002.7/.8 review, 2026-10-11

- ROADMAP.md WU-0002.8 acceptance (line 115): replace "`handling.zero_variance_corr`" with "the zero-variance count is `zero_variance_corr[rho][n_lib]` in the H2b result, a dict of counts (CP constant, PLP constant, both, non-finite, n_states)" (review R7/R8).
- Result keys: every criterion result carries `verdict` ("pass", "fail", "inconclusive"), `reason` (when inconclusive), `n_failed_resamples` and `pass` (DEC-0012 governs; DEC-0011 O3's `inconclusive_reason` is superseded for names). H3a's verdict is only pass or inconclusive.
- H3a needs at least 50 test states on the full sample (the per-regime minimum is waived, DEC-0011 O1); H2d keeps a pending marker until WU-0002.9 because its pass uses the point estimate (DEC-0011 O4).

## 10. Ruling on V7 (DEC-0015), 2026-10-11

- ROADMAP: the smoke acceptance wording ('smoke passes the gate') becomes 'smoke lists V1 to V7'; WU-0002.12 acceptance adds 'V7 passes at pilot size on DEV-0'.
- Ledger: the owner's `ruling` entry for DEF-0014 (option 1); say what 'superseded' means for the retirement of V7.

## 11. Additions from the WU-0002.9 plan check, 2026-10-11 (DEC-0016)

- v3 section 7: state the overall rule (supported only if all three systems pass; not supported if any fails; otherwise inconclusive; a missing system is inconclusive) and that the intersection-union remark controls only the error of "supported" (up to about 7.3% over three systems for "not supported", about 14% for H2c's two parts).
- v3 section 2, H1c: "(PLP)" stays; CP reported without a verdict.
- New ROADMAP row (gain bound): screen on the raw C >= 0 at every horizon, report the subset and the per-screen counts, no bar (concordance D-21(b), (c)).

## 12. Additions from the WU-0001.6 plan (DEC-0023) and the baseline change (DEC-0022), 2026-10-11

- ROADMAP section 2: WU-0001.6 is already the WU-0001 review sub-task; name the platform-record unit WU-0001.6b (or renumber) and list its dependency on WU-0002.12 (the regression found DEF-0024).
- ROADMAP WU-0002.12 acceptance: the baseline of the regression is the local re-run of tag `v1-baseline` on the reference platform (DEC-0022); the original pilot file is the historical record.
- DEC-0019 F1: once both runs carry W and U digests, state how a digest difference is treated in branch selection.

## 13. Additions from WU-0005.4, WU-0008 and the baseline run, 2026-10-11 (DEC-0024 addendum A1, DEC-0025)

- ROADMAP WU-0005.4 acceptance: the L2 tolerance 'relative 1e-12 on |c_k - J(u_k)|' is replaced by |c_k - J(u_k)| <= eta(2 sqrt(J) + eta), eta = 1e-12 max(1, ||X||_inf) (the relative form is not a valid round-off bound as J falls toward 1e-31); the p95 uses the inverted-CDF quantile; the report prints c beside c/rho^2 with the chi-square(D - m) reference (m = 3); add the key list of the `lm` summary (including `noise`, `gof_dof`, `fraction_late_progress`, `fraction_above_chi2`) and the handling schema `lpcstudy.handling/2`.
- v3 section 4 (LM): it covers about 2% wrong-basin estimates but not estimates still unconverged at the 15-iteration budget (2 to 13% in test configurations, production rate unknown): say whether the study measures and reports both (DEC-0025 D3) and whether 'PLP is the fixed 15-iteration LM' is a convention like LPC.NV.1 (DEC-0024 point 1).
- ROADMAP WU-0008 acceptance: H3c's budget 'Included' cell is 'no' (the test-state M draws do not enter H3c); the row-9 text says that Option C/K (DEC-0018) decides only whether the WU-0006 coverage rows stay asserted, and that widening the intervals is a separate owner decision (DEC-0024 addendum A1).
- Test amendment for the owner: `tests/unit/test_identifiers.py::test_no_stale_identifier_in_the_package` matches 'T1' inside a log filename (`slow-20261011T165447Z.log`) and inside the `kaplan_meier` docstring; it should match whole tokens only (with cases: '20261011T165447Z' is not flagged, a standalone 'T1' is). Recorded in DEF-0016; the WU-0008 text elides the letter in the filename meanwhile.
- DEF-0025 (robustness filter `d >= spec.dim` admits dof 0): choose `d > spec.dim` or None at dof 0.
- Ledger: the owner's `ruling` entries for the baseline instruction (DEC-0022) and for the pilot regression result (branch B, 0 failures: `docs/study/dev_regression_dev0_vs_local_v1.md`).

## 14. Questions and edits arising from the 2026-10-12 plans (WU-0002.11c, WU-0002.14, WU-0005.6, WU-0003; DEC-0026)

The planners' recommendations are working defaults, not covered by the 2026-10-12 ratification (made before they existed).

**WU-0002.11c** (branch `wu/0002-11c-start-states`): Q1 accept four new `context` leaves per system (`lyapunov_orbit_max_abs`, `trajectory_max_abs.{statistics,main,estimator}`) or keep only the Benettin maximum; Q2 accept the `lyapunov.json` format change (old entries recomputed once under the guard with a bitwise assertion).
**WU-0002.14** (seed-dependent start states + `make_rng` conversions): O1 statistics trajectory at the registry start (proposed) or seed-dependent; O2 oracle pool labelled `(seed, system, "oracle-pool")` (a change to DEC-0008 B's literal label); O3 add the system label to the label-free `make_rng` sites in this step (otherwise a second re-reference later); O4 (blocks the regenerated pilot) confirm `compare_pilot --redrawn-states` as the reading of DEC-0019 for a numbers-changing step (branch D forced, `--no-reference`, D2, N4, D3, every existing `context` leaf bitwise equal) and the D3 SE_new arm (DEC-0020); O5 name and location of the new reference (`docs/study/pilot_results_v3_dev0_reference.json`) and a v3-against-v3 mode of `compare_pilot` (needs the DEC-0023 F1 digest ruling); O6 raw start states in `context` for sealed runs; O7 rerun the WU-0006 consistency nodes once in this unit (about 20 min); O8 edits to Methods v2 ('separate: from a perturbed start') and the v3 Trajectories text (draft in the unit Log).
**WU-0005.6** (LM 15 against 30): O1 knob form (a CLI flag `--estimator-refine-steps`, refused for the sealed run; keep after the study?); O2 timing (run now, rerun once after the seed step: recommended); O3 the id clashes with the ROADMAP's WU-0005.6 (the WU-0005 review sub-task): rename WU-0005.7 or amend the ROADMAP; O4 does the DEV-0 measurement fill the LM row in the final report or does the full run need a 30-iteration twin; O5 the response if the change is not negligible (convention 'PLP is the fixed 15-iteration LM' / raise the design value, a v3 change folded into the seed-step regeneration / report and flag only); O6 the budget code change printing the measured row is a WU-0008 follow-up after O5.
**WU-0003** (plan amendment 1; corrections to the earlier estimate: the v3 pilot took 1980 s on CPU at `LPC_THREADS=8`, not 1.5 h; the full preset is about 1.7 to 2.2 h on CPU, not days): O1 the precondition order (DEF-0025 and tooling; WU-0002.11e; WU-0002.11c; the seed step with its regenerated pilot; the WU-0005.6 report; WU-0003.7 to .9; a gate at the rehearsal commit); O2 authorise R5 (full preset on DEV-2) and decide R4 and R6 (recommended all three); O3 set `XLA_FLAGS=--xla_gpu_deterministic_ops=true` for GPU runs (changes WU-0012's rule; the researcher first confirms what it does in JAX 0.11.2); O4 if GPU against CPU lands in the 'trajectory differs' tier: (a) pin trajectory generation to CPU, (b) the sealed run and its regeneration on the same device type (recommended; CPU as that device if R6 confirms about 2 h), (c) accept statistical agreement; O5 adopt the DEC-0023 F1 rule (a digest difference is a platform locus, not branch D); O6 per-state dump opt-in (recommended); O7 network-weight digests; O8 widen WU-0003.4 from one core cell to the pilot without robustness. ROADMAP amendments: add WU-0005.5, WU-0003.7 to .9 and the seed-step units to WU-0003.2's dependencies; pull WU-0016.3 forward.
**WU-0011.5:** the planner step was skipped by the main session (recorded in DEC-0026's note); the test-impact skill text and DEVELOPMENT_WORKFLOW 4.2 describe the older rule set: update them (your edit).

## 15. V6/V4 gate risk found by the WU-0002.14 P1 run (DEF-0026), 2026-10-13

- **Decision for you:** the validity gate can stop the sealed run. Per seed, V6 fails with probability about 4.4% (Chua; Lorenz-63 0.11%, Rossler 0; any system 4.5%) and V4 with a central estimate of 29% for any system (plausible range wide; n=2 per system). A failure at the sealed run is a hard stop, referred to you, never retuned (DEC-0027). Options without recommendation are in `docs/agent/notes/2026-10-13-v6-margin-mathematics.md` section 5 (branch `wu/0002-14-seeded-states`, merged with WU-0002.14): record the risk in the risk register and the preregistration; an offline V6 check on DEV-1 to DEV-4; the WU-0003 rehearsal; a V4 study over development seeds; a pre-seal rule for the response to a gate failure; evaluating the outcome-free gate checks first. Any change to the V4/V6 definition or bar is yours alone.
- v3 risk R1 and the M5(d) table: replace 'at least 13x margin, essentially no chance' by the draft text in section 4 of that note (for Chua, V6 is a heuristic indicator, not an exact error estimate; hypothesis row H3).
- Ledger: your `ruling` for the P1 result (WU-0002.14, redrawn start states: D2 exact, I1 33/33, R-f 30/30, D3 57/57, V1 to V7 pass) and, when you want it, the owner review of seed and statistics code that WU-0002.14 touches (needs owner review before freeze).

## 16. Owner flags from the WU-0003 mathematics check (M1 to M8; note `docs/agent/notes/2026-10-14-math-wu0003.md` on branch `wu/0003-rehearsal`, e8a39ed), 2026-10-14

The mathematician's refinements (plan amendment 2) keep every pre-registered threshold at least as strict; the following are yours.

- **OF-1:** whether a fitted-coefficient change beyond 1e-6 licenses H2c, H2d and H3c under tiers T1 to T3 (the cross-host margin there is only 1.7x).
- **OF-2:** if R0 shows a V1 difference above 1e-12 across devices, refer before R3; the principled replacement (about 1e-9) is wider.
- **OF-3:** which calibrated block-length reading to use (the acf-based factor or a pooled permutation test); the original rule stays reported.
- **OF-4:** correct the F1 'worst case' wording in WU-0008 M3 and DEC-0024 point 2 (a synthetic case reaches 1.38 F1; F1/hw_full is 0.54 to 1.20 at M = 200; 'below 10% of the half-width' would need M of about 5,700 to 29,000, so it is practically unreachable at M <= 399).
- **OF-5:** the change of the TD standard-error form (arms facing away, as DEC-0027 for D3; the constant 3.4 is kept over 18 parts, family level 1.2%).
- **OF-6:** pre-register the predicted gate failures over DEV-1 and DEV-2 (at least one V6 failure about 8.8%, 12.9% if R3 diverges; at least one V4 failure about 50 to 71%; see DEF-0026). R5's V4 uses 100 states and cannot be pooled with the pilot values.
- Predictions to read in advance (development, not tests): H2e will read 'not reproduced' on the narrow side (0.44 to 0.76 of v3's 0.04), H2b(ii) sits near its lower edge, Q-N is undetermined; the variance-ratio thresholds of C9 carry almost no information (some fire in about 97% of pilot runs with no dependence).

## 17. Owner flags from WU-0003.9 (`tools/compare_runs.py`, branch `wu/0003-9-compare-runs`; mathematician's note `docs/agent/notes/2026-10-14-math-wu0003-9-q1.md`), 2026-10-14

All of these loosen, or leave open, a tolerance or rule that exists before any rehearsal result: yours to rule; the tool keeps the strict reading until then.

- **OF-7 (loosens a pre-registered tolerance; not adopted):** four H1a leaves (`fitted_inverse_dim`, `ci_inverse_dim[0..1]`, `floor_rms`) fail the A6 T2/T3 'cp chain 1e-12' rule on the real BLAS kernel pair (7e-9 to 2.9e-7 relative). Cause: `curve_fit` (TRF, tolerances 1e-8, finite-difference Jacobian) amplifies the ulp change in W/U; an exact fit would pass 1e-12 (3.2e-14 input change moves the minimiser by at most 1.5e-13 s), but a stopping-test flip adds up to 7.4e-6 s (s = max(|lo|,|hi|)). The mathematician recommends re-tagging them out of the cp chain: `fitted_inverse_dim` and `ci_inverse_dim` under the A6 QoI rule (1e-4 s, class a), `floor_rms` as class g (as `ratio` and `ratio_ci` from the same fit already are); safety factor 2.5 against the a-priori bound 4e-5 s and 13.5 against the largest measured flip; 1e-5 s is not derivable. Until you rule, every T2 pair (R4 against R3, WU-0016 cross-host) fails on up to 24 H1a leaves at pilot size though the code is correct. Information added to OF-1: the A6 QoI rule has only a 2.5x a-priori margin on the H1a verdict leaves.
- **R5 (review of WU-0003.9):** on T1 to T3 pairs the tool prints rule O3 (declared tolerance above 1e-4) as information, because a pair passing at half its tolerance would otherwise always fail O3. That resolves a conflict between plan rules d2 and O3 in the looser direction: confirm or rule.
- **R6 / design gap:** A4 runs R2 and R3 with `--skip-robustness` and R1 without; robustness trains 4 extra estimators, so the estimator digest sets differ and R1 against R2/R3 gives 'tier undetermined' by construction. A scope rule must be pre-registered before R1 (the planner is drafting a working default).
- **Q7:** after R1 of the review, `gain_bound/n_screened_out` (25 to 23 on the kernel pair) fails because it is not on A6's list of discrete counts; should it license 0.1 hw?
- **Q8:** a `cov_digest` difference alone (W and U equal) is 'undetermined' (exit 2), not T2: confirm.
- **Q9 / untagged leaves:** 2849 untagged float leaves are treated as network chain (looser than A6 for the network-independent ones). The mathematician: tag every float leaf or give an explicit override before R1, with a test pinning the untagged set (a change in `tools/compare_pilot.py`'s table).
- **`handling` counts:** a differing count licenses 0.1 hw across its whole system, wider than the blocks that read that cell: confirm or narrow.
- **Q6:** the S3-pair fixtures of B2 d1 were replaced by synthetic trees plus a real-schema extract on a main-session instruction; to be recorded as a dated plan amendment (planner) or the 164 KB fixtures required.
- **Text slip:** B2 d3 and the WU-0003 note's M2 table quote 3.97e-7; under s = max(|lo|,|hi|) the figure is 2.94e-7 (declarations 1e-5 / 1e-4 unchanged).

## 18. Referral: WU-0003.9 after two fix rounds (`/refer`), 2026-10-14

The second re-review (`docs/agent/records/work/WU-0003.9-review-round2.md`, commit 8414273 on `wu/0003-9-compare-runs`; tool tip ed0cc05) leaves one blocker after the two fix rounds that the process allows, so the unit is referred (it is not merged anywhere and nothing else depends on it until the R4 against R3 comparison, so other units continue).

- **R14 (blocker, PRIME.2):** a `chosen_K` difference in a robustness variant opens the K scope of the main system (`count_scope` returns `(s, "K")` for `robustness/<s>/<variant>/chosen_K`, `tools/compare_runs.py` around lines 501-556). Probe on P1: `robustness/rossler/misspec=0.1/chosen_K` plus 1 makes `systems/rossler/H3c/A5_over_A4_mse`, moved by 0.5 x 0.1 hw, pass in T1, T2 and T3 where it fails without the change. Fix proposed by the reviewer: a robustness K scopes to its own variant (or the robustness block), with a test on that real path.
- **R15 (low):** the OF-7 pointer is attached to every failure under `H1a/by_noise`; it should be limited to `fitted_inverse_dim`, `ci_inverse_dim/[0|1]`, `floor_rms`.
- **R16 (low):** the exception list matches by name, so some clip counts and state denominators (`clip_sensitivity/test_eval_clipped_entries`, `href_clipped_draws/*`, `n_clipped_inputs`, `evaluation/denominators/test_states`, the `n_*_states` family) and threshold counts (`n_floored`, `n_w_zero`, `n_w_one`) fail exactly; Q7 should go to the owner and the mathematician as a class. The docstring's 'exactly A6's' overstates this.
- **R17 (low):** two looser readings are labelled strict (the whole-system clip scope called 'causal', and the K-block listing `follows_k`). Also: the whole-system clip scope is checked before the chain rules, so on a T2 pair any differing clip count lets that system's H1a fit leaves pass at 0.1 hw instead of cp 1e-12 (bypasses the OF-7 default); a robustness `n_states` licenses every robustness variant of its system.
- **Request:** authorize one more narrowly scoped fix round (R14 and R15 with R16/R17 relabelling, radius `tests/unit/test_tools_compare_runs.py` once, then a short check of R14 alone), or rule otherwise. I have not run it: it would exceed the two-round limit. Owner rulings are also needed on R5, R6 (plan amendment 3 option A), Q7 to Q9, OF-7 and the whole-system scope (reading 9).

## 19. WU-0003.8 review: owner questions and new rows (plan amendment 5, 687fca1 on `wu/0003-rehearsal`), 2026-10-14

- **OQ-R9 (seed code):** the diagnostics tool (`tools/rehearsal_diagnostics.py`) draws bootstraps and permutations with `make_rng(--seed, system, label)` and a scratch seed 20261018 (options `--permutations` 1000, `--resamples` 2000), unregistered. Working default (planner): fix those three values now; the first default-options report of each run is the record, any other value is labelled 'non-default option' on every reading it affects and is not the record. Should a registered diagnostic seed and fixed options be pre-registered before R1? Needs owner review before freeze.
- **H1a and H1c in the diagnostics:** H1d moves into .8 (computable from the dump). H1c needs a new bitwise-neutral sub-task .7c (dump schema `lpcstudy.states/2` with per-state H1c ratios and the H1a per-state squared seed errors). H1a has no influence series in the mathematician's list (M4.1): MA-1, a question to the mathematician. Until then they print 'not computable' and count toward exit 2, so the rehearsal cannot say whether the phi = 0 or phi = 0.3 coverage applies to the H1a interval (nor H1c's until .7c lands).
- **New rows:** .7c (dump schema /2), .8b (C4 LM readings and the N_lib bitwise check: B1 item 9, owned by no row before), .3a (`tools/rehearsal_report.py`, the C7 projections; must land before R1). Order: .8 fix round, .8b, .7c, .3a, then the gate at C_R. Each needs owner review before freeze.
- Ratified by the planner as definitions or stricter readings (confirm when you review): D1 coverage interpolation cov = cov0 + (cov0.3 - cov0) clamp(l/l_c, 0, 1) from l = 0; D4 (a) to (d); the exact D5 factor 1/(sqrt(2)-1); D6 five bins and the WU-0008 bound 0.40 s f_b printed with no cancellation credited; pilot-equivalent V4 (median of the first 40 half-widths) printed, never pooled with the pilot V4.

## 20. WU-0005.6: decisions around O5 (DEF-0027, DEF-0028), 2026-10-14

- **O5** (adopt the 15-iteration convention and report the flag; raise the design value to 30 or 60, which needs a new reference run and costs run time; or report and flag only): see `docs/study/lm_doubling_dev0_report.md` (v2 follows with corrections) and DEF-0027. DEV-0, B = 500, one realization.
- **DEF-0028 (rule R order):** amend `tools/lm_doubling.py` to the plan (a structural switch makes the part U before any X bullet) or amend the plan text to the tool's order. Effect on DEV-0: Chua H3c X to U; LM-row flag unchanged (5 of 18).
- Rule-R readings (R1 of the report check): endpoints cannot create N through S or remove X through d1, but can move a part either way through d2 <= d1/2; the report's 'never toward N' sentence is false and is replaced.

## 21. Plan amendment 6 (9f04013 on `wu/0003-rehearsal`) and the consolidated list of open owner items, 2026-10-14

- **OF-F3 (changes pre-registered predicted rates, stricter direction):** the H1a influence series (MA-1, `docs/agent/notes/2026-10-14-math-wu0003-ma1.md`) takes the diagnostics' series count from 18 to 24. Predicted rates under no dependence: acf familywise pilot 0.064 to 0.11, full 0.010 to 0.014; D2 'at least one of N' pilot 0.97 to 0.993, full 0.83 to 0.91. H1c (influence series already in M4.1) is added in row .8c as a secondary series; adding H1c or other series to the count is your choice (working default: count as written).
- **F4:** the .7c additions (four H1a keys, H1c eligibility masks, stronger b3) are kept by the planner; you may strike them.
- H1a is read as 'coverage not tabulated; phi = 0 reading only' (C3's 0.19 is not borrowed: looser); H1a and H1c no longer 'not computable' once .8c lands.
- The .7a/.7b a5 check is restated: each DEV-0 smoke compared with the v1 local baseline with --no-reference: same exit code and failure count, new + 11, nothing unclassified (6052 failures in both; new 1415 to 1426).
- **Consolidated open owner items for the rehearsal (answer before R1 where marked *):** OQ-R9 (diagnostic seed and options)*, OF-1, OF-2, OF-3, OF-4, OF-5, OF-6/P-2 (pre-register predicted gate failures)*, OF-7 (re-tag four H1a leaves), OF-F3, PF-1 to PF-5, C6-R5 (O3 on T1 to T3), C6-R6 (R1 against R2/R3 scope rule: working default option A, run R2/R3 without --skip-robustness)*, C6-H (handling-count scope), Q6 to Q9 and the untagged-leaf requirement C4*, WU-0003.9's R14 (referral: one more fix round), amendment 1's O1 to O8, O5 (LM convention, DEF-0027) and DEF-0028 (rule R order), DEF-0026 (V6/V4 gate risk), DEF-0018, N3 scope, the estimator convention, Chua H2a(i) under finite-M bias, all ledger entries, and `main` (only when fully green).

## 22. WU-0003.3a: kappa_E (OF-R2, OF-G6), H2a(ii) (OF-G3) and new row .10, 2026-10-15

- **OF-R2 / OF-G6 (method of B1 item 6, no pre-registered number changes):** the applied-mathematician (note `docs/agent/notes/2026-10-14-math-wu0003-3a-kappa.md`, 1f1d128 on `wu/0003-3a-report`) shows that the 'point estimate from the dump' of kappa_E is biased: from +0.003 to +0.135 in kappa on 56 synthetic cells (upward in all 56, so the projected half-width is 0.5% to 19% too wide), and in other worlds -0.02 to -0.07 (too narrow by up to 7.5%); the oracle half moments carry no per-draw A3/A4/A5 weights, so they cannot identify the draw-noise component. The pre-registered ranges (H2c, H2d 0.504 to 0.712; H3c 0.507 to 0.717; kappa in [0.7071, 1]) are exact bounds under the iid-draws hypothesis. Choose: (a) use the range at R1 (working default; reading (ii) is then wider on the low side, the PF-4 effect already recorded), or (b) add `core/cp_err_href` and `core/plp_err_href` ((n, E) each) to the dump and use the half-split estimator before R1 (unbiased to -0.002 to -0.005 in kappa squared but noisy: SE(kappa^2) 0.05 to 0.10 at n = 500; needs a new dump sub-task and a redesign of f2). Under (a), the exit-0 rule of amendment 7 G2 (a point kappa_E is required for H2c, H2d, H3c) makes exit 0 of `rehearsal_report` unreachable: the planner is asked for the rule.
- **OF-G3:** the H2a(ii) comparison against v3: default the margin band, 'not reproduced' iff hw_full > 0.0933 or < 0.0850 (the developer's hw band [0.0603, 0.135] printed beside it, non-governing). Most H2a(ii) parts are predicted to read 'not reproduced'.
- **New row .10:** `tools/rehearsal_common.py` (shared numerics of the report and diagnostics tools), byte-identical golden reports before and after the move, after .8, .8b, .8c, .3a merge and before the gate at C_R. Needs owner review before freeze.

## 23. Referral: WU-0003.3a after two fix rounds, 2026-10-15

Re-review round 2 (`docs/agent/records/work/WU-0003.3a-review-round2.md`, 680aace on `wu/0003-3a-report`; tool tip 960831d) confirms R1, R3, R4, R5 and G1 to G3 (H3a recomputed by hand for every P0/P1 pair: difference 0.0; the H2a(ii) margin band; production Holm and alpha 0.01 read by AST) and leaves the following after the two fix rounds the process allows; the unit is referred (not merged; nothing else depends on it before R1), like WU-0003.9 (section 18):

- **R7 (medium, PRIME.4):** `KAPPA_POLICY` (module constant, 'range' default; not settable from the CLI or the environment; only a source edit or a test monkeypatch changes it) with an unrecognised value (`"Range"`, `"points"`, `None`) keeps the range and prints FALLBACK but records no 'not computable' item: confirmed exit 0 with 12 FALLBACK rows and 0 counted. Fix: validate against `{"range", "point"}` at the start of `run` and exit 2 otherwise (or count the fallback on every non-'point' path), with a test.
- **R8 (low, text):** every `None` H3a pair is labelled 'zero log-rank variance'; production also writes `None` for an empty regime. R9 (low, print): a lower-bound pair prints `p_full <= 0` (underflow); print `p_full < 1e-300`.
- **R10 (planner and owner):** under default (a) the exit-0 rule of amendment 7 G2 can never be met (a point kappa_E is required). Choose: add a G2 clause for the range (a final), or build (b) (new dump arrays and the half-split estimator, which is a different estimator and should not reuse the switch); remove the 'point' branch if (a) becomes final.
- **Request:** authorize one more narrowly scoped fix round for WU-0003.9 (R14 to R17) and WU-0003.3a (R7 to R9), each checked by its unit test file once and a one-finding read, or rule otherwise.

## 24. Owner instruction of 2026-10-17 (recorded by the main session; not a ledger entry)

After the stop of 2026-10-16 the owner wrote: 'proceed. I modified the .claude/settings.json on main to cut down on the number of asks. limits are lifted, run as fast as possible'. The main session reads this as: resume all lanes, run lanes and presets in parallel and use the machine fully, and take the one further narrow fix round that sections 18 and 23 asked for on WU-0003.9 (R14 to R17) and WU-0003.3a (R7 to R9). It does not read it as lifting the safety rules (development seeds only; never the confirmatory seed or flag; no history rewrite; no criterion, tolerance or bound loosened; governance, ledger, ROADMAP and `.claude/` edits remain the owner's; no merge to `main`), nor as answering the open owner questions of sections 16 to 23 (which still bind R5/R6 authorization and the pre-registrations before R1). If the reading is wrong, say so.

## 25. R0 result and referral of OF-2 before R3 (2026-10-17)

R0 ran at develop e3b2645 (record `docs/agent/records/work/WU-0003-R0.md` on branch `run/r0-e3b2645`; provenance commit edb10e7 = e3b2645 plus one docs file). Three smokes with all three systems, development seeds, all exit 0: DEV-1 GPU (698 s), DEV-1 CPU (175 s), DEV-0 CPU (61 s).

- **DEV-0 against the step-4 reference (the 7c-tip dump-off smoke):** leafdiff 4794 common leaves, 0 different, 0 removed, 0 added; `compare_runs` T0 PASS. 7a leaves: 11 added against the dcc4ff2 smoke, as predicted. Dump absent.
- **GPU check:** device recorded as NVIDIA GeForce RTX 4090 (backend gpu), `JAX_PLATFORMS=cuda`, x64 true, `device_peak_bytes` 107,600,896, 100% utilization seen, no fallback; memory about 5% of 24 GB; DEV-1 seed 2844678021587022684 equals the registry value; weekly tally 0.1939 h.
- **Device probe (GPU against CPU, DEV-1):** tier **TD on all three systems**: every TD trigger differs (`state_mean_digest`, `lambda_max` by 1.9e-4, 3.1e-3 and 2.2e-2, `interval`, both start-state parts, `main_digest`, `estimator_digest`); no context digest is equal; TD statistic 18 of 18 parts, 0 failing, max |z| 2.53 (symmetric) and 2.61 (away) against 3.4. M8's answer: R0 cannot select T1 for R1 against R3; the plan's R1 against R3 is a TD comparison. The tool states that a TD pair between devices triggers O4 (choice of confirmatory device).
- **GPU speed (C6, smoke size only):** 4.0 times slower than CPU (698 against 175 s); the context build 55, 68, 83 s against 2.0, 1.4, 2.0 s. No conclusion for the pilot.
- **Referral (OF-2):** all six V1 leaves differ between GPU and CPU by 3.5e-10 to 1.5e-8 absolute, above the 1e-12 of item 11, which says refer before R3. In a TD pair the two contexts differ, so V1 is computed on different trajectories and the comparison is not like for like. The main session therefore holds R3 (CPU pilot on DEV-1) and does not rule on the applicability of item 11 or on its replacement (about 1e-9, wider). Please rule: (a) item 11 applies only to pairs with equal contexts (T0 to T2), so R3 may run; (b) it applies as written, with the replacement bound; (c) other. R1 and R2 (GPU) proceed under the working defaults.
- Smoke validation gates printed 'FAILED, provisional' on several smoke runs, with different flags on GPU and CPU; read as smoke size plus different trajectories, not a finding (details in the record).

## 26. Owner answers of 2026-10-17 given through the question tool (recorded by the main session; not ledger entries)

The owner answered four questions (asked in the session on 2026-10-17):
- **OF-2:** 'Equal contexts only': the V1 1e-12 rule of item 11 applies only to pairs whose context digests are equal (tiers T0 to T2); GPU-against-CPU pairs (TD) are judged by the TD statistic. R3 may run.
- **R5 and R6:** both authorized (full preset on DEV-2, GPU with dump on; and on the CPU with LPC_THREADS=8).
- **DEF-0026:** 'Offline V6/V4 check' only: run the V6 and V4 gate checks on DEV-1 to DEV-4 (about 10 s per system for V6) to test the estimates. Not chosen: pre-registering the response to a sealed-run gate failure, evaluating the outcome-free gate checks first, a risk-register-only entry.
- **OQ-R9:** 'Fix as defaults': seed 20261018, 1000 permutations and 2000 resamples are the pre-registered diagnostic defaults; the first default-options report per run is the record; any other option is labelled non-default and is not the record.

## 27. R1/R2 results and the offline V6/V4 check (2026-10-17)

- **R1 and R2** (DEV-1 pilot, GPU, develop c9bb981; R1 with the dump; checklist committed as 01d9fc7 before launch, runs carry dirty False): both exit 0 in 1659 s and 1640 s; **R1 against R2 is tier T0: all 20533 leaves equal** (repeated GPU runs on this host are bitwise identical); weekly tally 1.11 GPU-hours. DEV-1 gate V1 to V7 all pass on all three systems; V4 median half-widths 0.0349, 0.0439, 0.0272 (bound 0.05); P2(c) 0 violations; H_ref clip counts 0. `rehearsal_report.py`: 12 of 12 reproduction checks MATCH, kappa_E range governs 12 of 12, exit 0. **`rehearsal_diagnostics.py`: exit 1, three reproduction MISMATCHES, all `H1d nhat Spearman` (dump against `results.json`: 3.5e-6, 1.1e-5, 8.6e-5 against an allowed 6e-13)**; every other check MATCHes and the stack check says SAME; cause not yet known (tool or dump defect; `nhat` goes through the `log(x+c)` column of `core/profile`): under investigation, R5 waits for it because R5 uses the same dump code.
- **Pre-registered predictions on DEV-1 (one realization):** P-2: 0 V6 and 0 V4 failures (consistent); H2e narrow: matches (ratios to v3's 0.04 between 0.51 and 0.76); H2b(ii) at the lower edge: 11 of 12 within, Rossler H2b(ii) 0.863 of 0.03 just above the predicted 0.68 to 0.85; Q-N undetermined: matches; D1 77 of 78 series within threshold (exception Rossler H1d estimation_seed, +0.178); D2 fired on 4 of 24 primaries; H3a pass not reachable at full size on any system (K_pilot 6, 4, 5); H2a(ii) margin reading fires on 6 of 6.
- **Offline V6/V4 (DEF-0026 status line):** one real V6 failure: Chua DEV-1 full-preset context, 1.53e-3 above the 1e-3 bar; V6 failure per seed 4.6% for Chua, 4.8% any system; V4 or V6 combined 26 to 38% per seed at pilot size and 11 to 25% at full size. Seeds used: DEV-3 and DEV-4 now used (V6 contexts only, no outcome); DEV-2 was also evaluated at the pilot preset context for V6 (the plan keeps DEV-2 for full-size runs; V6 looks at no outcome). Registry statuses are yours.
- **R3 and R6:** the wrapper takes the one lock for every pilot or full run, also on `--device cpu`; the owner chose to run them sequentially under the standard lock (no per-run lock override; the main session's separate-lock proposal was refused by the permission system and not used).

## 28. R5 result: the first observed V6 gate failure (2026-10-17; main session; not a ledger entry)

Source: lane report of the R5 run (run branch `run/r1-c9bb981`, evidence commit d22044d, record `WU-0003-R1R2.md` and the `-R5` report files there). Code develop c9bb981 (code identical at b6ede8c). R5 = full preset, DEV-2, GPU, `--states-dump`; exit 0, 2739 s, clean wall time (R6 started 31 s after R5 ended).

- **Gate (GPU context of DEV-2, full size).** **Chua V6 FAILED: 2.405e-3 against the 1e-3 bar** (flagged provisional by the code). Chua V1, V2, V4, V5, V7 pass; Lorenz-63 and Rossler pass V1 to V7 (V6 3.6e-5, 3.8e-5). GPU and CPU contexts differ completely, so no value was predictable for R5; the offline check gave 4.3% for a Chua V6 failure under the GPU law, and this is that event. The CPU context of DEV-2 full is predicted to pass (3.34e-4); R6 will show. No bar, tolerance or criterion changed; this is a DEV run and its result is reported, not repaired (PRIME.2, PRIME.4).
- **V4 at full size (first measurement).** M=200 median half-widths 0.0263, 0.0424, 0.0299 against 0.05: all pass. The sqrt(40/100) scaling of R1's pilot values predicted about 0.022, 0.028, 0.017 (observed 1.19, 1.53, 1.74 times that); seed and GPU context differ, so V4 is not pooled with the pilot V4. Tally of gate failures on the GPU so far: V6 1 (R5 Chua), V4 0.
- **R1 (DEV-1 pilot, GPU) vs R2 (repeat).** compare_runs tier T0 PASS, all 20533 leaves equal: repeated GPU runs on this host are bitwise identical. V1 to V7 pass on all three systems in both.
- **Tools.** rehearsal_report: exit 0 on R1 and R5 (12 of 12 reproduction checks MATCH; kappa_E range governs; projection factors 1 for R5, so numbers are observed half-widths against v3). rehearsal_diagnostics: exit 1 on R1 and R5, only the 3 H1d nhat Spearman entries (the recorded tie artefact, b6ede8c). Stack check SAME; no "not computable" entries.
- **Counters.** C2: P2(c) 0 violations, chain counters 0 over 4000 states per system. C3: all H_ref clipped-draw counts 0. C4: 0 LM findings outside a band (R1 had 2 on Rossler). C5: nu_cap_clips 140/188/173; Rossler nu_replacements 163, lm_nonfinite_cost 468 (counted, reported).
- **Pre-registered predictions (development only).** 10 of 12 parts within. H2e narrow: all 6 cells within in both runs. H2a(ii) margin reading fires 6 of 6 (R1), 5 of 6 (R5; Chua interior no longer fires). H3a pass at full size reachable on Chua only (Holm p 0.00397). Observed R5 against the R1 projection: 4 reading-(ii) triggers over 69 parts (about 0.47 predicted); different seed and context, so this is a calibration observation for the owner, not a defect.
- **Diagnostics.** D1 acf(1): 77 of 78 within threshold in both runs. D2: rule fires on 4 of 24 primaries; block length 5 flagged as a design question on Lorenz-63 and Rossler. D3 log-SD 2.7 to 3.0 on Lorenz-63 (C2h/C4h rows apply). D5/D6: finite-M bias "not determined" on all three systems, so budget row 1 stays "not below 10%" (PF-5).

**For the owner (adds to the list in section 21).** (1) The V6 failure is a concrete instance of DEF-0026: the sealed gate is the same exposure, roughly 4.4 to 4.8% per fresh seed for V6 alone, and a failure is a hard stop referred to the owner (DEC-0027); the owner chose no pre-seal response rule (section 26). (2) Reading-(ii) triggers over the R1 projection (above). R6 (CPU, DEV-2) is running; its report will add the CPU-context V6 and the R5-vs-R6 TD comparison.

## 29. Owner answers of 2026-10-17 (second round, question tool) and the R6 result (main session; not ledger entries)

**Answers recorded (owner, through the question tool):**
- **O5 (DEF-0027):** "Report and flag only". Design value stays 15 iterations; the iteration-sensitivity flag is reported per part. No new reference run.
- **DEF-0028:** "Amend tool to the plan". `tools/lm_doubling.py` is to put the structural switch (class U) before the X bullets, as the plan text says. A code change with a test, after results exist, documented; dispatched to a developer.
- **OF-R2 / OF-G6:** "Keep the range". The pre-registered kappa_E range [0.7071, 1] governs (as in R1 and R5); no dump change, no half-split estimator, no rerun.
- **D2 block length 5:** "Report only, decide after R6". One consolidated recommendation to follow the precision report (WU-0003.3) and the R5/R6 reading.

**R6 (DEV-2, full preset, CPU; run branch `run/r3r6-c9bb981` d9c8b95; records `WU-0003-R3R6*.md/.txt`):** exit 0, 17031 s (4.73 h; above the A1 planning bound of 4 h; other lanes may have shared the CPU, so not a clean C6 figure; GPU R5 was 6.2 times faster). V1 to V7 and gate_pass pass on all three systems: V6 2.2e-5, 3.1e-5, **3.3e-4 (Chua; predicted 3.34e-4)**, V4 half-widths 0.0290, 0.0350, 0.0230. P2(c) 0 violations; clipped H_ref draws 0 (bound transferred); error_clips 0, failed_variants 0; counted handling: nu_cap_clips 460, nu_replacements 425 (Rossler), lm_nonfinite_cost 716, zero_variance_corr 505565 (all CP).
- **R5 vs R6 (TD):** tier TD on all three systems; TD statistic 18 of 18 parts computed, 0 failing; max |z| 2.32 symmetric / 2.26 away (Rossler H2b(i)), bound 3.4. PASS. 52 verdict-type leaves differ and are reported without failure. This is the device-dependence evidence for O4.
- **Report on R6:** exit 0; reading (i) fires on 10 of 18, reading (ii) on 10; H2e narrow side outside v3's 0.04 on Lorenz-63, Rossler, Chua; pre-registered predictions 11 of 12 within (Lorenz-63 Q-N oracle logit 0.0210, 0.525 of 0.04; was "undetermined"). H3a pass reachable only on Chua. Diagnostics exit 2 by design (no dump on R6). One C4 finding: Rossler `base|rho=0.05|sweep` oracle `fraction_no_decrease` 0.0017 above band [0, 0.0013] (reported, not acted on).
- **V6/V4 tally for DEV-2:** V6 failed on the GPU context (Chua, 2.405e-3) and passed on the CPU context; no V4 failure at full size on either. Same seed, different context, different outcome: the sealed gate outcome depends on the device, a fact for O4.
- Record wording: the R6 result section contains one garbled sentence ("... A1 planning upper bound of 4 h? No: above it"); it means the wall time exceeded 4 h. The record is append-only; this line is the correction.

**Draft for the owner: WU-0003.4 and the reproducibility tolerance (for WU-0003.6; a proposal, not a decision).** Measured: GPU-to-GPU on this host, same code, seed and context (R1 vs R2): **bitwise identical, 20533 of 20533 leaves** (so the roadmap's rule "10 times the GPU-to-GPU maximum relative difference, rounded up to a power of 10" is degenerate: 10 times zero). GPU-to-CPU (R3 vs R1 at the pilot; R5 vs R6 at full size): contexts differ completely, so the V1 1e-12 rule does not apply (OF-2, section 26) and the comparison is the TD statistic: max |z| 2.73 (pilot), 2.32 (full), bound 3.4, all pass. Proposed declaration: (a) same-context reruns (same device, same host, same code): bitwise (T0), with 1e-12 relative as the declared tolerance elsewhere (V1 rule, equal context digests only); (b) cross-device: TD statistic at z level 2.394, bound 3.4, with verdict-type leaves reported, not failed. The owner decides, and whether the sealed run is on GPU or CPU (O4, DEC-0027).

**Draft for WU-0003.6, sample size (rehearsal evidence):** at the full preset, H3a pass is reachable only on Chua (R5 Holm p 0.00397; R6 same pattern); H2e's narrow side is outside v3's 0.04 on all three systems in R6 (a precision gain, not a loss); reading (ii) fires on 10 of 18 parts in R6 and 4 of 69 over the R1 projection in R5, so the full preset is not oversized and the pilot size is not enough for the same statements. Whether to change sample size is the owner's; no recommendation to change it is made here.

## 30. DEF-0028 resolved (2026-10-17; main session; not a ledger entry)

Per your ruling (section 29) `classify` in `tools/lm_doubling.py` now applies a structural switch (M7) before any X bullet. Merged f14c8fa after independent review (R1 to R3 fixed; re-review approves; unit radius 134 passed once). Effect on DEV-0: Chua H3c X to U only; N 5 / X 6 / U 7; LM-row flag still 5 of 18; report v3 in `docs/study/`. **For you to confirm before freeze (readings the plan leaves open):** (1) a half-width <= 0, a NaN value, and an infinite point estimate with finite bounds are not structural switches (they stay U, or X if the verdicts differ); (2) an infinite lower or upper bound at any arm is a structural switch (M7: "an infinite bound").

## 31. Block-length analysis and owner answers (2026-10-17; main session; not ledger entries)

Analysis: `docs/agent/notes/2026-10-17-math-block-length.md` (merged 6ec43cb; applied-mathematician; R1 and R5 dumps, CPU, no new runs). Findings: D2 fires on 4 of 24 primaries in both runs, which is what no dependence produces (null mean 4.15 and 2.23; P(count >= 4) 0.60 and 0.19; at-least-one 0.988 and 0.897); the calibrated readings (beta-hat-5 on 0 of 48 series, pooled permutation on 0 of 6 system-runs, smallest p 0.025 against 0.01) never fired; short-range dependence is real on Lorenz-63 (V*(5)/V*(1) x1.077, p 0.003) and absorbed by block 5; beyond 5 pooled V*(10)/V*(5) x1.011 (upper 1.032), V*(20)/V*(5) x1.041 (upper 1.090), a half-width effect at most +1.6% / +4.4%, below the phi = 0.3 stress row (+7.3%). Everything beyond 5 states rests on one realization per run; slow weak dependence is unresolvable at n <= 1000 and belongs in the limitations.

**Owner answers (question tool):** (1) **keep block length 5 for all three systems** (no amendment to v3 or Methods v2); (2) **OF-3: the pooled permutation reading governs the D2 verdict; the A5 rule and beta-hat-5 stay computed and printed as information**; (3) **add a report-only "block-sensitive" label** to any primary verdict that widening the half-width by sqrt(max(1, V*(10)/V*(5))) would change (changes no criterion). Items (2) and (3) are a tool change, dispatched to a developer with tests and independent review. Limitation to state in the report: slow weak dependence; Lorenz-63 H1a rho = 1% has the largest acf(1) in both runs (selection-adjusted p 0.018 in R5).

## 32. Process slip: the golden regression test was red on develop from the H1d merge (2026-10-18; main session)

Found by the independent review of WU-0003.8d (R3, `docs/agent/records/work/WU-0003.8d-review.md` on `wu/0003-8d-block`). `test_regression_golden_outputs_are_byte_identical` went red at the develop merge 1ed9e2d (WU-0003.8 fix round 5, 53483c4, changed the printed H1d check line; that branch's base ad25e4e predates the goldens, which came in with e3b2645). The merge of 1ed9e2d into develop was made by me without rerunning the golden test after it (the line gate GATE-2026-10-17 covered the line tip before this fix round); nothing detected it until 8d. Effect: develop's test state was red for that test from 1ed9e2d until 6b04e49 (on `wu/0003-8d-block`, 14 H1d check lines only, numbers and the tolerance unchanged); `main` is untouched. Lesson recorded: a merge that joins a branch whose base predates a golden or test file needs that test in the post-merge radius. The next whole-suite gate (`LPC_GATE=merge`) before any main request will confirm the state.

## 33. Owner answers of 2026-10-18 (third round, question tool; recorded by the main session; not ledger entries)

- **OF-7:** re-tag the four H1a leaves (`fitted_inverse_dim`, `ci_inverse_dim[0..1]`, `floor_rms`) out of the cp chain, under the A6 QoI rule (1e-4 s, class a). Code change (tag table in `tools/compare_pilot.py`/`compare_runs.py`) with a test pinning the tags; the 1e-12 rule stays elsewhere.
- **OF-1:** keep strict (no licence for H2c, H2d, H3c under T1 to T3 for a fitted-coefficient change beyond 1e-6).
- **R5 (O3):** information-only on T1 to T3 pairs, confirmed.
- **Q7, Q8, Q9, handling-count scope:** keep the tool's strict readings (the handling-count licence kept as written).
- **OF-4:** correct the F1 'worst case' wording of WU-0008 M3 and DEC-0024 point 2 (draft for the owner to enter).
- **OF-5:** adopt the away-arm TD standard-error form as the failing rule (bound 3.4 over 18 parts); the symmetric form stays printed as information.
- **OF-F3:** keep N = 24 as written (H1c not counted).
- **OF-G3:** the margin band governs the H2a(ii) comparison (0.0850 to 0.0933); the wide hw band stays printed, not governing.
- **WU-0003.6:** reproducibility tolerance: adopt the proposal of section 29 (bitwise/1e-12 at equal contexts; TD statistic at z 2.394, bound 3.4, across devices); sample size: keep the full preset. Decision-entry texts are drafted for the owner to enter (agents do not write ledger entries).
- **F4 and Q6:** keep both as built; Q6 recorded as a dated plan amendment (planner draft).
- **Freeze checklist:** prepare now (WU-0004.1, main session).

## 34. Drafts for the owner's decision entries and where the evidence differs from the rulings as worded (2026-10-18; main session)

Drafts: `docs/agent/notes/2026-10-18-owner-decision-drafts.md` (merged; planner claude-opus-5-5). Points the planner found where the evidence does not match the wording of the rulings (for the owner, and carried into the freeze-blocker list):
1. Tolerance figures: V1 is absolute 1e-12, V2 1e-10; 1e-12 relative applies only to the cp, oracle, dynamics and fixture chain leaves; QoIs and interval endpoints use 1e-4 max(|lo|,|hi|). The draft states them as the tool implements them (the question text said "1e-12 relative where contexts are equal"; read it as the tool's per-chain rules).
2. No equal-context non-bitwise pair (tiers T1 to T3) was run in the rehearsal (R4 not run): that part rests on the WU-0003.9 kernel-pair evidence.
3. The z values quoted (2.73, 2.32) are the symmetric form; away-arm values are 2.72 (R1 vs R3) and 2.26 (R5 vs R6). Both pass. OF-5 is looser per part (away alone gives a lower z on 7 of 18 P0/P1 parts); the code change is with the developer (`wu/0003-9c-ruled`).
4. A TD pass does not reproduce verdicts or the gate: 52 verdict-type leaves differ, and Chua's gate passes on CPU and fails on GPU for DEV-2.
5. "O4 per DEC-0027" in the sample-size question mixed two questions: DEC-0027 rules on WU-0002.14's O4 (D3 arm pairing); the confirmatory device choice is plan amendment 1's O4, still open.
6. The ROADMAP WU-0003.4 definition of done is not met as written (no "one core cell" run, no differences table of that form, `tests/gpu/test_reproducibility.py` absent; the 10x rule is degenerate): the row needs the owner's edit, or the owner requires the gpu test.
7. OF-4: no criterion depends on the old F1 wording, but `lpcstudy/budget.py` (line 702, docstring 565 and 570) prints "indicative worst case <= F1" into every RESULTS.md (R1, R2, R3, R5, R6 carry it; a sealed run would): correcting it is a report-text code change before the freeze.
8. Q6: amendment 3 C2 says d3 ran on the unedited S3 pair; it exits 2 there (d3 was shown on scratch copies; the committed test is synthetic). Confirm "keep as built" covers d3 as well as d1.
