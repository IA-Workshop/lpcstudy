"""Tests of experiment C of phase J (WU-0049, ``lpcstudy/joint_decisions.py``).

The acceptance list of the plan as amended by the mathematics specification:

* the horizon of a policy: ``T - 1 <= T_c <= T`` and ``ceil(T_c)`` equals
  ``oracle.characteristic_horizon`` exactly on hand-built curves, with
  ``T_c = T - 1`` only where ``e_{T-1} = theta`` exactly (counted); ``T_c``
  equals the analytic crossing of a log-linear curve;
* the bottleneck skill identities: retained skill 1 for a bottleneck equal to
  the full model, 0 for one equal to the constant, an exact manufactured
  value in between, and the reading rules;
* the A2 rebuild, the ``ln H`` interpolation, the Kaplan-Meier leaf quantile,
  the false-trust rate, the cross-fitting folds and the per-row targets of
  the learner, each against an independent reference.

The realized-horizon reproduction of the run's stored aggregates needs a
dump: ``tests/integration/test_contribution_dump.py``. Random inputs come
from fixed ``np.random.default_rng(<int>)``.
"""

from __future__ import annotations

import math

import numpy as np
import pytest
from unit_helpers import _moments_from_draws

from lpcstudy import contribution as cb
from lpcstudy import joint_decisions as jd
from lpcstudy.allocation import global_weight
from lpcstudy.oracle import characteristic_horizon


# ------------------------------------------------------- policy horizons
def test_policy_crossing_equals_the_analytic_log_linear_crossing() -> None:
    """``T_c`` of a per-draw weight on ``E = a^2 e^{2 lam H}`` curves.

    With ``C = 0`` and ``rho = 0`` the policy's r.m.s. error is exactly
    ``A e^{lam H}``, ``A = sqrt(w^2 a_C^2 + (1 - w)^2 a_P^2)``, so the
    crossing is ``ln(theta / A) / lam``. Reference: that formula, and
    ``oracle.characteristic_horizon`` of the same curve for ``T`` (an
    independent first-passage code). Tolerance: 1e-9 steps (a few logs and
    one division of numbers of order 1; round-off is near 1e-13).
    """
    theta, h_max = 0.2, 240
    horizons = np.arange(1, h_max + 1)
    a_c = np.array([0.01, 0.02, 0.05, 0.3])
    a_p = np.array([0.03, 0.01, 0.04, 0.25])
    lam = np.array([0.02, 0.01, 0.004, 0.05])
    growth = np.exp(2 * lam[:, None] * horizons[None, :])
    e_c, e_p = a_c[:, None] ** 2 * growth, a_p[:, None] ** 2 * growth
    weight = np.array([[0.0, 0.3, 1.0], [0.5, 0.9, 0.1], [0.2, 0.2, 0.7]])
    weight = np.vstack([weight, [[1.0, 0.0, 0.5]]])
    w_full = np.repeat(weight[:, :, None], h_max, axis=2)
    cross = jd.policy_crossing(e_c, e_p, np.zeros_like(e_c), w_full, 0.0, theta)
    assert cross.T.shape == (4, 3)
    amp = np.sqrt(
        weight**2 * a_c[:, None] ** 2 + (1 - weight) ** 2 * a_p[:, None] ** 2
    )
    exact = np.log(theta / amp) / lam[:, None]
    for i in range(4):
        for j in range(3):
            mse = weight[i, j] ** 2 * e_c[i] + (1 - weight[i, j]) ** 2 * e_p[i]
            first, event = characteristic_horizon(
                mse[None], horizons, 0.0, theta
            )
            assert cross.T[i, j] == first[0] and cross.event[i, j] == event[0]
            if not event[0]:
                assert np.isinf(cross.T_c[i, j])
            elif first[0] == 1:
                assert cross.T_c[i, j] == 1.0
            else:
                assert abs(cross.T_c[i, j] - exact[i, j]) <= 1e-9
    assert (~cross.event).sum() >= 1  # a censored entry is exercised
    assert np.sum(cross.T == 1) >= 1 and cross.n_first_step == np.sum(
        cross.T == 1
    )


