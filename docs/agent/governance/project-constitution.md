# Project Constitution: LPC Study (`lpcstudy`)

| Field | Value |
| --- | --- |
| Level | LVL3 project instrument (GOV.20) |
| Inherits | LVL0 Constitution for Computational and Cyber-Physical Systems, revision 1.5 (`LVL0-constitution.md`) |
| Profiles (LVL1) | NVVUQ, proposed (`LVL1-profile-NVVUQ.md`), with its project instantiation in `NVVUQ-instantiation-LPC.md`. See LPC.PC.4. |
| LVL2 standards | The custodians' adopted defaults apply where this document is silent (GOV.22). |
| Project mnemonic | LPC. Provision identifiers are `LPC.PC.n` here, `LPC.AI.n` in the agent instructions, `LPC.RAR.n` and `LPC.EXC.n` in the register, `LPC.AUTH.n` in the authorizations and `LPC.TM.n` in the threat model. |
| Status | **Draft.** Proposed 2026-10-10 by Claude (claude-opus-5-5) at the human owner's request. Not in force until the human owner adopts it by ledger transaction (GOV.41, GOV.49). |
| Human owner | the PI: `<name>` (fill in at adoption) |

Every provision below cites the higher provisions it instantiates and only tightens them (PRIME.15). Where this document and a higher level appear to conflict, the higher level governs (GOV.1) and an agent halts and refers (PRIME.14).

**Design intent: autonomy with checkpoints.** The project is under deadline pressure. Its governance is therefore built so that an agent can develop and test code autonomously, and the human owner's attention goes to a few checkpoints:

1. the freeze;
2. the confirmatory run;
3. promotion of results;
4. anything the safeguards reserve.

Development work on development seeds is internal (LPC.PC.5), and broad verification is deferred to the freeze (RSRC.12).

## 1. Project, scope and roles

1. **LPC.PC.1 Scope** (SIMPL.10). The project implements, verifies and runs the LPC study specified by these documents:
   - the proposal and methods v3 (Claude Doc *LPC Study: Proposal and Methods (v3)*; export to `docs/study/` before relying on it);
   - Methods v2 (`docs/study/methods_experimental_procedures_v2.md`) and the decision log (`docs/study/decision_log_lpc.md`).

   Where v3 and v2 differ, v3 governs the study design. v2 §M15 lists the required code changes, and the decision log maps hypothesis identifiers between versions.

   Out of scope; refuse it or spin it off (SIMPL.10):
   - Lorenz-96 and transfer experiments;
   - a misspecified-model forecaster arm;
   - Lean formalization;
   - new hypotheses, systems or rules not in the v3 design.

   An agent that finds such work necessary records it as a note (SIMPL.3) and refers it.
2. **LPC.PC.2 Roles** (PRIN.1, PRIME.1).
   - **The PI is the human owner** and performs every act PRIME.1 and GOV.50 reserve.
   - **The student is the study's primary author** and an actor on the project. The student reviews results and proposes interpretations. Promotion stays with the human owner.
   - **Agents** (Claude Code sessions and the subagents they direct) are actors under the agent instructions (`agent-instructions.md`).

## 2. Classification and proportionality

3. **LPC.PC.3 Classification** (GOV.12, GOV.13, GOV.24).
   - **Consequence class: CSQ2 (relied upon).** The human owner stated it on 2026-10-10.
   - **Basis.** The study's results are relied upon beyond their author: by the student, the PI and science-fair judges. An error causes wrong conclusions, recoverable with substantial rework.
   - **Attributes for profile selectors:**
     - domain: numerical scientific computing (deterministic simulation of ODEs, stochastic sampling, statistical inference);
     - no physical hardware is commanded, configured or powered (the GPU is computing hardware);
     - no personal data;
     - no secrets in the work;
     - outputs feed a public science-fair entry;
     - single site, single owner.
