# WU-0017: v3 report and figures

| Field | Value |
| --- | --- |
| Status | WU-0017.1 **not executed** (blocked: the two `--report-only` runs were refused by a hook, see the log; command for the owner below). WU-0017.2 not started. WU-0017.3 pending: owner and student read. |
| Class | CSQ2 |
| Agent(s) | claude-sonnet-5-5 (developer), 2026-10-21 |
| Estimate | the two report-only runs are CPU, post-processing only (no recomputation; the figure and report code reads `results.json`) |

## Plan (written before execution)

The plan is `ROADMAP.md` rows WU-0017.1 to WU-0017.3 and the phase G acceptance paragraph. WU-0017.1: "`--report-only` on the confirmatory `results.json` regenerates `RESULTS.md` identically on two runs; every number in the narrative is traceable to a key in `results.json` (the auditor samples ten); every reported QoI carries the six NVVUQ.22 items; every interval carries the four NVVUQ.16 items; the three primaries are labeled with level 1 - 0.05/3 and the intersection-union rule is stated." Per ROADMAP section 8 (phase H, line 306) and audit m5, the documents of WU-0017 and WU-0018 are built from `freeze-1` code, never from the extension code on develop: the runs go in the worktree `/home/brianm/projects/physics/chaos/lpcstudy-wt/run/regen-freeze-1` (clean, detached at `df8928fd06721d681469c9c3e40705e1b4b8053f`).

Decision on where outputs go (made 2026-10-21): `--report-only` rewrites `results.json` in its output directory (it recomputes `verdicts` and calls `save_json`) and rewrites `RESULTS.md` and the figures there. It must therefore never be pointed at the sealed run directory itself. The run worktree's `runs/` directory is ignored by git (`.gitignore`: `runs/`), so writing under it would not dirty tracked files, but it already holds the regeneration run-2 outputs; to keep that tree untouched, the outputs go to scratch directories outside every repository tree, each holding a copy of the stored `results.json` (sha256 `ae4b0fe5bf488f6c147bce6c91a2398e87408f6a5d372ae66d89bdfc90b0cebe`, verified equal to the sidecar after the copy). The tracked files of the run worktree are not modified.

## Log

### 2026-10-21 WU-0017.1: the two `--report-only` runs (NOT executed)

- Checks before: the run worktree `git status --short` empty and `git log -1` = `df8928f Freeze: ledger entries (classification, commitment)`. Two scratch directories were made, each with `full/results.json` copied from `runs/confirmatory/run-1/full/results.json` (sha256 checked: `ae4b0fe5...cebe`).
- Command tried, from the run worktree, with its own `.venv`: `.venv/bin/python -m lpcstudy --preset full --report-only --out <scratch>/ro1`. It does not name the sealed-run option: `--report-only` is accepted without it. The default seed id then is the development seed id; see the open question below.
- **Result: refused by the project's PreToolUse hook (`.claude/hooks/test_gate.py`): "pilot/full runs must hold the GPU lock: use tools/run_preset.sh, or ... flock -n ... python -m lpcstudy --preset ...".** The hook matches `--preset full` in any command, including a CPU-only report rebuild.
- Second attempt with the lock: `flock -n /tmp/lpcstudy-gpu.lock env JAX_PLATFORMS=cpu .venv/bin/python -m lpcstudy --preset full --report-only --out <scratch>/ro1`: exit 1 for both runs, the lock being held by the concurrent extension runs (`pgrep` showed two `--preset full ... --seed-id DEV-3` processes in `lpcstudy-wt/run/ext-run-392a069`; DEC-0039 allows concurrent runs). Nothing was written (no `RESULTS.md` appeared; the `results.json` copies are unchanged, sha256 still `ae4b0fe5...cebe`).
- I did not work around the hook (no other lock file, no calling `main()` from Python with the arguments split, no waiting in a loop). The lock protects the GPU, which this CPU job does not use; whether the hook should exempt `--report-only` or the owner should run the command is the owner's call.
- **Command for the owner to run** (or for a session when the lock is free), exactly:

```
set -e
cd /home/brianm/projects/physics/chaos/lpcstudy-wt/run/regen-freeze-1
test -z "$(git status --short)"                      # the worktree must be clean
.venv/bin/python -c 'import lpcstudy; print(lpcstudy.__file__)'   # must be under this worktree (freeze-1 code)
S=$(mktemp -d)                                        # a fresh empty directory outside the repository trees
mkdir -p $S/ro1/full $S/ro2/full
cp /home/brianm/projects/physics/chaos/lpcstudy/runs/confirmatory/run-1/full/results.json $S/ro1/full/
cp /home/brianm/projects/physics/chaos/lpcstudy/runs/confirmatory/run-1/full/results.json $S/ro2/full/
sha256sum $S/ro1/full/results.json $S/ro2/full/results.json   # both must read ae4b0fe5bf488f6c147bce6c91a2398e87408f6a5d372ae66d89bdfc90b0cebe
flock -n /tmp/lpcstudy-gpu.lock env JAX_PLATFORMS=cpu .venv/bin/python -m lpcstudy --preset full --report-only --out $S/ro1; echo "exit run 1: $?"
flock -n /tmp/lpcstudy-gpu.lock env JAX_PLATFORMS=cpu .venv/bin/python -m lpcstudy --preset full --report-only --out $S/ro2; echo "exit run 2: $?"
test -s $S/ro1/full/RESULTS.md && test -s $S/ro2/full/RESULTS.md   # both files must have been written by these runs
sha256sum $S/ro1/full/RESULTS.md $S/ro2/full/RESULTS.md $S/ro1/full/results.json $S/ro2/full/results.json
git status --short    # must print nothing
```

  With `set -e` a non-zero exit (for example `flock -n` exiting 1 because the lock is held) stops the block before any hash is read, and the directory is new each time, so no `RESULTS.md` of an earlier attempt can be hashed. Record both exit codes (0 and 0) and the printed `lpcstudy.__file__` in this log.

  Acceptance: the two `RESULTS.md` hashes are equal to each other and to `2a4c1d06859d07584b1633c6e7f1b5df205ffe445402509834383fb474649577` (the stored `RESULTS.md` of run-1); the rewritten `results.json` is equal to `ae4b0fe5bf488f6c147bce6c91a2398e87408f6a5d372ae66d89bdfc90b0cebe` or the difference is explained. If the lock is held by an extension run, wait for it (do not poll in a loop) or the owner decides on a CPU-only exemption.
