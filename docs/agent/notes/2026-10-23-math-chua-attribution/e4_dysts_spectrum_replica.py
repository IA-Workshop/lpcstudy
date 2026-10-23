"""E4: candidate (iii) for the spectrum field: a replica of Dysts' spectrum recipe.

Recipe as relayed (researcher note A.5, fetch extract of find_lyapunov_exponents
and find_attractor_properties.py; not the code itself): trajectory sampled at
500 points per period (Delta = period/500, period = 1.4235), 15 000 samples,
Jacobian at each sample, backward-Euler tangent u <- inv(I - J Delta) u, QR at
every sample, exponents = sum log|diag R| / (Delta * 15000); 20 starts; the
stored spectrum is the average weighted by exp(-1000 * min_i |lambda_i|).
What is not known (assumed here): how the 20 starts are drawn (here: states
of one long on-attractor orbit, 60 time units apart), whether a transient is
discarded before the 15 000 samples (here: none beyond being on the attractor),
and the integrator (here: RK4 at Delta/5 instead of Radau rtol 1e-12).
R = 20 independent replications of the 20-start recipe give the sampling
spread of the recipe. The same orbits are also run with the exact RK4 tangent
(no backward Euler) to separate the integrator effect from the short length.
Parameters: DYSTS.
"""
import json, numpy as np
from chua_np import *
p = DYSTS
period = 1.4235
delta = period / 500
n_samp = 15000
R, K = 20, 20
s = np.array([[0.7, 0.0, 0.0]])
s = flow(s, p, 500.0, 0.005)
starts = []
for i in range(R * K):
    s = flow(s, p, 60.0, 0.005)
    starts.append(s[0].copy())
starts = np.array(starts)
n = starts.shape[0]
sub = 5
h = delta / sub
# backward-Euler tangent along the sampled trajectory
x = starts.copy()
q_be = np.broadcast_to(np.eye(3), (n, 3, 3)).copy()
q_rk = q_be.copy()
lsum_be = np.zeros((n, 3)); lsum_rk = np.zeros((n, 3))
eye = np.eye(3)
for k in range(n_samp):
    J = jac(x, p)
    u = np.linalg.solve(eye[None] - J * delta, q_be)
    q, r = np.linalg.qr(u)
    d = np.diagonal(r, axis1=1, axis2=2)
    q_be = q * np.sign(d)[:, None, :]
    lsum_be += np.log(np.abs(d))
    v = q_rk
    for _ in range(sub):
        x, v = rk4_tangent(x, v, p, h)
    q, r = np.linalg.qr(v)
    d = np.diagonal(r, axis1=1, axis2=2)
    q_rk = q * np.sign(d)[:, None, :]
    lsum_rk += np.log(np.abs(d))
T = delta * n_samp
lam_be = lsum_be / T
lam_rk = lsum_rk / T
out = {"T_per_run": T, "delta": delta}
for tag, lam in [("backward_euler", lam_be), ("rk4_tangent", lam_rk)]:
    w = np.exp(-1000 * np.min(np.abs(lam), axis=1))
    per_rep = []
    for rep in range(R):
        sl = slice(rep * K, (rep + 1) * K)
        ww = w[sl]
        if ww.sum() > 0:
            per_rep.append((lam[sl] * ww[:, None]).sum(axis=0) / ww.sum())
        else:
            per_rep.append(np.full(3, np.nan))
    per_rep = np.array(per_rep)
    unw = lam[:, 0]
    out[tag] = {
        "single_run_lam1_mean": float(unw.mean()), "single_run_lam1_sd": float(unw.std(ddof=1)),
        "single_run_lam_mean": lam.mean(axis=0).tolist(),
        "weighted_rep_lam1": per_rep[:, 0].tolist(),
        "weighted_rep_lam1_mean": float(np.nanmean(per_rep[:, 0])),
        "weighted_rep_lam1_sd": float(np.nanstd(per_rep[:, 0], ddof=1)),
        "weighted_rep_spectrum_mean": np.nanmean(per_rep, axis=0).tolist(),
        "n_nan_reps": int(np.isnan(per_rep[:, 0]).sum()),
        "max_weight_share_median": float(np.median([w[r*K:(r+1)*K].max() / w[r*K:(r+1)*K].sum() for r in range(R) if w[r*K:(r+1)*K].sum() > 0])),
    }
    o = out[tag]
    print(tag, f"T={T:.2f}; single-run lam1 mean {o['single_run_lam1_mean']:.4f} sd {o['single_run_lam1_sd']:.4f};",
          f"spectrum mean {np.round(o['single_run_lam_mean'], 4)}")
    print("   weighted 20-start recipe over", R, "reps: lam1 mean", round(o["weighted_rep_lam1_mean"], 4),
          "sd", round(o["weighted_rep_lam1_sd"], 4), "min", round(np.nanmin(per_rep[:, 0]), 4), "max", round(np.nanmax(per_rep[:, 0]), 4),
          "; spectrum", np.round(o["weighted_rep_spectrum_mean"], 4), "; median top-weight share", round(o["max_weight_share_median"], 3), flush=True)
json.dump(out, open("e4_dysts_spectrum_replica.json", "w"), indent=1)
