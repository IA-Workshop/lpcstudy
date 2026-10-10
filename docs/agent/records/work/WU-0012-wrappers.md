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

**2026-10-10, developer claude-sonnet-5-5: WU-0012.2 written** (`tools/run_preset.sh`, mode 755; `tests/unit/test_tools_run_preset.py`; `tests/integration/test_preset_wrapper.py`; `tests/unit/wrapper_helpers.py` extended with a recording fake `gpu_hours.py`, `real_tally=True` keeps the real one). Design choices within the plan: lock first (so a busy lock exits 75 at once, before the 2 s+ import-heavy `--help` probe), then the tally, then the probe; out-dir and test paths are taken from the caller's directory; the seed must also match `^DEV-[0-9]+$` before the registry lookup; a failure of the CLI probe is a refusal (64). The `note` for DEV-0 without `--seed-id` goes to stdout.

§4.9 checklist before the .2 unit run:
1. Change set: `M tests/unit/wrapper_helpers.py`, `?? tools/run_preset.sh`, `?? tests/unit/test_tools_run_preset.py`, `?? tests/integration/test_preset_wrapper.py`; vs `main`: also the .1 commit (`tools/run_tests.sh`, its test and the helper).
2. Radius (`python3 tools/test_impact.py`): unit `tests/unit/test_tools_run_preset.py tests/unit/test_tools_run_tests.py` (the helper changed and both name it); integration `tests/integration/test_preset_wrapper.py`. Smaller than the whole suite; no gate. `lpcstudy/` untouched.
3. Already run: the run_tests file ran on the .1 code (41 passed) but the helper has changed since; the preset file and the integration file have never run.
4. Device: `JAX_PLATFORMS=cpu`; the unit tests use a fake lock under `tmp_path`, never `/tmp/lpcstudy-gpu.lock`; no GPU.
5. Threads and time: `LPC_THREADS=4`; unit timeout 300 s, integration timeout 900 s (two smoke runs, about 2 x 50 s expected, shared cores).
6. Contention: no pilot/full/slow/gpu run by this unit; the integration run is the one smoke-preset CPU run permitted by the criterion (k) (wrapper-vs-direct comparison), done once, in this sub-task only.
7. Output: `-q --tb=short -rfE` (added by the wrapper); only the summary lines and failures recorded.
8. Commands: `tools/run_tests.sh unit tests/unit/test_tools_run_preset.py tests/unit/test_tools_run_tests.py`, then (background not needed) `tools/run_tests.sh integration tests/integration/test_preset_wrapper.py`.

Results of the .2 runs: unit `93 passed in 10.63s` (exit 0; the 41 tests of the run_tests file and 52 of the preset file); integration `2 passed in 69.26s` (exit 0; the real smoke preset on CPU through the wrapper and directly, identical `results.json` after removing the `seconds` keys, per DEC-0005 Q1; `runs/` left empty, the test removes its directories). No pilot or full preset and no GPU lock were used; no leftover process (`pgrep` clean). Self-check: the diff has no `clip|nan_to_num|isfinite|where(|except` and no randomness; the one `try:` is the test cleanup `finally` and the `try/except` in the embedded registry helper reports the failure as the refusal reason (never skips). No tolerance exists. Not yet covered here, by design: criterion (n) (in .3) and the real tally (.3). Commit: WU-0012.2 (see git log).

**2026-10-10, developer claude-sonnet-5-5: WU-0012.3 written** (`tools/gpu_hours.py`, mode 755; `tests/unit/test_tools_gpu_hours.py`, which also carries criterion (n), the wrapper-calls-the-tally tests). Definitions fixed in the tool and its docstring: `runs` = GPU runs overlapping the current week, `open` = those without an end, `cpu_excluded` = non-GPU runs overlapping the week, `unreadable` = files that are invalid in any way (counted, named on stderr, refused by `check`); an open run that starts after `now` counts as unreadable; a symlinked `run.meta.json` is not followed and counts as unreadable; stdout is one `key=value` line, notes and names go to stderr; H is parsed as a `Decimal`, so the 60 h boundary is exact.

