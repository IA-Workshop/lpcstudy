"""Tests of ``tools/test_impact.py``, the blast-radius tool (WU-0011.1 and WU-0011.2).

Reference for every test: the mapping table and the dependency graph of DEVELOPMENT_WORKFLOW.md
section 4.2, applied by hand to a small synthetic package built in ``tmp_path`` (the expected
sets are written literally in each test), and, for the real package, the hand-derived fixture
``tests/unit/fixtures/lpcstudy_graph.json`` (the LPC.PC.21a reference, WU-0011.2). None of the
expectations comes from the tool's own output.

Tolerance: none. Every output is a discrete set of paths or an exit code, compared for exact
equality. The one numeric check is the runtime of the selection on the real package, whose
bound (1.0 s) is the acceptance criterion; the expected time is about 0.1 s.

No test starts pytest: the tool's subprocess calls are replaced by a recorder (git passes
through) so that the tool is checked for what it would run.
"""

from __future__ import annotations

import importlib.util
import json
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "unit" / "fixtures" / "lpcstudy_graph.json"

_SPEC = importlib.util.spec_from_file_location("test_impact", ROOT / "tools" / "test_impact.py")
assert _SPEC is not None and _SPEC.loader is not None
tool = importlib.util.module_from_spec(_SPEC)
sys.modules["test_impact"] = tool
_SPEC.loader.exec_module(tool)

CORE = frozenset({"base", "cyc"})
FILES = {
    "lpcstudy/__init__.py": "",
    "lpcstudy/base.py": "from .cyc import g\n\n\ndef f():\n    return g()\n",
    "lpcstudy/cyc.py": "from .base import f\n\n\ndef g():\n    return 1\n",
    "lpcstudy/leaf.py": "def h():\n    return 2\n",
    "lpcstudy/mid.py": ("from .base import f\n\n\ndef m():\n    from .leaf import h\n"
                        "    return h() + f()\n"),
    "lpcstudy/top.py": "from . import mid as m\nfrom .new import y\n",
    "lpcstudy/pipeline.py": "from .top import t\n",
    "tests/conftest.py": "",
    "tests/unit/test_base.py": "def test_a():\n    pass\n",
    "tests/unit/test_leaf.py": "def test_a():\n    pass\n",
    "tests/unit/test_mid.py": "def test_a():\n    pass\n",
    "tests/unit/test_top.py": "def test_a():\n    pass\n",
    "tests/unit/unit_helpers.py": "VALUE = 1\n",
    "tests/unit/test_uses_helper.py": "from unit_helpers import VALUE\n",
    "tests/integration/test_smoke.py": "def test_a():\n    pass\n",
    "tests/slow/test_base_coverage.py": "def test_a():\n    pass\n",
    "tests/gpu/test_mid_repro.py": "def test_a():\n    pass\n",
    "tools/foo.py": "X = 1\n",
    "tools/bar.sh": "echo bar\n",
    "tests/unit/test_tools_foo.py": "def test_a():\n    pass\n",
    "pytest.ini": "[pytest]\n",
    "requirements.txt": "numpy\n",
    "docs/x.md": "docs\n",
    ".claude/y.md": "agent\n",
    "README.md": "readme\n",
}
GRAPH = {  # written by hand from FILES plus the untracked `new.py` (written by the tests)
    "__init__": [], "base": ["cyc"], "cyc": ["base"], "leaf": [], "mid": ["base", "leaf"],
    "new": [], "pipeline": ["top"], "top": ["mid", "new"],
}
UNIT = "tests/unit/"


def git(repo: Path, *args: str) -> str:
    """Run git in ``repo`` with a fixed identity and no signing; return stdout."""
    base = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"]
    done = subprocess.run([*base, "-C", str(repo), *args], check=True, capture_output=True,
                          text=True)
    return done.stdout


def write(repo: Path, rel: str, text: str) -> None:
    """Write ``text`` to ``repo/rel``, creating directories."""
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A committed synthetic repository on ``main``; ``lpcstudy/new.py`` is not written."""
    for rel, text in FILES.items():
        write(tmp_path, rel, text)
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-q", "-m", "initial")
    return tmp_path


class Recorder:
    """Replace ``subprocess.run`` in the tool: git runs for real, anything else is recorded."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch, codes: list[int] | None = None) -> None:
        self.calls: list[tuple[list[str], dict | None]] = []
        self.codes = list(codes or [])
        real = subprocess.run

        def fake(argv, *args, **kwargs):  # noqa: ANN001, ANN202
            argv = list(argv)
            if argv[0] == "git":
                return real(argv, *args, **kwargs)
            self.calls.append((argv, kwargs.get("env")))
            return subprocess.CompletedProcess(argv, self.codes.pop(0) if self.codes else 0)

        monkeypatch.setattr(tool.subprocess, "run", fake)


