#!/usr/bin/env python3
"""Regression of a DEV-0 pilot run against the v1 pilot (WU-0002.12, step 1: the comparison tool).

Usage::

    python3 -I tools/compare_pilot.py NEW_RESULTS_JSON [--old docs/study/pilot_results_v1.json]
        [--report docs/study/dev_regression_dev0.md]
        [--leaves-json runs/dev/wu0002-12/compare_leaves.json]
        [--run-dir DIR] [--manifest-row TEXT]
        [--reference LOCAL_V1_RESULTS_JSON | --no-reference]
        [--cache-file PATH] [--cache-preexisted yes|no]

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

Branch (the approved criterion, DEC-0019; the text is in the WU-0002.12 unit file, "final text for
the owner"). **D** if any ``context`` leaf differs, except that ``obs_scale`` may differ within 1e-12
relative (``lambda_max`` and ``interval`` bitwise, every integer leaf identical). Else **B** if every
``unchanged`` leaf is bitwise equal (R3: regret(v3) >= regret(v1) (1 - 1e-12), A* exactly 0.0), else
**N**: N1 the network-independent chains (tagged ``dynamics``, ``cp``, ``oracle``, ``fixture`` in the
rule table) are bitwise equal; N2 every other continuous unchanged leaf is within 1e-6 relative or
meets N3; N3 a chain-head event (a differing discrete quantity or integer count, or a ``fitted``
coefficient beyond 1e-6) lies upstream in its system and chain, and a leaf with a pilot interval moves
by at most 0.2 SE_arm (z = 1.960 at 95%, 2.394 at 1 - 0.05/3); N4 the gate and the V7 rule (n_nonfinite
0, median slope and median efficiency at every rho in [0.9, 1.1], closed); N5 regret(v3) >=
regret(v1) (1 - 1e-6) and A* regret 0.0 (a violation under a non-zero ``curvature_floor`` is
attributed to that sentinel). A divergence-locus table is always written. In branch D, D1 (with
``--reference``, the v1 code run locally): the new run against the reference by B then N, and D2
(|lambda_ref - lambda_pilot| <= 5 SE, closed, per system); D3 (``--no-reference``): D2 for the new
run, N4, and the interval band with z_B = Phi^-1(1 - 0.05 / (2 m)). Every branch checks the gate and
P2(c) (R4, R5), and the cache: ``lyapunov.json`` pre-existing is a finding.

Platform (WU-0001.6, DEF-0024; information only). The report has a "Platform" section: one row per
side (the new run, the old run and, with ``--reference``, the reference run) with the CPU model, the
OpenBLAS corenames and ``OPENBLAS_CORETYPE`` of that side's ``provenance`` block, or "not recorded".
When both sides of a pair are recorded and the model or a corename differs, an information line says
that cross-host differences in the cp, oracle and fixture chains are expected. No status, branch or
exit code depends on it. The four ``context`` digests of the new run (``state_mean_digest``,
``cov_digest``, ``whiten_digest``, ``unwhiten_digest``) are ``new`` leaves; the branch rule does not
read them (a v3-against-v3 comparison needs an owner ruling first, follow-up F1 of WU-0001.6).
The four orbit-guard leaves of each system (``context/lyapunov_orbit_max_abs`` and
``context/trajectory_max_abs/{statistics,main,estimator}``, WU-0002.11c, DEF-0015) are ``new`` leaves
too, and the branch rule does not read them.

Outputs. ``--report`` (default ``docs/study/dev_regression_dev0.md``), whose first line is
``DEVELOPMENT (DEV-0): not a hypothesis test``, and a per-leaf JSON file (default
``runs/dev/wu0002-12/compare_leaves.json``, untracked). The tool reads statistics and computes
none. It imports nothing but the standard library, and no ``lpcstudy`` module.

Exit codes: 0 no failure; 1 failures (the report lists them); 2 a leaf without exactly one rule, or
unreadable input, or a usage error; 3 branch D without ``--reference`` or ``--no-reference``.
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
from datetime import datetime
from pathlib import Path
from statistics import NormalDist

LABEL = "DEVELOPMENT (DEV-0): not a hypothesis test"
EXIT_FINDINGS, EXIT_ERROR, EXIT_NEEDS_INPUT = 1, 2, 3
SWITCH_REL_TOL = 1e-12   # obs_scale in the branch selection (DEC-0019)
R3_REL_TOL = 1e-12       # branch B: regret(v3) >= regret(v1) * (1 - 1e-12)
N5_REL_TOL = 1e-6        # branch N: regret(v3) >= regret(v1) * (1 - 1e-6)
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

# The approved criterion (DEC-0019; text in the WU-0002.12 unit file, 'final text for the owner'):
# N2 relative bound, N3 fraction of SE_arm, z of the two interval levels (1.960 at 95%,
# 2.394 at 1 - 0.05/3), D2 with k = 5 and the WU-0007 Benettin standard errors per system.
FALLBACK_CONSTANTS: dict = {
    "dec": "DEC-0019", "n2_rel": 1e-6, "n3_fraction": 0.2,
    "z": {CI_LEVEL: 1.960, PRIMARY_LEVEL: 2.394},
    "k": 5.0, "se": {"lorenz63": 0.0012, "rossler": 0.00055, "chua": 0.0048},
}

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
    # The delay/2 variant of v1 has a key whose delay differs from the system's own ``delay``; those
    # keys are renamed with the prefix ``delay2-variant:`` by ``mark_delay_variants`` (a system whose
    # own delay is 2 keeps its core estimators).
    kept = r"re:\('(lorenz63|rossler|chua)',\s(?:\d+|core),\s(?:\d+|core),\s[\d.]+\)"
    gone96 = r"re:\('lorenz96',.*"
    gone2 = r"re:delay2-variant:.*"
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
    add(_rules("new", f"{S}/context/{{state_mean_digest,cov_digest,whiten_digest,unwhiten_digest}}",
               "WU-0001.6", "DEF-0024", "platform record: SHA-256 of the whitening chain"))
    add(_rules("new", f"{S}/context/lyapunov_orbit_max_abs "
               f"{S}/context/trajectory_max_abs/{{statistics,main,estimator}}",
               "WU-0002.11c", "DEF-0015", "orbit guard: max |x| of the Benettin orbit and of the "
               "three trajectories (diagnostics)", chain="dynamics"))
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
               chain="network", item="R2",
               reason=("both proxies are fitted on the estimated nu (analog_f = distance * "
                       "min(nu_hat, nu_cap), allocation.py:123): network chain, so the plan's "
                       "CP-chain remark does not hold for this leaf")))
    add(_rules("unchanged", f"{S}/fitted/nu_cap", chain="network", item="R2",
               reason="the nu cap is unchanged"))
    add(_rules("changed", f"{S}/fitted/chosen_K", "WU-0002.3", "D-13 (DEF-0003)",
               "K rule on the calibration excess MSE; the pilot K was the fallback 5",
               discrete=True, chain="network"))
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
    add(_rules("unchanged", f"{h1b}/PLP/slope", chain="network", interval="ci", item="R2",
               reason="slope unchanged (PLP only is the verdict)"))
    add(_rules("unchanged", f"{h1b}/PLP/ci/[]", chain="network", level=CI_LEVEL, item="R2",
               reason="interval unchanged"))
    add(_rules("unchanged", f"{h1b}/CP/slope", chain="cp", interval="ci", item="R2",
               reason="CP slope uses analog_seed, sq_cp and the oracle gains only (CP chain)"))
    add(_rules("unchanged", f"{h1b}/CP/ci/[]", chain="cp", level=CI_LEVEL, item="R2",
               reason="interval unchanged (CP chain)"))
    add(_rules("unchanged", f"{h1b}/threshold/[]", item=smoke, reason="band [0.8, 1.2]"))
    add(_rules("removed", f"{h1b}/{{CP,PLP}}/pass", "WU-0002.4", "D-02",
               "v3 H1b is decided on the PLP interval"))
    add(_rules("changed", f"{h1b}/pass", "WU-0002.4, .9", "D-02, D-14",
               "pass from the PLP interval"))
    add(_rules("new", f"{h1b}/{{CP,PLP}}/n_* {h1b}/{{n_excluded_nonfinite,n_states,reason,verdict}}",
               "WU-0002.4, .9, .11", "D-02, D-14, A4", "counts and verdict"))
    # ---- H1c (v1 H1d) ----------------------------------------------------------------------
    h1c = f"{S}/H1c"
    add(_rules("unchanged", f"{h1c}/PLP/median_ratio", chain="network", interval="ci",
               item="R2", reason="median ratio unchanged"))
    add(_rules("unchanged", f"{h1c}/PLP/ci/[]", chain="network", level=CI_LEVEL, item="R2",
               reason="interval unchanged"))
    add(_rules("unchanged", f"{h1c}/PLP/n_states", chain="network", item=smoke,
               reason="state count unchanged"))
    add(_rules("unchanged", f"{h1c}/CP/median_ratio", chain="cp", interval="ci",
               item="R2", reason="median ratio unchanged (CP chain)"))
    add(_rules("unchanged", f"{h1c}/CP/ci/[]", chain="cp", level=CI_LEVEL, item="R2",
               reason="interval unchanged (CP chain)"))
    add(_rules("unchanged", f"{h1c}/CP/n_states", chain="cp", item=smoke,
               reason="state count unchanged (CP chain)"))
    add(_rules("unchanged", f"{h1c}/threshold/[] {h1c}/thresholds/[]", item=smoke,
               reason="band unchanged"))
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
    add(_rules("unchanged", f"{h2c}/A4_minus_A2/{{mean,pass}}", chain="network",
               interval="ci", item="R2", reason="A4 - A2 unchanged"))
    add(_rules("unchanged", f"{h2c}/A4_minus_A2/relative", chain="network", item="R2",
               reason=("A4 - A2 relative to the other MSE: no interval of its own (the ci "
                       "brackets the mean, in MSE units)")))
    add(_rules("unchanged", f"{h2c}/A4_minus_A2/ci/[]", chain="network", level=CI_LEVEL, item="R2",
               reason="A4 - A2 interval unchanged"))
    add(_rules("unchanged", f"{h2c}/A4_minus_A1/{{mean,pass}}", chain="network",
               interval="ci", item="R2", reason="pilot best single was A1",
               when=(("H2c", "best_single"), "A1")))
    add(_rules("unchanged", f"{h2c}/A4_minus_A1/relative", chain="network", item="R2",
               reason="pilot best single was A1; no interval of its own",
               when=(("H2c", "best_single"), "A1")))
    add(_rules("unchanged", f"{h2c}/A4_minus_A1/ci/[]", chain="network", level=CI_LEVEL, item="R2",
               reason="pilot best single was A1", when=(("H2c", "best_single"), "A1")))
    add(_rules("unchanged", f"{h2c}/pass", chain="network", item="R2",
               reason="both parts, with the pilot's best single A1",
               when=(("H2c", "best_single"), "A1")))
    add(_rules("changed", f"{h2c}/best_single", "WU-0002.8", "DEC-0008 A4(i), D-25(i)",
               "chosen on the calibration split, not on test", discrete=True,
               chain="network"))
    # The best single forecaster is chosen on the calibration split: the pilot's A1 keeps the v1
    # statistics above; the verdict keys of its part are new in v3, like every key of any other
    # single (A0 and, generically, any name other than A1 and A2).
    add(_rules("new", f"{h2c}/A4_minus_A1/{{n_failed_resamples,reason,verdict}}",
               "WU-0002.8, .9, .11", "DEC-0008 A4(i), D-20", "verdict keys of the H2c part"))
    add(_rules("new", f"{h2c}/re:A4_minus_(?!A1$|A2$)\\w+/** {h2c}/A4o_minus_A2/** "
               f"{h2c}/calibration_mse/* "
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
    add(_rules("unchanged", f"{rb}/H1b/PLP/slope", chain="network", interval="ci",
               item="R2", reason="robustness H1b (v1 H1c) unchanged; key renamed (D-16)"))
    add(_rules("unchanged", f"{rb}/H1b/PLP/ci/[]", chain="network", level=CI_LEVEL,
               item="R2", reason="robustness H1b interval unchanged"))
    add(_rules("unchanged", f"{rb}/H1b/CP/slope", chain="cp", interval="ci",
               item="R2", reason="robustness H1b CP slope unchanged (CP chain)"))
    add(_rules("unchanged", f"{rb}/H1b/CP/ci/[]", chain="cp", level=CI_LEVEL,
               item="R2", reason="robustness H1b CP interval unchanged (CP chain)"))
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
    add(_rules("unchanged", f"{fin_rb}/corr_fin_vs_linear", chain="oracle", item="R2",
               reason=("finite-amplitude growth agreement unchanged: true states and the oracle "
                       "growth only (experiments.py:522-539)")))
    add(_rules("unchanged", f"{fin_rb}/scale_times_rho", item="R2",
               reason="the scale of the perturbation (a config constant)"))
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
        condition is false, whether or not the leaf is present), or a finding: ``FAIL-differs``,
        ``FAIL-type``, ``FAIL-missing-new``, ``FAIL-new-only``, ``FAIL-direction-missing`` (a regret
        or A* leaf absent on one side), ``FAIL-new-rule-old-present``, ``FAIL-removed-rule-new-present``,
        ``ALERT``.
    same : bool or None
        For ``changed`` leaves present on both sides: the values are equal (the rule allows a change).
    direction_ok, direction_ok_n : bool or None
        For rules with a ``direction``: the expected direction holds with the allowance of branch B
        (R3, 1e-12 relative) and of branch N (N5, 1e-6 relative).
    """

    path: Path_
    rule: Rule
    old: object
    new: object
    status: str
    same: bool | None = None
    direction_ok: bool | None = None
    direction_ok_n: bool | None = None

    @property
    def is_finding(self) -> bool:
        """A finding in every branch: a structure that contradicts the class (a presence or a type),
        or an alert."""
        return self.status in STRUCTURE_FINDINGS

    @property
    def is_value_finding(self) -> bool:
        """An ``unchanged`` leaf that differs, or a violated R3 direction (branch B only; the other
        branches judge values by N1 to N5 and D1 to D3)."""
        return self.status == "FAIL-differs" or self.direction_ok is False


