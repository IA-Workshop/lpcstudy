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


@pytest.fixture
def point_policy(monkeypatch):
    """The ``"point"`` kappa policy: the c7d6e41 behaviour that the exit-0 condition of G2 describes."""
    monkeypatch.setattr(rr, "KAPPA_POLICY", "point")


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
    """Without a dump the range is used and shown (FALLBACK), exit 2, nothing else open.

    Reference: the arithmetic of the plan (12 kappa_E parts: H2c x2, H2d, H3c over 3 systems; one
    "no dump" line per system and one "range governs" line per part, G2: a FALLBACK is counted).
    Findings ("v3 precision not reproduced") never change the exit code, and no MISMATCH arises.
    """
    code = rr.main([str(FIXTURES / "p0_pilot.json"), "--states", str(tmp_path / "none")])
    out = capsys.readouterr().out
    assert code == 2
    assert out.splitlines()[0] == "DEVELOPMENT (DEV-0): conditional on one realization; not a hypothesis test"
    assert out.count("(FALLBACK)") == 12
    # three systems without a dump, twelve parts with the range governing, plus the closing count
    assert out.count("not computable: ") == 3 + 12 + 1
    assert "not computable: 15 item(s)" in out
    assert "kappa_E: point estimate from the dump governs for 0 of 12 parts; range fallback for 12" in out
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
              dump_seed: str = "DEV-0", drop_block: bool = False, mutate=None) -> Path:
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
    if mutate is not None:
        mutate(res)
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


