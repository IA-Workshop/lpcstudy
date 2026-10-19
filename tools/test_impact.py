#!/usr/bin/env python3
"""Blast-radius test selection (DEVELOPMENT_WORKFLOW.md 4.2, WU-0011).

The study's test discipline says: after a change, run only the tests that the
change can affect (the "blast radius"), never the whole suite. This tool finds
that set. It reads the change set (``git diff --name-only <base>...HEAD`` plus
the working tree) and the import graph of ``lpcstudy/`` (which module imports
which), applies the mapping table of section 4.2, prints the selected tests
with the exact command, and with ``--run`` executes them once per CPU tier.

Safety rules built in: it never selects ``slow`` or ``gpu`` tests unless
``--include-slow`` or ``--include-gpu`` is given (each excluded file is
printed), it never runs the ``gpu`` tier, and it never builds a command that
could run the whole suite. The hook ``.claude/hooks/test_gate.py`` cannot see
this tool's subprocess, so the tool is its own guard (``pytest_commands``
raises ``ValueError``). The ``/test-impact`` skill calls it; nothing in
``lpcstudy/`` imports it. The tests are in
``tests/unit/test_tools_test_impact.py``.

Standard library only.

Exit codes: 0 when the selection was printed (or the run passed); pytest's own
code with ``--run`` on a failure; 2 for a usage or environment error (not a git
repository, missing base, a module that does not parse).
"""

from __future__ import annotations

import argparse
import ast
import os
import shlex
import subprocess
import sys
from collections import deque
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path

PACKAGE = "lpcstudy"
CORE_MODULES = frozenset(
    {
        "config",
        "data",
        "systems",
        "dynamics",
        "statistics",
        "ensemble",
        "oracle",
    }
)
PIPELINE_MODULES = frozenset({"pipeline", "experiments", "report", "__main__"})
CPU_TIERS = ("unit", "integration", "slow")
ALL_TIERS = (*CPU_TIERS, "gpu")
NO_TEST_FILES = frozenset(
    {"README.md", "ROADMAP.md", "DEVELOPMENT_WORKFLOW.md", "seeds/README.md"}
)
NO_TEST_DIRS = ("docs/", ".claude/")
# Data files read by a tool (its template and constants): the tool's test file
# covers them, so an edit to one of them selects that test and nothing else.
TOOL_DATA_TESTS = {
    "tools/findings/": "tests/unit/test_tools_findings_build.py",
}
WHOLE_SUITE = frozenset({"", ".", "./", "tests", "tests/"})
PYTEST_FLAGS = ("-q", "--tb=short", "-rfE")
SEEDS_TESTS = (
    "tests/unit/test_seeds.py",
    "tests/integration/test_cli_seeds.py",
)
# A test whose text holds one of these reads the package source or its
# hand-written import graph (``PACKAGE.glob("*.py")``, ``lpcstudy_graph.json``):
# any change to a ``lpcstudy/*.py`` file can change what it sees (DEF-0016,
# scan-the-source rule).
SCAN_MARKERS = ('glob("*.py")', "glob('*.py')", "lpcstudy_graph.json")


class ToolError(Exception):
    """A usage or environment error.

    ``main`` reports it and exits with code 2.
    """


@dataclass
class Selection:
    """The result of ``select``: which tests to run, and why.

    Attributes
    ----------
    tiers : dict[str, list[str]]
        Selected paths (files, or a tier directory) per tier, sorted and
        without duplicates.
    reasons : dict[str, list[str]]
        Per changed file, one ``rule -> paths`` text for each rule that
        applied.
    warnings : list[str]
        Warnings, without the ``warning:`` prefix.
    excluded : list[tuple[str, str]]
        ``(tier, path)`` of slow or gpu files that the rules reach but the
        flags withhold.
    """

    tiers: dict[str, list[str]]
    reasons: dict[str, list[str]] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    excluded: list[tuple[str, str]] = field(default_factory=list)


# ----------------------------------------------------------------------- graph


