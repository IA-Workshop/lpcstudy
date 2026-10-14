"""Accuracy of the mech.py reference for Chua at the 12 top-D states: DOP853 (rtol 1e-13) vs
DOP853 (rtol 1e-10) and vs RK4 at 128 n_c substeps. DEVELOPMENT. Usage: python -I refcheck.py <code_root> <cache>"""
import sys, runpy
sys.argv = [sys.argv[0], sys.argv[1], sys.argv[2], "chua"]
import io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    import os; g = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mech.py"), run_name="refcheck")
import numpy as np
from scipy.integrate import solve_ivp
f, orb, top, sigma, rk4_obs, ref, n_c, interval = (g[k] for k in ("f", "orb", "top", "sigma", "rk4_obs", "ref", "n_c", "interval"))
worst = [0.0, 0.0]
for i in top:
    s0 = orb[i].astype(float); xr, _ = ref(s0)
    ts = np.arange(31) * interval
    lo = solve_ivp(lambda t, s: f(s), (0, ts[-1]), s0, method="DOP853", rtol=1e-10, atol=1e-12, t_eval=ts).y[0]
    fine = rk4_obs(s0, 128 * n_c)
    worst[0] = max(worst[0], np.max(np.abs(lo - xr)) / sigma); worst[1] = max(worst[1], np.max(np.abs(fine - xr)) / sigma)
print(f"max |DOP853(1e-10) - ref| = {worst[0]:.1e} sigma;  max |RK4(128 n_c) - ref| = {worst[1]:.1e} sigma (smallest e reported at top states: 1.5e-5)")