§4.9 checklist before the .3 run:
1. Change set (working tree vs HEAD): `?? tools/gpu_hours.py`, `?? tests/unit/test_tools_gpu_hours.py`. The log edit is docs only.
2. Radius: `tests/unit/test_tools_gpu_hours.py` (unit; `tools/gpu_hours.py` maps to it). `python3 tools/test_impact.py` over `main...HEAD` also lists the .1/.2 sets, which are not selected by this change: `run_preset.sh`, `run_tests.sh` and `wrapper_helpers.py` are unchanged since their runs, and `gpu_hours.py` is replaced by the recording fake in every `FakeRoot` test except the ones in the new file. The integration test is not affected (the smoke run calls no tally). Smaller than the whole suite; no gate.
3. Already run: no (the new file never ran); the .1/.2 sets ran on this exact code and are not rerun.
4. Device: `JAX_PLATFORMS=cpu`; fake lock under `tmp_path`; no GPU.
5. Threads and time: `LPC_THREADS=4`; unit timeout 300 s; each test expected under 5 s (git worktree test about 1 s).
6. Contention: nothing heavy started by this unit.
7. Output: `-q --tb=short -rfE`; summary and failures only.
8. Command: `tools/run_tests.sh unit tests/unit/test_tools_gpu_hours.py`.

Result of the .3 run: `46 passed in 8.86s` (exit 0). Self-check: `try`/`except` sites in `tools/gpu_hours.py` are (1) the reader of one meta file, which turns every failure into a `BadMeta` that is counted, named on stderr and refused by `check`, (2) the git call, which prints a note and falls back, (3) `Decimal` parsing of H, which exits 64; nothing is clipped, replaced or skipped without a count; no randomness; no tolerance (exact integer seconds). Criterion mapping: (l) `test_weekly_sum_matches_a_hand_sum`, `test_run_crossing_the_end_boundary_is_split`, `test_iso_week_53_and_year_boundary`; (m) `test_check_boundary_at_exactly_60_hours`, `test_check_rejects_hours_outside_0_to_12`, `test_unusable_file_is_counted_named_and_refuses_check`; (n) `test_wrapper_calls_the_tally_before_pilot_and_stops_on_65`, `test_wrapper_tally_hours_per_device_and_preset`, plus the real-tool wrapper tests. Commit: WU-0012.3 (see git log).

**Open points for the main session / reviewer (developer, 2026-10-10):**
- `tests/unit/wrapper_helpers.py` is a new support module not on the plan's file list (shared fake-root builder for the three tool test files).
- The tally cannot be tested end to end near the cap through the wrapper with the real clock (the wrapper never passes `--now`); (n) uses a recording fake as the plan says, and the real tool is exercised through the wrapper only on an empty tree and with a corrupt file (both date-independent).
- `run_tests.sh --background` is accepted for every tier, not only slow and gpu; `LPC_GPU_LOCK` is expected to be an absolute path (settings set one).
- The XLA CPU thread flag is not set (DEC-0005 Q3); the "observed CPU use within the cap" check of 4.5 is therefore not covered.
- `timeout` exit 137 (kill after 30 s) is returned as is, without the TIMEOUT line; only 124 prints it.
- The integration test (k) wrote under the worktree `runs/` (the wrapper accepts only `runs/`) and removed its directories afterwards.

