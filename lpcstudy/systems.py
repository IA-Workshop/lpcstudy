"""The three chaotic systems, their flow maps and Lyapunov exponents.

The study compares an analog forecaster (CP) with a physics-based forecaster
(PLP) on three chaotic systems: Lorenz-63, Rossler and Chua. This module
defines those systems as ordinary differential equations (ODEs) of the form
``ds/dt = f(s)``, and turns each one into a "flow map": a function that moves
a state forward by one observation interval. The flow map is built from
fixed-step RK4 (a standard fourth-order Runge-Kutta ODE solver), so that every
computation (trajectories, tangent propagation, ensembles) can be vectorized
with ``jax.vmap``.

The observation interval is chosen for each system so that one Lyapunov time
(``1 / lambda_max``, the time over which small errors grow by a factor of e)
equals ``steps_per_lyapunov`` observation steps. The value 30 is the ``dysts``
convention used in the Methods document.

The module also estimates the largest Lyapunov exponent and guards every
simulated orbit: a run is refused if an orbit becomes non-finite or leaves the
attractor bound (DEF-0015). ``data.py`` builds the trajectories from these
functions; ``dynamics.py``, ``oracle.py``, ``validation.py`` and the rest of
the pipeline reuse ``make_flow_step`` for forecasts and tangent dynamics.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass

import jax
import jax.numpy as jnp
import numpy as np

jax.config.update("jax_enable_x64", True)

VectorField = Callable[[jnp.ndarray, dict[str, float]], jnp.ndarray]


def lorenz63_field(state: jnp.ndarray, params: dict[str, float]) -> jnp.ndarray:
    """Evaluate the Lorenz-63 vector field.

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
    return jnp.stack(
        [
            params["sigma"] * (y - x),
            x * (params["rho"] - z) - y,
            x * y - params["beta"] * z,
        ]
    )


def rossler_field(state: jnp.ndarray, params: dict[str, float]) -> jnp.ndarray:
    """Evaluate the Rossler vector field.

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
    return jnp.stack(
        [
            -y - z,
            x + params["a"] * y,
            params["b"] + z * (x - params["c"]),
        ]
    )


def chua_field(state: jnp.ndarray, params: dict[str, float]) -> jnp.ndarray:
    """Evaluate the dimensionless Chua circuit with its piecewise-linear diode.

    The diode nonlinearity is
    ``f(x) = m1 x + (m0 - m1)(|x + 1| - |x - 1|) / 2``, used exactly. Its
    derivative exists everywhere except at the two breakpoints (a set of
    measure zero), so automatic differentiation returns the exact Jacobian
    almost everywhere and no smoothing is needed.

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
        jnp.abs(x + 1.0) - jnp.abs(x - 1.0)
    )
    return jnp.stack(
        [
            params["alpha"] * (y - x - diode),
            x - y + z,
            -params["beta"] * y,
        ]
    )


@dataclass(frozen=True)
class SystemSpec:
    """Static description of one dynamical system.

    Attributes
    ----------
    name : str
        Identifier, such as ``"lorenz63"``.
    field_fn : VectorField
        Vector field ``f(state, params)``.
    params : dict[str, float]
        Nominal parameters (used for the ground truth).
    dim : int
        State dimension ``m``.
    observed_index : int
        Index of the observed coordinate, so the observation is
        ``h(s) = s[observed_index]``.
    initial_state : tuple[float, ...]
        Initial condition before burn-in (the stretch of the orbit that is
        thrown away so the state settles onto the attractor).
    max_dt : float
        Largest RK4 step allowed (natural time units).
    orbit_bound : float or None
        Bound ``B`` on ``|s[0]|`` for every orbit simulated for the study
        (DEF-0015, DEC-0017 Q1). The guards refuse an orbit with a non-finite
        coordinate or with ``|s[0]| > B``. ``None`` is refused by every guard
        (``ValueError``): a spec without a bound is never silently unguarded.
        The bound is on the first coordinate only, because ``z`` exceeds ``B``
        on the Lorenz-63 and Chua attractors.
    """

    name: str
    field_fn: VectorField
    params: dict[str, float]
    dim: int
    observed_index: int
    initial_state: tuple[float, ...]
    max_dt: float
    orbit_bound: float | None = None


