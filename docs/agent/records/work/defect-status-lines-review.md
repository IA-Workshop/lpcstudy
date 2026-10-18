# Independent review: defect-register status lines (freeze-blocker C7)

Branch `wu/defect-status-lines`, tip e916249, base develop e10f65e. Change: 11 appended lines in `docs/agent/records/defects.md` (lines 255-265: DEF-0001, 0002, 0003, 0004, 0005, 0006, 0010, 0020, 0021, 0022, 0027).

## Review

- **Reviewer:** `reviewer`, model claude-opus-5-5, fresh context, 2026-10-18.
- **Method:** read-only git and grep only. No tests were run (records-only change; there is no test radius). No web access. No sealed seed was read.
- **Append-only check (item 3): pass.** `git diff --numstat e10f65e HEAD` gives `11 0 docs/agent/records/defects.md`. No existing line is edited or deleted, and no `Blocking:` field is changed.
- **Cited commits:** all 27 cited hashes exist and are ancestors of HEAD. Each merge subject matches its claim: bd83b51, 1db8a85, b0c939c, 91b8492, 85531db, 4aa16a5, 55ddccd, 1b20db9, ff26883, 181ee75, 3d27006, 91c31f7, f039310, 1ed9e2d, 7bb2744, 92562ec, 076b856, c2cc9f2, ca59cc3, 6dfd8db, 1d90153, 089e278, 8521b44, 1e3d726, db82ac5, f14c8fa and f3d5d72.
- **Cited tests:** all 20 named tests exist in the files the lines name. `sklearn_seed` is called at the four `random_state=` sites, `allocation.py:472` and `analysis.py:782`, `:1973` and `:1975`. The test `test_every_random_state_keyword_is_a_sklearn_seed_call` is an AST scan with `sites >= 4`.
- **Cited records:** these match their claims:
  - `GATE-2026-10-18b-develop.md`: green at ff26883, unit 1850, integration 19 at bec632c.
  - `pilot_results_v3_dev0_reference.json`: carries `lpcstudy.handling/2` with cells, oracles, fitting, result_counts and totals; `lpcstudy.provenance/2` with the listed fields; H1d `rows.*.interval`; H3c `level` 0.98333 and `n_failed_resamples`.
  - `WU-0001-seed-provenance.md` `## Audit`: gate 207, approve after one round.
  - `WU-0002-methods-v2-changes.md` `## Audit`: covers WU-0002.1/.2.
  - The `WU-0002.6-qn-h2a.md` Log has the DEV-3 smoke, the reviewer's own `sklearn_seed` derivation and the 3307 leaves.
  - `WU-0002.3-excess-mse.md` review: approve with fixes, record fixes only.
  - `dev_regression_dev0_vs_local_v1.md`: rows D-11 (DEF-0002, A\* regret 0.0), D-13 (DEF-0003, `chua/fitted/chosen_K` 5 to 4).
  - v3 line 363: quoted correctly.
- **Owner answers (amendments note §§29-36):**
  - The DEF-0020 quote is verbatim §35 B6a.
  - The DEF-0021 claim matches §36 B9 ("N2/N3 keep the code's reading").
  - The DEF-0027 claims match §29 O5, §30 and §35 B7.
  - The DEF-0022 claims about §33 (sample size, OF-G3) are accurate as citations; see R3 for what they do not cover.
- **DEC-0028 to DEC-0032:** no line cites them as existing. `decisions.md` ends at DEC-0027. DEF-0020 and DEF-0027 call DEC-0032 and DEC-0030 "draft" and "not yet in `decisions.md`" (see R6).

### Findings

**R1 (medium): DEF-0001, line 255.** "resolved" is too strong, the scan claim is inaccurate, and the "Residue, exactly" list is incomplete.

