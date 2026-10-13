#!/usr/bin/env python3
"""Levenberg-Marquardt iteration-doubling study of the PLP estimator (WU-0005.6, DEV-0 only).

DEVELOPMENT (DEV-0): conditional on one realization; never the confirmatory seed. The tool is not
imported by the package. It has three subcommands::

    python3 tools/lm_doubling.py compare RUN15 RUN30 [RUN60] [--probe PROBE_JSON] [--json OUT]
    python3 tools/lm_doubling.py probe --preset smoke|pilot --seed-id DEV-n --out DIR
        [--steps 15 30 60 120] [--systems S...] [--results K=PATH ...] [--per-estimate]
    python3 tools/lm_doubling.py identical RESULTS_A RESULTS_B

``compare`` (Part B, the QoI level) reads the ``results.json`` of runs made with
``--estimator-refine-steps`` 15, 30 and 60 (a run directory or the file). For each system and each
part of the five budget QoIs (H2a(i), H2a(ii) zero and interior, H2b(i), H2b(ii), H3c) it reports
the point estimate, the interval, n, the failed resamples and the verdict at each arm, the signed
changes relative to the half-width of the design (15-iteration) arm, the size ``d1`` (the largest
of the point and both endpoints; the component that sets it is named), ``d2`` for 30 to 60, the
bound ``S = d1 + 2 d2`` and the class of decision rule R of the Mathematics check (N negligible,
X not negligible, U not certified), with the label "endpoint-limited" where the point estimate
alone would give another class. It reports every verdict-bearing hypothesis, the Levenberg-Marquardt
summaries of ``handling.cells[*].lm``, the membership counts of M7, the pairing check C0 (the
leaves that cannot read a PLP output must be bitwise equal; a difference halts the study), the exact
monotonicity check P1 of the ``lm`` summaries across arms, and the transfer scaling (reported, never
applied). With ``--probe`` it reads the Part A tail ratio ``r_A`` of the same run.

``probe`` (Part A, per estimate) rebuilds the study's networks on the development seed, then for
each level of ``--steps`` re-estimates every PLP input of the five QoIs with the estimator rebuilt
by ``derive_estimator`` (``_fn`` reset, see the hazard note there), through ``forecast_draws`` in
the pipeline's chunks. It writes ``probe_<preset>.json`` (and an ``.npz`` of per-state aggregates;
per-estimate arrays only with ``--per-estimate``). With ``--results`` it checks P0 (the pooled
``lm_summary`` equals the stored one, exactly) and always checks P1 per estimate. It refuses a
non-DEV seed id, anything naming the sealed run, and the ``full`` preset; it refuses to start if a
preset run is active, takes ``flock -n`` on the GPU lock (exit 75 if held, never waits) and runs on
the CPU with the thread variables of ``tools/run_preset.sh``.

``identical`` compares two ``results.json`` leaf by leaf (bit pattern of floats), excluding the
``provenance`` block and every leaf named ``seconds`` (K3).

Exit codes: 0 no failure; 1 a halting finding (C0, P0 or P1 violated, or no leaf differs between
arms); 2 unreadable input or usage; 64 refusal; 75 lock held.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import math
import os
import re
import struct
import subprocess
import sys
import time
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lpcstudy import budget  # noqa: E402  (after the path line; no jax import)
from lpcstudy.config import PRESETS  # noqa: E402

LABEL = "DEVELOPMENT (DEV-0): conditional on one realization; not a hypothesis test"
EXIT_REFUSED = 64
EXIT_BUSY = 75
ARMS = (15, 30, 60)
LEVELS = (15, 30, 60, 120)
REFERENCE_LEVEL = 30
TOLERANCE = 0.1
"""Per-estimate tolerance as a fraction of ``rho * nu`` (applied-mathematician M3)."""
HALF = 0.5
"""The ratio bound of rule R: later changes at most halve, so the geometric tail is at most d2."""
BLOCK = 5
"""Block length of the batch-means standard error (the study's dependence model, M3)."""
COMPONENTS = ("pt", "lo", "hi")
KINDS = ("oracle", "eval", "check")
"""``pipeline.KINDS`` (a test pins the equality; the package is not imported here for it)."""
CHUNK_TRAJ = 6000
"""``ensemble_moments`` and ``evaluation_draws`` chunk size (trajectories), the default of both."""
LM_COUNTS = ("lm_nonfinite_cost", "lm_nonfinite_jacobian", "invariant_mean_replacements",
             "nu_replacements")
"""The counters of ``handling.cells[*].by_kind[*].counts`` that P0 compares."""
THREAD_VARIABLES = ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "PJRT_NPROC",
                    "NPROC")

QOI_GROUP = {"H2a(i)": "H2a", "H2a(ii)": "H2a", "H2b(i)": "H2b(i)", "H2b(ii)": "H2b(ii)",
             "H3c": "H3c"}
"""The Part A cell group whose PLP inputs feed each QoI (M4)."""
SIZE_KEY = {"H2a(i)": "n_test", "H2a(ii)": "n_test", "H2b(i)": "n_test_sweep",
            "H2b(ii)": "n_test_sweep", "H3c": "n_test"}
"""The sample size of each QoI in the transfer projection (500 to 1000, 300 to 1000)."""

# --------------------------------------------------------------------------------------------
# Part B: reading one QoI part from a results dict
# --------------------------------------------------------------------------------------------
POINT_PATH: dict[str, tuple[str, ...]] = {
    "H2a(i)": ("median_range",), "H2b(i)": ("noise", "mean_state_spearman"),
    "H2b(ii)": ("library_change", "mean_change"), "H3c": ("A5_over_A4_mse",)}
VERDICT_PATH: dict[str, tuple[str, ...]] = {
    "H2a(i)": ("part_i_verdict",), "H2b(i)": ("noise", "verdict"),
    "H2b(ii)": ("library_change", "verdict"), "H3c": ("verdict",)}
"""Where the point estimate and the verdict sit beside the interval that ``budget._parts_of`` reads;
H2a(ii) has one point (``partial_corr``) and one verdict per part under ``part_ii``."""

SINGLE_STATISTICS: dict[str, tuple[tuple[str, ...], ...]] = {
    "H1b": (("PLP", "slope"),), "H1c": (("PLP", "median_ratio"),),
    "H2c": (("A4_minus_A2", "mean"), ("A4_minus_A0", "mean")),
    "H2d": (("in_distribution_excess",),),
    "H3b": (("weight_lambda", "importance"), ("D", "value"))}
"""Verdict-bearing hypotheses that carry one natural-unit statistic per decision (paths in the
system's results); the others have several statistics and show the verdict only."""


@dataclass(frozen=True)
class Est:
    """One part of one QoI in one system at one arm, as stored.

    Attributes
    ----------
    pt, lo, hi : float or None
        Point estimate and interval ends (``None`` if not stored; infinities are kept).
    n, failed : int or None
        States and failed resamples.
    verdict : str or None
        The part verdict.
    mc_se : tuple or None
        ``ci_mc_se`` (lower, upper) if stored.
    """

    pt: float | None = None
    lo: float | None = None
    hi: float | None = None
    n: int | None = None
    failed: int | None = None
    verdict: str | None = None
    mc_se: tuple | None = None

    def value(self, component: str) -> float | None:
        """The ``pt``, ``lo`` or ``hi`` value."""
        return getattr(self, component)

    def complete(self, components: Sequence[str] = COMPONENTS) -> bool:
        """Whether every named component is stored (not ``None``)."""
        return all(self.value(c) is not None for c in components)