SYSTEMS: dict[str, SystemSpec] = {
    "lorenz63": SystemSpec(
        name="lorenz63",
        field_fn=lorenz63_field,
        params={"sigma": 10.0, "rho": 28.0, "beta": 8.0 / 3.0},
        dim=3,
        observed_index=0,
        initial_state=(1.0, 1.0, 1.0),
        max_dt=0.01,
        orbit_bound=40.0,
    ),
    "rossler": SystemSpec(
        name="rossler",
        field_fn=rossler_field,
        params={"a": 0.2, "b": 0.2, "c": 5.7},
        dim=3,
        observed_index=0,
        initial_state=(1.0, 1.0, 0.0),
        max_dt=0.04,
        orbit_bound=25.0,
    ),
    "chua": SystemSpec(
        name="chua",
        field_fn=chua_field,
        params={"alpha": 15.6, "beta": 28.0, "m0": -1.143, "m1": -0.714},
        dim=3,
        observed_index=0,
        initial_state=(0.7, 0.0, 0.0),
        max_dt=0.005,
        orbit_bound=3.0,
    ),
}


def make_flow_step(
    spec: SystemSpec, params: dict[str, float], interval: float
) -> Callable[[jnp.ndarray], jnp.ndarray]:
    """Build the flow map over one observation interval (fixed-step RK4).

    The interval is cut into equal substeps, none longer than
    ``spec.max_dt``, and one RK4 step is taken for each substep.

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


def simulate_trajectory(
    step_fn: Callable[[jnp.ndarray], jnp.ndarray],
    initial: jnp.ndarray,
    n_steps: int,
) -> np.ndarray:
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
        jnp.asarray(initial, dtype=jnp.float64)
    )
    return np.asarray(states)


class OrbitDivergence(RuntimeError):
    """An orbit left the attractor bound or became non-finite (DEF-0015).

    The run is refused: a diverging orbit is never carried on (DEC-0017 Q1,
    DEC-0026 item 3).
    """


def checked_bound(spec: SystemSpec) -> float:
    """Return ``spec.orbit_bound`` after checking that the guards can use it.

    Raises
    ------
    ValueError
        If the bound is missing, not finite or not positive, or if
        ``spec.observed_index`` is not 0. The bound was derived for the first
        coordinate, so reading another one would pass a diverging orbit
        silently.
    """
    bound = spec.orbit_bound
    if bound is None or not (math.isfinite(bound) and bound > 0.0):
        raise ValueError(
            f"orbit_bound of '{spec.name}' must be a positive finite float, "
            f"got {bound!r}: a spec without a bound is refused, never "
            "unguarded"
        )
    if spec.observed_index != 0:
        raise ValueError(
            f"observed_index of '{spec.name}' is {spec.observed_index}: the "
            "orbit bound applies to coordinate 0 only"
        )
    return float(bound)


def _refuse(
    spec: SystemSpec, orbit: str, largest: float, first: int
) -> OrbitDivergence:
    """Build the refusal: system, orbit, first bad step, max |x|, the bound."""
    size = f"{largest:.17g}" if math.isfinite(largest) else "non-finite"
    return OrbitDivergence(
        f"orbit '{orbit}' of '{spec.name}' left the bound: first failing "
        f"step {first}, max|x| {size}, bound {spec.orbit_bound:g} "
        "(the start is step 0)"
    )


def guard_orbit(spec: SystemSpec, orbit: str, states: np.ndarray) -> float:
    """Accept an orbit only if all values are finite and ``|x| <= B``.

    The test is ``|states[:, 0]| <= B`` (a closed bound: ``B`` itself passes).
    Needs owner review before freeze: it sets the study's time unit.

    Parameters
    ----------
    spec : SystemSpec
        System description; ``orbit_bound`` is ``B``.
    orbit : str
        Name of the orbit for the refusal message (``statistics``, ``main``,
        ``estimator``).
    states : np.ndarray
        Simulated array of shape ``(n, m)``, the burn-in included; row 0 is
        the start.

    Returns
    -------
    float
        ``max_t |states[t, 0]|``, or NaN if any coordinate of any row is
        non-finite (the refusal message then says "non-finite").

    Raises
    ------
    OrbitDivergence
        If a row fails; the message names the first failing row.
    ValueError
        If the bound is unusable (see ``SystemSpec.orbit_bound``) or
        ``states`` has the wrong shape or no rows.
    """
    bound = checked_bound(spec)
    if states.ndim != 2 or states.shape[0] == 0 or states.shape[1] != spec.dim:
        raise ValueError(
            f"orbit '{orbit}' of '{spec.name}': shape {states.shape} is not "
            f"(n >= 1, {spec.dim})"
        )
    finite = np.isfinite(states).all(axis=1)
    # NaN marks any non-finite coordinate.
    size = np.where(finite, np.abs(states[:, 0]), np.nan)
    failed = ~(finite & (size <= bound))
    # NaN propagates; the predicate above is the specification.
    largest = float(size.max())
    if failed.any():
        raise _refuse(spec, orbit, largest, int(np.argmax(failed)))
    return largest


def lyapunov_guarded(
    spec: SystemSpec, interval: float, n_steps: int, burn_in: int
) -> tuple[float, float]:
    """Estimate the largest Lyapunov exponent, with the orbit guard (DEF-0015).

    Benettin's method follows a small perturbation along the orbit. After each
    step a QR factorization (a standard matrix factorization) re-orthonormalizes
    the perturbation directions, and the exponent is the average log growth
    rate of the first direction.

    The guard checks every state ``0 ... burn_in + n_steps - 1`` of the orbit
    (the start is state 0), in the burn-in loop as well as in the averaging
    scan, with the predicate ``not (all finite and |x| <= B)``. The state
    arithmetic is that of the unguarded loop, so the exponent is bitwise
    unchanged on a given CPU and XLA build (a regression test and the V4 check
    pin the XLA float path). The derivative of ``|x|`` at NaN returns a finite
    Jacobian, so the exponent alone can never reveal divergence.

    Needs owner review before freeze: it sets the study's time unit.

    Parameters
    ----------
    spec : SystemSpec
        System description (``orbit_bound`` is required).
    interval : float
        Step length used for tangent propagation (natural time units).
    n_steps : int
        Number of averaging steps.
    burn_in : int
        Steps discarded before averaging.

    Returns
    -------
    tuple[float, float]
        The exponent per natural time unit and ``max |x|`` over the checked
        states.

    Raises
    ------
    OrbitDivergence
        If the orbit fails the guard; the message gives the first failing
        step.
    ValueError
        If the bound is unusable (see ``SystemSpec.orbit_bound``).
    """
    bound = checked_bound(spec)
    step_fn = make_flow_step(spec, spec.params, interval)
    jac_fn = jax.jacfwd(step_fn)

    def check(state, index, largest, first):
        finite = jnp.all(jnp.isfinite(state))
        # NaN marks a non-finite state.
        size = jnp.where(finite, jnp.abs(state[0]), jnp.nan)
        bad = jnp.logical_not(finite & (size <= bound))
        return jnp.maximum(largest, size), jnp.where(
            (first < 0) & bad, index, first
        )

    def burn_body(index, carry):
        state, largest, first = carry
        largest, first = check(state, index, largest, first)
        return step_fn(state), largest, first

    state = jnp.asarray(spec.initial_state, dtype=jnp.float64)
    state, largest, first = jax.jit(
        lambda c: jax.lax.fori_loop(0, burn_in, burn_body, c)
    )(
        (
            state,
            jnp.asarray(0.0, dtype=jnp.float64),
            jnp.asarray(-1, dtype=jnp.int64),
        )
    )

    def body(carry, _):
        current, basis, index, largest, first = carry
        largest, first = check(current, index, largest, first)
        propagated = jac_fn(current) @ basis
        q_mat, r_mat = jnp.linalg.qr(propagated)
        signs = jnp.sign(jnp.diag(r_mat))
        q_mat = q_mat * signs
        log_growth = jnp.log(jnp.abs(jnp.diag(r_mat)))
        return (
            (step_fn(current), q_mat, index + 1, largest, first),
            log_growth[0],
        )

    basis = jnp.eye(spec.dim)
    (_, _, _, largest, first), growth = jax.jit(
        lambda c: jax.lax.scan(body, c, None, length=n_steps)
    )((state, basis, jnp.asarray(burn_in, dtype=jnp.int64), largest, first))
    if int(first) >= 0:
        raise _refuse(spec, "lyapunov", float(largest), int(first))
    return float(jnp.sum(growth) / (n_steps * interval)), float(largest)


def estimate_lyapunov(
    spec: SystemSpec, interval: float, n_steps: int, burn_in: int
) -> float:
    """Return only the exponent of :func:`lyapunov_guarded`.

    A diverging orbit raises ``OrbitDivergence``, exactly as in
    :func:`lyapunov_guarded`. The parameters are the same, and the result is
    the largest Lyapunov exponent per natural time unit.
    """
    return lyapunov_guarded(spec, interval, n_steps, burn_in)[0]
