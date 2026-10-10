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

## Review

## Audit

### Plan amendment 2026-10-10 (answers to the plan's questions), claude-sonnet-5-5 (main session), before execution (VV.3)

Q1 to Q8 are answered in `DEC-0004` (proposed, for owner confirmation; see `docs/agent/records/decisions.md` on `main`). In short: the WU-0001.5 comparison also removes `config.seed_id` and nothing else (Q1); `--seed-id` defaults to DEV-0 (Q2); development headers carry the DEV label and UNPROMOTED (Q3); the sklearn seed-size crash is `DEF-0010`, fixed in WU-0002 after an owner ruling and NOT in this unit (Q4); do not change `tools/ledger.py`, monkeypatch its ledger path in tests, and only if that is impossible add an optional path argument with its own test (Q5); dirty-tree refusal is not implemented (Q6); the main-module test is `tests/unit/test___main__.py` and `test_seeds` is added by hand when `tools/ledger.py` changes (Q7); ledger path override from Python only (Q8). No acceptance criterion changes except the Q1 form of the WU-0001.5 comparison. Do not edit `decisions.md`, `defects.md` or `queue.md` in this branch.
