"""WU-0005.6 mathematics check, E1: an independent mirror of the LM loop (not production code).

DEVELOPMENT (test configuration, literal default_rng seeds; not a study seed).
Lorenz-63, RK4, dt = 1/(30*0.9056), D = 7, delay 5, x observed, diagonal whitening.
Checks:
  (a) chunk/batch-shape invariance of jit(vmap(refine)) (bitwise);
  (b) prefix property: the 15-iteration result equals the 30-iteration iterate at k = 15 (bitwise),
      hence c30 <= c15 exactly per estimate;
  (c) per-estimate convergence 15 -> 30 -> 60 in whitened units relative to rho*nu, and the
      chi-square(4) crossing counts, at several start errors and noise levels.
"""
import sys
import numpy as np
import jax
import jax.numpy as jnp

jax.config.update("jax_enable_x64", True)

DT = 1.0 / (30 * 0.9056)
SIG, RHO_L, BETA = 10.0, 28.0, 8.0 / 3.0
D, TAU, M = 7, 5, 3
SPAN = (D - 1) * TAU


def f(s):
    x, y, z = s
    return jnp.array([SIG * (y - x), x * (RHO_L - z) - y, x * y - BETA * z])


def step(s):
    k1 = f(s); k2 = f(s + 0.5 * DT * k1); k3 = f(s + 0.5 * DT * k2); k4 = f(s + DT * k3)
    return s + DT / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)


# attractor states
def _traj(s0, n):
    def body(c, _):
        n_ = step(c)
        return n_, n_
    return jax.lax.scan(body, s0, None, length=n)[1]
traj = np.asarray(jax.jit(_traj, static_argnums=1)(jnp.array([1.0, 1.0, 20.0]), 43000))[3000:]
MEAN = traj.mean(0)
STD = traj.std(0)
OBS_MEAN, OBS_SCALE = MEAN[0], STD[0]
ROOT = jnp.diag(jnp.asarray(STD))        # unwhiten
WHITEN = jnp.diag(jnp.asarray(1.0 / STD))
MEAN_J = jnp.asarray(MEAN)


def fwd(state):
    def body(c, _):
        n = step(c)
        return n, n[0]
    _, path = jax.lax.scan(body, state, None, length=SPAN)
    path = jnp.concatenate([state[0][None], path])
    vals = (path - OBS_MEAN) / OBS_SCALE
    return vals[(D - 1 - jnp.arange(D)) * TAU]


def generate(u):
    return fwd(MEAN_J + ROOT @ u)


jac = jax.jacfwd(generate)


def cost(u, target):
    r = target - generate(u)
    v = jnp.sum(r ** 2)
    return jnp.where(jnp.isfinite(v), v, jnp.inf)


def lm_step(carry, target):
    u, c_u, damping = carry
    a = jac(u)
    a = jnp.where(jnp.isfinite(a), a, 0.0)
    normal = a.T @ a
    rhs = a.T @ (target - generate(u))
    scale = jnp.trace(normal) / u.shape[0] + 1e-12
    delta = jnp.linalg.solve(normal + damping * scale * jnp.eye(u.shape[0]), rhs)
    cand = u + delta
    c_c = cost(cand, target)
    acc = c_c < c_u
    return (jnp.where(acc, cand, u), jnp.where(acc, c_c, c_u),
            jnp.where(acc, damping / 3.0, damping * 4.0))


def make_refine(n_iter):
    def single(u0, target):
        def body(carry, _):
            new = lm_step(carry, target)
            return new, (new[0], new[1])
        carry, ys = jax.lax.scan(body, (u0, cost(u0, target), 1e-3), None, length=n_iter)
        return carry[0], carry[1], ys
    return jax.jit(jax.vmap(single))


def advance(s_old):
    return jax.lax.fori_loop(0, SPAN, lambda _, x: step(x), s_old)


adv_b = jax.jit(jax.vmap(advance))
jstep = jax.jacfwd(step)


