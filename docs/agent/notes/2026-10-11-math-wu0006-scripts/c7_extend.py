"""WU-0006.4 (C7 correction): independent extension of the C7 reference, same generator and procedure.

Same code path as ``m2_coverage.py`` (C7 design of the note's M3 (a), B = 2000, blocks of 5,
np.quantile bounds at 0.95 and 1 - 0.05/3), with a different scratch seed literal (20261012, not a
DEV or CONF seed), so the replications are independent of the original R_ref = 20 000 of seed
20261011. Writes ``cov_C7_<phi>_ext.npy`` to the current directory (not committed).

Usage: python c7_extend.py <phi> <R>
"""
import sys
import time

import numpy as np

from m2_coverage import run

if __name__ == "__main__":
    phi, R = float(sys.argv[1]), int(sys.argv[2])
    t0 = time.time()
    arr = run("C7", phi, R, 20261012)
    np.save(f"cov_C7_{phi:g}_ext.npy", arr)
    print(f"C7 ext phi={phi:g} R={R} t={time.time() - t0:.0f}s", flush=True)
