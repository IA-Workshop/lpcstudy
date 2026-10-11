"""Tests for lpcstudy.identifiers: the identifier table and the v1 key map (WU-0002.2).

Every check is an exact comparison of strings, tuples or sets; there is no tolerance. The
references are the study documents, parsed here by code that shares nothing with the module:
``docs/study/decision_log_lpc.md`` (the "v3 ID | v2 ID | Role" map and the correction table) and
``docs/study/proposal_and_methods_v3.md`` (section 2 tables, section 7 primaries).
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from lpcstudy.identifiers import HYPOTHESIS_TABLE, V1_KEY_MAP, check_keys

ROOT = Path(__file__).resolve().parents[2]
DECISION_LOG = ROOT / "docs" / "study" / "decision_log_lpc.md"
PROPOSAL = ROOT / "docs" / "study" / "proposal_and_methods_v3.md"
PACKAGE = ROOT / "lpcstudy"


def unescape(text: str) -> str:
    """Remove Markdown escapes and bold markers from a table cell."""
    return re.sub(r"\\([\\`*_{}\[\]()#+\-.!|<>])", r"\1", text).replace("**", "").strip()


def table_rows(path: Path, header: str) -> list[list[str]]:
    """Cells of the Markdown table whose header line starts with ``header`` (separator skipped)."""
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(header))
    rows = []
    for line in lines[start + 2:]:
        if not line.startswith("|"):
            break
        rows.append([c.strip() for c in line.strip().strip("|").split(" | ")])
    return rows


def test_rows_equal_the_decision_log_map() -> None:
    """The 14 rows ``(v3_id, v2_id, role)`` equal the "v3 ID | v2 ID | Role" block, in order.

    Reference: the table in the decision log, parsed from the file. The log's role text for
    the gain bound is "gain bound, no pass/fail"; the table's role word for it is ``reported``
    (the ROADMAP row of WU-0002.2), the one mapping written out below.
    """
    parsed = [(v3, v2, "reported" if role.startswith("gain bound") else role)
              for v3, v2, role in table_rows(DECISION_LOG, "| v3 ID | v2 ID | Role |")]
    assert len(parsed) == 14
    assert [(h.v3_id, h.v2_id, h.role) for h in HYPOTHESIS_TABLE] == parsed
    assert len({h.key for h in HYPOTHESIS_TABLE}) == 14
    assert [h.key for h in HYPOTHESIS_TABLE if h.key != h.v3_id] == ["gain_bound"]


def test_v1_key_map_equals_the_correction_table() -> None:
    """``V1_KEY_MAP`` equals a hand transcription of the decision log's correction table.

    Reference: "v1 / code | v3" table of the log's 10 October correction (lines 78 to 94),
    transcribed here by hand: H1a became V7, H1b to H1f shift down by one (H1f is Q-N), H2a to
    H2d are kept, the v1 gain bound H2e is "reported" (key ``gain_bound``), H3b and T1 are
    dropped, v1 H3c becomes H3b and v1 H3d becomes H3c. The row "-- | H2e (noise matching)" has no
    v1 key. The check also reads the log to make sure the transcribed v1 column is its v1 column.
    """
    transcription = {"H1a": "V7", "H1b": "H1a", "H1c": "H1b", "H1d": "H1c", "H1e": "H1d",
                     "H1f": "Q-N", "H2a": "H2a", "H2b": "H2b", "H2c": "H2c", "H2d": "H2d",
                     "H2e": "gain_bound", "H3a": "H3a", "H3b": None, "H3c": "H3b",
                     "H3d": "H3c", "T1": None}
    assert V1_KEY_MAP == transcription
    log_rows = table_rows(DECISION_LOG, "| v1 / code | v3 |")
    v1_ids = [i for row in log_rows if not row[0].startswith("—")
              for i in re.findall(r"\b(?:H\d[a-f]|T1)\b", row[0])]
    assert sorted(v1_ids) == sorted(transcription)
    assert len(v1_ids) == len(set(v1_ids)) == 16


def test_criterion_text_is_the_v3_section_2_row() -> None:
    """Each ``criterion`` is ``"<statistic>; pass if <rule>"`` of its v3 section 2 row.

    Reference: the hypothesis tables of section 2 of the proposal and methods v3, parsed from
    the file (columns ID, Hypothesis, Statistic, Pass if; the markers ``**`` and the Markdown
    escapes removed; ``Q-N (estimate)`` is the id ``Q-N``). For the gain bound the reference is
    the sentence after the RQ3 table.
    """
    text = PROPOSAL.read_text(encoding="utf-8")
    section = text[text.index("## 2. Research questions"):text.index("## 3. Mathematical")]
    expected = {}
    for line in section.splitlines():
        if line.startswith("|") and not line.startswith(("| ID", "| ---")):
            ident, _, statistic, rule = [unescape(c) for c in line.strip().strip("|").split(" | ")]
            expected[ident.replace(" (estimate)", "")] = f"{statistic}; pass if {rule}"
    (sentence,) = [line for line in section.splitlines() if line.startswith("The hybrid's")]
    expected["(reported)"] = unescape(sentence)
    assert len(expected) == 14
    assert {h.v3_id: h.criterion for h in HYPOTHESIS_TABLE} == expected


def test_primaries_and_roles() -> None:
    """The primaries are H2a, H2b and H3c; the roles are the four allowed words.

    Reference: v3 section 7 (the three primary endpoints are H2a, H2b and H3c, at level
    1 - 0.05/3) and the ROADMAP row of WU-0002.2 (roles primary, secondary, estimate, reported),
    written out here.
    """
    assert {h.v3_id for h in HYPOTHESIS_TABLE if h.role == "primary"} == {"H2a", "H2b", "H3c"}
    assert {h.role for h in HYPOTHESIS_TABLE} <= {"primary", "secondary", "estimate", "reported"}
    assert [h.v3_id for h in HYPOTHESIS_TABLE if h.role in ("estimate", "reported")] == \
        ["Q-N", "(reported)"]


def test_pending_names_the_roadmap_rows() -> None:
    """``pending`` is the list of ROADMAP sub-tasks whose row names the id.

    Reference: ROADMAP rows WU-0002.4 to .8, read by hand: .4 names H1a and H1b; .5 H1d; .6 Q-N
    (done in WU-0002.6(c), so its pending is empty); .7 H2b and H2e; .8 H3a, H3c and H2d. No
    other row of .3 to .13 names a table id, so the other
    rows have no pending sub-task, with one exception added in the fix round (review R1): the
    gain bound keeps its v1 0.9 pass bar although v3 says "without a pass/fail bar", and the
    concordance (D-21 (a)) proposes removing it in WU-0002.9, so that row is pending on .9.
    WU-0002.4-5 phase 2 removes each id from ``pending`` in the commit that implements its
    statistic (H1a, H1b, H1d); the rows still pending are those of the remaining sub-tasks.
    """
    expected = {"H2b": ("WU-0002.7",), "H2e": ("WU-0002.7",),
                "H2d": ("WU-0002.8",), "H3a": ("WU-0002.8",), "H3c": ("WU-0002.8",),
                "(reported)": ("WU-0002.9",)}
    assert {h.v3_id: h.pending for h in HYPOTHESIS_TABLE if h.pending} == expected


def test_no_stale_identifier_in_the_package() -> None:
    """No module but ``identifiers`` holds a v1 or v2 id as a name or a string constant.

    Reference: the ROADMAP grep of WU-0002.2 (``H1e|H1f|H2f|H3d|T1``, ``h1e_|h1f_``), done on the
    syntax tree (names, attributes, function and argument names, string constants including
    docstrings). Every string constant that is exactly an identifier (``H1a`` ... ``Q-N``, ``T1``)
    must be a ``key`` of the table.
    """
    keys = {h.key for h in HYPOTHESIS_TABLE}
    stale = re.compile(r"H1e|H1f|H2f|H3d|T1|h1e_|h1f_")
    exact = re.compile(r"^(H\d[a-f]|Q-N|T1)$")
    found = []
    for path in sorted(PACKAGE.glob("*.py")):
        if path.name == "identifiers.py":
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            names = []
            if isinstance(node, ast.Name):
                names.append(node.id)
            elif isinstance(node, ast.Attribute):
                names.append(node.attr)
            elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                names.append(node.name)
            elif isinstance(node, ast.arg):
                names.append(node.arg)
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                names.append(node.value)
                if exact.match(node.value) and node.value not in keys:
                    found.append((path.name, "not a table key", node.value))
            found += [(path.name, "stale", n[:60]) for n in names if stale.search(n)]
    assert found == []


def test_check_keys_accepts_table_keys_and_refuses_stale_ids() -> None:
    """``check_keys`` passes the 14 table keys, V7 and ordinary keys; it raises on v1/v2 ids.

    Reference: the decision-log map. The ids that left the code are the v1/v2 ids that are not
    v3 keys: H1e, H1f, H2f, H3d, T1 (and a made-up H9f of the same shape). Exact: ``ValueError`` naming the keys.
    """
    fine = {h.key: 1 for h in HYPOTHESIS_TABLE} | {"V7": 1, "scores": 2, "H2a_median_range": 3}
    check_keys(fine)
    for stale in ("H1e", "H1f", "H2f", "H3d", "T1", "H9f"):
        with pytest.raises(ValueError, match=stale):
            check_keys({"H1a": 1, stale: 2})
