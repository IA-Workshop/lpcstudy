"""MA-1 core: the influence series of H1a's fitted 1/d and of the H1a ratio (WU-0003, MA-1).

DEVELOPMENT: not a hypothesis test. No lpcstudy import (no JAX). The production fit is a verbatim
copy of ``lpcstudy.analysis._floor_power_law`` and ``_fit_seed_law`` (develop 0e9b892; identical
on wu/0003-rehearsal), except that it returns all three parameters (curve_fit's ``params``).

Model (theta = (a, b, c) = (log c^2, 2/d, log f^2), x = log n_lib, y_j = log median_j):
    g(x; theta) = log(exp(a - b x) + exp(c)),   p = exp(a - b x) / (exp(a - b x) + exp(c))
    dg/da = p, dg/db = -x p, dg/dc = 1 - p
    Hess_theta g = p (1 - p) v v^T,  v = (1, -x, -1)
Least squares F = 1/2 sum_j (g_j - y_j)^2; stationarity J^T r = 0, r = g - y. Implicit function
theorem: d theta / d y = H^{-1} J^T, H = J^T J + sum_j r_j p_j (1 - p_j) v_j v_j^T.
"""
import warnings
import numpy as np
from scipy.optimize import curve_fit, least_squares, OptimizeWarning

BOUNDS = (0.01, 10.0)
LO = np.array([-50.0, BOUNDS[0], -60.0])
HI = np.array([50.0, BOUNDS[1], 10.0])


def model(log_n, log_c2, exponent, log_f2):
    """Verbatim ``_floor_power_law``."""
    return np.log(np.exp(log_c2) * np.exp(log_n) ** (-exponent) + np.exp(log_f2))


def guess_of(sizes, mean_sq):
    log_n = np.log(sizes)
    return (np.log(mean_sq[0]) + 2 * 0.5 * log_n[0], 1.0, np.log(mean_sq[-1] * 0.5))


def fit_prod(sizes, mean_sq):
    """Verbatim ``_fit_seed_law`` (curve_fit, TRF, scipy default tolerances, 2-point Jacobian),
    returning all three parameters; NaN on RuntimeError."""
    log_n = np.log(sizes)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", OptimizeWarning)
            params, _ = curve_fit(model, log_n, np.log(mean_sq), p0=guess_of(sizes, mean_sq),
                                  bounds=(list(LO), list(HI)), maxfev=20_000)
    except RuntimeError:
        return np.full(3, np.nan)
    return np.asarray(params, dtype=float)


def frac(log_n, theta):
    a, b, c = theta
    s = a - b * log_n
    return 1.0 / (1.0 + np.exp(c - s))          # p = e^s / (e^s + e^c), stable


def jac(log_n, theta):
    p = frac(log_n, theta)
    return np.column_stack([p, -log_n * p, 1.0 - p])


def hessian(log_n, y, theta):
    """Exact Hessian of F = 1/2 ||g - y||^2: J^T J + sum r_j p_j (1 - p_j) v_j v_j^T."""
    J = jac(log_n, theta)
    p = frac(log_n, theta)
    r = model(log_n, *theta) - y
    V = np.column_stack([np.ones_like(log_n), -log_n, -np.ones_like(log_n)])
    return J.T @ J + (V * (r * p * (1 - p))[:, None]).T @ V


def fit_tight(sizes, mean_sq, x0=None):
    """The exact minimiser: TRF with the analytic Jacobian at tolerance 1e-15, then Newton steps
    on the gradient with the exact Hessian until the step is below 1e-15 relative."""
    log_n, y = np.log(sizes), np.log(mean_sq)
    x0 = np.array(guess_of(sizes, mean_sq)) if x0 is None else np.asarray(x0, float)
    res = least_squares(lambda t: model(log_n, *t) - y, x0, jac=lambda t: jac(log_n, t),
                        method="trf", bounds=(LO, HI), ftol=1e-15, xtol=1e-15, gtol=1e-15,
                        max_nfev=20_000)
    t = res.x.copy()
    for _ in range(20):
        g = jac(log_n, t).T @ (model(log_n, *t) - y)
        step = np.linalg.solve(hessian(log_n, y, t), g)
        t = t - step
        if np.max(np.abs(step) / np.maximum(1.0, np.abs(t))) < 1e-15:
            break
    return t


