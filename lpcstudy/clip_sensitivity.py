"""Clip sensitivity of the verdicts (WU-0002.11e).

**Needs owner review before freeze** (verdict reporting and statistics code).
Background: DEC-0017 Q6 and DEC-0026 item 8.

The study measures forecast errors against the noise-free truth and clips any
error larger than ``ERROR_CLIP`` = 10 sigma_x (sigma_x is the standard deviation
of the x-coordinate; v3 section 4). The clip is part of the quantity being
estimated, so no verdict depends on it. This module only reports how sensitive
each verdict is to the clip: it asks what would change if the clip level were
doubled to 20 sigma_x. It reads the arrays that the forecast code already stores
and recomputes the verdict statistics on copies. It never changes a verdict,
never marks a result provisional (OD6), and draws no new random numbers.

Every bootstrap is rebuilt from a fresh ``make_rng`` generator with exactly the
labels (system included) of the verdict it re-reads (WU-0002.14). The resample
indices are then the same, and no shared generator advances (DEC-0012).
Otherwise the flags would measure resampling noise instead of the clip.

``experiments.py`` calls ``clip_sensitivity_block`` for each system and stores
the result in ``results["clip_sensitivity"]``; ``report.py`` prints it as the
``clip`` column. Read ``clip_sensitivity_block`` and ``_compute`` first; the
``*_part`` functions each re-read one verdict.

The perturbation P2
-------------------

Every clipped PLP error at ``H_ref`` (stored as ``sigma * L``, with ``sigma =
+-1`` the sign and ``L`` the clip level) moves to ``sigma * 2 L``. Everything
else is held fixed: the states, the draws, the unclipped entries, the proxies,
the A3 network, the regime tree, its assignment of draws to regimes, the chosen
``K``, and the bootstrap resample indices. On the stored arrays the update is
exact:

* an evaluation draw: ``e_P -> e_P + sigma L``;
* the oracle moments of a state with ``q`` clipped draws out of ``M`` and ``chi
  = (1/M) sum sigma e_C`` over them: ``E e_P^2 -> E e_P^2 + 3 L^2 q / M``, ``E
  e_C e_P -> E e_C e_P + L chi``, and ``E e_C^2`` unchanged (CP never clips,
  H-CP).

For a raw value that is non-finite or has ``|raw| >= 2 L``, this is what the
same code gives at clip level ``2 L``. For a finite raw value in ``(L, 2 L)`` it
is the extreme case (the raw value is not stored), so the flag can only fire
more often, never less.

The flag
--------

Take a verdict-bearing estimate ``T`` with interval ``[lo, hi]`` and verdict
``v``, and the same quantities ``T2``, ``v2`` under P2. Let ``delta = T2 - T``
and ``hw = (hi - lo) / 2``. Then ``flag = (10 |delta| > hw) or (v2 != v)``,
multiplied out so that the edge is exact in floating point.

Each verdict belongs to one of four tiers. **A**: exact recomputation (H2c, H2d,
H3c, H1b(PLP), H2a(ii), H2b(i), H2b(ii)). **B**: a bound from counts (H2e, the
median of per-state differences). **C**: a count of affected states (Q-N, H3b).
**D**: invariant under P2 by an argument that is checked at run time (H1c;
H2a(i) through ``L^2 / M > max(theta_max, r_lin)^2``; H3a through "no clipped
test evaluation entry"). H2a(i) is tier D and H2a(ii) is tier A.

A quantity that cannot be computed is reported with ``status = "not_computed"``
and a ``reason``, never as a False flag.

Counted, not silent (DEF-0001, WU-0004f). The 1e-12 floor of the H1b regression
is counted in the part entry (``n_floored``, ``n_floored_2L``; see ``h1b_part``
for what is proved about it). Every exception that this report-only block
swallows is counted in ``n_caught_exceptions`` of the block. Both counts are
mirrored in ``handling.result_counts``.
"""

from __future__ import annotations

import logging
from dataclasses import replace
from types import SimpleNamespace

import numpy as np

from . import analysis as an
from .allocation import deployable_profile, global_weight, regime_weight
from .config import StudyConfig
from .data import make_rng
from .ensemble import DRAW_COLUMN, ERROR_CLIP, EnsembleMoments
from .oracle import oracle_weight
from .statistics import (
    block_bootstrap_counted,
    bootstrap_values,
    criterion_verdict,
    ols_slope,
    percentile_interval,
)

LOG = logging.getLogger("lpcstudy")

# The clip level of P2 (units of sigma_x): a doubling, upward only (the
# clipped second moments are lower bounds of the unclipped ones; a halving
# would clip regular on-attractor errors).
PERTURBED_LEVEL: float = 2.0 * ERROR_CLIP

# A shift of one tenth of the interval half-width is immaterial (NVVUQ.9: a
# non-sampling row at least 10 times below the sampling half-width): the flag
# fires when ``FLAG_FACTOR * |delta| > hw``.
FLAG_FACTOR: float = 10.0

# Rules whose per-state MSE at ``H_ref`` is recomputed (``A*`` feeds no
# verdict).
STATE_RULES: tuple[str, ...] = ("A0", "A1", "A2", "A3", "A4", "A5", "A4o")

INVARIANCE_EXACT = "exact"
INVARIANCE_NOT_GUARANTEED = "not guaranteed"
INVARIANCE_OUTSIDE = "outside the invariance hypothesis"
INVARIANCE_NOT_COMPUTED = "not_computed"


# --- The perturbation (pure functions) ---
def clipped_draws(handled: np.ndarray) -> np.ndarray:
    """Return, per state, the number of clipped PLP draws at ``H_ref``.

    A draw counts if its error is finite beyond the clip or non-finite.

    Parameters
    ----------
    handled : np.ndarray
        The per-state ``handled`` array of moments or evaluation draws,
        shape ``(n, len(DRAW_COUNTERS))``.

    Returns
    -------
    np.ndarray
        Shape ``(n,)``, int64: ``error_clips_plp_href +
        error_clips_nonfinite_href``.
    """
    return (
        handled[:, DRAW_COLUMN["error_clips_plp_href"]]
        + handled[:, DRAW_COLUMN["error_clips_nonfinite_href"]]
    )


