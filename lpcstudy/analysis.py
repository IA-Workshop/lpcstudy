"""Statistics behind each pre-registered hypothesis and secondary analyses.

The identifiers are the v3 ones of :mod:`lpcstudy.identifiers`: H1a-H1d, Q-N, H2a-H2d, H3a-H3c,
the reported gain bound, and the validation check V7 (H2e, noise matching, is added by WU-0002.7).

Every function returns a plain ``dict`` (JSON-serializable) with the point
estimate, its block-bootstrap interval, the pre-registered threshold and a
``pass`` flag. Primary endpoints H2a and H2b use Bonferroni-adjusted
intervals at level ``1 - 0.05/3`` (H3c, also primary, gets its interval in WU-0002.8, and
until then has none); all others use 95% intervals.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import rankdata
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor

from .allocation import deployable_profile
from .config import StudyConfig
from .data import make_rng, sklearn_seed
from .identifiers import check_keys
from .oracle import characteristic_horizon, curvature, hybrid_mse, oracle_weight
from .pipeline import Cell, FittedRules, RuleScores
from .statistics import MIN_STATES, block_bootstrap, bootstrap_values, combine_verdicts, \
    criterion_verdict, holm_adjust, kaplan_meier, logrank_test, ols_slope, partial_correlation, \
    percentile_interval, spearman

PRIMARY_LEVEL = 1.0 - 0.05 / 3.0
PROFILE_NAMES = ("log_eps_tilde", "log_nu_tilde", "lambda_tilde", "log_noise_sens")


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


QN_SMALL = 0.05
"""Upper bound separating a small from a substantial gain in the Q-N reading (v3 section 7)."""


def qn_regressor(seed: int) -> HistGradientBoostingRegressor:
    """Gradient-boosted regressor of Q-N (Methods v2 M10 E3; DEC-0008 A4(c)).

    ``l2_regularization=1.0`` is part of the design (A4(c)): it was in the pilot code and is
    documented here. ``early_stopping=False`` is explicit; at 10^4 samples or fewer it is what
    the default ``'auto'`` does, so no earlier result changes. The scikit-learn seed is
    ``sklearn_seed(seed, "qn-regressor")`` (DEF-0010).

    Parameters
    ----------
    seed : int
        Master seed (``config.seed``).

    Returns
    -------
    HistGradientBoostingRegressor
        Unfitted regressor.
    """
    return HistGradientBoostingRegressor(
        max_iter=300, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=20,
        l2_regularization=1.0, early_stopping=False,
        random_state=sklearn_seed(seed, "qn-regressor"))


def _r2(y: np.ndarray, pred: np.ndarray, idx: np.ndarray) -> float:
    """``1 - SS_res / SS_tot`` of ``pred`` against ``y`` on the rows ``idx``; NaN if undefined."""
    if idx.size == 0:
        return float("nan")
    total = np.sum((y[idx] - y[idx].mean()) ** 2)
    if total == 0.0:
        return float("nan")
    return float(1.0 - np.sum((y[idx] - pred[idx]) ** 2) / total)


def delta_r2(y: np.ndarray, pred_three: np.ndarray, pred_four: np.ndarray,
             idx: np.ndarray) -> float:
    """Out-of-sample gain ``R^2(F4) - R^2(F3)`` on the rows ``idx`` (Q-N).

    Each ``R^2`` is ``1 - SS_res / SS_tot`` with ``SS_tot`` about the mean of ``y[idx]``, so a
    resample with repeated rows is handled by passing the resampled ``idx``. NaN if the rows
    are empty or ``y`` is constant on them (the bootstrap then counts a failed resample).

    Parameters
    ----------
    y : np.ndarray
        Target ``(n,)``.
    pred_three, pred_four : np.ndarray
        Predictions of the three- and four-coordinate models ``(n,)``.
    idx : np.ndarray
        Row indices (repeats allowed).

    Returns
    -------
    float
        ``R^2(F4) - R^2(F3)``.
    """
    return _r2(y, pred_four, idx) - _r2(y, pred_three, idx)


def qn_reading(lower: float, upper: float) -> str:
    """Reading of a Q-N interval for ``Delta R^2`` by the table of v3 section 7.

    Unrounded float64 bounds are compared.

    * upper bound < 0.05 and lower bound <= 0: ``"reduces"`` (N reduces to the other three);
    * lower bound > 0 and upper bound < 0.05: ``"distinct but small"``;
    * lower bound > 0 and upper bound >= 0.05: ``"substantial"``;
    * otherwise (including a NaN bound): ``"undetermined"``.

    Parameters
    ----------
    lower, upper : float
        Interval bounds.

    Returns
    -------
    str
        One of the four readings.
    """
    if np.isnan(lower) or np.isnan(upper):
        return "undetermined"
    if upper < QN_SMALL and lower <= 0.0:
        return "reduces"
    if lower > 0.0 and upper < QN_SMALL:
        return "distinct but small"
    if lower > 0.0 and upper >= QN_SMALL:
        return "substantial"
    return "undetermined"


def _qn_reading_reason(lower: float, upper: float, n_test: int) -> tuple[str, str | None]:
    """Reading and the reason it is "undetermined" for a cause other than the table (A3)."""
    if n_test < MIN_STATES:
        return "undetermined", f"n_states < {MIN_STATES}"
    reading = qn_reading(lower, upper)
    if np.isnan(lower) or np.isnan(upper):
        return reading, "not computable"
    if np.isinf(lower) or np.isinf(upper):
        return reading, "failed resamples >= threshold"
    return reading, None


def qn_profile_block(x_train: np.ndarray, x_test: np.ndarray, w_train: np.ndarray,
                     w_test: np.ndarray, log_t_train: np.ndarray, log_t_test: np.ndarray, *,
                     seed: int, n_resamples: int, block: int, boot_seed: int | np.random.Generator,
                     level: float = 0.95) -> dict:
    """Q-N for one profile: ``Delta R^2`` of F4 against F3 for three targets (DEC-0008 A4(a)).

    F3 is the first three coordinates of the profile, F4 all four. Targets, each fitted by
    ``qn_regressor`` under squared loss:

    * ``logit_w_interior``: ``logit w*`` trained on the interior states (``0 < w* < 1``) of the
      training splits, evaluated on the interior test states;
    * ``w_zero_indicator``: ``1{w* = 0}`` on all states, so ``R^2`` is the Brier skill score;
      predictions outside ``[0, 1]`` are not clipped, only counted;
    * ``log_horizon``: the log state horizon on all states, reported without a reading (D-04).

    The three intervals come from one bootstrap (one vector statistic), so they share the
    resample index sets; the interior filter is applied inside each resample over all test
    states in time order. A non-finite resample is failed and counted (A3). The intervals
    resample test states with the fitted models held fixed, so they omit training variability
    (v3 and Methods v2 E3). Passing the same integer ``boot_seed`` for several profiles shares
    their resamples. The reading of the first two targets is ``qn_reading`` of the interval, or
    "undetermined" with a reason if fewer than 50 test states are in the domain.

    Parameters
    ----------
    x_train, x_test : np.ndarray
        Profiles ``(n, 4)`` of the training (construction plus calibration) and test splits.
    w_train, w_test : np.ndarray
        Oracle weights ``w*(H_ref)`` in ``[0, 1]``.
    log_t_train, log_t_test : np.ndarray
        Log state horizons.
    seed : int
        Master seed for ``qn_regressor``.
    n_resamples, block : int
        Bootstrap resamples and block length.
    boot_seed : int or np.random.Generator
        Randomness of the resample indices.
    level : float, optional
        Confidence level (95%: Q-N is an estimate, v3 section 7).

    Returns
    -------
    dict
        ``logit_w_interior``, ``w_zero_indicator`` and ``log_horizon`` (each ``r2_three``,
        ``r2_four``, ``delta_r2``, ``ci``, ``n_failed_resamples``, ``n_train``, ``n_test``; the
        first two also ``reading`` and ``reason``; the indicator also ``n_pred_outside_unit``),
        and ``noise_sens_r2_from_three`` (how well N is predicted from the other three).

    Raises
    ------
    ValueError
        If the profiles do not have four columns, lengths disagree, or ``w*`` leaves ``[0, 1]``.
    """
    if x_train.shape[1] != 4 or x_test.shape[1] != 4:
        raise ValueError("profiles need four columns")
    if not (len(x_train) == len(w_train) == len(log_t_train)
            and len(x_test) == len(w_test) == len(log_t_test)):
        raise ValueError("profile, weight and horizon lengths disagree")
    for weight in (w_train, w_test):
        if not np.all(np.isfinite(weight)) or weight.min() < 0.0 or weight.max() > 1.0:
            raise ValueError("w* must be finite and inside [0, 1]")

    def logit_of(weight: np.ndarray, rows: np.ndarray) -> np.ndarray:
        inner = np.where(rows, weight, 0.5)  # placeholder outside the interior, never read
        return np.log(inner / (1.0 - inner))

    interior_train = (w_train > 0.0) & (w_train < 1.0)
    interior_test = (w_test > 0.0) & (w_test < 1.0)
    everywhere_train = np.ones(len(w_train), bool)
    everywhere_test = np.ones(len(w_test), bool)
    targets = {
        "logit_w_interior": (interior_train, logit_of(w_train, interior_train),
                             interior_test, logit_of(w_test, interior_test)),
        "w_zero_indicator": (everywhere_train, (w_train == 0.0).astype(float),
                             everywhere_test, (w_test == 0.0).astype(float)),
        "log_horizon": (everywhere_train, log_t_train, everywhere_test, log_t_test),
    }
    names = list(targets)
    pred3, pred4 = {}, {}
    for name, (rows_train, y_train, _, _) in targets.items():
        pred3[name] = qn_regressor(seed).fit(x_train[rows_train][:, :3],
                                             y_train[rows_train]).predict(x_test[:, :3])
        pred4[name] = qn_regressor(seed).fit(x_train[rows_train],
                                             y_train[rows_train]).predict(x_test)

    def stat(idx: np.ndarray) -> np.ndarray:
        out = []
        for name in names:
            _, _, rows_test, y_test = targets[name]
            out.append(delta_r2(y_test, pred3[name], pred4[name], idx[rows_test[idx]]))
        return np.array(out)

    point, values = bootstrap_values(stat, len(w_test), n_resamples, block, boot_seed)
    out: dict = {}
    for col, name in enumerate(names):
        rows_train, _, rows_test, y_test = targets[name]
        full = np.flatnonzero(rows_test)
        interval, n_failed = _interval_block(values[:, col], level)
        entry = {"r2_three": _r2(y_test, pred3[name], full),
                 "r2_four": _r2(y_test, pred4[name], full),
                 "delta_r2": float(point[col]), "ci": interval,
                 "n_failed_resamples": n_failed, "n_train": int(rows_train.sum()),
                 "n_test": int(rows_test.sum())}
        if name != "log_horizon":
            entry["reading"], entry["reason"] = _qn_reading_reason(
                interval[0], interval[1], entry["n_test"])
        if name == "w_zero_indicator":
            entry["n_pred_outside_unit"] = {
                "three": int(np.sum((pred3[name] < 0.0) | (pred3[name] > 1.0))),
                "four": int(np.sum((pred4[name] < 0.0) | (pred4[name] > 1.0)))}
        out[name] = entry
    n_pred = qn_regressor(seed).fit(x_train[:, :3], x_train[:, 3]).predict(x_test[:, :3])
    out["noise_sens_r2_from_three"] = _r2(x_test[:, 3], n_pred, np.arange(len(x_test)))
    return out


def qn_noise_redundancy(cell: Cell, rules: FittedRules, config: StudyConfig) -> dict:
    """Q-N: is the fourth LPC (noise sensitivity) reducible to the other three?

    An estimate, not a pass/fail criterion (v3 section 7; DEC-0008 A4(a)). Nested out-of-sample
    comparison on the construction plus calibration states (training) and the test states, for
    the oracle profile (primary) and the deployable profile (secondary): see
    ``qn_profile_block`` for the three targets (interior logit of ``w*``, the indicator
    ``1{w* = 0}``, the log horizon), the intervals and the readings. The resamples are shared
    across targets and across the two profiles (one integer seed, ``config.seed + 11``: the
    salt of the earlier bootstrap, kept so that the log-horizon interval is unchanged,
    DEC-0012). The counts of ``w* = 0`` and ``w* = 1`` over the test states are reported.

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
        ``role`` ("estimate"), ``primary`` ("oracle"), ``n_w_zero``, ``n_w_one``, ``n_test``,
        and the blocks ``oracle`` and ``deployable`` of ``qn_profile_block``.
    """
    from .allocation import state_horizon_target

    col = config.reference_horizon - 1
    lt = config.steps_per_lyapunov

    def targets(split: str) -> tuple[np.ndarray, np.ndarray]:
        m = cell.splits[split].moments
        t = state_horizon_target(m, cell.noise, config.primary_threshold)
        return oracle_weight(m)[:, col], np.log(t)

    def profiles(kind: str, split: str) -> np.ndarray:
        if kind == "oracle":
            return _oracle_profile(cell, split, config)
        ev = cell.splits[split].evals
        return deployable_profile(ev, rules.proxies, cell.noise, lt)[:, 0, :]

    train_splits = ("construction", "calibration")
    pairs = [targets(s) for s in train_splits]
    w_train = np.concatenate([w for w, _ in pairs])
    log_t_train = np.concatenate([t for _, t in pairs])
    w_test, log_t_test = targets("test")
    out: dict = {"role": "estimate", "primary": "oracle",
                 "n_w_zero": int(np.sum(w_test == 0.0)), "n_w_one": int(np.sum(w_test == 1.0)),
                 "n_test": int(len(w_test))}
    for kind in ("oracle", "deployable"):
        x_train = np.concatenate([profiles(kind, s) for s in train_splits])
        out[kind] = qn_profile_block(
            x_train, profiles(kind, "test"), w_train, w_test, log_t_train, log_t_test,
            seed=config.seed, n_resamples=config.bootstrap_resamples,
            block=config.bootstrap_block, boot_seed=config.seed + 11)
    out["threshold"] = ("estimate, no pass/fail: reading of the oracle Delta R^2 interval for "
                        "the interior logit and for 1{w*=0} by the table of v3 section 7 "
                        "(upper bound < 0.05 and lower bound <= 0: reduces; lower bound > 0 "
                        "and upper bound < 0.05: distinct but small; lower bound > 0 and upper "
                        "bound >= 0.05: substantial; otherwise undetermined)")
    return out


# ------------------------------------------------------------------------ RQ2
H2A_RANGE_BAND = (-np.inf, 0.1)
"""H2a(i): the interval of the median range must lie below 0.1 (upper edge open, A1)."""
H2A_PARTIAL_BAND = (-0.1, 0.1)
"""H2a(ii): each interval must lie inside the open band (DEC-0008 A1)."""


def quadratic_controls(seeds: np.ndarray) -> np.ndarray:
    """Quadratic controls ``[x1, x2, x1^2, x2^2, x1 x2]`` of the log seed ratios (DEC-0008 A4(a2)).

    ``x = (ln(eps_s / rho), ln(delta / rho))`` is centred on the mean of the rows given. Centring
    leaves the span of ``[1, Q]`` unchanged (polynomials of degree 2 are closed under
    translation), so a partial correlation does not depend on the centring; it only conditions
    the least-squares design. The intercept is added by ``partial_correlation``.

    Parameters
    ----------
    seeds : np.ndarray
        ``(n, 2)`` array of ``ln(eps_s / rho)`` and ``ln(delta / rho)``.

    Returns
    -------
    np.ndarray
        ``(n, 5)`` array of controls.

    Raises
    ------
    ValueError
        If ``seeds`` is not ``(n, 2)`` with finite entries.
    """
    x = np.asarray(seeds, dtype=float)
    if x.ndim != 2 or x.shape[1] != 2 or not np.all(np.isfinite(x)):
        raise ValueError(f"seeds must be a finite (n, 2) array; got shape {x.shape}")
    x = x - x.mean(axis=0)
    return np.column_stack([x[:, 0], x[:, 1], x[:, 0] ** 2, x[:, 1] ** 2, x[:, 0] * x[:, 1]])


def _partial_corr(target: np.ndarray, variable: np.ndarray, controls: np.ndarray) -> float:
    """Partial correlation, NaN when it is not defined (counted as a failed resample).

    A target or variable that is constant on the rows given (an indicator with one class in a
    resample), or too few rows for the least-squares fit, give NaN. The caller's bootstrap
    counts a non-finite value as failed (DEC-0008 A3); nothing is replaced here.
    """
    if target.size <= controls.shape[1] + 2 or np.ptp(target) == 0.0 or np.ptp(variable) == 0.0:
        return float("nan")
    with np.errstate(invalid="ignore", divide="ignore"):
        return partial_correlation(target, variable, controls)


def _interval_block(values: np.ndarray, level: float) -> tuple[list[float], int]:
    """``[lower, upper]`` and the failed count of one column of bootstrap values."""
    lo, hi, n_failed = percentile_interval(values, level)
    return [lo, hi], n_failed


def h2a_initial_segments(w_cols: np.ndarray, small: np.ndarray, horizon_labels: list[str], *,
                         n_resamples: int, block: int, seed: int | np.random.Generator,
                         level: float = PRIMARY_LEVEL) -> dict:
    """H2a(i): median range of ``w*`` over initial segments of the horizons (DEC-0008 A4(b)).

    ``L`` is the number of leading horizons at which both r.m.s. errors are small. A state is
    eligible iff ``L >= 2``; its range (max minus min of ``w*``) is taken over the first ``L``
    horizons. The statistic is the median of the ranges of the eligible states. The block
    bootstrap runs over all states in time order and re-evaluates eligibility in each resample,
    at level ``level``. The complete-case version (``L`` equal to all horizons) is reported as a
    sensitivity, with its interval from the same resamples and no verdict. Non-finite resamples
    (an empty eligible set) are failed and counted (A3). The verdict is
    ``criterion_verdict`` for the band ``(-inf, 0.1)`` (upper edge open): pass iff the upper
    bound is below 0.1, fail iff the lower bound is at least 0.1, and inconclusive with fewer
    than 50 eligible states.

    Parameters
    ----------
    w_cols : np.ndarray
        ``(n, k)`` weights ``w*`` at the ``k`` horizons of at least 1 LT, in time order.
    small : np.ndarray
        ``(n, k)`` bool, both r.m.s. errors at most ``linear_regime_rms``.
    horizon_labels : list[str]
        Labels of the ``k`` horizons (LT) for the span keys, for example ``["1", "2", "4"]``.
    n_resamples, block : int
        Bootstrap resamples and block length.
    seed : int or np.random.Generator
        Randomness of the resample indices.
    level : float, optional
        Confidence level (``1 - 0.05/3``).

    Returns
    -------
    dict
        ``median_range``, ``range_ci``, ``range_n_failed_resamples``, ``n_eligible_states``,
        ``n_excluded_states``, ``n_noncontiguous_states`` (states the earlier rule "at least two
        small horizons" admitted whose small horizons are not an initial segment),
        ``range_by_span`` (median and count of the states with ``L`` equal to each span),
        ``complete_case`` and ``part_i_verdict`` with ``part_i_reason``.
    """
    w_arr = np.asarray(w_cols, dtype=float)
    ok = np.asarray(small, dtype=bool)
    n_states, n_cols = w_arr.shape
    if ok.shape != w_arr.shape or len(horizon_labels) != n_cols or n_cols < 2:
        raise ValueError("w_cols and small must share a shape (n, k) with k >= 2 "
                         "and one label per horizon")
    if not np.all(np.isfinite(w_arr)):
        raise ValueError("w_cols holds non-finite weights")
    leading = np.cumprod(ok, axis=1).astype(bool)
    length = leading.sum(axis=1)
    eligible = length >= 2
    complete = length == n_cols
    high = np.where(leading, w_arr, -np.inf).max(axis=1)
    low = np.where(leading, w_arr, np.inf).min(axis=1)
    spread = np.where(eligible, high - low, np.nan)

    def median_of(rows: np.ndarray) -> float:
        return float(np.median(spread[rows])) if rows.size else float("nan")

    def stat(idx: np.ndarray) -> np.ndarray:
        return np.array([median_of(idx[eligible[idx]]), median_of(idx[complete[idx]])])

    point, values = bootstrap_values(stat, n_states, n_resamples, block, seed)
    interval, n_failed = _interval_block(values[:, 0], level)
    interval_cc, n_failed_cc = _interval_block(values[:, 1], level)
    n_eligible = int(eligible.sum())
    verdict, reason = criterion_verdict(float(point[0]), interval[0], interval[1],
                                        H2A_RANGE_BAND, (True, False), n_states=n_eligible)
    by_span = {}
    for span in range(2, n_cols + 1):
        rows = np.flatnonzero(length == span)
        by_span["-".join(horizon_labels[:span])] = {"median": median_of(rows),
                                                    "n_states": int(rows.size)}
    admitted_before = ok.sum(axis=1) >= 2
    return {"median_range": float(point[0]), "range_ci": interval,
            "range_n_failed_resamples": n_failed, "n_eligible_states": n_eligible,
            "n_excluded_states": int(n_states - n_eligible),
            "n_noncontiguous_states": int((admitted_before & (ok.sum(axis=1) != length)).sum()),
            "range_by_span": by_span,
            "complete_case": {"median_range": float(point[1]), "range_ci": interval_cc,
                              "n_failed_resamples": n_failed_cc,
                              "n_states": int(complete.sum())},
            "part_i_verdict": verdict, "part_i_reason": reason}


def h2a_part_ii(w_ref: np.ndarray, growth_scaled: np.ndarray, seeds: np.ndarray, *,
                n_resamples: int, block: int, seed: int | np.random.Generator,
                level: float = PRIMARY_LEVEL) -> dict:
    """H2a(ii), two parts with quadratic seed controls (DEC-0008 A4(a), A4(a2), A1, A3).

    ``w*`` is the oracle weight at ``H_ref`` in ``[0, 1]`` (no clip constant). With
    ``Q(x) = [x1, x2, x1^2, x2^2, x1 x2]`` and ``x = (ln(eps_s/rho), ln(delta/rho))``:

    * (ii-a) the partial correlation of ``1{w* = 0}`` with ``Lambda_tilde`` given ``Q``, over all
      states;
    * (ii-b) the same for ``logit w*`` over the states with ``0 < w* < 1``;
    * (ii-c) the same for ``1{w* = 1}`` over all states, added only if ``w* = 1`` holds in
      strictly more than 5% of the states (decided once, on the full sample).

    All parts use level ``level`` and the same resample index sets; the domain filter is applied
    inside each resample over all states in time order, and the least-squares fit is redone in
    each resample. A non-finite value in a resample (a constant indicator, too few rows) is a
    failed resample and is counted (A3). Each part gets ``criterion_verdict`` against the open
    band ``(-0.1, 0.1)``: inconclusive if its full-sample domain has fewer than 50 states or its
    estimate is not computable. (ii) passes iff every part passes and fails iff any part fails.
    The false-fail probability under the null at the band edge is at most ``k * alpha / 2`` with
    ``alpha = 0.05/3`` and ``k`` the number of parts (the near edge only; union bound).

    Parameters
    ----------
    w_ref : np.ndarray
        Oracle weights ``w*(H_ref)``, ``(n,)``, in ``[0, 1]``, in time order.
    growth_scaled : np.ndarray
        ``Lambda_tilde`` per state (growth rate per Lyapunov time), ``(n,)``.
    seeds : np.ndarray
        ``(n, 2)`` array of ``ln(eps_s / rho)`` and ``ln(delta / rho)``.
    n_resamples, block : int
        Bootstrap resamples and block length.
    seed : int or np.random.Generator
        Randomness of the shared resample indices.
    level : float, optional
        Confidence level (``1 - 0.05/3``).

    Returns
    -------
    dict
        ``part_ii`` (parts ``zero``, ``interior`` and, if triggered, ``one``, each with
        ``partial_corr``, ``ci``, ``n_states``, ``n_failed_resamples``, ``verdict``,
        ``reason``), ``n_w_zero``, ``n_w_one``, ``controls`` and ``part_ii_verdict``.

    Raises
    ------
    ValueError
        If the arrays disagree in length or ``w_ref`` leaves ``[0, 1]`` or is not finite.
    """
    weight = np.asarray(w_ref, dtype=float)
    lam = np.asarray(growth_scaled, dtype=float)
    n_states = len(weight)
    if len(lam) != n_states or len(seeds) != n_states:
        raise ValueError("w_ref, growth_scaled and seeds must have the same length")
    if not np.all(np.isfinite(weight)) or weight.min() < 0.0 or weight.max() > 1.0:
        raise ValueError("w_ref must be finite and inside [0, 1]")
    controls = quadratic_controls(seeds)
    is_zero, is_one = weight == 0.0, weight == 1.0
    interior = ~is_zero & ~is_one
    n_zero, n_one, n_interior = int(is_zero.sum()), int(is_one.sum()), int(interior.sum())
    add_one = 20 * n_one > n_states  # strictly more than 5% of the states, in integers
    logit = np.log(np.where(interior, weight, 0.5) / (1.0 - np.where(interior, weight, 0.5)))
    indicators = {"zero": is_zero.astype(float), "one": is_one.astype(float)}
    names = ["zero", "interior"] + (["one"] if add_one else [])
    domain_size = {"zero": n_states, "interior": n_interior, "one": n_states}

    def stat(idx: np.ndarray) -> np.ndarray:
        out = []
        for name in names:
            rows = idx[interior[idx]] if name == "interior" else idx
            target = logit[rows] if name == "interior" else indicators[name][rows]
            out.append(_partial_corr(target, lam[rows], controls[rows]))
        return np.array(out)

    point, values = bootstrap_values(stat, n_states, n_resamples, block, seed)
    parts, verdicts = {}, []
    for col, name in enumerate(names):
        interval, n_failed = _interval_block(values[:, col], level)
        verdict, reason = criterion_verdict(float(point[col]), interval[0], interval[1],
                                            H2A_PARTIAL_BAND, (False, False),
                                            n_states=domain_size[name])
        parts[name] = {"partial_corr": float(point[col]), "ci": interval,
                       "n_states": domain_size[name], "n_failed_resamples": n_failed,
                       "verdict": verdict, "reason": reason}
        verdicts.append(verdict)
    return {"part_ii": parts, "n_w_zero": n_zero, "n_w_one": n_one,
            "controls": "x1, x2, x1^2, x2^2, x1*x2 with x = (ln(eps_s/rho), ln(delta/rho)) "
                        "centred on the full-sample mean",
            "part_ii_verdict": combine_verdicts(verdicts)}


def h2a_separation(cell: Cell, config: StudyConfig) -> dict:
    """H2a (primary): beyond 1 LT the weight depends on the seed ratio, not on instability.

    Two parts (DEC-0008 A4): (i) the median range of ``w*`` over initial segments of the
    horizons 1, 2, 4 LT in the small-error regime (``h2a_initial_segments``); (ii) the two-part
    partial correlation of ``w*(H_ref)`` with ``Lambda_tilde`` given quadratic seed controls
    (``h2a_part_ii``). Both bootstraps are new: randomness comes from ``make_rng(config.seed,
    label)`` (DEC-0012), both at level ``1 - 0.05/3``. H2a passes iff both parts pass and fails
    iff either fails; ``pass`` is ``verdict == "pass"``.

    Parameters
    ----------
    cell : Cell
        Core cell.
    config : StudyConfig
        Study configuration.

    Returns
    -------
    dict
        The keys of ``h2a_initial_segments`` and ``h2a_part_ii``, plus ``verdict``, ``pass``,
        ``median_range_unrestricted``, ``short_horizon_range_median`` and
        ``unconditional_spearman_w_lambda`` (on the unclipped ``w*`` in ``[0, 1]``).
    """
    m = cell.splits["test"].moments
    o = cell.oracles["test"]
    lt = config.steps_per_lyapunov
    w_star = oracle_weight(m)
    long_horizons = [h for h in config.eval_horizons_lyapunov if h >= 1.0]
    cols = [m.at(int(h * lt)) for h in long_horizons]
    # Small-error regime (FW assumption A6): both forecasters' r.m.s. errors at most
    # config.linear_regime_rms, at the leading horizons.
    small = (np.sqrt(m.sq_cp[:, cols]) <= config.linear_regime_rms) & \
        (np.sqrt(m.sq_plp[:, cols]) <= config.linear_regime_rms)
    out = h2a_initial_segments(
        w_star[:, cols], small, [f"{h:g}" for h in long_horizons],
        n_resamples=config.bootstrap_resamples, block=config.bootstrap_block,
        seed=make_rng(config.seed, "h2a-initial-segments"), level=PRIMARY_LEVEL)
    out["median_range_unrestricted"] = float(np.median(np.ptp(w_star[:, cols], axis=1)))
    w_ref = w_star[:, m.at(config.reference_horizon)]
    seeds = np.column_stack([np.log(m.analog_seed / cell.noise),
                             np.log(m.est_seed / cell.noise)])
    lam = o.growth * lt
    out.update(h2a_part_ii(w_ref, lam, seeds, n_resamples=config.bootstrap_resamples,
                           block=config.bootstrap_block,
                           seed=make_rng(config.seed, "h2a-two-part"), level=PRIMARY_LEVEL))
    out["unconditional_spearman_w_lambda"] = spearman(w_ref, lam)
    out["short_horizon_range_median"] = float(np.median(np.ptp(
        w_star[:, [m.at(int(h * lt)) for h in config.eval_horizons_lyapunov]], axis=1)))
    out["verdict"] = combine_verdicts([out["part_i_verdict"], out["part_ii_verdict"]])
    out["threshold"] = ("(i) upper bound of the median range over initial segments (small-error "
                        "regime) < 0.1; (ii) each part's interval inside (-0.1, 0.1)")
    out["pass"] = bool(out["verdict"] == "pass")
    return out


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
    """H2b (primary): ``w*`` rises with ``n_lib`` (saturating below 1) and with ``rho``.

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
            "median_w_by_n_lib": dict(zip(map(str, sizes.astype(int)), med.tolist())),
            "mean_state_spearman": est, "ci": [lo, hi],
            "monotone_medians": bool(np.all(np.diff(med) > 0)),
            "median_at_largest_n_lib": float(med[-1]), "pass": ok}
        passes.append(ok)
    res["threshold"] = ("per-state Spearman CI lower bound > 0 for rho and for n_lib at "
                        "each rho; median w*(n_lib max) < 0.95 (monotone medians reported)")
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
    tree_w = DecisionTreeRegressor(max_leaf_nodes=max(chosen, 4),
                                   random_state=sklearn_seed(config.seed, "h3b-weight-tree"))
    tree_w.fit(flat, np.repeat(w_t, n_draws), sample_weight=np.repeat(c_t, n_draws))
    tree_t = DecisionTreeRegressor(max_leaf_nodes=max(chosen, 4),
                                   random_state=sklearn_seed(config.seed, "h3b-horizon-tree"))
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
