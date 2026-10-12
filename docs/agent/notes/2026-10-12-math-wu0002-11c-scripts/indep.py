"""Independent NumPy RK4 integrator for the registry fields (WU-0002.11c M1, M3, M5).

DEVELOPMENT. Written from the equations (Lorenz 1963; Rossler 1976; Chua with the
3-segment PWL diode), not from lpcstudy. Vectorized over starts: states (N, 3).
"""
import numpy as np

PARAMS = {
    "lorenz63": dict(sigma=10.0, rho=28.0, beta=8.0 / 3.0),
    "rossler": dict(a=0.2, b=0.2, c=5.7),
    "chua": dict(alpha=15.6, beta=28.0, m0=-1.143, m1=-0.714),
}
MAX_DT = {"lorenz63": 0.01, "rossler": 0.04, "chua": 0.005}


def field(name, s):
    x, y, z = s[..., 0], s[..., 1], s[..., 2]
    p = PARAMS[name]
    if name == "lorenz63":
        d = (p["sigma"] * (y - x), x * (p["rho"] - z) - y, x * y - p["beta"] * z)
    elif name == "rossler":
        d = (-y - z, x + p["a"] * y, p["b"] + z * (x - p["c"]))
    else:
        g = np.where(x > 1.0, p["m1"] * x + (p["m0"] - p["m1"]),
                     np.where(x < -1.0, p["m1"] * x - (p["m0"] - p["m1"]), p["m0"] * x))
        d = (p["alpha"] * (y - x - g), x - y + z, -p["beta"] * y)
    return np.stack(d, axis=-1)


def rk4(name, s, dt):
    k1 = field(name, s)
    k2 = field(name, s + 0.5 * dt * k1)
    k3 = field(name, s + 0.5 * dt * k2)
    k4 = field(name, s + dt * k3)
    return s + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)


def substeps(interval, max_dt):
    import math
    return max(1, math.ceil(interval / max_dt))


def run(name, starts, interval, n_steps, bound, freeze_at=1e6):
    """Iterate the observation map; return first index k with |x_k|>bound or non-finite
    (state 0 = start), the max |x| over states 0..n_steps-1 (frozen once |x|>freeze_at),
    and whether the orbit reached |x|>freeze_at."""
    sub = substeps(interval, MAX_DT[name])
    dt = interval / sub
    s = np.array(starts, dtype=float).copy()
    n = len(s)
    first = np.full(n, -1)
    mx = np.zeros(n)
    big = np.zeros(n, bool)
    with np.errstate(all="ignore"):
        for k in range(n_steps):
            ax = np.abs(s[:, 0])
            bad = ~(np.all(np.isfinite(s), axis=1) & (ax <= bound))
            first = np.where((first < 0) & bad, k, first)
            mx = np.where(big, mx, np.maximum(mx, np.where(np.isfinite(ax), ax, np.inf)))
            big |= ~(ax <= freeze_at)
            if big.all():
                break
            act = ~big
            t = s[act]
            for _ in range(sub):
                t = rk4(name, t, dt)
            s[act] = t
    return first, mx, big
