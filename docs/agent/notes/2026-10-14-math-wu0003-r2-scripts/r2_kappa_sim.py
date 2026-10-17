"""WU-0003.3a R2: bias of the tool's kappa_E under draw-level weight-error dependence (synthetic).

DEVELOPMENT, synthetic only (no run directory read). Randomness: lpcstudy.data.make_rng, seed
20261040, labels per scenario and replicate.

World (one replicate = one pilot-size run, n = 500 test states in time order):
  state i: latent AR(1) series (phi = 0.3) give log sC_i, log sP_i (seed-error scales) and
  log g_i (amplification).
  draw d (oracle draws M = 200, evaluation draws E): the draw's analog seed error
  eps_d = sC_i exp(sa xi_d), estimate seed error del_d = sP_i exp(sa xi'_d); errors
  e_C = g eps_d u1, e_P = g del_d u2, corr(u1, u2) = 0.3.
  proxies of the draw: log eps_hat = log sC_i + dep*sa*xi_d + (1-dep)*sa*xi*_d + sp*zeta_d
  (dep = 1: the proxy sees this draw's analog quality, as R and the profile do in the pipeline;
  dep = 0: an independent copy xi*, same weight variability, no dependence; dep = -1, "flip":
  +xi_d in even states and -xi_d in odd ones, so the dependence term b_i changes sign across
  states and is nearly uncorrelated with the state level; dep = -2, "anti": -xi_d in every
  state, b_i > 0 and proportional to the state level); same for del_hat.
  rules (weight on CP): A1 w = 0; A2 w = 0.3; A4 closed form del_hat^2/(eps_hat^2 + del_hat^2);
  A3 logistic(2 (log del_hat3 - log eps_hat3)) on noisier proxies (sp3 = 1); A5 four regimes
  on log(eps_hat/del_hat) cut at -1, 0, 1 with weights 0.9, 0.65, 0.35, 0.1.
Criteria: H2c (A4 - A2, A4 - A1; diff), H2d (A4/A3; ratio), H3c (A5/A4; ratio).

Estimators, all at E_run = 2, E_full = 4:
  tool : rr.kappa_estimate on V_i = mean_d V_i(w_d) (oracle moments, M = 200) and the realized
         per-state MSE (the code under review, imported).
  half : the proposed half-split estimator: V_d = BV(psi of (a_A - a_B)/2), a_A, a_B the
         per-state MSE of eval draws [0, E/2) and [E/2, E) (per-draw here), linearized with the
         same R-hat; kappa^2 = 1 - (1 - r) V_d / BV(psi(a)).
  truth: E_T = 16 evaluation draws per state (the run's two are the first two). With
         D = sum_i Q_ii s_i^2 (s_i^2 the within-state variance of the per-draw influence
         contribution, 15 df; Q_ii = BV(e_i), the exact weights of the block-variance quadratic
         form) and A = BV(psi(a_16)) - D/16, both unbiased for the state and per-draw parts,
         kappa_true^2 = (mean A + mean D/4)/(mean A + mean D/2) over replicates (exact E scaling
         under conditionally iid draws; same functional as the tool, so its O(b/n) factor cancels).
  Also the population form of the tool's estimand: sqrt((mean V_s + r mean V_d)/(mean V_s + mean V_d)).
"""
from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

WT = Path("/home/brianm/projects/physics/chaos/lpcstudy-wt/wu/0003-3a-report")
sys.path.insert(0, str(WT))
import numpy as np  # noqa: E402

from lpcstudy.data import make_rng  # noqa: E402

spec = importlib.util.spec_from_file_location("rehearsal_report", WT / "tools" / "rehearsal_report.py")
rr = importlib.util.module_from_spec(spec)
sys.modules["rehearsal_report"] = rr
spec.loader.exec_module(rr)

SEED = 20261040
N, M, E_FULL, E_RUN, BLOCK, E_T = 500, 200, 4, 2, 5, 16
R = int(sys.argv[1]) if len(sys.argv) > 1 else 400
CRITERIA = {"H2c A4-A2": ("diff", "A4", "A2"), "H2c A4-A1": ("diff", "A4", "A1"),
            "H2d A4/A3": ("ratio", "A4", "A3"), "H3c A5/A4": ("ratio", "A5", "A4")}