- *Evidence.*
  1. The defect's resolution is "WU-0002, item 11". The unit `WU-0002.11-counters.md` still has header Status `planned`, and its `## Audit` is the empty template (lines 876-880). The parent `WU-0002-methods-v2-changes.md` has no audit of item 11. The independent confirmation (`/audit freeze`, WU-0004.4) has not started. The line admits this, but it opens with a bold "**resolved ...**", and the only safeguard is a request that the freeze checklist "should read" it otherwise. The checklist's grep (`grep -n -A2 "Blocking:\*\* yes"`) never reads status lines, so that request cannot work through the tool.
  2. The line says the grep for `nan_to_num`, `1e-300`, `np.clip`, `np.maximum`, `errstate`, `nanquantile` and broad `except` "finds no site outside the inventory". That is false. `lpcstudy/clip_sensitivity.py:408-409` (`np.maximum(sq_plp, 1e-12)` and `np.maximum(sq_plp_2, 1e-12)` in `h1b_part`) matches the pattern and is not a row of the WU-0002.11 inventory: the module postdates 8fbfa6b. It is not counted (the H1b counterpart is inventory N4, counted as `n_floored`), and the WU-0002.11e grep (unit file line 389) did not include `maximum`. The broad `except`s in the same module (lines 570, 579, 619) are recorded and logged, so they are visible, but they are not inventory rows either. The scan also used a narrower pattern than the plan's V4 criterion, which also includes `isfinite`, `nanmedian`, `nanmean`, `np.minimum(`, `1e-12`, `1e300`, `1e6`, `try:`, `warnings`, `fallback`, `default_rng` and `jnp.where`. So it is not the V4 check.
  3. The residue list omits two items:
     - DEF-0019, which the line lists as "fixed", is "awaiting owner confirmation" (line 170). It is not resolved, although the sentence frames every moved row as going to "a named defect that is resolved".
     - DEF-0025's open follow-up: `Study.skipped_variants` is in `run.log` only, not in `results.json` (line 222). DEF-0001's own description asks for per-run counts in `results.json`. No configured preset reaches it.
  4. The "31 counter names" count cannot be reproduced, because the line does not list the names. I checked 36 names: the 27 `handling.totals` keys of the reference, `empty_regime_fallback_by_K`, `failed_variants` and the seven .11b result keys. All 36 occur in `lpcstudy/` and in `tests/unit/`, so the substance holds.
- *Why it matters.* DEF-0001 is `Blocking: yes`, and its status is what the freeze item "all blocking defects resolved" reads. The register is append-only, so a "resolved" that later needs qualifying has to be superseded in public.
- *Required fix.* Append a superseding DEF-0001 line, not an edit. Honest wording: "**fixed in code; open pending confirmation** (not resolved)". It should:
  - list the lanes and units that did the fix (.11a, .11b, .11c, .11e, WU-0005.4, WU-0002.14 and WU-0012.6, each reviewed and merged);
  - state the residues exactly:
    - (a) independent confirmation by `/audit freeze`, and the WU-0002.11 `## Audit` filled;
    - (b) the uncounted 1e-12 floor at `clip_sensitivity.py:408-409`, to be counted or justified (J, with a docstring sentence) by a unit;
    - (c) DEF-0019 owner confirmation;
    - (d) `skipped_variants` not yet in `results.json` (DEF-0025 follow-up);
    - (e) owner code review (B2);
  - correct the scan statement: name the pattern actually used, say it is narrower than V4, and name the `clip_sensitivity.py` hits;
  - list the counter names checked, or drop the count.

**R2 (medium): DEF-0027, line 265.** The per-system X counts are stale and contradict the line's own totals.

- *Evidence.* The line says "N 5 / X 6 / U 7" (after DEF-0028) and also says the 2026-10-14 correction "(Lorenz-63 has 4 X of 6, Chua 3, Rossler none) stands". DEF-0028 (line 245, line 254, merged f14c8fa) moved Chua H3c from X to U. Chua therefore has 2 X (H2a(i), H2b(i)), and 4 + 2 = 6 matches the total; 4 + 3 = 7 does not.
- *Why it matters.* This is a factual error about a reported limitation, and the sealed report's limitations text (B7) is drawn from these lines.
- *Required fix.* Append a correction line: "after DEF-0028, Lorenz-63 4 X of 6, Chua 2 X of 6 (H2a(i), H2b(i); H3c now U), Rossler none; total X 6".

**R3 (medium): DEF-0022, line 264.** "power finding accepted as a pre-registered limitation" is not backed by an owner answer, and it skips the full-size check that the defect asked for.

