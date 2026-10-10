# WU-0012: Test and preset wrappers, GPU-hour tally

| Field | Value |
| --- | --- |
| Status | in progress |
| Class | CSQ3 development |
| Agent(s) | claude-sonnet-5-5 (main session) under governance ledger entry 5 (authorizations 4, 6) |
| Estimate | WU-0012.1 S, .2 S, .3 S (ROADMAP.md §2) |

## Plan (written before execution)

Planner: claude-opus-5-5, 2026-10-10, on `wu/0012-wrappers` from `main` 70e19b7. Sources: ROADMAP.md rows WU-0012.1–.3 and their criteria; DEVELOPMENT_WORKFLOW.md §3, §4.1–4.9; LPC.AUTH.3; LPC.PC.7, .11, .22; `.claude/settings.json`; `.claude/hooks/test_gate.py`; skill `dev-run`; `tools/test_impact.py`; `lpcstudy/__main__.py`. Tooling unit: no v3 or Methods v2 content is in scope (LPC.PC.1).

**Scope.**
- *In:* `tools/run_tests.sh` (.1), `tools/run_preset.sh` (.2), `tools/gpu_hours.py` (.3); tests in `tests/unit/test_tools_wrappers.py` and `tests/integration/test_preset_wrapper.py`. The tools use only bash, coreutils (`timeout`, `nohup`, `date`, `realpath`), util-linux `flock`, `git` and the Python 3.13+ standard library. No new dependency.
- *Out:* changes to `lpcstudy/` (`--seed-id` is WU-0001.1), `tools/test_impact.py`, hooks, settings, skills and `queue.md`. The XLA CPU thread flag of §4.5 and the "observed CPU use within the cap" check are out until the flag's name for jax 0.11.2 is confirmed (Q3); an unknown `XLA_FLAGS` entry aborts XLA at startup. Peak memory (LPC.PC.22) is out because it is not in the criterion schema (Q5). `pgrep` (procps) is not used, because the lock already serializes heavy runs.
- *Shared rules:* the repository root is resolved from the script's own path, and the tools `cd` there. The interpreter is `$LPC_PYTHON`, else `<root>/.venv/bin/python` if it is executable, else `python3`; it is used only for `-m pytest` and `-m lpcstudy`. Registry and tally helpers always use `python3 -I`. `LPC_THREADS` must match `^[1-9][0-9]?$` (default 4), else exit 64. `OMP_NUM_THREADS`, `MKL_NUM_THREADS` and `OPENBLAS_NUM_THREADS` are set to `$LPC_THREADS`, and `XLA_PYTHON_CLIENT_PREALLOCATE=false` is forced, both overriding inherited values. The lock is `${LPC_GPU_LOCK:-/tmp/lpcstudy-gpu.lock}`, opened as `exec 9>>"$lock"` (never truncated). Exit codes: **64** usage or refusal, **65** weekly GPU hours, **75** lock busy, **124** timeout (coreutils), otherwise the child's code. A refusal prints exactly one line on stderr, naming the rule.

**WU-0012.1 `tools/run_tests.sh <tier> [--lf] [--tb=long] [--durations=N] [--background] <path>...`**
- The tier is one of `unit`, `integration`, `slow` or `gpu`. Every path (a node id is split at `::`) must exist and be `tests/<tier>` or lie under it. `tests`, `tests/` and `.` are refused, and so is any other flag (`-n`, `-s`, `-v`, …): 64. The wrapper is its own whole-suite guard, because the hook does not see inside it. Gates run one call per tier (`LPC_GATE=merge tools/run_tests.sh unit tests/unit`).
- Command: `timeout --kill-after=30 <T> $PY -m pytest -q --tb=short -rfE [extras] <paths>`, with T = 300, 900, 3600 or 1800 s for `unit`, `integration`, `slow` or `gpu` (§4.5). On exit 124 it prints `TIMEOUT after T s (§4.5): investigate, do not raise`.
- `JAX_PLATFORMS=cpu` is forced for the CPU tiers. For `gpu` it is `cuda,cpu`, with `flock -w ${LPC_GPU_WAIT:-30} 9 || exit 75`. `LPC_GPU_WAIT` must be an integer from 0 to 30, else 64; it can shorten the wait, never lengthen it.
- `--background` (§4.5, for `slow` and `gpu`): `nohup` re-runs the wrapper with the same arguments, minus the flag. The log goes to `runs/tests/<tier>-<UTC stamp>.log` and the exit code to `<log>.exit`. The wrapper prints `pid=… log=…` and exits 0. The default is the foreground, so `tools/test_impact.py --run` keeps its `tools/run_tests.sh <tier> <paths>` interface and gets pytest's exit code.

