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

### Plan amendment 2026-10-10, claude-sonnet-5-5 (main session), before execution (VV.3)

Q1 to Q6 are answered as recorded in `DEC-0003` (proposed, for owner confirmation): the tool follows DEVELOPMENT_WORKFLOW §4.2 as written; Q2 (also select a test file when a module it imports changes) is NOT implemented and is recommended to the owner; Q3 to Q5 are the planner's readings; Q6 needs no code. No acceptance criterion is changed. The fixture `tests/unit/fixtures/lpcstudy_graph.json` was committed at 37def38 before any tool code.

## Log

<dated entries: what was done, commands, results, commits>

### 2026-10-10, claude-sonnet-5-5 (developer), WU-0011.1 implementation

Files: `tools/test_impact.py` (new), `tests/unit/test_tools_test_impact.py` (new). The test file was written first and the tool second; no failing run was made between them (no run is allowed without a code change to justify it; the first run is the radius below). §4.2 implemented as written; the Q2 rule is not implemented (amendment).

Test-run checklist (§4.9), before the first radius run:
1. Change set: `git diff --name-only main...HEAD` = docs (decisions.md, this file, queue.md) and `tests/unit/fixtures/lpcstudy_graph.json`; `git status --porcelain`: untracked `tests/unit/test_tools_test_impact.py`, `tools/test_impact.py`.
2. Radius (hand-derived, rules `tools/<t>.py` -> `test_tools_<t>.py`, a test file -> itself, the fixture -> the test naming it): `tests/unit/test_tools_test_impact.py`, unit tier, one file; far smaller than the whole suite; no gate.
3. Already run? No: first run on this code.
4. Device: `JAX_PLATFORMS=cpu` (settings default, `echo` shows `cpu`); no GPU.
5. Threads and time: `LPC_THREADS=4` (shown); unit timeout 300 s, expected under 20 s.
6. Contention: no `lpcstudy --preset` process running (`pgrep` shows only itself).
7. Output: `-q --tb=short -rfE`; only the summary line and failures are recorded.
8. Command: `.venv/bin/python -m pytest -q --tb=short -rfE tests/unit/test_tools_test_impact.py` (variables set by the settings; `tools/run_tests.sh` does not exist yet, WU-0012).

Note on the run: WU-0011.1 and WU-0011.2 have the same radius (one file), and the file already holds the .2 tests (fixture comparison, schema, function-level sensitivity), so this one run covers both. I first moved the three .2 tests out of the file to commit .1 separately; the harness denied that run as test removal, so I restored them unchanged (no test deleted or edited) and run the whole file once. The .1 commit will hold the file minus the three .2 tests (a strict subset of the run), the .2 commit the full file.

Result of radius run 1 (first run on this code): `3 failed, 37 passed in 0.59s`. Failures, all errors in my own new test expectations, none in a criterion: `test_excluded_lines_are_printed` and `test_h_run_issues_one_flagged_command_per_cpu_tier` expected the core rule for the synthetic `base`, but `main` uses the real `CORE_MODULES`, in which `base` is a plain module (so no `test_top`, no integration); `test_tools_seeds_and_unknown_files` called `pick` on `notes.txt` and the seeds file without creating them, so the tool correctly added "is deleted" warnings. The tool is right in all three. Fixed the expectations (main-driven tests now use `base` for the plain rule and `pipeline` for the integration tier; the files are created); the core rule itself stays covered by `test_b_*` through `select(..., CORE, ...)`. No tolerance or reference loosened.

Checklist before the `--lf` run and the second radius run (both after the test fix above):
1. Change set: as before plus the edited test file (`tools/test_impact.py`, `tests/unit/test_tools_test_impact.py` untracked; fixture and docs on the branch).
2. Radius: same file, unit tier, smaller than the whole suite; first the three failing tests with `--lf`, then the file once.
3. Already run? Yes on the previous code (3 failed); the test file changed since, so this is the one rerun allowed after a fix (§4.4, §4.6).
4. Device `JAX_PLATFORMS=cpu`. 5. `LPC_THREADS=4`, unit timeout 300 s. 6. No preset running. 7. `-q --tb=short -rfE`. 8. Commands: `.venv/bin/python -m pytest --lf -q --tb=short -rfE tests/unit/test_tools_test_impact.py`, then the same without `--lf`.

