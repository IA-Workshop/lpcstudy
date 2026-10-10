---
name: uq-budget
description: "Assembles the uncertainty budget for a reported quantity of interest (sampling, numerical, proxy or estimator, epistemic) in the form NVVUQ.15 requires. Use when preparing any reported number, table or figure, and for WU-0008."
argument-hint: "[QoI]"
---

# Uncertainty budget for $ARGUMENTS

Fill one table per QoI. Every row gives a size, or "not estimated" with the reason. Separate aleatory items from epistemic ones.

| Source | Type | How estimated | Size (same units as the QoI) | Included in the reported interval? |
| --- | --- | --- | --- | --- |
| Oracle Monte Carlo (M draws per state) | aleatory | convergence check V4 / bootstrap over draws | | no (state-level); propagated into the state statistic |
| Sampling of test states | aleatory | moving-block bootstrap (block 5, 2000 resamples) | half-width | yes |
| Bootstrap Monte Carlo error | numerical | resampling of the endpoints, or the binomial error of the percentile | | no; must be small against the half-width |
| Discretization (RK4) | numerical | step halving (V6); the QoI is defined on the discrete map (LPC.NV.1) | | no |
| Iterative (Levenberg–Marquardt) | numerical | residual and iteration-count study; wrong-basin fraction | | no |
| Round-off | numerical | float64 and conditioning argument | | no |
| Proxy error (deployable against oracle) | estimator | proxy-oracle rank correlation; A4 against A4o | | reported separately |
| Model form: exact model, three systems, scalar observable | epistemic | not estimated; stated as a limitation (v3 §8) | — | no |

## Rules

- **Numerical rows** need evidence, or the QoI is labeled unverified (PRIME.3, NVVUQ.9). Each numerical row should be at least 10 times smaller than the sampling half-width; otherwise say so and widen the interval or refine.
- **Units and conventions:** state the interval level and the dependence assumption under the table (NVVUQ.16).
- **Seeds:** state which seed produced each number. Development numbers carry the `DEVELOPMENT (DEV-n)` label.
