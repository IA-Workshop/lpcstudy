"""Tests of ``tools/compare_runs.py``, the reproducibility-tier comparison of two runs (WU-0003.9).

Needs owner review before freeze (the tool decides tolerances and compares verdicts).

References (none of them is the tool's own output):

* **Tier truth table (B2 d1):** the table of plan A6 and B1 item 1, typed here as hand cases on a
  synthetic results tree (one leaf edited at a time).
* **Tolerances (d2):** each rule's number is quoted from the plan (1e-12, 1e-10, 1e-4, 1e-8, ``0.1 hw``,
  the two-proportion bound, ``eta (2 sqrt(c) + eta)``); every case passes at 0.5 x its tolerance and
  fails at 2 x, with the tolerance computed in the test from the plan's formula and the class scale
  decided by hand.
* **Scale classes (M2):** one hand case per class (a) to (g), with the floor chosen so that it binds.
* **10x rule (d3):** ``10^ceil(log10(10 x))`` evaluated by hand at the powers of ten and between them;
  the real kernel pair of WU-0002.14 S3 gave 1e-5 for class (a) and 1e-4 for (b) to (g), which is
  ``docs/agent/notes/2026-10-14-math-wu0003-scripts/m2_floors.log`` (a 164 KB pair, not copied here; the
  evidence run is in the unit Log).
* **TD statistic (d4):** the 18 primary parts of the DEV-0 pilots P0 and P1 (``fixtures/td_p0p1_parts.json``,
  5 KB, extracted from their ``results.json``), against the values printed by the independent script
  ``m1_td_p0p1.py`` in ``m1_td_p0p1.log`` (sum z^2 12.65 and 11.99, max 1.69, two decimals), plus hand
  cases at the 3.4 bound.
* **Real schema (review R10):** ``fixtures/real_schema_extract.json`` (10 KB) is an extract of the real
  ``results.json`` of the WU-0002.14 S3 smoke: the ``handling`` subtree of lorenz63 (one cell, with its LM
  kinds ``oracle``, ``eval``, ``check``, ``totals``, ``fitting``, ``result_counts``), the top-level
  ``handling`` block (``totals``, ``by_system``, ``robustness``, ``failed_variants``) and the
  ``clip_sensitivity`` block (``verdict_2L``, ``status``). The synthetic tree embeds it, so the scope,
  the LM kinds, the sum-over-systems case and the verdict strings are tested on real leaf shapes.
  (B2 d1 asked for fixtures built from the whole 164 KB pair; the main session instructed synthetic
  trees, and the extract is the real-schema part that matters; recorded in the unit Log.)
* **Accounting (d5), read-only, exit codes:** counts decided by construction; file contents hashed before
  and after.

Tolerances. Every comparison of a decision is exact (outcomes, tiers, exit codes). The numeric cases use
the plan's tolerance at factors 0.5 and 2, so round-off (1e-16 relative) never decides a case. The
printed TD sums are compared to the log's two decimals (abs 0.005, the log's rounding). Each test runs in
well under 5 s.
"""

from __future__ import annotations

import ast
import copy
import hashlib
import importlib.util
import json
import math
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools" / "compare_runs.py"
FIXTURE = ROOT / "tests" / "unit" / "fixtures" / "td_p0p1_parts.json"
EXTRACT = json.loads((ROOT / "tests" / "unit" / "fixtures" / "real_schema_extract.json").read_text())
_SPEC = importlib.util.spec_from_file_location("compare_runs", TOOL)
assert _SPEC is not None and _SPEC.loader is not None
cr = importlib.util.module_from_spec(_SPEC)
sys.modules["compare_runs"] = cr
_SPEC.loader.exec_module(cr)

DELETE = object()
Z_LEVEL = 2.39398      # Phi^-1(1 - 0.05/6) = 2.3939798 (log of m1_td_p0p1.py: 2.3940)


def dig(char: str) -> str:
    """A 64-character digest stand-in."""
    return char * 64


def system_block() -> dict:
    """One system of a synthetic results tree (paths and leaf kinds of the real ``results.json``; the
    ``handling`` and ``clip_sensitivity`` subtrees are the real ones)."""
    block = _system_block()
    lm = block["handling"]["cells"]["V3-cp-horizon"]["lm"]
    lm["n_estimates"] = 100                       # the formulas of the tests use n = 100
    pooled = {k: v for k, v in lm.items() if k != "by_kind"}
    for kind in ("oracle", "eval", "check"):      # every kind carries the same numbers (the real oracle and
        lm["by_kind"][kind] = copy.deepcopy(pooled)   # eval kinds are empty in this cell)
    return block


def _system_block() -> dict:
    return {
        "context": {"state_mean_digest": dig("1"), "cov_digest": dig("2"), "whiten_digest": dig("3"),
                    "unwhiten_digest": dig("4"), "main_digest": dig("5"), "estimator_digest": dig("6"),
                    "lambda_max": 0.9, "interval": 0.0333, "obs_scale": 1.5, "delay": 5,
                    "start_state": {"main": [1.0, 2.0, 3.0], "estimator": [4.0, 5.0, 6.0]},
                    "start_index": {"main": 10, "estimator": 20}},
        "validation": {"delay_jacobian_rel_err": 1e-9, "gain_rel_err": 2e-9, "crlb_ratio_min": 0.8,
                       "crlb_ratio_median": 1.0, "crlb_ratio_max": 1.2, "integrator_max_dev_sigma": 1e-6,
                       "cp_median_vpt_lyapunov": 3.0,
                       "estimators": {"('lorenz63', 7, 5, 0.01)": {
                           "weights_digest": dig("e"), "chosen_width": 32, "val_loss_by_width": {"32": 2.0}}}},
        "fitted": {"allocator_digest": dig("a"), "a5_leaf_digest": dig("l"), "chosen_K": 3,
                   "analog_proxy": {"floor": 0.01, "slope": 0.3, "nfev": 12, "status": 1},
                   "estimation_proxy": {"floor": 0.02, "slope": 0.4, "nfev": 9, "status": 1}},
        "H1b": {"CP": {"slope": 2.0, "ci": [1.0, 3.0]}, "PLP": {"slope": 1.0, "ci": [0.5, 1.5]},
                "n_states": 80, "verdict": "not supported", "pass": False},
        "H2a": {"median_range": 0.12, "range_ci": [0.08, 0.16], "n_eligible_states": 70,
                "part_ii": {"zero": {"partial_corr": -0.05, "ci": [-0.25, 0.15]},
                            "interior": {"partial_corr": 0.10, "ci": [-0.10, 0.30]}}},
        "H2b": {"noise": {"mean_state_spearman": 0.25, "ci": [0.10, 0.40]},
                "library_change": {"mean_change": 0.05, "ci": [0.01, 0.09]}},
        "H2c": {"best_single": "A1", "verdict": "supported",
                "A4_minus_A2": {"mean": 0.5, "ci": [0.2, 0.8], "relative": 0.1, "pass": True}},
        "H3c": {"A5_over_A4_mse": 0.9, "ci": [0.6, 1.2], "n_states": 80, "verdict": "inconclusive",
                "reason": "interval spans 1"},
        "H3a": {"chosen_K": 3, "logrank_p_raw": [0.01, 0.2], "n_per_regime": [30, 30, 20]},
        "H2e": {"corr_curve": {"0.01": {"10000": 0.05}}},
        "Q-N": {"oracle": {"logit_w_interior": {"r2_four": 0.4, "r2_three": 0.39, "delta_r2": 0.01,
                                                "ci": [0.0, 0.02]}}},
        "scores": {"A0": {"mse": {"1LT": 0.1}}, "A1": {"mse": {"1LT": 0.2}}, "A*": {"regret": {"1LT": 0.0}}},
        "weight_profile": {"median": [0.5, 0.6]},
        "km_curves": {"A1": [1.0, 0.9, 0.5]},
        "regime_curve": {"realized_K": {"2": 2}},
        "handling": copy.deepcopy(EXTRACT["system_handling"]),
        "clip_sensitivity": copy.deepcopy(EXTRACT["clip_sensitivity"]),
    }


def make(systems: tuple[str, ...] = ("lorenz63",)) -> dict:
    """A fresh synthetic results tree for the given systems (same device, host and threads)."""
    return {
        "config": {"name": "smoke", "seed": 7, "n_test": 80},
        "provenance": {"device": {"backend": "cpu", "kind": "cpu", "count": 1}, "platform": "Linux-test",
                       "cpu": {"model": "TestCPU"}, "env": {"LPC_THREADS": "4"}, "wall_seconds": 1.0},
        "seconds": 5.0,
        "estimators": {"('lorenz63', 7, 5, 0.01)": {
            "chosen_width": 32, "val_loss_by_width": {"32": 2.0}, "weights_digest": dig("e"),
            "seconds": 1.0}},
        "verdicts": {"H3c": {"verdict": "inconclusive", "by_system": {s: "inconclusive" for s in systems}}},
        "robustness": {"lorenz63": {"Lambda_fin(eps=1rho)": {"corr_fin_vs_linear": 0.7}}},
        "handling": {**copy.deepcopy(EXTRACT["top_handling"]),
                     "by_system": {s: copy.deepcopy(EXTRACT["by_system_lorenz63"]) for s in systems}},
        "systems": {s: system_block() for s in systems},
    }


def edit(tree: dict, path: str, value: object) -> dict:
    """Set (or with ``DELETE`` remove) the leaf at the ``/``-joined path (``[i]`` is a list index)."""
    node = tree
    parts = path.split("/")
    for part in parts[:-1]:
        node = node[int(part[1:-1])] if part.startswith("[") else node[part.replace("%2F", "/")]
    last = parts[-1]
    key = int(last[1:-1]) if last.startswith("[") else last.replace("%2F", "/")
    if value is DELETE:
        del node[key]
    else:
        node[key] = value
    return tree


def get(tree: dict, path: str) -> object:
    """The value at a ``/``-joined path."""
    node = tree
    for part in path.split("/"):
        node = node[int(part[1:-1])] if part.startswith("[") else node[part.replace("%2F", "/")]
    return node


S = "systems/lorenz63"
PROV = "provenance/device"
CELL = f"{S}/handling/cells/V3-cp-horizon"


def tier_pair(tier: str, **edits: object) -> tuple[dict, dict]:
    """A (ref, new) pair of the requested tier T1, T2 or T3 (digests set by hand), with extra edits on new."""
    ref, new = make(), make()
    if tier == "T1":
        edit(new, f"{PROV}/backend", "gpu")
        edit(new, f"{PROV}/kind", "gpu")
    elif tier == "T2":
        for name in ("cov_digest", "whiten_digest", "unwhiten_digest"):
            edit(new, f"{S}/context/{name}", dig("9"))
        edit(new, f"{S}/fitted/allocator_digest", dig("8"))
    elif tier == "T3":
        edit(new, f"{S}/fitted/allocator_digest", dig("8"))
    for path, value in edits.items():
        edit(new, path.replace("__", "/"), value)
    return ref, new


def run(ref: dict, new: dict, **kw: object) -> "cr.Comparison":
    """``compare_trees`` with the LM checks that need the dump allowed (they have their own tests)."""
    kw.setdefault("allow_not_computed", True)
    return cr.compare_trees(ref, new, **kw)


def row(res: "cr.Comparison", path: str) -> "cr.Row":
    """The decided row of a leaf path (different or one-sided)."""
    for r in (*res.rows, *res.one_sided):
        if "/".join(r.path) == path:
            return r
    raise AssertionError(f"no row for {path}")


def has_row(res: "cr.Comparison", path: str) -> bool:
    """Whether a leaf path has a row (it differs or is one-sided)."""
    return any("/".join(r.path) == path for r in (*res.rows, *res.one_sided))


# ---------------------------------------------------------------------------------- d1: tier truth table
TD_EDITS = {
    "state_mean_digest": (f"{S}/context/state_mean_digest", dig("9")),
    "lambda_max": (f"{S}/context/lambda_max", 0.9 + 1e-16),
    "interval": (f"{S}/context/interval", 0.0334),
    "start_state_main": (f"{S}/context/start_state/main/[2]", 3.5),
    "start_state_estimator": (f"{S}/context/start_state/estimator/[0]", 4.5),
    "main_digest": (f"{S}/context/main_digest", dig("9")),
    "estimator_digest": (f"{S}/context/estimator_digest", dig("9")),
}


@pytest.mark.parametrize("name", sorted(TD_EDITS))
def test_each_td_trigger_alone_selects_td(name: str) -> None:
    """Each of the six B1 item 1 triggers, alone, gives TD (start_state: main or estimator).

    Reference: the truth table of B1 item 1 (hand cases). Tolerance: exact; ``lambda_max`` differs by one
    ulp (0.9 + 1e-16 is the next double), which must select TD because the comparison is by IEEE bytes.
    """
    ref, new = make(), make()
    assert cr.select_tier(ref, new).name == "T0"
    path, value = TD_EDITS[name]
    edit(new, path, value)
    tier = cr.select_tier(ref, new)
    assert tier.name == "TD"
    assert tier.only_trajectory_digest == (name in ("main_digest", "estimator_digest"))
    assert any(name.split("_")[0] in reason for reason in tier.reasons)


@pytest.mark.parametrize("name", ["whiten_digest", "unwhiten_digest"])
def test_w_or_u_digest_alone_selects_t2(name: str) -> None:
    """A W or U digest alone (the context otherwise equal) gives T2 (A6)."""
    ref, new = make(), make()
    edit(new, f"{S}/context/{name}", dig("9"))
    assert cr.select_tier(ref, new).name == "T2"


def test_cov_digest_alone_matches_no_tier_and_is_undetermined() -> None:
    """R8: ``cov_digest`` differing with W and U equal is in no A6 row. T2 would apply looser LM bands, so the
    pair is undetermined (exit 2, owner reading). With W or U also differing, it is T2 as before."""
    ref, new = make(), make()
    edit(new, f"{S}/context/cov_digest", dig("9"))
    tier = cr.select_tier(ref, new)
    assert tier.name == "undetermined" and "matches no A6 tier" in tier.missing[0]
    assert cr.compare_trees(ref, new).exit_code == 2
    edit(new, f"{S}/context/whiten_digest", dig("9"))
    assert cr.select_tier(ref, new).name == "T2"


@pytest.mark.parametrize("path", [f"{S}/validation/estimators/('lorenz63', 7, 5, 0.01)/weights_digest",
                                  f"{S}/fitted/allocator_digest",
                                  "estimators/('lorenz63', 7, 5, 0.01)/weights_digest"])
def test_a_weight_digest_alone_selects_t3(path: str) -> None:
    """A weight digest alone (validation estimator, allocator, or top-level estimator) gives T3 (A6)."""
    ref, new = make(), make()
    edit(new, path, dig("9"))
    assert cr.select_tier(ref, new).name == "T3"


def test_equal_digests_split_into_t0_and_t1_by_host_device_and_threads() -> None:
    """All digests equal: T0 if host, device and ``LPC_THREADS`` agree, else T1 (A6, strict reading).

    Each of the six facts differing alone gives T1; ``cpu_device`` follows the backend.
    """
    ref = make()
    assert cr.select_tier(ref, make()).name == "T0"
    for path, value in (("provenance/device/backend", "gpu"), ("provenance/device/kind", "gpu"),
                        ("provenance/device/count", 2), ("provenance/platform", "Linux-other"),
                        ("provenance/cpu/model", "OtherCPU"), ("provenance/env/LPC_THREADS", "8")):
        new = edit(make(), path, value)
        tier = cr.select_tier(ref, new)
        assert tier.name == "T1", path
        assert path.split("/", 1)[1].replace("/", ".") in tier.reasons[0]
    both_gpu = [edit(edit(make(), f"{PROV}/backend", "gpu"), f"{PROV}/kind", "gpu") for _ in range(2)]
    assert cr.select_tier(*both_gpu).name == "T0" and not cr.select_tier(*both_gpu).cpu_device


def test_precedence_td_over_t2_over_t3_over_t1() -> None:
    """The pair gets the highest tier of any trigger (and of any system)."""
    ref = make(("lorenz63", "rossler"))
    new = copy.deepcopy(ref)
    edit(new, f"{PROV}/backend", "gpu")
    assert cr.select_tier(ref, new).name == "T1"
    edit(new, "systems/rossler/fitted/allocator_digest", dig("9"))
    assert cr.select_tier(ref, new).name == "T3"
    edit(new, "systems/lorenz63/context/whiten_digest", dig("9"))
    assert cr.select_tier(ref, new).name == "T2"
    edit(new, "systems/rossler/context/main_digest", dig("9"))
    assert cr.select_tier(ref, new).name == "TD"


SELECTING_LEAVES = [f"{S}/context/{n}" for n in ("state_mean_digest", "lambda_max", "interval", "main_digest",
                                                  "estimator_digest", "cov_digest", "whiten_digest",
                                                  "unwhiten_digest")] + [
    f"{S}/context/start_state/main", f"{S}/context/start_state/estimator",
    f"{S}/fitted/allocator_digest", f"{S}/validation/estimators", "estimators"]


@pytest.mark.parametrize("path", SELECTING_LEAVES)
@pytest.mark.parametrize("side", ["ref", "new"])
def test_a_missing_selecting_leaf_is_undetermined_and_exits_2(path: str, side: str) -> None:
    """B1 item 1: a pair in which either run lacks a selecting leaf is undetermined; no tolerance applies.

    Reference: the plan text. The leaf is removed (for a group, its whole subtree) from one run only.
    """
    ref, new = make(), make()
    edit(ref if side == "ref" else new, path, DELETE)
    res = cr.compare_trees(ref, new)
    assert res.tier.name == "undetermined" and res.exit_code == 2 and res.rows == []
    assert res.tier.missing


