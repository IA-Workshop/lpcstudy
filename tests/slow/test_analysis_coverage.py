"""C2, C4 to C9, C2h and C4h: coverage and verdict error rates through the production call sites
(WU-0006.2).

Slow tier: R = 1000 replications of 2000 resamples per (case, phi), run once on a pool of single-thread
workers. The harness and the reference tables are in ``wu0006_harness`` and ``wu0006_reference``.

**Procedure and call sites.** For each case the harness runs ``bootstrap_values`` and
``percentile_interval`` at 95% and 1 - 0.05/3 from the same resamples (blocks of 5, B = 2000), reads the
criterion's verdict with ``criterion_verdict`` and the band constants of ``analysis``, and, in the first
10 replications (3 for C6), calls the production function and requires the same estimate, interval,
failed count and verdict bitwise:

| case | criterion, production call | n | data; truth on the band edge | level; band |
| --- | --- | --- | --- | --- |
| C2 | H2c, ``h2c_state_dependence`` (A4 - A2) | 500 | log-normal pair, sigma 1, c 0.8; E[a - b] = 0 | 95%; (-inf, 0) open |
| C4 | H3c, ``h3c_ratio`` | 500 | as C2, mu_a = ln 1.05; E a / E b = 1.05 | 1 - 0.05/3; (-inf, 1.05] |
| C5 | H2d, ``h2d_empirical_comparison`` | 500 | as C2, mu_a = ln 1.10; truth 0.10 | 95%; (-inf, 0.10] |
| C6 | H1d, ``h1d_correlations`` (row ``analog_seed``) | 500 | Gaussian pair, c = 2 sin(0.7 pi/6); Spearman 0.7 | 95%; [0.7, inf) |
| C7 | H2a(ii), ``h2a_part_ii`` (column ``interior``) | 500 | partial correlation 0.1 exactly | 1 - 0.05/3; (-0.1, 0.1) |
| C8 | H2b(ii), ``_paired_change`` (mean) | 300 | AR(1) difference, mean 0 | 1 - 0.05/3; (0, inf) |
| C9 | H2e, ``_paired_change`` (median) | 300 | AR(1) difference, median 0 | 95%; (0, inf) |

All series are stationary AR(1) in the latent with lag-1 autocorrelation phi in {0, 0.3}; the generator
specifications are those of the applied-mathematician's review (M3 (a)). The C7 zero column has a
constant indicator (all w* interior) and must read "not computable" with all 2000 resamples failed.

**Reference and prediction** (independent simulation, scratch seed 20261011, R_ref 10 000 to 40 000
(C6 10 000), fixed before any result; the C7 verdict counts R_ref 60 000, see below): coverage at 95% / 98.3% (SE of the reference in the note), and P(ROADMAP bound
fails | correct code).

| case | phi 0: 95% / 98.3% | P(A1), P(A2) | phi 0.3: 95% / 98.3% | P(A1), P(A2) |
| --- | --- | --- | --- | --- |
| C2 | 0.9395 / 0.9774 | 0.10, 0.11 | 0.9282 / 0.9706 | 0.55, 0.55 |
| C4 | 0.9402 / 0.9772 | 0.08, 0.12 | 0.9265 / 0.9715 | 0.63, 0.49 |
| C5 | 0.9383 / 0.9766 | 0.13, 0.15 | 0.9275 / 0.9691 | 0.59, 0.66 |
| C6 | 0.9470 / 0.9794 | 0.01, 0.05 | 0.9439 / 0.9800 | 0.03, 0.04 |
| C7 | 0.9443 / 0.9794 | 0.03, 0.05 | 0.9389 / 0.9762 | 0.11, 0.17 |
| C8 | 0.9444 / 0.9806 | 0.02, 0.03 | 0.9230 / 0.9682 | 0.78, 0.72 |
| C9 | 0.9427 / 0.9782 | 0.04, 0.08 | 0.9311 / 0.9736 | 0.42, 0.33 |

**Edge rates** (P(verdict pass) / P(verdict fail) when the truth is on the band edge, at the criterion's
own level; the same reference, fixed before any result except the C7 pass entries, which the
applied-mathematician corrected after run 2: DEF-0022, R_ref 60 000, ranges (0, 6) and (0, 3) in place of
(1, 23) and (2, 27), because H2a(ii-b) passes only if the interval lies inside the band, and the 98.3%
interval is wider than the band). The ROADMAP bound is <= 39 of 1000 at 95% and <= 16 at 98.3%.

| case (level) | phi 0: pass / fail | phi 0.3: pass / fail |
| --- | --- | --- |
| C2 (95%) | 0.0308 / 0.0296 | 0.0360 / 0.0358 |
| C4 (98.3%) | 0.0116 / 0.0111 | 0.0145 / 0.0140 |
| C5 (95%) | 0.0320 / 0.0297 | 0.0362 / 0.0363 |
| C6 (95%) | 0.0268 / 0.0262 | 0.0274 / 0.0287 |
| C7 (98.3%) | 0.00103 / 0.0106 | 0.00025 / 0.0112 |
| C8 (98.3%) | 0.0100 / 0.0095 | 0.0158 / 0.0160 |
| C9 (95%) | 0.0299 / 0.0274 | 0.0335 / 0.0355 |

The C7 pass row cannot fail its ROADMAP bound (P about 1e-13): "pass" is almost unreachable at this
width (v3 section 7 pre-registers that H2a's second part can be refuted but essentially cannot pass).

Correct code is expected to fall short of about 1 to 2 of the 32 phi = 0 and about 11 of the 32 phi = 0.3
ROADMAP bounds of A1 to A3 (recorded, not asserted, under Option C; the block-5 percentile interval
undercovers, most for heavy tails and lag-1 0.3): a ROADMAP-bound failure inside the consistency range is a finding of class "method", not a defect.

**Assertion groups** (each (case, phi) is a separate test):

* exact: identity with production; A4 (the verdict equals the independent band rule in every
  replication: one-sided for C2, C4 to C6, C8 and C9, two-sided for C7); A5 (no failed resamples in the asserted column); the C7 zero column. Zero tolerance.
* consistency: coverage at both levels, and the wrong-pass and wrong-fail counts at the edge, lie in
  the 64 pre-registered ranges (C2, C4 to C9 are 56 of them; the defect test, always asserted).
* roadmap: A1 >= 930 of 1000, A2 >= 972, and A3 (P(pass) and P(fail) at the criterion's own level each
  <= 39 of 1000 at 95%, <= 16 at 1 - 0.05/3; nominal alpha/2 + 3 SE). Under Option C
  (``ASSERT_ROADMAP_BOUNDS = False``, in force since 2026-10-12, DEC-0026 item 2) these are recorded
  characterization rows (computed, written to the results table, shown as a pytest warning, not
  asserted); they are asserted only under Option K (True). Open and closed edges are not told apart by A4 (no ties occur);
  deterministic tie tests do that (``test_wu0006_harness.py`` and ``tests/unit/test_analysis.py``).

Characterization rows C2h and C4h (sigma 1.5 and 2, c 0.8, phi 0) are reported against the reference
(C2h 0.9298 / 0.9734 and 0.9214 / 0.9695; C4h 0.9331 / 0.9744 and 0.9227 / 0.9669), not asserted. The
outcomes of all groups are written to ``runs/tests/wu0006_coverage_analysis.json``.
"""

