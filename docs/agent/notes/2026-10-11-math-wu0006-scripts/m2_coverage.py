"""M2: Monte Carlo of the WU-0006 coverage cases with the production MBB semantics (B = 2000).

Each replication: data from the case's generator, B = 2000 moving-block resamples (blocks of 5,
uniform starts in 0..n-5), statistic per resample (exact fast forms, checked against production
to 4e-16), np.quantile percentile bounds at 0.95 and 1 - 0.05/3. Output: per-replication bounds.
"""
import os, sys, json, time
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
import numpy as np
from multiprocessing import get_context
from simcore import ar1, starts, idx_from, block_sums, mult, spearman_w, partial_w, quad

B = 2000
LEVELS = (0.95, 1 - 0.05 / 3)
C6_C = 2 * np.sin(0.7 * np.pi / 6)
TRUTH = {"C1": 0.0, "C2": 0.0, "C3": 0.0, "C4": 1.05, "C5": 0.10, "C6": 0.7, "C7": 0.1,
         "C8": 0.0, "C9": 0.0}
N = {"C8": 300, "C9": 300}


def one(case, phi, rng, sigma=1.0, c=0.8):
    n = N.get(case, 500)
    st = starts(rng, B, n)
    if case in ("C1", "C8"):
        x = ar1(rng, n, phi)
        vals = block_sums(x)[st].sum(1) / n
    elif case in ("C3", "C9"):
        x = ar1(rng, n, phi)
        vals = np.median(x[idx_from(st, n)], axis=1)
    elif case in ("C2", "C4", "C5"):
        uv = ar1(rng, n, phi, 2, c)
        mu = {"C2": 0.0, "C4": np.log(1.05), "C5": np.log(1.10)}[case]
        a, b = np.exp(mu + sigma * uv[:, 0]), np.exp(sigma * uv[:, 1])
        if case == "C2":
            vals = block_sums(a - b)[st].sum(1) / n
        else:
            vals = block_sums(a)[st].sum(1) / block_sums(b)[st].sum(1)
            if case == "C5":
                vals = vals - 1.0
    elif case == "C6":
        x = ar1(rng, n, phi, 2, C6_C)
        vals = spearman_w(mult(idx_from(st, n), n), x[:, 0], x[:, 1])
    elif case == "C7":
        s = ar1(rng, n, phi, 2, 0.0); e = ar1(rng, n, phi, 2, 0.1)
        t = 0.5 * s[:, 0] - 0.3 * s[:, 1] ** 2 + e[:, 0]
        v = 0.4 * s[:, 1] + 0.2 * s[:, 0] * s[:, 1] + e[:, 1]
        vals = partial_w(mult(idx_from(st, n), n), t, v, quad(s))
    out = []
    for lev in LEVELS:
        a = (1 - lev) / 2
        out += [np.quantile(vals, a), np.quantile(vals, 1 - a)]
    return out


def work(args):
    case, phi, seed, reps, kw = args
    rng = np.random.default_rng(seed)
    return [one(case, phi, rng, **kw) for _ in range(reps)]


def run(case, phi, R, seed, kw=None, workers=4, chunks=40):
    kw = kw or {}
    ss = np.random.SeedSequence([seed, int(case[1:]), int(round(phi * 1000)),
                                 int(round(kw.get("sigma", 1.0) * 100)), int(round(kw.get("c", 0.8) * 100))])
    seeds = [int(c.generate_state(1)[0]) for c in ss.spawn(chunks)]
    per = [R // chunks + (i < R % chunks) for i in range(chunks)]
    with get_context("spawn").Pool(workers) as pool:
        res = pool.map(work, [(case, phi, s, r, kw) for s, r in zip(seeds, per)])
    return np.array([row for part in res for row in part])


if __name__ == "__main__":
    case, phi, R = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
    tag = sys.argv[4] if len(sys.argv) > 4 else ""
    kw = json.loads(sys.argv[5]) if len(sys.argv) > 5 else {}
    t0 = time.time()
    arr = run(case, phi, R, 20261011, kw)
    np.save(f"cov_{case}_{phi:g}{tag}.npy", arr)
    tr = TRUTH[case]
    s = [f"{case}{tag} phi={phi:g} R={R} t={time.time()-t0:.0f}s"]
    for j, lev in enumerate(LEVELS):
        lo, hi = arr[:, 2 * j], arr[:, 2 * j + 1]
        cov = np.mean((lo <= tr) & (tr <= hi)); below = np.mean(tr < lo); above = np.mean(tr > hi)
        s.append(f"L{lev:.4f}: cov={cov:.4f}(se {np.sqrt(cov*(1-cov)/R):.4f}) "
                 f"truth<lo={below:.4f} truth>hi={above:.4f}")
    print(" | ".join(s), flush=True)
