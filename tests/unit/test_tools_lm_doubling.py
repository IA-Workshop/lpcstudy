"""Tests of ``tools/lm_doubling.py``, the iteration-doubling study tool (WU-0005.6b, DEV-0).

References (none of them is the tool's own output):

* K5: decision rule R of the Mathematics check, applied by hand to dyadic numbers with a half-width
  of 1, so every arithmetic step is exact in float64; the strict flag at 0.09, 0.10, 0.11 is
  ``budget.below_tenth`` (M9: yes, no, no).
* K6(a): closed forms of the clustered standard error (``SD(p, ddof=1)/sqrt(n)``) and of the
  batch-means standard error over blocks of 5 states, on hand-built arrays whose per-state fractions
  and ratios are dyadic; the weight formula against ``lpcstudy.oracle.oracle_weight`` (an
  independent implementation) and hand values.
* K6(b): the latent hazard found in the Mathematics check (M6): ``dataclasses.replace`` copies the
  cached ``StateEstimator._fn``. A small Lorenz-63 world (the independent simulation of
  ``simulate_trajectory``, a stub network) shows the 30-iteration copy runs the 15-iteration program
  when ``_fn`` is kept, and a different program with ``_fn = None``.
* C0, P1, K3: hand-built results trees (bit patterns by ``struct.pack``; the leaf lists of the M5
  items are typed here, one example path per pattern).
* P0: ``lm_summary`` of the package on hand arrays (the stored summary is built by the same function
  from the same arrays in the pipeline).

Tolerance: none. Every comparison is of integers, strings, bit patterns or dyadic floats that are
exact in float64; the only floats that are not dyadic (square roots, quantile interpolation of
dyadic values) are compared with ``pytest.approx`` at ``rel=1e-12``, about 5000 unit round-offs of
the few operations involved. Every test runs in under 5 s.
"""

from __future__ import annotations

import dataclasses
import importlib.util
import json
import math
import struct
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location("lm_doubling", ROOT / "tools" / "lm_doubling.py")
assert _SPEC is not None and _SPEC.loader is not None
lm = importlib.util.module_from_spec(_SPEC)
sys.modules["lm_doubling"] = lm
_SPEC.loader.exec_module(lm)

Est = lm.Est


def est(pt: float, lo: float = -1.0, hi: float = 1.0, verdict: str = "pass", n: int = 500) -> Est:
    """A part with half-width 1 at the design arm unless the interval is changed."""
    return Est(pt=pt, lo=lo, hi=hi, n=n, failed=0, verdict=verdict, mc_se=(0.01, 0.01))


def arms3(a: Est, b: Est, c: Est) -> dict:
    return {15: a, 30: b, 60: c}


# ------------------------------------------------------------------------------------------ K5
def test_k5_dyadic_negligible_case() -> None:
    """(d1, d2) = (1/32, 1/64) with hw = 1 gives S = 1/16, the ratio exactly 1/2, class N.

    Reference: rule R by hand. pt moves 0, 1/32, 3/64, so D1 = 1/32 and D2 = 1/64; the endpoints
    do not move. The ratio condition d2 <= d1/2 holds with equality; r_A = 1/2 holds with equality.
    """
    c = lm.classify(arms3(est(0.0), est(0.03125), est(0.046875)), tail=0.5)
    assert (c.cls, c.flag) == ("N", "yes")
    assert (c.hw, c.d1, c.d2, c.s) == (1.0, 0.03125, 0.015625, 0.0625)
    assert c.ratio_ok is True and c.tail_ok is True and c.verdict_same is True
    assert (c.size_kind, c.size, c.reasons) == ("estimate", 0.0625, ())
    assert c.sets_d1 == "pt" and c.sets_d2 == "pt"


def test_k5_dyadic_not_negligible_case() -> None:
    """(d1, d2) = (1/16, 1/32) gives S = 1/8: both ratio conditions hold, S >= 0.1, class X.

    The size is the estimate S * hw = 1/8 (both ratio conditions hold), the flag is no.
    """
    c = lm.classify(arms3(est(0.0), est(0.0625), est(0.09375)), tail=0.25)
    assert (c.cls, c.flag, c.s) == ("X", "no", 0.125)
    assert (c.size_kind, c.size) == ("estimate", 0.125)
    assert any("not below 0.1" in r for r in c.reasons)


@pytest.mark.parametrize(("size", "cls", "flag"), [(0.09, "N", "yes"), (0.10, "X", "no"),
                                                    (0.11, "X", "no")])
def test_k5_strict_flag_at_the_tenth(size: float, cls: str, flag: str) -> None:
    """E = 0.09, 0.10, 0.11 gives yes, no, no (strict, ``budget.below_tenth``, M9).

    ``strict_flag`` is checked against hand values; the same numbers through ``classify`` (pt moves
    by E at 15 to 30, then stays: d2 = 0 <= d1/2, tail 0) give N for 0.09 and X for 0.10 and 0.11
    (for 0.10 and 0.11 also by the bullet d1 >= 0.1).
    """
    assert lm.strict_flag(size, 1.0) == flag
    c = lm.classify(arms3(est(0.0), est(size), est(size)), tail=0.0)
    assert (c.cls, c.flag) == (cls, flag)
    assert lm.strict_flag(0.2, 2.0) == "no"        # 0.2 < 0.1 * 2.0 is false: the bound is strict
    assert lm.strict_flag(0.19999, 2.0) == "yes"
    assert lm.strict_flag(None, 1.0) == "not estimated"
    assert lm.strict_flag(0.05, math.inf) == "not estimated: interval unbounded"


def test_k5_zero_changes_are_negligible() -> None:
    """d1 = d2 = 0 is allowed (0 <= 0/2): class N with size 0."""
    c = lm.classify(arms3(est(0.5), est(0.5), est(0.5)), tail=0.0)
    assert (c.cls, c.s, c.size) == ("N", 0.0, 0.0)


def test_k5_signed_ratios_and_the_limiting_component() -> None:
    """Signed r_pt, r_lo, r_hi relative to hw, and the component that sets d1 (hand values).

    Design arm: pt 0.5, interval [0, 1] (hw = 1/2). At 30: pt 0.25 (D = -1/2), lo 1/8 (+1/4),
    hi 1 (0). At 60: pt 0.25, lo 1/8, hi 1 (D2 = 0). d1 = 1/2 is set by pt; a tie goes to the
    first of pt, lo, hi.
    """
    c = lm.classify(arms3(est(0.5, 0.0, 1.0), est(0.25, 0.125, 1.0), est(0.25, 0.125, 1.0)),
                    tail=0.0)
    assert c.hw == 0.5
    assert c.r1 == {"pt": -0.5, "lo": 0.25, "hi": 0.0} and c.r2 == {"pt": 0.0, "lo": 0.0, "hi": 0.0}
    assert (c.d1, c.sets_d1, c.cls) == (0.5, "pt", "X")
    tie = lm.classify(arms3(est(0.0), est(0.25, -0.75, 1.0), est(0.25, -0.75, 1.0)), tail=0.0)
    assert (tie.d1, tie.sets_d1) == (0.25, "pt")


def test_k5_ratio_fails_gives_u() -> None:
    """d2 > d1/2 with S < 0.1 and no verdict change: not certified (U), size 'unsupported'."""
    c = lm.classify(arms3(est(0.0), est(0.03125), est(0.0625)), tail=0.0)
    assert c.ratio_ok is False and (c.cls, c.flag, c.size_kind) == ("U", "no", "unsupported")
    assert c.size == 0.03125  # d1 * hw
    assert any("more than half" in r for r in c.reasons)


@pytest.mark.parametrize("tail", [0.5000001, 1.0, math.inf, None])
def test_k5_tail_above_a_half_or_absent_is_not_certified(tail: float | None) -> None:
    """r_A > 1/2, infinite, or no Part A: class U even with a tiny S (the tail is not supported)."""
    c = lm.classify(arms3(est(0.0), est(0.015625), est(0.015625)), tail=tail)
    assert (c.cls, c.flag, c.tail_ok) == ("U", "no", False)


def test_k5_a_changed_verdict_is_class_x() -> None:
    """A verdict that differs among the arms is X whatever the sizes (a lower size d1 * hw)."""
    c = lm.classify(arms3(est(0.0), est(0.015625, verdict="inconclusive"), est(0.015625)), tail=0.0)
    assert (c.cls, c.flag, c.verdict_same) == ("X", "no", False)
    assert c.reasons[0].startswith("the verdict differs among the arms")


def test_k5_large_first_change_is_x_with_lower_size_when_the_ratio_fails() -> None:
    """d1 >= 0.1 is X; the size is S*hw if both ratio conditions hold, else 'at least d1*hw'."""
    held = lm.classify(arms3(est(0.0), est(0.25), est(0.375)), tail=0.0)
    assert (held.cls, held.size_kind, held.size) == ("X", "estimate", 0.25 + 2 * 0.125)
    broke = lm.classify(arms3(est(0.0), est(0.25), est(0.75)), tail=0.0)
    assert (broke.cls, broke.size_kind, broke.size) == ("X", "lower", 0.25)


def test_k5_structural_switch_blocks_n_and_the_third_bullet() -> None:
    """A structural switch makes an otherwise-N part U, and an S >= 0.1 estimate U (not X)."""
    small = lm.classify(arms3(est(0.0), est(0.03125), est(0.046875)), tail=0.5,
                        structural=("the chosen K differs",))
    assert (small.cls, small.flag) == ("U", "no") and "the chosen K differs" in small.reasons
    big = lm.classify(arms3(est(0.0), est(0.0625), est(0.09375)), tail=0.25,
                      structural=("the chosen K differs",))
    assert (big.cls, big.flag) == ("U", "no")
    clear = lm.classify(arms3(est(0.0), est(0.25), est(0.25)), tail=0.0,
                        structural=("the chosen K differs",))
    assert clear.cls == "X"  # d1 >= 0.1 does not need the structural bullet


def test_k5_infinite_endpoint_or_bad_half_width_is_u_without_exception() -> None:
    """An infinite endpoint at any arm, hw <= 0 or hw not finite: U; if the verdicts differ: X."""
    infinite = lm.classify(arms3(est(0.0), est(0.0, lo=-math.inf), est(0.0)), tail=0.0)
    assert (infinite.cls, infinite.flag) == ("U", "no") and infinite.d1 is None
    assert "not computable" in infinite.reasons[-1]
    flipped = lm.classify(arms3(est(0.0), est(0.0, lo=-math.inf, verdict="inconclusive"),
                                est(0.0)), tail=0.0)
    assert flipped.cls == "X"
    for bad in (est(0.0, lo=1.0, hi=1.0), est(0.0, lo=1.0, hi=0.0), est(0.0, lo=0.0, hi=math.inf),
                est(0.0, lo=math.nan, hi=1.0)):
        assert lm.classify(arms3(bad, bad, bad), tail=0.0).cls == "U"


