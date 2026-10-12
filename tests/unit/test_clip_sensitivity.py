"""Tests for lpcstudy.clip_sensitivity (WU-0002.11e): the clip-sensitivity flag of the verdicts.

Every reference is deterministic and independent of the code under test: hand arithmetic on dyadic
numbers (T1, T3, T5, T7, T12), exact rational arithmetic (T4, ``fractions.Fraction``), the production
``clip_errors`` at the doubled level (T2), and the production verdict functions run on a world whose
errors were clipped at 20 sigma_x from the raw values (the brute-force world of the T-world tests).
Tolerances are stated in each docstring and were fixed before the first run.
"""

from __future__ import annotations

import dataclasses
import logging
import math
from fractions import Fraction
from types import SimpleNamespace

import numpy as np
import pytest

from lpcstudy import analysis as an
from lpcstudy import clip_sensitivity as cs
from lpcstudy.allocation import ProfileProxies, SeedProxy, calibrate_regimes, deployable_profile, \
    fit_regime_tree, global_weight, regime_weight
from lpcstudy.config import SMOKE
from lpcstudy.ensemble import DRAW_COLUMN, DRAW_COUNTERS, ENTRY_COUNTERS, DrawBatch, \
    EnsembleMoments, EvaluationDraws, clip_errors, draw_correlation, ensemble_moments, \
    evaluation_draws, forecast_draws
from lpcstudy.oracle import oracle_weight
from lpcstudy.pipeline import FittedRules, SplitData, rule_weights, score_rules

LEVEL = 10.0


# ----------------------------------------------------------------------------------- helpers
def _moments(sq_cp, sq_plp, cross, handled=None, chi=None) -> EnsembleMoments:
    """Hand-built moments, one horizon, ``(n, 1)`` second moments."""
    n = len(sq_cp)
    col = lambda x: np.asarray(x, dtype=float).reshape(n, 1)
    return EnsembleMoments(
        horizons=np.array([30]), mean_cp=np.zeros((n, 1)), mean_plp=np.zeros((n, 1)),
        sq_cp=col(sq_cp), sq_plp=col(sq_plp), cross=col(cross), analog_seed=np.ones(n),
        est_seed=np.ones(n), noise_sens=np.zeros(n), handled=handled,
        clip_cross_ref=None if chi is None else np.asarray(chi, dtype=float))


def _handled(plp_href, nonfinite_href) -> np.ndarray:
    """A ``handled`` array with only the two H_ref clip columns set."""
    out = np.zeros((len(plp_href), len(DRAW_COUNTERS)), dtype=np.int64)
    out[:, DRAW_COLUMN["error_clips_plp_href"]] = plp_href
    out[:, DRAW_COLUMN["error_clips_nonfinite_href"]] = nonfinite_href
    return out


def _planned_batch(cp_err, plp_err, sign, handled) -> DrawBatch:
    """A ``DrawBatch`` with planned errors, signs and counts; the other fields are dummies."""
    n, m = cp_err.shape[:2]
    return DrawBatch(
        cp_err=cp_err, plp_err=plp_err, analog_seed_sq=np.ones((n, m)), est_seed_sq=np.ones((n, m)),
        distance=np.ones((n, m)), inputs=np.zeros((n, m, 2)), est_states=np.zeros((n, m, 2)),
        est_nu=np.ones((n, m)), analog_vecs=np.zeros((n, m, 2)), handled=handled,
        clip_entries={name: 0 for name in ENTRY_COUNTERS},
        lm_residual=np.zeros((n, m)), lm_accepted=np.zeros((n, m), dtype=np.int32),
        lm_late=np.zeros((n, m), dtype=np.int32), clip_sign_ref=sign)


def _planned_lm(n_flat: int):
    from lpcstudy.estimation import LMDiagnostics

    rows = np.arange(n_flat)
    return LMDiagnostics(residual=rows + 0.5, accepted=(2 * rows).astype(np.int32),
                         nonfinite_cost=np.zeros(n_flat, dtype=bool),
                         nonfinite_jacobian=np.zeros(n_flat, dtype=bool),
                         late_progress=(rows % 2).astype(np.int32))


def _fake_world(plp_diff: np.ndarray, horizons: np.ndarray, n_states: int, n_draws: int):
    """A miniature deterministic world for the real ``forecast_draws`` (stubbed estimator and PLP path).

    The PLP path is the truth plus the planned error ``plp_diff`` (flat state-major
    ``(n_states * n_draws, nH)``); CP errors are differences of unit normals (far below 10).
    """
    from scipy.spatial import cKDTree

    from lpcstudy.embedding import delay_vectors
    from lpcstudy.ensemble import AnalogLibrary, ForecastSetup

    rng = np.random.default_rng(777)
    horizons = np.asarray(horizons)
    n_time, n_lib = 300, 200
    ctx = SimpleNamespace(
        eval_clean=rng.standard_normal(n_time), eval_states=rng.standard_normal((n_time, 2)),
        library_states=rng.standard_normal((n_lib, 2)), delay=1, embed_dim=3,
        split_indices={"test": np.arange(100, 100 + n_states)}, whiten_states=lambda x: x)
    series = rng.standard_normal(n_lib)
    indices = np.arange(2, n_lib - 10)
    library = AnalogLibrary(indices=indices, noisy_series=series,
                            tree=cKDTree(delay_vectors(series, indices, 1, 3)))
    truth = ctx.eval_clean[ctx.split_indices["test"][:, None] + horizons[None, :]]
    truth_flat = np.repeat(truth, n_draws, axis=0)
    h_last = int(horizons[-1])

    def paths(states):
        out = np.zeros((len(states), h_last))
        out[:, horizons - 1] = truth_flat + plp_diff
        return out

    class Stub:
        def estimate_counted(self, flat):
            n_flat = len(flat)
            return (np.full((n_flat, 2), 0.1), np.ones(n_flat), np.zeros(n_flat, dtype=bool),
                    np.zeros(n_flat, dtype=bool), _planned_lm(n_flat))

    setup = ForecastSetup(ctx=ctx, noise=0.01, estimator=Stub(), model_step=None)
    setup._paths[h_last] = paths
    noise = np.random.default_rng(778).standard_normal((n_states, n_draws, 3))
    return setup, library, noise, np.arange(n_states), truth


# ------------------------------------------------------------------ T1, T11: the stored arrays
def test_t1_moments_and_increments_to_the_doubled_clip_by_hand(monkeypatch) -> None:
    """T1: two states, M = 4, one horizon: the moments at L, chi and q, and the increments to 2L.

    Reference: hand arithmetic, every number dyadic so every sum and the divisions by 4 are exact.
    State 0: e_C = 0.5 four times, raw e_P = [0.25, 0.25, 0.25, +inf], stored [0.25, 0.25, 0.25, 10]:
    E e_P^2 = (3 * 0.0625 + 100) / 4 = 25.046875, E e_C e_P = (3 * 0.125 + 5) / 4 = 1.34375,
    chi = (+1 * 0.5) / 4 = 0.125, q = 1 (non-finite). State 1: e_C = 0.25, raw e_P = [-0.5, -0.5,
    -0.5, -64], stored [..., -10]: E e_P^2 = (3 * 0.25 + 100) / 4 = 25.1875, E e_C e_P =
    (3 * (-0.125) + (-2.5)) / 4 = -0.71875, chi = (-1 * 0.25) / 4 = -0.0625, q = 1 (finite clip).
    At 2L = 20: state 0 E e_P^2 = (0.1875 + 400) / 4 = 100.046875 (= 25.046875 + 3 * 100 / 4) and
    E e_C e_P = (0.375 + 10) / 4 = 2.59375 (= 1.34375 + 10 * 0.125); state 1: 100.1875 and -1.34375.
    The signs and counts are planned inputs of a stubbed ``forecast_draws``; ``ensemble_moments`` forms
    the moments and chi (the code under test). Exact (``==``).
    """
    cp_raw = np.array([[[0.5]] * 4, [[0.25]] * 4])
    plp_raw = np.array([[[0.25], [0.25], [0.25], [np.inf]], [[-0.5], [-0.5], [-0.5], [-64.0]]])
    cp_err, plp_err, masks = clip_errors(cp_raw, plp_raw, np.zeros((2, 1, 1)))
    sign = np.array([[0, 0, 0, 1], [0, 0, 0, -1]], dtype=np.int8)
    handled = _handled([0, 1], [1, 0])
    import lpcstudy.ensemble as ensemble

    monkeypatch.setattr(ensemble, "forecast_draws", lambda setup, library, split, rows, noise,
                        horizons, reference_horizon=None: _planned_batch(
                            cp_err[rows], plp_err[rows], sign[rows], handled[rows]))
    for chunk in (4, 10**6):  # one state per chunk, and both states in one chunk
        again = ensemble_moments(SimpleNamespace(noise=0.01), None, "test", np.zeros((2, 4, 2)),
                                 np.array([1]), chunk_traj=chunk, reference_horizon=1)
        assert again.clip_cross_ref.tolist() == [0.125, -0.0625]
    moments = ensemble_moments(SimpleNamespace(noise=0.01), None, "test", np.zeros((2, 4, 2)),
                               np.array([1]), reference_horizon=1)
    assert moments.sq_plp[:, 0].tolist() == [25.046875, 25.1875]
    assert moments.cross[:, 0].tolist() == [1.34375, -0.71875]
    assert moments.clip_cross_ref.tolist() == [0.125, -0.0625]
    assert cs.clipped_draws(moments.handled).tolist() == [1, 1]
    after = cs.perturb_moments(moments, 0, 4)
    assert after.sq_plp[:, 0].tolist() == [100.046875, 100.1875]
    assert after.cross[:, 0].tolist() == [2.59375, -1.34375]
    assert after.sq_cp.tolist() == moments.sq_cp.tolist()
    # the same numbers from the raw entries clipped at 20 by the production function (independent path)
    cp2, plp2, _ = clip_errors(cp_raw, plp_raw, np.zeros((2, 1, 1)), clip=20.0)
    assert (plp2**2).mean(axis=1)[:, 0].tolist() == after.sq_plp[:, 0].tolist()
    assert (cp2 * plp2).mean(axis=1)[:, 0].tolist() == after.cross[:, 0].tolist()
    # the input moments are not modified
    assert moments.sq_plp[:, 0].tolist() == [25.046875, 25.1875]


