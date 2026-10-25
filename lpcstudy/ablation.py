"""Ablation estimate rows of the follow-on study (WU-0039b): no verdicts.

Two ablations are computed for each core system, at the core cell (``rho =
1%``, ``n_lib = 10^4``) and ``H_ref``. They are estimates, read by tables, never
passed or failed (pre-registration draft of 2026-10-25, sections 6 and 7).

* **(a) The A4 coefficients.** A4's weight is ``w = delta_hat^2 / (eps_hat^2 +
  delta_hat^2)`` with ``eps_hat^2 = a (R nu)^2 + b (rho nu)^2`` and
  ``delta_hat^2 = a' (rho nu)^2 + b' rho^2`` (``allocation.ProfileProxies``).
  Each coefficient is removed in two ways: set to 0 with the other three at
  their fit (``zero``), or its term dropped and its partner refitted by the
  same robust log-scale least squares (``refit``, ``allocation.log_scale_fit``).
  Each variant is scored exactly as A4 is (``pipeline.score_rules`` on the
  test evaluation draws), and ``r = MSE(variant) / MSE(A4)`` at ``H_ref`` gets
  a paired moving-block bootstrap interval, as H3c.
* **(b) The profile conditions R, O, I, N** (the four coordinates of the
  profile), by the Q-N procedure (``analysis.qn_profile_block``): the same
  regressor and hyperparameters, the same training and test splits, models
  held fixed in the resamples, and resample index sets shared with Q-N and
  across targets and rows. (b1) is the leave-one-out ``Delta R^2_X``, (b2) the
  Shapley share over the 16 subsets, and (b3) A5 refitted without ``X``.

The levels are module constants so that the pending rulings (M-3, M-4 of the
pre-registration draft) can change them in one place. ``PROFILE_LEVEL`` must
stay equal to the Q-N level for the drop-N row to reproduce Q-N bitwise.

Randomness: the bootstrap generators of (a) and (b3) are new ``make_rng``
labels, ``(seed, system, "bootstrap", "ablation-A4")`` and ``(..., "ablation-
A5")``; (b1) and (b2) use Q-N's label ``(seed, system, "bootstrap", "Q-N")``
on purpose, as a fresh generator, so they draw Q-N's resamples. The regressors
use ``qn_regressor(seed)`` and the trees ``fit_regime_tree``'s seed, as in
production. No existing stream is consumed or moved.

Handled cases are counted, never silent: weights whose denominator ``eps_hat^2
+ delta_hat^2`` is below the ``1e-300`` floor of ``closed_form_weight``
(``n_floored``; the weight there is 0, PLP), failed resamples
(``n_failed_resamples``), empty regimes (``n_empty_regimes``). These keys are
copied into ``handling.result_counts`` by ``experiments.collect_result_counts``.
"""

from __future__ import annotations

import time
from dataclasses import replace
from itertools import combinations
from math import factorial

import numpy as np

from .allocation import (
    ProfileProxies,
    SeedProxy,
    closed_form_floor_count,
    closed_form_weight,
    deployable_profile,
    log_scale_fit,
    state_horizon_target,
)
from .analysis import (
    QN_PROFILES,
    _qn_reading_reason,
    _r2,
    qn_data,
    qn_regressor,
    qn_targets,
)
from .config import StudyConfig
from .data import make_rng
from .oracle import oracle_weight
from .pipeline import Cell, FittedRules, RuleScores, SplitData, fit_regime_maps
from .pipeline import score_rules
from .statistics import (
    MIN_STATES,
    bootstrap_values,
    endpoint_mc_error,
    percentile_interval,
)

A4_LEVEL: float = 1.0 - 0.05 / 3.0
"""Interval level of ablation (a) (pre-registration draft section 6.1, M-3)."""
A5_LEVEL: float = 1.0 - 0.05 / 3.0
"""Interval level of row (b3), A5 without ``X`` (section 7.2, M-3)."""
PROFILE_LEVEL: float = 0.95
"""Interval level of rows (b1) and (b2); the Q-N level, so drop-N is Q-N."""
RATIO_MARGIN: float = 1.05
"""Margin of the MSE-ratio reading table (H3c's band; M-2, closed as in H3c)."""
IDENTIFIABLE_CHANGE: float = 1e-6
"""Boundary rule of M-2 (WU-0041b): if zeroing a coefficient in the full A4
changes no test weight by more than this, both of its rows read "not
identifiable" (the coefficient is fitted at the boundary).

``exp(x)`` never reaches 0, so a coefficient the data do not support comes out
as a small positive number (WU-0036: ``b`` at 1e-16 to 1e-7, max weight change
at most 8.4e-8; non-boundary ``b'`` 2.4e-3 to 1.3e-2). A weight change of 1e-6
moves ``r`` by about 1e-5 at most.
"""
UNDEFINED_FLOOR: float = 1e-300
"""The floor of ``closed_form_weight``: a denominator below it is undefined."""