def nu_single(state):
    def body(carry, _):
        s_, t = carry
        t = jstep(s_) @ t
        return (step(s_), t), t[0]
    (_, q), rows = jax.lax.scan(body, (state, jnp.eye(3)), None, length=SPAN)
    rows = jnp.concatenate([jnp.eye(3)[0][None, :], rows], axis=0)
    a = rows[(D - 1 - jnp.arange(D)) * TAU] / OBS_SCALE
    cov = WHITEN @ q @ jnp.linalg.inv(a.T @ a) @ q.T @ WHITEN.T
    return jnp.sqrt(jnp.trace(cov))


nu_b = jax.jit(jax.vmap(nu_single))
fwd_b = jax.jit(jax.vmap(fwd))


def run(n_states, n_draws, rho, start_err, seed):
    rng = np.random.default_rng(seed)
    idx = rng.choice(np.arange(SPAN + 10, len(traj) - SPAN - 10, 60), n_states, replace=False)
    s_old = traj[idx]
    s_t = np.asarray(adv_b(jnp.asarray(s_old)))
    clean = np.asarray(fwd_b(jnp.asarray(s_old)))
    u_true = (s_old - MEAN) / STD
    noise = rng.standard_normal((n_states, n_draws, D))
    start = rng.standard_normal((n_states, n_draws, M))
    # heavy-tailed start error: a mixture of the given scale and 4x the scale (20%)
    big = rng.random((n_states, n_draws)) < 0.2
    scale = np.where(big, 4.0 * start_err, start_err)[..., None]
    targets = (clean[:, None, :] + rho * noise).reshape(-1, D)
    u0 = (u_true[:, None, :] + scale * start).reshape(-1, M)
    return dict(s_t=np.repeat(s_t, n_draws, 0), u0=u0, targets=targets, n_states=n_states,
                n_draws=n_draws, rho=rho)