def test_t2_increment_path_equals_a_direct_clip_at_twice_the_level() -> None:
    """T2: 10^4 random entries with injected non-finite and |raw| > 2L values.

    Reference: ``clip_errors(..., clip=20)`` of the planned raw errors (the production function at
    the doubled level), then fresh moments, at the H_ref column. Data: 100 states x 50 draws x 2
    horizons (10^4 entries), PLP error 2 N(0, 1) with 300 injected entries from
    {+inf, -inf, NaN, 37, -25, 1e9, -1e9, 22, -41} (none in (10, 20), asserted). The real
    ``forecast_draws`` runs on a stubbed estimator and path. Tolerance: rtol 1e-13, atol 1e-14. The
    two paths differ in the summation order of at most M = 50 terms (bound M u = 5.5e-15 relative)
    and in the round trip ``(truth + diff) - truth`` of the unclipped entries (at most
    2 u |truth| <= 1e-15 absolute per entry, averaged); the stored CP errors are the same in both.
    """
    n_states, n_draws, horizons, ref = 100, 50, np.array([1, 2]), 2
    rng = np.random.default_rng(2002)
    diff = 2.0 * rng.standard_normal((n_states * n_draws, 2))
    special = np.array([np.inf, -np.inf, np.nan, 37.0, -25.0, 1e9, -1e9, 22.0, -41.0])
    where = rng.choice(diff.size, size=300, replace=False)
    diff.reshape(-1)[where] = special[np.arange(300) % len(special)]
    finite = diff[np.isfinite(diff)]
    assert not np.any((np.abs(finite) > 10.0) & (np.abs(finite) < 20.0))  # premise: none in (L, 2L)
    setup, library, noise, rows, _ = _fake_world(diff, horizons, n_states, n_draws)
    batch = forecast_draws(setup, library, "test", rows, noise, horizons, reference_horizon=ref)
    moments = ensemble_moments(setup, library, "test", noise, horizons, reference_horizon=ref)
    assert np.abs(batch.cp_err).max() < LEVEL  # H-CP holds in the fixture
    assert moments.clip_cross_ref is not None and moments.handled[:, 4:6].sum() > 100
    after = cs.perturb_moments(moments, 1, n_draws)
    raw = diff.reshape(n_states, n_draws, 2)
    _, plp2, _ = clip_errors(batch.cp_err, raw, np.zeros((n_states, 1, 2)), clip=20.0)
    ref_sq = (plp2[:, :, 1] ** 2).mean(axis=1)
    ref_cross = (batch.cp_err[:, :, 1] * plp2[:, :, 1]).mean(axis=1)
    np.testing.assert_allclose(after.sq_plp[:, 1], ref_sq, rtol=1e-13, atol=1e-14)
    np.testing.assert_allclose(after.cross[:, 1], ref_cross, rtol=1e-13, atol=1e-14)
    assert after.sq_plp[:, 0].tobytes() == moments.sq_plp[:, 0].tobytes()  # the other horizon: bitwise
    assert after.cross[:, 0].tobytes() == moments.cross[:, 0].tobytes()


def test_t11_forecast_draws_signs_and_chi_are_consistent_with_the_counts() -> None:
    """T11: ``clip_sign_ref`` and ``clip_cross_ref`` on the WU-0002.11a ``forecast_draws`` fixture.

    Reference: the plan of that fixture, read off by hand. 4 states x 3 draws, horizons (1, 2, 3),
    H_ref = 2; PLP error plan (flat row = 3 state + draw): row 0 col 1 = +inf (state 0, draw 0,
    sign +1), row 1 col 1 = -25 (state 0, draw 1, sign -1), row 1 col 0 = NaN (not at H_ref), row 5
    col 2 = 12 (not at H_ref), row 9 col 1 = -10.0 exactly (not a clip), row 10 col 1 = 11 (state 3,
    draw 1, sign +1). So ``clip_sign_ref`` = [[1, -1, 0], [0, 0, 0], [0, 0, 0], [0, 1, 0]] (int8) and
    sum |sign| per state = the two ``handled`` H_ref columns = [2, 0, 0, 1]. chi_i = (1/3) sum
    sign e_C over the clipped draws, with e_C the returned CP errors at H_ref. Exact (``==``): at most
    two nonzero terms are added in the same order as the loop.
    """
    n_states, n_draws, horizons = 4, 3, np.array([1, 2, 3])
    diff = np.zeros((12, 3))
    diff[0, 1], diff[1, 1], diff[1, 0], diff[5, 2], diff[9, 1], diff[10, 1] = \
        np.inf, -25.0, np.nan, 12.0, -10.0, 11.0
    setup, library, noise, rows, _ = _fake_world(diff, horizons, n_states, n_draws)
    batch = forecast_draws(setup, library, "test", rows, noise, horizons, reference_horizon=2)
    expected = np.array([[1, -1, 0], [0, 0, 0], [0, 0, 0], [0, 1, 0]], dtype=np.int8)
    assert batch.clip_sign_ref.dtype == np.int8 and batch.clip_sign_ref.shape == (4, 3)
    np.testing.assert_array_equal(batch.clip_sign_ref, expected)
    np.testing.assert_array_equal(np.abs(batch.clip_sign_ref).sum(axis=1),
                                  cs.clipped_draws(batch.handled))
    assert cs.clipped_draws(batch.handled).tolist() == [2, 0, 0, 1]
    e_c = batch.cp_err[:, :, 1]
    chi = [(1.0 * e_c[0, 0] + -1.0 * e_c[0, 1]) / 3, 0.0, 0.0, 1.0 * e_c[3, 1] / 3]
    moments = ensemble_moments(setup, library, "test", noise, horizons, reference_horizon=2)
    assert moments.clip_cross_ref.tolist() == chi
    np.testing.assert_array_equal(moments.handled, batch.handled)
    part = moments.subset(np.array([3, 0]))
    assert part.clip_cross_ref.tolist() == [chi[3], chi[0]]
    plain = forecast_draws(setup, library, "test", rows, noise, horizons)  # no reference horizon
    assert plain.clip_sign_ref is None
    assert ensemble_moments(setup, library, "test", noise, horizons).clip_cross_ref is None


