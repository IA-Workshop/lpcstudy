"""Is the P1(a) curvature floor c >= rho^2/k true for the study's estimand?

The study's moments are over QUERY-noise draws with the library noise frozen
(``ensemble.forecast_draws``: ``unit_noise`` varies, ``ctx.library_unit_noise``
is fixed). Then the copied future noise xi = rho z_{i*+H} is a constant when
retrieval is stable across draws, so it is not orthogonal to e_P (E[xi e_P] =
xi E[e_P]) and the floor c >= rho^2/k is not implied. Three checks:

(A) A toy counterexample for the conditional estimand: e_C constant (stable
    retrieval), e_P = m + s z with s^2 < rho^2, |e_C - m| small -> c < rho^2.
(B) On Lorenz-63 with the code's own delay map and amplifier: the linearised
    variance of the PLP forecast error in noise units, ||Gamma_H J^+||^2, at
    H = 1, 2, 5, 30 steps. Values below 1 at short H mean Var(e_P) < rho^2 is
    realistic there, so (A) is not contrived. Invariant to the state
    coordinates, so physical coordinates are used (no whitening needed).
(C) The UNCONDITIONAL orthogonality (library noise averaged in): on a Lorenz-63
    delay-vector library, measure E[xi_H] and E[xi_H (e_C - xi_H)] / rho^2
    conditional on retrieval, over fresh library-noise realizations. A
    nonzero value at small H is the selection effect of the H-shifted
    competitor candidate i*+H, whose window contains x_{i*+H}.

DEVELOPMENT, synthetic scratch seed 20261019; CPU, one thread. No preset, no
test, no study seed.
"""

import time

import jax
import jax.numpy as jnp
import numpy as np
from scipy.spatial import cKDTree

from lpcstudy.dynamics import delay_map_forward, make_amplification
from lpcstudy.embedding import delay_vectors
from lpcstudy.systems import SYSTEMS, make_flow_step, simulate_trajectory

jax.config.update("jax_enable_x64", True)
rng = np.random.default_rng(20261019)
t0 = time.time()

# ---------------------------------------------------------------- (A) toy
rho, k = 0.01, 1
m, s = 0.003, np.sqrt(0.4) * rho  # Var(e_P) = 0.4 rho^2
z = rng.standard_normal(200)
e_p = m + s * z
e_c = np.full(200, m + 0.1 * rho)  # retrieval stable: constant CP error
c_cond = np.mean((e_c - e_p) ** 2)
print(f"(A) toy, conditional estimand: c = {c_cond:.3e}, rho^2/k = {rho**2/k:.3e}, "
      f"c/(rho^2/k) = {c_cond/(rho**2/k):.3f}  -> floor violated: {c_cond < rho**2/k}")

# ------------------------------------------------- (B) Lorenz leverage
spec = SYSTEMS["lorenz63"]
lam = 0.9054940534657817  # the code's cached value (runs/baseline/smoke/cache)
interval = 1.0 / (30 * lam)
step = make_flow_step(spec, spec.params, interval)
delay, D = 5, 7
history = (D - 1) * delay
burn = 3000
traj = simulate_trajectory(step, jnp.asarray(spec.initial_state), burn + 20_000)[burn:]
obs = traj[:, 0]
obs_mean, obs_scale = obs.mean(), obs.std()
fwd = delay_map_forward(step, 0, obs_mean, obs_scale, delay, D)
jac_fwd = jax.jit(jax.jacfwd(fwd))
Hs = (1, 2, 5, 10, 30)
amp = make_amplification(step, 0, obs_scale, np.eye(3), max(Hs))


def gamma_rows(s_t):
    """Gamma_H rows (1 x 3, physical coords) for H in Hs at state s_t."""
    jac = jax.jacfwd(step)
    tangent = jnp.eye(3)
    s = jnp.asarray(s_t)
    out = {}
    for h in range(1, max(Hs) + 1):
        tangent = jac(s) @ tangent
        s = step(s)
        if h in Hs:
            out[h] = np.asarray(tangent[0]) / obs_scale
    return out


advance = jax.jit(lambda s: jax.lax.fori_loop(0, history, lambda _, x: step(x), s))
lev = {h: [] for h in Hs}
idx = rng.choice(np.arange(history, len(traj) - 40), size=40, replace=False)
for t in idx:
    s_old = traj[t - history]
    J = np.asarray(jac_fwd(jnp.asarray(s_old)))  # D x 3, d X_t / d s_old
    Q = np.asarray(jax.jacfwd(advance)(jnp.asarray(s_old)))  # d s_t / d s_old
    J_t = J @ np.linalg.inv(Q)  # delay-map Jacobian at s_t
    Jp = np.linalg.pinv(J_t)  # 3 x D
    g = gamma_rows(traj[t])
    for h in Hs:
        lev[h].append(float(np.sum((g[h] @ Jp) ** 2)))
print("(B) Lorenz-63, ||Gamma_H J^+||^2 = Var(e_P)/rho^2 to first order, 40 attractor states")
print("    H(steps)  median   min     max    fraction < 1")
for h in Hs:
    a = np.array(lev[h])
    print(f"    {h:4d}     {np.median(a):7.3f} {a.min():7.3f} {a.max():8.3f}   {np.mean(a < 1):.2f}")

# ---------------------------------------------- (C) selection effect on xi
lib_len = 10_000
lib_states = traj[: lib_len + history + 40]
lib_clean = (lib_states[:, 0] - obs_mean) / obs_scale
lib_idx = np.arange(history, history + lib_len)
q_times = rng.choice(np.arange(lib_len + history + 100, len(traj) - 40), size=300, replace=False)
q_clean_vec = delay_vectors((traj[:, 0] - obs_mean) / obs_scale, q_times, delay, D)
truth = (traj[:, 0] - obs_mean) / obs_scale
R, Mq = 30, 4
Hsel = (1, 2, 3, 5, 10, 30)
acc_xi = {h: [] for h in Hsel}
acc_cross = {h: [] for h in Hsel}
for r in range(R):
    zlib = rng.standard_normal(len(lib_clean))
    noisy = lib_clean + rho * zlib
    tree = cKDTree(delay_vectors(noisy, lib_idx, delay, D))
    qn = q_clean_vec[:, None, :] + rho * rng.standard_normal((len(q_times), Mq, D))
    _, pos = tree.query(qn.reshape(-1, D), k=1, workers=1)
    istar = lib_idx[pos].reshape(len(q_times), Mq)
    for h in Hsel:
        xi = rho * zlib[istar + h]  # copied future noise
        mismatch = lib_clean[istar + h] - truth[q_times + h][:, None]  # e_C - xi
        acc_xi[h].append(xi.ravel())
        acc_cross[h].append((xi * mismatch).ravel())
print(f"(C) Lorenz-63 library N={lib_len}, D={D}, tau={delay}, rho={rho}, {R} library-noise "
      f"realizations x {len(q_times)} queries x {Mq} draws")
print("    H   E[xi]/rho (+-se)      E[xi (e_C - xi)]/rho^2 (+-se)   E[xi^2]/rho^2")
for h in Hsel:
    xi = np.concatenate(acc_xi[h]) / rho
    cr = np.concatenate(acc_cross[h]) / rho**2
    n = len(xi)
    print(f"   {h:3d}  {xi.mean():+.4f} ({xi.std()/np.sqrt(n):.4f})      "
          f"{cr.mean():+.4f} ({cr.std()/np.sqrt(n):.4f})            {np.mean(xi**2):.4f}")
print(f"elapsed {time.time()-t0:.1f} s")
