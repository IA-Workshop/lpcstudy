---
name: convergence-study
description: "Designs and runs a refinement or convergence study (step size, iterations, number of draws or samples) and reports observed order and an error estimate for a quantity of interest (NVVUQ.9–10). Use for code verification of an integrator or solver, or solution verification of a reported QoI."
argument-hint: "[quantity] [parameter to refine]"
---

# Convergence study: $ARGUMENTS

1. **Fix the QoI and the refinement parameter** before running. Typical parameters in this project:
   - the RK4 internal step;
   - the Levenberg–Marquardt iteration count;
   - the number of oracle draws M;
   - the bootstrap resamples;
   - the number of test states.
2. **Choose at least three levels** with a constant ratio r, usually 2: h, h/r, h/r².
3. **Compute the QoI at each level** on the same development seed. Common random numbers isolate the refinement.
4. **Deterministic refinement** (step size, iterations):
   - observed order `p = log(|q_h − q_{h/r}| / |q_{h/r} − q_{h/r²}|) / log r`;
   - Richardson error estimate for the finest level `e ≈ |q_{h/r} − q_{h/r²}| / (r^p − 1)`.

   Compare p with the formal order: 4 for RK4. A mismatch means a bug, or a solution that is not smooth enough, as at Chua's diode breakpoints.
5. **Stochastic refinement** (draws, samples): report the Monte Carlo standard error at each level and check that it scales as `n^(-1/2)`. The error estimate at the chosen n is the standard error, or a bootstrap half-width for the median or for an interval endpoint.
6. **Report a table:** level, QoI, difference, observed order or standard error. Add one sentence comparing the final error with the acceptance tolerance or with the sampling uncertainty of the QoI. Numerical error well below the sampling uncertainty is the goal (NVVUQ.9).
7. **Put the script** in `tools/` or the unit's folder and commit it, so the study can be regenerated (REPRO.10). Run on development seeds only.
