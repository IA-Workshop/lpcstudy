# WU-0004c: independent review (round 1)

## Review

- **Reviewer:** `reviewer`, claude-opus-5-5, 2026-10-18, fresh context. Companion to `WU-0004c-gpu-test.md`.
- **Scope:** `git diff 7b6f6e6..2b53553` (f32fcbb, bd8e168, 0c4a205, 2b53553). The changed files are `tests/gpu/test_reproducibility.py`, the unit file and one `queue.md` row. They are judged against:
  - owner ruling B10 (amendments note section 35);
  - the draft decision `docs/agent/notes/2026-10-18-owner-decision-drafts.md` section 1;
  - the unit's plan and acceptance criteria 1 to 8.
- **Tests:** none run, as instructed. The developer's single run stands: `1 passed in 414.83s (0:06:54)`, from `runs/tests/gpu-20261018T103516Z.log`, exit file `0`. The measured line in that log matches the Log entry word for word.
- **Read-only checks I made (CPU, stdlib, `python3 -I`, no GPU).**
  - The pytest temporary directory of that run is still on disk at `/tmp/pytest-of-brianm/pytest-1413/test_smoke_twice_on_gpu_is_bit0/`. I checked its two results files directly; see check 1.
  - The leaf counts of the files the Log cites; see check 5.

## Checks

1. **Can the test pass vacuously?** No.
   - **Separate processes and outputs.** The two runs are separate `subprocess.run` children with different `--out` directories (`tmp_path/run1` and `tmp_path/run2`). The `tmp_path` is new for each test.
   - **No shared cache.** The only on-disk cache in `lpcstudy/` is `out_dir/cache/lyapunov.json` (`pipeline.py:125`, `data.py:328`), so each run has its own. The retained directories show two separately written `cache/lyapunov.json` files, at 06:36 and 06:40. Nothing else in `lpcstudy/` reads a file outside the output directory, apart from the seed registry and ledger.
   - **No reuse of output.** The test reads `out_dir/smoke/results.json` only after the child exits 0. `__main__` writes the final file after `provenance.finish`, and both retained files carry `complete: true`.
   - **No CPU fallback.** The children run with `JAX_PLATFORMS=cuda`. `provenance.device.backend` comes from `jax.default_backend()` and is asserted to be in {gpu, cuda, rocm}. Retained provenance: backend `gpu`, RTX 4090, count 1, env `JAX_PLATFORMS=cuda`, commit bd8e168, `dirty` false in both runs.
   - **My own diff of the two retained files** (a separate walker, IEEE bytes): 11 differing leaves, all of them timing or provenance:
     - `seconds` at the top level, under `systems/lorenz63` and under `estimators/*`;
     - in `provenance`: `wall_seconds`, `start_utc`, `end_utc`, `argv`, `peak_rss_bytes` and `device_peak_bytes`.

     No result leaf differs.
   - **Degeneracy floor.** Both trees have 4,695 leaves and 3,166 floats by the test's walk.
   - Only one point stays open: R4, the compile cache, which is hardening.
2. **Tolerance.** Bitwise is item 1 of the draft decision, and the exclusions are the same: `seconds` keys and the top-level `provenance`.
   - The docstring names the pair as its own reference, explains why, and asserts nothing between the GPU and the CPU (scope out is respected).
   - `compare_runs.compare_trees` is used correctly. On a GPU T0 pair the tool treats a float difference as "measured" rather than a failure (`compare_runs.py:1099-1103`). The test asserts `not cmp.rows`, so that cannot let a difference pass.
   - The docstring could say more plainly that bitwise reproducibility is empirical rather than guaranteed: see R3.
3. **Exclusions.**
   - Every `seconds` key in the code is timing: `__main__.py:231`, `experiments.py:682` and `pipeline.py:171`. The retained diff confirms that no result leaf is called `seconds`.
   - Provenance is compared separately, on nine settings keys. Some settings relevant to numerics are left out: see R5.
4. **Skip logic and tier.**
   - `tests/gpu/` gives the `gpu` marker from the directory (`conftest.tier_of`).
   - The bounds are within the 1,800 s tier timeout: 120 s for the probe plus 780 s for each run, 1,680 s in total, against 415 s measured.
   - The probe exits 3 on any `RuntimeError` from `jax.devices('gpu')`. Any other failure, including a jax `ImportError`, exits non-zero and the test fails.
   - However, a CUDA backend that is present but fails to initialize also raises `RuntimeError`, so it skips. Under the wrapper's `-rfE` the reason is not printed and the exit code is 0: see R1.
   - The lock is not enforced if the file is run outside the wrapper: see R6.
