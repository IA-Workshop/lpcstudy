# WU-0004a: independent review

- **Reviewer:** `reviewer`, claude-opus-5-5, fresh context, 2026-10-18.
- **Scope:** branch `wu/0004a-dirty-guard`, `7b6f6e6..54816a9` (one commit). Plan: `WU-0004a-dirty-guard.md` (A1 to A7, Q1, Q2). Requirement: owner ruling B8 (amendments note section 35; DEC-0008 C; freeze-blockers note B8).
- **Method:** reading, plus read-only git and two offline probes: a throwaway repository in the reviewer's scratchpad, and a listing of the `lpcstudy` modules loaded when `lpcstudy.__main__` is imported. No test, no preset, no sealed flag, no sealed seed. The developer's recorded radius stands: `184 passed` (once). The integration tier and the C16 DEV-0 smoke are still to be run by the main session.
- **Owner checkpoint:** seed and provenance code. **Needs owner review before freeze** (LPC.PC.11).

## Checks

1. **Placement: correct on every path.**
   - `choose_clean_tree` runs inside the refusal `try` in `main` (`lpcstudy/__main__.py:192`). It comes after `choose_refine_steps` and `choose_states_dump` and before `choose_seed`, so it also precedes `provenance.collect` (l. 206) and `out_dir.mkdir` (l. 210).
   - `--report-only` passes through the same `try`, so it is guarded too. A1 covers it: `calls == [git]`, with no seed read.
   - The only production caller of `confirmatory_seed` is `choose_seed` (`__main__.py:163`). `choose_seed` is called only from `main`. No `tools/` script or `docs/` script imports either function.
   - `tools/run_preset.sh` refuses any argument that names the confirmatory path (l. 139), so the wrapper cannot reach it.
   - `allow_abbrev=False`: a prefix of the flag lands in `extras` and leaves `args.confirmatory` false. `choose_seed` then refuses it as an unrecognized option, and no seed is read.
   - The guard is a CLI guard. A Python caller of `lpcstudy.seeds.confirmatory_seed` bypasses it, as the ruling ("refused by the CLI") permits.
2. **Development runs are unaffected.** `if not args.confirmatory: return` comes before any git call. A4 and A6 check this with a spy that fails if git is read.
3. **Unknown-commit logic: correct.**
   - The regex `[0-9a-f]{40}|[0-9a-f]{64}` under `re.fullmatch` refuses `None`, `""`, `"unknown"` and abbreviated names. `dirty is None` is refused too.
   - Git's error text is discarded (`_git_error`). The two reasons are constants. The result is exit 64 with one line.
   - An unborn `HEAD` (`rev-parse` exits 128), a directory outside any repository and a missing git binary all become `(None, None, err)` in `git_state`. The real-git cases cover the first two.
4. **Tests: sound, with independent references.**
   - The references are hand-written lines and call lists. Exact asserts; no tolerance.
   - A1 (7 states x 2 shapes) would catch the guard moving after `choose_seed`, since `"seed"` would appear in `calls`. It would also catch a guard that drops the `dirty is None` arm (the `dirty-flag-unknown` case) or that echoes the git text (`boom`, `second line`).
   - `REAL_GIT_STATE` is captured at import time, before any fixture, so it is the production reader.
   - The real-git cases run on `tmp_path` repositories, with `GIT_CEILING_DIRECTORIES` set and `ROOT` patched. They never touch the real repository.
   - The autouse `_clean_tree` pin replaces no existing real-git assertion. The base `test___main__.py` had none; the real-git provenance checks live in `test_provenance.py`, which is unchanged. No existing assert or expected value was changed (PRIME.2 holds).
5. **Integration driver pin (`tests/integration/test_cli_seeds.py:30-33`): correct by reading.**
   - The pin rebinds `provenance.git_state` in the module namespace before `main` runs. The guard looks the function up through the module at call time, so the pin takes effect. So does `collect`, through the module global, though none of these cases reaches it.
   - That file has no tree-guard case, so the pin cannot mask a guard failure there.
   - Without the pin, on a dirty checkout the five sealed-flag cases would still pass (same prefix, exit 64), but on the dirty-tree refusal instead of their own. The pin makes them test what they claim.
   - These cases assert only the prefix, which was already so before this change. Not a finding of this unit.