def test_crossing_bounds_ceiling_and_exact_theta_on_hand_built_curves() -> None:
    """``T - 1 <= T_c <= T``; ``ceil(T_c) = T`` except at ``e_{T-1} = theta``.

    Hand-built r.m.s. curves ``(n, r, H)``: random increasing curves, one with
    ``e_{T-1} = theta`` exactly (``T_c = T - 1``, counted, the only entry where
    the ceiling differs), one crossing at the first step and one censored.
    Reference: ``oracle.characteristic_horizon`` on ``mse = e^2`` with
    ``rho = 0``. Tolerance: exact (integers, and bounds on one interpolation).
    """
    rng = np.random.default_rng(4901)
    theta, h_max = 0.2, 60
    horizons = np.arange(1, h_max + 1)
    start = rng.uniform(0.005, 0.1, (6, 2, 1))
    rate = rng.uniform(0.01, 0.15, (6, 2, 1))
    rms = (
        start
        * np.exp(rate * np.arange(h_max))
        * rng.uniform(1.0, 1.01, (6, 2, h_max))
    )
    rms = np.maximum.accumulate(rms, axis=2)
    rms[0, 0] = np.linspace(0.1, 0.3, h_max)
    rms[0, 0, 9], rms[0, 0, 10] = theta, 0.25  # e_{T-1} = theta, T = 11
    rms[0, 0, :9] = np.minimum(rms[0, 0, :9], 0.19)
    rms[1, 1] = np.full(h_max, 0.5)  # T = 1
    rms[2, 0] = np.full(h_max, 0.1)  # censored
    cross = cb.rms_crossing(rms, theta)
    first, event = characteristic_horizon(
        rms.reshape(-1, h_max) ** 2, horizons, 0.0, theta
    )
    np.testing.assert_array_equal(cross.T.ravel(), first)
    np.testing.assert_array_equal(cross.event.ravel(), event)
    t_c, t = cross.T_c.ravel(), first
    finite = np.isfinite(t_c)
    assert np.all(t[finite] - 1 <= t_c[finite]) and np.all(
        t_c[finite] <= t[finite]
    )
    ceiling = np.ceil(t_c[finite]) == t[finite]
    assert cross.n_exact_theta == 1 and cross.exact[0, 0]
    assert cross.T[0, 0] == 11 and cross.T_c[0, 0] == 10.0
    np.testing.assert_array_equal(~ceiling, cross.exact.ravel()[finite])
    assert cross.n_first_step == 1 and cross.T_c[1, 1] == 1.0
    assert np.isinf(cross.T_c[2, 0]) and cross.y[2, 0] == np.log(h_max)


def test_crossing_time_is_unchanged_for_the_oracle_hybrid() -> None:
    """``crossing_time`` (WU-0048) now goes through ``rms_crossing``.

    Reference: the same curve through ``policy_crossing`` with the oracle
    weight ``w*`` on every column (the moment form at ``w*`` is ``V(w*)``).
    Tolerance: exact for ``T`` and the event; 1e-12 relative for ``T_c``
    (``quad_mse`` at ``w*`` and ``V(w*)`` are the same expression).
    """
    rng = np.random.default_rng(4902)
    n, h_max = 30, 120
    base = rng.uniform(0.001, 0.02, (n, 1)) * np.exp(
        rng.uniform(0.01, 0.05, (n, 1)) * np.arange(h_max)
    )
    e_c, e_p = base * rng.uniform(0.5, 2.0, (n, 1)), base * rng.uniform(
        0.5, 2.0, (n, 1)
    )
    cross = 0.3 * np.sqrt(e_c * e_p)
    a = cb.crossing_time(e_c, e_p, cross, 0.01, 0.2)
    w_star = cb.allocation_targets(e_c, e_p, cross).w_star
    b = jd.policy_crossing(e_c, e_p, cross, w_star[:, None, :], 0.01, 0.2)
    np.testing.assert_array_equal(a.T, b.T[:, 0])
    np.testing.assert_array_equal(a.event, b.event[:, 0])
    fin = np.isfinite(a.T_c)
    np.testing.assert_allclose(a.T_c[fin], b.T_c[fin, 0], rtol=1e-12)