def dtheta_dy(sizes, mean_sq, theta):
    """d theta / d y (3 x nL) by the implicit function theorem, y = log(median)."""
    log_n, y = np.log(sizes), np.log(mean_sq)
    H = hessian(log_n, y, theta)
    return np.linalg.solve(H, jac(log_n, theta).T), np.linalg.cond(H), np.linalg.eigvalsh(H)


# ---------------------------------------------------------------- density of log X at its median
def g_sbg(ylog, h=None):
    """Siddiqui-Bloch-Gastwirth sparsity estimate of the density of Y at its median, with the
    Hall-Sheather bandwidth h = n^(-1/3) z^(2/3) (1.5 phi(0)^2)^(1/3), z = 1.96 (Koenker 2005,
    sec. 3.4.4): 1/g = (Y_(q=1/2+h) - Y_(q=1/2-h)) / (2h), with the empirical quantile by linear
    interpolation (numpy default)."""
    n = len(ylog)
    if h is None:
        h = n ** (-1 / 3) * 1.96 ** (2 / 3) * (1.5 * (1 / np.sqrt(2 * np.pi)) ** 2) ** (1 / 3)
    hi, lo = np.quantile(ylog, [0.5 + h, 0.5 - h])
    return 2 * h / (hi - lo)


def g_kde(ylog, at):
    """Gaussian kernel density of Y at ``at``, Silverman's bandwidth 0.9 min(sd, IQR/1.34) n^-1/5."""
    n = len(ylog)
    q75, q25 = np.quantile(ylog, [0.75, 0.25])
    bw = 0.9 * min(np.std(ylog, ddof=1), (q75 - q25) / 1.34) * n ** (-0.2)
    z = (ylog - at) / bw
    return float(np.exp(-0.5 * z * z).sum() / (n * bw * np.sqrt(2 * np.pi)))


def sign_type(x, m):
    """IF of a median up to 1/f: 1/2 - 1{x < m} - 1/2 1{x = m} (+1/2 above, -1/2 below)."""
    return 0.5 - (x < m) - 0.5 * (x == m)


def influence(seed_sq, inverse_dim, sizes, density="sbg", g_true=None, theta=None):
    """Influence series of the fitted 1/d and of the H1a ratio, per state (rows in time order).

    psi_inv_i   = sum_j A_j * s_ij / g_j,  A_j = (1/2) [d theta / d y]_{b, j}
    psi_ratio_i = (psi_inv_i - R (inverse_dim_i - mu)) / mu
    where s_ij = sign_type(seed_sq_ij, median_j), g_j the density of log seed_sq_.j at its median,
    mu = mean(inverse_dim), R = (b/2)/mu. ``theta`` (the fit at the sample medians) defaults to
    the tight refit started from the production fit.
    """
    med = np.median(seed_sq, axis=0)
    if theta is None:
        theta = fit_tight(sizes, med, x0=fit_prod(sizes, med))
    D, cond, eig = dtheta_dy(sizes, med, theta)
    A = 0.5 * D[1]
    ylog = np.log(seed_sq)
    if g_true is not None:
        g = np.asarray(g_true, float)
    elif density == "sbg":
        g = np.array([g_sbg(ylog[:, j]) for j in range(len(sizes))])
    else:
        g = np.array([g_kde(ylog[:, j], np.log(med[j])) for j in range(len(sizes))])
    S = sign_type(seed_sq, med[None, :])
    psi_inv = S @ (A / g)
    mu = inverse_dim.mean()
    R = 0.5 * theta[1] / mu
    psi_ratio = (psi_inv - R * (inverse_dim - mu)) / mu
    return dict(psi_inv=psi_inv, psi_ratio=psi_ratio, A=A, g=g, theta=theta, cond=cond,
                eig=eig, R=R, mu=mu, med=med)


def acf1(x):
    x = x - x.mean()
    return float((x[:-1] * x[1:]).sum() / (x * x).sum())


def beta5(phi):
    """M4.2 item 1: the block-5 factor of an AR(1) with lag-1 phi."""
    return (1 + 2 * sum((1 - k / 5) * phi ** k for k in range(1, 5))) * (1 - phi) / (1 + phi)