6. **TOCTOU.**
   - *Window between the guard and `collect`:* see R1.
   - *Changes after `collect`:* acceptable. Importing `lpcstudy.__main__` loads every `lpcstudy` module, as the probe listing shows: the function-level imports in `analysis`, `validation` and `oracle` find their modules already loaded. So an edit made during the run cannot change the code that runs.
   - The only modules imported after the guard are `tools.ledger` and the seal script's module, inside `seeds.check_commitment` (`lpcstudy/seeds.py:142-143`). That import falls in the window R1 covers.
   - Re-reading git in `finish` would add a key (the same key-set cost as Q2). It is not needed for B8.
7. **Governance: holds.**
   - The diff touches `lpcstudy/__main__.py`, two test files, the new unit file and `queue.md`. `queue.md` is one appended line.
   - Nothing touches the seal script, the seed registry, the ledger, `seeds/`, `.claude/` or governance.
   - The commit names the unit and ends with `Co-Authored-By` and `Agent: claude-sonnet-5-5`. History is not rewritten.
   - No randomness and no float handling are involved.

## Findings

### R1 (medium): the block of an accepted sealed run does not record "exactly what was checked"; the guard-to-`collect` window is unhandled

- **Where.** `lpcstudy/__main__.py:113-115` (docstring) and `main` (l. 192 against l. 206).
- **Evidence.**
  - The docstring says the block "records exactly what was checked". It does not: `collect` calls `git_state` a second time, after `confirmatory_seed`. A2 asserts this order itself: `[git, seed, collect, git]`.
  - If the tree is dirtied, or `HEAD` moves, between the two reads, the sealed run is accepted and runs to completion. Its own block then records `dirty: true` or a different commit.
  - The window is short, but it contains the import of `tools.ledger` and the seal script's module. The seed is single-use, so a sealed run whose block says `dirty: true` is spent and cannot be used. It is visible, not silent, yet nothing refuses it.
- **Required fix (preferred).**
  - `choose_clean_tree` returns the commit it checked.
  - In `main`, for a sealed run, after `collect` and before `out_dir.mkdir`: refuse with exit 64 and one line unless `block["commit"]` equals the checked commit and `block["dirty"] is False`. Nothing has been written at that point.
  - Add a unit test whose stub returns a clean state on the first read and a dirty one (then a different commit) on the second. Expect: 64, one exact line, out directory absent.
  - With this in place the docstring sentence is true.
