"""Tests of ``tools/rehearsal_report.py`` (WU-0003.3a; plan amendment 5, row .3a, acceptance f1 to f4).

DEVELOPMENT: the C7 projections of the precision report. Needs owner review before freeze. The
references, none of them the tool's own output:

* f1: the factors of the mathematics note ``2026-10-14-math-wu0003.md`` section M3 as printed
  (0.717, 0.555, 0.712, 0.552 and the ranges 0.504 to 0.712, 0.507 to 0.717, 0.434 to 0.712,
  0.527 to 0.712) to the half unit of their last printed digit (5e-4), and the closed forms
  ``sqrt(n_run/n_full) x B x range`` written here to 1e-15; the B factors 1.014 and 1.007 exactly.
* f3: ``m3_projection.log`` (the output of the mathematician's script, which is never imported),
  parsed here: half-widths and factors of all 54 rows of P0 and P1 (DEV-0 pilots, extracted to
  ``fixtures/rehearsal_report/``, lpcstudy 1b20db9 and 5b3fd8f) to the half unit of the last
  printed digit (4 decimals for half-widths, 3 for factors), and the ratios to the v3 statements
  of the note's section M3 table (H2b(ii) 0.68 to 0.85, H2e 0.44 to 0.76, Q-N 0.45 to 1.2).
* f4: the band edges (0.67, 1.5) by hand on dyadic or exactly representable numbers, and the
  false-trigger rates against ``scipy.stats.norm`` (an independent implementation of the normal
  CDF; the tool uses ``math.erf``) and the note's "about 0.4%" and "about 7%".
* kappa_E: block variance and influence series against naive loops with ``math.fsum``; kappa
  against the closed forms ``1`` (no draw part) and ``sqrt(E_run/E_full)`` (no state part); the
  whole dump path against an independent loop implementation on a synthetic dump
  (rel 1e-10: about 500 terms, 6 operations, round-off about 3e-13, margin 300 for the centred
  series). The Monte Carlo test of f2 is ``tests/slow/test_rehearsal_report_mc.py``.

Every test is under 5 s (synthetic dumps of 500 states; no run output).
"""

from __future__ import annotations

import importlib.util
import json
import math
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy import stats as sps

from lpcstudy.config import PRESETS
from lpcstudy.data import make_rng

ROOT = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location("rehearsal_report",
                                               ROOT / "tools" / "rehearsal_report.py")
assert _SPEC is not None and _SPEC.loader is not None
rr = importlib.util.module_from_spec(_SPEC)
sys.modules["rehearsal_report"] = rr
_SPEC.loader.exec_module(rr)

FIXTURES = ROOT / "tests" / "unit" / "fixtures" / "rehearsal_report"
LOG = (ROOT / "docs" / "agent" / "notes" / "2026-10-14-math-wu0003-scripts" / "m3_projection.log")
SEED = 20261031
SYSTEMS = ("lorenz63", "rossler", "chua")


def rng_for(label: str) -> np.random.Generator:
    """A generator from ``make_rng`` (the project's only source of randomness)."""
    return make_rng(SEED, "test_rehearsal_report", label)


# ------------------------------------------------------------------------------------------ f1
def test_factors_equal_the_note_table_to_printed_digits() -> None:
    """M3 table: 0.717, 0.555, 0.712, 0.552, the kappa and training ranges, B = 1.014 and 1.007.

    Reference: the numbers printed in the note's table (half unit of the last digit, 5e-4) and the
    closed forms written here. The B factors are constants of ``m3_bfactor.log``: exact.
    """
    full = PRESETS["full"]
    assert (full.n_test, full.n_test_sweep, full.n_eval_draws, full.bootstrap_resamples) == \
        (1000, 1000, 4, 2000)
    assert full.n_construction + full.n_calibration == 3000
    assert rr.B_FACTOR == {"primary": 1.014, "secondary": 1.007}
    assert rr.b_factor("primary", 500, 2000) == 1.014
    assert rr.b_factor("secondary", 500, 2000) == 1.007
    half = 5e-4 + 1e-12

    def product(n_run, n_full, level, extra):
        return rr.n_factor(n_run, n_full) * rr.b_factor(level, 500, 2000) * extra

    table = [
        (product(500, 1000, "primary", 1.0), 0.717, math.sqrt(0.5) * 1.014),
        (product(300, 1000, "primary", 1.0), 0.555, math.sqrt(0.3) * 1.014),
        (product(500, 1000, "secondary", 1.0), 0.712, math.sqrt(0.5) * 1.007),
        (product(300, 1000, "secondary", 1.0), 0.552, math.sqrt(0.3) * 1.007),
    ]
    k_lo, k_hi = rr.kappa_range(2, 4)
    assert k_lo == math.sqrt(0.5) and k_hi == 1.0
    table += [
        (product(500, 1000, "secondary", k_lo), 0.504, math.sqrt(0.5) * 1.007 * math.sqrt(0.5)),
        (product(500, 1000, "primary", k_lo), 0.507, math.sqrt(0.5) * 1.014 * math.sqrt(0.5)),
    ]
    q_logit, q_ind = rr.qn_range("logit", 900, 3000), rr.qn_range("indicator", 900, 3000)
    assert rr.qn_range("log_horizon", 900, 3000) == (0.61, 1.0)
    assert q_logit == (0.61, 1.0) and q_ind == (0.74, 1.0)
    table += [
        (product(500, 1000, "secondary", q_logit[0]), 0.434, math.sqrt(0.5) * 1.007 * 0.61),
        (product(500, 1000, "secondary", q_ind[0]), 0.527, math.sqrt(0.5) * 1.007 * 0.74),
    ]
    for value, printed, closed in table:
        assert abs(value - printed) <= half, (value, printed)
        assert value == pytest.approx(closed, rel=1e-15)


