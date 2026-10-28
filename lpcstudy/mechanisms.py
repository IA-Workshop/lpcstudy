"""LPC contribution study, experiment E: mechanisms (phase J, WU-0049).

DEVELOPMENT, exploratory: every number is a description of one development
realization, read as "consistent", "not consistent" or "not determined" by a
rule written here before any phase J result of E was seen. No causal claim
is made, and nothing here is set beside CONF-1. It runs offline on the state
dump of schema /3 (``lpcstudy.dump``) and on the run's ``results.json``.

Governing documents: the phase J plan (section 4.E) and the mathematics
specification (``...-phase-j-math-spec.md``), which governs: the amplification
mismatch uses ``H_0 = 1`` Lyapunov time (``H_ref``), restricted to the
horizons where both r.m.s. errors are at most ``0.5 sigma_x`` (as H2a(i)).

E-H2a, directional amplification (:func:`h2a_block`)
    Per test state, ``m(H) = ln[E_C(H) / E_C(H_0)] - ln[E_P(H) / E_P(H_0)]``
    where ``sqrt(E_C)`` and ``sqrt(E_P)`` are at most ``0.5`` at ``H`` and at
    ``H_0`` (other entries are excluded and counted). Reported by tercile of
    ``I`` (the oracle growth rate): the median ``m``, the drift ``w*(H) -
    w*(H_0)`` (same entries) and the uncentered error correlation ``C /
    sqrt(E_C E_P)`` (every state; it needs no restriction). The association
    of ``m`` with ``I`` is Spearman's rho with a moving-block interval (95%,
    the shared index sets, restricted to the kept states of each resample).

    Reading (fixed in advance). Over the horizons beyond ``H_0`` with at
    least 50 kept states: "consistent" (with the student's reading that the
    instability enters ``w*(H)`` through uneven growth) if at one of them
    the interval of Spearman(m, I) lies beyond the margin ``NEAR_ZERO`` on
    one side (lower bound > 0.1 or upper bound < -0.1; math spec addendum
    WU-0045c S2) and the median ``|drift|`` of the high-``I`` tercile
    exceeds that of the low tercile; "not consistent" if at every one of
    them the interval lies inside ``(-0.1, 0.1)``; otherwise "not
    determined", and "not determined (fewer than 50 kept states)" if no such
    horizon exists. With the same margin on both sides, the two determined
    words make contradictory claims on the true Spearman.

E-H2e, library size and correlation (:func:`h2e_block`)
    On the sweep states (the first ``n_test_sweep`` test states), per noise
    level of the library sweep, between the smallest and the largest library
    of the sweep (``10^3`` and ``10^5`` in the full preset): ``Delta corr =
    corr(10^5) - corr(10^3)``
    of the H2e error correlation (``sweep/.../err_corr_href``, centered over
    the oracle draws; 0 by convention where an error is constant over the
    draws, counted) and ``Delta R = (ln seed_sq(10^5) - ln seed_sq(10^3)) / 2``
    from ``h1a/rho=<g>/seed_sq`` (the change of ``R = ln eps / rho``; a
    non-finite or non-positive seed is excluded and counted). Stratified by
    terciles of R, O, I, N (core-cell oracle profile) and of ``Delta R``.
    Candidate mechanism (plan, stated before looking): the correlation rises
    most where R falls most, so ``median Delta corr > 0`` and Spearman(Delta
    corr, Delta R) ``< 0``.

    Reading (fixed in advance), on all valid states (primary, the H2e
    convention) and on the states whose correlation is non-zero at both
    sizes (sensitivity): "consistent" if the interval of the median ``Delta
    corr`` lies above 0 and that of Spearman lies below 0; "not consistent"
    if the Spearman interval lies above 0 or the median's below 0; otherwise
    "not determined". The final reading is the primary one if the two agree,
    else "not determined (depends on the zero-variance convention)".

E-H3c, A5 against A4 by system (:func:`h3c_block`, :func:`h3c_reading`)
    The H3c ratio and interval of the run (no verdict word), then per system:
    the share of the top 1% of states in the per-state A5 and A4 loss
    (``core/state_mse`` at ``H_ref``) and in ``|A5 - A4|``; lag
    autocorrelations of the per-state difference in time order and of its
    block means (block of the run's bootstrap); the chosen K and the leaf
    occupancy (``core/a5_leaf``, ``a5_leaf_calibration``); the within- and
    between-leaf variance of ``w*(H_ref)`` over (state, draw) pairs; the LPC
    marginals (quantiles, skewness, excess kurtosis, Sarle's bimodality
    coefficient ``BC``) and pairwise Spearman correlations of the oracle and
    the deployable profile; where the top 1% of ``|A5 - A4|`` states sit in
    the profile (mean percentile of each coordinate, share in the high-I
    tercile) and two geometric proxies of the Lorenz-63 lobe switch: the
    percentile of ``|x_t|`` and a sign change of ``x`` within the delay
    window.

    Candidate explanation (plan, stated before looking): Lorenz-63's wide
    interval comes from a heavy-tailed per-state loss in high-I states;
    Rössler's narrow interval from a near-unimodal profile. Reading (fixed
    in advance), per seed: "not determined (pattern not reproduced)" unless
    Lorenz-63 has the widest and Rössler the narrowest H3c interval. Then
    Lorenz-63 part: "consistent" if the top 1% of states carry at least 10%
    of ``sum |A5 - A4|`` and their median I percentile is at least 2/3;
    "not consistent" if that share is below 5% or the percentile below 1/2.
    Rössler part: "consistent" if every coordinate of the deployable profile
    (pooled over draws, the input of the A5 tree) has ``BC < 5/9`` (Sarle's
    unimodality rule); "not consistent" if two or more have ``BC > 5/9``.
    Overall: "consistent" if both parts are, "not consistent" if either is,
    else "not determined".

Randomness: the H2e interval indices come from ``make_rng(seed, system,
"bootstrap", "phase-J-H2e")`` (a new label); E-H2a uses the shared index sets
of ``contribution.bootstrap_generator``. Nothing else is random.
"""

