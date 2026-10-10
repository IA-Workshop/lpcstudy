"""Statistics behind each pre-registered hypothesis and secondary analyses.

The identifiers are the v3 ones of :mod:`lpcstudy.identifiers`: H1a-H1d, Q-N, H2a-H2d, H3a-H3c,
the reported gain bound, and the validation check V7 (H2e, noise matching, is added by WU-0002.7).

Every function returns a plain ``dict`` (JSON-serializable) with the point
estimate, its block-bootstrap interval, the pre-registered threshold and a
``pass`` flag. Primary endpoints (H2a, H2b, H3c) use Bonferroni-adjusted
intervals at level ``1 - 0.05/3``; all others use 95% intervals.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import rankdata
from sklearn.tree import DecisionTreeRegressor

from .allocation import deployable_profile
from .config import StudyConfig
from .identifiers import check_keys
from .oracle import characteristic_horizon, curvature, hybrid_mse, oracle_weight
from .pipeline import Cell, FittedRules, RuleScores
from .statistics import block_bootstrap, holm_adjust, kaplan_meier, logrank_test, \
    ols_slope, partial_correlation, spearman

PRIMARY_LEVEL = 1.0 - 0.05 / 3.0
PROFILE_NAMES = ("log_eps_tilde", "log_nu_tilde", "lambda_tilde", "log_noise_sens")
REDUNDANCY_MARGIN = 0.01


def _boot(config: StudyConfig, stat, n_items: int, level: float = 0.95, salt: int = 0
          ) -> tuple[float, float, float]:
    return block_bootstrap(stat, n_items, config.bootstrap_resamples,
                           config.bootstrap_block, config.seed + salt, level)


# ------------------------------------------------------------------------ RQ1
def v7_noise_scaling(noise_cells: dict[float, Cell], config: StudyConfig) -> dict:
    """V7: ``delta`` scales linearly with ``rho`` (per-state log-log slope in [0.9, 1.1]).

    Parameters
    ----------
    noise_cells : dict[float, Cell]
        Cells of the noise sweep (test-sweep states, same states across levels).
    config : StudyConfig
        Study configuration.

    Returns
    -------
    dict
        Median slope with interval, efficiency ``delta / (rho nu)`` per level.
    """
    levels = sorted(noise_cells)
    log_rho = np.log(levels)
    deltas = np.column_stack([noise_cells[r].splits["test"].moments.est_seed for r in levels])
    log_delta = np.log(deltas)
    centered = log_rho - log_rho.mean()
    slopes = (log_delta - log_delta.mean(axis=1, keepdims=True)) @ centered / \
        np.sum(centered**2)
    est, lo, hi = _boot(config, lambda idx: float(np.median(slopes[idx])), len(slopes))
    nu = noise_cells[levels[0]].oracles["test"].nu
    efficiency = {f"{r:g}": float(np.median(deltas[:, i] / (r * nu)))
                  for i, r in enumerate(levels)}
    return {"median_slope": est, "ci": [lo, hi], "threshold": [0.9, 1.1],
            "efficiency_median_by_noise": efficiency,
            "pass": bool(0.9 <= est <= 1.1)}


def _floor_power_law(log_n: np.ndarray, log_c2: float, exponent: float,
                     log_f2: float) -> np.ndarray:
    return np.log(np.exp(log_c2) * np.exp(log_n) ** (-exponent) + np.exp(log_f2))


def _fit_seed_law(sizes: np.ndarray, mean_sq: np.ndarray) -> tuple[float, float]:
    """Fit ``eps^2 = c^2 N^{-2/d} + f^2``; return ``(2/d, f^2)``."""
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
    """H1a: ``eps_s^2 ~ c^2 N^{-2/d} + f^2`` with ``1/d`` within 25% of Levina-Bickel.

    Parameters
    ----------
    library_cells : dict[tuple[float, int], Cell]
        Cells keyed by ``(rho, N)``.
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
            "mean_seed_by_N": {str(int(n)): float(np.sqrt(v))
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
                                             random_state=config.seed)

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


