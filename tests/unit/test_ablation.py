"""Tests of the ablation estimate rows (WU-0039b, ``lpcstudy/ablation.py``).

The rows are (a) the A4 coefficient variants and (b) the profile conditions
R, O, I, N by the Q-N procedure. The ROADMAP criteria of WU-0039 that a unit
test can carry are here:

* zero-term weights equal the hand formula within 1e-12 relative;
* a refit on synthetic data generated without the term recovers the other
  coefficients within a stated tolerance (and the boundary case of WU-0036);
* the full variant reproduces A4 bitwise (and the full refit reproduces A5);
* the drop-N row reproduces Q-N bitwise;
* Shapley shares sum to ``R^2(F) - R^2(empty)`` within 1e-12.

The null rate of irrelevant conditions is a simulation, in
``tests/slow/test_ablation_null_rate.py``. Every random input comes from a fixed
``np.random.default_rng(<int>)`` or a test-only ``make_rng`` label.
"""

from __future__ import annotations

import itertools
import math
import sys
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from scipy.optimize import least_squares, nnls

from lpcstudy import ablation
from lpcstudy.allocation import (
    ProfileProxies,
    SeedProxy,
    deployable_profile,
    global_weight,
    log_scale_fit,
    state_horizon_target,
)
from lpcstudy.analysis import qn_profile_block
from lpcstudy.config import SMOKE
from lpcstudy.data import make_rng
from lpcstudy.ensemble import EnsembleMoments, EvaluationDraws
from lpcstudy.oracle import oracle_weight
from lpcstudy.pipeline import (
    FittedRules,
    SplitData,
    fit_regime_maps,
    rule_weights,
    score_rules,
)

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "slow"))
import wu0006_harness as wu  # noqa: E402  (the WU-0006.3 null design)

NOISE = 0.01
COEFS_TRUE = {"a": 0.3, "b": 1.0, "a_prime": 1.0, "b_prime": 0.05}


# ------------------------------------------------------------ synthetic data
def _old_seed_proxy_fit(
    feature_sq: np.ndarray, floor_sq: np.ndarray, seed_sq: np.ndarray
) -> tuple[float, float, int, int]:
    """The body of ``SeedProxy.fit`` before WU-0039b, copied verbatim."""
    scale = np.median(seed_sq)
    design = np.column_stack([feature_sq, floor_sq]) / scale
    coef, _ = nnls(design, seed_sq / scale)
    start = np.log(np.maximum(coef, 1e-6))
    log_seed = np.log(seed_sq / scale)

    def residual(log_coef: np.ndarray) -> np.ndarray:
        return np.log(design @ np.exp(log_coef) + 1e-300) - log_seed

    sol = least_squares(residual, start, loss="soft_l1")
    slope, floor = np.exp(sol.x)
    return float(slope), float(floor), int(sol.nfev), int(sol.status)


def _log_uniform(rng: np.random.Generator, low: float, high: float, n: int):
    """Log-uniform draws on ``[low, high]``."""
    return np.exp(rng.uniform(np.log(low), np.log(high), n))


