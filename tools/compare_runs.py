#!/usr/bin/env python3
"""Compare two ``results.json`` files under the reproducibility tiers of WU-0003 A6 (WU-0003.9).

Usage::

    python3 -I tools/compare_runs.py REF NEW [--tol-other X] [--show N] [--all]
        [--allow-not-computed] [--td-only]

``REF`` and ``NEW`` are ``results.json`` files, or run directories that contain one. The tool is
read-only on both and writes nothing but its report to standard output. It reads statistics and
computes none of the study's; it computes the comparison only. It imports ``tools/compare_pilot.py``
(flattening and the chain tags of its rule table) and the standard library, and no ``lpcstudy``
module. The report is labelled DEVELOPMENT.

**Needs owner review before freeze** (tolerance and verdict-comparison code, CSQ2 use in WU-0016;
plan A10, B2 row .9). Every tolerance below is quoted from the plan, never chosen here; where the
plan is silent the strict reading is applied and printed (see "Readings that the plan leaves open").

Tier selection (A6, amended by B1 item 1; mechanical, from the digests)
-----------------------------------------------------------------------
Per system, from the ``context`` leaves, with ``provenance`` for the device:

* **TD** if any of ``state_mean_digest``, ``lambda_max``, ``interval``, ``start_state`` (main or
  estimator), ``main_digest``, ``estimator_digest`` differs.
* else **T2** if a ``whiten_digest`` or ``unwhiten_digest`` (W or U) differs (a ``cov_digest``
  difference alongside counts too); a ``cov_digest`` difference alone, with W and U equal, matches no tier
  of A6 and is left undetermined (exit 2; owner reading, since T2's LM bands are looser than T1's); else **T3** if a weight digest differs (``estimators/*/weights_digest``,
  ``validation/estimators/*/weights_digest``, ``fitted/allocator_digest``).
* else **T0** if the host (platform and CPU model), the device (backend, kind, count) and
  ``LPC_THREADS`` are all equal, else **T1** (the device differs).
* The pair gets the highest tier of any system (TD over T2 over T3 over T1 over T0).
* A selecting leaf that either run lacks (checked per leaf group on both runs: each of the six
  triggers with both ``start_state`` parts, the three W/U digests, ``allocator_digest``, at least one
  validation estimator digest, the top-level estimator digests), or whose leaf set differs, gives
  "tier undetermined": no tolerance is applied, and the exit code is 2.

Tolerances applied to a pair (A6 and B1 items 2 to 5)
-----------------------------------------------------
* **T0, CPU:** every leaf bitwise (IEEE bytes), except timing (keys ``seconds``) and the top-level
  ``provenance``. On a non-CPU device of one type (GPU against GPU, the R1 against R2 measurement)
  a float difference is the measurement of the 10x rule below, and every other leaf stays exact.
* **T1:** chain tags ``cp``, ``oracle``, ``dynamics``, ``fixture`` (tags of ``compare_pilot``'s rule
  table) ``|d| <= 1e-12 |ref|``; V1 (``delay_jacobian_rel_err``, ``gain_rel_err``) ``|d| <= 1e-12``
  absolute; V2 (``crlb_ratio_*``) ``|d| <= 1e-10 |ref|``; LM summaries ``fraction_no_decrease``
  exact, ``median_iterations`` within 1, the other LM summaries within ``1e-8 |ref|``; the
  per-estimate LM check of B1 item 2 (``lm_estimate_check``); QoIs and interval endpoints
  (class a) ``|d| <= 1e-4 s`` with ``s = max(|lo|, |hi|)`` of the reference interval.
* **T2, T3:** as T1, except the LM summaries of the "T2 rules": ``fraction_no_decrease`` within
  ``3 sqrt(2 pbar (1 - pbar) / n) + 1/n`` (WU-0005.4 M7(ii)), ``median_iterations`` within 1, and
  the order-statistic bands for ``median_residual`` and ``p95_residual`` (``order_statistic_band``).
  T2 applies the T2 rules to every LM summary. T3 ("network chain as T2; other chains as T1") applies
  them to the ``eval`` kind only; the ``oracle`` and ``check`` kinds and the pooled summary keep the
  T1 rules (strict default; the kind-to-chain map is a question for the mathematician).
* **In T1 to T3:** a leaf with an interval, in a result block where a discrete count of A6's list
  differs, is allowed ``|d| <= 0.1 hw`` instead of its tolerance (hw of the reference interval). The
  list is exactly A6's, unchanged by B1 item 3 (``licensing_kind``): K (``chosen_K``, ``realized_K``),
  ``best_single``, ``n_states`` and the state denominators, and clip, nu-cap and replacement counts
  (``error_clips*``, ``nu_cap_clips``, ``*_replacements``). The scope is per system and causal: a
  ``n_states`` or ``best_single`` reaches its own block; K reaches ``fitted``, ``H3a``, ``H3c`` and
  ``regime_curve``; a clip, nu-cap or replacement count under ``systems/<s>/handling`` reaches system
  ``s`` only. The top-level ``handling`` block (``totals``, ``by_system``, ``robustness``), a per-system
  ``totals`` mirror and a state denominator open no scope (the per-system source of a sum carries
  it). Any other differing integer is exact (a failure), including the other ``handling`` counters, LM
  ``n_estimates``, non-finite, warning, fallback and failed-resample counts; only integers inside a
  K-shaped block of a system whose K differs are listed as following K. A difference of the new
  integers (``nfev``, ``status``, ``a5_leaf_digest``) is printed beside the differences it may explain
  and licenses nothing (OF-1, working default). A leaf only on one side is a failure, except where a
  K or a count of its own block differs (the length follows the count).
* **Every verdict must be identical** (T0 to T3): a flag or verdict string that differs prints a
  ``DEF`` line. In TD the verdicts are reported only.
* **TD:** no per-leaf tolerance. Per primary part (6 parts per system, 18 over three systems)
  z is computed twice, with the symmetric se = hw / z_level and with the arms facing away from the
  other estimate (DEC-0027); a part fails if ``max(|z_sym|, |z_away|) > 3.4``. Both are printed. A
  TD pair between two devices triggers O4 (printed).

Scale classes and the 10x rule (B1 item 4, note M2)
---------------------------------------------------
``rel = |d| / s``, with s by class: (a) interval statistics (point estimate and endpoints),
``max(|lo|, |hi|)`` of the reference interval; (b) weight-scale leaves ``max(|ref|, 0.01)``; (c)
fractions and probabilities ``max(|ref|, 1/n)``; (d) correlations without an interval
``max(|ref|, 1/sqrt n)``; (e) p-values ``max(|ref|, 1e-3)``; (f) R2-type leaves
``max(|ref|, 0.01)``; (g) positive scales ``|ref|`` (an exact zero requires d = 0; every float leaf
that no rule names lands here and is counted as "default"). Excluded from the maximum, each under
its own rule: integer leaves, digests and strings, V1, V2, the fitted proxy coefficients (chain
heads, reported), ``median_iterations``, leaves in a block with a differing discrete count, timing
and provenance. The declared tolerance is ``10^ceil(log10(10 max rel))`` per class group, (a) and
(b) to (g); "bitwise on the same device type" if nothing differs. A declaration above 1e-4 is the
O3 finding (exit 1) for a T0 pair, the R1 against R2 calibration; on a T1 to T3 pair the same number is
printed as information (a pair that passes at half its tolerance would otherwise always fail). In T1 to T3 the class tolerance of (b) to (g) is ``--tol-other`` (default 1e-4, the O3
ceiling) until R1 and R2 declare one, never above 1e-4: a larger value is refused (exit 2), because A6
makes it an O3 finding that is not adopted silently. An exceedance is a listed finding.

Readings that the plan leaves open (strict reading applied; owner questions)
----------------------------------------------------------------------------
* The leaf-to-chain map is ``compare_pilot``'s rule table. **A leaf without a chain tag is treated as
  network chain (class rules, 1e-4), which is the looser choice** (the strict choice, 1e-12, would fail
  the many QoI leaves that the table leaves untagged: 111 differing leaves on the S3 pair). The count
  is printed, nothing is silent; this is an owner reading.
* A ``cov_digest`` difference alone is undetermined (see above); a ``None`` system never opens a scope.
* ``fraction_above_chi2`` and ``fraction_late_progress`` have no T2/T3 tolerance in A6: class (c)
  applies (T1: ``1e-8 |ref|``); the two-proportion band is printed beside them.
* The per-estimate LM check and the order-statistic bands need arrays of the per-state dump
  (WU-0003.7b), whose schema is not final. They are implemented as pure functions
  (``lm_estimate_check``, ``order_statistic_band``) and reported as NOT COMPUTED here; that is
  exit 2 unless ``--allow-not-computed``.
* A pair is "T0" only if host, device and threads are all equal; any other equal-digest pair is T1.

Exit codes: 0 pass; 1 a tolerance, verdict or TD failure (a ``DEF`` line for a verdict); 2 tier
undetermined, an unreadable input, a usage error, a TD part that cannot be computed, or a required
check that is NOT COMPUTED (unless ``--allow-not-computed``). ``--td-only`` computes the TD
statistic of the two files without tier selection or leaf comparison (for runs that predate the
selecting leaves).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
import struct
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from statistics import NormalDist

cp = sys.modules.get("compare_pilot")
if cp is None or not hasattr(cp, "TABLE"):
    _SPEC = importlib.util.spec_from_file_location("compare_pilot", Path(__file__).with_name("compare_pilot.py"))
    assert _SPEC is not None and _SPEC.loader is not None
    cp = importlib.util.module_from_spec(_SPEC)
    sys.modules["compare_pilot"] = cp
    _SPEC.loader.exec_module(cp)

LABEL = "DEVELOPMENT: comparison of two runs, not a hypothesis test"
REVIEW = ("needs owner review before freeze (tolerance and verdict-comparison code; "
          "CSQ2 use in WU-0016)")
EXIT_OK, EXIT_FAIL, EXIT_UNDETERMINED = 0, 1, 2

# --- tolerances quoted from the plan (A6 and B1); none is chosen here ------------------------------
TOL_CHAIN = 1e-12          # A6 T1: cp and oracle chains, relative (and fixture, dynamics, by N1)
TOL_V1 = 1e-12             # A6 T1: V1 |de| absolute
TOL_V2 = 1e-10             # A6 T1: V2 relative
TOL_QOI = 1e-4             # A6 T1: QoIs and interval endpoints, relative to max(|lo|, |hi|)
TOL_LM_SUMMARY = 1e-8      # WU-0005.4 M7(i): LM summaries relative (T1)
TOL_LM_ITERATIONS = 1.0    # WU-0005.4 M7: median_iterations within 1
TOL_O3 = 1e-4              # ROADMAP rule: a declared tolerance above this is a finding (O3)
HW_FRACTION = 0.1          # A6: discrete-count exception |d| <= 0.1 hw
TD_BOUND = 3.4             # A6, B1 item 5: |z| bound per primary part
PRIMARY_LEVEL = cp.PRIMARY_LEVEL
CHI2_4_999 = 18.47         # chi2_4 quantile 0.999 (WU-0005.4 D3): converged iff c / rho^2 <= this
ETA_ABS = 1e-12            # WU-0005.4 M2: eta = 1e-12 max(1, ||X||_inf)
LM_ESTIMATE_REL = 1e-8     # A6 T1: LM per estimate, relative
BAND_Z = 2.58              # WU-0005.4 M7(ii): 99% order-statistic band
FLOOR_WEIGHT = 0.01        # M2 (b), (f)
FLOOR_PVALUE = 1e-3        # M2 (e)

TD_TRIGGERS = ("state_mean_digest", "lambda_max", "interval", "start_state/main", "start_state/estimator",
               "main_digest", "estimator_digest")
WU_TRIGGERS = ("cov_digest", "whiten_digest", "unwhiten_digest")
WEIGHT_GROUPS = ("allocator_digest", "validation_weights")
RANK = {"T0": 0, "T1": 1, "T3": 2, "T2": 3, "TD": 4}
FACTS = (("device", "backend"), ("device", "kind"), ("device", "count"), ("platform",),
         ("cpu", "model"), ("env", "LPC_THREADS"))
LM_SUMMARY = frozenset({"fraction_above_chi2", "fraction_late_progress", "fraction_no_decrease",
                        "median_iterations", "median_residual", "p95_residual"})
EVIDENCE_DIGESTS = frozenset({"state_mean_digest", "cov_digest", "whiten_digest", "unwhiten_digest",
                              "main_digest", "estimator_digest", "weights_digest",
                              "allocator_digest"})
CHAIN_HEAD_INTEGERS = frozenset({"nfev", "status", "a5_leaf_digest"})
K_BLOCKS = ("fitted", "H3a", "H3c", "regime_curve")
CLIP_NAME = re.compile(r"error_clips.*|nu_cap_clips|.*_replacements")
INTERVAL_KEYS = frozenset({"ci", "interval", "ratio_ci", "mean_ci", "median_ci", "range_ci",
                           "ci_inverse_dim"})
KNOWN_POSITIVE = frozenset({
    "scores", "oracle_recovery", "estimators", "validation", "gain_bound", "fitted", "verification",
    "V7", "H1a", "H1b", "H1c", "H1d", "H2a", "H2b", "H2c", "H2d", "H2e", "H3a", "H3b", "H3c", "Q-N"})
INTERVAL_PARENTS = frozenset({"efficiency_ci_by_noise"})
POINT_INTERVALS = {
    "slope": ("ci",), "median_ratio": ("ci",), "median_slope": ("ci",), "delta_r2": ("ci",),
    "partial_corr": ("ci",), "mean_state_spearman": ("ci",), "mean_change": ("ci",),
    "in_distribution_excess": ("ci",), "median_change": ("ci",), "value": ("ci",),
    "A5_over_A4_mse": ("ci",), "importance": ("ci",), "spearman": ("interval",),
    "ratio": ("ratio_ci",), "fitted_inverse_dim": ("ci_inverse_dim",),
    "mean": ("mean_ci", "ci"), "median": ("median_ci",), "median_range": ("range_ci",)}
TD_PARTS = (
    ("H2a(i)", ("H2a", "median_range"), ("H2a", "range_ci")),
    ("H2a(ii) zero", ("H2a", "part_ii", "zero", "partial_corr"), ("H2a", "part_ii", "zero", "ci")),
    ("H2a(ii) interior", ("H2a", "part_ii", "interior", "partial_corr"),
     ("H2a", "part_ii", "interior", "ci")),
    ("H2b(i)", ("H2b", "noise", "mean_state_spearman"), ("H2b", "noise", "ci")),
    ("H2b(ii)", ("H2b", "library_change", "mean_change"), ("H2b", "library_change", "ci")),
    ("H3c", ("H3c", "A5_over_A4_mse"), ("H3c", "ci")),
)

Path_ = tuple[str, ...]


class ToolError(Exception):
    """An unreadable input or a usage error; ``main`` reports it and exits with code 2."""


# ----------------------------------------------------------------------------------- basic helpers
def is_float(value: object) -> bool:
    """True for a float (not a bool, not an int)."""
    return type(value) is float


def is_number(value: object) -> bool:
    """True for an int or a float (not a bool)."""
    return type(value) in (int, float)


def is_verdict_str(name: str) -> bool:
    """A string leaf that carries a verdict or a status: ``verdict``, ``verdict_2L``, ``part_i_verdict``,
    ``reading``, ``status`` (the clip-sensitivity strings)."""
    return name.startswith("verdict") or name.endswith("_verdict") or name in ("reading", "status")


def leaf_key(value: object) -> tuple:
    """Identity of a leaf: its type and, for a float, its 8 IEEE bytes (as ``tools/leafdiff.py``)."""
    if type(value) is float:
        return ("float", struct.pack("<d", value))
    return (type(value).__name__, value)


def flatten(tree: object) -> dict[Path_, object]:
    """Leaves of a results tree, without the top-level ``provenance`` and the ``seconds`` keys."""
    out = {}
    for path, value in cp.flatten(tree).items():
        if path[0] == "provenance" or "seconds" in path:
            continue
        out[path] = value
    return out


def excluded_counts(tree: object) -> dict[str, int]:
    """Number of leaves excluded from the comparison: provenance and timing."""
    flat = cp.flatten(tree)
    return {"provenance": sum(1 for p in flat if p[0] == "provenance"),
            "timing": sum(1 for p in flat if p[0] != "provenance" and "seconds" in p)}


def loc(path: Path_) -> tuple[str | None, str]:
    """``(system, block)`` of a leaf path (``None`` for a leaf that belongs to no one system)."""
    if path[0] == "systems" and len(path) >= 3:
        return path[1], path[2]
    if path[0] == "robustness" and len(path) >= 2:
        return path[1], "robustness"
    if path[0] == "handling" and len(path) >= 3 and path[1] == "by_system":
        return path[2], "handling"
    if path[0] == "handling" and len(path) >= 3 and path[1] == "robustness":
        return path[2], "robustness"
    return None, path[0]


def systems_of(flat: dict[Path_, object]) -> set[str]:
    """Systems that have a ``context`` block."""
    return {p[1] for p in flat if p[0] == "systems" and len(p) > 2 and p[2] == "context"}


def declared_tolerance(max_rel: float) -> float | None:
    """The ROADMAP 10x rule: ``10^ceil(log10(10 max_rel))`` (``None`` if ``max_rel`` is 0).

    The ceiling is taken with a slack of 1e-12 in ``log10`` so that ``max_rel = 1e-5`` gives 1e-4
    exactly (10 x 1e-5 is a power of ten) and is not pushed to 1e-3 by round-off.
    """
    if max_rel == 0:
        return None
    if not math.isfinite(max_rel):
        return math.inf
    return 10.0 ** math.ceil(math.log10(10.0 * max_rel) - 1e-12)


def fmt_num(value: object) -> str:
    """Compact text of a number."""
    if isinstance(value, float):
        return f"{value:.3g}"
    return str(value)


# ------------------------------------------------------------------------------------ tier selection
@dataclass
class Tier:
    """Outcome of the tier selection."""

    name: str                                   # T0, T1, T2, T3, TD or "undetermined"
    reasons: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    evidence: list[tuple[str, str, str]] = field(default_factory=list)   # (system, group, status)
    only_trajectory_digest: bool = False        # TD selected only by main_digest / estimator_digest
    cpu_device: bool = True
    devices_differ: bool = False


def group_leaves(flat: dict[Path_, object], system: str | None, group: str) -> dict[Path_, object]:
    """The leaves of one selecting group of one system (``None``: the top-level estimators).

    Groups: a ``context`` leaf name, ``start_state/main`` or ``start_state/estimator``,
    ``allocator_digest``, ``validation_weights`` (the weight digests of ``validation/estimators``).
    """
    out = {}
    for path, value in flat.items():
        if system is None:
            if path[0] == "estimators" and path[-1] == "weights_digest":
                out[path] = value
            continue
        if path[:2] != ("systems", system):
            continue
        rest = path[2:]
        if group == "validation_weights":
            ok = len(rest) > 2 and rest[:2] == ("validation", "estimators") and rest[-1] == "weights_digest"
        elif group == "allocator_digest":
            ok = rest == ("fitted", "allocator_digest")
        elif group.startswith("start_state/"):
            ok = len(rest) > 3 and rest[:3] == ("context", "start_state", group.split("/")[1])
        else:
            ok = len(rest) > 1 and rest[:2] == ("context", group)
        if ok:
            out[path] = value
    return out


def group_status(ref: dict[Path_, object], new: dict[Path_, object]) -> str:
    """``missing`` (empty on a side, or different leaf sets), ``equal`` or ``differs``."""
    if not ref or not new or set(ref) != set(new):
        return "missing"
    return "equal" if all(leaf_key(ref[p]) == leaf_key(new[p]) for p in ref) else "differs"


def provenance_facts(tree: object) -> dict[str, object]:
    """The host and device facts of a ``provenance`` block (``None`` where a key is absent)."""
    block = tree.get("provenance") if isinstance(tree, dict) else None
    facts: dict[str, object] = {}
    for keys in FACTS:
        node: object = block
        for key in keys:
            node = node.get(key) if isinstance(node, dict) else None
        facts[".".join(keys)] = node
    return facts


def select_tier(ref_tree: dict, new_tree: dict) -> Tier:
    """Select the reproducibility tier of a pair from the digests and the provenance (A6, B1 item 1).

    Returns
    -------
    Tier
        ``name`` is ``undetermined`` when a selecting leaf is missing on either run (or the leaf
        sets differ), when no system is common to both, or when the host or device facts needed to
        tell T0 from T1 are not recorded; ``missing`` lists what is absent.
    """
    ref, new = flatten(ref_tree), flatten(new_tree)
    common = sorted(systems_of(ref) & systems_of(new))
    tier = Tier("undetermined")
    if not common:
        tier.missing.append("no system with a context block on both runs")
        return tier
    td_hits, wu_hits, weight_hits = [], [], []
    for system in common:
        for group in (*TD_TRIGGERS, *WU_TRIGGERS, *WEIGHT_GROUPS):
            status = group_status(group_leaves(ref, system, group), group_leaves(new, system, group))
            tier.evidence.append((system, group, status))
            label = f"{system}/{group}"
            if status == "missing":
                tier.missing.append(label)
            elif status == "differs":
                (td_hits if group in TD_TRIGGERS else wu_hits if group in WU_TRIGGERS
                 else weight_hits).append(label)
    status = group_status(group_leaves(ref, None, "weights_digest"), group_leaves(new, None, "weights_digest"))
    tier.evidence.append(("(top level)", "estimators/*/weights_digest", status))
    if status == "differs":
        weight_hits.append("estimators/*/weights_digest")
    elif status == "missing":
        tier.missing.append("estimators/*/weights_digest")
    facts_ref, facts_new = provenance_facts(ref_tree), provenance_facts(new_tree)
    tier.cpu_device = facts_new.get("device.backend") == "cpu" and facts_ref.get("device.backend") == "cpu"
    if tier.missing:
        return tier
    if td_hits:
        tier.name = "TD"
        tier.reasons = [f"{h} differs" for h in td_hits]
        tier.only_trajectory_digest = all(h.rsplit("/", 1)[1] in ("main_digest", "estimator_digest")
                                          for h in td_hits)
    elif any(not h.endswith("/cov_digest") for h in wu_hits):
        tier.name, tier.reasons = "T2", [f"{h} differs" for h in wu_hits]
    elif wu_hits:
        # R8: cov_digest alone (W and U equal) matches no tier of A6; T2 would apply the looser LM bands,
        # so the pair is left undetermined (owner reading).
        tier.missing += [f"{h}: differs with whiten_digest and unwhiten_digest equal (matches no A6 tier)"
                         for h in wu_hits]
        return tier
    elif weight_hits:
        tier.name, tier.reasons = "T3", [f"{h} differs" for h in weight_hits]
    else:
        absent = [k for k in facts_ref if facts_ref[k] is None or facts_new[k] is None]
        if absent:
            tier.name = "undetermined"
            tier.missing += [f"provenance.{k}" for k in absent]
            return tier
        differ = [k for k in facts_ref if facts_ref[k] != facts_new[k]]
        tier.name = "T1" if differ else "T0"
        tier.reasons = [f"{k}: {facts_ref[k]!r} against {facts_new[k]!r}" for k in differ]
        tier.cpu_device = facts_ref["device.backend"] == "cpu" and facts_new["device.backend"] == "cpu"
    tier.devices_differ = any(facts_ref[k] != facts_new[k] for k in facts_ref
                              if facts_ref[k] is not None and facts_new[k] is not None
                              and k.startswith("device."))
    return tier


# ------------------------------------------------------------------------ interval pairing and class
def interval_of(flat: dict[Path_, object], path: Path_) -> tuple[float, float] | None:
    """The reference interval ``(lo, hi)`` that a leaf belongs to, as endpoint or as its point estimate."""
    if path[-1] in ("[0]", "[1]") and len(path) >= 2 and (
            path[-2] in INTERVAL_KEYS or (len(path) >= 3 and path[-3] in INTERVAL_PARENTS)):
        lo, hi = flat.get((*path[:-1], "[0]")), flat.get((*path[:-1], "[1]"))
        return (lo, hi) if is_float(lo) and is_float(hi) else None
    for key in POINT_INTERVALS.get(path[-1], ()):
        lo, hi = flat.get((*path[:-1], key, "[0]")), flat.get((*path[:-1], key, "[1]"))
        if is_float(lo) and is_float(hi):
            return lo, hi
    return None


def find_n(flat: dict[Path_, object], path: Path_) -> int | None:
    """The state (or estimate) count of a leaf: the nearest ``n_states``-type key up the path, else ``config/n_test``."""
    for depth in range(len(path) - 1, 0, -1):
        for key in ("n_states", "n_estimates", "n_eligible_states"):
            value = flat.get((*path[:depth], key))
            if type(value) is int and value > 0:
                return value
    value = flat.get(("config", "n_test"))
    return value if type(value) is int and value > 0 else None


def classify_float(flat: dict[Path_, object], path: Path_) -> tuple[str, float | None, bool]:
    """Scale class of a float leaf of the reference.

    Returns
    -------
    tuple
        ``(class letter, scale s or None if s depends on |ref|, defaulted)``. For classes whose
        scale is ``max(|ref|, floor)`` the returned ``s`` is the floor, to be combined with ``|ref|``
        by ``scale_of``; for (a) it is the interval's ``max(|lo|, |hi|)``.
    """
    interval = interval_of(flat, path)
    if interval is not None:
        return "a", max(abs(interval[0]), abs(interval[1])), False
    segs = set(path)
    last = path[-1]
    if segs & {"logrank_p_raw", "logrank_p_holm"}:
        return "e", FLOOR_PVALUE, False
    if last.startswith("fraction") or "km_curves" in segs:
        n = find_n(flat, path)
        return ("c", 1.0 / n, False) if n else ("g", None, True)
    if any(("spearman" in s or "corr" in s) for s in path if not s.startswith("[")):
        n = find_n(flat, path)
        return ("d", 1.0 / math.sqrt(n), False) if n else ("g", None, True)
    if last in ("r2_three", "r2_four", "delta_r2", "noise_sens_r2_from_three"):
        return "f", FLOOR_WEIGHT, False
    if segs & {"weight_profile", "median_w_by_noise", "regime_weights_href", "agreement_href"}:
        return "b", FLOOR_WEIGHT, False
    return "g", None, not segs & KNOWN_POSITIVE


def scale_of(cls: str, ref: float, floor_or_s: float | None) -> float:
    """The scale ``s`` of a leaf: interval scale (a), ``max(|ref|, floor)`` (b to f), ``|ref|`` (g)."""
    if cls == "a":
        return floor_or_s if floor_or_s is not None else 0.0
    if cls == "g" or floor_or_s is None:
        return abs(ref)
    return max(abs(ref), floor_or_s)


def licensing_kind(path: Path_, kind: str) -> str | None:
    """Which entry of A6's exception list a differing leaf is, or ``None`` (then a differing integer is exact).

    A6 (unchanged by B1 item 3): K (``chosen_K``, ``realized_K``), ``best_single`` (also
    ``best_single_2L``), ``n_states`` and the state denominators, and clip, nu-cap and replacement counts
    (``error_clips*``, ``nu_cap_clips``, ``*_replacements``). Nothing else is a licensing count: not
    the other ``handling`` counters, the LM ``n_estimates``, non-finite, warning, fallback or
    failed-resample counts.
    """
    name = path[-1]
    if kind == "str":
        return "best_single" if name.startswith("best_single") else None
    if kind != "int":
        return None
    if name in ("chosen_K", "realized_K") or "realized_K" in path:
        return "K"
    if name == "n_states":
        return "states"
    if "denominators" in path and name == "states":
        return "denominator"
    if any(CLIP_NAME.fullmatch(seg) for seg in path):
        return "clip"
    return None


def count_scope(path: Path_, kind: str) -> tuple[str, str] | None:
    """The scope ``(system, block)`` that a differing licensing count opens, or ``None``.

    ``block`` is the block the count lives in; ``"*"`` is the whole system (a per-system clip, nu-cap or
    replacement count under ``systems/<s>/handling``), ``"K"`` the blocks of ``K_BLOCKS``. A leaf of the
    top-level ``handling`` block (``totals``, ``by_system``, ``robustness``), a per-system ``totals``
    mirror, and a state denominator open no scope: the per-system source of a sum carries it, and a
    ``None`` system never matches every system (OF-1, per-system scope only).
    """
    lk = licensing_kind(path, kind)
    if lk is None or path[0] == "handling" or lk == "denominator":
        return None
    system, block = loc(path)
    if system is None:
        return None
    if block == "handling":
        if len(path) > 3 and path[3] == "totals":
            return None
        return (system, "*") if lk == "clip" else None
    if lk == "clip":
        return None
    return (system, "K") if lk == "K" else (system, block)


def in_scope(scopes: list[tuple[str, str]], path: Path_, star: bool = True) -> bool:
    """Whether a path is in the scope of a differing licensing count of its own system.

    ``star=False`` leaves out the whole-system scope of clip counts (used for one-sided leaves: only the
    shape that follows a count of its own block or K is excused).
    """
    system, block = loc(path)
    if system is None:
        return False
    for s_sys, s_block in scopes:
        if s_sys != system:
            continue
        if (s_block == "*" and star) or s_block == block or (s_block == "K" and block in K_BLOCKS):
            return True
    return False


def follows_k(scopes: list[tuple[str, str]], path: Path_) -> bool:
    """Whether a path lies in a K-shaped block of a system whose K differs."""
    system, block = loc(path)
    return system is not None and block in K_BLOCKS and (system, "K") in scopes


# ------------------------------------------------------------------------------------- LM functions
def order_statistic_band(n: int, q: float) -> tuple[int, int]:
    """Ranks ``(lo, hi)`` (1-based, clipped to ``1..n``) of the 99% distribution-free band for a quantile.

    WU-0005.4 M7(ii): the run's quantile q must lie between the reference's order statistics at
    ranks ``n q -/+ 2.58 sqrt(n q (1 - q))`` (assuming independent estimates, so it is conservative
    under the positive correlation of the draws of one state). Ranks are rounded outward
    (floor for the lower, ceil for the upper).
    """
    if n < 1 or not 0.0 < q < 1.0:
        raise ValueError("order_statistic_band needs n >= 1 and 0 < q < 1")
    half = BAND_Z * math.sqrt(n * q * (1.0 - q))
    lo = max(1, math.floor(n * q - half))
    hi = min(n, math.ceil(n * q + half))
    return lo, hi


def two_proportion_bound(p_ref: float, p_new: float, n: int) -> float:
    """``3 sqrt(2 pbar (1 - pbar) / n) + 1/n`` with ``pbar`` the mean of the two fractions (WU-0005.4 M7(ii))."""
    pbar = 0.5 * (p_ref + p_new)
    return 3.0 * math.sqrt(2.0 * pbar * (1.0 - pbar) / n) + 1.0 / n


def lm_estimate_check(c_ref: list[float], c_new: list[float], late_ref: list[int],
                      late_new: list[int], rho: float, x_inf: float) -> dict[str, object]:
    """The per-estimate LM check of B1 item 2 on the cost ``c`` of the core test split.

    For an estimate with ``lm_late_progress`` = 0 in both runs, ``|dc| <= 1e-8 |c_ref|``; if also
    ``c / rho^2 <= 18.47`` in both runs, ``|dc| <= min(1e-8 |c_ref|, eta (2 sqrt(c_ref) + eta))`` with
    ``eta = 1e-12 max(1, x_inf)`` (WU-0005.4 M2). Late-flagged estimates (in either run) are counted
    and listed with no tolerance.

    Returns
    -------
    dict
        ``n``, ``n_late`` (listed, no tolerance), ``n_checked``, ``n_tight`` (estimates under the
        min bound), ``violations`` (indices), ``max_ratio`` (largest ``|dc| / tolerance``).
    """
    if not (len(c_ref) == len(c_new) == len(late_ref) == len(late_new)):
        raise ValueError("lm_estimate_check: arrays of different length")
    if not (rho > 0 and x_inf >= 0):
        raise ValueError("lm_estimate_check needs rho > 0 and x_inf >= 0")
    eta = ETA_ABS * max(1.0, x_inf)
    out = {"n": len(c_ref), "n_late": 0, "n_checked": 0, "n_tight": 0, "violations": [],
           "late": [], "max_ratio": 0.0}
    for i, (a, b, la, lb) in enumerate(zip(c_ref, c_new, late_ref, late_new)):
        if la or lb:
            out["n_late"] += 1
            out["late"].append(i)
            continue
        tol = LM_ESTIMATE_REL * abs(a)
        if a / rho ** 2 <= CHI2_4_999 and b / rho ** 2 <= CHI2_4_999:
            tol = min(tol, eta * (2.0 * math.sqrt(abs(a)) + eta))
            out["n_tight"] += 1
        out["n_checked"] += 1
        delta = abs(a - b)
        ratio = math.inf if tol == 0 and delta > 0 else (0.0 if delta == 0 else delta / tol)
        out["max_ratio"] = max(out["max_ratio"], ratio)
        if delta > tol:
            out["violations"].append(i)
    return out


# ---------------------------------------------------------------------------- per-leaf comparison
@dataclass
class Row:
    """One differing leaf (or one-sided leaf) and what was decided about it."""

    path: Path_
    kind: str                       # float, int, str, bool, none, type, only_ref, only_new
    ref: object
    new: object
    cls: str = ""                   # a..g, or a rule family name
    rel: float | None = None        # |d| / s of the scale class (a to g): what the 10x rule maximizes
    metric: float | None = None     # the number compared with ``tol`` (``rel`` unless the rule says otherwise)
    tol: float | None = None
    rule: str = ""
    outcome: str = ""               # pass, FAIL, FINDING, DEF, listed, reported, measured, NOT COMPUTED
    note: str = ""
    for_10x: bool = False
    defaulted: bool = False


def kind_of(a: object, b: object) -> str:
    """The comparison kind of a pair of leaf values (``type`` when their types differ)."""
    if type(a) is not type(b):
        return "type"
    return {bool: "bool", int: "int", float: "float", str: "str", type(None): "none"}.get(type(a), "other")


def chain_of(path: Path_) -> str:
    """The chain tag of ``compare_pilot``'s rule table for a leaf (``''`` if untagged or unmatched)."""
    try:
        return cp.TABLE.classify(path).chain
    except cp.ToolError:
        return ""


