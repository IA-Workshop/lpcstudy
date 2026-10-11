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

    Every table key has a result with ``pass`` true and the sub-keys ``_key_number`` reads,
    except the keys in ``skip``. The numbers are arbitrary small values chosen by hand.
    """
    hours = ["0.25", "0.5", "1", "2", "4"]
    results = {
        "H1a": {"by_noise": {"0.01": {"fitted_inverse_dim": 0.5}}, "local_dimension_median": 2.0},
        "H1b": {"CP": {"slope": 1.0}, "PLP": {"slope": 0.9}},
        "H1c": {"PLP": {"median_ratio": 1.0}, "CP": {"median_ratio": 0.5}},
        "H1d": {"spearman": {"analog_seed": 0.8, "estimation_seed": 0.9, "growth": 0.7,
                             "noise_sensitivity": 0.6}},
        "Q-N": {"deployable": {"verdict": "redundant", "logit_w": {"delta_r2": 0.01,
                                                                    "ci": [0.0, 0.02]},
                               "log_horizon": {"delta_r2": 0.02, "ci": [0.01, 0.03]}},
                "oracle": {"verdict": "adds information"}},
        "H2a": {"median_range": 0.05, "range_ci": [0.01, 0.08], "partial_corr": 0.02},
        "H2b": {"noise": {"mean_state_spearman": 0.9},
                "library": {"0.01": {"median_at_largest_n_lib": 0.8,
                                         "median_w_by_n_lib": {"1000": 0.7, "10000": 0.8}}}},
        "H2c": {"A4_minus_A2": {"relative": -0.1}, "best_single": "A1",
                "A4_minus_A1": {"relative": -0.05}},
        "H2d": {"in_distribution_excess": 0.05},
        "H2e": {"median_change": 0.1},
        "gain_bound": {"fraction_within_bound": 0.95, "n_states": 40, "max_gain_lyapunov": 1.5},
        "H3a": {"chosen_K": 3, "regret_ratio": 0.04, "mean_iqr_lyapunov": 0.4},
        "H3b": {"weight_tree_importance": {"lambda_tilde": 0.1},
                "horizon_tree_importance": {"lambda_tilde": 0.6}},
        "H3c": {"A5_over_A4_mse": 1.0123},
    }
    system = {key: dict(value, **{"pass": True}) for key, value in results.items()
              if key not in skip}
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
    the ROADMAP pending sub-tasks, written out below. The fake results have no ``H2e``, so that
    row reads "[not computed until WU-0002.7]", its cell "n/a: no result" and its verdict
    "no result"; the rows with a result and a pending sub-task read "computed with the v1
    statistic". Exact string checks.
    """
    results, config = fake_results("DEV-0")
    system = fake_system(config, skip=("H2e",))
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
    assert {i for i, m in marked.items() if m} == {"H1a", "H1b", "H1d", "Q-N", "H2b", "H2d",
                                                   "H3a", "H3c", "(reported)"}
    h2e = rows[ids.index("H2e")]
    assert h2e.endswith("[not computed until WU-0002.7] | n/a: no result | no result |")
    gain = rows[ids.index("(reported)")]
    assert "within bound 0.95 (n=40, max gain 1.5 LT)" in gain and "PASS" in gain


def test_verdicts_skip_a_row_without_results_and_raise_on_a_partial_one() -> None:
    """``verdicts`` has no entry (and no ``KeyError``) for a key absent in every system.

    Reference: the plan for WU-0002.2 (v3 H2e has no result until WU-0002.7, so it is skipped,
    not an error; V7 is not a hypothesis). With every other row true on every system, the
    verdict is "supported" for the other 13 keys. A key present in one system only still raises
    ``KeyError`` (a missing result is not silently dropped). Exact.
    """
    config = dataclasses.replace(SMOKE, core_systems=("lorenz63", "rossler"))
    two = {"lorenz63": fake_system(config, skip=("H2e",)),
           "rossler": fake_system(config, skip=("H2e",))}
    out = verdicts({"systems": two}, config)
    assert "H2e" not in out and "V7" not in out
    assert list(out) == [h.key for h in HYPOTHESIS_TABLE if h.key != "H2e"]
    assert {v["verdict"] for v in out.values()} == {"supported"}
    assert all(v["by_system"] == {"lorenz63": True, "rossler": True} for v in out.values())
    partial = {"lorenz63": fake_system(config), "rossler": fake_system(config, skip=("H2e",))}
    with pytest.raises(KeyError):
        verdicts({"systems": partial}, config)


def test_key_numbers_are_exact_for_every_v3_key() -> None:
    """``_key_number`` returns the formatted numbers of each result, keyed by the table key.

    Reference: hand formatting of the synthetic values of ``fake_system`` with the ``.3g`` rule of
    ``_fmt`` (``.2g`` where the report asks for two digits, ``.4g`` for A5/A4), worked out from
    the values, e.g. 100 * 0.05 = 5 so "5%". The H1a and H2b strings name ``n_lib``. Exact.
    The v3 H2e has no number yet (it is not computed), so it is not in the table below.
    """
    system = fake_system(SMOKE)
    expected = {
        "H1a": "rho=0.01: 1/d (n_lib fit)=0.5 (1/d_LB=0.5)",
        "H1b": "CP 1, PLP 0.9",
        "H1c": "PLP 1, CP 0.5",
        "H1d": "eps 0.8, delta 0.9, Lambda 0.7, N 0.6",
        "Q-N": "redundant: dR2 w 0.01 [0, 0.02], T 0.02 [0.01, 0.03]; oracle: adds information",
        "H2a": "range 0.05 (CI hi 0.08); partial r 0.02",
        "H2b": "rho rank corr 0.9; n_lib@0.01: w*(n_lib max)=0.8",
        "H2c": "A4-A2 -10%; A4-A1 -5%",
        "H2d": "A4/A3-1 = 5%",
        "gain_bound": "within bound 0.95 (n=40, max gain 1.5 LT)",
        "H3a": "K=3: regret 4%, IQR 0.4 LT",
        "H3b": "Lambda imp: weight 0.1, horizon 0.6",
        "H3c": "A5/A4 1.012",
    }
    assert {key: _key_number(key, system) for key in expected} == expected
    assert set(expected) == {h.key for h in HYPOTHESIS_TABLE} - {"H2e"}


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
    config = dataclasses.replace(SMOKE, core_systems=("lorenz63", "rossler", "chua"))
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