def perturb_moments(
    moments: EnsembleMoments, column: int, n_draws: int
) -> EnsembleMoments:
    """Return the oracle moments after P2.

    Every clipped PLP error at ``H_ref`` moves from ``+-clip`` to ``+-2 clip``.
    Only the second moments ``sq_plp`` and ``cross`` at ``column`` change (the
    increments are in the module docstring); ``sq_cp`` is unchanged under H-CP.
    **The first moment ``mean_plp``, the correlation fields and ``kept`` are NOT
    updated.** The result is meant for ``oracle_weight``, ``curvature``,
    ``global_weight`` and ``regime_weight``, which read the three second moments
    only. The input is not modified, and a state with no clipped draw gets ``+
    0.0`` (bitwise unchanged).

    The ``1e-300`` floors of ``oracle_weight``, ``global_weight`` and
    ``regime_weight`` that run on these perturbed moments are not counted here,
    by this argument (DEF-0001, WU-0004f O-2). The curvature is ``c = E sq_cp -
    2 E cross + E sq_plp``. With the CP sentinel at 0 (checked by ``_block``: CP
    never clips, so ``|e_C| <= L`` and ``|chi| <= L q / M``), the perturbation
    changes it by ``c' - c = 3 L^2 q / M - 2 L chi >= L^2 q / M >= 0``. With ``q
    = 0`` it is bitwise unchanged. So a floor binds under P2 only where it
    already binds in the original, and those cases are counted by
    ``curvature_floor`` and ``pooled_curvature_floor``.

    Parameters
    ----------
    moments : EnsembleMoments
        Moments built by ``ensemble_moments`` with a reference horizon (they
        carry ``handled`` and ``clip_cross_ref``).
    column : int
        Column of ``H_ref`` in the moment arrays.
    n_draws : int
        Oracle draws ``M`` per state.

    Returns
    -------
    EnsembleMoments
        A copy with the perturbed ``sq_plp`` and ``cross``.

    Raises
    ------
    ValueError
        If the moments carry no ``handled`` or no ``clip_cross_ref``
        (hand-built, or built without a reference horizon).
    """
    if moments.handled is None or moments.clip_cross_ref is None:
        raise ValueError(
            "perturb_moments needs moments with handled and clip_cross_ref "
            "(built by ensemble_moments with a reference horizon)"
        )
    sq_plp, cross = moments.sq_plp.copy(), moments.cross.copy()
    sq_plp[:, column] = (
        sq_plp[:, column]
        + 3.0
        * ERROR_CLIP
        * ERROR_CLIP
        * clipped_draws(moments.handled)
        / n_draws
    )
    cross[:, column] = cross[:, column] + ERROR_CLIP * moments.clip_cross_ref
    return replace(moments, sq_plp=sq_plp, cross=cross)


def perturb_errors(plp_err: np.ndarray, sign: np.ndarray) -> np.ndarray:
    """Return the PLP errors after P2: ``e_P + sign * ERROR_CLIP``.

    ``sign`` is 0 where the entry was not clipped.

    Parameters
    ----------
    plp_err : np.ndarray
        Stored (clipped) PLP errors at ``H_ref``, any shape.
    sign : np.ndarray
        ``clip_sign_ref`` of the same shape, values -1, 0, +1.

    Returns
    -------
    np.ndarray
        New array; entries with ``sign == 0`` are bitwise equal to ``plp_err``.
    """
    return plp_err + ERROR_CLIP * sign


def rule_state_mse(
    weight: np.ndarray, cp_err: np.ndarray, plp_err: np.ndarray
) -> np.ndarray:
    """Return the per-state squared error of an allocation rule at one horizon.

    The expression is the one used by ``score_rules``, so the recomputation can
    be checked against the stored baseline.

    Parameters
    ----------
    weight, cp_err, plp_err : np.ndarray
        Arrays of shape ``(n, E)``: the weight on CP and the two errors at
        ``H_ref``.

    Returns
    -------
    np.ndarray
        Shape ``(n,)``: ``mean_r (w e_C + (1 - w) e_P)^2``.
    """
    err = weight * cp_err + (1 - weight) * plp_err
    return (err**2).mean(axis=1)


# --- The flag rule ---
def flag_rule(
    delta: float, lower: float, upper: float, verdict: str, verdict_2l: str
) -> tuple[bool, float | None]:
    """Return the flag: ``10 |delta| > hw`` or a changed verdict (OD2).

    Here ``hw = (upper - lower) / 2`` is the half-width of the reported
    interval. The inequality is strict and is written multiplied out (never
    ``|delta| / hw > 0.1``), so the edge is exact in floating point. If ``hw``
    is not finite (failed resamples at the A3 tail), only the verdict clause
    applies. If ``hw = 0``, the first clause reads ``delta != 0``.

    Parameters
    ----------
    delta : float
        ``T2 - T``, the change of the estimate.
    lower, upper : float
        The reported interval of the verdict (the original, not the
        perturbed one).
    verdict, verdict_2l : str
        The verdict and the verdict recomputed under P2.

    Returns
    -------
    tuple[bool, float | None]
        The flag and the ratio ``|delta| / hw`` (``None`` when ``hw`` is not
        finite or is 0).
    """
    half_width = (upper - lower) / 2.0
    usable = bool(np.isfinite(half_width))
    flag = bool(
        (usable and FLAG_FACTOR * abs(delta) > half_width)
        or verdict_2l != verdict
    )
    ratio = (
        float(abs(delta) / half_width) if usable and half_width > 0.0 else None
    )
    return flag, ratio


def not_computed(reason: str, n_clipped: int = 0, bound: bool = False) -> dict:
    """Return an entry for a quantity that cannot be computed.

    The entry is visible in the results and is never a False flag (PRIME.4).
    """
    out = {
        "status": "not_computed",
        "reason": reason,
        "delta_bound" if bound else "delta": None,
        "ratio": None,
        "flag": None,
        "n_clipped_inputs": int(n_clipped),
    }
    if not bound:
        out["verdict_2L"] = None
    return out


def part_entry(
    estimate: float | None,
    interval: list | None,
    verdict: str,
    estimate_2l: float | None,
    interval_2l: list | None,
    verdict_2l: str,
    n_clipped: int,
) -> dict:
    """Return the clip-sensitivity entry of one decided part (tier A).

    Parameters
    ----------
    estimate, interval, verdict
        ``T``, its interval and its verdict as the verdict code reports them
        (``None`` if it was not computed).
    estimate_2l, interval_2l, verdict_2l
        The same under P2 (``interval_2l`` is only checked for presence).
    n_clipped : int
        Clipped ``H_ref`` draws among the perturbed inputs of this part (0
        means the part is not affected).

    Returns
    -------
    dict
        ``status``, ``reason``, ``delta`` (``T2 - T``), ``ratio`` (``|delta|
        / hw``), ``flag``, ``verdict_2L`` and ``n_clipped_inputs``. The
        status is "not_computed", with a ``reason`` and no flag, if ``T`` or
        ``T2`` is absent or not finite.
    """
    if estimate is None or interval is None:
        return not_computed("the verdict itself is not computed", n_clipped)
    if not np.isfinite(estimate):
        return not_computed("estimate not finite", n_clipped)
    if (
        estimate_2l is None
        or interval_2l is None
        or not np.isfinite(estimate_2l)
    ):
        return not_computed("estimate at 20 sigma_x not finite", n_clipped)
    delta = float(estimate_2l) - float(estimate)
    flag, ratio = flag_rule(
        delta, interval[0], interval[1], verdict, verdict_2l
    )
    return {
        "status": "computed",
        "reason": None,
        "delta": delta,
        "ratio": ratio,
        "flag": flag,
        "verdict_2L": verdict_2l,
        "n_clipped_inputs": int(n_clipped),
    }