def test_unmeasured_factor_pairs_are_not_computable() -> None:
    """B is measured for 500 to 2000 only (equal B gives 1); Q-N training for 900 to 3000 only."""
    assert rr.b_factor("primary", 2000, 2000) == 1.0
    assert rr.qn_range("logit", 3000, 3000) == (1.0, 1.0)
    assert rr.kappa_range(4, 4) == (1.0, 1.0)
    with pytest.raises(rr.NotComputable, match="no measured B factor"):
        rr.b_factor("primary", 50, 2000)
    with pytest.raises(rr.NotComputable, match="no Q-N training factor"):
        rr.qn_range("logit", 360, 3000)
    with pytest.raises(rr.NotComputable):
        rr.kappa_range(4, 2)
    with pytest.raises(rr.NotComputable):
        rr.n_factor(0, 1000)


def test_specs_are_the_eighteen_rows_of_the_note_and_v7() -> None:
    """The rows of M3's ``m3_projection.py`` (18 per system: H2c two, H2a(ii) two, H2e two) and the
    five V7 rows (median slope; efficiency at the four noise levels of the configuration)."""
    cfg = json.loads((FIXTURES / "p0_pilot.json").read_text())["config"]
    labels = [s.label for s in rr.specs_for(cfg, "A1")]
    assert labels == ["H1b PLP slope", "H1c PLP median ratio", "H1d analog_seed",
                      "H1a ratio rho=0.01", "Q-N oracle logit", "Q-N oracle zero-ind",
                      "Q-N oracle log_hor", "H2a(i)", "H2a(ii) zero", "H2a(ii) interior",
                      "H2b(i)", "H2b(ii)", "H2c A4-A2", "H2c A4-A1", "H2d", "H2e rho=0.01",
                      "H2e rho=0.02", "H3c", "V7 median slope", "V7 efficiency rho=0.005",
                      "V7 efficiency rho=0.01", "V7 efficiency rho=0.02", "V7 efficiency rho=0.05"]
    assert "H2c A4-A0" in [s.label for s in rr.specs_for(cfg, "A0")]
    assert len([s.label for s in rr.specs_for(cfg, None)]) == 22


# ------------------------------------------------------------------------------------------ f3
ROW = re.compile(r"^(?P<name>.{22}) (?P<system>\S+)\s+(?P<hw>\d\.\d{4}) +(?P<fl>\d\.\d{3})-"
                 r"(?P<fh>\d\.\d{3}) +(?P<lo>\d\.\d{4})- *(?P<hi>\d\.\d{4})")


def parse_log() -> dict[str, dict[tuple[str, str], dict[str, float]]]:
    """The rows of ``m3_projection.log`` by pilot (``p0``, ``p1``), then (label, system)."""
    out: dict[str, dict[tuple[str, str], dict[str, float]]] = {}
    current = ""
    for line in LOG.read_text().splitlines():
        if line.startswith("=="):
            current = "p0" if "p0-" in line else "p1"
            out[current] = {}
        elif current and (m := ROW.match(line)) is not None:
            label = m["name"].strip().replace("rho=.01", "rho=0.01").replace("rho=.02", "rho=0.02")
            out[current][(label, m["system"])] = {k: float(m[k]) for k in ("hw", "fl", "fh",
                                                                        "lo", "hi")}
    return out


def tool_rows(name: str, tmp_path: Path) -> dict[tuple[str, str], dict]:
    """The rows of the tool for a fixture (no dump: the kappa range, as the script used)."""
    rep = rr.Report()
    rr.run(FIXTURES / f"{name}_pilot.json", states_dir=tmp_path / "no_states", rep=rep)
    return {(row["label"], system): row for system, rows in rep.data["rows"].items()
            for row in rows}


@pytest.mark.parametrize("name", ["p0", "p1"])
def test_p0_p1_projections_equal_the_script_log(name: str, tmp_path: Path) -> None:
    """f3: all 54 rows of each pilot equal ``m3_projection.log`` to its printed digits.

    Tolerance: half a unit of the last printed digit (5e-5 for the 4-decimal half-widths, 5e-4
    for the 3-decimal factors), plus 1e-12 for the order of the multiplications.
    """
    logged = parse_log()[name]
    mine = tool_rows(name, tmp_path)
    assert len(logged) == 54 and set(logged) <= set(mine)
    extra = set(mine) - set(logged)
    assert len(extra) == 15 and all(label.startswith("V7 ") for label, _ in extra)
    for key, expected in logged.items():
        row = mine[key]
        assert abs(row["hw_run"] - expected["hw"]) <= 5e-5 + 1e-12, key
        assert abs(row["f_lo"] - expected["fl"]) <= 5e-4 + 1e-12, key
        assert abs(row["f_hi"] - expected["fh"]) <= 5e-4 + 1e-12, key
        assert abs(row["hw_lo"] - expected["lo"]) <= 5e-5 + 1e-12, key
        assert abs(row["hw_hi"] - expected["hi"]) <= 5e-5 + 1e-12, key


def test_ratios_to_v3_equal_the_note_table(tmp_path: Path) -> None:
    """f3: the ratio ranges to v3 over P0 and P1: H2b(ii) 0.68-0.85, H2e 0.44-0.76, Q-N 0.45-1.2.

    Reference 1: the minimum and maximum of the log's own projected half-widths over the 18
    (system, pilot) rows divided by v3. Reference 2: the note's printed ranges; the Q-N hw are
    printed there to 3 decimals (0.018 to 0.048), so its ratios carry 0.0005/0.04 = 0.0125.
    """
    logged, rows = parse_log(), {n: tool_rows(n, tmp_path) for n in ("p0", "p1")}
    cases = [("H2b(ii)", 0.03, (0.68, 0.85), 0.005),
             ("H2e rho=0.01", 0.04, None, 0.005),
             ("Q-N oracle logit", 0.04, (0.45, 1.2), 0.0125)]
    h2e = {"lo": [], "hi": []}
    for label, v3, printed, slack in cases:
        lo = min(logged[n][(label, s)]["lo"] for n in logged for s in SYSTEMS) / v3
        hi = max(logged[n][(label, s)]["hi"] for n in logged for s in SYSTEMS) / v3
        mine_lo = min(rows[n][(label, s)]["ratio_lo"] for n in rows for s in SYSTEMS)
        mine_hi = max(rows[n][(label, s)]["ratio_hi"] for n in rows for s in SYSTEMS)
        assert abs(mine_lo - lo) <= 5e-5 / v3 + 1e-12 and abs(mine_hi - hi) <= 5e-5 / v3 + 1e-12
        if printed is not None:
            assert abs(mine_lo - printed[0]) <= slack and abs(mine_hi - printed[1]) <= slack
    for label in ("H2e rho=0.01", "H2e rho=0.02"):
        h2e["lo"] += [rows[n][(label, s)]["ratio_lo"] for n in rows for s in SYSTEMS]
        h2e["hi"] += [rows[n][(label, s)]["ratio_hi"] for n in rows for s in SYSTEMS]
    assert abs(min(h2e["lo"]) - 0.44) <= 0.005 and abs(max(h2e["hi"]) - 0.76) <= 0.005


