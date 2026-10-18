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
``lpcstudy/dump.py``; ``--states`` overrides the folder). Every recorded seed id (``config.seed_id``,
``provenance.seed_id``, ``provenance.seed_kind == "development"``, and each dump's ``meta/seed_id``)
must be present, agree and be a development seed ``DEV-n``; otherwise the run is refused (exit 2).

What it computes (plan amendment 2, B1 item 7 as amended; mathematics check
``docs/agent/notes/2026-10-14-math-wu0003.md``, M3 to M5; amendments 3 and 4 for the dump):

* **D1.** The influence series of every criterion (M4.1) over all states of its split in time
  order, 0 outside the criterion's domain: sign types for the medians (H2a(i), H2e), the
  influence of the partial correlation (H2a(ii) zero, interior and, when triggered, one), of an
  OLS slope (H1b), of a ratio of means (H3c, H2d), of a difference of means (H2c, H2b(ii), H2b(i)
  through the per-state Spearman) and of the Q-N gain ``Delta R^2``. Its autocorrelation at lags
  1 to 10 and the readings of the rule: ``|acf(1)| <= 0.15`` (n <= 500) or ``0.11`` (n > 500)
  means the phi = 0 rows apply; ``acf(1)`` at least the case value (0.30 H2b(i), H2b(ii), H2c;
  0.19 H2a(i), H2e; 0.16 H3c, H2d; 0.09 H2a(ii), H1d) means the phi = 0.3 rows are realistic and
  governs. The coverage (95% and 1 - 0.05/3) is ``cov0 + (cov0.3* - cov0) min(1, max(0, l/l_c))``
  from the WU-0006 table with the anchor ``cov0.3* = min(cov0, cov0.3)`` (amendment 9, I1),
  interpolated from l = 0 (plan amendment 5, E2), "at most cov0.3* (beyond
  the tabulated stress)" above the case value, and "coverage not tabulated" for Q-N and H1b.
* **D2.** ``V*(b) = b * var(means of the n - b + 1 overlapping blocks of length b)`` (the exact
  moving-block variance, no bootstrap noise) and the ratios ``V*(10)/V*(5)``, ``V*(20)/V*(5)``;
  the A5 rule (above 1.1 or above 1.15 on a primary series) with its predicted trigger rate under
  no dependence printed beside it (0.21, 0.164, 0.094 at n = 300, 500, 1000, and the
  at-least-one-of-k rate); the acf-implied block-5 factor beta_5 with its delta-method SE ("design
  question" when ``beta_5 + 2 SE < 0.8685``, used only when ``acf(2..10)`` is within ``2.5/sqrt(n)``
  of ``acf(1)**k``); and the pooled per-system mean of ``log V*(10)/V*(5)`` against a permutation
  null (one permutation of the test states per draw, applied to all the system's primary series;
  trigger at the 0.99 quantile). **Owner ruling OF-3 (2026-10-17, amendments note 31): the pooled
  permutation reading governs the D2 verdict**: the per-system line "D2 owner flag" says "block
  length 5 is a design question" iff that reading fires. The A5 rule and beta_5 stay computed and
  printed, with their predicted rates, as information (they do not decide the line). The block
  length stays 5. A run-level line repeats the governing reading over the systems.