def median_bound(diffs: np.ndarray, n_changed: int) -> float:
    """Return the largest possible move of the median (H2e, tier B).

    The move is the most the median can shift when at most ``n_changed`` values
    change.

    This is the bound for H2e (tier B). Let ``d(1) <= ... <= d(n)`` be the
    sorted values and ``a = n_changed``. Changing at most ``a`` values of the
    sample keeps the median inside ``[d(m+1-a), d(m+1+a)]`` for ``n = 2m + 1``,
    and inside ``[(d(m-a) + d(m+1-a)) / 2, (d(m+a) + d(m+1+a)) / 2]`` for ``n =
    2m``. An index below 1 is replaced by the lower range limit -2, and one
    above ``n`` by +2 (the values are correlation differences, so they lie in
    ``[-2, 2]``).

    Parameters
    ----------
    diffs : np.ndarray
        The per-state differences, finite, 1-D, not empty.
    n_changed : int
        ``a``: the number of states whose value may change.

    Returns
    -------
    float
        The larger of the distances from the median to the two limits.

    Raises
    ------
    ValueError
        If ``diffs`` is empty or not finite, or ``n_changed`` is negative.
    """
    d = np.sort(np.asarray(diffs, dtype=float).ravel())
    if d.size == 0 or not np.all(np.isfinite(d)) or n_changed < 0:
        raise ValueError(
            "median_bound needs finite differences and n_changed >= 0"
        )
    n, a = d.size, int(n_changed)

    def at(
        j: int,
    ) -> float:  # 1-based order statistic, the range limit outside 1..n
        return -2.0 if j < 1 else 2.0 if j > n else float(d[j - 1])

    m = n // 2
    if n % 2:
        median, lower, upper = float(d[m]), at(m + 1 - a), at(m + 1 + a)
    else:
        median = 0.5 * (float(d[m - 1]) + float(d[m]))
        lower = 0.5 * (at(m - a) + at(m + 1 - a))
        upper = 0.5 * (at(m + a) + at(m + 1 + a))
    return float(max(median - lower, upper - median))


def bound_entry(interval: list | None, bound: float, n_clipped: int) -> dict:
    """Return the clip-sensitivity entry of a tier-B quantity.

    The entry holds ``delta_bound`` and compares it with the half-width. The
    flag is ``10 * bound > hw``; there is no second clause because no verdict is
    recomputed. If the half-width is not finite, the entry is ``not_computed``.
    """
    half_width = (
        np.nan if interval is None else (interval[1] - interval[0]) / 2.0
    )
    if not np.isfinite(half_width):
        return not_computed(
            "interval half-width not finite (a bound has no second clause)",
            n_clipped,
            bound=True,
        )
    ratio = float(bound / half_width) if half_width > 0.0 else None
    return {
        "status": "computed",
        "reason": None,
        "delta_bound": float(bound),
        "ratio": ratio,
        "flag": bool(FLAG_FACTOR * bound > half_width),
        "n_clipped_inputs": int(n_clipped),
    }


def aggregate_flag(parts: dict[str, dict], extra: bool = False) -> bool | None:
    """Return the flag of a criterion made of several parts.

    The flag is True if a part fired (or ``extra`` is true). It is False if
    every part was computed and none fired. It is None if some part could not be
    computed and none fired.
    """
    flags = [p["flag"] for p in parts.values()]
    if extra or any(f is True for f in flags):
        return True
    return None if any(f is None for f in flags) else False


def _hypothesis(parts: dict[str, dict], **extra: object) -> dict:
    """Return ``{parts, flag, **extra}`` for one hypothesis.

    The key ``extra['extra_flag']`` is consumed here and adds to the flag.
    """
    fired = bool(extra.pop("extra_flag", False))
    return {"parts": parts, "flag": aggregate_flag(parts, fired), **extra}


# --- Recomputation of the tier-A verdict statistics ---
def _counted(entry: dict, n_failed: int | None, **more: int) -> dict:
    """Return ``entry`` plus the counts of the P2 recomputation.

    The counts are those that the entry would otherwise drop.

    (DEF-0001, WU-0004f.) ``n_failed_resamples`` is the number of non-finite
    bootstrap resamples of the recomputed statistic. They are placed at the
    unfavorable tail of the interval, as in the verdict code. It is ``None`` if
    the recomputation did not report one. ``more`` adds further integer counts
    (such as ``n_constant_states``). Only keys are added: no existing key of
    ``entry`` changes.
    """
    return {
        **entry,
        "n_failed_resamples": None if n_failed is None else int(n_failed),
        **more,
    }


def h3c_part(
    original: dict,
    a5_2: np.ndarray,
    a4_2: np.ndarray,
    config: StudyConfig,
    system: str,
    n_clipped: int,
) -> dict:
    """Return H3c under P2: ``an.h3c_ratio`` on the perturbed per-state MSEs.

    The bootstrap generator uses the same labels as the original verdict.
    """
    out = an.h3c_ratio(a5_2, a4_2, config, system)
    return _counted(
        part_entry(
            original["A5_over_A4_mse"],
            original["ci"],
            original["verdict"],
            out["A5_over_A4_mse"],
            out["ci"],
            out["verdict"],
            n_clipped,
        ),
        out["n_failed_resamples"],
    )


def h2d_part(
    original: dict,
    a3_2: np.ndarray,
    a4_2: np.ndarray,
    config: StudyConfig,
    system: str,
    n_clipped: int,
) -> dict:
    """Return H2d under P2 (``an.h2d_empirical_comparison``).

    The function runs on the perturbed per-state MSEs of A3 and A4.

    The per-state MSEs are those of A3 and A4, and the generator labels are the
    same as in the original verdict.
    """
    out = an.h2d_empirical_comparison(
        {
            "A3": SimpleNamespace(state_mse_ref=a3_2),
            "A4": SimpleNamespace(state_mse_ref=a4_2),
        },
        config,
        system,
    )
    return _counted(
        part_entry(
            original["in_distribution_excess"],
            original["ci"],
            original["verdict"],
            out["in_distribution_excess"],
            out["ci"],
            out["verdict"],
            n_clipped,
        ),
        out["n_failed_resamples"],
    )


def h2c_parts(
    original: dict,
    mse_2: dict[str, np.ndarray],
    calibration_2: SimpleNamespace,
    config: StudyConfig,
    system: str,
    n_clipped: dict[str, int],
) -> dict:
    """Return H2c under P2 (``an.h2c_state_dependence``).

    The function runs on the perturbed MSEs and calibration draws.

    If the better single forecaster of the calibration split changes
    (``best_single_2L``), the two parts no longer compare the same rules. The
    second part then has ``delta = None``, ``flag = True`` and ``reason = "best
    single changes at 2L"``, and the flag of the criterion fires.

    Parameters
    ----------
    original : dict
        The ``H2c`` result.
    mse_2 : dict[str, np.ndarray]
        Per-state MSE at ``H_ref`` under P2 of at least A2, A4, A4o and both
        single forecasters.
    calibration_2 : SimpleNamespace
        ``.evals`` with ``horizons``, ``cp_err`` and the perturbed
        ``plp_err`` of the calibration split.
    config : StudyConfig
        Configuration.
    system : str
        System name (a label of the bootstrap generator of the verdict this
        re-reads).
    n_clipped : dict[str, int]
        Clipped ``H_ref`` draws among the inputs of each part, by part name.

    Returns
    -------
    dict
        ``parts``, ``best_single_2L`` and ``flag``.
    """
    out = an.h2c_state_dependence(
        {k: SimpleNamespace(state_mse_ref=v) for k, v in mse_2.items()},
        calibration_2,
        config,
        system,
    )
    best, best_2 = original["best_single"], out["best_single"]
    parts = {}
    for name in ("A4_minus_A2", f"A4_minus_{best}"):
        old = original[name]
        if name == "A4_minus_A2" or best_2 == best:
            new = out[name]
            parts[name] = _counted(
                part_entry(
                    old["mean"],
                    old["ci"],
                    old["verdict"],
                    new["mean"],
                    new["ci"],
                    new["verdict"],
                    n_clipped[name],
                ),
                new["n_failed_resamples"],
            )
        else:
            parts[name] = {
                "status": "computed",
                "reason": "best single changes at 2L",
                "delta": None,
                "ratio": None,
                "flag": True,
                "verdict_2L": None,
                "n_clipped_inputs": int(n_clipped[name]),
            }
    return _hypothesis(parts, best_single_2L=best_2, extra_flag=best_2 != best)