COEFFICIENTS: dict[str, tuple[str, str]] = {
    "a": ("analog", "slope"),
    "b": ("analog", "floor"),
    "a_prime": ("estimation", "slope"),
    "b_prime": ("estimation", "floor"),
}
"""The A4 coefficients: (``ProfileProxies`` proxy, ``SeedProxy`` field)."""
MODES: tuple[str, str] = ("zero", "refit")
"""The two ways of removing a coefficient."""
CONDITIONS: tuple[str, ...] = ("R", "O", "I", "N")
"""The four profile coordinates, in profile column order."""
EMPTY_SUBSET: str = "none"
"""Key of the empty subset (the training-mean predictor) in ``r2_by_subset``."""


# --------------------------------------------------------------- the readings
def ratio_reading(lower: float, upper: float) -> str:
    """Reading of an MSE-ratio interval by the table of M-2 (WU-0041b).

    This is section 6.2 of the pre-registration draft as revised by the
    applied-mathematician (closed comparisons at ``RATIO_MARGIN``, as in H3c;
    "substantial" needs a lower bound above the margin). Rows are checked top
    to bottom, on the unrounded float64 bounds:

    * a NaN or infinite bound: ``"undetermined"``;
    * upper bound < 1: ``"lowers"`` (removing the term lowers the MSE);
    * lower bound <= 1 and upper bound <= 1.05: ``"negligible"`` (at this
      precision);
    * lower bound > 1 and upper bound <= 1.05: ``"small"`` (the term is needed,
      but its contribution is small);
    * lower bound > 1.05: ``"substantial"``;
    * lower bound > 1 and upper bound > 1.05: ``"needed, size not
      determined"``;
    * otherwise: ``"undetermined"``.

    The 50-state rule and the boundary rule of ablation (a) come first; see
    :func:`ratio_reading_reason`.

    Parameters
    ----------
    lower, upper : float
        Interval bounds.

    Returns
    -------
    str
        One of the six readings.
    """
    if not (np.isfinite(lower) and np.isfinite(upper)):
        return "undetermined"
    if upper < 1.0:
        return "lowers"
    if lower <= 1.0 and upper <= RATIO_MARGIN:
        return "negligible"
    if lower > 1.0 and upper <= RATIO_MARGIN:
        return "small"
    if lower > RATIO_MARGIN:
        return "substantial"
    if lower > 1.0:
        return "needed, size not determined"
    return "undetermined"


def ratio_reading_reason(
    lower: float,
    upper: float,
    n_states: int,
    identifiable: bool = True,
) -> tuple[str, str | None]:
    """Ratio reading with its guards, in the order of M-2.

    First fewer than 50 states, a NaN bound or an infinite bound (failed
    resamples) read "undetermined" with the reason; then a coefficient fitted
    at the boundary (``identifiable`` False, ablation (a) only) reads "not
    identifiable"; then :func:`ratio_reading`.
    """
    if n_states < MIN_STATES:
        return "undetermined", f"n_states < {MIN_STATES}"
    if np.isnan(lower) or np.isnan(upper):
        return "undetermined", "not computable"
    if np.isinf(lower) or np.isinf(upper):
        return "undetermined", "failed resamples >= threshold"
    if not identifiable:
        return "not identifiable", "fitted at the boundary"
    return ratio_reading(lower, upper), None


def _finite(value: float) -> float | None:
    """Return ``value``, or ``None`` if it is not finite (JSON has no NaN)."""
    return float(value) if np.isfinite(value) else None


