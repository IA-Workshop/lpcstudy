"""Scan of r around the Manneville-Pomeau threshold r_c = 166.07 (sigma 10,
beta 8/3), RK4 max_dt 0.002 (DEVELOPMENT). Per r: lambda_max (Benettin,
interval 0.04, 200 000 steps, block se); then on a 400 000-step orbit at
interval 0.04 (16 000 time units) the successive z-maxima, the fraction of
cycles with |z_max(n+1) - z_max(n)| < 1 and < 3 ('laminar', the ghost cycle
being symmetric so both halves have equal z_max), the laminar run lengths,
and the fraction of 1.6-time-unit windows whose Benettin growth is below
0.1 per time unit. r = 166.0 (below r_c) is the control: the limit cycle."""

import math
from dataclasses import replace

import jax
import jax.numpy as jnp
import numpy as np

from lpcstudy.systems import make_flow_step

from ext_common import CANDIDATES

base = CANDIDATES["S2"]()
interval = 0.04


def run(r):
    sp = replace(base, params={"sigma": 10.0, "rho": r, "beta": 8.0 / 3.0})
    step = make_flow_step(sp, sp.params, interval)
    jac = jax.jacfwd(step)

    def body(carry, _):
        s, q = carry
        prop = jac(s) @ q
        qn, rm = jnp.linalg.qr(prop)
        sg = jnp.sign(jnp.diag(rm))
        return (step(s), qn * sg), (jnp.log(jnp.abs(rm[0, 0])), s[2])

    s0 = jax.jit(lambda s: jax.lax.fori_loop(0, 25_000, lambda _, x: step(x), s))(jnp.asarray((1.0, 1.0, 1.0)))
    n = 400_000
    (_, _), (g, z) = jax.jit(lambda c: jax.lax.scan(body, c, None, length=n))((s0, jnp.eye(3)))
    g, z = np.asarray(g), np.asarray(z)
    lam = g.sum() / (n * interval)
    blocks = g.reshape(50, -1).sum(axis=1) / (n / 50 * interval)
    se = blocks.std(ddof=1) / math.sqrt(50)
    win = 40  # 1.6 time units
    per_win = g[: (n // win) * win].reshape(-1, win).sum(axis=1) / (win * interval)
    peaks = np.nonzero((z[1:-1] > z[:-2]) & (z[1:-1] >= z[2:]))[0] + 1
    zmax = z[peaks]
    d = np.abs(np.diff(zmax))
    out = [f"r {r:7.3f}: lambda {lam:.4f} +- {se:.4f}; windows(1.6 tu) with growth < 0.1: {np.mean(per_win < 0.1):.3f}; "
           f"{len(zmax)} z-maxima, lag-1 |dz| median {np.median(d):.2f}; laminar fraction (<1) {np.mean(d < 1):.3f}, (<3) {np.mean(d < 3):.3f}"]
    for thr in (1.0, 3.0):
        f = d < thr
        runs, cur = [], 0
        for v in f:
            cur = cur + 1 if v else (runs.append(cur) if cur else None) or 0
        if cur:
            runs.append(cur)
        runs = np.array(runs) if runs else np.array([0])
        out.append(f"    thr {thr}: {len(runs)} laminar phases, length cycles median {np.median(runs):.0f} p90 {np.quantile(runs, .9):.0f} max {runs.max()}")
    return "\n".join(out)


for r in (166.0, 166.075, 166.08, 166.1, 166.15, 166.2, 166.5, 167.0):
    print(run(r), flush=True)