def h1b_part(
    original: dict,
    sq_plp: np.ndarray,
    sq_plp_2: np.ndarray,
    gain: np.ndarray,
    seed_err: np.ndarray,
    dim: int,
    config: StudyConfig,
    system: str,
    n_clipped: int,
) -> dict:
    """Return H1b (PLP) under P2.

    The statistic is the OLS slope of ``0.5 ln E e_P^2`` on ``ln(g delta /
    sqrt(m))``.

    The statistic, the bootstrap generator and the verdict are those of the PLP
    regression in ``analysis.h1b_seed_amplifier`` (floor 0): ``y = 0.5 ln max(E
    e_P^2, 1e-12)``. The generator is a fresh ``make_rng(config.seed, system,
    "bootstrap", "H1b")``, the label of the PLP regression. The regressor ``x``
    does not depend on the errors. If the set of finite regression states
    changes, the part is not computed.

    The floor is counted, not silent (DEF-0001, WU-0004f; row N4 of the
    inventory is the original's counterpart). The entry carries ``n_floored``
    (regression states of the original with ``E e_P^2 < 1e-12``; the same
    expression and the same inputs as ``H1b.PLP.n_floored``, so the two are
    equal) and ``n_floored_2L`` (the same states, under P2), also when the part
    is not computed. Two facts hold by construction.

    (i) Under P2, ``sq_plp_2 = sq_plp + 3 L^2 q / M`` with ``q >= 0``
    (``perturb_moments``). So ``sq_plp_2 >= sq_plp`` (the sum of a float and a
    non-negative float is not below the float) and ``n_floored_2L <=
    n_floored``: the floor can bind under P2 only where it binds in the
    original.

    (ii) A state with ``q >= 1`` has ``sq_plp_2 >= 3 L^2 / M``, which is above
    1e-12 for every ``M <= 3e14``. So under P2 the floor binds only on states
    with no clipped draw. Where the floor does not bind, ``np.maximum`` returns
    its first argument unchanged. That it does not bind at all is not proved: it
    is the sentinel ``n_floored`` (it should read 0), reported.

    Returns
    -------
    dict
        ``part_entry`` or ``not_computed`` output, plus the two integer
        counts ``n_floored`` and ``n_floored_2L``.
    """
    x_all = np.log(gain * seed_err / np.sqrt(dim))
    keep = np.isfinite(x_all) & np.isfinite(
        0.5 * np.log(np.maximum(sq_plp, 1e-12))
    )
    y_2 = 0.5 * np.log(np.maximum(sq_plp_2, 1e-12))
    floored = {
        "n_floored": int(
            (sq_plp < 1e-12)[keep].sum()
        ),  # the floor binds in the original
        "n_floored_2L": int((sq_plp_2 < 1e-12)[keep].sum()),
    }  # ... and under P2
    if not np.array_equal(keep, np.isfinite(x_all) & np.isfinite(y_2)):
        return {
            **not_computed("regression states change at 20 sigma_x", n_clipped),
            **floored,
        }
    x, y = x_all[keep], y_2[keep]
    if len(x) == 0:
        return {**not_computed("no regression state", n_clipped), **floored}
    boot = block_bootstrap_counted(
        lambda idx: ols_slope(x[idx], y[idx]),
        len(x),
        config.bootstrap_resamples,
        config.bootstrap_block,
        make_rng(config.seed, system, "bootstrap", "H1b"),
        an.H1_LEVEL,
    )
    verdict_2, _ = criterion_verdict(
        boot.estimate, boot.lower, boot.upper, an.H1B_BAND, n_states=len(x)
    )
    plp = original["PLP"]
    return {
        **_counted(
            part_entry(
                plp["slope"],
                plp["ci"],
                original["verdict"],
                boot.estimate,
                [boot.lower, boot.upper],
                verdict_2,
                n_clipped,
            ),
            boot.n_failed,
        ),
        **floored,
    }


def h2a_parts(
    original: dict,
    w_ref_2: np.ndarray,
    growth_scaled: np.ndarray,
    seeds: np.ndarray,
    config: StudyConfig,
    system: str,
    n_clipped: int,
) -> dict:
    """Return H2a(ii) under P2 (``an.h2a_part_ii``).

    The function runs on the perturbed ``w*(H_ref)``.

    The generator labels are those of the original verdict. A part of the
    original that is absent under P2 (the ``w* = 1`` part is added only above 5%
    of the states) is not computed. A part that appears only under P2 has no
    entry of its own and sets the flag of the criterion (``parts_2L`` lists the
    parts under P2).
    """
    out = an.h2a_part_ii(
        w_ref_2,
        growth_scaled,
        seeds,
        n_resamples=config.bootstrap_resamples,
        block=config.bootstrap_block,
        seed=make_rng(config.seed, system, "h2a-two-part"),
        level=an.PRIMARY_LEVEL,
    )
    parts = {}
    for name, old in original["part_ii"].items():
        new = out["part_ii"].get(name)
        parts[name] = (
            not_computed("part absent at 20 sigma_x", n_clipped)
            if new is None
            else _counted(
                part_entry(
                    old["partial_corr"],
                    old["ci"],
                    old["verdict"],
                    new["partial_corr"],
                    new["ci"],
                    new["verdict"],
                    n_clipped,
                ),
                new["n_failed_resamples"],
            )
        )
    return _hypothesis(
        parts,
        parts_2L=list(out["part_ii"]),
        extra_flag=set(out["part_ii"]) != set(original["part_ii"]),
    )


def h2b_noise_part(
    original: dict,
    w_by_noise_2: np.ndarray,
    levels: np.ndarray,
    config: StudyConfig,
    system: str,
    n_clipped: int,
) -> dict:
    """Return H2b(i) under P2.

    The statistic is the mean per-state Spearman correlation of ``w*(H_ref)``
    with ``rho``.

    The statistic, the generator ``make_rng(config.seed, system, "bootstrap",
    "H2b-noise")``, the level ``1 - 0.05/3`` and the verdict rule are those of
    ``analysis.h2b_knob_response``.
    """
    rho_corr, n_constant = an._per_state_spearman_counted(levels, w_by_noise_2)
    point, values = bootstrap_values(
        lambda idx: float(np.mean(rho_corr[idx])),
        len(rho_corr),
        config.bootstrap_resamples,
        config.bootstrap_block,
        make_rng(config.seed, system, "bootstrap", "H2b-noise"),
    )
    lower, upper, n_failed = percentile_interval(values, an.PRIMARY_LEVEL)
    verdict_2, _ = criterion_verdict(
        float(point),
        lower,
        upper,
        (0.0, np.inf),
        (False, True),
        n_states=len(rho_corr),
    )
    return _counted(
        part_entry(
            original["mean_state_spearman"],
            original["ci"],
            original["verdict"],
            float(point),
            [lower, upper],
            verdict_2,
            n_clipped,
        ),
        n_failed,
        n_constant_states=int(n_constant),
    )


def h2b_library_part(
    original: dict,
    low_2: np.ndarray,
    high_2: np.ndarray,
    rho: float,
    config: StudyConfig,
    system: str,
    n_clipped: int,
) -> dict:
    """Return H2b(ii) under P2: ``an._paired_change`` on the perturbed weights.

    The labels and the level are the same as in the original verdict.
    """
    fields, verdict_2, _ = an._paired_change(
        low_2,
        high_2,
        config,
        an.PRIMARY_LEVEL,
        (system, "h2b-library-change", f"{rho:g}"),
        "mean_change",
        mc_error=True,
    )
    return _counted(
        part_entry(
            original["mean_change"],
            original["ci"],
            original["verdict"],
            fields["mean_change"],
            fields["ci"],
            verdict_2,
            n_clipped,
        ),
        fields["n_failed_resamples"],
    )