@pytest.mark.parametrize("path", SELECTING_LEAVES)
def test_a_selecting_leaf_missing_from_both_runs_is_undetermined(path: str) -> None:
    """R7: "either run lacks a selecting leaf" includes a leaf that both lack (for example ``start_state/estimator``
    while ``start_state/main`` is present, ``allocator_digest`` while the validation digests are present, or the
    top-level estimator digests). Reference: the plan text; each leaf group is removed from both runs."""
    ref, new = make(), make()
    edit(ref, path, DELETE)
    edit(new, path, DELETE)
    res = cr.compare_trees(ref, new)
    assert res.tier.name == "undetermined" and res.exit_code == 2 and res.tier.missing


def test_selecting_leaf_set_that_differs_is_undetermined() -> None:
    """A start-state vector of another length is a different leaf set: undetermined, not TD."""
    ref, new = make(), make()
    edit(new, f"{S}/context/start_state/main", [1.0, 2.0])
    assert cr.select_tier(ref, new).name == "undetermined"


def test_missing_provenance_fact_is_undetermined_only_when_it_decides_t0_against_t1() -> None:
    """T0 against T1 needs the host and device facts; TD, T2 and T3 do not."""
    ref, new = make(), make()
    edit(new, "provenance/env/LPC_THREADS", DELETE)
    tier = cr.select_tier(ref, new)
    assert tier.name == "undetermined" and "provenance.env.LPC_THREADS" in tier.missing
    edit(new, f"{S}/context/whiten_digest", dig("9"))
    assert cr.select_tier(ref, new).name == "T2"


def test_no_common_system_is_undetermined() -> None:
    """Runs with no system in common cannot be tiered."""
    assert cr.select_tier(make(("lorenz63",)), make(("rossler",))).name == "undetermined"


# ------------------------------------------------------------------------------------- T0 and TD paths
def test_t0_is_bitwise_and_ignores_timing_and_provenance() -> None:
    """T0 on CPU: equal trees pass; timing and provenance differences are ignored; one ulp, -0.0 and a
    type change each fail (leaves compared by IEEE bytes, as ``leafdiff``)."""
    ref = make()
    new = edit(edit(make(), "seconds", 99.0), "provenance/wall_seconds", 7.0)
    res = run(ref, new)
    assert res.tier.name == "T0" and res.exit_code == 0 and res.rows == []
    for path, value in ((f"{S}/H3c/A5_over_A4_mse", 0.9 + 1.2e-16), (f"{S}/scores/A*/regret/1LT", -0.0),
                        (f"{S}/H3c/n_states", 80.0)):
        res = run(make(), edit(make(), path, value))
        assert res.exit_code == 1 and row(res, path).outcome == "FAIL"
        assert row(res, path).rule == "T0: bitwise"


def test_t0_verdict_flip_prints_a_def_line() -> None:
    """A flag that differs in T0 is labelled DEF (a verdict difference is a DEF, A6)."""
    res = run(make(), edit(make(), f"{S}/H1b/pass", True))
    assert res.exit_code == 1 and row(res, f"{S}/H1b/pass").outcome == "DEF"
    assert any(line.startswith("DEF:") for line in cr.render(res, "a", "b"))


def test_t0_same_non_cpu_device_measures_float_differences_and_keeps_the_rest_exact() -> None:
    """GPU against GPU (R1 against R2): a float difference feeds the 10x rule and is not a failure; an
    integer, a verdict, or an O3 declaration (> 1e-4) is.

    Reference: ROADMAP rule as quoted in A6. Rel 5e-6 on a class (g) leaf declares 1e-4 (10 x 5e-6 =
    5e-5 -> 1e-4), no O3; rel 2e-3 declares 1e-1 (O3).
    """
    gpu = lambda t: edit(edit(t, f"{PROV}/backend", "gpu"), f"{PROV}/kind", "gpu")
    ref = gpu(make())
    res = run(ref, edit(gpu(make()), f"{S}/scores/A1/mse/1LT", 0.2 * (1 + 5e-6)))
    assert res.tier.name == "T0" and res.exit_code == 0
    assert row(res, f"{S}/scores/A1/mse/1LT").outcome == "measured"
    assert res.declared["(b) to (g)"]["declared"] == 1e-4 and not res.declared["(b) to (g)"]["o3"]
    res = run(ref, edit(gpu(make()), f"{S}/scores/A1/mse/1LT", 0.2 * (1 + 2e-3)))
    assert res.exit_code == 1 and res.declared["(b) to (g)"]["o3"]
    assert run(ref, edit(gpu(make()), f"{S}/H3c/n_states", 79)).exit_code == 1
    res = run(ref, gpu(make()))
    assert res.exit_code == 0 and res.declared["(b) to (g)"]["declared"] is None
    assert any("bitwise on the same device type" in ln for ln in cr.render(res, "a", "b"))


# ------------------------------------------------------------------------------- d2: tolerances at 0.5x, 2x
def at(tier: str, path: str, ref_value: float, tol_abs: float, factor: float, **extra: object) -> "cr.Comparison":
    """Compare a pair of tier ``tier`` where ``path`` moves from ``ref_value`` by ``factor * tol_abs``."""
    ref, new = tier_pair(tier, **extra)
    edit(ref, path, ref_value)
    edit(new, path, ref_value + factor * tol_abs)
    return run(ref, new)


# (path, reference value, tolerance in absolute terms computed by hand from the plan's formula)
SHARED_RULES = {
    # A6 T1: cp chain |d| <= 1e-12 |ref|; the chain tag comes from compare_pilot's rule table
    "cp chain": (f"{S}/H1b/CP/slope", 2.0, 1e-12 * 2.0),
    "cp chain (mse)": (f"{S}/scores/A0/mse/1LT", 0.1, 1e-12 * 0.1),
    "oracle chain": ("robustness/lorenz63/Lambda_fin(eps=1rho)/corr_fin_vs_linear", 0.7, 1e-12 * 0.7),
    "fixture chain": (f"{S}/validation/integrator_max_dev_sigma", 1e-6, 1e-12 * 1e-6),
    "dynamics chain": (f"{S}/context/obs_scale", 1.5, 1e-12 * 1.5),
    # V1 |de| <= 1e-12 absolute; V2 <= 1e-10 relative
    "V1 delay": (f"{S}/validation/delay_jacobian_rel_err", 1e-9, 1e-12),
    "V1 gain": (f"{S}/validation/gain_rel_err", 2e-9, 1e-12),
    "V2": (f"{S}/validation/crlb_ratio_median", 1.0, 1e-10),
    # class (a): 1e-4 max(|lo|, |hi|) of the reference interval [0.6, 1.2], for the point and the endpoints
    "QoI point": (f"{S}/H3c/A5_over_A4_mse", 0.9, 1e-4 * 1.2),
    "QoI lo": (f"{S}/H3c/ci/[0]", 0.6, 1e-4 * 1.2),
    "QoI hi": (f"{S}/H3c/ci/[1]", 1.2, 1e-4 * 1.2),
    "QoI H2c": (f"{S}/H2c/A4_minus_A2/mean", 0.5, 1e-4 * 0.8),
    # classes (b) to (g): rel <= tol_other = 1e-4 with the class scale
    "class b": (f"{S}/weight_profile/median/[0]", 0.5, 1e-4 * 0.5),
    "class c": (f"{S}/km_curves/A1/[2]", 0.5, 1e-4 * 0.5),
    "class d": (f"{S}/H2e/corr_curve/0.01/10000", 0.5, 1e-4 * 0.5),
    "class e": (f"{S}/H3a/logrank_p_raw/[1]", 0.2, 1e-4 * 0.2),
    "class f": (f"{S}/Q-N/oracle/logit_w_interior/r2_four", 0.4, 1e-4 * 0.4),
    "class g": (f"{S}/scores/A1/mse/1LT", 0.2, 1e-4 * 0.2),
}


@pytest.mark.parametrize("tier", ["T1", "T2", "T3"])
@pytest.mark.parametrize("name", sorted(SHARED_RULES))
def test_every_shared_rule_passes_at_half_its_tolerance_and_fails_at_double(tier: str, name: str) -> None:
    """A6 and B1 items 4, 5: each tolerance of T1 to T3 passes at 0.5 x and fails at 2 x.

    Reference: the plan's numbers, evaluated by hand in ``SHARED_RULES`` (a tolerance is the number times
    the class scale; for (b) to (g) the scale is |ref| here because every reference exceeds its floor).
    Tolerance: factors 0.5 and 2 leave a factor-of-two margin around round-off (1e-16 relative).
    """
    path, value, tol = SHARED_RULES[name]
    low = at(tier, path, value, tol, 0.5)
    assert row(low, path).outcome == "pass", (name, row(low, path))
    assert low.exit_code == 0
    high = at(tier, path, value, tol, 2.0)
    assert row(high, path).outcome in ("FAIL", "FINDING") and high.exit_code == 1


def test_class_b_to_g_exceedance_is_a_finding_and_a_or_chain_exceedance_a_failure() -> None:
    """Outcome names: a (b) to (g) exceedance is a listed FINDING (B1 item 4), the others FAIL."""
    assert row(at("T1", *SHARED_RULES["class g"], 2.0), SHARED_RULES["class g"][0]).outcome == "FINDING"
    assert row(at("T1", *SHARED_RULES["QoI point"], 2.0), SHARED_RULES["QoI point"][0]).outcome == "FAIL"
    assert row(at("T1", *SHARED_RULES["cp chain"], 2.0), SHARED_RULES["cp chain"][0]).outcome == "FAIL"


def test_tol_other_replaces_the_class_tolerance_of_b_to_g_only() -> None:
    """``--tol-other`` (the R1/R2 declaration) sets (b) to (g); the A6 numbers of the other rules stay."""
    path, value, _ = SHARED_RULES["class g"]
    ref, new = tier_pair("T1")
    edit(new, path, value * (1 + 5e-5))
    assert run(ref, new, tol_other=1e-4).exit_code == 0
    assert run(ref, new, tol_other=1e-5).exit_code == 1
    path, value, _ = SHARED_RULES["QoI point"]
    edit(new, f"{S}/scores/A1/mse/1LT", 0.2)
    edit(new, path, value + 2e-4 * 1.2)
    assert run(ref, new, tol_other=1e-4).exit_code == 1          # the A6 QoI rule is not an option


def test_tol_other_above_the_o3_ceiling_is_refused() -> None:
    """R4: a class tolerance above 1e-4 is an O3 finding that A6 does not let the tool adopt: ``compare_trees``
    raises, the command line exits 2 with a message, and nothing prints PASS. The ceiling itself is accepted."""
    ref, new = tier_pair("T1", **{f"{S}__scores__A1__mse__1LT": 0.3})
    for bad in (1.0, 1e-3, 1.0000001e-4):
        with pytest.raises(cr.ToolError):
            run(ref, new, tol_other=bad)
    assert run(ref, new, tol_other=1e-4).exit_code == 1
    for bad in (0.0, -1e-5, math.nan):
        with pytest.raises(cr.ToolError):
            run(ref, new, tol_other=bad)


# ---- scale classes: the floor binds (M2)
FLOOR_CASES = {
    # path, ref value, class, scale s by hand
    "a": (f"{S}/H3c/A5_over_A4_mse", 0.9, "a", 1.2),                       # max(|lo|, |hi|) of [0.6, 1.2]
    "b": (f"{S}/weight_profile/median/[0]", 0.001, "b", 0.01),             # max(|ref|, 0.01)
    "c": (f"{S}/km_curves/A1/[2]", 0.001, "c", 1 / 80),                    # max(|ref|, 1/n), n = n_test = 80
    "d": (f"{S}/H2e/corr_curve/0.01/10000", 0.05, "d", 1 / math.sqrt(80)),  # max(|ref|, 1/sqrt n)
    "e": (f"{S}/H3a/logrank_p_raw/[0]", 0.0001, "e", 1e-3),                 # max(|ref|, 1e-3)
    "f": (f"{S}/Q-N/oracle/logit_w_interior/r2_four", 0.004, "f", 0.01),    # max(|ref|, 0.01)
    "g": (f"{S}/scores/A1/mse/1LT", 0.2, "g", 0.2),                         # |ref|
}


@pytest.mark.parametrize("letter", sorted(FLOOR_CASES))
def test_scale_class_rel_is_delta_over_the_hand_scale(letter: str) -> None:
    """M2, one hand case per class: ``rel = |d| / s`` with ``s`` decided by hand, the floor binding.

    Reference: the class table of B1 item 4. Tolerance: relative 1e-9 on the quotient: the difference of two
    doubles near 1 has an absolute error of one ulp (1.1e-16), i.e. 4e-11 relative to a delta of 3e-6.
    """
    path, value, cls, scale = FLOOR_CASES[letter]
    ref, new = tier_pair("T3")
    edit(ref, path, value)
    delta = 3e-6
    edit(new, path, value + delta)
    r = row(run(ref, new), path)
    assert r.cls == cls
    assert r.rel == pytest.approx(delta / scale, rel=1e-9)


def test_class_a_endpoint_uses_the_reference_interval_scale_and_zero_interval_needs_exact_equality() -> None:
    """Class (a) endpoints share the interval's scale; if lo = hi = 0 any difference is infinite rel."""
    ref, new = tier_pair("T3")
    edit(new, f"{S}/H3c/ci/[0]", 0.6 + 6e-5)
    r = row(run(ref, new), f"{S}/H3c/ci/[0]")
    assert r.cls == "a" and r.rel == pytest.approx(6e-5 / 1.2, rel=1e-9)
    edit(ref, f"{S}/H3c/ci", [0.0, 0.0])
    edit(ref, f"{S}/H3c/A5_over_A4_mse", 0.0)
    edit(new, f"{S}/H3c/ci", [0.0, 0.0])
    edit(new, f"{S}/H3c/A5_over_A4_mse", 1e-30)
    r = row(run(ref, new), f"{S}/H3c/A5_over_A4_mse")
    assert r.rel == math.inf and r.outcome == "FAIL"


def test_class_g_exact_zero_requires_equality() -> None:
    """(g): a leaf that is exactly 0 in the reference (A* regret) must stay 0; 1e-30 fails (rel infinite)."""
    ref, new = tier_pair("T1", **{f"{S}__scores__A*__regret__1LT": 1e-30})
    r = row(run(ref, new), f"{S}/scores/A*/regret/1LT")
    assert r.rel == math.inf and r.outcome == "FINDING"


def test_every_float_leaf_without_a_rule_is_counted_in_the_default_class() -> None:
    """A float leaf that no class names lands in (g) with the ``defaulted`` flag, and is counted."""
    ref, new = tier_pair("T3")
    edit(ref, f"{S}/novel_block", {"x": 1.0})
    edit(new, f"{S}/novel_block", {"x": 1.0000001})
    r = row(run(ref, new), f"{S}/novel_block/x")
    assert r.cls == "g" and r.defaulted
    assert run(ref, new).declared["(b) to (g)"]["defaulted"] >= 1


# ---- LM rules
def lm_path(name: str, kind: str | None = None) -> str:
    """The LM summary leaf of the V3 cell: the pooled block, or one of the kinds ``oracle``, ``eval``, ``check``."""
    return f"{CELL}/lm/" + (f"by_kind/{kind}/" if kind else "") + name


def lm_at(tier: str, name: str, ref_value: float, new_value: float, kind: str | None = None) -> "cr.Comparison":
    """One LM summary (pooled or of a kind) moved from ``ref_value`` to ``new_value``."""
    ref, new = tier_pair(tier)
    edit(ref, lm_path(name, kind), ref_value)
    edit(new, lm_path(name, kind), new_value)
    return run(ref, new)


def test_t1_lm_summaries_exact_fraction_iterations_within_one_other_relative_1e_8() -> None:
    """T1 (A6 and WU-0005.4 M7(i)): ``fraction_no_decrease`` exact; ``median_iterations`` within 1 (0.5 passes,
    2 fails); ``median_residual`` within 1e-8 relative (0.5 x passes, 2 x fails). Real LM leaf shapes."""
    p = lm_path
    assert row(lm_at("T1", "fraction_no_decrease", 0.04, 0.04 + 1e-15), p("fraction_no_decrease")).outcome == "FAIL"
    assert row(lm_at("T1", "median_iterations", 8.0, 8.5), p("median_iterations")).outcome == "pass"
    assert row(lm_at("T1", "median_iterations", 8.0, 10.0), p("median_iterations")).outcome == "FAIL"
    assert row(lm_at("T1", "median_residual", 0.5, 0.5 * (1 + 0.5e-8)), p("median_residual")).outcome == "pass"
    assert row(lm_at("T1", "median_residual", 0.5, 0.5 * (1 + 2e-8)), p("median_residual")).outcome == "FAIL"


def solve_move(p_ref: float, factor: float) -> float:
    """The move m with m = factor x bound(p_ref + m/2), the bound ``3 sqrt(2 pbar (1 - pbar)/100) + 1/100`` at
    pbar = p_ref + m/2 (the tool's pbar is the mean of the two fractions). Solved by fixed-point iteration;
    the map is a contraction here (slope about 0.1 for factor 0.5 and 0.3 for factor 2)."""
    bound = lambda pbar: 3 * math.sqrt(2 * pbar * (1 - pbar) / 100) + 1 / 100
    m = 0.1
    for _ in range(200):
        m = factor * bound(p_ref + m / 2)
    assert m == pytest.approx(factor * bound(p_ref + m / 2), rel=1e-14)
    return m


