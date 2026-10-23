#!/bin/bash
# Regenerate all outputs: one niced thread, CPU only.
cd "$(dirname "$0")"
PY=${PY:-/home/brianm/projects/physics/chaos/lpcstudy/.venv/bin/python}
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 LPC_THREADS=1 JAX_PLATFORMS=cpu
for s in t0_checks t1_units e1_reference e2_benettin_settings e3_parameters_attractor e4_dysts_spectrum_replica e5_divergence_estimators t2_comparisons; do
  [ -n "$ONLY" ] && [[ " $ONLY " != *" $s "* ]] && continue
  nice -n 19 $PY -W ignore::RuntimeWarning $s.py > $s.log 2>&1 || echo "$s failed" >> $s.log
done
