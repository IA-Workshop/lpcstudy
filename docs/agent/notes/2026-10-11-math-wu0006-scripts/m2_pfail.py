"""Predicted P(fail) per assertion, integrating Bin(R_test, p) over p ~ N(p_hat, se^2) of the reference MC."""
import numpy as np
from scipy.stats import binom, norm
TRUTH = {"C1": 0.0, "C2": 0.0, "C3": 0.0, "C4": 1.05, "C5": 0.10, "C6": 0.7, "C7": 0.1, "C8": 0.0, "C9": 0.0}
# criterion level column (0: 95%, 1: 98.3%) and the side that is "pass" ('above' = truth > hi)
VERD = {"C2": (0, "above"), "C4": (1, "above"), "C5": (0, "above"), "C6": (0, "below"),
        "C7": (1, "above"), "C8": (1, "below"), "C9": (0, "below")}
RT = 1000
COV_MIN = {0: 930, 1: 972}     # pass iff count >= ...
EDGE_MAX = {0: 39, 1: 16}      # pass iff count <= ...
gh_x, gh_w = np.polynomial.hermite_e.hermegauss(41); gh_w = gh_w / gh_w.sum()


def p_fail_cov(p, se, kmin):
    ps = np.clip(p + se * gh_x, 1e-9, 1 - 1e-9)
    return float(np.sum(gh_w * binom.cdf(kmin - 1, RT, ps)))


def p_fail_rate(q, se, kmax):
    qs = np.clip(q + se * gh_x, 1e-9, 1 - 1e-9)
    return float(np.sum(gh_w * binom.sf(kmax, RT, qs)))


def main():
    rows = []
    for phi in ("0", "0.3"):
        for case in ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"):
            try:
                a = np.load(f"cov_{case}_{phi}.npy")
            except FileNotFoundError:
                continue
            R = len(a); tr = TRUTH[case]
            line = [f"{case} phi={phi} (R_ref={R})"]
            pf_all = []
            for j in (0, 1):
                lo, hi = a[:, 2 * j], a[:, 2 * j + 1]
                cov = np.mean((lo <= tr) & (tr <= hi)); se = np.sqrt(cov * (1 - cov) / R)
                pf = p_fail_cov(cov, se, COV_MIN[j]); pf_all.append(pf)
                line.append(f"{['95','98.3'][j]}: cov {cov:.4f}±{se:.4f} P(fail A{j+1})={pf:.2f}")
            if case in VERD:
                j, side = VERD[case]
                lo, hi = a[:, 2 * j], a[:, 2 * j + 1]
                above, below = np.mean(tr > hi), np.mean(tr < lo)
                q_pass, q_fail = (above, below) if side == "above" else (below, above)
                fp = p_fail_rate(q_pass, np.sqrt(q_pass * (1 - q_pass) / R), EDGE_MAX[j])
                ff = p_fail_rate(q_fail, np.sqrt(q_fail * (1 - q_fail) / R), EDGE_MAX[j])
                pf_all += [fp, ff]
                line.append(f"A3@{['95','98.3'][j]}: P(pass)={q_pass:.4f} P(fail)={q_fail:.4f} "
                            f"P(assert fails)={fp:.2f}/{ff:.2f}")
            line.append(f"P(any of case's assertions fails | indep)={1-np.prod(1-np.array(pf_all)):.2f} "
                        f"E[#fails]={sum(pf_all):.2f}")
            print(" | ".join(line))


if __name__ == "__main__":
    main()