def _number(value: object) -> float | None:
    """``float(value)`` for a real number (``bool`` excluded), else ``None``."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _walk(node: object, path: Sequence[str]) -> object:
    for key in path:
        if not isinstance(node, Mapping) or key not in node:
            return None
        node = node[key]
    return node


def extract_parts(system: Mapping, qoi: str) -> dict[str, Est] | None:
    """The parts of ``qoi`` in one system's results, by label, or ``None`` if the QoI is absent.

    The intervals, ``n`` and the failed resamples come from ``budget._parts_of`` (the budget's own
    reader); the point estimate and the verdict from ``POINT_PATH`` and ``VERDICT_PATH`` (one named
    key per part, beside the interval).
    """
    parts = budget._parts_of(qoi, system)
    if parts is None:
        return None
    result = system.get(budget.QOI_KEYS[qoi])
    out: dict[str, Est] = {}
    for part in parts:
        if qoi == "H2a(ii)":
            node = _walk(result, ("part_ii", part.label))
            point, verdict = _walk(node, ("partial_corr",)), _walk(node, ("verdict",))
        else:
            point = _walk(result, POINT_PATH[qoi])
            verdict = _walk(result, VERDICT_PATH.get(qoi, ("verdict",)))
        ci = part.ci if isinstance(part.ci, (list, tuple)) and len(part.ci) == 2 else None
        se = tuple(part.se) if isinstance(part.se, (list, tuple)) else None
        out[part.label] = Est(
            pt=_number(point), lo=_number(ci[0]) if ci else None,
            hi=_number(ci[1]) if ci else None, n=part.n_states, failed=part.n_failed,
            verdict=verdict if isinstance(verdict, str) else None, mc_se=se)
    return out


# --------------------------------------------------------------------------------------------
# Rule R (documented correction of the Mathematics check; replaces D1 to D3)
# --------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Classification:
    """The outcome of rule R for one part (see ``classify``).

    Attributes
    ----------
    cls : str
        ``"N"`` negligible, ``"X"`` not negligible, ``"U"`` not certified.
    flag : str
        ``"yes"`` iff class N (the strict 10% flag, ``budget.below_tenth``), else ``"no"``.
    hw : float or None
        Half-width of the design arm.
    d1, d2, s : float or None
        Largest relative change 15 to 30 and 30 to 60, and ``s = d1 + 2 d2``.
    r1, r2 : dict
        Signed relative changes ``(x30 - x15)/hw`` and ``(x60 - x30)/hw`` by component.
    sets_d1, sets_d2 : str or None
        The component that sets ``d1`` and ``d2`` (first in ``pt, lo, hi`` on a tie).
    verdict_same, ratio_ok, tail_ok : bool or None
        The three conditions of class N.
    size_kind : str
        ``"estimate"`` (``size = s * hw`` under H-geo), ``"lower"`` (at least ``d1 * hw``,
        monotone convergence), ``"unsupported"`` (``d1 * hw`` and ``d2 * hw``, tail not supported)
        or ``"none"``.
    size : float or None
        The size in the units of the QoI for ``size_kind`` (``s * hw``, or ``d1 * hw``).
    reasons : tuple[str, ...]
        Why the class is not N, in words (never empty for X or U).
    """

    cls: str
    flag: str
    hw: float | None = None
    d1: float | None = None
    d2: float | None = None
    s: float | None = None
    r1: dict = field(default_factory=dict)
    r2: dict = field(default_factory=dict)
    sets_d1: str | None = None
    sets_d2: str | None = None
    verdict_same: bool | None = None
    ratio_ok: bool | None = None
    tail_ok: bool | None = None
    size_kind: str = "none"
    size: float | None = None
    reasons: tuple = ()


def strict_flag(size: float | None, half_width: float | None) -> str:
    """``yes`` iff ``size < 0.1 * half_width`` strictly (the budget's own ``below_tenth``)."""
    return budget.below_tenth(size, half_width)


def _largest(changes: Mapping[str, float]) -> tuple[float, str]:
    """The largest absolute change and the first component that attains it."""
    top = max(abs(v) for v in changes.values())
    return top, next(name for name, v in changes.items() if abs(v) == top)


def classify(ests: Mapping[int, Est | None], tail: float | None, *,
             components: Sequence[str] = COMPONENTS, structural: Sequence[str] = ()
             ) -> Classification:
    """Apply decision rule R to one part (Mathematics check of WU-0005.6).

    Per component ``x`` in ``pt, lo, hi``: ``D1x = (x30 - x15)/hw`` and ``D2x = (x60 - x30)/hw`` with
    ``hw = (hi15 - lo15)/2``; ``d1 = max |D1x|``, ``d2 = max |D2x|``, ``S = d1 + 2 d2``. The Part A
    tail ratio ``tail`` (``r_A``) is given, or ``None`` if there is no Part A.

    * **N** (flag yes): the verdict is the same at 15, 30 and 60, ``d2 <= d1/2``, ``r_A <= 1/2``,
      ``S < 0.1`` (strict, ``strict_flag``), and no structural switch.
    * **X** (flag no): the verdicts differ among the arms, or ``d1 >= 0.1``, or (``d2 <= d1/2``,
      ``r_A <= 1/2``, ``S >= 0.1`` and no structural switch).
    * **U** (flag no): every other case: a part that is not estimated at an arm, a non-finite
      endpoint or ``hw <= 0`` or non-finite (nothing can be computed, unless the verdicts differ,
      which is X), a tail that is not supported, a structural switch, or no 60 arm.

    Parameters
    ----------
    ests : Mapping[int, Est or None]
        The part at each arm that was run (keys from 15, 30, 60; 15 and 30 are required); ``None``
        means the part is absent at that arm.
    tail : float or None
        ``r_A`` (see ``tail_ratio``).
    components : Sequence[str], optional
        Components entering ``d1`` and ``d2`` (``("pt",)`` for the endpoint-limited test).
    structural : Sequence[str], optional
        Structural switches (M7) found for this part; they block N and the third bullet of X.

    Returns
    -------
    Classification
        Class, flag, sizes and reasons.

    Raises
    ------
    ValueError
        If the 15 or 30 arm is not given.
    """
    if 15 not in ests or 30 not in ests:
        raise ValueError("classify needs the 15 and 30 arms")
    arms = [k for k in ARMS if k in ests]
    reasons: list[str] = []
    absent = [k for k in arms if ests[k] is None or not ests[k].complete(components)]
    if absent:
        return Classification("U", "no", reasons=(
            f"part not estimated at the {', '.join(map(str, absent))} arm(s)",))
    verdicts = [ests[k].verdict for k in arms]
    verdict_same = len(set(verdicts)) == 1
    if not verdict_same:
        reasons.append("the verdict differs among the arms: " + " / ".join(
            f"{k}: {ests[k].verdict}" for k in arms))
    reasons.extend(structural)
    e15 = ests[15]
    width = None if e15.lo is None or e15.hi is None else (e15.hi - e15.lo) / 2.0
    values = [ests[k].value(c) for k in arms for c in components]
    computable = (width is not None and math.isfinite(width) and width > 0.0
                  and all(math.isfinite(v) for v in values))
    if not computable:
        reasons.append("not computable: an endpoint is infinite or the half-width is not positive")
        return Classification("U" if verdict_same else "X", "no", hw=width,
                              verdict_same=verdict_same, reasons=tuple(reasons))
    r1 = {c: (ests[30].value(c) - e15.value(c)) / width for c in components}
    d1, sets1 = _largest(r1)
    r2: dict = {}
    d2 = s = sets2 = None
    ratio_ok = None
    if 60 in ests:
        r2 = {c: (ests[60].value(c) - ests[30].value(c)) / width for c in components}
        d2, sets2 = _largest(r2)
        s = d1 + 2.0 * d2
        ratio_ok = d2 <= d1 / 2.0
    tail_ok = tail is not None and tail <= HALF
    if 60 not in ests:
        reasons.append("no 60 arm: the tail cannot be bounded")
    elif not ratio_ok:
        reasons.append(f"the change 30 to 60 is more than half of 15 to 30 (d2 = {d2:.4g}, "
                       f"d1 = {d1:.4g})")
    if tail is None:
        reasons.append("no Part A tail ratio")
    elif not tail_ok:
        reasons.append(f"the per-estimate tail ratio r_A = {tail:.4g} exceeds 1/2")
    common = dict(hw=width, d1=d1, d2=d2, s=s, r1=r1, r2=r2, sets_d1=sets1, sets_d2=sets2,
                  verdict_same=verdict_same, ratio_ok=ratio_ok, tail_ok=tail_ok)
    supported = bool(ratio_ok) and tail_ok
    small = s is not None and strict_flag(s, 1.0) == "yes"
    if verdict_same and supported and small and not structural:
        return Classification("N", "yes", size_kind="estimate", size=s * width, reasons=(),
                              **common)
    third = supported and not small and not structural
    if not verdict_same or d1 >= TOLERANCE or third:
        if d1 >= TOLERANCE:
            reasons.append(f"d1 = {d1:.4g} is at least 0.1")
        if third:
            reasons.append(f"S = {s:.4g} is not below 0.1")
        kind, size = ("estimate", s * width) if supported else ("lower", d1 * width)
        return Classification("X", "no", size_kind=kind, size=size, reasons=tuple(reasons),
                              **common)
    return Classification("U", "no", size_kind="unsupported", size=d1 * width,
                          reasons=tuple(reasons), **common)


def tail_ratio(f_prev: float, f_next: float, t_prev: float, t_next: float) -> float:
    """``r_A = max(F_next/F_prev, T_next/T_prev)`` for the doublings 30 to 60 (prev) and 60 to 120.

    A zero numerator gives 0; a zero denominator with a positive numerator gives infinity (the
    tail grows from nothing), as fixed in rule R.
    """
    def one(prev: float, nxt: float) -> float:
        if nxt == 0:
            return 0.0
        return math.inf if prev == 0 else nxt / prev
    return max(one(f_prev, f_next), one(t_prev, t_next))


# --------------------------------------------------------------------------------------------
# Leaf comparison: C0 (pairing) and K3 (bitwise neutrality)
# --------------------------------------------------------------------------------------------
Path_ = tuple


def flatten(node: object, path: Path_ = ()) -> dict[Path_, object]:
    """Map every leaf of a nested dict/list to its path (a tuple of keys and ``int`` indices).

    An empty dict or list is a leaf (so that a missing container is a difference).
    """
    if isinstance(node, Mapping) and node:
        out: dict[Path_, object] = {}
        for key, child in node.items():
            out.update(flatten(child, (*path, key)))
        return out
    if isinstance(node, (list, tuple)) and node:
        out = {}
        for i, child in enumerate(node):
            out.update(flatten(child, (*path, i)))
        return out
    return {path: node}


def leaf_key(value: object) -> tuple:
    """A hashable identity of a leaf: the type, and the IEEE bytes of a float (NaN by bit pattern)."""
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return (type(value).__name__, value)
    if isinstance(value, int):
        return ("int", value)
    if isinstance(value, float):
        return ("float", struct.pack("<d", value))
    return (type(value).__name__, repr(value))


def excluded(path: Path_) -> bool:
    """``provenance`` and every leaf named ``seconds`` are never compared (wall clock, host)."""
    return bool(path) and (path[0] == "provenance" or "seconds" in path)


def differing_leaves(a: Mapping, b: Mapping) -> list[Path_]:
    """Paths whose leaves differ bitwise between two results (either side missing counts).

    Excludes ``provenance`` and every path containing the key ``seconds``. Key sets and list
    lengths are compared through the leaves (a leaf present on one side only differs).
    """
    left = {p: v for p, v in flatten(a).items() if not excluded(p)}
    right = {p: v for p, v in flatten(b).items() if not excluded(p)}
    paths = sorted(set(left) | set(right), key=lambda p: tuple(map(str, p)))
    return [p for p in paths if p not in left or p not in right
            or leaf_key(left[p]) != leaf_key(right[p])]


ANY, REST = "*", "**"
SYS = ("systems", ANY)
VAL = (*SYS, "validation")
CELLS = (*SYS, "handling", "cells", ANY)
C0_PATTERNS: tuple[tuple[tuple, str], ...] = (
    (("config", REST), "provenance.config_record: every key but estimator_refine_steps"),
    (("estimators", ANY, "chosen_width"),
     "Study.setup: train_estimator precedes and ignores the LM loop"),
    (("estimators", ANY, "val_loss_by_width", REST),
     "Study.setup: train_estimator precedes and ignores the LM loop (loss by width)"),
    ((*VAL, "estimators", ANY, "chosen_width"),
     "experiments.run_system: the same estimator_log entries"),
    ((*VAL, "estimators", ANY, "val_loss_by_width", REST),
     "experiments.run_system: the same estimator_log entries (loss by width)"),
    ((*SYS, "context", REST), "experiments.context_record(ctx): built before any estimator"),
    ((*VAL, {"delay_jacobian_rel_err", "gain_rel_err"}),
     "validation.check_jacobians(ctx): V1, no StateEstimator"),
    ((*VAL, {"crlb_ratio_median", "crlb_ratio_min", "crlb_ratio_max"}),
     "validation.check_cramer_rao(ctx): V2 runs its own Gauss-Newton"),
    ((*VAL, "km_max_abs_dev"), "validation.check_kaplan_meier: V5, synthetic samples"),
    ((*VAL, "integrator_max_dev_sigma"), "validation.check_integrator(ctx): V6, the flow map"),
    ((*VAL, "cp_median_vpt_lyapunov"), "validation.check_cp_horizon: V3 reads cp_err only"),
    ((*VAL, "gate", {"V1", "V2", "V5", "V6"}),
     "validation.gate_status: thresholds of the V1, V2, V5, V6 values above"),
    ((*SYS, "verification", "P2c", REST),
     "experiments.p2c_verification: library retrieval and noise_sens, CP only"),
    ((*SYS, "H1a", REST), "analysis.h1a_library_scaling: moments.analog_seed only"),
    ((*SYS, "H1b", "CP", REST), "analysis.h1b_seed_amplifier: CP seed and sq_cp"),
    ((*SYS, "H1c", "CP", REST), "analysis.h1c_horizon_law: sq_cp"),
    ((*SYS, "H1d", "rows", "nhat", REST),
     "analysis.h1d_proxies: pair (ev.noise_sens, m.noise_sens), built from inputs and library"),
    ((*SYS, "scores", "A0", {"mse", "mse_href", "km_median_lyapunov", "rmst_lyapunov"}),
     "Rule A0 puts weight 1 on CP: 1*c + 0*p = c exactly (PLP errors are clipped finite)"),
    ((*SYS, "km_curves", "A0", REST), "Rule A0, as above"),
    ((*SYS, "oracle_recovery", "mse_at_href", "A0"), "Rule A0, as above"),
    ((*SYS, "handling", "oracles", REST), "pipeline.oracle_block: true-state quantities"),
    ((*CELLS, "denominators", REST), "pipeline.cell_handling: sizes of the computations"),
    ((*CELLS, "by_kind", ANY, "denominators", REST), "pipeline.cell_handling: sizes"),
    ((*CELLS, "counts", {"error_clips_cp", "zero_variance_corr_cp"}),
     "pipeline.cell_handling: CP-only counters"),
    ((*CELLS, "by_kind", ANY, "counts", {"error_clips_cp", "zero_variance_corr_cp"}),
     "pipeline.cell_handling: CP-only counters"),
    ((*SYS, "H2a", "part_ii", "zero", "n_states"), "analysis.h2a_part_ii: all states"),
    ((*SYS, "H2b", "library_change", "n_states"), "analysis._paired_change: len(diff)"),
    ((*SYS, "H3c", "n_states"), "analysis.h3c_ratio: len(a5_state_mse)"),
    (("robustness", ANY, ANY, "H1b", "CP", REST), "the H1b CP block inside a variant summary"),
    (("robustness", ANY, ANY, "mse_href", "A0"), "Rule A0 inside a variant summary"),
    (("handling", "robustness", ANY, "oracles", REST), "run_handling: robustness oracles"),
    (("handling", "robustness", ANY, "cells", ANY, "denominators", REST),
     "run_handling: robustness cell sizes"),
    (("handling", "robustness", ANY, "cells", ANY, "by_kind", ANY, "denominators", REST),
     "run_handling: robustness cell sizes"),
    (("handling", "robustness", ANY, "cells", ANY, "counts",
      {"error_clips_cp", "zero_variance_corr_cp"}), "run_handling: CP-only counters"),
    (("handling", "robustness", ANY, "cells", ANY, "by_kind", ANY, "counts",
      {"error_clips_cp", "zero_variance_corr_cp"}), "run_handling: CP-only counters"),
)
"""The C0 list of the Mathematics check M5: leaves that cannot read a PLP output, each with the
producer that was read to say so (one line per pattern; a pattern found to read a PLP array is
removed here as a documented correction, never after a difference appears). ``ANY`` matches one
key, ``REST`` one or more trailing keys, a set one of its names. Not listed: ``provenance`` and any
leaf named ``seconds`` (excluded everywhere, ``excluded``) and the one leaf
``config.estimator_refine_steps`` (``C0_EXEMPT``)."""
C0_EXEMPT = ("config", "estimator_refine_steps")


def _match(path: Path_, pattern: tuple) -> bool:
    for i, element in enumerate(pattern):
        if element == REST:
            return len(path) > i
        if i >= len(path):
            return False
        if isinstance(element, (set, frozenset)):
            if path[i] not in element:
                return False
        elif element != ANY and element != path[i]:
            return False
    return len(path) == len(pattern)


def c0_pattern_of(path: Path_) -> str | None:
    """The producer line of the first C0 pattern that matches ``path``, or ``None``."""
    if path == C0_EXEMPT:
        return None
    return next((why for pattern, why in C0_PATTERNS if _match(path, pattern)), None)


def c0_violations(diffs: Iterable[Path_]) -> list[tuple[Path_, str]]:
    """The differing leaves that C0 says cannot differ, with the reason each should be equal."""
    return [(p, why) for p in diffs if (why := c0_pattern_of(p)) is not None]


# --------------------------------------------------------------------------------------------
# P1: the 30-iteration run starts with the 15-iteration run (the prefix property)
# --------------------------------------------------------------------------------------------
LM_MONOTONE: tuple[tuple[str, int], ...] = (
    ("median_residual", -1), ("p95_residual", -1), ("fraction_above_chi2", -1),
    ("nonfinite_residuals", -1), ("fraction_no_decrease", -1), ("median_iterations", +1))
"""``lm`` summary keys with their direction in the number of iterations: -1 non-increasing,
+1 non-decreasing (``None`` reads as infinity for the residuals, as ``lm_summary`` stores it)."""


def _lm_blocks(results: Mapping) -> Iterable[tuple[str, Mapping]]:
    """``(label, lm block)`` for every cell of every system and robustness record, with kinds."""
    for system, body in (results.get("systems") or {}).items():
        cells = _walk(body, ("handling", "cells")) or {}
        for cell, record in cells.items():
            yield f"{system}/{cell}", record.get("lm") or {}
    robust = _walk(results, ("handling", "robustness")) or {}
    for system, body in robust.items():
        for cell, record in (body.get("cells") or {}).items():
            yield f"robustness/{system}/{cell}", record.get("lm") or {}


def check_p1_partb(arms: Mapping[int, Mapping]) -> tuple[int, list[str]]:
    """Exact monotonicity of the ``lm`` summaries across the arms (P1; K4 replaced by it).

    For every cell and kind with estimates: equal ``n_estimates`` at all arms; the keys of
    ``LM_MONOTONE`` move in the stated direction from each arm to the next (equality allowed). The
    scan of length 2k runs the length-k scan first and the carried cost never rises, so each of
    these is exact (order statistics are monotone under an elementwise order). A violation is a
    finding, never a tolerance.

    Returns
    -------
    tuple[int, list[str]]
        Number of (cell, kind, key) comparisons made, and the violations in words.
    """
    ordered = sorted(arms)
    blocks = {k: dict(_lm_blocks(arms[k])) for k in ordered}
    checked, bad = 0, []
    for label in sorted(set.intersection(*(set(b) for b in blocks.values()))
                        if blocks else set()):
        for kind in (None, *KINDS):
            nodes = {k: (blocks[k][label] if kind is None
                         else (blocks[k][label].get("by_kind") or {}).get(kind)) for k in ordered}
            if any(n is None for n in nodes.values()):
                continue
            counts = {k: n.get("n_estimates") for k, n in nodes.items()}
            if len(set(counts.values())) != 1:
                bad.append(f"{label}/{kind or 'pooled'}: n_estimates differs {counts}")
                continue
            if not counts[ordered[0]]:
                continue
            for key, direction in LM_MONOTONE:
                values = {}
                for k in ordered:
                    value = nodes[k].get(key)
                    values[k] = math.inf if value is None and key.endswith("residual") else value
                for lo, hi in zip(ordered, ordered[1:]):
                    a, b = values[lo], values[hi]
                    if a is None or b is None:
                        continue
                    checked += 1
                    if direction * (b - a) < 0:
                        bad.append(f"{label}/{kind or 'pooled'}/{key}: {a!r} at {lo} -> "
                                   f"{b!r} at {hi}")
    return checked, bad


# --------------------------------------------------------------------------------------------
# Part B: the comparison
# --------------------------------------------------------------------------------------------
def find_results(path: str | Path) -> Path:
    """The ``results.json`` of a run: the file itself, ``<dir>/results.json`` or ``<dir>/*/results.json``.

    Raises
    ------
    FileNotFoundError
        If there is none, or more than one candidate.
    """
    path = Path(path)
    if path.is_file():
        return path
    direct = path / "results.json"
    if direct.is_file():
        return direct
    found = sorted(path.glob("*/results.json"))
    if len(found) != 1:
        raise FileNotFoundError(f"no unique results.json under {path} ({len(found)} found)")
    return found[0]


def _stored_choice(results: Mapping, system: str) -> object:
    return _walk(results, ("systems", system, "fitted", "chosen_K"))


def _structural(system: str, qoi: str, label: str, arms: Mapping[int, Mapping],
                parts: Mapping[int, Mapping[str, Est] | None]) -> list[str]:
    """Structural switches (M7) that apply to one part: they make the class not N."""
    out = []
    if qoi == "H2a(ii)":
        present = {k: (p is not None and label in p) for k, p in parts.items()}
        if len(set(present.values())) > 1:
            out.append(f"the part '{label}' exists at some arms only {present}")
    if qoi == "H3c":
        chosen = {k: _stored_choice(arms[k], system) for k in arms}
        if len(set(map(str, chosen.values()))) > 1:
            out.append(f"the chosen number of regimes K of A5 differs {chosen}")
    return out


def _projection(qoi: str, config: Mapping) -> float | None:
    """The factor sqrt(n_full / n_pilot) for the QoI's sample (reported, never applied)."""
    name = SIZE_KEY[qoi]
    n_run, n_full = config.get(name), getattr(PRESETS["full"], name)
    if not isinstance(n_run, int) or n_run < 1:
        return None
    return math.sqrt(n_full / n_run)


def _flip_summary(system: Mapping) -> dict:
    """Membership counts of M7 from one arm's system results (``None`` where absent)."""
    h2a = system.get("H2a") if isinstance(system.get("H2a"), Mapping) else {}
    part_ii = h2a.get("part_ii") if isinstance(h2a.get("part_ii"), Mapping) else {}
    return {"H2a.n_eligible_states": h2a.get("n_eligible_states"),
            "H2a.n_w_zero": h2a.get("n_w_zero"), "H2a.n_w_one": h2a.get("n_w_one"),
            **{f"H2a.part_ii.{name}.n_states": _walk(body, ("n_states",))
               for name, body in part_ii.items()},
            "H2b.noise.n_constant_states": _walk(system, ("H2b", "noise", "n_constant_states")),
            "H2b.library_change.n_zero_difference": _walk(
                system, ("H2b", "library_change", "n_zero_difference")),
            "fitted.chosen_K": _walk(system, ("fitted", "chosen_K"))}


def _lm_table(results: Mapping) -> dict:
    """The ``lm`` summaries of ``handling.cells`` (pooled and by kind), the report's subset."""
    rows = {}
    for label, block in _lm_blocks(results):
        for kind, node in (("pooled", block), *((k, (block.get("by_kind") or {}).get(k))
                                                 for k in KINDS)):
            if not isinstance(node, Mapping) or not node.get("n_estimates"):
                continue
            noise, median = node.get("noise"), node.get("median_residual")
            rows[f"{label}/{kind}"] = {
                "n_estimates": node["n_estimates"],
                "fraction_above_chi2": node.get("fraction_above_chi2"),
                "fraction_late_progress": node.get("fraction_late_progress"),
                "median_c_over_rho2": (median / noise**2 if median is not None and noise
                                       else None),
                "fraction_no_decrease": node.get("fraction_no_decrease"),
                "nonfinite_residuals": node.get("nonfinite_residuals"),
                "median_iterations": node.get("median_iterations")}
    return rows


def _verdict_table(arms: Mapping[int, Mapping]) -> dict:
    """Verdicts of every verdict-bearing hypothesis at each arm, and the single statistics."""
    keys = sorted({k for r in arms.values() for k in (r.get("verdicts") or {})})
    out = {}
    for key in keys:
        by_arm = {k: (arms[k].get("verdicts") or {}).get(key) for k in arms}
        entry = {"overall": {k: (v or {}).get("verdict") for k, v in by_arm.items()},
                 "by_system": {k: (v or {}).get("by_system") for k, v in by_arm.items()}}
        entry["changed"] = len({str(x) for x in entry["overall"].values()}) > 1 or len(
            {json.dumps(x, sort_keys=True) for x in entry["by_system"].values()}) > 1
        stats = {}
        for system in sorted({s for r in arms.values() for s in (r.get("systems") or {})}):
            for path in SINGLE_STATISTICS.get(key, ()):
                values = {k: _number(_walk(arms[k], ("systems", system, key, *path)))
                          for k in arms}
                stats[f"{system}/{'.'.join(path)}"] = {
                    "values": values, **_deltas(values)}
        entry["single_statistics"] = stats
        out[key] = entry
    return out


def _deltas(values: Mapping[int, float | None]) -> dict:
    """Natural-unit changes 15 to 30 and 30 to 60 (``None`` if a value is missing)."""
    def diff(a: int, b: int) -> float | None:
        return None if values.get(a) is None or values.get(b) is None else values[b] - values[a]
    return {"delta_15_30": diff(15, 30), "delta_30_60": diff(30, 60)}


def _robustness_table(arms: Mapping[int, Mapping]) -> dict:
    """Natural-unit changes of the scalar leaves of the robustness variant summaries."""
    flat = {k: {p: v for p, v in flatten(arms[k].get("robustness") or {}).items()
                if _number(v) is not None} for k in arms}
    paths = sorted(set.intersection(*(set(f) for f in flat.values())), key=str) if flat else []
    return {"/".join(map(str, p)): {"values": (vals := {k: flat[k][p] for k in arms}),
                                    **_deltas(vals)} for p in paths}


def build_comparison(arms: Mapping[int, Mapping], probe: Mapping | None = None) -> dict:
    """The full Part B comparison of the arms (see the module docstring).

    Parameters
    ----------
    arms : Mapping[int, Mapping]
        The ``results.json`` content by iteration budget (15 and 30 required, 60 optional).
    probe : Mapping, optional
        The Part A JSON (``probe_<preset>.json``); gives ``r_A`` per system and QoI group.

    Returns
    -------
    dict
        JSON-serializable report: ``qoi`` (per system and part: values at each arm, the
        classification, the endpoint-limited label, the projection), ``verdicts``, ``robustness``,
        ``lm``, ``membership``, ``c0`` (violations and the differing-leaf count per arm pair),
        ``p1`` (checks made and violations) and ``halt`` (the reasons to stop, empty if none).
    """
    if 15 not in arms or 30 not in arms:
        raise ValueError("compare needs the 15 and 30 arms")
    ordered = sorted(arms)
    report: dict = {"label": LABEL, "arms": ordered, "qoi": {}, "membership": {}, "lm": {}}
    config = arms[15].get("config") or {}
    resamples = config.get("bootstrap_resamples")
    systems = sorted({s for r in arms.values() for s in (r.get("systems") or {})})
    for system in systems:
        report["qoi"][system] = {}
        report["membership"][system] = {k: _flip_summary((arms[k].get("systems") or {})
                                                         .get(system) or {}) for k in ordered}
        for qoi in budget.QOI_IDS:
            per_arm = {k: extract_parts((arms[k].get("systems") or {}).get(system) or {}, qoi)
                       for k in ordered}
            labels = sorted({lab for p in per_arm.values() if p for lab in p})
            if not labels:
                continue
            report["qoi"][system][qoi] = {}
            for label in labels:
                ests = {k: (per_arm[k] or {}).get(label) for k in ordered}
                tail = None
                if probe is not None:
                    group = _walk(probe, ("systems", system, "groups", QOI_GROUP[qoi]))
                    tail = _walk(group, ("tail_ratio",))
                structural = _structural(system, qoi, label, arms, per_arm)
                full = classify(ests, tail, structural=structural)
                point_only = classify(ests, tail, components=("pt",), structural=structural)
                limited = point_only.cls != full.cls
                factor = _projection(qoi, config)
                projected = None if full.s is None or factor is None else full.s * factor
                report["qoi"][system][qoi][label or "all"] = {
                    "arms": {k: asdict(e) if e is not None else None for k, e in ests.items()},
                    "classification": asdict(full),
                    "class_point_only": point_only.cls,
                    "endpoint_limited": (f"endpoint-limited at B = {resamples}" if limited
                                         else None),
                    "se_over_hw": {k: _se_over_hw(e, ests[15]) for k, e in ests.items()},
                    "transfer_factor": factor, "projected_s": projected,
                    "projected_flag": None if projected is None else strict_flag(projected, 1.0),
                    "tail_ratio": tail}
    for k in ordered:
        report["lm"][k] = _lm_table(arms[k])
    report["verdicts"] = _verdict_table(arms)
    report["robustness"] = _robustness_table(arms)
    report["pairing_notes"] = pairing_notes(arms)
    report["c0"], halt = _c0_report(arms)
    checked, bad = check_p1_partb(arms)
    report["p1"] = {"checked": checked, "violations": bad}
    report["halt"] = halt + [f"P1: {line}" for line in bad]
    report["halt"] += [f"C0: {'/'.join(map(str, p))} ({why})"
                       for p, why in report["c0"]["violations_list"]]
    return report


def _se_over_hw(est: Est | None, design: Est | None) -> float | None:
    """``ci_mc_se / hw`` of the design arm (the larger endpoint SE), as context (M2)."""
    if est is None or design is None or not est.mc_se or design.lo is None or design.hi is None:
        return None
    se = [x for x in est.mc_se if isinstance(x, (int, float))]
    width = (design.hi - design.lo) / 2.0
    return max(se) / width if se and math.isfinite(width) and width > 0 else None


def _c0_report(arms: Mapping[int, Mapping]) -> tuple[dict, list[str]]:
    """C0 over every pair of arms: the differing leaves, the C0 violations, and the halt reasons."""
    pairs, violations, halt = {}, [], []
    ordered = sorted(arms)
    for i, lo in enumerate(ordered):
        for hi in ordered[i + 1:]:
            diffs = differing_leaves(arms[lo], arms[hi])
            effect = [p for p in diffs if p != C0_EXEMPT]  # the knob's own leaf is not an effect
            bad = c0_violations(diffs)
            pairs[f"{lo}-{hi}"] = {"n_differing": len(diffs), "n_effect": len(effect),
                                   "n_c0_violations": len(bad)}
            violations += bad
            if not effect:
                halt.append(f"no leaf differs between the {lo} and {hi} arms apart from the budget "
                            "itself: the knob has no effect (K4)")
    return {"pairs": pairs, "violations_list": violations,
            "n_patterns": len(C0_PATTERNS)}, halt


# --------------------------------------------------------------------------------------------
# Part B: text
# --------------------------------------------------------------------------------------------
def _fmt(value: object, digits: int = 4) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.{digits}g}"
    return str(value)


