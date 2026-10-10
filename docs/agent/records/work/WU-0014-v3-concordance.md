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

## Review

- **Reviewer:** not yet assigned. This unit changes documents only; the concordance should be spot-checked by a reviewer other than its author before the owner relies on it.
- **Findings and resolution:**

## Audit

- Is the definition of done met? Not yet: WU-0014.3 needs the owner's rulings.
- Defects recorded:
- Notes for successors: WU-0002 plans cite the rulings (decisions.md entries) for D-22 to D-27.

## Referral

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