def _split(
    rng: np.random.Generator, n: int, n_draws: int, n_hor: int
) -> SplitData:
    """A split whose seeds follow the A4 proxy model, with growing errors.

    Recurrence distances are log-uniform on [0.005, 0.05] and ``nu_hat`` on
    [0.5, 3]; the oracle seeds follow ``eps^2 = a (R nu)^2 + b (rho nu)^2`` and
    ``delta^2 = a' (rho nu)^2 + b' rho^2`` (``COEFS_TRUE``) with lognormal
    scatter 0.2. CP and PLP errors are Gaussian with state scales tied to the
    seeds, growing as ``exp(h / 30)``.
    """
    distance = _log_uniform(rng, 0.005, 0.05, n)[:, None] * _log_uniform(
        rng, 0.9, 1.1, n * n_draws
    ).reshape(n, n_draws)
    est_nu = _log_uniform(rng, 0.5, 3.0, n)[:, None] * _log_uniform(
        rng, 0.9, 1.1, n * n_draws
    ).reshape(n, n_draws)
    r_med, nu_med = np.median(distance, axis=1), np.median(est_nu, axis=1)
    c = COEFS_TRUE
    analog = np.sqrt(
        (c["a"] * (r_med * nu_med) ** 2 + c["b"] * (NOISE * nu_med) ** 2)
        * np.exp(0.2 * rng.standard_normal(n))
    )
    est = np.sqrt(
        (c["a_prime"] * (NOISE * nu_med) ** 2 + c["b_prime"] * NOISE**2)
        * np.exp(0.2 * rng.standard_normal(n))
    )
    growth = np.exp(np.arange(1, n_hor + 1) / 30.0)
    m_draws = 20

    def errors(scale: np.ndarray, draws: int) -> np.ndarray:
        return (
            scale[:, None, None]
            * growth[None, None, :]
            * rng.standard_normal((n, draws, n_hor))
        )

    cp_scale, plp_scale = 3.0 * analog / NOISE * 0.01, est / NOISE * 0.01
    cp, plp = errors(cp_scale, m_draws), errors(plp_scale, m_draws)
    moments = EnsembleMoments(
        horizons=np.arange(1, n_hor + 1),
        mean_cp=cp.mean(1),
        mean_plp=plp.mean(1),
        sq_cp=(cp**2).mean(1),
        sq_plp=(plp**2).mean(1),
        cross=(cp * plp).mean(1),
        analog_seed=analog,
        est_seed=est,
        noise_sens=_log_uniform(rng, 0.01, 1.0, n),
    )
    evals = EvaluationDraws(
        horizons=np.arange(1, n_hor + 1),
        cp_err=errors(cp_scale, n_draws),
        plp_err=errors(plp_scale, n_draws),
        verify_noise=NOISE * rng.standard_normal((n, n_draws, n_hor)),
        distance=distance,
        est_nu=est_nu,
        growth_proxy=rng.uniform(0.5, 1.5, (n, n_draws)) / 30.0,
        gain_proxy=np.ones((n, n_draws, n_hor)),
        inputs=np.zeros((n, n_draws, 1)),
        noise_sens=_log_uniform(rng, 0.01, 1.0, n * n_draws).reshape(
            n, n_draws
        ),
    )
    return SplitData(moments=moments, evals=evals)


@pytest.fixture(scope="module")
def world():
    """A synthetic core cell, its fitted rules and the production A4/A5 scores.

    The rules are fitted as ``pipeline.fit_rules`` fits them (``ProfileProxies``
    on construction, A2, ``fit_regime_maps`` on the deployable profiles), with
    a stub error predictor (A3 plays no part here). The scores are
    ``score_rules`` of ``rule_weights``: the production path of A4 and A5.
    """
    rng = np.random.default_rng(39002)
    config = replace(SMOKE, regime_counts=(2, 3, 4), bootstrap_resamples=60)
    n_hor = config.horizon_max
    n_draws = 2
    splits = {
        "construction": _split(rng, 160, n_draws, n_hor),
        "calibration": _split(rng, 80, n_draws, n_hor),
        "test": _split(rng, 80, n_draws, n_hor),
    }
    con, cal = splits["construction"], splits["calibration"]
    proxies = ProfileProxies.fit(
        con.evals.distance,
        con.evals.est_nu,
        con.moments.analog_seed,
        con.moments.est_seed,
        NOISE,
    )
    lt, col = config.steps_per_lyapunov, config.reference_horizon - 1
    profiles = [
        deployable_profile(s.evals, proxies, NOISE, lt) for s in (con, cal)
    ]
    a2 = global_weight(con.moments)
    regimes, chosen = fit_regime_maps(
        profiles[0],
        profiles[1],
        oracle_weight(con.moments)[:, col],
        np.log(
            state_horizon_target(
                con.moments, NOISE, config.primary_threshold
            )
        ),
        cal.moments,
        cal.evals,
        a2,
        config,
    )
    rules = FittedRules(
        proxies=proxies,
        global_weights=a2,
        predictor=SimpleNamespace(
            weights=lambda inputs, horizons: np.zeros(
                (*inputs.shape[:2], len(horizons))
            )
        ),
        regimes=regimes,
        chosen_regimes=chosen,
    )
    horizons = np.arange(1, n_hor + 1)
    core = SimpleNamespace(
        system="wu0039b-test",
        noise=NOISE,
        library_size=10_000,
        horizons=horizons,
        splits=splits,
    )
    weights = rule_weights(rules, splits["test"], NOISE, config, horizons)
    scores = score_rules(
        weights, splits["test"], horizons, config, config.primary_threshold
    )
    return SimpleNamespace(
        core=core,
        rules=rules,
        config=config,
        weights=weights,
        scores=scores,
    )


