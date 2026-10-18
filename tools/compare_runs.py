#!/usr/bin/env python3
"""Compare two ``results.json`` files under the reproducibility tiers of WU-0003 A6 (WU-0003.9).

Usage::

    python3 -I tools/compare_runs.py REF NEW [--tol-other X] [--show N] [--all]
        [--allow-not-computed] [--td-only] [--tags]

``REF`` and ``NEW`` are ``results.json`` files, or run directories that contain one. The tool is
read-only on both and writes nothing but its report to standard output. It reads statistics and
computes none of the study's; it computes the comparison only. It imports ``tools/compare_pilot.py``
(flattening and the chain tags of its rule table) and the standard library, and no ``lpcstudy``
module. The report is labelled DEVELOPMENT.

**Needs owner review before freeze** (tolerance and verdict-comparison code, CSQ2 use in WU-0016;
plan A10, B2 row .9). Every tolerance below is quoted from the plan, never chosen here; where the
plan is silent the strict reading is applied where possible, and the looser owner readings are marked (see
"Readings that the plan leaves open").

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
  list is A6's, as matched by name (``licensing_kind``; B1 item 3 leaves it unchanged): K (``chosen_K``, ``realized_K``),
  ``best_single``, ``n_states`` and the state denominators, and clip, nu-cap and replacement counts
  (``error_clips*``, ``nu_cap_clips``, ``*_replacements``). Other clip counts and state counts by meaning
  (``*_clipped_*``, ``n_clipped_inputs``, the ``n_*_states`` family, ``evaluation/denominators/test_states``)
  are not matched and fail exactly: an owner question (Q7). The scope is per system: a ``n_states`` or
  ``best_single`` reaches its own block; K reaches ``fitted``, ``H3a``, ``H3c`` and ``regime_curve``, and a K
  under ``robustness/<s>/<variant>`` reaches that variant only; a clip, nu-cap or replacement count under
  ``systems/<s>/handling`` reaches the whole of system ``s`` (owner reading 9: looser than "result block",
  and not causal), except the leaves of the network-independent chains (``cp``, ``oracle``, ``dynamics``,
  ``fixture``), which it does not reach (round 3: a differing clip count must not replace the cp 1e-12 rule,
  OF-7 working default, of that system's leaves). The top-level ``handling`` block (``totals``, ``by_system``, ``robustness``), a per-system
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
  other estimate (DEC-0027). **The failing rule is ``z_away > 3.4`` alone (owner ruling OF-5 of 2026-10-18,
  WU-0003.9c; before it a part failed on ``max(z_sym, z_away)``).** ``z_sym`` is still computed and printed, as
  information only: it fails no part, ``n_fail`` counts ``z_away`` only, and ``td["governing"]`` says ``"z_away"``.
  A TD pair between two devices triggers O4 (printed).

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

Readings that the plan leaves open (strict where possible; the looser owner readings are marked)
------------------------------------------------------------------------------------------------
* The leaf-to-chain map is ``compare_pilot``'s rule table, completed by the override table ``TAGS`` of this
  tool (WU-0003.9b, plan amendment 3 C4; needs owner review before freeze). **Every float leaf of the pilot schema has a
  chain tag, and an untagged float leaf is NOT COMPUTABLE** (exit 2 in every tier, also when it is equal in both runs
  or on one side only, and ``--allow-not-computed`` does not waive it; a failure elsewhere still gives exit 1). The
  old default, "untagged = network chain, class rules, 1e-4", never decides a tolerance. The tag is the
  most-downstream module a leaf depends on, derived from the production code, with a one-line reason that cites the
  producing function; ``fixture`` (a constant or a configuration echo) and ``cp`` are network-independent; ``network``
  is every leaf that reads a trained estimator or the PLP forecast or something built from them, and any leaf whose
  independence cannot be shown from the code (the looser class). The report prints, per run, the number of float leaves
  tagged by the table, tightened, by an override and untagged, and the reason of every override that tagged a differing leaf;
  ``--tags`` prints the whole override table. The pin is the test on the committed path shapes of P1, P0 and the smoke
  preset (``tests/unit/fixtures/pilot_schema``).
* **OF-7 (owner ruling of 2026-10-18, WU-0003.9c).** Four H1a outputs of the tolerance-stopped ``curve_fit`` (TRF,
  ftol = xtol = gtol = 1e-8, 2-point Jacobian) are governed by the A6 rules for QoIs, not by the cp 1e-12 of N1
  (which assumes forward-stable direct arithmetic): ``fitted_inverse_dim`` and ``ci_inverse_dim/[0|1]`` as class (a)
  (``|d| <= 1e-4 s``, ``s = max(|lo|, |hi|)`` of the reference ``ci_inverse_dim``), ``floor_rms`` as class (g) (the
  (b) to (g) tolerance ``--tol-other``, default ``1e-4 |ref|``; an exceedance is a FINDING). Basis: note
  ``docs/agent/notes/2026-10-14-math-wu0003-9-q1.md`` sections Q1.3 and Q1.4 (a-priori bound 4.0e-5 s, so the
  QoI tolerance has a safety factor of 2.5; 1e-5 s is not derivable). The table is ``RETAGS``. It changes the
  tolerance rule only: the dependence chain of these leaves stays ``cp`` (``compare_pilot``'s tag is not edited), so
  a whole-system clip count still does not reach them. If the reference has no interval for a class-(a) leaf, the
  class cannot be established and the strict cp 1e-12 rule stays, said in the row's note. The 1e-12 rule stays for
  every other leaf. In particular the H1a ``ratio`` and ``ratio_ci`` (the same fit, cp by dependence, not named in
  the ruling) still meet cp 1e-12 and carry a pointer to the note when they fail: 3 pointer leaves per
  (system, rho), 18 per pilot, where the first report counted 42. Extending the ruling to them is one row each in
  ``RETAGS``; the owner has not so ruled. The cp 1e-12 rule also applies to ``H1a`` ``inverse_dim_reference`` and
  ``median_seed_by_n_lib/*`` (direct arithmetic; the adopted tightening of Q1.4).
* ``TIGHTENINGS`` may replace a ``network`` chain of ``compare_pilot``'s table by a network-independent one where the
  code shows no estimator dependence, never the reverse (``H1d/rows/nhat/spearman``, review R2); ``compare_pilot`` is
  not edited. The scope of a clip, nu-cap or replacement count follows the chain, so it never reaches a
  network-independent leaf.
* A ``cov_digest`` difference alone is undetermined (see above); a ``None`` system never opens a scope.
* **Looser owner readings:** the whole-system scope of a clip, nu-cap or replacement count (reading 9, above);
  the ``network`` tag of every leaf whose independence
  of the estimator cannot be shown (above); and the listing of the integers of a K-shaped block when K differs
  (``follows_k``: listed, no licence), which is the "list with no licence" option of OF-1.
* ``fraction_above_chi2`` and ``fraction_late_progress`` have no T2/T3 tolerance in A6: class (c)
  applies (T1: ``1e-8 |ref|``); the two-proportion band is printed beside them.
* The per-estimate LM check and the order-statistic bands need arrays of the per-state dump
  (WU-0003.7b), whose schema is not final. They are implemented as pure functions
  (``lm_estimate_check``, ``order_statistic_band``) and reported as NOT COMPUTED here; that is
  exit 2 unless ``--allow-not-computed``.
* A pair is "T0" only if host, device and threads are all equal; any other equal-digest pair is T1.

Exit codes: 0 pass; 1 a tolerance, verdict or TD failure (a ``DEF`` line for a verdict); 2 tier
undetermined, an unreadable input, a usage error, a TD part that cannot be computed, a float leaf with no
chain tag (never waived), or a required check that is NOT COMPUTED (unless ``--allow-not-computed``). ``--td-only`` computes the TD
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

OF7_POINTER = ("OF-7 (ruled 2026-10-18 for fitted_inverse_dim, ci_inverse_dim and floor_rms only): ratio and ratio_ci come "
               "from the same tolerance-stopped fit but are not named in the ruling, so cp 1e-12 is kept; see "
               "docs/agent/notes/2026-10-14-math-wu0003-9-q1.md")
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
TD_BOUND = 3.4             # A6, B1 item 5: |z| bound per primary part (applied to z_away: OF-5, 2026-10-18)
TD_GOVERNING = "z_away"    # the TD form that fails a part; z_sym is information only
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
    if lk == "K":
        # R14: a K of a robustness variant reaches that variant only, never the K blocks of the main system
        return (system, "K") if path[0] == "systems" else (system, scope_block(path))
    return (system, scope_block(path))


def scope_block(path: Path_) -> str:
    """The block a scope refers to: ``loc``'s block, but one scope per robustness variant
    (``robustness/<variant>``), so a count of one variant does not reach another variant or the main system."""
    if path[0] == "robustness" and len(path) > 2:
        return f"robustness/{path[2]}"
    return loc(path)[1]


def in_scope(scopes: list[tuple[str, str]], path: Path_, star: bool = True) -> bool:
    """Whether a path is in the scope of a differing licensing count of its own system.

    ``star=False`` leaves out the whole-system scope of clip counts (used for one-sided leaves: only the
    shape that follows a count of its own block or K is excused).
    """
    system, _ = loc(path)
    block = scope_block(path)
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


# ----------------------------------------------------------------------------------- chain tags (C4)
def _tags(chain: str, patterns: str, reason: str) -> list[cp.Rule]:
    """Expand braces and build the override rows of one pattern group."""
    return [cp.Rule(pattern, "unchanged", reason=reason, chain=chain)
            for text in patterns.split() for pattern in cp._expand(text)]


LM_NAMES = "fraction_above_chi2,fraction_late_progress,fraction_no_decrease,median_iterations,median_residual,p95_residual"
CONSTANT = "constant, not computed from data: "
NETWORK_W = ("w* = oracle.py:oracle_weight reads the PLP moments sq_plp and cross (ensemble.py:ensemble_moments: the PLP "
             "forecast runs StateEstimator.estimate_counted from the trained psi, networks.py:train_estimator)")


def _build_tags() -> list[cp.Rule]:
    """The override table (WU-0003.9b, plan amendment 3 C4; needs owner review before freeze).

    Every float leaf of the pilot schema that ``compare_pilot``'s table leaves without a chain gets a row here,
    with the producing function as its reason. The chain is the most-downstream module the leaf depends on, derived
    from the production code: ``cp`` and ``fixture`` (a constant echoed from the configuration or a module constant)
    are network-independent; ``network`` is every leaf that reads a trained estimator, the PLP forecast or a quantity
    built from them (w*, the fitted proxies and regimes, the LM refinement), and the leaves whose independence of
    them cannot be shown from the code. Two patterns must not match one leaf: ``tag_of`` raises at lookup (a test
    checks every leaf of the fixtures), and a leaf that is tagged in ``compare_pilot``'s table never reaches this one.
    """
    S = "systems/*"
    out: list[cp.Rule] = []
    add = out.extend
    add(_tags("fixture", "config/**",
              "run configuration echoed from config.py:StudyConfig, not computed; compare_runs.py:decide compares "
              "it for identity and any difference fails"))
    # ---- constants -----------------------------------------------------------------------------------------
    add(_tags("fixture", f"{S}/H1a/band/[] {S}/H1a/level",
              CONSTANT + "analysis.py:h1a_library_scaling writes H1A_BAND and H1_LEVEL"))
    add(_tags("fixture", f"{S}/H1b/threshold/[] robustness/*/*/H1b/threshold/[]",
              CONSTANT + "analysis.py:h1b_seed_amplifier writes H1B_BAND"))
    add(_tags("fixture", f"{S}/H1c/threshold/[]", CONSTANT + "analysis.py:h1c_horizon_law writes H1C_BAND"))
    add(_tags("fixture", f"{S}/H1c/thresholds/[]",
              CONSTANT + "analysis.py:h1c_horizon_law writes config.py:admissible_thresholds, a function of the "
              "configuration and the noise level"))
    add(_tags("fixture", f"{S}/H1d/level {S}/H1d/threshold",
              CONSTANT + "analysis.py:h1d_correlations writes H1_LEVEL and H1D_BAND[0]"))
    add(_tags("fixture", f"{S}/V7/threshold/[]", CONSTANT + "analysis.py:v7_efficiency writes the band [0.9, 1.1]"))
    add(_tags("fixture", f"{S}/H2b/library_change/{{level,rho}}",
              CONSTANT + "analysis.py:h2b_knob_response writes PRIMARY_LEVEL and config.core_noise"))
    add(_tags("fixture", f"{S}/H2b/library_change_reported/*/level {S}/H2b/library_curves/*/*/level",
              CONSTANT + "analysis.py:h2b_knob_response writes the literal level 0.95"))
    add(_tags("fixture", f"{S}/H2c/A4o_minus_A2/level",
              CONSTANT + "analysis.py:h2c_state_dependence writes the literal level 0.95"))
    add(_tags("fixture", f"{S}/H2e/by_noise/*/level",
              CONSTANT + "analysis.py:h2e_noise_matching passes the literal level 0.95 to _paired_change"))
    add(_tags("fixture", f"{S}/H3b/D/level {S}/H3b/weight_lambda/level {S}/H3b/weight_lambda/band/[]",
              CONSTANT + "analysis.py:h3b_importances writes the literal level 0.95 and the band [0, 0.2]"))
    add(_tags("fixture", f"{S}/H3c/level {S}/H3c/threshold",
              CONSTANT + "analysis.py:h3c_ratio writes PRIMARY_LEVEL and H3C_BOUND"))
    add(_tags("fixture", f"{S}/clip_sensitivity/{{clip_level,perturbed_level}}",
              CONSTANT + "clip_sensitivity.py:_block writes ERROR_CLIP and PERTURBED_LEVEL"))
    add(_tags("fixture", "robustness/*/*/scale_times_rho",
              CONSTANT + "experiments.py:_perturbation_scale_variant echoes the configured perturbation scale"))
    add(_tags("fixture", f"{S}/handling/cells/*/lm/noise {S}/handling/cells/*/lm/by_kind/*/noise "
              "handling/robustness/*/cells/*/lm/noise handling/robustness/*/cells/*/lm/by_kind/*/noise",
              CONSTANT + "estimation.py:lm_summary echoes the noise level of the cell (config.py)"))
    add(_tags("fixture", f"{S}/verification/P2c/cell/noise {S}/verification/P2c/tolerances/kappa",
              CONSTANT + "experiments.py:p2c_verification echoes the cell noise; validation.py:p2_bound_summary "
              "writes P2C_KAPPA"))
    # ---- cp chain --------------------------------------------------------------------------------------------
    add(_tags("cp", f"{S}/H1a/inverse_dim_reference {S}/H1a/by_noise/*/median_seed_by_n_lib/*",
              "analysis.py:h1a_library_scaling: direct arithmetic (a median, a mean of log ratios) on the CP seed "
              "errors (ensemble.py:forecast_draws analog_seed: analog retrieval against the true states, no estimator) "
              "and on the oracle local dimension (oracle.py:local_dimension_counted); adopted tightening of note "
              "2026-10-14-math-wu0003-9-q1 section Q1.4"))
    add(_tags("cp", f"{S}/H1a/by_noise/*/ratio {S}/H1a/by_noise/*/ratio_ci/[]",
              "analysis.py:_median_fit_stats via h1a_library_scaling: depends on the CP seed errors and the oracle local "
              "dimension only (cp). It is an output of the tolerance-stopped curve_fit, like the three sibling fit leaves "
              "that the OF-7 ruling of 2026-10-18 re-tags (RETAGS); the ruling does not name ratio and ratio_ci, so "
              "cp 1e-12 may fail on correct code at a T2 pair and carries the pointer to note "
              "2026-10-14-math-wu0003-9-q1 (owner to rule whether they follow)"))
    add(_tags("cp", f"{S}/H1d/rows/nhat/interval/[]",
              "analysis.py:h1d_proxies: the pair (nhat, N) is ev.noise_sens against moments.noise_sens, both from analog "
              "retrieval on the noisy library (ensemble.py:evaluation_draws, ensemble_moments, retrieval_spread): no "
              "estimator and no PLP; the bootstrap is analysis.py:h1d_correlations. The sibling rows/nhat/spearman is "
              "tagged network in compare_pilot (looser than this leaf)"))
    add(_tags("cp", f"{S}/H2c/calibration_mse/A0",
              "analysis.py:h2c_state_dependence: mean of evals.cp_err**2 at H_ref on the calibration split "
              "(ensemble.py:forecast_draws cp_err: analog retrieval, no estimator)"))
    add(_tags("cp", f"{S}/verification/P2c/{{fraction_switching_draws,fraction_violations,population/*,"
              "noise_second_moment/*,tightness/*,tightness/N_over_sqrt_B/*,tolerances/tau_N_max}",
              "validation.py:p2_bound_summary on the terms of p2_bound_terms: the analog library, the clean queries and "
              "the noise draws only (experiments.py:p2c_verification), no estimator and no PLP"))
    # ---- network chain -----------------------------------------------------------------------------------------
    lm = ("estimation.py:lm_summary of the Levenberg-Marquardt refinement in StateEstimator.estimate_counted "
          "(ensemble.py:forecast_draws), started from the trained psi (networks.py:train_estimator)")
    add(_tags("network", f"{S}/handling/cells/*/lm/{{{LM_NAMES}}} {S}/handling/cells/*/lm/by_kind/*/{{{LM_NAMES}}} "
              f"handling/robustness/*/cells/*/lm/{{{LM_NAMES}}} handling/robustness/*/cells/*/lm/by_kind/*/{{{LM_NAMES}}}", lm))
    add(_tags("network", f"{S}/V7/efficiency_ci_by_noise/*/[]",
              "analysis.py:v7_efficiency: bootstrap of the median efficiency of the PLP estimation seed "
              "(moments.est_seed: the psi state estimate)"))
    add(_tags("network", f"{S}/H1d/rows/{{analog_seed,estimation_seed,growth}}/interval/[]",
              "analysis.py:h1d_proxies: the proxies come from allocation.py:ProfileProxies.fit on the estimated nu and "
              "the model growth at the estimated state (ensemble.py:evaluation_draws est_nu, growth_proxy)"))
    add(_tags("network", f"{S}/Q-N/{{deployable,oracle}}/{{logit_w_interior,w_zero_indicator}}/{{ci/[],delta_r2,r2_four,r2_three}}",
              "analysis.py:qn_profile_block: the targets are " + NETWORK_W + ", also for the oracle profile"))
    add(_tags("network", f"{S}/H2a/{{ci_mc_se/[],range_ci/[],complete_case/median_range,complete_case/range_ci/[],"
              "range_by_span/*/median,part_ii/*/ci/[],part_ii/*/ci_mc_se/[],part_ii/*/partial_corr}",
              "analysis.py:h2a_initial_segments and h2a_part_ii: " + NETWORK_W + ", and the PLP seed est_seed "
              "(ci_mc_se: statistics.py:endpoint_mc_error of the same bootstrap values)"))
    add(_tags("network", f"{S}/H2b/noise/ci_mc_se/[] {S}/H2b/library_change/{{ci/[],ci_mc_se/[],mean_change}} "
              f"{S}/H2b/library_change_reported/*/{{ci/[],mean_change}} "
              f"{S}/H2b/library_curves/*/*/{{mean,median,mean_ci/[],median_ci/[]}}",
              "analysis.py:h2b_knob_response: " + NETWORK_W))
    add(_tags("network", f"{S}/H2c/A4o_minus_A2/{{ci/[],mean,relative}} {S}/H2c/calibration_mse/A1 "
              f"{S}/H2c/re:A4_minus_(?!A1$|A2$)\\w+/{{ci/[],mean,relative}}",
              "analysis.py:h2c_state_dependence: per-state MSE at H_ref of A4 and A4o (closed-form weights from the "
              "fitted proxies and from est_seed) against A2 or a single forecaster (pipeline.py:score_rules); "
              "calibration_mse/A1 is the mean of evals.plp_err**2 (PLP)"))
    add(_tags("network", f"{S}/H2e/by_noise/*/{{ci/[],median_change}} {S}/H2e/corr_curve/*/*",
              "analysis.py:h2e_noise_matching: the CP-PLP error correlation over the oracle draws "
              "(ensemble.py:draw_correlation of cp_err and plp_err)"))
    add(_tags("network", f"{S}/H3a/{{iqr_lt/[],logrank_p_raw/[]}}",
              "analysis.py:h3a_logrank: regimes of the deployable profile (allocation.py:RegimeMap.assign, fitted by "
              "pipeline.py:fit_rules), realized horizons of A5 and the horizon target of the oracle hybrid "
              "(allocation.py:state_horizon_target)"))
    add(_tags("network", f"{S}/H3b/D/{{ci/[],value}} {S}/H3b/stability {S}/H3b/weight_lambda/{{ci/[],importance}}",
              "analysis.py:h3b_importances: trees fitted on the deployable profile (proxies from the estimated nu) "
              "with targets w* and the oracle-hybrid horizon"))
    add(_tags("network", f"{S}/H3c/{{ci/[],ci_mc_se/[]}}",
              "analysis.py:h3c_ratio: ratio of the per-state MSE of A5 over A4 (pipeline.py:score_rules, PLP errors)"))
    add(_tags("network", f"{S}/clip_sensitivity/by_hypothesis/*/parts/*/{{delta,delta_bound,ratio}} "
              f"{S}/clip_sensitivity/share_test/* {S}/clip_sensitivity/weight_shift/{{A2,A5_max}}",
              "clip_sensitivity.py:_compute: the verdict statistics re-evaluated with every clipped PLP error at H_ref "
              "moved to twice the clip (ensemble.py:clip_errors, plp_err)"))
    add(_tags("network", f"{S}/fitted/{{regime_weights_href,regime_horizons_km_lyapunov}}/*/[]",
              "experiments.py:fitted_record from pipeline.py:fit_rules and allocation.py:calibrate_regimes: regime "
              "weights and Kaplan-Meier horizons from the calibration moments and draws (PLP)"))
    add(_tags("network", f"{S}/km_curves/A5/[] {S}/oracle_recovery/{{A5_vs_Astar,mse_at_href/A5}} "
              f"{S}/scores/A5/{{agreement_href,km_median_lyapunov,mse_href,rmst_lyapunov,mse/*,regret/*}}",
              "pipeline.py:score_rules for A5: regime weights from fit_rules, err = w cp_err + (1 - w) plp_err"))
    add(_tags("network", f"{S}/scores/A\\*/regret/*",
              "pipeline.py:score_rules: oracle.py:excess_mse(moments, w*) with w* from the PLP moments; it is 0.0 by "
              "construction, which either class meets only with d = 0, so the network class loosens nothing"))
    add(_tags("network", "robustness/*/*/{H2a_partial_corr_zero,H2a_partial_corr_interior,H2a_partial_corr_zero_fin,"
              "H2a_partial_corr_interior_fin,ci_zero/[],ci_interior/[]}",
              "experiments.py:_variant_summary and _perturbation_scale_variant: analysis.py:h2a_part_ii on w* and the "
              "PLP seed (" + NETWORK_W + ")"))
    return out


TAGS = cp.Table(_build_tags())
TAG_CHAINS = frozenset({"fixture", "dynamics", "cp", "oracle", "network"})
UNTAGGED_RULE = "untagged: NOT COMPUTABLE"


def tag_of(path: Path_) -> cp.Rule | None:
    """The override row of a leaf, or ``None`` (an overlap of two rows is a defect and raises)."""
    found = TAGS.matches(path)
    if len(found) > 1:
        raise ToolError(f"{len(found)} override rows match {'/'.join(path)}: " + "; ".join(t.pattern for t in found))
    return found[0] if found else None


def _build_tightenings() -> list[cp.Rule]:
    """The tightening-only overrides (fix round 1, review R2; needs owner review before freeze).

    A row here replaces a ``network`` chain of ``compare_pilot``'s table by a network-independent one for the
    leaves where the code shows no estimator dependence. It never replaces a network-independent chain and
    never gives a looser one (``chain_source`` applies it only to a table chain ``network``, and a test checks that
    every row names a network-independent chain). ``compare_pilot`` is not edited: its table carries the rules of
    the v1 regression.
    """
    return _tags("cp", "systems/*/H1d/rows/nhat/spearman",
                 "analysis.py:h1d_proxies: the pair (nhat, N) is ev.noise_sens against moments.noise_sens, both from analog "
                 "retrieval on the noisy library (ensemble.py:evaluation_draws, ensemble_moments, retrieval_spread): no "
                 "estimator and no PLP, like its interval rows/nhat/interval (finding of review R2; compare_pilot's "
                 "table says network, which is looser than the code shows)")


TIGHTENINGS = cp.Table(_build_tightenings())


@dataclass(frozen=True)
class Retag(cp.Rule):
    """One tolerance re-tag (OF-7, owner ruling of 2026-10-18): a leaf that keeps its dependence chain but is
    governed by the A6 rules for QoIs instead of the cp 1e-12 of N1.

    Attributes
    ----------
    scale : str
        ``"a"``: class (a), ``|d| <= 1e-4 s`` with ``s = max(|lo|, |hi|)`` of the reference interval of the leaf.
        ``"g"``: class (g), the (b) to (g) tolerance (``--tol-other``) relative to ``|ref|``.
    """

    scale: str = "a"


def _build_retags() -> list[Retag]:
    """The OF-7 re-tag table (owner ruling of 2026-10-18, note 33; needs owner review before freeze).

    Exactly the four H1a leaves that the ruling names: ``fitted_inverse_dim`` and ``ci_inverse_dim/[0|1]`` (class
    (a)) and ``floor_rms`` (class (g), as note 2026-10-14-math-wu0003-9-q1 section Q1.4 says). A row never tags a
    leaf (``chain_source`` does not read this table): it only selects the tolerance rule of a leaf that already has
    its chain. The H1a ``ratio`` and ``ratio_ci`` are deliberately absent (not named in the ruling).
    """
    common = ("OF-7 ruled 2026-10-18: output of the tolerance-stopped curve_fit in analysis.py:_fit_seed_law "
              "(TRF, ftol = xtol = gtol = 1e-8, 2-point Jacobian), for which the 1e-12 premise of N1 (direct arithmetic) "
              "fails; ")
    qoi = (common + "a-priori bound 4.0e-5 s, so the A6 rule for QoIs (class (a), 1e-4 s) holds with a factor 2.5 "
           "(note 2026-10-14-math-wu0003-9-q1 sections Q1.3 and Q1.4)")
    cls_g = (common + "no interval, so relative to |ref|: measured flip <= 6.3e-7 and stopping error <= 6.8e-7 relative, "
             "so the A6 rule of class (g) (1e-4 |ref|) holds with a factor >= 70 (note 2026-10-14-math-wu0003-9-q1 "
             "sections Q1.3, last row of the table, and Q1.4)")
    return [Retag(pattern, "unchanged", reason=reason, chain="cp", scale=scale)
            for pattern, scale, reason in (
                ("systems/*/H1a/by_noise/*/fitted_inverse_dim", "a", qoi),
                ("systems/*/H1a/by_noise/*/ci_inverse_dim/[]", "a", qoi),
                ("systems/*/H1a/by_noise/*/floor_rms", "g", cls_g))]


RETAGS = cp.Table(_build_retags())


def retag_of(path: Path_) -> Retag | None:
    """The OF-7 re-tag row of a leaf, or ``None`` (an overlap of two rows is a defect and raises)."""
    found = RETAGS.matches(path)
    if len(found) > 1:
        raise ToolError(f"{len(found)} re-tag rows match {'/'.join(path)}: " + "; ".join(t.pattern for t in found))
    return found[0] if found else None  # type: ignore[return-value]


def chain_source(path: Path_) -> tuple[str, str, str]:
    """``(chain, source, reason)`` of a leaf: ``compare_pilot``'s table first, then the override table.

    ``source`` is ``"table"``, ``"tightening"`` (a table chain ``network`` replaced by a network-independent
    one), ``"override"`` or ``""`` (untagged: the chain and the reason are empty).
    """
    found = cp.TABLE.matches(path)
    if len(found) > 1:                     # two table rules for one leaf is a defect of the table, never a tag
        raise ToolError(cp.Table.explain(path, found))
    if found and found[0].chain:
        tight = TIGHTENINGS.matches(path)
        if tight and found[0].chain == "network":
            return tight[0].chain, "tightening", tight[0].reason
        return found[0].chain, "table", found[0].reason
    tag = tag_of(path)
    return (tag.chain, "override", tag.reason) if tag else ("", "", "")


def chain_of(path: Path_) -> str:
    """The chain tag of a leaf (``''`` if it is untagged): ``compare_pilot``'s table, tightened, else the overrides."""
    return chain_source(path)[0]


