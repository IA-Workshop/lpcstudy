"""Tests for lpcstudy.pipeline: rule scoring and the K rule (WU-0002.3)."""

from __future__ import annotations

import numpy as np
import pytest

from lpcstudy.config import StudyConfig
from lpcstudy.ensemble import EvaluationDraws
from lpcstudy.oracle import curvature, oracle_weight
from lpcstudy.pipeline import SplitData, score_rules
from unit_helpers import moments_from_triples, realizable_triples


def test_score_rules_regret_exact() -> None:
    """``score_rules`` reports the exact excess regret: A* is exactly 0.0, A0 is E_C - V(w*).

    Reference: brute force. For A0 (w = 1) the excess at each (state, horizon) is
    E_C - min over ``np.linspace(0, 1, 10_000)`` of V, with V evaluated directly from the
    moment triple; the reference regret per horizon is the mean over the 7 states (each
    appears E = 2 times). The 210 manufactured triples fill a 7 x 30 array (horizons
    1..30 = the reference horizon of the default configuration); they have u in (-5, 0)
    or [0, 0.9], so |1 - w*| >= 0.1 holds, asserted as a precondition on the w* the code
    returns. Half of the triples have u < 0 (clipped).
    Tolerances: A* regret ``== 0.0`` exactly (w equals the same clip of the same u, so both
    squares are bit-identical); A0 ``rtol=1e-6`` (the grid argument of
    ``test_excess_mse_matches_grid_minimum``: relative bias at most 2.5e-7 at distance
    0.1, round-off about 1e-12). The old c (w - w*)^2 mean must be smaller than the exact
    A0 regret by more than 1e-3 relative (detects DEF-0002).
    """
    rng = np.random.default_rng(77)
    t = realizable_triples(rng, 105, 105, 0, inside=(0.0, 0.9))
    order = rng.permutation(210)
    shape = (7, 30)
    e_c, e_p, cross = (t[k][order].reshape(shape) for k in ("E_C", "E_P", "C"))
    moments = moments_from_triples(e_c, e_p, cross)
    w_star = oracle_weight(moments)
    assert np.all(1.0 - w_star >= 0.1)  # precondition of the grid reference
    assert np.mean(oracle_weight(moments, clip=False) < 0) > 0.4

    config = StudyConfig()
    horizons = np.arange(1, 31)
    assert config.reference_horizon == 30
    n_states, n_draws, n_hor = 7, 2, 30
    noise_rng = np.random.default_rng(78)
    zeros = np.zeros((n_states, n_draws, n_hor))
    evals = EvaluationDraws(
        horizons=horizons, cp_err=noise_rng.standard_normal(zeros.shape),
        plp_err=noise_rng.standard_normal(zeros.shape), verify_noise=zeros,
        distance=np.zeros((n_states, n_draws)), est_nu=np.zeros((n_states, n_draws)),
        growth_proxy=np.zeros((n_states, n_draws)), gain_proxy=zeros,
        inputs=np.zeros((n_states, n_draws, 1)), noise_sens=np.zeros((n_states, n_draws)))
    weights = {"A0": np.ones(zeros.shape),
               "A*": np.broadcast_to(w_star[:, None, :], zeros.shape).copy()}
    scores = score_rules(weights, SplitData(moments=moments, evals=evals), horizons, config,
                         theta=1.0)
    assert np.all(scores["A*"].regret == 0.0)

    grid = np.linspace(0.0, 1.0, 10_000)
    v_grid = grid**2 * e_c[..., None] + (1 - grid) ** 2 * e_p[..., None] + \
        2 * grid * (1 - grid) * cross[..., None]  # (7, 30, 10000)
    reference = np.mean(e_c - v_grid.min(axis=-1), axis=0)
    np.testing.assert_allclose(scores["A0"].regret, reference, rtol=1e-6, atol=0.0)
    old = np.mean(curvature(moments) * (1.0 - w_star) ** 2, axis=0)
    assert np.mean(old) < np.mean(reference) * (1.0 - 1e-3)
