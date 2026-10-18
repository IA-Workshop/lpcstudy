#!/usr/bin/env python3
"""Extract the float-leaf PATH SHAPES of pilot results into small committed fixtures (WU-0003.9b).

DEVELOPMENT (DEV-0): not a hypothesis test. Reads ``results.json`` files read-only and writes
**paths only, no values**. A "shape" is a leaf path with every list index written ``[]`` and the
system name written ``<sys>`` (at ``systems/<s>``, ``robustness/<s>``, ``handling/by_system/<s>``
and ``handling/robustness/<s>``); all other keys (noise levels, library sizes, cell ids, estimator
keys) are kept as they are. Tags in ``tools/compare_pilot.py`` and ``tools/compare_runs.py`` are
indexed by the same wildcards (``[]`` and ``systems/*``), so a shape decides the tag of every leaf it
stands for; the test expands a shape to the concrete path ``[]`` -> ``[0]``, ``<sys>`` -> ``lorenz63``.

Each line is ``<shape><TAB><chain before>``. ``chain before`` is the chain tag the tool assigned to
the leaf BEFORE WU-0003.9b (tip ``d63677d`` of ``wu/0003-rehearsal``): the chain of the leaf in
``tools/compare_pilot.py``'s rule table (empty: untagged), and ``cp`` for the two H1a leaves that
``compare_runs`` then overrode (``inverse_dim_reference``, ``median_seed_by_n_lib/*``). It is computed
here from the unchanged table plus that one inline rule, so re-running this script reproduces it.
The files are the oracle of the "no existing tag changed" test (t2, a regression guard, not
correctness evidence).

Float leaves are JSON floats (``type(v) is float``). The top-level ``provenance`` block and the
``seconds`` keys (wall-clock) are excluded, as ``tools/compare_runs.py`` excludes them; ``config`` is
kept (its floats need a tag, too).

Usage::

    python3 -I extract_paths.py OUT_P1 OUT_P0_SMOKE --p1 P1.json --p0 P0.json --smoke SMOKE.json

with ``P1`` = ``lpcstudy-wt/run/p1-5b3fd8f/runs/dev/p1/pilot/results.json`` (lpcstudy 5b3fd8f),
``P0`` = ``lpcstudy-wt/run/p0-1b20db9/runs/dev/p0/pilot/results.json`` (1b20db9) and ``SMOKE`` =
``lpcstudy-wt/run/wu0003-7c-tip/runs/wu0003-7c-tip/smoke/results.json`` (the smoke preset at the
WU-0003.7c tip, which has every leaf of .7a, .7b (the dump is a separate ``states/*.npz``) and .7c).
``OUT_P1`` holds the shapes of P1; ``OUT_P0_SMOKE`` the union of the shapes of P0 and the smoke.
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
    """``tools/compare_pilot.py`` as a module (its flatten and its unchanged rule table)."""
    spec = importlib.util.spec_from_file_location(
        "compare_pilot", ROOT / "tools" / "compare_pilot.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["compare_pilot"] = module
    spec.loader.exec_module(module)
    return module


def shape_of(path: tuple[str, ...]) -> str:
    """The shape text of a leaf path (see the module docstring)."""
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
    """The chain tag of a leaf before WU-0003.9b: the table's, or ``cp`` for the two H1a overrides."""
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
    """Shape to chain-before of the float leaves of one results file."""
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
    """Write one fixture file (sorted shapes, a header that names the sources and their SHA-256)."""
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
    """Command-line entry."""
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
