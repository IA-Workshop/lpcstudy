"""Simulation tests of the study's basic bootstrap confidence intervals (cases C1, C3 and C1s).

A 95% confidence interval should contain the true value in about 95% of repeated
experiments; that fraction is its "coverage". The study builds intervals with a
moving-block bootstrap: resample the series in blocks of consecutive values (so that
time dependence is kept), recompute the statistic many times, and take percentiles of
the results. This module checks the coverage of those intervals in the simplest cases,
where the true answer is known exactly: C1 is the mean and C3 the median of a series
with known autocorrelation (WU-0006.2). It calls ``bootstrap_values`` and
``percentile_interval`` from ``lpcstudy.statistics``. The simulation tools are in
``tests/slow/wu0006_harness.py`` and the independent reference tables in
``tests/slow/wu0006_reference.py``. The rest of this docstring is the detailed
specification, kept for reviewers.

Slow tier: R = 1000 replications of 2000 resamples per (case, phi), run once on a pool of single-thread
workers (about 15 s per run). The harness and the reference tables are in ``wu0006_harness`` and
``wu0006_reference``.

**Procedure.** ``bootstrap_values`` and ``percentile_interval`` (the body of ``block_bootstrap_counted``)
with blocks of 5 and B = 2000, at 95% and at 1 - 0.05/3 from the same resamples. **Data.** A stationary
Gaussian AR(1) series with lag-1 autocorrelation phi (0 and 0.3), 500 states. **Truth.** 0, analytic
(C1 the mean; C3 the median of a symmetric law). **Seeds.** ``make_rng(6006, "wu0006", case, phi, r, .)``.

**Reference and prediction** (applied-mathematician's independent simulation, scratch seed 20261011,
R_ref 20 000 to 40 000, fixed before any result): coverage at 95% / 98.3% and the probability that the
ROADMAP bound fails for correct code.

| case | phi | 95% | 98.3% | P(A1 fails) | P(A2 fails) |
| --- | --- | --- | --- | --- | --- |
| C1 | 0 | 0.9451 (0.0011) | 0.9800 (0.0007) | 0.02 | 0.03 |
| C3 | 0 | 0.9448 (0.0016) | 0.9807 (0.0010) | 0.02 | 0.03 |
| C1 | 0.3 | 0.9257 (0.0013) | 0.9695 (0.0009) | 0.67 | 0.63 |
| C3 | 0.3 | 0.9292 (0.0018) | 0.9732 (0.0011) | 0.51 | 0.36 |
| C1s | 0.1 | 0.9398 (0.0017) | 0.9794 (0.0010) | reported only | |
| C1s | 0.2 | 0.9328 (0.0018) | 0.9740 (0.0011) | reported only | |

The block-5 bootstrap captures a long-run variance factor of about 1.60 against the true 1.857 at
phi = 0.3 (a property of the method, not of the code), so a failed A1 or A2 at phi = 0.3 is a predicted
finding of class "method", not a defect.

**Assertion groups** (each (case, phi) is a separate test, so one failure hides no other):

* exact: a regression guard (for these generic cases the harness path is the body of
  ``block_bootstrap_counted``, so the identity in 10 replications is a self-comparison), and no failed
  resamples (A5). Zero tolerance.
* consistency: the observed counts lie in the pre-registered range of the reference (the defect test;
  family-wise false alarm at most 3.5% over all 70 ranges of WU-0006).
* roadmap: A1 (count of covering intervals at 95% >= 930 of 1000, i.e. nominal - 3 SE = 0.929324,
  SE 0.00689) and A2 (>= 972, 0.971188, SE 0.00405). Under Option C (``ASSERT_ROADMAP_BOUNDS = False``,
  in force since 2026-10-12, DEC-0026 item 2) these are recorded characterization rows: the outcome is
  computed, written to the results table and shown as a pytest warning, never asserted (asserted only
  under Option K, ``ASSERT_ROADMAP_BOUNDS = True``). The exact and consistency groups are asserted in
  both positions.

The outcomes of all groups are written to ``runs/tests/wu0006_coverage_statistics.json``.
"""