- *Evidence.*
  1. The cited owner answers in §33 are "sample size: keep the full preset" and "OF-G3: the margin band governs the H2a(ii) comparison". Neither accepts the power finding. DEF-0022's Blocking field says "the power finding goes to the owner", and no §29-§36 answer addresses it.
  2. DEF-0022's description requires that "at the full preset sizes it must be checked: WU-0003.3's precision report must cover it". The line does not cite the full-size evidence. The R6 report (`WU-0003-R3R6-report-R6.txt`, lines 143-152) gives the H2a(ii) margins 0.1 - hw_full as:
     - +0.0354 (Lorenz-63 zero);
     - +0.0008 (Lorenz-63 interior);
     - +0.0202 (Rossler zero);
     - +0.0215 (Chua zero);
     - -0.0306 (Chua interior).

     It also says "v3 precision not reproduced" on 5 of 6 parts. So v3 line 363's "within about 0.01 of zero" is not what the full-size evidence shows part by part, and the pre-registered sentence alone does not state the limitation correctly.
  3. The line points to "the sealed report's limitations list (`2026-10-18-owner-decision-drafts.md` section 5)". That section has no H2a(ii) or DEF-0022 item (checked: slow dependence, one realization, device, V6, LM only). "Remaining owner action: none beyond ..." therefore hides an open item.
  4. The draft rehearsal report (WU-0003.3) is not adopted (amendments note §37).
- *Required fix.* Append a superseding line:
  - "reference corrected (done, db82ac5)";
  - "power finding: full-size margins from R5/R6 cited; the limitation is not yet in the drafts' §5 list; owner acceptance and wording pending (with the WU-0003.3 report)";
  - status "open (tracked, not blocking)".

**R4 (low): DEF-0003, line 257.** The tolerance is misquoted.

- *Evidence.* The line says "tolerance 1e-6 relative as in the plan". The ROADMAP acceptance (b), the WU-0002.3 plan row (b) ("**10⁻⁶ absolute**") and the test docstring (`Tolerance abs=1e-6`) all say absolute. The relative tolerance belongs to test (a), the excess MSE.
- *Required fix.* Append a correction line: "1e-6 absolute (plan row (b)); 1e-6 relative applies to DEF-0002's test (a)".

**R5 (low): DEF-0005, line 259.** "resolved in code" carries a residue that is part of the defect.

- *Evidence.* DEF-0005 is "identifiers and criteria in code follow v1/v2, not v3" (`Blocking: yes`; it affects the report and the verdicts). The line's own residue is that v3, Methods v2 and the ROADMAP still have to be edited "to state what the code tests" (B1). So code and v3 do not yet agree. The gain-bound row is also still `GAIN_BOUND_PENDING` (`identifiers.py:18`) with no WU. The line names both, which is honest, but the lead word is "resolved".
- *Required fix.* Append a line: "fixed in code; open until the B1 document amendments (ledger `amendment` per document) are recorded and the gain-bound row is opened or ruled out". Alternatively, the owner rules explicitly that the document edits are outside DEF-0005, and a line records that ruling.

**R6 (low): DEF-0020 and DEF-0027, lines 262 and 265.** They cross-reference provisional decision numbers.

- *Evidence.* The lines cite "draft DEC-0032 item 2" and "draft DEC-0030 items 5 and 6". Both are correctly marked as drafts that are not in `decisions.md`, and the draft contents match: DEC-0032 item 2 is B6a, and DEC-0030 items 5 and 6 are O5 and DEF-0028. But `2026-10-18-ledger-batch-draft.md` line 40 says "DEC-0028 to DEC-0032 below are proposed numbers ... At entry time, take the next free number". An append-only cross-reference to a number that may be reassigned can later point to the wrong entry.
- *Required fix.* None now. When the entries are made, append one line per defect that names the final DEC numbers (or "draft D7 / D3 of the batch draft, entered as DEC-nnnn").

**R7 (low): quoted figures in lines 258 and 260.** Two figures need labels.

