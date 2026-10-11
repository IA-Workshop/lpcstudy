"""Report header and output files for a fake results dict (WU-0001.4; LPC.PC.13, LPC.PC.18).

The fake dict has ``systems: {}`` and a ``verdicts`` stub per hypothesis, so no study is run.
The confirmatory value below is synthetic (LPC.PC.7). Checks are exact string checks.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pytest

from lpcstudy import provenance
from lpcstudy.config import SMOKE, StudyConfig
from lpcstudy.identifiers import HYPOTHESIS_TABLE
from lpcstudy import report
from lpcstudy.report import (HYPOTHESES, _key_number, header_lines, make_figures, save_json,
                             verdicts, write_markdown)
from lpcstudy.seeds import with_seed

SYNTHETIC_SEED = 987654321987654321
DEV_LABEL = "**DEVELOPMENT (DEV-0): not a hypothesis test** · **UNPROMOTED**"
CONF_LABEL = "**CONFIRMATORY: UNPROMOTED**"
ABSENT = "**UNPROMOTED** · provenance absent (output written before WU-0001)"


@pytest.fixture(autouse=True)
def _clean_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """No test sees a confirmatory seed or salt (LPC.PC.7)."""
    monkeypatch.delenv("LPC_CONF_SEED", raising=False)
    monkeypatch.delenv("LPC_CONF_SALT", raising=False)


def fake_results(seed_id: str) -> tuple[dict, StudyConfig]:
    """Return a fake results dict with a finished provenance block, and its config."""
    seed = SYNTHETIC_SEED if seed_id.startswith("CONF-") else SMOKE.seed
    config = with_seed(SMOKE, seed_id, seed)
    clock = provenance.RunClock()
    block = provenance.finish(provenance.collect(config, seed_id, ["--preset", "smoke"], clock),
                              clock)
    results = {"config": provenance.config_record(config), "systems": {}, "provenance": block,
               "verdicts": {h: {"by_system": {}, "verdict": "supported"} for h in HYPOTHESES}}
    return results, config


def test_confirmatory_value_is_in_neither_output_file(tmp_path: Path) -> None:
    """The synthetic confirmatory seed appears in neither ``results.json`` nor ``RESULTS.md``.

    Reference: ``str(seed)`` searched in both files written by ``save_json`` and
    ``write_markdown`` (the roadmap criterion). The id ``CONF-1`` and the label are present.
    """
    results, config = fake_results("CONF-1")
    save_json(results, tmp_path / "results.json")
    write_markdown(results, config, tmp_path / "RESULTS.md")
    for name in ("results.json", "RESULTS.md"):
        text = (tmp_path / name).read_text()
        assert str(SYNTHETIC_SEED) not in text, name
        assert "CONF-1" in text and "LPC_CONF" not in text, name
    assert json.loads((tmp_path / "results.json").read_text())["config"]["seed"] is None


def test_header_labels_are_exact_in_the_markdown_file(tmp_path: Path) -> None:
    """Line 3 of ``RESULTS.md`` is the exact label line for a DEV and a CONF run.

    Reference: the strings fixed by the plan (Q3): development prints the DEV label and
    UNPROMOTED; confirmatory prints ``CONFIRMATORY: UNPROMOTED``. Exact.
    """
    for seed_id, label in (("DEV-0", DEV_LABEL), ("CONF-1", CONF_LABEL)):
        results, config = fake_results(seed_id)
        write_markdown(results, config, tmp_path / f"{seed_id}.md")
        lines = (tmp_path / f"{seed_id}.md").read_text().splitlines()
        assert lines[0].startswith("# Results") and lines[1] == "" and lines[2] == label


def test_header_table_has_every_key_except_config_and_the_config_json() -> None:
    """The table has a row per provenance key except ``config``; the details block parses.

    Reference: the block's own keys (the table is a view of them). The JSON in the
    ``<details>`` block equals the block's ``config`` after a JSON round trip. Exact.
    """
    results, _ = fake_results("DEV-0")
    block = results["provenance"]
    lines = header_lines(block)
    rows = [ln for ln in lines if ln.startswith("| ") and not ln.startswith("| Provenance")]
    assert [ln.split(" | ")[0][2:] for ln in rows] == [k for k in block if k != "config"]
    assert "| promoted | false |" in rows and "| complete | true |" in rows
    start = lines.index("```json") + 1
    end = lines.index("```", start)
    assert json.loads("\n".join(lines[start:end])) == json.loads(json.dumps(block["config"]))
    assert lines[start - 3].startswith("<details>") and lines[-1] == "</details>"


def test_missing_provenance_is_flagged_and_stored_block_is_used_as_is() -> None:
    """No block gives the 'provenance absent' line; a stored block renders the same after JSON.

    Reference: the plan's ``--report-only`` rule. A block that went through ``json`` (as when
    read back from ``results.json``) renders identical lines. Exact.
    """
    assert header_lines(None) == [ABSENT]
    results, _ = fake_results("DEV-0")
    block = results["provenance"]
    assert header_lines(json.loads(json.dumps(block))) == header_lines(block)


def test_markdown_without_provenance_has_the_absent_line(tmp_path: Path) -> None:
    """``write_markdown`` on results with no ``provenance`` key prints the absent line."""
    results, config = fake_results("DEV-0")
    del results["provenance"]
    write_markdown(results, config, tmp_path / "RESULTS.md")
    assert (tmp_path / "RESULTS.md").read_text().splitlines()[2] == ABSENT


def test_a_pipe_in_a_value_cannot_break_the_table() -> None:
    """A value containing ``|`` is escaped so each row keeps two cells.

    Reference: Markdown table syntax (an unescaped pipe adds a cell). Exact.
    """
    results, _ = fake_results("DEV-0")
    block = dict(results["provenance"], platform="Linux|odd\nname")
    row = next(ln for ln in header_lines(block) if ln.startswith("| platform |"))
    assert row == "| platform | Linux\\|odd name |"


def fake_system(config: StudyConfig, skip: tuple[str, ...] = ()) -> dict:
    """One system's results with the minimal content ``verdicts`` and ``write_markdown`` read.

    Every table key has a result with ``verdict`` "pass" (and ``pass`` true) and the sub-keys
    ``_key_number`` reads, except the keys in ``skip``. Q-N is an estimate and the gain bound is
    reported with no bar (v3 sections 2 and 7), so neither carries a verdict. The numbers are
    arbitrary small values chosen by hand.
    """
    hours = ["0.25", "0.5", "1", "2", "4"]
    results = {
        "H1a": {"by_noise": {"0.01": {"fitted_inverse_dim": 0.5, "ratio": 1.02,
                                      "ratio_ci": [0.9, 1.1], "verdict": "pass"}},
                "inverse_dim_reference": 0.5},
        "H1b": {"CP": {"slope": 1.0}, "PLP": {"slope": 0.9, "ci": [0.85, 0.95]},
                "verdict": "pass", "reason": None},
        "H1c": {"PLP": {"median_ratio": 1.0, "ci": [0.95, 1.05]},
                "CP": {"median_ratio": 0.5, "ci": [0.4, 0.6]}},
        "H1d": {"rows": {"analog_seed": {"spearman": 0.8}, "estimation_seed": {"spearman": 0.9},
                         "growth": {"spearman": 0.7}, "nhat": {"spearman": 0.6}},
                "verdict": "pass", "reason": None},
        "Q-N": {"role": "estimate", "primary": "oracle", "n_w_zero": 30, "n_w_one": 4,
                "n_test": 120,
                "oracle": {"logit_w_interior": {"reading": "reduces", "delta_r2": 0.01,
                                                "ci": [0.0, 0.02]},
                           "w_zero_indicator": {"reading": "distinct but small",
                                                "delta_r2": 0.02, "ci": [0.01, 0.03]},
                           "log_horizon": {"delta_r2": 0.02, "ci": [0.01, 0.03]}},
                "deployable": {"logit_w_interior": {"reading": "undetermined"},
                               "w_zero_indicator": {"reading": "substantial"}}},
        "H2a": {"median_range": 0.05, "range_ci": [0.01, 0.08], "n_eligible_states": 120,
                "part_i_verdict": "pass", "part_ii_verdict": "pass", "n_w_zero": 30,
                "n_w_one": 4,
                "part_ii": {"zero": {"partial_corr": 0.02, "ci": [-0.05, 0.08]},
                            "interior": {"partial_corr": -0.03, "ci": [-0.09, 0.04]}}},
        "H2b": {"noise": {"mean_state_spearman": 0.9},
                "library_change": {"mean_change": 0.2, "ci": [0.1, 0.3]},
                "library_curves": {"0.01": {"1000": {"median": 0.7}, "10000": {"median": 0.8}}},
                "verdict": "pass", "reason": None},
        # mean, interval and relative are consistent: relative = mean / (mean of the reference),
        # with reference means 1.5 (A2) and 1.0 (A1), so -0.15 / 1.5 = -10% and -0.05 / 1.0 = -5%
        "H2c": {"A4_minus_A2": {"mean": -0.15, "relative": -0.1, "ci": [-0.2, -0.05],
                                "verdict": "pass", "reason": None},
                "best_single": "A1",
                "A4_minus_A1": {"mean": -0.05, "relative": -0.05, "ci": [-0.1, -0.01],
                                "verdict": "pass", "reason": None},
                "A4o_minus_A2": {"relative": -0.2}},
        "H2d": {"in_distribution_excess": 0.05, "ci": [0.04, 0.06]},
        "H2e": {"by_noise": {"0.01": {"median_change": 0.1, "ci": [0.05, 0.15]},
                             "0.02": {"median_change": None, "ci": None}},
                "verdict": "pass", "reason": None},
        "gain_bound": {"fraction_within_bound": 0.95, "n_states": 40, "n_total_states": 100,
                       "n_screened_out": {"growth_nonpositive": 3,
                                          "censored_single_forecaster": 5,
                                          "negative_covariance": 52},
                       "max_gain_lyapunov": 1.5},
        "H3a": {"chosen_K": 3, "logrank_p_holm": [0.004, 0.001], "iqr_lt_mean": 0.4,
                "verdict": "pass", "reason": None},
        "H3b": {"weight_lambda": {"importance": 0.1, "ci": [0.0, 0.15]},
                "D": {"value": 0.6, "ci": [0.3, 0.8]}, "stability": 0.97,
                "verdict": "pass", "reason": None},
        "H3c": {"A5_over_A4_mse": 1.0123, "ci": [0.99, 1.04], "verdict": "pass", "reason": None},
    }
    system = {key: (value if key == "gain_bound" else
                    dict(value, **{"pass": True}) if key == "Q-N" else
                    {"verdict": "pass", "reason": None, **value, "pass": True})
              for key, value in results.items() if key not in skip}
    system["validation"] = {
        "delay_jacobian_rel_err": 1e-6, "gain_rel_err": 1e-6, "crlb_ratio_median": 1.0,
        "cp_median_vpt_lyapunov": 2.0, "km_max_abs_dev": 1e-3, "integrator_max_dev_sigma": 1e-5,
        "convergence": {str(config.n_oracle_draws): {"median_half_width": 0.01}},
        "gate": {"gate_pass": True}}
    system["scores"] = {"A0": {"mse": {h: 1.0 for h in hours}, "regret": {h: 0.1 for h in hours},
                               "agreement_href": 0.5, "km_median_lyapunov": 1.0,
                               "rmst_lyapunov": 1.0}}
    system["oracle_recovery"] = {"A4_vs_A4o": 0.5, "A5_vs_Astar": 0.5}
    system["weight_profile"] = {"horizons": [30, 60], "q25": [0.2, 0.3], "median": [0.4, 0.5],
                                "q75": [0.6, 0.7]}
    system["km_curves"] = {"A0": [1.0, 0.8, 0.5]}
    system["regime_curve"] = {"regret_ratio_by_K": {"2": 0.1, "3": 0.05},
                              "realized_K": {"2": 2, "3": 3}}
    return system


def test_markdown_lists_the_table_ids_in_order_and_marks_pending_rows(tmp_path: Path) -> None:
    """The verdict table has one row per table id, in table order; pending rows say so.

    Reference: the 14 rows of the identifier table (decision-log map, order of v3 section 2) and
    the pending markers, written out below. WU-0002.7 and .8 computed H2b, H2e, H3a and H3c, and
    WU-0002.9 decides H2d by its interval, so none of those rows is pending; Q-N is done
    (WU-0002.6). The gain bound stays pending on the gain-bound screen row (DEC-0016 O2). The
    no-result example is H2d (a plan edit of this test): the fake results have no ``H2d``, so that
    row reads its criterion with no pending note, its cell "n/a: no result" and its verdict "no
    result"; the row with a result and a pending marker ("(reported)") reads "computed with the
    v1 statistic until the gain-bound screen row". Exact string checks.
    """
    results, config = fake_results("DEV-0")
    system = fake_system(config, skip=("H2d",))
    results["systems"] = {"lorenz63": system}
    results["verdicts"] = verdicts(results, config)
    write_markdown(results, config, tmp_path / "RESULTS.md")
    lines = (tmp_path / "RESULTS.md").read_text().splitlines()
    start = lines.index("## Hypothesis verdicts")
    rows = [line for line in lines[start:] if line.startswith("| ") and "---" not in line][1:15]
    ids = [row.split(" | ")[0][2:] for row in rows]
    assert ids == ["H1a", "H1b", "H1c", "H1d", "Q-N", "H2a", "H2b", "H2c", "H2d", "H2e",
                   "(reported)", "H3a", "H3b", "H3c"]
    assert ids == [h.v3_id for h in HYPOTHESIS_TABLE]
    marked = {row.split(" | ")[0][2:]: "[computed with the v1 statistic until " in row
              for row in rows}
    assert {i for i, m in marked.items() if m} == {"(reported)"}
    qn = rows[ids.index("Q-N")]  # an estimate: read, never PASS or FAIL (v3 section 7)
    assert "reduces: oracle: interior reduces" in qn and "PASS" not in qn and "FAIL" not in qn
    assert qn.endswith("| estimate (read, no pass/fail) |")
    h2d = rows[ids.index("H2d")]
    assert h2d.endswith("MSE ratio minus 1 at H_ref; pass if upper bound ≤ 0.10 | "
                        "n/a: no result | no result |")
    gain = rows[ids.index("(reported)")]
    assert "[computed with the v1 statistic until the gain-bound screen row (amendments note " \
        "section 11; ROADMAP row not yet opened)]" in gain
    assert "within bound 0.95 (n=40 of 100; screened out: growth<=0 3, censored 5, " \
        "covariance<0 52, max gain 1.5 LT)" in gain
    assert "PASS" not in gain and "FAIL" not in gain and gain.endswith("| reported (no pass/fail) |")


def test_verdicts_skip_a_row_without_results_and_raise_on_a_partial_one() -> None:
    """``verdicts`` has no entry (and no ``KeyError``) for a key absent in every system.

    Reference: the plan for WU-0002.2 (v3 H2e has no result until WU-0002.7, so it is skipped,
    not an error; V7 is not a hypothesis). With every other row passing on both systems, the
    verdict is "inconclusive" for the 11 decided keys, because chua was not run (v3 section 7 and
    DEC-0016 O1: a missing system is not a pass; a plan-listed edit of this test, which read
    "supported"), with ``missing_systems == ["chua"]`` and the verdict strings in ``by_system``.
    Q-N (an estimate) carries the oracle interior reading and no pass/fail verdict, and the gain
    bound is "reported". A key present in one system only still raises ``KeyError`` (a missing
    result is not silently dropped). Exact.
    """
    config = dataclasses.replace(SMOKE, core_systems=("lorenz63", "rossler"))
    two = {"lorenz63": fake_system(config, skip=("H2e",)),
           "rossler": fake_system(config, skip=("H2e",))}
    out = verdicts({"systems": two}, config)
    assert "H2e" not in out and "V7" not in out
    assert list(out) == [h.key for h in HYPOTHESIS_TABLE if h.key != "H2e"]
    pass_fail = {key: v for key, v in out.items() if key not in ("Q-N", "gain_bound")}
    assert len(pass_fail) == 11
    assert {v["verdict"] for v in pass_fail.values()} == {"inconclusive"}
    assert all(v["by_system"] == {"lorenz63": "pass", "rossler": "pass"}
               and v["missing_systems"] == ["chua"] for v in pass_fail.values())
    assert out["gain_bound"] == {"by_system": {"lorenz63": "reported", "rossler": "reported"},
                                 "verdict": "reported (no pass/fail)"}
    # Q-N is an estimate (WU-0002.6(c)): the interior reading of the oracle profile, no pass/fail.
    assert out["Q-N"] == {"by_system": {"lorenz63": "reduces", "rossler": "reduces"},
                          "verdict": "estimate (read, no pass/fail)"}
    partial = {"lorenz63": fake_system(config), "rossler": fake_system(config, skip=("H2e",))}
    with pytest.raises(KeyError):
        verdicts({"systems": partial}, config)


def test_key_numbers_are_exact_for_every_v3_key() -> None:
    """``_key_number`` returns the formatted numbers of each result, keyed by the table key.

    Reference: hand formatting of the synthetic values of ``fake_system`` with the ``.3g`` rule of
    ``_fmt`` (``.2g`` where the report asks for two digits, ``.4g`` for A5/A4), worked out from
    the values, e.g. 100 * 0.05 = 5 so "5%". The H1a and H2b strings name ``n_lib``. Exact.
    H2e (WU-0002.7) has a number now, with a missing 2% value shown as ``n/a`` (a plan edit of this
    test). WU-0002.9 adds the intervals and verdicts of H1c, H2c and H2d (plan-listed edit, R5):
    for example 100 * -0.1 = -10 gives "-10%", and the H2d interval [0.04, 0.06] gives "[4, 6]%".
    """
    system = fake_system(SMOKE)
    expected = {
        "H1a": "rho=0.01: 1/d (n_lib fit)=0.5, ratio 1.02 [0.9, 1.1] pass (1/d_LB=0.5)",
        "H1b": "CP 1, PLP 0.9 [0.85, 0.95]: pass",
        "H1c": "PLP 1 [0.95, 1.05]: pass; CP 0.5 [0.4, 0.6] (reported, no verdict)",
        "H1d": "eps 0.8, delta 0.9, Lambda 0.7, N 0.6: pass",
        "Q-N": "oracle: interior reduces (dR2 0.01 [0, 0.02]), w*=0 distinct but small "
               "(dR2 0.02 [0.01, 0.03]), log T dR2 0.02 [0.01, 0.03]; deployable interior "
               "undetermined, w*=0 substantial (w*=0: 30, w*=1: 4)",
        "H2a": "(i) pass: range 0.05 (CI hi 0.08, n=120); (ii) pass: partial r zero 0.02 "
               "[-0.05, 0.08], interior -0.03 [-0.09, 0.04] (w*=0: 30, w*=1: 4)",
        "H2b": "rho rank corr 0.9; n_lib 10^3->10^4 change 0.2 [0.1, 0.3]: pass",
        "H2c": "A4-A2 -0.15 [-0.2, -0.05] (-10%) pass; A4-A1 -0.05 [-0.1, -0.01] (-5%) pass; "
               "A4o-A2 -20% (reported): pass",
        "H2d": "A4/A3-1 = 5% [4, 6]%: pass",
        "H2e": "rho=0.01: median change 0.1 [0.05, 0.15]; rho=0.02: median change n/a n/a: pass",
        "gain_bound": "within bound 0.95 (n=40 of 100; screened out: growth<=0 3, censored 5, "
                      "covariance<0 52, max gain 1.5 LT)",
        "H3a": "K=3: largest Holm p 0.004, IQR 0.4 LT: pass",
        "H3b": "Lambda imp: weight 0.1 [0, 0.15], D 0.6 [0.3, 0.8], stability 0.97: pass",
        "H3c": "A5/A4 1.012 [0.99, 1.04]: pass",
    }
    assert {key: _key_number(key, system) for key in expected} == expected
    assert set(expected) == {h.key for h in HYPOTHESIS_TABLE}


def test_key_numbers_of_h1a_h1b_h1d_show_fail_and_inconclusive_with_the_reason() -> None:
    """The H1 key numbers carry the three-valued verdict, and the reason when inconclusive (R1).

    Reference: v3 section 7 (pass, fail and inconclusive are separate categories) and the
    strings of the developer's review fix R1, written out by hand with the ``.3g`` rule of
    ``_fmt``. An inconclusive row must not read as a fail: the H1b string for the smoke's
    PLP slope 0.801 [0.744, 0.95] says "inconclusive (interval meets band edge)", an H1d with a
    failing row says "fail", and an H1a rho with fewer than 50 states says "n_states < 50".
    Exact string checks.
    """
    system = fake_system(SMOKE)
    system["H1b"] = {"CP": {"slope": 1.51}, "PLP": {"slope": 0.801, "ci": [0.744, 0.95]},
                     "verdict": "inconclusive", "reason": "interval meets band edge"}
    system["H1d"] = dict(system["H1d"], verdict="fail", reason=None)
    system["H1a"] = {"by_noise": {"0.01": {"fitted_inverse_dim": 0.5, "ratio": 1.0,
                                           "ratio_ci": [0.9, 1.1], "verdict": "inconclusive",
                                           "reason": "n_states < 50"}},
                     "inverse_dim_reference": 0.5}
    assert _key_number("H1b", system) == \
        "CP 1.51, PLP 0.801 [0.744, 0.95]: inconclusive (interval meets band edge)"
    assert _key_number("H1d", system) == "eps 0.8, delta 0.9, Lambda 0.7, N 0.6: fail"
    assert _key_number("H1a", system) == ("rho=0.01: 1/d (n_lib fit)=0.5, ratio 1 [0.9, 1.1] "
                                          "inconclusive (n_states < 50) (1/d_LB=0.5)")


def test_key_numbers_of_wu_0002_7_8_rows_show_the_verdict_and_the_reason() -> None:
    """The H2b, H2e, H3a, H3b and H3c key numbers end with the verdict, and the reason if inconclusive.

    Reference: hand strings with the ``_fmt`` rules, as in the H1 test above (DEC-0012 contract
    `verdict` and `reason`, review R1): an inconclusive result must read as such, not as a fail.
    Exact string checks.
    """
    system = fake_system(SMOKE)
    system["H3b"] = dict(system["H3b"], verdict="inconclusive", reason="D: interval meets band edge")
    system["H3a"] = dict(system["H3a"], verdict="inconclusive", reason="n_states < 50")
    system["H2b"] = dict(system["H2b"], verdict="fail", reason=None)
    assert _key_number("H3b", system) == ("Lambda imp: weight 0.1 [0, 0.15], D 0.6 [0.3, 0.8], "
                                          "stability 0.97: inconclusive (D: interval meets band "
                                          "edge)")
    assert _key_number("H3a", system) == \
        "K=3: largest Holm p 0.004, IQR 0.4 LT: inconclusive (n_states < 50)"
    assert _key_number("H2b", system).endswith("[0.1, 0.3]: fail")


def test_library_figure_axis_reads_n_lib(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The library-size figure's x-label is "Library size n_lib" and the regime figure is drawn.

    Reference: the WU-0002.2 acceptance (every figure axis for library size reads ``n_lib``). The
    figures are kept open by replacing ``plt.close`` for the call (restored by ``monkeypatch``),
    then read through matplotlib's ``get_xlabel``. The regret-vs-K figure reads ``regime_curve``,
    so it exists and is labelled "Number of regimes K". Exact string checks.
    """
    real_close = plt.close
    monkeypatch.setattr(report.plt, "close", lambda fig=None: None)
    results, config = fake_results("DEV-0")
    results["systems"] = {"lorenz63": fake_system(config)}
    try:
        written = make_figures(results, config, tmp_path)
        labels = [fig.axes[0].get_xlabel() for fig in map(plt.figure, plt.get_fignums())]
    finally:
        real_close("all")
    assert [path.name for path in written] == [
        "separation_weight_vs_horizon.png", "kaplan_meier_by_rule.png",
        "regret_vs_regimes.png", "knob_response_library.png"]
    assert labels[2] == "Number of regimes K" and labels[3] == "Library size n_lib"


