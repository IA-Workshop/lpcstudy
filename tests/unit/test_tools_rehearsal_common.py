"""Tests of ``tools/rehearsal_common.py`` (WU-0003.10; plan amendment 7, G4,
acceptance h1 and h3).

DEVELOPMENT code; needs owner review before freeze (statistics code). The module
holds what ``tools/rehearsal_report.py`` and ``tools/rehearsal_diagnostics.py``
had in common, moved without a change of behavior. Two kinds of test check it:

* h1: the ``test_regression_*`` tests compare the complete outputs of both tools
  (text, ``--json``, exit code, stderr) with golden files recorded before the
  move (``fixtures/golden_rehearsal/``, see its README). This is a **regression
  guard** (the tool against its own earlier output), not evidence of
  correctness.
* h3: the other tests are specifications of the shared functions, with
  references written here by hand (truth tables, literal strings, a raw
  traceback walk) that do not depend on the code under test.

Not moved, so not tested here: ``block_variance`` and the influence-series
builders, which differ in substance between the two tools (unit Log,
WU-0003.10). Their tests stay in the two tool test files. All tests run on the
CPU in under 5 s and draw no random numbers.
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


# --- h1 -----------------------------------------------------------------------
@pytest.fixture(scope="module")
def produced() -> dict[str, str]:
    """Run every golden case once on the code under test."""
    return golden.produce()


def test_regression_the_golden_folder_and_the_cases_name_the_same_files(
    produced,
) -> None:
    """Regression guard: no case is missing or left over.

    This makes sure no golden file goes unchecked.
    """
    on_disk = sorted(
        p.name for p in golden.GOLDEN.iterdir() if p.name != "README.md"
    )
    assert sorted(produced) == on_disk
    assert all(
        (name + ".txt") in on_disk
        for name in sorted({n.split(".")[0] for n in on_disk})
    )


def test_regression_golden_outputs_are_byte_identical(produced) -> None:
    """Regression guard (h1): every report, JSON file, exit code and stderr is
    byte-identical to its golden file.

    This is not evidence of correctness. A failure names the first differing
    file and line. The golden files are never rewritten to make a test pass (see
    their README).
    """
    for name, text in sorted(produced.items()):
        want = (golden.GOLDEN / name).read_text()
        if text != want:
            got_lines, want_lines = text.splitlines(), want.splitlines()
            first = next(
                (
                    i
                    for i, (a, b) in enumerate(
                        zip(got_lines, want_lines, strict=False)
                    )
                    if a != b
                ),
                min(len(got_lines), len(want_lines)),
            )
            pytest.fail(
                f"{name} differs at line {first + 1}: got "
                f"{got_lines[first:first + 1]!r}, "
                f"golden {want_lines[first:first + 1]!r}"
            )


# --- sharing ------------------------------------------------------------------
def test_both_tools_use_one_definition_of_each_shared_name() -> None:
    """Each shared class and function exists once, and both tools use that one.

    The names in the two tools must be the very objects of the shared module.
    The diagnostics tool's ``Report`` may extend the shared one with its three
    own records and nothing else. Reference: the names listed here by hand.
    """
    assert rr.common is rd.common and common.__name__ == "rehearsal_common"
    for name in (
        "NotComputable",
        "Missing",
        "Refused",
        "attempt",
        "Dump",
        "dig",
        "fmt",
        "is_dev_id",
        "run_seed_id",
        "make_label",
        "find_results",
        "load_results",
    ):
        assert (
            getattr(rr, name) is getattr(common, name) is getattr(rd, name)
        ), name
    assert rr.Report is common.Report and issubclass(rd.Report, common.Report)
    assert rr._json_ready is common.json_ready is rd._json_ready
    assert issubclass(common.Missing, common.NotComputable)
    assert issubclass(common.Refused, common.NotComputable)
    extra = [
        f
        for f in rd.Report.__dataclass_fields__
        if f not in common.Report.__dataclass_fields__
    ]
    assert extra == ["findings", "uncomputed", "series_log"]
    assert list(common.Report.__dataclass_fields__) == [
        "lines",
        "incomplete",
        "defects",
        "data",
    ]
    assert (
        (rr.EXIT_MISMATCH, rr.EXIT_INCOMPLETE)
        == (1, 2)
        == (rd.EXIT_MISMATCH, rd.EXIT_INCOMPLETE)
    )
    assert (
        rr.SCHEMAS == rd.SCHEMAS == ("lpcstudy.states/1", "lpcstudy.states/2")
    )
    assert (
        rr.PRIMARY_LEVEL == rd.PRIMARY_LEVEL == 1.0 - 0.05 / 3.0
    )  # the v3 level 1 - alpha/3


# --- Report -------------------------------------------------------------------
def raiser(exc: Exception) -> None:
    """Raise ``exc`` from a named function, so the report can name this file and
    function.
    """
    raise exc


def innermost_line(exc: BaseException) -> int:
    """Return the line of the innermost frame of a traceback, found by walking
    the traceback objects directly.
    """
    tb = exc.__traceback__
    assert tb is not None
    while tb.tb_next is not None:
        tb = tb.tb_next
    return tb.tb_lineno


def test_report_collects_lines_and_the_exit_code_precedence() -> None:
    """Exit 1 beats exit 2, which beats 0; every record also prints a line.

    Nothing recorded gives 0. Reference: the truth table of the exit codes (0,
    1, 2) in the module docstring.
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
    assert (
        rep.defects == ["x differs"]
        and rep.lines[-1] == "  MISMATCH: x differs"
    )
    assert rep.exit_code() == 1
    only_defect = common.Report()
    only_defect.defect("y", label="DEFECT")
    assert only_defect.lines == ["  DEFECT: y"] and only_defect.exit_code() == 1