def test_pilot_fixture_report_is_complete_but_for_kappa(tmp_path: Path, capsys) -> None:
    """Without a dump the range is used and shown (FALLBACK), three "not computable" lines, exit 2.

    Reference: the arithmetic of the plan (12 kappa_E parts: H2c x2, H2d, H3c over 3 systems; one
    line per system), not the tool's output. Findings ("v3 precision not reproduced") never change
    the exit code, and no MISMATCH arises.
    """
    code = rr.main([str(FIXTURES / "p0_pilot.json"), "--states", str(tmp_path / "none")])
    out = capsys.readouterr().out
    assert code == 2
    assert out.splitlines()[0] == "DEVELOPMENT (DEV-0): conditional on one realization; not a hypothesis test"
    assert out.count("(FALLBACK)") == 12
    # three systems without a dump, the one H3a line, plus the closing count line
    assert out.count("not computable: ") == 3 + 1 + 1
    assert "not computable: 4 item(s)" in out and "H3a (all systems)" in out
    assert "kappa_E: point estimate from the dump for 0 of 12 parts; range fallback for 12" in out
    assert "MISMATCH" not in out
    assert "v3 precision not reproduced" in out


def test_chua_p0_h2a_interior_pass_is_impossible(capsys, tmp_path: Path) -> None:
    """The note (M3 pre-check): Chua P0 H2a(ii) interior needs |pc| < 0.1 - 0.1045 = -0.005."""
    rr.main([str(FIXTURES / "p0_pilot.json"), "--states", str(tmp_path / "none")])
    chua = capsys.readouterr().out.split("=== chua")[1]
    block = chua.split("H2a(ii) interior")[1].split("H2b(i)")[0]
    assert "pass needs |pc| < -0.005 .. -0.005; IMPOSSIBLE" in block


# ------------------------------------------------------------------------------------------ f4
def test_reading_i_at_the_band_edges() -> None:
    """f4 (i): the edges 0.67 and 1.5 of the reference are inside; one ulp beyond is outside."""
    ref = 1.0
    assert not rr.outside_nominal(0.67, ref) and not rr.outside_nominal(1.5, ref)
    assert rr.outside_nominal(np.nextafter(0.67, 0.0), ref)
    assert rr.outside_nominal(np.nextafter(1.5, 2.0), ref)
    assert not rr.outside_nominal(1.0, ref)
    ref = 0.03
    assert not rr.outside_nominal(0.67 * ref, ref) and not rr.outside_nominal(1.5 * ref, ref)
    assert rr.outside_nominal(np.nextafter(0.67 * ref, 0.0), ref)
    assert rr.outside_nominal(np.nextafter(1.5 * ref, 1.0), ref)


def test_reading_ii_at_the_band_edges() -> None:
    """f4 (ii) against v3: the whole range must be outside the band (an edge point is inside)."""
    v3 = 1.0
    assert not rr.outside_v3_range(0.3, 0.67, v3)  # the upper end sits on the lower edge
    assert rr.outside_v3_range(0.3, np.nextafter(0.67, 0.0), v3)
    assert not rr.outside_v3_range(1.5, 2.0, v3)
    assert rr.outside_v3_range(np.nextafter(1.5, 2.0), 2.0, v3)
    assert not rr.outside_v3_range(0.3, 2.0, v3)  # straddles the band: undetermined
    assert not rr.outside_v3_range(1.0, 1.0, v3)
    # a point range equals reading (i) with the same number
    for x in (0.5, 0.67, 0.9, 1.5, 1.6):
        assert rr.outside_v3_range(x, x, v3) == rr.outside_nominal(x, v3)


def test_reading_ii_against_an_observed_value_at_the_edges() -> None:
    """f4 (ii) against an observed full-size value: below 0.67 low or above 1.5 high is outside."""
    low, high = 2.0, 3.0
    assert not rr.outside_projection_range(0.67 * low, low, high)
    assert rr.outside_projection_range(np.nextafter(0.67 * low, 0.0), low, high)
    assert not rr.outside_projection_range(1.5 * high, low, high)
    assert rr.outside_projection_range(np.nextafter(1.5 * high, 10.0), low, high)
    assert not rr.outside_projection_range(2.5, low, high)


def test_the_two_readings_differ_as_pf4_says() -> None:
    """(i) fires and (ii) does not when the range reaches into the band; (ii) fires, (i) not, when
    the whole range is below it but the n-only value is not.

    Reference: hand arithmetic on v3 = 1: (i) uses the n-only value 0.66 (< 0.67); the range
    [0.5, 0.9] reaches into [0.67, 1.5]. The other case: n-only 0.7 (inside), range [0.5, 0.66]
    (entirely below 0.67).
    """
    v3 = 1.0
    assert rr.outside_nominal(0.66, v3) and not rr.outside_v3_range(0.5, 0.9, v3)
    assert not rr.outside_nominal(0.7, v3) and rr.outside_v3_range(0.5, 0.66, v3)


