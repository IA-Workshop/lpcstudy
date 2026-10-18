"""Statistics behind each pre-registered hypothesis and secondary analyses.

The identifiers are the v3 ones of :mod:`lpcstudy.identifiers`: H1a-H1d, Q-N, H2a-H2e, H3a-H3c,
the reported gain bound, and the validation check V7.

Every function returns a plain ``dict`` (JSON-serializable) with the point
estimate, its block-bootstrap interval and the pre-registered threshold. Every criterion that
carries a pass/fail rule also carries the three-valued ``verdict`` of DEC-0008 A1/A3 (``pass``,
``fail``, ``inconclusive``, with a ``reason`` for an inconclusive one) from the shared helpers of
:mod:`lpcstudy.statistics`, and ``pass`` is ``verdict == "pass"`` (DEC-0012; v3 section 7). The
gain bound has no bar (v3 section 2, "without a pass/fail bar") and so no verdict. Primary
endpoints H2a, H2b and H3c use Bonferroni-adjusted intervals at level ``1 - 0.05/3``; all others
use 95% intervals.

For the statistics of WU-0002.7 and .8 (H2b(ii), H2e, H3a, H3b, H3c) a result that cannot be
computed, or whose interval meets a band edge, is *inconclusive* and says why (``reason``); failed
bootstrap resamples are counted (``n_failed_resamples``) and widen the interval, never dropped.
H3a has no equivalence margin, so its ``verdict`` is only ``pass`` or ``inconclusive``
(DEC-0008 A3).
"""

from __future__ import annotations

import warnings

import numpy as np
from scipy.optimize import OptimizeWarning, curve_fit
from scipy.stats import rankdata
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor

from .allocation import (
    NOISE_SENS_FLOOR,
    deployable_profile,
    regime_regret,
    state_horizon_target,
)
from .config import StudyConfig
from .data import make_rng, sklearn_seed
from .dump import StateDump
from .identifiers import check_keys
from .oracle import characteristic_horizon, curvature, hybrid_mse, inverse_dimension, \
    oracle_weight
from .pipeline import Cell, FittedRules, RuleScores, SplitData
from .statistics import MIN_STATES, block_bootstrap_counted, block_bootstrap_dropped, \
    bootstrap_values, combine_verdicts, criterion_verdict, endpoint_mc_error, holm_adjust, \
    kaplan_meier, logrank_parts, logrank_test, ols_slope, partial_correlation, \
    percentile_interval, spearman

PRIMARY_LEVEL = 1.0 - 0.05 / 3.0
PROFILE_NAMES = ("log_eps_tilde", "log_nu_tilde", "lambda_tilde", "log_noise_sens")
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
H1A_BAND = (0.75, 1.25)  # DEC-0008 A1/A4(h): the ratio (1/d_fit)/(1/d_LB), closed band
H1B_BAND = (0.8, 1.2)  # v3 H1b: closed
H1D_BAND = (0.7, float("inf"))  # v3 H1d: [0.7, inf), closed
H1C_BAND = (0.8, 1.25)  # v3 H1c (PLP): closed (DEC-0008 A1)
H1C_MIN_INTERVAL = 10
"""H1c: fewest finite ratios for which an interval is computed at all (reported for 10 to 49 states,
though the verdict then reads ``n_states < 50``; fewer than 10 states give no number)."""
H2C_BAND = (float("-inf"), 0.0)  # v3 H2c: both upper bounds < 0, the edge 0 is open (DEC-0008 A1)
H2C_CLOSED = (True, False)
H2D_BAND = (float("-inf"), 0.10)  # v3 H2d: upper bound <= 0.10, the edge is closed (DEC-0008 A1)
H1_LEVEL = 0.95
H1A_EXPONENT_BOUNDS = (0.01, 10.0)
"""Bounds of the fitted ``2/d`` in :func:`_fit_seed_law` (``curve_fit``); a fit at a bound is a
constrained estimate, counted in ``n_exponent_at_bound`` (DEF-0001, row N3)."""
H1A_BOUND_TOL = 1e-6
"""A ``2/d`` within this distance of a bound counts as at the bound. The trust-region solver keeps
its iterates strictly inside the bounds: an exponent constrained at 0.01 returned 0.0100000000250
(a distance of 2.5e-11), so 1e-6 separates a constrained fit from a free one by four orders."""


def _boot(config: StudyConfig, stat, n_items: int, rng: np.random.Generator,
          level: float = 0.95) -> tuple[float, float, float, int]:
    """Block bootstrap drawing from ``rng``: the estimate, the interval and the number of NaN
    resamples that ``np.nanquantile`` dropped (DEF-0001, row T3).

    The estimate and bounds are those of ``statistics.block_bootstrap``. The two callers (V7,
    H1b CP) report the count as ``n_dropped_resamples``; neither converts it to the A3 tail
    (H2b(i) did until WU-0002.9b, DEF-0019). The generator is consumed: each call needs its own
    ``make_rng(config.seed, system, "bootstrap", ...)`` (WU-0002.14; needs owner review before
    freeze).
    """
    return block_bootstrap_dropped(stat, n_items, config.bootstrap_resamples,
                                   config.bootstrap_block, rng, level)