from __future__ import annotations

import math
import warnings

import numpy as np
from scipy.stats import kurtosis, rankdata, skew

from .ablation import CONDITIONS
from .contribution import (
    SHAPLEY_LEVEL,
    SystemData,
    allocation_targets,
    resample_indices,
)
from .data import make_rng
from .statistics import endpoint_mc_error, percentile_interval

AMPLITUDE_LIMIT: float = 0.5
"""The r.m.s. restriction of the mismatch, in units of ``sigma_x`` (H2a(i))."""
MIN_KEPT: int = 50
"""A horizon of E-H2a enters the reading only with this many kept states."""
NEAR_ZERO: float = 0.1
"""E-H2a: a Spearman interval inside ``(-0.1, 0.1)`` reads as no association."""
TOP_SHARE: float = 0.01
"""The tail of E-H3c: the top 1% of states."""
HEAVY_TAIL: float = 0.10
"""E-H3c: the top 1% carry at least this share (10 times their count)."""
LIGHT_TAIL: float = 0.05
"""E-H3c: below this share the tail is not heavy."""
UNIMODAL_BC: float = 5.0 / 9.0
"""Sarle's bimodality coefficient threshold (uniform distribution)."""
QUANTILES: tuple[float, ...] = (0.05, 0.25, 0.5, 0.75, 0.95)
"""Quantiles of the marginal summaries."""
MAX_LAG: int = 5
"""Lags of the autocorrelation of the per-state difference."""


# ------------------------------------------------------------ small tools
def terciles(values: np.ndarray) -> tuple[np.ndarray, list[float]]:
    """Tercile labels 0, 1, 2 (low to high) and the two cut points.

    A value equal to a cut point goes to the lower group.
    """
    cuts = np.quantile(values, [1.0 / 3.0, 2.0 / 3.0])
    return np.searchsorted(cuts, values, side="left"), [float(c) for c in cuts]


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    """Spearman's rho (Pearson correlation of average ranks); NaN if constant."""
    rx, ry = rankdata(x), rankdata(y)
    rx, ry = rx - rx.mean(), ry - ry.mean()
    den = math.sqrt(float(np.sum(rx**2) * np.sum(ry**2)))
    return float(np.sum(rx * ry) / den) if den > 0 else float("nan")


