"""Tests of ``tools/rehearsal_common.py`` (WU-0003.10; plan amendment 7, G4, acceptance h1 and h3).

DEVELOPMENT code; needs owner review before freeze (statistics code). The module holds what
``tools/rehearsal_report.py`` and ``tools/rehearsal_diagnostics.py`` had in common, moved without a
change of behaviour:

* h1: ``test_regression_*`` compares the complete outputs of both tools (text, ``--json``, exit code,
  stderr) with the golden files recorded before the move (``fixtures/golden_rehearsal/``, README).
  That is a **regression guard** (the tool against its own earlier output), not evidence of
  correctness.
* h3: the other tests are specifications of the shared functions with references written here by
  hand (truth tables, literal strings, a raw traceback walk), independent of the code under test.

Not moved, so not tested here: ``block_variance`` and the influence-series builders, which differ in
substance between the two tools (unit Log, WU-0003.10); their tests stay in the two tool test files.
All tests are CPU, under 5 s, and use no random number.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

import numpy as np
import pytest

import golden_rehearsal as golden

rr = golden.trep.rr
rd = golden.tdiag.rd
common = rr.common
ROOT = Path(__file__).resolve().parents[2]


# ------------------------------------------------------------------------------------------ h1
@pytest.fixture(scope="module")
def produced() -> dict[str, str]:
    """The outputs of every golden case, from the code under test (one pass for the module)."""
    return golden.produce()


def test_regression_the_golden_folder_and_the_cases_name_the_same_files(produced) -> None:
    """Regression guard: no case is missing or left over (so no golden file goes unchecked)."""
    on_disk = sorted(p.name for p in golden.GOLDEN.iterdir() if p.name != "README.md")
    assert sorted(produced) == on_disk
    assert all((name + ".txt") in on_disk for name in sorted({n.split(".")[0] for n in on_disk}))


def test_regression_golden_outputs_are_byte_identical(produced) -> None:
    """h1: after the move, every report, JSON file, exit code and stderr is byte-identical.

    Regression guard, not correctness evidence. A failure names the first differing file and line;
    the golden files are never rewritten to pass (README).
    """
    for name, text in sorted(produced.items()):
        want = (golden.GOLDEN / name).read_text()
        if text != want:
            got_lines, want_lines = text.splitlines(), want.splitlines()
            first = next((i for i, (a, b) in enumerate(zip(got_lines, want_lines, strict=False))
                          if a != b), min(len(got_lines), len(want_lines)))
            pytest.fail(f"{name} differs at line {first + 1}: got "
                        f"{got_lines[first:first + 1]!r}, golden {want_lines[first:first + 1]!r}")


# ------------------------------------------------------------------------------------------ sharing
def test_both_tools_use_one_definition_of_each_shared_name() -> None:
    """One class and one function each: the tools' names are the module's objects, and the
    diagnostics' ``Report`` extends the shared one with its three own records and nothing else."""
    assert rr.common is rd.common and common.__name__ == "rehearsal_common"
    for name in ("NotComputable", "Missing", "Refused", "attempt", "Dump", "dig", "fmt", "is_dev_id",
                 "run_seed_id", "make_label", "find_results", "load_results"):
        assert getattr(rr, name) is getattr(common, name) is getattr(rd, name), name
    assert rr.Report is common.Report and issubclass(rd.Report, common.Report)
    assert rr._json_ready is common.json_ready is rd._json_ready
    assert issubclass(common.Missing, common.NotComputable)
    assert issubclass(common.Refused, common.NotComputable)
    extra = [f for f in rd.Report.__dataclass_fields__ if f not in common.Report.__dataclass_fields__]
    assert extra == ["findings", "uncomputed", "series_log"]
    assert list(common.Report.__dataclass_fields__) == ["lines", "incomplete", "defects", "data"]
    assert (rr.EXIT_MISMATCH, rr.EXIT_INCOMPLETE) == (1, 2) == (rd.EXIT_MISMATCH, rd.EXIT_INCOMPLETE)
    assert rr.SCHEMAS == rd.SCHEMAS == ("lpcstudy.states/1", "lpcstudy.states/2")
    assert rr.PRIMARY_LEVEL == rd.PRIMARY_LEVEL == 1.0 - 0.05 / 3.0  # the v3 level 1 - alpha/3


