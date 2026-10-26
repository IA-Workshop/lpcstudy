"""Tests of the phase J contribution library (WU-0048, ``lpcstudy/contribution.py``).

The acceptance list of the plan as amended by the mathematics specification
(M-1 to M-8) and the main session's design decisions of 2026-10-26:

* (a) the kappa-form excess equals ``V(w) - V(w*)`` within 1e-12 relative,
  against exact rational arithmetic;
* (a') the weighted learner's initial prediction is ``sum kappa u / sum
  kappa`` within 1e-12 relative (also with one row per draw);
* (b) the Shapley shares sum to ``L(empty) - L(F)`` within 1e-12 and equal the
  average over all 24 orderings (an independent algorithm);
* (c) is a slow test (``tests/slow/test_contribution_interactions.py``): it
  fits the B models with the production learner (inner CV over ``GRID``);
* (d) coverage of the true conditional quantiles of a synthetic ``T`` with
  fixed censoring is within ``4 sqrt(tau (1 - tau) / n)`` of ``tau``, and a
  planted set above the cap exercises the cap rule and the bracket;
* (e) Harrell's C equals a brute-force double loop under the M-4 tie rules;
* the crossing time ``T_c`` is exact on a log-linear error curve;
* the inner cross-validation reads training states only, and its folds are
  contiguous in time.

(f1) and (g) need a dump and are in ``tests/integration/test_contribution_dump.py``.
Every random input comes from a fixed ``np.random.default_rng(<int>)``.
"""

from __future__ import annotations

import itertools
import math
from fractions import Fraction

import numpy as np
import pytest

from lpcstudy import contribution as cb
from lpcstudy.ablation import CONDITIONS, SUBSETS
from lpcstudy.oracle import characteristic_horizon


# --------------------------------------------------------------------- (a)
def _moments(rng: np.random.Generator, n: int) -> tuple[np.ndarray, ...]:
    """Sample moments of correlated errors (a valid Gram matrix per state)."""
    draws = 40
    scale_c = rng.uniform(0.01, 1.0, n)[:, None]
    scale_p = rng.uniform(0.01, 1.0, n)[:, None]
    shared = rng.standard_normal((n, draws))
    e_c = scale_c * (shared + rng.standard_normal((n, draws)))
    e_p = scale_p * (
        rng.uniform(-1, 1, n)[:, None] * shared
        + rng.standard_normal((n, draws))
    )
    return (e_c**2).mean(1), (e_p**2).mean(1), (e_c * e_p).mean(1)


def test_a_kappa_form_excess_equals_the_exact_quadratic_difference() -> None:
    """(a): ``kappa [(w - u)^2 - (w* - u)^2] = V(w) - V(w*)`` within 1e-12.

    Reference: ``V(w) - V(w*)`` evaluated in exact rational arithmetic
    (``fractions.Fraction``) from the same float inputs, with ``w*`` the
    exact clipped minimizer. Tolerance: 1e-12 relative. The float form
    loses at most about ``eps (w - u)^2 / |(w - u)^2 - (w* - u)^2|``; with
    ``|w - w*| >= 0.05`` and ``|u| <= 2`` that is below ``1600 eps = 3.6e-13``.
    """
    rng = np.random.default_rng(48001)
    e_c, e_p, cross = _moments(rng, 300)
    target = cb.allocation_targets(e_c, e_p, cross)
    assert np.all(np.abs(target.u) <= 2.0)
    assert np.any(target.u < 0) and np.any(target.u > 1)
    w = rng.uniform(0.0, 1.0, 300)
    far = np.abs(w - target.w_star) >= 0.05
    got = cb.excess_kappa(w, target.kappa, target.u, target.w_star)
    checked = 0
    for i in np.flatnonzero(far):
        ec, ep, cc, wi = (Fraction(float(v[i])) for v in (e_c, e_p, cross, w))
        kappa = ec + ep - 2 * cc
        u = (ep - cc) / kappa
        ws = min(max(u, Fraction(0)), Fraction(1))

        def v(x: Fraction) -> Fraction:
            return x * x * ec + (1 - x) ** 2 * ep + 2 * x * (1 - x) * cc

        exact = float(v(wi) - v(ws))
        assert got[i] == pytest.approx(exact, rel=1e-12, abs=0.0)
        checked += 1
    assert checked > 200
    assert np.all(got >= 0.0)
    assert np.all(
        cb.excess_kappa(target.w_star, target.kappa, target.u, target.w_star)
        == 0.0
    )