def test_verdicts_refuse_a_results_file_older_than_the_v3_identifiers() -> None:
    """A system with v1 keys (H1e, H1f, H3d) makes ``verdicts`` raise before any flag is read.

    Reference: the decision-log correction table (v1 keys H1e, H1f and H3d no longer exist; the
    same keys H1a to H1d, H3b and H3c now mean other statistics, so relabelling would be a
    silent mislabel). The synthetic stale system is a current one plus the v1 keys. A current
    system passes. Exact: the exception type and the key names in the message.
    """
    config = SMOKE
    stale = fake_system(config)
    stale.update({"H1e": {"pass": True}, "H1f": {"pass": True}, "H3d": {"pass": True}})
    with pytest.raises(ValueError, match="H1e.*H1f.*H3d|schema older than WU-0002.2"):
        verdicts({"systems": {"lorenz63": stale}}, config)
    assert len(verdicts({"systems": {"lorenz63": fake_system(config)}}, config)) == 14


def test_markdown_validation_table_has_the_two_v7_rows(tmp_path: Path) -> None:
    """The validation table lists V7 (efficiency at every rho; slope) with PASS/FAIL, or n/a.

    Reference: the WU-0002.10 plan (item 5, test x), hand strings from the synthetic V7 dicts
    with the ``.3g`` rule of ``_fmt``. System A passes everywhere (efficiencies 0.95 and 1.04,
    slope 1.05); B fails one level (0.9 to 1.3) and the slope (1.2); C has no V7 result and must
    render "n/a" without raising. The rows read the flags in the dict, not the numbers. Exact.
    """
    # WU-0002.9 plan-listed edit (R4): the config is a pilot one, because at the smoke preset the V7
    # row names carry the plumbing label (tested in test_markdown_labels_v7_as_plumbing_at_smoke).
    config = dataclasses.replace(SMOKE, name="pilot", core_systems=("lorenz63", "rossler", "chua"))
    results, _ = fake_results("DEV-0")
    systems = {name: fake_system(config) for name in config.core_systems}
    systems["lorenz63"]["V7"] = {
        "median_slope": 1.05, "slope_pass": True, "pass": True,
        "efficiency_median_by_noise": {"0.01": 0.95, "0.02": 1.04},
        "efficiency_pass_by_noise": {"0.01": True, "0.02": True}}
    systems["rossler"]["V7"] = {
        "median_slope": 1.2, "slope_pass": False, "pass": False,
        "efficiency_median_by_noise": {"0.01": 0.9, "0.02": 1.3},
        "efficiency_pass_by_noise": {"0.01": True, "0.02": False}}
    results["systems"] = systems
    results["verdicts"] = verdicts(results, config)
    write_markdown(results, config, tmp_path / "RESULTS.md")
    lines = (tmp_path / "RESULTS.md").read_text().splitlines()
    table = lines[lines.index("## Validation gate"):]
    assert "| V7 median δ/(ρν), every ρ | [0.9, 1.1] | 0.95–1.04 PASS | 0.9–1.3 FAIL | n/a |" \
        in table
    assert "| V7 median slope of ln δ on ln ρ | [0.9, 1.1] | 1.05 PASS | 1.2 FAIL | n/a |" in table
    names = [row.split(" | ")[0][2:6] for row in table if row.startswith("| V")]
    assert names == ["V1 d", "V1 a", "V2 l", "V3 C", "V4 w", "V5 K", "V6 R", "V7 m", "V7 m"]