def ratio_rows(
    variant_mse: dict[str, np.ndarray],
    base_mse: np.ndarray,
    level: float,
    n_resamples: int,
    block: int,
    rng: np.random.Generator,
    identifiable: dict[str, bool] | None = None,
) -> dict[str, dict]:
    """MSE ratios of several variants to a base rule, with paired intervals.

    The statistic of a variant is ``mean(variant[idx]) / mean(base[idx])``,
    the form of H3c, with one index array for numerator and denominator
    (paired on states). All variants are one vector statistic, so they share
    the resamples. A non-finite resample is failed and counted
    (``percentile_interval``).

    Parameters
    ----------
    variant_mse : dict[str, np.ndarray]
        Per-state squared error at ``H_ref`` of each variant, shape ``(n,)``.
    base_mse : np.ndarray
        The same for the base rule (A4 or A5).
    level : float
        Interval level.
    n_resamples, block : int
        Bootstrap resamples and block length.
    rng : np.random.Generator
        Generator of the resample indices (consumed).
    identifiable : dict[str, bool], optional
        Per variant, False if the boundary rule of M-2 applies (the row then
        reads "not identifiable"); default True for every variant.

    Returns
    -------
    dict[str, dict]
        Per variant: ``mse_ratio``, ``ci``, ``ci_mc_se``,
        ``n_failed_resamples``, ``mse_href``, ``reading`` and ``reason``.
    """
    names = list(variant_mse)

    def stat(idx: np.ndarray) -> np.ndarray:
        denominator = base_mse[idx].mean()
        return np.array(
            [variant_mse[k][idx].mean() / denominator for k in names]
        )

    point, values = bootstrap_values(
        stat, len(base_mse), n_resamples, block, rng
    )
    out = {}
    for col, name in enumerate(names):
        lower, upper, n_failed = percentile_interval(values[:, col], level)
        reading, reason = ratio_reading_reason(
            lower,
            upper,
            len(base_mse),
            True if identifiable is None else identifiable[name],
        )
        out[name] = {
            "mse_ratio": _finite(point[col]),
            "ci": [lower, upper],
            "ci_mc_se": list(endpoint_mc_error(values[:, col], level)),
            "n_failed_resamples": n_failed,
            "mse_href": float(variant_mse[name].mean()),
            "reading": reading,
            "reason": reason,
        }
    return out


def score_weight(
    weight: np.ndarray,
    split: SplitData,
    horizons: np.ndarray,
    config: StudyConfig,
) -> RuleScores:
    """Score a horizon-free weight ``(n, E)`` exactly as A4 is scored.

    The weight is broadcast over the horizons as ``pipeline.rule_weights``
    does for A4 and scored by ``pipeline.score_rules``.
    """
    shape = split.evals.cp_err.shape
    full = np.broadcast_to(weight[..., None], shape).copy()
    return score_rules(
        {"variant": full}, split, horizons, config, config.primary_threshold
    )["variant"]


# ------------------------------------------------------- (a) A4 coefficients
def construction_design(
    proxies: ProfileProxies,
    split: SplitData,
    noise: float,
) -> dict[str, np.ndarray]:
    """Return the per-state design of the proxy fits on construction.

    These are the arrays ``ProfileProxies.fit`` fits on: the median over draws
    of each squared feature (with the fitted ``nu`` cap), and the squared
    oracle seeds.

    Returns
    -------
    dict[str, np.ndarray]
        ``analog_f``, ``analog_g``, ``est_f``, ``est_g`` (each ``(n,)``),
        ``analog_seed_sq`` and ``est_seed_sq``.
    """
    ev, moments = split.evals, split.moments
    features = ProfileProxies.features(
        ev.distance, ev.est_nu, noise, proxies.nu_cap
    )
    design = {k: np.median(v**2, axis=1) for k, v in features.items()}
    design["analog_seed_sq"] = moments.analog_seed**2
    design["est_seed_sq"] = moments.est_seed**2
    return design


PROXY_COLUMNS: dict[str, tuple[str, str, str]] = {
    "analog": ("analog_f", "analog_g", "analog_seed_sq"),
    "estimation": ("est_f", "est_g", "est_seed_sq"),
}
"""Design keys of each proxy: (slope column, floor column, squared seed)."""


def term_share(
    proxies: ProfileProxies, design: dict[str, np.ndarray], name: str
) -> float:
    """Largest share of one term in its fitted seed over construction states.

    For ``b`` it is ``max_i b g_i / (a f_i + b g_i)`` on the fit's design.
    The share of a term of a hand-built proxy with both coefficients 0 is
    undefined; then it is NaN.
    """
    proxy_name, field = COEFFICIENTS[name]
    proxy = getattr(proxies, proxy_name)
    f_key, g_key, _ = PROXY_COLUMNS[proxy_name]
    slope_term = proxy.slope * design[f_key]
    floor_term = proxy.floor * design[g_key]
    term = slope_term if field == "slope" else floor_term
    total = slope_term + floor_term
    if np.any(total <= 0.0):
        return float("nan")
    return float(np.max(term / total))