def run_world(tmp_path: Path, capsys, **kwargs) -> tuple[int, str, dict]:
    """Write a synthetic run, report it with ``--json``, return (code, stdout, parsed json)."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    run = write_run(tmp_path / "run", **kwargs)
    json_out = tmp_path / "out.json"
    code = rr.main([str(run), "--json", str(json_out)])
    return code, capsys.readouterr().out, json.loads(json_out.read_text())


def test_complete_pilot_with_dump_exits_zero_when_the_point_estimate_governs(
        tmp_path: Path, capsys, point_policy) -> None:
    """G2: every row computed (18 criteria, V7, every H3a pair), every reproduction check passed,
    kappa_E a point estimate from a reproducing dump: exit 0, nothing open, no FALLBACK.

    Reference: ``kappa_by_hand`` (loops from the definitions of V_i and the influence series,
    rel 1e-10, see the module docstring). The projected half-widths use the point kappa at both
    ends (lo = hi).
    """
    code, out, data = run_world(tmp_path, capsys)
    assert code == 0, out
    assert "not computable" not in out and "FALLBACK" not in out
    assert "MISMATCH" not in out and out.count("MATCH") >= 12
    assert "kappa_E: point estimate from the dump governs for 12 of 12" in out
    expect = {"H2c A4-A2": ("diff", "A4", "A2"), "H2c A4-A1": ("diff", "A4", "A1"),
              "H2d": ("ratio", "A4", "A3"), "H3c": ("ratio", "A5", "A4")}
    for system in SYSTEMS:
        rows = {r["label"]: r for r in data["rows"][system]}
        assert len(rows) == 23 and set(data["h3a"]) == set(SYSTEMS)
        for label, (kind, first, second) in expect.items():
            want = kappa_by_hand(system, kind, first, second)
            row = rows[label]
            assert row["kappa"]["kappa"] == pytest.approx(want, rel=1e-10), (system, label)
            assert row["f_lo"] == row["f_hi"]
            assert row["f_lo"] == pytest.approx(
                math.sqrt(0.5) * rr.b_factor("primary" if label == "H3c" else "secondary", 500, 2000)
                * want, rel=1e-10)


def test_default_policy_range_governs_and_exit_is_two(tmp_path: Path, capsys) -> None:
    """R2 working default (a): with a reproducing dump the range [0.7071, 1] still governs the
    H2c, H2d and H3c projections (0.504-0.712 and 0.507-0.717), the point kappa is information
    only, labelled biased, and G2 counts the FALLBACK: exit 2, with exactly the 12 parts open.

    Reference: the note's ranges (closed forms) and ``kappa_by_hand`` for the information value.
    """
    code, out, data = run_world(tmp_path, capsys)
    assert code == 2
    open_lines = [line for line in out.splitlines() if line.startswith("  not computable")]
    assert len(open_lines) == 12 and all("range governs (R2" in line for line in open_lines)
    assert out.count("(FALLBACK)") == 12 and out.count("kappa_E point estimator biased (R2): range governs") == 12
    assert "MISMATCH" not in out and "exit 0 is unreachable while the range governs" in out
    for system in SYSTEMS:
        for row in data["rows"][system]:
            if row["label"].startswith(("H2c", "H2d")):
                assert row["f_lo"] == pytest.approx(math.sqrt(0.5) * 1.007 * math.sqrt(0.5), rel=1e-12)
                assert row["f_hi"] == pytest.approx(math.sqrt(0.5) * 1.007, rel=1e-12)
                assert row["kappa_governs"] == "range"
            if row["label"] == "H3c":
                assert row["f_lo"] == pytest.approx(math.sqrt(0.5) * 1.014 * math.sqrt(0.5), rel=1e-12)
                assert row["f_hi"] == pytest.approx(math.sqrt(0.5) * 1.014, rel=1e-12)
                assert row["kappa"]["kappa"] == pytest.approx(
                    kappa_by_hand(system, "ratio", "A5", "A4"), rel=1e-10)


def test_best_single_a0_uses_cp_alone(tmp_path: Path, capsys, point_policy) -> None:
    """With ``best_single = A0`` the second H2c row is A4 - A0 and V is E_C (weight 1)."""
    code, out, data = run_world(tmp_path, capsys, best="A0")
    assert code == 0, out
    rows = {r["label"]: r for r in data["rows"]["rossler"]}
    assert "H2c A4-A0" in rows and "H2c A4-A1" not in rows
    assert rows["H2c A4-A0"]["kappa"]["kappa"] == pytest.approx(
        kappa_by_hand("rossler", "diff", "A4", "A0"), rel=1e-10)


def test_dump_that_disagrees_with_the_results_is_a_mismatch(tmp_path: Path, capsys,
                                                            point_policy) -> None:
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
    assert "kappa_E: point estimate from the dump governs for 9 of 12 parts; range fallback for 3" in out
    h3c = [line for line in out.splitlines() if line.startswith("  H3c ")]
    assert len(h3c) == 3 and all("0.507-0.717" in line for line in h3c)


def test_mismatch_beats_not_computable_and_nothing_is_skipped(tmp_path: Path, capsys,
                                                              point_policy) -> None:
    """G2 precedence: a MISMATCH together with a H3a pair of p_raw None and a missing V7 block is
    still exit 1; without the mismatch the same run is exit 2."""
    def edit(res: dict) -> None:
        res["systems"]["chua"]["H3a"]["logrank_p_raw"][1] = None
        del res["systems"]["rossler"]["V7"]
    code, out, _ = run_world(tmp_path / "a", capsys, scale_h3c=1.0 + 1e-6, mutate=edit)
    assert code == 1 and "p_raw None" in out and "rossler V7 median slope" in out
    code, out, _ = run_world(tmp_path / "b", capsys, mutate=edit)
    assert code == 2 and "MISMATCH" not in out
    open_lines = [line for line in out.splitlines() if line.startswith("  not computable")]
    assert len(open_lines) == 1 + 5  # the H3a pair and the five V7 rows of rossler
    assert any("chua H3a pair (1, 0)" in line or "chua H3a pair (2, 1)" in line for line in open_lines)


@pytest.mark.parametrize(("scale", "code"), [(1.0 + 5e-13, 0), (1.0 + 2e-12, 1)])
def test_reproduction_bound_passes_at_half_and_fails_at_twice(tmp_path: Path, capsys, scale, code,
                                                              point_policy) -> None:
    """The dump-to-results bound ``1e-12 |leaf|``: passes at 0.5x of it, fails at 2x.

    A pass is a complete run (exit 0, no MISMATCH, no FALLBACK); a failure exits 1.
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


# ------------------------------------------------------------------------------------------ G1: H3a
def erfc_p(chi: float) -> float:
    """The 1-df chi-square survival function, ``erfc(sqrt(x/2))`` (an exact closed form)."""
    return math.erfc(math.sqrt(chi / 2.0))


def test_production_alpha_is_read_from_the_source() -> None:
    """The bar is the constant of ``lpcstudy/analysis.py`` (read as text), equal to the imported one."""
    from lpcstudy import analysis
    assert rr.production_constant("H3A_ALPHA") == analysis.H3A_ALPHA == 0.01
    with pytest.raises(rr.NotComputable, match="not assigned"):
        rr.production_constant("NO_SUCH_CONSTANT")


