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
  governs. The coverage (95% and 1 - 0.05/3) is ``cov0 + (cov0.3 - cov0) min(1, max(0, l/l_c))``
  from the WU-0006 table, interpolated from l = 0 (plan amendment 5, E2), "at most cov0.3 (beyond
  the tabulated stress)" above the case value, and "coverage not tabulated" for Q-N and H1b.
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
D2 line (at least one primary series triggers the A5 rule, against its predicted probability).

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
SCHEMAS = ("lpcstudy.states/1", "lpcstudy.states/2")
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
OUTSIDE_SCHEMA = (
    ("H1a", "no influence series yet (MA-1; row .8c)"),
    ("H1c", "no influence series yet (row .8c; its per-state ratios are in schema /2)"))
"""Criteria without a series in this tool (plan amendment 5, E1; amendment 6 assigns them to row
.8c): each is "not computable" by name (exit 2) and is named in the summary."""
PRIMARY_CRITERIA = ("H2a(i)", "H2a(ii)", "H2b(i)", "H2b(ii)", "H3c")
H1D_ROWS = (("analog_seed", 0, "eps_s"), ("estimation_seed", 1, "delta"),
            ("growth", 2, "Lambda_bar"), ("nhat", 3, "N"))
"""H1d pairs: name, column of ``core/profile`` (a strictly increasing transform of the proxy of the
first evaluation draw: ``log(x/rho)``, ``log(x/rho)``, ``x steps_per_lyapunov``, ``log(x + c)``)
and the dumped oracle array."""
H1D_TESTED = ("analog_seed", "estimation_seed", "growth")


# --------------------------------------------------------------------------------------------
# errors and the report
# --------------------------------------------------------------------------------------------
class NotComputable(Exception):
    """A diagnostic cannot be formed from the data given (never replaced by a number)."""


class Missing(NotComputable):
    """An array or leaf that the diagnostic needs is not in the file."""


class Refused(NotComputable):
    """The run is refused (a seed id that is not a development seed, or disagreeing ids)."""


@dataclass
class Report:
    """Lines, the "not computable" and mismatch lists, and the numbers (for ``--json``)."""

    lines: list[str] = field(default_factory=list)
    incomplete: list[str] = field(default_factory=list)
    defects: list[str] = field(default_factory=list)
    data: dict = field(default_factory=dict)
    uncomputed: list[tuple[str, bool]] = field(default_factory=list)
    """``(name, primary)`` of every series or criterion that was not computed (R13, plan E1)."""
    series_log: list[dict] = field(default_factory=list)
    """One entry per series with an acf (and its A5 trigger), for the run-level D1/D2 lines (R7)."""

    def say(self, text: str = "") -> None:
        """Add a line."""
        self.lines.append(text)

    def nc(self, where: str, why: str) -> None:
        """Record and print a diagnostic that cannot be computed."""
        line = f"not computable: {where}: {why}"
        self.incomplete.append(line)
        self.lines.append("  " + line)

    def internal(self, where: str, exc: Exception) -> None:
        """Record and print an unexpected exception (never lost, never read as a MISMATCH)."""
        import traceback
        frame = traceback.extract_tb(exc.__traceback__)[-1]
        line = (f"INTERNAL ERROR: {where}: {type(exc).__name__}: {exc} "
                f"(at {Path(frame.filename).name}:{frame.lineno} in {frame.name})")
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
    """Call ``fn``; a ``NotComputable`` is recorded under ``where`` and ``None`` is returned.

    Any other exception is recorded as an INTERNAL ERROR (exit 2) and also returns ``None``, so
    the rest of the report is still computed; a ``Refused`` is never caught.
    """
    try:
        return fn(*args, **kwargs)
    except Refused:
        raise
    except NotComputable as exc:
        rep.nc(where, str(exc))
        return None
    except Exception as exc:  # noqa: BLE001  (unexpected: reported, exit 2)
        rep.internal(where, exc)
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
    """The D1 coverage rule (plan amendment 5, E2), or None where no coverage is tabulated.

    ``cov(l) = cov0 + (cov0.3 - cov0) min(1, max(0, l / l_c))`` at 95% and at 1 - 0.05/3, from
    ``l = 0`` (not from the threshold: lower at every ``l`` in (0, l_c), the stricter choice).
    Above the case value ``l_c`` there is no extrapolation: the coverage is "at most cov0.3".
    """
    case, table = CASE_VALUE.get(criterion), COVERAGE.get(criterion)
    if case is None or table is None:
        return None
    (c0_95, c0_98), (c3_95, c3_98) = table
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
        cov_text = "coverage not tabulated"
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
    out = []
    for other in others:
        if other not in mse:
            ctx.rep.nc(f"{ctx.system} H2c A4-{other}", f"rule {other} is not a dumped rule")
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
            continue
        check(ctx, f"H1d {name} Spearman", rho, ("H1d", "rows", name, "spearman"), 1e-12,
              scale=1.0 / math.sqrt(int(keep.sum())))
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


