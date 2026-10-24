# Future analysis: a Bayesian counterpart to the Holm and interval criteria (idea, deferred)

Recorded 2026-10-19 by claude-sonnet-5-5 (main session) at the owner's instruction: "no time right now, but it could be considered in a future analysis". Nothing here is planned work, and nothing here applies to the sealed run.

**Why it came up.** The owner asked whether a Bayesian method could replace the Holm-adjusted p-values and be more mathematically self-consistent. In this study Holm decides only H3a (the log-rank tests between consecutive regimes, v3 section 2 and section 7). Every other criterion is decided by a percentile bootstrap interval (block length 5; the 98.33% level for the primary parts).

**What a Bayesian version could look like** (a sketch from the discussion; no design work has been done):
- H3a: a survival model with a regime effect, and the posterior probability that the regime medians are ordered and separated by a stated margin, in place of Holm over consecutive pairs.
- The interval criteria: credible intervals from a block-aware Bayesian bootstrap.
- The verdict rule: the joint posterior probability that all three systems pass.
- Possibly partial pooling across regimes or systems.

**Conditions for any use.**
- The sealed verdict stays as pre-registered (Holm and the interval rules). A change after the data exist would be post hoc (PRIME.2).
- Any Bayesian analysis is a separate, labeled secondary analysis, with its priors, thresholds and decision rule fixed before anyone opens the sealed numbers, and first tried on development seeds.
- It needs an explicit model of the dependence between neighboring states (the study measured it), and it must report prior sensitivity. The coverage simulations found a small undercoverage of the bootstrap intervals, so a parametric model is not automatically safer.
- No guaranteed long-run false-pass rate comes with a posterior threshold; state this wherever a Bayesian result is shown.

**Side observation, no action.** "Every Holm-adjusted p below 0.01" is stricter than an intersection-union rule needs. It is conservative, it protects against a false pass, and it is part of the pre-registered design.

**If picked up later:** the Fable mathematician can draft the design (model, priors, decision rule, development-seed test plan, pre-specified criteria).
