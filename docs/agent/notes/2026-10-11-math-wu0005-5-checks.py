"""WU-0005.5a scratch checks (applied-mathematician, 2026-10-11). Synthetic data only, CPU.

Regenerates every number in the "WU-0005.5a design" block of
docs/agent/records/work/WU-0005.5-p2c-bound.md. It is independent of lpcstudy/ (a
prototype of the P2(c) check, not the implementation). No study seed is used: the
Lorenz-63 library below is a self-made trajectory, not ctx data. Runtime about 1 min.

    OMP_NUM_THREADS=4 .venv/bin/python docs/agent/notes/2026-10-11-math-wu0005-5-checks.py
"""

import numpy as np
from scipy import integrate
from scipy import special as sp
from scipy.spatial import cKDTree
from scipy.stats import norm

U = 2.0**-53
KAPPA = 1e-13
D = 7


# ----------------------------------------------------------------------------- B_inf (M6)
def g_tail(j, t):
    """E[chi_D^j 1{chi_D >= t}] in closed form."""
    return 2 ** (j / 2) * sp.poch(D / 2, j / 2) * sp.gammaincc((D + j) / 2, t * t / 2)


def binf_inner(r1, rho, delta):
    """E[(r1 + ||eta||)^2 1{||eta|| >= delta/2}], eta ~ N(0, rho^2 I_D)."""
    t = delta / (2 * rho)
    return r1**2 * g_tail(0, t) + 2 * r1 * rho * g_tail(1, t) + rho**2 * g_tail(2, t)


def var_b(r1, rho, delta):
    """Variance of one per-draw term b_r and B_inf (B_M = mean_r b_r)."""
    t = delta / (2 * rho)
    c = 4 / (rho**2 * D)
    m2 = sum(sp.comb(4, k) * r1 ** (4 - k) * rho**k * g_tail(k, t) for k in range(5))
    m1 = binf_inner(r1, rho, delta)
    return c * c * (m2 - m1 * m1), c * m1


def quad_ref(r1, rho, delta):
    t = delta / (2 * rho)

    def f(x):
        if x <= 0:
            return 0.0
        return (r1 + rho * x) ** 2 * np.exp((D - 1) * np.log(x) - x * x / 2
                                            - (D / 2 - 1) * np.log(2) - sp.gammaln(D / 2))
    pts = sorted({t, max(t, np.sqrt(D - 1)), max(t, 12.0), max(t, 40.0)})
    total = 0.0
    for a, b in zip(pts[:-1], pts[1:]):
        total += integrate.quad(f, a, b, epsabs=0, epsrel=1e-13, limit=200)[0]
    return total + integrate.quad(f, pts[-1], np.inf, epsabs=0, epsrel=1e-13, limit=200)[0]


def check_u1():
    worst = 0.0
    for r in (0, 1, 10):
        for d in (0, 0.5, 2, 8, 16):
            cf, q = binf_inner(r, 1.0, d), quad_ref(r, 1.0, d)
            worst = max(worst, abs(cf - q) / q)
    print(f"U1 worst relative closed-form vs quad: {worst:.2e}")
    print("U1 Delta=0: G0-1 =", g_tail(0, 0) - 1, " G2-D =", g_tail(2, 0) - D)
    rng = np.random.default_rng(1)
    for r1, dr in [(0.5, 0.5), (0.5, 2), (5, 4), (0.1, 8)]:
        rho, m, reps = 0.1, 200, 20000
        nr = np.linalg.norm(rng.standard_normal((reps, m, D)) * rho, axis=-1)
        bm = (4 / (rho**2 * D) * (r1 + nr) ** 2 * (nr >= dr * rho / 2)).mean(1)
        v, binf = var_b(r1, rho, dr * rho)
        print(f"MC law r1={r1} Delta/rho={dr}: z(mean)={(bm.mean() - binf) / np.sqrt(v / m / reps):.2f}"
              f" sd/pred={bm.std() / np.sqrt(v / m):.4f}")


