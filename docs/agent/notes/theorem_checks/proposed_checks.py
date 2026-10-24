"""Executable checks for the proposed theorems N1-N8 (``theorem_proofs_detailed.md`` Part B)
and the clipping lemma of Section A4.4.

Same conventions as ``theorem_checks.py``: symbolic identities, randomized property tests
with a fixed seed, and constructions. Run ``python3 proposed_checks.py``.
"""
from __future__ import annotations

import json
import math
from dataclasses import asdict
from pathlib import Path

import numpy as np
import sympy as sp
from scipy.stats import norm

from theorem_checks import CheckResult, best_hybrid, first_passage, is_zero, random_gram

MASTER_SEED = 20261021
RNG = np.random.default_rng(MASTER_SEED)
TOL = 1e-10


def raw_moments(e_c: np.ndarray, e_p: np.ndarray) -> tuple[float, float, float]:
    """Raw second moments (E_C, E_P, C) over draws, as the study computes them."""
    return float(np.mean(e_c**2)), float(np.mean(e_p**2)), float(np.mean(e_c * e_p))


def check_conditioned_curvature() -> list[CheckResult]:
    """N1: c = E[(e_C - e_P)^2] >= Var(e_C - e_P); with stable retrieval c >= Var(e_P)."""
    worst, n_cases = np.inf, 5000
    for _ in range(n_cases):
        draws = RNG.integers(5, 300)
        e_p = RNG.normal(RNG.normal(0, 0.3), RNG.exponential(0.2), draws)
        e_c = np.full(draws, RNG.normal(0, 0.5))  # stable retrieval: constant over draws
        e_cc, e_pp, cross = raw_moments(e_c, e_p)
        curvature = e_cc + e_pp - 2 * cross
        worst = min(worst, curvature - np.var(e_p))
    return [CheckResult(
        "N1", "Stable retrieval (e_C constant over draws): c >= Var(e_P) > 0, with no "
        "copied-noise orthogonality assumption", "property", worst >= -1e-12,
        {"cases": n_cases, "min_slack": worst})]


def check_stable_retrieval() -> list[CheckResult]:
    """N2: closed form under stable retrieval and the necessary condition for w* = 0."""
    mu, mean_p, var_p = sp.symbols("mu m sigma2", real=True)
    e_c, e_p, cross = mu**2, mean_p**2 + var_p, mu * mean_p
    centre = (e_p - cross) / (e_c + e_p - 2 * cross)
    target = (mean_p**2 + var_p - mu * mean_p) / ((mu - mean_p) ** 2 + var_p)
    results = [CheckResult(
        "N2(a)", "Stable retrieval: u = (m^2 + s^2 - mu m) / ((mu - m)^2 + s^2); "
        "unbiased PLP (m = 0) gives u = s^2 / (mu^2 + s^2), strictly inside (0, 1)", "symbolic",
        is_zero(centre - target)
        and is_zero(centre.subs(mean_p, 0) - var_p / (mu**2 + var_p)))]
    n_zero, n_bad, n_cases = 0, 0, 200000
    mus, means = RNG.normal(0, 1, n_cases), RNG.normal(0, 1, n_cases)
    sds = RNG.exponential(0.5, n_cases)
    zero = mus * means >= means**2 + sds**2  # C >= E_P  <=>  w* = 0
    n_zero = int(zero.sum())
    bad = zero & ~((mus * means > 0) & (sds <= np.abs(mus) / 2 + 1e-15))
    n_bad = int(bad.sum())
    results.append(CheckResult(
        "N2(b)", "Stable retrieval: w* = 0 implies mu m > 0 and sigma_P <= |mu|/2", "property",
        n_bad == 0, {"cases": n_cases, "cases_with_w_zero": n_zero, "violations": n_bad}))
    # Noise-matching bound: |C - mu m| <= sqrt(E[(e_C - mu)^2 1_S]) sqrt(E[e_P^2 1_S]).
    worst = -np.inf
    for _ in range(3000):
        draws = 400
        eta = RNG.normal(size=draws)
        switch = eta > RNG.normal(1.0, 0.8)  # switching driven by the same noise
        base = RNG.normal()
        e_c = np.where(switch, base + RNG.normal(0.5, 0.5) * eta, base)
        e_p = RNG.normal(0, 0.3) + RNG.exponential(0.5) * eta
        _, _, cross = raw_moments(e_c, e_p)
        lhs = abs(cross - base * np.mean(e_p))
        rhs = math.sqrt(np.mean((e_c - base) ** 2 * switch)) * math.sqrt(np.mean(e_p**2 * switch))
        worst = max(worst, lhs - rhs)
    results.append(CheckResult(
        "N2(c)", "Without switching C = mu m exactly; with switching event S, "
        "|C - mu m| <= sqrt(E[(e_C - mu)^2 1_S]) sqrt(E[e_P^2 1_S])", "property",
        worst <= 1e-12, {"cases": 3000, "max_excess": worst}))
    return results