def test_report_internal_error_names_type_message_file_line_and_function() -> (
    None
):
    """An unexpected exception is printed with its type, message and innermost
    frame.

    It counts as incomplete (exit 2), never as a MISMATCH. Reference: the raw
    traceback for the line number, and literal strings for the file and function
    names.
    """
    try:
        raiser(ValueError("boom"))
    except ValueError as exc:
        rep = common.Report()
        rep.internal("stage", exc)
        line = innermost_line(exc)
    want = (
        f"INTERNAL ERROR: stage: ValueError: boom "
        f"(at test_tools_rehearsal_common.py:{line} in raiser)"
    )
    assert rep.incomplete == [want] and rep.lines == ["  " + want]
    assert rep.defects == [] and rep.exit_code() == 2


def test_attempt_records_failures_and_lets_refused_pass() -> None:
    """``attempt`` handles each kind of outcome as documented.

    A value passes through (arguments and keywords too). A ``NotComputable`` or
    ``Missing`` is recorded as "not computable" with the exception text. Any
    other exception is recorded as an INTERNAL ERROR. A ``Refused`` is never
    caught, because a refused run must stop. Reference: the contract in the
    docstring of ``attempt``, one case each.
    """
    rep = common.Report()
    assert (
        common.attempt(rep, "ok", lambda a, b=0: a + b, 2, b=3) == 5
        and rep.lines == []
    )
    assert (
        common.attempt(rep, "nc", raiser, common.NotComputable("no data"))
        is None
    )
    assert common.attempt(rep, "miss", raiser, common.Missing("gone")) is None
    assert rep.incomplete == [
        "not computable: nc: no data",
        "not computable: miss: gone",
    ]
    assert common.attempt(rep, "bad", raiser, KeyError("k")) is None
    assert rep.incomplete[-1].startswith(
        "INTERNAL ERROR: bad: KeyError: 'k' (at "
    )
    assert len(rep.incomplete) == 3 and rep.defects == []
    with pytest.raises(common.Refused, match="no way"):
        common.attempt(rep, "refused", raiser, common.Refused("no way"))
    assert (
        len(rep.incomplete) == 3
    )  # a refusal is not recorded: it stops the run