STRUCTURE_FINDINGS = ("FAIL-type", "FAIL-missing-new", "FAIL-new-only", "FAIL-direction-missing",
                      "FAIL-new-rule-old-present", "FAIL-removed-rule-new-present", "ALERT")


def _condition_holds(rule: Rule, path: Path_, new: dict[Path_, object]) -> bool:
    rel, expected = rule.when
    return new.get((*path[:2], *rel), MISSING) == expected


def _direction_ok(direction: str, old: object, new: object, rel: float) -> bool | None:
    """``new >= old * (1 - rel)`` (``new>=old``) or ``new == 0.0`` in IEEE bytes (``zero``)."""
    if not direction:
        return None
    if not all(isinstance(v, float) for v in (old, new)):
        return False
    if direction == "zero":
        return struct.pack("<d", new) == struct.pack("<d", 0.0)  # type: ignore[arg-type]
    return bool(new >= old * (1.0 - rel))  # type: ignore[operator]


def judge(path: Path_, rule: Rule, old: object, new: object,
          new_leaves: dict[Path_, object]) -> LeafResult:
    """Decide the outcome of one leaf under its rule (see ``LeafResult.status``)."""
    both = old is not MISSING and new is not MISSING
    if rule.cls == "timing":
        return LeafResult(path, rule, old, new, "timing")
    if rule.cls == "unchanged":
        if rule.when and not _condition_holds(rule, path, new_leaves):
            return LeafResult(path, rule, old, new, "skipped")   # present or not: not comparable
        if new is MISSING:
            return LeafResult(path, rule, old, new, "FAIL-missing-new")
        if old is MISSING:
            return LeafResult(path, rule, old, new, "FAIL-new-only")
        outcome = values_equal(old, new, rule.rel_tol)
        status = outcome if outcome in ("equal", "equal_nan", "within_tol") else f"FAIL-{outcome}"
        return LeafResult(path, rule, old, new, status)
    if rule.cls == "changed":
        if not both:
            if rule.direction:   # a regret or A* leaf missing on one side escapes R3 and N5
                return LeafResult(path, rule, old, new, "FAIL-direction-missing")
            return LeafResult(path, rule, old, new,
                              "changed-old-only" if new is MISSING else "changed-new-only")
        same = values_equal(old, new) in ("equal", "equal_nan")
        return LeafResult(path, rule, old, new, "changed", same,
                          _direction_ok(rule.direction, old, new, R3_REL_TOL),
                          _direction_ok(rule.direction, old, new, N5_REL_TOL))
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