def coefficient_records(
    proxies: ProfileProxies,
    design: dict[str, np.ndarray],
    weight_change: dict[str, float],
) -> dict[str, dict]:
    """Fitted value, term share and boundary flag of each coefficient.

    ``max_term_share`` (construction design) is a diagnostic.
    ``max_abs_weight_change`` is the largest ``|w(zero variant) - w(A4)|`` over
    the test (state, draw) pairs, and ``at_bound`` is the boundary rule of M-2:
    True if that change is at most ``IDENTIFIABLE_CHANGE``, so the coefficient
    is fitted at its bound 0, is not identifiable from these data, and both of
    its rows read "not identifiable".
    """
    out = {}
    for name, (proxy_name, field) in COEFFICIENTS.items():
        change = weight_change[name]
        out[name] = {
            "value": float(getattr(getattr(proxies, proxy_name), field)),
            "max_term_share": _finite(term_share(proxies, design, name)),
            "max_abs_weight_change": change,
            "at_bound": bool(change <= IDENTIFIABLE_CHANGE),
        }
    return out


def zero_variant(proxies: ProfileProxies, name: str) -> ProfileProxies:
    """Return the proxies with one coefficient set to 0, the rest unchanged."""
    proxy_name, field = COEFFICIENTS[name]
    proxy = getattr(proxies, proxy_name)
    return replace(
        proxies, **{proxy_name: replace(proxy, **{field: 0.0})}
    )


def refit_variant(
    proxies: ProfileProxies, design: dict[str, np.ndarray], name: str
) -> tuple[ProfileProxies, dict]:
    """Drop one term and refit its partner by the same log-scale fit.

    The other proxy's fit is a separate problem, unchanged by the drop, so its
    refit equals its fit (``log_scale_fit`` is deterministic) and it is kept.

    Returns
    -------
    tuple[ProfileProxies, dict]
        The variant, and a record: ``partner`` (the refitted coefficient),
        ``partner_value``, ``nfev``, ``status`` and ``coefficients`` (the
        variant's four coefficients, the removed one 0).
    """
    proxy_name, field = COEFFICIENTS[name]
    f_key, g_key, seed_key = PROXY_COLUMNS[proxy_name]
    kept = g_key if field == "slope" else f_key
    (value,), nfev, status = log_scale_fit([design[kept]], design[seed_key])
    refit = (
        SeedProxy(slope=0.0, floor=float(value), nfev=nfev, status=status)
        if field == "slope"
        else SeedProxy(slope=float(value), floor=0.0, nfev=nfev, status=status)
    )
    variant = replace(proxies, **{proxy_name: refit})
    partner = next(
        k
        for k, (p, f) in COEFFICIENTS.items()
        if p == proxy_name and f != field
    )
    return variant, {
        "partner": partner,
        "partner_value": float(value),
        "nfev": nfev,
        "status": status,
        "coefficients": {
            k: float(getattr(getattr(variant, p), f))
            for k, (p, f) in COEFFICIENTS.items()
        },
    }


def a4_weight(
    proxies: ProfileProxies, split: SplitData, noise: float
) -> tuple[np.ndarray, dict[str, int]]:
    """Return A4's weight ``(n, E)`` under ``proxies``, and its floor counts.

    The weight is computed as ``pipeline.rule_weights`` computes A4 (seeds,
    squares, ``closed_form_weight``), so the fitted proxies give A4 bitwise.
    ``n_floored`` counts the (state, draw) entries whose denominator is below
    the ``1e-300`` floor (undefined, 0 included; weight 0 there) and the states
    with at least one.
    """
    eps_hat, delta_hat = proxies.seeds(split.evals, noise)
    eps_sq, delta_sq = eps_hat**2, delta_hat**2
    undefined = eps_sq + delta_sq < UNDEFINED_FLOOR
    return closed_form_weight(eps_sq, delta_sq), {
        "entries": closed_form_floor_count(eps_sq, delta_sq),
        "states": int(np.sum(np.any(undefined, axis=1))),
    }