def _interval_record(point: float, values: np.ndarray, level: float) -> dict:
    lower, upper, n_failed = percentile_interval(values, level)
    return {
        "estimate": point if np.isfinite(point) else None,
        "ci": [
            float(lower) if np.isfinite(lower) else None,
            float(upper) if np.isfinite(upper) else None,
        ],
        "ci_mc_se": list(endpoint_mc_error(values, level)),
        "n_failed_resamples": n_failed,
        "level": level,
    }


def spearman_row(
    x: np.ndarray,
    y: np.ndarray,
    index: np.ndarray,
    mask: np.ndarray | None = None,
    level: float = SHAPLEY_LEVEL,
) -> dict:
    """Spearman's rho on the masked states with a paired resample interval.

    Each resample keeps its draws of masked states (a state drawn twice
    counts twice); a resample with fewer than 3 kept states or a constant
    variable is failed and counted (M-7).
    """
    keep = np.ones(len(x), bool) if mask is None else mask
    point = spearman(x[keep], y[keep]) if keep.sum() >= 3 else float("nan")
    values = np.empty(len(index))
    for b, rows in enumerate(index):
        rows = rows[keep[rows]]
        values[b] = spearman(x[rows], y[rows]) if rows.size >= 3 else np.nan
    row = _interval_record(point, values, level)
    row["n_states"] = int(keep.sum())
    return row


def median_row(
    values: np.ndarray,
    index: np.ndarray,
    mask: np.ndarray | None = None,
    level: float = SHAPLEY_LEVEL,
) -> dict:
    """Median of the masked states with a resample interval.

    A resample with no masked state has a NaN median: failed and counted
    (M-7) by ``percentile_interval``.
    """
    keep = np.ones(len(values), bool) if mask is None else mask
    point = float(np.median(values[keep])) if keep.any() else float("nan")
    picked = np.where(keep[index], values[index], np.nan)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)  # all-NaN resample
        boot = np.nanmedian(picked, axis=1)
    row = _interval_record(point, boot, level)
    row["n_states"] = int(keep.sum())
    return row


def bimodality_coefficient(values: np.ndarray) -> float:
    """Sarle's ``BC = (g^2 + 1) / (k + 3 (n - 1)^2 / ((n - 2)(n - 3)))``.

    ``g`` is the sample skewness and ``k`` the sample excess kurtosis, both
    bias-corrected; ``BC > 5/9`` suggests more than one mode.
    """
    n = len(values)
    g = float(skew(values, bias=False))
    k = float(kurtosis(values, bias=False))
    return (g**2 + 1.0) / (k + 3.0 * (n - 1) ** 2 / ((n - 2) * (n - 3)))


def tail_share(values: np.ndarray, share: float = TOP_SHARE) -> float:
    """Share of ``sum(values)`` carried by the top ``share`` of entries.

    ``values`` must be non-negative; the top count is ``ceil(share n)``.
    """
    if np.any(values < 0):
        raise ValueError("tail_share needs non-negative values")
    k = max(1, math.ceil(share * len(values)))
    total = float(values.sum())
    return (
        float(np.sort(values)[-k:].sum() / total) if total > 0 else float("nan")
    )


def autocorrelation(values: np.ndarray, lags: int) -> list[float]:
    """Sample autocorrelations at lags ``1..lags`` (mean removed, biased)."""
    centred = values - values.mean()
    den = float(np.sum(centred**2))
    if den == 0:
        return [float("nan")] * lags
    return [
        float(np.sum(centred[:-k] * centred[k:]) / den)
        for k in range(1, lags + 1)
    ]


