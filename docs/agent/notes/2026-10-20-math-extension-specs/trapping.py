"""Numerical check of the Lorenz trapping-ball bound used for the S2 orbit
bound (DEVELOPMENT). V = x^2 + y^2 + (z - sigma - r)^2;
dV/dt = -2 sigma x^2 - 2 y^2 - 2 beta (z - c/2)^2 + beta c^2 / 2, c = sigma + r
(algebra re-derived here by evaluating both sides on random points). Outside
the ellipsoid E: sigma x^2 + y^2 + beta (z - c/2)^2 <= beta c^2 / 4, dV/dt < 0,
so the ball V <= max_E V is forward invariant and contains every omega-limit
set. max_E V is found on the ellipsoid surface by dense sampling and compared
with the SLSQP value of spectra.py."""

import numpy as np

rng = np.random.default_rng(0)
for sigma, r, beta in [(10.0, 28.0, 8 / 3), (10.0, 166.1, 8 / 3)]:
    c = sigma + r
    p = rng.normal(size=(100000, 3)) * 100
    x, y, z = p.T
    lhs = 2 * x * sigma * (y - x) + 2 * y * (x * (r - z) - y) + 2 * (z - c) * (x * y - beta * z)
    rhs = -2 * sigma * x**2 - 2 * y**2 - 2 * beta * (z - c / 2) ** 2 + beta * c**2 / 2
    print(f"sigma {sigma} r {r}: max |dV/dt identity residual| / scale = {np.max(np.abs(lhs - rhs)) / np.max(np.abs(lhs)):.2e}")
    # surface of E: parametrize by sphere directions
    u = rng.normal(size=(2_000_000, 3))
    u /= np.linalg.norm(u, axis=1, keepdims=True)
    a = np.sqrt(beta * c * c / 4) / np.sqrt([sigma, 1.0, beta])
    xs, ys, zs = u[:, 0] * a[0], u[:, 1] * a[1], u[:, 2] * a[2] + c / 2
    v = xs**2 + ys**2 + (zs - c) ** 2
    print(f"  max_E V by sampling {v.max():.2f} -> |x| <= sqrt = {np.sqrt(v.max()):.2f}; attained near z {zs[np.argmax(v)]:.2f}, y {ys[np.argmax(v)]:.2f}")