def lm_name(path: Path_) -> str | None:
    """The LM summary name of a leaf under ``handling/**/lm`` (else ``None``)."""
    return path[-1] if "lm" in path and path[-1] in LM_SUMMARY and "handling" in (path[0], *path[2:3]) else None


@dataclass
class Comparison:
    """Everything the report prints."""

    tier: Tier
    n_ref: int
    n_new: int
    n_common: int
    n_equal: int
    rows: list[Row]
    one_sided: list[Row]
    excluded: dict[str, dict[str, int]]
    scopes: list[tuple[str | None, str]]
    declared: dict[str, dict]
    td: dict | None
    not_computed: list[str]
    untagged: int
    exit_code: int
    reasons: list[str]


def compare_leaves(ref_tree: dict, new_tree: dict, tier: Tier, tol_other: float = TOL_O3) -> tuple:
    """Decide every differing and one-sided leaf under ``tier``.

    Returns
    -------
    tuple
        ``(rows, one_sided, n_equal, scopes, untagged)``.
    """
    ref, new = flatten(ref_tree), flatten(new_tree)
    rows: list[Row] = []
    n_equal = 0
    for path in sorted(set(ref) & set(new)):
        a, b = ref[path], new[path]
        if leaf_key(a) == leaf_key(b):
            n_equal += 1
            continue
        rows.append(Row(path, kind_of(a, b), a, b))
    one_sided = [Row(p, "only_ref", ref[p], None) for p in sorted(set(ref) - set(new))]
    one_sided += [Row(p, "only_new", None, new[p]) for p in sorted(set(new) - set(ref))]
    scopes: list[tuple[str | None, str]] = []
    for row in rows:
        scope = count_scope(row.path, row.kind) if row.kind in ("int", "str") else None
        if scope is not None:
            scopes.append(scope)
    untagged = 0
    for row in rows:
        untagged += decide(row, ref, tier, scopes, tol_other)
    for row in one_sided:
        decide_one_sided(row, scopes, tier)
    return rows, one_sided, n_equal, scopes, untagged


