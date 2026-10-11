"""Tests for lpcstudy.estimation: the replacements of ``StateEstimator`` are counted (DEF-0001)."""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np

from lpcstudy.estimation import StateEstimator

STATE_MEAN = np.array([0.5, -1.0, 8.0])


def _estimator(states: np.ndarray, nu: np.ndarray) -> StateEstimator:
    """An estimator whose compiled function is a stub returning fixed arrays (no network)."""
    return StateEstimator(ctx=SimpleNamespace(state_mean=STATE_MEAN), network=None,
                          model_step=None, _fn=lambda inputs: (states, nu))


def _old_replacements(states: np.ndarray, nu: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The two ``np.where`` lines of ``StateEstimator.estimate`` before WU-0002.11a, verbatim."""
    nu = np.where(np.isfinite(nu), nu, 1e6)
    states = np.where(np.isfinite(states), states, STATE_MEAN)
    return states, nu


def test_estimate_counted_a1_one_nan_state_one_inf_nu() -> None:
    """A1: one row with a NaN coordinate and one with nu = inf give one count each.

    Reference: a hand stub. Row 0 is finite; row 1 has one NaN coordinate; row 2 has nu = +inf.
    The expected counts are read off the construction (1 and 1). Values are compared bitwise
    (``tobytes``) with the two ``np.where`` lines of the code before the change, copied above:
    exact equality, because the new code applies the same expressions in the same order.
    """
    states = np.array([[1.0, 2.0, 3.0], [1.0, np.nan, 3.0], [4.0, 5.0, 6.0]])
    nu = np.array([2.0, 3.0, np.inf])
    est = _estimator(states, nu)
    got_states, got_nu, state_replaced, nu_replaced = est.estimate_counted(np.zeros((3, 7)))
    ref_states, ref_nu = _old_replacements(states, nu)
    assert got_states.tobytes() == ref_states.tobytes()
    assert got_nu.tobytes() == ref_nu.tobytes()
    assert int(state_replaced.sum()) == 1 and state_replaced.tolist() == [False, True, False]
    assert int(nu_replaced.sum()) == 1 and nu_replaced.tolist() == [False, False, True]
    assert got_states[1].tolist() == [1.0, STATE_MEAN[1], 3.0] and got_nu[2] == 1e6


def test_estimate_counts_estimates_not_coordinates() -> None:
    """The unit is one estimate: two bad coordinates in a row count once, and a row can be in both.

    Reference: hand stub. Row 0: NaN and +inf coordinates and nu = NaN (one state replacement and
    one nu replacement). Row 1: all three coordinates -inf (one state replacement). Row 2: finite
    state, nu = -inf (one nu replacement; ``isfinite`` is False for -inf). Expected 2 and 2,
    by construction.
    """
    states = np.array([[np.nan, np.inf, 1.0], [-np.inf, -np.inf, -np.inf], [0.0, 0.0, 0.0]])
    nu = np.array([np.nan, 1.0, -np.inf])
    got_states, got_nu, state_replaced, nu_replaced = _estimator(states, nu).estimate_counted(
        np.zeros((3, 7)))
    assert int(state_replaced.sum()) == 2 and int(nu_replaced.sum()) == 2
    assert state_replaced.tolist() == [True, True, False]
    assert nu_replaced.tolist() == [True, False, True]
    ref_states, ref_nu = _old_replacements(states, nu)
    assert got_states.tobytes() == ref_states.tobytes() and got_nu.tobytes() == ref_nu.tobytes()


def test_estimate_delegates_to_estimate_counted() -> None:
    """``estimate`` returns exactly the first two outputs of ``estimate_counted``.

    Reference: the old ``estimate`` lines (copied) on a stub with a NaN state and an infinite nu;
    bitwise equality, since the same expressions run.
    """
    states = np.array([[1.0, np.nan, 3.0], [4.0, 5.0, 6.0]])
    nu = np.array([np.inf, 2.0])
    est = _estimator(states, nu)
    plain_states, plain_nu = est.estimate(np.zeros((2, 7)))
    ref_states, ref_nu = _old_replacements(states, nu)
    assert plain_states.tobytes() == ref_states.tobytes() and plain_nu.tobytes() == ref_nu.tobytes()