def render(report: Mapping) -> list[str]:
    """The comparison as text lines (the table of classes first, then the details)."""
    lines = [report["label"], "",
             f"Arms: {report['arms']}. Rule R: N negligible (flag yes), X not negligible, "
             "U not certified. hw = half-width of the 15-iteration arm.", "",
             "system | QoI part | class | flag | d1 (sets) | d2 (sets) | S | size | r_A | "
             "S x sqrt(n_full/n) | notes"]
    for system, qois in report["qoi"].items():
        for qoi, parts in qois.items():
            for label, row in parts.items():
                c = row["classification"]
                size = {"estimate": f"{_fmt(c['size'])} (estimate under H-geo)",
                        "lower": f">= {_fmt(c['size'])} (monotone convergence)",
                        "unsupported": f"{_fmt(c['size'])}; tail not supported",
                        "none": "-"}[c["size_kind"]]
                notes = "; ".join(filter(None, [row["endpoint_limited"], *c["reasons"]]))
                lines.append(" | ".join([
                    system, f"{qoi}{'' if label == 'all' else ' ' + label}", c["cls"], c["flag"],
                    f"{_fmt(c['d1'])} ({c['sets_d1'] or '-'})",
                    f"{_fmt(c['d2'])} ({c['sets_d2'] or '-'})", _fmt(c["s"]), size,
                    _fmt(row["tail_ratio"]), _fmt(row["projected_s"]), notes]))
    lines += ["", "Values by arm (point [lo, hi], n, failed resamples, verdict, ci_mc_se/hw):"]
    for system, qois in report["qoi"].items():
        for qoi, parts in qois.items():
            for label, row in parts.items():
                for arm, e in row["arms"].items():
                    text = "absent" if e is None else (
                        f"{_fmt(e['pt'], 6)} [{_fmt(e['lo'], 6)}, {_fmt(e['hi'], 6)}] n={e['n']} "
                        f"failed={e['failed']} {e['verdict']} se/hw={_fmt(row['se_over_hw'][arm])}")
                    lines.append(f"  {system} {qoi} {label} @{arm}: {text}")
                r1 = row["classification"]["r1"]
                if r1:
                    lines.append(f"  {system} {qoi} {label} signed 15->30: "
                                 + ", ".join(f"r_{k} = {_fmt(v, 6)}" for k, v in r1.items()))
    lines += ["", "Verdict-bearing hypotheses (overall verdict by arm; * marks a change):"]
    for key, entry in report["verdicts"].items():
        lines.append(f"  {key}{'*' if entry['changed'] else ''}: {entry['overall']}")
        for name, stat in entry["single_statistics"].items():
            lines.append(f"    {name}: {stat['values']} d15_30={_fmt(stat['delta_15_30'], 6)} "
                         f"d30_60={_fmt(stat['delta_30_60'], 6)}")
    lines += ["", "Pairing preconditions (commit, CPU, LPC_THREADS, XLA_FLAGS, jax, jaxlib): "
              + ("the same in every arm" if not report["pairing_notes"]
                 else "DIFFER: " + "; ".join(report["pairing_notes"])),
              f"C0: {report['c0']['n_patterns']} patterns; pairs {report['c0']['pairs']}",
              f"P1: {report['p1']['checked']} comparisons, {len(report['p1']['violations'])} "
              "violations", "Membership (M7):"]
    for system, by_arm in report["membership"].items():
        for arm, counts in by_arm.items():
            lines.append(f"  {system} @{arm}: {counts}")
    lines += ["Levenberg-Marquardt summaries (handling.cells[*].lm):"]
    for arm, rows in report["lm"].items():
        for name, row in rows.items():
            lines.append(f"  @{arm} {name}: " + ", ".join(f"{k}={_fmt(v)}" for k, v in row.items()))
    lines += ["Transfer: the scaling sqrt(n_full/n_pilot) is reported in the table and not applied "
              "to any class; a pilot class N transfers only if its projected S < 0.1."]
    if report["halt"]:
        lines += ["", "HALT (a finding, /refer):", *[f"  {h}" for h in report["halt"]]]
    return lines