def decide_one_sided(row: Row, scopes: list, tier: Tier) -> None:
    """A leaf on one side only: a failure, unless the length of a list follows a differing count."""
    row.cls, row.rule = "structure", "present on both runs"
    if tier.name == "TD":
        row.outcome, row.note = "reported", "TD: no per-leaf rule"
    elif tier.name != "T0" and in_scope(scopes, row.path, star=False):
        row.outcome, row.note = "listed", "shape follows a differing discrete count of its block"
    else:
        row.outcome = "FAIL"


def decide(row: Row, ref: dict, tier: Tier, scopes: list, tol_other: float) -> int:
    """Fill ``row.cls``, ``rel``, ``tol``, ``rule``, ``outcome`` for one differing leaf.

    Returns 1 if the leaf has no chain tag in ``compare_pilot``'s rule table (counted, not hidden).
    """
    path, a, b, kind = row.path, row.ref, row.new, row.kind
    name = path[-1]
    verdictlike = kind == "bool" or (kind == "str" and is_verdict_str(name)) or path[0] == "verdicts"
    if kind == "float":
        row.cls, floor, row.defaulted = classify_float(ref, path)
        scale = scale_of(row.cls, a, floor)
        delta = abs(a - b) if math.isfinite(a) and math.isfinite(b) else math.inf
        row.rel = (0.0 if delta == 0 else math.inf) if scale == 0 else delta / scale
        row.metric = row.rel
    if path[0] == "config":
        row.cls, row.rule = "config", "config identical"
        if tier.name == "TD" and name in ("seed", "seed_id"):
            row.outcome, row.note = "listed", "TD pairs are different realizations by design"
        else:
            row.outcome, row.note = "FAIL", "the two runs are not the same experiment"
        return 0
    if tier.name == "TD":
        row.rule, row.outcome = "TD: no per-leaf tolerance", "reported"
        row.note = "verdict-type leaf" if verdictlike else ""
        return 0
    if tier.name == "T0":
        if kind == "float" and not tier.cpu_device:
            row.rule, row.outcome, row.note = "T0 non-CPU: measured (10x rule)", "measured", "same device type"
            row.for_10x = True
            return 0
        row.cls = row.cls or ("verdict" if verdictlike else kind)
        row.rule = "T0: bitwise"
        row.outcome = "DEF" if verdictlike else "FAIL"
        return 0
    # T1, T2, T3 ----------------------------------------------------------------------------------------
    if kind in ("bool", "str", "none", "type", "other"):
        if kind == "str" and name in EVIDENCE_DIGESTS:
            row.cls, row.rule, row.outcome = "digest", "tier evidence", "listed"
            row.note = "selects the tier; printed in the evidence table"
        elif kind == "str" and name == "a5_leaf_digest":
            row.cls, row.rule, row.outcome = "chain head", "listed beside H2c, H2d, H3c, oracle_recovery", "listed"
            row.note = "OF-1: no licence for 0.1 hw"
        elif verdictlike:
            row.cls, row.rule = "verdict", "every verdict identical"
            row.outcome, row.note = "DEF", "a verdict or flag differs"
        elif licensing_kind(path, kind) is not None:
            row.cls, row.rule, row.outcome = "discrete", "A6 exception list", "listed"
        else:
            row.cls, row.rule, row.outcome = "categorical", "exact", "FAIL"
            row.note = "type changed" if kind == "type" else "text differs"
        return 0
    if kind == "int":
        if name in CHAIN_HEAD_INTEGERS:
            row.cls, row.rule, row.outcome = "chain head", "listed beside H2c, H2d, H3c, oracle_recovery", "listed"
            row.note = "OF-1: no licence for 0.1 hw"
        elif licensing_kind(path, "int") is not None:
            row.cls, row.rule, row.outcome = "discrete", "A6 exception list", "listed"
            if count_scope(path, "int") is None:
                row.note = "opens no scope (mirror, denominator or top-level sum)"
        elif follows_k(scopes, path):
            row.cls, row.rule, row.outcome = "discrete", "follows a differing K", "listed"
        else:
            row.cls, row.rule, row.outcome = "integer", "exact", "FAIL"
        return 0
    # float leaves ------------------------------------------------------------------------------------------
    interval = interval_of(ref, path)
    chain = chain_of(path)
    untagged = 0 if chain else 1
    lm = lm_name(path)
    row.for_10x = True
    if lm == "median_iterations":
        row.cls, row.rule, row.tol, row.for_10x = "lm", "median_iterations within 1", TOL_LM_ITERATIONS, False
        row.metric = abs(a - b)
        row.outcome = "pass" if row.metric <= row.tol else "FAIL"
    elif in_scope(scopes, path) and interval is not None:
        hw = 0.5 * (interval[1] - interval[0])
        row.rule, row.tol, row.for_10x = "discrete scope: 0.1 hw", HW_FRACTION * hw, False
        row.metric = abs(a - b)
        row.outcome = "pass" if row.metric <= row.tol else "FAIL"
    elif name in ("delay_jacobian_rel_err", "gain_rel_err") and "validation" in path:
        row.cls, row.rule, row.tol, row.for_10x = "V1", "V1 absolute", TOL_V1, False
        row.metric = abs(a - b)
        row.outcome = "pass" if row.metric <= row.tol else "FAIL"
    elif name.startswith("crlb_ratio_") and "validation" in path:
        row.cls, row.rule, row.tol, row.for_10x = "V2", "V2 relative", TOL_V2, False
        row.metric = abs(a - b) / abs(a) if a else (0.0 if a == b else math.inf)
        row.outcome = "pass" if row.metric <= row.tol else "FAIL"
    elif name in ("floor", "slope") and "fitted" in path and path[-2] in ("analog_proxy", "estimation_proxy"):
        row.cls, row.rule, row.outcome, row.for_10x = "head", "chain head: reported", "reported", False
        row.note = "fitted proxy coefficient (tolerance-stopped fit)"
    elif lm is not None:
        row.cls = "lm"
        lmrow(row, ref, tier, tol_other)
    elif chain in cp.NETWORK_INDEPENDENT:
        row.rule, row.tol = f"{chain} chain relative", TOL_CHAIN
        row.metric = abs(a - b) / abs(a) if a and math.isfinite(a) and math.isfinite(b) else (
            0.0 if a == b else math.inf)
        row.outcome = "pass" if row.metric <= row.tol else "FAIL"
    elif row.cls == "a":
        row.rule, row.tol = "QoI / interval endpoint", TOL_QOI
        row.outcome = "pass" if row.metric <= row.tol else "FAIL"
    else:
        row.rule, row.tol = "class (b) to (g)", tol_other
        row.outcome = "pass" if row.metric <= row.tol else "FINDING"
    return untagged