@pytest.mark.parametrize("tier", ["T2", "T3"])
def test_t2_rules_fraction_no_decrease_uses_the_two_proportion_bound(tier: str) -> None:
    """M7(ii): ``|d| <= 3 sqrt(2 pbar (1 - pbar) / n) + 1/n``, n = n_estimates = 100, for T2 on every kind and
    for T3 on the ``eval`` kind.

    Reference: the formula by hand; the moves are solved for exactly 0.5 x and 2 x the bound from p_ref = 0.10
    (R11): m = 0.5 bound(0.10 + m/2) (m = 0.0784) and m = 2 bound(0.10 + m/2) (m = 0.4108). Tolerance: the tool's |b - a| carries one
    ulp (1e-16) on a move of 0.08 to 0.45, so the ratios are 0.5 and 2 to 1e-9.
    """
    p = lm_path("fraction_no_decrease", "eval")
    half, double = solve_move(0.10, 0.5), solve_move(0.10, 2.0)
    # hand check of the fixed points: m = 0.07843, pbar = 0.13922, bound = 3 sqrt(2 x 0.13922 x 0.86078 / 100) + 0.01
    # = 0.15687 = 2 m; and m = 0.41081, pbar = 0.30541, bound = 0.20541 = m / 2 (digits typed from that hand calculation)
    assert half == pytest.approx(0.07843, abs=1e-5) and double == pytest.approx(0.41081, abs=1e-5)
    res = lm_at(tier, "fraction_no_decrease", 0.10, 0.10 + half, "eval")
    assert row(res, p).outcome == "pass" and row(res, p).metric / row(res, p).tol == pytest.approx(0.5, rel=1e-9)
    res = lm_at(tier, "fraction_no_decrease", 0.10, 0.10 + double, "eval")
    assert row(res, p).outcome == "FAIL" and row(res, p).metric / row(res, p).tol == pytest.approx(2.0, rel=1e-9)


def test_t3_keeps_the_t1_lm_rules_for_the_oracle_and_check_kinds_and_the_pooled_summary() -> None:
    """R3: A6 T3 is "network chain as T2; other chains as T1". With only the weights differing, a one-ulp move of
    ``fraction_no_decrease`` fails (T1: exact) in the pooled block and the ``oracle`` and ``check`` kinds, passes in
    the ``eval`` kind (T2 band) and in every kind under T2. Likewise a 2e-8 relative move of ``median_residual``
    fails under the T1 rules and is NOT COMPUTED (order-statistic band) under the T2 rules."""
    for kind, t3_outcome in ((None, "FAIL"), ("oracle", "FAIL"), ("check", "FAIL"), ("eval", "pass")):
        path = lm_path("fraction_no_decrease", kind)
        assert row(lm_at("T3", "fraction_no_decrease", 0.04, 0.04 + 1e-15, kind), path).outcome == t3_outcome, kind
        assert row(lm_at("T2", "fraction_no_decrease", 0.04, 0.04 + 1e-15, kind), path).outcome == "pass", kind
    mr = lambda kind: lm_path("median_residual", kind)
    assert row(lm_at("T3", "median_residual", 0.5, 0.5 * (1 + 2e-8), "oracle"), mr("oracle")).outcome == "FAIL"
    assert row(lm_at("T3", "median_residual", 0.5, 0.5 * (1 + 2e-8), "eval"), mr("eval")).outcome == "NOT COMPUTED"
    assert row(lm_at("T2", "median_residual", 0.5, 0.5 * (1 + 2e-8), "oracle"), mr("oracle")).outcome == "NOT COMPUTED"


@pytest.mark.parametrize("tier", ["T2", "T3"])
def test_t2_rules_other_lm_fractions_keep_class_c_and_print_the_band(tier: str) -> None:
    """``fraction_above_chi2`` (eval kind) has no T2 tolerance in A6: class (c) applies (strict), and the band is
    printed as information."""
    r = row(lm_at(tier, "fraction_above_chi2", 0.02, 0.03, "eval"), lm_path("fraction_above_chi2", "eval"))
    assert r.cls == "c" and r.outcome == "FINDING" and "two-proportion band" in r.note


def test_median_iterations_is_excluded_from_the_10x_maximum() -> None:
    """The note (M2 (h)) excludes the integer-valued ``median_iterations`` from the 10x maximum."""
    res = lm_at("T1", "median_iterations", 8.0, 9.0)
    assert res.declared["(b) to (g)"]["n"] == 0


def test_lm_checks_that_need_the_dump_are_not_computed_and_exit_2_unless_allowed() -> None:
    """T1 per-estimate check and T2/T3 order-statistic bands need the .7b dump: reported as NOT COMPUTED;
    exit 2 by default, and 0 with ``--allow-not-computed`` (a pair without a failure)."""
    for tier, text in (("T1", "per-estimate"), ("T2", "order-statistic"), ("T3", "order-statistic")):
        ref, new = tier_pair(tier)
        res = cr.compare_trees(ref, new)
        assert res.exit_code == 2 and any(text in item for item in res.not_computed)
        assert run(ref, new).exit_code == 0
        assert "NOT COMPUTED:" in "\n".join(cr.render(res, "a", "b"))
    ref, new = tier_pair("T1", **{f"{S}__scores__A1__mse__1LT": 0.3})
    assert cr.compare_trees(ref, new).exit_code == 1            # a failure outranks "not computed"
    ref, new = make(), make()
    assert cr.compare_trees(ref, new).exit_code == 0            # T0 needs no dump


# ---- discrete counts
def scope_case(count_edits: dict, leaf: str = f"{S}/H3c/A5_over_A4_mse", ref_value: float = 0.9,
               factor: float = 0.5, tier: str = "T1") -> "cr.Comparison":
    """H3c's estimate moves by ``factor`` x 0.1 hw (hw = 0.3) while the given counts differ."""
    ref, new = tier_pair(tier, **count_edits)
    edit(ref, leaf, ref_value)
    edit(new, leaf, ref_value + factor * 0.1 * 0.3)
    return run(ref, new)


@pytest.mark.parametrize("counts", [
    {f"{S}__H3c__n_states": 79},                                   # a state count of the block
    {f"{S}__fitted__chosen_K": 4},                                 # K reaches H3c
    {f"{CELL}__counts__error_clips": 3},                           # a clip count reaches the whole system
    {f"{CELL}__by_kind__oracle__counts__error_clips_cp": 2},       # clip counters of any name starting error_clips
    {f"{CELL}__counts__invariant_mean_replacements": 1},           # a replacement count
])
def test_a_discrete_count_of_the_scope_licenses_0_1_hw_and_not_more(counts: dict) -> None:
    """A6: in a block where a discrete count differs, ``|d| <= 0.1 hw`` replaces the tolerance.

    Reference: hw = (1.2 - 0.6)/2 = 0.3 of the reference interval, so 0.1 hw = 0.03; 0.5 x passes and 2 x
    fails. The same move without a differing count fails (the QoI rule 1e-4 x 1.2 = 1.2e-4).
    """
    path = f"{S}/H3c/A5_over_A4_mse"
    assert row(scope_case(counts), path).outcome == "pass"
    assert row(scope_case(counts, factor=2.0), path).outcome == "FAIL"
    assert row(scope_case({}), path).outcome == "FAIL"


def test_scope_is_causal_not_global() -> None:
    """A state count of H3c does not license H2c; K licenses H3c but not H2c; ``best_single`` licenses H2c
    only (also not H3c)."""
    h2c = f"{S}/H2c/A4_minus_A2/mean"          # hw = 0.3
    assert row(scope_case({f"{S}__H3c__n_states": 79}, h2c, 0.5), h2c).outcome == "FAIL"
    assert row(scope_case({f"{S}__fitted__chosen_K": 4}, h2c, 0.5), h2c).outcome == "FAIL"
    assert row(scope_case({f"{S}__H2c__best_single": "A2"}, h2c, 0.5), h2c).outcome == "pass"
    assert row(scope_case({f"{S}__H2c__best_single": "A2"}), f"{S}/H3c/A5_over_A4_mse").outcome == "FAIL"


def two_system_pair(**edits: object) -> "cr.Comparison":
    """Two systems, device differs (T1); both systems' H3c estimate moves by 0.5 x 0.1 hw (= 0.015) and the given
    leaves (paths with ``__`` for ``/``) are edited on the new run."""
    ref, new = make(("lorenz63", "rossler")), make(("lorenz63", "rossler"))
    edit(new, f"{PROV}/backend", "gpu")
    for system in ("lorenz63", "rossler"):
        edit(new, f"systems/{system}/H3c/A5_over_A4_mse", 0.915)
    for path, value in edits.items():
        edit(new, path.replace("__", "/"), value)
    return run(ref, new)


def test_a_clip_count_licenses_its_own_system_only_and_a_total_licenses_nothing() -> None:
    """R1, the sum-over-systems probe (real ``handling`` shapes). ``handling/totals`` and ``by_system`` are sums
    or mirrors of the per-system counts: if rossler's clip count rises by 1, its cell, its per-system totals, the
    top-level ``by_system/rossler`` and the top-level ``totals`` all differ.

    * rossler's H3c move (0.015 = 0.5 x 0.1 hw) passes (its own cell count licenses it); lorenz63's, whose
      counts did not move, fails (a ``None`` system must not match every system);
    * the mirrors are listed and open no scope: with only the mirrors moved, neither system is licensed.
    """
    h3c = lambda s: f"systems/{s}/H3c/A5_over_A4_mse"
    cell = "systems/rossler/handling/cells/V3-cp-horizon/counts/error_clips"
    full = two_system_pair(**{cell: 1, "systems__rossler__handling__totals__error_clips": 1,
                              "handling__by_system__rossler__error_clips": 1, "handling__totals__error_clips": 1})
    assert row(full, h3c("rossler")).outcome == "pass" and row(full, h3c("lorenz63")).outcome == "FAIL"
    for mirror in ("handling/totals/error_clips", "handling/by_system/rossler/error_clips",
                   "systems/rossler/handling/totals/error_clips"):
        assert row(full, mirror).outcome == "listed" and "opens no scope" in row(full, mirror).note
    assert row(full, cell).outcome == "listed" and "opens no scope" not in row(full, cell).note
    only = two_system_pair(**{"handling__totals__error_clips": 1, "handling__by_system__rossler__error_clips": 1,
                              "systems__rossler__handling__totals__error_clips": 1})
    assert row(only, h3c("rossler")).outcome == "FAIL" and row(only, h3c("lorenz63")).outcome == "FAIL"


@pytest.mark.parametrize("path", [
    f"{CELL}/counts/zero_variance_corr", f"{CELL}/counts/lm_nonfinite_cost", f"{CELL}/counts/gain_floor",
    f"{CELL}/denominators/estimates", f"{CELL}/lm/n_estimates", f"{CELL}/lm/nonfinite_residuals",
    f"{CELL}/lm/gof_dof", f"{S}/handling/fitting/counts/empty_regime_fallback",
    f"{S}/handling/fitting/denominators/pools", f"{S}/handling/result_counts/H3c%2Fn_failed_resamples",
    f"{S}/handling/result_counts/gain_bound%2Fn_screened_out%2Fnegative_covariance",
    f"{S}/handling/result_counts/H1a%2Fn_excluded_nonfinite", "handling/failed_variants"])
def test_other_integers_are_not_licensing_counts_and_fail(path: str) -> None:
    """R1: a differing integer that is not on A6's list (other ``handling`` counters, denominators other than the
    states, LM ``n_estimates``, non-finite, fallback, warning and failed-resample counts) is exact: FAIL, and it
    licenses nothing (H3c at 0.5 x 0.1 hw still fails). Reference: A6's list as quoted in the plan."""
    ref, new = tier_pair("T1")
    edit(new, path, get(ref, path) + 1)
    edit(new, f"{S}/H3c/A5_over_A4_mse", 0.915)
    res = run(ref, new)
    assert row(res, path).outcome == "FAIL" and row(res, f"{S}/H3c/A5_over_A4_mse").outcome == "FAIL"


def test_state_denominator_and_top_level_counts_are_listed_without_a_scope() -> None:
    """The state denominator is on A6's list (``n_states``) but, like the top-level ``handling`` sums, opens no
    scope; it is listed, not failed."""
    for path in (f"{CELL}/denominators/states", "handling/totals/nu_cap_clips"):
        ref, new = tier_pair("T1")
        edit(new, path, get(ref, path) + 1)
        edit(new, f"{S}/H3c/A5_over_A4_mse", 0.915)
        res = run(ref, new)
        assert row(res, path).outcome == "listed" and row(res, f"{S}/H3c/A5_over_A4_mse").outcome == "FAIL"


def test_only_k_reaches_the_k_shaped_leaves() -> None:
    """R1: an integer of ``H3a`` (``n_per_regime``) or ``regime_curve`` that differs is exact unless K differs in
    its system, when it is listed as following K; it is never a licensing count itself."""
    path = f"{S}/H3a/n_per_regime/[0]"
    res = run(*tier_pair("T1", **{path.replace("/", "__"): 31}))
    assert row(res, path).outcome == "FAIL"
    res = run(*tier_pair("T1", **{path.replace("/", "__"): 31, f"{S}__fitted__chosen_K": 4}))
    assert row(res, path).outcome == "listed" and row(res, path).rule == "follows a differing K"
    other = f"{S}/regime_curve/realized_K/2"
    res = run(*tier_pair("T1", **{other.replace("/", "__"): 3}))
    assert row(res, other).outcome == "listed"                       # realized_K is K itself


@pytest.mark.parametrize("path", [f"{S}__fitted__analog_proxy__nfev", f"{S}__fitted__analog_proxy__status",
                                  f"{S}__fitted__a5_leaf_digest"])
def test_new_integers_are_listed_and_license_nothing(path: str) -> None:
    """B1 item 3 and OF-1: a difference in ``nfev``, ``status`` or the A5 leaf digest is printed (not a
    failure) and does not license the 0.1 hw exception (H3c at 0.5 x 0.1 hw still fails)."""
    value = dig("z") if path.endswith("digest") else 99
    res = scope_case({path: value})
    leaf = row(res, path.replace("__", "/"))
    assert leaf.outcome == "listed" and leaf.cls == "chain head"
    assert row(res, f"{S}/H3c/A5_over_A4_mse").outcome == "FAIL"


def test_integer_leaf_outside_the_exception_list_is_exact() -> None:
    """``chosen_width`` is not on the A6 list of counts: a difference fails (exact)."""
    path = f"{S}/validation/estimators/('lorenz63', 7, 5, 0.01)/chosen_width"
    res = run(*tier_pair("T1", **{path.replace("/", "__"): 64}))
    assert row(res, path).outcome == "FAIL" and res.exit_code == 1


def test_fitted_proxy_coefficients_are_reported_with_no_tolerance() -> None:
    """The tolerance-stopped fit's coefficients (chain heads) are reported (M2 (h)), never failed."""
    path = f"{S}/fitted/analog_proxy/floor"
    res = run(*tier_pair("T3", **{path.replace("/", "__"): 0.0100001}))
    assert row(res, path).outcome == "reported" and res.exit_code == 0
    assert res.declared["(b) to (g)"]["n"] == 0


# ---- verdicts, categorical leaves, structure, config
def test_a_verdict_difference_is_a_def_in_t1_to_t3_and_only_reported_in_td() -> None:
    """A6: every verdict identical in T1 to T3 (DEF line, exit 1); in TD verdicts are reported."""
    for tier in ("T1", "T2", "T3"):
        for path, value in ((f"{S}/H3c/verdict", "supported"), (f"{S}/H1b/pass", True),
                            ("verdicts/H3c/verdict", "supported"),
                            ("verdicts/H3c/by_system/lorenz63", "supported")):
            res = run(*tier_pair(tier, **{path.replace("/", "__"): value}))
            assert row(res, path).outcome == "DEF" and res.exit_code == 1
            assert any(ln.startswith("DEF:") and path in ln for ln in cr.render(res, "a", "b"))
    ref, new = td_pair()
    edit(new, f"{S}/H3c/verdict", "supported")
    res = run(ref, new)
    assert res.tier.name == "TD" and res.exit_code == 0
    assert row(res, f"{S}/H3c/verdict").outcome == "reported"
    assert "verdict-type leaves differ" in "\n".join(cr.render(res, "a", "b"))


def test_non_verdict_text_and_a_type_change_fail_exactly() -> None:
    """A text leaf that is not a verdict, and a float that became an int, have no tolerance: FAIL."""
    res = run(*tier_pair("T1", **{f"{S}__H3c__reason": "other"}))
    assert row(res, f"{S}/H3c/reason").outcome == "FAIL"
    res = run(*tier_pair("T1", **{f"{S}__scores__A1__mse__1LT": 1}))
    assert row(res, f"{S}/scores/A1/mse/1LT").outcome == "FAIL" and row(res, f"{S}/scores/A1/mse/1LT").kind == "type"