def mark_delay_variants(leaves: dict[Path_, object]) -> dict[Path_, object]:
    """Normalise the ``estimators`` keys ``(system, D, delay, noise)`` of one side.

    * A key whose ``(D, delay)`` equals the system's own ``(context/embed_dim, context/delay)`` on
      this side is a core estimator: it becomes ``(system, core, core, noise)``, so that a change
      of the delay or of the embedding dimension between two runs does not read as a missing and a
      new estimator (R10).
    * Any other key with delay 2 is the removed ``delay/2`` variant (WU-0002.1, D-17) unless the
      system's own delay is 2: it gets the prefix ``delay2-variant:`` so that the rule table can
      remove it (a new run that still has one fails ``FAIL-removed-rule-new-present``).
    * Without the system's context nothing is renamed.
    """
    own = {p[1]: {} for p in leaves if p[0] == "systems" and len(p) == 4 and p[2] == "context"}
    for p, v in leaves.items():
        if p[0] == "systems" and len(p) == 4 and p[2] == "context" and p[3] in ("embed_dim", "delay"):
            own[p[1]][p[3]] = v
    out = {}
    for path, value in leaves.items():
        if path[0] == "estimators" and len(path) > 1:
            found = re.match(r"\('(\w+)',\s(\d+),\s(\d+),\s([\d.]+)\)$", path[1])
            ctx = own.get(found.group(1), {}) if found else {}
            if found and "delay" in ctx:
                dim, delay, noise = int(found.group(2)), int(found.group(3)), found.group(4)
                if ctx.get("embed_dim") == dim and ctx["delay"] == delay:
                    path = (path[0], f"('{found.group(1)}', core, core, {noise})", *path[2:])
                elif delay == 2 and ctx["delay"] != 2:
                    path = (path[0], "delay2-variant:" + path[1], *path[2:])
        out[path] = value
    return out


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
    return mark_delay_variants(old), mark_delay_variants(new), len(flat_new) - len(new)


# ------------------------------------------------------------------------------ branches B, N, D
NETWORK_INDEPENDENT = frozenset({"fixture", "dynamics", "cp", "oracle"})
CHAIN_ORDER = ("fixture", "dynamics", "cp", "oracle", "network")
V7_BAND = (0.9, 1.1)


def system_of(path: Path_) -> str | None:
    """The system a leaf belongs to (``None`` for run-level leaves)."""
    if path[0] in ("systems", "robustness") and len(path) > 1:
        return path[1]
    if path[0] == "estimators" and len(path) > 1:
        found = re.match(r"\('(\w+)'", path[1])
        return found.group(1) if found else None
    return None


def select_branch(results: list[LeafResult], old: dict[Path_, object],
                  new: dict[Path_, object]) -> tuple[str, list[str], bool]:
    """Select the branch of the approved criterion (DEC-0019).

    * **D**: any ``context`` difference other than the ones allowed for N: ``lambda_max`` and
      ``interval`` must be bitwise equal, every integer leaf identical, ``obs_scale`` within 1e-12
      relative; a context leaf missing from the new run is a difference.
    * **B**: not D, and every ``unchanged`` leaf is bitwise equal (or within its rule's cited
      ``rel_tol``).
    * **N**: not D, and some ``unchanged`` leaf differs.

    Returns
    -------
    tuple[str, list[str], bool]
        ``(branch, reasons, obs_scale_differs)``; ``reasons`` lists the context differences for D
        and a count of differing unchanged leaves for N.
    """
    reasons: list[str] = []
    obs_differs = False
    for path in sorted(p for p in old if p[0] == "systems" and len(p) == 4 and p[2] == "context"):
        a, b = old[path], new.get(path, MISSING)
        if b is MISSING:
            reasons.append(f"{show(path)} missing from the new run")
        elif path[3] == "obs_scale":
            outcome = values_equal(a, b, SWITCH_REL_TOL)
            if outcome == "within_tol":
                obs_differs = True
            elif outcome not in ("equal", "equal_nan"):
                reasons.append(f"{show(path)}: {a!r} -> {b!r} (beyond 1e-12 relative)")
        elif values_equal(a, b) not in ("equal", "equal_nan"):
            reasons.append(f"{show(path)}: {a!r} -> {b!r}")
    if reasons:
        return "D", reasons, obs_differs
    differing = [r for r in results if r.rule.cls == "unchanged" and r.status.startswith("FAIL")]
    if differing:
        return "N", [f"{len(differing)} unchanged leaves differ from the pilot"], obs_differs
    return "B", [], obs_differs


def z_of(constants: dict, level: float | None) -> float:
    """The z value of a nominal level (1.960 at 95%, 2.394 at 1 - 0.05/3; DEC-0019)."""
    if level is None or level not in constants["z"]:
        raise ToolError(f"no z value for the interval level {level!r}")
    return constants["z"][level]


def interval_of(leaves: dict[Path_, object], table: Table, path: Path_,
                rule: Rule) -> tuple[float, float, float | None] | None:
    """``(lo, hi, level)`` of the interval sibling of a statistic, or ``None``."""
    if not rule.interval:
        return None
    base = path[:-1]
    lo = leaves.get((*base, rule.interval, "[0]"), MISSING)
    hi = leaves.get((*base, rule.interval, "[1]"), MISSING)
    if not all(isinstance(v, float) and math.isfinite(v) for v in (lo, hi)):
        return None
    return lo, hi, table.classify((*base, rule.interval, "[0]")).level  # type: ignore[return-value]


def se_arm(est: float, lo: float, hi: float, delta: float, z: float) -> float:
    """The pilot arm on the side of ``delta`` (``hi - est`` if positive, else ``est - lo``) over z."""
    return ((hi - est) if delta > 0 else (est - lo)) / z


@dataclass
class NReport:
    """Result of the checks N1 to N5 (branch N) of the approved criterion."""

    n1: list[tuple]
    n2: list[tuple]
    n3: list[tuple]
    events: list[tuple]
    n5: list[tuple]
    locus: list[tuple]
    findings: list[str]

    @property
    def passed(self) -> bool:
        """No finding (N4, the gate, is judged with the gate rows)."""
        return not self.findings