4. **LPC.PC.4 Profiles** (GOV.25, GOV.28, GOV.29). The classification in LPC.PC.3 satisfies the selector of the proposed LVL1 profile NVVUQ (numerical VVUQ, `LVL1-profile-NVVUQ.md`).
   - **Once adopted.** When the custodians adopt NVVUQ, it binds this project in full, as instantiated in `NVVUQ-instantiation-LPC.md`.
   - **Until then.** NVVUQ applies by analogy (GOV.29). The human owner records that choice in the classification transaction, together with any other admitted profile whose selector the attributes satisfy.
5. **LPC.PC.5 Component classes** (GOV.13, GOV.14, GOV.11).

   | Component | Class | Why it is isolated |
   | --- | --- | --- |
   | **Development work** (code under development, runs on `DEV-n` seeds, scratch analyses, notes) | CSQ3 | Its outputs are relied upon only by the project team, feed work that is verified at the freeze, and are never reported as hypothesis tests |
   | **Confirmatory pipeline** (the code revision frozen for the confirmatory run, the confirmatory run itself, and its reported results) | CSQ2 | — |

   A development output that is reported or relied upon beyond the team, other than precision estimates the owner uses for a sample-size decision, takes CSQ2 first (GOV.14).
6. **LPC.PC.6 Proportionality judgment** (GOV.11, PRIN.9). The burden at each checkpoint is:

   | Checkpoint | Evidence required |
   | --- | --- |
   | **Merging a change during development (CSQ3)** | The floor (GOV.10), plus: the tests the change can affect pass (RSRC.11); new numerical code has at least one test against an independent reference (VV.7, LPC.PC.21); agent review under LPC.PC.11. |
   | **The freeze (entry to CSQ2)** | Full test suite; validation gate V1–V7 on all three systems; a development rehearsal on a `DEV-n` seed that runs end to end (WU-0003); dependency pins recorded; review by the human owner of the analysis code that computes verdicts. |
   | **Promotion of a confirmatory result (CSQ2)** | The result is regenerated from its record by an actor other than its producer (QA.9), meets the frozen criteria (VV.3), and states verification and validation status separately (VV.5). |

   Exploratory overhead stays at the floor. Nothing in this document requires more of development work.

## 3. Integrity of the pre-registration

7. **LPC.PC.7 Seed separation** (VV.3, QA.12, PRIME.2, PRIME.11).
   - **Development seeds.** Development runs use only master seeds listed in `seeds/development_seeds.json`.
   - **The confirmatory seed** is drawn by the human owner at the freeze. It is committed by SHA-256 in the ledger before first use (`seeds/README.md`) and held outside the repository.
   - **Agents never draw, request, read or guess the confirmatory seed**, and never run the confirmatory pipeline except under a per-action authorization (LPC.AUTH.6).
   - **A run on a seed not in the development registry and not matching the commitment** is a blocking defect. The code refuses it (WU-0001).
8. **LPC.PC.8 Freeze** (VV.3, REPRO.1). The freeze is a ledger transaction by the human owner. It records:
   - the commit hash of the code;
   - the SHA-256 of the exported proposal-and-methods document;
   - the configuration;
   - the dependency lock;
   - the confirmatory-seed commitment.

   After the freeze, any change to a criterion, statistic, horizon, sample size or analysis code that bears on a verdict is a recorded decision (REPRO.7). Results judged under the changed criterion are promotable only as unverified (QA.12). The one exception is the sample-size extension rule, if it was pre-registered before the freeze.

## 4. Project mechanisms (GOV.21)

9. **LPC.PC.9 Work process** (QA.1, QA.2).
   - **Unit files.** Each unit of work has one file, `docs/agent/records/work/WU-nnnn-<slug>.md`, from the template in that folder. It records the plan (scope, definition of done, acceptance criteria) before execution, then the execution log, the review and the closing audit (DoD met or not, with evidence).
   - **Queue.** `docs/agent/records/work/queue.md` lists units in priority order.
   - **Starting work.** An agent MAY open, plan and execute any unit in the queue, and MAY add units within scope (LPC.PC.1).
   - **Splitting work.** A unit that grows past one coherent change SHOULD be split.
10. **LPC.PC.10 Stopping rule** (QA.3). A unit of work halts and is reported to the human owner (GUARD.3) when the first of these occurs:
    - (a) three attempts at the same failing approach without new information;
    - (b) four hours of agent working time without measurable progress toward its definition of done;
    - (c) agent operating cost reaching twice the unit's recorded estimate, where one was recorded (LPC.PC.23).

    A continuation unit inherits the bound. Only the human owner changes this rule or extends a bound, by ledger transaction.