- **Acceptable alternative (owner's call).** Correct the docstring: the block records a second read taken just after the check. State in the unit file that the window is accepted, and why.

### R2 (low): the "clean" reading depends on user git configuration and environment

- **Where.** The guard relies on `provenance.git_state` (`lpcstudy/provenance.py:86-87`: `git -C ROOT status --porcelain`). The docstring at `__main__.py:116` says "untracked files count".
- **Evidence.** Shown on a throwaway repository in the scratchpad:
  - `git -c status.showUntrackedFiles=no status --porcelain` printed nothing while an untracked `numpy.py` was present. That setting can come from repository, global or system config.
  - After `git update-index --skip-worktree f`, a modified tracked file `f` also printed nothing.
  - Both would let a sealed run pass the guard while the tree is not clean. An untracked `numpy.py` in the repository root matters in practice: under `python -m lpcstudy` the working directory is first on `sys.path`, so such a file would shadow the real package.
  - `git` also honours `GIT_DIR` and `GIT_WORK_TREE` in the inherited environment. With either set, `-C ROOT` can report the state of another repository.
  - None of these is set here (`git config --get-regexp status.` is empty). This is a robustness gap against accidents, not a present defect.
- **Required fix (one of the two, owner's choice; both touch provenance or procedure, so owner review applies).**
  - **(a) Harden `git_state`.** Use `status --porcelain --untracked-files=normal --ignore-submodules=none` and a subprocess environment with `GIT_DIR`, `GIT_WORK_TREE` and `GIT_INDEX_FILE` removed. For the sealed path, also refuse if `git ls-files -v` shows any `S` or lowercase-tag entry. Add a real-git test using `-c status.showUntrackedFiles=no` and skip-worktree on a `tmp_path` repository. `test_provenance.py` then joins the radius.
  - **(b) Record the limitation.** Put it in the unit file and add three items to the WU-0015.1 pre-run checks: `status.showUntrackedFiles` unset, `git ls-files -v` showing no skip-worktree or assume-unchanged entries, and no `GIT_*` repository variables in the environment.

### R3 (low, governance): the Q1 follow-up (tag check) is not registered anywhere it will be picked up

- **Where.** `WU-0004a-dirty-guard.md` Q1 calls the tag check "a small follow-up", but no queue entry or freeze-blocker line records it.
- **Evidence.**
  - The ROADMAP's WU-0015.1 criterion is "`git status --porcelain` empty and `git describe --tags` equals `freeze-1`". It is a manual pre-run check, separated in time from the launch.
  - Nothing compares the commit recorded in a sealed block with `freeze-1^{commit}` after the run.
- **Required fix.**
  - Append a queue line (or a line in the freeze-blockers note under B8) that records the deferred tag check as an owner decision before freeze. Two options: (i) a CLI comparison of `commit` with `git rev-parse freeze-1^{commit}` once the tag name is fixed by WU-0004.7; (ii) an added WU-0015.2/WU-0016 acceptance item: "the block's `commit` equals `git rev-parse freeze-1^{commit}`".
  - No code change in this unit.

## Reviewer's view on Q1 and Q2

- **Q1.** Leaving the tag check out leaves a gap: any clean, known commit is accepted, including one after the freeze. WU-0015.1's manual check (`git describe --tags` equals `freeze-1` exactly, which holds only when `HEAD` is at the tag) covers this adequately if it is done just before launch, with the tree untouched in between. The gap is recoverable because the block records `commit` and can be compared after the run. My view: acceptable for this unit, on condition that R3 registers the follow-up. Once `freeze-1` exists, the CLI check is cheap, and the owner should prefer it to a manual-only control.
- **Q2.** I agree with leaving `VmHWM` out. B8 makes it optional. Adding it changes the provenance key set and three key lists, and the wrapper cannot read the child's `VmHWM`. A separate unit with the integration tier is the right vehicle.

## Verdict

**approve with fixes.** 3 findings: R1 medium, R2 low, R3 low. No correctness defect in the guard as specified: placement, the refusal logic and the tests are sound. The unit still **needs owner review before freeze**.

## Round 2

- **Reviewer:** `reviewer`, claude-opus-5-5, fresh context, 2026-10-18.
- **Scope:** fix round 1, `git diff 8fea300..6c740e6` (commit `6c740e6`), limited to R1 to R3, with an adversarial reading of the new seed and provenance code (LPC.PC.7).
- **Method:** reading, read-only git, and probes on throwaway repositories in the reviewer's scratchpad (`GIT_CEILING_DIRECTORIES` set). No test was run. No preset, sealed flag or sealed seed was used. The developer's recorded radius stands: `302 passed` (once, 9 unit files, `test_provenance.py` included).
- **Owner checkpoint:** seed and provenance code. **Needs owner review before freeze** (LPC.PC.11).

### R1: fixed

- **Return value.** `choose_clean_tree` returns the checked commit for a sealed request (`__main__.py:150`). It returns `None` only for a development run; every other sealed path raises.
- **Every sealed path goes through both checks.** With the flag, `checked_commit` is either a full object name or the `try` at l. 222-229 has already returned 64. So the block at l. 243-250 always runs for a sealed request.
  - On a run, it compares `block["commit"]` and `block["dirty"]` from `collect` (l. 239).
  - On `--report-only`, it takes a direct `git_state` read (l. 245).
  - In both cases this happens before `out_dir.mkdir` (l. 251), the log handler (l. 273) and any `save_json`.
  - `choose_seed` is still the only production caller of `confirmatory_seed`. No path reaches the seed without the first check, and none reaches output without the second.
- **The comparison is strict.** `commit != checked or dirty is not False` refuses a moved `HEAD`, a dirty tree, an unreadable state (`None, None`) and an unknown `dirty`. `git_state` returns a real `bool` (`bool(...) or any(...)`), so `is not False` cannot reject a clean read by type. The result is exit 64 with one line, and git's error text is not echoed.
- **Tests.** The new test covers 4 second-read states for each of run and report-only. It asserts the exact line, the exact call lists (`[git, seed, collect, git]` and `[git, seed, git]`), that no directory exists, and that neither the seed, the salt nor the git text appears in the output.
  - The stub is installed under `spy_calls`. `collect` reaches it through the module global, so the second read really is the block's read.
  - The truth-table test covers `(None, False)` and `checked is None`.
- **Changed round-0 assertions.** Both are stricter: `is None` became `== CLEAN_COMMIT` (A6), and `== <the test's own git rev-parse HEAD>` (real git). PRIME.2 holds.
- **Docstring.** The `choose_clean_tree` docstring now describes the second read correctly. The `check_tree_unchanged` docstring states honestly that the one-time draw is not undone. One stale line remains in the A6 test docstring: see R6.

### R2: fixed, with residuals R4 and R5

- **Ordinary checkouts read the same.** `ls-files -v` on this worktree and on the main checkout shows only `H` entries (533 and 136). There is no `.gitmodules`, so `--ignore-submodules=none` has no effect here. The block key set is unchanged, and `test_commit_and_dirty_equal_the_tests_own_git_calls` is untouched. Its plain `bool(git status --porcelain)` still equals the hardened value in this checkout.
- **Tag letters (git 2.56, checked in the scratchpad).**
  - Without `-t`/`-o`, `ls-files -v` lists cached entries only. Their tags are `H`, `S`, `M` (unmerged), and lowercase when `CE_VALID` is set.
  - An unmerged path already shows in `status` (`UU`), so missing `M`/`m` from `HIDDEN_TAGS` hides nothing.
  - The built-in fsmonitor (`core.fsmonitor=true`) did not turn tags lowercase under `-v`; only `-f` does that.
  - Two settings make a checkout read dirty that read clean before:
    - `core.ignoreStat=true` sets `h` on files that git updates.
    - A sparse checkout sets `S`.
  - Neither is set here, and both cases are conservative, since git does not track changes to those files. **No finding.** The owner should know that a sparse or `ignoreStat` checkout now records `dirty: true` on development runs too.
- **Other callers.** In production, `git_state` is called only from `collect` (`provenance.py:386`) and `__main__` (l. 142, 245). The test pins in `test_cli_seeds.py` and `test___main__.py` replace it whole, so they are unaffected. One duplicate of its definition has diverged: see R5.
- **Test safety.**
  - The new real-git tests build repositories under `tmp_path` with `GIT_CEILING_DIRECTORIES` set.
  - The `GIT_DIR` test makes the other repository before it sets the variables, and `monkeypatch` restores them afterwards.
  - Each hazard is established by the test's own plain git call, which is a sound independent reference.
  - None of them touches the real repository under the project's conditions: there are no git hooks or `core.hooksPath`, and the only `GIT_*` variable in the environment is `GIT_EDITOR`.
  - *Note, not a finding:* the test helpers' own git calls (`make_repository`, and the round-0 real-git helper) do not strip the redirect variables themselves. A suite run started with `GIT_DIR`/`GIT_INDEX_FILE` set, for example from inside a git hook, would have `add`/`commit` act on the real repository. Passing `env` without `provenance.GIT_REDIRECT_VARIABLES` in those helpers would close this cheaply.

### R3: fixed

- The follow-up U1 is in the unit Log and in a `queue.md` line, with both options and "owner decision before freeze". This is what was asked; no code change.

### New findings

#### R4 (low): untracked files can still be hidden by configuration; two docstrings claim otherwise

- **Where.** `lpcstudy/__main__.py:119-120` ("untracked files count, whatever the git configuration says") and `lpcstudy/provenance.py:79-81` ("a user, global or system setting such as `status.showUntrackedFiles=no` cannot hide a file").
- **Evidence (scratchpad).**
  - With an untracked `numpy.py`, `git -c core.excludesFile=<file listing numpy.py> status --porcelain --untracked-files=normal --ignore-submodules=none` prints nothing.
  - The same happens when the setting arrives through `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_0`/`GIT_CONFIG_VALUE_0`, which `GIT_REDIRECT_VARIABLES` does not strip (nor `GIT_CONFIG_PARAMETERS` or `GIT_CONFIG_GLOBAL`).
  - It also happens with a line in `.git/info/exclude`.
  - Adding `-c core.excludesFile=/dev/null` restored `?? numpy.py` even with the environment injection.
  - Here, global and system `core.excludesFile` are unset, `~/.config/git/ignore` is absent, and `.git/info/exclude` holds only `.venv`. So this is not a present defect, but the documented guarantee is false. That matters because the owner will rely on these docstrings at the B8 review.
- **Fix (owner's choice; provenance code).** Either:
  - (a) Pass `-c core.excludesFile=/dev/null` to the status call, and drop `GIT_CONFIG_PARAMETERS`, `GIT_CONFIG_COUNT` and its `GIT_CONFIG_KEY_n`/`GIT_CONFIG_VALUE_n` from the environment. Add a real-git test using `core.excludesFile`, with the hazard shown by the test's own plain call. `.git/info/exclude` stays a residual that the docstrings must name.
  - (b) Correct both docstrings to name the residual (global/system or environment `core.excludesFile`, `.git/info/exclude`). Add a WU-0015.1 pre-run item: `git config --show-origin --get-regexp '^core\.excludesfile'` empty, no `GIT_CONFIG_*` variables, `.git/info/exclude` only `.venv`.

#### R5 (low): `tools/lm_doubling.py` `git_dirty` still claims to be the provenance definition, and no longer is

- **Where.** `tools/lm_doubling.py:1388-1392`. It is used as a refusal gate at l. 1749-1752 and recorded in the probe's provenance (l. 1767).
- **Evidence.**
  - The docstring says "``bool(git status --porcelain)`` ..., the definition of ``provenance.git_state``".
  - After R2, `git_state` has explicit untracked and submodule modes, strips the redirect variables and counts index bits. `git_dirty` does none of these.
  - So the probe can accept, and record as clean, a tree that the arms' own provenance would record as dirty, under the configurations R2 guards against. Its precondition check compares the arms' `dirty` (new definition) with its own (old definition).
- **Fix.** Preferred: `git_dirty` returns `provenance.git_state(ROOT)[1]`, and `current_commit` returns `[0]` for the same reason. `test_tools_lm_doubling.py` then joins the radius. Alternative: correct the docstring and record the divergence in the unit Log.

#### R6 (low): two texts now misstate what they describe

- **Where.**
  - `lpcstudy/__main__.py:148-149`. The dirty refusal says "(git status --porcelain is not empty)". Since R2, `dirty` can be true with an empty status, from a skip-worktree or assume-unchanged entry. The one line would then send the owner to a `git status` that shows nothing (PRIME.4: say why).
  - `tests/unit/test___main__.py:789`. The A6 reference text still says "with the flag and a clean state it returns ``None``", while the assertion is now `== CLEAN_COMMIT`. A test's stated reference must match what it asserts (LPC.PC.21).
- **Fix.**
  - Reword the reason, for example "(git status --porcelain is not empty, or a tracked file is hidden by skip-worktree or assume-unchanged)". Update `DIRTY_LINE` (l. 650-651) to match, and record it in the Log as a deliberate message change, not a loosening.
  - Correct the A6 docstring line.

### Verdict (round 2)

**approve with fixes.** R1, R2 and R3 are fixed. 3 new findings, all low: R4, R5, R6. No path reaches the sealed seed without the first check or output without the second. The unit still **needs owner review before freeze** (seed and provenance code). One fix round (the second and last) remains before `/refer` (DEVELOPMENT_WORKFLOW.md §2.3).
