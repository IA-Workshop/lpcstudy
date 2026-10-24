"""E1: reference reproduction and parameter candidate (i).

Code's settings (data.lyapunov_record): RK4 h = 0.005, re-orthonormalisation
interval 0.1 (20 * max_dt), burn-in 5000 intervals, 100 000 intervals,
start (0.7, 0, 0). Plus the 8 grid starts with x < 0 (ic_half; the mirror halves give identical
exponents by the odd symmetry of the field).
Parameter sets: OURS, DYSTS (JSON digits), EXACT (-8/7, -5/7).
SE: batch means, 20 batches of 5000 intervals (500 time units each).
"""
import json, time, numpy as np
from chua_np import *
starts = np.vstack([[0.7, 0.0, 0.0], ic_half()])
out = {}
for name, p in [("ours", OURS), ("dysts", DYSTS), ("exact", EXACT)]:
    t = time.time()
    r = benettin_qr(starts, p)
    ok = ~r["diverged"]
    lam1 = r["lam"][:, 0]
    ens = lam1[ok]
    out[name] = {
        "lam_start07": r["lam"][0].tolist(),
        "batch_se_start07": float(r["batch_se"][0]),
        "lam1_all": lam1.tolist(),
        "batch_se_all": r["batch_se"].tolist(),
        "diverged": r["diverged"].tolist(),
        "ens_mean": float(ens.mean()),
        "ens_se": float(ens.std(ddof=1) / np.sqrt(ens.size)),
        "n_ok": int(ok.sum()),
        "spectrum_mean": r["lam"][ok].mean(axis=0).tolist(),
        "sum_spectrum_mean": float(r["lam"][ok].sum(axis=1).mean()),
        "mean_div": float(r["mean_div"][ok].mean()),
        "pos_frac": r["pos_frac"].tolist(),
        "switches": r["switches"].tolist(),
        "maxabs": r["maxabs"].tolist(), "maxabs_x": r["maxabs_x"].tolist(),
        "seconds": time.time() - t,
    }
    o = out[name]
    print(name, "start(0.7,0,0): lam", np.round(o["lam_start07"], 5), "batch SE", round(o["batch_se_start07"], 5))
    print("   ensemble of", o["n_ok"], "ok /", len(lam1), ": mean", round(o["ens_mean"], 5), "SE", round(o["ens_se"], 5),
          "min", round(ens.min(), 5), "max", round(ens.max(), 5))
    print("   spectrum mean", np.round(o["spectrum_mean"], 5), "sum", round(o["sum_spectrum_mean"], 5), "mean div", round(o["mean_div"], 5))
    print("   over ok: pos_frac range", round(min(np.array(o["pos_frac"])[ok]), 3), round(max(np.array(o["pos_frac"])[ok]), 3), "switches min", min(np.array(o["switches"])[ok]), "max|x| over ok", round(max(np.array(o["maxabs_x"])[ok]), 4))
    print("   diverged:", sum(o["diverged"]), " seconds", round(o["seconds"], 1), flush=True)
json.dump(out, open("e1_reference.json", "w"), indent=1)
