"""M3: diverging Chua starts with |x0| <= 3 for G5 (DEVELOPMENT; no seed except ball directions, literal 3).

Map: Benettin interval 20*max_dt = 0.1, 20 RK4 substeps of 0.005 (as lyapunov_guarded).
State index k: s_k = Phi^k(s_0), s_0 the start (k = 0 is the start itself).
"""
import itertools, sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from indep import run, rk4
INTERVAL = 20 * 0.005
cands = [np.array(p, float) for p in itertools.product(
    (-2.0, -1.0, 0.0, 1.0, 2.0), (-1.0, 0.0, 1.0), (-6.0, -4.0, 4.0, 6.0))]
cands += [np.array(p) for p in [(0.7, 0.0, 3.0), (0.7, 0.0, 5.0), (3.0, 0.0, 0.0), (2.5, 0.0, 0.0),
                                (0.0, 0.0, 5.0), (1.0, 0.0, 5.0), (2.0, 0.0, 3.0)]]
first, mx, big = run("chua", cands, INTERVAL, 5000, 3.0)
rng = np.random.default_rng(3)
rows = []
for p, f, g in zip(cands, first, big):
    if f < 1 or not g:
        continue
    # trajectory values around the crossing
    s = p[None].copy(); xs = [p[0]]
    for k in range(f + 1):
        for _ in range(20):
            s = rk4("chua", s, 0.005)
        xs.append(s[0, 0])
    lo, hi = abs(xs[f - 1]), abs(xs[f])
    # robustness: 200 starts in a ball of radius 1e-3
    d = rng.standard_normal((200, 3)); d /= np.linalg.norm(d, axis=1, keepdims=True)
    fb, _, gb = run("chua", p + 1e-3 * d, INTERVAL, 5000, 3.0)
    rows.append((p, f, lo, hi, (fb >= 0).all() and gb.all(), fb.min(), fb.max()))
rows.sort(key=lambda r: -min(3 - r[2], r[3] - 3))
for p, f, lo, hi, rob, fmin, fmax in rows[:12]:
    print(f"start {tuple(p)} first fail k={f} |x_(k-1)|={lo:.6f} |x_k|={hi:.6f} "
          f"margin={min(3-lo, hi-3):.4f}; 1e-3 ball all diverge: {rob}, k range {fmin}-{fmax}")
print("bounded candidates:", [tuple(p) for p, f in zip(cands, first) if f < 0])
