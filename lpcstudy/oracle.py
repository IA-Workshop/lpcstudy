"""Oracle (privileged) per-state quantities and the moment-based optimal weight."""

from __future__ import annotations

from dataclasses import dataclass

import jax.numpy as jnp
import numpy as np
from scipy.spatial import cKDTree

from .data import SystemContext
from .dynamics import growth_exponent, make_amplification, make_observability
from .ensemble import EnsembleMoments


@dataclass
class StateOracles:
    """Noise-independent oracle quantities of the states of one split.

    Attributes
    ----------
    nu : np.ndarray
        Noise-amplification factor ``nu(s)`` (whitened), ``(n,)``.
    gains : np.ndarray
        ``g_H(s)`` for ``H = 1..window``, ``(n, window)``.
    growth : np.ndarray
        Effective exponent ``Lambda_bar`` per step (slope of ``ln g_H``), ``(n,)``.
    local_dim : np.ndarray
        Levina-Bickel local dimension of the latent state, ``(n,)``.
    """

    nu: np.ndarray
    gains: np.ndarray
    growth: np.ndarray
    local_dim: np.ndarray

    def subset(self, rows: np.ndarray) -> "StateOracles":
        """Restrict to a subset of states."""
        return StateOracles(self.nu[rows], self.gains[rows], self.growth[rows],
                            self.local_dim[rows])


def local_dimension(reference: np.ndarray, queries: np.ndarray, n_neighbors: int = 20
                    ) -> np.ndarray:
    """Levina-Bickel maximum-likelihood local dimension.

    Parameters
    ----------
    reference : np.ndarray
        Reference sample of whitened states ``(N, m)``.
    queries : np.ndarray
        Whitened query states ``(n, m)`` (not contained in ``reference``).
    n_neighbors : int, optional
        Number of neighbors ``k``.

    Returns
    -------
    np.ndarray
        Local dimension estimates ``(n,)``.
    """
    dist, _ = cKDTree(reference).query(queries, k=n_neighbors, workers=-1)
    dist = np.maximum(dist, 1e-300)
    logs = np.log(dist[:, -1:] / dist[:, :-1])
    return (n_neighbors - 2) / np.sum(logs, axis=1)


def state_oracles(ctx: SystemContext, split: str, window: int,
                  chunk: int = 2000) -> StateOracles:
    """Compute ``nu``, ``g_H`` and ``Lambda_bar`` along the true trajectory.

    Parameters
    ----------
    ctx : SystemContext
        System context.
    split : str
        Split name.
    window : int
        Number of horizons for ``g_H`` and for the exponent fit (one Lyapunov time).
    chunk : int, optional
        States per batch.

    Returns
    -------
    StateOracles
        Oracle quantities of the split.
    """
    from .systems import make_flow_step

    step_fn = make_flow_step(ctx.spec, ctx.spec.params, ctx.interval)
    nu_fn = make_observability(step_fn, ctx.spec.observed_index, ctx.obs_scale,
                               ctx.whiten, ctx.delay, ctx.embed_dim)
    amp_fn = make_amplification(step_fn, ctx.spec.observed_index, ctx.obs_scale,
                                ctx.unwhiten, window)
    times = ctx.split_indices[split]
    nu_parts, gain_parts = [], []
    for start in range(0, len(times), chunk):
        t_chunk = times[start:start + chunk]
        nu_parts.append(np.asarray(nu_fn(jnp.asarray(ctx.eval_states[t_chunk - ctx.history]))))
        gain_parts.append(np.asarray(amp_fn(jnp.asarray(ctx.eval_states[t_chunk]))))
    gains = np.concatenate(gain_parts)
    rng = np.random.default_rng(0)
    pool = ctx.library_states[rng.choice(len(ctx.library_states),
                                         size=min(20_000, len(ctx.library_states)),
                                         replace=False)]
    dims = local_dimension(ctx.whiten_states(pool), ctx.whiten_states(ctx.eval_states[times]))
    return StateOracles(nu=np.concatenate(nu_parts), gains=gains,
                        growth=growth_exponent(gains, window), local_dim=dims)