# ----------------------------------------------------------------------------- prototype check
def retrieval_spread(analog_vecs, noise):
    """Verbatim copy of lpcstudy.ensemble.retrieval_spread."""
    centered = analog_vecs - analog_vecs.mean(axis=-2, keepdims=True)
    dim = analog_vecs.shape[-1]
    return np.sqrt(np.mean(np.sum(centered**2, axis=-1), axis=-1) / dim) / noise


def p2_terms(lib, clean, z, rho, offset_bug=False):
    tree = cKDTree(lib)
    n, m, dim = z.shape
    d2, p2 = tree.query(clean, k=2)
    r1, r2, i1 = d2[:, 0], d2[:, 1], p2[:, 0]
    delta = r2 - r1
    q = clean[:, None, :] + rho * z
    dq, pos = tree.query(q.reshape(-1, dim), k=1)
    pos, dq = pos.reshape(n, m), dq.reshape(n, m)
    y = tree.data[np.minimum(pos + 1, len(lib) - 1)] if offset_bug else tree.data[pos]
    x1 = tree.data[i1][:, None, :]
    n_m = retrieval_spread(y, rho)
    eta = np.linalg.norm(q - clean[:, None, :], axis=-1)
    slack = KAPPA * (r2[:, None] + eta)
    dist = np.linalg.norm(y - x1, axis=-1)
    sw = pos != i1[:, None]
    c = 1 / (rho**2 * dim)
    a_m = c * np.mean(dist**2, axis=-1)
    b_m = 4 * c * np.mean((r1[:, None] + eta) ** 2 * (eta >= delta[:, None] / 2), axis=-1)
    b_sw = 4 * c * np.mean((r1[:, None] + eta) ** 2 * sw, axis=-1)
    b_plus = 4 * c * np.mean((r1[:, None] + eta) ** 2 * (eta >= delta[:, None] / 2 - slack), axis=-1)
    tau = m * U * np.abs(y).max(axis=(1, 2)) / rho
    dqy = np.linalg.norm(q - y, axis=-1)
    viol = {
        "p2a": int(np.sum(sw & (eta < delta[:, None] / 2 - slack))),
        "triangle": int(np.sum(dist > 2 * (r1[:, None] + eta) * (1 + KAPPA))),
        "consistency": int(np.sum(np.abs(dqy - dq) > KAPPA * np.maximum(dqy, dq)))
        + int(np.sum(np.abs(np.linalg.norm(clean - tree.data[i1], axis=-1) - r1) > KAPPA * r1)),
        "N_le_A": int(np.sum(n_m**2 > a_m * (1 + KAPPA) + tau**2)),
        "A_le_B": int(np.sum(a_m > b_plus * (1 + 4 * KAPPA))),
        "headline": int(np.sum(n_m**2 > b_plus * (1 + 5 * KAPPA) + tau**2)),
        "band_draws": int(np.sum(np.abs(eta - delta[:, None] / 2) <= slack)),
    }
    return dict(r1=r1, delta=delta, N=n_m, A=a_m, B=b_m, Bsw=b_sw, tau=tau, sw=sw, dist=dist,
                eta=eta, viol=viol, pos=pos, y=y, x1=x1)


def check_u2_u3_tau():
    rho, m = 0.02, 200
    g = np.random.default_rng(7)
    x1 = np.zeros(D)
    x1[0] = 0.5
    others = []
    while len(others) < 40:
        v = np.round(g.uniform(-4, 4, D) * 16) / 16
        if np.linalg.norm(v) >= 1.5:
            others.append(v)
    lib = np.vstack([x1] + others)
    gen = g.standard_normal(lib.shape)
    gen *= np.linalg.norm(lib, axis=1, keepdims=True) / np.linalg.norm(gen, axis=1, keepdims=True)
    for name, lb in (("U2 dyadic", lib), ("U3 generic", gen)):
        z = np.random.default_rng(50055).standard_normal((1, m, D))
        t = p2_terms(lb, np.zeros((1, D)), z, rho)
        print(f"{name}: N={t['N'][0]:.3e} A={t['A'][0]} B={t['B'][0]} tauN={t['tau'][0]:.3e} {t['viol']}")
    for m in (200, 30):
        g = np.random.default_rng(11)
        worst = max(retrieval_spread(np.broadcast_to(v, (1, m, D)).copy(), 0.01)[0]
                    / (m * U * np.abs(v).max() / 0.01)
                    for v in (g.standard_normal(D) * g.uniform(0.1, 3) for _ in range(20000)))
        print(f"tau_N: M={m} worst centring residue / tau_N over 2e4 vectors = {worst:.3f}")