def locus_table(results: list[LeafResult]) -> list[tuple]:
    """The divergence-locus table: per system and chain (in ``CHAIN_ORDER``), the unchanged leaves
    compared, how many differ, the largest relative difference, and the first differing chain.

    Returns
    -------
    list[tuple]
        ``(system, chain, n_compared, n_differ, max_rel, first)`` with ``first`` true on the first
        chain of the system that differs; the chains before it are all equal by construction.
    """
    stats: dict[tuple[str, str], list] = {}
    for r in results:
        if r.rule.cls != "unchanged" or not r.rule.chain or r.status not in (
                "equal", "equal_nan", "within_tol", "FAIL-differs"):
            continue
        entry = stats.setdefault((system_of(r.path) or "-", r.rule.chain), [0, 0, 0.0])
        entry[0] += 1
        if r.status == "FAIL-differs":
            entry[1] += 1
            entry[2] = max(entry[2], _rel_diff(r.old, r.new))
    rows = []
    for system in sorted({k[0] for k in stats}):
        first_done = False
        for chain in CHAIN_ORDER:
            if (system, chain) not in stats:
                continue
            n, n_diff, max_rel = stats[(system, chain)]
            first = bool(n_diff) and not first_done
            first_done = first_done or first
            rows.append((system, chain, n, n_diff, max_rel, first))
    return rows


def _rel_diff(old: object, new: object) -> float:
    """``|new - old| / |old|`` for floats (``inf`` if old is 0 or either is not finite), else ``inf``."""
    if not (isinstance(old, float) and isinstance(new, float)):
        return math.inf
    delta = abs(new - old)
    if delta == 0.0:
        return 0.0
    if not (math.isfinite(delta) and old != 0.0):
        return math.inf
    return delta / abs(old)


def evaluate_n(results: list[LeafResult], old: dict[Path_, object], new: dict[Path_, object],
               table: Table, constants: dict, obs_scale_differs: bool = False) -> NReport:
    """Evaluate N1 to N3 and N5 (N4 is the gate: see ``gate_rows``).

    * N1: an ``unchanged`` leaf of a network-independent chain (dynamics, cp, oracle, fixture, as
      tagged in the rule table) that differs at all. If ``obs_scale`` differs, these leaves fall
      under N2 instead.
    * N2: every other continuous ``unchanged`` leaf has ``|new - old| <= n2_rel * |old|`` (closed),
      or meets N3.
    * N3: a leaf beyond that has a chain-head event upstream, and, if it has a pilot interval,
      ``|delta| <= n3_fraction * SE_arm``. Every N3 leaf (with the events that license it) and every
      event is listed; any other excess is a finding. An event has a scope. A per-system head
      (``chosen_width``, ``val_loss_by_width`` or a ``fitted`` coefficient beyond ``n2_rel``)
      licenses every leaf of its system and chain. A local event (an integer count, ``realized_K``,
      any other discrete flip) licenses only the leaves of its own result block (``path[:3]``).
    * N5: regret(v3) >= regret(v1) * (1 - 1e-6) for the rules with direction ``new>=old``, and
      A* exactly 0.0. A violation is attributed to the sentinel (listed, not a finding) if the
      ``curvature_floor`` counter of the core cell (``systems/<s>/handling/cells/base|...|core``)
      is not 0 (AM3 H3 concerns the scored entries; the cell record sums the three splits).

    Returns
    -------
    NReport
        Rows per check, the events, the locus table and the findings.
    """
    n2_rel, fraction = constants["n2_rel"], constants["n3_fraction"]
    n1, n2, events, candidates, findings = [], [], [], [], []

    def head(r: LeafResult, kind: str, scope: str) -> None:
        events.append((show(r.path), kind, r.old, r.new, system_of(r.path), r.rule.chain, scope))

    for r in results:
        if (r.rule.cls != "unchanged" or r.status != "FAIL-differs"
                or r.old is MISSING or r.new is MISSING):
            continue
        chain, path = r.rule.chain, r.path
        if chain in NETWORK_INDEPENDENT and not obs_scale_differs:
            n1.append((show(path), r.old, r.new, chain))
            findings.append(f"N1: {show(path)} ({chain} chain) differs: {r.old!r} -> {r.new!r}")
        elif isinstance(r.old, float) and isinstance(r.new, float):
            rel = _rel_diff(r.old, r.new)
            if rel <= n2_rel:
                n2.append((show(path), r.old, r.new, rel, "within"))
            elif "val_loss_by_width" in path:
                head(r, "val_loss beyond bound", "system")
                n2.append((show(path), r.old, r.new, rel, "chain-head event"))
            elif len(path) > 2 and path[2] == "fitted":
                head(r, "fitted coefficient", "system")
                n2.append((show(path), r.old, r.new, rel, "chain-head event"))
            else:
                candidates.append((r, rel))
        elif path[-1] == "chosen_width":
            head(r, "chosen width", "system")
        elif type(r.old) is int or r.rule.discrete:
            head(r, "integer count" if type(r.old) is int else "discrete", "/".join(path[:3]))
        else:
            findings.append(f"N2: discrete leaf {show(path)} differs without being a counted "
                            f"event: {r.old!r} -> {r.new!r}")
    n3 = []
    for r, rel in candidates:
        system, chain, block = system_of(r.path), r.rule.chain, "/".join(r.path[:3])
        upstream = [e for e in events if e[5] == chain and e[4] in (None, system)
                    and e[6] in ("system", block)]
        if not upstream:
            findings.append(f"N2: {show(r.path)} differs by {rel!r} relative (beyond {n2_rel!r}) "
                            f"with no chain-head event upstream in the {chain or 'untagged'} chain "
                            "(a count licenses only its own block)")
            n2.append((show(r.path), r.old, r.new, rel, "NO EVENT"))
            continue
        n2.append((show(r.path), r.old, r.new, rel, "N3"))
        names = "; ".join(e[0] for e in upstream)
        pair = interval_of(old, table, r.path, r.rule)
        if pair is None:
            n3.append((show(r.path), r.old, r.new, rel, names, None, None, None, None, None, True))
            continue
        lo, hi, level = pair
        delta = r.new - r.old  # type: ignore[operator]
        se = se_arm(r.old, lo, hi, delta, z_of(constants, level))  # type: ignore[arg-type]
        bound = fraction * se
        ok = bool(abs(delta) <= bound)
        n3.append((show(r.path), r.old, r.new, rel, names, lo, hi, level, se, bound, ok))
        if not ok:
            findings.append(f"N3: {show(r.path)} moves {delta!r}, more than {fraction} SE_arm "
                            f"= {bound!r} (level {level!r})")
    n5 = []
    for r in results:
        if not r.rule.direction or r.old is MISSING or r.new is MISSING:
            continue
        floor_path, floor = core_curvature_floor(new, system_of(r.path))
        attributed = r.direction_ok_n is False and isinstance(floor, int) and floor > 0
        n5.append((show(r.path), r.old, r.new, r.direction_ok_n, attributed,
                   show(floor_path) if attributed and floor_path else ""))
        if r.direction_ok_n is False and not attributed:
            findings.append(f"N5: {show(r.path)}: {r.old!r} -> {r.new!r} violates the "
                            f"{r.rule.direction} direction")
    return NReport(n1, n2, n3, events, n5, locus_table(results), findings)


def core_curvature_floor(new: dict[Path_, object], system: str | None
                         ) -> tuple[Path_ | None, object]:
    """The ``curvature_floor`` counter of the core cell of a system (sum of its splits), or
    ``(None, None)``. The core cell of ``handling.cells`` is the key ``base|...|core``."""
    for path in sorted(new):
        if (path[:3] == ("systems", system, "handling") and len(path) == 7 and path[3] == "cells"
                and path[4].startswith("base|") and path[4].endswith("|core")
                and path[5:] == ("counts", "curvature_floor")):
            return path, new[path]
    return None, None