**WU-0012.2 `tools/run_preset.sh <preset> <seed-id> <out-dir> [--device cpu|gpu] [--systems S…] [--skip-transfer] [--skip-robustness]`** (the positional form is the one in skill `dev-run`)
1. Refusals, each 64 with one line:
   - any argument containing `confirmatory` (case-insensitive);
   - a seed matching `^[0-9]+$` ("raw integer seed; use a DEV-n id, LPC.PC.7");
   - an id not in `seeds/development_seeds.json`, or a registry whose `schema` is not `lpcstudy.seed-registry/1`;
   - a preset other than `smoke`, `pilot` or `full`;
   - any other argument;
   - an `<out-dir>` whose `realpath -m` is not under `<root>/runs/`, so that the tally sees every run;
   - an existing `<out>/<preset>/run.meta.json`, which must not be overwritten, because that would erase GPU hours.
2. **Seed pass-through.** The wrapper probes `JAX_PLATFORMS=cpu timeout 120 $PY -m lpcstudy --help`. If the help mentions `--seed-id`, it passes `--seed-id <id>`. If not, DEV-0 runs without the flag (the CLI default is 20261005, the registry's DEV-0 value), with a printed note, and any other id is refused with 64 ("needs --seed-id, WU-0001.1"). If the probe fails, the run is refused with 64. The criteria stay as written: the wrapper picks up the flag automatically once WU-0001.1 merges.
3. **Device.** The default is `cpu` for `smoke` and `gpu` for `pilot` and `full`. `JAX_PLATFORMS` is `cpu` or `cuda`.
4. **Lock.** `pilot`, `full` and any `gpu` run take `flock -n 9 || exit 75` at once ("GPU busy: do other work"). A smoke run on CPU takes no lock (§4.5).
5. **Tally.** Before every `pilot` or `full` start, and before any `gpu` start, the wrapper calls `python3 -I tools/gpu_hours.py check --hours H` while it holds the lock, so no run can start between the check and the lock. H is 12 for `gpu` and 0 for `cpu`. A child exit of 64 or 65 is propagated. Any other non-zero exit, or a missing `gpu_hours.py`, gives 65 (fail closed).
6. **Meta.** `<out>/<preset>/run.meta.json` is written atomically (temporary file, then `mv`) at the start, with `end_utc`, `wall_seconds` and `exit_code` set to `null`, and rewritten at the end. Fields:
   - schema `lpcstudy.run-meta/1`;
   - `preset`, `seed_id`;
   - `start_utc`, `end_utc` (format `YYYY-MM-DDTHH:MM:SSZ`, from one `date -u +%s` epoch each);
   - `device` (`cpu` or `gpu`);
   - `wall_seconds` (an integer, end minus start);
   - `exit_code` (an integer);
   - extras: `seed_flag`, `lpc_threads`, `command`, `pid`.
7. **Run.** `timeout --kill-after=300 12h $PY -m lpcstudy --preset P --out OUT [--seed-id ID] [pass-through]`.
   - **Smoke** runs in the foreground and the wrapper returns the CLI's exit code.
   - **Pilot and full** always start in the background: `nohup "$0" __record <meta> -- <cmd> >"<out>/<preset>/console.log" 2>&1 </dev/null &`. The wrapper prints `started pid=… console=… run_log=<out>/<preset>/run.log meta=…` and exits 0. The child inherits fd 9, so it holds the lock until it ends.
   - `__record` refuses with 64 unless `/proc/self/fd/9` resolves to the lock path. It traps TERM, INT and HUP and records `128+signal` as the exit code.

**WU-0012.3 `tools/gpu_hours.py [--root DIR]… [--now ISO-Z] {sum | check --hours H}`**
- **Roots.** The default is `<worktree>/runs` for every worktree in `git worktree list --porcelain`, because all worktrees share one tally (§3). If git fails, it is `<root>/runs`, with a printed note. The tool scans `**/run.meta.json`, without following symlinks, and deduplicates by resolved path.
- **Week.** The current ISO week in UTC, `[Monday 00:00Z, next Monday 00:00Z)`. Only runs with `device == "gpu"` count.
- **Contribution.** The integer-second overlap of `[start, end)` with the week:
  - a run that crosses a week boundary is split, and each week gets its own part;
  - a run with `end_utc` `null` or missing (running, killed or rebooted) is counted as `end = min(now, start + 12 h)`, which is the timeout bound (conservative);
  - an end before the start, or an unreadable or schema-invalid file, is counted in the report, never skipped silently (PRIME.4). `check` refuses with 65 and names the file.
- **Output.** One line: the week id, the hours, and the numbers of runs, open runs, excluded CPU runs and unreadable files.
- **`check`.** H must be in [0, 12], else 64. It refuses with 65 if `used_s + H·3600 > 216000`, so exactly 60 h passes. It reserves the full 12 h because the timeout bounds a run at 12 h, so the cap cannot be passed (LPC.AUTH.3: refer before the cap). The wrapper never passes `--now`.

**Definition of done.** All three tools exist and are executable (git mode 100755). Every check below passes once in the radius, and the result is logged. The `dev-run` skill's command form works unchanged. The owner questions are listed for the main session. Independent review is done.

**Acceptance criteria** (ROADMAP §2, verbatim, fixed):
- *WU-0012.1:* "Shell test: with the `unit` tier, the child process environment has `JAX_PLATFORMS=cpu`, `OMP_NUM_THREADS`, `MKL_NUM_THREADS` and `OPENBLAS_NUM_THREADS` equal to `LPC_THREADS` (default 4), and the pytest arguments include `-q --tb=short -rfE`; with the `gpu` tier, `XLA_PYTHON_CLIENT_PREALLOCATE=false` is set and the wrapper exits 75 within 30 s when another process holds the lock. The timeouts are those of DEVELOPMENT_WORKFLOW §4.5."
- *WU-0012.2:* "Refuses an id not in `seeds/development_seeds.json`, a raw integer, and any argument containing `confirmatory`, each with exit 64 and a one-line reason. With the lock held, exits 75 at once. Writes `run.meta.json` with `preset`, `seed_id`, `start_utc`, `end_utc`, `device`, `wall_seconds`, `exit_code`. The smoke preset through the wrapper on CPU produces the same `results.json` as a direct invocation."
- *WU-0012.3:* "On a fixture tree of `run.meta.json` files, the weekly sum matches a hand sum; a start that would exceed 60 h returns exit 65. The wrapper calls it before a `pilot` or `full` start."

**Checks.** Every test copies the tools and the registry into a synthetic root in `tmp_path`, so the real `runs/` is never written. It puts fakes first on `PATH` or in `LPC_PYTHON` and sets `LPC_GPU_LOCK=tmp_path/lock`. Fake `python` records its argv and env as JSON, answers `--help` with or without `--seed-id`, writes a minimal `results.json`, waits for a sentinel file (capped at 10 s) and exits `$FAKE_EXIT`. Fake `timeout` records its argv and executes the command after the duration. A competing lock holder takes `fcntl.flock` in the test process, which is the same lock as flock(1) on Linux. The outcomes are discrete, so equality is exact and there is no tolerance. Each unit test stays under 5 s.
- *.1:*
  - (a) Unit tier, with `JAX_PLATFORMS=cuda` and `OMP_NUM_THREADS=1` inherited and `LPC_THREADS` unset: the child sees `cpu`, `4,4,4`, and argv contains `-q --tb=short -rfE` contiguously. With `LPC_THREADS=3`: `3,3,3`.
  - (b) The gpu tier with `XLA_PYTHON_CLIENT_PREALLOCATE=true` inherited: the child sees `false`.
  - (c) The lock is held and `LPC_GPU_WAIT=1`: exit 75, elapsed under 30 s (about 1 s expected), and the fake python never runs. With the default wait and a fake `flock`: argv `-w 30 9`.
  - (d) Fake `timeout` argv per tier: duration 300, 900, 3600 or 1800. A fake exiting 124 gives exit 124 and the TIMEOUT line.
  - (e) Refusals give 64: `tests`, `.`, no path, a wrong-tier path, `-n 2`, `-s`, `LPC_THREADS=0` and `LPC_GPU_WAIT=31`.
- *.2:*
  - (f) Each refusal gives 64 with one stderr line, no meta file and no fake call: `DEV-9`, `20261005`, `CONF-1`, and `confirmatory` or `CONFIRMATORY` placed in the seed, the out-dir, a pass-through argument and a `--confirmatory` flag. An out-dir outside `runs/` and an existing meta also give 64.
  - (g) The lock is held and the preset is `pilot`: exit 75, elapsed under 3 s. The bound is about 0.3 s of process start-up with a 10× margin for 4 shared cores. The fake never runs with `--preset`.
  - (h) Background: the wrapper exits 0 while the fake child waits on the sentinel. The meta then has `end_utc` `null`, the test's `LOCK_NB` attempt fails (the child holds the lock), and the child survives `SIGHUP` (nohup). The test creates the sentinel and waits at most 5 s for the PID. The meta then has all 7 keys with their types: ISO-Z strings, `wall_seconds == end − start`, and `exit_code == FAKE_EXIT` (0 and 3). The lock is free again.
  - (i) Fake `timeout` argv contains `12h`. The child env has `XLA_PYTHON_CLIENT_PREALLOCATE=false` and `JAX_PLATFORMS=cuda` (pilot) or `cpu` (smoke).
  - (j) Seed pass-through: if the help has `--seed-id`, argv has `--seed-id DEV-1`. If not, DEV-0 runs without the flag and DEV-1 is refused with 64.
  - (k) Integration (`tests/integration/test_preset_wrapper.py`): a real smoke run on CPU with the same `$PY`, `LPC_THREADS` and env, directly and through the wrapper into fresh directories. The two `results.json` must be identical after removing the keys named `seconds` at any depth (wall-clock: top level, `systems.*`, `estimators.*`). If WU-0001.4 has merged, its provenance timestamp, wall-clock and peak-memory fields are also removed. Every other value must be equal, floats bitwise, because the code, CPU and threads are the same (LPC.PC.18). The bound is the 900 s tier timeout (about 2 × 50 s expected).
- *.3:*
  - (l) A fixture tree with two roots, nested directories, and `--now` fixed. Expected values are written by hand in the docstring as integer seconds:
    - one gpu run inside the week;
    - one gpu run crossing into the week from Sunday 20:00Z to Monday 04:00Z, counted as 4 h;
    - one open run started 5 h before now (5 h) and one started 20 h before now (capped at 12 h);
    - one CPU run of 10 h and one run in the previous week (both 0);
    - one `run.meta.json.tmp` (ignored).

    A second `--now` in the next week takes the tail of a run that crosses the end boundary. ISO edge: `--now 2027-01-02T12:00:00Z` gives `2026-W53`, starting Monday 2026-12-28.
  - (m) `check`: exactly 60 h gives 0; 60 h + 1 s gives 65; 49 h with `--hours 12` gives 65; a corrupt file gives 65 and is named.
  - (n) The wrapper calls it: a fake `gpu_hours.py` in the copy records its argv and exits 65. Then `pilot` (gpu) gives 65, the CLI never runs, `--hours 12` is passed and `--now` is not, and the lock is free afterwards. For `pilot --device cpu` it is called with `--hours 0`; for `smoke` on CPU it is not called.

**Affected checks** (§4.2, by hand; `python3 tools/test_impact.py --run` gives the same set):
- Change set: the three `tools/` files (each maps to `tests/unit/test_tools_<t>.py`, which is absent, so there is a warning and no test), the two new test files (each selects only itself), and the unit file (no tests).
- Radius: `unit` `tests/unit/test_tools_wrappers.py`; `integration` `tests/integration/test_preset_wrapper.py`, which carries criterion (k).
- `lpcstudy/` is untouched, so `test_smoke_pipeline.py` is not in the radius.
- Invoke as `tools/run_tests.sh unit tests/unit/test_tools_wrappers.py`. The hook only inspects commands with a `pytest` token, so do not use `bash -c "…pytest…"`, and never type the confirmatory flag in a shell command; it appears only inside the test file.

**Owner checkpoints (LPC.PC.11).** The seed check and the `run.meta.json` provenance belong to the seed and provenance machinery, so the owner reviews them before the freeze. There is no verdict or statistics code and no dependency change.

**Order and split.** One branch, with one commit per sub-task: .1 → .2 → .3. In .2 the tally call fails closed (65) until .3 lands, and criterion (n) is tested in .3. Each part is a coherent change, so no further split is needed.

**Risks.**
- Deleting a `runs/` directory or a worktree within the week under-counts GPU hours (Q2).
- `LPC_PYTHON` can point anywhere. It selects the interpreter only, never the seed, the lock or the tally.
- The system `python3` is 3.14 and the venv is 3.13. The tools use only the standard library, so both work.
- If WU-0001.1 merges with a different flag name, the probe sees no `--seed-id` and the wrapper fails closed for DEV-1…4 with 64.

**Questions for the owner.**
- Q1. Criterion (k): is "the same `results.json`" read as identical except for wall-clock keys (`seconds` and the WU-0001.4 timing fields)? Bitwise is impossible for those keys.
- Q2. Is "per calendar week" (LPC.AUTH.3) the ISO week in UTC? Should a shared append-only tally outside `runs/` back up the meta files?
- Q3. For the researcher: the jax 0.11.2 or XLA CPU flag that caps intra-op threads (§4.5). Until it is known, the cap is not set.
- Q4. `tests/unit/test_tools_wrappers.py` does not match §4.2's `test_tools_<t>.py`. Later changes to a single wrapper will select no test. Proposed decision: split the file into `test_tools_run_tests.py`, `test_tools_run_preset.py` and `test_tools_gpu_hours.py`, or add a mapping line to §4.2 and `test_impact.py`.
- Q5. Should `run.meta.json` record peak RSS (LPC.PC.22) as an extra field?
- Q6. Should CPU `pilot` and `full` runs (WU-0002.12) take the GPU lock, as planned ("one run at a time")?

## Log

**2026-10-10, developer claude-sonnet-5-5: WU-0012.1 written** (`tools/run_tests.sh`, mode 755; `tests/unit/test_tools_run_tests.py`; helper `tests/unit/wrapper_helpers.py`, a new support module with the fake-root builder shared by the three tool test files, because the plan's Q4 split needs one builder; it is not on the plan's file list and is reported to the main session).

§4.9 checklist before the .1 run:
1. Change set: `?? tools/run_tests.sh`, `?? tests/unit/test_tools_run_tests.py`, `?? tests/unit/wrapper_helpers.py` (`git diff --name-only main...HEAD`: only this unit file).
2. Radius (`python3 tools/test_impact.py --explain`): `unit: tests/unit/test_tools_run_tests.py` (tool maps `tools/run_tests.sh` to its test file; the helper selects the test that names it). Smaller than the whole suite; no gate.
3. Already run: no (first run of this set on this code).
4. Device: `JAX_PLATFORMS=cpu` (settings default and forced by the wrapper); no GPU, and the tests use a fake lock in `tmp_path`, never `/tmp/lpcstudy-gpu.lock`.
5. Threads and time: `LPC_THREADS=4`; unit timeout 300 s; each test expected well under 5 s.
6. Contention: no pilot/full/slow/gpu run started by this unit; other agents share the 4 cores.
7. Output: `-q --tb=short -rfE` (added by the wrapper); only the summary line and failures recorded.
8. Command: `tools/run_tests.sh unit tests/unit/test_tools_run_tests.py`.

Result of run 1: `40 passed in 1.67s` (exit 0). After the run, a manual probe showed that an unopenable lock path printed two stderr lines (bash's own message and the refusal). Fixed with `{ exec 9>>"$lock"; } 2>/dev/null`, and `test_unopenable_lock_file_is_refused` added. Code changed, so the radius runs once more (same checklist answers, except 3: the code differs from run 1; command identical).

Result of run 2: `41 passed in 1.66s` (exit 0). Self-check: no `clip|nan_to_num|isfinite|where(|try:|except` and no randomness in the diff; no tolerance exists (discrete outcomes). Criterion (a) to (e) each have a test. Not set (DEC-0005 Q3): the XLA thread flag. Commit: WU-0012.1 (see git log).

## Review

- **Reviewer:** <actor, not the author>
- **Findings and resolution:**

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:

## Referral

<only if halted; use the form in agent-instructions.md, LPC.AI.13>

### Plan amendment 2026-10-10 (answers to the plan's questions), claude-sonnet-5-5 (main session), before execution (VV.3)

Q1 to Q6 are answered in `DEC-0005` (proposed, for owner confirmation; see `docs/agent/records/decisions.md` on `main`). In short: the smoke comparison excludes the wall-clock `seconds` fields (Q1); calendar week is the ISO week in UTC and no shared tally is added (Q2); the XLA thread-cap flag is not set (Q3); the wrapper tests are split into `tests/unit/test_tools_run_tests.py`, `test_tools_run_preset.py` and `test_tools_gpu_hours.py` instead of the single `test_tools_wrappers.py` (Q4; the radius in the criteria is read accordingly); `run.meta.json` has the fixed field list and no peak memory (Q5); CPU pilot and full runs take the same lock (Q6). No acceptance criterion changes. Do not edit `decisions.md`, `defects.md` or `queue.md` in this branch.