def a4_coefficient_block(
    core: Cell,
    rules: FittedRules,
    a4_state_mse: np.ndarray,
    config: StudyConfig,
) -> dict:
    """Ablation (a): the eight A4 coefficient variants, against A4.

    Parameters
    ----------
    core : Cell
        Core cell (construction for the refits, test for the scores).
    rules : FittedRules
        Fitted rules (the A4 proxies).
    a4_state_mse : np.ndarray
        A4's per-state squared error at ``H_ref`` on test (``scores["A4"]``).
    config : StudyConfig
        Study configuration.

    Returns
    -------
    dict
        ``role``, ``level``, ``n_states``, ``coefficients`` (fit records),
        ``full`` (the unchanged proxies rescored: ``reproduces_A4`` is the
        bitwise check against ``a4_state_mse``), ``variants`` (``zero`` and
        ``refit``, each keyed by coefficient) and ``threshold``.
    """
    proxies = rules.proxies
    test = core.splits["test"]
    design = construction_design(
        proxies, core.splits["construction"], core.noise
    )
    full_weight, full_floor = a4_weight(proxies, test, core.noise)
    full_mse = score_weight(
        full_weight, test, core.horizons, config
    ).state_mse_ref

    variants: dict[str, ProfileProxies] = {}
    extra: dict[str, dict] = {}
    for name in COEFFICIENTS:
        variants[f"zero/{name}"] = zero_variant(proxies, name)
        variant, record = refit_variant(proxies, design, name)
        variants[f"refit/{name}"] = variant
        extra[f"refit/{name}"] = record

    mse: dict[str, np.ndarray] = {}
    weights: dict[str, dict] = {}
    change: dict[str, float] = {}
    for key, variant in variants.items():
        weight, floored = a4_weight(variant, test, core.noise)
        mse[key] = score_weight(
            weight, test, core.horizons, config
        ).state_mse_ref
        weights[key] = {
            "mean_weight": float(weight.mean()),
            "n_floored": floored,
        }
        mode, name = key.split("/")
        if mode == "zero":
            change[name] = float(np.max(np.abs(weight - full_weight)))
    records = coefficient_records(proxies, design, change)
    rows = ratio_rows(
        mse,
        a4_state_mse,
        A4_LEVEL,
        config.bootstrap_resamples,
        config.bootstrap_block,
        make_rng(config.seed, core.system, "bootstrap", "ablation-A4"),
        identifiable={
            key: not records[key.split("/")[1]]["at_bound"] for key in mse
        },
    )
    by_mode: dict[str, dict] = {mode: {} for mode in MODES}
    for key, row in rows.items():
        mode, name = key.split("/")
        by_mode[mode][name] = {**row, **weights[key], **extra.get(key, {})}
    return {
        "role": "estimate",
        "level": A4_LEVEL,
        "n_states": int(len(a4_state_mse)),
        "coefficients": records,
        "full": {
            "mse_href": float(full_mse.mean()),
            "mean_weight": float(full_weight.mean()),
            "reproduces_A4": bool(np.array_equal(full_mse, a4_state_mse)),
            "n_floored": full_floor,
        },
        "variants": by_mode,
        "threshold": (
            "estimate, no pass/fail: r = MSE(variant)/MSE(A4) at H_ref, "
            "paired block bootstrap; reading by the table of M-2 (WU-0041b): "
            "n < 50 or a NaN or infinite bound: undetermined; max |dw| of "
            f"the zero variant <= {IDENTIFIABLE_CHANGE:g}: not identifiable "
            "(both rows); upper < 1: lowers; lower <= 1 and upper <= "
            f"{RATIO_MARGIN:g}: negligible; lower > 1 and upper <= "
            f"{RATIO_MARGIN:g}: small; lower > {RATIO_MARGIN:g}: "
            "substantial; lower > 1 and upper > "
            f"{RATIO_MARGIN:g}: needed, size not determined; otherwise "
            "undetermined"
        ),
    }


# ---------------------------------------------------- (b1), (b2) Q-N ablation
def subset_key(columns: tuple[int, ...]) -> str:
    """Key of a subset of the conditions: its letters in order, or ``none``."""
    return "".join(CONDITIONS[j] for j in columns) or EMPTY_SUBSET


def shapley_weight(size: int, n_players: int = len(CONDITIONS)) -> float:
    """Shapley weight ``|S|! (p - 1 - |S|)! / p!`` of a subset of size |S|."""
    return (
        factorial(size)
        * factorial(n_players - 1 - size)
        / factorial(n_players)
    )


SUBSETS: tuple[tuple[int, ...], ...] = tuple(
    s
    for size in range(len(CONDITIONS) + 1)
    for s in combinations(range(len(CONDITIONS)), size)
)
"""The 16 subsets of the four conditions, by size, each in column order."""


def _columns(profile: np.ndarray, subset: tuple[int, ...]) -> np.ndarray:
    """Return the columns ``subset`` of ``profile``, indexed as Q-N indexes.

    Q-N fits the full model on the profile itself and the three-coordinate
    model on the slice ``[:, :3]``; a leading run of columns is therefore
    taken as a slice (the same array operation), any other subset by a list.
    """
    if subset == tuple(range(profile.shape[1])):
        return profile
    if subset == tuple(range(len(subset))):
        return profile[:, : len(subset)]
    return profile[:, list(subset)]