def variance_split(values: np.ndarray, groups: np.ndarray) -> dict:
    """Within- and between-group variance (population form, pooled).

    ``within + between = total`` (the law of total variance).
    """
    total = float(np.var(values))
    mean = float(values.mean())
    within = between = 0.0
    for g in np.unique(groups):
        part = values[groups == g]
        within += float(np.sum((part - part.mean()) ** 2))
        between += len(part) * (float(part.mean()) - mean) ** 2
    n = len(values)
    return {
        "total": total,
        "within": within / n,
        "between": between / n,
        "within_share": within / n / total if total > 0 else float("nan"),
    }


def marginal_summary(profile: np.ndarray) -> dict:
    """Quantiles, skewness, excess kurtosis and BC of each coordinate."""
    out = {}
    for j, name in enumerate(CONDITIONS):
        x = profile[:, j]
        out[name] = {
            "quantiles": dict(
                zip(
                    (f"{q:g}" for q in QUANTILES),
                    (float(v) for v in np.quantile(x, QUANTILES)),
                )
            ),
            "skewness": float(skew(x, bias=False)),
            "excess_kurtosis": float(kurtosis(x, bias=False)),
            "bimodality_coefficient": bimodality_coefficient(x),
        }
    return out


def pair_spearman(profile: np.ndarray) -> dict[str, float]:
    """Spearman's rho of every pair of coordinates."""
    out = {}
    for j in range(4):
        for k in range(j + 1, 4):
            out[CONDITIONS[j] + CONDITIONS[k]] = spearman(
                profile[:, j], profile[:, k]
            )
    return out


# ------------------------------------------------------------------ E-H2a
def amplification_mismatch(
    e_c: np.ndarray, e_p: np.ndarray, ref: int, limit: float = AMPLITUDE_LIMIT
) -> tuple[np.ndarray, np.ndarray]:
    """``m(H)`` per state and horizon, and the entries kept by the restriction.

    ``m = ln[E_C(H) / E_C(H_0)] - ln[E_P(H) / E_P(H_0)]`` with ``H_0`` the
    column ``ref``; an entry is kept where ``sqrt(E_C)`` and ``sqrt(E_P)`` are
    at most ``limit`` at ``H`` and at ``H_0`` and every moment is positive.
    Inputs ``(n, H)``; ``m`` is NaN only where a moment is not positive.
    """
    positive = (e_c > 0) & (e_p > 0)
    small = (np.sqrt(e_c) <= limit) & (np.sqrt(e_p) <= limit) & positive
    kept = small & small[:, ref : ref + 1]
    with np.errstate(divide="ignore", invalid="ignore"):
        m = np.where(
            positive & positive[:, ref : ref + 1],
            np.log(e_c / e_c[:, ref : ref + 1])
            - np.log(e_p / e_p[:, ref : ref + 1]),
            np.nan,
        )
    return m, kept


def error_correlation(
    e_c: np.ndarray, e_p: np.ndarray, cross: np.ndarray
) -> np.ndarray:
    """The uncentered correlation ``C / sqrt(E_C E_P)`` (NaN if a moment is 0)."""
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(
            (e_c > 0) & (e_p > 0), cross / np.sqrt(e_c * e_p), np.nan
        )


def _group_median(
    values: np.ndarray, mask: np.ndarray, groups: np.ndarray
) -> list[float | None]:
    out: list[float | None] = []
    for g in range(3):
        keep = mask & (groups == g)
        out.append(float(np.median(values[keep])) if keep.any() else None)
    return out


def _curve_by_group(
    values: np.ndarray, mask: np.ndarray, groups: np.ndarray, min_count: int
) -> list[list[float | None]]:
    """Median per group and column (None where fewer than ``min_count``)."""
    out = []
    for g in range(3):
        row: list[float | None] = []
        for h in range(values.shape[1]):
            keep = mask[:, h] & (groups == g)
            row.append(
                float(np.median(values[keep, h]))
                if keep.sum() >= min_count
                else None
            )
        out.append(row)
    return out


