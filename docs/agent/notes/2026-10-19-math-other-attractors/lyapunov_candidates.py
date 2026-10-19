"""Full Lyapunov spectra and Kaplan-Yorke dimensions of candidate systems.

An INDEPENDENT Benettin/QR implementation (jax jacfwd of the code's own RK4
flow map, ``lpcstudy.systems.make_flow_step``, re-orthonormalised at every
tangent step) returning the whole spectrum. It is cross-checked against the
code's ``estimate_lyapunov`` (largest exponent only) on Lorenz-63 at the
registry settings (expected 0.905494..., bitwise on this host).

Every number here is a DEVELOPMENT estimate from this script, on CPU, one
thread, with a short run (so a few percent uncertainty on the small exponents
and on d_KY); none is a literature value. The candidate systems' equations and
parameters are written from memory and are marked UNVERIFIED until the
researcher confirms them (numbered requests in the note).

The Benettin standard error is the block standard error of the per-step log
growth over 50 blocks (a conservative first-order figure for the largest
exponent; the exponents are correlated, so d_KY's error is indicative).

Run cost: each system a few seconds to a minute at one thread.
"""

import math
import sys
import time
from dataclasses import replace

import jax
import jax.numpy as jnp
import numpy as np

from lpcstudy.systems import SYSTEMS, SystemSpec, estimate_lyapunov, make_flow_step

jax.config.update("jax_enable_x64", True)


# ----------------------------------------------------------------- fields
def lorenz96_field(s, p):
    f = p["F"]
    return (jnp.roll(s, -1) - jnp.roll(s, 2)) * jnp.roll(s, 1) - s + f


def rossler_hyper_field(s, p):
    x, y, z, w = s[0], s[1], s[2], s[3]
    return jnp.stack([-y - z, x + p["a"] * y + w, p["b"] + x * z, -p["c"] * z + p["d"] * w])


def henon_heiles_field(s, p):
    x, y, px, py = s[0], s[1], s[2], s[3]
    return jnp.stack([px, py, -x - 2 * x * y, -y - x * x + y * y])


def torus_field(s, p):
    # two uncoupled harmonic oscillators, frequencies 1 and sqrt(2): quasi-periodic, lambda = 0
    x1, y1, x2, y2 = s[0], s[1], s[2], s[3]
    return jnp.stack([y1, -x1, p["w"] * y2, -p["w"] * x2])


def chua_cubic_field(s, p):
    x, y, z = s[0], s[1], s[2]
    diode = p["a"] * x + p["b"] * x**3
    return jnp.stack([p["alpha"] * (y - x - diode), x - y + z, -p["beta"] * y])


def duffing_field(s, p):
    # autonomous form of the forced Duffing oscillator with a phase variable
    x, v, th = s[0], s[1], s[2]
    return jnp.stack([v, -p["delta"] * v - p["alpha"] * x - p["beta"] * x**3 + p["gamma"] * jnp.cos(th), jnp.full_like(th, p["omega"])])


def spec(name, field, params, dim, init, dt, bound):
    return SystemSpec(name=name, field_fn=field, params=params, dim=dim, observed_index=0,
                      initial_state=init, max_dt=dt, orbit_bound=bound)


L63 = SYSTEMS["lorenz63"]
ROS = SYSTEMS["rossler"]
CHUA = SYSTEMS["chua"]
candidates = [
    ("lorenz63 (registry, reference)", L63),
    ("lorenz63 r=166.1 (type-I intermittency, UNVERIFIED regime)", replace(L63, params={"sigma": 10.0, "rho": 166.1, "beta": 8 / 3}, max_dt=0.002, orbit_bound=120.0)),
    ("lorenz63 r=166.2", replace(L63, params={"sigma": 10.0, "rho": 166.2, "beta": 8 / 3}, max_dt=0.002, orbit_bound=120.0)),
    ("rossler (registry, reference)", ROS),
    ("rossler c=2.5 (expected period-1 limit cycle, UNVERIFIED)", replace(ROS, params={"a": 0.2, "b": 0.2, "c": 2.5})),
    ("rossler funnel a=0.3 b=0.2 c=5.7 (UNVERIFIED parameters)", replace(ROS, params={"a": 0.3, "b": 0.2, "c": 5.7}, max_dt=0.02, orbit_bound=40.0)),
    ("rossler funnel a=0.343 b=1.82 c=9.75 (UNVERIFIED parameters)", replace(ROS, params={"a": 0.343, "b": 1.82, "c": 9.75}, max_dt=0.02, orbit_bound=60.0)),
    ("chua (registry, reference)", CHUA),
    ("chua cubic alpha=10 beta=14.87 a=-1.27 b=0.0157? (UNVERIFIED Zhong-type)", spec("chua_cubic", chua_cubic_field, {"alpha": 10.0, "beta": 14.87, "a": -1.27, "b": 0.0157}, 3, (0.1, 0.0, 0.0), 0.005, 50.0)),
    ("rossler hyperchaos a=0.25 b=3 c=0.5 d=0.05 (Rossler 1979, UNVERIFIED)", spec("rossler_hyper", rossler_hyper_field, {"a": 0.25, "b": 3.0, "c": 0.5, "d": 0.05}, 4, (-10.0, -6.0, 0.0, 10.0), 0.005, 200.0)),
    ("lorenz96 N=5 F=8", spec("l96_5", lorenz96_field, {"F": 8.0}, 5, (8.0, 8.01, 8.0, 8.0, 8.0), 0.005, 40.0)),
    ("lorenz96 N=6 F=8", spec("l96_6", lorenz96_field, {"F": 8.0}, 6, (8.0, 8.01, 8.0, 8.0, 8.0, 8.0), 0.005, 40.0)),
    ("lorenz96 N=8 F=8", spec("l96_8", lorenz96_field, {"F": 8.0}, 8, tuple([8.0, 8.01] + [8.0] * 6), 0.005, 40.0)),
    ("henon-heiles E=1/6, start (0,0.1,px,0.3) chaotic? (energy 1/6; UNVERIFIED chaotic start)", None),
    ("henon-heiles E=1/8, start (0,0.1,px,0.2)", None),
    ("torus (two oscillators, w=sqrt 2): null case, lambda = 0", spec("torus", torus_field, {"w": math.sqrt(2.0)}, 4, (1.0, 0.0, 1.0, 0.0), 0.05, 2.0)),
    ("duffing delta=0.3 alpha=-1 beta=1 gamma=0.5 omega=1.2 (UNVERIFIED chaotic set)", spec("duffing", duffing_field, {"delta": 0.3, "alpha": -1.0, "beta": 1.0, "gamma": 0.5, "omega": 1.2}, 3, (0.1, 0.1, 0.0), 0.02, 10.0)),
]


