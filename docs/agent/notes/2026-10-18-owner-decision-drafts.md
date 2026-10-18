# Drafts for the owner: WU-0003.6 decisions, the OF-4 correction, the Q6 plan amendment, and the DEV-run limitations

Prepared 2026-10-18 by claude-opus-5-5 (planner), from the owner's rulings recorded by the main session in `docs/agent/notes/2026-10-11-amendments-for-owner.md` §29, §31 and §33 (develop `b554041`). **These are drafts.** Agents do not write ledger entries, `decisions.md` entries, ROADMAP, v3 or Methods v2 (GOV.49). The owner enters sections 1 to 3 (and the main session or owner appends section 4); `DEC-nnnn` numbers are left blank. Every number below comes from **development runs (DEV-0, DEV-1, DEV-2) and is not a hypothesis-test result.**

Sources read (all on develop unless stated): the amendments note §15–§33; `docs/agent/records/decisions.md` (DEC-0024, A1, A2, DEC-0026, DEC-0027); `ROADMAP.md` lines 176–189; `WU-0003-dev-rehearsal.md` (amendments 1 to 10, Log); `WU-0008-report-budget.md` M3; `docs/agent/notes/2026-10-14-math-wu0003.md` §M1.4, §M5; `tools/compare_runs.py`; `lpcstudy/budget.py`; `tests/unit/test_budget.py`, `tests/unit/test_tools_compare_runs.py`; run records `WU-0003-R1R2.md` (branch `run/r1-c9bb981`, d22044d) and `WU-0003-R3R6.md` with its compare and gate files (branch `run/r3r6-c9bb981`, d9c8b95).

---

## 1. Draft decision entry: reproducibility tolerance (WU-0003.6, from WU-0003.4)

