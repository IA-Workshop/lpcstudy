"""Harness of the WU-0006 simulation studies (WU-0006.1): generators, replication runner, evaluation.

A test helper, not a test module (no ``test_`` prefix, so pytest does not collect it). It is shared by
``test_statistics_coverage.py``, ``test_analysis_coverage.py``, ``test_analysis_logrank_size.py``,
``test_analysis_null_delta_r2.py`` and the smoke ``test_wu0006_harness.py``. It changes nothing under
``lpcstudy/`` and uses only public (and, for the paired change of H2b and H2e, one private) production
functions, which it checks bitwise against its own computation (the identity check I).

Design (plan d954db9, the applied-mathematician's review 9d1152e, the main-session amendment and DEC-0018):

* **Generators** are the specifications of the review's M3 (a) and (g). The consistency ranges of
  ``wu0006_reference`` hold only for them. All randomness is ``make_rng(WU0006_SEED, "wu0006", case,
  phi, replication, purpose)`` with the literal ``WU0006_SEED = 6006`` (not a registered seed). A
  replication's bootstrap seed is an integer drawn from its own ``"boot"`` stream and enters
  ``replace(FULL, seed=...)``, so the production code derives its resample seeds exactly as in the
  pipeline. A result depends on (case, phi, replication) only, not on the number of workers.
* **Procedure under test** is the study's: moving-block bootstrap with block 5 and B = 2000
  resamples (asserted from ``FULL`` by ``assert_design``), percentile intervals at 95% and at
  ``1 - 0.05/3`` taken from the same resamples, verdicts by ``criterion_verdict``.
* **Workers.** A spawned pool of single-thread processes (``worker_pool``). The thread variables are
  set to 1 in the parent environment before the pool is created and restored afterwards; the pool size
  is ``min(LPC_THREADS, 4)`` of the invoking environment.
* **Assertion groups.** ``Evaluation.exact`` (identity with production, A4 verdict equality per
  replication, A5 no failed resamples, the C7 zero column), ``Evaluation.consistency`` (the
  pre-registered reference ranges, the defect test) and ``Evaluation.roadmap`` (the ROADMAP bounds,
  asserted only while ``ASSERT_ROADMAP_BOUNDS`` is True; Option K of DEC-0018). Every group is always
  computed and written to the results table.
"""

from __future__ import annotations

import contextlib
import json
import math
import os
import time
from collections.abc import Callable, Iterator, Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from multiprocessing import get_context
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from scipy.signal import lfilter
from scipy.special import expit
from scipy.stats import chi2, norm

from lpcstudy.analysis import (
    H1D_BAND,
    H2A_PARTIAL_BAND,
    H2C_BAND,
    H2C_CLOSED,
    H2D_BAND,
    H3C_BOUND,
    PRIMARY_LEVEL,
    _paired_change,
    h1d_correlations,
    h2a_part_ii,
    h2c_state_dependence,
    h2d_empirical_comparison,
    h3a_logrank,
    h3c_ratio,
    qn_profile_block,
    qn_regressor,
    quadratic_controls,
)
from lpcstudy.config import FULL
from lpcstudy.data import make_rng
from lpcstudy.statistics import (
    block_bootstrap_counted,
    bootstrap_values,
    criterion_verdict,
    kaplan_meier,
    partial_correlation,
    percentile_interval,
    spearman,
)
from wu0006_reference import (
    A3_LEVEL,
    A3_REFERENCE,
    CHARACTERIZATION_R_REF,
    CHARACTERIZATION_REFERENCE,
    COVERAGE_REFERENCE,
    DELTA_R2_REFERENCE,
    LOGRANK_REFERENCE,
)

# ------------------------------------------------------------------------------------ constants
ASSERT_ROADMAP_BOUNDS = True
"""Option K of DEC-0018: the ROADMAP-bound rows (A1, A2, A3, L1, L2, N1) are asserted.

Flipping it to False is Option C, which only the owner may rule: those rows are then computed,
written to the results table and reported as characterization rows, and the pytest outcome is the
consistency ranges (the defect test) and the exact checks. N2 and N3 of the delta-R2 study are
asserted in both modes."""

WU0006_SEED = 6006
"""Literal master seed of the simulation studies; not a registered DEV or confirmatory seed."""

R_COVERAGE = 1000
R_LOGRANK = 2000
R_DELTA = 500
LEVELS: tuple[float, float] = (0.95, PRIMARY_LEVEL)
LEVEL_NAMES: tuple[str, str] = ("95", "98.3")
PHIS: tuple[float, float] = (0.0, 0.3)

# Integer bounds (applied-mathematician M1): the count out of R at which the formula
# nominal -/+ 3 sqrt(p (1 - p) / R) is met, the stricter of the formula and the ROADMAP rounding.
A1_MIN = 930          # coverage at 95%: >= 0.929324 * 1000
A2_MIN = 972          # coverage at 1 - 0.05/3: >= 0.971188 * 1000
A3_MAX = {"95": 39, "98.3": 16}   # one-sided miss at the edge: <= 0.039811 / 0.016957 of 1000
L_MAX = 33            # log-rank error: <= 0.016675 * 2000
N1_MIN = 461          # 95% interval contains 0: >= 0.921 * 500
N3_MIN = 461          # coverage of the conditional estimand: >= 0.921 * 500
N2_MAX = 22           # false "distinct": <= 0.045946 * 500

LOGNORMAL_CORR = 0.8
C6_CORR = 2.0 * math.sin(0.7 * math.pi / 6.0)
"""Gaussian correlation whose Spearman correlation is exactly 6/pi * arcsin(c/2) = 0.7."""

TRUTH = {"C1": 0.0, "C2": 0.0, "C3": 0.0, "C4": 1.05, "C5": 0.10, "C6": 0.7, "C7": 0.1,
         "C8": 0.0, "C9": 0.0}
SAMPLE_SIZE = {"C8": 300, "C9": 300}  # sweep states (H2b, H2e); the others use 500 test states
VERDICT_LEVEL = {"C2": 0, "C4": 1, "C5": 0, "C6": 0, "C7": 1, "C8": 1, "C9": 0}
"""Index into ``LEVELS`` of the level at which the criterion's verdict is read."""
IDENTITY_REPS = {"C6": 3}
IDENTITY_DEFAULT = 10
CHUNK = 25