def test_a_oracle_scores_use_the_kappa_form_and_deployable_the_draws() -> None:
    """Scoring: oracle rows by the moment form, deployable rows realized.

    Reference: the quadratic ``V(w)`` written out, and the realized score as
    an explicit loop over draws. Tolerance: 1e-12 relative (a few
    operations). Predictions outside ``[0, 1]`` are clipped and counted.
    """
    rng = np.random.default_rng(48002)
    n, draws = 50, 4
    e_c, e_p, cross = _moments(rng, n)
    target = cb.allocation_targets(e_c, e_p, cross)
    pred = rng.uniform(-0.2, 1.2, (n, 1))
    oracle = cb.score_allocation(pred, target, (e_c, e_p, cross), None)
    g = np.clip(pred[:, 0], 0, 1)
    v = g**2 * e_c + (1 - g) ** 2 * e_p + 2 * g * (1 - g) * cross
    np.testing.assert_allclose(oracle.mse, v, rtol=1e-12, atol=0)
    assert oracle.n_clipped == int(np.sum((pred < 0) | (pred > 1)))
    errors = (rng.standard_normal((n, draws)), rng.standard_normal((n, draws)))
    pred_d = rng.uniform(0, 1, (n, draws))
    dep = cb.score_allocation(pred_d, target, (e_c, e_p, cross), errors)
    loop = np.array(
        [
            sum(
                (
                    pred_d[i, j] * errors[0][i, j]
                    + (1 - pred_d[i, j]) * errors[1][i, j]
                )
                ** 2
                for j in range(draws)
            )
            / draws
            for i in range(n)
        ]
    )
    np.testing.assert_allclose(dep.mse, loop, rtol=1e-12, atol=0)
    np.testing.assert_allclose(
        dep.excess, loop - target.v_star, rtol=1e-12, atol=1e-15
    )


# -------------------------------------------------------------------- (a')
@pytest.mark.parametrize("rows", [1, 4])
def test_a_prime_weighted_learner_starts_at_the_kappa_weighted_mean(
    rows: int,
) -> None:
    """(a'): the initial prediction of the kappa-weighted fit is ``sum kappa u
    / sum kappa``, so the empty subset is A2 refit on the training rows.

    Reference: ``math.fsum`` of the products over ``math.fsum`` of the
    weights (independent of the learner and of ``kappa_baseline``).
    Tolerance: 1e-12 relative: the learner's weighted mean is a sum of 600
    (or 2400) terms, error about ``n eps`` = 5e-13 at worst.
    """
    rng = np.random.default_rng(48003)
    n = 600
    kappa = rng.lognormal(-4.0, 2.0, n)
    u = rng.normal(0.3, 0.5, n)
    x = rng.standard_normal((n, rows, 4))
    job = cb.FitJob(
        "regression",
        x,
        u,
        kappa / kappa.mean(),
        np.ones(n, bool),
        np.arange(n),
        x[:5],
        "kappa_excess",
        {"kappa": kappa, "u": u, "w_star": np.clip(u, 0, 1)},
    )
    model = cb._fit(job, cb.GRID[0], cb.Learner(seed=7), np.arange(n))
    reference = math.fsum(kappa * u) / math.fsum(kappa)
    assert float(np.ravel(model._baseline_prediction)[0]) == pytest.approx(
        reference, rel=1e-12, abs=0.0
    )
    assert cb.kappa_baseline(kappa, u) == pytest.approx(
        reference, rel=1e-12, abs=0.0
    )


