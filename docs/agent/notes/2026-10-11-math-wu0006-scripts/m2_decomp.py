"""Decompose MBB mean-interval coverage (Gaussian AR(1)): first order (E[V*]/V), plus V* noise
(normal interval centre +- z sqrt(V*), exact V* per data set, no resampling), against the full
B = 2000 percentile simulation (m2_coverage), whose difference is the endpoint (B) + shape term."""
import os
for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[v] = "1"
import numpy as np
from scipy.stats import norm
rng = np.random.default_rng(7)
R = 40000
for n in (500, 300):
    for phi in (0.0, 0.3):
        x = np.empty((R, n)); e = rng.standard_normal((R, n)); x[:, 0] = e[:, 0]
        for t in range(1, n):
            x[:, t] = phi * x[:, t - 1] + np.sqrt(1 - phi**2) * e[:, t]
        c = np.concatenate([np.zeros((R, 1)), np.cumsum(x, 1)], 1)
        bm = (c[:, 5:] - c[:, :-5]) / 5
        k = n // 5
        cen = bm.mean(1); vs = bm.var(1) / k
        V = ((1 + phi) / (1 - phi) - 2 * phi * (1 - phi**n) / (n * (1 - phi)**2)) / n
        out = [f"n={n} phi={phi}: E[V*]/V={vs.mean()/V:.4f} cv(V*)={vs.std()/vs.mean():.4f}"]
        for lev in (0.95, 1 - 0.05 / 3):
            z = norm.ppf(1 - (1 - lev) / 2)
            first = 2 * norm.cdf(z * np.sqrt(vs.mean() / V)) - 1
            cov = np.mean(np.abs(cen) <= z * np.sqrt(vs))
            out.append(f"L{lev:.4f}: first-order={first:.4f} with V*-noise={cov:.4f}(se {np.sqrt(cov*(1-cov)/R):.4f})")
        print(" | ".join(out), flush=True)
        del x, e, c, bm