def lm_rules(tier: Tier, path: Path_) -> str:
    """``T1`` or ``T2``: which LM rules apply to an LM summary leaf under the tier.

    A6: T2 applies the LM bands (T2 rules) to every LM summary. T3 says "network chain as T2; other
    chains as T1": the ``eval`` kind (the estimates of the evaluation draws, which run the trained
    network) gets the T2 rules; the ``oracle`` and ``check`` kinds and the pooled summary keep the T1
    rules (strict default until the mathematician gives the kind-to-chain map).
    """
    if tier.name == "T2":
        return "T2"
    if tier.name == "T3":
        kind = path[path.index("by_kind") + 1] if "by_kind" in path[:-1] else "pooled"
        return "T2" if kind == "eval" else "T1"
    return "T1"


def lmrow(row: Row, ref: dict, tier: Tier, tol_other: float) -> None:
    """The rule of an LM summary leaf (T1 rules: WU-0005.4 M7(i); T2 rules: M7(ii); see ``lm_rules``)."""
    a, b, path = row.ref, row.new, row.path
    rules = lm_rules(tier, path)
    name = path[-1]
    n = ref.get((*path[:-1], "n_estimates"))
    n = n if type(n) is int and n > 0 else None
    row.metric = abs(a - b) / abs(a) if a else (0.0 if a == b else math.inf)
    if name == "fraction_no_decrease":
        if rules == "T1":
            row.rule, row.tol, row.outcome = "T1: exact", 0.0, "FAIL"
            row.metric = abs(a - b)
        elif n is not None:
            row.rule, row.tol, row.metric = "T2 rules: 3 sqrt(2 pbar (1 - pbar) / n) + 1/n", two_proportion_bound(a, b, n), abs(a - b)
            row.outcome = "pass" if row.metric <= row.tol else "FAIL"
        else:
            row.rule, row.outcome, row.note = "needs n_estimates", "NOT COMPUTED", "n_estimates absent"
        return
    if rules == "T1":
        row.rule, row.tol = "T1: LM summary relative 1e-8 (M7(i))", TOL_LM_SUMMARY
        row.outcome = "pass" if row.metric <= row.tol else "FAIL"
    elif name in ("median_residual", "p95_residual"):
        row.rule, row.outcome, row.for_10x = "T2 rules: order-statistic band", "NOT COMPUTED", False
        row.note = "needs the per-estimate dump (WU-0003.7b); relative difference shown"
    else:
        row.cls = "c"
        scale = max(abs(a), 1.0 / n) if n else abs(a)
        row.metric = abs(a - b) / scale if scale else (0.0 if a == b else math.inf)
        row.rel = row.metric
        row.rule, row.tol = "class (c); no T2 tolerance in A6", tol_other
        if n:
            row.note = f"two-proportion band {two_proportion_bound(a, b, n):.3g} (information)"
        row.outcome = "pass" if row.metric <= row.tol else "FINDING"


