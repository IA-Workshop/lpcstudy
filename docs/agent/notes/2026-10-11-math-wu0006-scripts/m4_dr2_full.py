"""M4: null Delta R^2 (production qn_profile_block, B = 2000) and the conditional estimand.

x1..x3, xi independent AR(1); x4 = 0.6 x1 + 0.8 xi. L = x1 - 0.5 x2^2 + 0.5 x2 x3 + e (e AR(1), sd 1);
w* = 0 if L < q15 (15% exact zeros) else expit(L); log_t = 0.5 x1 + 0.3 x3 + 0.5 e' . Train 900 (two
independent paths 600 + 300), test 1000. Truth: fitted pair on 1e5 fresh i.i.d. stationary states.
"""
import os, sys, time
for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[v] = "1"
os.environ["JAX_PLATFORMS"] = "cpu"
import numpy as np
from multiprocessing import get_context
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[4]))  # repo root
from simcore import ar1

Q15 = None


def gen(rng, n, phi, iid=False):
    cols = [rng.standard_normal(n) if iid else ar1(rng, n, phi) for _ in range(6)]
    x1, x2, x3, xi, e, e2 = cols
    x = np.column_stack([x1, x2, x3, 0.6 * x1 + 0.8 * xi])
    lat = x1 - 0.5 * x2**2 + 0.5 * x2 * x3 + e
    w = np.where(lat < Q15, 0.0, 1 / (1 + np.exp(-lat)))
    return x, w, 0.5 * x1 + 0.3 * x3 + 0.5 * e2


def r2(y, p):
    return 1 - np.sum((y - p) ** 2) / np.sum((y - y.mean()) ** 2)


def work(args):
    global Q15
    from lpcstudy.analysis import qn_profile_block, qn_regressor
    phi, seed, reps = args
    rng = np.random.default_rng(seed)
    z = np.random.default_rng(99).standard_normal((4, 2_000_000))
    Q15 = np.quantile(z[0] - 0.5 * z[1]**2 + 0.5 * z[1] * z[2] + z[3], 0.15)
    out = []
    for _ in range(reps):
        xa, wa, ta = gen(rng, 2000, phi); xb, wb, tb = gen(rng, 1000, phi)
        xtr, wtr, ttr = np.concatenate([xa, xb]), np.concatenate([wa, wb]), np.concatenate([ta, tb])
        xte, wte, tte = gen(rng, 1000, phi)
        seed_m = int(rng.integers(2**31)); boot = int(rng.integers(2**31))
        res = qn_profile_block(xtr, xte, wtr, wte, ttr, tte, seed=seed_m, n_resamples=2000,
                               block=5, boot_seed=boot)
        xf, wf, _ = gen(rng, 100_000, phi, iid=True)
        row = []
        for name in ("logit_w_interior", "w_zero_indicator"):
            if name == "logit_w_interior":
                rtr, rte, rf = (wtr > 0) & (wtr < 1), (wte > 0) & (wte < 1), (wf > 0) & (wf < 1)
                ytr = np.log(wtr[rtr] / (1 - wtr[rtr])); yte = np.log(wte[rte] / (1 - wte[rte]))
                yf = np.log(wf[rf] / (1 - wf[rf]))
            else:
                rtr, rte, rf = (np.ones(len(wtr), bool), np.ones(len(wte), bool), np.ones(len(wf), bool))
                ytr, yte, yf = (wtr == 0).astype(float), (wte == 0).astype(float), (wf == 0).astype(float)
            m3 = qn_regressor(seed_m).fit(xtr[rtr][:, :3], ytr)
            m4 = qn_regressor(seed_m).fit(xtr[rtr], ytr)
            p3, p4 = m3.predict(xte[:, :3]), m4.predict(xte)
            refit = r2(yte, p4[rte]) - r2(yte, p3[rte])
            f3, f4 = m3.predict(xf[rf][:, :3]), m4.predict(xf[rf])
            d = (yf - f3) ** 2 - (yf - f4) ** 2
            sst = np.sum((yf - yf.mean()) ** 2)
            truth = d.sum() / sst
            truth_se = d.std() * np.sqrt(len(d)) / sst
            ent = res[name]
            row += [ent["delta_r2"], *ent["ci"], truth, truth_se, float(refit == ent["delta_r2"]),
                    ent["n_failed_resamples"], ent["r2_three"]]
        out.append(row)
    return out


if __name__ == "__main__":
    phi, R = float(sys.argv[1]), int(sys.argv[2])
    t0 = time.time()
    ss = np.random.SeedSequence([20261011, 4, int(phi * 1000)])
    chunks = 20
    seeds = [int(c.generate_state(1)[0]) for c in ss.spawn(chunks)]
    per = [R // chunks + (i < R % chunks) for i in range(chunks)]
    with get_context("spawn").Pool(4) as pool:
        res = pool.map(work, [(phi, s, r) for s, r in zip(seeds, per)])
    a = np.array([row for part in res for row in part])
    np.save(f"dr2full_{phi:g}.npy", a)
    for j, name in enumerate(("logit_w_interior", "w_zero_indicator")):
        est, lo, hi, tr, trse, same, nf, r3 = a[:, 8 * j: 8 * j + 8].T
        hw = (hi - lo) / 2
        print(f"{name} phi={phi:g} R={R} t={time.time()-t0:.0f}s: mean est={est.mean():.4f} "
              f"mean truth={tr.mean():.4f} sd truth={tr.std():.4f} mean halfwidth={hw.mean():.4f} "
              f"truthSE/hw={np.mean(trse/hw):.3f} | N1 P(contains 0)={np.mean((lo<=0)&(0<=hi)):.3f} "
              f"N2 P(lo>0)={np.mean(lo>0):.3f} N3 cov(cond)={np.mean((lo<=tr)&(tr<=hi)):.3f} "
              f"(truth<lo {np.mean(tr<lo):.3f}, truth>hi {np.mean(tr>hi):.3f}) P(truth>0)={np.mean(tr>0):.3f} "
              f"refit bitwise={same.mean():.3f} failed={nf.sum():.0f} R2_three={r3.mean():.3f}", flush=True)