def test_markdown_lyapunov_section_has_comparisons_convention_and_referent(tmp_path: Path) -> None:
    """The validation section compares lambda_max with published values and states two sentences.

    Reference: hand strings (WU-0007.3 plan and amendment A6). Fake lambda_max: lorenz63 0.9
    gives 0.9 / 0.90563 - 1 = -0.00622, "-0.62%", inside 1% (PASS). rossler 0.08 gives
    0.08 / 0.0714 - 1 = +0.12045, "+12.04%", and 0.08 / 0.07062 - 1 = +0.13282, "+13.28%", both
    outside 3% (FAIL, with the LPC.NV.1 phrase). chua 0.43 has no reference: the limitation text,
    no difference. The memo row names the unit test and says the set is a different one. The
    LPC.NV.1 convention and the NVVUQ.13 referent sentences are checked verbatim, as is the
    report-only sentence. A lorenz63 result without ``context`` gives "n/a" cells, not a skipped
    row (PRIME.4). Tolerance: none (exact strings; the percentages are rounded to 2 decimals by
    ``:+.2f``; the hand values 12.0448 and 13.2822 are far from float round-off, 1e-12).
    """
    config = dataclasses.replace(SMOKE, core_systems=("lorenz63", "rossler", "chua"))
    results, _ = fake_results("DEV-0")
    values = {"lorenz63": 0.9, "rossler": 0.08, "chua": 0.43}
    systems = {name: fake_system(config) for name in config.core_systems}
    for name, value in values.items():
        systems[name]["context"] = {"lambda_max": value}
    results["systems"] = systems
    results["verdicts"] = verdicts(results, config)
    write_markdown(results, config, tmp_path / "RESULTS.md")
    lines = (tmp_path / "RESULTS.md").read_text().splitlines()
    start = lines.index("### Largest Lyapunov exponent against published values")
    assert start > lines.index("## Validation gate")
    section = lines[start:]
    assert "| lorenz63 | 0.9 | 0.9056 | Sprott, sprott.physics.wisc.edu/chaos/lespec.htm " \
        "(confirmed) | -0.62% | PASS: within 1% |" in section
    assert "| rossler | 0.08 | 0.0714 | Sprott as cited by Bogdanov and Bogdanova, " \
        "arXiv:1412.2242 (secondary) | +12.04% | FAIL: outside 3%; step size suspected " \
        "(LPC.NV.1), reported, not tuned |" in section
    assert "| rossler | 0.08 | 0.07062 | Bogdanov and Bogdanova, arXiv:1412.2242, own estimate " \
        "0.07062 ± 0.00066 (primary) | +13.28% | FAIL: outside 3%; step size suspected " \
        "(LPC.NV.1), reported, not tuned |" in section
    assert "| chua | 0.43 | none | no confirmed published value | n/a | not validated: no " \
        "published reference at these parameters (known limitation, NVVUQ.13, DEC-0010) |" \
        in section
    memo = next(row for row in section if row.startswith("| chua, memo parameter set"))
    assert "| 0.3286 |" in memo and "within 10% is asserted by `tests/unit/test_data.py::" \
        "test_lyapunov_cached_matches_published_reference[chua_memo]`" in memo
    assert "a different parameter set from the study's: validates the routine and the field " \
        "form, not the study's Chua parameters |" in memo
    assert ("Every quantity is defined for the fixed-step RK4 flow map at the configured "
            "observation interval, not for the continuous ODE (LPC.NV.1). λ_max is estimated "
            "on that map by Benettin's method and compared in natural time units with "
            "published values for the continuous systems.") in section
    assert ("Validation against a real-world referent does not apply: the three systems are "
            "mathematical models (NVVUQ.13).") in section
    assert ("Chua at the study's own parameters (α=15.6, β=28, m0=−1.143, m1=−0.714) has no "
            "confirmed published value (known limitation, NVVUQ.13, DEC-0010): its λ_max is "
            "reported but not validated.") in section
    assert ("This comparison is report-only: it does not enter the validation gate or any "
            "verdict.") in section

    bare_config = dataclasses.replace(SMOKE, core_systems=("lorenz63",))
    bare, _ = fake_results("DEV-0")
    bare["systems"] = {"lorenz63": fake_system(bare_config)}
    bare["verdicts"] = verdicts(bare, bare_config)
    write_markdown(bare, bare_config, tmp_path / "BARE.md")
    rows = (tmp_path / "BARE.md").read_text().splitlines()
    assert "| lorenz63 | n/a | 0.9056 | Sprott, sprott.physics.wisc.edu/chaos/lespec.htm " \
        "(confirmed) | n/a | n/a: no λ_max in the results |" in rows