def test_deployable_leaf_size_counts_states() -> None:
    """``min_samples_leaf`` counts states: ``E`` rows per state multiply it."""
    for setting in cb.GRID:
        one = cb.make_estimator("regression", setting, 7, 1)
        four = cb.make_estimator("quantile", setting, 7, 4, tau=0.5)
        assert one.min_samples_leaf == setting.min_leaf_states
        assert four.min_samples_leaf == 4 * setting.min_leaf_states
        assert one.l2_regularization == setting.l2


# --------------------------------------------------------------------- (b)
def test_b_shapley_shares_sum_to_the_total_and_match_all_orderings() -> None:
    """(b): ``sum phi = L(empty) - L(F)`` within 1e-12, and each ``phi_X``
    equals the mean marginal contribution over the 24 orderings.

    Reference: the permutation definition of the Shapley value (an
    independent algorithm) with value ``v(S) = -L(S)``. Tolerance: 1e-12
    absolute on losses of order 1 (sums of 8 or 24 terms).
    """
    rng = np.random.default_rng(48004)
    for _ in range(5):
        loss = {s: float(rng.uniform(0.5, 2.0)) for s in SUBSETS}
        phi = cb.shapley_values(loss)
        assert abs(phi.sum() - (loss[()] - loss[SUBSETS[-1]])) <= 1e-12
        for j in range(4):
            total = 0.0
            for order in itertools.permutations(range(4)):
                before = tuple(sorted(order[: order.index(j)]))
                total += loss[before] - loss[tuple(sorted((*before, j)))]
            assert abs(phi[j] - total / 24) <= 1e-12
    vectors = {s: rng.uniform(0.5, 2.0, 7) for s in SUBSETS}
    phi = cb.shapley_values(vectors)
    np.testing.assert_allclose(
        phi.sum(0), vectors[()] - vectors[SUBSETS[-1]], rtol=0, atol=1e-12
    )


# --------------------------------------------------------------------- (d)
def test_d_true_quantiles_cover_at_their_level_with_fixed_censoring() -> None:
    """(d): the true conditional quantiles of ``min(T, H_max)`` cover at
    ``tau`` below the cap; the cap rule and the bracket are exact.

    Synthetic ``ln T = mu(x) + 0.4 z`` with ``mu = ln 30 + 1.5 x``, ``x ~ U(0,
    2)`` for 4000 states, plus a planted set of 300 states with ``mu = ln 240
    + 0.3`` (their 0.5 and 0.9 quantiles lie above the cap); censoring is fixed
    at ``H_max = 240``. Reference: the true quantile ``mu + 0.4 z_tau``,
    whose conditional coverage is exactly ``tau`` for any selection on ``x``;
    the cap counts and the bracket are recounted by hand. Tolerance: ``4
    sqrt(tau (1 - tau) / n_below)`` (math spec, WU-0048 (d)).
    """
    from scipy.stats import norm

    rng = np.random.default_rng(48007)
    h_max, sd = 240, 0.4
    mu = np.concatenate(
        [
            np.log(30) + 1.5 * rng.uniform(0, 2, 4000),
            np.full(300, np.log(h_max) + 0.3),
        ]
    )
    log_t = mu + sd * rng.standard_normal(mu.size)
    event = log_t <= np.log(h_max)
    y = np.minimum(log_t, np.log(h_max))
    cap = float(np.log(h_max))
    qs = {}
    for tau in cb.TAUS:
        q = mu + sd * norm.ppf(tau)
        qs[tau] = np.minimum(q, cap)[:, None]
        record = cb.coverage(y, event, qs[tau], cap)
        below = q < cap
        assert record["n_below_cap"] == int(below.sum())
        assert record["n_at_cap"] == int((~below).sum())
        tol = 4 * np.sqrt(tau * (1 - tau) / below.sum())
        assert abs(record["coverage_below_cap"] - tau) <= tol, (tau, record)
        unknown = ~below & ~event
        known = np.where(below, y <= q, event & ~below)
        assert record["n_unknown"] == int(unknown.sum())
        assert record["bracket"][0] == pytest.approx(known.mean(), abs=1e-15)
        assert record["bracket"][1] == pytest.approx(
            (known | unknown).mean(), abs=1e-15
        )
    assert cb.coverage(y, event, qs[0.9], cap)["n_unknown"] > 0
    inner = cb.interval_coverage(y, event, qs[0.1], qs[0.9], cap)
    below = qs[0.9][:, 0] < cap
    tol = 4 * np.sqrt(0.8 * 0.2 / below.sum())
    assert abs(inner["coverage_below_cap"] - 0.8) <= tol, inner