def gate_rows(new: dict[Path_, object]) -> list[tuple[str, str, object, bool]]:
    """R4 (the gate flags and the V7 rule) and R5 (P2(c) counters) of every system of the new run.

    The V7 rule is recomputed from the numbers: ``n_nonfinite`` is 0, the median slope and the
    median efficiency at every noise level are in [0.9, 1.1] (closed).

    Returns
    -------
    list[tuple]
        ``(check, path, value, ok)``. A missing leaf is ``ok = False`` with value ``MISSING``.
    """
    systems = sorted({p[1] for p in new if p[0] == "systems" and len(p) > 2})
    lo, hi = V7_BAND
    in_band = lambda v: isinstance(v, float) and lo <= v <= hi
    wanted = [("R4", ("validation", "gate", k), lambda v: v is True)
              for k in ("V1", "V2", "V4", "V5", "V6", "V7", "gate_pass")]
    wanted += [("R4", ("V7", "n_nonfinite"), lambda v: v == 0 and type(v) is int),
               ("R4", ("V7", "median_slope"), in_band)]
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
        levels = sorted(p for p in new if p[:4] == ("systems", system, "V7", "efficiency_median_by_noise")
                        and len(p) == 5)
        if not levels:
            rows.append(("R4", f"systems/{system}/V7/efficiency_median_by_noise/*", MISSING, False))
        rows += [("R4", show(p), new[p], in_band(new[p])) for p in levels]
    return rows


@dataclass
class DReport:
    """Result of branch D (D1 with a local v1 reference run, or D3 with ``--no-reference``)."""

    mode: str                      # "D1", "D3" or "missing" (neither a reference nor the flag)
    d2_subject: str
    d2: list[tuple]
    int_diffs: list[tuple]
    d1: Comparison | None
    d3: list[tuple]
    d3_reported: list[tuple]
    d3_z: float | None
    findings: list[str]

    @property
    def passed(self) -> bool:
        """The mode is decided and no finding was recorded."""
        return self.mode != "missing" and not self.findings


def context_ints_differ(old: dict[Path_, object], other: dict[Path_, object]) -> list[tuple]:
    """Integer ``context`` leaves of ``old`` that differ in ``other`` (listed by D2)."""
    return [(show(p), v, other.get(p, MISSING)) for p, v in sorted(old.items())
            if p[0] == "systems" and len(p) == 4 and p[2] == "context" and type(v) is int
            and other.get(p, MISSING) != v]


def d2_rows(old: dict[Path_, object], subject: dict[Path_, object],
            constants: dict) -> list[tuple]:
    """D2: ``|lambda_subject - lambda_pilot| <= k SE`` per system (closed)."""
    rows = []
    for path, value in sorted(old.items()):
        if path[0] == "systems" and len(path) == 4 and path[2:] == ("context", "lambda_max"):
            if path[1] not in constants["se"]:
                raise ToolError(f"no SE for {path[1]} in the fallback constants")
            got = subject.get(path, MISSING)
            tol = constants["k"] * constants["se"][path[1]]
            delta = abs(got - value) if isinstance(got, float) else math.inf  # type: ignore[operator]
            rows.append((path[1], value, got, delta, tol, bool(delta <= tol)))
    return rows


def d3_rows(results: list[LeafResult], old: dict[Path_, object], new: dict[Path_, object],
            table: Table, constants: dict) -> tuple[list[tuple], list[tuple], float | None]:
    """D3: for each ``unchanged`` statistic with an interval in both runs,
    ``|delta| <= z_B sqrt(SE_old^2 + SE_new^2)`` with ``z_B = Phi^-1(1 - 0.05 / (2 m))`` over the
    ``m`` such statistics. Statistics without intervals, and discrete flips, are reported only.

    Returns
    -------
    tuple
        ``(rows, reported, z_B)``; a row is ``(path, old, new, delta, se_old, se_new, bound, ok)``.
    """
    pairs = []
    for r in results:
        if (r.rule.cls != "unchanged" or not r.rule.interval or r.old is MISSING
                or r.new is MISSING or not isinstance(r.old, float) or not isinstance(r.new, float)):
            continue
        a, b = interval_of(old, table, r.path, r.rule), interval_of(new, table, r.path, r.rule)
        if a is not None and b is not None:
            pairs.append((r, a, b))
    z_b = NormalDist().inv_cdf(1.0 - 0.05 / (2 * len(pairs))) if pairs else None
    rows = []
    for r, a, b in pairs:
        delta = r.new - r.old  # type: ignore[operator]
        se_old = se_arm(r.old, a[0], a[1], delta, z_of(constants, a[2]))  # type: ignore[arg-type]
        se_new = se_arm(r.new, b[0], b[1], delta, z_of(constants, b[2]))  # type: ignore[arg-type]
        bound = z_b * math.hypot(se_old, se_new)  # type: ignore[operator]
        rows.append((show(r.path), r.old, r.new, delta, se_old, se_new, bound,
                     bool(abs(delta) <= bound)))
    in_rows = {row[0] for row in rows}
    reported = [(show(r.path), r.old, r.new, _rel_diff(r.old, r.new)) for r in results
                if r.rule.cls == "unchanged" and r.status == "FAIL-differs"
                and r.rule.level is None and show(r.path) not in in_rows
                and r.old is not MISSING and r.new is not MISSING]
    return rows, reported, z_b


def evaluate_d(results: list[LeafResult], old: dict[Path_, object], new: dict[Path_, object],
               table: Table, constants: dict, gates: list[tuple], reference: Comparison | None,
               no_reference: bool) -> DReport:
    """Evaluate branch D.

    * D1 (a ``reference`` run of the v1 code, same machine and threads): branches B then N must
      hold for (new run, reference), and D2 holds for the reference against the pilot.
    * D3 (``no_reference``): D2 holds for the new run, N4 (the gate) holds, and the interval band.
    * With neither, the mode is ``missing`` (the tool exits 3).
    """
    findings: list[str] = []
    if reference is not None:
        d2 = d2_rows(old, reference.old, constants)
        ints = context_ints_differ(old, reference.old)
        if reference.branch == "D":
            findings.append("D1: the new run is still in branch D against the local v1 run: "
                            + "; ".join(reference.reasons))
        elif reference.exit_code() != 0:
            findings.append(f"D1: branch {reference.branch} fails against the local v1 run")
        findings += [f"D2: lambda of {s}: local {b!r} against pilot {a!r}, |delta| {d!r} > {t!r}"
                     for s, a, b, d, t, ok in d2 if not ok]
        return DReport("D1", "local v1 run", d2, ints, reference, [], [], None, findings)
    if no_reference:
        d2 = d2_rows(old, new, constants)
        findings += [f"D2: lambda of {s}: new {b!r} against pilot {a!r}, |delta| {d!r} > {t!r}"
                     for s, a, b, d, t, ok in d2 if not ok]
        findings += [f"N4: {path} = {value!r}" for check, path, value, ok in gates
                     if check == "R4" and not ok]
        rows, reported, z_b = d3_rows(results, old, new, table, constants)
        findings += [f"D3: {p} moves {d!r}, more than {b!r}" for p, _, _, d, _, _, b, ok in rows
                     if not ok]
        return DReport("D3", "new run", d2, context_ints_differ(old, new), None, rows, reported,
                       z_b, findings)
    return DReport("missing", "", [], context_ints_differ(old, new), None, [], [], None,
                   [("branch D needs the local v1 reference run (--reference, D1) or --no-reference "
                    "(D3)")])


def cache_status(info: dict) -> tuple[str, bool]:
    """Whether ``lyapunov.json`` pre-existed in the run's cache directory (DEC-0019 condition).

    ``info`` has ``flag`` (``yes``, ``no`` or ``None``, from the launch record), ``cache_mtime`` (a
    timestamp or ``None``) and ``start`` (the run's start as a timestamp or ``None``).

    Returns
    -------
    tuple[str, bool]
        The sentence for the report and whether it is a finding (the run must then be repeated with
        an empty cache). A file last written before the run started cannot have been made by it.
    """
    if info.get("flag") == "yes":
        return "launch record: lyapunov.json pre-existed in the cache directory", True
    mtime, start = info.get("cache_mtime"), info.get("start")
    if mtime is not None and start is not None and mtime < start:
        return (("lyapunov.json was last written before the run started, so it pre-existed "
                "(and was read instead of recomputed)"), True)
    if info.get("flag") == "no":
        return "launch record: the cache directory was empty at the start", False
    if mtime is None:
        return "no lyapunov.json found next to the new run: pre-existence cannot be judged", False
    return ("lyapunov.json was written during the run; the run does not record whether it "
            "pre-existed (pass --cache-preexisted no from the launch record)"), False


