# Scripts for `2026-10-14-math-wu0003.md` (WU-0003 plan amendment 1, M1 to M8)

DEVELOPMENT (DEV-0 results already on disk, plus literal scratch seeds 20261014 to 20261017): not a hypothesis test. No preset, no test, no GPU; the confirmatory seed was not read, drawn or run. Every script reads `results.json` files read-only or simulates synthetic data. CPU, at most 4 threads.

`R=/home/brianm/projects/physics/chaos/lpcstudy-wt/run`, `PY=<repo>/.venv/bin/python -I` (numpy/scipy needed for `m3_bfactor`, `m4_ratios`, `m5_d5sim`, `m5_d5split`, `m6_bands`; the others run under `python3 -I`).

| Script | Item | Command | Log |
| --- | --- | --- | --- |
| `m1_kernel_pair.py` | M1 | `python3 -I m1_kernel_pair.py $R/wu0002-14-smokeB/runs/b/smoke/results.json $R/wu0002-14-smokeB/runs/bsandy/smoke/results.json` | `m1_kernel_pair.log` |
| `m1_td_p0p1.py` | M1 (TD), M3 | `python3 -I m1_td_p0p1.py $R/p0-1b20db9/runs/dev/p0/pilot/results.json $R/p1-5b3fd8f/runs/dev/p1/pilot/results.json` | `m1_td_p0p1.log` |
| `m2_floors.py` | M2 | as `m1_kernel_pair.py` | `m2_floors.log` |
| `m3_bfactor.py` | M3 | `$PY m3_bfactor.py` | `m3_bfactor.log` |
| `m3_projection.py` | M3 | `python3 -I m3_projection.py <P0> <P1>` | `m3_projection.log` |
| `m4_ratios.py` | M4 | `$PY m4_ratios.py` (R = 4000 per row, about 3 min) | `m4_ratios.log` |
| `m4_beta5.py` | M4 | `python3 -I m4_beta5.py` | `m4_beta5.log` |
| `m5_f1.py` | M5 | `python3 -I m5_f1.py <P0> <P1>` | `m5_f1.log` |
| `m5_d5sim.py` | M5 | `$PY m5_d5sim.py` (about 2 min) | `m5_d5sim.log` |
| `m5_d5split.py` | M5, M4 | `$PY m5_d5split.py` (primary D5 estimator on all eligible states; D2 union trigger; about 3 min) | `m5_d5split.log` |
| `c4_lm.py` | M6 | `python3 -I c4_lm.py <P0> <P1>` | `c4_lm.log` |
| `m6_bands.py` | M6 | `$PY m6_bands.py <P0> <P1>`; `m6_bands.log` is `m6_bands_all.log` without the duplicate library-sweep rows | `m6_bands_all.log`, `m6_bands.log` |

`<P0>` = `$R/p0-1b20db9/runs/dev/p0/pilot/results.json` (DEV-0, lpcstudy 1b20db9, old start states); `<P1>` = `$R/p1-5b3fd8f/runs/dev/p1/pilot/results.json` (DEV-0, lpcstudy 5b3fd8f, redrawn start states). The smoke pair is DEV-0 at 759d47b, default OpenBLAS kernel against `OPENBLAS_CORETYPE=Sandybridge` (WU-0002.14 S3).