def test_row_level_readings_on_a_hand_built_tree() -> None:
    """Row-level: H2b(ii) with n-only ratio 0.665 and projected ratio 0.665 x 1.014 = 0.6743.

    Hand arithmetic: 0.665 < 0.67, so (i) fires; 0.6743 > 0.67, so (ii) is silent.
    """
    cfg = json.loads((FIXTURES / "p0_pilot.json").read_text())["config"]
    hw = 0.665 * 0.03 / math.sqrt(300 / 1000)
    tree = {"H2b": {"library_change": {"mean_change": 0.05, "ci": [0.05 - hw, 0.05 + hw],
                                        "level": rr.PRIMARY_LEVEL}}}
    spec = next(s for s in rr.specs_for(cfg, "A1") if s.label == "H2b(ii)")
    row = rr.project_row(spec, "lorenz63", tree, cfg, None, rr.Report(), PRESETS["full"])
    assert row["ratio_nominal"] == pytest.approx(0.665, rel=1e-12)
    assert row["ratio_lo"] == pytest.approx(0.665 * 1.014, rel=1e-12)
    assert row["reading_i"] is True and row["reading_ii"] is False
    assert rr.which(row) == "(i)"


def test_false_trigger_rates_against_scipy() -> None:
    """The two-sided rate of the band for the log-ratio SDs of the note.

    Reference: ``scipy.stats.norm`` (the tool uses ``math.erf``), equal to 1e-12 (both accurate to
    a few ulp). The note's "about 0.4%" and "about 7%": fixed bounds [0.0035, 0.0045] and
    [0.065, 0.075] (hand estimates 0.0040 and 0.0695).
    """
    for sd_run, sd_full in ((0.115, 0.08), (0.18, 0.13), (0.1, 0.05)):
        sigma = math.hypot(sd_run, sd_full)
        expected = sps.norm.cdf(math.log(0.67), scale=sigma) + sps.norm.sf(math.log(1.5), scale=sigma)
        assert rr.false_trigger_rate(sd_run, sd_full) == pytest.approx(expected, rel=1e-12)
    assert 0.0035 <= rr.false_trigger_rate(*rr.FALSE_TRIGGER_SD["default"]) <= 0.0045
    assert 0.065 <= rr.false_trigger_rate(*rr.FALSE_TRIGGER_SD["H3c"]) <= 0.075


def test_false_trigger_rate_is_printed_per_part(capsys, tmp_path: Path) -> None:
    """Every part line carries its rate: 0.4% for 66 of the 69 rows, 7.0% for the three H3c rows."""
    rr.main([str(FIXTURES / "p1_pilot.json"), "--states", str(tmp_path / "none")])
    out = capsys.readouterr().out
    assert out.count("false-trigger 0.4%") == 66 and out.count("false-trigger 7.0%") == 3


# ------------------------------------------------------------------------------------------ kappa
def loop_block_variance(values: list[float], block: int) -> float:
    """``b x`` the ddof-0 variance of the overlapping block means, by loops and ``fsum``."""
    n = len(values)
    mean = math.fsum(values) / n
    centred = [v - mean for v in values]
    means = [math.fsum(centred[i:i + block]) / block for i in range(n - block + 1)]
    grand = math.fsum(means) / len(means)
    return block * math.fsum((m - grand) ** 2 for m in means) / len(means)


def test_block_variance_equals_a_naive_loop() -> None:
    """``V*(b)`` against loops (rel 1e-12: about n = 200 terms, round-off 2e-14, margin 50)."""
    x = rng_for("block").normal(size=200)
    for block in (1, 5, 20):
        assert rr.block_variance(x, block) == pytest.approx(loop_block_variance(list(x), block),
                                                            rel=1e-12)
    with pytest.raises(rr.NotComputable):
        rr.block_variance(np.arange(4.0), 5)
    with pytest.raises(rr.NotComputable):
        rr.block_variance(np.array([1.0, np.nan, 2.0, 3.0, 4.0, 5.0]), 2)


def test_kappa_limits() -> None:
    """No draw part gives exactly 1; no state part gives exactly sqrt(E_run/E_full).

    Reference: the closed form (V_s + V_d E_run/E_full)/(V_s + V_d) at its two ends, exact in
    float64 here (sqrt of 1.0 and of 0.5); and V_s = V_d = 1 gives sqrt(3/4).
    """
    assert rr.kappa_combine(2.0, 0.0, 2, 4) == 1.0
    assert rr.kappa_combine(0.0, 3.0, 2, 4) == math.sqrt(0.5)
    assert rr.kappa_combine(1.0, 1.0, 2, 4) == pytest.approx(math.sqrt(0.75), rel=1e-15)
    assert rr.kappa_combine(1.0, 1.0, 4, 4) == 1.0
    for bad in ((-1.0, 1.0), (1.0, float("nan")), (0.0, 0.0)):
        with pytest.raises(rr.NotComputable):
            rr.kappa_combine(*bad, 2, 4)
    with pytest.raises(ValueError):
        rr.kappa_estimate(np.ones(10), np.ones(10), np.ones(10), np.ones(10), "bad", 2, 4)


def influence_by_hand(kind: str, a: list[float], b: list[float]) -> list[float]:
    """The influence series by loops: centred difference, or ``(a - R b)/mean(b)``."""
    n = len(a)
    if kind == "diff":
        d = [a[i] - b[i] for i in range(n)]
        m = math.fsum(d) / n
        return [x - m for x in d]
    mean_a, mean_b = math.fsum(a) / n, math.fsum(b) / n
    ratio = mean_a / mean_b
    return [(a[i] - ratio * b[i]) / mean_b for i in range(n)]


@pytest.mark.parametrize("kind", ["diff", "ratio"])
def test_kappa_estimate_equals_a_loop_implementation(kind: str) -> None:
    """``kappa_estimate`` against loops (rel 1e-10: 120 terms, a few operations, margin 1e3)."""
    g = rng_for(f"kappa-{kind}")
    n = 120
    vs_a, vs_b = 1.0 + g.gamma(4.0, 0.1, n), 1.0 + g.gamma(4.0, 0.1, n)
    re_a, re_b = vs_a + g.normal(0, 0.2, n), vs_b + g.normal(0, 0.2, n)
    kappa, v_s, v_d = rr.kappa_estimate(vs_a, vs_b, re_a, re_b, kind, 2, 4, block=5)
    psi_state = influence_by_hand(kind, list(vs_a), list(vs_b))
    psi_real = influence_by_hand(kind, list(re_a), list(re_b))
    psi_diff = [r - s for r, s in zip(psi_real, psi_state, strict=True)]
    want_s, want_d = loop_block_variance(psi_state, 5), loop_block_variance(psi_diff, 5)
    assert v_s == pytest.approx(want_s, rel=1e-10) and v_d == pytest.approx(want_d, rel=1e-10)
    assert kappa == pytest.approx(math.sqrt((want_s + want_d * 0.5) / (want_s + want_d)), rel=1e-10)
    assert math.sqrt(0.5) <= kappa <= 1.0