def pick(repo: Path, changed: list[str], **kwargs: bool):  # noqa: ANN201
    """Build the graph of ``repo`` and select for ``changed`` with the synthetic core."""
    graph = tool.build_graph(repo / "lpcstudy")
    return tool.select(changed, graph, repo, CORE, kwargs.get("include_slow", False),
                       kwargs.get("include_gpu", False))


# ---------------------------------------------------------------------------------- graph


def test_graph_of_synthetic_package_equals_hand_written(repo: Path) -> None:
    """Function-level, ``from . import x as y``, cyclic and untracked-module edges are found.

    Reference: GRAPH, read by hand from the FILES strings above (``mid -> leaf`` exists only
    inside a ``def``; ``top -> mid`` only through ``from . import mid as m``). No tolerance.
    """
    write(repo, "lpcstudy/new.py", "")
    assert tool.build_graph(repo / "lpcstudy") == GRAPH


def test_graph_edge_forms(tmp_path: Path) -> None:
    """Every import form of the plan's edge rules, with the non-edges.

    Reference: the rules of the WU-0011 plan, applied by hand to the source of module ``m``
    below. Edges: one-dot and sub-module imports (``.a.sub`` -> a), ``from . import b`` (b.py
    exists), ``from . import ghost`` (no ghost.py -> ``__init__``), the absolute forms
    ``import lpcstudy.c``, ``import lpcstudy.d.deep``, ``from lpcstudy import e``, and imports
    nested in ``try``, ``if``, ``def`` and ``class`` (here ``f``, ``g``, ``h``). Non-edges: two
    dots, third-party and standard library, bare ``import lpcstudy``, and the self-import
    ``from .m import me``. No tolerance.
    """
    pkg = tmp_path / "lpcstudy"
    for name in ("__init__", "a", "b", "c", "d", "e", "f", "g", "h"):
        write(pkg, f"{name}.py", "")
    write(pkg, "m.py", (
        "import numpy\nimport os.path\nfrom json import dumps\nfrom ..a import z\n"
        "from .a.sub import q\nfrom . import b as bb, ghost\nimport lpcstudy.c\n"
        "import lpcstudy.d.deep\nfrom lpcstudy import e\nimport lpcstudy\nfrom .m import me\n"
        "try:\n    from .f import w\nexcept ImportError:\n    pass\n"
        "if True:\n    from .g import v\n"
        "class K:\n    def meth(self):\n        from .h import u\n"))
    graph = tool.build_graph(pkg)
    assert graph["m"] == ["__init__", "a", "b", "c", "d", "e", "f", "g", "h"]
    assert all(deps == [] for name, deps in graph.items() if name != "m")


def test_graph_syntax_error_is_named_not_skipped(tmp_path: Path) -> None:
    """A module that does not parse raises an error naming it (PRIME.4), exit code 2 via main.

    Reference: Python's grammar; ``def (`` is invalid. No tolerance.
    """
    write(tmp_path, "lpcstudy/broken.py", "def (\n")
    with pytest.raises(tool.ToolError, match="broken.py"):
        tool.build_graph(tmp_path / "lpcstudy")


# ------------------------------------------------------------------------ the criteria a-g


def test_a_leaf_change_selects_own_and_direct_dependents(repo: Path) -> None:
    """(a) ``leaf`` -> its file and ``mid``'s file; the only edge is the function-level import.

    Reference: section 4.2 row 1 on GRAPH: dependents of leaf = {mid}. Exact set equality.
    """
    sel = pick(repo, ["lpcstudy/leaf.py"])
    assert sel.tiers["unit"] == [UNIT + "test_leaf.py", UNIT + "test_mid.py"]
    assert sel.tiers["integration"] == [] and sel.tiers["slow"] == [] and sel.tiers["gpu"] == []
    assert sel.warnings == []