def oracle_weight(moments: EnsembleMoments, clip: bool = True) -> np.ndarray:
    """Minimum-mean-squared-error weight on CP at each state and horizon.

    ``w* = E[e_P (e_P - e_C)] / E[(e_C - e_P)^2]``: the exact minimizer of the
    ensemble mean of ``(w e_C + (1 - w) e_P)^2``, equal to FW Proposition 3 with
    sample moments (it includes the copied-noise term and the seed
    cross-covariance automatically).

    Parameters
    ----------
    moments : EnsembleMoments
        Ensemble moments.
    clip : bool, optional
        Clip to ``[0, 1]`` (the admissible class).

    Returns
    -------
    np.ndarray
        Weights ``(n, nH)``.
    """
    curv = curvature(moments)
    raw = (moments.sq_plp - moments.cross) / np.maximum(curv, 1e-300)
    return np.clip(raw, 0.0, 1.0) if clip else raw


def curvature(moments: EnsembleMoments) -> np.ndarray:
    """Curvature ``c = E[(e_C - e_P)^2]`` of the error quadratic, ``(n, nH)``."""
    return moments.sq_cp + moments.sq_plp - 2.0 * moments.cross


def hybrid_mse(moments: EnsembleMoments, weight: np.ndarray) -> np.ndarray:
    """Expected squared error ``E[(w e_C + (1-w) e_P)^2]`` for given weights.

    Parameters
    ----------
    moments : EnsembleMoments
        Ensemble moments.
    weight : np.ndarray
        Weights broadcastable to ``(n, nH)``.

    Returns
    -------
    np.ndarray
        Expected squared error against the noise-free truth, ``(n, nH)``.
    """
    w = np.broadcast_to(weight, moments.sq_cp.shape)
    return w**2 * moments.sq_cp + (1 - w) ** 2 * moments.sq_plp + \
        2 * w * (1 - w) * moments.cross


def characteristic_horizon(mse: np.ndarray, horizons: np.ndarray, noise: float,
                           theta: float) -> tuple[np.ndarray, np.ndarray]:
    """First horizon at which the r.m.s. error against the *noisy* truth exceeds ``theta``.

    Parameters
    ----------
    mse : np.ndarray
        Expected squared error against the noise-free truth, ``(n, nH)``,
        on contiguous horizons ``1..H_max``.
    horizons : np.ndarray
        Horizons (must be ``1..H_max``).
    noise : float
        Verification-noise level ``rho`` (added in quadrature).
    theta : float
        Tolerance (fraction of ``sigma_x``).

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Horizon in steps (``H_max`` if censored) and event indicator.

    Raises
    ------
    ValueError
        If the horizons are not contiguous from 1.
    """
    if not np.array_equal(horizons, np.arange(1, len(horizons) + 1)):
        raise ValueError("characteristic horizon needs horizons 1..H_max")
    exceed = np.sqrt(mse + noise**2) > theta
    event = exceed.any(axis=1)
    first = np.where(event, exceed.argmax(axis=1) + 1, len(horizons))
    return first, event


def realized_horizon(errors: np.ndarray, horizons: np.ndarray, theta: float
                     ) -> tuple[np.ndarray, np.ndarray]:
    """First passage of realized errors (against the noisy truth) above ``theta``.

    Parameters
    ----------
    errors : np.ndarray
        Realized errors against the noisy truth, ``(..., nH)`` with
        horizons ``1..H_max``.
    horizons : np.ndarray
        Horizons (``1..H_max``).
    theta : float
        Tolerance.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        First-passage horizon (``H_max`` if censored) and event indicator.
    """
    exceed = np.abs(errors) > theta
    event = exceed.any(axis=-1)
    first = np.where(event, exceed.argmax(axis=-1) + 1, len(horizons))
    return first, event
