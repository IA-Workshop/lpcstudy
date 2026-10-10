"""Unit tests for the mathematical building blocks."""

from __future__ import annotations

import jax
import jax.numpy as jnp
import numpy as np
import pytest

from lpcstudy.allocation import SeedProxy, closed_form_weight
from lpcstudy.dynamics import delay_map_forward, make_observability
from lpcstudy.embedding import autocorrelation_time, delay_vectors, select_delay
from lpcstudy.ensemble import EnsembleMoments
from lpcstudy.oracle import characteristic_horizon, curvature, hybrid_mse, oracle_weight
from lpcstudy.statistics import holm_adjust, kaplan_meier, logrank_test, \
    partial_correlation
from lpcstudy.systems import SYSTEMS, make_flow_step, simulate_trajectory


def _moments_from_draws(cp: np.ndarray, plp: np.ndarray) -> EnsembleMoments:
    return EnsembleMoments(
        horizons=np.arange(1, cp.shape[-1] + 1), mean_cp=cp.mean(1), mean_plp=plp.mean(1),
        sq_cp=(cp**2).mean(1), sq_plp=(plp**2).mean(1), cross=(cp * plp).mean(1),
        analog_seed=np.ones(len(cp)), est_seed=np.ones(len(cp)), noise_sens=np.zeros(len(cp)))


def test_oracle_weight_minimizes_ensemble_mse() -> None:
    """w* equals the brute-force minimizer of the ensemble MSE over [0, 1]."""
    rng = np.random.default_rng(0)
    common = rng.standard_normal((5, 400, 3))
    cp = 0.5 * common + rng.standard_normal((5, 400, 3))
    plp = 0.3 * common + 0.7 * rng.standard_normal((5, 400, 3))
    moments = _moments_from_draws(cp, plp)
    grid = np.linspace(0, 1, 2001)
    brute = np.array([[grid[np.argmin([np.mean((w * cp[i, :, h] + (1 - w) * plp[i, :, h]) ** 2)
                                       for w in grid])] for h in range(3)] for i in range(5)])
    assert np.allclose(oracle_weight(moments), brute, atol=1e-3)


def test_regret_identity() -> None:
    """V(w) - V(w*) = c (w - w*)^2 for the unclipped optimum (FW Prop. 5)."""
    rng = np.random.default_rng(1)
    cp, plp = rng.standard_normal((4, 300, 2)), 0.8 * rng.standard_normal((4, 300, 2))
    moments = _moments_from_draws(cp, plp)
    w_star = oracle_weight(moments, clip=False)
    w = np.full_like(w_star, 0.3)
    lhs = hybrid_mse(moments, w) - hybrid_mse(moments, w_star)
    assert np.allclose(lhs, curvature(moments) * (w - w_star) ** 2)


def test_closed_form_matches_uncorrelated_isotropic_case() -> None:
    """With independent seeds of variances eps^2 and delta^2, w* -> delta^2/(eps^2+delta^2)."""
    rng = np.random.default_rng(2)
    eps, delta = 0.4, 0.9
    cp = eps * rng.standard_normal((1, 200_000, 1))
    plp = delta * rng.standard_normal((1, 200_000, 1))
    w_star = oracle_weight(_moments_from_draws(cp, plp))[0, 0]
    assert w_star == pytest.approx(closed_form_weight(eps**2, delta**2), abs=5e-3)


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


def test_characteristic_horizon_and_censoring() -> None:
    """First crossing of sqrt(mse + rho^2) above theta; censored rows return H_max."""
    mse = np.array([[0.0, 0.01, 0.05, 0.2], [0.0, 0.0, 0.0, 0.0]])
    horizon, event = characteristic_horizon(mse, np.arange(1, 5), 0.0, 0.2)
    assert horizon.tolist() == [3, 4] and event.tolist() == [True, False]


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