def test_k5_missing_part_or_arm_is_u_and_never_an_exception() -> None:
    """A part absent (None, or without its interval) at one arm gives U; no exception."""
    assert lm.classify({15: est(0.0), 30: est(0.0), 60: None}, tail=0.0).cls == "U"
    assert lm.classify({15: est(0.0), 30: Est(pt=0.0, verdict="pass"), 60: est(0.0)}, tail=0.0).cls == "U"
    with pytest.raises(ValueError):
        lm.classify({15: est(0.0)}, tail=0.0)


def test_k5_without_a_60_arm_the_tail_cannot_be_bounded() -> None:
    """Two arms: no N and no S; X if d1 >= 0.1 or the verdict changed, else U."""
    quiet = lm.classify({15: est(0.0), 30: est(0.015625)}, tail=0.0)
    assert (quiet.cls, quiet.s, quiet.d2) == ("U", None, None)
    loud = lm.classify({15: est(0.0), 30: est(0.25)}, tail=0.0)
    assert (loud.cls, loud.size_kind, loud.size) == ("X", "lower", 0.25)


def test_k5_endpoint_limited_label_and_point_only_class() -> None:
    """If the point alone would give another class, the part is labelled endpoint-limited at B.

    Reference: hand dyadic numbers. The point never moves; the lower endpoint moves by 1/4 of hw
    at 15 to 30: the full rule gives X (d1 = 1/4 >= 0.1), the point alone N.
    """
    flat = est(0.0)
    moved = est(0.0, lo=-0.75, hi=1.0)
    arms = {k: results_with_h3c(v, bootstrap=500) for k, v in
            {15: flat, 30: moved, 60: moved}.items()}
    row = lm.build_comparison(arms, probe=probe_with_tail(0.0))["qoi"]["lorenz63"]["H3c"]["all"]
    assert row["classification"]["cls"] == "X" and row["class_point_only"] == "N"
    assert row["endpoint_limited"] == "endpoint-limited at B = 500"


# ------------------------------------------------------------------------------- tail ratio
@pytest.mark.parametrize(("f", "t", "expected"), [
    ((10, 4), (5.0, 2.0), 0.4), ((10, 5), (8.0, 2.0), 0.5), ((4, 0), (3.0, 0.0), 0.0),
    ((0, 3), (3.0, 1.0), math.inf), ((0, 0), (0.0, 0.0), 0.0), ((8, 2), (2.0, 3.0), 1.5),
    ((6, 3), (0.0, 1.0), math.inf),
    # rule R as written: r_A = 0 whenever F(60 to 120) = 0, whatever T (round-off steps after
    # convergence keep T positive); infinity if F(30 to 60) = 0 < F(60 to 120)
    ((4, 0), (3.0, 2.0), 0.0), ((0, 0), (1e-9, 2e-9), 0.0), ((7, 0), (0.0, 5.0), 0.0),
    ((0, 5), (0.0, 0.0), math.inf), ((0, 5), (4.0, 1.0), math.inf), ((5, 5), (4.0, 8.0), 2.0),
    ((5, 5), (8.0, 4.0), 1.0)])
def test_tail_ratio_cases(f: tuple, t: tuple, expected: float) -> None:
    """r_A of rule R, hand cases: 0 if F(60 to 120) = 0 (the converged case, T ignored), infinity
    if F(30 to 60) = 0 < F(60 to 120), else the larger of the F ratio and the T ratio."""
    assert lm.tail_ratio(f[0], f[1], t[0], t[1]) == expected


# ------------------------------------------------------------------------- results trees
def results_with_h3c(e: Est, *, bootstrap: int = 500, chosen_k: int = 4, n_test: int = 500,
                     n_sweep: int = 300) -> dict:
    """A results dict with an H3c block carrying ``e`` (and the config the report reads)."""
    block = {"A5_over_A4_mse": e.pt, "ci": [e.lo, e.hi] if e.lo is not None else None,
             "ci_mc_se": list(e.mc_se) if e.mc_se else None, "level": 0.98,
             "n_states": e.n, "n_failed_resamples": e.failed, "verdict": e.verdict}
    return {"config": {"bootstrap_resamples": bootstrap, "n_test": n_test, "n_test_sweep": n_sweep},
            "provenance": provenance_block(),
            "systems": {"lorenz63": {"H3c": block, "fitted": {"chosen_K": chosen_k}}},
            "verdicts": {"H3c": {"by_system": {"lorenz63": e.verdict}, "verdict": e.verdict}}}


def probe_with_tail(tail: float | None, arms: tuple = (15, 30, 60)) -> dict:
    """A Part A file of the stored shape from the same run as ``provenance_block`` (exact P0)."""
    block = provenance_block()
    return {"preset": "pilot", "seed_id": "DEV-0", "levels": [15, 30, 60, 120],
            "provenance": {"commit": block["commit"], "dirty": False, "packages": block["packages"],
                           "env": block["env"], "argv": ["probe"], "cpu": block["cpu"]["model"]},
            "systems": {"lorenz63": {"groups": {"H3c": {"tail_ratio": tail}},
                                     "p0": [{"arm": k, "mismatches": [],
                                             "arm_identity": {"start_utc": block["start_utc"],
                                                              "end_utc": block["end_utc"]}}
                                            for k in arms]}}}


def test_build_comparison_h3c_arithmetic_and_projection() -> None:
    """The comparison carries the classification, the arms' values, and the transfer factor.

    H3c: pt 1.0, 1.0625, 1.09375 with a design interval [0.5, 1.5] (hw = 1/2): D1 = 1/8, D2 = 1/16,
    so d1 = 0.125 >= 0.1, class X, S = 1/4 (both ratio conditions hold, tail 0.25), size S * hw =
    1/8. The transfer factor is sqrt(1000/500) = sqrt(2) for H3c (n_test), and S * factor is
    reported, not applied (the class stays X). Exact except the square root (hand: math.sqrt(2)).
    """
    arms = {15: results_with_h3c(est(1.0, 0.5, 1.5)), 30: results_with_h3c(est(1.0625, 0.5, 1.5)),
            60: results_with_h3c(est(1.09375, 0.5, 1.5))}
    report = lm.build_comparison(arms, probe=probe_with_tail(0.25))
    row = report["qoi"]["lorenz63"]["H3c"]["all"]
    c = row["classification"]
    assert (c["cls"], c["hw"], c["d1"], c["d2"], c["s"], c["size"]) == ("X", 0.5, 0.125, 0.0625,
                                                                         0.25, 0.125)
    assert row["arms"][60]["pt"] == 1.09375 and row["tail_ratio"] == 0.25
    assert row["transfer_factor"] == pytest.approx(math.sqrt(2.0), rel=1e-12)
    assert row["projected_s"] == pytest.approx(0.25 * math.sqrt(2.0), rel=1e-12)
    assert row["projected_flag"] == "no" and row["endpoint_limited"] is None
    assert report["halt"] == []  # the arms differ only where a PLP output can


def test_build_comparison_without_the_other_qois_and_with_missing_parts() -> None:
    """Absent QoIs are skipped; a part without its interval at one arm is U, with no exception."""
    arms = {15: results_with_h3c(est(1.0)), 30: results_with_h3c(est(1.0)),
            60: results_with_h3c(Est(pt=1.0, verdict="pass"))}
    report = lm.build_comparison(arms)
    assert list(report["qoi"]["lorenz63"]) == ["H3c"]
    c = report["qoi"]["lorenz63"]["H3c"]["all"]["classification"]
    assert c["cls"] == "U" and "not estimated" in c["reasons"][0]
    assert report["qoi"]["lorenz63"]["H3c"]["all"]["arms"][60]["lo"] is None


def test_build_comparison_flags_a_changed_regime_count_as_structural() -> None:
    """A change of A5's chosen K makes the H3c part not N (M7), with the reason in words."""
    arms = {15: results_with_h3c(est(1.0)), 30: results_with_h3c(est(1.0), chosen_k=5),
            60: results_with_h3c(est(1.0), chosen_k=5)}
    c = lm.build_comparison(arms, probe=probe_with_tail(0.0))["qoi"]["lorenz63"]["H3c"]["all"][
        "classification"]
    assert c["cls"] == "U" and any("chosen number of regimes" in r for r in c["reasons"])


def results_with_h2a(zero_pt: float, with_one: bool, interior_n: int = 100) -> dict:
    """A results dict with an H2a block of the stored shape (parts i, ii zero, interior, one)."""
    def part(point: float, n: int) -> dict:
        return {"partial_corr": point, "ci": [point - 1.0, point + 1.0], "ci_mc_se": [0.1, 0.1],
                "n_states": n, "n_failed_resamples": 0, "verdict": "pass"}
    part_ii = {"zero": part(zero_pt, 500), "interior": part(0.0, interior_n)}
    if with_one:
        part_ii["one"] = part(0.0, 500)
    return {"config": {"bootstrap_resamples": 500, "n_test": 500, "n_test_sweep": 300},
            "provenance": provenance_block(),
            "systems": {"lorenz63": {"H2a": {
                "median_range": 0.0625, "range_ci": [0.0, 0.125], "ci_mc_se": [0.01, 0.02],
                "range_n_failed_resamples": 1, "n_eligible_states": 321, "part_i_verdict": "pass",
                "part_ii": part_ii, "n_w_zero": 11, "n_w_one": 12}}}}


def test_h2a_parts_are_read_one_by_one_and_a_part_in_one_arm_only_is_structural() -> None:
    """H2a(i) and the parts of H2a(ii) are separate rows; the 'one' part at one arm only is U.

    Reference: the stored shape of ``analysis.h2a_initial_segments`` and ``h2a_part_ii`` (keys
    typed by hand from their docstrings): the point of (i) is ``median_range`` with ``range_ci``,
    that of each part of (ii) is ``partial_corr`` with ``ci``.
    """
    arms = {15: results_with_h2a(0.0, with_one=False), 30: results_with_h2a(0.0, with_one=True),
            60: results_with_h2a(0.0, with_one=True)}
    report = lm.build_comparison(arms)
    rows = report["qoi"]["lorenz63"]
    assert sorted(rows) == ["H2a(i)", "H2a(ii)"] and sorted(rows["H2a(ii)"]) == [
        "interior", "one", "zero"]
    part_i = rows["H2a(i)"]["all"]
    assert part_i["arms"][15]["pt"] == 0.0625 and part_i["arms"][15]["lo"] == 0.0
    assert part_i["arms"][15]["n"] == 321 and part_i["arms"][15]["failed"] == 1
    one = rows["H2a(ii)"]["one"]["classification"]
    assert one["cls"] == "U" and "not estimated at the 15 arm" in one["reasons"][0]
    zero = rows["H2a(ii)"]["zero"]["classification"]      # present at every arm: no structural reason
    assert zero["cls"] == "U" and zero["reasons"] == ("no Part A tail ratio",)
    assert report["membership"]["lorenz63"][15]["H2a.n_w_zero"] == 11
    assert report["membership"]["lorenz63"][30]["H2a.part_ii.one.n_states"] == 500