# --- Orchestration ---
def _part_names(results: dict) -> dict[str, list[str]]:
    """Return the parts of each tier-A or tier-B criterion in ``results``.

    The order is the report order.
    """
    names: dict[str, list[str]] = {}
    if "H1b" in results:
        names["H1b"] = ["PLP"]
    if "H2a" in results:
        names["H2a"] = list(results["H2a"]["part_ii"])
    if "H2b" in results:
        names["H2b"] = ["noise", "library_change"]
    if "H2c" in results:
        names["H2c"] = [
            "A4_minus_A2",
            f"A4_minus_{results['H2c']['best_single']}",
        ]
    if "H2d" in results:
        names["H2d"] = ["A4_over_A3"]
    if "H2e" in results:
        names["H2e"] = list(results["H2e"]["by_noise"])
    if "H3c" in results:
        names["H3c"] = ["A5_over_A4"]
    return names


class _BaselineMismatch(Exception):
    """The stored weights or MSEs are not reproduced by the recomputation.

    This is a defect, not a finding; the block then reports "not computed" with
    the reason.
    """


def _all_not_computed(results: dict, reason: str) -> dict:
    """Return every part as not computed, with ``reason``.

    This is the block-level fallback.
    """
    return {
        h: _hypothesis({n: not_computed(reason) for n in parts})
        for h, parts in _part_names(results).items()
    }


def _arrays_missing(cells: list) -> str | None:
    """Return a reason if a cell lacks the two internal arrays, else ``None``.

    The cells are moments or evaluation objects.
    """
    for name, moments in cells:
        if moments.handled is None or moments.clip_cross_ref is None:
            return (
                f"clip arrays absent in {name} moments (hand-built, or made "
                "without a reference horizon)"
            )
    return None


def _cp_clips(objects: list) -> int:
    """Return the total ``error_clips_cp`` of the objects with totals.

    Views carry no totals and are skipped.

    Views carry no totals and are skipped.
    """
    return int(
        sum(
            o.clip_entries["error_clips_cp"]
            for o in objects
            if o.clip_entries is not None
        )
    )


def _unique_cells(*groups: dict) -> list:
    """Return the distinct cells of the sweep dictionaries, in a stable order.

    A cell may sit in both dictionaries.
    """
    seen: dict[int, object] = {}
    for group in groups:
        for cell in group.values():
            seen.setdefault(id(cell), cell)
    return list(seen.values())


def clip_sensitivity_block(
    cell,
    rules,
    weights: dict[str, np.ndarray],
    scores: dict,
    noise_cells: dict,
    library_cells: dict,
    results: dict,
    config: StudyConfig,
) -> dict:
    """Return the ``clip_sensitivity`` result of one system.

    The module docstring gives the definition.

    Parameters
    ----------
    cell : Cell
        The core cell (all splits, all horizons, with evaluation draws).
    rules : FittedRules
        The rules fitted on it.
    weights : dict[str, np.ndarray]
        ``rule_weights`` of the test split, ``(n, E, nH)`` per rule.
    scores : dict[str, RuleScores]
        ``score_rules`` of the test split (``state_mse_ref`` is the
        recomputation baseline).
    noise_cells : dict[float, Cell]
        The noise sweep (as passed to ``h2b_knob_response``).
    library_cells : dict[tuple[float, int], Cell]
        The library sweep.
    results : dict
        The system's results so far: ``H1b``, ``H2a``, ``H2b``, ``H2c``,
        ``H2d``, ``H2e``, ``H3c`` (a criterion that is absent is skipped).
    config : StudyConfig
        Configuration.

    Returns
    -------
    dict
        ``clip_level``, ``perturbed_level``, ``status`` ("computed" or
        "not_computed", with ``reason``), ``href_clipped_draws``,
        ``held_fixed_entries``, ``test_eval_clipped_entries``,
        ``share_test``, ``weight_shift``, ``by_hypothesis`` (per criterion
        ``parts`` and ``flag``), ``invariance``, ``affected_states`` and
        ``n_caught_exceptions``. The entry ``share_test`` gives, per rule,
        the share of the pooled squared error on the test draws whose PLP
        error is clipped; it describes where the error sits (for A0 it is
        the CP squared-error share), and only its change under P2 is 0
        (Amendment 1 A1.4).

    Nothing here changes a verdict or marks a result provisional (OD6), and the
    recomputation consumes no randomness. This is a report-only block: **any**
    exception inside it is caught and recorded (``status = "not_computed"``,
    ``reason = "error: <repr>"``, ``LOG.exception``), so that a defect here can
    never end a run and lose the verdicts (the pattern of ``run_robustness``).

    **Every swallowed exception is counted** (DEF-0001, WU-0004f).
    ``n_caught_exceptions`` is the number of exceptions that the three broad
    ``except`` clauses of this module caught while building the block: one per
    failed criterion in ``_guarded``, one for the whole block here, and one for
    a failed listing of the parts in ``_failed``. It is present, and 0, when
    nothing was caught. A refusal that carries its own reason (arrays absent, a
    CP clip, a baseline not reproduced) is not an exception and is not counted;
    its ``reason`` says it. The count is a sentinel (it should be 0).
    """
    caught: list[str] = []
    try:
        return _block(
            cell,
            rules,
            weights,
            scores,
            noise_cells,
            library_cells,
            results,
            config,
            caught,
        )
    # Report-only block: the error is recorded and logged, never fatal.
    except Exception as exc:  # noqa: BLE001
        LOG.exception("clip sensitivity: block not computed: %r", exc)
        caught.append(repr(exc))
        return _failed(results, f"error: {exc!r}", len(caught))


def _failed(results: dict, reason: str, n_caught: int = 0) -> dict:
    """Return a block that was not computed, with every part not computed.

    The reason is given for each part, and no part is ever False.

    No part is ever False. ``n_caught`` is the number of exceptions already
    swallowed on the way here; a failure to list the parts adds one (and is
    logged: it was silent before WU-0004f).
    """
    try:
        by_hypothesis = _all_not_computed(results, reason)
    # Malformed results: there are no parts to list; the reason stays.
    except Exception as exc:  # noqa: BLE001
        LOG.exception(
            "clip sensitivity: the parts of the failed block could not be "
            "listed: %r",
            exc,
        )
        by_hypothesis = {}
        n_caught += 1
    return {
        "clip_level": ERROR_CLIP,
        "perturbed_level": PERTURBED_LEVEL,
        "status": "not_computed",
        "reason": reason,
        "by_hypothesis": by_hypothesis,
        "invariance": dict.fromkeys(
            ("H1c", "H2a_i", "H3a"), INVARIANCE_NOT_COMPUTED
        ),
        "affected_states": {"Q-N": None, "H3b": None},
        "n_caught_exceptions": int(n_caught),
    }