def hh_start(E, y, py):
    # kinetic energy px^2/2 = E - V(x=0,y) - py^2/2 with V = (x^2+y^2)/2 + x^2 y - y^3/3
    V = 0.5 * y * y - y**3 / 3
    px2 = 2 * (E - V - 0.5 * py * py)
    assert px2 > 0, px2
    return (0.0, y, math.sqrt(px2), py)


candidates[13] = (candidates[13][0], spec("hh", henon_heiles_field, {}, 4, hh_start(1 / 6, 0.1, 0.3), 0.02, 2.0))
candidates[14] = (candidates[14][0], spec("hh", henon_heiles_field, {}, 4, hh_start(1 / 8, 0.1, 0.2), 0.02, 2.0))


def spectrum(sp: SystemSpec, interval: float, n_steps: int, burn_in: int, n_blocks: int = 50):
    step = make_flow_step(sp, sp.params, interval)
    jac = jax.jacfwd(step)
    dim = sp.dim

    def burn(s):
        return jax.lax.fori_loop(0, burn_in, lambda _, x: step(x), s)

    def body(carry, _):
        s, q = carry
        prop = jac(s) @ q
        q_new, r = jnp.linalg.qr(prop)
        sg = jnp.sign(jnp.diag(r))
        return (step(s), q_new * sg), (jnp.log(jnp.abs(jnp.diag(r))), jnp.max(jnp.abs(s)))

    s0 = jax.jit(burn)(jnp.asarray(sp.initial_state, dtype=jnp.float64))
    (_, _), (growth, amax) = jax.jit(lambda c: jax.lax.scan(body, c, None, length=n_steps))((s0, jnp.eye(dim)))
    growth = np.asarray(growth)
    lam = growth.sum(axis=0) / (n_steps * interval)
    blocks = growth[: (n_steps // n_blocks) * n_blocks].reshape(n_blocks, -1, dim).sum(axis=1) / ((n_steps // n_blocks) * interval)
    se = blocks.std(axis=0, ddof=1) / math.sqrt(n_blocks)
    return lam, se, float(np.max(np.asarray(amax))), bool(np.all(np.isfinite(growth)))


def kaplan_yorke(lam):
    lam = np.sort(lam)[::-1]
    cum = np.cumsum(lam)
    if cum[0] <= 0:
        return 0.0 if lam[0] < 0 else float("nan")  # fixed point or lambda_max = 0 (a torus: d = number of zero exponents, not given by KY)
    j = int(np.max(np.nonzero(cum >= 0)[0]))
    if j + 1 >= len(lam):
        return float(len(lam))
    return j + 1 + cum[j] / abs(lam[j + 1])


t0 = time.time()
ref = estimate_lyapunov(L63, 20 * L63.max_dt, 100_000, 5_000)
print(f"cross-check: lpcstudy.estimate_lyapunov(lorenz63, registry settings) = {ref!r} "
      f"(expected 0.9054940534657817 on this host)  [{time.time()-t0:.0f} s]")
print()
print(f"{'system':70s} {'lambda spectrum (per unit time)':48s} {'se(l1)':8s} {'d_KY':6s} {'LT(1/l1)':9s} max|x|  finite")
names = [c[0] for c in candidates]
only = sys.argv[1:]
for name, sp in candidates:
    if only and not any(o in name for o in only):
        continue
    t1 = time.time()
    interval = 20 * sp.max_dt
    n_steps = 60_000 if sp.dim <= 4 else 40_000
    try:
        lam, se, amax, fin = spectrum(sp, interval, n_steps, 5_000)
    except Exception as exc:  # report, never hide
        print(f"{name:70s} FAILED: {exc!r}")
        continue
    dky = kaplan_yorke(lam)
    lt = 1 / lam.max() if lam.max() > 0 else float("inf")
    lam_s = ", ".join(f"{v:+.4f}" for v in np.sort(lam)[::-1])
    print(f"{name:70s} [{lam_s}] {se[0]:.4f}   {dky:5.2f}  {lt:8.2f}  {amax:6.2f}  {fin}  [{time.time()-t1:.0f} s]")
print(f"total {time.time()-t0:.0f} s")
