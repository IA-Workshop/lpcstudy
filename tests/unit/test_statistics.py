"""Tests for lpcstudy.statistics: Kaplan-Meier, log-rank, Holm, partial correlation."""

from __future__ import annotations

import numpy as np

from lpcstudy.statistics import holm_adjust, kaplan_meier, logrank_test, \
    partial_correlation


def test_kaplan_meier_matches_geometric_survival() -> None:
    """KM recovers the survival of censored geometric times."""
    rng = np.random.default_rng(3)
    times = rng.geometric(0.1, 50_000)
    censor = rng.integers(1, 41, 50_000)
    dur = np.minimum(np.minimum(times, censor), 40)
    ev = (times <= censor) & (times <= 40)
    curve = kaplan_meier(dur, ev, 40)
    assert np.max(np.abs(curve.survival - 0.9 ** curve.times)) < 0.01


def test_logrank_detects_difference_and_not_null() -> None:
    """Log-rank: small p for different hazards, large-ish p for equal hazards."""
    rng = np.random.default_rng(4)
    a, b = rng.geometric(0.1, 400), rng.geometric(0.2, 400)
    ones = np.ones(400, dtype=bool)
    assert logrank_test(a, ones, b, ones) < 1e-6
    c = rng.geometric(0.1, 400)
    assert logrank_test(a, ones, c, ones) > 1e-3


def test_holm() -> None:
    """Holm adjustment on a textbook example."""
    assert np.allclose(holm_adjust([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])


def test_partial_correlation_removes_confounder() -> None:
    """A variable related to the target only through a control has ~zero partial r."""
    rng = np.random.default_rng(6)
    z = rng.standard_normal(5000)
    x = z + 0.1 * rng.standard_normal(5000)
    y = z + 0.1 * rng.standard_normal(5000)
    assert abs(partial_correlation(y, x, z[:, None])) < 0.05
