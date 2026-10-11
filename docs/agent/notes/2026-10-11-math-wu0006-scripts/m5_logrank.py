"""M5: size of H3a (production h3a_logrank) under serially dependent labels and durations."""
import os, sys, time
for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[v] = "1"
os.environ["JAX_PLATFORMS"] = "cpu"
import numpy as np
from multiprocessing import get_context
from scipy.stats import norm, chi2
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[4]))  # repo root
from simcore import ar1

H, HMAX, N3 = 0.0125, 240, 200


def draw(rng, phi, partial):
    n = 3 * N3
    lab_latent = ar1(rng, n, phi)
    labels = np.empty(n, int); labels[np.argsort(lab_latent, kind="stable")] = np.repeat([0, 1, 2], N3)
    u = norm.cdf(ar1(rng, n, phi))
    haz = np.where((labels == 2) & partial, 2 * H, H)
    T = np.maximum(np.ceil(np.log(u) / np.log1p(-haz)), 1).astype(int)
    return labels, np.minimum(T, HMAX), T <= HMAX


def work(args):
    from lpcstudy.analysis import h3a_logrank
    from lpcstudy.statistics import kaplan_meier
    phi, partial, seed, reps = args
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(reps):
        cl, cd, ce = draw(rng, phi, partial)  # calibration draw for horizons_km
        hk = np.array([kaplan_meier(cd[cl == k], ce[cl == k], HMAX).median() for k in range(3)])
        lab, dur, ev = draw(rng, phi, partial)
        r = h3a_logrank(lab, dur, ev, hk, dur.astype(float), 30, 3)
        raw = r["logrank_p_raw"]
        out.append([min(r["logrank_p_holm"]) < 0.01, r["verdict"] == "pass",
                    *(np.nan if p is None else p for p in raw), ce.mean(),
                    int(any(p is None for p in raw)), *r["pairs"][0], *r["pairs"][1]])
    return out


if __name__ == "__main__":
    phi, partial, R = float(sys.argv[1]), sys.argv[2] == "L2", int(sys.argv[3])
    t0 = time.time()
    ss = np.random.SeedSequence([20261011, int(partial), int(phi * 1000)])
    seeds = [int(c.generate_state(1)[0]) for c in ss.spawn(40)]
    per = [R // 40 + (i < R % 40) for i in range(40)]
    with get_context("spawn").Pool(4) as pool:
        res = pool.map(work, [(phi, partial, s, r) for s, r in zip(seeds, per)])
    a = np.array([row for part in res for row in part], dtype=float)
    np.save(f"lr_{sys.argv[2]}_{phi:g}.npy", a)
    fwer, pas = a[:, 0].mean(), a[:, 1].mean()
    p1, p2 = a[:, 2], a[:, 3]
    # null pair(s): L1 both; L2 the pair without regime 2
    if partial:
        # row columns: 6,7 = first pair, 8,9 = second pair
        null_p = np.where((a[:, 6] != 2) & (a[:, 7] != 2), p1, p2)
        stat = chi2.isf(null_p, 1)
    else:
        stat = chi2.isf(np.concatenate([p1, p2]), 1)
    print(f"{sys.argv[2]} phi={phi:g} R={R} t={time.time()-t0:.0f}s FWER={fwer:.4f}(se {np.sqrt(fwer*(1-fwer)/R):.4f}) "
          f"P(pass)={pas:.4f} mean chi2 of null pair(s)={stat.mean():.4f}(se {stat.std()/np.sqrt(len(stat)):.4f}) "
          f"P(null p<0.01)={np.mean(stat > chi2.isf(0.01, 1)):.4f} P(null p<0.005)={np.mean(stat > chi2.isf(0.005, 1)):.4f} "
          f"censored={1-a[:, 4].mean():.4f} not_computed={a[:, 5].sum():.0f}", flush=True)