def test_quantile_rearrangement_and_pinball_are_counted_and_exact() -> None:
    """Crossed quantile triples are sorted and counted; the pinball loss
    equals its definition (reference: written out by cases)."""
    q = np.array([[[0.0, 1.0, 2.0]], [[1.0, 0.5, 2.0]], [[3.0, 2.0, 1.0]]])
    ordered, crossed = cb.rearrange(q)
    assert crossed == 2
    assert np.all(np.diff(ordered, axis=-1) >= 0)
    y = np.array([0.5, 2.0, -1.0])
    loss = cb.pinball(y, np.array([[1.0], [1.0], [1.0]]), 0.1)
    np.testing.assert_allclose(
        loss, [0.9 * 0.5, 0.1 * 1.0, 0.9 * 2.0], rtol=1e-15
    )


# --------------------------------------------------------------------- (e)
def _harrell_brute(time, event, score) -> float:
    """Double loop of the M-4 rule (reference)."""
    num = den = 0.0
    for i in range(len(time)):
        for j in range(len(time)):
            if not event[i]:
                continue
            if time[i] < time[j] or (time[i] == time[j] and not event[j]):
                den += 1
                num += (
                    1.0
                    if score[i] < score[j]
                    else 0.5
                    if score[i] == score[j]
                    else 0.0
                )
    return num / den


def test_e_harrell_c_equals_the_brute_force_count_with_ties() -> None:
    """(e): Harrell's C equals a double loop to 1e-12 under the M-4 rules:
    tied event times excluded, tied predictions 1/2, an event at ``H_max``
    against a censored state at ``H_max`` comparable.

    Reference: the brute-force loop. Tolerance: 1e-12 (a ratio of counts).
    """
    rng = np.random.default_rng(48008)
    h_max = 20.0
    time = rng.integers(1, 21, 80).astype(float)
    event = rng.uniform(size=80) < 0.8
    time[~event] = h_max
    time[:5], event[:5] = h_max, True  # events at H_max
    score = rng.integers(0, 6, 80).astype(float)  # many ties
    c, n_comp, n_tied = cb.harrell_c(time, event, score)
    assert abs(c - _harrell_brute(time, event, score)) <= 1e-12
    assert n_comp > 0 and n_tied > 0
    two = np.column_stack([score, score[::-1]])
    c2, _, _ = cb.harrell_c(time, event, two)
    reference = 0.5 * (
        _harrell_brute(time, event, score)
        + _harrell_brute(time, event, score[::-1])
    )
    assert abs(c2 - reference) <= 1e-12
    score_inf = np.where(score > 3, np.inf, score)
    c3, _, _ = cb.harrell_c(time, event, score_inf)
    assert abs(c3 - _harrell_brute(time, event, score_inf)) <= 1e-12