# ------------------------------------------------------------------------ RQ1
def v7_efficiency(levels: np.ndarray, deltas: np.ndarray, nu: np.ndarray,
                  config: StudyConfig, system: str) -> dict:
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
    system : str
        System name; the bootstrap generators are
        ``make_rng(config.seed, system, "bootstrap", "V7", "slope")`` and
        ``(..., "V7", f"efficiency-{rho:g}")`` (WU-0002.14). Needs owner review before freeze.

    Returns
    -------
    dict
        ``median_slope`` with block-bootstrap interval ``ci`` (reported only), ``threshold``,
        ``slope_pass``; ``efficiency_median_by_noise``, its interval
        ``efficiency_ci_by_noise`` (reported only) and ``efficiency_pass_by_noise`` per level;
        ``n_states``, ``n_nonfinite``, ``n_dropped_resamples`` (NaN resamples that the reported
        intervals dropped: ``slope`` and ``efficiency[rho]``; DEF-0001) and ``pass`` (slope and
        every level, bands closed).

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
    dropped_slope = 0  # no bootstrap runs when a state is bad, so nothing is dropped
    if n_bad:
        est, lo, hi = float(np.median(slopes)), *nan_ci
    else:
        est, lo, hi, dropped_slope = _boot(
            config, lambda idx: float(np.median(slopes[idx])), len(slopes),
            make_rng(config.seed, system, "bootstrap", "V7", "slope"))
    out_eff, out_ci, out_pass, out_dropped = {}, {}, {}, {}
    for i, rho in enumerate(levels):
        key = f"{rho:g}"
        out_eff[key] = float(np.median(efficiency[:, i]))
        out_dropped[key] = 0
        if n_bad:
            out_ci[key] = list(nan_ci)
        else:
            _, boot_lo, boot_hi, dropped = _boot(
                config, lambda idx: float(np.median(efficiency[idx, i])), len(efficiency),
                make_rng(config.seed, system, "bootstrap", "V7", f"efficiency-{rho:g}"))
            out_ci[key], out_dropped[key] = [boot_lo, boot_hi], int(dropped)
        out_pass[key] = bool(low <= out_eff[key] <= high)
    slope_pass = bool(low <= est <= high)
    return {"median_slope": est, "ci": [lo, hi], "threshold": [low, high],
            "slope_pass": slope_pass, "efficiency_median_by_noise": out_eff,
            "efficiency_ci_by_noise": out_ci, "efficiency_pass_by_noise": out_pass,
            "n_states": int(len(nu)), "n_nonfinite": n_bad,
            "n_dropped_resamples": {"slope": int(dropped_slope), "efficiency": out_dropped},
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
    return v7_efficiency(np.array(levels), deltas, nu, config, noise_cells[levels[0]].system)


def _floor_power_law(log_n: np.ndarray, log_c2: float, exponent: float,
                     log_f2: float) -> np.ndarray:
    return np.log(np.exp(log_c2) * np.exp(log_n) ** (-exponent) + np.exp(log_f2))


def _fit_seed_law(sizes: np.ndarray, mean_sq: np.ndarray) -> tuple[float, float]:
    """Fit ``eps^2 = c^2 n_lib^{-2/d} + f^2``; return ``(2/d, f^2)``.

    ``2/d`` is bounded to ``H1A_EXPONENT_BOUNDS`` (a silent clip: the solver cannot leave the
    bounds), so a result at a bound is a constrained estimate; the caller flags it
    (:func:`_median_fit_stats`, ``n_exponent_at_bound``). ``curve_fit`` also warns that the
    covariance of the parameters could not be estimated (``OptimizeWarning``; the covariance is not
    used, and the fit has three parameters, so it warns whenever there are three library sizes or
    fewer, as in the smoke preset); the caller counts those warnings (``n_covariance_warnings``).
    """
    log_n = np.log(sizes)
    guess = (np.log(mean_sq[0]) + 2 * 0.5 * log_n[0], 1.0, np.log(mean_sq[-1] * 0.5))
    try:
        params, _ = curve_fit(_floor_power_law, log_n, np.log(mean_sq), p0=guess,
                              bounds=([-50, H1A_EXPONENT_BOUNDS[0], -60],
                                      [50, H1A_EXPONENT_BOUNDS[1], 10]), maxfev=20_000)
    except RuntimeError:
        return float("nan"), float("nan")
    return float(params[1]), float(np.exp(params[2]))


def _median_fit_stats(seed_sq: np.ndarray, inverse_dim: np.ndarray, sizes: np.ndarray,
                      rows: np.ndarray) -> np.ndarray:
    """``[ratio, fitted 1/d, floor f^2, at bound, n warnings]`` of the median fit on ``rows``.

    The fit is :func:`_fit_seed_law` of the column medians of ``seed_sq[rows]``; the reference
    is the mean of ``inverse_dim[rows]``. A median that is not positive and finite, a fit that
    raises ``ValueError`` (``curve_fit`` does for non-finite residuals, and ``_fit_seed_law``
    catches only ``RuntimeError``) or a fit that returns NaN gives NaN for the first three, and so
    a failed (counted) bootstrap resample. A reference that is not positive gives a NaN ratio.

    The last two entries are counts, never NaN (DEF-0001, rows N2 and N3; they leave the first
    three unchanged): 1.0 if the fitted ``2/d`` is at a bound of the fit (0 if no fit), and the
    number of ``OptimizeWarning`` the fit emitted. The fit runs under ``catch_warnings(record=True)``
    with every warning recorded; the ``OptimizeWarning`` are counted and **not** re-issued, and every
    other warning is re-issued unchanged.
    """
    medians = np.median(seed_sq[rows], axis=0)
    two_over_d, floor_sq = float("nan"), float("nan")
    n_warnings = 0
    if np.all(np.isfinite(medians) & (medians > 0)):
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                two_over_d, floor_sq = _fit_seed_law(sizes, medians)
        except ValueError:
            pass
        for note in caught:
            if issubclass(note.category, OptimizeWarning):
                n_warnings += 1
            else:
                warnings.warn_explicit(note.message, note.category, note.filename, note.lineno,
                                       source=note.source)
    fitted = two_over_d / 2.0
    reference = float(inverse_dim[rows].mean())
    ratio = fitted / reference if np.isfinite(fitted) and reference > 0 else float("nan")
    at_bound = np.isfinite(two_over_d) and (
        min(abs(two_over_d - bound) for bound in H1A_EXPONENT_BOUNDS)
        <= H1A_BOUND_TOL
    )
    return np.array([ratio, fitted, floor_sq, float(at_bound), float(n_warnings)])


def h1a_library_scaling(library_cells: dict[tuple[float, int], Cell],
                        config: StudyConfig, capture: dict | None = None) -> dict:
    """H1a: median fit of ``eps_s^2 ~ b^2 n_lib^{-2/d} + f^2``; ratio of ``1/d`` to Levina-Bickel.

    Implements DEC-0008 A4(h), A5, A1 and A3. At each noise level the fit is to the *median*
    over states of the squared analog seed error at each library size (heavy-tail robust). The
    reference ``1/d_LB`` is the mean over states of ``S / (k - 1)``
    (:func:`lpcstudy.oracle.inverse_dimension`, exactly unbiased for ``1/d``; the median of
    ``S / (k - 1)`` would be biased by -1.7%, and the v1 reference ``1 / median(local_dim)``
    by +3.7%). The statistic is the ratio ``(1/d_fit)/(1/d_LB)``; its 95% moving-block-bootstrap
    interval is joint: one resampled state set per resample feeds the numerator and the
    denominator. Pass at
    a noise level iff the interval lies in the closed band [0.75, 1.25]; fail iff it misses the
    band; otherwise inconclusive. The whole passes iff every noise level passes (v3 section 7).
    The floor ``f`` is reported only (the v1 condition "floor increasing in rho" is removed).

    A state with a non-finite seed error (any library size, any noise level) or a non-finite
    reference is excluded from both parts and counted (``n_excluded_nonfinite``); fewer than
    ``statistics.MIN_STATES`` (50) states left gives inconclusive ("n_states < 50"); a
    non-finite point estimate gives inconclusive ("not computable"); failed resamples are
    counted per noise level (``n_failed_resamples``) and placed at the unfavourable tail by the
    shared helper.

    Parameters
    ----------
    library_cells : dict[tuple[float, int], Cell]
        Cells keyed by ``(rho, n_lib)``, all on the same test-sweep states.
    config : StudyConfig
        Study configuration.
    capture : dict, optional
        If given (the opt-in state dump, WU-0003.7c), it is filled with references to the arrays
        the function already computes and goes on to use (the caller copies them, as
        ``StateDump.record_extra`` does; nothing here writes to them): ``noise_levels`` and ``n_lib`` (the sorted levels and sizes),
        ``local_dim`` and ``inverse_dim`` (per test-sweep state, before the finite filter), and
        ``rho=<g>/seed_sq`` (``(n, len(n_lib))``, the squared analog seed errors before the
        filter). Nothing is computed for it and nothing flows back.

    Returns
    -------
    dict
        ``inverse_dim_reference``, ``reference_estimator``, ``n_states``, ``n_excluded_nonfinite``,
        ``band``, ``level``, ``verdict``, ``reason``, ``pass`` and ``by_noise[rho]`` with
        ``fitted_inverse_dim``, ``ci_inverse_dim`` (marginal, reported only), ``ratio``,
        ``ratio_ci``, ``n_failed_resamples``, ``n_exponent_at_bound`` and
        ``n_covariance_warnings`` (each ``{point, resamples}``: the fits whose ``2/d`` is at a bound
        of ``curve_fit`` and the ``OptimizeWarning`` emitted; counts only, DEF-0001),
        ``verdict``, ``reason``, ``floor_rms`` and ``median_seed_by_n_lib`` (square root of the
        median).

    Raises
    ------
    ValueError
        If the cells do not share the same ``local_dim`` (the same states), or a seed error has
        a different number of states.
    """
    noises = sorted({k[0] for k in library_cells})
    sizes = np.array(sorted({k[1] for k in library_cells}), dtype=float)
    first = library_cells[(noises[0], int(sizes[0]))]
    local_dim = first.oracles["test"].local_dim
    for key, cell in library_cells.items():
        if not np.array_equal(cell.oracles["test"].local_dim, local_dim, equal_nan=True):
            raise ValueError(f"cell {key} has a different local_dim: the library cells must "
                             f"share the test-sweep states")
    inverse_all = inverse_dimension(local_dim)
    seed_sq = {rho: np.column_stack([library_cells[(rho, int(n))].splits["test"]
                                     .moments.analog_seed ** 2 for n in sizes])
               for rho in noises}
    if capture is not None:
        capture.update({"noise_levels": np.array(noises), "n_lib": sizes, "local_dim": local_dim,
                        "inverse_dim": inverse_all,
                        **{f"rho={rho:g}/seed_sq": sq for rho, sq in seed_sq.items()}})
    finite = np.isfinite(inverse_all)
    for rho, sq in seed_sq.items():
        if sq.shape[0] != len(local_dim):
            raise ValueError(f"rho={rho:g}: {sq.shape[0]} seed errors for {len(local_dim)} "
                             f"local dimensions")
        finite &= np.all(np.isfinite(sq), axis=1)
    keep = np.flatnonzero(finite)  # time order kept; one state set for every rho
    n_states = len(keep)
    inverse = inverse_all[keep]
    nan_pair = [float("nan"), float("nan")]
    out: dict = {
        "inverse_dim_reference": float(inverse.mean()) if n_states else float("nan"),
        "reference_estimator": "mean over states of S/(k-1), S = sum_j ln(T_k/T_j), k = 20 "
                               "(Levina-Bickel with the k-1 normalisation; exactly unbiased for "
                               "1/d under the Poisson law)",
        "n_states": int(n_states), "n_excluded_nonfinite": int(len(local_dim) - n_states),
        "band": list(H1A_BAND), "level": H1_LEVEL, "by_noise": {}}
    system = first.system
    for rho in noises:
        sq = seed_sq[rho][keep]
        if n_states:
            point, values = bootstrap_values(
                lambda idx: _median_fit_stats(sq, inverse, sizes, idx), n_states,
                config.bootstrap_resamples, config.bootstrap_block,
                make_rng(config.seed, system, "bootstrap", "H1a", f"{rho:g}"))
            ratio_lo, ratio_hi, n_failed = percentile_interval(values[:, 0], H1_LEVEL)
            inv_lo, inv_hi, _ = percentile_interval(values[:, 1], H1_LEVEL)
            medians = np.median(sq, axis=0)
        else:
            point = np.array([np.nan, np.nan, np.nan, 0.0, 0.0])
            values = np.zeros((0, 5))
            ratio_lo = ratio_hi = inv_lo = inv_hi = float("nan")
            n_failed, medians = 0, np.full(len(sizes), np.nan)
        verdict, reason = criterion_verdict(float(point[0]), ratio_lo, ratio_hi, H1A_BAND,
                                            n_states=n_states)
        out["by_noise"][f"{rho:g}"] = {
            "fitted_inverse_dim": float(point[1]), "ci_inverse_dim": [inv_lo, inv_hi],
            "ratio": float(point[0]), "ratio_ci": [ratio_lo, ratio_hi],
            "n_failed_resamples": int(n_failed),
            "n_exponent_at_bound": {"point": int(point[3]), "resamples": int(values[:, 3].sum())},
            "n_covariance_warnings": {"point": int(point[4]),
                                      "resamples": int(values[:, 4].sum())},
            "verdict": verdict, "reason": reason, "floor_rms": float(np.sqrt(point[2])),
            "median_seed_by_n_lib": {str(int(n)): float(np.sqrt(v))
                                     for n, v in zip(sizes, medians)}}
    parts = out["by_noise"]
    out["verdict"] = combine_verdicts(v["verdict"] for v in parts.values())
    out["reason"] = "; ".join(f"rho={k}: {v['reason']}" for k, v in parts.items()
                              if v["verdict"] == "inconclusive") \
        if out["verdict"] == "inconclusive" else None
    out["pass"] = bool(out["verdict"] == "pass")
    return out


def h1b_seed_amplifier(cell: Cell, config: StudyConfig) -> dict:
    """H1b: ``log rms(e_H)`` against ``log(g_H seed / sqrt(m))`` has unit slope at ``H_ref``.

    The verdict rests on the PLP regression only (v3 H1b): its 95% block-bootstrap interval must
    lie in the closed band [0.8, 1.2] (pass), miss it (fail), or else the verdict is
    inconclusive (DEC-0008 A1, A3). The CP slope and interval are reported with no verdict
    (the CP regression is contaminated by the copied observation noise and is a diagnostic).
    States whose regression pair (``x``, ``y``) is not finite are excluded from that regression
    and counted (``n_excluded_nonfinite``; DEC-0008 A3); the PLP verdict applies the minimum of
    50 states after exclusion, and a CP exclusion never shrinks the PLP regression.
    The squared error enters as ``max(E e^2 - floor, 1e-12)``; a regression state where the floor
    binds (``E e^2 - floor < 1e-12``, so ``y`` is pinned at ``0.5 ln 1e-12 = -13.8``, a
    high-leverage vertical outlier) is kept and counted in ``n_floored`` (DEF-0001, row N4; for the
    PLP regression, whose floor is 0, it is a sentinel that should read 0).
    Both regressions bootstrap from a fresh ``make_rng(config.seed, system, "bootstrap", "H1b")``
    (the pairing of the CP and PLP resamples is kept, WU-0002.14; with different numbers of kept
    states the index arrays differ anyway). Failed resamples of the PLP slope are
    counted (``PLP.n_failed_resamples``) and placed at the unfavourable tail. The CP interval
    still drops non-finite resamples (``block_bootstrap_dropped``); it is reported only, and the
    drops are counted (``CP.n_dropped_resamples``).

    Parameters
    ----------
    cell : Cell
        Core cell.
    config : StudyConfig
        Study configuration.

    Returns
    -------
    dict
        ``CP`` (``slope``, ``ci``, ``n_floored``, ``n_dropped_resamples``), ``PLP`` (``slope``,
        ``ci``, ``n_floored``, ``n_failed_resamples``), ``threshold`` [0.8, 1.2], ``n_states`` and ``n_excluded_nonfinite`` (of the PLP
        regression), ``verdict``, ``reason`` and ``pass``.
    """
    m = cell.splits["test"].moments
    o = cell.oracles["test"]
    col = m.at(config.reference_horizon)
    gain = o.gains[:, config.reference_horizon - 1]
    dim = cell.ctx.spec.dim
    copied = cell.noise**2 / cell.setup.n_analogs
    res: dict = {}
    for name, seed_err, sq, floor in (("CP", m.analog_seed, m.sq_cp[:, col], copied),
                                      ("PLP", m.est_seed, m.sq_plp[:, col], 0.0)):
        x_all = np.log(gain * seed_err / np.sqrt(dim))
        y_all = 0.5 * np.log(np.maximum(sq - floor, 1e-12))
        keep = np.isfinite(x_all) & np.isfinite(y_all)  # excluded and counted (DEC-0008 A3)
        x, y = x_all[keep], y_all[keep]
        n_excluded = int(len(x_all) - len(x))
        n_floored = int(((sq - floor) < 1e-12)[keep].sum())  # the floor binds: y = -13.8
        stat = lambda idx: ols_slope(x[idx], y[idx])
        n_dropped = 0
        if len(x) == 0:
            est = lo = hi = float("nan")
            n_failed = 0
        elif name == "CP":
            est, lo, hi, n_dropped = _boot(config, stat, len(x),
                                           make_rng(config.seed, cell.system, "bootstrap", "H1b"))
            n_failed = 0
        else:
            interval = block_bootstrap_counted(
                stat, len(x), config.bootstrap_resamples, config.bootstrap_block,
                make_rng(config.seed, cell.system, "bootstrap", "H1b"), H1_LEVEL)
            est, lo, hi, n_failed = interval.estimate, interval.lower, interval.upper, \
                interval.n_failed
        res[name] = {"slope": est, "ci": [lo, hi], "n_excluded_nonfinite": n_excluded,
                     "n_floored": n_floored}
        if name == "CP":
            res[name]["n_dropped_resamples"] = int(n_dropped)
        else:
            res[name]["n_failed_resamples"] = int(n_failed)
            n_states = int(len(x))
    verdict, reason = criterion_verdict(res["PLP"]["slope"], *res["PLP"]["ci"], H1B_BAND,
                                        n_states=n_states)
    res.update({"threshold": list(H1B_BAND), "n_states": n_states,
                "n_excluded_nonfinite": res["PLP"]["n_excluded_nonfinite"],
                "verdict": verdict, "reason": reason, "pass": bool(verdict == "pass")})
    return res


def h1c_ratio_block(ratios: np.ndarray, config: StudyConfig, system: str, *,
                    with_verdict: bool = True) -> dict:
    """Median of the per-state ratios with its 95% block-bootstrap interval (H1c; WU-0002.9).

    Non-finite ratios are excluded and counted (``n_excluded_nonfinite``; DEC-0008 A3).
    ``n_states`` is the number of finite ratios. With at least ``H1C_MIN_INTERVAL`` (10) of them
    the interval is computed by ``block_bootstrap_counted`` from a fresh
    ``make_rng(config.seed, system, "bootstrap", "H1c")`` (the PLP and the CP share the label,
    WU-0002.14), with failed resamples counted (``n_failed_resamples``). With fewer, ``median_ratio`` and
    ``ci`` are None (a number that was not computed is not shown). The 50-state minimum of
    DEC-0008 A3 replaces the earlier "fewer than 10 states" branch: it is applied by
    ``criterion_verdict`` (inconclusive, ``n_states < 50``) and can only turn a verdict into
    inconclusive. The band is [0.8, 1.25], closed (v3 H1c).

    Parameters
    ----------
    ratios : np.ndarray
        ``Lambda_bar x slope`` of each eligible state.
    config : StudyConfig
        Study configuration (resamples, block, seed).
    system : str
        System name (a label of the bootstrap generator, WU-0002.14; the bootstrap seed of a
        verdict statistic: needs owner review before freeze).
    with_verdict : bool, optional
        Add ``verdict``, ``reason`` and ``pass``. False for the CP, which is reported with no
        verdict (v3 H1c names the PLP; DEC-0016 O3).

    Returns
    -------
    dict
        ``median_ratio``, ``ci``, ``n_states``, ``n_excluded_nonfinite``,
        ``n_failed_resamples`` and, with a verdict, ``verdict``, ``reason`` and ``pass``.
    """
    values = np.asarray(ratios, dtype=float)
    finite = np.isfinite(values)
    kept = values[finite]
    out: dict = {"median_ratio": None, "ci": None, "n_states": int(kept.size),
                 "n_excluded_nonfinite": int((~finite).sum()), "n_failed_resamples": 0}
    estimate = lower = upper = float("nan")
    if kept.size >= H1C_MIN_INTERVAL:
        interval = block_bootstrap_counted(
            lambda idx: float(np.median(kept[idx])), int(kept.size), config.bootstrap_resamples,
            config.bootstrap_block, make_rng(config.seed, system, "bootstrap", "H1c"), H1_LEVEL)
        estimate, lower, upper = interval.estimate, interval.lower, interval.upper
        out.update(median_ratio=estimate, ci=[lower, upper],
                   n_failed_resamples=int(interval.n_failed))
    if with_verdict:
        verdict, reason = criterion_verdict(estimate, lower, upper, H1C_BAND,
                                            n_states=int(kept.size))
        out.update(_decision(verdict, reason))
    return out


def h1c_horizon_law(cell: Cell, config: StudyConfig, capture: dict | None = None) -> dict:
    """H1c: state-wise slope of ``T`` against ``ln theta`` equals ``1 / Lambda_bar``.

    The verdict rests on the PLP median only (v3 H1c "(PLP)"): its 95% block-bootstrap interval
    must lie in the closed band [0.8, 1.25] (pass), miss it (fail), or else the verdict is
    inconclusive, with the 50-state minimum (DEC-0008 A1, A3; DEC-0016 O3). The CP median and
    interval are reported with no verdict. A state is eligible when it has at least three
    events at the admissible thresholds, horizons above one step, positive growth and varying
    horizons; the others are counted (``n_ineligible_states``), as are the non-finite ratios
    (``n_excluded_nonfinite``). The bootstrap of both medians is ``h1c_ratio_block`` (generator
    labels ``(seed, system, "bootstrap", "H1c")``, WU-0002.14).

    Parameters
    ----------
    cell : Cell
        Core cell.
    config : StudyConfig
        Study configuration.
    capture : dict, optional
        If given (the opt-in state dump, WU-0003.7c), it is filled with references to arrays the
        function builds (the caller copies them, as ``StateDump.record_extra`` does): ``thresholds`` and, for
        ``PLP`` and ``CP``, ``<name>/ratio`` (the per-state ratio of every state, NaN where the
        state is not eligible) and ``<name>/eligible`` (bool): the ratios of the eligible states,
        in order, are the array that ``h1c_ratio_block`` receives. Nothing is computed for it and
        nothing flows back.

    Returns
    -------
    dict
        ``thresholds``; ``PLP`` and ``CP`` (``h1c_ratio_block`` plus ``n_ineligible_states``;
        ``verdict``, ``reason`` and ``pass`` for the PLP only); ``threshold`` [0.8, 1.25]; and
        the PLP ``verdict``, ``reason``, ``pass``, ``n_failed_resamples`` and ``n_states`` at
        the top level (DEC-0012: every criterion result carries them).
    """
    m = cell.splits["test"].moments
    growth = cell.oracles["test"].growth
    thetas = np.array(config.admissible_thresholds(cell.noise))
    res: dict = {"thresholds": thetas.tolist()}
    if capture is not None:
        capture["thresholds"] = thetas
    for name, mse in (("PLP", m.sq_plp), ("CP", m.sq_cp)):
        passages = [
            characteristic_horizon(mse, m.horizons, cell.noise, t) for t in thetas
        ]
        horizons = np.column_stack([horizon for horizon, _ in passages])
        events = np.column_stack([event for _, event in passages])
        ratios, eligible = [], np.zeros(len(horizons), dtype=bool)
        for i in range(len(horizons)):
            ok = events[i] & (horizons[i] > 1)
            if ok.sum() >= 3 and growth[i] > 0 and np.ptp(horizons[i][ok]) > 0:
                ratios.append(growth[i] * ols_slope(np.log(thetas[ok]),
                                                    horizons[i][ok].astype(float)))
                eligible[i] = True
        if capture is not None:
            per_state = np.full(len(horizons), np.nan)
            per_state[eligible] = ratios
            capture.update({f"{name}/ratio": per_state, f"{name}/eligible": eligible})
        res[name] = h1c_ratio_block(np.asarray(ratios), config, cell.system,
                                    with_verdict=name == "PLP")
        res[name]["n_ineligible_states"] = int(len(horizons) - len(ratios))
    res["threshold"] = list(H1C_BAND)
    res.update({key: res["PLP"][key]
                for key in ("verdict", "reason", "pass", "n_failed_resamples", "n_states")})
    return res


H1D_TESTED = ("analog_seed", "estimation_seed", "growth")
H1D_REPORTED = ("nhat",)


def h1d_correlations(pairs: dict[str, tuple[np.ndarray, np.ndarray]], system: str,
                     config: StudyConfig) -> dict:
    """H1d core: Spearman correlation of each proxy with its oracle, with bootstrap intervals.

    Each pair gets a 95% moving-block-bootstrap percentile interval of the Spearman correlation
    (resamples and block from ``config``: 2000 and 5 in the study), seeded by
    ``make_rng(config.seed, system, "bootstrap", "H1d", name)``. The three tested pairs
    (``analog_seed``, ``estimation_seed``, ``growth``) are each judged by their lower bound
    against ``[0.7, inf)`` (closed; DEC-0008 A1, v3 H1d); the whole is ``combine_verdicts`` of the
    three. The pair ``nhat`` (N-hat against N) is reported with its interval and **no verdict**
    (v3 sections 2 and 8). A pair is cleaned per row: states where either member is non-finite
    are excluded and counted, so a reported row with missing values never shrinks a tested one;
    a row with fewer than ``statistics.MIN_STATES`` (50) states, or a correlation that cannot be
    computed, is inconclusive (DEC-0008 A3), and failed resamples are counted.

    Parameters
    ----------
    pairs : dict[str, tuple[np.ndarray, np.ndarray]]
        ``(proxy, oracle)`` per name; the names are exactly ``analog_seed``, ``estimation_seed``,
        ``growth`` and ``nhat``; the arrays are 1-D of equal length, in time order.
    system : str
        System name (seed label).
    config : StudyConfig
        Study configuration (bootstrap settings, master seed).

    Returns
    -------
    dict
        ``rows`` (per name: ``spearman``, ``interval``, ``n_failed_resamples``, ``n_states``,
        ``n_excluded_nonfinite``, and for tested rows ``verdict`` and ``reason``), ``threshold``
        0.7, ``level``, ``n_states`` (the smallest of the tested rows), ``n_excluded_nonfinite``
        (the largest of the tested rows), ``verdict``, ``reason`` and ``pass``.

    Raises
    ------
    ValueError
        If the names are not the four above or a pair is not two 1-D arrays of equal length.
    """
    if set(pairs) != {*H1D_TESTED, *H1D_REPORTED}:
        raise ValueError(f"pairs must be exactly {[*H1D_TESTED, *H1D_REPORTED]}; "
                         f"got {sorted(pairs)}")
    rows: dict = {}
    for name in (*H1D_TESTED, *H1D_REPORTED):
        proxy, oracle = (np.asarray(v, dtype=float) for v in pairs[name])
        if proxy.ndim != 1 or proxy.shape != oracle.shape:
            raise ValueError(f"{name}: need two 1-D arrays of equal length; got "
                             f"{proxy.shape} and {oracle.shape}")
        keep = np.isfinite(proxy) & np.isfinite(oracle)
        a_values, b_values = proxy[keep], oracle[keep]
        n_states = len(a_values)
        if n_states >= 2:
            interval = block_bootstrap_counted(
                lambda idx: spearman(a_values[idx], b_values[idx]), n_states,
                config.bootstrap_resamples, config.bootstrap_block,
                make_rng(config.seed, system, "bootstrap", "H1d", name), H1_LEVEL)
            est, lo, hi, n_failed = interval.estimate, interval.lower, interval.upper, \
                interval.n_failed
        else:
            est = lo = hi = float("nan")
            n_failed = 0
        rows[name] = {"spearman": est, "interval": [lo, hi], "n_failed_resamples": int(n_failed),
                      "n_states": int(n_states),
                      "n_excluded_nonfinite": int(len(proxy) - n_states)}
        if name in H1D_TESTED:
            rows[name]["verdict"], rows[name]["reason"] = criterion_verdict(
                est, lo, hi, H1D_BAND, n_states=n_states)
    tested = [rows[name] for name in H1D_TESTED]
    verdict = combine_verdicts(row["verdict"] for row in tested)
    reason = "; ".join(f"{name}: {rows[name]['reason']}" for name in H1D_TESTED
                       if rows[name]["verdict"] == "inconclusive") \
        if verdict == "inconclusive" else None
    return {"rows": rows, "threshold": H1D_BAND[0], "level": H1_LEVEL,
            "n_states": min(row["n_states"] for row in tested),
            "n_excluded_nonfinite": max(row["n_excluded_nonfinite"] for row in tested),
            "verdict": verdict, "reason": reason, "pass": bool(verdict == "pass")}


def h1d_proxies(cell: Cell, rules: FittedRules, config: StudyConfig) -> dict:
    """H1d: Spearman correlation of each deployable proxy with its oracle, lower bound >= 0.7.

    Tested pairs (first evaluation draw): (eps-hat, eps_s), (delta-hat, delta),
    (Lambda-hat, Lambda-bar). Reported only, with an interval and no verdict: (N-hat, N), and
    the Spearman correlation of the estimation seed with ``rho nu`` (a plain number). See
    :func:`h1d_correlations`.

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
        The result of :func:`h1d_correlations` plus ``estimation_seed_vs_cramer_rao``.
    """
    split = cell.splits["test"]
    ev, m, o = split.evals, split.moments, cell.oracles["test"]
    eps_hat, delta_hat = rules.proxies.seeds(ev, cell.noise)
    pairs = {"analog_seed": (eps_hat[:, 0], m.analog_seed),
             "estimation_seed": (delta_hat[:, 0], m.est_seed),
             "growth": (ev.growth_proxy[:, 0], o.growth),
             "nhat": (ev.noise_sens[:, 0], m.noise_sens)}
    out = h1d_correlations(pairs, cell.system, config)
    out["estimation_seed_vs_cramer_rao"] = spearman(m.est_seed, cell.noise * o.nu)
    return out


def _oracle_profile(cell: Cell, split: str, config: StudyConfig) -> np.ndarray:
    """Oracle four-coordinate profile of a split (state level)."""
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


def _masked_logit(weight: np.ndarray, rows: np.ndarray) -> np.ndarray:
    """Logit of ``weight`` on ``rows``; 0.5 (logit 0) elsewhere, never read."""
    inner = np.where(rows, weight, 0.5)
    return np.log(inner / (1.0 - inner))


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
                     level: float = 0.95, capture: dict | None = None) -> dict:
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
    capture : dict, optional
        If given (the opt-in state dump, WU-0003.7b), it is filled with copies of what the
        function already computed: per target the two predictions on every test state (``pred3``
        and ``pred4``), the target ``y`` (placeholder 0.0 outside its domain) and the ``domain``
        mask, keyed ``<target>/<name>``. Nothing is computed for it and nothing flows back.

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

    interior_train = (w_train > 0.0) & (w_train < 1.0)
    interior_test = (w_test > 0.0) & (w_test < 1.0)
    everywhere_train = np.ones(len(w_train), bool)
    everywhere_test = np.ones(len(w_test), bool)
    targets = {
        "logit_w_interior": (interior_train, _masked_logit(w_train, interior_train),
                             interior_test, _masked_logit(w_test, interior_test)),
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
    if capture is not None:
        for name in names:
            _, _, rows_test, y_test = targets[name]
            capture.update({f"{name}/pred3": pred3[name], f"{name}/pred4": pred4[name],
                            f"{name}/y": y_test, f"{name}/domain": rows_test})
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


def qn_noise_redundancy(cell: Cell, rules: FittedRules, config: StudyConfig,
                        dump: StateDump | None = None) -> dict:
    """Q-N: is the fourth LPC (noise sensitivity) reducible to the other three?

    An estimate, not a pass/fail criterion (v3 section 7; DEC-0008 A4(a)). Nested out-of-sample
    comparison on the construction plus calibration states (training) and the test states, for
    the oracle profile (primary) and the deployable profile (secondary): see
    ``qn_profile_block`` for the three targets (interior logit of ``w*``, the indicator
    ``1{w* = 0}``, the log horizon), the intervals and the readings. The resamples are shared
    across targets and across the two profiles (a fresh ``make_rng(config.seed, system,
    "bootstrap", "Q-N")`` for each profile, WU-0002.14: a shared generator would advance).
    The counts of ``w* = 0`` and ``w* = 1`` over the test states are reported.

    Parameters
    ----------
    cell : Cell
        Core cell.
    rules : FittedRules
        Fitted rules (seed proxies for the deployable profile).
    config : StudyConfig
        Study configuration.
    dump : StateDump, optional
        The opt-in state dump (WU-0003.7b): receives copies of the test profile, the targets and
        the predictions of both models, per profile kind. It changes nothing computed here.

    Returns
    -------
    dict
        ``role`` ("estimate"), ``primary`` ("oracle"), ``n_w_zero``, ``n_w_one``, ``n_test``,
        and the blocks ``oracle`` and ``deployable`` of ``qn_profile_block``.
    """
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
        x_test = profiles(kind, "test")
        captured: dict | None = None if dump is None else {}
        out[kind] = qn_profile_block(
            x_train, x_test, w_train, w_test, log_t_train, log_t_test,
            seed=config.seed, n_resamples=config.bootstrap_resamples,
            block=config.bootstrap_block,
            boot_seed=make_rng(config.seed, cell.system, "bootstrap", "Q-N"), capture=captured)
        if dump is not None and captured is not None:
            dump.record_qn(cell.system, kind, {"x_test": x_test, "w_star": w_test,
                                               "log_t": log_t_test, **captured})
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
            "ci_mc_se": list(endpoint_mc_error(values[:, 0], level)),  # WU-0008.2a
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
    logit = _masked_logit(weight, interior)
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
                       "ci_mc_se": list(endpoint_mc_error(values[:, col], level)),  # WU-0008.2a
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
    system, label)`` (DEC-0012, WU-0002.14), both at level ``1 - 0.05/3``. H2a passes iff both parts pass and fails
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
        seed=make_rng(config.seed, cell.system, "h2a-initial-segments"), level=PRIMARY_LEVEL)
    out["median_range_unrestricted"] = float(np.median(np.ptp(w_star[:, cols], axis=1)))
    w_ref = w_star[:, m.at(config.reference_horizon)]
    seeds = np.column_stack([np.log(m.analog_seed / cell.noise),
                             np.log(m.est_seed / cell.noise)])
    lam = o.growth * lt
    out.update(h2a_part_ii(w_ref, lam, seeds, n_resamples=config.bootstrap_resamples,
                           block=config.bootstrap_block,
                           seed=make_rng(config.seed, cell.system, "h2a-two-part"),
                           level=PRIMARY_LEVEL))
    out["unconditional_spearman_w_lambda"] = spearman(w_ref, lam)
    out["short_horizon_range_median"] = float(np.median(np.ptp(
        w_star[:, [m.at(int(h * lt)) for h in config.eval_horizons_lyapunov]], axis=1)))
    out["verdict"] = combine_verdicts([out["part_i_verdict"], out["part_ii_verdict"]])
    out["threshold"] = ("(i) upper bound of the median range over initial segments (small-error "
                        "regime) < 0.1; (ii) each part's interval inside (-0.1, 0.1)")
    out["pass"] = bool(out["verdict"] == "pass")
    return out