# ------------------------------------------------------------------------------------------ world
def make_dump(system: str, n: int = 500, draws: int = 2, ref: int = 2) -> dict[str, np.ndarray]:
    """A synthetic dump with the arrays that the tool reads (schema /2 keys)."""
    g = rng_for(f"dump-{system}")
    e_c = 0.4 + g.gamma(4.0, 0.1, (n, 5))
    e_p = 0.3 + g.gamma(4.0, 0.1, (n, 5))
    cross = 0.3 * np.sqrt(e_c * e_p)
    arrays: dict[str, np.ndarray] = {
        "meta/schema": np.array("lpcstudy.states/2"), "meta/system": np.array(system),
        "meta/seed_id": np.array("DEV-0"), "meta/preset": np.array("pilot"),
        "meta/n_eval_draws": np.array(draws), "core/ref_index": np.array(ref),
        "core/E_C": e_c, "core/E_P": e_p, "core/C": cross}
    weights = {r: g.uniform(0.0, 1.0, (n, draws)) for r in ("A2", "A3", "A4", "A5")}
    for rule, w in weights.items():
        arrays[f"core/weight_href/{rule}"] = w
    ec, ep, cc = e_c[:, ref], e_p[:, ref], cross[:, ref]
    for rule in ("A0", "A1", "A2", "A3", "A4", "A5"):
        if rule == "A0":
            v = ec.copy()
        elif rule == "A1":
            v = ep.copy()
        else:
            w = weights[rule]
            v = (w**2 * ec[:, None] + (1 - w) ** 2 * ep[:, None]
                 + 2 * w * (1 - w) * cc[:, None]).mean(axis=1)
        mse = np.tile(v[:, None], (1, 5))
        mse[:, ref] = v * (1.0 + 0.3 * g.normal(size=n))
        arrays[f"core/state_mse/{rule}"] = np.abs(mse)
    return arrays


def write_run(root: Path, best: str = "A1", scale_h3c: float = 1.0, h3c_level: float | None = None,
              dump_seed: str = "DEV-0", drop_block: bool = False) -> Path:
    """A run directory: the P0 fixture with the kappa leaves recomputed from synthetic dumps."""
    res = json.loads((FIXTURES / "p0_pilot.json").read_text())
    if drop_block:
        del res["config"]["bootstrap_block"]
    states = root / "states"
    states.mkdir(parents=True)
    for system in SYSTEMS:
        arrays = make_dump(system)
        arrays["meta/seed_id"] = np.array(dump_seed)
        mse = {r: arrays[f"core/state_mse/{r}"][:, 2] for r in ("A0", "A1", "A2", "A3", "A4", "A5")}
        tree = res["systems"][system]
        tree["H2c"]["best_single"] = best
        if best != "A1":
            tree["H2c"][f"A4_minus_{best}"] = tree["H2c"].pop("A4_minus_A1")
        tree["H2c"]["A4_minus_A2"]["mean"] = float(np.mean(mse["A4"] - mse["A2"]))
        tree["H2c"][f"A4_minus_{best}"]["mean"] = float(np.mean(mse["A4"] - mse[best]))
        tree["H2d"]["in_distribution_excess"] = float(np.mean(mse["A4"]) / np.mean(mse["A3"]) - 1.0)
        tree["H3c"]["A5_over_A4_mse"] = scale_h3c * float(np.mean(mse["A5"]) / np.mean(mse["A4"]))
        if h3c_level is not None:
            tree["H3c"]["level"] = h3c_level
        np.savez(states / f"{system}.npz", **arrays)
    (root / "results.json").write_text(json.dumps(res))
    return root


def kappa_by_hand(system: str, kind: str, first: str, second: str) -> float:
    """kappa_E for the synthetic dump of a system by loops (V_i from the definition per draw)."""
    arrays = make_dump(system)
    ref, n = 2, 500

    def draw_free(rule: str) -> list[float]:
        out = []
        for i in range(n):
            ec, ep, cc = (float(arrays[k][i, ref]) for k in ("core/E_C", "core/E_P", "core/C"))
            if rule in ("A0", "A1"):
                ws = [1.0 if rule == "A0" else 0.0]
            else:
                ws = [float(w) for w in arrays[f"core/weight_href/{rule}"][i]]
            out.append(math.fsum(w * w * ec + (1 - w) ** 2 * ep + 2 * w * (1 - w) * cc
                                 for w in ws) / len(ws))
        return out

    real = lambda r: [float(x) for x in arrays[f"core/state_mse/{r}"][:, ref]]  # noqa: E731
    psi_state = influence_by_hand(kind, draw_free(first), draw_free(second))
    psi_real = influence_by_hand(kind, real(first), real(second))
    v_s = loop_block_variance(psi_state, 5)
    v_d = loop_block_variance([r - s for r, s in zip(psi_real, psi_state, strict=True)], 5)
    return math.sqrt((v_s + v_d * 2 / 4) / (v_s + v_d))


