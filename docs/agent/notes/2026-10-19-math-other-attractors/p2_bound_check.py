"""Numerical check of Theorem P2 (a), (b), (c) on random libraries.

P2 is a statement about a finite point set in a normed space and a perturbed
query; it uses no dynamics. We check it on (i) a library uniform on a 2-flat
in R^7 (a stand-in for a d = 2 attractor), (ii) a library on a curve (d = 1,
strongly anisotropic), (iii) a Lorenz-free adversarial two-point library where
the bound should be nearly tight, and (iv) heavy-tailed (Student-t) noise,
where only E||eta||^2 = D rho^2 is assumed (no Gaussianity).

For each state and M draws: switch indicator, ||eta|| < Delta/2 implies no
switch (a); P(switch) <= P(||eta|| >= Delta/2) <= 4 D rho^2 / Delta^2 (b);
N_M^2 <= (4/(rho^2 D)) mean[(r1 + ||eta||)^2 1{||eta|| >= Delta/2}] on the
same draws (c). Also the tightness ratio N/sqrt(B) to show when the bound is
vacuous. Exact arithmetic is not used; a violation above 1e-9 relative would
be a defect of the theorem or the script.

DEVELOPMENT, scratch seed 20261019, numpy only.
"""

import numpy as np
from scipy.spatial import cKDTree
from scipy.stats import beta

rng = np.random.default_rng(20261019)
D, M = 7, 400


def check(name, lib, queries, noise_fn, rho):
    tree = cKDTree(lib)
    d, p = tree.query(queries, k=2)
    r1, r2 = d[:, 0], d[:, 1]
    delta = r2 - r1
    n = len(queries)
    eta = rho * noise_fn((n, M, D))  # noise at level rho (a unit draw was a bug in the first run)
    eta_norm = np.linalg.norm(eta, axis=-1)
    _, pq = tree.query((queries[:, None, :] + eta).reshape(-1, D), k=1)
    pq = pq.reshape(n, M)
    switched = pq != p[:, 0][:, None]
    Y = lib[pq]
    # (a)
    viol_a = np.sum(switched & (eta_norm < delta[:, None] / 2))
    # (b)
    p_switch = switched.mean(axis=1)
    p_eta = (eta_norm >= delta[:, None] / 2).mean(axis=1)
    markov = np.minimum(1.0, 4 * D * rho**2 / np.maximum(delta, 1e-300) ** 2)
    viol_b1 = np.sum(p_switch > p_eta + 1e-12)
    # population Markov bound against the empirical P(||eta|| >= Delta/2): a
    # Monte Carlo quantity; count states whose exact Clopper-Pearson 99.9%
    # lower bound on P(||eta|| >= Delta/2) exceeds the Markov bound (a
    # binomial SE is 0 when every draw exceeds, so it cannot be used)
    kk = (eta_norm >= delta[:, None] / 2).sum(axis=1)
    p_lo = np.where(kk > 0, beta.ppf(0.001, np.maximum(kk, 1), M - kk + 1), 0.0)
    viol_b2 = np.sum(p_lo > markov)
    # (c)
    N2 = np.mean(np.sum((Y - Y.mean(axis=1, keepdims=True)) ** 2, axis=-1), axis=1) / (rho**2 * D)
    B = 4 * np.mean((r1[:, None] + eta_norm) ** 2 * (eta_norm >= delta[:, None] / 2), axis=1) / (rho**2 * D)
    viol_c = np.sum(N2 > B * (1 + 1e-9) + 1e-300)
    pos = B > 0
    tight = np.sqrt(N2[pos] / B[pos]) if pos.any() else np.array([np.nan])
    print(f"{name}")
    print(f"   states {n}, draws {M}, rho {rho:g}; median r1/rho {np.median(r1/rho):.2f}, "
          f"median Delta/rho {np.median(delta/rho):.2f}, switching states {np.sum(p_switch>0)}")
    print(f"   (a) switches with ||eta|| < Delta/2: {viol_a}   (expected 0)")
    print(f"   (b) P(switch) > P(||eta||>=Delta/2): {viol_b1};  CP99.9% lower bound of P(||eta||>=Delta/2) > Markov: {viol_b2}  (expected 0, 0)")
    print(f"   (c) N^2 > B on the same draws: {viol_c}   (expected 0)")
    print(f"   tightness N/sqrt(B) over states with B>0: median {np.median(tight):.3f}, "
          f"p90 {np.quantile(tight, .9):.3f}, max {tight.max():.3f}; states with B = 0: {np.sum(~pos)}")
    print(f"   fraction of draws that switch {switched.mean():.4f}; Markov bound mean {markov.mean():.3f} "
          f"(vacuous (>=1) at {np.mean(markov>=1):.2f} of states)")


gauss = lambda shape: rng.standard_normal(shape)


def student(shape, df=3):
    t = rng.standard_t(df, shape)
    return t / np.sqrt(df / (df - 2))  # unit variance per coordinate


# (i) 2-flat in R^7
basis = np.linalg.qr(rng.standard_normal((D, 2)))[0]
lib = (rng.random((10_000, 2)) * 2 - 1) @ basis.T
qs = (rng.random((500, 2)) * 1.8 - 0.9) @ basis.T
for rho in (0.003, 0.01, 0.03):
    check(f"(i) uniform 2-flat, Gaussian noise", lib, qs, gauss, rho)
# (ii) curve (d = 1): points along a helix-like curve in R^7
t = rng.random(10_000) * 20
curve = lambda t: np.stack([np.cos(t), np.sin(t), 0.1 * t, np.cos(2 * t), np.sin(3 * t), 0.05 * t**2 / 20, np.cos(0.5 * t)], axis=1)
check("(ii) curve d=1, Gaussian noise", curve(t), curve(rng.random(500) * 19 + 0.5), gauss, 0.01)
# (iii) adversarial: two library points on a line, query between them with margin exactly 2*rho*sqrt(D)*0.5
rho = 0.01
margin = 2 * rho * np.sqrt(D) * 0.5
lib3 = np.zeros((2, D))
lib3[0, 0] = -0.05
lib3[1, 0] = 0.05 + margin
check("(iii) two-point adversarial library, Gaussian noise", lib3, np.zeros((200, D)), gauss, rho)
# (iv) heavy-tailed noise on the 2-flat (only E||eta||^2 = D rho^2 assumed)
check("(iv) uniform 2-flat, Student-t(3) noise (unit variance)", lib, qs, student, 0.01)
