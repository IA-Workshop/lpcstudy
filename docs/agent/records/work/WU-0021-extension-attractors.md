# WU-0021: Two additional attractors (S1 hyperchaotic Rössler, S2 Lorenz-63 at r = 166.1; S3 Rössler observed through z optional)

| Field | Value |
| --- | --- |
| Status | planned |
| Class | CSQ3 development (exploratory; DEV seeds only; never confirmatory) |
| Agent(s) | claude-opus-5-5 (planner); researcher, applied-mathematician, developer, reviewer and main session to be named; under DEC-0037 and the owner's pending ledger entries (ROADMAP §8) |
| Estimate | About 12 agent hours. Wall clock: GPU about 1 h for the pilot (.6) and 1 to 1.5 h for the full runs (.8); CPU smokes about 1.5 h at one thread. **Due 2026-10-22.** |

## Plan (written before execution)

- **Scope.**
  - **In:**
    - S1 `hyperrossler`: ẋ = −y − z, ẏ = x + ay + w, ż = b + xz, ẇ = −cz + dw, with (a, b, c, d) = (0.25, 3, 0.5, 0.05). The equations are confirmed in the researcher note of 2026-10-19, request 1.
    - S2 `lorenz63_r166`: the existing `lorenz63_field` with ρ = 166.1, which is 0.03 above r_c = 166.07 (Manneville & Pomeau 1980).
    - S3 `rossler_z`, optional: the registry Rössler with `observed_index = 2`.
    - The names are provisional; the WU-0021.2 specification fixes them.
    - Each system is an additive `SystemSpec` entry with its start state, `max_dt`, orbit bound and, if WU-0021.2 asks for it, a per-system Lyapunov run length. The field defaults to today's 100 000 steps, so the frozen systems do not change.
    - `report.LYAPUNOV_REFERENCES` rows for the new names. Today a missing key raises.
    - Tests, the smoke and pilot evidence, one labeled full run per system, and a development note.
  - **Out:**
    - any change to the three frozen systems, the presets `FULL`, `PILOT` and `SMOKE`, `statistics.V3_SYSTEMS`, the verdict and statistics code, seeds, provenance and `__main__.py`;
    - robustness E6 on the new systems (`--skip-robustness`);
    - Lorenz-96 and misspecified models (LPC.PC.1);
    - Rössler at c = 2.5 (it needs an interval override; not authorized);
    - merging to `main`;
    - any new hypothesis on the three studied systems.
  - **Basis:** DEC-0037 items 2 and 3; the math note 2026-10-19 §A.2 to §A.4 and §C.3; the specification note `docs/agent/notes/2026-10-20-math-extension-specs.md` (WU-0021.2). Where the specification is stricter than this plan, the specification governs.
- **Sub-tasks** (owner, effort, dependency, date):

  | Id | What | Owner | Effort | Depends on | Target |
  | --- | --- | --- | --- | --- | --- |
  | .1 | Dysts and literature values (note `2026-10-20-researcher-dysts-extension.md`), running | researcher | M | — | 10-20 AM |
  | .2 | Specification: values of the table below, the exploratory readings, the regression requirement | applied-mathematician | M | .1 | 10-20 noon |
  | .3 | Freeze-1 three-system smoke reference (below) | developer | S | — | 10-20 AM |
  | .4 | Implementation and tests | developer | M (4 h) | .2, .3 | 10-20 PM |
  | .5 | Smoke evidence: R1 regression, plumbing smoke per new system | developer | S | .4 | 10-20 PM |
  | .6 | Pilot on DEV-3, GPU, both systems, `--skip-robustness` | developer, main session | S | .5 | 10-20 evening |
  | .7 | Independent review, at most two fix rounds, then merge to `develop` | reviewer, main session | M | .5 | 10-21 |
  | .8 | Full preset per system on DEV-3, GPU, from a clean worktree at the merged commit | developer, main session | S | .6, .7 | 10-21 evening |
  | .9 | Development note: gate, pre-specified readings, stored per-system verdict words | main session, applied-mathematician | M | .8 | 10-22 |

