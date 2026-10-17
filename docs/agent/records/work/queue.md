# Work queue

Units in priority order. Each unit's plan, log, review and audit live in its own file, `WU-nnnn-<slug>.md`, copied from `WU-template.md` (LPC.PC.9).

| Unit | Title | Depends on | Owner checkpoint | Status |
| --- | --- | --- | --- | --- |
| WU-0001 | Seed registry, confirmatory-seed guard, run provenance | — | review of seed code before freeze | planned |
| WU-0002 | Code changes for Methods v2 §M15 and v3 identifiers | WU-0001 | review of verdict code before freeze | planned |
| WU-0003 | Development rehearsal on DEV-1 (pilot preset) and precision report | WU-0002 | sample-size decision; sets reproducibility tolerance | planned |
| WU-0004 | Freeze package (owner act) | WU-0003 | freeze transaction | planned |

The plans for WU-0001 to WU-0003 are in their unit files. WU-0004 is the owner's act; an agent prepares the checklist when WU-0003 closes.

## Added 2026-10-10: NVVUQ gaps (`docs/agent/governance/NVVUQ-instantiation-LPC.md`)

| Unit | Title | Depends on | Owner checkpoint | Status |
| --- | --- | --- | --- | --- |
| WU-0005 | Code-verification gaps: RK4 observed order, k-d tree against brute force, Levina–Bickel on sets of known dimension, Levenberg–Marquardt residual reporting, N against the Theorem P2 bound | — | none | planned |
| WU-0006 | Statistical-procedure verification: coverage and size simulations for the bootstrap intervals, log-rank with Holm, null ΔR², and the verdict rules, at pilot sample sizes | WU-0002 | review before the freeze | planned |
| WU-0007 | Reference-value validation: published λ_max and parameters for Lorenz-63, Rössler and Chua, retrieved and confirmed by the researcher agent (VV.2) | — | none | planned |
| WU-0008 | Uncertainty budget, numerical-error estimates and interval labels in the report | WU-0002, WU-0005 | review before the freeze | planned |

Before the freeze, WU-0005 to WU-0008 close or are recorded as known limitations. WU-0005 and WU-0007 can run in parallel with WU-0001.

## Added 2026-10-10: roadmap reconciliation (WU-0009.4; claude-opus-5-5, planner)

WU-0001 to WU-0008 are executed as the sub-tasks `WU-nnnn.k` of `ROADMAP.md` §2. Each unit file tracks status per sub-task. Where the dependencies in the tables above differ from the sub-task dependencies below, the sub-task dependencies are the plan (ROADMAP.md §0). The tables above are kept unedited (append-only).

| Unit | Title | Depends on | Owner checkpoint | Status |
| --- | --- | --- | --- | --- |
| WU-0009 | Foundations: baseline commit, environment, baseline smoke reference, queue reconciliation | — | environment set up (WU-0009.2) | in progress (.1, .2 done; .3 in progress; .4 this block) |
| WU-0010 | Test tiers: markers and conftest, split of `tests/test_core.py`, smoke integration test | WU-0009.1 | none | planned |
| WU-0011 | `tools/test_impact.py` and its hand-derived reference graph | WU-0010.2 | none | planned |
| WU-0012 | Run wrappers: `tools/run_tests.sh`, `tools/run_preset.sh`, `tools/gpu_hours.py` | WU-0010.1 | none | planned |
| WU-0013 | DEF-0007 audit of the 14 v1 tests and fixes | WU-0010.2 | none | planned |
| WU-0014 | v3 export, concordance with Methods v2 and code, discrepancy resolution | — | v3 export (WU-0014.1); referrals (WU-0014.3) | in progress (.1 done 2026-10-10, see WU-0009 log) |
| WU-0015 | Confirmatory run (CONF-1, full preset) | WU-0004.7 | per-action authorization; manifest entry; release of outputs | planned |
| WU-0016 | Regeneration by another actor and run comparison | WU-0015.3, WU-0003.6 | per-action authorization; manifest entry | planned |
| WU-0017 | v3 report and figures | WU-0015.4, WU-0016.4 | owner and student read the report | planned |
| WU-0018 | Pre-promotion audit and promotion | WU-0017.2 | promotion transaction | planned |
| WU-0019 | Close-out: retention and governance review | WU-0018.3 | retention; governance review | planned |