def test_whole_dump_path_gives_exit_zero_and_the_hand_kappa(tmp_path: Path, capsys) -> None:
    """A complete synthetic run (fixture results, three dumps): only H3a is open; kappa = the loops.

    Reference: ``kappa_by_hand`` (loops from the definitions of V_i and the influence series,
    rel 1e-10, see the module docstring). The projected half-widths use the point kappa at both
    ends (lo = hi), and the reproduction checks of the dump against the results leaves match.
    """
    run = write_run(tmp_path / "run")
    json_out = tmp_path / "out.json"
    code = rr.main([str(run), "--json", str(json_out)])
    out = capsys.readouterr().out
    # H3a is listed as not computable and counted, so a complete run exits 2 (plan question)
    assert code == 2, out
    incomplete = [line for line in out.splitlines() if line.startswith("  not computable")]
    assert len(incomplete) == 1 and "H3a (all systems)" in incomplete[0]
    assert "MISMATCH" not in out and "FALLBACK" not in out
    assert out.count("MATCH") >= 12 and "kappa_E: point estimate from the dump for 12 of 12" in out
    data = json.loads(json_out.read_text())
    expect = {"H2c A4-A2": ("diff", "A4", "A2"), "H2c A4-A1": ("diff", "A4", "A1"),
              "H2d": ("ratio", "A4", "A3"), "H3c": ("ratio", "A5", "A4")}
    for system in SYSTEMS:
        rows = {r["label"]: r for r in data["rows"][system]}
        for label, (kind, first, second) in expect.items():
            want = kappa_by_hand(system, kind, first, second)
            row = rows[label]
            assert row["kappa"]["kappa"] == pytest.approx(want, rel=1e-10), (system, label)
            assert row["f_lo"] == row["f_hi"]
            assert row["f_lo"] == pytest.approx(
                math.sqrt(0.5) * rr.b_factor("primary" if label == "H3c" else "secondary", 500, 2000)
                * want, rel=1e-10)


def test_best_single_a0_uses_cp_alone(tmp_path: Path, capsys) -> None:
    """With ``best_single = A0`` the second H2c row is A4 - A0 and V is E_C (weight 1)."""
    run = write_run(tmp_path / "run", best="A0")
    json_out = tmp_path / "out.json"
    code = rr.main([str(run), "--json", str(json_out)])
    out = capsys.readouterr().out
    assert code == 2 and out.count("  not computable") == 1, out  # H3a only
    rows = {r["label"]: r for r in json.loads(json_out.read_text())["rows"]["rossler"]}
    assert "H2c A4-A0" in rows and "H2c A4-A1" not in rows
    assert rows["H2c A4-A0"]["kappa"]["kappa"] == pytest.approx(
        kappa_by_hand("rossler", "diff", "A4", "A0"), rel=1e-10)


def test_dump_that_disagrees_with_the_results_is_a_mismatch(tmp_path: Path, capsys) -> None:
    """The H3c leaf off by a relative 1e-6 (the allowed 1e-12): MISMATCH, exit 1 (1 beats 2)."""
    run = write_run(tmp_path / "run", scale_h3c=1.0 + 1e-6)
    code = rr.main([str(run)])
    out = capsys.readouterr().out
    assert code == 1
    assert "MISMATCH: 3 item(s) (listed above)" in out
    assert out.count("  MISMATCH: ") == 3 and out.count("H3c ratio: dump") == 6  # check line + defect
    # R1: the mismatching dump does not supply kappa_E for H3c: the range, FALLBACK, not counted
    assert out.count("(FALLBACK)") == 3
    assert out.count("the dump does not reproduce the results leaf") == 3
    assert "kappa_E: point estimate from the dump for 9 of 12 parts; range fallback for 3" in out
    h3c = [line for line in out.splitlines() if line.startswith("  H3c ")]
    assert len(h3c) == 3 and all("0.507-0.717" in line for line in h3c)


@pytest.mark.parametrize(("scale", "code"), [(1.0 + 5e-13, 2), (1.0 + 2e-12, 1)])
def test_reproduction_bound_passes_at_half_and_fails_at_twice(tmp_path: Path, capsys, scale, code
                                                              ) -> None:
    """The dump-to-results bound ``1e-12 |leaf|``: passes at 0.5x of it, fails at 2x.

    A pass leaves only H3a open (exit 2, no MISMATCH, no FALLBACK); a failure exits 1.
    """
    run = write_run(tmp_path / "run", scale_h3c=scale)
    assert rr.main([str(run)]) == code
    out = capsys.readouterr().out
    assert ("MISMATCH" in out) == (code == 1) and ("(FALLBACK)" in out) == (code == 1)


def test_level_disagreement_is_a_mismatch(tmp_path: Path, capsys) -> None:
    """The results say 95% where the table has 1 - 0.05/3 (H3c): MISMATCH, exit 1."""
    run = write_run(tmp_path / "run", h3c_level=0.95)
    assert rr.main([str(run)]) == 1
    assert "record level 0.95" in capsys.readouterr().out


def test_dump_without_matching_seed_id_is_refused(tmp_path: Path, capsys) -> None:
    """A dump that records another seed id than the run: refused, exit 2, a stderr line."""
    run = write_run(tmp_path / "run", dump_seed="DEV-1")
    assert rr.main([str(run)]) == 2
    err = capsys.readouterr().err
    assert "refused" in err and "DEV-1" in err


@pytest.mark.parametrize("edit", ["seed_id", "kind", "disagree"])
def test_non_development_run_is_refused(tmp_path: Path, capsys, edit: str) -> None:
    """A run whose seed id is not DEV-n, or whose kind is not development, or whose ids differ."""
    res = json.loads((FIXTURES / "p0_pilot.json").read_text())
    if edit == "seed_id":
        res["config"]["seed_id"] = res["provenance"]["seed_id"] = "CONF-0"
    elif edit == "kind":
        res["provenance"]["seed_kind"] = "confirmatory"
    else:
        res["provenance"]["seed_id"] = "DEV-3"
    path = tmp_path / "results.json"
    path.write_text(json.dumps(res))
    assert rr.main([str(path)]) == 2
    captured = capsys.readouterr()
    assert "refused" in captured.err and captured.out == ""


def test_missing_block_and_bad_interval_are_listed_and_exit_two(tmp_path: Path, capsys) -> None:
    """A missing H1d block and a zero-width interval are "not computable"; the rest is printed."""
    res = json.loads((FIXTURES / "p0_pilot.json").read_text())
    del res["systems"]["chua"]["H1d"]
    res["systems"]["rossler"]["H1b"]["PLP"]["ci"] = [0.8, 0.8]
    path = tmp_path / "results.json"
    path.write_text(json.dumps(res))
    code = rr.main([str(path), "--states", str(tmp_path / "none")])
    out = capsys.readouterr().out
    assert code == 2
    assert "not computable: chua H1d analog_seed: results leaf H1d/rows/analog_seed is absent" in out
    assert "not computable: rossler H1b PLP slope" in out and "half-width not finite and positive" in out
    assert "H3c" in out.split("=== chua")[1]  # the other rows of the system are still reported


