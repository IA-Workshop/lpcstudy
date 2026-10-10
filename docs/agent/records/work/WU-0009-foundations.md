# WU-0009: Foundations: baseline commit, environment, baseline smoke reference, queue reconciliation

| Field | Value |
| --- | --- |
| Status | in progress |
| Class | CSQ3 development |
| Agent(s) | claude-sonnet-5-5 (main session); claude-opus-5-5 (planner, WU-0009.4) under governance ledger entry 5 |
| Estimate | four sub-tasks of effort S (ROADMAP.md §2, phase A) |

## Plan (written before execution)

- **Scope:** in: ROADMAP.md §2 phase A sub-tasks WU-0009.1 to WU-0009.4 (repository baseline, workstation environment, baseline smoke reference, reconciliation of `queue.md` with the roadmap). Out: any change to `lpcstudy/` or `tests/`, to governance or `.claude/`, and any study design (LPC.PC.1). Serves REPRO.1, LPC.AI.3, LPC.AI.8, LPC.PC.17, LPC.PC.18, LPC.AUTH.1, LPC.EXC.2, LPC.PC.9.
- **Sub-tasks** (from ROADMAP.md §2):

| Id | Title | Owner | Depends on | Radius |
| --- | --- | --- | --- | --- |
| WU-0009.1 | Initialize git and commit the bundle as the v1 baseline; tag `v1-baseline` | main session (or human owner) | — | none |
| WU-0009.2 | Environment on the workstation: `.venv`, `jax[cuda12]==0.11.2`, pins from `requirements.txt`; record devices and x64 | human owner | WU-0009.1 | none |
| WU-0009.3 | Baseline smoke reference: smoke preset on CPU at the baseline commit, kept as `runs/baseline/smoke/` and cited in the manifest | developer | WU-0009.1, WU-0009.2 | smoke |
| WU-0009.4 | Reconcile `queue.md` with this roadmap: add WU-0009 to WU-0019, sub-task columns, dependencies | planner | — | none |

- **Definition of done and acceptance criteria** (copied verbatim from ROADMAP.md §2, fixed before execution, VV.3):

| Id | Definition of done | Acceptance criteria (checkable) |
| --- | --- | --- |
| WU-0009.1 | `git log` shows one baseline commit of every tracked file; `.gitignore` honored | `git status --porcelain` is empty after the commit; the manifest's "Pilot v1" row gets a dated line naming the baseline commit hash. No file content changes. |
| WU-0009.2 | Environment recorded in the WU-0009 log | `python -c "import jax; print(jax.devices(), jax.config.jax_enable_x64)"` after `import lpcstudy.systems` prints a CUDA device and `True`; `pip freeze` matches every pin in `requirements.txt`; `nvidia-smi` output pasted. `tools/run_tests.sh unit` passes once on CPU. |
| WU-0009.3 | `runs/baseline/smoke/results.json` exists and the manifest cites it | Run on CPU with `JAX_PLATFORMS=cpu` at the baseline commit; `results.json` contains `config.seed == 20261005`; the manifest row records commit, device "cpu", Python and JAX versions. A second CPU run at the same commit is bitwise identical (`cmp` on `results.json` after removing the `seconds` fields): this fixes the CPU-determinism premise of LPC.PC.18 on this machine. If it is not identical, record DEF and stop: the WU-0001 and WU-0002 bitwise criteria then need an owner decision before execution. |
| WU-0009.4 | `queue.md` lists every unit and sub-task in this file | Every WU id in this file appears in `queue.md` with its dependencies; no existing row is edited (append a dated amendment block). |

- **Affected checks:** WU-0009.1, .2, .4: none (no code change). WU-0009.3: the smoke preset on CPU, twice, at the baseline commit (the second run is the determinism check, planned here, not a rerun). No unit-tier run is required by this unit beyond the one in WU-0009.2.
- **Owner checkpoints (LPC.PC.11):** WU-0009.2 is an owner act (environment and dependency pins, LPC.PC.17, LPC.AUTH.1). No verdict, statistics, seed or provenance code is touched. WU-0009.3 stops for an owner decision if CPU runs are not bitwise identical.
- **Split:** none beyond the four sub-tasks.

## Log

### 2026-10-10, claude-opus-5-5 (planner subagent, dispatched by the main session running claude-sonnet-5-5)

- Session model id (main session): claude-sonnet-5-5. Latest adoption ledger seq: 5 (authorization entries 4 and 6). `tools/ledger.py status` shows every governed file adopted and unchanged (entry 5).
- Facts below are as reported by the main session, except where marked "checked by planner".
- **WU-0009.1: done.** Commit `f01360d` (`f01360d606b161206bae13a59cc8f476f5ddacbd`), tag `v1-baseline`; `git status` clean after the commit.
  - Checked by planner: the tag exists and HEAD is `f01360d`. `git status --porcelain` now shows one untracked file, `docs/agent/records/network-log.jsonl`, created after the commit.
  - Open against the criterion: `docs/agent/records/results-manifest.md`'s "Pilot v1" row has no dated line naming the baseline commit hash yet. The planner may not edit the manifest; the main session appends it.