def render_probe(probe: Mapping) -> list[str]:
    """The Part A summary as text: per system and QoI group, per doubling, then the crossings.

    One line per doubling: the fraction of estimates that move by more than ``0.1 rho nu_30`` with
    its SE (the larger of the clustered and the batch-means), the count ``F``, the sum ``T``, the
    quantiles of the ratio, the fraction above ``0.1 ||s_30 - s_true||`` and the replaced estimates
    left out. Then the chi-square crossings, P1, the tail ratio ``r_A`` and the P0 outcome.
    """
    lines = [f"Part A (per estimate), levels {probe.get('levels')}, horizons {probe.get('horizons')} "
             f"({probe.get('preset')}, {probe.get('seed_id')}); {probe.get('label', LABEL)}"]
    for system, body in (probe.get("systems") or {}).items():
        for group, row in (body.get("groups") or {}).items():
            lines.append(f"  {system} {group}: {row.get('n_states')} states, "
                         f"{row.get('n_estimates')} estimates, r_A = {_fmt(row.get('tail_ratio'))}")
            for label, d in (row.get("doublings") or {}).items():
                lines.append(
                    f"    {label}: fraction {_fmt(d.get('fraction'))} (SE {_fmt(d.get('se'))}), "
                    f"F={d.get('F')}, T={_fmt(d.get('T'))}, q50/q90/q99 = {_fmt(d.get('q50'))}/"
                    f"{_fmt(d.get('q90'))}/{_fmt(d.get('q99'))}, max {_fmt(d.get('max'))}, "
                    f"fraction above 0.1*err {_fmt(d.get('fraction_true'))}, "
                    f"replaced left out {d.get('n_excluded')}")
            chi = row.get("chi2") or {}
            lines.append(f"    chi2: above {chi.get('above')}, above->below {chi.get('above_to_below')}, "
                         f"below->above {chi.get('below_to_above')}, share of T {chi.get('share_T')}, "
                         f"still above at the last level {chi.get('still_above_last')}")
            lines.append(f"    P1: {row.get('p1')}; MSE at H_ref change: {row.get('mse_href')}")
            lines.append(f"    w* transitions {row.get('w_star')}; eligibility {row.get('eligibility')}")
        for entry in body.get("p0") or []:
            lines.append(f"  {system} P0 @{entry.get('arm')}: "
                         + ("exact" if not entry.get("mismatches") else f"MISMATCH {entry['mismatches']}"))
    for line in probe.get("halt") or []:
        lines.append(f"HALT (a finding, /refer): {line}")
    return lines