def test_tool_does_not_modify_the_run_directory(tmp_path: Path) -> None:
    """Read-only: every file of the run directory is byte-identical after the report."""
    run = write_run(tmp_path / "run")
    before = {p: p.read_bytes() for p in sorted(run.rglob("*")) if p.is_file()}
    rr.main([str(run)])
    after = {p: p.read_bytes() for p in sorted(run.rglob("*")) if p.is_file()}
    assert before == after and before


def test_script_runs_isolated(tmp_path: Path) -> None:
    """``python -I tools/rehearsal_report.py`` works (its own path line), prints the label."""
    done = subprocess.run([sys.executable, "-I", str(ROOT / "tools" / "rehearsal_report.py"),
                           str(FIXTURES / "p1_pilot.json"), "--states", str(tmp_path / "none")],
                          capture_output=True, text=True, check=False, timeout=120)
    assert done.returncode == 2, done.stderr
    assert done.stdout.startswith("DEVELOPMENT (DEV-0)")


# ------------------------------------------------------------------------------------------ R5 vs R1
def observed_file(dest: Path, factors: dict[str, float], run_path: Path) -> Path:
    """A full-size results file whose half-width of each listed label is ``factor x`` the n-only
    projection of the run, intervals centred on 0 (only the half-widths are read)."""
    base = json.loads(run_path.read_text())
    cfg = base["config"]
    out = {"config": {"name": "full", "seed_id": "DEV-2"},
           "provenance": {"seed_id": "DEV-2", "seed_kind": "development", "commit": "x"},
           "systems": {}}
    for system, tree in base["systems"].items():
        copy = json.loads(json.dumps(tree))
        for spec in rr.specs_for(cfg, "A1"):
            if spec.label not in factors:
                continue
            block = copy
            for key in spec.path:
                block = block[key]
            lo, hi = block[spec.interval]
            nominal = (hi - lo) / 2 * rr.n_factor(cfg[spec.size_key], getattr(PRESETS["full"],
                                                                              spec.size_key))
            hw = factors[spec.label] * nominal
            block[spec.interval] = [-hw, hw]
        out["systems"][system] = copy
    dest.mkdir(parents=True)
    path = dest / "results.json"
    path.write_text(json.dumps(out))
    return path


def test_observed_run_is_read_against_the_projection(tmp_path: Path) -> None:
    """R5 against R1: both readings, by hand.

    H1b (point projection 1.007 x nominal): observed 1.2 x nominal is inside both; 2 x is outside
    both; 0.65 x nominal is outside (i) (< 0.67) and outside (ii) (0.67 x 1.007 = 0.6747 > 0.65).
    Q-N logit (range 0.434 to 0.712 over sqrt(0.5) = 0.7071, i.e. 0.614 to 1.007 x nominal):
    0.5 x nominal is outside (i) (< 0.67) but inside (ii) (0.67 x 0.614 = 0.4115 < 0.5).
    """
    run = FIXTURES / "p0_pilot.json"
    for factor, want_i, want_ii in ((1.2, False, False), (2.0, True, True), (0.65, True, True)):
        full = observed_file(tmp_path / f"f{factor}", {"H1b PLP slope": factor}, run)
        rep = rr.Report()
        rr.run(run, states_dir=tmp_path / "none", observed_path=full, rep=rep)
        row = next(r for r in rep.data["rows"]["lorenz63"] if r["label"] == "H1b PLP slope")
        assert row["obs_reading_i"] is want_i and row["obs_reading_ii"] is want_ii, factor
        assert row["observed"] == pytest.approx(factor * row["nominal"], rel=1e-12)
    full = observed_file(tmp_path / "q", {"Q-N oracle logit": 0.5}, run)
    rep = rr.Report()
    rr.run(run, states_dir=tmp_path / "none", observed_path=full, rep=rep)
    row = next(r for r in rep.data["rows"]["chua"] if r["label"] == "Q-N oracle logit")
    assert row["obs_reading_i"] is True and row["obs_reading_ii"] is False
    assert rr.which(row, "obs_") == "(i)"
    assert any("outside the band ((i)): chua Q-N oracle logit" in line for line in rep.lines)


def test_observed_run_must_be_full_and_development(tmp_path: Path) -> None:
    """``--observed`` with a pilot run, or a non-development one, is refused (exit 2)."""
    run = FIXTURES / "p0_pilot.json"
    with pytest.raises(rr.NotComputable, match="not 'full'"):
        rr.run(run, states_dir=tmp_path / "none", observed_path=FIXTURES / "p1_pilot.json")
    res = json.loads(run.read_text())
    res["config"]["name"] = "full"
    res["provenance"]["seed_kind"] = "confirmatory"
    bad = tmp_path / "results.json"
    bad.write_text(json.dumps(res))
    with pytest.raises(rr.Refused):
        rr.run(run, states_dir=tmp_path / "none", observed_path=bad)


