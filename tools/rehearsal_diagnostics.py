#!/usr/bin/env python3
"""Rehearsal diagnostics D1 to D6 from ``results.json`` and the per-state dump (WU-0003.8).

DEVELOPMENT only: conditional on one realization, never the confirmatory seed, not a hypothesis
test. **Needs owner review before freeze** (statistics feeding the block-length and M decisions).
The tool is read-only on run directories, is not imported by the package, and prints one report
labelled DEVELOPMENT. Usage::

    .venv/bin/python -I tools/rehearsal_diagnostics.py RUN [--states DIR] [--systems S ...] [--json OUT]
        [--seed N] [--resamples B] [--permutations P]

``RUN`` is a ``results.json`` or the directory that holds it; the dump of each system is
``<dir>/states/<system>.npz`` (schema ``lpcstudy.states/1``, the module docstring of
``lpcstudy/dump.py``; ``--states`` overrides the folder). The run's ``seed_id`` must be a
development seed ``DEV-n`` (anything else is refused, exit 2).

What it computes (plan amendment 2, B1 item 7 as amended; mathematics check
``docs/agent/notes/2026-10-14-math-wu0003.md``, M3 to M5; amendments 3 and 4 for the dump):

* **D1.** The influence series of every criterion (M4.1) over all states of its split in time
  order, 0 outside the criterion's domain: sign types for the medians (H2a(i), H2e), the
  influence of the partial correlation (H2a(ii) zero, interior and, when triggered, one), of an
  OLS slope (H1b), of a ratio of means (H3c, H2d), of a difference of means (H2c, H2b(ii), H2b(i)
  through the per-state Spearman) and of the Q-N gain ``Delta R^2``. Its autocorrelation at lags
  1 to 10 and the readings of the rule: ``|acf(1)| <= 0.15`` (n <= 500) or ``0.11`` (n > 500)
  means the phi = 0 rows apply; ``acf(1)`` at least the case value (0.30 H2b(i), H2b(ii), H2c;
  0.19 H2a(i), H2e; 0.16 H3c, H2d; 0.09 H2a(ii)) means the phi = 0.3 rows are realistic and
  governs; in between the weight toward the phi = 0.3 rows is printed (the plan gives no coverage
  table, so a coverage is not interpolated here).
* **D2.** ``V*(b) = b * var(means of the n - b + 1 overlapping blocks of length b)`` (the exact
  moving-block variance, no bootstrap noise) and the ratios ``V*(10)/V*(5)``, ``V*(20)/V*(5)``;
  the A5 rule (above 1.1 or above 1.15 on a primary series) with its predicted trigger rate under
  no dependence printed beside it (0.21, 0.164, 0.094 at n = 300, 500, 1000, and the
  at-least-one-of-k rate); the acf-implied block-5 factor beta_5 with its delta-method SE ("design
  question" when ``beta_5 + 2 SE < 0.8685``, used only when ``acf(2..10)`` is within ``2.5/sqrt(n)``
  of ``acf(1)**k``); and the pooled per-system mean of ``log V*(10)/V*(5)`` against a permutation
  null (one permutation of the test states per draw, applied to all the system's primary series;
  trigger at the 0.99 quantile). Any of the three readings firing is flagged to the owner as
  "block length 5 is a design question"; which reading governs is the owner's (OF-3).
* **D3.** The log-SD of the per-state evaluation MSE at H_ref of A1, A2, A3, A4 and A5 (reading:
  above 1.5 means the C2h/C4h rows apply), at the run's own number of evaluation draws E, with the
  projection to E = 4 (``sigma^2 - psi'(E/2) + psi'(2)``, Gaussian hybrid error) and the log-SD of
  the draw-free state part ``V_i(w)`` from the oracle moments.
* **D4.** Split-half reliability of the unclipped optimum ``u = (E_P - C)/c`` of draws 1-100 and
  101-200: the delta-method attenuation ``A`` of H2a(ii) interior (on delta-valid states, with
  the excluded count) with the Spearman-Brown value beside it (both "overstate reliability"),
  the indicator reliability of the zero part, and Spearman(v, Lambda_tilde | Q).
* **D5.** The finite-M bias of the H2a(i) median range: ``Delta_sh = (med r_A + med r_B)/2 -
  med r_200`` over all eligible test states, ``B(200) = Delta_sh/(sqrt 2 - 1)`` (order 1/2; order
  1 printed), its SE by the production moving-block bootstrap (blocks of 5), the reading against
  ``0.1 hw_full`` ("below 10%" iff ``|B| + 2 SE < 0.1 hw_full``; "not below 10%" iff
  ``|B| - 2 SE >= 0.1 hw_full``; else "not determined", treated as "not below 10%" for budget
  row 1, PF-5), the A5 point reading, and the V4 three-level check (observed order, ``2 m(200)``,
  signed mean deviation at H_ref).
* **D6.** The same split-half Richardson on the mean paired change of the two library cells of
  H2b(ii), and ``f_b``, the share of states whose unclipped optimum lies within 2 s of a clip
  bound (``s = |u_A - u_B|/2``), pooled by weight bin.

A missing array, a schema other than ``lpcstudy.states/1``, or a series that cannot be formed
prints ``not computable: <what>: <why>`` and is never skipped or replaced. Criteria whose arrays are
not part of the schema (H1a, H1c, H1d) are listed once as "outside the schema". Where the results
file carries the statistic that a series is the influence of, the tool recomputes the statistic from
the dump and prints MATCH or MISMATCH (a mismatch is a defect of the dump or of this tool).

The bootstrap and permutation generators are ``make_rng(--seed, system, label)``; the default seed
is a literal scratch seed (``TOOL_SEED``), not a development or confirmatory seed, so a report is
reproducible. The run's own seed is never read.

Exit codes: 0 everything computed and no mismatch; 1 at least one MISMATCH; 2 unreadable input,
a usage error, a refused seed id, or at least one "not computable" (the report is still printed in
full; 1 takes precedence over 2).
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from scipy import special
from scipy import stats as sps

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lpcstudy.config import PRESETS  # noqa: E402  (after the path line; no jax import)
from lpcstudy.statistics import block_resample_indices  # noqa: E402

EXIT_MISMATCH = 1
EXIT_INCOMPLETE = 2
SCHEMA = "lpcstudy.states/1"
TOOL_SEED = 20261018
"""Default seed of the tool's own bootstrap and permutations (a literal scratch seed)."""
LAGS = 10
BLOCKS = (5, 10, 20)
ACF_SMALL, ACF_LARGE = 0.15, 0.11
"""``|acf(1)|`` thresholds for n <= 500 and n > 500 (M4: 3.4 SE at n = 500 and at n = 1000)."""
CASE_VALUE = {"H2b(i)": 0.30, "H2b(ii)": 0.30, "H2c": 0.30, "H2a(i)": 0.19, "H2e": 0.19,
              "H3c": 0.16, "H2d": 0.16, "H2a(ii)": 0.09}
"""Lag-1 of the influence series at a latent phi = 0.3, by criterion (M4.2, WU-0006 M2)."""
RATIO_RULE = (1.1, 1.15)
BETA_STRESS = 0.8685
"""beta_5(0.3): the stress case already in the budget."""
UNION_NULL = {300: 0.210, 500: 0.164, 1000: 0.094}
"""P(V*(10)/V*(5) > 1.1 or V*(20)/V*(5) > 1.15) per series, no dependence (``m5_d5split.log``)."""
UNION_STRESS = {300: 0.401, 500: 0.425, 1000: 0.400}
"""The same at phi = 0.3 (power)."""
LOGSD_RULE = 1.5
PRIMARY_LEVEL_FACTOR = 1.014
"""E hw(B = 2000)/E hw(B = 500) at 1 - 0.05/3 (M3, ``m3_bfactor.log``)."""
RICHARDSON = 1.0 / (math.sqrt(2.0) - 1.0)
"""1/(2^(1/2) - 1) = 2.4142: the order-1/2 Richardson factor from M = 100 to M = 200."""
WEIGHT_BINS = ((0.0, 0.0), (0.0, 0.1), (0.1, 0.9), (0.9, 1.0), (1.0, 1.0))
"""Bins of ``w`` for ``f_b``: exactly 0, (0, 0.1), [0.1, 0.9], (0.9, 1), exactly 1."""
H2B_LIBRARY = (1_000, 10_000)
H2E_LIBRARY = (1_000, 100_000)
QN_TARGETS = ("logit_w_interior", "w_zero_indicator", "log_horizon")
RULES_LOGSD = ("A1", "A2", "A3", "A4", "A5")
OUTSIDE_SCHEMA = ("H1a", "H1c", "H1d")


# --------------------------------------------------------------------------------------------
# errors and the report
# --------------------------------------------------------------------------------------------
class NotComputable(Exception):
    """A diagnostic cannot be formed from the data given (never replaced by a number)."""


class Missing(NotComputable):
    """An array or leaf that the diagnostic needs is not in the file."""


@dataclass
class Report:
    """Lines, the "not computable" and mismatch lists, and the numbers (for ``--json``)."""

    lines: list[str] = field(default_factory=list)
    incomplete: list[str] = field(default_factory=list)
    defects: list[str] = field(default_factory=list)
    data: dict = field(default_factory=dict)

    def say(self, text: str = "") -> None:
        """Add a line."""
        self.lines.append(text)

    def nc(self, where: str, why: str) -> None:
        """Record and print a diagnostic that cannot be computed."""
        line = f"not computable: {where}: {why}"
        self.incomplete.append(line)
        self.lines.append("  " + line)

    def defect(self, text: str) -> None:
        """Record and print a MISMATCH."""
        self.defects.append(text)
        self.lines.append("  MISMATCH: " + text)

    def exit_code(self) -> int:
        """1 on a mismatch, else 2 on anything not computable, else 0."""
        return EXIT_MISMATCH if self.defects else (EXIT_INCOMPLETE if self.incomplete else 0)


def attempt(rep: Report, where: str, fn: Callable, *args, **kwargs):
    """Call ``fn``; a ``NotComputable`` is recorded under ``where`` and ``None`` is returned."""
    try:
        return fn(*args, **kwargs)
    except NotComputable as exc:
        rep.nc(where, str(exc))
        return None