def test_t11_evaluation_draws_carry_and_subset_the_sign_array(monkeypatch) -> None:
    """T11 (evaluation kind): ``clip_sign_ref`` is stacked for any chunking, sliced by ``subset``,
    and ``None`` when the batches carry none.

    Reference: planned signs (random ints from ``np.random.default_rng(91)`` mapped to -1, 0, 1)
    returned by a stubbed ``forecast_draws``; the expected array is the plan itself. Exact.
    """
    import lpcstudy.ensemble as ensemble

    n_states, n_draws, dim, n_hor = 6, 4, 2, 3
    rng = np.random.default_rng(91)
    sign = (rng.integers(0, 3, size=(n_states, n_draws)) - 1).astype(np.int8)
    cp = rng.standard_normal((n_states, n_draws, n_hor))
    plp = rng.standard_normal((n_states, n_draws, n_hor))
    handled = np.zeros((n_states, len(DRAW_COUNTERS)), dtype=np.int64)
    handled[:, 4] = (sign > 0).sum(axis=1)
    handled[:, 5] = (sign < 0).sum(axis=1)
    state = {"with_sign": True}

    def fake(setup, library, split, rows, unit_noise, horizons, reference_horizon=None):
        batch = _planned_batch(cp[rows], plp[rows], sign[rows] if state["with_sign"] else None,
                               handled[rows].copy())
        batch.est_states = np.stack([np.arange(len(rows) * n_draws, dtype=float).reshape(
            len(rows), n_draws), np.zeros((len(rows), n_draws))], axis=-1)
        batch.inputs = unit_noise
        batch.analog_vecs = np.zeros((len(rows), n_draws, dim))
        return batch

    monkeypatch.setattr(ensemble, "forecast_draws", fake)
    gains = np.ones((n_states * n_draws, 5))
    setup = SimpleNamespace(noise=0.01, n_analogs=1,
                            amplification=lambda steps: (lambda states: gains[:len(states)]))
    library = SimpleNamespace(query=lambda v, k: (np.zeros((len(v), k), dtype=np.int64),
                                                  np.zeros((len(v), k))),
                              analog_vectors=lambda idx: np.zeros((len(idx), dim)))
    args = (setup, library, "test", np.zeros((n_states, n_draws, dim)),
            np.zeros((n_states, n_draws, 5)), np.array([1, 3, 5]), 4,
            np.zeros((n_states, n_draws, 3, dim)))
    for chunk in (4, 10**6):
        out = evaluation_draws(*args, chunk_traj=chunk, reference_horizon=3)
        np.testing.assert_array_equal(out.clip_sign_ref, sign)
    np.testing.assert_array_equal(out.subset(np.array([4, 0])).clip_sign_ref, sign[[4, 0]])
    state["with_sign"] = False
    assert evaluation_draws(*args, reference_horizon=3).clip_sign_ref is None


# -------------------------------------------------------------------- T3, T4, T5: the formulas
def test_t3_hybrid_squared_error_is_not_bounded_by_three_h_squared() -> None:
    """T3: one hybrid draw, w = 1/2, e_C = -5, raw e_P = +inf: h^2 = 6.25 -> 56.25, change 50.

    Reference: hand arithmetic and the closed form of the plan, 3 (1 - w)^2 L^2 + 2 w (1 - w) sigma
    L e_C = 3 (0.25) 100 + 2 (0.25) 10 (-5) = 75 - 25 = 50, which is 8 h^2 (so ``3 s`` is not a bound
    for a hybrid). All values dyadic, exact.
    """
    cp, plp = np.array([[-5.0]]), np.array([[LEVEL]])  # the stored error of a +inf PLP forecast
    sign = np.array([[1]], dtype=np.int8)
    weight = np.array([[0.5]])
    before = cs.rule_state_mse(weight, cp, plp)[0]
    after = cs.rule_state_mse(weight, cp, cs.perturb_errors(plp, sign))[0]
    assert (before, after) == (6.25, 56.25)
    assert after - before == 50.0 == 3 * 0.25 * 100.0 + 2 * 0.5 * 0.5 * 10.0 * -5.0 == 8 * before


def test_t4_global_and_regime_weights_after_the_increment_equal_exact_rationals() -> None:
    """T4: A2' and A5' on the T1 pool plus a third state, against ``fractions.Fraction``.

    Reference: the raw entries clipped at 2L by hand, every moment as an exact rational
    (``Fraction`` of dyadic floats), then ``clip(sum b / sum c, 0, 1)`` with ``b = E e_P^2 - E e_C
    e_P`` and ``c = E e_C^2 + E e_P^2 - 2 E e_C e_P`` (the definition of the pooled weight, P3(a)),
    exactly. States 0 and 1 are those of T1 (E e_C^2 = 0.25, 0.0625); state 2 has e_C = 8, e_P = 0.5
    four times (E e_C^2 = 64, E e_P^2 = 0.25, E e_C e_P = 4, no clip). Tolerance: 2 ulp. Every moment
    is dyadic, so the sums are exact in float64 and only the one division rounds (0.5 ulp).
    """
    e_c = [[0.5] * 4, [0.25] * 4, [8.0] * 4]
    e_p = [[0.25, 0.25, 0.25, LEVEL], [-0.5, -0.5, -0.5, -LEVEL], [0.5] * 4]
    e_p2 = [[0.25, 0.25, 0.25, 20.0], [-0.5, -0.5, -0.5, -20.0], [0.5] * 4]

    def moment(rows):
        return [sum(Fraction(x) for x in r) / 4 for r in rows]

    def exact(members):
        sq_c = moment([[Fraction(x) ** 2 for x in r] for r in e_c])
        sq_p = moment([[Fraction(x) ** 2 for x in r] for r in e_p2])
        cross = moment([[Fraction(a) * Fraction(b) for a, b in zip(rc, rp)]
                        for rc, rp in zip(e_c, e_p2)])
        num = sum(sq_p[i] - cross[i] for i in members)
        den = sum(sq_c[i] + sq_p[i] - 2 * cross[i] for i in members)
        return float(min(max(num / den, Fraction(0)), Fraction(1)))

    sq_cp = [0.25, 0.0625, 64.0]
    sq_plp = [25.046875, 25.1875, 0.25]  # at L, by hand (T1)
    cross = [1.34375, -0.71875, 4.0]
    moments = _moments(sq_cp, sq_plp, cross, _handled([0, 1, 0], [1, 0, 0]), [0.125, -0.0625, 0.0])
    after = cs.perturb_moments(moments, 0, 4)
    pool = [(global_weight(after)[0], exact([0, 1, 2])),
            (regime_weight(after, np.array([0, 2, 2]))[0], exact([0, 2, 2])),  # a state with two draws
            (regime_weight(after, np.array([0, 1]))[0], exact([0, 1]))]
    for code, reference in pool:
        assert abs(code - reference) <= 2 * np.spacing(reference), (code, reference)
    assert 0.0 < pool[0][1] < 1.0 and 0.0 < pool[1][1] < 1.0  # interior cases, not both at a clip
    assert pool[2][1] == 1.0  # the T1 pool alone: sum b / sum c = 198.984375 / 198.046875 > 1


def test_t5_h1b_increment_for_one_clipped_draw_at_m_200_is_one_and_a_half() -> None:
    """T5: q = 1 and M = 200 add exactly 3 L^2 q / M = 1.5 to E e_P^2 (the H1b path).

    Reference: 3 * 100 * 1 / 200 = 1.5 by hand. E e_P^2 = 4.0 -> 5.5, exact in binary; a state with
    q = 0 gets + 0.0 (bitwise unchanged); the first moment and the other column are not touched.
    """
    moments = _moments([1.0, 1.0], [4.0, 4.0], [0.0, 0.0], _handled([0, 1], [0, 0]), [0.0, 0.0])
    after = cs.perturb_moments(moments, 0, 200)
    assert after.sq_plp[:, 0].tolist() == [4.0, 5.5]
    assert after.sq_plp[0, 0].tobytes() == moments.sq_plp[0, 0].tobytes()
    assert after.cross[:, 0].tolist() == [0.0, 0.0]


def test_perturb_moments_refuses_moments_without_the_arrays() -> None:
    """Hand-built moments (no ``handled`` or no ``clip_cross_ref``) raise instead of passing as 'no clip'."""
    with pytest.raises(ValueError, match="clip_cross_ref"):
        cs.perturb_moments(_moments([1.0], [1.0], [0.0], _handled([0], [0]), None), 0, 4)
    with pytest.raises(ValueError, match="handled"):
        cs.perturb_moments(_moments([1.0], [1.0], [0.0], None, [0.0]), 0, 4)