# --------------------------------------------------------------------------------------------
# Part A: the statistics (pure numpy)
# --------------------------------------------------------------------------------------------
@dataclass
class Segment:
    """The PLP estimates of one (cell, kind, split) at every level, whitened.

    Attributes
    ----------
    name : str
        ``<cell id>/<kind>/<split>``.
    rho : float
        Noise level.
    dof : int
        ``D - m`` of the cell (the chi-square reference).
    s : dict[int, np.ndarray]
        Whitened estimates ``(n, M, m)`` by level.
    nu, c, accepted, late : dict[int, np.ndarray]
        ``nu``, the final cost, the accepted iterations and the late-progress flag, ``(n, M)``.
    replaced : dict[int, np.ndarray]
        Bool ``(n, M)``: the estimate had a state or ``nu`` replaced at that level.
    serr : dict[int, np.ndarray]
        ``||s_hat - s_true||`` in whitened units, ``(n, M)``.
    cp_sq : np.ndarray
        Per-state ``E[e_C^2]`` at the probe horizons ``(n, nH)`` (independent of the level).
    sq_plp, cross : dict[int, np.ndarray]
        Per-state ``E[e_P^2]`` and ``E[e_C e_P]`` ``(n, nH)`` by level.
    counts : dict[int, dict[str, int]]
        The ``LM_COUNTS`` sums by level.
    """

    name: str
    rho: float
    dof: int
    s: dict
    nu: dict
    c: dict
    accepted: dict
    late: dict
    replaced: dict
    serr: dict
    cp_sq: np.ndarray
    sq_plp: dict
    cross: dict
    counts: dict

    def rows(self, rows: slice) -> "Segment":
        """The segment restricted to a slice of states (views, no copy)."""
        def cut(d: dict) -> dict:
            return {k: v[rows] for k, v in d.items()}
        return Segment(self.name, self.rho, self.dof, cut(self.s), cut(self.nu), cut(self.c),
                       cut(self.accepted), cut(self.late), cut(self.replaced), cut(self.serr),
                       self.cp_sq[rows], cut(self.sq_plp), cut(self.cross), self.counts)


def block_means(values: np.ndarray, size: int = BLOCK) -> np.ndarray:
    """Means of consecutive blocks of ``size`` states (a remainder is dropped); NaN-aware."""
    values = np.asarray(values, dtype=np.float64)
    n_blocks = len(values) // size
    if n_blocks == 0:
        return np.zeros(0)
    with np.errstate(all="ignore"):
        return np.nanmean(values[: n_blocks * size].reshape(n_blocks, size), axis=1)


def sd_over_root(values: np.ndarray) -> float:
    """``SD(values, ddof = 1) / sqrt(n)`` over the finite values; NaN if fewer than 2."""
    values = np.asarray(values, dtype=np.float64)
    values = values[np.isfinite(values)]
    if values.size < 2:
        return math.nan
    return float(np.std(values, ddof=1) / math.sqrt(values.size))


def clustered_se(per_state: Sequence[np.ndarray]) -> tuple[float, float, float]:
    """The state-clustered SE and the batch-means SE of per-state fractions, and the larger.

    The first is ``SD(p_i, ddof = 1)/sqrt(n_states)`` (cluster-robust for equal cluster sizes with
    independent states); the second is the same over the means of consecutive blocks of 5 states
    (the study's dependence model; blocks are formed inside each segment). The larger is used (M3).
    """
    pooled = np.concatenate([np.asarray(p, dtype=np.float64) for p in per_state])
    blocks = np.concatenate([block_means(p) for p in per_state])
    cluster, batch = sd_over_root(pooled), sd_over_root(blocks)
    both = [x for x in (cluster, batch) if math.isfinite(x)]
    return cluster, batch, (max(both) if both else math.nan)


def _clean(value: object) -> object:
    """JSON-ready: NumPy scalars to Python, NaN to ``None`` (infinity is kept)."""
    if isinstance(value, dict):
        return {k: _clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_clean(v) for v in value]
    if isinstance(value, np.ndarray):
        return _clean(value.tolist())
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def doubling_stats(segments: Sequence[Segment], lo: int, hi: int, ref: int = REFERENCE_LEVEL,
                   tolerance: float = TOLERANCE) -> dict:
    """The per-estimate change of the whitened state from ``lo`` to ``hi`` iterations (M3).

    Over the estimates with no replacement at any probed level (their number is reported), the
    change ``||s_hi - s_lo||`` is divided by ``rho * nu_ref`` with ``nu`` at the ``ref``
    (30-iteration) estimate, whatever the doubling.

    Returns
    -------
    dict
        ``n``, ``n_excluded`` (replaced at some level), ``n_excluded_other`` (a non-finite or
        non-positive ``rho nu``), ``n_states_no_valid_draw`` and ``n_states_dropped_from_blocks``
        (states left out of the SEs: no valid draw, or the remainder of the blocks of 5), ``F``
        (the count above ``tolerance``), ``fraction``, the three SEs
        (``se_cluster``, ``se_block5``, ``se`` the larger), ``T`` (the sum of the ratios), the
        quantiles ``q50``, ``q90``, ``q99``, ``max`` and ``mean`` of the ratio, and ``F_true`` and
        ``fraction_true`` (above ``tolerance * ||s_ref - s_true||``, for comparison with WU-0005.4).
    """
    ratios, per_state, true_above, true_valid, excluded_n, other_n = [], [], 0, 0, 0, 0
    f_total, valid_total = 0, 0
    for seg in segments:
        keep = ~np.any(np.stack(list(seg.replaced.values())), axis=0)
        excluded_n += int((~keep).sum())
        change = np.linalg.norm(seg.s[hi] - seg.s[lo], axis=-1)
        scale = seg.rho * seg.nu[ref]
        with np.errstate(all="ignore"):
            ratio = change / scale
        good = keep & np.isfinite(ratio) & (scale > 0)
        other_n += int((keep & ~good).sum())
        above = good & (ratio > tolerance)
        n_valid = good.sum(axis=1)
        with np.errstate(all="ignore"):
            per_state.append(np.where(n_valid > 0, above.sum(axis=1) / np.maximum(n_valid, 1),
                                      np.nan))
        ratios.append(ratio[good])
        f_total += int(above.sum())
        valid_total += int(good.sum())
        cmp_ok = good & np.isfinite(seg.serr[ref])
        true_above += int((cmp_ok & (change > tolerance * seg.serr[ref])).sum())
        true_valid += int(cmp_ok.sum())
    pooled = np.concatenate(ratios) if ratios else np.zeros(0)
    cluster, batch, se = clustered_se(per_state) if per_state else (math.nan,) * 3
    n_empty = int(sum(np.isnan(p).sum() for p in per_state))      # no valid draw: left out of the SEs
    n_dropped = int(sum(len(p) % BLOCK for p in per_state))      # remainder of the blocks of 5
    quant = (np.quantile(pooled, [0.5, 0.9, 0.99]) if pooled.size else [math.nan] * 3)
    return _clean({
        "n": valid_total, "n_excluded": excluded_n, "n_excluded_other": other_n,
        "n_states_no_valid_draw": n_empty, "n_states_dropped_from_blocks": n_dropped,
        "F": f_total, "fraction": f_total / valid_total if valid_total else math.nan,
        "se_cluster": cluster, "se_block5": batch, "se": se,
        "T": float(pooled.sum()), "q50": quant[0], "q90": quant[1], "q99": quant[2],
        "max": float(pooled.max()) if pooled.size else math.nan,
        "mean": float(pooled.mean()) if pooled.size else math.nan,
        "F_true": true_above, "n_true": true_valid,
        "fraction_true": true_above / true_valid if true_valid else math.nan})


