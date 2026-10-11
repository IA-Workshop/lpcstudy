"""Tests for lpcstudy.pipeline: rule scoring and the K rule (WU-0002.3)."""

from __future__ import annotations

import numpy as np
import pytest
from sklearn.tree import DecisionTreeRegressor

from lpcstudy.allocation import RegimeMap
from lpcstudy.config import StudyConfig
from lpcstudy.ensemble import EvaluationDraws
from lpcstudy.oracle import curvature, oracle_weight
from lpcstudy.pipeline import SplitData, _choose_regimes, choose_regime_count, score_rules
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


K_VALUES = (2, 3, 4, 5, 6, 8)


HAND_VECTORS = (
    ([10, 8, 6, 5, 4.1, 4.0], 6),             # monotone: 4.1 <= 1.05 * 4.0 = 4.2, 5 > 4.2
    ([1.04, 1.03, 1.02, 1.01, 1.0, 1.0], 2),  # flat within 5%
    ([5, 2.05, 4, 2.0, 3, 2.5], 3),           # non-monotone: 2.05 <= 2.1, first such K
    ([9, 8, 7, 6, 5, 1.0], 8),                # minimum at K = 8
    ([1.3, 1.05, 1.2, 1.0, 1.1, 1.0], 3),     # tie at the 5% edge counts as inside
    ([1.3, np.nextafter(1.05, np.inf), 1.2, 1.0, 1.1, 1.0], 5),  # one ulp above: outside
)


def test_k_rule_hand_vectors() -> None:
    """The K rule returns the hand-expected K on the six fixed excess-vs-K vectors (M2 §M7).

    Reference: hand computation, written beside each vector: the smallest K in
    (2, 3, 4, 5, 6, 8) with excess_K <= 1.05 * min. Vector 5 (min 1.0) has 1.05 exactly
    at the edge: float64 ``1.0 + 0.05 == 1.05``, so K = 3 is inside (the subtraction form
    ``x - m <= 0.05 m`` would give 5, because 1.05 - 1.0 = 0.05000000000000004). The last
    vector replaces 1.05 by ``np.nextafter(1.05, inf)`` and expects 5 (the edge is
    sharp). Tolerance: none; the output is an integer from unrounded float64 comparisons.
    """
    for excess, expected in HAND_VECTORS:
        assert choose_regime_count(dict(zip(K_VALUES, excess))) == expected, excess


def test_k_rule_rejects_bad_input() -> None:
    """Empty input, NaN, infinity and negative excess raise ``ValueError`` (PRIME.4).

    Reference: the documented contract. A negative minimum would invert the multiplicative
    margin, and the exact excess is never negative, so it signals a bug. A negative margin
    also raises. Tolerance: none (exception type).
    """
    with pytest.raises(ValueError):
        choose_regime_count({})
    for bad in (float("nan"), float("inf"), -1e-12):
        with pytest.raises(ValueError):
            choose_regime_count({2: 1.0, 3: bad, 4: 0.5})
    with pytest.raises(ValueError):
        choose_regime_count({2: 1.0}, margin=-0.1)
    assert choose_regime_count({8: 1.0, 2: 1.04, 4: 3.0}) == 2  # sorted order, not insertion


def test_choose_regimes_uses_absolute_excess_at_href_column() -> None:
    """``_choose_regimes`` applies the rule to the calibration excess at the H_ref column.

    Reference: hand computation. All 40 states have the same realizable triple E_C = 1.5,
    E_P = 1.5, C = 0.5 (c = 2, b = 1, u = 0.5, so the excess of weight w is
    2 (w - 0.5)^2, exact algebra). Horizons (10, 30, 60) are not contiguous and
    ``reference_horizon`` is 30, so the column is 1 (found by value). Candidates K = 2, 3,
    4 have w = 0.9, 0.7, 0.6 at column 1, i.e. excess 0.32, 0.08, 0.02, so only K = 4 is
    within 5% of the minimum; at columns 0 and 2 all candidates have w = 0.5 (excess 0),
    which would give K = 2 if the wrong column were used. K = 12 (w = 0.5 at column 1,
    excess 0) is above ``regime_max_primary`` = 8 and must be ignored, otherwise K = 12
    would be chosen. The regime maps share one 2-leaf tree on a 1-D profile; the keys are
    labels only. Tolerance: none; the output is an integer and the margins between the
    excess values are factors of 4 or more.
    """
    n_states = 40
    triple = (np.full((n_states, 3), 1.5), np.full((n_states, 3), 1.5),
              np.full((n_states, 3), 0.5))
    moments = moments_from_triples(*triple)
    moments.horizons = np.array([10, 30, 60])
    x = np.concatenate([-np.ones(20), np.ones(20)])
    profile = np.stack([x, x], axis=1)[:, :, None]
    tree = DecisionTreeRegressor(max_leaf_nodes=2, random_state=0)
    tree.fit(profile.reshape(-1, 1), np.repeat((x > 0).astype(float), 2))
    leaf_ids = np.nonzero(tree.tree_.children_left == -1)[0]

    def regime_map(w_href: float) -> RegimeMap:
        row = np.array([0.5, w_href, 0.5])
        return RegimeMap(tree=tree, leaf_ids=leaf_ids, weights=np.stack([row, row]),
                         horizons_km=np.full(2, np.nan))

    regimes = {2: regime_map(0.9), 3: regime_map(0.7), 4: regime_map(0.6),
               12: regime_map(0.5)}
    config = StudyConfig()
    assert config.reference_horizon == 30 and config.regime_max_primary == 8
    assert _choose_regimes(regimes, profile, moments, config) == 4


def test_concat_moments_stacks_the_correlation_fields_and_refuses_a_mixture() -> None:
    """``_concat_moments`` stacks ``err_corr``, ``cp_constant`` and ``plp_constant`` row-wise.

    Reference: ``np.concatenate`` of hand-built arrays whose entries are their own flat index
    (expected values read off by eye). Two parts of 3 and 2 states: the stacked field is the 5
    rows in order. Parts without the fields give ``None``. A mixture (one part with, one
    without) raises ``ValueError`` instead of dropping the field silently (PRIME.4). Exact.
    """
    import dataclasses

    from lpcstudy.pipeline import _concat_moments
    from unit_helpers import _moments_from_draws

    rng = np.random.default_rng(6)
    plain = [_moments_from_draws(rng.standard_normal((n, 4, 3)), rng.standard_normal((n, 4, 3)))
             for n in (3, 2)]
    assert _concat_moments(plain).err_corr is None
    grid = np.arange(15.0).reshape(5, 3)
    with_fields = [dataclasses.replace(p, err_corr=g, cp_constant=g > 6, plp_constant=g < 4)
                   for p, g in zip(plain, (grid[:3], grid[3:]))]
    stacked = _concat_moments(with_fields)
    np.testing.assert_array_equal(stacked.err_corr, grid)
    np.testing.assert_array_equal(stacked.cp_constant, grid > 6)
    np.testing.assert_array_equal(stacked.plp_constant, grid < 4)
    with pytest.raises(ValueError, match="err_corr"):
        _concat_moments([with_fields[0], plain[1]])