# Edge of each criterion for the independent verdict rule: (kind, edge, closed). Hard-coded here, not
# read from lpcstudy.analysis, so that a change of a band constant is caught by A4.
EDGE_RULES = {"C2": ("upper", 0.0, False), "C4": ("upper", 1.05, True),
              "C5": ("upper", 0.10, True), "C6": ("lower", 0.7, True),
              "C7": ("both", 0.1, False), "C8": ("lower", 0.0, False),
              "C9": ("lower", 0.0, False)}

# What the production code uses: (band, closed) per case.
_BANDS = {"C2": (H2C_BAND, H2C_CLOSED), "C4": ((-math.inf, H3C_BOUND), (True, True)),
          "C5": (H2D_BAND, (True, True)), "C6": (H1D_BAND, (True, True)),
          "C7": (H2A_PARTIAL_BAND, (False, False)), "C8": ((0.0, math.inf), (False, True)),
          "C9": ((0.0, math.inf), (False, True))}
SYSTEM_LABEL = "wu0006"

RESULTS_DIR = Path(__file__).resolve().parents[2] / "runs" / "tests"

# --------------------------------------------------------------------------------- worker pool
_POOL_ENV = {"OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
             "LPC_THREADS": "1", "PJRT_NPROC": "1", "NPROC": "1", "JAX_PLATFORMS": "cpu"}


def pool_size() -> int:
    """Workers of the pool: ``min(LPC_THREADS, 4)`` of the invoking environment (default 4)."""
    text = os.environ.get("LPC_THREADS", "4")
    if not text.isdigit() or not 1 <= int(text) <= 99:
        raise ValueError(f"LPC_THREADS must be an integer from 1 to 99; got {text!r}")
    return min(int(text), 4)


@contextlib.contextmanager
def worker_pool(workers: int | None = None) -> Iterator[ProcessPoolExecutor]:
    """A spawned pool of single-thread workers; the parent environment is restored on exit.

    The thread variables are set in ``os.environ`` before the pool exists, because a spawned child
    reads them when numpy, OpenBLAS and jax are imported to unpickle its first task (an initializer
    would be too late). They stay set while the pool lives, since children are started on demand.
    """
    size = pool_size() if workers is None else workers
    saved = {key: os.environ.get(key) for key in _POOL_ENV}
    os.environ.update(_POOL_ENV)
    try:
        with ProcessPoolExecutor(max_workers=size, mp_context=get_context("spawn")) as pool:
            yield pool
    finally:
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def run_tasks(pool: ProcessPoolExecutor, function: Callable, tasks: Sequence) -> list:
    """Results of ``function(task)`` in task order (so independent of the worker count)."""
    futures = [pool.submit(function, task) for task in tasks]
    return [future.result() for future in futures]


def assert_design() -> None:
    """The procedure under test is the study's (v3 section 7): B = 2000, block 5, the two levels."""
    assert FULL.bootstrap_resamples == 2000 and FULL.bootstrap_block == 5, (
        f"FULL bootstrap is {FULL.bootstrap_resamples} x {FULL.bootstrap_block}, not 2000 x 5")
    assert LEVELS[1] == 1.0 - 0.05 / 3.0
    assert (FULL.n_construction + FULL.n_calibration, FULL.n_test) == (3000, 1000)


# ---------------------------------------------------------------------------------- generators
def ar1(rng: np.random.Generator, n: int, phi: float, columns: int = 1, cross: float = 0.0
        ) -> np.ndarray:
    """Stationary unit-variance AR(1): ``x_0 = e_0``, ``x_t = phi x_{t-1} + sqrt(1 - phi^2) e_t``.

    Parameters
    ----------
    rng : np.random.Generator
        Source of the standard normal innovations.
    n : int
        Length.
    phi : float
        Lag-1 autocorrelation, in ``[0, 1)``; common to both columns.
    columns : int, optional
        1 for a series of shape ``(n,)``; 2 for a bivariate series ``(n, 2)`` whose innovations
        have lag-0 correlation ``cross`` (so the stationary marginal correlation is ``cross``).
    cross : float, optional
        Correlation of the two columns.

    Returns
    -------
    np.ndarray
        The series, float64.
    """
    if not 0.0 <= phi < 1.0:
        raise ValueError(f"phi must lie in [0, 1); got {phi}")
    if columns == 1:
        innovations = rng.standard_normal(n)
    elif columns == 2:
        z = rng.standard_normal((n, 2))
        innovations = np.column_stack(
            [z[:, 0], cross * z[:, 0] + math.sqrt(1.0 - cross * cross) * z[:, 1]])
    else:
        raise ValueError(f"columns must be 1 or 2; got {columns}")
    scaled = innovations.copy()
    scaled[1:] *= math.sqrt(1.0 - phi * phi)
    return lfilter([1.0], [1.0, -phi], scaled, axis=0)


# ------------------------------------------------------------------------- coverage case specs
@dataclass(frozen=True)
class CaseSpec:
    """One coverage design: the base case C1..C9, and the log-SD of the log-normal cases.

    Attributes
    ----------
    base : str
        "C1" to "C9" (the plan's case table).
    sigma : float
        Log-SD of the log-normal pair of C2, C4 and C5 (1 in the asserted cases).
    tag : str
        Suffix of the seed label and the table key for a characterization variant
        ("h1.5" for C2h at sigma = 1.5, "h2" for sigma = 2, "s" for C1s, whose key adds phi);
        empty for an asserted case.
    """

    base: str
    sigma: float = 1.0
    tag: str = ""

    @property
    def label(self) -> str:
        """Seed label and table key of the case."""
        return self.base + self.tag

    @property
    def n(self) -> int:
        """States per replication."""
        return SAMPLE_SIZE.get(self.base, 500)

    @property
    def truth(self) -> float:
        """The true value of the estimand (analytic)."""
        return TRUTH[self.base]

    @property
    def verdict_level(self) -> int | None:
        """Index into ``LEVELS`` of the verdict level, or None for a case without a verdict."""
        return VERDICT_LEVEL.get(self.base)

    @property
    def asserted(self) -> bool:
        """Whether the case is one of the nine asserted designs (not a characterization row)."""
        return self.tag == ""


