# Brief for Claude (web): update the Claude Doc "LPC Study: Proposal and Methods (v3)"

Written 2026-10-20 by claude-sonnet-5-5 (main session) for the project owner to paste into Claude web together with the attachments listed in section 6. Handling: the attachments contain sealed-run results that are UNPROMOTED and internal to the owner and the student (Deem Albaty) until promotion. Share the Claude Doc and this conversation only with them.

## 1. What this is

The study compares an analog forecaster (CP) with a physics-based forecaster (PLP) on Lorenz-63, Rössler and Chua's circuit and tests whether four local predictability conditions decide the blend weight. The Claude Doc "LPC Study: Proposal and Methods (v3)" is a **working copy**. The governing text is the file `docs/study/proposal_and_methods_v3.md` in the repository, frozen on 2026-10-19 (freeze tag `freeze-1`), with SHA-256 `4f2ead48b77953f3c48db25bd72fefefe0a47ce2ea73d08697df644a35abe073` recorded in the ledger. The pre-registration lives in that file.

## 2. Task

Bring the Claude Doc up to date with what happened after the freeze, **without changing any pre-registered text**. All new material goes in clearly marked, dated addenda placed after Section 9 and before the References. Return (a) the updated Claude Doc and (b) a list of every change, so that the owner can approve it and export the addenda to a separate repository file.

## 3. Hard rules

1. **Do not edit Sections 1 to 8, the Summary, or the pre-registered parts of Section 9** (hypotheses, bands, levels, block length, decision rules, the post-freeze steps 1 to 4). Not even typos. List typos and inconsistencies you find in a final section "Editorial issues noticed (not changed)".
2. Every addition is headed "Addendum, post-freeze, 2026-10-20" and says that it is not part of the pre-registration.
3. **Numbers and verdict words come only from the attached files.** Never compute, round differently, or infer a number. Quote the stored verdict words (supported, not supported, inconclusive, pass, fail) exactly. "Supported" is always written "supported (preliminary, unpromoted)" until promotion. Do not write "confirmed", "proved", "significant", "demonstrates". "Inconclusive" does not mean "no effect".
4. Keep the label **PRELIMINARY: internal to the owner and the student until promotion** on every results statement.
5. Extension results (new attractors, Dysts comparisons, the development ensemble) are **exploratory, development seeds, never confirmatory**, and are never placed beside the sealed result. No overall verdict for the extension.
6. If a requested statement cannot be supported by the attachments, say so in a "Needs input" list instead of writing it.

## 4. Content of the addenda

**Addendum A: status after the freeze** (one short table plus a few sentences):
- the sealed CPU run (CONF-1, full preset, commit df8928f, 15555 s) is complete; the GPU cross-check is complete; the regeneration of the CPU run at the same commit by the owner is under way (WU-0016), with the result to be added;
- the three primary hypotheses' overall verdict words and the per-system words, from the preliminary findings document, section 4 (copy the stored words; do not interpret beyond that document's own sentences);
- the cross-check summary from section 8 of that document: the 18 primary parts agree statistically (largest z 2.21 against the bound 3.4); 44 stored verdict words differ between the CPU and GPU runs, and the CPU verdicts stand (DEC-0031);
- post-freeze rulings that touch the design text, quoted from `docs/agent/records/decisions.md`: DEC-0033 (M2: bitwise agreement at the official size is extrapolated from smoke size; M3: the gain-bound screen is reported only), DEC-0035 (the owner may be the regenerating actor, v3 section 9 item 4), DEC-0036 (Q-N is shown with both readings; the DEF-0027 count follows RESULTS.md and the v3 section 8 wording differs from it, v3 not edited);
- what is still pending before promotion (regeneration comparison, pre-promotion audit by `/audit`, promotion).

**Addendum B: extension program (exploratory)**, from DEC-0037, the schedule note `2026-10-20-extension-schedule.md` and the specification note `2026-10-20-math-extension-specs.md` (when attached):
- why (the limitation "same attractors, fresh seeds"), what (two additional attractors with different properties: hyperchaotic Rössler with two positive exponents and Kaplan-Yorke dimension about 3; Lorenz-63 at r = 166.1 with intermittency), how the pre-registered analysis is applied unchanged and per system, what is reported and what is not (no overall verdict, no confirmatory claim);
- Dysts context: the cross-check of the three systems against the Dysts database, further Dysts systems, and a descriptive comparison with the Dysts forecasting benchmark, as described in the researcher note `2026-10-20-researcher-dysts-extension.md` (when attached);
- the development ensemble (full preset, GPU, development seeds DEV-1, DEV-3, DEV-4), reported only in a labeled development appendix.

**Addendum C: AI-use update** (one paragraph, in the style of the existing AI-use statement; the owner and the student edit it): AI assistance extended to planning, implementing, testing and independently reviewing the code and the findings document, and to checking literature and the Dysts database; the run decisions and rulings are the owner's.

**Final section: Editorial issues noticed (not changed)**, at least these two already known: the due date reads "Oct 30, 2026" in Section 9 while the internal proposal date is 2026-10-28; Section 9 numbers two items "4.".

## 5. Output format

1. The updated Claude Doc.
2. A table "Change list": location, text added, source attachment and section, status (new / needs input).
3. "Needs input": questions for the owner and student.
4. Do not export or replace the governing v3 file. When the owner accepts the addenda, they are exported as a **separate** repository file `docs/study/proposal_and_methods_v3_addendum.md`, recorded with a ledger `amendment` entry; the v3 SHA-256 above stays the pre-registration's.

## 6. Attachments to give Claude web

Required now:
1. `docs/study/proposal_and_methods_v3.md` (governing text, for reference).
2. `docs/agent/notes/2026-10-20-prelim-findings-conf1.md` and its three figures in `2026-10-20-prelim-findings-conf1.figures/` (F1_primary.png, F2_secondary.png, F3_crosscheck.png) (UNPROMOTED).
3. `docs/agent/records/decisions.md`, entries DEC-0031, DEC-0033, DEC-0035, DEC-0036, DEC-0037 (or the whole file).
4. `docs/agent/notes/2026-10-19-research-statement-draft.md` and `2026-10-19-prelim-poster-outline.md` (context for tone and audience).
5. This brief.

When they exist (they are being written now):
6. `docs/agent/notes/2026-10-20-extension-schedule.md`, `2026-10-20-math-extension-specs.md`, `2026-10-20-researcher-dysts-extension.md`.
7. After the regeneration: `runs/confirmatory/run-2-compare.txt` (the owner's comparison, tier and result line).
8. After the ensemble: a development ensemble summary (labeled development), from the main session.