# ------------------------------------------------------------------------------------------ predictions
def test_preregistered_predictions_are_checked_within_printed_precision(tmp_path: Path) -> None:
    """H2e 0.44 to 0.76 and H2b(ii) 0.68 to 0.85 of v3: inside; a value beyond is a finding.

    The slack is half a unit of the last printed digit (0.005); the tests stay 0.001 away from the
    edge (a round trip through the half-width would blur an exact edge by 1e-16). Reference: hand
    ratios.
    """
    cfg = json.loads((FIXTURES / "p0_pilot.json").read_text())["config"]
    full = PRESETS["full"]

    def row_for(label: str, hw_full_over_v3: float, v3: float, factor: float) -> dict:
        spec = next(s for s in rr.specs_for(cfg, "A1") if s.label == label)
        hw = hw_full_over_v3 * v3 / factor
        block = {"ci": [0.0, 2 * hw], "mean_change": 0.0, "median_change": 0.0, "level":
                 rr.PRIMARY_LEVEL if spec.level == "primary" else rr.SECONDARY_LEVEL}
        tree = {"H2b": {"library_change": block}, "H2e": {"by_noise": {"0.01": block}}}
        return rr.project_row(spec, "lorenz63", tree, cfg, None, rr.Report(), full)

    f_h2b = math.sqrt(0.3) * 1.014
    assert row_for("H2b(ii)", 0.80, 0.03, f_h2b)["prediction"]["within"] is True
    assert row_for("H2b(ii)", 0.68 - 0.004, 0.03, f_h2b)["prediction"]["within"] is True
    assert row_for("H2b(ii)", 0.68 - 0.006, 0.03, f_h2b)["prediction"]["within"] is False
    assert row_for("H2b(ii)", 0.85 + 0.004, 0.03, f_h2b)["prediction"]["within"] is True
    assert row_for("H2b(ii)", 0.85 + 0.006, 0.03, f_h2b)["prediction"]["within"] is False
    f_h2e = math.sqrt(0.3) * 1.007
    assert row_for("H2e rho=0.01", 0.60, 0.04, f_h2e)["prediction"]["within"] is True
    assert row_for("H2e rho=0.01", 0.78, 0.04, f_h2e)["prediction"]["within"] is False


def test_qn_prediction_holds_iff_reading_ii_is_silent() -> None:
    """Q-N logit "undetermined by the projection": within iff the whole range is not outside.

    Hand arithmetic, v3 = 0.04, training range 0.61 to 1 times the point factor: a high end of
    0.04 gives the range [0.0244, 0.04], which reaches into [0.0268, 0.06] (silent); a high end of
    0.02 gives [0.0122, 0.02], wholly below 0.0268 (reading (ii) fires, the prediction fails).
    """
    cfg = json.loads((FIXTURES / "p0_pilot.json").read_text())["config"]
    spec = next(s for s in rr.specs_for(cfg, "A1") if s.label == "Q-N oracle logit")
    point = math.sqrt(0.5) * 1.007
    for high, within in ((0.04, True), (0.02, False)):
        hw = high / point
        tree = {"Q-N": {"oracle": {"logit_w_interior": {"ci": [0.0, 2 * hw], "delta_r2": 0.0}}}}
        row = rr.project_row(spec, "chua", tree, cfg, None, rr.Report(), PRESETS["full"])
        assert row["reading_ii"] is (not within)
        assert row["prediction"]["within"] is within


def test_missing_block_length_is_not_computable_not_a_default(tmp_path: Path, capsys) -> None:
    """R4: no ``bootstrap_block`` in the configuration: kappa_E falls back to the range, FALLBACK,
    one "not computable" line per part (12), exit 2; the dump is not read with an invented block."""
    run = write_run(tmp_path / "run", drop_block=True)
    code = rr.main([str(run)])
    out = capsys.readouterr().out
    assert code == 2
    assert out.count("results leaf bootstrap_block is absent") == 12
    assert out.count("(FALLBACK)") == 12 and "range fallback for 12" in out


def test_v7_rows_are_projected_like_the_sweep_criteria() -> None:
    """R5: V7 (median slope, efficiency at each noise level) at n_test_sweep, 95%, B 1.007.

    Reference: the fixture's own V7 intervals and the closed form ``sqrt(300/1000) x 1.007``
    (rel 1e-12, a product of three numbers).
    """
    res = json.loads((FIXTURES / "p0_pilot.json").read_text())
    rows = {r["label"]: r for r in tool_rows_from(res)["lorenz63"]}
    v7 = res["systems"]["lorenz63"]["V7"]
    factor = math.sqrt(300 / 1000) * 1.007
    lo, hi = v7["ci"]
    row = rows["V7 median slope"]
    assert row["hw_run"] == pytest.approx((hi - lo) / 2, rel=1e-12)
    assert row["hw_lo"] == row["hw_hi"] == pytest.approx((hi - lo) / 2 * factor, rel=1e-12)
    assert row["estimate"] == v7["median_slope"] and "v3" not in row
    lo, hi = v7["efficiency_ci_by_noise"]["0.05"]
    row = rows["V7 efficiency rho=0.05"]
    assert row["hw_run"] == pytest.approx((hi - lo) / 2, rel=1e-12)
    assert row["hw_hi"] == pytest.approx((hi - lo) / 2 * factor, rel=1e-12)
    assert row["estimate"] == v7["efficiency_median_by_noise"]["0.05"]


def tool_rows_from(res: dict) -> dict[str, list[dict]]:
    """The rows by system of a results tree held in memory (no dump)."""
    rep = rr.Report()
    cfg, full = res["config"], PRESETS["full"]
    out: dict[str, list[dict]] = {}
    for system, tree in res["systems"].items():
        out[system] = [rr.project_row(spec, system, tree, cfg, None, rep, full)
                       for spec in rr.specs_for(cfg, str(tree["H2c"]["best_single"]))]
    return out


def test_h2c_is_printed_relative_to_its_mse_level() -> None:
    """R5: hw / MSE level, with level = mean / relative.

    Hand arithmetic: mean 0.02 and relative 0.2 give a level 0.1; hw 0.01 gives 0.1; the
    projection scales it by the same factor as the half-width. A zero relative leaf is "not
    computable".
    """
    cfg = json.loads((FIXTURES / "p0_pilot.json").read_text())["config"]
    spec = next(s for s in rr.specs_for(cfg, "A1") if s.label == "H2c A4-A2")
    tree = {"H2c": {"A4_minus_A2": {"mean": 0.02, "ci": [0.01, 0.03], "relative": 0.2}}}
    row = rr.project_row(spec, "lorenz63", tree, cfg, None, rr.Report(), PRESETS["full"])
    assert row["rel_run"] == pytest.approx(0.1, rel=1e-12)
    assert row["rel_lo"] == pytest.approx(0.1 * row["f_lo"], rel=1e-12)
    tree["H2c"]["A4_minus_A2"]["relative"] = 0.0
    with pytest.raises(rr.NotComputable, match="no MSE level"):
        rr.project_row(spec, "lorenz63", tree, cfg, None, rr.Report(), PRESETS["full"])