def test_verdict_table_and_single_statistics() -> None:
    """A changed verdict is flagged; natural-unit changes of single statistics are exact."""
    def tree(slope: float, verdict: str) -> dict:
        return {"config": {}, "systems": {"lorenz63": {"H1b": {"PLP": {"slope": slope}}}},
                "verdicts": {"H1b": {"by_system": {"lorenz63": verdict}, "verdict": verdict}}}
    table = lm.build_comparison({15: tree(1.0, "pass"), 30: tree(1.25, "pass"),
                                 60: tree(1.375, "fail")})["verdicts"]
    entry = table["H1b"]
    assert entry["changed"] is True and entry["overall"] == {15: "pass", 30: "pass", 60: "fail"}
    stat = entry["single_statistics"]["lorenz63/PLP.slope"]
    assert (stat["delta_15_30"], stat["delta_30_60"]) == (0.25, 0.125)


# ------------------------------------------------------------------------------ leaf compare
def bits(x: float) -> bytes:
    return struct.pack("<d", x)


def test_k3_bitwise_comparison_rules() -> None:
    """0.0 and -0.0 differ; NaN equals NaN with the same bits; int and float differ; bool and int
    differ; a key or list item on one side only differs; provenance and every 'seconds' are ignored.

    Reference: IEEE bit patterns by ``struct.pack`` (typed in the test) and the rules of K3.
    """
    base = {"a": 0.0, "b": float("nan"), "c": 1, "d": True, "e": [1.0, 2.0], "f": {"x": None},
            "provenance": {"git": "abc"}, "seconds": 1.0, "g": {"seconds": 2.0, "keep": 3.0}}
    same = json.loads(json.dumps(base).replace('"abc"', '"def"').replace("1.0, \"g\"", "9.5, \"g\""))
    assert lm.differing_leaves(base, same) == []   # provenance and the top-level seconds differ
    assert bits(0.0) != bits(-0.0) and bits(float("nan")) == bits(float("nan"))
    def diff(**changes: object) -> list:
        other = {**base, **changes}
        return [p for p in lm.differing_leaves(base, other)]
    assert diff(a=-0.0) == [("a",)]
    assert diff(c=1.0) == [("c",)] and diff(d=1) == [("d",)]
    assert diff(e=[1.0]) == [("e", 1)] and diff(e=[1.0, 2.0, 3.0]) == [("e", 2)]
    assert diff(f={}) == [("f",), ("f", "x")]   # an empty container is a leaf of its own
    assert diff(g={"seconds": 99.0, "keep": 3.0}) == []   # a nested 'seconds' is excluded too
    assert diff(g={"seconds": 2.0, "keep": 4.0}) == [("g", "keep")]
    assert diff(h=1.0) == [("h",)]
    assert lm.differing_leaves({"b": float("nan")}, {"b": float("nan")}) == []
    assert lm.differing_leaves({"x": 1.0 + 2.0**-52}, {"x": 1.0}) == [("x",)]  # one ulp


def test_identical_subcommand_exit_codes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """``identical`` returns 0 for equal files (up to provenance and seconds) and 1 otherwise."""
    a, b, c = (tmp_path / n for n in ("a.json", "b.json", "c.json"))
    a.write_text(json.dumps({"x": 1.5, "provenance": {"t": 1}, "seconds": 3.0}))
    b.write_text(json.dumps({"x": 1.5, "provenance": {"t": 2}, "seconds": 4.0}))
    c.write_text(json.dumps({"x": 2.5, "provenance": {"t": 2}, "seconds": 4.0}))
    assert lm.main(["identical", str(a), str(b)]) == 0
    assert "1 leaves compared" in capsys.readouterr().out
    assert lm.main(["identical", str(a), str(c)]) == 1
    assert "differs: x" in capsys.readouterr().out


C0_EXAMPLES: list[tuple] = [
    ("config", "seed"),
    ("estimators", "('lorenz63', 7, 5, 0.01)", "chosen_width"),
    ("estimators", "('lorenz63', 7, 5, 0.01)", "val_loss_by_width", "32"),
    ("systems", "rossler", "validation", "estimators", "('rossler', 7, 5, 0.01)", "chosen_width"),
    ("systems", "rossler", "validation", "estimators", "('rossler', 7, 5, 0.01)", "val_loss_by_width", "32"),
    ("systems", "chua", "context", "lambda_max"),
    ("systems", "chua", "validation", "gain_rel_err"),
    ("systems", "chua", "validation", "crlb_ratio_max"),
    ("systems", "chua", "validation", "km_max_abs_dev"),
    ("systems", "chua", "validation", "integrator_max_dev_sigma"),
    ("systems", "chua", "validation", "cp_median_vpt_lyapunov"),
    ("systems", "chua", "validation", "gate", "V5"),
    ("systems", "chua", "verification", "P2c", "tightness", "median"),
    ("systems", "chua", "H1a", "by_noise", "0.01", "ratio"),
    ("systems", "chua", "H1b", "CP", "slope"),
    ("systems", "chua", "H1c", "CP", "ci", 0),
    ("systems", "chua", "H1d", "rows", "nhat", "spearman"),
    ("systems", "chua", "scores", "A0", "mse_href"),
    ("systems", "chua", "km_curves", "A0", 3),
    ("systems", "chua", "oracle_recovery", "mse_at_href", "A0"),
    ("systems", "chua", "handling", "oracles", "test", "counts", "oracle_nonfinite"),
    ("systems", "chua", "handling", "cells", "base|rho=0.01|n_lib=10000|core", "denominators", "estimates"),
    ("systems", "chua", "handling", "cells", "base|rho=0.01|n_lib=10000|core", "by_kind", "oracle", "denominators", "states"),
    ("systems", "chua", "handling", "cells", "base|rho=0.01|n_lib=10000|core", "counts", "error_clips_cp"),
    ("systems", "chua", "handling", "cells", "base|rho=0.01|n_lib=10000|core", "by_kind", "eval", "counts", "zero_variance_corr_cp"),
    ("systems", "chua", "H2a", "part_ii", "zero", "n_states"),
    ("systems", "chua", "H2b", "library_change", "n_states"),
    ("systems", "chua", "H3c", "n_states"),
    ("robustness", "rossler", "D=10", "H1b", "CP", "slope"),
    ("robustness", "rossler", "k=5", "mse_href", "A0"),
    ("handling", "robustness", "rossler", "oracles", "test|D=10", "denominators", "states"),
    ("handling", "robustness", "rossler", "cells", "D=10|rho=0.01|n_lib=10000|core", "denominators", "estimates"),
    ("handling", "robustness", "rossler", "cells", "D=10|rho=0.01|n_lib=10000|core", "by_kind", "oracle", "denominators", "states"),
    ("handling", "robustness", "rossler", "cells", "D=10|rho=0.01|n_lib=10000|core", "counts", "error_clips_cp"),
    ("handling", "robustness", "rossler", "cells", "D=10|rho=0.01|n_lib=10000|core", "by_kind", "oracle", "counts", "zero_variance_corr_cp"),
]


def test_c0_one_example_per_pattern_matches_that_pattern() -> None:
    """Each pattern of the M5 list matches its own example path, and every pattern has an example.

    Reference: the paths typed above from the stored shape (``results.json`` of a smoke run). A
    pattern that matches nothing would be a dead guard; the producer line is non-empty for each.
    """
    patterns = lm.C0_PATTERNS
    assert len(C0_EXAMPLES) == len(patterns)
    for example, (pattern, why) in zip(C0_EXAMPLES, patterns):
        assert lm._match(example, pattern), example
        assert why.strip() and lm.c0_pattern_of(example) is not None
    assert lm.c0_pattern_of(("config", "estimator_refine_steps")) is None   # the one varied leaf


@pytest.mark.parametrize("path", [
    ("systems", "chua", "H2a", "median_range"), ("systems", "chua", "H2a", "part_ii", "interior", "n_states"),
    ("systems", "chua", "H2b", "noise", "mean_state_spearman"), ("systems", "chua", "H3c", "ci"),
    ("systems", "chua", "H1b", "PLP", "slope"), ("systems", "chua", "H1c", "PLP", "median_ratio"),
    ("systems", "chua", "scores", "A4", "mse_href"), ("systems", "chua", "scores", "A0", "regret", "1LT"),
    ("systems", "chua", "scores", "A0", "agreement_href"),
    ("systems", "chua", "handling", "cells", "c", "lm", "median_residual"),
    ("systems", "chua", "handling", "cells", "c", "counts", "nu_replacements"),
    ("systems", "chua", "handling", "cells", "c", "by_kind", "oracle", "counts", "lm_nonfinite_cost"),
    ("systems", "chua", "validation", "convergence", "pass"), ("systems", "chua", "validation", "gate", "V4"),
    ("systems", "chua", "validation", "gate", "gate_pass"), ("systems", "chua", "H1d", "rows", "analog_seed", "spearman"),
    ("systems", "chua", "fitted", "chosen_K"), ("handling", "totals", "nu_replacements"),
    ("verdicts", "H2a", "verdict"), ("config",),
])
def test_c0_does_not_cover_leaves_that_can_read_a_plp_output(path: tuple) -> None:
    """Leaves that read PLP arrays are not in the C0 list (so a change there is allowed)."""
    assert lm.c0_pattern_of(path) is None


def test_c0_violations_pick_only_the_listed_leaves() -> None:
    """A differing C0 leaf is a violation with its producer line; a differing QoI leaf is not."""
    diffs = [("config", "estimator_refine_steps"), ("systems", "chua", "H3c", "ci", 0),
             ("systems", "chua", "H3c", "n_states"), ("config", "seed")]
    bad = lm.c0_violations(diffs)
    assert [p for p, _ in bad] == [("systems", "chua", "H3c", "n_states"), ("config", "seed")]
    assert all(why for _, why in bad)


def test_report_halts_on_a_c0_violation_and_on_no_difference() -> None:
    """A C0 leaf that differs between arms halts; so does an arm pair that differs in nothing else
    than the budget itself (K4: the differing-leaf set must not be empty, the budget leaf excepted).

    Reference: the rules of the plan, applied by hand to trees that differ in one leaf. The 15 and
    30 arms differ in the H3c point (a leaf that reads PLP output): no halt. The 30 and 60 arms are
    copies bar ``config.estimator_refine_steps``: halt. A third arm that changes ``H3c.n_states``
    (a C0 leaf) halts with that path named.
    """
    def arm(steps: int, e: Est) -> dict:
        tree = results_with_h3c(e)
        tree["config"]["estimator_refine_steps"] = steps
        return tree

    moved = est(1.0625)
    quiet = lm.build_comparison({15: arm(15, est(1.0)), 30: arm(30, moved)})
    assert quiet["halt"] == [] and quiet["c0"]["pairs"]["15-30"]["n_effect"] >= 1
    stuck = lm.build_comparison({15: arm(15, est(1.0)), 30: arm(30, moved), 60: arm(60, moved)})
    assert stuck["halt"] == ["no leaf differs between the 30 and 60 arms apart from the budget "
                             "itself: the knob has no effect (K4)"]
    broken = arm(30, moved)
    broken["systems"]["lorenz63"]["H3c"]["n_states"] = 499
    report = lm.build_comparison({15: arm(15, est(1.0)), 30: broken})
    assert [h for h in report["halt"] if h.startswith("C0: ")] == [
        "C0: systems/lorenz63/H3c/n_states (analysis.h3c_ratio: len(a5_state_mse))"]


