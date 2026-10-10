"""Tests for lpcstudy.ensemble: retrieval spread."""

from __future__ import annotations

import numpy as np
import pytest


def test_retrieval_spread() -> None:
    """Noise sensitivity is 0 for a fixed analog and ~1 for unit-noise wander."""
    from lpcstudy.ensemble import retrieval_spread

    fixed = np.ones((1, 50, 7))
    assert retrieval_spread(fixed, 0.1)[0] == 0.0
    wander = 0.1 * np.random.default_rng(8).standard_normal((1, 20_000, 7))
    assert retrieval_spread(wander, 0.1)[0] == pytest.approx(1.0, rel=0.02)
