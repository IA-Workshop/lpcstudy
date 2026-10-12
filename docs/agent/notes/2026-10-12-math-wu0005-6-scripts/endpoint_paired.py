"""WU-0005.6 mathematics check, E2: paired (common-index) bootstrap endpoint changes.

DEVELOPMENT (synthetic; literal default_rng seeds; not a study seed). Independent of lpcstudy:
own moving-block bootstrap (block 5), np.quantile linear, level 1 - 0.05/3.
Questions: (1) is |d endpoint| <= max_b |d T_b| (1-Lipschitz); (2) how does the endpoint change
compare with the point change and with the endpoint MC SE; (3) what is the MC noise of the
endpoint change itself at B = 500 and 2000 (against B = 20000).
"""
import numpy as np

LEVEL = 1 - 0.05 / 3
A = (1 - LEVEL) / 2


def block_idx(rng, n, B, block=5):
    n_blocks = -(-n // block)
    starts = rng.integers(0, n - block + 1, size=(B, n_blocks))
    idx = (starts[:, :, None] + np.arange(block)).reshape(B, -1)[:, :n]
    return idx


def mc_se(vals, q):
    B = len(vals)
    d = np.sqrt(q * (1 - q) / B)
    return (np.quantile(vals, q + d) - np.quantile(vals, q - d)) / 2


def study(kind, n, B_list, n_rep, seed):
    rng = np.random.default_rng(seed)
    rows = []
    for rep in range(n_rep):
        if kind == "median":   # H2a(i)-like: median of positive skewed ranges, eligibility flag
            x = rng.gamma(2.0, 0.08, n)
            elig15 = rng.random(n) < 0.7
            delta = np.zeros(n)
            mv = rng.random(n) < 0.05
            delta[mv] = rng.normal(0, 0.05, mv.sum())
            x30 = np.clip(x + delta, 0, None)
            elig30 = elig15.copy()
            flip = rng.choice(n, 3, replace=False)
            elig30[flip] = ~elig30[flip]

            def stat(idx, xx, el):
                sel = idx[el[idx]]
                return np.median(xx[sel])
            args15, args30 = (x, elig15), (x30, elig30)
        else:                  # H2b-like: mean of per-state values in [-1, 1], sparse large moves
            x = np.clip(rng.normal(0.2, 0.6, n), -1, 1)
            delta = np.zeros(n)
            mv = rng.random(n) < 0.02
            delta[mv] = rng.normal(0, 0.3, mv.sum())
            x30 = np.clip(x + delta, -1, 1)

            def stat(idx, xx):
                return xx[idx].mean(axis=-1)
            args15, args30 = (x,), (x30,)
        full = np.arange(n)
        p15, p30 = stat(full, *args15), stat(full, *args30)
        out = {"dpt": p30 - p15}
        for B in B_list:
            idx = block_idx(np.random.default_rng(1000 + rep), n, B)
            if kind == "median":
                t15 = np.array([stat(i, *args15) for i in idx])
                t30 = np.array([stat(i, *args30) for i in idx])
            else:
                t15, t30 = stat(idx, *args15), stat(idx, *args30)
            lo15, hi15 = np.quantile(t15, [A, 1 - A])
            lo30, hi30 = np.quantile(t30, [A, 1 - A])
            db = t30 - t15
            out[B] = dict(hw=(hi15 - lo15) / 2, dlo=lo30 - lo15, dhi=hi30 - hi15,
                          lip=max(abs(lo30 - lo15), abs(hi30 - hi15)) <= np.abs(db).max() + 1e-15,
                          se=max(mc_se(t15, A), mc_se(t15, 1 - A)), sd_db=db.std())
        rows.append(out)
    Bmax = B_list[-1]
    print(f"\n== {kind}, n = {n}, {n_rep} data sets; reference B = {Bmax}")
    print("   Lipschitz bound |d endpoint| <= max_b |d T_b| held in all:",
          all(r[B]["lip"] for r in rows for B in B_list))
    hw = np.array([r[Bmax]["hw"] for r in rows])
    for B in B_list[:-1]:
        e_lo = np.array([r[B]["dlo"] - r[Bmax]["dlo"] for r in rows]) / hw
        e_hi = np.array([r[B]["dhi"] - r[Bmax]["dhi"] for r in rows]) / hw
        se = np.array([r[B]["se"] for r in rows]) / hw
        print(f"   B = {B}: MC noise of the endpoint change / hw: RMS lo {np.sqrt(np.mean(e_lo**2)):.4f},"
              f" hi {np.sqrt(np.mean(e_hi**2)):.4f};  endpoint MC SE / hw (median) {np.median(se):.4f}")
    dpt = np.array([r["dpt"] for r in rows]) / hw
    dlo = np.array([r[Bmax]["dlo"] for r in rows]) / hw
    dhi = np.array([r[Bmax]["dhi"] for r in rows]) / hw
    sd_db = np.array([r[Bmax]["sd_db"] for r in rows]) / hw
    print(f"   |r_pt| median {np.median(np.abs(dpt)):.4f}; |r_lo - r_pt| median "
          f"{np.median(np.abs(dlo - dpt)):.4f}; |r_hi - r_pt| median {np.median(np.abs(dhi - dpt)):.4f};"
          f" SD_b(dT_b)/hw median {np.median(sd_db):.4f}")
    d1_three = np.maximum(np.abs(dpt), np.maximum(np.abs(dlo), np.abs(dhi)))
    print(f"   d1 (three) / |r_pt|: median {np.median(d1_three / np.maximum(np.abs(dpt), 1e-12)):.2f}")


if __name__ == "__main__":
    study("mean", 300, [500, 2000, 20000], 40, 5)
    study("median", 500, [500, 2000, 8000], 20, 6)