def h2a_block(data: SystemData, index: np.ndarray) -> dict:
    """E-H2a on the test states (oracle moments on ``1..H_max``)."""
    t = data.test
    e_c, e_p, cross = t["E_C"], t["E_P"], t["C"]
    ref = int(data.horizons[data.ref_index]) - 1
    m, kept = amplification_mismatch(e_c, e_p, ref)
    w_star = allocation_targets(e_c, e_p, cross).w_star
    drift = w_star - w_star[:, ref : ref + 1]
    corr = error_correlation(e_c, e_p, cross)
    rate = t["profile_oracle"][:, 2]
    groups, cuts = terciles(rate)
    everywhere = np.isfinite(corr)
    rows = {}
    for column, h in enumerate(data.horizons):
        col = int(h) - 1
        keep = kept[:, col]
        row = {
            "horizon": data.horizon_label(int(h)),
            "n_kept": int(keep.sum()),
            "median_m": float(np.median(m[keep, col])) if keep.any() else None,
            "median_m_by_tercile": _group_median(m[:, col], keep, groups),
            "median_drift_by_tercile": _group_median(
                drift[:, col], keep, groups
            ),
            "median_abs_drift_by_tercile": _group_median(
                np.abs(drift[:, col]), keep, groups
            ),
            "median_corr_by_tercile": _group_median(
                corr[:, col], everywhere[:, col], groups
            ),
        }
        if col != ref:
            row["spearman_m_I"] = spearman_row(m[:, col], rate, index, keep)
            row["spearman_abs_m_I"] = spearman_row(
                np.abs(m[:, col]), rate, index, keep
            )
        rows[str(int(h))] = row
    reading = h2a_reading(rows, ref + 1)
    grid = np.arange(1, e_c.shape[1] + 1)
    return {
        "reference_horizon": ref + 1,
        "steps_per_lt": data.steps_per_lt,
        "amplitude_limit": AMPLITUDE_LIMIT,
        "I_tercile_cuts": cuts,
        "n_states": int(len(rate)),
        "n_nonpositive_moments": int(np.sum((e_c <= 0) | (e_p <= 0))),
        "n_corr_undefined": int(np.sum(~everywhere)),
        "by_horizon": rows,
        "reading": reading,
        "figure": {
            "H": grid.tolist(),
            "n_kept": kept.sum(axis=0).tolist(),
            # Entries outside ``kept`` are placeholders, never read.
            "median_m": _curve_by_group(
                np.where(kept, m, 0.0), kept, groups, 10
            ),
            "median_drift": _curve_by_group(drift, kept, groups, 10),
            "median_corr": _curve_by_group(
                np.where(everywhere, corr, 0.0), everywhere, groups, 10
            ),
        },
    }


def h2a_reading(rows: dict, ref: int) -> dict:
    """The E-H2a reading of the module docstring from the horizon rows."""
    usable = [
        (h, r)
        for h, r in rows.items()
        if int(h) > ref and r["n_kept"] >= MIN_KEPT
    ]
    if not usable:
        return {"reading": "not determined (fewer than 50 kept states)"}
    support, null = [], []
    for h, r in usable:
        lower, upper = r["spearman_m_I"]["ci"]
        low_drift, _, high_drift = r["median_abs_drift_by_tercile"]
        beyond = (lower is not None and lower > NEAR_ZERO) or (
            upper is not None and upper < -NEAR_ZERO
        )
        larger = (
            low_drift is not None
            and high_drift is not None
            and high_drift > low_drift
        )
        if beyond and larger:
            support.append(h)
        if (
            lower is not None
            and upper is not None
            and lower > -NEAR_ZERO
            and upper < NEAR_ZERO
        ):
            null.append(h)
    if support:
        text = "consistent"
    elif len(null) == len(usable):
        text = "not consistent"
    else:
        text = "not determined"
    return {
        "reading": text,
        "horizons_used": [h for h, _ in usable],
        "horizons_supporting": support,
        "horizons_null": null,
    }


