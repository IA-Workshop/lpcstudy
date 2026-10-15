"""WU-0003.3a R2: a world where the tool's kappa-hat is biased DOWN (f2-style arrays, independent states).

Difference criterion; per state i (iid, so the long-run variance is the plain variance):
  nu_F = s z1, nu_S = s z2                  draw-free MSEs (what the tool's V_i targets, c = 0)
  b_i  = beta z3                            dependence term E[X|i] - E[V_i(w_d)|i], constant over draws,
                                            uncorrelated with nu (weights near-optimal: c second order)
  X_{F,id} = nu_F + b_i + dd * u_{id}, X_{S,id} = nu_S + dd * v_{id}, d = 1..E (conditionally iid)
Tool: V_s = 2 s^2, V_d = beta^2 + 2 dd^2/E_run. Truth: state 2 s^2 + beta^2, draw 2 dd^2/E.
Seed 20261041 (make_rng), R = 2000 replicates of n = 500.
"""
import importlib.util, math, sys
from pathlib import Path
WT = Path("/home/brianm/projects/physics/chaos/lpcstudy-wt/wu/0003-3a-report"); sys.path.insert(0, str(WT))
import numpy as np
from lpcstudy.data import make_rng
spec = importlib.util.spec_from_file_location("rehearsal_report", WT / "tools" / "rehearsal_report.py")
rr = importlib.util.module_from_spec(spec); sys.modules["rehearsal_report"] = rr; spec.loader.exec_module(rr)
N, R, ER, EF = 500, 2000, 2, 4
for s, beta, dd in [(1.0, 1.0, 1.0), (1.0, 0.5, 1.0), (1.0, 1.0, 2.0)]:
    g = make_rng(20261041, "r2-down", s, beta, dd)
    kt, kh = np.empty(R), np.empty(R)
    for r in range(R):
        nf, ns, b = s * g.standard_normal(N), s * g.standard_normal(N), beta * g.standard_normal(N)
        xf = nf[:, None] + b[:, None] + dd * g.standard_normal((N, ER))
        xs = ns[:, None] + dd * g.standard_normal((N, ER))
        af, as_ = xf.mean(1), xs.mean(1)
        kt[r] = rr.kappa_estimate(nf, ns, af, as_, "diff", ER, EF, block=5)[0]
        d = af - as_
        tot = rr.block_variance(d - d.mean(), 5)
        half = ((xf[:, 0] - xf[:, 1]) - (xs[:, 0] - xs[:, 1])) / 2
        kh[r] = 1 - (1 - ER / EF) * rr.block_variance(half, 5) / tot
    vs_t, vd_t = 2 * s**2 + beta**2, 2 * dd**2 / ER
    truth = math.sqrt((vs_t + vd_t * ER / EF) / (vs_t + vd_t))
    pop = math.sqrt((2 * s**2 + (beta**2 + 2 * dd**2 / ER) * ER / EF) / (2 * s**2 + beta**2 + 2 * dd**2 / ER))
    print(f"s {s} beta {beta} dd {dd}: truth {truth:.4f}; tool estimand {pop:.4f} ({pop-truth:+.4f}); "
          f"tool mean {kt.mean():.4f} ({kt.mean()-truth:+.4f} +- {kt.std(ddof=1)/math.sqrt(R):.4f}); "
          f"half k2 mean {kh.mean():.4f} vs truth^2 {truth**2:.4f} ({kh.mean()-truth**2:+.4f} +- {kh.std(ddof=1)/math.sqrt(R):.4f}); "
          f"sd tool {kt.std(ddof=1):.3f}, sd half k2 {kh.std(ddof=1):.3f}")