def test_b_core_change_selects_transitive_dependents_and_integration(repo: Path) -> None:
    """(b) core ``base`` -> own, mid, top (transitive, through ``from . import mid``) + integration.

    Reference: section 4.2 row 2 on GRAPH: dependents of base = {cyc, mid, top, pipeline}
    (the cycle base <-> cyc terminates); unit files exist for base, mid, top only. The slow file
    is excluded by default and added by ``include_slow``. Exact set equality.
    """
    sel = pick(repo, ["lpcstudy/base.py"])
    assert sel.tiers["unit"] == [UNIT + "test_base.py", UNIT + "test_mid.py",
                                 UNIT + "test_top.py"]
    assert sel.tiers["integration"] == ["tests/integration"]
    assert sel.tiers["slow"] == []
    assert ("slow", "tests/slow/test_base_coverage.py") in sel.excluded
    with_slow = pick(repo, ["lpcstudy/base.py"], include_slow=True)
    assert with_slow.tiers["slow"] == ["tests/slow/test_base_coverage.py"]
    assert with_slow.excluded == []


def test_pipeline_module_selects_own_dependents_and_integration(repo: Path) -> None:
    """The pipeline class: own file, direct dependents' files, integration (section 4.2 row 3).

    Reference: GRAPH has no dependent of ``pipeline`` and no ``test_pipeline.py`` exists, so the
    selection is integration alone, with the no-test-file warning. Exact equality.
    """
    sel = pick(repo, ["lpcstudy/pipeline.py"])
    assert sel.tiers["unit"] == []
    assert sel.tiers["integration"] == ["tests/integration"]
    assert "no test file for lpcstudy/pipeline.py" in sel.warnings


def test_c_docs_and_agent_changes_select_nothing(repo: Path, monkeypatch, capsys) -> None:  # noqa: ANN001
    """(c) docs, ``.claude/`` and README changes -> ``no tests``, exit 0, no pytest started.

    Reference: section 4.2 last row ("no tests"). The change is real (unstaged edits to three
    tracked files) and ``--run`` is on, so a wrong mapping would start the recorded runner.
    """
    for rel in ("docs/x.md", ".claude/y.md", "README.md"):
        write(repo, rel, "edited\n")
    recorder = Recorder(monkeypatch)
    code = tool.main(["--root", str(repo), "--run", "--explain"])
    out = capsys.readouterr().out
    assert code == 0
    assert "no tests" in out
    assert recorder.calls == []


def test_d_test_file_change_selects_that_file_only(repo: Path) -> None:
    """(d) a change in ``tests/unit/test_mid.py`` selects exactly that file.

    Reference: section 4.2 row 4. Exact equality.
    """
    sel = pick(repo, ["tests/unit/test_mid.py"])
    assert sel.tiers == {"unit": ["tests/unit/test_mid.py"], "integration": [], "slow": [],
                         "gpu": []}


@pytest.mark.parametrize(("path", "unit", "integration"), [
    ("pytest.ini", ["tests/unit"], []),
    ("tests/conftest.py", ["tests/unit"], []),
    ("requirements.txt", ["tests/unit"], ["tests/integration"]),
])
def test_e_gate_files_select_the_unit_tier_with_a_warning(
        repo: Path, path: str, unit: list[str], integration: list[str]) -> None:
    """(e) pytest.ini, conftest.py and requirements.txt select the whole unit tier and warn.

    Reference: section 4.2 rows 5 and 9 (requirements.txt adds integration and the recorded
    decision). Exact equality; the warning must say ``gate-sized``.
    """
    sel = pick(repo, [path])
    assert sel.tiers["unit"] == unit and sel.tiers["integration"] == integration
    assert any("gate-sized" in warning for warning in sel.warnings)
    if path == "requirements.txt":
        assert any("LPC.PC.17" in warning for warning in sel.warnings)


def test_f_new_module_selects_dependents_and_warns(repo: Path) -> None:
    """(f) the untracked ``new`` (no test file) -> ``test_top`` and a warning.

    Reference: section 4.2 "Unknown mapping": dependents of new in GRAPH = {top}; top has a
    unit file. Exact equality, through the real git change set (``new.py`` is untracked).
    """
    write(repo, "lpcstudy/new.py", "")
    graph = tool.build_graph(repo / "lpcstudy")
    changed = tool.changed_files(repo, "main")
    assert changed == ["lpcstudy/new.py"]
    sel = tool.select(changed, graph, repo, CORE, False, False)
    assert sel.tiers["unit"] == [UNIT + "test_top.py"]
    assert sel.warnings == ["no test file for lpcstudy/new.py"]


