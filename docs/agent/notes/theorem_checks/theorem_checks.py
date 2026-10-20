"""Executable checks for the LPC theorem program (L1-L11, P1-P3).

Each check verifies one statement of the theorem program (``theorem_program_lpc_v1.md``),
as amended by the v3 proposal (P1-P3), in one or more of three ways:

* **symbolic** - an algebraic identity proved by ``sympy`` simplification to 0;
* **property** - a randomized test of an inequality over many random instances
  (fixed seed), reporting the worst-case slack;
* **construction** - a counterexample or a tightness example built explicitly.

A numerical check is evidence, not a proof. The proofs are in the report; these checks
guard against algebra slips in the statements and the proofs, and fix the constants.

Run ``python3 theorem_checks.py`` to print a table and write ``theorem_checks.json``.
"""
from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np
import sympy as sp

MASTER_SEED = 20261020
RNG = np.random.default_rng(MASTER_SEED)
TOL = 1e-10


@dataclass
class CheckResult:
    """Outcome of one check.

    Attributes
    ----------
    item : str
        Theorem-program item, e.g. ``"P1(c) / L7(i)"``.
    claim : str
        The statement checked, in words.
    method : str
        ``symbolic``, ``property`` or ``construction``.
    passed : bool
        Whether the check passed.
    detail : dict
        Counts, worst-case slack and other numbers.
    """

    item: str
    claim: str
    method: str
    passed: bool
    detail: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Coerce sympy and NumPy booleans to a plain bool."""
        self.passed = bool(self.passed)


def is_zero(expr: sp.Expr) -> bool:
    """Return True if ``expr`` simplifies to exactly zero."""
    return sp.simplify(sp.expand(expr)) == 0


def random_gram(rng: np.random.Generator, size: int = 2) -> np.ndarray:
    """Return a random positive semidefinite Gram matrix of ``size`` random variables."""
    factor = rng.normal(size=(size, size + 1)) * rng.exponential(1.0, size=(size, 1))
    return factor @ factor.T


def hybrid_mse(w: np.ndarray, e_c: float, e_p: float, cross: float) -> np.ndarray:
    """Hybrid mean squared error V(w) = w^2 E_C + (1-w)^2 E_P + 2 w (1-w) C."""
    return w**2 * e_c + (1 - w) ** 2 * e_p + 2 * w * (1 - w) * cross


def best_hybrid(e_c: np.ndarray, e_p: np.ndarray, cross: np.ndarray) -> np.ndarray:
    """Minimum of V over w in [0, 1] (P1(a), (b)): V(u) inside, the smaller E at the clip."""
    clipped = cross >= np.minimum(e_c, e_p)
    curv = np.where(clipped, 1.0, e_c + e_p - 2 * cross)
    return np.where(clipped, np.minimum(e_c, e_p), (e_c * e_p - cross**2) / curv)


# ----------------------------------------------------------------------------- L1


def check_taylor_remainder() -> list[CheckResult]:
    """L1: first-order remainder bound and its quadratic scaling on the Lorenz-63 flow."""
    results = []
    # (a) generic F with a known Hessian bound: F(x) = sin(a.x) + 0.5 (b.x)^2.
    worst, n_cases = -np.inf, 4000
    for _ in range(n_cases):
        a, b = RNG.normal(size=3), RNG.normal(size=3)
        hess_bound = a @ a + b @ b
        x, xi = RNG.normal(size=3), RNG.normal(size=3) * RNG.exponential(0.5)
        value = lambda z: math.sin(a @ z) + 0.5 * (b @ z) ** 2  # noqa: E731
        grad = math.cos(a @ x) * a + (b @ x) * b
        remainder = abs(value(x + xi) - value(x) - grad @ xi)
        worst = max(worst, remainder - 0.5 * hess_bound * (xi @ xi))
    results.append(CheckResult(
        "L1", "|F(s+xi) - F(s) - grad F . xi| <= (M2/2)|xi|^2 for F with |D^2F| <= M2",
        "property", worst <= TOL, {"cases": n_cases, "max_excess": worst}))

    # (b) Lorenz-63 flow over 1 LT: remainder scales as |xi|^2 (log-log slope 2).
    state = lorenz_orbit_point()
    direction = RNG.normal(size=3)
    direction /= np.linalg.norm(direction)
    steps, step = 30, (1 / 0.905) / 30
    observe = lambda s: flow_lorenz(s, steps, step)[0]  # noqa: E731
    base = observe(state)
    eps_fd = 1e-6
    deriv = (observe(state + eps_fd * direction) - observe(state - eps_fd * direction)) / (2 * eps_fd)
    sizes = np.logspace(-4, -2, 7)
    remainders = [abs(observe(state + h * direction) - base - h * deriv) for h in sizes]
    slope = np.polyfit(np.log(sizes), np.log(remainders), 1)[0]
    results.append(CheckResult(
        "L1", "On the Lorenz-63 time-1-LT map the linearization remainder scales as |xi|^2",
        "property", abs(slope - 2) < 0.15, {"loglog_slope": slope}))
    return results


def lorenz_field(s: np.ndarray) -> np.ndarray:
    """Lorenz-63 vector field (sigma=10, r=28, b=8/3)."""
    x, y, z = s
    return np.array([10 * (y - x), x * (28 - z) - y, x * y - 8 / 3 * z])


def flow_lorenz(s: np.ndarray, steps: int, step: float, substeps: int = 10) -> np.ndarray:
    """Integrate Lorenz-63 by RK4 for ``steps`` observation intervals of length ``step``."""
    h = step / substeps
    for _ in range(steps * substeps):
        k1 = lorenz_field(s)
        k2 = lorenz_field(s + h / 2 * k1)
        k3 = lorenz_field(s + h / 2 * k2)
        k4 = lorenz_field(s + h * k3)
        s = s + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return s


def lorenz_orbit_point(spin_up: float = 20.0) -> np.ndarray:
    """Return a point near the Lorenz-63 attractor after a spin-up."""
    return flow_lorenz(np.array([1.0, 1.0, 20.0]), int(spin_up / 0.01), 0.01, 1)


# ----------------------------------------------------------------------------- L2, L3


def check_gauss_markov() -> list[CheckResult]:
    """L2: left inverses, the trace identity, Gauss-Markov and the noise covariance."""
    worst_psd, worst_trace, worst_left, n_cases = np.inf, 0.0, 0.0, 2000
    for _ in range(n_cases):
        jac = RNG.normal(size=(7, 3)) @ np.diag(RNG.exponential(1.0, 3))
        pinv = np.linalg.solve(jac.T @ jac, jac.T)
        null_part = RNG.normal(size=(3, 7)) @ (np.eye(7) - jac @ pinv)
        left = pinv + null_part
        worst_left = max(worst_left, np.abs(left @ jac - np.eye(3)).max())
        gap = left @ left.T - np.linalg.inv(jac.T @ jac)
        worst_psd = min(worst_psd, np.linalg.eigvalsh((gap + gap.T) / 2).min())
        sing = np.linalg.svd(jac, compute_uv=False)
        worst_trace = max(worst_trace, abs(np.trace(pinv @ pinv.T) / np.sum(sing**-2) - 1))
    results = [CheckResult(
        "L2(a)-(c)", "L J = I for L = J+ + Z (ZJ = 0); LL^T - (J^TJ)^-1 is PSD; "
        "tr(J+ J+^T) = sum sigma_j^-2", "property",
        worst_left < 1e-8 and worst_psd > -1e-8 and worst_trace < 1e-8,
        {"cases": n_cases, "max_left_inverse_error": worst_left,
         "min_eigenvalue_of_gap": worst_psd, "max_relative_trace_error": worst_trace})]
    # (d) Monte Carlo covariance of J+ eta.
    jac = RNG.normal(size=(7, 3))
    pinv = np.linalg.pinv(jac)
    rho, draws = 0.01, 400_000
    errors = (pinv @ (rho * RNG.normal(size=(7, draws)))).T
    target = rho**2 * np.linalg.inv(jac.T @ jac)
    rel = np.abs(np.cov(errors.T) - target).max() / np.abs(target).max()
    results.append(CheckResult(
        "L2(d)", "Cov(J+ eta) = rho^2 (J^TJ)^-1 for white noise of variance rho^2",
        "property", rel < 0.02, {"draws": draws, "max_relative_error": rel}))
    return results


def check_observability_invariance() -> list[CheckResult]:
    """L3: forward formula, and affine invariance of the whitened observability factor."""
    results = []
    worst_forward, n_cases = 0.0, 2000
    for _ in range(n_cases):
        a_mat, q_mat = RNG.normal(size=(7, 3)), RNG.normal(size=(3, 3))
        jac = a_mat @ np.linalg.inv(q_mat)
        lhs = np.linalg.inv(jac.T @ jac)
        rhs = q_mat @ np.linalg.inv(a_mat.T @ a_mat) @ q_mat.T
        worst_forward = max(worst_forward, np.abs(lhs - rhs).max() / np.abs(lhs).max())
    results.append(CheckResult(
        "L3", "J = A Q^-1 implies (J^TJ)^-1 = Q (A^TA)^-1 Q^T (no inverse of Q needed)",
        "property", worst_forward < 1e-6, {"cases": n_cases, "max_relative_error": worst_forward}))

    # Whitened nu^2 = tr[(J^TJ)^-1 C^-1]; under s' = A s + b: J' = J A^-1, C' = A C A^T.
    worst_affine = 0.0
    for _ in range(n_cases):
        jac = RNG.normal(size=(7, 3))
        cov = random_gram(RNG, 3) + 0.1 * np.eye(3)
        affine = RNG.normal(size=(3, 3))
        nu_sq = np.trace(np.linalg.inv(jac.T @ jac) @ np.linalg.inv(cov))
        jac_new, cov_new = jac @ np.linalg.inv(affine), affine @ cov @ affine.T
        nu_new = np.trace(np.linalg.inv(jac_new.T @ jac_new) @ np.linalg.inv(cov_new))
        worst_affine = max(worst_affine, abs(nu_new - nu_sq) / nu_sq)
    results.append(CheckResult(
        "L3 (strengthened)", "Whitened nu^2 = tr[(J^TJ)^-1 C^-1] is invariant under every invertible "
        "affine change of state coordinates (not only orthogonal ones)", "property",
        worst_affine < 1e-6, {"cases": n_cases, "max_relative_change": worst_affine}))

    # The program's literal form tr[W (J^TJ)^-1 W^T] with W -> U W is NOT affine-invariant.
    jac, white = RNG.normal(size=(7, 3)), RNG.normal(size=(3, 3))
    shear = np.array([[1.0, 2.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    before = np.trace(white @ np.linalg.inv(jac.T @ jac) @ white.T)
    jac_new = jac @ np.linalg.inv(shear)
    after = np.trace(shear @ white @ np.linalg.inv(jac_new.T @ jac_new) @ white.T @ shear.T)
    results.append(CheckResult(
        "L3 (literal form)", "tr[W(J^TJ)^-1W^T] with W -> UW changes under a shear U "
        "(why the v1 erratum restricted it to orthogonal U)", "construction",
        abs(after - before) / before > 1e-3, {"before": before, "after": after}))
    return results


# ----------------------------------------------------------------------------- L4


def check_delay_bound() -> list[CheckResult]:
    """L4: delay-space distance bounds the latent mismatch inside the local radius."""
    worst, n_cases, n_used = -np.inf, 3000, 0
    for _ in range(n_cases):
        lin = RNG.normal(size=(7, 3))
        quad = RNG.normal(size=(7, 3, 3))
        quad = (quad + quad.transpose(0, 2, 1)) / 2
        curv = RNG.exponential(0.3)
        delay_map = lambda s: lin @ s + 0.5 * curv * np.einsum("ijk,j,k->i", quad, s, s)  # noqa: E731
        hess_bound = curv * math.sqrt(sum(np.linalg.norm(q, 2) ** 2 for q in quad))
        s = RNG.normal(size=3)
        jac = lin + curv * np.einsum("ijk,k->ij", quad, s)
        sigma_min = np.linalg.svd(jac, compute_uv=False).min()
        radius = sigma_min / hess_bound
        direction = RNG.normal(size=3)
        a = s + direction / np.linalg.norm(direction) * radius * RNG.uniform(0, 1)
        eta_t, eta_a = RNG.normal(size=7) * 0.01, RNG.normal(size=7) * 0.01
        recurrence = np.linalg.norm(delay_map(s) + eta_t - delay_map(a) - eta_a)
        bound = 2 * (recurrence + np.linalg.norm(eta_t - eta_a)) / sigma_min
        worst = max(worst, np.linalg.norm(a - s) - bound)
        n_used += 1
    return [CheckResult(
        "L4", "|a - s| <= 2 (R + |eta_t - eta_a|) / sigma_m whenever |a - s| <= sigma_m / L2",
        "property", worst <= TOL, {"cases": n_used, "max_excess": worst})]


# ----------------------------------------------------------------------------- P1 = L5 + L7


def check_optimal_weight() -> list[CheckResult]:
    """P1(a), (b) / L5: completing the square, strict convexity, the clip and the iff."""
    w, e_c, e_p, cross = sp.symbols("w E_C E_P C", real=True)
    curvature = e_c + e_p - 2 * cross
    centre = (e_p - cross) / curvature
    mse = w**2 * e_c + (1 - w) ** 2 * e_p + 2 * w * (1 - w) * cross
    v_at_centre = (e_c * e_p - cross**2) / curvature
    results = [CheckResult(
        "P1(a) / L5", "V(w) = c (w - u)^2 + V(u), with V(u) = (E_C E_P - C^2)/c", "symbolic",
        is_zero(mse - (curvature * (w - centre) ** 2 + v_at_centre))
        and is_zero(mse.subs(w, centre) - v_at_centre))]

    # Copied noise: e_C = a + xi with xi orthogonal to a and e_P => c >= rho^2/k.
    grid = np.linspace(0, 1, 20001)
    worst_curv, worst_min, worst_iff, n_cases = np.inf, 0.0, 0, 5000
    for _ in range(n_cases):
        gram = random_gram(RNG)  # moments of (a, e_P)
        copied = RNG.exponential(0.2)  # E[xi^2] = rho^2/k
        mc, mp, mx = gram[0, 0] + copied, gram[1, 1], gram[0, 1]
        curv = mc + mp - 2 * mx
        worst_curv = min(worst_curv, curv - copied)
        u = (mp - mx) / curv
        clipped = min(max(u, 0.0), 1.0)
        grid_min = hybrid_mse(grid, mc, mp, mx).min()
        worst_min = max(worst_min, hybrid_mse(np.array(clipped), mc, mp, mx) - grid_min)
        inside = 0 <= u <= 1
        worst_iff += inside != (mx <= min(mc, mp) + 1e-14)
    results.append(CheckResult(
        "P1(a) / L5", "With copied noise orthogonal to e_P and e_C - xi: c >= rho^2/k > 0, "
        "and clip(u) minimizes V on [0, 1]", "property",
        worst_curv >= -TOL and worst_min <= 1e-9,
        {"cases": n_cases, "min_of_c_minus_copied": worst_curv,
         "max_gap_clip_vs_grid_min": worst_min}))
    results.append(CheckResult(
        "P1(b)", "u lies in [0, 1] iff C <= min(E_C, E_P)", "property", worst_iff == 0,
        {"cases": n_cases, "mismatches": int(worst_iff)}))
    return results


def check_blending_limit() -> list[CheckResult]:
    """P1(c), (e) / L7(i), (iv): the factor-1/2 floor and its counterexample."""
    e_c, e_p, cross = sp.symbols("E_C E_P C", real=True)
    curvature = e_c + e_p - 2 * cross
    proof_identity = 2 * (e_c * e_p - cross**2) - e_c * curvature - (
        e_c * (e_p - e_c) + 2 * cross * (e_c - cross))
    results = [CheckResult(
        "P1(c) proof step", "2V(u) - E_C = E_C(E_P - E_C) + 2C(E_C - C), times c > 0",
        "symbolic", is_zero(proof_identity))]
    grid = np.linspace(0, 1, 20001)
    worst, n_cases, n_kept = np.inf, 20000, 0
    for _ in range(n_cases):
        gram = random_gram(RNG)
        if gram[0, 1] < 0:
            continue
        n_kept += 1
        floor = 0.5 * min(gram[0, 0], gram[1, 1])
        worst = min(worst, hybrid_mse(grid, gram[0, 0], gram[1, 1], gram[0, 1]).min() - floor)
    results.append(CheckResult(
        "P1(c) / L7(i)", "C >= 0 implies min over [0,1] of V >= (1/2) min(E_C, E_P)",
        "property", worst >= -1e-12, {"cases_with_C_nonneg": n_kept, "min_slack": worst}))
    tight = hybrid_mse(np.array(0.5), 1.0, 1.0, 0.0)
    results.append(CheckResult(
        "P1(c) tightness", "Equality at E_C = E_P, C = 0 (independent, equal errors): min V = 1/2",
        "construction", abs(tight - 0.5) < 1e-15, {"min_V": float(tight)}))
    counter = hybrid_mse(grid, 1.0, 1.0, -1.0).min()
    results.append(CheckResult(
        "P1(e) / L7(iv)", "E_C = E_P = 1, C = -1 (e_C = -e_P) gives min V = 0", "construction",
        abs(counter) < 1e-12, {"min_V": float(counter)}))
    return results


def first_passage(curve: np.ndarray, level: float) -> int | None:
    """Return the first index at which ``curve`` exceeds ``level`` (None if censored)."""
    above = np.nonzero(curve > level)[0]
    return int(above[0]) if above.size else None


def check_horizon_gain() -> list[CheckResult]:
    """P1(d) / L7(ii)-(iii), plus the new tolerance-ratio form of the gain bound."""
    results = []
    lam, ratio = sp.symbols("Lambda r", positive=True)
    gain_exact = sp.log(1 + ratio**2) / (2 * lam)
    results.append(CheckResult(
        "L7(iii)", "Uncorrelated proportional seeds: gain = ln(1 + r^2) / (2 Lambda), "
        "maximal (= ln 2 / (2 Lambda)) at r = 1", "symbolic",
        is_zero(gain_exact.subs(ratio, 1) - sp.log(2) / (2 * lam))
        and sp.diff(gain_exact, ratio).subs({ratio: sp.Rational(1, 2), lam: 1}) > 0))

    # Continuous-exponential version on a fine grid.
    horizons = np.linspace(0, 20, 200_001)
    worst_exp, n_cases = -np.inf, 2000
    for _ in range(n_cases):
        growth = RNG.uniform(0.2, 3.0)
        seed_c, seed_p = RNG.exponential(0.01, 2)
        corr = RNG.uniform(0, 1)
        amp = np.exp(2 * growth * horizons)
        e_c, e_p = seed_c**2 * amp, seed_p**2 * amp
        cross = corr * seed_c * seed_p * amp
        hybrid = best_hybrid(e_c, e_p, cross)
        tol = RNG.uniform(0.05, 0.5)
        t_best = first_passage(np.minimum(e_c, e_p), tol**2)
        t_hyb = first_passage(hybrid, tol**2)
        if t_best is None or t_hyb is None:
            continue
        gain = horizons[t_hyb] - horizons[t_best]
        worst_exp = max(worst_exp, gain - math.log(2) / (2 * growth))
    results.append(CheckResult(
        "P1(d) / L7(ii)", "Exponential growth and C >= 0: horizon gain <= ln 2 / (2 Lambda)",
        "property", worst_exp <= 1e-3, {"cases": n_cases, "max_excess": worst_exp}))

    # New form: gain <= T_env(sqrt2 * tol) - T_env(tol), any growth shape, C >= 0 at one step.
    worst_ratio, worst_lambda_form, n_cases, n_violate_lambda = -np.inf, -np.inf, 4000, 0
    steps = np.arange(241)
    for _ in range(n_cases):
        envelope = random_envelope(steps)
        other = envelope * RNG.uniform(1.0, 3.0, size=steps.size)  # the worse forecaster
        corr = RNG.uniform(0, 1, size=steps.size)
        cross = corr * envelope * other
        e_best, e_worse = envelope**2, other**2
        hybrid = best_hybrid(e_best, e_worse, cross)
        tol = RNG.uniform(0.05, 0.6)
        t_env = first_passage(e_best, tol**2)
        t_env_wide = first_passage(e_best, 2 * tol**2)
        t_hyb = first_passage(hybrid, tol**2)
        if t_env is None or t_env_wide is None or t_hyb is None:
            continue
        worst_ratio = max(worst_ratio, (t_hyb - t_env) - (t_env_wide - t_env))
        # The ln2/(2 Lambda_bar) screen with Lambda fitted over the first 30 steps can fail here.
        lam_fit = np.polyfit(steps[1:31], np.log(envelope[1:31]), 1)[0]
        if lam_fit > 0 and (t_hyb - t_env) > math.log(2) / (2 * lam_fit) + 1:
            n_violate_lambda += 1
    results.append(CheckResult(
        "P1(d') new", "Any growth shape, C >= 0 at the single step T_env(sqrt2 tol): "
        "gain over the better-forecaster envelope <= T_env(sqrt2 tol) - T_env(tol)",
        "property", worst_ratio <= 0,
        {"cases": n_cases, "max_excess_steps": worst_ratio,
         "cases_where_ln2_over_2Lambda_screen_fails": n_violate_lambda}))

    # Construction: fast early growth, slow growth at the crossing. The ln2/(2 Lambda_bar)
    # screen (Lambda fitted over the first 1 LT) is far exceeded; P1(d') is exact.
    envelope = 0.01 * np.exp(np.where(steps <= 60, 0.05 * steps, 3.0 + 0.004 * (steps - 60)))
    e_best = envelope**2
    hybrid = best_hybrid(e_best, e_best, np.zeros_like(e_best))  # equal, uncorrelated: = e/2
    tol = 0.21
    t_env, t_wide = first_passage(e_best, tol**2), first_passage(e_best, 2 * tol**2)
    t_hyb = first_passage(hybrid, tol**2)
    lam_fit = np.polyfit(steps[1:31], np.log(envelope[1:31]), 1)[0]
    results.append(CheckResult(
        "P1(d) vs P1(d')", "Two-phase growth (fast for 2 LT, then slow): the gain far exceeds "
        "ln2/(2 Lambda_bar) from the first LT, and equals the P1(d') bound", "construction",
        t_hyb - t_env == t_wide - t_env and (t_hyb - t_env) > math.log(2) / (2 * lam_fit) + 1,
        {"gain_steps": t_hyb - t_env, "p1d_prime_bound_steps": t_wide - t_env,
         "ln2_over_2Lambda_bar_steps": math.log(2) / (2 * lam_fit)}))
    return results


def random_envelope(steps: np.ndarray) -> np.ndarray:
    """Return a random increasing, saturating r.m.s. error curve (not exponential)."""
    rate = RNG.uniform(0.01, 0.08)
    seed = RNG.exponential(0.01) + 1e-4
    saturation = RNG.uniform(0.5, 1.5)
    wiggle = 1 + 0.3 * np.sin(steps * RNG.uniform(0.02, 0.2)) * RNG.uniform(0, 1)
    raw = seed * np.exp(rate * steps * wiggle)
    return np.maximum.accumulate(saturation * raw / np.sqrt(saturation**2 + raw**2))


# ----------------------------------------------------------------------------- L6


def check_separation() -> list[CheckResult]:
    """L6: scale invariance of w*, the copied-noise transient, and anisotropy."""
    results = []
    q, eps, dlt, kap, noise = sp.symbols("q epsilon delta kappa n", positive=True)

    def weight(v_a: sp.Expr, v_s: sp.Expr, v_k: sp.Expr) -> sp.Expr:
        return (v_s - v_k) / (v_a + v_s - 2 * v_k)

    invariant = weight(eps**2 * q, dlt**2 * q, kap * q) - weight(eps**2, dlt**2, kap)
    results.append(CheckResult(
        "L6", "Proportional seed covariances: w* is the same at every horizon (q_H cancels)",
        "symbolic", is_zero(invariant)))
    transient = (dlt**2 * q - kap * q) / ((eps**2 + dlt**2 - 2 * kap) * q + noise)
    deriv = sp.simplify(sp.diff(transient, q))
    deriv_expected = (dlt**2 - kap) * noise / ((eps**2 + dlt**2 - 2 * kap) * q + noise) ** 2
    limit = sp.limit(transient, q, sp.oo)
    results.append(CheckResult(
        "L6 transient", "With copied noise n = rho^2/k: dw*/dq_H = (delta^2 - kappa) n / (...)^2 "
        "> 0 when delta^2 > kappa, and w* -> (delta^2 - kappa)/(eps^2 + delta^2 - 2 kappa)",
        "symbolic", is_zero(deriv - deriv_expected)
        and is_zero(limit - (dlt**2 - kap) / (eps**2 + dlt**2 - 2 * kap))))

    # Anisotropy: when Sigma_a is not proportional to Sigma_s, w* depends on the direction of
    # the amplifier Gamma_H, i.e. on horizon and instability (why H2a can fail).
    spread_iso, spread_aniso = [], []
    for _ in range(500):
        shape = random_gram(RNG, 3) + 0.05 * np.eye(3)
        e2, d2 = RNG.exponential(1.0, 2)
        aniso = random_gram(RNG, 3) + 0.05 * np.eye(3)
        weights_iso, weights_aniso = [], []
        for _ in range(50):
            gamma = RNG.normal(size=3)
            q_h = gamma @ shape @ gamma
            weights_iso.append(d2 * q_h / ((e2 + d2) * q_h))
            v_a, v_s = gamma @ (e2 * aniso) @ gamma, gamma @ (d2 * shape) @ gamma
            weights_aniso.append(v_s / (v_a + v_s))
        spread_iso.append(np.ptp(weights_iso))
        spread_aniso.append(np.ptp(weights_aniso))
    results.append(CheckResult(
        "L6 (hypothesis)", "Proportional covariances: w* range over amplifier directions is 0; "
        "random anisotropic seeds: it is not", "construction",
        max(spread_iso) < 1e-12 and np.median(spread_aniso) > 0.05,
        {"max_range_proportional": float(max(spread_iso)),
         "median_range_anisotropic": float(np.median(spread_aniso))}))
    return results


# ----------------------------------------------------------------------------- L8, L8', L9


def check_horizon_law() -> list[CheckResult]:
    """L8: the law, its slope in ln(theta), the bracket and the discrete first passage."""
    results = []
    lam, tol, seed = sp.symbols("Lambda theta e0", positive=True)
    horizon = sp.log(tol / seed) / lam
    results.append(CheckResult(
        "L8", "g_H = e^(Lambda H): T = ln(theta'/e0)/Lambda, so dT/d ln(theta) = 1/Lambda",
        "symbolic", is_zero(sp.diff(horizon, tol) * tol - 1 / lam)))
    worst, n_cases = -np.inf, 3000
    for _ in range(n_cases):
        rate, slack = RNG.uniform(0.05, 1.0), RNG.uniform(0, 0.04)
        rate_low, rate_high = rate - slack, rate + slack
        e0, level = RNG.exponential(0.005) + 1e-5, RNG.uniform(0.05, 0.5)
        steps = np.arange(1, 4000)
        wobble = RNG.uniform(-1, 1) * slack * steps * np.sin(steps * RNG.uniform(0.05, 1.0))
        log_gain = np.clip(rate * steps + wobble, rate_low * steps, rate_high * steps)
        passage = first_passage(e0 * np.exp(log_gain), level)
        if passage is None:
            continue
        t_obs = steps[passage]
        lower = math.log(level / e0) / rate_high
        upper = math.log(level / e0) / rate_low + 1
        worst = max(worst, lower - t_obs, t_obs - upper)
    results.append(CheckResult(
        "L8 bracket", "(Lambda - e)H <= ln g_H <= (Lambda + e)H implies "
        "ln(theta'/e0)/(Lambda+e) <= T <= ln(theta'/e0)/(Lambda-e) (+1 step, discrete)",
        "property", worst <= TOL, {"cases": n_cases, "max_excess": worst}))
    return results


def check_certified_horizon() -> list[CheckResult]:
    """L8': the Gronwall horizon on Lorenz-63, and how short it is against 1 LT."""
    orbit = [lorenz_orbit_point()]
    for _ in range(4000):
        orbit.append(flow_lorenz(orbit[-1], 1, 0.01, 1))
    orbit = np.array(orbit)
    lo, hi = orbit.min(axis=0) - 2, orbit.max(axis=0) + 2

    def jacobian_norm(s: np.ndarray) -> float:
        x, y, z = s
        jac = np.array([[-10, 10, 0], [28 - z, -1, -x], [y, x, -8 / 3]])
        return np.linalg.norm(jac, 2)

    # Upper bound of |Df|_2 on the box by the Frobenius norm at the box's worst corner.
    corners = np.array(np.meshgrid(*zip(lo, hi), indexing="ij")).reshape(3, -1).T
    lipschitz = max(math.sqrt(100 + 100 + (28 - z) ** 2 + 1 + x**2 + y**2 + x**2 + (8 / 3) ** 2)
                    for x, y, z in corners)
    sigma_x = orbit[:, 0].std()
    seed_size, level = 0.01 * sigma_x, 0.2 * sigma_x  # 1% of sigma_x, theta = 0.2
    certified = math.log(level / seed_size) / lipschitz
    # Empirical check: the bound |x-error(t)| <= |xi| e^(L t) on sampled pairs inside the box.
    worst, n_pairs = -np.inf, 200
    for start in orbit[RNG.integers(0, len(orbit), n_pairs)]:
        xi = RNG.normal(size=3)
        xi *= seed_size / np.linalg.norm(xi)
        a, b = start.copy(), start + xi
        for k in range(1, 101):
            a, b = flow_lorenz(a, 1, 0.001, 1), flow_lorenz(b, 1, 0.001, 1)
            inside = np.all((a > lo) & (a < hi) & (b > lo) & (b < hi))
            if inside:
                worst = max(worst, np.linalg.norm(a - b) - seed_size * math.exp(lipschitz * k * 0.001))
    lyapunov_time = 1 / 0.905
    return [CheckResult(
        "L8'", "Gronwall: |error(t)| <= |xi| e^(L_K t) on a convex box containing both orbits; "
        "certified horizon ln(theta/|xi|)/L_K", "property", worst <= 1e-12,
        {"L_K_box_bound": lipschitz, "lambda_max": 0.905,
         "certified_horizon_LT": certified / lyapunov_time,
         "linearized_horizon_LT": math.log(level / seed_size) / 0.905 / lyapunov_time,
         "max_excess_sampled": worst})]


