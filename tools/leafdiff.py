#!/usr/bin/env python3
"""Leaf-wise comparison of two ``results.json`` files, floats by IEEE bytes (WU-0002.14, review R4).

Usage::

    python3 -I tools/leafdiff.py A_RESULTS_JSON B_RESULTS_JSON [--group-depth N] [--show N]
        [--predicted-equal FILE]

Both files are flattened to leaves addressed by ``/``-joined paths (a ``/`` inside a key is written
``%2F``; list items are ``[i]``, and the length of every list is a leaf ``<path>/#len`` so that a
change of shape is seen). The top-level ``provenance`` block and every key named ``seconds`` are
excluded (wall-clock and host record, not results). Two leaves are equal iff their types are the
same and, for floats, their IEEE-754 bytes are the same: ``0.0`` and ``-0.0`` differ, NaN equals a
NaN with the same payload, ``1`` (int) differs from ``1.0``.

Reported: the leaf counts, the number of different, added (only in B) and removed (only in A)
leaves, the counts of each grouped by the first ``--group-depth`` path segments (default 3), and the
first ``--show`` paths of each kind (default 20). With ``--predicted-equal FILE`` (one regular
expression per line, ``#`` comments; a path matches if the expression ``fullmatch``es it) the leaves
that match a line are checked: a different or missing one is listed as a DEFECT (a predicted-equal
leaf that differs), and the equal leaves that no line predicted are counted.

What it is for: the staged smokes S0 to S3 of WU-0002.14, and the criteria of P1 that compare two
runs leaf by leaf (R-a key set against P0, the digests and ``trajectory_max_abs.statistics`` of R-b,
R-g and R-h). It reads statistics and computes none. Standard library only.

Exit codes: 0 no different, added or removed leaf (and no DEFECT); 1 at least one of them; 2 an
unreadable input or a usage error.
"""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from collections import Counter
from pathlib import Path

EXCLUDED_TOP = frozenset({"provenance"})
EXCLUDED_KEY = "seconds"


def _escape(key: object) -> str:
    return str(key).replace("/", "%2F")


def flatten(tree: object, prefix: tuple[str, ...] = (), top: bool = True) -> dict[str, object]:
    """Flatten a JSON tree to ``{path: leaf}`` (see the module docstring for the conventions)."""
    out: dict[str, object] = {}
    if isinstance(tree, dict):
        for key, value in tree.items():
            if key == EXCLUDED_KEY or (top and key in EXCLUDED_TOP):
                continue
            out.update(flatten(value, (*prefix, _escape(key)), False))
        if not tree and prefix:
            out["/".join((*prefix, "<empty>"))] = "<empty dict>"
    elif isinstance(tree, list):
        out["/".join((*prefix, "#len"))] = len(tree)
        for i, value in enumerate(tree):
            out.update(flatten(value, (*prefix, f"[{i}]"), False))
    else:
        out["/".join(prefix)] = tree
    return out


def leaf_key(value: object) -> tuple:
    """The identity of a leaf: its type and, for a float, its 8 IEEE bytes."""
    if isinstance(value, float):
        return ("float", struct.pack("<d", value))
    return (type(value).__name__, value)


def compare(a: dict[str, object], b: dict[str, object]) -> dict[str, list[str]]:
    """Classify the paths of two flattened files: ``common``, ``different``, ``added``, ``removed``."""
    common = sorted(set(a) & set(b))
    return {"common": common,
            "different": [p for p in common if leaf_key(a[p]) != leaf_key(b[p])],
            "added": sorted(set(b) - set(a)), "removed": sorted(set(a) - set(b))}


def group_counts(paths: list[str], depth: int) -> Counter:
    """Count paths by their first ``depth`` segments."""
    return Counter("/".join(p.split("/")[:depth]) for p in paths)


def check_predicted(result: dict[str, list[str]], patterns: list[str]) -> dict[str, list[str]]:
    """Leaves matching a predicted-equal pattern: ``defects`` (different or absent from B) and
    ``unpredicted`` (equal leaves that no pattern covers)."""
    regexes = [re.compile(p) for p in patterns]
    covered = lambda path: any(r.fullmatch(path) for r in regexes)
    different = set(result["different"])
    defects = [p for p in result["common"] if covered(p) and p in different]
    defects += [p for p in result["removed"] if covered(p)]
    unpredicted = [p for p in result["common"] if p not in different and not covered(p)]
    return {"defects": defects, "unpredicted": unpredicted}


def report(a_path: str, b_path: str, a: dict, b: dict, result: dict, depth: int, show: int,
           predicted: dict | None) -> list[str]:
    """The text report."""
    lines = [f"A: {a_path}", f"B: {b_path}",
             f"leaves: A {len(a)}, B {len(b)}, common {len(result['common'])}, different "
             f"{len(result['different'])}, removed {len(result['removed'])}, added "
             f"{len(result['added'])}"]
    for kind in ("different", "added", "removed"):
        paths = result[kind]
        if not paths:
            continue
        lines.append(f"-- {kind}: {len(paths)} leaves by the first {depth} path segments")
        lines += [f"  {n:6d}  {g}" for g, n in sorted(group_counts(paths, depth).items())]
        lines += [f"  first {min(show, len(paths))}:"] + [f"    {p}" for p in paths[:show]]
    if predicted is not None:
        lines.append(f"predicted-equal: {len(predicted['defects'])} DEFECTS; equal but not "
                     f"predicted: {len(predicted['unpredicted'])}")
        lines += [f"  DEFECT {p}" for p in predicted["defects"][:show]]
    return lines


def main(argv: list[str] | None = None) -> int:
    """Command-line entry; returns the exit code."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("a", type=Path)
    ap.add_argument("b", type=Path)
    ap.add_argument("--group-depth", type=int, default=3)
    ap.add_argument("--show", type=int, default=20)
    ap.add_argument("--predicted-equal", type=Path, default=None)
    args = ap.parse_args(argv)
    try:
        a, b = (flatten(json.loads(p.read_text())) for p in (args.a, args.b))
        patterns = None
        if args.predicted_equal is not None:
            patterns = [ln.strip() for ln in args.predicted_equal.read_text().splitlines()
                        if ln.strip() and not ln.lstrip().startswith("#")]
        result = compare(a, b)
        predicted = check_predicted(result, patterns) if patterns is not None else None
    except (OSError, ValueError, re.error) as exc:
        print(f"leafdiff: error: {exc}", file=sys.stderr)
        return 2
    print("\n".join(report(str(args.a), str(args.b), a, b, result, args.group_depth, args.show,
                           predicted)))
    bad = result["different"] or result["added"] or result["removed"] or (
        predicted is not None and predicted["defects"])
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
