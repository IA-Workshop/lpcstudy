"""Tests of ``tools/leafdiff.py`` (WU-0002.14, review R4).

References: hand-written JSON trees whose differences are known by construction (IEEE bytes of
doubles: ``0.0`` against ``-0.0``, the next double after 1.0, NaN against NaN, int against float),
and the exit codes of the tool's docstring. Tolerance: none (exact comparisons).
"""

from __future__ import annotations

import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools" / "leafdiff.py"
_SPEC = importlib.util.spec_from_file_location("leafdiff", TOOL)
assert _SPEC is not None and _SPEC.loader is not None
ld = importlib.util.module_from_spec(_SPEC)
sys.modules["leafdiff"] = ld
_SPEC.loader.exec_module(ld)

BASE = {"config": {"seed": 7}, "provenance": {"commit": "a"}, "seconds": 1.0,
        "systems": {"lorenz63": {"seconds": 2.0, "context": {"lambda_max": 0.9, "delay": 5},
                                 "H3a": {"pairs": [[0, 1], [1, 2]]}, "a/b": {"z": -0.0},
                                 "empty": {}, "x": math.nan}}}


def edited(**paths):
    """A deep copy of BASE with ``systems.lorenz63.<dotted>`` replaced (``None`` deletes)."""
    tree = json.loads(json.dumps(BASE, allow_nan=True))
    node = tree["systems"]["lorenz63"]
    for dotted, value in paths.items():
        *head, last = dotted.split("__")
        target = node
        for part in head:
            target = target[part]
        if value is ...:
            del target[last]
        else:
            target[last] = value
    return tree


def run(tmp_path, a, b, *flags):
    pa, pb = tmp_path / "a.json", tmp_path / "b.json"
    pa.write_text(json.dumps(a))
    pb.write_text(json.dumps(b))
    return subprocess.run([sys.executable, "-I", str(TOOL), str(pa), str(pb), *flags],
                          capture_output=True, text=True, timeout=60, check=False)


def classify(a, b):
    return ld.compare(ld.flatten(a), ld.flatten(b))


def test_flatten_excludes_provenance_and_seconds_and_escapes_slashes() -> None:
    """The conventions of the docstring: list lengths are leaves, ``/`` in a key is ``%2F``."""
    leaves = ld.flatten(BASE)
    assert "provenance/commit" not in leaves and not any(p.endswith("seconds") for p in leaves)
    assert leaves["systems/lorenz63/a%2Fb/z"] == 0.0
    assert leaves["systems/lorenz63/H3a/pairs/#len"] == 2
    assert leaves["systems/lorenz63/H3a/pairs/[1]/#len"] == 2
    assert leaves["systems/lorenz63/H3a/pairs/[1]/[0]"] == 1
    assert leaves["systems/lorenz63/empty/<empty>"] == "<empty dict>"


def test_identical_files_are_identical_including_nan() -> None:
    """NaN against the same NaN, and a tree against itself: nothing differs."""
    result = classify(BASE, edited())
    assert not (result["different"] or result["added"] or result["removed"])


def test_one_ulp_negative_zero_and_int_against_float_differ() -> None:
    """Hand cases: the next double after 0.9, -0.0 against 0.0, 5 against 5.0, a string."""
    result = classify(BASE, edited(context__lambda_max=math.nextafter(0.9, 1.0)))
    assert result["different"] == ["systems/lorenz63/context/lambda_max"]
    result = classify(BASE, edited(**{"a/b__z": 0.0}))
    assert result["different"] == ["systems/lorenz63/a%2Fb/z"]
    result = classify(BASE, edited(context__delay=5.0))
    assert result["different"] == ["systems/lorenz63/context/delay"]
    result = classify(BASE, edited(context__delay="5"))
    assert result["different"] == ["systems/lorenz63/context/delay"]


def test_added_removed_and_a_change_of_list_length() -> None:
    """A new key is added, a deleted one removed, a longer list adds its items and changes #len."""
    result = classify(BASE, edited(context__start=3, context__delay=...))
    assert result["added"] == ["systems/lorenz63/context/start"]
    assert result["removed"] == ["systems/lorenz63/context/delay"]
    longer = edited(H3a={"pairs": [[0, 1], [1, 2], [2, 3]]})
    result = classify(BASE, longer)
    assert result["different"] == ["systems/lorenz63/H3a/pairs/#len"]
    assert result["added"] == ["systems/lorenz63/H3a/pairs/[2]/#len",
                               "systems/lorenz63/H3a/pairs/[2]/[0]",
                               "systems/lorenz63/H3a/pairs/[2]/[1]"]


def test_groups_count_by_path_prefix() -> None:
    """``group_counts`` groups by the first segments."""
    counts = ld.group_counts(["a/b/c", "a/b/d", "a/e/f", "g"], 2)
    assert dict(counts) == {"a/b": 2, "a/e": 1, "g": 1}


def test_predicted_equal_lists_defects_and_unpredicted() -> None:
    """A predicted-equal leaf that differs (or vanished) is a DEFECT; covered equal leaves are not."""
    result = classify(BASE, edited(context__lambda_max=1.0, context__delay=...))
    out = ld.check_predicted(result, [r"systems/lorenz63/context/.*", r"config/seed"])
    assert out["defects"] == ["systems/lorenz63/context/lambda_max",
                              "systems/lorenz63/context/delay"]
    assert "systems/lorenz63/H3a/pairs/#len" in out["unpredicted"]
    assert "config/seed" not in out["unpredicted"]


def test_cli_exit_codes_and_report(tmp_path) -> None:
    """Exit 0 for equal files; 1 for a difference; 2 for an unreadable file; the report counts."""
    done = run(tmp_path, BASE, edited())
    assert done.returncode == 0 and "different 0, removed 0, added 0" in done.stdout
    done = run(tmp_path, BASE, edited(context__lambda_max=1.0, context__start=1))
    assert done.returncode == 1
    assert "different 1, removed 0, added 1" in done.stdout
    assert "systems/lorenz63/context/lambda_max" in done.stdout
    missing = subprocess.run([sys.executable, "-I", str(TOOL), str(tmp_path / "no.json"),
                              str(tmp_path / "no2.json")], capture_output=True, text=True,
                             timeout=60, check=False)
    assert missing.returncode == 2 and "leafdiff: error" in missing.stderr


def test_cli_predicted_file(tmp_path) -> None:
    """``--predicted-equal``: a defect makes exit 1 and is printed; comment lines are ignored."""
    predicted = tmp_path / "pred.txt"
    predicted.write_text("# comment\nsystems/lorenz63/context/.*\n")
    done = run(tmp_path, BASE, edited(context__lambda_max=1.0), "--predicted-equal", str(predicted))
    assert done.returncode == 1 and "1 DEFECTS" in done.stdout
    assert "DEFECT systems/lorenz63/context/lambda_max" in done.stdout
    done = run(tmp_path, BASE, edited(), "--predicted-equal", str(predicted))
    assert done.returncode == 0 and "0 DEFECTS" in done.stdout
    bad = tmp_path / "bad.txt"
    bad.write_text("(unclosed\n")
    done = run(tmp_path, BASE, edited(), "--predicted-equal", str(bad))
    assert done.returncode == 2