# ------------------------------------------------------------------ E-H2e
def h2e_block(
    data: SystemData,
    arrays: dict[str, np.ndarray],
    seed: int,
    n_resamples: int,
    block: int,
) -> dict:
    """E-H2e on the sweep states, per noise level of the library sweep."""
    n_sweep = int(arrays["meta/n_test_sweep"])
    profile = data.test["profile_oracle"][:n_sweep]
    sizes = [int(v) for v in arrays["h1a/n_lib"]]
    lo, hi = int(np.argmin(sizes)), int(np.argmax(sizes))
    ends = (sizes[lo], sizes[hi])
    index = resample_indices(
        n_sweep,
        n_resamples,
        block,
        make_rng(seed, data.system, "bootstrap", "phase-J-H2e"),
    )
    strata = {
        name: terciles(profile[:, j]) for j, name in enumerate(CONDITIONS)
    }
    out = {"n_sweep_states": n_sweep, "library_ends": list(ends), "levels": {}}
    for rho in arrays["h1a/noise_levels"]:
        key = f"{float(rho):g}"
        corr = {
            size: arrays[f"sweep/rho={key}|n_lib={size}/err_corr_href"]
            for size in ends
        }
        seed_sq = arrays[f"h1a/rho={key}/seed_sq"]
        s_lo, s_hi = seed_sq[:, lo], seed_sq[:, hi]
        seed_ok = (
            np.isfinite(s_lo) & np.isfinite(s_hi) & (s_lo > 0) & (s_hi > 0)
        )
        with np.errstate(divide="ignore", invalid="ignore"):
            delta_r = np.where(
                seed_ok, 0.5 * (np.log(s_hi) - np.log(s_lo)), np.nan
            )
        c_lo, c_hi = corr[ends[0]], corr[ends[1]]
        corr_ok = np.isfinite(c_lo) & np.isfinite(c_hi)
        delta_c = np.where(corr_ok, c_hi - c_lo, np.nan)
        valid = seed_ok & corr_ok
        defined = valid & (c_lo != 0.0) & (c_hi != 0.0)
        by = {}
        for name, (groups, cuts) in strata.items():
            by[name] = {
                "cuts": cuts,
                "median_delta_corr": _group_median(delta_c, valid, groups),
                "mean_delta_corr": [
                    (
                        float(delta_c[valid & (groups == g)].mean())
                        if (valid & (groups == g)).any()
                        else None
                    )
                    for g in range(3)
                ],
                "median_delta_R": _group_median(delta_r, valid, groups),
            }
        dr_groups = np.full(len(valid), -1)  # invalid states: no group
        dr_groups[valid], dr_cuts = terciles(delta_r[valid])
        by["delta_R"] = {
            "cuts": dr_cuts,
            "median_delta_corr": _group_median(delta_c, valid, dr_groups),
            "median_delta_R": _group_median(delta_r, valid, dr_groups),
        }
        parts = {}
        for part, mask in (("all", valid), ("both_defined", defined)):
            # Outside ``mask`` the inputs are placeholders, never read.
            parts[part] = {
                "median_delta_corr": median_row(delta_c, index, mask),
                "spearman_delta_corr_delta_R": spearman_row(
                    np.where(valid, delta_c, 0.0),
                    np.where(valid, delta_r, 0.0),
                    index,
                    mask,
                ),
            }
            parts[part]["reading"] = h2e_part_reading(parts[part])
        primary = parts["all"]["reading"]
        final = (
            primary
            if primary == parts["both_defined"]["reading"]
            else "not determined (depends on the zero-variance convention)"
        )
        out["levels"][key] = {
            "n_valid": int(valid.sum()),
            "n_seed_excluded": int((~seed_ok).sum()),
            "n_corr_nonfinite": int((~corr_ok).sum()),
            "n_corr_zero_smallest": int(np.sum(corr_ok & (c_lo == 0.0))),
            "n_corr_zero_largest": int(np.sum(corr_ok & (c_hi == 0.0))),
            "n_both_defined": int(defined.sum()),
            "median_corr": {
                "smallest": float(np.median(c_lo[corr_ok])),
                "largest": float(np.median(c_hi[corr_ok])),
            },
            "median_delta_R": float(np.median(delta_r[valid])),
            "by_tercile": by,
            "parts": parts,
            "reading": final,
            "figure": {
                "delta_R": delta_r[valid].tolist(),
                "delta_corr": delta_c[valid].tolist(),
                "zero_at_smallest": (c_lo == 0.0)[valid].tolist(),
            },
        }
    return out


