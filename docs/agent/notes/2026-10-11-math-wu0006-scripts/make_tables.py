"""Markdown tables of the WU-0006 reference predictions from the saved replication arrays."""
import numpy as np
from m2_pfail import TRUTH, VERD, p_fail_cov, p_fail_rate, COV_MIN, EDGE_MAX
from m2_ranges import rng_counts
N = {"C8": 300, "C9": 300}
INF = {"C1": 0.30, "C2": 0.16, "C3": 0.19, "C4": 0.16, "C5": 0.16, "C6": "<=0.09", "C7": "<=0.09",
       "C8": 0.30, "C9": 0.19}
cases = ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"]
print("| Case | n | infl. lag-1 at phi=0.3 | phi | 95%: coverage (SE) | P(A1 fails) | range | "
      "98.3%: coverage (SE) | P(A2 fails) | range |")
print("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
tot = {}
for phi in ("0", "0.3"):
    for case in cases:
        a = np.load(f"cov_{case}_{phi}.npy"); R = len(a); tr = TRUTH[case]; cells = []
        for j in (0, 1):
            lo, hi = a[:, 2 * j], a[:, 2 * j + 1]
            p = np.mean((lo <= tr) & (tr <= hi)); se = np.sqrt(p * (1 - p) / R)
            pf = p_fail_cov(p, se, COV_MIN[j]); k = rng_counts(p, se)
            tot.setdefault(phi, []).append(pf)
            cells += [f"{p:.4f} ({se:.4f})", f"{pf:.2f}", f"[{k[0]}, {k[1]}]"]
        print(f"| {case} | {N.get(case, 500)} | {INF[case]} | {phi} | " + " | ".join(cells) + " |")
print()
print("| Case | level | phi | P(pass) at edge (ref) | P(A3-pass fails) | range | P(fail) at edge (ref) | "
      "P(A3-fail fails) | range |")
print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
for phi in ("0", "0.3"):
    for case in VERD:
        a = np.load(f"cov_{case}_{phi}.npy"); R = len(a); tr = TRUTH[case]
        j, side = VERD[case]; lo, hi = a[:, 2 * j], a[:, 2 * j + 1]
        above, below = np.mean(tr > hi), np.mean(tr < lo)
        qp, qf = (above, below) if side == "above" else (below, above)
        cells = []
        for q in (qp, qf):
            se = np.sqrt(q * (1 - q) / R); pf = p_fail_rate(q, se, EDGE_MAX[j]); k = rng_counts(q, se)
            tot[phi].append(pf); cells += [f"{q:.4f}", f"{pf:.2f}", f"[{k[0]}, {k[1]}]"]
        print(f"| {case} | {['95%', '98.3%'][j]} | {phi} | " + " | ".join(cells) + " |")
print()
for phi, v in tot.items():
    v = np.array(v)
    print(f"phi={phi}: {len(v)} A1-A3 assertions; E[# ROADMAP-bound failures | correct code] = {v.sum():.2f}; "
          f"P(>=1) (independence) = {1 - np.prod(1 - v):.2f}")
print()
print("| Case | phi | 95% coverage (SE) | 98.3% coverage (SE) |")
print("| --- | --- | --- | --- |")
import glob
for f in sorted(glob.glob("cov_C1_0.[12].npy")) + sorted(glob.glob("cov_C[24]_0_sigma*.npy")):
    a = np.load(f); R = len(a); case = f.split("_")[1]; tr = TRUTH[case]; cells = []
    for j in (0, 1):
        lo, hi = a[:, 2 * j], a[:, 2 * j + 1]; p = np.mean((lo <= tr) & (tr <= hi))
        cells.append(f"{p:.4f} ({np.sqrt(p*(1-p)/R):.4f})")
    print(f"| {f[4:-4]} | | " + " | ".join(cells) + " |")