SCEN = {  # name: (sa, sp, dep, state log-SD, gain log-SD)
    "S5 no weight variation (tool exact up to M noise)": (0.0, 0.0, 1, 0.6, 0.4),
    "S0 weights vary, no draw-level error scale": (0.0, 0.5, 1, 0.6, 0.4),
    "S1 independent control sa .5": (0.5, 0.5, 0, 0.6, 0.4),
    "S2 dependent sa .5": (0.5, 0.5, 1, 0.6, 0.4),
    "S3 independent control sa 1": (1.0, 0.3, 0, 0.6, 0.4),
    "S4 dependent sa 1": (1.0, 0.3, 1, 0.6, 0.4),
    "S6 dependent sa 1, heavy states": (1.0, 0.3, 1, 1.0, 0.7),
    "S7 dependent sa .5, wide states (larger state share)": (0.5, 0.5, 1, 1.5, 0.2),
    "S8 independent control of S7": (0.5, 0.5, 0, 1.5, 0.2),
    "S9 sign-flip dependence (counterexample design)": (1.0, 0.0, -1, 0.6, 0.4),
    "S10 pipeline-like light states, dependent": (0.5, 0.3, 1, 0.25, 0.2),
    "S11 independent control of S10": (0.5, 0.3, 0, 0.25, 0.2),
    "S12 anti dependence, wide states (counterexample design)": (1.0, 0.0, -2, 1.5, 0.2),
    "S13 dependence of S12 with the sign of S7 (control)": (1.0, 0.0, 1, 1.5, 0.2),
}


def ar1(g, n, phi=0.3):
    x = np.empty(n)
    x[0] = g.standard_normal()
    eps = g.standard_normal(n) * math.sqrt(1 - phi**2)
    for i in range(1, n):
        x[i] = phi * x[i - 1] + eps[i]
    return x


def draws(g, sC, sP, gain, k, sa, sp, dep):
    """Errors and rule weights of k draws per state: dict rule -> (n, k) weight, e_C, e_P."""
    n = len(sC)
    xi, xi2 = g.standard_normal((n, k)), g.standard_normal((n, k))
    eps = sC[:, None] * np.exp(sa * xi)
    dl = sP[:, None] * np.exp(sa * xi2)
    u1 = g.standard_normal((n, k))
    u2 = 0.3 * u1 + math.sqrt(1 - 0.09) * g.standard_normal((n, k))
    e_c, e_p = gain[:, None] * eps * u1, gain[:, None] * dl * u2
    xs, xs2 = g.standard_normal((n, k)), g.standard_normal((n, k))
    if dep in (-1, -2):  # -1 "flip": follows the draw in even states, opposes it in odd ones;
        # -2 "anti": opposes the draw in every state (the rule moves weight toward the worse draw)
        sgn = (np.where(np.arange(n) % 2 == 0, 1.0, -1.0) if dep == -1 else -np.ones(n))[:, None]
        px, px2 = sgn * xi, sgn * xi2
    else:
        px = dep * xi + (1 - dep) * xs
        px2 = dep * xi2 + (1 - dep) * xs2
    leh = np.log(sC)[:, None] + sa * px + sp * g.standard_normal((n, k))
    ldh = np.log(sP)[:, None] + sa * px2 + sp * g.standard_normal((n, k))
    leh3 = leh + 1.0 * g.standard_normal((n, k))
    ldh3 = ldh + 1.0 * g.standard_normal((n, k))
    w = {"A1": np.zeros((n, k)), "A2": np.full((n, k), 0.3),
         "A4": np.exp(2 * ldh) / (np.exp(2 * leh) + np.exp(2 * ldh)),
         "A3": 1.0 / (1.0 + np.exp(-2.0 * (ldh3 - leh3)))}
    reg = np.digitize(leh - ldh, [-1.0, 0.0, 1.0])
    w["A5"] = np.array([0.9, 0.65, 0.35, 0.1])[reg]
    return w, e_c, e_p


def bv(x):
    return rr.block_variance(np.asarray(x, float), BLOCK)


def psi(kind, a, b, rhat=None, bbar=None):
    if kind == "diff":
        d = a - b
        return d - d.mean()
    return rr.influence_ratio(a, b)


QII = None


def q_diag():
    global QII
    if QII is None:
        QII = np.array([bv(np.eye(1, N, i)[0]) for i in range(N)])
    return QII


