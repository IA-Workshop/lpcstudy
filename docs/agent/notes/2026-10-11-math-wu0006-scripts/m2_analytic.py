"""Influence-series ACFs at latent phi and first-order MBB coverage (exact E[V*] = tr(M Sigma))."""
import numpy as np
from scipy.stats import norm
s2, c = 1.0, 0.8


def acf_case(case, phi, kmax=60):
    k = np.arange(kmax + 1); r = phi ** k
    if case == "mean":
        g = r
    elif case == "median":
        g = 2 / np.pi * np.arcsin(r)
    elif case in ("C2", "C4", "C5"):
        mu = {"C2": 0.0, "C4": np.log(1.05), "C5": np.log(1.10)}[case]
        R = {"C2": 1.0, "C4": 1.05, "C5": 1.10}[case]
        Ea, Eb = np.exp(mu + s2 / 2), np.exp(s2 / 2)
        caa = Ea * Ea * (np.exp(s2 * r) - 1); cbb = Eb * Eb * (np.exp(s2 * r) - 1)
        cab = Ea * Eb * (np.exp(s2 * c * r) - 1)
        g = caa - 2 * R * cab + R * R * cbb  # psi = a - R b (C2: R = 1, difference)
    elif case == "even2":
        g = r ** 2
    return g / g[0]


def mbb_cov(acf, n, b=5):
    """Exact Var(mean) and E*[Var*(mean*)] for the MBB with blocks of b over n items."""
    S = acf[np.abs(np.subtract.outer(np.arange(n), np.arange(n)))]
    vtrue = S.sum() / n**2
    nb = n - b + 1; k = n // b
    # block-mean vector: Bm_j = mean x[j:j+b]; Var*(mean*) = (1/k) * empirical var of the nb block means
    A = np.zeros((nb, n))
    for j in range(nb):
        A[j, j:j + b] = 1 / b
    C = np.eye(nb) - np.ones((nb, nb)) / nb
    M = A.T @ C @ A / nb / k
    ev = np.trace(M @ S)
    return vtrue, ev


for case in ("mean", "median", "C2", "C4", "C5", "even2"):
    for phi in (0.0, 0.1, 0.2, 0.3):
        g = acf_case(case, phi, 520)
        for n in ((500, 300) if case in ("mean", "median") else (500,)):
            vt, ev = mbb_cov(g, n)
            ratio = ev / vt
            covs = [2 * norm.cdf(norm.ppf(1 - (1 - L) / 2) * np.sqrt(ratio)) - 1 for L in (0.95, 1 - 0.05 / 3)]
            lr = 1 + 2 * g[1:].sum()
            print(f"{case:6s} phi={phi:.1f} n={n} acf1={g[1]:.4f} acf2={g[2]:.4f} longrun={lr:.4f} "
                  f"E[V*]/V={ratio:.4f} cov1st={covs[0]:.4f}/{covs[1]:.4f}")