# --------------------------------------------------------------------------------------- P1
def lm_block(n: int, median: float | None, p95: float | None, above: float, nonfinite: int,
             nodecr: float, iters: float) -> dict:
    return {"n_estimates": n, "median_residual": median, "p95_residual": p95,
            "fraction_above_chi2": above, "nonfinite_residuals": nonfinite,
            "fraction_no_decrease": nodecr, "median_iterations": iters}


def arm_with_lm(block: dict) -> dict:
    cell = {"lm": {**block, "by_kind": {"oracle": block, "eval": {**block, "n_estimates": 0}}}}
    return {"systems": {"lorenz63": {"handling": {"cells": {"base|core": cell}}}}}


def test_p1_exact_monotonicity_passes_with_equality() -> None:
    """Non-increasing residual summaries and non-decreasing iterations pass, equality included.

    Reference: the prefix property (the scan of length 2k runs the length-k scan first): hand
    numbers that fall (or stay) with k. The number of comparisons is 6 keys x 2 steps x 2 nodes
    (pooled and oracle; eval has no estimates).
    """
    arms = {15: arm_with_lm(lm_block(10, 4.0, 9.0, 0.5, 2, 0.25, 9.0)),
            30: arm_with_lm(lm_block(10, 2.0, 9.0, 0.25, 1, 0.0, 12.0)),
            60: arm_with_lm(lm_block(10, 2.0, 5.0, 0.125, 1, 0.0, 12.0))}
    checked, bad = lm.check_p1_partb(arms)
    assert bad == [] and checked == 24


@pytest.mark.parametrize(("key", "arm_30"), [
    ("median_residual", 4.5), ("p95_residual", 9.5), ("fraction_above_chi2", 0.55),
    ("nonfinite_residuals", 3), ("fraction_no_decrease", 0.3), ("median_iterations", 8.0)])
def test_p1_a_violation_in_any_key_is_reported(key: str, arm_30: float) -> None:
    """Moving one key the wrong way between 15 and 30 gives exactly that violation (no tolerance)."""
    block = lm_block(10, 4.0, 9.0, 0.5, 2, 0.25, 9.0)
    wrong = {**block, key: arm_30}
    checked, bad = lm.check_p1_partb({15: arm_with_lm(block), 30: arm_with_lm(wrong)})
    assert len(bad) == 2 and all(key in line for line in bad)   # pooled and oracle


def test_p1_none_reads_as_infinity_and_estimate_counts_must_agree() -> None:
    """A residual median that goes from finite to None (inf) is a violation; None to finite is not;
    a different number of estimates is reported."""
    finite, none = lm_block(10, 4.0, 9.0, 0.5, 2, 0.25, 9.0), lm_block(10, None, None, 0.5, 2, 0.25, 9.0)
    assert lm.check_p1_partb({15: arm_with_lm(none), 30: arm_with_lm(finite)})[1] == []
    assert len(lm.check_p1_partb({15: arm_with_lm(finite), 30: arm_with_lm(none)})[1]) == 4
    other = lm_block(11, 4.0, 9.0, 0.5, 2, 0.25, 9.0)
    assert "n_estimates differs" in lm.check_p1_partb({15: arm_with_lm(finite),
                                                       30: arm_with_lm(other)})[1][0]


# ----------------------------------------------------------------------- K6(a): Part A arrays
def seg(change: np.ndarray, *, rho: float = 0.5, nu_ref: float = 2.0, serr: float = 1.0,
        replaced: dict | None = None, levels: tuple = (15, 30, 60), name: str = "s") -> "lm.Segment":
    """A segment whose estimate moves by ``change[i, j]`` (first coordinate) from level to level.

    ``s_15 = 0``, ``s_30 = change``, ``s_60 = 2 change``: the doublings 15 to 30 and 30 to 60 both
    move by ``change``. ``nu`` is 7 at 15 and 9 at 60 but ``nu_ref`` at 30, so a wrong reference
    level would change every ratio. ``rho * nu_ref = 1`` by default.
    """
    n, m = change.shape
    shape = (n, m, 3)
    s = {}
    for i, level in enumerate(levels):
        arr = np.zeros(shape)
        arr[..., 0] = i * change
        s[level] = arr
    ones = np.ones((n, m))
    nu = {level: np.full((n, m), {15: 7.0, 30: nu_ref, 60: 9.0, 120: 11.0}[level])
          for level in levels}
    flags = {level: np.zeros((n, m), dtype=bool) for level in levels}
    flags.update(replaced or {})
    return lm.Segment(
        name=name, rho=rho, dof=4, s=s, nu=nu, c={k: ones * 100.0 for k in levels},
        accepted={k: np.full((n, m), 5, dtype=np.int32) for k in levels},
        late={k: np.zeros((n, m), dtype=np.int32) for k in levels}, replaced=flags,
        serr={k: ones * serr for k in levels}, cp_sq=np.ones((n, 3)),
        sq_plp={k: np.ones((n, 3)) for k in levels}, cross={k: np.zeros((n, 3)) for k in levels},
        counts={k: {name: 0 for name in lm.LM_COUNTS} for k in levels})


def test_k6a_doubling_stats_closed_forms_cluster_larger() -> None:
    """Fractions, quantiles, T and the SEs of a hand-built case (blocks of 5 states dominate).

    Ten states, four draws each. States 0 to 4 move by 1/16 (ratio 1/16 < 0.1), states 5 to 9 by 1/2
    (ratio 1/2 > 0.1), since ``rho * nu_30 = 1``. Hand: F = 20 of 40, fraction 1/2; T = 20/16 + 10 =
    11.25 exactly; the pooled ratios sorted are 20 x 1/16 then 20 x 1/2, so q50 = (1/16 + 1/2)/2 =
    9/32 (index 19.5), q90 = 1/2 (index 35.1), q99 = 1/2, max = 1/2, mean = 9/32. Per-state fractions
    are [0]*5 + [1]*5: the clustered SE is ``sqrt(2.5/9)/sqrt(10) = sqrt(5/180)``; the means of the two
    blocks are 0 and 1, so the batch-means SE is ``sd([0, 1], ddof=1)/sqrt(2) = 1/2``, the larger.
    """
    change = np.vstack([np.full((5, 4), 0.0625), np.full((5, 4), 0.5)])
    stats = lm.doubling_stats([seg(change)], 15, 30)
    assert (stats["n"], stats["n_excluded"], stats["F"], stats["fraction"]) == (40, 0, 20, 0.5)
    assert (stats["n_states_no_valid_draw"], stats["n_states_dropped_from_blocks"]) == (0, 0)
    assert stats["T"] == 11.25
    assert (stats["q50"], stats["q90"], stats["q99"], stats["max"], stats["mean"]) == (
        0.28125, 0.5, 0.5, 0.5, 0.28125)
    assert stats["se_cluster"] == pytest.approx(math.sqrt(5.0 / 180.0), rel=1e-12)
    assert stats["se_block5"] == pytest.approx(0.5, rel=1e-12) and stats["se"] == stats["se_block5"]


def test_k6a_cluster_se_is_the_larger_when_blocks_agree() -> None:
    """Per-state fractions [0, 1/4, 1/2, 3/4, 1] twice: every block mean is 1/2, so the block SE is 0
    and the clustered SE ``sqrt(1.25/9)/sqrt(10)`` (ddof = 1; ddof = 0 would give another number) is used."""
    change = np.zeros((10, 4))
    for i, p in enumerate([0, 1, 2, 3, 4] * 2):             # p draws above out of 4
        change[i] = [0.5] * p + [0.0625] * (4 - p)
    stats = lm.doubling_stats([seg(change)], 15, 30)
    assert stats["se_block5"] == 0.0
    assert stats["se_cluster"] == pytest.approx(math.sqrt(1.25 / 9.0) / math.sqrt(10.0), rel=1e-12)
    assert stats["se_cluster"] != pytest.approx(math.sqrt(1.25 / 10.0) / math.sqrt(10.0), rel=1e-3)
    assert stats["se"] == stats["se_cluster"]


def test_k6a_reference_nu_is_the_30_iteration_estimate_at_every_doubling() -> None:
    """Both doublings divide by rho * nu at 30 (here 1), not by nu at the level itself.

    nu is 7 at 15 and 9 at 60 in ``seg``: dividing by those would give T = 40 * (1/2)/(0.5 * 7) and
    another count above. With the reference level, 15 to 30 and 30 to 60 both give T = 40 * 0.5 = 20.
    """
    stats = lm.doubling_stats([seg(np.full((10, 4), 0.5))], 15, 30)
    later = lm.doubling_stats([seg(np.full((10, 4), 0.5))], 30, 60)
    assert stats["T"] == later["T"] == 20.0
    assert stats["F"] == later["F"] == 40


def test_k6a_replaced_estimates_are_excluded_at_any_level_and_counted() -> None:
    """An estimate replaced at any one level leaves every ratio (and is counted), the rest stay.

    State 0, draw 0 is replaced at level 60 only; state 9, draw 3 at level 15 only. Both are
    excluded from the 15 to 30 stats: n = 38, n_excluded = 2, and the per-state fraction of state 0
    is taken over its 3 remaining draws.
    """
    change = np.full((10, 4), 0.5)
    flags = {60: np.zeros((10, 4), dtype=bool), 15: np.zeros((10, 4), dtype=bool)}
    flags[60][0, 0] = True
    flags[15][9, 3] = True
    stats = lm.doubling_stats([seg(change, replaced=flags)], 15, 30)
    assert (stats["n"], stats["n_excluded"], stats["F"]) == (38, 2, 38)
    assert stats["T"] == 19.0 and stats["fraction"] == 1.0


def test_k6a_fraction_above_the_realized_error_uses_the_30_iteration_error() -> None:
    """F_true counts change > 0.1 ||s_30 - s_true||: with serr = 10 the threshold is 1 (none above)."""
    change = np.full((10, 4), 0.5)
    assert lm.doubling_stats([seg(change, serr=10.0)], 15, 30)["F_true"] == 0
    assert lm.doubling_stats([seg(change, serr=1.0)], 15, 30)["F_true"] == 40


def test_k6a_chi2_crossings_shares_and_transitions() -> None:
    """Above-to-below and below-to-above counts and the shares of T and F they carry (hand case).

    One state, four draws, rho = 1, threshold 10 (a stub for ``gof_threshold``). Costs at 15:
    [20, 20, 5, 5], at 30: [20, 5, 5, 20]: draw 1 crosses above to below, draw 3 below to above
    (impossible in the real loop, P1; here it proves the counter). Changes 15 to 30 are
    [0.5, 0.25, 0.0625, 0.0625] and ``rho nu_30 = 1``: T = 0.875, crossing draw 1 carries 0.25, so
    share_T = 2/7; F (above 0.1) = 2 (draws 0, 1), crossing carries 1, share_F = 1/2.
    """
    segment = seg(np.array([[0.5, 0.25, 0.0625, 0.0625]]), rho=1.0, nu_ref=1.0)
    segment.c[15] = np.array([[20.0, 20.0, 5.0, 5.0]])
    segment.c[30] = np.array([[20.0, 5.0, 5.0, 20.0]])
    segment.c[60] = np.array([[5.0, 5.0, 5.0, 5.0]])
    out = lm.chi2_stats([segment], (15, 30, 60), lambda dof: 10.0)
    assert out["above"] == {"15": 2, "30": 2, "60": 0} and out["n"] == 4
    assert out["above_to_below"] == {"15->30": 1, "30->60": 2}
    assert out["below_to_above"] == {"15->30": 1, "30->60": 0}
    assert out["share_T"]["15->30"] == pytest.approx(2.0 / 7.0, rel=1e-12)
    assert out["share_F"]["15->30"] == 0.5 and out["still_above_last"] == 0


