"""WU-0006.4 A9: N1, N2, N3 reference rates, predicted P(fail) and consistency ranges at 3000/1000.

Input: ``dr2ref_<phi>.npy`` (``dr2_full_ref.py``) in the current directory; 8 columns per target
(estimate, lo, hi, conditional truth, truth SE, refit bitwise, failed resamples, R2_three).
Range rule: the same as for the other WU-0006 ranges (``m2_ranges``), here for R_test = 500:
central 1 - 0.0005 interval of Bin(500, p) mixed over p ~ N(p_ref, se_ref^2) (61-point
Gauss-Hermite). P(fail): probability that the slow test's bound fails (N1, N3: count < 461;
N2: count > 22), with the same mixing.
"""
import numpy as np
from scipy.stats import binom

RT, TAIL = 500, 0.00025
N_MIN, N2_MAX = 461, 22
gx, gw = np.polynomial.hermite_e.hermegauss(61)
gw = gw / gw.sum()


def mix(p, se):
    return np.clip(p + se * gx, 1e-9, 1 - 1e-9)


def count_range(p, se):
    ks = np.arange(RT + 1)
    pm = sum(w * binom.pmf(ks, RT, q) for q, w in zip(mix(p, se), gw))
    c = np.cumsum(pm)
    return int(np.searchsorted(c, TAIL)), int(np.searchsorted(c, 1 - TAIL))


def p_below(p, se, kmin):
    return float(np.sum(gw * binom.cdf(kmin - 1, RT, mix(p, se))))


def p_above(p, se, kmax):
    return float(np.sum(gw * binom.sf(kmax, RT, mix(p, se))))


def main():
    tot = []
    for phi in ("0", "0.3"):
        a = np.load(f"dr2ref_{phi}.npy")
        R = len(a)
        for j, name in enumerate(("logit_w_interior", "w_zero_indicator")):
            est, lo, hi, tr, trse, same, nf, r3 = a[:, 8 * j: 8 * j + 8].T
            hw = (hi - lo) / 2
            rates = {"N1": np.mean((lo <= 0) & (0 <= hi)), "N2": np.mean(lo > 0),
                     "N3": np.mean((lo <= tr) & (tr <= hi))}
            cells = []
            for key, p in rates.items():
                se = np.sqrt(p * (1 - p) / R)
                pf = p_above(p, se, N2_MAX) if key == "N2" else p_below(p, se, N_MIN)
                pf_point = p_above(p, 0, N2_MAX) if key == "N2" else p_below(p, 0, N_MIN)
                rng = count_range(p, se)
                if key != "N1":
                    tot.append(pf)
                cells.append(f"{key} {p:.4f} (se {se:.4f}) P(fail) {pf:.3f} [point {pf_point:.3f}] "
                             f"range {rng}")
            print(f"phi={phi} {name} R_ref={R}: mean gain {tr.mean():.5f} sd {tr.std():.5f} "
                  f"P(gain>0) {np.mean(tr > 0):.3f} mean half-width {hw.mean():.4f} "
                  f"truth<lo {np.mean(tr < lo):.4f} truth>hi {np.mean(tr > hi):.4f} "
                  f"truthSE/hw mean {np.mean(trse / hw):.3f} max {np.max(trse / hw):.3f} "
                  f"refit bitwise {same.mean():.3f} failed {nf.sum():.0f} R2_three {r3.mean():.3f}")
            for c in cells:
                print("    " + c)
    tot = np.array(tot)
    print(f"N2+N3 always-asserted rows (8): expected failures per run of the slow file "
          f"{tot.sum():.2f}; P(at least one) (independence) {1 - np.prod(1 - tot):.3f}")


if __name__ == "__main__":
    main()
