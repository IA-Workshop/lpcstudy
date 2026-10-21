#!/usr/bin/env bash
# As run.sh, but PYTHONPATH = the wu/ext-impl2 worktree (the implementation's code).
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
py="/home/brianm/projects/physics/chaos/lpcstudy/.venv/bin/python"
export LPC_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export PJRT_NPROC=1 NPROC=1 JAX_PLATFORMS=cpu XLA_PYTHON_CLIENT_PREALLOCATE=false
export XLA_FLAGS="--xla_cpu_multi_thread_eigen=false intra_op_parallelism_threads=1"
export PYTHONPATH="/home/brianm/projects/physics/chaos/lpcstudy-wt/wu/ext-impl2"
for s in "$@"; do
  echo "== $s"
  nice -n 19 "$py" -s "$here/$s" ${ARGS:-} > "$here/${s%.py}.log" 2>&1 || echo "FAILED: $s (see log)"
done