Results: `--lf`: `3 passed, 37 deselected in 0.28s`. Radius, once: `40 passed in 0.51s` (all of the file, including the three .2 tests: `test_graph_equals_hand_derived_fixture`, `test_fixture_schema`, `test_function_level_import_is_an_edge`; the comparison with the fixture passed on its first run, so there is no fixture error to report). Self-check: grep of the tool for `clip|nan_to_num|isfinite|where(|try:|except|default_rng|random.|PRNGKey` finds only the two `try/except` that turn a `SyntaxError` (build_graph) and a `ToolError` (main) into a named error and exit 2, neither silent; no randomness; no tolerance in any assert, the only numeric bound is the criterion `< 1.0` s.

Dogfood: `.venv/bin/python tools/test_impact.py --base main --explain` on this branch prints `unit: tests/unit/test_tools_test_impact.py` as the only selection (exit 0), with one warning, `non-test file tests/unit/fixtures/lpcstudy_graph.json: selected the unit tests that name 'lpcstudy_graph'`, and the three docs files as "no tests".

Facts about the real layout (recorded, not fixed). (1) Runtime of `build_graph` + `select` on the real package, one change each: 0.030 to 0.033 s (criterion `< 1 s`). (2) Q2 gap is real: a change to `lpcstudy/systems.py` selects `tests/unit/test_allocation.py`, `test_analysis.py`, `test_ensemble.py`, `test_oracle.py` plus `tests/integration` and the warning `no test file for lpcstudy/systems.py`; it does NOT select `tests/unit/test_dynamics.py` or `tests/unit/test_embedding.py`, although both import `lpcstudy.systems` (`from lpcstudy.systems import SYSTEMS, make_flow_step, simulate_trajectory`, line 11 and line 9). `systems` has no `tests/unit/test_systems.py`. Same pattern for `config` (`no test file for lpcstudy/config.py`). (3) A change to `lpcstudy/pipeline.py` selects `tests/unit/test_analysis.py` and `tests/integration`; to `statistics.py`: `test_allocation`, `test_analysis`, `test_statistics` + integration; to `embedding.py` (non-core): `test_embedding`, `test_ensemble` only.

### 2026-10-10, claude-sonnet-5-5 (developer), WU-0011.2 comparison test

Commit 164b5bb is WU-0011.1. WU-0011.2 adds the three fixture tests to `tests/unit/test_tools_test_impact.py` (already run in the radius run above: `40 passed in 0.51s`, no code change since, so no further run per §4.4): `test_graph_equals_hand_derived_fixture` (docstring names `tests/unit/fixtures/lpcstudy_graph.json` as the LPC.PC.21a reference, "update by hand, never from tool output"; exact equality of `build_graph(lpcstudy/)` with `json["graph"]`), `test_fixture_schema` (18 stems as keys, sorted lists of keys), `test_function_level_import_is_an_edge` (a copy of the package with a `def _probe()` import `from .config import StudyConfig` appended to `embedding.py` differs from the fixture by exactly `embedding -> config`). The fixture was not edited or regenerated (last commit touching it: 37def38); I did not read its contents to shape the graph builder. The comparison passed on its first run; there is no fixture error to report.

Commit split: the .1 commit stages the test file without the three .2 tests (via the index; the working file is untouched), the .2 commit adds them.

### 2026-10-10, claude-sonnet-5-5 (developer), fix round 1 (R1 to R4)

Changes: `tools/test_impact.py` (test-file branch of `_map_file` returns `_exists(root, path)`, so a deleted or renamed-away test file is not selected; the "is deleted; mapped by name" warning stays); `tests/unit/test_tools_test_impact.py` (three tests appended, no existing assertion changed: `test_deleted_and_renamed_test_files_are_not_selected` (R1), `test_gpu_files_are_listed_but_never_run` (R2), `test_core_and_pipeline_constants_equal_the_workflow_lists` (R3, literals copied by hand from §4.2)).

Checklist before the radius run:
1. Change set: branch diff = docs, fixture, `tools/test_impact.py`, the test file (commits 164b5bb, e9552ec, b2bb46b); working tree: modified `tools/test_impact.py`, `tests/unit/test_tools_test_impact.py`.
2. Radius: `tests/unit/test_tools_test_impact.py`, unit tier (rules: `tools/<t>.py` -> its test file; a test file -> itself); one file, smaller than the whole suite, no gate.
3. Already run? Not on this code (tool and tests changed since the 40-passed run).
4. Device `JAX_PLATFORMS=cpu`. 5. `LPC_THREADS=4`, unit timeout 300 s. 6. No preset running. 7. `-q --tb=short -rfE`, summary and failures only.
8. Command: `.venv/bin/python -m pytest -q --tb=short -rfE tests/unit/test_tools_test_impact.py` (no `tools/run_tests.sh` yet).

