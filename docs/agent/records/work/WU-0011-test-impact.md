# WU-0011: Blast-radius tool (tools/test_impact.py) and its reference graph

| Field | Value |
| --- | --- |
| Status | in progress |
| Class | CSQ3 development |
| Agent(s) | claude-sonnet-5-5 (main session) under governance ledger entry 5 (authorizations 4, 6) |
| Estimate | WU-0011.1 M, WU-0011.2 S (ROADMAP.md §2) |

## Plan (written before execution)

Planner: claude-opus-5-5, 2026-10-10, at `main` = `d6abaa7` (no `tools/test_impact.py` exists). Governing text: DEVELOPMENT_WORKFLOW §4.1, §4.2, §4.4–4.6, §4.9; ROADMAP rows WU-0011.1/.2.

**Split and order.** (0) Commit the fixture `tests/unit/fixtures/lpcstudy_graph.json`, copied byte-for-byte from §F below (copy, not re-derivation), *before* any tool code, so git dates the reference before the tool. (1) WU-0011.1: tool and its tests. (2) WU-0011.2: comparison test. One branch, `wu/0011-test-impact`.

### WU-0011.1 `tools/test_impact.py`

- **Scope in.** Stdlib only (`ast`, `argparse`, `json`, `subprocess`, `os`, `sys`, `pathlib`, `time`). Pure core plus thin I/O: `build_graph(package_dir) -> dict[str, list[str]]`; `changed_files(root, base) -> list[str]`; `select(changed, graph, root, core, include_slow, include_gpu) -> Selection` (paths per tier, reasons per changed file, warnings, exclusions); `pytest_commands(selection, root) -> list[list[str]]`; `main(argv) -> int`. `CORE_MODULES` is a module constant equal to the §4.2 list (`config, data, systems, dynamics, statistics, ensemble, oracle`); `select` takes `core` as a parameter so tests use a synthetic set. `PIPELINE_MODULES = pipeline, experiments, report, __main__`.
- **Scope out.** Timeouts per tier, `XLA_FLAGS` threads, GPU lock (WU-0012.1); editing `.claude/skills/test-impact/SKILL.md` or §4.2 (owner; see questions); a `--graph` dump (excluded on purpose: it would invite copying tool output into the fixture); packaging `tools/`.
- **CLI.** `python3 tools/test_impact.py [--base main] [--explain] [--run] [--include-slow] [--include-gpu] [--root PATH]` (`--root` default: `Path(__file__).resolve().parents[1]`, so a worktree uses its own tree). Prints one line per selected tier (`unit: <paths>`), every `warning:` and `excluded (slow|gpu): <path> (use --include-slow|--include-gpu)`, then `command: <exact argv>` per tier. `--explain` adds `<changed file> -> <rule> -> <paths>` per file. Empty selection: prints `no tests`, exits 0. Exit 2 on: not a git repo, git error, missing base, `SyntaxError` in a package module (named, never skipped, PRIME.4). Without `--run` it never starts pytest.
- **Change set.** `git rev-parse --verify --quiet <base>^{commit}` first (missing → exit 2, `base '<b>' not found`; no fallback, a fallback would under-select silently). Then `git diff --name-only --no-renames <base>...HEAD` plus `git status --porcelain=v1 -z --untracked-files=all --no-renames` (`-z`: unquoted paths; `-uall`: files inside untracked directories, e.g. a new `tests/unit/fixtures/`; `--no-renames`: a rename yields both old and new path). Union, sorted, deduplicated. A deleted path is kept and mapped by name (own test file if present) with a warning.
- **Graph.** `ast.parse` every `<pkg>/*.py`; walk the whole tree (`ast.walk`, so function-, class- and `if`/`try`-level imports count). Edge rules: `from .x import y` → `x`; `from .x.y import z` → `x`; `from . import x [as a]` → `x` when `x.py` exists, else `__init__`; `import lpcstudy.x`, `from lpcstudy.x import y`, `from lpcstudy import x` → `x`; `level ≥ 2` and third-party → none; self-edges dropped. Keys: every `.py` file stem, incl. `__init__` and `__main__`, values sorted, deduplicated. The implicit import of `__init__` by every submodule is not an edge.
- **Mapping (per changed file, union).** Test-to-module convention: `tests/unit/test_<m>.py` is `<m>`'s unit file; in `tests/slow/` and `tests/gpu/`, `test_<m>.py` or `test_<m>_*.py` belong to `<m>`. Tier = first directory under `tests/` (as `tier_of` in `tests/conftest.py`).
  - (a) non-core, non-pipeline `lpcstudy/<m>.py` (real: `embedding, networks, estimation, allocation, validation, analysis`): own unit file + unit files of direct dependents.
  - (b) core `<m>`: own + unit files of every transitive dependent (BFS on the reverse graph, visited set, so cycles terminate) + `tests/integration`.
  - pipeline module: own + direct dependents' unit files + `tests/integration`.
  - (c) `docs/**`, `.claude/**`, `README.md`, `ROADMAP.md`, `DEVELOPMENT_WORKFLOW.md`, `seeds/README.md`: nothing.
  - (d) a single `tests/<tier>/test_*.py`: that file only. A non-test file under `tests/<tier>/` (`unit_helpers.py`, `fixtures/*.json`): the test files of that tier whose text contains its stem (default rule of §4.2 applied to the tests' own imports), with a warning.
  - (e) `pytest.ini`, `tests/conftest.py`: `tests/unit` + `warning: gate-sized run (whole unit tier); record it in the log`. `requirements.txt`: `tests/unit` + `tests/integration` + the same warning + `run once by the main session; recorded decision (LPC.PC.17)`.
  - (f) a module with no `tests/unit/test_<m>.py` (new or existing): the rule of its class without the own file, plus `warning: no test file for lpcstudy/<m>.py`. `tools/<t>.py|sh`: `tests/unit/test_tools_<t>.py` if present, else a warning. `seeds/development_seeds.json`: the two §4.2 files if present, else a warning. Any other file: §4.2 default (own test file if any + dependents), with `warning: unmapped file, default rule used`.
  - (g) slow/gpu files that the rules above would select (by the convention, for each changed module, including `statistics`, `analysis`) or that changed directly are listed as `excluded` unless `--include-slow`/`--include-gpu`. Never silently dropped.
- **`--run`.** Never with an empty path list or a whole-suite path (`tests`, `tests/`, `.`): `pytest_commands` raises `ValueError` (the tool's subprocess is invisible to `.claude/hooks/test_gate.py`, so the tool is its own guard). One invocation per tier, `unit` → `integration` → `slow`, stopping at the first non-zero exit (fix, then `--lf`, §4.4); `gpu` files are printed, never run by the tool (lock is WU-0012). If `tools/run_tests.sh` exists: `tools/run_tests.sh <tier> <paths>` (interface from the skill, step 4). Else `[sys.executable, "-m", "pytest", "-q", "--tb=short", "-rfE", *paths]` with env: `JAX_PLATFORMS=cpu` forced, `XLA_PYTHON_CLIENT_PREALLOCATE=false` forced, `LPC_THREADS` kept or `4`, `OMP/MKL/OPENBLAS_NUM_THREADS=$LPC_THREADS`. Never `-n`, `-s`, `-v`. Returns pytest's exit code.
- **Tests (`tests/unit/test_tools_test_impact.py`, unit tier).** Import the tool by path: `importlib.util.spec_from_file_location("test_impact", ROOT / "tools/test_impact.py")`, register in `sys.modules` before `exec_module`; no `__init__.py`, no packaging change. A fixture writes a synthetic repo in `tmp_path`: `lpcstudy/{base,cyc,leaf,mid,top,pipeline,new}.py` (`new` untracked, imports nothing), core = `{base, cyc}` with a `cyc ↔ base` import cycle; `mid`: `from .base import f` and inside a `def` `from .leaf import h`; `top`: `from . import mid as m` and `from .new import y`; `pipeline`: `from .top import t`; tests `tests/unit/test_{base,leaf,mid,top}.py` (none for `new`, `pipeline`), `tests/integration/test_smoke.py`, `tests/slow/test_base_coverage.py`, `tests/gpu/test_mid_repro.py`, `tests/conftest.py`, `pytest.ini`, `requirements.txt`, `docs/x.md`, `.claude/y.md`, `README.md`. The synthetic graph is asserted literally in the test (written by hand). No test starts pytest; git tests use `git -c user.name=t -c user.email=t@t -c commit.gpgsign=false`.

**Acceptance criteria (ROADMAP, verbatim, fixed).** "Tool prints a correct test selection for every change class in DEVELOPMENT_WORKFLOW §4.2" — "On a synthetic package in `tmp_path` with a known graph: (a) a leaf-module change selects its own test file plus its direct dependents' files; (b) a core-module change selects all transitive dependents plus `tests/integration`; (c) a docs-only or `.claude/`-only change selects nothing and exits 0 with "no tests"; (d) a change in `tests/unit/test_x.py` selects that file only; (e) a change to `requirements.txt`, `pytest.ini` or `tests/conftest.py` selects the whole `unit` tier and prints a warning that this is a gate-sized run; (f) a new module with no test file selects its direct dependents' files and prints a warning; (g) the tool never selects `slow` or `gpu` without `--include-slow` or `--include-gpu`; (h) no pytest process is started without `--run`. Runtime of the selection under 1 s on the real package."

**Checks (reference: the hand-written synthetic graph and §4.2 table; all exact set equality, no tolerance, outputs are discrete).** a: `{leaf}` → `{test_leaf, test_mid}` exactly (edge only via the function-level import). b: `{base}` → `{test_base, test_mid, test_top}` + `tests/integration`, not `tests/slow/...`; with `--include-slow` it is added; terminates on the cycle. c: `{docs/x.md, .claude/y.md, README.md}` via `main(["--run", ...])` on a git repo → stdout `no tests`, exit 0, recorded subprocess calls contain no pytest. d: `{tests/unit/test_mid.py}` → exactly that file. e: each of the three files alone → `tests/unit` (+ `tests/integration` for `requirements.txt`) and stdout contains `gate-sized`. f: `{new}` (untracked) → `{test_top}` + `warning: no test file for lpcstudy/new.py`. g: `{mid}` → no `tests/gpu/...` and an `excluded (gpu)` line; `{tests/slow/test_base_coverage.py}` → nothing selected, `excluded (slow)` line; flags add them. h: `main([...])` without `--run` with `subprocess.run` wrapped by a recorder (git passes through) → no argv contains `pytest` or `run_tests.sh`; with `--run` and a fake runner → one argv per CPU tier, flags exactly `-q --tb=short -rfE`, no `-n`, env `JAX_PLATFORMS=cpu`; `pytest_commands` on an empty or `tests` path list raises. Git: committed-on-branch, staged, unstaged, untracked-in-new-dir, rename (both paths), deletion, and missing base (exit 2, message) each appear correctly. Runtime: `build_graph` + `select` on the real `lpcstudy/` with every `lpcstudy/*.py` plus `tests/conftest.py` as the change set, one `perf_counter` measurement, `< 1.0 s` (criterion; expected ≈ 0.1 s for 18 files / 5.2 kLOC, margin ≥ 5× for a loaded 2-core CPU; never repeated to pass).
- **Definition of done.** All checks above pass in one run of the radius; dogfood: `python3 tools/test_impact.py --base main --explain` on this branch prints exactly `tests/unit/test_tools_test_impact.py` (output pasted in the Log); independent review approved.

### WU-0011.2 Fixture and comparison test

- **Criteria (ROADMAP, verbatim, fixed).** "Fixture committed; comparison test passes" — "The fixture is written by reading the `from .x import` statements of each module, including function-level imports; the test asserts the tool's graph equals the fixture exactly. The fixture docstring names it as the independent reference (LPC.PC.21a). A change to the import graph fails this test until the fixture is updated by hand in the same change."
- **Checks.** `test_graph_equals_hand_derived_fixture`: `build_graph(ROOT/"lpcstudy") == json.load(fixture)["graph"]`, exact (docstring names the fixture as the LPC.PC.21a reference, says "update by hand, never from tool output"). `test_function_level_import_is_an_edge`: copy `lpcstudy/*.py` to `tmp_path`, append `def _probe():\n    from .config import StudyConfig` to `embedding.py`, assert the graph now differs from the fixture exactly by `embedding → config` (sensitivity of the comparison). Schema check: keys = the 18 `.py` stems, values sorted lists of keys.
- **§F Fixture (derived by hand, 2026-10-10).** Method: `grep -nE '^\s*(from|import)\s' lpcstudy/*.py`, then reading each line and its context; `grep -nE 'lpcstudy|importlib|__import__|TYPE_CHECKING|except ImportError'` for other forms. 58 relative import lines, 5 duplicates, **53 edges**; no absolute `lpcstudy.` imports, no `TYPE_CHECKING`, no import inside `try`/`if`, no `importlib`. Non-trivial: function-level `oracle.py:87 from .systems` (the *only* source of `oracle → systems`), `analysis.py:233,274,619` (allocation, duplicate), `validation.py:217` (ensemble, duplicate), `experiments.py:34` (pipeline, duplicate); `experiments.py:18 from . import analysis as an`; `report.py:15–16` after `matplotlib.use("Agg")` (unconditional, `noqa: E402`); `__init__.py` empty. Agrees with the §4.2 table row by row. Schema: `{"description": str, "source_commit": str, "graph": {module: sorted [modules]}}`.

```json
{
  "description": "Independent reference (LPC.PC.21a) for the import graph built by tools/test_impact.py. Derived by hand by the planner (claude-opus-5-5, WU-0011.2, 2026-10-10) from the import statements of lpcstudy/*.py, including function-level imports and 'from . import x', before the tool existed. Key: module stem; value: sorted lpcstudy modules it imports directly, at any scope. Update by hand in the same change as any import edit; never from tool output.",
  "source_commit": "d6abaa7511e6e7db8ec377dd59d9b91c6d54b83a",
  "graph": {
    "__init__": [],
    "__main__": ["config", "experiments", "pipeline", "report"],
    "allocation": ["ensemble", "networks", "oracle", "statistics"],
    "analysis": ["allocation", "config", "oracle", "pipeline", "statistics"],
    "config": [],
    "data": ["config", "embedding", "systems"],
    "dynamics": [],
    "embedding": [],
    "ensemble": ["data", "dynamics", "embedding", "estimation"],
    "estimation": ["data", "dynamics", "networks"],
    "experiments": ["allocation", "analysis", "config", "dynamics", "ensemble", "oracle", "pipeline", "statistics", "validation"],
    "networks": [],
    "oracle": ["data", "dynamics", "ensemble", "systems"],
    "pipeline": ["allocation", "config", "data", "ensemble", "estimation", "networks", "oracle", "statistics", "systems"],
    "report": ["allocation", "config"],
    "statistics": [],
    "systems": [],
    "validation": ["data", "dynamics", "ensemble", "oracle", "statistics", "systems"]
  }
}
```

### Common

- **Affected checks (§4.2).** Both sub-tasks: `tests/unit/test_tools_test_impact.py`, `unit` tier only (rules: `tools/<t>.py` → `test_tools_<t>.py`; a test file → itself; the fixture → the test file naming it). No `lpcstudy/` change, so no `tests/integration` (RSRC.11).
- **Owner checkpoints (LPC.PC.11).** None: no verdict, statistics, seed or provenance code; no dependency (stdlib only).
- **Risks.** (1) The tool's own subprocess bypasses the hook: guarded by the empty/whole-suite `ValueError` and test h. (2) Hook false positive: any shell token ending in `pytest` that is followed by no path or by `tests` is read as a whole-suite run and blocked, e.g. `echo pytest`, `grep -rn pytest tests`, or `git commit -m "... pytest"`. Avoid such tokens: quote the word inside a longer token, and always pass explicit file paths. The tool's own invocation (`python3 tools/test_impact.py ...`) contains no such token. (3) The skill runs the tool with `2>/dev/null || echo "not available yet"`, which will mask exit-2 errors after this unit (owner edit to `.claude/`, see Q6). (4) Runtime check under load: one measurement; a failure is investigated, not retried. (5) Tests must never run pytest on the real suite (no `pytester.runpytest` here).
- **Questions for the owner.**
  - Q1. Core list is not derivable from the import graph. Transitive-dependent counts: `config`, `systems`, `embedding` 11; `data`, `dynamics`, `networks` 10; `estimation` 9; `ensemble` 8; `statistics`, `oracle` 7; `allocation` 5. So `embedding`, `networks`, `estimation` reach more modules than `statistics`/`oracle` but are not core. "≥ 4 direct dependents" gives the list plus `allocation`. "Reaches `pipeline`" makes 11 modules core (integration, ~70 s, on almost every change). The plan implements the §4.2 list as written (one constant). Keep it as a designated list (and say so in §4.2), or adopt a graph rule?
  - Q2. Tests import other modules than their own: `test_dynamics` and `test_embedding` import `lpcstudy.systems`. A `systems` change (core) does not select them under §4.2. Add a rule "a test file is also selected when a module it imports directly is changed"? It costs about 1 s and is not in the plan unless approved.
  - Q3. A JSON file has no docstring. The plan uses a `description` field plus the test's docstring. Does this satisfy "fixture docstring"?
  - Q4. The plan reads (a) "leaf-module" as §4.2's "not a core module". `config`, `systems`, `dynamics` and `statistics` import nothing but are core. Confirm.
  - Q5. If a test file under `tests/slow/` or `tests/gpu/` changes, (d) and (g) conflict. The plan lets (g) win and prints an `excluded` line. Confirm.
  - Q6. Two possible owner edits: §4.2 says `--run` goes "through `tools/run_tests.sh`" (the plan delegates when the wrapper exists, else uses the env by hand), and the skill's fallback message would hide tool errors.

## Log

<dated entries: what was done, commands, results, commits>

## Review

- **Reviewer:** <actor, not the author>
- **Findings and resolution:**

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:

## Referral

<only if halted; use the form in agent-instructions.md, LPC.AI.13>