Sub-task dependency index (from ROADMAP.md §2; "—" means none):

| Unit | Sub-tasks and their dependencies |
| --- | --- |
| WU-0009 | WU-0009.1 ← —; WU-0009.2 ← WU-0009.1; WU-0009.3 ← WU-0009.1, WU-0009.2; WU-0009.4 ← — |
| WU-0010 | WU-0010.1 ← WU-0009.1; WU-0010.2 ← WU-0010.1; WU-0010.3 ← WU-0010.1 |
| WU-0011 | WU-0011.1 ← WU-0010.2; WU-0011.2 ← WU-0011.1 |
| WU-0012 | WU-0012.1 ← WU-0010.1; WU-0012.2 ← WU-0012.1; WU-0012.3 ← WU-0012.2 |
| WU-0013 | WU-0013.1 ← WU-0010.2; WU-0013.2 ← WU-0013.1 |
| WU-0014 | WU-0014.1 ← —; WU-0014.2 ← WU-0014.1; WU-0014.3 ← WU-0014.2 |
| WU-0001 | WU-0001.1 ← WU-0010.2; WU-0001.2 ← WU-0001.1; WU-0001.3 ← WU-0001.2; WU-0001.4 ← WU-0001.1; WU-0001.5 ← WU-0001.4 (compares against WU-0009.3); WU-0001.6 ← WU-0001.5 |
| WU-0002 | WU-0002.1 ← WU-0010.2; WU-0002.2 ← WU-0002.1; WU-0002.3 ← WU-0002.2; WU-0002.4 ← WU-0002.2; WU-0002.5 ← WU-0002.2; WU-0002.6 ← WU-0002.2; WU-0002.7 ← WU-0002.2; WU-0002.8 ← WU-0002.1; WU-0002.9 ← WU-0002.2; WU-0002.10 ← WU-0002.2; WU-0002.11 ← WU-0002.1; WU-0002.12 ← WU-0002.1 to WU-0002.11, WU-0012.2; WU-0002.13 ← each sub-task |
| WU-0005 | WU-0005.1 ← WU-0010.2; WU-0005.2 ← WU-0010.2; WU-0005.3 ← WU-0010.2; WU-0005.4 ← WU-0002.11; WU-0005.5 ← WU-0002.2; WU-0005.6 ← WU-0005.1 to WU-0005.5 |
| WU-0006 | WU-0006.1 ← WU-0002.5, WU-0002.7, WU-0002.8; WU-0006.2 ← WU-0006.1; WU-0006.3 ← WU-0006.1; WU-0006.4 ← WU-0006.2, WU-0006.3 |
| WU-0007 | WU-0007.1 ← —; WU-0007.2 ← WU-0007.1; WU-0007.3 ← WU-0007.2 |
| WU-0008 | WU-0008.1 ← WU-0002.9, WU-0005.4; WU-0008.2 ← WU-0008.1; WU-0008.3 ← WU-0002.2; WU-0008.4 ← WU-0002.2; WU-0008.5 ← WU-0008.1 to WU-0008.4 |
| WU-0003 | WU-0003.1 ← WU-0009.2, WU-0012.2; WU-0003.2 ← WU-0002.13, WU-0003.1, WU-0005.4, WU-0008.3; WU-0003.3 ← WU-0003.2; WU-0003.4 ← WU-0003.1; WU-0003.5 ← WU-0003.2; WU-0003.6 ← WU-0003.3, WU-0003.4 |
| WU-0004 | WU-0004.1 ← WU-0003.6, WU-0005.6, WU-0006.4, WU-0007.3, WU-0008.5, WU-0013.2, WU-0014.3; WU-0004.2 ← WU-0004.1; WU-0004.3 ← WU-0004.1; WU-0004.4 ← WU-0004.2; WU-0004.5 ← WU-0004.4; WU-0004.6 ← WU-0004.5; WU-0004.7 ← WU-0004.6; WU-0004.8 ← WU-0004.7 |
| WU-0015 | WU-0015.1 ← WU-0004.7; WU-0015.2 ← WU-0015.1; WU-0015.3 ← WU-0015.2; WU-0015.4 ← WU-0015.3 |
| WU-0016 | WU-0016.1 ← WU-0015.3; WU-0016.2 ← WU-0016.1; WU-0016.3 ← WU-0003.6; WU-0016.4 ← WU-0016.3 |
| WU-0017 | WU-0017.1 ← WU-0015.4, WU-0016.4; WU-0017.2 ← WU-0017.1; WU-0017.3 ← WU-0017.1 |
| WU-0018 | WU-0018.1 ← WU-0017.2; WU-0018.2 ← WU-0018.1; WU-0018.3 ← WU-0018.2 |
| WU-0019 | WU-0019.1 ← WU-0018.3; WU-0019.2 ← WU-0018.3 |

