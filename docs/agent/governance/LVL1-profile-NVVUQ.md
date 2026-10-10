# LVL1 Profile NVVUQ: Numerical Verification, Validation and Uncertainty Quantification

| Field | Value |
| --- | --- |
| Level | LVL1 profile (GOV.16, GOV.23–GOV.31) |
| Mnemonic | NVVUQ (to be entered in the mnemonic register by ledger transaction, GOV.37). Provisions are `NVVUQ.n`. |
| Parent | LVL0 Constitution for Computational and Cyber-Physical Systems, r1.5 |
| Status | **Proposed** 2026-10-10 by Claude (claude-opus-5-5) for adoption by the custodians (GOV.28, GOV.41). Not in force until adopted. |
| Drafted for | First applied to the LPC study (`lpcstudy`). How that project meets each provision is in `NVVUQ-instantiation-LPC.md` (LVL3). |

This profile states the domain obligations for computations whose numerical results are relied upon. Every provision only tightens the LVL0 provisions it cites (PRIME.15, GOV.26). It names no language, library, tool or method (GOV.18). Where it says "for example", the example is informative.

## 1. Selector and scope

**NVVUQ.1 Selector** (GOV.25, GOV.26). This profile binds a project whose classification records any of these work attributes:

- (a) numerical solution of differential, integral or algebraic equations;
- (b) numerical optimization, estimation or inversion;
- (c) stochastic simulation or Monte Carlo sampling;
- (d) statistical inference whose conclusions rest on computed data.

The selector is decidable from the classification attribute `domain` (GOV.24).

**NVVUQ.2 Relation to LVL0.** This profile adds no safeguards. GUARD and the prime directives apply unchanged. Its provisions rank with the Article they cite (GOV.5), mostly VV and REPRO, and are waivable only as those provisions are (GOV.17, GOV.44).

## 2. Terms

These terms are defined for this profile only. They do not redefine LVL0 terms (GOV.26).

| Term | Meaning |
| --- | --- |
| Quantity of interest (QoI) | A computed number, or set of numbers, that a reported result or decision rests on |
| Code verification | Evidence that an algorithm is implemented correctly: the program solves the stated mathematical problem with its designed accuracy |
| Solution verification | Evidence of the numerical error in a particular computed QoI |
| Numerical error | Discretization error, iterative or convergence error, and round-off error in a QoI |
| Sampling error | Error in a QoI from a finite number of random draws or samples |
| Formal order | The rate at which a method's error decreases with resolution, according to its theory |
| Observed order | That rate as measured from a refinement study |
| Reference solution | An exact, manufactured, analytic or independently computed solution of known accuracy |
| Uncertainty budget | The itemized sources of uncertainty in a QoI, each with its estimated size and how it was estimated |
| Aleatory uncertainty | Variability inherent in the modeled process or data |
| Epistemic uncertainty | Uncertainty from lack of knowledge, including model-form error |
| Confirmatory computation | A computation whose result tests a criterion fixed before it was seen (VV.3) |
| Exploratory computation | Any other computation |
| Coverage | The long-run fraction of intervals from a procedure that contain the true value |

## 3. Specification of what is computed

**NVVUQ.3 QoIs declared** (VV.3, INTPR.4, INTPR.9). Before a QoI is computed for reliance, it is declared with five things:

- its definition;
- its units and conventions;
- the acceptance criteria that will judge it;
- the error or uncertainty that would change a decision;
- the decision the QoI informs.

**NVVUQ.4 Domain of validity** (INTPR.10). Each numerical method declares the regime in which its accuracy is established: parameter ranges, step sizes, conditioning, sample sizes and the assumptions of any theorem relied upon. A computation outside that regime is reported as such.

## 4. Code verification

**NVVUQ.5 Order and exactness tests** (VV.1, VV.6, VV.7). Every numerical method that bears on a QoI is verified by at least one of the following:

- an observed-order test that matches the formal order within a stated tolerance;
- an exact or manufactured-solution test;
- comparison with an independent implementation or algorithm.

The test names its reference and justifies its tolerance from the method's theory.

**NVVUQ.6 Derivatives** (VV.1). Every computed derivative, Jacobian or sensitivity that bears on a QoI is checked against an independent computation, such as finite differences, complex step or an analytic form. The tolerance is justified from the step size and the conditioning.

**NVVUQ.7 Statistical procedures** (VV.1, VV.4). Every estimator, test or interval procedure that bears on a reported result is verified on synthetic data with a known truth:

- point estimators for bias;
- tests for size;
- interval procedures for coverage.

The check is run at the sample sizes and dependence structure of use, with its own Monte Carlo error stated. At CSQ2 and more severe classes this is required before confirmatory use. At CSQ3 and CSQ4 it is recommended (SHOULD).

**NVVUQ.8 Random streams** (DSGN.17, REPRO.1, REPRO.3). Randomness enters through seeded streams whose independence across purposes is designed and declared. Every result records the seeds that produced it.

## 5. Solution verification

**NVVUQ.9 Numerical error estimated** (VV.1, VV.5, PRIN.3). For each reported QoI, the discretization, iterative and round-off errors are each:

- estimated, for example by refinement, iteration-count or precision studies;
- shown to be small compared with the acceptance tolerance or the sampling uncertainty, or else included in the uncertainty budget.

An unestimated numerical error leaves the QoI unverified (PRIME.3).

**NVVUQ.10 Convergence evidence** (VV.1).