from __future__ import annotations

import pytest

import wu0006_harness as wu

CASES = ("C2", "C4", "C5", "C6", "C7", "C8", "C9")
HEAVY = (wu.CaseSpec("C2", 1.5, "h1.5"), wu.CaseSpec("C2", 2.0, "h2"),
         wu.CaseSpec("C4", 1.5, "h1.5"), wu.CaseSpec("C4", 2.0, "h2"))


@pytest.fixture(scope="module")
def pool():
    """Spawned single-thread workers for the module."""
    with wu.worker_pool() as shared:
        yield shared


@pytest.fixture(scope="module")
def cache() -> wu.RunCache:
    return wu.RunCache("coverage_analysis")


@pytest.mark.parametrize("phi", wu.PHIS)
@pytest.mark.parametrize("case", CASES)
def test_exact_checks(pool, cache: wu.RunCache, case: str, phi: float) -> None:
    """Identity with the production call site, A4 per replication, A5, the C7 zero column.

    Reference: the production function (identity), the band rule written in the harness from the criterion's wording (A4; two-sided for C7)
    and the guard of DEC-0008 A3 (a constant indicator is not computable). Zero tolerance: all are
    deterministic comparisons of floats and strings."""
    evaluation = cache.coverage(pool, wu.CaseSpec(case), phi)
    assert not evaluation.exact, "; ".join(evaluation.exact)


@pytest.mark.parametrize("phi", wu.PHIS)
@pytest.mark.parametrize("case", CASES)
def test_counts_are_consistent_with_the_reference(pool, cache: wu.RunCache, case: str,
                                                  phi: float) -> None:
    """Coverage at both levels and the edge pass and fail counts lie in the pre-registered ranges
    (central 0.9995 of Bin(1000, p_ref) mixed over the reference's own Monte Carlo error). A count
    outside is a defect candidate (DEF class "code"); inside, a ROADMAP-bound failure is "method"."""
    evaluation = cache.coverage(pool, wu.CaseSpec(case), phi)
    assert not evaluation.consistency, "; ".join(evaluation.consistency)


@pytest.mark.parametrize("phi", wu.PHIS)
@pytest.mark.parametrize("case", CASES)
def test_roadmap_coverage_and_verdict_bounds(pool, cache: wu.RunCache, case: str,
                                             phi: float) -> None:
    """A1, A2 and A3 at R = 1000: coverage >= 930 (95%) and >= 972 (1 - 0.05/3); P(pass) and P(fail)
    at the edge <= 39 (95%) or <= 16 (98.3%). Bounds are nominal -/+ 3 SE (SE 0.00689, 0.00405,
    0.00494, 0.00287); truth on the band edge, analytic. Predicted P(fail) per the module table; a
    failure is a finding recorded in the unit Log, never tuned away (PRIME.2). Under Option C
    (``ASSERT_ROADMAP_BOUNDS = False``, as shipped) the outcome is only recorded and warned about,
    never asserted; under Option K (True) a failed bound raises."""
    evaluation = cache.coverage(pool, wu.CaseSpec(case), phi)
    assert wu.enforce(evaluation.roadmap) in ("pass", "fail")


@pytest.mark.parametrize("spec", HEAVY, ids=lambda s: s.label)
def test_heavy_tail_rows_are_reported(pool, cache: wu.RunCache, spec: wu.CaseSpec) -> None:
    """C2h and C4h: coverage with log-SD 1.5 and 2 (phi 0), reported against the reference, not asserted.

    The per-state MSE of the study may be heavier-tailed than sigma = 1 (a dynamics proxy gives a
    log-SD of 1.7 to 2.0), so the H2c and H3c intervals may run at an effective 0.92 to 0.93. Only the
    exact checks are asserted."""
    evaluation = cache.coverage(pool, spec, 0.0)
    assert evaluation.row["asserted"] is False and "z_vs_reference" in evaluation.row
    assert not evaluation.exact, "; ".join(evaluation.exact)