class Dump:
    """One system's ``states/<system>.npz`` (or a dict of the same keys, for tests)."""

    def __init__(self, arrays, source: str) -> None:
        self._arrays = arrays
        self.source = source

    @classmethod
    def load(cls, path: Path) -> Dump:
        """Open an archive (never with pickles)."""
        return cls(np.load(path, allow_pickle=False), str(path))

    def close(self) -> None:
        """Close the archive (a dict has nothing to close)."""
        if hasattr(self._arrays, "close"):
            self._arrays.close()

    def has(self, key: str) -> bool:
        """Whether the key is present."""
        return key in self._arrays

    def __getitem__(self, key: str) -> np.ndarray:
        if key not in self._arrays:
            raise Missing(f"array {key!r} is not in {self.source}")
        return np.asarray(self._arrays[key])

    def scalar(self, key: str):
        """A 0-d array as a Python scalar."""
        return self[key].item()


def dig(tree: dict, *path: str):
    """A leaf of the results tree; ``Missing`` if any key is absent or the leaf is None."""
    node = tree
    for key in path:
        if not isinstance(node, dict) or key not in node:
            raise Missing(f"results leaf {'/'.join(path)} is absent")
        node = node[key]
    if node is None:
        raise Missing(f"results leaf {'/'.join(path)} is null")
    return node


def fmt(x: float | None, digits: int = 4) -> str:
    """A number for a report line; None prints as ``n/a``."""
    if x is None:
        return "n/a"
    return f"{x:.{digits}g}"


# --------------------------------------------------------------------------------------------
# numerics: autocorrelation, block variances, beta_5, trigamma
# --------------------------------------------------------------------------------------------
def acf(values: np.ndarray, max_lag: int = LAGS) -> np.ndarray:
    """Sample autocorrelation at lags 1..``max_lag`` (centred, divided by the lag-0 sum).

    Raises
    ------
    NotComputable
        If the series is constant or has at most ``max_lag`` entries.
    """
    x = np.asarray(values, dtype=float)
    if x.size <= max_lag:
        raise NotComputable(f"series of {x.size} entries is not longer than {max_lag} lags")
    if not np.all(np.isfinite(x)):
        raise NotComputable("non-finite entry in the series")
    xc = x - x.mean()
    denom = float(xc @ xc)
    if denom == 0.0:
        raise NotComputable("constant series (zero variance)")
    return np.array([float(xc[:-k] @ xc[k:]) for k in range(1, max_lag + 1)]) / denom


def block_variance(values: np.ndarray, block: int) -> float:
    """``V*(b) = b * var`` (ddof 0) of the ``n - b + 1`` overlapping block means.

    This is the exact moving-block bootstrap variance of the mean (no resampling noise); the
    ratios of it across ``b`` are what D2 reads.
    """
    x = np.asarray(values, dtype=float)
    if block < 1 or block > x.size:
        raise NotComputable(f"block length {block} does not fit a series of {x.size}")
    windows = np.lib.stride_tricks.sliding_window_view(x - x.mean(), block)
    return float(block * windows.mean(axis=1).var())


def block_variances(matrix: np.ndarray, block: int) -> np.ndarray:
    """``V*(b)`` of every row of a matrix (the permutation null), by cumulative sums."""
    x = np.asarray(matrix, dtype=float)
    x = x - x.mean(axis=1, keepdims=True)
    cum = np.concatenate([np.zeros((x.shape[0], 1)), np.cumsum(x, axis=1)], axis=1)
    return block * ((cum[:, block:] - cum[:, :-block]) / block).var(axis=1)


def beta_five(phi: float) -> float:
    """Block-5 variance factor ``[1 + 2 sum_{k<5} (1 - k/5) phi^k] (1 - phi)/(1 + phi)`` (AR(1))."""
    poly = 1.0 + 2.0 * sum((1.0 - k / 5.0) * phi**k for k in range(1, 5))
    return poly * (1.0 - phi) / (1.0 + phi)


def beta_five_slope(phi: float) -> float:
    """Derivative of ``beta_five`` in phi (analytic)."""
    poly = 1.0 + 2.0 * sum((1.0 - k / 5.0) * phi**k for k in range(1, 5))
    dpoly = 2.0 * sum(k * (1.0 - k / 5.0) * phi ** (k - 1) for k in range(1, 5))
    return dpoly * (1.0 - phi) / (1.0 + phi) - 2.0 * poly / (1.0 + phi) ** 2


def trigamma(z: float) -> float:
    """``psi'(z)`` (scipy's polygamma of order 1)."""
    return float(special.polygamma(1, z))


# --------------------------------------------------------------------------------------------
# influence series (M4.1); each is the influence at z_i, 0 outside the domain
# --------------------------------------------------------------------------------------------
def _domain(values: np.ndarray, domain: np.ndarray | None) -> tuple[np.ndarray, np.ndarray]:
    v = np.asarray(values, dtype=float)
    dom = np.ones(v.shape, bool) if domain is None else np.asarray(domain, dtype=bool)
    if dom.shape != v.shape:
        raise ValueError(f"domain shape {dom.shape} differs from values {v.shape}")
    if not dom.any():
        raise NotComputable("empty domain")
    if not np.all(np.isfinite(v[dom])):
        raise NotComputable("non-finite value inside the domain")
    return v, dom


def psi_sign(values: np.ndarray, domain: np.ndarray | None = None) -> np.ndarray:
    """Rank score of a median: ``1{v < m} + 1/2 1{v = m} - 1/2`` in the domain, 0 outside.

    ``m`` is the median of the domain values (the mid-rank rule handles ties and the atom at 0).
    It is minus the influence of the median times the density at ``m``; the acf and the variance
    ratios do not depend on that factor or its sign. Sums to 0.
    """
    v, dom = _domain(values, domain)
    m = float(np.median(v[dom]))
    out = np.zeros(v.shape)
    d = v[dom]
    out[dom] = (d < m).astype(float) + 0.5 * (d == m) - 0.5
    return out


def psi_mean(values: np.ndarray, domain: np.ndarray | None = None) -> np.ndarray:
    """Influence of a mean: ``v_i - mean`` in the domain, 0 outside."""
    v, dom = _domain(values, domain)
    out = np.zeros(v.shape)
    out[dom] = v[dom] - v[dom].mean()
    return out


def psi_ratio(numerator: np.ndarray, denominator: np.ndarray,
              domain: np.ndarray | None = None) -> np.ndarray:
    """Influence of ``mean(a)/mean(b)``: ``(a_i - R b_i)/mean(b)`` (H3c, H2d)."""
    a, dom = _domain(numerator, domain)
    b, _ = _domain(denominator, dom)
    mean_b = float(b[dom].mean())
    if mean_b == 0.0:
        raise NotComputable("mean of the denominator is 0")
    ratio = float(a[dom].mean()) / mean_b
    out = np.zeros(a.shape)
    out[dom] = (a[dom] - ratio * b[dom]) / mean_b
    return out


def residuals(values: np.ndarray, controls: np.ndarray) -> np.ndarray:
    """Least-squares residuals of ``values`` on ``[1, controls]``."""
    design = np.column_stack([np.ones(len(values)), controls])
    return values - design @ np.linalg.lstsq(design, values, rcond=None)[0]


def psi_partial_corr(target: np.ndarray, variable: np.ndarray, controls: np.ndarray,
                     domain: np.ndarray | None = None) -> tuple[np.ndarray, float]:
    """Influence of the partial correlation given ``[1, controls]`` (H2a(ii)), and its value.

    ``psi_i = e_y e_x/(s_y s_x) - (r/2)(e_y^2/s_y^2 + e_x^2/s_x^2)`` with the residuals ``e`` of
    ``y`` and ``x`` on ``[1, Q]`` and their second moments ``s^2`` over the domain, 0 outside it.
    """
    y, dom = _domain(target, domain)
    x, _ = _domain(variable, dom)
    q = np.asarray(controls, dtype=float)
    rows = int(dom.sum())
    if rows <= q.shape[1] + 2:
        raise NotComputable(f"{rows} states in the domain are too few for {q.shape[1]} controls")
    ey, ex = residuals(y[dom], q[dom]), residuals(x[dom], q[dom])
    sy, sx = math.sqrt(float(np.mean(ey**2))), math.sqrt(float(np.mean(ex**2)))
    if sy == 0.0 or sx == 0.0 or np.ptp(y[dom]) == 0.0 or np.ptp(x[dom]) == 0.0:
        raise NotComputable("a constant target or variable (partial correlation undefined)")
    r = float(np.mean(ey * ex)) / (sy * sx)
    out = np.zeros(y.shape)
    out[dom] = ey * ex / (sy * sx) - 0.5 * r * (ey**2 / sy**2 + ex**2 / sx**2)
    return out, r


def psi_slope(x: np.ndarray, y: np.ndarray, domain: np.ndarray | None = None) -> np.ndarray:
    """Influence of the OLS slope: ``(x_i - xbar)(y_i - a - b x_i)/S_xx`` (``S_xx`` a mean)."""
    xv, dom = _domain(x, domain)
    yv, _ = _domain(y, dom)
    xc = xv[dom] - xv[dom].mean()
    s_xx = float(np.mean(xc**2))
    if s_xx == 0.0:
        raise NotComputable("constant regressor")
    beta = float(np.mean(xc * (yv[dom] - yv[dom].mean()))) / s_xx
    out = np.zeros(xv.shape)
    out[dom] = xc * ((yv[dom] - yv[dom].mean()) - beta * xc) / s_xx
    return out


def psi_delta_r2(y: np.ndarray, pred_three: np.ndarray, pred_four: np.ndarray,
                 domain: np.ndarray | None = None) -> tuple[np.ndarray, float]:
    """Influence of ``R^2(F4) - R^2(F3)`` with the models held fixed, and its value (Q-N).

    ``psi_i = [(y - f3)^2 - (y - f4)^2 - Delta (y - ybar)^2]/mean (y - ybar)^2`` in the domain.
    """
    yv, dom = _domain(y, domain)
    f3, _ = _domain(pred_three, dom)
    f4, _ = _domain(pred_four, dom)
    d = (yv[dom] - yv[dom].mean()) ** 2
    total = float(d.mean())
    if total == 0.0:
        raise NotComputable("constant target (R^2 undefined)")
    gain = (yv[dom] - f3[dom]) ** 2 - (yv[dom] - f4[dom]) ** 2
    delta = float(gain.mean()) / total
    out = np.zeros(yv.shape)
    out[dom] = (gain - delta * d) / total
    return out, delta


