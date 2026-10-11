"""Tests for lpcstudy.allocation: closed-form weight and the seed proxy."""

from __future__ import annotations

import numpy as np
import pytest

from sklearn.tree import DecisionTreeRegressor

from lpcstudy import allocation
from lpcstudy.allocation import RULE_LABELS, RegimeMap, SeedProxy, closed_form_weight, \
    regime_regret
from lpcstudy.oracle import curvature, oracle_weight
from unit_helpers import _moments_from_draws, moments_from_triples, realizable_triples


def test_closed_form_matches_uncorrelated_isotropic_case() -> None:
    """With independent seeds of variances eps^2 and delta^2, w* -> delta^2/(eps^2+delta^2).

    Reference: the analytic value delta^2/(eps^2+delta^2) = 0.81/0.97 = 0.8351
    (FW Cor. 1), written out in the test (not taken from ``closed_form_weight``).
    The tested quantity is ``oracle_weight`` of plain sample moments of 200 000
    independent draws (moments from the test helper, not from ``lpcstudy.ensemble``).

    Tolerance ``abs=5e-3``: Monte Carlo error, kept unchanged. The delta-method
    standard error of the sample weight w = (b - c)/(a + b - 2c), with a, b the
    sample second moments and c the sample cross moment, at N = 200 000 is
    sqrt([(b/D^2)^2 2 a^2 + (a/D^2)^2 2 b^2 + ((b-a)/D^2)^2 a b]/N) = 8.3e-4
    (a = eps^2, b = delta^2, D = a + b), so 5e-3 is 6.0 standard errors.
    """
    rng = np.random.default_rng(2)
    eps, delta = 0.4, 0.9
    cp = eps * rng.standard_normal((1, 200_000, 1))
    plp = delta * rng.standard_normal((1, 200_000, 1))
    w_star = oracle_weight(_moments_from_draws(cp, plp))[0, 0]
    analytic = delta**2 / (eps**2 + delta**2)
    assert w_star == pytest.approx(analytic, abs=5e-3)


def test_closed_form_weight_exact_values() -> None:
    """``closed_form_weight`` equals delta^2/(eps^2+delta^2) written out by hand.

    Reference: the formula evaluated on exact rationals (FW Cor. 1): 0.16, 0.81 give
    81/97; eps^2 = 0 gives 1 (all weight on the physics forecaster); delta^2 = 0 gives 0;
    equal seeds give 1/2.
    Tolerance ``rel=1e-14``: one addition and one division in float64, a relative
    error of at most about 3 * 1.1e-16 = 3.3e-16, so 1e-14 leaves a factor of 30.
    """
    got = closed_form_weight(np.array([0.16, 0.0, 0.5, 0.3]), np.array([0.81, 2.0, 0.0, 0.3]))
    assert got == pytest.approx([81 / 97, 1.0, 0.0, 0.5], rel=1e-14, abs=0.0)


def test_seed_proxy_recovers_parameters() -> None:
    """Log-scale least squares recovers slope and floor of seed^2 = a f^2 + b g^2.

    Reference: manufactured solution. The data are generated with the known
    (a, b) = (2, 3) and multiplicative log-normal noise of sd 0.01, n = 500.
    Tolerances ``rel=0.02`` (slope) and ``rel=0.05`` (floor), kept unchanged: the
    linearized standard errors of log a and log b are the square roots of the
    diagonal of sigma^2 (J^T J)^-1, with J the Jacobian of log(seed^2) with
    respect to (log a, log b) on the test's own 500 states and sigma = 0.01: 5.8e-4
    and 1.7e-3 (relative errors of a and b). The tolerances are therefore about
    34 and 29 standard errors: loose, and they leave room for the soft-L1 loss
    (for residuals near 0.01 it differs from a quadratic by a relative z/4 = 2.5e-5,
    with z the squared residual) and the nonlinearity.
    """
    rng = np.random.default_rng(5)
    rho = 0.02
    feature = rng.uniform(0.01, 0.2, 500)
    floor = rho * rng.uniform(0.5, 2.0, 500)
    seed_sq = (2.0 * feature**2 + 3.0 * floor**2) * np.exp(0.01 * rng.standard_normal(500))
    proxy = SeedProxy.fit(feature**2, floor**2, seed_sq)
    assert proxy.slope == pytest.approx(2.0, rel=0.02)
    assert proxy.floor == pytest.approx(3.0, rel=0.05)


def test_rule_set_is_the_v3_rule_set() -> None:
    """The rule labels are exactly A0-A5, A4o and A*; A4f and its function are gone (WU-0002.1).

    Reference: proposal and methods v3 section 5 (rules A0 to A5, A4o, A*) and the decision
    log (A4f is dropped), written out in the test, not read from the code.
    Tolerance: none; equality of a discrete set of strings.
    """
    assert set(RULE_LABELS) == {"A0", "A1", "A2", "A3", "A4", "A5", "A4o", "A*"}
    assert not hasattr(allocation, "full_form_weight")