* **Block-sensitive label (owner ruling of 2026-10-17, amendments note 31; report-only).** For
  every primary part (the 24 parts of F3: H2a(i), H2a(ii) zero and interior, and "one" when it is
  triggered, H2b(i), H2b(ii), H3c, H1a per rho), the interval of ``results.json`` is widened on each
  side about its point estimate by ``f = sqrt(max(1, V*(10)/V*(5)))`` of the part's own influence
  series, and the verdict rule of the part (the production band and the production
  ``criterion_verdict``, with ``n_states`` the part's domain) is applied to the widened interval.
  If the verdict changes, the part is labelled "BLOCK-SENSITIVE" (also in ``--json``). The label
  changes no criterion, no verdict, no number of the report and **no exit code**: it is
  informational. A part for which the inputs are missing (a leaf absent or not finite, V*(5) not
  positive, a baseline verdict recomputed from the interval that differs from the recorded one, a
  series that could not be built) is counted "not computable" in the label lines and in the
  ``--json``, and never skipped; because the label is informational, those rows do not add to the
  "not computable" list that decides the exit code (a series that could not be built is there
  already).
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

A missing array, a schema other than ``lpcstudy.states/1``, a non-finite half-width, a series that
cannot be formed, or an unexpected exception (an "INTERNAL ERROR" line with the place it happened)
prints ``not computable: <what>: <why>`` and is never skipped or replaced; the rest of the section
and of the report is still computed. H1a and H1c have no arrays in the schema: each is one "not
computable" line per run (so every run exits 2 until the schema carries them). H1d is computed from
``core/profile`` (columns 0 to 3 of the first evaluation draw are strictly increasing transforms of
the proxies, which Spearman ignores) and ``core/eps_s``, ``delta``, ``Lambda_bar``, ``N``. Where the
results file carries the statistic that a series is the influence of, the tool recomputes it from
the dump and prints MATCH or MISMATCH (a mismatch is a defect of the dump or of this tool) with
``|diff| <= tol max(|leaf|, scale)``, the scale being the natural size of the statistic's terms.
After the systems it prints the run-level D1 line (every |acf(1)| within its threshold?) and the
D2 lines (at least one primary series triggers the A5 rule, against its predicted probability; the
governing pooled permutation reading over the systems; the block-sensitive parts).

The bootstrap and permutation generators are ``make_rng(--seed, system, label)``; the default seed
is a literal scratch seed (``TOOL_SEED``), not a development or confirmatory seed, so a report is
reproducible. The run's own seed is never read.

Exit codes: 0 everything computed and no mismatch; 1 at least one MISMATCH; 2 unreadable input, a
usage error, a refused run, an internal error, or at least one "not computable" (the report is still
printed in full; 1 takes precedence over 2). The seed and the options are printed prominently and
recorded in the ``--json`` output: rerunning with other options to change a reading is not allowed
(an owner question).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
import warnings
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from scipy import special
from scipy import stats as sps
from scipy.optimize import OptimizeWarning, curve_fit, least_squares

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lpcstudy.config import PRESETS  # noqa: E402  (after the path line; no jax import)
from lpcstudy.statistics import block_resample_indices, criterion_verdict  # noqa: E402

common = sys.modules.get("rehearsal_common")
if common is None:  # the shared code of the two rehearsal tools (WU-0003.10), loaded by path
    _SPEC = importlib.util.spec_from_file_location("rehearsal_common",
                                                   Path(__file__).with_name("rehearsal_common.py"))
    assert _SPEC is not None and _SPEC.loader is not None
    common = importlib.util.module_from_spec(_SPEC)
    sys.modules["rehearsal_common"] = common
    _SPEC.loader.exec_module(common)

EXIT_MISMATCH = common.EXIT_MISMATCH
EXIT_INCOMPLETE = common.EXIT_INCOMPLETE
SCHEMA = "lpcstudy.states/1"
SCHEMAS = common.SCHEMAS
"""Accepted schema versions: ``/2`` adds the ``h1a/`` and ``h1c/`` groups and keeps every key of
``/1`` (the keys this tool reads are the same)."""
DEFAULT_RESAMPLES, DEFAULT_PERMUTATIONS = 2000, 1000
COVERAGE = {
    "H2a(i)": ((0.9448, 0.9807), (0.9292, 0.9732)),
    "H2a(ii)": ((0.9443, 0.9794), (0.9389, 0.9762)),
    "H2b(i)": ((0.9444, 0.9806), (0.9230, 0.9682)),
    "H2b(ii)": ((0.9444, 0.9806), (0.9230, 0.9682)),
    "H3c": ((0.9402, 0.9772), (0.9265, 0.9715)),
    "H2c": ((0.9395, 0.9774), (0.9282, 0.9706)),
    "H2d": ((0.9383, 0.9766), (0.9275, 0.9691)),
    "H2e": ((0.9427, 0.9782), (0.9311, 0.9736)),
    "H1d": ((0.9470, 0.9794), (0.9439, 0.9800)),
}
"""WU-0006 reference coverage at pilot n, ``((phi = 0 at 95%, at 1 - 0.05/3), (phi = 0.3 at 95%, at
1 - 0.05/3))`` per criterion (plan amendment 5, E2: cases C3, C7, C8, C4, C2, C5, C9, C6)."""
TOOL_SEED = 20261018
"""Default seed of the tool's own bootstrap and permutations (a literal scratch seed)."""
LAGS = 10
BLOCKS = (5, 10, 20)
ACF_SMALL, ACF_LARGE = 0.15, 0.11
"""``|acf(1)|`` thresholds for n <= 500 and n > 500 (M4: 3.4 SE at n = 500 and at n = 1000)."""
CASE_VALUE = {"H2b(i)": 0.30, "H2b(ii)": 0.30, "H2c": 0.30, "H2a(i)": 0.19, "H2e": 0.19,
              "H3c": 0.16, "H2d": 0.16, "H2a(ii)": 0.09, "H1d": 0.09}
"""Lag-1 of the influence series at a latent phi = 0.3, by criterion (M4.2, WU-0006 M2)."""
RATIO_RULE = (1.1, 1.15)
BETA_STRESS = 0.8685
"""beta_5(0.3): the stress case already in the budget."""
UNION_NULL = {300: 0.210, 500: 0.164, 1000: 0.094}
"""P(V*(10)/V*(5) > 1.1 or V*(20)/V*(5) > 1.15) per series, no dependence (``m5_d5split.log``)."""
UNION_STRESS = {300: 0.401, 500: 0.425, 1000: 0.400}
"""The same at phi = 0.3 (power)."""
VERDICT_RULES = {
    "H2a(i)": ((-math.inf, 0.1), (True, False)),
    "H2a(ii)": ((-0.1, 0.1), (False, False)),
    "H2b(i)": ((0.0, math.inf), (False, True)),
    "H2b(ii)": ((0.0, math.inf), (False, True)),
    "H3c": ((-math.inf, 1.05), (True, True)),
    "H1a": ((0.75, 1.25), (True, True)),
}
"""Band and closed edges of each primary part's verdict: copies of ``lpcstudy.analysis``
(``H2A_RANGE_BAND`` with closed edges ``(True, False)``, ``H2A_PARTIAL_BAND`` ``(False, False)``,
the one-sided ``(0, inf)`` with ``(False, True)`` of H2b, ``H3C_BOUND`` and ``H1A_BAND``); that module
is not imported (it needs the whole pipeline). A test compares the copies with it."""
LOGSD_RULE = 1.5
PRIMARY_LEVEL_FACTOR = 1.014
"""E hw(B = 2000)/E hw(B = 500) at 1 - 0.05/3 (M3, ``m3_bfactor.log``)."""
RICHARDSON = 1.0 / (math.sqrt(2.0) - 1.0)
"""1/(2^(1/2) - 1) = 2.4142: the order-1/2 Richardson factor from M = 100 to M = 200."""
WEIGHT_BINS = (("w=0", 0.0, 0.0, True, True), ("0<w<0.1", 0.0, 0.1, False, False),
               ("0.1<=w<=0.9", 0.1, 0.9, True, True), ("0.9<w<1", 0.9, 1.0, False, False),
               ("w=1", 1.0, 1.0, True, True))
"""Bins of ``w`` for ``f_b``: label, edges and whether each edge is included."""
H2B_LIBRARY = (1_000, 10_000)
H2E_LIBRARY = (1_000, 100_000)
QN_TARGETS = ("logit_w_interior", "w_zero_indicator", "log_horizon")
RULES_LOGSD = ("A1", "A2", "A3", "A4", "A5")
OUTSIDE_SCHEMA: tuple[tuple[str, str], ...] = ()
"""Criteria with no series at all (none since row .8c: H1a and H1c are computed from schema /2; a
dump of schema /1, or a cell that cannot be computed, makes them "not computable" by name)."""
NOT_TABULATED = {
    "H1a": "coverage not tabulated (no WU-0006 case for H1a); phi = 0 reading only",
    "H1c": "coverage not tabulated; phi = 0 reading only"}
PRIMARY_CRITERIA = ("H2a(i)", "H2a(ii)", "H2b(i)", "H2b(ii)", "H3c", "H1a")
"""The familywise set (F3): the 18 primaries plus H1a, 24 series at the pilot."""
NAMED_WHEN_MISSING = ("H1a", "H1c")
"""Criteria named in the summary when they are not computable (plan amendment 5, E1)."""
H1A_BOUNDS = (0.01, 10.0)
H1A_BOUND_TOL = 1e-6
H1A_LO = np.array([-50.0, H1A_BOUNDS[0], -60.0])
H1A_HI = np.array([50.0, H1A_BOUNDS[1], 10.0])
HALL_SHEATHER = 1.96 ** (2.0 / 3.0) * (1.5 / (2.0 * math.pi)) ** (1.0 / 3.0)
"""0.97157: the Hall-Sheather bandwidth constant, ``h = HALL_SHEATHER n^(-1/3)`` (MA-1 section 5)."""
REFIT_TOLERANCE = 4e-5
"""The a-priori bound on the production fit's stopping noise, as a fraction of the interval scale."""
HESSIAN_COND_MAX = 1e8
H1A_MIN_STATES = 8
H1D_ROWS = (("analog_seed", 0, "eps_s"), ("estimation_seed", 1, "delta"),
            ("growth", 2, "Lambda_bar"), ("nhat", 3, "N"))
"""H1d pairs: name, column of ``core/profile`` (a strictly increasing transform of the proxy of the
first evaluation draw: ``log(x/rho)``, ``log(x/rho)``, ``x steps_per_lyapunov``, ``log(x + c)``)
and the dumped oracle array."""
H1D_TESTED = ("analog_seed", "estimation_seed", "growth")


# --------------------------------------------------------------------------------------------
# errors and the report
# --------------------------------------------------------------------------------------------
NotComputable = common.NotComputable
Missing = common.Missing
Refused = common.Refused


@dataclass
class Report(common.Report):
    """The shared report (lines, "not computable" and mismatch lists, numbers for ``--json``) and
    the diagnostics' own records."""

    findings: list[str] = field(default_factory=list)
    """Readings outside a band (C4): information, no effect on the exit code."""
    uncomputed: list[tuple[str, bool]] = field(default_factory=list)
    """``(name, primary)`` of every series or criterion that was not computed (R13, plan E1)."""
    series_log: list[dict] = field(default_factory=list)
    """One entry per series with an acf (and its A5 trigger), for the run-level D1/D2 lines (R7)."""


attempt = common.attempt
Dump = common.Dump
dig = common.dig
fmt = common.fmt


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


def psi_spearman(x: np.ndarray, y: np.ndarray, domain: np.ndarray | None = None
                 ) -> tuple[np.ndarray, float]:
    """Influence of the Spearman correlation at the empirical measure, and its value (H1d).

    With the mid-distribution functions ``a_j = F(x_j) = (#{x < x_j} + #{x = x_j}/2)/n`` and
    ``b_j = G(y_j)`` (an affine function of the average ranks), ``rho = (T - 1/4)/sqrt((S_F -
    1/4)(S_G - 1/4))`` with ``T = mean(ab)``, ``S_F = mean(a^2)``, ``S_G = mean(b^2)`` (the means of
    ``a`` and ``b`` are exactly 1/2). The Gateaux derivative at the point ``i``, which includes the
    change of the ranks themselves, is

    ``dT = a_i b_i + mean_j(c^x_ij b_j) + mean_j(a_j c^y_ij) - 3 T``,
    ``dS_F = a_i^2 + 2 mean_j(c^x_ij a_j) - 3 S_F`` (likewise ``dS_G``),
    ``psi_i = dT/D - (rho/2)(dS_F/(S_F - 1/4) + dS_G/(S_G - 1/4))``,

    with ``c^x_ij = 1{x_i < x_j} + 1{x_i = x_j}/2`` and ``D`` the denominator. O(n^2). 0 outside the
    domain. Spearman is invariant to strictly increasing transforms of ``x`` and ``y``.
    """
    xv, dom = _domain(x, domain)
    yv, _ = _domain(y, dom)
    xs, ys = xv[dom], yv[dom]
    n = len(xs)
    if n < 3 or np.ptp(xs) == 0.0 or np.ptp(ys) == 0.0:
        raise NotComputable("Spearman correlation undefined (too few states or a constant series)")
    cx = (xs[:, None] < xs[None, :]).astype(float) + 0.5 * (xs[:, None] == xs[None, :])
    cy = (ys[:, None] < ys[None, :]).astype(float) + 0.5 * (ys[:, None] == ys[None, :])
    a, b = cx.sum(axis=0) / n, cy.sum(axis=0) / n
    t, s_f, s_g = float(np.mean(a * b)), float(np.mean(a * a)), float(np.mean(b * b))
    var_f, var_g = s_f - 0.25, s_g - 0.25
    denom = math.sqrt(var_f * var_g)
    rho = (t - 0.25) / denom
    d_t = a * b + cx @ b / n + cy @ a / n - 3.0 * t
    d_f = a * a + 2.0 * (cx @ a) / n - 3.0 * s_f
    d_g = b * b + 2.0 * (cy @ b) / n - 3.0 * s_g
    out = np.zeros(xv.shape)
    out[dom] = d_t / denom - 0.5 * rho * (d_f / var_f + d_g / var_g)
    return out, rho


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


def coverage_at(criterion: str, lag1: float) -> dict | None:
    """The D1 coverage rule (plan amendments 5 E2 and 9 I1), or None where none is tabulated.

    ``cov(l) = cov0 + (cov0.3* - cov0) min(1, max(0, l / l_c))`` at 95% and at 1 - 0.05/3, from
    ``l = 0`` (not from the threshold), with the anchor ``cov0.3* = min(cov0, cov0.3)`` so that the
    printed coverage never rises with ``l`` (only H1d at 98.3% has ``cov0.3 > cov0``). Above the
    case value ``l_c`` there is no extrapolation: the coverage is "at most cov0.3*".
    """
    case, table = CASE_VALUE.get(criterion), COVERAGE.get(criterion)
    if case is None or table is None:
        return None
    (c0_95, c0_98), (c3_95, c3_98) = table
    c3_95, c3_98 = min(c0_95, c3_95), min(c0_98, c3_98)  # amendment 9, I1: never above cov0
    frac = min(1.0, max(0.0, lag1 / case))
    return {"fraction": frac, "beyond": bool(lag1 > case),
            "cov95": c0_95 + (c3_95 - c0_95) * frac, "cov983": c0_98 + (c3_98 - c0_98) * frac,
            "bound95": c3_95, "bound983": c3_98}


def acf_reading(criterion: str, lag1: float, n: int) -> tuple[str, dict | None]:
    """The C9 reading of ``acf(1)`` with the E2 coverage (95% and 1 - 0.05/3).

    Returns ``(text, coverage)`` where ``coverage`` is ``coverage_at`` (None: "coverage not
    tabulated", the phi = 0 reading only).
    """
    thr = acf_threshold(n)
    case = CASE_VALUE.get(criterion)
    cov = coverage_at(criterion, lag1)
    if cov is None:
        cov_text = NOT_TABULATED.get(criterion, "coverage not tabulated")
    elif cov["beyond"]:
        cov_text = (f"coverage <= {cov['bound95']:.4f} (95%) / {cov['bound983']:.4f} (98.3%) "
                    "(beyond the tabulated stress)")
    else:
        cov_text = (f"coverage {cov['cov95']:.4f} (95%) / {cov['cov983']:.4f} (98.3%) "
                    f"(interpolated from l = 0 to the case value {case:g})")
    if case is not None and lag1 >= case:
        both = " (both readings hold; the phi = 0.3 reading governs)" if abs(lag1) <= thr else ""
        text = f"phi = 0.3 rows realistic (acf1 >= {case:g}){both}"
    elif abs(lag1) <= thr:
        extra = "" if case is not None else " (no case value for the phi = 0.3 reading)"
        text = f"phi = 0 rows apply (|acf1| <= {thr:g}){extra}"
    elif lag1 > thr:
        text = (f"acf1 above {thr:g}; no case value defined" if case is None else
                f"between the readings (acf1 {lag1:.3f} of the case value {case:g})")
    else:
        text = f"acf1 below -{thr:g}: neither reading applies (negative dependence, reported)"
    return f"{text}; {cov_text}", cov


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
    n_rate: int | None = None
    """Length at which the predicted D2 rate is looked up (None: the series length)."""

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
    """"below 10%", "not below 10%" or "not determined" (limit is ``0.1 hw_full``).

    Raises
    ------
    NotComputable
        If any input is not finite: an infinite half-width (failed resamples put the interval at
        ``(-inf, inf)``) would otherwise read "below 10%", the favourable direction (R1).
    """
    if not all(math.isfinite(v) for v in (bias, se, limit)):
        raise NotComputable(f"non-finite input to the reading (bias {bias}, SE {se}, "
                            f"limit {limit})")
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
    """States near a clip bound: ``min(|u|, |1 - u|) <= factor * s`` (plan amendment 5, E6).

    A state whose unclipped optimum lies far outside [0, 1] (``u = -0.3`` with a small ``s``) is
    not near: its clipped weight does not move with the draw noise.
    """
    return np.minimum(np.abs(u_full), np.abs(1.0 - u_full)) <= factor * half_sd


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
    if not math.isfinite(hw) or not hw > 0.0:
        raise NotComputable(f"half-width not finite and positive: {hw}")
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
    stack: dict | None = None
    """``compare_stack`` of the analysis stack against the run's provenance (None: no comparison,
    read as a different stack)."""

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

    def option_flag(self, kind: str) -> str:
        """" [non-default option: ...]" for a reading that an option changes (plan amendment 5, E8).

        The seed affects every bootstrap and permutation reading, ``--resamples`` the D5 and D6
        ones, ``--permutations`` the D2 one.
        """
        changed = []
        if self.seed != TOOL_SEED:
            changed.append(f"seed {self.seed}")
        if kind in ("d5", "d6") and self.resamples != DEFAULT_RESAMPLES:
            changed.append(f"resamples {self.resamples}")
        if kind == "d2" and self.permutations != DEFAULT_PERMUTATIONS:
            changed.append(f"permutations {self.permutations}")
        return f" [non-default option: {', '.join(changed)}]" if changed else ""

    def group(self, rho: float, n_lib: int) -> str:
        """The sweep group prefix of a cell."""
        return f"sweep/rho={rho:g}|n_lib={n_lib}"


def check(ctx: Context, label: str, mine: float, path: tuple[str, ...], tol: float,
          offset: float = 0.0, scale: float = 0.0) -> None:
    """Compare a recomputed statistic with the results leaf; a MISMATCH is a defect.

    The bound is ``|mine - leaf| <= tol max(|leaf|, scale)``. ``scale`` is the natural size of the
    terms of the statistic (for example ``mean |terms|`` of a mean, ``max(|R^2_3|, |R^2_4|)`` for a
    difference of two R^2, 1 for a correlation), the scale at which a different order of the same
    additions rounds: without it a statistic near 0 that is a difference of larger numbers gets a
    false MISMATCH on correct code (R4: a Delta R^2 of 7e-5 differs from production by about 2e-14
    absolute, 3e-10 relative). ``tol`` is a multiple of the round-off of the terms (1e-12: about
    10^3 additions of unit round-off times a margin of 10; 1e-9 where a least-squares fit or a
    logarithm intervenes). With ``scale = 0`` and ``tol = 0`` the comparison is exact. ``offset`` is
    added to ``mine`` first (H2d is a ratio minus 1). The floor ``tol x scale`` is at most 1e-9 of
    a natural scale, six orders below any real mismatch (a mutation test perturbs by 1e-6).
    """
    try:
        leaf = float(dig(ctx.res, *path))
    except Missing as exc:
        ctx.rep.nc(f"{ctx.system} {label}: reproduction check", str(exc))
        return
    value = mine + offset
    diff = abs(value - leaf)
    allowed = tol * max(abs(leaf), scale)
    ok = bool(diff <= allowed)
    ctx.rep.say(f"  check {label}: dump {value:.12g} vs results {leaf:.12g} "
                f"(|diff| {diff:.2e}, allowed {allowed:.2e} = {tol:g} x max(|leaf|, scale "
                f"{scale:.3g})): {'MATCH' if ok else 'MISMATCH'}")
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
            ctx.rep.uncomputed.append((f"{ctx.system} H2a(ii) {name}", True))
            continue
        check(ctx, f"H2a(ii) {name} partial correlation", r,
              ("H2a", "part_ii", name, "partial_corr"), 1e-9, scale=1.0)
        out.append(Series(ctx.system, "H2a(ii)", name, psi, True, int(dom.sum())))
    return out


def series_h2b_i(ctx: Context) -> list[Series]:
    levels = np.array(sorted(float(r) for r in dig(ctx.cfg, "noise_levels")))
    library = int(dig(ctx.cfg, "core_library"))
    w = np.column_stack([ctx.dump[f"{ctx.group(r, library)}/w_star_href"] for r in levels])
    spear, n_constant = per_state_spearman(levels, w)
    check(ctx, "H2b(i) mean per-state Spearman", float(spear.mean()),
          ("H2b", "noise", "mean_state_spearman"), 1e-12, scale=float(np.mean(np.abs(spear))))
    check(ctx, "H2b(i) constant states (scored 0 by the tie convention)", float(n_constant),
          ("H2b", "noise", "n_constant_states"), 0.0)
    return [Series(ctx.system, "H2b(i)", "", psi_mean(spear), True, len(spear))]


def series_h2b_ii(ctx: Context) -> list[Series]:
    rho = float(dig(ctx.cfg, "core_noise"))
    low, high = (ctx.dump[f"{ctx.group(rho, n)}/w_star_href"] for n in H2B_LIBRARY)
    diff = high - low
    check(ctx, "H2b(ii) mean paired change", float(diff.mean()),
          ("H2b", "library_change", "mean_change"), 1e-12, scale=float(np.mean(np.abs(diff))))
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
        ctx.rep.uncomputed.append((f"{ctx.system} H2c A4-best", False))
    out = []
    for other in others:
        if other not in mse:
            ctx.rep.nc(f"{ctx.system} H2c A4-{other}", f"rule {other} is not a dumped rule")
            ctx.rep.uncomputed.append((f"{ctx.system} H2c A4-{other}", False))
            continue
        diff = mse["A4"] - mse[other]
        check(ctx, f"H2c A4-{other} mean", float(diff.mean()),
              ("H2c", f"A4_minus_{other}", "mean"), 1e-12, scale=float(np.mean(np.abs(diff))))
        out.append(Series(ctx.system, "H2c", f"A4-{other}", psi_mean(diff), False, len(diff)))
    return out


def series_h2d(ctx: Context) -> list[Series]:
    a4, a3 = (ctx.dump[f"core/state_mse/{r}"][:, ctx.ref] for r in ("A4", "A3"))
    check(ctx, "H2d A4/A3 - 1", float(a4.mean() / a3.mean()), ("H2d", "in_distribution_excess"),
          1e-12, offset=-1.0, scale=float(a4.mean() / a3.mean()))
    return [Series(ctx.system, "H2d", "", psi_ratio(a4, a3), False, len(a4))]


def series_h2e(ctx: Context) -> list[Series]:
    out = []
    for rho in dig(ctx.cfg, "library_sweep_noises"):
        low, high = (ctx.dump[f"{ctx.group(float(rho), n)}/err_corr_href"] for n in H2E_LIBRARY)
        diff = high - low
        check(ctx, f"H2e rho={rho:g} median change", float(np.median(diff)),
              ("H2e", "by_noise", f"{float(rho):g}", "median_change"), 1e-12,
              scale=float(np.mean(np.abs(diff))))
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
                ctx.rep.uncomputed.append((f"{ctx.system} Q-N {kind} {target}", False))
                continue
            yd = y[dom]
            sst = float(np.sum((yd - yd.mean()) ** 2))
            ss3, ss4 = (float(np.sum((yd - p[dom]) ** 2)) / sst for p in (p3, p4))
            # the terms of R^2_4 - R^2_3 = (1 - ss4) - (1 - ss3) are ss3 and ss4 (fractions of
            # SST) and 1: their round-off is of the size ss/SST even when both R^2 are near 0
            # (R15); the scale is the largest of them
            r2_size = max(abs(1.0 - ss3), abs(1.0 - ss4), ss3, ss4)
            check(ctx, f"Q-N {kind} {target} delta R^2", delta,
                  ("Q-N", kind, target, "delta_r2"), 1e-12, scale=r2_size)
            out.append(Series(ctx.system, "Q-N", f"{kind} {target}", psi, False, int(dom.sum())))
    return out


def spearman_tiebreak_interval(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """The range of Spearman(x, y) over all ways of breaking the ties of ``x``.

    The extreme orders sort each tied group of ``x`` by ``y``, ascending for the maximum and
    descending for the minimum (the rearrangement inequality: the correlation of the ranks is
    largest when equal ``x`` are ordered like ``y``). The ties of ``y`` are real and keep mid-ranks.
    """
    out = []
    for sign in (-1.0, 1.0):
        order = np.lexsort((sign * y, x))
        ranks = np.empty(len(x))
        ranks[order] = np.arange(len(x))
        out.append(float(sps.spearmanr(ranks, y).statistic))
    return min(out), max(out)


def h1d_reproduction(rho: float, leaf: float, interval: tuple[float, float] | None,
                     allowed: float) -> str:
    """``match`` (``|rho - leaf| <= allowed``), ``tie_bound`` (differs, but the stored column has
    ties and the leaf lies inside the tie-break interval) or ``mismatch``."""
    if abs(rho - leaf) <= allowed:
        return "match"
    if interval is not None and interval[0] <= leaf <= interval[1]:
        return "tie_bound"
    return "mismatch"


def check_spearman_ties(ctx: Context, label: str, rho: float, proxy: np.ndarray, truth: np.ndarray,
                        path: tuple[str, ...], scale: float) -> None:
    """The H1d reproduction check with the tie rule of the R1 finding (fix round 5).

    A profile transform such as ``log(N-hat + c)`` can create ties that the raw array of production
    does not have, so the stored column cannot reproduce the leaf exactly. If the exact comparison
    fails and the stored column has ties, the leaf is compared with the Spearman interval over all
    tie-breaks: inside is "not computable exactly" (exit 2, never a pass), outside a MISMATCH. With
    no ties the comparison is exact as before.
    """
    try:
        leaf = float(dig(ctx.res, *path))
    except Missing as exc:
        ctx.rep.nc(f"{ctx.system} {label}: reproduction check", str(exc))
        return
    allowed = 1e-12 * max(abs(leaf), scale)
    interval = None
    if abs(rho - leaf) > allowed and len(np.unique(proxy)) < len(proxy):
        interval = spearman_tiebreak_interval(proxy, truth)
    verdict = h1d_reproduction(rho, leaf, interval, allowed)
    diff = abs(rho - leaf)
    tail = {"match": "MATCH", "mismatch": "MISMATCH",
            "tie_bound": "NOT COMPUTABLE EXACTLY (the transform created ties)"}[verdict]
    bound = f"; tie-break interval [{interval[0]:.9f}, {interval[1]:.9f}]" if interval else ""
    ctx.rep.say(f"  check {label}: dump {rho:.12g} vs results {leaf:.12g} (|diff| {diff:.2e}, "
                f"allowed {allowed:.2e}{bound}): {tail}")
    if verdict == "mismatch":
        ctx.rep.defects.append(f"{ctx.system} {label}: dump {rho!r} vs results {leaf!r}")
    elif verdict == "tie_bound":
        ctx.rep.nc(f"{ctx.system} {label}", f"not computable exactly: the transform created ties; "
                   f"leaf within [{interval[0]:.9f}, {interval[1]:.9f}] (dump {rho:.9f}, leaf {leaf:.9f})")


def series_h1d(ctx: Context) -> list[Series]:
    """H1d: Spearman of each deployable proxy (first evaluation draw) with its oracle.

    The proxies enter ``core/profile[:, 0, k]`` through strictly increasing transforms (``log(x/rho)``
    for the two seeds, ``x steps_per_lyapunov`` for the growth, ``log(x + c)`` for N-hat), which
    leave every rank, tie and Spearman correlation unchanged. A proxy that is finite but maps to
    a non-finite profile entry (``log 0``) is excluded here and not in production: the exclusion
    counts are compared with the results, so that case is a MISMATCH, never silent.
    """
    d = ctx.dump
    profile = d["core/profile"]
    if profile.ndim != 3 or profile.shape[2] != 4:
        raise NotComputable(f"core/profile has shape {profile.shape}, not (n, E, 4)")
    out = []
    for name, column, oracle in H1D_ROWS:
        proxy, truth = profile[:, 0, column], d[f"core/{oracle}"]
        keep = np.isfinite(proxy) & np.isfinite(truth)
        try:
            psi, rho = psi_spearman(proxy, truth, keep)
        except NotComputable as exc:
            ctx.rep.nc(f"{ctx.system} H1d {name}", str(exc))
            ctx.rep.uncomputed.append((f"{ctx.system} H1d {name}", False))
            continue
        check_spearman_ties(ctx, f"H1d {name} Spearman", rho, proxy[keep], truth[keep],
                            ("H1d", "rows", name, "spearman"), scale=1.0 / math.sqrt(int(keep.sum())))
        check(ctx, f"H1d {name} states excluded as non-finite", float((~keep).sum()),
              ("H1d", "rows", name, "n_excluded_nonfinite"), 0.0)
        out.append(Series(ctx.system, "H1d", name, psi, False, int(keep.sum())))
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
    check(ctx, "H1b PLP slope", slope, ("H1b", "PLP", "slope"), 1e-9,
          scale=float(np.std(y[keep]) / np.std(x[keep])))
    check(ctx, "H1b PLP states excluded as non-finite", float((~keep).sum()),
          ("H1b", "PLP", "n_excluded_nonfinite"), 0.0)
    check(ctx, "H1b PLP states where the floor binds", float((e_p[keep] < 1e-12).sum()),
          ("H1b", "PLP", "n_floored"), 0.0)
    return [Series(ctx.system, "H1b", "PLP", psi, False, int(keep.sum()))]


# --------------------------------------------------------------------------------------------
# the analysis stack against the run's provenance (plan amendment 10, J2)
# --------------------------------------------------------------------------------------------
STACK_ENV = ("OPENBLAS_CORETYPE", "NPY_DISABLE_CPU_FEATURES")


def stack_record() -> dict:
    """The stack fields of this process, from the same ``lpcstudy.provenance`` functions the run used."""
    import os
    import platform

    from lpcstudy import provenance as pv  # imports jax: needed only for this record
    return {"python": platform.python_version(), "packages": pv._package_versions(),
            "cpu": pv.cpu_record(), "blas": pv.blas_record(), "numpy_simd": pv.simd_record(),
            "env": {name: os.environ.get(name) for name in pv.ENV_NAMES}}


def _usable(block: object, *path: str) -> tuple[object, bool]:
    """A provenance field and whether it is usable: present, not null, and its block has no error."""
    node = block
    for key in path:
        if not isinstance(node, dict) or key not in node:
            return None, False
        node = node[key]
    return node, node is not None


def _stack_fields(prov: dict) -> dict[str, tuple[object, bool]]:
    """The compared fields of one provenance block: ``{name: (value, usable)}``."""
    out: dict[str, tuple[object, bool]] = {}
    out["python"] = _usable(prov, "python")
    for pkg in ("numpy", "scipy"):
        out[f"packages.{pkg}"] = _usable(prov, "packages", pkg)
    cpu_ok = isinstance(prov.get("cpu"), dict) and prov["cpu"].get("error") is None
    for key in ("model", "isa"):
        value, ok = _usable(prov, "cpu", key)
        out[f"cpu.{key}"] = (tuple(value) if isinstance(value, list) else value, ok and cpu_ok)
    blas = prov.get("blas")
    libs = blas.get("libraries") if isinstance(blas, dict) else None
    blas_ok = (isinstance(blas, dict) and blas.get("error") is None and isinstance(libs, list)
               and len(libs) > 0 and all(isinstance(e, dict) and e.get("error") is None for e in libs))
    out["blas.libraries"] = (tuple((e.get("library"), e.get("corename")) for e in libs)
                             if isinstance(libs, list) else None, blas_ok)
    simd = prov.get("numpy_simd")
    found = simd.get("found") if isinstance(simd, dict) else None
    out["numpy_simd.found"] = (tuple(found) if isinstance(found, list) else None,
                               isinstance(simd, dict) and simd.get("error") is None
                               and isinstance(found, list))
    env = prov.get("env")
    for name in STACK_ENV:  # an unset variable is recorded as null: present and null is a value
        present = isinstance(env, dict) and name in env
        out[f"env.{name}"] = (env.get(name) if present else None, present)
    return out


def compare_stack(run_prov: dict, own: dict) -> dict:
    """Compare the analysis stack with the run's provenance field by field (amendment 10, J2).

    A field that is missing, null, or recorded with a non-null ``error`` on either side counts as
    different (an environment variable recorded as null is a value: unset). Returns ``{"same":
    bool, "rows": [(field, run value, own value, status)]}`` with status ``same``, ``different``
    or ``unusable``.
    """
    a, b = _stack_fields(run_prov), _stack_fields(own)
    rows = []
    for name in a:
        (va, ok_a), (vb, ok_b) = a[name], b[name]
        status = "unusable" if not (ok_a and ok_b) else ("same" if va == vb else "different")
        rows.append((name, va, vb, status))
    return {"same": all(r[3] == "same" for r in rows), "rows": rows}


def fit_rule(mine: float, leaf: float, same_stack: bool, scale: float) -> str:
    """The three branches for a fit-derived leaf: ``match``, ``mismatch`` or ``needs_stack``.

    Same stack: bitwise. Different stack: within ``4e-5 scale`` (the a-priori bound for a pair of
    correct fits, the constant of ``REFIT_TOLERANCE``) the bitwise reproduction cannot be judged
    (``needs_stack``: never a pass); beyond it a MISMATCH. The bound is inclusive.
    """
    if same_stack:
        return "match" if _bits(float(mine)) == _bits(float(leaf)) else "mismatch"
    return "needs_stack" if abs(float(mine) - float(leaf)) <= REFIT_TOLERANCE * scale else "mismatch"


def check_fit(ctx: Context, label: str, mine: float, path: tuple[str, ...], scale: float) -> None:
    """Reproduce a leaf that comes from the production fit, by ``fit_rule`` (J2)."""
    try:
        leaf = float(dig(ctx.res, *path))
    except Missing as exc:
        ctx.rep.nc(f"{ctx.system} {label}: reproduction check", str(exc))
        return
    same = bool(ctx.stack and ctx.stack.get("same"))
    verdict = fit_rule(mine, leaf, same, scale)
    diff = abs(mine - leaf)
    stack_text = "same stack: bitwise" if same else (
        f"different stack: bound {REFIT_TOLERANCE:g} x {scale:.4g} = {REFIT_TOLERANCE * scale:.3g}")
    ctx.rep.say(f"  check {label}: dump {mine:.12g} vs results {leaf:.12g} (|diff| {diff:.2e}; "
                f"{stack_text}): "
                + {"match": "MATCH", "mismatch": "MISMATCH",
                   "needs_stack": "NOT COMPUTABLE (bitwise reproduction needs the run's stack)"}[verdict])
    if verdict == "mismatch":
        ctx.rep.defects.append(f"{ctx.system} {label}: dump {mine!r} vs results {leaf!r}")
    elif verdict == "needs_stack":
        ctx.rep.nc(f"{ctx.system} {label}", f"bitwise reproduction needs the run's stack (|diff| "
                   f"{diff:.2e} is within {REFIT_TOLERANCE:g} x {scale:.4g})")


# --------------------------------------------------------------------------------------------
# H1a and H1c (row .8c; plan amendment 6 F1, F2; MA-1)
# --------------------------------------------------------------------------------------------
def production_model(log_n: np.ndarray, log_c2: float, exponent: float, log_f2: float) -> np.ndarray:
    """``log(c^2 n^-b + f^2)``: the floor power law of ``analysis._floor_power_law``, verbatim."""
    return np.log(np.exp(log_c2) * np.exp(log_n) ** (-exponent) + np.exp(log_f2))


def production_fit(sizes: np.ndarray, medians: np.ndarray) -> np.ndarray:
    """The production H1a fit (``analysis._fit_seed_law``: ``curve_fit``, TRF, default tolerances,
    2-point Jacobian, the same guess and bounds), returning all three parameters.

    Raises
    ------
    NotComputable
        If the fit does not converge or meets a non-finite residual.
    """
    log_n = np.log(sizes)
    guess = (np.log(medians[0]) + 2 * 0.5 * log_n[0], 1.0, np.log(medians[-1] * 0.5))
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", OptimizeWarning)
            params, _ = curve_fit(production_model, log_n, np.log(medians), p0=guess,
                                  bounds=([-50, H1A_BOUNDS[0], -60], [50, H1A_BOUNDS[1], 10]),
                                  maxfev=20_000)
    except (RuntimeError, ValueError) as exc:
        raise NotComputable(f"the production fit failed: {exc}") from exc
    return np.asarray(params, dtype=float)


def h1a_fraction(log_n: np.ndarray, theta: np.ndarray) -> np.ndarray:
    """``p = e^(a - b x)/(e^(a - b x) + e^c)``, the share of the power-law term."""
    return 1.0 / (1.0 + np.exp(theta[2] - (theta[0] - theta[1] * log_n)))


def h1a_jacobian(log_n: np.ndarray, theta: np.ndarray) -> np.ndarray:
    """``dg/d(a, b, c) = (p, -x p, 1 - p)`` of ``g = log(e^(a - b x) + e^c)``."""
    p = h1a_fraction(log_n, theta)
    return np.column_stack([p, -log_n * p, 1.0 - p])


def h1a_residual(log_n: np.ndarray, y: np.ndarray, theta: np.ndarray) -> np.ndarray:
    """``g(x; theta) - y`` computed stably (``logaddexp``)."""
    return np.logaddexp(theta[0] - theta[1] * log_n, theta[2]) - y


def h1a_hessian(log_n: np.ndarray, y: np.ndarray, theta: np.ndarray, curvature: bool = True
                ) -> np.ndarray:
    """The exact Hessian of ``F = 1/2 sum (g_j - y_j)^2``: ``J^T J + sum r_j p_j (1 - p_j) v_j v_j^T``
    with ``v = (1, -x, -1)``. ``curvature=False`` drops the second term (the Gauss-Newton form,
    24% wrong on a pilot cell: it exists for the mutation test a5 only)."""
    jac = h1a_jacobian(log_n, theta)
    hess = jac.T @ jac
    if curvature:
        p = h1a_fraction(log_n, theta)
        v = np.column_stack([np.ones_like(log_n), -log_n, -np.ones_like(log_n)])
        hess = hess + (v * (h1a_residual(log_n, y, theta) * p * (1.0 - p))[:, None]).T @ v
    return hess


def h1a_fit_tight(log_n: np.ndarray, y: np.ndarray, x0: np.ndarray) -> np.ndarray:
    """The minimiser to machine precision: TRF with the analytic Jacobian (tolerances 1e-15), then
    Newton steps on the gradient with the exact Hessian until the step is below 1e-15 relative."""
    res = least_squares(lambda t: h1a_residual(log_n, y, t), np.asarray(x0, float),
                        jac=lambda t: h1a_jacobian(log_n, t), method="trf",
                        bounds=(H1A_LO, H1A_HI), ftol=1e-15, xtol=1e-15, gtol=1e-15,
                        max_nfev=20_000)
    theta = res.x.copy()
    for _ in range(20):
        grad = h1a_jacobian(log_n, theta).T @ h1a_residual(log_n, y, theta)
        try:
            step = np.linalg.solve(h1a_hessian(log_n, y, theta), grad)
        except np.linalg.LinAlgError as exc:
            raise NotComputable("the Hessian of the refit is singular (the floor or the exponent "
                                "is not identified by the five medians)") from exc
        theta = theta - step
        if np.max(np.abs(step) / np.maximum(1.0, np.abs(theta))) < 1e-15:
            break
    return theta


def h1a_fit_weights(sizes: np.ndarray, medians: np.ndarray, theta: np.ndarray,
                    curvature: bool = True) -> dict:
    """``A_j = (1/2) [H^-1 J^T]_{b, j}``: the response of ``1/d_fit = b/2`` to ``log m_j``.

    Raises
    ------
    NotComputable
        If ``lambda_min(H) <= 0`` or ``cond(H) > 1e8`` (hypothesis H-d of MA-1).
    """
    log_n, y = np.log(sizes), np.log(medians)
    hess = h1a_hessian(log_n, y, theta, curvature)
    eig = np.linalg.eigvalsh(hess)
    cond = float(np.linalg.cond(hess))
    if not eig[0] > 0.0:
        raise NotComputable(f"the Hessian is not positive definite (lambda_min {eig[0]:.3g})")
    if not cond <= HESSIAN_COND_MAX:
        raise NotComputable(f"the Hessian is ill conditioned (cond {cond:.3g} > 1e8)")
    weights = 0.5 * np.linalg.solve(hess, h1a_jacobian(log_n, theta).T)[1]
    return {"A": weights, "cond": cond, "lambda_min": float(eig[0])}


def sbg_density(log_values: np.ndarray) -> float:
    """Siddiqui-Bloch-Gastwirth density of the values at their median, Hall-Sheather bandwidth.

    ``h = 0.97157 n^(-1/3)``, ``1/g = (Q(1/2 + h) - Q(1/2 - h))/(2h)`` with numpy's default quantile.

    Raises
    ------
    NotComputable
        If there are fewer than ``H1A_MIN_STATES`` values (``1/2 +- h`` must stay inside (0, 1)) or
        the spread is not positive.
    """
    n = len(log_values)
    if n < H1A_MIN_STATES:
        raise NotComputable(f"{n} states are too few for the density bandwidth (need {H1A_MIN_STATES})")
    h = HALL_SHEATHER * n ** (-1.0 / 3.0)
    high, low = np.quantile(log_values, [0.5 + h, 0.5 - h])
    if not high - low > 0.0:
        raise NotComputable("the density spread of a column is zero")
    return 2.0 * h / float(high - low)


def sign_type(x: np.ndarray, m: np.ndarray) -> np.ndarray:
    """``1/2 - 1{x < m} - 1/2 1{x = m}``: the influence of a median up to ``1/f`` (+1/2 above)."""
    return 0.5 - (x < m) - 0.5 * (x == m)


def h1a_psi(seed_sq: np.ndarray, inverse_dim: np.ndarray, medians: np.ndarray, mu: float,
            weights: np.ndarray, density: np.ndarray, ratio: float) -> np.ndarray:
    """``psi_i = [sum_j A_j s_ij/g_j - R (v_i - mu)]/mu`` (MA-1 section 0); rows are the kept states."""
    return (sign_type(seed_sq, medians[None, :]) @ (weights / density)
            - ratio * (inverse_dim - mu)) / mu


def h1a_cell(seed_sq: np.ndarray, inverse_dim: np.ndarray, sizes: np.ndarray, ci_scale: float,
             at_bound_leaf: int | None = 0, production: Callable = production_fit) -> dict:
    """The H1a series of one rho on the compacted kept states, or ``NotComputable`` with the reason.

    The conditions (plan amendment 6 F1): the exponent at a bound (the leaf flag or the recomputed
    fit); the tight refit differing from the production fit by more than ``4e-5 ci_scale``
    (``max(|lo|, |hi|)`` of ``ci_inverse_dim``; the difference is printed in the reason);
    ``lambda_min(H) <= 0`` or ``cond(H) > 1e8``; a zero density spread; too few states.
    """
    medians = np.median(seed_sq, axis=0)
    if not np.all(np.isfinite(medians) & (medians > 0)):
        raise NotComputable("a column median is not positive and finite")
    params = production(sizes, medians)
    two_over_d = float(params[1])
    if (at_bound_leaf or 0) == 1 or min(abs(two_over_d - b) for b in H1A_BOUNDS) <= H1A_BOUND_TOL:
        raise NotComputable("exponent at a bound")
    fitted = two_over_d / 2.0
    log_n, y = np.log(sizes), np.log(medians)
    theta = h1a_fit_tight(log_n, y, params)
    diff = abs(theta[1] / 2.0 - fitted)
    if diff > REFIT_TOLERANCE * ci_scale:
        raise NotComputable(f"refit differs: |b*/2 - fitted_inverse_dim| = {diff:.3g} > "
                            f"{REFIT_TOLERANCE:g} x {ci_scale:.3g}")
    fit = h1a_fit_weights(sizes, medians, theta)
    density = np.array([sbg_density(np.log(seed_sq[:, j])) for j in range(seed_sq.shape[1])])
    mu = float(inverse_dim.mean())
    ratio = fitted / mu
    psi = h1a_psi(seed_sq, inverse_dim, medians, mu, fit["A"], density, ratio)
    return {"psi": psi, "A": fit["A"], "g": density, "theta": theta, "fitted": fitted, "mu": mu,
            "ratio": ratio, "cond": fit["cond"], "lambda_min": fit["lambda_min"],
            "medians": medians, "refit_diff": diff}


def series_h1a(ctx: Context) -> list[Series]:
    """H1a per rho: reproduction checks, then the influence series (primary: F3 counts it)."""
    d, rep = ctx.dump, ctx.rep
    levels, sizes, inverse_all = d["h1a/noise_levels"], d["h1a/n_lib"], d["h1a/inverse_dim"]
    raw = {float(r): d[f"h1a/rho={float(r):g}/seed_sq"] for r in levels}
    keep = np.isfinite(inverse_all)
    for sq in raw.values():
        keep &= np.all(np.isfinite(sq), axis=1)
    n_rate, n_keep = len(inverse_all), int(keep.sum())
    inverse = inverse_all[keep]
    shared_before = len(rep.defects)
    check(ctx, "H1a states kept", float(n_keep), ("H1a", "n_states"), 0.0)
    check(ctx, "H1a states excluded as non-finite", float(n_rate - n_keep),
          ("H1a", "n_excluded_nonfinite"), 0.0)
    nu = n_keep * 2.0**-53
    check(ctx, "H1a inverse_dim_reference (gamma_n)",
          float(inverse.mean()) if n_keep else float("nan"), ("H1a", "inverse_dim_reference"),
          nu / (1.0 - nu))
    if len(rep.defects) > shared_before:  # a shared input is not reproduced: no H1a reading
        for rho in raw:
            rep.uncomputed.append((f"{ctx.system} H1a rho={rho:g}", True))
        rep.say("  H1a: a shared reproduction check failed; no H1a series is used")
        return []
    out = []
    for rho, sq_all in raw.items():
        g = f"{rho:g}"
        where = f"{ctx.system} H1a rho={g}"
        before = len(rep.defects)
        sq = sq_all[keep]
        medians = np.median(sq, axis=0) if n_keep else np.full(len(sizes), np.nan)
        for j, n_lib in enumerate(sizes):
            check(ctx, f"H1a rho={g} median_seed_by_n_lib {int(n_lib)}", float(np.sqrt(medians[j])),
                  ("H1a", "by_noise", g, "median_seed_by_n_lib", str(int(n_lib))), 0.0)
        got = attempt(rep, where, _h1a_one, ctx, g, sq, inverse, sizes)
        if len(rep.defects) > before:
            rep.uncomputed.append((where, True))
            continue
        if got is None:
            rep.uncomputed.append((where, True))
            continue
        out.append(Series(ctx.system, "H1a", f"rho={g}", got["psi"], True, n_keep, n_rate=n_rate))
    return out


def _h1a_one(ctx: Context, g: str, sq: np.ndarray, inverse: np.ndarray, sizes: np.ndarray) -> dict:
    ci = dig(ctx.res, "H1a", "by_noise", g, "ci_inverse_dim")
    ci_scale = max(abs(float(ci[0])), abs(float(ci[1])))
    if not math.isfinite(ci_scale) or ci_scale == 0.0:
        raise NotComputable(f"ci_inverse_dim not finite and non-zero: {ci}")
    flag = int(dig(ctx.res, "H1a", "by_noise", g, "n_exponent_at_bound", "point"))
    cell = h1a_cell(sq, inverse, sizes, ci_scale, flag)
    check_fit(ctx, f"H1a rho={g} fitted_inverse_dim (production fit)", cell["fitted"],
              ("H1a", "by_noise", g, "fitted_inverse_dim"), ci_scale)
    rci = dig(ctx.res, "H1a", "by_noise", g, "ratio_ci")
    ratio_scale = max(abs(float(rci[0])), abs(float(rci[1])))
    check_fit(ctx, f"H1a rho={g} ratio", cell["ratio"], ("H1a", "by_noise", g, "ratio"),
              ratio_scale if math.isfinite(ratio_scale) and ratio_scale > 0 else ci_scale)
    psi, n = cell["psi"], len(cell["psi"])
    se_iid = float(np.std(psi, ddof=1)) / math.sqrt(n)
    se_mbb = math.sqrt(block_variance(psi, 5) / n)
    ref = (float(rci[1]) - float(rci[0])) / 3.92
    ctx.rep.say(f"  H1a rho={g}: cond(H) {cell['cond']:.3g}, lambda_min {cell['lambda_min']:.3g}, "
                f"refit difference {cell['refit_diff']:.2g}; information: SE_iid of psi {se_iid:.4f}, "
                f"SE_MBB5 {se_mbb:.4f} against (hi - lo)/3.92 of ratio_ci {ref:.4f}")
    return cell


def series_h1c(ctx: Context) -> list[Series]:
    """H1c, PLP and CP: the sign-type series of the eligible, finite ratios in time order (compacted)."""
    d, out = ctx.dump, []
    for name in ("PLP", "CP"):
        ratio, eligible = d[f"h1c/{name}/ratio"], d[f"h1c/{name}/eligible"].astype(bool)
        kept = ratio[eligible & np.isfinite(ratio)]
        check(ctx, f"H1c {name} states kept", float(kept.size), ("H1c", name, "n_states"), 0.0)
        check(ctx, f"H1c {name} ineligible states", float((~eligible).sum()),
              ("H1c", name, "n_ineligible_states"), 0.0)
        check(ctx, f"H1c {name} states excluded as non-finite",
              float((eligible & ~np.isfinite(ratio)).sum()),
              ("H1c", name, "n_excluded_nonfinite"), 0.0)
        if kept.size < 10:
            ctx.rep.nc(f"{ctx.system} H1c {name}", f"{kept.size} eligible finite ratios; the "
                       "production reports no median below 10")
            ctx.rep.uncomputed.append((f"{ctx.system} H1c {name}", False))
            continue
        check(ctx, f"H1c {name} median ratio", float(np.median(kept)), ("H1c", name, "median_ratio"), 0.0)
        out.append(Series(ctx.system, "H1c", name, psi_sign(kept), False, int(kept.size)))
    return out


SERIES_BUILDERS: tuple[tuple[str, Callable[[Context], list[Series]]], ...] = (
    ("H2a(i)", series_h2a_i), ("H2a(ii)", series_h2a_ii), ("H2b(i)", series_h2b_i),
    ("H2b(ii)", series_h2b_ii), ("H3c", series_h3c), ("H2c", series_h2c), ("H2d", series_h2d),
    ("H2e", series_h2e), ("Q-N", series_qn), ("H1b", series_h1b), ("H1d", series_h1d),
    ("H1a", series_h1a), ("H1c", series_h1c))


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
        else:
            rep.uncomputed.append((f"{ctx.system} {name}", name in PRIMARY_CRITERIA))
    rep.say(f"D1 influence series and autocorrelation, {ctx.system} "
            f"(P = primary; lags 1 to {LAGS}; rule 0.15 for n <= 500, 0.11 above)")
    rows: dict = {}
    for s in series:
        try:
            lags = acf(s.values)
        except NotComputable as exc:
            rep.nc(f"{ctx.system} {s.name} acf", str(exc))
            rep.uncomputed.append((f"{ctx.system} {s.name}", s.primary))
            continue
        text, cov = acf_reading(s.criterion, float(lags[0]), s.n)
        if s.criterion == "H2a(ii)" and s.part in ("zero", "one"):
            text += "; C7 borrowed (indicator part)"
        rep.say(f"  {s.name:28s} n={s.n:5d} domain={s.domain:5d} {'P' if s.primary else '-'} "
                + " ".join(f"{a:+.3f}" for a in lags))
        rep.say(f"      reading: {text}; P(|acf1| > {acf_threshold(s.n):g} | no dependence) "
                f"= {lag_zero_false_trigger(s.n):.4f}")
        rows[s.name] = {"n": s.n, "domain": s.domain, "primary": s.primary, "acf": lags.tolist(),
                        "reading": text, "coverage": cov}
        rep.series_log.append({"system": ctx.system, "name": s.name, "n": s.n,
                               "n_rate": s.n_rate, "primary": s.primary, "acf1": float(lags[0]),
                               "within": bool(abs(lags[0]) <= acf_threshold(s.n)), "fires": None})
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
            rep.uncomputed.append((f"{ctx.system} {s.name} (D2)", s.primary))
            continue
        lags = np.array(rows[s.name]["acf"])
        beta = beta_reading(lags, s.n)
        n_rate = s.n_rate or s.n
        null_rate = UNION_NULL.get(n_rate)
        rate_text = ("not tabulated for this n" if null_rate is None else
                     f"{null_rate:.3f} under no dependence; {UNION_STRESS[n_rate]:.3f} at phi = 0.3")
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
        for entry in rep.series_log:
            if entry["system"] == ctx.system and entry["name"] == s.name:
                entry["fires"] = bool(summary["fires"])
        if s.primary:
            fires += summary["fires"]
            beta_fires += beta["fires"]
    rep.data.setdefault(ctx.system, {})["D2"] = d2
    prim = [s for s in primaries if s.name in d2]
    rates = [UNION_NULL.get(s.n_rate or s.n) for s in prim]
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
    governing = None if perm is None else bool(perm["fires"])
    rep.data.setdefault(ctx.system, {})["D2_any_reading_fired"] = any_fire
    rep.data[ctx.system]["D2_governing_reading"] = "pooled permutation (OF-3)"
    rep.data[ctx.system]["D2_design_question"] = governing
    gaps = [name for name, primary in rep.uncomputed
            if primary and name.startswith(ctx.system + " ")]
    if perm is None:
        gaps.append(f"{ctx.system} permutation null")
    gap_text = f"; not computed: {', '.join(gaps)}" if gaps else ""
    info = (f"A5 rule fired on {fires} of {len(prim)} primary series, beta5 on {beta_fires} of "
            f"{len(prim)}")
    if governing:
        text = ("block length 5 is a design question (the pooled permutation reading fired; it "
                "governs, OF-3; the A5 rule and beta5 are information, not governing: " + info + ")"
                + gap_text)
    elif not prim:
        text = "not determined (no D2 reading was computed)" + gap_text
    elif governing is None:
        text = ("not determined (the governing pooled permutation reading was not computed; "
                "information, not governing: " + info + ")" + gap_text)
    elif fires or beta_fires:
        text = ("no design question on the governing reading (the pooled permutation did not fire); "
                "information, not governing: " + info
                + (f"; not computed: {', '.join(gaps)}" if gaps else ""))
    elif gaps:
        text = f"no reading fired among the computed readings{gap_text}"
    else:
        text = "no reading fired"
    rep.data[ctx.system]["D2_owner_flag"] = text
    rep.say("  D2 owner flag, " + ctx.system + ": " + text + ctx.option_flag("d2"))
    attempt(rep, f"{ctx.system} block-sensitive label", _block_sensitivity_lines, ctx, series)
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
            f"{q99:+.4f}, one-sided p {p:.4f}: {'DESIGN QUESTION' if fires else 'no'}"
            + ctx.option_flag("d2"))
    return {"observed": obs, "q99": q99, "p": p, "fires": fires, "n_series": len(usable)}


def verdict_leaves(s: Series) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    """Results paths of the point estimate, the interval and the recorded verdict of a primary part.

    Raises
    ------
    NotComputable
        If the series is not a part with a verdict rule (not one of the six primary criteria).
    """
    c, part = s.criterion, s.part
    if c == "H2a(i)":
        return ("H2a", "median_range"), ("H2a", "range_ci"), ("H2a", "part_i_verdict")
    if c == "H2a(ii)":
        base = ("H2a", "part_ii", part)
        return base + ("partial_corr",), base + ("ci",), base + ("verdict",)
    if c in ("H2b(i)", "H2b(ii)"):
        base, stat = (("H2b", "noise"), "mean_state_spearman") if c == "H2b(i)" else (
            ("H2b", "library_change"), "mean_change")
        return base + (stat,), base + ("ci",), base + ("verdict",)
    if c == "H3c":
        return ("H3c", "A5_over_A4_mse"), ("H3c", "ci"), ("H3c", "verdict")
    if c == "H1a" and part.startswith("rho="):
        base = ("H1a", "by_noise", part[len("rho="):])
        return base + ("ratio",), base + ("ratio_ci",), base + ("verdict",)
    raise NotComputable(f"no verdict rule for {s.name}")


def widen_interval(point: float, lower: float, upper: float, factor: float) -> tuple[float, float]:
    """Each side of an interval scaled about its point estimate: ``point -+ factor x (side length)``."""
    return point - factor * (point - lower), point + factor * (upper - point)


def block_sensitivity(ctx: Context, s: Series) -> dict:
    """Would widening the half-width by ``sqrt(max(1, V*(10)/V*(5)))`` change the part's verdict?

    First order (the half-width of a block-bootstrap interval of an asymptotically linear
    statistic goes as ``sqrt(V*(b))`` of its own influence series). The verdict of the recorded
    interval is recomputed with the production rule and must equal the recorded one; the widened
    interval is then read with the same rule and the same ``n_states`` (the part's domain).
    Report-only: nothing here changes a number, a verdict or the exit code.

    Raises
    ------
    NotComputable
        If a leaf is absent or not finite, V*(5) is not positive, the part has no verdict rule, or
        the recomputed baseline verdict differs from the recorded one.
    """
    rule = VERDICT_RULES.get(s.criterion)
    if rule is None:
        raise NotComputable(f"no verdict rule for {s.name}")
    band, closed = rule
    ratio = variance_summary(s.values)["ratio10"]
    factor = math.sqrt(max(1.0, ratio))
    point_path, interval_path, verdict_path = verdict_leaves(s)
    try:
        point = float(dig(ctx.res, *point_path))
        lower, upper = (float(x) for x in dig(ctx.res, *interval_path))
    except (TypeError, ValueError) as exc:
        raise NotComputable(f"point or interval of {s.name} is not a number: {exc}") from exc
    recorded = str(dig(ctx.res, *verdict_path))
    if not math.isfinite(point) or math.isnan(lower) or math.isnan(upper) or lower > upper:
        raise NotComputable(f"point {point!r} or interval [{lower!r}, {upper!r}] of {s.name} is "
                            "not usable")
    base, _ = criterion_verdict(point, lower, upper, band, closed, n_states=s.domain)
    if base != recorded:
        raise NotComputable(f"the verdict recomputed from the interval ({base}) differs from the "
                            f"recorded one ({recorded})")
    wide_lower, wide_upper = widen_interval(point, lower, upper, factor)
    wide, _ = criterion_verdict(point, wide_lower, wide_upper, band, closed, n_states=s.domain)
    return {"point": point, "interval": [lower, upper], "ratio10": ratio, "factor": factor,
            "verdict": base, "widened_interval": [wide_lower, wide_upper],
            "widened_verdict": wide, "sensitive": bool(wide != base), "reason": None}


def _block_sensitivity_lines(ctx: Context, series: list[Series]) -> None:
    """The report-only block-sensitive label of every primary part of one system."""
    rep = ctx.rep
    rep.say(f"Block-sensitive label, {ctx.system} (report-only: each primary interval widened on each "
            "side by sqrt(max(1, V*(10)/V*(5))) of its own series; a verdict that changes is "
            "BLOCK-SENSITIVE; no criterion, verdict, number or exit code changes)")
    built = {f"{ctx.system} {s.name}" for s in series}
    unbuilt = [name for name, primary in rep.uncomputed
               if primary and name.startswith(ctx.system + " ") and name not in built
               and not name.endswith("(D2)")]
    rows: dict[str, dict] = {}
    for s in series:
        if not s.primary:
            continue
        try:
            row = block_sensitivity(ctx, s)
        except NotComputable as exc:
            row = {"sensitive": None, "reason": str(exc)}
            rep.say(f"  {s.name:24s} block sensitivity not computable: {exc}")
        else:
            rep.say(f"  {s.name:24s} verdict {row['verdict']:12s} V10/V5 {row['ratio10']:.3f} "
                    f"widen x{row['factor']:.3f}: [{row['interval'][0]:+.4f}, "
                    f"{row['interval'][1]:+.4f}] -> [{row['widened_interval'][0]:+.4f}, "
                    f"{row['widened_interval'][1]:+.4f}] {row['widened_verdict']:12s} "
                    + ("BLOCK-SENSITIVE" if row["sensitive"] else "not block-sensitive"))
        rows[s.name] = row
    for name in unbuilt:
        reason = "no influence series for this part (listed as not computable above)"
        rep.say(f"  {name[len(ctx.system) + 1:]:24s} block sensitivity not computable: {reason}")
        rows[name[len(ctx.system) + 1:]] = {"sensitive": None, "reason": reason}
    flagged = [n for n, r in rows.items() if r["sensitive"]]
    computable = [n for n, r in rows.items() if r["sensitive"] is not None]
    missing = [n for n, r in rows.items() if r["sensitive"] is None]
    rep.say(f"  block-sensitive parts, {ctx.system}: {len(flagged)} of {len(computable)} computable "
            "primary parts" + (f" ({', '.join(flagged)})" if flagged else "")
            + f"; not computable: {len(missing)}" + (f" ({', '.join(missing)})" if missing else "")
            + "; informational, no effect on the exit code")
    rep.data.setdefault(ctx.system, {})["block_sensitivity"] = {
        "rows": rows, "sensitive_parts": flagged, "n_computable": len(computable),
        "n_not_computable": len(missing), "not_computable_parts": missing,
        "exit_code_effect": "none"}


def section_d3(ctx: Context) -> None:
    """D3: log-SD of the per-state evaluation MSE and of its draw-free state part (each rule alone)."""
    rep, d = ctx.rep, ctx.dump
    n_draws = int(d.scalar("meta/n_eval_draws"))
    rep.say(f"D3 log-SD of the per-state evaluation MSE at H_ref, {ctx.system} "
            f"(E = {n_draws} evaluation draws; reading: above {LOGSD_RULE} the C2h/C4h rows apply)")
    e_c, e_p, cross = (d[f"core/{k}"][:, ctx.ref] for k in ("E_C", "E_P", "C"))
    out: dict = {}
    for rule in RULES_LOGSD:
        got = attempt(rep, f"{ctx.system} D3 {rule}", _d3_rule, ctx, rule, n_draws, e_c, e_p, cross)
        if got is not None:
            out[rule] = got
    rep.data.setdefault(ctx.system, {})["D3"] = {"E": n_draws, "rules": out}


def _d3_rule(ctx: Context, rule: str, n_draws: int, e_c, e_p, cross) -> dict:
    rep, d = ctx.rep, ctx.dump
    sigma, n_bad = log_sd(d[f"core/state_mse/{rule}"][:, ctx.ref])
    proj = logsd_at_draws(sigma, n_draws)
    reading = "C2h/C4h rows apply" if sigma > LOGSD_RULE else "C2h/C4h rows do not apply"
    proj_text = (f"{proj:.3f}" if proj is not None else
                 "not defined (log-SD^2 is below psi'(E/2) - psi'(2))")
    state_sd, state_bad = None, None
    try:
        weight = (np.zeros(len(e_c)) if rule == "A1" else d[f"core/weight_href/{rule}"])
        state_sd, state_bad = log_sd(hybrid_state_mse(weight, e_c, e_p, cross))
    except NotComputable as exc:
        rep.nc(f"{ctx.system} D3 {rule} state part", str(exc))
    rep.say(f"  {rule}: log-SD {sigma:.3f} ({reading}); at E = 4: {proj_text}; "
            f"draw-free state part {fmt(state_sd, 3)}"
            + (f"; {n_bad} non-positive per-state MSE excluded" if n_bad else "")
            + (f"; {state_bad} non-positive state-part values excluded" if state_bad else ""))
    return {"log_sd": sigma, "above_rule": bool(sigma > LOGSD_RULE), "log_sd_E4": proj,
            "state_part_log_sd": state_sd, "n_nonpositive": n_bad,
            "state_part_n_nonpositive": state_bad}


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


PRIMARY_LEVEL = common.PRIMARY_LEVEL


def failure_threshold(n_boot: int, level: float = PRIMARY_LEVEL) -> int:
    """Failed resamples from which the production interval at ``level`` is infinite.

    ``floor((B - 1) a) + 1`` with ``a = (1 - level)/2`` (``statistics.percentile_interval``): 5 of
    500 and 17 of 2000 at 1 - 0.05/3. A bootstrap SE with that many failures is not used for a
    reading either: the resampling distribution it comes from is no longer the one whose interval
    the criterion itself would still call usable.
    """
    return int(math.floor((n_boot - 1) * (1.0 - level) / 2.0)) + 1


def budget_reading(ctx: Context, bias: float, se: float | None, failed: int | None,
                   ci_path: tuple[str, ...], size_key: str, kind: str) -> dict:
    """The three-way reading of a finite-M bias against ``0.1 hw_full`` (D5 and D6).

    Raises
    ------
    NotComputable
        If the SE is not available, the failed resamples reach ``failure_threshold`` (R16), or the
        interval of the criterion is absent or not finite (an interval at ``(-inf, inf)`` from
        failed resamples must never read "below 10%", R1).
    """
    if se is None or failed is None:
        raise NotComputable("the bootstrap SE is not available, so there is no reading")
    limit_failed = failure_threshold(ctx.resamples)
    if failed >= limit_failed:
        raise NotComputable(f"{failed} of {ctx.resamples} bootstrap resamples failed (the "
                            f"production interval is infinite from {limit_failed}); the SE is "
                            "not used for a reading")
    ci = dig(ctx.res, *ci_path)
    lo, hi = float(ci[0]), float(ci[1])
    if not (math.isfinite(lo) and math.isfinite(hi)):
        raise NotComputable(f"half-width not finite: interval [{lo}, {hi}] of "
                            f"{'/'.join(ci_path)}; no reading")
    hw = (hi - lo) / 2.0
    hw_full, how = full_halfwidth(hw, ctx.cfg, size_key)
    limit = 0.1 * hw_full
    reading = three_way_reading(bias, se, limit)
    point = "above" if abs(bias) > limit else "not above"
    row1 = ("may be stated below 10%" if reading == "below 10%"
            else "stays 'not below 10%' (PF-5: 'not determined' is treated as not below)")
    ctx.rep.say(f"  hw (pilot or run) {hw:.5f}; hw_full {hw_full:.5f} ({how}); "
                f"0.1 hw_full {limit:.5f}")
    ctx.rep.say(f"  reading: {reading}; point reading |B| {point} 0.1 hw_full; budget row 1 {row1}"
                + ctx.option_flag(kind))
    return {"hw": hw, "hw_full": hw_full, "hw_full_how": how, "limit": limit, "reading": reading,
            "point_reading": point}


def _d5_primary(ctx: Context, r_full, r_a, r_b, eligible) -> dict:
    rep = ctx.rep
    n = len(r_full)
    med = lambda r: float(np.median(r[eligible]))  # noqa: E731
    shift = split_half_shift(med(r_a), med(r_b), med(r_full))
    bias = RICHARDSON * shift
    out: dict = {"n_eligible": int(eligible.sum()), "delta_sh": shift, "bias_order_half": bias,
                 "bias_order_one": shift}
    rep.say(f"  eligible states {int(eligible.sum())} of {n}; med r_A {med(r_a):.5f}, med r_B "
            f"{med(r_b):.5f}, med r_200 {med(r_full):.5f}")

    def stat(idx: np.ndarray) -> float:
        rows = idx[eligible[idx]]
        if rows.size == 0:
            return float("nan")
        return RICHARDSON * split_half_shift(*(float(np.median(r[rows])) for r in (r_a, r_b, r_full)))

    check(ctx, "H2a(i) median range (D5 input)", med(r_full), ("H2a", "median_range"), 0.0)
    block = attempt(rep, f"{ctx.system} D5 block length", lambda: int(dig(ctx.cfg, "bootstrap_block")))
    boot = (attempt(rep, f"{ctx.system} D5 bootstrap", bootstrap_se, stat, n, ctx.resamples,
                    block, ctx.rng("d5-bootstrap")) if block is not None else None)
    se, failed = boot if boot is not None else (None, None)
    rep.say(f"  Delta_sh {shift:+.5f}; B(200) order 1/2 {bias:+.5f}; order 1 {shift:+.5f}; "
            f"SE {fmt(se, 4)} ({failed} failed of {ctx.resamples} resamples, block {block}, "
            f"seed {ctx.seed})" + ctx.option_flag("d5"))
    out.update(se=se, n_failed=failed)
    got = attempt(rep, f"{ctx.system} D5 reading", budget_reading, ctx, bias, se, failed,
                  ("H2a", "range_ci"), "n_test", "d5")
    if got is not None:
        out.update(got)
    return out


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
    has_40 = n_v4 >= 40
    for i, m in enumerate(levels):
        hw_all = float(np.median(half[order[i], :, 0]))
        hw_first = float(np.median(half[order[i], :40, 0])) if has_40 else None
        out["median_half_width"][int(m)] = {"all": hw_all, "first_40": hw_first}
    rep.say(f"    median half-width at H_ref over all {n_v4} V4 states: "
            + ", ".join(f"M={m}: {out['median_half_width'][int(m)]['all']:.5f}" for m in levels))
    if has_40:
        rep.say("    pilot-equivalent V4 (median over the first 40 V4 states; never pooled with a "
                "pilot V4): "
                + ", ".join(f"M={m}: {out['median_half_width'][int(m)]['first_40']:.5f}"
                            for m in levels))
    else:
        rep.nc(f"{ctx.system} D5 pilot-equivalent V4",
               f"only {n_v4} V4 states; the median over the first 40 needs 40")
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


def weight_bin_mask(w: np.ndarray, lo: float, hi: float, lo_closed: bool, hi_closed: bool
                    ) -> np.ndarray:
    """States of ``w`` in the bin with the given edges and closure."""
    return ((w >= lo) if lo_closed else (w > lo)) & ((w <= hi) if hi_closed else (w < hi))


def f_b_by_bin(w: np.ndarray, u: np.ndarray, u_a: np.ndarray, u_b: np.ndarray) -> dict:
    """``f_b`` and the WU-0008 bound of one cell (plan amendment 5, E6).

    ``u`` is the unclipped optimum of the 200 draws, ``s_i = |u_A - u_B|/2`` from the halves and
    ``w`` the clipped weight that sets the bin (five bins). A state is near a bound if
    ``min(|u|, |1 - u|) <= 2 s``. Two forms are computed, per bin and per cell: with each state's
    own ``s_i``, and with the pooled ``s_bin = sqrt(mean(s_i^2))`` of the state's bin; **the larger
    ``f_b`` governs**. The bound ``|bias| <= 0.40 (1/n) sum_near s`` (``n`` the states with a
    defined ``u`` and ``s``, the smaller and so stricter denominator) is computed for both forms
    and the larger is reported (``s_bin`` in the pooled form). States with an undefined (NaN)
    optimum are excluded from every share and counted (``n_undefined``).
    """
    ok = np.isfinite(u) & np.isfinite(u_a) & np.isfinite(u_b)
    s_i = np.where(ok, np.abs(u_a - u_b) / 2.0, 0.0)
    u_ok = np.where(ok, u, 0.5)
    near_state = ok & near_clip(u_ok, s_i)
    s_pool = np.zeros(len(w))
    out: dict = {"n_undefined": int((~ok).sum()), "n_defined": int(ok.sum()), "bins": {}}
    for label, lo, hi, lo_closed, hi_closed in WEIGHT_BINS:
        sel = ok & weight_bin_mask(w, lo, hi, lo_closed, hi_closed)
        row: dict = {"n": int(sel.sum()), "s_bin": None, "f_b_state": None, "f_b_pooled": None,
                     "f_b": None, "governs": None}
        if sel.any():
            s_bin = float(np.sqrt(np.mean(s_i[sel] ** 2)))
            s_pool[sel] = s_bin
            f_state = float(near_state[sel].mean())
            f_pool = float(near_clip(u_ok[sel], s_bin).mean())
            row.update(s_bin=s_bin, f_b_state=f_state, f_b_pooled=f_pool,
                       f_b=max(f_state, f_pool), governs="s_bin" if f_pool > f_state else "s_i")
        out["bins"][label] = row
    if not ok.any():
        raise NotComputable("no state has a defined unclipped optimum")
    near_pool = ok & near_clip(u_ok, s_pool)
    f_state, f_pool = float(near_state[ok].mean()), float(near_pool[ok].mean())
    n = int(ok.sum())
    bound_state = 0.40 * float(s_i[near_state].sum()) / n
    bound_pool = 0.40 * float(s_pool[near_pool].sum()) / n
    out.update(f_b_state=f_state, f_b_pooled=f_pool, f_b=max(f_state, f_pool),
               governs="s_bin" if f_pool > f_state else "s_i", bound_state=bound_state,
               bound_pooled=bound_pool, bound=max(bound_state, bound_pool))
    return out


def _d6_cells(ctx: Context, rho: float) -> dict:
    d, cells = ctx.dump, {}
    for n_lib in H2B_LIBRARY:
        g = ctx.group(rho, n_lib)
        mom = {t: tuple(d[f"{g}/{k}{t}"] for k in ("E_C", "E_P", "C")) for t in ("_A", "_B", "")}
        u = [unclipped_optimum(*mom[t])[0] for t in ("_A", "_B", "")]
        w = {t: weight_from_moments(*mom[t]) for t in mom}
        if not np.array_equal(w[""], d[f"{g}/w_star_href"]):
            ctx.rep.defect(f"{ctx.system} D6 {g}: the weight rebuilt from the dumped moments "
                           "differs from w_star_href")
        cells[n_lib] = {"u_a": u[0], "u_b": u[1], "u": u[2], "w_a": w["_A"], "w_b": w["_B"],
                        "w": w[""]}
    return cells


def section_d6(ctx: Context) -> None:
    """D6: the H2b(ii) bias by split-half Richardson on the paired change, and f_b."""
    rep = ctx.rep
    rep.say(f"D6 H2b(ii) clip-boundary bias, {ctx.system} (split-half Richardson on the mean "
            "paired change of the library cells; f_b = share within 2 s of a clip bound)")
    out: dict = {}
    rep.data.setdefault(ctx.system, {})["D6"] = out
    rho = attempt(rep, f"{ctx.system} D6 core noise", lambda: float(dig(ctx.cfg, "core_noise")))
    cells = attempt(rep, f"{ctx.system} D6 inputs", _d6_cells, ctx, rho) if rho is not None else None
    if cells is None:
        return
    lo, hi = H2B_LIBRARY
    change = {k: cells[hi][k] - cells[lo][k] for k in ("w_a", "w_b", "w")}
    n = len(change["w"])
    shift = split_half_shift(float(change["w_a"].mean()), float(change["w_b"].mean()),
                             float(change["w"].mean()))
    bias = RICHARDSON * shift
    out.update(n_states=n, delta_sh=shift, bias_order_half=bias, bias_order_one=shift)
    mean_change = float(change["w"].mean())
    check(ctx, "H2b(ii) mean change (D6 input)", mean_change,
          ("H2b", "library_change", "mean_change"), 1e-12,
          scale=float(np.mean(np.abs(change["w"]))))
    block = attempt(rep, f"{ctx.system} D6 block length",
                    lambda: int(dig(ctx.cfg, "bootstrap_block")))
    boot = (attempt(rep, f"{ctx.system} D6 bootstrap", bootstrap_se,
                    lambda idx: RICHARDSON * split_half_shift(
                        *(float(change[k][idx].mean()) for k in ("w_a", "w_b", "w"))),
                    n, ctx.resamples, block, ctx.rng("d6-bootstrap")) if block is not None else None)
    se, failed = boot if boot is not None else (None, None)
    out.update(se=se, n_failed=failed)
    rep.say(f"  {n} sweep states; Delta_sh {shift:+.5f}; B order 1/2 {bias:+.5f}; order 1 {shift:+.5f};"
            f" SE {fmt(se, 4)} ({failed} failed of {ctx.resamples}, block {block}, seed {ctx.seed})"
            + ctx.option_flag("d6"))
    got = attempt(rep, f"{ctx.system} D6 reading", budget_reading, ctx, bias, se, failed,
                  ("H2b", "library_change", "ci"), "n_test_sweep", "d6")
    if got is not None:
        out.update(got)
    fb: dict = {}
    for n_lib in H2B_LIBRARY:
        c = cells[n_lib]
        row = attempt(rep, f"{ctx.system} D6 f_b n_lib {n_lib}", f_b_by_bin, c["w"], c["u"],
                      c["u_a"], c["u_b"])
        if row is None:
            continue
        fb[n_lib] = row
        rep.say(f"  n_lib {n_lib}: f_b {row['f_b']:.3f} (s_i {row['f_b_state']:.3f}, s_bin "
                f"{row['f_b_pooled']:.3f}; {row['governs']} governs; {row['n_undefined']} states "
                f"with an undefined half optimum); |bias| <= 0.40 (1/n) sum_near s = "
                f"{row['bound']:.5f}")
        rep.say("      by w bin (n, s_bin, f_b with s_i, with s_bin): "
                + "; ".join(f"[{k}] {v['n']}, {fmt(v['s_bin'], 3)}, {fmt(v['f_b_state'], 3)}, "
                            f"{fmt(v['f_b_pooled'], 3)}" for k, v in row["bins"].items()))
    out["f_b"] = fb
    if len(fb) == len(H2B_LIBRARY):
        paired = sum(fb[n_lib]["bound"] for n_lib in H2B_LIBRARY)
        out["bound_paired"] = paired
        rep.say(f"  WU-0008 bound for the paired change: {paired:.5f} = the sum of the two cells' "
                "bounds (no cancellation credited)")
    else:
        rep.nc(f"{ctx.system} D6 paired bound", "a cell's f_b is not computable")


# --------------------------------------------------------------------------------------------
# C4: the Levenberg-Marquardt readings (row .8b; B1 item 9; note section M6)
# --------------------------------------------------------------------------------------------
def _band(above, late, nodec, iters) -> dict:
    return {"above": above, "late": late, "nodec": nodec, "iters": iters}


LM_BANDS: dict[str, dict[float, dict]] = {
    "lorenz63": {
        0.005: _band((0.0099, 0.041), (0.011, 0.043), 1e-4, (6, 8)),
        0.01: _band((0.011, 0.047), (0.012, 0.049), 1e-4, (6, 8)),
        0.02: _band((0.015, 0.066), (0.017, 0.070), 1e-4, (7, 9)),
        0.05: _band((0.019, 0.092), (0.024, 0.105), 1e-4, (7, 9))},
    "rossler": {
        0.005: _band((0.0004, 0.0023), (0.0005, 0.0034), 1e-4, (6, 8)),
        0.01: _band((0.0005, 0.0021), (0.0009, 0.0045), 1e-4, (7, 9)),
        0.02: _band((0.0006, 0.0027), (0.0014, 0.0065), 6.7e-4, (7, 9)),
        0.05: _band((0.0006, 0.0031), (0.0035, 0.014), 1.3e-3, (7, 9))},
    "chua": {
        0.005: _band((0.0017, 0.016), (0.0042, 0.021), 1e-4, (5, 7)),
        0.01: _band((0.0012, 0.0093), (0.0047, 0.019), 1e-4, (5, 7)),
        0.02: _band((0.0027, 0.013), (0.0097, 0.044), 1e-4, (5, 7)),
        0.05: _band((0.0059, 0.029), (0.026, 0.113), 1e-4, (5, 7))}}
"""Pilot bands of the oracle kind by system and rho (note M6, "Pilot bands"): ``fraction_above_chi2``
and ``fraction_late_progress`` as ``(lo, hi)``, ``fraction_no_decrease`` as an upper end, and
``median_iterations`` as ``(lo, hi)``."""
CHI2_REFERENCE_TAIL = 0.001
"""The chi-square tail beyond ``fraction_above_chi2``'s threshold under the reference law."""
POISSON_LEVEL = 0.99


def lm_band_for(system: str, rho: float, preset: str) -> dict:
    """The band of a system and rho for a pilot or a full-preset run (M6; B1 item 9).

    Full preset: upper ends as the pilot; lower ends 0.0005 (``fraction_above_chi2``) and 0
    (``fraction_late_progress``); ``median_iterations`` at most pilot + 1 (no lower end).

    Raises
    ------
    NotComputable
        For a preset other than ``pilot`` and ``full``, or a system or rho without a band.
    """
    if preset not in ("pilot", "full"):
        raise NotComputable(f"the C4 bands are defined for the pilot and full presets, not {preset!r}")
    row = LM_BANDS.get(system, {}).get(float(rho))
    if row is None:
        raise NotComputable(f"no C4 band for system {system!r} at rho {rho:g}")
    if preset == "pilot":
        return {k: v for k, v in row.items()}
    return {"above": (0.0005, row["above"][1]), "late": (0.0, row["late"][1]),
            "nodec": row["nodec"], "iters": (0.0, row["iters"][1] + 1)}


def poisson_count_interval(n: int, lo: float, hi: float, level: float = POISSON_LEVEL
                           ) -> tuple[float, float]:
    """The 99% Poisson interval of a count whose fraction lies in ``[lo, hi]`` of ``n``.

    ``[ppf((1 - level)/2, n lo), ppf((1 + level)/2, n hi)]`` (``0`` when ``lo`` is 0).
    """
    from scipy.stats import poisson
    low = 0.0 if lo <= 0 else float(poisson.ppf((1.0 - level) / 2.0, n * lo))
    return low, float(poisson.ppf((1.0 + level) / 2.0, n * hi))


def chi2_relation(median_over_rho2: float, f_above: float, n: int, dof: int = 4) -> dict:
    """``|median c/rho^2 - Q| <= 4 SE_iid`` with ``Q = chi2.ppf(0.5/(1 - (f - 0.001)), dof)`` and
    ``SE_iid = sqrt(0.25/n)/chi2.pdf(Q, dof)`` (note M6; a share ``f - 0.001`` lies above the law)."""
    from scipy.stats import chi2
    pi = f_above - CHI2_REFERENCE_TAIL
    if not pi < 0.5:
        raise NotComputable(f"fraction_above_chi2 {f_above} gives a share {pi:.3g} above the law: "
                            "the relation's quantile 0.5/(1 - share) exists only for a share "
                            "below 1/2")
    predicted = float(chi2.ppf(0.5 / (1.0 - pi), dof))
    se = math.sqrt(0.25 / n) / float(chi2.pdf(predicted, dof))
    diff = median_over_rho2 - predicted
    return {"predicted": predicted, "se_iid": se, "diff": diff, "z": diff / se,
            "ok": bool(abs(diff) <= 4.0 * se)}


def _bits(x: object) -> object:
    """A float as its IEEE bit pattern (so 0.0 and -0.0 differ and NaN equals NaN)."""
    import struct
    return struct.pack(">d", x) if isinstance(x, float) else x


def lm_leaves(node: object, prefix: str = "") -> dict[str, object]:
    """Flatten an ``lm`` summary to ``{path: leaf}`` with floats as bit patterns."""
    if isinstance(node, dict):
        out: dict[str, object] = {}
        for key, value in node.items():
            out.update(lm_leaves(value, f"{prefix}/{key}"))
        return out
    return {prefix: _bits(node)}


def nlib_exact_check(cells: dict) -> tuple[list[str], list[str]]:
    """The library-sweep cells at one rho have bitwise equal ``lm`` summaries across N_lib.

    The LM reads the observation, not the library, so these cells (``base|rho=<g>|n_lib=<n>|sweep``)
    must agree exactly. Returns ``(checked groups, defects)``; a defect names the rho, the two
    sizes and the first differing path.
    """
    import re
    groups: dict[str, list[tuple[int, dict]]] = {}
    for key, cell in cells.items():
        m = re.fullmatch(r"base\|rho=([^|]+)\|n_lib=(\d+)\|sweep", key)
        if m and isinstance(cell, dict) and "lm" in cell:
            groups.setdefault(m.group(1), []).append((int(m.group(2)), cell["lm"]))
    checked, defects = [], []
    for rho, members in sorted(groups.items()):
        if len(members) < 2:
            continue  # a single library size has nothing to be compared with
        members.sort(key=lambda item: item[0])
        ref_n, ref = members[0]
        ref_leaves = lm_leaves(ref)
        checked.append(f"rho={rho}: n_lib {', '.join(str(n) for n, _ in members)}")
        for n, lm in members[1:]:
            leaves = lm_leaves(lm)
            if leaves.keys() != ref_leaves.keys():
                defects.append(f"rho={rho}: the lm summary of n_lib {n} has other keys than n_lib "
                               f"{ref_n}")
                continue
            for path, value in leaves.items():
                if value != ref_leaves[path]:
                    defects.append(f"rho={rho}: lm{path} differs between n_lib {ref_n} and {n}")
                    break
    return checked, defects


def nlib_expected_cells(cells: dict, cfg: dict) -> tuple[list[str], list[str]]:
    """The library-sweep cells that the configuration promises and the results lack (R18).

    The expected cells are ``base|rho=<g>|n_lib=<n>|sweep`` for ``library_sweep_noises`` x
    ``library_sizes``, except ``(core noise, core library)``, which is the core cell (it pools three
    splits and the eval draws, so it is not compared). Returns ``(absent, by_design)``: a sentence per
    expected cell that is missing or has no ``lm`` summary, and the rho values that have fewer than
    two expected library sizes (nothing to compare, stated rather than skipped).
    """
    core_noise, core_library = float(dig(cfg, "core_noise")), int(dig(cfg, "core_library"))
    sizes = [int(n) for n in dig(cfg, "library_sizes")]
    absent, by_design = [], []
    for rho in dig(cfg, "library_sweep_noises"):
        rho = float(rho)
        wanted = [n for n in sizes if not (rho == core_noise and n == core_library)]
        if len(wanted) < 2:
            by_design.append(f"rho={rho:g}")
        for n in wanted:
            key = f"base|rho={rho:g}|n_lib={n}|sweep"
            if key not in cells:
                absent.append(f"expected cell {key} is absent")
            elif "lm" not in cells[key]:
                absent.append(f"expected cell {key} has no lm summary")
    return absent, by_design


def section_c4(rep: Report, system: str, sysres: dict, cfg: dict) -> None:
    """C4: the LM readings of one system against the M6 bands, the chi-square relation, and the
    N_lib bitwise check. Findings (outside a band or the relation) are reported, never a failure."""
    rep.say(f"C4 Levenberg-Marquardt readings, {system} (bands of note M6; a value outside is a "
            "FINDING, not a failure)")
    preset = cfg.get("name")
    cells = dig(sysres, "handling", "cells")
    core_noise, library = float(dig(cfg, "core_noise")), int(dig(cfg, "core_library"))
    targets = [(f"base|rho={core_noise:g}|n_lib={library}|core", core_noise)] + [
        (f"base|rho={float(r):g}|n_lib={library}|sweep", float(r))
        for r in dig(cfg, "noise_levels") if float(r) != core_noise]
    out: dict = {"cells": {}, "findings": [], "nlib": {}}
    n_find, skipped_eval = 0, 0
    for key, rho in targets:
        if key not in cells or "lm" not in cells[key]:
            rep.nc(f"{system} C4 {key}", "the cell or its lm summary is absent")
            continue
        try:
            band = lm_band_for(system, rho, preset)
        except NotComputable as exc:
            rep.nc(f"{system} C4 {key}", str(exc))
            continue
        for kind in ("oracle", "eval"):
            lm = cells[key]["lm"].get("by_kind", {}).get(kind)
            if lm is None:
                rep.nc(f"{system} C4 {key} {kind}", "no by_kind summary")
                continue
            n = lm.get("n_estimates")
            required = kind == "oracle" or key.endswith("|core")
            if not n:
                if required:
                    rep.nc(f"{system} C4 {key} {kind}",
                           "n_estimates is " + ("absent" if n is None else "0")
                           + ": a required kind has no estimates")
                else:
                    skipped_eval += 1
                continue
            missing = [k for k in ("median_residual", "fraction_above_chi2",
                                   "fraction_late_progress", "fraction_no_decrease",
                                   "median_iterations", "noise", "gof_dof") if lm.get(k) is None]
            if missing:
                rep.nc(f"{system} C4 {key} {kind}", f"lm leaves null or absent: {', '.join(missing)}")
                continue
            res = _c4_cell(rep, system, key, kind, lm, band)
            n_find += res["n_findings"]
            out["cells"][f"{key}/{kind}"] = res
    out["n_findings"] = n_find
    if skipped_eval:
        rep.say(f"  eval kind of the {skipped_eval} sweep cell(s): not part of the design "
                "(n_estimates 0), skipped")
    checked, defects = nlib_exact_check(cells)
    absent, by_design = attempt(rep, f"{system} C4 N_lib check", nlib_expected_cells, cells, cfg) \
        or ([], [])
    for text in absent:
        rep.nc(f"{system} C4 N_lib check", text)
    for text in by_design:
        rep.say(f"  N_lib check ({text}): one library size by design, nothing to compare")
    out["nlib"] = {"groups": checked, "defects": defects, "absent": absent}
    if not checked and not by_design and not absent:
        rep.nc(f"{system} C4 N_lib check", "no library-sweep cells with an lm summary")
    for text in checked:
        rep.say(f"  N_lib check ({text}): lm summaries bitwise "
                + ("equal" if not any(d.startswith(text.split(":")[0]) for d in defects)
                   else "DIFFER"))
    for text in defects:
        rep.defect(f"{system} C4 N_lib: {text} (the LM does not read the library)", label="DEFECT")
    rep.say(f"  {n_find} finding(s) in the bands and the relation (information; exit code unaffected)")
    rep.data.setdefault(system, {})["C4"] = out


def _c4_cell(rep: Report, system: str, key: str, kind: str, lm: dict, band: dict) -> dict:
    n, rho = int(lm["n_estimates"]), float(lm["noise"])
    median_c = float(lm["median_residual"]) / rho**2
    rows = {"fraction_above_chi2": ("above", float(lm["fraction_above_chi2"])),
            "fraction_late_progress": ("late", float(lm["fraction_late_progress"])),
            "fraction_no_decrease": ("nodec", float(lm["fraction_no_decrease"])),
            "median_iterations": ("iters", float(lm["median_iterations"]))}
    findings, lines = [], []
    for name, (bkey, value) in rows.items():
        b = band[bkey]
        if bkey == "nodec":
            lo, hi = 0.0, float(b)
        else:
            lo, hi = float(b[0]), float(b[1])
        how = f"[{lo:g}, {hi:g}]"
        if kind == "eval" and bkey != "iters":
            c_lo, c_hi = poisson_count_interval(n, lo, hi)
            count = round(value * n)
            ok = c_lo <= count <= c_hi
            how += f" -> count {count} in 99% Poisson [{c_lo:g}, {c_hi:g}] of {n}"
        else:
            ok = lo <= value <= hi
        lines.append(f"      {name} {value:.5g} vs {how}: {'in band' if ok else 'FINDING (outside)'}")
        if not ok:
            findings.append(f"{system} {key} {kind} {name} {value:.5g} outside {how}")
    rel = None
    try:
        rel = chi2_relation(median_c, float(lm["fraction_above_chi2"]), n, int(lm["gof_dof"]))
    except NotComputable as exc:
        rep.nc(f"{system} C4 {key} {kind} relation", str(exc))
    if rel is not None:
        lines.append(f"      relation: median c/rho^2 {median_c:.4f} vs Q {rel['predicted']:.4f} "
                     f"(SE_iid {rel['se_iid']:.4f}, z {rel['z']:+.2f}): "
                     + ("within 4 SE" if rel["ok"] else "FINDING (outside 4 SE)"))
        if not rel["ok"]:
            findings.append(f"{system} {key} {kind} median c/rho^2 {median_c:.4f} vs "
                            f"{rel['predicted']:.4f}")
    rep.say(f"  {key} [{kind}] n={n}, median c/rho^2 {median_c:.4f}")
    for line in lines:
        rep.say(line)
    for text in findings:
        rep.findings.append(text)
    return {"n": n, "median_c_over_rho2": median_c, "relation": rel, "findings": findings,
            "n_findings": len(findings)}


# --------------------------------------------------------------------------------------------
# driver
# --------------------------------------------------------------------------------------------
def run_level_lines(rep: Report) -> None:
    """D1 and D2 over the whole run (B1 7.D1: every |acf(1)|; 7.D2: at least one of the primaries).

    The predicted probability of at least one A5 trigger under no dependence is
    ``1 - prod(1 - r_i)`` over the primary series with the tabulated per-series rates (n = 300, 500,
    1000); it is 0.97 for the pilot's 18 primaries and 0.83 for the full preset's. Every sentence is
    about the **computed** series only: whatever was not computed is named, and no sentence reads
    "every series" or "none fired" over a set that has gaps (R13).
    """
    log = rep.series_log
    rep.say("Run level (all systems)")
    gaps = [name for name, _ in rep.uncomputed]
    gaps_primary = [name for name, primary in rep.uncomputed if primary]
    gap_text = ("; not computed, so not read here: " + ", ".join(gaps)) if gaps else ""
    if not log:
        rep.nc("run-level D1 and D2", "no series had an autocorrelation" + gap_text)
        rep.data["run_level"] = {"n_series": 0, "uncomputed": gaps}
        return
    within = [e for e in log if e["within"]]
    prim = [e for e in log if e["primary"]]
    prim_within = [e for e in prim if e["within"]]
    outside = [f"{e['system']} {e['name']} ({e['acf1']:+.3f})" for e in log if not e["within"]]
    scope = "computed series" if gaps else "series"
    rep.say(f"  D1: |acf(1)| within its threshold for {len(within)} of {len(log)} computed series "
            f"({len(prim_within)} of {len(prim)} primary): "
            + (f"every one of the {len(log)} computed series is within (the phi = 0 rows apply to "
               f"these {scope} only)" if not outside else
               "NOT every computed series is within: " + "; ".join(outside)) + gap_text)
    p_any = None
    if prim:
        p_any = 1.0 - float(np.prod([1.0 - lag_zero_false_trigger(e["n"]) for e in prim]))
        rep.say(f"      predicted P(some |acf(1)| of these {len(prim)} primary series above its "
                f"threshold) under no dependence: {p_any:.3f}")
    fired = [e for e in prim if e["fires"]]
    known = [e for e in prim if e["fires"] is not None]
    rates = [UNION_NULL.get(e.get("n_rate") or e["n"]) for e in known]
    if known and all(r is not None for r in rates):
        predicted = 1.0 - float(np.prod([1.0 - r for r in rates]))
        pred_text = f"{predicted:.3f}"
    else:
        predicted, pred_text = None, "not tabulated for these n"
    if not known:
        rep.nc("run-level D2", "0 of 0 primary series were computed; no statement on the A5 rule"
               + gap_text)
        verdict_text = "no statement (no primary series computed)"
    else:
        expected = len(known) + len(gaps_primary)
        verdict_text = (f"the A5 rule fired on {len(fired)} of the {len(known)} computed primary "
                        f"series ({len(known)} computed of {expected} expected; at least one "
                        f"fired: {'yes' if fired else 'no'}"
                        + (f"; primary series not computed: {', '.join(gaps_primary)})"
                           if gaps_primary else ")"))
    rep.say(f"  D2: {verdict_text}; predicted P(at least one) under no dependence for these "
            f"{len(known)} series {pred_text} (18 primaries: 0.97 pilot, 0.83 full; with H1a, 24 series: "
            "0.993 and 0.91)")
    rep.data["run_level"] = {"n_series": len(log), "n_within": len(within), "n_primary": len(prim),
                             "n_primary_within": len(prim_within), "n_fired": len(fired),
                             "n_primary_known": len(known), "predicted_at_least_one": predicted,
                             "at_least_one_fired": bool(fired), "uncomputed": gaps,
                             "predicted_acf_any": p_any}
    governing_line(rep)
    block_sensitive_line(rep)


def governing_line(rep: Report) -> None:
    """The run-level line of the governing D2 reading (OF-3): the pooled permutation, per system."""
    perms = {k: v["D2_permutation"] for k, v in rep.data.items()
             if isinstance(v, dict) and "D2_permutation" in v}
    done = {k: v for k, v in perms.items() if v}
    fired = [k for k, v in done.items() if v["fires"]]
    missing = [k for k, v in perms.items() if not v]
    smallest = min((v["p"] for v in done.values() if v.get("p") is not None), default=None)
    if fired:
        answer = "YES, block length 5 is a design question (" + ", ".join(fired) + ")"
    elif done:
        answer = "no" + (" among the computed systems" if missing else "")
    else:
        answer = "not determined (no system had a pooled permutation reading)"
    rep.say(f"  D2 governing reading (pooled permutation, OF-3; the A5 rule and beta5 above are "
            f"information): fired on {len(fired)} of {len(done)} computed system(s)"
            + (f", smallest one-sided p {smallest:.4f} (trigger: the 0.99 quantile of the null)"
               if smallest is not None else "")
            + f"; block length 5 is a design question: {answer}"
            + (f"; not computed: {', '.join(missing)}" if missing else ""))
    rep.data["run_level"]["d2_governing"] = {
        "reading": "pooled permutation (OF-3)", "n_systems_computed": len(done),
        "fired_systems": fired, "not_computed_systems": missing, "smallest_p": smallest,
        "design_question": (True if fired else (False if done else None))}


def block_sensitive_line(rep: Report) -> None:
    """The run-level line of the report-only block-sensitive label (no effect on the exit code)."""
    log = [(system, name, row["sensitive"]) for system, v in rep.data.items()
           if isinstance(v, dict) and "block_sensitivity" in v
           for name, row in v["block_sensitivity"]["rows"].items()]
    flagged = [f"{system} {name}" for system, name, state in log if state]
    missing = [f"{system} {name}" for system, name, state in log if state is None]
    n_computable = sum(state is not None for _, _, state in log)
    rep.say(f"  Block-sensitive primary verdicts (report-only; widening by sqrt(max(1, V*(10)/V*(5))) "
            f"would change them; informational, no effect on the exit code): {len(flagged)} of "
            f"{n_computable} computable primary parts"
            + (": " + "; ".join(flagged) if flagged else "")
            + f"; not computable: {len(missing)}" + (": " + "; ".join(missing) if missing else ""))
    rep.data["run_level"]["block_sensitive"] = {
        "parts": flagged, "n_computable": n_computable, "n_not_computable": len(missing),
        "not_computable_parts": missing, "exit_code_effect": "none"}


def check_provenance(ctx: Context, seed_id: str) -> None:
    """The dump must belong to this run.

    ``meta/seed_id`` must be present, agree with the run's id and be ``DEV-n`` (else the run is
    refused, R8); ``meta/system`` and ``meta/preset`` that differ from the results are a MISMATCH.
    """
    for key, expected in (("meta/system", ctx.system), ("meta/preset", ctx.cfg.get("name"))):
        if not ctx.dump.has(key):
            ctx.rep.nc(f"{ctx.system} dump provenance", f"array {key!r} is not in {ctx.dump.source}")
        elif str(ctx.dump.scalar(key)) != str(expected):
            ctx.rep.defect(f"{ctx.system}: {key} is {ctx.dump.scalar(key)!r} in the dump but "
                           f"{expected!r} in results.json (the dump is not this run's)")
    if not ctx.dump.has("meta/seed_id"):
        raise Refused(f"refused: the dump of {ctx.system} records no seed id ({ctx.dump.source})")
    dump_id = str(ctx.dump.scalar("meta/seed_id"))
    if dump_id != seed_id or not is_dev_id(dump_id):
        raise Refused(f"refused: the dump of {ctx.system} records seed id {dump_id!r} but the run "
                      f"records {seed_id!r} (all recorded ids must agree and be DEV-n)")


is_dev_id = common.is_dev_id
run_seed_id = common.run_seed_id
make_label = common.make_label
find_results = common.find_results
load_results = common.load_results


def run(results_path: Path, states_dir: Path | None = None, systems: Sequence[str] | None = None,
        seed: int = TOOL_SEED, resamples: int = 2000, permutations: int = 1000,
        rep: Report | None = None) -> Report:
    """Build the whole report for one run (into ``rep`` if given, so a caller keeps it on a crash).

    Raises
    ------
    NotComputable
        If the results file is unreadable.
    Refused
        If a recorded seed id is not a development id or the recorded ids disagree.
    """
    path, results, seed_id = load_results(results_path)
    cfg, prov = results["config"], results["provenance"]
    folder = states_dir if states_dir is not None else path.parent / "states"
    rep = rep if rep is not None else Report()
    options = {"seed": seed, "resamples": resamples, "permutations": permutations,
               "default": bool((seed, resamples, permutations)
                               == (TOOL_SEED, DEFAULT_RESAMPLES, DEFAULT_PERMUTATIONS))}
    rep.say(make_label(seed_id))
    rep.say("rehearsal_diagnostics (WU-0003.8): D1 to D6; needs owner review before freeze "
            "(statistics feeding the block-length and M decisions)")
    rep.say(f"NOTICE: every reading below is computed with tool seed {seed} (a literal scratch seed, "
            f"not a development or confirmatory seed), {resamples} bootstrap resamples and "
            f"{permutations} permutations"
            + ("" if options["default"] else " -- NON-DEFAULT OPTIONS")
            + f" (defaults: seed {TOOL_SEED}, 2000, 1000). Rerunning with other --seed, --resamples "
            "or --permutations to change a reading is not allowed; the seed and the options are an "
            "owner question (review R9).")
    rep.say(f"run: {path}; preset {cfg.get('name')}; commit {prov.get('commit', 'not recorded')}")
    rep.data["label"] = make_label(seed_id)
    rep.data["options"] = options
    stack = attempt(rep, "analysis stack", lambda: compare_stack(prov, stack_record()))
    if stack is None:
        stack = {"same": False, "rows": []}
    rep.say("Analysis stack against the run's provenance (a7): "
            + ("SAME stack (fit-derived leaves are reproduced bitwise)" if stack["same"] else
               "DIFFERENT stack (fit-derived leaves: within 4e-5 s is not computable, beyond is a "
               "MISMATCH)"))
    for name, run_value, own_value, status in stack["rows"]:
        rep.say(f"  {name}: run {run_value!r}; here {own_value!r}: {status}")
    rep.data["stack"] = {"same": stack["same"], "rows": [list(r[:1]) + [str(r[1]), str(r[2]), r[3]]
                                                           for r in stack["rows"]]}
    for name, why in OUTSIDE_SCHEMA:
        rep.nc(f"{name} (all systems)", why)
        rep.uncomputed.append((f"{name} (all systems)", False))
    all_systems = list(results.get("systems", {}))
    chosen = [s for s in all_systems if systems is None or s in systems]
    for wanted in systems or ():
        if wanted not in all_systems:
            rep.nc(f"system {wanted}", "not in results.json")
    for system in chosen:
        rep.say("")
        rep.say(f"=== {system} ===")
        attempt(rep, f"{system} C4", section_c4, rep, system, results["systems"][system], cfg)
        file = folder / f"{system}.npz"
        if not file.is_file():
            rep.nc(f"{system} (D1 to D6)", f"{file} not found (run without --states-dump?)")
            continue
        dump = None
        try:
            dump = Dump.load(file)
            schema = dump.scalar("meta/schema")
            if schema not in SCHEMAS:
                rep.nc(f"{system} (D1 to D6)", f"schema {schema!r} is not one of {SCHEMAS}")
                continue
            ctx = Context(system, dump, results["systems"][system], cfg, rep, seed, resamples,
                          permutations, stack)
            check_provenance(ctx, seed_id)
            section_d1_d2(ctx)
            for name, section in (("D3", section_d3), ("D4", section_d4), ("D5", section_d5),
                                  ("D6", section_d6)):
                attempt(rep, f"{system} {name}", section, ctx)
        except Refused:
            raise
        except NotComputable as exc:
            rep.nc(f"{system} (D1 to D6)", str(exc))
        except Exception as exc:  # noqa: BLE001  (a corrupt archive and the like: exit 2, R6)
            rep.internal(f"{system} (D1 to D6)", exc)
        finally:
            if dump is not None:
                dump.close()
    rep.say("")
    run_level_lines(rep)
    rep.say("")
    rep.say("Summary")
    if rep.incomplete:
        rep.say(f"  not computable: {len(rep.incomplete)} item(s) (listed above); never skipped")
        named = [name for name, _ in rep.uncomputed
                 if any(name.endswith(c) or f" {c} " in f" {name} " or f" {c}" in name
                        for c in NAMED_WHEN_MISSING)]
        if named:
            rep.say(f"  not computable by name: {', '.join(named)}. Without them the rehearsal "
                    "cannot say whether the phi = 0 or the phi = 0.3 coverage applies to the H1a "
                    "interval (nor to H1c's); D1 and D2 say nothing about those intervals.")
    if rep.findings:
        rep.say(f"  C4 findings: {len(rep.findings)} reading(s) outside a band or the relation "
                "(information for the owner; not a failure)")
    if rep.defects:
        rep.say(f"  MISMATCH: {len(rep.defects)} item(s) (listed above)")
    if not options["default"]:
        rep.say(f"  NON-DEFAULT OPTION: seed {seed}, resamples {resamples}, permutations "
                f"{permutations} (defaults {TOOL_SEED}, {DEFAULT_RESAMPLES}, "
                f"{DEFAULT_PERMUTATIONS}); this report is not the rehearsal record (plan "
                "amendment 5, E8)")
    return rep


_json_ready = common.json_ready


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
    rep = Report()
    try:
        run(args.run, args.states, args.systems, args.seed, args.resamples, args.permutations,
            rep=rep)
    except NotComputable as exc:  # unreadable input or a refused run: nothing else is trusted
        print(f"rehearsal_diagnostics: error: {exc}", file=sys.stderr)
        return EXIT_INCOMPLETE
    except Exception as exc:  # noqa: BLE001  (R6: keep the report, exit 2, never the MISMATCH code)
        rep.internal("run", exc)
        rep.say("INTERNAL ERROR: the report above is partial; exit 2")
    print("\n".join(rep.lines))
    code = rep.exit_code()
    if args.json is not None:
        try:
            args.json.write_text(json.dumps(_json_ready(rep.data), indent=1))
        except (OSError, TypeError, ValueError) as exc:  # R14: not the MISMATCH code
            print(f"rehearsal_diagnostics: error: cannot write {args.json}: "
                  f"{type(exc).__name__}: {exc}", file=sys.stderr)
            code = code if code == EXIT_MISMATCH else EXIT_INCOMPLETE
    return code


if __name__ == "__main__":
    sys.exit(main())