def main():
    out = {}
    # (a) chunk invariance and (b) prefix property
    d = run(64, 8, 0.01, 0.05, 20261012)
    r15, r30 = make_refine(15), make_refine(30)
    u15, c15, _ = r15(jnp.asarray(d["u0"]), jnp.asarray(d["targets"]))
    u30, c30, ys30 = r30(jnp.asarray(d["u0"]), jnp.asarray(d["targets"]))
    u15, c15, u30, c30 = map(np.asarray, (u15, c15, u30, c30))
    pre_u = np.asarray(ys30[0])[:, 14]
    pre_c = np.asarray(ys30[1])[:, 14]
    print("(b) prefix: u15 == u30@15 bitwise:", np.array_equal(u15, pre_u),
          " c15 == c30@15:", np.array_equal(c15, pre_c),
          " max|du|:", np.max(np.abs(u15 - pre_u)), " c30<=c15 all:", bool(np.all(c30 <= c15)))
    full = np.asarray(r15(jnp.asarray(d["u0"]), jnp.asarray(d["targets"]))[0])
    n = len(d["u0"])
    parts = []
    for size in (40, 24):  # different batch shapes: 512 = 12*40 + 32 tail
        chunks = [np.asarray(r15(jnp.asarray(d["u0"][i:i + size]),
                                 jnp.asarray(d["targets"][i:i + size]))[0])
                  for i in range(0, n, size)]
        parts.append(np.concatenate(chunks))
    one = np.concatenate([np.asarray(r15(jnp.asarray(d["u0"][i:i + 1]),
                                         jnp.asarray(d["targets"][i:i + 1]))[0])
                          for i in range(0, 32)])
    print("(a) chunk 40 == full:", np.array_equal(parts[0], full),
          " chunk 24 == full:", np.array_equal(parts[1], full),
          " batch 1 == full (first 32):", np.array_equal(one, full[:32]),
          " max|diff| (40, 24, 1):", np.max(np.abs(parts[0] - full)),
          np.max(np.abs(parts[1] - full)), np.max(np.abs(one - full[:32])))
    # same chunking twice (determinism)
    again = np.concatenate([np.asarray(r15(jnp.asarray(d["u0"][i:i + 40]),
                                           jnp.asarray(d["targets"][i:i + 40]))[0])
                            for i in range(0, n, 40)])
    print("(a) same chunking twice bitwise:", np.array_equal(again, parts[0]))
    # (c) convergence 15 -> 30 -> 60
    r60 = make_refine(60)
    thr = 18.4668
    for rho, se in ((0.01, 0.02), (0.01, 0.2), (0.05, 0.02), (0.05, 0.2)):
        d = run(128, 16, rho, se, 7 + int(1000 * rho) + int(100 * se))
        res = {}
        for k, fn in ((15, r15), (30, r30), (60, r60)):
            u, c, _ = fn(jnp.asarray(d["u0"]), jnp.asarray(d["targets"]))
            u = np.asarray(u)
            s_old = MEAN + u * STD
            sh = np.asarray(adv_b(jnp.asarray(s_old)))
            res[k] = dict(sw=sh / STD, c=np.asarray(c) / rho ** 2,
                          nu=np.asarray(nu_b(jnp.asarray(s_old))), s_old=s_old)
        nu30 = res[30]["nu"]
        err30 = np.linalg.norm(res[30]["sw"] - d["s_t"] / STD, axis=1)
        a = np.linalg.norm(res[15]["sw"] - res[30]["sw"], axis=1) / (rho * nu30)
        b = np.linalg.norm(res[30]["sw"] - res[60]["sw"], axis=1) / (rho * nu30)
        ns = d["n_states"]
        per_state_a = (a > 0.1).reshape(ns, -1).mean(1)
        per_state_b = (b > 0.1).reshape(ns, -1).mean(1)
        se_a = per_state_a.std(ddof=1) / np.sqrt(ns)
        blk = per_state_a[: ns // 5 * 5].reshape(-1, 5).mean(1)
        se_blk = blk.std(ddof=1) / np.sqrt(len(blk))
        moving = a > 1e-6
        up = {k: res[k]["c"] > thr for k in res}
        print(f"\n(c) rho={rho} start={se} (20% at 4x): n={len(a)}")
        print(f"   err30/(rho nu) median {np.median(err30 / (rho * nu30)):.3f}")
        print(f"   frac |d15-30|>0.1 rho nu: {np.mean(a > 0.1):.4f} (cluster SE {se_a:.4f}, "
              f"block-5 SE {se_blk:.4f});  frac |d30-60|>0.1: {np.mean(b > 0.1):.4f}")
        print(f"   frac > 0.1*err30 (WU-0005.4 def): "
              f"{np.mean(np.linalg.norm(res[15]['sw'] - res[30]['sw'], axis=1) > 0.1 * err30):.4f}")
        print(f"   quantiles d15-30/(rho nu) 50/90/99/max: "
              f"{np.quantile(a, [0.5, 0.9, 0.99]).round(5)} {a.max():.3g}")
        print(f"   quantiles d30-60/(rho nu) 50/90/99/max: "
              f"{np.quantile(b, [0.5, 0.9, 0.99]).round(5)} {b.max():.3g}")
        if moving.any():
            print(f"   moving (a>1e-6): {moving.sum()}; median a {np.median(a[moving]):.3g}, "
                  f"median b {np.median(b[moving]):.3g}; sum a {a.sum():.3g}, sum b {b.sum():.3g}")
        print(f"   above chi2(0.999): 15 {up[15].sum()}, 30 {up[30].sum()}, 60 {up[60].sum()}; "
              f"15->30 above->below {np.sum(up[15] & ~up[30])}, below->above {np.sum(~up[15] & up[30])};"
              f" 30->60 above->below {np.sum(up[30] & ~up[60])}")
        sw = (a > 0.1)
        tr = up[15] & ~up[30]
        print(f"   of the {sw.sum()} estimates moving >0.1 rho nu (15->30), {np.sum(sw & tr)} are "
              f"chi2 crossings; share of sum a from crossings: {a[tr].sum() / max(a.sum(), 1e-300):.3f}")
        print(f"   monotone c30<=c15: {bool(np.all(res[30]['c'] <= res[15]['c']))}, "
              f"c60<=c30: {bool(np.all(res[60]['c'] <= res[30]['c']))}")


if __name__ == "__main__":
    main()