def test_k6a_p1_per_estimate_counts_violations() -> None:
    """c rising or accepted falling between levels is counted per estimate (both 0 in a real run)."""
    segment = seg(np.full((2, 3), 0.5))
    assert lm.p1_stats([segment], (15, 30, 60)) == {
        "15->30": {"c_increase": 0, "accepted_decrease": 0},
        "30->60": {"c_increase": 0, "accepted_decrease": 0}}
    segment.c[30][0, 1] = 100.5
    segment.accepted[60][1, 2] = 4
    assert lm.p1_stats([segment], (15, 30, 60)) == {
        "15->30": {"c_increase": 1, "accepted_decrease": 0},
        "30->60": {"c_increase": 0, "accepted_decrease": 1}}


def test_k6a_weight_star_hand_values_and_the_package_formula() -> None:
    """w* = (E_P - C)/(E_C + E_P - 2C), clipped: hand values, and equal to ``oracle_weight``.

    Hand: (E_C, E_P, C) = (1, 1, 0) gives 1/2; (4, 1, 0) gives 1/5; (1, 4, 0) gives 4/5; (1, 4, 1)
    gives exactly 1 (C = E_C); (1, 1, 1) has zero curvature and gives 0 (the floor 1e-300).
    The independent reference is ``lpcstudy.oracle.oracle_weight`` on the same arrays.
    """
    from lpcstudy.oracle import oracle_weight
    e_c, e_p, c = (np.array(v, dtype=float) for v in ([1, 4, 1, 1, 1], [1, 1, 4, 4, 1],
                                                       [0, 0, 0, 1, 1]))
    w = lm.weight_star(e_c, e_p, c)
    assert w.tolist() == [0.5, 0.2, 0.8, 1.0, 0.0]
    package = oracle_weight(SimpleNamespace(sq_cp=e_c[:, None], sq_plp=e_p[:, None],
                                            cross=c[:, None]))[:, 0]
    assert np.array_equal(w, package)
    assert lm.weight_class(w).tolist() == [1, 1, 1, 2, 0]


def test_k6a_eligibility_and_transition_counts() -> None:
    """Eligibility is a leading run of at least two small horizons (rms <= 0.5, closed).

    Hand: squares 0.25 (rms 0.5, small), 1 (not small). Rows: (s, s, s) eligible; (s, n, s) run 1, not;
    (n, s, s) run 0, not; (s, s, n) run 2, eligible. Transition matrices count (before, after).
    """
    cp = np.array([[0.25, 0.25, 0.25], [0.25, 1.0, 0.25], [1.0, 0.25, 0.25], [0.1, 0.1, 2.0]])
    plp = np.full_like(cp, 0.1)
    assert lm.eligible(cp, plp, 0.5).tolist() == [True, False, False, True]
    assert lm.transitions(np.array([0, 1, 1, 2]), np.array([0, 2, 1, 2]), 3).tolist() == [
        [1, 0, 0], [0, 1, 1], [0, 0, 1]]


def test_k6a_mse_change_hand_values() -> None:
    """Relative change of the per-state MSE: zero denominators are counted and left out.

    sq_lo = [1, 2, 0, 4], sq_hi = [1.5, 2, 0.5, 3]: rel = [1/2, 0, 1/4] over the three defined
    states; sorted (0, 1/4, 1/2): median 1/4, mean 1/4, q90 at index 1.8 = 1/4 + 0.8/4 = 0.45.
    """
    out = lm.mse_change(np.array([1.0, 2.0, 0.0, 4.0]), np.array([1.5, 2.0, 0.5, 3.0]))
    assert out["n_zero_denominator"] == 1 and out["n_changed"] == 3
    assert (out["median"], out["mean"]) == (0.25, 0.25)
    assert out["q90"] == pytest.approx(0.45, rel=1e-12)


def test_k6a_group_report_has_the_tail_ratio_only_with_the_120_level() -> None:
    """r_A comes from the 30 to 60 and 60 to 120 doublings; None without the 120 level.

    Hand: 3 x 4 estimates move by 0.5 from 30 to 60 (F = 12, T = 6) and by 0.25 from 60 to 120
    (F = 12, T = 3), so r_A = max(12/12, 3/6) = 1. The 15 and 30 levels are the same segment.
    """
    n, m = 3, 4
    levels = (15, 30, 60, 120)
    segment = seg(np.full((n, m), 0.5), levels=(15, 30, 60))
    full = seg(np.full((n, m), 0.5), levels=levels)
    for k, shift in ((15, 0.0), (30, 0.5), (60, 1.0), (120, 1.25)):
        full.s[k] = np.zeros((n, m, 3))
        full.s[k][..., 0] = shift
    kwargs = dict(ref_column=0, long_columns=[0, 1, 2], limit=0.5)
    short = lm.group_report([segment], (15, 30, 60), lambda dof: 18.5, **kwargs)
    assert short["tail_ratio"] is None
    report = lm.group_report([full], levels, lambda dof: 18.5, **kwargs)
    assert report["doublings"]["30->60"]["F"] == 12 and report["doublings"]["60->120"]["F"] == 12
    assert report["doublings"]["30->60"]["T"] == 6.0 and report["doublings"]["60->120"]["T"] == 3.0
    assert report["tail_ratio"] == 1.0 and report["n_estimates"] == 12


# ----------------------------------------------------------------------------------- P0
def test_p0_pooled_summary_equals_lm_summary_of_the_joined_arrays_and_mismatches_are_listed() -> None:
    """Pooling joins the segments in order and calls ``lm_summary``; ``compare_p0`` is exact.

    Reference: ``lm_summary`` of the package on the arrays joined by hand (the pipeline builds the
    stored block the same way); the counts are sums. A one-ulp difference in the stored median is
    a mismatch; None equals None; extra stored keys (``by_kind``) are ignored.
    """
    from lpcstudy.estimation import lm_summary
    a, b = seg(np.full((2, 3), 0.5), name="a"), seg(np.full((1, 3), 0.5), name="b")
    a.c[15] = np.array([[1e-4, 2e-4, 5.0], [30.0, 1e-3, 2.0]])
    b.c[15] = np.array([[0.5, 0.25, 7.0]])
    a.counts[15]["nu_replacements"], b.counts[15]["nu_replacements"] = 2, 3
    summary, counts = lm.pooled_summary([a, b], 15, lm_summary)
    expected = lm_summary(np.concatenate([a.c[15].ravel(), b.c[15].ravel()]),
                          np.full(9, 5, dtype=np.int32), np.zeros(9, dtype=np.int32), 0.5, 4)
    assert summary == expected and counts["nu_replacements"] == 5
    stored = {**summary, "by_kind": {"oracle": {}}}
    assert lm.compare_p0(stored, counts, summary, counts) == []
    off = {**stored, "median_residual": float(np.nextafter(summary["median_residual"], 1.0))}
    assert len(lm.compare_p0(off, counts, summary, counts)) == 1
    assert lm.compare_p0({**stored, "median_residual": None}, counts, {**summary,
                         "median_residual": None}, counts) == []
    assert lm.compare_p0(stored, {**counts, "nu_replacements": 4}, summary, counts) == [
        "counts.nu_replacements: stored 4, probe 5"]


# ------------------------------------------------------------------------ chunks and specs
def test_chunk_rows_are_the_pipelines_chunks() -> None:
    """The row chunks are those of ``ensemble_moments``: 6000 // M states, the last one shorter.

    Reference: the hand arithmetic of the Mathematics check (pilot: 600 = 20 x 30, 300 = 10 x 30,
    500 = 16 x 30 + 20 with M = 200; eval M = 2: one chunk of 500), and the rows that
    ``ensemble_moments`` passes to ``forecast_draws`` (recorded with a stub that returns zero
    batches of the right shape).
    """
    sizes = lambda n, m: [len(r) for r in lm.chunk_rows(n, m)]
    assert sizes(600, 200) == [30] * 20 and sizes(300, 200) == [30] * 10
    assert sizes(500, 200) == [30] * 16 + [20] and sizes(500, 2) == [500]
    assert sizes(120, 30) == [120] and sizes(7, 6001) == [1] * 7
    import lpcstudy.ensemble as ensemble
    seen: list[np.ndarray] = []

    def stub(setup, library, split, states_idx, unit_noise, horizons, reference_horizon=None):
        seen.append(np.asarray(states_idx))
        n, m, d = unit_noise.shape
        z = np.zeros((n, m, len(horizons)))
        return ensemble.DrawBatch(
            cp_err=z, plp_err=z, analog_seed_sq=np.zeros((n, m)), est_seed_sq=np.zeros((n, m)),
            distance=np.zeros((n, m)), inputs=np.zeros((n, m, d)), est_states=np.zeros((n, m, 3)),
            est_nu=np.zeros((n, m)), analog_vecs=np.zeros((n, m, d)),
            handled=np.zeros((n, len(ensemble.DRAW_COUNTERS)), dtype=np.int64),
            clip_entries=dict.fromkeys(ensemble.ENTRY_COUNTERS, 0), lm_residual=np.zeros((n, m)),
            lm_accepted=np.zeros((n, m), dtype=np.int32), lm_late=np.zeros((n, m), dtype=np.int32))

    original = ensemble.forecast_draws
    ensemble.forecast_draws = stub
    try:
        ensemble.ensemble_moments(SimpleNamespace(noise=0.01), None, "test",
                                  np.zeros((500, 200, 7)), np.array([1, 2]))
    finally:
        ensemble.forecast_draws = original
    assert [r.tolist() for r in seen] == [r.tolist() for r in lm.chunk_rows(500, 200)]


def test_segment_specs_and_groups_follow_the_pilot_design() -> None:
    """Pilot: core oracle (200 draws) and eval (2) on all splits, and test rows 0 to 299 of each
    noise-sweep cell at a noise other than 1%. Groups: H2a the core test; H2b(i) the core test rows
    0 to 299 plus the sweeps; H2b(ii) the core test rows; H3c the core oracle and eval, all splits.

    Reference: ``config.PILOT`` values and ``pipeline.cell_id`` (the key of ``handling.cells``).
    """
    from lpcstudy.config import PILOT
    from lpcstudy.pipeline import cell_id
    specs = lm.segment_specs(PILOT)
    core = cell_id("base", 0.01, 10_000, True)
    assert core == "base|rho=0.01|n_lib=10000|core"
    assert [(s.cell == core, s.kind, s.split, s.n_draws) for s in specs[:6]] == [
        (True, "oracle", "construction", 200), (True, "oracle", "calibration", 200),
        (True, "oracle", "test", 200), (True, "eval", "construction", 2),
        (True, "eval", "calibration", 2), (True, "eval", "test", 2)]
    sweeps = specs[6:]
    assert [(s.cell, s.rho, s.rows) for s in sweeps] == [
        (cell_id("base", r, 10_000, False), r, slice(0, 300)) for r in (0.005, 0.02, 0.05)]
    groups = lm.groups_of(specs, PILOT)
    assert groups["H2a"] == [(f"{core}/oracle/test", slice(None))]
    assert groups["H2b(ii)"] == [(f"{core}/oracle/test", slice(0, 300))]
    assert [name for name, _ in groups["H2b(i)"]] == [f"{core}/oracle/test"] + [
        f"{s.cell}/oracle/test" for s in sweeps]
    assert [name.rsplit("/", 2)[1:] for name, _ in groups["H3c"]] == [
        ["oracle", "construction"], ["oracle", "calibration"], ["oracle", "test"],
        ["eval", "construction"], ["eval", "calibration"], ["eval", "test"]]
    assert len(groups["all"]) == 9