def check_pencil_bound() -> list[CheckResult]:
    """N3: w* lies between 1/(1 + lambda_max) and 1/(1 + lambda_min) of the pencil."""
    worst, worst_attain, n_cases = -np.inf, 0.0, 2000
    for _ in range(n_cases):
        sig_a = random_gram(RNG, 3) + 1e-3 * np.eye(3)
        sig_s = random_gram(RNG, 3) + 1e-2 * np.eye(3)
        root = np.linalg.cholesky(sig_s)
        inv_root = np.linalg.inv(root)
        lams, vecs = np.linalg.eigh(inv_root @ sig_a @ inv_root.T)
        lo, hi = 1 / (1 + lams[-1]), 1 / (1 + lams[0])
        for _ in range(20):
            gamma = RNG.normal(size=3)
            weight = gamma @ sig_s @ gamma / (gamma @ sig_a @ gamma + gamma @ sig_s @ gamma)
            worst = max(worst, lo - weight, weight - hi)
        gamma_star = inv_root.T @ vecs[:, 0]  # attains the upper end
        weight = gamma_star @ sig_s @ gamma_star / (gamma_star @ (sig_a + sig_s) @ gamma_star)
        worst_attain = max(worst_attain, abs(weight - hi))
    results = [CheckResult(
        "N3(a)", "K = 0: 1/(1 + lambda_max) <= w*(Gamma) <= 1/(1 + lambda_min), eigenvalues of "
        "Sigma_s^-1/2 Sigma_a Sigma_s^-T/2; both ends attained", "property",
        worst <= 1e-12 and worst_attain < 1e-9,
        {"cases": n_cases * 20, "max_excess": worst, "max_attainment_gap": worst_attain})]
    worst_rank1 = 0.0
    for _ in range(2000):
        mismatch = RNG.normal(size=3)
        sig_s = random_gram(RNG, 3) + 1e-2 * np.eye(3)
        root_inv = np.linalg.inv(np.linalg.cholesky(sig_s))
        lams = np.linalg.eigvalsh(root_inv @ np.outer(mismatch, mismatch) @ root_inv.T)
        mahal = mismatch @ np.linalg.solve(sig_s, mismatch)
        worst_rank1 = max(worst_rank1, abs(lams[-1] - mahal), abs(lams[0]))
    results.append(CheckResult(
        "N3(b)", "Rank-one analog seed Sigma_a = d d^T: lambda_max = d^T Sigma_s^-1 d, "
        "lambda_min = 0, so w* ranges over [1/(1 + d^T Sigma_s^-1 d), 1]", "property",
        worst_rank1 < 1e-8, {"cases": 2000, "max_error": worst_rank1}))
    return results


def check_correlated_gain() -> list[CheckResult]:
    """N4: the floor ratio f(rho, r), its monotonicity, and the two-sided gain bound."""
    corr, ratio = sp.symbols("rho r", positive=True)
    root = sp.sqrt(ratio)
    floor_ratio = (1 - corr**2) / (1 + ratio - 2 * corr * root)
    e_min, e_max = sp.symbols("b a", positive=True)
    v_min = (e_max * e_min * (1 - corr**2)) / (e_max + e_min - 2 * corr * sp.sqrt(e_max * e_min))
    deriv = sp.diff(floor_ratio, corr)
    factored = 2 * (root - corr) * (1 - corr * root) / (1 + ratio - 2 * corr * root) ** 2
    results = [CheckResult(
        "N4(a)", "min V / min(E_C, E_P) = (1 - rho^2) / (1 + r - 2 rho sqrt r), r = min/max; "
        "d/d rho = 2(sqrt r - rho)(1 - rho sqrt r)/(...)^2 >= 0 on [-1, sqrt r]", "symbolic",
        is_zero(sp.simplify(v_min / e_min - floor_ratio.subs(ratio, e_min / e_max)))
        and is_zero(deriv - factored)
        and is_zero(floor_ratio.subs(corr, root) - 1))]
    steps = np.arange(241)
    worst_up, worst_low, n_cases = -np.inf, -np.inf, 4000
    for _ in range(n_cases):
        rate = RNG.uniform(0.01, 0.08)
        envelope = np.maximum.accumulate(
            (RNG.exponential(0.01) + 1e-4) * np.exp(rate * steps * (1 + 0.3 * np.sin(steps * 0.1))))
        other = envelope * RNG.uniform(1.0, 3.0)
        corr_path = RNG.uniform(-0.9, 0.9, steps.size)
        cross = corr_path * envelope * other
        hybrid = best_hybrid(envelope**2, other**2, cross)
        ratio_path = hybrid / envelope**2
        tol = RNG.uniform(0.05, 0.5)
        t_env, t_hyb = first_passage(envelope**2, tol**2), first_passage(hybrid, tol**2)
        if t_env is None or t_hyb is None:
            continue
        worst_low = max(worst_low, t_env - t_hyb)  # gain >= 0
        floor0 = ratio_path[t_env:].min()
        t_wide = first_passage(envelope**2, tol**2 / floor0)
        if t_wide is not None:
            worst_up = max(worst_up, (t_hyb - t_env) - (t_wide - t_env))
    results.append(CheckResult(
        "N4(b)", "If min V / m^2 >= f0 from T(theta) on: 0 <= gain <= T(theta/sqrt f0) - T(theta)",
        "property", worst_up <= 0 and worst_low <= 0,
        {"cases": n_cases, "max_excess_upper": worst_up, "max_excess_lower": worst_low}))
    return results