def test_one_sided_leaves_fail_unless_a_count_of_their_block_explains_the_shape() -> None:
    """A leaf on one run only is a FAIL; the length of a K-shaped list that follows a differing K is listed."""
    res = run(*tier_pair("T1", **{f"{S}__H3c__extra": 1.0}))
    assert row(res, f"{S}/H3c/extra").outcome == "FAIL" and res.exit_code == 1
    ref, new = tier_pair("T1", **{f"{S}__fitted__chosen_K": 4, f"{S}__H3a__chosen_K": 4})
    edit(new, f"{S}/H3a/logrank_p_raw", [0.01, 0.2, 0.3])
    res = run(ref, new)
    assert row(res, f"{S}/H3a/logrank_p_raw/[2]").outcome == "listed" and res.exit_code == 0


def test_config_must_be_identical_except_the_seed_in_td() -> None:
    """A changed config is a different experiment: FAIL in every tier; in TD only seed and seed_id are
    listed instead (the realizations differ by design)."""
    res = run(*tier_pair("T1", **{"config__n_test": 81}))
    assert row(res, "config/n_test").outcome == "FAIL" and res.exit_code == 1
    ref, new = td_pair()
    edit(new, "config/seed", 8)
    assert row(run(ref, new), "config/seed").outcome == "listed"
    edit(new, "config/n_test", 81)
    assert run(ref, new).exit_code == 1


# ---- round 2: H1a fit outputs, OF-7 pointer, untagged census
H1A = f"{S}/H1a/by_noise/0.01"


def with_h1a(tree: dict, **leaves: object) -> dict:
    """Add an ``H1a`` block shaped like the real one (fit outputs, ``ratio`` and its interval, the seeds by n_lib)."""
    block = {"by_noise": {"0.01": {"fitted_inverse_dim": 0.55, "ci_inverse_dim": [0.48, 0.65], "floor_rms": 0.03,
                                   "ratio": 1.09, "ratio_ci": [0.96, 1.3],
                                   "median_seed_by_n_lib": {"1000": 0.16, "10000": 0.14}}},
             "inverse_dim_reference": 0.6, "n_states": 80, "verdict": "inconclusive"}
    tree["systems"]["lorenz63"]["H1a"] = block
    for path, value in leaves.items():
        edit(tree, path.replace("__", "/"), value)
    return tree


@pytest.mark.parametrize("tier", ["T1", "T2", "T3"])
@pytest.mark.parametrize("path, value", [
    (f"{S}/H1a/inverse_dim_reference", 0.6), (f"{H1A}/median_seed_by_n_lib/1000", 0.16),
    (f"{H1A}/median_seed_by_n_lib/10000", 0.14)])
def test_cp_rule_applies_to_the_untagged_h1a_leaves(tier: str, path: str, value: float) -> None:
    """Round 2, item 2: ``inverse_dim_reference`` and ``median_seed_by_n_lib/*`` are untagged in compare_pilot's
    table but are cp-chain outputs of H1a: the strict 1e-12 relative rule applies. 0.5 x passes, 2 x fails
    (a move of 1e-12 |ref| x factor; before the change they got the (b) to (g) class tolerance 1e-4)."""
    low = tier_pair(tier)
    for tree in low:
        with_h1a(tree)
    edit(low[1], path, value * (1 + 0.5e-12))
    r = row(run(*low), path)
    assert r.outcome == "pass" and r.rule == "cp chain relative" and r.tol == 1e-12
    high = tier_pair(tier)
    for tree in high:
        with_h1a(tree)
    edit(high[1], path, value * (1 + 2e-12))
    assert row(run(*high), path).outcome == "FAIL"


def test_failures_of_the_h1a_ratio_keep_the_cp_rule_and_print_the_of7_pointer_with_an_unchanged_exit() -> None:
    """Round 2, item 1, extended by WU-0003.9b fix round 1 (review R1), SUPERSEDED IN PART by WU-0003.9c (owner ruling
    OF-7 of 2026-10-18, note 33): the four H1a fit leaves ``fitted_inverse_dim``, ``ci_inverse_dim/[0|1]`` and
    ``floor_rms`` are re-tagged under the A6 QoI rule, so a move of 1e-7 relative (the size on the S3 kernel pair)
    now PASSES for them and carries no pointer (it FAILED, with the pointer, before). The ruling names those four
    only: ``ratio`` and ``ratio_ci`` (the same ``curve_fit``) keep cp 1e-12 and the pointer, so a 1e-7 move of them
    still FAILS (exit 1, nothing else loosened). The pointer is on three leaves per (system, rho). A failure outside
    ``H1a/by_noise`` carries none; a pass carries none."""
    ref, new = tier_pair("T2")
    for tree in (ref, new):
        with_h1a(tree)
    for leaf, value in (("fitted_inverse_dim", 0.55), ("floor_rms", 0.03), ("ratio", 1.09)):
        edit(new, f"{H1A}/{leaf}", value * (1 + 1e-7))
    edit(new, f"{H1A}/ci_inverse_dim/[0]", 0.48 * (1 + 1e-7))
    edit(new, f"{H1A}/ratio_ci/[0]", 0.96 * (1 + 1e-7))
    edit(new, f"{H1A}/ci_inverse_dim/[1]", 0.65 * (1 + 1e-7))
    edit(new, f"{H1A}/ratio_ci/[1]", 1.3 * (1 + 1e-7))
    res = run(ref, new)
    # three leaves per (system, rho) carry the pointer: 3 systems x 2 rho x 3 = 18 per pilot T2 pair (42 before the
    # ruling, 24 of them the four leaves that are now re-tagged)
    assert sum(cr.OF7_POINTER in r.note for r in res.rows) == 3
    for leaf in ("fitted_inverse_dim", "floor_rms", "ci_inverse_dim/[0]", "ci_inverse_dim/[1]"):
        r = row(res, f"{H1A}/{leaf}")
        assert r.outcome == "pass" and cr.OF7_POINTER not in r.note, leaf
    for leaf in ("ratio", "ratio_ci/[0]", "ratio_ci/[1]"):
        r = row(res, f"{H1A}/{leaf}")
        assert r.outcome == "FAIL" and cr.OF7_POINTER in r.note and "2026-10-14-math-wu0003-9-q1.md" in r.note
    assert res.exit_code == 1
    text = "\n".join(cr.render(res, "a", "b"))
    assert text.count("pointer: " + cr.OF7_POINTER) == 1
    for leaf, value in (("median_seed_by_n_lib/1000", 0.16),):                  # R15: not an OF-7 leaf
        edit(new, f"{H1A}/{leaf}", value * (1 + 1e-3))
    res = run(ref, new)
    for leaf in ("median_seed_by_n_lib/1000",):
        r = row(res, f"{H1A}/{leaf}")
        assert r.outcome == "FAIL" and cr.OF7_POINTER not in r.note, leaf
    ref, new = tier_pair("T2", **{f"{S}__H1b__CP__slope": 2.0 * (1 + 1e-7)})
    res = run(ref, new)
    assert row(res, f"{S}/H1b/CP/slope").outcome == "FAIL" and cr.OF7_POINTER not in row(res, f"{S}/H1b/CP/slope").note
    assert "pointer:" not in "\n".join(cr.render(res, "a", "b"))


def test_untagged_census_counts_hand_known_leaves_and_the_report_prints_it() -> None:
    """Round 2, item 3, rewritten for WU-0003.9b (plan amendment 3 C4): the census counts float leaves without a
    chain tag, by block, and the report prints it. An untagged float leaf is NOT COMPUTABLE (exit 2).

    Reference: a tree of six floats whose tags are known by hand. ``H1b/CP/slope`` is cp and ``H3c/A5_over_A4_mse``
    network (``compare_pilot``'s table); ``H2e/corr_curve/..`` and ``scores/A*/regret/1LT`` are tagged by override
    since WU-0003.9b (they were the untagged examples of round 2); ``config`` is an override too; ``novel_block/x`` is
    in no table. Integers and strings are not counted. The round-2 version of this test expected ``{"H2e": 1,
    "scores": 1}`` and a census that was "information, not a failure"; both are what C4 retires."""
    flat = cr.flatten({"config": {"n_test": 1.0}, "systems": {"lorenz63": {
        "H1b": {"CP": {"slope": 1.0}}, "H3c": {"A5_over_A4_mse": 0.9, "n_states": 80},
        "H2e": {"corr_curve": {"0.01": {"10000": 0.05}}}, "scores": {"A*": {"regret": {"1LT": 0.0}}},
        "novel_block": {"x": 1.0}}}})
    assert cr.untagged_census(flat) == {"novel_block": 1}
    ref, new = tier_pair("T3")
    edit(ref, f"{S}/novel_block", {"x": 1.0})
    edit(new, f"{S}/novel_block", {"x": 1.0000001})
    res = run(ref, new)
    assert res.untagged == 1 and res.census == {"novel_block": 1} and res.exit_code == 2
    assert row(res, f"{S}/novel_block/x").outcome == "NOT COMPUTED"
    text = "\n".join(cr.render(res, "a", "b"))
    assert "untagged 1" in text and "novel_block 1" in text and "NOT COMPUTABLE" in text


# ---- round 3: robustness K scope (R14) and the cp rule against the whole-system clip scope (R17)
def with_robustness(tree: dict) -> dict:
    """Two robustness variants shaped like the real ``robustness/<s>/<variant>/`` (own ``chosen_K`` and an H1b PLP
    slope with its interval). WU-0003.9b: the interval leaf was ``H3c/A5_over_A4_mse`` and ``H3c/ci``, which no real
    variant has (a real variant holds ``H1b``, the ``H2a_*`` leaves, ``A4_*``, ``mse_href`` and ``chosen_K``); a
    float leaf of a path outside the schema is NOT COMPUTABLE now (C4), so the test uses a real one, with the same
    numbers (estimate 0.9, interval [0.6, 1.2])."""
    tree["robustness"]["lorenz63"].update({v: {"chosen_K": 3, "H1b": {"PLP": {"slope": 0.9, "ci": [0.6, 1.2]}}}
                                           for v in ("base", "misspec=0.1")})
    return tree


def robustness_case(tier: str, **edits: object) -> "cr.Comparison":
    """Both trees get the variants; the main H3c estimate moves by 0.5 x 0.1 hw (= 0.015); ``edits`` apply to new."""
    ref, new = tier_pair(tier)
    for tree in (ref, new):
        with_robustness(tree)
    edit(new, f"{S}/H3c/A5_over_A4_mse", 0.915)
    for path, value in edits.items():
        edit(new, path.replace("__", "/"), value)
    return run(ref, new)


@pytest.mark.parametrize("tier", ["T1", "T2", "T3"])
def test_a_robustness_k_reaches_its_own_variant_only(tier: str) -> None:
    """R14: a K difference at ``robustness/<s>/<variant>/chosen_K`` must not open the K blocks of the main system.

    Reference: the probe of the review on the real P1 schema. Control: without any count the main H3c move
    (0.5 x 0.1 hw) fails; with the main ``fitted/chosen_K`` bumped it passes (K reaches H3c); with only the
    variant's K bumped it fails again, and a main ``H3a`` integer that differs is exact, not listed. The variant's
    own interval leaf is licensed by its own K (0.1 hw) and the other variant's is not."""
    h3c = f"{S}/H3c/A5_over_A4_mse"
    variant_k = "robustness/lorenz63/misspec=0.1/chosen_K"
    assert row(robustness_case(tier), h3c).outcome == "FAIL"
    assert row(robustness_case(tier, **{f"{S}__fitted__chosen_K": 4}), h3c).outcome == "pass"
    res = robustness_case(tier, **{variant_k.replace("/", "__"): 4})
    assert row(res, variant_k).outcome == "listed" and row(res, h3c).outcome == "FAIL" and res.exit_code == 1
    res = robustness_case(tier, **{variant_k.replace("/", "__"): 4, f"{S}__H3a__n_per_regime__[0]": 31})
    assert row(res, f"{S}/H3a/n_per_regime/[0]").outcome == "FAIL"
    own, other = "robustness/lorenz63/misspec=0.1/H1b/PLP/slope", "robustness/lorenz63/base/H1b/PLP/slope"
    res = robustness_case(tier, **{variant_k.replace("/", "__"): 4, own.replace("/", "__"): 0.915,
                                   other.replace("/", "__"): 0.915})
    assert row(res, own).outcome == "pass" and row(res, other).outcome == "FAIL"


def test_a_main_system_k_one_sided_shape_is_not_excused_by_a_robustness_k() -> None:
    """The one-sided rule uses the same scope: a longer main ``H3a`` list is excused by the main K, not by a
    variant's K."""
    path = f"{S}/H3a/logrank_p_raw/[2]"
    res = robustness_case("T1", **{"robustness__lorenz63__misspec=0.1__chosen_K": 4, "systems__lorenz63__H3a__logrank_p_raw": [0.01, 0.2, 0.3]})
    assert row(res, path).outcome == "FAIL"
    res = robustness_case("T1", **{f"{S}__fitted__chosen_K": 4, "systems__lorenz63__H3a__logrank_p_raw": [0.01, 0.2, 0.3]})
    assert row(res, path).outcome == "listed"


@pytest.mark.parametrize("tier", ["T1", "T2", "T3"])
def test_a_differing_clip_count_does_not_license_the_h1a_fit_leaves(tier: str) -> None:
    """R17, adapted to the OF-7 ruling of WU-0003.9c (the old test moved the fit leaves by 1e-7 and expected FAIL under
    cp 1e-12; under the ruling 1e-7 passes the QoI rule, so the move is now 1e-3 absolute, which is what the
    whole-system clip scope would wrongly license): the whole-system scope of a clip count must not let a cp-dependent
    leaf pass at 0.1 hw. Hand numbers: ``ci_inverse_dim`` [0.48, 0.65] has s = 0.65, QoI tolerance 6.5e-5, and
    0.1 hw = 0.1 x 0.085 = 8.5e-3, so a move of 1e-3 FAILS the QoI rule and would pass at 0.1 hw; ``floor_rms``
    (class g, 1e-4 |ref| = 3e-6) moved by 1e-4 is a FINDING and has no interval to license. With the cell
    ``error_clips`` +1 they must all stay outside, while the network-chain H3c estimate passes at 0.5 x 0.1 hw.
    A state count of the H1a block itself (block-local) licenses the interval leaves, as A6 says."""
    ref, new = tier_pair(tier)
    for tree in (ref, new):
        with_h1a(tree)
    edit(new, f"{CELL}/counts/error_clips", 1)
    edit(new, f"{S}/H3c/A5_over_A4_mse", 0.915)
    edit(new, f"{H1A}/fitted_inverse_dim", 0.55 + 1e-3)
    edit(new, f"{H1A}/floor_rms", 0.03 + 1e-4)
    edit(new, f"{H1A}/ci_inverse_dim/[0]", 0.48 + 1e-3)
    res = run(ref, new)
    assert row(res, f"{S}/H3c/A5_over_A4_mse").outcome == "pass"
    assert row(res, f"{H1A}/fitted_inverse_dim").outcome == "FAIL"
    assert row(res, f"{H1A}/ci_inverse_dim/[0]").outcome == "FAIL"
    assert row(res, f"{H1A}/floor_rms").outcome == "FINDING"
    edit(new, f"{CELL}/counts/error_clips", 0)
    edit(new, f"{S}/H1a/n_states", 79)                     # block-local count of H1a: licenses its interval leaves
    res = run(ref, new)
    assert row(res, f"{H1A}/ci_inverse_dim/[0]").outcome == "pass"
    assert row(res, f"{H1A}/ci_inverse_dim/[0]").rule == "discrete scope: 0.1 hw"


@pytest.mark.parametrize("tier", ["T1", "T2", "T3"])
def test_a_differing_clip_count_does_not_license_the_h1a_ratio_and_its_interval(tier: str) -> None:
    """Review R1 of WU-0003.9b, the R17 analogue for ``ratio`` and ``ratio_ci``: they are cp-dependent, so a
    whole-system clip count (a PLP count) must not let them pass at 0.1 hw. Reference: the plan's numbers by hand.
    ``ratio`` 1.09 -> 1.10 and ``ratio_ci/[1]`` 1.30 -> 1.31 are 0.01, far above 1e-12 |ref| and also above
    1e-4 s = 1.3e-4: they FAIL with no count, and still FAIL with the cell ``error_clips`` +1 (the whole-system
    scope), while the network-chain H3c estimate moved by 0.5 x 0.1 hw passes with it. A count of the block itself
    (``H1a/n_states``) licenses them, as A6 says."""
    ref, new = tier_pair(tier)
    for tree in (ref, new):
        with_h1a(tree)
    edit(new, f"{H1A}/ratio", 1.10)
    edit(new, f"{H1A}/ratio_ci/[1]", 1.31)
    for counts in (0, 1):
        edit(new, f"{CELL}/counts/error_clips", counts)
        edit(new, f"{S}/H3c/A5_over_A4_mse", 0.915)
        res = run(ref, new)
        assert row(res, f"{H1A}/ratio").outcome == "FAIL" and row(res, f"{H1A}/ratio_ci/[1]").outcome == "FAIL", counts
        assert row(res, f"{H1A}/ratio").rule == "cp chain relative"
        assert (row(res, f"{S}/H3c/A5_over_A4_mse").outcome == "pass") == bool(counts)
    edit(new, f"{CELL}/counts/error_clips", 0)
    edit(new, f"{S}/H1a/n_states", 79)
    res = run(ref, new)
    assert row(res, f"{H1A}/ratio").outcome == "pass" and row(res, f"{H1A}/ratio_ci/[1]").outcome == "pass"