# ---------------------------------------------------------------------------------------- TD statistic
def z_level() -> float:
    """The two-sided normal quantile of the primary level ``1 - 0.05/3``."""
    return NormalDist().inv_cdf(1.0 - (1.0 - PRIMARY_LEVEL) / 2.0)


def td_part(est0: float, ci0: list, est1: float, ci1: list) -> dict:
    """The TD statistic of one primary part of two runs (A6 TD, B1 item 5, DEC-0027).

    ``z_sym = |d| / sqrt(se0^2 + se1^2)`` with ``se = hw / z_level``; ``z_away`` uses the arms that
    face away from the other estimate (run 1 above run 0: run 0's lower arm and run 1's upper arm).
    A division of zero by zero is 0; a nonzero difference over a zero standard error is infinite.

    Returns
    -------
    dict
        ``d``, ``z_sym``, ``z_away``, ``hw0``, ``hw1``; or ``{"error": text}`` if an input is
        missing or not finite, or an arm is negative (the estimate outside its interval).
    """
    if not isinstance(ci0, list) or not isinstance(ci1, list) or len(ci0) != 2 or len(ci1) != 2:
        return {"error": "interval missing"}
    if not all(is_number(v) and math.isfinite(v) for v in (est0, est1, *ci0, *ci1)):
        return {"error": "estimate or interval missing or not finite"}
    zl = z_level()
    hw0, hw1 = 0.5 * (ci0[1] - ci0[0]), 0.5 * (ci1[1] - ci1[0])
    d = est1 - est0
    if d > 0:
        arm0, arm1 = est0 - ci0[0], ci1[1] - est1
    else:
        arm0, arm1 = ci0[1] - est0, est1 - ci1[0]
    if min(hw0, hw1, arm0, arm1) < 0:
        return {"error": "negative half-width or arm (estimate outside its interval)"}

    def ratio(se0: float, se1: float) -> float:
        den = math.hypot(se0, se1)
        return (0.0 if d == 0 else math.inf) if den == 0 else abs(d) / den

    return {"d": d, "z_sym": ratio(hw0 / zl, hw1 / zl), "z_away": ratio(arm0 / zl, arm1 / zl),
            "hw0": hw0, "hw1": hw1}


