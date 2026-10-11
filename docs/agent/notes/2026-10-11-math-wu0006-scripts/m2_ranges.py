"""Reference predictions and consistency count ranges (R_test = 1000) for A1/A2/A3.

Range: central 1 - 0.0005 of the predictive count distribution Bin(1000, p), p ~ N(p_ref, se_ref^2)."""
import numpy as np
from scipy.stats import binom
from m2_pfail import TRUTH, VERD, p_fail_cov, p_fail_rate, COV_MIN, EDGE_MAX
gx, gw = np.polynomial.hermite_e.hermegauss(61); gw = gw / gw.sum()
RT, TAIL = 1000, 0.00025


def rng_counts(p, se):
    ks = np.arange(RT + 1)
    pm = sum(w * binom.pmf(ks, RT, np.clip(p + se * x, 1e-9, 1 - 1e-9)) for x, w in zip(gx, gw))
    c = np.cumsum(pm)
    return int(np.searchsorted(c, TAIL)), int(np.searchsorted(c, 1 - TAIL))


def main():
    tot = {"0": [], "0.3": []}
    for phi in ("0", "0.3"):
        for case in ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"):
            a = np.load(f"cov_{case}_{phi}.npy"); R = len(a); tr = TRUTH[case]
            cells = []
            for j, lab in ((0, "95"), (1, "98.3")):
                lo, hi = a[:, 2 * j], a[:, 2 * j + 1]
                p = np.mean((lo <= tr) & (tr <= hi)); se = np.sqrt(p * (1 - p) / R)
                k = rng_counts(p, se); pf = p_fail_cov(p, se, COV_MIN[j]); tot[phi].append(pf)
                cells.append(f"{lab}: {p:.4f}±{se:.4f} [{k[0]},{k[1]}] Pf={pf:.2f}")
            if case in VERD:
                j, side = VERD[case]
                lo, hi = a[:, 2 * j], a[:, 2 * j + 1]
                above, below = np.mean(tr > hi), np.mean(tr < lo)
                qp, qf = (above, below) if side == "above" else (below, above)
                for nm, q in (("P(pass)", qp), ("P(fail)", qf)):
                    se = np.sqrt(q * (1 - q) / R); k = rng_counts(q, se)
                    pf = p_fail_rate(q, se, EDGE_MAX[j]); tot[phi].append(pf)
                    cells.append(f"A3 {nm}: {q:.4f} [{k[0]},{k[1]}] Pf={pf:.2f}")
            print(f"{case} phi={phi} R_ref={R} | " + " | ".join(cells))
    for phi, v in tot.items():
        v = np.array(v)
        print(f"phi={phi}: {len(v)} A1-A3 assertions, E[#ROADMAP-bound failures]={v.sum():.2f}, "
              f"P(>=1) if independent={1-np.prod(1-v):.2f}")


if __name__ == "__main__":
    main()
