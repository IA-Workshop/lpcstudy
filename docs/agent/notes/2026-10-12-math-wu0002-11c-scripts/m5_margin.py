"""M5 / WU-0002.14 M1: escape probability of attractor states perturbed by eps*C^{1/2}u (DEVELOPMENT,
literal seed 20261015). 1000 attractor states thinned by 30 steps; one N(0,I) direction each;
3000 steps (one 100-LT burn-in) under the guard (|x|<=B and finite)."""
import sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from indep import run, rk4, substeps, MAX_DT
LAM = {"rossler": 0.07193978510879935, "chua": 0.43113260161336364, "lorenz63": 0.9054940534657817}
REG = {"lorenz63": (1.0, 1.0, 1.0), "rossler": (1.0, 1.0, 0.0), "chua": (0.7, 0.0, 0.0)}
B = {"lorenz63": 40.0, "rossler": 25.0, "chua": 3.0}
rng = np.random.default_rng(20261015)
for name in ("chua", "rossler", "lorenz63"):
    delta = 1 / (30 * LAM[name]); sub = substeps(delta, MAX_DT[name]); dt = delta / sub
    s = np.array([REG[name]], float)
    for k in range(3000):
        for _ in range(sub): s = rk4(name, s, dt)
    pts = []
    for k in range(30_000):
        if k % 30 == 0: pts.append(s[0].copy())
        for _ in range(sub): s = rk4(name, s, dt)
    pts = np.array(pts); C = np.cov(pts.T)
    w, v = np.linalg.eigh(C); root = v @ np.diag(np.sqrt(w)) @ v.T
    u = rng.standard_normal(pts.shape)
    for eps in (1e-6, 1e-3, 1e-2, 3e-2, 1e-1, 3e-1, 1.0):
        f, m, g = run(name, pts + eps * u @ root.T, delta, 3000, B[name])
        print(f"{name}: eps={eps:g} (whitened): refused {(f>=0).sum()}/{len(pts)}, diverged {g.sum()}; "
              f"max|x| of the others {m[f<0].max():.4f}", flush=True)
