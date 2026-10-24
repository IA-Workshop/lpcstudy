# Scripts of the note `2026-10-19-math-other-attractors.md`

DEVELOPMENT (scratch seed 20261019): not a hypothesis test. CPU, one thread, `nice -n 19`. No preset, no test tier, no GPU, no network; the confirmatory seed, flag and run directory were not touched. The project venv was not modified.

Run everything (each script writes `<name>.log` beside it):

```
./run.sh p1_p3_identities.py p2_bound_check.py p3_regime_floor.py p1d_horizon_gain.py lyapunov_candidates.py p1_curvature_floor.py
nice -n 19 env OMP_NUM_THREADS=1 uv run --no-project --with sympy python -I p1_p3_sympy.py > p1_p3_sympy.log 2>&1
```

`run.sh` uses `/home/brianm/projects/physics/chaos/lpcstudy/.venv/bin/python -s` with `PYTHONPATH` set to the worktree (`python -I` would ignore it). The SymPy script runs in an ephemeral `uv` environment (sympy 1.14.0, mpmath 1.3.0 at the time of the run); sympy is not a project dependency.

| Script | Time (1 thread) |
| --- | --- |
| `p1_p3_identities.py` | < 5 s |
| `p1_p3_sympy.py` | < 10 s |
| `p2_bound_check.py` | about 20 s |
| `p3_regime_floor.py` | about 30 s |
| `p1d_horizon_gain.py` | < 5 s |
| `lyapunov_candidates.py` | 15 s |
| `p1_curvature_floor.py` | about 4 min (un-jitted per-state Jacobians) |

Fixes made during the run and recorded in the logs' history: `p2_bound_check.py` first drew the noise at unit scale instead of ρ (parts (a) and (c) are scale-free and were unaffected; the Markov comparison and the r₁/ρ summaries were wrong) and used a binomial SE that is zero when every draw exceeds the threshold; both were corrected before the committed log. `p3_regime_floor.py`'s first construction of the all-above-1 regimes was invalid (an assertion caught it) and was replaced.