def expected_verdict(case: str, lower: float, upper: float) -> str:
    """The verdict the band rule implies for an interval, written from the one-sided misses.

    Pass iff the interval is wholly on the predicted side of the edge, fail iff it is wholly on the
    other side, otherwise inconclusive; the edge belongs to the band as the criterion says (the
    upper edge of H2c is open, of H2d and H3c closed; the lower edge of H1d is closed, of H2b and
    H2e open; the band of H2a(ii) is open at both ends). Independent of
    ``statistics.interval_verdict``.
    """
    kind, edge, closed = EDGE_RULES[case]
    if kind == "upper":
        passes = upper <= edge if closed else upper < edge
        fails = lower > edge if closed else lower >= edge
    elif kind == "lower":
        passes = lower >= edge if closed else lower > edge
        fails = upper < edge if closed else upper <= edge
    else:
        passes = lower > -edge and upper < edge
        fails = lower >= edge or upper <= -edge
    return "fail" if fails else "pass" if passes else "inconclusive"


def generate(spec: CaseSpec, phi: float, rng: np.random.Generator, n: int | None = None
             ) -> dict[str, np.ndarray]:
    """Data of one replication, by the generator specification of the review's M3 (a).

    ``n`` overrides the case's sample size (the self-checks of the truths use very long series).
    """
    base = spec.base
    n = spec.n if n is None else n
    if base in ("C1", "C3", "C8", "C9"):
        return {"x": ar1(rng, n, phi)}
    if base in ("C2", "C4", "C5"):
        mean_log = {"C2": 0.0, "C4": math.log(1.05), "C5": math.log(1.10)}[base]
        pair = ar1(rng, n, phi, 2, LOGNORMAL_CORR)
        return {"a": np.exp(mean_log + spec.sigma * pair[:, 0]),
                "b": np.exp(spec.sigma * pair[:, 1])}
    if base == "C6":
        pair = ar1(rng, n, phi, 2, C6_CORR)
        return {"x": pair[:, 0], "y": pair[:, 1]}
    if base == "C7":
        seeds = ar1(rng, n, phi, 2, 0.0)
        noise = ar1(rng, n, phi, 2, 0.1)
        target = 0.5 * seeds[:, 0] - 0.3 * seeds[:, 1] ** 2 + noise[:, 0]
        growth = 0.4 * seeds[:, 1] + 0.2 * seeds[:, 0] * seeds[:, 1] + noise[:, 1]
        return {"seeds": seeds, "weight": expit(target), "growth": growth}
    raise ValueError(f"unknown case {base!r}")


def _bootstrap_plan(spec: CaseSpec, data: dict[str, np.ndarray], cfg
                    ) -> tuple[Callable[[np.ndarray], float], Callable[[], object]]:
    """The statistic of an index array and a factory of its bootstrap seed, as production uses them.

    The seed factory returns a fresh generator (or the integer) on every call, because a generator
    advances; production and harness each take their own.
    """
    base = spec.base
    if base == "C1":
        x = data["x"]
        return (lambda idx: float(x[idx].mean()),
                lambda: make_rng(cfg.seed, "wu0006", "C1"))
    if base == "C3":
        x = data["x"]
        return (lambda idx: float(np.median(x[idx])),
                lambda: make_rng(cfg.seed, "wu0006", "C3"))
    if base == "C2":
        diff = data["a"] - data["b"]
        return (lambda idx: float(np.mean(diff[idx])), lambda: cfg.seed + 5)
    if base == "C4":
        a, b = data["a"], data["b"]
        return (lambda idx: float(a[idx].mean() / b[idx].mean()),
                lambda: make_rng(cfg.seed, "h3c-ratio"))
    if base == "C5":
        a, b = data["a"], data["b"]
        return (lambda idx: float(a[idx].mean() / b[idx].mean() - 1.0), lambda: cfg.seed + 6)
    if base == "C6":
        x, y = data["x"], data["y"]
        return (lambda idx: spearman(x[idx], y[idx]),
                lambda: make_rng(cfg.seed, SYSTEM_LABEL, "bootstrap", "H1d", "analog_seed"))
    if base == "C7":
        weight, growth = data["weight"], data["growth"]
        logit = np.log(weight / (1.0 - weight))
        controls = quadratic_controls(data["seeds"])
        return (lambda idx: partial_correlation(logit[idx], growth[idx], controls[idx]),
                lambda: make_rng(cfg.seed, "wu0006", "h2a-part-ii"))
    diff = data["x"]
    centre = np.mean if base == "C8" else np.median
    return (lambda idx: float(centre(diff[idx])), lambda: make_rng(cfg.seed, "wu0006", base))


def _state(values: np.ndarray) -> SimpleNamespace:
    return SimpleNamespace(state_mse_ref=values)


def _production(spec: CaseSpec, data: dict[str, np.ndarray], cfg, seed_factory
                ) -> tuple[dict, dict | None]:
    """The production function of the case at its own level, and for C7 the zero column.

    Returns ``({estimate, lower, upper, n_failed, verdict}, extra)``.
    """
    base = spec.base
    if base in ("C1", "C3"):
        stat = _bootstrap_plan(spec, data, cfg)[0]
        boot = block_bootstrap_counted(stat, spec.n, cfg.bootstrap_resamples,
                                       cfg.bootstrap_block, seed_factory(), LEVELS[0])
        return ({"estimate": boot.estimate, "lower": boot.lower, "upper": boot.upper,
                 "n_failed": boot.n_failed, "verdict": ""}, None)
    if base == "C2":
        scores = {"A4": _state(data["a"]), "A2": _state(data["b"]), "A0": _state(data["b"]),
                  "A1": _state(data["b"]), "A4o": _state(data["b"])}
        evals = SimpleNamespace(horizons=np.array([cfg.reference_horizon]),
                                cp_err=np.ones((1, 1, 1)), plp_err=np.ones((1, 1, 1)))
        out = h2c_state_dependence(scores, SimpleNamespace(evals=evals), cfg)["A4_minus_A2"]
        return ({"estimate": out["mean"], "lower": out["ci"][0], "upper": out["ci"][1],
                 "n_failed": out["n_failed_resamples"], "verdict": out["verdict"]}, None)
    if base == "C4":
        out = h3c_ratio(data["a"], data["b"], cfg)
        return ({"estimate": out["A5_over_A4_mse"], "lower": out["ci"][0], "upper": out["ci"][1],
                 "n_failed": out["n_failed_resamples"], "verdict": out["verdict"]}, None)
    if base == "C5":
        out = h2d_empirical_comparison({"A3": _state(data["b"]), "A4": _state(data["a"])}, cfg)
        return ({"estimate": out["in_distribution_excess"], "lower": out["ci"][0],
                 "upper": out["ci"][1], "n_failed": out["n_failed_resamples"],
                 "verdict": out["verdict"]}, None)
    if base == "C6":
        names = ("analog_seed", "estimation_seed", "growth", "nhat")
        rows = h1d_correlations({name: (data["x"], data["y"]) for name in names},
                                SYSTEM_LABEL, cfg)["rows"]
        row = rows["analog_seed"]
        return ({"estimate": row["spearman"], "lower": row["interval"][0],
                 "upper": row["interval"][1], "n_failed": row["n_failed_resamples"],
                 "verdict": row["verdict"]}, None)
    if base == "C7":
        out = h2a_part_ii(data["weight"], data["growth"], data["seeds"],
                          n_resamples=cfg.bootstrap_resamples, block=cfg.bootstrap_block,
                          seed=seed_factory(), level=PRIMARY_LEVEL)
        part, zero = out["part_ii"]["interior"], out["part_ii"]["zero"]
        return ({"estimate": part["partial_corr"], "lower": part["ci"][0],
                 "upper": part["ci"][1], "n_failed": part["n_failed_resamples"],
                 "verdict": part["verdict"]},
                {"zero_part": zero, "combined": out["part_ii_verdict"]})
    low = np.zeros(spec.n)
    out, verdict, _ = _paired_change(
        low, data["x"], cfg, LEVELS[VERDICT_LEVEL[base]], ("wu0006", base), "change",
        "mean" if base == "C8" else "median")
    return ({"estimate": out["change"], "lower": out["ci"][0], "upper": out["ci"][1],
             "n_failed": out["n_failed_resamples"], "verdict": verdict}, None)