def _per_state_spearman_counted(levels: np.ndarray, values: np.ndarray
                                ) -> tuple[np.ndarray, int]:
    """Spearman correlation of each row of ``values`` with ``levels``, and the constant rows.

    Ties (e.g. weights clipped to 0 at several levels) receive average ranks, so
    a state whose weight does not change across levels scores 0, not +1. That 0 is the tie
    convention that defines the H2b(i) estimand (it shrinks the mean toward 0 and cannot flip its
    sign); the states that get it, those with a zero rank denominator, are returned as an
    ``int`` count (DEF-0001, row N6; ``H2b.noise.n_constant_states``).

    The count is of ``not (denom > 0)``, which also includes a NaN denominator (``rankdata``
    propagates NaN, so a row with a non-finite weight would be scored 0 by ``np.where`` and must
    be counted too; ``denom == 0`` would leave it zeroed and uncounted). Such a row cannot occur
    today: the weights are ``oracle_weight`` of moments built from errors clipped at +-10, so they
    are finite (``h2b_knob_response`` takes them as they are).

    Returns
    -------
    tuple[np.ndarray, int]
        The per-state correlations and the number of states scored 0 by the convention.
    """
    ranks = rankdata(values, axis=1)
    lev = rankdata(levels)
    lev_c = lev - lev.mean()
    ranks_c = ranks - ranks.mean(axis=1, keepdims=True)
    denom = np.sqrt(np.sum(ranks_c**2, axis=1) * np.sum(lev_c**2))
    return (np.where(denom > 0, ranks_c @ lev_c / np.maximum(denom, 1e-300), 0.0),
            int((~(denom > 0)).sum()))