def _edge_targets(node: ast.AST, package: Path) -> list[str]:
    """Return the ``lpcstudy`` modules that one import statement names.

    The edge rules are listed in ``build_graph``.
    """
    name = package.name
    targets: list[str] = []

    def from_names(names: list[ast.alias]) -> None:
        for alias in names:
            exists = (package / f"{alias.name}.py").is_file()
            targets.append(alias.name if exists else "__init__")

    if isinstance(node, ast.ImportFrom):
        parts = (node.module or "").split(".") if node.module else []
        if node.level == 1:
            if parts:
                targets.append(parts[0])
            else:
                from_names(node.names)
        elif node.level == 0 and parts and parts[0] == name:
            if len(parts) > 1:
                targets.append(parts[1])
            else:
                from_names(node.names)
    elif isinstance(node, ast.Import):
        for alias in node.names:
            parts = alias.name.split(".")
            if parts[0] == name and len(parts) > 1:
                targets.append(parts[1])
    return targets


def build_graph(package_dir: str | Path) -> dict[str, list[str]]:
    """Build the import graph of a package from its source text.

    The graph says, for each module, which other modules of the package it
    imports. Every ``<package_dir>/*.py`` is parsed with ``ast`` (Python's
    syntax-tree module) and the whole tree is walked, so imports inside
    functions, classes, ``if`` and ``try`` blocks count too. Edge rules:
    ``from .x import y`` and ``from .x.y import z`` give ``x``;
    ``from . import x`` gives ``x`` when ``x.py`` exists and ``__init__``
    otherwise; ``import lpcstudy.x``, ``from lpcstudy.x import y`` and
    ``from lpcstudy import x`` give ``x``. Two-dot, third-party and
    standard-library imports and self-edges give none. The implicit import of
    ``__init__`` by every submodule is not an edge.

    Parameters
    ----------
    package_dir : str or Path
        The package directory.

    Returns
    -------
    dict[str, list[str]]
        Module stem to the sorted, deduplicated stems it imports directly.

    Raises
    ------
    ToolError
        If the directory is missing or a module has a syntax error (named,
        never skipped).
    """
    package = Path(package_dir)
    if not package.is_dir():
        raise ToolError(f"package directory not found: {package}")
    graph: dict[str, list[str]] = {}
    for path in sorted(package.glob("*.py")):
        try:
            tree = ast.parse(path.read_text(), filename=str(path))
        except SyntaxError as error:
            raise ToolError(f"syntax error in {path}: {error}") from error
        found = {
            t for node in ast.walk(tree) for t in _edge_targets(node, package)
        }
        graph[path.stem] = sorted(found - {path.stem})
    return graph


