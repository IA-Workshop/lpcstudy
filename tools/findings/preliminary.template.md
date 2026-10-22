{{banner}}
PRELIMINARY: internal to the owner and the student until promotion (QA.11, LPC.PC.13).

{{mode_notice}}

# Preliminary findings for seed {{official:provenance/seed_id}}

This document is built by `tools/findings_build.py` from the files named in §2. Every number in it is either read from one of those files (and listed in the trace file) or is a design constant of the v3 proposal that cites its section. The build computes no statistic and no verdict. Agents write the tables and this frame; the student writes §11. `check` re-renders the whole document and accepts a difference only in §11 and in dated lines appended to §9.

## 1. The question

The study asks whether four measurable local conditions of a chaotic system (recurrence, observability, instability and noise sensitivity) can decide, state by state, how much to trust an analog forecaster against a physics-based forecaster. The analog forecaster (CP) copies the future of the nearest past delay vector. The physics-based forecaster (PLP) estimates the hidden state and integrates the known equations. The two are blended with a weight w on CP. Three pre-registered primary hypotheses (H2a, H2b and H3c) are tested on Lorenz-63, Rössler and Chua's circuit. This document reports what the pre-registered analysis returned and adds no statistic, threshold, subgroup or recomputed verdict.

## 2. What was run

{{table:provenance}}

## 3. Validation gate (experiment E0) [PRE-REGISTERED]

Checks V1 to V7 of v3 §6, per system. A system whose gate failed is marked PROVISIONAL in every table and figure below. Its verdicts are still computed and shown (v3 §6, E0), and the failure is referred to the owner (DEC-0027, DEC-0031). V3 is reported, not checked.

{{table:gate}}

{{gate_box}}

## 4. Overall verdicts and the decision rule [PRE-REGISTERED]

