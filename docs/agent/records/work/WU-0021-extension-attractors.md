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

## Review

- **Reviewer:**
- **Findings and resolution:**

## Audit

- Is the definition of done met? Give the evidence.
- Defects recorded:
- Notes for successors:

## Referral