Result: `43 passed in 1.47s` (40 earlier tests unchanged and passing, 3 new). Self-check: the diff of `tools/` has no `clip|nan_to_num|isfinite|where(|try:|except|default_rng|random.|PRNGKey` line; no tolerance touched; no existing assertion changed or removed.

R4, dogfood output, verbatim, after the fixes (`.venv/bin/python tools/test_impact.py --base main --explain`, run before the fix commit, so the working-tree files appear):

```
docs/agent/records/decisions.md -> no tests (docs, .claude, readme) -> nothing
docs/agent/records/work/WU-0011-test-impact.md -> no tests (docs, .claude, readme) -> nothing
docs/agent/records/work/queue.md -> no tests (docs, .claude, readme) -> nothing
tests/unit/fixtures/lpcstudy_graph.json -> test helper: tests naming it -> tests/unit/test_tools_test_impact.py
tests/unit/test_tools_test_impact.py -> test file: that file only -> tests/unit/test_tools_test_impact.py
tools/test_impact.py -> tool: its test file -> tests/unit/test_tools_test_impact.py
unit: tests/unit/test_tools_test_impact.py
warning: non-test file tests/unit/fixtures/lpcstudy_graph.json: selected the unit tests that name 'lpcstudy_graph'
command: /home/brianm/projects/physics/chaos/lpcstudy/.venv/bin/python -m pytest -q --tb=short -rfE tests/unit/test_tools_test_impact.py
exit 0
```


## Review

- **Reviewer:** `reviewer`, claude-opus-5-5, fresh context, 2026-10-10, at `e9552ec` (branch `wu/0011-test-impact`; working tree clean before this edit).
- **Radius (hand-derived, §4.2: `tools/<t>.py` -> `test_tools_<t>.py`; a test file -> itself; the fixture -> the test naming it):** `tests/unit/test_tools_test_impact.py`, unit tier. Run once, CPU defaults (`JAX_PLATFORMS=cpu`, `LPC_THREADS=4`, no `LPC_GATE`, no preset running): `.venv/bin/python -m pytest -q --tb=short -rfE tests/unit/test_tools_test_impact.py` -> `40 passed in 1.32s`.
- **Independent checks (no finding).**
  - Fixture: unchanged since 37def38 (`git diff 37def38 HEAD -- tests/unit/fixtures` empty; one commit touches it). It is byte-identical to plan §F. All 53 edges were checked against `grep` of the `from .`/`lpcstudy` imports, including `oracle.py:87` (function-level, the only `oracle -> systems`), `analysis.py:233/274/619`, `validation.py:217`, `experiments.py:18` (`from . import analysis`) and `:34`, and `report.py:15-16`. A separate 10-line `ast` script of my own also reproduces the fixture exactly. The tool never opens the fixture: its only `json` text is the seeds path at line 283.
  - Criteria (a)–(h), read path by path. (a) Non-core rule, lines 245–249. (b) BFS with a visited set, lines 197–207: terminates on cycles. (c) Lines 273–274, `no tests` and exit 0 at lines 446–448. (d) Lines 293–294. (e) Lines 275–282, with `gate-sized` in both warnings. (f) Missing own file -> warning, line 236. (g) Every slow/gpu path goes through the `wanted` filter at lines 351–354, and the helper and convention routes also pass through it. (h) `subprocess.run` appears for pytest only under `if args.run` (line 455). `pytest_commands` refuses empty and whole-suite lists. `gpu` is outside `CPU_TIERS`. Flags are exactly `-q --tb=short -rfE`. Runtime: the in-test measurement and the 0.03 s in the log are both far below 1 s. Probes in my scratch directory (no pytest started) confirmed: gpu-only with `--include-gpu` -> "no CPU tests to run" and exit 0; `__init__` change -> "no tests" plus two warnings.
  - (i) Three test expectations changed after run 1. The run-1 text is not in git (the files were untracked), so I judged the final text against the code. All three were corrections of wrong expectations; none weakens a test or hides a tool defect. 1. `main` hard-codes `CORE_MODULES`, so the synthetic `base` really is non-core there. The new expectation (`test_base`, `test_mid`, no integration) is the hand-derived non-core set. 2. The integration-tier argv is still checked exactly, now through `pipeline`. 3. A file that does not exist is correctly reported as deleted, and creating the files is the right fix. The core rule itself remains tested exactly by `test_b_*`. See R3 for the coverage this leaves on the real constant.
  - (ii) The .2 tests are intact. `git diff 164b5bb e9552ec` adds exactly the three tests, plus imports and `FIXTURE`, and removes no assertion. They match the plan's check list: exact equality, docstring naming LPC.PC.21a and "never from tool output", the `embedding -> config` sensitivity probe, and the 18-stem schema.
  - (iii) The 164b5bb/e9552ec split does not matter. The tool is identical in both commits. The .1 test file is a strict subset (30 of 33 functions) and has no dangling `json`/`shutil`/`FIXTURE` reference (checked with `ast`). The merge gate runs HEAD.
  - (iv) The `__init__` warning (lines 237–239) is harmless. It changes no selection and makes a known under-selection visible (PRIME.4). It is not scope creep. The extra "not the top-level" refusal (line 180) is similarly harmless.
  - (v) The Q2 gap is stated accurately. My own BFS on the fixture graph gives this §4.2 set for `systems`: `test_allocation`, `test_analysis`, `test_ensemble`, `test_oracle` + `tests/integration`. That set equals the log. `test_dynamics.py:11` and `test_embedding.py:9` import `lpcstudy.systems` and are not selected. These are the only cross-imports outside §4.2's reach: `test_allocation -> oracle` and the `unit_helpers -> ensemble` users are already covered.
  - Governance. No silent handling: every failure is exit 2 with a named message, or pytest's code. Stdlib only, no randomness. Commits name the unit and carry `Agent:`. Records are append-only (no removed lines in `docs/`). Owner checkpoint: none (no verdict, statistics, seed, provenance or dependency code).