def _zero_column_ok(extra: dict, n_resamples: int) -> bool:
    """C7: with all w* interior the zero part is not computable: all resamples failed (A5)."""
    zero = extra["zero_part"]
    return (zero["n_failed_resamples"] == n_resamples and zero["reason"] == "not computable"
            and zero["verdict"] == "inconclusive" and extra["combined"] == "inconclusive")


def _replicate(spec: CaseSpec, phi: float, r: int, identity: bool) -> tuple:
    """One replication: intervals at both levels from the same resamples, verdicts, identity."""
    key = (WU0006_SEED, "wu0006", spec.label, f"{phi:g}", r)
    data = generate(spec, phi, make_rng(*key, "data"))
    cfg = replace(FULL, seed=int(make_rng(*key, "boot").integers(2**31)))
    statistic, seed_factory = _bootstrap_plan(spec, data, cfg)
    point, values = bootstrap_values(statistic, spec.n, cfg.bootstrap_resamples,
                                     cfg.bootstrap_block, seed_factory())
    intervals = [percentile_interval(values, level) for level in LEVELS]
    level_index = spec.verdict_level
    verdict = expected = ""
    if level_index is not None:
        band, closed = _BANDS[spec.base]
        lower, upper, _ = intervals[level_index]
        verdict = criterion_verdict(point, lower, upper, band, closed, n_states=spec.n)[0]
        expected = expected_verdict(spec.base, lower, upper)
    same, zero_ok = -1, -1
    if identity:
        level_used = 0 if level_index is None else level_index
        produced, extra = _production(spec, data, cfg, seed_factory)
        mine = {"estimate": float(point), "lower": intervals[level_used][0],
                "upper": intervals[level_used][1], "n_failed": intervals[level_used][2],
                "verdict": verdict}
        same = int(produced == mine)
        if extra is not None:
            zero_ok = int(_zero_column_ok(extra, cfg.bootstrap_resamples))
    return (float(point), intervals[0][0], intervals[0][1], intervals[0][2], intervals[1][0],
            intervals[1][1], intervals[1][2], verdict, expected, same, zero_ok)


def _coverage_task(task: tuple) -> list[tuple]:
    spec, phi, start, stop, n_identity = task
    return [_replicate(spec, phi, r, r < n_identity) for r in range(start, stop)]


@dataclass
class CoverageRun:
    """The replications of one (case, phi): bounds at both levels, verdicts, identity flags."""

    spec: CaseSpec
    phi: float
    R: int
    estimate: np.ndarray
    lower: np.ndarray       # (R, 2)
    upper: np.ndarray       # (R, 2)
    failed: np.ndarray      # (R, 2) failed resamples
    verdict: np.ndarray     # (R,) str, "" if the case has no verdict
    expected: np.ndarray    # (R,) str
    identity: np.ndarray    # (R,) int: 1 equal, 0 different, -1 not checked
    zero_ok: np.ndarray     # (R,) int, as identity (C7 only)
    seconds: float = 0.0

    def counts(self) -> dict:
        """Counts out of R: coverage, one-sided misses, verdicts, failed resamples."""
        truth = self.spec.truth
        inside = (self.lower <= truth) & (truth <= self.upper)
        out = {"cover": inside.sum(0).tolist(),
               "truth_above_upper": (truth > self.upper).sum(0).tolist(),
               "truth_below_lower": (truth < self.lower).sum(0).tolist(),
               "failed_resamples": int(self.failed.sum()),
               "mean_half_width": ((self.upper - self.lower) / 2).mean(0).tolist()}
        if self.spec.verdict_level is not None:
            out.update({"verdict_pass": int((self.verdict == "pass").sum()),
                        "verdict_fail": int((self.verdict == "fail").sum()),
                        "verdict_inconclusive": int((self.verdict == "inconclusive").sum()),
                        "verdict_mismatch": int((self.verdict != self.expected).sum())})
        return out


def run_coverage(pool: ProcessPoolExecutor, spec: CaseSpec, phi: float, R: int = R_COVERAGE
                 ) -> CoverageRun:
    """Run R replications of a coverage design on the pool."""
    assert_design()
    n_identity = IDENTITY_REPS.get(spec.base, IDENTITY_DEFAULT)
    tasks = [(spec, phi, start, min(start + CHUNK, R), n_identity) for start in range(0, R, CHUNK)]
    started = time.perf_counter()
    rows = [row for part in run_tasks(pool, _coverage_task, tasks) for row in part]
    return CoverageRun(
        spec=spec, phi=phi, R=R, estimate=np.array([row[0] for row in rows]),
        lower=np.array([[row[1], row[4]] for row in rows]),
        upper=np.array([[row[2], row[5]] for row in rows]),
        failed=np.array([[row[3], row[6]] for row in rows]),
        verdict=np.array([row[7] for row in rows]), expected=np.array([row[8] for row in rows]),
        identity=np.array([row[9] for row in rows]), zero_ok=np.array([row[10] for row in rows]),
        seconds=time.perf_counter() - started)


