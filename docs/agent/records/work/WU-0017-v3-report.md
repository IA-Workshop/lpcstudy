# WU-0017: v3 report and figures

| Field | Value |
| --- | --- |
| Status | WU-0017.1 executed 2026-10-21 (second attempt, lock free): the two `--report-only` runs give a `RESULTS.md` byte-identical to the stored one (see the entry below); the earlier refusals are kept in the log. WU-0017.2: figures byte-identical, but the captions do not name an experiment or a v3 identifier (gap, see below). WU-0017.3 pending: owner and student read. |
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

### 2026-10-21 (later) WU-0017.1 executed with the hardened block (claude-sonnet-5-5)

4.9 checklist: (1) no code or test change; records only. (2) No test to run. (3) Run lock: `pgrep` showed no `lpcstudy --preset` process; `flock -n /tmp/lpcstudy-gpu.lock` was taken by each run. (4) `JAX_PLATFORMS=cpu` (set in the command), CPU only, post-processing (no recomputation). (5) Outputs only in `/tmp/tmp.yvHoCJpzKH` (kept, outside every repository tree); the sealed directory was never an output; the sealed-run flag was not used or named. (6) The worktree `lpcstudy-wt/run/regen-freeze-1`: clean before and after (`git status --short` empty), HEAD `df8928f`; `lpcstudy.__file__` printed `.../run/regen-freeze-1/lpcstudy/__init__.py` (the freeze-1 code).

The block of this file was run exactly as written (output of the two runs redirected to `$S/ro1.out` and `$S/ro2.out`, both empty).

| Item | Result |
|---|---|
| Input copies, sha256 | both `ae4b0fe5bf488f6c147bce6c91a2398e87408f6a5d372ae66d89bdfc90b0cebe` (equal to the manifest) |
| Exit code run 1, run 2 | 0 and 0 |
| `ro1/full/RESULTS.md` sha256 | `2a4c1d06859d07584b1633c6e7f1b5df205ffe445402509834383fb474649577` |
| `ro2/full/RESULTS.md` sha256 | `2a4c1d06859d07584b1633c6e7f1b5df205ffe445402509834383fb474649577` |
| Stored `RESULTS.md` of run-1 | `2a4c1d06859d07584b1633c6e7f1b5df205ffe445402509834383fb474649577`: all three equal |
| Rewritten `results.json` (ro1, ro2) | both `ae4b0fe5bf488f6c147bce6c91a2398e87408f6a5d372ae66d89bdfc90b0cebe`: equal to the stored one, no difference to explain (the verdicts recomputed by `--report-only` equal the stored ones; the default development seed id did not change any byte) |

Result: WU-0017.1 acceptance "regenerates `RESULTS.md` identically on two runs": **met** (the two runs are byte-equal to each other and to the file of record). Provenance and label are printed from the stored block, so the header still reads `CONFIRMATORY: UNPROMOTED`. The open question of 2026-10-21 (seed id) is closed: no difference arose.

**Acceptance sample of ten narrative numbers** (the regenerated `RESULTS.md` is the stored file byte for byte; leaves read from `results.json` `ae4b0fe5...cebe`, the GPU file `b768cb03...5887` and the compare text):