# ---------------------------------------------------------------------------------- d3: 10x rule
@pytest.mark.parametrize("max_rel, expected", [
    (0.0, None), (1e-16, 1e-15), (3.97e-7, 1e-5), (2.94e-7, 1e-5), (1e-5, 1e-4), (1.0000001e-5, 1e-3),
    (4.99e-6, 1e-4), (5e-5, 1e-3), (9.9e-5, 1e-3), (1e-4, 1e-3), (math.inf, math.inf)])
def test_ten_times_rule_rounds_up_to_a_power_of_ten(max_rel: float, expected: float | None) -> None:
    """ROADMAP: 10 x the largest rel, rounded up to a power of 10 (hand table; an exact power of ten stays).

    Reference: the rule by hand: 10 x 1e-5 = 1e-4 is already a power, so 1e-4; 10 x 1.0000001e-5 is above it,
    so 1e-3; 0 gives "bitwise" (None). Tolerance: exact (decimal powers compare equal as doubles).
    """
    got = cr.declared_tolerance(max_rel)
    assert got == expected if expected in (None, math.inf) else got == pytest.approx(expected, rel=1e-12)


def test_declaration_per_class_group_and_the_o3_finding() -> None:
    """d3 on a synthetic pair shaped like the kernel pair: (a) max rel 3e-7 declares 1e-5 and (b) to (g)
    max rel 4.99e-6 declares 1e-4; neither is above the O3 ceiling. A (b) to (g) rel of 2e-4 declares 1e-2 and the leaf
    exceeds the class tolerance (FINDING, exit 1); on a T2 pair the O3 line is information, on the T0 calibration pair it
    is O3 itself (R5 is with the owner)."""
    ref, new = tier_pair("T2")
    edit(new, f"{S}/H3c/ci/[1]", 1.2 * (1 + 3e-7))                       # rel to s = 1.2: 3e-7
    edit(new, f"{S}/weight_profile/median/[0]", 0.5 * (1 + 4.99e-6))    # class b, rel 4.99e-6
    res = run(ref, new)
    assert res.declared["(a)"]["declared"] == pytest.approx(1e-5) and not res.declared["(a)"]["o3"]
    assert res.declared["(a)"]["max_rel"] == pytest.approx(3e-7, rel=1e-6)
    assert res.declared["(b) to (g)"]["declared"] == pytest.approx(1e-4)
    assert res.declared["(b) to (g)"]["max_rel"] == pytest.approx(4.99e-6, rel=1e-6)
    assert not res.declared["(b) to (g)"]["o3"] and res.exit_code == 0
    edit(new, f"{S}/scores/A1/mse/1LT", 0.2 * (1 + 2e-4))
    res = run(ref, new)
    assert res.declared["(b) to (g)"]["declared"] == pytest.approx(1e-2) and res.declared["(b) to (g)"]["o3"]
    assert res.exit_code == 1 and row(res, f"{S}/scores/A1/mse/1LT").outcome == "FINDING"    # 2e-4 > 1e-4
    assert any("information" in ln for ln in cr.render(res, "a", "b"))


def test_ten_times_maximum_excludes_the_leaves_the_note_excludes() -> None:
    """M2 (h): integers, V1, V2, fitted coefficients, ``median_iterations`` and leaves in a block with a
    differing discrete count do not enter the maximum. All of them differ hugely here and the pool stays empty."""
    ref, new = tier_pair("T3", **{
        f"{S}__validation__delay_jacobian_rel_err": 5e-10, f"{S}__validation__crlb_ratio_median": 1.01,
        f"{S}__fitted__analog_proxy__floor": 0.02, f"{CELL}__lm__median_iterations": 9.0,
        f"{S}__H3c__n_states": 79, f"{S}__H3c__A5_over_A4_mse": 0.91})
    res = run(ref, new)
    assert res.declared["(a)"]["n"] == 0 and res.declared["(b) to (g)"]["n"] == 0
    assert res.declared["(a)"]["declared"] is None


# ---------------------------------------------------------------------------------- d4: TD statistic
def fixture_parts() -> dict:
    """The 18 primary parts of P0 and P1 (DEV-0)."""
    return json.loads(FIXTURE.read_text())["systems"]


def trees_from_fixture() -> tuple[dict, dict]:
    """Two results trees whose primary parts are those of P0 and P1."""
    paths = {"H2a(i)": ("H2a", "median_range", "range_ci"),
             "H2a(ii) zero": ("H2a/part_ii/zero", "partial_corr", "ci"),
             "H2a(ii) interior": ("H2a/part_ii/interior", "partial_corr", "ci"),
             "H2b(i)": ("H2b/noise", "mean_state_spearman", "ci"),
             "H2b(ii)": ("H2b/library_change", "mean_change", "ci"),
             "H3c": ("H3c", "A5_over_A4_mse", "ci")}
    systems = tuple(fixture_parts())
    out = []
    for run_key in ("p0", "p1"):
        tree = make(systems)
        for system, parts in fixture_parts().items():
            for name, (block, point, interval) in paths.items():
                node = get(tree, f"systems/{system}/{block}")
                node[point] = parts[name][run_key]["estimate"]
                node[interval] = parts[name][run_key]["ci"]
        out.append(tree)
    return out[0], out[1]


def test_td_statistic_on_the_p0_p1_parts_matches_the_independent_script() -> None:
    """d4: sum z^2 12.65 (symmetric) and 11.99 (away), max |z| 1.69 on 18 parts; no part fails.

    Reference: ``m1_td_p0p1.log`` printed by the independent script ``m1_td_p0p1.py`` (z_level 2.3940),
    including the per-part values of the two parts where the forms differ most (Chua H3c: 1.34 and
    1.02). Tolerance: the log prints two decimals, so abs 0.005 on the sums and the parts.
    """
    tree0, tree1 = trees_from_fixture()
    td = cr.td_statistic(tree0, tree1)
    assert td["k"] == 18 and td["n_error"] == 0 and td["n_fail"] == 0
    assert td["sum_sym"] == pytest.approx(12.65, abs=0.005)
    assert td["sum_away"] == pytest.approx(11.99, abs=0.005)
    assert td["max_z"] == pytest.approx(1.69, abs=0.005)
    chua_h3c = next(p for p in td["parts"] if p["system"] == "chua" and p["part"] == "H3c")
    assert chua_h3c["z_sym"] == pytest.approx(1.34, abs=0.005) and chua_h3c["z_away"] == pytest.approx(1.02, abs=0.005)
    rossler = next(p for p in td["parts"] if p["system"] == "rossler" and p["part"] == "H2a(ii) zero")
    assert rossler["z_sym"] == pytest.approx(1.69, abs=0.005) and rossler["z_away"] == pytest.approx(1.69, abs=0.005)


def test_td_z_is_symmetric_under_swapping_the_runs() -> None:
    """The away arms are chosen from the sign of the difference, so swapping the two runs changes no z
    (a property of the DEC-0027 definition, checked on all 18 parts)."""
    a, b = trees_from_fixture()
    forward, backward = cr.td_statistic(a, b), cr.td_statistic(b, a)
    for f, g in zip(forward["parts"], backward["parts"]):
        assert f["z_sym"] == pytest.approx(g["z_sym"], rel=1e-12)
        assert f["z_away"] == pytest.approx(g["z_away"], rel=1e-12)


def test_z_level_is_the_primary_interval_quantile() -> None:
    """z_level = Phi^-1(1 - 0.05/6) = 2.39398 (the log prints 2.3940); tolerance abs 1e-5 (6 digits typed)."""
    assert cr.z_level() == pytest.approx(Z_LEVEL, abs=1e-5)


def hand_z(d: float, se0: float, se1: float) -> float:
    """``|d| / sqrt(se0^2 + se1^2)``, by hand."""
    return abs(d) / math.sqrt(se0 ** 2 + se1 ** 2)


def test_td_part_hand_case_symmetric_intervals() -> None:
    """Estimates 0 and 3 with intervals [-1, 1] and [2, 4]: hw = 1, se = 1 / z_level, so
    z = 3 z_level / sqrt(2) = 5.078 in both forms. Tolerance: 1e-5 relative (z_level typed to 6 digits)."""
    res = cr.td_part(0.0, [-1.0, 1.0], 3.0, [2.0, 4.0])
    expected = hand_z(3.0, 1 / Z_LEVEL, 1 / Z_LEVEL)
    assert expected == pytest.approx(5.078, abs=1e-3)
    assert res["z_sym"] == pytest.approx(expected, rel=1e-5) and res["z_away"] == pytest.approx(expected, rel=1e-5)
    assert res["d"] == 3.0 and res["hw0"] == 1.0 and res["hw1"] == 1.0


def test_td_part_uses_the_arms_facing_away_and_the_two_forms_differ() -> None:
    """DEC-0027 by hand. Run 1 above run 0, so run 0's lower arm and run 1's upper arm enter.

    * Short away arms (0.2 each, hw 1): z_sym = 2 z_level / sqrt(2) = 3.386 < 3.4 but
      z_away = 2 z_level / 0.2828 = 16.9.
    * Long away arms (1.8 each, hw 1), d = 2.02: z_sym = 3.420 > 3.4 but z_away = 1.90. Tolerance: relative 1e-5.

    This test checks the two z values of ``td_part`` only. Which one fails a part was "either" before the OF-5 ruling
    of 2026-10-18 and is z_away alone since (WU-0003.9c); ``test_td_failing_rule_is_the_away_form_alone`` pins that.
    """
    short = cr.td_part(0.0, [-0.2, 1.8], 2.0, [0.2, 2.2])
    assert short["z_sym"] == pytest.approx(2.0 * Z_LEVEL / math.sqrt(2), rel=1e-5) and short["z_sym"] < 3.4
    assert short["z_away"] == pytest.approx(2.0 * Z_LEVEL / math.hypot(0.2, 0.2), rel=1e-5) and short["z_away"] > 3.4
    long = cr.td_part(0.0, [-1.8, 0.2], 2.02, [1.82, 3.82])
    assert long["z_sym"] == pytest.approx(2.02 * Z_LEVEL / math.sqrt(2), rel=1e-5) and long["z_sym"] > 3.4
    assert long["z_away"] == pytest.approx(2.02 * Z_LEVEL / math.hypot(1.8, 1.8), rel=1e-5) and long["z_away"] < 3.4


def test_td_part_edge_cases() -> None:
    """d = 0 gives 0 (also with zero width); a nonzero d over a zero standard error is infinite; a missing
    interval, a non-finite number, or an estimate outside its interval is an error (never a number)."""
    assert cr.td_part(1.0, [1.0, 1.0], 1.0, [1.0, 1.0])["z_sym"] == 0.0
    assert cr.td_part(1.0, [1.0, 1.0], 2.0, [2.0, 2.0])["z_sym"] == math.inf
    assert "error" in cr.td_part(1.0, None, 2.0, [1.0, 3.0])
    assert "error" in cr.td_part(1.0, [0.0, 2.0], math.nan, [1.0, 3.0])
    assert "error" in cr.td_part(-1.0, [0.0, 2.0], 6.0, [5.0, 7.0])      # estimate below its interval


def td_pair(**edits: object) -> tuple[dict, dict]:
    """A pair that is TD (trajectory digest differs; the devices also differ)."""
    ref, new = make(), make()
    edit(new, f"{S}/context/main_digest", dig("9"))
    edit(new, f"{PROV}/backend", "gpu")
    for path, value in edits.items():
        edit(new, path.replace("__", "/"), value)
    return ref, new


def test_td_pair_passes_fails_or_is_undetermined_by_its_parts() -> None:
    """A TD pair exits 0 if every part is within 3.4, 1 if one exceeds it, 2 if a part cannot be computed.

    Reference: the bound of A6/B1 item 5 on hand-shifted parts: H3c's estimate 0.9 with hw 0.3 on both
    runs has se = 0.3/z_level = 0.1253; a shift of 0.5 gives z = 0.5/(0.1253 sqrt 2) = 2.82 (< 3.4,
    pass) and a shift of 0.7 gives 3.95 (> 3.4, fail).
    """
    ref, new = td_pair()
    res = run(ref, new)
    assert res.tier.name == "TD" and res.exit_code == 0 and res.td["k"] == 6
    edit(new, f"{S}/H3c/A5_over_A4_mse", 0.9 + 0.5)
    edit(new, f"{S}/H3c/ci", [0.6 + 0.5, 1.2 + 0.5])
    z = 0.5 / (0.3 / Z_LEVEL * math.sqrt(2))
    assert z == pytest.approx(2.82, abs=0.01)
    assert run(ref, new).exit_code == 0
    edit(new, f"{S}/H3c/A5_over_A4_mse", 0.9 + 0.7)
    edit(new, f"{S}/H3c/ci", [0.6 + 0.7, 1.2 + 0.7])
    res = run(ref, new)
    assert res.td["n_fail"] == 1 and res.exit_code == 1
    assert any(p["fail"] and p["part"] == "H3c" for p in res.td["parts"])
    ref, new = td_pair()
    edit(new, f"{S}/H3c/ci", None)
    res = run(ref, new)
    assert res.td["n_error"] == 1 and res.exit_code == 2


def test_td_reports_both_forms_the_o4_line_and_the_trajectory_only_note() -> None:
    """TD between two devices triggers O4; a TD selected only by a trajectory digest lists the per-leaf
    differences as report only. Both z forms are printed."""
    ref, new = td_pair()
    text = "\n".join(cr.render(run(ref, new), "a", "b"))
    assert "triggers O4" in text and "z_sym" in text and "z_away" in text
    assert "selected only by main_digest" in text and "(report only)" in text
    ref, new = make(), make()
    edit(new, f"{S}/context/lambda_max", 0.95)
    text = "\n".join(cr.render(run(ref, new), "a", "b"))
    assert "selected only by main_digest" not in text and "triggers O4" not in text


def test_td_only_mode_needs_no_selecting_leaves(tmp_path: Path) -> None:
    """``--td-only`` computes the statistic of two runs that predate the digests (P0, P1) and exits by it."""
    a, b = trees_from_fixture()
    pa, pb = tmp_path / "p0.json", tmp_path / "p1.json"
    for tree, path in ((a, pa), (b, pb)):
        for system in tree["systems"].values():
            for group in ("context", "validation", "fitted"):
                system.pop(group, None)
        path.write_text(json.dumps(tree))
    assert cr.main([str(pa), str(pb)]) == 2                        # undetermined without the leaves
    assert cr.main([str(pa), str(pb), "--td-only"]) == 0


def test_a_system_missing_on_one_run_is_not_computable_in_both_modes() -> None:
    """R2: B1 item 5 fixes 18 parts. A system absent from one run gives its 6 parts as NOT COMPUTABLE (exit 2),
    in ``td_statistic``, in ``--td-only`` and in a full TD comparison; the expected count (6 x systems) is printed.
    Reference: 3 systems x 6 parts = 18 by construction."""
    a, b = trees_from_fixture()
    del b["systems"]["chua"]
    td = cr.td_statistic(a, b)
    assert td["expected"] == 18 and td["k"] == 12 and td["n_error"] == 6
    assert all("missing" in p["error"] for p in td["parts"] if "error" in p) and not td["n_fail"]
    assert "12 of 18 expected" in "\n".join(cr.render_td(td))
    assert cr.td_statistic(b, a)["n_error"] == 6                      # either side
    lines, code = cr.run_td_only(a, b, "a", "b")
    assert code == 2 and "UNDETERMINED" in lines[-1]
    ref, new = td_pair()
    ref2, new2 = make(("lorenz63", "rossler")), make(("lorenz63", "rossler"))
    edit(new2, f"{S}/context/main_digest", dig("9"))
    del new2["systems"]["rossler"]
    res = run(ref2, new2)
    assert res.tier.name == "TD" and res.td["expected"] == 12 and res.td["n_error"] == 6 and res.exit_code == 2


# ---- verdict-type strings of the real schema
@pytest.mark.parametrize("tier", ["T0", "T1", "T2", "T3"])
@pytest.mark.parametrize("path, value", [
    (f"{S}/clip_sensitivity/by_hypothesis/H3c/parts/A5_over_A4/verdict_2L", "fail"),
    (f"{S}/clip_sensitivity/by_hypothesis/H2c/parts/A4_minus_A2/status", "not_computed"),
    (f"{S}/clip_sensitivity/status", "not_computed")])
def test_clip_sensitivity_verdict_and_status_strings_give_def_lines(tier: str, path: str, value: str) -> None:
    """R9: ``verdict_2L`` and ``status`` of the real ``clip_sensitivity`` block are verdict-type strings: a
    difference prints a DEF line (not a categorical failure). Reference: the real leaf paths of the S3 smoke."""
    ref, new = (make(), make()) if tier == "T0" else tier_pair(tier)
    assert get(ref, path) != value
    edit(new, path, value)
    res = run(ref, new)
    assert row(res, path).outcome == "DEF" and res.exit_code == 1
    assert any(ln.startswith("DEF:") and path in ln for ln in cr.render(res, "a", "b"))


def test_best_single_2l_is_a_listed_discrete_count_not_a_failure() -> None:
    """``clip_sensitivity/.../best_single_2L`` is a best-single, like ``H2c/best_single``: listed (A6)."""
    path = f"{S}/clip_sensitivity/by_hypothesis/H2c/best_single_2L"
    res = run(*tier_pair("T1", **{path.replace("/", "__"): "A1"}))
    assert row(res, path).outcome == "listed" and res.exit_code == 0