def chi2_stats(segments: Sequence[Segment], levels: Sequence[int], threshold: Callable[[int], float],
               ref: int = REFERENCE_LEVEL) -> dict:
    """The counts above ``c/rho^2 > chi2_{dof}(0.999)`` at each level, and the crossings (M8).

    ``threshold(dof)`` is ``gof_threshold``. Reports the count above at each level, the
    above-to-below and below-to-above transitions per doubling (the latter is 0 exactly, P1), the
    share of ``T`` and of ``F`` (the movers above the tolerance) that the above-to-below estimates
    carry, and the count still above at the last level.
    """
    out: dict = {"above": {str(k): 0 for k in levels}, "n": 0, "above_to_below": {},
                 "below_to_above": {}, "share_T": {}, "share_F": {},
                 "still_above_last": 0}
    pairs = [(a, b) for a, b in zip(levels, levels[1:]) if b == 2 * a]
    sums = {f"{a}->{b}": {"T": 0.0, "T_cross": 0.0, "F": 0, "F_cross": 0, "ab": 0, "ba": 0}
            for a, b in pairs}
    for seg in segments:
        thr = threshold(seg.dof) * seg.rho**2
        out["n"] += int(seg.c[levels[0]].size)
        above = {k: seg.c[k] > thr for k in levels}
        for k in levels:
            out["above"][str(k)] += int(above[k].sum())
        out["still_above_last"] += int(above[levels[-1]].sum())
        keep = ~np.any(np.stack(list(seg.replaced.values())), axis=0)
        scale = seg.rho * seg.nu[ref]
        for a, b in pairs:
            row = sums[f"{a}->{b}"]
            cross = above[a] & ~above[b]
            row["ab"] += int(cross.sum())
            row["ba"] += int((~above[a] & above[b]).sum())
            with np.errstate(all="ignore"):
                ratio = np.linalg.norm(seg.s[b] - seg.s[a], axis=-1) / scale
            good = keep & np.isfinite(ratio) & (scale > 0)
            moving = good & (ratio > TOLERANCE)
            row["T"] += float(ratio[good].sum())
            row["T_cross"] += float(ratio[good & cross].sum())
            row["F"] += int(moving.sum())
            row["F_cross"] += int((moving & cross).sum())
    for label, row in sums.items():
        out["above_to_below"][label] = row["ab"]
        out["below_to_above"][label] = row["ba"]
        out["share_T"][label] = row["T_cross"] / row["T"] if row["T"] > 0 else math.nan
        out["share_F"][label] = row["F_cross"] / row["F"] if row["F"] > 0 else math.nan
    return _clean(out)


def p1_stats(segments: Sequence[Segment], levels: Sequence[int]) -> dict:
    """Per-estimate P1 (exact): the cost never rises and the accepted count never falls.

    Counts, per doubling, the estimates with ``c_2k > c_k`` and with ``accepted_2k < accepted_k``;
    both must be 0 (a violation is a finding, not a tolerance).
    """
    out = {}
    for a, b in zip(levels, levels[1:]):
        out[f"{a}->{b}"] = {
            "c_increase": sum(int((seg.c[b] > seg.c[a]).sum()) for seg in segments),
            "accepted_decrease": sum(int((seg.accepted[b] < seg.accepted[a]).sum())
                                     for seg in segments)}
    return out


def weight_star(sq_cp: np.ndarray, sq_plp: np.ndarray, cross: np.ndarray) -> np.ndarray:
    """``w* = clip((E_P - C)/max(E_C + E_P - 2C, 1e-300), 0, 1)``, the formula of ``oracle_weight``."""
    curvature = sq_cp + sq_plp - 2.0 * cross
    return np.clip((sq_plp - cross) / np.maximum(curvature, 1e-300), 0.0, 1.0)


def weight_class(w: np.ndarray) -> np.ndarray:
    """0 where ``w = 0``, 2 where ``w = 1``, else 1."""
    return np.where(w == 0.0, 0, np.where(w == 1.0, 2, 1))


def eligible(sq_cp: np.ndarray, sq_plp: np.ndarray, limit: float) -> np.ndarray:
    """H2a(i) eligibility: a leading run of at least two small horizons (both r.m.s. <= ``limit``).

    The arrays are ``(n, nH_long)`` over the long horizons in order (1, 2, 4 Lyapunov times).
    """
    small = (np.sqrt(sq_cp) <= limit) & (np.sqrt(sq_plp) <= limit)
    return np.cumprod(small, axis=1).sum(axis=1) >= 2


def transitions(before: np.ndarray, after: np.ndarray, n_classes: int) -> np.ndarray:
    """Counts of states by (class before, class after), an ``(n_classes, n_classes)`` matrix."""
    out = np.zeros((n_classes, n_classes), dtype=int)
    np.add.at(out, (np.asarray(before), np.asarray(after)), 1)
    return out


def mse_change(sq_lo: np.ndarray, sq_hi: np.ndarray) -> dict:
    """Relative change of the per-state PLP MSE at H_ref between two levels (M3).

    ``|mse_hi - mse_lo| / mse_lo`` where ``mse_lo > 0``; states with ``mse_lo = 0`` are counted
    and left out. Reports the median, the mean, the 0.9 and 0.99 quantiles, and the counts.
    """
    defined = sq_lo > 0
    with np.errstate(all="ignore"):
        rel = np.abs(sq_hi - sq_lo)[defined] / sq_lo[defined]
    q = np.quantile(rel, [0.5, 0.9, 0.99]) if rel.size else [math.nan] * 3
    return _clean({"n_states": int(len(sq_lo)), "n_zero_denominator": int((~defined).sum()),
                   "median": q[0], "q90": q[1], "q99": q[2],
                   "mean": float(rel.mean()) if rel.size else math.nan,
                   "n_changed": int((sq_hi != sq_lo).sum())})


def group_report(segments: Sequence[Segment], levels: Sequence[int], threshold: Callable[[int], float],
                 *, ref_column: int, long_columns: Sequence[int], limit: float,
                 ref: int = REFERENCE_LEVEL) -> dict:
    """Everything Part A reports for one group of segments (one QoI's PLP inputs).

    Returns ``doublings`` (``doubling_stats`` for each ``k -> 2k``), ``chi2``, ``p1``, ``mse_href``
    (``mse_change`` per doubling, over the concatenated states), ``w_star`` and ``eligibility``
    (transition matrices per doubling, over the states of the group), the sizes, and ``tail_ratio``
    (``r_A`` of rule R, ``None`` unless the levels 30, 60 and 120 are all present).
    """
    pairs = [(a, b) for a, b in zip(levels, levels[1:]) if b == 2 * a]
    out: dict = {"n_segments": len(segments), "n_states": int(sum(len(s.cp_sq) for s in segments)),
                 "n_estimates": int(sum(s.c[levels[0]].size for s in segments)),
                 "doublings": {f"{a}->{b}": doubling_stats(segments, a, b, ref) for a, b in pairs},
                 "chi2": chi2_stats(segments, levels, threshold, ref), "p1": p1_stats(segments, levels),
                 "mse_href": {}, "w_star": {}, "eligibility": {}}
    cp = np.concatenate([s.cp_sq for s in segments])
    for a, b in pairs:
        label = f"{a}->{b}"
        sq = {k: np.concatenate([s.sq_plp[k] for s in segments]) for k in (a, b)}
        cr = {k: np.concatenate([s.cross[k] for s in segments]) for k in (a, b)}
        out["mse_href"][label] = mse_change(sq[a][:, ref_column], sq[b][:, ref_column])
        w = {k: weight_class(weight_star(cp[:, ref_column], sq[k][:, ref_column],
                                         cr[k][:, ref_column])) for k in (a, b)}
        out["w_star"][label] = transitions(w[a], w[b], 3).tolist()
        el = {k: eligible(cp[:, long_columns], sq[k][:, long_columns], limit).astype(int)
              for k in (a, b)}
        out["eligibility"][label] = transitions(el[a], el[b], 2).tolist()
    d = out["doublings"]
    out["tail_ratio"] = None
    if all(f"{a}->{2 * a}" in d for a in (30, 60)):
        out["tail_ratio"] = tail_ratio(d["30->60"]["F"], d["60->120"]["F"], d["30->60"]["T"],
                                       d["60->120"]["T"])
    return _clean(out)


def pooled_summary(segments: Sequence[Segment], level: int, lm_summary: Callable) -> tuple[dict, dict]:
    """The pooled ``lm_summary`` and the ``LM_COUNTS`` sums of segments at one level.

    ``lm_summary`` is ``lpcstudy.estimation.lm_summary`` (passed in, so that the tool imports no jax
    at module level). The residual, accepted and late arrays are flattened and joined in the order
    given, as ``pipeline._lm_arrays`` does.
    """
    first = segments[0]
    joined = [np.concatenate([getattr(s, name)[level].ravel() for s in segments])
              for name in ("c", "accepted", "late")]
    summary = lm_summary(*joined, first.rho, first.dof)
    counts = {name: sum(int(s.counts[level][name]) for s in segments) for name in LM_COUNTS}
    return summary, counts


def compare_p0(stored_lm: Mapping, stored_counts: Mapping, summary: Mapping,
               counts: Mapping) -> list[str]:
    """P0 (exact): the probe's pooled summary and counts equal the stored ones; mismatches listed.

    ``None`` equals ``None``; floats are compared with ``==`` (the same arrays through the same
    code, so equal bit for bit). Keys of the stored ``lm`` block that the summary lacks
    (``by_kind``) are ignored; every key of the summary must match.
    """
    bad = [f"lm.{k}: stored {stored_lm.get(k)!r}, probe {v!r}" for k, v in summary.items()
           if stored_lm.get(k, object()) != v]
    bad += [f"counts.{k}: stored {stored_counts.get(k)!r}, probe {counts[k]!r}"
            for k in LM_COUNTS if stored_counts.get(k) != counts[k]]
    return bad


# --------------------------------------------------------------------------------------------
# Part A: the probe (capture; imports lpcstudy and jax lazily)
# --------------------------------------------------------------------------------------------
def thread_environment(env: Mapping[str, str]) -> dict[str, str]:
    """The environment of a probe run: the same as ``tools/run_preset.sh`` for ``LPC_THREADS``.

    ``LPC_THREADS`` (1 to 99, default 4) sets ``OMP``, ``MKL`` and ``OPENBLAS`` threads and the XLA
    CPU pools (``PJRT_NPROC``, ``NPROC``); the device is the CPU and preallocation is off. ``P0``
    needs the arm's own value (8 at pilot), so the probe must not default to another.

    Raises
    ------
    ValueError
        If ``LPC_THREADS`` is set and is not an integer from 1 to 99.
    """
    threads = env.get("LPC_THREADS", "") or "4"
    if re.fullmatch(r"[1-9][0-9]?", threads) is None:
        raise ValueError(f"LPC_THREADS must be an integer from 1 to 99, got {threads!r}")
    out = {name: threads for name in THREAD_VARIABLES}
    out.update(LPC_THREADS=threads, JAX_PLATFORMS="cpu", XLA_PYTHON_CLIENT_PREALLOCATE="false")
    return out


def running_presets(run: Callable = subprocess.run) -> list[str]:
    """The command lines of active ``lpcstudy --preset`` runs (``pgrep -fa``); fail closed.

    Raises
    ------
    RuntimeError
        If ``pgrep`` itself fails (exit code other than 0 or 1).
    """
    done = run(["pgrep", "-fa", "[l]pcstudy --preset"], capture_output=True, text=True,
               check=False)
    if done.returncode == 1:
        return []
    if done.returncode != 0:
        raise RuntimeError(f"pgrep failed with exit code {done.returncode}")
    return [line for line in done.stdout.splitlines() if line.strip()]