# ------------------------------------------------------------------- T7, T12: the rule and bound
def test_t7_flag_edge_is_exact_and_degenerate_intervals_are_handled() -> None:
    """T7: the flag rule at its edge, with a changed verdict, hw = 0 and an infinite bound.

    Reference: hand arithmetic. (delta, lo, hi) = (0.0625, -0.625, 0.625): hw = 0.625 and
    10 * 0.0625 = 0.625 exactly, so the strict inequality is False; with ``nextafter(0.0625, 1)`` it
    is True; -delta behaves as +delta; hw = 0 and delta != 0 gives True (10 |delta| > 0), delta = 0
    gives False; hi = +inf leaves only the verdict clause and no ratio; a changed verdict flags with
    delta = 0. The ratio is |delta| / hw (None when hw is 0 or not finite). Exact.
    """
    edge = (-0.625, 0.625)
    assert cs.flag_rule(0.0625, *edge, "pass", "pass") == (False, 0.1)
    above = math.nextafter(0.0625, 1.0)
    assert cs.flag_rule(above, *edge, "pass", "pass")[0] is True
    assert cs.flag_rule(-0.0625, *edge, "pass", "pass")[0] is False
    assert cs.flag_rule(-above, *edge, "pass", "pass")[0] is True
    assert cs.flag_rule(1e-300, 1.0, 1.0, "pass", "pass") == (True, None)  # hw = 0, delta != 0
    assert cs.flag_rule(0.0, 1.0, 1.0, "pass", "pass") == (False, None)
    assert cs.flag_rule(0.0, *edge, "pass", "inconclusive") == (True, 0.0)
    assert cs.flag_rule(5.0, -math.inf, math.inf, "pass", "pass") == (False, None)  # only clause 2
    assert cs.flag_rule(5.0, 0.0, math.inf, "pass", "fail") == (True, None)


def test_part_entry_reports_what_cannot_be_computed_and_never_a_false_flag() -> None:
    """``part_entry``: absent or non-finite T or T2 gives ``not_computed`` with a reason and no flag.

    Reference: the plan's section 4 ("T or T2 not finite, or the part is not computable:
    status = not_computed, flag absent: visible, not False"). Exact.
    """
    good = cs.part_entry(1.0, [0.5, 1.5], "pass", 1.25, [0.6, 1.6], "pass", 3)
    assert good == {"status": "computed", "reason": None, "delta": 0.25, "ratio": 0.5, "flag": True,
                    "verdict_2L": "pass", "n_clipped_inputs": 3}
    for args in ((None, None, "inconclusive", 1.0, [0, 1], "pass"),
                 (math.nan, [0, 1], "inconclusive", 1.0, [0, 1], "pass"),
                 (1.0, [0, 1], "pass", math.inf, [0, 1], "pass"),
                 (1.0, [0, 1], "pass", None, None, "pass")):
        entry = cs.part_entry(*args, 0)
        assert entry["status"] == "not_computed" and entry["reason"] and entry["flag"] is None
        assert entry["delta"] is None and entry["verdict_2L"] is None
    assert cs.aggregate_flag({"a": good, "b": entry}) is True  # a fired part decides
    unfired = cs.part_entry(1.0, [0.0, 2.0], "pass", 1.0, [0.0, 2.0], "pass", 0)
    assert unfired["flag"] is False and cs.part_state(unfired) == "none"
    assert cs.aggregate_flag({"a": unfired, "b": entry}) is None  # not computed is not False
    assert cs.aggregate_flag({"a": unfired}) is False


def test_t12_median_bound_by_hand_and_by_brute_force() -> None:
    """T12: the bound on the median when a states change, by hand and by enumeration.

    Reference: (a) d = [-1, 0, 1, 2, 3], a = 1: median d(3) = 1, limits d(2) = 0 and d(4) = 2, so the
    bound is 1. (b) even n = 6: d = [0, 1, 2, 4, 7, 11], a = 1: median (2 + 4) / 2 = 3, limits
    (1 + 2) / 2 = 1.5 and (4 + 7) / 2 = 5.5, so the bound is max(1.5, 2.5) = 2.5. (c) a > m with the
    range limits +-2: d = [-1.5, -1, -0.5], a = 2: median -1, the lower index 0 is the limit -2, the
    upper index 4 is the limit +2, so the bound is 2 - (-1) = 3; a = 0 gives 0. (d) enumeration: for
    random d in [-2, 2] with n <= 7 and a <= 3, the largest |median change| over every choice of at
    most a positions replaced by -2 or +2 (the extremes suffice, the median is monotone in each value)
    equals the bound. Exact (the arithmetic is on short dyadic or random floats and the same order
    statistics, no rounding differences).
    """
    assert cs.median_bound(np.array([-1.0, 0.0, 1.0, 2.0, 3.0]), 1) == 1.0
    assert cs.median_bound(np.array([11.0, 0.0, 7.0, 1.0, 4.0, 2.0]), 1) == 2.5
    assert cs.median_bound(np.array([-1.5, -1.0, -0.5]), 2) == 3.0
    assert cs.median_bound(np.array([-1.5, -1.0, -0.5]), 0) == 0.0
    import itertools

    rng = np.random.default_rng(1212)
    for _ in range(40):
        n = int(rng.integers(1, 8))
        a = int(rng.integers(0, 4))
        d = rng.uniform(-2.0, 2.0, n)
        best = 0.0
        for k in range(min(a, n) + 1):
            for positions in itertools.combinations(range(n), k):
                for values in itertools.product((-2.0, 2.0), repeat=k):
                    changed = d.copy()
                    changed[list(positions)] = values
                    best = max(best, abs(float(np.median(changed)) - float(np.median(d))))
        assert cs.median_bound(d, a) == pytest.approx(best, rel=0, abs=1e-15), (d, a)
    with pytest.raises(ValueError):
        cs.median_bound(np.array([0.0, math.nan]), 1)
    with pytest.raises(ValueError):
        cs.median_bound(np.array([]), 1)


def test_bound_entry_flags_by_ten_times_the_bound_and_refuses_an_infinite_half_width() -> None:
    """``bound_entry``: flag = 10 * bound > hw (strict, multiplied out); no second clause.

    Reference: hw = 0.625 from the interval [-0.625, 0.625]: bound 0.0625 gives False (10 * 0.0625 ==
    0.625), the next float gives True; an infinite half-width gives ``not_computed`` (a bound has no
    verdict to compare), never False. Exact.
    """
    assert cs.bound_entry([-0.625, 0.625], 0.0625, 2)["flag"] is False
    assert cs.bound_entry([-0.625, 0.625], math.nextafter(0.0625, 1.0), 2)["flag"] is True
    entry = cs.bound_entry([-math.inf, 1.0], 0.0625, 2)
    assert entry["status"] == "not_computed" and entry["flag"] is None
    assert entry["delta_bound"] is None and "verdict_2L" not in entry
    assert cs.bound_entry(None, 0.1, 0)["status"] == "not_computed"


# ------------------------------------------------------------------- T8, T9: recomputed verdicts
def _config(**changes):
    """The smoke configuration with a short bootstrap (the verdict rules are those of every preset)."""
    return dataclasses.replace(SMOKE, bootstrap_resamples=40, bootstrap_block=5, **changes)


def test_t8_h3c_flips_when_one_clipped_draw_doubles() -> None:
    """T8: H3c with 60 identical states, E = 2: the ratio 41 / 42.25 (pass) becomes 116 / 61 (fail).

    Reference: hand arithmetic. Draw 0: e_C = 0, e_P = +10 (clipped, sign +1); draw 1: e_C = 8,
    e_P = 0. A5 has w = 1/2: draw 0 h = 5 -> 25, draw 1 h = 4 -> 16, mean 20.5; A4 has w = 3/4: draw
    0 h = 2.5 -> 6.25, draw 1 h = 6 -> 36, mean 21.125; ratio 20.5 / 21.125 = 41 / 42.25 = 0.9704
    (<= 1.05, pass). At 20: A5 h = 10 -> 100, mean 58; A4 h = 5 -> 25, mean 30.5; ratio 58 / 30.5 =
    116 / 61 = 1.9016 (fail). The 60 states are identical, so every resample equals the estimate
    and the intervals are degenerate (hw = 0): the first clause reads delta != 0. Tolerance 2 ulp
    (one division of exact dyadic sums).
    """
    n = 60
    cp = np.tile([0.0, 8.0], (n, 1))
    plp = np.tile([LEVEL, 0.0], (n, 1))
    sign = np.tile(np.array([1, 0], dtype=np.int8), (n, 1))
    config = _config()
    w5, w4 = np.full((n, 2), 0.5), np.full((n, 2), 0.75)
    a5, a4 = cs.rule_state_mse(w5, cp, plp), cs.rule_state_mse(w4, cp, plp)
    original = an.h3c_ratio(a5, a4, config)
    assert abs(original["A5_over_A4_mse"] - 41 / 42.25) <= 2 * np.spacing(41 / 42.25)
    assert original["verdict"] == "pass" and original["ci"][0] == original["ci"][1]
    plp2 = cs.perturb_errors(plp, sign)
    entry = cs.h3c_part(original, cs.rule_state_mse(w5, cp, plp2), cs.rule_state_mse(w4, cp, plp2),
                        config, n)
    assert entry["status"] == "computed" and entry["flag"] is True
    assert entry["verdict_2L"] == "fail" and entry["ratio"] is None  # hw = 0
    assert abs(entry["delta"] - (116 / 61 - 41 / 42.25)) <= 4 * np.spacing(2.0)
    # the same arrays with no clipped entry: delta is 0.0 exactly, the verdict is the same, no flag
    null = cs.h3c_part(original, a5, a4, config, 0)
    assert null["delta"] == 0.0 and null["verdict_2L"] == "pass" and null["flag"] is False