# ----------------------------------------------------------------------------- d5: accounting and listing
def test_leaf_accounting_union_one_sided_and_excluded_counts() -> None:
    """d5: the union of leaves is counted, one-sided leaves are listed, timing and provenance are excluded.

    Reference: counts by construction. The synthetic provenance block has 7 leaves (3 device, platform,
    cpu model, LPC_THREADS, wall_seconds) and the tree 2 ``seconds`` leaves (top level, one estimator).
    """
    ref, new = tier_pair("T1")
    edit(ref, f"{S}/H3c/only_ref", 1.0)
    edit(new, f"{S}/H3c/only_new_a", 1.0)
    edit(new, f"{S}/H3c/only_new_b", 2.0)
    res = run(ref, new)
    assert (res.n_ref, res.n_new) == (res.n_common + 1, res.n_common + 2)
    text = "\n".join(cr.render(res, "a", "b"))
    assert "provenance 7 leaves, timing 2 leaves" in text
    assert f"union {res.n_common + 3}" in text and "one-sided 3" in text
    assert {r.kind for r in res.one_sided} == {"only_ref", "only_new"} and len(res.one_sided) == 3
    assert all(f"{S}/H3c/{n}" in text for n in ("only_ref", "only_new_a", "only_new_b"))


def test_every_difference_is_listed_with_class_rel_tolerance_and_outcome_with_all() -> None:
    """d5: ``--all`` lists every difference (default: the first ``show`` of a passing group; every failure)."""
    ref, new = tier_pair("T3")
    edit(ref, f"{S}/weight_profile/median", [0.5 + 0.01 * j for j in range(25)])
    edit(new, f"{S}/weight_profile/median", [0.5 + 0.01 * j + 1e-9 for j in range(25)])
    res = run(ref, new)
    default = "\n".join(cr.render(res, "a", "b", show=5))
    full = "\n".join(cr.render(res, "a", "b", show=5, every=True))
    listed = lambda text: sum(1 for ln in text.splitlines() if ln.startswith("      ") and "weight_profile" in ln)
    assert listed(default) == 5 and listed(full) == 25
    line = next(ln for ln in full.splitlines() if "weight_profile/median/[3]" in ln)
    assert "rel " in line and "tol 0.0001" in line


# ------------------------------------------------------------------------------------- pure LM functions
def test_lm_estimate_check_hand_cases() -> None:
    """B1 item 2 on hand arrays, rho = 0.1 and ||X||_inf = 3, so eta = 1e-12 max(1, 3) = 3e-12; each bound is
    exercised at 0.5 x (passes) and 2 x (violates).

    * c = 0.5 (c/rho^2 = 50 > 18.47): only 1e-8 |c| = 5e-9 applies: d = 2.5e-9 passes, 1e-8 violates.
    * c = 1e-4 (c/rho^2 = 0.01): min(1e-12, eta (2 sqrt(c) + eta) = 6e-14) = 6e-14: d = 3e-14 passes,
      1.2e-13 violates.
    * c = 1e-12: min(1e-20, eta (2 sqrt(c) + eta) = 6e-18) = 1e-20 (PF-2): d = 5e-21 passes and d = 2e-20
      violates, although it is below the eta bound.
    * c = 0.15 (c/rho^2 = 15, converged): min(1.5e-9, eta (2 sqrt(0.15) + eta) = 2.3238e-12) = 2.3238e-12:
      d = 0.5 x and 2 x that value (computed in the test).
    * c = 0.2 (c/rho^2 = 20 > 18.47, not converged): the 1e-8 bound alone, 2e-9: d = 1e-9 passes (it would
      violate the tight bound 2.7e-12, which must not apply).
    * a late-flagged estimate (either run) is counted and never checked, however large d.
    Tolerance: the d values are 0.5 x or 2 x the bound; the one-ulp error of c + d (2.8e-17 at c = 0.15, so the
    realized ratios are 0.5 and 2 to 2.4e-5 there and much better elsewhere) never decides a case.
    """
    eta = 3e-12
    assert eta * (2 * math.sqrt(1e-4) + eta) == pytest.approx(6e-14, rel=1e-9)
    assert eta * (2 * math.sqrt(0.15) + eta) == pytest.approx(2.3238e-12, rel=1e-4)
    tight = eta * (2 * math.sqrt(0.15) + eta)
    c_ref = [0.5, 0.5, 1e-4, 1e-4, 1e-12, 1e-12, 0.15, 0.15, 0.2, 5.0]
    d = [2.5e-9, 1e-8, 3e-14, 1.2e-13, 5e-21, 2e-20, 0.5 * tight, 2 * tight, 1e-9, 100.0]
    c_new = [c + x for c, x in zip(c_ref, d)]
    late_ref, late_new = [0] * 10, [0] * 9 + [1]
    out = cr.lm_estimate_check(c_ref, c_new, late_ref, late_new, rho=0.1, x_inf=3.0)
    assert out["n"] == 10 and out["n_late"] == 1 and out["late"] == [9] and out["n_checked"] == 9
    assert out["violations"] == [1, 3, 5, 7]
    assert out["n_tight"] == 6                      # indices 2 to 7
    assert out["max_ratio"] > 1.0


def test_lm_estimate_check_passing_set_and_validation() -> None:
    """A converged estimate that moves by 1e-13 against its bound 2.3e-12 passes (ratio about 0.04); a late flag
    in the reference run alone also excludes an estimate. Bad input raises."""
    ok = cr.lm_estimate_check([0.15, 0.3], [0.15 + 1e-13, 9.0], [0, 1], [0, 0], rho=0.1, x_inf=3.0)
    assert ok["violations"] == [] and ok["n_checked"] == 1 and ok["n_late"] == 1 and ok["max_ratio"] < 0.1
    with pytest.raises(ValueError):
        cr.lm_estimate_check([1.0], [1.0, 2.0], [0], [0], rho=0.1, x_inf=1.0)
    with pytest.raises(ValueError):
        cr.lm_estimate_check([1.0], [1.0], [0], [0], rho=0.0, x_inf=1.0)


def test_order_statistic_band_hand_values() -> None:
    """M7(ii): ranks n q -/+ 2.58 sqrt(n q (1 - q)), rounded outward and clipped to 1..n.

    By hand: n = 100, q = 0.5: half = 2.58 x 5 = 12.9 -> ranks 37 and 63. q = 0.95: half = 2.58 x 2.17945 =
    5.6230 -> floor(95 - 5.623) = 89 and ceil(100.623) = 101 clipped to 100. n = 4, q = 0.5: half = 2.58 ->
    floor(-0.58) clipped to 1, and ceil(4.58) clipped to 4.
    """
    assert cr.order_statistic_band(100, 0.5) == (37, 63)
    assert cr.order_statistic_band(100, 0.95) == (89, 100)
    assert cr.order_statistic_band(4, 0.5) == (1, 4)
    for bad in ((0, 0.5), (10, 0.0), (10, 1.0)):
        with pytest.raises(ValueError):
            cr.order_statistic_band(*bad)


def test_two_proportion_bound_literal() -> None:
    """3 sqrt(2 pbar (1 - pbar) / n) + 1/n at n = 100, pbar = 0.1: 3 x 0.042426 + 0.01 = 0.13728 (abs 1e-5)."""
    assert cr.two_proportion_bound(0.1, 0.1, 100) == pytest.approx(0.13728, abs=1e-5)


# ------------------------------------------------------------------------------- CLI, read-only, hygiene
def write_run(dir_: Path, tree: dict) -> Path:
    """A run directory with a results.json and two sibling files."""
    dir_.mkdir()
    (dir_ / "results.json").write_text(json.dumps(tree))
    (dir_ / "run.log").write_text("log\n")
    (dir_ / "RESULTS.md").write_text("# r\n")
    return dir_


def snapshot(*dirs: Path) -> dict:
    """Names and SHA-256 of every file under the directories."""
    return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for d in dirs for p in sorted(d.rglob("*"))
            if p.is_file()} | {str(p): "dir" for d in dirs for p in sorted(d.rglob("*")) if p.is_dir()}


def test_the_tool_is_read_only_on_run_directories_and_accepts_directories(tmp_path: Path, capsys) -> None:
    """Both run directories are byte-for-byte (and name-for-name) unchanged after a comparison, whatever the
    outcome, and a directory is read as its ``results.json``."""
    a = write_run(tmp_path / "a", make())
    b = write_run(tmp_path / "b", edit(make(), f"{S}/H3c/A5_over_A4_mse", 0.95))
    before = snapshot(a, b)
    assert cr.main([str(a), str(b)]) == 1
    assert cr.main([str(a), str(a)]) == 0
    assert cr.main([str(a), str(b), "--all"]) == 1
    assert snapshot(a, b) == before
    assert "RESULT: FAIL" in capsys.readouterr().out
    assert sorted(p.name for p in tmp_path.iterdir()) == ["a", "b"]


def test_cli_usage_and_input_errors_exit_2(tmp_path: Path, capsys) -> None:
    """Unreadable files, a file that is not a results.json, a bad option value and unknown flags exit 2."""
    good = tmp_path / "g.json"
    good.write_text(json.dumps(make()))
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    other = tmp_path / "other.json"
    other.write_text("[1, 2]")
    assert cr.main([str(good), str(tmp_path / "missing.json")]) == 2
    assert cr.main([str(good), str(bad)]) == 2
    assert cr.main([str(good), str(other)]) == 2
    assert cr.main([str(good), str(good), "--tol-other", "0"]) == 2
    assert cr.main([str(good), str(good), "--tol-other", "1"]) == 2          # above the O3 ceiling (R4)
    assert cr.main([str(good), str(good), "--tol-other", "1e-4"]) == 0
    assert cr.main([str(good), str(good), "--tol-other", "nan"]) == 2
    assert cr.main([str(good), str(good), "--show", "-1"]) == 2
    assert cr.main([str(good), str(good), "--nonsense"]) == 2
    assert cr.main([str(good)]) == 2
    assert "compare_runs: error" in capsys.readouterr().err


def test_cli_isolated_subprocess_exit_codes_and_label(tmp_path: Path) -> None:
    """``python3 -I tools/compare_runs.py`` (the documented invocation) prints the DEVELOPMENT label and the
    review note, and exits 0 and 1 on a passing and a failing pair."""
    a, b, c = tmp_path / "a.json", tmp_path / "b.json", tmp_path / "c.json"
    a.write_text(json.dumps(make()))
    b.write_text(json.dumps(make()))
    c.write_text(json.dumps(edit(make(), f"{S}/H3c/A5_over_A4_mse", 0.95)))
    ok = subprocess.run([sys.executable, "-I", str(TOOL), str(a), str(b)], capture_output=True, text=True,
                        timeout=60, check=False)
    bad = subprocess.run([sys.executable, "-I", str(TOOL), str(a), str(c)], capture_output=True, text=True,
                         timeout=60, check=False)
    assert ok.returncode == 0 and bad.returncode == 1
    assert ok.stdout.startswith("DEVELOPMENT: comparison of two runs, not a hypothesis test")
    assert "needs owner review before freeze" in ok.stdout and "RESULT: PASS" in ok.stdout


def test_tool_source_hygiene() -> None:
    """The tool draws no random numbers, imports no numpy, scipy, jax or lpcstudy module, replaces nothing
    silently and never opens a file for writing.

    Reference: the AST and the text of the tool (LPC.PC.7, PRIME.4: the tool computes a comparison and counts
    what it cannot compute).
    """
    text = TOOL.read_text()
    for banned in ("default_rng", "random.", "PRNGKey", "nan_to_num", "np.clip", "np.where"):
        assert banned not in text, banned
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert all(a.name.split(".")[0] not in ("numpy", "scipy", "jax", "lpcstudy", "random") for a in node.names)
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in ("numpy", "scipy", "jax", "lpcstudy", "random")
        if isinstance(node, ast.Call):
            name = getattr(node.func, "attr", getattr(node.func, "id", ""))
            assert name not in ("write_text", "write_bytes", "mkdir", "unlink", "rename", "touch", "dump"), name
            if name == "open":
                assert all(not (isinstance(a, ast.Constant) and isinstance(a.value, str) and set(a.value) & set("wax+"))
                           for a in node.args), "open() for writing"


def test_chain_tags_of_the_imported_rule_table_are_the_known_set() -> None:
    """The tool relies on ``compare_pilot``'s chain tags (cp, oracle, dynamics, fixture, network): a new tag
    would be silently treated as network, so the set is pinned."""
    tags = {rule.chain for rule in cr.cp.TABLE.rules}
    assert tags <= {"", "network", "dynamics", "fixture", "cp", "oracle"}
    assert cr.cp.NETWORK_INDEPENDENT == {"fixture", "dynamics", "cp", "oracle"}


# ======================================================================================================
# WU-0003.9b (plan amendment 3 C4): every float leaf of the pilot schema has a chain tag
# ======================================================================================================
# Needs owner review before freeze: the tags decide tolerance classes (network-independent chains meet 1e-12,
# the network chain the class rules).
#
# References, all independent of the tag table under test:
#   * the paths of the real DEV-0 pilot P1 (5b3fd8f), of P0 (1b20db9) and of the smoke preset at the .7c tip,
#     committed as shapes without values (``fixtures/pilot_schema``, written by ``extract_paths.py``);
#   * the chain each of those leaves had BEFORE this unit (column 2 of the fixtures; a regression guard, not
#     correctness evidence, so the test is named ``test_regression_*``);
#   * the plan's numbers (1e-12 for the network-independent chains, 1e-4 s for class (a)), typed in the tests.
# Tolerances: every comparison of a tag, a count or an exit code is exact; the numeric cases use the factors 0.5
# and 2 around the plan's tolerance, so round-off (1e-16 relative) never decides a case.
SCHEMA_DIR = ROOT / "tests" / "unit" / "fixtures" / "pilot_schema"
FIXTURE_FILES = ("p1_float_paths.txt", "p0_smoke_float_paths.txt")
OVERRIDE_CHAINS = {"fixture", "cp", "oracle", "dynamics", "network"}


def read_shapes(name: str) -> dict[str, str]:
    """``{shape: chain before WU-0003.9b}`` from a fixture file (comment lines start with ``#``)."""
    out = {}
    for line in (SCHEMA_DIR / name).read_text().splitlines():
        if line and not line.startswith("#"):
            shape, chain = line.split("\t")
            out[shape] = chain
    return out


def concrete(shape: str) -> tuple[str, ...]:
    """The path a shape stands for: every ``[]`` is ``[0]`` and ``<sys>`` is ``lorenz63``."""
    return tuple("[0]" if s == "[]" else "lorenz63" if s == "<sys>" else s for s in shape.split("/"))


ALL_SHAPES = {name: read_shapes(name) for name in FIXTURE_FILES}


def test_the_schema_fixtures_hold_paths_and_old_chains_only() -> None:
    """The fixtures are what the header says: shapes of float leaves, no values, a chain column from the known set,
    and they hold the blocks the census named (config, H1a, handling lm, km_curves, clip_sensitivity, verification).
    A reading of the real pilot gave 970 shapes for P1 (``extract_paths.py``)."""
    for name, shapes in ALL_SHAPES.items():
        assert len(shapes) > 900, name
        assert {c for c in shapes.values()} <= {"", "network", "dynamics", "fixture", "cp", "oracle"}
        blocks = {shape.split("/")[2] if shape.startswith("systems/") else shape.split("/")[0] for shape in shapes}
        assert {"config", "H1a", "handling", "km_curves", "clip_sensitivity", "verification", "robustness"} <= blocks
        assert all("\t" not in shape for shape in shapes)
    assert "systems/<sys>/H1a/by_noise/0.01/ratio" in ALL_SHAPES["p1_float_paths.txt"]
    assert any(s.startswith("systems/<sys>/context/start_state/") for s in ALL_SHAPES["p0_smoke_float_paths.txt"])


@pytest.mark.parametrize("name", FIXTURE_FILES)
def test_no_float_leaf_of_the_pilot_schema_is_untagged(name: str) -> None:
    """C4 (t1): the untagged set is EMPTY on the paths of P1, and on the union of the paths of P0 and the smoke
    preset (which has the .7a, .7b and .7c leaves). Before WU-0003.9b it held 2849 leaves in P1 (609 shapes in
    the shapes of this fixture, of which the ``config`` ones are tagged by override now)."""
    untagged = [shape for shape in ALL_SHAPES[name] if not cr.chain_of(concrete(shape))]
    assert untagged == []


# the one documented change of an existing chain (review R2): a tightening, network to cp
DOCUMENTED_TIGHTENINGS = {"systems/<sys>/H1d/rows/nhat/spearman": ("network", "cp")}


@pytest.mark.parametrize("name", FIXTURE_FILES)
def test_regression_every_previously_tagged_leaf_keeps_its_chain_but_the_documented_tightening(name: str) -> None:
    """C4 (t2), a regression guard: the chain each leaf had before this unit (column 2, written by
    ``extract_paths.py`` from ``compare_pilot``'s unchanged table and the one H1a override) is the chain it has
    now, with one exception, a finding of the review resolved stricter (R2): ``H1d/rows/nhat/spearman``, network in
    the table but cp by the code, is tightened by ``TIGHTENINGS``. The assertion message lists every difference; a
    change must be that documented tightening and must go to a network-independent chain."""
    changed = {shape: (before, cr.chain_of(concrete(shape)))
               for shape, before in ALL_SHAPES[name].items() if before and cr.chain_of(concrete(shape)) != before}
    assert changed == {s: v for s, v in DOCUMENTED_TIGHTENINGS.items() if s in ALL_SHAPES[name]}, changed
    assert all(new in cr.cp.NETWORK_INDEPENDENT and old == "network" for old, new in changed.values())


