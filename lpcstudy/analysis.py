"""Statistics behind each pre-registered hypothesis and secondary analyses.

The identifiers are the v3 ones of :mod:`lpcstudy.identifiers`: H1a-H1d, Q-N, H2a-H2e, H3a-H3c,
the reported gain bound, and the validation check V7.

Every function returns a plain ``dict`` (JSON-serializable) with the point
estimate, its block-bootstrap interval, the pre-registered threshold and a
``pass`` flag. Primary endpoints H2a, H2b and H3c use Bonferroni-adjusted
intervals at level ``1 - 0.05/3``; all others use 95% intervals.

The statistics of WU-0002.7 and .8 (H2b(ii), H2e, H3a, H3b, H3c) follow DEC-0008 A1 and A3 through
the shared helpers of :mod:`lpcstudy.statistics`: a result that cannot be computed, or whose
interval meets a band edge, is *inconclusive* and says why (``inconclusive_reason``); failed
bootstrap resamples are counted (``n_failed_resamples``) and widen the interval, never dropped.
Until WU-0002.9 adds the fail side (DEC-0011 O3), such a result carries ``pass`` and
``inconclusive_reason`` and no ``fail`` key: ``pass`` is False for both fail and inconclusive, and
``inconclusive_reason`` is not None only for an inconclusive result.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import rankdata
from sklearn.tree import DecisionTreeRegressor

from .allocation import deployable_profile
from .config import StudyConfig
from .data import make_rng, sklearn_seed
from .identifiers import check_keys
from .oracle import characteristic_horizon, curvature, hybrid_mse, oracle_weight
from .pipeline import Cell, FittedRules, RuleScores, SplitData
from .statistics import block_bootstrap, block_bootstrap_counted, bootstrap_values, \
    combine_verdicts, criterion_verdict, holm_adjust, kaplan_meier, logrank_parts, \
    logrank_test, ols_slope, partial_correlation, percentile_interval, spearman

PRIMARY_LEVEL = 1.0 - 0.05 / 3.0
PROFILE_NAMES = ("log_eps_tilde", "log_nu_tilde", "lambda_tilde", "log_noise_sens")
REDUNDANCY_MARGIN = 0.01
H2B_LIBRARY_SIZES = (1_000, 10_000)
"""Library sizes of H2b(ii): the paired change in w* from ``N_lib = 10^3`` to ``10^4``."""
H2E_NOISES = (0.01, 0.02)
"""Noise levels of H2e (both must pass)."""
H2E_LIBRARY_SIZES = (1_000, 100_000)
"""Library sizes of H2e: the change in error correlation from ``N_lib = 10^3`` to ``10^5``."""
H3B_LEAVES = 8
"""Fixed leaf count of the H3b trees (DEC-0008 A3, A4(e))."""
H3A_ALPHA = 0.01
"""H3a: every Holm-adjusted log-rank p must be below this (v3 section 2)."""
H3C_BOUND = 1.05
"""H3c: the upper bound of the MSE ratio must not exceed this (v3 section 2; closed)."""


def _boot(config: StudyConfig, stat, n_items: int, level: float = 0.95, salt: int = 0
          ) -> tuple[float, float, float]:
    return block_bootstrap(stat, n_items, config.bootstrap_resamples,
                           config.bootstrap_block, config.seed + salt, level)


# ------------------------------------------------------------------------ RQ1
def v7_efficiency(levels: np.ndarray, deltas: np.ndarray, nu: np.ndarray,
                  config: StudyConfig) -> dict:
    """V7: the estimator attains the Cramer-Rao scaling ``delta = rho nu`` at every ``rho``.

    Two checks, both on point medians over the sweep states (E0 verification check, decided like
    V2; the intervals are reported and enter neither flag):

    * the median over states of the per-state OLS slope of ``ln delta_i`` on ``ln rho`` lies in
      [0.9, 1.1] (v3 E0; DEC-0008 A2);
    * at **every** ``rho``, the median over states of ``delta_i / (rho nu_i)`` lies in
      [0.9, 1.1], each state with its own oracle ``nu_i`` (Methods v2 M2 section M10).

    A state with a non-finite or non-positive ``delta`` at any level, or a non-finite or
    non-positive ``nu_i``, is counted in ``n_nonfinite``, kept (never dropped), given NaN
    statistics so that the median is NaN, and makes ``pass`` false (PRIME.4).

    Parameters
    ----------
    levels : np.ndarray
        Noise levels ``rho``, shape ``(n_levels,)``, at least two distinct positive values.
    deltas : np.ndarray
        R.m.s. whitened estimation error ``delta_i(rho)``, shape ``(n_states, n_levels)``.
    nu : np.ndarray
        Per-state oracle ``nu_i`` (noise-free, the same states at every level), ``(n_states,)``.
    config : StudyConfig
        Study configuration (bootstrap settings).

    Returns
    -------
    dict
        ``median_slope`` with block-bootstrap interval ``ci`` (reported only), ``threshold``,
        ``slope_pass``; ``efficiency_median_by_noise``, its interval
        ``efficiency_ci_by_noise`` (reported only) and ``efficiency_pass_by_noise`` per level;
        ``n_states``, ``n_nonfinite`` and ``pass`` (slope and every level, bands closed).

    Raises
    ------
    ValueError
        If the shapes disagree or the levels are not at least two distinct positive values.
    """
    levels = np.asarray(levels, dtype=float)
    deltas = np.asarray(deltas, dtype=float)
    nu = np.asarray(nu, dtype=float)
    if levels.ndim != 1 or deltas.ndim != 2 or deltas.shape[1] != len(levels) \
            or nu.shape != (deltas.shape[0],):
        raise ValueError(f"V7 needs levels (L,), deltas (n, L), nu (n,); got {levels.shape}, "
                         f"{deltas.shape}, {nu.shape}")
    if len(np.unique(levels)) < 2 or not np.all(levels > 0):
        raise ValueError(f"V7 needs at least two distinct positive levels; got {levels}")
    low, high = 0.9, 1.1
    bad = ~np.all(np.isfinite(deltas) & (deltas > 0), axis=1) | ~(np.isfinite(nu) & (nu > 0))
    n_bad = int(bad.sum())
    safe_deltas = np.where(bad[:, None], np.nan, deltas)  # counted in n_nonfinite, fails pass
    safe_nu = np.where(bad, np.nan, nu)
    log_delta = np.log(safe_deltas)
    centered = np.log(levels) - np.log(levels).mean()
    slopes = (log_delta - log_delta.mean(axis=1, keepdims=True)) @ centered / \
        np.sum(centered**2)
    efficiency = safe_deltas / (levels[None, :] * safe_nu[:, None])
    nan_ci = (float("nan"), float("nan"))  # no bootstrap on NaN statistics (all-NaN quantile)
    est, lo, hi = (float(np.median(slopes)), *nan_ci) if n_bad else \
        _boot(config, lambda idx: float(np.median(slopes[idx])), len(slopes))
    out_eff, out_ci, out_pass = {}, {}, {}
    for i, rho in enumerate(levels):
        key = f"{rho:g}"
        out_eff[key] = float(np.median(efficiency[:, i]))
        out_ci[key] = list(nan_ci) if n_bad else list(_boot(
            config, lambda idx: float(np.median(efficiency[idx, i])), len(efficiency),
            salt=7000 + i)[1:])
        out_pass[key] = bool(low <= out_eff[key] <= high)
    slope_pass = bool(low <= est <= high)
    return {"median_slope": est, "ci": [lo, hi], "threshold": [low, high],
            "slope_pass": slope_pass, "efficiency_median_by_noise": out_eff,
            "efficiency_ci_by_noise": out_ci, "efficiency_pass_by_noise": out_pass,
            "n_states": int(len(nu)), "n_nonfinite": n_bad,
            "pass": bool(slope_pass and all(out_pass.values()) and n_bad == 0)}


def v7_noise_scaling(noise_cells: dict[float, Cell], config: StudyConfig) -> dict:
    """V7 on the cells of the noise sweep: extract the arrays, then :func:`v7_efficiency`.

    Parameters
    ----------
    noise_cells : dict[float, Cell]
        Cells of the noise sweep (test-sweep states, same states across levels).
    config : StudyConfig
        Study configuration.

    Returns
    -------
    dict
        The result of :func:`v7_efficiency` (levels sorted ascending).
    """
    levels = sorted(noise_cells)
    deltas = np.column_stack([noise_cells[r].splits["test"].moments.est_seed for r in levels])
    nu = noise_cells[levels[0]].oracles["test"].nu
    return v7_efficiency(np.array(levels), deltas, nu, config)


def _floor_power_law(log_n: np.ndarray, log_c2: float, exponent: float,
                     log_f2: float) -> np.ndarray:
    return np.log(np.exp(log_c2) * np.exp(log_n) ** (-exponent) + np.exp(log_f2))


def _fit_seed_law(sizes: np.ndarray, mean_sq: np.ndarray) -> tuple[float, float]:
    """Fit ``eps^2 = c^2 n_lib^{-2/d} + f^2``; return ``(2/d, f^2)``."""
    log_n = np.log(sizes)
    guess = (np.log(mean_sq[0]) + 2 * 0.5 * log_n[0], 1.0, np.log(mean_sq[-1] * 0.5))
    try:
        params, _ = curve_fit(_floor_power_law, log_n, np.log(mean_sq), p0=guess,
                              bounds=([-50, 0.01, -60], [50, 10.0, 10]), maxfev=20_000)
    except RuntimeError:
        return float("nan"), float("nan")
    return float(params[1]), float(np.exp(params[2]))


def h1a_library_scaling(library_cells: dict[tuple[float, int], Cell],
                        config: StudyConfig) -> dict:
    """H1a: ``eps_s^2 ~ c^2 n_lib^{-2/d} + f^2`` with ``1/d`` within 25% of Levina-Bickel.

    Parameters
    ----------
    library_cells : dict[tuple[float, int], Cell]
        Cells keyed by ``(rho, n_lib)``.
    config : StudyConfig
        Study configuration.

    Returns
    -------
    dict
        Fitted exponent per noise level, local-dimension reference, floors.
    """
    noises = sorted({k[0] for k in library_cells})
    sizes = np.array(sorted({k[1] for k in library_cells}), dtype=float)
    first = library_cells[(noises[0], int(sizes[0]))]
    d_ref = float(np.median(first.oracles["test"].local_dim))
    out: dict = {"local_dimension_median": d_ref, "by_noise": {}}
    floors = {}
    for rho in noises:
        sq = np.column_stack([library_cells[(rho, int(n))].splits["test"].moments.analog_seed**2
                              for n in sizes])
        stat = lambda idx: _fit_seed_law(sizes, sq[idx].mean(axis=0))[0]
        est, lo, hi = _boot(config, stat, len(sq), salt=int(1e4 * rho))
        two_over_d, floor_sq = _fit_seed_law(sizes, sq.mean(axis=0))
        floors[rho] = floor_sq
        rel = abs(two_over_d / 2.0 - 1.0 / d_ref) / (1.0 / d_ref)
        out["by_noise"][f"{rho:g}"] = {
            "fitted_inverse_dim": two_over_d / 2.0, "ci_inverse_dim": [lo / 2, hi / 2],
            "relative_error_vs_local_dim": rel, "floor_rms": float(np.sqrt(floor_sq)),
            "mean_seed_by_n_lib": {str(int(n)): float(np.sqrt(v))
                               for n, v in zip(sizes, sq.mean(axis=0))}}
    rel_ok = all(v["relative_error_vs_local_dim"] <= 0.25 for v in out["by_noise"].values())
    floor_ok = all(floors[b] > floors[a] for a, b in zip(noises[:-1], noises[1:])) \
        if len(noises) > 1 else True
    out.update({"threshold": "relative error <= 0.25; floor increasing in rho",
                "floor_increases": floor_ok, "pass": bool(rel_ok and floor_ok)})
    return out


def h1b_seed_amplifier(cell: Cell, config: StudyConfig) -> dict:
    """H1b: ``log rms(e_H)`` against ``log(g_H seed / sqrt(m))`` has unit slope at ``H_ref``.

    Parameters
    ----------
    cell : Cell
        Core cell.
    config : StudyConfig
        Study configuration.

    Returns
    -------
    dict
        Slopes and intervals for CP and PLP.
    """
    m = cell.splits["test"].moments
    o = cell.oracles["test"]
    col = m.at(config.reference_horizon)
    gain = o.gains[:, config.reference_horizon - 1]
    dim = cell.ctx.spec.dim
    copied = cell.noise**2 / cell.setup.n_analogs
    res = {}
    for name, seed, sq, floor in (("CP", m.analog_seed, m.sq_cp[:, col], copied),
                                  ("PLP", m.est_seed, m.sq_plp[:, col], 0.0)):
        x = np.log(gain * seed / np.sqrt(dim))
        y = 0.5 * np.log(np.maximum(sq - floor, 1e-12))
        est, lo, hi = _boot(config, lambda idx: ols_slope(x[idx], y[idx]), len(x))
        res[name] = {"slope": est, "ci": [lo, hi], "pass": bool(0.8 <= est <= 1.2)}
    res["threshold"] = [0.8, 1.2]
    res["pass"] = bool(res["CP"]["pass"] and res["PLP"]["pass"])
    return res


def h1c_horizon_law(cell: Cell, config: StudyConfig) -> dict:
    """H1c: state-wise slope of ``T`` against ``ln theta`` equals ``1 / Lambda_bar``.

    Parameters
    ----------
    cell : Cell
        Core cell.
    config : StudyConfig
        Study configuration.

    Returns
    -------
    dict
        Median of ``Lambda_bar x slope`` per forecaster (PLP is primary).
    """
    m = cell.splits["test"].moments
    growth = cell.oracles["test"].growth
    thetas = np.array(config.admissible_thresholds(cell.noise))
    res: dict = {"thresholds": thetas.tolist()}
    for name, mse in (("PLP", m.sq_plp), ("CP", m.sq_cp)):
        horizons = np.column_stack([characteristic_horizon(mse, m.horizons, cell.noise, t)[0]
                                    for t in thetas])
        events = np.column_stack([characteristic_horizon(mse, m.horizons, cell.noise, t)[1]
                                  for t in thetas])
        ratios = []
        for i in range(len(horizons)):
            ok = events[i] & (horizons[i] > 1)
            if ok.sum() >= 3 and growth[i] > 0 and np.ptp(horizons[i][ok]) > 0:
                ratios.append(growth[i] * ols_slope(np.log(thetas[ok]),
                                                    horizons[i][ok].astype(float)))
        ratios = np.asarray(ratios)
        if ratios.size < 10:
            res[name] = {"n_states": int(ratios.size), "pass": False}
            continue
        est, lo, hi = _boot(config, lambda idx: float(np.median(ratios[idx])), len(ratios))
        res[name] = {"median_ratio": est, "ci": [lo, hi], "n_states": int(ratios.size),
                     "pass": bool(0.8 <= est <= 1.25)}
    res["threshold"] = [0.8, 1.25]
    res["pass"] = bool(res["PLP"].get("pass", False))
    return res


def h1d_proxies(cell: Cell, rules: FittedRules, config: StudyConfig) -> dict:
    """H1d: Spearman correlation of each deployable proxy with its oracle >= 0.7.

    Parameters
    ----------
    cell : Cell
        Core cell.
    rules : FittedRules
        Fitted rules (seed proxies).
    config : StudyConfig
        Study configuration.

    Returns
    -------
    dict
        Spearman correlations (first evaluation draw).
    """
    split = cell.splits["test"]
    ev, m, o = split.evals, split.moments, cell.oracles["test"]
    eps_hat, delta_hat = rules.proxies.seeds(ev, cell.noise)
    corr = {"analog_seed": spearman(eps_hat[:, 0], m.analog_seed),
            "estimation_seed": spearman(delta_hat[:, 0], m.est_seed),
            "growth": spearman(ev.growth_proxy[:, 0], o.growth),
            "noise_sensitivity": spearman(ev.noise_sens[:, 0], m.noise_sens),
            "estimation_seed_vs_cramer_rao": spearman(m.est_seed, cell.noise * o.nu)}
    passed = all(corr[k] >= 0.7 for k in ("analog_seed", "estimation_seed", "growth",
                                          "noise_sensitivity"))
    return {"spearman": corr, "threshold": 0.7, "pass": bool(passed)}


def _oracle_profile(cell: Cell, split: str, config: StudyConfig) -> np.ndarray:
    """Oracle four-coordinate profile of a split (state level)."""
    from .allocation import NOISE_SENS_FLOOR

    m, o = cell.splits[split].moments, cell.oracles[split]
    return np.column_stack([np.log(m.analog_seed / cell.noise), np.log(m.est_seed / cell.noise),
                            o.growth * config.steps_per_lyapunov,
                            np.log(m.noise_sens + NOISE_SENS_FLOOR)])


def qn_noise_redundancy(cell: Cell, rules: FittedRules, config: StudyConfig) -> dict:
    """Q-N: is the fourth LPC (noise sensitivity) reducible to the other three?

    Nested out-of-sample comparison. Gradient-boosted regressors are trained on
    the construction and calibration states with the first three profile
    coordinates (F3) or all four (F4), for two targets: ``logit w*(H_ref)`` and the
    log state horizon. The statistic is ``Delta R^2 = R^2(F4) - R^2(F3)`` on the
    test states, with a block-bootstrap interval. Pre-registered reading (margin
    0.01):

    * ``redundant`` (FW Remark 1 prediction; pass): both upper bounds < margin;
    * ``adds information``: either lower bound > margin;
    * ``inconclusive``: otherwise.

    Run on the deployable profile (primary) and on the oracle profile.

    Parameters
    ----------
    cell : Cell
        Core cell.
    rules : FittedRules
        Fitted rules (seed proxies for the deployable profile).
    config : StudyConfig
        Study configuration.

    Returns
    -------
    dict
        R^2 values, Delta R^2 with intervals, verdicts, and how well N is
        predicted from the other three coordinates.
    """
    from sklearn.ensemble import HistGradientBoostingRegressor

    from .allocation import state_horizon_target

    col = config.reference_horizon - 1
    lt = config.steps_per_lyapunov

    def targets(split: str) -> dict[str, np.ndarray]:
        m = cell.splits[split].moments
        w = np.clip(oracle_weight(m)[:, col], 0.01, 0.99)
        t = state_horizon_target(m, cell.noise, config.primary_threshold)
        return {"logit_w": np.log(w / (1 - w)), "log_horizon": np.log(t)}

    def profiles(kind: str, split: str) -> np.ndarray:
        if kind == "oracle":
            return _oracle_profile(cell, split, config)
        ev = cell.splits[split].evals
        return deployable_profile(ev, rules.proxies, cell.noise, lt)[:, 0, :]

    def model() -> HistGradientBoostingRegressor:
        return HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05,
                                             max_leaf_nodes=15, min_samples_leaf=20,
                                             l2_regularization=1.0,
                                             random_state=sklearn_seed(config.seed,
                                                                       "qn-regressor"))

    def r2(y: np.ndarray, pred: np.ndarray, idx: np.ndarray) -> float:
        resid = np.sum((y[idx] - pred[idx]) ** 2)
        total = np.sum((y[idx] - y[idx].mean()) ** 2)
        return float(1.0 - resid / total)

    train_splits = ("construction", "calibration")
    y_train = {k: np.concatenate([targets(s)[k] for s in train_splits])
               for k in ("logit_w", "log_horizon")}
    y_test = targets("test")
    out: dict = {"margin": REDUNDANCY_MARGIN}
    for kind in ("deployable", "oracle"):
        x_train = np.concatenate([profiles(kind, s) for s in train_splits])
        x_test = profiles(kind, "test")
        res_kind: dict = {}
        verdicts = []
        for name in ("logit_w", "log_horizon"):
            pred3 = model().fit(x_train[:, :3], y_train[name]).predict(x_test[:, :3])
            pred4 = model().fit(x_train, y_train[name]).predict(x_test)
            y = y_test[name]
            stat = lambda idx: r2(y, pred4, idx) - r2(y, pred3, idx)
            est, lo, hi = _boot(config, stat, len(y), salt=11)
            full = np.arange(len(y))
            res_kind[name] = {"r2_three": r2(y, pred3, full), "r2_four": r2(y, pred4, full),
                              "delta_r2": est, "ci": [lo, hi]}
            verdicts.append((lo, hi))
        if all(hi < REDUNDANCY_MARGIN for _, hi in verdicts):
            verdict = "redundant"
        elif any(lo > REDUNDANCY_MARGIN for lo, _ in verdicts):
            verdict = "adds information"
        else:
            verdict = "inconclusive"
        n_pred = model().fit(x_train[:, :3], x_train[:, 3]).predict(x_test[:, :3])
        res_kind["noise_sens_r2_from_three"] = r2(x_test[:, 3], n_pred, np.arange(len(x_test)))
        res_kind["verdict"] = verdict
        out[kind] = res_kind
    out["threshold"] = ("redundant if Delta R^2 upper bound < 0.01 for both targets "
                        "(deployable profile)")
    out["pass"] = bool(out["deployable"]["verdict"] == "redundant")
    return out


# ------------------------------------------------------------------------ RQ2
def h2a_separation(cell: Cell, config: StudyConfig) -> dict:
    """H2a (primary): beyond 1 LT the weight depends on the seed ratio, not on instability.

    Parameters
    ----------
    cell : Cell
        Core cell.
    config : StudyConfig
        Study configuration.

    Returns
    -------
    dict
        Median range of ``w*`` over ``H in {1, 2, 4}`` LT and partial correlation of
        ``logit w*(H_ref)`` with ``Lambda_tilde`` given the log seed ratios.
    """
    m = cell.splits["test"].moments
    o = cell.oracles["test"]
    lt = config.steps_per_lyapunov
    w_star = oracle_weight(m)
    cols = [m.at(int(h * lt)) for h in config.eval_horizons_lyapunov if h >= 1.0]
    # Small-error regime (FW assumption A6): both forecasters' r.m.s. errors below
    # config.linear_regime_rms; a state needs >= 2 such horizons to have a range.
    small = (np.sqrt(m.sq_cp[:, cols]) <= config.linear_regime_rms) & \
        (np.sqrt(m.sq_plp[:, cols]) <= config.linear_regime_rms)
    eligible = small.sum(axis=1) >= 2
    masked = np.where(small, w_star[:, cols], np.nan)
    ranges = (np.nanmax(masked, axis=1) - np.nanmin(masked, axis=1))[eligible]
    if ranges.size == 0:
        ranges = np.array([np.nan])
    est_r, lo_r, hi_r = _boot(config, lambda idx: float(np.median(ranges[idx])),
                              len(ranges), PRIMARY_LEVEL, salt=1)
    unrestricted = np.ptp(w_star[:, cols], axis=1)
    w_ref = np.clip(w_star[:, m.at(config.reference_horizon)], 0.01, 0.99)
    logit = np.log(w_ref / (1 - w_ref))
    controls = np.column_stack([np.log(m.analog_seed / cell.noise),
                                np.log(m.est_seed / cell.noise)])
    lam = o.growth * lt
    stat = lambda idx: partial_correlation(logit[idx], lam[idx], controls[idx])
    est_p, lo_p, hi_p = _boot(config, stat, len(logit), PRIMARY_LEVEL, salt=2)
    raw = spearman(w_ref, lam)
    passed = hi_r < 0.1 and max(abs(lo_p), abs(hi_p)) < 0.1
    return {"median_range": est_r, "range_ci": [lo_r, hi_r],
            "n_eligible_states": int(eligible.sum()),
            "median_range_unrestricted": float(np.median(unrestricted)),
            "partial_corr": est_p, "partial_ci": [lo_p, hi_p],
            "unconditional_spearman_w_lambda": raw,
            "short_horizon_range_median": float(np.median(np.ptp(
                w_star[:, [m.at(int(h * lt)) for h in config.eval_horizons_lyapunov]],
                axis=1))),
            "threshold": "upper CI of median range (small-error regime) < 0.1 and "
                         "|partial r| CI within 0.1",
            "pass": bool(passed)}


def _per_state_spearman(levels: np.ndarray, values: np.ndarray) -> np.ndarray:
    """Spearman correlation of each row of ``values`` with ``levels``.

    Ties (e.g. weights clipped to 0 at several levels) receive average ranks, so
    a state whose weight does not change across levels scores 0, not +1.
    """
    ranks = rankdata(values, axis=1)
    lev = rankdata(levels)
    lev_c = lev - lev.mean()
    ranks_c = ranks - ranks.mean(axis=1, keepdims=True)
    denom = np.sqrt(np.sum(ranks_c**2, axis=1) * np.sum(lev_c**2))
    return np.where(denom > 0, ranks_c @ lev_c / np.maximum(denom, 1e-300), 0.0)


def _decision(verdict: str, reason: str | None) -> dict:
    """The ``pass`` and ``inconclusive_reason`` keys of a result (no ``fail`` key until WU-0002.9).

    ``pass`` is True only for a pass; ``inconclusive_reason`` is the reason given by
    ``criterion_verdict`` for an inconclusive result and None for a pass or a fail.
    """
    return {"pass": verdict == "pass", "inconclusive_reason": reason}


def _combined_decision(parts: dict[str, tuple[str, str | None]]) -> dict:
    """``pass`` and ``inconclusive_reason`` of a criterion with several named parts.

    The verdict is ``combine_verdicts`` of the parts (v3 section 7: all must pass; one fail
    fails it). The reason lists the inconclusive parts, and is None unless the combination is
    inconclusive.
    """
    verdict = combine_verdicts(v for v, _ in parts.values())
    reason = "; ".join(f"{name}: {why}" for name, (v, why) in parts.items()
                       if v == "inconclusive") if verdict == "inconclusive" else None
    return _decision(verdict, reason)


def _split_weights(cell: Cell, config: StudyConfig) -> np.ndarray:
    """``w*(H_ref)`` of the test-sweep states of a cell."""
    m = cell.splits["test"].moments
    return oracle_weight(m)[:, m.at(config.reference_horizon)]


def _missing_cells(cells: dict, wanted: list[tuple[float, int]]) -> list[str]:
    """Names of the (rho, n_lib) cells of ``wanted`` that are not in ``cells``."""
    return [f"rho={rho:g} n_lib={n}" for rho, n in wanted if (rho, n) not in cells]


def _paired_change(low: np.ndarray, high: np.ndarray, config: StudyConfig, level: float,
                   labels: tuple[str, ...], name: str, statistic: str = "mean"
                   ) -> tuple[dict, str, str | None]:
    """Bootstrap interval of the mean or median of per-state paired differences ``high - low``.

    One index array (the moving-block resample of states) serves both cells, and the
    generator is ``make_rng(config.seed, *labels)`` (DEC-0012). Failed (non-finite)
    resamples are counted at the unfavourable tail (DEC-0008 A3).

    Returns
    -------
    tuple[dict, str, str | None]
        ``{<name>, ci, level, n_states, n_failed_resamples, n_zero_difference}``, then the
        verdict and the reason of the criterion "lower bound > 0" (strict, DEC-0008 A1) from
        ``criterion_verdict``.
    """
    if low.shape != high.shape or low.ndim != 1:
        raise ValueError(f"paired cells must hold the same states; got {low.shape}, {high.shape}")
    diff = high - low
    centre = np.mean if statistic == "mean" else np.median
    boot = block_bootstrap_counted(lambda idx: float(centre(diff[idx])), len(diff),
                                   config.bootstrap_resamples, config.bootstrap_block,
                                   make_rng(config.seed, *labels), level)
    verdict, reason = criterion_verdict(boot.estimate, boot.lower, boot.upper, (0.0, np.inf),
                                        (False, True), n_states=len(diff))
    out = {name: boot.estimate, "ci": [boot.lower, boot.upper], "level": level,
           "n_states": int(len(diff)), "n_failed_resamples": boot.n_failed,
           "n_zero_difference": int(np.count_nonzero(diff == 0.0))}
    return out, verdict, reason


def _unavailable(level: float, missing: list[str], name: str) -> tuple[dict, str, str]:
    """A paired change that cannot be computed: no value, no NaN (PRIME.4), inconclusive."""
    return ({name: None, "ci": None, "level": level, "n_states": None,
             "n_failed_resamples": None, "n_zero_difference": None},
            "inconclusive", "missing cell(s): " + ", ".join(missing))


def h2b_knob_response(noise_cells: dict[float, Cell],
                      library_cells: dict[tuple[float, int], Cell],
                      config: StudyConfig) -> dict:
    """H2b (primary): ``w*`` rises with the noise level and with the library size.

    * (i) ``noise``: the mean over states of the per-state Spearman correlation of ``w*(H_ref)``
      with ``rho``; the interval is at level ``1 - 0.05/3``, pass iff its lower bound is above 0.
    * (ii) ``library_change``: the mean over states of ``w*_i(H_ref, 10^4) - w*_i(H_ref, 10^3)``
      at ``rho = config.core_noise`` (1%), one block-bootstrap index array for both sizes, level
      ``1 - 0.05/3``, pass iff the lower bound is above 0 (strict; DEC-0008 A1). A missing cell
      gives ``mean_change = None``, ``pass = False`` and the missing cells in
      ``inconclusive_reason``; an interval with the lower bound at or below 0, or with failed
      resamples at or above the threshold, is inconclusive (DEC-0008 A3).
    * ``pass`` = (i) and (ii) (v3 section 2).

    Reported only, at 95% (v3 section 7, Methods v2 M2 section M12): ``library_curves``, the mean
    and the median of ``w*(H_ref)`` with intervals for every ``n_lib`` at every
    ``rho`` of the library sweep (the M2 curve; all sizes share each resample), and
    ``library_change_reported``, the 10^3 to 10^4 change at every other ``rho`` of the sweep
    (``0.02``). The per-``rho`` library Spearman and the saturation rule of v1
    (``median_at_largest_n_lib < 0.95``) are gone (D-05; M2 section M14).

    Parameters
    ----------
    noise_cells : dict[float, Cell]
        Noise sweep at the core library size.
    library_cells : dict[tuple[float, int], Cell]
        Library sweep, keyed ``(rho, n_lib)``.
    config : StudyConfig
        Study configuration.

    Returns
    -------
    dict
        ``noise``, ``library_change``, ``library_curves``, ``library_change_reported``,
        ``threshold``, ``pass`` and ``inconclusive_reason`` (the reason of part (ii)).
    """
    res: dict = {}
    rho_levels = np.array(sorted(noise_cells))
    w_rho = np.column_stack([_split_weights(noise_cells[r], config) for r in rho_levels])
    rho_corr = _per_state_spearman(rho_levels, w_rho)
    est, lo, hi = _boot(config, lambda idx: float(np.mean(rho_corr[idx])), len(rho_corr),
                        PRIMARY_LEVEL, salt=3)
    medians = np.median(w_rho, axis=0)
    res["noise"] = {"median_w_by_noise": dict(zip(map(str, rho_levels), medians.tolist())),
                    "mean_state_spearman": est, "ci": [lo, hi],
                    "monotone_medians": bool(np.all(np.diff(medians) > 0)),
                    "pass": bool(lo > 0)}

    rho = config.core_noise
    wanted = [(rho, n) for n in H2B_LIBRARY_SIZES]
    missing = _missing_cells(library_cells, wanted)
    fields, verdict, reason = _unavailable(PRIMARY_LEVEL, missing, "mean_change") if missing \
        else _paired_change(*(_split_weights(library_cells[key], config) for key in wanted),
                            config, PRIMARY_LEVEL, ("h2b-library-change", f"{rho:g}"),
                            "mean_change")
    res["library_change"] = {**fields, "rho": rho, "n_lib": list(H2B_LIBRARY_SIZES),
                             **_decision(verdict, reason)}

    res["library_curves"] = {}
    res["library_change_reported"] = {}
    for other in sorted({k[0] for k in library_cells}):
        sizes = sorted(n for r, n in library_cells if r == other)
        weights = np.column_stack([_split_weights(library_cells[(other, n)], config)
                                   for n in sizes])
        n_sizes = len(sizes)
        _, values = bootstrap_values(
            lambda idx: np.concatenate([weights[idx].mean(axis=0),
                                        np.median(weights[idx], axis=0)]),
            len(weights), config.bootstrap_resamples, config.bootstrap_block,
            make_rng(config.seed, "h2b-curves", f"{other:g}"))
        curve = {}
        for j, n in enumerate(sizes):
            mean_lo, mean_hi, mean_failed = percentile_interval(values[:, j], 0.95)
            med_lo, med_hi, med_failed = percentile_interval(values[:, n_sizes + j], 0.95)
            curve[str(n)] = {
                "mean": float(weights[:, j].mean()), "mean_ci": [mean_lo, mean_hi],
                "median": float(np.median(weights[:, j])), "median_ci": [med_lo, med_hi],
                "level": 0.95, "n_states": int(len(weights)),
                "n_failed_resamples": {"mean": mean_failed, "median": med_failed}}
        res["library_curves"][f"{other:g}"] = curve
        if other != rho:
            pair = [(other, n) for n in H2B_LIBRARY_SIZES]
            gone = _missing_cells(library_cells, pair)
            fields, _, _ = _unavailable(0.95, gone, "mean_change") if gone else _paired_change(
                *(_split_weights(library_cells[key], config) for key in pair), config, 0.95,
                ("h2b-library-change", f"{other:g}"), "mean_change")
            res["library_change_reported"][f"{other:g}"] = {
                **fields, "role": "reported", "unavailable_reason": (
                    "missing cell(s): " + ", ".join(gone)) if gone else None}
    res["threshold"] = ("(i) per-state Spearman of w* with rho: CI lower bound > 0; (ii) mean "
                        "paired change in w*(H_ref) from n_lib 10^3 to 10^4 at rho = 1%: CI lower "
                        "bound > 0 (both at level 1 - 0.05/3)")
    res["pass"] = bool(res["noise"]["pass"] and res["library_change"]["pass"])
    res["inconclusive_reason"] = res["library_change"]["inconclusive_reason"]
    return res


def h2e_noise_matching(library_cells: dict[tuple[float, int], Cell], config: StudyConfig
                       ) -> dict:
    """H2e: the median per-state change in the CP-PLP error correlation, ``N_lib`` 10^3 to 10^5.

    The per-state correlation ``r_i(rho, n_lib)`` is the correlation over the oracle noise draws of
    the CP and PLP errors at ``H_ref`` (``ensemble.draw_correlation``; two-pass Pearson). The
    statistic at each ``rho`` of ``H2E_NOISES`` is the median over states of
    ``r_i(rho, 10^5) - r_i(rho, 10^3)`` with a 95% block-bootstrap interval (one index array);
    ``pass`` needs the lower bound above 0 (strict) at both 1% and 2%. A state whose CP or PLP
    error is constant over the draws has correlation exactly 0 in both cells (DEC-0011 O2,
    Methods v2 section M11); the counts of such states per cell (``zero_variance_corr``, split into
    CP-constant, PLP-constant and both) and of states whose change is exactly 0
    (``n_zero_difference``) are reported. A median with an atom at 0 can put the lower bound at
    exactly 0, which is inconclusive; that is intended. Any cell missing for a ``rho``
    (the smoke preset has neither 10^5 nor 2%) gives ``median_change = None`` and a reason
    naming it; no NaN is invented. Non-finite correlations are not dropped: they make the
    estimate or a resample non-finite, so they are counted and widen the interval.

    Parameters
    ----------
    library_cells : dict[tuple[float, int], Cell]
        Library sweep, keyed ``(rho, n_lib)`` (cells with ``err_corr``).
    config : StudyConfig
        Study configuration.

    Returns
    -------
    dict
        ``by_noise`` (per ``rho``: ``median_change``, ``ci``, ``level``, ``n_states``,
        ``n_failed_resamples``, ``n_zero_difference``, ``pass``, ``inconclusive_reason``),
        ``corr_curve[rho][n_lib]`` (median correlation for every available cell),
        ``zero_variance_corr[rho][n_lib]``, ``threshold``, ``pass``, ``inconclusive_reason``.

    Raises
    ------
    ValueError
        If a cell's moments carry no ``err_corr``.
    """
    ref = config.reference_horizon
    corr: dict[tuple[float, int], np.ndarray] = {}
    out: dict = {"corr_curve": {}, "zero_variance_corr": {}}
    for rho, n in sorted(library_cells):
        cell = library_cells[(rho, n)]
        m = cell.splits["test"].moments
        if m.err_corr is None or m.cp_constant is None or m.plp_constant is None:
            raise ValueError(f"cell (rho={rho:g}, n_lib={n}) has no err_corr; H2e needs moments "
                             "from ensemble_moments")
        col = m.at(ref)
        corr[(rho, n)] = m.err_corr[:, col]
        cp_const, plp_const = m.cp_constant[:, col], m.plp_constant[:, col]
        out["corr_curve"].setdefault(f"{rho:g}", {})[str(n)] = float(np.median(corr[(rho, n)]))
        out["zero_variance_corr"].setdefault(f"{rho:g}", {})[str(n)] = {
            "cp_constant": int(cp_const.sum()), "plp_constant": int(plp_const.sum()),
            "both_constant": int((cp_const & plp_const).sum()),
            "n_nonfinite": int((~np.isfinite(corr[(rho, n)])).sum()),
            "n_states": int(len(cp_const))}
    parts: dict[str, tuple[str, str | None]] = {}
    by_noise: dict = {}
    for rho in H2E_NOISES:
        wanted = [(rho, n) for n in H2E_LIBRARY_SIZES]
        missing = _missing_cells(library_cells, wanted)
        fields, verdict, reason = _unavailable(0.95, missing, "median_change") if missing \
            else _paired_change(corr[wanted[0]], corr[wanted[1]], config, 0.95,
                                ("h2e", f"{rho:g}"), "median_change", "median")
        by_noise[f"{rho:g}"] = {**fields, **_decision(verdict, reason)}
        parts[f"rho={rho:g}"] = (verdict, reason)
    out["by_noise"] = by_noise
    out["threshold"] = ("median per-state change in CP-PLP error correlation at H_ref, n_lib 10^3 "
                        "to 10^5: 95% CI lower bound > 0 at rho = 1% and 2%")
    out.update(_combined_decision(parts))
    return out


def h2c_state_dependence(scores: dict[str, RuleScores], calibration: SplitData,
                         config: StudyConfig) -> dict:
    """H2c: A4 has lower MSE at ``H_ref`` than A2 and than the better single forecaster.

    The better single forecaster is chosen on the calibration split, not on the test data that
    the differences are computed on (DEC-0008 A4(i)): the realized MSE at ``H_ref`` of A0 (CP
    alone) and A1 (PLP alone) on the calibration split's evaluation draws, against the
    noise-free truth, the same definition as on test; a tie goes to A0. The two values are
    reported as ``calibration_mse``. The entry ``A4o_minus_A2`` (A4 with the oracle seeds against
    A2; reported only, no pass; D-20) is the paired mean difference of the per-state squared
    errors at ``H_ref``, 95%, on the same states and the same resamples (salt 5) as the other
    differences.

    Parameters
    ----------
    scores : dict[str, RuleScores]
        Test-split scores.
    calibration : SplitData
        Calibration split of the core cell, with evaluation draws (only ``evals.cp_err`` and
        ``evals.plp_err`` at ``H_ref`` are read).
    config : StudyConfig
        Study configuration.

    Returns
    -------
    dict
        ``best_single``, ``calibration_mse``, the mean paired differences with intervals
        (``A4_minus_A2``, ``A4_minus_<best>`` with ``pass``; ``A4o_minus_A2`` reported only), and
        ``pass``.

    Raises
    ------
    ValueError
        If the calibration split has no evaluation draws, lacks ``H_ref``, or a calibration MSE
        is not finite.
    """
    evals = calibration.evals
    if evals is None or config.reference_horizon not in evals.horizons:
        raise ValueError("H2c needs calibration evaluation draws that include H_ref")
    col = int(np.nonzero(evals.horizons == config.reference_horizon)[0][0])
    calibration_mse = {"A0": float(np.mean(evals.cp_err[:, :, col] ** 2)),
                       "A1": float(np.mean(evals.plp_err[:, :, col] ** 2))}
    if not all(np.isfinite(v) for v in calibration_mse.values()):
        raise ValueError(f"calibration MSE at H_ref is not finite: {calibration_mse}")
    a4 = scores["A4"].state_mse_ref
    best_single = "A0" if calibration_mse["A0"] <= calibration_mse["A1"] else "A1"
    out = {"best_single": best_single, "calibration_mse": calibration_mse}
    for other in ("A2", best_single):
        diff = a4 - scores[other].state_mse_ref
        est, lo, hi = _boot(config, lambda idx: float(np.mean(diff[idx])), len(diff), salt=5)
        out[f"A4_minus_{other}"] = {"mean": est, "ci": [lo, hi],
                                    "relative": est / float(scores[other].state_mse_ref.mean()),
                                    "pass": bool(hi < 0)}
    out["pass"] = bool(out["A4_minus_A2"]["pass"] and out[f"A4_minus_{best_single}"]["pass"])
    diff_o = scores["A4o"].state_mse_ref - scores["A2"].state_mse_ref
    est, lo, hi = _boot(config, lambda idx: float(np.mean(diff_o[idx])), len(diff_o), salt=5)
    out["A4o_minus_A2"] = {"mean": est, "ci": [lo, hi], "level": 0.95,
                           "relative": est / float(scores["A2"].state_mse_ref.mean()),
                           "role": "reported"}
    return out


def h2d_empirical_comparison(scores: dict[str, RuleScores], config: StudyConfig) -> dict:
    """H2d: A4 within 10% of A3 in-distribution (part (ii) is removed in v3).

    Parameters
    ----------
    scores : dict[str, RuleScores]
        Core test scores.
    config : StudyConfig
        Study configuration.

    Returns
    -------
    dict
        In-distribution excess of A4 over A3 with its interval, and the pass flags.
    """
    a3, a4 = scores["A3"].state_mse_ref, scores["A4"].state_mse_ref
    stat = lambda idx: float(a4[idx].mean() / a3[idx].mean() - 1.0)
    est, lo, hi = _boot(config, stat, len(a3), salt=6)
    in_dist_ok = est <= 0.10
    return {"in_distribution_excess": est, "ci": [lo, hi], "in_distribution_pass":
            bool(in_dist_ok), "pass": bool(in_dist_ok)}


def gain_horizon_bound(cell: Cell, config: StudyConfig) -> dict:
    """Gain bound: hybrid horizon gain over the better forecaster <= ``ln 2 / (2 Lambda_bar)``.

    Evaluated on states with positive growth, uncensored single-forecaster
    horizons and nonnegative error covariance at the better forecaster's crossing.

    Parameters
    ----------
    cell : Cell
        Core cell.
    config : StudyConfig
        Study configuration.

    Returns
    -------
    dict
        Fraction of states within the bound (+1 step discretization tolerance).
    """
    m = cell.splits["test"].moments
    growth = cell.oracles["test"].growth
    theta = config.primary_threshold
    t_cp, ev_cp = characteristic_horizon(m.sq_cp, m.horizons, cell.noise, theta)
    t_plp, ev_plp = characteristic_horizon(m.sq_plp, m.horizons, cell.noise, theta)
    t_hyb, _ = characteristic_horizon(hybrid_mse(m, oracle_weight(m)), m.horizons,
                                      cell.noise, theta)
    better = np.maximum(t_cp, t_plp)
    col = np.clip(better - 1, 0, len(m.horizons) - 1)
    rows = np.arange(len(better))
    cov = m.cross[rows, col] - m.mean_cp[rows, col] * m.mean_plp[rows, col]
    ok = (growth > 0) & ev_cp & ev_plp & (cov >= 0)
    gain = (t_hyb - better)[ok]
    bound = np.log(2.0) / (2.0 * growth[ok])
    within = gain <= bound + 1.0
    frac = float(within.mean()) if within.size else float("nan")
    return {"fraction_within_bound": frac, "n_states": int(ok.sum()),
            "median_gain_lyapunov": float(np.median(gain)) / config.steps_per_lyapunov
            if gain.size else float("nan"),
            "max_gain_lyapunov": float(np.max(gain)) / config.steps_per_lyapunov
            if gain.size else float("nan"),
            "threshold": 0.9, "pass": bool(frac >= 0.9)}


# ------------------------------------------------------------------------ RQ3
def _finite_or_none(value: float) -> float | None:
    """``value`` as a float, or None if it is not finite (a degenerate fit is not a number)."""
    return float(value) if np.isfinite(value) else None


def h3a_logrank(first_regime: np.ndarray, durations: np.ndarray, events: np.ndarray,
                horizons_km: np.ndarray, horizon_target: np.ndarray, lt: int,
                chosen_k: int) -> dict:
    """H3a: Holm-adjusted log-rank tests between consecutive regimes, all adjusted p < 0.01.

    One observation per state, the first evaluation draw (DEC-0008 A4(f)): the caller passes the
    first-draw regime, realized horizon and event flag, so the test does not treat repeated
    draws of a state as independent. The regimes are ordered by their Kaplan-Meier median
    horizon (NaN, a median not reached, last) with ``np.argsort(kind="stable")``, so a tie
    is ordered by regime index and the pairs do not depend on the CPU (DEF-0013). The family is
    all ``K_real - 1`` consecutive pairs. A pair with an empty regime or with zero log-rank
    variance (``logrank_parts``) is not computed: its raw p is ``None`` and it enters the Holm
    family at p = 1 (conservative; DEC-0011 O1). No minimum number of states per regime is
    imposed (DEC-0011 O1). ``pass`` needs every pair computed and every adjusted p < 0.01
    (strict). No equivalence margin is set, so H3a cannot fail (DEC-0008 A3): anything else is
    inconclusive, with the reason. With fewer than two regimes there is no pair and the result
    is inconclusive.

    Parameters
    ----------
    first_regime : np.ndarray
        Regime index of each test state at the first evaluation draw, ``(n,)``.
    durations, events : np.ndarray
        Realized horizon (steps) and event flag of the A5 rule at that draw, ``(n,)``.
    horizons_km : np.ndarray
        Kaplan-Meier median horizon of each regime (steps), ``(K_real,)``.
    horizon_target : np.ndarray
        Characteristic horizon of each state (steps), ``(n,)``, for the reported spread.
    lt : int
        Steps per Lyapunov time.
    chosen_k : int
        The regime count chosen by the K rule.

    Returns
    -------
    dict
        ``chosen_K``, ``pairs`` (regime indices, in test order), ``logrank_p_raw`` (None where
        not computed), ``logrank_p_holm``, ``n_per_regime``, ``iqr_lt`` (interquartile range of
        the characteristic horizon in Lyapunov times per regime, None below 2 states),
        ``iqr_lt_mean`` (their mean weighted by regime size, the v1 ``mean_iqr_lyapunov``; None
        if no regime has 2 states), ``threshold``, ``pass``, ``inconclusive_reason``.
    """
    n_regimes = len(horizons_km)
    counts = [int(np.sum(first_regime == k)) for k in range(n_regimes)]
    iqr: list[float | None] = []
    for k in range(n_regimes):
        members = first_regime == k
        if members.sum() >= 2:
            q75, q25 = np.percentile(horizon_target[members] / lt, [75, 25])
            iqr.append(float(q75 - q25))
        else:
            iqr.append(None)
    spread = [(v, c) for v, c in zip(iqr, counts) if v is not None]
    iqr_mean = float(np.average([v for v, _ in spread], weights=[c for _, c in spread])) \
        if spread else None

    order = np.argsort(np.nan_to_num(horizons_km, nan=np.inf), kind="stable")
    pairs = [(int(a), int(b)) for a, b in zip(order[:-1], order[1:])]
    raw: list[float | None] = []
    why: list[str] = []
    for a, b in pairs:
        in_a, in_b = first_regime == a, first_regime == b
        if not (in_a.any() and in_b.any()):
            raw.append(None)
            why.append(f"pair ({a}, {b}): empty regime")
        elif logrank_parts(durations[in_a], events[in_a], durations[in_b], events[in_b])[1] <= 0:
            raw.append(None)
            why.append(f"pair ({a}, {b}): zero log-rank variance")
        else:
            raw.append(logrank_test(durations[in_a], events[in_a], durations[in_b], events[in_b]))
    adjusted = holm_adjust([1.0 if p is None else p for p in raw]) if pairs else []
    decided = bool(pairs) and not why
    if decided and max(adjusted) < H3A_ALPHA:
        verdict, reason = "pass", None
    elif not pairs:
        verdict, reason = "inconclusive", "fewer than two regimes: no pair to test"
    elif why:
        verdict, reason = "inconclusive", "; ".join(why)
    else:
        verdict, reason = "inconclusive", (f"largest Holm-adjusted p {max(adjusted):.3g} "
                                           f">= {H3A_ALPHA}")
    return {"chosen_K": chosen_k, "pairs": [list(pair) for pair in pairs],
            "logrank_p_raw": raw, "logrank_p_holm": adjusted, "n_per_regime": counts,
            "iqr_lt": iqr, "iqr_lt_mean": iqr_mean,
            "threshold": f"all Holm-adjusted log-rank p between consecutive regimes < {H3A_ALPHA}",
            **_decision(verdict, reason)}


def _h3b_trees(seed: int) -> tuple[DecisionTreeRegressor, DecisionTreeRegressor]:
    """The weight tree and the horizon tree of H3b: ``max_leaf_nodes = 8`` (DEC-0008 A3, A4(e))."""
    return (DecisionTreeRegressor(max_leaf_nodes=H3B_LEAVES,
                                  random_state=sklearn_seed(seed, "h3b-weight-tree")),
            DecisionTreeRegressor(max_leaf_nodes=H3B_LEAVES,
                                  random_state=sklearn_seed(seed, "h3b-horizon-tree")))


def _state_rows(idx: np.ndarray, n_draws: int) -> np.ndarray:
    """Rows of the flattened ``(n * E, p)`` profile that belong to the states ``idx`` (all draws).

    State ``i`` owns rows ``i * E, ..., i * E + E - 1``; the rows of ``idx`` are concatenated in
    the order of ``idx``, so a resample keeps the draws of a state together.
    """
    return (idx[:, None] * n_draws + np.arange(n_draws)).ravel()


def h3b_importances(con_profile: np.ndarray, w_target: np.ndarray, curvature_ref: np.ndarray,
                    t_target: np.ndarray, config: StudyConfig) -> dict:
    """H3b: impurity importances of ``Lambda_tilde`` in a weight tree and a horizon tree.

    Two regression trees with ``max_leaf_nodes = 8`` (DEC-0008 A3, A4(e); fixed so that the
    estimand does not depend on the data-chosen K) are fitted on the construction states'
    deployable profiles: the weight tree to ``w*(H_ref)`` with the curvature ``c`` at ``H_ref`` as
    sample weight (Theorem P3(a): the curvature-weighted regret), the horizon tree to ``ln T``
    (unweighted). The ``E`` evaluation draws of a state share its target. The point estimate is
    the full-data fit.

    The interval is a moving-block bootstrap (blocks of ``config.bootstrap_block`` consecutive
    construction states, ``config.bootstrap_resamples`` resamples, 95%,
    ``make_rng(config.seed, "h3b-bootstrap")``) in which all draws of a state stay together and
    **both trees are refitted in every resample**; the weight curvature is that of the resampled
    rows. Intervals are percentile intervals (importances lie in [0, 1] and the weight importance
    sits on the boundary 0 under the hypothesis, where a basic interval is anti-conservative).
    They condition on the fitted proxies (which are not refitted) and are not guaranteed to
    cover, because the split variable can switch between resamples (the bootstrap of a non-smooth
    functional); ``stability`` is reported for that reason.

    * ``weight_lambda``: importance of ``Lambda_tilde`` in the weight tree. Band [0, 0.2): pass
      iff the interval lies inside it (upper bound strictly below 0.2).
    * ``D``: ``imp_t(Lambda_tilde)`` minus the maximum of the other coordinates' ``imp_t``,
      computed in each resample from the joint importance vector. Pass iff the lower bound is
      above 0 (strict).
    * ``stability``: the share of the ``B`` resamples with ``D > 0`` strictly; a failed resample
      and ``D = 0`` count as "not first" (the denominator is ``B``).

    A tree with a single leaf has no split: its importances are 0/0, so they are not computable,
    not zero. Such a fit is detected by ``tree_.n_leaves == 1``. In a resample it is a failed
    resample (NaN, counted at the unfavourable tail of the interval, DEC-0008 A3). A degenerate
    full-data fit makes that part inconclusive. ``pass`` needs both parts to pass.

    Parameters
    ----------
    con_profile : np.ndarray
        Deployable profile of the construction states, ``(n, E, 4)`` in time order.
    w_target : np.ndarray
        ``w*(H_ref)`` per state, ``(n,)``.
    curvature_ref : np.ndarray
        Curvature ``c`` at ``H_ref`` per state, ``(n,)`` (the weight tree's sample weight).
    t_target : np.ndarray
        ``ln T`` per state (log characteristic horizon), ``(n,)``.
    config : StudyConfig
        Study configuration (seed, bootstrap settings).

    Returns
    -------
    dict
        ``weight_lambda``, ``D``, ``stability``, ``weight_tree_importance`` and
        ``horizon_tree_importance`` (full-data vectors by coordinate, None if degenerate),
        ``degenerate_fits``, ``nan_resamples``, ``n_states``, ``n_resamples``,
        ``max_leaf_nodes``, ``threshold``, ``pass`` and ``inconclusive_reason``.

    Raises
    ------
    ValueError
        If the shapes disagree or the profile does not have ``len(PROFILE_NAMES)`` coordinates.
    """
    n_states, n_draws, n_coords = con_profile.shape
    if n_coords != len(PROFILE_NAMES) or any(
            a.shape != (n_states,) for a in (w_target, curvature_ref, t_target)):
        raise ValueError(f"H3b needs a profile (n, E, {len(PROFILE_NAMES)}) and three (n,) "
                         f"targets; got {con_profile.shape}, {w_target.shape}, "
                         f"{curvature_ref.shape}, {t_target.shape}")
    flat = con_profile.reshape(-1, n_coords)
    lam = PROFILE_NAMES.index("lambda_tilde")
    others = np.array([j for j in range(n_coords) if j != lam])

    def importances(idx: np.ndarray) -> np.ndarray:
        rows = _state_rows(idx, n_draws)
        tree_w, tree_t = _h3b_trees(config.seed)
        tree_w.fit(flat[rows], np.repeat(w_target[idx], n_draws),
                   sample_weight=np.repeat(curvature_ref[idx], n_draws))
        tree_t.fit(flat[rows], np.repeat(t_target[idx], n_draws))
        failed = np.full(n_coords, np.nan)  # a single-leaf tree has no importance (0/0)
        return np.concatenate([
            tree_w.feature_importances_ if tree_w.tree_.n_leaves > 1 else failed,
            tree_t.feature_importances_ if tree_t.tree_.n_leaves > 1 else failed])

    point, values = bootstrap_values(importances, n_states, config.bootstrap_resamples,
                                     config.bootstrap_block, make_rng(config.seed, "h3b-bootstrap"))
    imp_w, imp_t = point[:n_coords], point[n_coords:]
    d_values = values[:, n_coords + lam] - values[:, n_coords + others].max(axis=1)
    d_point = imp_t[lam] - imp_t[others].max()
    w_lo, w_hi, w_failed = percentile_interval(values[:, lam], 0.95)
    d_lo, d_hi, d_failed = percentile_interval(d_values, 0.95)
    parts = {
        "weight_lambda": criterion_verdict(imp_w[lam], w_lo, w_hi, (0.0, 0.2), (True, False),
                                           n_states=n_states),
        "D": criterion_verdict(d_point, d_lo, d_hi, (0.0, np.inf), (False, True),
                               n_states=n_states)}
    degenerate_point = {"weight_tree": bool(np.isnan(imp_w).all()),
                        "horizon_tree": bool(np.isnan(imp_t).all())}
    for name, tree in (("weight_lambda", "weight_tree"), ("D", "horizon_tree")):
        verdict, reason = parts[name]
        if reason == "not computable" and degenerate_point[tree]:
            parts[name] = (verdict, f"not computable: degenerate full-data fit ({tree} has a "
                                    "single leaf)")
    stability = float(np.count_nonzero(d_values > 0.0) / len(d_values)) if len(d_values) else None
    out = {
        "weight_lambda": {"importance": _finite_or_none(imp_w[lam]), "ci": [w_lo, w_hi],
                          "level": 0.95, "band": [0.0, 0.2], "n_failed_resamples": w_failed,
                          **_decision(*parts["weight_lambda"])},
        "D": {"value": _finite_or_none(d_point), "ci": [d_lo, d_hi], "level": 0.95,
              "n_failed_resamples": d_failed, **_decision(*parts["D"])},
        "stability": stability,
        "weight_tree_importance": {n: _finite_or_none(v) for n, v in zip(PROFILE_NAMES, imp_w)},
        "horizon_tree_importance": {n: _finite_or_none(v) for n, v in zip(PROFILE_NAMES, imp_t)},
        "degenerate_fits": {"weight_tree": int(np.isnan(values[:, :n_coords]).any(axis=1).sum()),
                            "horizon_tree": int(np.isnan(values[:, n_coords:]).any(axis=1).sum()),
                            "full_data": degenerate_point},
        "nan_resamples": int(np.isnan(values).any(axis=1).sum()),
        "n_states": int(n_states), "n_resamples": int(len(values)),
        "max_leaf_nodes": H3B_LEAVES,
        "threshold": "weight tree: Lambda_tilde importance interval inside [0, 0.2); horizon tree: "
                     "D = importance(Lambda_tilde) - max(other importances) lower bound > 0"}
    out.update(_combined_decision(parts))
    return out


def h3c_ratio(a5_state_mse: np.ndarray, a4_state_mse: np.ndarray, config: StudyConfig) -> dict:
    """H3c (primary): the regimes' MSE over the closed form's, ``mean(A5) / mean(A4)`` at ``H_ref``.

    A ratio of means with the same block-bootstrap index array in the numerator and the
    denominator (paired on states), level ``1 - 0.05/3``, ``make_rng(config.seed, "h3c-ratio")``.
    Pass iff the upper bound is at most 1.05 (closed; DEC-0008 A1). Failed resamples are
    counted (DEC-0008 A3). The interval conditions on the fitted A4 and A5.

    Parameters
    ----------
    a5_state_mse, a4_state_mse : np.ndarray
        Per-state realized squared error at ``H_ref`` of A5 and A4, ``(n,)``.
    config : StudyConfig
        Study configuration.

    Returns
    -------
    dict
        ``A5_over_A4_mse``, ``ci``, ``level``, ``n_states``, ``n_failed_resamples``,
        ``threshold``, ``pass`` and ``inconclusive_reason``.
    """
    if a5_state_mse.shape != a4_state_mse.shape or a5_state_mse.ndim != 1:
        raise ValueError(f"need two (n,) arrays; got {a5_state_mse.shape}, {a4_state_mse.shape}")
    boot = block_bootstrap_counted(
        lambda idx: float(a5_state_mse[idx].mean() / a4_state_mse[idx].mean()),
        len(a5_state_mse), config.bootstrap_resamples, config.bootstrap_block,
        make_rng(config.seed, "h3c-ratio"), PRIMARY_LEVEL)
    verdict, reason = criterion_verdict(boot.estimate, boot.lower, boot.upper,
                                        (-np.inf, H3C_BOUND), (True, True),
                                        n_states=len(a5_state_mse))
    return {"A5_over_A4_mse": _finite_or_none(boot.estimate), "ci": [boot.lower, boot.upper],
            "level": PRIMARY_LEVEL, "n_states": int(len(a5_state_mse)),
            "n_failed_resamples": boot.n_failed, "threshold": H3C_BOUND,
            **_decision(verdict, reason)}


def h3_regimes(cell: Cell, rules: FittedRules, scores: dict[str, RuleScores],
               config: StudyConfig) -> dict:
    """H3a-H3c and the regime curve: sufficiency, structure and cost of the regimes.

    Parameters
    ----------
    cell : Cell
        Core cell.
    rules : FittedRules
        Fitted rules (regime maps).
    scores : dict[str, RuleScores]
        Test scores (for H3a and H3c).
    config : StudyConfig
        Study configuration.

    Returns
    -------
    dict
        Results for H3a (:func:`h3a_logrank`), H3b (:func:`h3b_importances`) and H3c
        (:func:`h3c_ratio`), and the reported ``regime_curve`` (regret ratio and realized regime
        count by requested ``K``).
    """
    from .allocation import regime_regret, state_horizon_target

    test = cell.splits["test"]
    m, ev = test.moments, test.evals
    col = config.reference_horizon - 1
    lt = config.steps_per_lyapunov
    profile = deployable_profile(ev, rules.proxies, cell.noise, lt)
    curve = {k: regime_regret(rmap, profile, m, col)[1] for k, rmap in rules.regimes.items()}
    realized = {k: rmap.n_regimes for k, rmap in rules.regimes.items()}

    chosen = rules.chosen_regimes
    rmap = rules.regimes[chosen]
    regime = rmap.assign(profile)
    t_state = state_horizon_target(m, cell.noise, config.primary_threshold)
    a5 = scores["A5"]
    h3a = h3a_logrank(regime[:, 0], a5.durations[:, 0], a5.events[:, 0], rmap.horizons_km,
                      t_state, lt, chosen)

    regime_curve = {"regret_ratio_by_K": {str(k): v for k, v in curve.items()},
                    "realized_K": {str(k): v for k, v in realized.items()}}

    con = cell.splits["construction"]
    con_profile = deployable_profile(con.evals, rules.proxies, cell.noise, lt)
    h3b = h3b_importances(
        con_profile, oracle_weight(con.moments)[:, col], curvature(con.moments)[:, col],
        np.log(state_horizon_target(con.moments, cell.noise, config.primary_threshold)), config)

    h3c = h3c_ratio(scores["A5"].state_mse_ref, scores["A4"].state_mse_ref, config)
    out = {"H3a": h3a, "H3b": h3b, "H3c": h3c, "regime_curve": regime_curve}
    check_keys(out)
    return out


# ------------------------------------------------------------------ secondary
def oracle_recovery(scores: dict[str, RuleScores], config: StudyConfig) -> dict:
    """Fraction of the oracle's gain over A2 recovered by deployable rules at ``H_ref``."""
    ref = config.reference_horizon - 1
    mse = {k: float(v.mse[ref]) for k, v in scores.items()}
    def gain(rule: str, oracle: str) -> float:
        denom = mse["A2"] - mse[oracle]
        return (mse["A2"] - mse[rule]) / denom if denom > 0 else float("nan")

    return {"A4_vs_A4o": gain("A4", "A4o"), "A5_vs_Astar": gain("A5", "A*"),
            "A4_vs_Astar": gain("A4", "A*"), "mse_at_href": mse}


def summarize_scores(scores: dict[str, RuleScores], horizons: np.ndarray,
                     config: StudyConfig) -> dict:
    """JSON summary of rule scores at the evaluation horizons."""
    cols = [int(np.nonzero(horizons == h)[0][0]) for h in config.eval_horizons
            if h in horizons]
    labels = [f"{lt:g}LT" for h, lt in zip(config.eval_horizons,
                                            config.eval_horizons_lyapunov) if h in horizons]
    ref = int(np.nonzero(horizons == config.reference_horizon)[0][0])
    return {k: {"mse": dict(zip(labels, v.mse[cols].tolist())),
                "regret": dict(zip(labels, v.regret[cols].tolist())),
                "agreement_href": v.agreement, "km_median_lyapunov": v.km_median,
                "rmst_lyapunov": v.rmst, "mse_href": float(v.mse[ref])}
            for k, v in scores.items()}


def weight_profiles(cell: Cell, config: StudyConfig) -> dict:
    """Median oracle weight per horizon (for figures)."""
    m = cell.splits["test"].moments
    w = oracle_weight(m)
    return {"horizons": m.horizons.tolist(), "median": np.median(w, axis=0).tolist(),
            "q25": np.percentile(w, 25, axis=0).tolist(),
            "q75": np.percentile(w, 75, axis=0).tolist()}


def km_curves(scores: dict[str, RuleScores], horizon_max: int) -> dict:
    """Kaplan-Meier survival curves of realized horizons per rule (for figures)."""
    return {k: kaplan_meier(v.durations, v.events, horizon_max).survival.tolist()
            for k, v in scores.items() if v.durations.size}