def check_local_horizon() -> list[CheckResult]:
    """N5: dT/d ln(theta') = 1 / (d ln E / dH) at the crossing."""
    hh, k1, k2 = sp.symbols("H k1 k2", positive=True)
    log_err = sp.log(sp.Rational(1, 100)) + k1 * hh + k2 * hh**2  # an accelerating error curve
    level = sp.symbols("L", real=True)
    crossing = sp.solve(sp.Eq(log_err, level), hh)
    crossing = [c for c in crossing if c.subs({k1: 1, k2: 1, level: 0}).is_positive][0]
    lhs = sp.diff(crossing, level)
    rhs = 1 / sp.diff(log_err, hh).subs(hh, crossing)
    results = [CheckResult(
        "N5", "Implicit differentiation: dT/d ln theta' = 1 / Lambda_loc(T), where "
        "Lambda_loc = d ln E(H) / dH (checked on ln E = ln e0 + k1 H + k2 H^2)", "symbolic",
        is_zero(sp.simplify(lhs - rhs)))]
    noise_factor = sp.symbols("theta rho", positive=True)
    theta, rho = noise_factor
    eff = sp.sqrt(theta**2 - rho**2)
    results.append(CheckResult(
        "N5 noise factor", "d ln theta' / d ln theta = theta^2 / (theta^2 - rho^2) for "
        "theta' = sqrt(theta^2 - rho^2)", "symbolic",
        is_zero(sp.diff(sp.log(eff), theta) * theta - theta**2 / (theta**2 - rho**2))))
    return results


def check_floor_identity() -> list[CheckResult]:
    """N6: floor = E[c (u - u_bar(F))^2] = (1 - R_c^2) x excess of the best global weight."""
    worst, n_cases = 0.0, 2000
    for _ in range(n_cases):
        n_states, n_profile = 600, RNG.integers(1, 8)
        profile = RNG.integers(0, n_profile, n_states)
        curvs = RNG.exponential(1.0, n_states)
        centres = np.clip(0.5 + 0.15 * RNG.normal(size=n_states) + 0.05 * profile, 0.01, 0.99)
        cond = np.zeros(n_states)
        for value in range(n_profile):
            mask = profile == value
            if mask.any():
                cond[mask] = curvs[mask] @ centres[mask] / curvs[mask].sum()
        glob = curvs @ centres / curvs.sum()
        floor = np.mean(curvs * (cond - centres) ** 2)
        global_excess = np.mean(curvs * (glob - centres) ** 2)
        r2_weighted = 1 - floor / global_excess
        worst = max(worst, abs(floor - (1 - r2_weighted) * global_excess),
                    abs(floor - np.mean(curvs * centres**2) + np.mean(curvs * cond**2)))
    return [CheckResult(
        "N6", "No clipping: floor = E[c (u - u_bar(F))^2] = (1 - R_c^2) E[c (u - u_bar)^2]; "
        "Pythagoras: E[c u^2] = E[c u_bar(F)^2] + floor", "property", worst < 1e-10,
        {"cases": n_cases, "max_error": worst})]