def refuse_reason(preset: str, seed_id: str, steps: Sequence[int], argv: Sequence[str]) -> str | None:
    """Why a probe request is refused (``None`` if allowed): the sealed run, seed ids, presets, levels."""
    if any("confirmatory" in a.lower() for a in argv):
        return "an argument names the confirmatory path, which is owner-only (LPC.PC.7)"
    if re.fullmatch(r"DEV-(0|[1-9][0-9]*)", seed_id) is None:
        return "the seed id must be a registered DEV-n id (LPC.PC.7)"
    if preset not in ("smoke", "pilot"):
        return "the probe runs the smoke and pilot presets only (never full)"
    if (len(steps) < 2 or steps[0] != 15 or any(b != 2 * a for a, b in zip(steps, steps[1:]))
            or REFERENCE_LEVEL not in steps):
        return "--steps must be 15 and its doublings (15 30 60 120), including 30"
    return None


PRECONDITION_ENV = ("LPC_THREADS", *THREAD_VARIABLES, "XLA_FLAGS", "JAX_PLATFORMS")
PRECONDITION_PACKAGES = ("jax", "jaxlib")


def current_commit() -> str | None:
    """``git rev-parse HEAD`` of the repository of this tool, or ``None`` if git fails."""
    done = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True,
                          text=True, check=False)
    return done.stdout.strip() if done.returncode == 0 and done.stdout.strip() else None


def precondition_mismatches(provenance: Mapping, env: Mapping[str, str | None],
                            versions: Mapping[str, str | None], commit: str | None
                            ) -> list[str]:
    """Where an arm's recorded run differs from this process (M6: P0 needs the same).

    P0 is exact only for the same commit, host, ``LPC_THREADS``, ``XLA_FLAGS`` and jax and jaxlib
    (a different batch shape or thread pool changes the result by round-off, E1(a)), so the probe
    refuses to spend hours on an arm it cannot reproduce. Compares ``provenance.commit`` with
    ``commit``, ``provenance.env`` for the names of ``PRECONDITION_ENV`` (a name that is not
    recorded is a mismatch) and the versions of ``PRECONDITION_PACKAGES``. The host is not
    compared here (``compare`` lists the CPU model of every arm in ``pairing_notes``).
    """
    stored = provenance.get("env")
    if not isinstance(stored, Mapping):
        return ["no env block in the recorded provenance"]
    out = [] if provenance.get("commit") == commit else [
        f"commit: recorded {provenance.get('commit')!r}, here {commit!r}"]
    out += [f"{name}: recorded {stored.get(name, 'not recorded')!r}, here {env.get(name)!r}"
            for name in PRECONDITION_ENV if name not in stored or stored[name] != env.get(name)]
    packages = provenance.get("packages") or {}
    out += [f"{name}: recorded {packages.get(name)!r}, here {versions.get(name)!r}"
            for name in PRECONDITION_PACKAGES if packages.get(name) != versions.get(name)]
    return out


def pairing_notes(arms: Mapping[int, Mapping]) -> list[str]:
    """Differences between the arms' recorded runs that can break the bitwise pairing C0 (notes).

    The commit, the CPU model, ``LPC_THREADS``, ``XLA_FLAGS`` and the jax and jaxlib versions should
    be the same in every arm (plan: same host, commit and ``LPC_THREADS``). Information only: a C0
    failure on arms that differ here has a known candidate cause, but still halts the study.
    """
    def facts(arm: Mapping) -> dict:
        prov = arm.get("provenance") or {}
        env = prov.get("env") or {}
        return {"commit": prov.get("commit"), "cpu": (prov.get("cpu") or {}).get("model"),
                "LPC_THREADS": env.get("LPC_THREADS"), "XLA_FLAGS": env.get("XLA_FLAGS"),
                **{n: (prov.get("packages") or {}).get(n) for n in PRECONDITION_PACKAGES}}
    base = {k: facts(a) for k, a in arms.items()}
    first = min(base)
    return [f"{name}: {base[first][name]!r} at {first}, {base[k][name]!r} at {k}"
            for k in sorted(base) if k != first for name in base[first]
            if base[k][name] != base[first][name]]


def derive_estimator(estimator, steps: int):
    """The estimator ``estimator`` with ``steps`` Levenberg-Marquardt iterations and no cached program.

    ``StateEstimator._fn`` is an init field and ``dataclasses.replace`` copies it, so once the source
    estimator has been called a plain ``replace(estimator, refine_steps=k)`` keeps running the
    cached program of the source's own iteration count and the doubling would read zero. Passing
    ``_fn=None`` rebuilds the program for ``steps`` (the network object is shared). The library
    should harden this (``field(init=False)``, a later unit); the tool does not change it.
    """
    import dataclasses
    return dataclasses.replace(estimator, refine_steps=steps, _fn=None)