def lookup(tree: object, keys: tuple[str, ...]) -> object:
    """``tree[k1][k2]...`` or ``None`` if a key is absent."""
    for key in keys:
        if not isinstance(tree, dict) or key not in tree:
            return None
        tree = tree[key]
    return tree


def td_statistic(ref_tree: dict, new_tree: dict) -> dict:
    """The TD table over the primary parts of every system of either run (6 parts per system, 18 over three).

    A system missing on one run gives 6 parts that cannot be computed (never dropped silently: B1 item 5
    fixes the number of parts).

    Returns
    -------
    dict
        ``parts`` (rows with ``system``, ``part`` and ``td_part``'s keys, or ``error``), ``expected``
        (6 x systems), ``sum_sym``, ``sum_away``, ``max_z``, ``k`` (parts computed), ``n_error``,
        ``n_fail``.
    """
    ref_systems, new_systems = ref_tree.get("systems", {}), new_tree.get("systems", {})
    systems = sorted(set(ref_systems) | set(new_systems))
    parts, errors = [], 0
    for system in systems:
        r, n = ref_systems.get(system), new_systems.get(system)
        for name, point, interval in TD_PARTS:
            if r is None or n is None:
                res = {"error": f"system missing on the {'reference' if r is None else 'new'} run"}
            else:
                res = td_part(lookup(r, point), lookup(r, interval), lookup(n, point), lookup(n, interval))
            res.update(system=system, part=name)
            errors += "error" in res
            res["fail"] = "error" not in res and max(res["z_sym"], res["z_away"]) > TD_BOUND
            parts.append(res)
    good = [p for p in parts if "error" not in p]
    return {"parts": parts, "k": len(good), "n_error": errors, "n_fail": sum(p["fail"] for p in good),
            "expected": len(TD_PARTS) * len(systems),
            "sum_sym": sum(p["z_sym"] ** 2 for p in good), "sum_away": sum(p["z_away"] ** 2 for p in good),
            "max_z": max((max(p["z_sym"], p["z_away"]) for p in good), default=0.0),
            "max_sym": max((p["z_sym"] for p in good), default=0.0),
            "max_away": max((p["z_away"] for p in good), default=0.0),
            "no_systems": not systems}