def test_holm_equals_production_and_hand_values() -> None:
    """Holm step-down: hand case (0.01, 0.04, 0.03) -> (0.03, 0.06, 0.06); equal to production's."""
    from lpcstudy.statistics import holm_adjust
    assert rr.holm_adjust([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06], rel=1e-15)
    g = rng_for("holm")
    for _ in range(5):
        p = g.uniform(0, 0.05, 7).tolist()
        assert rr.holm_adjust(p) == holm_adjust(p)
    assert rr.holm_adjust([1.0, 0.9]) == [1.0, 1.0]


def test_h3a_projection_against_closed_forms() -> None:
    """chi2_pilot = isf(p, 1), doubled, p_full = sf: textbook values and the erfc closed form.

    Reference: the chi-square(1) quantiles 3.841458820694124 (p = 0.05) and 6.634896601021213
    (p = 0.01) (rel 1e-9: ten digits typed), and ``erfc(sqrt(x/2))`` for the survival function
    (rel 1e-9: the quantile is exact to a few ulp, the sensitivity of erfc to x is below 40).
    """
    for p, chi in ((0.05, 3.841458820694124), (0.01, 6.634896601021213)):
        got = rr.h3a_projection(p, 2.0)
        assert got["chi2_pilot"] == pytest.approx(chi, rel=1e-9) and got["computed"]
        assert got["chi2_full"] == pytest.approx(2.0 * chi, rel=1e-9) and not got["lower_bound"]
        assert got["p_full"] == pytest.approx(erfc_p(2.0 * chi), rel=1e-9)
        assert erfc_p(got["chi2_pilot"]) == pytest.approx(p, rel=1e-9)
    one = rr.h3a_projection(1.0, 2.0)
    assert one["chi2_pilot"] == 0.0 and one["p_full"] == 1.0
    with pytest.raises(rr.NotComputable):
        rr.h3a_projection(1.5, 2.0)
    with pytest.raises(rr.NotComputable):
        rr.h3a_projection(0.5, 0.0)


@pytest.mark.parametrize("p_raw", [1e-301, 0.0])
def test_h3a_tiny_p_is_a_lower_bound_and_counted_computed(p_raw: float) -> None:
    """p_raw below 1e-300: chi2 is the lower bound isf(1e-300, 1) (about 1380), computed, and the
    projected p (an upper bound) is below every bar. Reference: erfc closed form at 1e-300."""
    got = rr.h3a_projection(p_raw, 2.0)
    assert got["computed"] and got["lower_bound"]
    assert erfc_p(got["chi2_pilot"]) == pytest.approx(1e-300, rel=1e-6)
    assert got["chi2_full"] == 2.0 * got["chi2_pilot"] and got["p_full"] <= 1e-300


def test_h3a_none_is_not_computed() -> None:
    """p_raw None (zero log-rank variance): not computed; no number is invented."""
    got = rr.h3a_projection(None, 2.0)
    assert got["computed"] is False and got["chi2_pilot"] is None and got["p_full"] is None


def h3a_tree(raw: list) -> tuple[dict, dict]:
    """A results tree with an H3a block of ``len(raw)`` pairs, and the pilot configuration."""
    cfg = json.loads((FIXTURES / "p0_pilot.json").read_text())["config"]
    pairs = [[i + 1, i] for i in range(len(raw))]
    return {"H3a": {"chosen_K": len(raw) + 1, "pairs": pairs, "logrank_p_raw": raw}}, cfg