def _block(
    cell,
    rules,
    weights,
    scores,
    noise_cells,
    library_cells,
    results,
    config,
    caught: list[str],
) -> dict:
    """Return the body of ``clip_sensitivity_block``.

    The caller catches whatever this function raises.

    ``caught`` collects the repr of every exception swallowed while building the
    block. It belongs to the caller, so a later failure of the whole block keeps
    the count.
    """
    out: dict = {
        "clip_level": ERROR_CLIP,
        "perturbed_level": PERTURBED_LEVEL,
        "status": "computed",
        "reason": None,
    }
    con, cal, test = (
        cell.splits[s] for s in ("construction", "calibration", "test")
    )
    sweeps = _unique_cells(noise_cells, library_cells)
    reason = _arrays_missing(
        [
            ("core construction", con.moments),
            ("core calibration", cal.moments),
            ("core test", test.moments),
            *(
                (f"sweep cell {i}", c.splits["test"].moments)
                for i, c in enumerate(sweeps)
            ),
        ]
    )
    if reason is None and (
        cal.evals.clip_sign_ref is None or test.evals.clip_sign_ref is None
    ):
        reason = "clip_sign_ref absent in the core evaluation draws"
    if reason is None:
        n_cp = _cp_clips(
            [
                *(s.moments for s in cell.splits.values()),
                *(s.evals for s in cell.splits.values() if s.evals is not None),
                *(c.splits["test"].moments for c in sweeps),
            ]
        )
        if n_cp:
            reason = f"CP clip sentinel nonzero ({n_cp} entries)"
    if reason is not None:
        return _failed(results, reason, len(caught))
    try:
        out.update(
            _compute(
                cell,
                rules,
                weights,
                scores,
                noise_cells,
                library_cells,
                results,
                config,
                sweeps,
                caught,
            )
        )
    except _BaselineMismatch as exc:
        return _failed(results, str(exc), len(caught))
    out["n_caught_exceptions"] = len(caught)
    return out


def _guarded(names: list[str], build, tier_b: bool, caught: list[str]) -> dict:
    """Return ``build()``; if it raises, return every part not computed.

    The error is logged and counted: its repr is appended to ``caught`` (the
    block's ``n_caught_exceptions``).

    The error is logged and counted: its repr is appended to ``caught`` (the
    block's ``n_caught_exceptions``).
    """
    try:
        return build()
    # A flag that cannot be computed is reported, not fatal.
    except Exception as exc:  # noqa: BLE001
        LOG.exception("clip sensitivity: %s", exc)
        caught.append(repr(exc))
        return _hypothesis(
            {n: not_computed(f"error: {exc!r}", bound=tier_b) for n in names}
        )