def profile_ablation_block(
    x_train: np.ndarray,
    x_test: np.ndarray,
    w_train: np.ndarray,
    w_test: np.ndarray,
    log_t_train: np.ndarray,
    log_t_test: np.ndarray,
    *,
    seed: int,
    n_resamples: int,
    block: int,
    boot_seed: int | np.random.Generator,
    level: float = PROFILE_LEVEL,
    horizon_cap: float | None = None,
) -> dict:
    """Rows (b1) and (b2) for one profile: leave-one-out and Shapley shares.

    The targets, domains and regressor are those of
    :func:`lpcstudy.analysis.qn_profile_block` (``qn_targets``,
    ``qn_regressor(seed)``). For each target a model is fitted on every
    non-empty subset ``S`` of the four coordinates, on the training rows of
    the target's domain, and scored on the test rows of its domain; the empty
    subset is the training-mean predictor. Then

    * (b1) ``Delta R^2_X = R^2(F) - R^2(F without X)``; for ``X = N`` this is
      the Q-N statistic, computed by the same operations, so with the same
      ``boot_seed`` and level its leaves equal Q-N's bitwise;
    * (b2) ``phi_X = sum_{S not containing X} |S|! (3 - |S|)! / 4! [R^2(S + X)
      - R^2(S)]``, which sums over ``X`` to ``R^2(F) - R^2(empty)``.

    All rows of all three targets are one vector statistic, so they share the
    resamples (the Q-N resamples when ``boot_seed`` is Q-N's generator). The
    models are held fixed in the resamples; the interior filter is applied in
    each resample, as in Q-N. A non-finite resample is failed and counted. Each
    interval is read by the Q-N table (``analysis.qn_reading``), the horizon
    target included (section 7.2 of the pre-registration draft).

    Parameters
    ----------
    x_train, x_test, w_train, w_test, log_t_train, log_t_test
        As in :func:`lpcstudy.analysis.qn_profile_block`.
    seed : int
        Master seed for :func:`lpcstudy.analysis.qn_regressor`.
    n_resamples, block : int
        Bootstrap resamples and block length.
    boot_seed : int or np.random.Generator
        Randomness of the resample indices.
    level : float, optional
        Interval level (``PROFILE_LEVEL``).
    horizon_cap : float, optional
        The censoring value of the log horizon, ``ln H_max`` (M-5). If given,
        every row of ``log_horizon`` carries ``n_censored`` (test states with
        ``log_t >= horizon_cap``, i.e. ``T >= 8 LT``) and ``n_uncensored``, and
        a horizon row with fewer than 50 uncensored test states reads
        "undetermined" (reason ``n_uncensored < 50``).

    Returns
    -------
    dict
        Per target: ``r2_by_subset`` (16 point values), ``leave_one_out`` and
        ``shapley`` (per condition: the point value, ``ci``,
        ``n_failed_resamples``, ``reading``, ``reason``; leave-one-out also
        ``r2_without``), ``shapley_sum``, ``r2_full_minus_empty``,
        ``n_train`` and ``n_test``; with ``horizon_cap``, the horizon target
        also ``n_censored`` and ``n_uncensored`` (in the entry and each row).
    """
    targets = qn_targets(
        x_train, x_test, w_train, w_test, log_t_train, log_t_test
    )
    names = list(targets)
    full = SUBSETS[-1]
    preds: dict[str, dict[tuple[int, ...], np.ndarray]] = {}
    for name, (rows_train, y_train, _, _) in targets.items():
        preds[name] = {
            (): np.full(len(x_test), y_train[rows_train].mean())
        }
        for subset in SUBSETS[1:]:
            preds[name][subset] = (
                qn_regressor(seed)
                .fit(_columns(x_train[rows_train], subset), y_train[rows_train])
                .predict(_columns(x_test, subset))
            )

    def without(subset: tuple[int, ...], j: int) -> tuple[int, ...]:
        return tuple(k for k in subset if k != j)

    def rows_of(name: str, r2: dict) -> list[float]:
        loo = [r2[full] - r2[without(full, j)] for j in range(len(CONDITIONS))]
        phi = [
            sum(
                shapley_weight(len(s)) * (r2[tuple(sorted((*s, j)))] - r2[s])
                for s in SUBSETS
                if j not in s
            )
            for j in range(len(CONDITIONS))
        ]
        return loo + phi

    def r2_all(name: str, idx: np.ndarray) -> dict:
        _, _, _, y_test = targets[name]
        return {s: _r2(y_test, preds[name][s], idx) for s in SUBSETS}

    def stat(idx: np.ndarray) -> np.ndarray:
        out = []
        for name in names:
            rows_test = targets[name][2]
            out += rows_of(name, r2_all(name, idx[rows_test[idx]]))
        return np.array(out)

    point, values = bootstrap_values(
        stat, len(w_test), n_resamples, block, boot_seed
    )
    n_rows = 2 * len(CONDITIONS)
    out: dict = {}
    for t, name in enumerate(names):
        rows_train, _, rows_test, _ = targets[name]
        n_test = int(rows_test.sum())
        censoring: dict[str, int] = {}
        if name == "log_horizon" and horizon_cap is not None:
            n_censored = int(np.sum(log_t_test[rows_test] >= horizon_cap))
            censoring = {
                "n_censored": n_censored,
                "n_uncensored": n_test - n_censored,
            }
        r2 = r2_all(name, np.flatnonzero(rows_test))
        entry: dict = {
            "r2_by_subset": {subset_key(s): _finite(r2[s]) for s in SUBSETS},
            "leave_one_out": {},
            "shapley": {},
        }
        for k in range(n_rows):
            col = t * n_rows + k
            j = k % len(CONDITIONS)
            lower, upper, n_failed = percentile_interval(values[:, col], level)
            reading, reason = _qn_reading_reason(lower, upper, n_test)
            if censoring and censoring["n_uncensored"] < MIN_STATES:
                reading = "undetermined"
                reason = f"n_uncensored < {MIN_STATES}"
            row = {
                "ci": [lower, upper],
                "n_failed_resamples": n_failed,
                "reading": reading,
                "reason": reason,
                **censoring,
            }
            if k < len(CONDITIONS):
                entry["leave_one_out"][CONDITIONS[j]] = {
                    "delta_r2": float(point[col]),
                    "r2_without": _finite(r2[without(full, j)]),
                    **row,
                }
            else:
                entry["shapley"][CONDITIONS[j]] = {
                    "share": float(point[col]),
                    **row,
                }
        shares = point[t * n_rows + len(CONDITIONS) : (t + 1) * n_rows]
        entry["shapley_sum"] = float(np.sum(shares))
        entry["r2_full_minus_empty"] = float(r2[full] - r2[()])
        entry["n_train"] = int(rows_train.sum())
        entry["n_test"] = n_test
        entry.update(censoring)
        out[name] = entry
    return out


