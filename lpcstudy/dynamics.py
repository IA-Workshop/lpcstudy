"""Vectorized propagation: forecasts, tangent dynamics, delay-map observability.

Conventions: latent states are passed in *physical* coordinates unless a
function says otherwise; amplification factors and observability are reported
in *whitened* latent coordinates and *normalized* observation units
(``x / sigma_x``), which makes them dimensionless and comparable across
systems.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import partial

import jax
import jax.numpy as jnp
import numpy as np

StepFn = Callable[[jnp.ndarray], jnp.ndarray]


def make_observation_paths(step_fn: StepFn, observed_index: int, obs_mean: float,
                           obs_scale: float, n_steps: int
                           ) -> Callable[[jnp.ndarray], jnp.ndarray]:
    """Build a batched function returning normalized observations along forecasts.

    Parameters
    ----------
    step_fn : StepFn
        Flow map over one observation interval (the forecast model).
    observed_index : int
        Observed coordinate.
    obs_mean, obs_scale : float
        Normalization of the observable.
    n_steps : int
        Number of steps propagated (``H = 1..n_steps``).

    Returns
    -------
    Callable[[jnp.ndarray], jnp.ndarray]
        Maps states ``(n, m)`` to observations ``(n, n_steps)``; entry ``H-1``
        is ``h(Phi^H(s))``. Non-finite values (blow-up off the attractor) are
        replaced by ``+inf`` and handled by the caller.
    """
    def single(state: jnp.ndarray) -> jnp.ndarray:
        def body(s, _):
            nxt = step_fn(s)
            return nxt, (nxt[observed_index] - obs_mean) / obs_scale
        _, path = jax.lax.scan(body, state, None, length=n_steps)
        return jnp.where(jnp.isfinite(path), path, jnp.inf)

    return jax.jit(jax.vmap(single))


def make_amplification(step_fn: StepFn, observed_index: int, obs_scale: float,
                       unwhiten: np.ndarray, n_steps: int
                       ) -> Callable[[jnp.ndarray], jnp.ndarray]:
    """Build a batched function returning ``g_H(s) = ||Gamma_H(s)||``.

    ``Gamma_H(s) = grad h(Phi^H s) D Phi^H(s)`` is expressed in whitened latent
    coordinates (right-multiplied by ``C^{1/2}``) and normalized observation
    units (divided by ``sigma_x``).

    Parameters
    ----------
    step_fn : StepFn
        Flow map over one observation interval.
    observed_index : int
        Observed coordinate.
    obs_scale : float
        ``sigma_x``.
    unwhiten : np.ndarray
        ``C^{1/2}``.
    n_steps : int
        Largest horizon.

    Returns
    -------
    Callable[[jnp.ndarray], jnp.ndarray]
        Maps physical states ``(n, m)`` to ``g_H`` of shape ``(n, n_steps)``.
    """
    jac = jax.jacfwd(step_fn)
    root = jnp.asarray(unwhiten)

    def single(state: jnp.ndarray) -> jnp.ndarray:
        def body(carry, _):
            s, tangent = carry
            tangent = jac(s) @ tangent
            s = step_fn(s)
            return (s, tangent), jnp.linalg.norm(tangent[observed_index]) / obs_scale
        _, gains = jax.lax.scan(body, (state, root), None, length=n_steps)
        return gains

    return jax.jit(jax.vmap(single))


def growth_exponent(gains: np.ndarray, window: int) -> np.ndarray:
    """Effective exponent: least-squares slope of ``ln g_H`` over ``H = 1..window``.

    Parameters
    ----------
    gains : np.ndarray
        Amplification factors, shape ``(n, >= window)``.
    window : int
        Number of horizons in the fit.

    Returns
    -------
    np.ndarray
        Slopes per observation step, shape ``(n,)``.
    """
    horizons = np.arange(1, window + 1, dtype=float)
    centered = horizons - horizons.mean()
    logs = np.log(np.maximum(gains[:, :window], 1e-300))
    return (logs - logs.mean(axis=1, keepdims=True)) @ centered / np.sum(centered**2)


def make_finite_growth(step_fn: StepFn, observed_index: int, obs_scale: float,
                       unwhiten: np.ndarray, n_steps: int, n_dirs: int,
                       rng: np.random.Generator) -> Callable[[jnp.ndarray, float], jnp.ndarray]:
    """Finite-amplitude growth ``Lambda_fin`` from random whitened perturbations.

    Parameters
    ----------
    step_fn : StepFn
        Flow map.
    observed_index : int
        Observed coordinate.
    obs_scale : float
        ``sigma_x``.
    unwhiten : np.ndarray
        ``C^{1/2}``.
    n_steps : int
        Window length.
    n_dirs : int
        Number of random unit directions.
    rng : np.random.Generator
        Source of the directions, consumed once (``n_dirs * dim`` normal draws). The caller
        builds a *fresh* ``make_rng(seed, system, "finite-growth")`` per call, so that the
        directions are the same at every perturbation scale (common random numbers across
        scales, WU-0002.14) and different for every seed and system. Needs owner review before
        freeze.

    Returns
    -------
    Callable[[jnp.ndarray, float], jnp.ndarray]
        Maps (physical states ``(n, m)``, amplitude ``eps`` in whitened units)
        to slopes per step ``(n,)`` of ``0.5 ln mean |dh|^2 / eps^2``.
    """
    dim = unwhiten.shape[0]
    dirs = rng.standard_normal((n_dirs, dim))
    dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
    offsets = jnp.asarray(dirs @ unwhiten.T)

    def paths(states: jnp.ndarray) -> jnp.ndarray:
        def body(s, _):
            nxt = step_fn(s)
            return nxt, nxt[observed_index]
        return jax.lax.scan(body, states, None, length=n_steps)[1]

    batched = jax.vmap(paths)

    @jax.jit
    def run(states: jnp.ndarray, eps: float) -> jnp.ndarray:
        base = batched(states)  # (n, n_steps)
        perturbed = jax.vmap(lambda s: batched(s[None, :] + eps * offsets))(states)
        diff = (perturbed - base[:, None, :]) / obs_scale
        log_growth = 0.5 * jnp.log(jnp.mean(diff**2, axis=1) / eps**2)
        horizons = jnp.arange(1, n_steps + 1, dtype=float)
        centered = horizons - horizons.mean()
        return (log_growth - log_growth.mean(axis=1, keepdims=True)) @ centered / \
            jnp.sum(centered**2)

    return run


def make_observability(step_fn: StepFn, observed_index: int, obs_scale: float,
                       whiten: np.ndarray, delay: int, embed_dim: int
                       ) -> Callable[[jnp.ndarray], jnp.ndarray]:
    """Noise-amplification factor ``nu(s)`` of the delay map, forward-only.

    With ``s_old = s_{t-(D-1) tau}``, ``A = d X_t / d s_old`` (rows
    ``grad h D Phi^{(D-1-k) tau}(s_old) / sigma_x``) and
    ``Q = D Phi^{(D-1) tau}(s_old)``, the delay-map Jacobian at ``s_t`` is
    ``J_G = A Q^{-1}``, hence ``(J_G^T J_G)^{-1} = Q (A^T A)^{-1} Q^T``. In
    whitened coordinates ``nu^2 = tr[C^{-1/2} Q (A^T A)^{-1} Q^T C^{-1/2}]``.
    No backward integration and no inverse of ``Q`` is needed.

    Parameters
    ----------
    step_fn : StepFn
        Flow map.
    observed_index : int
        Observed coordinate.
    obs_scale : float
        ``sigma_x``.
    whiten : np.ndarray
        ``C^{-1/2}``.
    delay : int
        Delay ``tau_d``.
    embed_dim : int
        Embedding dimension ``D``.

    Returns
    -------
    Callable[[jnp.ndarray], jnp.ndarray]
        Maps *oldest* window states ``s_old`` ``(n, m)`` to ``nu`` ``(n,)``.
    """
    jac = jax.jacfwd(step_fn)
    span = (embed_dim - 1) * delay
    w_mat = jnp.asarray(whiten)

    def single(state: jnp.ndarray) -> jnp.ndarray:
        dim = state.shape[0]

        def body(carry, _):
            s, tangent = carry
            tangent = jac(s) @ tangent
            return (step_fn(s), tangent), tangent[observed_index]

        (_, q_mat), rows = jax.lax.scan(body, (state, jnp.eye(dim)), None, length=span)
        rows = jnp.concatenate([jnp.eye(dim)[observed_index][None, :], rows], axis=0)
        # rows[j] = grad h D Phi^{j}(s_old); X_t[k] uses j = (D-1-k) tau.
        a_mat = rows[(embed_dim - 1 - jnp.arange(embed_dim)) * delay] / obs_scale
        info_inv = jnp.linalg.inv(a_mat.T @ a_mat)
        cov = w_mat @ q_mat @ info_inv @ q_mat.T @ w_mat.T
        return jnp.sqrt(jnp.trace(cov))

    return jax.jit(jax.vmap(single))


def delay_map_forward(step_fn: StepFn, observed_index: int, obs_mean: float,
                      obs_scale: float, delay: int, embed_dim: int
                      ) -> Callable[[jnp.ndarray], jnp.ndarray]:
    """Delay vector as a function of the oldest window state (for validation).

    Parameters
    ----------
    step_fn : StepFn
        Flow map.
    observed_index : int
        Observed coordinate.
    obs_mean, obs_scale : float
        Normalization of the observable.
    delay : int
        Delay ``tau_d``.
    embed_dim : int
        Embedding dimension ``D``.

    Returns
    -------
    Callable[[jnp.ndarray], jnp.ndarray]
        ``s_old -> X_t`` (ordered newest first, as in ``delay_vectors``).
    """
    span = (embed_dim - 1) * delay

    def single(state: jnp.ndarray) -> jnp.ndarray:
        def body(s, _):
            nxt = step_fn(s)
            return nxt, nxt[observed_index]
        _, path = jax.lax.scan(body, state, None, length=span)
        path = jnp.concatenate([state[observed_index][None], path])
        values = (path - obs_mean) / obs_scale
        return values[(embed_dim - 1 - jnp.arange(embed_dim)) * delay]

    return single


@partial(jax.jit, static_argnums=(0, 2))
def _advance(step_fn: StepFn, states: jnp.ndarray, n_steps: int) -> jnp.ndarray:
    return jax.lax.fori_loop(0, n_steps, lambda _, s: jax.vmap(step_fn)(s), states)


def advance_states(step_fn: StepFn, states: np.ndarray, n_steps: int) -> np.ndarray:
    """Advance a batch of states by ``n_steps`` observation intervals.

    Parameters
    ----------
    step_fn : StepFn
        Flow map.
    states : np.ndarray
        States ``(n, m)``.
    n_steps : int
        Number of steps.

    Returns
    -------
    np.ndarray
        Advanced states ``(n, m)``.
    """
    return np.asarray(_advance(step_fn, jnp.asarray(states), n_steps))
