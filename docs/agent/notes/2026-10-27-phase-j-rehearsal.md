# Phase J confirmatory rehearsal (WU-0055)

**DEVELOPMENT (DEV-5, DEV-6): rehearsal of the sealed chain. No reading or result changes.** Main session (claude-opus-5-5), 2026-10-27. Owner direction "once WU-0054 lands, proceed as recommended until my action is needed".

- **Code:** develop at 54975c7 (WU-0054 merged), detached worktree `lpcstudy-wt/run/phj-reh-54975c7`.
- **Runs:** `tools/run_preset.sh` on the GPU under the lock, `--preset phasej --skip-robustness --states-dump`, DEV-5 then DEV-6. Each run's cache started from the pinned `docs/study/preregistration_phase_j/lyapunov.json` (sha256 852ce1f6…7453417). The cache file was read and not rewritten (same hash after the run).
- **Reference:** the frozen runs `lpcstudy-wt/run/phj-freeze/runs/dev/phj-DEV-{5,6}` and their `contrib-freeze` analyses.
- **Analysis:** `lpc_contrib.py --replication`, then `lpc_contrib_ce.py --replication --abd <o>/contrib.json`, then `lpc_confirm.py --rehearsal` on the two seeds.

## Results

| Check | DEV-5 | DEV-6 |
|---|---|---|
| GPU run exit code, wall time | 0, 1710 s | 0, 1880 s |
| `compare_runs` T0 against the frozen run | **FAIL**: 420 of 20,846 leaves differ | pass: 20,790 of 20,790 equal |
| Dump arrays bitwise (355 per system) | **11 / 8 / 8 differ** (Chua / Lorenz-63 / Rössler) | 0 differ |
| Analysis exit codes (A/B/D, C/E) | 0, 0 | 0, 0 |
| Categorical readings against the frozen analysis | **16 differ, all Chua deployable** (11 contrib, 5 C/E) | 0 differ (only provenance and timing leaves) |

- **`lpc_confirm --rehearsal` on two seeds:** exit 0; 48 rows, all "not confirmable" (2 seeds present, fewer than 4), as expected.
- **The evaluator on the frozen DEV-5 and DEV-6 analyses:** the same 48 rows, with **0 per-seed readings changed**. The v3 description is identical.
- **WU-0055 criterion "with the pinned cache, a second GPU run of each rehearsal seed is bitwise equal to the first (tier T0)": not met** (DEV-5).

## What differs on DEV-5 (DEF-0033)

1. **The orbits are bitwise equal.** The chaotic states, the oracle seeds `eps_s` and `delta`, the oracle ν, the growth proxy and the noise sensitivity are all equal. The pin worked: λ_max is the same.
2. **What moved: the fitted coefficients of both seed proxies,** in all three systems.
   - The relative change is about 1e-9: for example, the Lorenz-63 analog slope went from 0.27916085862757833 to 0.2791608592836142.
   - On Chua and Rössler, `least_squares` took a different path: nfev 13 → 18 and 20 → 12, status 2 → 3 and 4 → 2.
   - Profile columns 0 and 1 (ln ε̂/ρ, ln δ̂/ρ) shift by the constant ½·Δln(slope) on every construction state, which is what a change in the coefficients alone produces (Lorenz-63: 1.175e-9 predicted, 1.08e-9 to 1.18e-9 observed).
3. **Where it comes from.** On 9 of 16,000 Lorenz-63 test entries, δ̂ also moves, by up to 1.5e-6, outside that constant shift. δ̂ depends only on ν̂ at the estimated state, which the Levenberg–Marquardt state estimator (`estimate_counted`) computes on the GPU.
   - So ν̂ at the estimated state is not reproducible on a few entries.
   - The CPU fit carries that into every state through the coefficients.
   - Likely mechanism: a last-bit difference in a GPU reduction changes where the iteration stops. The responsible operation was not isolated.
4. **How far it reaches.**
   - In results.json, the largest class (a) change is 1.6% relative, on a Chua Shapley R interval bound. Four integer leaves differ: the nfev and status entries above.
   - In the analysis, 16 Chua deployable readings flip. Among them are interaction detections (ON at 60 steps; RN and IN at the horizon), drop-one N detection at the horizon, and the C2 prediction check. None is a pre-registered row.
   - So some non-claimed Chua deployable readings sit at a threshold that a 1e-9 perturbation crosses.
5. **The rate is not known.** It was seen in 1 of 2 runs here. DEV-6 was bitwise, and so were the build-context rebuilds of DEV-5 and DEV-8 in the V1 diagnosis (those did not reach the proxy fit).

## Outputs (sha256)

```
67959abac5688b7107f4eac371cb433fd8c8c9293dcfb1cf15bcae7df8ddf100 runs/dev/reh-DEV-5/phasej/results.json
3267b3232ce42a565b60c63b753638b3878b626d5a94bc6af8fd2d79c54c07ae runs/dev/reh-DEV-6/phasej/results.json
a68146a297b0726ca0c229238765c5cb68673dd41983f7834c85c27bcbfd5b38 runs/dev/reh-DEV-5/contrib-reh/contrib.json
413bf143d6aca0325c58f5a22c7eccc7f9861bee8dafa48ee1fdbd27f1f775b0 runs/dev/reh-DEV-5/contrib-reh/ce.json
84852fecec9ecd5ead1a61a89789319ff5aeb069305b45feebfc2f8068b27581 runs/dev/reh-DEV-6/contrib-reh/contrib.json
ec2db5d32669c83df0232f4e1c76bb01d1dc8fdd56b6c2bf994ddc3fdae42ac6 runs/dev/reh-DEV-6/contrib-reh/ce.json
e7a8c685787c8c6db88b02d4a95ed7f628e8605c8f0a98cc4864b05b6d510e28 runs/dev/reh-confirm/confirm.json
fbdd73edee887e2c560979ef11e57c4d8e11a92391401049a99c8941f53b5d68 runs/dev/reh-confirm/v3.json
```

Paths are relative to `lpcstudy-wt/run/phj-reh-54975c7`.

## What it changes

- **Phase J development readings:** nothing is re-read. The report already states replication over five seeds, not the stability of any single run. But the 16 flipped Chua readings show that a single DEV-5 run's deployable Chua readings near a threshold are not reproducible on the GPU.
- **The confirmatory round:**
  - DC-4 promised a bitwise regeneration, and the rehearsal shows it cannot be promised on the GPU, even with the pin.
  - The pre-registration (§5) already says "No verdict depends on the regeneration", so the verdict rule is unaffected.
  - The expectation, and what a non-bitwise regeneration means, need the owner's ruling before approval (P-2).
