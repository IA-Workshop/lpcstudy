"""N1 to N3: the Q-N interval for delta R^2 under the null (WU-0006.3), through ``qn_profile_block``.

Slow tier: R = 500 replications per phi at the full sizes (3000 training, 1000 test states), 2000
resamples of blocks of 5, about 3 s per replication on a single-thread worker.

**Design** (the review's M3 (g), O3). x1, x2, x3, xi, e, e' independent stationary AR(1) with lag-1
phi in {0, 0.3}; x4 = 0.6 x1 + 0.8 xi. L = x1 - 0.5 x2^2 + 0.5 x2 x3 + e; w* = 0 where L is below its
15% quantile (-2.1471), else expit(L); log horizon = 0.5 x1 + 0.3 x3 + 0.5 e'. All three targets depend
on x1..x3 and noise independent of x4, so the population gain of x4 is 0. Training: two independent
paths (2000 + 1000); test: one path of 1000.

**What the interval covers.** The test-state bootstrap holds the two fitted models fixed (v3, Methods
v2 E3), so the interval is for the conditional gain
Delta_cond = [E(Y - f3)^2 - E(Y - f4)^2] / Var(Y) of the fitted pair over a new stationary state in the
target's domain, not for the population gain 0. Under the null Delta_cond has a negative mean (the
learner pays for an irrelevant feature): reference -0.0023 (logit) and -0.0035 (indicator), positive in
15% and 21% of training sets.

**Rows.**

* N1 (ROADMAP as written): the 95% interval contains 0, for ``logit_w_interior`` and
  ``w_zero_indicator``, >= 461 of 500 (0.921, SE 0.00975). Reference P(contains 0) 0.925 (logit) and
  0.890 (indicator): predicted P(fail) 0.42 and 0.88. This is an estimand mismatch, not a defect.
  Asserted while ``ASSERT_ROADMAP_BOUNDS`` is True (Option K).
* N2 (always asserted): false "distinct", P(lower bound > 0) <= 22 of 500 (0.045946, SE 0.00698).
  Reference 0.020 and 0.035; predicted P(fail) < 0.01.
  TO BE REPLACED by the 3000/1000 reference: this P(fail) holds only at 900/1000 states (applied-
  mathematician's addendum A7, item 1); a 3000/1000 reference is being produced.
* N3 (always asserted): coverage of Delta_cond, truth computed from the returned fitted pair on 10^5
  fresh i.i.d. stationary states (Monte Carlo error 0.05 of the half-width on average), >= 461 of 500.
  Reference 0.960 and 0.925 (R_ref 200, indicative); predicted P(fail) about 0.03.
  TO BE REPLACED by the 3000/1000 reference: this P(fail) holds only at 900/1000 states (addendum A7,
  item 2); R_ref 200 is too small to pre-register N2 and N3 at these sizes.
* Exact: refitting ``qn_regressor(seed)`` on the same data reproduces the returned ``delta_r2``
  bitwise in every replication.

Failed resamples, the reading frequencies, Delta_cond moments and the half-width are written to
``runs/tests/wu0006_delta_r2.json`` and compared with the reference there (R_ref 200 at phi = 0).
"""

from __future__ import annotations

import pytest

import wu0006_harness as wu


@pytest.fixture(scope="module")
def pool():
    """Spawned single-thread workers for the module."""
    with wu.worker_pool() as shared:
        yield shared


@pytest.fixture(scope="module")
def cache() -> wu.RunCache:
    return wu.RunCache("delta_r2")


@pytest.mark.parametrize("phi", wu.PHIS)
def test_refit_reproduces_the_returned_gain_bitwise(pool, cache: wu.RunCache, phi: float) -> None:
    """Exact: the refit of ``qn_regressor(seed)`` in the same worker gives ``delta_r2`` bitwise
    (reference: 1000 of 1000 in the review). It is what makes the truth of N3 the conditional gain of
    the very pair that was returned."""
    evaluation = cache.delta(pool, phi)
    assert not evaluation.exact, "; ".join(evaluation.exact)


@pytest.mark.parametrize("phi", wu.PHIS)
def test_false_distinct_rate_and_conditional_coverage(pool, cache: wu.RunCache,
                                                      phi: float) -> None:
    """N2 (P(lower > 0) <= 22 of 500) and N3 (coverage of Delta_cond >= 461 of 500), both targets.

    Nominal -/+ 3 SE with R = 500: 0.045946 and 0.92076 (rounded up to the ROADMAP's 0.921). Always
    asserted, in both Option K and Option C."""
    evaluation = cache.delta(pool, phi)
    assert not evaluation.always, "; ".join(evaluation.always)


@pytest.mark.parametrize("phi", wu.PHIS)
def test_roadmap_interval_contains_zero(pool, cache: wu.RunCache, phi: float) -> None:
    """N1 as the ROADMAP words it: the 95% interval contains 0 in >= 461 of 500 replications.

    Predicted to fail (estimand mismatch: the interval is for Delta_cond, whose mean is negative under
    the null). A failure is a finding for the owner, who may amend the ROADMAP row to N2 and N3
    (DEC-0018), and is never tuned away. Under Option C the outcome is only recorded."""
    evaluation = cache.delta(pool, phi)
    assert wu.enforce(evaluation.roadmap) in ("pass", "fail")