# ------------------------------------------------------------------------------ platform (WU-0001.6)
PLATFORM_SIDES = (("new", "new run"), ("old", "old (v1 pilot)"),
                  ("reference", "reference (local v1 run)"))
PLATFORM_LINE = ("platform differs (DEF-0024): cross-host differences in the cp, oracle and fixture "
                 "chains are expected")


def platform_record(tree: object) -> dict:
    """The platform of one ``results.json`` tree, from its ``provenance`` block.

    Returns
    -------
    dict
        ``{"recorded": True, "model", "corenames", "coretype", "determinate", "why"}``
        (``corenames``: the runtime OpenBLAS kernel of each library, in the block's order, used to compare;
        ``model_text`` and ``blas_text``: the table cells, which show a failure with its error and never
        as a value;
        ``coretype``: the value of ``OPENBLAS_CORETYPE`` or ``None``; ``determinate``: False when
        a probe failed or found nothing, so two such records must not be compared as values; ``why``:
        the reasons, as text), or ``{"recorded": False, "why": <text>}`` for a tree without a
        provenance block or without the platform keys (a ``/1`` block).
    """
    block = tree.get("provenance") if isinstance(tree, dict) else None
    if not isinstance(block, dict):
        return {"recorded": False, "why": "no provenance block"}
    cpu, blas, env = block.get("cpu"), block.get("blas"), block.get("env")
    if not isinstance(cpu, dict) or not isinstance(blas, dict):
        return {"recorded": False, "why": "no platform keys in the provenance block"}
    libraries = [lib for lib in blas.get("libraries", []) if isinstance(lib, dict)]
    model = str(cpu.get("model", "unknown"))
    corenames = [str(lib.get("corename") or "unknown") for lib in libraries]
    reasons = []
    if model == "unknown" or cpu.get("error"):
        reasons.append("CPU model unknown" + (f" ({cpu['error']})" if cpu.get("error") else ""))
    if blas.get("error"):
        reasons.append(f"BLAS probe failed ({blas['error']})")
    elif not libraries:
        reasons.append("no OpenBLAS library mapped")
    reasons += [f"{lib.get('library', '?')} corename unknown"
                + (f" ({lib['error']})" if lib.get("error") else "")
                for lib in libraries if not lib.get("corename")]
    if blas.get("error"):
        blas_text = f"probe failed ({blas['error']})"
    else:
        blas_text = ", ".join(
            (f"{name} ({lib['error']})" if lib.get("error") else name)
            for name, lib in zip(corenames, libraries)) or "none mapped"
    model_text = (f"unknown ({cpu.get('error') or 'source ' + str(cpu.get('source', 'none'))})"
                  if model == "unknown" else model)
    return {"recorded": True, "model": model, "corenames": corenames,
            "coretype": env.get("OPENBLAS_CORETYPE") if isinstance(env, dict) else None,
            "determinate": not reasons, "why": "; ".join(reasons),
            "model_text": model_text, "blas_text": blas_text}


def platform_mismatch(first: dict, second: dict, labels: tuple[str, str] = ("first", "second")
                      ) -> str | None:
    """The information line about two platforms (never a status, branch or exit code).

    * A side that is recorded but not determinate (a failed probe, an unknown model or corename):
      ``platform not determinable (<side>: <why>)``, because two unknowns are not the same platform
      and the comparison below would call them equal.
    * Both recorded and determinate, with a different CPU model or a different corename:
      ``PLATFORM_LINE``. ``OPENBLAS_CORETYPE`` alone does not count (the corename is what ran).
    * Otherwise ``None`` (a side not recorded, or the two agree).
    """
    bad = [f"{label}: {rec['why']}" for rec, label in zip((first, second), labels)
           if rec["recorded"] and not rec["determinate"]]
    if bad:
        return "platform not determinable (" + "; ".join(bad) + ")"
    if not (first["recorded"] and second["recorded"]):
        return None
    if first["model"] != second["model"] or sorted(first["corenames"]) != sorted(second["corenames"]):
        return PLATFORM_LINE
    return None


def platform_rows(records: dict[str, dict]) -> tuple[list[tuple], list[str]]:
    """The rows of the Platform table and the information lines, for the sides present.

    Parameters
    ----------
    records : dict
        ``platform_record`` of each side, keyed ``new``, ``old`` and (optionally) ``reference``.
    """
    rows: list[tuple] = []
    for key, label in PLATFORM_SIDES:
        if key not in records:
            continue
        rec = records[key]
        if rec["recorded"]:
            rows.append((label, rec["model_text"], rec["blas_text"], rec["coretype"] or "unset"))
        else:
            rows.append((label, f"not recorded ({rec['why']})", "", ""))
    notes = []
    for key, label in PLATFORM_SIDES[1:]:
        if key in records and "new" in records:
            line = platform_mismatch(records["new"], records[key], ("new run", label))
            if line:
                notes.append(f"new run against {label}: {line}")
    return rows, notes


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
    """Everything the report and the exit code need.

    Attributes
    ----------
    branch : str
        ``B``, ``N`` or ``D`` (DEC-0019).
    nreport : NReport or None
        The N1 to N5 evaluation (branch N only).
    dreport : DReport or None
        The D1 to D3 evaluation (branch D only).
    cache : tuple[str, bool]
        The lyapunov.json statement and whether it is a finding.
    """

    results: list[LeafResult]
    old: dict[Path_, object]
    new: dict[Path_, object]
    n_provenance: int
    branch: str
    reasons: list[str]
    gates: list[tuple]
    nreport: NReport | None
    dreport: DReport | None
    cache: tuple[str, bool]
    info: dict
    obs_scale_differs: bool = False

    def findings(self) -> list[LeafResult]:
        """Leaf findings that fail the run: structure findings in every branch, plus the value
        findings (a differing unchanged leaf, a violated R3 direction) in branch B."""
        out = [r for r in self.results if r.is_finding]
        if self.branch == "B":
            out += [r for r in self.results if r.is_value_finding]
        return out

    def failures(self) -> list[str]:
        """One sentence per reason the run fails (empty: exit 0)."""
        out = [f"{r.status}: {show(r.path)}" for r in self.findings()]
        out += [f"{c}: {p} = {fmt(v)}" for c, p, v, ok in self.gates if not ok]
        if self.cache[1]:
            out.append("cache: " + self.cache[0])
        if self.nreport is not None:
            out += self.nreport.findings
        if self.dreport is not None:
            out += self.dreport.findings
        return out

    def exit_code(self) -> int:
        """0 pass; 1 findings; 3 branch D without a reference run and without ``--no-reference``."""
        if self.dreport is not None and self.dreport.mode == "missing":
            return EXIT_NEEDS_INPUT
        return EXIT_FINDINGS if self.failures() else 0


def _pack(rows_in: list[LeafResult], label) -> list[tuple]:
    """Rows of findings: one row per leaf, one row per rule for bulk arrays."""
    rows = [(label(r), show(r.path), fmt(r.old), fmt(r.new), r.rule.pattern, r.rule.sub)
            for r in rows_in if not r.rule.bulk]
    packed: dict[tuple[str, str], list[LeafResult]] = defaultdict(list)
    for r in rows_in:
        if r.rule.bulk:
            packed[(label(r), r.rule.pattern)].append(r)
    rows += [(status, f"{len(g)} leaves, first {show(g[0].path)}", fmt(g[0].old), fmt(g[0].new),
              pattern, g[0].rule.sub) for (status, pattern), g in packed.items()]
    return rows


