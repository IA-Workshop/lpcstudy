# WU-0005.6: reading of decision rule R (report-check findings R1 and R7)

Applied-mathematician claude-opus-5-5, 2026-10-14. **DEVELOPMENT (DEV-0).** Requested before the owner decides O5.

**Sources.**
- The rule: rule R, M1, M2 and M7 in the `## Mathematics check` of `docs/agent/records/work/WU-0005.6-lm-doubling.md`.
- The developer's recorded choice: Log, line 420.
- The tool: `classify` and `_structural` in `tools/lm_doubling.py`.
- The report: `docs/study/lm_doubling_dev0_report.md`.
- The review findings: R1 and R7 in `WU-0005.6-report-check.md`.

**Data, read only.** `lpcstudy-wt/run/lm-post/runs/dev/wu0005-6/pilot-compare.json`. The reviewer verified its signed r1 and r2 against the three `results.json` files to 1e-15.

**Script.** A scratch script under `python3 -I`, written independently of the tool. It reclassified the 18 parts from r1, r2, r_A, the verdict sameness and the structural reasons, under two orders:
- order A is the tool's order;
- order B gives M7 precedence.

Order A reproduces all 18 classes and all 18 point-only classes of the tool.

**Scope.** No class, code, preset or test was changed or run. The endpoint question in the request cites M4, but the endpoint item is **M2**. M4 only supplies r_A, which is the same for the full and the point-only classes, so it plays no part here.

## R1. Endpoint noise and class N

**What rule R and M2 guarantee.** Let a part have components C = {pt, lo, hi}, and let P = {pt} ⊂ C. The changes are d1(C) = max over x in C of |Δ1x|, and d2(C) likewise.

1. **Component-set monotonicity: correct.** A maximum over a larger set is at least the maximum over a subset. So d1(C) ≥ d1(P), d2(C) ≥ d2(P), and S(C) ≥ S(P) because S = d1 + 2d2 is non-decreasing in both arguments. The DEV-0 data agree: the inequalities hold in all 18 parts. Hence, relative to the point-only class, using the endpoints:
   - can never make "S < 0.1" true;
   - can never make "d1 ≥ 0.1" false.

   This is the content of M2's "never toward a false negligible **through S**".
2. **The ratio condition is not monotone: M2's general sentence is false.** The condition d2 ≤ d1/2 compares two maxima, and they can come from different components.
   - Adding a component can satisfy it, when an endpoint raises d1.
   - Adding a component can also break it, when an endpoint raises d2.

   So the set of class-N parts is not monotone in the component set. Counterexample in the data, Rössler H2b(ii):
   - point only: |r1_pt| = 2.83e-5 and |r2_pt| = 2.63e-5 > 1.42e-5, so the class is U;
   - with all components: d1 = |r1_lo| = 7.58e-5 and d2 = 2.63e-5 ≤ 3.79e-5, so the class is N.

   The reviewer's R1 is correct.
3. **Relative to the B → ∞ endpoints there is no guarantee for a single realization.**
   - Write each measured endpoint change as Δx + εx, where εx is the zero-mean Monte Carlo error from finite B. The point estimate does not depend on B.
   - By Jensen, E|Δx + εx| ≥ |Δx|. Also E maxₓ ≥ maxₓ E.
   - So noise inflates d1, d2 and S **in expectation only**. A single realization can lower an endpoint's change, and therefore S, below 0.1.
   - Illustration, assuming Gaussian noise: a true endpoint change of 0.12 with paired-change noise of RMS 0.04 (the M2 E2 median-type value at B = 500) is read below 0.1 with probability 0.31.

   "Noise inflates d1 and d2" in M2 is correct as an expectation, and false realization by realization.

**The correct statement** (for the report erratum, replacing "noise pushes toward X or U, never toward N"):

> Using the bootstrap endpoints can only raise d1, d2 and S relative to the point alone. So it never produces N through the S < 0.1 condition, and never removes an X that the point alone gives through d1 ≥ 0.1. The ratio condition d2 ≤ d1/2 compares maxima that may come from different components, so the endpoints can move a part in either direction through it. In Rössler H2b(ii) the lower-endpoint change raised d1, and the part is N with the endpoints but U on the point alone. Relative to infinitely many resamples, endpoint Monte Carlo noise raises d1, d2 and S in expectation but not in every realization.

**Direction of the 7 endpoint-limited parts** (point-only class → full class):

| Direction | Parts |
| --- | --- |
| Toward X through d1 | chua H2a(i) N→X; lorenz63 H2b(ii) N→X; lorenz63 H2a(i) U→X |
| Toward U through the ratio | chua H2a(ii) zero N→U; lorenz63 H2a(ii) interior N→U; rossler H2a(i) N→U |
| Toward N through the ratio | rossler H2b(ii) U→N |