# ------------------------------------------------------------------------------------------ Report
def raiser(exc: Exception) -> None:
    """Raise ``exc`` from a named frame (so that the report names this file and function)."""
    raise exc


def innermost_line(exc: BaseException) -> int:
    """Line of the innermost frame of a traceback, by walking the raw traceback objects."""
    tb = exc.__traceback__
    assert tb is not None
    while tb.tb_next is not None:
        tb = tb.tb_next
    return tb.tb_lineno


def test_report_collects_lines_and_the_exit_code_precedence() -> None:
    """Exit 1 beats exit 2 beats 0; nothing recorded gives 0; every record also prints a line.

    Reference: the truth table of the contract written in the module docstring (0 / 1 / 2).
    """
    rep = common.Report()
    assert rep.exit_code() == 0 and rep.lines == [] and rep.data == {}
    rep.say("plain")
    rep.say()
    assert rep.lines == ["plain", ""] and rep.exit_code() == 0
    rep.nc("w", "why")
    assert rep.incomplete == ["not computable: w: why"]
    assert rep.lines[-1] == "  not computable: w: why" and rep.exit_code() == 2
    rep.defect("x differs")
    assert rep.defects == ["x differs"] and rep.lines[-1] == "  MISMATCH: x differs"
    assert rep.exit_code() == 1
    only_defect = common.Report()
    only_defect.defect("y", label="DEFECT")
    assert only_defect.lines == ["  DEFECT: y"] and only_defect.exit_code() == 1


def test_report_internal_error_names_type_message_file_line_and_function() -> None:
    """An unexpected exception is printed with its type, message and innermost frame, counted as
    incomplete (exit 2), never as a MISMATCH.

    Reference: the raw traceback (``tb_next`` walk) for the line; the file and function are literals.
    """
    try:
        raiser(ValueError("boom"))
    except ValueError as exc:
        rep = common.Report()
        rep.internal("stage", exc)
        line = innermost_line(exc)
    want = (f"INTERNAL ERROR: stage: ValueError: boom "
            f"(at test_tools_rehearsal_common.py:{line} in raiser)")
    assert rep.incomplete == [want] and rep.lines == ["  " + want]
    assert rep.defects == [] and rep.exit_code() == 2


def test_attempt_returns_the_value_records_not_computable_and_internal_errors_and_lets_refused_pass(
) -> None:
    """``attempt``: a value passes through; ``NotComputable`` (and ``Missing``) are recorded as
    "not computable" with the exception text; any other exception is an INTERNAL ERROR; ``Refused``
    is a ``NotComputable`` that is never caught.

    Reference: the contract in the docstring, one case each; arguments and keywords pass through.
    """
    rep = common.Report()
    assert common.attempt(rep, "ok", lambda a, b=0: a + b, 2, b=3) == 5 and rep.lines == []
    assert common.attempt(rep, "nc", raiser, common.NotComputable("no data")) is None
    assert common.attempt(rep, "miss", raiser, common.Missing("gone")) is None
    assert rep.incomplete == ["not computable: nc: no data", "not computable: miss: gone"]
    assert common.attempt(rep, "bad", raiser, KeyError("k")) is None
    assert rep.incomplete[-1].startswith("INTERNAL ERROR: bad: KeyError: 'k' (at ")
    assert len(rep.incomplete) == 3 and rep.defects == []
    with pytest.raises(common.Refused, match="no way"):
        common.attempt(rep, "refused", raiser, common.Refused("no way"))
    assert len(rep.incomplete) == 3  # a refusal is not recorded: it stops the run


