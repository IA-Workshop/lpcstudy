"""Dynamical systems, flow maps and Lyapunov exponents.

All systems are autonomous ODEs ``ds/dt = f(s)``. The flow map over one
observation interval ``Delta`` is approximated by fixed-step RK4 with
``substeps`` internal steps, which keeps every computation (trajectories,
tangent propagation, ensembles) vectorizable with ``jax.vmap``.

The observation interval is chosen per system so that one Lyapunov time
(``1 / lambda_max``) equals ``steps_per_lyapunov`` observation steps
(30, the ``dysts`` convention used in the Methodology document).
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field

import jax
import jax.numpy as jnp
import numpy as np

jax.config.update("jax_enable_x64", True)

VectorField = Callable[[jnp.ndarray, dict[str, float]], jnp.ndarray]


def lorenz63_field(state: jnp.ndarray, params: dict[str, float]) -> jnp.ndarray:
    """Lorenz-63 vector field.

    Parameters
    ----------
    state : jnp.ndarray
        State ``(x, y, z)``.
    params : dict[str, float]
        Keys ``sigma``, ``rho``, ``beta``.

    Returns
    -------
    jnp.ndarray
        Time derivative of the state.
    """
    x, y, z = state[0], state[1], state[2]
    return jnp.stack([
        params["sigma"] * (y - x),
        x * (params["rho"] - z) - y,
        x * y - params["beta"] * z,
    ])


def rossler_field(state: jnp.ndarray, params: dict[str, float]) -> jnp.ndarray:
    """Rössler vector field.

    Parameters
    ----------
    state : jnp.ndarray
        State ``(x, y, z)``.
    params : dict[str, float]
        Keys ``a``, ``b``, ``c``.

    Returns
    -------
    jnp.ndarray
        Time derivative of the state.
    """
    x, y, z = state[0], state[1], state[2]
    return jnp.stack([
        -y - z,
        x + params["a"] * y,
        params["b"] + z * (x - params["c"]),
    ])


def chua_field(state: jnp.ndarray, params: dict[str, float]) -> jnp.ndarray:
    """Dimensionless Chua circuit with the piecewise-linear diode.

    The nonlinearity ``f(x) = m1 x + (m0 - m1)(|x + 1| - |x - 1|) / 2`` is used
    exactly. Its derivative is defined everywhere except the two breakpoints
    (a set of measure zero), so automatic differentiation returns the exact
    Jacobian almost everywhere and no smoothing is needed.

    Parameters
    ----------
    state : jnp.ndarray
        State ``(x, y, z)``.
    params : dict[str, float]
        Keys ``alpha``, ``beta``, ``m0``, ``m1``.

    Returns
    -------
    jnp.ndarray
        Time derivative of the state.
    """
    x, y, z = state[0], state[1], state[2]
    diode = params["m1"] * x + 0.5 * (params["m0"] - params["m1"]) * (
        jnp.abs(x + 1.0) - jnp.abs(x - 1.0))
    return jnp.stack([
        params["alpha"] * (y - x - diode),
        x - y + z,
        -params["beta"] * y,
    ])


@dataclass(frozen=True)
class SystemSpec:
    """Static description of a dynamical system.

    Attributes
    ----------
    name : str
        Identifier.
    field_fn : VectorField
        Vector field ``f(state, params)``.
    params : dict[str, float]
        Nominal parameters (used for ground truth).
    dim : int
        State dimension ``m``.
    observed_index : int
        Index of the observed coordinate (``h(s) = s[observed_index]``).
    initial_state : tuple[float, ...]
        Initial condition before burn-in.
    max_dt : float
        Largest RK4 step allowed (natural time units).
    """

    name: str
    field_fn: VectorField
    params: dict[str, float]
    dim: int
    observed_index: int
    initial_state: tuple[float, ...]
    max_dt: float
    extra: dict[str, float] = field(default_factory=dict)


SYSTEMS: dict[str, SystemSpec] = {
    "lorenz63": SystemSpec(
        name="lorenz63", field_fn=lorenz63_field,
        params={"sigma": 10.0, "rho": 28.0, "beta": 8.0 / 3.0},
        dim=3, observed_index=0, initial_state=(1.0, 1.0, 1.0), max_dt=0.01),
    "rossler": SystemSpec(
        name="rossler", field_fn=rossler_field,
        params={"a": 0.2, "b": 0.2, "c": 5.7},
        dim=3, observed_index=0, initial_state=(1.0, 1.0, 0.0), max_dt=0.04),
    "chua": SystemSpec(
        name="chua", field_fn=chua_field,
        params={"alpha": 15.6, "beta": 28.0, "m0": -1.143, "m1": -0.714},
        dim=3, observed_index=0, initial_state=(0.7, 0.0, 0.0), max_dt=0.005),
}


def make_flow_step(spec: SystemSpec, params: dict[str, float], interval: float
                   ) -> Callable[[jnp.ndarray], jnp.ndarray]:
    """Build the flow map over one observation interval (fixed-step RK4).

    Parameters
    ----------
    spec : SystemSpec
        System description (provides the vector field and ``max_dt``).
    params : dict[str, float]
        Parameters to integrate with (nominal or perturbed).
    interval : float
        Observation interval ``Delta`` in natural time units.

    Returns
    -------
    Callable[[jnp.ndarray], jnp.ndarray]
        Pure function ``state -> Phi^Delta(state)``.
    """
    substeps = max(1, math.ceil(interval / spec.max_dt))
    dt = interval / substeps
    field_fn = spec.field_fn

    def rk4_step(state: jnp.ndarray) -> jnp.ndarray:
        k1 = field_fn(state, params)
        k2 = field_fn(state + 0.5 * dt * k1, params)
        k3 = field_fn(state + 0.5 * dt * k2, params)
        k4 = field_fn(state + dt * k3, params)
        return state + dt / 6.0 * (k1 + 2.0 * k2 + 2.0 * k3 + k4)

    def flow_step(state: jnp.ndarray) -> jnp.ndarray:
        return jax.lax.fori_loop(0, substeps, lambda _, s: rk4_step(s), state)

    return flow_step


def simulate_trajectory(step_fn: Callable[[jnp.ndarray], jnp.ndarray],
                        initial: jnp.ndarray, n_steps: int) -> np.ndarray:
    """Iterate a flow map and return the visited states.

    Parameters
    ----------
    step_fn : Callable
        Flow map over one observation interval.
    initial : jnp.ndarray
        Initial state.
    n_steps : int
        Number of states returned (the first is ``initial``).

    Returns
    -------
    np.ndarray
        Array of shape ``(n_steps, m)``.
    """
    def body(state, _):
        nxt = step_fn(state)
        return nxt, state

    _, states = jax.jit(lambda s: jax.lax.scan(body, s, None, length=n_steps))(
        jnp.asarray(initial, dtype=jnp.float64))
    return np.asarray(states)


def estimate_lyapunov(spec: SystemSpec, interval: float, n_steps: int,
                      burn_in: int) -> float:
    """Largest Lyapunov exponent by Benettin's method with QR re-orthonormalization.

    Parameters
    ----------
    spec : SystemSpec
        System description.
    interval : float
        Step length used for tangent propagation (natural time units).
    n_steps : int
        Number of averaging steps.
    burn_in : int
        Steps discarded before averaging.

    Returns
    -------
    float
        Largest Lyapunov exponent per natural time unit.
    """
    step_fn = make_flow_step(spec, spec.params, interval)
    jac_fn = jax.jacfwd(step_fn)
    state = jnp.asarray(spec.initial_state, dtype=jnp.float64)
    state = jax.jit(lambda s: jax.lax.fori_loop(
        0, burn_in, lambda _, x: step_fn(x), s))(state)

    def body(carry, _):
        current, basis = carry
        propagated = jac_fn(current) @ basis
        q_mat, r_mat = jnp.linalg.qr(propagated)
        signs = jnp.sign(jnp.diag(r_mat))
        q_mat = q_mat * signs
        log_growth = jnp.log(jnp.abs(jnp.diag(r_mat)))
        return (step_fn(current), q_mat), log_growth[0]

    basis = jnp.eye(spec.dim)
    _, growth = jax.jit(lambda c: jax.lax.scan(body, c, None, length=n_steps))(
        (state, basis))
    return float(jnp.sum(growth) / (n_steps * interval))
