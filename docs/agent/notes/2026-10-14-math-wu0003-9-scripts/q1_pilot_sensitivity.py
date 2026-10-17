"""Q1 step 2: conditioning and solver-stopping error of the H1a fit on pilot-shaped inputs.

DEVELOPMENT (DEV-0): not a hypothesis test. Reads the P0 and P1 DEV-0 pilot results.json read-only
(the 12 (system, rho) H1a blocks, 5 library sizes each) and perturbs their medians synthetically
(scratch seed 20261018). CPU, numpy and scipy only; the fit is the verbatim copy in q1_reproduce.

For each input y = log(median^2):
  theta_prod  = production curve_fit (trf, ftol = xtol = gtol = 1e-8, scipy defaults)
  theta_star  = the same problem solved to 1e-15 (the exact minimiser; unique when J has rank 3)
  e           = theta_prod - theta_star (solver stopping error)
  S = d theta_star / d y (central differences on tight fits), kappa_ulp = |S| . (delta) bound
Then the ulp experiment: y + log(1 + eps), |eps_i| <= GAMMA (uniform), refit with production
settings, |d(1/d)| / s and |d floor_rms| / floor_rms, where s = max(|lo|, |hi|) of the
reference ci_inverse_dim.
"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from q1_reproduce import fit_ls, model

GAMMA = 3.2e-14   # 2x the largest relative input change seen on the kernel pair (1.65e-14)
N_ULP = 200       # ulp perturbations per input
N_RES = 40        # resample-like inputs per pilot cell
SIG_RES = None    # set per cell from the reference CI width (see below)
rng = np.random.default_rng(20261018)


def tight(sizes, med):
    return fit_ls(sizes, med, tol=1e-15)


def study(sizes, med, s_scale, n_ulp=N_ULP):
    rp = fit_ls(sizes, med)
    rt = tight(sizes, med)
    log_n = np.log(sizes)
    y = np.log(med)
    J = np.empty((len(sizes), 3))
    for k in range(3):
        e = np.zeros(3); e[k] = 1e-6
        J[:, k] = (model(log_n, *(rt.x + e)) - model(log_n, *(rt.x - e))) / 2e-6
    sv = np.linalg.svd(J, compute_uv=False)
    # sensitivity of theta_star to y (central differences, step 1e-6 in y)
    S = np.empty((3, len(sizes)))
    for i in range(len(sizes)):
        d = np.zeros(len(sizes)); d[i] = 1e-6
        S[:, i] = (tight(sizes, med * np.exp(d)).x - tight(sizes, med * np.exp(-d)).x) / 2e-6
    e_stop = rp.x - rt.x
    d_inv, d_floor, flips = [], [], 0
    for _ in range(n_ulp):
        eps = rng.uniform(-GAMMA, GAMMA, len(sizes))
        rq = fit_ls(sizes, med * (1 + eps))
        flips += int(rq.nfev != rp.nfev or rq.status != rp.status)
        d_inv.append(abs(rq.x[1] - rp.x[1]) / 2 / s_scale)
        d_floor.append(abs(np.exp(rq.x[2] / 2) - np.exp(rp.x[2] / 2)) / np.exp(rp.x[2] / 2))
    return dict(status=rp.status, nfev=rp.nfev, sv_min=sv[-1], sv_max=sv[0],
                e_inv=abs(e_stop[1]) / 2 / s_scale,
                e_floor=abs(np.exp(rp.x[2] / 2) - np.exp(rt.x[2] / 2)) / np.exp(rt.x[2] / 2),
                lin_inv=np.abs(S[1]).sum() * GAMMA / 2 / s_scale,
                lin_floor=np.abs(S[2]).sum() * GAMMA / 2,
                ulp_inv=max(d_inv), ulp_floor=max(d_floor), flips=flips, x=rp.x)


if __name__ == "__main__":
    rows = []
    for path in sys.argv[1:]:
        A = json.load(open(path))
        for system, blk in A["systems"].items():
            for rho, b in blk.get("H1a", {}).get("by_noise", {}).items():
                sizes = np.array(sorted(int(k) for k in b["median_seed_by_n_lib"]), dtype=float)
                med = np.array([b["median_seed_by_n_lib"][str(int(n))] for n in sizes]) ** 2
                lo, hi = b["ci_inverse_dim"]
                s = max(abs(lo), abs(hi))
                r = study(sizes, med, s)
                tag = f"{Path(path).parts[-3]} {system:8s} {rho}"
                print(f"{tag}  leaf 1/d {b['fitted_inverse_dim']:.12f} repro {r['x'][1]/2:.12f} "
                      f"| status {r['status']} nfev {r['nfev']:2d} sv [{r['sv_min']:.3g}, {r['sv_max']:.3g}] "
                      f"| stop err 1/d {r['e_inv']:.2e} s, floor {r['e_floor']:.2e} "
                      f"| linear ulp 1/d {r['lin_inv']:.1e} s | ulp-exp max 1/d {r['ulp_inv']:.2e} s, "
                      f"floor {r['ulp_floor']:.2e}, path flips {r['flips']}/{N_ULP}")
                rows.append(("point", r))
                # resample-like inputs: each median jittered by an independent 5% log-SD (the pilot
                # 95% CI of 1/d spans about +-20%; 5% per median gives fits of that spread)
                for _ in range(N_RES):
                    medj = med * np.exp(rng.normal(0, 0.05, len(sizes)))
                    rj = study(sizes, medj, s, n_ulp=20)
                    rows.append(("resample", rj))
    for kind in ("point", "resample"):
        rr = [r for k, r in rows if k == kind]
        st = {}
        for r in rr:
            st[r["status"]] = st.get(r["status"], 0) + 1
        print(f"\n== {kind}: {len(rr)} fits; status counts {st}")
        for key in ("e_inv", "e_floor", "lin_inv", "lin_floor", "ulp_inv", "ulp_floor"):
            v = np.array([r[key] for r in rr])
            print(f"  {key:9s} median {np.median(v):.2e}  max {v.max():.2e}")
        print(f"  sv_min min {min(r['sv_min'] for r in rr):.3g}; path flips "
              f"{sum(r['flips'] for r in rr)} of {sum(N_ULP if kind == 'point' else 20 for _ in rr)}")
        print(f"  at a bound (2/d within 1e-6 of 0.01 or 10, or log f2 <= -59): "
              f"{sum(1 for r in rr if min(abs(r['x'][1]-0.01), abs(r['x'][1]-10)) <= 1e-6 or r['x'][2] <= -59)}")
