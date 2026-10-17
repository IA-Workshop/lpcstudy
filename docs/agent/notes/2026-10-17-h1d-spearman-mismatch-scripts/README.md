# Scripts of `2026-10-17-h1d-spearman-mismatch.md`

DEVELOPMENT (DEV-1, the R1 pilot dump at develop c9bb981): read-only on the run directory and on `lpcstudy/`; no preset, no GPU, no new random draw. Interpreter: the project `.venv`. Run from this directory:
`$P probeN.py` with `P=/home/brianm/projects/physics/chaos/lpcstudy/.venv/bin/python`; the run is `/home/brianm/projects/physics/chaos/lpcstudy-wt/run/r1-c9bb981/runs/r1-gpu-dev1/pilot`.

| Script | What | Log |
| --- | --- | --- |
| `probe1.py` | H1d nhat from `core/profile[:, 0, 3]` and `core/N` against the leaf; ties and the minimum | stdout |
| `probe2.py` | all four H1d rows, the tie structure, the Spearman range over all tie-breaks of the profile column | `probe2.log` |
| `probe3.py` | ties per profile column; raw N-hat below 1e-12 | `probe3.log` |
| `probe4.py` | the tied groups and the raw N-hat they hide | `probe4.log` |