# ------------------------------------------------------------------------------------------ Dump, dig, fmt
def test_dump_over_a_dict_and_over_an_npz_without_pickles(tmp_path: Path) -> None:
    """``Dump``: ``has``, item access, ``scalar`` and the named ``Missing``; an archive is opened
    with ``allow_pickle=False``, so an object array in it is refused by numpy.

    Reference: the arrays written here (``np.savez``) and read back by hand.
    """
    arrays = {"a": np.arange(6.0).reshape(2, 3), "meta/schema": np.array("lpcstudy.states/2"),
              "n": np.array(7)}
    dump = common.Dump(arrays, "memory")
    assert dump.has("a") and not dump.has("b")
    np.testing.assert_array_equal(dump["a"], np.arange(6.0).reshape(2, 3))
    assert dump.scalar("n") == 7 and isinstance(dump.scalar("n"), int)
    assert dump.scalar("meta/schema") == "lpcstudy.states/2"
    with pytest.raises(common.Missing, match=r"array 'b' is not in memory"):
        dump["b"]
    dump.close()  # a dict has nothing to close
    path = tmp_path / "s.npz"
    np.savez(path, **arrays)
    loaded = common.Dump.load(path)
    try:
        assert loaded.source == str(path) and loaded.has("a")
        np.testing.assert_array_equal(loaded["a"], arrays["a"])
        with pytest.raises(common.Missing, match=f"array 'zz' is not in {re.escape(str(path))}"):
            loaded["zz"]
    finally:
        loaded.close()
    pickled = tmp_path / "p.npz"
    np.savez(pickled, o=np.array([{"x": 1}], dtype=object))
    with pytest.raises(ValueError, match="allow_pickle=False"):
        common.Dump.load(pickled)["o"]


def test_dig_walks_the_tree_and_names_the_absent_or_null_leaf() -> None:
    """``dig`` returns the leaf; an absent key, a non-dict on the way, or a null leaf is ``Missing``.

    Reference: the literal tree below; messages are the literal strings of the contract.
    """
    tree = {"a": {"b": {"c": 3.5, "n": None, "zero": 0}}, "s": "text"}
    assert common.dig(tree, "a", "b", "c") == 3.5
    assert common.dig(tree, "a", "b", "zero") == 0  # a falsy leaf is a value
    assert common.dig(tree, "a")["b"]["c"] == 3.5
    assert common.dig(tree) is tree  # no path: the tree itself
    with pytest.raises(common.Missing, match=r"results leaf a/x/c is absent"):
        common.dig(tree, "a", "x", "c")
    with pytest.raises(common.Missing, match=r"results leaf s/t is absent"):
        common.dig(tree, "s", "t")
    with pytest.raises(common.Missing, match=r"results leaf a/b/n is null"):
        common.dig(tree, "a", "b", "n")


def test_fmt_prints_general_format_and_none_as_na() -> None:
    """``fmt``: four significant digits by default, ``n/a`` for None.

    Reference: Python's ``g`` format applied to literals by hand (0.123456 -> 0.1235, 12345.6 ->
    1.235e+04, 1e-7 -> 1e-07, 0 -> 0).
    """
    assert common.fmt(None) == "n/a" and common.fmt(None, 9) == "n/a"
    assert common.fmt(0.123456) == "0.1235"
    assert common.fmt(12345.6) == "1.235e+04"
    assert common.fmt(1e-7) == "1e-07"
    assert common.fmt(0.0) == "0"
    assert common.fmt(math.pi, 8) == "3.1415927"
    assert common.fmt(float("nan")) == "nan"


# ------------------------------------------------------------------------------------------ seeds and files
def test_is_dev_id_truth_table() -> None:
    """Only a string ``DEV-`` followed by digits is a development id.

    Reference: the plan's identifier form ``DEV-n`` (LPC.PC.7); a confirmatory or malformed id, a
    lower-case prefix, an empty or non-numeric suffix and a non-string are all refused.
    """
    for good in ("DEV-0", "DEV-1", "DEV-12", "DEV-007"):
        assert common.is_dev_id(good) is True, good
    for bad in ("DEV-", "dev-1", "DEV-1a", "DEV-1 ", " DEV-1", "DEV--1", "DEV-1.5", "CONF-1",
                "CONFIRMATORY", "", None, 1, 1.0, ["DEV-1"], b"DEV-1"):
        assert common.is_dev_id(bad) is False, bad


def run_tree(config_id: object = "DEV-3", provenance_id: object = "DEV-3",
             kind: object = "development") -> dict:
    """A minimal results tree with the three recorded seed fields."""
    prov = {"seed_id": provenance_id}
    if kind is not None:
        prov["seed_kind"] = kind
    return {"config": {"seed_id": config_id}, "provenance": prov}


