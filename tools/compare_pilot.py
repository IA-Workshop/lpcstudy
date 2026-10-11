#!/usr/bin/env python3
"""Regression of a DEV-0 pilot run against the v1 pilot (WU-0002.12, step 1: the comparison tool).

Usage::

    python3 -I tools/compare_pilot.py NEW_RESULTS_JSON [--old docs/study/pilot_results_v1.json]
        [--report docs/study/dev_regression_dev0.md]
        [--leaves-json runs/dev/wu0002-12/compare_leaves.json]
        [--run-dir DIR] [--manifest-row TEXT]

What it does. It reads two ``results.json`` files and flattens each to leaves addressed by tuples
of keys (written ``a/b/c``; list items are ``[0]``, ``[1]``; a ``/`` inside a key is written
``%2F``, as in the v1 key ``delay/2``). The v1 paths are transformed to the v3 names (``V1_TO_V3``,
the correction table of the decision log; ``H3b/{realized_K, regret_ratio_by_K}`` move to
``regime_curve``; ``*_by_N`` becomes ``*_by_n_lib``; robustness ``H1c`` becomes ``H1b``; the H1d
``spearman/<x>`` leaves move to ``rows/<x>/spearman``; two H3a keys are renamed). The new side's
``provenance`` is excluded. Every remaining leaf of either side is classified by exactly one rule
of the table ``RULES`` into one of five groups:

* ``unchanged``: must be bitwise equal (IEEE bytes for floats; ``0.0`` and ``-0.0`` differ; NaN
  equals NaN and is counted), or within the rule's ``rel_tol`` (0 by default; a positive value needs
  a cited, logged change of summation order);
* ``changed``: changed by design; listed with the old and the new value, the sub-task and the reason;
* ``new``: only in the new run; ``removed``: only in the v1 pilot;
* ``timing``: wall-clock, not compared (both values are reported).

A leaf that matches no rule or two rules is an error (exit 2) and is never classified silently.

Branch. The switch rule of ROADMAP WU-0002.12: if a ``context`` leaf of the new run differs from
the pilot (a float beyond 1e-12 relative, any other type at all) the fallback branch applies,
else the bitwise branch. The fallback criterion is the owner's (LPC.AI.12). Until its constants
are recorded (``FALLBACK_CONSTANTS`` is ``None``) the fallback branch is refused: exit 3 naming the
missing decision. Both branches check the gate (V1 to V7, ``gate_pass``) and P2(c) in the new run.

Outputs. ``--report`` (default ``docs/study/dev_regression_dev0.md``), whose first line is
``DEVELOPMENT (DEV-0): not a hypothesis test``, and a per-leaf JSON file (default
``runs/dev/wu0002-12/compare_leaves.json``, untracked). The tool reads statistics and computes
none. It imports nothing but the standard library, and no ``lpcstudy`` module.

Exit codes: 0 no finding; 1 findings (the report lists them); 2 a leaf without exactly one rule, or
unreadable input, or a usage error; 3 the fallback branch applies and its constants are missing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import struct
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

LABEL = "DEVELOPMENT (DEV-0): not a hypothesis test"
EXIT_FINDINGS, EXIT_ERROR, EXIT_FALLBACK = 1, 2, 3
SWITCH_REL_TOL = 1e-12
PRIMARY_LEVEL = 1.0 - 0.05 / 3.0
CI_LEVEL = 0.95
CLASSES = ("unchanged", "changed", "new", "removed", "timing")

# The correction table of docs/study/decision_log_lpc.md ("v1 / code" -> "v3"), typed by hand.
# None marks a dropped result; its leaves keep their path under the prefix ``v1:``.
V1_TO_V3: dict[str, str | None] = {
    "H1a": "V7", "H1b": "H1a", "H1c": "H1b", "H1d": "H1c", "H1e": "H1d", "H1f": "Q-N",
    "H2a": "H2a", "H2b": "H2b", "H2c": "H2c", "H2d": "H2d", "H2e": "gain_bound",
    "H3a": "H3a", "H3b": None, "H3c": "H3b", "H3d": "H3c", "T1": None,
}
DROPPED_PREFIX = "v1:"

# The fallback criterion F2 needs k and the per-system standard errors. They are the owner's to
# fix (LPC.AI.12; the proposal is in the WU-0002.12 plan, not in force): a dict
# {"dec": "DEC-nnnn", "k": float, "se": {system: float}} once a DEC records them.
FALLBACK_CONSTANTS: dict | None = None

Path_ = tuple[str, ...]


class ToolError(Exception):
    """An input or table error; ``main`` reports it and exits with code 2."""


class Unclassified(ToolError):
    """Leaves that match no rule, or two rules."""


class _Missing:
    """Marks a leaf that is absent on one side."""

    def __repr__(self) -> str:
        return "MISSING"


MISSING = _Missing()


# ------------------------------------------------------------------------------ leaves
def flatten(tree: object, prefix: Path_ = ()) -> dict[Path_, object]:
    """Flatten a JSON tree to its leaves.

    Dict keys become path segments (``/`` written ``%2F``), list items ``[i]``. An empty list is
    one leaf ``<path>/[]`` (value ``[]``) and an empty dict one leaf ``<path>/<empty>``, so that nothing
    vanishes silently and a rule for the items of a list also covers the list when it is empty. An
    empty root has no leaves.

    Parameters
    ----------
    tree : object
        A parsed JSON value.
    prefix : tuple[str, ...]
        Path of ``tree``.

    Returns
    -------
    dict[tuple[str, ...], object]
        Leaf path to value.
    """
    if isinstance(tree, dict):
        if not tree:
            return {} if not prefix else {(*prefix, "<empty>"): tree}
        out: dict[Path_, object] = {}
        for key, value in tree.items():
            out.update(flatten(value, (*prefix, str(key).replace("/", "%2F"))))
        return out
    if isinstance(tree, list):
        if not tree:
            return {(*prefix, "[]"): tree}
        out = {}
        for i, value in enumerate(tree):
            out.update(flatten(value, (*prefix, f"[{i}]")))
        return out
    return {prefix: tree}


def show(path: Path_) -> str:
    """The ``/``-joined text of a path."""
    return "/".join(path)


def transform_v1(path: Path_) -> Path_:
    """Map a v1 leaf path to its v3 name.

    Parameters
    ----------
    path : tuple[str, ...]
        A leaf path of ``pilot_results_v1.json``.

    Returns
    -------
    tuple[str, ...]
        The path under the v3 names. A leaf of a dropped result (v1 ``H3b`` except its two moved
        curves, ``T1``) keeps its path under the key ``v1:<key>``; leaves of removed features
        (shift, A4f, transfer, ``delay/2``, Lorenz-96) keep their path and are classified
        ``removed`` by the rule table.
    """
    p = [k[:-5] + "_by_n_lib" if k.endswith("_by_N") else k for k in path]
    p = ["median_at_largest_n_lib" if k == "median_at_largest_N" else k for k in p]
    if p[0] == "systems" and len(p) >= 3:
        old = p[2]
        if old in V1_TO_V3:
            p[2] = V1_TO_V3[old] or DROPPED_PREFIX + old
        if old == "H3b" and len(p) > 3 and p[3] in ("realized_K", "regret_ratio_by_K"):
            p = [p[0], p[1], "regime_curve", *p[3:]]
        elif old == "H1e" and len(p) > 4 and p[3] == "spearman":
            who = p[4]
            if who == "estimation_seed_vs_cramer_rao":
                p = [*p[:3], who, *p[5:]]
            else:
                p = [*p[:3], "rows", "nhat" if who == "noise_sensitivity" else who, "spearman",
                     *p[5:]]
        elif old == "H3a" and len(p) > 3:
            p[3] = {"logrank_holm_p": "logrank_p_holm",
                    "mean_iqr_lyapunov": "iqr_lt_mean"}.get(p[3], p[3])
    elif p[0] == "verdicts" and len(p) >= 2 and p[1] in V1_TO_V3:
        p[1] = V1_TO_V3[p[1]] or DROPPED_PREFIX + p[1]
    elif p[0] == "robustness" and len(p) >= 4 and p[3] == "H1c":
        p[3] = "H1b"
    return tuple(p)


# ------------------------------------------------------------------------------ comparison
def values_equal(old: object, new: object, rel_tol: float = 0.0) -> str:
    """Compare two leaf values exactly.

    Floats compare by IEEE bytes: ``0.0`` and ``-0.0`` differ, and NaN equals NaN. Types must match
    exactly: ``1`` and ``1.0`` differ, and so do ``True`` and ``1``.

    Parameters
    ----------
    old, new : object
        Leaf values.
    rel_tol : float
        Relative tolerance for finite floats (0 means bitwise).

    Returns
    -------
    str
        ``equal``, ``equal_nan`` (both NaN), ``within_tol``, ``differs`` or ``type``.
    """
    if type(old) is not type(new):
        return "type"
    if isinstance(old, float):
        if math.isnan(old) and math.isnan(new):  # type: ignore[arg-type]
            return "equal_nan"
        if struct.pack("<d", old) == struct.pack("<d", new):  # type: ignore[arg-type]
            return "equal"
        if rel_tol > 0 and math.isfinite(old) and math.isfinite(new):  # type: ignore[arg-type]
            scale = max(abs(old), abs(new))  # type: ignore[type-var]
            if abs(old - new) <= rel_tol * scale:  # type: ignore[operator]
                return "within_tol"
        return "differs"
    return "equal" if old == new else "differs"


# ------------------------------------------------------------------------------ rule table
@dataclass(frozen=True)
class Rule:
    """One row of the rule table.

    Attributes
    ----------
    pattern : str
        ``/``-joined segments in the v3 namespace. A segment is literal, or a glob with ``*``
        (``\\*`` is a literal star), or ``[]`` (any list index), or ``re:<regex>`` (full match). A
        last segment ``**`` matches one or more segments. The first segment is literal.
    cls : str
        ``unchanged``, ``changed``, ``new``, ``removed`` or ``timing``.
    sub, item, reason : str
        Sub-task (``WU-0002.k``), concordance or decision item, and the reason.
    direction : str
        For ``changed``: ``new>=old`` (up to 1e-12 relative) or ``zero`` (new is exactly 0.0).
    rel_tol, rel_tol_ref : float, str
        Relative tolerance of an ``unchanged`` rule and the logged change of summation order that
        justifies it (required when ``rel_tol`` > 0).
    interval, level : str, float or None
        ``interval``: key of the sibling ``[lo, hi]`` of a statistic. ``level``: the nominal level
        of an interval leaf.
    discrete, bulk : bool
        ``discrete``: an integer or label that can flip (F5). ``bulk``: curves or arrays, reported
        in summary rows.
    chain : str
        Computation chain (``dynamics``, ``fixture``, ``cp``, ``oracle``, ``network``) where the
        plan names it.
    when : tuple
        ``(relative path under the system, value)``: an ``unchanged`` leaf is expected only if the
        new run has that value there (the H2c best single forecaster).
    alert : bool
        A leaf present on the new side is a finding (a failed robustness variant).
    """

    pattern: str
    cls: str
    sub: str = ""
    item: str = ""
    reason: str = ""
    direction: str = ""
    rel_tol: float = 0.0
    rel_tol_ref: str = ""
    interval: str = ""
    level: float | None = None
    discrete: bool = False
    bulk: bool = False
    chain: str = ""
    when: tuple = ()
    alert: bool = False


def _segment_matcher(seg: str):
    if seg == "[]":
        regex = re.compile(r"\[\d*\]")
        return regex.fullmatch
    if seg.startswith("re:"):
        return re.compile(seg[3:]).fullmatch
    if "*" in seg.replace("\\*", ""):
        parts = re.split(r"(?<!\\)\*", seg)
        regex = re.compile(".*".join(re.escape(p.replace("\\*", "*")) for p in parts), re.DOTALL)
        return regex.fullmatch
    literal = seg.replace("\\*", "*")
    return lambda text, literal=literal: text == literal


class Table:
    """An indexed rule table: ``classify`` returns the one rule that matches a path."""

    def __init__(self, rules: list[Rule]) -> None:
        self.rules = list(rules)
        self._fixed: dict[tuple[str, int], list[tuple[Rule, list]]] = defaultdict(list)
        self._tail: dict[str, list[tuple[Rule, list, int]]] = defaultdict(list)
        seen: set[str] = set()
        for rule in self.rules:
            self._check(rule, seen)
            segs = rule.pattern.split("/")
            tail = segs[-1] == "**"
            if tail:
                segs = segs[:-1]
            matchers = [_segment_matcher(s) for s in segs]
            if tail:
                self._tail[segs[0]].append((rule, matchers, len(segs)))
            else:
                self._fixed[(segs[0], len(segs))].append((rule, matchers))

    @staticmethod
    def _check(rule: Rule, seen: set[str]) -> None:
        first = rule.pattern.split("/")[0]
        if rule.cls not in CLASSES:
            raise ToolError(f"rule {rule.pattern!r}: unknown class {rule.cls!r}")
        if not first or first.startswith("re:") or "*" in first.replace("\\*", "") or first == "[]":
            raise ToolError(f"rule {rule.pattern!r}: the first segment must be literal")
        if rule.pattern in seen:
            raise ToolError(f"rule {rule.pattern!r} is listed twice")
        seen.add(rule.pattern)
        if rule.rel_tol < 0 or (rule.rel_tol > 0 and (not rule.rel_tol_ref or rule.cls != "unchanged")):
            raise ToolError(f"rule {rule.pattern!r}: rel_tol needs an unchanged rule and a cited "
                            "logged change of summation order (rel_tol_ref)")
        if rule.cls == "changed" and not (rule.sub and rule.reason):
            raise ToolError(f"rule {rule.pattern!r}: a changed rule needs a sub-task and a reason")
        if rule.direction not in ("", "new>=old", "zero") or (rule.direction and rule.cls != "changed"):
            raise ToolError(f"rule {rule.pattern!r}: bad direction {rule.direction!r}")
        if rule.when and rule.cls != "unchanged":
            raise ToolError(f"rule {rule.pattern!r}: 'when' belongs to an unchanged rule")

    def matches(self, path: Path_) -> list[Rule]:
        """All rules that match ``path``."""
        found = []
        for rule, matchers in self._fixed.get((path[0], len(path)), ()):
            if all(m(seg) for m, seg in zip(matchers, path)):
                found.append(rule)
        for rule, matchers, count in self._tail.get(path[0], ()):
            if len(path) > count and all(m(seg) for m, seg in zip(matchers, path)):
                found.append(rule)
        return found

    def classify(self, path: Path_) -> Rule:
        """The one rule of ``path``.

        Raises
        ------
        Unclassified
            If no rule or more than one rule matches.
        """
        found = self.matches(path)
        if len(found) != 1:
            raise Unclassified(self.explain(path, found))
        return found[0]

    @staticmethod
    def explain(path: Path_, found: list[Rule]) -> str:
        """One line naming the path and, for an ambiguity, the rules."""
        if not found:
            return f"no rule matches {show(path)}"
        return f"{len(found)} rules match {show(path)}: " + "; ".join(r.pattern for r in found)


def _expand(pattern: str) -> list[str]:
    match = re.search(r"\{([^{}]*)\}", pattern)
    if not match:
        return [pattern]
    out = []
    for choice in match.group(1).split(","):
        out.extend(_expand(pattern[:match.start()] + choice + pattern[match.end():]))
    return out


INTERVAL_KEYS = frozenset({"ci", "interval", "ratio_ci", "band", "mean_ci", "median_ci", "ci_zero",
                           "ci_interior", "range_ci", "partial_ci", "ci_inverse_dim"})


def _rules(cls: str, patterns: str, sub: str = "", item: str = "", reason: str = "",
           **kw: object) -> list[Rule]:
    """Expand braces and build the rules. A pattern for the items of an interval (``.../ci/[]``)
    also covers the key itself, because an interval that was not computed is ``None``, not a list
    (``analysis.py``: 'a number that was not computed is not shown')."""
    out = []
    for text in patterns.split():
        for pattern in _expand(text):
            out.append(Rule(pattern, cls, sub, item, reason, **kw))  # type: ignore[arg-type]
            head, _, last = pattern.rpartition("/")
            if last == "[]" and head.rpartition("/")[2] in INTERVAL_KEYS:
                out.append(Rule(head, cls, sub, item, reason, **kw))  # type: ignore[arg-type]
    return out


def _build_rules() -> list[Rule]:
    R: list[Rule] = []
    add = R.extend
    S = "systems/*"
    smoke = "smoke-equal (v1 baseline smoke against develop, session scratch)"
    # ---- config ------------------------------------------------------------------------
    add(_rules("unchanged",
               "config/{allocator_draws,allocator_epochs,bootstrap_block,bootstrap_resamples,"
               "burn_in_lyapunov,convergence_states,core_library,core_noise,embedding_dim,"
               "estimator_epochs,estimator_pairs,estimator_refine_steps,horizon_max_lyapunov,"
               "linear_regime_rms,n_calibration,n_construction,n_eval_draws,n_oracle_draws,n_test,"
               "n_test_sweep,name,noise_sensitivity_draws,perturbation_dirs,primary_threshold,"
               "reference_horizon_lyapunov,seed,steps_per_lyapunov,theiler_lyapunov,"
               "thinning_factor,threshold_noise_factor} "
               "config/{analog_counts,convergence_draws,core_systems,estimator_widths,"
               "eval_horizons_lyapunov,library_sizes,library_sweep_noises,misspec_levels,"
               "noise_levels,perturbation_scales,regime_counts,robustness_dims,"
               "robustness_systems,thresholds}/[]",
               item="config of the PILOT preset", reason="the preset is unchanged except below"))
    add(_rules("changed", "config/regime_max_primary", "WU-0002.3", "D-13",
               "K rule covers K up to 8 (was 5)", discrete=True))
    add(_rules("removed", "config/{transfer_sources,transfer_targets}/[]", "WU-0002.1", "D-17",
               "transfer stage removed"))
    add(_rules("new", "config/seed_id", "WU-0001", "", "seed id recorded"))
    # ---- estimators (top level and per system) ------------------------------------------
    # Keys of ``estimators`` are tuples (system, embedding dim, delay, noise); no literal spaces
    # (the rule strings are split on white space).
    kept = r"re:\('(lorenz63|rossler|chua)',\s\d+,\s(?!2,)\d+,\s[\d.]+\)"
    gone96 = r"re:\('lorenz96',.*"
    gone2 = r"re:\('\w+',\s\d+,\s2,\s[\d.]+\)"
    add(_rules("unchanged", f"estimators/{kept}/chosen_width", chain="network", discrete=True,
               item="R2", reason="psi training is unchanged (network chain, R1 exposure)"))
    add(_rules("unchanged", f"estimators/{kept}/val_loss_by_width/*", chain="network",
               item="R2", reason="psi training is unchanged (network chain, R1 exposure)"))
    add(_rules("timing", f"estimators/{kept}/seconds", reason="wall-clock"))
    add(_rules("removed", f"estimators/{gone96}/** estimators/{gone2}/**", "WU-0002.1", "D-17",
               "Lorenz-96 and the delay/2 robustness variant are removed"))
    add(_rules("unchanged", f"{S}/validation/estimators/*/chosen_width", chain="network",
               discrete=True, item="R2", reason="psi training is unchanged"))
    add(_rules("unchanged", f"{S}/validation/estimators/*/val_loss_by_width/*", chain="network",
               item="R2", reason="psi training is unchanged"))
    add(_rules("timing", f"seconds {S}/seconds {S}/validation/estimators/*/seconds",
               reason="wall-clock"))
    # ---- context and validation ----------------------------------------------------------
    add(_rules("unchanged", f"{S}/context/{{acf_time,ami_delay,delay,embed_dim,library_len,spacing,"
               "theiler,trajectory_len}", chain="dynamics", discrete=True, item="R2, F1",
               reason="dynamics and embedding code unchanged since v1-baseline"))
    add(_rules("unchanged", f"{S}/context/{{interval,lambda_max,obs_scale}}", chain="dynamics",
               item="R2, switch rule", reason="dynamics and embedding code unchanged"))
    add(_rules("unchanged", f"{S}/validation/{{delay_jacobian_rel_err,gain_rel_err,"
               "integrator_max_dev_sigma,km_max_abs_dev}", chain="fixture", item="R2 (V1, V2, V5, V6)",
               reason="fixed-seed or deterministic fixtures"))
    add(_rules("unchanged", f"{S}/validation/crlb_ratio_{{max,median,min}}", chain="fixture",
               item="R2 (V2)", reason="fixed-seed fixture"))
    add(_rules("unchanged", f"{S}/validation/cp_median_vpt_lyapunov", chain="cp", item="R2 (V3)",
               reason="CP chain"))
    add(_rules("unchanged", f"{S}/validation/convergence/{{pass,used_M}} "
               f"{S}/validation/convergence/*/{{mean_abs_dev_from_max,median_half_width}}",
               chain="network", item="R2 (V4)", reason="oracle convergence check"))
    add(_rules("unchanged", f"{S}/validation/gate/{{V1,V2,V4,V5,V6}}", item="R2, R4",
               reason="gate flags V1 to V6"))
    add(_rules("changed", f"{S}/validation/gate/gate_pass", "WU-0002.10", "D-15",
               "V7 enters the gate"))
    add(_rules("new", f"{S}/validation/gate/V7", "WU-0002.10", "D-15, DEC-0015",
               "V7 is a gate flag"))
    # ---- verification, handling (new) -----------------------------------------------------
    add(_rules("new", f"{S}/verification/**", "WU-0005.5", "P2(c)", "P2(c) verification check"))
    add(_rules("new", f"{S}/handling/** handling/**", "WU-0002.11", "D-18",
               "counted handling of clips, replacements and fallbacks"))
    # ---- fitted ----------------------------------------------------------------------------
    add(_rules("unchanged", f"{S}/fitted/{{analog_proxy,estimation_proxy}}/{{floor,slope}}",
               chain="cp", item="R2", reason="proxy fits are unchanged"))
    add(_rules("unchanged", f"{S}/fitted/nu_cap", chain="network", item="R2",
               reason="the nu cap is unchanged"))
    add(_rules("changed", f"{S}/fitted/chosen_K", "WU-0002.3", "D-13 (DEF-0003)",
               "K rule on the calibration excess MSE; the pilot K was the fallback 5",
               discrete=True))
    add(_rules("changed", f"{S}/fitted/regime_weights_href/*/[]", "WU-0002.3", "D-12 (DEF-0003)",
               "regime weight from unclipped moments; K changes", bulk=True))
    add(_rules("changed", f"{S}/fitted/regime_horizons_km_lyapunov/*/[]", "WU-0002.3", "D-12, D-13",
               "regimes follow the new K and weights", bulk=True))
    # ---- scores ----------------------------------------------------------------------------
    plain = "A0,A1,A2,A3,A4,A4o,A\\*"
    later = "A1,A2,A3,A4,A4o,A\\*"
    add(_rules("unchanged", f"{S}/scores/{{{plain}}}/agreement_href "
               f"{S}/scores/{{{later}}}/{{km_median_lyapunov,mse_href,rmst_lyapunov}} "
               f"{S}/scores/{{{later}}}/mse/*", chain="network", item="R2",
               reason="MSE, KM and agreement are unchanged for A0 to A4, A4o, A*"))
    add(_rules("unchanged", f"{S}/scores/A0/{{km_median_lyapunov,mse_href,rmst_lyapunov}} "
               f"{S}/scores/A0/mse/*", chain="cp", item="R2",
               reason="CP alone: MSE and KM depend on the CP chain only"))
    add(_rules("changed", f"{S}/scores/{{A0,A1,A2,A3,A4,A4o}}/regret/*", "WU-0002.3",
               "D-11 (DEF-0002), R3",
               "exact excess V(w) - V(w*) >= c(w - w*)^2 replaces the clipped form",
               direction="new>=old", chain="network"))
    add(_rules("changed", f"{S}/scores/A\\*/regret/*", "WU-0002.3", "D-11 (DEF-0002), R3",
               "A* is its own reference: excess exactly 0.0", direction="zero"))
    add(_rules("changed", f"{S}/scores/A5/{{agreement_href,km_median_lyapunov,mse_href,"
               "rmst_lyapunov} " f"{S}/scores/A5/{{mse,regret}}/*", "WU-0002.3", "D-11 to D-13",
               "A5 follows the new K and regime weights"))
    add(_rules("removed", f"{S}/scores/A4f/**", "WU-0002.1", "D-17", "A4f removed"))
    add(_rules("unchanged", f"{S}/km_curves/{{{later}}}/[]", chain="network", bulk=True, item="R2",
               reason="Kaplan-Meier curves of A1 to A4, A4o, A* are unchanged"))
    add(_rules("unchanged", f"{S}/km_curves/A0/[]", chain="cp", bulk=True, item="R2",
               reason="Kaplan-Meier curve of CP alone is unchanged"))
    add(_rules("changed", f"{S}/km_curves/A5/[]", "WU-0002.3", "D-13",
               "A5 follows the new K", bulk=True))
    add(_rules("removed", f"{S}/km_curves/A4f/[]", "WU-0002.1", "D-17", "A4f removed", bulk=True))
    add(_rules("unchanged", f"{S}/weight_profile/{{horizons,median,q25,q75}}/[]", chain="network",
               bulk=True, item="R2", reason="weight profile is unchanged"))
    add(_rules("unchanged", f"{S}/oracle_recovery/A4_vs_A4o "
               f"{S}/oracle_recovery/mse_at_href/{{{later}}}", chain="network", item="R2",
               reason="functions of the MSE at H_ref"))
    add(_rules("unchanged", f"{S}/oracle_recovery/mse_at_href/A0", chain="cp", item="R2",
               reason="MSE of CP alone at H_ref"))
    add(_rules("unchanged", f"{S}/oracle_recovery/A4_vs_Astar", chain="network",
               item="not in R2's list; " + smoke,
               reason="function of the MSE at H_ref of A2, A4 and A*, all unchanged"))
    add(_rules("changed", f"{S}/oracle_recovery/A5_vs_Astar {S}/oracle_recovery/mse_at_href/A5",
               "WU-0002.3", "D-13", "A5 follows the new K"))
    add(_rules("removed", f"{S}/oracle_recovery/mse_at_href/A4f", "WU-0002.1", "D-17",
               "A4f removed"))
    # ---- V7 (v1 H1a) -----------------------------------------------------------------------
    add(_rules("unchanged", f"{S}/V7/median_slope", chain="network", interval="ci", item="R2",
               reason="same code path as v1 H1a (WU-0002.10)"))
    add(_rules("unchanged", f"{S}/V7/ci/[]", chain="network", level=CI_LEVEL, item="R2",
               reason="same code path as v1 H1a"))
    add(_rules("unchanged", f"{S}/V7/efficiency_median_by_noise/*", chain="network", item="R2",
               reason="same code path as v1 H1a"))
    add(_rules("unchanged", f"{S}/V7/threshold/[]", item=smoke, reason="band [0.9, 1.1]"))
    add(_rules("changed", f"{S}/V7/pass", "WU-0002.10", "D-28, DEC-0015",
               "pass needs the slope and every noise level"))
    add(_rules("new", f"{S}/V7/{{efficiency_ci_by_noise/*/[],efficiency_pass_by_noise/*,"
               "invariant_mean_replacements/*,n_dropped_resamples/**,n_nonfinite,n_states,"
               "slope_pass}", "WU-0002.10, .11", "D-28, A10",
               "V7 slope part, per-level flags and counts"))
    # ---- H1a (v1 H1b) ----------------------------------------------------------------------
    h1a = f"{S}/H1a"
    add(_rules("changed", f"{h1a}/by_noise/*/{{fitted_inverse_dim,floor_rms}}", "WU-0002.4",
               "D-01", "median fit instead of the mean fit", chain="cp"))
    add(_rules("changed", f"{h1a}/by_noise/*/ci_inverse_dim/[]", "WU-0002.4", "D-01",
               "interval of the median fit", level=CI_LEVEL, chain="cp"))
    add(_rules("removed", f"{h1a}/by_noise/*/mean_seed_by_n_lib/*", "WU-0002.4", "D-01",
               "replaced by median_seed_by_n_lib"))
    add(_rules("removed", f"{h1a}/by_noise/*/relative_error_vs_local_dim", "WU-0002.4",
               "D-25(h)", "replaced by ratio and ratio_ci"))
    add(_rules("removed", f"{h1a}/{{floor_increases,local_dimension_median,threshold}}",
               "WU-0002.4", "D-19, D-25(h)",
               "floor condition dropped; reference is Levina-Bickel k-1; band replaces threshold"))
    add(_rules("changed", f"{h1a}/pass", "WU-0002.4, .9", "D-19, D-14",
               "pass from the interval of 1/d inside the band"))
    add(_rules("new", f"{h1a}/{{band/[],inverse_dim_reference,level,n_excluded_nonfinite,n_states,"
               "reason,reference_estimator,verdict} "
               f"{h1a}/by_noise/*/{{median_seed_by_n_lib/*,n_covariance_warnings/*,"
               "n_exponent_at_bound/*,n_failed_resamples,ratio,ratio_ci/[],reason,verdict}",
               "WU-0002.4, .9, .11", "D-01, D-14, D-25(h)", "median fit, ratio and verdict"))
    # ---- H1b (v1 H1c) ----------------------------------------------------------------------
    h1b = f"{S}/H1b"
    add(_rules("unchanged", f"{h1b}/{{CP,PLP}}/slope", chain="network", interval="ci", item="R2",
               reason="slope unchanged (PLP only is the verdict)"))
    add(_rules("unchanged", f"{h1b}/{{CP,PLP}}/ci/[]", chain="network", level=CI_LEVEL, item="R2",
               reason="interval unchanged"))
    add(_rules("unchanged", f"{h1b}/threshold/[]", item=smoke, reason="band [0.8, 1.2]"))
    add(_rules("removed", f"{h1b}/{{CP,PLP}}/pass", "WU-0002.4", "D-02",
               "v3 H1b is decided on the PLP interval"))
    add(_rules("changed", f"{h1b}/pass", "WU-0002.4, .9", "D-02, D-14",
               "pass from the PLP interval"))
    add(_rules("new", f"{h1b}/{{CP,PLP}}/n_* {h1b}/{{n_excluded_nonfinite,n_states,reason,verdict}}",
               "WU-0002.4, .9, .11", "D-02, D-14, A4", "counts and verdict"))
    # ---- H1c (v1 H1d) ----------------------------------------------------------------------
    h1c = f"{S}/H1c"
    add(_rules("unchanged", f"{h1c}/{{CP,PLP}}/median_ratio", chain="network", interval="ci",
               item="R2", reason="median ratio unchanged"))
    add(_rules("unchanged", f"{h1c}/{{CP,PLP}}/ci/[]", chain="network", level=CI_LEVEL, item="R2",
               reason="interval unchanged"))
    add(_rules("unchanged", f"{h1c}/{{CP,PLP}}/n_states {h1c}/threshold/[] {h1c}/thresholds/[]",
               item=smoke, reason="state count and band unchanged"))
    add(_rules("removed", f"{h1c}/CP/pass", "WU-0002.9", "D-14, DEC-0016",
               "v3 H1c is decided on the PLP interval"))
    add(_rules("changed", f"{h1c}/{{pass,PLP/pass}}", "WU-0002.9", "D-14, DEC-0016 O3",
               "pass from the PLP interval"))
    add(_rules("new", f"{h1c}/{{CP,PLP}}/{{n_excluded_nonfinite,n_failed_resamples,"
               "n_ineligible_states} "
               f"{h1c}/PLP/{{reason,verdict}} {h1c}/{{n_failed_resamples,n_states,reason,verdict}}",
               "WU-0002.9, .11", "D-14, DEC-0016", "counts and verdict"))
    # ---- H1d (v1 H1e) ----------------------------------------------------------------------
    h1d = f"{S}/H1d"
    add(_rules("unchanged", f"{h1d}/rows/{{analog_seed,estimation_seed,growth,nhat}}/spearman "
               f"{h1d}/estimation_seed_vs_cramer_rao", chain="network", item="R2, D-03",
               reason="the point values moved under rows/<x>/spearman (WU-0002.5)"))
    add(_rules("unchanged", f"{h1d}/threshold", item=smoke, reason="threshold 0.7"))
    add(_rules("changed", f"{h1d}/pass", "WU-0002.5", "D-03", "N-hat leaves the pass"))
    add(_rules("new", f"{h1d}/rows/*/{{interval/[],n_excluded_nonfinite,n_failed_resamples,"
               "n_states,reason,verdict} "
               f"{h1d}/{{level,n_excluded_nonfinite,n_states,reason,verdict}}",
               "WU-0002.5, .9", "D-03, DEC-0016 O3", "intervals and verdicts are new"))
    # ---- Q-N (v1 H1f) ----------------------------------------------------------------------
    qn = f"{S}/Q-N"
    add(_rules("unchanged", f"{qn}/{{deployable,oracle}}/log_horizon/delta_r2", chain="network",
               interval="ci", item="R2", reason="log-horizon target unchanged (WU-0002.6)"))
    add(_rules("unchanged", f"{qn}/{{deployable,oracle}}/log_horizon/ci/[]", chain="network",
               level=CI_LEVEL, item="R2", reason="interval unchanged"))
    add(_rules("unchanged", f"{qn}/{{deployable,oracle}}/log_horizon/{{r2_four,r2_three}} "
               f"{qn}/{{deployable,oracle}}/noise_sens_r2_from_three", chain="network", item="R2",
               reason="log-horizon and noise-sensitivity R2 unchanged"))
    add(_rules("removed", f"{qn}/{{deployable,oracle}}/logit_w/{{delta_r2,r2_four,r2_three}} "
               f"{qn}/{{deployable,oracle}}/verdict {qn}/{{margin,pass}}", "WU-0002.6", "D-04, D-25(a)",
               "replaced by logit_w_interior and w_zero_indicator; reading by the v3 table"))
    add(_rules("removed", f"{qn}/{{deployable,oracle}}/logit_w/ci/[]", "WU-0002.6", "D-04, D-25(a)",
               "replaced by logit_w_interior and w_zero_indicator; reading by the v3 table",
               level=CI_LEVEL))
    add(_rules("changed", f"{qn}/threshold", "WU-0002.6", "D-04", "criterion text"))
    add(_rules("new", f"{qn}/{{deployable,oracle}}/{{logit_w_interior,w_zero_indicator}}/** "
               f"{qn}/{{deployable,oracle}}/log_horizon/{{n_failed_resamples,n_test,n_train}} "
               f"{qn}/{{n_test,n_w_one,n_w_zero,primary,role}}", "WU-0002.6", "D-04, D-25(a)",
               "two-part target and counts"))
    # ---- H2a --------------------------------------------------------------------------------
    h2a = f"{S}/H2a"
    add(_rules("unchanged", f"{h2a}/{{median_range_unrestricted,short_horizon_range_median}}",
               chain="network", item="R2", reason="unchanged (WU-0002.6 Log)"))
    add(_rules("changed", f"{h2a}/{{median_range,n_eligible_states,unconditional_spearman_w_lambda}}",
               "WU-0002.6", "D-25(a), D-25(b)",
               "initial-segment eligibility and unclipped w*; smoke: range -3%, one state fewer",
               chain="network"))
    add(_rules("changed", f"{h2a}/range_ci/[]", "WU-0002.6", "D-25(b)",
               "resample over all states with eligibility re-evaluated", level=PRIMARY_LEVEL))
    add(_rules("removed", f"{h2a}/partial_ci/[]", "WU-0002.6", "D-25(a)",
               "replaced by part_ii", level=PRIMARY_LEVEL))
    add(_rules("removed", f"{h2a}/partial_corr", "WU-0002.6", "D-25(a)", "replaced by part_ii"))
    add(_rules("changed", f"{h2a}/{{pass,threshold}}", "WU-0002.6, .9", "D-24, DEC-0016",
               "two-part criterion"))
    add(_rules("new", f"{h2a}/{{complete_case/**,controls,n_excluded_states,n_noncontiguous_states,"
               "n_w_one,n_w_zero,part_i_reason,part_i_verdict,part_ii/**,part_ii_verdict,"
               "range_by_span/**,range_n_failed_resamples,reason,verdict}", "WU-0002.6, .9, .11",
               "D-25(a), D-25(b)", "parts, counts and verdicts"))
    # ---- H2b --------------------------------------------------------------------------------
    h2b = f"{S}/H2b"
    add(_rules("unchanged", f"{h2b}/noise/{{mean_state_spearman,pass,monotone_medians}}",
               chain="network", interval="ci", item="R2", reason="H2b(i) values unchanged (WU-0002.9b)"))
    add(_rules("unchanged", f"{h2b}/noise/ci/[]", chain="network", level=PRIMARY_LEVEL, item="R2",
               reason="H2b(i) interval unchanged"))
    add(_rules("unchanged", f"{h2b}/noise/median_w_by_noise/*", chain="network", item="R2",
               reason="H2b(i) medians unchanged"))
    add(_rules("removed", f"{h2b}/library/*/ci/[]", "WU-0002.7", "D-05",
               "library part replaced by library_change and library_curves", level=PRIMARY_LEVEL))
    add(_rules("removed", f"{h2b}/library/*/{{mean_state_spearman,median_at_largest_n_lib,"
               "median_w_by_n_lib/*,monotone_medians,pass}", "WU-0002.7", "D-05",
               "library part replaced by library_change and library_curves"))
    add(_rules("changed", f"{h2b}/{{pass,threshold}}", "WU-0002.7", "D-05",
               "H2b(ii) is the mean paired change 10^3 to 10^4"))
    add(_rules("new", f"{h2b}/{{library_change/**,library_curves/**,library_change_reported/**,"
               "reason,verdict} "
               f"{h2b}/noise/{{n_constant_states,n_dropped_resamples,n_failed_resamples,reason,"
               "verdict}", "WU-0002.7, .9, .9b, .11", "D-05, DEF-0019", "H2b(ii), counts, verdicts"))
    # ---- H2c --------------------------------------------------------------------------------
    h2c = f"{S}/H2c"
    add(_rules("unchanged", f"{h2c}/A4_minus_A2/{{mean,relative,pass}}", chain="network",
               interval="ci", item="R2", reason="A4 - A2 unchanged"))
    add(_rules("unchanged", f"{h2c}/A4_minus_A2/ci/[]", chain="network", level=CI_LEVEL, item="R2",
               reason="A4 - A2 interval unchanged"))
    add(_rules("unchanged", f"{h2c}/A4_minus_A1/{{mean,relative,pass}}", chain="network",
               interval="ci", item="R2", reason="pilot best single was A1",
               when=(("H2c", "best_single"), "A1")))
    add(_rules("unchanged", f"{h2c}/A4_minus_A1/ci/[]", chain="network", level=CI_LEVEL, item="R2",
               reason="pilot best single was A1", when=(("H2c", "best_single"), "A1")))
    add(_rules("unchanged", f"{h2c}/pass", chain="network", item="R2",
               reason="both parts, with the pilot's best single A1",
               when=(("H2c", "best_single"), "A1")))
    add(_rules("changed", f"{h2c}/best_single", "WU-0002.8", "DEC-0008 A4(i), D-25(i)",
               "chosen on the calibration split, not on test", discrete=True))
    add(_rules("new", f"{h2c}/A4_minus_A0/** {h2c}/A4o_minus_A2/** {h2c}/calibration_mse/* "
               f"{h2c}/A4_minus_A2/{{n_failed_resamples,reason,verdict}} "
               f"{h2c}/{{n_failed_resamples,reason,verdict}}", "WU-0002.8, .9, .11",
               "DEC-0008 A4(i), D-20", "calibration choice, A4o - A2 and verdicts"))
    # ---- H2d --------------------------------------------------------------------------------
    h2d = f"{S}/H2d"
    add(_rules("unchanged", f"{h2d}/in_distribution_excess", chain="network", interval="ci",
               item="R2", reason="in-distribution excess unchanged"))
    add(_rules("unchanged", f"{h2d}/ci/[]", chain="network", level=CI_LEVEL, item="R2",
               reason="interval unchanged"))
    add(_rules("removed", f"{h2d}/{{shift_cells,shift_pass,shift_wins_A4_over_A3,"
               "in_distribution_pass}", "WU-0002.1, .8", "D-07", "part (ii) shift dropped"))
    add(_rules("changed", f"{h2d}/pass", "WU-0002.8, .9", "D-07, DEC-0016", "single-part criterion"))
    add(_rules("new", f"{h2d}/{{n_failed_resamples,reason,verdict}}", "WU-0002.9, .11", "D-14",
               "counts and verdict"))
    # ---- H2e (v3 noise matching; v1 H2e is the gain bound) ---------------------------------
    add(_rules("new", f"{S}/H2e/**", "WU-0002.7", "D-06", "noise-matching check (first time computable)"))
    # ---- gain bound (v1 H2e) ---------------------------------------------------------------
    gb = f"{S}/gain_bound"
    add(_rules("unchanged", f"{gb}/{{fraction_within_bound,max_gain_lyapunov,median_gain_lyapunov,"
               "n_states}", chain="network", item="R2", reason="gain-bound numbers unchanged"))
    add(_rules("removed", f"{gb}/{{pass,threshold}}", "WU-0002.9", "D-21(a)",
               "reported, no pass/fail bar"))
    add(_rules("new", f"{gb}/{{n_screened_out/*,n_total_states}}", "WU-0002.9", "D-21",
               "screen counts"))
    # ---- H3a --------------------------------------------------------------------------------
    h3a = f"{S}/H3a"
    add(_rules("changed", f"{h3a}/chosen_K", "WU-0002.3", "D-13", "K rule", discrete=True))
    add(_rules("changed", f"{h3a}/{{logrank_p_holm/[],iqr_lt_mean}}", "WU-0002.3, .8",
               "D-08, D-13", "regimes follow the new K (renamed from logrank_holm_p, "
               "mean_iqr_lyapunov)", chain="network"))
    add(_rules("changed", f"{h3a}/pass", "WU-0002.8", "D-08", "log-rank criterion only"))
    add(_rules("removed", f"{h3a}/{{iqr_pass,logrank_pass,regret_pass,regret_ratio}}", "WU-0002.8",
               "D-08", "log-rank criterion only"))
    add(_rules("new", f"{h3a}/{{iqr_lt/[],logrank_p_raw/[],n_degenerate_pairs,n_empty_regimes,"
               "n_km_not_reached,n_per_regime/[],pairs/[]/[],reason,threshold,verdict}",
               "WU-0002.8, .9, .11", "D-08, DEC-0008 A3", "log-rank detail, counts, verdict"))
    # ---- H3b (v1 H3c) -----------------------------------------------------------------------
    h3b = f"{S}/H3b"
    add(_rules("changed", f"{h3b}/{{horizon_tree_importance,weight_tree_importance}}/*", "WU-0002.8",
               "DEC-0008 A3, A4(e)", "trees have 8 leaves (v1: max(K, 4)); the pilot K was 5",
               chain="network"))
    add(_rules("changed", f"{h3b}/{{pass,threshold}}", "WU-0002.8, .9", "D-24, DEC-0008 A3",
               "tree and interval criterion"))
    add(_rules("new", f"{h3b}/{{D/**,degenerate_fits/**,max_leaf_nodes,n_resamples,n_states,"
               "nan_resamples,reason,stability,verdict,weight_lambda/**}", "WU-0002.8, .9, .11",
               "DEC-0008 A3, A4(e)", "bootstrap of the tree importances, counts, verdict"))
    # ---- H3c (v1 H3d) -----------------------------------------------------------------------
    h3c = f"{S}/H3c"
    add(_rules("changed", f"{h3c}/A5_over_A4_mse", "WU-0002.3", "D-13", "A5 follows the new K",
               chain="network"))
    add(_rules("changed", f"{h3c}/pass", "WU-0002.8", "D-10", "interval at 1 - 0.05/3"))
    add(_rules("unchanged", f"{h3c}/threshold", item=smoke, reason="bound 1.05"))
    add(_rules("new", f"{h3c}/{{ci/[],level,n_failed_resamples,n_states,reason,verdict}}",
               "WU-0002.8, .9, .11", "D-10", "interval, counts, verdict"))
    # ---- regime curve (moved from v1 H3b) -------------------------------------------------
    add(_rules("unchanged", f"{S}/regime_curve/realized_K/*", chain="network", discrete=True,
               item="R2", reason="trees do not change (moved from v1 H3b)"))
    add(_rules("changed", f"{S}/regime_curve/regret_ratio_by_K/*", "WU-0002.3", "D-11 (DEF-0002)",
               "exact excess replaces the clipped regret (moved from v1 H3b)", chain="network"))
    # ---- dropped v1 results ----------------------------------------------------------------
    add(_rules("removed", f"{S}/v1:H3b/{{loglog_slope,p_eff,pass,threshold}}", "WU-0002.8", "D-09",
               "v1 H3b (p_eff) is dropped"))
    add(_rules("removed", f"{S}/shift/**", "WU-0002.1", "D-17", "shift experiment removed"))
    add(_rules("removed", "transfer/**", "WU-0002.1", "D-17", "transfer stage (T1) removed"))
    add(_rules("unchanged", "robustness/<empty>", item="plumbing",
               reason="empty where the preset has no robustness systems (smoke); never at pilot"))
    # ---- verdicts ---------------------------------------------------------------------------
    hyp = "H1a,H1b,H1c,H1d,H2a,H2b,H2c,H2d,H3a,H3b,H3c,Q-N,gain_bound"
    add(_rules("changed", f"verdicts/{{{hyp}}}/{{by_system/*,verdict}}", "WU-0002.9",
               "D-14, DEC-0016", "verdicts are strings from intervals (supported, not supported, "
               "inconclusive)"))
    add(_rules("new", "verdicts/H2e/** verdicts/{" + hyp + "}/missing_systems/[]", "WU-0002.7, .9",
               "D-06, DEC-0016", "H2e verdict; systems not run"))
    add(_rules("removed", "verdicts/{V7,v1:H3b,v1:T1}/**", "WU-0002.2, .9", "D-14, D-17",
               "V7 is a validation check, v1 H3b and T1 are dropped"))
    # ---- robustness -------------------------------------------------------------------------
    var = r"re:(base|D=\d+|k=\d+|misspec=[\d.]+)"
    fin = r"re:Lambda_fin\(.*\)"
    rb = f"robustness/*/{var}"
    add(_rules("unchanged", f"{rb}/H1b/{{CP,PLP}}/slope", chain="network", interval="ci",
               item="R2", reason="robustness H1b (v1 H1c) unchanged; key renamed (D-16)"))
    add(_rules("unchanged", f"{rb}/H1b/{{CP,PLP}}/ci/[]", chain="network", level=CI_LEVEL,
               item="R2", reason="robustness H1b interval unchanged"))
    add(_rules("unchanged", f"{rb}/H1b/threshold/[]", item="R2", reason="band [0.8, 1.2]"))
    add(_rules("removed", f"{rb}/H1b/{{CP,PLP}}/pass", "WU-0002.4", "D-02", "PLP-only criterion"))
    add(_rules("changed", f"{rb}/H1b/pass", "WU-0002.4, .9", "D-02, D-14", "pass from the PLP interval"))
    add(_rules("new", f"{rb}/H1b/{{CP,PLP}}/n_* {rb}/H1b/{{n_excluded_nonfinite,n_states,reason,"
               "verdict}", "WU-0002.4, .11", "D-02", "counts and verdict"))
    add(_rules("unchanged", f"{rb}/{{A4_vs_A2_relative,A4_over_A3}}", chain="network", item="R2",
               reason="robustness summary unchanged"))
    add(_rules("unchanged", f"{rb}/mse_href/{{A0,A1,A2,A3,A4,A4o,A\\*}}", chain="network",
               item="R2", reason="robustness MSE at H_ref unchanged"))
    add(_rules("changed", f"{rb}/{{A5_regret_ratio,chosen_K}} {rb}/mse_href/A5", "WU-0002.3",
               "D-11 to D-13", "A5 follows the new K and exact excess", chain="network"))
    add(_rules("removed", f"{rb}/mse_href/A4f", "WU-0002.1", "D-17", "A4f removed"))
    add(_rules("changed", f"{rb}/H2a_median_range", "WU-0002.6", "D-25(b)",
               "initial-segment eligibility", chain="network"))
    add(_rules("removed", f"{rb}/H2a_partial_corr", "WU-0002.6", "D-25(a)",
               "replaced by the zero and interior parts"))
    add(_rules("new", f"{rb}/{{H2a_partial_corr_zero,H2a_partial_corr_interior}}", "WU-0002.6",
               "D-25(a)", "two-part partial correlation"))
    add(_rules("new", "robustness/*/*/error", "WU-0002.11", "A14",
               "a robustness variant failed (handling.failed_variants)", alert=True))
    fin_rb = f"robustness/*/{fin}"
    add(_rules("unchanged", f"{fin_rb}/{{corr_fin_vs_linear,scale_times_rho}}", chain="network",
               item="R2", reason="finite-amplitude growth agreement unchanged"))
    add(_rules("removed", f"{fin_rb}/H2a_partial_corr_fin", "WU-0002.6", "D-25(a)",
               "replaced by the zero and interior parts"))
    add(_rules("removed", f"{fin_rb}/ci/[]", "WU-0002.6", "D-25(a)",
               "replaced by the zero and interior parts", level=CI_LEVEL))
    add(_rules("new", f"{fin_rb}/{{H2a_partial_corr_zero_fin,H2a_partial_corr_interior_fin,"
               "ci_zero/[],ci_interior/[]}", "WU-0002.6", "D-25(a)", "two-part partial correlation"))
    add(_rules("removed", "robustness/*/delay%2F2/**", "WU-0002.1", "D-17",
               "delay/2 variant removed"))
    return R


RULES: list[Rule] = _build_rules()
TABLE = Table(RULES)


# ------------------------------------------------------------------------------ comparison
@dataclass
class LeafResult:
    """The outcome for one leaf path.

    Attributes
    ----------
    path : tuple[str, ...]
        The v3 path.
    rule : Rule
        The one rule that matched.
    old, new : object
        Values, or ``MISSING``.
    status : str
        ``equal``, ``equal_nan``, ``within_tol``, ``changed``, ``changed-old-only``,
        ``changed-new-only``, ``new``, ``removed``, ``timing``, ``skipped`` (an unchanged leaf whose
        condition is false), or a finding: ``FAIL-differs``, ``FAIL-type``, ``FAIL-missing-new``,
        ``FAIL-new-only``, ``FAIL-new-rule-old-present``, ``FAIL-removed-rule-new-present``,
        ``ALERT``.
    same : bool or None
        For ``changed`` leaves present on both sides: the values are equal (the rule allows a change).
    direction_ok : bool or None
        For rules with a ``direction``: the expected direction holds.
    """

    path: Path_
    rule: Rule
    old: object
    new: object
    status: str
    same: bool | None = None
    direction_ok: bool | None = None

    @property
    def is_finding(self) -> bool:
        """A finding in every branch: a presence that contradicts the class, or an alert."""
        return self.status in ("FAIL-new-rule-old-present", "FAIL-removed-rule-new-present",
                               "ALERT")

    @property
    def is_value_finding(self) -> bool:
        """An ``unchanged`` leaf that differs, or a violated direction (bitwise branch only)."""
        return self.status in VALUE_FINDINGS or self.direction_ok is False


VALUE_FINDINGS = ("FAIL-differs", "FAIL-type", "FAIL-missing-new", "FAIL-new-only")


def _condition_holds(rule: Rule, path: Path_, new: dict[Path_, object]) -> bool:
    rel, expected = rule.when
    return new.get((*path[:2], *rel), MISSING) == expected


def _direction_ok(direction: str, old: object, new: object) -> bool | None:
    if not direction or not all(isinstance(v, float) for v in (old, new)):
        return None if not direction else False
    if direction == "zero":
        return struct.pack("<d", new) == struct.pack("<d", 0.0)  # type: ignore[arg-type]
    scale = max(abs(old), abs(new))  # type: ignore[type-var]
    return bool(new - old >= -1e-12 * scale)  # type: ignore[operator]


def judge(path: Path_, rule: Rule, old: object, new: object,
          new_leaves: dict[Path_, object]) -> LeafResult:
    """Decide the outcome of one leaf under its rule (see ``LeafResult.status``)."""
    both = old is not MISSING and new is not MISSING
    if rule.cls == "timing":
        return LeafResult(path, rule, old, new, "timing")
    if rule.cls == "unchanged":
        if new is MISSING:
            if rule.when and not _condition_holds(rule, path, new_leaves):
                return LeafResult(path, rule, old, new, "skipped")
            return LeafResult(path, rule, old, new, "FAIL-missing-new")
        if old is MISSING:
            return LeafResult(path, rule, old, new, "FAIL-new-only")
        outcome = values_equal(old, new, rule.rel_tol)
        status = outcome if outcome in ("equal", "equal_nan", "within_tol") else f"FAIL-{outcome}"
        return LeafResult(path, rule, old, new, status)
    if rule.cls == "changed":
        if not both:
            return LeafResult(path, rule, old, new,
                              "changed-old-only" if new is MISSING else "changed-new-only")
        same = values_equal(old, new) in ("equal", "equal_nan")
        return LeafResult(path, rule, old, new, "changed", same,
                          _direction_ok(rule.direction, old, new))
    if rule.cls == "new":
        if old is not MISSING:
            return LeafResult(path, rule, old, new, "FAIL-new-rule-old-present")
        return LeafResult(path, rule, old, new, "ALERT" if rule.alert else "new")
    if new is not MISSING:  # removed
        return LeafResult(path, rule, old, new, "FAIL-removed-rule-new-present")
    return LeafResult(path, rule, old, new, "removed")


def compare_leaves(old: dict[Path_, object], new: dict[Path_, object],
                   table: Table = TABLE) -> list[LeafResult]:
    """Classify and judge every leaf of the two sides.

    Parameters
    ----------
    old : dict
        v1 leaves already under the v3 names (``transform_v1`` applied).
    new : dict
        Leaves of the new run, without ``provenance``.
    table : Table
        The rule table.

    Returns
    -------
    list[LeafResult]
        One result per path of either side, sorted by path.

    Raises
    ------
    Unclassified
        Naming every leaf with no rule or with several rules.
    """
    paths = sorted(set(old) | set(new))
    rules: dict[Path_, Rule] = {}
    bad: list[str] = []
    for path in paths:
        found = table.matches(path)
        if len(found) == 1:
            rules[path] = found[0]
        else:
            bad.append(table.explain(path, found))
    if bad:
        shown = bad[:200]
        extra = f" (and {len(bad) - 200} more)" if len(bad) > 200 else ""
        raise Unclassified(f"{len(bad)} leaves without exactly one rule{extra}:\n  "
                           + "\n  ".join(shown))
    return [judge(p, rules[p], old.get(p, MISSING), new.get(p, MISSING), new) for p in paths]


def load_sides(old_tree: object, new_tree: object) -> tuple[dict, dict, int]:
    """Flatten both trees, transform the v1 paths and drop the new side's provenance.

    Returns
    -------
    tuple
        ``(old_leaves, new_leaves, n_provenance)``.

    Raises
    ------
    ToolError
        If two v1 paths map to one v3 path, or the old side has a ``provenance``.
    """
    old: dict[Path_, object] = {}
    for path, value in flatten(old_tree).items():
        moved = transform_v1(path)
        if moved in old:
            raise ToolError(f"two v1 leaves map to {show(moved)}")
        old[moved] = value
    if any(p[0] == "provenance" for p in old):
        raise ToolError("the v1 side has a provenance block: not expected")
    flat_new = flatten(new_tree)
    new = {p: v for p, v in flat_new.items() if p[0] != "provenance"}
    return old, new, len(flat_new) - len(new)


# ------------------------------------------------------------------------------ switch, fallback, gates
def context_switch(old: dict[Path_, object], new: dict[Path_, object]) -> tuple[str, list[str]]:
    """Apply the switch rule of ROADMAP WU-0002.12 to the ``context`` leaves.

    A float that differs by more than 1e-12 relative, or any other leaf that differs in type or
    value, or a leaf missing from the new run, selects the fallback branch.

    Returns
    -------
    tuple[str, list[str]]
        ``("bitwise" | "fallback", reasons)``.
    """
    reasons = []
    for path in sorted(p for p in old if p[0] == "systems" and len(p) == 4 and p[2] == "context"):
        a, b = old[path], new.get(path, MISSING)
        if b is MISSING:
            reasons.append(f"{show(path)} missing from the new run")
        elif values_equal(a, b, SWITCH_REL_TOL) not in ("equal", "equal_nan", "within_tol"):
            reasons.append(f"{show(path)}: {a!r} -> {b!r}")
    return ("fallback" if reasons else "bitwise"), reasons


@dataclass
class FallbackReport:
    """Result of the fallback criterion F1 to F5 (the owner's text; constants from a DEC)."""

    f1: list[tuple]
    f2: list[tuple]
    f3: list[tuple]
    f4: list[tuple]
    f5: list[tuple]

    @property
    def passed(self) -> bool:
        """All of F1, F2, F3, F4, F5 hold ('reported' rows in F3 carry no pass/fail)."""
        return (all(r[-1] for r in self.f1) and all(r[-1] for r in self.f2)
                and all(r[6] for r in self.f3 if r[6] is not None)
                and all(r[-1] for r in self.f4) and not self.f5)


def evaluate_fallback(results: list[LeafResult], old: dict[Path_, object],
                      new: dict[Path_, object], table: Table,
                      constants: dict | None) -> FallbackReport:
    """Evaluate the fallback criterion.

    Parameters
    ----------
    results : list[LeafResult]
        Output of ``compare_leaves``.
    old, new : dict
        The two leaf dicts.
    table : Table
        The rule table (for the level of an interval leaf).
    constants : dict or None
        ``{"dec": str, "k": float, "se": {system: float}}``.

    Returns
    -------
    FallbackReport
        F1: integer context leaves identical. F2: ``|lambda_new - lambda_pilot| <= k * SE`` (closed).
        F3: each unchanged statistic with a pilot interval lies in it (closed); other differing
        floats are reported with their relative difference (no pass/fail). F4: the gate flags.
        F5: discrete unchanged leaves that flipped.

    Raises
    ------
    ToolError
        If ``constants`` is ``None`` or lacks a system's SE.
    """
    if constants is None:
        raise ToolError("the fallback constants are not recorded")
    f1, f2, f3, f4, f5 = [], [], [], [], []
    for path, value in sorted(old.items()):
        if path[0] == "systems" and len(path) == 4 and path[2] == "context":
            if type(value) is int:
                got = new.get(path, MISSING)
                f1.append((show(path), value, got, got == value and type(got) is int))
            if path[3] == "lambda_max":
                got = new.get(path, MISSING)
                if path[1] not in constants["se"]:
                    raise ToolError(f"no SE for {path[1]} in the fallback constants")
                tol = constants["k"] * constants["se"][path[1]]
                delta = abs(got - value) if isinstance(got, float) else math.inf
                f2.append((path[1], value, got, delta, tol, delta <= tol))
    for res in results:
        if res.rule.cls != "unchanged" or res.old is MISSING or res.new is MISSING:
            continue
        if res.rule.discrete and res.status.startswith("FAIL"):
            f5.append((show(res.path), res.old, res.new))
        if not (isinstance(res.old, float) and isinstance(res.new, float)):
            continue
        if res.rule.interval:
            parent = res.path[:-1]
            lo, hi = (old.get((*parent, res.rule.interval, f"[{i}]"), MISSING) for i in (0, 1))
            if lo is not MISSING and hi is not MISSING:
                level = table.classify((*parent, res.rule.interval, "[0]")).level
                f3.append((show(res.path), res.old, res.new, lo, hi, level,
                           bool(lo <= res.new <= hi)))  # type: ignore[operator]
                continue
        if res.status.startswith("FAIL"):
            scale = max(abs(res.old), abs(res.new))
            rel = abs(res.new - res.old) / scale if scale else math.inf
            f3.append((show(res.path), res.old, res.new, None, None, None, None, rel))
    for path, value in sorted(new.items()):
        if path[0] == "systems" and len(path) == 5 and path[2:4] == ("validation", "gate"):
            f4.append((show(path), value, value is True))
    return FallbackReport(f1, f2, f3, f4, f5)


def gate_rows(new: dict[Path_, object]) -> list[tuple[str, str, object, bool]]:
    """R4 (the gate flags) and R5 (P2(c) counters) of every system of the new run.

    Returns
    -------
    list[tuple]
        ``(check, path, value, ok)``. A missing leaf is ``ok = False`` with value ``MISSING``.
    """
    systems = sorted({p[1] for p in new if p[0] == "systems" and len(p) > 2})
    wanted = [("R4", ("validation", "gate", k), lambda v: v is True)
              for k in ("V1", "V2", "V4", "V5", "V6", "V7", "gate_pass")]
    wanted += [("R5", ("verification", "P2c", "n_violations"), lambda v: v == 0 and type(v) is int)]
    wanted += [("R5", ("verification", "P2c", "n_chain_violations", k),
                lambda v: v == 0 and type(v) is int)
               for k in ("A_le_B", "N_le_A", "consistency", "p2a", "triangle")]
    rows = []
    for system in systems:
        for check, rel, test in wanted:
            path = ("systems", system, *rel)
            value = new.get(path, MISSING)
            rows.append((check, show(path), value, value is not MISSING and bool(test(value))))
    return rows


# ------------------------------------------------------------------------------ report
def fmt(value: object) -> str:
    """Text of a leaf value in a report cell (floats and ints by ``repr``)."""
    if value is MISSING:
        return "(absent)"
    return repr(value)


def cell(text: object) -> str:
    """Escape a value for a Markdown table cell."""
    return str(text).replace("|", "\\|").replace("\n", " ")


def row(*cells: object) -> str:
    """One Markdown table row."""
    return "| " + " | ".join(cell(c) for c in cells) + " |"


def table_lines(header: tuple[str, ...], rows: list[tuple]) -> list[str]:
    """A Markdown table, or the line ``none`` when there are no rows."""
    if not rows:
        return ["none", ""]
    return [row(*header), row(*("---" for _ in header)), *(row(*r) for r in rows), ""]


def _max_abs_diff(group: list[LeafResult]) -> str:
    """Largest |new - old| over the finite float pairs; the pairs left out are counted."""
    pairs = [(r.old, r.new) for r in group if isinstance(r.old, float) and isinstance(r.new, float)]
    finite = [abs(b - a) for a, b in pairs if math.isfinite(a) and math.isfinite(b)]
    text = repr(max(finite)) if finite else ""
    left_out = len(pairs) - len(finite)
    return text + (f" ({left_out} non-finite pairs not in the maximum)" if left_out else "")


# Things to look at: read, with no criterion (plan "Things to look at"). Predicates over the path.
LOOK_AT: list[tuple[str, object]] = [
    ("H2e and zero variance (per cell and rho)",
     lambda p: p[0] == "systems" and len(p) > 3 and p[2] == "H2e"),
    ("Handling counts by system (clips, replacements, floors, zero variance, fallbacks, nu cap)",
     lambda p: p[:2] == ("handling", "by_system")),
    ("Failed robustness variants", lambda p: p[:2] == ("handling", "failed_variants")),
    ("w* at 0 and at 1 (H2a, Q-N)",
     lambda p: p[0] == "systems" and len(p) == 4 and p[3] in ("n_w_zero", "n_w_one")
     and p[2] in ("H2a", "Q-N")),
    ("H2b: constant states and zero differences",
     lambda p: p[0] == "systems" and ((len(p) == 5 and p[2:4] == ("H2b", "noise")
                                       and p[4] == "n_constant_states")
                                      or p[2:4] == ("H2b", "library_change")
                                      and p[-1] in ("n_zero_difference", "n_failed_resamples"))),
    ("H3a: regimes and log-rank",
     lambda p: p[0] == "systems" and p[2] == "H3a" and p[3] in (
         "n_per_regime", "n_empty_regimes", "n_degenerate_pairs", "n_km_not_reached",
         "logrank_p_raw", "logrank_p_holm", "chosen_K")),
    ("H3b: degenerate fits, stability, NaN resamples",
     lambda p: p[0] == "systems" and p[2] == "H3b" and p[3] in (
         "degenerate_fits", "stability", "nan_resamples", "n_resamples")),
    ("Choices (K per system, H2c best single)",
     lambda p: p[0] == "systems" and ((p[2:4] == ("fitted", "chosen_K") and len(p) == 4)
                                      or p[2:4] == ("H2c", "best_single"))),
    ("Sentinels (V7 replacements, exponent at bound, floors)",
     lambda p: p[0] == "systems" and (p[2:4] == ("V7", "invariant_mean_replacements")
                                      or "n_exponent_at_bound" in p or p[-1] == "n_floored")),
    ("Failed and dropped resamples",
     lambda p: p[0] == "systems" and p[-1] in ("n_failed_resamples", "n_dropped_resamples")),
]


@dataclass
class Comparison:
    """Everything the report and the exit code need."""

    results: list[LeafResult]
    old: dict[Path_, object]
    new: dict[Path_, object]
    n_provenance: int
    branch: str
    switch_reasons: list[str]
    gates: list[tuple]
    fallback: FallbackReport | None
    fallback_missing: bool
    info: dict

    def findings(self) -> list[LeafResult]:
        """Leaves that make the run fail under the selected branch."""
        out = [r for r in self.results if r.is_finding]
        if self.branch == "bitwise":
            out += [r for r in self.results if r.is_value_finding]
        return out

    def exit_code(self) -> int:
        """0, 1 or 3 (the fallback branch applies without constants)."""
        if self.fallback_missing:
            return EXIT_FALLBACK
        failed = bool(self.findings()) or any(not g[3] for g in self.gates)
        if self.branch == "fallback" and self.fallback is not None and not self.fallback.passed:
            failed = True
        return EXIT_FINDINGS if failed else 0


def render_report(cmp: Comparison) -> str:
    """The Markdown report of a comparison (first line: the DEVELOPMENT label)."""
    info = cmp.info
    note = ("Generated by `tools/compare_pilot.py`; do not edit. A difference between a DEV-0 run "
            "and the pilot is a regression finding for the development of the code, not evidence "
            "about any hypothesis.")
    out = [LABEL, "", "# DEV-0 regression against the v1 pilot (WU-0002.12)", "", note, "",
           "## Provenance", ""]
    for key in ("commit", "dirty", "run_dir", "sha256_old", "sha256_new", "manifest_row",
                "lpc_threads", "nproc"):
        out.append(f"- {key.replace('_', ' ')}: {info.get(key, 'n/a')}")
    out.append(f"- provenance leaves excluded from the new run: {cmp.n_provenance}")
    out += ["", "## Branch", ""]
    out.append(f"- branch: {cmp.branch}")
    if cmp.switch_reasons:
        out += [f"- switch rule fired by: {cell(r)}" for r in cmp.switch_reasons]
    else:
        out.append("- switch rule: every context leaf equals the pilot's (floats within 1e-12 "
                   "relative)")
    out += ["", "## Counts", ""]
    by_class: dict[str, Counter] = defaultdict(Counter)
    for r in cmp.results:
        by_class[r.rule.cls][r.status] += 1
    out += table_lines(("group", "leaves", "outcomes"),
                       [(c, sum(by_class[c].values()),
                         ", ".join(f"{s}: {n}" for s, n in sorted(by_class[c].items())))
                        for c in CLASSES if by_class[c]])
    nan_equal = sum(1 for r in cmp.results if r.status == "equal_nan")
    out.append(f"NaN equal to NaN (counted): {nan_equal}")
    out.append("")

    out += ["## Findings", ""]
    out.append("Value findings (an unchanged leaf that differs, or a violated direction) fail the "
               "run under the bitwise branch only; the other findings fail it under both.")
    out.append("")
    found = [r for r in cmp.results if r.is_finding or r.is_value_finding]
    rows = [(("direction violated" if r.direction_ok is False else r.status),
             show(r.path), fmt(r.old), fmt(r.new), r.rule.pattern, r.rule.sub)
            for r in found if not r.rule.bulk]
    packed: dict[tuple[str, str], list[LeafResult]] = defaultdict(list)
    for r in found:
        if r.rule.bulk:
            packed[(r.status, r.rule.pattern)].append(r)
    rows += [(status, f"{len(g)} leaves, first {show(g[0].path)}", fmt(g[0].old), fmt(g[0].new),
              pattern, g[0].rule.sub) for (status, pattern), g in packed.items()]
    out += table_lines(("status", "path", "v1 pilot", "new", "rule", "sub-task"), rows)

    out += ["## Changed statistics", ""]
    changed = [r for r in cmp.results if r.rule.cls == "changed"]
    single = [r for r in changed if not r.rule.bulk]
    out += table_lines(("path", "v1 pilot", "new", "sub-task", "item", "reason", "direction"),
                       [(show(r.path), fmt(r.old), fmt(r.new), r.rule.sub, r.rule.item,
                         r.rule.reason + (" (value equal)" if r.same else ""),
                         "" if not r.rule.direction else
                         (f"{r.rule.direction}: " + ("ok" if r.direction_ok else "VIOLATED")))
                        for r in single])
    bulk: dict[str, list[LeafResult]] = defaultdict(list)
    for r in changed:
        if r.rule.bulk:
            bulk[r.rule.pattern].append(r)
    out += ["Arrays and curves, summarized (all values in the per-leaf JSON):", ""]
    out += table_lines(("rule", "leaves", "equal", "max abs diff", "sub-task", "item"),
                       [(pat, len(g), sum(1 for r in g if r.same), _max_abs_diff(g),
                         g[0].rule.sub, g[0].rule.item) for pat, g in bulk.items()])

    out += ["## Removed groups (counted per rule)", ""]
    groups: dict[str, list[LeafResult]] = defaultdict(list)
    for r in cmp.results:
        if r.rule.cls == "removed":
            groups[r.rule.pattern].append(r)
    out += table_lines(("rule", "leaves", "sub-task", "item", "reason"),
                       [(pat, len(g), g[0].rule.sub, g[0].rule.item, g[0].rule.reason)
                        for pat, g in groups.items()])

    out += ["## New checks (counted per rule)", ""]
    groups = defaultdict(list)
    for r in cmp.results:
        if r.rule.cls == "new":
            groups[r.rule.pattern].append(r)
    out += table_lines(("rule", "leaves", "sub-task", "item", "reason"),
                       [(pat, len(g), g[0].rule.sub, g[0].rule.item, g[0].rule.reason)
                        for pat, g in groups.items()])
    out += ["New verdicts:", ""]
    out += table_lines(("path", "value"),
                       [(show(r.path), fmt(r.new)) for r in cmp.results
                        if r.rule.cls == "new" and r.path[-1] == "verdict"])

    out += ["## Gate and P2(c)", ""]
    out += table_lines(("check", "path", "value", "ok"),
                       [(c, p, fmt(v), "yes" if ok else "NO") for c, p, v, ok in cmp.gates])

    if cmp.branch == "fallback":
        out += ["## Fallback criterion", ""]
        if cmp.fallback_missing or cmp.fallback is None:
            refused = ("REFUSED: the fallback constants are not recorded (the owner's decision, "
                       "LPC.AI.12; ROADMAP WU-0002.12). Exit 3.")
            out += [refused, ""]
        else:
            fb = cmp.fallback
            out += ["F1 (integer context identical):", ""]
            out += table_lines(("path", "v1 pilot", "new", "ok"),
                               [(a, fmt(b), fmt(c), "yes" if d else "NO") for a, b, c, d in fb.f1])
            out += ["F2 (|lambda new - lambda pilot| <= k SE):", ""]
            out += table_lines(("system", "v1 pilot", "new", "delta", "k SE", "ok"),
                               [(a, fmt(b), fmt(c), fmt(d), fmt(e), "yes" if f else "NO")
                                for a, b, c, d, e, f in fb.f2])
            out += ["F3 (unchanged statistics inside the pilot interval, closed; others reported):",
                    ""]
            out += table_lines(("path", "v1 pilot", "new", "lower", "upper", "level", "result"),
                               [(r[0], fmt(r[1]), fmt(r[2]), fmt(r[3]), fmt(r[4]), fmt(r[5]),
                                 ("inside" if r[6] else "OUTSIDE") if r[6] is not None
                                 else f"reported, relative difference {r[7]!r}") for r in fb.f3])
            out += ["F4 (gate flags):", ""]
            out += table_lines(("path", "value", "ok"),
                               [(a, fmt(b), "yes" if c else "NO") for a, b, c in fb.f4])
            out += ["F5 (discrete unchanged leaves that flipped):", ""]
            out += table_lines(("path", "v1 pilot", "new"),
                               [(a, fmt(b), fmt(c)) for a, b, c in fb.f5])

    out += ["## Things to look at (read, no criterion)", ""]
    for title, predicate in LOOK_AT:
        rows = [(show(p), fmt(v)) for p, v in sorted(cmp.new.items())
                if predicate(p)]  # type: ignore[operator]
        out += [f"### {title}", ""]
        out += table_lines(("path", "value"), rows)

    out += ["## Wall-clock (not compared)", ""]
    out += table_lines(("path", "v1 pilot [s]", "new [s]", "new / v1"),
                       [(show(r.path), fmt(r.old), fmt(r.new),
                         repr(r.new / r.old) if isinstance(r.old, float) and isinstance(r.new, float)
                         and r.old else "")
                        for r in cmp.results if r.rule.cls == "timing"
                        and r.old is not MISSING and r.new is not MISSING])
    return "\n".join(out) + "\n"


def leaves_json(cmp: Comparison) -> list[dict]:
    """The per-leaf table written next to the report."""
    return [{"path": show(r.path), "group": r.rule.cls, "status": r.status, "old": _json(r.old),
             "new": _json(r.new), "sub_task": r.rule.sub, "item": r.rule.item,
             "rule": r.rule.pattern, "same": r.same, "direction_ok": r.direction_ok}
            for r in cmp.results]


def _json(value: object) -> object:
    return None if value is MISSING else value


# ------------------------------------------------------------------------------ command line
def sha256_of(path: Path) -> str:
    """SHA-256 of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def provenance_info(new_tree: object, old_path: Path, new_path: Path, run_dir: str,
                    manifest_row: str) -> dict:
    """Provenance fields of the report (from the new run's own ``provenance`` block)."""
    prov = new_tree.get("provenance", {}) if isinstance(new_tree, dict) else {}
    env = prov.get("env", {}) if isinstance(prov, dict) else {}
    try:
        affinity = len(os.sched_getaffinity(0))
    except AttributeError:
        affinity = "n/a"
    return {"commit": prov.get("commit", "n/a"), "dirty": prov.get("dirty", "n/a"),
            "run_dir": run_dir, "sha256_old": sha256_of(old_path),
            "sha256_new": sha256_of(new_path), "manifest_row": manifest_row,
            "lpc_threads": f"{env.get('LPC_THREADS', 'n/a')} (run); nproc {env.get('NPROC', 'n/a')} "
                           "(run env)",
            "nproc": f"{os.cpu_count()} cpus, affinity {affinity} (this process)"}


def compare_files(new_path: Path, old_path: Path, run_dir: str, manifest_row: str,
                  constants: dict | None = None, table: Table = TABLE) -> Comparison:
    """Run the whole comparison for two files.

    Raises
    ------
    ToolError
        On unreadable input; ``Unclassified`` (a ``ToolError``) on a leaf without exactly one rule.
    """
    try:
        old_tree = json.loads(old_path.read_text())
        new_tree = json.loads(new_path.read_text())
    except (OSError, ValueError) as exc:
        raise ToolError(f"cannot read input: {exc}") from exc
    old, new, n_prov = load_sides(old_tree, new_tree)
    results = compare_leaves(old, new, table)
    branch, reasons = context_switch(old, new)
    fallback, missing = None, False
    if branch == "fallback":
        if constants is None:
            missing = True
        else:
            fallback = evaluate_fallback(results, old, new, table, constants)
    return Comparison(results, old, new, n_prov, branch, reasons, gate_rows(new), fallback, missing,
                      provenance_info(new_tree, old_path, new_path, run_dir, manifest_row))


def main(argv: list[str] | None = None) -> int:
    """Command-line entry; returns the exit code."""
    root = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("new", type=Path, help="results.json of the DEV-0 pilot run")
    ap.add_argument("--old", type=Path, default=root / "docs/study/pilot_results_v1.json")
    ap.add_argument("--report", type=Path, default=root / "docs/study/dev_regression_dev0.md")
    ap.add_argument("--leaves-json", type=Path,
                    default=root / "runs/dev/wu0002-12/compare_leaves.json")
    ap.add_argument("--run-dir", default=None, help="run directory to print (default: the dir of NEW)")
    ap.add_argument("--manifest-row", default="Pilot v1 (docs/agent/records/results-manifest.md)")
    args = ap.parse_args(argv)
    run_dir = args.run_dir or str(args.new.resolve().parent)
    try:
        cmp = compare_files(args.new, args.old, run_dir, args.manifest_row, FALLBACK_CONSTANTS)
    except ToolError as exc:
        print(f"compare_pilot: error: {exc}", file=sys.stderr)
        return EXIT_ERROR
    for path in (args.report, args.leaves_json):
        path.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(render_report(cmp))
    args.leaves_json.write_text(json.dumps(leaves_json(cmp), indent=1))
    code = cmp.exit_code()
    counts = Counter(r.rule.cls for r in cmp.results)
    print(f"compare_pilot: branch {cmp.branch}; "
          + ", ".join(f"{c} {counts[c]}" for c in CLASSES)
          + f"; findings {len(cmp.findings())}; gate failures {sum(1 for g in cmp.gates if not g[3])}"
          + f"; report {args.report}; exit {code}")
    if cmp.fallback_missing:
        print("compare_pilot: the switch rule selected the fallback branch, but the fallback "
              "constants (k, SE per system) are not recorded: the owner's DEC is missing "
              "(LPC.AI.12). Reasons: " + "; ".join(cmp.switch_reasons), file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