def check_growth_exponents() -> list[CheckResult]:
    """L9: mean of logs <= log of mean, equality iff all growth factors are equal."""
    worst, n_cases = -np.inf, 5000
    for _ in range(n_cases):
        gains = RNG.lognormal(0, RNG.uniform(0, 2), size=RNG.integers(2, 50))
        worst = max(worst, np.mean(np.log(gains**2)) - math.log(np.mean(gains**2)))
    equal = np.full(10, 3.7)
    gap_equal = abs(np.mean(np.log(equal**2)) - math.log(np.mean(equal**2)))
    return [CheckResult(
        "L9", "(1/2H) mean ln g_i^2 <= (1/2H) ln mean g_i^2, equality iff all g_i equal",
        "property", worst <= TOL and gap_equal < 1e-12,
        {"cases": n_cases, "max_excess": worst, "gap_when_equal": gap_equal})]


# ----------------------------------------------------------------------------- P3 = L10


def check_regime_regret() -> list[CheckResult]:
    """P3 / L10: the regret identity, the regime weight, the bound, the rate, the floor."""
    results = []
    w, c, u, v0 = sp.symbols("w c u V0", real=True)
    results.append(CheckResult(
        "L10(i) corrected", "V_i(w) - V_i(u_i) = c_i (w - u_i)^2 with the UNCLIPPED u_i",
        "symbolic", is_zero((c * (w - u) ** 2 + v0) - (c * (u - u) ** 2 + v0) - c * (w - u) ** 2)))
    # The v1 form with the clipped w* is false: u = 1.4, w* = 1, w = 0.
    curv, centre = 1.0, 1.4
    exact = curv * (0 - centre) ** 2 - curv * (1 - centre) ** 2  # V(0) - V(w*)
    v1_form = curv * (0 - 1) ** 2
    results.append(CheckResult(
        "L10(i) as in v1", "V(w) - V(w*) = c (w - w*)^2 with CLIPPED w* fails: u = 1.4, w = 0 "
        "gives excess 1.80, the v1 form gives 1.00 (understated)", "construction",
        abs(exact - 1.8) < 1e-12 and abs(v1_form - 1.0) < 1e-12,
        {"exact_excess": exact, "v1_excess": v1_form}))

    grid = np.linspace(0, 1, 20001)
    worst_weight, worst_bound, n_cases = 0.0, -np.inf, 3000
    for _ in range(n_cases):
        size = RNG.integers(2, 40)
        curvs, centres = RNG.exponential(1.0, size), RNG.normal(0.5, 0.8, size)
        totals = (curvs[:, None] * (grid[None, :] - centres[:, None]) ** 2).sum(axis=0)
        regime = min(max(curvs @ centres / curvs.sum(), 0.0), 1.0)
        total_at = (curvs * (regime - centres) ** 2).sum()
        worst_weight = max(worst_weight, total_at - totals.min())
        # (iii): mean regret <= eps_w^2 max c, when |w_k - u_i| <= eps_w.
        eps_w = np.abs(regime - centres).max()
        worst_bound = max(worst_bound, np.mean(curvs * (regime - centres) ** 2)
                          - eps_w**2 * curvs.max())
    results.append(CheckResult(
        "P3(a) / L10(ii)", "The regime weight clip(sum c_i u_i / sum c_i) minimizes "
        "sum_i V_i(w) on [0, 1]", "property", worst_weight <= 1e-8,
        {"cases": n_cases, "max_gap_vs_grid": worst_weight}))
    results.append(CheckResult(
        "L10(iii)", "|w_k - u_i| <= eps_w on the regime implies mean regret <= eps_w^2 max c_i",
        "property", worst_bound <= TOL, {"cases": n_cases, "max_excess": worst_bound}))

    # (iv) grid rate for a Lipschitz target on [0,1]^p.
    worst_rate = -np.inf
    for dim in (1, 2, 3):
        for cells in (2, 4, 8):
            lip = RNG.uniform(0.5, 3)
            points = RNG.uniform(size=(4000, dim))
            target = 0.5 + 0.5 * np.sin(lip * points.sum(axis=1) / math.sqrt(dim)) / 1.0
            true_lip = lip / math.sqrt(dim) * 0.5 * math.sqrt(dim)  # |grad| <= lip/2
            curvs = RNG.exponential(1.0, 4000)
            labels = np.minimum((points * cells).astype(int), cells - 1)
            keys = np.ravel_multi_index(labels.T, (cells,) * dim)
            regret = 0.0
            for key in np.unique(keys):
                mask = keys == key
                weight = curvs[mask] @ target[mask] / curvs[mask].sum()
                regret += (curvs[mask] * (weight - target[mask]) ** 2).sum()
            bound = curvs.max() * true_lip**2 * dim / cells**2
            worst_rate = max(worst_rate, regret / 4000 - bound)
    results.append(CheckResult(
        "L10(iv)", "L-Lipschitz w* on a grid of K = n^p cells: mean regret <= c_max L^2 p K^(-2/p)",
        "property", worst_rate <= TOL, {"max_excess": worst_rate}))

    # P3(b) measurability floor: no function of a discrete profile F beats clip(E[cu|F]/E[c|F]).
    worst_floor, n_cases = np.inf, 300
    for _ in range(n_cases):
        n_profile = RNG.integers(1, 6)
        profile = RNG.integers(0, n_profile, 400)
        curvs, centres = RNG.exponential(1.0, 400), RNG.normal(0.4, 0.6, 400)
        floor_rule = np.empty(400)
        for value in range(n_profile):
            mask = profile == value
            if mask.any():
                floor_rule[mask] = np.clip(curvs[mask] @ centres[mask] / curvs[mask].sum(), 0, 1)
        floor = np.mean(curvs * (floor_rule - centres) ** 2)
        for _ in range(20):  # random competitor rules that see only F
            table = RNG.uniform(0, 1, n_profile)
            worst_floor = min(worst_floor, np.mean(curvs * (table[profile] - centres) ** 2) - floor)
    results.append(CheckResult(
        "P3(b)", "Every rule that is a function of the profile F has mean excess >= that of "
        "clip(E[c u | F] / E[c | F])", "property", worst_floor >= -TOL,
        {"cases": n_cases * 20, "min_slack": worst_floor}))
    return results