def untagged_leaves(flat: dict[Path_, object]) -> list[Path_]:
    """The float leaves of a run that no table tags: NOT COMPUTABLE (C4), sorted."""
    return sorted(path for path, value in flat.items() if is_float(value) and not chain_of(path))


def untagged_census(flat: dict[Path_, object]) -> dict[str, int]:
    """The untagged float leaves of a run by block (``{}`` when the schema is complete, as C4 requires)."""
    out: dict[str, int] = defaultdict(int)
    for path in untagged_leaves(flat):
        out[loc(path)[1]] += 1
    return dict(sorted(out.items()))


def source_counts(flat: dict[Path_, object]) -> dict[str, int]:
    """Float leaves of a run by the source of their chain tag: ``table``, ``tightening``, ``override``, ``untagged``."""
    out = {"table": 0, "tightening": 0, "override": 0, "untagged": 0}
    for path, value in flat.items():
        if is_float(value):
            out[chain_source(path)[1] or "untagged"] += 1
    return out


def tag_lines(flats: dict[str, dict[Path_, object]]) -> list[str]:
    """The whole override table with the number of float leaves each row tags in each run, and its reason."""
    counts: dict[str, dict[str, int]] = {}
    for name, flat in flats.items():
        counts[name] = defaultdict(int)
        for path, value in flat.items():
            if is_float(value) and chain_source(path)[1] == "override":
                tag = tag_of(path)
                assert tag is not None
                counts[name][tag.pattern] += 1
    out = [f"chain tags assigned by override ({len(TAGS.rules)} patterns; the rest come from compare_pilot's rule table):"]
    for tag in TAGS.rules:
        out.append(f"  {tag.pattern}: chain {tag.chain}, float leaves "
                   + ", ".join(f"{counts[n][tag.pattern]} {n}" for n in flats))
        out.append(f"      reason: {tag.reason}")
    out.append(f"tolerance re-tags (OF-7, owner ruling of 2026-10-18; {len(RETAGS.rules)} patterns; the chain stays, "
               "the tolerance rule is the A6 rule of the class):")
    retag_counts: dict[str, dict[str, int]] = {name: defaultdict(int) for name in flats}
    for name, flat in flats.items():
        for path, value in flat.items():
            tag = retag_of(path) if is_float(value) else None
            if tag is not None:
                retag_counts[name][tag.pattern] += 1
    for tag in RETAGS.rules:
        out.append(f"  {tag.pattern}: class {tag.scale}, float leaves "
                   + ", ".join(f"{retag_counts[n][tag.pattern]} {n}" for n in flats))
        out.append(f"      reason: {tag.reason}")
    out.append(f"chain tags tightened over compare_pilot's table ({len(TIGHTENINGS.rules)} patterns; network to a "
               "network-independent chain, never the reverse):")
    for tag in TIGHTENINGS.rules:
        out.append(f"  {tag.pattern}: chain {tag.chain}")
        out.append(f"      reason: {tag.reason}")
    return out


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
    census: dict[str, int] = field(default_factory=dict)    # untagged float leaves by block (REF)
    untagged_leaves: list[Path_] = field(default_factory=list)   # untagged float leaves of either run (C4)
    flats: dict[str, dict[Path_, object]] = field(default_factory=dict)   # the flattened runs, for the tag report


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

    Returns 1 if the leaf has no chain tag in ``compare_pilot``'s rule table or the override table: it is NOT
    COMPUTED and nothing is decided for it (counted, not hidden).
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
    if not chain_of(path):                        # C4: no tag, so no tolerance is decided (the default is retired)
        row.rule, row.outcome = UNTAGGED_RULE, "NOT COMPUTED"
        row.note = "float leaf with no chain tag in compare_pilot's table or the override table"
        row.for_10x = True
        return 1
    chain = chain_of(path)
    lm = lm_name(path)
    row.for_10x = True
    if lm == "median_iterations":
        row.cls, row.rule, row.tol, row.for_10x = "lm", "median_iterations within 1", TOL_LM_ITERATIONS, False
        row.metric = abs(a - b)
        row.outcome = "pass" if row.metric <= row.tol else "FAIL"
    elif in_scope(scopes, path, star=chain not in cp.NETWORK_INDEPENDENT) and interval is not None:
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
    elif (retag := retag_of(path)) is not None and (retag.scale == "g" or row.cls == "a"):
        # OF-7 (WU-0003.9c): a tolerance-stopped fit output meets the A6 rule of its class, not the cp 1e-12
        if retag.scale == "a":
            row.rule, row.tol = "QoI / interval endpoint (OF-7 re-tag)", TOL_QOI
            row.outcome = "pass" if row.metric <= row.tol else "FAIL"
        else:
            row.rule, row.tol = "class (b) to (g) (OF-7 re-tag)", tol_other
            row.outcome = "pass" if row.metric <= row.tol else "FINDING"
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
    if row.rule == "cp chain relative" and retag_of(path) is not None:     # class (a) needs the reference interval
        row.note = (row.note + "; " if row.note else "") + (
            "OF-7 re-tag not applied: no reference interval, so the class (a) scale is undefined; cp 1e-12 kept")
    if (row.outcome == "FAIL" and row.rule == "cp chain relative" and "H1a" in path and "by_noise" in path
            and (name == "ratio" or (path[-2] == "ratio_ci" and name in ("[0]", "[1]")))):
        row.note = (row.note + "; " if row.note else "") + OF7_POINTER
    return 0


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
    Since the OF-5 ruling of 2026-10-18 the failing rule is ``z_away`` alone (``z_sym`` is information).

    Returns
    -------
    dict
        ``d``, ``z_sym`` (information), ``z_away``, ``z_governing`` (= ``z_away``, the value the bound applies to),
        ``hw0``, ``hw1``; or ``{"error": text}`` if an input is missing or not finite, or an arm is negative
        (the estimate outside its interval).
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

    z_away = ratio(arm0 / zl, arm1 / zl)
    return {"d": d, "z_sym": ratio(hw0 / zl, hw1 / zl), "z_away": z_away, "z_governing": z_away,
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

    A part fails iff ``z_away > TD_BOUND`` (OF-5, owner ruling of 2026-10-18, WU-0003.9c); ``z_sym`` is computed
    and kept for information.

    Returns
    -------
    dict
        ``parts`` (rows with ``system``, ``part`` and ``td_part``'s keys, or ``error``; ``fail`` is the
        away-arm rule), ``governing`` (``"z_away"``: the form the bound applies to), ``expected`` (6 x systems),
        ``sum_sym`` (information), ``sum_away``, ``max_z`` (the largest governing ``z_away``), ``max_sym``
        (information), ``max_away``, ``k`` (parts computed), ``n_error``, ``n_fail`` (``z_away`` only).
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
            res["fail"] = "error" not in res and res["z_away"] > TD_BOUND
            parts.append(res)
    good = [p for p in parts if "error" not in p]
    return {"parts": parts, "governing": TD_GOVERNING, "k": len(good), "n_error": errors,
            "n_fail": sum(p["fail"] for p in good),
            "expected": len(TD_PARTS) * len(systems),
            "sum_sym": sum(p["z_sym"] ** 2 for p in good), "sum_away": sum(p["z_away"] ** 2 for p in good),
            "max_z": max((p["z_away"] for p in good), default=0.0),
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
    unc = sorted(set(untagged_leaves(flat_ref)) | set(untagged_leaves(flat_new)))   # C4: NOT COMPUTABLE
    flats = {"REF": flat_ref, "NEW": flat_new}
    if tier.name == "undetermined":
        return Comparison(tier, len(flat_ref), len(flat_new), 0, 0, [], [], excluded, [], {}, None, [],
                          0, EXIT_UNDETERMINED,
                          ["tier undetermined: " + "; ".join(tier.missing) + " (no T0 to T3 tolerance applied)"],
                          untagged_census(flat_ref), unc, flats)
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
            reasons.append(f"TD: {td['n_fail']} of {td['k']} parts exceed {TD_BOUND} ({TD_GOVERNING})")
        if td["n_error"] or td["no_systems"]:
            code = code if code == EXIT_FAIL else EXIT_UNDETERMINED
            reasons.append(f"TD: {td['n_error']} parts cannot be computed")
    if unc:
        by_block = defaultdict(int)
        for path in unc:
            by_block[loc(path)[1]] += 1
        reasons.append(f"{len(unc)} float leaves have no chain tag: NOT COMPUTABLE ("
                       + ", ".join(f"{b} {n}" for b, n in sorted(by_block.items())) + f"; first {show_path(unc[0])})")
        code = code if code == EXIT_FAIL else EXIT_UNDETERMINED           # never waived by --allow-not-computed
    if code == EXIT_OK and not_computed and not allow_not_computed:
        code = EXIT_UNDETERMINED
        reasons.append(f"{len(not_computed)} required checks NOT COMPUTED")
    return Comparison(tier, len(flat_ref), len(flat_new), len(set(flat_ref) & set(flat_new)), n_equal, rows,
                      one_sided, excluded, scopes, declared, td, not_computed, untagged, code, reasons,
                      untagged_census(flat_ref), unc, flats)


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


def tag_summary(cmp: Comparison) -> list[str]:
    """The report lines on the chain tags (C4): the count per source and run, the untagged leaves by block, and the
    reason of every override that tagged a differing leaf."""
    parts = []
    for name, flat in cmp.flats.items():
        c = source_counts(flat)
        parts.append(f"{name}: compare_pilot table {c['table']}, tightened {c['tightening']}, "
                     f"override {c['override']}, untagged {c['untagged']}")
    out = ["chain tags of the float leaves (config included; untagged leaves are NOT COMPUTABLE, exit 2): "
           + "; ".join(parts)]
    if cmp.untagged_leaves:
        out.append("  untagged by block (REF): " + (", ".join(f"{b} {n}" for b, n in cmp.census.items()) or "none")
                   + f"; differing untagged leaves not computed: {cmp.untagged}; first: "
                   + ", ".join(show_path(q) for q in cmp.untagged_leaves[:5]))
    used: dict[str, list[Row]] = defaultdict(list)
    for r in cmp.rows:
        if r.kind != "float":                 # only a float leaf needs a chain (a non-float ambiguity must not abort)
            continue
        chain, source, reason = chain_source(r.path)
        if source in ("override", "tightening"):
            used[f"{source} {(tag_of(r.path) or TIGHTENINGS.matches(r.path)[0]).pattern}"].append(r)
    for key in sorted(used):
        chain, _, reason = chain_source(used[key][0].path)
        out.append(f"  {key}: chain {chain}, {len(used[key])} differing leaves; reason: {reason}")
    retagged: dict[str, list[Row]] = defaultdict(list)
    for r in cmp.rows:
        tag = retag_of(r.path) if r.kind == "float" else None
        if tag is not None and r.rule.endswith("(OF-7 re-tag)"):
            retagged[tag.pattern].append(r)
    for pattern in sorted(retagged):
        tag = retag_of(retagged[pattern][0].path)
        assert tag is not None
        out.append(f"  OF-7 re-tag {pattern}: class {tag.scale}, {len(retagged[pattern])} differing leaves; "
                   f"reason: {tag.reason}")
    return out


def render(cmp: Comparison, ref_path: str, new_path: str, show: int = 20, every: bool = False,
           tags: bool = False) -> list[str]:
    """The text report (``tags``: also the whole override table with its reasons)."""
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
    out += tag_summary(cmp)
    if tags:
        out += tag_lines(cmp.flats)
    if tier.name == "undetermined":
        return out + [f"RESULT: UNDETERMINED (exit {cmp.exit_code}): " + "; ".join(cmp.reasons)]
    if any(OF7_POINTER in r.note for r in cmp.rows):
        out.append("pointer: " + OF7_POINTER)
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
    out = [f"TD statistic: z_level {z_level():.4f}, bound {TD_BOUND} on z_away per part (the away-arm standard error, "
           f"DEC-0027; owner ruling OF-5 of 2026-10-18); z_sym is information only and fails no part",
           f"  {'system':9s} {'part':17s} {'d':>9s} {'z_sym (information)':>19s} {'z_away (governs)':>16s} "
           f"{'hw1/hw0':>8s}  status"]
    for p in td["parts"]:
        if "error" in p:
            out.append(f"  {p['system']:9s} {p['part']:17s} NOT COMPUTABLE: {p['error']}")
            continue
        ratio = p["hw1"] / p["hw0"] if p["hw0"] else math.inf
        out.append(f"  {p['system']:9s} {p['part']:17s} {p['d']:9.4f} {p['z_sym']:19.2f} {p['z_away']:16.2f} "
                   f"{ratio:8.3f}  {'FAIL' if p['fail'] else 'ok'}")
    out.append(f"  parts computed {td['k']} of {td['expected']} expected (cannot be computed: {td['n_error']}); sum z^2 away "
               f"{td['sum_away']:.2f}, symmetric (information) {td['sum_sym']:.2f}; max z away {td['max_away']:.2f}, "
               f"symmetric (information) {td['max_sym']:.2f}; failing parts (z_away > {TD_BOUND}) {td['n_fail']}")
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
    ap.add_argument("--tags", action="store_true",
                    help="also print the override table of chain tags with the leaf counts and the reasons")
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
            lines, code = render(cmp, str(args.ref), str(args.new), args.show, args.all, args.tags), cmp.exit_code
    except ToolError as exc:
        print(f"compare_runs: error: {exc}", file=sys.stderr)
        return EXIT_UNDETERMINED
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main())