```
## DEC-nnnn: WU-0003.6: the reproducibility tolerance declaration (same context bitwise; equal contexts by the A6 tiers; across devices by the TD statistic, away-arm form)  (2026-10-18, human owner; ruling given through the question tool, recorded in the amendments note §29 and §33; text drafted by claude-opus-5-5 (planner))

**Decision.** The project declares its outputs reproducible as follows (LPC.PC.18 "within the tolerance recorded in WU-0003"; REPRO.3; NVVUQ.12). The tier of a pair is selected mechanically from the context digests by `tools/compare_runs.py` (A6, B1 item 1), and the pair is judged by that tool.
1. **Same context, same device type, same host, code, seed and environment (tier T0): bitwise.** Every leaf identical (IEEE bytes), except timing (`seconds`) and the top-level `provenance` block.
2. **Equal context digests, different device, host, BLAS kernel or network weights (tiers T1 to T3): the A6/B1 tolerances as implemented in `compare_runs`.** The network-independent chain leaves (`cp`, `oracle`, `dynamics`, `fixture`) within 1e-12 relative; V1 (`delay_jacobian_rel_err`, `gain_rel_err`) within 1e-12 absolute; V2 within 1e-10 relative; LM summaries by the T1/T2 rules; QoIs and interval endpoints within 1e-4·max(|lo|, |hi|) (class a; this includes the four H1a fit leaves re-tagged under OF-7); other classes by the 10x rule, capped at 1e-4; every verdict identical. By OF-2 the V1 1e-12 rule applies only to these equal-context pairs.
3. **Different contexts (tier TD; GPU against CPU in practice): the TD statistic.** No per-leaf tolerance. For each of the 18 primary parts (6 per system; H2a(ii) counts two), z = |d| / sqrt(se0^2 + se1^2) with each se taken from the interval arm that faces away from the other estimate (if run 1 lies above run 0: run 0's lower arm and run 1's upper arm; the pairing of DEC-0027; OF-5), se = arm / z_level, z_level = Phi^-1(1 - 0.05/6) = 2.394 (the primary level 1 - 0.05/3). A part fails if |z_away| > 3.4 (Phi^-1(1 - 0.01/30) = 3.403; family level at most 1.2% over 18 parts). The symmetric form (se = hw / z_level) is printed as information and does not fail a part. Verdict-type leaves that differ are reported, not failed.
4. **What a TD pass does not mean.** It does not reproduce verdicts or the gate outcome. R5 against R6 passes the statistic while 52 verdict-type leaves differ and Chua's `gate_pass` differs (V6 on the GPU context 2.405e-3, a fail; on the CPU context 3.3e-4). The choice of confirmatory device (WU-0003 plan amendment 1, A12 O4) is **not** decided here.

**Evidence (DEVELOPMENT; not hypothesis tests).**
- R1 against R2 (DEV-1 pilot, GPU RTX 4090, code c9bb981, repeated on the same host): tier T0, **20533 of 20533 leaves equal** (provenance and 23 timing leaves excluded). `WU-0003-R1R2.md` and `WU-0003-R1R2-compare-r1-r2.txt` on `run/r1-c9bb981`.
- R0 (smoke): DEV-0 CPU against the step-4 reference smoke: T0, 4794 leaves, 0 different (CPU bitwise). DEV-1 GPU against DEV-1 CPU: TD on all three systems; 18 of 18 parts, 0 failing, max |z| 2.53 symmetric / 2.61 away. All six V1 leaves differ across devices by 3.5e-10 to 1.5e-8 absolute (different trajectories: the reason for OF-2).
- R1 against R3 (DEV-1 pilot, GPU against CPU): TD; 18 of 18 parts, 0 failing; **max |z| 2.73 symmetric, 2.72 away** (Lorenz-63 H2a(ii) zero); 30 verdict-type leaves differ. `WU-0003-R3R6-compare-R1-R3.txt`.
- R5 against R6 (DEV-2 full, GPU against CPU): TD; 18 of 18 parts, 0 failing; **max |z| 2.32 symmetric, 2.26 away** (Rossler H2b(i)); sum z^2 16.5 / 15.8; 52 verdict-type leaves differ. `WU-0003-R3R6-compare-R5-R6.txt`.
- No rehearsal pair fell in T1 to T3 (no R4 record exists on the branches read). The T1 to T3 numbers rest on the WU-0003.9 kernel-pair evidence (WU-0002.14 S3 smoke pair, scratch copies with injected digests: declared 1e-5 for class (a), largest rel 2.94e-7; 1e-4 for (b) to (g)) and on the mathematician's notes `2026-10-14-math-wu0003.md` §M1, §M2 and `2026-10-14-math-wu0003-9-q1.md`.

**Alternatives weighed and why rejected.**
- *ROADMAP WU-0003.4's rule, "10x the GPU-to-GPU maximum relative difference, rounded up to a power of 10".* Degenerate: the GPU repeat is bitwise (10 x 0). It survives as item 1 (bitwise) and says nothing about cross-device pairs.
- *The V1 1e-12 rule across devices, as item 11 was written, or a wider replacement of about 1e-9 (OF-2 (b)).* Rejected (OF-2, §26): across devices the contexts differ, so V1 is computed on different trajectories and the comparison is not like for like.
- *A part fails on max(|z_sym|, |z_away|) > 3.4 (plan amendment 2, B1 item 5; the tool as built).* Replaced by the away-arm form (OF-5). See "Dissent".
- *Pin trajectory generation to the CPU (O4 (a)).* Not decided here (O4).

**Affects.**
- `tools/compare_runs.py`: the TD failing rule (`td_statistic`, the line `res["fail"] = ... max(res["z_sym"], res["z_away"]) > TD_BOUND`, and the module docstring "TD" bullet) must change to |z_away| > 3.4, with a test, independent review and owner review before freeze. **Until that change lands the tool applies the stricter max-of-both rule.** OF-7's re-tag (`tools/compare_pilot.py` / `compare_runs.py` tag table) is a separate change.
- ROADMAP WU-0003.4 (line 176) and its definition of done (line 187) do not match what was done: no "one core cell" (O8 widened it to the pilot), no differences table for w*, eps_s, delta, nu, Lambda-bar, N in the row's form, and `tests/gpu/test_reproducibility.py` does not exist. The compare_runs reports stand in. The row text is the owner's edit (or the owner requires the gpu test).
- ROADMAP WU-0003.6 (lines 178, 189): this entry is one of its two decision entries.
- WU-0016.3 (cross-host comparisons, CSQ2), WU-0004.1 (freeze checklist), LPC.PC.18.
- Not decided here: O3 (`--xla_gpu_deterministic_ops`), O4 (confirmatory device).

**Dissent and resolution (REPRO.8).** The applied-mathematician recommended the away arms and called them "not a loosening" on the sum (P0/P1: sum z^2 11.99 against 12.65; note §M1.4). Plan amendment 2 (B1 item 5) recorded that the away form alone gives a lower z on 7 of the 18 P0/P1 parts (Chua H3c 1.02 against 1.34), so, per part, away-only is looser than the as-built max-of-both rule. The owner ruled for the away form (§33, OF-5). Every rehearsal pair passes under both forms, so no rehearsal outcome changes.

**Status:** owner ruling 2026-10-18 (question tool); the ledger `ruling` entry is the owner's. Needs owner review before freeze (tolerance and verdict-comparison code).
```