def test_kinds_are_the_pipelines() -> None:
    """``KINDS`` and ``CHUNK_TRAJ`` are the package's (the tool does not import ``pipeline``)."""
    import inspect
    from lpcstudy import ensemble, pipeline
    assert lm.KINDS == pipeline.KINDS
    for function in (ensemble.ensemble_moments, ensemble.evaluation_draws):
        assert inspect.signature(function).parameters["chunk_traj"].default == lm.CHUNK_TRAJ
    assert set(lm.LM_COUNTS) <= set(pipeline.CELL_COUNTERS)


# --------------------------------------------------------------- refusals, lock, environment
@pytest.mark.parametrize(("preset", "seed", "steps", "argv"), [
    ("smoke", "DEV-0", [15, 30, 60, 120], ["probe"]),
    ("pilot", "DEV-12", [15, 30], ["probe"]),
])
def test_refuse_reason_allows_development_requests(preset: str, seed: str, steps: list, argv: list) -> None:
    assert lm.refuse_reason(preset, seed, steps, argv) is None


@pytest.mark.parametrize(("preset", "seed", "steps", "argv"), [
    ("smoke", "CONF-1", [15, 30], ["x"]), ("smoke", "20261005", [15, 30], ["x"]),
    ("smoke", "dev-0", [15, 30], ["x"]), ("smoke", "DEV-01", [15, 30], ["x"]),
    ("smoke", "DEV-0;ls", [15, 30], ["x"]), ("full", "DEV-0", [15, 30], ["x"]),
    ("huge", "DEV-0", [15, 30], ["x"]), ("smoke", "DEV-0", [30, 60], ["x"]),
    ("smoke", "DEV-0", [15, 45], ["x"]), ("smoke", "DEV-0", [15], ["x"]),
    ("smoke", "DEV-0", [15, 30, 90], ["x"]),
    ("smoke", "DEV-0", [15, 30], ["--confirmatory"]), ("smoke", "DEV-0", [15, 30], ["--out", "runs/CONFIRMATORY"]),
])
def test_refuse_reason_refuses(preset: str, seed: str, steps: list, argv: list) -> None:
    """A non-DEV id, anything naming the sealed run (any case, any argument), the full preset and
    steps that are not 15 and its doublings are refused."""
    assert lm.refuse_reason(preset, seed, steps, argv) is not None


@pytest.mark.parametrize(("env", "expected"), [({}, "4"), ({"LPC_THREADS": ""}, "4"),
                                                ({"LPC_THREADS": "8"}, "8"), ({"LPC_THREADS": "99"}, "99")])
def test_thread_environment_matches_the_wrapper(env: dict, expected: str) -> None:
    """LPC_THREADS (default 4, as ``${LPC_THREADS:-4}``) sets OMP, MKL, OPENBLAS, PJRT_NPROC, NPROC;
    the device is the CPU; preallocation is off. Reference: ``tools/run_preset.sh`` (read by hand)."""
    out = lm.thread_environment(env)
    assert {out[k] for k in lm.THREAD_VARIABLES} == {expected} and out["LPC_THREADS"] == expected
    assert out["JAX_PLATFORMS"] == "cpu" and out["XLA_PYTHON_CLIENT_PREALLOCATE"] == "false"


@pytest.mark.parametrize("bad", ["0", "100", "four", "-1", "2.5", " 4"])
def test_thread_environment_refuses_a_bad_count(bad: str) -> None:
    with pytest.raises(ValueError):
        lm.thread_environment({"LPC_THREADS": bad})


def test_running_presets_uses_pgrep_and_fails_closed() -> None:
    """The check is ``pgrep -fa '[l]pcstudy --preset'``: exit 1 none, 0 lines, other raises."""
    calls: list = []

    def runner(code: int, out: str = ""):
        def run(command, **kwargs):
            calls.append(command)
            return SimpleNamespace(returncode=code, stdout=out)
        return run

    assert lm.running_presets(runner(1)) == []
    assert lm.running_presets(runner(0, "12 python -m lpcstudy --preset pilot\n")) == [
        "12 python -m lpcstudy --preset pilot"]
    with pytest.raises(RuntimeError):
        lm.running_presets(runner(2))
    assert calls[0] == ["pgrep", "-fa", "[l]pcstudy --preset"]


def test_probe_refusals_and_lock_through_main(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                              capsys: pytest.CaptureFixture[str]) -> None:
    """The probe refuses (64) a bad id or preset, an active preset run, and exits 75 if the lock is
    held, each before anything is created. Reference: the plan (64 refusal, 75 lock, never waits)."""
    import fcntl
    out = tmp_path / "out"
    base = ["probe", "--out", str(out), "--steps", "15", "30"]
    monkeypatch.setenv("LPC_THREADS", "4")
    assert lm.main([*base, "--preset", "full", "--seed-id", "DEV-0"]) == 64
    assert lm.main([*base, "--preset", "smoke", "--seed-id", "CONF-1"]) == 64
    monkeypatch.setattr(lm, "running_presets", lambda: ["99 python -m lpcstudy --preset pilot"])
    assert lm.main([*base, "--preset", "smoke", "--seed-id", "DEV-0"]) == 64
    assert "preset run is active" in capsys.readouterr().err
    monkeypatch.setattr(lm, "running_presets", lambda: [])
    lock = tmp_path / "lock"
    monkeypatch.setenv("LPC_GPU_LOCK", str(lock))
    with open(lock, "w") as holder:
        fcntl.flock(holder, fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert lm.main([*base, "--preset", "smoke", "--seed-id", "DEV-0"]) == 75
    assert "GPU busy" in capsys.readouterr().err
    assert not out.exists()


def test_the_tool_never_names_the_sealed_run_in_code_paths() -> None:
    """The tool has no sealed-run option, reads no sealed seed and no ledger or environment seed.

    Reference: a scan of the source text (the same kind of guard as the wrapper's)."""
    text = (ROOT / "tools" / "lm_doubling.py").read_text()
    assert "LPC_CONF" not in text and "ledger" not in text.lower()
    assert "confirmatory_seed" not in text and "LEDGER_PATH" not in text


# -------------------------------------------------------------- K6(b): the hazard (real LM)
EMBED, TAU = 7, 5
INTERVAL = 1.0 / (30 * 0.9056)


class StubNetwork:
    """A network whose ``predict`` returns the start the test sets."""

    width = 0

    def __init__(self) -> None:
        self.u0 = None

    def predict(self, inputs):
        import jax.numpy as jnp
        return jnp.asarray(self.u0)


def lorenz_world():
    """Lorenz-63 flow map, an independently simulated trajectory, a context, targets and truths."""
    import jax.numpy as jnp
    from lpcstudy.systems import SYSTEMS, make_flow_step, simulate_trajectory
    spec = SYSTEMS["lorenz63"]
    step = make_flow_step(spec, spec.params, INTERVAL)
    span = (EMBED - 1) * TAU
    burn = simulate_trajectory(step, jnp.asarray(spec.initial_state), 3000)
    traj = simulate_trajectory(step, jnp.asarray(burn[-1]), 600 + span + 1)
    mean, scale = float(traj[:, 0].mean()), float(traj[:, 0].std())
    ctx = SimpleNamespace(unwhiten=np.eye(3), whiten=np.eye(3), state_mean=np.zeros(3),
                          spec=SimpleNamespace(observed_index=0), obs_mean=mean, obs_scale=scale,
                          delay=TAU, embed_dim=EMBED, history=span)
    starts = np.random.default_rng(20261011).choice(600, size=32, replace=False)
    obs = (traj[:, 0] - mean) / scale
    index = starts[:, None] + (EMBED - 1 - np.arange(EMBED))[None, :] * TAU
    noise = 0.01 * np.random.default_rng(5).standard_normal((32, EMBED))
    return step, ctx, np.asarray(obs[index]) + noise, np.asarray(traj[starts])


def test_k6b_derived_estimator_runs_its_own_program_after_the_source_was_called() -> None:
    """After the 15-iteration estimator has been called, the derived 30-iteration one has no cached
    program, and its residuals are at most the 15-iteration ones, with some strictly lower.

    Reference: the prefix property (the length-30 scan runs the length-15 scan first and the carried
    cost never rises), so c30 <= c15 elementwise is exact (no tolerance); strictly lower in at
    least one entry because the starts are 0.5 (whitened) from the truth with noise 0.01, where the
    loop has not converged at 15 (probed: 12 of 32 estimates still fall). The hazard itself is shown
    alongside: a plain ``dataclasses.replace`` keeps the cached program and reproduces the
    15-iteration residuals bitwise, which would make the doubling read zero (M6).
    """
    from lpcstudy.estimation import StateEstimator
    step, ctx, x, truth = lorenz_world()
    network = StubNetwork()
    direction = np.random.default_rng(3).standard_normal(truth.shape)
    network.u0 = truth + 0.5 * direction / np.linalg.norm(direction, axis=1, keepdims=True)
    source = StateEstimator(ctx=ctx, network=network, model_step=step, refine_steps=15)
    lm15 = source.estimate_counted(x)[4]
    assert source._fn is not None
    derived = lm.derive_estimator(source, 30)
    assert derived._fn is None and derived.refine_steps == 30
    assert derived.network is source.network and derived.ctx is source.ctx
    lm30 = derived.estimate_counted(x)[4]
    assert derived._fn is not source._fn
    assert np.all(lm30.residual <= lm15.residual) and np.any(lm30.residual < lm15.residual)
    assert np.all(lm30.accepted >= lm15.accepted)
    plain = dataclasses.replace(source, refine_steps=30)
    assert plain._fn is source._fn                                     # the hazard: copied
    assert plain.estimate_counted(x)[4].residual.tobytes() == lm15.residual.tobytes()
    again = lm.derive_estimator(source, 15)                            # and the identity at 15
    assert again.estimate_counted(x)[4].residual.tobytes() == lm15.residual.tobytes()


def test_recorder_keeps_the_per_estimate_replacement_flags() -> None:
    """The recorder returns the inner outputs unchanged and keeps ``state_replaced | nu_replaced``."""
    outputs = (np.zeros((3, 3)), np.ones(3), np.array([True, False, False]),
               np.array([False, False, True]), "lm")
    inner = SimpleNamespace(estimate_counted=lambda x: outputs)
    recorder = lm.Recorder(inner)
    assert recorder.estimate_counted(np.zeros((3, 7))) is outputs
    assert recorder.flags[0].tolist() == [True, False, True]


# ------------------------------------------------------------------------- compare, the CLI
def test_compare_cli_prints_the_table_and_returns_the_halt_code(tmp_path: Path,
                                                                capsys: pytest.CaptureFixture[str]) -> None:
    """``compare`` reads directories or files, prints the class table, and exits 1 on a halt.

    Reference: hand dyadic arms (the H3c part: pt 1.0, 1.0078125, 1.01171875 with hw = 1/2 gives
    d1 = 1/64, d2 = 1/128, S = 1/32, class N with tail 0.25 from the probe file); arms that differ
    in the config budget and the QoI only.
    """
    arms = {}
    for k, pt in zip((15, 30, 60), (1.0, 1.0078125, 1.01171875)):
        tree = results_with_h3c(est(pt, 0.5, 1.5))
        tree["config"]["estimator_refine_steps"] = k
        directory = tmp_path / f"run{k}" / "pilot"
        directory.mkdir(parents=True)
        (directory / "results.json").write_text(json.dumps(tree))
        arms[k] = tmp_path / f"run{k}"
    probe = tmp_path / "probe.json"
    probe.write_text(json.dumps(probe_with_tail(0.25)))
    report_json = tmp_path / "report.json"
    code = lm.main(["compare", str(arms[15]), str(arms[30]), str(arms[60]), "--probe", str(probe),
                    "--json", str(report_json)])
    text = capsys.readouterr().out
    assert code == 0
    assert text.startswith("DEVELOPMENT (DEV-0)") and "lorenz63 | H3c | N | yes" in text
    saved = json.loads(report_json.read_text())
    assert saved["qoi"]["lorenz63"]["H3c"]["all"]["classification"]["s"] == 0.03125
    (arms[60] / "pilot" / "results.json").write_text(
        (arms[30] / "pilot" / "results.json").read_text().replace('"estimator_refine_steps": 30',
                                                                  '"estimator_refine_steps": 60'))
    assert lm.main(["compare", str(arms[15]), str(arms[30]), str(arms[60])]) == 1   # 30 = 60 bar the budget
    assert lm.main(["compare", str(tmp_path / "missing"), str(arms[30])]) == 2


# ------------------------------------------------------------------ environment preconditions
def provenance_block(threads: str = "8", commit: str = "abc", xla: str | None = None,
                     jax: str = "0.11.2", cpu: str = "Intel i9", dirty: bool | None = False,
                     seed_id: str = "DEV-0", preset: str = "pilot",
                     start: str = "2026-10-12T10:00:00Z") -> dict:
    """A recorded provenance block of the stored shape (``env``, ``packages``, ``cpu``, ...)."""
    env = {name: threads for name in lm.THREAD_VARIABLES}
    env.update(LPC_THREADS=threads, XLA_FLAGS=xla, JAX_PLATFORMS="cpu")
    return {"env": env, "commit": commit, "dirty": dirty, "cpu": {"model": cpu},
            "seed_id": seed_id, "preset": preset, "packages": {"jax": jax, "jaxlib": jax},
            "start_utc": start, "end_utc": "2026-10-12T11:00:00Z"}


def test_precondition_mismatches_name_each_difference() -> None:
    """The probe's run must equal the arm's: commit, LPC_THREADS and its mirrors, XLA_FLAGS, jax."""
    here = dict(provenance_block()["env"])
    versions = {"jax": "0.11.2", "jaxlib": "0.11.2"}
    check = lambda prov, env=here, ver=versions, commit="abc": lm.precondition_mismatches(
        prov, env, ver, commit)
    assert check(provenance_block()) == []
    other = check(provenance_block(threads="4"))
    assert len(other) == 6 and other[0] == "LPC_THREADS: recorded '4', here '8'"
    assert check(provenance_block(xla="--x")) == ["XLA_FLAGS: recorded '--x', here None"]
    assert check(provenance_block(), ver={"jax": "0.11.3", "jaxlib": "0.11.2"}) == [
        "jax: recorded '0.11.2', here '0.11.3'"]
    assert check(provenance_block(), commit="def") == ["commit: recorded 'abc', here 'def'"]
    assert check(provenance_block(), commit=None) == ["commit: recorded 'abc', here None"]
    for dirty in (True, None):   # a tree that was dirty, or not recorded, cannot be reproduced
        got = check(provenance_block(dirty=dirty))
        assert len(got) == 1 and got[0].startswith("dirty: the arm was run from a tree recorded as")
    assert check({}) == ["no env block in the recorded provenance"]
    missing = provenance_block()
    del missing["env"]["NPROC"]
    assert check(missing) == ["NPROC: recorded 'not recorded', here '8'"]


def test_current_commit_is_the_head_of_this_repository() -> None:
    """``current_commit`` returns a 40-hex SHA equal to ``git rev-parse HEAD`` (reference: git)."""
    import subprocess
    expected = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True,
                              text=True, check=True).stdout.strip()
    assert lm.current_commit() == expected and len(expected) == 40


