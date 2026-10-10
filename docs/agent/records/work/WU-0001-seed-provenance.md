# WU-0001: Seed registry, confirmatory-seed guard, run provenance

| Field | Value |
| --- | --- |
| Status | planned |
| Class | CSQ3 development; the code becomes part of the CSQ2 pipeline at the freeze |
| Agent(s) | — |

## Plan

**Scope.**

- **Command-line seeds.** Add `--seed-id DEV-n` (reads `seeds/development_seeds.json`) and `--confirmatory` (reads the seed and salt from the environment variables `LPC_CONF_SEED` and `LPC_CONF_SALT`, never from a file in the repository) to `python -m lpcstudy`.
- **Commitment check.** Verify a confirmatory seed against the latest ledger `commitment` entry for `CONF-1`, using `tools/seal_confirmatory_seed.make_commitment`.
- **Refusals.** Refuse loudly (PRIME.4) on:
  - an unknown seed id;
  - a missing or mismatched commitment;
  - `--confirmatory` without the environment variables;
  - a raw integer seed passed on the command line.
- **Provenance.** Write the block LPC.PC.18 requires into `results.json` and the `RESULTS.md` header:
  - the seed id, never the confirmatory value;
  - the code commit and the dirty flag;
  - the preset and full configuration;
  - Python and package versions;
  - the device, and whether JAX x64 is enabled;
  - wall-clock time and peak memory (LPC.PC.22).
- **Labels.** Header label `DEVELOPMENT (DEV-n): not a hypothesis test` or `CONFIRMATORY: UNPROMOTED`.
- **Out of scope:** any change to the scientific computation.

**Definition of done.** All refusals are tested; provenance appears in smoke output; the existing tests still pass; reviewed.

**Acceptance criteria.**

- **Unit tests** for each refusal path, and for the commitment check with a known seed and salt: the expected digest is computed independently in the test with `hashlib`.
- **Smoke regression.** `--seed-id DEV-0` smoke output matches the v1 smoke output's numbers bit for bit on CPU, since DEV-0 equals the v1 default seed. The provenance block is present and parses.
- **Workspace check.** Running with `--confirmatory` in the test environment uses a throwaway ledger fixture, never the real ledger or a real seed.

**Affected checks.** `tests/`; the smoke preset.

**Owner checkpoint.** The owner reviews the seed and provenance code before the freeze (LPC.PC.11).

### Plan amendment 2026-10-10, planner (claude-opus-5-5), under ledger entry 5, before execution (VV.3)

This amendment aligns the plan with ROADMAP.md §2 (sub-tasks WU-0001.1 to .6) and with `main` at 70e19b7. Since the original plan was written, WU-0009, WU-0010 and WU-0011 have landed: tests now live in `tests/unit/test_<module>.py`, tiers come from `tests/conftest.py` and `pytest.ini`, and `tools/test_impact.py` exists. The original plan above stays in force wherever this amendment does not refine it. No acceptance criterion is changed: the criteria quoted below are copied verbatim from ROADMAP §2, and questions Q1 to Q8 hold anything that cannot be met as worded. Work happens in worktree `wu/0001-seeds-provenance`, one commit series per sub-task, in the order .1 → .2 → .3 → .4 → .5 → .6.