def _h2c_fixture(n: int, cal_cp: np.ndarray, cal_plp: np.ndarray, config):
    """Scores for H2c with 60 states and a calibration split of the given H_ref errors, E = 2."""
    rng = np.random.default_rng(909)
    base = 1.0 + 0.1 * rng.standard_normal(n)
    mse = {"A4": base, "A2": base + 0.2, "A0": base + 0.3, "A1": base + 0.4, "A4o": base + 0.1}
    scores = {k: SimpleNamespace(state_mse_ref=v) for k, v in mse.items()}
    calibration = SimpleNamespace(evals=SimpleNamespace(
        horizons=np.array([config.reference_horizon]), cp_err=cal_cp[:, :, None],
        plp_err=cal_plp[:, :, None]))
    return mse, scores, calibration


def test_t9_h2c_best_single_changes_when_the_calibration_mses_are_closer_than_the_increment() -> None:
    """T9: the better single forecaster of the calibration split changes at 2L; the part says so.

    Reference: hand arithmetic. Calibration split, 60 states x 2 draws at H_ref: e_C = 1.7 everywhere,
    so A0 has MSE 1.7^2 = 2.89; e_P = 0.9 except one clipped draw (stored 10, sign +1), so A1 has MSE
    (119 * 0.81 + 100) / 120 = 1.6366 < 2.89 and the better single forecaster is A1. At 20 the clipped
    draw adds 3 * 100 / 120 = 2.5 to A1: 4.1366 > 2.89, so the better single forecaster becomes A0
    (the two MSEs are closer than the increment). Part 2 then has delta None, flag True and reason
    "best single changes at 2L"; the first part is computed as usual (its test errors are the same, so
    delta is 0.0); ``best_single_2L`` is "A0" and the criterion's flag is True. With no clipped
    calibration draw the best single does not change and the second part is an ordinary entry with
    delta 0.0. Exact (strings, booleans, 0.0).
    """
    n, config = 60, _config()
    cal_cp = np.full((n, 2), 1.7)
    cal_plp = np.full((n, 2), 0.9)
    cal_plp[0, 0] = LEVEL
    sign = np.zeros((n, 2), dtype=np.int8)
    sign[0, 0] = 1
    mse, scores, calibration = _h2c_fixture(n, cal_cp, cal_plp, config)
    original = an.h2c_state_dependence(scores, calibration, config)
    assert original["best_single"] == "A1"
    shifted = SimpleNamespace(evals=SimpleNamespace(
        horizons=calibration.evals.horizons, cp_err=calibration.evals.cp_err,
        plp_err=(cal_plp + LEVEL * sign)[:, :, None]))
    counts = {"A4_minus_A2": 5, "A4_minus_A1": 3}
    out = cs.h2c_parts(original, mse, shifted, config, counts)
    assert out["best_single_2L"] == "A0" and out["flag"] is True
    part = out["parts"]["A4_minus_A1"]
    assert part["delta"] is None and part["flag"] is True and part["status"] == "computed"
    assert part["reason"] == "best single changes at 2L" and part["verdict_2L"] is None
    assert part["n_clipped_inputs"] == 3
    assert out["parts"]["A4_minus_A2"]["status"] == "computed"
    assert out["parts"]["A4_minus_A2"]["delta"] == 0.0  # the test errors are unchanged here
    null = cs.h2c_parts(original, mse, calibration, config, counts)
    assert null["best_single_2L"] == "A1" and null["flag"] is False
    assert null["parts"]["A4_minus_A1"]["delta"] == 0.0
    assert null["parts"]["A4_minus_A1"]["verdict_2L"] == original["A4_minus_A1"]["verdict"]


# --------------------------------------------------------------------- the brute-force world
H, REF_STEP, M, E, N, LT = 16, 4, 20, 2, 60, 4
"""Horizons 1..16, H_ref = 4 steps (steps_per_lyapunov 4), oracle draws M, evaluation draws E, states."""
SPECIALS = np.array([np.inf, -np.inf, np.nan, 37.0, -25.0, 1e9, -1e9, 22.0, -41.0])
"""Raw PLP errors that the clip stores as +-10: non-finite or beyond 2L = 20 (never in (10, 20))."""
SWEEP_KEYS = [(0.02, 1000), (0.02, 100000), (0.01, 1000), (0.01, 100000), (0.02, 10000)]
"""The sweep cells other than the core cell ``(0.01, 10000)`` (library sweep) ..."""
NOISE_KEYS = {0.02: (0.02, 10000), 0.05: (0.05, 10000)}
"""... and the noise cells other than the core (0.01), which is the core cell's own test moments."""


def _world_config():
    return dataclasses.replace(SMOKE, steps_per_lyapunov=LT, n_oracle_draws=M, n_eval_draws=E,
                               bootstrap_resamples=60, bootstrap_block=5)


def _raw(rng, n_draws: int, inject: int, extra: int = 0, cp_inject: int = 0):
    """Raw CP and PLP errors ``(N, n_draws, H)``, below 10 in modulus, plus injections.

    A third of the states have a PLP error much smaller than the CP error (w* = 0), a tenth a PLP
    error 1.6 times the CP error (w* = 1), the rest an interior optimum. ``inject`` states get 1 or 2
    special PLP entries at H_ref, ``extra`` states one special entry at horizon 10 (clipped, away from
    H_ref), ``cp_inject`` states a CP error of 12 (the sentinel).
    """
    scale = 0.3 + 0.05 * np.arange(H)
    cp = 0.7 * scale * rng.standard_normal((N, n_draws, H))
    kind = rng.choice(3, size=N, p=[0.3, 0.1, 0.6])[:, None, None]
    slope = np.where(kind == 0, 0.3, np.where(kind == 1, 1.6, 0.5))
    own = np.where(kind == 0, 0.1, np.where(kind == 1, 0.05, 0.6))
    plp = slope * cp + own * scale * rng.standard_normal((N, n_draws, H))
    assert np.abs(cp).max() < LEVEL and np.abs(plp).max() < LEVEL
    states = rng.choice(N, size=inject + extra + cp_inject, replace=False)
    for k, i in enumerate(states[:inject]):
        for j in range(1 + k % 2):
            plp[i, (3 * k + j) % n_draws, REF_STEP - 1] = SPECIALS[(k + j) % len(SPECIALS)]
    for k, i in enumerate(states[inject:inject + extra]):
        plp[i, k % n_draws, 9] = SPECIALS[k % len(SPECIALS)]
    for i in states[inject + extra:]:
        cp[i, 0, 5] = 12.0
    return cp, plp


def _clip_arrays(masks, plp_err):
    """``handled`` (the two H_ref columns), the signs and the entry totals of a world at L (the
    fixture builder; the production derivation is tested in T1 and T11)."""
    n, ref = len(plp_err), REF_STEP - 1
    handled = np.zeros((n, len(DRAW_COUNTERS)), dtype=np.int64)
    handled[:, DRAW_COLUMN["error_clips_plp_href"]] = masks.plp[:, :, ref].sum(axis=1)
    handled[:, DRAW_COLUMN["error_clips_nonfinite_href"]] = masks.nonfinite[:, :, ref].sum(axis=1)
    clipped = masks.plp[:, :, ref] | masks.nonfinite[:, :, ref]
    sign = np.where(clipped, np.sign(plp_err[:, :, ref]), 0.0).astype(np.int8)
    counts = masks.counts()
    return handled, sign, {k: counts[k] for k in ENTRY_COUNTERS}