- **Findings and resolution:**
  - **R1 (medium, correctness/plan).** `tools/test_impact.py:293-294`: a changed test file is selected even when it no longer exists. This covers a `git rm` of a test file and the old path of a renamed test file. The plan maps a deleted path "by name (own test file if present)". Probe: `git mv tests/unit/test_b.py tests/unit/test_c.py` -> `command: ... pytest ... tests/unit/test_b.py tests/unit/test_c.py`. Under `--run`, pytest exits 4 (file not found). The tool returns 4 and stops before `integration`, so every test deletion or rename produces a spurious failed radius (and an excluded line for a missing slow/gpu file). Fix: return `_exists(root, path)` in that branch; the existing "is deleted; mapped by name" warning already reports it. Add a test: rename `test_top.py` -> only the new path is selected, with the warning; `git rm` alone -> `no tests`.
  - **R2 (low, evidence).** `tests/unit/test_tools_test_impact.py:326-347`: the docstring claims "gpu files are not run", but no gpu file is selected in this test (`test_mid_repro.py` belongs to `mid`, which is not changed). `--include-gpu` is therefore vacuous, and the "gpu tier is never run by the tool" behavior (plan `--run` bullet) has no test. The code is right by reading. Fix: in that test, also change `lpcstudy/mid.py` (expected argv hand-derived again) and assert that no argv contains `tests/gpu/`. Alternatively, add a gpu-only `--run --include-gpu` case asserting `recorder.calls == []`.
  - **R3 (low, evidence).** `tools/test_impact.py:32-34`: no test pins `CORE_MODULES` or `PIPELINE_MODULES` against §4.2. After the run-1 fix, every `main`-level test uses names outside both sets, and the real-package runtime test asserts only a non-empty selection. A typo in either constant would silently change the core/pipeline rule on the real package. That rule is what criterion (b) protects, and Q2 already shows how quietly the real radius can shrink. The constants are correct now: I checked them against §4.2 rows 2–3. Fix: one test asserting both constants equal the §4.2 lists, written literally. Reference: DEVELOPMENT_WORKFLOW §4.2 table. No tolerance.
  - **R4 (low, definition of done).** Unit file, `## Log` (the "Dogfood" paragraph): the DoD requires the dogfood output to be "pasted in the Log", but the log paraphrases it. My run at `e9552ec` agrees with the paraphrase: one `unit:` line, `tests/unit/test_tools_test_impact.py`, one fixture warning, exit 0. Fix: paste the verbatim output after the R1 fix, as a new dated entry.
- **Verdict:** `approve with fixes` (R1 required; R2–R4 are small evidence and record fixes). Re-review covers R1–R4 only.

### Re-review, fix round 1, 2026-10-10, `reviewer`, claude-opus-5-5 (fresh context), at `78fcfd6`

