"""Percentile ranks of the development-seed V6 values in the 2026-10-13 law, and tests of the law.

Inputs: the per-state deviation arrays D_<system>.npz of the 2026-10-13 note (perstate.py, 5 orbits
x 2e5 states, CPU lambda), the v6_dev.py output (CPU, registry seeds), and the R1 GPU values
(results.json, read-only). The law is rebuilt exactly as law.py (sliding 20-state windows at the
production spacing) and checked against the committed law.log numbers before use. Nothing here
draws a random number. DEVELOPMENT.

Usage: python -I v6_ranks.py <dir with D_*.npz> <v6_dev.npz> <R1 results.json>
"""
import json
import sys

import numpy as np
from scipy import stats as st

d_dir, dev_npz, r1_json = sys.argv[1:4]
bar = 1e-3
spacing = {"lorenz63": 45, "rossler": 150, "chua": 150}
# committed law.log values (2026-10-13), for the reproduction check
logged = {"lorenz63": (1.077e-3, 3.77e-5, 1.03e-3), "rossler": (0.0, 3.72e-5, 4.45e-5),
          "chua": (4.479e-2, 1.96e-4, 1.09e-2)}
p0 = {"lorenz63": 3.925015986765526e-05, "rossler": 3.3054095038130976e-05,  # P0 results.json
      "chua": 7.544974259394876e-05}
p1 = {"lorenz63": 0.0004832547134836568, "rossler": 4.253412949499829e-05,
      "chua": 0.00029249004360848153}
dev = np.load(dev_npz)
r1 = json.load(open(r1_json))["systems"]
ranks_all = []
draws_tbl = {}
for system in ("lorenz63", "rossler", "chua"):
    D = np.load(f"{d_dir}/D_{system}.npz")["D"]
    span = 19 * spacing[system] + 1
    V = np.stack([np.lib.stride_tricks.sliding_window_view(D[o], span)[:, ::spacing[system]]
                  .max(axis=1) for o in range(D.shape[0])])
    allV = np.sort(V.ravel())
    pf = np.mean(allV >= bar)
    q50, q999 = np.quantile(allV, .5), np.quantile(allV, .999)
    ok = (f"{pf:.3e}" == f"{logged[system][0]:.3e}" and f"{q50:.2e}" == f"{logged[system][1]:.2e}"
          and f"{q999:.2e}" == f"{logged[system][2]:.2e}")
    print(f"== {system}: law rebuilt from {D.size} states, {allV.size} windows; P(V6>=1e-3) = "
          f"{pf:.4e}; median {q50:.2e}; 99.9% {q999:.2e}; matches law.log: {ok}")

    def rank(v):
        """F(v-) on the pooled law and the SD of F over the 5 orbits / sqrt(5)."""
        per = np.array([np.mean(V[o] < v) for o in range(V.shape[0])])
        return np.searchsorted(allV, v, side="left") / allV.size, per.std(ddof=1) / np.sqrt(len(per))

    rows = [("P0 (DEV-0, a5cd75b, CPU)", p0[system]), ("P1 (DEV-0, 5b3fd8f, CPU)", p1[system])]
    rows += [(f"{sid} pilot (CPU, offline)", float(dev[f"pilot|{sid}|{system}#v6"]))
             for sid in ("DEV-1", "DEV-2", "DEV-3", "DEV-4")]
    rows += [(f"{sid} full (CPU, offline)", float(dev[f"full|{sid}|{system}#v6"]))
             for sid in ("DEV-1", "DEV-2", "DEV-3", "DEV-4")]
    rows += [("R1 DEV-1 pilot (GPU lambda; other law)",
              r1[system]["validation"]["integrator_max_dev_sigma"])]
    draws_tbl[system] = []
    for name, v in rows:
        r, se = rank(v)
        surv = np.mean(allV >= v)
        flag = "FAIL" if v >= bar else "pass"
        print(f"  {name:40s} V6 {v:.3e}  {flag}  margin x{bar / v:6.2f}  rank F {r:.4f} "
              f"(+-{se:.4f})  P(V6 >= value) {surv:.3e}")
        draws_tbl[system].append((name, v, r))
        if "GPU" not in name:
            ranks_all.append((system, name, r))

print("\n== Tests of the law on the CPU draws (P0, P1, DEV-1..4 pilot, DEV-1..4 full)")
for system in ("lorenz63", "rossler", "chua"):
    r = np.array([x[2] for x in ranks_all if x[0] == system])
    ks = st.kstest(r, "uniform")
    print(f"  {system:9s} n={len(r)} ranks {np.round(np.sort(r), 3)}  KS D={ks.statistic:.3f} "
          f"p={ks.pvalue:.3f}")
r = np.array([x[2] for x in ranks_all])
ks = st.kstest(r, "uniform")
print(f"  all       n={len(r)} KS D={ks.statistic:.3f} p={ks.pvalue:.3f}; mean rank {r.mean():.3f} "
      f"(uniform: 0.5 +- {np.sqrt(1 / 12 / len(r)):.3f})")
# Fisher-type upper-tail combination: -2 sum log(1 - F) ~ chi2(2n) under the law (sensitive to
# draws that sit high in the law, i.e. a heavier tail than predicted)
fisher = -2 * np.sum(np.log(1 - np.clip(r, 0, 1 - 1e-12)))
print(f"  upper-tail Fisher statistic {fisher:.2f} on {2 * len(r)} df, p = "
      f"{st.chi2.sf(fisher, 2 * len(r)):.3f}")
fisher_lo = -2 * np.sum(np.log(np.clip(r, 1e-12, 1)))
print(f"  lower-tail Fisher statistic {fisher_lo:.2f} on {2 * len(r)} df, p = "
      f"{st.chi2.sf(fisher_lo, 2 * len(r)):.3f}")

print("\n== Failure counts against the law (binomial; draws independent, see note)")
law_p = {"lorenz63": 1.077e-3, "rossler": 0.0, "chua": 4.479e-2}
for system, sel in (("chua", None), ("lorenz63", None), ("rossler", None)):
    for label, keep in (("P0,P1 + DEV-1..4 pilot", lambda n: "full" not in n and "GPU" not in n),
                        ("+ DEV-1..4 full", lambda n: "GPU" not in n),
                        ("+ R1 (GPU)", lambda n: True)):
        vals = [v for n, v, _ in draws_tbl[system] if keep(n)]
        n, k = len(vals), int(np.sum(np.array(vals) >= bar))
        p = law_p[system]
        lo = st.beta.ppf(.025, k, n - k + 1) if k > 0 else 0.0
        hi = st.beta.ppf(.975, k + 1, n - k)
        p_ge = st.binom.sf(k - 1, n, p) if k > 0 else 1.0
        print(f"  {system:9s} {label:24s} n={n:2d} failures k={k}  direct {k / n:.3f} "
              f"[Clopper-Pearson 95% {lo:.4f}, {hi:.3f}]  law {p:.4f}: P(K>={k}) = {p_ge:.3f}, "
              f"P(K=0) = {(1 - p) ** n:.3f}")