- **Iterative solvers** report their stopping criterion and achieved residual.
- **Sampling-based estimates** report their sampling error, and convergence in the number of samples is shown where the sample count was chosen by the project.

**NVVUQ.11 Nonconvergence and special values** (PRIME.4). Every nonconvergence, non-finite value, clamp, fallback or replacement is counted and reported with the result it affects. None is silent.

**NVVUQ.12 Precision and determinism** (REPRO.2, REPRO.3).

- **Precision.** The floating-point precision of each stage is declared, and a change of precision is a recorded decision.
- **Variation.** Run-to-run variation from parallel or accelerator execution is measured and declared as a tolerance before confirmatory use.

## 6. Validation

**NVVUQ.13 Referent and status** (VV.4, VV.5).

- **With a real-world referent:** validation compares QoIs with it using a pre-specified metric and criterion.
- **Without one** (for example a numerical experiment on a mathematical model, where the model is the object of study): the report says that validation against a real-world referent does not apply. It then reports the validation that does apply:
  - the model's agreement with established reference values for the same model, confirmed under VV.2;
  - whether the hypotheses of each theorem relied upon hold in the regime computed.

**NVVUQ.14 Theorem hypotheses** (VV.9, INTPR.10). Where a computation tests or relies on a theorem, each of the theorem's hypotheses is checked numerically in the regime of use, or declared as an axiom (VV.9). A result where a hypothesis fails is reported as outside the theorem's domain, not as a counterexample to it.

## 7. Uncertainty quantification

**NVVUQ.15 Uncertainty budget** (VV.5, INTPR.9). Every reported QoI carries an uncertainty budget that lists:

- sampling error;
- numerical error;
- estimator or proxy error;
- the epistemic sources the project can identify, including model-form assumptions.

Each item gives its size, or "not estimated" with the reason. Aleatory and epistemic contributions are reported separately where both are present.

**NVVUQ.16 Intervals** (VV.3, VV.7). Every interval states:

- its procedure;
- its level;
- the dependence it assumes (for example independence or block structure);
- the multiplicity adjustment, if any.

A figure or table that shows intervals says what they are.

**NVVUQ.17 Sensitivity to choices** (VV.1, INTPR.10). For each analysis choice that can move a reported QoI or verdict, sensitivity is reported, or the choice is declared fixed with its reason. Such choices include embedding parameters, tolerances, sample sizes, model parameters and estimator settings.

## 8. Inference from computed data

**NVVUQ.18 Confirmatory and exploratory separation** (VV.3, QA.12, PRIME.2). Confirmatory computations use inputs that are committed before any confirmatory output exists, such as random seeds and data splits. The commitment is recorded so that it is verifiable afterward. No input to a confirmatory computation is chosen, repeated or replaced after its output is seen. Exploratory results are labeled as exploratory wherever they are reported.

**NVVUQ.19 Decision rules** (VV.3). Each confirmatory criterion has a decision rule fixed in advance that maps an interval to a verdict. Ruling to "inconclusive" is a stated outcome. A claim of equivalence or absence of an effect requires an interval inside a stated margin; a failure to reject is never enough.

**NVVUQ.20 Precision planning** (QA.1, RSRC.1). Before a confirmatory computation, the expected interval width of each primary criterion is estimated, for example from a pilot or a development rehearsal on separate inputs. The record states which verdicts are reachable at the planned size.

**NVVUQ.21 Multiplicity** (VV.3). The family of primary criteria and its error control are stated before the confirmatory computation. Secondary criteria are labeled as such.

## 9. Reporting

**NVVUQ.22 Reported QoIs** (VV.5, INTPR.9, REPRO.4). Every reported QoI is given with:

- its value;
- its interval or uncertainty budget;
- its numerical-error estimate;
- its verification and validation status (VV.5);
- whether it is confirmatory or exploratory;
- the provenance of its inputs (seeds, revision, environment).

## 10. Proportionality

**NVVUQ.23 Burden by consequence class** (GOV.11, PRIN.9). The provisions above apply at CSQ2. At other classes the table below sets the burden. "Required" means SHALL; "recommended" means SHOULD (PRIN.10).

| Provision | CSQ4 | CSQ3 | CSQ2 | CSQ1 and CSQ0 |
| --- | --- | --- | --- | --- |
| NVVUQ.3–4 QoIs, domain | recommended | required | required | required |
| NVVUQ.5–6 code verification | the floor's basic tests (GOV.10) | required for new methods | required for every method that bears on a QoI | required, with independent review of each test (QA.8) |
| NVVUQ.7 statistical procedures | — | recommended | required before confirmatory use | required, and repeated after any change to the procedure |
| NVVUQ.8, 11, 12 streams, special values, precision | required (they instantiate PRIME.4 and REPRO) | required | required | required |
| NVVUQ.9–10 solution verification | — | recommended | required | required, with independent regeneration (QA.9) |
| NVVUQ.13–14 validation | — | recommended | required | required |
| NVVUQ.15–17 UQ | — | sampling error only | full budget | full budget, with independent review |
| NVVUQ.18–21 inference | labeling only | labeling only | required | required |
| NVVUQ.22 reporting | labeling only | required for anything shared beyond the author | required | required |

## Revision history

| Revision | Date | Change |
| --- | --- | --- |
| 0.1 (proposed) | 2026-10-10 | Drafted by Claude for the custodians' review, at the request of the LPC project's human owner. |