# ------------------------------------------------------------------------- git


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run git in ``root`` and return the completed process.

    A bad exit code does not raise; the caller checks ``returncode``.
    """
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def changed_files(root: str | Path, base: str) -> list[str]:
    """Return the change set of the current branch.

    The set holds the commits on the branch, staged files, unstaged files and
    untracked files. It is the union of
    ``git diff --name-only --no-renames <base>...HEAD``
    and ``git status --porcelain=v1 -z --untracked-files=all --no-renames``.
    A rename gives both paths and a deletion is kept.

    Parameters
    ----------
    root : str or Path
        The repository top-level directory.
    base : str
        The base revision (``main``). It must exist; there is no fallback,
        because a guessed base could select too few tests.

    Returns
    -------
    list[str]
        Sorted, deduplicated POSIX paths relative to ``root``.

    Raises
    ------
    ToolError
        If ``root`` is not a git top-level, the base does not exist, or git
        fails.
    """
    root = Path(root).resolve()
    top = _git(root, "rev-parse", "--show-toplevel")
    if top.returncode != 0:
        raise ToolError(f"not a git repository: {root}")
    if Path(top.stdout.strip()).resolve() != root:
        raise ToolError(
            f"{root} is not the top-level directory of its git repository"
        )
    if (
        _git(
            root, "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}"
        ).returncode
        != 0
    ):
        raise ToolError(f"base '{base}' not found")
    diff = _git(
        root, "diff", "--name-only", "--no-renames", "-z", f"{base}...HEAD"
    )
    status = _git(
        root,
        "status",
        "--porcelain=v1",
        "-z",
        "--untracked-files=all",
        "--no-renames",
    )
    for done in (diff, status):
        if done.returncode != 0:
            raise ToolError(f"git failed: {done.stderr.strip()}")
    paths = {entry for entry in diff.stdout.split("\0") if entry}
    paths |= {
        entry[3:] for entry in status.stdout.split("\0") if len(entry) > 3
    }
    return sorted(paths)


# ---------------------------------------------------------------------- select


def _dependents(
    reverse: Mapping[str, Iterable[str]], module: str, transitive: bool
) -> list[str]:
    """Return the modules that import ``module``, directly or transitively.

    The search is breadth-first and safe on import cycles.
    """
    seen, found, queue = {module}, [], deque([module])
    while queue:
        for dependent in reverse.get(queue.popleft(), ()):
            if dependent not in seen:
                seen.add(dependent)
                found.append(dependent)
                if transitive:
                    queue.append(dependent)
    return sorted(found)


def _exists(root: Path, relative: str) -> list[str]:
    """Return ``[relative]`` if the file exists under ``root``, else ``[]``."""
    return [relative] if (root / relative).is_file() else []


def _convention(root: Path, tier: str, module: str) -> list[str]:
    """Return the tier's ``test_<m>.py`` and ``test_<m>_*.py`` files.

    Only files that exist are returned, as ``tests/<tier>/...`` paths.
    """
    folder = root / "tests" / tier
    names = {p.name for p in folder.glob(f"test_{module}.py")}
    names |= {p.name for p in folder.glob(f"test_{module}_*.py")}
    return [f"tests/{tier}/{name}" for name in sorted(names)]


def _test_files(root: Path) -> list[str]:
    """Return every ``tests/<tier>/**/test_*.py`` file, sorted.

    Paths are POSIX style and relative to ``root``.
    """
    found = []
    for tier in ALL_TIERS:
        folder = root / "tests" / tier
        found += [
            p.relative_to(root).as_posix() for p in folder.rglob("test_*.py")
        ]
    return sorted(found)


def scan_tests(
    root: Path, warnings: list[str]
) -> tuple[dict[str, set[str]], list[str]]:
    """Read every test file once for the two extra rules (DEF-0016).

    The rules are "direct import" (a test that imports a changed module is
    selected whatever its name) and "scan the source" (a test that reads the
    package text is selected for any package change).

    Direct imports are the absolute ``lpcstudy`` edges of ``_edge_targets``,
    found by walking the syntax tree of the test file at any nesting level
    (``import lpcstudy.m``, ``from lpcstudy.m import x``,
    ``from lpcstudy import m``). Strings, comments and ``importlib`` calls are
    not imports. A test file that does not parse is named in a warning and
    gets no imports (never skipped silently); relative imports in a test file
    do not name the package.

    Known gaps (the two rules are text based and import based, and the owner
    ratified them as such): a test that reads the source of one package file
    by path without importing it. There is a real case in the tree:
    ``tests/unit/test_budget.py`` reads ``lpcstudy/experiments.py`` with
    ``read_text`` and asserts that ``(200, m_draws)`` is in it, so a change to
    ``experiments.py`` alone selects it under neither rule. Another gap is a
    test that loads a module with ``importlib.import_module`` or reads its
    text with ``inspect.getsource``. For these, planners add the test by hand:
    ``test_budget.py`` when ``experiments.py`` changes (DEF-0016 status line
    2026-10-12). No third marker is added here, because it would widen the
    rules beyond what the owner ratified.

    Returns
    -------
    tuple
        ``(imports, scanners)``: the set of package modules each test file
        imports directly, and the test files whose text holds a
        ``SCAN_MARKERS`` entry.
    """
    package = root / PACKAGE
    imports: dict[str, set[str]] = {}
    scanners: list[str] = []
    for path in _test_files(root):
        text = (root / path).read_text(errors="replace")
        if any(marker in text for marker in SCAN_MARKERS):
            scanners.append(path)
        if PACKAGE not in text:
            continue
        try:
            tree = ast.parse(text, filename=path)
        except SyntaxError as error:
            warnings.append(
                f"syntax error in {path}: "
                f"its imports of {PACKAGE} cannot be read "
                f"({error.msg}, line {error.lineno})"
            )
            continue
        found: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import) or (
                isinstance(node, ast.ImportFrom) and node.level == 0
            ):
                found.update(_edge_targets(node, package))
        if found:
            imports[path] = found
    return imports, scanners


def _tier_of(path: str) -> str | None:
    """Return the tier of a ``tests/<tier>/...`` path, or None.

    The tier is the first directory under ``tests/``.
    """
    parts = Path(path).parts
    if len(parts) > 2 and parts[0] == "tests" and parts[1] in ALL_TIERS:
        return parts[1]
    return None


def _module_paths(
    module: str,
    graph: Mapping[str, list[str]],
    reverse: Mapping[str, list[str]],
    root: Path,
    core: frozenset[str],
    warnings: list[str],
) -> tuple[str, list[str]]:
    """Return the rule text and test paths for a changed package module.

    Core modules also select their transitive dependents and the integration
    tier; pipeline modules select direct dependents and the integration tier;
    any other module selects its own test and its direct dependents' tests.
    """
    own = _exists(root, f"tests/unit/test_{module}.py")
    if not own:
        warnings.append(f"no test file for {PACKAGE}/{module}.py")
    if module == "__init__":
        warnings.append(
            "package __init__ changed: "
            "its implicit import by every module is not "
            "in the graph"
        )
    integration = (
        ["tests/integration"]
        if (root / "tests" / "integration").is_dir()
        else []
    )
    if module in core:
        rule, depth, extra = (
            "core module: own + transitive dependents + integration",
            True,
            True,
        )
    elif module in PIPELINE_MODULES:
        rule, depth, extra = (
            "pipeline module: own + direct dependents + integration",
            False,
            True,
        )
    else:
        rule, depth, extra = "module: own + direct dependents", False, False
    paths = list(own)
    for dependent in _dependents(reverse, module, depth):
        paths += _exists(root, f"tests/unit/test_{dependent}.py")
    if extra:
        if not integration:
            warnings.append("tests/integration does not exist")
        paths += integration
    return rule, paths


def _helper_paths(
    path: str, tier: str, root: Path, warnings: list[str]
) -> list[str]:
    """Return the tier's test files whose text names the stem of a helper.

    A helper is a non-test file under ``tests/<tier>/``, such as a shared
    fixture module.
    """
    stem = Path(path).stem
    found = []
    for candidate in sorted((root / "tests" / tier).rglob("test_*.py")):
        if stem in candidate.read_text(errors="replace"):
            found.append(candidate.relative_to(root).as_posix())
    warnings.append(
        f"non-test file {path}: selected the {tier} tests that name '{stem}'"
        if found
        else f"non-test file {path}: no {tier} test names '{stem}'"
    )
    return found


def _map_file(
    path: str,
    graph: Mapping[str, list[str]],
    reverse: Mapping[str, list[str]],
    root: Path,
    core: frozenset[str],
    warnings: list[str],
) -> tuple[str, list[str]]:
    """Map one changed file to ``(rule text, test paths)`` (section 4.2)."""
    parts = Path(path).parts
    if path in NO_TEST_FILES or path.startswith(NO_TEST_DIRS):
        return "no tests (docs, .claude, readme)", []
    if path in {"pytest.ini", "tests/conftest.py"}:
        warnings.append(
            f"{path} changed: gate-sized run (whole unit tier); "
            "record it in the log"
        )
        return "test configuration: whole unit tier", ["tests/unit"]
    if path == "requirements.txt":
        warnings.append(
            "requirements.txt changed: gate-sized run (whole unit tier plus "
            "integration); run once by the main session; recorded decision "
            "(LPC.PC.17)"
        )
        return "requirements: unit tier + integration", [
            "tests/unit",
            "tests/integration",
        ]
    if path == "seeds/development_seeds.json":
        missing = [name for name in SEEDS_TESTS if not (root / name).is_file()]
        warnings += [f"{name} does not exist ({path})" for name in missing]
        return "seeds file: the two seed tests", [
            n for n in SEEDS_TESTS if n not in missing
        ]
    if (
        len(parts) == 2
        and parts[0] == "tools"
        and path.endswith((".py", ".sh"))
    ):
        test = f"tests/unit/test_tools_{Path(path).stem}.py"
        if not (root / test).is_file():
            warnings.append(f"{path} has no test ({test})")
        return "tool: its test file", _exists(root, test)
    for prefix, test in TOOL_DATA_TESTS.items():
        if path.startswith(prefix):
            return "tool data file: its tool's test file", _exists(root, test)
    tier = _tier_of(path)
    if (
        tier is not None
        and Path(path).name.startswith("test_")
        and path.endswith(".py")
    ):
        return "test file: that file only", _exists(root, path)
    if tier is not None:
        return "test helper: tests naming it", _helper_paths(
            path, tier, root, warnings
        )
    if len(parts) == 2 and parts[0] == PACKAGE and path.endswith(".py"):
        return _module_paths(
            Path(path).stem, graph, reverse, root, core, warnings
        )
    warnings.append(f"unmapped file {path}: default rule used")
    stem = Path(path).stem
    paths = _exists(root, f"tests/unit/test_{stem}.py")
    for dependent in _dependents(reverse, stem, False):
        paths += _exists(root, f"tests/unit/test_{dependent}.py")
    return "default: own test + direct dependents", paths


def select(
    changed: Iterable[str],
    graph: Mapping[str, list[str]],
    root: str | Path,
    core: frozenset[str],
    include_slow: bool,
    include_gpu: bool,
) -> Selection:
    """Select the tests a change set can affect (DEVELOPMENT_WORKFLOW.md 4.2).

    For a changed ``lpcstudy/<m>.py`` two rules add to the table of 4.2
    (WU-0011.5, DEF-0016): a test file that imports ``<m>`` directly is
    selected whatever its name (``scan_tests``), and a test that scans the
    package source or the graph fixture (``SCAN_MARKERS``) is selected for any
    change to a ``lpcstudy/*.py`` file. Slow and gpu files they reach follow
    the flags.

    Parameters
    ----------
    changed : iterable of str
        Changed paths relative to ``root`` (POSIX).
    graph : mapping
        Import graph from ``build_graph``.
    root : str or Path
        Repository root, where test files are looked up.
    core : frozenset of str
        Core module names.
    include_slow, include_gpu : bool
        Whether slow or gpu tests that the rules reach are selected, or only
        listed as excluded.

    Returns
    -------
    Selection
        Paths per tier, reasons per changed file, warnings and exclusions.
    """
    root = Path(root)
    reverse: dict[str, list[str]] = {}
    for module, imports in graph.items():
        for target in imports:
            reverse.setdefault(target, []).append(module)
    warnings: list[str] = []
    reasons: dict[str, list[str]] = {}
    wanted: set[str] = set()
    changed = sorted(set(changed))
    is_module = [
        len(Path(p).parts) == 2
        and p.startswith(f"{PACKAGE}/")
        and p.endswith(".py")
        for p in changed
    ]
    imports, scanners = (
        scan_tests(root, warnings) if any(is_module) else ({}, [])
    )

    def visible(paths: Iterable[str]) -> str:
        """Return the paths the flags let through, as the reason text prints."""
        kept = [
            p
            for p in paths
            if _tier_of(p) not in ("slow", "gpu")
            or (_tier_of(p) == "slow" and include_slow)
            or (_tier_of(p) == "gpu" and include_gpu)
        ]
        return " ".join(sorted(set(kept))) or "nothing"

    for path, module_file in zip(changed, is_module):
        rule, paths = _map_file(path, graph, reverse, root, core, warnings)
        if not (root / path).exists():
            warnings.append(f"{path} is deleted; mapped by name")
        extra: list[tuple[str, list[str]]] = []
        if module_file:
            module = Path(path).stem
            paths = [
                *paths,
                *_convention(root, "slow", module),
                *_convention(root, "gpu", module),
            ]
            extra = [
                (
                    "direct import: tests importing the module",
                    [t for t, found in imports.items() if module in found],
                ),
                (
                    "scan the source: tests reading the package text",
                    list(scanners),
                ),
            ]
        wanted.update(paths)
        reasons.setdefault(path, []).append(f"{rule} -> {visible(paths)}")
        for text, more in extra:
            wanted.update(more)
            reasons[path].append(f"{text} -> {visible(more)}")
    tiers: dict[str, list[str]] = {tier: [] for tier in ALL_TIERS}
    excluded: list[tuple[str, str]] = []
    for path in sorted(wanted):
        tier = path.split("/")[1]
        if (tier == "slow" and not include_slow) or (
            tier == "gpu" and not include_gpu
        ):
            excluded.append((tier, path))
        else:
            tiers[tier].append(path)
    for (
        tier,
        paths,
    ) in tiers.items():  # a selected tier directory covers the files inside it
        directories = [p for p in paths if p == f"tests/{tier}"]
        if directories:
            tiers[tier] = directories
    return Selection(tiers, reasons, list(dict.fromkeys(warnings)), excluded)


# -------------------------------------------------------------------- commands


def run_environment(base: Mapping[str, str] | None = None) -> dict[str, str]:
    """Return the environment of a test run.

    The run is forced onto the CPU, JAX is told not to grab memory in
    advance, and the thread count is capped.

    Parameters
    ----------
    base : mapping, optional
        Starting environment (default ``os.environ``). ``LPC_THREADS`` is
        kept or set to 4 and copied to the OMP, MKL and OpenBLAS thread
        variables.
    """
    env = dict(os.environ if base is None else base)
    env["JAX_PLATFORMS"] = "cpu"
    env["XLA_PYTHON_CLIENT_PREALLOCATE"] = "false"
    env.setdefault("LPC_THREADS", "4")
    for name in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
        env[name] = env["LPC_THREADS"]
    return env


def pytest_commands(selection: Selection, root: str | Path) -> list[list[str]]:
    """Return one argument list per CPU tier that has paths.

    The order is unit, integration, slow. The command is
    ``tools/run_tests.sh <tier> <paths>`` when the wrapper exists, else
    ``python -m pytest -q --tb=short -rfE <paths>``. The gpu tier is never run
    here.

    Raises
    ------
    ValueError
        If no CPU tier has a path, or a path would run the whole suite
        (``tests``, ``.``).
    """
    wrapper = Path(root) / "tools" / "run_tests.sh"
    commands = []
    for tier in CPU_TIERS:
        paths = selection.tiers.get(tier, [])
        if not paths:
            continue
        bad = [p for p in paths if p.rstrip("/") in WHOLE_SUITE]
        if bad:
            raise ValueError(
                f"refusing a whole-suite path in the {tier} tier: {bad}"
            )
        if wrapper.is_file():
            commands.append([str(wrapper), tier, *paths])
        else:
            commands.append(
                [sys.executable, "-m", "pytest", *PYTEST_FLAGS, *paths]
            )
    if not commands:
        raise ValueError("refusing to build a command with an empty path list")
    return commands


# ------------------------------------------------------------------------ main


def main(argv: list[str] | None = None) -> int:
    """Print the selection for the current change set.

    With ``--run``, also run it tier by tier and stop at the first failure.
    """
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--base", default="main", help="base revision (default main)"
    )
    parser.add_argument(
        "--explain", action="store_true", help="print the rule for each file"
    )
    parser.add_argument(
        "--run", action="store_true", help="run the selection (CPU tiers)"
    )
    parser.add_argument("--include-slow", action="store_true")
    parser.add_argument("--include-gpu", action="store_true")
    parser.add_argument(
        "--root", default=str(Path(__file__).resolve().parents[1])
    )
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    try:
        changed = changed_files(root, args.base)
        graph = build_graph(root / PACKAGE)
    except ToolError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    selection = select(
        changed, graph, root, CORE_MODULES, args.include_slow, args.include_gpu
    )
    if args.explain:
        for path, texts in selection.reasons.items():
            for text in texts:
                print(f"{path} -> {text}")
    for tier in ALL_TIERS:
        if selection.tiers[tier]:
            print(f"{tier}: {' '.join(selection.tiers[tier])}")
    for warning in selection.warnings:
        print(f"warning: {warning}")
    for tier, path in selection.excluded:
        print(f"excluded ({tier}): {path} (use --include-{tier})")
    if not any(selection.tiers.values()):
        print("no tests")
        return 0
    if not any(selection.tiers[tier] for tier in CPU_TIERS):
        print(
            "no CPU tests to run "
            "(gpu files are printed, never run by this tool)"
        )
        return 0
    commands = pytest_commands(selection, root)
    for command in commands:
        print("command: " + shlex.join(command))
    if args.run:
        env = run_environment()
        for command in commands:
            code = subprocess.run(
                command, cwd=root, env=env, check=False
            ).returncode
            if code != 0:
                return code
    return 0


if __name__ == "__main__":
    sys.exit(main())