def h2e_part_reading(part: dict) -> str:
    """The E-H2e reading of one state set (module docstring)."""
    m_lo, m_hi = part["median_delta_corr"]["ci"]
    s_lo, s_hi = part["spearman_delta_corr_delta_R"]["ci"]
    if (s_lo is not None and s_lo > 0) or (m_hi is not None and m_hi < 0):
        return "not consistent"
    if m_lo is not None and m_lo > 0 and s_hi is not None and s_hi < 0:
        return "consistent"
    return "not determined"


# ------------------------------------------------------------------ E-H3c
def h3c_block(
    data: SystemData,
    arrays: dict[str, np.ndarray],
    system_results: dict,
    block: int,
) -> dict:
    """E-H3c descriptives of one system (no interval beyond the run's)."""
    t = data.test
    ref = data.ref_index
    h3c = system_results["H3c"]
    loss5 = t["state_mse/A5"][:, ref]
    loss4 = t["state_mse/A4"][:, ref]
    diff = loss5 - loss4
    n = len(diff)
    k = max(1, math.ceil(TOP_SHARE * n))
    top = np.argsort(np.abs(diff), kind="stable")[-k:]
    top5 = np.argsort(loss5, kind="stable")[-k:]
    oracle = t["profile_oracle"]
    deploy = t["profile_deployable"].reshape(-1, 4)
    pct = (rankdata(oracle, axis=0) - 0.5) / n
    groups, _ = terciles(oracle[:, 2])
    x_t = t["delay_clean"][:, 0]
    x_pct = (rankdata(np.abs(x_t)) - 0.5) / n
    switch = np.any(
        np.sign(t["delay_clean"]) != np.sign(t["delay_clean"][:, :1]), axis=1
    )
    n_blocks = n // block
    means = diff[: n_blocks * block].reshape(n_blocks, block).mean(axis=1)
    leaf_test = arrays["core/a5_leaf"]
    leaf_cal = arrays["core/a5_leaf_calibration"]
    h = int(data.horizons[ref]) - 1
    w_star = allocation_targets(
        t["E_C"][:, h], t["E_P"][:, h], t["C"][:, h]
    ).w_star
    w_pairs = np.repeat(w_star, leaf_test.shape[1])

    def occupancy(leaves: np.ndarray) -> dict:
        ids, counts = np.unique(leaves, return_counts=True)
        return {
            "n_leaves_used": int(len(ids)),
            "counts": {str(int(i)): int(c) for i, c in zip(ids, counts)},
            "largest_share": float(counts.max() / counts.sum()),
            "smallest_share": float(counts.min() / counts.sum()),
        }

    def location(rows: np.ndarray) -> dict:
        return {
            "mean_percentile": {
                name: float(pct[rows, j].mean())
                for j, name in enumerate(CONDITIONS)
            },
            "median_I_percentile": float(np.median(pct[rows, 2])),
            "share_high_I_tercile": float(np.mean(groups[rows] == 2)),
            "median_abs_x_percentile": float(np.median(x_pct[rows])),
            "share_sign_change_in_window": float(np.mean(switch[rows])),
            "share_of_signed_difference": (
                float(diff[rows].sum() / diff.sum())
                if diff.sum() != 0
                else None
            ),
        }

    sorted_abs = np.sort(np.abs(diff))[::-1]
    cumulative = np.cumsum(sorted_abs) / sorted_abs.sum()
    bins = 40
    hist = {}
    for j, name in enumerate(CONDITIONS):
        lo, hi = np.quantile(deploy[:, j], [0.001, 0.999])
        edges = np.linspace(lo, hi, bins + 1)
        counts, _ = np.histogram(deploy[:, j], edges)  # outside: counted
        hist[name] = {
            "edges": edges.tolist(),
            "counts": counts.tolist(),
            "n_outside_shown": int(
                np.sum((deploy[:, j] < lo) | (deploy[:, j] > hi))
            ),
            "top_states": oracle[top, j].tolist(),
        }
    return {
        "H3c": {
            "ratio": h3c.get("A5_over_A4_mse"),
            "ci": h3c.get("ci"),
            "level": h3c.get("level"),
            "width": (
                h3c["ci"][1] - h3c["ci"][0]
                if None not in h3c.get("ci", [None, None])
                else None
            ),
            "n_failed_resamples": h3c.get("n_failed_resamples"),
        },
        "n_states": n,
        "top_count": k,
        "mean_loss": {"A5": float(loss5.mean()), "A4": float(loss4.mean())},
        "tail_share": {
            "A5": tail_share(loss5),
            "A4": tail_share(loss4),
            "abs_difference": tail_share(np.abs(diff)),
        },
        "autocorrelation_difference": autocorrelation(diff, MAX_LAG),
        "block_means": {
            "block": block,
            "lag1_autocorrelation": autocorrelation(means, 1)[0],
            "variance_ratio": (
                float(np.var(means) * block / np.var(diff))
                if np.var(diff) > 0
                else None
            ),
        },
        "chosen_K": int(system_results["fitted"]["chosen_K"]),
        "occupancy_test": occupancy(leaf_test),
        "occupancy_calibration": occupancy(leaf_cal),
        "w_star_variance_by_leaf": variance_split(w_pairs, leaf_test.ravel()),
        "marginals_oracle": marginal_summary(oracle),
        "marginals_deployable": marginal_summary(deploy),
        "spearman_oracle": pair_spearman(oracle),
        "spearman_deployable": pair_spearman(deploy),
        "top_abs_difference": location(top),
        "top_A5_loss": location(top5),
        "figure": {
            "cumulative_share": cumulative[: max(10 * k, 100)].tolist(),
            "n_states": n,
            "histograms": hist,
        },
    }