def test_partial_correlation_removes_confounder() -> None:
    """A variable related to the target only through a control has ~zero partial r."""
    rng = np.random.default_rng(6)
    z = rng.standard_normal(5000)
    x = z + 0.1 * rng.standard_normal(5000)
    y = z + 0.1 * rng.standard_normal(5000)
    assert abs(partial_correlation(y, x, z[:, None])) < 0.05


def test_delay_vectors_order() -> None:
    """X_t = (x_t, x_{t-tau}, ...)."""
    series = np.arange(20.0)
    out = delay_vectors(series, np.array([10]), 3, 3)
    assert out.tolist() == [[10.0, 7.0, 4.0]]


def test_delay_and_acf() -> None:
    """AMI delay of Lorenz-63 x at 1 LT = 30 steps lies near 0.15-0.2 time units;
    a pure sine is phase-coherent and never decorrelates."""
    spec = SYSTEMS["lorenz63"]
    step = make_flow_step(spec, spec.params, 0.0368)
    x = simulate_trajectory(step, jnp.asarray(spec.initial_state), 60_000)[5_000:, 0]
    assert 3 <= select_delay((x - x.mean()) / x.std(), 60) <= 8
    t = np.arange(20_000)
    assert autocorrelation_time(np.sin(2 * np.pi * t / 40), 500) == 500


def test_observability_matches_independent_jacobians() -> None:
    """nu from the scan-based forward formula equals tr[W Q (A^T A)^{-1} Q^T W^T]
    with A and Q obtained by independent automatic differentiation of the forward
    delay map and of the flow over the window. (Forming J = A Q^{-1} explicitly is
    avoided: cond(Q) ~ 1e7 makes J^T J numerically singular, which is why the
    forward formula is used.)"""
    spec = SYSTEMS["lorenz63"]
    step = make_flow_step(spec, spec.params, 0.0368)
    traj = simulate_trajectory(step, jnp.asarray(spec.initial_state), 3000)[2000:]
    delay, dim = 5, 7
    whiten = np.eye(3) / traj.std(axis=0)
    nu_fn = make_observability(step, 0, 7.9, whiten, delay, dim)
    fwd = delay_map_forward(step, 0, 0.0, 7.9, delay, dim)
    span = (dim - 1) * delay
    advance = lambda s: jax.lax.fori_loop(0, span, lambda _, x: step(x), s)
    for s_old in traj[:3]:
        a_mat = np.asarray(jax.jacfwd(fwd)(jnp.asarray(s_old)))
        q_mat = np.asarray(jax.jacfwd(advance)(jnp.asarray(s_old)))
        cov = whiten @ q_mat @ np.linalg.inv(a_mat.T @ a_mat) @ q_mat.T @ whiten.T
        got = float(nu_fn(jnp.asarray(s_old[None, :]))[0])
        assert got == pytest.approx(np.sqrt(np.trace(cov)), rel=1e-8)


def test_per_state_spearman_handles_ties() -> None:
    """A state whose weight is clipped to 0 at every level has no trend (rho = 0)."""
    from lpcstudy.analysis import _per_state_spearman

    values = np.array([[0.0, 0.0, 0.0, 0.0], [0.1, 0.2, 0.3, 0.4], [0.4, 0.3, 0.2, 0.1]])
    rho = _per_state_spearman(np.array([1.0, 2.0, 3.0, 4.0]), values)
    assert np.allclose(rho, [0.0, 1.0, -1.0])


def test_retrieval_spread() -> None:
    """Noise sensitivity is 0 for a fixed analog and ~1 for unit-noise wander."""
    from lpcstudy.ensemble import retrieval_spread

    fixed = np.ones((1, 50, 7))
    assert retrieval_spread(fixed, 0.1)[0] == 0.0
    wander = 0.1 * np.random.default_rng(8).standard_normal((1, 20_000, 7))
    assert retrieval_spread(wander, 0.1)[0] == pytest.approx(1.0, rel=0.02)