11. **LPC.PC.11 Review** (QA.7, QA.8). Every change is reviewed, before it is merged to `main`, by an actor other than its author, and the review is recorded in the unit file. Independence is proportioned as follows:

    | Change | Reviewer |
    | --- | --- |
    | Development code, tests, tools, docs | Any other actor, including an agent session or subagent with a fresh context that did not author the change |
    | Code that computes a verdict, statistic or acceptance criterion; the seed and provenance machinery; dependency additions | The above, plus the human owner before the freeze |
    | Governance (any file in `docs/agent/governance/`) | The human owner, at adoption |
12. **LPC.PC.12 Verification cadence** (VV.8, RSRC.11, RSRC.12, GOV.7).
    - **During development.** Each change runs the smallest set of checks that establishes the evidence it needs: the affected unit tests, plus the smoke preset when the pipeline is touched.
    - **At the freeze.** The full suite, validation gate V1–V7 and the regression comparison against the pilot on `DEV-0` run, within the tolerances recorded in WU-0003.

    Deferral NEVER becomes omission: the freeze does not proceed without them.
13. **LPC.PC.13 Regeneration and promotion** (QA.9, QA.11, PRIME.3).
    - **Regeneration.** A confirmatory result is regenerated from its recorded inputs before promotion: by the human owner, or by an agent session other than the one that produced it, under its own per-action authorization.
    - **Promotion** is the human owner's ledger transaction. An agent MAY propose it.
    - **Unpromoted outputs.** Until promotion, every output is marked `UNPROMOTED` in its report header. A development output is additionally marked `DEVELOPMENT (DEV-n): not a hypothesis test`.
14. **LPC.PC.14 Defect tracking** (QA.4, QA.5, QA.6). Defects are recorded in `docs/agent/records/defects.md` with:
    - an identifier `DEF-nnnn`;
    - what the defect affects;
    - whether it is blocking (Normative Language);
    - its status and resolution schedule.

    Blocking defects are resolved before the freeze. Tracked defects are resolved before promotion, or recorded as known limitations in the report (INTPR.10).
15. **LPC.PC.15 Correction propagation** (QA.13, QA.14). Every reported or cited result is listed in `docs/agent/records/results-manifest.md` with its inputs: seed id, commit, configuration and environment.

    When a result, a component or a decision is found wrong, the actor that finds it:
    - identifies the dependents from the manifest and the provenance;
    - records the correction in `defects.md`;
    - notifies the human owner, who notifies the student and other relying parties;
    - re-verifies, corrects or withdraws each dependent.

    Records are amended, never replaced.
16. **LPC.PC.16 Incidents** (QA.15). A defect that reached a reported result or a release is recorded as an incident in `docs/agent/records/incidents.md`. The record gives the root cause, the check added so it is caught next time, and whether governance failed. A governance failure is reported to the custodians.
17. **LPC.PC.17 Dependency management** (REPRO.9, SIMPL.4).
    - **Pins.** `requirements.txt` pins every direct dependency to an exact version.
    - **Reasons.** `docs/agent/records/dependencies.md` records why each dependency is carried and its license.
    - **Adding or removing a dependency** is a recorded decision in that file.
    - **Review.** The human owner reviews the pins at the freeze and at least every three months while the project is active.