Decision rule (v3 §7). A hypothesis is supported if it passes on all three systems, not supported if it fails on at least one system, and inconclusive otherwise, including when a system has no result. Requiring every system to pass is an intersection–union test, so the error of "supported" needs no further multiplicity correction. The error of "not supported" is not controlled this way: with {{const:standard_level_pct}} intervals it can reach {{const:unc_not_supported}} over three systems ({{const:unc_h2c}} for H2c's two parts).

Each cell below is the stored verdict word. A "supported" verdict is always written "supported (preliminary, unpromoted)". The last column is the clip-sensitivity text copied from RESULTS.md.

{{table:verdicts}}

{{wording:qn}} The hybrid's horizon gain is {{const:gain_label}}.

{{wording:primary}}

{{wording:secondary}}

## 5. The three primary hypotheses (E1, E2, E4, E5) [PRE-REGISTERED]

Each row is one primary part on one system: the stored estimate, its interval at the level stored in the result (or the primary level of v3 §7 where the result stores none), the pass band of v3 §2 and the stored verdict. The two notes on every row are limitations stated before the run (v3 §8). Endpoints are rounded to four-digit precision for printing; every verdict uses the unrounded endpoints (v3 §7), so a printed edge can equal a band edge that the stored endpoint does not reach.

{{table:primary}}

{{fig:F1}}

{{table:counts}}

## 6. Secondary hypotheses, Q-N, H3a counts and the gain bound (E2 to E5) [PRE-REGISTERED]

Endpoints are rounded to four-digit precision for printing; every verdict uses the unrounded endpoints (v3 §7). The H2c row A4o minus A2 is reported with its interval and carries no verdict (v3 §2).

{{table:secondary}}

{{const:h3b_edge_note}}

Q-N, oracle values, read by the table of v3 §7 (a reading, never pass or fail):

{{table:qn}}

H3a: events and censored states per regime, with the stored Holm-adjusted log-rank p-values (DEF-0018). H3a cannot fail, since no equivalence margin is set (v3 §2).

{{table:h3a}}

{{table:counts}}

Hybrid horizon gain against the P1 bound ({{const:gain_label}}):

{{table:gain}}

Reported quantities that carry no verdict (v3 §2 lists each as reported; each value is read from its stored leaf, and no verdict depends on it):

{{table:reported}}

{{wording:h2c_label}}

{{fig:F2}}

{{table:counts}}

## 7. Handling counters (nothing is silent) [DIAGNOSTIC]

The handling counters of the main systems (PRIME.4). Zero counters are printed, never omitted. The counters of the robustness variants are not listed here: they are in `handling.robustness` of results.json. All nonzero result counts are listed in the Handling section of RESULTS.md; the floors, exclusions and screen-outs among them are read from their stored leaves in the table after the counters.

{{table:handling}}

{{table:resultcounts}}

## 8. GPU cross-check (information only) [CROSS-CHECK: information only]

The GPU run of the same seed is a cross-check, never the result (v3 §9 item 3, DEC-0031). The z value uses the interval arm facing away from the other estimate, and a part disagrees if it exceeds the bound {{const:td_bound}}. The numbers in the first table are copied from the compare_runs text. {{const:hw_ratio_note}}

{{table:crosscheck}}

{{table:crossverdicts}}

{{wording:gpu}}

{{fig:F3}}

## 9. Reproducibility

Regeneration of the official run (WU-0016, v3 §9 item 4): each dated line below is appended after the event it reports.

## 10. Limitations

All items of v3 §8 apply, plus the registered deficiencies and rulings listed here.

- Deployable closed form: the deployable closed form A4 depends almost only on recurrence distance in noise units.
- Exact model: with an exact model, PLP usually wins after one Lyapunov time.
- Deployable features carry little of the information in the exact ones.
- N̂ measures retrieval sensitivity at the observed (noisy) query, not at the true one, so it is reported, not tested.
- The seed × amplifier test (H1b) assumes isotropic seeds and is applied to PLP only.
- Same attractors, fresh seeds: this is not a new set of systems.
- Interval coverage (DEF-0020): {{const:coverage_limit}}
- Slow dependence beyond five states cannot be resolved at these sample sizes.
- Small regimes in H3a (DEF-0018): no minimum is set per regime, so counts are reported beside every p-value.
- Iterative error of PLP (DEF-0027): {{const:lm_limitation}} The report is {{const:lm_report_pointer}}.
- Per-seed gate risk (DEF-0026): V4 and V6 can fail on a given seed, and a failure is referred, never repaired.
- lambda_max for Chua has no published reference value at the study's parameters.
- Doubled thinning is not checked (Methods v2 §M16).
- Bitwise agreement at the official size is extrapolated from smoke size (DEC-0033 M2).
- The gain-bound screen is reported only, computed with the v1 statistic, and the v3 screen is pending (DEC-0033 M3).
- One realization per system: one sealed seed gives one set of data per system, so no replicate variation is estimated.
- The block-sensitive label (a primary verdict that widening the half-width would change) is not computable for the sealed run, because the sealed run writes no states dump (owner default D6).
- Q-N and the gain bound are reported and carry no verdict.
- Power of H2a(ii) (DEF-0022): {{const:def0022_proposed}}
- Regeneration by the same actor (DEC-0035): {{const:same_host_limit}}
- {{const:vv_status_limit}}
- {{const:nvvuq_gaps_limit}}
- {{const:figure_map_limit}}

## 11. What it means and does not mean [STUDENT]

The student writes this section in their own words. Prompts only, with no results: What did each primary hypothesis claim? Which verdicts are supported, not supported or inconclusive, and what does each word allow you to say? Which limitations matter most for what you say? What would you check next?

## A. Development context [DEVELOPMENT]

{{dev_appendix}}

## B. Interval labels

Copied verbatim from the `RESULTS.md` of the official run, one per row (procedure, level, dependence and multiplicity; NVVUQ.16).

{{table:labels}}

## C. Trace

Every number quoted above is listed with its source and leaf path in `{{meta:trace_name}}`. Run the `check` command of `tools/findings_build.py` on this directory to verify the document against the sources.

{{table:missing}}
