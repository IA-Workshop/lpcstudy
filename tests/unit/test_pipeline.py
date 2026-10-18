"""Tests for ``lpcstudy.pipeline``, the assembly line of the study.

The pipeline builds forecast cells, fits the rules that choose the blending
weight, scores them, and records every clip, replacement and fallback in a
"handling" block. These tests check three things.

* The score of a rule (its regret, the excess error over the best weight).
* The rule that chooses the number of regimes K.
* The bookkeeping: counters, stacking of arrays from several cells, and the
  handling record, all against small hand-built inputs whose answers can be
  worked out on paper.

Heavy parts (network training, forecasting) are replaced by stubs, so every
test runs in well under 5 seconds.
"""

from __future__ import annotations

import numpy as np
import pytest
from sklearn.tree import DecisionTreeRegressor

from lpcstudy.allocation import RegimeMap
from lpcstudy.config import StudyConfig
from lpcstudy.data import make_rng
from lpcstudy.ensemble import EvaluationDraws
from lpcstudy.oracle import curvature, oracle_weight
from lpcstudy.pipeline import (
    SplitData,
    _choose_regimes,
    choose_regime_count,
    score_rules,
)
from unit_helpers import moments_from_triples, realizable_triples


def test_score_rules_regret_exact() -> None:
    """``score_rules`` reports the exact regret: A* is 0, A0 is E_C - V(w*).

    Regret is the extra error a rule has compared with the best weight w*.

    Reference: brute force. For A0 (w = 1) the excess at each
    (state, horizon) is E_C minus the minimum over ``np.linspace(0, 1,
    10_000)`` of V, with V evaluated directly from the moment triple. The
    reference regret per horizon is the mean over the 7 states (each appears
    E = 2 times). The 210 manufactured triples fill a 7 x 30 array (horizons
    1..30 = the reference horizon of the default configuration). They have u
    in (-5, 0) or [0, 0.9], so |1 - w*| >= 0.1 holds; this is asserted as a
    precondition on the w* the code returns. Half of the triples have u < 0
    (clipped).

    Tolerances: the A* regret is ``== 0.0`` exactly (w equals the same clip of
    the same u, so both squares are bit-identical). The A0 regret uses
    ``rtol=1e-6`` (the grid argument of
    ``test_excess_mse_matches_grid_minimum``: relative bias at most 2.5e-7 at
    distance 0.1, round-off about 1e-12). The old c (w - w*)^2 mean must be
    smaller than the exact A0 regret by more than 1e-3 relative (this detects
    DEF-0002).
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
        horizons=horizons,
        cp_err=noise_rng.standard_normal(zeros.shape),
        plp_err=noise_rng.standard_normal(zeros.shape),
        verify_noise=zeros,
        distance=np.zeros((n_states, n_draws)),
        est_nu=np.zeros((n_states, n_draws)),
        growth_proxy=np.zeros((n_states, n_draws)),
        gain_proxy=zeros,
        inputs=np.zeros((n_states, n_draws, 1)),
        noise_sens=np.zeros((n_states, n_draws)),
    )
    weights = {
        "A0": np.ones(zeros.shape),
        "A*": np.broadcast_to(w_star[:, None, :], zeros.shape).copy(),
    }
    scores = score_rules(
        weights,
        SplitData(moments=moments, evals=evals),
        horizons,
        config,
        theta=1.0,
    )
    assert np.all(scores["A*"].regret == 0.0)

    grid = np.linspace(0.0, 1.0, 10_000)
    v_grid = (
        grid**2 * e_c[..., None]
        + (1 - grid) ** 2 * e_p[..., None]
        + 2 * grid * (1 - grid) * cross[..., None]
    )  # (7, 30, 10000)
    reference = np.mean(e_c - v_grid.min(axis=-1), axis=0)
    np.testing.assert_allclose(
        scores["A0"].regret, reference, rtol=1e-6, atol=0.0
    )
    old = np.mean(curvature(moments) * (1.0 - w_star) ** 2, axis=0)
    assert np.mean(old) < np.mean(reference) * (1.0 - 1e-3)


K_VALUES = (2, 3, 4, 5, 6, 8)


HAND_VECTORS = (
    # monotone: 4.1 <= 1.05 * 4.0 = 4.2, 5 > 4.2
    ([10, 8, 6, 5, 4.1, 4.0], 6),
    # flat within 5%
    ([1.04, 1.03, 1.02, 1.01, 1.0, 1.0], 2),
    # non-monotone: 2.05 <= 2.1, first such K
    ([5, 2.05, 4, 2.0, 3, 2.5], 3),
    # minimum at K = 8
    ([9, 8, 7, 6, 5, 1.0], 8),
    # tie at the 5% edge counts as inside
    ([1.3, 1.05, 1.2, 1.0, 1.1, 1.0], 3),
    # one ulp (the smallest float step) above the edge: outside
    ([1.3, np.nextafter(1.05, np.inf), 1.2, 1.0, 1.1, 1.0], 5),
)


def test_k_rule_hand_vectors() -> None:
    """The K rule returns the hand-expected K on six fixed excess-vs-K vectors.

    The rule (M2 §M7) picks the smallest number of regimes K whose excess
    error is within 5% of the best.

    Reference: hand computation, written beside each vector: the smallest K in
    (2, 3, 4, 5, 6, 8) with excess_K <= 1.05 * min. Vector 5 (min 1.0) has
    1.05 exactly at the edge: in float64 ``1.0 + 0.05 == 1.05``, so K = 3 is
    inside (the subtraction form ``x - m <= 0.05 m`` would give 5, because
    1.05 - 1.0 = 0.05000000000000004). The last vector replaces 1.05 by
    ``np.nextafter(1.05, inf)`` and expects 5 (the edge is sharp).

    Tolerance: none; the output is an integer from unrounded float64
    comparisons.
    """
    for excess, expected in HAND_VECTORS:
        assert (
            choose_regime_count(dict(zip(K_VALUES, excess))) == expected
        ), excess


def test_k_rule_rejects_bad_input() -> None:
    """Empty input, NaN, infinity and negative excess raise ``ValueError``.

    This is the PRIME.4 rule: bad input is never handled silently.

    Reference: the documented contract. A negative minimum would invert the
    multiplicative margin, and the exact excess is never negative, so a
    negative value signals a bug. A negative margin also raises.

    Tolerance: none (exception type).
    """
    with pytest.raises(ValueError):
        choose_regime_count({})
    for bad in (float("nan"), float("inf"), -1e-12):
        with pytest.raises(ValueError):
            choose_regime_count({2: 1.0, 3: bad, 4: 0.5})
    with pytest.raises(ValueError):
        choose_regime_count({2: 1.0}, margin=-0.1)
    # Sorted order, not insertion order:
    assert choose_regime_count({8: 1.0, 2: 1.04, 4: 3.0}) == 2


def test_choose_regimes_uses_absolute_excess_at_href_column() -> None:
    """``_choose_regimes`` applies the rule to the excess at the H_ref column.

    H_ref is the reference horizon, the one forecast length the study scores
    its rules at.

    Reference: hand computation. All 40 states have the same realizable
    triple E_C = 1.5, E_P = 1.5, C = 0.5 (c = 2, b = 1, u = 0.5, so the excess
    of weight w is 2 (w - 0.5)^2, exact algebra). Horizons (10, 30, 60) are
    not contiguous and ``reference_horizon`` is 30, so the column is 1 (found
    by value). Candidates K = 2, 3, 4 have w = 0.9, 0.7, 0.6 at column 1, i.e.
    excess 0.32, 0.08, 0.02, so only K = 4 is within 5% of the minimum. At
    columns 0 and 2 all candidates have w = 0.5 (excess 0), which would give
    K = 2 if the wrong column were used. K = 12 (w = 0.5 at column 1, excess
    0) is above ``regime_max_primary`` = 8 and must be ignored, otherwise
    K = 12 would be chosen. The regime maps share one 2-leaf tree on a 1-D
    profile; the keys are labels only.

    Tolerance: none; the output is an integer and the margins between the
    excess values are factors of 4 or more.
    """
    n_states = 40
    triple = (
        np.full((n_states, 3), 1.5),
        np.full((n_states, 3), 1.5),
        np.full((n_states, 3), 0.5),
    )
    moments = moments_from_triples(*triple)
    moments.horizons = np.array([10, 30, 60])
    x = np.concatenate([-np.ones(20), np.ones(20)])
    profile = np.stack([x, x], axis=1)[:, :, None]
    tree = DecisionTreeRegressor(max_leaf_nodes=2, random_state=0)
    tree.fit(profile.reshape(-1, 1), np.repeat((x > 0).astype(float), 2))
    leaf_ids = np.nonzero(tree.tree_.children_left == -1)[0]

    def regime_map(w_href: float) -> RegimeMap:
        row = np.array([0.5, w_href, 0.5])
        return RegimeMap(
            tree=tree,
            leaf_ids=leaf_ids,
            weights=np.stack([row, row]),
            horizons_km=np.full(2, np.nan),
        )

    regimes = {
        2: regime_map(0.9),
        3: regime_map(0.7),
        4: regime_map(0.6),
        12: regime_map(0.5),
    }
    config = StudyConfig()
    assert config.reference_horizon == 30 and config.regime_max_primary == 8
    assert _choose_regimes(regimes, profile, moments, config) == 4


def test_concat_moments_stacks_the_correlation_fields_and_refuses_a_mixture() -> (
    None
):
    """``_concat_moments`` stacks the correlation fields row by row.

    The fields are ``err_corr``, ``cp_constant`` and ``plp_constant``.

    Reference: ``np.concatenate`` of hand-built arrays whose entries are their
    own flat index (expected values read off by eye). Two parts of 3 and 2
    states: the stacked field is the 5 rows in order. Parts without the fields
    give ``None``. A mixture (one part with, one without) raises
    ``ValueError`` instead of dropping the field silently (PRIME.4).

    Tolerance: exact.
    """
    import dataclasses

    from lpcstudy.pipeline import _concat_moments
    from unit_helpers import _moments_from_draws

    rng = np.random.default_rng(6)
    plain = [
        _moments_from_draws(
            rng.standard_normal((n, 4, 3)), rng.standard_normal((n, 4, 3))
        )
        for n in (3, 2)
    ]
    assert _concat_moments(plain).err_corr is None
    grid = np.arange(15.0).reshape(5, 3)
    with_fields = [
        dataclasses.replace(
            p, err_corr=g, cp_constant=g > 6, plp_constant=g < 4
        )
        for p, g in zip(plain, (grid[:3], grid[3:]))
    ]
    stacked = _concat_moments(with_fields)
    np.testing.assert_array_equal(stacked.err_corr, grid)
    np.testing.assert_array_equal(stacked.cp_constant, grid > 6)
    np.testing.assert_array_equal(stacked.plp_constant, grid < 4)
    with pytest.raises(ValueError, match="err_corr"):
        _concat_moments([with_fields[0], plain[1]])


def test_concat_carries_handled_and_sums_entry_totals() -> None:
    """Stacking cells joins ``handled`` row by row and adds ``clip_entries``.

    This covers ``_concat_moments`` and ``_concat_evals``.

    Reference: hand-built arrays whose entries are their own flat index
    (expected values read off by eye) and hand-added totals. Two parts of 3
    and 2 states with 6 counter columns: the stacked ``handled`` is the 5 rows
    in order; the totals are the sums (3 + 4, 0 + 1, 5 + 6). A part without
    ``handled`` among parts with it raises ``ValueError`` (PRIME.4); parts
    without any give ``None``; a part whose totals are ``None`` (a view) gives
    ``None`` totals.

    Tolerance: exact.
    """
    import dataclasses

    from lpcstudy.pipeline import _concat_evals, _concat_moments
    from unit_helpers import _moments_from_draws

    rng = np.random.default_rng(6)
    plain = [
        _moments_from_draws(
            rng.standard_normal((n, 4, 3)), rng.standard_normal((n, 4, 3))
        )
        for n in (3, 2)
    ]
    assert (
        _concat_moments(plain).handled is None
        and _concat_moments(plain).clip_entries is None
    )
    grid = np.arange(30, dtype=np.int64).reshape(5, 6)
    entries = [
        {"error_clips_cp": 3, "error_clips_plp": 0, "error_clips_nonfinite": 5},
        {"error_clips_cp": 4, "error_clips_plp": 1, "error_clips_nonfinite": 6},
    ]
    parts = [
        dataclasses.replace(p, handled=g, clip_entries=e)
        for p, g, e in zip(plain, (grid[:3], grid[3:]), entries)
    ]
    stacked = _concat_moments(parts)
    np.testing.assert_array_equal(stacked.handled, grid)
    assert stacked.clip_entries == {
        "error_clips_cp": 7,
        "error_clips_plp": 1,
        "error_clips_nonfinite": 11,
    }
    with pytest.raises(ValueError, match="handled"):
        _concat_moments([parts[0], plain[1]])
    assert (
        _concat_moments(
            [parts[0], dataclasses.replace(parts[1], clip_entries=None)]
        ).clip_entries
        is None
    )

    def evals(n: int, handled, entry) -> EvaluationDraws:
        zeros = np.zeros((n, 2, 3))
        return EvaluationDraws(
            horizons=np.arange(1, 4),
            cp_err=zeros,
            plp_err=zeros,
            verify_noise=zeros,
            distance=np.zeros((n, 2)),
            est_nu=np.zeros((n, 2)),
            growth_proxy=np.zeros((n, 2)),
            gain_proxy=zeros,
            inputs=np.zeros((n, 2, 1)),
            noise_sens=np.zeros((n, 2)),
            handled=handled,
            clip_entries=entry,
        )

    both = _concat_evals(
        [evals(3, grid[:3], entries[0]), evals(2, grid[3:], entries[1])]
    )
    np.testing.assert_array_equal(both.handled, grid)
    assert both.clip_entries["error_clips_cp"] == 7
    assert both.cp_err.shape == (5, 2, 3)
    none = _concat_evals([evals(3, None, None), evals(2, None, None)])
    assert none.handled is None and none.clip_entries is None


def _flag_moments(
    n_states: int, cp_cells: list, plp_cells: list, horizons=(10, 30, 60)
):
    """Return moments with the given constant (state, horizon) cells.

    The curvature is 2 everywhere.
    """
    n_hor = len(horizons)
    moments = moments_from_triples(
        np.full((n_states, n_hor), 2.0),
        np.full((n_states, n_hor), 2.0),
        np.full((n_states, n_hor), 1.0),
    )
    moments.horizons = np.array(horizons)
    cp = np.zeros((n_states, n_hor), dtype=bool)
    plp = np.zeros((n_states, n_hor), dtype=bool)
    for state, hor in cp_cells:
        cp[state, hor] = True
    for state, hor in plp_cells:
        plp[state, hor] = True
    moments.err_corr = np.zeros((n_states, n_hor))
    moments.cp_constant, moments.plp_constant = cp, plp
    return moments


def test_moment_counters_a4_union_and_h2e_slice() -> None:
    """A4: ``zero_variance_corr`` is the union over horizons.

    Its H_ref slice must match the H2e fields.

    A "constant" error means the error did not vary over the oracle draws, so
    its correlation with the other forecaster's error is undefined (set to 0).

    Reference: a hand construction. 4 states, horizons (10, 30, 60), H_ref =
    30 (column 1). CP is constant at (0,0), (1,1), (2,1), (3,2); PLP is
    constant at (2,1), (0,2), (3,1). So CP has 4, PLP has 3, both at (2,1) is
    1, and the union is 4 + 3 - 1 = 6 (D4: an entry that is both CP- and
    PLP-constant). The H_ref slice, counted by hand: CP at states {1, 2} = 2,
    PLP at {2, 3} = 2, both {2} = 1. The slice is compared field by field with
    the ``cp_constant``, ``plp_constant`` and ``both_constant`` of
    ``h2e_noise_matching`` on a cell holding the same moments.

    Tolerance: exact integers.
    """
    from lpcstudy.analysis import h2e_noise_matching
    from lpcstudy.pipeline import Cell, moment_counters

    moments = _flag_moments(
        4, [(0, 0), (1, 1), (2, 1), (3, 2)], [(2, 1), (0, 2), (3, 1)]
    )
    got = moment_counters(moments, 30)
    assert got["zero_variance_corr"] == 6 and got["zero_variance_corr_cp"] == 4
    assert got["zero_variance_corr_plp"] == 3
    assert (
        got["zero_variance_corr"]
        == got["zero_variance_corr_cp"] + got["zero_variance_corr_plp"] - 1
    )
    cell = Cell(
        system="lorenz63",
        noise=0.01,
        library_size=1000,
        label="stub",
        setup=None,
        splits={"test": SplitData(moments, None)},
        oracles={},
        horizons=moments.horizons,
    )
    h2e = h2e_noise_matching({(0.01, 1000): cell}, StudyConfig())[
        "zero_variance_corr"
    ]["0.01"]["1000"]
    assert (h2e["cp_constant"], h2e["plp_constant"], h2e["both_constant"]) == (
        2,
        2,
        1,
    )
    cp, plp = moments.cp_constant[:, 1], moments.plp_constant[:, 1]
    assert (int(cp.sum()), int(plp.sum()), int((cp & plp).sum())) == (2, 2, 1)


def test_moment_counters_a5_floors_and_bad_input() -> None:
    """A5: the two floor counters count one entry each; bad moments raise.

    The floors are sentinels: counters of cases that should never occur, kept
    so that they would show up if they did.

    Reference: hand moments, 4 states x 3 horizons (10, 30, 60), H_ref 30.
    ``E_C = E_P = 2`` and ``C = 1`` give ``c = 2``. The entry (0, 0) has
    ``E_C = E_P = C = 1`` so ``c = 0`` exactly (one curvature floor). State 2
    has ``E_P = 0`` at H_ref (column 1) with ``C = 0`` (one decisive floor;
    ``c = 2``, so no curvature floor). A cancellation case: (1, 2) has ``C``
    just above ``(E_C + E_P) / 2`` so ``c < 0`` (counted: the expression is
    ``curvature(moments) < 1e-300``). Expected ``curvature_floor == 2`` and
    ``decisive_floor == 1``. Moments without the masks, and an unknown
    ``H_ref``, raise ``ValueError`` (PRIME.4).

    Tolerance: exact integers.
    """
    from lpcstudy.pipeline import moment_counters

    moments = _flag_moments(4, [], [])
    moments.sq_cp[0, 0], moments.sq_plp[0, 0], moments.cross[0, 0] = (
        1.0,
        1.0,
        1.0,
    )
    moments.sq_plp[2, 1], moments.cross[2, 1] = 0.0, 0.0
    moments.cross[1, 2] = 2.0 + 1e-3  # c = 2 + 2 - 2 * 2.001 = -0.002 < 0
    assert float(curvature(moments)[1, 2]) < 0.0
    got = moment_counters(moments, 30)
    assert got["curvature_floor"] == 2 and got["decisive_floor"] == 1
    assert got["zero_variance_corr"] == 0
    bare = moments_from_triples(
        np.ones((2, 3)), np.ones((2, 3)), np.ones((2, 3))
    )
    with pytest.raises(ValueError, match="masks"):
        moment_counters(bare, 2)
    with pytest.raises(ValueError, match="reference horizon"):
        moment_counters(moments, 31)


def test_fit_counters_sum_by_k_and_chosen() -> None:
    """``fit_counters`` sums empty regimes over K and keeps the chosen K.

    It also sums the pooled floors.

    Reference: hand-built maps. K = 2 has 1 empty regime, K = 3 has 0, K = 4
    has 2 (``empty`` masks written out), with pooled floors 0, 1, 0; the
    chosen K is 4; the A2 floor is 1; there is 1 constant target. Expected:
    ``empty_regime_fallback == 3``, by-K ``{"2": 1, "3": 0, "4": 2}``, chosen
    2, ``pooled_curvature_floor == 2``, ``regime_target_constant == 1``. The
    by-K keys are strings, so that the block survives a round trip through
    JSON.

    Tolerance: exact.
    """
    import json

    from lpcstudy.pipeline import fit_counters

    def regime_map(empty: list[bool], pooled: int) -> RegimeMap:
        return RegimeMap(
            tree=None,
            leaf_ids=np.arange(len(empty)),
            weights=np.zeros((len(empty), 1)),
            horizons_km=np.full(len(empty), np.nan),
            empty=np.array(empty),
            pooled_curvature_floor=pooled,
        )

    maps = {
        2: regime_map([True, False], 0),
        3: regime_map([False] * 3, 1),
        4: regime_map([True, False, True, False], 0),
    }
    got = fit_counters(maps, 4, a2_floor=1, target_constant=1)
    assert got == {
        "empty_regime_fallback": 3,
        "empty_regime_fallback_by_K": {"2": 1, "3": 0, "4": 2},
        "empty_regime_fallback_chosen": 2,
        "pooled_curvature_floor": 2,
        "regime_target_constant": 1,
    }
    assert json.loads(json.dumps(got)) == got


def test_fit_rules_records_fit_counters(monkeypatch) -> None:
    """``fit_rules`` returns ``handled`` with the fit counts.

    The counts are for empty regimes, floors and constant targets.

    Reference: a hand construction with the heavy parts stubbed (proxy fit,
    error-predictor fit and the profile: the profile of a split is its
    ``growth_proxy`` column, a 1-D feature). Config: 2 steps per Lyapunov
    time, H_max = 4, H_ref = 2, K in (2, 3). There are 40 construction states,
    half at x = -1 (E_C = 2, E_P = 1, C = 0, so w* = 1/3) and half at x = +1
    (E_C = 1, E_P = 2, C = 0, so w* = 2/3). The error moments make the hybrid
    exceed theta at horizon 1 for every state, so the log-horizon target is
    the constant 0 and the weight target is not: ``regime_target_constant`` is
    exactly 1 (once, not once per K: D7). Calibration profiles are all x = +1,
    so with only two distinct feature values every K has two leaves and the
    x = -1 leaf is empty: by K ``{"2": 1, "3": 1}``, total 2. The chosen K is
    2 (the rule picks the smallest K inside the margin; both maps are
    identical), so ``empty_regime_fallback_chosen == 1``. All curvatures are
    3, so ``pooled_curvature_floor == 0``.

    Tolerance: exact integers.
    """
    from dataclasses import replace
    from types import SimpleNamespace

    from lpcstudy import pipeline
    from lpcstudy.ensemble import EvaluationDraws

    config = replace(
        StudyConfig(),
        steps_per_lyapunov=2,
        horizon_max_lyapunov=2.0,
        reference_horizon_lyapunov=1.0,
        eval_horizons_lyapunov=(0.5, 1.0, 2.0),
        regime_counts=(2, 3),
        regime_max_primary=3,
        primary_threshold=0.2,
    )
    assert config.horizon_max == 4 and config.reference_horizon == 2
    n_draws, n_hor = 2, 4

    def split(n: int, x: np.ndarray, planned: bool) -> SplitData:
        e_c = np.where(x < 0, 2.0, 1.0)[:, None] * np.ones((1, n_hor))
        e_p = np.where(x < 0, 1.0, 2.0)[:, None] * np.ones((1, n_hor))
        moments = moments_from_triples(e_c, e_p, np.zeros((n, n_hor)))
        moments.kept = {
            "inputs": np.zeros((n, 1, 1)),
            "cp_err": np.zeros((n, 1, 1)),
            "plp_err": np.zeros((n, 1, 1)),
        }
        ones = np.ones((n, n_draws, n_hor))
        evals = EvaluationDraws(
            horizons=np.arange(1, n_hor + 1),
            cp_err=ones,
            plp_err=ones,
            verify_noise=np.zeros_like(ones),
            distance=np.ones((n, n_draws)),
            est_nu=np.ones((n, n_draws)),
            growth_proxy=np.repeat(x[:, None], n_draws, axis=1),
            gain_proxy=ones,
            inputs=np.zeros((n, n_draws, 1)),
            noise_sens=np.zeros((n, n_draws)),
        )
        return SplitData(moments=moments, evals=evals)

    x_con = np.concatenate([-np.ones(20), np.ones(20)])
    cell = SimpleNamespace(
        system="lorenz63",
        ctx=SimpleNamespace(embed_dim=7),
        noise=0.01,
        splits={
            "construction": split(40, x_con, True),
            "calibration": split(40, np.ones(40), True),
        },
    )
    monkeypatch.setattr(
        pipeline,
        "ProfileProxies",
        SimpleNamespace(fit=lambda *a, **k: "proxies"),
    )
    allocator_rngs: list = []
    monkeypatch.setattr(
        pipeline,
        "ErrorPredictor",
        SimpleNamespace(
            fit=lambda *a, **k: (allocator_rngs.append(k["rng"]), "predictor")[
                1
            ]
        ),
    )
    monkeypatch.setattr(
        pipeline,
        "deployable_profile",
        lambda ev, *a, **k: ev.growth_proxy[..., None],
    )
    rules = pipeline.fit_rules([cell], config)
    # WU-0002.14: the allocator network draws from
    # make_rng(seed, system, embed_dim, "allocator")
    assert len(allocator_rngs) == 1
    assert (
        allocator_rngs[0].bit_generator.state
        == make_rng(config.seed, "lorenz63", 7, "allocator").bit_generator.state
    )
    assert rules.chosen_regimes == 2
    assert rules.handled == {
        "empty_regime_fallback": 2,
        "empty_regime_fallback_by_K": {"2": 1, "3": 1},
        "empty_regime_fallback_chosen": 1,
        "pooled_curvature_floor": 0,
        "regime_target_constant": 1,
    }


def _planned_lm_arrays(n: int, kind: str):
    """Return planned LM arrays for ``n == 4`` states and 2 draws.

    (LM is the Levenberg-Marquardt estimator; the values are written out in
    the L6 test.) Oracle: residuals 1..8, accepted [0, 0, 1, 2, 3, 4, 5, 15],
    late progress on the first and the last estimate. Evaluation: residuals
    10, 20, ..., 70 and inf, accepted [0, 0, 0, 0, 2, 2, 2, 2], no late
    progress. For other ``n`` the arrays are filled with ones (shape only).
    """
    if n != 4:
        return (
            np.ones((n, 2)),
            np.ones((n, 2), dtype=np.int32),
            np.ones((n, 2), dtype=np.int32),
        )
    if kind == "oracle":
        return (
            np.arange(1.0, 9.0).reshape(4, 2),
            np.array([0, 0, 1, 2, 3, 4, 5, 15], dtype=np.int32).reshape(4, 2),
            np.array([1, 0, 0, 0, 0, 0, 0, 1], dtype=np.int32).reshape(4, 2),
        )
    return (
        np.array([10.0, 20, 30, 40, 50, 60, 70, np.inf]).reshape(4, 2),
        np.array([0, 0, 0, 0, 2, 2, 2, 2], dtype=np.int32).reshape(4, 2),
        np.zeros((4, 2), dtype=np.int32),
    )


def _counted_split(
    n: int, handled: np.ndarray, clip: dict, cp_cells: list
) -> SplitData:
    """Return a split whose moments and draws carry planned counts.

    These are the counts that ``run_cell`` would store.
    """
    moments = _flag_moments(n, cp_cells, [], horizons=(10, 30, 60))
    moments.handled, moments.clip_entries = handled, dict(clip)
    moments.lm_residual, moments.lm_accepted, moments.lm_late = (
        _planned_lm_arrays(n, "oracle")
    )
    zeros = np.zeros((n, 2, 3))
    evals = EvaluationDraws(
        horizons=moments.horizons,
        cp_err=zeros,
        plp_err=zeros,
        verify_noise=zeros,
        distance=np.zeros((n, 2)),
        est_nu=np.full((n, 2), 3.0),
        growth_proxy=np.zeros((n, 2)),
        gain_proxy=zeros,
        inputs=np.zeros((n, 2, 1)),
        noise_sens=np.zeros((n, 2)),
        handled=handled + 1,
        clip_entries={k: v + 1 for k, v in clip.items()},
    )
    evals.lm_residual, evals.lm_accepted, evals.lm_late = _planned_lm_arrays(
        n, "eval"
    )
    return SplitData(moments=moments, evals=evals)


def test_cell_handling_and_system_assembly_a11(tmp_path) -> None:
    """A11: every counter is an int, totals are sums of parts, JSON round-trips.

    Reference: hand sums. Two cells of 4 test states, 2 oracle draws (M) and 2
    evaluation draws, 3 horizons. Cell 1 has ``handled`` all 1 in the six
    columns (so each oracle column sums to 4) and the evaluation draws
    ``handled + 1`` (each sums to 8), entry totals (cp, plp, nonfinite) (1, 2,
    3) for the oracle kind and (2, 3, 4) for the evaluation kind, and one
    CP-constant entry. Cell 2 has ``handled`` all 2 with entry totals (0, 0,
    5) and (1, 1, 6), and no constant entry.

    Hand totals: ``invariant_mean_replacements``: cell 1 oracle 4 + eval 8,
    cell 2 oracle 8 + eval 12 = 32. ``error_clips`` = cell 1 (1+2+3) +
    (2+3+4) = 15, cell 2 5 + (1+1+6) = 13, total 28. ``zero_variance_corr`` =
    1 (cell 1 oracle). Oracle blocks 1, 0, 2 flags; the fit block counts 1, 1,
    0, 1. The system total of each counter equals the sum over cells, their
    evaluation sub-blocks, the oracle blocks and the fit; the run total equals
    the sum over two systems. ``json.dumps`` round-trips. The denominators
    follow n, M, E, nH.

    Tolerance: exact integers.
    """
    import json
    from types import SimpleNamespace

    from lpcstudy.ensemble import DRAW_COUNTERS
    from lpcstudy.experiments import run_handling
    from lpcstudy.oracle import StateOracles
    from lpcstudy.pipeline import ALL_COUNTERS, Study, cell_handling, cell_id

    n, m_draws, width = 4, 2, len(DRAW_COUNTERS)
    study = Study(StudyConfig(), tmp_path)
    clip_1 = {
        "error_clips_cp": 1,
        "error_clips_plp": 2,
        "error_clips_nonfinite": 3,
    }
    clip_2 = {
        "error_clips_cp": 0,
        "error_clips_plp": 0,
        "error_clips_nonfinite": 5,
    }
    one = cell_handling(
        {
            "test": _counted_split(
                n, np.ones((n, width), dtype=np.int64), clip_1, [(0, 0)]
            )
        },
        m_draws,
        30,
        0.01,
        4,
    )
    two = cell_handling(
        {
            "test": _counted_split(
                n, np.full((n, width), 2, dtype=np.int64), clip_2, []
            )
        },
        m_draws,
        30,
        0.02,
        4,
    )
    assert one["counts"]["invariant_mean_replacements"] == 4 + 8
    assert (
        one["by_kind"]["oracle"]["counts"]["invariant_mean_replacements"] == 4
    )
    assert one["by_kind"]["eval"]["counts"]["invariant_mean_replacements"] == 8
    assert two["counts"]["invariant_mean_replacements"] == 8 + 12
    assert one["counts"]["error_clips"] == (1 + 2 + 3) + (2 + 3 + 4) == 15
    assert (
        one["counts"]["error_clips_cp"] == 1 + 2
        and one["counts"]["zero_variance_corr"] == 1
    )
    assert two["counts"]["error_clips"] == 5 + (1 + 1 + 6)
    assert (
        one["denominators"]["estimates"] == n * m_draws + n * 2
        and one["denominators"]["error_entries"] == n * m_draws * 3 + n * 2 * 3
    )
    assert (
        one["denominators"]["moment_entries"] == n * 3
        and one["denominators"]["states"] == n
    )
    assert (
        one["denominators"]["eval_draws"] == n * 2
        and one["denominators"]["href_draws"] == n * m_draws + n * 2
    )
    for record in (one, two):
        for kind in record["by_kind"].values():
            assert set(kind["counts"]) == set(record["counts"])
        assert all(type(v) is int for v in record["counts"].values())
        assert all(
            record["counts"][k]
            == sum(kind["counts"][k] for kind in record["by_kind"].values())
            for k in record["counts"]
        )

    study.record_cell(
        "lorenz63", "base", cell_id("base", 0.01, 10_000, True), one
    )
    study.record_cell(
        "lorenz63", "base", cell_id("base", 0.02, 10_000, False), two
    )
    flags = np.array(
        [[0, 1, 0], [0, 0, 0], [1, 0, 1], [0, 0, 1]], dtype=np.int64
    )
    study._oracles[("lorenz63", 7, 3, "test")] = StateOracles(
        nu=np.ones(n),
        gains=np.ones((n, 2)),
        growth=np.ones(n),
        local_dim=np.ones(n),
        handled=flags,
    )
    rules = SimpleNamespace(
        proxies=SimpleNamespace(
            nu_cap=2.0,
            seeds=lambda ev, noise: (np.zeros((n, 2)), np.zeros((n, 2))),
        ),
        handled={
            "empty_regime_fallback": 1,
            "empty_regime_fallback_by_K": {"2": 1},
            "empty_regime_fallback_chosen": 1,
            "pooled_curvature_floor": 0,
            "regime_target_constant": 1,
        },
        regimes={2: None},
        chosen_regimes=2,
    )
    cell1 = SimpleNamespace(
        label="base",
        noise=0.01,
        library_size=10_000,
        horizons=np.arange(3),
        splits={
            "construction": SplitData(
                _counted_split(
                    n, np.ones((n, width), dtype=np.int64), clip_1, []
                ).moments,
                None,
            ),
            "test": _counted_split(
                n, np.ones((n, width), dtype=np.int64), clip_1, [(0, 0)]
            ),
        },
    )
    # est_nu = 3 > cap 2 on every draw; the construction split has no draws, so
    # only the test split counts.
    study.record_rules("lorenz63", cell1, rules)
    handling = study.system_handling("lorenz63", {"H1b/n_failed_resamples": 2})
    assert handling["schema"] == "lpcstudy.handling/2"  # WU-0005.4 (O1)
    assert set(handling["totals"]) == set(ALL_COUNTERS)
    assert all(type(v) is int for v in handling["totals"].values())
    evaluation = handling["cells"][cell_id("base", 0.01, 10_000, True)][
        "evaluation"
    ]
    assert evaluation["counts"] == {
        "nu_cap_clips": n * 2,
        "closed_form_floor_a4": n * 2,
        "closed_form_floor_a4o": 0,
    }
    assert evaluation["by_split"] == {"nu_cap_clips": {"test": n * 2}}
    t = handling["totals"]
    assert t["invariant_mean_replacements"] == 12 + 20
    assert t["error_clips"] == 15 + 13 and t["zero_variance_corr"] == 1
    assert (
        t["local_dim_zero_distance"],
        t["oracle_gain_floor"],
        t["oracle_nonfinite"],
    ) == (1, 1, 2)
    assert (
        t["nu_cap_clips"],
        t["closed_form_floor_a4"],
        t["closed_form_floor_a4o"],
    ) == (8, 8, 0)
    assert (
        t["empty_regime_fallback"],
        t["empty_regime_fallback_chosen"],
        t["pooled_curvature_floor"],
        t["regime_target_constant"],
    ) == (1, 1, 0, 1)
    assert handling["result_counts"] == {"H1b/n_failed_resamples": 2}
    assert handling["fitting"]["empty_regime_fallback_by_K"] == {"2": 1}
    assert handling["fitting"]["denominators"] == {
        "regimes": 2,
        "chosen_regimes": 2,
        "pools": 3 * 3,
        "targets": 2,
    }
    assert json.loads(json.dumps(handling)) == handling
    # the run level: two systems with the same block
    results = {
        "systems": {
            "lorenz63": {"handling": handling},
            "rossler": {"handling": handling},
        }
    }
    run = run_handling(study, results)
    assert (
        run["totals"] == {k: 2 * v for k, v in t.items()}
        and run["failed_variants"] == 0
    )
    assert run["by_system"]["rossler"] == t and run["robustness"] == {}
    assert json.loads(json.dumps(run)) == run


# ---------------------------------------------------------------------------
# WU-0005.4 (L6): the Levenberg-Marquardt block of the handling record. Hand
# values below.
# ---------------------------------------------------------------------------
def test_cell_handling_lm_block_hand_values() -> None:
    """L6: ``cell_handling`` builds the ``lm`` block per kind and in total.

    The block summarizes the Levenberg-Marquardt fits (median and 95th
    percentile of the final cost, iteration counts, and so on).

    Reference: hand order statistics of the planned arrays of
    ``_planned_lm_arrays`` (4 states, 2 draws each for the oracle and the
    evaluation kind), noise 0.5 so the goodness-of-fit threshold on c is
    18.4668 * 0.25 = 4.617.

    * Oracle (n = 8): residuals 1..8, median 4.5, p95 = x_(ceil(7.6)) = 8;
      accepted [0,0,1,2,3,4,5,15] has median 2.5 and 2 zeros (0.25); late
      progress 2 of 8; above 4.617: 5,6,7,8 (0.5).
    * Evaluation (n = 8): residuals 10..70 and inf, median 45, p95 = x_(8) =
      inf -> None, one infinite residual; accepted [0,0,0,0,2,2,2,2] has
      median 1, no decrease 0.5, late 0, above 1.0.
    * All (n = 16): sorted 1..8, 10..70, inf: median (8 + 10)/2 = 9, p95 =
      x_(16) = inf -> None; accepted: six zeros, 1, five 2s, 3, 4, 5, 15 ->
      median 2, no decrease 6/16, late 2/16, above 12/16.

    The check kind has no estimate: n is 0 and the values are None. The
    estimate counts equal the ``estimates`` denominators.

    Tolerance: exact (small dyadic rationals), and the record round-trips
    through JSON.
    """
    import json

    from lpcstudy.ensemble import DRAW_COUNTERS
    from lpcstudy.pipeline import cell_handling

    n, width = 4, len(DRAW_COUNTERS)
    clip = {
        "error_clips_cp": 0,
        "error_clips_plp": 0,
        "error_clips_nonfinite": 0,
    }
    record = cell_handling(
        {
            "test": _counted_split(
                n, np.ones((n, width), dtype=np.int64), clip, []
            )
        },
        2,
        30,
        0.5,
        4,
    )
    lm = record["lm"]
    oracle, evaluation, check = (
        lm["by_kind"][k] for k in ("oracle", "eval", "check")
    )
    assert (
        oracle["n_estimates"],
        oracle["median_residual"],
        oracle["p95_residual"],
    ) == (8, 4.5, 8.0)
    assert (oracle["median_iterations"], oracle["fraction_no_decrease"]) == (
        2.5,
        0.25,
    )
    assert (
        oracle["fraction_late_progress"],
        oracle["fraction_above_chi2"],
    ) == (0.25, 0.5)
    assert oracle["nonfinite_residuals"] == 0 and oracle["noise"] == 0.5
    assert (evaluation["n_estimates"], evaluation["median_residual"]) == (
        8,
        45.0,
    )
    assert (
        evaluation["p95_residual"] is None
        and evaluation["nonfinite_residuals"] == 1
    )
    assert (
        evaluation["median_iterations"],
        evaluation["fraction_no_decrease"],
    ) == (1.0, 0.5)
    assert (
        evaluation["fraction_late_progress"],
        evaluation["fraction_above_chi2"],
    ) == (0.0, 1.0)
    assert (lm["n_estimates"], lm["median_residual"], lm["p95_residual"]) == (
        16,
        9.0,
        None,
    )
    assert (lm["median_iterations"], lm["fraction_no_decrease"]) == (
        2.0,
        6 / 16,
    )
    assert (lm["fraction_late_progress"], lm["fraction_above_chi2"]) == (
        2 / 16,
        12 / 16,
    )
    assert lm["nonfinite_residuals"] == 1
    assert check["n_estimates"] == 0 and check["median_residual"] is None
    assert set(lm["by_kind"]) == {"oracle", "eval", "check"}
    assert record["denominators"]["estimates"] == lm["n_estimates"]
    assert (
        record["by_kind"]["oracle"]["denominators"]["estimates"]
        == oracle["n_estimates"]
    )
    assert (
        lm["gof_dof"]
        == oracle["gof_dof"]
        == evaluation["gof_dof"]
        == check["gof_dof"]
        == 4
    )
    # R2: with 7 degrees of freedom (D = 10, m = 3) the threshold on c is 24.32
    # * 0.25 = 6.08, so only the oracle residuals 7 and 8 exceed it (0.25,
    # against 0.5 for dof 4); dof is stored.
    wide = cell_handling(
        {
            "test": _counted_split(
                n, np.ones((n, width), dtype=np.int64), clip, []
            )
        },
        2,
        30,
        0.5,
        7,
    )
    assert wide["lm"]["by_kind"]["oracle"]["fraction_above_chi2"] == 0.25
    assert wide["lm"]["gof_dof"] == 7
    assert json.loads(json.dumps(record)) == record


def test_cell_handling_refuses_moments_without_lm_arrays() -> None:
    """``cell_handling`` raises for missing LM arrays or wrong shapes.

    Reference: construction (PRIME.4: no silent n = 0 for a cell that has
    estimates). The error names the split.

    Tolerance: exact.
    """
    from lpcstudy.ensemble import DRAW_COUNTERS
    from lpcstudy.pipeline import cell_handling

    n, width = 4, len(DRAW_COUNTERS)
    clip = {
        "error_clips_cp": 0,
        "error_clips_plp": 0,
        "error_clips_nonfinite": 0,
    }
    split = _counted_split(n, np.ones((n, width), dtype=np.int64), clip, [])
    split.moments.lm_residual = None
    with pytest.raises(ValueError, match="split 'test' moments.*Levenberg"):
        cell_handling({"test": split}, 2, 30, 0.5, 4)
    split = _counted_split(n, np.ones((n, width), dtype=np.int64), clip, [])
    split.evals.lm_residual = np.ones((n, 3))
    with pytest.raises(ValueError, match="evaluation draws.*shapes"):
        cell_handling({"test": split}, 2, 30, 0.5, 4)


def test_check_record_lm_block_and_size_check() -> None:
    """L6: ``check_record`` summarizes a validation check as the ``check`` kind.

    Reference: hand values. 2 states x 2 draws: residuals [1, 2, 3, 4] (median
    2.5, p95 = x_(ceil(3.8)) = 4), accepted [0, 1, 2, 3] (median 1.5, one
    zero: 0.25), late [0, 0, 1, 0] (0.25); noise 0.5, threshold 4.617: none
    above (0.0). The other kinds are empty, the ``lm`` of the record equals
    its ``check`` part plus ``by_kind``, and the two new counters flow through
    the handled dict. A wrong array size raises.

    Tolerance: exact.
    """
    from lpcstudy.ensemble import DRAW_COUNTERS
    from lpcstudy.pipeline import check_record

    handled = dict.fromkeys(DRAW_COUNTERS, 0)
    handled["lm_nonfinite_cost"], handled["lm_nonfinite_jacobian"] = 3, 1
    clip = {
        "error_clips_cp": 0,
        "error_clips_plp": 0,
        "error_clips_nonfinite": 0,
    }
    arrays = (
        np.array([1.0, 2.0, 3.0, 4.0]),
        np.array([0, 1, 2, 3]),
        np.array([0, 0, 1, 0]),
    )
    record = check_record(handled, clip, 2, 2, 1, 0.5, 4, arrays)
    part = record["lm"]["by_kind"]["check"]
    assert (
        part["n_estimates"],
        part["median_residual"],
        part["p95_residual"],
    ) == (4, 2.5, 4.0)
    assert (part["median_iterations"], part["fraction_no_decrease"]) == (
        1.5,
        0.25,
    )
    assert (part["fraction_late_progress"], part["fraction_above_chi2"]) == (
        0.25,
        0.0,
    )
    assert part["gof_dof"] == 4
    assert {k: v for k, v in record["lm"].items() if k != "by_kind"} == part
    assert record["lm"]["by_kind"]["oracle"]["n_estimates"] == 0
    assert (
        record["counts"]["lm_nonfinite_cost"] == 3
        and record["counts"]["lm_nonfinite_jacobian"] == 1
    )
    assert record["denominators"]["estimates"] == part["n_estimates"]
    with pytest.raises(ValueError, match="expected 4 estimates"):
        check_record(
            handled,
            clip,
            2,
            2,
            1,
            0.5,
            4,
            (arrays[0][:3], arrays[1], arrays[2]),
        )


def test_concat_stacks_lm_arrays_and_refuses_partial() -> None:
    """Stacking cells joins the LM arrays in order; a partial set raises.

    This covers ``_concat_moments`` and ``_concat_evals``.

    Reference: hand arrays (rows of residual r_i = i, accepted 2 i, late
    i mod 2, for the rows 0..4 split 3 + 2): the stack equals the whole. If
    only some parts carry them the call raises (no silent drop); if none does,
    the field stays ``None``.

    Tolerance: exact.
    """
    import dataclasses

    from lpcstudy.pipeline import _concat_evals, _concat_moments
    from unit_helpers import _moments_from_draws

    rng = np.random.default_rng(6)
    plain = [
        _moments_from_draws(
            rng.standard_normal((n, 4, 3)), rng.standard_normal((n, 4, 3))
        )
        for n in (3, 2)
    ]
    residual = np.arange(10.0).reshape(5, 2)
    accepted = (2 * np.arange(10)).reshape(5, 2).astype(np.int32)
    late = (np.arange(10) % 2).reshape(5, 2).astype(np.int32)
    parts = [
        dataclasses.replace(
            p,
            lm_residual=residual[a:b],
            lm_accepted=accepted[a:b],
            lm_late=late[a:b],
        )
        for p, (a, b) in zip(plain, ((0, 3), (3, 5)))
    ]
    stacked = _concat_moments(parts)
    assert stacked.lm_residual.tobytes() == residual.tobytes()
    assert np.array_equal(stacked.lm_accepted, accepted) and np.array_equal(
        stacked.lm_late, late
    )
    with pytest.raises(ValueError, match="only some parts"):
        _concat_moments([parts[0], plain[1]])
    assert _concat_moments(plain).lm_residual is None

    def evals(
        n: int, lo: int, hi: int, with_lm: bool = True
    ) -> EvaluationDraws:
        zeros = np.zeros((n, 2, 3))
        extra = (
            dict(
                lm_residual=residual[lo:hi],
                lm_accepted=accepted[lo:hi],
                lm_late=late[lo:hi],
            )
            if with_lm
            else {}
        )
        return EvaluationDraws(
            horizons=np.arange(1, 4),
            cp_err=zeros,
            plp_err=zeros,
            verify_noise=zeros,
            distance=np.zeros((n, 2)),
            est_nu=np.zeros((n, 2)),
            growth_proxy=np.zeros((n, 2)),
            gain_proxy=zeros,
            inputs=np.zeros((n, 2, 1)),
            noise_sens=np.zeros((n, 2)),
            **extra,
        )

    both = _concat_evals([evals(3, 0, 3), evals(2, 3, 5)])
    assert both.lm_residual.tobytes() == residual.tobytes() and np.array_equal(
        both.lm_late, late
    )
    assert (
        _concat_evals(
            [evals(3, 0, 3, False), evals(2, 3, 5, False)]
        ).lm_residual
        is None
    )
    with pytest.raises(ValueError, match="only some parts"):
        _concat_evals([evals(3, 0, 3), evals(2, 3, 5, False)])


def test_estimator_streams_are_labeled_by_system_dimension_delay_noise_and_width(
    monkeypatch, tmp_path
) -> None:
    """WU-0002.14 (b): each width trains from its own labeled random stream.

    ``Study.setup`` trains psi (the state estimator) from
    ``make_rng(seed, system, D, delay, "estimator", f"{rho:g}", width)``, one
    stream per width.

    Reference: the label written out by hand and a fresh ``make_rng`` for each
    width (the stream factory is called inside the stubbed
    ``train_estimator``, which replaces the training). The factory must return
    a generator in its initial state, different between widths, and with the
    same label for the second call of the same setup (the network is cached by
    system, D, delay and noise, so the stub runs once).

    Tolerance: none (bit-generator state equality).
    """
    from types import SimpleNamespace

    from lpcstudy import pipeline
    from lpcstudy.config import SMOKE
    from lpcstudy.systems import SYSTEMS

    streams: list = []

    def stub(inputs, targets, noise, widths, epochs, stream):
        streams.append((noise, widths, stream))
        # the stub network has the one method ``setup`` reads since WU-0003.7a
        return SimpleNamespace(
            width=widths[0], weights_digest=lambda: "0" * 64
        ), {widths[0]: 1.0}

    monkeypatch.setattr(pipeline, "train_estimator", stub)
    study = pipeline.Study(SMOKE, tmp_path)
    ctx = SimpleNamespace(
        spec=SYSTEMS["lorenz63"],
        embed_dim=7,
        delay=5,
        interval=0.03,
        estimator_inputs=np.zeros((4, 7)),
        estimator_targets=np.zeros((4, 3)),
    )
    study.setup(ctx, 0.01)
    study.setup(ctx, 0.01, n_analogs=5)
    assert len(streams) == 1
    noise, widths, stream = streams[0]
    assert noise == 0.01
    for width in (32, 64):
        expected = make_rng(
            SMOKE.seed, "lorenz63", 7, 5, "estimator", "0.01", width
        )
        assert stream(width).bit_generator.state == expected.bit_generator.state
    assert stream(32).bit_generator.state != stream(64).bit_generator.state


def test_setup_logs_the_weights_digest_of_each_trained_estimator(
    monkeypatch, tmp_path
) -> None:
    """WU-0003.7a (a2): the estimator log carries a digest of the weights.

    ``estimator_log[<key>]["weights_digest"]`` is the SHA-256 hash of the
    weights of the trained network. It is logged once per trained network (a
    cached network is not logged twice), with the existing leaves unchanged.

    Reference: ``hashlib.sha256`` of the layer arrays of a hand-built network
    (weight then bias per layer, little-endian binary64, row-major), packed
    with ``struct`` in the test. The training is replaced by a stub that
    returns that network, so the digest is independent of any training. The
    existing keys keep their values (``val_loss_by_width``, ``chosen_width``)
    and the log entry has exactly the keys val_loss_by_width, chosen_width,
    seconds and weights_digest.

    Tolerance: exact.
    """
    import hashlib
    import struct
    from types import SimpleNamespace

    from lpcstudy import pipeline
    from lpcstudy.config import SMOKE
    from lpcstudy.networks import TrainedNetwork
    from lpcstudy.systems import SYSTEMS

    params = [
        (np.array([[0.1, 0.2], [0.3, 0.4]]), np.array([0.5, -0.5])),
        (np.array([[1.0], [2.0]]), np.array([1e-7])),
    ]
    network = TrainedNetwork(
        params=params,
        in_mean=np.zeros(2),
        in_scale=np.ones(2),
        out_mean=np.zeros(1),
        out_scale=np.ones(1),
        val_loss=0.5,
        width=2,
    )
    monkeypatch.setattr(
        pipeline, "train_estimator", lambda *args: (network, {2: 0.5, 4: 0.75})
    )
    study = pipeline.Study(SMOKE, tmp_path)
    ctx = SimpleNamespace(
        spec=SYSTEMS["lorenz63"],
        embed_dim=7,
        delay=5,
        interval=0.03,
        estimator_inputs=np.zeros((4, 7)),
        estimator_targets=np.zeros((4, 3)),
    )
    study.setup(ctx, 0.01)
    study.setup(ctx, 0.01, n_analogs=5)  # cached network: no second entry
    study.setup(ctx, 0.02)
    values = [v for w, b in params for a in (w, b) for v in a.ravel().tolist()]
    expected = hashlib.sha256(
        struct.pack("<%dd" % len(values), *values)
    ).hexdigest()
    assert set(study.estimator_log) == {
        "('lorenz63', 7, 5, 0.01)",
        "('lorenz63', 7, 5, 0.02)",
    }
    for entry in study.estimator_log.values():
        assert list(entry) == [
            "val_loss_by_width",
            "chosen_width",
            "seconds",
            "weights_digest",
        ]
        assert entry["weights_digest"] == expected
        assert (
            entry["val_loss_by_width"] == {2: 0.5, 4: 0.75}
            and entry["chosen_width"] == 2
        )


def test_run_cell_asks_for_half_draw_moments_only_with_the_dump_on_for_the_base_test_split(
    monkeypatch, tmp_path
) -> None:
    """WU-0003.7b: ``run_cell`` asks for half-draw moments only with the dump.

    It passes ``half_out`` to the test split of a base cell, and only then.

    Reference: a spy on ``ensemble_moments`` and a stub for everything else
    (hand-built cells, no computation). Dump off: ``half_out`` is ``None`` in
    every call, for a core and a sweep cell. Dump on: a core cell (three
    splits) gives a dict to the ``test`` call only, and the arrays the spy put
    in it are recorded under ``(system, rho, n_lib, core)``; a sweep cell
    records under ``core = False``; a variant (label other than ``base``) gets
    no dict.

    Tolerance: exact.
    """
    from types import SimpleNamespace

    from lpcstudy import pipeline
    from lpcstudy.config import SMOKE
    from lpcstudy.dump import StateDump

    seen: list[tuple[str, bool]] = []

    def spy(
        setup,
        library,
        split,
        noise,
        horizons,
        keep_horizons=None,
        keep_draws=0,
        chunk_traj=6000,
        reference_horizon=None,
        half_out=None,
    ):
        seen.append((split, half_out is not None))
        if half_out is not None:
            half_out.update(
                {"sq_cp_A": np.zeros((2, 3)), "n_draws": np.array([1, 1])}
            )
        return SimpleNamespace(handled=None)

    monkeypatch.setattr(pipeline, "ensemble_moments", spy)
    monkeypatch.setattr(pipeline, "cell_handling", lambda *a, **k: {})
    monkeypatch.setattr(
        pipeline.AnalogLibrary, "build", classmethod(lambda cls, *a, **k: None)
    )
    ctx = SimpleNamespace(spec=SimpleNamespace(dim=3), embed_dim=7)

    def make(dump):
        study = pipeline.Study(SMOKE, tmp_path)
        study.dump = dump
        monkeypatch.setattr(
            study, "context", lambda system, embed_dim=None: ctx
        )
        monkeypatch.setattr(study, "setup", lambda *a, **k: object())
        monkeypatch.setattr(
            study, "unit_noise", lambda *a, **k: np.zeros((100, 3, 7))
        )
        monkeypatch.setattr(
            study,
            "state_oracles",
            lambda ctx, split: SimpleNamespace(subset=lambda rows: "subset"),
        )
        monkeypatch.setattr(study, "record_cell", lambda *a, **k: None)
        return study

    off = make(None)
    off.run_cell("lorenz63", 0.01, 10_000, True, False)
    off.run_cell("lorenz63", 0.02, 10_000, False, False)
    assert seen == [
        ("construction", False),
        ("calibration", False),
        ("test", False),
        ("test", False),
    ]
    seen.clear()
    dump = StateDump()
    on = make(dump)
    on.run_cell("lorenz63", 0.01, 10_000, True, False)
    on.run_cell("lorenz63", 0.02, 10_000, False, False)
    on.run_cell("lorenz63", 0.01, 10_000, True, False, label="misspec=0.05")
    assert seen == [
        ("construction", False),
        ("calibration", False),
        ("test", True),
        ("test", True),
        ("construction", False),
        ("calibration", False),
        ("test", False),
    ]
    assert set(dump._halves) == {
        ("lorenz63", 0.01, 10_000, True),
        ("lorenz63", 0.02, 10_000, False),
    }
    for record in dump._halves.values():
        assert record["n_draws"].tolist() == [1, 1]
        assert record["sq_cp_A"].shape == (2, 3)