def profile_ablation(
    core: Cell, rules: FittedRules, config: StudyConfig
) -> dict:
    """Rows (b1) and (b2) for the oracle (primary) and deployable profiles.

    The data are Q-N's (``analysis.qn_data``) and each profile gets a fresh
    Q-N generator ``make_rng(config.seed, system, "bootstrap", "Q-N")``, so the
    resamples are Q-N's (shared on purpose: the drop-N row is Q-N).
    """
    data = qn_data(core, rules, config)
    out: dict = {
        "role": "estimate",
        "primary": "oracle",
        "level": PROFILE_LEVEL,
    }
    for kind in QN_PROFILES:
        x_train, x_test = data[kind]
        out[kind] = profile_ablation_block(
            x_train,
            x_test,
            data["w_train"],
            data["w_test"],
            data["log_t_train"],
            data["log_t_test"],
            seed=config.seed,
            n_resamples=config.bootstrap_resamples,
            block=config.bootstrap_block,
            boot_seed=make_rng(config.seed, core.system, "bootstrap", "Q-N"),
            level=PROFILE_LEVEL,
            horizon_cap=float(np.log(config.horizon_max)),
        )
    out["threshold"] = (
        "estimate, no pass/fail: leave-one-out Delta R^2_X and Shapley share "
        "phi_X (16 subsets, empty = training mean) by the Q-N procedure; each "
        "interval read by the Q-N table of v3 section 7"
    )
    return out