def test_g_slow_and_gpu_need_their_flags(repo: Path) -> None:
    """(g) slow and gpu tests are never selected without the flag, and never dropped silently.

    Reference: the plan's rule (g) on FILES: ``test_mid_repro.py`` belongs to ``mid``,
    ``test_base_coverage.py`` to ``base``. A changed slow test file is excluded, not selected.
    """
    sel = pick(repo, ["lpcstudy/mid.py"])
    assert sel.tiers["gpu"] == [] and sel.tiers["slow"] == []
    assert sel.excluded == [("gpu", "tests/gpu/test_mid_repro.py")]
    assert pick(repo, ["lpcstudy/mid.py"], include_gpu=True).tiers["gpu"] == [
        "tests/gpu/test_mid_repro.py"]
    direct = pick(repo, ["tests/slow/test_base_coverage.py"])
    assert all(paths == [] for paths in direct.tiers.values())
    assert direct.excluded == [("slow", "tests/slow/test_base_coverage.py")]
    assert pick(repo, ["tests/slow/test_base_coverage.py"], include_slow=True).tiers["slow"] == [
        "tests/slow/test_base_coverage.py"]


def test_excluded_lines_are_printed(repo: Path, capsys) -> None:  # noqa: ANN001
    """The excluded slow file appears as an ``excluded (slow)`` line in the output (not silent).

    Reference: the output format of the plan, and section 4.2 row 1: ``main`` uses the real
    core list, in which the synthetic ``base`` is not core, so the selection is the own file and
    the direct dependents' (cyc has no file, mid has one). Substring check on stdout.
    """
    write(repo, "lpcstudy/base.py", FILES["lpcstudy/base.py"] + "# edit\n")
    assert tool.main(["--root", str(repo)]) == 0
    out = capsys.readouterr().out
    assert "excluded (slow): tests/slow/test_base_coverage.py (use --include-slow)" in out
    assert "unit: tests/unit/test_base.py tests/unit/test_mid.py\n" in out
    assert "integration:" not in out


def test_h_nothing_runs_without_run_flag(repo: Path, monkeypatch, capsys) -> None:  # noqa: ANN001
    """(h) without ``--run`` no pytest or wrapper argv is ever issued; it only prints a command.

    Reference: the plan's check h. The recorder keeps every non-git subprocess call; the list
    must be empty.
    """
    write(repo, "lpcstudy/leaf.py", "def h():\n    return 3\n")
    recorder = Recorder(monkeypatch)
    assert tool.main(["--root", str(repo)]) == 0
    out = capsys.readouterr().out
    assert recorder.calls == []
    assert "command: " in out and "tests/unit/test_leaf.py" in out


def test_h_run_issues_one_flagged_command_per_cpu_tier(repo: Path, monkeypatch) -> None:  # noqa: ANN001
    """(h) with ``--run`` there is one argv per CPU tier with the quiet flags and CPU env.

    Reference: DEVELOPMENT_WORKFLOW.md 4.5/4.6 (``-q --tb=short -rfE``, no ``-n``, no ``-s``,
    ``JAX_PLATFORMS=cpu``, threads 4). gpu files are not run. Exact equality on argv and env.
    ``main`` uses the real core list, so the synthetic ``base`` is a plain module (own file and
    ``mid``'s) and ``pipeline`` is a pipeline module (integration).
    """
    write(repo, "lpcstudy/base.py", FILES["lpcstudy/base.py"] + "# edit\n")
    write(repo, "lpcstudy/pipeline.py", FILES["lpcstudy/pipeline.py"] + "# edit\n")
    recorder = Recorder(monkeypatch)
    assert tool.main(["--root", str(repo), "--run", "--include-slow", "--include-gpu"]) == 0
    flags = ["-q", "--tb=short", "-rfE"]
    assert [argv for argv, _ in recorder.calls] == [
        [sys.executable, "-m", "pytest", *flags, "tests/unit/test_base.py",
         "tests/unit/test_mid.py"],
        [sys.executable, "-m", "pytest", *flags, "tests/integration"],
        [sys.executable, "-m", "pytest", *flags, "tests/slow/test_base_coverage.py"],
    ]
    for _, env in recorder.calls:
        assert env["JAX_PLATFORMS"] == "cpu"
        assert env["XLA_PYTHON_CLIENT_PREALLOCATE"] == "false"