def test_the_nhat_spearman_is_tightened_to_cp_and_meets_the_chain_tolerance() -> None:
    """Review R2: ``H1d/rows/nhat/spearman`` (a point estimate with the interval ``interval``) is cp 1e-12 relative,
    like its interval; the other H1d rows stay network. Reference: the plan's 1e-12 by hand; 0.5 x passes and 2 x
    fails, in T1, T2 and T3. ``compare_pilot``'s table is unchanged (it still says network)."""
    leaf = ("systems", "lorenz63", "H1d", "rows", "nhat", "spearman")
    assert cr.chain_source(leaf)[:2] == ("cp", "tightening")
    assert cr.cp.TABLE.classify(leaf).chain == "network"
    assert cr.chain_of(("systems", "lorenz63", "H1d", "rows", "growth", "spearman")) == "network"
    for tier in ("T1", "T2", "T3"):
        for factor, outcome in ((0.5, "pass"), (2.0, "FAIL")):
            ref, new = tier_pair(tier)
            for tree in (ref, new):
                block_leaf(tree, "H1d", {"rows": {"nhat": {"spearman": 0.5, "interval": [0.4, 0.6]}}})
            edit(new, f"{S}/H1d/rows/nhat/spearman", 0.5 + factor * 1e-12 * 0.5)
            r = row(run(ref, new), f"{S}/H1d/rows/nhat/spearman")
            assert r.outcome == outcome and r.rule == "cp chain relative" and r.tol == 1e-12, (tier, factor)


@pytest.mark.parametrize("name", FIXTURE_FILES)
def test_overrides_never_shadow_a_compare_pilot_tag_and_never_overlap(name: str) -> None:
    """An override applies only where ``compare_pilot``'s table has no chain (the table decides first, so a
    shadowing override would be dead code that misleads a reader), and no leaf matches two overrides."""
    for shape in ALL_SHAPES[name]:
        path = concrete(shape)
        found = cr.TAGS.matches(path)
        assert len(found) <= 1, (shape, [t.pattern for t in found])
        table_chain = ""
        try:
            table_chain = cr.cp.TABLE.classify(path).chain
        except cr.cp.ToolError:
            pass
        assert not (table_chain and found), (shape, table_chain, found[0].pattern)


def test_every_override_matches_a_leaf_of_the_fixtures_and_names_no_index_or_system() -> None:
    """No dead pattern (a typo would leave its leaves untagged and the pin red, but a pattern that matches nothing
    is also a defect), and the patterns use the wildcards that the fixtures' shapes assume (``[]``, ``systems/*``):
    no literal list index and no literal system name."""
    used = set()
    for shapes in ALL_SHAPES.values():
        for shape in shapes:
            used.update(t.pattern for t in cr.TAGS.matches(concrete(shape)))
    assert sorted(t.pattern for t in cr.TAGS.rules if t.pattern not in used) == []
    for tag in cr.TAGS.rules:
        segs = tag.pattern.split("/")
        assert not any(re.fullmatch(r"\[\d+\]", seg) for seg in segs), tag.pattern
        assert not any(seg in ("lorenz63", "rossler", "chua") for seg in segs), tag.pattern


def test_every_override_has_a_known_chain_a_reason_that_cites_its_source_and_a_known_tolerance() -> None:
    """Each override carries a printed reason that cites the producing function (``file.py:function``) or says
    that the leaf is a run configuration or a constant, and a chain from the known set. The tightening rows name a
    network-independent chain only (they may tighten a table chain, never loosen it)."""
    assert len(cr.TAGS.rules) > 40
    for tag in cr.TAGS.rules:
        assert tag.chain in OVERRIDE_CHAINS, tag.pattern
        assert re.search(r"\w+\.py:\w+", tag.reason) or tag.reason.startswith("run configuration"), tag.pattern
        assert len(tag.reason) > 25, tag.pattern
    for tag in cr.TIGHTENINGS.rules:
        assert tag.chain in cr.cp.NETWORK_INDEPENDENT and re.search(r"\w+\.py:\w+", tag.reason), tag.pattern


def test_the_chain_of_a_leaf_is_the_table_chain_then_the_override() -> None:
    """``chain_of`` and ``chain_source`` on hand-known paths: a table tag keeps its reason, an override says so,
    and a leaf in no table has none."""
    cases = [(("systems", "lorenz63", "H1b", "CP", "slope"), "cp", "table"),
             (("systems", "lorenz63", "scores", "A1", "mse", "1LT"), "network", "table"),
             (("systems", "lorenz63", "H2e", "corr_curve", "0.01", "10000"), "network", "override"),
             (("systems", "lorenz63", "verification", "P2c", "fraction_violations"), "cp", "override"),
             (("systems", "lorenz63", "H3c", "level"), "fixture", "override"),
             (("config", "core_noise"), "fixture", "override"),
             (("systems", "lorenz63", "H1d", "rows", "nhat", "spearman"), "cp", "tightening"),
             (("systems", "lorenz63", "novel_block", "x"), "", "")]
    for path, chain, source in cases:
        got_chain, got_source, reason = cr.chain_source(path)
        assert (got_chain, got_source) == (chain, source), path
        assert cr.chain_of(path) == chain
        assert bool(reason) == bool(source)


def test_an_untagged_float_leaf_is_not_computable_in_every_tier_even_when_equal() -> None:
    """C4: an untagged float leaf of either run is NOT COMPUTABLE: exit 2 in every tier, also when the leaf is equal
    in both runs, also when it is on one side only, and ``allow_not_computed`` does not waive it. A real failure
    elsewhere still gives exit 1 (the pair fails whatever the untagged leaves say), and the untagged leaf is listed."""
    for tier in ("T1", "T2", "T3"):
        ref, new = tier_pair(tier)
        for tree in (ref, new):
            edit(tree, f"{S}/novel_block", {"x": 1.0})
        res = run(ref, new)
        assert res.exit_code == 2 and res.untagged == 0, tier          # equal: not decided, but not computable
        assert res.untagged_leaves == [("systems", "lorenz63", "novel_block", "x")]
        assert any("NOT COMPUTABLE" in reason for reason in res.reasons)
        edit(new, f"{S}/novel_block", {"x": 2.0})
        res = run(ref, new)
        assert res.exit_code == 2 and res.untagged == 1 and row(res, f"{S}/novel_block/x").outcome == "NOT COMPUTED"
    ref, new = make(), make()
    assert cr.compare_trees(ref, new).exit_code == 0
    edit(new, f"{S}/novel_extra", {"y": 1.0})                              # one-sided and untagged, T0
    res = cr.compare_trees(ref, new, allow_not_computed=True)
    assert res.untagged_leaves == [("systems", "lorenz63", "novel_extra", "y")]
    assert res.exit_code == 1                                              # the one-sided leaf itself is a failure
    ref, new = tier_pair("T1", **{f"{S}__scores__A1__mse__1LT": 0.3})
    edit(new, f"{S}/novel_block", {"x": 1.0})
    assert run(ref, new).exit_code == 1                                    # a failure outranks the untagged leaf
    td_ref, td_new = make(), make()
    edit(td_new, f"{S}/context/state_mean_digest", dig("9"))
    for tree in (td_ref, td_new):
        edit(tree, f"{S}/novel_block", {"x": 1.0})
    res = run(td_ref, td_new)
    assert res.tier.name == "TD" and res.exit_code == 2 and res.untagged_leaves


def test_a_config_float_is_tagged_and_still_compared_exactly() -> None:
    """The ``config`` floats get an override (so that the census is 0), but ``config`` stays compared for identity:
    a differing config float is a failure in T1 exactly as before."""
    ref, new = tier_pair("T1")
    for tree in (ref, new):
        edit(tree, "config", {"name": "smoke", "seed": 7, "n_test": 80, "core_noise": 0.01})
    assert run(ref, new).exit_code == 0
    edit(new, "config/core_noise", 0.0100000001)
    res = run(ref, new)
    assert res.exit_code == 1 and row(res, "config/core_noise").outcome == "FAIL" and res.untagged == 0


# ---- the tolerance follows the chain of an override (hand cases at 0.5 x and 2 x the plan's number)
def block_leaf(tree: dict, block: str, content: dict) -> dict:
    """Add a block to the system of a synthetic tree (``edit`` cannot create a missing parent)."""
    tree["systems"]["lorenz63"][block] = content
    return tree


OVERRIDE_CASES = {
    # a cp-chain override: A6 T1, |d| <= 1e-12 |ref|
    "cp (P2c)": ("verification", {"P2c": {"fraction_violations": 0.2}}, "verification/P2c/fraction_violations",
                 0.2, 1e-12 * 0.2, "cp chain relative"),
    # a constant: fixture chain, the same 1e-12
    "fixture (level)": ("H3c", {"level": 0.9833333333333333}, "H3c/level", 0.9833333333333333,
                        1e-12 * 0.9833333333333333, "fixture chain relative"),
}


@pytest.mark.parametrize("tier", ["T1", "T2", "T3"])
@pytest.mark.parametrize("name", sorted(OVERRIDE_CASES))
def test_an_override_chain_meets_the_chain_tolerance(tier: str, name: str) -> None:
    """A6 T1 to T3: the network-independent chains meet ``|d| <= 1e-12 |ref|``; 0.5 x passes, 2 x fails.

    Reference: the plan's number, evaluated by hand in ``OVERRIDE_CASES``. Tolerance: the factors 0.5 and 2."""
    block, content, leaf, value, tol, rule = OVERRIDE_CASES[name]
    path = f"{S}/{leaf}"
    for factor, outcome in ((0.5, "pass"), (2.0, "FAIL")):
        ref, new = tier_pair(tier)
        for tree in (ref, new):
            block_leaf(tree, block, copy.deepcopy(content))
        edit(new, path, value + factor * tol)
        r = row(run(ref, new), path)
        assert r.outcome == outcome and r.rule == rule and r.tol == 1e-12, (name, factor)


@pytest.mark.parametrize("tier", ["T1", "T2", "T3"])
def test_the_h1a_ratio_is_cp_and_meets_the_strict_chain_tolerance_with_the_of7_pointer(tier: str) -> None:
    """Review R1 of WU-0003.9b: ``ratio`` and ``ratio_ci`` depend on the cp chain only and meet cp 1e-12 relative. The
    four sibling outputs of the same tolerance-stopped ``curve_fit`` were re-tagged by the OF-7 ruling of 2026-10-18
    (WU-0003.9c); the ruling does not name ``ratio`` and ``ratio_ci``, so they keep cp 1e-12 (the A6 QoI rule 1e-4 s
    is the owner's alternative, not applied, flagged in the Log). Reference: the plan's 1e-12 by hand
    (``ratio`` 1.09, ``ratio_ci/[1]`` 1.3); 0.5 x passes and 2 x fails, and a failure carries the OF-7 pointer."""
    assert cr.chain_of(("systems", "lorenz63", "H1a", "by_noise", "0.01", "ratio")) == "cp"
    for leaf, value in (("ratio", 1.09), ("ratio_ci/[1]", 1.3)):
        for factor, outcome in ((0.5, "pass"), (2.0, "FAIL")):
            pair = tier_pair(tier)
            for tree in pair:
                with_h1a(tree)
            edit(pair[1], f"{H1A}/{leaf}", value + factor * 1e-12 * value)
            r = row(run(*pair), f"{H1A}/{leaf}")
            assert r.outcome == outcome and r.rule == "cp chain relative" and r.tol == 1e-12, (leaf, factor)
            assert (cr.OF7_POINTER in r.note) == (outcome == "FAIL")


# ---- the whole real schema, with made-up values
def tree_from_shapes(shapes: dict[str, str]) -> dict:
    """A results tree with a 1.0 at every float shape (index 0 of each list, system ``lorenz63``) and the leaves
    that the tier selection reads (digests, host facts)."""
    root: dict = {}
    for shape in shapes:
        node = root
        segs = concrete(shape)
        for seg in segs[:-1]:
            node = node.setdefault(seg, {})
        node[segs[-1]] = 1.0

    def finalize(node: object) -> object:
        if not isinstance(node, dict):
            return node
        if set(node) == {"[0]"}:
            return [finalize(node["[0]"])]
        return {k: finalize(v) for k, v in node.items()}

    tree = finalize(root)
    assert isinstance(tree, dict)
    tree["provenance"] = {"device": {"backend": "cpu", "kind": "cpu", "count": 1}, "platform": "Linux-test",
                          "cpu": {"model": "TestCPU"}, "env": {"LPC_THREADS": "4"}}
    for block in tree["systems"].values():
        block["context"].update({n: dig("1") for n in ("state_mean_digest", "cov_digest", "whiten_digest",
                                                       "unwhiten_digest", "main_digest", "estimator_digest")})
        block.setdefault("fitted", {})["allocator_digest"] = dig("a")
        for entry in block.get("validation", {}).get("estimators", {}).values():
            entry["weights_digest"] = dig("e")
    for entry in tree.get("estimators", {}).values():
        entry["weights_digest"] = dig("e")
    return tree


def scaled(tree: object, factor: float, path: tuple[str, ...] = ()) -> object:
    """A copy with every float multiplied by ``factor``, except under ``config`` and ``context``."""
    if isinstance(tree, dict):
        return {k: tree[k] if (not path and k in ("config", "provenance")) or k == "context"
                else scaled(tree[k], factor, (*path, k)) for k in tree}
    if isinstance(tree, list):
        return [scaled(v, factor, path) for v in tree]
    return tree * factor if type(tree) is float else tree


@pytest.mark.parametrize("name", FIXTURE_FILES)
def test_the_whole_pilot_schema_runs_through_the_tolerance_rules_with_no_untagged_leaf(name: str) -> None:
    """C4 (t3 in miniature): a results tree with every float shape of the real P1 (or P0 + smoke) schema, run
    against a copy on another device (tier T1) with every float moved by a relative 5e-13 (0.5 x the chain
    tolerance 1e-12) and then by 2e-12 (2 x). Reference: the plan's 1e-12 and 1e-4 s, and the chain of each
    leaf from the fixture's own old column or the known set.

    Asserted: no leaf is untagged or NOT COMPUTED for lack of a tag; at 0.5 x nothing fails except the T1 LM rule
    ``fraction_no_decrease`` (exact); at 2 x every failure is a network-independent leaf, a V1/V2 or LM rule, and at
    least one failure is a leaf that an override tagged (so the overrides are consulted)."""
    tree = tree_from_shapes(ALL_SHAPES[name])
    new = copy.deepcopy(tree)
    edit(new, "provenance/device/backend", "gpu")
    edit(new, "provenance/device/kind", "gpu")
    for factor, label in ((1 + 5e-13, "low"), (1 + 2e-12, "high")):
        res = cr.compare_trees(tree, scaled(new, factor), allow_not_computed=True)
        assert res.tier.name == "T1", res.tier
        assert res.untagged == 0 and res.untagged_leaves == [] and res.census == {}
        assert not [r for r in res.rows if r.outcome == "NOT COMPUTED" and r.rule == cr.UNTAGGED_RULE]
        failing = [r for r in res.rows if r.outcome in ("FAIL", "FINDING")]
        if label == "low":
            assert {r.rule for r in failing} <= {"T1: exact"}, {r.rule for r in failing}
        else:
            assert failing
            for r in failing:
                assert (cr.chain_of(r.path) in cr.cp.NETWORK_INDEPENDENT or r.rule.startswith(("V1", "V2", "T1:"))
                        or "LM summary" in r.rule), (r.path, r.rule)
            assert any(cr.chain_source(r.path)[1] == "override" for r in failing
                       if cr.chain_of(r.path) in cr.cp.NETWORK_INDEPENDENT)


# ---- what the report prints
def test_the_report_prints_the_tag_summary_and_the_reason_of_each_override_in_use() -> None:
    """C4: the report says how many float leaves each source tagged and that none is untagged, and prints the
    reason of every override pattern that tagged a DIFFERING leaf; ``--tags`` prints the whole override table."""
    ref, new = tier_pair("T1")
    for tree in (ref, new):
        block_leaf(tree, "verification", {"P2c": {"fraction_violations": 0.2}})
    edit(new, f"{S}/verification/P2c/fraction_violations", 0.2 + 2e-12 * 0.2)
    res = run(ref, new)
    text = "\n".join(cr.render(res, "a", "b"))
    assert "untagged 0" in text and "compare_pilot table" in text and "override" in text
    assert "systems/*/verification/P2c/fraction_violations" in text and "validation.py" in text
    full = "\n".join(cr.render(res, "a", "b", tags=True))
    assert full.count("\n") > text.count("\n")
    for tag in cr.TAGS.rules:
        assert tag.pattern in full, tag.pattern


def test_the_command_line_prints_the_tag_table_with_tags(tmp_path: Path, capsys) -> None:
    """``--tags`` is an option of the comparison (it needs the two files), changes no exit code and prints the table."""
    a = tmp_path / "a.json"
    a.write_text(json.dumps(make()))
    assert cr.main([str(a), str(a), "--tags"]) == 0
    out = capsys.readouterr().out
    assert "chain tags assigned by override" in out and "RESULT: PASS" in out


