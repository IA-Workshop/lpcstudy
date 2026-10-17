# Scripts for `2026-10-14-math-wu0003-3a-kappa.md` (WU-0003.3a review finding R2)

DEVELOPMENT. Synthetic data (scratch seeds 20261040, 20261041, 20261042 through `lpcstudy.data.make_rng`), plus a read-only look at the DEV-0 pilot leaves (P0, P1). No preset, no test, no GPU. The confirmatory seed was not read, drawn or run. CPU only, 4 threads.

The scripts import `tools/rehearsal_report.py` (functions `kappa_estimate`, `block_variance`, `influence_ratio`, unchanged from cd56397 to c7d6e41) and `lpcstudy.data` from the worktree `/home/brianm/projects/physics/chaos/lpcstudy-wt/wu/0003-3a-report` (absolute path in each script). Run them from this folder with `PY=<repo>/.venv/bin/python3 -I` and `OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4`.

| Script | What | Command | Log |
| --- | --- | --- | --- |
| `r2_mean_b.py` | Mean dependence term from P0/P1 leaves (`mse - regret - mse(A*)` at 1 LT); controls have b = 0 | `python3 -I r2_mean_b.py` | `r2_mean_b.log` |
| `r2_kappa_sim.py` | Mechanistic synthetic world, 14 scenarios x 4 criteria: the tool's kappa-hat, its population estimand, and the half-split estimator against the ANOVA truth (16 draws per state) | `$PY r2_kappa_sim.py 1000` (about 3 min) | `r2_kappa_sim.log` |
| `r2_kappa_down.py` | f2-style arrays with a dependence term uncorrelated with the state level: the tool is biased down | `$PY r2_kappa_down.py` | `r2_kappa_down.log` |
| `r2_jack.py` | Coverage of kappa^2 by half-split +- 2 delete-a-block jackknife SE (20 blocks of 25 states) | `$PY r2_jack.py` (about 2 min) | `r2_jack.log` |

Columns of `r2_kappa_sim.log`: `truth` (SE from a joint bootstrap over replicates); `tool` (the mean of the tool's kappa-hat), its bias and the paired SE; `tool pop` (the population form of the tool's estimand), its bias and SE; `k2 half-truth2` (the half-split kappa^2 minus truth^2) and SE; `half pop` (the half-split population form), its bias and SE; `draw share` (the per-draw part of the E = 2 variance; values just above 1 are Monte Carlo noise of a state part near 0); the per-run SDs; and the number of the 1000 runs whose half-split kappa^2 lies outside [1/2, 1] (reported, not clipped). The single `nan` (S7 H2d) is a bootstrap SE in which the population form went negative, a heavy-tailed case.
