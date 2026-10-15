"""MA-1 check 2: the estimated influence series on finite samples (pilot n = 300, full n = 1000).

DEVELOPMENT (DEV-0 pilot medians, read-only; scratch seed 20261021): not a hypothesis test.

World (dump-shaped: seed_sq (nS x 5), inverse_dim (nS,)), on two pilot cells as population:
  latent z_ij = c u_i + sqrt(1 - c^2) e_ij (j = 1..5), u and e_.j independent unit AR(1) with phi;
  seed_sq_ij = m_j Q_kappa_j(Phi(z_ij)) / med(Gamma(kappa_j))   (Gamma marginals, median m_j)
  inverse_dim_i = mu Q_19(Phi(z_i0)) / 19,  z_i0 = c_r u_i + sqrt(1 - c_r^2) e_i0
  (S/(k-1) under the exact Gamma law, k = 20, correlated with the seed errors through u).
c = 0.7 (state factor: same state, five library sizes), c_r = 0.5, kappa_j = linspace(0.6, 2.5).

Per replication: the production statistic T = (1/2) b_prod / mean(inverse_dim) (curve_fit copy);
its Bahadur linear term L = mean_i psi(X_i; F) with population medians and true densities; the
estimated series psi_hat (sample medians, tight refit, densities by SBG/Hall-Sheather, by KDE, or
true). Reported: corr(T - T0, L) and sd(T)/sd(L) (is the first-order term the statistic?);
sd(T) against the long-run SE implied by psi_hat; acf(1) of psi_hat under each density; the
relative error of the density estimates. Case value: acf(1) of psi at phi = 0.3 on one series of
2e5 states with the population quantities, and the arcsin formula for the fit part.
"""
import json, sys
from pathlib import Path
import numpy as np
from scipy import stats
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ma1_core as mc

rng = np.random.default_rng(20261021)
KAPPA = np.linspace(0.6, 2.5, 5)
Q = stats.gamma.ppf(0.5, KAPPA)
G_TRUE = Q * stats.gamma.pdf(Q, KAPPA)
C, C_R = 0.7, 0.5
REPS = 400


def ar1(n, phi, k):
    e = rng.standard_normal((n + 200, k))
    out = np.empty_like(e)
    out[0] = e[0]
    s = np.sqrt(1 - phi * phi)
    for t in range(1, n + 200):
        out[t] = phi * out[t - 1] + s * e[t]
    return out[200:]


def world(n, phi, med, mu):
    u = ar1(n, phi, 1)
    e = ar1(n, phi, 6)
    z = C * u + np.sqrt(1 - C * C) * e[:, :5]
    z0 = C_R * u[:, 0] + np.sqrt(1 - C_R ** 2) * e[:, 5]
    sq = med[None, :] * stats.gamma.ppf(stats.norm.cdf(z), KAPPA) / Q
    inv = mu * stats.gamma.ppf(stats.norm.cdf(z0), 19.0) / 19.0
    return sq, inv


def pop_psi(sq, inv, med, mu, A, R):
    return (mc.sign_type(sq, med[None, :]) @ (A / G_TRUE) - R * (inv - mu)) / mu