def chunk_rows(n_states: int, n_draws: int, chunk_traj: int = CHUNK_TRAJ) -> list[np.ndarray]:
    """The row chunks of ``ensemble_moments`` and ``evaluation_draws``: ``max(1, chunk // M)`` states.

    At pilot (M = 200) that is 30 states: 600 = 20 x 30, 300 = 10 x 30, 500 = 16 x 30 + 20. P0
    needs these shapes (a different batch shape changes the result by up to 3e-9, E1(a)).
    """
    per_chunk = max(1, chunk_traj // n_draws)
    return [np.arange(start, min(n_states, start + per_chunk))
            for start in range(0, n_states, per_chunk)]


class Recorder:
    """Wraps an estimator to keep the per-estimate replacement flags of each call.

    ``forecast_draws`` calls only ``estimate_counted`` and reduces the flags to per-state counts,
    so the probe needs them from here (the exclusion of replaced estimates is per estimate, M3).
    """

    def __init__(self, inner) -> None:
        self.inner = inner
        self.flags: list[np.ndarray] = []

    def estimate_counted(self, inputs):
        """The inner call; the OR of its two flags is appended to ``flags``."""
        out = self.inner.estimate_counted(inputs)
        self.flags.append(np.asarray(out[2]) | np.asarray(out[3]))
        return out


@dataclass(frozen=True)
class Spec:
    """A segment to probe: where its inputs come from."""

    cell: str
    kind: str
    split: str
    rho: float
    rows: slice
    n_draws: int
    core: bool

    @property
    def name(self) -> str:
        """``<cell id>/<kind>/<split>``, the key of the segment."""
        return f"{self.cell}/{self.kind}/{self.split}"


def segment_specs(cfg) -> list[Spec]:
    """The segments of one system (M4): the core cell (all splits, oracle and eval draws) and the
    test rows 0 to ``n_test_sweep - 1`` of every noise-sweep cell at a noise other than the core's."""
    from lpcstudy.data import SPLITS
    from lpcstudy.pipeline import cell_id
    core_id = cell_id("base", cfg.core_noise, cfg.core_library, True)
    specs = [Spec(core_id, "oracle", s, cfg.core_noise, slice(None), cfg.n_oracle_draws, True)
             for s in SPLITS]
    specs += [Spec(core_id, "eval", s, cfg.core_noise, slice(None), cfg.n_eval_draws, True)
              for s in SPLITS]
    for rho in cfg.noise_levels:
        if rho != cfg.core_noise:
            specs.append(Spec(cell_id("base", rho, cfg.core_library, False), "oracle", "test", rho,
                              slice(0, cfg.n_test_sweep), cfg.n_oracle_draws, False))
    return specs


def groups_of(specs: Sequence[Spec], cfg) -> dict[str, list[tuple[str, slice]]]:
    """The segments feeding each QoI (M4): ``(segment name, row slice)`` per group."""
    core_test = next(s for s in specs if s.core and s.kind == "oracle" and s.split == "test")
    sweep = slice(0, cfg.n_test_sweep)
    core_oracle = [s for s in specs if s.core and s.kind == "oracle"]
    return {
        "H2a": [(core_test.name, slice(None))],
        "H2b(i)": [(core_test.name, sweep), *[(s.name, slice(None)) for s in specs
                                                 if not s.core]],
        "H2b(ii)": [(core_test.name, sweep)],
        "H3c": [(s.name, slice(None)) for s in [*core_oracle,
                                                 *[s for s in specs if s.kind == "eval"]]],
        "all": [(s.name, slice(None)) for s in specs]}


def capture_segment(study, setup, library, spec: Spec, estimators: Mapping[int, object],
                    horizons: np.ndarray, ref_horizon: int, chunk_traj: int = CHUNK_TRAJ
                    ) -> Segment:
    """Estimate one segment at every level through ``forecast_draws`` in the pipeline's chunks.

    ``estimators`` maps each level to the estimator of ``setup`` rebuilt for it
    (``derive_estimator``); the compiled programs are kept across the segments of one noise level.
    The path and amplification caches of ``setup`` are shared (they do not depend on the estimator).
    """
    import dataclasses
    from lpcstudy.ensemble import DRAW_COLUMN, forecast_draws
    levels = tuple(estimators)
    ctx = setup.ctx
    purpose = "oracle" if spec.kind == "oracle" else "eval"
    noise = study.unit_noise(ctx, spec.split, purpose, spec.n_draws, ctx.embed_dim)[spec.rows]
    n_states = noise.shape[0]
    times = ctx.split_indices[spec.split][np.arange(n_states)]
    truth_w = ctx.whiten_states(ctx.eval_states[times])
    seg = dict(s={}, nu={}, c={}, accepted={}, late={}, replaced={}, serr={}, sq_plp={}, cross={},
               counts={})
    cp_sq = None
    for level in levels:
        recorder = Recorder(estimators[level])
        level_setup = dataclasses.replace(setup, estimator=recorder)
        parts: dict[str, list] = {k: [] for k in ("s", "nu", "c", "acc", "late", "sq_plp", "cross",
                                                    "cp_sq", "handled")}
        for rows in chunk_rows(n_states, spec.n_draws, chunk_traj):
            batch = forecast_draws(level_setup, library, spec.split, rows, noise[rows], horizons,
                                   ref_horizon)
            flat = batch.est_states.reshape(-1, batch.est_states.shape[-1])
            parts["s"].append(ctx.whiten_states(flat).reshape(batch.est_states.shape))
            parts["nu"].append(batch.est_nu)
            parts["c"].append(batch.lm_residual)
            parts["acc"].append(batch.lm_accepted)
            parts["late"].append(batch.lm_late)
            parts["sq_plp"].append((batch.plp_err**2).mean(axis=1))
            parts["cross"].append((batch.cp_err * batch.plp_err).mean(axis=1))
            parts["cp_sq"].append((batch.cp_err**2).mean(axis=1))
            parts["handled"].append(batch.handled)
        join = {k: np.concatenate(v) for k, v in parts.items()}
        seg["s"][level], seg["nu"][level] = join["s"], join["nu"]
        seg["c"][level], seg["accepted"][level] = join["c"], join["acc"]
        seg["late"][level] = join["late"]
        seg["replaced"][level] = np.concatenate(
            [f.reshape(len(r), spec.n_draws) for f, r in zip(
                recorder.flags, chunk_rows(n_states, spec.n_draws, chunk_traj))])
        seg["serr"][level] = np.linalg.norm(join["s"] - truth_w[:, None, :], axis=-1)
        seg["sq_plp"][level], seg["cross"][level] = join["sq_plp"], join["cross"]
        seg["counts"][level] = {name: int(join["handled"][:, DRAW_COLUMN[name]].sum())
                                for name in LM_COUNTS}
        if cp_sq is None:
            cp_sq = join["cp_sq"]
        elif not np.array_equal(cp_sq, join["cp_sq"]):
            raise RuntimeError(f"{spec.cell}/{spec.kind}/{spec.split}: the CP errors changed with "
                               "the iteration count (they must not): a defect")
    return Segment(f"{spec.cell}/{spec.kind}/{spec.split}", spec.rho,
                   ctx.embed_dim - ctx.spec.dim, cp_sq=cp_sq, **seg)


def p0_report(system: Mapping, specs: Sequence[Spec], segments: Mapping[str, Segment],
              arm: int, lm_summary: Callable) -> dict:
    """P0 at one arm: for each cell and kind, the probe's pooled summary against the stored one."""
    out: dict = {"arm": arm, "mismatches": []}
    cells = (system.get("handling") or {}).get("cells") or {}
    done = set()
    for spec in specs:
        if (spec.cell, spec.kind) in done:
            continue
        done.add((spec.cell, spec.kind))
        mine = [segments[s.name] for s in specs if (s.cell, s.kind) == (spec.cell, spec.kind)]
        record = cells.get(spec.cell)
        stored = _walk(record, ("lm", "by_kind", spec.kind))
        stored_counts = _walk(record, ("by_kind", spec.kind, "counts"))
        if not isinstance(stored, Mapping) or not isinstance(stored_counts, Mapping):
            out["mismatches"].append(f"{spec.cell}/{spec.kind}: no stored lm summary")
            continue
        summary, counts = pooled_summary(mine, arm, lm_summary)
        out["mismatches"] += [f"{spec.cell}/{spec.kind}: {m}"
                              for m in compare_p0(stored, stored_counts, summary, counts)]
    return out


def run_probe(args: argparse.Namespace) -> int:
    """The ``probe`` subcommand (see the module docstring)."""
    reason = refuse_reason(args.preset, args.seed_id, args.steps, args.argv)
    if reason is not None:
        print(f"lm_doubling.py: refused: {reason}", file=sys.stderr)
        return EXIT_REFUSED
    try:
        env = thread_environment(os.environ)
        active = running_presets()
    except (ValueError, RuntimeError) as error:
        print(f"lm_doubling.py: refused: {error}", file=sys.stderr)
        return EXIT_REFUSED
    if active:
        print("lm_doubling.py: refused: a preset run is active: " + "; ".join(active)[:200],
              file=sys.stderr)
        return EXIT_REFUSED
    lock_path = Path(os.environ.get("LPC_GPU_LOCK", "/tmp/lpcstudy-gpu.lock"))
    handle = open(lock_path, "a")  # held until the process ends
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        handle.close()
        print(f"lm_doubling.py: GPU busy (lock {lock_path} is held): do other work",
              file=sys.stderr)
        return EXIT_BUSY
    if any(os.environ.get(k) != v for k, v in env.items()):  # BLAS reads its threads at import
        os.environ.update(env)
        os.execv(sys.executable, [sys.executable, *sys.argv])
    from lpcstudy.estimation import gof_threshold, lm_summary
    from lpcstudy.ensemble import AnalogLibrary
    from lpcstudy.pipeline import Study
    from lpcstudy.seeds import REGISTRY_PATH, load_registry, resolve_dev_seed, with_seed
    start = time.time()
    seed = resolve_dev_seed(args.seed_id, load_registry(REGISTRY_PATH))
    cfg = with_seed(PRESETS[args.preset], args.seed_id, seed)
    systems = args.systems or list(cfg.core_systems)
    out_dir = Path(args.out) / args.preset
    stored = {int(k): json.loads(find_results(p).read_text()) for k, p in
              (item.split("=", 1) for item in args.results)}
    from importlib import metadata
    versions = {name: metadata.version(name) for name in PRECONDITION_PACKAGES}
    commit = current_commit()
    for arm, results in stored.items():
        wrong = precondition_mismatches(results.get("provenance") or {}, dict(os.environ), versions,
                                        commit)
        if wrong:
            print(f"lm_doubling.py: refused: the {arm} arm was run in another environment, so P0 "
                  "cannot hold: " + "; ".join(wrong), file=sys.stderr)
            return EXIT_REFUSED
    out_dir.mkdir(parents=True, exist_ok=True)
    study = Study(cfg, out_dir)
    horizons = np.array([h for h in cfg.eval_horizons if h >= cfg.steps_per_lyapunov], dtype=int)
    ref_column = int(np.nonzero(horizons == cfg.reference_horizon)[0][0])
    long_columns = list(range(len(horizons)))
    report: dict = {"schema": "lpcstudy.lm-probe/1", "label": LABEL, "preset": args.preset,
                    "seed_id": args.seed_id, "levels": list(args.steps), "horizons": horizons.tolist(),
                    "environment": env, "systems": {}, "halt": []}
    arrays: dict[str, np.ndarray] = {}
    for system in systems:
        t0 = time.time()
        ctx = study.context(system)
        specs = segment_specs(cfg)
        segments: dict[str, Segment] = {}
        libraries, estimators = {}, {}
        for spec in specs:
            setup = study.setup(ctx, spec.rho)
            if spec.rho not in libraries:
                libraries[spec.rho] = AnalogLibrary.build(ctx, spec.rho, cfg.core_library,
                                                           cfg.horizon_max)
                estimators[spec.rho] = {level: derive_estimator(setup.estimator, level)
                                        for level in args.steps}
            segment = capture_segment(study, setup, libraries[spec.rho], spec,
                                      estimators[spec.rho], horizons, cfg.reference_horizon)
            segments[segment.name] = segment
            print(f"{system}: {segment.name} captured at {list(args.steps)} "
                  f"({time.time() - t0:.0f}s into the system)", flush=True)
        groups = {}
        for group, members in groups_of(specs, cfg).items():
            parts = [segments[name].rows(rows) for name, rows in members]
            groups[group] = group_report(parts, args.steps, gof_threshold, ref_column=ref_column,
                                         long_columns=long_columns, limit=cfg.linear_regime_rms)
        p0 = [p0_report(stored[arm].get("systems", {}).get(system) or {}, specs, segments, arm,
                        lm_summary) for arm in args.steps if arm in stored]
        print(f"{system}: groups and P0 done ({time.time() - t0:.0f}s)", flush=True)
        report["systems"][system] = {"groups": groups, "p0": p0, "seconds": time.time() - t0,
                                     "segments": [s.name for s in specs]}
        for entry in p0:
            report["halt"] += [f"P0 {system} @{entry['arm']}: {m}" for m in entry["mismatches"]]
        for label, row in groups["all"]["p1"].items():
            if row["c_increase"] or row["accepted_decrease"]:
                report["halt"].append(f"P1 {system} {label}: {row}")
        for name, seg in segments.items():
            for level in args.steps:
                key = f"{system}/{name}/{level}"
                arrays[f"{key}/sq_plp"], arrays[f"{key}/cross"] = seg.sq_plp[level], seg.cross[level]
                if args.per_estimate:
                    arrays[f"{key}/c"], arrays[f"{key}/nu"] = seg.c[level], seg.nu[level]
                    arrays[f"{key}/s"] = seg.s[level]
                    arrays[f"{key}/serr"] = seg.serr[level]
            arrays[f"{system}/{name}/cp_sq"] = seg.cp_sq
    report["seconds"] = time.time() - start
    path = out_dir / f"probe_{args.preset}.json"
    path.write_text(json.dumps(_clean(report), indent=1) + "\n")
    np.savez_compressed(out_dir / f"probe_{args.preset}.npz", **arrays)
    print(f"probe written: {path} ({report['seconds']:.0f}s)")
    for line in report["halt"]:
        print(f"HALT (a finding, /refer): {line}")
    return 1 if report["halt"] else 0


# --------------------------------------------------------------------------------------------
# Command line
# --------------------------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    """The command-line parser (abbreviations off)."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0], allow_abbrev=False)
    sub = parser.add_subparsers(dest="command", required=True)
    cmp_ = sub.add_parser("compare", allow_abbrev=False)
    cmp_.add_argument("runs", nargs="+", help="the 15, 30 and optional 60 run (dir or results.json)")
    cmp_.add_argument("--probe", default=None, help="probe_<preset>.json of Part A")
    cmp_.add_argument("--json", default=None, help="write the report as JSON")
    probe = sub.add_parser("probe", allow_abbrev=False)
    probe.add_argument("--preset", required=True)
    probe.add_argument("--seed-id", required=True)
    probe.add_argument("--out", required=True)
    probe.add_argument("--steps", type=int, nargs="+", default=list(LEVELS))
    probe.add_argument("--systems", nargs="*", default=None)
    probe.add_argument("--results", nargs="*", default=[], metavar="K=PATH",
                       help="Part B runs for P0, as 15=DIR 30=DIR ...")
    probe.add_argument("--per-estimate", action="store_true",
                       help="also write per-estimate s, nu, c and the errors (large)")
    same = sub.add_parser("identical", allow_abbrev=False)
    same.add_argument("a")
    same.add_argument("b")
    return parser


def run_compare(args: argparse.Namespace) -> int:
    """The ``compare`` subcommand."""
    if not 2 <= len(args.runs) <= 3:
        print("compare needs RUN15 RUN30 [RUN60]", file=sys.stderr)
        return 2
    try:
        arms = {k: json.loads(find_results(p).read_text()) for k, p in zip(ARMS, args.runs)}
        probe = json.loads(Path(args.probe).read_text()) if args.probe else None
    except (OSError, ValueError) as error:
        print(f"compare: {error}", file=sys.stderr)
        return 2
    report = build_comparison(arms, probe)
    print("\n".join(render(report)))
    if probe is not None:
        print("\n".join(["", *render_probe(probe)]))
        report["halt"] = [*report["halt"], *(probe.get("halt") or [])]
    if args.json:
        Path(args.json).write_text(json.dumps(_clean(report), indent=1) + "\n")
    return 1 if report["halt"] else 0


def run_identical(args: argparse.Namespace) -> int:
    """The ``identical`` subcommand (K3): 0 if the two files differ in no compared leaf."""
    try:
        a = json.loads(find_results(args.a).read_text())
        b = json.loads(find_results(args.b).read_text())
    except (OSError, ValueError) as error:
        print(f"identical: {error}", file=sys.stderr)
        return 2
    diffs = differing_leaves(a, b)
    n_leaves = len({p for p in flatten(a) if not excluded(p)})
    print(f"{n_leaves} leaves compared (provenance and 'seconds' excluded); "
          f"{len(diffs)} differ")
    for path in diffs[:20]:
        print("  differs: " + "/".join(map(str, path)))
    return 1 if diffs else 0


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point."""
    args = build_parser().parse_args(argv)
    args.argv = list(sys.argv[1:] if argv is None else argv)
    return {"compare": run_compare, "probe": run_probe, "identical": run_identical}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