- *Evidence.*
  1. DEF-0004 quotes "H3c `ci` [0.327, 0.970]" with no system. That interval is Lorenz-63. Rossler is [0.850, 0.995] and Chua is [0.887, 1.490] (verdict inconclusive).
  2. DEF-0006's "42 tests" is the number of test functions in `test_provenance.py`. Three functions are parametrized (lines 199, 648 and 729), so pytest collects more.
- *Required fix.* Optional clarifying line: "H3c interval quoted is Lorenz-63; 42 test functions".

**R8 (medium; hand-back, not the diff): "no open blocking defect remains" is not supported.**

- *Evidence.*
  1. The hand-back is right that the grep matches only the field text. `.claude/skills/freeze-checklist/SKILL.md:10` runs `grep -n -A2 "Blocking:\*\* yes"`, which prints the field and the next two lines and never reaches a status line.
  2. It also never matches the entries whose field reads "to be ruled on by the owner": DEF-0014, 0015, 0017, 0020 and 0021.
  3. The defects whose field is `Blocking: yes` (lines 11, 27, 35, 42, 49, 56, 63, 86), with their latest status after this branch:

     | Defect | Latest status |
     | --- | --- |
     | DEF-0001 | **open**: "one condition open" by its own line; R1 adds residues |
     | DEF-0002 | resolved |
     | DEF-0003 | resolved |
     | DEF-0004 | resolved |
     | DEF-0005 | **open in substance**: documents and the gain-bound row (R5) |
     | DEF-0006 | resolved |
     | DEF-0007 | resolved (2026-10-10) |
     | DEF-0010 | resolved |

  4. Further pre-freeze items that the grep cannot see:
     - DEF-0019: fixed, awaiting owner confirmation; its field says "before ... the freeze".
     - DEF-0020: ruling given, no decision entry.
     - DEF-0021: ROADMAP edit owed.
     - DEF-0014: its resolution line, "resolved by owner ruling (DEC-0015)", is filed at line 143 under DEF-0016 without a defect id, so a reader of DEF-0014 sees no status.
     - DEF-0018: owner ruled B6b (§35), no status line, implementation still owed per draft DEC-0032 item 3.
     - DEF-0013: no closing line, although the fix was planned inside WU-0002.8.
     - DEF-0026 and DEF-0027: owner and B1 items before the seal.
- *Required fix.* Do not record C7 as closing the freeze item "all blocking defects resolved". Any record of C7 should list DEF-0001 and DEF-0005 as open and should list the other pre-freeze items above. Optionally, append a DEF-0014 status line that points to line 143. The freeze-checklist grep could also print the status lines (for example `grep -n "^- DEF-nnnn"`); that is a governed `.claude/` edit and the owner's to make.

**Governance note (not a finding against the lines).** The commit e916249 names freeze-blocker item "C7", not a unit id, and no unit file records the change. The `Agent:` trailer is present. Freeze-blockers note C7 assigns "planner for the evidence check", and this review stands in for it. Every unit cited as resolving a defect has an empty `## Audit` (WU-0002.3, .4-5, .6, .11, .11c, WU-0012.6). This is long-standing register practice ("resolved" on merge after independent review, as for DEF-0012 and DEF-0015), not something this branch introduced. It is relevant to C15 and the `/audit freeze`.

### Item 4: is "resolved" too strong for DEF-0001?

Yes. The honest wording is "**fixed in code; open pending confirmation**". Every inventory row reached its planned final state through reviewed, merged lanes. But the independent confirmation is missing, the WU-0002.11 audit is empty, and R1 found one uncounted floor outside the inventory plus two unlisted residues. A `Blocking: yes` entry should not carry "resolved" until the confirmation is recorded.

### Owner checkpoint

This change is records only: no verdict, statistics, seed, provenance or dependency code is touched. It does not by itself need owner review. The defects it describes do (B2).

### Verdict

**changes required**: 8 findings. R1, R2, R3 and R8 are medium; R4, R5, R6 and R7 are low. Every fix is an appended superseding line (or a hand-back correction for R8). No existing line may be edited.

# Round 2 (re-review of fix round 1)

