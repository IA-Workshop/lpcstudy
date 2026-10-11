"""Survival analysis for censored horizons, bootstrap intervals, verdicts and regressions."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from typing import Literal

import numpy as np
from scipy import stats as sps

MIN_STATES: int = 50
"""Fewest states a bootstrapped statistic may rest on (DEC-0008 A3: 10 blocks of 5)."""

Verdict = Literal["pass", "fail", "inconclusive"]

V3_SYSTEMS: tuple[str, ...] = ("lorenz63", "rossler", "chua")
"""The three systems of v3 section 7; the overall verdict is over exactly these (DEC-0016 O1)."""


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

    The hazard is 0 where nobody is at risk (the ``np.where`` below; DEF-0001, inventory row T1).
    That branch never changes a value of the formula, and its two cases are these.

    * Since ``deaths(t) <= at_risk(t)``, ``at_risk = 0`` implies ``deaths = 0``, so
      ``deaths / max(at_risk, 1)`` is already 0: the ``np.where`` states the convention
      "hazard 0 when nobody is at risk, so S is carried forward" and is not a replacement.
    * With ``n >= 1`` and censoring only at ``H_max`` (every caller using ``realized_horizon``
      or ``characteristic_horizon``), ``at_risk = 0`` before ``H_max`` means that everyone had
      an event. At the last event time ``t_L`` the risk set is exactly the ``d(t_L)`` subjects
      that fail, so the hazard is ``d / d = 1`` in IEEE arithmetic and ``S(t_L) = 0`` exactly;
      S stays 0 afterwards. So the convention fires only where S is already 0.

    Two hypotheses. (i) ``check_kaplan_meier`` (V5) censors at random times, so there the branch
    is the standard carry-forward convention and not "S is already 0"; it does not fire at its
    n = 20000. (ii) ``n = 0`` (an empty set; no caller passes one) gives ``S = 1`` at every
    horizon, a NaN median and a restricted mean of ``H_max``; ``durations`` must then have an
    integer dtype (``np.bincount`` rejects floats).

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


def logrank_parts(dur_a: np.ndarray, ev_a: np.ndarray, dur_b: np.ndarray,
                  ev_b: np.ndarray) -> tuple[float, float]:
    """Observed minus expected events of group A and the log-rank variance.

    The sum over event times of ``d_A - d n_A / n`` and of the tie-corrected hypergeometric
    variance ``d (n_A/n)(1 - n_A/n)(n - d)/(n - 1)`` (terms with ``n = 1`` skipped). A
    variance of 0 is the case that ``logrank_test`` maps to ``p = 1.0``; a caller that must
    tell "no information" from "no evidence" (H3a, DEC-0011) reads it here.

    Parameters
    ----------
    dur_a, ev_a : np.ndarray
        Durations and event indicators of group A.
    dur_b, ev_b : np.ndarray
        Durations and event indicators of group B.

    Returns
    -------
    tuple[float, float]
        ``(O - E, V)``.
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
    return float(observed_minus_expected), float(variance)


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
        Two-sided p-value (chi-square, 1 degree of freedom); 1.0 if the variance is 0
        (see ``logrank_parts``).

    Notes
    -----
    ``p = 1.0`` at ``V <= 0`` is a convention, not a measurement (DEF-0001, row T2). ``V`` is a
    sum of non-negative terms, so ``V < 0`` is impossible and ``V = 0`` is exact. The only caller
    (``analysis.h3a_logrank``) reads ``logrank_parts`` first, does not call this function for such
    a pair, records the reason, and counts the pair in ``H3a.n_degenerate_pairs``.
    """
    observed_minus_expected, variance = logrank_parts(dur_a, ev_a, dur_b, ev_b)
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


def block_resample_indices(n_items: int, n_resamples: int, block: int,
                           seed: int | np.random.Generator) -> Iterator[np.ndarray]:
    """Yield moving-block bootstrap index arrays, one per resample.

    Blocks of ``block`` consecutive items start at independent uniform positions
    and are concatenated and cut to ``n_items``. (The final ``np.minimum`` clip to the
    last item is kept from the original code for bitwise identity; it never fires,
    because every start is at most ``n_items - block`` or 0.) Parts of one criterion that must share resamples take the same
    integer seed (or a fresh generator per part built from the same labels), or use
    one vector statistic; a shared ``Generator`` advances between calls.

    Parameters
    ----------
    n_items : int
        Number of items (at least 1).
    n_resamples : int
        Number of resamples (at least 0).
    block : int
        Block length (at least 1).
    seed : int or np.random.Generator
        Integer seed, or a generator that is consumed (it advances).

    Returns
    -------
    Iterator[np.ndarray]
        ``n_resamples`` integer arrays of length ``n_items``, drawn lazily.

    Raises
    ------
    ValueError
        If ``n_items`` or ``block`` is below 1 or ``n_resamples`` is negative.
    """
    if n_items < 1 or block < 1 or n_resamples < 0:
        raise ValueError(f"need n_items >= 1, block >= 1, n_resamples >= 0; got "
                         f"{n_items}, {block}, {n_resamples}")
    rng = seed if isinstance(seed, np.random.Generator) else np.random.default_rng(seed)
    return _draw_indices(n_items, n_resamples, block, rng)


def _draw_indices(n_items: int, n_resamples: int, block: int,
                  rng: np.random.Generator) -> Iterator[np.ndarray]:
    """Draw the index arrays of ``block_resample_indices`` from ``rng``."""
    base = np.arange(n_items)
    n_blocks = int(np.ceil(n_items / block))
    starts_max = max(1, n_items - block + 1)
    for _ in range(n_resamples):
        starts = rng.integers(0, starts_max, n_blocks)
        idx = (starts[:, None] + np.arange(block)[None, :]).ravel()[:n_items]
        yield base[np.minimum(idx, n_items - 1)]


def bootstrap_values(statistic: Callable[[np.ndarray], float | np.ndarray], n_items: int,
                     n_resamples: int, block: int, seed: int | np.random.Generator
                     ) -> tuple[float | np.ndarray, np.ndarray]:
    """Evaluate a statistic on moving-block bootstrap resamples and on all items.

    Parameters
    ----------
    statistic : Callable[[np.ndarray], float | np.ndarray]
        Function of an index array returning a scalar, or a 1-D array of fixed
        length ``q`` (several quantities that share the same resamples). It signals
        "cannot compute" by returning NaN; exceptions are not caught.
    n_items, n_resamples, block, seed
        As in ``block_resample_indices``.

    Returns
    -------
    point : float or np.ndarray
        ``statistic(np.arange(n_items))``, evaluated after the resamples.
    values : np.ndarray
        Resampled values, shape ``(n_resamples,)`` for a scalar statistic and
        ``(n_resamples, q)`` for a vector statistic. Non-finite values are kept.

    Raises
    ------
    ValueError
        If the statistic's output is not a scalar or 1-D array, or its shape changes.
    """
    draws = [np.asarray(statistic(idx), dtype=float)
             for idx in block_resample_indices(n_items, n_resamples, block, seed)]
    point = np.asarray(statistic(np.arange(n_items)), dtype=float)
    shapes = {draw.shape for draw in draws} | {point.shape}
    if len(shapes) != 1 or point.ndim > 1:
        raise ValueError(f"statistic must return a scalar or a 1-D array of fixed "
                         f"shape; got shapes {sorted(shapes)}")
    values = np.stack(draws) if draws else np.empty((0, *point.shape))
    return (float(point) if point.ndim == 0 else point), values


def percentile_interval(values: np.ndarray, level: float) -> tuple[float, float, int]:
    """Percentile interval of bootstrap values with failed resamples counted (DEC-0008 A3).

    A resample is failed if its value is not finite. Failed values count as ``-inf``
    for the lower bound and ``+inf`` for the upper bound (widening is the unfavourable
    tail for both pass and fail). With ``a = (1 - level)/2`` and ``B`` resamples, a bound
    is infinite iff the linear-interpolation quantile gives weight to a failed order
    statistic, i.e. iff the number of failures ``F >= floor((B - 1) a) + 1``; then both
    bounds are infinite. Otherwise each failed value is replaced by the smallest (lower
    bound) or largest (upper bound) finite value, which leaves the quantile unchanged
    and avoids infinite arithmetic. With ``F = 0`` the result is ``np.quantile``.

    Float convention: the threshold is evaluated in float64 with ``a = (1 - level)/2``
    as computed. When ``(B - 1) a`` is an exact integer but the float ``a`` rounds
    below it, the float floor is one lower than exact arithmetic, so the threshold is
    one failure lower: for ``B = 21`` at level 0.8, ``(B - 1) a = 1.9999999999999996``
    gives ``F* = 2``, and ``F = 2`` returns ``(-inf, inf)`` where exact arithmetic gives
    a finite lower bound (the third order statistic). This is conservative (more
    inconclusive, never fewer), and it matches ``np.quantile`` only for the lower
    bound, whose float index puts weight 4e-16 on a failure; making both bounds
    infinite together is a convention. It occurs only for some B at levels 0.8 and 0.9
    (748 pairs with B <= 5000, none at 0.95 or ``1 - 0.05/3`` or at B in {50, 500, 2000}),
    so no study verdict changes. The tests pin the ``B = 21`` case.

    Parameters
    ----------
    values : np.ndarray
        1-D resampled values (for a vector statistic call this once per column).
    level : float
        Confidence level in (0, 1).

    Returns
    -------
    tuple[float, float, int]
        Lower bound, upper bound and the number of failed resamples.

    Raises
    ------
    ValueError
        If ``values`` is not 1-D and non-empty or ``level`` is outside (0, 1).
    """
    resampled = np.asarray(values, dtype=float)
    if resampled.ndim != 1 or resampled.size == 0:
        raise ValueError(f"values must be a non-empty 1-D array; got shape {resampled.shape}")
    if not 0.0 < level < 1.0:
        raise ValueError(f"level must lie in (0, 1); got {level}")
    alpha = (1.0 - level) / 2.0
    failed = ~np.isfinite(resampled)
    n_failed = int(failed.sum())
    if n_failed >= int(np.floor((resampled.size - 1) * alpha)) + 1:
        return float("-inf"), float("inf"), n_failed
    if n_failed == 0:
        return (float(np.quantile(resampled, alpha)),
                float(np.quantile(resampled, 1.0 - alpha)), 0)
    finite = resampled[~failed]
    return (float(np.quantile(np.where(failed, finite.min(), resampled), alpha)),
            float(np.quantile(np.where(failed, finite.max(), resampled), 1.0 - alpha)),
            n_failed)


@dataclass(frozen=True)
class BootstrapInterval:
    """Point estimate and percentile interval with the failed resamples counted.

    Attributes
    ----------
    estimate : float
        Statistic on all items.
    lower, upper : float
        Interval bounds; either may be infinite (see ``percentile_interval``).
    n_failed : int
        Resamples whose value was not finite.
    n_resamples : int
        Number of resamples.
    level : float
        Confidence level.
    """

    estimate: float
    lower: float
    upper: float
    n_failed: int
    n_resamples: int
    level: float


def block_bootstrap_counted(statistic: Callable[[np.ndarray], float], n_items: int,
                            n_resamples: int, block: int, seed: int | np.random.Generator,
                            level: float = 0.95) -> BootstrapInterval:
    """Moving-block bootstrap interval that counts failed resamples (DEC-0008 A3).

    Same resamples as ``block_bootstrap``; with no failed resample the estimate and
    both bounds equal its output bitwise (integer seed).

    Parameters
    ----------
    statistic : Callable[[np.ndarray], float]
        Function of an index array returning a scalar (NaN if it cannot compute).
    n_items, n_resamples, block, seed
        As in ``block_resample_indices``.
    level : float, optional
        Confidence level.

    Returns
    -------
    BootstrapInterval
        The estimate, the interval, the failure count and the resample count.

    Raises
    ------
    ValueError
        If the statistic returns an array (use ``bootstrap_values`` and
        ``percentile_interval`` for a vector statistic).
    """
    point, values = bootstrap_values(statistic, n_items, n_resamples, block, seed)
    if values.ndim != 1:
        raise ValueError("block_bootstrap_counted needs a scalar statistic; use "
                         "bootstrap_values and percentile_interval for a vector")
    lower, upper, n_failed = percentile_interval(values, level)
    return BootstrapInterval(estimate=float(point), lower=lower, upper=upper,
                             n_failed=n_failed, n_resamples=int(values.size), level=level)


def interval_verdict(lower: float, upper: float, band: tuple[float, float],
                     closed: tuple[bool, bool] = (True, True)) -> Verdict:
    """Verdict of an interval against a band (DEC-0008 A1; v3 section 2).

    Pass iff the interval lies inside the band; fail iff it misses the band entirely;
    otherwise inconclusive. ``band = (a, b)``; ``a = -inf`` or ``b = +inf`` gives a
    one-sided band, whose infinite edge is always satisfied. ``closed`` says whether
    each finite edge belongs to the band. Unrounded float64 values are compared.

    Parameters
    ----------
    lower, upper : float
        Interval bounds, ``lower <= upper``. A NaN bound gives "inconclusive".
    band : tuple[float, float]
        Band edges ``a < b``.
    closed : tuple[bool, bool], optional
        Whether the lower and upper edges are in the band.

    Returns
    -------
    Verdict
        "pass", "fail" or "inconclusive".

    Raises
    ------
    ValueError
        If the band is not ``a < b`` or ``lower > upper``.
    """
    edge_a, edge_b = band
    if not edge_a < edge_b:
        raise ValueError(f"band edges must satisfy a < b; got {band}")
    if lower > upper:
        raise ValueError(f"interval needs lower <= upper; got ({lower}, {upper})")
    if np.isnan(lower) or np.isnan(upper):
        return "inconclusive"
    closed_a, closed_b = closed
    inside_a = edge_a == -np.inf or (lower >= edge_a if closed_a else lower > edge_a)
    inside_b = edge_b == np.inf or (upper <= edge_b if closed_b else upper < edge_b)
    if inside_a and inside_b:
        return "pass"
    below = edge_a > -np.inf and (upper < edge_a if closed_a else upper <= edge_a)
    above = edge_b < np.inf and (lower > edge_b if closed_b else lower >= edge_b)
    return "fail" if below or above else "inconclusive"


def combine_verdicts(parts: Iterable[Verdict]) -> Verdict:
    """Combine the verdicts of the parts of one criterion (v3 section 7).

    Parameters
    ----------
    parts : Iterable[Verdict]
        One or more verdicts.

    Returns
    -------
    Verdict
        "fail" if any part fails; else "pass" if all parts pass; else "inconclusive".

    Raises
    ------
    ValueError
        If ``parts`` is empty or holds a string that is not a verdict.
    """
    listed = list(parts)
    if not listed:
        raise ValueError("combine_verdicts needs at least one part")
    unknown = [part for part in listed if part not in ("pass", "fail", "inconclusive")]
    if unknown:
        raise ValueError(f"unknown verdict(s) {unknown}")
    if "fail" in listed:
        return "fail"
    return "pass" if all(part == "pass" for part in listed) else "inconclusive"


def overall_verdict(by_system: dict[str, Verdict], required: tuple[str, ...] = V3_SYSTEMS
                    ) -> tuple[str, list[str]]:
    """Overall verdict of a hypothesis over the systems (v3 section 7; DEC-0008 A1; DEC-0016 O1).

    "supported" if every system in ``required`` is present and passes; "not supported" if any
    system present fails (whatever is missing); "inconclusive" otherwise. A missing system has
    no pass, so a run of fewer than the three v3 systems (smoke, development) can never read
    "supported". ``required`` is the constant ``V3_SYSTEMS``, never the run's configured
    systems. The rule is total on the three verdicts and absence; only the all-absent input and
    bad labels raise. The intersection-union argument of v3 section 7 controls the error of
    "supported" only; "not supported" is a union over systems (DEC-0016, error-rate note).

    Parameters
    ----------
    by_system : dict[str, Verdict]
        Verdict of each system that was run.
    required : tuple[str, ...], optional
        Systems that must all pass; defaults to the three v3 systems.

    Returns
    -------
    tuple[str, list[str]]
        The overall verdict and the systems of ``required`` that are absent, in the order of
        ``required``.

    Raises
    ------
    ValueError
        If ``by_system`` is empty, has a system outside ``required`` (a non-v3 label must not
        decide "not supported"), or has a value that is not "pass", "fail" or "inconclusive".
    """
    if not by_system:
        raise ValueError("overall_verdict needs at least one system with a verdict")
    outside = [name for name in by_system if name not in required]
    if outside:
        raise ValueError(f"system(s) {outside} are not in required {list(required)}")
    unknown = [v for v in by_system.values() if v not in ("pass", "fail", "inconclusive")]
    if unknown:
        raise ValueError(f"unknown verdict(s) {unknown}")
    missing = [name for name in required if name not in by_system]
    values = list(by_system.values())
    if "fail" in values:
        return "not supported", missing
    if not missing and all(v == "pass" for v in values):
        return "supported", missing
    return "inconclusive", missing


def criterion_verdict(estimate: float, lower: float, upper: float,
                      band: tuple[float, float], closed: tuple[bool, bool] = (True, True),
                      *, n_states: int) -> tuple[Verdict, str | None]:
    """Verdict of one criterion with the A3 guards applied in order (DEC-0008 A3).

    1. ``n_states < MIN_STATES``: inconclusive, reason "n_states < 50".
    2. A non-finite estimate (or a NaN bound): inconclusive, reason "not computable".
    3. Otherwise ``interval_verdict``. The reason is None for pass and fail;
       for inconclusive it is "failed resamples >= threshold" if a bound is infinite,
       else "interval meets band edge".

    Parameters
    ----------
    estimate : float
        Point estimate on all states.
    lower, upper : float
        Interval bounds (see ``percentile_interval``).
    band, closed
        As in ``interval_verdict``.
    n_states : int
        Full-sample number of states, after exclusion of non-finite states.

    Returns
    -------
    tuple[Verdict, str | None]
        The verdict and the reason.
    """
    if n_states < MIN_STATES:
        return "inconclusive", f"n_states < {MIN_STATES}"
    if not np.isfinite(estimate) or np.isnan(lower) or np.isnan(upper):
        return "inconclusive", "not computable"
    verdict = interval_verdict(lower, upper, band, closed)
    if verdict != "inconclusive":
        return verdict, None
    if np.isinf(lower) or np.isinf(upper):
        return verdict, "failed resamples >= threshold"
    return verdict, "interval meets band edge"


def block_bootstrap_dropped(statistic: Callable[[np.ndarray], float], n_items: int,
                            n_resamples: int, block: int, seed: int | np.random.Generator,
                            level: float = 0.95) -> tuple[float, float, float, int]:
    """Moving-block bootstrap of a statistic of item indices, counting the dropped resamples.

    Items are states in temporal order; blocks of consecutive states are
    resampled with replacement to respect residual serial dependence. NaN
    resamples are dropped here (``np.nanquantile``), as ``block_bootstrap`` always did, and
    **counted** (DEF-0001, row T3). Use ``block_bootstrap_counted`` for the DEC-0008 A3 rule,
    which places failed resamples at the unfavourable tail instead. A resample of +-inf is not
    dropped by ``np.nanquantile``: it stays in the quantiles and is not counted here. If every
    resample is NaN (``n_dropped == n_resamples``) both bounds are NaN and NumPy warns
    ``All-NaN slice``.

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
    seed : int or np.random.Generator
        Seed, or a generator that is consumed.
    level : float, optional
        Confidence level.

    Returns
    -------
    tuple[float, float, float, int]
        Point estimate on all items, lower and upper percentile bounds, and the number of NaN
        resamples that were dropped.
    """
    values = np.empty(n_resamples)
    for r, idx in enumerate(block_resample_indices(n_items, n_resamples, block, seed)):
        values[r] = statistic(idx)
    alpha = (1.0 - level) / 2.0
    return (float(statistic(np.arange(n_items))), float(np.nanquantile(values, alpha)),
            float(np.nanquantile(values, 1.0 - alpha)), int(np.isnan(values).sum()))


def block_bootstrap(statistic: Callable[[np.ndarray], float], n_items: int,
                    n_resamples: int, block: int, seed: int | np.random.Generator,
                    level: float = 0.95) -> tuple[float, float, float]:
    """Moving-block bootstrap of a statistic of item indices.

    Items are states in temporal order; blocks of consecutive states are
    resampled with replacement to respect residual serial dependence. Non-finite
    resamples are dropped silently here (``np.nanquantile``); use
    ``block_bootstrap_dropped`` to count them and ``block_bootstrap_counted`` for the
    DEC-0008 A3 rule. This is the first three items of ``block_bootstrap_dropped``.

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
    seed : int or np.random.Generator
        Seed, or a generator that is consumed.
    level : float, optional
        Confidence level.

    Returns
    -------
    tuple[float, float, float]
        Point estimate on all items, lower and upper percentile bounds.
    """
    return block_bootstrap_dropped(statistic, n_items, n_resamples, block, seed, level)[:3]


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