- 2026-10-10, claude-sonnet-5-5 (main session): WU-0010 (.1 to .3) **done** on branch `wu/0010-test-tiers`: independent review approved, merge gate `20 passed in 75.57s`, DEC-0002 confirmed by the owner; merge to `main` follows. Dependent sub-tasks (WU-0011, WU-0012, WU-0013, WU-0001, WU-0002, WU-0005) are unblocked once the merge lands.
- 2026-10-10, claude-opus-5-5 (planner): WU-0011 **plan written** on branch `wu/0011-test-impact` (`.1` tool, `.2` fixture and comparison test). The reference graph is derived by hand in the plan (53 edges, at `d6abaa7`), to be committed verbatim before any tool code. Owner questions Q1–Q6 are in the unit file; none blocks `.1` or `.2`.

- 2026-10-10, claude-sonnet-5-5 (main session): WU-0011 (.1 and .2) **done** on branch `wu/0011-test-impact`: independent review approved, merge gate `63 passed in 75.04s`; DEC-0003 (proposed) and the Q2 selection gap are with the owner; merge to `main` follows. WU-0012.1 (wrappers) and the other tool units can now use `tools/test_impact.py`.

- 2026-10-10, claude-sonnet-5-5 (main session): WU-0014.1 and .2 **done** and merged (concordance reviewed, approve after one fix round; 28 discrepancies: 18 code, 4 gap, 6 document, 1 resolved). WU-0014.3 **waits for the owner's rulings** on the referral (five items).
- 2026-10-10, claude-sonnet-5-5 (main session): in progress in worktrees under `../lpcstudy-wt/wu/`: WU-0001.1-.5 (`wu/0001-seeds-provenance`), WU-0012.1-.3 (`wu/0012-wrappers`), WU-0013.2 (`wu/0013-def0007-audit`; WU-0013.1 audit done: 13 reference, 1 defective). New defects: DEF-0010 (seeds of 2**32 or more crash scikit-learn; blocks WU-0003), DEF-0011 (fixed literal seed in oracle.py). New proposed decisions awaiting the owner: DEC-0003 to DEC-0005.

- 2026-10-10, claude-sonnet-5-5 (main session): WU-0013 (.1 and .2) **done** and merged (audit: 13 reference, 1 defective; gate 78 passed; DEF-0007 resolved). WU-0001.1-.5 and WU-0012.1-.3 are implemented and in review (fix rounds in progress). New proposed decisions awaiting the owner: DEC-0004 (WU-0001), DEC-0005 (WU-0012), DEC-0006 (RSS test bound).

- 2026-10-11, claude-opus-5-5 (planner): WU-0006 **plan written** on branch `wu/0006-simstudies` (`docs/agent/records/work/WU-0006-simstudies.md`): harness, coverage and verdict error rates C1–C9, log-rank size L1–L2, null ΔR² N1–N3, with criteria fixed in advance. It awaits the applied-mathematician (M1–M6) and the owner (O1–O5: process pool, file names, ΔR² sizes, residual autocorrelation, ΔR² estimand). Failures are predicted at lag-1 0.3 for mean-type statistics (blocks of 5) and for N1.

