"""Survival analysis for censored horizons, bootstrap intervals and regressions."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from scipy import stats as sps


@dataclass
class SurvivalCurve:
    """Kaplan-Meier estimate on integer horizons ``1..H_max``.

    Attributes
    ----------
    times : np.ndarray
        Horizons ``1..H_max``.
    survival : np.ndarray
        ``S(H) = Pr(T > H)``.
    """

    times: np.ndarray
    survival: np.ndarray

    def median(self) -> float:
        """Smallest horizon with ``S(H) <= 0.5`` (``nan`` if not reached)."""
        hit = np.nonzero(self.survival <= 0.5)[0]
        return float(self.times[hit[0]]) if hit.size else float("nan")

    def restricted_mean(self) -> float:
        """Restricted mean survival time to ``H_max`` (``sum_{H<H_max} S(H)`` + 1)."""
        return float(1.0 + np.sum(self.survival[:-1]))


def kaplan_meier(durations: np.ndarray, events: np.ndarray, horizon_max: int
                 ) -> SurvivalCurve:
    """Kaplan-Meier estimator for discrete first-passage times.

    Parameters
    ----------
    durations : np.ndarray
        Observed horizons (event or censoring time), integers in ``1..H_max``.
    events : np.ndarray
        ``True`` if the tolerance was exceeded at ``durations``.
    horizon_max : int
        Censoring horizon.

    Returns
    -------
    SurvivalCurve
        The estimate.
    """
    durations = np.asarray(durations).ravel()
    events = np.asarray(events, dtype=bool).ravel()
    times = np.arange(1, horizon_max + 1)
    deaths = np.bincount(durations[events], minlength=horizon_max + 1)[1:]
    exits = np.bincount(durations, minlength=horizon_max + 1)[1:]
    at_risk = len(durations) - np.concatenate([[0], np.cumsum(exits)[:-1]])
    hazard = np.where(at_risk > 0, deaths / np.maximum(at_risk, 1), 0.0)
    return SurvivalCurve(times=times, survival=np.cumprod(1.0 - hazard))


def logrank_test(dur_a: np.ndarray, ev_a: np.ndarray, dur_b: np.ndarray,
                 ev_b: np.ndarray) -> float:
    """Two-sample log-rank test p-value.

    Parameters
    ----------
    dur_a, ev_a : np.ndarray
        Durations and event indicators of group A.
    dur_b, ev_b : np.ndarray
        Durations and event indicators of group B.

    Returns
    -------
    float
        Two-sided p-value (chi-square, 1 degree of freedom).
    """
    dur = np.concatenate([dur_a, dur_b]).ravel()
    ev = np.concatenate([ev_a, ev_b]).ravel().astype(bool)
    group = np.concatenate([np.zeros(np.size(dur_a)), np.ones(np.size(dur_b))])
    observed_minus_expected, variance = 0.0, 0.0
    for t in np.unique(dur[ev]):
        at_risk = dur >= t
        n_total = at_risk.sum()
        n_a = (at_risk & (group == 0)).sum()
        d_total = (ev & (dur == t)).sum()
        d_a = (ev & (dur == t) & (group == 0)).sum()
        observed_minus_expected += d_a - d_total * n_a / n_total
        if n_total > 1:
            variance += d_total * (n_a / n_total) * (1 - n_a / n_total) * \
                (n_total - d_total) / (n_total - 1)
    if variance <= 0:
        return 1.0
    return float(sps.chi2.sf(observed_minus_expected**2 / variance, df=1))


def holm_adjust(p_values: list[float]) -> list[float]:
    """Holm step-down adjusted p-values.

    Parameters
    ----------
    p_values : list[float]
        Raw p-values.

    Returns
    -------
    list[float]
        Adjusted p-values in the original order.
    """
    p_arr = np.asarray(p_values, dtype=float)
    order = np.argsort(p_arr)
    adjusted = np.empty_like(p_arr)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, min(1.0, (len(p_arr) - rank) * p_arr[idx]))
        adjusted[idx] = running
    return adjusted.tolist()


def block_bootstrap(statistic: Callable[[np.ndarray], float], n_items: int,
                    n_resamples: int, block: int, seed: int,
                    level: float = 0.95) -> tuple[float, float, float]:
    """Moving-block bootstrap of a statistic of item indices.

    Items are states in temporal order; blocks of consecutive states are
    resampled with replacement to respect residual serial dependence.

    Parameters
    ----------
    statistic : Callable[[np.ndarray], float]
        Function of an index array returning a scalar.
    n_items : int
        Number of items.
    n_resamples : int
        Number of bootstrap resamples.
    block : int
        Block length.
    seed : int
        Seed.
    level : float, optional
        Confidence level.

    Returns
    -------
    tuple[float, float, float]
        Point estimate on all items, lower and upper percentile bounds.
    """
    rng = np.random.default_rng(seed)
    base = np.arange(n_items)
    n_blocks = int(np.ceil(n_items / block))
    starts_max = max(1, n_items - block + 1)
    values = np.empty(n_resamples)
    for r in range(n_resamples):
        starts = rng.integers(0, starts_max, n_blocks)
        idx = (starts[:, None] + np.arange(block)[None, :]).ravel()[:n_items]
        values[r] = statistic(base[np.minimum(idx, n_items - 1)])
    alpha = (1.0 - level) / 2.0
    return (float(statistic(base)), float(np.nanquantile(values, alpha)),
            float(np.nanquantile(values, 1.0 - alpha)))


def ols_slope(x_values: np.ndarray, y_values: np.ndarray) -> float:
    """Ordinary least-squares slope of ``y`` on ``x`` (with intercept)."""
    x_c = x_values - x_values.mean()
    return float(np.sum(x_c * (y_values - y_values.mean())) / np.sum(x_c**2))


def partial_correlation(target: np.ndarray, variable: np.ndarray,
                        controls: np.ndarray) -> float:
    """Correlation of ``target`` and ``variable`` after regressing out ``controls``.

    Parameters
    ----------
    target : np.ndarray
        Response ``(n,)``.
    variable : np.ndarray
        Variable of interest ``(n,)``.
    controls : np.ndarray
        Control variables ``(n, p)``.

    Returns
    -------
    float
        Partial correlation coefficient.
    """
    design = np.column_stack([np.ones(len(target)), controls])
    resid_t = target - design @ np.linalg.lstsq(design, target, rcond=None)[0]
    resid_v = variable - design @ np.linalg.lstsq(design, variable, rcond=None)[0]
    return float(np.corrcoef(resid_t, resid_v)[0, 1])


def spearman(a_values: np.ndarray, b_values: np.ndarray) -> float:
    """Spearman rank correlation."""
    return float(sps.spearmanr(a_values, b_values).statistic)
