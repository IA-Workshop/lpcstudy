# Scripts of `2026-10-14-math-wu0003-9-q1.md` (WU-0003.9, Q1, Q2, Q5)

DEVELOPMENT (DEV-0 results already on disk, plus literal scratch seeds 20261018 and 20261019): not a hypothesis test. No preset, no test, no GPU; the confirmatory seed was not read, drawn or run. Every script reads `results.json` files read-only. CPU, `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=4`. Interpreter: the project `.venv` (numpy 2.5.3, scipy 1.18.1, as pinned and as recorded in the runs' provenance).

`$P` = `/home/brianm/projects/physics/chaos/lpcstudy/.venv/bin/python`; `$R` = `/home/brianm/projects/physics/chaos/lpcstudy-wt/run`. `<P0>` = `$R/p0-1b20db9/runs/dev/p0/pilot/results.json`; `<P1>` = `$R/p1-5b3fd8f/runs/dev/p1/pilot/results.json`. Kernel pair (WU-0002.14 S3, default OpenBLAS kernel against `OPENBLAS_CORETYPE=Sandybridge`): `<B>` = `$R/wu0002-14-smokeB/runs/b/smoke/results.json`, `<BS>` = `$R/wu0002-14-smokeB/runs/bsandy/smoke/results.json`; the older pair `$R/wu0002-14-s3/runs/{s3default,s3sandy}` gives identical H1a leaves (`q1_reproduce_s3.log` equals `q1_reproduce.log`).

| Script | Question | Command (run from this directory) | Log |
| --- | --- | --- | --- |
| `q1_reproduce.py` | Q1: reproduce the smoke H1a fit, its stop and its rank | `$P -I q1_reproduce.py <B> <BS>` (and the s3 pair) | `q1_reproduce.log`, `q1_reproduce_s3.log` |
| `q1_pilot_sensitivity.py` | Q1: exact conditioning, stopping error, ulp experiment on the 12 pilot cells and 480 resample-like inputs | `$P -I q1_pilot_sensitivity.py <P0> <P1>` | `q1_pilot_sensitivity.log` |
| `q1_flip_bound.py` | Q1: size of a stopping-test flip; mechanism (2-point against analytic Jacobian) | `$P -I q1_flip_bound.py <P0> <P1> <B>` | `q1_flip_bound.log` |
| `q1_ftol_theory.py` | Q1: a-priori scales (sqrt(ftol) stop, FD fixed point) against observation | `$P -I q1_ftol_theory.py <P0> <P1>` | `q1_ftol_theory.log` |
| `q2_scale.py` | Q2: rel under s = max(\|lo\|, \|hi\|) and unscaled | `$P -I q2_scale.py <B> <BS>` | `q2_scale.log` |
| `q5_chain_census.py` | Q5: chain tags of `compare_pilot` over the float leaves | `$P -I q5_chain_census.py ../../../../tools <B> <BS>`; `... ../../../../tools <P1>` | `q5_chain_census.log`, `q5_chain_census_pilot.log` |

The fit in `q1_reproduce.py` is a verbatim copy of `lpcstudy.analysis._floor_power_law` and `_fit_seed_law` (worktree c80f908), so that no `lpcstudy` module (and no JAX) is imported; it reproduces the reference leaf bitwise (`q1_reproduce.log`, "equal: True").