---

## 2. Draft decision entry: confirmatory sample size (WU-0003.6, from WU-0003.3 and .5)

```
## DEC-nnnn: WU-0003.6: the confirmatory sample size stays the full preset  (2026-10-18, human owner; ruling given through the question tool, recorded in the amendments note §33; text drafted by claude-opus-5-5 (planner))

**Decision.** The confirmatory run uses the full preset as in v3 §4 and `lpcstudy/config.py` `FULL`: construction 2000, calibration 1000, test 1000 and sweep cells 1000 states; M = 200 oracle draws and 4 evaluation draws per state; V4 at M = 50, 200, 800 on 100 states; B = 2000 bootstrap resamples. No size changes.

**These are development runs, not hypothesis-test results.** Every number below comes from DEV-1 and DEV-2. None is a verdict of the study, and none was used to choose a criterion.

**Rehearsal evidence.**
- **H3a.** At full size a pass is reachable only on Chua (R5: Holm p 0.00397; R6: same pattern). On Lorenz-63 and Rossler the full preset cannot deliver an H3a pass at these realizations. The R1 pilot projection reached it on no system (K_pilot 6, 4, 5).
- **H2e.** R6 half-widths 0.0207 (Lorenz-63), 0.0218 (Rossler, rho 0.01), 0.0241 and 0.0244 (Chua): all narrower than v3 §7's projected 0.04 (a precision gain).
- **v3 §7 precision statements.** On R6, reading (i) fires on 10 of 18 parts and reading (ii) on 10 of 18. R5 against the R1 projection: 4 reading-(ii) triggers over 69 parts (about 0.47 predicted). R6 pre-registered predictions: 11 of 12 within (outside: Lorenz-63 Q-N oracle logit, 0.0210, 0.525 of v3's 0.04, where "undetermined" was predicted). The pilot size does not support the same statements; the full preset is not oversized.
- **V4 at full size** (bar 0.05): R5 0.0263, 0.0424, 0.0299; R6 0.0290, 0.0350, 0.0230. All pass.
- **Finite-M bias.** D5 "not determined" on all three systems (R5), so budget row 1 stays "not below 10%" (PF-5). Raising M is not a lever: no admissible M (at most 399, H-M1/H-M2) brings F1 below 0.1 hw_full; that would need M of about 5,700 to 29,000 (note `2026-10-14-math-wu0003.md` §M5.1).
- **Compute against LPC.PC.22** (budget: the full preset completes within 12 h on the owner's GPU workstation). R5, GPU: 2739 s (0.76 h). R6, CPU at `LPC_THREADS=8`: 17031 s (4.73 h), peak RSS 4.75 GB; above the A1 planning bound of 4 h, below 12 h; not a clean C6 figure (other lanes may have shared the CPU). Both are within budget, so no optimization is warranted (RSRC.4).
- **Device (input to O4, not decided here).** For the same seed, the device changes the context and therefore the realization: DEV-2 Chua V6 fails on the GPU context (2.405e-3) and passes on the CPU context (3.3e-4). GPU repeats are bitwise on this host (R1/R2); a CPU sealed run would take about 4.7 h (R6, not clean) and regenerates bitwise on CPU.

**Alternatives weighed and why rejected.**
- *Pilot size.* Rejected: the projections from R1 reach fewer decisions (H3a on no system), and reading (ii) shows the pilot does not support v3 §7's statements.
- *Larger n.* Not chosen; no recommendation was made. Its effect on H3a for Lorenz-63 and Rossler is not measured, and it lengthens the CPU run.
- *Larger M.* Rejected on the M5.1 evidence above (no admissible M reaches the 10% rule).

**Affects:** WU-0003.6 (ROADMAP lines 178, 189), WU-0004.1 (freeze checklist), the pre-registration text. v3 §4 is unchanged. Whether v3 §7's precision paragraph is updated with the rehearsal figures is a separate owner edit, not decided here. O4 (the confirmatory device, plan amendment 1 A12) stays open.

**Dissent and resolution (REPRO.8).** None recorded.

**Status:** owner ruling 2026-10-18 (question tool); the ledger `ruling` entry is the owner's.
```