Scope: R1–R4 only, judged from `git show 78fcfd6` and the new `## Log` entry. As instructed, no tests were run; the developer's radius result at this code is `43 passed in 1.47s`.

- **R1: fixed.** `tools/test_impact.py:294` now returns `_exists(root, path)`, so a test path that no longer exists is not selected, and the "is deleted" warning is still printed (line 340). The new test `test_deleted_and_renamed_test_files_are_not_selected` does a real `git mv test_top.py -> test_top2.py` and then a `git rm -f`, and asserts the change sets exactly. It would fail against the old code: after the rename the old code selects `[test_top.py, test_top2.py]` instead of `[test_top2.py]`, and after the deletion it selects `[test_top.py]` instead of nothing.
- **R2: fixed.** `test_gpu_files_are_listed_but_never_run` has two parts:
  - It changes `mid` under `--run --include-gpu`. `tests/gpu/test_mid_repro.py` appears in the `gpu:` line, and the recorded argv is exactly the one unit command `[test_mid, test_top]`. That is the non-core set derived by hand: own file plus direct dependent `top`.
  - It then makes a gpu-only change. The recorder shows no calls and the output says "no CPU tests to run".
- **R3: fixed.** The literals in the test match DEVELOPMENT_WORKFLOW.md §4.2 exactly. Line 124 lists the core modules `config, data, systems, dynamics, statistics, ensemble, oracle`. Line 125 lists the pipeline modules `pipeline, experiments, report, __main__`. The test compares them by exact `frozenset` equality.
- **R4: fixed.** The pasted output is verbatim and matches my own run at `e9552ec` line for line. It was captured from the working tree before the commit, and that does not matter. The only tool change is line 294, which affects only test paths that do not exist. The six paths in the change set are the same whether they were committed or still in the working tree.
- **Other checks.**
  - The test-file diff `e9552ec..78fcfd6` only appends three tests after line 592. None of the 40 earlier tests or their assertions changed.
  - The fixture is still unchanged since 37def38.
  - 78fcfd6 touches only `tools/test_impact.py`, the test file and the unit file.
  - The unit-file diff against `b2bb46b` is additions only: one new `## Log` entry, placed at the end of the Log, before `## Review`.
  - The commit names the unit and carries `Agent:`.
- **Verdict:** `approve`. All of R1–R4 are fixed, with no new finding.

### Resolution of findings, 2026-10-10, claude-sonnet-5-5 (main session)

- **R1: fixed in 78fcfd6** (re-review: fixed). **R2: fixed in 78fcfd6** (fixed). **R3: fixed in 78fcfd6** (fixed). **R4: fixed in 78fcfd6** (fixed; the dogfood output was captured from the working tree before the commit, which the reviewer judged immaterial).
- `DEC-0003` stays **proposed** for the owner. It changes no criterion and no behavior of §4.2; the one open design question in it is Q2, recommended to the owner and not implemented.

### Merge gate, 2026-10-10, claude-sonnet-5-5 (main session), checklist before the run (§4.9, §4.3)

1. **Change set:** `git diff --name-only main...HEAD`: `tools/test_impact.py`, `tests/unit/test_tools_test_impact.py`, `tests/unit/fixtures/lpcstudy_graph.json`, `docs/agent/records/decisions.md`, `docs/agent/records/work/WU-0011-test-impact.md`, `docs/agent/records/work/queue.md`. `git status --porcelain` is empty after the commit that carries this entry.
2. **Radius:** the merge gate of §4.3, tiers `unit` and `integration`, by the main session (the named role): `tests/unit tests/integration`.
3. **Already run?** The full set has not run on this code. Only `tests/unit/test_tools_test_impact.py` has (developer: 43 passed; reviewer: 40 passed before the fix). This gate is the first run of the whole unit and integration set with this change, once.
4. **Device:** `JAX_PLATFORMS=cpu`, `XLA_PYTHON_CLIENT_PREALLOCATE=false`.
5. **Threads and time:** `LPC_THREADS=4`, `OMP/MKL/OPENBLAS_NUM_THREADS=4`, `timeout 600`.
6. **Contention:** no preset running; no GPU use.
7. **Output:** `-q --tb=short -rfE`.
8. **Command:** `LPC_GATE=merge timeout 600 .venv/bin/python -m pytest -q --tb=short -rfE tests/unit tests/integration`.

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:

## Referral

<only if halted; use the form in agent-instructions.md, LPC.AI.13>
