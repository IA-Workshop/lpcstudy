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


def s1(max_dt=0.01, bound=300.0):
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