# ---------------------------------------------------------------------------------- evaluation
@dataclass
class Evaluation:
    """Outcome of one study row, by assertion group; ``row`` goes to the results table."""

    row: dict
    exact: list[str] = field(default_factory=list)
    consistency: list[str] = field(default_factory=list)
    roadmap: list[str] = field(default_factory=list)
    always: list[str] = field(default_factory=list)


def in_range(count: int, bounds: tuple[int, int]) -> bool:
    """Whether a count lies in an inclusive pre-registered range."""
    return bounds[0] <= count <= bounds[1]


def enforce(failures: Sequence[str], *, asserting: bool | None = None) -> str:
    """Raise on the ROADMAP-bound failures while they are asserted; return the outcome.

    Parameters
    ----------
    failures : Sequence[str]
        One message per failed ROADMAP-bound row.
    asserting : bool, optional
        True for Option K (raise), False for Option C (only report). Default: the module constant
        ``ASSERT_ROADMAP_BOUNDS`` read at call time.

    Returns
    -------
    str
        "pass" or "fail"; the outcome of the bounds whatever the mode.
    """
    if asserting is None:
        asserting = ASSERT_ROADMAP_BOUNDS
    if failures and asserting:
        raise AssertionError("ROADMAP bound failed (a finding to record, not to tune): "
                             + "; ".join(failures))
    return "fail" if failures else "pass"


def _rate(count: int, total: int) -> float:
    return count / total


def evaluate_coverage(run: CoverageRun, *, strict: bool = True) -> Evaluation:
    """A1 to A5, I and the reference ranges for one (case, phi), plus the results-table row.

    ``strict`` requires the registered R (1000); the smoke test turns it off to exercise the code at a
    tiny R, where the integer bounds are applied unscaled and so read as failures that it ignores.
    """
    if strict and run.R != R_COVERAGE:
        raise ValueError(f"R must be {R_COVERAGE} for the registered bounds; got {run.R}")
    spec, phi_key = run.spec, f"{run.phi:g}"
    counts = run.counts()
    ev = Evaluation(row={"case": spec.label, "phi": run.phi, "n": spec.n, "R": run.R,
                         "truth": spec.truth, "sigma": spec.sigma, "seconds": run.seconds,
                         "level_names": list(LEVEL_NAMES), **counts})
    label = f"{spec.label} phi={phi_key}"
    # exact checks: a failure is a code defect.
    if counts["failed_resamples"] != 0:
        ev.exact.append(f"{label}: A5 failed resamples {counts['failed_resamples']} != 0")
    if spec.verdict_level is not None and counts["verdict_mismatch"] != 0:
        ev.exact.append(f"{label}: A4 verdict differs from the band rule in "
                        f"{counts['verdict_mismatch']} replications")
    bad = int((run.identity == 0).sum())
    wanted = min(run.R, IDENTITY_REPS.get(spec.base, IDENTITY_DEFAULT))
    checked = int((run.identity == 1).sum())
    ev.row["identity_checked"] = checked
    if bad or checked != wanted:
        ev.exact.append(f"{label}: identity with production: {checked} equal, {bad} different, "
                        f"{wanted} expected")
    if spec.base == "C7":
        zero_bad = int((run.zero_ok == 0).sum())
        ev.row["zero_column_checked"] = int((run.zero_ok == 1).sum())
        if zero_bad or ev.row["zero_column_checked"] != wanted:
            ev.exact.append(f"{label}: C7 zero column is not 'not computable' with every resample "
                            f"failed in {zero_bad} replications")
    reference = COVERAGE_REFERENCE.get((spec.base, phi_key)) if spec.asserted else None
    if reference is None:
        return _characterize(run, ev)
    ev.row["asserted"] = True
    cover = counts["cover"]
    floors = (A1_MIN, A2_MIN)
    for j, name in enumerate(LEVEL_NAMES):
        p_ref, se_ref, p_fail, rng = reference[name]
        ev.row[f"cover_{name}_reference"] = {"coverage": p_ref, "se": se_ref,
                                             "p_roadmap_fails": p_fail, "range": list(rng)}
        ev.row[f"cover_{name}_roadmap_ok"] = cover[j] >= floors[j]
        ev.row[f"cover_{name}_range_ok"] = in_range(cover[j], rng)
        if cover[j] < floors[j]:
            ev.roadmap.append(
                f"{label}: A{j + 1} coverage at {name}% {cover[j]}/{run.R} < {floors[j]} "
                f"(reference {p_ref:.4f}+-{se_ref:.4f}, P(fail | correct code) {p_fail:.2f})")
        if not in_range(cover[j], rng):
            ev.consistency.append(f"{label}: coverage at {name}% {cover[j]}/{run.R} outside the "
                                  f"pre-registered range {rng} (reference {p_ref:.4f})")
    if spec.base in A3_LEVEL:
        level_name = A3_LEVEL[spec.base]
        ref_a3 = A3_REFERENCE[(spec.base, phi_key)]
        for kind in ("pass", "fail"):
            count = counts[f"verdict_{kind}"]
            rate, p_fail, rng = ref_a3[kind]
            ev.row[f"a3_{kind}_reference"] = {"rate": rate, "p_roadmap_fails": p_fail,
                                              "range": list(rng), "level": level_name}
            ev.row[f"a3_{kind}_roadmap_ok"] = count <= A3_MAX[level_name]
            ev.row[f"a3_{kind}_range_ok"] = in_range(count, rng)
            if count > A3_MAX[level_name]:
                ev.roadmap.append(
                    f"{label}: A3 P({kind}) at the edge {count}/{run.R} > {A3_MAX[level_name]} "
                    f"(level {level_name}%, reference {rate:.4f}, P(fail | correct code) "
                    f"{p_fail:.2f})")
            if not in_range(count, rng):
                ev.consistency.append(f"{label}: A3 P({kind}) {count}/{run.R} outside the "
                                      f"pre-registered range {rng} (reference {rate:.4f})")
    ev.row["roadmap_outcome"] = "fail" if ev.roadmap else "pass"
    ev.row["consistency_outcome"] = "fail" if ev.consistency else "pass"
    ev.row["roadmap_failures"] = list(ev.roadmap)
    return ev