# ------------------------------------------------------------- weights
def test_pooled_weight_equals_the_production_global_weight() -> None:
    """A2 on ``1..H_max`` against ``allocation.global_weight`` (the run's A2).

    Reference: the production function on an ``EnsembleMoments`` built by
    plain sample averages (``unit_helpers``). Tolerance: 1e-14 relative (two
    sums of 50 terms in a different association order).
    """
    rng = np.random.default_rng(4903)
    cp = rng.standard_normal((50, 40, 7)) * rng.uniform(0.1, 1, (50, 1, 7))
    plp = 0.4 * cp + rng.standard_normal((50, 40, 7)) * 0.3
    m = _moments_from_draws(cp, plp)
    np.testing.assert_allclose(
        jd.pooled_weight(m.sq_cp, m.sq_plp, m.cross),
        global_weight(m),
        rtol=1e-14,
    )


def test_full_grid_weight_is_linear_in_log_h_and_exact_at_the_knots() -> None:
    """Interpolation in ``ln H``, constant beyond the end knots.

    Reference: ``np.interp`` on ``ln H`` row by row (an independent code).
    Tolerance: exact at the knots (copied values); 1e-15 absolute elsewhere
    (one convex combination of numbers in [0, 1]).
    """
    rng = np.random.default_rng(4904)
    knots = np.array([8, 15, 30, 60, 120])
    w = rng.uniform(0, 1, (3, 2, 5))
    out = jd.full_grid_weight(w, knots, 240)
    assert out.shape == (3, 2, 240)
    grid = np.log(np.arange(1, 241))
    for i in range(3):
        for j in range(2):
            ref = np.interp(grid, np.log(knots), w[i, j])
            np.testing.assert_allclose(out[i, j], ref, rtol=0, atol=1e-15)
            np.testing.assert_array_equal(out[i, j, knots - 1], w[i, j])
            assert np.all(out[i, j, :8] == w[i, j, 0])
            assert np.all(out[i, j, 119:] == w[i, j, -1])


# ----------------------------------------------------- KM and false trust
def _brute_quantile(
    t: np.ndarray, event: np.ndarray, h_max: int, level: float
) -> float:
    """Smallest H with #{event, T <= H} >= level n (censoring at H_max only)."""
    n = len(t)
    for h in range(1, h_max + 1):
        if np.sum(event & (t <= h)) >= level * n:
            return float(h)
    return float(h_max)


def test_km_leaf_quantile_matches_a_direct_count() -> None:
    """Per-leaf Kaplan-Meier 10% quantile, pooled fallback counted.

    With censoring only at ``H_max``, ``S(H) = 1 - #{event, T <= H} / n``, so
    the quantile is the smallest ``H`` whose event count reaches ``0.1 n``.
    Reference: that direct count. Sizes avoid ``0.1 n`` integer boundaries
    (n = 997 pooled, leaves of 331 to 333), so the product-limit round-off
    cannot move the answer. Tolerance: exact (integers).
    """
    rng = np.random.default_rng(4905)
    h_max = 100
    t = rng.integers(1, h_max + 1, (997, 1))
    event = rng.uniform(size=(997, 1)) < 0.9
    t[~event] = h_max
    leaf = np.repeat([[3], [7], [9]], [333, 332, 332], axis=0)
    leaf_test = np.array([[3, 7], [9, 11]])  # leaf 11 has no calibration pair
    q, rec = jd.leaf_quantiles(leaf, t, event, leaf_test, h_max)
    for value in (3, 7, 9):
        rows = leaf[:, 0] == value
        ref = _brute_quantile(t[rows, 0], event[rows, 0], h_max, 0.1)
        assert rec["quantile_by_leaf"][str(value)] == ref
    pooled = _brute_quantile(t[:, 0], event[:, 0], h_max, 0.1)
    assert rec["pooled_quantile"] == pooled and q[1, 1] == pooled
    assert q[0, 0] == rec["quantile_by_leaf"]["3"]
    assert rec["n_test_entries_pooled_fallback"] == 1
    assert (
        jd.km_quantile(np.full(10, h_max), np.zeros(10, bool), h_max, 0.1)
        == h_max
    )


