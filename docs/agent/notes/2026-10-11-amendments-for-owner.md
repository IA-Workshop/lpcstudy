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
