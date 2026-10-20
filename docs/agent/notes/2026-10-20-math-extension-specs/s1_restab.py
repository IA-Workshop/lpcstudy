"""S1 re-specification (review R1): the |x| tail at a STABLE step and the RK4
frozen-coefficient stability at the excursion states (DEVELOPMENT, one thread).

(a) 64 starts on the attractor (points of a long orbit, perturbed by 1e-6
    whitened-ish), each run 700 000 steps at Delta with max_dt 0.005
    (h = Delta/60 = 0.00494, |h x| < 2.785 up to |x| = 564): per-orbit max |x|,
    the state at the orbit's minimum x, non-finite flags, and counts of steps
    with |x| > 200 and > 300.
(b) At every recorded minimum-x state: eigenvalues of the Jacobian J and the
    spectral radius of the RK4 amplification matrix R(hJ) = sum (hJ)^k/k!,
    k = 0..4, for the old step (0.009875), the new step and max_dt 0.004.
(c) Along a 200 000-step typical orbit, sampled every 5 steps: the largest
    |Re eig(J)|, |eig(J)| and max_i |R(h lambda_i)| at the new step."""

import math

import jax
import jax.numpy as jnp
import numpy as np

from lpcstudy.systems import lyapunov_guarded, make_flow_step, simulate_trajectory

from ext_common import CANDIDATES

sp = CANDIDATES["S1"]()
lam, _ = lyapunov_guarded(sp, 20 * sp.max_dt, 100_000, 5_000)
interval = 1.0 / (30 * lam)
substeps = math.ceil(interval / sp.max_dt)
h_new = interval / substeps
step = make_flow_step(sp, sp.params, interval)
print(f"S1 at max_dt {sp.max_dt}: lambda(1e5) {lam:.5f}, Delta {interval:.6f}, substeps {substeps}, h {h_new:.6f}; RK4 real-axis limit |h x| < 2.785 -> |x| < {2.785/h_new:.0f}")

orbit = simulate_trajectory(step, jnp.asarray(sp.initial_state), 3000 + 320_000)[3000:]
starts = orbit[::5000][:64] + 1e-6 * np.random.default_rng(20261020).standard_normal((64, 4))
n_steps = 700_000
bstep = jax.vmap(step)


def body(c, _):
    s, k, first, xmax, xmin_state, n200, n300 = c
    n = bstep(s)
    ok = jnp.all(jnp.isfinite(n), axis=1)
    first = jnp.where((first < 0) & ~ok, k, first)
    alive = first < 0
    ax = jnp.abs(n[:, 0])
    xmax = jnp.where(alive, jnp.maximum(xmax, ax), xmax)
    better = alive & (n[:, 0] < xmin_state[:, 0])
    xmin_state = jnp.where(better[:, None], n, xmin_state)
    n200 = n200 + (alive & (ax > 200))
    n300 = n300 + (alive & (ax > 300))
    return (n, k + 1, first, xmax, xmin_state, n200, n300), None


s0 = jnp.asarray(starts)
c0 = (s0, 1, -jnp.ones(64, int), jnp.abs(s0[:, 0]), s0, jnp.zeros(64, int), jnp.zeros(64, int))
(_, _, first, xmax, xmin_state, n200, n300), _ = jax.jit(lambda c: jax.lax.scan(body, c, None, length=n_steps))(c0)
first, xmax, xmin_state, n200, n300 = map(np.asarray, (first, xmax, xmin_state, n200, n300))
print(f"(a) 64 orbits x {n_steps} steps = {64*n_steps*interval/1e6:.2f}e6 time units: non-finite {int((first>=0).sum())}; per-orbit max|x| sorted (top 12): "
      f"{np.round(np.sort(xmax)[::-1][:12], 2).tolist()}; orbits with max > 200: {int((xmax>200).sum())}, > 300: {int((xmax>300).sum())}, > 304: {int((xmax>304).sum())}; "
      f"steps with |x| > 200: {int(n200.sum())}, > 300: {int(n300.sum())}; quantiles of per-orbit max 50/90% {np.round(np.quantile(xmax, [.5,.9]), 1).tolist()}")


def jac(s):
    x, y, z, w = s
    a, b, c, d = sp.params["a"], sp.params["b"], sp.params["c"], sp.params["d"]
    return np.array([[0, -1, -1, 0], [1, a, 0, 1], [z, 0, x, 0], [0, 0, -c, d]], float)


def rk4_radius(J, h):
    hJ = h * J
    R = np.eye(4) + hJ + hJ @ hJ / 2 + hJ @ hJ @ hJ / 6 + hJ @ hJ @ hJ @ hJ / 24
    return np.max(np.abs(np.linalg.eigvals(R)))


print("(b) at the recorded minimum-x states (orbits sorted by min x):")
order = np.argsort(xmin_state[:, 0])
for i in order[:8]:
    s = xmin_state[i]
    ev = np.linalg.eigvals(jac(s))
    print(f"   state (x,y,z,w) = {np.round(s, 2).tolist()}: eig(J) real parts {np.round(ev.real, 2).tolist()}, |imag| max {np.abs(ev.imag).max():.2f}; "
          f"rho(R(hJ)) at h 0.009875: {rk4_radius(jac(s), 0.009875):.3f}, at h {h_new:.5f}: {rk4_radius(jac(s), h_new):.4f}, at h 0.00395: {rk4_radius(jac(s), 0.00395):.4f}; h_new*x = {h_new*s[0]:.3f}")
print("(c) typical orbit, 200 000 steps sampled every 5:")
samp = orbit[:200_000:5]
re_max, abs_max, r_max = 0.0, 0.0, 0.0
for s in samp:
    ev = np.linalg.eigvals(jac(s))
    re_max = max(re_max, np.max(np.abs(ev.real))); abs_max = max(abs_max, np.max(np.abs(ev)))
    r_max = max(r_max, np.max(np.abs(np.exp(0) + 0)) if False else max(np.abs(1 + h_new*e + (h_new*e)**2/2 + (h_new*e)**3/6 + (h_new*e)**4/24) for e in ev))
print(f"   max |Re eig| {re_max:.1f}, max |eig| {abs_max:.1f}; max_i |R(h lambda_i)| at the new step {r_max:.4f} (the unstable physical modes give values slightly above 1 by h*lambda_u); margin 2.785/(h max|Re eig|) = {2.785/(h_new*re_max):.1f}")