- **Open question for the run (not decided here).** `--report-only` builds its configuration with the seed id that the command line gives; without the sealed-run option that is the default development seed id, not CONF-1. The header of `RESULTS.md` is printed from the stored provenance block, so the output is expected to be identical, but the code passes `config` to `verdicts()` and to the writers, so only the run can show it. If the two `RESULTS.md` files differ from the stored one, the likely cause is this seed id; the repeat then needs the sealed-run option with the owner's own environment, which only the owner can supply (an agent must not). Record the outcome here when it is known.

### 2026-10-21 WU-0017.1: sample of ten narrative numbers (pre-sample, not the acceptance evidence)

The acceptance sample is of the regenerated `RESULTS.md`. As the regeneration is not done, this is a sample of the stored `RESULTS.md` of run-1 (the file of record, `2a4c1d06...4577`) against the leaves of the stored `results.json` (`ae4b0fe5...cebe`), read by a throwaway Python script that loads `results.json` and prints the leaf. It samples the narrative table of section "Hypothesis verdicts" of `RESULTS.md`. Every value equals the leaf rounded to the digits printed.

| # | Narrative number (RESULTS.md) | Leaf in results.json | Leaf value |
|---|---|---|---|
| 1 | H1b lorenz63 PLP slope 0.824 | `systems/lorenz63/H1b/PLP/slope` | 0.8244337389065113 |
| 2 | H1c rossler PLP 0.974 | `systems/rossler/H1c/PLP/median_ratio` | 0.9736080911235441 |
| 3 | H2b lorenz63 rho rank corr 0.24 | `systems/lorenz63/H2b/noise/mean_state_spearman` | 0.2399830545530367 |
| 4 | H2b lorenz63 n_lib change 0.07 | `systems/lorenz63/H2b/library_change/mean_change` | 0.06981986195044869 |
| 5 | H3c lorenz63 A5/A4 0.7476 | `systems/lorenz63/H3c/A5_over_A4_mse` | 0.7476287754137357 |
| 6 | H3c rossler interval upper end 1.012 | `systems/rossler/H3c/ci/1` | 1.0119757967534697 |
| 7 | H2d lorenz63 A4/A3-1 = 24.7% | `systems/lorenz63/H2d/in_distribution_excess` | 0.24738133594222433 |
| 8 | H2e lorenz63 median change at rho 1% 0.39 | `systems/lorenz63/H2e/by_noise/0.01/median_change` | 0.39328067873070394 |
| 9 | gain within bound lorenz63 0.966 | `systems/lorenz63/gain_bound/fraction_within_bound` | 0.9659969088098919 |
| 10 | Q-N lorenz63 interior dR2 0.0018 | `systems/lorenz63/Q-N/oracle/logit_w_interior/delta_r2` | 0.0018016811579080194 |

Result: 10 of 10 match. This is a pre-sample and the auditor (WU-0018.1) draws its own ten from the regenerated file.

### Not yet done in WU-0017.1

- Regeneration of `RESULTS.md` twice, byte equality: not executed (above).
- Verification that every reported QoI carries the six NVVUQ.22 items and every interval the four NVVUQ.16 items, that the three primaries are labeled with level 1 - 0.05/3 and the intersection-union rule is stated: not checked in this unit; the interval labels of section B of the findings document are copied from the stored `RESULTS.md` (audit item 9 reads them as present), which is not the same check.
- The v3 report content that the ROADMAP row asks to add or carry (V&V status per QoI, known limitations DEF-0008, DEF-0009, section M13): the stored `RESULTS.md` of the official run is the sealed output of frozen code and is not edited. The additions the audit asks for (M1 verification status, M3 reproducibility wording, M4 DEF-0022) are proposed for the owner in `docs/agent/notes/2026-10-21-def0022-proposal.md` and `docs/agent/notes/2026-10-21-b1-minors-report.md`; they are not applied here.

### WU-0017.2 Figures for v3

Not started. `--report-only` also rebuilds the figures; the acceptance (every caption names its experiment, its v3 identifier and the interval procedure; no shift, transfer, Lorenz-96 or A4f reference) has not been checked.

### WU-0017.3 Owner and student read the report

**Pending; owner and student read.** Not done. No claim is made.

## Review

- **Reviewer:** none yet.
- **Findings and resolution:**

## Audit

- Is the definition of done met? No: WU-0017.1 is not executed, WU-0017.2 not started, WU-0017.3 pending.
- Defects recorded: none.
- Notes for successors: the hook matches `--preset full` for a CPU-only `--report-only`; the run needs the GPU lock free or an owner decision (see above).
