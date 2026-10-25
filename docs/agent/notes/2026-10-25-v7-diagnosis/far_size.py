"""WU-0037: size of the wrong-local-minimum errors against rho nu.

DEVELOPMENT (DEV-3): not a hypothesis test.

Usage: python far_size.py <dir with diag.py npz files>. A draw is a wrong
local minimum when its production cost exceeds chi2_0.999 rho^2 and the
truth-started LM reaches a lower cost (as in analyze.py).
"""
import sys
from pathlib import Path

import numpy as np

from lpcstudy.estimation import gof_threshold

DIMS = {"rossler_hyper": 4, "hyper_jha": 4, "lorenz96_4": 4}
d = Path(sys.argv[1])
print("DEVELOPMENT (DEV-3): not a hypothesis test")
for s in ["lorenz63_r166", "rossler_z", "hindmarsh_rose", "hyper_jha", "lorenz96_4", "lorenz63"]:
    z = np.load(d / f"{s}.npz")
    M, nu = int(z["n_draws"]), z["nu"]
    chi = gof_threshold(7 - DIMS.get(s, 3))
    out = []
    for r in (0.005, 0.01, 0.02, 0.05):
        e, c, ct = z[f"{r:g}/prod/err"], z[f"{r:g}/prod/cost"], z[f"{r:g}/truth/cost"]
        w = (c > chi * r * r) & (c > ct * (1 + 1e-9))
        rn = np.repeat(r * nu, M)
        if w.any():
            out.append(f"{r:g}: E_far median {np.median(e[w]):.3g}, E/(rho nu) median "
                       f"{np.median(e[w] / rn[w]):.3g}, c_far median {np.median(c[w]):.3g}")
        else:
            out.append(f"{r:g}: no wrong-local-minimum draw")
    print(s, "; ".join(out))
print("P(>= 1 chance chi2_0.999 exceedance in 200 draws) =", 1 - 0.999**200)
