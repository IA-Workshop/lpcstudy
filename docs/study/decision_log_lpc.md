# Decision Log: LPC Study (ISEF Mathematics entry)

Records the decisions that fix the scope of the study for the 30 October 2026 proposal and methods submission. Each row gives the decision, who decided it, and why.

## 10 October 2026 (PI sign-off after the adversarial audit)

The audit is in `claude/audit_decision_plan_v1.md`.

| # | Decision | Reason |
|---|---|---|
| D1 | **Keep four local predictability conditions (LPCs).** The fourth, the analog-retrieval noise sensitivity N, stays in the profile, the regime map A5 and H3c. H1f stops being a pass/fail redundancy test. It becomes a pre-registered *estimate*: the oracle-level ΔR² for adding N, with its interval and a reading table. The deployable version is secondary. | This follows the PI's standing instruction: keep the four proposed coordinates, and let the study show whether they reduce to three. It also resolves the contradiction in H1f's predicted direction (audit F2). |
| D2 | **Exact model only for the primary design.** The misspecified-PLP arm becomes future work. The ±5/±10% parameter perturbation stays as a reported robustness variant. | Under model error the seed × amplifier law for PLP collapses. The arm would need its own theory and proxy (audit F7). |
| D3 | **Core systems are Lorenz-63, Rössler and Chua.** Lorenz-96 and the transfer hypothesis T1 are dropped. | Lorenz-96 PLP cannot be interpreted as designed, and the fix would be a research task. T1 rests on a single meaningful target (audit F15). |
| D4 | **The student proves the theorems by hand; Lean is deferred until after the fair results exist.** P1 (the optimal weight plus the horizon-gain bound; L5 + L7) and P2 (retrieval stability and the spread bound; L11(b)) are required. P3 (the regret identity and the measurability floor; L10) is optional. The proposal adds an AI-use and mentor-contribution statement. | The student must be able to defend every proof at the board, and the Lean library is the PI's earlier work (audit F5). |
| D5 | **Pre-registration amendments:** see the list below. | Audit F3, F4, F8–F10, F12. |
| D6 | **Two plans.** Methods v2 and the proposal are on the 30 October critical path. The full preset run, replicates and the thinning check happen after 30 October. | The 30 October deliverable is a proposal and methods description, not results (audit F1). |

**D5 amendments in detail:**

- H2a is reported both restricted (small-error regime) and unrestricted, with the restricted version tested.
- H2b(ii) becomes the mean paired change in w* from N_lib = 10³ to 10⁴ at ρ = 1%. Median and mean curves are reported with intervals.
- The three primary endpoints are H2a, H2b and H3d, at level 1 − 0.05/3.
- H2f is added (secondary): the CP–PLP error correlation rises with N_lib (noise matching), found in the 10 October recheck of the pilot library sweep.
- H3a's 5% regret bar is replaced, and H3d becomes primary.
- H3b and the "partially supported" verdict are dropped.
- H1a becomes validation check V7.
- Library size is renamed N_lib.
- A4f is dropped.

**Schedule.**

| Dates | Owner | Task |
|---|---|---|
| 10/10–10/14 | Claude | Methods v2 and the corrected pilot report |
| 10/14–10/21 | Student | Rewrite the proposal; attempt P1 and P2 by hand with the PI |
| 10/21–10/24 | PI, then Claude | PI review; Claude consistency redline |
| 10/24–10/28 | Student | Final edits and ISEF forms |
| 10/30 | Student | Submit |

## 10 October 2026 (later): clean proposal and methods v3

The clean, scoped proposal and methods is the Claude Doc "LPC Study: Proposal and Methods (v3)":
https://claude.ai/code/artifact/33c9754b-d69c-46f4-8d29-032c71e8443a

It supersedes Methods v2 for the 30 October submission, and its design is the same as Methods v2. It drops the appendices: the amendment log stays in Methods v2 §M14, and the code changes stay in §M15.

**Hypotheses are renumbered in v3.** The code and Methods v2 still use the v2 IDs.

| v3 ID | v2 ID | Role |
|---|---|---|
| H1a | H1b | secondary |
| H1b | H1c | secondary |
| H1c | H1d | secondary |
| H1d | H1e | secondary |
| Q-N | Q-N | estimate |
| H2a | H2a | primary |
| H2b | H2b | primary |
| H2c | H2c | secondary |
| H2d | H2d | secondary |
| H2e | H2f | secondary |
| (reported) | H2e | gain bound, no pass/fail |
| H3a | H3a | secondary |
| H3b | H3c | secondary |
| H3c | H3d | primary |

The rule and experiment IDs change as follows:

- Rules A0–A5, A4o and A* are unchanged.
- Experiments: E5 (shift) is dropped from v3. E6 (regimes) becomes E5, and E7 (robustness) becomes E6.

The code changes after 30 October must adopt the v3 IDs.


## Correction (2026-10-10, later; Claude)

The note above says the code and Methods v2 still use the v2 identifiers. Methods v2 does, but **the code still uses the v1 identifiers** (Methods v1 §M9). The identifier switch in WU-0002 therefore maps from v1 to v3.

| v1 / code | v3 |
| --- | --- |
| H1a (δ ∝ ρ) | V7 (validation check) |
| H1b | H1a |
| H1c | H1b |
| H1d | H1c |
| H1e | H1d |
| H1f | Q-N |
| H2a, H2b, H2c | unchanged |
| H2d | H2d, part (ii) dropped |
| H2e (gain bound) | reported, no pass/fail |
| — | H2e (noise matching; v2 H2f) |
| H3a | H3a (log-rank criterion) |
| H3b | dropped |
| H3c | H3b |
| H3d | H3c |
| T1 | dropped |

The audit found this inconsistency (planner, `ROADMAP.md` §6).
