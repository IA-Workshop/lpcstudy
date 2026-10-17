"""MA-1 check 3: the implicit-function Jacobian of the fit, and the case value of H1a.

DEVELOPMENT (DEV-0 pilot medians, read-only): not a hypothesis test. Deterministic (no draws).

(a) On the 12 pilot cells: d(1/d)/dy by the implicit function theorem (exact Hessian) against
    central differences of the tight fit (step 1e-5 in y; truncation ~ h^2, fit error ~1e-15/h),
    and against the Gauss-Newton form (J^T J)^{-1} J^T (drops the residual-curvature term), and
    the 2-point-Jacobian production fit differenced at the same step (the Q1-note noise).
(b) The H1a case value: influence lag-1 at latent phi = 0.3 of the fit part,
        l_c = sum_jk w_j w_k arcsin(0.3 rho_jk) / sum_jk w_j w_k arcsin(rho_jk),  w = A / g,
    for an exchangeable latent correlation rho_jk = c^2 (j != k), c^2 in [0, 1), with the pilot
    A_j and two density patterns (equal g; the kappa = 0.6..2.5 pattern of checks 1 and 2).
    The arcsin form is the sign covariance of a Gaussian copula: cov(sgn z_j, sgn z_k) =
    (2/pi) arcsin(corr). Its min over c^2 is the smallest case value the pilot weights allow.
"""
import json, sys
from pathlib import Path
import numpy as np
from scipy import stats
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ma1_core as mc

KAPPA = np.linspace(0.6, 2.5, 5)
Q = stats.gamma.ppf(0.5, KAPPA)
G_K = Q * stats.gamma.pdf(Q, KAPPA)

if __name__ == "__main__":
    worst = dict(fd=0.0, gn=0.0, prod=0.0)
    lc_rows = []
    for path in sys.argv[1:]:
        A_ = json.load(open(path))
        for system, blk in A_["systems"].items():
            for rho, b in blk["H1a"]["by_noise"].items():
                sizes = np.array(sorted(int(k) for k in b["median_seed_by_n_lib"]), float)
                med = np.array([b["median_seed_by_n_lib"][str(int(n))] for n in sizes]) ** 2
                log_n, y = np.log(sizes), np.log(med)
                th = mc.fit_tight(sizes, med, x0=mc.fit_prod(sizes, med))
                D, cond, eig = mc.dtheta_dy(sizes, med, th)
                ift = 0.5 * D[1]
                J = mc.jac(log_n, th)
                gn = 0.5 * np.linalg.solve(J.T @ J, J.T)[1]
                h = 1e-5
                fd, pr = np.empty(5), np.empty(5)
                for j in range(5):
                    e = np.zeros(5); e[j] = h
                    fd[j] = 0.25 * (mc.fit_tight(sizes, med * np.exp(e), x0=th)[1]
                                    - mc.fit_tight(sizes, med * np.exp(-e), x0=th)[1]) / h
                    pr[j] = 0.25 * (mc.fit_prod(sizes, med * np.exp(e))[1]
                                    - mc.fit_prod(sizes, med * np.exp(-e))[1]) / h
                s = np.max(np.abs(ift))
                r = dict(fd=np.max(np.abs(fd - ift)) / s, gn=np.max(np.abs(gn - ift)) / s,
                         prod=np.max(np.abs(pr - ift)) / s)
                for k in worst:
                    worst[k] = max(worst[k], r[k])
                resid = mc.model(log_n, *th) - y
                tag = f"{Path(path).parts[-3][:2]} {system:8s} {rho}"
                print(f"{tag}  |r| max {np.max(np.abs(resid)):.3e}  cond(H) {cond:.2e}  "
                      f"IFT vs FD {r['fd']:.1e}  GN-only vs IFT {r['gn']:.2e}  "
                      f"prod-FD vs IFT {r['prod']:.1e}")
                for gname, g in (("equal g", np.ones(5)), ("kappa g", G_K)):
                    w = ift / g
                    vals = []
                    for c2 in np.linspace(0, 0.99, 100):
                        rl = np.full((5, 5), c2) + (1 - c2) * np.eye(5)
                        vals.append((w @ np.arcsin(0.3 * rl) @ w) / (w @ np.arcsin(rl) @ w))
                    vals = np.array(vals)
                    lc_rows.append((tag, gname, vals.min(), np.linspace(0, 0.99, 100)[vals.argmin()],
                                    vals[0], vals[49]))
    print("\n== max over 12 cells of |. - IFT| / max|IFT| for d(1/d)/dy:")
    print(f"  central differences of the tight fit (h = 1e-5): {worst['fd']:.2e}")
    print(f"  Gauss-Newton form (J^T J)^-1 J^T (no residual curvature): {worst['gn']:.2e}")
    print(f"  central differences of the production fit (h = 1e-5): {worst['prod']:.2e}")
    print("\n== case value l_c (fit part, latent phi = 0.3), exchangeable latent correlation c^2:")
    for tag, gname, mn, at, at0, at05 in lc_rows:
        print(f"  {tag} {gname:8s}: min {mn:.4f} at c^2 = {at:.2f}; c^2 = 0: {at0:.4f}; "
              f"c^2 = 0.49: {at05:.4f}")
    print(f"  overall min {min(r[2] for r in lc_rows):.4f}; (2/pi) arcsin(0.3) = "
          f"{2 / np.pi * np.arcsin(0.3):.4f}")
