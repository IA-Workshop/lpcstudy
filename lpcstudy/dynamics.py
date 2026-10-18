"""Vectorized propagation: forecasts, tangent dynamics, delay-map observability.

The physics-based forecaster (PLP) and the per-state predictability conditions
both need to push many states forward in time at once and to know how small
errors grow along the way. This module builds those batched functions from a
flow map (see ``systems.make_flow_step``):

* the forecast path of the observed coordinate (``make_observation_paths``);
* the amplification factor ``g_H`` that says how much an initial error is
  stretched after ``H`` steps (``make_amplification``), and its summary
  growth exponent (``growth_exponent``);
* a finite-size version of the growth exponent for random perturbations
  (``make_finite_growth``);
* the observability factor ``nu`` that says how strongly observation noise
  corrupts a state estimate (``make_observability``), and the delay map it is
  built on (``delay_map_forward``).

``ensemble.py``, ``oracle.py``, ``estimation.py``, ``validation.py`` and
``experiments.py`` call these builders.

Conventions: latent states are passed in *physical* coordinates unless a
function says otherwise. Amplification factors and observability are reported
in *whitened* latent coordinates (rescaled so the state has unit covariance)
and *normalized* observation units (``x / sigma_x``), which makes them
dimensionless and comparable across systems.
"""

from __future__ import annotations

from collections.abc import Callable

import jax
import jax.numpy as jnp
import numpy as np

StepFn = Callable[[jnp.ndarray], jnp.ndarray]


def make_observation_paths(
    step_fn: StepFn,
    observed_index: int,
    obs_mean: float,
    obs_scale: float,
    n_steps: int,
) -> Callable[[jnp.ndarray], jnp.ndarray]:
    """Build a batched function returning normalized observations of forecasts.

    Parameters
    ----------
    step_fn : StepFn
        Flow map over one observation interval (the forecast model).
    observed_index : int
        Observed coordinate.
    obs_mean, obs_scale : float
        Mean and scale used to normalize the observable.
    n_steps : int
        Number of steps propagated (``H = 1..n_steps``).

    Returns
    -------
    Callable[[jnp.ndarray], jnp.ndarray]
        Maps states ``(n, m)`` to observations ``(n, n_steps)``; entry ``H-1``
        is ``h(Phi^H(s))``. Non-finite values (a blow-up off the attractor)
        are replaced by ``+inf`` and handled by the caller.
    """

    def single(state: jnp.ndarray) -> jnp.ndarray:
        def body(s, _):
            nxt = step_fn(s)
            return nxt, (nxt[observed_index] - obs_mean) / obs_scale

        _, path = jax.lax.scan(body, state, None, length=n_steps)
        return jnp.where(jnp.isfinite(path), path, jnp.inf)

    return jax.jit(jax.vmap(single))


def make_amplification(
    step_fn: StepFn,
    observed_index: int,
    obs_scale: float,
    unwhiten: np.ndarray,
    n_steps: int,
) -> Callable[[jnp.ndarray], jnp.ndarray]:
    """Build a batched function returning ``g_H(s) = ||Gamma_H(s)||``.

    ``Gamma_H(s) = grad h(Phi^H s) D Phi^H(s)`` measures how a small error in
    the starting state shows up in the observation ``H`` steps later. It is
    expressed in whitened latent coordinates (right-multiplied by
    ``C^{1/2}``) and normalized observation units (divided by ``sigma_x``).

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
            return (s, tangent), (
                jnp.linalg.norm(tangent[observed_index]) / obs_scale
            )

        _, gains = jax.lax.scan(body, (state, root), None, length=n_steps)
        return gains

    return jax.jit(jax.vmap(single))


def growth_exponent(gains: np.ndarray, window: int) -> np.ndarray:
    """Return the effective growth exponent of each state.

    The exponent is the least-squares slope of ``ln g_H`` against
    ``H = 1..window``, so it is the average exponential growth rate of the
    amplification factor over the window.

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
    return ((logs - logs.mean(axis=1, keepdims=True)) @ centered) / np.sum(
        centered**2
    )


def make_finite_growth(
    step_fn: StepFn,
    observed_index: int,
    obs_scale: float,
    unwhiten: np.ndarray,
    n_steps: int,
    n_dirs: int,
    rng: np.random.Generator,
) -> Callable[[jnp.ndarray, float], jnp.ndarray]:
    """Build the finite-amplitude growth ``Lambda_fin`` from random kicks.

    Instead of the infinitesimal (tangent) growth used by
    ``make_amplification``, this measures the growth of perturbations of a
    given finite size ``eps``, using random whitened directions.

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
        Source of the directions, consumed once (``n_dirs * dim`` normal
        draws). The caller builds a *fresh*
        ``make_rng(seed, system, "finite-growth")`` per call, so that the
        directions are the same at every perturbation scale (common random
        numbers across scales, WU-0002.14) and different for every seed and
        system. Needs owner review before freeze.

    Returns
    -------
    Callable[[jnp.ndarray, float], jnp.ndarray]
        Maps (physical states ``(n, m)``, amplitude ``eps`` in whitened
        units) to slopes per step ``(n,)`` of
        ``0.5 ln mean |dh|^2 / eps^2``.
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
        perturbed = jax.vmap(lambda s: batched(s[None, :] + eps * offsets))(
            states
        )
        diff = (perturbed - base[:, None, :]) / obs_scale
        log_growth = 0.5 * jnp.log(jnp.mean(diff**2, axis=1) / eps**2)
        horizons = jnp.arange(1, n_steps + 1, dtype=float)
        centered = horizons - horizons.mean()
        return (
            (log_growth - log_growth.mean(axis=1, keepdims=True))
            @ centered
            / jnp.sum(centered**2)
        )

    return run


def make_observability(
    step_fn: StepFn,
    observed_index: int,
    obs_scale: float,
    whiten: np.ndarray,
    delay: int,
    embed_dim: int,
) -> Callable[[jnp.ndarray], jnp.ndarray]:
    """Build the noise-amplification factor ``nu(s)`` of the delay map.

    The factor ``nu`` says how much observation noise is magnified when the
    state is recovered from a delay vector. It is computed forward only.

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

        (_, q_mat), rows = jax.lax.scan(
            body, (state, jnp.eye(dim)), None, length=span
        )
        rows = jnp.concatenate(
            [jnp.eye(dim)[observed_index][None, :], rows], axis=0
        )
        # rows[j] = grad h D Phi^{j}(s_old); X_t[k] uses j = (D-1-k) tau.
        a_mat = (
            rows[(embed_dim - 1 - jnp.arange(embed_dim)) * delay] / obs_scale
        )
        info_inv = jnp.linalg.inv(a_mat.T @ a_mat)
        cov = w_mat @ q_mat @ info_inv @ q_mat.T @ w_mat.T
        return jnp.sqrt(jnp.trace(cov))

    return jax.jit(jax.vmap(single))


def delay_map_forward(
    step_fn: StepFn,
    observed_index: int,
    obs_mean: float,
    obs_scale: float,
    delay: int,
    embed_dim: int,
) -> Callable[[jnp.ndarray], jnp.ndarray]:
    """Build the delay vector as a function of the oldest window state.

    A delay vector stacks the observation at the current time and at earlier
    times spaced ``delay`` steps apart. Starting from the oldest state of the
    window and running the model forward gives every entry, which is what the
    Gauss-Newton estimator and the validation checks need.

    Parameters
    ----------
    step_fn : StepFn
        Flow map.
    observed_index : int
        Observed coordinate.
    obs_mean, obs_scale : float
        Mean and scale used to normalize the observable.
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
