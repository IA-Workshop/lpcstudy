# WU-0023: CP / PLP / A4 comparison on further Dysts systems (first set, development appendix)

| Field | Value |
| --- | --- |
| Status | planned |
| Class | CSQ3 development (exploratory; DEV-3; never confirmatory) |
| Agent(s) | claude-opus-5-5 (planner); researcher, applied-mathematician, developer, reviewer and main session to be named; under DEC-0037 |
| Estimate | About 2 agent hours per system plus 2 h of overhead; GPU about 0.5 h per system at the pilot preset. **Target 2026-10-26** for a first set. |

## Plan (written before execution)

- **Scope.**
  - **In:**
    - up to the owner's cap (O9; planner default 4) of further Dysts ODE systems, each added as an additive `SystemSpec` exactly as in WU-0021;
    - one pilot per system on DEV-3, on the GPU under the lock, with `--skip-robustness`;
    - a development appendix table.
  - **Out:**
    - full-preset runs (unless GPU time is left on 10-25 and the owner asks);
    - seed-to-seed replicates;
    - Lorenz-96 (LPC.PC.1, D3);
    - misspecified models;
    - maps, delay and PDE systems;
    - any new criterion.
- **Selection rules** (fixed now; the researcher applies them, the mathematician confirms):
  1. An autonomous ODE flow with a Dysts entry giving equations, parameters and an estimated λ_max > 0.
  2. Dimension 3 to 5, with D = 7 > 2 d_KY. d_KY stands in for d_box (Embedology), and the shortfall is reported.
  3. Coordinate 0 is bounded on the attractor and is a usable observable. Otherwise the system is dropped: a guard change is out of scope here.
  4. RK4 with `max_dt` meeting V6 at no more than about 60 substeps per observation interval, which keeps the cost at or below about 2.5 × a 3-D system.
  5. A qualitative contrast with the systems already in the study (studied and WU-0021), named in one line per system: for example a different d_KY, a multi-scroll attractor, a non-smooth field, or a slow manifold.
  6. A published or Dysts λ with its source.

  Ties are broken by the lowest cost.
- **Sub-tasks.**

  | Id | What | Owner | Effort | Depends on | Target |
  | --- | --- | --- | --- | --- | --- |
  | .1 | Ranked recommendation against rules 1 to 6, with sources | researcher | S | WU-0021.1 | 10-22 |
  | .2 | Specification per system (as WU-0021.2) and readings, fixed before any run | applied-mathematician | S per system | .1, O9 | 10-22/23 |
  | .3 | Implementation per system, R1 regression, plumbing smoke | developer | S per system | WU-0021.7 merged, .2 | 10-23 |
  | .4 | Review of .3 (one review for the set), then pilots in sequence on the GPU | reviewer; developer, main session | S + wall clock | .3 | 10-24/25 |
  | .5 | Appendix table: gate V1 to V7, stored per-system verdict words, λ, CP VPT (V3 leaf) | main session | S | .4 | 10-26 |

- **Definition of done.** The selected systems are merged on `develop`, each with a pilot recorded in the manifest as exploratory, and the appendix table is ready for WU-0025.5.
- **Acceptance criteria.**
  - **C1.** For every added system: R1 (bitwise three-system smoke regression), R2 (additivity), R3 (pins, extended with the WU-0021 systems), and A1 to A7, all as in WU-0021 with the same references and tolerances.
  - **C2.** Gate V1 to V7 at v3 §6. A failure marks the system provisional and is reported, never retuned.
  - **C3.** Every table value is a stored leaf with its path, or a cited source.
- **Affected checks.**
  - The same core-module radius as WU-0021.4. Confirm it with `tools/test_impact.py --base develop --explain`.
  - Slow tier: `test_start_states.py -k <new>` and the λ test once per added system.
  - Integration tier once per change set, not once per system: add the systems in one change set.
- **Owner checkpoints.** The cap and the list (O9). No verdict, seed, provenance or dependency change.
- **Drop rule.** If WU-0021 is not done by 10-22 end of day, .3 starts only after it. The set shrinks to what can be piloted by 10-25 18:00. Below one system, the unit is deferred and the appendix says so.

## Log
- 2026-10-20 (main session, owner instruction after the researcher and specification notes): the owner keeps S2 (WU-0021) as a reference and asks for further candidates, run batched to save time. Candidates S4 Hindmarsh-Rose, S5 HyperJha, S6 4-D Lorenz-96 (F = 20), S7 coupled Lorenz (6-D, stretch) are taken from the researcher note (B.3, D.2) and are being specified by the applied-mathematician in `docs/agent/notes/2026-10-20-math-extension-specs-2.md` (staged: S4 and S5 first). Implementation follows the WU-0021 pattern, in a lane after the WU-0021 branch lands. Batching decision (main session; owner may overrule): after code review, all extension systems run in ONE invocation of the study command per development seed (`--systems <list> --skip-robustness`, GPU, one lock), the separate pilot stage of WU-0021.6 is folded into that full run (the full run carries the gate V1 to V7 per system); results stay provisional until the review of the code approves it, and a code change after the run means a rerun. Spare CPU cores (the regeneration run-2 ends this evening) may run the same systems on the CPU in parallel at LPC_THREADS 8 as a development cross-device check (TD tier), never replacing the GPU result. Target for the first batch moves from 10-26 to 10-23.

## Review

- **Reviewer:**
- **Findings and resolution:**

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:

## Referral