def collinear(r1_over_rho, seed, rho=0.1, m=200, grid=(0.5, 1, 2, 4, 8, 16), per=50):
    rng = np.random.default_rng(seed)
    out = []
    for g in grid:
        for _ in range(per):
            r1, de = r1_over_rho * rho, g * rho
            x1, x2 = np.zeros(D), np.zeros(D)
            x1[0], x2[0] = r1, -(r1 + de)
            dirs = rng.standard_normal((20, D))
            dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
            lib = np.vstack([x1, x2, dirs * (r1 + de + 20 * rho)])
            out.append((g, p2_terms(lib, np.zeros((1, D)), rng.standard_normal((1, m, D)), rho)))
    return out


def check_u4_u5():
    rho, m = 0.1, 200
    for name, r1r, seed in (("U4", 5, 50056), ("U5", 50, 50057)):
        out = collinear(r1r, seed)
        tot = {k: sum(t["viol"][k] for _, t in out) for k in out[0][1]["viol"]}
        n_sw = sum(t["sw"].any() for _, t in out)
        n_dis = sum(int(np.sum(~np.isin(t["pos"], [0, 1]))) for _, t in out)
        ratio = max((t["dist"][0][t["sw"][0]] / (2 * (t["r1"][0] + t["eta"][0][t["sw"][0]]))).max()
                    for _, t in out if t["sw"].any())
        ab = max(t["A"][0] / t["B"][0] for _, t in out if t["B"][0] > 0)
        e_n = e_a = e_i = 0.0
        for _, t in out:
            p = t["sw"][0].mean()
            big_l = 2 * t["r1"][0] + t["delta"][0]
            n_ref = np.sqrt(big_l**2 * p * (1 - p) / (rho**2 * D))
            a_ref = big_l**2 * p / (rho**2 * D)
            e_n = max(e_n, abs(t["N"][0] - n_ref) / (t["tau"][0] + KAPPA * n_ref))
            if a_ref > 0:
                e_a = max(e_a, abs(t["A"][0] - a_ref) / (KAPPA * a_ref))
                hu = np.sum((t["y"][0].mean(0) - t["x1"][0, 0]) ** 2) / (rho**2 * D)
                e_i = max(e_i, abs(t["N"][0] ** 2 - (t["A"][0] - hu))
                          / (t["tau"][0] ** 2 + 2 * KAPPA * t["A"][0]))
        print(f"{name}: {tot} switching states {n_sw}/300, distractor retrievals {n_dis}, "
              f"max per-draw ratio {ratio:.4f}, max A/B {ab:.4f}; reference errors in units of "
              f"tolerance: N {e_n:.4f}, A {e_a:.4f}, Huygens {e_i:.4f}")
    p = [1 - (1 - norm.cdf(-g / 2)) ** m for g in (0.5, 1, 2, 4, 8, 16)]
    print("P(state switches) per grid value", np.round(p, 4), "E[#switching] =", 50 * sum(p))