# ----------------------------------------------------- WU-0002.9: verdict strings and overall rule
THREE = ("lorenz63", "rossler", "chua")
INTRO_TEXT = ("Generated by `python -m lpcstudy`. Each criterion is decided per system by its "
              "interval against the pre-registered band of the proposal (v3 §2): pass, fail or "
              "inconclusive. A hypothesis is *supported* if it passes on all three systems, *not "
              "supported* if it fails on at least one, and *inconclusive* otherwise; a system "
              "that was not run counts as inconclusive (v3 §7). A validation-gate FAIL marks "
              "that system's results provisional (v3 §6 E0); it does not change the verdicts.")
V7_LABEL = " (smoke: plumbing-size numbers, judged at pilot size; DEC-0015)"
SMOKE_NOTE = ("Note: at the smoke preset a gate FAIL is expected. V7 is a plumbing check there, "
              "judged at pilot size and above (DEC-0015).")


def _three_systems(config: StudyConfig, h2a: tuple[str, str, str]) -> dict:
    """Results of three systems whose H2a verdicts are ``h2a`` (all other rows pass)."""
    systems = {name: fake_system(config) for name in THREE}
    for name, verdict in zip(THREE, h2a):
        systems[name]["H2a"] = dict(systems[name]["H2a"], verdict=verdict, reason=None)
    return {"systems": systems}