# ---------------------------------------------------------------- (a) A4 rows
def test_log_scale_fit_is_the_long_standing_proxy_fit_bitwise() -> None:
    """``SeedProxy.fit`` through ``log_scale_fit`` equals the old fit bitwise.

    Regression guard (not correctness evidence): the reference is a verbatim
    copy of the pre-WU-0039b body of ``SeedProxy.fit``. Same operations, so the
    two coefficients, ``nfev`` and ``status`` must be identical (``==``).
    """
    rng = np.random.default_rng(39001)
    f, g = _log_uniform(rng, 1e-2, 1e2, 500), _log_uniform(rng, 1e-2, 1e2, 500)
    seed = (0.3 * f + 1.0 * g) * np.exp(0.3 * rng.standard_normal(500))
    got = SeedProxy.fit(f, g, seed)
    assert (got.slope, got.floor, got.nfev, got.status) == _old_seed_proxy_fit(
        f, g, seed
    )


@pytest.mark.parametrize("name", list(ablation.COEFFICIENTS))
def test_zero_variant_weight_equals_the_hand_formula(world, name: str) -> None:
    """Each zero variant's weight equals the hand formula within 1e-12 relative.

    Reference: ``w = (a' rho^2 nu^2 + b' rho^2) / (a R^2 nu^2 + b rho^2 nu^2 +
    a' rho^2 nu^2 + b' rho^2)`` with ``nu = min(nu_hat, nu_cap)`` and the named
    coefficient set to 0, written here from the A4 definition (v3 section 5),
    not through ``ProfileProxies``. Tolerance 1e-12 (the ROADMAP criterion):
    the production path takes a square root and squares it again, and adds and
    divides positive terms, a few ulps (about 1e-15) in all.
    """
    proxies = world.rules.proxies
    test = world.core.splits["test"].evals
    coef = {
        "a": proxies.analog.slope,
        "b": proxies.analog.floor,
        "a_prime": proxies.estimation.slope,
        "b_prime": proxies.estimation.floor,
    }
    coef[name] = 0.0
    nu = np.minimum(test.est_nu, proxies.nu_cap)
    assert np.any(test.est_nu > proxies.nu_cap)  # the cap is exercised
    rho2 = NOISE**2
    delta2 = coef["a_prime"] * rho2 * nu**2 + coef["b_prime"] * rho2
    eps2 = coef["a"] * test.distance**2 * nu**2 + coef["b"] * rho2 * nu**2
    hand = delta2 / (eps2 + delta2)
    got, floored = ablation.a4_weight(
        ablation.zero_variant(proxies, name), world.core.splits["test"], NOISE
    )
    assert floored == {"entries": 0, "states": 0}
    np.testing.assert_allclose(got, hand, rtol=1e-12, atol=0.0)