def _characterize(run: CoverageRun, ev: Evaluation) -> Evaluation:
    """Characterization row (C1s, C2h, C4h): observed coverage against the reference, no assertion."""
    spec = run.spec
    key = spec.label + (f"{run.phi:g}" if spec.tag == "s" else "")
    ref = CHARACTERIZATION_REFERENCE.get(key)
    ev.row["asserted"] = False
    ev.row["characterization_key"] = key
    if ref is not None:
        cover = ev.row["cover"]
        z_scores = []
        for j, p_ref in enumerate(ref):
            observed = cover[j] / run.R
            se = math.sqrt(p_ref * (1 - p_ref) * (1 / run.R + 1 / CHARACTERIZATION_R_REF))
            z_scores.append((observed - p_ref) / se)
        ev.row["reference_coverage"] = list(ref)
        ev.row["z_vs_reference"] = z_scores
    return ev


# ------------------------------------------------------------------------------------ log-rank
LOGRANK_HAZARD = 0.0125
LOGRANK_HMAX = 240
LOGRANK_PER_REGIME = 200
LOGRANK_LT = 30
LOGRANK_K = 3


def logrank_draw(rng: np.random.Generator, phi: float, partial: bool
                 ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """One sample of regime labels, durations and event flags (the review's M5 design).

    Labels are the terciles of an AR(1) latent (200 states per regime); durations are geometric with
    hazard 0.0125 per step through a Gaussian copula of a second AR(1) latent, censored at 240 steps.
    ``partial`` doubles the hazard of regime 2 (the partial null L2).
    """
    n = LOGRANK_K * LOGRANK_PER_REGIME
    latent = ar1(rng, n, phi)
    labels = np.empty(n, dtype=int)
    labels[np.argsort(latent, kind="stable")] = np.repeat(np.arange(LOGRANK_K), LOGRANK_PER_REGIME)
    uniform = norm.cdf(ar1(rng, n, phi))
    hazard = np.where((labels == 2) & partial, 2 * LOGRANK_HAZARD, LOGRANK_HAZARD)
    steps = np.maximum(np.ceil(np.log(uniform) / np.log1p(-hazard)), 1).astype(int)
    return labels, np.minimum(steps, LOGRANK_HMAX), steps <= LOGRANK_HMAX


def _logrank_replicate(row: str, phi: float, r: int) -> list[float]:
    key = (WU0006_SEED, "wu0006", row, f"{phi:g}", r, "data")
    rng = make_rng(*key)
    partial = row == "L2"
    cal_labels, cal_dur, cal_ev = logrank_draw(rng, phi, partial)
    horizons = np.array([kaplan_meier(cal_dur[cal_labels == k], cal_ev[cal_labels == k],
                                      LOGRANK_HMAX).median() for k in range(LOGRANK_K)])
    labels, dur, ev = logrank_draw(rng, phi, partial)
    out = h3a_logrank(labels, dur, ev, horizons, dur.astype(float), LOGRANK_LT, LOGRANK_K)
    raw = [math.nan if p is None else p for p in out["logrank_p_raw"]]
    pairs = [index for pair in out["pairs"] for index in pair]
    return [float(min(out["logrank_p_holm"]) < 0.01), float(out["verdict"] == "pass"),
            *raw, float(sum(p is None for p in out["logrank_p_raw"])), 1.0 - float(ev.mean()),
            *pairs]


def _logrank_task(task: tuple) -> list[list[float]]:
    row, phi, start, stop = task
    return [_logrank_replicate(row, phi, r) for r in range(start, stop)]


@dataclass
class LogrankRun:
    """Replications of one log-rank row: error indicators, raw p-values, counts of uncomputed pairs."""

    row: str
    phi: float
    R: int
    table: np.ndarray       # columns: fwer, pass, p_raw (2), n_uncomputed, censored, pairs (4)
    seconds: float = 0.0


def run_logrank(pool: ProcessPoolExecutor, row: str, phi: float, R: int = R_LOGRANK
                ) -> LogrankRun:
    """Run R families of the log-rank design ``row`` ("L1" global null, "L2" partial null)."""
    assert_design()
    tasks = [(row, phi, start, min(start + CHUNK * 2, R)) for start in range(0, R, CHUNK * 2)]
    started = time.perf_counter()
    rows = [item for part in run_tasks(pool, _logrank_task, tasks) for item in part]
    return LogrankRun(row=row, phi=phi, R=R, table=np.array(rows, dtype=float),
                      seconds=time.perf_counter() - started)


def evaluate_logrank(run: LogrankRun, *, strict: bool = True) -> Evaluation:
    """L1, L2 against the ROADMAP bound and the reference ranges; L3 (uncomputed pairs) exact."""
    if strict and run.R != R_LOGRANK:
        raise ValueError(f"R must be {R_LOGRANK}; got {run.R}")
    phi_key = f"{run.phi:g}"
    label = f"{run.row} phi={phi_key}"
    table = run.table
    fwer, passed = int(table[:, 0].sum()), int(table[:, 1].sum())
    uncomputed = int(table[:, 4].sum())
    p_raw = table[:, 2:4]
    if run.row == "L1":
        null_p = p_raw.ravel()
    else:  # the pair that does not involve regime 2
        pairs = table[:, 6:10].reshape(-1, 2, 2)
        null_p = p_raw[np.all(pairs != 2, axis=2)]
    inflation = float(chi2.isf(null_p[np.isfinite(null_p)], 1).mean())
    reference = LOGRANK_REFERENCE[(run.row, phi_key)]
    ev = Evaluation(row={"row": run.row, "phi": run.phi, "R": run.R, "fwer_count": fwer,
                         "pass_count": passed, "uncomputed_pairs": uncomputed,
                         "censored_fraction": float(table[:, 5].mean()),
                         "mean_chi2_null_pairs": inflation, "reference": reference,
                         "seconds": run.seconds})
    if uncomputed:
        ev.exact.append(f"{label}: L3 {uncomputed} pairs not computed (expected 0)")
    checks = [("P(pass)", passed, reference["pass"][1], reference["pass"][0])]
    if run.row == "L1":
        checks.append(("FWER", fwer, reference["fwer"][1], reference["fwer"][0]))
    for name, count, rng, rate in checks:
        ok_bound, ok_range = count <= L_MAX, in_range(count, rng)
        ev.row[f"{name}_roadmap_ok"], ev.row[f"{name}_range_ok"] = ok_bound, ok_range
        if not ok_bound:
            ev.roadmap.append(f"{label}: {name} {count}/{run.R} > {L_MAX} (reference {rate:.4f}, "
                              f"P(fail | correct code) {reference['p_fail']:.3f})")
        if not ok_range:
            ev.consistency.append(f"{label}: {name} {count}/{run.R} outside the pre-registered "
                                  f"range {rng} (reference {rate:.4f})")
    ev.row["roadmap_outcome"] = "fail" if ev.roadmap else "pass"
    ev.row["consistency_outcome"] = "fail" if ev.consistency else "pass"
    ev.row["roadmap_failures"] = list(ev.roadmap)
    return ev


# ------------------------------------------------------------------------------ null delta R^2
DELTA_Q15 = -2.1471
"""15% quantile of L = x1 - 0.5 x2^2 + 0.5 x2 x3 + e (2e6 draws, the review's M3 (g)); w* = 0 below it."""
DELTA_TARGETS = ("logit_w_interior", "w_zero_indicator")
DELTA_TRUTH_STATES = 100_000
DELTA_COLUMNS = 9  # per target: est, lo, hi, truth, truth_se, refit_equal, n_failed, r2_three, reduces


def delta_states(rng: np.random.Generator, n: int, phi: float, iid: bool = False
                 ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Profile ``(n, 4)``, oracle weight and log horizon of the null design (the review's M3 (g)).

    x1, x2, x3, xi, e and e' are independent AR(1) (or i.i.d. N(0, 1) for the fresh states of the
    truth); x4 = 0.6 x1 + 0.8 xi is unit variance and carries nothing beyond x1..x3 for any target.
    L = x1 - 0.5 x2^2 + 0.5 x2 x3 + e, w* = 0 where L < DELTA_Q15 (about 15%) and expit(L) otherwise,
    and the log horizon is 0.5 x1 + 0.3 x3 + 0.5 e'.
    """
    draw = (lambda: rng.standard_normal(n)) if iid else (lambda: ar1(rng, n, phi))
    x1, x2, x3, xi, e, e2 = (draw() for _ in range(6))
    profile = np.column_stack([x1, x2, x3, 0.6 * x1 + 0.8 * xi])
    latent = x1 - 0.5 * x2**2 + 0.5 * x2 * x3 + e
    weight = np.where(latent < DELTA_Q15, 0.0, expit(latent))
    return profile, weight, 0.5 * x1 + 0.3 * x3 + 0.5 * e2


def _r2(y: np.ndarray, pred: np.ndarray) -> float:
    return float(1.0 - np.sum((y - pred) ** 2) / np.sum((y - y.mean()) ** 2))


def _delta_replicate(phi: float, r: int) -> list[float]:
    key = (WU0006_SEED, "wu0006", "DR2", f"{phi:g}", r)
    rng, seed_rng = make_rng(*key, "data"), make_rng(*key, "boot")
    xa, wa, ta = delta_states(rng, FULL.n_construction, phi)
    xb, wb, tb = delta_states(rng, FULL.n_calibration, phi)
    x_test, w_test, t_test = delta_states(rng, FULL.n_test, phi)
    x_fresh, w_fresh, _ = delta_states(rng, DELTA_TRUTH_STATES, phi, iid=True)
    x_train, w_train = np.concatenate([xa, xb]), np.concatenate([wa, wb])
    t_train = np.concatenate([ta, tb])
    model_seed, boot_seed = int(seed_rng.integers(2**31)), int(seed_rng.integers(2**31))
    result = qn_profile_block(x_train, x_test, w_train, w_test, t_train, t_test, seed=model_seed,
                              n_resamples=FULL.bootstrap_resamples, block=FULL.bootstrap_block,
                              boot_seed=boot_seed)
    row: list[float] = []
    for name in DELTA_TARGETS:
        if name == "logit_w_interior":
            keep_train = (w_train > 0) & (w_train < 1)
            keep_test = (w_test > 0) & (w_test < 1)
            keep_fresh = (w_fresh > 0) & (w_fresh < 1)
            y_train = np.log(w_train[keep_train] / (1 - w_train[keep_train]))
            y_test = np.log(w_test[keep_test] / (1 - w_test[keep_test]))
            y_fresh = np.log(w_fresh[keep_fresh] / (1 - w_fresh[keep_fresh]))
        else:
            keep_train, keep_test, keep_fresh = (np.ones(len(w), dtype=bool)
                                                 for w in (w_train, w_test, w_fresh))
            y_train, y_test, y_fresh = ((w == 0).astype(float) for w in (w_train, w_test, w_fresh))
        model3 = qn_regressor(model_seed).fit(x_train[keep_train][:, :3], y_train)
        model4 = qn_regressor(model_seed).fit(x_train[keep_train], y_train)
        pred3, pred4 = model3.predict(x_test[:, :3]), model4.predict(x_test)
        refit = _r2(y_test, pred4[keep_test]) - _r2(y_test, pred3[keep_test])
        fresh3 = model3.predict(x_fresh[keep_fresh][:, :3])
        fresh4 = model4.predict(x_fresh[keep_fresh])
        gain = (y_fresh - fresh3) ** 2 - (y_fresh - fresh4) ** 2
        total = np.sum((y_fresh - y_fresh.mean()) ** 2)
        entry = result[name]
        row += [entry["delta_r2"], entry["ci"][0], entry["ci"][1], gain.sum() / total,
                gain.std() * math.sqrt(len(gain)) / total, float(refit == entry["delta_r2"]),
                float(entry["n_failed_resamples"]), entry["r2_three"],
                float(entry["reading"] == "reduces")]
    return row


def _delta_task(task: tuple) -> list[list[float]]:
    phi, start, stop = task
    return [_delta_replicate(phi, r) for r in range(start, stop)]


@dataclass
class DeltaRun:
    """Replications of the null delta-R2 study at one phi."""

    phi: float
    R: int
    table: np.ndarray       # (R, 2 * DELTA_COLUMNS)
    seconds: float = 0.0

    def target(self, name: str) -> np.ndarray:
        """Columns of one target, shape ``(R, DELTA_COLUMNS)``."""
        j = DELTA_TARGETS.index(name)
        return self.table[:, DELTA_COLUMNS * j: DELTA_COLUMNS * (j + 1)]


def run_delta(pool: ProcessPoolExecutor, phi: float, R: int = R_DELTA, chunk: int = 5
              ) -> DeltaRun:
    """Run R replications of the null delta-R2 study (3000 training, 1000 test states)."""
    assert_design()
    tasks = [(phi, start, min(start + chunk, R)) for start in range(0, R, chunk)]
    started = time.perf_counter()
    rows = [item for part in run_tasks(pool, _delta_task, tasks) for item in part]
    return DeltaRun(phi=phi, R=R, table=np.array(rows, dtype=float),
                    seconds=time.perf_counter() - started)


def evaluate_delta(run: DeltaRun, *, strict: bool = True) -> Evaluation:
    """N1 (ROADMAP, under the constant), N2 and N3 (always) and the exact refit check."""
    if strict and run.R != R_DELTA:
        raise ValueError(f"R must be {R_DELTA}; got {run.R}")
    ev = Evaluation(row={"phi": run.phi, "R": run.R, "seconds": run.seconds,
                         "sizes": [FULL.n_construction + FULL.n_calibration, FULL.n_test],
                         "targets": {}})
    for name in DELTA_TARGETS:
        est, lo, hi, truth, truth_se, refit, failed, r2_three, reduces = run.target(name).T
        label = f"{name} phi={run.phi:g}"
        n1 = int(np.sum((lo <= 0) & (0 <= hi)))
        n2 = int(np.sum(lo > 0))
        n3 = int(np.sum((lo <= truth) & (truth <= hi)))
        half = (hi - lo) / 2
        reference = DELTA_R2_REFERENCE[name]
        ev.row["targets"][name] = {
            "n1_contains_zero": n1, "n2_false_distinct": n2, "n3_covers_conditional": n3,
            "truth_below_lower": int(np.sum(truth < lo)), "truth_above_upper": int(np.sum(truth > hi)),
            "mean_estimate": float(est.mean()), "mean_conditional_gain": float(truth.mean()),
            "sd_conditional_gain": float(truth.std()), "p_gain_positive": float(np.mean(truth > 0)),
            "mean_half_width": float(half.mean()),
            "truth_se_over_half_width_mean": float(np.mean(truth_se / half)),
            "truth_se_over_half_width_max": float(np.max(truth_se / half)),
            "p_reduces": float(reduces.mean()), "refit_bitwise": int(refit.sum()),
            "failed_resamples": int(failed.sum()), "mean_r2_three": float(r2_three.mean()),
            "reference_phi0_R200": reference, "n1_roadmap_ok": n1 >= N1_MIN,
            "n2_ok": n2 <= N2_MAX, "n3_ok": n3 >= N3_MIN}
        if int(refit.sum()) != run.R:
            ev.exact.append(f"{label}: refitting qn_regressor reproduced delta_r2 bitwise in "
                            f"{int(refit.sum())}/{run.R} replications")
        if n1 < N1_MIN:
            ev.roadmap.append(f"{label}: N1 interval contains 0 in {n1}/{run.R} < {N1_MIN} "
                              "(predicted to fail: the interval targets the conditional gain, "
                              f"mean {truth.mean():.4f}, not the population gain 0)")
        if n2 > N2_MAX:
            ev.always.append(f"{label}: N2 false 'distinct' {n2}/{run.R} > {N2_MAX}")
        if n3 < N3_MIN:
            ev.always.append(f"{label}: N3 coverage of the conditional gain {n3}/{run.R} < {N3_MIN}")
    ev.row["roadmap_outcome"] = "fail" if ev.roadmap else "pass"
    ev.row["roadmap_failures"] = list(ev.roadmap)
    ev.row["always_outcome"] = "fail" if ev.always else "pass"
    return ev


# --------------------------------------------------------------------------------------- tables
def _plain(value: object) -> object:
    """JSON-safe copy: numpy scalars and arrays to Python, tuples to lists, non-finite to strings."""
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    if isinstance(value, np.ndarray):
        return _plain(value.tolist())
    if isinstance(value, np.generic):
        return _plain(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    return value


class ResultTable:
    """The results table of one test file: a JSON under ``runs/tests/`` rewritten on every row."""

    def __init__(self, name: str, directory: Path = RESULTS_DIR) -> None:
        self.path = directory / f"wu0006_{name}.json"
        self.rows: dict[str, object] = {}

    def add(self, key: str, row: dict) -> None:
        """Store a row and rewrite the file (so a crashed run keeps what it finished)."""
        self.rows[key] = _plain(row)
        meta = {"written_utc": datetime.now(UTC).isoformat(timespec="seconds"),
                "assert_roadmap_bounds": ASSERT_ROADMAP_BOUNDS, "workers": pool_size(),
                "seed": WU0006_SEED, "bootstrap": [FULL.bootstrap_resamples, FULL.bootstrap_block]}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps({"_meta": meta, **self.rows}, indent=1, sort_keys=True))


class RunCache:
    """Runs each design once per session and records its row; shared by the tests of one table.

    A design is run by the first test that needs it. An exception is cached and raised again for the
    later tests of the same design, so a failing run is not repeated (and not paid for) per assertion
    group.
    """

    def __init__(self, name: str) -> None:
        self.table = ResultTable(name)
        self._done: dict[str, Evaluation | BaseException] = {}

    def _get(self, key: str, make: Callable[[], Evaluation]) -> Evaluation:
        if key not in self._done:
            try:
                evaluation = make()
            except Exception as error:  # cached and re-raised below; never swallowed
                self._done[key] = error
                raise
            self._done[key] = evaluation
            self.table.add(key, evaluation.row)
        done = self._done[key]
        if isinstance(done, BaseException):
            raise done
        return done

    def coverage(self, pool: ProcessPoolExecutor, spec: CaseSpec, phi: float) -> Evaluation:
        """Evaluation of ``R_COVERAGE`` replications of a coverage design."""
        return self._get(f"{spec.label}-phi{phi:g}",
                         lambda: evaluate_coverage(run_coverage(pool, spec, phi)))

    def logrank(self, pool: ProcessPoolExecutor, row: str, phi: float) -> Evaluation:
        """Evaluation of ``R_LOGRANK`` log-rank families."""
        return self._get(f"{row}-phi{phi:g}", lambda: evaluate_logrank(run_logrank(pool, row, phi)))

    def delta(self, pool: ProcessPoolExecutor, phi: float) -> Evaluation:
        """Evaluation of ``R_DELTA`` null delta-R2 replications."""
        return self._get(f"DR2-phi{phi:g}", lambda: evaluate_delta(run_delta(pool, phi)))