def _n_lines(rep: NReport, heading: str) -> list[str]:
    out = [heading, ""]
    out += ["N1 (network-independent chains bitwise equal): leaves that differ", ""]
    out += table_lines(("path", "v1 pilot", "new", "chain"), [(a, fmt(b), fmt(c), d)
                                                              for a, b, c, d in rep.n1])
    out += ["N2 (continuous unchanged leaves that differ, bound 1e-6 relative, closed):", ""]
    out += table_lines(("path", "v1 pilot", "new", "relative difference", "outcome"),
                       [(a, fmt(b), fmt(c), repr(d), e) for a, b, c, d, e in rep.n2])
    out += [("N3 (beyond the bound: chain-head event upstream, and 0.2 SE_arm when the pilot has an "
            "interval):"), ""]
    out += table_lines(("path", "v1 pilot", "new", "relative", "licensing events", "lower", "upper",
                        "level", "SE_arm", "0.2 SE_arm", "ok"),
                       [(a, fmt(b), fmt(c), repr(d), e, fmt(f), fmt(g), fmt(h), fmt(i), fmt(j),
                         "yes" if k else "NO") for a, b, c, d, e, f, g, h, i, j, k in rep.n3])
    out += [("Chain-head events (differing discrete quantities, integer counts, fitted "
            "coefficients beyond 1e-6):"), ""]
    out += table_lines(("path", "kind", "v1 pilot", "new", "system", "chain", "scope"),
                       [(a, b, fmt(c), fmt(d), e, f, g) for a, b, c, d, e, f, g in rep.events])
    out += ["N5 (regret(v3) >= regret(v1) (1 - 1e-6); A* regret exactly 0.0):", ""]
    bad = [r for r in rep.n5 if r[3] is False]
    out.append(f"checked {len(rep.n5)} leaves; violations {len(bad)}")
    out += table_lines(("path", "v1 pilot", "new", "attributed to curvature_floor (counter)"),
                       [(a, fmt(b), fmt(c), f"yes ({g})" if e else "no")
                        for a, b, c, d, e, g in bad])
    return out


def _locus_lines(rows: list[tuple]) -> list[str]:
    out = ["## Divergence locus", "",
           ("Per system, the chains in the order fixture, dynamics, cp, oracle, network; the first "
           "chain with a differing unchanged leaf is marked, and every chain before it is equal."),
           ""]
    out += table_lines(("system", "chain", "leaves compared", "differ", ("largest relative "
                        "difference"), "first differing chain"),
                       [(s, c, n, d, repr(m), "FIRST" if f else "") for s, c, n, d, m, f in rows])
    return out


def _d_lines(rep: DReport, branch_note: str) -> list[str]:
    out = ["## Branch D", "", branch_note, "", f"mode: {rep.mode}"]
    if rep.mode == "missing":
        return out + ["", *rep.findings, ""]
    out += ["", f"D2 (lambda of the {rep.d2_subject} against the pilot, |delta| <= 5 SE, closed):", ""]
    out += table_lines(("system", "pilot", rep.d2_subject, "delta", "k SE", "ok"),
                       [(a, fmt(b), fmt(c), fmt(d), fmt(e), "yes" if f else "NO")
                        for a, b, c, d, e, f in rep.d2])
    out += [f"Integer context leaves of the pilot that differ in the {rep.d2_subject} (listed):", ""]
    out += table_lines(("path", "pilot", rep.d2_subject),
                       [(a, fmt(b), fmt(c)) for a, b, c in rep.int_diffs])
    if rep.mode == "D1" and rep.d1 is not None:
        sub = rep.d1
        out += [f"D1 reference run (the v1 code run locally): {sub.info.get('old_path')}",
                f"- sha256: {sub.info.get('sha256_old')}", ""]
        out += [(f"D1: the new run against the local v1 run is in branch {sub.branch}; exit code of "
                f"that comparison {sub.exit_code()}."), ""]
        if sub.reasons:
            out += [f"- {cell(x)}" for x in sub.reasons] + [""]
        reasons = sub.failures()
        out += [f"Failures of that comparison: {len(reasons)}", ""]
        out += [f"- {cell(x)}" for x in reasons[:100]]
        if len(reasons) > 100:
            out.append(f"- ... and {len(reasons) - 100} more (see the D1 leaves JSON)")
        if sub.nreport is not None:
            out += [""] + _n_lines(sub.nreport, "### D1: branch N checks against the local v1 run")
        out.append("")
    if rep.mode == "D3":
        out += [(f"D3 (m = {len(rep.d3)} statistics with intervals in both runs; z_B = "
                f"{rep.d3_z!r}):"), ""]
        out += table_lines(("path", "pilot", "new", "delta", "SE pilot", "SE new", "bound", "ok"),
                           [(a, fmt(b), fmt(c), fmt(d), fmt(e), fmt(f), fmt(g), "yes" if h else "NO")
                            for a, b, c, d, e, f, g, h in rep.d3])
        out += ["Reported only (no interval in one of the runs, or discrete):", ""]
        out += table_lines(("path", "pilot", "new", "relative difference"),
                           [(a, fmt(b), fmt(c), repr(d)) for a, b, c, d in rep.d3_reported])
    return out


