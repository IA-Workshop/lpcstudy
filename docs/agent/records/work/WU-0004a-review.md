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