- **Values that WU-0021.2 fixes before .4 is finished** (math note 2026-10-19 provisional value → criterion):
  - `max_dt`: S1 0.005, S2 0.002. Criterion: V6 passes, meaning that halving the step changes x by less than 10⁻³ σ_x over 1 LT.
  - Orbit bound on |x|: S1 about 60, S2 300. Rule: 1.5 × the statistics-orbit maximum, rounded up.
  - Lyapunov run length: chosen so that the batch SE is at most 1% of λ, or the reached SE is reported.
  - AMI delay: τ ≤ 5, so that 6τ ≤ 30.
  - Embedding: D = 7. For S1, D > 2 d_box holds only if d_box < 3.5 (Embedology); this is reported, not assumed.
  - Seed: DEV-3.
  - Exploratory readings: pre-specified support, counterexample and report-only items per system, as in the math note §C.3. They are copied into this file's Log before .6 starts.
- **Definition of done.**
  - S1 and S2 (and S3 if taken) are merged on `develop`.
  - R1 to R3 and A1 to A8 are met.
  - Review approved.
  - One labeled full development run per system is recorded in the manifest as exploratory.
  - The development note is committed.
  - `main` is untouched.
- **Acceptance criteria** (fixed now, VV.3; WU-0021.2 may tighten them, never loosen them):
  - **R1 Bitwise regression of the frozen pipeline** (zero tolerance).
    - Reference (.3): smoke preset, `--seed-id DEV-0 --systems lorenz63 rossler chua`, CPU, `LPC_THREADS=1`, run through `tools/run_preset.sh`. The tree is clean at develop 22483b4 or later, with `git diff --quiet freeze-1 -- lpcstudy/` true (recorded).
    - Comparison (.5): the same command at the extension tip. `tools/leafdiff.py <ref> <new>` must show 0 changed, 0 removed and 0 added leaves outside `provenance/` and the `seconds` leaves.
    - The tolerance is zero because the CPU, the thread count and the inputs are the same, and WU-0009.3 established CPU determinism on this machine.
    - If R1 fails, one planned determinism measurement follows: the reference command is rerun once at the base. If the base reproduces itself, the extension is at fault: stop and fix. Otherwise open a DEF.
    - R1 is rerun after every fix round that touches `lpcstudy/`.
  - **R2 Additivity.** `git diff --numstat freeze-1 -- lpcstudy/` shows no deleted line, except:
    - (i) the `n_steps` and `burn_in` arguments of `data.lyapunov_record`, if a per-system run length is introduced;
    - (ii) for S3 only, the `observed_index` check in `systems.checked_bound`.

    Each exception is listed in the Log and checked by the reviewer hunk by hunk.
  - **R3 Pins.** A unit test compares `SYSTEMS["lorenz63"|"rossler"|"chua"]` field by field with literals copied from `git show freeze-1:lpcstudy/systems.py`: params, dim, observed_index, initial_state, max_dt, orbit_bound, and the identity of `field_fn`. The same test checks `FULL`, `PILOT` and `SMOKE.core_systems` and `statistics.V3_SYSTEMS`. Exact equality.
  - **A1 Field.** Reference: a NumPy evaluation of the equations as quoted in the researcher's note, with the quote in the docstring, at 5 fixed states with dyadic coordinates. Tolerance: |Δ| ≤ 4 ε Σ|terms| per component, the round-off bound of a three-term sum of products (ε = 2⁻⁵²).
  - **A2 Jacobian.** `jax.jacfwd(field)` against the analytic Jacobian written by hand in the test, at the same states, with the same bound.
  - **A3 RK4 order.** `make_flow_step` on the new field from 3 attractor states, at steps h, h/2 and h/4, over a horizon with the finest self-difference above 10⁻¹¹ and the coarsest below 10⁻³. The observed order must lie in [3.8, 4.2]. The reference is Richardson self-convergence, as in WU-0005.1. Under 5 s.
  - **A4 V6 at the chosen `max_dt`.** Over 20 attractor states, max |x_h − x_{h/2}| over 1 LT is below 10⁻³ σ_x. This is the v3 §6 criterion, unchanged. It is a unit test if under 5 s, else slow.
  - **A5 Guard.** For each new spec, `guard_orbit` accepts |x| = B and refuses B(1 + 10⁻⁹) and NaN. The cached orbit maximum is below B. S3 only: a spec with `observed_index ≠ 0` and no explicit bound coordinate is still refused.
  - **A6 λ_max** (new slow test `tests/slow/test_extension_lyapunov.py`, run once).
    - The code's `lyapunov_record` value is compared with an independent Benettin/QR implementation: the applied-mathematician's script, or one written in the test without importing `lpcstudy.systems`.
    - Tolerance: |Δ| ≤ 3·√(SE_code² + SE_ref²), with the SEs from 20 batch means, stated in the docstring.
    - A Dysts or literature value is reported with its relative difference. It is asserted only if the researcher marks it confirmed with a stated precision.
  - **A7 Plumbing.** A smoke run per new system (`--systems <S>`, CPU) exits 0. `results.json` has `systems/<S>/context` (λ, τ_d, spacing, orbit maxima) and the gate keys V1 to V7. The smoke gate outcome is recorded, not required.
  - **A8 Gate and readings.**
    - Pilot (.6) and full (.8): V1 to V7 at the v3 §6 criteria.
    - A failure marks the system provisional and is reported. No setting changes after a result is seen without an owner referral (PRIME.2).
    - The readings are reported exactly as pre-specified.
    - The stored overall verdict is not quoted for a run without the three v3 systems: `overall_verdict` requires `V3_SYSTEMS`, so it cannot read "supported".
    - Header: `DEVELOPMENT (DEV-3): not a hypothesis test`.
    - Wall clock under 12 h per run.
  - **A9 Sealed hygiene.**
    - No command in the Log contains `confirmatory`.
    - `git diff --name-only freeze-1` lists nothing under `seeds/`, `runs/confirmatory/`, `docs/study/` or `docs/agent/governance/`.
