"""Q1 step 4: check the a-priori form of the stopping error, |e| <~ sqrt(ftol) ||r|| / sigma_min(J),
and the FD-Jacobian fixed-point shift, |d theta| ~ ||dJ|| ||r|| / sigma_min^2 with
||dJ|| ~ sqrt(m) u max|y| / h, h = sqrt(u) max(1, |x|) (scipy 2-point), on the 12 P0/P1 H1a cells.
DEVELOPMENT (DEV-0): read-only; prints, per cell, the observed |e| and the two predicted scales,
all as a fraction of s = max(|lo|, |hi|) of the reference ci_inverse_dim (for the 1/d component)."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from q1_reproduce import model, fit_ls

U = np.finfo(float).eps / 2
rows = []
for path in sys.argv[1:]:
    for system, blk in json.load(open(path))["systems"].items():
        for rho, b in blk["H1a"]["by_noise"].items():
            sizes = np.array(sorted(int(k) for k in b["median_seed_by_n_lib"]), dtype=float)
            med = np.array([b["median_seed_by_n_lib"][str(int(n))] for n in sizes]) ** 2
            s = max(map(abs, b["ci_inverse_dim"]))
            rp, rt = fit_ls(sizes, med), fit_ls(sizes, med, tol=1e-15)
            log_n, y = np.log(sizes), np.log(med)
            r = model(log_n, *rt.x) - y
            a = np.exp(rt.x[0] - rt.x[1] * log_n); f = np.exp(rt.x[2]); den = a + f
            J = np.column_stack([a / den, -log_n * a / den, f / den])
            sv = np.linalg.svd(J, compute_uv=False)
            Jinv = np.linalg.pinv(J)                     # row 1 = sensitivity of 2/d
            e_obs = abs(rp.x[1] - rt.x[1]) / 2 / s
            e_pred = np.sqrt(1e-8) * np.linalg.norm(r) * np.linalg.norm(Jinv[1]) / 2 / s
            h = np.sqrt(np.finfo(float).eps) * np.maximum(1, np.abs(rt.x))
            dJ = np.sqrt(len(sizes)) * 2 * U * np.abs(y).max() / h.min()
            fd_pred = dJ * np.linalg.norm(r) * np.linalg.norm(Jinv[1]) / sv[-1] / 2 / s
            rows.append((e_obs, e_pred, fd_pred))
            print(f"{Path(path).parts[-3]} {system:8s} {rho}: ||r|| {np.linalg.norm(r):.3g} "
                  f"sigma_min {sv[-1]:.3g} | stop err obs {e_obs:.2e} s, sqrt(ftol) scale {e_pred:.2e} s "
                  f"(ratio {e_obs / e_pred:.2f}) | FD fixed-point scale {fd_pred:.2e} s")
rows = np.array(rows)
print(f"max obs/pred (stop) {np.max(rows[:, 0] / rows[:, 1]):.2f}; max sqrt(ftol) scale {rows[:, 1].max():.2e} s; "
      f"max FD scale {rows[:, 2].max():.2e} s")