def per_state_spearman(levels: np.ndarray, values: np.ndarray) -> tuple[np.ndarray, int]:
    """Spearman of each row of ``values`` with ``levels`` (average ranks), constant rows score 0.

    Returns the correlations and the number of rows scored 0 by that convention (H2b(i)).
    """
    ranks = sps.rankdata(values, axis=1)
    lev = sps.rankdata(levels)
    lev_c = lev - lev.mean()
    ranks_c = ranks - ranks.mean(axis=1, keepdims=True)
    denom = np.sqrt(np.sum(ranks_c**2, axis=1) * np.sum(lev_c**2))
    good = denom > 0
    out = np.where(good, ranks_c @ lev_c / np.where(good, denom, 1.0), 0.0)
    return out, int((~good).sum())


def leading_ranges(weights: np.ndarray, small: np.ndarray
                   ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """H2a(i): range of ``w`` over the leading small-error horizons; eligible iff at least two.

    Returns ``(range with NaN for ineligible states, eligible mask, leading mask)``.
    """
    leading = np.cumprod(np.asarray(small, dtype=bool), axis=1).astype(bool)
    length = leading.sum(axis=1)
    eligible = length >= 2
    high = np.where(leading, weights, -np.inf).max(axis=1)
    low = np.where(leading, weights, np.inf).min(axis=1)
    return np.where(eligible, high - low, np.nan), eligible, leading


def segment_ranges(weights: np.ndarray, leading: np.ndarray) -> np.ndarray:
    """Range of ``w`` over a fixed set of leading horizons (the 200-draw segments), NaN if empty."""
    high = np.where(leading, weights, -np.inf).max(axis=1)
    low = np.where(leading, weights, np.inf).min(axis=1)
    return np.where(leading.any(axis=1), high - low, np.nan)


def quadratic_controls(seeds: np.ndarray) -> np.ndarray:
    """``[x1, x2, x1^2, x2^2, x1 x2]`` of the log seed ratios, centred on the sample mean."""
    x = np.asarray(seeds, dtype=float)
    x = x - x.mean(axis=0)
    return np.column_stack([x[:, 0], x[:, 1], x[:, 0] ** 2, x[:, 1] ** 2, x[:, 0] * x[:, 1]])


def weight_from_moments(e_c: np.ndarray, e_p: np.ndarray, cross: np.ndarray) -> np.ndarray:
    """The clipped oracle weight ``(E_P - C)/max(E_C + E_P - 2C, 1e-300)`` (as the package)."""
    curv = e_c + e_p - 2.0 * cross
    return np.clip((e_p - cross) / np.maximum(curv, 1e-300), 0.0, 1.0)


def unclipped_optimum(e_c: np.ndarray, e_p: np.ndarray, cross: np.ndarray
                      ) -> tuple[np.ndarray, np.ndarray]:
    """``u = (E_P - C)/c`` with ``c = E_C + E_P - 2C``; NaN where ``c <= 0`` (counted by callers)."""
    curv = e_c + e_p - 2.0 * cross
    good = curv > 0
    return np.where(good, (e_p - cross) / np.where(good, curv, 1.0), np.nan), curv


# --------------------------------------------------------------------------------------------
# D1 and D2 readings
# --------------------------------------------------------------------------------------------
def acf_threshold(n: int) -> float:
    """0.15 for n <= 500, 0.11 above (M4: the same 3.4 SE)."""
    return ACF_SMALL if n <= 500 else ACF_LARGE


def acf_reading(criterion: str, lag1: float, n: int) -> tuple[str, float | None]:
    """The C9 reading of ``acf(1)`` and, between the readings, the weight toward phi = 0.3.

    Returns ``(text, weight)``; ``weight`` is None unless the lag-1 lies strictly between the
    threshold and the case value.
    """
    thr = acf_threshold(n)
    case = CASE_VALUE.get(criterion)
    if case is not None and lag1 >= case:
        both = " (both readings hold; the phi = 0.3 reading governs)" if abs(lag1) <= thr else ""
        return f"phi = 0.3 rows realistic (acf1 >= {case:g}){both}", None
    if abs(lag1) <= thr:
        extra = "" if case is not None else " (no case value for the phi = 0.3 reading)"
        return f"phi = 0 rows apply (|acf1| <= {thr:g}){extra}", None
    if lag1 > thr:
        if case is None:
            return f"acf1 above {thr:g}; no case value defined", None
        weight = (lag1 - thr) / (case - thr)
        return f"between the readings (weight {weight:.2f} toward the phi = 0.3 rows)", weight
    return f"acf1 below -{thr:g}: neither reading applies (negative dependence, reported)", None


def lag_zero_false_trigger(n: int) -> float:
    """Predicted P(|acf1| > threshold) under no dependence: ``2 (1 - Phi(thr sqrt(n)))``."""
    return math.erfc(acf_threshold(n) * math.sqrt(n) / math.sqrt(2.0))


@dataclass
class Series:
    """One influence series: ``values`` over the states of its split, in time order."""

    system: str
    criterion: str
    part: str
    values: np.ndarray
    primary: bool
    domain: int
    """States inside the criterion's domain (the series is 0 outside it)."""

    @property
    def name(self) -> str:
        """Criterion and part."""
        return f"{self.criterion} {self.part}".strip()

    @property
    def n(self) -> int:
        """Series length (states of the split)."""
        return int(self.values.size)


def variance_summary(values: np.ndarray) -> dict:
    """V*(5), V*(10), V*(20), the two ratios and the A5 trigger of one series."""
    v5, v10, v20 = (block_variance(values, b) for b in BLOCKS)
    if not (v5 > 0.0 and math.isfinite(v5)):
        raise NotComputable("V*(5) is not positive")
    r10, r20 = v10 / v5, v20 / v5
    return {"V5": v5, "V10": v10, "V20": v20, "ratio10": r10, "ratio20": r20,
            "fires": bool(r10 > RATIO_RULE[0] or r20 > RATIO_RULE[1])}


def beta_reading(lags: np.ndarray, n: int) -> dict:
    """The acf-implied block-5 factor and whether it says "design question".

    The reading is used only if ``acf(2..10)`` lies within ``2.5/sqrt(n)`` of ``acf(1)**k``;
    otherwise ``used`` is False and ``fires`` is False (the premise fails, reported).
    """
    phi = float(lags[0])
    beta = beta_five(phi)
    se = abs(beta_five_slope(phi)) * math.sqrt((1.0 - phi * phi) / n)
    expected = phi ** np.arange(2, LAGS + 1)
    gap = float(np.max(np.abs(lags[1:] - expected)))
    used = gap <= 2.5 / math.sqrt(n)
    return {"phi": phi, "beta5": beta, "se": se, "gap": gap, "used": used,
            "fires": bool(used and beta + 2.0 * se < BETA_STRESS)}


def permutation_null(series: Sequence[np.ndarray], n_perm: int, rng: np.random.Generator
                     ) -> tuple[float, np.ndarray]:
    """Pooled ``mean log V*(10)/V*(5)`` of a system's primary series and its permutation null.

    Each series is over the first ``n_i`` test states. A permutation draws one random key per
    state; the order of the first ``n_i`` states under it is applied to series ``i``, so every
    series of the system is permuted by the same permutation (the cross-series dependence and the
    tails are kept, the serial dependence is removed).

    Returns
    -------
    tuple[float, np.ndarray]
        The observed pooled statistic and the ``n_perm`` null values.

    Raises
    ------
    NotComputable
        If no series is given or a block variance is not positive.
    """
    if not series:
        raise NotComputable("no primary series")
    n_max = max(len(s) for s in series)
    keys = rng.random((n_perm, n_max))
    obs, null = [], np.zeros(n_perm)
    for s in series:
        x = np.asarray(s, dtype=float)
        v5, v10 = block_variance(x, 5), block_variance(x, 10)
        if not (v5 > 0 and v10 > 0):
            raise NotComputable("a block variance is not positive")
        obs.append(math.log(v10 / v5))
        order = np.argsort(keys[:, :len(x)], axis=1)
        perm = x[order]
        p5, p10 = block_variances(perm, 5), block_variances(perm, 10)
        if not (np.all(p5 > 0) and np.all(p10 > 0)):
            raise NotComputable("a permuted block variance is not positive")
        null += np.log(p10 / p5)
    return float(np.mean(obs)), null / len(series)


# --------------------------------------------------------------------------------------------
# D3 to D6: the numerics
# --------------------------------------------------------------------------------------------
def log_sd(values: np.ndarray) -> tuple[float, int]:
    """SD (ddof 1) of ``log`` of the positive entries, and the number of non-positive ones."""
    v = np.asarray(values, dtype=float)
    pos = v > 0
    if pos.sum() < 2:
        raise NotComputable("fewer than two positive per-state values")
    return float(np.std(np.log(v[pos]), ddof=1)), int((~pos).sum())


def logsd_at_draws(sigma: float, n_draws: int, target: int = 4) -> float | None:
    """Projection of a log-SD from ``n_draws`` to ``target`` evaluation draws, or None.

    ``sigma'^2 = sigma^2 - psi'(E/2) + psi'(target/2)`` (a Gaussian hybrid error has
    ``a_i = V_i chi^2_E / E``, whose log has the extra variance ``psi'(E/2)``). None if the
    result is not positive (the projection is not defined).
    """
    value = sigma**2 - trigamma(n_draws / 2.0) + trigamma(target / 2.0)
    return math.sqrt(value) if value > 0 else None


def hybrid_state_mse(weight: np.ndarray | float, e_c: np.ndarray, e_p: np.ndarray,
                     cross: np.ndarray) -> np.ndarray:
    """The draw-free per-state MSE ``w^2 E_C + (1 - w)^2 E_P + 2 w (1 - w) C`` (mean over draws)."""
    w = np.asarray(weight, dtype=float)
    if w.ndim == 2:
        e_c, e_p, cross = e_c[:, None], e_p[:, None], cross[:, None]
    value = w**2 * e_c + (1.0 - w) ** 2 * e_p + 2.0 * w * (1.0 - w) * cross
    return value.mean(axis=1) if w.ndim == 2 else value


def split_half_shift(stat_a: float, stat_b: float, stat_full: float) -> float:
    """``Delta_sh = (s_A + s_B)/2 - s_200``: the level-100 minus level-200 shift of a statistic."""
    return 0.5 * (stat_a + stat_b) - stat_full


def three_way_reading(bias: float, se: float, limit: float) -> str:
    """"below 10%", "not below 10%" or "not determined" (limit is ``0.1 hw_full``)."""
    if abs(bias) + 2.0 * se < limit:
        return "below 10%"
    if abs(bias) - 2.0 * se >= limit:
        return "not below 10%"
    return "not determined"


def v4_order(m_small: float, m_mid: float, ratio: float = 4.0) -> tuple[float | None, str]:
    """Observed order ``p = log_r[(m(M1) - m(M2))/m(M2)]`` of the V4 median shifts.

    ``m(M) = med r_M - med r_Mmax`` with ``M2/M1 = Mmax/M2 = r``. Returns ``(p, note)``; ``p`` is
    None ("order not determined") if either shift is not positive or p is outside [0.3, 1.5].
    """
    if not (m_mid > 0.0 and m_small - m_mid > 0.0):
        return None, "order not determined (a shift is not positive)"
    p = math.log((m_small - m_mid) / m_mid) / math.log(ratio)
    if not 0.3 <= p <= 1.5:
        return None, f"order not determined (observed {p:.3g} outside [0.3, 1.5])"
    return p, "order determined"


def near_clip(u_full: np.ndarray, half_sd: np.ndarray, factor: float = 2.0) -> np.ndarray:
    """States whose unclipped optimum is within ``factor * s`` of a clip bound (0 or 1)."""
    return (u_full - factor * half_sd <= 0.0) | (u_full + factor * half_sd >= 1.0)


def logit(w: np.ndarray) -> np.ndarray:
    """``log(w/(1 - w))`` (callers pass interior weights)."""
    return np.log(w / (1.0 - w))


def interior_attenuation(u_a: np.ndarray, u_b: np.ndarray, w_full: np.ndarray,
                         controls: np.ndarray, lam: np.ndarray, width: float = 3.0) -> dict:
    """D4, H2a(ii) interior: delta-method attenuation ``A`` from the split halves of ``u``.

    ``v_i = ((u_A - u_B)/2)^2/[w_i (1 - w_i)]^2`` on the interior states (``0 < w_i < 1`` with
    ``w_i`` the 200-draw weight), restricted to the delta-valid ones (``w_i +- width s_i`` inside
    (0, 1), ``s_i = |u_A - u_B|/2``). ``A = sqrt(1 - mean(v)/var(y~))`` with ``y~`` the
    Q-residualized logit ``w`` (residualized on the interior domain; the variance over the
    delta-valid states, the stricter of the two denominators; the all-interior value is returned
    as ``A_all``). The Spearman-Brown reliability uses the states where ``u_A`` and ``u_B`` are
    both in (0, 1). The excluded near-clip states are the noisiest, so both values overstate the
    reliability. Also the partial Spearman of ``v`` with ``lam`` given ``[1, Q]``.
    """
    finite = np.isfinite(u_a) & np.isfinite(u_b)
    interior = (w_full > 0.0) & (w_full < 1.0)
    dom = interior & finite
    n_interior, n_dom = int(interior.sum()), int(dom.sum())
    if n_dom < controls.shape[1] + 3:
        raise NotComputable(f"{n_dom} interior states with defined halves are too few")
    w = w_full[dom]
    s = np.abs(u_a[dom] - u_b[dom]) / 2.0
    q = controls[dom]
    y_res = residuals(logit(w), q)
    v = s**2 / (w * (1.0 - w)) ** 2
    valid = (w - width * s > 0.0) & (w + width * s < 1.0)
    n_valid = int(valid.sum())
    if n_valid < 2:
        raise NotComputable("fewer than two delta-valid states")
    var_valid, var_all = float(np.var(y_res[valid])), float(np.var(y_res))
    mean_v = float(v[valid].mean())

    def attenuation(var: float) -> dict:
        rel = 1.0 - mean_v / var if var > 0 else float("nan")
        return {"reliability": rel, "A": math.sqrt(rel) if rel > 0 else None}

    both = (u_a[dom] > 0) & (u_a[dom] < 1) & (u_b[dom] > 0) & (u_b[dom] < 1)
    sb: dict = {"n_states": int(both.sum()), "r_ab": None, "reliability": None, "A": None}
    if both.sum() >= controls.shape[1] + 3:
        ra = residuals(logit(u_a[dom][both]), q[both])
        rb = residuals(logit(u_b[dom][both]), q[both])
        if np.ptp(ra) > 0 and np.ptp(rb) > 0:
            r_ab = float(np.corrcoef(ra, rb)[0, 1])
            rel = 2.0 * r_ab / (1.0 + r_ab) if r_ab != -1.0 else float("nan")
            sb.update(r_ab=r_ab, reliability=rel, A=math.sqrt(rel) if rel > 0 else None)
    rank_v = residuals(sps.rankdata(v), q)
    rank_l = residuals(sps.rankdata(lam[dom]), q)
    spear = (float(np.corrcoef(rank_v, rank_l)[0, 1])
             if np.ptp(rank_v) > 0 and np.ptp(rank_l) > 0 else None)
    main = attenuation(var_valid)
    return {"n_interior": n_interior, "n_domain": n_dom, "n_valid": n_valid,
            "n_excluded_delta": n_dom - n_valid, "n_undefined_halves": n_interior - n_dom,
            "mean_v": mean_v, "var_valid": var_valid, "var_all": var_all, **main,
            "A_all": attenuation(var_all)["A"], "bias_at_edge": (
                None if main["A"] is None else 0.1 * (1.0 - main["A"])),
            "spearman_brown": sb, "spearman_v_lambda_given_Q": spear}


def zero_reliability(w_a: np.ndarray, w_b: np.ndarray, w_full: np.ndarray) -> dict:
    """D4, H2a(ii) zero: indicator reliability from the split-half covariance.

    ``r_100 = Cov(1{w_A = 0}, 1{w_B = 0}) / Var(1{w_200 = 0})`` (population moments, all states),
    Spearman-Brown to 200 draws ``2 r/(1 + r)``, attenuation ``sqrt`` of it. The Pearson
    correlation of the two half indicators and its Spearman-Brown value are printed beside it.
    """
    ia, ib, ic = ((w == 0.0).astype(float) for w in (w_a, w_b, w_full))
    p = float(ic.mean())
    if p == 0.0 or p == 1.0:
        raise NotComputable("the 200-draw zero indicator is constant")
    cov = float(np.mean(ia * ib) - ia.mean() * ib.mean())
    r = cov / (p * (1.0 - p))
    out: dict = {"n_states": int(len(ic)), "share_zero": p, "cov": cov, "r100": r,
                 "reliability": None, "A": None, "pearson_r": None, "pearson_reliability": None}
    if r != -1.0:
        rel = 2.0 * r / (1.0 + r)
        out.update(reliability=rel, A=math.sqrt(rel) if rel > 0 else None)
    if np.ptp(ia) > 0 and np.ptp(ib) > 0:
        pr = float(np.corrcoef(ia, ib)[0, 1])
        out["pearson_r"] = pr
        if pr != -1.0:
            out["pearson_reliability"] = 2.0 * pr / (1.0 + pr)
    return out


def full_halfwidth(hw: float, cfg: dict, size_key: str) -> tuple[float, str]:
    """Half-width at the full preset: observed on a full run, else the R1 projection (M3).

    The projection is ``hw sqrt(n_run/n_full)`` times 1.014 when the run's B is 500 and the full
    preset's 2000 (the B factor of M3 at 1 - 0.05/3); with another B the factor is 1 and the
    note says so.
    """
    full = PRESETS["full"]
    if cfg.get("name") == "full":
        return hw, "observed (full preset)"
    n_run, n_full = cfg[size_key], getattr(full, size_key)
    factor = math.sqrt(n_run / n_full)
    note = f"projected from {size_key} {n_run} to {n_full}: x{factor:.3f}"
    if cfg.get("bootstrap_resamples") == 500 and full.bootstrap_resamples == 2000:
        factor *= PRIMARY_LEVEL_FACTOR
        note += f" x{PRIMARY_LEVEL_FACTOR} (B 500 to 2000)"
    else:
        note += " (B factor 1: the run's B is not 500)"
    return hw * factor, note


def bootstrap_se(statistic: Callable[[np.ndarray], float], n: int, n_boot: int, block: int,
                 rng: np.random.Generator) -> tuple[float, int]:
    """SE (ddof 1) of a statistic over production moving-block resamples, and the failed count.

    A resample on which the statistic is not finite is counted (``n_failed``), never dropped
    silently.
    """
    values = np.array([statistic(idx) for idx in block_resample_indices(n, n_boot, block, rng)])
    ok = np.isfinite(values)
    if ok.sum() < 2:
        raise NotComputable("fewer than two finite bootstrap values")
    return float(np.std(values[ok], ddof=1)), int((~ok).sum())


# --------------------------------------------------------------------------------------------
# series of the criteria (M4.1)
# --------------------------------------------------------------------------------------------
@dataclass
class Context:
    """Everything a diagnostic of one system reads."""

    system: str
    dump: Dump
    res: dict
    cfg: dict
    rep: Report
    seed: int
    resamples: int
    permutations: int

    @property
    def lt(self) -> int:
        """Steps per Lyapunov time."""
        return int(self.dump.scalar("meta/steps_per_lyapunov"))

    @property
    def ref(self) -> int:
        """Column of H_ref in the core arrays."""
        return int(self.dump.scalar("core/ref_index"))

    def rng(self, label: str) -> np.random.Generator:
        """``make_rng(seed, system, label)`` (imported on use: the package module needs jax)."""
        from lpcstudy.data import make_rng
        return make_rng(self.seed, self.system, label)

    def group(self, rho: float, n_lib: int) -> str:
        """The sweep group prefix of a cell."""
        return f"sweep/rho={rho:g}|n_lib={n_lib}"


def check(ctx: Context, label: str, mine: float, path: tuple[str, ...], tol: float,
          offset: float = 0.0) -> None:
    """Compare a recomputed statistic with the results leaf; a MISMATCH is a defect.

    ``|mine - leaf| <= tol |leaf|`` (relative, no floor; an exact 0 needs equality). ``offset`` is
    added to ``mine`` first (H2d is a ratio minus 1).
    """
    try:
        leaf = float(dig(ctx.res, *path))
    except Missing as exc:
        ctx.rep.nc(f"{ctx.system} {label}: reproduction check", str(exc))
        return
    value = mine + offset
    diff = abs(value - leaf)
    ok = diff <= tol * abs(leaf)
    ctx.rep.say(f"  check {label}: dump {value:.12g} vs results {leaf:.12g} "
                f"(|diff| {diff:.2e}, tol {tol:g} relative): {'MATCH' if ok else 'MISMATCH'}")
    if not ok:
        ctx.rep.defects.append(f"{ctx.system} {label}: dump {value!r} vs results {leaf!r}")


def h2a_inputs(ctx: Context) -> dict:
    """The H2a(i) inputs from the dump: weights at the long horizons and the small-error flags."""
    d, lt = ctx.dump, ctx.lt
    horizons = d["core/horizons"]
    cols = np.flatnonzero(horizons >= lt)
    if cols.size < 2:
        raise NotComputable("fewer than two horizons of at least 1 Lyapunov time")
    rms = float(dig(ctx.cfg, "linear_regime_rms"))
    small = (np.sqrt(d["core/E_C"][:, cols]) <= rms) & (np.sqrt(d["core/E_P"][:, cols]) <= rms)
    return {"cols": cols, "horizons": horizons[cols], "small": small,
            "w": d["core/w_star"][:, cols], "w_a": d["core/w_star_A"][:, cols],
            "w_b": d["core/w_star_B"][:, cols]}


def series_h2a_i(ctx: Context) -> list[Series]:
    inp = h2a_inputs(ctx)
    ranges, eligible, _ = leading_ranges(inp["w"], inp["small"])
    psi = psi_sign(ranges, eligible)
    check(ctx, "H2a(i) median range", float(np.median(ranges[eligible])),
          ("H2a", "median_range"), 0.0)
    return [Series(ctx.system, "H2a(i)", "", psi, True, int(eligible.sum()))]


def series_h2a_ii(ctx: Context) -> list[Series]:
    d = ctx.dump
    w_ref = d["core/w_star"][:, ctx.ref]
    lam = d["core/Lambda_bar"] * ctx.lt
    rho = float(dig(ctx.cfg, "core_noise"))
    controls = quadratic_controls(np.column_stack([np.log(d["core/eps_s"] / rho),
                                                   np.log(d["core/delta"] / rho)]))
    n = len(w_ref)
    zero, one = w_ref == 0.0, w_ref == 1.0
    interior = ~zero & ~one
    parts: dict[str, tuple[np.ndarray, np.ndarray]] = {
        "zero": (zero.astype(float), np.ones(n, bool)),
        "interior": (np.log(np.where(interior, w_ref, 0.5) / (1.0 - np.where(interior, w_ref, 0.5))),
                     interior)}
    if 20 * int(one.sum()) > n:  # strictly more than 5% of the states: the production rule
        parts["one"] = (one.astype(float), np.ones(n, bool))
    out = []
    for name, (target, dom) in parts.items():
        try:
            psi, r = psi_partial_corr(target, lam, controls, dom)
        except NotComputable as exc:
            ctx.rep.nc(f"{ctx.system} H2a(ii) {name}", str(exc))
            continue
        check(ctx, f"H2a(ii) {name} partial correlation", r,
              ("H2a", "part_ii", name, "partial_corr"), 1e-9)
        out.append(Series(ctx.system, "H2a(ii)", name, psi, True, int(dom.sum())))
    return out


def series_h2b_i(ctx: Context) -> list[Series]:
    levels = np.array(sorted(float(r) for r in dig(ctx.cfg, "noise_levels")))
    library = int(dig(ctx.cfg, "core_library"))
    w = np.column_stack([ctx.dump[f"{ctx.group(r, library)}/w_star_href"] for r in levels])
    spear, n_constant = per_state_spearman(levels, w)
    check(ctx, "H2b(i) mean per-state Spearman", float(spear.mean()),
          ("H2b", "noise", "mean_state_spearman"), 1e-12)
    check(ctx, "H2b(i) constant states (scored 0 by the tie convention)", float(n_constant),
          ("H2b", "noise", "n_constant_states"), 0.0)
    return [Series(ctx.system, "H2b(i)", "", psi_mean(spear), True, len(spear))]


def series_h2b_ii(ctx: Context) -> list[Series]:
    rho = float(dig(ctx.cfg, "core_noise"))
    low, high = (ctx.dump[f"{ctx.group(rho, n)}/w_star_href"] for n in H2B_LIBRARY)
    diff = high - low
    check(ctx, "H2b(ii) mean paired change", float(diff.mean()),
          ("H2b", "library_change", "mean_change"), 1e-12)
    return [Series(ctx.system, "H2b(ii)", "", psi_mean(diff), True, len(diff))]


def series_h3c(ctx: Context) -> list[Series]:
    a5, a4 = (ctx.dump[f"core/state_mse/{r}"][:, ctx.ref] for r in ("A5", "A4"))
    check(ctx, "H3c A5/A4 ratio", float(a5.mean() / a4.mean()), ("H3c", "A5_over_A4_mse"), 1e-12)
    return [Series(ctx.system, "H3c", "", psi_ratio(a5, a4), True, len(a5))]


def series_h2c(ctx: Context) -> list[Series]:
    mse = {r: ctx.dump[f"core/state_mse/{r}"][:, ctx.ref] for r in ("A0", "A1", "A2", "A4")}
    others = ["A2"]
    try:
        others.append(str(dig(ctx.res, "H2c", "best_single")))
    except Missing as exc:
        ctx.rep.nc(f"{ctx.system} H2c A4-best", str(exc))
    out = []
    for other in others:
        if other not in mse:
            ctx.rep.nc(f"{ctx.system} H2c A4-{other}", f"rule {other} is not a dumped rule")
            continue
        diff = mse["A4"] - mse[other]
        check(ctx, f"H2c A4-{other} mean", float(diff.mean()),
              ("H2c", f"A4_minus_{other}", "mean"), 1e-12)
        out.append(Series(ctx.system, "H2c", f"A4-{other}", psi_mean(diff), False, len(diff)))
    return out


def series_h2d(ctx: Context) -> list[Series]:
    a4, a3 = (ctx.dump[f"core/state_mse/{r}"][:, ctx.ref] for r in ("A4", "A3"))
    check(ctx, "H2d A4/A3 - 1", float(a4.mean() / a3.mean()), ("H2d", "in_distribution_excess"),
          1e-12, offset=-1.0)
    return [Series(ctx.system, "H2d", "", psi_ratio(a4, a3), False, len(a4))]


def series_h2e(ctx: Context) -> list[Series]:
    out = []
    for rho in dig(ctx.cfg, "library_sweep_noises"):
        low, high = (ctx.dump[f"{ctx.group(float(rho), n)}/err_corr_href"] for n in H2E_LIBRARY)
        diff = high - low
        check(ctx, f"H2e rho={rho:g} median change", float(np.median(diff)),
              ("H2e", "by_noise", f"{float(rho):g}", "median_change"), 1e-12)
        out.append(Series(ctx.system, "H2e", f"rho={float(rho):g}", psi_sign(diff), False,
                          len(diff)))
    return out


def series_qn(ctx: Context) -> list[Series]:
    out = []
    for kind in ("oracle", "deployable"):
        for target in QN_TARGETS:
            base = f"qn/{kind}/{target}"
            try:
                y, p3, p4, dom = (ctx.dump[f"{base}/{k}"] for k in ("y", "pred3", "pred4", "domain"))
                psi, delta = psi_delta_r2(y, p3, p4, dom)
            except NotComputable as exc:
                ctx.rep.nc(f"{ctx.system} Q-N {kind} {target}", str(exc))
                continue
            check(ctx, f"Q-N {kind} {target} delta R^2", delta,
                  ("Q-N", kind, target, "delta_r2"), 1e-12)
            out.append(Series(ctx.system, "Q-N", f"{kind} {target}", psi, False, int(dom.sum())))
    return out


def series_h1b(ctx: Context) -> list[Series]:
    d = ctx.dump
    gain, seed_err, e_p = d["core/g_H_ref"], d["core/delta"], d["core/E_P"][:, ctx.ref]
    with np.errstate(divide="ignore", invalid="ignore"):
        x = np.log(gain * seed_err)
        y = 0.5 * np.log(np.maximum(e_p, 1e-12))
    keep = np.isfinite(x) & np.isfinite(y)
    psi = psi_slope(x, y, keep)
    xc = x[keep] - x[keep].mean()
    slope = float(np.sum(xc * (y[keep] - y[keep].mean())) / np.sum(xc**2))
    check(ctx, "H1b PLP slope", slope, ("H1b", "PLP", "slope"), 1e-9)
    check(ctx, "H1b PLP states excluded as non-finite", float((~keep).sum()),
          ("H1b", "PLP", "n_excluded_nonfinite"), 0.0)
    check(ctx, "H1b PLP states where the floor binds", float((e_p[keep] < 1e-12).sum()),
          ("H1b", "PLP", "n_floored"), 0.0)
    return [Series(ctx.system, "H1b", "PLP", psi, False, int(keep.sum()))]


SERIES_BUILDERS: tuple[tuple[str, Callable[[Context], list[Series]]], ...] = (
    ("H2a(i)", series_h2a_i), ("H2a(ii)", series_h2a_ii), ("H2b(i)", series_h2b_i),
    ("H2b(ii)", series_h2b_ii), ("H3c", series_h3c), ("H2c", series_h2c), ("H2d", series_h2d),
    ("H2e", series_h2e), ("Q-N", series_qn), ("H1b", series_h1b))


# --------------------------------------------------------------------------------------------
# the sections
# --------------------------------------------------------------------------------------------
def section_d1_d2(ctx: Context) -> list[Series]:
    """D1 and D2 for one system; returns its series."""
    rep = ctx.rep
    series: list[Series] = []
    rep.say(f"Reproduction of the results statistics from the dump, {ctx.system}")
    for name, builder in SERIES_BUILDERS:
        got = attempt(rep, f"{ctx.system} {name} series", builder, ctx)
        if got:
            series.extend(got)
    rep.say(f"D1 influence series and autocorrelation, {ctx.system} "
            f"(P = primary; lags 1 to {LAGS}; rule 0.15 for n <= 500, 0.11 above)")
    rows: dict = {}
    for s in series:
        try:
            lags = acf(s.values)
        except NotComputable as exc:
            rep.nc(f"{ctx.system} {s.name} acf", str(exc))
            continue
        text, weight = acf_reading(s.criterion, float(lags[0]), s.n)
        rep.say(f"  {s.name:28s} n={s.n:5d} domain={s.domain:5d} {'P' if s.primary else '-'} "
                + " ".join(f"{a:+.3f}" for a in lags))
        rep.say(f"      reading: {text}; P(|acf1| > {acf_threshold(s.n):g} | no dependence) "
                f"= {lag_zero_false_trigger(s.n):.4f}")
        rows[s.name] = {"n": s.n, "domain": s.domain, "primary": s.primary, "acf": lags.tolist(),
                        "reading": text, "weight_toward_phi03": weight}
    rep.data.setdefault(ctx.system, {})["D1"] = rows
    primaries = [s for s in series if s.primary and s.name in rows]
    if primaries:
        within = sum(abs(rows[s.name]["acf"][0]) <= acf_threshold(s.n) for s in primaries)
        rep.say(f"  primary series with |acf1| within the phi = 0 threshold: "
                f"{within} of {len(primaries)}")
    rep.say(f"D2 block-length diagnostics, {ctx.system} (V*(b) exact; A5 rule: "
            f"V*(10)/V*(5) > {RATIO_RULE[0]} or V*(20)/V*(5) > {RATIO_RULE[1]})")
    d2: dict = {}
    fires = beta_fires = 0
    for s in series:
        if s.name not in rows:
            continue
        try:
            summary = variance_summary(s.values)
        except NotComputable as exc:
            rep.nc(f"{ctx.system} {s.name} V*", str(exc))
            continue
        lags = np.array(rows[s.name]["acf"])
        beta = beta_reading(lags, s.n)
        null_rate = UNION_NULL.get(s.n)
        rate_text = ("not tabulated for this n" if null_rate is None else
                     f"{null_rate:.3f} under no dependence; {UNION_STRESS[s.n]:.3f} at phi = 0.3")
        rep.say(f"  {s.name:28s} {'P' if s.primary else '-'} V5 {summary['V5']:.4g}  "
                f"V10/V5 {summary['ratio10']:.3f}  V20/V5 {summary['ratio20']:.3f}  "
                f"A5 rule {'FIRES' if summary['fires'] else 'quiet'} (predicted trigger rate: "
                f"{rate_text})")
        rep.say(f"      beta5 {beta['beta5']:.4f} +- {beta['se']:.4f} (phi {beta['phi']:+.3f}; "
                f"geometric acf {'holds' if beta['used'] else 'FAILS'}, max gap {beta['gap']:.3f} "
                f"vs {2.5 / math.sqrt(s.n):.3f}): "
                + ("DESIGN QUESTION (beta5 + 2 SE < 0.8685)" if beta["fires"]
                   else ("no" if beta["used"] else "not used")))
        d2[s.name] = {**summary, "beta": beta, "null_rate": null_rate, "primary": s.primary}
        if s.primary:
            fires += summary["fires"]
            beta_fires += beta["fires"]
    rep.data.setdefault(ctx.system, {})["D2"] = d2
    prim = [s for s in primaries if s.name in d2]
    rates = [UNION_NULL.get(s.n) for s in prim]
    if prim and all(r is not None for r in rates):
        any_rate = 1.0 - float(np.prod([1.0 - r for r in rates]))
        rep.say(f"  A5 rule fires on {fires} of {len(prim)} primary series; predicted P(at least "
                f"one) under no dependence for these n: {any_rate:.3f}")
    elif prim:
        rep.say(f"  A5 rule fires on {fires} of {len(prim)} primary series; predicted rates are "
                "tabulated for n = 300, 500, 1000 only (not tabulated here)")
    rep.say(f"  beta5 reading fires on {beta_fires} of {len(prim)} primary series")
    perm = attempt(rep, f"{ctx.system} D2 permutation null", _permutation_reading, ctx, prim)
    rep.data.setdefault(ctx.system, {})["D2_permutation"] = perm
    any_fire = bool(fires or beta_fires or (perm and perm["fires"]))
    rep.data.setdefault(ctx.system, {})["D2_design_question"] = any_fire
    rep.say("  D2 owner flag, " + ctx.system + ": "
            + ("block length 5 is a design question (a reading fired; which reading governs is "
               "OF-3, the owner's)" if any_fire else "no reading fired"))
    return series


def _permutation_reading(ctx: Context, primaries: list[Series]) -> dict:
    rep = ctx.rep
    usable = []
    for s in primaries:
        try:
            variance_summary(s.values)
            usable.append(s)
        except NotComputable as exc:
            rep.nc(f"{ctx.system} {s.name} permutation null input", str(exc))
    obs, null = permutation_null([s.values for s in usable], ctx.permutations,
                                 ctx.rng("d2-permutation"))
    q99 = float(np.quantile(null, 0.99))
    p = (1 + int(np.sum(null >= obs))) / (1 + len(null))
    fires = bool(obs > q99)
    rep.say(f"  pooled mean log V*(10)/V*(5) over {len(usable)} primary series: {obs:+.4f}; "
            f"permutation null ({len(null)} permutations, seed {ctx.seed}) 0.99 quantile "
            f"{q99:+.4f}, one-sided p {p:.4f}: {'DESIGN QUESTION' if fires else 'no'}")
    return {"observed": obs, "q99": q99, "p": p, "fires": fires, "n_series": len(usable)}


def section_d3(ctx: Context) -> None:
    """D3: log-SD of the per-state evaluation MSE and of its draw-free state part."""
    rep, d = ctx.rep, ctx.dump
    n_draws = int(d.scalar("meta/n_eval_draws"))
    rep.say(f"D3 log-SD of the per-state evaluation MSE at H_ref, {ctx.system} "
            f"(E = {n_draws} evaluation draws; reading: above {LOGSD_RULE} the C2h/C4h rows apply)")
    e_c, e_p, cross = (d[f"core/{k}"][:, ctx.ref] for k in ("E_C", "E_P", "C"))
    out: dict = {}
    for rule in RULES_LOGSD:
        try:
            sigma, n_bad = log_sd(d[f"core/state_mse/{rule}"][:, ctx.ref])
        except NotComputable as exc:
            rep.nc(f"{ctx.system} D3 {rule}", str(exc))
            continue
        proj = logsd_at_draws(sigma, n_draws)
        if rule == "A1":
            state = hybrid_state_mse(np.zeros(len(e_c)), e_c, e_p, cross)
        elif rule in ("A2", "A3", "A4", "A5"):
            state = (hybrid_state_mse(d[f"core/weight_href/{rule}"], e_c, e_p, cross)
                     if d.has(f"core/weight_href/{rule}") else None)
        else:
            state = None
        state_sd = None
        if state is None:
            rep.nc(f"{ctx.system} D3 {rule} state part", f"array 'core/weight_href/{rule}' missing")
        else:
            state_sd = log_sd(state)[0]
        reading = ("C2h/C4h rows apply" if sigma > LOGSD_RULE else "C2h/C4h rows do not apply")
        proj_text = (f"{proj:.3f}" if proj is not None else
                     "not defined (log-SD^2 is below psi'(E/2) - psi'(2))")
        rep.say(f"  {rule}: log-SD {sigma:.3f} ({reading}); at E = 4: {proj_text}; "
                f"draw-free state part {fmt(state_sd, 3)}"
                + (f"; {n_bad} non-positive per-state MSE excluded" if n_bad else ""))
        out[rule] = {"log_sd": sigma, "above_rule": bool(sigma > LOGSD_RULE), "log_sd_E4": proj,
                     "state_part_log_sd": state_sd, "n_nonpositive": n_bad}
    rep.data.setdefault(ctx.system, {})["D3"] = {"E": n_draws, "rules": out}


def _half_arrays(ctx: Context) -> dict:
    """Unclipped optima of the two halves and the full 200 draws at H_ref, with the weights."""
    d, ref = ctx.dump, ctx.ref
    mom = {t: tuple(d[f"core/{k}{t}"][:, ref] for k in ("E_C", "E_P", "C"))
           for t in ("_A", "_B", "")}
    u = {t: unclipped_optimum(*mom[t])[0] for t in mom}
    return {"u_a": u["_A"], "u_b": u["_B"], "u": u[""], "w": d["core/w_star"][:, ref],
            "w_a": d["core/w_star_A"][:, ref], "w_b": d["core/w_star_B"][:, ref]}


def section_d4(ctx: Context) -> None:
    """D4: split-half reliability and the attenuation of H2a(ii)."""
    rep, d = ctx.rep, ctx.dump
    rep.say(f"D4 split-half reliability of the unclipped optimum u = (E_P - C)/c, {ctx.system} "
            "(draws 1-100 against 101-200; the interior values overstate reliability: the "
            "excluded near-clip states are the noisiest)")
    out: dict = {}
    h = attempt(rep, f"{ctx.system} D4 inputs", _half_arrays, ctx)
    if h is None:
        return
    rho = float(dig(ctx.cfg, "core_noise"))
    controls = quadratic_controls(np.column_stack([np.log(d["core/eps_s"] / rho),
                                                   np.log(d["core/delta"] / rho)]))
    lam = d["core/Lambda_bar"] * ctx.lt
    inter = attempt(rep, f"{ctx.system} D4 interior", interior_attenuation,
                    h["u_a"], h["u_b"], h["w"], controls, lam)
    if inter:
        sb = inter["spearman_brown"]
        rep.say(f"  interior: {inter['n_interior']} interior states, {inter['n_undefined_halves']} "
                f"without a defined half optimum, {inter['n_excluded_delta']} excluded as not "
                f"delta-valid (of {inter['n_domain']}); mean v {inter['mean_v']:.4g}, var(y~) "
                f"{inter['var_valid']:.4g} (all interior {inter['var_all']:.4g})")
        rep.say(f"      delta-method reliability {fmt(inter['reliability'])}, attenuation A "
                f"{fmt(inter['A'])} (A with the all-interior variance {fmt(inter['A_all'])}); "
                f"bias of a partial correlation at the band edge 0.1 (1 - A) = "
                f"{fmt(inter['bias_at_edge'])}")
        rep.say(f"      Spearman-Brown: r_AB {fmt(sb['r_ab'])} on {sb['n_states']} states, "
                f"reliability {fmt(sb['reliability'])}, A {fmt(sb['A'])} (overstates reliability)")
        rep.say(f"      Spearman(v, Lambda_tilde | Q) = {fmt(inter['spearman_v_lambda_given_Q'])} "
                "(nonzero: the draw noise is not classical; sign unknown)")
        out["interior"] = inter
    zero = attempt(rep, f"{ctx.system} D4 zero", zero_reliability, h["w_a"], h["w_b"], h["w"])
    if zero:
        rep.say(f"  zero: share of w = 0 {zero['share_zero']:.3f}; r_100 = Cov/Var(200-draw "
                f"indicator) = {fmt(zero['r100'])}; Spearman-Brown reliability "
                f"{fmt(zero['reliability'])}, attenuation sqrt = {fmt(zero['A'])}; Pearson form: "
                f"r {fmt(zero['pearson_r'])}, reliability {fmt(zero['pearson_reliability'])}")
        out["zero"] = zero
    rep.data.setdefault(ctx.system, {})["D4"] = out


def _v4_flag_line(ctx: Context) -> str:
    d = ctx.dump
    if not d.has("v4/extra_href_equal"):
        return "v4/extra_href_equal is not in the dump (2 and 4 LT columns unverified)"
    equal = bool(d.scalar("v4/extra_href_equal"))
    diff = int(d.scalar("v4/extra_href_diff")) if d.has("v4/extra_href_diff") else None
    if equal:
        return "extra_href_equal True (the second V4 forecast reproduces the H_ref column)"
    return (f"WARNING extra_href_equal FALSE ({diff} differing H_ref entries): the 2 and 4 LT "
            "columns come from a call that did not reproduce the production H_ref column")


def _v4_flag_short(ctx: Context) -> str:
    """``extra_href_equal`` in a few words, printed beside a reading that uses the 2 and 4 LT columns."""
    if not ctx.dump.has("v4/extra_href_equal"):
        return "extra_href_equal not in the dump"
    return ("extra_href_equal True" if bool(ctx.dump.scalar("v4/extra_href_equal"))
            else "EXTRA_HREF_EQUAL FALSE")


def section_d5(ctx: Context) -> None:
    """D5: the finite-M bias of the H2a(i) median range, and the V4 check."""
    rep = ctx.rep
    rep.say(f"D5 finite-M bias of the H2a(i) median range, {ctx.system} (split-half Richardson, "
            "order 1/2; order 1 printed beside it)")
    out: dict = {}
    inp = attempt(rep, f"{ctx.system} D5 inputs", h2a_inputs, ctx)
    if inp is not None:
        r_full, eligible, leading = leading_ranges(inp["w"], inp["small"])
        r_a, r_b = segment_ranges(inp["w_a"], leading), segment_ranges(inp["w_b"], leading)
        if not np.all(np.isfinite(r_a[eligible]) & np.isfinite(r_b[eligible])):
            rep.nc(f"{ctx.system} D5", "a half-draw range is not finite on an eligible state")
        else:
            out = _d5_primary(ctx, r_full, r_a, r_b, eligible)
    out["v4"] = attempt(rep, f"{ctx.system} D5 V4 check", _d5_v4, ctx)
    rep.data.setdefault(ctx.system, {})["D5"] = out


def _d5_primary(ctx: Context, r_full, r_a, r_b, eligible) -> dict:
    rep = ctx.rep
    n = len(r_full)
    med = lambda r: float(np.median(r[eligible]))  # noqa: E731
    shift = split_half_shift(med(r_a), med(r_b), med(r_full))
    bias = RICHARDSON * shift

    def stat(idx: np.ndarray) -> float:
        rows = idx[eligible[idx]]
        if rows.size == 0:
            return float("nan")
        return RICHARDSON * split_half_shift(*(float(np.median(r[rows])) for r in (r_a, r_b, r_full)))

    block = int(dig(ctx.cfg, "bootstrap_block"))
    se, failed = bootstrap_se(stat, n, ctx.resamples, block, ctx.rng("d5-bootstrap"))
    ci = dig(ctx.res, "H2a", "range_ci")
    hw = (ci[1] - ci[0]) / 2.0
    hw_full, how = full_halfwidth(hw, ctx.cfg, "n_test")
    limit = 0.1 * hw_full
    reading = three_way_reading(bias, se, limit)
    point = "above" if abs(bias) > limit else "not above"
    row1 = ("may be stated below 10%" if reading == "below 10%"
            else "stays 'not below 10%' (PF-5: 'not determined' is treated as not below)")
    rep.say(f"  eligible states {int(eligible.sum())} of {n}; med r_A {med(r_a):.5f}, med r_B "
            f"{med(r_b):.5f}, med r_200 {med(r_full):.5f}")
    rep.say(f"  Delta_sh {shift:+.5f}; B(200) order 1/2 {bias:+.5f}; order 1 {shift:+.5f}; "
            f"SE {se:.5f} ({failed} failed of {ctx.resamples} resamples, block {block}, "
            f"seed {ctx.seed})")
    rep.say(f"  hw (pilot or run) {hw:.5f}; hw_full {hw_full:.5f} ({how}); 0.1 hw_full {limit:.5f}")
    rep.say(f"  reading: {reading}; point reading |B| {point} 0.1 hw_full; budget row 1 {row1}")
    check(ctx, "H2a(i) median range (D5 input)", med(r_full), ("H2a", "median_range"), 0.0)
    return {"n_eligible": int(eligible.sum()), "delta_sh": shift, "bias_order_half": bias,
            "bias_order_one": shift, "se": se, "n_failed": failed, "hw": hw, "hw_full": hw_full,
            "hw_full_how": how, "limit": limit, "reading": reading, "point_reading": point}


def _d5_v4(ctx: Context) -> dict:
    rep, d = ctx.rep, ctx.dump
    rep.say("  V4 three-level check (first states of the test split, 1, 2 and 4 LT)")
    rep.say("    " + _v4_flag_line(ctx))
    levels, w_hat, dev, half = (d[f"v4/{k}"] for k in ("M", "w_hat", "signed_dev", "half_width"))
    horizons = d["v4/horizons"]
    n_v4 = w_hat.shape[1]
    core_h = d["core/horizons"]
    try:
        cols = [int(np.flatnonzero(core_h == h)[0]) for h in horizons]
    except IndexError:
        raise NotComputable("a V4 horizon is not among the core horizons") from None
    rms = float(dig(ctx.cfg, "linear_regime_rms"))
    small = np.column_stack([(np.sqrt(d["core/E_C"][:n_v4, c]) <= rms)
                             & (np.sqrt(d["core/E_P"][:n_v4, c]) <= rms) for c in cols])
    leading = np.cumprod(small, axis=1).astype(bool)
    eligible = leading.sum(axis=1) >= 2
    if eligible.sum() < 2:
        raise NotComputable(f"{int(eligible.sum())} eligible V4 states")
    order = np.argsort(levels)
    levels = levels[order]
    ranges = [segment_ranges(w_hat[i], leading)[eligible] for i in order]
    med = [float(np.median(r)) for r in ranges]
    out: dict = {"M": levels.tolist(), "n_v4": n_v4, "n_eligible": int(eligible.sum()),
                 "extra_href_equal": (bool(d.scalar("v4/extra_href_equal"))
                                      if d.has("v4/extra_href_equal") else None),
                 "median_half_width": {}}
    dev_mean = {int(m): float(np.mean(dev[order[i], :, 0])) for i, m in enumerate(levels)}
    out["signed_mean_dev_href"] = dev_mean
    rep.say("    signed mean of w_M - w_ref at H_ref by M: "
            + ", ".join(f"M={m}: {v:+.5f}" for m, v in dev_mean.items()))
    first = min(n_v4, 40)
    for i, m in enumerate(levels):
        hw_all = float(np.median(half[order[i], :, 0]))
        hw_first = float(np.median(half[order[i], :first, 0]))
        out["median_half_width"][int(m)] = {"all": hw_all, "first_40": hw_first}
    rep.say("    median half-width at H_ref (all V4 states; first 40, the pilot-equivalent V4): "
            + ", ".join(f"M={m}: {out['median_half_width'][int(m)]['all']:.5f} "
                        f"({out['median_half_width'][int(m)]['first_40']:.5f})" for m in levels))
    if len(levels) < 3:
        rep.nc(f"{ctx.system} D5 V4 order", f"{len(levels)} draw counts; the check needs three")
        return out
    m_a, m_b, m_c = (int(x) for x in levels[-3:])
    if m_b / m_a != 4 or m_c / m_b != 4:
        rep.nc(f"{ctx.system} D5 V4 order", f"draw counts {m_a}, {m_b}, {m_c} are not a ratio-4 "
               "chain")
        return out
    s = {k: med[len(levels) - 3 + j] - med[-1] for j, k in enumerate(("a", "b"))}
    p, note = v4_order(s["a"], s["b"])
    shift_b = 2.0 * s["b"]
    rep.say(f"    m({m_a}) {s['a']:+.5f}, m({m_b}) {s['b']:+.5f} (shifts of the median range "
            f"against M = {m_c}); observed order {fmt(p)} ({note}); B_V4({m_b}) = 2 m({m_b}) = "
            f"{shift_b:+.5f} (order 1/2) [uses the 2 and 4 LT columns; {_v4_flag_short(ctx)}]")
    out.update(shift_a=s["a"], shift_b=s["b"], order=p, order_note=note, bias_v4=shift_b)
    return out


def section_d6(ctx: Context) -> None:
    """D6: the H2b(ii) bias by split-half Richardson on the paired change, and f_b."""
    rep, d = ctx.rep, ctx.dump
    rep.say(f"D6 H2b(ii) clip-boundary bias, {ctx.system} (split-half Richardson on the mean "
            "paired change of the library cells; f_b = share within 2 s of a clip bound)")
    rho = float(dig(ctx.cfg, "core_noise"))
    cells: dict = {}
    try:
        for n_lib in H2B_LIBRARY:
            g = ctx.group(rho, n_lib)
            mom = {t: tuple(d[f"{g}/{k}{t}"] for k in ("E_C", "E_P", "C"))
                   for t in ("_A", "_B", "")}
            u, _ = zip(*(unclipped_optimum(*mom[t]) for t in ("_A", "_B", "")))
            w = {t: weight_from_moments(*mom[t]) for t in mom}
            if not np.array_equal(w[""], d[f"{g}/w_star_href"]):
                ctx.rep.defects.append(f"{ctx.system} D6 {g}: the weight rebuilt from the dumped "
                                       "moments differs from w_star_href")
                rep.say(f"  MISMATCH: weight rebuilt from the moments of {g} differs from w_star_href")
            cells[n_lib] = {"u_a": u[0], "u_b": u[1], "u": u[2], "w_a": w["_A"], "w_b": w["_B"],
                            "w": w[""]}
    except NotComputable as exc:
        rep.nc(f"{ctx.system} D6 inputs", str(exc))
        return
    lo, hi = H2B_LIBRARY
    change = {k: cells[hi][k] - cells[lo][k] for k in ("w_a", "w_b", "w")}
    n = len(change["w"])
    shift = split_half_shift(float(change["w_a"].mean()), float(change["w_b"].mean()),
                             float(change["w"].mean()))
    bias = RICHARDSON * shift
    block = int(dig(ctx.cfg, "bootstrap_block"))
    se, failed = attempt(rep, f"{ctx.system} D6 bootstrap", bootstrap_se,
                         lambda idx: RICHARDSON * split_half_shift(
                             *(float(change[k][idx].mean()) for k in ("w_a", "w_b", "w"))),
                         n, ctx.resamples, block, ctx.rng("d6-bootstrap")) or (None, None)
    out: dict = {"n_states": n, "delta_sh": shift, "bias_order_half": bias,
                 "bias_order_one": shift, "se": se, "n_failed": failed}
    check(ctx, "H2b(ii) mean change (D6 input)", float(change["w"].mean()),
          ("H2b", "library_change", "mean_change"), 1e-12)
    try:
        ci = dig(ctx.res, "H2b", "library_change", "ci")
        hw_full, how = full_halfwidth((ci[1] - ci[0]) / 2.0, ctx.cfg, "n_test_sweep")
        out.update(hw_full=hw_full, hw_full_how=how)
    except Missing as exc:
        ctx.rep.nc(f"{ctx.system} D6 hw_full", str(exc))
        hw_full, how = None, ""
    rep.say(f"  {n} sweep states; Delta_sh {shift:+.5f}; B order 1/2 {bias:+.5f}; order 1 {shift:+.5f};"
            f" SE {fmt(se, 4)} ({failed} failed of {ctx.resamples}, block {block}, seed {ctx.seed})")
    if hw_full is not None and se is not None:
        limit = 0.1 * hw_full
        reading = three_way_reading(bias, se, limit)
        point = "above" if abs(bias) > limit else "not above"
        rep.say(f"  hw_full {hw_full:.5f} ({how}); 0.1 hw_full {limit:.5f}; reading: {reading}; "
                f"point reading |B| {point} 0.1 hw_full")
        out.update(limit=limit, reading=reading, point_reading=point)
    fb: dict = {}
    for n_lib in H2B_LIBRARY:
        c = cells[n_lib]
        ok = np.isfinite(c["u"]) & np.isfinite(c["u_a"]) & np.isfinite(c["u_b"])
        s = np.where(ok, np.abs(c["u_a"] - c["u_b"]) / 2.0, np.nan)
        near = np.where(ok, near_clip(np.where(ok, c["u"], 0.5), np.where(ok, s, 0.0)), False)
        row = {"n_undefined": int((~ok).sum()), "f_b": float(near[ok].mean()) if ok.any() else None,
               "bins": {}}
        for lo_w, hi_w in WEIGHT_BINS:
            if lo_w == hi_w:
                sel = ok & (c["w"] == lo_w)
            elif hi_w == 1.0:
                sel = ok & (c["w"] > lo_w) & (c["w"] < 1.0)
            elif lo_w == 0.1:
                sel = ok & (c["w"] >= lo_w) & (c["w"] <= hi_w)
            else:
                sel = ok & (c["w"] > lo_w) & (c["w"] < hi_w)
            row["bins"][f"{lo_w:g}-{hi_w:g}"] = (int(sel.sum()), float(near[sel].mean())
                                                 if sel.any() else None)
        fb[n_lib] = row
        rep.say(f"  n_lib {n_lib}: f_b {fmt(row['f_b'], 3)} ({row['n_undefined']} states with an "
                "undefined half optimum); by w bin (count, f_b): "
                + ", ".join(f"[{k}] {v[0]}, {fmt(v[1], 3)}" for k, v in row["bins"].items()))
    out["f_b"] = fb
    rep.data.setdefault(ctx.system, {})["D6"] = out


# --------------------------------------------------------------------------------------------
# driver
# --------------------------------------------------------------------------------------------
def check_provenance(ctx: Context, seed_id: str) -> None:
    """The dump must belong to this run: same system, seed id and preset (else a MISMATCH)."""
    want = {"meta/system": ctx.system, "meta/seed_id": seed_id, "meta/preset": ctx.cfg.get("name")}
    for key, expected in want.items():
        if not ctx.dump.has(key):
            ctx.rep.nc(f"{ctx.system} dump provenance", f"array {key!r} is not in {ctx.dump.source}")
        elif str(ctx.dump.scalar(key)) != str(expected):
            ctx.rep.defect(f"{ctx.system}: {key} is {ctx.dump.scalar(key)!r} in the dump but "
                           f"{expected!r} in results.json (the dump is not this run's)")


def make_label(seed_id: str | None) -> str:
    """The DEVELOPMENT label with the seed id the run recorded."""
    return (f"DEVELOPMENT ({seed_id}): conditional on one realization; not a hypothesis test")


def find_results(path: Path) -> Path:
    """The ``results.json`` of a run (a file, or the directory that holds it)."""
    target = path / "results.json" if path.is_dir() else path
    if not target.is_file():
        raise NotComputable(f"no results.json at {path}")
    return target


def run(results_path: Path, states_dir: Path | None = None, systems: Sequence[str] | None = None,
        seed: int = TOOL_SEED, resamples: int = 2000, permutations: int = 1000) -> Report:
    """Build the whole report for one run.

    Raises
    ------
    NotComputable
        If the results file is unreadable or its seed id is not a development seed.
    """
    path = find_results(results_path)
    try:
        results = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        raise NotComputable(f"{path} is unreadable: {exc}") from exc
    cfg = results.get("config")
    prov = results.get("provenance", {})
    seed_id = (prov.get("seed_id") if isinstance(prov, dict) else None) or (
        cfg.get("seed_id") if isinstance(cfg, dict) else None)
    if not isinstance(cfg, dict) or not isinstance(seed_id, str):
        raise NotComputable("results.json has no config block or no seed id")
    if not (seed_id.startswith("DEV-") and seed_id[4:].isdigit()):
        raise NotComputable(f"refused: seed id {seed_id!r} is not a development seed DEV-n")
    folder = states_dir if states_dir is not None else path.parent / "states"
    rep = Report()
    rep.say(make_label(seed_id))
    rep.say("rehearsal_diagnostics (WU-0003.8): D1 to D6; needs owner review before freeze "
            "(statistics feeding the block-length and M decisions)")
    rep.say(f"run: {path}; preset {cfg.get('name')}; commit {prov.get('commit', 'not recorded')}; "
            f"tool seed {seed} (literal scratch seed, not a development or confirmatory seed)")
    rep.say(f"outside schema {SCHEMA} (no arrays; not computed): " + ", ".join(OUTSIDE_SCHEMA))
    rep.data["label"] = make_label(seed_id)
    all_systems = list(results.get("systems", {}))
    chosen = [s for s in all_systems if systems is None or s in systems]
    for wanted in systems or ():
        if wanted not in all_systems:
            rep.nc(f"system {wanted}", "not in results.json")
    for system in chosen:
        rep.say("")
        rep.say(f"=== {system} ===")
        file = folder / f"{system}.npz"
        if not file.is_file():
            rep.nc(f"{system} (D1 to D6)", f"{file} not found (run without --states-dump?)")
            continue
        dump = Dump.load(file)
        try:
            schema = dump.scalar("meta/schema")
        except NotComputable as exc:
            rep.nc(f"{system} (D1 to D6)", str(exc))
            continue
        if schema != SCHEMA:
            rep.nc(f"{system} (D1 to D6)", f"schema {schema!r} is not {SCHEMA!r}")
            continue
        ctx = Context(system, dump, results["systems"][system], cfg, rep, seed, resamples,
                      permutations)
        try:
            check_provenance(ctx, seed_id)
            section_d1_d2(ctx)
            for name, section in (("D3", section_d3), ("D4", section_d4), ("D5", section_d5),
                                  ("D6", section_d6)):
                attempt(rep, f"{system} {name}", section, ctx)
        finally:
            dump.close()
    rep.say("")
    if rep.incomplete:
        rep.say(f"not computable: {len(rep.incomplete)} item(s) (listed above); never skipped")
    if rep.defects:
        rep.say(f"MISMATCH: {len(rep.defects)} item(s) (listed above)")
    return rep


def _json_ready(obj):
    if isinstance(obj, dict):
        return {str(k): _json_ready(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_ready(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return _json_ready(obj.tolist())
    if isinstance(obj, (np.floating, float)):
        return None if not math.isfinite(float(obj)) else float(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    return obj


def main(argv: list[str] | None = None) -> int:
    """Command-line entry; returns the exit code."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("run", type=Path, help="results.json, or the directory that holds it")
    ap.add_argument("--states", type=Path, default=None, help="folder of <system>.npz dumps")
    ap.add_argument("--systems", nargs="+", default=None, help="restrict to these systems")
    ap.add_argument("--json", type=Path, default=None, help="write the numbers to this file")
    ap.add_argument("--seed", type=int, default=TOOL_SEED,
                    help=f"seed of the tool's bootstrap and permutations (default {TOOL_SEED})")
    ap.add_argument("--resamples", type=int, default=2000, help="D5/D6 bootstrap resamples")
    ap.add_argument("--permutations", type=int, default=1000, help="D2 permutations")
    args = ap.parse_args(argv)
    if args.resamples < 2 or args.permutations < 2:
        print("rehearsal_diagnostics: error: --resamples and --permutations need at least 2",
              file=sys.stderr)
        return EXIT_INCOMPLETE
    try:
        rep = run(args.run, args.states, args.systems, args.seed, args.resamples,
                  args.permutations)
    except NotComputable as exc:
        print(f"rehearsal_diagnostics: error: {exc}", file=sys.stderr)
        return EXIT_INCOMPLETE
    print("\n".join(rep.lines))
    if args.json is not None:
        args.json.write_text(json.dumps(_json_ready(rep.data), indent=1))
    return rep.exit_code()


if __name__ == "__main__":
    sys.exit(main())