def lorenz_series():
    def f(s):
        x, y, z = s[..., 0], s[..., 1], s[..., 2]
        return np.stack([10 * (y - x), x * (28 - z) - y, x * y - 8 / 3 * z], -1)

    def rk4(s, h):
        k1 = f(s)
        k2 = f(s + h / 2 * k1)
        k3 = f(s + h / 2 * k2)
        k4 = f(s + h * k3)
        return s + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    dt, sub = 1 / (0.905 * 30), 4
    s = np.array([1.0, 1.0, 20.0])
    for _ in range(3000 * sub):
        s = rk4(s, dt / sub)
    xs = np.empty(10000 + 60 + 60000)
    for t in range(len(xs)):
        for _ in range(sub):
            s = rk4(s, dt / sub)
        xs[t] = s[0]
    return (xs - xs.mean()) / xs.std()


def check_lorenz():
    xs = lorenz_series()

    def dv(series, idx):
        return series[idx[:, None] - np.arange(D)[None, :] * 5]
    rng = np.random.default_rng(424242)
    libser, evalser = xs[:12000], xs[12500:]
    idx_lib, idx_ev = np.arange(30, 10030), np.arange(30, 30 + 1400 * 30, 30)
    clean = dv(evalser, idx_ev)
    libnoise = rng.standard_normal(len(libser))
    z = rng.standard_normal((1400, 200, D))
    for rho in (0.01, 0.05):
        lib = dv(libser + rho * libnoise, idx_lib)
        t = p2_terms(lib, clean, z, rho)
        sw, b = t["sw"].any(1), t["B"]
        binf = np.array([binf_inner(a, rho, d) for a, d in zip(t["r1"], t["delta"])]) * 4 / (rho**2 * D)
        vb = np.array([var_b(a, rho, d)[0] for a, d in zip(t["r1"], t["delta"])])
        tight = t["N"][b > 0] / np.sqrt(b[b > 0])
        print(f"Lorenz rho={rho}: {t['viol']}")
        print("   Delta/rho q01 q10 q50 q90", np.round(np.quantile(t["delta"] / rho, [.01, .1, .5, .9]), 3),
              " median r1/rho", np.round(np.median(t["r1"] / rho), 2))
        print(f"   switching states {sw.sum()}/1400, switching draws {t['sw'].mean():.4f}, "
              f"B=0 states {(b == 0).sum()}, N/sqrtB median p90 max", np.round(np.quantile(tight, [.5, .9, 1]), 3))
        print("   medians over switching states: N2/A", np.round(np.median(t["N"][sw] ** 2 / t["A"][sw]), 3),
              " A/Bsw", np.round(np.median(t["A"][sw] / t["Bsw"][sw]), 3),
              " Bsw/B", np.round(np.median(t["Bsw"][sw] / b[sw]), 3))
        print(f"   sum N2 / sum Binf {(t['N'] ** 2).sum() / binf.sum():.4f}; states N2>Binf "
              f"{(t['N'] ** 2 > binf).sum()}; z(sum B_M - sum Binf) {(b.sum() - binf.sum()) / np.sqrt(vb.sum() / 200):.2f}; "
              f"noise 2nd moment {(t['eta'] ** 2).mean() / (D * rho**2):.5f} (SE {np.sqrt(2 / z.size):.5f}); "
              f"max tauN {t['tau'].max():.2e}; max N non-switching {t['N'][~sw].max():.2e}")
        if rho == 0.01:
            print("   OFFSET-BUG MUTANT:", p2_terms(lib, clean, z, rho, offset_bug=True)["viol"])


def check_chunking():
    rng = np.random.default_rng(3)
    for m, per in ((200, 30), (30, 200)):
        lib = rng.standard_normal((50, D)) * 1.3
        y = lib[rng.integers(0, 50, (1400, m))]
        full = retrieval_spread(y, 0.01)
        chunks = np.concatenate([retrieval_spread(y[s:s + per], 0.01) for s in range(0, 1400, per)])
        print(f"retrieval_spread chunk-invariant (M={m}, chunks of {per}): {np.array_equal(full, chunks)}")


if __name__ == "__main__":
    check_u1()
    check_chunking()
    check_u2_u3_tau()
    check_u4_u5()
    check_lorenz()