- 2026-10-11, claude-opus-5-5 (planner): WU-0005.5 **plan written** on branch `wu/0005-5-p2c-bound` (`docs/agent/records/work/WU-0005.5-p2c-bound.md`): split into .5a (applied-mathematician fixes the empirical form of P2(c), decisions M1-M9) and .5b (developer). Owner questions O1 (DEV-0 vs DEV-1 rehearsal; add WU-0005.5 to WU-0003.2's dependencies) and O2 (P2(c) outside the validation gate) are in the unit file; neither blocks .5a.

- 2026-10-11, claude-opus-5-5 (planner): WU-0002.11 **plan written** on branch `wu/0002-11-counters` (`WU-0002.11-counters.md`). The plan inventories every silent site and fixes the `handling` schema. It splits the work into four lanes:
  - .11a, pipeline counters: now, in parallel with WU-0002.9;
  - .11b, statistics and analysis counters: after WU-0002.9 merges;
  - .11c, the DEF-0015 guard: after the owner's ruling Q1;
  - .11d, the DEF-0011 audit: a table now, conversions after WU-0002.12.

  DEF-0012 is proposed as a separate small unit. The LM-internal sites go to WU-0005.4. Owner questions Q1 to Q7; Q1 blocks .11c only. The applied-mathematician checks M1 to M8 before execution.

- 2026-10-11, claude-opus-5-5 (planner): WU-0002.12 **plan written** on branch `wu/0002-12-pilot-regression` (`WU-0002.12-pilot-regression.md`). Step 1, the tool `tools/compare_pilot.py` and its tests T1 to T10, can start now. Steps 2 and 3, the CPU pilot run on DEV-0 and the comparison, are **BLOCKED** until the owner records the fallback criterion (risk R1; referral in the unit file; proposed text F1 to F5 with tightenings (a) to (c)). The applied-mathematician's tasks AM1 to AM5 come before the owner's ruling. Further owner decisions: O2 (`LPC_THREADS`), O3 (order: WU-0002.9b before the run, DEF-0017 and .11d after it), O4, O5.

- 2026-10-11, claude-opus-5-5 (planner): WU-0008 **plan written** on branch `wu/0008-report-budget` (`WU-0008-report-budget.md`). Order: .3 labels and .4 QoI table first (no WU-0005.4 dependency), then .2a (endpoint Monte Carlo error at the five primary sites), then .1/.2b budget tables. The LM row waits for WU-0005.4's keys and prints `not estimated` until they exist. Design tasks M1 to M9 go to the applied-mathematician before .1/.2. Owner questions O1 to O6; none blocks .3 or .4.
- 2026-10-11, claude-opus-5-5 (planner): WU-0001.6 (platform record, DEC-0022 item 4, DEF-0024) **plan written** on branch `wu/0001-6-platform-record` (`WU-0001.6-platform-record.md`). The plan has two steps: .6a in `lpcstudy/` (`provenance.array_digest`; W and U digests as new `context` leaves via `experiments.context_record`, with `data.py` untouched; `cpu`, `blas` and `numpy_simd` in the provenance block via stdlib probes; `OPENBLAS_CORETYPE` and `NPY_DISABLE_CPU_FEATURES` in `ENV_NAMES`; a `Platform:` header line) and .6b, the `compare_pilot` rule for the new leaves and a platform section. .6b is required, because without it the tool exits 2 on new output. Acceptance criteria A1 to A10 are exact. The mathematician checks M1 to M5. Owner questions: O1 (schema `/2`, recommended), O2 (the identifier clashes with the ROADMAP's WU-0001.6 review sub-task) and O3 (the platform record of the local v1 baseline). Needs owner review before freeze (provenance code).

- 2026-10-11, claude-sonnet-5-5 (developer): WU-0001.6 (platform record) **in progress** on branch `wu/0001-6-platform-record`: .6a and .6b implemented, independent review rounds 1 and 2 answered (R1 to R3, R5, R6 fixed), unit radius green. **Needs owner review before freeze** (provenance code, LPC.PC.11). Pending before merge: R4 (A3 base-against-final smoke, the integration pair), then A9 (forced Sandybridge) before closure; they wait for the v1-baseline pilot run to end.

- 2026-10-11, claude-opus-5-5 (planner): WU-0005.4 **plan written** on branch `wu/0005-4-lm-diagnostics` (`WU-0005.4-lm-diagnostics.md`): residual, accepted-step count and the S3/S4 counters returned from the same compiled LM loop (no separate pass), summarized per cell under `handling.cells[<id>].lm`, with a RESULTS.md row. Criteria L1-L7 and V1-V3 (V1: every pre-existing smoke leaf bitwise equal, `handling` included). The applied-mathematician answers M1-M7 before execution; owner questions O1-O4 (schema id, placement, wrong-basin rate, other solvers) block nothing before M1-M7.

## Added 2026-10-12: DEC-0026 items 3 and 4 (claude-opus-5-5, planner)

| Unit | Title | Depends on | Owner checkpoint | Status |
| --- | --- | --- | --- | --- |
| WU-0002.11c | DEF-0015 guard: a diverging Lyapunov or `build_context` orbit refuses the run (bounds on \|x\| 40, 25, 3, plus finiteness); orbit maxima as `context` leaves; cache recomputed once and asserted bitwise | WU-0002.11 (lanes .11a, .11b merged) | owner ruling given (DEC-0026 item 3); needs owner review before freeze | planned |
| WU-0002.14 | Seed-dependent start states (`make_rng(seed, "start", system)`) plus the remaining `default_rng` conversions (DEF-0011, R1 table), as one numbers-changing step; DEV-0 pilot regenerated and adopted as the new reference | WU-0002.11c merged | seed and statistics code: needs owner review before freeze; O1 to O8 (O4 before the P1 run) | planned |

- 2026-10-12, claude-opus-5-5 (planner): WU-0002.11c and WU-0002.14 **plans written** on branch `wu/0002-11c-start-states` (`WU-0002.11c-orbit-guard.md`, `WU-0002.14-seeded-states.md`).
  - **.11c.** Criteria G1 to G8 (analytic RK4 references; λ bitwise against a verbatim copy of the pre-change Benettin loop) and V1 to V4 (smoke neutrality: exactly 4 new `context` leaves at smoke). The applied-mathematician checks M1 to M5. Owner questions Q1 and Q2.
  - **.14.** It starts after .11c merges, on a fresh branch. Split .14a (conversions), .14b (start states), .14c (`compare_pilot --redrawn-states`), .14d (runs).
  - **.14 verification.** Property tests P1 to P7 and slow distributional checks S-D1 and S-D2. Staged smokes S1 and S2 with predicted divergence loci. A P0 pilot at the base (branch B against the local baseline), then P1 under D3 plus exact invariants I1 and R-c to R-h. P1 becomes the new reference.
  - **.14 questions.** The applied-mathematician checks M1 to M7. Owner questions O1 to O8; O4 (the regression reading and the DEC-0020 SE_new arm) is needed before P1.
- 2026-10-14, claude-sonnet-5-5 (main session): **WU-0002.14 merged to develop** (4aa16a5) after plan, mathematics check, implementation, review, two fix rounds plus a text/rule round, the P0 (branch B) and P1 (branch D) pilots, the independent P1 review (accept; R2 to R4 closed) and the integration tier (12 passed) at the branch tip; needs owner review before freeze (seed, provenance, statistics code). New reference `docs/study/pilot_results_v3_dev0_reference.json`. DEF-0011 and DEF-0017 resolved; DEF-0026 opened (V6/V4 gate risk, owner decision). Next: WU-0005.6 merge (review round 2 accepted, tip 0896d1a; R9 post-merge radius and smoke redo), then a merge gate on develop.
- 2026-10-12, claude-opus-5-5 (planner): WU-0005.6 (LM iteration-doubling study, DEC-0026 item 9) **plan written** on branch `wu/0005-6-lm-doubling` (`WU-0005.6-lm-doubling.md`). The plan has three steps:
  - .6a: a CLI flag `--estimator-refine-steps N` (refused with `--confirmatory`) with a `run_preset.sh` pass-through. The production default stays 15.
  - .6b: `tools/lm_doubling.py`, with `compare` (QoI level) and `probe` (per estimate, core cell, 15/30/60).
  - .6c: DEV-0 smoke runs at 15, 30 and 60, then pilots at 15 and 30 (60 only under rule D2), all on CPU, one at a time.

  The decision rule (d1 = max relative change of point and endpoints over the half-width) is fixed in advance:
  - negligible if d1 < 0.05 with a credible 30-iteration reference;
  - not negligible if d1 ≥ 0.1 or a verdict changes;
  - undetermined in between, which triggers the 60 arm.

  The applied-mathematician answers M1 to M8 before execution. Owner questions O1 to O6; O3 is an identifier clash with the ROADMAP's WU-0005.6 review sub-task. Recommendation: run now, before the seed step. Needs owner review before freeze (the seed-guard parser and the wrapper).
- 2026-10-14, claude-sonnet-5-5 (main session): **WU-0003 lanes.** .7a implemented and reviewed on `wu/0003-rehearsal` (f51e204; fix round 1 done; the a1 smoke pair, `compare_pilot` on the real pair and the integration tier wait for a free CPU slot, held by the WU-0005.6 k15/k30 pilots). Plan amendments 2 and 3 written (dcc4ff2, 19a07ee). .9 (`tools/compare_runs.py`, `wu/0003-9-compare-runs`, tip ed0cc05) **referred** after two fix rounds (blocker R14, owner note section 18); needs owner review before freeze. Owner flags OF-1 to OF-7 and the rulings listed in sections 16 to 18 of `docs/agent/notes/2026-10-11-amendments-for-owner.md`.
- 2026-10-12, claude-opus-5-5 (planner): WU-0003 **plan amendment 1 written** on branch `wu/0003-rehearsal` (`WU-0003-dev-rehearsal.md`; DEC-0026 item 10). Procedure: R0 smoke and device probe; R1 pilot on DEV-1 on the GPU with a per-state dump; R2 and R3 reproducibility (GPU against GPU, GPU against CPU); R4 optional forced-BLAS CPU run; R5 full on DEV-2 (owner authorizes); R6 optional full on CPU. New sub-tasks .7 (dump, split-half moments, V4 by horizon, weight digests), .8 (diagnostics) and .9 (`compare_runs`, WU-0016.3 pulled forward). Reproducibility tiers T0 to TD are fixed by digests before the runs. **Blocked until** DEF-0025, the WU-0002.11e implementation, WU-0002.11c, the seed step (DEF-0017 with .11d and the regenerated DEV-0 reference), the WU-0005.6 report, .7 to .9 and a gate at `C_R`. The applied-mathematician answers M1 to M8 before execution; owner questions O1 to O8.
- 2026-10-14, claude-opus-5-5 (planner): WU-0003 **plan amendment 2 written** on branch `wu/0003-rehearsal` (`WU-0003-dev-rehearsal.md`, B1 to B5; basis: the mathematics check `2026-10-14-math-wu0003.md`; develop b982806 merged first). There are 12 amended items. Every threshold is at least as strict as in amendment 1. Where the draft was looser, the stricter reading applies and the point is flagged (PF-1 to PF-5).
  - **Sub-tasks:** .7 is split into .7a (results leaves: trajectory, proxy-fit and A5 digests, weight digests) and .7b (opt-in dump); .8 (diagnostics D1 to D6); .9 (`compare_runs`). All four need owner review before freeze.
  - **Order:** .7a, .9, .7b, .8.
  - **Owner:** questions OF-1 to OF-6 and PF-1 to PF-5, and the pre-registration items P-1 (R0 on three systems) and P-2 (the C1 gate-failure probabilities). OF-6/P-2 must be settled before R1.
- 2026-10-14, claude-sonnet-5-5 (developer): WU-0003.7a **implemented** on branch `wu/0003-rehearsal` (unit radius run once, see `WU-0003-dev-rehearsal.md` `## Log`). New bitwise-neutral `results.json` leaves, no new random draw: `context/main_digest` and `estimator_digest`; `fitted/<proxy>/nfev` and `status` for both proxy fits; `fitted/a5_leaf_digest` and `fitted/allocator_digest`; `weights_digest` in every `estimators` entry. A `new` rule in `tools/compare_pilot.py` for them. **Needs owner review before freeze** (provenance digests and the verdict-chain leaves, B2 row .7a). **Pending:** the a1 DEV-0 smokes (base and tip) and the integration tier, which start smoke presets and wait for a free slot (a pilot arm of another lane was running).
- 2026-10-14, claude-opus-5-5 (planner): WU-0003 **plan amendment 3 written** (`WU-0003-dev-rehearsal.md`, C1 to C6; from the WU-0003.9 review, note `2026-10-14-math-wu0003-9-q1.md` and the amendments note §17). Contents:
  - C1: d3 figure corrected to 2.94e-7;
  - C2: d1 fixture change recorded (Q6);
  - C3: the R1-against-R2/R3 scope rule; working default (A), R2 and R3 without `--skip-robustness`;
  - C4: every float leaf tagged or overridden, with a pinning test, before R1 (Q9);
  - C6: owner questions R5/O3, OF-7, Q7, Q8, `handling` scope, R6, Q6, Q9.

  No threshold is loosened.
- 2026-10-14, claude-sonnet-5-5 (developer): WU-0003.7b **implemented** on branch `wu/0003-rehearsal` (unit radius run once, see `WU-0003-dev-rehearsal.md` `## Log`). Opt-in `--states-dump` writes `states/<system>.npz` (schema `lpcstudy.states/1`, documented in `lpcstudy/dump.py`); refused with the sealed flag before the seed is read and with `--report-only`; dump on adds one provenance leaf. **Needs owner review before freeze** (validation and LM data; the CLI guard). Nine open questions in the Log, each answered with the stricter option (notably: LM arrays for all three splits, so that b3 can reproduce the pooled LM block). **Pending:** the integration tier (including the new `tests/integration/test_states_dump.py`), the b1 and a1 smokes, `compare_pilot` and the b7 size, all of which start presets and wait for the slot.

- 2026-10-14, claude-sonnet-5-5 (developer): WU-0003.8 **implemented** on branch `wu/0003-8-diagnostics` (`tools/rehearsal_diagnostics.py`, D1 to D6; unit file `47 passed` after fix round 1, see `WU-0003-dev-rehearsal.md` `## Log` and `WU-0003.8-review.md`). Tool only: nothing in `lpcstudy/` changed. **Needs owner review before freeze** (statistics feeding the block-length and M decisions; the tool seed constant and options, review R9). **Pending:** the slow tier `tests/slow/test_rehearsal_diagnostics_mc.py` (waits for a free CPU slot) and the real-data run on the R1 dump. Planner questions Q1, Q2, Q7, Q8, Q11, Q12, Q13 are in the Log.
- 2026-10-14, claude-sonnet-5-5 (developer): WU-0003.7c **implemented** on `wu/0003-rehearsal` (461d171): dump schema `lpcstudy.states/2` (per-state H1c ratios with eligibility, H1a squared seed errors with sizes, levels and inverse dimension), bitwise-neutral. Evidence: dump-off smoke against the .7b tip 0 different, 0 removed, 0 added; unit radius 379 passed; integration tier 19 passed (H1c and H1a reproduced bitwise from the dump). **Needs owner review before freeze** (verdict-chain data; schema consumed by the diagnostics).
- 2026-10-14, claude-sonnet-5-5 (developer): correction to the WU-0003.7c line above (append-only): the unit radius run was `1 failed, 379 passed in 43.94s` and, after fixing my own round-trip assertion, `--lf` `1 passed` (the line said only "379 passed"). Fix round 1 for the review findings R1 to R4 is in the Log (docstrings, a `record_extra` guard, test labels and corrections); no result changes.
- 2026-10-17, claude-sonnet-5-5 (developer): WU-0003.8 **fix round 2** on `wu/0003-8-diagnostics` (re-review R12 to R16; amendment 5 E1 to E8 implemented; `wu/0003-rehearsal` merged in, unit file and queue.md as a union). Unit file `54 passed`. Slow tier unchanged (not rerun). **Needs owner review before freeze** (statistics; the tool seed and options, OQ-R9). Later rows: .8b (C4), .8c (H1a, H1c).
- 2026-10-14, claude-sonnet-5-5 (developer): WU-0003.3a **implemented** on branch `wu/0003-3a-report` (from `wu/0003-rehearsal` 7456737): `tools/rehearsal_report.py`, the C7 projection of the precision report (readings (i) and (ii), kappa_E from the dump, v3 comparison, false-trigger rates, R5 against R1 with `--observed`). Unit radius `1 failed, 35 passed` (my own assertion), `--lf` `1 passed`; slow f2 `4 passed` (one case at 3.85 SE, estimator bias +7e-4, see the Log). f3 reproduces `m3_projection.log` for P0 and P1 to the printed digits. Needs owner review before freeze (sample-size decision); open questions 1 to 9 in the Log. No `lpcstudy/` change, no preset.

- 2026-10-15, claude-sonnet-5-5 (developer): WU-0003.3a **fix round 2** (amendment 7 G1 to G3 and the R2 note): H3a projected from `logrank_p_raw` (chi2.isf, doubled, Holm, bar read from `analysis.H3A_ALPHA`), exit rule G2, H2a(ii) margin reading governing, range governing kappa_E (point kappa information only). Unit radius `55 passed`. Exit 0 is unreachable under working default (a) (G2 counts the FALLBACK): planner/owner question in the Log. f2 untouched.
- 2026-10-17, claude-sonnet-5-5 (developer): WU-0003.3a **fix round 3** (review round 2, R7 to R9): an unknown `KAPPA_POLICY` is refused (exit 2) and the policy is recorded in `--json`; the `None` H3a pair names both causes; a lower-bound pair prints `p_full < 1e-300`. Unit radius `63 passed`. R10 (exit-0 rule under (a)) stays with the planner and owner.
- 2026-10-17, claude-sonnet-5-5 (developer): WU-0003.3a **final round** (plan amendment 8 H1 to H3): range-governed H2c, H2d and H3c rows count as computed (exit 0 reachable); the `"point"` branch is removed and the point kappa is information only (mutation test: no projected number changes); documentation of H2. Unit radius `63 passed`. **.3a is finished pending the independent read** and the owner's OF-H1.
- 2026-10-17, claude-sonnet-5-5 (developer): WU-0003.3a **fix round 5** (independent read of rounds 3 and 4, R11 to R13): a core system absent from `results.json` is a counted item (exit 2); a dump with any defect is unusable on its first defect (no information values); the summary range follows the run (`kappa_range`). Unit radius `69 passed` (once; the session paused after the run, nothing rerun). Pending the owner rulings OF-H1 and OF-R2.
- 2026-10-17, claude-sonnet-5-5 (developer): WU-0003.3a **fix round 6** (read of 559f2fd, R14 to R16): malformed `core_systems` is one counted item; an unexpected dump exception is counted and the dump unused with the report complete; docstrings corrected. Unit radius `77 passed` (once). Pending the owner rulings OF-H1 and OF-R2.
- 2026-10-17, claude-sonnet-5-5 (developer): WU-0003.8b (C4 LM readings) and WU-0003.8c (H1a and H1c influence series) **implemented** on `wu/0003-8-diagnostics`, with fix round 3 (R17 to R20) and amendment 9 (I1 min anchor, I2 C7 for the H2a(ii) "one" part, N up to 27). Unit file `77 passed`. **Needs owner review before freeze** (statistics; seed code OQ-R9; OF-I1, OF-I2). Slow tier unchanged. Pending: the real-data run on the R1 dump; WU-0003.10 (shared module) after .3a.
- 2026-10-17, claude-sonnet-5-5 (developer): WU-0003.8 **fix round 4** (R22 to R27) and amendment 10 (J1 acf figures, J2 stack-dependent reproduction of `fitted_inverse_dim`) on `wu/0003-8-diagnostics`; unit file `85 passed`. Needs owner review before freeze (statistics; seed code OQ-R9). Slow tier unchanged.
- 2026-10-17, claude-sonnet-5-5 (developer): WU-0005.6 / DEF-0028 **implemented on branch `wu/0005-6-rule-r-order`** (owner ruling: structural switch gives U before the X bullets); unit test file 132 passed; DEV-0 offline re-run: Chua H3c X -> U, N 5 / X 6 / U 7, LM-row flag 5 of 18; report v3 in `docs/agent/notes/`. **Pending independent review; not merged.**