def _decision(verdict: str, reason: str | None) -> dict:
    """The ``verdict``, ``reason`` and ``pass`` keys of a result (DEC-0012, as in the H1 lane).

    ``verdict`` is "pass", "fail" or "inconclusive"; ``reason`` is the one given by
    ``criterion_verdict`` for an inconclusive result and None for a pass or a fail; ``pass`` is
    ``verdict == "pass"``.
    """
    return {"verdict": verdict, "reason": reason, "pass": verdict == "pass"}


def _combined_decision(parts: dict[str, tuple[str, str | None]]) -> dict:
    """``verdict``, ``reason`` and ``pass`` of a criterion with several named parts.

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
                   labels: tuple[str, ...], name: str, statistic: str = "mean",
                   mc_error: bool = False) -> tuple[dict, str, str | None]:
    """Bootstrap interval of the mean or median of per-state paired differences ``high - low``.

    One index array (the moving-block resample of states) serves both cells, and the
    generator is ``make_rng(config.seed, *labels)`` (DEC-0012; the callers' labels start with the
    system, WU-0002.14). Failed (non-finite)
    resamples are counted at the unfavourable tail (DEC-0008 A3). With ``mc_error`` the result
    also carries ``ci_mc_se`` (``statistics.endpoint_mc_error`` on the same resample values;
    WU-0008.2a: set only for the primary H2b(ii)); estimate and interval are those of
    ``block_bootstrap_counted``, whose body is called here (``bootstrap_values`` then
    ``percentile_interval``, bitwise the same).

    Returns
    -------
    tuple[dict, str, str | None]
        ``{<name>, ci, level, n_states, n_failed_resamples, n_zero_difference}`` (and
        ``ci_mc_se`` with ``mc_error``), then the
        verdict and the reason of the criterion "lower bound > 0" (strict, DEC-0008 A1) from
        ``criterion_verdict``.
    """
    if low.shape != high.shape or low.ndim != 1:
        raise ValueError(f"paired cells must hold the same states; got {low.shape}, {high.shape}")
    diff = high - low
    centre = np.mean if statistic == "mean" else np.median
    point, values = bootstrap_values(lambda idx: float(centre(diff[idx])), len(diff),
                                     config.bootstrap_resamples, config.bootstrap_block,
                                     make_rng(config.seed, *labels))
    lower, upper, n_failed = percentile_interval(values, level)
    verdict, reason = criterion_verdict(float(point), lower, upper, (0.0, np.inf),
                                        (False, True), n_states=len(diff))
    out = {name: float(point), "ci": [lower, upper], "level": level,
           "n_states": int(len(diff)), "n_failed_resamples": n_failed,
           "n_zero_difference": int(np.count_nonzero(diff == 0.0))}
    if mc_error:
        out["ci_mc_se"] = list(endpoint_mc_error(values, level))
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
      with ``rho``; the interval is at level ``1 - 0.05/3`` (WU-0002.14: new generator), pass iff its lower
      bound is above 0 (strict), fail iff the whole interval is at or below 0, else inconclusive
      (``criterion_verdict``, including the 50-state guard). Two counts sit beside it (DEF-0001;
      report only, no treatment changes): ``n_constant_states``, the states scored 0 because their
      weight is the same at every level (a zero rank denominator; the tie convention,
      conservative for "> 0": it shrinks the mean toward 0; at pilot size 20-40% of the states
      have ``w* = 0`` at every level; the count would also include a non-finite row, which cannot
      occur since the weights are finite), and
      ``n_failed_resamples``, the non-finite resamples, which ``block_bootstrap_counted`` places
      at the unfavourable tail (DEC-0008 A3; DEF-0019, WU-0002.9b): at the threshold
      ``floor((B - 1) a) + 1`` both bounds are infinite and the verdict is inconclusive (a mean of
      finite correlations cannot fail, so 0 is expected). The generator is
      ``make_rng(config.seed, system, "bootstrap", "H2b-noise")`` (WU-0002.14). ``n_dropped_resamples`` is kept as an alias with the same value (a published key
      since WU-0002.11b; nothing is dropped any more).
    * (ii) ``library_change``: the mean over states of ``w*_i(H_ref, 10^4) - w*_i(H_ref, 10^3)``
      at ``rho = config.core_noise`` (1%), one block-bootstrap index array for both sizes, level
      ``1 - 0.05/3``, pass iff the lower bound is above 0 (strict; DEC-0008 A1). A missing cell
      gives ``mean_change = None``, an inconclusive verdict and the missing cells in
      ``reason``; an interval with the lower bound at or below 0, or with failed
      resamples at or above the threshold, is inconclusive (DEC-0008 A3).
    * The verdict is ``combine_verdicts`` of (i) and (ii) (v3 section 7: one fail fails it; the
      reason lists the inconclusive parts), ``pass`` is ``verdict == "pass"``.

    Reported only, at 95% (v3 section 7, Methods v2 M2 section M12): ``library_curves``, the mean
    and the median of ``w*(H_ref)`` with intervals for every ``n_lib`` at every
    ``rho`` of the library sweep (the M2 curve; all sizes share each resample), and
    ``library_change_reported``, the 10^3 to 10^4 change at every other ``rho`` of the sweep
    (``0.02``). The per-``rho`` library Spearman and the saturation rule of v1
    (median w* at the largest ``n_lib`` below 0.95) are gone (D-05; M2 section M14).

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
        ``threshold``, ``verdict``, ``reason`` and ``pass``.
    """
    res: dict = {}
    system = noise_cells[min(noise_cells)].system
    rho_levels = np.array(sorted(noise_cells))
    w_rho = np.column_stack([_split_weights(noise_cells[r], config) for r in rho_levels])
    rho_corr, n_constant = _per_state_spearman_counted(rho_levels, w_rho)
    # the body of block_bootstrap_counted, to keep the resample values for ci_mc_se
    point, noise_values = bootstrap_values(
        lambda idx: float(np.mean(rho_corr[idx])), len(rho_corr), config.bootstrap_resamples,
        config.bootstrap_block, make_rng(config.seed, system, "bootstrap", "H2b-noise"))
    lo, hi, noise_failed = percentile_interval(noise_values, PRIMARY_LEVEL)
    est = float(point)
    medians = np.median(w_rho, axis=0)
    res["noise"] = {"median_w_by_noise": dict(zip(map(str, rho_levels), medians.tolist())),
                    "mean_state_spearman": est, "ci": [lo, hi],
                    "ci_mc_se": list(endpoint_mc_error(noise_values, PRIMARY_LEVEL)),  # WU-0008.2a
                    "monotone_medians": bool(np.all(np.diff(medians) > 0)),
                    "n_constant_states": n_constant, "n_failed_resamples": int(noise_failed),
                    "n_dropped_resamples": int(noise_failed)}
    noise_verdict, noise_reason = criterion_verdict(est, lo, hi, (0.0, np.inf), (False, True),
                                                    n_states=len(rho_corr))
    res["noise"].update(_decision(noise_verdict, noise_reason))

    rho = config.core_noise
    wanted = [(rho, n) for n in H2B_LIBRARY_SIZES]
    missing = _missing_cells(library_cells, wanted)
    fields, verdict, reason = _unavailable(PRIMARY_LEVEL, missing, "mean_change") if missing \
        else _paired_change(*(_split_weights(library_cells[key], config) for key in wanted),
                            config, PRIMARY_LEVEL, (system, "h2b-library-change", f"{rho:g}"),
                            "mean_change", mc_error=True)
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
            make_rng(config.seed, system, "h2b-curves", f"{other:g}"))
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
                (system, "h2b-library-change", f"{other:g}"), "mean_change")
            res["library_change_reported"][f"{other:g}"] = {
                **fields, "role": "reported", "unavailable_reason": (
                    "missing cell(s): " + ", ".join(gone)) if gone else None}
    res["threshold"] = ("(i) per-state Spearman of w* with rho: CI lower bound > 0; (ii) mean "
                        "paired change in w*(H_ref) from n_lib 10^3 to 10^4 at rho = 1%: CI lower "
                        "bound > 0 (both at level 1 - 0.05/3)")
    res.update(_combined_decision({
        "noise": (res["noise"]["verdict"], res["noise"]["reason"]),
        "library_change": (res["library_change"]["verdict"], res["library_change"]["reason"])}))
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
    exactly 0, which is inconclusive; that is intended. The bootstrap generator is
    ``make_rng(config.seed, system, "h2e", f"{rho:g}")`` (WU-0002.14). Any cell missing for a ``rho``
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
        ``n_failed_resamples``, ``n_zero_difference``, ``verdict``, ``reason``, ``pass``),
        ``corr_curve[rho][n_lib]`` (median correlation for every available cell),
        ``zero_variance_corr[rho][n_lib]``, ``threshold``, ``verdict``, ``reason``, ``pass``.

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
                                (library_cells[wanted[0]].system, "h2e", f"{rho:g}"),
                                "median_change", "median")
        by_noise[f"{rho:g}"] = {**fields, **_decision(verdict, reason)}
        parts[f"rho={rho:g}"] = (verdict, reason)
    out["by_noise"] = by_noise
    out["threshold"] = ("median per-state change in CP-PLP error correlation at H_ref, n_lib 10^3 "
                        "to 10^5: 95% CI lower bound > 0 at rho = 1% and 2%")
    out.update(_combined_decision(parts))
    return out


