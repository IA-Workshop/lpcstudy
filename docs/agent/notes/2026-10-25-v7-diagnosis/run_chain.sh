#!/bin/bash
# WU-0037: run diag.py on a chain of systems, sequentially, one CPU core, one thread, nice 19.
# Usage: run_chain.sh OUTDIR CORE "sys:N sys:N ..."
# DEVELOPMENT (DEV-3): not a hypothesis test.
OUT=${1:?output dir}; CORE=${2:?core}; LIST=${3:?systems}
HERE=/home/brianm/projects/physics/chaos/lpcstudy-wt/wu/0037-v7-diagnosis
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 LPC_THREADS=1
export XLA_FLAGS="--xla_cpu_multi_thread_eigen=false intra_op_parallelism_threads=1"
export JAX_PLATFORMS=cpu XLA_PYTHON_CLIENT_PREALLOCATE=false PYTHONPATH=$HERE
for item in $LIST; do
  s=${item%%:*}; n=${item##*:}
  taskset -c $CORE nice -n 19 /home/brianm/projects/physics/chaos/lpcstudy/.venv/bin/python -s \
    $HERE/docs/agent/notes/2026-10-25-v7-diagnosis/diag.py $s --states $n --out $OUT > $OUT/$s.log 2>&1
done