# ======================================================================================================
# WU-0003.9c (owner rulings of 2026-10-18, note 33 of the amendments note): OF-7 re-tag and OF-5 TD rule
# ======================================================================================================
# Needs owner review before freeze (these tests pin tolerances and the failing rule of a reproducibility tool).
#
# References, independent of the tool: the ruling text and the mathematician's note section Q1.4 (the class of each
# leaf, typed here), the plan's tolerance 1e-4 s of class (a) and the (b) to (g) tolerance 1e-4 |ref|, evaluated by
# hand on the H1a block of the synthetic tree (``with_h1a``: ``ci_inverse_dim`` [0.48, 0.65] so s = 0.65), and the
# DEC-0027 arms by hand. Tolerances: decisions and counts are exact; the numeric cases use 0.5 x and 2 x the plan's
# number, so round-off (1e-16 relative) never decides a case.
OF7_RETAGS = {          # pattern -> class letter: the four leaves named by the ruling, and nothing else
    "systems/*/H1a/by_noise/*/fitted_inverse_dim": "a",
    "systems/*/H1a/by_noise/*/ci_inverse_dim/[]": "a",
    "systems/*/H1a/by_noise/*/floor_rms": "g",
}
OF7_SHAPES = {          # the shapes of the pilot schema (both fixtures) that the retag rows match
    f"systems/<sys>/H1a/by_noise/{rho}/{leaf}" for rho in ("0.01", "0.02")
    for leaf in ("ci_inverse_dim/[]", "fitted_inverse_dim", "floor_rms")}
OF7_KEPT_CP = ("ratio", "ratio_ci/[0]", "ratio_ci/[1]", "median_seed_by_n_lib/1000")


def test_of7_retag_table_is_pinned_to_the_four_named_leaves_and_leaves_the_rest_alone() -> None:
    """The owner's OF-7 ruling re-tags ``fitted_inverse_dim``, ``ci_inverse_dim[0..1]`` and ``floor_rms`` and nothing
    else. Pinned: the three patterns and their classes (a, a, g: note Q1.4); each keeps the dependence chain ``cp``
    (the note says do not edit that meaning) and cites the note; on both schema fixtures (P1; P0 plus smoke) they
    match exactly the six shapes of the two noise levels, which is 4 leaves x 2 rho x 3 systems = 24 per pilot
    (counted by hand: a ``[]`` shape stands for 2 endpoints); ``ratio``, ``ratio_ci``, ``median_seed_by_n_lib`` and
    ``inverse_dim_reference`` are not re-tagged, so the cp 1e-12 rule stays for every other leaf."""
    assert {r.pattern: r.scale for r in cr.RETAGS.rules} == OF7_RETAGS
    for r in cr.RETAGS.rules:
        assert r.chain == "cp" and "2026-10-14-math-wu0003-9-q1" in r.reason and "OF-7" in r.reason, r.pattern
    # R1 of the review: each row prints the basis of its own class (note Q1.3: class (a) rests on the a-priori bound
    # 4.0e-5 s, factor 2.5; floor_rms on the measured flip <= 6.3e-7 and stopping error <= 6.8e-7 relative, factor >= 70)
    for r in cr.RETAGS.rules:
        if r.scale == "a":
            assert "4.0e-5 s" in r.reason and "factor 2.5" in r.reason, r.pattern
        else:
            assert r.pattern.endswith("floor_rms")
            assert "6.3e-7" in r.reason and "6.8e-7" in r.reason and "factor >= 70" in r.reason
            assert "4.0e-5" not in r.reason and "factor 2.5" not in r.reason
    for name, shapes in ALL_SHAPES.items():
        hit = {s for s in shapes if cr.retag_of(concrete(s)) is not None}
        assert hit == OF7_SHAPES, name
        n_leaves = sum(2 if s.endswith("/[]") else 1 for s in hit) * 3
        assert n_leaves == 24
    base = ("systems", "lorenz63", "H1a")
    for leaf in OF7_KEPT_CP + ("inverse_dim_reference",):
        path = (*base, "inverse_dim_reference") if leaf == "inverse_dim_reference" else (
            *base, "by_noise", "0.01", *leaf.split("/"))
        assert cr.retag_of(path) is None and cr.chain_of(path) == "cp", leaf
    # a retag row is not a chain tag: a leaf of that shape outside H1a stays untagged
    assert cr.retag_of(("systems", "lorenz63", "novel", "by_noise", "0.01", "floor_rms")) is None
    assert cr.chain_of(("systems", "lorenz63", "novel", "by_noise", "0.01", "floor_rms")) == ""


def test_of7_declared_class_is_the_class_the_tool_assigns_to_the_leaf() -> None:
    """A retag row declares the class it applies (a: the interval scale s = max(|lo|, |hi|); g: |ref|). The class
    the tool derives for each leaf of an H1a block (``classify_float``) must equal it, with the scale s = 0.65 of
    [0.48, 0.65] for the class-(a) leaves (hand value)."""
    flat = cr.flatten(with_h1a(make()))
    for leaf, letter in (("fitted_inverse_dim", "a"), ("ci_inverse_dim/[0]", "a"), ("ci_inverse_dim/[1]", "a"),
                         ("floor_rms", "g")):
        path = tuple(f"{H1A}/{leaf}".split("/"))
        retag = cr.retag_of(path)
        assert retag is not None and retag.scale == letter, leaf
        cls, scale, defaulted = cr.classify_float(flat, path)
        assert cls == letter and not defaulted, leaf
        if letter == "a":
            assert scale == 0.65


OF7_CASES = {   # leaf -> (reference value, absolute tolerance by hand, outcome beyond it, rule)
    "fitted_inverse_dim": (0.55, 1e-4 * 0.65, "FAIL", "QoI / interval endpoint (OF-7 re-tag)"),
    "ci_inverse_dim/[0]": (0.48, 1e-4 * 0.65, "FAIL", "QoI / interval endpoint (OF-7 re-tag)"),
    "ci_inverse_dim/[1]": (0.65, 1e-4 * 0.65, "FAIL", "QoI / interval endpoint (OF-7 re-tag)"),
    "floor_rms": (0.03, 1e-4 * 0.03, "FINDING", "class (b) to (g) (OF-7 re-tag)"),
}


@pytest.mark.parametrize("tier", ["T1", "T2", "T3"])
@pytest.mark.parametrize("leaf", sorted(OF7_CASES))
def test_of7_retagged_leaf_meets_the_a6_rule_at_half_and_fails_at_double(tier: str, leaf: str) -> None:
    """Hand-worked: ``fitted_inverse_dim`` 0.55 with the reference interval [0.48, 0.65] has s = 0.65, so the QoI
    tolerance is 1e-4 x 0.65 = 6.5e-5; a move of 0.5 x passes (relative 5e-5 of s), 2 x FAILS (2e-4). The same for
    the endpoints. ``floor_rms`` 0.03 is class (g): 1e-4 x 0.03 = 3e-6, 2 x is a FINDING (the (b) to (g) outcome).
    Before WU-0003.9c all four met cp 1e-12, so 0.5 x was a FAIL (6.5e-5 / 0.55 = 1.2e-4 >> 1e-12) and carried the
    OF-7 pointer; here it passes, with no pointer and the re-tag named in the rule."""
    value, tol, beyond, rule = OF7_CASES[leaf]
    for factor, outcome in ((0.5, "pass"), (2.0, beyond)):
        ref, new = tier_pair(tier)
        for tree in (ref, new):
            with_h1a(tree)
        edit(new, f"{H1A}/{leaf}", value + factor * tol)
        r = row(run(ref, new), f"{H1A}/{leaf}")
        assert r.outcome == outcome and r.rule == rule, (leaf, factor)
        assert r.tol == 1e-4 and r.cls == ("g" if leaf == "floor_rms" else "a")
        assert cr.OF7_POINTER not in r.note


def test_of7_floor_rms_follows_the_tol_other_option_like_every_class_g_leaf() -> None:
    """``floor_rms`` is class (g), so ``--tol-other`` governs it: 0.5 x 3e-6 = 1.5e-6 is 5e-5 relative, a pass at the
    default 1e-4 and a FINDING at 1e-5 (hand: 1e-5 x 0.03 = 3e-7 < 1.5e-6)."""
    ref, new = tier_pair("T2")
    for tree in (ref, new):
        with_h1a(tree)
    edit(new, f"{H1A}/floor_rms", 0.03 + 1.5e-6)
    assert row(run(ref, new), f"{H1A}/floor_rms").outcome == "pass"
    r = row(run(ref, new, tol_other=1e-5), f"{H1A}/floor_rms")
    assert r.outcome == "FINDING" and r.tol == 1e-5


@pytest.mark.parametrize("tier", ["T1", "T2", "T3"])
def test_of7_effect_on_a_pair_the_four_pass_the_ratio_leaves_still_fail_and_nothing_else_moves(tier: str) -> None:
    """The effect of the ruling on a pair like the S3 kernel pair, in the synthetic tree: every H1a fit leaf moved by
    3e-7 relative (the largest measured on that pair is 2.94e-7 of s). The four named leaves pass; ``ratio`` and
    ``ratio_ci/[0|1]`` (same fit, not named) still FAIL cp 1e-12 with the pointer, so the exit is 1 and the pointer
    leaves per (system, rho) are 3 (18 per pilot). With only the four moved, the pair passes (exit 0) and prints no
    pointer. Reference: 3e-7 vs the plan's 1e-12 and 1e-4 by hand."""
    ref, new = tier_pair(tier)
    for tree in (ref, new):
        with_h1a(tree)
    four = (("fitted_inverse_dim", 0.55), ("floor_rms", 0.03), ("ci_inverse_dim/[0]", 0.48), ("ci_inverse_dim/[1]", 0.65))
    for leaf, value in four:
        edit(new, f"{H1A}/{leaf}", value * (1 + 3e-7))
    res = run(ref, new)
    assert res.exit_code == 0 and all(r.outcome == "pass" for r in res.rows if r.path[:4] == ("systems", "lorenz63", "H1a", "by_noise"))
    assert "pointer:" not in "\n".join(cr.render(res, "a", "b"))
    for leaf, value in (("ratio", 1.09), ("ratio_ci/[0]", 0.96), ("ratio_ci/[1]", 1.3)):
        edit(new, f"{H1A}/{leaf}", value * (1 + 3e-7))
    res = run(ref, new)
    assert res.exit_code == 1
    assert [r.outcome for r in res.rows if cr.OF7_POINTER in r.note] == ["FAIL"] * 3
    assert {r.path[-1] if r.path[-1] == "ratio" else "/".join(r.path[-2:]) for r in res.rows if r.outcome == "FAIL"} == {
        "ratio", "ratio_ci/[0]", "ratio_ci/[1]"}


def test_of7_retag_without_a_reference_interval_keeps_cp_and_says_so() -> None:
    """A class-(a) retag needs the reference interval (its scale s). If the reference has none, the class cannot be
    established; the tool does not guess a looser class: the strict cp 1e-12 rule stays and the row says why.
    Hand: ``fitted_inverse_dim`` moved by 1e-7 relative fails cp 1e-12."""
    ref, new = tier_pair("T2")
    for tree in (ref, new):
        with_h1a(tree)
        edit(tree, f"{H1A}/ci_inverse_dim", None)
    edit(new, f"{H1A}/fitted_inverse_dim", 0.55 * (1 + 1e-7))
    r = row(run(ref, new), f"{H1A}/fitted_inverse_dim")
    assert r.outcome == "FAIL" and r.rule == "cp chain relative" and r.tol == 1e-12
    assert "OF-7 re-tag not applied" in r.note and "no reference interval" in r.note


def test_of7_an_untagged_float_leaf_still_exits_2_beside_retagged_leaves() -> None:
    """The ruling re-tags a tolerance, not a schema: an untagged float leaf is still NOT COMPUTABLE (exit 2), also
    when it has the name of a retagged leaf under another block, and the retagged leaves beside it still pass."""
    ref, new = tier_pair("T2")
    for tree in (ref, new):
        with_h1a(tree)
        edit(tree, f"{S}/novel", {"by_noise": {"0.01": {"floor_rms": 0.03}}})
    edit(new, f"{H1A}/fitted_inverse_dim", 0.55 * (1 + 1e-7))
    res = run(ref, new)
    assert res.exit_code == 2
    assert res.untagged_leaves == [("systems", "lorenz63", "novel", "by_noise", "0.01", "floor_rms")]
    assert row(res, f"{H1A}/fitted_inverse_dim").outcome == "pass"
    edit(new, f"{S}/novel/by_noise/0.01/floor_rms", 0.04)
    res = run(ref, new)
    assert res.exit_code == 2 and row(res, f"{S}/novel/by_noise/0.01/floor_rms").outcome == "NOT COMPUTED"


def test_of7_report_names_the_retag_and_the_tags_option_prints_the_table() -> None:
    """The report says which retag decided a differing leaf (pattern, class, reason) and ``--tags`` prints the whole
    retag table with the float-leaf counts per run (hand: one noise level of the synthetic block gives 1 + 2 + 1 = 4
    leaves)."""
    ref, new = tier_pair("T2")
    for tree in (ref, new):
        with_h1a(tree)
    edit(new, f"{H1A}/fitted_inverse_dim", 0.55 * (1 + 1e-7))
    res = run(ref, new)
    text = "\n".join(cr.render(res, "a", "b"))
    assert "OF-7 re-tag systems/*/H1a/by_noise/*/fitted_inverse_dim: class a, 1 differing leaves" in text
    full = "\n".join(cr.render(res, "a", "b", tags=True))
    assert "tolerance re-tags (OF-7, owner ruling of 2026-10-18" in full
    for pattern in OF7_RETAGS:
        assert pattern in full
    assert "systems/*/H1a/by_noise/*/ci_inverse_dim/[]: class a, float leaves 2 REF, 2 NEW" in full
    assert "systems/*/H1a/by_noise/*/fitted_inverse_dim: class a, float leaves 1 REF, 1 NEW" in full
    assert "systems/*/H1a/by_noise/*/floor_rms: class g, float leaves 1 REF, 1 NEW" in full


# ---- OF-5: the TD failing rule is the away-arm form alone
def h3c_td_pair(est0: float, ci0: list, est1: float, ci1: list) -> tuple[dict, dict]:
    """A TD pair whose only differing primary part is H3c, with the given estimates and intervals."""
    ref, new = td_pair()
    edit(ref, f"{S}/H3c/A5_over_A4_mse", est0)
    edit(ref, f"{S}/H3c/ci", ci0)
    edit(new, f"{S}/H3c/A5_over_A4_mse", est1)
    edit(new, f"{S}/H3c/ci", ci1)
    return ref, new


def test_td_failing_rule_is_the_away_form_alone() -> None:
    """OF-5 (owner ruling of 2026-10-18; WU-0003.9c): a part fails iff z_away > 3.4; z_sym is information only.
    Hand cases of DEC-0027 with z_level = 2.39398:

    * short away arms (0.2, hw 1), d = 2: z_away = 2 z_level / hypot(0.2, 0.2) = 16.9 > 3.4 fails (z_sym = 3.386);
    * long away arms (1.8, hw 1), d = 2.02: z_sym = 2.02 z_level / sqrt 2 = 3.420 > 3.4, z_away = 1.90: before the
      ruling this part FAILED on max(z_sym, z_away); now it passes, with z_sym printed.

    ``n_fail`` counts z_away only, ``max_z`` is the largest z_away, the governing field says ``z_away``, and the
    dict is JSON-serializable with both z values."""
    ref, new = h3c_td_pair(0.0, [-0.2, 1.8], 2.0, [0.2, 2.2])
    res = run(ref, new)
    part = next(p for p in res.td["parts"] if p["part"] == "H3c")
    assert part["z_sym"] < 3.4 < part["z_away"] and part["fail"] and part["z_governing"] == part["z_away"]
    assert res.td["n_fail"] == 1 and res.exit_code == 1
    assert res.td["governing"] == "z_away" and res.td["max_z"] == res.td["max_away"]
    ref, new = h3c_td_pair(0.0, [-1.8, 0.2], 2.02, [1.82, 3.82])
    res = run(ref, new)
    part = next(p for p in res.td["parts"] if p["part"] == "H3c")
    assert part["z_sym"] == pytest.approx(2.02 * Z_LEVEL / math.sqrt(2), rel=1e-5) and part["z_sym"] > 3.4
    assert part["z_away"] == pytest.approx(2.02 * Z_LEVEL / math.hypot(1.8, 1.8), rel=1e-5) and part["z_away"] < 3.4
    assert not part["fail"] and res.td["n_fail"] == 0 and res.exit_code == 0
    assert res.td["max_z"] == res.td["max_away"] < 3.4 < res.td["max_sym"]
    back = json.loads(json.dumps(res.td))
    assert back["governing"] == "z_away" and back["parts"][0]["z_sym"] >= 0.0
    h3c = next(p for p in back["parts"] if p["part"] == "H3c")
    assert h3c["z_sym"] == part["z_sym"] and h3c["z_away"] == part["z_away"] and h3c["z_governing"] == part["z_away"]


def test_td_report_says_which_form_governs_and_prints_the_other_as_information() -> None:
    """The printed header names the governing form and the bound; the symmetric column and sums are labelled
    information; the failing-parts count is the away count. ``--td-only`` prints the same."""
    ref, new = h3c_td_pair(0.0, [-1.8, 0.2], 2.02, [1.82, 3.82])
    text = "\n".join(cr.render(run(ref, new), "a", "b"))
    assert "bound 3.4 on z_away" in text and "OF-5" in text and "z_sym (information)" in text
    assert "max(|z_sym|, |z_away|)" not in text
    lines, code = cr.run_td_only(ref, new, "a", "b")
    assert code == 0 and "bound 3.4 on z_away" in "\n".join(lines)