def h2c_state_dependence(scores: dict[str, RuleScores], calibration: SplitData,
                         config: StudyConfig, system: str) -> dict:
    """H2c: A4 has lower MSE at ``H_ref`` than A2 and than the better single forecaster.

    The better single forecaster is chosen on the calibration split, not on the test data that
    the differences are computed on (DEC-0008 A4(i)): the realized MSE at ``H_ref`` of A0 (CP
    alone) and A1 (PLP alone) on the calibration split's evaluation draws, against the
    noise-free truth, the same definition as on test; a tie goes to A0. The two values are
    reported as ``calibration_mse``. The entry ``A4o_minus_A2`` (A4 with the oracle seeds against
    A2; reported only, no pass; D-20) is the paired mean difference of the per-state squared
    errors at ``H_ref``, 95%, on the same states and the same resamples as the other differences
    (each part draws from its own fresh ``make_rng(config.seed, system, "bootstrap", "H2c")``,
    so the index arrays are identical; a shared generator would advance); it is a new bootstrap, so it goes through
    ``block_bootstrap_counted`` and reports ``n_failed_resamples`` (DEC-0012; bitwise equal to
    ``block_bootstrap`` when no resample fails).

    Each decided part goes through ``block_bootstrap_counted`` with that generator (failed
    resamples are counted and widen the interval). Its verdict is ``criterion_verdict`` against the band
    ``(-inf, 0)`` with the upper edge open (DEC-0008 A1: a difference whose upper bound is 0
    is not below 0, so it fails), at 95% and with the 50-state minimum. The criterion is
    ``combine_verdicts`` of the two parts (v3 section 7). The top-level ``n_failed_resamples``
    is the larger of the two parts' counts (the parts share the same resamples).

    Parameters
    ----------
    scores : dict[str, RuleScores]
        Test-split scores.
    calibration : SplitData
        Calibration split of the core cell, with evaluation draws (only ``evals.cp_err`` and
        ``evals.plp_err`` at ``H_ref`` are read).
    config : StudyConfig
        Study configuration.
    system : str
        System name (a label of the bootstrap generator, WU-0002.14; the bootstrap seed of a
        verdict statistic: needs owner review before freeze).

    Returns
    -------
    dict
        ``best_single``, ``calibration_mse``, the mean paired differences with intervals
        (``A4_minus_A2``, ``A4_minus_<best>``, each with ``n_failed_resamples``, ``verdict``,
        ``reason`` and ``pass``; ``A4o_minus_A2`` reported only), and the criterion's
        ``verdict``, ``reason``, ``pass`` and ``n_failed_resamples``.

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
        boot = block_bootstrap_counted(lambda idx: float(np.mean(diff[idx])), len(diff),
                                       config.bootstrap_resamples, config.bootstrap_block,
                                       make_rng(config.seed, system, "bootstrap", "H2c"),
                                       H1_LEVEL)
        verdict, reason = criterion_verdict(boot.estimate, boot.lower, boot.upper, H2C_BAND,
                                            H2C_CLOSED, n_states=len(diff))
        out[f"A4_minus_{other}"] = {
            "mean": boot.estimate, "ci": [boot.lower, boot.upper],
            "relative": boot.estimate / float(scores[other].state_mse_ref.mean()),
            "n_failed_resamples": boot.n_failed, **_decision(verdict, reason)}
    parts = {name: out[name] for name in ("A4_minus_A2", f"A4_minus_{best_single}")}
    out.update(_combined_decision({name: (part["verdict"], part["reason"])
                                   for name, part in parts.items()}))
    out["n_failed_resamples"] = max(part["n_failed_resamples"] for part in parts.values())
    diff_o = scores["A4o"].state_mse_ref - scores["A2"].state_mse_ref
    boot = block_bootstrap_counted(lambda idx: float(np.mean(diff_o[idx])), len(diff_o),
                                   config.bootstrap_resamples, config.bootstrap_block,
                                   make_rng(config.seed, system, "bootstrap", "H2c"), 0.95)
    out["A4o_minus_A2"] = {"mean": boot.estimate, "ci": [boot.lower, boot.upper], "level": 0.95,
                           "n_failed_resamples": boot.n_failed,
                           "relative": boot.estimate / float(scores["A2"].state_mse_ref.mean()),
                           "role": "reported"}
    return out


def h2d_empirical_comparison(scores: dict[str, RuleScores], config: StudyConfig,
                             system: str) -> dict:
    """H2d: A4 within 10% of A3 in-distribution (part (ii) is removed in v3).

    The statistic is ``mean(A4) / mean(A3) - 1`` over states. The verdict is the 95%
    block-bootstrap interval (``make_rng(config.seed, system, "bootstrap", "H2d")``) against the band
    ``(-inf, 0.10]``, closed at 0.10 (v3 H2d: "upper bound <= 0.10"; DEC-0008 A1; DEC-0011 O4 is
    lifted by WU-0002.9): pass if the upper bound is at most 0.10, fail if the lower bound is
    above it, else inconclusive, with the 50-state minimum. Failed resamples are counted and
    widen the interval. No single resample value can
    equal 0.10 (for a result near 0.1 the subtraction is exact on a multiple of ``2**-52``,
    which 0.1 is not), but the interpolated percentile bound can, so the edge is a live case.

    Parameters
    ----------
    scores : dict[str, RuleScores]
        Core test scores.
    config : StudyConfig
        Study configuration.
    system : str
        System name (a label of the bootstrap generator, WU-0002.14; the bootstrap seed of a
        verdict statistic: needs owner review before freeze).

    Returns
    -------
    dict
        ``in_distribution_excess``, ``ci``, ``n_failed_resamples``, ``verdict``, ``reason`` and
        ``pass``.
    """
    a3, a4 = scores["A3"].state_mse_ref, scores["A4"].state_mse_ref
    boot = block_bootstrap_counted(lambda idx: float(a4[idx].mean() / a3[idx].mean() - 1.0),
                                   len(a3), config.bootstrap_resamples, config.bootstrap_block,
                                   make_rng(config.seed, system, "bootstrap", "H2d"), H1_LEVEL)
    verdict, reason = criterion_verdict(boot.estimate, boot.lower, boot.upper, H2D_BAND,
                                        (True, True), n_states=len(a3))
    return {"in_distribution_excess": boot.estimate, "ci": [boot.lower, boot.upper],
            "n_failed_resamples": boot.n_failed, **_decision(verdict, reason)}


def gain_horizon_bound(cell: Cell, config: StudyConfig) -> dict:
    """Gain bound: hybrid horizon gain over the better forecaster <= ``ln 2 / (2 Lambda_bar)``.

    Reported against the P1 bound with no pass/fail bar (v3 section 2; concordance D-21(a)), so
    there is no ``pass`` and no ``threshold``. Evaluated on states with positive growth,
    uncensored single-forecaster horizons and nonnegative error covariance at the better
    forecaster's crossing. The number of states each screen excludes is reported next to
    ``n_states`` (``n_screened_out``; the screens overlap, so each count is over all
    ``n_total_states``, and a state may be in several). The screen is the v1 one: the covariance
    screen is centered and at one horizon, and the subset that satisfies P1's hypotheses at every
    horizon is not computed (concordance D-21(b), (c); the report row stays marked pending).

    Parameters
    ----------
    cell : Cell
        Core cell.
    config : StudyConfig
        Study configuration.

    Returns
    -------
    dict
        Fraction of states within the bound (+1 step discretization tolerance), ``n_states``
        (those that pass every screen), ``n_total_states``, ``n_screened_out``
        (``growth_nonpositive``, ``censored_single_forecaster``, ``negative_covariance``;
        a NaN covariance counts as negative) and the median and maximum gain in Lyapunov times.
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
            "n_total_states": int(len(growth)),
            "n_screened_out": {"growth_nonpositive": int((~(growth > 0)).sum()),
                               "censored_single_forecaster": int((~(ev_cp & ev_plp)).sum()),
                               "negative_covariance": int((~(cov >= 0)).sum())},
            "median_gain_lyapunov": float(np.median(gain)) / config.steps_per_lyapunov
            if gain.size else float("nan"),
            "max_gain_lyapunov": float(np.max(gain)) / config.steps_per_lyapunov
            if gain.size else float("nan")}


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
    horizon (NaN, a median not reached, mapped to infinity so that it comes last; the number of
    such regimes is reported as ``n_km_not_reached``) with ``np.argsort(kind="stable")``, so a tie
    is ordered by regime index and the pairs do not depend on the CPU (DEF-0013). The family is
    all ``K_real - 1`` consecutive pairs. A pair with an empty regime or with zero log-rank
    variance (``logrank_parts``) is not computed: its raw p is ``None`` and it enters the Holm
    family at p = 1 (conservative; DEC-0011 O1). No minimum number of states per regime is
    imposed (DEC-0011 O1), but the full sample (the test states) needs at least ``MIN_STATES`` = 50
    (DEC-0008 A3), else the result is inconclusive with the reason ``"n_states < 50"``. ``pass`` needs
    every pair computed and every adjusted p < 0.01
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
        not computed), ``logrank_p_holm``, ``n_per_regime``, ``n_events_per_regime`` and
        ``n_censored_per_regime`` (per regime, in regime-index order, on the same first-draw
        states and event flags as the test; events plus censored equals ``n_per_regime``; reported
        beside the p-values because the test sets no minimum per regime and a regime with one event
        can give an extreme p, DEF-0018, ruling B6b; they enter no decision), ``n_km_not_reached``,
        ``n_empty_regimes`` (regimes with no test state; independent of ``n_km_not_reached``, which
        counts the regimes whose Kaplan-Meier median, from the calibration split, is not reached), ``n_degenerate_pairs`` (pairs not computed because
        the log-rank variance is 0; ``logrank_test`` would return p = 1 for them, DEF-0001 row T2;
        a pair with an empty regime is not counted here), ``iqr_lt`` (interquartile range of
        the characteristic horizon in Lyapunov times per regime, None below 2 states),
        ``iqr_lt_mean`` (their mean weighted by regime size, the v1 ``mean_iqr_lyapunov``; None
        if no regime has 2 states), ``threshold``, ``verdict``, ``reason``, ``pass``.
    """
    n_regimes = len(horizons_km)
    n_states = len(first_regime)
    counts = [int(np.sum(first_regime == k)) for k in range(n_regimes)]
    # WU-0004d (DEF-0018, owner ruling B6b): the events and the censored states of each regime,
    # beside the p-values. Read-only: nothing below uses them.
    events_per_regime = [int(np.count_nonzero(events[first_regime == k])) for k in range(n_regimes)]
    censored_per_regime = [c - e for c, e in zip(counts, events_per_regime)]
    iqr: list[float | None] = []
    for k in range(n_regimes):
        members = first_regime == k
        if members.sum() >= 2:
            q75, q25 = np.percentile(horizon_target[members] / lt, [75, 25])
            iqr.append(float(q75 - q25))
        else:
            iqr.append(None)
    n_empty_regimes = int(sum(c == 0 for c in counts))
    spread = [(v, c) for v, c in zip(iqr, counts) if v is not None]
    iqr_mean = float(np.average([v for v, _ in spread], weights=[c for _, c in spread])) \
        if spread else None

    order = np.argsort(np.nan_to_num(horizons_km, nan=np.inf), kind="stable")
    pairs = [(int(a), int(b)) for a, b in zip(order[:-1], order[1:])]
    raw: list[float | None] = []
    why: list[str] = []
    n_degenerate_pairs = 0
    for a, b in pairs:
        in_a, in_b = first_regime == a, first_regime == b
        if not (in_a.any() and in_b.any()):
            raw.append(None)
            why.append(f"pair ({a}, {b}): empty regime")
        elif logrank_parts(durations[in_a], events[in_a], durations[in_b], events[in_b])[1] <= 0:
            raw.append(None)
            why.append(f"pair ({a}, {b}): zero log-rank variance")
            n_degenerate_pairs += 1
        else:
            raw.append(logrank_test(durations[in_a], events[in_a], durations[in_b], events[in_b]))
    adjusted = holm_adjust([1.0 if p is None else p for p in raw]) if pairs else []
    decided = bool(pairs) and not why
    if n_states < MIN_STATES:  # the full-sample minimum of DEC-0008 A3 (DEC-0011 O1)
        verdict, reason = "inconclusive", f"n_states < {MIN_STATES}"
    elif decided and max(adjusted) < H3A_ALPHA:
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
            "n_events_per_regime": events_per_regime, "n_censored_per_regime": censored_per_regime,
            "n_km_not_reached": int(np.isnan(horizons_km).sum()),
            "n_empty_regimes": n_empty_regimes, "n_degenerate_pairs": n_degenerate_pairs,
            "iqr_lt": iqr,
            "iqr_lt_mean": iqr_mean,
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
                    t_target: np.ndarray, config: StudyConfig, system: str) -> dict:
    """H3b: impurity importances of ``Lambda_tilde`` in a weight tree and a horizon tree.

    Two regression trees with ``max_leaf_nodes = 8`` (DEC-0008 A3, A4(e); fixed so that the
    estimand does not depend on the data-chosen K) are fitted on the construction states'
    deployable profiles: the weight tree to ``w*(H_ref)`` with the curvature ``c`` at ``H_ref`` as
    sample weight (Theorem P3(a): the curvature-weighted regret), the horizon tree to ``ln T``
    (unweighted). The ``E`` evaluation draws of a state share its target. The point estimate is
    the full-data fit.

    The interval is a moving-block bootstrap (blocks of ``config.bootstrap_block`` consecutive
    construction states, ``config.bootstrap_resamples`` resamples, 95%,
    ``make_rng(config.seed, system, "h3b-bootstrap")``) in which all draws of a state stay together and
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
    system : str
        System name (a label of the bootstrap generator, WU-0002.14; the bootstrap seed of a
        verdict statistic: needs owner review before freeze).

    Returns
    -------
    dict
        ``weight_lambda``, ``D``, ``stability``, ``weight_tree_importance`` and
        ``horizon_tree_importance`` (full-data vectors by coordinate, None if degenerate),
        ``degenerate_fits``, ``nan_resamples``, ``n_states``, ``n_resamples``,
        ``max_leaf_nodes``, ``threshold``, ``verdict``, ``reason`` and ``pass``.

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
                                     config.bootstrap_block,
                                     make_rng(config.seed, system, "h3b-bootstrap"))
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


