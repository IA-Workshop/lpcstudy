# WU-0014: v3 export and concordance

| Field | Value |
| --- | --- |
| Status | in progress (WU-0014.1 and .2 done; .3 waits on the owner's rulings) |
| Class | CSQ3 development |
| Agent(s) | claude-sonnet-5-5 (main session); concordance by claude-opus-5-5 (planner), under governance ledger entry 5 (authorizations 4, 6) |
| Estimate | 3 sub-tasks (S, M, S) |

## Plan (written before execution)

- **Scope:** ROADMAP.md §2 phase A, WU-0014.1 to .3. In: the v3 export record, the concordance of v3 against Methods v2, the decision log and the code, and the disposition of each discrepancy. Out: any change to a criterion, decision rule or tolerance (agents do not change criteria, `.claude/rules/study-docs.md`, LPC.AI.12), and any code change (those go to WU-0002.k).
- **Definition of done and acceptance criteria** (copied verbatim from ROADMAP.md §2, fixed before execution, VV.3):

| Id | Definition of done | Acceptance criteria (checkable) |
| --- | --- | --- |
| WU-0014.1 | File present with SHA-256 recorded in the WU-0014 log | `sha256sum docs/study/proposal_and_methods_v3.md` recorded; the document states the v3 identifiers of the decision log and experiments E0 to E6. Owner-only: agents have no web access to the Claude Doc. |
| WU-0014.2 | Concordance covers 14 hypothesis rows (H1a–H1d, Q-N, H2a–H2e, gain bound, H3a–H3c), 7 experiments (E0–E6), rules A0–A5, A4o, A* | Every row names the v2 id, the v3 id, the Methods v2 section, and the function in `lpcstudy/analysis.py` or `lpcstudy/experiments.py` that computes it, or "to add in WU-0002.k". The shift experiment appears as "dropped in v3". |
| WU-0014.3 | No open discrepancy without a WU item or a referral | List of discrepancies with their disposition; referrals use the LPC.AI.13 form. |

- **Affected checks:** none (documents only; no code, no tests).
- **Owner checkpoints (LPC.PC.11):** the referral below, and the rulings it asks for, before WU-0002.8 and .9 are planned.

## Log

### 2026-10-10, claude-sonnet-5-5 (main session)

- **WU-0014.1 done** (owner act, recorded in the WU-0009 log): `docs/study/proposal_and_methods_v3.md`, SHA-256 `6fb99e8eeaac437ba1e561e01bd88f26fc86f836173460c7f2a0f8899fabad2b`, recomputed by the planner and by the main session.
- **WU-0014.2 done** by the planner (claude-opus-5-5): `docs/agent/notes/2026-10-10-v3-concordance.md`. 14 hypothesis rows, 7 experiments plus the shift experiment marked dropped, 8 rules (A0–A5, A4o, A*) plus A4f marked removed. The note's own check: the v3 hash matches. The planner wrote the note outside its usual files because ROADMAP WU-0014.2 assigns the task to it.
- **Main-session spot check of the two most consequential findings, against the source files:** v3 line 100 defines H3b (importances in a weight tree and a horizon tree), so the ROADMAP's WU-0002.8 check "no `H3b` key exists anywhere in results" cannot pass on a v3-conformant implementation (D-23). v3 states H2a(i) as "interval below 0.1" (strict), against WU-0002.9's premise that no document fixes the boundary convention (D-22). I did not check the other 25 rows.
- **WU-0014.3 open.** 27 discrepancies: 18 code items (all mapped to WU-0002.1 to .11), 3 plan gaps (D-19 to D-21, proposed for WU-0002.4 and .8), 6 document discrepancies in five referral items (D-22 to D-27), 1 resolved (the shift experiment). The referral is below. Until the owner rules, the parts of WU-0002.8 and .9 that depend on items 1 to 3 are not planned; the rest of WU-0002 is not blocked.
- **Supersedes** the owner decision the ROADMAP queued "before WU-0002.9" (boundary convention, my earlier message to the owner): referral item 1 replaces it, because v3 §2 fixes the operator per criterion.

### 2026-10-10, planner (claude-opus-5-5): fix round 1 (review R1-R7)

- **Changed in the note** (`docs/agent/notes/2026-10-10-v3-concordance.md`):
  - D-14: adds H1b (R1);
  - D-22: adds H1a as "v3 silent" (R2);
  - D-26: adds the K-rule wording and corrects the state-spacing bullet (R3);
  - new row D-28 (gap): V7 acceptance (R4);
  - D-25: adds (h) and (i), and says the 22–36% is a pilot figure (R5).

  The referral now has a corrected "State left in" line, effect, risk and cost for each option, and a reworded option 2 (R6, R7). Counts: 18 code, 4 gap, 6 ref, 1 resolved. The note's §2 "Revisions" list records each change.
- **Disputed in part:** R5(h)'s "not tied to a stated library". The Levina–Bickel reference uses the 2×10⁴ library-segment states that M2 §M5 states, and the oracles are cached per system, independent of ρ and N_lib (`pipeline.Study.state_oracles`). The missing interval is kept as D-25(h).
- **Referral:** the `## Referral` block below is replaced with the revised §3 block of the note. The two copies are identical.
- **Not done in this round:** no tests run (documents only), and nothing committed.

## Review

- **Reviewer:** `reviewer`, claude-opus-5-5, fresh context, 2026-10-10. Scope: WU-0014.2 note (`docs/agent/notes/2026-10-10-v3-concordance.md`) and this unit file, at commit aa4c6c0 on `wu/0014-2-concordance`. No tests were run (documents only). Sources read: v3 (all), M2 §M7, §M9–§M11, the DL and its correction, ROADMAP WU-0002.1–.13 and WU-0014, `analysis.py`, `allocation.py`, `pipeline.py`, `experiments.py`, `config.py`, `report.py`, and the function names in `validation.py` and `oracle.py`.
- **Coverage (acceptance WU-0014.2): met.** There are 14 hypothesis rows, and each gives the v3 id, the v2 id (the code key), the M2 section and the function, or "to add in WU-0002.k" (H2e → WU-0002.7). There are 7 experiment rows, with v2 E5 (shift) marked "dropped in v3"; the E5/E6 versus M2 E6/E7 renumbering is correct. Rules A0–A5, A4o and A\* are covered. The rule rows cite `pipeline`/`allocation` functions instead of `analysis`/`experiments`, which the note states explicitly, and they cite M2 §M7 once for all rules. Every cited function exists.
- **Branch scope:** `git diff --name-only c350b4b...HEAD` lists only the note and this unit file. The working tree is clean. The commit names the unit and has the `Agent:` trailer.
- **Spot-check of discrepancies against source (24 of 27 in detail; D-09 (`analysis.py:662-669`) and D-15 (`config.py:135`) were also seen and agree; D-06 was not checked):**
  - Confirmed:
    - D-01 (`analysis.py:108,110`, mean);
    - D-02 (`:155`);
    - D-03 (`:226-227`, N̂ in `pass`, no interval);
    - D-04 (`:25`, `:332-334`);
    - D-05 (`:444-456`, including `med[-1] < 0.95`);
    - D-07 (`:514-520`);
    - D-08 (`:654-660`);
    - D-10 (`:690-691`);
    - D-11 (`allocation.py:437`, `pipeline.py:488`, `experiments.py:269`);
    - D-12 (`allocation.py:395`, clipped `oracle_weight`);
    - D-13 (`pipeline.py:339-346`, `config.py:148`, `regime_max_primary = 5`, falls back to `max(admissible)` = 5);
    - D-16 (`analysis.py:5`);
    - D-17 (`experiments.py:326`);
    - D-18 (`:190-191`, `:367-368`, `:656`);
    - D-19 (`:119-122`; M2:376 "floor f reported"; ROADMAP:88, 112 silent);
    - D-20 (M2:383; `h2c_state_dependence` has no A4o − A2);
    - D-21 (a) `:562`, (b) `:551` centered at one column, (c) M2:386;
    - D-23 (ROADMAP:116 against v3:100 and DL:92);
    - D-24 (v3:322 against v3:99-100);
    - D-25(a): the clip is at `:372` and `:281`, and "22–36% of states had w\* = 0" is in v3 §8, line 376, as cited. It is a pilot figure at 1 LT; the note's present tense should say "in the pilot";
    - D-25(b) (`:362-366`; M2:277 fixes only the 0.5 σ_x threshold, not the per-(state, horizon) rule or the ≥ 2 horizons rule);
    - D-25(c)–(g) (`:294`, `allocation.py:357`, `analysis.py:678`, `:646`, `pipeline.py:166-168`);
    - D-27 (ROADMAP:85).
  - Imprecise: D-14 (see R1), D-22 (see R2), and D-26 on state spacing. M2's 5·min(τ_ac, 1 LT) can fall below v3's "at least 1 LT", so this is a possible conflict, not silence. The code enforces both (`data.py:245`, `max(..., theiler)`), so it does no harm.
  - Not confirmed: none.
- **WU-0002.k mapping:** every cited sub-task (.1–.11) exists in ROADMAP §2 and covers what the note says, except as noted in R1 and R4.
- **Findings:**
  - **R1 (medium), note D-14, line 102.** The list of `pass` flags computed from a point estimate (H1a, H1c, H1d, H2d, H3c) omits **H1b**: `h1c_seed_amplifier` sets `pass = 0.8 <= est <= 1.2` at `analysis.py:153`, and the PLP-only `pass` at `:155` inherits it. The ROADMAP WU-0002.4 acceptance (ROADMAP:112, "CP slope 1.6, PLP slope 1.0 giving pass") also tests a point slope. So the H1b verdict could stay on a point estimate after WU-0002.4 and .9, against v3 §7 (every criterion is decided by an interval). *Fix:* add H1b to D-14, and state that the WU-0002.9 plan must decide H1b from `ci` of the PLP slope.
  - **R2 (medium), note D-22, line 110, and referral item 1.** The operator lists are presented as complete, but they omit **H1a**. v3:79 gives "interval of 1/d within ±25% of the independently estimated 1/d", which does not say whether the band is open or closed (M2:376 has the same wording). The owner would rule on an incomplete list. *Fix:* add H1a, and H1a's "at both ρ" from D-26, to the items where v3 is silent, in D-22 and in referral item 1.
  - **R3 (low), missed discrepancy: K rule.** v3:289 says "calibration **error** within 5% of the best value". M2 §M7:203 and ROADMAP WU-0002.3 (line 87) say "calibration **excess** MSE within 5% of the minimum". Read as total MSE, this is a different and much looser rule. The note quotes v3 in table 1c and is silent on the difference. *Fix:* add to D-26 (v3 imprecise, M2 specific) and to referral item 5.
  - **R4 (low), missed discrepancy: V7 acceptance.** v3 V7 (line 313) has two parts: median δ/(ρν), and the median slope of ln δ on ln ρ, both in [0.9, 1.1]. M2:305 adds "at every ρ". The ROADMAP WU-0002.10 acceptance (line 118) tests only δ/(ρν) = 1 against 0.85. D-15 maps V7 to WU-0002.10 without this. The acceptance criterion is fixed (VV.3). *Fix:* record it as a ref item for the owner, or as a gap for the WU-0002.10 plan, and list it in the referral.
  - **R5 (low), missed undocumented definitions (add to D-25).**
    - (h) H1a's "independently estimated 1/d" is taken as a fixed point: the median Levina–Bickel `local_dim` of the test states of the first cell only, (ρ = 1%, N_lib = 10³) (`analysis.py:101-102`). It has no interval and is not tied to a stated library.
    - (i) H2c's "better single forecaster" is chosen from the same test-split point means it is then tested on (`analysis.py:480-481`).

    Both change secondary statistics, and no document states them.
  - **R6 (low, governance), referral form (LPC.AI.13).**
    - "State left in" says "this note uncommitted; no other file edited". Both files were committed in aa4c6c0, and this unit file was edited. It should name the commit.
    - The form asks for "effect, risk, cost" for each option. Options 1 and 2 give no risk, and option 3 gives no cost.

    *Fix:* correct the "State left in" line in both copies (note §3 and `## Referral`), and complete the option fields.
  - **R7 (low, governance), referral option 2 and the recommendation for item 4(a)–(b).** The recommendation is within agent authority: it asks the owner to rule and changes no criterion. But option 2 is framed as "the documents state what the code computes", and it recommends this for the primary H2a. That invites the owner to ratify code choices, not to choose the definition: the logit clip at [0.01, 0.99] matters because 22–36% of states had w\* = 0 at 1 LT in the pilot. *Fix:* reword option 2 as "the owner fixes the definition (the code's or an alternative), with the applied-mathematician's view, before the freeze", so the choice is made on its merits (PRIME.2).
- **Verdict: approve with fixes** (7 findings: 2 medium, 5 low). Coverage meets WU-0014.2. Of the 24 discrepancies checked, 21 are confirmed and 3 are imprecise; none is wrong. R1–R5 should be folded into the note and the referral before the owner rules on WU-0014.3. R6 and R7 are edits to the referral text.

### Re-review, 2026-10-10, `reviewer` (claude-opus-5-5), fix round 1

- **Scope:** R1 to R7 only. I read the uncommitted `git diff` of the note and of this unit file on `wu/0014-2-concordance`, and checked it against `oracle.py:67-108`, `pipeline.py:202-207` and `:251-277`, `data.py:262`, M2 §M5 line 155, and ROADMAP §0 line 13. No tests were run.
- **R1: fixed.** D-14 now lists H1b. It cites `analysis.py:153` and `:155` and ROADMAP line 112, and says that WU-0002.9 must decide H1b from the interval of the PLP slope against [0.8, 1.2].
- **R2: fixed.** D-22 and referral item 1 list H1a's "within ±25%" as "v3 silent" (v3 line 79), together with "at both ρ".
- **R3: fixed.** D-26 and referral item 5 state the K-rule wording: v3 says "calibration error", and M2 §M7 and WU-0002.3 say "calibration excess MSE".
- **R4: fixed.** D-28 (gap) states the gap in V7's slope part and per-ρ condition. The fixed WU-0002.10 acceptance is unchanged: the plan only adds tests, and ROADMAP §0 permits tightening only. D-28 is also listed in referral item 2 for the owner.
- **R5: fixed; the dispute is upheld.** The planner is right.
  - `Study.state_oracles` is keyed on (system, embed_dim, delay, split) and is "independent of noise and library" (`pipeline.py:202-207`).
  - `local_dim` takes its pool from a fixed subsample of up to 2×10⁴ of `ctx.library_states`, the library segment (`oracle.py:99-103`, `data.py:262`). This is the setting in M2 §M5 line 155.
  - So my phrases "first cell only" and "not tied to a stated library" were wrong. Only the missing interval stands.

  D-25(h) as now worded is accurate: it gives the median over the test-sweep states (the first cell is a sweep cell, `pipeline.py:276-277`), a point value, and an unchanged value. D-25(i) is accurate (`analysis.py:480-481`).
- **R6: fixed.** "State left in" now names aa4c6c0 and the uncommitted round-1 edits. All three options give effect, risk and cost, as the form in agent-instructions.md line 94 asks.
- **R7: fixed.** Option 2 and the recommendation now ask the owner to fix each definition on its merits, with the applied-mathematician's view. The code's choice is one candidate; the referral no longer asks the owner to ratify it.
- **Consistency checks:**
  - The block in note §3 and the block in `## Referral` are byte-identical (checked with `diff`).
  - The kinds in §2 are 18 code (D-01 to D-18), 4 gap (D-19 to D-21, D-28), 6 ref (D-22 to D-27) and 1 resolved. This matches the counts table.
  - The "Revisions" list is dated and appended. The earlier log entries were left as they were.
  - `git status` shows only the note and this unit file.
- **Observation, outside R1 to R7, for the main session to record as a DEF:** `oracle.py:99` draws the Levina–Bickel pool with `np.random.default_rng(0)`, not `make_rng`. This breaks the convention that randomness comes only from `make_rng`, and it fixes the pool across seed ids. D-25(h) records the call, but no WU item owns it.
- **Verdict: approve** (R1 to R7 all fixed; R5(h) dispute upheld).

## Audit

- Is the definition of done met? Not yet: WU-0014.3 needs the owner's rulings.
- Defects recorded:
- Notes for successors: WU-0002 plans cite the rulings (decisions.md entries) for D-22 to D-27.

## Referral

## Referral: five document discrepancies the v3 concordance found (agents do not change criteria)
Unit: WU-0014 (.2 -> .3)   Raised by: claude-opus-5-5   Date: 2026-10-10 (revised in fix round 1, same date)
What I was doing:  Building the v3 concordance (docs/agent/notes/2026-10-10-v3-concordance.md).
What stopped me:   .claude/rules/study-docs.md and LPC.AI.12: criteria, decision rules and
                   fixed acceptance criteria (VV.3) are the owner's to change.
Findings:          1. Boundary convention (D-22): ROADMAP WU-0002.9's premise and its
                      uniform "closed" proposal conflict with v3 §2's explicit per-criterion
                      operators (strict for H2a, H2b, H2c, H2e, H3a; closed for H1b-H1d,
                      H2d, H3c). Open: H1a's "within ±25%" band (v3 line 79, open or
                      closed not stated) and its "at both ρ" (M2 only); endpoint on the
                      fail side; the K-rule "within 5%" tie.
                   2. ROADMAP text (D-23, D-27, D-28): WU-0002.8 acceptance "no H3b key
                      exists anywhere" contradicts v3 H3b; WU-0002.1 "v3 drops E5" should
                      read "v2 E5 (shift)"; WU-0002.10 acceptance tests only the δ/(ρν)
                      part of V7, not the slope part (v3 line 313) or "at every ρ" (M2).
                   3. Verdict for non-interval criteria (D-24): v3 §7 says every criterion
                      is decided by an interval; H3a (p-values) and H3b (importances) have
                      none, and no rule covers a statistic that cannot be computed.
                   4. Undocumented code definitions (D-25 a-i), of which (a) the logit clip
                      at [0.01, 0.99] and (b) the H2a(i) eligibility rule affect the primary
                      H2a. In the pilot 22-36% of states had w* = 0 at 1 LT (v3 §8), so the
                      clip value sets the logit of those states and changes the statistic.
                   5. v3 silent or imprecise, M2 specific (D-26), including the K rule:
                      v3 "calibration error" vs M2 §M7 "calibration excess MSE".
