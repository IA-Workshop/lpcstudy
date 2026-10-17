"""Independent check of the largest per-state V6 deviation at one (preset, DEV id, system).

Rebuilds the production context (registry seed, as v6_dev.py), takes the test state with the
largest D, and recomputes D with an independent NumPy RK4 (field written out here, not the
library's), the true coarse error e_h against SciPy DOP853 (rtol 1e-13, restarted at the diode
breakpoints |x| = 1 for Chua), a refinement study n_c, 2n_c, 4n_c, 8n_c with observed orders,
the number of breakpoint crossings in the window, and the 1-LT stretching ln sigma_1.
No randomness. DEVELOPMENT. Usage: python -I verify_state.py <code_root> <cache> <preset> <DEV-n> <system>
"""
import math
import sys
from pathlib import Path

code_root, cache_dir, preset, seed_id, system = sys.argv[1], Path(sys.argv[2]), *sys.argv[3:6]
sys.path.insert(0, code_root)
import numpy as np  # noqa: E402
import jax  # noqa: E402

jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp  # noqa: E402
from scipy.integrate import solve_ivp  # noqa: E402
from lpcstudy.config import PRESETS  # noqa: E402
from lpcstudy.data import build_context  # noqa: E402
from lpcstudy.seeds import REGISTRY_PATH, load_registry, resolve_dev_seed, with_seed  # noqa: E402
from lpcstudy.systems import make_flow_step  # noqa: E402
from lpcstudy.validation import check_integrator  # noqa: E402

assert seed_id.startswith("DEV-")
cfg = with_seed(PRESETS[preset], seed_id, resolve_dev_seed(seed_id, load_registry(REGISTRY_PATH)))
ctx = build_context(system, cfg, cache_dir)
v6 = check_integrator(ctx)["integrator_max_dev_sigma"]
spec, P, interval, sigma = ctx.spec, ctx.spec.params, ctx.interval, ctx.obs_scale
n_c = math.ceil(interval / spec.max_dt)
n_f = math.ceil(interval / (spec.max_dt / 2))


def f(s):
    x, y, z = s[..., 0], s[..., 1], s[..., 2]
    if system == "lorenz63":
        return np.stack([P["sigma"] * (y - x), x * (P["rho"] - z) - y, x * y - P["beta"] * z], -1)
    if system == "rossler":
        return np.stack([-y - z, x + P["a"] * y, P["b"] + z * (x - P["c"])], -1)
    g = P["m1"] * x + 0.5 * (P["m0"] - P["m1"]) * (np.abs(x + 1) - np.abs(x - 1))
    return np.stack([P["alpha"] * (y - x - g), x - y + z, -P["beta"] * y], -1)


def rk4_obs(s0, n_sub):
    dt = interval / n_sub
    s = s0.copy()
    out = [s[0]]
    for _ in range(30):
        for _ in range(n_sub):
            k1 = f(s); k2 = f(s + .5 * dt * k1); k3 = f(s + .5 * dt * k2); k4 = f(s + dt * k3)
            s = s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        out.append(s[0])
    return np.array(out)


def reference(s0):
    events = []
    if system == "chua":
        e1 = lambda t, s: s[0] - 1.0  # noqa: E731
        e2 = lambda t, s: s[0] + 1.0  # noqa: E731
        events = [e1, e2]
    ts = np.arange(31) * interval
    xs, s, t, crossings = [s0[0]], s0.copy(), 0.0, 0
    for j in range(1, 31):
        while True:
            sol = solve_ivp(lambda t, s: f(s), (t, ts[j]), s, method="DOP853", rtol=1e-13,
                            atol=1e-14, events=events or None)
            s, t = sol.y[:, -1], sol.t[-1]
            if events and any(len(te) for te in sol.t_events):
                crossings += 1
                if t >= ts[j] - 1e-15:
                    break
                continue
            break
        xs.append(s[0])
    return np.array(xs), crossings


coarse = make_flow_step(spec, P, interval)
idx = ctx.split_indices["test"][:20]
ds = []
for t in idx:
    s0 = np.asarray(ctx.eval_states[t], dtype=float)
    ds.append(np.max(np.abs(rk4_obs(s0, n_c) - rk4_obs(s0, n_f))) / sigma)
ds = np.array(ds)
k = int(ds.argmax())
s0 = np.asarray(ctx.eval_states[idx[k]], dtype=float)
xr, crossings = reference(s0)
e = [np.max(np.abs(rk4_obs(s0, m * n_c) - xr)) / sigma for m in (1, 2, 4, 8)]
p = [math.log2(e[i] / e[i + 1]) for i in range(3)]
J = np.asarray(jax.jacfwd(lambda s: jax.lax.fori_loop(0, 30, lambda _, x: coarse(x), s))(
    jnp.asarray(s0)))
stretch = float(np.log(np.linalg.svd(J, compute_uv=False)[0]))
print(f"{preset}|{seed_id}|{system}: library V6 {v6:.6e}; NumPy RK4 max-over-20 D {ds.max():.6e} "
      f"(rel diff {abs(ds.max() - v6) / v6:.1e}); state k={k} (test index {idx[k]})")
print(f"  n_c {n_c}, n_f {n_f}; e_h at n_c,2n_c,4n_c,8n_c vs DOP853: "
      + " ".join(f"{v:.3e}" for v in e) + "; observed orders " + " ".join(f"{v:.2f}" for v in p))
print(f"  D / e_h = {ds.max() / e[0]:.3f}; breakpoint crossings in window: {crossings}; "
      f"ln sigma_1 (1 LT) = {stretch:.2f}; second-largest D {np.sort(ds)[-2]:.3e}")
