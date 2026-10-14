"""M5: Rossler small-eps escape probability, 10 000 attractor states (DEVELOPMENT, literal seed 20261016)."""
import sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from indep import run, rk4, substeps, MAX_DT
LAM = 0.07193978510879935; delta = 1 / (30 * LAM); sub = substeps(delta, MAX_DT["rossler"]); dt = delta / sub
rng = np.random.default_rng(20261016)
s = np.array([[1.0, 1.0, 0.0]])
for k in range(3000):
    for _ in range(sub): s = rk4("rossler", s, dt)
s = s + 1e-6 * rng.standard_normal((100, 3))
for k in range(1500):
    for _ in range(sub): s = rk4("rossler", s, dt)
pts = []
for k in range(3000):
    if k % 30 == 0: pts.append(s.copy())
    for _ in range(sub): s = rk4("rossler", s, dt)
pts = np.concatenate(pts)  # 10 000 states (100 decorrelated orbits x 100)
C = np.cov(pts.T); w, v = np.linalg.eigh(C); root = v @ np.diag(np.sqrt(w)) @ v.T
u = rng.standard_normal(pts.shape)
for eps in (3e-3, 1e-2, 2e-2):
    f, m, g = run("rossler", pts + eps * u @ root.T, delta, 3000, 25.0)
    print(f"rossler eps={eps:g}: refused {(f>=0).sum()}/{len(pts)}, diverged {g.sum()}", flush=True)
