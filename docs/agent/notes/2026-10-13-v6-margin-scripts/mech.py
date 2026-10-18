"""Mechanism of the V6 tail: independent NumPy RK4 refinement study + scipy reference at
the top-D states vs random states; stretching (FTLE over the 1-LT window) and, for Chua,
breakpoint-crossing speed. DEVELOPMENT; literal seeds. Usage: python -I mech.py <code_root> <cache> <system>
"""
import sys
from pathlib import Path
code_root, cache_dir, system = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
sys.path.insert(0, code_root)
import numpy as np, jax, math
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
from scipy.integrate import solve_ivp
from lpcstudy.config import PRESETS
from lpcstudy.data import lyapunov_record
from lpcstudy.systems import SYSTEMS, make_flow_step, simulate_trajectory
spec = SYSTEMS[system]; P = spec.params
lam, _ = lyapunov_record(spec, cache_dir / "lyapunov.json")
interval = 1.0 / (30 * lam)
coarse = make_flow_step(spec, P, interval)
burn = 3000
stats = simulate_trajectory(coarse, jnp.asarray(spec.initial_state), burn + 200_000)[burn:]
sigma = float(stats[:, 0].std())
# regenerate orbit 0 of perstate.py (same literal seed and order)
rng = np.random.default_rng(14_0006)
x0 = stats[rng.integers(0, len(stats))] + 1e-3 * rng.standard_normal(3)
orb = simulate_trajectory(coarse, jnp.asarray(x0), burn + 200_000)[burn:]
D = np.load(f"D_{system}.npz")["D"][0]
# independent field (NumPy)
def f(s):
    x, y, z = s[..., 0], s[..., 1], s[..., 2]
    if system == "lorenz63":
        return np.stack([P["sigma"] * (y - x), x * (P["rho"] - z) - y, x * y - P["beta"] * z], -1)
    if system == "rossler":
        return np.stack([-y - z, x + P["a"] * y, P["b"] + z * (x - P["c"])], -1)
    g = P["m1"] * x + 0.5 * (P["m0"] - P["m1"]) * (np.abs(x + 1) - np.abs(x - 1))
    return np.stack([P["alpha"] * (y - x - g), x - y + z, -P["beta"] * y], -1)
def rk4_obs(s0, n_sub):
    dt = interval / n_sub; s = s0.copy(); out = [s[..., 0].copy()]
    for _ in range(30):
        for _ in range(n_sub):
            k1 = f(s); k2 = f(s + .5 * dt * k1); k3 = f(s + .5 * dt * k2); k4 = f(s + dt * k3)
            s = s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        out.append(s[..., 0].copy())
    return np.stack(out, -1)
n_c = math.ceil(interval / spec.max_dt); n_f = math.ceil(interval / (spec.max_dt / 2))
# top episodes: local maxima of D separated by >= 30 steps
order = np.argsort(D)[::-1]; top = []
for i in order:
    if all(abs(i - j) > 30 for j in top): top.append(i)
    if len(top) == 12: break
rand = np.random.default_rng(5).integers(0, len(D), 12)
def ref(s0):
    ev = []
    if system == "chua":
        e1 = lambda t, s: s[0] - 1.0; e2 = lambda t, s: s[0] + 1.0
        ev = [e1, e2]
    ts = np.arange(31) * interval; xs = [s0[0]]; s = s0.copy(); t = 0.0; cross = []
    for j in range(1, 31):
        while True:
            sol = solve_ivp(lambda t, s: f(s), (t, ts[j]), s, method="DOP853", rtol=1e-13, atol=1e-14, events=ev or None)
            s = sol.y[:, -1]; t = sol.t[-1]
            if ev and any(len(te) for te in sol.t_events):
                # restart just past the event to keep each segment analytic
                vel = f(s)[0]; cross.append(abs(vel))
                if t >= ts[j] - 1e-15: break
                continue
            break
        xs.append(s[0])
    return np.array(xs), cross
def ftle(s0):
    J = np.asarray(jax.jacfwd(lambda s: jax.lax.fori_loop(0, 30, lambda _, x: coarse(x), s))(jnp.asarray(s0)))
    return np.log(np.linalg.svd(J, compute_uv=False)[0])  # per LT (window = 1 LT)
print(f"{system}: n_c {n_c}, n_f {n_f}, sigma {sigma:.4f}")
print("kind  idx      D(lib)    D(np)     e_h       e_h/2     e_h/4     e_h/8     p1    p2    p3   ln-stretch  min|xdot| at |x|=1")
for kind, idxs in (("top", top), ("rand", rand)):
    for i in idxs:
        s0 = orb[i].astype(float)
        xr, cross = ref(s0)
        lv = [rk4_obs(s0, n) for n in (n_c, 2 * n_c, 4 * n_c, 8 * n_c)]
        dnp = np.max(np.abs(rk4_obs(s0, n_c) - rk4_obs(s0, n_f))) / sigma
        e = [np.max(np.abs(x - xr)) / sigma for x in lv]
        p = [math.log2(e[k] / e[k + 1]) if e[k + 1] > 0 else float('nan') for k in range(3)]
        mc = f"{min(cross):.3f}" if cross else "-"
        print(f"{kind:5s} {i:7d} {D[i]:.2e} {dnp:.2e} " + " ".join(f"{v:.2e}" for v in e) + " " + " ".join(f"{v:5.2f}" for v in p) + f"  {ftle(s0):6.2f}   {mc}")