def test_run_stops_at_first_failing_tier_and_returns_its_code(repo: Path, monkeypatch) -> None:  # noqa: ANN001
    """``--run`` stops at the first non-zero exit and returns that code (fix, then ``--lf``).

    Reference: DEVELOPMENT_WORKFLOW.md 4.4. The recorder fails the unit run with code 1.
    """
    write(repo, "lpcstudy/base.py", FILES["lpcstudy/base.py"] + "# edit\n")
    recorder = Recorder(monkeypatch, codes=[1])
    assert tool.main(["--root", str(repo), "--run"]) == 1
    assert len(recorder.calls) == 1


def test_run_delegates_to_the_wrapper_when_it_exists(repo: Path, monkeypatch) -> None:  # noqa: ANN001
    """If ``tools/run_tests.sh`` exists, ``--run`` calls ``run_tests.sh <tier> <paths>``.

    Reference: step 4 of the test-impact skill. The wrapper is only named, never executed.
    """
    write(repo, "tools/run_tests.sh", "echo wrapper\n")
    write(repo, "lpcstudy/leaf.py", "def h():\n    return 4\n")
    recorder = Recorder(monkeypatch)
    assert tool.main(["--root", str(repo), "--run"]) == 0
    assert [argv for argv, _ in recorder.calls] == [
        [str(repo / "tools" / "run_tests.sh"), "unit", "tests/unit/test_leaf.py",
         "tests/unit/test_mid.py"]]


def test_thread_environment_defaults_and_keeps_lpc_threads() -> None:
    """The run environment forces CPU and caps threads at ``LPC_THREADS`` (default 4).

    Reference: DEVELOPMENT_WORKFLOW.md 4.5. Exact equality.
    """
    env = tool.run_environment({"JAX_PLATFORMS": "cuda", "PATH": "/bin"})
    assert env["JAX_PLATFORMS"] == "cpu" and env["LPC_THREADS"] == "4"
    assert env["PATH"] == "/bin"
    for name in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
        assert env[name] == "4"
    kept = tool.run_environment({"LPC_THREADS": "2"})
    assert kept["LPC_THREADS"] == "2" and kept["OMP_NUM_THREADS"] == "2"


@pytest.mark.parametrize("paths", [[], ["tests"], ["tests/"], ["."], ["./"], ["tests/unit", "."]])
def test_commands_refuse_empty_and_whole_suite_paths(paths: list[str]) -> None:
    """``pytest_commands`` raises on an empty or whole-suite path (the tool is its own guard).

    Reference: the plan, risk 1 (the hook cannot see the tool's subprocess). A tier directory
    such as ``tests/unit`` is allowed (checked in the tests above).
    """
    selection = tool.Selection(tiers={"unit": paths, "integration": [], "slow": [], "gpu": []})
    with pytest.raises(ValueError):
        tool.pytest_commands(selection, ROOT)


def test_commands_for_a_tier_directory_are_allowed(tmp_path: Path) -> None:
    """A tier directory is a legitimate argument (not the whole suite). Exact argv equality.

    Hermetic (WU-0012 gate fix F1): the root is an empty ``tmp_path`` with no ``tools/run_tests.sh``,
    so the direct ``python -m pytest`` form is built whether or not the real repository has the
    wrapper. The wrapper form is the next test.
    """
    selection = tool.Selection(
        tiers={"unit": ["tests/unit"], "integration": [], "slow": [], "gpu": []})
    assert not (tmp_path / "tools" / "run_tests.sh").exists()
    assert tool.pytest_commands(selection, tmp_path) == [
        [sys.executable, "-m", "pytest", "-q", "--tb=short", "-rfE", "tests/unit"]]


def test_commands_for_a_tier_directory_use_the_wrapper_when_it_exists(tmp_path: Path) -> None:
    """With ``tools/run_tests.sh`` present the tier directory goes through it. Exact argv equality.

    Reference: the plan of WU-0011 (Q6) and DEVELOPMENT_WORKFLOW.md 4.5: ``run_tests.sh <tier> <paths>``.
    The wrapper is only named, never executed.
    """
    write(tmp_path, "tools/run_tests.sh", "echo wrapper\n")
    selection = tool.Selection(
        tiers={"unit": ["tests/unit"], "integration": [], "slow": [], "gpu": []})
    assert tool.pytest_commands(selection, tmp_path) == [
        [str(tmp_path / "tools" / "run_tests.sh"), "unit", "tests/unit"]]


