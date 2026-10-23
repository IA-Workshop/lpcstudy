"""T0: code checks of chua_np (tangent vs central differences; region eigenvalues; timing)."""
import time, numpy as np
from chua_np import *
p = OURS
s = np.array([[1.5, 0.1, -0.7], [-0.3, 0.05, 0.4]])
v = np.broadcast_to(np.eye(3), (2, 3, 3)).copy()
h = 0.005
s1, v1 = rk4_tangent(s, v, p, h)
eps = 1e-6
fd = np.zeros((2, 3, 3))
for k in range(3):
    e = np.zeros(3); e[k] = eps
    fd[:, :, k] = (rk4_state(s + e, p, h) - rk4_state(s - e, p, h)) / (2 * eps)
print("max |tangent - central FD| of one RK4 step (no breakpoint crossed):", np.abs(v1 - fd).max())
for name, slope in [("inner |x|<1 (m0)", p["m0"]), ("outer |x|>1 (m1)", p["m1"])]:
    A = np.array([[-p["alpha"] * (1 + slope), p["alpha"], 0], [1, -1, 1], [0, -p["beta"], 0]])
    print(name, "eigenvalues:", np.round(np.linalg.eigvals(A), 4), "trace", round(np.trace(A), 4))
t = time.time()
r = benettin_qr(ic_grid(), p, n_int=500, burn=100)
print("time per interval, N=16:", (time.time() - t) / 600, "s")