def test_undefined_weights_are_counted_and_set_to_plp() -> None:
    """A zero denominator is counted per entry and per state; its weight is 0.

    Reference: hand construction. With ``a = b = 0`` and ``a' = b' = 0`` both
    seeds are 0, so ``eps^2 + delta^2 = 0`` in every (state, draw): 3 states x
    2 draws = 6 entries, 3 states, and ``closed_form_weight`` returns 0 there
    (its ``1e-300`` floor), never NaN. With only ``a = 0`` and ``b = 0`` on the
    analog side, ``delta^2 > 0`` everywhere, so nothing is counted and the
    weight is 1 (CP). Exact.
    """
    zero = SeedProxy(slope=0.0, floor=0.0)
    split = SimpleNamespace(
        evals=SimpleNamespace(
            distance=np.full((3, 2), 0.02), est_nu=np.ones((3, 2))
        )
    )
    both = ProfileProxies(analog=zero, estimation=zero, nu_cap=10.0)
    weight, floored = ablation.a4_weight(both, split, NOISE)
    assert floored == {"entries": 6, "states": 3}
    assert np.array_equal(weight, np.zeros((3, 2)))
    one = replace(both, estimation=SeedProxy(slope=1.0, floor=0.0))
    weight, floored = ablation.a4_weight(one, split, NOISE)
    assert floored == {"entries": 0, "states": 0}
    assert np.array_equal(weight, np.ones((3, 2)))


def _design(
    rng: np.random.Generator, n: int, sigma: float, dropped: str
) -> tuple[dict, dict]:
    """A construction design whose seeds are generated without ``dropped``.

    The four columns are log-uniform on [1e-2, 1e2]; the proxy that owns
    ``dropped`` is generated from its other term alone, the other proxy from
    both terms, each with lognormal scatter ``sigma``. Returns the design and
    the true coefficients (the dropped one 0).
    """
    truth = dict(COEFS_TRUE, b=1.0, b_prime=1.0)
    truth[dropped] = 0.0
    cols = {
        k: _log_uniform(rng, 1e-2, 1e2, n) for k in ("af", "ag", "ef", "eg")
    }

    def seed(slope: float, floor: float, f: np.ndarray, g: np.ndarray):
        return (slope * f + floor * g) * np.exp(sigma * rng.standard_normal(n))

    design = {
        "analog_f": cols["af"],
        "analog_g": cols["ag"],
        "est_f": cols["ef"],
        "est_g": cols["eg"],
        "analog_seed_sq": seed(truth["a"], truth["b"], cols["af"], cols["ag"]),
        "est_seed_sq": seed(
            truth["a_prime"], truth["b_prime"], cols["ef"], cols["eg"]
        ),
    }
    return design, truth


def _log_se(columns: list[np.ndarray], coef: np.ndarray, sigma: float):
    """Asymptotic standard errors of ``ln c`` of the log-scale fit.

    Linearization at the truth: ``J_ij = c_j X_ij / sum_k c_k X_ik`` (the
    derivative of the log model in ``ln c_j``), covariance ``sigma^2 (J^T
    J)^-1``. ``soft_l1`` with residuals of size 0.1 (``f_scale`` 1) is
    quadratic to within 0.25 %, so the least-squares covariance applies.
    """
    x = np.column_stack(columns)
    jac = x * coef / (x @ coef)[:, None]
    return sigma * np.sqrt(np.diag(np.linalg.inv(jac.T @ jac)))


