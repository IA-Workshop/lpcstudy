"""WU-0003.3a R2: coverage of kappa^2 by the half-split estimator +- 2 block-jackknife SE.

Delete-a-block jackknife, 20 contiguous blocks of 25 states (n = 500), deterministic (no random
number in the estimator). Worlds S2, S4, S10 of r2_kappa_sim.py (truth from r2_kappa_sim.log, R =
1000) and the toy of r2_kappa_down.py (exact truth). Seed 20261042 (make_rng), R = 400 per world.
"""
import importlib.util, math, sys
sys.argv = [sys.argv[0], "1"]
spec = importlib.util.spec_from_file_location("sim", "r2_kappa_sim.py"); sim = importlib.util.module_from_spec(spec); spec.loader.exec_module(sim)
import numpy as np
from lpcstudy.data import make_rng
rr, bv = sim.rr, sim.bv
R, NB = 400, 20
r = sim.E_RUN / sim.E_FULL

def k2_half(kind, xf, xs):
    af, as_ = xf.mean(1), xs.mean(1)
    hf, hs = (xf[:, 0] - xf[:, 1]) / 2, (xs[:, 0] - xs[:, 1]) / 2
    if kind == "diff":
        d = af - as_; tot = bv(d - d.mean()); h = hf - hs
    else:
        tot = bv(rr.influence_ratio(af, as_)); h = (hf - af.mean() / as_.mean() * hs) / as_.mean()
    return 1 - (1 - r) * bv(h) / tot

def jack(kind, xf, xs):
    n = len(xf); edges = np.linspace(0, n, NB + 1).astype(int)
    full = k2_half(kind, xf, xs)
    th = np.array([k2_half(kind, np.delete(xf, slice(edges[j], edges[j+1]), 0),
                           np.delete(xs, slice(edges[j], edges[j+1]), 0)) for j in range(NB)])
    se = math.sqrt((NB - 1) / NB * ((th - th.mean())**2).sum())
    return full, se

TRUTH = {"S2 dependent sa .5": {"H2c A4-A2": .7614, "H2c A4-A1": .7701, "H2d A4/A3": .7081, "H3c A5/A4": .7143},
         "S4 dependent sa 1": {"H2c A4-A2": .7126, "H2c A4-A1": .7123, "H2d A4/A3": .7065, "H3c A5/A4": .7083},
         "S10 pipeline-like light states, dependent": {"H2c A4-A2": .7248, "H2c A4-A1": .7342, "H2d A4/A3": .7079, "H3c A5/A4": .7076}}
for name, tr in TRUTH.items():
    par = sim.SCEN[name]
    hits = {c: 0 for c in tr}; ses = {c: [] for c in tr}
    for rep in range(R):
        g = make_rng(20261042, "r2-jack", name, rep)
        z1, z2, z3 = sim.ar1(g, sim.N), sim.ar1(g, sim.N), sim.ar1(g, sim.N)
        ls, lg = par[3], par[4]
        sC, sP, gain = np.exp(-1.0 + ls * z1), np.exp(-1.2 + ls * z2), np.exp(lg * z3)
        w, ec, ep = sim.draws(g, sC, sP, gain, 2, *par[:3])
        X = {k: (w[k] * ec + (1 - w[k]) * ep) ** 2 for k in w}
        for c, (kind, f, s) in sim.CRITERIA.items():
            k2, se = jack(kind, X[f], X[s])
            ses[c].append(se)
            hits[c] += abs(k2 - tr[c]**2) <= 2 * se
    print(name, "; ".join(f"{c}: cover {hits[c]/R:.3f}, median SE(k2) {np.median(ses[c]):.3f}" for c in tr))
# toy (iid states)
for s_, beta, dd in [(1.0, 1.0, 1.0), (1.0, 1.0, 2.0)]:
    vs_t, vd_t = 2 * s_**2 + beta**2, 2 * dd**2 / 2
    k2t = (vs_t + vd_t * r) / (vs_t + vd_t)
    g = make_rng(20261042, "r2-jack-toy", s_, beta, dd); hit = 0; sel = []
    for rep in range(R):
        nf, ns, b = s_ * g.standard_normal(500), s_ * g.standard_normal(500), beta * g.standard_normal(500)
        xf = nf[:, None] + b[:, None] + dd * g.standard_normal((500, 2)); xs = ns[:, None] + dd * g.standard_normal((500, 2))
        k2, se = jack("diff", xf, xs); hit += abs(k2 - k2t) <= 2 * se; sel.append(se)
    print(f"toy s {s_} beta {beta} dd {dd}: cover {hit/R:.3f}, median SE(k2) {np.median(sel):.3f}")