# ----------------------------------------------------------------------------- P2 = L11


def nearest_index(library: np.ndarray, query: np.ndarray) -> np.ndarray:
    """Return the nearest library index for each query row."""
    dist = ((query[:, None, :] - library[None, :, :]) ** 2).sum(axis=2)
    return dist.argmin(axis=1)


def check_retrieval_stability() -> list[CheckResult]:
    """P2 / L11(b): stability, its tightness, the Markov bound and the spread bound."""
    results = []
    dim = 7
    n_switch_small, n_cases = 0, 3000
    for _ in range(n_cases):
        library = RNG.normal(size=(RNG.integers(5, 200), dim))
        query = RNG.normal(size=dim)
        dist = np.sort(np.linalg.norm(library - query, axis=1))
        margin = dist[1] - dist[0]
        eta = RNG.normal(size=dim)
        eta *= RNG.uniform(0, 0.999999) * margin / 2 / np.linalg.norm(eta)
        base = nearest_index(library, query[None])[0]
        n_switch_small += nearest_index(library, (query + eta)[None])[0] != base
    results.append(CheckResult(
        "P2(a) / L11(b)(i)", "|eta| < Delta/2 never changes the retrieved analog", "property",
        n_switch_small == 0, {"cases": n_cases, "switches": int(n_switch_small)}))
    library = np.array([[1.0] + [0] * 6, [-1.3] + [0] * 6])  # r1 = 1, r2 = 1.3, Delta = 0.3
    eta = np.array([-(0.15 + 1e-9)] + [0] * 6)
    results.append(CheckResult(
        "P2(a) tightness", "Collinear library: |eta| = Delta/2 + 1e-9 toward the runner-up "
        "switches the analog, so the constant 1/2 cannot be improved", "construction",
        nearest_index(library, eta[None])[0] == 1))

    worst_markov, worst_spread, n_states, rho = -np.inf, -np.inf, 400, 0.05
    for _ in range(n_states):
        library = RNG.normal(size=(RNG.integers(20, 400), dim)) * RNG.uniform(0.2, 1.0)
        query = RNG.normal(size=dim) * 0.5
        dist = np.sort(np.linalg.norm(library - query, axis=1))
        r1, margin = dist[0], dist[1] - dist[0]
        noise = rho * RNG.normal(size=(1000, dim))
        idx = nearest_index(library, query + noise)
        base = nearest_index(library, query[None])[0]
        switch_rate = np.mean(idx != base)
        worst_markov = max(worst_markov, switch_rate - min(1.0, 4 * dim * rho**2 / margin**2))
        retrieved = library[idx]
        spread_sq = np.mean(((retrieved - retrieved.mean(axis=0)) ** 2).sum(axis=1)) / (rho**2 * dim)
        norms = np.linalg.norm(noise, axis=1)
        bound = 4 / (rho**2 * dim) * np.mean((r1 + norms) ** 2 * (norms >= margin / 2))
        worst_spread = max(worst_spread, spread_sq - bound)
    results.append(CheckResult(
        "P2(b) / L11(b)(ii)", "Pr(retrieval changes) <= Pr(|eta| >= Delta/2) <= 4 D rho^2 / Delta^2",
        "property", worst_markov <= 0.01,
        {"states": n_states, "draws_per_state": 1000, "max_excess_rate": worst_markov}))
    results.append(CheckResult(
        "P2(c) / L11(b)(iii)", "N^2 <= (4/(rho^2 D)) E[(r1 + |eta|)^2 1{|eta| >= Delta/2}] "
        "(exact for the empirical law of the draws)", "property", worst_spread <= TOL,
        {"states": n_states, "max_excess": worst_spread}))

    # L11(a): PLP-side noise sensitivity rho |Gamma J+| <= rho g_H nu, with nu = |J+|_F.
    worst_plp = -np.inf
    for _ in range(3000):
        jac, gamma = RNG.normal(size=(7, 3)), RNG.normal(size=3)
        pinv = np.linalg.pinv(jac)
        worst_plp = max(worst_plp, np.linalg.norm(gamma @ pinv)
                        - np.linalg.norm(gamma) * math.sqrt(np.trace(np.linalg.inv(jac.T @ jac))))
    results.append(CheckResult(
        "L11(a)", "PLP noise sensitivity |Gamma_H J+| <= g_H nu: a function of observability "
        "and amplification only", "property", worst_plp <= TOL, {"max_excess": worst_plp}))
    return results