def main(path, keys):
    A_ = json.load(open(path))
    for system, rho in keys:
        b = A_["systems"][system]["H1a"]["by_noise"][rho]
        mu = A_["systems"][system]["H1a"]["inverse_dim_reference"]
        sizes = np.array(sorted(int(k) for k in b["median_seed_by_n_lib"]), float)
        med = np.array([b["median_seed_by_n_lib"][str(int(n))] for n in sizes]) ** 2
        th0 = mc.fit_tight(sizes, med, x0=mc.fit_prod(sizes, med))
        D, _, _ = mc.dtheta_dy(sizes, med, th0)
        A = 0.5 * D[1]
        T0 = 0.5 * th0[1] / mu
        R0 = T0
        w = A / G_TRUE
        print(f"\n### {Path(path).parts[-3][:2]} {system} rho={rho}: T0 = {T0:.4f} "
              f"(1/d {0.5 * th0[1]:.4f}, mu {mu:.4f}); w_j = A_j/g_j {np.round(w, 3).tolist()}")
        # case value: long series at phi = 0.3, population quantities
        for phi in (0.0, 0.3):
            sq, inv = world(200_000, phi, med, mu)
            psi = pop_psi(sq, inv, med, mu, A, R0)
            psi_fit = mc.sign_type(sq, med[None, :]) @ w
            rho_lat = np.full((5, 5), C * C) + (1 - C * C) * np.eye(5)
            fit_formula = (w @ np.arcsin(phi * rho_lat) @ w) / (w @ np.arcsin(rho_lat) @ w)
            share = np.var(R0 * (inv - mu)) / np.var(psi_fit)
            print(f"  population, phi={phi}: acf1(psi_ratio) {mc.acf1(psi):.4f}  "
                  f"acf1(psi_1/d) {mc.acf1(psi_fit):.4f}  arcsin formula (1/d part) "
                  f"{fit_formula:.4f}  var share reference/fit {share:.4f}  "
                  f"beta5(acf1) {mc.beta5(mc.acf1(psi)):.4f}")
        for n in (300, 1000):
            for phi in (0.0, 0.3):
                rec = {k: [] for k in ("T", "L", "acf_true", "acf_sbg", "acf_kde", "acf_pop",
                                       "sd_sbg", "sd_kde", "gerr_sbg", "gerr_kde", "dacf_sbg",
                                       "dacf_kde", "lrv_sbg")}
                for _ in range(REPS):
                    sq, inv = world(n, phi, med, mu)
                    medh = np.median(sq, axis=0)
                    th_p = mc.fit_prod(sizes, medh)
                    rec["T"].append(0.5 * th_p[1] / inv.mean())
                    psi_pop = pop_psi(sq, inv, med, mu, A, R0)
                    rec["L"].append(psi_pop.mean())
                    rec["acf_pop"].append(mc.acf1(psi_pop))
                    ps = {}
                    for kind in ("true", "sbg", "kde"):
                        out = mc.influence(sq, inv, sizes, density=kind,
                                           g_true=G_TRUE if kind == "true" else None)
                        ps[kind] = out["psi_ratio"]
                        rec[f"acf_{kind}"].append(mc.acf1(out["psi_ratio"]))
                        if kind != "true":
                            rec[f"sd_{kind}"].append(out["psi_ratio"].std(ddof=1) / np.sqrt(n))
                            rec[f"gerr_{kind}"].append(out["g"] / G_TRUE - 1)
                            rec[f"dacf_{kind}"].append(rec[f"acf_{kind}"][-1] - rec["acf_true"][-1])
                    # long-run SE from psi_sbg: Bartlett/MBB-5 form, b * var of block means
                    x = ps["sbg"] - ps["sbg"].mean()
                    bm = np.convolve(x, np.ones(5) / 5, mode="valid")
                    rec["lrv_sbg"].append(np.sqrt(5 * np.mean(bm ** 2) / n))
                r = {k: np.array(v) for k, v in rec.items()}
                dT = r["T"] - T0
                ok = np.isfinite(dT)
                print(f"  n={n} phi={phi} (R={REPS}, {int((~ok).sum())} failed fits): "
                      f"sd(T) {dT[ok].std(ddof=1):.4f}  bias(T) {dT[ok].mean():+.4f}  "
                      f"corr(T - T0, L) {np.corrcoef(dT[ok], r['L'][ok])[0, 1]:.4f}  "
                      f"sd(T)/sd(L) {dT[ok].std(ddof=1) / r['L'][ok].std(ddof=1):.4f}")
                print(f"     SE from psi_hat (sbg; iid form) mean {r['sd_sbg'].mean():.4f}, "
                      f"(kde) {r['sd_kde'].mean():.4f}; MBB-5 long-run form (sbg) "
                      f"{r['lrv_sbg'].mean():.4f}  -> ratio to sd(T): iid "
                      f"{r['sd_sbg'].mean() / dT[ok].std(ddof=1):.3f}, block "
                      f"{r['lrv_sbg'].mean() / dT[ok].std(ddof=1):.3f}")
                print(f"     acf1: population-psi mean {r['acf_pop'].mean():+.4f} (sd "
                      f"{r['acf_pop'].std(ddof=1):.4f}); true-g {r['acf_true'].mean():+.4f} "
                      f"(sd {r['acf_true'].std(ddof=1):.4f}); sbg {r['acf_sbg'].mean():+.4f} "
                      f"(sd {r['acf_sbg'].std(ddof=1):.4f}); kde {r['acf_kde'].mean():+.4f} "
                      f"(sd {r['acf_kde'].std(ddof=1):.4f})")
                print(f"     acf1(est g) - acf1(true g): sbg mean {r['dacf_sbg'].mean():+.5f} "
                      f"sd {r['dacf_sbg'].std(ddof=1):.5f} max|.| {np.abs(r['dacf_sbg']).max():.4f};"
                      f" kde mean {r['dacf_kde'].mean():+.5f} sd {r['dacf_kde'].std(ddof=1):.5f}"
                      f" max|.| {np.abs(r['dacf_kde']).max():.4f}")
                print(f"     g_hat/g - 1 per column: sbg mean "
                      f"{np.round(r['gerr_sbg'].mean(0), 3).tolist()} sd "
                      f"{np.round(r['gerr_sbg'].std(0, ddof=1), 3).tolist()}; kde mean "
                      f"{np.round(r['gerr_kde'].mean(0), 3).tolist()} sd "
                      f"{np.round(r['gerr_kde'].std(0, ddof=1), 3).tolist()}")


if __name__ == "__main__":
    print(f"design: c = {C}, c_r = {C_R}, kappa = {KAPPA.round(3).tolist()}, "
          f"g_true = {G_TRUE.round(4).tolist()}")
    main(sys.argv[1], [("lorenz63", "0.01")])
    main(sys.argv[2], [("rossler", "0.02")])
