"""G4 band (WU-0002.11c M4), DEVELOPMENT. Independent NumPy RK4 (indep.py) at the Benettin
interval 20*max_dt: (1) max|x| over states 0..104999 from the registry start (same orbit
definition as lyapunov_guarded with the burn-in carried); (2) 32 block maxima of 1e5 states from
decorrelated attractor orbits (literal seed 20261014). Outputs: g4_indep_out.txt, g4_blockmax_out.txt."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from indep import rk4, run
REG = {"lorenz63": (1., 1., 1.), "rossler": (1., 1., 0.), "chua": (0.7, 0., 0.)}
MD = {"lorenz63": 0.01, "rossler": 0.04, "chua": 0.005}
for n, s0 in REG.items():
    f, m, g = run(n, [s0], 20 * MD[n], 105_000, 1e300)
    print(n, "numpy max|x| over states 0..104999:", repr(m[0]))
rng = np.random.default_rng(20261014)
for name, s0 in REG.items():
    md = MD[name]; s = np.array([s0])
    for k in range(5000):
        for _ in range(20): s = rk4(name, s, md)
    s = s + 1e-6 * rng.standard_normal((32, 3))
    for k in range(2000):
        for _ in range(20): s = rk4(name, s, md)
    mx = np.zeros(32)
    for k in range(100_000):
        mx = np.maximum(mx, np.abs(s[:, 0]))
        for _ in range(20): s = rk4(name, s, md)
    print(name, "32 block maxima: min %.4f q10 %.4f median %.4f max %.4f"
          % (mx.min(), np.quantile(mx, .1), np.median(mx), mx.max()))