def _moments_from(cp_err, plp_err, masks, seeds):
    """Moments of errors ``(n, M, H)`` as ``ensemble_moments`` forms them (with the clip arrays if
    ``masks`` is given)."""
    corr, cp_const, plp_const = draw_correlation(cp_err, plp_err)
    handled = np.zeros((len(cp_err), len(DRAW_COUNTERS)), dtype=np.int64)
    chi = entries = None
    if masks is not None:
        handled, sign, entries = _clip_arrays(masks, plp_err)
        chi = (sign * cp_err[:, :, REF_STEP - 1]).mean(axis=1)
    return EnsembleMoments(
        horizons=np.arange(1, H + 1), mean_cp=cp_err.mean(axis=1), mean_plp=plp_err.mean(axis=1),
        sq_cp=(cp_err**2).mean(axis=1), sq_plp=(plp_err**2).mean(axis=1),
        cross=(cp_err * plp_err).mean(axis=1), analog_seed=seeds[0], est_seed=seeds[1],
        noise_sens=seeds[2], err_corr=corr, cp_constant=cp_const, plp_constant=plp_const,
        handled=handled, clip_entries=entries, clip_cross_ref=chi)


def _evals_from(feats, cp_err, plp_err, masks):
    """Evaluation draws ``(n, E, H)`` with the features ``deployable_profile`` reads."""
    distance, est_nu, growth, noise_sens, verify = feats
    handled = np.zeros((len(cp_err), len(DRAW_COUNTERS)), dtype=np.int64)
    sign = entries = None
    if masks is not None:
        handled, sign, entries = _clip_arrays(masks, plp_err)
    return EvaluationDraws(
        horizons=np.arange(1, H + 1), cp_err=cp_err, plp_err=plp_err, verify_noise=verify,
        distance=distance, est_nu=est_nu, growth_proxy=growth, gain_proxy=np.ones((len(cp_err), E, H)),
        inputs=np.zeros((len(cp_err), E, 2)), noise_sens=noise_sens, handled=handled,
        clip_entries=entries, clip_sign_ref=sign)


def _world(seed: int, inject: bool = True, cp_inject: int = 0, with_reference: bool = True):
    """A miniature core cell with the production fitting steps, and the 20 sigma_x reference world.

    Three splits of 60 states (oracle draws M = 20, evaluation draws E = 2, horizons 1..16, H_ref = 4
    steps), a regime tree fitted once on the construction states of the world at L, an A3 allocator
    (fixed random weights), the production ``global_weight``, ``calibrate_regimes``, ``rule_weights``
    and ``score_rules`` at L, the production analysis function of every criterion, six sweep cells
    for H2b and H2e, and (``with_reference``) the same assembly on errors clipped at 20 from the raw
    values with the tree, proxies, A3 weights, seeds and bootstrap seeds held fixed (the brute-force
    world).
    """
    rng = np.random.default_rng(seed)
    config = _world_config()
    n_inject = 6 if inject else 0
    splits = ("construction", "calibration", "test")
    raw = {s: _raw(rng, M, n_inject, 3 if inject else 0, cp_inject if s == "test" else 0)
           for s in splits}
    eval_raw = {s: _raw(rng, E, 5 if inject else 0) for s in splits}
    seeds = {s: (0.2 + rng.random(N), 0.1 + rng.random(N), rng.random(N)) for s in splits}
    feats = {s: (0.5 + rng.random((N, E)), 0.5 + rng.random((N, E)), rng.random((N, E)),
                 rng.random((N, E)), 0.05 * rng.standard_normal((N, E, H))) for s in splits}
    sweep_raw = {key: _raw(rng, M, 4 if inject else 0) for key in [*SWEEP_KEYS, NOISE_KEYS[0.05]]}
    gains = np.exp(0.3 * rng.standard_normal((N, H)))
    growth = 0.5 * rng.standard_normal(N)
    a3_fixed = rng.uniform(0.1, 0.9, (N, E, H))
    t_target = rng.standard_normal(N)
    truth = np.zeros((N, 1, H))
    proxies = ProfileProxies(SeedProxy(0.5, 0.5), SeedProxy(0.5, 0.5), nu_cap=5.0)
    predictor = SimpleNamespace(weights=lambda inputs, horizons: a3_fixed)
    horizons = np.arange(1, H + 1)
    col = REF_STEP - 1

    def at_level(level: float, masked: bool):
        moments, evals = {}, {}
        for s in splits:
            cp_err, plp_err, masks = clip_errors(*raw[s], truth, clip=level)
            moments[s] = _moments_from(cp_err, plp_err, masks if masked else None, seeds[s])
            e_cp, e_plp, e_masks = clip_errors(*eval_raw[s], truth, clip=level)
            evals[s] = _evals_from(feats[s], e_cp, e_plp, e_masks if masked else None)
        sweep = {}
        for key, (cp, plp) in sweep_raw.items():
            cp_err, plp_err, masks = clip_errors(cp, plp, truth, clip=level)
            sweep[key] = _moments_from(cp_err, plp_err, masks if masked else None, seeds["test"])
        sweep[(0.01, 10000)] = moments["test"]  # the core cell's own test moments
        return moments, evals, sweep

    moments_l, evals_l, sweep_l = at_level(LEVEL, True)
    profile = {s: deployable_profile(evals_l[s], proxies, 0.01, LT) for s in splits}
    tree = fit_regime_tree(profile["construction"], oracle_weight(moments_l["construction"])[:, col],
                           t_target, 3, config.seed)

    def build(moments, evals, sweep):
        a2 = global_weight(moments["construction"])
        rmap = calibrate_regimes(tree, profile["calibration"], moments["calibration"],
                                 evals["calibration"], config.primary_threshold, a2)
        rules = FittedRules(proxies=proxies, global_weights=a2, predictor=predictor,
                            regimes={3: rmap}, chosen_regimes=3)
        test = SplitData(moments["test"], evals["test"])
        weights = rule_weights(rules, test, 0.01, config, horizons)
        scores = score_rules(weights, test, horizons, config, config.primary_threshold)
        cell_of = lambda key: SimpleNamespace(splits={"test": SplitData(sweep[key], None)})
        core_sub = cell_of((0.01, 10000))  # one object in both sweeps, as in run_system
        noise_cells = {0.01: core_sub, 0.02: cell_of(NOISE_KEYS[0.02]),
                       0.05: cell_of(NOISE_KEYS[0.05])}
        library_cells = {(0.01, 10000): core_sub, **{key: cell_of(key) for key in SWEEP_KEYS}}
        cell = SimpleNamespace(
            system="mini", noise=0.01, library_size=10000, label="base",
            setup=SimpleNamespace(n_analogs=1), ctx=SimpleNamespace(spec=SimpleNamespace(dim=3)),
            splits={s: SplitData(moments[s], evals[s]) for s in splits},
            oracles={"test": SimpleNamespace(gains=gains, growth=growth)}, horizons=horizons)
        results = {
            "H1b": an.h1b_seed_amplifier(cell, config),
            "H2a": an.h2a_separation(cell, config),
            "H2b": an.h2b_knob_response(noise_cells, library_cells, config),
            "H2c": an.h2c_state_dependence(scores, cell.splits["calibration"], config),
            "H2d": an.h2d_empirical_comparison(scores, config),
            "H2e": an.h2e_noise_matching(library_cells, config),
            "H3c": an.h3c_ratio(scores["A5"].state_mse_ref, scores["A4"].state_mse_ref, config)}
        return SimpleNamespace(config=config, cell=cell, rules=rules, weights=weights,
                               scores=scores, noise_cells=noise_cells, library_cells=library_cells,
                               results=results)

    world = build(moments_l, evals_l, sweep_l)
    if with_reference:
        world.reference = build(*at_level(2 * LEVEL, False))
    return world


def _run(world):
    return cs.clip_sensitivity_block(world.cell, world.rules, world.weights, world.scores,
                                     world.noise_cells, world.library_cells, world.results,
                                     world.config)


def _expected_part(old_estimate, old_ci, old_verdict, new_estimate, new_verdict):
    """The entry a part must have, by the flag rule restated here (not by calling the code)."""
    delta = new_estimate - old_estimate
    half = (old_ci[1] - old_ci[0]) / 2.0
    return delta, (10.0 * abs(delta) > half) or new_verdict != old_verdict