def test_regime_regret_is_mean_exact_excess() -> None:
    """``regime_regret`` is the mean over (state, draw) of V(w_k) - V(w*), not c (w_k - w*)^2.

    Reference: brute force. For each state the excess is V(w_k) - min over
    ``np.linspace(0, 1, 10_000)`` of V, with V evaluated directly from the moment triple
    (the grid argument of ``test_excess_mse_matches_grid_minimum``); the reference is the
    mean of these over the states (each state appears E = 2 times with the same regime).
    Setup: a 2-leaf tree on a 1-D synthetic profile (140 states, 2 horizon columns; the
    regret is requested at column 1). Leaf 0 holds 70 states with u in (1, 6) or [0.6, 1]
    and w_k = 0.35; leaf 1 holds 70 states with u in (-5, 0) or [0, 0.2] and w_k = 0.7, so
    |w_k - w*| >= 0.25 >= 0.1 for every state, asserted as a precondition on the weights
    the code returns. Half of the states have u outside [0, 1]. The second output is
    checked against the mean of min(E_C, E_P) written out here.
    Tolerance ``rtol=1e-6``: the grid minimum exceeds V(w*) by at most c (h/2)^2 =
    2.5e-9 c with h = 1/9999 and the excess is at least c (w_k - w*)^2 >= 0.0625 c, so the
    relative bias is at most 4e-8 (the argument of the 10-fold looser bound at 0.1);
    round-off is about 1e-12. It also asserts that the old c (w - w*)^2 mean is below the
    exact value by more than 1e-3 relative (the test would detect DEF-0002).
    """
    rng = np.random.default_rng(31)
    parts = []
    for _ in range(2):  # two horizon columns, each with its own triples
        left = realizable_triples(rng, 0, 20, 50, inside=(0.6, 1.0))
        right = realizable_triples(rng, 50, 20, 0, inside=(0.0, 0.2))
        parts.append({k: np.concatenate([left[k], right[k]]) for k in left})
    n_states = 140
    e_c = np.stack([p["E_C"] for p in parts], axis=1)
    e_p = np.stack([p["E_P"] for p in parts], axis=1)
    cross = np.stack([p["C"] for p in parts], axis=1)
    moments = moments_from_triples(e_c, e_p, cross)
    x = np.concatenate([-rng.uniform(0.5, 1.5, (70, 2)), rng.uniform(0.5, 1.5, (70, 2))])
    profile = x[:, :, None]  # (140, 2, 1)
    label = (x[:, 0] > 0).astype(float)
    tree = DecisionTreeRegressor(max_leaf_nodes=2, random_state=0)
    tree.fit(profile.reshape(-1, 1), np.repeat(label, 2))
    leaf_ids = np.nonzero(tree.tree_.children_left == -1)[0]
    regime_map = RegimeMap(tree=tree, leaf_ids=leaf_ids,
                           weights=np.array([[0.4, 0.35], [0.6, 0.7]]),
                           horizons_km=np.full(2, np.nan))
    column = 1
    regime = regime_map.assign(profile)
    assert np.array_equal(regime[:, 0], np.r_[np.zeros(70, int), np.ones(70, int)])
    w_k = regime_map.weights[regime, column]
    w_star = oracle_weight(moments)[:, column]
    assert np.all(np.abs(w_k - w_star[:, None]) >= 0.1)  # precondition of the grid reference
    unclipped = oracle_weight(moments, clip=False)[:, column]
    assert np.mean((unclipped < 0) | (unclipped > 1)) >= 0.4

    grid = np.linspace(0.0, 1.0, 10_000)

    def direct_v(weight: np.ndarray) -> np.ndarray:
        return weight**2 * e_c[:, [column]] + (1 - weight) ** 2 * e_p[:, [column]] + \
            2 * weight * (1 - weight) * cross[:, [column]]

    v_min = direct_v(grid[None, :]).min(axis=1)
    reference = float(np.mean(direct_v(w_k) - v_min[:, None]))
    regret, ratio = regime_regret(regime_map, profile, moments, column)
    assert regret == pytest.approx(reference, rel=1e-6, abs=0.0)
    best = float(np.mean(np.minimum(e_c[:, column], e_p[:, column])))
    assert ratio == pytest.approx(regret / best, rel=1e-12, abs=0.0)
    old = float(np.mean(curvature(moments)[:, [column]] * (w_k - w_star[:, None]) ** 2))
    assert old < reference * (1.0 - 1e-3)
