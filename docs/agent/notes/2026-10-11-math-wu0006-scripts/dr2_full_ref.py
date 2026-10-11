"""WU-0006.4 A9: null delta-R2 reference at the sizes the study uses (3000 training / 1000 test).

Same replication as ``m4_dr2_full.work`` (the review's M3 (g) design, production ``qn_profile_block``
with B = 2000 and blocks of 5, truth from the returned fitted pair on 1e5 fresh i.i.d. states), which
is the design of ``wu0006_harness._delta_replicate``. Scratch seed literal 20261014 (not a DEV or CONF
seed; independent of the R = 200 run of seed 20261011). Spawned single-thread workers; chunks of 5
replications, progress printed per chunk; writes ``dr2ref_<phi>.npy`` to the current directory.

Usage: python dr2_full_ref.py <phi> <R> [workers]
"""
import os
import sys
import time

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[v] = "1"
os.environ["JAX_PLATFORMS"] = "cpu"
import numpy as np
from multiprocessing import get_context

from m4_dr2_full import work

CHUNK = 5

if __name__ == "__main__":
    phi, R = float(sys.argv[1]), int(sys.argv[2])
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    t0 = time.time()
    n_chunks = -(-R // CHUNK)
    ss = np.random.SeedSequence([20261014, 9, int(round(phi * 1000))])
    seeds = [int(c.generate_state(1)[0]) for c in ss.spawn(n_chunks)]
    tasks = [(phi, s, min(CHUNK, R - i * CHUNK)) for i, s in enumerate(seeds)]
    done = 0
    rows = [None] * n_chunks
    with get_context("spawn").Pool(workers) as pool:
        for i, part in enumerate(pool.imap(work, tasks)):  # in task order
            rows[i] = part
            done += len(part)
            if (i + 1) % 10 == 0 or done == R:
                print(f"phi={phi:g} {done}/{R} t={time.time() - t0:.0f}s", flush=True)
    a = np.array([row for part in rows for row in part])
    np.save(f"dr2ref_{phi:g}.npy", a)
    print(f"phi={phi:g} R={len(a)} done t={time.time() - t0:.0f}s", flush=True)