# --------------------------------------------------------------------------------------------- driver
def declarations(rows: list[Row]) -> dict[str, dict]:
    """The 10x rule per class group, (a) and (b) to (g), over the eligible float leaves."""
    out = {}
    for label, classes in (("(a)", ("a",)), ("(b) to (g)", ("b", "c", "d", "e", "f", "g"))):
        pool = [r for r in rows if r.for_10x and r.kind == "float" and r.cls in classes and r.rel is not None]
        worst = max(pool, key=lambda r: r.rel, default=None)
        max_rel = worst.rel if worst else 0.0
        declared = declared_tolerance(max_rel)
        out[label] = {"n": len(pool), "max_rel": max_rel, "argmax": "/".join(worst.path) if worst else "",
                      "declared": declared, "o3": declared is not None and declared > TOL_O3,
                      "defaulted": sum(r.defaulted for r in pool)}
    return out


def compare_trees(ref_tree: dict, new_tree: dict, tol_other: float = TOL_O3,
                  allow_not_computed: bool = False) -> Comparison:
    """Compare two parsed results trees: tier, leaf decisions, 10x declarations, TD, exit code."""
    if not 0 < tol_other <= TOL_O3:
        raise ToolError(f"--tol-other {tol_other:g} is outside (0, {TOL_O3:g}]: a class tolerance above the O3 "
                        "ceiling is an O3 finding that A6 does not let the tool adopt (stricter reading)")
    tier = select_tier(ref_tree, new_tree)
    flat_ref, flat_new = flatten(ref_tree), flatten(new_tree)
    excluded = {"ref": excluded_counts(ref_tree), "new": excluded_counts(new_tree)}
    reasons: list[str] = []
    if tier.name == "undetermined":
        return Comparison(tier, len(flat_ref), len(flat_new), 0, 0, [], [], excluded, [], {}, None, [],
                          0, EXIT_UNDETERMINED,
                          ["tier undetermined: " + "; ".join(tier.missing) + " (no T0 to T3 tolerance applied)"])
    rows, one_sided, n_equal, scopes, untagged = compare_leaves(ref_tree, new_tree, tier, tol_other)
    td = td_statistic(ref_tree, new_tree) if tier.name == "TD" else None
    not_computed: list[str] = []
    if tier.name in ("T1", "T2", "T3") and any(lm_name(p) for p in flat_ref):
        if tier.name in ("T1", "T3"):
            not_computed.append("LM per-estimate check (B1 item 2)"
                                + (" for the oracle and check kinds and the pooled summary" if tier.name == "T3" else "")
                                + ": needs the per-estimate arrays of the WU-0003.7b dump")
        if tier.name in ("T2", "T3"):
            not_computed.append("LM order-statistic bands for median_residual and p95_residual (M7(ii))"
                                + (" of the eval kind" if tier.name == "T3" else "")
                                + ": needs the per-estimate arrays of the WU-0003.7b dump")
    if any(r.outcome == "NOT COMPUTED" and r.note == "n_estimates absent" for r in rows):
        not_computed.append("fraction_no_decrease needs n_estimates, absent from a cell")
    declared = declarations(rows) if tier.name != "TD" else {}
    fails = [r for r in (*rows, *one_sided) if r.outcome in ("FAIL", "FINDING", "DEF")]
    code = EXIT_OK
    if fails:
        code = EXIT_FAIL
        reasons.append(f"{len(fails)} leaf failures or findings")
    if tier.name == "T0" and any(d["o3"] for d in declared.values()):
        code = EXIT_FAIL
        reasons.append("O3: a declared tolerance exceeds 1e-4")
    if td is not None:
        if td["n_fail"]:
            code = EXIT_FAIL
            reasons.append(f"TD: {td['n_fail']} of {td['k']} parts exceed {TD_BOUND}")
        if td["n_error"] or td["no_systems"]:
            code = code if code == EXIT_FAIL else EXIT_UNDETERMINED
            reasons.append(f"TD: {td['n_error']} parts cannot be computed")
    if code == EXIT_OK and not_computed and not allow_not_computed:
        code = EXIT_UNDETERMINED
        reasons.append(f"{len(not_computed)} required checks NOT COMPUTED")
    return Comparison(tier, len(flat_ref), len(flat_new), len(set(flat_ref) & set(flat_new)), n_equal, rows,
                      one_sided, excluded, scopes, declared, td, not_computed, untagged, code, reasons)


def load(path: Path) -> dict:
    """Read a ``results.json`` from a file or a run directory (read-only)."""
    target = path / "results.json" if path.is_dir() else path
    try:
        tree = json.loads(target.read_text())
    except (OSError, ValueError) as exc:
        raise ToolError(f"cannot read {target}: {exc}") from exc
    if not isinstance(tree, dict) or "systems" not in tree:
        raise ToolError(f"{target} is not a results.json (no 'systems' block)")
    return tree


# ---------------------------------------------------------------------------------------------- report
def show_path(path: Path_) -> str:
    """``/``-joined text of a path."""
    return "/".join(path)


