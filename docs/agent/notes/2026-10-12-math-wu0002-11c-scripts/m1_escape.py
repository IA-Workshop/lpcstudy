"""M1/M4/M5: attractor maxima per coordinate and escape behaviour (DEVELOPMENT).

Independent NumPy RK4 (indep.py). Literal default_rng seed 20261012 (development only;
not a project seed).
"""
import sys
import time

import numpy as np

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from indep import MAX_DT, rk4, run, substeps

REG = {"lorenz63": (1.0, 1.0, 1.0), "rossler": (1.0, 1.0, 0.0), "chua": (0.7, 0.0, 0.0)}
B = {"lorenz63": 40.0, "rossler": 25.0, "chua": 3.0}
LAM = {"lorenz63": 0.9054940534657817, "rossler": 0.07193978510879935,
       "chua": 0.43113260161336364}

part = sys.argv[1]

if part == "attractor":
    # per-coordinate max over 64 parallel orbits x 20000 steps (1.28e6 states) at the study
    # interval Delta = 1/(30 lambda); copies decorrelate within ~40 LT (1200 steps).
    rng0 = np.random.default_rng(20261013)  # DEVELOPMENT literal seed
    for name in REG:
        delta = 1.0 / (30 * LAM[name])
        sub = substeps(delta, MAX_DT[name]); dt = delta / sub
        s = np.array([REG[name]], float)
        reg_mx = np.zeros(3)
        for k in range(3000):
            reg_mx = np.maximum(reg_mx, np.abs(s[0]))
            for _ in range(sub):
                s = rk4(name, s, dt)
        s = s + 1e-6 * rng0.standard_normal((64, 3))
        mx = np.zeros(3); mn = np.full(3, np.inf)
        t0 = time.time()
        for k in range(20_000):
            mx = np.maximum(mx, np.abs(s).max(axis=0)); mn = np.minimum(mn, s.min(axis=0))
            for _ in range(sub):
                s = rk4(name, s, dt)
        print(f"{name}: Delta={delta:.5f} sub={sub}: burn-in 3000 from registry start max|s_i| = {reg_mx}; "
              f"attractor 1.28e6 states max|s_i| = {mx}, min s_i = {mn}, B/max|x| = {B[name]/mx[0]:.3f} "
              f"({time.time()-t0:.0f}s)", flush=True)

if part == "escape":
    rng = np.random.default_rng(20261012)  # DEVELOPMENT literal seed
    for name, box in [("chua", (3.0, 1.0, 6.0)), ("rossler", (25.0, 25.0, 25.0))]:
        n = 4000
        starts = rng.uniform(-1, 1, size=(n, 3)) * np.array(box)
        delta = 1.0 / (30 * LAM[name])
        n_steps = 28_000  # shortest guarded orbit: smoke estimator, 3000 + 5*5000 (+history)
        t0 = time.time()
        first, mx, big = run(name, starts, delta, n_steps, B[name])
        esc = first >= 0
        print(f"{name}: {n} starts in box |s_i|<={box}; Delta={delta:.5f}; {n_steps} steps "
              f"({time.time()-t0:.0f}s)")
        print(f"  refused (|x|>B or non-finite at some state): {esc.sum()}; reached |x|>1e6: "
              f"{big.sum()}; refused but never >1e6: {(esc & ~big).sum()}; "
              f">1e6 but never refused: {(big & ~esc).sum()}")
        ok = ~esc
        print(f"  bounded starts: max|x| over orbit max {mx[ok].max():.4f}; "
              f"after-start max distribution q50/q99/max of mx: "
              f"{np.quantile(mx[ok], [0.5, 0.99, 1.0])}")
        f = first[esc]
        print(f"  first failing step among refused: q50 {np.median(f):.0f}, q99 "
              f"{np.quantile(f, 0.99):.0f}, max {f.max()} (= {f.max()*delta:.1f} time units)")
        np.save(__import__("pathlib").Path(__file__).resolve().parent / f"esc_{name}.npy", np.c_[starts, first, mx, big])