def test_h3a_reading_reachable_not_reachable_and_not_determined() -> None:
    """The reading by hand (n_test 500 -> 1000: chi2 doubles; p_full = erfc(sqrt(chi2_pilot))).

    * (1e-10, 0.05): p_full 1e-20-ish and erfc(sqrt(3.8415)) = 0.0056; Holm over 2: (2e-20, 0.0056)
      both below 0.01: reachable.
    * (1e-10, 0.1): chi2_pilot 2.7055, p_full = erfc(1.645) = 0.0200 > 0.01: not reachable.
    * a None pair: not determined, the others' values stay.
    * (0.0, 1e-5): the tiny pair counts as computed; reachable.
    """
    full = PRESETS["full"]
    for raw, reading in (([1e-10, 0.05], "reachable"), ([1e-10, 0.1], "not reachable"),
                         ([1e-10, None], "not determined"), ([0.0, 1e-5], "reachable")):
        tree, cfg = h3a_tree(raw)
        got = rr.h3a_system(tree, cfg, full)
        assert got["reading"] == reading, raw
        assert got["factor"] == 2.0 and got["alpha"] == 0.01 and got["chosen_K"] == len(raw) + 1
    tree, cfg = h3a_tree([1e-10, 0.05])
    got = rr.h3a_system(tree, cfg, full)
    chi = 3.841458820694124
    assert got["entries"][1]["p_full"] == pytest.approx(erfc_p(2 * chi), rel=1e-9)
    assert got["largest_holm_full"] == pytest.approx(erfc_p(2 * chi), rel=1e-9)  # rank 1 of 2
    assert got["entries"][0]["holm_full"] == pytest.approx(2 * got["entries"][0]["p_full"], rel=1e-15)
    tree, cfg = h3a_tree([1e-10, None])
    got = rr.h3a_system(tree, cfg, full)
    assert got["entries"][1]["computed"] is False and got["entries"][1]["holm_full"] == 1.0


def test_h3a_missing_leaves_are_not_computable() -> None:
    """A block without ``logrank_p_raw``, or with unequal lengths, is "not computable"."""
    tree, cfg = h3a_tree([0.1, 0.2])
    with pytest.raises(rr.NotComputable):
        rr.h3a_system({"H3a": {"chosen_K": 3, "pairs": [[1, 0]]}}, cfg, PRESETS["full"])
    tree["H3a"]["logrank_p_raw"] = [0.1]
    with pytest.raises(rr.NotComputable):
        rr.h3a_system(tree, cfg, PRESETS["full"])


def test_h3a_is_printed_conditional_on_k_and_matches_a_hand_holm(tmp_path: Path, capsys) -> None:
    """P0 fixture: each system prints its pairs, "conditional on K_pilot", a reading; the Chua
    largest projected Holm p equals a hand computation (erfc, loops) to 1e-9.

    Chua pairs p_raw (0.14112, 1.4872e-5, 0.0072534): p_full = erfc(sqrt(chi2_pilot)), Holm
    (3, 2, 1) x sorted p_full.
    """
    rr.main([str(FIXTURES / "p0_pilot.json"), "--states", str(tmp_path / "none"), "--json",
             str(tmp_path / "o.json")])
    out = capsys.readouterr().out
    assert out.count("conditional on K_pilot") >= 6 and "H3a chua: conditional on K_pilot = 4" in out
    data = json.loads((tmp_path / "o.json").read_text())["h3a"]
    raw = json.loads((FIXTURES / "p0_pilot.json").read_text())["systems"]["chua"]["H3a"]["logrank_p_raw"]
    chi = [float(rr.sps.chi2.isf(p, 1)) for p in raw]
    full = sorted(erfc_p(2.0 * c) for c in chi)
    hand = max(min(1.0, (3 - i) * p) for i, p in enumerate(full))
    assert data["chua"]["largest_holm_full"] == pytest.approx(hand, rel=1e-9)
    assert data["chua"]["reading"] == "not reachable" and data["lorenz63"]["reading"] == "not reachable"


def test_h3a_tiny_and_none_pairs_in_the_report(tmp_path: Path, capsys) -> None:
    """A tiny pair prints a lower bound (">=") and counts computed; a None pair is listed as not
    computable (exit 2) and the reading is "not determined"."""
    res = json.loads((FIXTURES / "p0_pilot.json").read_text())
    res["systems"]["rossler"]["H3a"]["logrank_p_raw"] = [1e-301, None]
    path = tmp_path / "results.json"
    path.write_text(json.dumps(res))
    code = rr.main([str(path), "--states", str(tmp_path / "none")])
    out = capsys.readouterr().out
    assert code == 2
    assert "chi2 >= " in out and "p_full <= " in out
    assert "not computable: rossler H3a pair (1, 0): zero log-rank variance" in out
    assert "H3a rossler (conditional on K_pilot = 3): pass reachable at full size: not determined" in out