Out of scope for the whole unit: any change to the scientific computation (no `make_rng` call, seed arithmetic or estimator changes), `handling` counters (WU-0002.11), `tools/run_preset.sh` (WU-0012.2), and any authorization logic for LPC.AUTH.6 (the owner's act, not code). No new dependency: everything uses the standard library (`resource`, `subprocess`, `platform`, `importlib.metadata`, `hmac`).

**Interfaces (fixed here).**

- **`lpcstudy/seeds.py`** (new; imports `config`):
  - `REGISTRY_SCHEMA = "lpcstudy.seed-registry/1"`;
  - `REGISTRY_PATH` = `<repo>/seeds/development_seeds.json`;
  - `LEDGER_PATH` = `<repo>/docs/agent/governance/ledger.jsonl`;
  - `class SeedRefusal(Exception)`: every message names LPC.PC.7 and never contains a seed or salt value.
  - `load_registry(path: Path) -> dict[str, int]`. Refuses: `schema` ≠ `REGISTRY_SCHEMA`; an id that does not match `^DEV-(0|[1-9][0-9]*)$`; a duplicate id or value; a value that is not an `int` (a `bool` counts as not an `int`) in `[0, 2**64)`.
  - `resolve_dev_seed(seed_id: str, registry: Mapping[str, int]) -> int`.
  - `check_commitment(seed: int, salt_hex: str, ledger_path: Path, seed_id: str = "CONF-1") -> None`. It reads lines with `tools.ledger.read_lines(path)` and refuses a broken chain (`tools.ledger.verify_chain`). It takes the **latest** entry with `type == "commitment"` and `data.seed_id == seed_id`, and compares `data.sha256` with `tools.seal_confirmatory_seed.make_commitment(seed, salt_hex)` using `hmac.compare_digest`. It refuses when there is no entry or no match. The `tools` imports are lazy, inside this function, so development runs never import them. `make_commitment` is imported, never `main()`.
  - `confirmatory_seed(environ: Mapping[str, str], ledger_path: Path) -> int`. Requires both `LPC_CONF_SEED` and `LPC_CONF_SALT`. The seed must match `^[0-9]+$` and be below `2**64`; the salt must be non-empty lowercase hex. Then it calls `check_commitment`.
  - `with_seed(config: StudyConfig, seed_id: str, seed: int) -> StudyConfig`, which is `dataclasses.replace`.
- **`StudyConfig`:** a new last field `seed_id: str = "DEV-0"`, so `asdict` puts it after `seed`. `seed: int = 20261005` is unchanged. No preset changes.
- **`tools/ledger.py`:** `read_lines(path: Path = LEDGER) -> list[str]`, backward compatible. The CLI behavior is unchanged.
- **CLI (`lpcstudy/__main__.py`):**
  - `ArgumentParser(allow_abbrev=False)`, so `--conf` and `--seed` can no longer abbreviate a real flag.
  - `--seed-id ID` (default `None`, which resolves to `DEV-0`; see Q2).
  - `--confirmatory` (store_true), mutually exclusive with `--seed-id`.
  - `--seed` (hidden, `help=SUPPRESS`), which exists only to be refused.
  - `main(argv: list[str] | None = None, *, ledger_path: Path = LEDGER_PATH, registry_path: Path = REGISTRY_PATH) -> int`. The paths can be overridden only from Python, never by a flag or an environment variable, so the commitment cannot be redirected from the command line (Q8).
  - **Refusal contract:** exactly one stderr line `lpcstudy: refused (LPC.PC.7): <reason>`, exit code **64**, emitted before `out_dir.mkdir`, before logging setup and before `Study`.
- **`results["config"]` and the provenance `config`:** `dataclasses.asdict(config)`, with `seed` set to `null` when `seed_id` starts with `CONF-`.
- **`lpcstudy/provenance.py`** (new; imports `config`):
  - `RunClock`: `perf_counter` at construction, `start_utc` (ISO 8601, UTC, seconds), `elapsed() -> float`.
  - `git_state(root: Path) -> tuple[str | None, bool | None, str | None]` runs `git -C root rev-parse HEAD` and `git -C root status --porcelain`, so `dirty = bool(stdout.strip())` and untracked files count. On failure it returns `None, None, <error>`, which is recorded and logged, never silent. `root` is the repo root above the package, and it is read **once, at the start**, before any output is written.
  - `peak_rss_bytes() -> int`: `resource.getrusage(RUSAGE_SELF).ru_maxrss`, multiplied by 1024 on Linux, where the unit is KiB (on Darwin it is already bytes).
  - `device_peak_bytes() -> int | None`: `jax.devices()[0].memory_stats()["peak_bytes_in_use"]` when available, else `None` (the CPU case).
  - `collect(config, seed_id, argv, clock) -> dict` and `finish(block, clock) -> dict`.
  - `header_label(seed_id: str) -> str`: `"DEVELOPMENT (DEV-n): not a hypothesis test"` with the real id, or `"CONFIRMATORY: UNPROMOTED"`.
- **Provenance block `results["provenance"]`.** It is written from the first incremental `save_json` (with `complete: false`) and finished before the final save.

  | Key | Type | Source (LPC.PC.18 / .22 / .13) |
  | --- | --- | --- |
  | `schema` | str `"lpcstudy.provenance/1"` | — |
  | `seed_id` | str | .18 seed id (never the CONF value) |
  | `seed_kind` | `"development"` or `"confirmatory"` | .7 |
  | `label` | str, from `header_label` | .13 |
  | `promoted` | bool, always `false` | .13 |
  | `commit` | str (40 hex) or null | .18 |
  | `dirty` | bool or null | .18 |
  | `git_error` | str or null | PRIME.4 |
  | `preset` | str | .18 |
  | `config` | dict (full, CONF seed nulled) | .18 |
  | `argv` | list[str] | .18 (regeneration) |
  | `python` | str, `platform.python_version()` | .18 |
  | `packages` | dict[str, str or null] for `jax`, `jaxlib`, `optax`, `numpy`, `scipy`, `scikit-learn`, `matplotlib`; `null` means not installed (counted) | .18 |
  | `platform` | str, `platform.platform()` | .18 |
  | `device` | `{backend: str, kind: str, count: int}` from `jax.default_backend()` and `jax.devices()` | .18 / .22 |
  | `jax_x64` | bool, `jax.config.jax_enable_x64` | .18 precision |
  | `jax_matmul_precision` | str or null | .18 precision |
  | `env` | dict[str, str or null] for `JAX_PLATFORMS`, `XLA_FLAGS`, `XLA_PYTHON_CLIENT_PREALLOCATE`, `LPC_THREADS`, `OMP_NUM_THREADS`, `MKL_NUM_THREADS`, `OPENBLAS_NUM_THREADS` (never `LPC_CONF_*`) | .18 determinism |
  | `start_utc`, `end_utc` | str; `end_utc` is null until the end | .22 |
  | `wall_seconds` | float or null: `RunClock` from just after argument validation to just before the final save | .22 |
  | `peak_rss_bytes` | int or null | .22 |
  | `device_peak_bytes` | int or null | .22 |
  | `complete` | bool | — |

  The existing `results["seconds"]` stays unchanged.
- **`RESULTS.md` header** (`report.header_lines(provenance: dict | None) -> list[str]`, called by `write_markdown`; `report` gains no import):
  - the title, then the label line `**DEVELOPMENT (DEV-0): not a hypothesis test** · **UNPROMOTED**` (Q3) or `**CONFIRMATORY: UNPROMOTED**`;
  - then a two-column table of every key above except `config`;
  - then the full configuration as JSON in a `<details>` block.
  - With `--report-only`, the stored block is used as-is. When it is absent, the header line reads `**UNPROMOTED** · provenance absent (output written before WU-0001)`.

**Per sub-task.** The acceptance criteria are copied verbatim from ROADMAP §2 and are fixed.

- **WU-0001.1** (S). **Files:**
  - changed: `lpcstudy/config.py`, `lpcstudy/__main__.py` (seed id only);
  - new: `lpcstudy/seeds.py` (registry part), `tests/unit/test_seeds.py`, `tests/unit/test_config.py`, `tests/unit/test_data.py`, `tests/unit/test___main__.py` (the roadmap's `test_main`, named to the tool's `test_<module>` convention; see Q7);
  - updated by hand: `tests/unit/fixtures/lpcstudy_graph.json` (`__main__` gains `seeds`, plus `seeds: [config]`).

  *DoD:* `python -m lpcstudy --preset smoke --seed-id DEV-0` runs; `config.seed_id` and `config.seed` are in `results.json`. *Criterion:* "Unit: `DEV-0` resolves to 20261005, `DEV-1` to the registry value; `--seed 5` and `--seed-id 5` exit non-zero with a message naming LPC.PC.7; the registry loader rejects a file whose `schema` field differs from `lpcstudy.seed-registry/1`."

  *Tests and references:*
  - **DEV-0:** the literal 20261005 (v1 `config.py`, pilot record).
  - **DEV-1:** the value read by the test with `json.load` on the registry. This is independent of `load_registry`.
  - **Bad registries:** synthetic files in `tmp_path` with a bad schema, a duplicate id, a `bool` value, and a `CONF-1` id.
  - **CLI refusals:** `main([...])` with `capsys` checks exit 64 and `"LPC.PC.7"` in stderr for `--seed 5`, `--seed-id 5`, `--seed-id dev-1` and `--conf`.
  - **`test_config`:** every preset's `(seed_id, seed)` pair equals the registry entry, parsed by the test.
  - **`test_data`:** `make_rng(with_seed(SMOKE, "DEV-1", v).seed, "a", 1)` draws equal `np.random.default_rng([v, zlib.crc32(b"a|1")])` draws. This is NumPy used directly as the reference.
  - All checks are exact (integers and identical streams); no tolerance.
- **WU-0001.2** (M). **Files:** `lpcstudy/seeds.py` (commitment part), `tools/ledger.py` (`read_lines(path)`), `tests/unit/test_tools_ledger.py` (new), additions to `test_seeds.py`.

  *DoD:* commitment check implemented against a ledger file passed as a path. *Criterion:* "Unit: with a throwaway ledger fixture in `tmp_path` holding a `commitment` entry whose digest the test computes independently with `hashlib.sha256(f"{seed}:{salt}".encode()).hexdigest()`, the check accepts the matching pair and rejects a wrong seed, a wrong salt, and a ledger with no `CONF-1` entry. The real ledger and any real seed never appear in tests (asserted: the fixture path is under `tmp_path`)."

  *Tests:*
  - The fixture ledger is built line by line in the test, with `prev_sha256` computed by `hashlib` in the test (an independent chain).
  - The synthetic seed and salt are `123456789012345` and `"0f" * 16`.
  - Added checks (they tighten, they do not change the criterion): a broken chain is refused; with two `CONF-1` entries, only the latest is used; refusal messages contain neither the seed nor the salt.
  - `monkeypatch` points `tools.ledger.LEDGER` at a nonexistent `tmp_path` file, so a stray default read fails loudly.
  - `monkeypatch.delenv("LPC_CONF_SEED"/"LPC_CONF_SALT", raising=False)` runs in every test.
  - `test_tools_ledger` checks that `read_lines(tmp)` returns the non-empty lines in order, and that `read_lines()` with no argument still targets `LEDGER` (a path equality check; the file is not read).
- **WU-0001.3** (S). **Files:** the refusal wiring in `lpcstudy/__main__.py`, `tests/integration/test_cli_seeds.py` (new). *DoD:* every refusal path has a test. *Criterion:* "Integration: each of the four refusal cases exits with a non-zero code and a one-line reason on stderr, and writes no `results.json`. `--confirmatory` is never invoked outside `tmp_path` fixtures (the `settings.json` deny rule stays)."

  *Test:* a parametrized subprocess call to `python -c "import sys; from pathlib import Path; from lpcstudy.__main__ import main; sys.exit(main(sys.argv[2:], ledger_path=Path(sys.argv[1])))" <tmp ledger> ...`, with `--out tmp_path/out`. The environment is built explicitly: `JAX_PLATFORMS=cpu`, with `LPC_CONF_*` removed unless the case sets synthetic values. The cases are:
  1. `--seed-id DEV-99`;
  2. no `CONF-1` commitment, and a mismatched commitment;
  3. `--confirmatory` with neither variable, and with only one of them;
  4. `--seed 5` and `--seed-id 5`.

  *Assertions:* exit 64; exactly one stderr line starting `lpcstudy: refused (LPC.PC.7):`; no `results.json` under `tmp_path` (`rglob`); the out directory was not created.
- **WU-0001.4** (M). **Files:**
  - new: `lpcstudy/provenance.py`, `tests/unit/test_provenance.py`, `tests/unit/test_report.py`;
  - changed: `lpcstudy/report.py` (`header_lines`, called by `write_markdown`), `lpcstudy/__main__.py` (collect, incremental save, finish), the graph fixture (`__main__` gains `provenance`, plus `provenance: [config]`).

  *DoD:* provenance block present in smoke output and the header label correct. *Criterion:* "Unit on a fake results dict: every LPC.PC.18 field is present and typed; the confirmatory value never appears in any output (test greps `results.json` and `RESULTS.md` for the fixture seed value); `commit` equals `git rev-parse HEAD` and `dirty` equals `bool(git status --porcelain)`; `peak_rss_bytes` from `resource.getrusage` is greater than 0; `wall_seconds` is within 1% of the elapsed time measured by the test."

  *Tests and references:*
  - **Fields and types:** every key in the table above with its type, on a fake results dict (`systems: {}`, a `verdicts` stub per `HYPOTHESES` key). Written with `save_json` and `write_markdown` into `tmp_path`, for `DEV-0` and for `CONF-1` with the fixture seed `987654321987654321`. `str(seed)` is grepped in both files and must be absent. The exact label strings are asserted.
  - **Git state:** the test's own `subprocess` calls to `git rev-parse HEAD` and `git status --porcelain` at the same moment.
  - **`peak_rss_bytes`:** greater than 0. Proposed tightening for the applied mathematician: on Linux, `VmHWM` from `/proc/self/status` (an independent kernel counter) read before and after, so `1024·VmHWM_before ≤ peak_rss_bytes ≤ 1024·VmHWM_after`.
  - **`wall_seconds`:** `t0 = perf_counter(); clock = RunClock(); sleep(1.0); w = clock.elapsed(); t1 = perf_counter()`, then `|w − (t1 − t0)| ≤ 0.01·(t1 − t0)`. Both clocks span the same sleep, so the tolerance has to absorb only two call gaps (microseconds) plus one possible preemption, which is under 10 ms at 1 s. The sleep cancels, so the test fits the 5 s unit budget.
  - **`python`:** equals `"%d.%d.%d" % sys.version_info[:3]`.
  - **`packages`:** each equals the pin parsed from `requirements.txt` by the test. A mismatch is a real LPC.PC.17 finding, not a test to loosen.
  - **`jax_x64`:** equals `jnp.zeros(1).dtype == float64` after `import lpcstudy.systems`.
  - **`device.backend`:** `"cpu"` under `JAX_PLATFORMS=cpu`.
- **WU-0001.5** (S). **Files:** none, unless the comparison fails. *DoD:* numbers unchanged by the unit. *Criterion:* "On CPU, `--seed-id DEV-0` smoke `results.json` equals `runs/baseline/smoke/results.json` bitwise after removing `provenance`, `seconds` and `handling` keys (the unit adds nothing else); the provenance block parses."

  *Method:*
  1. On a **committed, clean** tree, run `JAX_PLATFORMS=cpu XLA_PYTHON_CLIENT_PREALLOCATE=false LPC_THREADS=4 OMP/MKL/OPENBLAS=4 python -m lpcstudy --preset smoke --seed-id DEV-0 --out <worktree>/runs/dev/wu0001-5` (`runs/` is gitignored), once. The reference is `/home/brianm/projects/physics/chaos/lpcstudy/runs/baseline/smoke/results.json`, read-only, with sha256 `0da48771…4b79` re-checked first.
  2. Apply a one-off `python -c` comparison, recorded in the Log: load both files; delete the top-level `provenance` and every `seconds` and `handling` key at any depth, counting each deletion per file (`handling` is expected to be 0 in both, since it does not exist before WU-0002.11); compare `json.dumps(obj, sort_keys=True, allow_nan=True)` strings for equality. This is canonical text, so NaN compares equal to NaN and floats compare exactly by repr round-trip; it is the method WU-0009.3 used.
  3. Report the counts and the first differing path if any.
  4. Check that `provenance` has `seed_id == "DEV-0"`, `complete == true`, `dirty == false` and `device.backend == "cpu"`.

  Tolerance: exact. CPU determinism on this machine was established in WU-0009.3. **Blocked as worded by Q1** (`config.seed_id`).
- **WU-0001.6** (S). A fresh `reviewer` runs `/independent-review`, with at most two fix rounds (DEVELOPMENT_WORKFLOW §2.3). The main session marks "needs owner review before freeze" in `queue.md`. *Criterion:* "Reviewer verdict `approve` or `approve with fixes` with every finding resolved; rounds within DEVELOPMENT_WORKFLOW §2.3."

**Affected checks** (DEVELOPMENT_WORKFLOW §4.2 as implemented by `tools/test_impact.py`, plus hand additions for the Q2 gap, DEC-0003). Unit radius per sub-task; one integration run, deferred to .5 and recorded (§4.8).

| Sub-task | Changed | Rule | Unit files | Integration |
| --- | --- | --- | --- | --- |
| .1 | `config.py` (core), `seeds.py` (new), `__main__.py`, fixture JSON | core: own + transitive dependents; fixture → tests naming it | `test_config`, `test_seeds`, `test_data`, `test___main__`, `test_allocation`, `test_analysis`, `test_ensemble`, `test_oracle`, `test_tools_test_impact` | deferred to .5 |
| .2 | `seeds.py`, `tools/ledger.py` | module: own + direct dependents; tool → `test_tools_ledger`; **by hand:** `test_seeds` imports `tools.ledger` (Q2 gap) | `test_seeds`, `test___main__`, `test_tools_ledger` | — |
| .3 | `__main__.py`, new integration file | pipeline: own + integration | `test___main__` | `tests/integration/test_cli_seeds.py` |
| .4 | `provenance.py` (new), `report.py`, `__main__.py`, fixture | pipeline: own + direct dependents + integration | `test_provenance`, `test_report`, `test___main__`, `test_tools_test_impact` | deferred to .5 |
| .5 | none | §4.2: the manual smoke run and `test_smoke_pipeline.py` are the same evidence, so run one | — | manual smoke (above) + `test_cli_seeds.py`, once |

The tool checks are integration and unit only, never `slow` or `gpu`. No `requirements.txt` change. `test_smoke_pipeline.py` stays valid **unchanged** with the default `DEV-0` (Q2); the merge gate runs it. If the owner makes `--seed-id` required, that file gains `--seed-id DEV-0` and joins the .5 radius instead of the manual run.

**Risks.**

- **The confirmatory seed is never drawn, read or run.**
  - Tests use only synthetic seeds and `tmp_path` ledgers.
  - Every test clears `LPC_CONF_*`.
  - No test reads the real ledger.
  - No agent invokes `--confirmatory` from Bash (the deny rule stays). `allow_abbrev=False` closes the `--conf…` abbreviation bypass.
  - `seal_confirmatory_seed.main` is never called.
- **The confirmatory value leaks into outputs.** It is nulled in `config` and never logged. The reviewer greps `lpcstudy/` for `config.seed`/`cfg.seed` in log calls and f-strings: the end-to-end CONF pipeline is never run in tests, so `run.log` and figures are checked by review only.
- **Bitwise comparison.** `config.seed_id` is a new key in the compared JSON (Q1). The baseline has 5 `seconds` keys at several depths, and all of them must be removed. `handling` is absent now, so its removal must be counted (0), not assumed. NaN needs canonical-text comparison.
- **Dirty flag.** It is read at start, so a run writing into `runs/` (ignored) does not flip it. Running .5 on an uncommitted tree gives `dirty: true` (allowed, but recorded).
- **The import graph changes.** The fixture must be edited by hand in the same commit, or `test_graph_equals_hand_derived_fixture` fails, which is correct behavior. DEVELOPMENT_WORKFLOW §4.2's graph table also needs rows for `seeds` and `provenance` (main session; Q7).
- **Shared CPU.** At most 4 threads. Each refusal subprocess imports jax (about 3 s × 8, about 25 s for the integration tier).

**Owner checkpoint (LPC.PC.11).** Seed and provenance code: **needs owner review before freeze**. Verdict and statistics code is not touched. Dependencies: none added.

**Questions for the owner.**

- **Q1 (blocks .5 as worded).** WU-0001.1's DoD puts `config.seed_id` into `results.json`, but WU-0001.5 compares after removing only `provenance`, `seconds` and `handling` and says "the unit adds nothing else". Both cannot hold. Proposed DEC text: *"WU-0001.5 also removes the single key `config.seed_id` before comparison; every other key, including `config.seed`, is compared exactly."*
- **Q2.** Should `--seed-id` default to `DEV-0` when omitted? The default keeps `test_smoke_pipeline.py` and the current commands valid, and the provenance records the id. Making it required is stricter. The planner proposes the default, with the run log stating "seed id defaulted to DEV-0".
- **Q3.** LPC.PC.13 marks every output `UNPROMOTED` and development outputs additionally with the DEV label. The plan prints both on development headers (the roadmap string is kept exactly). Confirm.
- **Q4 (blocker outside this unit, verified).** sklearn's `random_state` accepts only values below `2**32`: `check_random_state(2844678021587022684)` raises `ValueError`. `analysis.py:295, 678, 680` and `allocation.py:358` pass `config.seed`, so DEV-1 to DEV-4 and any 62-bit CONF seed will crash, which blocks the WU-0003 rehearsal and "smoke on DEV-3". Fixing it changes numbers, so it cannot be done in WU-0001 (.5). Proposal: open a DEF and fix it in WU-0002 (for example, derive each `random_state` from `make_rng(seed, label)`), accepting the DEV-0 change through the WU-0002.12 regression. Related: `experiments.py:88` and `dynamics.py:147` call `np.random.default_rng(seed)` directly, against the `make_rng`-only rule.
- **Q5.** `tools/ledger.py` gains an optional `path` argument on `read_lines`. The CLI behavior and the chain format are unchanged. Acceptable?
- **Q6.** Should a confirmatory run refuse when `dirty` is true or the commit is unknown? This is not in the criteria and is not implemented. It is a candidate for the WU-0004 freeze checklist.
- **Q7.** Tool gaps:
  - The tool maps `__main__` to `test___main__.py` (used here) rather than the roadmap's `test_main`.
  - A change to `tools/ledger.py` or `tools/seal_confirmatory_seed.py` does not select `test_seeds`/`test_cli_seeds` (the Q2 gap); this needs a by-hand rule until DEC-0003 is decided.
  - DEVELOPMENT_WORKFLOW §4.2's graph table needs rows for `seeds` and `provenance`.

  These are for the main session.
- **Q8.** The ledger and registry paths can be overridden only as Python parameters of `main` (used by tests), never by a flag or an environment variable. Confirm this is preferred over a `--ledger` flag.

## Log

### 2026-10-10 developer (claude-sonnet-5-5), WU-0001.1: start

Decisions of the developer within the plan (no criterion changed):

- Q5: `tools/ledger.py` is NOT changed. `seeds.check_commitment` reads the ledger file itself (`Path.read_text`, non-empty lines) and calls only `tools.ledger.verify_chain(lines)` (it takes lines, not a path) and `tools.seal_confirmatory_seed.make_commitment`. So `read_lines(path)` is not needed (the Q5 "only if impossible" condition is not met), `tools/ledger.py` and `tests/unit/test_tools_ledger.py` are not touched, and .2 has one file fewer than the plan table lists. The `monkeypatch` of `tools.ledger.LEDGER` guard in the plan is kept in the .2 tests.
- Argument errors: the parser uses `parse_known_args`; any leftover token is refused with exit 64 and one line (option names only, values never echoed), so `--conf` (abbreviation attempt) is a refusal, not an argparse exit 2. `--seed` is `nargs="*"` and hidden; its presence is always refused. `--confirmatory` is added in .3 (until then it is an unrecognized option and refused).
- `tests/unit/test_tools_test_impact.py::test_fixture_schema` hard-codes the module count (`len(stems) == 18`). Adding `seeds.py` makes it 19 (20 with `provenance.py` in .4). This count is a fact about the package, not a tolerance; edited with the fixture, same commit. The stems-equality check, the independent part, is unchanged.
- Hook note: the Bash tool blocks any command naming the seal script, so its source was read with the Read tool (source only; no seed or salt exists in it).

§4.9 checklist, WU-0001.1 run (unit radius):

1. Change set: `lpcstudy/{__main__,config,seeds}.py`, `tests/unit/fixtures/lpcstudy_graph.json`, `tests/unit/test_{seeds,config,data,__main__,tools_test_impact}.py` (new except the last), this unit file.
2. Radius: `tools/test_impact.py --base main --explain` selects 9 unit files (`test___main__ test_allocation test_analysis test_config test_data test_ensemble test_oracle test_seeds test_tools_test_impact`) plus `tests/integration` (config is core). The plan defers the integration smoke to .5 (table row .1); the unit set is far smaller than the suite.
3. Already run: no.
4. Device: `JAX_PLATFORMS=cpu`.
5. Threads: `LPC_THREADS=4`, `OMP/MKL/OPENBLAS_NUM_THREADS=4`; unit tier (<5 s per test).
6. Contention: no `pilot`/`full`/`slow`/`gpu` run by me; unit tier only.
7. Output: `-q --tb=short -rfE`.
8. Command: `JAX_PLATFORMS=cpu XLA_PYTHON_CLIENT_PREALLOCATE=false LPC_THREADS=4 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 .venv/bin/python -m pytest -q --tb=short -rfE <the 9 files>` (tools/run_tests.sh does not exist yet).

Result: `103 passed in 1.30s`. Self-check of the diff: no `clip|nan_to_num|isfinite|where(|try:|except` outside `seeds.py` (`try/except` there converts `OSError`/`ValueError`/`ImportError` into a loud `SeedRefusal`; nothing is swallowed); no `default_rng|random.|PRNGKey` in `lpcstudy/` changes (the tests use `np.random.default_rng([v, crc32])` as the stated reference); no tolerance in any assert.

Commit `b2c7b44` (WU-0001.1).

### 2026-10-10 developer (claude-sonnet-5-5), WU-0001.2: commitment check tests

The code (`check_commitment`, `confirmatory_seed`) was written with `seeds.py` in .1 and is first tested here. §4.9 checklist:

1. Change set: `tests/unit/test_seeds.py` (additions), this unit file. No `lpcstudy/` or `tools/` change in .2 (Q5: `tools/ledger.py` is not edited).
2. Radius: per the plan table row .2 without `tools/ledger.py`: `test_seeds` (changed test file) and `test___main__` (direct dependent of `seeds`); `test_tools_ledger` does not exist because `read_lines` is not changed. `test_seeds` imports `tools.ledger` (the Q2 gap, handled by hand: it is in the set). Far smaller than the suite.
3. Already run: no (the .1 run did not contain these tests).
4. Device: `JAX_PLATFORMS=cpu`.
5. Threads: 4; unit tier.
6. Contention: none.
7. Output: `-q --tb=short -rfE`.
8. Command: as in .1 with files `tests/unit/test_seeds.py tests/unit/test___main__.py`.

Result: `84 passed in 0.81s`. Self-check: only test files changed; fixture ledgers are asserted outside the repository; `LPC_CONF_*` deleted and `tools.ledger.LEDGER` monkeypatched in an autouse fixture; no tolerance.

Commit `10b7913` (WU-0001.2).

### 2026-10-10 developer (claude-sonnet-5-5), WU-0001.3: the confirmatory flag and its refusals

Code: `__main__.py` gains the confirmatory flag (mutually exclusive with `--seed-id`, refused with exit 64 if both; seed and salt only via `seeds.confirmatory_seed(os.environ, ledger_path)`), and `results["config"]` carries `seed: null` for a `CONF-*` id (moved to `provenance.config_record` in .4). Hook note: the Bash tool blocks any command text containing the flag, so the .3 source and test files were written with the Edit/Write tools (the hook scans commands, not files); no command with the flag was run. The flag is exercised only in-process in `test___main__.py` (synthetic seed, tmp_path ledger) and in the subprocess cases of the plan's `tests/integration/test_cli_seeds.py` (tmp_path ledger, synthetic values, `LPC_CONF_*` stripped from the child environment first).

§4.9 checklist, WU-0001.3 run:

1. Change set: `lpcstudy/__main__.py`, `tests/unit/test___main__.py`, `tests/integration/test_cli_seeds.py` (new), this unit file.
2. Radius: plan row .3, `__main__` is a pipeline module: own + integration: `tests/unit/test___main__.py` and `tests/integration/test_cli_seeds.py` (the plan names the new file; the smoke test `test_smoke_pipeline.py` is deferred to .5, where the manual smoke run is its evidence). Smaller than the suite.
3. Already run: no (`test___main__` last ran before this change).
4. Device: `JAX_PLATFORMS=cpu`.
5. Threads: 4; the 8 subprocess cases import jax once each (about 3 s), timeout 120 s per case.
6. Contention: no `pilot`/`full` run by me; other agents share the CPU.
7. Output: `-q --tb=short -rfE`.
8. Command: as in .1 with `tests/unit/test___main__.py tests/integration/test_cli_seeds.py`.

Result: `31 passed in 7.91s`. Self-check: `os.environ` read only in `choose_seed`; no `clip|nan_to_num|isfinite|where(|try:|except` added in `lpcstudy/__main__.py`; no randomness added; no tolerance.

Commit `90c63c3` (WU-0001.3).

### 2026-10-10 developer (claude-sonnet-5-5), WU-0001.4: provenance block and report header

Code: new `lpcstudy/provenance.py` (`RunClock`, `git_state`, `peak_rss_bytes`, `device_peak_bytes`, `header_label`, `config_record`, `collect`, `finish`); `report.header_lines` called by `write_markdown`; `__main__` collects the block after seed validation and before any output (`out_dir.mkdir`), writes it from the first `save_json`, finishes it before the final save, and logs the commit, dirty flag, any `git_error` (warning) and the count of uninstalled packages (warning). `--report-only` collects nothing and uses the stored block as-is. `try/except` sites: `provenance.git_state` (OSError, RuntimeError, SubprocessError become the recorded `git_error` text) and `provenance._package_versions` (`PackageNotFoundError` becomes a recorded `null`); both are counted/logged by `__main__`. Fixture graph updated by hand: `__main__` + `provenance`, new `provenance: [config]`; `test_fixture_schema` count 19 to 20. In `test___main__.py` two fake-study tests check the incremental `complete: false` first save and `true` last save, and that a faked confirmatory run saves no seed value.

§4.9 checklist, WU-0001.4 run:

1. Change set: `lpcstudy/{__main__,report,provenance}.py`, `tests/unit/fixtures/lpcstudy_graph.json`, `tests/unit/test_{provenance,report,__main__,tools_test_impact}.py`, this unit file.
2. Radius: plan row .4: `test_provenance`, `test_report`, `test___main__`, `test_tools_test_impact` (tool output for `provenance.py`/`report.py`/`__main__.py`/fixture, plus the unit files; `config.py` is unchanged in .4, so the core set is not re-run). `tests/integration` is deferred to .5 as the plan's table says. Smaller than the suite.
3. Already run: no (these files are new or changed since the last run).
4. Device: `JAX_PLATFORMS=cpu`.
5. Threads: 4; unit tier; the wall-clock test sleeps 1 s.
6. Contention: none from me.
7. Output: `-q --tb=short -rfE`.
8. Command: as in .1 with `tests/unit/test_provenance.py tests/unit/test_report.py tests/unit/test___main__.py tests/unit/test_tools_test_impact.py`.

Result of run 1: `1 failed, 89 passed in 3.59s`. Failure: `test_peak_rss_is_positive_and_bracketed_by_the_kernel_counter`: `1024*640828 <= 653611008` false, i.e. `ru_maxrss` was 2.6 MB (0.4%) below `1024*VmHWM` read just before. Diagnosis: the bracket is the planner's *proposed tightening* ("for the applied mathematician"), not the roadmap criterion (which is `peak_rss_bytes > 0`, still asserted exactly). `getrusage` reads the per-CPU RSS counters approximately while `/proc/self/status` sums them, so equality at the byte level is not a property of the kernel. The code is correct (`ru_maxrss * 1024`); the reference had no slack. Fix, in the test only: slack `ncpu * max(32, 2*ncpu) * pagesize` (8 MiB at 32 CPUs, a bound on the per-CPU counter approximation error), stated in the docstring; a wrong unit (factor 1024) is still caught. This adds a tolerance to a proposed check that never held; no criterion changed. FLAGGED FOR THE REVIEWER and the applied mathematician: confirm or reject the slack formula; if rejected the check reduces to the criterion `> 0`.

`--lf` on the failing test: `1 passed, 15 deselected in 0.21s`. Radius once more after the test change: `90 passed in 2.34s`. Self-check: each `try/except` in the diff is listed above and reports (git_error, null package) or refuses (seeds); no `clip|nan_to_num|isfinite|where(`; no `default_rng|random.|PRNGKey` in `lpcstudy/`; the only tolerances are the existing-by-plan 1% wall-clock check and the RSS slack flagged above.

Commit `ed6dacb` (WU-0001.4).

### 2026-10-10 developer (claude-sonnet-5-5), WU-0001.5: smoke regression against the v1 baseline

Method as in the plan. Clean committed tree at `ed6dacb0ed5714a122c7c85fcb3ca5a53453043d` (`git status --porcelain` empty, no `lpcstudy --preset` run active). Reference `/home/brianm/projects/physics/chaos/lpcstudy/runs/baseline/smoke/results.json` read-only, sha256 re-checked: `0da48771ee967525f71518d4bb6e7aec675349ff175a2d4544234d4f8f084b79` (matches `0da48771…4b79`).

Run, once, CPU, in the foreground (about 30 s wall, so no background needed): `JAX_PLATFORMS=cpu XLA_PYTHON_CLIENT_PREALLOCATE=false LPC_THREADS=4 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 .venv/bin/python -m lpcstudy --preset smoke --seed-id DEV-0 --out <worktree>/runs/dev/wu0001-5` -> exit 0, "study finished in 25s", output under `runs/dev/wu0001-5/smoke/` (gitignored).

Comparison (one-off `python` script, scratchpad, not committed): load both files; delete the top-level `provenance`, every `seconds` and `handling` key at any depth and (DEC-0004 Q1) `config.seed_id`, counting each; compare `json.dumps(obj, sort_keys=True, allow_nan=True)`.

- Removed in the baseline: `seconds` 5, `handling` 0, `provenance` 0, `config.seed_id` 0 (absent in v1).
- Removed in the new file: `provenance` 1, `seconds` 5, `handling` 0, `config.seed_id` 1.
- Result: **equal** (both canonical texts 61786 characters). No differing path. Nothing else was removed.
- Provenance of the new file: `seed_id` DEV-0, `complete` true, `dirty` false, `git_error` null, `commit` `ed6dacb0…`, `device` `{backend: cpu, kind: cpu, count: 1}`, `jax_x64` true, all seven package versions equal the `requirements.txt` pins, `wall_seconds` 25.30, `peak_rss_bytes` 1298530304, 24 keys, parses as JSON. `RESULTS.md` line 3 is `**DEVELOPMENT (DEV-0): not a hypothesis test** · **UNPROMOTED**`.

§4.9 checklist, `tests/integration/test_cli_seeds.py` once (plan row .5: manual smoke plus this file once; `test_smoke_pipeline.py` is not run because the manual smoke run above is the same evidence):

1. Change set: none since `ed6dacb` (this log excepted); the branch diff is `lpcstudy/{__main__,config,seeds,provenance,report}.py` and tests.
2. Radius: `tests/integration/test_cli_seeds.py` only (code changed in .4 since its .3 run; a new run on new code).
3. Already run: only on the .3 code; `__main__.py` has changed since, so this is a run on different code.
4. Device: `JAX_PLATFORMS=cpu`.
5. Threads: 4; eight subprocess cases, timeout 120 s each.
6. Contention: the smoke run has finished; no other preset run seen.
7. Output: `-q --tb=short -rfE`.
8. Command: as in .1 with `tests/integration/test_cli_seeds.py`.

Result: `8 passed in 6.61s`.

State at hand-over (for the reviewer): unit and integration radius runs per sub-task are recorded above; `tests/integration/test_smoke_pipeline.py` and the whole suite were not run (merge gate, main session). Open points: (a) the RSS bracket slack in `test_provenance` (flagged under .4); (b) `test_fixture_schema` module count edited 18 to 19 to 20 with the graph fixture; (c) `--report-only` resolves the seed id (and, with the confirmatory flag, would need the environment) before it reads `results.json`, a consequence of refusing uniformly; (d) DEF-0010 untouched: DEV-1 to DEV-4 are not runnable on a preset until it is fixed; (e) DEVELOPMENT_WORKFLOW §4.2 graph table rows for `seeds` and `provenance` are for the main session (Q7).

### 2026-10-10 Mathematics review of the peak-RSS tolerance (R1), applied-mathematician, claude-opus-5-5

No test was run. I used scratch probes only (`rss_probe.py` and `vfork_probe.py` in the session scratchpad; no suite, CPU, a few seconds each). Machine facts: kernel 7.2.9, 32 online CPUs, 4096 B pages. The headers came from `/lib/modules/7.2.9-2-cachyos/build/include/linux/mm.h`. The `.c` sources (`kernel/sys.c`, `fs/proc/task_mmu.c`, `lib/percpu_counter.c`, `fs/exec.c`) are not installed, so the statements about them below are from memory and confirmed by the probes. They are flagged for `researcher` if a citation is wanted.

**What the two numbers are** (in pages; n = online CPUs).
- Since Linux 6.2 the per-thread `SPLIT_RSS_COUNTING` caches (sync after 64 events per thread) are gone. The caller's thread-based model applies only to kernels before 6.2. The mm RSS is now `percpu_counter rss_stat[]` (header: `get_mm_counter = percpu_counter_read_positive`, `get_mm_rss` = FILE + ANON + SHMEM).
- Each counter has an exact value `E_i`. The kernel stores it as a central `count` plus per-CPU deltas. `percpu_counter_add_batch` keeps every delta at most `b - 1` in absolute value, with `b = percpu_counter_batch = max(32, 2n)`.
- The approximate read `A = Σ max(0, count_i)` therefore satisfies `|A - E| <= T := 3 n (b - 1)` pages. The clamp at 0 only moves `A` toward `E >= 0`.
- `mm->hiwater_rss = H` is raised only by `update_hiwater_rss` (an approximate read), called on the unmap and zap paths just before RSS falls. It never falls unless someone writes `clear_refs`.
- `ru_maxrss` (RUSAGE_SELF) = `max(S, H, A_now) * PAGE_SIZE/1024` KiB. Here `S = signal->maxrss` is the hiwater of the image that this process exec'd from. It is always a whole number of pages.
- `VmHWM` = `max(H, E_now)` in kB. `task_mem` uses `get_mm_counter_sum`, the exact sum, on recent kernels (about 6.16 and later as I recall). On 6.2 to 6.15 it is the approximate read.

**Probes.**
1. Batch: on one pinned CPU, the deficit `1024·VmHWM − 1024·ru_maxrss` has a sawtooth of period exactly 64 pages. This gives b = 64 = max(32, 2·32).
2. Adversarial case: pin to each of the 32 CPUs in turn, flush, then touch b − 1 pages, for the anon counter and then the shmem counter. The deficit is 2036 pages after anon and 4052 pages (16.6 MB) after anon plus shmem. That is n(b − 1) = 2016 pages per counter, so the per-counter bound is attained. The file counter takes the same code path and adds up to 2016 more. The bound is T = 6048 pages = 24.77 MB.
3. Typical case: three runs of `import lpcstudy.provenance`, then `before`, `peak`, `after`. `1024·before` is about 182 MB and `peak − 1024·before` is −0.60, −0.78 and −0.86 MB. The developer's pytest run showed −2.6 MB at 650 MB. Every `peak` is a multiple of 4096.
4. The `S` term: a child exec'd from a Python that had touched 200 MB, by vfork (`subprocess`), by fork (`preexec_fn`) or by `sh -c` exec-in-place, reports `ru_maxrss` of 213 to 218 MB against `VmHWM` of 11 MB. A fresh fork from a small `bash` resets it (11.8 MB against 11.8 MB). In this harness pytest's parent is a forked `bash` with 4 MB, so `S` is small here.

**Derivation.** Assumptions:
- (A1) Kernel 6.2 or later (percpu RSS counters).
- (A2) No CPU hotplug during the test process.
- (A3) No `clear_refs` write.
- (A4) No reclaim or swap-out of this process's pages between the two `/proc` reads, i.e. every RSS decrease in the window goes through an `update_hiwater_rss` path.
- (A5) `S <= 1024·VmHWM_after + 2T`: the process was not exec'd, directly or through exec-in-place, from a process with a larger peak.

Under these, `VmHWM_before − 2T <= ru_maxrss <= VmHWM_after + 2T` (pages):
- Lower side: `ru >= H_before` and `ru >= E − T`. Any fall in the window first raises `H` to at least `E_before − T`. That gives a slack of T when `/proc` is exact (this kernel), and 2T when `/proc` is also approximate (6.2 to 6.15).
- Upper side: `A <= E + T`. `E` at the read is at most `VmHWM_after`, or at most `VmHWM_after + T` if RSS fell in the window, which gives 2T.

I use 2T on both sides so that the one formula holds on the GPU workstation's kernel too. The bound does not depend on the number of threads.

**Error-detection matrix.** This machine has E ≥ 182 MB and 2T = 49.5 MB.

| Mistake | Wrong value | Bracket ±2T | Ratio [0.5, 2] (R1 proposal) | `peak % page == 0` |
| --- | --- | --- | --- | --- |
| ×1024 forgotten (KiB/bytes) | E/1024 | caught when E > 2T | caught | caught, unless pages ≡ 0 mod 1024 (1/1024) |
| ×4096 (KiB treated as pages) | 4E | caught when E > 2T/3 | caught | not caught |
| factor 2 | 2E | caught when E > 2T | **not caught** | not caught |
| ×1000 (kB/KiB) | 0.977E | not caught (4 MB < 2T) | not caught | caught, unless pages ≡ 0 mod 128 |
| `(ru + 1)·1024` | E + 1 KiB | not caught | not caught | caught (exact) |
| +1 page | E + 4096 B | not caught | not caught | not caught |

A one-page additive error cannot be resolved by any reference here, because kernel noise is about 10³ pages; it is 0.002% of the peak. The bracket is valid for any E; only its power depends on E. The ratio bracket is not independent of kernel internals either: it is valid only when E ≥ 2T. On a 64-CPU host T = 100 MB, so the ratio bracket would also need about 200 MB.

**Recommendation.** Keep `> 0` (the criterion). Add the exact page-multiple check. Replace the slack with the derived bound:
```python
    page = resource.getpagesize()
    before = hwm()
    peak = provenance.peak_rss_bytes()
    after = hwm()
    online = os.sysconf("SC_NPROCESSORS_ONLN")
    counter_error = 3 * online * (max(32, 2 * online) - 1) * page
    assert peak % page == 0, f"peak {peak} B is not a whole number of {page} B pages"
    assert 1024 * before - 2 * counter_error <= peak <= 1024 * after + 2 * counter_error, (
        f"peak {peak} B outside [{1024 * before}, {1024 * after}] B +- {2 * counter_error} B")
```
Use `os.sysconf`, not `os.cpu_count()`: in Python 3.13, `PYTHON_CPU_COUNT` and `-X cpu_count` override `os.cpu_count()`, and the kernel batch follows the online CPUs. The docstring paragraph to paste:

> Tolerance. Since Linux 6.2 the RSS is three `percpu_counter`s (file, anon, shmem). `getrusage` reads them approximately; each per-CPU delta is below the batch `b = max(32, 2n)` (n = online CPUs), so the read is within `T = 3 n (b - 1)` pages of the exact sum (24.8 MB at n = 32; attained per counter in a probe, WU-0001 Log 2026-10-10). `VmHWM` is the exact sum (approximate before about 6.16) and `mm->hiwater_rss` is refreshed by an approximate read before RSS falls, so `1024 VmHWM_before - 2T <= peak <= 1024 VmHWM_after + 2T`. Assumptions: no CPU hotplug, `clear_refs` or reclaim between the two reads; the process was not exec'd (vfork, fork or exec-in-place) from a process whose peak exceeds the upper bound, because `ru_maxrss` includes the pre-exec image (`signal->maxrss`), which `VmHWM` does not; a failure on the upper side with a large launcher is that, not a code defect. Power: with `1024 VmHWM >= 182 MB` (after importing jax) and `2T = 49.5 MB`, the bracket rejects a missing `x1024` (E/1024), `x4096` (4E) and any factor-2 error. `ru_maxrss` is pages x PAGE_SIZE/1024 KiB, so `peak % pagesize == 0` holds exactly and also catches `x1000` and sub-page offsets. Neither check resolves a one-page additive error (kernel noise is about 10^3 pages).

**Verdict on the existing slack.** It is not acceptable as written:
- (i) It bounds one counter, not three. The probe exceeded it with two counters: 4052 pages against 2048 pages.
- (ii) It uses `os.cpu_count()`, which can be overridden.
- (iii) It leaves the `S` (pre-exec) assumption of the upper side unstated.
- It would rarely flake in practice, since typical deficits are 0.6 to 2.6 MB, but it is not a derived bound.

The reviewer's ratio bracket is valid here, but it misses factor-2 errors and its validity also rests on E ≥ 2T.

**Note for the main session.**
- The replacement 2T (49.5 MB) is wider than the developer's 8 MiB. Against the fixed criterion (`> 0`) it is a tightening. Against the planner's zero-slack proposal, which was never a kernel property, it is a correction, not a loosening to pass. Record it in `decisions.md`, as R1 asks.
- Out of scope for the test, but relevant to the meaning of LPC.PC.22: `peak_rss_bytes` can report the launcher's peak, not the study's (probe 4). Consider also recording `VmHWM` on Linux, or documenting this. This is for the planner or developer; I made no code change.

### 2026-10-10 developer (claude-sonnet-5-5), fix round 1: R1 to R4

- R1: in `test_provenance.py` the 8 MiB slack is replaced by exactly the applied-mathematician's assertion: `peak % pagesize == 0` and `1024*VmHWM_before - 2*counter_error <= peak <= 1024*VmHWM_after + 2*counter_error`, `counter_error = 3*online*(max(32, 2*online) - 1)*pagesize`, `online = os.sysconf("SC_NPROCESSORS_ONLN")`; `peak > 0` kept; the docstring carries the mathematician's tolerance paragraph and the launcher-peak limitation. The same limitation is in the `peak_rss_bytes` docstring in `lpcstudy/provenance.py`. No schema change (no new field). DEC-0006 (proposed, on main) is not edited here.
- R2: `choose_seed` echoes an unrecognized dash token only if it is one of the parser's known option strings, else `<value>`; a new test `test_unrecognized_token_is_never_echoed` covers `-424242424242`, `--424242424242`, `--conf`, `--conf=424242`, `--seed-i` and checks that no part of the token is on the one stderr line.
- R3: the 1% check is now on `provenance.finish(block, clock)["wall_seconds"]` (block collected on the same clock, reference span `t1 - t0` around collect, the 1 s sleep and finish). Tolerance still 1%; the span exceeds 1 s so 1% (about 10 ms) is well above timer noise.
- R4: `source_commit` of `lpcstudy_graph.json` is now `ed6dacb0ed5714a122c7c85fcb3ca5a53453043d` (the commit at which the graph matched the imports and the comparison test passed), and one dated sentence is appended to `description`. Edited by hand; the graph itself is unchanged.

§4.9 checklist, fix round 1 run:

1. Change set: `lpcstudy/{__main__,provenance}.py`, `tests/unit/{test___main__,test_provenance}.py`, `tests/unit/fixtures/lpcstudy_graph.json`, this unit file (with the uncommitted `## Review`, committed as is).
2. Radius: `test___main__` (changed `__main__`, direct dependent of `provenance`), `test_provenance`, `test_tools_test_impact` (fixture) and `tests/integration/test_cli_seeds.py` (`__main__` changed). `test_report` and `test_seeds` import no changed code. Smaller than the suite; the smoke integration test is not selected (no computation path changed).
3. Already run: not on this code.
4. Device: `JAX_PLATFORMS=cpu`.
5. Threads: 4; unit tier plus 8 short subprocess cases.
6. Contention: no preset run by me.
7. Output: `-q --tb=short -rfE`.
8. Command: as in .1 with `tests/unit/test___main__.py tests/unit/test_provenance.py tests/unit/test_tools_test_impact.py tests/integration/test_cli_seeds.py`.

Result: `97 passed in 11.43s`. Self-check: no new `clip|nan_to_num|isfinite|where(`; the new `try/except` count is zero; no randomness added; the only tolerances are the 1% (unchanged) and the mathematician's derived 2T bracket (no other test tolerance changed).

### Resolution of findings and merge-gate checklist, 2026-10-10, claude-sonnet-5-5 (main session)

- **R1 to R4: fixed in 80dbb57** (re-review: all fixed, approve). The RSS bound is the applied-mathematician's derived bracket, recorded as `DEC-0006` (proposed) on `main`.
- **Owner review needed before the freeze** (seed and provenance code, LPC.PC.11); to be marked in the queue. `DEC-0004` (Q1: the WU-0001.5 comparison also removes `config.seed_id`) and `DEC-0006` are still **proposed**; the numbers are bitwise equal to the baseline either way. Flagged for the owner, not a blocker for the merge, which needs the owner's approval at the prompt.
- **Not in this unit:** DEF-0010 (seeds of 2**32 or more crash scikit-learn), so only DEV-0 can run a preset.

Merge-gate checklist (§4.9, §4.3):

1. **Change set:** `git diff --name-only main...HEAD`: new `lpcstudy/` modules for seeds and provenance, `__main__.py`, `config.py`/`report.py` as planned, new tests under `tests/unit/` and `tests/integration/test_cli_seeds.py`, the hand-edited graph fixture, `tests/unit/test_tools_test_impact.py` (module count), this unit file. `main` was merged into the branch (3066684) so the gate runs on what will be merged. `git status --porcelain` is empty after the commit that carries this entry.
2. **Radius:** the merge gate of §4.3, tiers `unit` and `integration`, by the main session: `tests/unit tests/integration`.
3. **Already run?** The changed files ran as radius sets (developer 97 passed; reviewer 167 passed) but never the whole unit and integration set together on this code, and `test_smoke_pipeline.py` has not run on this code. This gate is that run, once.
4. **Device:** `JAX_PLATFORMS=cpu`, `XLA_PYTHON_CLIENT_PREALLOCATE=false`.
5. **Threads and time:** `LPC_THREADS=4`, `OMP/MKL/OPENBLAS_NUM_THREADS=4`, `timeout 900`.
6. **Contention:** other agents share the 4 cores (WU-0012's fix round); no GPU use; no preset of mine running.
7. **Output:** `-q --tb=short -rfE`.
8. **Command:** `LPC_GATE=merge timeout 900 .venv/bin/python -m pytest -q --tb=short -rfE tests/unit tests/integration`.

## Review

### Round 1, 2026-10-10, reviewer (claude-opus-5-5), fresh context, branch `wu/0001-seeds-provenance` at `dae50c5` against `main`

**Radius run (once, hand-derived).** These are the unit files the diff adds or touches, plus the test files that import a changed module, plus the integration file: `test_seeds`, `test_config`, `test_data`, `test___main__`, `test_provenance`, `test_report`, `test_tools_test_impact`, `tests/integration/test_cli_seeds.py`. The run used CPU, 4 threads, `LPC_CONF_*` unset and no `LPC_GATE`. Summary: `167 passed in 11.88s`. `test_smoke_pipeline.py` and the whole suite were not run; they belong to the merge gate.

**Criteria, checked one at a time.**

- **.1 met.** DEV-0 equals the literal; DEV-1 equals the value from `json.load`. `--seed 5` and `--seed-id 5` exit 64 with a message naming LPC.PC.7. A different schema is refused.
- **.2 met.** The digest is computed independently with hashlib. The matching pair is accepted. A wrong seed, a wrong salt and a missing CONF-1 entry are each refused. The fixture path is asserted to lie under `tmp_path`.
- **.3 met.** All 8 subprocess cases exit 64 with one stderr line. No out directory and no `results.json` are created.
- **.4 met, apart from R1 and R3.**
- **.5 met under DEC-0004 Q1.** I re-ran the comparison independently from the stored output:
  - the baseline sha256 matches `0da48771…4b79`;
  - removed from the baseline: `seconds` ×5;
  - removed from the new file: `seconds` ×5, `provenance` ×1, `config.seed_id` ×1, `handling` ×0 in both;
  - the canonical texts are equal (61786 characters each);
  - the only new top-level key is `provenance`;
  - `dirty` is false at `ed6dacb`, and `ed6dacb..HEAD` touches only this file.

  The Q1 reading is sound. `config.seed_id` is required by the .1 DoD and by LPC.PC.18, and `config.seed` and every number are still compared exactly. However, DEC-0004 is still `proposed`, so .5 passes only once the owner confirms it.

**Safety (LPC.PC.7).**

- **Seed literals.** The only numeric literals in the diff are synthetic seeds (`123456789012345`, `222222222222222`, `987654321987654321`, `424242424242`) and DEV-1 quoted in the plan text.
- **Environment.** `LPC_CONF_*` is read only in `seeds.confirmatory_seed`, through `choose_seed`. Every test file clears these variables. The subprocess tests strip them from the child environment. All ledgers are under `tmp_path`, and `tools.ledger.LEDGER` is monkeypatched.
- **No run without a commitment.** A confirmatory run cannot start without a matching latest CONF-1 commitment on an intact chain. There is no flag or environment override of the ledger path.
- **Abbreviations.** `allow_abbrev=False` is set, and `--conf` and `--seed-i` are refused with exit 64 before `mkdir` and before logging.
- **No seed in outputs.** The seed is nulled in both config records. No log call or report line emits `config.seed`. The smoke `run.log` and `RESULTS.md` hold only the seed id. The tests grep `results.json` and `RESULTS.md` for the fixture value.
- **DEF-0010 and presets.** DEF-0010 is untouched, and no DEV-1..4 preset was run.

**Provenance.** Every LPC.PC.18 and LPC.PC.22 field is present and typed. `commit` and `dirty` are read once, before any output, and are tested against the test's own git calls. The labels match LPC.PC.13 exactly, with DEV carrying the extra `UNPROMOTED` per Q3. Git failures and missing packages are recorded in the block and logged. Nothing is silent.

**Q5.** `tools/ledger.py` is unchanged. `check_commitment` reads the file with the same non-empty-line filter as `read_lines` and calls `verify_chain`, the same check the CLI `verify` runs. A missing file is a refusal, which is stricter than `read_lines`. The ledger's integrity check is not weakened.

**Fixture (`lpcstudy_graph.json`).** I derived the edges by hand from the import statements:

- `__main__` gains `provenance` (`from . import provenance`) and `seeds`;
- `seeds` imports `config` only; the `tools.*` imports are lazy and not lpcstudy modules;
- `provenance` imports `config` only, plus `jax`, which is external;
- the `report` and `config` imports are unchanged.

The fixture matches. `lpcstudy/*.py` has 20 stems, so the count edit 18→20 records a fact and does not loosen the test. The stems-equality assertion is unchanged, and no other existing assertion changed.

**Findings.**

- **R1 (medium; PRIME.2, tests.md "fix the code, not the test").** `tests/unit/test_provenance.py:124-153`. The RSS bracket gained slack `ncpu·max(32,2·ncpu)·pagesize` after it failed. I judge this the correction of a wrong expectation, not a loosening that hides a defect:
  - the criterion is only `peak_rss_bytes > 0`, which is still asserted exactly;
  - the code is the obvious `ru_maxrss·1024`;
  - `getrusage` uses the approximate per-CPU `mm` RSS counters, while `/proc/self/status` `VmHWM` uses an exact sum on recent kernels (7.2.9 here), so byte equality is not a kernel property.

  The stated bound is not rigorous, though. As I read the kernel, `get_mm_rss` sums three per-CPU counters (file, anon and shmem pages), so the worst-case error is about 3× the slack (about 24 MiB at 32 online CPUs). The test can therefore flake on a larger or busier process. A tolerance was also added after a failure without the applied-mathematician's confirmation or a decision record.

  *Fix.* The applied-mathematician must confirm. Preferred: replace the slack with a bracket that is independent of kernel internals and still catches the KiB/bytes unit error, for example `0.5·1024·VmHWM_before ≤ peak ≤ 2·1024·VmHWM_after`. Otherwise use 3× the slack and cite the kernel source through `researcher`. The main session records the choice in `decisions.md`.
- **R2 (low; LPC.PC.7 refusal contract "values never echoed").** `lpcstudy/__main__.py:59-60`. The refusal echoes any unrecognized token that begins with `-`. Probe: `main(["-424242424242"])` prints `unrecognized option(s) -424242424242`, and `--424242424242` does the same. A seed-like value can reach stderr this way.

  *Fix.* Echo only names that match `^--?[A-Za-z][A-Za-z0-9-]*$` and show `<value>` otherwise. Add the two probe cases to `test_refusal_is_one_line_exit_64_and_creates_nothing`.
- **R3 (low; .4 criterion wording).** `tests/unit/test_provenance.py:156-170`. The 1% check is made on `RunClock.elapsed()`, but the criterion names the recorded `wall_seconds`. `finish()` is checked only against the loose bound `[0, t1−t0]`.

  *Fix.* After the sleep, assert the 1% bound on `provenance.finish(block, clock)["wall_seconds"]`, with `block` collected on the same clock and the reference span measured around the `finish` call.
- **R4 (low; LPC.PC.21a reference provenance).** `tests/unit/fixtures/lpcstudy_graph.json:3`. `source_commit` still names `d6abaa7`, but the graph now includes `seeds` and `provenance`, which do not exist at that commit.

  *Fix.* Update `source_commit` and the description to name this unit's hand edit, for example "updated by hand in WU-0001.1/.4".

**Not findings (noted).**

- `--report-only` resolves the seed before reading the stored output. It needs no confirmatory environment, because the label comes from the stored block.
- The `--out results` default lies outside `.gitignore`, so a second run in the repository records `dirty: true`. The flag is recorded honestly, and Q6 is deferred to WU-0004.

**Owner checkpoint.** This unit touches seed and provenance code: **needs owner review before freeze** (LPC.PC.11, `.claude/rules/seeds.md`). The owner also needs to confirm DEC-0004, on which .5 depends. No verdict or statistics code and no dependency is touched.

**Verdict: approve with fixes** (R1 to R4; R1 needs the applied-mathematician's confirmation).

### Re-review, 2026-10-10, reviewer (claude-opus-5-5), fix round 1 (commit `80dbb57`)

This round covers R1 to R4 only. I read the diff `dae50c5..80dbb57` and the logs and ran no tests, as instructed. The developer's log records the radius run `97 passed in 11.43s`.

- **R1 fixed.** `tests/unit/test_provenance.py` asserts exactly what the applied-mathematician recommended (Log, "Mathematics review of the peak-RSS tolerance"):
  - `peak > 0` is kept;
  - `peak % page == 0` is exact;
  - the bracket is `1024·before − 2T ≤ peak ≤ 1024·after + 2T`, with `T = 3·online·(max(32, 2·online) − 1)·pagesize` and `online = os.sysconf("SC_NPROCESSORS_ONLN")`.

  The launcher-peak limitation is documented in the test docstring and in the `provenance.peak_rss_bytes` docstring. The provenance schema is unchanged: only a docstring changed in `provenance.py`. The choice is recorded as DEC-0006 (proposed) on `main`. My ratio-bracket suggestion was weighed there and declined with a reason (it misses factor-2 errors), which I accept.
- **R2 fixed.** `lpcstudy/__main__.py:58-64` echoes a dash token's name only if it is one of the parser's own option strings, and prints `<value>` otherwise. The part after `=` is never shown. The new parametrized test covers `-424242424242`, `--424242424242`, `--conf`, `--conf=424242` and `--seed-i`. It asserts one stderr line with the refusal prefix and that no part of the token appears in it. The order is unchanged: `choose_seed` still runs before `out_dir.mkdir` and logging, and returns 64.
- **R3 fixed.** The 1% bound now applies to `provenance.finish(block, clock)["wall_seconds"]`, with `collect` on the same clock and the reference span around the `finish` call. The 1% tolerance is unchanged.
- **R4 fixed.** In the fixture, `source_commit` is now `ed6dacb` and the description gains a dated note on the hand edit. The `graph` object is identical to `dae50c5`, which I compared as parsed JSON. Its new-module edges were verified against the imports in round 1.

**Other checks.**

- **Scope.** Only the files these fixes need were changed (`__main__.py`, `provenance.py`, the fixture, `test___main__.py`, `test_provenance.py` and this unit file). The only assertions removed are the two that were replaced (the RSS slack and the `RunClock.elapsed` check). In this unit file, the developer added lines and deleted none, so the round-1 review is untouched.
- **Safety.** The new diff contains only synthetic numeric literals, introduces no new seed or salt echo, and adds no read of `LPC_CONF_*`. The safety properties from round 1 still hold.

**Owner checkpoint.** These items still stand: **needs owner review before freeze**, owner confirmation of DEC-0004 (on which .5 depends), and owner confirmation of DEC-0006.

**Verdict: approve.**

## Audit

### Plan amendment 2026-10-10 (answers to the plan's questions), claude-sonnet-5-5 (main session), before execution (VV.3)

Q1 to Q8 are answered in `DEC-0004` (proposed, for owner confirmation; see `docs/agent/records/decisions.md` on `main`). In short: the WU-0001.5 comparison also removes `config.seed_id` and nothing else (Q1); `--seed-id` defaults to DEV-0 (Q2); development headers carry the DEV label and UNPROMOTED (Q3); the sklearn seed-size crash is `DEF-0010`, fixed in WU-0002 after an owner ruling and NOT in this unit (Q4); do not change `tools/ledger.py`, monkeypatch its ledger path in tests, and only if that is impossible add an optional path argument with its own test (Q5); dirty-tree refusal is not implemented (Q6); the main-module test is `tests/unit/test___main__.py` and `test_seeds` is added by hand when `tools/ledger.py` changes (Q7); ledger path override from Python only (Q8). No acceptance criterion changes except the Q1 form of the WU-0001.5 comparison. Do not edit `decisions.md`, `defects.md` or `queue.md` in this branch.
