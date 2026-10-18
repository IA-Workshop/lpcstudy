"""M3 verification (DEVELOPMENT): start (0.6, -0.3, 1.0), registry Chua, interval 0.1.
(1) DOP853 rtol=atol=1e-12 on the continuous ODE (independent of RK4 and of lpcstudy);
(2) NumPy RK4 (indep.py);
(3) evaluation only: the production map through the scratch old/new Benettin loops.
"""
import sys, dataclasses
import numpy as np
from scipy.integrate import solve_ivp
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from indep import field, rk4
p0 = np.array([0.6, -0.3, 1.0])
K = 120
sol = solve_ivp(lambda t, s: field("chua", s), (0, 0.1 * K), p0, method="DOP853",
                rtol=1e-12, atol=1e-12, t_eval=0.1 * np.arange(K + 1))
xd = np.abs(sol.y[0])
s = p0[None].copy(); xr = [abs(p0[0])]
for k in range(K):
    for _ in range(20):
        s = rk4("chua", s, 0.005)
    xr.append(abs(s[0, 0]))
xr = np.array(xr)
kd = int(np.argmax(xd > 3)); kr = int(np.argmax(xr > 3))
print(f"DOP853 first k with |x|>3: {kd}; |x_(k-1)|={xd[kd-1]:.6f} |x_k|={xd[kd]:.6f}; max|x| before: {xd[:kd].max():.6f}")
print(f"RK4    first k with |x|>3: {kr}; |x_(k-1)|={xr[kr-1]:.6f} |x_k|={xr[kr]:.6f}; max|x| before: {xr[:kr].max():.6f}")
print(f"max |RK4 - DOP853| over k<=K: {np.max(np.abs(xr - xd)):.2e}")
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[4]))
from lpcstudy.systems import SYSTEMS
from m2_bitwise import old, new
spec = dataclasses.replace(SYSTEMS["chua"], initial_state=(0.6, -0.3, 1.0))
lo = old(spec, 0.1, 100_000, 5_000)
lb, mb, fb = new(spec, 0.1, 100_000, 5_000, 3.0, True)
la, ma, fa = new(spec, 0.1, 100_000, 5_000, 3.0, False)
print(f"old estimate_lyapunov (verbatim) = {lo!r}  (finite positive: DEF-0015 reproduced)")
print(f"guarded, burn-in carried: lambda={lb!r} max={mb} first_fail={fb}")
print(f"guarded, final burn-in + averaging only: lambda={la!r} max={ma} first_fail={fa}")
lb2, mb2, fb2 = new(spec, 0.1, 1_000, 200, 3.0, True)
print(f"short run burn 200 / n 1000, burn-in carried: first_fail={fb2}, max={mb2}")