def h3c_ratio(a5_state_mse: np.ndarray, a4_state_mse: np.ndarray, config: StudyConfig,
              system: str) -> dict:
    """H3c (primary): the regimes' MSE over the closed form's, ``mean(A5) / mean(A4)`` at ``H_ref``.

    A ratio of means with the same block-bootstrap index array in the numerator and the
    denominator (paired on states), level ``1 - 0.05/3``, ``make_rng(config.seed, system, "h3c-ratio")``.
    Pass iff the upper bound is at most 1.05 (closed; DEC-0008 A1). Failed resamples are
    counted (DEC-0008 A3). The interval conditions on the fitted A4 and A5.

    Parameters
    ----------
    a5_state_mse, a4_state_mse : np.ndarray
        Per-state realized squared error at ``H_ref`` of A5 and A4, ``(n,)``.
    config : StudyConfig
        Study configuration.
    system : str
        System name (a label of the bootstrap generator, WU-0002.14; the bootstrap seed of a
        verdict statistic: needs owner review before freeze).

    Returns
    -------
    dict
        ``A5_over_A4_mse``, ``ci``, ``level``, ``n_states``, ``n_failed_resamples``,
        ``threshold``, ``verdict``, ``reason`` and ``pass``.
    """
    if a5_state_mse.shape != a4_state_mse.shape or a5_state_mse.ndim != 1:
        raise ValueError(f"need two (n,) arrays; got {a5_state_mse.shape}, {a4_state_mse.shape}")
    # the body of block_bootstrap_counted (same seed, bitwise the same), to keep the values
    point, values = bootstrap_values(
        lambda idx: float(a5_state_mse[idx].mean() / a4_state_mse[idx].mean()),
        len(a5_state_mse), config.bootstrap_resamples, config.bootstrap_block,
        make_rng(config.seed, system, "h3c-ratio"))
    lower, upper, n_failed = percentile_interval(values, PRIMARY_LEVEL)
    verdict, reason = criterion_verdict(float(point), lower, upper,
                                        (-np.inf, H3C_BOUND), (True, True),
                                        n_states=len(a5_state_mse))
    return {"A5_over_A4_mse": _finite_or_none(float(point)), "ci": [lower, upper],
            "ci_mc_se": list(endpoint_mc_error(values, PRIMARY_LEVEL)),  # WU-0008.2a
            "level": PRIMARY_LEVEL, "n_states": int(len(a5_state_mse)),
            "n_failed_resamples": n_failed, "threshold": H3C_BOUND,
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
        np.log(state_horizon_target(con.moments, cell.noise, config.primary_threshold)), config,
        cell.system)

    h3c = h3c_ratio(scores["A5"].state_mse_ref, scores["A4"].state_mse_ref, config, cell.system)
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