**2026-10-10, developer claude-sonnet-5-5: fix round 1 (R1 to R4) written, not yet run.**
- R1: the `__record` mode and the `nohup bash "$self" __record` re-entry are removed from `tools/run_preset.sh`. Pilot and full now start the recorder as a background subshell of the checked front end (`( ignore_hup=1; trap '' HUP; run_recorded ... ) >console.log 2>&1 </dev/null & disown`): it inherits fd 9 (the lock held by this same process), the validated argv and the written meta; the meta `pid` is `$BASHPID` (equal to the printed `$!`). New tests: `test_no_hidden_mode_runs_a_command` (7 mode names x 3 argument shapes, with the lock file on fd 9 as in the reviewer's probe; marker never created, no fake called, exit 64, one stderr line), `test_script_has_no_second_entry_point`, `test_background_run_has_the_checks_of_the_front_end`; the old `test_record_refuses_without_the_lock_on_fd_9` is replaced. The background, lock-inheritance, SIGHUP and SIGTERM tests are kept unchanged.
- R1 audit of the whole script for any argument or environment variable that selects a hidden path. Arguments: after the case-insensitive 'confirmatory' scan of every argument, the only grammar is `<smoke|pilot|full> <DEV-n in the registry> <out-dir under runs/>` plus `--device cpu|gpu`, `--systems <[A-Za-z0-9_]+>...`, `--skip-transfer`, `--skip-robustness`; every other word, including `__record` and any option, ends in `refuse` (64) before any lock, tally or command; nothing is `eval`ed, and the command is an array built only from validated values (`--out` is the absolute resolved path). Environment variables read: `LPC_THREADS` (regex 1..99), `LPC_GPU_LOCK` (the lock file only; a different file means a different lock, which is the documented override of 4.5, and does not skip the tally, which scans `runs/` of every worktree), `LPC_PYTHON` (the interpreter that runs `-m lpcstudy --preset ... --out ...` after all checks; it cannot skip a check, and an agent that can set it can already run any command from the shell), `PATH` (the usual: `timeout`, `flock`, `python3`, `realpath`, `date`, `grep`), and the internal shell variable `ignore_hup`, which only decides whether the foreground handler or the ignore is installed for SIGHUP (set to 1 from outside it just ignores HUP in a smoke run). No other `$VAR` or `${VAR:-}` read is from the environment (`grep` of the script); variables used before being set are initialised in the script (`device`, `systems`, `passthrough`); `BASH_ENV`/exported shell functions are the same class as `PATH` and are not defended against.
- R2: `find_meta_files` passes `onerror` to `os.walk`; each directory error is counted as unreadable (with the path) so `sum` reports it and `check` exits 65. Test `test_unreadable_directory_is_counted_named_and_refuses_check` (chmod 000, restored in `finally`; skipped as root with the reason).
- R3: `run_tests.sh` refuses (64, one line) when `PYTEST_ADDOPTS` or `PYTEST_PLUGINS` is non-empty; three refusal cases added to test (e); `FakeRoot.environment` now also strips `PYTEST_*`.
- R4: `run_tests.sh` prints the TIMEOUT line on exit 124 and on 137 (with elapsed seconds, the tier's limit and the 30 s grace); I did not require elapsed >= limit for 137, because the fake `timeout` cannot wait 300 s and an external SIGKILL gives 137 too, so the line says both. Test `test_timeout_kill_exit_137_is_reported`.
- R5: for the owner, no code change in this unit: the weekly tally sees only `run_preset.sh` runs; `gpu`-tier test runs write no `run.meta.json` and call no `check`; the legacy `flock -n ... python -m lpcstudy --preset` allow rules in `.claude/settings.json` and the `flock` exemption in `.claude/hooks/test_gate.py` still start pilot/full without a meta. To be recorded by the main session as a decision or an accepted gap.

§4.9 checklist before the fix-round run:
1. Change set: `M tools/run_preset.sh`, `M tools/run_tests.sh`, `M tools/gpu_hours.py`, `M tests/unit/wrapper_helpers.py`, `M tests/unit/test_tools_run_preset.py`, `M tests/unit/test_tools_run_tests.py`, `M tests/unit/test_tools_gpu_hours.py`, and the unit file (the Review section is the reviewer's and is committed with the fix, untouched).
2. Radius (`python3 tools/test_impact.py`): unit `test_tools_gpu_hours.py test_tools_run_preset.py test_tools_run_tests.py` (each tool maps to its file; the helper is named by all three); integration `tests/integration/test_preset_wrapper.py`, selected because `run_preset.sh` changed and the real smoke path goes through its run_recorded path. Smaller than the whole suite; no gate.
3. Already run: the code differs from the earlier runs; this exact code has not run.
4. Device: `JAX_PLATFORMS=cpu`; fake locks under `tmp_path`; the real `/tmp/lpcstudy-gpu.lock` and the GPU are not used.
5. Threads and time: `LPC_THREADS=4`; unit timeout 300 s, integration 900 s.
6. Contention: no pilot/full/slow/gpu run; the integration test is the one CPU smoke comparison of criterion (k).
7. Output: `-q --tb=short -rfE`; summary lines and failures only.
8. Commands: `tools/run_tests.sh unit tests/unit/test_tools_gpu_hours.py tests/unit/test_tools_run_preset.py tests/unit/test_tools_run_tests.py`, then `tools/run_tests.sh integration tests/integration/test_preset_wrapper.py`.

Results of the fix round: unit `152 passed in 20.45s` (exit 0; 139 earlier + 13 net new: hidden modes x7, structure x1, front-end checks x1, unreadable directory x1, PYTEST_* refusals x3, exit 137 x1, minus the replaced `__record` test); integration `2 passed in 119.11s` (exit 0; shared cores, the smoke results.json through the wrapper still equals the direct run after removing `seconds`; `runs/` empty afterwards). Self-check: the `try`/`except` sites are unchanged except the new `onerror` handler (counts and names the directory); no clipping, no randomness, no tolerance changed. No pilot/full/GPU job and no real lock. Commit: "WU-0012 fix R1-R4" (see git log). The Review section is the reviewer's and is untouched; R1 to R4 resolution: fixed in that commit; R5 recorded above for the owner.

### Resolution of findings, 2026-10-10, claude-sonnet-5-5 (main session)

- **R1 (high), R2, R3, R4: fixed in 6330c78** (re-review: all fixed, approve; the reviewer read the whole script and probed it in a scratch root).
- **R5 (for the owner, no code change here):** `.claude/settings.json` and the hook still allow the old `flock ... python -m lpcstudy --preset` command form, and GPU-tier test runs are not counted in the weekly 60 GPU-hours. Both are `.claude/` edits.
- **Residual risk the reviewer noted for the owner's review before the freeze:** someone who controls the environment can still get around the wrapper (a fake `flock` or `python3` on PATH, `BASH_ENV`, exported functions, `LPC_GPU_LOCK`, `LPC_PYTHON`). The plan allows these and the tests rely on them.
- **Owner review needed before the freeze** (the seed check, `run.meta.json`, and the 60 h enforcement in `gpu_hours.py`). `DEC-0005` is **proposed**.
- **Merge gate not yet run.** It runs once, on the tree that includes the merged WU-0001 (so the whole unit and integration set runs on what will be on `main`), after the owner authorizes the merges.

### Merge gate, 2026-10-10, claude-sonnet-5-5 (main session), checklist before the run (§4.9, §4.3)

Merges to `main` authorized by the owner (this session). `main` (with WU-0001, WU-0010, WU-0011, WU-0013, WU-0014) merged into the branch so the gate runs on what will be merged.

1. **Change set:** `git diff --name-only main...HEAD`: `tools/run_tests.sh`, `tools/run_preset.sh`, `tools/gpu_hours.py`, `tests/unit/test_tools_run_tests.py`, `test_tools_run_preset.py`, `test_tools_gpu_hours.py`, `tests/unit/wrapper_helpers.py`, `tests/integration/test_preset_wrapper.py`, this unit file. `git status --porcelain` is empty after the commit that carries this entry.
2. **Radius:** the merge gate of §4.3, tiers `unit` and `integration`, by the main session: `tests/unit tests/integration`.
3. **Already run?** The wrapper test files ran as radius sets (developer 152 and 2 passed; reviewer 139 passed), but never together with the rest of the unit and integration set on this merged tree. This gate is that run, once.
4. **Device:** `JAX_PLATFORMS=cpu`, `XLA_PYTHON_CLIENT_PREALLOCATE=false`.
5. **Threads and time:** `LPC_THREADS=4`, `OMP/MKL/OPENBLAS_NUM_THREADS=4`, `timeout 900`.
6. **Contention:** no other agent running; no preset running; no GPU use; the real lock is never taken by the tests.
7. **Output:** `-q --tb=short -rfE`.
8. **Command:** `LPC_GATE=merge timeout 900 .venv/bin/python -m pytest -q --tb=short -rfE tests/unit tests/integration`.

**2026-10-10, developer claude-sonnet-5-5: merge-gate fixes F1 and F2 written, not yet run.** The merge gate (main merged into this branch) had `2 failed, 359 passed`; both failures are interactions with units on main.
- F1: `tests/unit/test_tools_test_impact.py::test_commands_for_a_tier_directory_are_allowed` is a WU-0011 test on main and this edits it. Cause: it built the expected direct `python -m pytest` argv with the real repo root, but `tools/test_impact.py` uses `tools/run_tests.sh` as soon as that file exists (WU-0011 plan Q6), and this branch creates it. The test was environment-dependent, not wrong in purpose. Fix: the root is an empty `tmp_path` (asserted to have no wrapper), the exact argv equality is unchanged; no assertion is weakened. The wrapper form for a tier directory was not covered (the existing fake-wrapper test uses file paths), so `test_commands_for_a_tier_directory_use_the_wrapper_when_it_exists` is added, exact equality `[<root>/tools/run_tests.sh, "unit", "tests/unit"]`.
- F2: `tests/integration/test_preset_wrapper.py`. WU-0001.4 added the top-level `provenance` block to `results.json` (argv, start/end, wall seconds, peak memory), which differs between a direct and a wrapped run by construction (DEC-0005 Q1 anticipated it). Same reading as WU-0001.5 (which removes `provenance`, `seconds`): the canonical JSON of `results.json` without `seconds` and without `provenance` must be bitwise equal; and, separately, the two provenance blocks must have the same keys, equal values for every field of `lpcstudy/provenance.py` except `RUN_SPECIFIC = {argv, start_utc, end_utc, wall_seconds, peak_rss_bytes, device_peak_bytes}`, and equal argv once the `--out` value is masked (and different argv, since the out-dirs differ). Nothing dropped or loosened beyond that.

§4.9 checklist before the gate-fix run:
1. Change set: `M tests/unit/test_tools_test_impact.py`, `M tests/integration/test_preset_wrapper.py` (and this log).
2. Radius, as set by the main session: F1 by node ids (`test_commands_for_a_tier_directory_are_allowed`, `test_commands_for_a_tier_directory_use_the_wrapper_when_it_exists`); F2 `tests/integration/test_preset_wrapper.py`. Nothing else is run; the main session reruns the gate.
3. Already run: not on this code (the gate run was on the unfixed tests).
4. Device: `JAX_PLATFORMS=cpu`; no GPU, no real lock.
5. Threads and time: `LPC_THREADS=4`; unit timeout 300 s, integration 900 s (two smoke runs, 70 to 120 s on shared cores).
6. Contention: no pilot/full/slow/gpu running.
7. Output: `-q --tb=short -rfE`.
8. Commands: `tools/run_tests.sh unit tests/unit/test_tools_test_impact.py::test_commands_for_a_tier_directory_are_allowed tests/unit/test_tools_test_impact.py::test_commands_for_a_tier_directory_use_the_wrapper_when_it_exists`, then `tools/run_tests.sh integration tests/integration/test_preset_wrapper.py`.

Results of the gate-fix run: F1 `2 passed in 0.21s` (exit 0); F2 `2 passed in 68.12s` (exit 0; the real smoke preset through the wrapper equals the direct run bitwise after removing `seconds` and `provenance`, and the provenance blocks agree on every field except `argv`, `start_utc`, `end_utc`, `wall_seconds`, `peak_rss_bytes`, `device_peak_bytes`; `runs/` empty afterwards). No other test was run (the main session reruns the gate). No tolerance was loosened and no assertion removed. Commit: "WU-0012 fix gate F1-F2" (see git log).

## Review

- **Reviewer:** `reviewer`, claude-opus-5-5, fresh context, 2026-10-10. Reviewed diff `main...HEAD` (557e074, dbca55e, c831aa6 on plan 1639d96), against the plan, DEC-0005, DEVELOPMENT_WORKFLOW §2.3/§4.5/§4.6/§4.9, settings.json, test_gate.py, skill dev-run and `tools/test_impact.py`.
  - §4.9 checklist before the run: (1) change set = the 9 files of the diff, working tree clean; (2) radius by hand (§4.2: each `tools/<t>` maps to `tests/unit/test_tools_<t>.py`; the helper is named by all three): the three unit files, the integration file excluded by the caller's instruction (the merge gate runs it); (3) not yet run by the reviewer; (4) `JAX_PLATFORMS=cpu`, fake locks under `tmp_path`; (5) `LPC_THREADS=4`, unit timeout 300 s; (6) no preset running (`pgrep` clean); (7) `-q --tb=short -rfE` from the wrapper; (8) `tools/run_tests.sh unit tests/unit/test_tools_run_tests.py tests/unit/test_tools_run_preset.py tests/unit/test_tools_gpu_hours.py`.
  - Result, run once: **`139 passed in 15.64s`** (exit 0; 41 + 52 + 46, matching the developer's three runs).
  - Checked and correct: criteria .1–.3 each have a test with a literal, independent expected value and no tolerance; the hand sums of (l) re-derived (9000 + 14400 + 18000 + 43200 = 84600 s = 23.5 h; W53: 10800 + 3600 = 14400 s; calendar facts checked: 2026-10-12 and 2026-12-28 are ISO Mondays of W42 and W53, 2027-01-02 is 2026-W53); the cap boundary (`used + H·3600 > 216000`) is exact (Decimal), 60 h passes, 60 h + 1 s and 49 h + 12 h refuse; open runs count `min(now, start + 12 h)`; a corrupt file makes `check` exit 65 and is named. The front-end refusals read correctly: the case-insensitive substring test on every argument (`${arg,,}`) covers `--confirmatory=1`, any case and any position; abbreviations such as `--conf` are refused as unexpected arguments (64), because only `--device`, `--systems <[A-Za-z0-9_]+>`, `--skip-transfer` and `--skip-robustness` reach the CLI and `--out` is always an absolute path. Lock: `flock -n` before the tally and the probe (75 at once), `flock -w 30` for the gpu tier, the background child inherits fd 9, no loop waits on the lock, and CPU pilot/full take the lock (DEC-0005 Q6). `tools/test_impact.py --run` builds `[tools/run_tests.sh, tier, *paths]` with `cwd=root`, which the wrapper accepts (tier directories included); no command text contains a `pytest` token. Modes 100755; no dependency, `lpcstudy/`, `.claude/` or `requirements.txt` change; `runs/` is git-ignored and nothing under it is committed; commit messages name the sub-unit and carry `Agent: claude-sonnet-5-5`.
  - Developer's additions (scope, item 4): `tests/unit/wrapper_helpers.py` is harmless and follows from the Q4 split. The `^DEV-[0-9]+$` check and the 64 on a failed CLI probe tighten the plan; the failed-probe refusal is already in the plan. `--background` on every tier is harmless, because the child is the same validated wrapper and `test_impact.py` never passes it. The integration test writing under the worktree's `runs/` (uuid directory, removed in `finally`) is harmless: it is required by the out-dir rule and it writes only a CPU smoke meta. None of these weakens a criterion. The exit 137 without the TIMEOUT line is R4.
- **Findings and resolution:**
  - **R1 (high; safety, LPC.PC.7, LPC.AUTH.3, PRIME.4): the internal `__record` mode runs any command, with no lock held and no seed, registry, preset or tally check.** Location: `tools/run_preset.sh:131-141`, and `:113` (`run_recorded` only warns when the meta is not a run-meta file). The only guard is that `/proc/self/fd/9` *resolves to* the lock path. It does not check that the lock is held, and it never validates the command. Probe in a scratch root with a scratch lock (`LPC_GPU_LOCK=<scratch>/lock`): `run_preset.sh __record <scratch>/plain.txt -- sh -c '…' 9>><scratch>/lock` ran the arbitrary command and exited 0, printing only two WARNING lines; the lock was free during and after the run. `.claude/settings.json` auto-allows `Bash(tools/run_preset.sh *)`, and `test_gate.py` lets any command containing `run_preset.sh` through its pilot/full check. So this entry point can start a pilot or full run without a permission prompt and outside every check: on a raw or unregistered seed once WU-0001.1 adds `--seed-id`, without the lock (breaking "one run at a time"), without the tally, and without a valid `run.meta.json` (so the hours are not counted). Once the CLI gains its owner-only flag, an argparse abbreviation of it would also pass, because `allow_abbrev` is on by default and neither the substring check nor the hook regex matches a prefix. This breaks the requirement that the wrapper "can never start a confirmatory run" and the dev-seed-only rule. **Fix:** remove the externally callable mode. Background the recorder as a subshell of the validated front end (for example `( trap '' HUP; run_recorded "$meta" "${command[@]}" ) >"$console" 2>&1 </dev/null & disown`), so it inherits fd 9 and the validated argv. If `__record` is kept, it must refuse with 64 unless all of these hold: the meta is an open `lpcstudy.run-meta/1` file whose `command` equals `shlex.join` of the argv; the argv re-parses under the front end's grammar (pilot/full, `--out` under `runs/`, a registered DEV id); and `meta_call pid` succeeds (refuse, do not warn). Add tests: fd 9 open on an unlocked lock file → refused; non-meta file → refused; command differing from `meta.command` → refused; the CLI is never called in any of these cases.
  - **R2 (medium; PRIME.4, fail-closed tally): an unreadable directory under `runs/` is skipped silently, so GPU hours are under-counted.** Location: `tools/gpu_hours.py:168`. `os.walk(root, followlinks=False)` has no `onerror`, and `os.walk` drops directory errors by default. Probe (scratch tree, two 10 h GPU runs, `--now 2026-10-14T00:00:00Z`, `check --hours 12`): 72000 s, exit 0. After `chmod 000` on the directory of one run: `gpu_seconds=36000 … unreadable=0`, exit 0. The hidden 10 h vanished with no count and no name, which contradicts the tool's own contract ("never skipped silently", `check` fails closed). **Fix:** pass `onerror=` to `os.walk` and record each `OSError` (with its path) in `unreadable`, so `sum` reports it and `check` exits 65. Add a test with a `chmod 000` subdirectory (skip it if run as root, with the reason stated).
  - **R3 (low; §4.5/§4.6, the wrapper as its own guard): `PYTEST_ADDOPTS` passes through `run_tests.sh` unchecked.** Location: `tools/run_tests.sh:105-119`. The wrapper refuses `-n`, `-s` and `-v` on its command line, but pytest also reads `PYTEST_ADDOPTS` (and `PYTEST_PLUGINS`) from the inherited environment. The hook never sees either, because the command text has no `pytest` token. **Fix:** refuse with 64 and one line when `PYTEST_ADDOPTS` or `PYTEST_PLUGINS` is non-empty (or `unset` them and say so). Add one refusal case to the parametrized test (e).
  - **R4 (low; §4.5 "a timeout is a failure to investigate", PRIME.4): a timeout that escalates to SIGKILL is not reported as a timeout.** Location: `tools/run_tests.sh:121-123`. With `--kill-after=30`, coreutils `timeout` exits 137, not 124, when pytest ignores TERM, which is exactly the hung case. The wrapper returns 137 with no TIMEOUT line, so the record shows an unexplained 137. **Fix:** also print the TIMEOUT line (or "TIMEOUT after T s, killed after 30 s grace") on 137 when the elapsed time is ≥ T. Add a fake-`timeout` case exiting 137.
  - **R5 (low; LPC.AUTH.3 coverage; record, no code change required in this unit): the weekly tally sees only `run_preset.sh` runs.** Location: `tools/run_tests.sh:107-114`, `.claude/settings.json` (the legacy `flock -n … python -m lpcstudy --preset` allow rules) and `test_gate.py` (`"flock" in command` passes). LPC.AUTH.3 caps all GPU-hours, but a `gpu`-tier test run (up to 30 min under the lock) writes no `run.meta.json` and calls no `check`, and the legacy flock form still auto-runs pilot/full without any meta. Both are outside the plan, and `.claude/` is an owner edit. **Fix:** the main session records it for the owner, either as a decision (count gpu-tier runs by writing a `device: gpu` meta under `runs/tests/`, and retire the legacy allow rule and the hook's `flock` exemption once this unit merges) or as an accepted gap. Do not widen this unit to do it.
  - **Owner checkpoint (LPC.PC.11):** mark the unit **needs owner review before freeze**. It covers the seed check (registry and DEV-n refusals in `run_preset.sh`), the `run.meta.json` provenance, and the LPC.AUTH.3 enforcement in `gpu_hours.py`. There is no verdict or statistics code and no dependency change.
  - **Verdict: changes required** (R1 must be fixed, R2 should be fixed; R3 and R4 are small; R5 is routed to the owner). Findings: 5.

### Re-review 2026-10-10 (fix round 1), `reviewer`, claude-opus-5-5, fresh context

Scope: R1 to R4 only, on commit 6330c78 (`git show 6330c78`). Tests were not rerun, on the main session's instruction. The developer's log records `152 passed in 20.45s` (unit) and `2 passed in 119.11s` (integration), one run each on the changed code.

- **R1: fixed.**
  - What changed: `__record` and the `nohup bash "$self"` re-entry are gone. The script has a single grammar, read in full in `tools/run_preset.sh:126-279`: `<smoke|pilot|full> <DEV-n> <out-dir>` plus `--device`, `--systems [A-Za-z0-9_]+`, `--skip-transfer` and `--skip-robustness`. Everything else gives 64.
  - Order of the checks: pilot and full now start as `( trap '' HUP; run_recorded … ) & disown`, after the confirmatory scan, the seed check (regex plus exact registry match), the out-dir check, the lock, the tally and the probe. The background job inherits fd 9 and the validated `command` array.
  - Quoting: the user-supplied seed and out-dir are quoted everywhere and reach the meta only as argv to `python3 -I -c`. The out-dir is absolute, so it cannot be read as a flag. IFS is not imported by bash.
  - Probes, run in a scratch root with a scratch lock and `LPC_PYTHON=/bin/false`:
    - `__record`, `record` and `--record` with fd 9 open on the lock, a plain file and `sh -c touch …`: 64 each, nothing ran;
    - a seed `DEV-1` followed by a newline, or by `\x01`: 64;
    - a trailing `--`: 64.
  - The new test `test_no_hidden_mode_runs_a_command` copies my original probe: fd 9 on `$LPC_GPU_LOCK`, a plain file, then `sh -c touch`. On the old code it would have failed, because the marker gets created and the exit is 0. So it would have caught the hole. The text check is a regression guard. The front-end test checks the meta pid equals the printed pid (the `$BASHPID` change).
  - Residual risk, not a finding: anyone who controls the environment can still go around the wrapper. The ways are `PATH` fakes for `flock` or `python3`, `BASH_ENV`, exported bash functions, `LPC_GPU_LOCK` pointing at another file, and `LPC_PYTHON` pointing at any program. These need a deliberate environment prefix or a planted file. The plan and §4.5 sanction them (the tests depend on them). Noted for the owner's review before the freeze.
- **R2: fixed.** `os.walk(..., onerror=)` records each directory that cannot be listed, with its path, in `unreadable`. `sum` names it and `check` exits 65. The new test restores the mode in `finally` and is skipped as root, with the reason given. Its hand sum is 36000 s seen and unreadable 1.
- **R3: fixed.** A non-empty `PYTEST_ADDOPTS` or `PYTEST_PLUGINS` gives 64 with one line, before anything starts. Three cases are added to (e). `FakeRoot.environment` now strips `PYTEST_*`, so the tests do not depend on the caller's environment. No assertion is weakened.
- **R4: fixed.** A one-line TIMEOUT message is printed for both 124 and 137. The 137 wording is accurate: it gives the elapsed time, the limit plus the 30 s grace, and says an external SIGKILL gives the same code. It still says "investigate, do not raise".
- **Scope and evidence.**
  - Only the files these fixes need changed: the three tools, three unit test files, the helper and the unit file. `tests/integration/test_preset_wrapper.py` is unchanged, so criterion (k), the real smoke comparison against a direct run, is still tested. Its rerun is logged (`2 passed`), as it should be after the `run_preset.sh` change.
  - The one removed test (`test_record_refuses_without_the_lock_on_fd_9`) tested the deleted mode. The new tests replace it and are stricter. No other assertion changed.
  - The earlier review text is untouched. The commit names the unit and carries `Agent: claude-sonnet-5-5`. Modes are still 100755.
- **Owner checkpoint unchanged:** needs owner review before freeze (seed check, `run.meta.json`, the LPC.AUTH.3 enforcement). R5 stays routed to the owner.
- **Verdict: approve.** R1 to R4 fixed; no new findings.

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:

## Referral

<only if halted; use the form in agent-instructions.md, LPC.AI.13>

### Plan amendment 2026-10-10 (answers to the plan's questions), claude-sonnet-5-5 (main session), before execution (VV.3)

Q1 to Q6 are answered in `DEC-0005` (proposed, for owner confirmation; see `docs/agent/records/decisions.md` on `main`). In short: the smoke comparison excludes the wall-clock `seconds` fields (Q1); calendar week is the ISO week in UTC and no shared tally is added (Q2); the XLA thread-cap flag is not set (Q3); the wrapper tests are split into `tests/unit/test_tools_run_tests.py`, `test_tools_run_preset.py` and `test_tools_gpu_hours.py` instead of the single `test_tools_wrappers.py` (Q4; the radius in the criteria is read accordingly); `run.meta.json` has the fixed field list and no peak memory (Q5); CPU pilot and full runs take the same lock (Q6). No acceptance criterion changes. Do not edit `decisions.md`, `defects.md` or `queue.md` in this branch.
