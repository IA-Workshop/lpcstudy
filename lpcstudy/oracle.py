"""Oracle (privileged) per-state quantities and the moment-based optimal weight."""

from __future__ import annotations

from dataclasses import dataclass

import jax.numpy as jnp
import numpy as np
from scipy.spatial import cKDTree

from .data import SystemContext
from .dynamics import growth_exponent, make_amplification, make_observability
from .ensemble import EnsembleMoments


ORACLE_COUNTERS: tuple[str, ...] = ("local_dim_zero_distance", "oracle_gain_floor",
                                    "oracle_nonfinite")
"""Columns of ``StateOracles.handled``; each counts states of the split (DEF-0001)."""


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
    handled : np.ndarray or None
        Per-state 0/1 flags ``(n, 3)`` int64, columns ``ORACLE_COUNTERS``: a neighbour distance
        below the ``1e-300`` floor of ``local_dimension``; a gain below that floor in the window;
        a non-finite ``nu`` or gain (never replaced: it propagates). All three are sentinels
        (a nonzero count means a hypothesis or the code failed). ``None`` for hand-built oracles.
    """

    nu: np.ndarray
    gains: np.ndarray
    growth: np.ndarray
    local_dim: np.ndarray
    handled: np.ndarray | None = None

    def subset(self, rows: np.ndarray) -> "StateOracles":
        """Restrict to a subset of states."""
        return StateOracles(self.nu[rows], self.gains[rows], self.growth[rows],
                            self.local_dim[rows],
                            None if self.handled is None else self.handled[rows])


def local_dimension_counted(reference: np.ndarray, queries: np.ndarray, n_neighbors: int = 20
                            ) -> tuple[np.ndarray, np.ndarray]:
    """Levina-Bickel local dimension and the states whose distance floor bound.

    A neighbour at distance below ``1e-300`` (an exact duplicate of the query in the reference,
    which the contract excludes) is floored to ``1e-300`` before the logarithm. The dimension
    is that of :func:`local_dimension`; the flag marks the states (``local_dim_zero_distance``).

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
    dims : np.ndarray
        Local dimension estimates ``(n,)``.
    floored : np.ndarray
        Boolean ``(n,)``: at least one of the ``k`` neighbour distances was below ``1e-300``.
    """
    dist, _ = cKDTree(reference).query(queries, k=n_neighbors, workers=-1)
    floored = (dist < 1e-300).any(axis=1)
    dist = np.maximum(dist, 1e-300)
    logs = np.log(dist[:, -1:] / dist[:, :-1])
    return (n_neighbors - 2) / np.sum(logs, axis=1), floored


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
    return local_dimension_counted(reference, queries, n_neighbors)[0]


def inverse_dimension(local_dim: np.ndarray, n_neighbors: int = 20) -> np.ndarray:
    """Per-state Levina-Bickel inverse dimension ``S / (k - 1)`` (H1a reference, DEC-0008 A4(h)).

    ``S = sum_{j<k} ln(T_k / T_j)`` is the sum of the ``k - 1`` log distance ratios of a state.
    With the nearest-neighbor ball uniform on a ``d``-flat (the Poisson law of Levina and
    Bickel 2005, NIPS 17, Sec. 3.1), ``S d ~ Gamma(k - 1, 1)``, so ``E[S / (k - 1)] = 1 / d``
    exactly. It is *not* ``1 / local_dim``: :func:`local_dimension` is ``(k - 2) / S``, whose
    inverse ``S / (k - 2)`` is too high by ``(k - 1) / (k - 2) - 1 = +1 / (k - 2)`` (5.6% at
    ``k = 20``). This function inverts the k - 2 estimate and applies the ``(k - 2) / (k - 1)``
    correction, so ``inverse_dimension(local_dimension(r, q, k), k) = S / (k - 1)``.

    Parameters
    ----------
    local_dim : np.ndarray
        Output of :func:`local_dimension`, ``(n,)``. NaN stays NaN, and ``+inf`` (``S = 0``,
        all neighbors at the same distance) gives 0; the caller excludes and counts such
        states.
    n_neighbors : int, optional
        The ``k`` used to compute ``local_dim`` (same default as :func:`local_dimension`).

    Returns
    -------
    np.ndarray
        ``(k - 2) / ((k - 1) local_dim)``, ``(n,)``.

    Raises
    ------
    ValueError
        If ``n_neighbors < 3`` (with ``k = 2`` the estimator ``(k - 2) / S`` is identically 0).
    """
    if n_neighbors < 3:
        raise ValueError(f"n_neighbors must be at least 3; got {n_neighbors}")
    return (n_neighbors - 2) / ((n_neighbors - 1) * np.asarray(local_dim, dtype=float))


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
    nu = np.concatenate(nu_parts)
    rng = np.random.default_rng(0)
    pool = ctx.library_states[rng.choice(len(ctx.library_states),
                                         size=min(20_000, len(ctx.library_states)),
                                         replace=False)]
    dims, zero_distance = local_dimension_counted(
        ctx.whiten_states(pool), ctx.whiten_states(ctx.eval_states[times]))
    return StateOracles(nu=nu, gains=gains, growth=growth_exponent(gains, window),
                        local_dim=dims, handled=oracle_handling(nu, gains, window, zero_distance))


def oracle_handling(nu: np.ndarray, gains: np.ndarray, window: int, zero_distance: np.ndarray
                    ) -> np.ndarray:
    """Per-state sentinel flags of the oracle quantities (``ORACLE_COUNTERS``). Nothing is replaced.

    ``oracle_gain_floor`` marks a state with a gain below the ``1e-300`` floor of
    ``growth_exponent`` in the first ``window`` columns (NaN does not count: ``NaN < x`` is
    False). ``oracle_nonfinite`` marks a state with a non-finite ``nu`` or a non-finite gain
    anywhere; such a value propagates to ``growth`` and the weights as NaN, visibly.

    Parameters
    ----------
    nu : np.ndarray
        Oracle ``nu``, ``(n,)``.
    gains : np.ndarray
        Oracle gains, ``(n, window)``.
    window : int
        Growth window (steps).
    zero_distance : np.ndarray
        Boolean ``(n,)`` from :func:`local_dimension_counted`.

    Returns
    -------
    np.ndarray
        ``(n, 3)`` int64 flags, columns ``ORACLE_COUNTERS``.
    """
    floor = (gains[:, :window] < 1e-300).any(axis=1)
    nonfinite = ~np.isfinite(nu) | ~np.isfinite(gains).all(axis=1)
    return np.column_stack([zero_distance, floor, nonfinite]).astype(np.int64)


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


def excess_mse(moments: EnsembleMoments, weight: np.ndarray) -> np.ndarray:
    """Exact excess error ``V(w) - V(w*)`` of a weight over the constrained optimum.

    Implements Theorem P1(a). With ``c = E[(e_C - e_P)^2]`` (``curvature``) and the
    unconstrained minimizer ``u = E[e_P (e_P - e_C)] / c``, the expected squared
    error is ``V(w) = c (w - u)^2 + V(u)``. The admissible optimum is
    ``w* = clip(u, 0, 1)``, hence

    ``V(w) - V(w*) = c [(w - u)^2 - (w* - u)^2]``,

    which equals ``c (w - w*)^2`` only when ``u`` lies in ``[0, 1]``. When ``u`` is
    clipped, ``c (w - w*)^2`` underestimates the excess (DEF-0002). This form is
    evaluated in IEEE arithmetic from the same ``u`` that gives ``w*``, so the
    result is ``>= 0`` and is exactly ``0.0`` at ``w = w*`` (rounding is monotone and
    ``|w - u| >= |w* - u|``); the factored form ``(w - w*)(c (w + w*) - 2 b)``
    can be negative near ``w*``.

    Hypothesis: ``c > 0`` (P1(a): ``c >= rho^2 / k``). A non-positive or non-finite
    curvature is not filtered here (it makes ``u`` infinite or NaN through the
    ``1e-300`` floor of ``oracle_weight``); counting it belongs to the floor audit of
    DEF-0001.

    Parameters
    ----------
    moments : EnsembleMoments
        Ensemble moments, arrays ``(n, nH)``.
    weight : np.ndarray
        Weights ``(n, nH)`` or ``(n, E, nH)``. For three dimensions the moments
        are broadcast along axis 1 (draws).

    Returns
    -------
    np.ndarray
        Excess expected squared error against the noise-free truth, same shape
        as ``weight``.

    Raises
    ------
    ValueError
        If ``weight`` is not ``(n, nH)`` or ``(n, E, nH)`` for the moments' shape.
    """
    unclipped = oracle_weight(moments, clip=False)
    curv = curvature(moments)
    if weight.ndim == 2 and weight.shape == curv.shape:
        pass
    elif weight.ndim == 3 and weight.shape[0] == curv.shape[0] \
            and weight.shape[2] == curv.shape[1]:
        unclipped, curv = unclipped[:, None, :], curv[:, None, :]
    else:
        raise ValueError(f"weight shape {weight.shape} does not match moments "
                         f"{curv.shape}: expected (n, nH) or (n, E, nH)")
    optimum = np.clip(unclipped, 0.0, 1.0)
    return curv * ((weight - unclipped) ** 2 - (optimum - unclipped) ** 2)


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