# ------------------------------------------------------------------ the other mapping rules


def test_tools_seeds_and_unknown_files(repo: Path) -> None:
    """Section 4.2 rows for ``tools/<t>``, the seeds file, and the unknown-mapping default.

    Reference: the table. A tool with a test file selects it; one without warns; the seeds file
    names two test files and warns for the ones that do not exist; an unnamed file uses the
    default rule with a warning. Exact equality.
    """
    write(repo, "notes.txt", "n\n")
    write(repo, "seeds/development_seeds.json", "{}\n")
    sel = pick(repo, ["tools/foo.py", "tools/bar.sh", "seeds/development_seeds.json",
                      "notes.txt"])
    assert sel.tiers["unit"] == ["tests/unit/test_tools_foo.py"]
    assert sel.tiers["integration"] == []
    assert sel.warnings == [  # changed files are processed in sorted order
        "unmapped file notes.txt: default rule used",
        "tests/unit/test_seeds.py does not exist (seeds/development_seeds.json)",
        "tests/integration/test_cli_seeds.py does not exist (seeds/development_seeds.json)",
        "tools/bar.sh has no test (tests/unit/test_tools_bar.py)",
    ]


def test_test_helper_selects_tests_that_name_it(repo: Path) -> None:
    """A non-test file under a tier selects that tier's test files whose text contains its stem.

    Reference: the plan's rule (d), second sentence: ``test_uses_helper.py`` imports
    ``unit_helpers``; ``test_base.py`` does not. Exact equality, with a warning.
    """
    sel = pick(repo, ["tests/unit/unit_helpers.py"])
    assert sel.tiers["unit"] == ["tests/unit/test_uses_helper.py"]
    assert sel.warnings


def test_deleted_files_are_kept_and_warned(repo: Path) -> None:
    """A deleted module keeps its own test file and its recorded dependents, with a warning.

    Reference: the plan ("a deleted path is kept and mapped by name, with a warning"). ``leaf.py``
    is removed; ``mid`` still names it, so its test file stays selected. Exact equality.
    """
    (repo / "lpcstudy" / "leaf.py").unlink()
    sel = pick(repo, ["lpcstudy/leaf.py"])
    assert "lpcstudy/leaf.py is deleted; mapped by name" in sel.warnings
    assert sel.tiers["unit"] == [UNIT + "test_leaf.py", UNIT + "test_mid.py"]