---

## 3. Draft correction: OF-4 (the F1 "worst case" wording), for WU-0008 M3 and DEC-0024 point 2

Records are append-only (PRIME.5), so the corrections below are an addendum to DEC-0024 and an appended correction block in the WU-0008 Log, not edits in place. The quoted text is left as written.

### 3.1 The wording to correct (quoted)

- `docs/agent/records/work/WU-0008-report-budget.md`, M3, line 310: "Indicative worst case, assuming draw noise independent across the k = 3 horizons and SD s_med at each: **F1 = (3/√π)·h/z₀.₉₇₅ = 0.86362·h**".
- Same file, lines 313–315: "The Rössler fail survives: 0.211 − 0.034 = 0.177 > 0.1." / "**The Chua pilot fail does not survive the worst case:** 0.1135 − 0.027 = 0.087." / Cell: "not estimated: finite-M bias upward (toward fail); indicative worst case ≤ F1 (independent draw noise across horizons; V4 at H_ref only)".
- Same file, line 216 (design table, row 1, H2a(i) column): "bias upward; indicative bound F1". Line 868 (review round, developer deviation 3): "States with L = 2 make k = 3 the worst case, so F1 stays an upper indication."
- `docs/agent/records/decisions.md`, DEC-0024 point 2, line 370: "The mathematician's indicative worst-case bound for the finite-M (oracle draws) bias in the H2a(i) median range is 0.86 of the V4 median half-width, i.e. 43 to 86% of the interval half-width on the DEV-0 pilot: the Chua pilot's fail does not survive it (a pass is not certified either). ... it bears on how many oracle draws M the full preset needs".
- **Code (prints the old wording into every RESULTS.md):** `lpcstudy/budget.py` line 565 docstring "F1 of M3: indicative worst-case upward bias of the H2a(i) median range from finite M", line 570 "Independent draw noise across the horizons is the worst case.", and line 702, the H2a(i) cell: `f"; indicative worst case ≤ F1 = {...} (independent draw noise across {k} horizons; V4 at H_ref only)"`. The RESULTS.md of R1, R2, R3, R5 and R6 carry this text.

### 3.2 Draft addendum to DEC-0024

