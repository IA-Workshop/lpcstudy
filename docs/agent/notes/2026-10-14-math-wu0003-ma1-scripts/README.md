# Scripts of `2026-10-14-math-wu0003-ma1.md` (WU-0003, mathematician item MA-1)

DEVELOPMENT (DEV-0 pilot medians already on disk, read-only, plus literal scratch seeds 20261020 and 20261021 for synthetic worlds): not a hypothesis test. No preset, no test, no GPU; the confirmatory seed was not read, drawn or run. CPU, `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=4`. Interpreter: the project `.venv` (Python 3.13.16, numpy 2.5.3, scipy 1.18.1). No `lpcstudy` import: `ma1_core.py` holds a verbatim copy of `_floor_power_law` and `_fit_seed_law` (develop 0e9b892; the fit code is identical on `wu/0003-rehearsal`), returning all three parameters.

`$P` = `/home/brianm/projects/physics/chaos/lpcstudy/.venv/bin/python`; `$R` = `/home/brianm/projects/physics/chaos/lpcstudy-wt/run`; `<P0>` = `$R/p0-1b20db9/runs/dev/p0/pilot/results.json`; `<P1>` = `$R/p1-5b3fd8f/runs/dev/p1/pilot/results.json`.

| Script | Check | Command (run from this directory) | Time | Log |
| --- | --- | --- | --- | --- |
| `ma1_core.py` | the model, the exact Hessian, the IFT Jacobian, the density estimators, the influence series | (module) | | |
| `ma1_gateaux.py` | 1: analytic IF against the numerical Gateaux derivative (population worlds on the 12 pilot cells; step refinement; production-fit noise) | `$P -I ma1_gateaux.py <P0> <P1>` | 8 s | `ma1_gateaux.log` |
| `ma1_sample.py` | 2: estimated series on samples of n = 300 and 1000, phi = 0 and 0.3 (linearization, SE, acf(1), density error) | `$P -I ma1_sample.py <P0> <P1>` | 40 s | `ma1_sample.log` |
| `ma1_ift.py` | 3: IFT Jacobian against differences of the tight and the production fit; Gauss-Newton error; the case-value range | `$P -I ma1_ift.py <P0> <P1>` | 2 s | `ma1_ift.log` |
| `ma1_sumzero.py` | 4: the identity sum_j A_j = 0 | `$P -I ma1_sumzero.py <P0> <P1>` | 1 s | `ma1_sumzero.log` |

The scratch seeds use `numpy.random.default_rng` literals, as in the earlier WU-0003 notes; they are not admissible in `tests/` (the `make_rng` rule).