def test_false_trust_never_counts_a_censored_path() -> None:
    """Hand-built: ``T <= q`` counts only events; ties at ``q`` count.

    Reference: the cases enumerated by hand. Tolerance: exact.
    """
    y = np.log(np.array([[10.0, 50.0, 240.0, 240.0]]))
    event = np.array([[True, True, True, False]])
    q = y.copy()  # ties at 10 and at the cap (an event at H_max) count
    q[0, 1] = np.log(20.0)  # 50 > 20: no false trust
    assert jd.false_trust(y, event, q).tolist() == [0.5]  # censored: never


# ------------------------------------------------- bottleneck identities
def test_retained_skill_identities_and_readings() -> None:
    """Retained skill is 1 for the full model, 0 for the constant, exact between.

    Manufactured losses: ``L(const) = 4``, ``L(F) = 2``, ``L(B) = 3.5`` per
    state give ``(4 - 3.5) / (4 - 2) = 0.25`` exactly in binary. The
    resampled values of an identity are the identity, so the interval is
    degenerate. Reference: the hand values. Tolerance: exact.
    """
    rng = np.random.default_rng(4906)
    n = 200
    index = cb.resample_indices(n, 50, 5, rng)
    noise = rng.uniform(0, 0.5, n)
    const, full = 4.0 + noise, 2.0 + noise
    same = jd.retained_rows(const, full, full, index)
    assert same["retained"]["ratio"] == 1.0 and same["retained"]["ci"] == [
        1.0,
        1.0,
    ]
    assert same["retained"]["reading"] == "keeps most"
    none = jd.retained_rows(const, const, full, index)
    assert none["retained"]["ratio"] == 0.0 and none["retained"]["ci"] == [
        0.0,
        0.0,
    ]
    assert none["retained"]["reading"] == "loses most"
    part = jd.retained_rows(
        np.full(n, 4.0), np.full(n, 3.5), np.full(n, 2.0), index
    )
    assert part["retained"]["ratio"] == 0.25
    no_skill = jd.retained_rows(const, full, const, index)
    assert no_skill["retained"]["reading"].startswith(
        "not determined (full-profile"
    )
    guarded = jd.retained_rows(const, full, full, index, n_eff=(49.0, 300.0))
    assert guarded["retained"]["reading"] == "not determined (n_eff < 50)"
    spans = jd.retained_reading({"ci": [0.4, 0.6]}, {"ci": [0.1, 0.2]})
    assert spans == "not determined (interval spans 0.5)"


def test_c2_prediction_rule() -> None:
    """The math-spec prediction is read from the bottleneck readings."""

    def record(text: str, ratio: float = 0.1) -> dict:
        return {"retained": {"reading": text, "ratio": ratio}}

    fwd = {
        **record("loses most"),
        "single_horizon": {"8": record("x", 0.1), "120": record("x", 0.4)},
    }
    rev = {
        "8": record("loses most"),
        "30": record("not determined (n_eff < 50)"),
    }
    out = jd.c2_prediction(fwd, rev)
    assert (
        out["reading"] == "consistent"
        and out["forward_single_largest_at"] == "120"
    )
    rev["30"] = record("keeps most")
    assert jd.c2_prediction(fwd, rev)["reading"] == "not consistent"
    fwd2 = {
        **record("not determined (interval spans 0.5)"),
        "single_horizon": {},
    }
    assert (
        jd.c2_prediction(fwd2, {"8": record("loses most")})["reading"]
        == "not determined"
    )


def test_shapley_rank_is_the_spearman_of_the_shares() -> None:
    """Identical orders give 1, reversed orders -1 (four items, descriptive)."""
    rows = lambda v: {
        "rows": {x: {"phi": p} for x, p in zip("ROIN", v)}
    }  # noqa: E731
    abd = {
        "horizon": {"oracle": {"shapley_pinball": rows([1.0, 2.0, 3.0, 4.0])}},
        "allocation": {
            "8": {
                "oracle": {
                    "horizon": "H=8",
                    "shapley_L_A": rows([0.1, 0.2, 0.3, 0.4]),
                }
            },
            "30": {
                "oracle": {
                    "horizon": "H=30",
                    "shapley_L_A": rows([4.0, 3.0, 2.0, 1.0]),
                }
            },
        },
    }
    out = jd.shapley_rank_rows(abd)
    assert out["8"]["spearman"] == pytest.approx(1.0, abs=1e-15)
    assert out["30"]["spearman"] == pytest.approx(-1.0, abs=1e-15)


