"""M1: Rossler starts near the outer saddle-focus P+ (DEVELOPMENT, literal seed 11)."""
import sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from indep import run
a, b, c = 0.2, 0.2, 5.7
xp = (c + np.sqrt(c * c - 4 * a * b)) / 2
P = np.array([xp, -xp / a, xp / a])
J = np.array([[0, -1, -1], [1, a, 0], [P[2], 0, P[0] - c]])
w, v = np.linalg.eig(J)
print("P+ =", P, "eigenvalues", w)
LAM = 0.07193978510879935; delta = 1 / (30 * LAM)
rng = np.random.default_rng(11)
for eps in (1e-2, 1e-6, 1e-10, 1e-14):
    d = rng.standard_normal((200, 3)); d /= np.linalg.norm(d, axis=1, keepdims=True)
    f, m, g = run("rossler", P + eps * d, delta, 3000, 25.0)
    ref = f >= 0
    print(f"eps={eps:.0e}: refused {ref.sum()}/200 (diverged {g.sum()}), refusal step max {f[ref].max() if ref.any() else None} "
          f"median {np.median(f[ref]) if ref.any() else None}; not refused: max|x| {m[~ref].max() if (~ref).any() else None}")