def test_verdicts_overall_rule_over_the_three_v3_systems() -> None:
    """``verdicts`` returns the verdict strings per system and the v3 section 7 overall rule.

    Reference (plan R1): v3 section 7, "supported: pass on all three systems; not supported: fail
    on at least one; inconclusive: otherwise", and DEC-0016 O1, as a hand table over H2a verdicts
    of three systems: (pass, pass, pass) supported; any fail not supported, with the rest passing
    or inconclusive; all inconclusive, or two pass and one inconclusive, inconclusive and never
    "not supported". ``missing_systems`` is empty for three systems. With the smoke config
    (``core_systems == ("lorenz63",)``) a lone pass reads inconclusive with
    ``missing_systems == ["rossler", "chua"]`` (``required`` is the constant of the three v3
    systems, not the config), and a lone fail reads not supported. A system outside the three
    raises; a decided row with ``pass`` and no ``verdict``, or an unknown verdict, raises (stale
    schema; R3). Exact.
    """
    config = dataclasses.replace(SMOKE, name="pilot", core_systems=THREE)
    table = [(("pass", "pass", "pass"), "supported"),
             (("pass", "fail", "pass"), "not supported"),
             (("fail", "inconclusive", "pass"), "not supported"),
             (("inconclusive", "inconclusive", "inconclusive"), "inconclusive"),
             (("pass", "pass", "inconclusive"), "inconclusive"),
             (("pass", "inconclusive", "fail"), "not supported")]
    for flags, want in table:
        out = verdicts(_three_systems(config, flags), config)["H2a"]
        assert out == {"by_system": dict(zip(THREE, flags)), "verdict": want,
                       "missing_systems": []}, flags
    lone = lambda verdict: {"systems": {"lorenz63": dict(
        fake_system(SMOKE), H2a=dict(fake_system(SMOKE)["H2a"], verdict=verdict))}}
    assert SMOKE.core_systems == ("lorenz63",)
    assert verdicts(lone("pass"), SMOKE)["H2a"] == {
        "by_system": {"lorenz63": "pass"}, "verdict": "inconclusive",
        "missing_systems": ["rossler", "chua"]}
    assert verdicts(lone("fail"), SMOKE)["H2a"]["verdict"] == "not supported"
    assert verdicts(lone("inconclusive"), SMOKE)["H2a"]["verdict"] == "inconclusive"

    odd = dataclasses.replace(SMOKE, core_systems=("lorenz96",))
    with pytest.raises(ValueError, match="lorenz96"):
        verdicts({"systems": {"lorenz96": fake_system(odd)}}, odd)
    old = fake_system(SMOKE)
    old["H2a"] = {"pass": True}
    with pytest.raises(ValueError, match="no verdict.*WU-0002.9"):
        verdicts({"systems": {"lorenz63": old}}, SMOKE)
    old["H2a"] = {"pass": True, "verdict": "maybe"}
    with pytest.raises(ValueError, match="no verdict"):
        verdicts({"systems": {"lorenz63": old}}, SMOKE)


