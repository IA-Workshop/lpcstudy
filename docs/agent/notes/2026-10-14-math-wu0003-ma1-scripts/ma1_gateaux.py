"""MA-1 check 1: the analytic influence function against a numerical Gateaux derivative.

DEVELOPMENT (DEV-0 pilot medians, read-only; scratch seed 20261020): not a hypothesis test.

Population world per pilot cell (12 cells: P0, P1 x 3 systems x rho 0.01, 0.02): column j has
the law X_j = m_j G_j / med(G_j), G_j ~ Gamma(kappa_j), so its median is the pilot median m_j
exactly (the square of the leaf ``median_seed_by_n_lib``). Shapes kappa_j = linspace(0.6, 2.5)
make the density term differ by column (with one common shape it would cancel up to scale).
Reference: mu = the pilot ``inverse_dim_reference``; per-state inverse_dim = mu Gamma(19)/19.

Functional: T(F) = (1/2) theta_b(F) / mu(F), theta = exact least-squares fit to log medians.
Contamination F_eps = (1 - eps) F + eps delta_x at a state x = (x_1..x_5, inv_x):
    median_j(eps) = Q_j((1/2 - eps 1{x_j < m_j}) / (1 - eps)),  mu(eps) = (1 - eps) mu + eps inv_x
(exact quantiles: scipy gamma.ppf). Numerical Gateaux derivative: central difference in eps with
the tight fit (analytic Jacobian, tol 1e-15, Newton polish). Analytic IF: ma1_core.influence
formula with the true densities g_j = q f_kappa(q), q = med Gamma(kappa_j) (density of log X_j at
log m_j; scale-free). 60 contamination points per cell drawn from the world.

Steps h = 4e-3, 2e-3, 1e-3 (observed order; expected 2 for a central difference of a smooth
function: the contaminated medians are smooth in eps once the side of x_j is fixed) and 1e-5
(round-off floor). Then the same Gateaux derivative with the PRODUCTION fit (curve_fit defaults,
2-point Jacobian) at h = 1e-5, 1e-3, 1e-2, to show the stopping noise.
"""
import json, sys
from pathlib import Path
import numpy as np
from scipy import stats
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ma1_core as mc

rng = np.random.default_rng(20261020)
KAPPA = np.linspace(0.6, 2.5, 5)
N_X = 60


def cells(paths):
    for path in paths:
        A = json.load(open(path))
        for system, blk in A["systems"].items():
            h = blk["H1a"]
            for rho, b in h["by_noise"].items():
                sizes = np.array(sorted(int(k) for k in b["median_seed_by_n_lib"]), float)
                med = np.array([b["median_seed_by_n_lib"][str(int(n))] for n in sizes]) ** 2
                yield (f"{Path(path).parts[-3][:2]} {system:8s} {rho}", sizes, med,
                       h["inverse_dim_reference"], b)


def contaminated(m, mu, x, inv_x, eps):
    q = stats.gamma.ppf(0.5, KAPPA)
    p = (0.5 - eps * (x < m)) / (1 - eps)
    return m * stats.gamma.ppf(p, KAPPA) / q, (1 - eps) * mu + eps * inv_x


def T(sizes, med, mu, x0, fit):
    th = mc.fit_tight(sizes, med, x0=x0) if fit == "tight" else mc.fit_prod(sizes, med)
    return 0.5 * th[1] / mu, 0.5 * th[1]


if __name__ == "__main__":
    q = stats.gamma.ppf(0.5, KAPPA)
    g_true = q * stats.gamma.pdf(q, KAPPA)          # density of log X_j at log m_j
    print(f"kappa {KAPPA.round(3).tolist()}  g_j (density of log X at its median) "
          f"{g_true.round(4).tolist()}")
    worst = {h: 0.0 for h in (4e-3, 2e-3, 1e-3, 1e-5)}
    worst_inv = {h: 0.0 for h in worst}
    prod_err = {h: [] for h in (1e-5, 1e-3, 1e-2)}
    orders = []
    for tag, sizes, med, mu, b in cells(sys.argv[1:]):
        th0 = mc.fit_tight(sizes, med, x0=mc.fit_prod(sizes, med))
        D, cond, eig = mc.dtheta_dy(sizes, med, th0)
        A = 0.5 * D[1]
        R = 0.5 * th0[1] / mu
        # contamination points from the world (independent columns suffice: the IF is pointwise)
        X = med[None, :] * stats.gamma.rvs(KAPPA, size=(N_X, 5), random_state=rng) / q
        INV = mu * rng.gamma(19.0, size=N_X) / 19.0
        psi_an = (mc.sign_type(X, med[None, :]) @ (A / g_true) - R * (INV - mu)) / mu
        psi_an_inv = mc.sign_type(X, med[None, :]) @ (A / g_true)
        scale = np.max(np.abs(psi_an))
        num = {}
        for h in worst:
            vals, vals_inv = [], []
            for x, iv in zip(X, INV):
                mp, mup = contaminated(med, mu, x, iv, h)
                mm, mum = contaminated(med, mu, x, iv, -h)
                tp, ip = T(sizes, mp, mup, th0, "tight")
                tm, im = T(sizes, mm, mum, th0, "tight")
                vals.append((tp - tm) / (2 * h)); vals_inv.append((ip - im) / (2 * h))
            num[h] = np.array(vals)
            worst[h] = max(worst[h], np.max(np.abs(num[h] - psi_an)) / scale)
            worst_inv[h] = max(worst_inv[h], np.max(np.abs(np.array(vals_inv) - psi_an_inv))
                               / np.max(np.abs(psi_an_inv)))
        e1 = np.max(np.abs(num[4e-3] - num[2e-3])); e2 = np.max(np.abs(num[2e-3] - num[1e-3]))
        orders.append(np.log2(e1 / e2))
        for h in prod_err:
            for x, iv, pa in list(zip(X, INV, psi_an))[:20]:
                mp, mup = contaminated(med, mu, x, iv, h)
                mm, mum = contaminated(med, mu, x, iv, -h)
                d = (T(sizes, mp, mup, None, "prod")[0] - T(sizes, mm, mum, None, "prod")[0]) / (2 * h)
                prod_err[h].append(abs(d - pa) / scale)
        print(f"{tag}  theta {np.round(th0, 4).tolist()} |1/d leaf - tight| "
              f"{abs(b['fitted_inverse_dim'] - th0[1] / 2):.1e}  cond(H) {cond:.2e} "
              f"eig_min {eig[0]:.3e}  A_j {np.round(A, 4).tolist()}  "
              f"max|psi| {scale:.3f}  sd(psi_an over x) {psi_an.std():.3f}  "
              f"rel err h=1e-3 {np.max(np.abs(num[1e-3] - psi_an)) / scale:.2e}  "
              f"order {orders[-1]:.2f}")
    print("\n== tight fit, central difference: max over 12 cells x 60 points of "
          "|num - IF| / max|IF| (ratio; 1/d in brackets)")
    for h in worst:
        print(f"  h = {h:.0e}: {worst[h]:.2e}  [{worst_inv[h]:.2e}]")
    print(f"  observed order (h = 4e-3, 2e-3, 1e-3): min {min(orders):.2f} "
          f"median {np.median(orders):.2f} max {max(orders):.2f}")
    print("== production fit (curve_fit defaults, 2-point Jacobian), same difference, "
          "20 points per cell: |num - IF| / max|IF|")
    for h, v in prod_err.items():
        v = np.array(v)
        print(f"  h = {h:.0e}: median {np.median(v):.2e}  p95 {np.quantile(v, 0.95):.2e}  "
              f"max {v.max():.2e}")