# --- Dump, dig, fmt -----------------------------------------------------------
def test_dump_over_a_dict_and_over_an_npz_without_pickles(
    tmp_path: Path,
) -> None:
    """``Dump`` works on a dict and on an ``.npz`` file, and refuses pickles.

    Checks ``has``, item access, ``scalar`` and the named ``Missing`` error. An
    archive is opened with ``allow_pickle=False``, so numpy must refuse an
    object array in it. Reference: arrays written here with ``np.savez`` and
    read back by hand.
    """
    arrays = {
        "a": np.arange(6.0).reshape(2, 3),
        "meta/schema": np.array("lpcstudy.states/2"),
        "n": np.array(7),
    }
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
        with pytest.raises(
            common.Missing, match=f"array 'zz' is not in {re.escape(str(path))}"
        ):
            loaded["zz"]
    finally:
        loaded.close()
    pickled = tmp_path / "p.npz"
    np.savez(pickled, o=np.array([{"x": 1}], dtype=object))
    with pytest.raises(ValueError, match="allow_pickle=False"):
        common.Dump.load(pickled)["o"]


def test_dig_walks_the_tree_and_names_the_absent_or_null_leaf() -> None:
    """``dig`` returns the leaf, and raises ``Missing`` for an absent or null
    leaf.

    An absent key, a non-dictionary in the middle of the path and a null leaf
    are all ``Missing``, while a falsy value such as 0 is a real value.
    Reference: the literal tree in the test and the literal messages.
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
    """``fmt`` uses four significant digits by default and prints None as
    ``n/a``.

    Reference: Python's ``g`` format applied to literals by hand (0.123456 gives
    0.1235, 12345.6 gives 1.235e+04, 1e-7 gives 1e-07, 0 gives 0).
    """
    assert common.fmt(None) == "n/a" and common.fmt(None, 9) == "n/a"
    assert common.fmt(0.123456) == "0.1235"
    assert common.fmt(12345.6) == "1.235e+04"
    assert common.fmt(1e-7) == "1e-07"
    assert common.fmt(0.0) == "0"
    assert common.fmt(math.pi, 8) == "3.1415927"
    assert common.fmt(float("nan")) == "nan"


# --- seeds and files ----------------------------------------------------------
def test_is_dev_id_truth_table() -> None:
    """Only a string ``DEV-`` followed by digits is a development id.

    Reference: the identifier form ``DEV-n`` of LPC.PC.7. A confirmatory or
    malformed id, a lower-case prefix, an empty or non-numeric suffix, and a
    non-string must all be refused.
    """
    for good in ("DEV-0", "DEV-1", "DEV-12", "DEV-007"):
        assert common.is_dev_id(good) is True, good
    for bad in (
        "DEV-",
        "dev-1",
        "DEV-1a",
        "DEV-1 ",
        " DEV-1",
        "DEV--1",
        "DEV-1.5",
        "CONF-1",
        "CONFIRMATORY",
        "",
        None,
        1,
        1.0,
        ["DEV-1"],
        b"DEV-1",
    ):
        assert common.is_dev_id(bad) is False, bad


def run_tree(
    config_id: object = "DEV-3",
    provenance_id: object = "DEV-3",
    kind: object = "development",
) -> dict:
    """Build a minimal results tree with the three recorded seed fields."""
    prov = {"seed_id": provenance_id}
    if kind is not None:
        prov["seed_kind"] = kind
    return {"config": {"seed_id": config_id}, "provenance": prov}


def test_run_seed_id_accepts_only_agreeing_development_ids() -> None:
    """A run is accepted only if both recorded ids agree, are ``DEV-n``, and the
    kind is ``development``.

    Every other case must raise ``Refused`` with its own message. Reference: the
    rule of LPC.PC.7 in the module docstring, one probe per clause.
    """
    assert common.run_seed_id(run_tree()) == "DEV-3"
    with pytest.raises(
        common.Refused, match="no config block or no provenance block"
    ):
        common.run_seed_id({"provenance": {}})
    with pytest.raises(
        common.Refused, match="no config block or no provenance block"
    ):
        common.run_seed_id({"config": {}, "provenance": None})
    with pytest.raises(
        common.Refused,
        match=r"config.seed_id is 'CONF-1', not a development seed",
    ):
        common.run_seed_id(run_tree(config_id="CONF-1"))
    with pytest.raises(
        common.Refused, match=r"provenance.seed_id is None, not a development"
    ):
        common.run_seed_id(run_tree(provenance_id=None))
    with pytest.raises(common.Refused, match="the recorded seed ids disagree"):
        common.run_seed_id(run_tree(config_id="DEV-3", provenance_id="DEV-4"))
    with pytest.raises(
        common.Refused, match=r"seed_kind is 'confirmatory', not 'development'"
    ):
        common.run_seed_id(run_tree(kind="confirmatory"))
    with pytest.raises(
        common.Refused, match=r"seed_kind is None, not 'development'"
    ):
        common.run_seed_id(run_tree(kind=None))


def test_make_label_is_the_literal_development_label() -> None:
    """The label line that opens both reports is the expected literal text."""
    assert common.make_label("DEV-1") == (
        "DEVELOPMENT (DEV-1): conditional on one realization; "
        "not a hypothesis test"
    )
    assert common.make_label(None).startswith("DEVELOPMENT (None): conditional")


def test_find_results_and_load_results_read_a_file_or_its_directory(
    tmp_path: Path,
) -> None:
    """``find_results`` accepts a file or its directory, and ``load_results``
    reports bad input.

    ``load_results`` returns the file, the tree and the seed id. A missing file,
    bad JSON and a JSON value that is not an object are ``NotComputable``. A
    refused seed id is ``Refused``, a subclass that ``attempt`` never catches.
    Reference: files written here with ``json.dumps`` and the literal messages.
    """
    tree = run_tree()
    (tmp_path / "results.json").write_text(json.dumps(tree))
    assert common.find_results(tmp_path) == tmp_path / "results.json"
    assert (
        common.find_results(tmp_path / "results.json")
        == tmp_path / "results.json"
    )
    assert common.load_results(tmp_path) == (
        tmp_path / "results.json",
        tree,
        "DEV-3",
    )
    with pytest.raises(
        common.NotComputable,
        match=f"no results.json at {re.escape(str(tmp_path / 'nope'))}",
    ):
        common.find_results(tmp_path / "nope")
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(common.NotComputable, match="no results.json at"):
        common.load_results(empty)
    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "results.json").write_text("{not json")
    with pytest.raises(
        common.NotComputable, match=r"results.json is unreadable: "
    ):
        common.load_results(bad)
    listing = tmp_path / "list"
    listing.mkdir()
    (listing / "results.json").write_text("[1, 2]")
    with pytest.raises(
        common.NotComputable, match="does not hold a JSON object"
    ):
        common.load_results(listing)
    refused = tmp_path / "refused"
    refused.mkdir()
    (refused / "results.json").write_text(
        json.dumps(run_tree(config_id="CONF-1"))
    )
    with pytest.raises(common.Refused):
        common.load_results(refused)


# --- json_ready ---------------------------------------------------------------
def test_json_ready_makes_numpy_and_nonfinite_values_json_safe() -> None:
    """Numpy values, tuples and non-string keys become plain JSON types.

    NaN and the infinities become null, and the result survives
    ``json.dumps(..., allow_nan=False)``. Reference: the expected structure
    written by hand.
    """
    obj = {
        1: (np.float64(0.5), np.int64(3), np.bool_(True)),
        "arr": np.array([[1.0, np.nan], [np.inf, -np.inf]]),
        "f": float("nan"),
        "ok": [1, "s", None, False],
        "nested": {"x": np.float32(2.0)},
    }
    got = common.json_ready(obj)
    assert got == {
        "1": [0.5, 3, True],
        "arr": [[1.0, None], [None, None]],
        "f": None,
        "ok": [1, "s", None, False],
        "nested": {"x": 2.0},
    }
    assert (
        type(got["1"][1]) is int
        and type(got["1"][2]) is bool
        and type(got["1"][0]) is float
    )
    assert json.loads(json.dumps(got, allow_nan=False)) == got
    assert common.json_ready("text") == "text" and common.json_ready(4) == 4