```
## DEC-0024 addendum A3: OF-4: F1 is an indicative value, not a worst case for the median  (2026-10-18, human owner; ruling given through the question tool, recorded in the amendments note §33; text drafted by claude-opus-5-5 (planner) from the applied-mathematician's note `docs/agent/notes/2026-10-14-math-wu0003.md` §M5)

Amends point 2 of DEC-0024 and the F1 wording of WU-0008 M3 (design 28dfbd1). The earlier text is left as written.

**Correction.** F1 = (3/sqrt(pi))·h/z_0.975 is the expected range of a state whose true range is zero, with draw noise independent across the 3 horizons. It is **indicative (the bias of a zero-range state); it is not a bound on the bias of the median range.** When more than half of the eligible states have exact separation, the median of the noisy ranges lies near an upper quantile of the noise-only range, above its mean. A synthetic case (60% separated, independent noise across horizons, M = 200; `m5_d5sim.log`, seed 20261016) reaches **1.38·F1**; with noise correlation 0.5 it is 1.01·F1, with 0.9 it is 0.48·F1. The direction stands: upward, toward a fail.

**Point 2, replacement text.** "The Chua pilot H2a(i) fail is not certified against the finite-M bias. The indicative F1 for the H2a(i) median range is 0.86 of the V4 median half-width, i.e. 43 to 86% of the interval half-width on the DEV-0 pilot; a bias of that size already moves the Chua pilot's range below the 0.1 bound (0.1135 − 0.027 = 0.087), and F1 does not bound the bias, which can be larger (1.38·F1 in a synthetic case). A pass is not certified either. This is a development-run observation (DEV-0, not a hypothesis test). The number of oracle draws is not a remedy: F1/hw_full is 0.54 to 1.20 at M = 200 (0.38 to 0.85 at M = 399, the largest admissible M by H-M1/H-M2), and bringing F1 below 10% of the half-width would need M of about 5,700 to 29,000. Only a small measured bias (the D5 estimator of WU-0003) can show the row below 10%."

**WU-0008 M3, replacement wording** (appended to the WU-0008 Log as a dated correction):
- line 310: "Indicative value (the bias of a zero-range state; not a bound on the median), assuming draw noise independent across the k = 3 horizons and SD s_med at each: F1 = (3/√π)·h/z₀.₉₇₅ = 0.86362·h. Use 2/√π if k = 2."
- line 313: "The Rössler fail survives a bias of size F1 (0.211 − 0.034 = 0.177 > 0.1); F1 is not a bound, so this is an indication, not a certificate."
- line 314: "The Chua pilot fail is not certified against the finite-M bias: a bias of size F1 already gives 0.1135 − 0.027 = 0.087, and the true bias can exceed F1."
- line 315, the cell: "not estimated: finite-M bias upward (toward fail); indicative F1 = … (bias of a zero-range state, independent draw noise across horizons; not a bound on the median; V4 at H_ref only)".
- line 216, row 1, H2a(i): "bias upward; indicative F1 (not a bound)".
- line 868 (a review record; left as written): its "upper indication" is superseded by this addendum.

**Code consequence.** `lpcstudy/budget.py` prints the old wording into RESULTS.md. The docstring of `oracle_range_bound` (lines 565, 570) and the cell string at line 702 change to the wording above: a report-text change, no number changes. Radius from `/test-impact` (at least `tests/unit/test_budget.py`); needs owner review before freeze. Until it lands, every RESULTS.md, including a sealed run's, prints "indicative worst case ≤ F1".

**Affects:** WU-0008 (M3, row 1), DEC-0024 point 2 (still open per DEC-0026), `lpcstudy/budget.py`. **Status:** owner ruling 2026-10-18; the ledger entry is the owner's.
```

### 3.3 Does any criterion depend on the old wording? (checked, not assumed)

- **WU-0008 criteria: no.** Row 1's flag is "not estimated, never compared as a size" (M3 "Flag"; M1 (a)); the strict 10% flag (M9, test B3) is never computed from F1. B5 tests the F1 formula only (`test_budget.py`, 1e-15 relative), which does not change. `test_oracle_cell_shows_f1_and_f2_with_three_digits` asserts only the substring `F1 = <value>`, which the replacement keeps. No test, golden file or tool asserts "worst case" or "≤ F1" (grep of `tests/`, `tools/`, `docs/study/`).
- **WU-0003 criteria: no.** The rehearsal tools do not print F1. D5 has its own three-way reading against 0.1·hw_full (B1 7.D5, E4), and PF-5 treats "not determined" as "not below 10%". The OF-4 row of plan amendment 2 says "the rehearsal report uses the corrected wording", which holds vacuously. Plan amendment 1 (line 116) calls F1 "the worst case" in explanatory text, not in a criterion.
- **A printed claim does depend on it.** The H2a(i) budget cell in the generated RESULTS.md states "indicative worst case ≤ F1". It is not a criterion, but it is a claim in the confirmatory report, so the code change above is needed before the freeze.
- **DEC-0024 point 2's conclusion keeps its direction** (the Chua pilot fail is not certified) but loses its basis as written ("does not survive the worst case"). Its clause "bears on how many oracle draws M the full preset needs" is superseded by the M5.1 figures (M is not a lever).

---

## 4. Draft plan amendment (Q6): the B2 d1 fixtures

To be inserted by the main session or owner in `docs/agent/records/work/WU-0003-dev-rehearsal.md` after plan amendment 10 and before `## Log`. If another amendment 11 lands first, renumber.