def test_run_seed_id_accepts_only_agreeing_development_ids_of_kind_development() -> None:
    """The id is returned when ``config.seed_id`` and ``provenance.seed_id`` agree, are ``DEV-n``
    and the recorded kind is ``development``; every other case is ``Refused`` with its message.

    Reference: the rule of LPC.PC.7 in the module docstring, one probe per clause.
    """
    assert common.run_seed_id(run_tree()) == "DEV-3"
    with pytest.raises(common.Refused, match="no config block or no provenance block"):
        common.run_seed_id({"provenance": {}})
    with pytest.raises(common.Refused, match="no config block or no provenance block"):
        common.run_seed_id({"config": {}, "provenance": None})
    with pytest.raises(common.Refused, match=r"config.seed_id is 'CONF-1', not a development seed"):
        common.run_seed_id(run_tree(config_id="CONF-1"))
    with pytest.raises(common.Refused, match=r"provenance.seed_id is None, not a development"):
        common.run_seed_id(run_tree(provenance_id=None))
    with pytest.raises(common.Refused, match="the recorded seed ids disagree"):
        common.run_seed_id(run_tree(config_id="DEV-3", provenance_id="DEV-4"))
    with pytest.raises(common.Refused, match=r"seed_kind is 'confirmatory', not 'development'"):
        common.run_seed_id(run_tree(kind="confirmatory"))
    with pytest.raises(common.Refused, match=r"seed_kind is None, not 'development'"):
        common.run_seed_id(run_tree(kind=None))


def test_make_label_is_the_literal_development_label() -> None:
    """The label line that opens both reports (a literal)."""
    assert common.make_label("DEV-1") == (
        "DEVELOPMENT (DEV-1): conditional on one realization; not a hypothesis test")
    assert common.make_label(None).startswith("DEVELOPMENT (None): conditional")


def test_find_results_and_load_results_read_a_file_or_its_directory(tmp_path: Path) -> None:
    """``find_results`` accepts the file or its directory; ``load_results`` returns
    ``(file, tree, seed_id)``; a missing file, bad JSON and a non-object are ``NotComputable``;
    a refused id is ``Refused`` (a ``NotComputable`` subclass that ``attempt`` never catches).

    Reference: files written here with ``json.dumps``; the messages are the literal strings.
    """
    tree = run_tree()
    (tmp_path / "results.json").write_text(json.dumps(tree))
    assert common.find_results(tmp_path) == tmp_path / "results.json"
    assert common.find_results(tmp_path / "results.json") == tmp_path / "results.json"
    assert common.load_results(tmp_path) == (tmp_path / "results.json", tree, "DEV-3")
    with pytest.raises(common.NotComputable, match=f"no results.json at {re.escape(str(tmp_path / 'nope'))}"):
        common.find_results(tmp_path / "nope")
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(common.NotComputable, match="no results.json at"):
        common.load_results(empty)
    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "results.json").write_text("{not json")
    with pytest.raises(common.NotComputable, match=r"results.json is unreadable: "):
        common.load_results(bad)
    listing = tmp_path / "list"
    listing.mkdir()
    (listing / "results.json").write_text("[1, 2]")
    with pytest.raises(common.NotComputable, match="does not hold a JSON object"):
        common.load_results(listing)
    refused = tmp_path / "refused"
    refused.mkdir()
    (refused / "results.json").write_text(json.dumps(run_tree(config_id="CONF-1")))
    with pytest.raises(common.Refused):
        common.load_results(refused)


# ------------------------------------------------------------------------------------------ json_ready
def test_json_ready_converts_numpy_and_nonfinite_values_so_strict_json_accepts_them() -> None:
    """Numpy scalars and arrays, tuples and non-string keys become JSON types; NaN and the
    infinities become null; the result survives ``json.dumps(..., allow_nan=False)``.

    Reference: the expected structure written by hand.
    """
    obj = {1: (np.float64(0.5), np.int64(3), np.bool_(True)),
           "arr": np.array([[1.0, np.nan], [np.inf, -np.inf]]), "f": float("nan"),
           "ok": [1, "s", None, False], "nested": {"x": np.float32(2.0)}}
    got = common.json_ready(obj)
    assert got == {"1": [0.5, 3, True], "arr": [[1.0, None], [None, None]], "f": None,
                   "ok": [1, "s", None, False], "nested": {"x": 2.0}}
    assert type(got["1"][1]) is int and type(got["1"][2]) is bool and type(got["1"][0]) is float
    assert json.loads(json.dumps(got, allow_nan=False)) == got
    assert common.json_ready("text") == "text" and common.json_ready(4) == 4