def _compute(
    cell,
    rules,
    weights,
    scores,
    noise_cells,
    library_cells,
    results,
    config,
    sweeps,
    caught: list[str],
) -> dict:
    """Return the body of ``clip_sensitivity_block`` for inputs with the arrays.

    The function recomputes the weights of A2 and A5 from the perturbed oracle
    moments, checks that the unperturbed recomputation reproduces the stored
    baseline, then rebuilds each criterion. ``caught`` receives the repr of each
    criterion whose builder raised (see ``_guarded``).
    """

    def guard(names: list[str], build, tier_b: bool = False) -> dict:
        return _guarded(names, build, tier_b, caught)

    ref, m_draws, lt = (
        config.reference_horizon,
        config.n_oracle_draws,
        config.steps_per_lyapunov,
    )
    con, cal, test = (
        cell.splits[s] for s in ("construction", "calibration", "test")
    )
    names = _part_names(results)
    q = {
        "construction_oracle": clipped_draws(con.moments.handled),
        "calibration_oracle": clipped_draws(cal.moments.handled),
        "test_oracle": clipped_draws(test.moments.handled),
    }
    href = {k: int(v.sum()) for k, v in q.items()}
    for name, split in (("calibration_eval", cal), ("test_eval", test)):
        href[name] = int(clipped_draws(split.evals.handled).sum())
        if href[name] != int(np.abs(split.evals.clip_sign_ref).sum()):
            raise _BaselineMismatch(
                f"clip_sign_ref disagrees with handled in the {name} draws"
            )
    entries = (
        lambda o: o.clip_entries["error_clips_plp"]
        + o.clip_entries["error_clips_nonfinite"]
    )
    out: dict = {
        "href_clipped_draws": {
            k: href[k]
            for k in (
                "construction_oracle",
                "calibration_oracle",
                "calibration_eval",
                "test_oracle",
                "test_eval",
            )
        },
        "held_fixed_entries": int(
            entries(con.moments) + entries(cal.moments) + entries(cal.evals)
        ),
        "test_eval_clipped_entries": int(entries(test.evals)),
    }

    # --- fitting channel: A2 and A5 from the perturbed oracle moments,
    # the tree and assignment held fixed
    col = con.moments.at(ref)
    con_2 = perturb_moments(con.moments, col, m_draws)
    cal_2 = perturb_moments(cal.moments, col, m_draws)
    test_2 = perturb_moments(test.moments, col, m_draws)
    rmap = rules.regimes[rules.chosen_regimes]
    profile = lambda split: deployable_profile(
        split.evals, rules.proxies, cell.noise, lt
    )
    regime_cal, regime_test = rmap.assign(profile(cal)), rmap.assign(
        profile(test)
    )
    # a regime with no calibration member takes the fallback A2' (the
    # construction oracle)
    empty = np.array(
        [not (regime_cal == k).any() for k in range(rmap.n_regimes)]
    )
    if rmap.empty is not None and not np.array_equal(rmap.empty, empty):
        raise _BaselineMismatch(
            "the empty regimes of the map disagree with the calibration "
            "assignment"
        )
    empty_used = bool(
        empty[regime_test].any()
    )  # some test draw is scored with the fallback

    def regime_weights(
        fallback: np.ndarray, moments: EnsembleMoments
    ) -> np.ndarray:
        # The weights of calibrate_regimes: an empty regime keeps the
        # fallback, others regime_weight.
        table = np.tile(fallback, (rmap.n_regimes, 1)).astype(float)
        for k in range(rmap.n_regimes):
            members = np.nonzero(regime_cal == k)[0]
            if members.size:
                table[k] = regime_weight(moments, members)
        return table

    a2_0, a2_2 = global_weight(con.moments), global_weight(con_2)
    a5_0, a5_2 = regime_weights(a2_0, cal.moments), regime_weights(a2_2, cal_2)
    if not (
        np.array_equal(a2_0, rules.global_weights)
        and np.array_equal(a5_0, rmap.weights)
    ):
        raise _BaselineMismatch("baseline A2 or A5 weights not reproduced")
    out["weight_shift"] = {
        "A2": float(a2_2[col] - a2_0[col]),
        "A5_max": float(np.max(np.abs(a5_2[:, col] - a5_0[:, col]))),
    }

    # --- evaluation channel: per-state MSE at H_ref of every rule,
    # original and perturbed
    ecol = int(np.nonzero(test.evals.horizons == ref)[0][0])
    cp_t, plp_t = test.evals.cp_err[:, :, ecol], test.evals.plp_err[:, :, ecol]
    plp_t2 = perturb_errors(plp_t, test.evals.clip_sign_ref)
    w_0 = {r: weights[r][:, :, ecol] for r in STATE_RULES}
    w_2 = {
        **w_0,
        "A2": np.broadcast_to(a2_2[col], plp_t.shape),
        "A5": a5_2[regime_test, col],
    }
    mse_0 = {r: rule_state_mse(w_0[r], cp_t, plp_t) for r in STATE_RULES}
    if not (
        np.array_equal(w_0["A5"], a5_0[regime_test, col])
        and np.array_equal(w_0["A2"], np.broadcast_to(a2_0[col], plp_t.shape))
        and all(
            np.array_equal(mse_0[r], scores[r].state_mse_ref)
            for r in STATE_RULES
        )
    ):
        raise _BaselineMismatch(
            "baseline A2/A5 weights or per-state MSE at H_ref not reproduced"
        )
    mse_2 = {r: rule_state_mse(w_2[r], cp_t, plp_t2) for r in STATE_RULES}
    mask = test.evals.clip_sign_ref != 0

    def share(rule: str) -> float | None:
        h2 = (w_0[rule] * cp_t + (1 - w_0[rule]) * plp_t) ** 2
        return float(h2[mask].sum() / h2.sum()) if h2.sum() > 0 else None

    out["share_test"] = {
        r: share(r) for r in ("A0", "A1", "A2", "A3", "A4", "A5")
    }

    # --- the criteria
    by_hypothesis: dict = {}
    n_test_eval = href["test_eval"]
    if "H3c" in names:
        by_hypothesis["H3c"] = guard(
            names["H3c"],
            lambda: _hypothesis(
                {
                    "A5_over_A4": h3c_part(
                        results["H3c"],
                        mse_2["A5"],
                        mse_2["A4"],
                        config,
                        cell.system,
                        n_test_eval
                        + href["calibration_oracle"]
                        + empty_used * href["construction_oracle"],
                    )
                }
            ),
        )
    if "H2d" in names:
        by_hypothesis["H2d"] = guard(
            names["H2d"],
            lambda: _hypothesis(
                {
                    "A4_over_A3": h2d_part(
                        results["H2d"],
                        mse_2["A3"],
                        mse_2["A4"],
                        config,
                        cell.system,
                        n_test_eval,
                    )
                }
            ),
        )
    if "H2c" in names:

        def build_h2c() -> dict:
            plp_cal = cal.evals.plp_err.copy()
            cecol = int(np.nonzero(cal.evals.horizons == ref)[0][0])
            plp_cal[:, :, cecol] = perturb_errors(
                plp_cal[:, :, cecol], cal.evals.clip_sign_ref
            )
            calibration_2 = SimpleNamespace(
                evals=SimpleNamespace(
                    horizons=cal.evals.horizons,
                    cp_err=cal.evals.cp_err,
                    plp_err=plp_cal,
                )
            )
            shared = n_test_eval + href["calibration_eval"]
            counts = {
                "A4_minus_A2": shared + href["construction_oracle"],
                names["H2c"][1]: shared,
            }
            return h2c_parts(
                results["H2c"],
                mse_2,
                calibration_2,
                config,
                cell.system,
                counts,
            )

        by_hypothesis["H2c"] = guard(names["H2c"], build_h2c)
    m_test = test.moments
    wcol = m_test.at(ref)
    if "H1b" in names:
        by_hypothesis["H1b"] = guard(
            names["H1b"],
            lambda: _hypothesis(
                {
                    "PLP": h1b_part(
                        results["H1b"],
                        m_test.sq_plp[:, wcol],
                        test_2.sq_plp[:, wcol],
                        cell.oracles["test"].gains[:, ref - 1],
                        m_test.est_seed,
                        cell.ctx.spec.dim,
                        config,
                        cell.system,
                        href["test_oracle"],
                    )
                }
            ),
        )
    if "H2a" in names:

        def build_h2a() -> dict:
            seeds = np.column_stack(
                [
                    np.log(m_test.analog_seed / cell.noise),
                    np.log(m_test.est_seed / cell.noise),
                ]
            )
            return h2a_parts(
                results["H2a"],
                oracle_weight(test_2)[:, wcol],
                cell.oracles["test"].growth * lt,
                seeds,
                config,
                cell.system,
                href["test_oracle"],
            )

        by_hypothesis["H2a"] = guard(names["H2a"], build_h2a)
    if "H2b" in names:
        by_hypothesis["H2b"] = guard(
            names["H2b"],
            lambda: _h2b(
                results["H2b"], noise_cells, library_cells, config, m_draws
            ),
        )
    if "H2e" in names:
        by_hypothesis["H2e"] = guard(
            names["H2e"],
            lambda: _h2e(results["H2e"], library_cells, config),
            tier_b=True,
        )
    out["by_hypothesis"] = by_hypothesis

    # --- tier C (counts) and tier D (invariance, checked here)
    out["affected_states"] = {
        "Q-N": int(
            (q["construction_oracle"] > 0).sum()
            + (q["calibration_oracle"] > 0).sum()
            + (q["test_oracle"] > 0).sum()
        ),
        "H3b": int((q["construction_oracle"] > 0).sum()),
    }
    counts = {
        "test_eval": (out["test_eval_clipped_entries"], href["test_eval"]),
        "calibration_eval": (int(entries(cal.evals)), href["calibration_eval"]),
        "calibration_oracle": (
            int(entries(cal.moments)),
            href["calibration_oracle"],
        ),
        "construction_oracle": (
            int(entries(con.moments)),
            href["construction_oracle"],
        ),
    }
    out["invariance"] = invariance(
        config, counts, out["weight_shift"]["A5_max"], empty_used
    )
    if out["invariance"]["H3a"] == INVARIANCE_EXACT:
        # P-c of Amendment 1: with no clipped entry feeding A5 or the
        # Kaplan-Meier order, the A5 weights at H_ref that H3a reads
        # must be bitwise unchanged (the rows of an empty regime only
        # matter if a test draw falls in one). A failure is a defect,
        # not a finding.
        rows = ~empty | empty_used
        if not np.array_equal(a5_2[rows, col], a5_0[rows, col]):
            raise _BaselineMismatch(
                "P-c failed: the A5 weights at H_ref changed although no "
                "clipped entry feeds H3a (defect)"
            )
    return out


def invariance(
    config: StudyConfig,
    counts: dict[str, tuple[int, int]],
    a5_shift: float = 0.0,
    empty_regime_used: bool = False,
) -> dict[str, str]:
    """Return the tier-D statements, checked at run time (Amendment 1).

    They follow NVVUQ.14.

    H1c and H2a(i) read the test oracle only (never a fitted weight). A horizon
    at which P2 changes anything carries a clipped draw, so its mean square is
    at least ``L^2 / M``. If ``L^2 / M > max(theta_max, r_lin)^2`` (H-M1, H-M2),
    the statistic exceeded the threshold (or was non-small) at ``L`` already,
    and it is unchanged. This is asserted here; if it fails, the statement is
    "outside the invariance hypothesis".

    H3a reads the A5 weights and the Kaplan-Meier regime order, which come from
    the calibration oracle (and, for a regime with no calibration member, from
    the construction oracle), and the test and calibration evaluation errors. It
    is "exact" only if none of those inputs holds a clipped entry at any
    horizon: no test evaluation entry, no calibration evaluation entry, no
    calibration oracle entry, and no construction oracle entry if some test draw
    falls in an empty regime. Otherwise it is ``"not guaranteed: " + ";
    ".join(causes)``, each cause naming the source, its total, its count at
    ``H_ref`` and what it feeds. "Not guaranteed" does not mean "changed".

    Parameters
    ----------
    config : StudyConfig
        Configuration (``thresholds``, ``linear_regime_rms``,
        ``n_oracle_draws``).
    counts : dict[str, tuple[int, int]]
        For ``test_eval``, ``calibration_eval``, ``calibration_oracle`` and
        ``construction_oracle``: the clipped PLP entries (finite beyond the
        clip, or non-finite) at all horizons, and the clipped draws at
        ``H_ref``.
    a5_shift : float, optional
        ``max_k |A5'_k - A5_k|`` at ``H_ref`` (named in the
        calibration-oracle cause).
    empty_regime_used : bool, optional
        Some test draw falls in a regime with no calibration member.

    Returns
    -------
    dict[str, str]
        ``H1c``, ``H2a_i`` (``"exact"`` or "outside the invariance
        hypothesis") and ``H3a`` (``"exact"`` or ``"not guaranteed:
        <causes>"``).
    """
    holds = ERROR_CLIP**2 / config.n_oracle_draws > max(
        max(config.thresholds) ** 2, config.linear_regime_rms**2
    )
    note = {
        "test_eval": ("test evaluation", ""),
        "calibration_eval": (
            "calibration evaluation",
            "; Kaplan-Meier regime order",
        ),
        "calibration_oracle": (
            "calibration oracle",
            f"; A5 weights, A5_max shift {a5_shift:.3g}",
        ),
        "construction_oracle": (
            "construction oracle",
            "; A2 fallback of an empty regime",
        ),
    }
    causes = []
    for key, (label, what) in note.items():
        total, at_ref = counts[key]
        if total and (key != "construction_oracle" or empty_regime_used):
            causes.append(
                f"{label}: {total} clipped entries ({at_ref} at H_ref{what})"
            )
    return {
        "H1c": INVARIANCE_EXACT if holds else INVARIANCE_OUTSIDE,
        "H2a_i": INVARIANCE_EXACT if holds else INVARIANCE_OUTSIDE,
        "H3a": (
            INVARIANCE_EXACT
            if not causes
            else INVARIANCE_NOT_GUARANTEED + ": " + "; ".join(causes)
        ),
    }


