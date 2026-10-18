#!/usr/bin/env python3
"""Extract the float-leaf PATH SHAPES of pilot results into small committed fixtures (WU-0003.9b).

What this script does for the study
-----------------------------------
A pilot run writes one big ``results.json``: a tree of numbers. The tool
``tools/compare_runs.py`` compares two such trees number by number, and each
number (a *leaf* of the tree, found by its *path* of keys) must carry a *tag*
that says how to compare it (for example, which chain of the study it belongs
to). A test checks that no floating-point leaf of the pilot results is left
without a tag. That test needs the list of leaf paths, but the full results
files are large and are not committed. This script reads them once and writes
small text files that hold the paths only, never the values, so they are safe
and small to commit. The tests under ``tests/unit/`` read those text files.

DEVELOPMENT (DEV-0): not a hypothesis test. The script reads ``results.json``
files read-only and writes **paths only, no values**.

What a "shape" is
-----------------
A shape is a leaf path with every list index written ``[]`` and the system
name written ``<sys>`` (at ``systems/<s>``, ``robustness/<s>``,
``handling/by_system/<s>`` and ``handling/robustness/<s>``). All other keys
(noise levels, library sizes, cell ids, estimator keys) are kept as they are.
The tags in ``tools/compare_pilot.py`` and ``tools/compare_runs.py`` are
indexed by the same wildcards (``[]`` and ``systems/*``), so one shape decides
the tag of every leaf it stands for. The test expands a shape to a concrete
path by ``[]`` -> ``[0]`` and ``<sys>`` -> ``lorenz63``.

The output format
-----------------
Each line is ``<shape><TAB><chain before>``. "Chain before" is the chain tag
the tool assigned to the leaf BEFORE WU-0003.9b (tip ``d63677d`` of
``wu/0003-rehearsal``). It is the chain of the leaf in the rule table of
``tools/compare_pilot.py`` (empty means untagged), except that it is ``cp``
for the two H1a leaves that ``compare_runs`` then overrode
(``inverse_dim_reference`` and ``median_seed_by_n_lib/*``; ``cp`` is the
analog forecaster). The script computes it from the unchanged table plus that
one inline rule, so running the script again reproduces the files. These files
are the reference for the test "no existing tag changed" (t2). That test is a
regression guard (it detects change); it is not evidence that the tags are
correct.

Which leaves are kept
---------------------
Float leaves are JSON floats (``type(v) is float``). The top-level
``provenance`` block and the ``seconds`` keys (wall-clock time, which differs
on every run) are excluded, as ``tools/compare_runs.py`` excludes them.
``config`` is kept, because its floats need a tag, too.

Usage::

    python3 -I extract_paths.py OUT_P1 OUT_P0_SMOKE --p1 P1.json --p0 P0.json --smoke SMOKE.json

with ``P1`` = ``lpcstudy-wt/run/p1-5b3fd8f/runs/dev/p1/pilot/results.json``
(lpcstudy 5b3fd8f), ``P0`` =
``lpcstudy-wt/run/p0-1b20db9/runs/dev/p0/pilot/results.json`` (1b20db9) and
``SMOKE`` =
``lpcstudy-wt/run/wu0003-7c-tip/runs/wu0003-7c-tip/smoke/results.json`` (the
smoke preset, a quick plumbing run, at the WU-0003.7c tip, which has every
leaf of .7a, .7b and .7c; the state dump is a separate ``states/*.npz``).
``OUT_P1`` holds the shapes of P1; ``OUT_P0_SMOKE`` holds the union of the
shapes of P0 and the smoke run.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SYSTEMS = ("lorenz63", "rossler", "chua")


def load_pilot_tool():
    """Load ``tools/compare_pilot.py`` as a module and return it.

    The script needs two things from it: ``flatten`` (turns a results tree
    into a path -> value dictionary) and the unchanged rule table that maps a
    path to its chain tag. The tool is loaded from its file because ``tools/``
    is not an importable package.
    """
    spec = importlib.util.spec_from_file_location(
        "compare_pilot", ROOT / "tools" / "compare_pilot.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["compare_pilot"] = module
    spec.loader.exec_module(module)
    return module


def shape_of(path: tuple[str, ...]) -> str:
    """Return the shape text of a leaf path.

    List indices become ``[]``, a system name in one of the four places named
    in the module docstring becomes ``<sys>``, and the segments are joined
    with ``/``.
    """
    segs = list(path)
    where = None
    if segs[0] in ("systems", "robustness") and len(segs) > 1:
        where = 1
    elif (
        segs[0] == "handling"
        and len(segs) > 2
        and segs[1] in ("by_system", "robustness")
    ):
        where = 2
    if where is not None and segs[where] in SYSTEMS:
        segs[where] = "<sys>"
    return "/".join("[]" if re.fullmatch(r"\[\d+\]", s) else s for s in segs)


def chain_before(cp, path: tuple[str, ...]) -> str:
    """Return the chain tag of a leaf as it was before WU-0003.9b.

    This is the tag from the rule table, or the empty string if the table has
    no rule for the path. The one exception is the two H1a groups that
    ``compare_runs`` overrode (``inverse_dim_reference`` and
    ``median_seed_by_n_lib``), which get ``cp``.
    """
    try:
        chain = cp.TABLE.classify(path).chain
    except cp.ToolError:
        chain = ""
    if (
        not chain
        and "H1a" in path
        and (
            path[-1] == "inverse_dim_reference"
            or "median_seed_by_n_lib" in path
        )
    ):
        return "cp"
    return chain


def float_shapes(cp, source: Path) -> dict[str, str]:
    """Map each shape to its chain-before tag for one results file.

    Only float leaves count (see the module docstring). Two leaves with the
    same shape must have the same chain; if they do not, the shape notation
    would lose information, so the script stops with an error instead.
    """
    out: dict[str, str] = {}
    for path, value in cp.flatten(json.loads(source.read_text())).items():
        if (
            type(value) is not float
            or path[0] == "provenance"
            or "seconds" in path
        ):
            continue
        shape, chain = shape_of(path), chain_before(cp, path)
        if out.setdefault(shape, chain) != chain:
            raise SystemExit(
                f"{source}: shape {shape!r} has two chains: {out[shape]!r} and {chain!r}"
            )
    return out


def write(dst: Path, shapes: dict[str, str], sources: list[Path]) -> None:
    """Write one fixture file.

    The file has a header that names each source file and its SHA-256 hash
    (a fingerprint that shows which exact file the shapes came from),
    followed by the sorted shapes, one per line.
    """
    lines = [
        "# DEVELOPMENT (DEV-0): paths only, no values. WU-0003.9b. See extract_paths.py for the format.",
        "# columns: shape TAB chain tag before WU-0003.9b (empty: untagged)",
    ]
    for source in sources:
        lines.append(
            f"# source {'/'.join(source.parts[-6:])}: "
            f"sha256 {hashlib.sha256(source.read_bytes()).hexdigest()}"
        )
    lines += [f"{shape}\t{chain}" for shape, chain in sorted(shapes.items())]
    dst.write_text("\n".join(lines) + "\n")


def main(argv: list[str] | None = None) -> int:
    """Command-line entry: write the two fixture files and print counts.

    The printed line gives, for each output, the number of shapes and how many
    of them were untagged before WU-0003.9b. Returns the exit code, 0.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("out_p1", type=Path)
    ap.add_argument("out_p0_smoke", type=Path)
    ap.add_argument("--p1", type=Path, required=True)
    ap.add_argument("--p0", type=Path, required=True)
    ap.add_argument("--smoke", type=Path, required=True)
    args = ap.parse_args(argv)
    cp = load_pilot_tool()
    p1 = float_shapes(cp, args.p1)
    union: dict[str, str] = {}
    for source in (args.p0, args.smoke):
        for shape, chain in float_shapes(cp, source).items():
            if union.setdefault(shape, chain) != chain:
                raise SystemExit(
                    f"shape {shape!r} has two chains across P0 and the smoke"
                )
    write(args.out_p1, p1, [args.p1])
    write(args.out_p0_smoke, union, [args.p0, args.smoke])
    print(
        f"P1: {len(p1)} shapes ({sum(1 for c in p1.values() if not c)} untagged before); "
        f"P0 + smoke: {len(union)} shapes ({sum(1 for c in union.values() if not c)} untagged before)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