def one(g, sa, sp, dep, ls, lg):
    z1, z2, z3 = ar1(g, N), ar1(g, N), ar1(g, N)
    sC, sP, gain = np.exp(-1.0 + ls * z1), np.exp(-1.2 + ls * z2), np.exp(lg * z3)
    # oracle moments from M draws (same law, independent)
    _, oc, op = draws(g, sC, sP, gain, M, sa, sp, dep)
    EC, EP, CC = (oc**2).mean(1), (op**2).mean(1), (oc * op).mean(1)
    w, ec, ep = draws(g, sC, sP, gain, E_T, sa, sp, dep)
    X = {r: (w[r] * ec + (1 - w[r]) * ep) ** 2 for r in w}
    Vf = {r: (w[r][:, :E_RUN] ** 2 * EC[:, None] + (1 - w[r][:, :E_RUN]) ** 2 * EP[:, None]
              + 2 * w[r][:, :E_RUN] * (1 - w[r][:, :E_RUN]) * CC[:, None]).mean(1) for r in w}
    out = {}
    for crit, (kind, f, s) in CRITERIA.items():
        a2f, a2s = X[f][:, :E_RUN].mean(1), X[s][:, :E_RUN].mean(1)
        atf, ats = X[f].mean(1), X[s].mean(1)
        k_tool, vs, vd = rr.kappa_estimate(Vf[f], Vf[s], a2f, a2s, kind, E_RUN, E_FULL, BLOCK)
        # half-split estimator (E_run = 2: halves are single draws)
        hf, hs = (X[f][:, 0] - X[f][:, 1]) / 2, (X[s][:, 0] - X[s][:, 1]) / 2
        if kind == "diff":
            pd = hf - hs
        else:
            rhat = a2f.mean() / a2s.mean()
            pd = (hf - rhat * hs) / a2s.mean()
        tot = bv(psi(kind, a2f, a2s))
        vdh = bv(pd)
        k2h = 1 - (1 - E_RUN / E_FULL) * vdh / tot
        if kind == "diff":
            per = X[f] - X[s]
        else:
            per = (X[f] - (atf.mean() / ats.mean()) * X[s]) / ats.mean()
        dd = float(q_diag() @ per.var(axis=1, ddof=1))
        aa = bv(psi(kind, atf, ats)) - dd / E_T
        out[crit] = (k_tool, k2h, tot, aa, dd, vs, vd, vdh)
    return out


def main():
    print(f"R = {R} replicates of n = {N}, M = {M}, E {E_RUN} -> {E_FULL}, truth from {E_T} draws, "
          f"block {BLOCK}, seed {SEED}")
    r = E_RUN / E_FULL
    for name, par in SCEN.items():
        res = {c: [] for c in CRITERIA}
        for rep in range(R):
            g = make_rng(SEED, "r2-kappa", name, rep)
            o = one(g, *par)
            for c in CRITERIA:
                res[c].append(o[c])
        print(f"\n{name}: (sa, sp, dep, state sd, gain sd) = {par}")
        print(f"  {'criterion':11s} {'truth':>7s} {'(SE)':>6s} {'tool':>7s} {'bias':>8s} {'(SE)':>6s} "
              f"{'tool pop':>8s} {'bias':>8s} {'(SE)':>6s} {'k2 half-truth2':>14s} {'(SE)':>6s} {'half pop':>8s} {'bias':>8s} {'(SE)':>6s} {'draw share':>10s} "
              f"{'sd tool':>7s} {'sd k2half':>9s} {'half k2 outside [r,1]':>21s}")
        for c in CRITERIA:
            a = np.array(res[c])
            A, D = a[:, 3], a[:, 4]
            k_true = math.sqrt((A.mean() + D.mean() / E_FULL) / (A.mean() + D.mean() / E_RUN))
            # joint bootstrap over replicates (scratch; fixed generator): every bias SE is paired
            gb = make_rng(SEED, "r2-kappa-se", name, c)
            idx = gb.integers(0, R, (1000, R))
            Ab, Db = A[idx].mean(1), D[idx].mean(1)
            kb = np.sqrt((Ab + Db / E_FULL) / (Ab + Db / E_RUN))
            se_true = float(kb.std(ddof=1))
            kt = a[:, 0]
            k2h = a[:, 1]
            n_out = int(np.sum(k2h < r) + np.sum(k2h > 1))
            vs, vd = a[:, 5].mean(), a[:, 6].mean()
            k_pop = math.sqrt((vs + r * vd) / (vs + vd))
            share = (D.mean() / E_RUN) / (A.mean() + D.mean() / E_RUN)
            se_t = float((kt[idx].mean(1) - kb).std(ddof=1))
            kpb = np.sqrt((a[idx, 5].mean(1) + r * a[idx, 6].mean(1)) / (a[idx, 5].mean(1) + a[idx, 6].mean(1)))
            se_pop = float((kpb - kb).std(ddof=1))
            # half estimator, no truncation: its kappa^2 against truth^2, and the population form
            k2h_bias = float(k2h.mean() - k_true**2)
            k2h_se = float((k2h[idx].mean(1) - kb**2).std(ddof=1))
            kh_pop = math.sqrt(1 - (1 - r) * a[:, 7].mean() / a[:, 2].mean())
            khb = np.sqrt(1 - (1 - r) * a[idx, 7].mean(1) / a[idx, 2].mean(1))
            se_hpop = float((khb - kb).std(ddof=1))
            print(f"  {c:11s} {k_true:7.4f} {se_true:6.4f} {kt.mean():7.4f} {kt.mean()-k_true:+8.4f} "
                  f"{se_t:6.4f} {k_pop:8.4f} {k_pop-k_true:+8.4f} {se_pop:6.4f} {k2h_bias:+14.4f} {k2h_se:6.4f} "
                  f"{kh_pop:8.4f} {kh_pop-k_true:+8.4f} {se_hpop:6.4f} "
                  f"{share:10.3f} {kt.std(ddof=1):7.3f} {k2h.std(ddof=1):9.3f} {n_out:21d}")


if __name__ == "__main__":
    main()