# ------------------------------------------------------------- crossing time
def test_crossing_time_is_exact_on_a_log_linear_error_curve() -> None:
    """``T_c`` on ``e_H = a e^{lambda H}`` is ``ln(theta / a) / lambda``.

    The moments are built so that ``V(w*) + rho^2 = e_H^2`` (``C = 0``,
    ``E_C = E_P = 2 V``, so ``u = 1/2``). Reference: the analytic crossing,
    and ``oracle.characteristic_horizon`` for ``T`` (``ceil(T_c) = T``).
    Tolerance: 1e-9 absolute in steps (logs of numbers of order 1).
    """
    rho, theta, h_max = 0.01, 0.2, 240
    horizons = np.arange(1, h_max + 1)
    a = np.array([0.012, 0.015, 0.02, 0.05, 0.3])
    lam = np.array([0.02, 0.05, 0.01, 0.003, 0.01])
    rms = a[:, None] * np.exp(lam[:, None] * horizons[None, :])
    v = rms**2 - rho**2
    zero = np.zeros_like(v)
    cross = cb.crossing_time(2 * v, 2 * v, zero, rho, theta)
    first, event = characteristic_horizon(v, horizons, rho, theta)
    np.testing.assert_array_equal(cross.T, first)
    np.testing.assert_array_equal(cross.event, event)
    exact = np.log(theta / a) / lam
    for i in range(len(a)):
        if not event[i]:
            assert np.isinf(cross.T_c[i]) and cross.y[i] == np.log(h_max)
        elif first[i] == 1:
            assert cross.T_c[i] == 1.0
        else:
            assert abs(cross.T_c[i] - exact[i]) <= 1e-9
            assert first[i] - 1 <= cross.T_c[i] <= first[i]
    assert cross.n_first_step == int(np.sum(event & (first == 1)))
    assert (~event).sum() >= 1 and np.sum(event & (first == 1)) >= 1


def test_lyapunov_form_is_undefined_where_the_rate_is_not_positive() -> None:
    """M-5: ``T0`` from the hand formula, ``inf`` where ``I <= 0``."""
    profile = np.array([[0.5, 1.0, 2.0, 0.0], [0.5, 1.0, -0.1, 0.0]])
    t0, ok = cb.lyapunov_horizon(profile, 0.01, 0.2, 30)
    seed = -0.5 * np.log(np.exp(-1.0) + np.exp(-2.0))
    expected = 30 / 2.0 * (np.log(0.2 * np.sqrt(3) / 0.01) - seed)
    assert ok.tolist() == [True, False]
    assert t0[0] == pytest.approx(expected, rel=1e-14)
    assert np.isinf(t0[1])


# ------------------------------------------------------------ inner CV
def test_inner_cv_reads_training_states_only() -> None:
    """The setting is chosen on the training states: changing the test inputs
    does not change it, while a planted leak of test rows into training does.

    Reference: the choice itself (a structural property). The leak is a
    positive control: 2000 states of a strong interaction signal appended to
    150 states of a weak linear one, so a more complex setting wins once the
    leaked rows are in the folds.
    """
    rng = np.random.default_rng(48009)
    n, n_leak = 150, 2000
    x = rng.standard_normal((n, 1, 4))
    y = 0.2 * x[:, 0, 0] + rng.standard_normal(n)
    x_leak = rng.standard_normal((n_leak, 1, 4))
    y_leak = 2 * np.sin(3 * x_leak[:, 0, 0]) * np.cos(3 * x_leak[:, 0, 1])
    learner = cb.Learner(seed=13)

    def job(xs, ys, x_test) -> cb.FitJob:
        return cb.FitJob(
            "regression",
            xs,
            ys,
            None,
            np.ones(len(ys), bool),
            np.arange(len(ys)),
            x_test,
            "squared",
            {"y": ys},
        )

    plain, scores, _ = cb.select_setting(job(x, y, x_leak), learner)
    other, _, _ = cb.select_setting(job(x, y, -x_leak[:7] * 5), learner)
    assert plain == other
    leaked, _, _ = cb.select_setting(
        job(np.concatenate([x, x_leak]), np.concatenate([y, y_leak]), x),
        learner,
    )
    assert leaked != plain, (plain, leaked, scores)
    assert set(scores) == {s.name for s in cb.GRID}