def test_world_flags_equal_the_production_functions_on_errors_clipped_at_twenty() -> None:
    """The brute-force test (T-world): every tier-A part, the A2 and A5 shifts and the H2e bound.

    Reference (independent algorithm, QA/NVVUQ): the production functions ``global_weight``,
    ``calibrate_regimes``, ``rule_weights``, ``score_rules``, ``h1b_seed_amplifier``,
    ``h2a_separation``, ``h2b_knob_response``, ``h2c_state_dependence``, ``h2d_empirical_comparison``,
    ``h3c_ratio`` run on a world whose errors were clipped at 20 sigma_x from the same raw values
    (no raw error lies in (10, 20), so the doubling P2 and a clip at 20 coincide), with the tree,
    proxies, A3 weights, seeds and bootstrap indices held fixed. The flag is restated here as
    ``10 |delta| > hw`` or a changed verdict. Mini-world: 3 splits x 60 states, M = 20, E = 2, H_ref
    = 4, 6 states with 1 to 2 clipped H_ref draws per oracle split, 5 per evaluation split, 3 with a
    clip at a later horizon; five sweep cells with 4 clipped states each. Tolerance on delta:
    rtol 1e-9, atol 1e-12. The increment path and the direct path differ in summation orders (about
    M u = 2e-15 relative per moment, TIMES the condition number of the weight ratio (curvature of a
    state with a clipped draw is >= L^2 / M = 5, so <= 1e2), then a mean over states and a bootstrap
    quantile: well below 1e-11); 1e-9 leaves two orders of margin. Verdict strings and flags: exact.
    At least four parts must fire and at least one verdict must change (premises, asserted).
    """
    world = _world(1101)
    block = _run(world)
    ref, results = world.reference.results, world.results
    assert block["status"] == "computed" and block["reason"] is None
    hyp = block["by_hypothesis"]

    def check(entry, old_estimate, old_ci, old_verdict, new_estimate, new_verdict):
        delta, flag = _expected_part(old_estimate, old_ci, old_verdict, new_estimate, new_verdict)
        assert entry["status"] == "computed", entry
        assert entry["delta"] == pytest.approx(delta, rel=1e-9, abs=1e-12), entry
        assert entry["flag"] is flag, (entry, delta)
        assert entry["verdict_2L"] == new_verdict, entry
        return entry["flag"]

    fired = []
    h3c, h3c_ref = results["H3c"], ref["H3c"]
    fired.append(check(hyp["H3c"]["parts"]["A5_over_A4"], h3c["A5_over_A4_mse"], h3c["ci"],
                       h3c["verdict"], h3c_ref["A5_over_A4_mse"], h3c_ref["verdict"]))
    h2d, h2d_ref = results["H2d"], ref["H2d"]
    fired.append(check(hyp["H2d"]["parts"]["A4_over_A3"], h2d["in_distribution_excess"], h2d["ci"],
                       h2d["verdict"], h2d_ref["in_distribution_excess"], h2d_ref["verdict"]))
    h2c, h2c_ref = results["H2c"], ref["H2c"]
    assert h2c_ref["best_single"] == h2c["best_single"], "premise: the best single does not change"
    assert hyp["H2c"]["best_single_2L"] == h2c_ref["best_single"]
    for name in ("A4_minus_A2", f"A4_minus_{h2c['best_single']}"):
        fired.append(check(hyp["H2c"]["parts"][name], h2c[name]["mean"], h2c[name]["ci"],
                           h2c[name]["verdict"], h2c_ref[name]["mean"], h2c_ref[name]["verdict"]))
    h1b, h1b_ref = results["H1b"], ref["H1b"]
    fired.append(check(hyp["H1b"]["parts"]["PLP"], h1b["PLP"]["slope"], h1b["PLP"]["ci"],
                       h1b["verdict"], h1b_ref["PLP"]["slope"], h1b_ref["verdict"]))
    h2a, h2a_ref = results["H2a"], ref["H2a"]
    assert set(h2a_ref["part_ii"]) == set(h2a["part_ii"]), "premise: the parts of (ii) do not change"
    for name, part in h2a["part_ii"].items():
        fired.append(check(hyp["H2a"]["parts"][name], part["partial_corr"], part["ci"],
                           part["verdict"], h2a_ref["part_ii"][name]["partial_corr"],
                           h2a_ref["part_ii"][name]["verdict"]))
    h2b, h2b_ref = results["H2b"], ref["H2b"]
    fired.append(check(hyp["H2b"]["parts"]["noise"], h2b["noise"]["mean_state_spearman"],
                       h2b["noise"]["ci"], h2b["noise"]["verdict"],
                       h2b_ref["noise"]["mean_state_spearman"], h2b_ref["noise"]["verdict"]))
    fired.append(check(hyp["H2b"]["parts"]["library_change"], h2b["library_change"]["mean_change"],
                       h2b["library_change"]["ci"], h2b["library_change"]["verdict"],
                       h2b_ref["library_change"]["mean_change"],
                       h2b_ref["library_change"]["verdict"]))
    assert sum(fired) >= 4, f"premise: at least four parts fire, got {fired}"
    # the A2 and A5 shifts of the weight_shift leaf equal the reference world's weights at H_ref
    col = REF_STEP - 1
    ref_rules = world.reference.rules
    assert block["weight_shift"]["A2"] == pytest.approx(
        ref_rules.global_weights[col] - world.rules.global_weights[col], rel=1e-9, abs=1e-12)
    assert block["weight_shift"]["A5_max"] == pytest.approx(
        np.max(np.abs(ref_rules.regimes[3].weights[:, col]
                      - world.rules.regimes[3].weights[:, col])), rel=1e-9, abs=1e-12)
    assert block["weight_shift"]["A5_max"] > 0.0 and block["weight_shift"]["A2"] != 0.0
    # H2e: the bound holds for the actual change of the median in the reference world
    for rho, part in hyp["H2e"]["parts"].items():
        actual = abs(ref["H2e"]["by_noise"][rho]["median_change"]
                     - results["H2e"]["by_noise"][rho]["median_change"])
        assert part["status"] == "computed" and part["delta_bound"] >= actual - 1e-12, (rho, part)
        assert part["n_clipped_inputs"] > 0


def test_world_counts_shares_and_invariance_are_read_off_the_stored_arrays() -> None:
    """The count leaves: ``href_clipped_draws``, ``held_fixed_entries``, ``share_test``, tiers C and D.

    Reference: Python loops over the stored arrays (independent of the vectorized code): the clipped
    evaluation draws are the entries of ``clip_sign_ref`` that are nonzero and whose stored error is
    +-10 (both asserted to agree); the oracle counts are the sums of the two ``handled`` H_ref columns;
    ``held_fixed_entries`` is the entry totals of the construction and calibration oracles and of the
    calibration evaluation draws; the A1 share (w = 0) is the clipped part of the pooled E e_P^2 (an
    exact identity with ``3 s M`` of the plan) and the A0 share (w = 1) the clipped part of the pooled
    CP error (a descriptor of where the CP error lies, not a change of A0); L^2 / M = 5 > 0.25, so the
    tier-D statements are 'exact' for H1c and H2a(i), and the test evaluation draws hold clipped
    entries, so H3a is 'not guaranteed'. Counts exact; the share rtol 1e-12 (the same terms summed in
    two orders).
    """
    world = _world(1101, with_reference=False)
    block = _run(world)
    cell = world.cell
    ref = REF_STEP - 1
    for key, split in (("calibration_eval", "calibration"), ("test_eval", "test")):
        ev = cell.splits[split].evals
        loop = 0
        for i in range(N):
            for r in range(E):
                signed = ev.clip_sign_ref[i, r] != 0
                assert signed == (abs(ev.plp_err[i, r, ref]) == LEVEL)
                loop += int(signed)
        assert block["href_clipped_draws"][key] == loop > 0, key
    for key, split in (("construction_oracle", "construction"), ("calibration_oracle", "calibration"),
                       ("test_oracle", "test")):
        handled = cell.splits[split].moments.handled
        loop = sum(int(row[4]) + int(row[5]) for row in handled)
        assert block["href_clipped_draws"][key] == loop > 0, key
    entries = lambda o: o.clip_entries["error_clips_plp"] + o.clip_entries["error_clips_nonfinite"]
    assert block["held_fixed_entries"] == entries(cell.splits["construction"].moments) \
        + entries(cell.splits["calibration"].moments) + entries(cell.splits["calibration"].evals)
    assert block["test_eval_clipped_entries"] == entries(cell.splits["test"].evals) > 0
    q = lambda s: cell.splits[s].moments.handled[:, 4] + cell.splits[s].moments.handled[:, 5]
    assert block["affected_states"] == {
        "Q-N": int(sum((q(s) > 0).sum() for s in ("construction", "calibration", "test"))),
        "H3b": int((q("construction") > 0).sum())}
    ev = cell.splits["test"].evals
    squares = ev.plp_err[:, :, ref] ** 2  # A1 has weight 0: its error is the PLP error
    clipped = sum(squares[i, r] for i in range(N) for r in range(E) if ev.clip_sign_ref[i, r] != 0)
    assert block["share_test"]["A1"] == pytest.approx(clipped / squares.sum(), rel=1e-12)
    cp_squares = ev.cp_err[:, :, ref] ** 2  # A0 has weight 1: its error is the CP error
    cp_clipped = sum(cp_squares[i, r] for i in range(N) for r in range(E)
                     if ev.clip_sign_ref[i, r] != 0)
    assert block["share_test"]["A0"] == pytest.approx(cp_clipped / cp_squares.sum(), rel=1e-12)
    assert block["invariance"] == {"H1c": "exact", "H2a_i": "exact", "H3a": "not guaranteed"}


