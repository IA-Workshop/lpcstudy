"""O4 proxy (indicative only): serial dependence of a dynamics-driven per-state quantity on the
test-state grid. Independent numpy RK4 (pilot step interval, spacing and max_dt from the pilot
metadata / systems.py). For each of 500 test states: the 30-step (1 LT = H_ref) tangent propagator J;
series: log ||J||_F^2 (log of the error amplification, proxy for log per-state MSE) and ||J||_F^2.
Per-state MSE adds draw and seed noise that is independent across states, which lowers the acf;
so this proxy is an upper-side indication for the dynamics part."""
import os
for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[v] = "1"
import numpy as np

def mat(rows, s):
    return np.array([[np.broadcast_to(np.asarray(e, float), s[0].shape) for e in r] for r in rows])


SYS = {
    "lorenz63": (lambda s: np.stack([10 * (s[1] - s[0]), s[0] * (28 - s[2]) - s[1], s[0] * s[1] - 8 / 3 * s[2]]),
                 lambda s: mat([[-10, 10, 0], [28 - s[2], -1, -s[0]], [s[1], s[0], -8 / 3]], s),
                 0.03681231611157454, 45, 0.01, (1.0, 1.0, 1.0)),
    "rossler": (lambda s: np.stack([-s[1] - s[2], s[0] + 0.2 * s[1], 0.2 + s[2] * (s[0] - 5.7)]),
                lambda s: mat([[0, -1, -1], [1, 0.2, 0], [s[2], 0, s[0] - 5.7]], s),
                0.4633504712715099, 150, 0.04, (1.0, 1.0, 0.0)),
    "chua": (None, None, 0.07731573350889016, 150, 0.005, (0.7, 0.0, 0.0)),
}
al, be, m0, m1 = 15.6, 28.0, -1.143, -0.714


def chua_f(s):
    d = m1 * s[0] + 0.5 * (m0 - m1) * (np.abs(s[0] + 1) - np.abs(s[0] - 1))
    return np.stack([al * (s[1] - s[0] - d), s[0] - s[1] + s[2], -be * s[1]])


def chua_j(s):
    dd = np.where(np.abs(s[0]) < 1, m0, m1)
    z, o = np.zeros_like(s[0]), np.ones_like(s[0])
    return mat([[al * (-1 - dd), al * o, z], [o, -o, o], [z, -be * o, z]], s)


SYS["chua"] = (chua_f, chua_j, *SYS["chua"][2:])


def acf(x, k):
    x = x - x.mean()
    return float(np.sum(x[:-k] * x[k:]) / np.sum(x * x))


for name, (f, jac, interval, spacing, max_dt, init) in SYS.items():
    nsub = int(np.ceil(interval / max_dt)); h = interval / nsub
    def step(s):
        for _ in range(nsub):
            k1 = f(s); k2 = f(s + 0.5 * h * k1); k3 = f(s + 0.5 * h * k2); k4 = f(s + h * k3)
            s = s + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        return s
    s = np.array(init, float)
    for _ in range(3000):  # burn-in (100 LT)
        s = step(s)
    n = 500
    states = np.empty((n, 3))
    for i in range(n):
        states[i] = s
        for _ in range(spacing):
            s = step(s)
    # tangent propagators over 30 steps, vectorized over states: X' = f(X), J' = Df(X) J
    X = states.T.copy(); J = np.tile(np.eye(3)[:, :, None], (1, 1, n))
    def rhs(X, J):
        return f(X), np.einsum('ikn,kjn->ijn', jac(X), J)
    for _ in range(30 * nsub):
        a1, b1 = rhs(X, J); a2, b2 = rhs(X + 0.5 * h * a1, J + 0.5 * h * b1)
        a3, b3 = rhs(X + 0.5 * h * a2, J + 0.5 * h * b2); a4, b4 = rhs(X + h * a3, J + h * b3)
        X = X + h / 6 * (a1 + 2 * a2 + 2 * a3 + a4); J = J + h / 6 * (b1 + 2 * b2 + 2 * b3 + b4)
    fro2 = np.einsum('ijn,ijn->n', J, J)
    lg = np.log(fro2)
    print(f"{name}: spacing {spacing} steps; log||J||^2 mean {lg.mean():.2f} sd {lg.std():.2f}; "
          f"acf lag1..3 of log: {[round(acf(lg, k), 3) for k in (1, 2, 3)]}; "
          f"of raw: {[round(acf(fro2, k), 3) for k in (1, 2, 3)]}; 2/sqrt(n)={2/np.sqrt(n):.3f}", flush=True)