def test_markdown_flags_inconclusive_rows_and_leaves_the_gain_bound_without_a_flag(
        tmp_path: Path) -> None:
    """The flag column reads PASS, FAIL or INCONCLUSIVE; the gain bound has none; the intro is exact.

    Reference (plan R2): hand strings. With H2a inconclusive on all three systems the row has
    three "INCONCLUSIVE" cells, no "FAIL", no "not supported" and ends "| inconclusive |"; with
    one fail (and the rest passing) it has one "FAIL" and ends "| not supported |". With only
    two systems run, the overall cell names the missing one: "inconclusive (missing: chua)". The
    gain-bound row has no PASS, FAIL or INCONCLUSIVE and ends "| reported (no pass/fail) |". Q-N
    keeps "| estimate (read, no pass/fail) |". The intro sentence equals the hand string
    ``INTRO_TEXT`` exactly, and the old wording ("§M9", "partially supported") is gone. Exact.
    """
    config = dataclasses.replace(SMOKE, name="pilot", core_systems=THREE)

    def rows_of(results: dict) -> tuple[dict[str, str], list[str]]:
        results = dict(results, config={}, verdicts=None)
        results["verdicts"] = verdicts(results, config)
        results["provenance"] = None
        write_markdown(results, config, tmp_path / "R.md")
        lines = (tmp_path / "R.md").read_text().splitlines()
        start = lines.index("## Hypothesis verdicts")
        table = [ln for ln in lines[start:] if ln.startswith("| ") and "---" not in ln][1:15]
        return {row.split(" | ")[0][2:]: row for row in table}, lines

    rows, lines = rows_of(_three_systems(config, ("inconclusive",) * 3))
    h2a = rows["H2a"]
    assert h2a.count("INCONCLUSIVE") == 3 and "FAIL" not in h2a and "not supported" not in h2a
    assert h2a.endswith("| inconclusive |")
    assert INTRO_TEXT in lines and "§M9" not in "\n".join(lines)
    assert "partially supported" not in "\n".join(lines)
    gain = rows["(reported)"]
    assert not any(word in gain for word in ("PASS", "FAIL", "INCONCLUSIVE"))
    assert gain.endswith("| reported (no pass/fail) |")
    assert rows["Q-N"].endswith("| estimate (read, no pass/fail) |")
    rows, _ = rows_of(_three_systems(config, ("pass", "fail", "pass")))
    assert rows["H2a"].count("FAIL") == 1 and rows["H2a"].count("PASS") == 2
    assert rows["H2a"].endswith("| not supported |")
    assert rows["H1a"].endswith("| supported |")

    two = dataclasses.replace(config, core_systems=("lorenz63", "rossler"))
    results = {"config": {}, "provenance": None,
               "systems": {n: fake_system(two) for n in two.core_systems}}
    results["verdicts"] = verdicts(results, two)
    write_markdown(results, two, tmp_path / "TWO.md")
    row = next(ln for ln in (tmp_path / "TWO.md").read_text().splitlines()
               if ln.startswith("| H2a "))
    assert row.endswith("| inconclusive (missing: chua) |")


