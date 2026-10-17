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


def test_failures_of_the_h1a_fit_keep_the_cp_rule_and_print_the_of7_pointer_with_an_unchanged_exit() -> None:
    """Round 2, item 1: the four H1a fit leaves that fail the cp rule on a platform pair (here 1e-7 relative, as on
    the S3 pair) still FAIL (exit 1, nothing loosened) and carry the OF-7 pointer; the report prints it once. A
    failure outside ``H1a/by_noise`` carries none; a pass carries none."""
    ref, new = tier_pair("T2")
    for tree in (ref, new):
        with_h1a(tree)
    for leaf, value in (("fitted_inverse_dim", 0.55), ("floor_rms", 0.03)):
        edit(new, f"{H1A}/{leaf}", value * (1 + 1e-7))
    edit(new, f"{H1A}/ci_inverse_dim/[0]", 0.48 * (1 + 1e-7))
    res = run(ref, new)
    for leaf in ("fitted_inverse_dim", "floor_rms", "ci_inverse_dim/[0]"):
        r = row(res, f"{H1A}/{leaf}")
        assert r.outcome == "FAIL" and cr.OF7_POINTER in r.note and "2026-10-14-math-wu0003-9-q1.md" in r.note
    assert res.exit_code == 1
    text = "\n".join(cr.render(res, "a", "b"))
    assert text.count("pointer: " + cr.OF7_POINTER) == 1
    for leaf, value in (("median_seed_by_n_lib/1000", 0.16), ("ratio", 1.09)):          # R15: not OF-7 leaves
        edit(new, f"{H1A}/{leaf}", value * (1 + 1e-3))
    res = run(ref, new)
    for leaf in ("median_seed_by_n_lib/1000", "ratio"):
        r = row(res, f"{H1A}/{leaf}")
        assert r.outcome == "FAIL" and cr.OF7_POINTER not in r.note, leaf
    ref, new = tier_pair("T2", **{f"{S}__H1b__CP__slope": 2.0 * (1 + 1e-7)})
    res = run(ref, new)
    assert row(res, f"{S}/H1b/CP/slope").outcome == "FAIL" and cr.OF7_POINTER not in row(res, f"{S}/H1b/CP/slope").note
    assert "pointer:" not in "\n".join(cr.render(res, "a", "b"))


def test_untagged_census_counts_hand_known_leaves_and_the_report_prints_it() -> None:
    """Round 2, item 3: the census counts float leaves without a chain tag, by block, and the report prints
    it. Reference: a tree of four floats whose tags are known from compare_pilot's table (checked by hand):
    ``H1b/CP/slope`` is cp, ``H3c/A5_over_A4_mse`` is network, ``H2e/corr_curve/..`` and ``scores/A*/regret/1LT`` are
    untagged; integers, strings and ``config`` are not counted. The census is information: no exit code depends on it."""
    flat = cr.flatten({"config": {"n_test": 1.0}, "systems": {"lorenz63": {
        "H1b": {"CP": {"slope": 1.0}}, "H3c": {"A5_over_A4_mse": 0.9, "n_states": 80},
        "H2e": {"corr_curve": {"0.01": {"10000": 0.05}}}, "scores": {"A*": {"regret": {"1LT": 0.0}}}}}})
    assert cr.untagged_census(flat) == {"H2e": 1, "scores": 1}
    ref, new = tier_pair("T3", **{f"{S}__H2e__corr_curve__0.01__10000": 0.0500001})
    res = run(ref, new)
    assert res.untagged == 1 and res.census.get("H2e") == 1 and res.census.get("scores") == 1
    text = "\n".join(cr.render(res, "a", "b"))
    assert "census (information, not a failure)" in text and "H2e 1" in text
    assert run(ref, new).exit_code == res.exit_code


# ---- round 3: robustness K scope (R14) and the cp rule against the whole-system clip scope (R17)
def with_robustness(tree: dict) -> dict:
    """Two robustness variants shaped like the real ``robustness/<s>/<variant>/`` (own ``chosen_K`` and an H3c)."""
    tree["robustness"]["lorenz63"].update({v: {"chosen_K": 3, "H3c": {"A5_over_A4_mse": 0.9, "ci": [0.6, 1.2]}}
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
    own, other = "robustness/lorenz63/misspec=0.1/H3c/A5_over_A4_mse", "robustness/lorenz63/base/H3c/A5_over_A4_mse"
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
def test_a_differing_clip_count_does_not_replace_the_cp_rule_of_the_h1a_fit_leaves(tier: str) -> None:
    """R17: the whole-system scope of a clip count must not let a cp-chain leaf pass at 0.1 hw (that replaced the
    OF-7 working default, cp 1e-12). With rossler-style cell ``error_clips`` +1, the H1a fit outputs moved by 1e-7
    relative still FAIL, while the network-chain H3c estimate passes at 0.5 x 0.1 hw. A state count of the H1a
    block itself (block-local) still licenses them, as A6 says: the strictness is only against the system-wide
    scope."""
    ref, new = tier_pair(tier)
    for tree in (ref, new):
        with_h1a(tree)
    edit(new, f"{CELL}/counts/error_clips", 1)
    edit(new, f"{S}/H3c/A5_over_A4_mse", 0.915)
    for leaf, value in (("fitted_inverse_dim", 0.55), ("floor_rms", 0.03)):
        edit(new, f"{H1A}/{leaf}", value * (1 + 1e-7))
    edit(new, f"{H1A}/ci_inverse_dim/[0]", 0.48 * (1 + 1e-7))
    res = run(ref, new)
    assert row(res, f"{S}/H3c/A5_over_A4_mse").outcome == "pass"
    for leaf in ("fitted_inverse_dim", "floor_rms", "ci_inverse_dim/[0]"):
        assert row(res, f"{H1A}/{leaf}").outcome == "FAIL", leaf
    edit(new, f"{CELL}/counts/error_clips", 0)
    edit(new, f"{S}/H1a/n_states", 79)                     # block-local count of H1a: licenses its interval leaves
    res = run(ref, new)
    assert row(res, f"{H1A}/ci_inverse_dim/[0]").outcome == "pass"


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


def test_td_part_uses_the_arms_facing_away_and_either_form_can_decide() -> None:
    """DEC-0027 by hand. Run 1 above run 0, so run 0's lower arm and run 1's upper arm enter.

    * Short away arms (0.2 each, hw 1): z_sym = 2 z_level / sqrt(2) = 3.386 < 3.4 but
      z_away = 2 z_level / 0.2828 = 16.9: the part fails on the away form alone.
    * Long away arms (1.8 each, hw 1), d = 2.02: z_sym = 3.420 > 3.4 but z_away = 1.90: fails on the
      symmetric form alone. Tolerance: relative 1e-5.
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