Options:           1. Owner rules each item in decisions.md (and amends ROADMAP rows
                      WU-0002.1/.8/.9/.10 by dated amendment); WU-0002 plans cite the
                      rulings. Effect: WU-0002.8/.9 can be planned. Risk: a ruling on a
                      definition (item 4) without the mathematician's view may fix a poor
                      definition. Cost: one owner session.
                   2. Owner fixes the definitions of items 1, 3 and 4 on their merits
                      (the code's current choice is one candidate, alternatives another),
                      with the applied-mathematician's view, and records them as a dated
                      amendment to v3/M2 before the freeze. Effect: the documents define
                      what is tested. Risk: a definition differing from the code's changes
                      pilot-comparable statistics (WU-0002.12 lists them as changed).
                      Cost: an applied-mathematician pass plus a document revision.
                   3. Defer: plan WU-0002.1-.7, .10 and .11 now, hold the parts of .8/.9
                      that depend on items 1-3. Effect: no block on the rest. Risk:
                      rework if rulings touch planned code. Cost: none now; a later
                      re-plan of .8/.9.
Recommendation:    Option 1 now, with option 2 for item 4(a)-(b), because they define a
                   primary statistic: the owner chooses the logit treatment of w* = 0 and
                   the H2a(i) eligibility rule on their merits, not by ratifying the code.
                   For item 1, follow v3 §2's operators as written rather than one uniform
                   convention. For item 2, change the WU-0002.8 check to "no key for v1
                   H3b (p_eff)" and let the WU-0002.10 plan add V7 slope tests (a
                   strengthening). For item 5, confirm that the M2 detail governs where v3
                   is silent or imprecise.
To verify the outcome: each D-22..D-28 cites a decisions.md entry or a dated ROADMAP or
                   document amendment; WU-0002.8/.9/.10 plans reference them.
State left in:     branch wu/0014-2-concordance; note and unit file committed in aa4c6c0;
                   fix-round-1 edits to the note and to the unit file's ## Log and
                   ## Referral are uncommitted. No code, governance or decisions.md edited.