5. **The Log.**
   - The correction of the earlier hand-back is honest. Commit 0c4a205 added only the `queue.md` row despite its subject line, and 2b53553 appends the result. The test file has not changed since f32fcbb, and the run was at bd8e168 with `dirty` false, so "no code changed after it" holds. All commits only add lines; the history is linear from 7b6f6e6.
   - The main explanation of the leaf count is right:
     - `SMOKE.core_systems = ("lorenz63",)` (`config.py:208`);
     - the R0 file was run with `--systems lorenz63 rossler chua` on DEV-1, and has 13,791 leaves and 9,432 floats;
     - the 7b and 7c smokes were one system on DEV-0, with 4,689 leaves.
   - The subsidiary figures are not right (R2): each R0 system block has 4,509, 4,503 or 4,521 leaves, not "about 4,400". The sum is 13,533, plus 258 at the top level, not "about 13.2 thousand plus the top-level blocks".
   - The GPU-hours figure is right. The children ran 237.8 s and 172.6 s by provenance (239 s and 174 s by the test's clock), and the whole test took 414.83 s, so 0.115 GPU-hours either way. It has no destination yet (R7).
6. **Governance.**
   - The seed is DEV-0 only, and `seed_kind` `development` is asserted. The confirmatory flag is not used and the CONF seed is not touched; no file under `seeds/` or the ledger changed.
   - Randomness: none.
   - Commit messages: all four name WU-0004c and end with `Co-Authored-By` and `Agent: claude-sonnet-5-5`.
   - No history was rewritten, nothing was merged, and nothing changed outside the plan's scope.

## Findings

**R1 (medium; criterion 6, PRIME.4). A broken CUDA backend skips with exit 0, and the skip reason is not printed.**
- **Evidence.**
  - `test_reproducibility.py:34-41,138-149`: the probe sets `JAX_PLATFORMS=cuda,cpu` and turns any `RuntimeError` from `jax.devices('gpu')` into exit 3, which skips. This covers two different cases:
    - "no CUDA plugin or no device";
    - "CUDA plugin installed but initialization failed" (driver or library mismatch, a device that is not visible).

    The developer's own check of the skip path used `CUDA_VISIBLE_DEVICES=-1`, which is the second case.
  - `tools/run_tests.sh:130` runs pytest with `-rfE`, so a skip's reason is not reported, and pytest exits 0 when every test is skipped.
- **Why it matters.** On the GPU workstation, the one host where the `gpu` tier is meant to run (including at the freeze gate), a CUDA breakage would show up as `1 skipped` with exit 0 and no reason. Criterion 6 says that a broken jax or probe fails; only a missing GPU skips.
- **Fix.**
  - Skip only when no CUDA backend is present. For example: skip when `jax.devices()` under default platforms reports no GPU and no CUDA plugin is importable. Fail when a CUDA plugin is installed but the backend raises on initialization. An equivalent split on the error is also acceptable.
  - Print the skip reason with `capsys.disabled()` (or to stderr) so that it reaches the log under `-rfE`.
  - Re-check the two probe paths offline (exit 3 with no plugin; failure with `CUDA_VISIBLE_DEVICES=-1`) and log them.

**R2 (low; criterion 4 justification, Log accuracy). The threshold comment is wrong for what the test runs, and the Log's subsidiary figures are off.**
- **Evidence.**
  - `test_reproducibility.py:29`: `MIN_LEAVES = 1000  # the measured smoke has about 13.8 thousand leaves`. The preset the test runs gives 4,695 leaves and 3,166 floats; 13,791 is the three-system DEV-1 R0 file.
  - Log, line 50: "about 4,400" leaves per system and "about 13.2 thousand"; measured, 4,503 to 4,521 and 13,533 (see check 5).
- **Fix.**
  - Correct the comment: 4,695 leaves and 3,166 floats, for the one-system default smoke at bd8e168.
  - Append a correction line to the Log; do not edit the existing line.

**R3 (low; PRIME.2 honesty of the justification). The docstring should state that bitwise GPU reproducibility is a measured property, not a guarantee.**
- **Evidence.** The docstring (`:176-186`) cites the measured R1 against R2 fact. It does not say:
  - that the property holds for this card, driver and jaxlib (0.11.2);
  - that it holds without `--xla_gpu_deterministic_ops`, which is still an open item (O3; the draft says so in "Not decided here");
  - that a failure after a driver, jaxlib or host change is a finding about that change.

  It also cites the tolerance as a draft decision. B10 says the test comes "after the WU-0003.6 decision", and the ruling has not yet been entered.
- **Fix.**
  - Add one or two sentences stating this scope.
  - Replace the draft citation with the DEC id once the owner enters it. The Log should record that this test asserts a ruled but not yet entered tolerance.

**R4 (low; hardening of "two independent runs"). The persistent compilation cache is not pinned off.**
- **Evidence.**
  - `gpu_environment()` (`:133-135`) passes all of `os.environ` to the children.
  - If `JAX_COMPILATION_CACHE_DIR` is set in the environment, run 2 loads run 1's compiled executables, including the XLA GPU autotuning choices. That would hide one known source of nondeterminism between processes.
  - In the venv's jax the default `jax_compilation_cache_dir` is None, so the measured run probably used no cache. This cannot be confirmed: `provenance.ENV_NAMES` does not record the variable.
  - Run 2 was 65 s faster than run 1 (172.6 s against 237.8 s), and the Log does not explain it.
- **Fix.**
  - In `gpu_environment()`, remove `JAX_COMPILATION_CACHE_DIR` and set `JAX_ENABLE_COMPILATION_CACHE=false`, or assert that they are absent and say so in the docstring.
  - Record the reason for the speed difference if known; otherwise state that it is unexplained.

**R5 (low; criterion 3 "identical settings"). The settings comparison omits numerics-relevant provenance keys.**
- **Evidence.** `SAME_SETTINGS` (`:32`) leaves out `jax_x64`, `jax_matmul_precision` and `python`. Host identity (`platform`, `cpu`) is covered only indirectly, through `compare_runs`' T0 selection. Both retained runs have `jax_x64` true and `jax_matmul_precision` null, so the passed run is unaffected.
- **Fix.**
  - Add `jax_x64`, `jax_matmul_precision` and `python` to `SAME_SETTINGS`.
  - Assert `jax_x64 is True` (the float64 convention).

**R6 (low; LPC.AUTH.3, one GPU job under the lock). The test does not check that it runs under the wrapper's lock.**
- **Evidence.**
  - The docstring (`:3-5`) says to run the test only through `tools/run_tests.sh gpu`, but nothing enforces this.
  - `gpu_environment()` forces `JAX_PLATFORMS=cuda` whatever the parent environment is. A direct pytest call on this file, or a future gate that calls pytest over the whole tests directory, would therefore start two GPU jobs (about 7 minutes) without the lock.
- **Fix.** Fail fast unless the wrapper's GPU context is present. A cheap marker is to require `JAX_PLATFORMS == "cuda,cpu"` in the parent, which only the `gpu` tier of the wrapper sets. Anything stronger, such as a wrapper-exported marker, needs a change to `tools/` and is a separate unit.

**R7 (low; LPC.AUTH.3 tally). The 0.115 GPU-hours have no destination.**
- **Evidence.** Log line 51 says "to add to the LPC.AUTH.3 weekly tally by hand", but names no owner and no record. `tools/gpu_hours.py` reads only `run.meta.json`, so every `gpu`-tier run is outside the tally, including those at future gates.
- **Fix.**
  - Name in the Log who records the hours and where, for example a note to the main session or owner in `queue.md`.
  - Raise the tier-wide gap as a referral or note. It is not a code change in this unit.

## Owner checkpoint

**Needs owner review before freeze.** The test changes no verdict, statistics, seed or provenance code and no dependency. It does encode the declared reproducibility tolerance, which the draft decision marks for owner review before freeze, and it will serve as the freeze gate's `gpu` tier check. The ROADMAP WU-0003.4 row edit belongs to the owner (B10).

## Verdict

**Approve with fixes.** 7 findings: 1 medium (R1) and 6 low (R2 to R7). The single run is sound evidence:
- two independent GPU processes;
- separate outputs and caches;
- backend `gpu` asserted;
- 4,695 leaves bitwise equal;
- only timing and provenance differ, confirmed independently from the retained files.

R1, R4, R5 and R6 change the test file. After those fixes the passing run no longer covers the file as committed, so one rerun under the lock is warranted, as a code change (4.4). R2's comment, R3 and R7 are text only.

## Developer answers (fix round 1, claude-sonnet-5-5, 2026-10-18)

- **R1:** fixed in da88bf6. Skip only without a CUDA plugin, or with `CUDA_ERROR_NO_DEVICE` from the driver; a present but broken CUDA backend fails; the skip reason is printed with capture disabled. Offline: `CUDA_VISIBLE_DEVICES=-1` skip, `XLA_PYTHON_CLIENT_ALLOCATOR=bogus` fail, no plugin skip (detail and the jaxlib-wording caveat in the unit Log). Not exercised through pytest (that would be a rerun).
- **R2:** fixed in da88bf6 (comment) and the correction line in the unit Log (commit c82fa16).
- **R3:** fixed in da88bf6 (docstring scope; the draft is cited until the DEC id exists, as the Log says).
- **R4:** fixed in da88bf6 (`JAX_ENABLE_COMPILATION_CACHE=false`, no `JAX_COMPILATION_CACHE_DIR`). The speed difference is not explained: it reversed sign in the rerun (run 2 slower by 32 s), so it is neither a compile cache nor a systematic warm-up (unit Log).
- **R4 (owner instruction, 2026-10-18; append-only note).** Timing differences below 2x are immaterial (owner, 2026-10-18); no cause is sought or claimed. The R4 line above is restored as first written; commit 1cc1c38 had replaced it in place.
- **R5:** fixed in da88bf6 (`python`, `jax_x64`, `jax_matmul_precision` compared; `jax_x64 is True` asserted).
- **R6:** fixed in da88bf6 (fails unless the parent has `JAX_PLATFORMS=cuda,cpu`).
- **R7:** fixed in c82fa16 and the next commit: queue.md note, the main session records the hours (0.238 h in total for the unit), tier-wide gap for the owner.
- Rerun: `1 passed in 443.39s (0:07:23)`, 4695 leaves, 0 different, tier T0 (unit Log).