@pytest.mark.parametrize("dropped", list(ablation.COEFFICIENTS))
def test_refit_recovers_the_other_coefficients(dropped: str) -> None:
    """On data generated without a term, the refit recovers the other three.

    Reference: the true coefficients of the synthetic design (``_design``,
    n = 2000 construction states, lognormal scatter 0.1). The variant's
    partner is refitted alone by ``log_scale_fit``; the other proxy keeps its
    two-term fit (``ProfileProxies`` fitted here as production does, from the
    same design). Tolerance: ``|ln c_hat - ln c| <= 5 SE`` per coefficient,
    with SE from the linearized covariance (``_log_se``: ``0.1 / sqrt(2000) =
    0.0022`` for the one-term refit, 0.003 to 0.005 for two terms; checked
    against 200 replications, SD within 4 %). Under normality a 5 SE miss has
    probability 6e-7 per coefficient, so 12 checks fail by chance at about
    7e-6. The least-squares stopping error (``xtol = 1e-8`` relative) is far
    below one SE. The removed coefficient is exactly 0 in the variant.
    """
    sigma, n = 0.1, 2000
    index = list(ablation.COEFFICIENTS).index(dropped)
    rng = np.random.default_rng(39003 + index)
    design, truth = _design(rng, n, sigma, dropped)
    proxies = ProfileProxies(
        analog=SeedProxy.fit(
            design["analog_f"], design["analog_g"], design["analog_seed_sq"]
        ),
        estimation=SeedProxy.fit(
            design["est_f"], design["est_g"], design["est_seed_sq"]
        ),
        nu_cap=np.inf,
    )
    variant, record = ablation.refit_variant(proxies, design, dropped)
    got = record["coefficients"]
    assert got[dropped] == 0.0
    owner = ablation.COEFFICIENTS[dropped][0]
    partner = record["partner"]
    f_key, g_key, _ = ablation.PROXY_COLUMNS[owner]
    kept_col = design[g_key] if partner in ("b", "b_prime") else design[f_key]
    se_partner = _log_se([kept_col], np.array([truth[partner]]), sigma)[0]
    assert abs(math.log(got[partner] / truth[partner])) <= 5 * se_partner
    other = "estimation" if owner == "analog" else "analog"
    f_key, g_key, _ = ablation.PROXY_COLUMNS[other]
    names = [k for k, (p, _) in ablation.COEFFICIENTS.items() if p == other]
    coef = np.array([truth[k] for k in names])
    se = _log_se([design[f_key], design[g_key]], coef, sigma)
    for k, true, s in zip(names, coef, se):
        assert abs(math.log(got[k] / true)) <= 5 * s, (k, got[k], true, s)


@pytest.mark.parametrize("dropped", ["b", "a"])
def test_boundary_term_is_flagged_and_refit_reproduces_the_fit(
    dropped: str,
) -> None:
    """Noise-free data without a term: the fit puts it at its bound.

    This is the boundary case of WU-0036 (``b`` fitted at about 0 in every
    cell). Reference: exact analog seeds ``seed^2 = c x`` from one of the two
    A4 columns, ``x = (R nu)^2`` or ``(rho nu)^2``, on 2000 states that also
    serve as the evaluation states. The two-term fit cannot return an exact 0
    (``exp``), so the check is the boundary rule of M-2: zeroing the absent
    coefficient changes no weight by more than 1e-6 (``at_bound``), while
    zeroing the kept one does. Tolerances: the kept coefficient of the
    two-term fit is within 1e-6 relative (its relative error is at most the
    absent term's largest share of the seed, asserted below 1e-6 as well); the
    one-term refit is a zero-residual problem solved to the ``xtol = 1e-8``
    relative step of ``least_squares`` (Gauss-Newton converges quadratically
    there), so 1e-8.
    """
    rng = np.random.default_rng(39010)
    n = 2000
    distance = _log_uniform(rng, 0.005, 0.05, n)[:, None]
    est_nu = _log_uniform(rng, 0.5, 3.0, n)[:, None]
    split = SimpleNamespace(
        evals=SimpleNamespace(distance=distance, est_nu=est_nu)
    )
    f, g = (distance[:, 0] * est_nu[:, 0]) ** 2, (NOISE * est_nu[:, 0]) ** 2
    kept, value = ("a", 0.3) if dropped == "b" else ("b", 1.0)
    seed_sq = value * (f if kept == "a" else g)
    est_f, est_g = g, np.full(n, NOISE**2)
    design = {
        "analog_f": f,
        "analog_g": g,
        "analog_seed_sq": seed_sq,
        "est_f": est_f,
        "est_g": est_g,
        "est_seed_sq": est_f + 0.05 * est_g,
    }
    proxies = ProfileProxies(
        analog=SeedProxy.fit(f, g, seed_sq),
        estimation=SeedProxy.fit(est_f, est_g, design["est_seed_sq"]),
        nu_cap=np.inf,
    )
    full, _ = ablation.a4_weight(proxies, split, NOISE)
    change = {
        name: float(
            np.max(
                np.abs(
                    ablation.a4_weight(
                        ablation.zero_variant(proxies, name), split, NOISE
                    )[0]
                    - full
                )
            )
        )
        for name in ablation.COEFFICIENTS
    }
    records = ablation.coefficient_records(proxies, design, change)
    assert records[dropped]["at_bound"] is True
    assert records[kept]["at_bound"] is False
    assert records[dropped]["max_term_share"] <= 1e-6
    assert abs(records[kept]["value"] / value - 1.0) <= 1e-6
    _, record = ablation.refit_variant(proxies, design, dropped)
    assert record["partner"] == kept
    assert abs(record["partner_value"] / value - 1.0) <= 1e-8


