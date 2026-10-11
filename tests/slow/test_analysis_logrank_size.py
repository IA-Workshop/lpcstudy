"""L1 and L2: size of the H3a log-rank family (WU-0006.3), through ``h3a_logrank``.

Slow tier: R = 2000 families per (row, phi), about 5 s each on the pool.

**Design** (applied-mathematician's M5). 3 regimes of exactly 200 states each, the terciles of an AR(1)
latent; geometric durations with hazard h = 0.0125 per step through a Gaussian copula of an independent
AR(1) latent, censored at 240 steps (4.89% censored in L1); horizons for the regime order from
``kaplan_meier(...).median()`` on an independent calibration draw, as in the pipeline. L1: all hazards
equal (global null). L2: regimes 0 and 1 at h, regime 2 at 2h (partial null; "pass" needs the null pair
to reject). phi (lag-1 of both latents) in {0, 0.3}. ``h3a_logrank`` uses the Holm family of the 2
consecutive pairs at 0.01.

**Reference and prediction** (production ``h3a_logrank``, 40 000 families per row, scratch seed
20261011): L1 FWER (any Holm-adjusted p < 0.01) 0.0105 at phi 0 and 0.0134 at 0.3, P(pass) 0.0010 and
0.0013; L2 P(pass) 0.0115 and 0.0122; variance inflation of the null pair 1.009 and 1.079 (L1), 1.012
and 1.046 (L2). Predicted P(the ROADMAP bound fails | correct code): L1 0.006 (phi 0) and 0.105
(phi 0.3), L2 0.021 and 0.041. The log-rank test assumes independent states; the serially correlated
labels and durations at phi = 0.3 inflate its variance by about 1.08, a property of the method.

**Assertion groups**: exact (L3: no pair left uncomputed, counted, 0), consistency (the pre-registered
ranges of counts of 2000: L1 FWER 7 to 39 at phi 0 and 11 to 47 at 0.3; L1 pass 0 to 9 and 0 to 10; L2
pass 8 to 42 and 9 to 44), and roadmap (each error count <= 33 of 2000: nominal 0.01 + 3 SE, SE 0.00222,
bound 0.016675), asserted while ``ASSERT_ROADMAP_BOUNDS`` is True. Results are written to
``runs/tests/wu0006_logrank.json`` with the censoring fraction and the variance inflation.
"""

from __future__ import annotations

import pytest

import wu0006_harness as wu
import wu0006_reference as ref

ROWS = ("L1", "L2")


@pytest.fixture(scope="module")
def pool():
    """Spawned single-thread workers for the module."""
    with wu.worker_pool() as shared:
        yield shared


@pytest.fixture(scope="module")
def cache() -> wu.RunCache:
    return wu.RunCache("logrank")


@pytest.mark.parametrize("phi", wu.PHIS)
@pytest.mark.parametrize("row", ROWS)
def test_no_pair_is_left_uncomputed(pool, cache: wu.RunCache, row: str, phi: float) -> None:
    """L3: with 200 states per regime and 4.9% censoring no pair has zero log-rank variance or an
    empty regime in 2000 families (reference: 0 in 160 000 families); counted, zero tolerance."""
    evaluation = cache.logrank(pool, row, phi)
    assert not evaluation.exact, "; ".join(evaluation.exact)


@pytest.mark.parametrize("phi", wu.PHIS)
@pytest.mark.parametrize("row", ROWS)
def test_counts_are_consistent_with_the_reference(pool, cache: wu.RunCache, row: str,
                                                  phi: float) -> None:
    """The FWER and P(pass) counts lie in the pre-registered ranges (central 0.9995 of the predictive
    distribution of the count out of 2000 under the reference rate)."""
    evaluation = cache.logrank(pool, row, phi)
    assert not evaluation.consistency, "; ".join(evaluation.consistency)


@pytest.mark.parametrize("phi", wu.PHIS)
@pytest.mark.parametrize("row", ROWS)
def test_roadmap_size_bound(pool, cache: wu.RunCache, row: str, phi: float) -> None:
    """FWER (L1) and P(H3a verdict = pass) (L1 and L2) <= 33 of 2000, i.e. 0.01 + 3 SE = 0.016675.

    Under L1 a "pass" is a false positive; under L2 it needs the null pair to reject. Predicted
    P(fail): see the module table (0.105 for L1 at phi = 0.3). A failure is a finding of class
    "method" (dependent labels), recorded in the unit Log, never tuned away. Under Option C the
    outcome is only recorded."""
    evaluation = cache.logrank(pool, row, phi)
    assert wu.enforce(evaluation.roadmap) in ("pass", "fail")


def test_reference_table_is_the_m5_table() -> None:
    """The study reads its references from ``wu0006_reference`` (a change there selects this file):
    L1 and L2 at phi 0 and 0.3 (R_ref = 40 000 per row), 6 ranges of counts out of 2000 in all."""
    assert sorted(ref.LOGRANK_REFERENCE) == [(row, f"{phi:g}") for row in ROWS for phi in wu.PHIS]
    ranges = [entry[key][1] for entry in ref.LOGRANK_REFERENCE.values() for key in ("fwer", "pass")
              if entry[key] is not None]
    assert len(ranges) == 6 and all(0 <= low <= high <= wu.R_LOGRANK for low, high in ranges)