def h2b_knob_response(noise_cells: dict[float, Cell],
                      library_cells: dict[tuple[float, int], Cell],
                      config: StudyConfig) -> dict:
    """H2b (primary): ``w*`` rises with ``N`` (saturating below 1) and with ``rho``.

    Parameters
    ----------
    noise_cells : dict[float, Cell]
        Noise sweep at the core library size.
    library_cells : dict[tuple[float, int], Cell]
        Library sweep.
    config : StudyConfig
        Study configuration.

    Returns
    -------
    dict
        Median ``w*(H_ref)`` per level, per-state rank correlations, saturation.
    """
    def weights_of(cell: Cell) -> np.ndarray:
        m = cell.splits["test"].moments
        return oracle_weight(m)[:, m.at(config.reference_horizon)]

    res: dict = {}
    rho_levels = np.array(sorted(noise_cells))
    w_rho = np.column_stack([weights_of(noise_cells[r]) for r in rho_levels])
    rho_corr = _per_state_spearman(rho_levels, w_rho)
    est, lo, hi = _boot(config, lambda idx: float(np.mean(rho_corr[idx])), len(rho_corr),
                        PRIMARY_LEVEL, salt=3)
    medians = np.median(w_rho, axis=0)
    res["noise"] = {"median_w_by_noise": dict(zip(map(str, rho_levels), medians.tolist())),
                    "mean_state_spearman": est, "ci": [lo, hi],
                    "monotone_medians": bool(np.all(np.diff(medians) > 0)),
                    "pass": bool(lo > 0)}
    res["library"] = {}
    passes = [res["noise"]["pass"]]
    for rho in sorted({k[0] for k in library_cells}):
        sizes = np.array(sorted(n for r, n in library_cells if r == rho))
        w_n = np.column_stack([weights_of(library_cells[(rho, int(n))]) for n in sizes])
        n_corr = _per_state_spearman(sizes, w_n)
        est, lo, hi = _boot(config, lambda idx: float(np.mean(n_corr[idx])), len(n_corr),
                            PRIMARY_LEVEL, salt=4)
        med = np.median(w_n, axis=0)
        ok = bool(lo > 0 and med[-1] < 0.95)
        res["library"][f"{rho:g}"] = {
            "median_w_by_N": dict(zip(map(str, sizes.astype(int)), med.tolist())),
            "mean_state_spearman": est, "ci": [lo, hi],
            "monotone_medians": bool(np.all(np.diff(med) > 0)),
            "median_at_largest_N": float(med[-1]), "pass": ok}
        passes.append(ok)
    res["threshold"] = ("per-state Spearman CI lower bound > 0 for rho and for N at each "
                        "rho; median w*(N_max) < 0.95 (monotone medians reported)")
    res["pass"] = bool(all(passes))
    return res