def test_full_variant_reproduces_a4_and_full_refit_reproduces_a5(world) -> None:
    """The unchanged proxies give A4 bitwise; the four-column refit gives A5.

    Reference: the production path, ``rule_weights`` then ``score_rules``, of
    the fixture (independent of ``lpcstudy.ablation``). Exact (``==`` on the
    weight arrays and on the per-state MSE). Also: every zero and refit row
    exists with a finite ratio and no failed resample; each coefficient's
    ``max_abs_weight_change`` is the largest ``|w(zero) - w(A4)|`` recomputed
    here; and a coefficient flagged at its bound reads "not identifiable" in
    both rows (M-2).
    """
    core, rules, config = world.core, world.rules, world.config
    test = core.splits["test"]
    weight, _ = ablation.a4_weight(rules.proxies, test, NOISE)
    assert np.array_equal(
        np.broadcast_to(weight[..., None], test.evals.cp_err.shape),
        world.weights["A4"],
    )
    a4 = ablation.a4_coefficient_block(
        core, rules, world.scores["A4"].state_mse_ref, config
    )
    assert a4["full"]["reproduces_A4"] is True
    for mode in ablation.MODES:
        assert set(a4["variants"][mode]) == set(ablation.COEFFICIENTS)
        for row in a4["variants"][mode].values():
            assert np.isfinite(row["mse_ratio"])
            assert row["n_failed_resamples"] == 0
    for name, record in a4["coefficients"].items():
        zero, _ = ablation.a4_weight(
            ablation.zero_variant(rules.proxies, name), test, NOISE
        )
        assert record["max_abs_weight_change"] == float(
            np.max(np.abs(zero - weight))
        )
        assert record["at_bound"] is (
            record["max_abs_weight_change"] <= ablation.IDENTIFIABLE_CHANGE
        )
        if record["at_bound"]:
            for mode in ablation.MODES:
                row = a4["variants"][mode][name]
                assert row["reading"] == "not identifiable", (name, mode)
    a5 = ablation.a5_ablation_block(
        core, rules, world.scores["A5"].state_mse_ref, config
    )
    assert a5["full"]["reproduces_A5"] is True
    assert a5["full"]["chosen_K"] == rules.chosen_regimes
    assert set(a5["without"]) == set(ablation.CONDITIONS)