def arms_of(*blocks: dict) -> dict:
    return {k: {"provenance": b} for k, b in zip((15, 30, 60), blocks)}


def test_pairing_problems_list_what_differs_between_arms() -> None:
    """Seed id, preset, commit, CPU, threads, XLA_FLAGS, jax, a dirty tree or a missing
    provenance are each a problem (F4, M6); identical clean arms have none."""
    clean = provenance_block
    assert lm.pairing_problems(arms_of(clean(), clean(), clean())) == []
    assert lm.pairing_problems(arms_of(clean(), clean(commit="def", threads="4"))) == [
        "commit: 'abc' at 15, 'def' at 30", "LPC_THREADS: '8' at 15, '4' at 30"]
    assert lm.pairing_problems(arms_of(clean(), clean(), clean(dirty=True))) == [
        "the 60 arm was run from a dirty tree"]
    assert lm.pairing_problems(arms_of(clean(), clean(dirty=None))) == [
        "the 30 arm records no provenance"]
    assert lm.pairing_problems({15: {}, 30: {"provenance": clean()}}) == [
        "the 15 arm records no provenance", "seed_id: None at 15, 'DEV-0' at 30",
        "preset: None at 15, 'pilot' at 30", "commit: None at 15, 'abc' at 30",
        "cpu: None at 15, 'Intel i9' at 30", "LPC_THREADS: None at 15, '8' at 30",
        "jax: None at 15, '0.11.2' at 30", "jaxlib: None at 15, '0.11.2' at 30"]
    assert lm.pairing_problems(arms_of(clean(), clean(xla="--xla_cpu_x"))) == [
        "XLA_FLAGS: None at 15, '--xla_cpu_x' at 30"]
    assert lm.pairing_problems(arms_of(clean(), clean(cpu="Other CPU"))) == [
        "cpu: 'Intel i9' at 15, 'Other CPU' at 30"]
    assert lm.pairing_problems(arms_of(clean(seed_id="DEV-1"), clean(preset="smoke"))) == [
        "seed_id: 'DEV-1' at 15, 'DEV-0' at 30", "preset: 'pilot' at 15, 'smoke' at 30"]


def test_unpaired_arms_halt_and_block_class_n() -> None:
    """A commit that differs between arms, or a dirty arm, halts the comparison and the part is
    not N even though the numbers say N (hand dyadic case of K5: S = 1/16, tail 0.25)."""
    def arm(pt: float, **prov) -> dict:
        tree = results_with_h3c(est(pt))
        tree["provenance"] = provenance_block(**prov)
        return tree
    pts = (0.0, 0.03125, 0.046875)
    good = lm.build_comparison({k: arm(pt) for k, pt in zip((15, 30, 60), pts)},
                               probe=probe_with_tail(0.25))
    row = good["qoi"]["lorenz63"]["H3c"]["all"]["classification"]
    assert (row["cls"], good["halt"]) == ("N", [])
    for bad_prov, why in (({"commit": "def"}, "commit: 'abc' at 15, 'def' at 60"),
                          ({"dirty": True}, "the 60 arm was run from a dirty tree")):
        arms = {15: arm(pts[0]), 30: arm(pts[1]), 60: arm(pts[2], **bad_prov)}
        report = lm.build_comparison(arms, probe=probe_with_tail(0.25))
        cls = report["qoi"]["lorenz63"]["H3c"]["all"]["classification"]
        assert cls["cls"] == "U" and any("arms not paired" in r for r in cls["reasons"])
        assert f"pairing: {why}" in report["halt"]


def test_probe_problems_one_case_per_condition() -> None:
    """A Part A file is used only if it has the arms' preset, seed id, commit, threads and jax, a
    clean tree, the levels 30, 60 and 120, and an exact P0 at every arm of every system."""
    arms = {k: {"provenance": provenance_block()} for k in (15, 30, 60)}
    probe = probe_with_tail(0.25)
    assert lm.probe_problems(probe, arms) == []

    def changed(**edits) -> dict:
        out = json.loads(json.dumps(probe))
        for key, value in edits.items():
            node = out
            *path, last = key.split(".")
            for part in path:
                node = node[part]
            node[last] = value
        return out
    cases = {
        "preset": changed(preset="smoke"), "seed_id": changed(seed_id="DEV-1"),
        "commit": changed(**{"provenance.commit": "other"}),
        "dirty": changed(**{"provenance.dirty": True}),
        "tree no record": changed(**{"provenance.dirty": None}),
        "levels": changed(levels=[15, 30, 60]),
    }
    for name, bad in cases.items():
        assert lm.probe_problems(bad, arms), name
    threads = changed(**{"provenance.env": {**probe["provenance"]["env"], "LPC_THREADS": "4"}})
    assert lm.probe_problems(threads, arms) == [
        "the probe's LPC_THREADS is '4', the arms' is ['8']"]
    jax = changed(**{"provenance.packages": {"jax": "0.11.3", "jaxlib": "0.11.2"}})
    assert lm.probe_problems(jax, arms) == ["the probe's jax is '0.11.3', the arms' is ['0.11.2']"]
    xla = changed(**{"provenance.env": {**probe["provenance"]["env"], "XLA_FLAGS": "--x"}})
    assert lm.probe_problems(xla, arms) == ["the probe's XLA_FLAGS is '--x', the arms' is ['None']"]
    cpu = changed(**{"provenance.cpu": "Other CPU"})
    assert lm.probe_problems(cpu, arms) == ["the probe's cpu is 'Other CPU', the arms' is ['Intel i9']"]
    no_cpu = changed(**{"provenance.cpu": None})
    assert len(lm.probe_problems(no_cpu, arms)) == 1
    # a P0 made against other directories of the same commit: the arm identity must be this arm's
    other_run = {k: {"provenance": provenance_block(start="2026-10-12T09:00:00Z")} for k in (15, 30, 60)}
    wrong = lm.probe_problems(probe, other_run)
    assert len(wrong) == 3 and all("was made against another run of that arm" in w for w in wrong)
    swapped = {15: arms[15], 30: {"provenance": provenance_block(start="x")}, 60: arms[60]}
    assert len(lm.probe_problems(probe, swapped)) == 1
    unrecorded = {k: {"provenance": {**provenance_block(), "start_utc": None}} for k in (15, 30, 60)}
    assert len(lm.probe_problems(probe, unrecorded)) == 3
    unrecorded_p0 = changed(**{"systems": {"lorenz63": {"groups": {}, "p0": [
        {"arm": k, "mismatches": []} for k in (15, 30, 60)]}}})
    assert len(lm.probe_problems(unrecorded_p0, arms)) == 3
    # a probe run without --results has no P0; a P0 with a mismatch, or for fewer arms, is refused
    none = changed(**{"systems": {"lorenz63": {"groups": {}, "p0": []}}})
    assert lm.probe_problems(none, arms) == [
        "the probe has no exact P0 for lorenz63 at the arm(s) [15, 30, 60]"]
    bad_p0 = probe_with_tail(0.25)
    bad_p0["systems"]["lorenz63"]["p0"][1]["mismatches"] = ["x"]
    assert lm.probe_problems(bad_p0, arms) == [
        "the probe has no exact P0 for lorenz63 at the arm(s) [30]"]
    assert lm.probe_problems(probe_with_tail(0.25, arms=(15, 30)), arms) == [
        "the probe has no exact P0 for lorenz63 at the arm(s) [60]"]


