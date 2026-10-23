"""Independent NumPy implementation of the dimensionless Chua system (WU-0022.2).

Written from the equations only (Dysts ``_rhs`` as relayed in
2026-10-20-researcher-dysts-extension.md A.1, identical to the study's
``chua_field``); it imports nothing from ``lpcstudy``.

    x' = alpha (y - x - f(x)),  y' = x - y + z,  z' = -beta y
    f(x) = m1 x + (m0 - m1)(|x + 1| - |x - 1|) / 2   (slope m0 for |x| < 1)

Estimators
----------
* ``benettin_qr``: RK4 on the state and on the variational equation
  dV/dt = J(x) V (analytic piecewise Jacobian), QR re-orthonormalisation
  every ``interval``. Gives the full spectrum, batch means of lambda_1 and
  the time-mean divergence (trace of J) along the orbit.
* ``benettin_pair``: two-trajectory Benettin (no Jacobian), separation
  renormalised to ``d0`` every ``interval``.

All arrays carry a leading ensemble axis (N initial conditions run together).
float64 throughout. No random numbers.
"""

from __future__ import annotations

import numpy as np

OURS = {"alpha": 15.6, "beta": 28.0, "m0": -1.143, "m1": -0.714}
DYSTS = {"alpha": 15.6, "beta": 28.0, "m0": -1.142857, "m1": -0.71429}
EXACT = {"alpha": 15.6, "beta": 28.0, "m0": -8.0 / 7.0, "m1": -5.0 / 7.0}


def field(s: np.ndarray, p: dict) -> np.ndarray:
    """Chua vector field, s of shape (N, 3)."""
    x, y, z = s[:, 0], s[:, 1], s[:, 2]
    f = p["m1"] * x + 0.5 * (p["m0"] - p["m1"]) * (np.abs(x + 1) - np.abs(x - 1))
    return np.stack([p["alpha"] * (y - x - f), x - y + z, -p["beta"] * y], axis=1)


def jac(s: np.ndarray, p: dict, jac_mode: str = "exact") -> np.ndarray:
    """Analytic Jacobian (N, 3, 3).

    jac_mode: "exact" (f' = m0 inside, m1 outside), "swapped" (inner and outer
    slopes exchanged), "nohalf" (the factor 1/2 of f dropped in f').
    """
    x = s[:, 0]
    inner = np.abs(x) < 1.0
    if jac_mode == "exact":
        fp = np.where(inner, p["m0"], p["m1"])
    elif jac_mode == "swapped":
        fp = np.where(inner, p["m1"], p["m0"])
    elif jac_mode == "nohalf":
        fp = np.where(inner, p["m1"] + 2 * (p["m0"] - p["m1"]), p["m1"])
    else:
        raise ValueError(jac_mode)
    n = s.shape[0]
    j = np.zeros((n, 3, 3))
    j[:, 0, 0] = -p["alpha"] * (1.0 + fp)
    j[:, 0, 1] = p["alpha"]
    j[:, 1, 0] = 1.0
    j[:, 1, 1] = -1.0
    j[:, 1, 2] = 1.0
    j[:, 2, 1] = -p["beta"]
    return j


def rk4_state(s, p, dt):
    k1 = field(s, p)
    k2 = field(s + 0.5 * dt * k1, p)
    k3 = field(s + 0.5 * dt * k2, p)
    k4 = field(s + dt * k3, p)
    return s + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)


def rk4_tangent(s, v, p, dt, jac_mode="exact"):
    """One RK4 step of (state, tangent matrix); v of shape (N, 3, k)."""
    k1s = field(s, p)
    k1v = jac(s, p, jac_mode) @ v
    sa = s + 0.5 * dt * k1s
    k2s = field(sa, p)
    k2v = jac(sa, p, jac_mode) @ (v + 0.5 * dt * k1v)
    sb = s + 0.5 * dt * k2s
    k3s = field(sb, p)
    k3v = jac(sb, p, jac_mode) @ (v + 0.5 * dt * k2v)
    sc = s + dt * k3s
    k4s = field(sc, p)
    k4v = jac(sc, p, jac_mode) @ (v + dt * k3v)
    return (
        s + dt / 6.0 * (k1s + 2 * k2s + 2 * k3s + k4s),
        v + dt / 6.0 * (k1v + 2 * k2v + 2 * k3v + k4v),
    )


def flow(s, p, interval, dt):
    n_sub = max(1, int(round(interval / dt)))
    h = interval / n_sub
    for _ in range(n_sub):
        s = rk4_state(s, p, h)
    return s