from __future__ import annotations

import pytest

import wu0006_harness as wu

CASES = ("C1", "C3")


@pytest.fixture(scope="module")
def pool():
    """Start the pool of single-thread worker processes, shared by the whole module."""
    with wu.worker_pool() as shared:
        yield shared


@pytest.fixture(scope="module")
def cache() -> wu.RunCache:
    """Return the on-disk cache that keeps each simulation result for the module's tests."""
    return wu.RunCache("coverage_statistics")


@pytest.mark.parametrize("phi", wu.PHIS)
@pytest.mark.parametrize("case", CASES)
def test_exact_checks(pool, cache: wu.RunCache, case: str, phi: float) -> None:
    """Regression guard: identity with ``block_bootstrap_counted`` and check A5.

    The identity is bitwise, over 10 replications. A5 requires 0 failed
    resamples in continuous data. For C1 and C3 the harness's path is the body of
    that function, so the identity is a self-comparison, not correctness
    evidence. The evidence is the coverage against the analytic truth and the
    independent reference (the other two tests).
    """
    evaluation = cache.coverage(pool, wu.CaseSpec(case), phi)
    assert not evaluation.exact, "; ".join(evaluation.exact)


@pytest.mark.parametrize("phi", wu.PHIS)
@pytest.mark.parametrize("case", CASES)
def test_counts_are_consistent_with_the_reference(
    pool, cache: wu.RunCache, case: str, phi: float
) -> None:
    """The coverage counts at 95% and 98.3% lie in the pre-registered ranges.

    A range is the central 0.9995 of Bin(1000, p_ref), a binomial count of 1000
    trials, mixed over the reference's Monte Carlo error. A count outside is a
    defect candidate, a DEF of class "code".
    """
    evaluation = cache.coverage(pool, wu.CaseSpec(case), phi)
    assert not evaluation.consistency, "; ".join(evaluation.consistency)


@pytest.mark.parametrize("phi", wu.PHIS)
@pytest.mark.parametrize("case", CASES)
def test_roadmap_coverage_bounds(
    pool, cache: wu.RunCache, case: str, phi: float
) -> None:
    """A1 (>= 930 of 1000 at 95%) and A2 (>= 972 of 1000 at 1 - 0.05/3): nominal - 3 SE, R = 1000.

    The truth is 0 (analytic). The predicted P(fail) is in the module table. A
    failure at phi = 0.3 is a finding of class "method" recorded in the unit Log,
    never tuned away (PRIME.2). Under Option C (``ASSERT_ROADMAP_BOUNDS = False``,
    as shipped) the outcome is only recorded and warned about, never asserted;
    under Option K (True) a failed bound raises.
    """
    evaluation = cache.coverage(pool, wu.CaseSpec(case), phi)
    outcome = wu.enforce(evaluation.roadmap)
    assert outcome in ("pass", "fail")


@pytest.mark.parametrize("phi", (0.1, 0.2))
def test_c1s_dependence_curve_is_reported(
    pool, cache: wu.RunCache, phi: float
) -> None:
    """C1s: the coverage of the mean at lag-1 0.1 and 0.2, reported for the owner, not asserted.

    Reference (R_ref 20 000): 0.9398 / 0.9794 at 0.1 and 0.9328 / 0.9740 at 0.2 (95% / 98.3%). The
    row records the deviation in standard errors; only the exact checks are asserted.
    """
    evaluation = cache.coverage(pool, wu.CaseSpec("C1", tag="s"), phi)
    assert (
        evaluation.row["asserted"] is False
        and "z_vs_reference" in evaluation.row
    )
    assert not evaluation.exact, "; ".join(evaluation.exact)
