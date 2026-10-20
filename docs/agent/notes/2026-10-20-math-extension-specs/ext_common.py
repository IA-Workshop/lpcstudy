"""Candidate SystemSpec entries for the extension (DEVELOPMENT; not in lpcstudy).

S1 hyperchaotic Rossler (Rossler 1979; equations and parameters confirmed by
the researcher note of 2026-10-19, request 1), S2 Lorenz-63 at r = 166.1
(Manneville & Pomeau 1980: r_c = 166.07), S3 the registry Rossler with the
state permuted to (z, x, y) so that observed_index = 0 observes z and the
orbit guard (coordinate 0) bounds z. Nothing here edits lpcstudy.
"""

from dataclasses import replace

import jax
import jax.numpy as jnp

from lpcstudy.systems import SYSTEMS, SystemSpec, lorenz63_field

jax.config.update("jax_enable_x64", True)


def rossler_hyper_field(state, params):
    x, y, z, w = state[0], state[1], state[2], state[3]
    return jnp.stack(
        [
            -y - z,
            x + params["a"] * y + w,
            params["b"] + x * z,
            -params["c"] * z + params["d"] * w,
        ]
    )


def rossler_zfirst_field(state, params):
    # state = (z, x, y): the registry Rossler field with coordinates permuted.
    z, x, y = state[0], state[1], state[2]
    return jnp.stack(
        [
            params["b"] + z * (x - params["c"]),
            -y - z,
            x + params["a"] * y,
        ]
    )


def s1(max_dt=0.005, bound=460.0):
    return SystemSpec(
        name="rossler_hyper",
        field_fn=rossler_hyper_field,
        params={"a": 0.25, "b": 3.0, "c": 0.5, "d": 0.05},
        dim=4,
        observed_index=0,
        initial_state=(-10.0, -6.0, 0.0, 10.0),
        max_dt=max_dt,
        orbit_bound=bound,
    )


def s2(max_dt=0.002, bound=185.0):
    return SystemSpec(
        name="lorenz63_r166",
        field_fn=lorenz63_field,
        params={"sigma": 10.0, "rho": 166.1, "beta": 8.0 / 3.0},
        dim=3,
        observed_index=0,
        initial_state=(1.0, 1.0, 1.0),
        max_dt=max_dt,
        orbit_bound=bound,
    )


def s3(max_dt=0.04, bound=50.0):
    return SystemSpec(
        name="rossler_z",
        field_fn=rossler_zfirst_field,
        params={"a": 0.2, "b": 0.2, "c": 5.7},
        dim=3,
        observed_index=0,
        initial_state=(0.0, 1.0, 1.0),  # (z, x, y) of the registry start (1, 1, 0)
        max_dt=max_dt,
        orbit_bound=bound,
    )


CANDIDATES = {"S1": s1, "S2": s2, "S3": s3, "L63": lambda: SYSTEMS["lorenz63"], "ROS": lambda: SYSTEMS["rossler"]}


# ---- second note (2026-10-20-math-extension-specs-2.md): S4, S5, S6 ----

def hindmarsh_rose_field(state, params):
    # Dysts ``HindmarshRose`` parameterisation (Marhl & Perc 2005 as cited by
    # Dysts). xdot as quoted in the researcher note; ydot and zdot FROM MEMORY
    # of dysts/flows.py, UNVERIFIED (researcher request in the note).
    x, y, z = state[0], state[1], state[2]
    tx, tz = params["tx"], params["tz"]
    return jnp.stack(
        [
            -x + y / tx - params["a"] * x**3 / tx + params["b"] * x**2 / tx + z / tx,
            -params["a"] * x**3 - (params["d"] - params["b"]) * x**2 + z,
            (-params["s"] * x - z + params["c"]) / tz,
        ]
    )


def hyper_jha_field(state, params):
    # Dysts ``HyperJha`` (researcher note D.2, equations quoted in full).
    x, y, z, w = state[0], state[1], state[2], state[3]
    return jnp.stack(
        [
            params["a"] * (y - x) + w,
            -x * z + params["b"] * x - y,
            x * y - params["c"] * z,
            -x * z + params["d"] * w,
        ]
    )


def lorenz96_field(state, params):
    # Lorenz 1995/1996: dX_k/dt = (X_{k+1} - X_{k-2}) X_{k-1} - X_k + F, cyclic.
    return (jnp.roll(state, -1) - jnp.roll(state, 2)) * jnp.roll(state, 1) - state + params["F"]


def s4(max_dt=0.0025, bound=5.0):
    return SystemSpec(
        name="hindmarsh_rose",
        field_fn=hindmarsh_rose_field,
        params={"a": 0.49, "b": 1.0, "c": 0.0322, "d": 1.0, "s": 1.0, "tx": 0.03, "tz": 0.8},
        dim=3,
        observed_index=0,
        initial_state=(0.1, 0.1, 0.1),
        max_dt=max_dt,
        orbit_bound=bound,
    )


def s5(max_dt=0.0025, bound=80.0):
    return SystemSpec(
        name="hyper_jha",
        field_fn=hyper_jha_field,
        params={"a": 10.0, "b": 28.0, "c": 2.667, "d": 1.3},
        dim=4,
        observed_index=0,
        initial_state=(1.0, 1.0, 1.0, 1.0),
        max_dt=max_dt,
        orbit_bound=bound,
    )


def s6(max_dt=0.005, bound=60.0):
    return SystemSpec(
        name="lorenz96_4",
        field_fn=lorenz96_field,
        params={"F": 20.0},
        dim=4,
        observed_index=0,
        initial_state=(20.0, 20.01, 20.0, 20.0),
        max_dt=max_dt,
        orbit_bound=bound,
    )


CANDIDATES.update({"S4": s4, "S5": s5, "S6": s6})