def test_folds_are_contiguous_blocks_in_time_order() -> None:
    """Each fold is a run of consecutive times, and the folds cover once."""
    rng = np.random.default_rng(48010)
    order = rng.permutation(103) * 3 + 7
    folds = cb.time_folds(order, 5)
    assert len(folds) == 5
    assert sorted(np.concatenate(folds).tolist()) == list(range(103))
    ranks = np.argsort(np.argsort(order))
    for fold in folds:
        r = np.sort(ranks[fold])
        assert np.all(np.diff(r) == 1)


# ------------------------------------------------------------ the readings
def test_ratio_rows_guard_effective_size_and_count_failures() -> None:
    """A ratio reads "undetermined (n_eff < 50)" below the guard; a resample
    whose denominator mean is not positive is failed and counted."""
    rng = np.random.default_rng(48011)
    n = 200
    den = rng.uniform(1, 2, n)
    num = 1.2 * den
    index = cb.resample_indices(n, 100, 5, np.random.default_rng(48012))
    row = cb.ratio_row(num, den, index, 0.95, n_eff=(49.0, 500.0))
    assert row["reading"] == "undetermined" and row["reason"] == "n_eff < 50"
    row = cb.ratio_row(num, den, index, 0.95, n_eff=(60.0,))
    assert row["reading"] == "substantial"
    signed = np.where(np.arange(n) < 100, 1.0, -1.0) * den
    row = cb.ratio_row(num, signed, index, 0.95)
    assert row["n_failed_resamples"] > 0
    assert cb.kish_size(np.ones(10)) == pytest.approx(10.0)
    assert cb.kish_size(np.array([1.0] + [0.0] * 9)) == pytest.approx(1.0)


def test_pair_constraints_cover_every_pair_once() -> None:
    """``interaction_cst``: singletons for the additive model, one group of
    two for each pair (the other two singletons), none for the full model."""
    cst = cb.pair_constraints()
    assert cst["add"] == [[0], [1], [2], [3]]
    assert cst["full"] is None
    for j, k in itertools.combinations(range(4), 2):
        groups = cst[CONDITIONS[j] + CONDITIONS[k]]
        assert groups[0] == [j, k]
        assert sorted(sum(groups, [])) == [0, 1, 2, 3]


# ------------------------------------------------------- rulings R1 to R3
def test_r3_dependence_terms_sum_to_the_paired_difference() -> None:
    """R3: ``T0 + T1 + T2`` equals the paired difference per state, to 1e-9.

    Reference: ``(S - S_A1) - (Q - Q_A1)`` written out draw by draw (the
    realized blend squared, minus ``e_P^2``, minus the quadratic ``V`` at
    each draw's weight, plus ``E_P``). Tolerance: 1e-9 relative to the
    state's largest term (the identity is algebraic; round-off is a few ulps
    of terms of that size). Weights that vary over draws, and one state with
    a constant weight (``d = 0``, so ``T1 = T2 = 0`` exactly).
    """
    rng = np.random.default_rng(48013)
    n, draws = 40, 4
    e_c_m, e_p_m, cross = _moments(rng, n)
    e_c = rng.standard_normal((n, draws)) * 0.3
    e_p = rng.standard_normal((n, draws)) * 0.5
    w = rng.uniform(0, 1, (n, draws))
    w[0] = 0.4
    terms = cb.dependence_terms(w, e_c, e_p, (e_c_m, e_p_m, cross))
    for i in range(n):
        s = (
            sum(
                (w[i, j] * e_c[i, j] + (1 - w[i, j]) * e_p[i, j]) ** 2
                - e_p[i, j] ** 2
                for j in range(draws)
            )
            / draws
        )
        q = (
            sum(
                w[i, j] ** 2 * e_c_m[i]
                + (1 - w[i, j]) ** 2 * e_p_m[i]
                + 2 * w[i, j] * (1 - w[i, j]) * cross[i]
                - e_p_m[i]
                for j in range(draws)
            )
            / draws
        )
        parts = terms["t0"][i] + terms["t1"][i] + terms["t2"][i]
        scale = max(
            abs(terms["t0"][i]),
            abs(terms["t1"][i]),
            abs(terms["t2"][i]),
            abs(s - q),
            1e-300,
        )
        assert abs(parts - (s - q)) <= 1e-9 * scale, i
        assert abs(terms["total"][i] - (s - q)) <= 1e-9 * scale, i
    assert terms["t1"][0] == 0.0 and terms["t2"][0] == 0.0