# ------------------------------------------------------------ fit helpers
def _job(n: int, r: int, y: np.ndarray, weight=None) -> cb.FitJob:
    rng = np.random.default_rng(4907)
    x = rng.standard_normal((n, r, 2))
    return cb.FitJob(
        "quantile" if y.ndim == 2 else "regression",
        x,
        y,
        weight,
        np.ones(n, bool),
        np.arange(n)[::-1].copy(),
        x[:5],
        "pinball" if y.ndim == 2 else "squared",
        {"y": y},
        tau=0.5 if y.ndim == 2 else None,
    )


def test_cross_fit_folds_partition_the_training_states() -> None:
    """Five contiguous time blocks, each predicted by a model not trained on it.

    The weight is renormalized to mean 1 on the kept states (M-2). Reference:
    set arithmetic. Tolerance: exact, and 1e-15 for the mean.
    """
    n = 53
    y = np.arange(n, dtype=float)
    weight = np.linspace(0.5, 2.0, n)
    parts = jd.cross_fit_jobs(_job(n, 1, y, weight), 5)
    held = np.concatenate([fold for fold, _ in parts])
    assert sorted(held.tolist()) == list(range(n))
    for fold, sub in parts:
        assert len(sub.y_train) == n - len(fold)
        assert not set(sub.y_train.tolist()) & set(y[fold].tolist())
        assert abs(sub.weight.mean() - 1.0) <= 1e-15
        np.testing.assert_array_equal(
            sub.x_test, _job(n, 1, y, weight).x_train[fold]
        )
    order = np.arange(n)[::-1]
    for fold, _ in parts:  # contiguous in time order
        times = np.sort(order[fold])
        assert np.all(np.diff(times) == 1)
    oof = jd.assemble(
        [f for f, _ in parts],
        [np.full((len(f), 1), k) for k, (f, _) in enumerate(parts)],
        n,
    )
    assert not np.isnan(oof).any()


def test_per_row_targets_are_paired_with_their_rows() -> None:
    """A target per (state, draw) trains on the matching rows.

    Reference: ``HistGradientBoostingRegressor`` fitted directly on the
    flattened rows with the per-row targets and weight ``1/r`` (the
    learner's own row weight), the same setting and seed. Tolerance: exact
    (the same fit on the same data); the loss is checked against a hand
    pinball sum.
    """
    rng = np.random.default_rng(4908)
    n, r = 60, 3
    y = rng.standard_normal((n, r))
    job = _job(n, r, y)
    setting = cb.GRID[0]
    learner = cb.Learner(seed=11, grid=(setting,))
    result = cb.run_job((job, learner))
    model = cb.make_estimator("quantile", setting, 11, r, 0.5)
    model.fit(
        job.x_train.reshape(-1, 2),
        y.reshape(-1),
        sample_weight=np.full(n * r, 1 / r),
    )
    ref = model.predict(job.x_test.reshape(-1, 2)).reshape(5, r)
    np.testing.assert_array_equal(result.pred, ref)
    loss = cb.state_loss("pinball", result.pred, {"y": y[:5]}, 0.5)
    diff = y[:5] - result.pred
    hand = np.mean(np.maximum(0.5 * diff, -0.5 * diff), axis=1)
    np.testing.assert_array_equal(loss, hand)