SERIES_BUILDERS: tuple[tuple[str, Callable[[Context], list[Series]]], ...] = (
    ("H2a(i)", series_h2a_i), ("H2a(ii)", series_h2a_ii), ("H2b(i)", series_h2b_i),
    ("H2b(ii)", series_h2b_ii), ("H3c", series_h3c), ("H2c", series_h2c), ("H2d", series_h2d),
    ("H2e", series_h2e), ("Q-N", series_qn), ("H1b", series_h1b), ("H1d", series_h1d))


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
        rep.say(f"  {s.name:28s} n={s.n:5d} domain={s.domain:5d} {'P' if s.primary else '-'} "
                + " ".join(f"{a:+.3f}" for a in lags))
        rep.say(f"      reading: {text}; P(|acf1| > {acf_threshold(s.n):g} | no dependence) "
                f"= {lag_zero_false_trigger(s.n):.4f}")
        rows[s.name] = {"n": s.n, "domain": s.domain, "primary": s.primary, "acf": lags.tolist(),
                        "reading": text, "coverage": cov}
        rep.series_log.append({"system": ctx.system, "name": s.name, "n": s.n,
                               "primary": s.primary, "acf1": float(lags[0]),
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
        for entry in rep.series_log:
            if entry["system"] == ctx.system and entry["name"] == s.name:
                entry["fires"] = bool(summary["fires"])
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
            f"{q99:+.4f}, one-sided p {p:.4f}: {'DESIGN QUESTION' if fires else 'no'}"
            + ctx.option_flag("d2"))
    return {"observed": obs, "q99": q99, "p": p, "fires": fires, "n_series": len(usable)}


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


PRIMARY_LEVEL = 1.0 - 0.05 / 3.0


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
    fired = [e for e in prim if e["fires"]]
    known = [e for e in prim if e["fires"] is not None]
    rates = [UNION_NULL.get(e["n"]) for e in known]
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
        verdict_text = (f"the A5 rule fired on {len(fired)} of the {len(known)} computed primary "
                        f"series (at least one fired: {'yes' if fired else 'no'}"
                        + (f"; primary series not computed: {', '.join(gaps_primary)})"
                           if gaps_primary else ")"))
    rep.say(f"  D2: {verdict_text}; predicted P(at least one) under no dependence for these "
            f"{len(known)} series {pred_text} (0.97 pilot, 0.83 full for the plan's 18 primaries)")
    rep.data["run_level"] = {"n_series": len(log), "n_within": len(within), "n_primary": len(prim),
                             "n_primary_within": len(prim_within), "n_fired": len(fired),
                             "n_primary_known": len(known), "predicted_at_least_one": predicted,
                             "at_least_one_fired": bool(fired), "uncomputed": gaps}


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


def is_dev_id(seed_id: object) -> bool:
    """Whether a recorded seed id is a development id ``DEV-n``."""
    return isinstance(seed_id, str) and seed_id.startswith("DEV-") and seed_id[4:].isdigit()


def run_seed_id(results: dict) -> str:
    """The run's seed id: ``config.seed_id`` and ``provenance.seed_id`` must both be present, agree
    and be ``DEV-n``, and a recorded ``provenance.seed_kind`` must be ``development`` (R8).

    Raises
    ------
    Refused
        Otherwise.
    """
    cfg, prov = results.get("config"), results.get("provenance")
    if not isinstance(cfg, dict) or not isinstance(prov, dict):
        raise Refused("refused: results.json has no config block or no provenance block")
    ids = {"config.seed_id": cfg.get("seed_id"), "provenance.seed_id": prov.get("seed_id")}
    for where, value in ids.items():
        if not is_dev_id(value):
            raise Refused(f"refused: {where} is {value!r}, not a development seed id DEV-n")
    if ids["config.seed_id"] != ids["provenance.seed_id"]:
        raise Refused(f"refused: the recorded seed ids disagree: {ids}")
    if prov.get("seed_kind") != "development":
        raise Refused(f"refused: provenance.seed_kind is {prov.get('seed_kind')!r}, not "
                      "'development'")
    return str(ids["config.seed_id"])


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
    path = find_results(results_path)
    try:
        results = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        raise NotComputable(f"{path} is unreadable: {exc}") from exc
    if not isinstance(results, dict):
        raise NotComputable(f"{path} does not hold a JSON object")
    seed_id = run_seed_id(results)
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
                          permutations)
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
        by_name = ", ".join(name for name, _ in OUTSIDE_SCHEMA)
        rep.say(f"  not computable by name: {by_name}. Without them the rehearsal cannot say "
                "whether the phi = 0 or the phi = 0.3 coverage applies to the H1a interval (nor to "
                "H1c's); D1 and D2 say nothing about those intervals.")
    if rep.defects:
        rep.say(f"  MISMATCH: {len(rep.defects)} item(s) (listed above)")
    if not options["default"]:
        rep.say(f"  NON-DEFAULT OPTION: seed {seed}, resamples {resamples}, permutations "
                f"{permutations} (defaults {TOOL_SEED}, {DEFAULT_RESAMPLES}, "
                f"{DEFAULT_PERMUTATIONS}); this report is not the rehearsal record (plan "
                "amendment 5, E8)")
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
