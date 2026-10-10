---
name: numerical-test
description: "Writes a correctness test for numerical or statistical code with an independent reference and a justified tolerance (LPC.PC.21, NVVUQ.5–7). Use whenever adding or changing a numerical function, estimator or statistic."
---

# Writing a numerical correctness test

A test is a specification plus an oracle (VV.7). A test that compares the code with its own earlier output is a **regression guard**, not correctness evidence. Name it `test_regression_*` and say so in its docstring.

## Choose the reference, strongest first

1. **Exact or analytic:** closed-form solutions, such as a linear ODE `x' = Ax` with solution `expm(A t) x0`, or a known distribution's moments.
2. **Manufactured:** pick the answer, then construct the input that produces it.
3. **Independent algorithm:** brute force against the fast path, such as an exhaustive nearest-neighbor search against the k-d tree, or a grid minimization against a closed-form minimizer.
4. **Order of accuracy:** the observed order from a refinement study matches the formal order (skill `convergence-study`).
5. **Synthetic data with a known truth** for statistics: bias of an estimator, size of a test, coverage of an interval. Use enough replications that the Monte Carlo error is below the tolerance.

## Justify the tolerance in the test

State in a comment where the number comes from:

- **Round-off:** about `n_ops * eps64 * condition_number`.
- **Discretization:** `C * h^p`, with C estimated from a coarser step.
- **Monte Carlo:** `z * sqrt(p(1-p)/R)` for a coverage fraction from R replications, or `z * sd / sqrt(R)` for a mean.

## Template

```python
def test_rk4_observed_order_is_four() -> None:
    """RK4 on x' = A x matches expm(A t) with observed order 4 (NVVUQ.5).

    Reference: exact solution via scipy.linalg.expm (independent of the integrator).
    Tolerance: observed order in [3.8, 4.2]; error at the finest step is dominated
    by truncation (well above 1e-13 round-off), so the slope is well determined.
    """
```

## Checklist

- [ ] The reference is independent of the code under test.
- [ ] The tolerance is justified in a comment and was fixed before the result was seen.
- [ ] Edge cases: boundaries, ties, clipping at 0 and 1, empty or degenerate input. Bad input raises (PRIME.4).
- [ ] float64. Seeds come from `make_rng` or a fixed `np.random.default_rng(<int>)` in the test.
- [ ] It runs in under 5 s, or is marked `@pytest.mark.slow` with the reason.