def test_r3_constant_weight_rule_has_no_dependence_part() -> None:
    """A rule whose weight does not vary over draws has ``T1 + T2 = 0``, so
    its (f2) interval is ``[0, 0]`` and it reads "no detectable dependence
    bias" whatever its ``z`` (a constant rule is the A2 case)."""
    rng = np.random.default_rng(48014)
    n, draws = 60, 4
    mom = _moments(rng, n)
    errors = (rng.standard_normal((n, draws)), rng.standard_normal((n, draws)))
    weight = np.full((n, draws), 0.3)
    index = cb.resample_indices(n, 50, 5, np.random.default_rng(48015))
    out = cb.dependence_bias(weight, errors, mom, (mom, mom), (10, 10), index)
    assert out["dependence"]["estimate"] == 0.0
    assert out["dependence"]["ci"] == [0.0, 0.0]
    assert out["reading"] in (
        "no detectable dependence bias",
        "realized-noise outlier, no detectable dependence bias",
    )


def test_r2_guard_uses_the_moment_form_excess_not_the_realized_one() -> None:
    """R2: the guard's second size is Kish of the substituted excess.

    A realized excess with mean near 0 and large draw noise has a tiny Kish
    size (signal to noise); its moment-form counterpart, positive and spread
    evenly, has Kish near n. Reference: Kish computed by hand.
    """
    n = 400
    kappa = np.ones(n)
    substituted = np.full(n, 0.01)
    sizes = cb.guard_sizes(kappa, substituted)
    assert sizes == (pytest.approx(n), pytest.approx(n))
    rng = np.random.default_rng(48016)
    realized = substituted + rng.standard_normal(n)
    assert cb.kish_size(realized) < 5 < min(sizes)


def test_r1_pair_that_fits_worse_reads_no_gain() -> None:
    """R1: a pair whose ``Delta`` upper bound is below 0 reads "no interaction
    gain; the pair model fits worse" (also its loss ratio); a clear gain is
    "interaction gain detected"; otherwise "no interaction gain detected".

    Reference: hand-built per-state losses (the pair losses are the additive
    ones scaled by 1.3, by 0.5, or equal plus noise).
    """
    rng = np.random.default_rng(48017)
    n = 300
    add = rng.uniform(1.0, 2.0, n)
    losses = {"add": add}
    for j, k in cb.PAIRS:
        name = CONDITIONS[j] + CONDITIONS[k]
        losses[name] = add * (1.0 + 0.02 * rng.standard_normal(n))
    losses["RO"] = 1.3 * add
    losses["RI"] = 0.5 * add
    index = cb.resample_indices(n, 200, 5, np.random.default_rng(48018))
    rows = cb.pair_rows(losses, index)["pairs"]
    assert rows["RO"]["reading"] == cb.NO_GAIN
    assert rows["RO"]["loss_ratio"]["reading"] == cb.NO_GAIN
    assert rows["RI"]["reading"] == "interaction gain detected"
    assert rows["ON"]["reading"] in ("no interaction gain detected", cb.NO_GAIN)
