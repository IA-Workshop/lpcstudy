#!/usr/bin/env bash
# Run the scripts of the note 2026-10-20-math-extension-specs.md, single
# threaded and niced, writing <script>.log beside it (REPRO.10). Development
# only: no preset, no test tier, no GPU, no network, no confirmatory artefact.
# A CPU run-2 job and a GPU ensemble were running: one thread, nice 19.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
wt="$(cd "$here/../../../.." && pwd)"
py="/home/brianm/projects/physics/chaos/lpcstudy/.venv/bin/python"
export LPC_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export PJRT_NPROC=1 NPROC=1 JAX_PLATFORMS=cpu XLA_PYTHON_CLIENT_PREALLOCATE=false
export XLA_FLAGS="--xla_cpu_multi_thread_eigen=false intra_op_parallelism_threads=1"
export PYTHONPATH="$wt"
for s in "$@"; do
  echo "== $s"
  nice -n 19 "$py" -s "$here/$s" > "$here/${s%.py}.log" 2>&1 || echo "FAILED: $s (see log)"
  tail -n 3 "$here/${s%.py}.log"
done