def _weights_at_ref(
    cell, config: StudyConfig, m_draws: int
) -> tuple[np.ndarray, np.ndarray, int]:
    """Return ``w*(H_ref)`` of a sweep cell's test states under P2.

    The function also returns the clipped draws per state and the column of
    ``H_ref``.
    """
    m = cell.splits["test"].moments
    col = m.at(config.reference_horizon)
    return (
        oracle_weight(perturb_moments(m, col, m_draws))[:, col],
        clipped_draws(m.handled),
        col,
    )


def _h2b(
    original: dict,
    noise_cells: dict,
    library_cells: dict,
    config: StudyConfig,
    m_draws: int,
) -> dict:
    """Return H2b(i) and H2b(ii) under P2.

    The sweep cells carry their own clip arrays.
    """
    levels = np.array(sorted(noise_cells))
    pieces = [_weights_at_ref(noise_cells[r], config, m_draws) for r in levels]
    system = noise_cells[min(noise_cells)].system
    noise = h2b_noise_part(
        original["noise"],
        np.column_stack([p[0] for p in pieces]),
        levels,
        config,
        system,
        int(sum(p[1].sum() for p in pieces)),
    )
    rho = config.core_noise
    wanted = [(rho, n) for n in an.H2B_LIBRARY_SIZES]
    old = original["library_change"]
    if old["mean_change"] is None:
        library = not_computed(
            f"the verdict itself is not computed ({old['reason']})"
        )
    else:
        low, high = (
            _weights_at_ref(library_cells[key], config, m_draws)
            for key in wanted
        )
        library = h2b_library_part(
            old,
            low[0],
            high[0],
            rho,
            config,
            system,
            int(low[1].sum() + high[1].sum()),
        )
    return _hypothesis({"noise": noise, "library_change": library})


def _h2e(original: dict, library_cells: dict, config: StudyConfig) -> dict:
    """Return H2e under P2: the bound on the median change from the counts.

    This is tier B, so no verdict is recomputed.
    """
    ref = config.reference_horizon
    parts = {}
    for rho in an.H2E_NOISES:
        entry = original["by_noise"][f"{rho:g}"]
        wanted = [(rho, n) for n in an.H2E_LIBRARY_SIZES]
        if entry["median_change"] is None:
            parts[f"{rho:g}"] = not_computed(
                f"the verdict itself is not computed ({entry['reason']})",
                bound=True,
            )
            continue
        moments = [library_cells[key].splits["test"].moments for key in wanted]
        corr = [m.err_corr[:, m.at(ref)] for m in moments]
        counts = [clipped_draws(m.handled) for m in moments]
        diff = corr[1] - corr[0]
        if not np.all(np.isfinite(diff)):
            parts[f"{rho:g}"] = not_computed(
                "a per-state correlation is not finite", bound=True
            )
            continue
        n_changed = int(((counts[0] > 0) | (counts[1] > 0)).sum())
        parts[f"{rho:g}"] = bound_entry(
            entry["ci"],
            median_bound(diff, n_changed),
            int(counts[0].sum() + counts[1].sum()),
        )
    return _hypothesis(parts)


# --- Reading and logging ---
def part_state(entry: dict) -> str:
    """Return the state of one entry: "none", "ok", "fired" or "not_computed".

    "none" means no input is clipped.
    """
    if entry["status"] != "computed":
        return "not_computed"
    if entry["flag"]:
        return "fired"
    return "none" if entry["n_clipped_inputs"] == 0 else "ok"


def log_flags(system: str, block: dict) -> int:
    """Write one WARNING line per fired flag, event and block failure.

    The lines make every flag visible in the log (PRIME.4).

    Parameters
    ----------
    system : str
        System name (for the line text).
    block : dict
        The ``clip_sensitivity`` result.

    Returns
    -------
    int
        The number of WARNING lines written.
    """
    lines = 0
    if block["status"] != "computed":
        LOG.warning(
            "clip sensitivity %s: NOT COMPUTED: %s", system, block["reason"]
        )
        return 1
    for hypothesis, entry in block["by_hypothesis"].items():
        for name, part in entry["parts"].items():
            if part["status"] == "computed" and part["flag"]:
                size = part.get("delta", part.get("delta_bound"))
                LOG.warning(
                    "clip sensitivity %s %s %s: CLIP-SENSITIVE (|delta|/hw = "
                    "%s, delta = %s, at 20 sigma_x: %s; %s of the part's "
                    "inputs clipped at H_ref)",
                    system,
                    hypothesis,
                    name,
                    "n/a" if part["ratio"] is None else f"{part['ratio']:.3g}",
                    "n/a" if size is None else f"{size:.3g}",
                    part.get("verdict_2L") or part["reason"] or "bound",
                    part["n_clipped_inputs"],
                )
                lines += 1
        if (
            hypothesis == "H2a"
            and entry["flag"]
            and not any(p["flag"] for p in entry["parts"].values())
        ):
            LOG.warning(
                "clip sensitivity %s H2a: CLIP-SENSITIVE (the parts of (ii) "
                "change at 20 sigma_x: %s)",
                system,
                entry["parts_2L"],
            )
            lines += 1
    if block["invariance"]["H3a"].startswith(INVARIANCE_NOT_GUARANTEED):
        LOG.warning(
            "clip sensitivity %s H3a: invariance %s",
            system,
            block["invariance"]["H3a"],
        )
        lines += 1
    for name in ("H1c", "H2a_i"):
        if block["invariance"][name] == INVARIANCE_OUTSIDE:
            LOG.warning(
                "clip sensitivity %s %s: outside the invariance hypothesis "
                "(L^2/M <= max(theta_max, r_lin)^2)",
                system,
                name,
            )
            lines += 1
    if block["held_fixed_entries"]:
        LOG.warning(
            "clip sensitivity %s: tree, A3 and KM inputs contain %d clipped "
            "entries; not recomputed",
            system,
            block["held_fixed_entries"],
        )
        lines += 1
    return lines