def test_coverage_accepts_a_target_per_entry() -> None:
    """``coverage`` with ``(n, r)`` targets equals the per-entry count.

    Reference: a loop over the entries with the M-4 cap rule. Tolerance:
    exact (counts).
    """
    rng = np.random.default_rng(4909)
    cap = math.log(100)
    y = np.log(rng.integers(1, 101, (40, 3)).astype(float))
    event = rng.uniform(size=(40, 3)) < 0.8
    y[~event] = cap
    q = np.minimum(rng.uniform(0, 5.0, (40, 3)), cap)
    q[0, 0] = cap
    rec = cb.coverage(y, event, q, cap)
    below = q < cap
    hits = [
        y[i, j] <= q[i, j] for i in range(40) for j in range(3) if below[i, j]
    ]
    assert rec["n_below_cap"] == len(hits)
    assert rec["coverage_below_cap"] == np.mean(hits)


# ------------------------------------------- WU-0049b: deployable and L_w
def _c2_record(forward: str, reverse: str) -> dict:
    return {
        "forward": {"retained": {"reading": forward}},
        "reverse": {"8": {"retained": {"reading": reverse}}},
    }


def test_retention_comparison_is_the_paired_difference() -> None:
    """Deployable minus oracle retained skill, exact on manufactured losses.

    Oracle ``(4, 3, 2)`` per state retains ``1/2``, deployable ``(4, 3.5,
    2)`` retains ``1/4``: the difference is ``-1/4`` exactly on every
    resample, so the interval is degenerate and reads "retains less";
    identical triples give 0 and "no difference detected"; a row whose
    reading is blocked on either profile reads not determined with that
    reason. Reference: the hand values. Tolerance: exact (binary fractions).
    """
    n = 120
    index = cb.resample_indices(n, 40, 5, np.random.default_rng(4931))
    const, full = np.full(n, 4.0), np.full(n, 2.0)
    oracle = {
        "forward": ((const, np.full(n, 3.0), full), ()),
        "reverse/8": ((const, np.full(n, 3.0), full), ()),
    }
    deploy = {
        "forward": ((const, np.full(n, 3.5), full), ()),
        "reverse/8": ((const, np.full(n, 3.0), full), ()),
    }
    rec = _c2_record("keeps most", "loses most")
    out = jd.retention_comparison(oracle, deploy, rec, rec, index)
    fwd = out["forward"]
    assert (fwd["oracle"], fwd["deployable"], fwd["difference"]) == (
        0.5,
        0.25,
        -0.25,
    )
    assert fwd["ci"] == [-0.25, -0.25]
    assert fwd["reading"] == "deployable retains less"
    assert out["reverse/8"]["difference"] == 0.0
    assert out["reverse/8"]["reading"] == "no difference detected"
    blocked = _c2_record("keeps most", "not determined (n_eff < 50)")
    out = jd.retention_comparison(oracle, deploy, rec, blocked, index)
    assert out["reverse/8"]["reading"] == "not determined (n_eff < 50)"
    assert out["forward"]["reading"] == "deployable retains less"


def test_unit_allocation_job_is_the_l_w_fit() -> None:
    """``unit=True`` gives M-2 rule 2's fit: u, no sample weight, ``L_w`` loss.

    Reference: the definition of the WU-0048 ``W/<set>`` job. Exact.
    """
    from types import SimpleNamespace

    rng = np.random.default_rng(4932)
    e_c, e_p, cross = _moments_like(rng, 30)
    target = cb.allocation_targets(e_c, e_p, cross)
    data = SimpleNamespace(train={"state_index": np.arange(30)})
    x = rng.standard_normal((30, 1, 4))
    job_w = jd._alloc_job(data, target, x, x[:5], unit=True)
    job_a = jd._alloc_job(data, target, x, x[:5])
    assert job_w.weight is None and job_w.loss == "unit_excess"
    assert job_a.loss == "kappa_excess"
    np.testing.assert_array_equal(
        job_a.weight, target.kappa / target.kappa.mean()
    )
    np.testing.assert_array_equal(job_w.y_train, target.u)


def _moments_like(rng: np.random.Generator, n: int) -> tuple[np.ndarray, ...]:
    """Moments of correlated draws (a valid Gram matrix per state)."""
    e_c = rng.standard_normal((n, 50)) * rng.uniform(0.1, 1, (n, 1))
    e_p = 0.3 * e_c + rng.standard_normal((n, 50)) * 0.5
    return (e_c**2).mean(1), (e_p**2).mean(1), (e_c * e_p).mean(1)