def test_explain_lists_one_line_per_changed_file(repo: Path, capsys) -> None:  # noqa: ANN001
    """``--explain`` prints ``<file> -> <rule> -> <paths>`` for every changed file."""
    write(repo, "lpcstudy/leaf.py", "def h():\n    return 5\n")
    write(repo, "docs/x.md", "edited\n")
    assert tool.main(["--root", str(repo), "--explain"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert any(line.startswith("lpcstudy/leaf.py -> ") and line.endswith(
        "tests/unit/test_leaf.py tests/unit/test_mid.py") for line in lines)
    assert any(line.startswith("docs/x.md -> ") and line.endswith("nothing") for line in lines)


# --------------------------------------------------------------------------------- git


def test_change_set_union_of_committed_staged_unstaged_untracked(repo: Path) -> None:
    """The change set is the union of branch commits, staged, unstaged and untracked files.

    Reference: git's own definitions, set up by hand: one file in each state, including an
    untracked file inside a new directory. Exact equality (sorted).
    """
    git(repo, "checkout", "-q", "-b", "feat")
    write(repo, "docs/x.md", "committed\n")
    git(repo, "commit", "-q", "-am", "branch commit")
    write(repo, "README.md", "staged\n")
    git(repo, "add", "README.md")
    write(repo, "lpcstudy/leaf.py", "def h():\n    return 9\n")
    write(repo, "tests/unit/fixtures/new.json", "{}\n")
    assert tool.changed_files(repo, "main") == [
        "README.md", "docs/x.md", "lpcstudy/leaf.py", "tests/unit/fixtures/new.json"]


def test_change_set_rename_gives_both_paths_and_deletion_is_kept(repo: Path) -> None:
    """A rename yields the old and the new path; a deletion is kept.

    Reference: git semantics, set up by hand (``git mv`` and an ``rm``). Exact equality.
    """
    git(repo, "mv", "lpcstudy/leaf.py", "lpcstudy/leaf2.py")
    git(repo, "rm", "-q", "tests/unit/test_top.py")
    assert tool.changed_files(repo, "main") == [
        "lpcstudy/leaf.py", "lpcstudy/leaf2.py", "tests/unit/test_top.py"]


def test_missing_base_is_an_error_not_a_fallback(repo: Path, capsys) -> None:  # noqa: ANN001
    """A base that does not exist exits 2 with a message (a fallback would under-select).

    Reference: the plan (change set). Exact exit code; the message names the base.
    """
    assert tool.main(["--root", str(repo), "--base", "nope"]) == 2
    assert "base 'nope' not found" in capsys.readouterr().err


def test_not_a_git_repository_is_an_error(tmp_path: Path, capsys) -> None:  # noqa: ANN001
    """Outside a git repository the tool exits 2 and says so."""
    write(tmp_path, "lpcstudy/a.py", "")
    assert tool.main(["--root", str(tmp_path)]) == 2
    assert "not a git repository" in capsys.readouterr().err


def test_syntax_error_in_package_exits_two(repo: Path, capsys) -> None:  # noqa: ANN001
    """A package module that does not parse makes the tool exit 2 naming the file."""
    write(repo, "lpcstudy/leaf.py", "def (\n")
    assert tool.main(["--root", str(repo)]) == 2
    assert "leaf.py" in capsys.readouterr().err


# ------------------------------------------------------------ WU-0011.2: the real package


def test_graph_equals_hand_derived_fixture() -> None:
    """The tool's graph of ``lpcstudy/`` equals the hand-derived fixture exactly (WU-0011.2).

    Reference: ``tests/unit/fixtures/lpcstudy_graph.json``, the independent reference
    (LPC.PC.21a): derived by the planner by reading the ``from .x import`` statements of each
    module, including function-level imports, before the tool existed (git history: the
    fixture is committed before the tool). Update the fixture by hand in the same change as any
    import edit, never from tool output. A change to the import graph fails this test until
    then. Tolerance: none, exact equality of a discrete mapping.
    """
    expected = json.loads(FIXTURE.read_text())["graph"]
    assert tool.build_graph(ROOT / "lpcstudy") == expected


def test_fixture_schema() -> None:
    """The fixture has the 22 module stems as keys and sorted lists of keys as values.

    Reference: the file listing of ``lpcstudy/`` (``*.py`` stems) and the schema of the plan.
    """
    data = json.loads(FIXTURE.read_text())
    assert set(data) == {"description", "source_commit", "graph"}
    graph = data["graph"]
    stems = sorted(path.stem for path in (ROOT / "lpcstudy").glob("*.py"))
    assert sorted(graph) == stems and len(stems) == 22
    for deps in graph.values():
        assert deps == sorted(set(deps)) and set(deps) <= set(stems)


def test_function_level_import_is_an_edge(tmp_path: Path) -> None:
    """The comparison is sensitive: a function-level import adds exactly one edge.

    Reference: the fixture. A copy of the package gets
    ``def _probe(): from .config import StudyConfig`` appended to ``embedding.py``; the graph
    must then differ from the fixture by exactly ``embedding -> config``. Exact equality.
    """
    pkg = tmp_path / "lpcstudy"
    shutil.copytree(ROOT / "lpcstudy", pkg, ignore=shutil.ignore_patterns("__pycache__"))
    with (pkg / "embedding.py").open("a") as handle:
        handle.write("\n\ndef _probe():\n    from .config import StudyConfig\n    return StudyConfig\n")
    expected = json.loads(FIXTURE.read_text())["graph"]
    expected["embedding"] = ["config"]
    assert tool.build_graph(pkg) == expected


def test_selection_runtime_on_the_real_package_is_under_one_second() -> None:
    """Graph build and selection on the real package, every module changed, take under 1 s.

    Reference: the acceptance criterion (runtime under 1 s on the real package). Tolerance:
    the expected time is about 0.1 s (18 files, about 5 kLOC, ``ast.parse``), so a 1.0 s bound
    leaves a margin of about 10 on a loaded 2-core CPU. One measurement, never repeated.
    """
    changed = [f"lpcstudy/{path.name}" for path in sorted((ROOT / "lpcstudy").glob("*.py"))]
    changed.append("tests/conftest.py")
    start = time.perf_counter()
    graph = tool.build_graph(ROOT / "lpcstudy")
    selection = tool.select(changed, graph, ROOT, tool.CORE_MODULES, False, False)
    elapsed = time.perf_counter() - start
    assert selection.tiers["unit"]
    assert elapsed < 1.0


def test_command_line_text_is_shell_quoted(repo: Path, capsys) -> None:  # noqa: ANN001
    """The printed command is exactly the argv joined with shell quoting."""
    write(repo, "lpcstudy/leaf.py", "def h():\n    return 6\n")
    tool.main(["--root", str(repo)])
    line = next(row for row in capsys.readouterr().out.splitlines() if row.startswith("command:"))
    argv = [sys.executable, "-m", "pytest", "-q", "--tb=short", "-rfE",
            "tests/unit/test_leaf.py", "tests/unit/test_mid.py"]
    assert line == "command: " + shlex.join(argv)


# ------------------------------------------------------------- fix round 1 (R1 to R3)


def test_deleted_and_renamed_test_files_are_not_selected(repo: Path) -> None:
    """A deleted test file selects nothing; a renamed one selects only its new path (R1).

    Reference: the plan ("a deleted path is kept and mapped by name, own test file if
    present") and pytest's behavior (a path that does not exist is an error), set up by hand
    with ``git mv`` and ``git rm`` on the synthetic repository. Exact equality.
    """
    graph = tool.build_graph(repo / "lpcstudy")
    git(repo, "mv", "tests/unit/test_top.py", "tests/unit/test_top2.py")
    changed = tool.changed_files(repo, "main")
    assert changed == ["tests/unit/test_top.py", "tests/unit/test_top2.py"]
    sel = tool.select(changed, graph, repo, CORE, False, False)
    assert sel.tiers["unit"] == ["tests/unit/test_top2.py"]
    assert "tests/unit/test_top.py is deleted; mapped by name" in sel.warnings
    git(repo, "rm", "-q", "-f", "tests/unit/test_top2.py")
    removed = tool.changed_files(repo, "main")
    assert removed == ["tests/unit/test_top.py"]
    sel = tool.select(removed, graph, repo, CORE, False, False)
    assert all(paths == [] for paths in sel.tiers.values()) and sel.excluded == []


def test_gpu_files_are_listed_but_never_run(repo: Path, monkeypatch, capsys) -> None:  # noqa: ANN001
    """With ``--run --include-gpu`` a changed gpu file is selected and printed, never run (R2).

    Reference: the plan's ``--run`` bullet (gpu files are printed, never run by the tool).
    ``mid`` is a plain module in ``main`` (own file and ``top``'s), and ``test_mid_repro.py``
    belongs to ``mid``. Exact equality on the recorded argv; a gpu-only change runs nothing.
    """
    write(repo, "lpcstudy/mid.py", FILES["lpcstudy/mid.py"] + "# edit\n")
    recorder = Recorder(monkeypatch)
    assert tool.main(["--root", str(repo), "--run", "--include-gpu"]) == 0
    out = capsys.readouterr().out
    assert "gpu: tests/gpu/test_mid_repro.py" in out
    assert [argv for argv, _ in recorder.calls] == [
        [sys.executable, "-m", "pytest", "-q", "--tb=short", "-rfE", "tests/unit/test_mid.py",
         "tests/unit/test_top.py"]]
    git(repo, "checkout", "-q", "lpcstudy/mid.py")
    write(repo, "tests/gpu/test_mid_repro.py", FILES["tests/gpu/test_mid_repro.py"] + "# edit\n")
    gpu_only = Recorder(monkeypatch)
    assert tool.main(["--root", str(repo), "--run", "--include-gpu"]) == 0
    assert gpu_only.calls == []
    assert "no CPU tests to run" in capsys.readouterr().out


def test_core_and_pipeline_constants_equal_the_workflow_lists() -> None:
    """``CORE_MODULES`` and ``PIPELINE_MODULES`` equal the lists of DEVELOPMENT_WORKFLOW 4.2 (R3).

    Reference: section 4.2, mapping rules: core modules ``config``, ``data``, ``systems``,
    ``dynamics``, ``statistics``, ``ensemble``, ``oracle``; the pipeline row ``pipeline``,
    ``experiments``, ``report``, ``__main__``. Lists copied by hand from the text. Exact equality.
    """
    assert tool.CORE_MODULES == frozenset(
        {"config", "data", "systems", "dynamics", "statistics", "ensemble", "oracle"})
    assert tool.PIPELINE_MODULES == frozenset({"pipeline", "experiments", "report", "__main__"})