- **Affected checks** (DEVELOPMENT_WORKFLOW §4.2; confirm with `python3 tools/test_impact.py --base develop --explain` and log it):
  - `systems.py` is a core module. The radius is `tests/unit/test_systems.py` plus the unit tests of every transitive dependent (in practice nearly the whole `unit` tier: this is the rule's radius, not a gate run), plus `tests/integration/`.
  - `report.py` adds its own tests and `tests/unit/test___main__.py`. `data.py`, if touched, is core and adds no further files.
  - Slow tier, once each: the new `tests/slow/test_extension_lyapunov.py`, and `tests/slow/test_start_states.py -k "<new names>"`. The latter is parametrized over `sorted(SYSTEMS)`, so it gains the new systems; it runs only for those.
  - The smokes of R1 and A7 are separate evidence from `tests/integration/test_smoke_pipeline.py`: R1 is a bitwise three-system comparison.
  - **While run-2 is active:** the unit radius and the smokes run at `LPC_THREADS=1` under `nice -n 19`. The integration tier waits until run-2 ends.
- **Owner checkpoints** (LPC.PC.11):
  - verdict or statistics code: none;
  - seed or provenance code: none;
  - dependencies: none (Dysts is not installed);
  - the DEF-0015 orbit guard: only if S3 is taken (exception R2 (ii));
  - the scope ruling and the decisions O1 to O9 of the schedule note.
- **Split.** .1 and .2 (values) can be reviewed apart from .4 and .5 (code). S3 is a separate optional lane, .4b, after S1 and S2 pass R1. It is dropped first if anything slips.
- **Open questions for the researcher:** covered by the running .1 note: the Dysts entries for S1 and S2 (and an intermittent Lorenz entry, if any), the published hyper-Rössler spectrum (the Scholarpedia snippet 0.112, 0.019, 0, −25.188 was unconfirmed), and any λ at r = 166.1.

## Log

- **2026-10-20, WU-0021.3: freeze-1 three-system smoke reference (R1), developer claude-sonnet-5-5.**
  - Test-run checklist (§4.9): no pytest run, this is a preset run. Command and device: the R1 reference command below, CPU, `LPC_THREADS=1`, `nice -n 19`, no GPU. Seed: DEV-0 through the registry. The sealed run-2 CPU regeneration (8 threads) and the GPU ensemble were active and were not touched. The run is not repeated (R1 text calls for a rerun only after a failed comparison).
  - Worktree: clean detached `/home/brianm/projects/physics/chaos/lpcstudy-wt/run/ext-ref-fc49d5f` at develop fc49d5f (later than 22483b4), `.venv` symlinked; `git status --porcelain` empty; `git diff --quiet freeze-1 -- lpcstudy/` is true (exit 0).
  - Command (from that worktree): `LPC_THREADS=1 nice -n 19 tools/run_preset.sh smoke DEV-0 runs/ext-ref --device cpu --systems lorenz63 rossler chua`. The first attempt exited 127 before any start (`/usr/bin/time` absent), so nothing ran and no `run.meta.json` was written; the second attempt is the reference.
  - Result: exit 0; provenance in the run log: seed id DEV-0, commit fc49d5f101dd4e697c4ee4de59317623b8376f58, dirty False. Wall time 87 s (study 83 s; `run.meta.json` wall_seconds 86). Start 2026-10-20T09:45:30Z.
  - Reference path: `/home/brianm/projects/physics/chaos/lpcstudy-wt/run/ext-ref-fc49d5f/runs/ext-ref/smoke/` (not committed).
  - sha256 of `results.json`: `07d75aad92835990a62cf16b11c65642a9f25ddaf57da1a1dfa0f6bbde821d46`.
  - Handling counters printed by the run (for example `zero_variance_corr_cp` in chua, 9 nonzero counters in 10 blocks) are the frozen pipeline's own reports and are part of the reference.
  - Next: .5 compares the extension tip with `tools/leafdiff.py <ref> <new>`.
  - Status of .4: not started. The specification note `docs/agent/notes/2026-10-20-math-extension-specs.md` did not exist at this time (the applied-mathematician's scripts directory `2026-10-20-math-extension-specs/` on `wu/ext-math` holds work in progress only).
- **2026-10-20, WU-0021.4 (implementation), developer claude-sonnet-5-5, branch `wu/ext-impl` from develop 2b8240e.**
  - Authority: the specification note `2026-10-20-math-extension-specs.md` (section 0 fixes the values) and the main session's rulings on its section 7: R1 `lyapunov_steps` 4e6 for S2 with its SE reported beside every Lyapunov-time statement; R2 S3 promoted to a full member (all three systems implemented); R3 S3 as the permuted-state spec, so no change to `checked_bound` and the plan's exception R2 (ii) lapses; R4 bounds S1 300, S2 185, S3 50; R5 the registry-pinning tests change by design; R11 the `LYAPUNOV_REFERENCES` rows. Names: `rossler_hyper`, `lorenz63_r166`, `rossler_z`. Where the specification differs from this plan's provisional values it governs: S1 `max_dt` is 0.01 (plan: 0.005; V6 measured 1.1e-6 at 0.01), S1 bound 300 (plan: about 60, which the guard refused), S2 bound 185 (plan: 300).
  - Code change (additive): `systems.py`: `rossler_hyper_field`, `rossler_zfirst_field`, three registry entries, field `lyapunov_steps: int = 100_000` on `SystemSpec`; `data.py`: `n_steps=spec.lyapunov_steps` in `lyapunov_record` (the only deleted line, exception R2 (i): `n_steps=100_000`); `report.py`: three keys in `LYAPUNOV_REFERENCES` (S1 0.1121 with 3%, Ramasubramanian and Sriram 1999 Table 1; S2 and S3 empty). `config.py`, `statistics.py`, `checked_bound`, presets, seeds, provenance and `__main__.py` untouched.
  - Registry-pinning tests changed by design (R5; no tolerance changed, no frozen-entry check dropped; the frozen three are now pinned by literal equality in the new `tests/unit/test_extension_systems.py`):
    - `tests/unit/test_systems.py::test_registry_holds_exactly_the_three_v3_systems`: old `assert set(SYSTEMS) == {"lorenz63", "rossler", "chua"}`; new `frozen <= set(SYSTEMS)` and `set(SYSTEMS) - frozen == {"rossler_hyper", "lorenz63_r166", "rossler_z"}` (the `lorenz96_field` check kept).
    - `tests/unit/test_systems.py::test_registry_bounds_are_the_ratified_ones`: old `{name: spec.orbit_bound for name, spec in SYSTEMS.items()} == {lorenz63: 40, rossler: 25, chua: 3}`; new: the same dict restricted to the three frozen names (exact), and the extension names equal `{rossler_hyper: 300, lorenz63_r166: 185, rossler_z: 50}`.
    - `tests/unit/test_experiments.py::test_no_configured_preset_changes_its_robustness_dimensions_def_0025` (D3): old `set(SYSTEMS) == {"lorenz63", "rossler", "chua"}` and `spec.dim == 3` for every spec; new `set(SYSTEMS) == frozen | {extension}`, `spec.dim == 3` for the frozen three and `{rossler_hyper: 4, lorenz63_r166: 3, rossler_z: 3}` for the extension; the expected `robustness_dimensions` result is unchanged (`[]` smoke, `[5, 10]` pilot and full, skipped `[]`, for every spec, because 5 > 4).
  - New tests: `tests/unit/test_extension_systems.py` (R3 pins, A1, A2, A3, A4, A5 and the S2 analytic trapping bound, with independent references and tolerances justified in the docstrings); `tests/slow/test_extension_lyapunov.py` (A6) separately.
  - A3 scan, before the test was fixed (exploratory, scratchpad script, 3 states 150 steps apart after a 3 000-step burn-in; horizon T in Lyapunov times; n = substeps of the coarsest run; observed order per state): S1 T=0.5 n=160: 4.09, 4.10, 4.01; n=320: 4.05, 4.05, 4.00; T=1 n=320: 4.06, 4.01, 3.95. S2 T=0.5 n=320: 4.94, 4.18, 3.86 (out of range); n=640: 4.11, 4.10, 3.93; n=1280: 4.06, 4.05, 3.97; T=0.25 n=320: 3.67, 4.52, 4.06; n=640: 3.86, 4.36, 4.03; n=1280: 3.94, 4.19, 4.02. S3 T=0.5 n=80: 3.89, 4.00, 3.98; n=160: 3.95, 4.00, 3.99; T=1 n=320: 3.93, 3.90, 3.91. The test uses T=0.5 LT with n = 320 (S1), 640 (S2), 160 (S3). The acceptance interval [3.8, 4.2] and the premise window (finest self-difference above 1e-11, coarsest below 1e-3) are the plan's and were not changed. For S2 the test steps (0.0013) are finer than production (0.002): at production resolution the observed orders are 4.2 to 4.9 on some states, the asymptotic-late behaviour that the specification note section 2 reports (4.4 to 4.8); this is reported, not a defect.
  - **Test-run checklist (§4.9), run U1** (unit tier radius, chunk 1 of 4: the three files that change by design and the new file):
    1. Change set: `lpcstudy/{systems,data,report}.py`, `tests/unit/{test_systems,test_experiments,test_extension_systems}.py`, this file.
    2. Radius: `python3 tools/test_impact.py --base develop --explain` gives the unit tier of 26 files (rule: `systems.py` and `data.py` are core modules, `report.py` a pipeline module) plus `tests/integration`; smaller than the whole suite, no gate. The 26 files run in four calls (the unit wrapper limit is 300 s per call and the host is shared); chunk 1 is `test_extension_systems.py`, `test_systems.py`, `test_experiments.py`. Integration waits until run-2 ends (plan, "While run-2 is active").
    3. Already run: no (first run of this code).
    4. Device: CPU (`JAX_PLATFORMS=cpu` set by `tools/run_tests.sh`).
    5. Threads and time: `LPC_THREADS=1`, `nice -n 19`; unit limit 300 s per call.
    6. Contention: run-2 (CPU) and the GPU ensemble are active; no GPU, no preset, no slow test started here.
    7. Output: `-q --tb=short -rfE` (wrapper).
    8. Command: `LPC_THREADS=1 nice -n 19 tools/run_tests.sh unit tests/unit/test_extension_systems.py tests/unit/test_systems.py tests/unit/test_experiments.py`.
  - U1 result: `56 passed in 9.39s`. Mutation check (not a radius run; one direct `pytest -x` call on the new file with `w' = -c z - d w` temporarily patched into `systems.py`, then restored byte for byte): A1 failed as it must (`1 failed, 4 passed`), so the tests can fail.
  - Chunks U2 to U4 (same answers to checklist items 3 to 8; item 3: not yet run on this code): U2 `test___main__ test_allocation test_analysis test_budget test_clip_sensitivity test_data test_dump test_dynamics`; U3 `test_embedding test_ensemble test_estimation test_identifiers test_oracle test_pipeline test_provenance`; U4 `test_report test_rng_hygiene test_statistics test_tools_findings_build test_tools_lm_doubling test_tools_rehearsal_diagnostics test_tools_rehearsal_report test_tools_test_impact test_validation`. Command per chunk: `LPC_THREADS=1 nice -n 19 tools/run_tests.sh unit <files>`.
  - U2 `311 passed in 31.02s`; U3 `181 passed in 11.23s`; U4 `604 passed in 19.12s`; U1 `56 passed in 9.39s`. Unit radius (26 files, 1 152 tests) green. After U1 a test of the `report.LYAPUNOV_REFERENCES` rows was added to `tests/unit/test_extension_systems.py` (test change only); that one file was rerun once: `19 passed in 3.09s`. The integration tier of the radius (`tests/integration`) is deferred until run-2 ends (plan), see the entry of .5.
  - **Checklist, run S1 (slow, `tests/slow/test_extension_lyapunov.py`, once):** 1. change set as above plus the new slow test. 2. Radius: the new file only (plan A6; owner of the statistic). 3. Not run before. 4. CPU. 5. `LPC_THREADS=1`, `nice -n 19`, slow limit 3600 s; planned runtime: about 3.5 x `lyapunov_steps` Benettin steps per system (cached run, independent reference, 20 batch runs of the code); the specification note timed the cached run alone at 7 s (S1), 23 s (S2), 6 s (S3) unloaded, so the planned total is 10 to 20 minutes on one thread with the host loaded. 6. Contention: run-2 CPU (8 threads) and the GPU ensemble active; one niced CPU thread only; no preset started in parallel. 7. `-q --tb=short -rfE` (wrapper). 8. `LPC_THREADS=1 nice -n 19 tools/run_tests.sh slow --background tests/slow/test_extension_lyapunov.py`.
  - S1 result: `3 passed in 91.89s`. Output (one line per system; SE from the 20 code batches): S1 cached 0.11251662457254273 (not bitwise the note's ...265: relative difference 7e-17, inside the 1e-12 cross-host rule), reference 0.111942 +- 0.000530, tolerance 2.39e-3, |diff| 5.7e-4, relative SE 0.53%, published 0.1121 relative difference +0.37%; S2 cached 0.6217010154674514 (bitwise as specified), reference 0.615625 +- 0.003225, tolerance 2.25e-2, |diff| 6.1e-3, relative SE 1.09%; S3 cached 0.07133265490530956 (bitwise), reference 0.071550 +- 0.000161, tolerance 6.10e-4, |diff| 2.2e-4, relative SE 0.17%, -0.84% against the registry Rossler 0.07193978510879935. Orbit maxima (code, reference, bound): S1 166.4, 167.1, 300; S2 62.4, 62.4, 185; S3 22.85, 22.85, 50. Wall time 92 s on one niced thread (planned 10 to 20 minutes: the cost was lower).
  - **R1 (regression of the frozen pipeline), .5:** the reference command run at the extension tip `4949843` (clean tree, provenance `dirty False`) in `/home/brianm/projects/physics/chaos/lpcstudy-wt/wu/ext-impl/runs/ext-new/smoke/` (exit 0, wall 89 s, `LPC_THREADS=1`, `nice -n 19`, DEV-0, `--systems lorenz63 rossler chua`, CPU, through `tools/run_preset.sh`). `python3 -I tools/leafdiff.py <ref results.json> <new results.json>`: `leaves: A 14174, B 14174, common 14174, different 0, removed 0, added 0` (exit 0). `python3 -I tools/compare_runs.py <ref dir> <new dir>`: tier T0, `leaves: REF 13914, NEW 13914, equal 13914, different 0, one-sided 0`, `RESULT: PASS (exit 0)`. **R1 met, zero tolerance** (sha256 of the two `results.json` differ only through the excluded provenance and `seconds` leaves: new `fa619a25...097ad`, reference `07d75aad...21d46`). R2 (additivity): `git diff --numstat freeze-1 -- lpcstudy/` is `1 1 data.py`, `15 0 report.py`, `108 0 systems.py`; the one deleted line is `n_steps=100_000` (exception (i)), listed for the reviewer.
  - **A7 plumbing smoke (CPU, 1 thread, niced, `tools/run_preset.sh smoke DEV-0 runs/ext-<S> --device cpu --systems <S>`): FAILED for all three systems, exit 1 after 33 s (S1), 36 s (S2), 26 s (S3), with `ValueError: system(s) ['<S>'] are not in required ['lorenz63', 'rossler', 'chua']` raised by `statistics.overall_verdict`, called from `report.verdicts` (`report.py` line 265, `__main__.py` line 571). The run writes `results.json` with `systems/<S>/context` (lambda, tau_d, spacing, orbit maxima) and the gate results (`validation`, `V7`) before this line, but nothing after it: no handling block, no verdicts, no estimators, no provenance finish, no RESULTS.md, no figures.** The specification note section 5 and the plan A8 assumed that `overall_verdict` returns "inconclusive"; the code raises for a system outside `V3_SYSTEMS` (DEC-0016: a non-v3 label must not decide "not supported"). A7 requires exit 0, so the extension cannot be run end to end without a change in `report.verdicts`, which the plan lists as out of scope. See the Referral.
  - Probe (not evidence, not committed): a throwaway worktree `/home/brianm/projects/physics/chaos/lpcstudy-wt/run/ext-probe-4949843` with a five-line patch of `report.verdicts` (call `overall_verdict` only when the systems are a subset of `V3_SYSTEMS`, else store "inconclusive" and no missing systems) ran `--systems rossler_z` to completion: exit 0, 25 s, `RESULTS.md`, figures and handling written. The probe shows that the rest of the pipeline accepts a new system once this line is passed.
  - **Checklist, runs S2a to S2c (slow, `tests/slow/test_start_states.py -k <system>`, one call per new system, once each):** 1. change set: committed tip c20f753, tree clean. 2. Radius: the plan names this file for the new names only; the parametrization is over `sorted(SYSTEMS)`, so it gains the three new systems (3 cases each: S-D1, stress arm, S-D2). 3. Not run before on these systems. 4. CPU. 5. `LPC_THREADS=1`, `nice -n 19`, slow limit 3600 s per call; planned runtime: per system the statistics orbit (203 000 steps), the cached exponent (7 s, 23 s, 6 s) and two vmapped scans of 400 starts (`burn + 705 000` steps with 30, 27 and 12 substeps), estimated 10 to 40 minutes each on one thread (S3 first, to calibrate; S1 the longest). 6. Contention: run-2 CPU and the GPU ensemble active; nothing else of mine runs. 7. `-q --tb=short -rfE`. 8. `LPC_THREADS=1 nice -n 19 tools/run_tests.sh slow --background tests/slow/test_start_states.py -k <system>`.
  - Start-state slow tests (`tests/slow/test_start_states.py`, three cases per system, one call each): S3 `3 passed in 12.14s`; S2 `3 passed in 33.56s` (KS D after burn-in 0.0559 against D_crit 0.0976; 0 refusals of 400 starts over 708 000 steps; max |x| 59.4 against 185; stress arm 0 refusals, max 55.0); S1 first call `3 errors in 5.01s`: a harness defect, not a result: the negative-control row of the `run` fixture is `[[2.0 * bound, 0.0, 0.0]]`, three coordinates, and fails to stack with the 4-coordinate states of S1 (`ValueError`, in the fixture before any start was run). Fix in `tests/slow/test_start_states.py` (a changed test line, recorded here; no tolerance changed; identical control row for dim 3): the control row now has `orbit.shape[1] - 1` zeros after `2 B` and the trailing `[:, : orbit.shape[1]]` slice is dropped as redundant. The S1 cases are rerun once after this code change (checklist answers as for S2a to S2c).
  - **S1 start-state rerun (after the fixture fix): `1 failed, 2 passed in 35.64s`. S-D1 FAILED: 10 of 400 starts refused over `burn + 705 000` steps (the full-preset main length) for `rossler_hyper`, against the pre-specified 0 refusals (the specification note section 1.1 called a false refusal "improbable" over a full-preset trajectory).** Stress arm (eta = 1e-3, burn-in only): 0 refusals, max |x| 153.6; S-D2: KS D 0.0378 against D_crit 0.0976 (pass). Diagnosis (scratch script `.../scratchpad/s1diag.py`, same seeds and code path, 1 thread, one run, not part of the evidence set): 7 of the 400 starts become non-finite (first failing 1 000-step chunk at steps 45 000, 86 000, 132 000, 150 000, 283 000, 537 000, 587 000; starts 137, 99, 249, 342, 339, 119, 188), so these orbits escape to infinity (the term `z' = b + x z` grows exponentially when x and z are positive and large: S1 has no global trapping region), and the survivors include starts whose |x| reaches 300.79 (> 300), whose largest coordinate reaches 1 116.6, so the other 3 refusals are bound exceedances on the way to an escape or large excursions. The escape rate is about 7 / (400 x 7.05e5 steps) = 2.5e-8 per step per orbit, i.e. about 0.8% per pilot-length main trajectory and about 1.7% per full-length one for each of the main and estimator trajectories, and the refusal stops the whole run (DEF-0015). No setting was changed; the test is left as written and red for S1; this is a finding for the Referral, not a defect of the test.

## Review

- **Reviewer:**
- **Findings and resolution:**

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:

## Referral

- **2026-10-20, developer claude-sonnet-5-5 (LPC.AI.12, LPC.AI.13): the extension systems cannot complete a run without a change to verdict-reporting code.**
  - **What was attempted:** the A7 plumbing smoke of each new system, `--systems <S>`, exactly as in the Log.
  - **Why it stops:** `report.verdicts` calls `statistics.overall_verdict(found)` for each hypothesis row with every system of the run in `found`, and `overall_verdict` raises `ValueError` for a system outside `V3_SYSTEMS` (its docstring: "a non-v3 label must not decide 'not supported'"). So any run of S1, S2 or S3 ends with exit 1 after the per-system results and before the handling counts, verdicts, estimator log, provenance finish, RESULTS.md and figures. A7 (exit 0, gate keys) and the pilot (.6) and full runs (.8) need these. The plan puts "the verdict and statistics code" and `__main__.py` out of scope, and lists no owner checkpoint for it; the specification note section 5 expected "inconclusive", which is not what the code does.
  - **Smallest change, for a decision (not made):** in `report.verdicts`, call `overall_verdict` only when `set(found) <= set(V3_SYSTEMS)`; otherwise store the per-system verdicts (`by_system`) with `missing_systems` `[]` and a verdict word that cannot be read as an overall result. `statistics.overall_verdict` and its tests stay unchanged; the three frozen systems take the same branch as today, so R1 is unaffected (to be confirmed by rerunning R1 after the change). A new unit test would pin both branches (a v3 subset gives the same result as now; an extension system gives per-system verdicts only, never "supported" or "not supported"). Needs an owner ruling on the verdict word, because `report.py` verdicts feed `tools/compare_pilot.py` (`verdicts/**`) and RESULTS.md (line 1443 reads `missing_systems`).
  - **Options:** (a) the change above, as a reviewed addition in WU-0021 with an owner checkpoint (verdict-reporting code, not the statistic); (b) a separate unit for it, with WU-0021 stopped at .4; (c) no change: run the extension only to the per-system results (`results.json` before the crash) and read the per-system keys, with no RESULTS.md or handling summary: not recommended, because the handling counters (clips, replacements) would go unreported (PRIME.4). **Recommendation: (a).**
  - **Second finding (S1 only), same entry: S-D1 fails for `rossler_hyper`** (10 of 400 full-length starts refused, 7 of them non-finite escapes; see the Log). Consequence: a pilot or full run of S1 has about a 2% to 5% chance per seed of an orbit refusal that aborts the run (main and estimator trajectories, each 3.1e5 steps at the pilot and 7e5 at the full preset; the statistics orbit and the Benettin orbit are single orbits from the fixed start and passed). Raising the bound does not help (non-finite escapes). Options for the owner and the applied-mathematician: (a) keep S1 and accept the hazard, reporting a refusal as a result, with a re-draw of the seed id only by an owner decision (the plan has no such rule); (b) change the S1 parameters or the start-draw perturbation (a new specification, new V6 and spectrum checks; the equations are the researcher-confirmed ones); (c) drop S1 and keep S2 and S3 (both pass S-D1: S2 0 of 400 refused; S3 0 of 400). No recommendation without the applied-mathematician; the pre-specified S-D1 criterion is not loosened.
  - **Still done and committed:** the additive systems, `lyapunov_steps`, the reference rows, tests A1 to A5, R3, R11, A6, R1 (met). **Not done:** the A7 smoke (blocked) and, pending the ruling, the integration tier.