def render(cmp: Comparison, ref_path: str, new_path: str, show: int = 20, every: bool = False) -> list[str]:
    """The text report."""
    out = [LABEL, f"NOTE: {REVIEW}", f"REF: {ref_path}", f"NEW: {new_path}"]
    tier = cmp.tier
    out.append(f"tier: {tier.name}" + (f" ({'; '.join(tier.reasons)})" if tier.reasons else ""))
    if tier.name == "undetermined":
        out += [f"  missing selecting leaf: {m}" for m in tier.missing]
        out.append("no T0 to T3 tolerance applied; for runs that predate the selecting leaves use --td-only")
    else:
        for system, group, status in tier.evidence:
            if status != "equal" or every:
                out.append(f"  evidence {system}/{group}: {status}")
        if tier.name == "TD" and tier.only_trajectory_digest:
            out.append("  TD selected only by main_digest / estimator_digest: per-leaf differences listed below (report only)")
        if tier.name == "TD" and tier.devices_differ:
            out.append("  TD between two devices triggers O4 (owner choice of confirmatory device)")
    if tier.name == "undetermined":
        out.append(f"leaves: REF {cmp.n_ref}, NEW {cmp.n_new} (not compared)")
    else:
        out.append(f"leaves: REF {cmp.n_ref}, NEW {cmp.n_new}, union {cmp.n_ref + cmp.n_new - cmp.n_common}, "
                   f"common {cmp.n_common}, equal {cmp.n_equal}, different {len(cmp.rows)}, "
                   f"one-sided {len(cmp.one_sided)}")
    for side in ("ref", "new"):
        out.append(f"excluded ({side}): provenance {cmp.excluded[side]['provenance']} leaves, "
                   f"timing {cmp.excluded[side]['timing']} leaves")
    if tier.name == "undetermined":
        return out + [f"RESULT: UNDETERMINED (exit {cmp.exit_code}): " + "; ".join(cmp.reasons)]
    out.append(f"leaves without a chain rule in compare_pilot's table (treated as network): {cmp.untagged}")
    if cmp.scopes:
        out.append("discrete counts that differ (scope of the 0.1 hw exception): "
                   + ", ".join(sorted({f"{s or '*'}/{b}" for s, b in cmp.scopes})))
    groups: dict[tuple[str, str, str], list[Row]] = defaultdict(list)
    for row in (*cmp.rows, *cmp.one_sided):
        groups[(row.rule, row.cls, row.outcome)].append(row)
    out.append("differences by rule (every FAIL, FINDING and DEF is listed; a pass group lists its first "
               f"{show}{'' if not every else ', all with --all'}):")
    for (rule, cls, outcome), members in sorted(groups.items(), key=lambda kv: kv[0]):
        shown = [(r.metric if r.metric is not None else r.rel) for r in members]
        rels = [v for v in shown if v is not None]
        worst = max(zip(shown, members), key=lambda t: -1.0 if t[0] is None else t[0])[1]
        out.append(f"  [{outcome}] {rule} (class {cls or '-'}): {len(members)} leaves"
                   + (f", max metric {max(rels):.3g} at {show_path(worst.path)}" if rels else ""))
        limit = len(members) if (outcome in ("FAIL", "FINDING", "DEF") or every) else show
        for r in members[:limit]:
            out.append(f"      {show_path(r.path)}: {fmt_num(r.ref)} -> {fmt_num(r.new)}"
                       + (f" rel {r.rel:.3g}" if r.rel is not None else "")
                       + (f" metric {r.metric:.3g}" if r.metric is not None and r.metric != r.rel else "")
                       + (f" tol {r.tol:.3g}" if r.tol is not None else "")
                       + (f" ({r.note})" if r.note else ""))
    defs = [r for r in cmp.rows if r.outcome == "DEF"]
    for r in defs:
        out.append(f"DEF: verdict or flag differs at {show_path(r.path)}: {r.ref!r} -> {r.new!r}")
    verdict_td = [r for r in cmp.rows if tier.name == "TD" and r.note == "verdict-type leaf"]
    if verdict_td:
        out.append(f"TD: {len(verdict_td)} verdict-type leaves differ (reported, no failure):")
        out += [f"      {show_path(r.path)}: {r.ref!r} -> {r.new!r}" for r in verdict_td[:show]]
    if cmp.declared:
        out.append("10x rule (ROADMAP; classes per note M2):")
        for label, d in cmp.declared.items():
            tol = "bitwise on the same device type" if d["declared"] is None else f"{d['declared']:.0e}"
            out.append(f"  class {label}: {d['n']} leaves, max rel {d['max_rel']:.3g}"
                       + (f" at {d['argmax']}" if d["argmax"] else "") + f" -> declared {tol}"
                       + (f"; {d['defaulted']} leaves in the default class (g)" if d["defaulted"] else "")
                       + (("; O3 FINDING: above 1e-4" if tier.name == "T0" else
                           "; above 1e-4 (information: this pair is not the R1/R2 calibration)")
                          if d["o3"] else ""))
    if cmp.td is not None:
        out += render_td(cmp.td)
    if cmp.not_computed:
        out.append("NOT COMPUTED:")
        out += [f"  {item}" for item in cmp.not_computed]
    out.append(f"RESULT: {['PASS', 'FAIL', 'UNDETERMINED'][cmp.exit_code]} (exit {cmp.exit_code})"
               + (": " + "; ".join(cmp.reasons) if cmp.reasons else ""))
    return out


def render_td(td: dict) -> list[str]:
    """The TD table lines."""
    out = [f"TD statistic: z_level {z_level():.4f}, bound {TD_BOUND} on max(|z_sym|, |z_away|) per part",
           f"  {'system':9s} {'part':17s} {'d':>9s} {'z_sym':>7s} {'z_away':>7s} {'hw1/hw0':>8s}  status"]
    for p in td["parts"]:
        if "error" in p:
            out.append(f"  {p['system']:9s} {p['part']:17s} NOT COMPUTABLE: {p['error']}")
            continue
        ratio = p["hw1"] / p["hw0"] if p["hw0"] else math.inf
        out.append(f"  {p['system']:9s} {p['part']:17s} {p['d']:9.4f} {p['z_sym']:7.2f} {p['z_away']:7.2f} "
                   f"{ratio:8.3f}  {'FAIL' if p['fail'] else 'ok'}")
    out.append(f"  parts computed {td['k']} of {td['expected']} expected (cannot be computed: {td['n_error']}); sum z^2 symmetric "
               f"{td['sum_sym']:.2f}, away {td['sum_away']:.2f}; max |z| symmetric {td['max_sym']:.2f}, "
               f"away {td['max_away']:.2f}; failing parts {td['n_fail']}")
    return out


def run_td_only(ref_tree: dict, new_tree: dict, ref_path: str, new_path: str) -> tuple[list[str], int]:
    """``--td-only``: the TD table without tier selection or leaf comparison."""
    td = td_statistic(ref_tree, new_tree)
    code = EXIT_FAIL if td["n_fail"] else (EXIT_UNDETERMINED if td["n_error"] or td["no_systems"] else EXIT_OK)
    out = [LABEL, f"NOTE: {REVIEW}", f"REF: {ref_path}", f"NEW: {new_path}",
           "mode: --td-only (no tier selection, no per-leaf comparison)", *render_td(td),
           f"RESULT: {['PASS', 'FAIL', 'UNDETERMINED'][code]} (exit {code})"]
    return out, code


def main(argv: list[str] | None = None) -> int:
    """Command-line entry; returns the exit code."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("ref", type=Path)
    ap.add_argument("new", type=Path)
    ap.add_argument("--tol-other", type=float, default=TOL_O3,
                    help="class (b) to (g) tolerance of T1 to T3 (default 1e-4, the O3 ceiling)")
    ap.add_argument("--show", type=int, default=20)
    ap.add_argument("--all", action="store_true", help="list every difference and every evidence row")
    ap.add_argument("--allow-not-computed", action="store_true")
    ap.add_argument("--td-only", action="store_true")
    try:
        args = ap.parse_args(argv)
    except SystemExit as exc:
        return EXIT_UNDETERMINED if exc.code else EXIT_OK
    try:
        if not (args.tol_other > 0 and math.isfinite(args.tol_other)) or args.show < 0:
            raise ToolError("--tol-other must be positive and finite, --show not negative")
        if args.tol_other > TOL_O3 and not args.td_only:
            raise ToolError(f"--tol-other {args.tol_other:g} is above the O3 ceiling {TOL_O3:g}: refused "
                            "(A6: such a tolerance is a finding, never adopted silently)")
        ref_tree, new_tree = load(args.ref), load(args.new)
        if args.td_only:
            lines, code = run_td_only(ref_tree, new_tree, str(args.ref), str(args.new))
        else:
            cmp = compare_trees(ref_tree, new_tree, args.tol_other, args.allow_not_computed)
            lines, code = render(cmp, str(args.ref), str(args.new), args.show, args.all), cmp.exit_code
    except ToolError as exc:
        print(f"compare_runs: error: {exc}", file=sys.stderr)
        return EXIT_UNDETERMINED
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main())