18. **LPC.PC.18 Provenance and determinism** (REPRO.1–REPRO.4, REPRO.11, INTPR.9).
    - **Provenance in every output.** Every `results.json` and report written by the code records:
      - the master seed id (never the confirmatory seed's value before promotion);
      - the code commit and whether the working tree was dirty;
      - the preset and the full configuration;
      - Python and package versions;
      - device type (CPU or GPU model) and the JAX precision mode.
    - **Determinism.** GPU reductions are not guaranteed bitwise reproducible, so the project declares outputs reproducible within the tolerance recorded in WU-0003 (REPRO.3). Bitwise identity is expected on CPU for the same environment.
    - **Agent sessions** record their model identifier and the governance revision they ran under (the latest adoption entry's sequence number) in the unit file (REPRO.11).
19. **LPC.PC.19 Retention** (REPRO.12, REPRO.13).
    - **What is kept.** Records, governance, the ledger and every cited result are kept for two years after the last science-fair use or publication of the study, whichever is later, in JSON, CSV, Markdown or NPZ (an open format).
    - **Backup.** The owner keeps an independent copy of `docs/` and of cited results, outside the working machine.
    - **Regenerable outputs.** Development outputs not cited by a record MAY be deleted as regenerable (LPC.EXC.2).
20. **LPC.PC.20 Working-notes workspace** (INTPR.5). `docs/agent/notes/` holds working notes, plans and context for later recovery.
    - It carries no instruction authority (PRIME.11) and is never the only record of anything a reader of the code needs.
    - Notes worth keeping are moved into code comments, the unit file, a decision record or the study documents.

## 5. Numerical code

21. **LPC.PC.21 Numerical evidence** (VV.1, VV.7, VV.10, PRIME.2, PRIME.4, INTPR.4).
    - **(a) Every test names its reference.** Acceptable references:
      - analytic solutions;
      - finite differences against derivatives;
      - independent algorithms (for example a second integrator, or a brute-force search against the k-d tree);
      - exact distributions or the published values cited in the code;
      - manufactured solutions.

      A test against the code's own earlier output is labeled a regression guard and is not correctness evidence.
    - **(b) Tolerances are justified** in the test, from the method's order, conditioning or sampling error, and fixed before the result is seen.
    - **(c) Invariants are asserted:** shapes, finiteness, probabilities in [0, 1], weights in [0, 1], monotone survival curves, and the convergence check of V4.
    - **(d) Visible handling of bad values.** Every clipping, replacement of a non-finite value, fallback, or non-converged solve is counted and reported in the results and the run log, never silent. The known cases (estimates replaced by the invariant mean, errors clipped at 10 σ_x, the regime-count fallback) are DEF-0001.
    - **(e) Units and conventions are declared once** where every reader passes: time in steps and in Lyapunov times, noise as a fraction of σ_x, whitened state coordinates. Silent conversion is a defect.
    - **(f) float64 throughout.** A change of precision is a recorded decision.
22. **LPC.PC.22 Compute** (RSRC.1–RSRC.4, PRIME.8).
    - **Recording.** Each run records wall-clock time and peak memory, and the device it ran on.
    - **Optimization** is undertaken only against a measured shortfall from a recorded budget (RSRC.4).
    - **Current budget** for the full preset: completes within 12 hours on the owner's GPU workstation.

## 6. Agents

23. **LPC.PC.23 Agent operating cost** (GUARD.14, PRIME.8, GUARD.15).
    - **Discipline:** `<owner to set at adoption: for example, "use the included usage of the owner's Claude subscription; no pay-as-you-go API spend">`.
    - **Until it is set**, an agent uses the least costly configuration able to complete each unit reliably, and records a rough cost estimate in the unit file when the unit is expected to be large.
    - **Subagents.** Agents SHOULD dispatch simple, well-specified edits to smaller models.
24. **LPC.PC.24 Autonomy** (GUARD.1, PRIN.10).
    - **Free actions.** Within the provisioned environment, an agent takes the free actions listed in the agent instructions (LPC.AI.3) without asking.
    - **Authorized actions.** It takes the actions the adopted authorizations cover without asking.
    - **Everything else** is referred under PRIME.14.

    The human owner intends autonomous development. An agent SHOULD batch referrals into one findings and justification statement per unit, rather than stopping for each question, and SHOULD continue with other units in the queue while a referral is pending.
25. **LPC.PC.25 Review of this constitution** (GOV.46, GOV.47). The human owner rereads this document at the freeze and at the end of the project. Each review records in the ledger whether a provision was routinely waived, ignored or found ambiguous, and whether governance failed.

## Revision history

| Revision | Date | Change |
| --- | --- | --- |
| 0.1 (draft) | 2026-10-10 | Proposed by Claude for adoption by the human owner. |