So 6 parts move away from N and 1 moves toward N.

**Faithfulness: yes.** `classify` computes d1 and d2 as maxima over {pt, lo, hi}, and it tests d2 ≤ d1/2 on those maxima. That is what rule R writes. The endpoint-limited label compares the result with the point-only class, as M2 prescribes. Two remarks follow; neither changes a class.

- **The ratio test is weaker than the S bound needs.**
  - The bound S rests on H-geo per component: |e15,x| ≤ |Δ1x| + 2|Δ2x| ≤ S (M1). The max-based ratio test is only the empirical support for H-geo, and it is weaker than a per-component test.
  - Two N parts have a component whose own ratio exceeds ½:
    - rossler H2b(ii), pt, ratio 0.93;
    - chua H2b(ii), lo. This N holds on the point alone too, so it is not endpoint-limited.
- **The Rössler H2b(ii) N is materially safe.** Suppose the pt component kept its ratio q = 0.927 at every later doubling. Then |e15,pt| ≤ |Δ1| + |Δ2|/(1 − q) = 3.9e-4 (in units of hw), against 0.1. Also r_A = 0: no estimate moves by more than 0.1ρν from 60 to 120. This is a sensitivity reading, not a reclassification.

## R7. Order of a structural switch and class X

**What the plan requires.** Rule R gives N as four conditions, and X as any one of three bullets. Neither mentions structural switches. U is "every other case, **including the structural switches of M7**". M7 says the switches "are reported and **make the part class U**".

- A residual class can contain only cases that fail N and X.
- The two sentences are therefore true together only if a structural switch excludes N **and every X bullet**.
- So the plan-faithful order is: **structural switch ⇒ U, before X** (order B).

The plain residual reading, where the switch is ignored and X applies first, makes M7's sentence false whenever d1 ≥ 0.1 or a verdict changes. It is not a consistent reading of the plan.

**The tool differs from the plan.**
- `classify` lets a switch block only N and the third X bullet. X bullets 1 and 2 (a verdict change, d1 ≥ 0.1) still return X. This is order A.
- The developer recorded the choice before any output, on Log line 420, so it was not silent. But the justification given there, "as the table of the Mathematics check reads", has no support: the summary table's M7 row says only "Report additions".
- Round-1 review found the choice "defensible". The author of rule R never adopted it.
- This is therefore **a defect of the tool relative to the plan**, to be reported (a DEF entry or the erratum), and not adopted after the fact.

**Same defect, not triggered on DEV-0.** In `classify`, a non-computable part, such as one with an infinite bound (A3, an M7 switch), returns X if the verdicts differ. M7 gives U. The pairing blockers are also routed as structural reasons, but `pairing_problems` is empty on DEV-0.

**"Membership changes" are not structural switches.** M7 explicitly keeps eligibility and zero-set flips inside d1 as iterative error of the QoI. Only the following are structural:
- the H2a(ii) "one" part existing at some arms only;
- a change in A5's chosen K;
- an infinite bound.

On DEV-0 the membership counts move (for example lorenz63 `n_eligible_states` 327 / 332 / 333). They are correctly not treated as switches. The only structural switch in the data is chua H3c, where K is 8 / 5 / 5.

**Affected parts under the plan-faithful order B** (all 18 recomputed):

| Part | Tool (A) | Plan (B) | LM-row flag | Endpoint-limited |
| --- | --- | --- | --- | --- |
| chua H3c | X, size S·hw = 0.0554 ("estimate under H-geo") | **U**, sizes d1·hw = 0.0549 and d2·hw = 0.00028 (hw = 0.3013), "tail not supported" | no → no (unchanged) | no → no (unchanged: the point-only class is X under A and U under B) |

- No other part changes class. No flag changes, because the flag is "yes" exactly for class N and no N part has a structural switch.
- The counts become N 5, X 6, U 7. For chua they become N 1 / X 2 / U 3; lorenz63 and rossler are unchanged.

**Mathematical opinion, for the owner and not adopted here.** Order A is a defensible rule on the merits:
- X bullets 1 and 2 do not rely on H-geo;
- the "≥ d1·hw" lower estimate needs monotone convergence whether or not a switch occurs;
- only the S·hw estimate and N are invalidated by a discrete switch.

But order A is not the pre-registered rule.
- Recommendation: report chua H3c as U, plan-faithful, and show the tool's X as a secondary reading.
- Adopting order A would be a documented amendment by the owner after results exist, with its effect stated: one class label, no flag.
- Fixing the tool to order B is a developer task with a hand-case test.
- In either case, the chua H3c size line must not read "S·hw (estimate under H-geo)", since an H-geo extrapolation across a discrete switch has no meaning. This agrees with the reviewer's R7.