def h3c_reading(blocks: dict[str, dict]) -> dict:
    """The E-H3c reading of one seed from its three systems' blocks."""
    widths = {s: b["H3c"]["width"] for s, b in blocks.items()}
    needed = ("lorenz63", "rossler", "chua")
    if any(widths.get(s) is None for s in needed):
        return {
            "reading": "not determined (an H3c interval is missing)",
            "widths": widths,
        }
    reproduced = widths["lorenz63"] == max(widths[s] for s in needed) and (
        widths["rossler"] == min(widths[s] for s in needed)
    )
    lorenz = blocks["lorenz63"]
    share = lorenz["tail_share"]["abs_difference"]
    pct = lorenz["top_abs_difference"]["median_I_percentile"]
    if share >= HEAVY_TAIL and pct >= 2.0 / 3.0:
        lorenz_part = "consistent"
    elif share < LIGHT_TAIL or pct < 0.5:
        lorenz_part = "not consistent"
    else:
        lorenz_part = "not determined"
    bc = {
        name: v["bimodality_coefficient"]
        for name, v in blocks["rossler"]["marginals_deployable"].items()
    }
    n_bimodal = sum(v > UNIMODAL_BC for v in bc.values())
    if all(v < UNIMODAL_BC for v in bc.values()):
        rossler_part = "consistent"
    elif n_bimodal >= 2:
        rossler_part = "not consistent"
    else:
        rossler_part = "not determined"
    if not reproduced:
        overall = "not determined (pattern not reproduced)"
    elif "not consistent" in (lorenz_part, rossler_part):
        overall = "not consistent"
    elif lorenz_part == rossler_part == "consistent":
        overall = "consistent"
    else:
        overall = "not determined"
    return {
        "reading": overall,
        "pattern_reproduced": bool(reproduced),
        "widths": widths,
        "lorenz63_part": lorenz_part,
        "lorenz63_tail_share": share,
        "lorenz63_top_median_I_percentile": pct,
        "rossler_part": rossler_part,
        "rossler_bimodality": bc,
    }