# ----------------------------------------------------------------------------- driver

CHECKS: list[Callable[[], list[CheckResult]]] = [
    check_taylor_remainder, check_gauss_markov, check_observability_invariance,
    check_delay_bound, check_optimal_weight, check_blending_limit, check_horizon_gain,
    check_separation, check_horizon_law, check_certified_horizon, check_growth_exponents,
    check_regime_regret, check_retrieval_stability,
]


def run_all() -> list[CheckResult]:
    """Run every check and return the results in program order."""
    results: list[CheckResult] = []
    for check in CHECKS:
        results.extend(check())
    return results


def main() -> None:
    """Run the suite, print a summary table and write the JSON record."""
    results = run_all()
    for res in results:
        print(f"{'PASS' if res.passed else 'FAIL'}  {res.method:12s}  {res.item:22s}  {res.claim}")
        if res.detail:
            print(" " * 6, json.dumps(res.detail, default=float))
    n_pass = sum(r.passed for r in results)
    print(f"\n{n_pass}/{len(results)} checks passed (seed {MASTER_SEED}).")
    out = Path(__file__).with_name("theorem_checks.json")
    out.write_text(json.dumps({"seed": MASTER_SEED, "results": [asdict(r) for r in results]},
                              indent=1, default=float))


if __name__ == "__main__":
    main()