def test_markdown_labels_v7_as_plumbing_at_smoke_and_adds_the_gate_note(tmp_path: Path) -> None:
    """At the smoke preset the V7 rows carry the DEC-0015 label and a gate note follows the gate line.

    Reference (plan R4, DEC-0015): hand strings. The smoke config gives both V7 row names the
    label ``V7_LABEL`` and prints ``SMOKE_NOTE`` after the "Validation gate:" line; a pilot
    config gives neither. The V7 numbers and PASS/FAIL text are the same at both (the smoke row
    with the label removed equals the pilot row), the gate line still reads FAIL (results
    provisional) for a false ``gate_pass``, and the other validation rows are unchanged. Exact.
    """
    def render(name: str, gate_pass: bool) -> list[str]:
        config = dataclasses.replace(SMOKE, name=name, core_systems=("lorenz63",))
        system = fake_system(config)
        system["validation"]["gate"] = {"gate_pass": gate_pass}
        system["V7"] = {"median_slope": 1.2, "slope_pass": False, "pass": False,
                        "efficiency_median_by_noise": {"0.01": 0.9, "0.02": 1.3},
                        "efficiency_pass_by_noise": {"0.01": True, "0.02": False}}
        results = {"config": {}, "provenance": None, "systems": {"lorenz63": system}}
        results["verdicts"] = verdicts(results, config)
        write_markdown(results, config, tmp_path / f"{name}.md")
        return (tmp_path / f"{name}.md").read_text().splitlines()

    smoke, pilot = render("smoke", False), render("pilot", False)
    v7 = lambda lines: [ln for ln in lines if ln.startswith("| V7 ")]
    assert len(v7(smoke)) == 2 and all(V7_LABEL in ln for ln in v7(smoke))
    assert not any(V7_LABEL in ln for ln in v7(pilot))
    assert [ln.replace(V7_LABEL, "") for ln in v7(smoke)] == v7(pilot)
    assert "0.9–1.3 FAIL" in v7(pilot)[0] and "1.2 FAIL" in v7(pilot)[1]
    gate = smoke.index("Validation gate: lorenz63 FAIL (results provisional)")
    assert smoke[gate + 1:gate + 3] == ["", SMOKE_NOTE]
    assert SMOKE_NOTE not in pilot
    assert pilot[pilot.index("Validation gate: lorenz63 FAIL (results provisional)") + 1] == ""
    assert [ln for ln in smoke if ln.startswith("| V") and not ln.startswith("| V7 ")] == \
        [ln for ln in pilot if ln.startswith("| V") and not ln.startswith("| V7 ")]


