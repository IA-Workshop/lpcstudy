"""Tests for lpcstudy.allocation: closed-form weight and the seed proxy."""

from __future__ import annotations

import numpy as np
import pytest

from lpcstudy.allocation import SeedProxy, closed_form_weight
from lpcstudy.oracle import oracle_weight
from unit_helpers import _moments_from_draws


def test_closed_form_matches_uncorrelated_isotropic_case() -> None:
    """With independent seeds of variances eps^2 and delta^2, w* -> delta^2/(eps^2+delta^2)."""
    rng = np.random.default_rng(2)
    eps, delta = 0.4, 0.9
    cp = eps * rng.standard_normal((1, 200_000, 1))
    plp = delta * rng.standard_normal((1, 200_000, 1))
    w_star = oracle_weight(_moments_from_draws(cp, plp))[0, 0]
    assert w_star == pytest.approx(closed_form_weight(eps**2, delta**2), abs=5e-3)


def test_seed_proxy_recovers_parameters() -> None:
    """Log-scale least squares recovers slope and floor of seed^2 = a f^2 + b g^2."""
    rng = np.random.default_rng(5)
    rho = 0.02
    feature = rng.uniform(0.01, 0.2, 500)
    floor = rho * rng.uniform(0.5, 2.0, 500)
    seed_sq = (2.0 * feature**2 + 3.0 * floor**2) * np.exp(0.01 * rng.standard_normal(500))
    proxy = SeedProxy.fit(feature**2, floor**2, seed_sq)
    assert proxy.slope == pytest.approx(2.0, rel=0.02)
    assert proxy.floor == pytest.approx(3.0, rel=0.05)