# ------------------------------------------------------------------------------------------ G3: margin
def test_margin_reading_at_the_edges() -> None:
    """G3: m = 0.1 - hw_full against 0.01 x [0.67, 1.5] = [0.0067, 0.015]; edges inside.

    Reference: hand values; hw_full 0.0933 and 0.0850 are the same bounds on the half-width.
    """
    lo, hi = 0.67 * 0.01, 1.5 * 0.01
    assert not rr.outside_margin(lo, lo) and not rr.outside_margin(hi, hi)
    assert rr.outside_margin(np.nextafter(lo, 0.0), np.nextafter(lo, 0.0))
    assert rr.outside_margin(np.nextafter(hi, 1.0), np.nextafter(hi, 1.0))
    assert not rr.outside_margin(0.001, 0.05)  # a range reaching into the band is undetermined
    assert rr.outside_margin(0.02, 0.05) and rr.outside_margin(-0.01, 0.005)
    for hw, outside in ((0.09, False), (0.0933 - 1e-4, False), (0.0933 + 1e-4, True),
                        (0.0850 + 1e-4, False), (0.0850 - 1e-4, True), (0.1458 * 0.717, True)):
        m = rr.H2A_PARTIAL_EDGE - hw
        assert rr.outside_margin(m, m) is outside, hw


def h2a_row(hw_projected: float, label: str = "H2a(ii) zero") -> dict:
    """A row of H2a(ii) whose projected half-width is ``hw_projected`` (primary level, n factor)."""
    cfg = json.loads((FIXTURES / "p0_pilot.json").read_text())["config"]
    hw = hw_projected / (math.sqrt(0.5) * 1.014)
    part = {"partial_corr": 0.0, "ci": [-hw, hw]}
    tree = {"H2a": {"part_ii": {"zero": part, "interior": part}}}
    spec = next(s for s in rr.specs_for(cfg, "A1") if s.label == label)
    return rr.project_row(spec, "lorenz63", tree, cfg, None, rr.Report(), PRESETS["full"])


def test_h2a_ii_governing_reading_is_the_margin_and_the_hw_band_is_beside_it() -> None:
    """Hand arithmetic at projected hw (n factor 0.7071, B 1.014; nominal = projected / 1.014):

    * 0.0900: m = 0.0100, inside both readings, and inside the old hw band.
    * 0.0950: m = 0.0050 < 0.0067: both fire; the old hw band (ratio 1.06) is silent.
    * 0.0935: m = 0.0065 fires (ii); the n-only value 0.0935/1.014 = 0.09221 has m = 0.0078, so
      (i) is silent: the readings differ on the low side, as PF-4 says.
    * 0.0800: m = 0.0200 > 0.015 fires both; the old band (ratio 0.89) is silent.
    """
    for hw, i, ii in ((0.0900, False, False), (0.0950, True, True), (0.0935, False, True),
                      (0.0800, True, True)):
        row = h2a_row(hw)
        assert (row["reading_i"], row["reading_ii"]) == (i, ii), hw
        assert row["margin_lo"] == pytest.approx(0.1 - hw, rel=1e-9)
        assert row["margin_nominal"] == pytest.approx(0.1 - hw / 1.014, rel=1e-9)
        assert not row["legacy_reading_i"] and not row["legacy_reading_ii"]
    assert rr.which(h2a_row(0.0935)) == "(ii)"
    lines = rr.format_row(h2a_row(0.0950))
    assert any("GOVERNING" in line and "[0.0067, 0.015]" in line for line in lines)
    assert any("non-governing" in line and "[0.0603, 0.135]" in line for line in lines)
    far = h2a_row(0.0950 * 1.8 / 1.06)  # hw/0.09 = 1.8 > 1.5: the old band fires as well
    assert far["legacy_reading_i"] and far["legacy_reading_ii"]


@pytest.mark.parametrize("name", ["p0", "p1"])
def test_h2a_ii_governing_readings_on_p0_p1_against_the_log(name: str, tmp_path: Path) -> None:
    """Pre-registered: the margin reading fires on most parts. Reference: the log's projected
    half-widths (4 decimals, the margin is known to 5e-5; no part lies within 1e-4 of an edge)."""
    logged, mine = parse_log()[name], tool_rows(name, tmp_path)
    for label in ("H2a(ii) zero", "H2a(ii) interior"):
        for system in SYSTEMS:
            margin = 0.1 - logged[(label, system)]["hi"]
            assert min(abs(margin - 0.0067), abs(margin - 0.015)) > 1e-4, (label, system)
            fires = margin < 0.0067 or margin > 0.015
            row = mine[(label, system)]
            assert row["reading_i"] is fires and row["reading_ii"] is fires, (name, label, system)