def test_world_without_a_clipped_entry_is_bitwise_unchanged() -> None:
    """T6: no clipped entry anywhere: every delta is 0.0 exactly, every verdict_2L equals the
    verdict, every flag is False, ``best_single_2L`` equals ``best_single``, H3a is 'exact'.

    Reference: the definition (the same operations on the same arrays): the increments are + 0.0, the
    perturbed errors are the stored ones, and the verdict code rebuilds each bootstrap from the same
    seed and labels. Bitwise (``==`` on floats, strings and booleans); nothing is skipped: the
    mini-world has all seven criteria and the two sweep verdicts.
    """
    world = _world(1102, inject=False, with_reference=False)
    block = _run(world)
    assert block["status"] == "computed"
    assert block["href_clipped_draws"] == dict.fromkeys(block["href_clipped_draws"], 0)
    assert block["held_fixed_entries"] == 0 and block["test_eval_clipped_entries"] == 0
    assert block["weight_shift"] == {"A2": 0.0, "A5_max": 0.0}
    assert block["invariance"]["H3a"] == "exact"
    assert block["affected_states"] == {"Q-N": 0, "H3b": 0}
    n_parts = 0
    for hypothesis, entry in block["by_hypothesis"].items():
        for name, part in entry["parts"].items():
            assert part["status"] == "computed", (hypothesis, name, part)
            n_parts += 1
            assert part["n_clipped_inputs"] == 0 and part["flag"] is False, (hypothesis, name)
            if hypothesis == "H2e":
                assert part["delta_bound"] == 0.0
            else:
                assert part["delta"] == 0.0, (hypothesis, name, part)
        assert entry["flag"] is False
    assert n_parts == 1 + 1 + 1 + 2 + len(world.results["H2a"]["part_ii"]) + 2 + 2
    results = world.results
    assert block["by_hypothesis"]["H2c"]["best_single_2L"] == results["H2c"]["best_single"]
    for hypothesis, key in (("H3c", "A5_over_A4"), ("H2d", "A4_over_A3")):
        assert block["by_hypothesis"][hypothesis]["parts"][key]["verdict_2L"] == \
            results[hypothesis]["verdict"]
    assert block["by_hypothesis"]["H1b"]["parts"]["PLP"]["verdict_2L"] == results["H1b"]["verdict"]
    assert all(p["verdict_2L"] == results["H2a"]["part_ii"][n]["verdict"]
               for n, p in block["by_hypothesis"]["H2a"]["parts"].items())
    assert cs.log_flags("mini", block) == 0  # nothing fired, nothing held fixed: no WARNING


def test_world_with_a_clipped_cp_error_is_not_computed_and_says_why(caplog) -> None:
    """H-CP: a nonzero ``error_clips_cp`` makes every part ``not_computed`` with the reason (never False).

    Reference: the plan (section 1: 'If H-CP fails, the clip sensitivity is not computed:
    status = "not_computed", with reason = "CP clip sentinel nonzero"'). The world has one CP error of
    12 in a test-split oracle state. Exact strings; every part's flag is None, the block's
    ``affected_states`` are None, and one WARNING line says so.
    """
    world = _world(1103, cp_inject=1, with_reference=False)
    assert world.cell.splits["test"].moments.clip_entries["error_clips_cp"] == 1
    block = _run(world)
    assert block["status"] == "not_computed" and block["reason"].startswith("CP clip sentinel nonzero")
    for hypothesis, entry in block["by_hypothesis"].items():
        assert entry["flag"] is None
        for part in entry["parts"].values():
            assert part["status"] == "not_computed" and part["flag"] is None
            assert part["reason"] == block["reason"]
    assert block["affected_states"] == {"Q-N": None, "H3b": None}
    with caplog.at_level(logging.WARNING, logger="lpcstudy"):
        assert cs.log_flags("mini", block) == 1
    assert "NOT COMPUTED" in caplog.text and "CP clip sentinel" in caplog.text


def test_missing_arrays_and_a_baseline_that_is_not_reproduced_are_reported() -> None:
    """Moments without the clip arrays, or stored MSEs that the recomputation does not reproduce,
    give a ``not_computed`` block with the reason, never a number.

    Reference: construction. (a) ``clip_cross_ref = None`` on the test moments; (b) a stored A4
    per-state MSE changed by one ulp in one state. Exact strings.
    """
    world = _world(1104, with_reference=False)
    world.cell.splits["test"].moments.clip_cross_ref = None
    assert _run(world)["reason"].startswith("clip arrays absent in core test")
    world = _world(1104, with_reference=False)
    world.scores["A4"].state_mse_ref[3] = math.nextafter(world.scores["A4"].state_mse_ref[3], 9.0)
    block = _run(world)
    assert block["status"] == "not_computed" and "not reproduced" in block["reason"]
    assert all(p["status"] == "not_computed" for e in block["by_hypothesis"].values()
               for p in e["parts"].values())


def test_world_log_flags_writes_one_warning_per_fired_flag(caplog) -> None:
    """One WARNING line per fired part, plus one for the held-fixed entries and one for H3a.

    Reference: the plan (section 4: 'One logging WARNING line is written per fired flag'; section 5:
    H3a 'not guaranteed'; section 4: held_fixed_entries note). The count of lines is read off the
    block by a loop over its parts (independent of ``log_flags``). Exact.
    """
    world = _world(1101, with_reference=False)
    block = _run(world)
    fired = sum(1 for e in block["by_hypothesis"].values() for p in e["parts"].values()
                if p["status"] == "computed" and p["flag"])
    extra = sum(1 for e in block["by_hypothesis"].values()
                if e["flag"] and not any(p["flag"] for p in e["parts"].values()))
    expected = fired + extra + 1 + (block["held_fixed_entries"] > 0)  # + H3a not guaranteed
    with caplog.at_level(logging.WARNING, logger="lpcstudy"):
        assert cs.log_flags("mini", block) == expected
    assert caplog.text.count("CLIP-SENSITIVE") >= fired > 0
    assert "H3a: invariance NOT GUARANTEED" in caplog.text
    assert "not recomputed" in caplog.text


def test_invariance_outside_the_hypothesis_when_l_squared_over_m_is_small() -> None:
    """H-M1/H-M2: the invariance of H1c and H2a(i) is asserted at run time through L^2 / M.

    Reference: the plan (section 5): ``L**2 / M > max(max(thresholds)**2, linear_regime_rms**2)``, with
    thresholds (0.1, 0.2, 0.3, 0.5) and r_lin = 0.5, so the bound is 0.25: M = 399 gives 100 / 399 =
    0.2506 (holds) and M = 400 gives exactly 0.25 (does not hold, the inequality is strict: 100 / 400
    is exact). Exact.
    """
    assert cs.invariance(dataclasses.replace(SMOKE, n_oracle_draws=399), 0) == {
        "H1c": "exact", "H2a_i": "exact", "H3a": "exact"}
    out = cs.invariance(dataclasses.replace(SMOKE, n_oracle_draws=400), 3)
    assert out == {"H1c": "outside the invariance hypothesis",
                   "H2a_i": "outside the invariance hypothesis", "H3a": "not guaranteed"}