def test_a_probe_that_does_not_match_gives_no_r_a_and_halts() -> None:
    """With a probe from another run the tail ratio is not used (the part is U, never N) and the
    comparison halts with the reason; with the matching probe it is N."""
    arms = {k: results_with_h3c(est(pt)) for k, pt in zip((15, 30, 60), (0.0, 0.03125, 0.046875))}
    mismatched = probe_with_tail(0.25)
    mismatched["provenance"]["commit"] = "other"
    report = lm.build_comparison(arms, probe=mismatched)
    row = report["qoi"]["lorenz63"]["H3c"]["all"]
    assert row["tail_ratio"] is None and row["classification"]["cls"] == "U"
    assert any(h.startswith("probe: the probe's commit") for h in report["halt"])
    no_p0 = probe_with_tail(0.25, arms=())
    assert lm.build_comparison(arms, probe=no_p0)["qoi"]["lorenz63"]["H3c"]["all"][
        "classification"]["cls"] == "U"
    assert lm.build_comparison(arms, probe=probe_with_tail(0.25))["qoi"]["lorenz63"]["H3c"][
        "all"]["classification"]["cls"] == "N"


def test_labels_use_the_recorded_seed_id() -> None:
    """The label names the seed id of the runs, never a fixed one; an unrecorded id is flagged."""
    assert lm.make_label("DEV-7").startswith("DEVELOPMENT (DEV-7):")
    assert lm.make_label(None).startswith("UNVERIFIED (seed id not recorded):")
    assert lm.make_label("CONF-1").startswith("UNVERIFIED (CONF-1):")
    arms = {k: results_with_h3c(est(pt)) for k, pt in zip((15, 30), (0.0, 0.5))}
    for arm in arms.values():
        arm["provenance"]["seed_id"] = "DEV-7"
    assert lm.build_comparison(arms)["label"].startswith("DEVELOPMENT (DEV-7):")
    assert "DEV-7" in "\n".join(lm.render_probe({"seed_id": "DEV-7", "systems": {}}))


def test_c0_coverage_counts_matches_and_reports_gaps() -> None:
    """Leaves matched per pattern on the 15 arm; a pattern with no match while its block is present
    is a gap, one whose block is absent is not (hand tree).

    The tree has the config and the P2c block (patterns 1 and 13 match), a ``robustness`` block with
    only an unrelated leaf (the two robustness patterns under ``robustness`` are gaps), and no
    ``handling.robustness`` (no gap there).
    """
    tree = {"config": {"seed": 1, "estimator_refine_steps": 15},
            "systems": {"lorenz63": {"verification": {"P2c": {"a": 1, "b": 2, "c": 3}}}},
            "robustness": {"lorenz63": {"base": {"other": 1.0}}}}
    out = lm.c0_coverage(tree)
    matched = out["matched"]
    assert len(matched) == len(lm.C0_PATTERNS)
    assert matched[0] == 2 and matched[12] == 3 and sum(matched) == 5
    gap_ids = [g["pattern"] for g in out["gaps"]]
    by_hand = [i + 1 for i, (pattern, _) in enumerate(lm.C0_PATTERNS)
               if matched[i] == 0 and pattern[0] in ("systems", "robustness")]
    assert gap_ids == by_hand and {29, 30} <= set(gap_ids)   # the two robustness patterns
    assert not {1, 13} & set(gap_ids)                          # matched
    assert not {2, 3} & set(gap_ids)                           # top-level estimators: block absent
    assert not set(range(31, 36)) & set(gap_ids)               # handling.robustness is absent
    assert {g["root"] for g in out["gaps"]} == {"systems", "robustness"}
    report = lm.build_comparison({15: tree, 30: {**tree, "config": {"seed": 1}}})
    assert report["c0"]["coverage"] == matched and report["c0"]["coverage_gaps"] == out["gaps"]


def test_render_probe_prints_every_group_and_the_p0_outcome(tmp_path: Path,
                                                            capsys: pytest.CaptureFixture[str]) -> None:
    """The Part A text names each system, group, doubling and the P0 outcome; a probe halt halts.

    Reference: a hand-built probe dict of the stored shape (keys typed from ``group_report``); the
    expected substrings are typed from it. ``compare --probe`` returns 1 if the probe halted.
    """
    group = {"n_states": 3, "n_estimates": 12, "tail_ratio": 0.25, "doublings": {"30->60": {
        "fraction": 0.5, "se": 0.125, "F": 6, "T": 3.0, "q50": 0.0, "q90": 1.0, "q99": 2.0,
        "max": 4.0, "fraction_true": 0.25, "n_excluded": 1}},
        "chi2": {"above": {"15": 2}}, "p1": {}, "mse_href": {}, "w_star": {}, "eligibility": {}}
    probe = {"levels": [15, 30, 60, 120], "horizons": [30], "preset": "smoke", "seed_id": "DEV-0",
             "systems": {"lorenz63": {"groups": {"H2a": group}, "p0": [
                 {"arm": 15, "mismatches": []}, {"arm": 30, "mismatches": ["x"]}]}},
             "halt": ["P0 lorenz63 @30: x"]}
    text = "\n".join(lm.render_probe(probe))
    assert "lorenz63 H2a: 3 states, 12 estimates, r_A = 0.25" in text
    assert "30->60: fraction 0.5 (SE 0.125), F=6, T=3" in text and "replaced left out 1" in text
    assert "lorenz63 P0 @15: exact" in text and "P0 @30: MISMATCH ['x']" in text
    assert "HALT (a finding, /refer): P0 lorenz63 @30: x" in text
    arms = []
    for k, pt in zip((15, 30, 60), (1.0, 1.0078125, 1.01171875)):
        tree = results_with_h3c(est(pt, 0.5, 1.5))
        path = tmp_path / f"r{k}.json"
        path.write_text(json.dumps(tree))
        arms.append(str(path))
    probe_file = tmp_path / "probe.json"
    probe_file.write_text(json.dumps(probe))
    assert lm.main(["compare", *arms, "--probe", str(probe_file)]) == 1
    assert "Part A (per estimate)" in capsys.readouterr().out


def test_k6a_states_left_out_of_the_standard_errors_are_counted() -> None:
    """A state with no valid draw and the remainder of the blocks of 5 are reported, not hidden.

    Seven states of three draws: state 0 has all three draws replaced (no valid draw), so it is left
    out of the SEs (its three draws are in ``n_excluded``); 7 states give one block of 5 and a remainder of 2.
    """
    flags = {60: np.zeros((7, 3), dtype=bool)}
    flags[60][0, :] = True
    stats = lm.doubling_stats([seg(np.full((7, 3), 0.5), replaced=flags)], 15, 30)
    assert (stats["n"], stats["n_excluded"]) == (18, 3)
    assert (stats["n_states_no_valid_draw"], stats["n_states_dropped_from_blocks"]) == (1, 2)


@pytest.mark.parametrize("dirty", [True, None])
def test_probe_refuses_a_dirty_tree_before_any_work(dirty: bool | None, tmp_path: Path,
                                                    monkeypatch: pytest.MonkeyPatch,
                                                    capsys: pytest.CaptureFixture[str]) -> None:
    """The probe returns 64 when git says the tree is dirty (or git fails), before the study is built.

    The environment already equals ``thread_environment`` (so no re-exec), no preset is active, the
    lock is free, and ``Study`` is replaced by a function that fails the test if it is reached.
    """
    import lpcstudy.pipeline as pipeline

    def unreachable(*args, **kwargs):
        raise AssertionError("the study must not be built from a dirty tree")

    monkeypatch.setattr(pipeline, "Study", unreachable)
    for name, value in lm.thread_environment({"LPC_THREADS": "4"}).items():
        monkeypatch.setenv(name, value)
    monkeypatch.delenv("XLA_FLAGS", raising=False)
    monkeypatch.setenv("LPC_GPU_LOCK", str(tmp_path / "lock"))
    monkeypatch.setattr(lm, "running_presets", lambda: [])
    monkeypatch.setattr(lm, "git_dirty", lambda: dirty)
    out = tmp_path / "out"
    code = lm.main(["probe", "--preset", "smoke", "--seed-id", "DEV-0", "--out", str(out),
                    "--steps", "15", "30"])
    assert code == 64 and "working tree is not clean" in capsys.readouterr().err
    assert not out.exists()


def test_probe_file_records_its_provenance() -> None:
    """The head of a probe file holds the commit, tree state, argv, packages, CPU and environment.

    Reference: the arguments typed here; ``probe_problems`` reads exactly these keys, so a probe
    built by ``probe_header`` and ``probe_provenance`` is accepted against arms recorded by the same
    run (``provenance_block``), and the label carries the seed id.
    """
    block = provenance_block()
    environ = {**block["env"], "UNRELATED": "x"}
    provenance = lm.probe_provenance("abc", False, ["probe", "--preset", "pilot"], block["packages"],
                                     environ, "Intel i9")
    assert provenance == {"commit": "abc", "dirty": False, "argv": ["probe", "--preset", "pilot"],
                          "packages": block["packages"], "cpu": "Intel i9",
                          "env": {n: environ.get(n) for n in lm.PRECONDITION_ENV}}
    assert "UNRELATED" not in provenance["env"]
    header = lm.probe_header("pilot", "DEV-0", [15, 30, 60, 120], [30, 60, 120], block["env"],
                             provenance)
    assert header["provenance"] == provenance and header["seed_id"] == "DEV-0"
    assert header["label"].startswith("DEVELOPMENT (DEV-0):") and header["halt"] == []
    header["systems"] = probe_with_tail(0.25)["systems"]
    arms = {k: {"provenance": block} for k in (15, 30, 60)}
    assert lm.probe_problems(header, arms) == []
    assert lm.arm_identity(arms[15]) == {"start_utc": block["start_utc"], "end_utc": block["end_utc"]}