# ---------------------------------------------------------- (b3) A5 without X
def a5_ablation_block(
    core: Cell,
    rules: FittedRules,
    a5_state_mse: np.ndarray,
    config: StudyConfig,
) -> dict:
    """Row (b3): A5 refitted on the three deployable coordinates other than X.

    The refit is the A5 procedure (``pipeline.fit_regime_maps``: a tree per
    ``K`` on construction, leaf weights on calibration, ``K`` by the v3 rule)
    on the profile without column ``X``, scored on test as A5 is. ``full`` is
    the same refit on all four columns, checked bitwise against A5.

    Parameters
    ----------
    core : Cell
        Core cell.
    rules : FittedRules
        Fitted rules (proxies for the profile, A2 for empty regimes).
    a5_state_mse : np.ndarray
        A5's per-state squared error at ``H_ref`` on test.
    config : StudyConfig
        Study configuration.

    Returns
    -------
    dict
        ``role``, ``level``, ``n_states``, ``full`` (``reproduces_A5``,
        ``chosen_K``), ``without`` (per condition: the ratio row,
        ``chosen_K``, ``n_empty_regimes``) and ``threshold``.
    """
    lt = config.steps_per_lyapunov
    col = config.reference_horizon - 1
    con, cal, test = (
        core.splits[s] for s in ("construction", "calibration", "test")
    )
    profiles = [
        deployable_profile(s.evals, rules.proxies, core.noise, lt)
        for s in (con, cal, test)
    ]
    w_target = oracle_weight(con.moments)[:, col]
    t_target = np.log(
        state_horizon_target(con.moments, core.noise, config.primary_threshold)
    )

    def refit(columns: list[int]) -> tuple[np.ndarray, int, int]:
        con_p, cal_p, test_p = (p[..., columns] for p in profiles)
        regimes, chosen = fit_regime_maps(
            con_p,
            cal_p,
            w_target,
            t_target,
            cal.moments,
            cal.evals,
            rules.global_weights,
            config,
        )
        rmap = regimes[chosen]
        weight = rmap.weights[rmap.assign(test_p)][..., core.horizons - 1]
        scores = score_rules(
            {"A5": weight},
            test,
            core.horizons,
            config,
            config.primary_threshold,
        )
        return scores["A5"].state_mse_ref, chosen, int(rmap.empty.sum())

    all_columns = list(range(len(CONDITIONS)))
    full_mse, full_k, _ = refit(all_columns)
    mse, fits = {}, {}
    for j, name in enumerate(CONDITIONS):
        mse[name], chosen, empty = refit([k for k in all_columns if k != j])
        fits[name] = {"chosen_K": chosen, "n_empty_regimes": empty}
    rows = ratio_rows(
        mse,
        a5_state_mse,
        A5_LEVEL,
        config.bootstrap_resamples,
        config.bootstrap_block,
        make_rng(config.seed, core.system, "bootstrap", "ablation-A5"),
    )
    return {
        "role": "estimate",
        "level": A5_LEVEL,
        "n_states": int(len(a5_state_mse)),
        "full": {
            "reproduces_A5": bool(np.array_equal(full_mse, a5_state_mse)),
            "chosen_K": full_k,
        },
        "without": {k: {**rows[k], **fits[k]} for k in CONDITIONS},
        "threshold": (
            "estimate, no pass/fail: r = MSE(A5 without X)/MSE(A5) at H_ref, "
            "paired block bootstrap; reading by the table of M-2 (WU-0041b), "
            "without the boundary rule"
        ),
    }


# ------------------------------------------------------------------ the block
def ablation_block(
    core: Cell,
    rules: FittedRules,
    scores: dict[str, RuleScores],
    config: StudyConfig,
) -> dict:
    """Return the ``ablation`` block of one system (WU-0039b; no verdict).

    Parameters
    ----------
    core : Cell
        Core cell.
    rules : FittedRules
        Rules fitted on it.
    scores : dict[str, RuleScores]
        Test scores of the rules (A4 and A5 are the bases of the ratios).
    config : StudyConfig
        Study configuration.

    Returns
    -------
    dict
        ``role``, ``cell`` (noise, library size, ``H_ref`` in steps),
        ``A4_coefficients``, ``profile_conditions`` and
        ``A5_without_condition``. Each part carries its wall time in a key
        ``seconds`` (skipped by ``tools/leafdiff.py``).
    """
    out: dict = {
        "role": "estimate",
        "cell": {
            "noise": core.noise,
            "library_size": core.library_size,
            "reference_horizon": config.reference_horizon,
        },
    }
    parts = (
        (
            "A4_coefficients",
            lambda: a4_coefficient_block(
                core, rules, scores["A4"].state_mse_ref, config
            ),
        ),
        ("profile_conditions", lambda: profile_ablation(core, rules, config)),
        (
            "A5_without_condition",
            lambda: a5_ablation_block(
                core, rules, scores["A5"].state_mse_ref, config
            ),
        ),
    )
    for key, build in parts:
        start = time.time()
        out[key] = build()
        out[key]["seconds"] = time.time() - start
    return out