- **WU-0009.2: done.**
  - Environment: uv venv, Python 3.13.16; `jax[cuda12]==0.11.2` plus the pinned `requirements.txt`.
  - Devices: `jax.devices()` with `JAX_PLATFORMS=cuda` gives `[CudaDevice(id=0)]`, and `jax_enable_x64` is `True`.
  - GPU: NVIDIA RTX 4090, 24564 MiB, driver 615.78.08. These are summary values; the full `nvidia-smi` output was not pasted.
  - `pip freeze` matches every pin.
  - Tests: `tests/test_core.py` on CPU, run once: 14 passed in 11.44 s.
  - Deviation from the criterion text: `tools/run_tests.sh unit` cannot exist before WU-0012.1, which depends on WU-0010.1. The direct pytest run of `tests/test_core.py`, the whole suite per `.claude/rules/test-discipline.md`, stood in for it. The main session or the owner records the disposition. No tolerance or criterion is changed.
- **WU-0009.3:** in progress, by the main session.
- **WU-0009.4:** this entry.
  - Appended a dated block to `docs/agent/records/work/queue.md`. It contains the line stating that WU-0001 to WU-0008 are executed as roadmap sub-tasks, a table of units WU-0009 to WU-0019, and a dependency index of every sub-task id in ROADMAP.md §2. The index is there because the acceptance criterion asks for every WU id, which is more than ROADMAP §7 lists.
  - No existing row edited. No tests run (none in the radius).
- **WU-0014.1 satisfied** (owner act): the owner imported `docs/study/proposal_and_methods_v3.md`, with SHA-256 `6fb99e8eeaac437ba1e561e01bd88f26fc86f836173460c7f2a0f8899fabad2b`.
  - Checked by planner: `sha256sum` reproduces this digest. The file names experiments E0 to E6 and the v3 ids H1a–H1d, Q-N, H2a–H2e and H3a–H3c. This was a grep only; WU-0014.2 does the full concordance.
  - ROADMAP places this record in the WU-0014 log. No WU-0014 file exists yet, so it is recorded here, and the WU-0014 file should cite this entry.

### 2026-10-10, claude-sonnet-5-5 (main session): closing WU-0009.1 to .3

- **WU-0009.1 closed.** Manifest "Pilot v1" row now has a dated line naming `f01360d606b161206bae13a59cc8f476f5ddacbd`. `docs/agent/records/network-log.jsonl` (written by the researcher agent after the commit) is untracked and goes in the next commit.
- **WU-0009.2 closed, with a recorded deviation.** `nvidia-smi` at 15:34 local, pasted in full:

  ```
  NVIDIA-SMI 615.78.08   KMD Version: 615.78.08   CUDA UMD Version: 13.4
  GPU 0: NVIDIA GeForce RTX 4090, 00000000:01:00.0, 41C, P8, 16W / 450W, 533MiB / 24564MiB, util 32%
  Processes (graphics only): Xorg 153MiB, xfwm4 7MiB, firefox 206MiB, one other 100MiB
  ```

  An earlier call in this session had reported "Driver/library version mismatch" (NVML library 615.78); it was gone at the next check in this session (cause not investigated; the kernel string changed from 7.2.9-1 to 7.2.9-2, which suggests a kernel update and reboot). `tools/run_tests.sh unit` does not exist before WU-0012.1, so the direct run of `tests/test_core.py` (14 passed, 11.44 s, CPU, once) stood in for it. **Disposition requested from the owner**: accept the stand-in (recommended; no criterion or tolerance changes) or hold WU-0009.2 open until WU-0012.1.
- **WU-0009.3 closed: CPU determinism holds.**
  - Command (both runs): `JAX_PLATFORMS=cpu XLA_PYTHON_CLIENT_PREALLOCATE=false LPC_THREADS=4 OMP/MKL/OPENBLAS_NUM_THREADS=4 python -m lpcstudy --preset smoke --out <dir>`, commit `f01360d`, `lpcstudy/` and `tests/` unmodified (only records changed during the runs). Run 1: 50 s, to `runs/baseline/smoke`. Run 2: 64 s, to the scratchpad.
  - The preset writes into `<out>/smoke/`; the files were moved up one level by `mv` after run 1 so the reference is at `runs/baseline/smoke/results.json` as the criterion states. No file content changed.
  - `config.seed == 20261005`. After removing the 5 `seconds` fields, the two `results.json` documents are identical as parsed JSON (exact float equality, every key compared; a recursive diff printed nothing), and `cache/lyapunov.json` is byte-identical (`cmp`). This is the CPU-determinism premise of LPC.PC.18 on this machine. sha256 of the reference `results.json`: `0da48771ee967525f71518d4bb6e7aec675349ff175a2d4544234d4f8f084b79`.
  - The comparison was on parsed JSON, not a `cmp` of the files, because the `seconds` fields differ; the criterion allows removing them.
  - **Noted for WU-0002.11 (PRIME.4), not acted on here:** the smoke log shows `OptimizeWarning: Covariance of the parameters could not be estimated` (`lpcstudy/analysis.py:76`) and `RuntimeWarning: All-NaN slice encountered` (`lpcstudy/analysis.py:366`). Whether these cases are counted is for the DEF-0001 audit.
- **Open items**: WU-0009 as a whole stays open until the owner gives the WU-0009.2 disposition. The planner's reconciliation findings 1, 2, 5 and 6 (older `queue.md` dependencies conflict with the roadmap; WU-0016.4 omits WU-0016.2) are for the owner; the sub-task dependencies in the roadmap govern, as the amendment block states.

## Review

- **Reviewer:**
- **Findings and resolution:**

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:

## Referral
