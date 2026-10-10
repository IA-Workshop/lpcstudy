"""Report header and output files for a fake results dict (WU-0001.4; LPC.PC.13, LPC.PC.18).

The fake dict has ``systems: {}`` and a ``verdicts`` stub per hypothesis, so no study is run.
The confirmatory value below is synthetic (LPC.PC.7). Checks are exact string checks.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lpcstudy import provenance
from lpcstudy.config import SMOKE, StudyConfig
from lpcstudy.report import HYPOTHESES, header_lines, save_json, write_markdown
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