def h2c_state_dependence(scores: dict[str, RuleScores], config: StudyConfig) -> dict:
    """H2c: A4 has lower MSE at ``H_ref`` than A2 and than the better single forecaster.

    Parameters
    ----------
    scores : dict[str, RuleScores]
        Test-split scores.
    config : StudyConfig
        Study configuration.

    Returns
    -------
    dict
        Mean paired differences with intervals.
    """
    a4 = scores["A4"].state_mse_ref
    best_single = "A0" if scores["A0"].state_mse_ref.mean() <= \
        scores["A1"].state_mse_ref.mean() else "A1"
    out = {"best_single": best_single}
    for other in ("A2", best_single):
        diff = a4 - scores[other].state_mse_ref
        est, lo, hi = _boot(config, lambda idx: float(np.mean(diff[idx])), len(diff), salt=5)
        out[f"A4_minus_{other}"] = {"mean": est, "ci": [lo, hi],
                                    "relative": est / float(scores[other].state_mse_ref.mean()),
                                    "pass": bool(hi < 0)}
    out["pass"] = bool(out["A4_minus_A2"]["pass"] and out[f"A4_minus_{best_single}"]["pass"])
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
        Test scores (for H3c).
    config : StudyConfig
        Study configuration.

    Returns
    -------
    dict
        Results for H3a, H3b and H3c, and the reported ``regime_curve`` (regret ratio and
        realized regime count by requested ``K``).
    """
    from .allocation import regime_regret, state_horizon_target

    test = cell.splits["test"]
    m, ev = test.moments, test.evals
    col = config.reference_horizon - 1
    profile = deployable_profile(ev, rules.proxies, cell.noise, config.steps_per_lyapunov)
    curve = {k: regime_regret(rmap, profile, m, col)[1] for k, rmap in rules.regimes.items()}
    realized = {k: rmap.n_regimes for k, rmap in rules.regimes.items()}

    chosen = rules.chosen_regimes
    rmap = rules.regimes[chosen]
    regime = rmap.assign(profile)
    t_state = state_horizon_target(m, cell.noise, config.primary_threshold)
    lt = config.steps_per_lyapunov
    iqr, weights = [], []
    for k in range(rmap.n_regimes):
        members = regime[:, 0] == k
        if members.sum() >= 2:
            q75, q25 = np.percentile(t_state[members] / lt, [75, 25])
            iqr.append(q75 - q25)
            weights.append(members.sum())
    mean_iqr = float(np.average(iqr, weights=weights)) if iqr else float("nan")

    # One observation per state (first evaluation draw) so that the log-rank test
    # does not treat repeated draws of the same state as independent.
    a5 = scores["A5"]
    first = regime[:, 0]
    dur0, ev0 = a5.durations[:, 0], a5.events[:, 0]
    order = np.argsort(np.nan_to_num(rmap.horizons_km, nan=np.inf))
    p_vals = []
    for a, b in zip(order[:-1], order[1:]):
        in_a, in_b = first == a, first == b
        if in_a.any() and in_b.any():
            p_vals.append(logrank_test(dur0[in_a], ev0[in_a], dur0[in_b], ev0[in_b]))
    adjusted = holm_adjust(p_vals) if p_vals else []
    regret_ok = curve[chosen] <= 0.05
    iqr_ok = mean_iqr <= 0.5
    logrank_ok = bool(adjusted) and max(adjusted) < 0.01
    h3a = {"chosen_K": chosen, "regret_ratio": curve[chosen], "mean_iqr_lyapunov": mean_iqr,
           "logrank_holm_p": adjusted, "regret_pass": bool(regret_ok),
           "iqr_pass": bool(iqr_ok), "logrank_pass": bool(logrank_ok),
           "pass": bool(regret_ok and iqr_ok and logrank_ok)}

    regime_curve = {"regret_ratio_by_K": {str(k): v for k, v in curve.items()},
                    "realized_K": {str(k): v for k, v in realized.items()}}

    con = cell.splits["construction"]
    con_profile = deployable_profile(con.evals, rules.proxies, cell.noise, lt)
    flat = con_profile.reshape(-1, con_profile.shape[-1])
    n_draws = con_profile.shape[1]
    w_t = oracle_weight(con.moments)[:, col]
    c_t = curvature(con.moments)[:, col]
    t_t = np.log(state_horizon_target(con.moments, cell.noise, config.primary_threshold))
    tree_w = DecisionTreeRegressor(max_leaf_nodes=max(chosen, 4), random_state=config.seed)
    tree_w.fit(flat, np.repeat(w_t, n_draws), sample_weight=np.repeat(c_t, n_draws))
    tree_t = DecisionTreeRegressor(max_leaf_nodes=max(chosen, 4), random_state=config.seed)
    tree_t.fit(flat, np.repeat(t_t, n_draws))
    imp_w, imp_t = tree_w.feature_importances_, tree_t.feature_importances_
    names = list(PROFILE_NAMES)
    h3b = {"weight_tree_importance": dict(zip(names, imp_w.tolist())),
           "horizon_tree_importance": dict(zip(names, imp_t.tolist())),
           "threshold": "weight tree: lambda < 0.2; horizon tree: lambda > each other "
                        "coordinate",
           "pass": bool(imp_w[2] < 0.2 and imp_t[2] > max(np.delete(imp_t, 2)))}

    ratio = float(scores["A5"].state_mse_ref.mean() / scores["A4"].state_mse_ref.mean())
    h3c = {"A5_over_A4_mse": ratio, "threshold": 1.05, "pass": bool(ratio <= 1.05)}
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
