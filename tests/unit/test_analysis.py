"""Tests for lpcstudy.analysis: per-state Spearman trend."""

from __future__ import annotations

import numpy as np


def test_per_state_spearman_handles_ties() -> None:
    """A state whose weight is clipped to 0 at every level has no trend (rho = 0)."""
    from lpcstudy.analysis import _per_state_spearman

    values = np.array([[0.0, 0.0, 0.0, 0.0], [0.1, 0.2, 0.3, 0.4], [0.4, 0.3, 0.2, 0.1]])
    rho = _per_state_spearman(np.array([1.0, 2.0, 3.0, 4.0]), values)
    assert np.allclose(rho, [0.0, 1.0, -1.0])
