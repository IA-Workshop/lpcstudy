# Chua V1 on DEV-7 and DEV-8: diagnosis

**DEVELOPMENT (DEV-5 to DEV-9): exploratory diagnosis. No reading, result or code changes.** Main session (claude-opus-5-5), 2026-10-27. Owner direction "Proceed with 2 and 3 as recommended".

- **Code:** the `phasej-freeze` worktree (`lpcstudy-wt/run/phj-freeze`, clean). Contexts are built through `build_context`, as production does.
- **Scripts:** session scratchpad (`v1_chua_diag.py`, `v1_rate.py`). They read the frozen code and change nothing.
- **Departure from the plan stated to the owner:** I said it would be a CPU job with no GPU. It needed the GPU, because CPU and GPU produce different Chua orbits from the same seed (finding 3). Three short GPU jobs ran under the lock (about 15 min in total).

## Findings

1. **Both failures are finite-difference artifacts, not Jacobian errors.**
   - **What V1 compares.** The automatic-differentiation Jacobian of the delay map against a central difference with step h = 1e-6 × scale.
   - **The failing states.** On the GPU contexts that reproduce the production values bitwise (DEV-8 7.756810517601765e-4; DEV-7 7.05288265138793e-4), the failing state of each seed shows the same signature:

     | step h (× scale) | DEV-8 state 4: central / forward / backward | DEV-7 state 1: central / forward / backward |
     |---|---|---|
     | 1e-5 | 3.0e-3 / 5.9e-3 / 1.7e-10 | 1.6e-3 / 3.2e-3 / 3.6e-10 |
     | 1e-6 (V1) | 7.8e-4 / 1.6e-3 / 1.8e-9 | 7.1e-4 / 1.4e-3 / 3.1e-9 |
     | 1e-7 | 1.4e-8 / 2.5e-8 / 1.4e-8 | 5.5e-9 / 3.9e-8 / 3.3e-8 |

   - **Why that means a kink.** At h = 1e-6, one one-sided difference agrees with the automatic Jacobian to rounding error; the other does not. The central error then collapses once h drops below the distance to the kink. This is what happens when the step straddles a point where the numerical flow map is not differentiable. Chua's diode is piecewise linear, so an RK4 stage that evaluates the field on the other side of a breakpoint creates such a point. Automatic differentiation returns the one-sided derivative there, which is the correct derivative of the map as computed. The same mechanism shows at h = 1e-4 on many passing states.
   - **The other checks are clean.** In the same production runs, V1's other finite-difference check, `gain_rel_err`, is 2.5e-9 (DEV-7) and 1.5e-9 (DEV-8).
2. **Rate.** V1's exact recipe, applied on CPU to the first 4,000 test states of DEV-5, DEV-6 and DEV-9, fails on 23, 23 and 16 states: **62 of 12,000, about 0.5% per state.**
   - V1 checks 10 states per seed, so it fails on Chua for **about 5% of seeds** (1 − (1 − 0.0052)^10).
   - Phase J saw 2 failures in 9 GPU runs with Chua (DEV-1, DEV-3 and DEV-4 at full; DEV-1 and DEV-5 to DEV-9 at `phasej`). At 5%, two or more failures in nine runs has a probability of about 7%.
   - The median per-state error is 1.2e-9.
   - **This is a new gate risk beside DEF-0026,** which estimated V6 at about 4.6% per seed on Chua.
3. **GPU nondeterminism in the Lyapunov exponent (DEV-7).**
   - **The different value.** Chua's λ_max is computed on the statistics orbit and does not depend on the seed. In the DEV-7 production run it came out as 0.4408520035546001. Eight other phase J GPU runs and my rebuild gave 0.4408520035546002.
   - **The consequence.** The step interval follows from λ_max, so it changed in its last digit (0.0756111644374209 against 0.07561116443742089). The chaotic orbit, and so every test state of DEV-7's Chua, differs from what a rerun gives.
   - **The confirmation.** A GPU rebuild with the run's own cached `lyapunov.json` reproduces DEV-7 bitwise. A GPU rebuild without it does not. DEV-5 and DEV-8 rebuild bitwise.
   - **What this means.** A GPU regeneration of a sealed run can therefore fail to be bitwise on a system, in about 1 of 9 runs here. That matters for phase I (decision 4, "regeneration … expected bitwise") and for the phase J confirmatory plan (DC-4).
   - **A fix that needs no code change.** Pre-populate each run's cache with one pinned `lyapunov.json` and record its hash. This needs the owner's ruling. It was not tested beyond the DEV-7 rebuild.
4. **CPU and GPU give different orbits** from the same seed: the test-state delay vectors differ by O(1). A CPU run informs only; it cannot reproduce a GPU state. This is consistent with DEF-0026's device dependence.

## What it changes

- **Phase J readings:** nothing. Chua on DEV-7 and DEV-8 stays labeled provisional under the freeze rule. The diagnosis supports reading the failures as artifacts of the check, but lifting the label would be an owner ruling made after the freeze.
- **CONF-1:** nothing. Its official run was on the CPU and passed V1, and its CPU regeneration was bitwise.
- **Before any sealed round:** the gate rule (DC-5) and the device and regeneration rule (DC-4) should take findings 2 and 3 into account. Changing V1's bar or recipe is the owner's alone and is not proposed.