def benettin_qr(
    s0: np.ndarray,
    p: dict,
    dt: float = 0.005,
    interval: float = 0.1,
    burn: int = 5000,
    n_int: int = 100_000,
    n_batch: int = 20,
    bound: float = 50.0,
    jac_mode: str = "exact",
) -> dict:
    """Benettin/QR spectrum for an ensemble of initial states s0 (N, 3).

    burn and n_int count re-orthonormalisation intervals. Returns per-member
    lambda (N, 3), batch means of lambda_1 (N, n_batch), the time-mean
    divergence (N,), the fraction of time with x > 0, the number of sign
    changes of x across the origin region (|x| crossing from >1 to <-1),
    and a divergence flag (max |state| > bound).
    """
    s = np.array(s0, dtype=np.float64)
    n = s.shape[0]
    n_sub = max(1, int(round(interval / dt)))
    h = interval / n_sub
    for _ in range(burn):
        for _ in range(n_sub):
            s = rk4_state(s, p, h)
    q = np.broadcast_to(np.eye(3), (n, 3, 3)).copy()
    logs = np.zeros((n, n_int, 3))
    div_sum = np.zeros(n)
    pos_time = np.zeros(n)
    side = np.sign(s[:, 0])
    switches = np.zeros(n, dtype=np.int64)
    maxabs = np.max(np.abs(s), axis=1)
    maxabs_x = np.abs(s[:, 0])
    for i in range(n_int):
        v = q
        for _ in range(n_sub):
            fp = np.where(np.abs(s[:, 0]) < 1.0, p["m0"], p["m1"])
            div_sum += -p["alpha"] * (1.0 + fp) - 1.0
            s, v = rk4_tangent(s, v, p, h, jac_mode)
        q, r = np.linalg.qr(v)
        d = np.diagonal(r, axis1=1, axis2=2)
        sg = np.sign(d)
        q = q * sg[:, None, :]
        logs[:, i, :] = np.log(np.abs(d))
        pos_time += s[:, 0] > 0
        new_side = np.where(s[:, 0] > 1, 1.0, np.where(s[:, 0] < -1, -1.0, side))
        switches += (new_side != side) & (side != 0)
        side = new_side
        maxabs = np.maximum(maxabs, np.max(np.abs(s), axis=1))
        maxabs_x = np.maximum(maxabs_x, np.abs(s[:, 0]))
    lam = logs.sum(axis=1) / (n_int * interval)
    b = n_int // n_batch
    batches = logs[:, : b * n_batch, 0].reshape(n, n_batch, b).sum(axis=2) / (b * interval)
    finite = np.all(np.isfinite(lam), axis=1)
    return {
        "lam": lam,
        "batches": batches,
        "batch_se": batches.std(axis=1, ddof=1) / np.sqrt(n_batch),
        "mean_div": div_sum / (n_int * n_sub),
        "pos_frac": pos_time / n_int,
        "switches": switches,
        "maxabs": maxabs,
        # NaN-safe: an orbit that escaped to infinity during the burn-in has a
        # NaN state, and its tangent then follows the constant outer-region
        # Jacobian, which gives a finite "exponent" (Re of the outer pair).
        "diverged": (~finite) | ~(maxabs <= bound),
        "maxabs_x": maxabs_x,
        "final": s,
    }


def benettin_pair(
    s0: np.ndarray,
    p: dict,
    dt: float = 0.005,
    interval: float = 0.1,
    burn: int = 5000,
    n_int: int = 100_000,
    d0: float = 1e-8,
    n_batch: int = 20,
) -> dict:
    """Two-trajectory Benettin estimate of lambda_1 (no Jacobian)."""
    s = np.array(s0, dtype=np.float64)
    n = s.shape[0]
    n_sub = max(1, int(round(interval / dt)))
    h = interval / n_sub
    for _ in range(burn):
        for _ in range(n_sub):
            s = rk4_state(s, p, h)
    e = np.ones((n, 3)) / np.sqrt(3.0)
    t = s + d0 * e
    logs = np.zeros((n, n_int))
    for i in range(n_int):
        for _ in range(n_sub):
            s = rk4_state(s, p, h)
            t = rk4_state(t, p, h)
        d = np.linalg.norm(t - s, axis=1)
        logs[:, i] = np.log(d / d0)
        t = s + (t - s) * (d0 / d)[:, None]
    lam = logs.sum(axis=1) / (n_int * interval)
    b = n_int // n_batch
    batches = logs[:, : b * n_batch].reshape(n, n_batch, b).sum(axis=2) / (b * interval)
    return {
        "lam": lam,
        "batch_se": batches.std(axis=1, ddof=1) / np.sqrt(n_batch),
    }


def ic_grid() -> np.ndarray:
    """Deterministic 16-point grid of initial states near the attractor.

    The field is odd, f(-s) = -f(s), and the grid is closed under s -> -s, so
    points come in mirror pairs with identical exponents; use ``ic_half`` for
    distinct orbits.
    """
    xs = [-1.5, -0.5, 0.5, 1.5]
    zs = [-1.0, 1.0]
    ys = [-0.2, 0.2]
    pts = [(x, y, z) for x in xs for y in ys for z in zs]
    return np.array(pts, dtype=np.float64)


def ic_half() -> np.ndarray:
    """The 8 grid points with x < 0 (one of each mirror pair)."""
    g = ic_grid()
    return g[g[:, 0] < 0]