```
### Plan amendment 11 (2026-10-18, planner claude-opus-5-5)

**Basis:**
- the owner's ruling of 2026-10-18 on Q6 and F4, "keep both as built; Q6 recorded as a dated plan amendment" (amendments note §33, develop `b554041`);
- plan amendment 3 C2 and C6 (Q6);
- the WU-0003.9 Log, fix round 1, "Record of the d1 change": the main-session instruction (task message of 2026-10-14, which also said not to copy large results into tests);
- review R10 (`WU-0003.9-review.md`) and its round-2 confirmation (`WU-0003.9-review-round2.md`).

Earlier amendments stay in force except where an item below says otherwise. No threshold, tolerance or criterion changes. This amendment records a decision on a test fixture made during WU-0003.9 (2026-10-14), after the fact but before it decided any rehearsal outcome.

| # | Decision | Relation | Strictness |
| --- | --- | --- | --- |
| K1 | **B2 d1 is met on synthetic result trees plus the real-schema extract** (`tests/unit/fixtures/real_schema_extract.json`, about 10 KB, from the WU-0002.14 S3 smoke `results.json`: the lorenz63 `handling` subtree with its LM kinds, the top-level `handling` block, the `clip_sensitivity` block), **not on the 164 KB S3-pair fixtures.** The tier truth table (each of the six TD triggers alone gives TD, both `start_state` parts; W or U alone gives T2; a weight digest alone gives T3; all equal on another device gives T1; same host, device and threads gives T0; a missing selecting leaf on either side gives exit 2; precedence TD > T2 > T3 > T1) is exact on the synthetic trees. Scope, LM kinds, verdict strings and sum-over-systems run on the extract. Authorized by the main session on 2026-10-14; ruled by the owner on 2026-10-18 (Q6 closed). | Replaces "fixtures built from the WU-0002.14 S3 smoke pair (164 KB each, copied to `tests/unit/fixtures/`)" in B2 d1; confirms C2. | At least as discriminating for tier selection (note `2026-10-14-math-wu0003-9-q1.md` §Q5, reading 12). The S3 pair predates .7a and lacks the selecting leaves, so every unedited pair from it is "tier undetermined" by B1 item 1. |
| K2 | **Record of d3 as built (information).** C2 says "d3 runs on the unedited S3 pair". As built, the unedited pair gives exit 2 (no .7a selecting leaves). The d3 declarations (1e-5 for class (a), largest rel 2.94e-7; 1e-4 for (b) to (g)) were shown once on scratch copies of the real pair with injected digests (Log, WU-0003.9 evidence run). The committed test is a synthetic pair shaped like the kernel pair, citing `m2_floors.log`. d4 runs on the committed P0/P1 extract (`td_p0p1_parts.json`), as C2 says. | Corrects C2's description of d3. | No test changes. Whether the owner's "as built" covers d3 as well as d1 is the owner's to confirm. |

**Affected checks:** none (documentation only). **Owner checkpoint:** `tools/compare_runs.py` still needs owner review before freeze (tolerance and verdict-comparison code; CSQ2 use in WU-0016).
```

---

## 5. Limitations the report must state for the DEV runs

The rehearsal runs (R0 to R6 on DEV-0, DEV-1 and DEV-2) are development runs, not hypothesis tests. The report must state the following limitations.

- **Slow weak dependence.** Block length 5 absorbs the short-range dependence measured on Lorenz-63 (V*(5)/V*(1) x1.077). Dependence beyond 5 states (pooled V*(20)/V*(5) x1.041, upper 1.090) cannot be resolved at n ≤ 1000. Lorenz-63 H1a at rho = 1% has the largest acf(1) in both runs (selection-adjusted p 0.018 in R5).
- **One realization per system and seed.** Every interval is conditional on one trajectory, library, noise and network realization, and H3c on the fitted A4 and A5. Everything said about dependence beyond 5 states rests on one realization per run.
- **The gate depends on the device.** GPU and CPU build different contexts, so for the same seed they are different realizations. DEV-2 Chua V6 fails on the GPU (2.405e-3 against 1e-3) and passes on the CPU (3.3e-4), and 52 verdict-type leaves differ between R5 and R6 although the TD statistic passes.
- **V6 Chua gate risk (DEF-0026).** About 4.6% per fresh seed for Chua (4.3% under the GPU law), 4.8% for any system. Combined V4 or V6 failure is about 11 to 25% per seed at full size. A failure in the sealed run is a hard stop referred to the owner, never retuned, with no pre-seal response rule.
- **LM sensitivity (O5, DEF-0027).** The PLP estimator is the fixed 15-iteration Levenberg-Marquardt by design. On the DEV-0 doubling study (15 against 30 iterations, B = 500, one realization), the LM row is flagged on 5 of 18 primary parts (rule R after DEF-0028: N 5, X 6, U 7). The flag is reported per part and not corrected (owner ruling "report and flag only").