def render_report(cmp: Comparison) -> str:
    """The Markdown report of a comparison (first line: the DEVELOPMENT label)."""
    info = cmp.info
    note = ("Generated by `tools/compare_pilot.py`; do not edit. A difference between a DEV-0 run "
            "and the pilot is a regression finding for the development of the code, not evidence "
            "about any hypothesis. Criterion: DEC-0019.")
    out = [LABEL, "", "# DEV-0 regression against the v1 pilot (WU-0002.12)", "", note, "",
           "## Provenance", ""]
    for key in ("commit", "dirty", "run_dir", "sha256_old", "sha256_new", "manifest_row",
                "lpc_threads", "nproc"):
        out.append(f"- {key.replace('_', ' ')}: {info.get(key, 'n/a')}")
    out.append(f"- provenance leaves excluded from the new run: {cmp.n_provenance}")
    out.append(f"- lyapunov.json: {cell(cmp.cache[0])}" + (" (FINDING)" if cmp.cache[1] else ""))
    out += ["", "## Platform", "",
            "Information only (DEF-0024): no status, branch or exit code depends on this section.", ""]
    rows, notes = platform_rows(info["platform"])
    out += table_lines(("side", "CPU model", "OpenBLAS corenames", "OPENBLAS_CORETYPE"), rows)
    out += [f"- {cell(note)}" for note in notes] + (["", ] if notes else [])
    out += ["", "## Branch", ""]
    meaning = {"B": "bitwise: every unchanged leaf equals the pilot's",
               "N": "network: the context equals the pilot's, some unchanged leaf differs",
               "D": "dynamics: the context differs (a new realization of the whole study)"}
    out.append(f"- branch: {cmp.branch} ({meaning[cmp.branch]})")
    out += [f"- {cell(r)}" for r in cmp.reasons]
    if cmp.obs_scale_differs:
        out.append("- obs_scale differs within 1e-12 relative: N2 applies to the network-independent "
                   "chains too")
    out += ["", "## Counts", ""]
    by_class: dict[str, Counter] = defaultdict(Counter)
    for r in cmp.results:
        by_class[r.rule.cls][r.status] += 1
    out += table_lines(("group", "leaves", "outcomes"),
                       [(c, sum(by_class[c].values()),
                         ", ".join(f"{s}: {n}" for s, n in sorted(by_class[c].items())))
                        for c in CLASSES if by_class[c]])
    nan_equal = sum(1 for r in cmp.results if r.status == "equal_nan")
    out += [f"NaN equal to NaN (counted): {nan_equal}", ""]

    out += ["## Findings", ""]
    fails = cmp.failures()
    out.append(f"Failures under branch {cmp.branch}: {len(fails)}")
    out.append("")
    out += [f"- {cell(x)}" for x in fails[:200]]
    if len(fails) > 200:
        out.append(f"- ... and {len(fails) - 200} more")
    out.append("")
    out.append("Structure findings (a presence or a type that contradicts the class, an alert) "
               "fail the run in every branch; a differing unchanged leaf and a violated R3 "
               "direction fail it in branch B; in N and D the values are judged by N1 to N5 and "
               "D1 to D3.")
    out.append("")
    shown = [r for r in cmp.results if r.is_finding or (cmp.branch == "B" and r.is_value_finding)]
    out += table_lines(("status", "path", "v1 pilot", "new", "rule", "sub-task"),
                       _pack(shown, lambda r: "direction violated" if r.direction_ok is False
                             and r.status == "changed" else r.status))
    if cmp.branch != "B":
        differing = [r for r in cmp.results if r.status == "FAIL-differs"]
        out += [(f"Unchanged leaves that differ from the pilot ({len(differing)}; judged by the "
                "branch checks below):"), ""]
        out += table_lines(("status", "path", "v1 pilot", "new", "rule", "sub-task"),
                           _pack(differing, lambda r: r.status))

    if cmp.nreport is not None:
        out += _n_lines(cmp.nreport, "## Branch N: N1 to N5")
        out += [""] + _locus_lines(cmp.nreport.locus)
    if cmp.dreport is not None:
        out += _d_lines(cmp.dreport, "D1 re-reference (the local v1 run), D2 and D3 of DEC-0019.")
    if cmp.nreport is None:
        out += _locus_lines(locus_table(cmp.results))

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
             "rule": r.rule.pattern, "chain": r.rule.chain, "same": r.same,
             "direction_ok": r.direction_ok, "direction_ok_n": r.direction_ok_n}
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
            "run_dir": run_dir, "old_path": str(old_path), "sha256_old": sha256_of(old_path),
            "sha256_new": sha256_of(new_path), "manifest_row": manifest_row,
            "lpc_threads": f"{env.get('LPC_THREADS', 'n/a')} (run); nproc {env.get('NPROC', 'n/a')} "
                           "(run env)",
            "nproc": f"{os.cpu_count()} cpus, affinity {affinity} (this process)"}


def cache_info(new_tree: object, cache_file: Path | None, flag: str | None) -> dict:
    """Inputs of ``cache_status``: the launch-record flag, the file's mtime, the run's start."""
    prov = new_tree.get("provenance", {}) if isinstance(new_tree, dict) else {}
    start = None
    try:
        start = datetime.fromisoformat(prov["start_utc"]).timestamp()
    except (KeyError, ValueError, TypeError):
        start = None
    mtime = cache_file.stat().st_mtime if cache_file is not None and cache_file.exists() else None
    return {"flag": flag, "cache_mtime": mtime, "start": start}


def compare_files(new_path: Path, old_path: Path, run_dir: str, manifest_row: str,
                  constants: dict | None = None, table: Table = TABLE,
                  reference_path: Path | None = None, no_reference: bool = False,
                  cache_file: Path | None = None, cache_flag: str | None = None) -> Comparison:
    """Run the whole comparison for two files (and the reference run in branch D).

    Parameters
    ----------
    constants : dict or None
        The approved criterion constants (default ``FALLBACK_CONSTANTS``).
    reference_path : Path or None
        ``results.json`` of the v1 code run locally (D1); compared with the new run by branch B
        then N, and with the pilot by D2.
    no_reference : bool
        Branch D without a reference run: D3.

    Raises
    ------
    ToolError
        On unreadable input; ``Unclassified`` (a ``ToolError``) on a leaf without exactly one rule.
    """
    constants = FALLBACK_CONSTANTS if constants is None else constants
    try:
        old_tree = json.loads(old_path.read_text())
        new_tree = json.loads(new_path.read_text())
    except (OSError, ValueError) as exc:
        raise ToolError(f"cannot read input: {exc}") from exc
    old, new, n_prov = load_sides(old_tree, new_tree)
    results = compare_leaves(old, new, table)
    branch, reasons, obs_differs = select_branch(results, old, new)
    gates = gate_rows(new)
    nrep = drep = None
    if branch == "N":
        nrep = evaluate_n(results, old, new, table, constants, obs_differs)
    elif branch == "D":
        reference = None
        if reference_path is not None:
            reference = compare_files(new_path, reference_path, run_dir, manifest_row, constants,
                                      table, None, False, cache_file, cache_flag)
        drep = evaluate_d(results, old, new, table, constants, gates, reference, no_reference)
    cache = cache_status(cache_info(new_tree, cache_file, cache_flag))
    info = provenance_info(new_tree, old_path, new_path, run_dir, manifest_row)
    info["platform"] = {"new": platform_record(new_tree), "old": platform_record(old_tree)}
    if reference_path is not None:
        try:
            info["platform"]["reference"] = platform_record(json.loads(reference_path.read_text()))
        except (OSError, ValueError):   # branch D raised above; elsewhere the row says so
            info["platform"]["reference"] = {"recorded": False, "why": "reference unreadable"}
    return Comparison(results, old, new, n_prov, branch, reasons, gates, nrep, drep, cache, info,
                      obs_differs)


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
    ap.add_argument("--reference", type=Path, default=None,
                    help="results.json of the v1-baseline code run locally (branch D1)")
    ap.add_argument("--no-reference", action="store_true",
                    help="branch D without a reference run (D3, only if the owner declines D1)")
    ap.add_argument("--cache-file", type=Path, default=None,
                    help="lyapunov.json of the new run (default: <dir of NEW>/cache/lyapunov.json)")
    ap.add_argument("--cache-preexisted", choices=("yes", "no"), default=None,
                    help="from the launch record: did lyapunov.json exist before the run?")
    args = ap.parse_args(argv)
    if args.reference is not None and args.no_reference:
        print("compare_pilot: error: --reference and --no-reference exclude each other",
              file=sys.stderr)
        return EXIT_ERROR
    run_dir = args.run_dir or str(args.new.resolve().parent)
    cache_file = args.cache_file or args.new.resolve().parent / "cache" / "lyapunov.json"
    try:
        cmp = compare_files(args.new, args.old, run_dir, args.manifest_row, FALLBACK_CONSTANTS,
                            reference_path=args.reference, no_reference=args.no_reference,
                            cache_file=cache_file, cache_flag=args.cache_preexisted)
    except ToolError as exc:
        print(f"compare_pilot: error: {exc}", file=sys.stderr)
        return EXIT_ERROR
    for path in (args.report, args.leaves_json):
        path.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(render_report(cmp))
    args.leaves_json.write_text(json.dumps(leaves_json(cmp), indent=1))
    if cmp.dreport is not None and cmp.dreport.d1 is not None:
        sub = args.leaves_json.with_name(args.leaves_json.stem + ".d1.json")
        sub.write_text(json.dumps(leaves_json(cmp.dreport.d1), indent=1))
    code = cmp.exit_code()
    counts = Counter(r.rule.cls for r in cmp.results)
    print(f"compare_pilot: branch {cmp.branch}; "
          + ", ".join(f"{c} {counts[c]}" for c in CLASSES)
          + f"; failures {len(cmp.failures())}; report {args.report}; exit {code}")
    if code == EXIT_NEEDS_INPUT:
        print("compare_pilot: branch D selected (" + "; ".join(cmp.reasons) + "). Give the local "
              "v1 reference run with --reference (D1) or --no-reference (D3).", file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
