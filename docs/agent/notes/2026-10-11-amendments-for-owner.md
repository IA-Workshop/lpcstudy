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