@pytest.mark.parametrize(
    ("lower", "upper", "reading"),
    [
        (0.5, 0.999, "lowers"),
        (0.9, 1.0, "negligible"),
        (1.0, 1.05, "negligible"),
        (1.0, 1.0501, "undetermined"),
        (1.0001, 1.05, "small"),
        (1.0001, 1.0501, "needed, size not determined"),
        (1.05, 2.0, "needed, size not determined"),
        (1.0501, 2.0, "substantial"),
        (float("-inf"), float("inf"), "undetermined"),
        (float("nan"), 1.0, "undetermined"),
    ],
)
def test_ratio_reading_follows_the_m2_table(
    lower: float, upper: float, reading: str
) -> None:
    """The MSE-ratio reading follows the table of M-2 at its edges.

    Reference: the table as quoted in the applied-mathematician's note
    (WU-0041b, M-2), first match from the top: upper < 1; lower <= 1 and upper
    <= 1.05; lower > 1 and upper <= 1.05; lower > 1.05; lower > 1 and upper >
    1.05; otherwise undetermined. Exact strings.
    """
    assert ablation.ratio_reading(lower, upper) == reading


def test_ratio_guards_come_before_the_table_in_the_m2_order() -> None:
    """Fewer than 50 states, then NaN or infinite bounds, then the boundary.

    Reference: the order written in M-2. A row at its bound reads "not
    identifiable" whatever its interval, but an infinite bound still reads
    "undetermined" first. Exact.
    """
    reason = ablation.ratio_reading_reason
    assert reason(0.9, 1.0, 49) == ("undetermined", "n_states < 50")
    assert reason(-np.inf, np.inf, 80, identifiable=False) == (
        "undetermined",
        "failed resamples >= threshold",
    )
    assert reason(1.2, 1.3, 80, identifiable=False) == (
        "not identifiable",
        "fitted at the boundary",
    )
    assert reason(1.2, 1.3, 80) == ("substantial", None)


# ------------------------------------------------------- (b1), (b2) Q-N rows
@pytest.fixture(scope="module")
def profile_rows():
    """Q-N and the profile ablation on the WU-0006.3 null design, small size.

    300 training and 200 test states (``wu0006_harness.delta_states``, phi 0),
    100 resamples of blocks of 5, the same integer model seed and a fresh
    test-only generator per call with the same labels (so the same
    resamples, as production shares Q-N's). The horizon cap is the 20%
    quantile of the test horizons, so 160 of 200 test states count as
    censored and 40 as uncensored (below the 50-state rule of M-5).
    """
    rng = np.random.default_rng(39020)
    x_train, w_train, t_train = wu.delta_states(rng, 300, 0.0)
    x_test, w_test, t_test = wu.delta_states(rng, 200, 0.0)
    args = (x_train, x_test, w_train, w_test, t_train, t_test)
    common = {"seed": 39021, "n_resamples": 100, "block": 5}
    qn = qn_profile_block(
        *args, **common, boot_seed=make_rng(39022, "wu0039b-test", "boot")
    )
    rows = ablation.profile_ablation_block(
        *args,
        **common,
        boot_seed=make_rng(39022, "wu0039b-test", "boot"),
        horizon_cap=float(np.quantile(t_test, 0.2)),
    )
    return qn, rows, t_test


def _bits(value: object) -> object:
    """Float leaves as their IEEE bytes (hex), so ``==`` is bitwise."""
    if isinstance(value, float):
        return value.hex()
    if isinstance(value, list):
        return [_bits(v) for v in value]
    return value