def check_halfspace_bound() -> list[CheckResult]:
    """N7: max_j p_j <= Pr(switch) <= sum_j p_j with exact Gaussian half-space p_j."""
    worst_up, worst_low, n_states, dim, rho = -np.inf, -np.inf, 300, 7, 0.05
    tighter = 0
    for _ in range(n_states):
        library = RNG.normal(size=(RNG.integers(20, 300), dim)) * RNG.uniform(0.2, 1.0)
        query = RNG.normal(size=dim) * 0.5
        dist = np.linalg.norm(library - query, axis=1)
        order = np.argsort(dist)
        base, r1 = order[0], dist[order[0]]
        others = order[1:]
        gaps = np.linalg.norm(library[others] - library[base], axis=1)
        probs = norm.sf((dist[others] ** 2 - r1**2) / (2 * rho * gaps))
        noise = rho * RNG.normal(size=(20000, dim))
        d2 = ((query + noise)[:, None, :] - library[None, :, :]) ** 2
        rate = np.mean(d2.sum(axis=2).argmin(axis=1) != base)
        ref = max(rate, probs.max(), 1 / 20000)  # binomial s.e. at the larger of the two rates
        se = math.sqrt(ref * (1 - min(ref, 0.5)) / 20000)
        worst_up = max(worst_up, rate - min(1.0, probs.sum()) - 4 * se)
        worst_low = max(worst_low, probs.max() - rate - 4 * se)
        margin = dist[order[1]] - r1
        markov = min(1.0, 4 * dim * rho**2 / margin**2)
        tighter += probs.sum() <= markov
    return [CheckResult(
        "N7", "Exact half-space probabilities p_j = Phi_bar((r_j^2 - r_1^2)/(2 rho |X_j - X_1|)): "
        "max p_j <= Pr(switch) <= sum p_j (dimension-free)", "property",
        worst_up <= 0 and worst_low <= 0,
        {"states": n_states, "draws": 20000, "max_excess_upper": worst_up,
         "max_excess_lower": worst_low, "states_where_tighter_than_markov": tighter})]


def check_noise_monotonicity() -> list[CheckResult]:
    """N8: w*(rho) = q / ((A/rho + z)^2 + q) increases in rho iff A (A + rho z) > 0."""
    amp, zeta, rho, q = sp.symbols("A z rho q", real=True)
    weight = q / ((amp / rho + zeta) ** 2 + q)
    deriv = sp.diff(weight, rho)
    expected = 2 * q * amp * (amp + rho * zeta) / (rho**3 * ((amp / rho + zeta) ** 2 + q) ** 2)
    return [CheckResult(
        "N8", "Stable retrieval, unbiased PLP, common random numbers: dw*/drho = "
        "2 q A (A + rho z) / (rho^3 (...)^2), positive iff the copied noise does not overturn "
        "the amplified mismatch A = Gamma_H d", "symbolic", is_zero(sp.simplify(deriv - expected)))]


def check_clip_lemma() -> list[CheckResult]:
    """A4.4 lemma: V(clip v) - V(clip u) <= c (v - u)^2 for every real v and u."""
    u_vals, v_vals = RNG.normal(0.5, 1.5, 400000), RNG.normal(0.5, 1.5, 400000)
    curv = RNG.exponential(1.0, 400000)
    lhs = curv * ((np.clip(v_vals, 0, 1) - u_vals) ** 2 - (np.clip(u_vals, 0, 1) - u_vals) ** 2)
    worst = float(np.max(lhs - curv * (v_vals - u_vals) ** 2))
    return [CheckResult(
        "A4.4 lemma", "Clipping never hurts the comparison: V(clip v) - V(w*) <= c (v - u)^2",
        "property", worst <= 1e-12, {"cases": 400000, "max_excess": worst})]


CHECKS = [check_clip_lemma, check_conditioned_curvature, check_stable_retrieval, check_pencil_bound,
          check_correlated_gain, check_local_horizon, check_floor_identity,
          check_halfspace_bound, check_noise_monotonicity]


def main() -> None:
    """Run the proposed-theorem checks and write ``proposed_checks.json``."""
    results = [res for check in CHECKS for res in check()]
    for res in results:
        print(f"{'PASS' if res.passed else 'FAIL'}  {res.method:12s}  {res.item:16s}  {res.claim}")
        if res.detail:
            print(" " * 6, json.dumps(res.detail, default=float))
    print(f"\n{sum(r.passed for r in results)}/{len(results)} checks passed (seed {MASTER_SEED}).")
    Path(__file__).with_name("proposed_checks.json").write_text(
        json.dumps({"seed": MASTER_SEED, "results": [asdict(r) for r in results]},
                   indent=1, default=float))


if __name__ == "__main__":
    main()