| # | Group | Narrative number in `RESULTS.md` | Leaf | Leaf value |
|---|---|---|---|---|
| 1 | primary H2b | chua rho rank corr 0.26 | `systems/chua/H2b/noise/mean_state_spearman` | 0.25753480505742554 |
| 2 | primary H3c | chua A5/A4 interval [0.9752, 1.062] | `systems/chua/H3c/ci` | [0.9751543853530962, 1.0622020621421788] |
| 3 | primary H2a(ii) | lorenz63 zero interval [-0.047, 0.1] | `systems/lorenz63/H2a/part_ii/zero/ci` | [-0.04719450219020303, 0.10145835812962745] |
| 4 | primary H2a(ii) | rossler interior interval [-0.048, 0.17] | `systems/rossler/H2a/part_ii/interior/ci` | [-0.048257975512058134, 0.16619322462551567] |
| 5 | secondary H1b | chua PLP 0.98 [0.942, 1.02] | `systems/chua/H1b/PLP/slope`, `.../ci` | 0.9795509184294233, [0.942187171833557, 1.0191930543926104] |
| 6 | secondary H1c | lorenz63 PLP 0.612 | `systems/lorenz63/H1c/PLP/median_ratio` | 0.6122381592173741 |
| 7 | secondary H2d | chua A4/A3-1 = -5% | `systems/chua/H2d/in_distribution_excess` | -0.04998601632589905 |
| 8 | secondary H2e | rossler rho=0.01 median change 0.36 | `systems/rossler/H2e/by_noise/0.01/median_change` | 0.35637111813376077 |
| 9 | cross-check (GPU `RESULTS.md`) | lorenz63 H3c A5/A4 0.6824 [0.434, 0.9624], pass | GPU `systems/lorenz63/H3c/A5_over_A4_mse`, `.../verdict` | 0.6823587497808661, pass (CPU word: inconclusive) |
| 10 | cross-check (compare text) | max z away 2.21 | `runs/confirmatory/run-1-compare.txt` line 381 (a printed statistic, not a results leaf) | 2.21 |

Result: 10 of 10 match to the printed digits (rows 3 and 4 and the interval rows round endpoint values as printed).

**Counts for H2a(ii)** from the stored verdict words, `systems/<s>/H2a/part_ii/<part>/verdict`: lorenz63 zero inconclusive, interior fail; rossler zero inconclusive, interior inconclusive; chua zero inconclusive, interior fail. Counter: **2 fail, 4 inconclusive, 0 pass** (6 parts). The two failing parts are the interior parts of lorenz63 and chua. The Rossler interior interval [-0.048257975512058134, 0.16619322462551567] has upper minus lower 0.2144 (arithmetic on the stored endpoints), more than the band width 0.2.

### WU-0017.2 Figures (checked 2026-10-21, not closed)

- `--report-only` rewrote four figures in each scratch directory: `kaplan_meier_by_rule.png`, `knob_response_library.png`, `regret_vs_regimes.png`, `separation_weight_vs_horizon.png`. All four are byte-identical to the stored `runs/confirmatory/run-1/full/figures/*` (`cmp`) and to each other (ro1 against ro2).
- Banned references: `grep -i -E "shift|transfer|lorenz-?96|a4f"` over `lpcstudy/report.py`, `lpcstudy/budget.py` (where the captions live, `FIGURE_CAPTIONS`) and the regenerated `RESULTS.md`: no match. (`lpcstudy/figures.py` does not exist at `freeze-1`; `make_figures` is in `report.py`.)
- **Gap against the acceptance text** ("every figure caption names its experiment, its v3 identifier and the interval procedure"): the four captions in `budget.FIGURE_CAPTIONS` name neither an experiment (E1 to E6) nor a v3 identifier. They state that no interval is shown (so no interval procedure applies). The frozen code is not edited (`lpcstudy/` is frozen at `freeze-1`; WU-0017's documents are built from `freeze-1`). The three figures of the findings document (F1, F2, F3) are made by `tools/findings_build.py` and do name experiments and v3 identifiers, but they are not the figures of the `RESULTS.md`. The owner decides: accept the four captions as sealed output, or have the promoted report state the experiment and identifier of each figure in its text (not in the PNGs). Not marked done.

### Still not done in WU-0017.1

NVVUQ.22 six items per QoI and NVVUQ.16 four items per interval: not checked here. WU-0017.3: pending; owner and student read.

## Review

- **Reviewer:** none yet.
- **Findings and resolution:**

## Audit

- Is the definition of done met? No: WU-0017.1 regeneration and ten-number sample met, NVVUQ.22 and NVVUQ.16 item checks open; WU-0017.2 has the caption gap above; WU-0017.3 pending.
- Defects recorded: none.
- Notes for successors: the hook matches `--preset full` for a CPU-only `--report-only`; the run needs the GPU lock free or an owner decision (see above).
