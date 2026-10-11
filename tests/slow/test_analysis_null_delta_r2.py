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
learner pays for an irrelevant feature): reference (A9, phi 0) -0.0024 (logit) and -0.0032 (indicator), positive in
17% and 22% of training sets.

**Reference** (addendum A9, 2026-10-11: production ``qn_profile_block`` at these sizes, R_ref = 1000 per
phi, scratch seed 20261014; it replaces the R_ref = 200 values of the review's M4 and was made after
run 2, VV.3, without using the run-2 counts). Rates with their standard errors (0.003 to 0.009), the
probability that the bound fails at R = 500 for correct code, and the consistency range of the count
out of 500:

| phi | target | N1: P(0 in CI) | P(N1 fails) | N1 range | N2: P(lo > 0) | P(N2 fails) | N2 range | N3: coverage | P(N3 fails) | N3 range |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | logit | 0.919 | 0.54 | 431-483 | 0.016 | 0.000 | 0-23 | 0.941 | 0.066 | 446-490 |
| 0 | indicator | 0.933 | 0.19 | 440-487 | 0.019 | 0.001 | 0-25 | 0.945 | 0.033 | 448-491 |
| 0.3 | logit | 0.924 | 0.41 | 434-484 | 0.009 | 0.000 | 0-16 | 0.946 | 0.028 | 449-491 |
| 0.3 | indicator | 0.926 | 0.35 | 436-485 | 0.014 | 0.000 | 0-21 | 0.945 | 0.033 | 448-491 |

**Rows.**

* N1 (ROADMAP as written): the 95% interval contains 0, for ``logit_w_interior`` and
  ``w_zero_indicator``, >= 461 of 500 (0.921, SE 0.00975). Predicted P(fail) 0.19 to 0.54 per row,
  an estimand mismatch, not a defect.
* N2: false "distinct", P(lower bound > 0) <= 22 of 500 (0.045946, SE 0.00698). Predicted P(fail)
  at most 0.001 per row.
* N3: coverage of Delta_cond, truth computed from the returned fitted pair on 10^5 fresh i.i.d.
  stationary states (Monte Carlo error 0.05 of the half-width on average), >= 461 of 500. Predicted
  P(fail) 0.03 to 0.07 per row (the block-5 percentile interval covers Delta_cond at 0.941 to 0.946,
  2.0 to 2.4 SE above the bound).
* The nominal bounds of N1, N2 and N3 are asserted while ``ASSERT_ROADMAP_BOUNDS`` is True (Option K;
  DEC-0018, main-session decision after addendum A9; before it N2 and N3 were always asserted).
  Over the 8 N2 and N3 rows a correct implementation fails at least one with probability about 0.15 per
  run (almost all from N3): such a failure at a count inside its range is a predicted finding of class
  "method", not a defect.
* Consistency (always asserted, any switch position): each of the 12 counts lies in its range above,
  the defect test; family-wise false alarm at most 12 x 0.0005 = 0.6%. The ranges were fixed AFTER
  the run-2 counts were known (VV.3), and a rerun with the same design and seeds is bitwise
  deterministic, so their passes in run 7 (the run-2 counts lie inside all 12) are a determinism check
  and a regression guard, not independent confirmation that they detect a defect. Their first
  genuinely pre-registered use is the first run whose counts were not known when they were fixed (for
  example after a change of seed derivation).
* Exact: refitting ``qn_regressor(seed)`` on the same data reproduces the returned ``delta_r2``
  bitwise in every replication.

Failed resamples, the reading frequencies, Delta_cond moments and the half-width are written to
``runs/tests/wu0006_delta_r2.json`` and compared with the reference there.
"""

from __future__ import annotations

import pytest

import wu0006_harness as wu
import wu0006_reference as ref


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
@pytest.mark.parametrize("target", wu.DELTA_TARGETS)
@pytest.mark.parametrize("row", ("n1", "n2", "n3"))
def test_count_is_consistent_with_the_reference(pool, cache: wu.RunCache, row: str, target: str,
                                                phi: float) -> None:
    """The count of N1, N2 or N3 lies in its reference range (addendum A9: central 0.9995 of
    Bin(500, p_ref) mixed over the reference's error, R_ref = 1000). These ranges were fixed after
    run 2's counts were known (VV.3), so until a run whose counts are not known in advance a pass is
    a regression guard (determinism), not independent confirmation. Always asserted; a count outside
    is a defect candidate (DEF class "code")."""
    evaluation = cache.delta(pool, phi)
    assert evaluation.consistency_rows[f"{row}|{target}"] is None, \
        evaluation.consistency_rows[f"{row}|{target}"]


@pytest.mark.parametrize("phi", wu.PHIS)
def test_roadmap_false_distinct_rate_and_conditional_coverage(pool, cache: wu.RunCache,
                                                              phi: float) -> None:
    """N2 (P(lower > 0) <= 22 of 500) and N3 (coverage of Delta_cond >= 461 of 500), both targets.

    Nominal -/+ 3 SE with R = 500: 0.045946 and 0.92076 (rounded up to the ROADMAP's 0.921). Predicted
    P(fail) per row: N2 at most 0.001, N3 0.03 to 0.07 (module table). Under the switch since
    addendum A9: asserted under Option K, only recorded under Option C."""
    evaluation = cache.delta(pool, phi)
    assert wu.enforce(wu.delta_rows(evaluation, "n2", "n3")) in ("pass", "fail")


@pytest.mark.parametrize("phi", wu.PHIS)
def test_roadmap_interval_contains_zero(pool, cache: wu.RunCache, phi: float) -> None:
    """N1 as the ROADMAP words it: the 95% interval contains 0 in >= 461 of 500 replications.

    Predicted P(fail) 0.19 to 0.54 per row (estimand mismatch: the interval is for Delta_cond, whose
    mean is negative under the null). A failure is a finding for the owner, who may amend the ROADMAP
    row (DEC-0018), and is never tuned away. Under Option C the outcome is only recorded."""
    evaluation = cache.delta(pool, phi)
    assert wu.enforce(wu.delta_rows(evaluation, "n1")) in ("pass", "fail")


def test_reference_table_is_the_a9_table() -> None:
    """The study reads its references from ``wu0006_reference`` (a change there selects this file):
    4 (phi, target) cells x 3 rows = 12 ranges, from R_ref = 1000 (addendum A9)."""
    assert ref.DELTA_R2_REFERENCE_R == 1000
    assert sorted(ref.DELTA_R2_REFERENCE) == [(f"{phi:g}", target) for phi in wu.PHIS
                                              for target in wu.DELTA_TARGETS]
    assert sum(len(cell[row]) == 4 for cell in ref.DELTA_R2_REFERENCE.values()
               for row in ("n1", "n2", "n3")) == 12