def test_key_numbers_show_inconclusive_h1c_h2c_h2d_with_their_reasons() -> None:
    """The H1c, H2c and H2d key numbers carry the verdict and the reason; absent numbers read n/a.

    Reference (plan R5): hand strings with the ``.3g`` rule of ``_fmt``. An H1c PLP with fewer
    than 10 states has no median and no interval ("n/a n/a"), the reason names the 50-state
    minimum; an H2c with one inconclusive part and one fail shows each part's verdict, the failing
    whole, and no reason; an H2d inconclusive at the edge shows its reason in parentheses. Exact.
    """
    system = fake_system(SMOKE)
    system["H1c"] = {"PLP": {"median_ratio": None, "ci": None}, "CP": {"median_ratio": 1.6,
                                                                       "ci": [1.5, 1.7]},
                     "verdict": "inconclusive", "reason": "n_states < 50"}
    assert _key_number("H1c", system) == ("PLP n/a n/a: inconclusive (n_states < 50); "
                                          "CP 1.6 [1.5, 1.7] (reported, no verdict)")
    system["H2c"] = dict(system["H2c"], verdict="fail", reason=None)
    system["H2c"]["A4_minus_A2"] = dict(system["H2c"]["A4_minus_A2"], verdict="inconclusive",
                                        reason="interval meets band edge")
    system["H2c"]["A4_minus_A1"] = dict(system["H2c"]["A4_minus_A1"], verdict="fail", reason=None)
    assert _key_number("H2c", system) == (
        "A4-A2 -0.15 [-0.2, -0.05] (-10%) inconclusive (interval meets band edge); "
        "A4-A1 -0.05 [-0.1, -0.01] (-5%) fail; A4o-A2 -20% (reported): fail")
    # R3: a gain-bound result without the screen counts fails loudly (PRIME.4), not silently
    bare = {key: value for key, value in system["gain_bound"].items() if key != "n_screened_out"}
    with pytest.raises(KeyError, match="n_screened_out"):
        _key_number("gain_bound", dict(system, gain_bound=bare))
    system["H2d"] = dict(system["H2d"], verdict="inconclusive", reason="interval meets band edge")
    assert _key_number("H2d", system) == \
        "A4/A3-1 = 5% [4, 6]%: inconclusive (interval meets band edge)"


# ------------------------------------------------- WU-0005.5: Theorem P2(c) verification subsection
def _p2c_block(violations: int, chain: tuple[int, ...], spread: dict, same: bool | None) -> dict:
    """The fields of ``verification.P2c`` that the report reads (hand-planned values)."""
    return {"n_states": 1400, "n_violations": violations,
            "n_chain_violations": dict(zip(("N_le_A", "A_le_B", "p2a", "triangle", "consistency"),
                                           chain)),
            "n_switching_states": 1052, "n_zero_bound_states": 12,
            "tightness": {"N_over_sqrt_B": spread}, "same_draws_identical": same}


def test_markdown_p2c_section_is_labelled_report_only_and_shows_defects(tmp_path: Path) -> None:
    """The validation section has the P2(c) subsection: label, one row per system, defects bold.

    Reference: hand strings (WU-0005.5 plan, ``results.json`` and report paragraph). Lorenz has
    no violation and the draws match (``yes``); rossler has 3 violating states, a chain count per
    item, no state with B > 0 (median ``None`` gives "n/a") and a bitwise mismatch (``NO:
    DEFECT``); chua has no block and must show "n/a", not a skipped row (PRIME.4). The label
    sentence is verbatim from the plan. The numbers use the ``.3g`` rule of ``_fmt``. Exact
    strings, no tolerance.
    """
    config = dataclasses.replace(SMOKE, core_systems=("lorenz63", "rossler", "chua"))
    results, _ = fake_results("DEV-0")
    systems = {name: fake_system(config) for name in config.core_systems}
    systems["lorenz63"]["verification"] = {"P2c": _p2c_block(
        0, (0, 0, 0, 0, 0), {"n_states": 1388, "median": 0.1724, "p90": 0.3312, "max": 0.4611}, True)}
    systems["rossler"]["verification"] = {"P2c": _p2c_block(
        3, (1, 2, 0, 0, 1), {"n_states": 0, "median": None, "p90": None, "max": None}, False)}
    results["systems"] = systems
    results["verdicts"] = verdicts(results, config)
    write_markdown(results, config, tmp_path / "RESULTS.md")
    lines = (tmp_path / "RESULTS.md").read_text().splitlines()
    start = lines.index("### Theorem P2(c) bound (verification check, not a hypothesis)")
    assert start > lines.index("### Largest Lyapunov exponent against published values")
    section = lines[start:]
    assert "| lorenz63 | 1400 | 0 | 0, 0, 0, 0, 0 | 1052 | 12 | 0.172, 0.331, 0.461 | yes |" \
        in section
    assert "| rossler | 1400 | **3: DEFECT** | 1, 2, 0, 0, 1 | 1052 | 12 | n/a | **NO: DEFECT** |" \
        in section
    assert "| chua | n/a: no P2(c) result | | | | | | |" in section
    assert any(row.startswith("Verification check (NVVUQ.14, v3 Theorem P2(c)); not a hypothesis "
                              "test; no verdict; not in the validation gate.") for row in section)
    assert "P2c" not in "".join(lines[:lines.index("## Validation gate")])  # no verdict row