def test_drop_n_row_reproduces_qn_bitwise(profile_rows) -> None:
    """The leave-one-out row of N carries Q-N's leaves, bit for bit.

    Reference: ``analysis.qn_profile_block`` on the same inputs, model seed and
    resample labels. Compared per target: ``delta_r2``, ``ci``,
    ``n_failed_resamples``, ``n_train``, ``n_test``, ``r2_three`` (as
    ``r2_without``), ``r2_four`` (as the full subset), and for the two weight
    targets ``reading`` and ``reason``. Exact (float hex).
    """
    qn, rows, _ = profile_rows
    for target in ("logit_w_interior", "w_zero_indicator", "log_horizon"):
        q, entry = qn[target], rows[target]
        drop_n = entry["leave_one_out"]["N"]
        pairs = [
            (drop_n["delta_r2"], q["delta_r2"]),
            (drop_n["ci"], q["ci"]),
            (drop_n["n_failed_resamples"], q["n_failed_resamples"]),
            (drop_n["r2_without"], q["r2_three"]),
            (entry["r2_by_subset"]["ROIN"], q["r2_four"]),
            (entry["n_train"], q["n_train"]),
            (entry["n_test"], q["n_test"]),
        ]
        if target != "log_horizon":
            pairs += [
                (drop_n["reading"], q["reading"]),
                (drop_n["reason"], q["reason"]),
            ]
        for got, want in pairs:
            assert _bits(got) == _bits(want), (target, got, want)


def test_shapley_shares_sum_to_the_full_gain_and_match_permutations(
    profile_rows,
) -> None:
    """Shapley shares sum to the full gain and equal the permutation form.

    References: (1) the efficiency identity of the Shapley value; (2) an
    independent algorithm, the average over the 24 orderings of the four
    conditions of each condition's marginal gain in ``R^2``, from the stored
    ``r2_by_subset``. Tolerance 1e-12 absolute for both: R^2 values are O(1)
    and each share is a sum of 8 (or 24) weighted differences, round-off
    about 1e-15. Also the leave-one-out point equals ``R^2(F) - R^2(F
    without X)`` of the stored values (exact: the same subtraction).
    """
    _, rows, _ = profile_rows
    letters = ablation.CONDITIONS
    for target, entry in rows.items():
        r2 = entry["r2_by_subset"]
        assert len(r2) == 16
        shares = {x: entry["shapley"][x]["share"] for x in letters}
        assert abs(sum(shares.values()) - entry["r2_full_minus_empty"]) <= 1e-12
        assert abs(entry["shapley_sum"] - entry["r2_full_minus_empty"]) <= 1e-12

        def key(members: set[str]) -> str:
            return "".join(x for x in letters if x in members) or "none"

        for x in letters:
            gains = []
            for order in itertools.permutations(letters):
                before = set(order[: order.index(x)])
                gains.append(r2[key(before | {x})] - r2[key(before)])
            assert abs(np.mean(gains) - shares[x]) <= 1e-12, (target, x)
            loo = entry["leave_one_out"][x]["delta_r2"]
            assert loo == r2["ROIN"] - r2[key(set(letters) - {x})]


def test_horizon_rows_carry_censored_counts_and_the_uncensored_rule(
    profile_rows,
) -> None:
    """Every horizon row stores its censored and uncensored counts (M-5).

    Reference: the counts recomputed here, ``sum(t_test >= cap)`` with the
    fixture's cap (the 20% quantile of 200 test values, so 160 censored and
    40 uncensored), and the M-5 rule: fewer than 50 uncensored test states
    read "undetermined" with reason ``n_uncensored < 50``. The weight targets
    carry no count. Exact.
    """
    _, rows, t_test = profile_rows
    cap = float(np.quantile(t_test, 0.2))
    n_censored = int(np.sum(t_test >= cap))
    assert (n_censored, len(t_test) - n_censored) == (160, 40)
    horizon = rows["log_horizon"]
    assert (horizon["n_censored"], horizon["n_uncensored"]) == (160, 40)
    for kind in ("leave_one_out", "shapley"):
        for x in ablation.CONDITIONS:
            row = horizon[kind][x]
            assert (row["n_censored"], row["n_uncensored"]) == (160, 40)
            assert (row["reading"], row["reason"]) == (
                "undetermined",
                "n_uncensored < 50",
            )
    for target in ("logit_w_interior", "w_zero_indicator"):
        assert "n_censored" not in rows[target]
        assert "n_censored" not in rows[target]["leave_one_out"]["R"]