- **Reviewer:** `reviewer`, model claude-opus-5-5, fresh context, 2026-10-18.
- **Scope:** `git diff c7431ce..e070d07 -- docs/agent/records/defects.md` (fix round 1, commit e070d07). This round covers R1 to R8 and the three status lines that were not requested (DEF-0013, DEF-0014, DEF-0018).
- **Method:** read-only git, grep and one read-only `python3 -I` look at the reference JSON. No tests were run: the change is records only, and `git diff e10f65e e070d07 -- lpcstudy/` is empty. No web access. No sealed seed was read.
- **Append-only:** pass. `git diff --numstat` gives `12 0 docs/agent/records/defects.md`, and no line starting with `-` appears in the diff. Each line that replaces an earlier one says **supersedes** or **corrects**. No `Blocking:` field changed. Commit e070d07 names the item (C7 fix round 1) and carries `Agent: claude-sonnet-5-5`.

## R1 to R8

| Finding | Result | Evidence checked |
| --- | --- | --- |
| R1 | **resolved** | The lead is "fixed in code; open pending confirmation. It is not resolved." The lanes and units match round 1's verified hashes. I checked all 36 counter names: the 27 `handling.totals` keys of the reference (read from the JSON; "error_clips and its five variants" is `_cp`, `_nonfinite`, `_nonfinite_href`, `_plp`, `_plp_href`), `empty_regime_fallback_by_K`, `failed_variants` and the seven .11b keys. Each one occurs in `lpcstudy/` and in `tests/unit/`. The inventory name `regime_count_fallback` is at `WU-0002.11-counters.md:65,95`, as the line says. Residue (a): `clip_sensitivity.py:408-409` are the two `np.maximum(..., 1e-12)` floors, and lines 570, 579 and 619 are the three `except Exception` sites. Residue (c): `experiments.py:496-499` logs `skipped_variants` and leaves it out of the returned block. Residues (b), (d) and (e) match round 1. The scan statement now names the pattern used and admits that it is narrower than V4 and that V4 was not run. One detail, not a finding: the line's list of what V4 "adds" (plan line 29) leaves out bare `clip(` and bare `except`. The conclusion "narrower" still holds. |
| R2 | **resolved** | `lm_doubling_dev0_report_v3.md` line 23 and line 89 give Lorenz-63 N1/X4/U1, Rossler N3/X0/U3 and Chua N1/X2/U3, for a total of N5/X6/U7. The table rows (lines 70-81) show Lorenz-63 X = H2a(i), H2b(i), H2b(ii), H3c; Chua X = H2a(i), H2b(i); Chua H3c = U. All of this matches the line. |
| R3 | **resolved** | The status is "open (tracked, not blocking)". The line says no owner answer accepts the power finding. The five margins match `WU-0003-R3R6-report-R6.txt` lines 143-152 exactly (+0.0354, +0.0008, +0.0202, +0.0215, -0.0306 against 0.0067..0.015), and so does "5 of 6" (line 151, "fires on 5 of 6 parts"). The line also says that §5 of the drafts lacks the item and that the report is not adopted (§37). |
| R4 | **resolved** | `test_allocation.py:165` gives `abs=1e-6` for `test_regime_weight_matches_brute_force`. `test_oracle.py:143` gives `rtol=1e-6` for `test_excess_mse_matches_grid_minimum`. |
| R5 | **resolved** | The status is "fixed in code; open for the document edits". `GAIN_BOUND_PENDING` is at `identifiers.py:18`. The closing path for an owner ruling is stated. |
| R6 | **resolved** | The provisional-number note cites ledger-batch draft line 40, which I verified, and it commits to appending the final DEC numbers. |
| R7 | **resolved** | The reference JSON gives H3c `ci`: Lorenz-63 [0.327, 0.970] pass, Rossler [0.850, 0.995] pass, Chua [0.887, 1.490] inconclusive. `test_provenance.py` has 42 `def test_` functions. |
| R8 | **resolved** | The `Blocking: yes` fields are at lines 11, 27, 35, 42, 49, 56, 63 and 86, which are DEF-0001 to DEF-0007 and DEF-0010. The "to be ruled on by the owner" fields are at lines 122, 130, 147, 174 and 182, which are DEF-0014, 0015, 0017, 0020 and 0021. The note marks DEF-0001 and DEF-0005 as open in substance and says not to record C7 as closing "all blocking defects resolved". For one omission in its list, see R9. |

