#!/usr/bin/env python3
"""Leaf-wise comparison of two ``results.json`` files, floats by IEEE bytes
(WU-0002.14, review R4).

A study run writes one ``results.json`` file: a large tree of numbers, strings
and lists. This tool answers one question about two such files: is every number
the same, down to the last bit? It is how the staged smoke runs of WU-0002.14
and the P1 criteria check that a code change did not move any result. It only
reads statistics and computes none, and it uses the standard library only. No
other module of the study imports it, except a few tests.

Usage::

    python3 -I tools/leafdiff.py A_RESULTS_JSON B_RESULTS_JSON
        [--group-depth N] [--show N] [--predicted-equal FILE]

How the comparison works. Both files are flattened to "leaves", the values at
the bottom of the tree, each named by a path of keys joined with ``/`` (a ``/``
inside a key is written ``%2F``; list items are written ``[i]``). The length of
every list is also a leaf, ``<path>/#len``, so a change of shape is noticed. The
top-level ``provenance`` block and every key named ``seconds`` are skipped,
because they record the host and the wall-clock time, not results. Two leaves
are equal only if they have the same type and, for floats, the same 8 IEEE-754
bytes. So ``0.0`` and ``-0.0`` differ, a NaN equals a NaN with the same payload,
and the integer ``1`` differs from the float ``1.0``.

What is reported. The report gives the leaf counts, the number of different
leaves, of added leaves (only in B) and of removed leaves (only in A), the
counts of each grouped by the first ``--group-depth`` path segments (default 3),
and the first ``--show`` paths of each kind (default 20). With
``--predicted-equal FILE`` (one regular expression per line; ``#`` starts a
comment; a path matches if the expression matches the whole path) the leaves
that a line predicts to be equal are checked. A predicted leaf that differs or
is missing is listed as a DEFECT, and the equal leaves that no line predicted
are counted.

Exit codes: 0 when no leaf is different, added or removed (and there is no
DEFECT); 1 when at least one is; 2 for an unreadable input or a usage error.
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
    """Return ``key`` as text, with each ``/`` written ``%2F``."""
    return str(key).replace("/", "%2F")


def flatten(
    tree: object, prefix: tuple[str, ...] = (), top: bool = True
) -> dict[str, object]:
    """Turn a JSON tree into a flat ``{path: leaf}`` dictionary.

    A path is the keys on the way down, joined with ``/``. A list contributes
    one leaf for its length (``<path>/#len``) and one subtree per item
    (``[i]``). An empty dictionary becomes the leaf ``<path>/<empty>``. Under
    ``top`` (the root) the ``provenance`` key is skipped, and the key
    ``seconds`` is skipped at every depth.

    Parameters
    ----------
    tree : object
        A parsed JSON value.
    prefix : tuple of str
        The path of ``tree`` within the whole file.
    top : bool
        True only for the root, where ``provenance`` is excluded.

    Returns
    -------
    dict of str to object
        Leaf path to leaf value.
    """
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
    """Return the identity of a leaf: its type and, for a float, its 8 IEEE
    bytes.

    Comparing these keys, instead of the values, is what makes ``0.0`` differ
    from ``-0.0`` and a NaN equal itself.
    """
    if isinstance(value, float):
        return ("float", struct.pack("<d", value))
    return (type(value).__name__, value)


def compare(a: dict[str, object], b: dict[str, object]) -> dict[str, list[str]]:
    """Sort the paths of two flattened files into four lists.

    Parameters
    ----------
    a, b : dict
        Flattened files, as returned by ``flatten``.

    Returns
    -------
    dict of str to list of str
        ``common`` (in both), ``different`` (in both, but not equal by
        ``leaf_key``), ``added`` (only in ``b``) and ``removed`` (only in
        ``a``).
    """
    common = sorted(set(a) & set(b))
    return {
        "common": common,
        "different": [p for p in common if leaf_key(a[p]) != leaf_key(b[p])],
        "added": sorted(set(b) - set(a)),
        "removed": sorted(set(a) - set(b)),
    }


def group_counts(paths: list[str], depth: int) -> Counter:
    """Count paths by their first ``depth`` segments, to see where differences
    cluster.
    """
    return Counter("/".join(p.split("/")[:depth]) for p in paths)


def check_predicted(
    result: dict[str, list[str]], patterns: list[str]
) -> dict[str, list[str]]:
    """Check the leaves that the ``--predicted-equal`` patterns say must not
    change.

    Parameters
    ----------
    result : dict
        The output of ``compare``.
    patterns : list of str
        Regular expressions; a path is "covered" if one matches all of it.

    Returns
    -------
    dict of str to list of str
        ``defects``: covered leaves that differ or are missing from B.
        ``unpredicted``: equal leaves that no pattern covers.
    """
    regexes = [re.compile(p) for p in patterns]
    covered = lambda path: any(r.fullmatch(path) for r in regexes)
    different = set(result["different"])
    defects = [p for p in result["common"] if covered(p) and p in different]
    defects += [p for p in result["removed"] if covered(p)]
    unpredicted = [
        p for p in result["common"] if p not in different and not covered(p)
    ]
    return {"defects": defects, "unpredicted": unpredicted}


def report(
    a_path: str,
    b_path: str,
    a: dict,
    b: dict,
    result: dict,
    depth: int,
    show: int,
    predicted: dict | None,
) -> list[str]:
    """Build the text report (a list of lines) from the comparison.

    Parameters
    ----------
    a_path, b_path : str
        The file names, printed at the top.
    a, b : dict
        The flattened files.
    result : dict
        The output of ``compare``.
    depth : int
        How many path segments to group by.
    show : int
        How many example paths to print for each kind.
    predicted : dict or None
        The output of ``check_predicted``, or None when not requested.
    """
    lines = [
        f"A: {a_path}",
        f"B: {b_path}",
        f"leaves: A {len(a)}, B {len(b)}, common {len(result['common'])}, "
        f"different {len(result['different'])}, "
        f"removed {len(result['removed'])}, added {len(result['added'])}",
    ]
    for kind in ("different", "added", "removed"):
        paths = result[kind]
        if not paths:
            continue
        lines.append(
            f"-- {kind}: {len(paths)} leaves by the first {depth} path segments"
        )
        lines += [
            f"  {n:6d}  {g}"
            for g, n in sorted(group_counts(paths, depth).items())
        ]
        lines += [f"  first {min(show, len(paths))}:"] + [
            f"    {p}" for p in paths[:show]
        ]
    if predicted is not None:
        lines.append(
            f"predicted-equal: {len(predicted['defects'])} DEFECTS; "
            f"equal but not predicted: {len(predicted['unpredicted'])}"
        )
        lines += [f"  DEFECT {p}" for p in predicted["defects"][:show]]
    return lines


def main(argv: list[str] | None = None) -> int:
    """Run the command line and return the exit code (0, 1 or 2)."""
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
            patterns = [
                ln.strip()
                for ln in args.predicted_equal.read_text().splitlines()
                if ln.strip() and not ln.lstrip().startswith("#")
            ]
        result = compare(a, b)
        predicted = (
            check_predicted(result, patterns) if patterns is not None else None
        )
    except (OSError, ValueError, re.error) as exc:
        print(f"leafdiff: error: {exc}", file=sys.stderr)
        return 2
    print(
        "\n".join(
            report(
                str(args.a),
                str(args.b),
                a,
                b,
                result,
                args.group_depth,
                args.show,
                predicted,
            )
        )
    )
    bad = (
        result["different"]
        or result["added"]
        or result["removed"]
        or (predicted is not None and predicted["defects"])
    )
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
