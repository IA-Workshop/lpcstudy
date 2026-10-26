# Phase J analysis freeze (WU-0051)

**DEVELOPMENT, phase J.** Main session (claude-opus-5-5), 2026-10-26. Frozen before any held-out seed (DEV-5 to DEV-9) was run or read.

## What is frozen

- **Commit.** The tag `phasej-freeze` on develop, the commit that adds this note. Its `lpcstudy/` tree is `99e97619e5354033a133733e5e0703b13b1fa78e` and its `tools/` tree is `1d8bac62f0f48a7d68155d6c9f4b6f968ca33611`. The code is identical to analysis commit 33cb71e, which made the exploration records.
- **Files** (git blob hashes):

| File | Blob |
|---|---|
| `lpcstudy/contribution.py` | `629cd60c0f8d17b5f38c1753029d3be976fe6a1b` |
| `lpcstudy/joint_decisions.py` | `a04ee3d825e31f9444b96a968a6f15991f27153c` |
| `lpcstudy/mechanisms.py` | `32622e691acda32d0fe03091453af9de365b12d6` |
| `lpcstudy/dump.py` | `3a3d273ce5399426e7aca6549eb5079f27f58c9a` |
| `lpcstudy/config.py` | `99b6609d0605b6cc164d0b1f4c3103ad298474c1` |
| `lpcstudy/pipeline.py` | `a10b4c45b81aad2ac2eeb6d5976cc60d1d1c65b1` |
| `tools/lpc_contrib.py` | `e095b308673567df0774e79e13d989ec7cd7b3f3` |
| `tools/lpc_contrib_ce.py` | `eca7628d8d6867007e13bc07635587549e8f2580` |
| `tools/lpc_replicate.py` | `02d3411784e7e504538c83e870509e7799491905` |
| `tools/run_preset.sh` | `816df7addb38a977f8d52e2584c9935d4ce7bcc3` |

- **Design.** The plan (`2026-10-26-phase-j-lpc-contribution-plan.md` §3 to §5, amended by §8 to §10) and the math spec (`2026-10-26-phase-j-math-spec.md`: M-1 to M-8, addenda R1 to R3 and S1 to S4).
- **Predictions.** Plan §4 and the math spec's "Refined predictions", as written before any phase J data. The exploration report (`2026-10-26-phase-j-exploration-report.md` §2) compares them with the exploration seeds; that comparison is not a prediction.
- **Replication rule.** M-6 with S1 to S4, as implemented in `tools/lpc_replicate.py`: at least 4 of 5 seeds and no contradiction; the claim-level fallback; point readings never contradict; C1 shown for display only. The expected number of false replications is reported per family, using r from `2026-10-26-phase-j-r-measurement.md`.
- **Gate.** Freeze gate at 2b2891c: unit 2163 passed, integration 29 passed, slow 210 passed. Later changes (S2 in `mechanisms.py`, the replication tool) passed their blast radius: unit 141 passed, integration 7 passed.

## Procedure for the held-out seeds (WU-0051, WU-0052)

1. Clean detached worktree at `phasej-freeze`. For each of DEV-5 to DEV-9, one at a time under the lock:
   `tools/run_preset.sh phasej DEV-n runs/dev/phj-DEV-n --device gpu --skip-robustness --states-dump`
2. One manifest line per run (commit, seed, device, wall, sha256 of `results.json`), with the validation gate per system.
3. Analysis, once per seed, on CPU, in the same worktree. First check `git diff --quiet phasej-freeze -- lpcstudy tools`, which must pass. Then:
   `tools/lpc_contrib.py <run>/phasej --out <run>/contrib-freeze` and `tools/lpc_contrib_ce.py <run>/phasej --abd <run>/contrib-freeze --out <run>/contrib-freeze`
4. Replication, once: `tools/lpc_replicate.py <run DEV-5..9>/contrib-freeze --out runs/dev/replication-phasej-freeze`, in rule mode (no `--exploratory`).
5. No analysis code changes between step 1 and step 4. If a tool refuses or fails, the failure is reported as it is. Any fix is a new commit, recorded as a departure, and its results are labeled as made after the freeze.

A validation-gate failure on a held-out seed is reported, and that system's rows for that seed are marked provisional. The seed is not redrawn.