## The three status lines that were not requested

- **DEF-0013: correct.** `analysis.py:1930` is `np.argsort(np.nan_to_num(horizons_km, nan=np.inf), kind="stable")`. Both the line and `test_h3a_orders_tied_and_missing_horizons_by_regime_index` (`test_analysis.py:1858`) were introduced by 1b2c6ad, an ancestor of merge f039310 ("Merge WU-0002.7/.8 ... into develop"). The test checks the order of tied and NaN medians against hand-written pairs, which is the independent reference. The WU-0002.7-8 review's round 2 verdict is "approve" (unit file line 519). The only other unstable sorts in `lpcstudy/` are `statistics.py:174` (Holm, order-invariant per the defect's own description) and `clip_sensitivity.py:284` (values only). Neither affects regime order.
- **DEF-0014: correct in substance; see R9.** The misfiled line is the last dated line under DEF-0016 (defects.md line 143). `decisions.md:243` holds DEC-0015, whose text matches the quote. The pilot-size claim matches freeze-blockers note A2 line 35 (R1, R3 and R6 pass V1-V7; R5 fails Chua V6). The DEV-0 reference JSON also has `V7.pass` true on all three systems, which is DEC-0015's WU-0002.12 condition.
- **DEF-0018: correct in substance; see R10.** a0a15c0 exists, is an ancestor of HEAD, and its subject is "Merge WU-0004d ... (DEF-0018, ruling B6b); additive, no verdict change". The B6b quote is verbatim from amendments note line 312, in §35 (heading at line 307). The keys are at `analysis.py:1913-1916` and are returned at 1961. All three tests exist: `test_analysis.py:1884` and `:1916`, and `test_report.py:1172`. Draft DEC-0032 item 3 (ledger-batch draft line 244) is B6b. The reference JSON has 0 occurrences of the two new keys, as stated.

## New findings

**R9 (low): DEF-0014 status line and the freeze-checklist note (defects.md, new lines 275 and 277).** The remaining owner action for DEF-0014 is not stated.

- *Evidence.* DEC-0015 says "recorded here pending the owner's ledger entry", and its open item is what "superseded" means. `docs/agent/governance/ledger.jsonl` has no DEC-0015 entry (0 matches). Freeze-blockers note line 94 lists the DEC-0015 `ruling` entry as owed. The new DEF-0014 line says only "the ledger `ruling` entry is the owner's". The freeze-checklist note says "DEF-0018 and DEF-0014 (now carry status lines above; DEF-0018 still needs the owner's entry)", which implies that DEF-0014 needs no entry.
- *Why it matters.* R8's purpose was a complete list of the pre-freeze items that the grep cannot see. DEF-0014's resolution rests on a ruling that is not yet in the ledger, the same state that DEF-0018 is flagged for.
- *Fix.* Append one line: "DEF-0014: remaining owner action: append the DEC-0015 `ruling` ledger entry (freeze-blockers note, item 3 of the ledger list) and, optionally, say what supersedes V7; the freeze-checklist note's list should read 'DEF-0018 and DEF-0014 still need the owner's entry'."

**R10 (low): DEF-0018 status line (defects.md, new line 276).** "R1 to R5 closed" overstates the review record.

- *Evidence.* `WU-0004d-review.md` Round 2 (line 213) gives "approve with fixes; R1, R2 and R3 are resolved", with R4 and R5 new. R4 and R5 were then fixed by the developer in da7bfb2 (unit file lines 99-113), and no third review round confirms them. The merge is allowed, because DEVELOPMENT_WORKFLOW.md line 38 permits "approve with fixes with every finding resolved". But "closed" reads as reviewer-confirmed.
- *Fix.* Append a correction: "R1 to R3 confirmed resolved by the round 2 re-review; R4 and R5 fixed by the developer in da7bfb2 under approve-with-fixes, not re-reviewed."

## Owner checkpoint

This change is records only. It does not by itself need owner review.

## Verdict (round 2)

**approve with fixes.** R1 to R8 are resolved. There are 2 new findings, R9 and R10, both low; each is fixed by one appended line. The DEF-0013 line is correct as written.
