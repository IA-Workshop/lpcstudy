#!/usr/bin/env python3
"""Project pilot-run precision to the full-size run (C7 projections).

The study must choose how large the final ("full") run should be. A small
rehearsal run (the pilot, R1) gives confidence intervals for the 18 criteria
(plus the V7 rows and the H3a log-rank pairs). This tool asks: if we repeated
the run at full size, how wide would each interval be? An interval's half-width
(hw) is half its length. It shrinks when there are more test states, more
bootstrap resamples and more evaluation draws, so the projection is ``hw_full =
hw_run x f`` where ``f`` is a product of the factors below. The report is a
DEVELOPMENT report: it is conditional on one realization, it never touches the
sealed seed, and it is not a hypothesis test. **It needs owner review before
freeze** because it informs the owner's sample-size decision (LPC.PC.5).

The tool only reads run directories and is not imported by the package.
``tools/rehearsal_common.py`` supplies the shared report, dump reader and
seed-id helpers. ``tools/rehearsal_diagnostics.py`` is its sibling. Usage::

    .venv/bin/python -I tools/rehearsal_report.py RUN [--states DIR]
        [--systems S ...] [--observed FULL_RUN] [--json OUT]

``RUN`` is the pilot-size rehearsal (R1): a ``results.json`` or the directory
that holds it. The per-state dump of each system, ``<dir>/states/<system>.npz``
(schema ``lpcstudy.states/1`` or ``/2``, see the module docstring of
``lpcstudy/dump.py``; ``--states`` overrides the folder), is used for the
evaluation-draw factor. ``--observed`` is a full-size run (R5); its half-widths
are compared with the projection made from ``RUN``. Every recorded seed id must
be present, must agree, and must be a development seed ``DEV-n``; otherwise the
run is refused (exit 2).

The factors (plan amendment 2, B1 item 6; mathematics check
``docs/agent/notes/2026-10-14-math-wu0003.md``, M3):

* **n:** ``sqrt(n_run / n_full)``, using the criterion's own number of test
  states (``n_test`` or ``n_test_sweep``) from the run's configuration and the
  ``full`` preset.
* **B:** the bootstrap-endpoint factor ``E hw(B = 2000) / E hw(B = 500)``, 1.014
  at the primary level ``1 - 0.05/3`` and 1.007 at 95%. It is defined only for B
  from 500 to 2000: equal B gives 1, any other pair is "not computable".
* **kappa_E,** for the criteria built on evaluation-draw MSEs (H2c, H2d, H3c; E
  from 2 to 4). The pre-registered range ``[sqrt(E_run/E_full), 1]`` governs
  (``KAPPA_POLICY = "range"``). A point estimate of kappa_E from the dump is
  biased, so it is printed as information only and never enters a projection
  (plan amendment 8, H1 and H3; note ``2026-10-14-math-wu0003-3a-kappa.md``).
  Rows governed by the range count as computed rows for the exit code. The dump
  is first checked against the results leaf it belongs to; a dump that fails is
  not used at all (MISMATCH, exit 1).
* **Q-N training size,** 900 to 3000: the range ``[0.61, 1]`` (logit,
  log-horizon) or ``[0.74, 1]`` (indicator); equal sizes give 1, any other pair
  is "not computable".

Ratio criteria (H1a, H1c, H2d, H3c) are also printed as ``hw / R``, where ``R``
is the run's point estimate. H2c is printed relative to its MSE level.

Two readings compare a half-width with the v3 precision statements (section 7 of
the proposal; H2b(ii) 0.03, H2e 0.04, Q-N 0.04, H2a(ii) needing ``|pc|`` about
0.01) using the band ``[0.67, 1.5]``. Reading (i) uses ``hw_run
sqrt(n_run/n_full)`` alone. Reading (ii) asks whether the whole projected range
lies outside the band. "v3 precision not reproduced" is printed if either
reading says outside. For H2a(ii) the band applies to the margin ``m = 0.1 -
hw_full`` (plan amendment 7, G3), and the older comparison of ``hw_full`` with
``0.09 x [0.67, 1.5]`` is printed beside it as non-governing. Pre-registered
predictions (B1 item 6) are printed beside the run's values; a value outside is
a finding and never a failure.

H3a (plan amendment 7, G1): each pair is a one-degree-of-freedom log-rank test,
so ``chi2_pilot = chi2.isf(logrank_p_raw, 1)``. The projection scales it by the
ratio of test-state counts, applies the Holm step-down correction, and reads
"pass reachable at full size" when every adjusted p is below ``H3A_ALPHA`` (read
from ``lpcstudy/analysis.py``). The reading is conditional on the pilot's chosen
K.

Exit codes: 0 if every row is computed and every reproduction check passes; 1
for a MISMATCH (a dump that does not reproduce its results leaf, or an interval
level that disagrees with the table; 1 takes precedence); 2 for unreadable
input, a usage error, a refused run, an internal error, or any "not computable"
item (a missing leaf, a ``None`` H3a pair, a run without a dump). The report is
always printed in full. A complete run with dumps exits 0; the dump-less P0 and
P1 pilots exit 2.
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import math
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy import stats as sps

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Imported after the path line; this module needs no jax import.
from lpcstudy.config import PRESETS  # noqa: E402

common = sys.modules.get("rehearsal_common")
if common is None:
    # Load the code shared by the two rehearsal tools (WU-0003.10) by path.
    _SPEC = importlib.util.spec_from_file_location(
        "rehearsal_common", Path(__file__).with_name("rehearsal_common.py")
    )
    assert _SPEC is not None and _SPEC.loader is not None
    common = importlib.util.module_from_spec(_SPEC)
    sys.modules["rehearsal_common"] = common
    _SPEC.loader.exec_module(common)

EXIT_MISMATCH = common.EXIT_MISMATCH
EXIT_INCOMPLETE = common.EXIT_INCOMPLETE
SCHEMAS = common.SCHEMAS
PRIMARY_LEVEL = common.PRIMARY_LEVEL
SECONDARY_LEVEL = 0.95
B_FACTOR = {"primary": 1.014, "secondary": 1.007}
"""E hw(B = 2000) / E hw(B = 500) at 1 - 0.05/3 and at 95% (M3,
``m3_bfactor.log``).
"""
B_FROM, B_TO = 500, 2000
BAND = (0.67, 1.5)
"""The C7 band, as multiples of the v3 value or of the projection."""
QN_TRAIN = {"logit": 0.61, "indicator": 0.74, "log_horizon": 0.61}
"""Lower end of the Q-N training-size range. The ratios come from the WU-0006
synthetic half-widths (0.0155/0.0255 and 0.0251/0.0341, M3); the upper end is
1.
"""
QN_TRAIN_FROM, QN_TRAIN_TO = 900, 3000
FALSE_TRIGGER_SD = {"default": (0.115, 0.08), "H3c": (0.18, 0.13)}
"""SD of log hw at the run's size and at the full size, per part (M3, "The
[0.67, 1.5] bands").
"""
BLOCK = 5
"""Block length of the long-run variance (the study's moving-block bootstrap).
"""
H2A_PARTIAL_EDGE = 0.1
"""Half-width of the H2a(ii) band on the partial correlation: a pass needs
``|pc| < 0.1 - hw``.
"""
V3_H2A_II = H2A_PARTIAL_EDGE - 0.01
"""The v3 section 7 phrase "needing ``|pc|`` about 0.01" written as a half-width
(derived, and labeled so in the report).
"""
MARGIN_V3 = 0.01
"""v3 section 7: a pass of H2a(ii) "would need a partial correlation within
about 0.01 of zero", so the margin ``m = 0.1 - hw_full`` is about 0.01. The
band [0.67, 1.5] applies to this margin (plan amendment 7, G3): "not
reproduced" exactly when ``m < 0.0067`` or ``m > 0.015``.
"""
KAPPA_POLICY = "range"
"""Which kappa_E governs the H2c, H2d and H3c projections: the pre-registered
range ``[sqrt(E_run/E_full), 1]`` (note
``2026-10-14-math-wu0003-3a-kappa.md``, R2; plan amendment 8, H1). The point
estimate is information only. The owner's choice (b), a half-split estimator
from a dump with ``core/cp_err_href`` and ``core/plp_err_href``, would
replace this constant.
"""
KAPPA_POLICIES = ("range",)
"""The admitted values of ``KAPPA_POLICY``. ``run`` refuses any other value
(exit 2), ``"point"`` included, so that no path computes a projection from
the point estimate (amendment 8, H3).
"""
H3A_TINY = 1e-300
"""A log-rank p below this has no finite chi-square in float64, so chi2 is only
a lower bound.
"""
SLACK = 0.005
"""Half a unit of the last printed digit of the pre-registered ranges (two
decimals).
"""


# ----------------------------------------------------------------------------
# errors and the report (shared with the diagnostics: tools/rehearsal_common.py)
# ----------------------------------------------------------------------------
NotComputable = common.NotComputable
Missing = common.Missing
Refused = common.Refused
Report = common.Report
# Names re-exported from the shared module; test_tools_rehearsal_common.py
# checks that each one is the shared object.
attempt = common.attempt
Dump = common.Dump
dig = common.dig
fmt = common.fmt
is_dev_id = common.is_dev_id
run_seed_id = common.run_seed_id
make_label = common.make_label
find_results = common.find_results
load_results = common.load_results


# ----------------------------------------------------------------------------
# the factors and the readings (pure)
# ----------------------------------------------------------------------------
def n_factor(n_run: float, n_full: float) -> float:
    """The sample-size factor ``sqrt(n_run / n_full)``.

    A regular statistic's half-width shrinks like ``1/sqrt(n)``, so using
    ``n_full`` states instead of ``n_run`` multiplies the half-width by this
    factor.

    Raises
    ------
    NotComputable
        If a size is not positive.
    """
    if not (n_run > 0 and n_full > 0):
        raise NotComputable(f"sizes must be positive: {n_run}, {n_full}")
    return math.sqrt(n_run / n_full)


def b_factor(level: str, b_run: int, b_full: int) -> float:
    """The bootstrap-endpoint factor of M3 for ``level`` in ``primary``,
    ``secondary``.

    Only the pair of resample counts 500 to 2000 was measured, plus the trivial
    case of equal counts.

    Raises
    ------
    NotComputable
        If the pair of resample counts is neither equal nor 500 to 2000.
    """
    if b_run == b_full:
        return 1.0
    if (b_run, b_full) != (B_FROM, B_TO):
        raise NotComputable(
            f"no measured B factor for B {b_run} to {b_full} (only {B_FROM} to "
            f"{B_TO} and equal B)"
        )
    return B_FACTOR[level]


def qn_range(kind: str, train_run: int, train_full: int) -> tuple[float, float]:
    """The Q-N training-size factor range ``[low, 1]``, or ``(1, 1)`` for equal
    sizes.

    Raises
    ------
    NotComputable
        If the sizes differ and are not the measured pair 900 to 3000.
    """
    if train_run == train_full:
        return 1.0, 1.0
    if (train_run, train_full) != (QN_TRAIN_FROM, QN_TRAIN_TO):
        raise NotComputable(
            f"no Q-N training factor for {train_run} to {train_full} (only "
            f"{QN_TRAIN_FROM} to {QN_TRAIN_TO} and equal sizes)"
        )
    return QN_TRAIN[kind], 1.0


def kappa_range(e_run: int, e_full: int) -> tuple[float, float]:
    """The range ``[sqrt(E_run / E_full), 1]`` of kappa_E (M3).

    The two ends are the cases where the per-state part of the variance is zero
    (only draw noise, which falls like ``1/E``) and where the draw part is zero.

    Raises
    ------
    NotComputable
        If the number of evaluation draws does not increase from run to full.
    """
    if e_full < e_run or e_run < 1:
        raise NotComputable(
            f"evaluation draws {e_run} to {e_full} do not increase"
        )
    return math.sqrt(e_run / e_full), 1.0


def kappa_combine(
    var_state: float, var_draw: float, e_run: int, e_full: int
) -> float:
    """The point estimate ``kappa = sqrt((V_s + V_d E_run/E_full) / (V_s +
    V_d))``.

    Here ``V_s`` is the state-to-state variance and ``V_d`` the draw variance
    (M3: the draw part falls like ``1/E``).

    Raises
    ------
    NotComputable
        If a variance is negative or not finite, the total is 0, or the draws do
        not increase.
    """
    if e_full < e_run or e_run < 1:
        raise NotComputable(
            f"evaluation draws {e_run} to {e_full} do not increase"
        )
    if (
        not (math.isfinite(var_state) and math.isfinite(var_draw))
        or var_state < 0
        or var_draw < 0
    ):
        raise NotComputable(
            f"variance not finite and non-negative: V_s {var_state}, V_d "
            f"{var_draw}"
        )
    total = var_state + var_draw
    if total == 0.0:
        raise NotComputable("V_s + V_d is 0 (constant influence series)")
    return math.sqrt((var_state + var_draw * e_run / e_full) / total)


def outside_nominal(value: float, reference: float) -> bool:
    """Reading (i): is ``value`` outside ``[0.67 reference, 1.5 reference]``?

    The band edges themselves count as inside.
    """
    return bool(value < BAND[0] * reference or value > BAND[1] * reference)


def outside_v3_range(low: float, high: float, v3: float) -> bool:
    """Reading (ii) against a v3 value.

    True when the whole range ``[low, high]`` lies outside ``[0.67 v3, 1.5
    v3]``. A range that touches the band is "inside". Pass the same number twice
    to test a single value (the H2a(ii) margin uses ``v3 = MARGIN_V3``).
    """
    return bool(high < BAND[0] * v3 or low > BAND[1] * v3)


def outside_projection_range(observed: float, low: float, high: float) -> bool:
    """Reading (ii) against an observed value.

    True when ``observed`` is below ``0.67 low`` or above ``1.5 high``.
    """
    return bool(observed < BAND[0] * low or observed > BAND[1] * high)


def false_trigger_rate(sd_run: float, sd_full: float) -> float:
    """Chance that the band fires by luck alone.

    If the log of the ratio (full-size half-width over its projection) is normal
    with SD ``sqrt(sd_run^2 + sd_full^2)``, this is the two-sided probability of
    landing outside ``[0.67, 1.5]``.
    """
    sigma = math.hypot(sd_run, sd_full)

    def cdf(x: float) -> float:
        return 0.5 * (1.0 + math.erf(x / (sigma * math.sqrt(2.0))))

    return cdf(math.log(BAND[0])) + 1.0 - cdf(math.log(BAND[1]))


def block_variance(values: np.ndarray, block: int = BLOCK) -> float:
    """``V*(b)``: ``b`` times the variance (ddof 0) of the overlapping block
    means.

    This is the exact moving-block bootstrap variance of the mean per
    observation. It uses all ``n - b + 1`` blocks, so there is no resampling
    noise.

    Raises
    ------
    NotComputable
        If the block does not fit the series or an entry is not finite.
    """
    x = np.asarray(values, dtype=float)
    if block < 1 or block > x.size:
        raise NotComputable(
            f"block length {block} does not fit a series of {x.size}"
        )
    if not np.all(np.isfinite(x)):
        raise NotComputable("non-finite entry in a series")
    windows = np.lib.stride_tricks.sliding_window_view(x - x.mean(), block)
    return float(block * windows.mean(axis=1).var())


def influence_diff(first: np.ndarray, second: np.ndarray) -> np.ndarray:
    """Influence series of ``mean(first - second)``: the centered difference
    (H2c).

    An influence series says how much each state pulls on a statistic; its
    long-run variance gives the statistic's sampling variance.
    """
    d = np.asarray(first, dtype=float) - np.asarray(second, dtype=float)
    return d - d.mean()


def influence_ratio(
    numerator: np.ndarray, denominator: np.ndarray
) -> np.ndarray:
    """Influence series of ``mean(a)/mean(b)``: ``(a_i - R b_i)/mean(b)`` (H2d,
    H3c).

    Raises
    ------
    NotComputable
        If the mean of the denominator is 0.
    """
    a, b = np.asarray(numerator, dtype=float), np.asarray(
        denominator, dtype=float
    )
    mean_b = float(b.mean())
    if mean_b == 0.0:
        raise NotComputable("mean of the denominator is 0")
    return (a - (float(a.mean()) / mean_b) * b) / mean_b


def kappa_estimate(
    state_first: np.ndarray,
    state_second: np.ndarray,
    real_first: np.ndarray,
    real_second: np.ndarray,
    kind: str,
    e_run: int,
    e_full: int,
    block: int = BLOCK,
) -> tuple[float, float, float]:
    """Point kappa_E, ``V_s`` and ``V_d`` of one criterion.

    The inputs are the draw-free per-state MSEs and the realized ones. The
    estimate is information only (see ``KAPPA_POLICY``).

    Parameters
    ----------
    state_first, state_second : np.ndarray
        Draw-free per-state MSEs ``V_i`` of the two rules (numerator and
        denominator, or minuend and subtrahend).
    real_first, real_second : np.ndarray
        The realized per-state MSEs (averaged over the run's ``e_run`` draws).
    kind : str
        ``"diff"`` (mean of the difference) or ``"ratio"`` (ratio of means).
    e_run, e_full : int
        Evaluation draws of the run and of the full preset.
    block : int
        Block length of the long-run variances.

    Returns
    -------
    tuple[float, float, float]
        ``(kappa, V_s, V_d)``.

    Raises
    ------
    ValueError
        If ``kind`` is neither ``"diff"`` nor ``"ratio"``.
    """
    make = {"diff": influence_diff, "ratio": influence_ratio}.get(kind)
    if make is None:
        raise ValueError(f"kind must be 'diff' or 'ratio', got {kind!r}")
    psi_state = make(state_first, state_second)
    psi_diff = make(real_first, real_second) - psi_state
    var_state, var_draw = block_variance(psi_state, block), block_variance(
        psi_diff, block
    )
    return (
        kappa_combine(var_state, var_draw, e_run, e_full),
        var_state,
        var_draw,
    )


def production_constant(name: str) -> float:
    """A numeric constant of ``lpcstudy/analysis.py``, read from its source
    text.

    The source is parsed instead of imported so that the tool does not load jax.

    Raises
    ------
    NotComputable
        If the file or the assignment is absent or not a literal number.
    """
    path = ROOT / "lpcstudy" / "analysis.py"
    try:
        tree = ast.parse(path.read_text())
    except (OSError, SyntaxError) as exc:
        raise NotComputable(f"{path} cannot be read: {exc}") from exc
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == name for t in node.targets
        ):
            try:
                return float(ast.literal_eval(node.value))
            except (ValueError, TypeError) as exc:
                raise NotComputable(
                    f"{name} in {path} is not a numeric literal"
                ) from exc
    raise NotComputable(f"{name} is not assigned in {path}")


def holm_adjust(p_values: Sequence[float]) -> list[float]:
    """Holm step-down adjusted p-values, in the original order.

    This is the production definition: sort the p-values, multiply the k-th
    smallest by ``m - k + 1``, and keep a running maximum (capped at 1).
    """
    p = np.asarray(p_values, dtype=float)
    adjusted = np.empty_like(p)
    running = 0.0
    for rank, idx in enumerate(np.argsort(p)):
        running = max(running, min(1.0, (len(p) - rank) * p[idx]))
        adjusted[idx] = running
    return adjusted.tolist()


def h3a_projection(p_raw: float | None, factor: float) -> dict:
    """The projected H3a statistic of one pair (note M3, conditional on
    K_pilot).

    ``chi2_pilot = chi2.isf(p_raw, 1)`` (exact for a one-degree-of-freedom
    log-rank test), ``chi2_full = factor x chi2_pilot`` and ``p_full =
    chi2.sf(chi2_full, 1)``. A ``p_raw`` below ``H3A_TINY`` gives the lower
    bound ``chi2 >= chi2.isf(H3A_TINY, 1)``; the pair still counts as computed
    and its projected p is reported as the strict upper bound ``H3A_TINY``,
    below every bar. ``None`` (an empty regime or zero log-rank variance) gives
    ``computed = False``.

    Raises
    ------
    NotComputable
        If ``p_raw`` is outside [0, 1] or not a number, or the factor is not
        positive.
    """
    if not factor > 0:
        raise NotComputable(f"H3a size factor {factor} is not positive")
    if p_raw is None:
        return {
            "computed": False,
            "p_raw": None,
            "chi2_pilot": None,
            "lower_bound": False,
            "chi2_full": None,
            "p_full": None,
            "p_full_bound": False,
        }
    p = float(p_raw)
    if not (0.0 <= p <= 1.0):
        raise NotComputable(f"log-rank p {p_raw!r} is not in [0, 1]")
    lower = p < H3A_TINY
    chi_pilot = float(sps.chi2.isf(H3A_TINY if lower else p, 1))
    chi_full = factor * chi_pilot
    # for a lower-bound pair sf underflows to 0.0, a false inequality as a "<=
    # 0": report the valid
    # strict bound instead (the factor is at least 1 and sf is decreasing)
    p_full = H3A_TINY if lower else float(sps.chi2.sf(chi_full, 1))
    return {
        "computed": True,
        "p_raw": p,
        "chi2_pilot": chi_pilot,
        "lower_bound": lower,
        "chi2_full": chi_full,
        "p_full": p_full,
        "p_full_bound": lower,
    }


def h3a_system(tree: dict, cfg: dict, full) -> dict:
    """H3a of one system: every pair projected, Holm on the projected p, the
    reading.

    The reading is ``"reachable"`` when every projected Holm-adjusted p is below
    ``H3A_ALPHA``, ``"not reachable"`` otherwise, and ``"not determined"`` if a
    pair has ``p_raw`` of None. Such a pair enters the Holm step as 1.0, as in
    production, so the other pairs' adjusted values stay valid.
    """
    block = dig(tree, "H3a")
    raw, pairs = dig(block, "logrank_p_raw"), dig(block, "pairs")
    k = dig(block, "chosen_K")
    if len(raw) != len(pairs) or not len(raw):
        raise NotComputable(
            f"H3a has {len(raw)} p-values for {len(pairs)} pairs"
        )
    factor = int(full.n_test) / int(dig(cfg, "n_test"))
    alpha = production_constant("H3A_ALPHA")
    entries = [
        dict(h3a_projection(p, factor), pair=list(pair))
        for p, pair in zip(raw, pairs, strict=True)
    ]
    adjusted = holm_adjust(
        [1.0 if e["p_full"] is None else e["p_full"] for e in entries]
    )
    for entry, adj in zip(entries, adjusted, strict=True):
        entry["holm_full"] = adj
    if any(not e["computed"] for e in entries):
        reading = "not determined"
    else:
        reading = "reachable" if max(adjusted) < alpha else "not reachable"
    return {
        "chosen_K": k,
        "factor": factor,
        "alpha": alpha,
        "entries": entries,
        "reading": reading,
        "largest_holm_full": max(adjusted),
    }


# ----------------------------------------------------------------------------
# the criteria
# ----------------------------------------------------------------------------
@dataclass(frozen=True)
class Spec:
    """One projected half-width (one row of the report).

    Attributes
    ----------
    label : str
        Name in the report (the labels of ``m3_projection.py`` except
        ``rho=0.01``).
    path : tuple[str, ...]
        Path of the block that holds the interval, under ``systems/<s>``.
    interval : str | tuple[str, ...]
        Key (or key path) of the interval in the block.
    estimate : str | tuple[str, ...] | None
        Key (or key path) of the point estimate in the block (None: not
        printed).
    level : str
        ``"primary"`` (1 - 0.05/3) or ``"secondary"`` (95%).
    size_key : str
        Configuration field of the criterion's own sample size.
    extra : str
        ``"none"``, ``"kappa"`` or ``"qn:<kind>"``.
    ratio : bool
        Whether the half-width is also printed relative to the point estimate.
    ratio_offset : float
        Added to the estimate to form the ratio ``R`` (1 for H2d, whose
        statistic is ``R - 1``).
    v3 : float | None
        The v3 section 7 half-width statement, if any.
    v3_note : str
        How the v3 value was obtained, when it is not a stated half-width.
    kappa : tuple[str, str, str] | None
        ``(kind, rule_first, rule_second)`` of a kappa_E criterion.
    kappa_leaf : tuple[str, ...] | None
        Path (under ``systems/<s>``) of the leaf that the dump's statistic must
        reproduce.
    rel_key : str | None
        Key of a leaf ``relative = estimate / (MSE level)`` in the block. The
        half-width is then also printed as ``hw / MSE level`` (H2c).
    margin : bool
        Whether the governing v3 comparison is on the margin ``0.1 - hw``
        (H2a(ii), G3); ``v3`` is then the non-governing half-width equivalent.
    """

    label: str
    path: tuple[str, ...]
    interval: str | tuple[str, ...]
    estimate: str | tuple[str, ...] | None
    level: str
    size_key: str
    extra: str = "none"
    ratio: bool = False
    ratio_offset: float = 0.0
    v3: float | None = None
    v3_note: str = ""
    kappa: tuple[str, str, str] | None = None
    kappa_leaf: tuple[str, ...] | None = None
    rel_key: str | None = None
    margin: bool = False


NON_GOVERNING_NOTE = (
    "non-governing: derived hw = 0.1 - 0.01 = 0.09 x [0.67, 1.5]"
)
"""Label printed beside the older, non-governing H2a(ii) comparison."""


def keys_of(key: str | tuple[str, ...]) -> tuple[str, ...]:
    """A key or a key path as a tuple."""
    return (key,) if isinstance(key, str) else tuple(key)


def specs_for(cfg: dict, best_single: str | None) -> list[Spec]:
    """The projected half-widths of one system (the 18 rows of
    ``m3_projection.py``, and V7).

    ``best_single`` is the H2c better single forecaster of the system (``A0`` or
    ``A1``), or None when that leaf is missing. The H2c second row is then
    absent and the caller reports it.
    """
    core = f"{float(cfg['core_noise']):g}"
    out = [
        Spec(
            "H1b PLP slope",
            ("H1b", "PLP"),
            "ci",
            "slope",
            "secondary",
            "n_test",
        ),
        Spec(
            "H1c PLP median ratio",
            ("H1c", "PLP"),
            "ci",
            "median_ratio",
            "secondary",
            "n_test",
            ratio=True,
        ),
        Spec(
            "H1d analog_seed",
            ("H1d", "rows", "analog_seed"),
            "interval",
            "spearman",
            "secondary",
            "n_test",
        ),
        Spec(
            f"H1a ratio rho={core}",
            ("H1a", "by_noise", core),
            "ratio_ci",
            "ratio",
            "secondary",
            "n_test_sweep",
            ratio=True,
        ),
        Spec(
            "Q-N oracle logit",
            ("Q-N", "oracle", "logit_w_interior"),
            "ci",
            "delta_r2",
            "secondary",
            "n_test",
            "qn:logit",
            v3=0.04,
        ),
        Spec(
            "Q-N oracle zero-ind",
            ("Q-N", "oracle", "w_zero_indicator"),
            "ci",
            "delta_r2",
            "secondary",
            "n_test",
            "qn:indicator",
        ),
        Spec(
            "Q-N oracle log_hor",
            ("Q-N", "oracle", "log_horizon"),
            "ci",
            "delta_r2",
            "secondary",
            "n_test",
            "qn:log_horizon",
        ),
        Spec(
            "H2a(i)", ("H2a",), "range_ci", "median_range", "primary", "n_test"
        ),
        Spec(
            "H2a(ii) zero",
            ("H2a", "part_ii", "zero"),
            "ci",
            "partial_corr",
            "primary",
            "n_test",
            v3=V3_H2A_II,
            margin=True,
            v3_note=NON_GOVERNING_NOTE,
        ),
        Spec(
            "H2a(ii) interior",
            ("H2a", "part_ii", "interior"),
            "ci",
            "partial_corr",
            "primary",
            "n_test",
            v3=V3_H2A_II,
            margin=True,
            v3_note=NON_GOVERNING_NOTE,
        ),
        Spec(
            "H2b(i)",
            ("H2b", "noise"),
            "ci",
            "mean_state_spearman",
            "primary",
            "n_test_sweep",
        ),
        Spec(
            "H2b(ii)",
            ("H2b", "library_change"),
            "ci",
            "mean_change",
            "primary",
            "n_test_sweep",
            v3=0.03,
        ),
        Spec(
            "H2c A4-A2",
            ("H2c", "A4_minus_A2"),
            "ci",
            "mean",
            "secondary",
            "n_test",
            "kappa",
            kappa=("diff", "A4", "A2"),
            kappa_leaf=("H2c", "A4_minus_A2", "mean"),
            rel_key="relative",
        ),
    ]
    if best_single is not None:
        out.append(
            Spec(
                f"H2c A4-{best_single}",
                ("H2c", f"A4_minus_{best_single}"),
                "ci",
                "mean",
                "secondary",
                "n_test",
                "kappa",
                kappa=("diff", "A4", best_single),
                kappa_leaf=("H2c", f"A4_minus_{best_single}", "mean"),
                rel_key="relative",
            )
        )
    out.append(
        Spec(
            "H2d",
            ("H2d",),
            "ci",
            "in_distribution_excess",
            "secondary",
            "n_test",
            "kappa",
            ratio=True,
            ratio_offset=1.0,
            kappa=("ratio", "A4", "A3"),
            kappa_leaf=("H2d", "in_distribution_excess"),
        )
    )
    for noise in cfg["library_sweep_noises"]:
        key = f"{float(noise):g}"
        out.append(
            Spec(
                f"H2e rho={key}",
                ("H2e", "by_noise", key),
                "ci",
                "median_change",
                "secondary",
                "n_test_sweep",
                v3=0.04,
            )
        )
    out.append(
        Spec(
            "H3c",
            ("H3c",),
            "ci",
            "A5_over_A4_mse",
            "primary",
            "n_test",
            "kappa",
            ratio=True,
            kappa=("ratio", "A5", "A4"),
            kappa_leaf=("H3c", "A5_over_A4_mse"),
        )
    )
    out.append(
        Spec(
            "V7 median slope",
            ("V7",),
            "ci",
            "median_slope",
            "secondary",
            "n_test_sweep",
        )
    )
    for noise in cfg["noise_levels"]:
        key = f"{float(noise):g}"
        out.append(
            Spec(
                f"V7 efficiency rho={key}",
                ("V7",),
                ("efficiency_ci_by_noise", key),
                ("efficiency_median_by_noise", key),
                "secondary",
                "n_test_sweep",
            )
        )
    return out


PREDICTIONS = {
    "H2e": ("narrower than v3 (0.44 to 0.76 of 0.04)", 0.44, 0.76),
    "H2b(ii)": (
        "near the lower edge of the band (0.68 to 0.85 of 0.03)",
        0.68,
        0.85,
    ),
    "Q-N oracle logit": (
        "undetermined by the projection (reading (ii) silent)",
        None,
        None,
    ),
}
"""Pre-registered predictions of B1 item 6, from P0 and P1: criterion prefix,
text and ratio range.
"""


def prediction_for(label: str) -> tuple[str, float | None, float | None] | None:
    """The pre-registered prediction that applies to a row label, or None."""
    for prefix, value in PREDICTIONS.items():
        if label == prefix or label.startswith(prefix + " "):
            return value
    return None


# ----------------------------------------------------------------------------
# kappa_E from the dump
# ----------------------------------------------------------------------------
@dataclass
class DumpView:
    """One system's dump together with the run it must belong to."""

    system: str
    dump: Dump
    cfg: dict
    res: dict
    rep: Report
    failed: str | None = None
    """The first defect of the dump (a provenance mismatch, a failed
    reproduction check, or an input that cannot be read). Once set, the dump
    supplies nothing (amendment 8, H1: "not used for anything").
    """

    def fail(self, reason: str) -> None:
        """Mark the dump unusable on its first defect (later ones keep the first
        reason).
        """
        if self.failed is None:
            self.failed = reason

    @property
    def ref(self) -> int:
        """Column of H_ref in the core arrays."""
        return int(self.dump.scalar("core/ref_index"))


def check_reproduction(
    view: DumpView,
    label: str,
    mine: float,
    leaf_path: tuple[str, ...],
    scale: float = 0.0,
    offset: float = 0.0,
    tol: float = 1e-12,
) -> bool:
    """Compare a statistic recomputed from the dump with its results leaf.

    A difference beyond the bound is a MISMATCH. The function returns whether
    the values matched; the caller must not use a dump that did not match.

    The bound is ``|mine + offset - leaf| <= tol max(|leaf|, scale)``. The
    default ``tol = 1e-12`` is about 10^3 additions of unit round-off with a
    margin of 10. The dump holds the very arrays the leaf was formed from, so
    the bound only has to cover a different order of the same additions.
    ``scale`` is the natural size of the terms of a mean of differences (the
    leaf itself may be near 0).
    """
    leaf = float(dig(view.res, *leaf_path))
    value = mine + offset
    diff = abs(value - leaf)
    allowed = tol * max(abs(leaf), scale)
    ok = bool(diff <= allowed)
    view.rep.say(
        f"  check {view.system} {label}: dump {value:.12g} vs results "
        f"{leaf:.12g} "
        f"(|diff| {diff:.2e}, allowed {allowed:.2e}): "
        f"{'MATCH' if ok else 'MISMATCH'}"
    )
    if not ok:
        view.rep.defect(
            f"{view.system} {label}: dump {value!r} vs results {leaf!r}"
        )
    return ok


def draw_free_mse(view: DumpView, rule: str) -> np.ndarray:
    """``V_i`` of a rule at H_ref: the per-state MSE averaged over the oracle
    moments only.

    Rule A0 (CP alone) has weight 1 and A1 (PLP alone) weight 0. The other rules
    use the dumped weight of every evaluation draw (``core/weight_href/<rule>``,
    shape ``(n, E)``), averaged over the draws.

    Raises
    ------
    NotComputable
        If the dumped weights do not have the shape ``(n, E)``.
    """
    d, ref = view.dump, view.ref
    e_c, e_p, cross = (d[f"core/{k}"][:, ref] for k in ("E_C", "E_P", "C"))
    if rule == "A0":
        weight = np.ones((len(e_c), 1))
    elif rule == "A1":
        weight = np.zeros((len(e_c), 1))
    else:
        weight = d[f"core/weight_href/{rule}"]
        if weight.ndim != 2 or weight.shape[0] != len(e_c):
            raise NotComputable(
                f"core/weight_href/{rule} has shape {weight.shape}, not (n, E)"
            )
    value = (
        weight**2 * e_c[:, None]
        + (1.0 - weight) ** 2 * e_p[:, None]
        + 2.0 * weight * (1.0 - weight) * cross[:, None]
    )
    return value.mean(axis=1)


def kappa_inputs(view: DumpView, spec: Spec) -> dict:
    """The validated arrays of one kappa criterion: realized and draw-free
    per-state MSEs.

    Raises
    ------
    NotComputable
        If the draws or the number of states disagree with the configuration, an
        array is missing, or an entry is not finite.
    """
    assert spec.kappa is not None
    _, first, second = spec.kappa
    d, ref = view.dump, view.ref
    n_draws = int(d.scalar("meta/n_eval_draws"))
    if n_draws != int(dig(view.cfg, "n_eval_draws")):
        raise NotComputable(
            f"dump n_eval_draws {n_draws} differs from the configuration's "
            f"{dig(view.cfg, 'n_eval_draws')}"
        )
    real = {r: d[f"core/state_mse/{r}"][:, ref] for r in (first, second)}
    state = {r: draw_free_mse(view, r) for r in (first, second)}
    n = len(real[first])
    if n != int(dig(view.cfg, "n_test")):
        raise NotComputable(
            f"dump holds {n} test states but the configuration has "
            f"{dig(view.cfg, 'n_test')}"
        )
    for arr in (*real.values(), *state.values()):
        if not np.all(np.isfinite(arr)):
            raise NotComputable("non-finite per-state MSE in the dump")
    return {"real": real, "state": state, "n": n, "n_draws": n_draws}


def verify_dump(view: DumpView, specs: Sequence[Spec]) -> None:
    """Run every reproduction check of the system's kappa criteria, once, before
    any use.

    A mismatch (MISMATCH, exit 1), an unreadable input (counted) or a provenance
    defect marks the dump as failed. A failed dump supplies no information value
    for any row.
    """
    for spec in specs:
        if spec.kappa is None or spec.kappa_leaf is None:
            continue
        kind, first, second = spec.kappa
        try:
            got = kappa_inputs(view, spec)
            a, b = got["real"][first], got["real"][second]
            if kind == "diff":
                diff = a - b
                ok = check_reproduction(
                    view,
                    f"{spec.label} mean",
                    float(diff.mean()),
                    spec.kappa_leaf,
                    scale=float(np.mean(np.abs(diff))),
                )
            else:
                ratio = float(a.mean() / b.mean())
                ok = check_reproduction(
                    view,
                    f"{spec.label} ratio",
                    ratio,
                    spec.kappa_leaf,
                    offset=-spec.ratio_offset,
                    scale=ratio if spec.ratio_offset else 0.0,
                )
        except NotComputable as exc:
            view.rep.nc(f"{view.system} {spec.label} dump check", str(exc))
            view.fail(f"{spec.label}: {exc}")
            continue
        except Exception as exc:  # noqa: BLE001
            # An unexpected input: counted, and the dump is not used.
            view.rep.internal(f"{view.system} {spec.label} dump check", exc)
            view.fail(f"{spec.label}: {type(exc).__name__}: {exc}")
            continue
        if not ok:
            view.fail(f"{spec.label} does not reproduce its results leaf")


def kappa_from_dump(view: DumpView, spec: Spec, e_full: int) -> dict:
    """The point kappa_E of one criterion (information only; it never enters a
    projection).

    A dump that failed any check (``verify_dump``, provenance) is not used. The
    block length is the run's ``bootstrap_block`` (a missing leaf is "not
    computable"; there is no default).

    Returns
    -------
    dict
        ``kappa``, ``V_s``, ``V_d`` and ``n``.

    Raises
    ------
    NotComputable
        If the dump failed a check or an input is missing.
    """
    assert spec.kappa is not None and spec.kappa_leaf is not None
    if view.failed is not None:
        raise NotComputable(
            f"the dump of {view.system} failed a check ({view.failed}); not "
            "used"
        )
    kind, first, second = spec.kappa
    block = int(dig(view.cfg, "bootstrap_block"))
    got = kappa_inputs(view, spec)
    value, var_state, var_draw = kappa_estimate(
        got["state"][first],
        got["state"][second],
        got["real"][first],
        got["real"][second],
        kind,
        got["n_draws"],
        e_full,
        block,
    )
    return {"kappa": value, "V_s": var_state, "V_d": var_draw, "n": got["n"]}


def open_dump(
    folder: Path, system: str, cfg: dict, res: dict, seed_id: str, rep: Report
) -> DumpView | None:
    """Open the system's dump as a ``DumpView``; return None (with a "not
    computable" line) if unusable.

    The dump's schema, system and preset are checked against the run.

    Raises
    ------
    Refused
        If the dump records no seed id, or one that differs from the run's or is
        not ``DEV-n``.
    """
    file = folder / f"{system}.npz"
    if not file.is_file():
        rep.nc(
            f"{system} kappa_E (H2c, H2d, H3c)",
            f"{file} not found (run without "
            "--states-dump?); the range is used",
        )
        return None
    try:
        dump = Dump.load(file)
    except Exception as exc:  # noqa: BLE001
        # A corrupt archive: exit 2.
        rep.internal(f"{system} dump", exc)
        return None
    try:
        schema = dump.scalar("meta/schema") if dump.has("meta/schema") else None
        if schema not in SCHEMAS:
            rep.nc(
                f"{system} kappa_E (H2c, H2d, H3c)",
                f"schema {schema!r} is not one of "
                f"{SCHEMAS}; the range is used",
            )
            dump.close()
            return None
        problem: str | None = None
        for key, expected in (
            ("meta/system", system),
            ("meta/preset", cfg.get("name")),
        ):
            if not dump.has(key):
                rep.nc(
                    f"{system} dump provenance",
                    f"array {key!r} is not in {dump.source}",
                )
                problem = problem or f"{key} is absent"
            elif str(dump.scalar(key)) != str(expected):
                rep.defect(
                    f"{system}: {key} is {dump.scalar(key)!r} in the dump but "
                    f"{expected!r} in results.json (the dump is not this run's)"
                )
                problem = (
                    problem
                    or f"{key} is {dump.scalar(key)!r}, not {expected!r}"
                )
        if not dump.has("meta/seed_id"):
            raise Refused(
                f"refused: the dump of {system} records no seed id "
                f"({dump.source})"
            )
        dump_id = str(dump.scalar("meta/seed_id"))
        if dump_id != seed_id or not is_dev_id(dump_id):
            raise Refused(
                f"refused: the dump of {system} records seed id {dump_id!r} "
                "but the run "
                f"records {seed_id!r} (all recorded ids must agree and be "
                "DEV-n)"
            )
    except BaseException:
        dump.close()
        raise
    return DumpView(system, dump, cfg, res, rep, failed=problem)


# ----------------------------------------------------------------------------
# one criterion
# ----------------------------------------------------------------------------
def interval_of(block: dict, spec: Spec) -> tuple[float, float]:
    """The interval of a criterion as two finite floats, ``lo < hi``."""
    raw = dig(block, *keys_of(spec.interval))
    if not isinstance(raw, (list, tuple)) or len(raw) != 2:
        raise NotComputable(f"interval {raw!r} is not a pair")
    lo, hi = float(raw[0]), float(raw[1])
    if not (math.isfinite(lo) and math.isfinite(hi)) or not hi > lo:
        raise NotComputable(
            f"half-width not finite and positive: interval [{lo}, {hi}]"
        )
    return lo, hi


def level_of(spec: Spec) -> float:
    """The interval level of a criterion."""
    return PRIMARY_LEVEL if spec.level == "primary" else SECONDARY_LEVEL


def check_level(rep: Report, where: str, block: dict, spec: Spec) -> None:
    """Record a MISMATCH if the recorded level differs from the table's."""
    stated = block.get("level")
    if stated is not None and abs(float(stated) - level_of(spec)) > 1e-9:
        rep.defect(
            f"{where}: the results record level {stated!r} but the table has "
            f"{level_of(spec)!r}"
        )


def project_row(
    spec: Spec,
    system: str,
    tree: dict,
    cfg: dict,
    view: DumpView | None,
    rep: Report,
    full,
) -> dict:
    """Everything the report says about one criterion of one system.

    The row holds the run's half-width, the factors, the projected range, the
    readings against v3 and the false-trigger rate. For kappa_E the
    pre-registered range governs and is printed as FALLBACK (a computed row,
    amendment 8, H1). The point estimate from a dump without any defect is only
    information; it never enters ``x_lo``, ``x_hi`` or any number of the row.

    Raises
    ------
    NotComputable
        If a needed leaf is missing or not usable.
    Missing
        If the criterion's block is absent.
    """
    where = f"{system} {spec.label}"
    block = dig(tree, *spec.path)
    if not isinstance(block, dict):
        raise Missing(
            f"{where}: results leaf {'/'.join(spec.path)} is not a block"
        )
    lo, hi = interval_of(block, spec)
    hw = (hi - lo) / 2.0
    check_level(rep, where, block, spec)
    estimate = (
        float(dig(block, *keys_of(spec.estimate))) if spec.estimate else None
    )
    n_run, n_full = int(dig(cfg, spec.size_key)), int(
        getattr(full, spec.size_key)
    )
    fn = n_factor(n_run, n_full)
    fb = b_factor(
        spec.level,
        int(dig(cfg, "bootstrap_resamples")),
        int(full.bootstrap_resamples),
    )
    e_run, e_full = int(dig(cfg, "n_eval_draws")), int(full.n_eval_draws)
    note = ""
    kappa_info: dict | None = None
    if spec.extra == "none":
        x_lo = x_hi = 1.0
    elif spec.extra.startswith("qn:"):
        x_lo, x_hi = qn_range(
            spec.extra[3:],
            int(dig(cfg, "n_construction")) + int(dig(cfg, "n_calibration")),
            full.n_construction + full.n_calibration,
        )
        note = "Q-N training-size range"
    elif e_run == e_full:
        x_lo = x_hi = 1.0
        note = "kappa_E 1 (same number of evaluation draws)"
    else:
        r_lo, r_hi = kappa_range(e_run, e_full)
        x_lo, x_hi = r_lo, r_hi
        note = f"kappa_E range [{r_lo:.3f}, {r_hi:.3f}] (FALLBACK)"
        if view is not None:
            # a failure is recorded by attempt() with its reason (exit 2); the
            # range is used
            got = attempt(
                rep,
                f"{where} kappa_E (the range is used)",
                kappa_from_dump,
                view,
                spec,
                e_full,
            )
            if got is not None:
                kappa_info = got
                note += (
                    f" -- kappa_E point estimator biased (R2): range governs; "
                    "point kappa "
                    f"{got['kappa']:.4f} is information only, not an estimator "
                    "of kappa_E"
                )
            else:
                note += " -- kappa_E point estimator biased (R2): range governs"
        else:
            note += (
                " -- kappa_E point estimator biased (R2): range governs; "
                "no dump"
            )
        # a missing or unusable dump is a "not computable" item of its own
        # (open_dump or attempt)
    f_lo, f_hi = fn * fb * x_lo, fn * fb * x_hi
    row = {
        "label": spec.label,
        "system": system,
        "hw_run": hw,
        "estimate": estimate,
        "n_run": n_run,
        "n_full": n_full,
        "f_n": fn,
        "f_b": fb,
        "f_lo": f_lo,
        "f_hi": f_hi,
        "hw_lo": hw * f_lo,
        "hw_hi": hw * f_hi,
        "nominal": hw * fn,
        "note": note,
        "kappa": kappa_info,
        "level": level_of(spec),
        "kappa_governs": (
            "range" if spec.extra == "kappa" and e_run != e_full else "n/a"
        ),
        "kappa_range": (
            [x_lo, x_hi] if spec.extra == "kappa" and e_run != e_full else None
        ),
    }
    if spec.ratio and estimate is not None:
        r_hat = estimate + spec.ratio_offset
        if r_hat == 0.0 or not math.isfinite(r_hat):
            raise NotComputable(
                f"{where}: ratio estimate {r_hat} cannot scale a half-width"
            )
        row["rel_run"] = hw / abs(r_hat)
        row["rel_lo"], row["rel_hi"] = (
            row["rel_run"] * f_lo,
            row["rel_run"] * f_hi,
        )
    if spec.rel_key is not None:
        relative = float(dig(block, spec.rel_key))
        if (
            estimate is None
            or estimate == 0.0
            or relative == 0.0
            or not math.isfinite(relative)
        ):
            raise NotComputable(
                f"{where}: mean {estimate} and relative {relative} give no MSE "
                "level"
            )
        row["rel_run"] = hw / abs(estimate / relative)
        row["rel_lo"], row["rel_hi"] = (
            row["rel_run"] * f_lo,
            row["rel_run"] * f_hi,
        )
    if spec.label.startswith("H2a(ii)"):
        row["pass_bound_lo"] = H2A_PARTIAL_EDGE - row["hw_hi"]
        row["pass_bound_hi"] = H2A_PARTIAL_EDGE - row["hw_lo"]
    sd = FALSE_TRIGGER_SD["H3c" if spec.label == "H3c" else "default"]
    row["false_trigger"] = false_trigger_rate(*sd)
    if spec.v3 is not None:
        v3 = spec.v3
        row["v3"] = v3
        row["v3_note"] = spec.v3_note
        row["ratio_lo"], row["ratio_hi"] = row["hw_lo"] / v3, row["hw_hi"] / v3
        row["ratio_nominal"] = row["nominal"] / v3
        row["reading_i"] = outside_nominal(row["nominal"], v3)
        row["reading_ii"] = outside_v3_range(row["hw_lo"], row["hw_hi"], v3)
        if spec.margin:
            # G3: the governing comparison is on the margin m = 0.1 - hw; the hw
            # band is kept
            row["legacy_reading_i"], row["legacy_reading_ii"] = (
                row["reading_i"],
                row["reading_ii"],
            )
            m_nom = H2A_PARTIAL_EDGE - row["nominal"]
            row["margin_nominal"] = m_nom
            row["margin_lo"], row["margin_hi"] = (
                row["pass_bound_lo"],
                row["pass_bound_hi"],
            )
            row["reading_i"] = outside_v3_range(m_nom, m_nom, MARGIN_V3)
            row["reading_ii"] = outside_v3_range(
                row["margin_lo"], row["margin_hi"], MARGIN_V3
            )
    prediction = prediction_for(spec.label)
    if prediction is not None and spec.v3 is not None:
        text, p_lo, p_hi = prediction
        if p_lo is not None and p_hi is not None:
            inside = bool(
                row["ratio_lo"] >= p_lo - SLACK
                and row["ratio_hi"] <= p_hi + SLACK
            )
        else:
            inside = not row["reading_ii"]
        row["prediction"] = {"text": text, "within": inside}
    return row


def observed_row(
    spec: Spec, system: str, tree: dict, projected: dict, rep: Report
) -> dict:
    """The observed full-size half-width of a criterion against the projection
    of the run.
    """
    where = f"{system} {spec.label}"
    block = dig(tree, *spec.path)
    if not isinstance(block, dict):
        raise Missing(
            f"{where}: observed results leaf {'/'.join(spec.path)} is not a "
            "block"
        )
    lo, hi = interval_of(block, spec)
    observed = (hi - lo) / 2.0
    check_level(rep, f"{where} (observed)", block, spec)
    return {
        "observed": observed,
        "obs_ratio_nominal": observed / projected["nominal"],
        "obs_ratio_lo": observed / projected["hw_hi"],
        "obs_ratio_hi": observed / projected["hw_lo"],
        "obs_reading_i": outside_nominal(observed, projected["nominal"]),
        "obs_reading_ii": outside_projection_range(
            observed, projected["hw_lo"], projected["hw_hi"]
        ),
    }


# ----------------------------------------------------------------------------
# the report
# ----------------------------------------------------------------------------
def which(row: dict, prefix: str = "") -> str:
    """``"(i)"``, ``"(ii)"``, ``"(i) and (ii)"`` or ``""``: the readings that
    fire.

    ``prefix`` selects the observed readings (``"obs_"``) instead of the v3
    ones.
    """
    hits = [
        name
        for name, key in (("(i)", "reading_i"), ("(ii)", "reading_ii"))
        if row.get(prefix + key)
    ]
    return " and ".join(hits)


def side(outside: bool) -> str:
    """The word printed for a reading: ``OUTSIDE`` or ``inside`` the band."""
    return "OUTSIDE" if outside else "inside"


def format_row(row: dict) -> list[str]:
    """The report lines of one projected criterion."""
    rel = (
        f"  rel hw {row['rel_run']:.4f} -> "
        f"{row['rel_lo']:.4f}-{row['rel_hi']:.4f}"
        if "rel_run" in row
        else ""
    )
    lines = [
        f"  {row['label']:22s} hw {row['hw_run']:9.4f}  "
        f"x{row['f_lo']:6.3f}-{row['f_hi']:5.3f}"
        f"  -> {row['hw_lo']:8.4f}-{row['hw_hi']:7.4f}{rel}  "
        f"[{row['note'] or 'n and B only'}]"
        f"  false-trigger {100.0 * row['false_trigger']:.1f}%"
    ]
    if "pass_bound_lo" in row:
        impossible = (
            "; IMPOSSIBLE at the lower projection of hw"
            if row["pass_bound_hi"] < 0
            else ""
        )
        lines.append(
            f"      pass needs |pc| < {row['pass_bound_lo']:+.3f} .. "
            f"{row['pass_bound_hi']:+.3f}{impossible} (v3: about 0.01)"
        )
    if "margin_nominal" in row:
        flag = which(row)
        lo_m, hi_m = BAND[0] * MARGIN_V3, BAND[1] * MARGIN_V3
        legacy = " and ".join(
            name
            for name, key in (
                ("(i)", "legacy_reading_i"),
                ("(ii)", "legacy_reading_ii"),
            )
            if row[key]
        )
        lines.append(
            f"      v3 margin about {MARGIN_V3:g} x [0.67, 1.5] = [{lo_m:.4f}, "
            f"{hi_m:.3f}] "
            f"(hw_full in [{H2A_PARTIAL_EDGE - hi_m:.4f}, "
            f"{H2A_PARTIAL_EDGE - lo_m:.4f}]): "
            f"margin {row['margin_lo']:+.4f}..{row['margin_hi']:+.4f} (n only "
            f"{row['margin_nominal']:+.4f}); GOVERNING reading (i) "
            f"{side(row['reading_i'])}, (ii) "
            f"{side(row['reading_ii'])}"
            + (f" -> v3 precision not reproduced by {flag}" if flag else "")
        )
        lines.append(
            f"      non-governing, hw against 0.09 x [0.67, 1.5] = "
            f"[{0.67 * 0.09:.4f}, "
            f"{1.5 * 0.09:.3f}]: ratio "
            f"{row['ratio_lo']:.3f}-{row['ratio_hi']:.3f}; "
            f"(i) {side(row['legacy_reading_i'])}, (ii) "
            f"{side(row['legacy_reading_ii'])}"
            + (f" -> would be not reproduced by {legacy}" if legacy else "")
        )
    elif "v3" in row:
        flag = which(row)
        lines.append(
            f"      v3 {row['v3']:g}: ratio to v3 "
            f"{row['ratio_lo']:.3f}-{row['ratio_hi']:.3f} "
            f"(n only: {row['ratio_nominal']:.3f}); reading (i) "
            f"{side(row['reading_i'])}, (ii) "
            f"{side(row['reading_ii'])}"
            + (f" -> v3 precision not reproduced by {flag}" if flag else "")
            + (f"  [{row['v3_note']}]" if row.get("v3_note") else "")
        )
    if "prediction" in row:
        word = "within" if row["prediction"]["within"] else "OUTSIDE (finding)"
        lines.append(
            f"      pre-registered: {row['prediction']['text']}: {word}"
        )
    if "observed" in row:
        flag = which(row, "obs_")
        lines.append(
            f"      observed hw {row['observed']:.4f}: against the projection "
            f"{row['obs_ratio_lo']:.3f}-{row['obs_ratio_hi']:.3f} (n only "
            f"{row['obs_ratio_nominal']:.3f}); reading (i) "
            f"{side(row['obs_reading_i'])}, (ii) "
            f"{side(row['obs_reading_ii'])}"
            + (f" -> outside the band by {flag}" if flag else "")
        )
    return lines


def format_h3a(system: str, got: dict) -> list[str]:
    """The report lines of the H3a projection of one system."""
    lines = [
        f"  H3a {system}: conditional on K_pilot = {got['chosen_K']}; "
        "chi2_full = "
        f"{got['factor']:g} x chi2_pilot, Holm on the projected p, bar "
        f"{got['alpha']:g} "
        f"(analysis.H3A_ALPHA)"
    ]
    for e in got["entries"]:
        if not e["computed"]:
            lines.append(
                f"      pair {tuple(e['pair'])}: p_raw None (empty regime or "
                "zero log-rank "
                "variance): not computable"
            )
            continue
        bound = ">= " if e["lower_bound"] else ""
        lines.append(
            f"      pair {tuple(e['pair'])}: p_raw {e['p_raw']:.4g}, chi2 "
            f"{bound}"
            f"{e['chi2_pilot']:.4g} -> {bound}{e['chi2_full']:.4g}, p_full "
            f"{'< ' if e['lower_bound'] else ''}{e['p_full']:.4g}, Holm "
            f"{'< ' if e['lower_bound'] else ''}{e['holm_full']:.4g}"
        )
    lines.append(
        f"      pass reachable at full size: {got['reading']} (largest "
        "projected "
        f"Holm-adjusted p {got['largest_holm_full']:.3g}), conditional on "
        "K_pilot"
    )
    return lines


def summary_lines(rep: Report, observed: bool) -> list[str]:
    """The run-level summary: readings that fire, predictions, fallbacks."""
    rows = [r for rows in rep.data.get("rows", {}).values() for r in rows]
    out = ["Summary"]
    v3 = [r for r in rows if "v3" in r]
    out.append(
        f"  v3 section 7 comparison: {len(v3)} parts; reading (i) fires on "
        f"{sum(r['reading_i'] for r in v3)}, reading (ii) on "
        f"{sum(r['reading_ii'] for r in v3)}, "
        f"either on {sum(bool(which(r)) for r in v3)}"
    )
    for r in v3:
        if which(r) and "margin_nominal" in r:
            out.append(
                f"    v3 precision not reproduced ({which(r)}, margin "
                f"reading): {r['system']} "
                f"{r['label']}: margin 0.1 - hw_full = "
                f"{r['margin_lo']:+.4f}..{r['margin_hi']:+.4f} "
                f"against {BAND[0] * MARGIN_V3:.4f}..{BAND[1] * MARGIN_V3:.3f}"
            )
        elif which(r):
            out.append(
                f"    v3 precision not reproduced ({which(r)}): {r['system']} "
                f"{r['label']}: "
                f"projected {r['hw_lo']:.4f}-{r['hw_hi']:.4f} against v3 "
                f"{r['v3']:g}"
            )
    margin_rows = [r for r in v3 if "margin_nominal" in r]
    n_legacy = sum(
        bool(r["legacy_reading_i"] or r["legacy_reading_ii"])
        for r in margin_rows
    )
    out.append(
        f"  H2a(ii) margin reading (governing, G3): fires on "
        f"{sum(bool(which(r)) for r in margin_rows)} of {len(margin_rows)} "
        "parts "
        "(pre-registered: most); the hw band 0.09 x [0.67, 1.5] would fire on "
        f"{n_legacy}"
    )
    preds = [r for r in rows if "prediction" in r]
    out.append(
        f"  pre-registered predictions: "
        f"{sum(r['prediction']['within'] for r in preds)} of "
        f"{len(preds)} parts within"
    )
    for r in preds:
        if not r["prediction"]["within"]:
            out.append(
                f"    outside (finding): {r['system']} {r['label']}: "
                f"{r['prediction']['text']}"
            )
    kappa_rows = [
        r for r in rows if r["label"].startswith(("H2c", "H2d", "H3c"))
    ]
    governed = sum(r["kappa_governs"] == "range" for r in kappa_rows)
    info = sum(r["kappa"] is not None for r in kappa_rows)
    ranges = sorted(
        {tuple(r["kappa_range"]) for r in kappa_rows if r["kappa_range"]}
    )
    text = " and ".join(f"[{lo:.4f}, {hi:g}]" for lo, hi in ranges) or "[none]"
    out.append(
        f"  kappa_E: the range {text} governs {governed} of {len(kappa_rows)} "
        "parts "
        f"(FALLBACK rows, counted as computed; KAPPA_POLICY {KAPPA_POLICY!r}); "
        "point kappa "
        f"shown as information for {info} (not an estimator of kappa_E)"
    )
    expected = sum(r["false_trigger"] for r in rows)
    out.append(
        f"  predicted false triggers of the band over the {len(rows)} parts: "
        f"{expected:.2f} "
        "(sum of the per-part rates)"
    )
    if observed:
        obs = [r for r in rows if "observed" in r]
        out.append(
            f"  observed against the R1 projection: {len(obs)} parts; reading "
            "(i) outside on "
            f"{sum(r['obs_reading_i'] for r in obs)}, (ii) on "
            f"{sum(r['obs_reading_ii'] for r in obs)}"
        )
        for r in obs:
            if which(r, "obs_"):
                out.append(
                    f"    outside the band ({which(r, 'obs_')}): {r['system']} "
                    f"{r['label']}: "
                    f"observed {r['observed']:.4f} against "
                    f"{r['hw_lo']:.4f}-{r['hw_hi']:.4f}"
                )
    h3a = rep.data.get("h3a", {})
    for system, got in h3a.items():
        out.append(
            f"  H3a {system} (conditional on K_pilot = {got['chosen_K']}): "
            "pass reachable at "
            f"full size: {got['reading']} (largest projected Holm p "
            f"{got['largest_holm_full']:.3g}, bar {got['alpha']:g})"
        )
    return out


def run(
    results_path: Path,
    states_dir: Path | None = None,
    systems: Sequence[str] | None = None,
    observed_path: Path | None = None,
    rep: Report | None = None,
) -> Report:
    """Build the whole report.

    The report goes into ``rep`` if one is given, so that a caller keeps it even
    after a crash.

    Raises
    ------
    NotComputable
        If a results file is unreadable.
    Refused
        If a recorded seed id is not a development id or the recorded ids
        disagree.
    """
    if KAPPA_POLICY not in KAPPA_POLICIES:
        raise NotComputable(
            f"unknown KAPPA_POLICY {KAPPA_POLICY!r}: expected one of "
            f"{KAPPA_POLICIES}; refusing to report with an uncounted fallback"
        )
    path, results, seed_id = load_results(results_path)
    cfg = results["config"]
    obs_results, obs_seed = None, None
    if observed_path is not None:
        obs_file, obs_results, obs_seed = load_results(observed_path)
    full = PRESETS["full"]
    folder = states_dir if states_dir is not None else path.parent / "states"
    rep = rep if rep is not None else Report()
    rep.say(make_label(seed_id))
    rep.say(
        "rehearsal_report (WU-0003.3a): C7 projections to the full preset; "
        "needs owner review "
        "before freeze (sample-size decision)"
    )
    rep.say(
        f"run: {path}; preset {cfg.get('name')} (n_test {cfg.get('n_test')}, "
        "n_test_sweep "
        f"{cfg.get('n_test_sweep')}, E {cfg.get('n_eval_draws')}, B "
        f"{cfg.get('bootstrap_resamples')}) -> full (n_test {full.n_test}, "
        "n_test_sweep "
        f"{full.n_test_sweep}, E {full.n_eval_draws}, B "
        f"{full.bootstrap_resamples}); commit "
        f"{results['provenance'].get('commit', 'not recorded')}"
    )
    if obs_results is not None:
        rep.say(
            f"observed: {obs_file}; preset "
            f"{obs_results['config'].get('name')}; seed id "
            f"{obs_seed} (the run's own is {seed_id}; the two realizations are "
            "independent)"
        )
        if obs_results["config"].get("name") != "full":
            raise NotComputable(
                f"--observed run {obs_file} is preset "
                f"{obs_results['config'].get('name')!r}, not 'full'"
            )
    rep.data["label"] = make_label(seed_id)
    rep.data["rows"] = {}
    rep.data["kappa_policy"] = KAPPA_POLICY
    rep.data["h3a"] = {}
    all_systems = list(results.get("systems", {}))
    chosen = [s for s in all_systems if systems is None or s in systems]
    # R11: every requested system (all of config.core_systems unless restricted)
    # must be present
    core: list[str] = []
    try:
        raw_core = dig(cfg, "core_systems")
        if (
            not isinstance(raw_core, (list, tuple))
            or not raw_core
            or not all(isinstance(c, str) and c for c in raw_core)
        ):
            raise NotComputable(
                f"{raw_core!r} is not a non-empty list of system names"
            )
        core = list(raw_core)
    except NotComputable as exc:
        rep.nc(
            "config core_systems",
            f"{exc}; the systems that must be present are unknown",
        )
    for wanted in (list(systems) if systems else core):
        if wanted not in all_systems:
            rep.nc(
                f"system {wanted}",
                "not in results.json"
                + ("" if systems else " (it is in config core_systems)"),
            )
    for extra in chosen:
        if core and extra not in core:
            rep.say(
                f"note: system {extra} is in results.json but not in config "
                "core_systems "
                f"{core}; it is reported"
            )
    for system in chosen:
        rep.say("")
        rep.say(f"=== {system} ({seed_id}) ===")
        tree = results["systems"][system]
        needs_dump = int(dig(cfg, "n_eval_draws")) != int(full.n_eval_draws)
        view = (
            open_dump(folder, system, cfg, tree, seed_id, rep)
            if needs_dump
            else None
        )
        rows: list[dict] = []
        rep.data["rows"][system] = rows
        try:
            try:
                best = str(dig(tree, "H2c", "best_single"))
                if best not in ("A0", "A1"):
                    raise NotComputable(
                        f"H2c best_single {best!r} is not A0 or A1"
                    )
            except NotComputable as exc:
                rep.nc(
                    f"{system} H2c second row (A4 against the best single "
                    "forecaster)",
                    str(exc),
                )
                best = None
            specs = specs_for(cfg, best)
            if view is not None:
                verify_dump(view, specs)
            for spec in specs:
                row = attempt(
                    rep,
                    f"{system} {spec.label}",
                    project_row,
                    spec,
                    system,
                    tree,
                    cfg,
                    view,
                    rep,
                    full,
                )
                if row is None:
                    continue
                if obs_results is not None:
                    got = attempt(
                        rep,
                        f"{system} {spec.label} (observed)",
                        observed_row,
                        spec,
                        system,
                        obs_results["systems"].get(system, {}),
                        row,
                        rep,
                    )
                    if got is not None:
                        row.update(got)
                rows.append(row)
                for line in format_row(row):
                    rep.say(line)
            got = attempt(rep, f"{system} H3a", h3a_system, tree, cfg, full)
            if got is not None:
                rep.data["h3a"][system] = got
                for line in format_h3a(system, got):
                    rep.say(line)
                for entry in got["entries"]:
                    if not entry["computed"]:
                        rep.nc(
                            f"{system} H3a pair {tuple(entry['pair'])}",
                            "p_raw is None (empty regime or zero log-rank "
                            "variance): chi2 not "
                            "computable",
                        )
        finally:
            if view is not None:
                view.dump.close()
    rep.say("")
    for line in summary_lines(rep, obs_results is not None):
        rep.say(line)
    rep.say("")
    if rep.incomplete:
        rep.say(
            f"not computable: {len(rep.incomplete)} item(s) (listed above); "
            "never skipped"
        )
    if rep.defects:
        rep.say(f"MISMATCH: {len(rep.defects)} item(s) (listed above)")
    return rep


_json_ready = common.json_ready


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point; returns the exit code."""
    ap = argparse.ArgumentParser(
        description="C7 projections for the precision report: pilot "
        "half-widths to the full preset (WU-0003.3a)."
    )
    ap.add_argument(
        "run", type=Path, help="results.json of the rehearsal, or the directory"
    )
    ap.add_argument(
        "--states", type=Path, default=None, help="folder of <system>.npz dumps"
    )
    ap.add_argument(
        "--systems", nargs="+", default=None, help="restrict to these systems"
    )
    ap.add_argument(
        "--observed",
        type=Path,
        default=None,
        help="results.json (or directory) of a full-size run to compare "
        "with the projection",
    )
    ap.add_argument(
        "--json", type=Path, default=None, help="write the numbers to this file"
    )
    args = ap.parse_args(argv)
    rep = Report()
    try:
        run(args.run, args.states, args.systems, args.observed, rep=rep)
    except NotComputable as exc:
        # Unreadable input or a refused run: nothing else is trusted.
        print(f"rehearsal_report: error: {exc}", file=sys.stderr)
        return EXIT_INCOMPLETE
    except Exception as exc:  # noqa: BLE001
        # Keep the report and exit 2, never the MISMATCH code.
        rep.internal("run", exc)
        rep.say("INTERNAL ERROR: the report above is partial; exit 2")
    print("\n".join(rep.lines))
    if args.json is not None:
        args.json.write_text(json.dumps(_json_ready(rep.data), indent=1))
    return rep.exit_code()


if __name__ == "__main__":
    sys.exit(main())
